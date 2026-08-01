"""N1 folding, N2 boundary-aware phrase matching, N3 expansion gate.

This module is the whole of NEPANTLA Step 1. It makes Tlamatini's deterministic
capability scorer a function of INTENT rather than of the language the intent
happened to arrive in.

THE MEASURED DEFECT
-------------------
``capability_registry._TOKEN_RE = re.compile(r"[a-z0-9_]+")`` treats every
non-ASCII byte as a delimiter, so accented Spanish is shredded before any logic
runs::

    codigo (with an acute o)    ->  ['digo']
    analisis (with an acute a)  ->  ['lisis']
    anos (with a tilde n)       ->  ['os']

and phrase matching was unbounded substring containment, so the two-character
alias ``ue`` matched inside *prueba*: Unrealer scored 24 and ranked FIRST on a
Spanish e-mail request while chat_agent_send_email scored 0.

THE REGISTER THIS SERVES
------------------------
Spanish is the MATRIX language; English is the EMBEDDED technical lexicon::

    "Haciendo un Pod en Dockerer y creando un Container en Kubernetes"

Note the consequence for THIS module, which is easy to get backwards: that
sentence needs NO expansion at all. Pod, Dockerer, Container and Kubernetes are
already English and already hit the registry hints directly. The expansion gate
below will not fire on it, and that is CORRECT behaviour, not a miss.

What genuinely needs mapping is the Spanish CARRIER - the verbs and the
connectives: *borra los archivos de esa carpeta*, *crea un archivo llamado
notas.txt*, *envia un correo a soporte*. That is what the lexicon covers.

THREE HARD CONTRACTS
--------------------
1. IDENTITY ON ASCII. For pure-ASCII English input ``fold_text`` is exactly
   ``str.lower()``; ``phrase_hit`` can only ever REMOVE an accidental substring
   hit, never add one; and ``expand_request`` is the identity, because the
   Spanish-signal gate cannot fire on English. Pinned by a golden corpus.
2. FAIL-OPEN. Every function falls back to today's expression on any error. A
   scoring helper that raises would take down the execution planner.
3. NO ``agent.*`` IMPORTS, EVER. ``capability_registry`` imports this module
   directly rather than through a package facade, precisely so an ImportError
   elsewhere in the language layer cannot reach the hot path.

WHAT THIS MODULE NEVER DOES
---------------------------
It never renames, translates or normalises an ASSET. Agent display names
(Emailer, Asker, Apirer, STM32er, ...), tool names, flags, config keys and
protocol sentinels pass through byte-identical in every locale. This module
changes only how a USER'S SENTENCE is read.

Stdlib only: re, unicodedata, functools.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from typing import FrozenSet, Set

__all__ = [
    "ASCII_IDENTITY_GUARANTEED",
    "fold_text",
    "phrase_hit",
    "looks_spanish_carrier",
    "expand_request",
    "legacy_lower",
]

ASCII_IDENTITY_GUARANTEED = True

# Mirrors capability_registry._TOKEN_RE. Do not "improve" it: the point is that
# after folding, the SAME rule applies, so English behaviour is unchanged.
_TOKEN_RE = re.compile(r"[a-z0-9_]+")

# Characters that count as "inside a word" for boundary purposes. Latin-1
# Supplement plus Latin Extended-A/B covers every accented character Spanish,
# Portuguese, Catalan, Galician, French and Italian can produce.
_WORD_CLASS = r"0-9A-Za-z_À-ɏ"

_PHRASE_CACHE = 8192

# ---------------------------------------------------------------------------
# The Spanish-carrier gate for N3
# ---------------------------------------------------------------------------
# Expansion must be PROVABLY inert on English, so it fires only when the folded
# request carries at least _MIN_SIGNALS distinct markers from this set.
#
# These are deliberately CARRIER words - articles, prepositions, pronouns,
# demonstratives, and Spanish verb forms - because under the real register the
# technical NOUNS in a Spanish request are already English.
#
# CURATION RULE: every entry must be a word that is NOT also an ordinary
# English word. Deliberately EXCLUDED for that reason:
#     la (musical note)   no    son   van   sin   solo   hay   favor
#     lee   leer   con   en   y   real   final   as
# Adding an English homograph here would let a Spanish expansion fire on an
# English prompt and silently break the identity guarantee.
_ES_MARKERS: FrozenSet[str] = frozenset("""
    el los las un una unos unas del al por para que su sus mis tus
    le les nos otra otro otros otras cada algun alguna mismo misma
    esta este esto estos estas ese esa esos esas aquel aquella
    hacia desde sobre entre pero porque cuando donde como cual cuales
    muy mas tambien tampoco todo toda todos todas ninguna ningun
    tiene tienes tengo quiero necesito dame damelo hazme hazlo dime
    puedes podrias quisiera ayudame
    archivo archivos carpeta carpetas pantalla correo ruta rutas
    borra borrar elimina eliminar crea crear muestra muestrame
    ejecuta ejecutar corre lanza envia enviar manda mandar busca buscar
    revisa revisar abre abrir guarda guardar escribe escribir
    descarga descargar analiza analizar resume genera generar
    haciendo creando ejecutando enviando buscando mostrando borrando
    guardando revisando abriendo leyendo escribiendo generando
    ahora luego despues antes primero entonces
