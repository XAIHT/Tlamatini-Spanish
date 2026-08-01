# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""
Tlamatini — 1000 preguntas EN ESPAÑOL a través del chat REAL, con evidencia
fotográfica de pantalla completa (todo el escritorio, con el RELOJ visible)
para CADA pregunta.

Angela's rules this runner obeys, without exception:
  * HEADED, real Chrome, on her real desktop. Never headless (run_test.py
    hard-refuses --headless anyway).
  * One FULL-SCREEN photo per test, taskbar clock visible.
  * NEVER record a stale / transient / busy answer as a pass:
      - busy + "not ready" banners are filtered accent-insensitively
        (config.is_busy_banner / is_not_ready),
      - self-healing "Tactic #..." status frames are rejected and re-asked,
      - an answer identical to the previous question's answer is rejected.
  * Multi-Turn is RE-ASSERTED immediately before every single send.

What it actually judges (this is a SPANISH test, not a smoke test):
  1. ¿contestó?            non-empty, plausible length
  2. ¿contestó EN ESPAÑOL? Spanish function-word score must beat English.
                           A Spanish question answered in English is a FAIL --
                           that is the whole point of the Spanish edition.
  3. ¿respetó el registro? For questions carrying `keep_en`, the English
                           technical noun must survive. A register BREAK is
                           scored only when the English term is ABSENT *and*
                           its Spanish translation is PRESENT -- so an answer
                           that says "un container (contenedor)" is fine, and
                           common Spanish words never cause a false positive.
  4. gemelas de acentos    the 60 accented/unaccented pairs are compared after
                           the run: both halves must reach the same verdict.

Usage (from this folder):
    python prueba_1000_es.py                 # all 1000, resumable
    set ES_N=25 && python prueba_1000_es.py  # a short sanity slice first
