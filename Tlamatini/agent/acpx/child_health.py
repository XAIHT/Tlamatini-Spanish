# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""
ACPX child-health classification — did the external CLI actually DELIVER?

Why this exists
---------------
An ACP child can exit **0** and still have done nothing the user asked for.
Measured live on 2026-09-07 (Angela's SETI research run):

    $ claude -p "Use WebSearch to find ..."
    Angela, the web search was blocked — permission wasn't granted, so I
    can't look up the current Python version.
    $ echo $?
    0

ACPX reported that turn as a SUCCESS, the Exec Report stamped it green, and
the orchestrating LLM went on believing it had research in hand. That is the
same *silent, plausible, WRONG deliverable* class as the missing-images PDFer
bug and the LaTeXer linter verdict: an exit code is one bit, and one bit
cannot describe what a coding agent did.

The same run also produced four **noisy** failures that ``acp_doctor`` had
already declared healthy, because ``--version`` answers fine on a CLI that is
broken everywhere else:

    gemini   -> Error authenticating: IneligibleTierError ...
    codex    -> Error loading config.toml: unknown variant `default`
    claude   -> Credit balance is too low
    copilot  -> (no output at all)

This module is the ONE place that decides "delivered vs not", and it is used
by BOTH callers so they can never drift:

    * ``runtime.AcpSession._oneshot_send_turn`` — stamps every finished turn.
    * ``runtime.AcpxRuntime.readiness_probe``   — powers ``acp_doctor(deep)``.

Contract (do NOT weaken)
------------------------
1. **A long, real answer is NEVER reclassified as a failure.** Only short or
   empty output is even examined for refusal markers. A 3 KB research briefing
   that happens to contain the words "rate limit" stays a success. This is the
   same anchoring discipline the self-healing status matcher learned the hard
   way — a substring match on a long answer creates false failures, and a
   false failure is worse than the missed one it replaces.
2. **Markers are read from the HEAD of the output only.** A refusal announces
   itself immediately; it does not bury the reason on line 90.
3. **Chrome is not a deliverable** — but SHORT IS NOT CHROME. Output only
   counts as chrome when it is both long enough to be more than a terse reply
   AND almost letter-free, i.e. a TUI that painted a box-drawing frame and no
   words. A 7-character "PEER_OK" is a complete, correct answer.
4. **FAIL-OPEN**: anything unrecognised is treated as DELIVERED. This module
   exists to stop ACPX lying about failure, not to invent new ones, and it
   must never raise into a caller.
5. Stdlib-only; imports nothing from ``agent.*`` so it behaves identically
   frozen and from source, and can never create an import cycle.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# A refusal is short. A deliverable is not. Output longer than this is
# accepted as real work without ever being scanned for refusal markers.
SHORT_ANSWER_CHARS = 1200

# Refusal markers must appear this early — a real reason leads, it does not
# hide behind 400 characters of preamble.
HEAD_CHARS = 400

# "Decorative" output: plenty of characters, almost no letters -- a TUI that
# painted a box frame and nothing else (kimi / copilot on the tui-repl
# transport did exactly this). BOTH conditions are required, and that pairing
# is load-bearing: an early draft tested the letter count ALONE and classified
# a perfectly good 7-character answer ("PEER_OK") as NO_OUTPUT. Short is not
# the same as empty, and a false failure is the one thing this module must
# never manufacture.
MIN_ALNUM_CHARS = 40
DECORATIVE_MIN_CHARS = 60

# ── The closed vocabulary of non-delivery codes ──────────────────────
#   Every code below means: the requested work did NOT happen.
PERMISSION_BLOCKED = "PERMISSION_BLOCKED"
WORKSPACE_NOT_TRUSTED = "WORKSPACE_NOT_TRUSTED"
NO_CREDIT = "NO_CREDIT"
USAGE_LIMIT = "USAGE_LIMIT"
AUTH_FAILED = "AUTH_FAILED"
CONFIG_INVALID = "CONFIG_INVALID"
UPSTREAM_ERROR = "UPSTREAM_ERROR"
NO_OUTPUT = "NO_OUTPUT"
CHILD_ERROR = "CHILD_ERROR"
DELIVERED = "DELIVERED"

NON_DELIVERY_CODES = frozenset({
    PERMISSION_BLOCKED, WORKSPACE_NOT_TRUSTED, NO_CREDIT, USAGE_LIMIT,
    AUTH_FAILED, CONFIG_INVALID, UPSTREAM_ERROR, NO_OUTPUT, CHILD_ERROR,
})

# De lo MAS especifico a lo mas general. Cada entrada: (code, razon humana,
# patrones). Los patrones se comparan sin distinguir mayusculas contra la
# CABEZA de la salida.
#
# ── POR QUE ESTA TABLA TIENE PATRONES EN LOS DOS IDIOMAS (Angela, 2026-09-08) ─
#
# El `code` es canal de MAQUINA y se queda en ingles, byte-exacto: lo leen
# `NON_DELIVERY_CODES`, el envelope de `acp_doctor` y las pruebas de los dos
# arboles. La RAZON si la lee Angela, asi que va en español.
#
# Los PATRONES son otra cosa: son la salida del CLI EXTERNO (claude / gemini /
# codex / cursor / qwen), que NO es nuestro y puede hablar el idioma que se le
# antoje. Por eso se conservan TODOS los patrones en ingles Y se agregan sus
# equivalentes en español, con y sin acento — un `límite de uso` que no casara
# con `usage limit` haria que el clasificador dijera DELIVERED sobre una
# negativa, y el Exec Report la pintaria VERDE. Ese es exactamente el bug de la
# corrida SETI del 2026-09-07 que este archivo existe para matar, nada mas que
# en español. Un patron de mas no cuesta nada; uno de menos cuesta una mentira.
_SIGNATURES: List[Tuple[str, str, Tuple[str, ...]]] = [
    (WORKSPACE_NOT_TRUSTED,
     "el directorio de trabajo del hijo no es de confianza, asi que se ignoro su archivo de permisos",
     ("has not been trusted", "trust dialog",
      "not inside a trusted directory",
      # español
      "no es de confianza", "no confiable",
      "directorio no confiable", "carpeta no confiable")),
    (NO_CREDIT,
     "la cuenta detras de este CLI se quedo sin credito",
     ("credit balance is too low", "insufficient credit",
      "insufficient_quota", "billing",
      # español
      "saldo insuficiente", "sin credito", "sin crédito",
      "credito insuficiente", "crédito insuficiente",
      "saldo es demasiado bajo", "facturacion", "facturación")),
    (USAGE_LIMIT,
     "la cuenta topo un limite de plan / uso / frecuencia",
     ("hit your session limit", "session limit", "usage limit",
      "rate limit", "rate_limit", "quota exceeded", "too many requests",
      # español
      "limite de uso", "límite de uso",
      "limite de sesion", "límite de sesión",
      "limite de frecuencia", "límite de frecuencia",
      "cuota excedida", "cuota agotada",
      "demasiadas solicitudes", "demasiadas peticiones")),
    (PERMISSION_BLOCKED,
     "el hijo se detuvo en su propio dialogo de permiso y no hizo el trabajo",
     ("permission wasn't granted", "permission was not granted",
      "awaiting your permission", "hasn't been granted permission",
      "has not been granted permission", "was blocked because",
      "search was blocked", "need from you: approve",
      "please approve", "run `/permissions`", "/permissions",
      "requires permission", "permission denied for tool",
      # español
      "no se concedio el permiso", "no se concedió el permiso",
      "no se otorgo el permiso", "no se otorgó el permiso",
      "esperando tu permiso", "requiere permiso", "necesita permiso",
      "permiso denegado", "fue bloqueada porque", "fue bloqueado porque",
      "la busqueda fue bloqueada", "la búsqueda fue bloqueada",
      "necesito que apruebes", "por favor aprueba")),
    (AUTH_FAILED,
     "el CLI no pudo autenticarse",
     ("error authenticating", "ineligibletiererror", "not authenticated",
      "api key is invalid", "invalid api key", "invalid_api_key",
      "no auth type is selected", "please log in", "login required",
      "unauthorized", "authentication failed", "oauth",
      # español
      "error de autenticacion", "error de autenticación",
      "autenticacion fallida", "autenticación fallida",
      "no autenticado", "no autorizado",
      "clave de api invalida", "clave de api inválida",
      "inicia sesion", "inicia sesión", "sesion requerida")),
    (CONFIG_INVALID,
     "el CLI se nego a arrancar porque su propio archivo de configuracion es invalido",
     ("error loading config", "unknown variant", "invalid configuration",
      "failed to parse config", "config error",
      # español
      "error al cargar la configuracion", "error al cargar la configuración",
      "configuracion invalida", "configuración inválida",
      "error de configuracion", "error de configuración")),
    (UPSTREAM_ERROR,
     "el proveedor del modelo devolvio un error de su lado",
     ("server had an error", "server_error", "internal server error",
      "error code: 500", "error code: 502", "error code: 503",
      "service unavailable", "overloaded",
      # español
      "error interno del servidor", "error del servidor",
      "servicio no disponible", "sobrecargado", "saturado")),
]


@dataclass(frozen=True)
class ChildVerdict:
    """Typed answer to: did this ACP child actually deliver the work?"""
    delivered: bool
    code: str
    reason: str
    evidence: str = ""

    def as_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"delivered": self.delivered, "code": self.code}
        if not self.delivered:
            out["failure_reason"] = self.reason
            if self.evidence:
                out["failure_evidence"] = self.evidence
        return out


