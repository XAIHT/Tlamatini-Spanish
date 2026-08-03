# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
r"""
PRUEBA VISIBLE — el aviso de "se cayó el backend" en el diseñador ACP (ESPAÑOL)
==============================================================================

QUÉ PRUEBA, DE VERDAD
    Mata el servidor de Tlamatini EN VIVO, con el diseñador ACP abierto en un
    Chrome de carne y hueso, y exige que aparezca la barra roja. Luego lo vuelve
    a levantar y exige que la barra se ponga verde y se esconda sola.

    No revisa el archivo: revisa la PANTALLA. Un test que sólo grepea el .js
    habría pasado aunque el <script> nunca se hubiera incluido en la plantilla
    (que fue exactamente el bug del 2026-08-01: el chequeo "¿ya está incluido?"
    encontró el nombre del archivo DENTRO del comentario que acababa de
    insertar, y se saltó el <script>).

VISIBLE, SIEMPRE (regla de Angela, innegociable)
    Chrome REAL, headed. `--headless` está PROHIBIDO y este archivo se niega a
    correr si se lo pasan. Una foto de PANTALLA COMPLETA por paso, con el reloj
    de la barra de tareas a la vista, para que se pueda comprobar cuándo pasó.

NUNCA MIENTE
    * Espera a que el banner aparezca de VERDAD (con timeout); no asume.
    * Comprueba el TEXTO y el COLOR (la clase -warning / -ok), no sólo que el
      div exista.
    * Comprueba que el idioma sea el de ESTE árbol y que NO se haya colado el
      otro idioma.
    * Si el servidor no se puede levantar, marca FALLO — no "salta" el paso.

CONTRASEÑA
    Se lee de .creds.env (gitignored) — nunca se imprime, nunca se pasa por la
    línea de comandos.

USO
    python prueba_banner_acp.py
    python prueba_banner_acp.py --puerto 8000
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import socket
import subprocess
import sys
import time

try:
    from playwright.sync_api import sync_playwright
except Exception as exc:  # pragma: no cover
    print("!!! Hace falta Playwright: %s" % exc)
    sys.exit(2)

# PROHIBIDO PIL.ImageGrab (Angela, 2026-08-02): las fotos las toma
# SHOTER, el agent de Tlamatini. Ver shoter_foto.py.
from shoter_foto import toma_foto


AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = r"C:\Development\Tlamatini-Spanish"
DJANGO_DIR = os.path.join(RAIZ, "Tlamatini")

# ── Lo que ESTE árbol debe decir, y lo que NO debe decir jamás ───────────────
IDIOMA = "ESPAÑOL"
TEXTO_CAIDO = "Se perdió la conexión con el backend"
TEXTO_VUELTA = "El backend ya volvió"
TEXTO_DEL_OTRO_IDIOMA = "Backend connection lost"

SEL = {
    "usuario": "#id_username",
    "clave": "#id_password",
    "entrar": "form button[type=submit]",
    "banner": "#connection-status",
    "canvas": "#agents-container",
}

ESPERA_BANNER_S = 30      # el latido es cada 8 s; 30 da margen de sobra
RESULTADOS: list = []
FOTOS: list = []
SALIDA = ""
_PAGE = None


def log(m: str) -> None:
    print("[%s] %s" % (_dt.datetime.now().strftime("%H:%M:%S"), m), flush=True)


def foto(nombre: str) -> None:
    """Foto de PANTALLA COMPLETA — con Chrome al frente y el reloj visible."""
    global _PAGE
    if _PAGE is not None:
        try:
            _PAGE.bring_to_front()
            time.sleep(0.4)
        except Exception:
            pass
    ruta = os.path.join(SALIDA, "%02d_%s.png" % (len(FOTOS), nombre))
    toma_foto(os.path.dirname(ruta), os.path.basename(ruta))
    FOTOS.append(os.path.basename(ruta))


def check(nombre: str, ok: bool, detalle: str) -> None:
    RESULTADOS.append({"check": nombre, "pass": bool(ok), "detalle": detalle})
    log(("   PASA  " if ok else "   FALLA ") + "%s — %s" % (nombre, detalle))


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


# ── manejo del servidor ─────────────────────────────────────────────────────
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
    """Arranca runserver en una consola VISIBLE y devuelve el Popen."""
    if puerto_abierto(puerto):
        log("el servidor ya estaba arriba")
        return None
    log("arrancando el servidor…")
    p = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "--noreload",
         "127.0.0.1:%d" % puerto],
        cwd=DJANGO_DIR,
        creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
    )
    for _ in range(60):
        time.sleep(1)
        if puerto_abierto(puerto):
            log("servidor arriba")
            return p
    log("!! el servidor NO levantó")
    return p


def mata_servidor(puerto: int) -> bool:
    """Mata a quien tenga el puerto. Devuelve True si quedó libre."""
    log("MATANDO el servidor (simulando la caída)…")
    try:
        out = subprocess.run(
            ["netstat", "-ano", "-p", "TCP"],
            capture_output=True, text=True, timeout=20).stdout
    except Exception:
        out = ""
    pids = set()
    for ln in out.splitlines():
        if ":%d " % puerto in ln and "LISTENING" in ln.upper():
            partes = ln.split()
            if partes and partes[-1].isdigit():
                pids.add(partes[-1])
    for pid in pids:
        subprocess.run(["taskkill", "/PID", pid, "/T", "/F"],
                       capture_output=True)
    for _ in range(20):
        time.sleep(0.5)
        if not puerto_abierto(puerto):
            log("puerto libre — el backend está caído")
            return True
    log("!! no logré matar el servidor")
    return False


# ── el estado del banner, leído de la PANTALLA ──────────────────────────────
def estado_banner(page) -> dict:
    try:
        return page.evaluate("""() => {
            const el = document.getElementById('connection-status');
            if (!el) { return {existe:false}; }
            const cl = el.className || '';
            const st = window.getComputedStyle(el);
            return {
                existe: true,
                texto: (el.textContent || '').trim(),
                oculto: cl.indexOf('connection-status-hidden') >= 0,
                rojo:   cl.indexOf('connection-status-warning') >= 0,
                verde:  cl.indexOf('connection-status-ok') >= 0,
                visible: st.display !== 'none'
            };
        }""")
    except Exception as exc:
        return {"existe": False, "error": str(exc)}


def espera_banner(page, quiero: str, limite=ESPERA_BANNER_S) -> dict:
    """Espera de VERDAD a que el banner llegue al estado pedido."""
    t0 = time.time()
    ultimo = {}
    while time.time() - t0 < limite:
        ultimo = estado_banner(page)
        if quiero == "rojo" and ultimo.get("rojo") and ultimo.get("visible"):
            return ultimo
        if quiero == "verde" and ultimo.get("verde") and ultimo.get("visible"):
            return ultimo
        if quiero == "oculto" and ultimo.get("oculto"):
            return ultimo
        time.sleep(0.5)
    return ultimo


def main() -> int:
    global SALIDA, _PAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", type=int, default=8000)
    ap.add_argument("--headless", action="store_true",
                    help="PROHIBIDO — está aquí sólo para negarse a correr")
    args = ap.parse_args()

    if args.headless:
        print("!!! HEADLESS ESTÁ PROHIBIDO EN ESTE PROYECTO. "
              "Las pruebas se ven o no se corren.")
        return 2

    sello = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    SALIDA = os.path.join(AQUI, "reports", "banner_acp_es_%s" % sello)
    os.makedirs(SALIDA, exist_ok=True)

    usuario, clave = credenciales()
    if not usuario or not clave:
        log("!! no encontré TLAMATINI_USER / TLAMATINI_PASS en .creds.env")
        return 2

    print("=" * 74)
    print("  PRUEBA VISIBLE — aviso de backend caído en el ACP  (%s)" % IDIOMA)
    print("=" * 74)
    print("  árbol   : %s" % RAIZ)
    print("  puerto  : %d" % args.puerto)
    print("  usuario : %s   (la contraseña NO se imprime)" % usuario)
    print("  reporte : %s" % SALIDA)
    print("=" * 74)

    srv = arranca_servidor(args.puerto)
    if not puerto_abierto(args.puerto):
        check("servidor arriba antes de empezar", False, "no levantó")
        return 1

    base = "http://127.0.0.1:%d" % args.puerto
    codigo = 0
    with sync_playwright() as pw:
        # HEADED, Chrome real, en el escritorio de Angela.
        nav = pw.chromium.launch(headless=False, channel="chrome",
                                 args=["--start-maximized"])
        ctx = nav.new_context(no_viewport=True)
        page = ctx.new_page()
        _PAGE = page
        try:
            # ── 1. entrar y abrir el diseñador ──────────────────────────────
            page.goto(base + "/", wait_until="domcontentloaded")
            page.fill(SEL["usuario"], usuario)
            page.fill(SEL["clave"], clave)          # nunca se imprime
            page.click(SEL["entrar"])
            page.wait_for_load_state("domcontentloaded")
            page.goto(base + "/agent/agentic_control_panel/",
                      wait_until="domcontentloaded")
            page.wait_for_selector(SEL["canvas"], timeout=20000)
            foto("01_acp_abierto")

            st = estado_banner(page)
            check("el banner existe en el DOM", bool(st.get("existe")),
                  "id=connection-status")
            check("arranca ESCONDIDO", bool(st.get("oculto")),
                  "clases=%s" % ("oculto" if st.get("oculto") else st))

            # ── 2. matar el backend ─────────────────────────────────────────
            muerto = mata_servidor(args.puerto)
            check("el backend quedó caído", muerto, "puerto %d libre" % args.puerto)

            st = espera_banner(page, "rojo")
            foto("02_backend_caido")
            check("aparece la barra ROJA", bool(st.get("rojo") and st.get("visible")),
                  "texto=%r" % (st.get("texto", "")[:70]))
            check("el texto es el correcto (%s)" % IDIOMA,
                  TEXTO_CAIDO in (st.get("texto") or ""),
                  "esperaba %r" % TEXTO_CAIDO)
            check("NO trae el otro idioma",
                  TEXTO_DEL_OTRO_IDIOMA not in (st.get("texto") or ""),
                  "no aparece %r" % TEXTO_DEL_OTRO_IDIOMA)

            # ── 3. revivir el backend ───────────────────────────────────────
            srv2 = arranca_servidor(args.puerto)
            check("el backend volvió", puerto_abierto(args.puerto),
                  "puerto %d escuchando" % args.puerto)

            st = espera_banner(page, "verde")
            foto("03_backend_volvio")
            check("la barra se pone VERDE", bool(st.get("verde")),
                  "texto=%r" % (st.get("texto", "")[:70]))
            check("avisa que ya volvió (%s)" % IDIOMA,
                  TEXTO_VUELTA in (st.get("texto") or ""),
                  "esperaba %r" % TEXTO_VUELTA)

            st = espera_banner(page, "oculto", limite=12)
            foto("04_barra_escondida")
            check("la barra se esconde sola", bool(st.get("oculto")),
                  "vuelve a quedar limpia")

            for p in (srv, srv2):
                if p is not None:
                    try:
                        p.kill()
                    except Exception:
                        pass
        except Exception as exc:
            check("la prueba corrió sin explotar", False, str(exc)[:200])
            foto("99_error")
        finally:
            try:
                time.sleep(2)
                ctx.close()
                nav.close()
            except Exception:
                pass

    fallas = [r for r in RESULTADOS if not r["pass"]]
    codigo = 1 if fallas else 0
    with open(os.path.join(SALIDA, "resultados.json"), "w", encoding="utf-8") as fh:
        json.dump({"idioma": IDIOMA, "arbol": RAIZ, "checks": RESULTADOS,
                   "fotos": FOTOS}, fh, ensure_ascii=False, indent=2)

    print("=" * 74)
    print("  %d de %d checks PASAN" % (len(RESULTADOS) - len(fallas), len(RESULTADOS)))
    for f in fallas:
        print("   FALLA: %s — %s" % (f["check"], f["detalle"]))
    print("  fotos   : %d en %s" % (len(FOTOS), SALIDA))
    print("  VEREDICTO: %s" % ("TODO BIEN" if not fallas else "HAY FALLAS"))
    print("=" * 74)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
