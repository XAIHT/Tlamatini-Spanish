# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creada por  Angela López Mendoza   ·   @angelahack1
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no quitar
r"""
PRUEBA VISIBLE — el saludo de entrada y el diálogo de permiso
============================================================

DOS COSAS QUE ANGELA LEE TODOS LOS DÍAS

  1. El SALUDO de la pantalla de bienvenida. Decía "Bienvenida(o), angela!":
     un paréntesis a media palabra en el primer texto del día, y sin la
     apertura "¡". El propio catálogo (i18n/ui_es.py:47-48) ya mandaba usar
     género neutro — el template no lo estaba respetando.

  2. El intro del diálogo de Ask Execs. Decía "Tlamatini quiere ejecutar lo
     siguiente…": ella hablando de sí misma en tercera persona, como si un
     tercero reportara sobre un aparato. Ahora dice "Quiero ejecutar…".
     ⚠️ Esa frase vive DUPLICADA en agent_page.html y en ui_es.py; esta prueba
     mira la PANTALLA, así que se entera si alguna de las dos se queda atrás.

Las fotos las toma SHOTER. Chrome real, con ventana; `--headless` PROHIBIDO.
"""
from __future__ import annotations

import datetime as _dt
import os
import socket
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

from shoter_foto import toma_foto

AQUI = os.path.dirname(os.path.abspath(__file__))
DIR_DJANGO = r"C:\Development\Tlamatini-Spanish\Tlamatini"

RESULTADOS: list = []


def revisa(nombre, ok, detalle):
    RESULTADOS.append((nombre, bool(ok), detalle))
    print(("   PASA  " if ok else "   FALLA  ") + "%s — %s" % (nombre, detalle))


def credenciales():
    u = c = ""
    p = os.path.join(AQUI, ".creds.env")
    if os.path.isfile(p):
        for ln in open(p, encoding="utf-8", errors="replace"):
            if "=" in ln and not ln.strip().startswith("#"):
                k, v = ln.split("=", 1)
                if k.strip() == "TLAMATINI_USER":
                    u = v.strip()
                elif k.strip() == "TLAMATINI_PASS":
                    c = v.strip()
    return u, c


def puerto_abierto(p=8000):
    s = socket.socket()
    s.settimeout(1.5)
    try:
        s.connect(("127.0.0.1", p))
        return True
    except Exception:
        return False
    finally:
        s.close()


def main():
    if "--headless" in sys.argv:
        print("!!! HEADLESS ESTÁ PROHIBIDO. Las pruebas se ven o no se corren.")
        return 2

    salida = os.path.join(AQUI, "reports",
                          "saludo_es_" + _dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(salida, exist_ok=True)
    usuario, password = credenciales()
    if not usuario:
        print("!! faltan credenciales")
        return 2

    srv = None
    if not puerto_abierto():
        print("arrancando el server…")
        srv = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", "--noreload", "127.0.0.1:8000"],
            cwd=DIR_DJANGO, creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
        for _ in range(60):
            time.sleep(1)
            if puerto_abierto():
                break

    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=False, channel="chrome",
                                 args=["--start-maximized"])
        page = nav.new_context(no_viewport=True).new_page()
        try:
            # ── 1. el saludo de bienvenida ──────────────────────────────────
            page.goto("http://127.0.0.1:8000/", wait_until="domcontentloaded")
            page.fill("#id_username", usuario)
            page.fill("#id_password", password)
            page.click("form button[type=submit]")
            page.wait_for_load_state("domcontentloaded")
            time.sleep(1.5)
            page.bring_to_front()
            time.sleep(0.4)
            toma_foto(salida, "00_saludo.png")

            saludo = page.evaluate(
                """() => (document.querySelector('.card-title')||{}).textContent || ''""")
            saludo = (saludo or "").strip()
            revisa("hay saludo de bienvenida", bool(saludo), "texto=%r" % saludo[:60])
            revisa("el saludo es de género neutro",
                   "Bienvenida(o)" not in saludo and "Bienvenido," not in saludo,
                   "ya no dice 'Bienvenida(o)'")
            revisa("abre con el signo ¡", saludo.startswith("¡"),
                   "empieza con %r" % saludo[:3])
            revisa("usa la fórmula del catálogo",
                   "Te damos la bienvenida" in saludo,
                   "i18n/ui_es.py:47-48")

            # ── 2. el diálogo de permiso ────────────────────────────────────
            page.goto("http://127.0.0.1:8000/agent/agent/",
                      wait_until="domcontentloaded")
            page.wait_for_selector("#exec-perm-intro", timeout=25000, state="attached")
            intro = page.evaluate(
                """() => (document.getElementById('exec-perm-intro')||{}).textContent || ''""")
            intro = (intro or "").strip()
            page.bring_to_front()
            time.sleep(0.4)
            toma_foto(salida, "01_chat.png")

            revisa("el intro del permiso existe", bool(intro), "texto=%r" % intro[:60])
            revisa("Tlamatini habla en PRIMERA persona",
                   intro.startswith("Quiero"),
                   "dice %r" % intro[:34])
            revisa("ya no habla de sí misma en tercera persona",
                   "Tlamatini quiere" not in intro,
                   "'Tlamatini quiere' ausente")
        except Exception as exc:
            revisa("la prueba corrió sin reventar", False, str(exc)[:160])
            toma_foto(salida, "99_error.png")
        finally:
            time.sleep(2)
            nav.close()
            if srv is not None:
                try:
                    srv.kill()
                except Exception:
                    pass

    fallas = [r for r in RESULTADOS if not r[1]]
    print("=" * 62)
    print("  %d de %d revisiones PASAN" % (len(RESULTADOS) - len(fallas),
                                           len(RESULTADOS)))
    print("  fotos (por Shoter): %s" % salida)
    print("  VEREDICTO: %s" % ("TODO BIEN" if not fallas else "HAY FALLAS"))
    print("=" * 62)
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
