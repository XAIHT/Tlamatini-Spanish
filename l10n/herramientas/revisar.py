# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Revisión de cada par en→es, al estilo de pofilter (Translate Toolkit).

Errores (detienen la verificación): marcadores de posición, etiquetas HTML,
URLs, términos que no se traducen (nombres de agents, producto), traducción
vacía, delimitadores distintos y traducciones prohibidas del glosario.
Avisos (se reportan): saltos de línea, signos de apertura ¿ ¡ ausentes.
"""
import re
from collections import Counter

MARCADORES = [
    ("llaves", re.compile(r"(?<!\{)\{[A-Za-z_][\w.]*(?:![rsa])?(?::[^{}]*)?\}(?!\})|(?<!\{)\{\d*\}(?!\})")),
    # (sin la bandera de espacio: "100% conserva" no es un %c)
    ("printf", re.compile(r"%(?:\([\w]+\))?[-+#0]*\d*(?:\.\d+)?[sdifrxXeEgGc%](?![a-záéíóúñ])")),
    ("plantilla JS", re.compile(r"\$\{")),
    ("Django", re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.S)),
]
# (las entidades HTML como &amp; son texto, no marcadores: "&" se traduce "y")
ETIQUETA = re.compile(r"</?([a-zA-Z][\w-]*)\b[^<>]*>")
HTML_REALES = frozenset("""a abbr b blockquote br caption center code col colgroup dd del details dfn div dl dt
em font h1 h2 h3 h4 h5 h6 hr i img ins kbd label li mark ol p pre q s samp small span strike
strong sub summary sup table tbody td tfoot th thead tr tt u ul var""".split())
URL = re.compile(r"https?://[^\s'\"<>)]+")
ESCAPE = re.compile(r"\\[ntr]")


def _cuerpo(raw: str) -> str:
    """El texto sin sus delimitadores (comillas, `>`/`<`, `attr="`)."""
    m = re.match(r"^([rRbBuUfF]*)('''|\"\"\"|'|\"|`)(.*)\2$", raw, re.S)
    if m:
        return m.group(3)
    m = re.match(r"^>(.*)<$", raw, re.S)
    if m:
        return m.group(1)
    m = re.match(r"^[\w:-]+=(\"|')(.*)\1$", raw, re.S)
    if m:
        return m.group(2)
    return raw


def _delimitadores(raw: str) -> tuple:
    m = re.match(r"^([rRbBuUfF]*)('''|\"\"\"|'|\"|`)", raw)
    if m:
        return ("cadena", m.group(1).lower(), m.group(2))
    if raw.startswith(">") and raw.endswith("<"):
        return ("texto",)
    m = re.match(r"^([\w:-]+)=(\"|')", raw)
    if m:
        return ("atributo", m.group(1), m.group(2))
    return ("otro",)


def revisar_par(en: str, es: str, intocables: list[str], prohibidas: dict[str, str],
                libres=(), llm=False) -> tuple[list, list]:
    """`libres`: términos intocables que en ESTE texto no son nombres (p. ej. un "AND" enfático).
    `llm`: el texto es un prompt del Catálogo de prompts; sus {{ }} los llena el LLM (no son
    plantillas Django), así que se traducen por dentro: sólo se exige la MISMA cantidad."""
    errores, avisos = [], []
    if en == es:
        return errores, avisos
    if _delimitadores(en) != _delimitadores(es):
        errores.append("cambiaron los delimitadores (comillas, prefijo o atributo)")
    a, b = _cuerpo(en), _cuerpo(es)
    if a.strip() and not b.strip():
        errores.append("la traducción quedó vacía")
    for nombre, rx in MARCADORES:
        if llm and nombre == "Django":
            if len(rx.findall(a)) != len(rx.findall(b)):
                errores.append("cantidad distinta de marcadores {{ }} / {% %}")
            continue
        ca, cb = Counter(rx.findall(a)), Counter(rx.findall(b))
        if ca != cb:
            faltan = list((ca - cb).elements())
            sobran = list((cb - ca).elements())
            errores.append(f"marcadores {nombre} distintos (faltan {faltan[:4]}, sobran {sobran[:4]})")
    ta = Counter(m.group(1).lower() for m in ETIQUETA.finditer(a))
    tb = Counter(m.group(1).lower() for m in ETIQUETA.finditer(b))
    if llm:
        # en un prompt del catálogo, <veredicto> o <el path del reporte> son espacios que llena
        # el LLM; sólo las etiquetas HTML reales tienen que sobrevivir tal cual
        ta = Counter({k: v for k, v in ta.items() if k in HTML_REALES})
        tb = Counter({k: v for k, v in tb.items() if k in HTML_REALES})
    if ta != tb:
        errores.append(f"etiquetas HTML distintas ({dict(ta)} → {dict(tb)})")
    if Counter(URL.findall(a)) != Counter(URL.findall(b)):
        errores.append("cambiaron las URLs")
    for termino in intocables:
        if termino in libres:
            continue
        rx = re.compile(r"(?<![\w-])" + re.escape(termino) + r"(?![\w-])")
        na = len(rx.findall(a))
        if na and na > len(rx.findall(b)):
            errores.append(f"el término intocable «{termino}» no sobrevivió tal cual")
    # sólo el texto visible: sin etiquetas, marcadores ni URLs
    visible = re.sub(r"<[^>]+>|\$\{[^}]*\}|\{\{.*?\}\}|\{%.*?%\}|\{[^{}]*\}|https?://\S+", " ", b)
    minus = visible.lower()
    for mala, buena in prohibidas.items():
        if re.search(r"(?<![\wáéíóúñ])" + re.escape(mala) + r"(?![\wáéíóúñ])", minus):
            errores.append(f"usa «{mala}»: en Tlamatini se dice «{buena}»")
    if Counter(ESCAPE.findall(a)) != Counter(ESCAPE.findall(b)):
        avisos.append("cambió el número de escapes \\n / \\t / \\r")
    texto_b = re.sub(r"\{[^{}]*\}|<[^>]+>", " ", b)
    for cierre, apertura in (("?", "¿"), ("!", "¡")):
        frases = re.findall(r"[^.!?¿¡\n]*\?" if cierre == "?" else r"[^.!?¿¡\n]*!", texto_b)
        for f in frases:
            if apertura not in texto_b and re.search(r"[a-záéíóúñ]{3,}", f.lower()) and not f.strip().startswith(("http", "/")):
                avisos.append(f"falta «{apertura}» de apertura")
                break
    return errores, avisos
