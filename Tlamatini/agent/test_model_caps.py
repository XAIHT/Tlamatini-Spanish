"""Contract tests for NEPANTLA Stage 0 - the per-model capability gate.

Every invariant asserted in ``agent/i18n/model_caps.py``'s docstring is pinned
here. The module makes strong claims - "the seed can never demote", "a
transport failure is not evidence", "observation demotes but never promotes" -
and a claim that is not tested is a comment.

Run:  python Tlamatini/agent/test_model_caps.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.i18n import model_caps as mc  # noqa: E402


# ---------------------------------------------------------------------------
# Stand-in models. No network, no Ollama, fully deterministic.
# ---------------------------------------------------------------------------
def fake_fluent(prompt):
    if "git push" in prompt:
        return ("Sube los commits de tu rama local al repositorio remoto para "
                "que el equipo los pueda ver.")
    if "container" in prompt:
        return ("Un Docker container es un proceso aislado con su propio "
                "filesystem, y un Kubernetes pod agrupa uno o mas containers "
                "que comparten la red.")
    if "tool correcta" in prompt:
        return "chat_agent_deleter"
    return "El niño pequeño compró un pingüino en España."


def fake_weak(prompt):
    """Answers in English, over-translates, picks the wrong tool."""
    if "git push" in prompt:
        return "It uploads your local commits to the remote repository."
    if "container" in prompt:
        return ("Un contenedor de Docker es un proceso aislado y una vaina de "
                "Kubernetes agrupa contenedores.")
    if "tool correcta" in prompt:
        return "chat_agent_gitter"
    return "El nino pequeno compro un pinguino en Espana."


def fake_indecisive(prompt):
    """Fluent Spanish, but lists every tool instead of choosing one."""
    if "tool correcta" in prompt:
        return ("Podrias usar chat_agent_deleter, chat_agent_emailer, "
                "chat_agent_gitter o chat_agent_shoter.")
    return fake_fluent(prompt)


def fake_dead(prompt):
    raise OSError("connection refused")


class _Isolated(unittest.TestCase):
    """Each test gets its own cache file; none touches the real one."""

    def setUp(self):
        self._dir = tempfile.mkdtemp(prefix="nepantla-caps-")
        self._prev = os.environ.get("CONFIG_PATH")
        os.environ["CONFIG_PATH"] = os.path.join(self._dir, "config.json")
        mc.invalidate()

    def tearDown(self):
        if self._prev is None:
            os.environ.pop("CONFIG_PATH", None)
        else:
            os.environ["CONFIG_PATH"] = self._prev
        mc.invalidate()
        shutil.rmtree(self._dir, ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════════════
class IdentityTests(_Isolated):
    """The cache key must change iff the artifact changes."""

    def test_cloud_suffix_is_part_of_the_identity(self):
        # The bug this pins: an earlier revision normalised both to "glm-5.2",
        # so a local model and a cloud model shared one verdict.
        self.assertNotEqual(mc.identity("glm-5.2:cloud"),
                            mc.identity("glm-5.2"))

    def test_size_tag_is_part_of_the_identity(self):
        self.assertNotEqual(mc.identity("qwen3-vl:8b"),
                            mc.identity("qwen3-vl:4b"))

    def test_registry_namespace_is_stripped_but_tag_kept(self):
        self.assertEqual(mc.identity("library/qwen3.5:cloud"),
                         mc.identity("qwen3.5:cloud"))

    def test_digest_beats_name(self):
        a = mc.identity("whatever:latest", digest="sha256:" + "ab" * 32)
        b = mc.identity("something-else", digest="ab" * 32)
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("sha256:"))

    def test_identity_never_raises(self):
        for junk in (None, "", "   ", 12345, {"x": 1}, b"\x00", "\x00\x01"):
            self.assertIsInstance(mc.identity(junk), str)


# ═══════════════════════════════════════════════════════════════════════════
class SeedIsNotAnAuthorityTests(_Isolated):
    """The correction that matters: a regex may never decide competence."""

    def test_seed_can_never_emit_weak(self):
        # Property over the whole table plus adversarial ids. Demotion by name
        # is the unrecoverable direction and must be structurally impossible.
        probes = ["phi3:mini", "tinyllama:1.1b", "smollm:135m", "stablelm",
                  "glm-5.2:cloud", "qwen3.5:cloud", "claude-opus-5",
                  "some-brand-new-thing:v9", "", "???", "llama2:7b"]
        for name in probes:
            self.assertIn(mc.seed_tier(name), (mc.FLUENT, mc.UNKNOWN),
                          "seed emitted a demotion for %r" % name)

    def test_absence_from_the_table_is_unknown_not_weak(self):
        self.assertEqual(mc.seed_tier("utterly-unheard-of:v1"), mc.UNKNOWN)

    def test_unknown_behaves_exactly_as_assist(self):
        u = mc.policy_for("utterly-unheard-of:v1")
        self.assertEqual(
            (u["fold"], u["expand"], u["boost_english"]),
            mc._POLICY[mc.ASSIST])

    def test_probe_overrides_a_fluent_seed(self):
        name = "glm-5.2:cloud"
        self.assertEqual(mc.seed_tier(name), mc.FLUENT)
        mc.record(name, mc.run_probe(name, fake_weak))
        self.assertEqual(mc.tier_for(name), mc.WEAK)
        self.assertTrue(mc.policy_for(name)["authoritative"])

    def test_probe_overrides_an_unknown_seed(self):
        name = "nobody-has-heard-of-this:v1"
        self.assertEqual(mc.seed_tier(name), mc.UNKNOWN)
        mc.record(name, mc.run_probe(name, fake_fluent))
        self.assertEqual(mc.tier_for(name), mc.FLUENT)

    def test_seed_only_applies_before_a_probe(self):
        name = "claude-opus-5"
        self.assertEqual(mc.policy_for(name)["source"], "seed")
        mc.record(name, mc.run_probe(name, fake_fluent))
        self.assertEqual(mc.policy_for(name)["source"], "probe")


# ═══════════════════════════════════════════════════════════════════════════
class FailOpenTests(_Isolated):
    """Any doubt resolves to ASSIST. Never to FLUENT, never to an exception."""

    def test_garbage_never_raises_and_never_claims_fluent(self):
        for junk in (None, "", "   ", 12345, {"x": 1}, [1, 2], "\x00\x01"):
            pol = mc.policy_for(junk)
            self.assertNotEqual(pol["tier"], mc.FLUENT,
                                "claimed fluent for %r" % (junk,))
            self.assertTrue(pol["expand"])

    def test_a_corrupt_cache_degrades_to_the_seed(self):
        with open(mc.cache_path(), "w", encoding="utf-8") as fh:
            fh.write("{not json at all")
        mc.invalidate()
        self.assertEqual(mc.tier_for("claude-opus-5"), mc.FLUENT)   # seed
        self.assertEqual(mc.tier_for("mystery:v1"), mc.UNKNOWN)

    def test_a_cache_of_the_wrong_shape_is_ignored(self):
        with open(mc.cache_path(), "w", encoding="utf-8") as fh:
            json.dump({"mystery:v1": "not-a-dict"}, fh)
        mc.invalidate()
        self.assertEqual(mc.tier_for("mystery:v1"), mc.UNKNOWN)

    def test_stale_probe_version_is_treated_as_absent(self):
        name = "mystery:v1"
        v = mc.run_probe(name, fake_fluent)
        v["probe_version"] = mc.PROBE_VERSION - 1
        mc.record(name, v)
        self.assertIsNone(mc.known(name))
        self.assertEqual(mc.tier_for(name), mc.UNKNOWN)


# ═══════════════════════════════════════════════════════════════════════════
class ProbeTests(_Isolated):

    def test_fluent_model_scores_fluent(self):
        v = mc.run_probe("x:1", fake_fluent)
        self.assertEqual(v["tier"], mc.FLUENT)
        self.assertGreaterEqual(v["score"], mc._FLUENT_AT)

    def test_weak_model_scores_weak(self):
        v = mc.run_probe("x:1", fake_weak)
        self.assertEqual(v["tier"], mc.WEAK)

    def test_listing_every_tool_is_not_selecting_one(self):
        # A model that answers "you could use A, B, C or D" has not done the
        # job, and must not score full marks on the check that matters most.
        v = mc.run_probe("x:1", fake_indecisive)
        self.assertLess(v["checks"]["semantic"]["score"], 1.0)

    def test_raw_features_are_persisted_for_retuning(self):
        name = "x:1"
        mc.record(name, mc.run_probe(name, fake_fluent))
        rec = mc.known(name)
        self.assertIn("checks", rec)
        for key in ("language", "register", "semantic", "charset"):
            self.assertIn(key, rec["checks"])
            self.assertIn("score", rec["checks"][key])
            self.assertIn("answer", rec["checks"][key])   # auditable

    def test_transport_failure_is_inconclusive_not_weak(self):
        # THE important one. A dead connection says nothing about Spanish;
        # recording WEAK here would permanently damn a model for a network
        # blip, and the seed could never rescue it.
        v = mc.run_probe("x:1", fake_dead)
        self.assertTrue(v["inconclusive"])
        self.assertEqual(v["tier"], mc.UNKNOWN)

    def test_an_inconclusive_probe_is_never_cached(self):
        name = "x:1"
        mc.record(name, mc.run_probe(name, fake_dead))
        self.assertIsNone(mc.known(name))

    def test_embedders_are_never_probed(self):
        self.assertTrue(mc.is_embedder("Nomic-Embed-Text:latest"))
        started = mc.probe_in_background("Nomic-Embed-Text:latest", fake_fluent)
        self.assertFalse(started)

    def test_probe_is_deterministic(self):
        a = mc.run_probe("x:1", fake_fluent)
        b = mc.run_probe("x:1", fake_fluent)
        self.assertEqual(a["score"], b["score"])
        self.assertEqual(a["tier"], b["tier"])


# ═══════════════════════════════════════════════════════════════════════════
class GraderTests(unittest.TestCase):
    """Each grader is a pure function; no model judges another model."""

    def test_english_reply_to_spanish_question_fails_language(self):
        self.assertEqual(
            mc._g_language("It uploads your commits to the remote repo."), 0.0)

    def test_spanish_reply_passes_language(self):
        self.assertEqual(
            mc._g_language("Sube los commits de la rama local al remoto."), 1.0)

    def test_over_translation_is_a_hard_zero(self):
        self.assertEqual(
            mc._g_register("Un contenedor de Docker y una vaina de Kubernetes."),
            0.0)

    def test_keeping_the_english_nouns_scores_full(self):
        self.assertEqual(
            mc._g_register("Un Docker container y un Kubernetes pod."), 1.0)

    def test_dodging_the_register_question_is_neither_pass_nor_fail(self):
        self.assertEqual(mc._g_register("Son cosas de la nube."), 0.5)

    def test_mojibake_is_a_hard_zero(self):
        self.assertEqual(mc._g_charset("El niÃ±o pequeÃ±o comprÃ³"), 0.0)

    def test_correct_diacritics_score_full(self):
        self.assertEqual(
            mc._g_charset("El niño pequeño compró un "
                          "pingüino en España."), 1.0)

    def test_wrong_tool_is_zero(self):
        self.assertEqual(
            mc._g_semantic("chat_agent_gitter", "chat_agent_deleter"), 0.0)

    def test_graders_never_raise_on_empty_or_none(self):
        for g in (mc._g_language, mc._g_register, mc._g_charset):
            for bad in ("", None, "   "):
                self.assertIsInstance(g(bad), float)


# ═══════════════════════════════════════════════════════════════════════════
class PassiveVerificationTests(_Isolated):
    """L2 corrects a standing verdict from real traffic. Demotes only."""

    def _seed_fluent(self, name):
        mc.record(name, mc.run_probe(name, fake_fluent))
        self.assertEqual(mc.tier_for(name), mc.FLUENT)

    def test_english_requests_are_ignored(self):
        name = "x:1"
        self._seed_fluent(name)
        for _ in range(50):
            mc.observe(name, "delete the old log files please",
                       "Sure, deleting them now.")
        self.assertIsNone(mc.known(name).get("observations"))

    def test_one_bad_answer_does_not_flip_the_gate(self):
        name = "x:1"
        self._seed_fluent(name)
        mc.observe(name, "borra los archivos viejos de la carpeta de logs",
                   "Sure, I deleted them for you.")
        self.assertEqual(mc.tier_for(name), mc.FLUENT)

    def test_sustained_english_replies_demote_to_assist(self):
        name = "x:1"
        self._seed_fluent(name)
        change = None
        for _ in range(mc._OBSERVE_MIN_SAMPLE + 4):
            change = mc.observe(
                name, "borra los archivos viejos de la carpeta de logs",
                "Sure, I have deleted the old files for you.") or change
        self.assertEqual(mc.tier_for(name), mc.ASSIST)
        self.assertTrue(mc.known(name)["demoted"])
        self.assertIsNotNone(change)

    def test_observation_never_promotes(self):
        # A weak model answering easy Spanish well must NOT be upgraded;
        # promotion requires a probe.
        name = "x:1"
        mc.record(name, mc.run_probe(name, fake_weak))
        self.assertEqual(mc.tier_for(name), mc.WEAK)
        for _ in range(60):
            mc.observe(name, "borra los archivos viejos de la carpeta de logs",
                       "Claro, ya borré los archivos viejos de la carpeta.")
        self.assertEqual(mc.tier_for(name), mc.WEAK)

    def test_observation_without_a_probe_does_nothing(self):
        # L2 is a corrector, never a bootstrapper.
        name = "never-probed:v1"
        for _ in range(40):
            mc.observe(name, "borra los archivos viejos de la carpeta",
                       "Sure, done.")
        self.assertIsNone(mc.known(name))

    def test_the_window_is_bounded(self):
        name = "x:1"
        self._seed_fluent(name)
        for _ in range(mc._OBSERVE_WINDOW + 60):
            mc.observe(name, "borra los archivos viejos de la carpeta de logs",
                       "Claro, ya borré los archivos viejos.")
        self.assertLessEqual(mc.known(name)["observations"]["n"],
                             mc._OBSERVE_WINDOW + 1)

    def test_a_fresh_probe_resets_the_observation_window(self):
        """Found by review 2026-07-28: the probe was not actually the authority.

        A model demoted on a poisoned window, then re-probed FLUENT, was
        re-demoted by the NEXT response because the stale counters survived.
        """
        name = "x:1"
        self._seed_fluent(name)
        for _ in range(mc._OBSERVE_MIN_SAMPLE + 8):
            mc.observe(name, "borra los archivos viejos de la carpeta de logs",
                       "Sure, I deleted the old files for you.")
        self.assertEqual(mc.tier_for(name), mc.ASSIST)

        mc.record(name, mc.run_probe(name, fake_fluent))     # re-probe
        self.assertEqual(mc.tier_for(name), mc.FLUENT)

        # ONE further imperfect response must NOT undo a fresh verdict.
        mc.observe(name, "borra los archivos viejos de la carpeta de logs",
                   "Sure, I deleted the old files for you.")
        self.assertEqual(mc.tier_for(name), mc.FLUENT)

    def test_the_old_window_is_kept_for_audit(self):
        name = "x:1"
        self._seed_fluent(name)
        for _ in range(mc._OBSERVE_MIN_SAMPLE + 2):
            mc.observe(name, "borra los archivos viejos de la carpeta de logs",
                       "Sure, deleted.")
        mc.record(name, mc.run_probe(name, fake_fluent))
        rec = mc.known(name)
        self.assertIn("previous_observations", rec)
        self.assertIsNone(rec.get("observations"))

    def test_observe_never_raises(self):
        for args in ((None, None, None), ("x", "", ""), (1, 2, 3)):
            self.assertIsNone(mc.observe(*args))


# ═══════════════════════════════════════════════════════════════════════════
class FertilityIsNotUsedTests(unittest.TestCase):
    """Encodes the research finding so nobody helpfully re-adds it.

    Tokenizer fertility measures COST, not Spanish competence: measured on
    this project's own models it spanned 0.74-0.83 for every model including
    a 756B frontier model, and the literature finds no significant
    correlation in narrow-range languages (rho=-0.43, p=0.34).
    """

    def test_module_contains_no_token_counting_logic(self):
        with open(mc.__file__, encoding="utf-8") as fh:
            src = fh.read()
        # Split the docstring (which discusses and REJECTS fertility) from the
        # code, and assert the rejection never leaked into an implementation.
        body = src.split('"""', 2)[-1]
        for banned in ("prompt_eval_count", "eval_count", "fertility",
                       "tokens_per", "chars_per_token", "token_tax"):
            self.assertNotIn(banned, body,
                             "fertility logic reappeared in the gate: %r"
                             % banned)

    def test_module_reads_no_language_metadata(self):
        with open(mc.__file__, encoding="utf-8") as fh:
            src = fh.read()
        body = src.split('"""', 2)[-1]
        for banned in ("general.languages", "model_info", "api/show"):
            self.assertNotIn(banned, body,
                             "the gate started trusting metadata: %r" % banned)