"""
import os
import sys
import time
import json
import random
import html
import unicodedata
import datetime as _dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Credentials live in .creds.env (gitignored). Load before importing config.
_CREDS = os.path.join(HERE, ".creds.env")
if os.path.exists(_CREDS):
    with open(_CREDS, "r", encoding="utf-8-sig") as _fh:
        for _line in _fh:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

import config as C          # noqa: E402
import run_test as R        # noqa: E402
from preguntas_es import CORPUS   # noqa: E402

try:
    from PIL import ImageGrab
except Exception as _e:      # pragma: no cover
    print("FATAL: se requiere Pillow (PIL.ImageGrab) para la evidencia:", _e)
    sys.exit(2)

from playwright.sync_api import sync_playwright   # noqa: E402


# ------------------------------------------------------------------- config
N = int(os.environ.get("ES_N", "1000"))
CLEAR_EVERY = int(os.environ.get("ES_CLEAR_EVERY", "15"))
TIMEOUT_MS = int(os.environ.get("ES_TIMEOUT_S", "150")) * 1000

# ⚠️ ORDEN ALEATORIO, NO SECUENCIAL (Angela, 2026-07-30 — obligatorio).
#
# El corpus está AGRUPADO POR CATEGORÍA (concepto 200, registro 120,
# acentos 120, …). Recorrerlo en orden es un error de método por dos razones:
#   1. `CORPUS[:N]` con N chico daba UNA SOLA categoría — un ES_N=25 preguntaba
#      25 veces 'concepto' y jamás tocaba acentos, registro ni mexicano. La
#      corrida parecía verde sin haber probado nada de lo interesante.
#   2. Ir de lo simple a lo complejo en bloques ESCONDE los bugs que dependen
#      del orden y del estado que se arrastra entre preguntas: si las difíciles
#      siempre caen al final, no se distingue "difícil" de "la sesión ya venía
#      degradada".
# Barajar mezcla las categorías y las dificultades, así que un fallo dice algo.
# Igual que run_test.py: por omisión se baraja con una semilla FRESCA que se
# IMPRIME, para poder reproducir exactamente esa corrida con ES_SEED=<n>.
NO_SHUFFLE = os.environ.get("ES_NO_SHUFFLE", "0") not in ("0", "", "false", "False")
_seed_env = os.environ.get("ES_SEED", "").strip()
SEED = int(_seed_env) if _seed_env else None
DJANGO_DIR = os.environ.get(
    "ES_DJANGO_DIR", r"C:\Development\Tlamatini-Spanish\Tlamatini")

# MULTI-TURN: APAGADO por omisión en este corpus. Ver la nota de abajo.
#
# ⚠️ HALLAZGO EN VIVO (2026-07-29, primera corrida): con Multi-Turn ENCENDIDO,
# preguntas perfectamente inocentes como "¿qué puedes hacer por mí?" o
# "¿cuántos agents tienes? Dame un ejemplo." hacen que Tlamatini se comporte
# como OPERADORA y *demuestre* lo que puede hacer: en 97 preguntas disparó
# chat_agent_shoter 78 veces y chat_agent_image_interpreter 90 veces -- se
# tomaba capturas de su PROPIA pantalla y las analizaba con visión en la nube
# (llegó a describir su propio avatar y el reloj de la barra de tareas).
# Eso no es un bug de su español: es su modo operador funcionando. Pero para
# un corpus de IDIOMA es ruido carísimo, y acabó atascando la cadena de un
# solo carril ("RAG chain not ready"), dejando el chat inservible.
#
# Este corpus mide ESPAÑOL (¿contesta en español? ¿respeta el registro?), así
# que corre por la ruta conversacional. Para probar el modo operador en
# español: ES_MULTI_TURN=1 (con un corpus chico, p. ej. ES_N=40).
MULTI_TURN = os.environ.get("ES_MULTI_TURN", "0") not in ("0", "", "false", "False")
RUN_TAG = _dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
RUN_DIR = os.path.join(HERE, "reports", "espanol_1000_%s" % RUN_TAG)
SHOTS_DIR = os.path.join(RUN_DIR, "fotos")
os.makedirs(SHOTS_DIR, exist_ok=True)
RESULTS = os.path.join(RUN_DIR, "resultados.jsonl")
SUMMARY_HTML = os.path.join(RUN_DIR, "RESUMEN.html")


# --------------------------------------------------------------- utilidades
def fold(text):
    """minúsculas + sin diacríticos."""
    d = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in d if not unicodedata.combining(c)).lower()


_ES_WORDS = (
    "que", "de", "la", "el", "los", "las", "un", "una", "para", "con", "por",
    "se", "es", "esta", "esto", "tu", "te", "como", "mas", "pero", "cuando",
    "donde", "puedes", "hacer", "tiene", "del", "al", "sus", "muy", "tambien",
    "porque", "si", "no", "lo", "en", "y", "o", "ya", "asi", "cada", "sobre",
)
_EN_WORDS = (
    "the", "is", "are", "you", "can", "this", "that", "with", "for", "and",
    "your", "what", "how", "when", "which", "will", "would", "should", "there",
    "these", "from", "have", "has", "been", "they", "their", "about", "into",
)

# English term -> Spanish translations that would count as a register BREAK,
# but ONLY when the English term itself is absent from the answer.
_TRADUCCIONES = {
    "container": ("contenedor",),
    "pod": ("vaina", "cápsula"),
    "log": ("bitácora",),
    "path": ("ruta de acceso",),
    "output": ("salida estándar",),
    "input": ("entrada estándar",),
    "token": ("ficha",),
    "endpoint": ("punto final", "punto de conexión"),
    "commit": ("confirmación de cambios",),
    "branch": ("rama",),
    "merge": ("fusión",),
    "buffer": ("memoria intermedia",),
    "thread": ("hilo de ejecución",),
    "deadlock": ("interbloqueo", "abrazo mortal"),
    "socket": ("zócalo",),
    "firewall": ("cortafuegos",),
    "backup": ("copia de seguridad", "respaldo"),
    "script": ("guion", "guión"),
    "framework": ("marco de trabajo",),
    "middleware": ("capa intermedia",),
    "cache": ("memoria caché",),
    "payload": ("carga útil",),
    "timeout": ("tiempo de espera",),
    "deploy": ("despliegue",),
    "breakpoint": ("punto de interrupción",),
    "stack trace": ("traza de pila", "rastro de pila"),
    "query": ("consulta sql",),
    "index": ("índice de la tabla",),
    "pipeline": ("tubería", "canalización"),
    "webhook": ("gancho web",),
    "proxy": ("intermediario de red",),
    "kernel": ("núcleo del sistema",),
    "driver": ("controlador de dispositivo",),
    "rollback": ("reversión",),
    "linter": ("analizador de estilo",),
    "schema": ("esquema de la base",),
    "streaming": ("transmisión continua",),
    "profiling": ("perfilado",),
}


def _score_words(folded, words):
    padded = " " + folded.replace("\n", " ") + " "
    return sum(padded.count(" " + w + " ") for w in words)


def es_o_en(answer):
    """('es'|'en'|'?', es_score, en_score)"""
    f = fold(answer)
    es = _score_words(f, _ES_WORDS)
    en = _score_words(f, _EN_WORDS)
    if es == 0 and en == 0:
        return "?", es, en
    return ("es" if es >= en else "en"), es, en


def revisa_registro(answer, keep_en):
    """Return (perdidos, rotos): terms missing, and terms actually TRANSLATED."""
    f = fold(answer)
    perdidos, rotos = [], []
    for term in keep_en or []:
        if fold(term) in f:
            continue                       # término en inglés presente -> OK
        perdidos.append(term)
        for trad in _TRADUCCIONES.get(term.lower(), ()):
            if fold(trad) in f:
                rotos.append("%s->%s" % (term, trad))
                break
    return perdidos, rotos


# Bilingual on purpose: this is the SPANISH edition, so the live frames say
# "Táctica #N ... sólo tú puedes detenerme". Missing them would let a transient
# status frame be scraped and recorded as a PASS -- exactly the "NEVER LIE" rule.
_TRANSIENT = (
    "I will NOT hang; only you can stop me",
    "retrying the same request",
    "Tactic #",
    "Tactic '",
    "Táctica #",
    "Táctica '",
    "puedes detenerme",
    "cambio a otra táctica",
)


def es_transitorio(ans):
    a = ans or ""
    return any(m in a for m in _TRANSIENT)


def veredicto(q, answer):
    """(estado, razones) -- nunca lanza excepción."""
    a = (answer or "").strip()
    razones = []
    if not a:
        return "FAIL", ["respuesta-vacía"]
    if es_transitorio(a):
        return "FAIL", ["estado-transitorio-del-self-healing"]
    low = a.lower()
    if "traceback (most recent call last)" in low:
        return "FAIL", ["traceback-en-la-respuesta"]

    if len(a) < q.get("min_len", 20):
        razones.append("muy-corta(%d<%d)" % (len(a), q.get("min_len", 20)))

    idioma, es_s, en_s = es_o_en(a)
    if idioma == "en":
        return "FAIL", razones + ["contestó-en-inglés(es=%d,en=%d)" % (es_s, en_s)]
    if idioma == "?":
        razones.append("idioma-indeterminado")

    perdidos, rotos = revisa_registro(a, q.get("keep_en"))
    if rotos:
        return "FAIL", razones + ["registro-roto:" + ",".join(rotos)]
    if perdidos:
        razones.append("término-no-mencionado:" + ",".join(perdidos))

    if razones:
        return "WEAK", razones
    return "PASS", ["español-correcto+registro-respetado"]


# Re-assert the pinned toolbar state right before EVERY send, and return what
# the chat's own submit builder will actually transmit for Multi-Turn.
_JS_FORCE_MT = """(want) => {
    const el = document.querySelector('#multi-turn-enabled');
    if (el && !el.disabled && el.checked !== want) {
        el.checked = want; el.dispatchEvent(new Event('change', {bubbles: true}));
    }
    const other = {'#acpx-enabled': false, '#exec-report-enabled': false,
                   '#ask-execs-enabled': false, '#internetEnabled': false};
    for (const sel of Object.keys(other)) {
        const e2 = document.querySelector(sel);
        if (e2 && !e2.disabled && e2.checked !== other[sel]) {
            e2.checked = other[sel]; e2.dispatchEvent(new Event('change', {bubbles: true}));
        }
    }
    return (typeof isMultiTurnEnabled === 'function') ? isMultiTurnEnabled() : (el ? !!el.checked : null);
}"""


def fuerza_multi_turn(page):
    """Re-afirma el estado de la barra ANTES de cada envío y devuelve lo que
    el propio chat va a transmitir. Devuelve MULTI_TURN cuando coincide."""
    try:
        return page.evaluate(_JS_FORCE_MT, MULTI_TURN)
    except Exception:
        return None


# --------------------------------------------------------- voz de Tlamatini
# Modos de avatar.js: 'silent' (mudo) · 'notify' (frase fija, DEFAULT) ·
# 'speak' (lee la RESPUESTA completa en voz alta). Para esta corrida queremos
# 'speak': Angela tiene que OÍR el español mexicano real, no una frase fija —
# ése es justo el defecto que estamos verificando (antes leía español con voz
# inglesa). La voz sale de Piper vía POST /agent/tts/ cuando Windows no tiene
# ninguna voz es-*; si no hay voz, avatar.js se queda CALLADO a propósito.
_JS_VOZ = """() => {
  try {
    const prev = JSON.parse(localStorage.getItem('tlm_voice_settings') || '{}');
    const next = Object.assign({}, prev, {mode: 'speak', volume: 100});
    localStorage.setItem('tlm_voice_settings', JSON.stringify(next));
    return next.mode;
  } catch (e) { return 'error:' + e; }
}"""


def activa_voz(page):
    """Deja a Tlamatini leyendo cada respuesta en voz alta. Nunca truena."""
    try:
        modo = page.evaluate(_JS_VOZ)
        print("  voz         : modo '%s' (lee la respuesta completa)" % modo)
        return modo == "speak"
    except Exception as exc:
        print("  voz         : no la pude activar (%s) — sigo sin audio" % exc)
        return False


# ------------------------------------------------- recuperación de atascos
def _puerto_abierto(host="127.0.0.1", port=8000, timeout=2.0):
    import socket

    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def reinicia_servidor():
    """Mata lo que tenga el 8000 y relanza el servidor EN UNA VENTANA VISIBLE.

    Existe porque la cadena de un solo carril puede quedarse en
    'RAG chain not ready' para siempre: el server sigue vivo y respondiendo
    HTTP, pero el chat ya no acepta nada y el input nunca se vuelve editable.
    Recargar la página no lo cura -- hay que reconstruir el proceso.
    """
    import subprocess

    print("    !! cadena atascada -> REINICIANDO el servidor")
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-NetTCPConnection -LocalPort 8000 -State Listen "
             "-ErrorAction SilentlyContinue | ForEach-Object { "
             "Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
            capture_output=True, timeout=60)
    except Exception as exc:
        print("       (no se pudo matar el 8000: %s)" % exc)
    time.sleep(4)
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-NoExit", "-Command",
             "$Host.UI.RawUI.WindowTitle='TLAMATINI ESPANOL - SERVIDOR (reiniciado)'; "
             "cd '%s'; python manage.py runserver 8000 --noreload" % DJANGO_DIR],
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
    except Exception as exc:
        print("       (no se pudo relanzar: %s)" % exc)
        return False
    for _ in range(60):          # el arranque tarda (fase GPU-PERF ~40 s)
        if _puerto_abierto():
            print("       servidor de vuelta")
            time.sleep(6)
            return True
        time.sleep(5)
    print("       *** el servidor no volvio ***")
    return False


def asegura_lista(h, espera_s=45):
    """Deja el chat en estado utilizable, escalando hasta lograrlo.

    1) esperar        2) recargar la página        3) limpiar historial
    4) REINICIAR el servidor  (el único remedio real para la cadena atascada)

    Devuelve True si el input quedó editable.
    """
    ms = int(espera_s * 1000)
    if h._wait_editable(timeout_ms=ms):
        return True

    print("    ~ el chat no acepta entrada -> recargo la pagina")
    h.recover()
    if h._wait_editable(timeout_ms=ms):
        return True

    print("    ~ sigue atascado -> limpio historial (reconstruye la cadena)")
    try:
        h.clear_history()
    except Exception:
        pass
    if h._wait_editable(timeout_ms=ms):
        return True

    if reinicia_servidor():
        try:
            h.login()
            h.goto_chat()
            h.set_toggles()
        except Exception as exc:
            print("       (no se pudo re-entrar: %s)" % exc)
        if h._wait_editable(timeout_ms=ms * 2):
            return True
    return False


def foto_pantalla_completa(page, path):
    """TODO el escritorio (incluye el reloj de la barra de tareas)."""
    try:
        page.bring_to_front()
    except Exception:
        pass
    time.sleep(0.25)
    try:
        img = ImageGrab.grab(all_screens=True)
    except TypeError:
        img = ImageGrab.grab()
    img.convert("RGB").save(path, "JPEG", quality=72)
    return path


# ------------------------------------------------------------------ resumen
_COLOR = {"PASS": "#1e8e3e", "WEAK": "#b06000", "FAIL": "#c5221f"}


def escribe_resumen(rows, started_iso, total):
    hechos = len(rows)
    tally = {"PASS": 0, "WEAK": 0, "FAIL": 0}
    por_cat = {}
    for r in rows:
        st = r.get("estado", "FAIL")
        tally[st] = tally.get(st, 0) + 1
        cat = por_cat.setdefault(r.get("category", "?"), {"PASS": 0, "WEAK": 0, "FAIL": 0})
        cat[st] = cat.get(st, 0) + 1

    # gemelas de acentos: ambas mitades deben coincidir
    by_id = {r["id"]: r for r in rows}
    pares_ok = pares_mal = 0
    for r in rows:
        twin = r.get("twin")
        if not twin or twin not in by_id or r["id"] > twin:
            continue
        if r.get("estado") == by_id[twin].get("estado"):
            pares_ok += 1
        else:
            pares_mal += 1

    prom = (sum(r.get("elapsed_s", 0) for r in rows) / hechos) if hechos else 0
    faltan = max(0, total - hechos)
    eta_min = int(faltan * prom / 60)

    parts = ["""<!doctype html><html lang="es"><meta charset="utf-8">
