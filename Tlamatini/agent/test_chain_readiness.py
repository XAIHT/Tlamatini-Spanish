# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""
Regression pins for the PERMANENT CHAT WEDGE (Angela, live run 2026-07-29).

THE BUG
    ``rag_chain_ready`` is the busy/free latch for Tlamatini's ONE chat lane.
    ``ask_rag`` lowered it on entry and raised it again on every ORDINARY exit
    — answer, cancel, prompt rejection — but its ``except Exception`` branch
    re-raised a non-cancellation error and skipped the restore. So ONE failed
    ``rag_chain.invoke()`` left the latch DOWN for the rest of the process.

WHAT THAT LOOKED LIKE
    The Django server alive and answering HTTP. Ollama healthy (embeddings in
    21 s). The GPU idle at 0 %. Nothing computing anywhere. And the chat DEAD
    FOREVER: every message answered only with "Tlamatini todavía no está
    lista." Reloading the browser did not help. Only killing the process did.
    It surfaced during a 1000-question Spanish run, after heavy Multi-Turn work
    (Shoter ×78, Image-Interpreter ×90) threw inside the chain.

THE FIX
    ``ask_rag`` is now a thin wrapper whose ``finally`` restores the latch
    unconditionally; the old body moved to ``_ask_rag_impl``. The invariant is
    now structural rather than something every future ``return`` must remember.

