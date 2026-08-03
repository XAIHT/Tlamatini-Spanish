# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creada por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no quitar
r"""
PRUEBA VISIBLE — los diálogos del chat, en ESPAÑOL de arriba a abajo
===================================================================

QUÉ PRUEBA DE VERDAD
    Que los diálogos que abre agent_page_init.js ya NO salen "mitad y mitad":
    la BARRA DE TÍTULO y las DOS LEYENDAS (h5 + p) en español, no sólo los
    botones. Antes el título decía "Configure Mcps..." y la leyenda
    "MCPs will be used to provide additional information to Tlamatini."
    mientras los botones ya estaban en español.

    Abre cada diálogo HACIENDO CLIC EN EL MENÚ REAL — no llamando a
    OpenMcpsDialog() por atrás. Si el menú se rompe, la prueba se entera.

LO QUE TAMBIÉN CUIDA (y por eso revisa los botones)
    agent_page_dialogs.js estiliza los botones buscándolos por su TEXTO
    (:contains("Continuar") / :contains("Cancelar")). Si la traducción hubiera
    tocado esas etiquetas, los botones seguirían ahí pero SIN estilo. Por eso
    aquí se exige que "Continuar" y "Cancelar" sigan existiendo.

SIEMPRE VISIBLE (regla de Angela)
    Chrome real, con ventana. `--headless` PROHIBIDO. Captura de pantalla
    completa por diálogo, con el reloj a la vista.

USO
    python prueba_dialogos_es.py
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
DIR_DJANGO = r"C:\Development\Tlamatini-Spanish\Tlamatini"

# (nombre, menú a abrir o None, item a clicar, título esperado, leyenda esperada)
CASOS = [
    ("Configurar MCPs", "#mcps-menu-button", "#enable-mcps",
     "Configurar MCPs", "Los MCPs le dan información adicional a Tlamatini."),
    ("Configurar Agents", "#agents-menu-button", "#enable-agents",
     "Configurar Agents", "Los Agents le dan información adicional a Tlamatini."),
    ("Limpiar historial", None, "#clean-history",
     "Confirmación", "¿Seguro que quieres limpiar el historial?"),
]

# Palabras que NO deben aparecer en ningún diálogo.
INGLES_PROHIBIDO = ["Configure Mcps", "Configure Agents", "will be used to provide",
                    "Are you sure", "Confirmation..."]

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
            time.sleep(0.35)
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


def texto_dialogo(page) -> dict:
    """Lee el diálogo jQuery UI que esté abierto: título, leyendas y botones."""
    return page.evaluate("""() => {
        const w = Array.from(document.querySelectorAll('.ui-dialog'))
            .filter(d => d.offsetParent !== null).pop();
        if (!w) { return {abierto: false}; }
        const t = w.querySelector('.ui-dialog-title');
        const cuerpo = w.querySelector('.ui-dialog-content');
        const h5 = cuerpo ? cuerpo.querySelector('h5') : null;
        const p  = cuerpo ? cuerpo.querySelector('p')  : null;
        const botones = Array.from(w.querySelectorAll('.ui-dialog-buttonpane button'))
            .map(b => (b.textContent || '').trim());
        return {
            abierto: true,
            titulo: t ? (t.textContent || '').trim() : '',
            h5: h5 ? (h5.textContent || '').trim() : '',
            p:  p  ? (p.textContent  || '').trim() : '',
            botones: botones,
            todo: (cuerpo ? (cuerpo.innerText || '') : '') + ' ' +
                  (t ? t.textContent : '')
        };
    }""")


def cierra_dialogo(page) -> None:
    try:
        page.evaluate("""() => {
            const w = Array.from(document.querySelectorAll('.ui-dialog'))
                .filter(d => d.offsetParent !== null).pop();
            if (!w) { return; }
            const b = Array.from(w.querySelectorAll('.ui-dialog-buttonpane button'))
                .find(x => /Cancel/i.test(x.textContent || ''));
            if (b) { b.click(); return; }
            const x = w.querySelector('.ui-dialog-titlebar-close');
            if (x) { x.click(); }
        }""")
        time.sleep(0.5)
    except Exception:
        pass


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
    SALIDA = os.path.join(AQUI, "reports", "dialogos_es_%s" % sello)
    os.makedirs(SALIDA, exist_ok=True)

    usuario, password = credenciales()
    if not usuario or not password:
        log("!! faltan credenciales en .creds.env")
        return 2

    print("=" * 74)
    print("  PRUEBA VISIBLE — diálogos del chat en ESPAÑOL")
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
            page.goto(base + "/agent/agent/", wait_until="domcontentloaded")
            page.wait_for_selector("#clean-history", timeout=25000)
            time.sleep(1.5)                      # que asiente el WebSocket
            foto("00_chat_abierto")

            for nombre, menu, item, titulo_esp, leyenda_esp in CASOS:
                log("abriendo: %s" % nombre)
                try:
                    if menu:
                        page.click(menu)
                        time.sleep(0.4)
                    page.click(item)
                    time.sleep(1.0)
                except Exception as exc:
                    revisa("se abre %s" % nombre, False, str(exc)[:110])
                    continue

                d = texto_dialogo(page)
                foto("dialogo_%s" % nombre.replace(" ", "_").lower())

                revisa("se abre %s" % nombre, bool(d.get("abierto")),
                       "titulo=%r" % (d.get("titulo") or "")[:48])
                revisa("%s: TÍTULO en español" % nombre,
                       titulo_esp.lower() in (d.get("titulo") or "").lower(),
                       "se esperaba %r, salió %r" % (titulo_esp, d.get("titulo")))
                leyenda = ((d.get("h5") or "") + " " + (d.get("p") or "")).lower()
                revisa("%s: LEYENDA en español" % nombre,
                       leyenda_esp.lower()[:38] in leyenda,
                       "se esperaba %r" % leyenda_esp[:56])

                todo = d.get("todo") or ""
                colados = [w for w in INGLES_PROHIBIDO if w.lower() in todo.lower()]
                revisa("%s: NO quedó inglés" % nombre, not colados,
                       "colados=%s" % colados)

                # Los botones NO debieron cambiar: agent_page_dialogs.js los
                # busca por texto para estilizarlos.
                botones = " ".join(d.get("botones") or [])
                revisa("%s: los botones siguen siendo Continuar/Cancelar" % nombre,
                       ("Continuar" in botones and "Cancelar" in botones),
                       "botones=%s" % (d.get("botones") or []))

                cierra_dialogo(page)

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
