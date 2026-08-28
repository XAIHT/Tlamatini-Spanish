"""The localization invariant, as a test.

    Every do-not-translate term present in an English GUI string MUST also be
    present in its Spanish rendering.

This is what turns Angela's instruction - "all the terms remain in English,
all the technical terms remain in English, the GUI is Spanish but keeps the
terms and topics in English" - from a style guideline into something the build
can prove. A translator (human or model) that renders *Emailer* as *Correero*,
or *commit* as *confirmacion*, fails here rather than shipping.

Run standalone:

    python agent/test_ui_dnt.py          # from <tree>/Tlamatini

or as part of the suite:

    python manage.py test agent.test_ui_dnt
"""

from __future__ import annotations

import os
import sys
import unittest

if __name__ == "__main__" and __package__ is None:  # standalone convenience
    _TREE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, _TREE)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tlamatini.settings")
    try:
        import django

        django.setup()
    except Exception as exc:  # pragma: no cover
        print("--- django.setup() skipped: %s" % exc, file=sys.stderr)

from agent.i18n import dnt  # noqa: E402
from agent.i18n.ui_es import UI_ES, translate  # noqa: E402


class DoNotTranslateInvariantTests(unittest.TestCase):
    """The central contract."""

    def test_every_catalog_entry_preserves_its_dnt_terms(self):
        violations = []
        for english, spanish in UI_ES.items():
            dropped = dnt.missing_terms(english, spanish)
            if dropped:
                violations.append((english, spanish, dropped))

        if violations:
            strict = dnt._case_sensitive_terms()
            loose = set(dnt._loose_lexicon())
            names = set(dnt.agent_display_names())
            tools = set(dnt.tool_names())

            def where(term):
                """Which list is demanding this term? Diagnose, never guess."""
                for label, pool in (("asset-name", names), ("tool-name", tools),
                                    ("product", set(dnt.PRODUCT_TERMS)),
                                    ("sentinel", set(dnt.MACHINE_SENTINELS)),
                                    ("tech-lexicon", loose),
                                    ("spanish-preferred", dnt._spanish_preferred())):
                    if term in pool:
                        return label
                return "strict-other" if term in strict else "unknown"

            lines = ["", "%d string(s) dropped a do-not-translate term:" % len(violations)]
            for english, spanish, dropped in violations:
                lines.append("")
                lines.append("  EN      : %s" % english)
                lines.append("  ES      : %s" % spanish)
                lines.append("  DROPPED : %s" % ", ".join(
                    "%s [%s]" % (t, where(t)) for t in dropped))
            self.fail("\n".join(lines))

    def test_no_agent_display_name_was_renamed_anywhere(self):
        """No Spanish string may contain a MIS-CASED asset name.

        Separate from the check above, which only catches a name that VANISHED.
        This catches a name that survived in the WRONG case - ``Stm32er`` for
        ``STM32er`` - which is the failure Tlamatini's naming rules exist to
        prevent, and which a case-insensitive reader would never notice.
        """
        names = dnt.agent_display_names()
        self.assertGreater(len(names), 40, "display names were not harvested")

        offenders = []
        for spanish in UI_ES.values():
            low = spanish.lower()
            for name in names:
                if len(name) < 4:
                    continue
                if name.lower() in low and not dnt.term_present(name, spanish):
                    offenders.append((name, spanish))
        self.assertEqual(offenders, [], "mis-cased asset name(s): %r" % (offenders,))

    def test_angelas_name_is_never_translated_or_dropped(self):
        """Non-negotiable, and asserted explicitly rather than by omission."""
        key = "CREATED BY ANGELA LÓPEZ MENDOZA"
        self.assertIn(key, UI_ES, "Angela's credit line left the catalog")
        es = UI_ES[key]
        # Angela asked for the line in Spanish, with the accented spelling
        # of her first name (2026-07-28). The invariant was never "this
        # line stays English" - it is "her NAME is never dropped, scrubbed,
        # or attributed to anyone else". Assert exactly that.
        # ⚠️ SIN DISTINGUIR MAYUSCULAS. La linea es un BANNER y va en versales
        # en los dos arboles ("CREATED BY ANGELA LÓPEZ MENDOZA" alla,
        # "CREADA POR ANGELA LÓPEZ MENDOZA" aqui), asi que comparar con
        # mayusculas exactas reprobaba una linea donde el nombre esta
        # ENTERO y bien escrito. El invariante nunca fue "asi se escribe
        # con mayusculas": es "su nombre no se cae, ni se borra, ni se le
        # atribuye a nadie mas", y eso se comprueba igual sin importar la
        # caja. El ACENTO si se exige: Angela pidio la grafia acentuada.
        bajo = es.lower()
        self.assertIn("lópez mendoza", bajo,
                      "Angela's surname was dropped from the credit line")
        self.assertIn("ngela", bajo,
                      "Angela's first name was dropped from the credit line")
        self.assertNotIn("CREATED BY", es,
                         "the Spanish credit line still reads as English")

    def test_product_terms_survive(self):
        """The terms Angela named explicitly: MCPs and Wizard, plus the toggles."""
        # Step-by-Step is NOT here any more: Angela ordered it shown as
        # "Paso-a-Paso" (2026-07-28), so it is a carrier string now.
        for term in ("MCPs", "ACPX", "Multi-Turn", "Ask Execs",
                     "Exec report", "Access Keys Wizard", "Skills", "Agents"):
            hits = [(en, es) for en, es in UI_ES.items() if dnt.term_present(term, en)]
            self.assertTrue(hits, "no catalog entry exercises %r" % term)
            for en, es in hits:
                self.assertTrue(
                    dnt.term_present(term, es),
                    "%r was translated away in %r -> %r" % (term, en, es))


