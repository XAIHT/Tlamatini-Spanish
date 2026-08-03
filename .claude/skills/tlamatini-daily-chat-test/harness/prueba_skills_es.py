# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creada por  Angela López Mendoza   ·   @angelahack1
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no quitar
r"""
PRUEBA VISIBLE — las descripciones de los Skills, en ESPAÑOL
============================================================

Las 28 descripciones son lo ÚNICO que dice para qué sirve cada skill cuando
Angela tiene que decidir cuál prender en ACPX-Skills ▸ Configurar Skills.

Las fotos las toma SHOTER (regla de Angela, 2026-08-02). Chrome real, con
ventana; `--headless` PROHIBIDO.
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

# Frases EXACTAS que ya no deben verse, y sus traducciones que sí.
INGLES = ["Summarize a long text", "Route plain-language", "Look up current weather",
          "Review a git diff", "Run whichever SAST", "Manage Trello boards",
          "Create, edit, validate", "Read and send Gmail"]
ESPANOL = ["Resume un texto largo", "Enruta peticiones", "Administra boards",
           "Revisa un git diff", "Crea, edita, valida"]


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
                          "skills_es_" + _dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
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

    fallas = 0
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=False, channel="chrome",
                                 args=["--start-maximized"])
        page = nav.new_context(no_viewport=True).new_page()
        try:
            page.goto("http://127.0.0.1:8000/", wait_until="domcontentloaded")
            page.fill("#id_username", usuario)
            page.fill("#id_password", password)
            page.click("form button[type=submit]")
            page.wait_for_load_state("domcontentloaded")
            page.goto("http://127.0.0.1:8000/agent/agent/",
                      wait_until="domcontentloaded")
            page.wait_for_selector("#skills-menu-button", timeout=25000)
            time.sleep(2.5)

            page.click("#skills-menu-button")
            time.sleep(0.6)
            page.click('a[onclick*="OpenSkillsConfigureDialog"]')
            time.sleep(2.0)
            page.bring_to_front()
            time.sleep(0.5)
            toma_foto(salida, "00_configurar_skills.png")

            txt = page.evaluate("""() => {
                const w = Array.from(document.querySelectorAll('.ui-dialog'))
                    .filter(d => d.offsetParent !== null).pop();
                return w ? (w.innerText || '').trim() : '';
            }""")

            ing = [p for p in INGLES if p in txt]
            esp = [p for p in ESPANOL if p in txt]

            print("=" * 62)
            print("  texto del diálogo      : %d caracteres" % len(txt))
            print("  descripciones ESPAÑOL  : %d  %s" % (len(esp), esp))
            print("  descripciones INGLÉS   : %d  %s" % (len(ing), ing))
            if not txt:
                print("  FALLA: el diálogo no abrió")
                fallas += 1
            if not esp:
                print("  FALLA: no se vio ninguna descripción en español")
                fallas += 1
            if ing:
                print("  FALLA: quedaron descripciones en inglés")
                fallas += 1
            print("  fotos (por Shoter)     : %s" % salida)
            print("  VEREDICTO: %s" % ("TODO BIEN" if not fallas else "HAY FALLAS"))
            print("=" * 62)
        except Exception as exc:
            print("FALLA: %s" % str(exc)[:200])
            toma_foto(salida, "99_error.png")
            fallas += 1
        finally:
            time.sleep(2)
            nav.close()
            if srv is not None:
                try:
                    srv.kill()
                except Exception:
                    pass
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