These tests fail on the OLD code and pass on the new. Do not weaken them: the
exception test is the one that actually reproduces the outage.
"""
import unittest

from django.test import SimpleTestCase

from agent.rag import interface as I


READY = "rag_chain_ready"


class _FakeChain:
    """Minimal stand-in for the real chain object."""

    def __init__(self, behaviour="ok"):
        self.behaviour = behaviour
        self.calls = 0

    def invoke(self, payload):
        self.calls += 1
        if self.behaviour == "raise":
            raise RuntimeError("fallo simulado del modelo")
        if self.behaviour == "dict":
            return {"answer": "listo", "multi_turn_used": True}
        return "listo"

    def getHttpxClientInstance(self):      # noqa: N802 (mirrors the real API)
        return None


def _question(text="hola"):
    """A Multi-Turn question, so prompt-shape/access validation is bypassed."""
    return {
        "input": text,
        "conversation_user_id": 1,
        "multi_turn_enabled": True,
        "exec_report_enabled": False,
        "acpx_enabled": False,
        "ask_execs_enabled": False,
        "step_by_step_enabled": False,
    }


class ChainReadinessLatchTests(SimpleTestCase):
    """The latch must be released on EVERY exit path."""

    def setUp(self):
        # Start each test from a known-bad state so a test that never touches
        # the flag cannot accidentally pass.
        I.global_state.set_state(READY, False)

    def _ready(self):
        return I.global_state.get_state(READY)

    def test_latch_released_after_a_normal_answer(self):
        out = I.ask_rag(_FakeChain("ok"), _question())
        self.assertTrue(self._ready(), "una respuesta normal debe liberar la cadena")
        self.assertIn("listo", str(out))

    def test_latch_released_after_a_dict_answer(self):
        out = I.ask_rag(_FakeChain("dict"), _question())
        self.assertTrue(self._ready(), "una respuesta dict debe liberar la cadena")
        self.assertIn("listo", str(out))

    def test_latch_released_when_the_chain_RAISES(self):
        """*** THE OUTAGE ***  Fails on the old code: the latch stayed down."""
        chain = _FakeChain("raise")
        with self.assertRaises(RuntimeError):
            I.ask_rag(chain, _question())
        self.assertTrue(
            self._ready(),
            "una excepción NO debe dejar la cadena trabada: ese es exactamente "
            "el bug que mató el chat de forma permanente",
        )

    def test_the_error_still_propagates(self):
        """The fix must not SWALLOW the failure — silent success is worse."""
        with self.assertRaises(RuntimeError) as ctx:
            I.ask_rag(_FakeChain("raise"), _question())
        self.assertIn("fallo simulado", str(ctx.exception))

    def test_chat_still_works_after_a_failure(self):
        """The real user-visible contract: one bad request must not kill the chat."""
        with self.assertRaises(RuntimeError):
            I.ask_rag(_FakeChain("raise"), _question("esta truena"))
        self.assertTrue(self._ready())
        out = I.ask_rag(_FakeChain("ok"), _question("y esta si jala"))
        self.assertIn("listo", str(out))
        self.assertTrue(self._ready())

    def test_repeated_failures_never_latch_it_down(self):
        for _ in range(5):
            with self.assertRaises(RuntimeError):
                I.ask_rag(_FakeChain("raise"), _question())
            self.assertTrue(self._ready())


class ChainReadinessSourceContractTests(SimpleTestCase):
    """Pin the STRUCTURE, so a future refactor cannot quietly undo the fix."""

    def _source(self):
        import inspect

        return inspect.getsource(I)

    def test_ask_rag_is_a_wrapper_with_a_finally(self):
        src = self._source()
        self.assertIn("def _ask_rag_impl(", src,
                      "el cuerpo debe vivir en _ask_rag_impl")
        head = src.split("def _ask_rag_impl(")[0]
        wrapper = head.split("def ask_rag(")[-1]
        self.assertIn("finally:", wrapper,
                      "ask_rag DEBE liberar la cadena en un finally")
        self.assertIn("rag_chain_ready", wrapper)

    def test_the_finally_is_unconditional(self):
        """No `if` may guard the release — that reintroduces the outage."""
        src = self._source()
        wrapper = src.split("def _ask_rag_impl(")[0].split("def ask_rag(")[-1]
        tail = wrapper.split("finally:", 1)[1]
        release = [ln.strip() for ln in tail.splitlines()
                   if "rag_chain_ready" in ln]
        self.assertTrue(release, "el finally debe restaurar rag_chain_ready")
        for line in release:
            self.assertTrue(
                line.startswith("global_state.set_state("),
                "la liberación debe ser incondicional, no dentro de un if: %r" % line,
            )
        self.assertNotIn("if ", tail.split("global_state.set_state(")[0],
                         "nada debe condicionar la liberación de la cadena")


class ChainBuildLatchTests(SimpleTestCase):
    """The REBUILD path — this is what actually caused the outage.

    ``ask_rag`` had been hardened long ago; ``setup_llm`` /
    ``setup_llm_with_context`` never were. They lowered the same process-global
    latch on entry and raised it only on SUCCESS, so a failed or raising
    rebuild stranded it. And because the latch is process-global while the
    rebuild lock is per-connection, refreshing the browser inherited the dead
    latch — which is why only killing the process fixed it.
    """

    def setUp(self):
        from agent.rag import factory as F

        self.F = F
        F.global_state.set_state(READY, False)

    def _ready(self):
        return self.F.global_state.get_state(READY)

    def test_setup_llm_releases_the_latch_when_the_build_RAISES(self):
        F = self.F
        original = F._setup_llm_impl

        def _boom(*a, **k):
            F.global_state.set_state(READY, False)     # what the real impl does
            raise RuntimeError("build reventó")

        F._setup_llm_impl = _boom
        try:
            with self.assertRaises(RuntimeError):
                F.setup_llm()
            self.assertTrue(self._ready(),
                            "un build que truena NO debe dejar el chat muerto")
        finally:
            F._setup_llm_impl = original

    def test_setup_llm_releases_the_latch_when_the_build_returns_None(self):
        F = self.F
        original = F._setup_llm_impl

        def _fails(*a, **k):
            F.global_state.set_state(READY, False)
            return None                                 # the `return None` paths

        F._setup_llm_impl = _fails
        try:
            self.assertIsNone(F.setup_llm())
            self.assertTrue(self._ready(),
                            "un build fallido debe dejar el carril ABIERTO para reintentar")
        finally:
            F._setup_llm_impl = original

    def test_setup_llm_with_context_releases_the_latch_when_it_RAISES(self):
        F = self.F
        original = F._setup_llm_with_context_impl

        def _boom(*a, **k):
            F.global_state.set_state(READY, False)
            raise RuntimeError("build contextual reventó")

        F._setup_llm_with_context_impl = _boom
        try:
            with self.assertRaises(RuntimeError):
                F.setup_llm_with_context("some/path")
            self.assertTrue(self._ready())
        finally:
            F._setup_llm_with_context_impl = original

    def test_both_builders_are_wrappers_with_an_unconditional_finally(self):
        import inspect

        src = inspect.getsource(self.F)
        for public, impl in (("setup_llm", "_setup_llm_impl"),
                             ("setup_llm_with_context", "_setup_llm_with_context_impl")):
            self.assertIn("def %s(" % impl, src,
                          "%s debe delegar en %s" % (public, impl))
            wrapper = src.split("def %s(" % impl)[0].split("\ndef %s(" % public)[-1]
            self.assertIn("finally:", wrapper,
                          "%s DEBE liberar la cadena en un finally" % public)
            self.assertIn("rag_chain_ready", wrapper)

    def test_prompt_only_fallback_returns_None_instead_of_raising(self):
        """The last-resort builder must degrade, never explode."""
        F = self.F
        original = F._build_prompt_only_chain_impl

        def _boom(*a, **k):
            raise RuntimeError("fallback reventó")

        F._build_prompt_only_chain_impl = _boom
        try:
            self.assertIsNone(F.build_prompt_only_chain({}, "plantilla"))
        finally:
            F._build_prompt_only_chain_impl = original


class RebuildIsNonDestructiveTests(SimpleTestCase):
    """A failed self-heal must not destroy a chain that was working."""

    def test_consumer_never_nulls_the_chain_on_failure(self):
        import inspect

        from agent import consumers

        src = inspect.getsource(consumers)

        # Scope to the two REBUILD methods only. `self.rag_chain = None` is
        # legitimate in __init__ (initial value) and appears in a comment.
        rebuilds = {
            "setup_rag_chain":
                src.split("async def setup_rag_chain")[1]
                   .split("async def setup_contextual_rag_chain")[0],
            "setup_contextual_rag_chain":
                src.split("async def setup_contextual_rag_chain")[1]
                   .split("async def heartbeat")[0],
        }
        for name, body in rebuilds.items():
            self.assertNotIn(
                "self.rag_chain = None", body,
                "%s: un rebuild fallido NO debe borrar la cadena que ya servía "
                "— eso es lo que hacía que el auto-remedio dejara el chat PEOR" % name,
            )
            self.assertIn("_prev_chain", body,
                          "%s debe conservar la cadena anterior" % name)
            self.assertIn(
                "global_state.set_state('rag_chain_ready', self.rag_chain is not None)",
                body,
                "%s debe reafirmar el latch con la verdad en su finally" % name,
            )


if __name__ == "__main__":
    unittest.main()
