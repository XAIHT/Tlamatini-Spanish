"""The DO-NOT-TRANSLATE inventory, and the checker that enforces it.

WHAT THIS IS FOR
----------------
Tlamatini's Spanish GUI follows the register its users actually speak: Spanish
supplies the grammar, English supplies the technical vocabulary.

    "Envia un email por SMTP cuando se detecta un pattern en el log."
    "Haciendo un Pod en Dockerer y creando un Container en Kubernetes."

Not *correo*, not *patron*, not *registro*, not *vaina*. Translating those reads
as foreign to the very audience the translation is for - and in the case of an
ASSET NAME it is worse than foreign, it is WRONG: ``Emailer`` is the name of a
thing in this system, and a GUI that calls it *Correero* is describing software
that does not exist.

So the localization has three strata, and only one of them moves:

    1. MACHINE SURFACE   never moves. Identifiers, tool names, argument keys,
                         config keys, CLI flags, INI_SECTION_* sentinels, CSS
                         classes, log lines. Not visible to the user as prose.
    2. TECHNICAL LEXICON never moves, but IS visible. Asset names (Emailer,
                         STM32er, Kyber-KeyGen), product terms (MCP, ACPX,
                         Wizard, Multi-Turn), and the ordinary English technical
                         nouns a Spanish-speaking developer already uses
                         (log, commit, push, Pod, Container, deployment,
                         screenshot, firmware, browser, timeout).
    3. CARRIER           moves. Articles, prepositions, connectives, generic
                         verbs, and the explanatory prose around strata 1 and 2.

This module is the machine-readable definition of strata 1 and 2, plus
``missing_terms``, which mechanically verifies that a Spanish string preserved
every do-not-translate term its English source contained.

WHY THE NAMES ARE HARVESTED, NOT TYPED
--------------------------------------
Every asset name here is read AT RUNTIME out of the registries that already
define it. Hand-copying 64 display names into a second list would create a
second source of truth that silently rots - and Tlamatini's naming rules are
unforgiving about exactly that: ``STM32er`` is not ``STM32Er``, ``PDFer`` is not
``Pdfer``, ``Kyber-KeyGen`` is not ``Kyber KeyGen`` (the hyphen is functional -
the canvas connection handler compares the hyphenated literal, so a spaced name
silently never saves the connection). A harvested list cannot drift.

Only the terms that no registry knows about - product vocabulary and the shared
English technical lexicon - are authored by hand below.

FAIL-OPEN
---------
Harvesting degrades to the hand-authored core if the registries cannot be
imported (a pool subprocess, a partially-initialised Django). A DNT check that
raises would be worse than one that under-reports.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import FrozenSet, Iterable, List, Tuple

__all__ = [
    "PRODUCT_TERMS",
    "TECH_LEXICON",
    "MACHINE_SENTINELS",
    "agent_display_names",
    "tool_names",
    "dnt_terms",
    "term_present",
    "term_preserved",
    "missing_terms",
]


# ---------------------------------------------------------------------------
# Stratum 2a - product vocabulary. Tlamatini's own nouns.
# ---------------------------------------------------------------------------
PRODUCT_TERMS: Tuple[str, ...] = (
    "Tlamatini",
    "ACPX", "ACPXer", "ACP", "MCP", "MCPs",
    # Angela's NAME, in every spelling that may appear. It is the one
    # term in this file that is not a product noun - it is a person, and
    # the author banner forbids it EVER being dropped or altered.
    "Ángela López Mendoza", "Angela López Mendoza", "López Mendoza",
    # NOT product terms any more (Angela, 2026-07-28): she ordered these
    # translated in the GUI - External->Externos, External MCPs->MCPs
    # Externos, Config->Configuración, Admin->Administración,
    # Catalog of Prompts->Catálogo de prompts.
    # (Step-by-Step SALIO de esta lista el 2026-08-08: Angela lo devolvio al
    # ingles junto con los otros tres toggles de la toolbar, y ahora vive
    # abajo en PRODUCT_TERMS. Ver el comentario de esa fila.)
    # GUI column headers and control labels kept in English per
    # Angela's register rule (2026-07-28): American technical terms
    # and collocations stay English inside Spanish grammar.
    "Access aimed",
    "DB",
    "Email",
    "Service",
    "Status",
    "Telegram",
    "Unified",
    "WhatsApp",
    # Config dialog labels. These name MODELS and TRANSPORTS, which are
    # American technical terms, so they stay English (Angela, 2026-07-28).
    "Transport", "Embedding", "Chained", "Summarizer",
    "Image interpreter 1", "Image interpreter 2", "Image merger",
    # The two built-in MCP context providers, by name.
    "System-Metrics", "Files-Search",
    # Los cuatro toggles de la toolbar del chat. Angela (2026-08-08):
    # "all the buttons/checkboxes with Multi-turn, Step-by-Step, Exec report,
    # ACPX must stay in English". Van juntos a proposito: son UNA sola fila de
    # controles y traducir uno solo se ve peor que no traducir ninguno.
    "Multi-Turn", "Exec Report", "Ask Execs", "Step-by-Step",
    "Skill", "Skills", "SKILL.md",
    "Flow", "Flows", ".flw", "FlowCreator", "FlowHypervisor", "FlowBacker",
    "Canvas", "Starter", "Ender", "Stopper", "Cleaner", "Parametrizer",
    "Agentic Control Panel", "Flow Control Panel",
    "Wizard", "Access Keys Wizard",
    "RAG", "FAISS", "BM25", "LLM", "Ollama", "Anthropic", "Claude",
    # Kept abbreviations. A Spanish speaker says "la DB" and "el SQL"
    # exactly as written; expanding them would be stranger, not clearer.
    "DB", "SQL", "IP", "URI", "Uri",
    "Create Flow", "Agent", "Agents", "Tool", "Tools",
    # NOT here, on purpose: "Context" and "About" are ordinary menu words,
    # not names of anything. "Contexto" and "Acerca de" are correct.
)


# ---------------------------------------------------------------------------
# Stratum 2b - the shared English technical lexicon.
#
# CURATION RULE: a term belongs here when a Spanish-speaking developer says the
# ENGLISH word out loud. That is an empirical question about usage, not a
# stylistic preference, and the test is simple - would translating it make a
# colleague pause? "Haz un commit" is natural; "haz una confirmacion" is not.
#
# Terms deliberately NOT listed, because Spanish genuinely owns them and a
# developer really does say them in Spanish: archivo, carpeta, pantalla,
# usuario, contrasena, fecha, ayuda, buscar, guardar, borrar, enviar.
# ---------------------------------------------------------------------------
TECH_LEXICON: Tuple[str, ...] = (
    # version control
    "commit", "commits", "push", "pull", "merge", "branch", "branches",
    "repo", "repos", "repository", "checkout", "rebase", "diff", "tag",
    # build / run
    "build", "builds", "deploy", "deployment", "deployments", "release",
    "script", "scripts", "shell", "batch",
    "pipeline", "job", "jobs", "workflow", "rollback",
    # containers / infra
    "Pod", "Pods", "Container", "Containers", "cluster", "namespace",
    "Docker", "Kubernetes", "kubectl",
    "host", "server", "servers", "endpoint", "endpoints", "cloud",
    # "image" / "volume" are DELIBERATELY absent: a Docker image and a
    # picture are the same English word, and "imagen" / "volumen" are what
    # a Spanish speaker says for the non-Docker sense. Enforcing them
    # would force wrong Spanish in the Voice and image-paste strings.
    "LPAR", "backup", "backups",
    # data / protocol
    "log", "logs", "token", "tokens", "prompt", "prompts", "request",
    "response", "payload", "header", "headers", "query", "queries",
    "cache", "buffer", "thread", "threads", "timeout", "timeouts",
    "debug", "stack trace",
    # ALSO deliberately absent: path, output, input, status, command.
    # "ruta", "salida", "entrada", "estado" and "comando" are ordinary
    # Spanish that developers use without hesitation.
    "API", "REST", "JSON", "YAML", "HTTP", "HTTPS", "SMTP", "IMAP",
    "SSH", "SCP", "URL", "URLs", "SQL", "CSV", "PDF", "ZIP",
    # desktop / media
    "screenshot", "screenshots", "desktop", "browser", "webcam",
    "mouse", "click", "scroll", "hardware", "driver", "drivers",
    "firmware", "socket", "sockets", "baud",
    # "port" is absent: "puerto" is completely natural Spanish.
    "mp3", "mp4", "WAV", "stream", "streaming",
    # product-adjacent
    "chat", "checkbox", "dashboard", "wizard", "plugin", "plugins",
    "software", "hardware", "backend", "frontend", "framework",
)


# ---------------------------------------------------------------------------
# Stratum 1 - machine sentinels. These appear in prose only when the GUI is
# telling the user about a literal the machine will read back.
# ---------------------------------------------------------------------------
MACHINE_SENTINELS: Tuple[str, ...] = (
    "INI_SECTION_", "END_SECTION_", "END-RESPONSE",
    "BEGIN-CODE", "END-CODE", "TLM_VERDICT::",
    "config.yaml", "config.json", "tlamatini.log", "data.keys",
    "prompt.pmt", "SKILL.md", "requirements.txt",
    "--noreload", "--self-modify", "runserver", "startserver",
)


def _safe(iterable) -> List[str]:
    out: List[str] = []
    try:
        for value in iterable:
            text = str(value or "").strip()
            if text:
                out.append(text)
    except Exception:
        pass
    return out


@lru_cache(maxsize=1)
def agent_display_names() -> Tuple[str, ...]:
    """Every wrapped agent's display name, HARVESTED from the registry.

    Never hand-typed: these are the names Tlamatini's own naming rules protect
    byte-for-byte (``STM32er``, ``PDFer``, ``SQLer``, ``Kyber-KeyGen``,
    ``De-Compresser``, ``Monitor-Log``), and a second hand-maintained copy would
    be a mis-casing waiting to happen.
    """
    names: List[str] = []
    try:
        from ..chat_agent_registry import WRAPPED_CHAT_AGENT_SPECS

        names.extend(_safe(spec.display_name for spec in WRAPPED_CHAT_AGENT_SPECS))
    except Exception:
        pass
    try:
        from ..services.agent_paths import display_name_from_agent_type

        # The boot resolver's override map is the real source of truth for a
        # display name, so pull anything it knows that the specs did not carry.
        for agent_type in list(dict.fromkeys(
                n.lower().replace(" ", "_").replace("-", "_") for n in names)):
            resolved = display_name_from_agent_type(agent_type)
            if resolved:
                names.append(str(resolved))
    except Exception:
        pass
    return tuple(sorted(set(names), key=lambda s: (-len(s), s)))


@lru_cache(maxsize=1)
def tool_names() -> Tuple[str, ...]:
    """Every wrapped tool name (``chat_agent_*``) plus the direct @tool names."""
    names: List[str] = []
    try:
        from ..chat_agent_registry import WRAPPED_CHAT_AGENT_SPECS

        names.extend(_safe(spec.tool_name for spec in WRAPPED_CHAT_AGENT_SPECS))
        names.extend(_safe(spec.tool_description for spec in WRAPPED_CHAT_AGENT_SPECS))
    except Exception:
        pass
    return tuple(sorted(set(names), key=lambda s: (-len(s), s)))


@lru_cache(maxsize=1)
def dnt_terms() -> FrozenSet[str]:
    """The complete do-not-translate set.

    Harvested asset names, plus the hand-authored product and technical
    vocabulary, plus anything an optional ``termbase_en`` module contributes.
    """
    terms: List[str] = []
    terms.extend(agent_display_names())
    terms.extend(tool_names())
    terms.extend(PRODUCT_TERMS)
    terms.extend(TECH_LEXICON)
    terms.extend(MACHINE_SENTINELS)
    try:
        from . import termbase_en

        for attr in dir(termbase_en):
            if attr.startswith("_"):
                continue
            value = getattr(termbase_en, attr)
            if isinstance(value, (tuple, list, set, frozenset)):
                terms.extend(_safe(value))
    except Exception:
        pass
    return frozenset(t for t in terms if t)


# ---------------------------------------------------------------------------
# The checker
# ---------------------------------------------------------------------------

_WORDISH = r"0-9A-Za-z_"


@lru_cache(maxsize=4096)
def _term_re(term: str):
    """Case-SENSITIVE, boundary-aware pattern for one term.

    Case sensitivity is the point: ``STM32er`` and ``Stm32er`` are not the same
    asset, and a check that folded case would wave the wrong one through.

    Boundaries are applied only where the term's own edges are word characters -
    ``.flw``, ``--noreload`` and ``INI_SECTION_`` must still match.
    """
    left = "(?<![%s])" % _WORDISH if re.match("[%s]" % _WORDISH, term[0]) else ""
    right = "(?![%s])" % _WORDISH if re.match("[%s]" % _WORDISH, term[-1]) else ""
    return re.compile(left + re.escape(term) + right)


def term_present(term: str, text: str) -> bool:
    """Is ``term`` present in ``text``, byte-identical and at a word boundary?"""
    if not term or not text:
        return False
    try:
        return _term_re(term).search(text) is not None
    except Exception:
        return term in text


def term_preserved(term: str, text: str) -> bool:
    """Like ``term_present``, but accepts the term's own ENGLISH plural.

    Used ONLY by the localization checker, never by the request scorer, so it
    does not touch the strict-boundary rule the scorer relies on.

    It exists because a Spanish sentence often pluralises the English term it
    borrows: "MCP catalog" becomes "Catalogo de MCPs". The term was preserved -
    the sentence simply needed the plural. Refusing that would push the
    translator toward worse Spanish for no gain in fidelity.
    """
    if term_present(term, text):
        return True
    for suffix in ("s", "es"):
        if term_present(term + suffix, text):
            return True
    return False


@lru_cache(maxsize=1)
def _case_sensitive_terms() -> FrozenSet[str]:
    """Terms whose CASE is part of their identity.

    Asset names, tool names, product terms and machine sentinels. ``STM32er``
    is not ``Stm32er``; ``PDFer`` is not ``Pdfer``; ``ACPX`` is not ``acpx``.
    A check that folded case here would wave the wrong asset through.
    """
    terms = set(agent_display_names()) | set(tool_names())
    terms |= set(PRODUCT_TERMS) | set(MACHINE_SENTINELS)
    for attr in ("AGENT_DISPLAY_NAMES", "TOOL_NAMES",
                 "PRODUCT_TERMS", "MACHINE_SENTINELS"):
        terms.update(_termbase_tuple(attr))
    # A term the termbase itself marks as better rendered in Spanish is not a
    # do-not-translate term, whatever list it also appears in.
    terms -= _spanish_preferred()
    return frozenset(t for t in terms if t)


def _termbase_tuple(attr: str) -> set:
    """One named tuple from the optional termbase. Absent -> empty."""
    try:
        from . import termbase_en

        value = getattr(termbase_en, attr, None)
        if isinstance(value, (tuple, list, set, frozenset)):
            return set(_safe(value))
    except Exception:
        pass
    return set()


@lru_cache(maxsize=1)
def _spanish_preferred() -> FrozenSet[str]:
    """Terms the termbase says SHOULD be rendered in Spanish.

    The exclusion that keeps the checker honest: "Contexto", "Puerto" and
    "Visor del log" are correct Spanish, and a checker that demanded the
    English word back would be forcing bad localization in the name of
    fidelity. Accepts either a dict (term -> preferred Spanish) or a plain
    collection of terms.
    """
    try:
        from . import termbase_en

        value = getattr(termbase_en, "SPANISH_PREFERRED", None)
        if isinstance(value, dict):
            return frozenset(_safe(value.keys()))
        if isinstance(value, (tuple, list, set, frozenset)):
            return frozenset(_safe(value))
    except Exception:
        pass
    return frozenset()


@lru_cache(maxsize=1)
def _loose_lexicon() -> FrozenSet[str]:
    """The case-INSENSITIVE generic technical vocabulary, folded to lowercase.

    Mine, plus every TECH_* family the termbase contributes. These are words,
    not names, so their capitalisation carries no meaning.
    """
    terms = {t.lower() for t in TECH_LEXICON}
    try:
        from . import termbase_en

        for attr in dir(termbase_en):
            if not attr.startswith("TECH"):
                continue
            value = getattr(termbase_en, attr)
            if isinstance(value, (tuple, list, set, frozenset)):
                terms.update(t.lower() for t in _safe(value))
    except Exception:
        pass
    terms -= {t.lower() for t in _spanish_preferred()}
    return frozenset(t for t in terms if t)


def missing_terms(english: str, spanish: str,
                  extra: Iterable[str] = ()) -> Tuple[str, ...]:
    """Which do-not-translate terms did the Spanish string DROP?

    For every DNT term that appears in the English source, the same term must
    appear in the Spanish target. Anything returned here is a localization
    DEFECT: either an asset was renamed, or a technical term was over-translated.

    TWO CASE REGIMES, deliberately:

    * ASSET / PRODUCT / SENTINEL terms are matched CASE-SENSITIVELY, in both
      directions. Their case is part of their identity.
    * The GENERIC TECHNICAL LEXICON is matched case-INSENSITIVELY, because a
      sentence legitimately capitalises its first word: "Shell to be executed"
      may become "Shell donde se va a ejecutar", and *shell* survived. What
      matters is that the WORD survived, not its capitalisation.

    Returns an empty tuple when the string is clean, so a lint can assert
    falsiness and print the tuple on failure.
    """
    if not english:
        return ()
    try:
        strict = set(_case_sensitive_terms())
        strict.update(t for t in extra if t)
        loose = set(_loose_lexicon())

        missing = [term for term in strict
                   if term_present(term, english)
                   and not term_preserved(term, spanish)]

        en_low, es_low = english.lower(), spanish.lower()
        missing += [term for term in loose
                    if term_present(term, en_low)
                    and not term_preserved(term, es_low)]

        # Longest first: reporting "Instant Messaging Doctor" is more useful
        # than reporting the "Doctor" fragment inside it.
        return tuple(sorted(set(missing), key=lambda s: (-len(s), s)))
    except Exception:
        return ()
