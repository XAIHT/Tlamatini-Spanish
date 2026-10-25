# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Genera y verifica Tlamatini-Spanish a partir de Tlamatini (inglés).

El árbol inglés es la ÚNICA fuente del código. Este árbol se reconstruye así:

    python l10n/portar.py copiar   --ingles C:/Development/XAIHT/Tlamatini
    python l10n/portar.py aplicar
    python l10n/portar.py verificar
    python l10n/portar.py pendientes [ruta ...]

`copiar` toma los archivos versionados del commit inglés (por omisión HEAD) y
lo anota en l10n/BASE_INGLES.json. `aplicar` parte SIEMPRE del original inglés
de ese commit y le aplica la memoria de traducción (l10n/memoria/); por eso se
puede correr las veces que sea y da el mismo resultado. `verificar` comprueba
que entre cada original y su versión en español sólo cambiaron textos.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

L10N = Path(__file__).resolve().parent
RAIZ = L10N.parent
HERRAMIENTAS = L10N / "herramientas"
sys.path.insert(0, str(HERRAMIENTAS))

from memoria import aplicar_segmentos, cargar_memoria  # noqa: E402

BASE = L10N / "BASE_INGLES.json"
MEMORIA = L10N / "memoria"
PROPIOS = ("l10n/",)  # rutas que sólo existen en la edición en español


def _git(ingles: Path, *args, binario=False):
    r = subprocess.run(["git", "-C", str(ingles), *args], capture_output=True, check=True)
    return r.stdout if binario else r.stdout.decode("utf-8")