class CatalogShapeTests(unittest.TestCase):

    def test_translate_is_fail_open(self):
        self.assertEqual(translate("a string nobody catalogued"),
                         "a string nobody catalogued")
        self.assertEqual(translate(""), "")
        self.assertIsNone(translate(None))

    def test_translation_actually_differs_for_carrier_strings(self):
        """Guard against a catalog that 'passes' by never translating anything."""
        changed = sum(1 for en, es in UI_ES.items() if en != es)
        self.assertGreater(changed, len(UI_ES) * 0.6,
                           "too few strings actually moved to Spanish")

    def test_intentional_identities_are_product_terms(self):
        """Where EN == ES, it must be BECAUSE the string is a term, not laziness."""
        # Compared case-insensitively: a product term is still a product term
        # when a sentence lowercases it ("View context directory in canvas").
        pool = {t.lower() for t in dnt.PRODUCT_TERMS}
        pool |= {t.lower() for t in dnt.agent_display_names()}
        pool |= {t.lower() for t in dnt.TECH_LEXICON}
        pool |= {t.lower() for t in dnt.MACHINE_SENTINELS}

        identities = [en for en, es in UI_ES.items() if en == es]
        for en in identities:
            carries_term = any(dnt.term_present(t, en.lower()) for t in pool)
            self.assertTrue(
                carries_term or en in (
                "or",
                # Angela's credit line is justified by being her NAME.
                # Pinned separately by
                # test_angelas_name_is_never_translated_or_dropped.
                "CREATED BY ANGELA LÓPEZ MENDOZA",
            ),
                "%r is identical in both languages but carries no "
                "do-not-translate term - translate it or justify it" % en)


class DntCheckerTests(unittest.TestCase):
    """The checker itself must not be vacuous."""

    def test_detects_a_renamed_asset(self):
        self.assertIn(
            "Emailer",
            dnt.missing_terms("Configure the Emailer agent",
                              "Configura el agente Correero"))

    def test_detects_an_over_translated_technical_term(self):
        self.assertIn(
            "commit",
            dnt.missing_terms("Make a commit and push",
                              "Haz una confirmacion y un empuje"))

    def test_accepts_the_correct_register(self):
        self.assertEqual(
            (),
            dnt.missing_terms("Make a commit and push to the repo",
                              "Haz un commit y push al repo"))
        self.assertEqual(
            (),
            dnt.missing_terms("Send an email by SMTP when a pattern is in the log",
                              "Envia un email por SMTP cuando hay un pattern en el log"))

    def test_case_is_enforced_for_assets_but_not_for_generic_terms(self):
        # An asset in the wrong case is a failure.
        self.assertIn("STM32er",
                      dnt.missing_terms("Flash with STM32er", "Flashea con Stm32er"))
        # A generic term capitalised at the start of a sentence is fine.
        self.assertEqual((),
                         dnt.missing_terms("Shell to run", "Shell donde correr"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
