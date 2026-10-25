# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Nodos de texto y atributos traducibles de una plantilla HTML de Django, con offsets en bytes.

Las etiquetas Django ({% %}, {{ }}, {# #}) quedan opacas dentro del texto; el
contenido de <script>/<style> se reporta aparte para que lo revise el
extractor de JavaScript. Los comentarios nunca se traducen.
"""
import json
import re
import sys

# Atributos que la especificación WHATWG declara traducibles, más los aria-* y
# data-* con texto de pantalla que usa Tlamatini.
ATRIBUTOS_TRADUCIBLES = ("title", "placeholder", "aria-label", "alt", "aria-description",
                         "data-tooltip", "data-title", "data-placeholder", "data-label",
                         "data-confirm", "data-hint", "label", "value", "aria-roledescription", "lang")

ETIQUETA_RE = re.compile(rb"<(/?)([A-Za-z][\w:-]*)((?:\s+[^\s=>/]+(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?)*)\s*(/?)>", re.S)
ATRIBUTO_RE = re.compile(rb"([^\s=>/]+)(?:\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+))?", re.S)
COMENTARIO_RE = re.compile(rb"<!--.*?-->", re.S)
COMENTARIO_DJANGO_RE = re.compile(rb"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", re.S)


def segmentos(datos: bytes):
    salida = []
    enmascarado = bytearray(datos)
    comentarios = []
    # los comentarios se blanquean para que sus etiquetas no cuenten (los offsets no cambian)
    for rx in (COMENTARIO_RE, COMENTARIO_DJANGO_RE):
        for m in rx.finditer(bytes(enmascarado)):
            comentarios.append((m.start(), m.end()))
            for k in range(m.start(), m.end()):
                if enmascarado[k] not in (10, 13):
                    enmascarado[k] = 32
    comentarios.sort()
    buf = bytes(enmascarado)

    def agregar_texto(a, b):
        # el nodo de texto se corta alrededor de los comentarios
        piezas = []
        cursor = a
        for cs, ce in comentarios:
            if ce <= cursor or cs >= b:
                continue
            if cs > cursor:
                piezas.append((cursor, cs))
            cursor = max(cursor, ce)
        if cursor < b:
            piezas.append((cursor, b))
        for ps, pe in piezas:
            txt = datos[ps:pe]
            if txt.strip():
                salida.append({"kind": "text", "bstart": ps, "bend": pe, "raw": txt.decode("utf-8")})

    pos = 0
    crudo_hasta = None  # dentro de <script>/<style>
    for m in ETIQUETA_RE.finditer(buf):
        if crudo_hasta is not None:
            if m.group(1) == b"/" and m.group(2).lower().decode() == crudo_hasta:
                salida.append({"kind": crudo_hasta, "bstart": pos, "bend": m.start(),
                               "raw": datos[pos:m.start()].decode("utf-8")})
                crudo_hasta = None
                pos = m.end()
            continue
        if m.start() > pos:
            agregar_texto(pos, m.start())
        etiqueta = m.group(2).lower().decode()
        base = m.start(3)
        for a in ATRIBUTO_RE.finditer(m.group(3)):
            nombre = a.group(1).decode().lower()
            if a.group(2) is None:
                continue
            if nombre in ATRIBUTOS_TRADUCIBLES or (nombre == "content" and etiqueta == "meta"):
                vs, ve = base + a.start(2), base + a.end(2)
                salida.append({"kind": "attr", "attr": nombre, "tag": etiqueta, "nstart": base + a.start(1),
                               "bstart": vs, "bend": ve, "raw": datos[vs:ve].decode("utf-8")})
        if etiqueta in ("script", "style") and m.group(1) == b"" and not m.group(4):
            crudo_hasta = etiqueta
        pos = m.end()
    if pos < len(datos):
        agregar_texto(pos, len(datos))
    for s in salida:
        s["line"] = datos.count(b"\n", 0, s["bstart"]) + 1
    return salida


if __name__ == "__main__":
    sys.stdout.write(json.dumps(segmentos(open(sys.argv[1], "rb").read()), ensure_ascii=False))
