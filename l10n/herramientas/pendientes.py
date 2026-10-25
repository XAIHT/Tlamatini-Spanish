# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Textos de pantalla que siguen en inglés: ni traducidos ni conservados a propósito.

Un candidato está cubierto si su texto crudo aparece dentro de algún `en` de
la memoria del archivo, o si figura en su lista `conservar`.
"""
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from base_ingles import OriginalesIngles  # noqa: E402
from extraer import acorn_dir, extraer_bytes  # noqa: E402
from memoria import cargar_memoria  # noqa: E402

TIPOS = (".js", ".mjs", ".cjs", ".html", ".py", ".md", ".ps1")
EXCLUIR = re.compile(
    r"(^|/)(test_[^/]*|[^/]*_test)\.py$|(^|/)tests?_?e2e/|^Tests/|^AuxTests/|/vendor/|\.min\.js$|"
    r"/migrations/|^\.claude/|^\.gemini/|^\.codex/|^scripts/|^l10n/|^eslint\.config\.mjs$"
)


def cubiertos(memoria: dict | None) -> tuple[list[str], set[str]]:
    if not memoria:
        return [], set()
    return [s["en"] for s in memoria.get("segmentos", [])], {c["en"] for c in memoria.get("conservar", [])}


def pendientes_de(datos: bytes, ruta: str, memoria: dict | None, acorn: str) -> list[dict]:
    try:
        items = extraer_bytes(datos, Path(ruta).suffix, acorn)
    except Exception as exc:  # noqa: BLE001 - se reporta, no se esconde
        return [{"id": 0, "l": 0, "c": "error", "en": f"no se pudo extraer: {exc}"}]
    traducidos, conservados = cubiertos(memoria)
    out = []
    for it in items:
        en = it["en"]
        if en in conservados or any(en in t for t in traducidos):
            continue
        out.append(it)
    return out


def listar_pendientes(base: dict, raiz: Path, memoria_dir: Path, rutas: list[str], como_json: bool) -> int:
    acorn = acorn_dir(raiz, Path(base["ingles"]))
    archivos = [a for a in base["archivos"] if a.endswith(TIPOS)]
    if rutas:
        rutas = [r.replace("\\", "/") for r in rutas]
        archivos = [a for a in archivos if any(a == r or a.startswith(r.rstrip("/") + "/") for r in rutas)]
    else:
        archivos = [a for a in archivos if not EXCLUIR.search(a)]
    total = 0
    resultado = {}
    with OriginalesIngles(base["ingles"], base["commit"]) as orig:
        for ruta in archivos:
            datos = orig.leer(ruta)
            if datos is None:
                continue
            mem_path = memoria_dir / (ruta + ".json")
            memoria = cargar_memoria(mem_path) if mem_path.exists() else None
            pend = pendientes_de(datos, ruta, memoria, acorn)
            if pend:
                resultado[ruta] = pend
                total += len(pend)
    if como_json:
        print(json.dumps(resultado, ensure_ascii=False, indent=0))
    else:
        for ruta, pend in sorted(resultado.items(), key=lambda kv: -len(kv[1])):
            print(f"{len(pend):5}  {ruta}")
        print(f"Total: {total} textos pendientes en {len(resultado)} archivos.")
    return 0
