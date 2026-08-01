# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""
Regenerate TERMINOLOGY.md from the LIVE ``agent/i18n/`` files.

WHY THIS SCRIPT EXISTS
    TERMINOLOGY.md has always ended with "Generated from the live
    ``agent/i18n/`` files. Regenerate rather than edit by hand." — but the
    generator was never committed. It lived once as a throwaway scratch script
    under ``Temp/`` and read a hand-dumped JSON snapshot, so there was no
    reproducible way to regenerate the document at all.

    The predictable happened: by 2026-07-29 the committed document disagreed
    with the code in six counts AND contradicted itself twice (its summary
    claimed 24 forbidden renderings while its own section header said 34; the
    SPANISH_PREFERRED header said 26 while the table under it listed 33).

    This script closes that hole. It imports the real modules — no intermediate
    JSON, nothing transcribed — so every number below is whatever the code
    actually enforces at the moment you run it.

USAGE
    python docs/research/spanish-localization/generate_terminology.py

    Writes TERMINOLOGY.md next to this script. Override with --out <path>
    (repeatable), or --check to verify without writing (exit 1 when the
    committed file is stale — CI-friendly).

WHERE THESE ASSETS LIVE (Angela, 2026-07-29)
    Every English->Spanish conversion asset now lives ONLY in Tlamatini-Spanish.
    The English tree used to carry a second copy of docs/research/
    spanish-localization/; it was removed so there is exactly one home for this
    work and the two copies can never drift apart again (they already had).
    The sibling-tree destination below is kept only so the script still does
    the right thing if that layout ever comes back — it is skipped when the
    directory does not exist.
