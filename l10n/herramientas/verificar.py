# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Verificación completa del árbol en español contra su base inglesa.

1. Un archivo SIN memoria debe ser idéntico, byte a byte, a su original.
2. Un archivo CON memoria debe ser exactamente `aplicar(original, memoria)`:
   nadie edita a mano el árbol en español.
3. Entre original y traducción sólo pueden cambiar textos (tokens JS/Python,
   esqueleto HTML, llaves YAML/JSON, forma del Markdown, CSS).
4. Cada par en→es pasa la revisión tipo pofilter (marcadores, etiquetas,
   URLs, nombres intocables, glosario).
5. Acoplamientos: si un texto traducido aparece también en OTRO archivo
   (un matcher que lo reconoce por sus palabras), ese otro archivo tiene que
   haberse traducido igual, o el acoplamiento debe estar revisado.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from base_ingles import OriginalesIngles  # noqa: E402
from extraer import acorn_dir  # noqa: E402
from memoria import aplicar_segmentos, cargar_memoria  # noqa: E402
from revisar import _cuerpo, revisar_par  # noqa: E402
import estructura as vc  # noqa: E402


def _cargar_json(ruta: Path, defecto):
    if ruta.exists():
        with open(ruta, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return defecto


def verificar_estructura(ruta: str, en: bytes, es: bytes, acorn: str, tmp: Path, traducibles,
                         permitidos=frozenset()) -> list[str]:
    suf = Path(ruta).suffix.lower()
    if suf in (".js", ".mjs", ".cjs"):
        return vc.verificar_js_bytes(en, es, acorn, tmp, permitidos)
    if suf == ".py":
        return vc.verificar_py_bytes(en, es, permitidos)
    if suf == ".html":
        return vc.verificar_html_bytes(en, es, acorn, tmp, permitidos)
    if suf in (".yaml", ".yml"):
        return vc.verificar_yaml_bytes(en, es, traducibles)
    if suf == ".json":
        return vc.verificar_json_bytes(en, es, traducibles)
    if suf == ".md":
        return vc.verificar_md_bytes(en, es)
    if suf == ".css":
        return vc.verificar_css_bytes(en, es)
    if suf == ".ps1":
        return vc.verificar_ps1_bytes(en, es)
    return []  # texto libre (.txt, .pmt…): sin estructura que comparar


def _fragmento_acoplable(en_raw: str) -> str | None:
    """La frase más larga del texto (entre marcadores), si tiene al menos 4 palabras."""
    cuerpo = _cuerpo(en_raw)
    partes = re.split(r"\{[^{}]*\}|\$\{[^}]*\}|%\(?\w*\)?[sd]|<[^>]+>|\\n", cuerpo)
    mejor = max((p.strip(" .,:;!?-—\"'") for p in partes), key=len, default="")
    if len(re.findall(r"[A-Za-z']+", mejor)) >= 4 and len(mejor) >= 20:
        return mejor
    return None


_CODIGO = (".py", ".js", ".mjs", ".cjs")
_DATOS = (".json", ".yaml", ".yml", ".pmt", ".fpmt", ".flw")


# tokens previos pegados: "logging.warning(", "self.logger.info(", "print("
_LOG_PY = re.compile(r"(^|[^\w.])(print|(?:self\.)?(?:logger|logging|log|_log|_logger|LOG|LOGGER)\.\w+|"
                     r"warnings\.warn|sys\.stderr\.write|sys\.stdout\.write)\($")
# Archivos que no son la interfaz: sus acoplamientos son deuda de pruebas (aviso), no error.
_PRUEBAS = re.compile(r"(^|/)(test_[^/]*|[^/]*_test|tests)\.py$|(^|/)tests?_?e2e/|^Tests/|^AuxTests/|"
                      r"^scripts/|^\.claude/|^\.gemini/|^\.codex/|\.cjs$")


def _literales_de(ruta: str, datos: bytes, acorn: str) -> str:
    """Las cadenas de un archivo de código (o el texto entero de un archivo de datos), en minúsculas.

    Las cadenas de logs (console.*, print, logging) no cuentan: se quedan en inglés a propósito.
    """
    try:
        if ruta.endswith(_DATOS):
            return datos.decode("utf-8").lower()
        if ruta.endswith(".py"):
            from py_cadenas import cadenas_de
            return "\n".join(s["raw"] for s in cadenas_de(datos)
                             if not s["suelta"] and not _LOG_PY.search("".join(s["prev"][-6:]))).lower()
        from extraer import _node_json
        return "\n".join(s["raw"] for s in _node_json("js_cadenas.cjs", acorn, datos)
                         if not s["ctx"].startswith("call:console.")).lower()
    except Exception:  # noqa: BLE001 - un archivo ilegible no aporta acoplamientos
        return ""


def _corpus_literales(base: dict, acorn: str, leer) -> dict:
    """{ruta: cadenas en minúsculas} de todo el árbol inglés, con caché por commit."""
    cache = Path(tempfile.gettempdir()) / f"l10n_literales_v4_{base['commit'][:12]}.json"
    if cache.exists():
        with open(cache, "r", encoding="utf-8") as fh:
            return json.load(fh)
    corpus = {}
    for ruta in base["archivos"]:
        if not ruta.endswith(_CODIGO + _DATOS) or "/vendor/" in ruta:
            continue
        datos = leer(ruta)
        if datos is None or b"\0" in datos[:4096]:
            continue
        texto = _literales_de(ruta, datos, acorn)
        if texto:
            corpus[ruta] = texto
    with open(cache, "w", encoding="utf-8") as fh:
        json.dump(corpus, fh, ensure_ascii=False)
    return corpus


def recoger_acoplamientos(base, raiz: Path, memoria_dir: Path, productores: set) -> list[str]:
    """Las claves exactas «ruta::frag» de los acoplamientos cruzados cuyo archivo
    productor (el que sigue en inglés) está en `productores`. Mismo recorrido que
    `verificar_todo`, para que las claves coincidan byte a byte con las que revisa."""
    acorn = acorn_dir(raiz, Path(base["ingles"]))
    memorias = {}
    for rj in memoria_dir.rglob("*.json"):
        m = cargar_memoria(rj)
        memorias[m["archivo"]] = m
    claves = set()
    with OriginalesIngles(base["ingles"], base["commit"]) as orig:
        corpus_en = _corpus_literales(base, acorn, orig.leer)
        cache_es = {}
        for ruta_mem, mem in memorias.items():
            for seg in mem["segmentos"]:
                frag = _fragmento_acoplable(seg["en"])
                if not frag or "angela lópez mendoza" in frag.lower():
                    continue
                f = frag.lower()
                for otra in productores:
                    if otra == ruta_mem or otra not in corpus_en or f not in corpus_en[otra]:
                        continue
                    if otra not in cache_es:
                        destino = raiz / otra
                        cache_es[otra] = _literales_de(otra, destino.read_bytes(), acorn) if destino.exists() else ""
                    if f in cache_es[otra]:
                        claves.add(f"{otra}::{frag}")
    return sorted(claves)


def verificar_todo(base, raiz: Path, memoria_dir: Path, rutas, _original, es_propio) -> int:
    l10n = memoria_dir.parent
    config = _cargar_json(l10n / "verificacion.json", {})
    intocables = config.get("intocables", [])
    prohibidas = config.get("prohibidas", {})
    traducibles = frozenset(config.get("llaves_traducibles", []))
    revisados = set(config.get("acoplamientos_revisados", []))
    acorn = acorn_dir(raiz, Path(base["ingles"]))
    tmp = Path(tempfile.mkdtemp(prefix="l10n_verif_"))

    memorias = {}
    for rj in memoria_dir.rglob("*.json"):
        m = cargar_memoria(rj)
        memorias[m["archivo"]] = m

    archivos = base["archivos"]
    if rutas:
        rutas = [r.replace("\\", "/") for r in rutas]
        archivos = [a for a in archivos if any(a == r or a.startswith(r.rstrip("/") + "/") for r in rutas)]

    errores, avisos = 0, 0
    textos_es = {}

    def reportar(ruta, nivel, msg):
        nonlocal errores, avisos
        if nivel == "error":
            errores += 1
            print(f"✗ {ruta}: {msg}")
        else:
            avisos += 1
            print(f"· {ruta}: {msg}")

    with OriginalesIngles(base["ingles"], base["commit"]) as orig:
        originales = {}
        for ruta in archivos:
            if es_propio(ruta):
                continue
            en = orig.leer(ruta)
            originales[ruta] = en
            destino = raiz / ruta
            if not destino.exists():
                reportar(ruta, "error", "falta en el árbol en español")
                continue
            es = destino.read_bytes()
            mem = memorias.get(ruta)
            if mem is None:
                if es != en:
                    reportar(ruta, "error", "difiere del original y no tiene memoria (¿editado a mano?)")
                continue
            esperado, problemas = aplicar_segmentos(en, mem["segmentos"])
            for p in problemas:
                reportar(ruta, "error", f"segmento sin aplicar: {p}")
            if es != esperado:
                reportar(ruta, "error", "el archivo no coincide con aplicar(original, memoria): corre `portar.py aplicar`")
                continue
            permitidos = frozenset(s["en"] for s in mem["segmentos"] if s.get("maquina"))
            # Adaptaciones de código DECLARADAS (marca "codigo"): la prueba de "sólo
            # cambiaron textos" se hace sin ellas, y el archivo final debe compilar.
            codigo = [s for s in mem["segmentos"] if s.get("codigo")]
            comparable = es
            if codigo:
                comparable, _ = aplicar_segmentos(en, [s for s in mem["segmentos"] if not s.get("codigo")])
                for s in codigo:
                    reportar(ruta, "aviso", f"adaptación de código declarada: {s['codigo']}")
                if ruta.endswith(".py"):
                    try:
                        compile(es, ruta, "exec")
                    except SyntaxError as exc:
                        reportar(ruta, "error", f"no compila con la adaptación de código: {exc}")
                elif ruta.endswith((".js", ".mjs", ".cjs")):
                    prueba = tmp / ("_codigo" + Path(ruta).suffix)
                    prueba.write_bytes(es)
                    r = subprocess.run(["node", "--check", str(prueba)], capture_output=True, text=True,
                                       encoding="utf-8", errors="replace")
                    if r.returncode != 0:
                        linea = next((x for x in r.stderr.splitlines() if "Error" in x), r.stderr.strip()[:200])
                        reportar(ruta, "error", f"JS inválido con la adaptación de código: {linea}")
            for p in verificar_estructura(ruta, en, comparable, acorn, tmp, traducibles, permitidos):
                reportar(ruta, "error", p)
            for seg in mem["segmentos"]:
                if seg.get("codigo"):
                    continue
                errs, avs = revisar_par(seg["en"], seg["es"], intocables, prohibidas, seg.get("libres", ()),
                                        llm=bool(seg.get("llm")))
                for e in errs:
                    reportar(ruta, "error", f"{e}: {seg['en'][:70]!r}")
                for a in avs:
                    reportar(ruta, "aviso", f"{a}: {seg['es'][:70]!r}")
            textos_es[ruta] = es

        # textos que el código COMPARA en otro lado (etiqueta ↔ `=== 'Cancel'`, `:contains("Save")`…)
        from acoples import indice, valor_visible
        idx = indice(base, acorn, orig.leer)
        for ruta_mem, mem in memorias.items():
            if rutas and ruta_mem not in textos_es:
                continue
            for seg in mem["segmentos"]:
                if seg["en"] == seg["es"]:
                    continue
                valor = valor_visible(seg["en"])
                if len(re.sub(r"[^A-Za-z]", "", valor)) < 3:  # "or", "OK"… se revisan a mano
                    continue
                for otra, crudo, linea in idx.get(valor, []):
                    if otra == ruta_mem and crudo in seg["en"]:
                        continue
                    mem_otra = memorias.get(otra, {"segmentos": []})
                    traducido = any(crudo in s["en"] and s["es"] != s["en"] for s in mem_otra["segmentos"])
                    if not traducido and f"{otra}::{valor}" not in revisados:
                        reportar(ruta_mem, "aviso" if _PRUEBAS.search(otra) else "error",
                                 f"«{valor}» también se compara en {otra}:{linea} ({crudo[:60]}); "
                                 "tradúcelo ahí a la vez (marcado con !) o conserva éste")

        # acoplamientos entre archivos: una frase traducida que OTRO archivo de código
        # reconoce por sus palabras (dentro de sus cadenas, no de sus comentarios)
        if not rutas:
            corpus_en = _corpus_literales(base, acorn, orig.leer)
            cache_es = {}
            for ruta_mem, mem in memorias.items():
                for seg in mem["segmentos"]:
                    frag = _fragmento_acoplable(seg["en"])
                    if not frag or "angela lópez mendoza" in frag.lower():
                        continue
                    f = frag.lower()
                    for otra, texto in corpus_en.items():
                        if otra == ruta_mem or f not in texto:
                            continue
                        if f"{otra}::{frag}" in revisados:
                            continue
                        if otra not in cache_es:
                            destino = raiz / otra
                            cache_es[otra] = _literales_de(otra, destino.read_bytes(), acorn) if destino.exists() else ""
                        if f in cache_es[otra]:
                            nivel = "aviso" if _PRUEBAS.search(otra) else "error"
                            reportar(otra, nivel, f"acoplamiento sin traducir con {ruta_mem}: «{frag[:60]}»")
    print(f"\nVerificación: {errores} error(es), {avisos} aviso(s), {len(textos_es)} archivos traducidos revisados.")
    return 1 if errores else 0
