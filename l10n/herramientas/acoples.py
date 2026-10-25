# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Índice de los textos que el código COMPARA, para traducir productor y matcher juntos.

Un texto de pantalla corto ('Cancel', 'Save') también puede ser un valor que el
código compara en otro lado: `boton.textContent === 'Cancel'`, un selector
`button:contains("Save")`, un `includes(...)`, un `== "..."` en Python. Si la
etiqueta se traduce y la comparación no, la función deja de funcionar sin
avisar. Este índice junta, en todo el árbol inglés, cada valor que aparece en
un contexto de comparación, para que `verificar` exija que ambos lados se
traduzcan a la vez (o que el acoplamiento quede revisado).
"""
import ast
import json
import re
import subprocess
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent

JS_COMPARA = re.compile(
    r"^(bin:(===|!==|==|!=)|case|call:.*\.(includes|indexOf|lastIndexOf|startsWith|endsWith|"
    r"test|match|search|has|get)(:|$))"
)
CONTAINS = re.compile(r""":contains\((["'])(.*?)\1\)""")
PY_COMPARA = re.compile(r"(==|!=|\bin|\bnot in|startswith \(|endswith \(|\.get \()$")


def _normal(valor: str) -> str:
    # con mayúsculas: 'Close' (etiqueta) no es 'close' (valor de máquina)
    return " ".join(valor.split())


def _js_ocurrencias(datos: bytes, acorn: str) -> list[tuple]:
    from extraer import _node_json
    salida = []
    try:
        cadenas = _node_json("js_cadenas.cjs", acorn, datos)
    except ValueError:
        return salida
    for s in cadenas:
        if s["kind"] != "lit":
            continue
        valor = s["value"]
        if JS_COMPARA.match(s["ctx"]):
            salida.append((_normal(valor), s["raw"], s["line"]))
        for m in CONTAINS.finditer(valor):
            salida.append((_normal(m.group(2)), s["raw"], s["line"]))
    return salida


def _py_ocurrencias(datos: bytes) -> list[tuple]:
    from py_cadenas import cadenas_de
    salida = []
    try:
        cadenas = cadenas_de(datos)
    except Exception:  # noqa: BLE001 - un archivo que no tokeniza no aporta acoples
        return salida
    for s in cadenas:
        if s["kind"] != "str":
            continue
        previo = " ".join(s["prev"][-2:])
        if not PY_COMPARA.search(previo):
            continue
        try:
            valor = ast.literal_eval(s["raw"])
        except (ValueError, SyntaxError):
            continue
        if isinstance(valor, str):
            salida.append((_normal(valor), s["raw"], s["line"]))
    return salida


def indice(base: dict, acorn: str, leer) -> dict:
    """{valor_normalizado: [(archivo, crudo, línea), ...]} de todo el árbol inglés (con caché)."""
    cache = Path(tempfile.gettempdir()) / f"l10n_acoples_v2_{base['commit'][:12]}.json"
    if cache.exists():
        with open(cache, "r", encoding="utf-8") as fh:
            return json.load(fh)
    resultado: dict[str, list] = {}
    for ruta in base["archivos"]:
        suf = Path(ruta).suffix.lower()
        if suf not in (".js", ".mjs", ".cjs", ".py") or "/vendor/" in ruta:
            continue
        datos = leer(ruta)
        if datos is None:
            continue
        ocurrencias = _js_ocurrencias(datos, acorn) if suf != ".py" else _py_ocurrencias(datos)
        for valor, crudo, linea in ocurrencias:
            if valor:
                resultado.setdefault(valor, []).append((ruta, crudo, linea))
    with open(cache, "w", encoding="utf-8") as fh:
        json.dump(resultado, fh, ensure_ascii=False)
    return resultado


def valor_visible(en: str) -> str:
    """El texto visible de un `en` de la memoria (sin comillas, `>`/`<` ni nombre de atributo)."""
    from revisar import _cuerpo
    return _normal(_cuerpo(en))
