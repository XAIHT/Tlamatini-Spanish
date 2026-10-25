# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Extrae los textos candidatos a traducción de un archivo, con su contexto.

Produce una lista de trabajo con un renglón por literal:
    {"id": n, "l": línea, "c": contexto, "en": texto crudo exacto}

El texto crudo incluye sus delimitadores (comillas en JS/Python, `>`/`<` en
los nodos de texto HTML, `nombre="…"` en los atributos), así que reemplazarlo
nunca alcanza a un identificador vecino.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import tokenize
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from html_segmentos import segmentos as html_segmentos  # noqa: E402
from py_cadenas import cadenas_de  # noqa: E402

PALABRA = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]{2,}")
DJANGO_TAG = re.compile(r"\{[%{#].*?[%}#]\}", re.S)
HTML_TAG = re.compile(r"<[^>]+>")

# Contextos JS que son canal máquina: nunca texto de pantalla.
JS_MAQUINA = re.compile(
    r"^(call:(console|logger|log)\.|call:.*\.(getElementById|querySelector|querySelectorAll|closest|matches|"
    r"addEventListener|removeEventListener|getAttribute|removeAttribute|hasAttribute|toggleAttribute|"
    r"createElement|createElementNS|getItem|setItem|removeItem|postMessage|dispatchEvent|"
    r"startsWith|endsWith|includes|indexOf|lastIndexOf|split|replace|replaceAll|match|matchAll|search|test|"
    r"join|padStart|padEnd|getPropertyValue|setProperty|removeProperty|toLocaleString|toLocaleDateString|"
    r"toLocaleTimeString|has|get|delete|on|off|one|trigger|addClass|removeClass|toggleClass|hasClass|is|find|"
    r"filter|css|send)(:|$)|"
    r"call:(fetch|require|import|RegExp|Symbol|CustomEvent|Event|\$|jQuery|parseInt|parseFloat|Number|"
    r"encodeURIComponent|decodeURIComponent|getComputedStyle|setTimeout|setInterval|WebSocket|URL|"
    r"Worker|BroadcastChannel)(:|$)|"
    r"call:.*\.setAttribute:arg0$|call:.*\.attr:arg0$|"
    r"call:.*classList\.|call:.*\.dataset|bin:(===|!==|==|!=|in|instanceof)|case|propkey(?!:buttons)|import|member|"
    r"assign:.*\.(className|id|type|name|href|src|rel|method|action|accept|autocomplete|role|"
    r"style(\.\w+)?|cssText|display|cursor|dataset\.\w+|lang|dir|htmlFor|target|download)$|"
    r"prop:(method|credentials|mode|cache|headers|Content-Type|X-CSRFToken|type|dialogClass|className|"
    r"class|id|name|key|kind|action|state|level|severity|role|icon|cssClass|selector|event|"
    r"url|href|src|path|endpoint|position|my|at|of|collision|width|height|minWidth|minHeight|maxWidth|"
    r"maxHeight|display|cursor|overflow|zIndex|color|background|border|font|easing|effect|"
    r"dataType|contentType|accept|encoding|lang|locale|channel|tool|agent|command|cmd|op|code)$)"
)
JS_UI = re.compile(
    r"(textContent|innerText|innerHTML|outerHTML|placeholder|title|label|alt|ariaLabel|"
    r"[Aa]lert|[Cc]onfirm|[Pp]rompt|[Tt]oast|[Nn]otif|[Mm]essage|[Ee]rror|[Ww]arn|[Tt]ext|[Hh]int|"
    r"[Tt]ooltip|[Cc]aption|[Hh]eading|[Bb]anner|[Ss]tatus|setAttribute|[Dd]escription|[Ss]ummary)"
)


CSS_VALOR = re.compile(
    r"^((rgba?|hsla?|var|calc|url|linear-gradient|radial-gradient|translate[XYZ]?|scale|rotate)\(.*\)|"
    r"#[0-9a-fA-F]{3,8}|-?\d+(\.\d+)?(px|em|rem|vh|vw|%|ms|s|deg)?( -?\d+(\.\d+)?(px|em|rem|vh|vw|%)?)*|"
    r"(solid|dashed|dotted) .*|.*\b(px|rem)\b.*\b(solid|dashed)\b.*)$"
)


def _tiene_texto(valor: str) -> bool:
    if not valor:
        return False
    limpio = DJANGO_TAG.sub(" ", HTML_TAG.sub(" ", valor))
    return bool(PALABRA.search(limpio))


def _es_token_unico(valor: str) -> bool:
    """identificador, selector, ruta, URL, clase CSS, MIME… (sin espacios)."""
    v = valor.strip()
    if not v or " " in v:
        return False
    if re.fullmatch(r"[A-Z][a-z]+[.:!?…]*", v):  # "Cancel", "Save:", "Done!"
        return False
    if re.fullmatch(r"[A-Z][a-z]+(-[A-Z][a-z]+)*[.:!?…]*", v):
        return False
    return True