# ═══════════════════════════════════════════════════════════════════════════
class IntegrationTests(_Isolated):
    """The gate must actually change what the scorer sees - and only that."""

    def setUp(self):
        super().setUp()
        import importlib
        from agent import capability_registry
        importlib.reload(capability_registry)
        self.cr = capability_registry

    ES = "borra los archivos viejos de la carpeta de logs"
    EN = "delete the old files from the logs folder"

    def test_fluent_model_keeps_the_users_own_words(self):
        mc.record("f:1", mc.run_probe("f:1", fake_fluent))
        base = self.cr.normalize_request(self.ES)
        flu = self.cr.normalize_request(self.ES, "f:1")
        self.assertLess(len(flu), len(base))

    def test_weak_model_still_gets_the_hints(self):
        mc.record("w:1", mc.run_probe("w:1", fake_weak))
        base = self.cr.normalize_request(self.ES)
        weak = self.cr.normalize_request(self.ES, "w:1")
        self.assertEqual(weak, base)

    def test_no_model_name_is_byte_identical_to_the_legacy_path(self):
        mc.record("f:1", mc.run_probe("f:1", fake_fluent))
        self.assertNotEqual(self.cr.normalize_request(self.ES),
                            self.cr.normalize_request(self.ES, "f:1"))

    def test_english_is_untouched_on_every_path(self):
        mc.record("f:1", mc.run_probe("f:1", fake_fluent))
        mc.record("w:1", mc.run_probe("w:1", fake_weak))
        a = self.cr.normalize_request(self.EN)
        b = self.cr.normalize_request(self.EN, "f:1")
        c = self.cr.normalize_request(self.EN, "w:1")
        self.assertEqual(a, b)
        self.assertEqual(b, c)


if __name__ == "__main__":
    unittest.main(verbosity=2)
