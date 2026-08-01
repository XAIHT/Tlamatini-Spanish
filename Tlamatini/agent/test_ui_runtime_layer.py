# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""
Pins for the NEPANTLA runtime layer and the three-channel policy.

Before this, ui_es.UI_ES was a 198-pair catalog that nothing executed: the GUI
Spanish was hardcoded in the template, so the catalog and the screen could
drift apart silently. The template now names the ENGLISH source and the catalog
produces the Spanish, which makes them the same fact instead of two copies.

The other two channels are pinned here for a different reason: their policy is
to do NOTHING, and an invariant that consists of not acting is exactly the kind
that gets "helpfully" broken later. So the passthrough is asserted, and there
is a source-contract test that fails if a translation call ever appears on the
answer path.
"""
import os
import re
import unittest

from django.template import Context, Template
from django.test import SimpleTestCase

from agent.i18n import policy
from agent.i18n.ui_es import UI_ES

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(AGENT_DIR, "templates", "agent", "agent_page.html")


def render(src, **ctx):
    return Template(src).render(Context(ctx))


# ══════════════════════════════════════════════ Channel A — GUI chrome
class TemplateTagTests(SimpleTestCase):
    """{% t %} is the runtime layer. It must be correct AND unsurprising."""

    def test_tag_translates_a_known_string(self):
        out = render('{% load nepantla %}{% t "Context" %}')
        self.assertEqual(out, UI_ES["Context"])
        self.assertEqual(out, "Contexto")

    def test_filter_form_works_too(self):
        out = render("{% load nepantla %}{{ label|t }}", label="Save")
        self.assertEqual(out, UI_ES["Save"])

    def test_unknown_string_falls_through_unchanged(self):
        """FAIL-OPEN: a missing entry shows English, never a blank control."""
        out = render('{% load nepantla %}{% t "No such string at all" %}')
        self.assertEqual(out, "No such string at all")

    def test_empty_and_none_are_safe(self):
        self.assertEqual(render('{% load nepantla %}{% t "" %}'), "")
        self.assertEqual(render("{% load nepantla %}{{ nothing|t }}"), "")

    def test_render_ui_is_idempotent(self):
        """translate(translate(x)) == translate(x).

        A string can pass through the layer more than once; a second pass must
        never double-translate. This also proves no Spanish VALUE is itself an
        English KEY, which would silently chain two lookups.
        """
        offenders = []
        for en, es in UI_ES.items():
            once = policy.render_ui(en)
            twice = policy.render_ui(once)
            if once != twice:
                offenders.append((en, once, twice))
        self.assertEqual(offenders, [], "translation is not idempotent: %r" % offenders[:5])

    def test_dnt_terms_survive_the_layer(self):
        """The register rule, enforced through the actual runtime path."""
        for en, term in (("Context", "Context"), ("Exec report", "Exec report"),
                         ("Multi-Turn", "Multi-Turn"), ("MCPs", "MCPs")):
            out = policy.render_ui(en)
            if term in en and term not in ("Context",):
                self.assertIn(term, out,
                              "%r must survive byte-exact in %r" % (term, out))


class TemplateWiringTests(SimpleTestCase):
    """The template must actually USE the layer, and keep using it."""

    def setUp(self):
        with open(TEMPLATE, encoding="utf-8") as fh:
            self.src = fh.read()

    def test_template_loads_the_library(self):
        self.assertIn("{% load nepantla %}", self.src)

    def test_template_uses_the_tag_substantially(self):
        uses = re.findall(r'\{%\s*t\s+"', self.src)
        self.assertGreater(len(uses), 100,
                           "expected the GUI chrome to go through the layer")

    def test_every_key_used_by_the_template_exists_in_the_catalog(self):
        """A typo in a {% t %} key would silently ship English."""
        missing = [k for k in re.findall(r'\{%\s*t\s+"([^"]+)"\s*%\}', self.src)
                   if k not in UI_ES]
        self.assertEqual(missing, [],
                         "template asks for keys the catalog lacks: %r" % missing[:8])

    def test_converted_strings_need_no_escaping(self):
        """THE ESCAPING CONTRACT.

        Literal template text is emitted raw; a tag's return value is HTML
        escaped. Converting a string containing & < > \" ' would therefore
        change the rendered bytes. Only escape-neutral strings were converted,
        and this keeps it that way.
        """
        special = set("&<>\"'")
        bad = []
        for key in re.findall(r'\{%\s*t\s+"([^"]+)"\s*%\}', self.src):
            value = UI_ES.get(key, key)
            if special & set(value):
                bad.append((key, value))
        self.assertEqual(bad, [],
                         "these would render differently once escaped: %r" % bad[:5])

    def test_no_convertible_spanish_is_left_hardcoded(self):
        """Drift guard: if someone re-hardcodes a label the catalog knows,
        the catalog stops being the source of truth again."""
        rev = {}
        for en, es in UI_ES.items():
            rev.setdefault(es, []).append(en)
        unambiguous = {es for es, ens in rev.items() if len(ens) == 1}

        # ignore <script>/<style>, where Spanish may be JS data
        body = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", "",
                      self.src, flags=re.DOTALL | re.IGNORECASE)
        special = set("&<>\"'")
        leftover = []
        for text in re.findall(r">([^<>{}\n]{2,90})<", body):
            t = text.strip()
            if t in unambiguous and not (special & set(t)):
                leftover.append(t)
        self.assertEqual(leftover, [],
                         "still hardcoded although the catalog has them: %r"
                         % leftover[:6])


# ═══════════════════════════════════════ Channel B — the user's prompt
class PromptIsNeverTranslatedTests(SimpleTestCase):
    """Her words reach the model exactly as typed."""

    CASES = [
        "borra los archivos viejos de la carpeta de logs",
        "¿cómo reviso el log de un container?",
        "échame la mano con una duda de programación",
        "haciendo un Pod en Dockerer y creando un Container en Kubernetes",
        "muéstrame el path del config",
        "BEGIN-CODE<<<x.py>>>\nprint('hola')\nEND-CODE",
    ]

    def test_prompt_passes_through_byte_for_byte(self):
        for text in self.CASES:
            self.assertEqual(policy.carry_prompt(text), text)

    def test_accents_and_inverted_marks_are_not_stripped(self):
        text = "¿Qué onda? Aguántame tantito, ¡ahorita!"
        self.assertEqual(policy.carry_prompt(text), text)

    def test_english_technical_nouns_are_not_translated_into_spanish(self):
        text = "revisa el log del container y el status del pod"
        out = policy.carry_prompt(text)
        for term in ("log", "container", "status", "pod"):
            self.assertIn(term, out)
        for wrong in ("bitácora", "contenedor", "vaina"):
            self.assertNotIn(wrong, out)


# ══════════════════════════════════════ Channel C — the model's answer
class AnswerIsNeverTranslatedTests(SimpleTestCase):
    """The answer is passed through untouched — deliberately."""

    CASES = [
        "Un container de Docker es un empaque aislado.\nEND-RESPONSE",
        "BEGIN-CODE<<<main.py>>>\nprint('hi')\nEND-CODE",
        "INI_SECTION_EXECUTER<<<\nstatus: ok\n\ncuerpo\n>>>END_SECTION_EXECUTER",
        "<table class='exec-report-table'><tr><td>Executer</td></tr></table>",
        "<!--TLAMATINI_EXEC_REPORT_BOUNDARY-->",
        "🔁 Tactic #2 while working — reintento la misma petición",
    ]

    def test_answer_passes_through_byte_for_byte(self):
        for text in self.CASES:
            self.assertEqual(policy.carry_answer(text), text)

    def test_machine_sentinels_survive(self):
        for sentinel in ("END-RESPONSE", "BEGIN-CODE", "INI_SECTION_",
                         "TLAMATINI_EXEC_REPORT_BOUNDARY"):
            payload = "texto %s texto" % sentinel
            self.assertIn(sentinel, policy.carry_answer(payload))


class NoAnswerSideTranslationContractTests(SimpleTestCase):
    """Source contract: nothing on the answer path may translate.

    This is the test that makes Channel C a guarantee rather than a habit. It
    reads the files an answer actually travels through and fails if a
    translation call appears in any of them.
    """

    ANSWER_PATH = [
        "consumers.py",
        os.path.join("services", "response_parser.py"),
        os.path.join("rag", "chains", "unified.py"),
        os.path.join("rag", "chains", "basic.py"),
        os.path.join("rag", "chains", "history_aware.py"),
    ]
    FORBIDDEN = re.compile(
        r"\b(ui_es|UI_ES|render_ui|translate\s*\(|back_translat\w*)", re.IGNORECASE)

    def test_answer_path_contains_no_translation_call(self):
        offenders = []
        for rel in self.ANSWER_PATH:
            path = os.path.join(AGENT_DIR, rel)
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8", errors="ignore") as fh:
                for n, line in enumerate(fh, 1):
                    if line.lstrip().startswith("#"):
                        continue
                    if self.FORBIDDEN.search(line):
                        offenders.append("%s:%d %s" % (rel, n, line.strip()[:70]))
        self.assertEqual(
            offenders, [],
            "the model's answer must never be translated — see "
            "agent/i18n/policy.py for the four reasons:\n  " + "\n  ".join(offenders))

    def test_policy_names_all_three_channels(self):
        self.assertEqual(set(policy.CHANNELS), {"ui", "prompt", "answer"})
        self.assertEqual(policy.CHANNELS["ui"]["policy"], "TRANSLATED")
        self.assertEqual(policy.CHANNELS["prompt"]["policy"], "NEVER TRANSLATED")
        self.assertEqual(policy.CHANNELS["answer"]["policy"], "NEVER TRANSLATED")
        self.assertEqual(len(policy.explain()), 3)

    def test_the_identity_functions_are_really_identities(self):
        """Guards against someone quietly giving them behaviour."""
        import inspect

        for fn in (policy.carry_prompt, policy.carry_answer):
            body = inspect.getsource(fn)
            code = [ln.strip() for ln in body.splitlines()
                    if ln.strip() and not ln.strip().startswith(("#", '"""', "'''"))]
            self.assertIn("return text", code[-1],
                          "%s must return its input unchanged" % fn.__name__)


if __name__ == "__main__":
    unittest.main()
