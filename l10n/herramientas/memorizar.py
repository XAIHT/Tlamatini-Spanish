# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Incorpora decisiones de traducción a la memoria de un archivo.

Entrada (JSON):
    {"archivo": "ruta/relativa",
     "decisiones": [{"en": "<crudo inglés>", "es": "<crudo español>"},
                    {"en": "<crudo inglés>", "conservar": "motivo"}]}

Cada `en` debe existir tal cual en el original inglés. El conteo `n` de cada
segmento se calcula aplicando la memoria completa en el mismo orden que usa
`aplicar` (el más largo primero), así que ambos siempre coinciden.
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from memoria import _patron, aplicar_segmentos, cargar_memoria, guardar_memoria  # noqa: E402


def ruta_memoria(memoria_dir: Path, archivo: str) -> Path:
    return memoria_dir / (archivo + ".json")


def recalcular_conteos(original: bytes, segmentos: list[dict]) -> list[str]:
    """Fija `n` simulando la aplicación; devuelve los `en` que no aparecen."""
    ausentes = []
    datos = original
    for i in sorted(range(len(segmentos)), key=lambda k: -len(segmentos[k]["en"])):
        seg = segmentos[i]
        if seg["en"] == seg["es"]:
            continue
        n = len(list(_patron(seg["en"]).finditer(datos)))
        if n == 0:
            ausentes.append(seg["en"])
            continue
        seg["n"] = n
        datos, _ = aplicar_segmentos(datos, [seg])
    return ausentes


def memorizar(memoria_dir: Path, original: bytes, archivo: str, decisiones: list[dict]) -> dict:
    ruta = ruta_memoria(memoria_dir, archivo)
    mem = cargar_memoria(ruta) if ruta.exists() else {"archivo": archivo, "segmentos": [], "conservar": []}
    mem.setdefault("conservar", [])
    por_en = {s["en"]: s for s in mem["segmentos"]}
    conservados = {c["en"]: c for c in mem["conservar"]}
    for d in decisiones:
        en = d["en"]
        if "conservar" in d:
            por_en.pop(en, None)
            conservados[en] = {"en": en, "motivo": d["conservar"]}
        else:
            conservados.pop(en, None)
            por_en[en] = {"en": en, "es": d["es"]}
            for marca in ("maquina", "codigo", "libres", "llm"):
                if d.get(marca):
                    por_en[en][marca] = d[marca]
    mem["segmentos"] = list(por_en.values())
    mem["conservar"] = list(conservados.values())
    ausentes = recalcular_conteos(original, mem["segmentos"])
    if ausentes:
        raise ValueError("No aparecen en el original inglés: " + "; ".join(a[:60] for a in ausentes))
    guardar_memoria(ruta, mem)
    return mem
