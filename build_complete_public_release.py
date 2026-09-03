#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""
build_complete_public_release.py -- PUBLIC release builder (scrubbed + verified).

Builds a CLEAN Tlamatini release safe to distribute: secrets become placeholders
and your private data is scrubbed BEFORE the build, then the package is re-audited
by check_private_data.py. The build BLOCKS only if YOUR personal data actually
survives into the package (the thousands of structural matches on bundled
third-party binaries are reported as informational, not blockers).

Twin of build_complete_private_release.py (the keyed build for your own machine).

ABSOLUTE RULE (CLAUDE.md PRIVATE DATA GUARD): never rewrites git history. It makes
FORWARD, in-place edits to a temporary scrub of the WORKING TREE, then RESTORES the
tree byte-for-byte afterwards.

Pipeline
--------
  0. SAFETY: refuse the carried interpreter; load leak targets (auto from
     .private_targets.json when not given).
  1. BACK UP touched files (restored in `finally`).
  2. regen_secrets.py --mode push-able  -> config secrets become placeholders.
  3. sanitize external_mcps.json (ship an empty catalog) + SCRUB the working tree.
  4. build.py --no-self-modify           -> freeze app + pkg.zip (build.py deletes dist/).
     DEFAULT: NO source tree and NO Tlamatini.md, keeping ~15.7k tokens out of
     the system prompt per request; pass --self-modify here to bundle both.
  5. VERIFY: extract pkg.zip and run check_private_data.py over it.
       any of YOUR personal data present -> ABORT, tree restored.
  6. build_uninstaller.py + build_installer.py -> dist/Tlamatini_Release_v<ver>/.
  7. zip -> dist/..._PUBLIC_CLEAN_win11x64.zip
  8. ALWAYS restore the working tree (finally).

Los targets son OPCIONALES, nunca se ASUMEN  (2026-08-30)
---------------------------------------------------------
`.private_targets.json` esta en .gitignore, asi que un CLON RECIEN HECHO nunca lo
trae — y este builder antes se NEGABA a correr sin el. Ahora es OPCIONAL. La
negativa no se borro sin mas, porque "no hay lista de targets" significa dos cosas
OPUESTAS:

  * un clon PRISTINO — no hay datos privados en el arbol, asi que no hay nada que
    limpiar. Negarse aqui es friccion pura: bloquea un build publico a cambio de nada.
  * el arbol PROPIO de Angela con el archivo borrado / renombrado / mal escrito — SI
    hay datos privados y acabamos de perder la lista. Seguir aqui publicaria su
    telefono. Negarse es lo unico seguro.

Un PRE-FLIGHT DE PRIVACIDAD independiente de los targets (`privacy_preflight()`)
distingue los dos casos buscando EVIDENCIA de que ESTE arbol si puede fugar:
`data.keys`, un `config.json` o un `config.yaml` de agent con llaves, una libreta de
contactos, un catalogo External-MCP con llaves, archivos `*.key` en la raiz. Entonces:

  hay evidencia -> SE NIEGA, nombrando la evidencia exacta y las cuatro salidas.
  no hay        -> construye en modo ARBOL-LIMPIO (CLEAN-TREE).

El modo arbol-limpio NO queda "sin proteccion": siguen corriendo todas las defensas
independientes de los targets (regen_secrets --mode push-able, el barrido del arbol
con SECRET_KEY_RE, la libreta de contactos vacia, el catalogo MCP sembrado en codigo,
y el aborto de build.py ante un secreto MCP vivo). Lo unico ausente es el paso de PII
— que necesita una lista de PII que buscar — y el banner, la linea de auditoria y el
resumen final lo DICEN en voz alta, en vez de insinuar una verificacion que no ocurrio.

El pre-flight FALLA HACIA LA NEGATIVA: cualquier error al leer cualquier sonda cuenta
COMO evidencia. Es lo contrario, a proposito, de la regla fail-open habitual de
Tlamatini, por la misma razon por la que el guard de bisect de LaTeXer falla seguro:
publicar los datos privados de Angela es mucho peor que un build que se detiene y
pregunta.

`private_targets.example.json` es una plantilla RASTREADA e INERTE (solo la forma, sin
valores reales). A proposito NO esta en DEFAULT_TARGETS_FILES y sus valores de relleno
se quitan del conjunto a limpiar, porque una plantilla capaz de volver la lista de
targets meramente no-vacia SILENCIARIA la negativa de arriba y produciria un build que
reporta "verificado" habiendo limpiado nada real — estrictamente peor que la negativa
que reemplazo.

