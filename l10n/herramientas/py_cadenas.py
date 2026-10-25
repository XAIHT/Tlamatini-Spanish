# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Cada literal de cadena de un archivo Python, con sus offsets en bytes y su contexto."""
import io
import json
import sys
import tokenize

_IGNORAR = (tokenize.NL, tokenize.COMMENT, tokenize.ENCODING)
_ESTRUCTURA = (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)


def cadenas_de(datos: bytes):
    toks = [t for t in tokenize.tokenize(io.BytesIO(datos).readline) if t.type not in _IGNORAR]
    inicios = [0]
    for i, b in enumerate(datos):
        if b == 0x0A:
            inicios.append(i + 1)
    bom = 3 if datos.startswith(b"\xef\xbb\xbf") else 0
    texto = datos[bom:].decode("utf-8")
    # tokenize parte los renglones sólo en "\n" (splitlines también partiría en \x0c,  …)
    lineas = [parte + "\n" for parte in texto.split("\n")]

    def offset(fila, col):
        linea = lineas[fila - 1] if fila - 1 < len(lineas) else ""
        extra = bom if fila == 1 else 0
        return inicios[fila - 1] + extra + len(linea[:col].encode("utf-8"))

    salida = []
    previos = []  # tokens significativos anteriores (contexto)
    i = 0
    while i < len(toks):
        t = toks[i]
        fin = i
        if t.type == tokenize.STRING:
            tipo = "str"
        elif t.type == getattr(tokenize, "FSTRING_START", -1):
            tipo = "fstr"
            profundidad = 0
            while fin < len(toks):
                if toks[fin].type == tokenize.FSTRING_START:
                    profundidad += 1
                elif toks[fin].type == tokenize.FSTRING_END:
                    profundidad -= 1
                    if profundidad == 0:
                        break
                fin += 1
        else:
            if t.type not in _ESTRUCTURA:
                previos.append(t)
            i += 1
            continue
        s, e = offset(*t.start), offset(*toks[fin].end)
        antes = toks[i - 1] if i > 0 else None
        despues = toks[fin + 1] if fin + 1 < len(toks) else None
        salida.append({
            "kind": tipo, "line": t.start[0], "bstart": s, "bend": e,
            "raw": datos[s:e].decode("utf-8"),
            "prev": [p.string for p in previos[-4:]],
            # sentencia suelta (docstring o cadena-comentario): antes hay NEWLINE,
            # INDENT, DEDENT o el inicio del archivo, y después termina la sentencia
            "suelta": (antes is None or antes.type in _ESTRUCTURA) and
                      (despues is None or despues.type in (tokenize.NEWLINE, tokenize.ENDMARKER)),
            "sig": despues.string if despues is not None else "",
        })
        previos.append(t)
        i = fin + 1
    return salida


if __name__ == "__main__":
    sys.stdout.write(json.dumps(cadenas_de(open(sys.argv[1], "rb").read()), ensure_ascii=False))
