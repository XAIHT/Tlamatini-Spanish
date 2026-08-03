# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Guards the ACTIVE-FIRST ordering of the External ▸ MCPs dialog.

Ported from the English tree (Angela, 2026-08-02). With a large catalog it was
a headache to see WHICH ≤5 servers are actually active, so the dialog now pins
the active ones to the TOP of the list and groups the rest underneath.

Three layers are guarded, because each can break on its own:

1. BEHAVIOUR — ``compareServers`` is lifted out of the browser file and run in
   node against shuffled fixtures. This tests the ordering LOGIC, not the mere
   presence of the text. Skipped (never failed) when node is unavailable.
2. SOURCE CONTRACT — the invariants a future edit could silently undo, above
   all ``shown.sort()`` running BEFORE ``shown.slice()``: sorting after the
   slice would let the render limit cut an ACTIVE server out of the list, which
   is exactly the bug the feature exists to prevent.
3. COLLECTED STATIC — ``staticfiles/`` is what the browser actually downloads.
   Source can be perfect while the served copy is stale, so both are checked
   (this mirrors ``test_frontend_mutable_state.py``'s const-poison guard).

This is the SPANISH edition, so the two group headings and the legend are also
pinned to Spanish: an English string here is a localization regression.
"""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent

JS_RELATIVE = Path("agent") / "js" / "external_mcps_dialog.js"
CSS_RELATIVE = Path("agent") / "css" / "external_mcps_dialog.css"

JS_SOURCE = ROOT / "static" / JS_RELATIVE
CSS_SOURCE = ROOT / "static" / CSS_RELATIVE

# Angela's edition is Spanish: these are the exact user-visible strings.
HEADING_ACTIVE_ES = "Activos — se mandan con tu prompt"
HEADING_REST_ES = "Catálogo — inactivos"
LEGEND_FRAGMENT_ES = "los activos se quedan fijos hasta arriba"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_compare_servers(js_text: str) -> str:
    """Lift the ``compareServers`` function body out of the browser file.

    The file is an IIFE that touches ``document`` on load, so it cannot simply
    be imported into node. Slicing the one function out keeps the behavioural
    test honest (it runs the SHIPPED code) without needing a DOM.
    """
    start = js_text.index("function compareServers(")
    depth = 0
    for index in range(start, len(js_text)):
        char = js_text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return js_text[start:index + 1]
    raise AssertionError("compareServers(...) has unbalanced braces")


class ExternalMcpsActiveFirstBehaviourTests(unittest.TestCase):
    """Runs the REAL comparator in node — logic, not text matching."""

    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which("node")
        if not cls.node:
            raise unittest.SkipTest("node is not on PATH; behavioural check skipped")
        cls.compare_src = _extract_compare_servers(_read(JS_SOURCE))

    def _order(self, servers):
        """Return the display order the dialog would render for *servers*."""
        script = (
            self.compare_src
            + "\nconst servers = " + json.dumps(servers) + ";\n"
            + "servers.sort(compareServers);\n"
            + "console.log(JSON.stringify(servers.map(s => s.display || s.key)));\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "compare.mjs"
            path.write_text(script, encoding="utf-8")
            proc = subprocess.run(
                [self.node, str(path)], capture_output=True, text=True,
                encoding="utf-8", timeout=60,
            )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        return json.loads(proc.stdout.strip())

    def test_active_servers_are_hoisted_above_every_inactive_one(self):
        order = self._order([
            {"key": "aaa", "display": "Aaa", "active": False},
            {"key": "zzz", "display": "Zzz", "active": True},
            {"key": "mmm", "display": "Mmm", "active": False},
            {"key": "bbb", "display": "Bbb", "active": True},
        ])
        # Zzz is LAST alphabetically yet must outrank every inactive server.
        self.assertEqual(order, ["Bbb", "Zzz", "Aaa", "Mmm"])

    def test_each_block_is_alphabetical_and_case_insensitive(self):
        order = self._order([
            {"key": "d", "display": "delta", "active": True},
            {"key": "a", "display": "Alpha", "active": True},
            {"key": "c", "display": "charlie", "active": False},
            {"key": "b", "display": "Bravo", "active": False},
        ])
        self.assertEqual(order, ["Alpha", "delta", "Bravo", "charlie"])

    def test_numeric_aware_so_server10_sorts_after_server9(self):
        order = self._order([
            {"key": "s10", "display": "server10", "active": True},
            {"key": "s9", "display": "server9", "active": True},
            {"key": "s1", "display": "server1", "active": True},
        ])
        self.assertEqual(order, ["server1", "server9", "server10"])

    def test_missing_display_falls_back_to_the_key(self):
        order = self._order([
            {"key": "zeta", "display": "", "active": True},
            {"key": "alpha", "active": True},
        ])
        self.assertEqual(order, ["alpha", "zeta"])

    def test_ordering_is_stable_for_an_all_inactive_catalog(self):
        order = self._order([
            {"key": "b", "display": "Beta", "active": False},
            {"key": "a", "display": "Alpha", "active": False},
        ])
        self.assertEqual(order, ["Alpha", "Beta"])


class ExternalMcpsActiveFirstSourceContractTests(unittest.TestCase):
    """Pins the invariants a careless edit could silently undo."""

    def setUp(self):
        self.js = _read(JS_SOURCE)
        self.css = _read(CSS_SOURCE)

    def test_render_list_sorts_before_it_slices(self):
        """The whole point: an ACTIVE server must never be cut by the limit.

        Sorting AFTER the slice would leave an active server below the render
        limit invisible — the exact failure this feature exists to prevent.
        """
        sort_at = self.js.index("shown.sort(compareServers)")
        slice_at = self.js.index("shown.slice(0, EXTERNAL_MCPS_RENDER_LIMIT)")
        self.assertLess(
            sort_at, slice_at,
            msg="shown.sort(compareServers) must run BEFORE shown.slice(...), "
                "or the render limit can hide an active server.",
        )

    def test_summary_table_uses_the_same_comparator(self):
        self.assertIn(
            "servers.filter(s => s.active).sort(compareServers)", self.js,
            msg="The summary table must use the same order as the list.",
        )

    def test_group_headings_are_emitted_only_when_both_blocks_are_present(self):
        self.assertIn("function listHeading(", self.js)
        self.assertIn(
            "const showGroups = rendered.some(s => s.active) "
            "&& rendered.some(s => !s.active)", self.js,
            msg="A heading over a single-block list is noise; keep the guard.",
        )

    def test_toggling_a_server_reveals_and_refocuses_its_row(self):
        """renderList() replaces the DOM node the focus was sitting on."""
        self.assertIn("function revealRow(", self.js)
        reveal_at = self.js.index("revealRow(key);")
        render_at = self.js.rindex("renderAll();", 0, reveal_at)
        self.assertLess(
            render_at, reveal_at,
            msg="revealRow(key) must run AFTER renderAll(), or it re-focuses "
                "a row that is about to be replaced.",
        )

    def test_css_defines_both_group_headings(self):
        self.assertIn(".emx-group {", self.css)
        self.assertIn(".emx-group-rest {", self.css)

    def test_headings_and_legend_are_in_spanish(self):
        """This is the Spanish edition — an English string here is a regression."""
        for spanish in (HEADING_ACTIVE_ES, HEADING_REST_ES, LEGEND_FRAGMENT_ES):
            self.assertIn(spanish, self.js, msg=f"missing Spanish string: {spanish}")
        for english in ("Active — sent with your prompt", "Catalog — inactive"):
            self.assertNotIn(
                english, self.js,
                msg=f"untranslated English string left in the Spanish tree: {english}",
            )


class ExternalMcpsActiveFirstCollectedStaticTests(unittest.TestCase):
    """staticfiles/ is what the browser downloads — a stale copy ships nothing."""

    def _collected(self, relative: Path) -> str:
        path = PROJECT_ROOT / "staticfiles" / relative
        if not path.exists():
            self.skipTest(f"{path} does not exist; run collectstatic to validate it.")
        return _read(path)

    def test_collected_js_carries_the_active_first_ordering(self):
        text = self._collected(JS_RELATIVE)
        for needle in ("function compareServers(", "shown.sort(compareServers)",
                       "function revealRow(", HEADING_ACTIVE_ES):
            self.assertIn(
                needle, text,
                msg=f"collected external_mcps_dialog.js is stale (missing {needle!r}); "
                    "run `python Tlamatini/manage.py collectstatic --noinput`.",
            )

    def test_collected_css_carries_the_group_headings(self):
        text = self._collected(CSS_RELATIVE)
        self.assertIn(".emx-group {", text)
        self.assertIn(".emx-group-rest {", text)


if __name__ == "__main__":
    unittest.main()