def leer_base() -> dict:
    with open(BASE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def original_ingles(base: dict, ruta: str) -> bytes:
    return _git(Path(base["ingles"]), "show", f"{base['commit']}:{ruta}", binario=True)


def es_propio(ruta: str) -> bool:
    return any(ruta.startswith(p) for p in PROPIOS)


# ───────────────────────── copiar ─────────────────────────

def cmd_copiar(args):
    ingles = Path(args.ingles).resolve()
    commit = _git(ingles, "rev-parse", args.commit).strip()
    sucio = _git(ingles, "status", "--porcelain", "--untracked-files=no").strip()
    if sucio and args.commit == "HEAD":
        print("Aviso: el árbol inglés tiene cambios sin commit; se copia el commit, no el disco.")
    archivos = _git(ingles, "ls-tree", "-r", "--name-only", "-z", commit).split("\0")
    archivos = [a for a in archivos if a]
    anteriores = set()
    if BASE.exists():
        anteriores = set(leer_base().get("archivos", []))
    # cat-file --batch: un solo proceso para todos los blobs
    proc = subprocess.Popen(["git", "-C", str(ingles), "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    escritos = 0
    for ruta in archivos:
        proc.stdin.write(f"{commit}:{ruta}\n".encode("utf-8"))
        proc.stdin.flush()
        cabecera = proc.stdout.readline().split()
        tam = int(cabecera[2])
        datos = proc.stdout.read(tam)
        proc.stdout.read(1)
        destino = RAIZ / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not destino.exists() or destino.read_bytes() != datos:
            destino.write_bytes(datos)
            escritos += 1
    proc.stdin.close()
    proc.wait()

    # Los payloads de terceros vendorizados (marked, xterm, pdfjs…) están GITIGNORADOS
    # —los cubre vendor/frontend/manifest.json, no git— así que `ls-tree` NO los ve. El
    # build SÍ los exige en disco (build_runtime_assets.REQUIRED_STATIC). Se copian desde
    # el disco del árbol inglés, byte a byte (nunca se traducen), o el build truena pidiendo
    # marked.umd.js, xterm.js, etc. Se guardan aparte: no entran a la memoria ni a verificar.
    vendor_rel = "Tlamatini/agent/static/agent/vendor"
    ignorados = _git(ingles, "ls-files", "--others", "--ignored", "--exclude-standard",
                     "-z", "--", vendor_rel).split("\0")
    ignorados = [a for a in ignorados if a]
    vendorizados = 0
    for ruta in ignorados:
        fuente = ingles / ruta
        if not fuente.is_file():
            continue
        datos = fuente.read_bytes()
        destino = RAIZ / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not destino.exists() or destino.read_bytes() != datos:
            destino.write_bytes(datos)
            vendorizados += 1

    protegidos = set(archivos) | set(ignorados)
    borrados = 0
    for ruta in sorted(anteriores - protegidos):
        destino = RAIZ / ruta
        if destino.exists() and not es_propio(ruta):
            destino.unlink()
            borrados += 1
    fecha = _git(ingles, "log", "-1", "--format=%cI", commit).strip()
    titulo = _git(ingles, "log", "-1", "--format=%s", commit).strip()
    with open(BASE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"ingles": str(ingles).replace("\\", "/"), "commit": commit, "fecha_commit": fecha,
                   "titulo_commit": titulo, "copiado": datetime.now().isoformat(timespec="seconds"),
                   "archivos": archivos, "vendorizados_ignorados": ignorados}, fh,
                  ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"Base inglesa {commit[:10]} ({fecha}): {len(archivos)} archivos, "
          f"{escritos} escritos, {vendorizados} vendorizados, {borrados} borrados.")
    print("Ahora corre:  python l10n/portar.py aplicar")


# ───────────────────────── aplicar ─────────────────────────

def memorias():
    for ruta_json in sorted(MEMORIA.rglob("*.json")):
        mem = cargar_memoria(ruta_json)
        yield ruta_json, mem


def cmd_aplicar(args):
    base = leer_base()
    total_ok, total_mal, archivos = 0, 0, 0
    for ruta_json, mem in memorias():
        ruta = mem["archivo"]
        if args.rutas and not any(ruta.startswith(r.replace("\\", "/")) for r in args.rutas):
            continue
        try:
            datos = original_ingles(base, ruta)
        except subprocess.CalledProcessError:
            print(f"✗ {ruta}: ya no existe en la base inglesa; su memoria quedó huérfana")
            total_mal += 1
            continue
        nuevo, problemas = aplicar_segmentos(datos, mem["segmentos"])
        destino = RAIZ / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(nuevo)
        archivos += 1
        aplicados = len(mem["segmentos"]) - len(problemas)
        total_ok += aplicados
        total_mal += len(problemas)
        if problemas:
            print(f"✗ {ruta}: {len(problemas)} segmento(s) sin aplicar")
            for p in problemas:
                print(f"    · {p}")
    print(f"Aplicados {total_ok} segmentos en {archivos} archivos; {total_mal} con problema.")
    return 1 if total_mal else 0


# ───────────────────────── verificar ─────────────────────────

def cmd_verificar(args):
    from verificar import verificar_todo
    base = leer_base()
    return verificar_todo(base, RAIZ, MEMORIA, args.rutas, original_ingles, es_propio)


# ───────────────────────── pendientes ─────────────────────────

def cmd_pendientes(args):
    from pendientes import listar_pendientes
    base = leer_base()
    return listar_pendientes(base, RAIZ, MEMORIA, args.rutas, args.json)


# ───────────────────────── revisar ─────────────────────────

def cmd_revisar(args):
    """Registra como REVISADOS los acoplamientos cuyos archivos productores se dan,
    con un motivo. Para cadenas que son correctas en inglés (texto para el LLM,
    comentarios, logs, build, voz, datos del modelo), no para lo que falta traducir."""
    from verificar import recoger_acoplamientos
    base = leer_base()
    config = {}
    ruta_cfg = L10N / "verificacion.json"
    if ruta_cfg.exists():
        with open(ruta_cfg, "r", encoding="utf-8") as fh:
            config = json.load(fh)
    productores = {p.replace("\\", "/") for p in args.productores}
    claves = recoger_acoplamientos(base, RAIZ, MEMORIA, productores)
    if not claves:
        print("No hay acoplamientos activos para esos archivos productores.")
        return 0
    revisados = config.setdefault("acoplamientos_revisados", [])
    motivos = config.setdefault("acoplamientos_motivos", {})
    nuevos = 0
    for clave in claves:
        if clave not in revisados:
            revisados.append(clave)
            nuevos += 1
        motivos[clave] = args.motivo
    config["acoplamientos_revisados"] = sorted(set(revisados))
    with open(ruta_cfg, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(config, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"Registrados {nuevos} acoplamiento(s) nuevo(s) ({len(claves)} en total) con motivo: {args.motivo}")
    return 0


# ───────────────────────── memorizar ─────────────────────────

def cmd_memorizar(args):
    """Incorpora a la memoria las decisiones de uno o varios archivos JSON."""
    from memorizar import memorizar
    base = leer_base()
    fallas = 0
    for ruta_dec in args.decisiones:
        with open(ruta_dec, "r", encoding="utf-8") as fh:
            contenido = json.load(fh)
        lotes = contenido if isinstance(contenido, list) else [contenido]
        for lote in lotes:
            archivo = lote["archivo"]
            try:
                original = original_ingles(base, archivo)
                mem = memorizar(MEMORIA, original, archivo, lote["decisiones"])
                print(f"✓ {archivo}: {len(mem['segmentos'])} traducidos, {len(mem['conservar'])} conservados")
            except (ValueError, subprocess.CalledProcessError) as exc:
                fallas += 1
                print(f"✗ {archivo}: {exc}")
    return 1 if fallas else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("copiar", help="copia los archivos versionados del commit inglés")
    c.add_argument("--ingles", required=True, help="ruta del árbol inglés (repositorio git)")
    c.add_argument("--commit", default="HEAD")
    for nombre, ayuda in (("aplicar", "aplica la memoria de traducción"),
                          ("verificar", "verifica que sólo cambiaron textos"),
                          ("pendientes", "lista textos que siguen en inglés")):
        s = sub.add_parser(nombre, help=ayuda)
        s.add_argument("rutas", nargs="*")
        if nombre == "pendientes":
            s.add_argument("--json", action="store_true")
    m = sub.add_parser("memorizar", help="agrega decisiones de traducción a la memoria")
    m.add_argument("decisiones", nargs="+", help="archivos JSON con {archivo, decisiones}")
    rv = sub.add_parser("revisar", help="registra acoplamientos correctos-en-inglés como revisados")
    rv.add_argument("--motivo", required=True)
    rv.add_argument("productores", nargs="+", help="archivos productores (el lado que se queda en inglés)")
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    funcion = {"copiar": cmd_copiar, "aplicar": cmd_aplicar, "verificar": cmd_verificar,
               "pendientes": cmd_pendientes, "memorizar": cmd_memorizar, "revisar": cmd_revisar}[args.cmd]
    sys.exit(funcion(args) or 0)


if __name__ == "__main__":
    main()
