"""Regression tests for the Spanish release-tag edition marker."""
import unittest

from agent import self_update, version


class EditionSuffixNormalizationTests(unittest.TestCase):
    def test_helper_removes_only_the_core_edition_marker(self):
        cases = {
            "1.50.0s": "1.50.0",
            "v1.50.0s": "v1.50.0",
            "1.50.0s-rc.1": "1.50.0-rc.1",
            "1.50.0s+build.491": "1.50.0+build.491",
            "1.50.0": "1.50.0",
            "not-a-version": "not-a-version",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(version.strip_edition_suffix(raw), expected)

    def test_strict_parser_stays_strict(self):
        self.assertIsNone(version.parse_semver("1.50.0s"))

    def test_win32_tuple_accepts_spanish_versions(self):
        self.assertEqual(version.semver_to_win32_tuple("1.50.0s"), (1, 50, 0, 0))
        self.assertEqual(
            version.semver_to_win32_tuple("1.50.0s-rc.1+build.491"),
            (1, 50, 0, 0),
        )

    def test_render_keeps_suffix_in_strings_but_not_numeric_tuple(self):
        rendered = version.render_pyinstaller_version_file("1.50.0s")
        self.assertIn("filevers=(1, 50, 0, 0)", rendered)
        self.assertIn("prodvers=(1, 50, 0, 0)", rendered)
        self.assertIn("ProductVersion',   u'1.50.0s'", rendered)

    def test_update_comparison_keeps_patch_precision(self):
        self.assertTrue(self_update.is_newer("v1.50.1s", "1.50.0s"))
        self.assertFalse(self_update.is_newer("v1.50.0s", "1.50.0s"))
        self.assertFalse(self_update.is_newer("v1.49.1s", "1.50.0s"))


if __name__ == "__main__":
    unittest.main()
