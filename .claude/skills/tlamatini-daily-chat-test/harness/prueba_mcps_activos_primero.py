# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""Prueba VISIBLE del orden ACTIVOS-PRIMERO del diálogo External ▸ MCPs.

Angela, 2026-08-02. Los tests de Python prueban la LÓGICA; esto prueba lo que
de verdad se ve en pantalla, en Chrome de verdad, en tu escritorio de verdad.

REGLAS QUE OBEDECE (duras, tuyas):
  * NADA de headless: Chrome REAL, headed (channel="chrome").
  * La foto la toma SHOTER, el agent de Tlamatini. PIL.ImageGrab PROHIBIDO.
  * Foto de PANTALLA COMPLETA, con el reloj de la barra de tareas visible.
  * Nunca se reporta como PASA algo que no se vio de verdad.

ES DE SÓLO LECTURA CON TU CATÁLOGO: abre el diálogo, lee el orden que
renderizó y lo cierra con **Cancelar**. No prende, no apaga y no guarda
NADA — tu conjunto de servers activos queda exactamente como estaba.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# PROHIBIDO PIL.ImageGrab (Angela, 2026-08-02): las fotos las toma
# SHOTER, el agent de Tlamatini. Ver shoter_foto.py.
from shoter_foto import toma_foto  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = r"C:\Development\Tlamatini-Spanish"
DJANGO_DIR = os.path.join(RAIZ, "Tlamatini")
PUERTO = 8000

SEL = {
    "usuario": "#id_username",
    "clave": "#id_password",
    "entrar": "form button[type=submit]",
    "ir_al_chat": "a.btn-primary:has-text('Ir al Chat')",
    # OJO: "MCPs" vive DENTRO del desplegable "Externos". El enlace existe en
    # el DOM desde el principio pero está OCULTO, así que hay que abrir el menú
    # primero. La 3ª corrida murió justo aquí: 63 intentos viendo el enlace
    # "hidden". Lo dijo la bitácora, no la foto.
    "menu_externos": "#external-menu-button",
    "menu_mcps": "#external-mcps",
    "dialogo": "#external-mcps-dialog-message",
    "lista": "#external-mcps-list",
    "leyenda": "#external-mcps-legend",
    "chip": "#external-mcps-chip",
    "cancelar": "#external-mcps-cancel",
}

# Los textos que ESTE árbol (español) debe mostrar, y el inglés que NO.
ENCABEZADO_ACTIVOS = "Activos — se mandan con tu prompt"
ENCABEZADO_RESTO = "Catálogo — inactivos"
LEYENDA_FRAGMENTO = "los activos se quedan fijos hasta arriba"
DEL_OTRO_IDIOMA = ("Active — sent with your prompt", "Catalog — inactive")

RESULTADOS: list = []
FOTOS: list = []
SALIDA = ""
_PAGE = None


def log(m: str) -> None:
    """A la consola VISIBLE y ADEMÁS a un archivo.

    La 2ª corrida murió y la foto de la excepción salió con otra app al frente
    (Chrome ya estaba cerrado), así que no hubo forma de leer el error. Un test
    cuyo fallo no se puede leer es un mal test: desde aquí todo queda en
    bitacora.log junto a las fotos.
    """
    linea = "[%s] %s" % (_dt.datetime.now().strftime("%H:%M:%S"), m)
    print(linea, flush=True)
    if SALIDA:
        try:
            with open(os.path.join(SALIDA, "bitacora.log"), "a",
                      encoding="utf-8") as fh:
                fh.write(linea + "\n")
        except OSError:
            pass


def foto(nombre: str) -> None:
    """Foto de PANTALLA COMPLETA — Chrome al frente y el reloj visible."""
    global _PAGE
    if _PAGE is not None:
        try:
            _PAGE.bring_to_front()
            time.sleep(0.5)
        except Exception:
            pass
    ruta = os.path.join(SALIDA, "%02d_%s.png" % (len(FOTOS), nombre))
    toma_foto(os.path.dirname(ruta), os.path.basename(ruta))
    FOTOS.append(os.path.basename(ruta))


def check(nombre: str, ok: bool, detalle: str) -> None:
    RESULTADOS.append({"check": nombre, "pass": bool(ok), "detalle": detalle})
    log(("   PASA   " if ok else "   FALLA  ") + "%s — %s" % (nombre, detalle))