"""
import argparse
import csv
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# docs/research/spanish-localization -> repo root
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DJANGO_ROOT = os.path.join(REPO_ROOT, "Tlamatini")

# Default destinations: this repo, and the sibling tree if it is present.
_DEFAULT_OUTS = [
    os.path.join(HERE, "TERMINOLOGY.md"),
    os.path.join(os.path.dirname(REPO_ROOT), "Tlamatini",
                 "docs", "research", "spanish-localization", "TERMINOLOGY.md"),
    os.path.join(os.path.dirname(REPO_ROOT), "Tlamatini-Spanish",
                 "docs", "research", "spanish-localization", "TERMINOLOGY.md"),
]


def _load_live():
    """Import the live i18n modules. Fails loudly — a silent fallback here
    would reintroduce exactly the drift this script exists to prevent."""
    if DJANGO_ROOT not in sys.path:
        sys.path.insert(0, DJANGO_ROOT)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tlamatini.settings")
    from agent.i18n import lexicon_es, termbase_en, ui_es
    return termbase_en, lexicon_es, ui_es


def _load_terms_csv():
    """agent/i18n/terms.csv — the reviewable source of truth (added 2026-07)."""
    path = os.path.join(DJANGO_ROOT, "agent", "i18n", "terms.csv")
    if not os.path.exists(path):
        return []
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


PURPOSE = {
    "MACHINE_SENTINELS": (
        "Literals the MACHINE reads back. Translating one does not spoil the "
        "style, it breaks the protocol."),
    "PRODUCT_TERMS": (
        "Tlamatini's own product vocabulary. Angela named MCPs and Wizard "
        "explicitly; the toolbar toggles are feature NAMES."),
    "AGENT_DISPLAY_NAMES": (
        "The asset names. Case and hyphenation are FUNCTIONAL - the canvas "
        "connection handler compares the hyphenated literal."),
    "TOOL_NAMES": (
        "Wrapped tool identifiers and their Tool-row descriptions. Pure "
        "machine surface that happens to be visible in the Exec Report."),
    "TECH_CONTAINERS": (
        "Containers and orchestration. Angela's own example sentence lives "
        "here: Pod, Container, Kubernetes, deployment, LPAR."),
    "TECH_VCS": "Version control. 'Haz un commit y push' is how it is said.",
    "TECH_BUILD": "Build and release vocabulary.",
    "TECH_RUNTIME": "Runtime and diagnostics. 'log' is the load-bearing one.",
    "TECH_WEB": "Web and API vocabulary.",
    "TECH_DATA": "Data and persistence.",
    "TECH_FILES_OS": "Files, OS and shell.",
    "TECH_AI": "AI / LLM vocabulary - the newest and least calqued domain.",
    "TECH_FIRMWARE": "Hardware and firmware (STM32er / ESP32er / Arduiner).",
    "TECH_SECURITY": "Security (Kalier / Nmapper / Discoverer).",
}

FAMILY_ORDER = [
    "MACHINE_SENTINELS", "PRODUCT_TERMS", "AGENT_DISPLAY_NAMES", "TOOL_NAMES",
    "TECH_CONTAINERS", "TECH_VCS", "TECH_BUILD", "TECH_RUNTIME", "TECH_WEB",
    "TECH_DATA", "TECH_FILES_OS", "TECH_AI", "TECH_FIRMWARE", "TECH_SECURITY",
]

WHY = {
    "Folder": "everyday noun, exact equivalent",
    "File": "everyday noun, exact equivalent",
    "Directory": "cognate, unambiguous",
    "Path": "*ruta* is universal; no concept is lost",
    "Port": "*puerto* is universal",
    "Command": "*comando* is in the RAE dictionary and said by everyone",
    "Status": "*estado* is unambiguous in prose",
    "Context": "*contexto* is a direct cognate",
    "Chain": "*cadena* is the standard word",
    "Image": "*imagen* - note the Docker sense stays `Image`",
    "Output": "*salida* is unambiguous",
    "Input": "*entrada* is unambiguous",
    "Volume": "*volumen* - the audio sense; Docker volume stays English",
    "Screen": "*pantalla* is universal",
    "Window": "*ventana* is universal",
    "Network": "*red* is universal",
    "Password": "*contraseña* is universal",
    "User": "*usuario* is universal",
    "Name": "everyday noun",
    "Date": "everyday noun",
    "Size": "everyday noun",
    "Line": "everyday noun",
    "Page": "everyday noun",
    "Version": "direct cognate",
    "Save": "generic verb - carrier, not lexicon",
    "Open": "generic verb - carrier",
    "Close": "generic verb - carrier",
    "Cancel": "generic verb - carrier",
    "Continue": "generic verb - carrier",
    "Delete": "generic verb - carrier",
    "Search": "generic verb - carrier",
    "Send": "generic verb - carrier",
    "Help": "generic noun - carrier",
}


def build_markdown():
    termbase_en, lexicon_es, ui_es = _load_live()

    tb = {fam: list(getattr(termbase_en, fam))
          for fam in FAMILY_ORDER if hasattr(termbase_en, fam)}
    sp = dict(termbase_en.SPANISH_PREFERRED)
    forb = dict(termbase_en.FORBIDDEN_SPANISH_RENDERINGS)
    lex = dict(lexicon_es.ES_TO_CANONICAL)
    ui = dict(ui_es.UI_ES)
    rows = _load_terms_csv()

    sp_low = {k.lower(): v for k, v in sp.items()}

    L = []
    w = L.append

    w("# NEPANTLA Terminology Reference")
    w("")
    w("**The complete term inventory for Tlamatini's Spanish edition, read out "
      "of the live files.** Every count and every list below is produced by "
      "`generate_terminology.py`, which imports `agent/i18n/termbase_en.py`, "
      "`lexicon_es.py`, `ui_es.py` and `terms.csv` directly. Nothing is "
      "hand-transcribed, so this document cannot drift from what the code "
      "actually enforces.")
    w("")
    w("## The rule")
    w("")
    w("> Spanish supplies the grammar. English supplies the technical vocabulary.")
    w("")
    w("The register Tlamatini's users already speak:")
    w("")
    w("> *\"Haciendo un Pod en Dockerer y creando un Container en Kubernetes y "
      "haciendo el deployment en la LPAR\"*")
    w("")
    w("This is the **Matrix Language Frame** configuration (Myers-Scotton 1993): "
      "Spanish is the *matrix* language supplying morphosyntax and system "
      "morphemes; English is the *embedded* language supplying content morphemes, "
      "with multi-word feature names such as **Exec Report** entering whole as "
      "embedded-language islands. Iakovenko and Hain (2024, arXiv:2410.02521) "
      "confirm the direction empirically for this exact language pair: in real "
      "English/Spanish code-switching, Spanish is preferred as the matrix.")
    w("")
    w("The rule extends past nouns: Spanish supplies the **verbs** too. "
      "*\"Aguántame tantito\"*, *\"ya merito\"*, *\"ahorita\"* — the Mexican "
      "register is the carrier, and the English technical noun rides inside it "
      "untouched.")
    w("")
    w("## The adjudication criterion: *biunivocidad*")
    w("")
    w("Where a term is contested, the decision is not taste. Lazaro Carreter "
      "(1998: 587), quoted in Garriga Escribano (2022), endorses **unadapted** "
      "technical anglicisms precisely because doing so *\"facilita "
      "internacionalmente la biunivocidad que conviene a la terminologia "
      "cientifica\"* - it preserves the one-term-to-one-concept mapping technical "
      "vocabulary depends on. That gives a test:")
    w("")
    w("| | Rule |")
    w("|---|---|")
    w("| **KEEP ENGLISH** | when a Spanish rendering would BREAK the 1:1 mapping - "
      "the term names a specific technical concept whose Spanish form is invented, "
      "ambiguous, or collides with another domain. *Pod, Container, deployment, "
      "commit, log, pattern, token, endpoint.* |")
    w("| **USE SPANISH** | when an exact, unambiguous, everyday equivalent already "
      "exists and every speaker uses it. *ruta, comando, puerto, contexto, carpeta, "
      "archivo, pantalla, ventana.* |")
    w("")
    w("Nothing is lost by *\"la ruta del archivo\"*. Everything is lost by "
      "*\"la vaina\"* for a Pod.")
    w("")

    # ---------------------------------------------------------------- summary
    w("## Summary")
    w("")
    w("| Family | N | Moves? | Purpose |")
    w("|---|---:|---|---|")
    for fam in FAMILY_ORDER:
        if fam not in tb:
            continue
        w("| `%s` | %d | **no** | %s |" % (fam, len(tb[fam]), PURPOSE.get(fam, "")))
    w("| `SPANISH_PREFERRED` | %d | **yes** | English -> the Spanish rendering we DO want. |"
      % len(sp))
    w("| `FORBIDDEN_SPANISH_RENDERINGS` | %d | n/a | Wrong Spanish -> the English "
      "required instead. The 'Exclusions' half of a Microsoft-style termbase. |"
      % len(forb))
    w("")
    w("| Artifact | Count |")
    w("|---|---:|")
    w("| Termbase entries (with cross-family overlap) | %d |"
      % sum(len(v) for v in tb.values()))
    w("| Distinct terms after de-duplication | %d |"
      % len({t for v in tb.values() for t in v}))
    w("| Spanish carrier terms mapped to English hints (`lexicon_es`) | %d |" % len(lex))
    w("| Distinct canonical hints those map onto | %d |"
      % len({h for v in lex.values() for h in v}))
    w("| GUI strings catalogued (`ui_es`) | %d |" % len(ui))
    w("| ... rendered into Spanish | %d |" % sum(1 for k, v in ui.items() if k != v))
    w("| ... deliberately kept identical (they ARE terms) | %d |"
      % sum(1 for k, v in ui.items() if k == v))
    if rows:
        w("| Reviewable rows in `terms.csv` | %d |" % len(rows))
    w("")

    # ------------------------------------------------------------- terms.csv
    if rows:
        by_policy = {}
        for r in rows:
            by_policy.setdefault(r.get("policy", "?"), []).append(r)
        w("## `terms.csv` — the reviewable source of truth")
        w("")
        w("The Python families above are what the runtime imports; `terms.csv` is "
          "the same inventory in a form a human translator can review, diff and "
          "argue with in a pull request. Each row carries a **policy**:")
        w("")
        w("| Policy | N | Meaning |")
        w("|---|---:|---|")
        meaning = {
            "KEEP": "stays English — translating it would break *biunivocidad*",
            "TRANSLATE": "has an exact everyday Spanish equivalent, so it moves",
            "ASSET": "an agent / product name — byte-exact, case and hyphens are functional",
            "MACHINE": "a protocol literal the machine reads back — translating it breaks parsing",
        }
        for pol in ("KEEP", "TRANSLATE", "ASSET", "MACHINE"):
            if pol in by_policy:
                w("| `%s` | %d | %s |" % (pol, len(by_policy[pol]), meaning.get(pol, "")))
        other = [p for p in by_policy if p not in meaning]
        for pol in sorted(other):
            w("| `%s` | %d | |" % (pol, len(by_policy[pol])))
        w("")
        translate = sorted(by_policy.get("TRANSLATE", []),
                           key=lambda r: r.get("english", "").lower())
        if translate:
            w("### Every `TRANSLATE` row (%d)" % len(translate))
            w("")
            w("These are the only terms in the whole inventory that change "
              "language. Everything else is KEEP, ASSET or MACHINE.")
            w("")
            w("| English | Spanish | Domain |")
            w("|---|---|---|")
            for r in translate:
                w("| `%s` | **%s** | %s |" % (r.get("english", ""),
                                              r.get("spanish", ""),
                                              r.get("domain", "")))
            w("")

    # ---------------------------------------------------------- per family
    w("## Families that never move")
    w("")
    for fam in FAMILY_ORDER:
        terms = tb.get(fam, [])
        if not terms:
            continue
        w("### `%s` — %d terms" % (fam, len(terms)))
        w("")
        w(PURPOSE.get(fam, ""))
        w("")
        dual = [t for t in terms if t.lower() in sp_low]
        for i in range(0, len(terms), 6):
            w("- " + " · ".join("`%s`" % t for t in terms[i:i + 6]))
        if dual:
            w("")
            w("> **Contradiction:** %s also appear%s in `SPANISH_PREFERRED`. "
              "Runtime resolves this correctly (the Spanish rendering wins, because "
              "`dnt.py` subtracts `SPANISH_PREFERRED` from both the strict and the "
              "loose sets), but the file asserts two things at once."
              % (", ".join("`%s`" % t for t in dual), "" if len(dual) > 1 else "s"))
        w("")

    # ------------------------------------------------------ spanish preferred
    w("## `SPANISH_PREFERRED` — the %d terms that DO become Spanish" % len(sp))
    w("")
    w("| English | Spanish | Why it is safe |")
    w("|---|---|---|")
    for k in sorted(sp):
        w("| `%s` | **%s** | %s |" % (k, sp[k], WHY.get(k, "everyday equivalent exists")))
    w("")

    # ------------------------------------------------------------- forbidden
    w("## `FORBIDDEN_SPANISH_RENDERINGS` — the %d mistranslations the build rejects"
      % len(forb))
    w("")
    w("These are the words a careless translator reaches for. Each one breaks "
      "*biunivocidad*: the Spanish either names a different thing, or names "
      "nothing at all.")
    w("")
    w("| Never write | Required instead |")
    w("|---|---|")
    for k in sorted(forb):
        w("| *%s* | **%s** |" % (k, forb[k]))
    w("")

    # --------------------------------------------------------------- lexicon
    w("## `lexicon_es` — %d Spanish CARRIER terms mapped to English hints" % len(lex))
    w("")
    w("This is a different mechanism and must not be confused with the termbase. "
      "It never renames anything and is never shown to a user: it lifts a Spanish "
      "**request** into the canonical English key space the capability scorer "
      "already understands, so *\"borra los archivos\"* scores like *\"delete the "
      "files\"*. Every value already exists in the registry's own hint corpus - "
      "nothing is invented.")
    w("")
    w("Note the consequence of the register: a sentence like *\"haciendo un Pod en "
      "Dockerer\"* needs **no** entry here at all, because its technical nouns are "
      "already English and hit the hints directly. What this table covers is the "
      "Spanish carrier - the verbs and connectives.")
    w("")
    w("| Spanish | -> canonical English hints |")
    w("|---|---|")
    for k in sorted(lex):
        w("| `%s` | %s |" % (k, ", ".join("`%s`" % h for h in lex[k])))
    w("")

    # ---------------------------------------------------------- ui identical
    identical = sorted([k for k, v in ui.items() if k == v])
    w("## GUI strings deliberately kept identical (%d of %d)" % (len(identical), len(ui)))
    w("")
    w("Where the Spanish equals the English, it is because the string **is** a "
      "term - not because it was skipped. The test "
      "`test_intentional_identities_are_product_terms` fails the build if an "
      "identity cannot be justified by a do-not-translate term.")
    w("")
    for i in range(0, len(identical), 4):
        w("- " + " · ".join("`%s`" % t for t in identical[i:i + 4]))
    w("")

    # ------------------------------------------------------ stage 0 (caps)
    w("## Stage 0 — the per-model capability gate")
    w("")
    w("Everything above assumes the model on the other end can actually hold "
      "Spanish. `agent/i18n/model_caps.py` is the gate that decides whether to "
      "trust it, and it sits BEFORE the N1/N2/N3 pipeline:")
    w("")
    w("| Tier | What it means | Effect on this termbase |")
    w("|---|---|---|")
    w("| `FLUENT` | the model handles Spanish and the register | the user's own "
      "words pass through untouched — no English hint expansion |")
    w("| `ASSIST` | partial competence | the carrier terms from `lexicon_es` are "
      "expanded into English hints so the capability scorer still routes correctly |")
    w("| `WEAK` | cannot be trusted with Spanish | full expansion |")
    w("| `UNKNOWN` | not measured yet | treated as `ASSIST` — the recoverable "
      "direction |")
    w("")
    w("Three properties matter for terminology work, and each is test-pinned:")
    w("")
    w("- **Identity is the model, not the family.** A local model is keyed by its "
      "GGUF sha256, a cloud model by its exact id (`:cloud` suffix preserved), so "
      "two builds of \"the same\" model are never confused for one another.")
    w("- **The seed can never demote.** A prior belief may only say `FLUENT` or "
      "`UNKNOWN`; only a measured probe or observed failures can lower a model.")
    w("- **Observation demotes, never promotes.** Passive verification watches "
      "real answers and can drop a model a tier, but earning a tier requires the "
      "graded probe.")
    w("")
    w("Tokenizer *fertility* was measured as a competence signal and **rejected** "
      "— it tracks tokenizer design, not language ability. `model_caps.py` is "
      "asserted to contain no fertility heuristic.")
    w("")

    # ------------------------------------------------------------ enforcement
    w("## How this is enforced")
    w("")
    w("| Mechanism | File | What it guarantees |")
    w("|---|---|---|")
    w("| DNT invariant | `agent/test_ui_dnt.py` | Every do-not-translate term "
      "present in an English GUI string is present, byte-identical, in its Spanish "
      "rendering. |")
    w("| Case enforcement | same | An asset name that survives in the WRONG case "
      "(`Stm32er` for `STM32er`) fails, which a case-insensitive reader would miss. |")
    w("| Angela's credit line | same | Angela López Mendoza's credit maps to "
      "itself, asserted explicitly rather than by omission. |")
    w("| Harvest, never transcribe | `agent/i18n/dnt.py` | The asset names are "
      "read at runtime from the registries that define them, so a second "
      "hand-maintained copy cannot rot. |")
    w("| Checker is not vacuous | `agent/test_ui_dnt.py` | Separate tests prove "
      "the checker DOES reject a renamed asset and an over-translated term. |")
    w("| Capability gate | `agent/test_model_caps.py` | Identity keying, "
      "seed-cannot-demote, observe-cannot-promote, fail-open, and the absence of "
      "any fertility heuristic. |")
    w("| This document | `generate_terminology.py` | Regenerated from the live "
      "modules; `--check` fails when the committed copy is stale. |")
    w("")
    w("---")
    w("")
    w("*Generated by `docs/research/spanish-localization/generate_terminology.py` "
      "from the live `agent/i18n/` files. Regenerate rather than edit by hand.*")

    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", action="append", default=None,
                    help="destination path (repeatable). Default: both trees.")
    ap.add_argument("--check", action="store_true",
                    help="verify only; exit 1 if a destination is stale")
    args = ap.parse_args()

    body = build_markdown()
    outs = args.out if args.out else [p for p in _DEFAULT_OUTS
                                      if os.path.isdir(os.path.dirname(p))]
    # de-duplicate while preserving order (both defaults can resolve to one path)
    seen, targets = set(), []
    for p in outs:
        key = os.path.normcase(os.path.abspath(p))
        if key not in seen:
            seen.add(key)
            targets.append(p)

    if not targets:
        print("No destination directory exists; nothing written.")
        return 1

    stale = 0
    for path in targets:
        if args.check:
            current = ""
            if os.path.exists(path):
                with io.open(path, encoding="utf-8") as fh:
                    current = fh.read()
            if current != body:
                stale += 1
                print("STALE  %s" % path)
            else:
                print("ok     %s" % path)
            continue
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        print("WROTE  %s  (%d bytes, %d lines)"
              % (path, len(body), body.count("\n")))

    if args.check and stale:
        print("\n%d file(s) stale — run without --check to regenerate." % stale)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
