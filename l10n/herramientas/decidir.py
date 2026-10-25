# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Convierte respuestas por id (texto visible en español) en decisiones de memoria.

Entrada:
  * la lista de trabajo de un archivo: `portar.py pendientes <ruta> --json`
    (o el JSON {"archivo", "items"} que guarda una herramienta de apoyo);
  * un archivo de respuestas, un renglón por id, separado por tabulador:

        12<TAB>Guardar archivo
        13<TAB>=término técnico         (conservar en inglés, con su motivo)
        14<TAB>!Estoy trabajando        (traducción acoplada: un matcher que el código
                                         compara contra un mensaje traducido igual)

    Un salto de línea real dentro del texto se escribe ⏎.
    Sólo se escribe el texto VISIBLE: las comillas, los `>`/`<` de un nodo
    HTML, el `nombre="…"` de un atributo y los espacios de alrededor se
    reconstruyen solos. Dentro del texto van, tal cual, los marcadores del
    original (`{name}`, `${count}`, `%s`, `{{ var }}`, `\\n`, etiquetas HTML).
    La comilla que delimita la cadena se escapa sola.

Salida: el JSON de decisiones que consume `portar.py memorizar`.
"""
import json
import re
import sys
from pathlib import Path

CADENA = re.compile(r"^([rRbBuUfF]*)('''|\"\"\"|'|\"|`)(.*)\2$", re.S)
ATRIBUTO = re.compile(r"^([\w:-]+=)([\"'])(.*)\2$", re.S)


def _escapar(texto: str, comilla: str) -> str:
    if len(comilla) == 3 or comilla not in texto:
        return texto
    salida = []
    i = 0
    while i < len(texto):
        c = texto[i]
        if c == "\\" and i + 1 < len(texto):
            salida.append(texto[i:i + 2])
            i += 2
            continue
        salida.append("\\" + c if c == comilla else c)
        i += 1
    return "".join(salida)


def _orillas(texto: str) -> tuple[str, str]:
    sin_izq = texto.lstrip(" \t")
    izq = texto[:len(texto) - len(sin_izq)]
    der = sin_izq[len(sin_izq.rstrip(" \t")):] if sin_izq else ""
    return izq, der


def reconstruir(en: str, visible: str) -> str:
    """Arma el crudo en español con los mismos delimitadores y espacios que el inglés."""
    m = CADENA.match(en)
    if m:
        prefijo, comilla, interior = m.groups()
        # los espacios de las orillas son del original (piezas que se concatenan):
        # se conservan siempre, aunque el archivo de respuestas los haya perdido
        izq, der = _orillas(interior)
        return prefijo + comilla + izq + _escapar(visible.strip(" \t"), comilla) + der + comilla
    m = ATRIBUTO.match(en)
    if m:
        nombre, comilla, interior = m.groups()
        izq, der = _orillas(interior)
        visible = visible.strip(" \t")
        if comilla in visible:
            visible = visible.replace(comilla, "&quot;" if comilla == '"' else "&#39;")
        return nombre + comilla + izq + visible + der + comilla
    abre = ">" if en.startswith(">") else ""
    cierra = "<" if en.endswith("<") and len(en) > len(abre) else ""
    centro = en[len(abre):len(en) - len(cierra)]
    izq = centro[:len(centro) - len(centro.lstrip())]
    der = centro[len(centro.rstrip()):]
    # los espacios de alrededor ya vienen del original: no duplicarlos
    if izq:
        visible = visible.lstrip()
    if der:
        visible = visible.rstrip()
    return abre + izq + visible + der + cierra


def leer_respuestas(ruta: Path) -> dict[int, str]:
    respuestas = {}
    for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        if "\t" not in linea:
            raise ValueError(f"{ruta.name}:{n}: falta el tabulador entre id y texto")
        ident, texto = linea.split("\t", 1)
        # ⏎ marca un salto de línea real dentro del texto (nodos HTML de varias líneas)
        respuestas[int(ident)] = texto.replace("⏎", "\n")
    return respuestas


def decisiones(trabajo: dict, respuestas: dict[int, str]) -> dict:
    por_id = {it["id"]: it for it in trabajo["items"]}
    faltan = sorted(set(por_id) - set(respuestas))
    sobran = sorted(set(respuestas) - set(por_id))
    if sobran:
        raise ValueError(f"ids que no existen en la lista de trabajo: {sobran[:10]}")
    salida = []
    for ident, texto in sorted(respuestas.items()):
        en = por_id[ident]["en"]
        if texto.startswith("="):
            salida.append({"en": en, "conservar": texto[1:].strip() or "se queda en inglés"})
        elif texto.startswith("!"):
            # traducción ACOPLADA: la cadena la compara el código (un matcher que
            # reconoce un mensaje por sus palabras) y se traduce a la vez que su productor
            salida.append({"en": en, "es": reconstruir(en, texto[1:]), "maquina": "acoplada con su productor"})
        else:
            salida.append({"en": en, "es": reconstruir(en, texto)})
    return {"archivo": trabajo["archivo"], "decisiones": salida, "sin_decidir": faltan}


def main():
    trabajo_path, respuestas_path, salida_path = map(Path, sys.argv[1:4])
    with open(trabajo_path, "r", encoding="utf-8") as fh:
        trabajo = json.load(fh)
    if "items" not in trabajo:  # salida directa de `pendientes --json`: {ruta: [items]}
        (ruta, items), = trabajo.items()
        trabajo = {"archivo": ruta, "items": items}
    resultado = decisiones(trabajo, leer_respuestas(respuestas_path))
    with open(salida_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(resultado, fh, ensure_ascii=False, indent=1)
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"{trabajo['archivo']}: {len(resultado['decisiones'])} decisiones; "
          f"sin decidir: {len(resultado['sin_decidir'])} {resultado['sin_decidir'][:20]}")


if __name__ == "__main__":
    main()