def acorn_dir(*bases: Path) -> str:
    for base in bases:
        nm = base / "node_modules"
        pnpm = nm / ".pnpm"
        if pnpm.is_dir():
            cands = sorted(pnpm.glob("acorn@*/node_modules/acorn"))
            if cands:
                return str(cands[-1])
        if (nm / "acorn").is_dir():
            return str(nm / "acorn")
    raise SystemExit("No encuentro acorn: instala las dependencias de node o indica el árbol inglés.")


def _node_json(script: str, acorn: str, datos: bytes):
    fd, tmp = tempfile.mkstemp(suffix=".js")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(datos)
        r = subprocess.run(["node", str(AQUI / script), acorn, tmp],
                           capture_output=True, text=True, encoding="utf-8")
    finally:
        os.unlink(tmp)
    if r.returncode != 0:
        lineas = [x for x in r.stderr.splitlines() if "Error" in x]
        raise ValueError(lineas[0].strip() if lineas else r.stderr.strip()[:200])
    return json.loads(r.stdout)


def js_items(datos: bytes, acorn: str, base_bytes: int = 0, base_linea: int = 0):
    items = []
    for s in _node_json("js_cadenas.cjs", acorn, datos):
        valor = s["value"] if s["kind"] == "lit" else " ".join(q or "" for q in s["quasis"])
        pegado = s["value"] if s["kind"] == "lit" else "".join(q or "" for q in s["quasis"])
        if not _tiene_texto(valor):
            continue
        if JS_MAQUINA.match(s["ctx"]) or s["ctx"] == "ExpressionStatement":
            continue
        if CSS_VALOR.match(pegado.strip()):
            continue
        if _es_token_unico(HTML_TAG.sub(" ", pegado)) and not JS_UI.search(s["ctx"]):
            continue
        items.append({"l": s["line"] + base_linea, "c": s["ctx"], "en": s["raw"],
                      "b": [s["bstart"] + base_bytes, s["bend"] + base_bytes]})
    return items


PY_LOG = re.compile(r"^(logger|logging|log|_log|LOG|_LOG|_logger|LOGGER|warnings)$")


def py_items(datos: bytes):
    cadenas = cadenas_de(datos)
    items = []
    for s in cadenas:
        raw = s["raw"]
        prev = s["prev"]
        # docstrings y cadenas sueltas: documentación del código, no pantalla
        if s["suelta"]:
            continue
        # llave de diccionario o subíndice: canal máquina
        if s["sig"] == ":" and prev and prev[-1] in ("{", ","):
            continue
        # subíndice x["llave"] (no una lista de un elemento ["texto"])
        if (len(prev) >= 2 and prev[-1] == "[" and s["sig"] == "]"
                and (re.match(r"^[A-Za-z_]\w*$", prev[-2]) or prev[-2] in (")", "]"))
                and prev[-2] not in ("return", "in", "and", "or", "not", "yield", "else", "if", "lambda")):
            continue
        if raw[:2].lower() in ("b'", 'b"') or raw[:3].lower() in ("rb'", 'rb"', "br'", 'br"'):
            continue
        cuerpo = re.sub(r"^[rRbBuUfF]*('''|\"\"\"|'|\")", "", raw)
        cuerpo = re.sub(r"('''|\"\"\"|'|\")$", "", cuerpo)
        if not _tiene_texto(re.sub(r"\{[^{}]*\}", " ", cuerpo)):
            continue
        if _es_token_unico(cuerpo):
            continue
        # logging: los logs se quedan en inglés
        if len(prev) >= 4 and prev[-1] == "(" and prev[-3] == "." and PY_LOG.match(prev[-4]):
            continue
        items.append({"l": s["line"], "c": " ".join(prev[-4:]), "en": raw, "b": [s["bstart"], s["bend"]]})
    return items


def html_items(datos: bytes, acorn: str):
    items = []
    for s in html_segmentos(datos):
        if s["kind"] == "script":
            if s["raw"].strip():
                try:
                    items.extend(js_items(s["raw"].encode("utf-8"), acorn, base_bytes=s["bstart"],
                                          base_linea=s["line"] - 1))
                except ValueError as exc:
                    items.append({"l": s["line"], "c": "error", "en": f"<script ilegible: {exc}>"})
            continue
        if s["kind"] == "style":
            continue
        raw = s["raw"]
        if "<!DOCTYPE" in raw.upper():
            if not _tiene_texto(re.sub(r"(?i)<!DOCTYPE[^>]*>", "", raw)):
                continue
        if not _tiene_texto(raw):
            continue
        if s["kind"] == "attr":
            if s["attr"] == "content":
                continue
            if s["attr"] == "value":
                # sólo el value de un <input type="submit|button|reset"> se ve en pantalla;
                # el de <option>, <button> y los demás inputs es un dato que se envía
                inicio_tag = datos.rfind(b"<", 0, s["bstart"])
                tag_txt = datos[inicio_tag:s["bstart"]].lower()
                if s.get("tag") != "input" or not re.search(rb"type\s*=\s*[\"']?(submit|button|reset)", tag_txt):
                    continue
            ini = s.get("nstart", datos.rfind(s["attr"].encode(), 0, s["bstart"]))
            items.append({"l": s["line"], "c": f"attr:{s.get('tag')}.{s['attr']}",
                          "en": datos[ini:s["bend"]].decode("utf-8"), "b": [ini, s["bend"]]})
        else:
            ini, fin = s["bstart"] - 1, s["bend"] + 1  # incluye `>` y `<`
            if datos[ini:ini + 1] != b">":
                ini += 1
            if datos[fin - 1:fin] != b"<":
                fin -= 1
            items.append({"l": s["line"], "c": "texto", "en": datos[ini:fin].decode("utf-8"), "b": [ini, fin]})
    return items