def credenciales() -> tuple:
    p = os.path.join(AQUI, ".creds.env")
    u = c = ""
    if os.path.isfile(p):
        for ln in open(p, encoding="utf-8", errors="replace"):
            if ln.strip().startswith("#") or "=" not in ln:
                continue
            k, v = ln.split("=", 1)
            if k.strip() == "TLAMATINI_USER":
                u = v.strip()
            elif k.strip() == "TLAMATINI_PASS":
                c = v.strip()
    return u, c


def puerto_abierto(puerto: int) -> bool:
    s = socket.socket()
    s.settimeout(1.5)
    try:
        s.connect(("127.0.0.1", puerto))
        return True
    except Exception:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def arranca_servidor(puerto: int):
    if puerto_abierto(puerto):
        log("el servidor ya estaba arriba")
        return None
    log("arrancando el servidor español en una consola VISIBLE…")
    p = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "--noreload",
         "127.0.0.1:%d" % puerto],
        cwd=DJANGO_DIR,
        creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
    )
    for _ in range(90):
        time.sleep(1)
        if puerto_abierto(puerto):
            log("servidor arriba")
            return p
    log("!! el servidor NO levantó")
    return p


def lee_lista(page) -> dict:
    """Lee de la PANTALLA el orden renderizado y los encabezados de grupo."""
    return page.evaluate("""() => {
        const cont = document.getElementById('external-mcps-list');
        if (!cont) return {existe: false};
        const filas = [];
        const grupos = [];
        const secuencia = [];
        for (const nodo of cont.children) {
            if (nodo.classList.contains('emx-group')) {
                grupos.push((nodo.textContent || '').trim());
                secuencia.push({tipo: 'grupo',
                                texto: (nodo.textContent || '').trim()});
            } else if (nodo.classList.contains('emx-row')) {
                const nombre = (nodo.querySelector('.emx-name')
                                || nodo).textContent || '';
                filas.push({
                    key: nodo.dataset.key || '',
                    activo: nodo.classList.contains('on'),
                    texto: nombre.trim().split('\\n')[0].trim(),
                });
                secuencia.push({tipo: 'fila',
                                key: nodo.dataset.key || '',
                                activo: nodo.classList.contains('on')});
            }
        }
        const leyenda = document.getElementById('external-mcps-legend');
        const chip = document.getElementById('external-mcps-chip');
        return {
            existe: true, filas, grupos, secuencia,
            leyenda: (leyenda && leyenda.textContent || '').trim(),
            chip: (chip && chip.textContent || '').trim(),
        };
    }""")


