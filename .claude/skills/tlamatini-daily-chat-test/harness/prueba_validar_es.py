# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creada por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no quitar
r"""
PRUEBA VISIBLE — la ventana de Validar del diseñador, en ESPAÑOL
================================================================

QUÉ PRUEBA DE VERDAD
    Que al presionar **Validar** en el Agentic Control Panel la ventana ya no
    sale mitad y mitad. Antes el título estaba en español ("Validación del Flow:
    falló ❌") y el CUERPO en inglés ("Validation Failed", "Flow is Valid",
    "All verification checks passed successfully…"), y la lista de errores venía
    revuelta: unos renglones en español y otros en inglés.

    Arma un flow de verdad arrastrando agents al canvas y le pica a Validar.
    No inspecciona el archivo: lee la VENTANA.

SIEMPRE VISIBLE (regla de Angela)
    Chrome real, con ventana. `--headless` PROHIBIDO. Captura de pantalla
    completa, con el reloj de la barra de tareas a la vista.

NO MIENTE
    * ESPERA a que la ventana aparezca de verdad (con timeout).
    * Exige español Y prohíbe explícitamente las frases en inglés que había.
    * Revisa la lista de errores renglón por renglón: si UNO solo sigue en
      inglés, es FALLA (la mezcla es justo lo que molesta).

USO
    python prueba_validar_es.py
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
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
DIR_DJANGO = r"C:\Development\Tlamatini-Spanish\Tlamatini"

# Frases en inglés que ESTABAN en esta ventana y ya no deben aparecer.
PROHIBIDO = [
    "Flow is Valid", "Validation Failed", "Validation Errors Found",
    "Flow Not Validated", "All verification checks passed",
    "must not connect to itself", "references target",
    "can only be connected from", "No validation has been executed",
    "Failed to read agent configurations",
]

# Señales de que el cuerpo SÍ está en español: los cuatro encabezados posibles
# del resultado. Se comparan SIN distinguir mayúsculas — la primera versión de
# esta prueba buscaba "Validación" con mayúscula y el cuerpo dice "La validación
# falló", así que reprobaba una ventana que estaba perfectamente en español.
ESPERADO = [
    "la validación falló",
    "el flow es válido",
    "se encontraron errores de validación",
    "el flow no ha sido validado",
]

AGENTES = ["Starter", "Executer"]

RESULTADOS: list = []
FOTOS: list = []
SALIDA = ""
_PAGINA = None


def log(m: str) -> None:
    print("[%s] %s" % (_dt.datetime.now().strftime("%H:%M:%S"), m), flush=True)


def foto(nombre: str) -> None:
    global _PAGINA
    if _PAGINA is not None:
        try:
            _PAGINA.bring_to_front()
            time.sleep(0.4)
        except Exception:
            pass
    ruta = os.path.join(SALIDA, "%02d_%s.png" % (len(FOTOS), nombre))
    toma_foto(os.path.dirname(ruta), os.path.basename(ruta))
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


def puerto_abierto(p: int) -> bool:
    s = socket.socket()
    s.settimeout(1.5)
    try:
        s.connect(("127.0.0.1", p))
        return True
    except Exception:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def arranca_server(p: int):
    if puerto_abierto(p):
        log("el server ya estaba arriba")
        return None
    log("arrancando el server…")
    proc = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "--noreload", "127.0.0.1:%d" % p],
        cwd=DIR_DJANGO, creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
    for _ in range(60):
        time.sleep(1)
        if puerto_abierto(p):
            log("el server está arriba")
            return proc
    log("!! el server NO levantó")
    return proc


def lee_ventana(page) -> dict:
    return page.evaluate("""() => {
        const w = Array.from(document.querySelectorAll('.ui-dialog'))
            .filter(d => d.offsetParent !== null).pop();
        if (!w) { return {abierta: false}; }
        const t = w.querySelector('.ui-dialog-title');
        const c = w.querySelector('.ui-dialog-content');
        return {
            abierta: true,
            titulo: t ? (t.textContent || '').trim() : '',
            cuerpo: c ? (c.innerText || '').trim() : '',
            botones: Array.from(w.querySelectorAll('.ui-dialog-buttonpane button'))
                .map(b => (b.textContent || '').trim())
        };
    }""")


def main() -> int:
    global SALIDA, _PAGINA
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--headless", action="store_true", help="PROHIBIDO")
    args = ap.parse_args()

    if args.headless:
        print("!!! HEADLESS ESTÁ PROHIBIDO EN ESTE PROYECTO. "
              "Las pruebas se ven o no se corren.")
        return 2

    sello = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    SALIDA = os.path.join(AQUI, "reports", "validar_es_%s" % sello)
    os.makedirs(SALIDA, exist_ok=True)

    usuario, password = credenciales()
    if not usuario or not password:
        log("!! faltan credenciales en .creds.env")
        return 2

    print("=" * 74)
    print("  PRUEBA VISIBLE — la ventana de Validar, en ESPAÑOL")
    print("=" * 74)
    print("  usuario : %s   (la contraseña NUNCA se imprime)" % usuario)
    print("  reporte : %s" % SALIDA)
    print("=" * 74)

    srv = arranca_server(args.port)
    if not puerto_abierto(args.port):
        revisa("el server levanta", False, "no levantó")
        return 1

    base = "http://127.0.0.1:%d" % args.port
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=False, channel="chrome",
                                 args=["--start-maximized"])
        ctx = nav.new_context(no_viewport=True)
        page = ctx.new_page()
        _PAGINA = page
        try:
            page.goto(base + "/", wait_until="domcontentloaded")
            page.fill("#id_username", usuario)
            page.fill("#id_password", password)
            page.click("form button[type=submit]")
            page.wait_for_load_state("domcontentloaded")
            page.goto(base + "/agent/agentic_control_panel/",
                      wait_until="domcontentloaded")
            page.wait_for_selector("#agents-container", timeout=25000)
            time.sleep(1.0)
            foto("00_acp_abierto")

            # ── armar un flow de verdad, arrastrando del sidebar al canvas ──
            for nombre in AGENTES:
                it = page.locator('.agent-tool-item[data-content="%s"]' % nombre).first
                it.scroll_into_view_if_needed()
                it.drag_to(page.locator("#submonitor-container").first)
                time.sleep(0.6)
            nodos = page.locator(".canvas-item").count()
            foto("01_flow_armado")
            revisa("se armó un flow en el canvas", nodos >= 2, "nodos=%d" % nodos)

            # ── Validar ─────────────────────────────────────────────────────
            page.click("#btn-validate")
            v = {}
            try:
                page.wait_for_selector(".ui-dialog:visible", timeout=20000)
                time.sleep(0.8)
                v = lee_ventana(page)
            except Exception as exc:
                log("(no abrió la ventana: %s)" % str(exc)[:90])
            foto("02_ventana_validar")

            revisa("se abre la ventana de Validar", bool(v.get("abierta")),
                   "titulo=%r" % (v.get("titulo") or "")[:52])

            cuerpo = v.get("cuerpo") or ""
            titulo = v.get("titulo") or ""
            todo = titulo + "\n" + cuerpo

            revisa("el TÍTULO está en español",
                   "Validación" in titulo,
                   "titulo=%r" % titulo[:56])

            revisa("el CUERPO está en español",
                   bool(cuerpo) and any(x in cuerpo.lower() for x in ESPERADO),
                   "cuerpo=%r" % cuerpo[:76].replace("\n", " / "))

            colados = [f for f in PROHIBIDO if f.lower() in todo.lower()]
            revisa("NO quedó ni una frase en inglés", not colados,
                   "coladas=%s" % colados)

            # ── la lista de errores, renglón por renglón ────────────────────
            renglones = [r.strip() for r in cuerpo.split("\n") if len(r.strip()) > 18]
            ingles = []
            for r in renglones:
                # un renglón sin acentos Y con palabras claramente inglesas
                if re.search(r"[áéíóúñ¿¡]", r):
                    continue
                if re.search(r"\b(the|must|cannot|which|from|type of|not present|"
                             r"connected|references)\b", r, re.I):
                    ingles.append(r[:70])
            revisa("ningún renglón de la lista quedó en inglés", not ingles,
                   "renglones revisados=%d  en inglés=%s" % (len(renglones), ingles))

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
                nav.close()
            except Exception:
                pass

    fallas = [r for r in RESULTADOS if not r["pasa"]]
    with open(os.path.join(SALIDA, "resultados.json"), "w", encoding="utf-8") as fh:
        json.dump({"revisiones": RESULTADOS, "fotos": FOTOS}, fh,
                  ensure_ascii=False, indent=2)

    print("=" * 74)
    print("  %d de %d revisiones PASAN" % (len(RESULTADOS) - len(fallas), len(RESULTADOS)))
    for f in fallas:
        print("   FALLA: %s — %s" % (f["revision"], f["detalle"]))
    print("  fotos   : %d en %s" % (len(FOTOS), SALIDA))
    print("  VEREDICTO: %s" % ("TODO BIEN" if not fallas else "HAY FALLAS"))
    print("=" * 74)
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
