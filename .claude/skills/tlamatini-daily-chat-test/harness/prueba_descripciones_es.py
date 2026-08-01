# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creada por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no quitar
r"""
PRUEBA VISIBLE — las descripciones de los agents en ESPAÑOL
==========================================================

QUÉ PRUEBA DE VERDAD
    Que las 86 descripciones de agents se ven EN ESPAÑOL en las DOS superficies
    donde Angela realmente las lee, con el navegador abierto en su pantalla:

      1. el TOOLTIP al pasar el mouse sobre un agent del sidebar del ACP
      2. el CUERPO del diálogo Descripción al hacer clic derecho sobre un nodo

    No revisa el archivo: revisa la PANTALLA. Un test que sólo abriera el .md
    habría pasado aunque el resolver de idioma nunca se hubiera cableado (que
    era justo el hallazgo: existía el texto pero nadie lo leía), y también
    habría pasado si el drop de `collectstatic` dejara el JS viejo sirviéndose.

SIEMPRE VISIBLE (regla de Angela, no se negocia)
    Chrome real, con ventana. `--headless` está PROHIBIDO y este archivo se
    niega a correr si se lo pasan. Una captura de PANTALLA COMPLETA por paso,
    con el reloj de la barra de tareas a la vista.

NO MIENTE
    * ESPERA a que el tooltip aparezca de verdad (con timeout); nunca supone.
    * Revisa que el texto esté en español Y que NO se haya quedado el inglés.
    * Arrastra el agent al canvas con el drag REAL de la interfaz (HTML5
      dataTransfer), no llamando a funciones internas por atrás.
    * Si el server no levanta, es FALLA — no se salta.

CONTRASEÑA
    Se lee de .creds.env (gitignored). Nunca se imprime, nunca va en la línea
    de comandos.

USO
    python prueba_descripciones_es.py
    python prueba_descripciones_es.py --port 8000
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

try:
    from PIL import ImageGrab
except Exception:  # pragma: no cover
    ImageGrab = None

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = r"C:\Development\Tlamatini-Spanish"
DIR_DJANGO = os.path.join(RAIZ, "Tlamatini")

# El agent con el que se prueba: existe siempre y su descripción es corta.
AGENT = "Executer"
# Arranque de la descripción en español y su equivalente en inglés, para exigir
# el uno y prohibir el otro.
ESPERADO_ES = "Ejecuta un comando de shell"
PROHIBIDO_EN = "Runs an arbitrary shell command"

# Arranques típicos del inglés: si una descripción empieza así, no se tradujo.
ARRANQUES_EN = ("Runs ", "Takes ", "Sends ", "Watches ", "The ", "An ", "A ",
                "Bridge ", "Drives ", "Reads ", "Writes ")

SEL = {
    "usuario": "#id_username",
    "password": "#id_password",
    "entrar": "form button[type=submit]",
    "sidebar": "#agents-container",
    "item": '.agent-tool-item[data-content="%s"]' % AGENT,
    "tooltip": "#agent-purpose-tooltip",
    "canvas": "#submonitor-container",
    "nodo": ".canvas-item",
    "dlg_cuerpo": "#agent-description-content",
    "dlg": "#agent-description-dialog",
}

RESULTADOS: list = []
FOTOS: list = []
SALIDA = ""
_PAGINA = None


def log(m: str) -> None:
    print("[%s] %s" % (_dt.datetime.now().strftime("%H:%M:%S"), m), flush=True)


def foto(nombre: str) -> None:
    """Captura de TODO el escritorio — Chrome al frente, reloj a la vista."""
    global _PAGINA
    if _PAGINA is not None:
        try:
            _PAGINA.bring_to_front()
            time.sleep(0.4)
        except Exception:
            pass
    ruta = os.path.join(SALIDA, "%02d_%s.png" % (len(FOTOS), nombre))
    if ImageGrab is not None:
        try:
            ImageGrab.grab(all_screens=True).save(ruta)
        except Exception as exc:
            log("(no se pudo capturar: %s)" % exc)
    FOTOS.append(os.path.basename(ruta))


def revisa(nombre: str, ok: bool, detalle: str) -> None:
    RESULTADOS.append({"revision": nombre, "pasa": bool(ok), "detalle": detalle})
    log(("   PASA  " if ok else "   FALLA  ") + "%s — %s" % (nombre, detalle))


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


def arranca_server(puerto: int):
    if puerto_abierto(puerto):
        log("el server ya estaba arriba")
        return None
    log("arrancando el server…")
    p = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "--noreload",
         "127.0.0.1:%d" % puerto],
        cwd=DIR_DJANGO,
        creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
    )
    for _ in range(60):
        time.sleep(1)
        if puerto_abierto(puerto):
            log("el server está arriba")
            return p
    log("!! el server NO levantó")
    return p


def main() -> int:
    global SALIDA, _PAGINA
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--headless", action="store_true",
                    help="PROHIBIDO — está sólo para poder negarse")
    args = ap.parse_args()

    if args.headless:
        print("!!! HEADLESS ESTÁ PROHIBIDO EN ESTE PROYECTO. "
              "Las pruebas se ven o no se corren.")
        return 2

    sello = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    SALIDA = os.path.join(AQUI, "reports", "descripciones_es_%s" % sello)
    os.makedirs(SALIDA, exist_ok=True)

    usuario, password = credenciales()
    if not usuario or not password:
        log("!! no encontré TLAMATINI_USER / TLAMATINI_PASS en .creds.env")
        return 2

    print("=" * 74)
    print("  PRUEBA VISIBLE — descripciones de agents en ESPAÑOL")
    print("=" * 74)
    print("  árbol   : %s" % RAIZ)
    print("  puerto  : %d" % args.port)
    print("  usuario : %s   (la contraseña NUNCA se imprime)" % usuario)
    print("  reporte : %s" % SALIDA)
    print("=" * 74)

    srv = arranca_server(args.port)
    if not puerto_abierto(args.port):
        revisa("el server levanta", False, "no levantó")
        return 1

    base = "http://127.0.0.1:%d" % args.port
    with sync_playwright() as pw:
        navegador = pw.chromium.launch(headless=False, channel="chrome",
                                       args=["--start-maximized"])
        ctx = navegador.new_context(no_viewport=True)
        page = ctx.new_page()
        _PAGINA = page
        try:
            # ── 1. entrar y abrir el diseñador ──────────────────────────────
            page.goto(base + "/", wait_until="domcontentloaded")
            page.fill(SEL["usuario"], usuario)
            page.fill(SEL["password"], password)      # nunca se imprime
            page.click(SEL["entrar"])
            page.wait_for_load_state("domcontentloaded")
            page.goto(base + "/agent/agentic_control_panel/",
                      wait_until="domcontentloaded")
            page.wait_for_selector(SEL["sidebar"], timeout=20000)
            foto("01_acp_abierto")

            # ── 2. el mapa que el backend inyectó ───────────────────────────
            mapa = page.evaluate("""() => {
                const el = document.getElementById('agent-purpose-map');
                if (!el) { return null; }
                try { return JSON.parse(el.textContent || '{}'); }
                catch (e) { return null; }
            }""")
            revisa("el backend inyectó el mapa de descripciones",
                   isinstance(mapa, dict) and len(mapa) > 0,
                   "%d agents" % (len(mapa) if isinstance(mapa, dict) else 0))

            if isinstance(mapa, dict):
                en_ingles = [k for k, v in mapa.items()
                             if isinstance(v, str) and v.startswith(ARRANQUES_EN)]
                revisa("NINGUNA descripción quedó en inglés",
                       not en_ingles,
                       "en inglés: %d %s" % (len(en_ingles), sorted(en_ingles)[:5]))

            # ── 3. TOOLTIP del sidebar (superficie 1) ───────────────────────
            item = page.locator(SEL["item"]).first
            item.scroll_into_view_if_needed()
            item.hover()
            texto_tt = ""
            try:
                page.wait_for_selector(SEL["tooltip"], state="visible", timeout=8000)
                texto_tt = (page.locator(SEL["tooltip"]).first.inner_text() or "").strip()
            except Exception as exc:
                log("(el tooltip no apareció: %s)" % str(exc)[:90])
            foto("02_tooltip_sidebar")

            revisa("aparece el tooltip del sidebar", bool(texto_tt),
                   "texto=%r" % texto_tt[:70])
            revisa("el tooltip está en ESPAÑOL",
                   ESPERADO_ES.lower() in texto_tt.lower(),
                   "se esperaba %r" % ESPERADO_ES)
            revisa("el tooltip NO se quedó en inglés",
                   PROHIBIDO_EN.lower() not in texto_tt.lower(),
                   "%r ausente" % PROHIBIDO_EN)

            # ── 4. arrastrar el agent al canvas (drag REAL de la interfaz) ──
            page.mouse.move(0, 0)
            item.drag_to(page.locator(SEL["canvas"]).first)
            nodo = page.locator(SEL["nodo"]).first
            try:
                nodo.wait_for(state="visible", timeout=8000)
                hay_nodo = True
            except Exception:
                hay_nodo = False
            foto("03_nodo_en_canvas")
            revisa("el agent cayó en el canvas", hay_nodo,
                   "nodos=%d" % page.locator(SEL["nodo"]).count())

            # ── 5. DIÁLOGO Descripción (superficie 2) ───────────────────────
            cuerpo = ""
            if hay_nodo:
                nodo.click(button="right")
                time.sleep(0.6)
                try:
                    entrada = page.locator(
                        "li:has-text('Descripci'), "
                        "div[role='menuitem']:has-text('Descripci'), "
                        "*[class*='menu'] *:has-text('Descripci')").first
                    entrada.click(timeout=5000)
                except Exception as exc:
                    log("(no se pudo abrir la entrada Descripción: %s)"
                        % str(exc)[:90])
                try:
                    page.wait_for_selector(SEL["dlg_cuerpo"], state="visible",
                                           timeout=8000)
                    cuerpo = (page.locator(SEL["dlg_cuerpo"]).first.inner_text()
                              or "").strip()
                except Exception as exc:
                    log("(el diálogo no apareció: %s)" % str(exc)[:90])
            foto("04_dialogo_descripcion")

            revisa("se abre el diálogo Descripción", bool(cuerpo),
                   "texto=%r" % cuerpo[:70])
            revisa("el diálogo está en ESPAÑOL",
                   ESPERADO_ES.lower() in cuerpo.lower(),
                   "se esperaba %r" % ESPERADO_ES)
            revisa("el diálogo NO se quedó en inglés",
                   PROHIBIDO_EN.lower() not in cuerpo.lower(),
                   "%r ausente" % PROHIBIDO_EN)

            # ── 6. las dos superficies dicen LO MISMO ───────────────────────
            revisa("tooltip y diálogo coinciden",
                   bool(texto_tt) and bool(cuerpo)
                   and texto_tt[:40].lower() in cuerpo.lower(),
                   "las dos leen el mismo dataset.agentPurpose")

            if srv is not None:
                try:
                    srv.kill()
                except Exception:
                    pass
        except Exception as exc:
            revisa("la prueba corrió sin reventar", False, str(exc)[:200])
            foto("99_error")
        finally:
            try:
                time.sleep(2)
                ctx.close()
                navegador.close()
            except Exception:
                pass

    fallas = [r for r in RESULTADOS if not r["pasa"]]
    with open(os.path.join(SALIDA, "resultados.json"), "w", encoding="utf-8") as fh:
        json.dump({"arbol": RAIZ, "revisiones": RESULTADOS, "fotos": FOTOS},
                  fh, ensure_ascii=False, indent=2)

    print("=" * 74)
    print("  %d de %d revisiones PASAN" % (len(RESULTADOS) - len(fallas),
                                           len(RESULTADOS)))
    for f in fallas:
        print("   FALLA: %s — %s" % (f["revision"], f["detalle"]))
    print("  fotos   : %d en %s" % (len(FOTOS), SALIDA))
    print("  VEREDICTO: %s" % ("TODO BIEN" if not fallas else "HAY FALLAS"))
    print("=" * 74)
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