def main() -> int:
    global SALIDA, _PAGE
    SALIDA = os.path.join(
        AQUI, "resultados",
        "mcps_activos_primero_" + _dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(SALIDA, exist_ok=True)
    log("salida: " + SALIDA)

    usuario, clave = credenciales()
    if not usuario or not clave:
        log("!! no encontré TLAMATINI_USER / TLAMATINI_PASS en .creds.env")
        return 2

    proc = arranca_servidor(PUERTO)
    if not puerto_abierto(PUERTO):
        log("!! sin servidor no hay prueba visible — me detengo (no invento un PASA)")
        return 2

    codigo = 1
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=False, channel="chrome",
                                 args=["--start-maximized"])
        ctx = nav.new_context(no_viewport=True)
        page = ctx.new_page()
        _PAGE = page
        try:
            base = "http://127.0.0.1:%d" % PUERTO
            log("abriendo el login…")
            page.goto(base + "/agent/agent/", wait_until="domcontentloaded")
            if page.locator(SEL["usuario"]).count():
                page.fill(SEL["usuario"], usuario)
                page.fill(SEL["clave"], clave)          # nunca se imprime
                page.click(SEL["entrar"])
                page.wait_for_load_state("domcontentloaded")
            # El login NO cae en el chat: cae en la página de bienvenida, con un
            # botón "Ir al Chat". Sin este paso el diálogo no existe todavía y
            # el harness truena buscando #external-mcps (pasó la 1ª corrida).
            page.wait_for_timeout(1500)
            if page.locator(SEL["ir_al_chat"]).count():
                log("estoy en la bienvenida — entrando al chat…")
                foto("01_bienvenida")
                page.click(SEL["ir_al_chat"])
                page.wait_for_load_state("domcontentloaded")
            page.wait_for_selector(SEL["menu_externos"], timeout=30000)
            page.wait_for_timeout(2500)
            foto("02_chat_cargado")

            log("abriendo el menú Externos…")
            page.click(SEL["menu_externos"])
            page.wait_for_selector(SEL["menu_mcps"] + ":visible", timeout=15000)
            page.wait_for_timeout(600)
            log("abriendo External ▸ MCPs…")
            page.click(SEL["menu_mcps"])
            page.wait_for_selector(SEL["dialogo"] + ":not([hidden])", timeout=20000)
            page.wait_for_timeout(2500)   # deja que pinte la lista
            foto("02_dialogo_mcps_abierto")

            datos = lee_lista(page)
            if not datos.get("existe"):
                check("el diálogo renderizó", False, "no encontré #external-mcps-list")
            else:
                filas = datos["filas"]
                log("chip: %s" % datos["chip"])
                log("leyenda: %s" % datos["leyenda"])
                for f in filas:
                    log("   %-9s %s" % ("ACTIVO" if f["activo"] else "inactivo",
                                        f["key"] or f["texto"]))

                activos = [f for f in filas if f["activo"]]
                inactivos = [f for f in filas if not f["activo"]]

                # 1. no hay ningún activo DESPUÉS de un inactivo
                idx_ult_activo = max(
                    [i for i, f in enumerate(filas) if f["activo"]], default=-1)
                idx_1er_inactivo = min(
                    [i for i, f in enumerate(filas) if not f["activo"]],
                    default=len(filas))
                check("los activos van hasta arriba",
                      idx_ult_activo < idx_1er_inactivo,
                      "%d activo(s), %d inactivo(s); último activo en la posición %d, "
                      "primer inactivo en la %d"
                      % (len(activos), len(inactivos), idx_ult_activo, idx_1er_inactivo))

                # 2. los encabezados de grupo, en español
                grupos = datos["grupos"]
                if activos and inactivos:
                    check("encabezado 'Activos' en español",
                          ENCABEZADO_ACTIVOS in grupos, repr(grupos))
                    check("encabezado 'Catálogo' en español",
                          ENCABEZADO_RESTO in grupos, repr(grupos))
                else:
                    check("encabezados de grupo",
                          not grupos,
                          "un solo bloque -> sin encabezados, correcto")

                # 3. la leyenda dice lo nuevo, en español
                check("la leyenda anuncia el orden",
                      LEYENDA_FRAGMENTO in datos["leyenda"], datos["leyenda"])

                # 4. NADA en inglés
                todo = " ".join(grupos) + " " + datos["leyenda"]
                fugas = [t for t in DEL_OTRO_IDIOMA if t in todo]
                check("sin texto del otro idioma", not fugas, repr(fugas) or "limpio")

            log("cerrando con CANCELAR — tu catálogo no se toca")
            page.click(SEL["cancelar"])
            page.wait_for_timeout(1200)
            foto("03_cerrado_sin_guardar")

            codigo = 0 if all(r["pass"] for r in RESULTADOS) and RESULTADOS else 1
        except Exception as e:
            import traceback
            log("!! excepción: %r" % (e,))
            for ln in traceback.format_exc().split("\n"):
                log("   | " + ln)
            # Qué se ve REALMENTE en la página cuando truena — sin esto uno
            # adivina. La foto puede salir con otra app al frente si Chrome ya
            # murió, así que la verdad la da el DOM, no la imagen.
            try:
                log("   url: %s" % page.url)
                log("   título: %s" % page.title())
                visible = page.evaluate(
                    "() => (document.body ? document.body.innerText : '')"
                    ".trim().slice(0, 700)")
                for ln in str(visible).split("\n")[:25]:
                    log("   pantalla| " + ln)
            except Exception as e2:
                log("   (no pude leer la página: %r)" % (e2,))
            try:
                foto("99_excepcion")
            except Exception:
                pass
        finally:
            try:
                ctx.close()
                nav.close()
            except Exception:
                pass

    with open(os.path.join(SALIDA, "resultado.json"), "w", encoding="utf-8") as fh:
        json.dump({"checks": RESULTADOS, "fotos": FOTOS}, fh,
                  ensure_ascii=False, indent=2)

    pasa = sum(1 for r in RESULTADOS if r["pass"])
    log("")
    log("=" * 62)
    log("RESULTADO: %d/%d checks pasaron" % (pasa, len(RESULTADOS)))
    for r in RESULTADOS:
        log(("  PASA   " if r["pass"] else "  FALLA  ") + r["check"])
    log("fotos (tomadas por Shoter): %d en %s" % (len(FOTOS), SALIDA))
    log("=" * 62)
    if proc is not None:
        log("(el servidor se queda arriba; ciérralo tú cuando quieras)")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