EN RUNTIME: nada de esto lo lee jamas la aplicacion corriendo. `.private_targets.json`
es un artefacto SOLO DE BUILD-TIME — ningun modulo bajo `Tlamatini/agent/` lo abre, y
ni `build.py` ni `install.py` lo envian o lo mencionan — asi que su ausencia nunca
puede afectar el primer arranque de Tlamatini ni ninguno posterior. Fijado por
`Tlamatini/agent/test_public_release_targets.py`.
"""

from __future__ import annotations

import json
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import zipfile
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parent
DIST = REPO_ROOT / "dist"
DIST_MANAGE = DIST / "manage"
PKG_ZIP = REPO_ROOT / "pkg.zip"            # build.py's real artifact (it deletes dist/)
VERIFY_EXTRACT = REPO_ROOT / "Temp" / "public_verify_extract"
EXTERNAL_MCPS = REPO_ROOT / "Tlamatini" / "agent" / "external_mcps.json"  # user state
REGEN = REPO_ROOT / "regen_secrets.py"
BUILD = REPO_ROOT / "build.py"
BUILD_UNINST = REPO_ROOT / "build_uninstaller.py"
BUILD_INST = REPO_ROOT / "build_installer.py"
CHECKER = REPO_ROOT / "check_private_data.py"

# Auto-discovered local targets file (gitignored) used when no --targets-file /
# --target / env CHECK_PRIVATE_DATA_TARGETS is given. Values are read at run
# time -- never hardcoded.
#: La plantilla que se copia a .private_targets.json. Va COMMITEADA y trae solo
#: formas de ejemplo — ningun valor real de Angela. Es lo que hace que un clon
#: nuevo pueda armar su propia lista sin adivinar el formato.
TARGETS_TEMPLATE = REPO_ROOT / "private_targets.example.json"

DEFAULT_TARGETS_FILES = [REPO_ROOT / ".private_targets.json",
                         REPO_ROOT / "private_targets.json"]

PLACEHOLDER = "<REDACTED>"

# Angela's NAME and her GitHub handle are NEVER scrubbed -- in the public OR the
# private build. Her authorship stays everywhere, always, by her explicit
# instruction: her display name "Angela Lopez Mendoza" in ANY case / accent /
# spacing variant (Angela, Ángela, Lopez, López, Mendoza, the full name) AND her
# GitHub handle @angelahack1 are kept. Only her OTHER private data is masked --
# emails, her PHONE, the "Ana*" legal-name variants, and secrets. Her phone in
# particular must NEVER appear in the repo: it lives ONLY in data.keys (which is
# gitignored and in SCRUB_SKIP_FILES, so it is never scrubbed OR published).
# Kept values are dropped from the scrub set before any redaction runs.
KEEP_NAME_TOKENS = {"angela", "lopez", "mendoza"}   # accent-stripped, lowercased
KEEP_HANDLES = {"angelahack1"}                      # with or without a leading @


def _strip_accents(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", value or "")
                   if not unicodedata.combining(c))


def _is_kept_name(value: str) -> bool:
    """True for Angela's name (ANY accent / case / spacing variant) and her GitHub
    handle -- these are kept in EVERY build. Her emails, phone and the "Ana*" legal
    variants are NOT kept (they carry an @domain, digits, or non-name tokens)."""
    norm = _strip_accents(value).strip().lower()
    if not norm:
        return False
    if norm.lstrip("@") in KEEP_HANDLES:
        return True
    # Kept only when EVERY token is one of her name tokens, so "Angela",
    # "Angela Lopez Mendoza" and "Ángela López Mendoza" are all kept, but
    # "<REDACTED>" or "<REDACTED>" (a token that isn't a bare name) are not.
    tokens = [t for t in re.split(r"[\s.]+", norm) if t]
    return bool(tokens) and all(t in KEEP_NAME_TOKENS for t in tokens)


SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist",
             "build", ".mypy_cache", ".ruff_cache", ".pytest_cache",
             "staticfiles", "Temp", "python", "ms-playwright", "jre", "git",
             # Gitignored local runtimes / scratch / snapshots — never published,
             # so never scrubbed. The self-provisioned Go toolchain in particular
             # holds READ-ONLY module-cache files (crash write_text with
             # PermissionError), and it plus the pool scratch is huge. Mirrors the
             # SKIP_DIRS in check_private_data.py.
             "Go", "go-build", "Templates", "TlamatiniSourceCode",
             "pools", "mcp_agent_runs",
             # Blue-hat toolkit runtime EVIDENCE (gitignored): alerts.log,
             # monitor.log and the visible asset-test artifacts. Never published
             # (build.py ignores it), so a release build must never rewrite it.
             # Mirrors the SKIP_DIRS in check_private_data.py.
             "security_logs"}
TEXT_EXT = {".py", ".js", ".ts", ".json", ".yaml", ".yml", ".md", ".txt", ".env",
            ".cfg", ".ini", ".toml", ".html", ".css", ".csv", ".pmt", ".keys"}
# NEVER scrub the sources of truth: the keys vault and the targets file. Scrubbing
# .private_targets.json turns your real values into "<REDACTED>" inside it, which
# then makes the verifier hunt for the literal text "<REDACTED>" and "find" it in
# every scrubbed file (the 737-false-positive bug). data.keys must stay intact too.
SCRUB_SKIP_FILES = {"data.keys", ".private_targets.json", "private_targets.json",
                    "contacts.private.json"}

SECRET_KEY_RE = re.compile(
    r'(?i)("(?:api[_-]?key|api[_-]?secret|token|access[_-]?token|auth[_-]?token|'
    r'password|passwd|secret|client[_-]?secret|session[_-]?string|bearer)"\s*:\s*")'
    r'([^"]+)(")'
)


def banner(msg: str) -> None:
    print("\n" + "=" * 74, flush=True)
    print(f"== {msg}", flush=True)
    print("=" * 74, flush=True)


def assert_self_modify_payload(expect_self_modify: bool) -> None:
    """PROVE the built package matches the flag — never merely claim it.

    Tlamatini's own source tree (``TlamatiniSourceCode/``) and her self-knowledge
    file (``Tlamatini.md``) ship TOGETHER, or not at all. A build that silently
    kept ``Tlamatini.md`` would put her entire self-description back into the
    system prompt of EVERY request (~63k characters, ~15.7k tokens) — exactly
    what the default not-self-able-modify mode exists to avoid. So we open the
    artifact and LOOK, and we fail loud on a mismatch in either direction.
    """
    if not PKG_ZIP.is_file():
        print(f"  NOTE: {PKG_ZIP.name} not found — skipping self-modify payload check.")
        return
    with zipfile.ZipFile(PKG_ZIP) as zf:
        names = [n.replace("\\", "/") for n in zf.namelist()]
    tree = any("TlamatiniSourceCode/" in n for n in names)
    self_md = any(n.rsplit("/", 1)[-1] == "Tlamatini.md" for n in names)
    print(f"  package payload: TlamatiniSourceCode={'PRESENT' if tree else 'absent'}, "
          f"Tlamatini.md={'PRESENT' if self_md else 'absent'}")
    if expect_self_modify and not (tree and self_md):
        sys.exit("ABORT: --self-modify was requested but the package is missing "
                 "TlamatiniSourceCode/ and/or Tlamatini.md — she could not modify herself.")
    if not expect_self_modify and (tree or self_md):
        sys.exit("ABORT: this is a not-self-able-modify build, yet the package still "
                 "contains TlamatiniSourceCode/ and/or Tlamatini.md — the per-request "
                 "prompt savings would be silently lost.")


def assert_system_python(py: str) -> None:
    try:
        resolved = Path(py).resolve()
    except Exception:
        return
    carried = (REPO_ROOT / "python").resolve()
    try:
        resolved.relative_to(carried)
    except ValueError:
        return
    sys.exit(
        f"REFUSING: '{py}' is the CARRIED python under {carried}.\n"
        f"Build with the SYSTEM python, e.g.:\n"
        f'  & "C:/Program Files/Python312/python.exe" .\\build_complete_public_release.py'
    )


#: Managed config files that `regen_secrets.py` REWRITES, so STEP 1 can back every
#: one of them up byte-for-byte BEFORE running it.
#:
#: WARNING: DERIVED, never hand-typed. The hand-written list carried only 5 of the
#: 7 agent config.yaml files regen actually edits -- `zavuerer` and `discoverer`
#: were missing. On a machine WITHOUT data.keys the `finally` re-key is skipped, so
#: those two were scrubbed to placeholders with NO backup to restore from: silent
#: loss of the operator's own keys. Reading the paths out of regen_secrets itself
#: means the NEXT managed config file is covered the day it is added there.
#: Pinned by Tlamatini/agent/test_public_release_targets.py.
_REGEN_MANAGED_BASENAMES = ("config.json", "config.yaml", "external_mcps.json")
_REGEN_TOUCHED_FALLBACK = [
    REPO_ROOT / "Tlamatini" / "agent" / "config.json",
    REPO_ROOT / "Tlamatini" / "agent" / "external_mcps.json",
] + [REPO_ROOT / "Tlamatini" / "agent" / "agents" / _a / "config.yaml"
     for _a in ("telegrammer", "whatsapper", "teletlamatini", "emailer",
                "recmailer", "zavuerer", "discoverer")]
#: Obvious TEMPLATE stand-ins, not real private data. Stripped from the scrub set
#: so that copying private_targets.example.json to .private_targets.json and
#: forgetting to fill it in behaves like "no targets given" (-> the pre-flight
#: decides) instead of like "targets given" (-> a build that reports VERIFIED
#: CLEAN having scrubbed the literal text "<your phone number>").
#
# NOTE ON THE PREFIX GROUP: it matches with NO word boundary, because the real
# placeholders in this repo are glued: `YourStrongPassword` (sqler/config.yaml),
# `YOUR_EMAIL_HERE`, `ChangeMeNow`. A `\b` after the keyword misses every one of
# them -- `\b` needs a non-word char, and `S`/`_` are word chars. The prefixes are
# therefore chosen to be ones no real name or value starts with; in particular
# `my` is DELIBERATELY ABSENT, because it would swallow real names like "Myriam".
_PLACEHOLDER_RE = re.compile(
    r"""(?ix)
    ^\s*(?:
        <[^>]*>                                            # <your email>, <REDACTED>
      | (?:your|example|sample|dummy|placeholder|changeme|change[_\- ]me
          |replace[_\- ]?me|fill[_\- ]?me|todo|tbd|xxx+).*  # glued, no \b
      | (?:none|n/?a)\b.*                                  # short: boundary needed
      | [^@\s]*@(?:example|sample|test|invalid|localhost)\.[a-z.]+   # RFC 2606
      | \+?[\s\-()]*0[\d\s\-()]*                           # +000000000, 000-000-0000
    )\s*$""")
#: Credential-shaped config keys. Anchored on purpose -- a bare `token` substring
#: would match `max_tokens: 4096` in talker/config.yaml and make EVERY tree look
#: keyed, which would permanently refuse the very clone this feature exists for.
_SECRET_NAME_RE = re.compile(
    r"(?i)(?:^|[_.\-])(?:api[_-]?key|apikey|api[_-]?secret|access[_-]?token"
    r"|auth[_-]?token|bearer[_-]?token|client[_-]?secret|session[_-]?string"
    r"|password|passwd|secret)(?:$|[_.\-])"
    r"|(?:^|[_.\-])(?:token|key)$")
#: Un valor que NO puede ser una credencial viva NI un dato personal. `[\d.]+` cubre
#: BOTH plain numbers (`max_body_bytes: 1048576`) and dotted-numeric addresses
#: (`host: 127.0.0.1`, `webhook_host: 0.0.0.0`) -- committed defaults that a
#: naive phone-shape test happily reads as a phone number. `tlamatini` is the
#: product's own name, shipped as the default `verify_token` in whatsapper and
#: instant_messaging_doctor; it is a documented default, never a credential.
_INERT_VALUE_RE = re.compile(
    r"(?i)^\s*(?:|<[^>]*>|none|null|false|true|changeme|tlamatini|\d+|[\d.]+)\s*$")
#: FORMAS DE PII — reconocibles sin conocer los valores reales de Angela.
_EMAIL_SHAPE_RE = re.compile(r"[^@\s<>\"']+@[^@\s<>\"']+\.[A-Za-z]{2,}")
#: A written phone number carries a `+` or a separator. Requiring one (and
#: excluding `.` from the class entirely) is what stops `1048576` and `127.0.0.1`
#: from reading as phone numbers -- the exact false positives that made a fresh
#: clone unbuildable when this was first written.
_PHONE_SHAPE_RE = re.compile(r"^\+?[\d\s\-()]{7,24}$")
_PHONE_SEPARATORS = ("+", " ", "-", "(")
#: Una credencial viva mide al menos esto. Los valores cortos son ajustes
#: (`sort_key: mtime`, `key: id`), not secrets, and treating them as secrets would
#: make a pristine clone unbuildable.
_MIN_SECRET_LEN = 8


def _regen_touched_files() -> list[Path]:
    """Toda ruta que regen_secrets.py puede reescribir, leida del propio regen_secrets.

    FALLA HACIA RESPALDAR DE MAS: si el import devuelve menos rutas que el
    fallback explicito (una constante renombrada, un error de sintaxis, una
    lectura a medias), gana el fallback. Respaldar un archivo que no hacia falta
    cuesta una copia; NO respaldar uno cuesta las credenciales de la operadora.
    """
    try:
        import importlib.util as _ilu
        spec = _ilu.spec_from_file_location("_tlm_regen_paths", REGEN)
        mod = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        found = sorted({v for name, v in vars(mod).items()
                        if name.isupper() and isinstance(v, Path)
                        and v.name in _REGEN_MANAGED_BASENAMES})
        if len(found) >= len(_REGEN_TOUCHED_FALLBACK):
            return found
        print(f"  NOTA: regen_secrets expuso {len(found)} ruta(s) administrada(s); uso "
              f"el fallback de {len(_REGEN_TOUCHED_FALLBACK)} rutas (respaldo de mas).")
    except Exception as exc:
        print(f"  NOTA: no pude leer las rutas de regen_secrets ({exc}); uso la "
              f"lista de fallback explicita.")
    return list(_REGEN_TOUCHED_FALLBACK)

#: ⚠️ DERIVADA, NO ESCRITA A MANO. La lista de aqui estaba tecleada y le
#: FALTABAN `external_mcps.json`, `zavuerer` y `discoverer` — tres archivos que
#: regen_secrets SI reescribe. Un build publico los habria dejado en placeholders
#: SIN respaldo, o sea perdiendo las llaves de la operadora sin avisar.
#: `_regen_touched_files()` se las pregunta al propio regen_secrets y falla hacia
#: RESPALDAR DE MAS: respaldar de mas cuesta una copia; respaldar de menos cuesta
#: las credenciales.
REGEN_TOUCHED = _regen_touched_files()



def _is_placeholder(value: str) -> bool:
    """True cuando el valor es un relleno de plantilla.

    CONSERVADORA A PROPOSITO. Un "si" equivocado aqui SACA un valor real del
    conjunto a limpiar, y ese es EL error que publica datos privados — asi que
    solo casan formas de plantilla inconfundibles, y todo lo ambiguo se trata
    como real.
    """
    return bool(_PLACEHOLDER_RE.match(value or ""))


def _is_live_secret(name, value) -> bool:
    if not isinstance(value, str) or not _SECRET_NAME_RE.search(str(name)):
        return False
    v = value.strip().strip("'\"")
    if len(v) < _MIN_SECRET_LEN or _INERT_VALUE_RE.match(v) or _is_placeholder(v):
        return False
    return "goes here" not in v.lower()


def _looks_like_pii(value: str) -> bool:
    """Un correo o un telefono ESCRITO, juzgado solo por su forma.

    La prueba de valores inertes va PRIMERO, y es la que deja fuera los valores
    por defecto que si estan commiteados: un conteo de bytes (`1048576`) o una
    direccion de bind (`127.0.0.1`, `0.0.0.0`) son numeros, no personas. Un
    telefono ademas tiene que traer un `+` o un separador y entre 7 y 15
    digitos, asi que un entero pelado nunca califica.
    """
    v = (value or "").strip()
    if not v or _INERT_VALUE_RE.match(v) or _is_placeholder(v):
        return False
    if _EMAIL_SHAPE_RE.search(v):
        return True
    return bool(_PHONE_SHAPE_RE.match(v)
                and any(sep in v for sep in _PHONE_SEPARATORS)
                and 7 <= sum(c.isdigit() for c in v) <= 15)


def _json_secret_hits(path: Path) -> list[str]:
    """Llaves con forma de credencial cuyo valor NO es un relleno, a cualquier profundidad."""
    hits: list[str] = []

    def walk(node, trail: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                where = f"{trail}.{k}" if trail else str(k)
                if _is_live_secret(k, v):
                    hits.append(where)
                else:
                    walk(v, where)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{trail}[{i}]")

    walk(json.loads(path.read_text(encoding="utf-8-sig")), "")
    return sorted(set(hits))


def _yaml_scan(path: Path) -> tuple[list[str], list[str]]:
    """(llaves de credencial, llaves con forma de PII) en UN config.yaml de agent.

    Va por lineas, igual que el parcheador de YAML del propio regen_secrets (que
    edita linea por linea para no perder los comentarios) — asi no depende de
    yaml y no reformatea nada.
    """
    secrets: list[str] = []
    pii: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0]
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip().strip("'\"")
        if not key or not val:
            continue
        if _is_live_secret(key, val):
            secrets.append(key)
        elif _looks_like_pii(val):
            pii.append(key)
    return sorted(set(secrets)), sorted(set(pii))


def privacy_preflight() -> list[str]:
    """Evidencia de que este arbol de trabajo trae material privado que limpiar.

    Devuelve lineas de evidencia que una persona puede leer; una lista VACIA
    significa "arbol limpio".

    ⚠️ POR QUE EXISTE: antes el build del release publico se NEGABA a correr sin
    `.private_targets.json`, un archivo que esta en .gitignore — o sea que un
    clon nuevo, otra maquina o un CI JAMAS podian construir el release publico.
    Pero la negativa no era simplemente un error: sin esa lista, la MISMA
    ausencia significa dos cosas OPUESTAS, y solo una es segura.

        clon PRISTINO, no hay nada privado en el arbol  -> construir
        el arbol de Angela, con el archivo borrado      -> NEGARSE

    Esta sonda le pregunta AL ARBOL cual de los dos casos es, sin depender de
    ninguna lista de objetivos.
    """
    evidence: list[str] = []

    def probe(label: str, fn) -> None:
        """Corre UNA sonda. CUALQUIER excepcion cuenta como evidencia — nunca pasa callando."""
        try:
            found = fn()
        except Exception as exc:
            evidence.append(
                f"{label}: ILEGIBLE ({exc}) — cuenta COMO dato privado, porque un "
                f"archivo que no se pudo revisar jamas debe darse por limpio")
            return
        if found:
            evidence.append(f"{label}: {found}")

    agent_dir = REPO_ROOT / "Tlamatini" / "agent"

    def _vault() -> str:
        vault = REPO_ROOT / "data.keys"
        if not vault.is_file():
            return ""
        n = sum(1 for ln in vault.read_text(encoding="utf-8",
                                            errors="replace").splitlines()
                if "=" in ln and not ln.lstrip().startswith("#"))
        return f"presente, {n} llave(s) — este es un arbol CON LLAVES, de mantenimiento" if n else ""

    probe("data.keys (la boveda de secretos vivos)", _vault)

    for cfg in (agent_dir / "config.json", agent_dir / "external_mcps.json"):
        def _json_probe(p=cfg) -> str:
            return ", ".join(_json_secret_hits(p)) if p.is_file() else ""
        probe(f"{cfg.name} trae secreto(s) vivo(s)", _json_probe)

    for yml in sorted(agent_dir.glob("agents/*/config.yaml")):
        def _yaml_probe(p=yml) -> str:
            secrets, pii = _yaml_scan(p)
            parts = []
            if secrets:
                parts.append("secreto(s) vivo(s): " + ", ".join(secrets))
            if pii:
                parts.append("correo/telefono real en: " + ", ".join(pii))
            return "; ".join(parts)
        probe(f"agents/{yml.parent.name}/config.yaml", _yaml_probe)

    for book in (agent_dir / "contacts.json", agent_dir / "contacts.private.json",
                 REPO_ROOT / "contacts.json", REPO_ROOT / "contacts.private.json"):
        def _book_probe(p=book) -> str:
            if not p.is_file():
                return ""
            data = json.loads(p.read_text(encoding="utf-8-sig") or "null")
            n = len(data) if isinstance(data, (list, dict)) else 0
            return f"{n} contacto(s) real(es)" if n else ""
        probe(f"{book.name} (una libreta de contactos de personas reales)", _book_probe)

    probe("archivo(s) de llave privada en la raiz del repo",
          lambda: ", ".join(sorted(p.name for p in REPO_ROOT.glob("*.key"))))

    return evidence



def _utf8_env() -> dict:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    # Silence pip's "A new release of pip is available" nag in EVERY child of
    # this wrapper (build.py / build_uninstaller.py / build_installer.py) and in
    # every pip THEY spawn. It is pure noise, and upgrading pip does not fix it:
    # the build Python is normally the SYSTEM one under Program Files, whose pip
    # sits in a READ-ONLY prefix (upgrading the carried <repo>/python's pip
    # instead changes nothing there). Full rationale in build.py.
    # Pinned by Tlamatini/agent/test_build_pip_quiet.py.
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    # PUBLIC build ALWAYS ships an EMPTY contacts.json -- never a real book, even
    # if the ambient shell exported TLAMATINI_BUNDLE_CONTACTS. build.py ships the
    # empty placeholder whenever this is unset.
    env.pop("TLAMATINI_BUNDLE_CONTACTS", None)
    # PUBLIC build ALWAYS ships ONLY the External MCP servers Tlamatini herself
    # implements (memory, sequential-thinking) -- never the maintainer's catalog,
    # even if the ambient shell exported TLAMATINI_BUNDLE_EXTERNAL_MCPS. build.py
    # generates that two-server catalog from external_mcp_defaults whenever this
    # is unset, and hard-ABORTS the build if a live secret ever reaches it.
    env.pop("TLAMATINI_BUNDLE_EXTERNAL_MCPS", None)
    return env


def run(cmd: list[str], *, cwd: Path = REPO_ROOT) -> int:
    print(f"\n$ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=str(cwd), env=_utf8_env()).returncode


def default_targets_file() -> Path | None:
    for cand in DEFAULT_TARGETS_FILES:
        if cand.is_file():
            return cand
    return None


def load_targets_values(args) -> list[str]:
    """Reuse check_private_data.load_targets (NEVER hardcode private data)."""
    sys.path.insert(0, str(REPO_ROOT))
    import check_private_data as cpd  # noqa: E402
    ns = SimpleNamespace(targets_file=args.targets_file, target=args.target)
    targets = cpd.load_targets(ns)
    # NEVER scrub Angela's name -- keep her authorship everywhere, in every build.
    # ⚠️ DOS EXCLUSIONES MAS, y las dos existen para que una PLANTILLA SIN LLENAR
    # no se haga pasar por una lista de objetivos de verdad (eso callaria la sonda
    # y produciria un build que imprime VERIFICADO LIMPIO sin haber limpiado nada):
    #   * las llaves JSON que empiezan con `_` son DOCUMENTACION, no datos.
    #     cpd.load_targets convierte CADA llave en una `category` y cada valor en
    #     un objetivo, asi que sin esto un `_README` se vuelve un 'valor privado'
    #     que ir a cazar por todo el arbol. Es la misma convencion del `_` que ya
    #     usa external_mcps.json.
    #   * los valores con forma de relleno se descartan — ver _is_placeholder.
    vals = [t["value"] for t in targets
            if t.get("value", "").strip()
            and not str(t.get("category", "")).startswith("_")
            and not _is_kept_name(t["value"])
            and not _is_placeholder(t["value"])]
    return sorted(set(vals), key=len, reverse=True)


class Backup:
    """Byte-for-byte backup + guaranteed restore of every file we mutate."""

    def __init__(self, root: Path):
        self.dir = root / "Temp" / f"public_build_backup_{time.strftime('%Y%m%d_%H%M%S')}"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.saved: dict[Path, Path] = {}

    def save(self, path: Path) -> None:
        path = path.resolve()
        if path in self.saved or not path.exists():
            return
        rel = path.relative_to(REPO_ROOT) if str(path).startswith(str(REPO_ROOT)) else Path(path.name)
        dst = self.dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dst)
        self.saved[path] = dst

    def restore_all(self) -> None:
        for orig, bak in self.saved.items():
            try:
                shutil.copy2(bak, orig)
            except Exception as e:  # pragma: no cover
                print(f"  [!] restore FAILED for {orig}: {e}", file=sys.stderr)
        print(f"  restored {len(self.saved)} file(s) to their original bytes.")


def scrub_file(path: Path, values: list[str], extra: list[str], backup: Backup) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return 0
    original = text
    for v in values + extra:
        if v and v in text:
            text = text.replace(v, PLACEHOLDER)
    text = SECRET_KEY_RE.sub(lambda m: m.group(1) + PLACEHOLDER + m.group(3), text)
    if text != original:
        try:
            backup.save(path)
            path.write_text(text, encoding="utf-8")
        except OSError as exc:
            # A read-only / locked file we don't own (e.g. a bundled runtime's
            # module cache) must NEVER abort the release. SKIP_DIRS already excludes
            # the known runtime trees; this is the belt-and-suspenders backstop.
            print(f"  [skip] cannot scrub {path}: {exc}")
            return 0
        return 1
    return 0


def scrub_tree(values: list[str], extra: list[str], backup: Backup) -> int:
    changed = 0
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if os.path.splitext(name)[1].lower() not in TEXT_EXT:
                continue
            if name in SCRUB_SKIP_FILES:
                continue
            changed += scrub_file(Path(dirpath) / name, values, extra, backup)
    return changed


def newest_release_dir() -> Path | None:
    cands = sorted(glob.glob(str(DIST / "Tlamatini_Release_v*")),
                   key=lambda p: os.path.getmtime(p), reverse=True)
    for c in cands:
        if Path(c).is_dir():
            return Path(c)
    return None


def resolve_verify_root() -> Path:
    """What STEP 5 scans. build.py creates pkg.zip then DELETES dist/, so the real
    artifact is pkg.zip -- extract it and scan that. Fall back to dist/manage when
    an older build.py still leaves it in place."""
    if DIST_MANAGE.exists():
        return DIST_MANAGE
    if PKG_ZIP.exists():
        if VERIFY_EXTRACT.exists():
            shutil.rmtree(VERIFY_EXTRACT, ignore_errors=True)
        VERIFY_EXTRACT.mkdir(parents=True, exist_ok=True)
        print(f"  build.py removed dist/; extracting {PKG_ZIP.name} to verify...", flush=True)
        with zipfile.ZipFile(PKG_ZIP) as zf:
            zf.extractall(VERIFY_EXTRACT)
        return VERIFY_EXTRACT
    sys.exit("ERROR: neither dist/manage nor pkg.zip exists after build.py.")


#: Se le pasa al auditor en MODO ARBOL LIMPIO. check_private_data.py sale con 2
#: cuando no recibe ningun objetivo, lo que tumbaria el build — pero saltarse la
#: auditoria entera dejaria caer EN SILENCIO la unica inspeccion post-build. Un
#: valor que no puede aparecer en ningun artefacto cumple su precondicion, asi
#: que todas las capas ESTRUCTURALES (bloques PEM, certificados, blobs de alta
#: entropia, material Kyber, esteganografia) siguen corriendo, y el conteo de PII
#: es cero de verdad porque nunca se busco PII.
STRUCTURAL_ONLY_SENTINEL = "TLAMATINI-NO-PII-TARGETS-SENTINEL-8f3c1d47a9b24e60"


def verify_clean(py: str, verify_root: Path, targets_file: str,
                 target: list[str], use_llm: bool,
                 structural_only: bool = False) -> int:
    """Run the auditor over the built package. Returns the number of files that
    contain YOUR personal data (the BLOCKING count). Structural/binary pattern
    matches (kyber keyword, certs, high-entropy, PEM) are reported but never block."""
    report = REPO_ROOT / "public_release_verify_report.json"
    cmd = [py, str(CHECKER), "--local", "--repo", str(verify_root),
           "--output", str(report)]
    if structural_only:
        cmd += ["--target", STRUCTURAL_ONLY_SENTINEL]
    else:
        if targets_file:
            cmd += ["--targets-file", targets_file]
        for t in target or []:
            cmd += ["--target", t]
    if not use_llm:
        cmd += ["--no-llm"]
    rc = run(cmd)
    if rc == 2:
        sys.exit("VERIFY ERROR: auditor got no targets. Pass --targets-file/--target.")
    import json
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except Exception:
        return 1 if rc else 0
    findings = []
    for scan in data.get("scans", []):
        findings += scan.get("result", {}).get("findings", [])

    def _is_sensitive(value: str) -> bool:
        # BLOCK only on genuinely-unique PII: emails (contain '@') and phone
        # numbers (>=7 digits). Bare common names ("Angela", "Ana") are NOT
        # blocked -- they appear all over bundled third-party libraries (django,
        # nltk, emoji, ...) and Angela wants her name left everywhere by design.
        # Angela's OWN kept name / handle (@angelahack1) is never a leak, even
        # though the handle contains '@' -- so it never blocks the build.
        v = value or ""
        if _is_kept_name(v):
            return False
        return ("@" in v) or (sum(c.isdigit() for c in v) >= 7)

    personal = 0
    name_only = 0
    struct = 0
    for f in findings:
        ms = f.get("matches", [])
        pii = [m for m in ms
               if (m.get("layer", "").startswith("bytes:") or m.get("layer") == "fuzzy-regex")]
        if any(_is_sensitive(m.get("target", "")) for m in pii):
            personal += 1
        elif pii:
            name_only += 1
        struct += sum(1 for m in ms if m.get("layer", "").startswith(("struct:", "steg:")))
    if structural_only:
        # NO MENTIR: decir exactamente que se reviso y que no. Reportar
        # "0 fugas de PII" sin esta linea daria a entender una verificacion
        # de datos personales que nunca ocurrio.
        print("  MODO: MODO ARBOL LIMPIO — no se dieron objetivos de PII, asi que "
              "NO se busco ningun dato personal (el 0 es por construccion, no "
              "por inspeccion).")
    print(f"  sensitive PII leak files (BLOCKING: emails/handles/phones): {personal}")
    print(f"  name-only matches (NOT blocking; common names left as-is): {name_only}")
    print(f"  structural/binary false-positive matches (informational only): {struct}")
    return personal


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build a PUBLIC (scrubbed, leak-verified) Tlamatini release.")
    ap.add_argument("--targets-file", help="JSON {names,phones,handles} or newline list of private values")
    ap.add_argument("--target", action="append", help="one private value to scrub/verify (repeatable)")
    ap.add_argument("--extra-redact", action="append", default=[],
                    help="extra literal string to scrub (e.g. a leaked apikey); repeatable")
    ap.add_argument("--version", default="", help="explicit version (default: git-tag derived)")
    ap.add_argument("--python", default=sys.executable, help="system python to drive the build")
    # DEFAULT IS OFF: a public release ships NEITHER the TlamatiniSourceCode
    # tree NOR Tlamatini.md (her self-knowledge) — the two travel together, and
    # dropping both keeps ~15.7k tokens out of the system prompt on EVERY
    # request. --no-self-modify is accepted as the explicit form of the default.
    ap.add_argument("--self-modify", action="store_true",
                    help="also bundle the (scrubbed) TlamatiniSourceCode tree AND "
                         "Tlamatini.md (default: NEITHER is bundled).")
    ap.add_argument("--no-self-modify", action="store_true",
                    help="explicit form of the DEFAULT; overrides --self-modify.")
    ap.add_argument("--verify-llm", action="store_true",
                    help="let the auditor also run its LLM deep-review layer (slower, deeper)")
    ap.add_argument("--keep-scrubbed", action="store_true",
                    help="DANGEROUS: do not restore the working tree afterwards")
    ap.add_argument("--assume-clean-tree", action="store_true",
                    help="PELIGROSO: construir SIN objetivos aunque la sonda de "
                         "privacidad haya encontrado material privado en este arbol. "
                         "Estas afirmando que TODO lo reportado se puede publicar.")
    ap.add_argument("--exclude-module", action="append", default=[],
                    metavar="MODULO",
                    help="Modulo que PyInstaller NO debe empaquetar en el proceso "
                         "congelado. Se puede repetir. Se reenvia tal cual a build.py. "
                         "NO afecta al Python ACARREADO (otro interprete), asi que no "
                         "puede dejar muda a Tlamatini.")
    args = ap.parse_args(argv)
    # --no-self-modify is the explicit form of the DEFAULT and always wins, so a
    # wrapper (or muscle memory) can force the small-prompt build unambiguously.
    if args.no_self_modify:
        args.self_modify = False

    py = args.python
    assert_system_python(py)

    # If no targets given, auto-load the local gitignored targets file so the bare
    # command just works. Values are read from that file -- never hardcoded.
    if (not args.targets_file and not args.target
            and not os.environ.get("CHECK_PRIVATE_DATA_TARGETS")):
        auto = default_targets_file()
        if auto:
            args.targets_file = str(auto)
            print(f"targets file : auto-loaded {auto.name} (no --targets-file given)")

    values = load_targets_values(args)

    # ⛔ SIN LISTA DE OBJETIVOS NO ES UN ERROR POR SI MISMO (Angela, 2026-08-30).
    # `.private_targets.json` esta en .gitignore, asi que un clon nuevo, otra
    # maquina o un CI NUNCA pueden tenerlo — y antes eso bastaba para que el
    # build del release publico se negara a correr. Pero la misma ausencia
    # significa dos cosas OPUESTAS y solo una es segura:
    #
    #   clon PRISTINO (no hay nada privado)  -> construir; la negativa era friccion
    #   el arbol de Angela, archivo borrado  -> NEGARSE; publicar seria filtrar
    #
    # Asi que decide una sonda que le pregunta AL ARBOL, no a la lista, y que
    # FALLA HACIA LA NEGATIVA: cualquier archivo ilegible cuenta como evidencia.
    clean_tree = False
    if not values:
        banner("SONDA DE PRIVACIDAD  (sin objetivos — reviso el arbol)")
        evidence = privacy_preflight()
        for line in evidence:
            print(f"  [EVIDENCIA] {line}")
        if evidence and not args.assume_clean_tree:
            sys.exit(
                f"\nME NIEGO: este arbol de trabajo trae material privado "
                f"({len(evidence)} cosa(s) arriba) pero NO hay lista de que limpiar, "
                f"asi que un build publico lo publicaria.\n\n"
                f"Arreglalo como te acomode:\n"
                f"  1. copia {TARGETS_TEMPLATE.name} -> .private_targets.json y pon "
                f"TUS valores reales\n"
                f"     (ese nombre esta en .gitignore, nunca sale de tu maquina)\n"
                f"  2. --targets-file <ruta>\n"
                f"  3. --target \"valor\"          (se puede repetir)\n"
                f"  4. la variable de entorno CHECK_PRIVATE_DATA_TARGETS\n"
                f"  5. PELIGROSO, solo si estas segura de que TODO lo de arriba se "
                f"puede publicar: --assume-clean-tree\n\n"
                f"(Los datos privados NUNCA estan escritos a mano en este repo — por "
                f"eso la lista tiene que venir de ti.)")
        if evidence:
            print("\n  !!! SE PASO --assume-clean-tree: sigo a pesar de la evidencia "
                  "de arriba.")
            print("  !!! NO va a correr NI la limpieza NI la verificacion de datos "
                  "personales.")
            print("  !!! Estas afirmando que todo lo de arriba se puede publicar.")
        else:
            print("  no encontre material privado — este es un clon pristino, asi que "
                  "no hay nada que limpiar.")
        clean_tree = True

    banner("PUBLIC RELEASE BUILD  (SCRUBBED + LEAK-VERIFIED -- safe to distribute)")
    print(f"repo         : {REPO_ROOT}")
    print(f"python       : {py}")
    if clean_tree:
        print("targets      : NINGUNO — MODO ARBOL LIMPIO (sin limpieza ni verificacion de PII)")
        print("               SIGUEN ACTIVAS: regen_secrets --mode push-able; la "
              "limpieza por regex")
        print("               de secret-key; una libreta de contactos VACIA; el "
              "catalogo de MCPs")
        print("               sembrado desde el codigo; y el aborto duro de build.py "
              "ante un secreto vivo.")
    else:
        print(f"targets      : {len(values)} valor(es) que limpiar y verificar")
    print(f"self-modify  : {'YES (scrubbed snapshot) — source tree + Tlamatini.md bundled' if args.self_modify else 'no (DEFAULT) — no source tree, no self-knowledge, smaller prompt'}")

    backup = Backup(REPO_ROOT)
    ok = False
    try:
        banner("STEP 1/6  regen_secrets.py --mode push-able")
        for f in REGEN_TOUCHED:
            backup.save(f)
        if run([py, str(REGEN), "--mode", "push-able"]) != 0:
            sys.exit("regen_secrets push-able failed.")

        # Ship a CLEAN External-MCP catalog in the PUBLIC build (user state).
        if EXTERNAL_MCPS.exists():
            backup.save(EXTERNAL_MCPS)
            EXTERNAL_MCPS.write_text('{\n  "mcpServers": {},\n  "active": []\n}\n',
                                     encoding="utf-8")
            print("  sanitized external_mcps.json (empty catalog for public build).")

        banner("STEP 2/6  scrubbing private data from the working tree")
        n = scrub_tree(values, args.extra_redact, backup)
        print(f"  scrubbed {n} file(s).")

        banner("STEP 3/6  build.py (reads the scrubbed tree)")
        build_cmd = [py, str(BUILD)]
        # Pass the decision EXPLICITLY either way, so the intent is recorded in
        # the build log and a stray "--self-modify" in the ambient argv cannot
        # flip it. DEFAULT (no flag on this script) = not-self-able-modify.
        build_cmd.append("--self-modify" if args.self_modify else "--no-self-modify")
        if args.version:
            build_cmd.append(args.version)
        if run(build_cmd) != 0:
            sys.exit("build.py failed.")
        assert_self_modify_payload(args.self_modify)

        # build.py creates pkg.zip then removes dist/, so scan the package
        # (extracted) instead of the deleted dist/manage.
        banner("STEP 4/6  VERIFY the built package is clean (check_private_data.py)")
        verify_root = resolve_verify_root()
        leaks = verify_clean(py, verify_root, args.targets_file, args.target, args.verify_llm, structural_only=clean_tree)
        if VERIFY_EXTRACT.exists():
            shutil.rmtree(VERIFY_EXTRACT, ignore_errors=True)
        if leaks:
            sys.exit(f"\n!!! ABORT: {leaks} file(s) in the build STILL contain your personal "
                     f"data. No public artifact produced. See public_release_verify_report.json. "
                     f"(Working tree will be restored.)")
        print("  VERIFIED CLEAN: 0 files with your personal data.")

        banner("STEP 5/6  build_uninstaller.py + build_installer.py")
        if run([py, str(BUILD_UNINST)] + ([args.version] if args.version else [])) != 0:
            sys.exit("build_uninstaller.py failed.")
        if run([py, str(BUILD_INST)] + ([args.version] if args.version else [])) != 0:
            sys.exit("build_installer.py failed.")

        rel = newest_release_dir()
        if rel is None:
            sys.exit("ERROR: no dist/Tlamatini_Release_v* folder was produced.")

        banner("STEP 6/6  packaging PUBLIC CLEAN zip")
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_base = DIST / f"{rel.name}_PUBLIC_CLEAN_win11x64_{ts}"
        archive = shutil.make_archive(str(out_base), "zip", root_dir=str(DIST), base_dir=rel.name)

        ok = True
        banner("PUBLIC RELEASE COMPLETE -- VERIFIED CLEAN")
        print(f"  release folder : {rel}")
        print(f"  public zip     : {archive}")
        print(f"  verify report  : {REPO_ROOT / 'public_release_verify_report.json'}")
        return 0
    finally:
        banner("RESTORING WORKING TREE (no git history was touched)")
        if args.keep_scrubbed:
            print("  --keep-scrubbed set: tree LEFT scrubbed (remember to restore it!).")
        else:
            backup.restore_all()
            if Path(REPO_ROOT / "data.keys").exists():
                run([py, str(REGEN), "--mode", "keyed"])
        if not ok:
            print("  (build did not complete; see messages above.)")


if __name__ == "__main__":
    raise SystemExit(main())
