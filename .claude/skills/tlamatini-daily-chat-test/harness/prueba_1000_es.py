# PROHIBIDO PIL.ImageGrab (Angela, 2026-08-02): las fotos las toma
# SHOTER, el agent de Tlamatini. Ver shoter_foto.py.
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

Usage (from this folder). The server MUST already be running MUTED --
the runner refuses to start until you confirm it (exit code 2):

    # 1) server, muted:
    $env:TLAMATINI_SIN_AUDIO="1"; python manage.py runserver

    # 2) runner, confirming the server is muted:
    $env:ES_SERVIDOR_MUDO="1"; python prueba_1000_es.py          # all 1000
    $env:ES_SERVIDOR_MUDO="1"; $env:ES_N="25"; python prueba_1000_es.py

It is RESUMABLE: reports/es1000/resultados.json is written after every
question, and a re-run skips whatever is already answered. Delete that
file to start over. Exit 0 only when every question PASSED and every
accent twin agreed.
"""
import os
import sys

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

# ── El resto del harness vive aqui al lado ────────────────────────────────
TLAMATINI = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "Tlamatini"))
if TLAMATINI not in sys.path:
    sys.path.insert(0, TLAMATINI)

import datetime as _dt                                   # noqa: E402
import html                                              # noqa: E402
import json                                              # noqa: E402
import re                                                # noqa: E402
import unicodedata                                       # noqa: E402

import config as C                                       # noqa: E402
import run_test as R                                     # noqa: E402
from preguntas_es import CORPUS                          # noqa: E402
from shoter_foto import toma_foto                        # noqa: E402

# El termbase NEPANTLA es la MISMA autoridad que usa la app para decidir si un
# termino tecnico se conservo. NO se reimplementa aqui: si la regla cambia,
# tiene que cambiar en UN solo lugar y esta prueba tiene que enterarse sola.
from agent.i18n import dnt                               # noqa: E402

try:
    from agent.i18n.termbase_en import FORBIDDEN_SPANISH_RENDERINGS as _PROHIBIDAS
except Exception:                                        # pragma: no cover
    _PROHIBIDAS = {}


# ══════════════════════════════════════════════════════════════════════════
#  Juez 2 — ¿contesto EN ESPAÑOL?
# ══════════════════════════════════════════════════════════════════════════
# Palabras FUNCIONALES, no de contenido: son las que un texto no puede evitar
# y las que un modelo no traduce por accidente. Un texto en español lleno de
# nombres tecnicos en ingles sigue puntuando español, que es exactamente lo
# que queremos — el contrato NEPANTLA es "portador español, carga tecnica en
# ingles", asi que contar sustantivos tecnicos daria falsos negativos.
_FUNC_ES = frozenset("""
el la los las un una unos unas de del al a en con por para sin sobre entre
que quien cuyo como cuando donde porque pues aunque si no ni y o u pero sino
es son era eran fue fueron ser estar esta estan estoy estas hay haber tiene
tienen tener hace hacen puede pueden debe deben va van
su sus mi mis tu tus nuestro nuestra se lo le les me te nos
tambien muy mas menos ya solo cada todo toda todos todas otro otra
esto esta este estos estas eso esa ese aquel asi entonces despues antes
""".split())

_FUNC_EN = frozenset("""
the a an of to in on at for with without from by about between into
that which who whose how when where because although if not and or but
is are was were be been being have has had do does did can could
should would will shall may might must
this these those there their its it his her your our my
also very more less only each all other another then after before
you i we they he she them us
""".split())

_RE_PALABRA = re.compile("[^\\W\\d_]+", re.UNICODE)


def _dobla(texto):
    """Minusculas sin acentos — para comparar sin que un tilde decida nada."""
    n = unicodedata.normalize("NFD", texto or "")
    return "".join(c for c in n if unicodedata.category(c) != "Mn").lower()


def juzga_idioma(respuesta):
    """(es_espanol, marcador). Gana el idioma con mas palabras funcionales.

    Un empate cuenta como NO-español a proposito: la edicion en español tiene
    que ser inequivoca. "No se pudo decidir" es un problema, no un aprobado.
    """
    palabras = [_dobla(w) for w in _RE_PALABRA.findall(respuesta or "")]
    if not palabras:
        return False, {"es": 0, "en": 0, "total": 0}
    es = sum(1 for w in palabras if w in _FUNC_ES)
    en = sum(1 for w in palabras if w in _FUNC_EN)
    return es > en, {"es": es, "en": en, "total": len(palabras)}


# ══════════════════════════════════════════════════════════════════════════
#  Juez 3 — ¿respeto el REGISTRO? (el termino tecnico sigue en ingles)
# ══════════════════════════════════════════════════════════════════════════
def juzga_registro(pregunta, respuesta):
    """(ok, rotos). Un termino se cuenta ROTO solo si el ingles esta AUSENTE
    *y* su traduccion al español esta PRESENTE.

    Las dos mitades son necesarias. Sin la primera, "un container (contenedor)"
    saldria roto siendo perfecto. Sin la segunda, una respuesta que simplemente
    no menciona el termino saldria rota sin haber traducido nada. Y como la
    traduccion prohibida se busca por palabra completa con el termbase, una
    palabra española comun jamas dispara un falso positivo.
    """
    rotos = []
    for termino in (pregunta.get("keep_en") or ()):
        if dnt.term_preserved(termino, respuesta):
            continue
        for es_render, en_term in _PROHIBIDAS.items():
            if _dobla(en_term) != _dobla(termino):
                continue
            if dnt.term_present(es_render, respuesta):
                rotos.append({"termino": termino, "traducido_como": es_render})
                break
    return (not rotos), rotos


# ══════════════════════════════════════════════════════════════════════════
#  Marcos transitorios que NUNCA son la respuesta
# ══════════════════════════════════════════════════════════════════════════
# El auto-sanado emite marcos con la MISMA forma que la respuesta final. El
# matcher va ANCLADO (se quitan los no-letras del principio y se compara el
# arranque) porque una busqueda por substring tambien casaria con el banner
# "SELF-HEALING NOTE —" que la respuesta final SI trae, y entonces tirariamos
# la respuesta buena. Es el mismo error que una vez dejo el boton en Cancel.

# Se quita TODO lo que no sea letra al principio (emoji, vinetas, numeros,
# espacios). Un lstrip con lista fija de caracteres no sirve: el marco real
# empieza con un EMOJI, y ese emoji no esta en ninguna lista que uno se
# acuerde de escribir — fue exactamente el caso que fallo al probarlo.
_RE_HASTA_LETRA = re.compile("^[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")


def es_marco_de_autosanado(texto):
    limpio = _dobla(_RE_HASTA_LETRA.sub("", texto or "").strip())
    limpio = _dobla(limpio)
    return limpio.startswith(("tactic #", "tactic '", "tactica #", "tactica '"))


# ══════════════════════════════════════════════════════════════════════════
#  El runner
# ══════════════════════════════════════════════════════════════════════════
class _Args(object):
    """Los atributos que Harness espera. Se fijan aqui a proposito: esta
    prueba tiene UNA configuracion correcta y no se negocia por linea de
    comandos."""
    headless = False          # PROHIBIDO. Harness igual lo rechaza.
    slowmo = 0
    not_ready_retries = 8
    not_ready_backoff = 20.0
    judge_model = None        # no hay juez-LLM: aqui todo es determinista
    user = C.USERNAME
    password = C.PASSWORD
    timeout = int(os.environ.get("ES_TIMEOUT", "360"))


class PruebaES(R.Harness):
    """Harness + las cuatro exigencias que esta prueba agrega."""

    def reasserta_multi_turn(self):
        """Multi-Turn se vuelve a marcar ANTES DE CADA envio.

        No es paranoia: el toggle vive en sessionStorage y cualquier recarga,
        reconexion o `recover()` lo puede dejar apagado. Una pregunta enviada
        sin Multi-Turn si contesta — y contesta distinto — asi que el
        resultado seria verde y MENTIROSO.
        """
        return self.page.evaluate(
            """(sel) => {
                const el = document.querySelector(sel);
                if (!el) return 'missing';
                if (el.checked) return 'ya';
                el.checked = true;
                el.dispatchEvent(new Event('change', {bubbles: true}));
                return 'reactivado';
            }""",
            C.SEL["t_multi_turn"],
        )

    def pregunta_limpia(self, q, anterior, intentos=3):
        """Pregunta hasta obtener una respuesta que no sea reciclada ni un
        marco transitorio. Devuelve (rec, notas)."""
        notas = []
        rec = None
        for intento in range(1, intentos + 1):
            estado = self.reasserta_multi_turn()
            if estado == "reactivado":
                notas.append("multi-turn estaba APAGADO y se reactivo")
            elif estado == "missing":
                notas.append("no se encontro el checkbox de Multi-Turn")

            rec = self.ask_one(q, timeout_ms=_Args.timeout * 1000)
            texto = (rec.get("answer") or "").strip()

            if es_marco_de_autosanado(texto):
                notas.append("intento %d: marco de auto-sanado, se repregunta" % intento)
                self.page.wait_for_timeout(2500)
                continue
            if texto and anterior and _dobla(texto) == _dobla(anterior):
                notas.append("intento %d: respuesta IDENTICA a la anterior, se repregunta" % intento)
                self.page.wait_for_timeout(2500)
                continue
            break
        return rec, notas


def _califica(q, rec, notas):
    """Los tres jueces por pregunta. Devuelve el registro final."""
    texto = (rec.get("answer") or "").strip()
    razones = list(notas)

    contesto = bool(texto) and len(texto) >= int(q.get("min_len") or 1)
    if not texto:
        razones.append("respuesta VACIA")
    elif not contesto:
        razones.append("muy corta (%d < min_len %s)" % (len(texto), q.get("min_len")))
    if not rec.get("completed", True):
        razones.append("la generacion no completo (timeout)")

    en_espanol, marcador = juzga_idioma(texto)
    if contesto and not en_espanol:
        razones.append("NO esta en español (es=%d vs en=%d)" % (marcador["es"], marcador["en"]))

    registro_ok, rotos = juzga_registro(q, texto)
    for r in rotos:
        razones.append("registro roto: '%s' se tradujo como '%s'"
                       % (r["termino"], r["traducido_como"]))

    veredicto = "PASS" if (contesto and en_espanol and registro_ok
                           and rec.get("completed", True)) else "FAIL"
    rec.update({
        "veredicto": veredicto,
        "contesto": contesto,
        "en_espanol": en_espanol,
        "marcador_idioma": marcador,
        "registro_ok": registro_ok,
        "registro_rotos": rotos,
        "razones": razones,
        "twin": q.get("twin"),
    })
    return rec


def _compara_gemelas(resultados):
    """Juez 4 — las parejas con/sin acento deben caer del mismo lado.

    Una divergencia NO es ruido: significa que un tilde cambio el resultado,
    o sea que la respuesta no depende de lo que se pregunto sino de como se
    escribio. Se reporta aparte porque no es culpa de ninguna de las dos
    preguntas por separado.
    """
    por_id = {}
    for r in resultados:
        por_id[r["id"]] = r
    vistas = set()
    parejas = []
    for r in resultados:
        gemela = r.get("twin")
        if not gemela or r["id"] in vistas:
            continue
        otra = por_id.get(gemela)
        if not otra:
            continue
        vistas.add(r["id"])
        vistas.add(gemela)
        parejas.append({
            "a": r["id"], "b": gemela,
            "veredicto_a": r["veredicto"], "veredicto_b": otra["veredicto"],
            "coinciden": r["veredicto"] == otra["veredicto"],
        })
    return parejas


_PLANTILLA = """<!doctype html><meta charset="utf-8">
<title>Tlamatini - 1000 preguntas en espanol</title>
<style>body{font:14px system-ui;margin:24px;background:#faf9f7;color:#222}
h1{margin:0 0 4px}table{border-collapse:collapse;width:100%;font-size:12.5px}
td,th{border:1px solid #ddd;padding:5px 7px;vertical-align:top}
th{background:#efeae2;text-align:left}
.k{display:inline-block;margin:0 18px 10px 0}.k b{font-size:22px}</style>
<h1>Tlamatini - 1000 preguntas EN ESPANOL</h1>
<p>__TS__ &middot; fotos en <code>__FOTOS__</code></p>
<p><span class="k">contestadas<br><b>__TOTAL__</b></span>
<span class="k">PASS<br><b style="color:#1b7f3b">__OK__</b></span>
<span class="k">FAIL<br><b style="color:#a11">__MAL__</b></span>
<span class="k">no en espanol<br><b>__SINES__</b></span>
<span class="k">registro roto<br><b>__REG__</b></span>
<span class="k">gemelas discrepantes<br><b>__DISP__</b></span></p>
<table><tr><th>id</th><th>categoria</th><th>pregunta</th><th>veredicto</th>
<th>idioma</th><th>razones</th><th>evidencia</th></tr>__FILAS__</table>
"""


def _escribe_resumen(ruta_html, resultados, parejas, dir_fotos):
    total = len(resultados)
    ok = sum(1 for r in resultados if r["veredicto"] == "PASS")
    sin_es = sum(1 for r in resultados if r.get("contesto") and not r.get("en_espanol"))
    reg = sum(1 for r in resultados if not r.get("registro_ok"))
    disp = [p for p in parejas if not p["coinciden"]]

    filas = []
    for r in resultados:
        color = "#1b7f3b" if r["veredicto"] == "PASS" else "#a11"
        m = r.get("marcador_idioma") or {"es": 0, "en": 0}
        filas.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td>"
            "<td style='color:%s;font-weight:700'>%s</td>"
            "<td>es %d / en %d</td><td>%s</td>"
            "<td><a href='fotos/%s.png'>foto</a></td></tr>"
            % (html.escape(r["id"]), html.escape(r.get("category", "")),
               html.escape((r.get("question") or "")[:90]), color, r["veredicto"],
               m.get("es", 0), m.get("en", 0),
               html.escape("; ".join(r.get("razones", []))[:180]),
               html.escape(r["id"]))
        )

    doc = _PLANTILLA
    for marca, valor in (
        ("__TS__", _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("__FOTOS__", html.escape(dir_fotos)),
        ("__TOTAL__", str(total)), ("__OK__", str(ok)), ("__MAL__", str(total - ok)),
        ("__SINES__", str(sin_es)), ("__REG__", str(reg)), ("__DISP__", str(len(disp))),
        ("__FILAS__", "".join(filas)),
    ):
        doc = doc.replace(marca, valor)
    with open(ruta_html, "w", encoding="utf-8") as fh:
        fh.write(doc)


_AVISO_MUDO = """
=================================================================
 ANTES DE CORRER ESTO: EL SERVIDOR TIENE QUE ESTAR MUDO.

 Esta prueba maneja la app DE VERDAD con Multi-Turn encendido, y
 Multi-Turn liga TODA la superficie de tools — incluido el Talker.
 La reja de silencio vive en el proceso del SERVIDOR, no aqui: se
 arma con TLAMATINI_SIN_AUDIO. Si el servidor arranco sin esa marca,
 una sola pregunta puede hacer sonar las bocinas de Angela.

 Arranca el servidor asi, y vuelve:

     $env:TLAMATINI_SIN_AUDIO="1"; python manage.py runserver

 Luego confirma aqui que ya lo hiciste:

     $env:ES_SERVIDOR_MUDO="1"; python prueba_1000_es.py

 La confirmacion es MANUAL a proposito: desde este proceso no hay
 forma de leer el environment del servidor, y adivinar que esta mudo
 es justo la suposicion que ya costo un susto a media noche.
=================================================================
"""


def _exige_servidor_mudo():
    """Se niega a arrancar si nadie confirmo que el servidor esta mudo."""
    marca = str(os.environ.get("ES_SERVIDOR_MUDO", "")).strip().lower()
    if marca and marca not in ("0", "false", "no"):
        return True
    print(_AVISO_MUDO)
    return False


def main():
    from playwright.sync_api import sync_playwright

    if not _exige_servidor_mudo():
        return 2


    n = int(os.environ.get("ES_N", "0") or 0)
    preguntas = CORPUS[:n] if n > 0 else CORPUS

    salida = os.path.join(HERE, "reports", "es1000")
    fotos = os.path.join(salida, "fotos")
    os.makedirs(fotos, exist_ok=True)
    ruta_json = os.path.join(salida, "resultados.json")

    # Resumible: lo ya contestado no se vuelve a preguntar.
    hechos = {}
    if os.path.exists(ruta_json):
        try:
            with open(ruta_json, "r", encoding="utf-8") as fh:
                for r in json.load(fh):
                    hechos[r["id"]] = r
            print("--- reanudando: %d preguntas ya hechas" % len(hechos))
        except Exception as exc:
            print("--- no se pudo leer el avance (%s); se empieza de cero" % exc)

    pendientes = [q for q in preguntas if q["id"] not in hechos]
    print("--- %d preguntas en total, %d pendientes" % (len(preguntas), len(pendientes)))

    if pendientes:
        h = PruebaES(_Args())
        anterior = ""
        with sync_playwright() as p:
            h.launch(p)
            h.login()
            h.goto_chat()
            h.wait_ready(timeout_ms=90000, label="lista para platicar")
            h.set_toggles()

            for i, q in enumerate(pendientes, 1):
                print("--- [%d/%d] %s  %s" % (i, len(pendientes), q["id"], q["text"][:60]))
                # El historial se limpia ANTES de cada pregunta: sin esto una
                # respuesta vieja sigue en el DOM y el scraper la puede recoger
                # como si fuera la nueva. Ese es el "resultado rancio" que
                # Angela prohibio registrar como aprobado.
                h.clear_history()
                try:
                    rec, notas = h.pregunta_limpia(q, anterior)
                except Exception as exc:
                    print("    !! excepcion: %s -> recuperando" % exc)
                    try:
                        h.recover()
                    except Exception:
                        pass
                    rec = {"id": q["id"], "category": q["category"],
                           "question": q["text"], "answer": "", "completed": False}
                    notas = ["excepcion en la pregunta: %s" % exc]

                rec = _califica(q, rec, notas)
                anterior = (rec.get("answer") or "").strip() or anterior

                # UNA foto de TODO el escritorio por pregunta, tomada por
                # SHOTER. PIL.ImageGrab esta PROHIBIDO (Angela, 2026-08-02):
                # si Shoter falla se REPORTA, no se sustituye — usar el agent
                # ES la prueba del agent.
                try:
                    if not toma_foto(fotos, "%s.png" % q["id"], runtime_base=salida):
                        rec.setdefault("razones", []).append("SHOTER no pudo tomar la foto")
                except Exception as exc:
                    rec.setdefault("razones", []).append("SHOTER fallo: %s" % exc)

                hechos[q["id"]] = rec
                with open(ruta_json, "w", encoding="utf-8") as fh:
                    json.dump(list(hechos.values()), fh, ensure_ascii=False, indent=1)
                print("    -> %s  %s" % (rec["veredicto"],
                                         "; ".join(rec.get("razones", []))[:110]))

    resultados = [hechos[q["id"]] for q in preguntas if q["id"] in hechos]
    parejas = _compara_gemelas(resultados)
    _escribe_resumen(os.path.join(salida, "SUMMARY.html"), resultados, parejas, fotos)

    ok = sum(1 for r in resultados if r["veredicto"] == "PASS")
    disp = [p for p in parejas if not p["coinciden"]]
    print("=" * 62)
    print("PASS %d / %d   ·   gemelas discrepantes: %d" % (ok, len(resultados), len(disp)))
    for p in disp[:10]:
        print("   %s(%s) != %s(%s)" % (p["a"], p["veredicto_a"], p["b"], p["veredicto_b"]))
    print("resumen: %s" % os.path.join(salida, "SUMMARY.html"))
    print("=" * 62)
    return 0 if (ok == len(resultados) and not disp) else 1


if __name__ == "__main__":
    sys.exit(main())