_DELIVERED = ChildVerdict(True, DELIVERED, "")


def _alnum_count(text: str) -> int:
    return sum(1 for ch in text if ch.isalnum())


def _is_decorative(text: str) -> bool:
    """True when the child emitted chrome instead of an answer.

    Requires BOTH "long enough to be more than a terse reply" AND "almost no
    letters". A short answer is never decorative -- see MIN_ALNUM_CHARS.
    """
    return (len(text) >= DECORATIVE_MIN_CHARS
            and _alnum_count(text) < MIN_ALNUM_CHARS)


def _match_signature(head: str) -> Optional[Tuple[str, str, str]]:
    """Return (code, reason, matched_marker) for the first signature hit."""
    low = head.lower()
    for code, reason, patterns in _SIGNATURES:
        for marker in patterns:
            if marker in low:
                return (code, reason, marker)
    return None


def _first_meaningful_line(text: str, limit: int = 180) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and _alnum_count(stripped) >= 3:
            return stripped[:limit]
    return text.strip()[:limit]


def classify_child_output(stdout: Any, stderr: Any = "",
                          exit_code: Any = 0) -> ChildVerdict:
    """Decide whether an ACP child delivered real work. NEVER raises.

    See the module docstring for the contract. The short version: only short,
    empty or letter-less output is ever suspected; everything else is work.
    """
    try:
        out = (stdout or "") if isinstance(stdout, str) else str(stdout or "")
        err = (stderr or "") if isinstance(stderr, str) else str(stderr or "")
        try:
            rc = int(exit_code)
        except (TypeError, ValueError):
            rc = 0

        out_stripped = out.strip()
        err_stripped = err.strip()

        # ── Rule 1 ── A substantial answer is work. Never second-guessed.
        if len(out_stripped) >= SHORT_ANSWER_CHARS and \
                _alnum_count(out_stripped) >= MIN_ALNUM_CHARS:
            return _DELIVERED

        # ── Rule 2 ── Nothing legible came back at all: either literally
        # empty, or pure chrome (a TUI frame with no words in it).
        if not out_stripped or _is_decorative(out_stripped):
            hit = _match_signature(err_stripped[:HEAD_CHARS]) if err_stripped else None
            if hit:
                code, reason, marker = hit
                return ChildVerdict(False, code, reason,
                                    _first_meaningful_line(err_stripped))
            if err_stripped:
                return ChildVerdict(
                    False, CHILD_ERROR,
                    "el hijo no produjo una respuesta usable y escribio en stderr",
                    _first_meaningful_line(err_stripped))
            return ChildVerdict(
                False, NO_OUTPUT,
                "el hijo no produjo NADA de salida "
                "(un transport TUI que nunca vacio el buffer, o un crash mudo)",
                "")

        # ── Rule 3 ── Short but legible: this is where refusals live.
        hit = _match_signature(out_stripped[:HEAD_CHARS])
        if hit:
            code, reason, marker = hit
            return ChildVerdict(False, code, reason,
                                _first_meaningful_line(out_stripped))
        if err_stripped:
            hit = _match_signature(err_stripped[:HEAD_CHARS])
            if hit:
                code, reason, marker = hit
                return ChildVerdict(False, code, reason,
                                    _first_meaningful_line(err_stripped))

        # ── Rule 4 ── Short, legible, no known refusal, but the process
        # itself failed. Trust the exit code here — there is no deliverable
        # large enough to contradict it.
        if rc != 0:
            return ChildVerdict(
                False, CHILD_ERROR,
                "el hijo salio con %s sin producir una respuesta usable" % rc,
                _first_meaningful_line(out_stripped or err_stripped))

        # ── Rule 5 ── FAIL-OPEN. A short clean answer is still an answer.
        return _DELIVERED
    except Exception:                                   # pragma: no cover
        # A health classifier that can break the chat path is worse than the
        # mislabelled row it was written to fix.
        return _DELIVERED


def summarize_for_doctor(verdict: ChildVerdict) -> Dict[str, Any]:
    """Shape a ChildVerdict for the per-agent rows of ``acp_doctor(deep)``."""
    return {
        "ready": bool(verdict.delivered),
        "code": verdict.code,
        "reason": "" if verdict.delivered else verdict.reason,
        "evidence": "" if verdict.delivered else verdict.evidence,
    }


__all__ = [
    "ChildVerdict",
    "classify_child_output",
    "summarize_for_doctor",
    "NON_DELIVERY_CODES",
    "SHORT_ANSWER_CHARS",
    "HEAD_CHARS",
    "MIN_ALNUM_CHARS",
    "DELIVERED",
    "PERMISSION_BLOCKED",
    "WORKSPACE_NOT_TRUSTED",
    "NO_CREDIT",
    "USAGE_LIMIT",
    "AUTH_FAILED",
    "CONFIG_INVALID",
    "UPSTREAM_ERROR",
    "NO_OUTPUT",
    "CHILD_ERROR",
]
