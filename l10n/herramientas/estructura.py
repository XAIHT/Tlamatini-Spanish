# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Verificaciones estructurales: entre el original inglés y su versión en español
sólo pueden cambiar los TEXTOS. Todo lo que lee una máquina queda idéntico.

Cada función recibe los bytes de ambos archivos y devuelve una lista de
problemas (vacía = el archivo pasa).
"""
import io
import json
import re
import subprocess
import tokenize
from pathlib import Path

AQUI = Path(__file__).resolve().parent

DJANGO_TAG = re.compile(r"\{%.*?%\}|\{\{.*?\}\}|\{#.*?#\}", re.S)


# ───────────────────────── JavaScript ─────────────────────────

def _tokens_js(ruta: Path, acorn: str) -> list:
    r = subprocess.run(["node", str(AQUI / "js_tokens.cjs"), acorn, str(ruta)],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        lineas = [x for x in r.stderr.splitlines() if "Error" in x]
        raise ValueError(lineas[0].strip() if lineas else "error de sintaxis")
    return json.loads(r.stdout)


def _primera_diferencia(a: list, b: list) -> str:
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return f"token #{i}: inglés {x!r} ≠ español {y!r}"
    return f"distinto número de tokens: inglés {len(a)}, español {len(b)}"


def verificar_js_bytes(en: bytes, es: bytes, acorn: str, tmpdir: Path, permitidos=frozenset()) -> list[str]:
    """`permitidos`: crudos ingleses con traducción ACOPLADA revisada (marca "maquina")."""
    a, b = tmpdir / "_v_en.js", tmpdir / "_v_es.js"
    a.write_bytes(en)
    b.write_bytes(es)
    try:
        ta = _tokens_js(a, acorn)
    except ValueError as exc:
        return [f"el original inglés no se pudo tokenizar ({exc})"]
    try:
        tb = _tokens_js(b, acorn)
    except ValueError as exc:
        return [f"JS inválido tras traducir: {exc}"]
    if ta != tb:
        return ["el código cambió, no sólo los textos: " + _primera_diferencia(ta, tb)]
    return _cadenas_js_en_contexto_maquina(a, b, acorn, permitidos)


def _cadenas_js(ruta: Path, acorn: str) -> list:
    r = subprocess.run(["node", str(AQUI / "js_cadenas.cjs"), acorn, str(ruta)],
                       capture_output=True, text=True, encoding="utf-8")
    return json.loads(r.stdout) if r.returncode == 0 else []


def _cadenas_js_en_contexto_maquina(a: Path, b: Path, acorn: str, permitidos=frozenset()) -> list[str]:
    """Un texto que cambió no puede estar donde lo lee una máquina (salvo acoplamiento revisado)."""
    from extraer import JS_MAQUINA
    ca, cb = _cadenas_js(a, acorn), _cadenas_js(b, acorn)
    if len(ca) != len(cb):
        return [f"distinto número de cadenas: inglés {len(ca)}, español {len(cb)}"]
    out = []
    for x, y in zip(ca, cb):
        if x["raw"] == y["raw"] or any(x["raw"] in p for p in permitidos):
            continue
        if JS_MAQUINA.match(x["ctx"]):
            out.append(f"línea {x['line']}: se tradujo una cadena de canal máquina ({x['ctx']}): {x['raw'][:70]}")
    return out


# ───────────────────────── Python ─────────────────────────

def _tokens_py(datos: bytes) -> list:
    """Tokens con el texto de las cadenas en blanco.

    En una f-string el texto literal puede moverse alrededor de los `{expr}` (el español
    a veces lo pone antes de la variable), así que el texto de nivel 0 no cuenta; las
    expresiones, su orden y su formato (lo que va después de ':' dentro de las llaves) sí.
    """
    out = []
    llaves = []  # profundidad de llaves dentro de cada f-string abierta
    for t in tokenize.tokenize(io.BytesIO(datos).readline):
        if t.type in (tokenize.ENCODING, tokenize.COMMENT, tokenize.NL):
            continue
        if t.type == tokenize.STRING:
            prefijo = re.match(r"[A-Za-z]*", t.string).group(0).lower()
            out.append(("STR", prefijo))
        elif t.type == getattr(tokenize, "FSTRING_START", -99):
            llaves.append(0)
            out.append(("FSTART", re.match(r"[A-Za-z]*", t.string).group(0).lower()))
        elif t.type == getattr(tokenize, "FSTRING_MIDDLE", -99):
            if llaves and llaves[-1] > 0:
                out.append(("FSPEC", t.string))  # formato dentro de {…:formato}
        elif t.type == getattr(tokenize, "FSTRING_END", -99):
            if llaves:
                llaves.pop()
            out.append(("FEND", ""))
        elif t.type in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
            out.append((tokenize.tok_name[t.type], ""))
        else:
            if llaves and t.type == tokenize.OP and t.string in ("{", "}"):
                llaves[-1] += 1 if t.string == "{" else -1
            out.append((tokenize.tok_name[t.type], t.string))
    return out


def verificar_py_bytes(en: bytes, es: bytes, permitidos=frozenset()) -> list[str]:
    try:
        ta = _tokens_py(en)
    except (tokenize.TokenError, SyntaxError) as exc:
        return [f"el original inglés no se pudo tokenizar ({exc})"]
    try:
        tb = _tokens_py(es)
    except (tokenize.TokenError, SyntaxError) as exc:
        return [f"Python inválido tras traducir: {exc}"]
    problemas = []
    if ta != tb:
        problemas.append("el código cambió, no sólo los textos: " + _primera_diferencia(ta, tb))
    try:
        compile(es, "<es>", "exec")
    except SyntaxError as exc:
        problemas.append(f"no compila: {exc}")
    if not problemas:
        problemas += _cadenas_py_en_contexto_maquina(en, es, permitidos)
    return problemas


# Contexto (tokens previos) donde una cadena Python la lee una máquina.
PY_MAQUINA_PREV = re.compile(
    r"(==|!=|\bin|\bnot in|\bis|startswith \(|endswith \(|\.get \(|\.pop \(|\.setdefault \(|"
    # `x [` es subíndice (canal máquina); `= [` / `( [` / `, [` es una lista literal
    r"getattr \(|hasattr \(|setattr \(|environ \[|getenv \(|(?:^|[\w)\]]) \[|re\.\w+ \(|compile \(|"
    r"split \(|replace \(|join \(|encode \(|decode \(|import|from)$"
)


def _cadenas_py_en_contexto_maquina(en: bytes, es: bytes, permitidos=frozenset()) -> list[str]:
    from py_cadenas import cadenas_de
    try:
        ca, cb = cadenas_de(en), cadenas_de(es)
    except (tokenize.TokenError, SyntaxError):
        return []
    if len(ca) != len(cb):
        return [f"distinto número de cadenas: inglés {len(ca)}, español {len(cb)}"]
    out = []
    for x, y in zip(ca, cb):
        if x["raw"] == y["raw"] or any(x["raw"] in p for p in permitidos):
            continue
        previo = " ".join(x["prev"][-2:])
        siguiente_es_llave = False
        fin = x["bend"]
        resto = en[fin:fin + 3].lstrip()
        if resto[:1] == b":" and x["prev"] and x["prev"][-1] in ("{", ","):
            siguiente_es_llave = True
        if PY_MAQUINA_PREV.search(previo) or siguiente_es_llave:
            out.append(f"línea {x['line']}: se tradujo una cadena de canal máquina ({previo!r}): {x['raw'][:70]}")
    return out


# ───────────────────────── HTML / plantillas Django ─────────────────────────

def verificar_html_bytes(en: bytes, es: bytes, acorn: str, tmpdir: Path, permitidos=frozenset()) -> list[str]:
    from html_segmentos import segmentos
    sa, sb = segmentos(en), segmentos(es)
    problemas = []
    if [(s["kind"], s.get("attr"), s.get("tag")) for s in sa] != [(s["kind"], s.get("attr"), s.get("tag")) for s in sb]:
        return ["la estructura de la plantilla cambió (nodos de texto / atributos / scripts distintos)"]

    def esqueleto(datos, segs):
        piezas, cur = [], 0
        for s in segs:
            piezas.append(datos[cur:s["bstart"]])
            piezas.append(f"\x00{s['kind']}\x00".encode())
            cur = s["bend"]
        piezas.append(datos[cur:])
        return b"".join(piezas)

    if esqueleto(en, sa) != esqueleto(es, sb):
        problemas.append("cambió algo fuera de los textos traducibles (etiquetas, atributos de máquina, clases o ids)")
    for x, y in zip(sa, sb):
        if DJANGO_TAG.findall(x["raw"]) != DJANGO_TAG.findall(y["raw"]):
            problemas.append(f"línea {x['line']}: cambiaron las etiquetas Django dentro del texto")
        if x["kind"] == "script" and x["raw"] != y["raw"]:
            for p in verificar_js_bytes(x["raw"].encode(), y["raw"].encode(), acorn, tmpdir, permitidos):
                problemas.append(f"<script> de la línea {x['line']}: {p}")
        if x["kind"] == "style" and x["raw"] != y["raw"]:
            problemas.append(f"<style> de la línea {x['line']} cambió")
    return problemas


# ───────────────────────── YAML / JSON ─────────────────────────

def _comparar_arbol(a, b, ruta="", traducibles=frozenset()) -> list[str]:
    if type(a) is not type(b):
        return [f"{ruta or '/'}: cambió el tipo ({type(a).__name__} → {type(b).__name__})"]
    if isinstance(a, dict):
        if list(a.keys()) != list(b.keys()):
            return [f"{ruta or '/'}: cambiaron las llaves"]
        out = []
        for k in a:
            out += _comparar_arbol(a[k], b[k], f"{ruta}/{k}", traducibles)
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{ruta}: cambió el largo de la lista"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += _comparar_arbol(x, y, f"{ruta}[{i}]", traducibles)
        return out
    if a != b:
        llave = ruta.rsplit("/", 1)[-1].split("[")[0]
        if not (isinstance(a, str) and llave in traducibles):
            return [f"{ruta}: cambió un valor que no es texto traducible"]
    return []


def verificar_yaml_bytes(en: bytes, es: bytes, traducibles=frozenset()) -> list[str]:
    import yaml
    try:
        da = list(yaml.safe_load_all(en.decode("utf-8")))
    except yaml.YAMLError as exc:
        return [f"el original inglés no es YAML válido ({str(exc).splitlines()[0]})"]
    try:
        db = list(yaml.safe_load_all(es.decode("utf-8")))
    except yaml.YAMLError as exc:
        return [f"YAML inválido tras traducir: {str(exc).splitlines()[0]}"]
    return _comparar_arbol(da, db, "", traducibles)


def verificar_json_bytes(en: bytes, es: bytes, traducibles=frozenset()) -> list[str]:
    try:
        da = json.loads(en.decode("utf-8-sig"))
    except ValueError as exc:
        return [f"el original inglés no es JSON válido ({exc})"]
    try:
        db = json.loads(es.decode("utf-8-sig"))
    except ValueError as exc:
        return [f"JSON inválido tras traducir: {exc}"]
    return _comparar_arbol(da, db, "", traducibles)


# ───────────────────────── Markdown ─────────────────────────

CERCA = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.S | re.M)
COMENTARIO_HTML = re.compile(r"<!--.*?-->", re.S)
DESTINO = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODIGO_EN_LINEA = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")


def _forma_md(texto: str) -> dict:
    sin_cercas = CERCA.sub("", texto)
    lineas = sin_cercas.split("\n")
    return {
        "cercas": CERCA.findall(texto) and [m.group(0) for m in CERCA.finditer(texto)],
        "comentarios": COMENTARIO_HTML.findall(texto),
        "titulos": [len(m.group(1)) for m in re.finditer(r"^(#{1,6}) ", sin_cercas, re.M)],
        "tablas": [l.count("|") for l in lineas if l.lstrip().startswith("|")],
        "destinos": DESTINO.findall(sin_cercas),
        "codigo": sorted(CODIGO_EN_LINEA.findall(sin_cercas)),
    }


def verificar_md_bytes(en: bytes, es: bytes) -> list[str]:
    fa, fb = _forma_md(en.decode("utf-8")), _forma_md(es.decode("utf-8"))
    frases = {"cercas": "cambiaron los bloques de código",
              "comentarios": "cambiaron los comentarios HTML (incluido el banner de autora)",
              "titulos": "cambiaron los niveles de los títulos",
              "tablas": "cambió la forma de las tablas",
              "destinos": "cambiaron los destinos de los enlaces",
              "codigo": "cambiaron los fragmentos de `código` en línea"}
    return [frases[k] for k in fa if fa[k] != fb[k]]


# ───────────────────────── PowerShell ─────────────────────────

def verificar_ps1_bytes(en: bytes, es: bytes) -> list[str]:
    """Fuera de las cadenas, el script debe ser idéntico (comentarios incluidos)."""
    from extraer import ps1_cadenas

    def esqueleto(datos: bytes) -> str:
        texto = datos.decode("utf-8-sig")
        piezas, cursor = [], 0
        for ini, fin, crudo in ps1_cadenas(texto):
            piezas.append(texto[cursor:ini])
            piezas.append(crudo[0] + "…" + crudo[-1])
            cursor = fin
        piezas.append(texto[cursor:])
        return "".join(piezas)

    if en.startswith(b"\xef\xbb\xbf") != es.startswith(b"\xef\xbb\xbf"):
        return ["cambió el BOM del script"]
    problemas = [] if esqueleto(en) == esqueleto(es) else ["cambió el script fuera de sus cadenas"]
    # Windows PowerShell 5.1 lee como ANSI un .ps1 sin BOM: un acento se ve como basura y
    # los bytes de Ó/Ñ (0x93/0x91 en cp1252) son COMILLAS para PowerShell y rompen el script.
    if not es.startswith(b"\xef\xbb\xbf"):
        originales = {c for _, _, c in ps1_cadenas(en.decode("utf-8-sig"))}
        for _, _, crudo in ps1_cadenas(es.decode("utf-8-sig")):
            if crudo not in originales and not crudo.isascii():
                problemas.append(f"cadena con acentos en un .ps1 sin BOM (usa español sin acentos): {crudo[:60]}")
    return problemas


# ───────────────────────── CSS ─────────────────────────

CSS_CADENA = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'")


def verificar_css_bytes(en: bytes, es: bytes) -> list[str]:
    a = CSS_CADENA.sub('""', en.decode("utf-8"))
    b = CSS_CADENA.sub('""', es.decode("utf-8"))
    return [] if a == b else ["cambió el CSS fuera de las cadenas `content:`"]
