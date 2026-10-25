# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Prueba VISIBLE de la interfaz en español de Tlamatini-Spanish.

Dos pasos, cada uno en su propia ventana a la vista:

    python l10n/prueba_visible.py preparar
        Migra la base de datos de ESTE árbol y crea el usuario de prueba del harness
        (usuario y contraseña de .claude/skills/tlamatini-daily-chat-test/harness/config.py).

    python l10n/prueba_visible.py recorrer [--url http://127.0.0.1:8011]
        Con el servidor de ESTE árbol ya corriendo en otra ventana visible, abre Chrome
        real (headed, sin sonido: --mute-audio), inicia sesión y recorre la bienvenida,
        el chat y sus menús y diálogos, el Agentic Control Panel y el Prompt Flow Panel.
        En cada paso el agent Shoter toma una foto de pantalla completa, y se junta el
        texto visible más los atributos title / placeholder / aria-label / alt para
        marcar lo que se haya quedado en inglés. Escribe Temp/l10n_prueba_visible/reporte.md.

Códigos de salida: 0 todo en español · 2 no se pudo preparar la base · 3 el servidor no
responde o no es el de este árbol · 4 falló el inicio de sesión · 5 Shoter no tomó una
foto · 6 quedó texto en inglés en pantalla.
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

L10N = Path(__file__).resolve().parent
RAIZ = L10N.parent
PROYECTO = RAIZ / "Tlamatini"
SALIDA = RAIZ / "Temp" / "l10n_prueba_visible"
SHOTER = PROYECTO / "agent" / "agents" / "shoter"
HARNESS_CONFIG = RAIZ / ".claude" / "skills" / "tlamatini-daily-chat-test" / "harness" / "config.py"

INGLES = set("""the and to of is are your you please with for this that from not can will it an in on be
has have was were all any more when which what how there their they them then than into out up
about after before while only also just been being do does did done here could would should may might
must shall our ours its my me we us he she his her these those such no yes or if else other some
click select open save close cancel settings search send delete edit view help loading""".split())
ESPANOL = set("""el la los las de del que en un una unos unas para con por se tu tus es son está están
al lo le su sus mi mis más sin sobre ya aquí este esta estos estas ese esa eso cuando como muy también
hay ser fue puede puedes haz elige escribe abre guarda cierra cancelar guardar cerrar abrir buscar
enviar eliminar editar ver ayuda cargando""".split())
# Lo que se queda en inglés A PROPÓSITO (nombres, producto, vocabulario técnico).
PERMITIDO = re.compile(
    r"\b(Tlamatini|XAIHT|ACPX|MCPs?|Multi-Turn|Exec report|Ask Execs|Compact mode|Self-modify|"
    r"Agentic Control Panel|Prompt Flow Panel|Admin Panel|Access Keys Wizard|System-Metrics|"
    r"Files-Search|Current-Time|CONTEXT-WINDOW|Ollama|Whisperer|Talker|Terminals|Canvas)\b")


def registrar(msg: str) -> None:
    linea = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(linea, flush=True)
    SALIDA.mkdir(parents=True, exist_ok=True)
    with open(SALIDA / "progreso.log", "a", encoding="utf-8") as fh:
        fh.write(linea + "\n")


def credenciales() -> tuple[str, str]:
    spec = importlib.util.spec_from_file_location("harness_config", HARNESS_CONFIG)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.USERNAME, modulo.PASSWORD


# ───────────────────────── preparar ─────────────────────────

def preparar() -> int:
    registrar("Migrando la base de datos de Tlamatini-Spanish…")
    r = subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], cwd=PROYECTO,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        registrar("✗ migrate falló")
        return 2
    usuario, contrasena = credenciales()
    codigo = (
        "from django.contrib.auth import get_user_model\n"
        "U = get_user_model()\n"
        f"u, _ = U.objects.get_or_create(username={usuario!r})\n"
        f"u.set_password({contrasena!r}); u.is_staff = True; u.is_superuser = True; u.save()\n"
        "print('usuario de prueba listo')\n"
    )
    r = subprocess.run([sys.executable, "manage.py", "shell", "-c", codigo], cwd=PROYECTO,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        registrar("✗ no se pudo crear el usuario de prueba")
        return 2
    registrar("✓ Base de datos y usuario de prueba listos")
    return 0


# ───────────────────────── Shoter ─────────────────────────

_RUNTIME = None


def foto(nombre: str) -> str | None:
    """Foto de pantalla completa con el agent Shoter de ESTE árbol."""
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = SALIDA / "_shoter_runtime"
        if _RUNTIME.exists():
            shutil.rmtree(_RUNTIME, ignore_errors=True)
        shutil.copytree(SHOTER, _RUNTIME, ignore=shutil.ignore_patterns("__pycache__", "*.log", "shoter_*"))
    with open(_RUNTIME / "config.yaml", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"output_dir: {str(SALIDA).replace(chr(92), '/')}\n")
        fh.write("all_screens: true\n")
        fh.write(f"filename: {nombre}\n")
        fh.write("target_agents: []\n")
    r = subprocess.run([sys.executable, "shoter.py"], cwd=_RUNTIME, capture_output=True, text=True,
                       timeout=90, encoding="utf-8", errors="replace")
    destino = SALIDA / nombre
    if destino.is_file():
        registrar(f"📸 {nombre}")
        return str(destino)
    registrar(f"✗ Shoter no dejó la foto {nombre} (rc={r.returncode}) {r.stderr[-200:]}")
    return None


# ───────────────────────── análisis del texto ─────────────────────────

JS_TEXTOS = """() => {
  const visibles = (document.body ? document.body.innerText : '') || '';
  const attrs = [];
  for (const el of document.querySelectorAll('[title],[placeholder],[aria-label],[alt]')) {
    const r = el.getBoundingClientRect();
    const estilo = getComputedStyle(el);
    if (estilo.display === 'none' || estilo.visibility === 'hidden') continue;
    if (r.width === 0 && r.height === 0) continue;
    for (const a of ['title', 'placeholder', 'aria-label', 'alt']) {
      const v = el.getAttribute(a);
      if (v) attrs.push(v);
    }
  }
  return {visibles, attrs, lang: document.documentElement.lang, titulo: document.title};
}"""


def sospechosas(textos: list[str]) -> list[str]:
    salida = []
    for bruto in textos:
        for linea in re.split(r"[\n\r]+", bruto):
            linea = linea.strip()
            if len(linea) < 3:
                continue
            limpia = PERMITIDO.sub(" ", linea)
            palabras = re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñ']+", limpia.lower())
            if not palabras:
                continue
            en = sum(1 for p in palabras if p in INGLES)
            es = sum(1 for p in palabras if p in ESPANOL) + len(re.findall(r"[áéíóúñ¿¡]", limpia.lower()))
            if en >= 1 and en > es:
                salida.append(linea[:160])
    return sorted(set(salida))


# ───────────────────────── recorrer ─────────────────────────

def esperar_servidor(url: str, segundos: int = 240) -> bool:
    limite = time.time() + segundos
    while time.time() < limite:
        try:
            with urllib.request.urlopen(url + "/", timeout=5) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                if 'lang="es-MX"' in html:
                    return True
                registrar("✗ El servidor responde pero NO es Tlamatini-Spanish (no hay lang=\"es-MX\")")
                return False
        except Exception:  # noqa: BLE001 - todavía arrancando
            time.sleep(3)
    return False


def recorrer(url: str) -> int:
    from playwright.sync_api import sync_playwright

    SALIDA.mkdir(parents=True, exist_ok=True)
    registrar(f"Esperando el servidor de Tlamatini-Spanish en {url} …")
    if not esperar_servidor(url):
        registrar("✗ El servidor no respondió como Tlamatini-Spanish")
        return 3
    usuario, contrasena = credenciales()
    hallazgos: dict[str, list[str]] = {}
    fotos_fallidas = 0

    def revisar(page, nombre: str, tomar_foto: bool = True):
        nonlocal fotos_fallidas
        page.wait_for_timeout(900)
        datos = page.evaluate(JS_TEXTOS)
        hallazgos[nombre] = sospechosas([datos["visibles"], *datos["attrs"], datos["titulo"]])
        registrar(f"   {nombre}: lang={datos['lang']} · título «{datos['titulo']}» · "
                  f"{len(hallazgos[nombre])} renglones sospechosos")
        if tomar_foto and foto(f"{len(hallazgos):02d}_{nombre}.png") is None:
            fotos_fallidas += 1

    with sync_playwright() as pw:
        navegador = pw.chromium.launch(channel="chrome", headless=False,
                                       args=["--mute-audio", "--start-maximized"])
        contexto = navegador.new_context(no_viewport=True, locale="es-MX")
        # el avatar no habla durante la prueba: modo silencioso guardado en el navegador
        contexto.add_init_script(
            "try { const s = JSON.parse(localStorage.getItem('tlm_voice_settings') || '{}');"
            " s.mode = 'silent'; localStorage.setItem('tlm_voice_settings', JSON.stringify(s)); } catch (e) {}")
        page = contexto.new_page()
        page.goto(url + "/")
        revisar(page, "login")
        page.fill("#id_username", usuario)
        page.fill("#id_password", contrasena)
        page.click("button[type=submit]")
        try:
            page.wait_for_url("**/welcome/**", timeout=20000)
        except Exception:  # noqa: BLE001
            registrar("✗ El inicio de sesión no llegó a la bienvenida")
            navegador.close()
            return 4
        revisar(page, "bienvenida")

        page.goto(url + "/agent/agent/")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(8000)  # deja que el chat pinte sus mensajes fijos
        revisar(page, "chat")
        for menu in ("views-menu-button", "context-menu-button", "panels-menu-button", "skills-menu-button",
                     "external-menu-button", "config-menu-button", "db-menu-button", "about-menu-button"):
            try:
                page.click(f"#{menu}", timeout=5000)
                revisar(page, f"menu_{menu.replace('-menu-button', '')}")
                page.keyboard.press("Escape")
                page.mouse.click(5, 300)
            except Exception as exc:  # noqa: BLE001
                registrar(f"   (no se pudo abrir #{menu}: {str(exc)[:80]})")

        for pagina, nombre in (("/agent/agentic_control_panel/", "agentic_control_panel"),
                               ("/agent/prompt_flow_panel/", "prompt_flow_panel")):
            page.goto(url + pagina)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000)
            revisar(page, nombre)
        navegador.close()

    total = sum(len(v) for v in hallazgos.values())
    with open(SALIDA / "reporte.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# Prueba visible de Tlamatini-Spanish — {datetime.now().isoformat(timespec='seconds')}\n\n")
        fh.write(f"Servidor: {url}. Fotos en esta misma carpeta (las tomó Shoter).\n\n")
        for nombre, lineas in hallazgos.items():
            fh.write(f"## {nombre} — {len(lineas)} renglón(es) sospechoso(s)\n\n")
            for linea in lineas:
                fh.write(f"- {linea}\n")
            fh.write("\n")
    registrar(f"Reporte: {SALIDA / 'reporte.md'} · {total} renglones sospechosos · fotos fallidas: {fotos_fallidas}")
    if fotos_fallidas:
        return 5
    return 6 if total else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preparar")
    r = sub.add_parser("recorrer")
    r.add_argument("--url", default="http://127.0.0.1:8011")
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(preparar() if args.cmd == "preparar" else recorrer(args.url.rstrip("/")))


if __name__ == "__main__":
    main()