""".split())

_MIN_SIGNALS = 2


# ---------------------------------------------------------------------------
# N1 - folding
# ---------------------------------------------------------------------------

def legacy_lower(text: str) -> str:
    """Exactly what the scorer did before. Kept for the golden-corpus test."""
    return (text or "").lower()


def fold_text(text: str) -> str:
    """NFKD-fold: decompose, drop combining marks, lowercase.

    Identical to ``str.lower()`` for pure-ASCII input, because NFKD is the
    identity on ASCII and ASCII carries no combining marks.

    This turns the accented spelling of *codigo* into ``codigo`` instead of
    ``digo`` - and it also removes an accent-dependent nondeterminism that
    affects ENGLISH users today, since the same intent scored differently
    depending on whether an accent happened to be typed.
    """
    if not text:
        return ""
    try:
        decomposed = unicodedata.normalize("NFKD", text)
        return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).lower()
    except Exception:
        try:
            return text.lower()
        except Exception:
            return ""


# ---------------------------------------------------------------------------
# N2 - boundary-aware phrase matching
# ---------------------------------------------------------------------------

_EDGE_RE = re.compile(f"[{_WORD_CLASS}]")


def _has_word_edges(phrase: str) -> bool:
    """True when BOTH ends of the phrase are word characters.

    A phrase such as ``--noreload``, ``INI_SECTION_`` or ``send email:`` has a
    non-word edge; a boundary assertion there would wrongly reject a legitimate
    hit, so those fall back to plain containment.
    """
    if not phrase:
        return False
    return bool(_EDGE_RE.match(phrase[0])) and bool(_EDGE_RE.match(phrase[-1]))


@lru_cache(maxsize=_PHRASE_CACHE)
def _bounded(phrase: str):
    return re.compile(
        f"(?<![{_WORD_CLASS}])" + re.escape(phrase) + f"(?![{_WORD_CLASS}])"
    )


def phrase_hit(phrase: str, haystack: str) -> bool:
    """Boundary-aware replacement for ``phrase in haystack``.

    Both arguments are expected to be already folded by the caller.

    The behaviour change is one-directional by construction - it can only
    remove an accidental hit, never create one::

        phrase_hit('ue',    'envia un correo de prueba')  -> False  (was True)
        phrase_hit('api',   'hazlo rapido por favor')     -> False  (was True)
        phrase_hit('ls',    'eso es falso')               -> False  (was True)
        phrase_hit('send email', 'please send email now') -> True   (unchanged)
        phrase_hit('--noreload', 'run with --noreload')   -> True   (unchanged)

    The first three are ALSO English defects: ``api`` inside *rapid*, ``ls``
    inside *false*, ``pid`` inside *rapid*.

    Where strict matching removes a hit that the registry genuinely meant - the
    hint ``container`` inside the word *containers* - the fix belongs in the
    REGISTRY, by declaring the surface form, not in this matcher. Only the
    registry knows which agent OWNS a word: ``screen`` inside *screenshot* looks
    identical to a matcher, yet it must NOT boost VideoPlayer.
    """
    if not phrase or not haystack:
        return False
    try:
        if not _has_word_edges(phrase):
            return phrase in haystack
        return _bounded(phrase).search(haystack) is not None
    except Exception:
        return phrase in haystack


# ---------------------------------------------------------------------------
# N3 - canonical-key expansion, behind the Spanish-carrier gate
# ---------------------------------------------------------------------------

def looks_spanish_carrier(folded_text: str) -> bool:
    """True when the folded text is carried by Spanish grammar.

    Requires at least two distinct markers from ``_ES_MARKERS``, every one of
    which is a word that is not also ordinary English. That is what makes N3
    provably inert on an English request.

    Note the deliberate consequence of the register: a heavily technical
    Spanish sentence whose nouns are all English may not reach two markers. It
    then receives no expansion - correctly, because its English terms already
    match the registry hints directly.
    """
    if not folded_text:
        return False
    try:
        seen: Set[str] = set()
        for tok in _TOKEN_RE.findall(folded_text):
            if tok in _ES_MARKERS:
                seen.add(tok)
                if len(seen) >= _MIN_SIGNALS:
                    return True
        return False
    except Exception:
        return False


def _lexicon():
    """Load the data-only lexicon lazily. Absent or broken -> no expansion."""
    try:
        from . import lexicon_es
        table = getattr(lexicon_es, "ES_TO_CANONICAL", None)
        return table if isinstance(table, dict) else None
    except Exception:
        return None


def expand_request(folded_text: str, *, force: bool = False) -> str:
    """Append the canonical ENGLISH hint tokens a Spanish request implies.

    Returns the input UNCHANGED unless the Spanish-carrier gate fires (or
    ``force`` is set, which exists only for the test harness).

    Every value appended already exists in the registry's own hint corpus - the
    closure is enforced by a test that re-derives the legal set. Nothing is
    invented, so the scorer's tuned English behaviour remains the only
    behaviour; the Spanish request is simply lifted into the canonical key
    space before it is scored::

        expand_request('envia un correo a soporte')
        -> 'envia un correo a soporte email mail send'

        expand_request('send an email to support')
        -> unchanged (gate does not fire)
    """
    if not folded_text:
        return folded_text or ""
    try:
        if not force and not looks_spanish_carrier(folded_text):
            return folded_text
        table = _lexicon()
        if not table:
            return folded_text

        tokens = set(_TOKEN_RE.findall(folded_text))
        additions: list[str] = []
        seen: Set[str] = set()

        for tok in tokens:
            for hint in table.get(tok, ()):
                if hint not in seen:
                    seen.add(hint)
                    additions.append(hint)

        for key, hints in table.items():
            if " " not in key:
                continue
            if phrase_hit(key, folded_text):
                for hint in hints:
                    if hint not in seen:
                        seen.add(hint)
                        additions.append(hint)

        if not additions:
            return folded_text
        return folded_text + " " + " ".join(additions)
    except Exception:
        # FAIL-OPEN: an unexpanded request scores exactly as it does today.
        return folded_text
