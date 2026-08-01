# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""
The termbase exists TWICE. This is what stops the two copies drifting.

    agent/i18n/terms.csv        the reviewable inventory — what a human
                                translator reads, diffs and argues with in a
                                pull request
    agent/i18n/termbase_en.py   the runtime data — imported, no file I/O

Two representations of one inventory is a reasonable design (a CSV is
reviewable, a module is fast), but only if something proves they agree.
Nothing did — and on 2026-07-29 they were found to disagree, with the Python
side shipping FIVE Spanish words with their accents stripped:

    Password   contrasena   should be   contraseña
    Size       tamano                   tamaño
    Page       pagina                   página
    Line       linea                    línea
    Version    version                  versión

The CSV had them right the whole time. Nobody noticed because the two files
were never compared, and the accent-stripped forms are *plausible* enough to
survive a skim.

WHY A TEST AND NOT A RUNTIME LOADER
    The obvious alternative was to delete the module and load terms.csv at
    runtime (that is what the now-removed ``termdb.py`` was for). A test is the
    better tool: it gives the same single-source-of-truth guarantee with no
    file I/O on a hot path, no missing/corrupt-CSV failure mode, and no new
    packaging surfaces to keep in step (build.py, the self-modify snapshot and
    the self-update carriage would each have needed to ship the CSV).

WHAT IS ASSERTED, AND WHAT DELIBERATELY IS NOT
    Asserted: the TRANSLATE mapping agrees EXACTLY, and no Spanish rendering
    loses a diacritic. That is the user-visible half — a wrong value here ships
    a misspelling.

    Not asserted: identical membership across KEEP / ASSET / MACHINE. The CSV
    is a broader inventory (118 MACHINE rows to the module's 25) and the module
    carries casing variants the CSV does not (``Recmailer`` beside
    ``RecMailer``). Those are scope differences by design; asserting equality
    there would be a false alarm, and a test that cries wolf gets deleted.
"""
import csv
import os
import unicodedata
import unittest

from django.test import SimpleTestCase

from agent.i18n import termbase_en as TB

I18N_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n")
TERMS_CSV = os.path.join(I18N_DIR, "terms.csv")


def _rows():
    with open(TERMS_CSV, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _csv_translate():
    return {r["english"].strip(): r["spanish"].strip()
            for r in _rows() if r["policy"].strip() == "TRANSLATE"}


def _has_lost_accents(text):
    """True when folding the text changes it — i.e. it still HAS accents."""
    folded = "".join(c for c in unicodedata.normalize("NFKD", text)
                     if not unicodedata.combining(c))
    return folded != text


class TermsCsvIsPresentTests(SimpleTestCase):
    def test_csv_exists_and_is_readable(self):
        self.assertTrue(os.path.exists(TERMS_CSV), "terms.csv must ship")
        rows = _rows()
        self.assertGreater(len(rows), 300)
        self.assertEqual(
            set(rows[0].keys()),
            {"english", "spanish", "policy", "domain", "note"})

    def test_every_row_has_a_known_policy(self):
        allowed = {"KEEP", "TRANSLATE", "ASSET", "MACHINE"}
        bad = sorted({r["policy"].strip() for r in _rows()} - allowed)
        self.assertEqual(bad, [], "unknown policy value(s): %r" % bad)


class TranslateMappingAgreesTests(SimpleTestCase):
    """The half that is user-visible must agree EXACTLY."""

    def test_no_conflicting_spanish_rendering(self):
        csv_tr = _csv_translate()
        py_tr = dict(TB.SPANISH_PREFERRED)
        conflicts = [
            "%s: python=%r csv=%r" % (k, py_tr[k], csv_tr[k])
            for k in sorted(set(py_tr) & set(csv_tr))
            if py_tr[k] != csv_tr[k]
        ]
        self.assertEqual(
            conflicts, [],
            "terms.csv and termbase_en.py disagree on the Spanish rendering.\n"
            "The CSV is the reviewed copy — fix the module to match it:\n  "
            + "\n  ".join(conflicts))

    def test_module_invents_no_term_the_reviewed_csv_lacks(self):
        """The module may not add a rendering that no human reviewed."""
        missing = sorted(set(TB.SPANISH_PREFERRED) - set(_csv_translate()))
        self.assertEqual(
            missing, [],
            "termbase_en.py has TRANSLATE terms absent from terms.csv: %r"
            % missing)


class AccentsAreNotStrippedTests(SimpleTestCase):
    """The specific defect that motivated this file."""

    # Words whose correct Spanish carries a diacritic. If the module ever
    # renders one of these without it, the product misspells itself.
    MUST_KEEP_ACCENT = {
        "Password": "contraseña",
        "Size": "tamaño",
        "Page": "página",
        "Line": "línea",
        "Version": "versión",
    }

    def test_the_five_known_words_are_spelled_correctly(self):
        for key, expected in self.MUST_KEEP_ACCENT.items():
            self.assertEqual(
                TB.SPANISH_PREFERRED.get(key), expected,
                "%r must render as %r — an accent-stripped Spanish word is a "
                "misspelling, not a simplification" % (key, expected))

    def test_no_csv_accent_is_lost_in_the_module(self):
        """Generalised: if the CSV spells it with an accent, so must we."""
        csv_tr = _csv_translate()
        lost = []
        for key, spanish in csv_tr.items():
            if key not in TB.SPANISH_PREFERRED:
                continue
            ours = TB.SPANISH_PREFERRED[key]
            if _has_lost_accents(spanish) and not _has_lost_accents(ours):
                lost.append("%s: csv=%r module=%r" % (key, spanish, ours))
        self.assertEqual(lost, [],
                         "accent(s) dropped in termbase_en.py: %r" % lost)


class TermdbIsGoneTests(SimpleTestCase):
    """termdb.py was a runtime loader for a job this test file does better.

    It had ZERO importers anywhere in the repo — not one, not even a test —
    while shipping a full API over terms.csv. Keeping it implied the CSV was
    loaded at runtime, which it never was.
    """

    def test_termdb_module_is_removed(self):
        self.assertFalse(
            os.path.exists(os.path.join(I18N_DIR, "termdb.py")),
            "termdb.py is dead weight: it had no importers and the CSV/module "
            "agreement is guaranteed by this test file instead")

    def test_the_csv_itself_is_kept(self):
        """Deleting the loader must NOT delete the reviewable inventory."""
        self.assertTrue(os.path.exists(TERMS_CSV))


if __name__ == "__main__":
    unittest.main()
