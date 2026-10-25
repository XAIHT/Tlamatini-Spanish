# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Núcleo de la memoria de traducción: aplicar pares en→es byte a byte.

Cada par vive en l10n/memoria/<ruta del archivo>.json:
    {"archivo": "...", "segmentos": [{"en": "...", "es": "...", "n": 1}, ...]}

`en` es el texto EXACTO del original inglés (con sus comillas o delimitadores),
`es` su reemplazo, `n` cuántas veces debe aparecer. Los saltos de línea se
guardan como "\n" y coinciden con LF o CRLF en el archivo: el reemplazo usa el
mismo final de línea que encontró, y ningún otro byte del archivo cambia.
"""
import json
import re
from pathlib import Path


class ErrorDeMemoria(Exception):
    pass


def _patron(en: str) -> re.Pattern:
    partes = en.split("\n")
    return re.compile(rb"\r?\n".join(re.escape(p.encode("utf-8")) for p in partes))


def _con_finales(es: str, finales: list[bytes]) -> bytes:
    """Codifica `es` reusando, salto por salto, los finales de línea que tenía el original.

    En un archivo de finales mezclados (LF y CRLF), el k-ésimo salto del reemplazo
    toma el k-ésimo final que se encontró; los saltos de más toman el último.
    """
    partes = es.encode("utf-8").split(b"\n")
    if len(partes) == 1:
        return partes[0]
    salida = [partes[0]]
    for k, parte in enumerate(partes[1:]):
        salida.append(finales[k] if k < len(finales) else (finales[-1] if finales else b"\n"))
        salida.append(parte)
    return b"".join(salida)


def aplicar_segmentos(datos: bytes, segmentos: list[dict]) -> tuple[bytes, list[str]]:
    """Aplica los segmentos (el más largo primero). Devuelve (bytes, problemas)."""
    problemas = []
    orden = sorted(range(len(segmentos)), key=lambda i: -len(segmentos[i]["en"]))
    for i in orden:
        seg = segmentos[i]
        en, es = seg["en"], seg["es"]
        if en == es:
            continue
        rx = _patron(en)
        hallados = list(rx.finditer(datos))
        esperados = seg.get("n", 1)
        if len(hallados) != esperados:
            problemas.append(f"aparece {len(hallados)} veces (se esperaban {esperados}): {en[:90]!r}")
            continue
        piezas = []
        cursor = 0
        for m in hallados:
            finales = re.findall(rb"\r?\n", m.group(0))
            piezas.append(datos[cursor:m.start()])
            piezas.append(_con_finales(es, finales))
            cursor = m.end()
        piezas.append(datos[cursor:])
        datos = b"".join(piezas)
    return datos, problemas


def cargar_memoria(ruta_json: Path) -> dict:
    with open(ruta_json, "r", encoding="utf-8") as fh:
        return json.load(fh)


def guardar_memoria(ruta_json: Path, memoria: dict) -> None:
    ruta_json.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(memoria, ensure_ascii=False, indent=1) + "\n"
    with open(ruta_json, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(texto)