MD_CERCA = re.compile(r"^\s*(```|~~~)")
MD_LISTA = re.compile(r"^\s*([-*+]|\d+[.)])\s+")


def md_items(datos: bytes):
    """Bloques de Markdown: títulos, párrafos, elementos de lista y renglones de tabla.

    Los bloques de código, los comentarios HTML (banner de autora incluido) y los
    separadores de tabla nunca se ofrecen. Un párrafo de varias líneas es UN
    segmento (se traduce entero; el Markdown lo vuelve a fluir igual).
    """
    texto = datos.decode("utf-8")
    lineas = texto.split("\n")
    items = []
    en_cerca = False
    en_comentario = False
    bloque, inicio = [], 0

    def cerrar_bloque():
        nonlocal bloque
        if bloque:
            crudo = "\n".join(l.rstrip("\r") for l in bloque)
            if _tiene_texto(crudo):
                items.append({"l": inicio + 1, "c": "md", "en": crudo})
        bloque = []

    for n, linea in enumerate(lineas):
        limpia = linea.rstrip("\r")
        if en_comentario:
            if "-->" in limpia:
                en_comentario = False
            continue
        if MD_CERCA.match(limpia):
            cerrar_bloque()
            en_cerca = not en_cerca
            continue
        if en_cerca:
            continue
        if limpia.lstrip().startswith("<!--"):
            cerrar_bloque()
            if "-->" not in limpia:
                en_comentario = True
            continue
        if not limpia.strip():
            cerrar_bloque()
            continue
        es_tabla = limpia.lstrip().startswith("|")
        es_titulo = limpia.lstrip().startswith("#")
        es_lista = bool(MD_LISTA.match(limpia))
        if es_tabla or es_titulo or es_lista:
            cerrar_bloque()
            if es_tabla and re.fullmatch(r"\s*\|[\s:|-]+\|?\s*", limpia):
                continue  # separador |---|---|
            bloque, inicio = [linea], n
            if es_tabla or es_titulo:
                cerrar_bloque()
            continue
        if bloque and (bloque[0].lstrip().startswith("|") or bloque[0].lstrip().startswith("#")):
            cerrar_bloque()
        if not bloque:
            inicio = n
        bloque.append(linea)
    cerrar_bloque()
    return items


# PowerShell: comentarios (# … y <# … #>), here-strings (@"…"@, @'…'@) y cadenas.
PS1_TOKEN = re.compile(
    r"<#.*?#>|#[^\n]*|@\"\r?\n.*?\r?\n\"@|@'\r?\n.*?\r?\n'@|\"(?:[^\"`]|`.|\"\")*\"|'(?:[^']|'')*'",
    re.S)


def ps1_cadenas(texto: str):
    """(inicio, fin, crudo) de cada cadena de PowerShell, saltándose los comentarios."""
    for m in PS1_TOKEN.finditer(texto):
        crudo = m.group(0)
        if crudo.startswith("#") or crudo.startswith("<#"):
            continue
        yield m.start(), m.end(), crudo


def ps1_items(datos: bytes):
    texto = datos.decode("utf-8-sig")
    items = []
    for ini, fin, crudo in ps1_cadenas(texto):
        cuerpo = crudo[1:-1] if not crudo.startswith("@") else crudo[2:-2]
        if not _tiene_texto(re.sub(r"\$\(.*?\)|\$\{?[\w:]+\}?", " ", cuerpo)):
            continue
        if _es_token_unico(cuerpo):
            continue
        linea = texto.count("\n", 0, ini) + 1
        inicio_linea = texto.rfind("\n", 0, ini) + 1
        ctx = texto[inicio_linea:ini].strip()[-40:]
        items.append({"l": linea, "c": ctx, "en": crudo})
    return items


def extraer_bytes(datos: bytes, sufijo: str, acorn: str | None):
    sufijo = sufijo.lower()
    if sufijo in (".js", ".mjs", ".cjs"):
        items = js_items(datos, acorn)
    elif sufijo == ".py":
        items = py_items(datos)
    elif sufijo == ".html":
        items = html_items(datos, acorn)
    elif sufijo == ".md":
        items = md_items(datos)
    elif sufijo == ".ps1":
        items = ps1_items(datos)
    else:
        raise ValueError(f"tipo no soportado: {sufijo}")
    for i, it in enumerate(items, 1):
        it["id"] = i
    return items


if __name__ == "__main__":
    ruta = Path(sys.argv[1])
    ingles = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(r"C:\Development\XAIHT\Tlamatini")
    acorn = acorn_dir(AQUI.parents[1], ingles)
    res = extraer_bytes(ruta.read_bytes(), ruta.suffix, acorn)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=0))
