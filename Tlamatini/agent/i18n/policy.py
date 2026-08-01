# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""
NEPANTLA channel policy — the one place that says what is translated.

Tlamatini's Spanish edition carries THREE distinct streams of text, and they
get THREE different policies. Before this module the three decisions lived in
different files, and two of them were invisible: nothing in the codebase stated
that the user's prompt and the model's answer are deliberately NOT translated.
An unwritten decision is indistinguishable from an oversight, and it survives
only until someone "helpfully" adds a translate() call to the answer path.

    ┌───────────────────────┬─────────────┬──────────────────────────────────┐
    │ CHANNEL               │ POLICY      │ WHY                              │
    ├───────────────────────┼─────────────┼──────────────────────────────────┤
    │ A. GUI chrome         │ TRANSLATED  │ Our own finite, authored strings │
    │    labels, buttons,   │             │ (ui_es.UI_ES). A closed set we   │
    │    menus, banners     │             │ wrote, reviewed and DNT-checked. │
    ├───────────────────────┼─────────────┼──────────────────────────────────┤
    │ B. The user's prompt  │ NEVER       │ Her words go to the model AS     │
    │                       │ TRANSLATED  │ WRITTEN. NEPANTLA N1/N2/N3 build │
    │                       │             │ a separate SCORING KEY for tool  │
    │                       │             │ selection; they never rewrite    │
    │                       │             │ what the model receives.         │
    ├───────────────────────┼─────────────┼──────────────────────────────────┤
    │ C. The model's answer │ NEVER       │ She answers in Spanish natively. │
    │                       │ TRANSLATED  │ See the four reasons below.      │
    └───────────────────────┴─────────────┴──────────────────────────────────┘

WHY CHANNEL C IS A DESIGN DECISION, NOT A MISSING FEATURE
    1. It would destroy the register. `container` would come back
       `contenedor`, `log` would come back `bitácora` — the exact renderings
       `FORBIDDEN_SPANISH_RENDERINGS` exists to reject. The termbase protects
       OUR strings; it cannot police a machine translator's output.
    2. It would corrupt machine surfaces. An answer carries `END-RESPONSE`,
       `BEGIN-CODE<<<file>>>`, `INI_SECTION_*`, HTML tables and the
       `<!--TLAMATINI_EXEC_REPORT_BOUNDARY-->` sentinel. A translator does not
       know which spans are protocol, and one rewritten sentinel breaks
       parsing downstream.
    3. It would make her untruthful. A translation layer can subtly alter a
       claim about what was executed. An Exec Report that says something other
       than what ran is worse than an answer in the wrong language.
    4. It is the paper's thesis. §4, "Why an Upstream Translation Stage Cannot
       Deliver the Guarantee": a translation stage bolted onto either end
       cannot preserve non-inferiority. The competence question is answered by
       measuring the MODEL (Stage 0, ``model_caps``), not by post-processing
       its words.

    The right lever when a model cannot hold Spanish is therefore Stage 0 —
    tier the model and expand the scoring key — NOT a back-translation stage.

THE IDENTITY FUNCTIONS ARE THE POINT
    ``carry_prompt`` and ``carry_answer`` return their input unchanged. They
    look like dead code and are not: they are the executable statement of a
    decision, they give the passthrough a name a test can pin, and they give
    any future "let's translate the answer" change one obvious place to argue
    with. Deleting them does not simplify anything — it removes the only
    evidence that the passthrough is intentional.

Coverage: ``agent/test_ui_runtime_layer.py``.
"""
from __future__ import annotations

from typing import Dict, List

__all__ = [
    "render_ui",
    "carry_prompt",
    "carry_answer",
    "CHANNELS",
    "explain",
]


# --------------------------------------------------------------- Channel A
def render_ui(text: str) -> str:
    """Translate ONE piece of GUI chrome (Channel A).

    The only translating function in the product. Fail-open: an unknown string
    is returned unchanged, so a missing entry shows English rather than
    blanking a control.

    IDEMPOTENT: ``render_ui(render_ui(x)) == render_ui(x)``. A string may pass
    through more than once (a template value that is later re-rendered), and a
    second pass must never double-translate. Pinned by
    ``test_render_ui_is_idempotent``.
    """
    if not text:
        return text
    try:
        from .ui_es import translate
    except Exception:      # pragma: no cover - defensive
        return text
    try:
        return translate(text)
    except Exception:      # pragma: no cover - defensive
        return text


# --------------------------------------------------------------- Channel B
def carry_prompt(text: str) -> str:
    """The user's prompt, UNCHANGED. Deliberately an identity function.

    What the user typed is what the model receives — accents, Mexican idiom,
    English technical nouns and all. NEPANTLA's normalization
    (``capability_registry.normalize_request``) produces a SEPARATE string used
    only to score tool selection; it is never substituted for the prompt.

    Do not add translation here. If a model cannot handle Spanish, that is
    Stage 0's job (``model_caps``): tier the model and expand the scoring key.
    """
    return text


# --------------------------------------------------------------- Channel C
def carry_answer(text: str) -> str:
    """The model's answer, UNCHANGED. Deliberately an identity function.

    See the module docstring for the four reasons. In short: translating the
    answer would break the register, corrupt the machine surfaces embedded in
    it, risk misreporting what actually executed, and contradict the
    architecture's central claim.
    """
    return text


# ------------------------------------------------------------------- table
CHANNELS: Dict[str, Dict[str, str]] = {
    "ui": {
        "policy": "TRANSLATED",
        "function": "render_ui",
        "what": "GUI chrome: labels, buttons, menus, system banners",
        "why": "our own closed, authored, DNT-checked string set",
    },
    "prompt": {
        "policy": "NEVER TRANSLATED",
        "function": "carry_prompt",
        "what": "what the user typed",
        "why": "NEPANTLA builds a separate scoring key; the model gets her words",
    },
    "answer": {
        "policy": "NEVER TRANSLATED",
        "function": "carry_answer",
        "what": "what the model produced",
        "why": "protects register, machine surfaces and truthfulness (paper §4)",
    },
}


def explain() -> List[str]:
    """Human-readable policy lines — for docs, logs and tests."""
    return [
        "%-7s %-16s %-11s %s" % (k, v["function"], v["policy"], v["why"])
        for k, v in CHANNELS.items()
    ]
