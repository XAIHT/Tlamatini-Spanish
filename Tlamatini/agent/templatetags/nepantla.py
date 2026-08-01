# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""
The NEPANTLA runtime layer for templates — Channel A only.

    {% load nepantla %}
    {% t "Context" %}              ->  Contexto
    {{ label|t }}                  ->  same, for a variable
    {% t "Save" as verb %}{{ verb }}

WHAT THIS REPLACED
    Every Spanish label used to be a hardcoded literal in the template, which
    meant ``ui_es.UI_ES`` — 198 reviewed, DNT-checked pairs — was documentation
    that nothing executed. The catalog and the GUI could drift apart with
    nothing to notice. Now the template names the ENGLISH source string and the
    catalog is what produces the Spanish, so the two cannot disagree: they are
    the same fact.

THE ESCAPING CONTRACT (subtle, and the reason this file has a test)
    Literal text typed into a Django template is emitted RAW. A value returned
    from a tag is HTML-ESCAPED. So a naive swap silently changes the output for
    any string containing ``& < > " '``.

    ``t`` therefore refuses to be a silent rewriter: it returns a plain string
    and lets Django escape normally, and the conversion is only applied to
    strings that contain no HTML-special character — verified by
    ``test_converted_strings_need_no_escaping``. Anything that would render
    differently is left as a literal rather than quietly changed.

    If a future string genuinely needs markup, add it with ``{% t "..." %}``
    and mark it up in the TEMPLATE around the tag — never by returning
    ``mark_safe`` from here, which would make the catalog a source of raw HTML.

FAIL-OPEN
    Any failure returns the key unchanged, so the worst case is an English
    label — never a blank control and never a 500.
"""
from __future__ import annotations

from django import template

register = template.Library()


def _translate(value: object) -> str:
    """Channel A lookup. Never raises, never returns None."""
    if value is None:
        return ""
    text = value if isinstance(value, str) else str(value)
    if not text:
        return text
    try:
        from agent.i18n.policy import render_ui
    except Exception:      # pragma: no cover - defensive
        return text
    try:
        return render_ui(text)
    except Exception:      # pragma: no cover - defensive
        return text


@register.simple_tag(name="t")
def t(source: object) -> str:
    """``{% t "English source" %}`` -> the Spanish rendering.

    The argument is the ENGLISH string, verbatim as it appears in
    ``ui_es.UI_ES``. Using English as the key is deliberate: it keeps one
    canonical id per label, it is what the DNT checker validates against, and
    it makes an untranslated string degrade to readable English instead of a
    key like ``ui.context.label``.
    """
    return _translate(source)


@register.filter(name="t")
def t_filter(value: object) -> str:
    """``{{ value|t }}`` — same lookup, for values already in the context."""
    return _translate(value)