<title>Tlamatini — 1000 preguntas en español</title>
<style>
 body{font-family:Segoe UI,system-ui,sans-serif;margin:24px;background:#fbfbfd;color:#16161a}
 h1{margin:0 0 4px} .sub{color:#5f6368;margin-bottom:18px}
 .cards{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px}
 .card{background:#fff;border:1px solid #e3e3e8;border-radius:10px;padding:12px 18px;min-width:120px}
 .card b{display:block;font-size:26px;line-height:1.1}
 table{border-collapse:collapse;width:100%;background:#fff;font-size:13px}
 th,td{border:1px solid #e3e3e8;padding:6px 8px;vertical-align:top;text-align:left}
 th{background:#f1f3f4;position:sticky;top:0}
 .badge{color:#fff;border-radius:5px;padding:1px 8px;font-weight:600;font-size:12px}
 .q{max-width:340px} .a{max-width:520px;color:#3c4043}
 img{height:52px;border:1px solid #dadce0;border-radius:4px}
</style>
<h1>Tlamatini — 1000 preguntas en español</h1>"""]
    parts.append('<div class="sub">Edición en español · corrida iniciada %s · '
                 'servidor %s · evidencia: una foto de pantalla completa por pregunta</div>'
                 % (html.escape(started_iso), html.escape(C.BASE_URL)))
    parts.append('<div class="cards">')
    for k in ("PASS", "WEAK", "FAIL"):
        parts.append('<div class="card"><b style="color:%s">%d</b>%s</div>'
                     % (_COLOR[k], tally.get(k, 0), k))
    parts.append('<div class="card"><b>%d / %d</b>hechas</div>' % (hechos, total))
    parts.append('<div class="card"><b>%.1f s</b>promedio</div>' % prom)
    parts.append('<div class="card"><b>~%d min</b>faltan</div>' % eta_min)
    parts.append('<div class="card"><b>%d / %d</b>gemelas de acento iguales</div>'
                 % (pares_ok, pares_ok + pares_mal))
    parts.append("</div>")

    parts.append("<h3>Por categoría</h3><table><tr><th>categoría</th>"
                 "<th>PASS</th><th>WEAK</th><th>FAIL</th></tr>")
    for cat in sorted(por_cat):
        c = por_cat[cat]
        parts.append("<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td></tr>"
                     % (html.escape(cat), c["PASS"], c["WEAK"], c["FAIL"]))
    parts.append("</table>")

    parts.append("<h3>Cada pregunta</h3><table><tr><th>#</th><th>cat</th>"
                 "<th>pregunta</th><th>respuesta (recorte)</th><th>estado</th>"
                 "<th>razones</th><th>seg</th><th>evidencia</th></tr>")
    for r in rows:
        st = r.get("estado", "FAIL")
        shot = r.get("foto", "")
        rel = ("fotos/" + os.path.basename(shot)) if shot else ""
        parts.append(
            "<tr><td>%s</td><td>%s</td><td class='q'>%s</td><td class='a'>%s</td>"
            "<td><span class='badge' style='background:%s'>%s</span></td>"
            "<td>%s</td><td>%.1f</td><td>%s</td></tr>"
            % (html.escape(r.get("id", "")),
               html.escape(r.get("category", "")),
               html.escape((r.get("question") or "")[:200]),
               html.escape((r.get("answer") or "")[:400]),
               _COLOR.get(st, "#666"), st,
               html.escape(", ".join(r.get("razones", []))[:160]),
               r.get("elapsed_s", 0),
               ('<a href="%s" target="_blank"><img src="%s"></a>' % (rel, rel)) if rel else ""))
    parts.append("</table></html>")

    with open(SUMMARY_HTML, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))


# --------------------------------------------------------------------- main
class Args:
    """Lo que Harness espera."""
    headless = False          # PROHIBIDO cambiarlo: las pruebas son visibles
    slowmo = 0
    user = os.environ.get("TLAMATINI_USER", "angela")
    password = os.environ.get("TLAMATINI_PASS", "changeme")
    judge_model = os.environ.get("TLAMATINI_JUDGE_MODEL", "")
    # Bajos a propósito: si la cadena está atascada, insistir 6 veces x 12 s
    # sólo tira 72 s por pregunta sin arreglar nada. Quien de verdad lo cura
    # es asegura_lista() (recarga -> limpia historial -> reinicia servidor).
    not_ready_retries = 2
    not_ready_backoff = 8.0


def main():
    # BARAJAR ANTES DE CORTAR. Si se cortara primero (CORPUS[:N]) el subconjunto
    # ya vendría sesgado a la primera categoría y barajarlo después no lo
    # arreglaría — sólo reordenaría el mismo bloque sesgado.
    orden = list(CORPUS)
    if NO_SHUFFLE:
        semilla = None
    else:
        semilla = SEED if SEED is not None else random.randrange(1, 2 ** 31 - 1)
        random.Random(semilla).shuffle(orden)
    preguntas = orden[:N]
    # La barra se fija según ESTE corpus, no según el default del harness.
    C.TOGGLE_STATE["t_multi_turn"] = MULTI_TURN
    started = _dt.datetime.now()
    started_iso = started.isoformat(timespec="seconds")

    print("=" * 74)
    print("  TLAMATINI — 1000 PREGUNTAS EN ESPAÑOL (chat real, Chrome visible)")
    print("=" * 74)
    print("  servidor    : %s" % C.BASE_URL)
    print("  usuario     : %s" % Args.user)
    print("  preguntas   : %d" % len(preguntas))
    if semilla is None:
        print("  orden       : SECUENCIAL (ES_NO_SHUFFLE=1) — ojo: sesgado por categoría")
    else:
        print("  orden       : ALEATORIO  |  semilla=%d" % semilla)
        print("                (repite esta corrida exacta con  set ES_SEED=%d)" % semilla)
        _cats = {}
        for _q in preguntas:
            _cats[_q["category"]] = _cats.get(_q["category"], 0) + 1
        print("  mezcla      : " + ", ".join("%s=%d" % kv for kv in sorted(_cats.items())))
    print("  Multi-Turn  : %s" % ("ENCENDIDO (modo operadora)" if MULTI_TURN
                                  else "APAGADO (corpus de IDIOMA)"))
    print("  reporte     : %s" % RUN_DIR)
    print("  evidencia   : una foto de pantalla completa por pregunta")
    print("=" * 74)

    filas = []
    ultima_respuesta = ""
    args = Args()
    h = R.Harness(args)

    with sync_playwright() as p:
        browser = h.launch(p)
        try:
            h.login()
            h.goto_chat()
            h.set_toggles()
            activa_voz(h.page)      # que se le oiga la voz mexicana

            for i, q in enumerate(preguntas):
                if i and i % CLEAR_EVERY == 0:
                    h.clear_history()

                vacio = {"id": q["id"], "category": q["category"],
                         "question": q["text"], "answer": "", "elapsed_s": 0.0}

                # Antes de escribir nada: dejar el chat realmente utilizable,
                # escalando hasta reiniciar el servidor si hace falta. Sin
                # esto, una cadena atascada convierte la corrida en un bucle
                # infinito de "input still readOnly -> recovering".
                if not asegura_lista(h):
                    print("    !! el chat sigue inservible -> registro FAIL y sigo")
                    mt, rec = None, dict(vacio)
                else:
                    mt = fuerza_multi_turn(h.page)
                    try:
                        rec = h.ask_one(q, TIMEOUT_MS)
                    except Exception as exc:
                        print("    !! excepción: %s" % exc)
                        h.recover()
                        rec = dict(vacio)

                ans = (rec.get("answer") or "").strip()

                # Nunca aceptar un estado transitorio del self-healing.
                #
                # NOTA (corregido en vivo, 2026-07-29): NO se rechaza una
                # respuesta por ser igual a la anterior. La frescura ya está
                # garantizada estructuralmente: run_test._filter_answer sólo
                # devuelve los mensajes POSTERIORES a prev_count, así que un
                # texto repetido es un mensaje NUEVO con el mismo contenido,
                # no un raspado viejo. Y es lo correcto para los saludos: la
                # ruta rápida de saludo (REGEX_GREETING -> MSG_GREETING_RESPONSE)
                # contesta lo MISMO a propósito. Rechazarlo marcaba como FAIL
                # justamente el comportamiento correcto.
                if ans and es_transitorio(ans):
                    print("    ~ estado transitorio del self-healing -> vuelvo a preguntar")
                    try:
                        fuerza_multi_turn(h.page)
                        rec = h.ask_one(q, TIMEOUT_MS)
                        ans = (rec.get("answer") or "").strip()
                    except Exception:
                        pass
                    if es_transitorio(ans):
                        ans = ""      # se rechaza: nunca se registra como respuesta

                estado, razones = veredicto(q, ans)
                if mt != MULTI_TURN:
                    razones.append("multi-turn-no-confirmado(%s, esperado %s)"
                                   % (mt, MULTI_TURN))
                # Una respuesta idéntica a la anterior YA NO se rechaza (ver la
                # nota de arriba), pero fuera de la ruta de saludo -- donde la
                # respuesta canónica se repite a propósito -- sigue siendo una
                # señal que vale la pena anotar, así que baja a WEAK.
                if ans and ans == ultima_respuesta and q["category"] != "saludo":
                    razones.append("respuesta-idéntica-a-la-anterior")
                    if estado == "PASS":
                        estado = "WEAK"
                if ans:
                    ultima_respuesta = ans

                foto = os.path.join(SHOTS_DIR, "%s_%s.jpg" % (q["id"], estado))
                try:
                    foto_pantalla_completa(h.page, foto)
                except Exception as exc:
                    print("    !! no se pudo tomar la foto: %s" % exc)
                    foto = ""

                fila = {
                    "id": q["id"], "category": q["category"], "twin": q.get("twin"),
                    "question": q["text"], "answer": ans,
                    "estado": estado, "razones": razones,
                    "elapsed_s": rec.get("elapsed_s", 0.0),
                    "multi_turn": mt, "foto": foto,
                    "ts": _dt.datetime.now().isoformat(timespec="seconds"),
                }
                filas.append(fila)
                with open(RESULTS, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(fila, ensure_ascii=False) + "\n")
                escribe_resumen(filas, started_iso, len(preguntas))

                print("  [%4d/%4d] %s %-13s %-5s %5.1fs  %s"
                      % (i + 1, len(preguntas), q["id"], q["category"], estado,
                         fila["elapsed_s"], (q["text"][:52] + "...")))

        finally:
            escribe_resumen(filas, started_iso, len(preguntas))
            try:
                browser.close()
            except Exception:
                pass

    tally = {}
    for r in filas:
        tally[r["estado"]] = tally.get(r["estado"], 0) + 1
    print("=" * 74)
    print("  TERMINADO  PASS=%d  WEAK=%d  FAIL=%d  de %d"
          % (tally.get("PASS", 0), tally.get("WEAK", 0), tally.get("FAIL", 0), len(filas)))
    print("  Resumen: %s" % SUMMARY_HTML)
    print("=" * 74)


if __name__ == "__main__":
    main()
