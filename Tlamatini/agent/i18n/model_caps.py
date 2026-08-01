"""Per-model Spanish competence: measured, cached, and continuously corrected.

    NEPANTLA · Stage 0 · the capability gate

WHAT THIS MODULE DECIDES
========================
Before the scorer sees a Spanish request, something must decide whether to help
the model or leave it alone. Helping is not free in the sense that matters:
appending canonical English keys to a Spanish request raises the right tool's
score for a model whose Spanish is thin, and *lowers signal-to-noise* for a
model that already understood the sentence. Both directions are correctness
failures. This module answers one question - **does THIS model need help?** -
and it answers it from evidence.

WHY THERE IS NOTHING TO LOOK UP
===============================
The obvious design is a lookup: ask the provider which languages the model
supports. That design is impossible. Verified against primary sources
(2026-07-28), no provider exposes language support programmatically:

    Anthropic  GET /v1/models   id, display_name, max_tokens, capabilities{...}
    OpenAI     GET /v1/models   id, object, created, owned_by - the whole schema
    Google     models.list      name, tokenLimits, supportedGenerationMethods
    Ollama     /api/show        capabilities[] = completion|tools|vision|...
    OpenRouter /api/v1/models   the richest schema in existence

Not one carries a language field. Ollama's ``capabilities`` enum is real and
useful - and contains no language member, by design.

The single structured language declaration anywhere in the stack is the GGUF
key ``general.languages``. It is optional, author-supplied, and **wrong where
present**: measured across 15 real model files it appears in 8, is ABSENT from
qwen3, gemma3, gemma-2-9b, Mistral-7B-v0.3 and Llama-2 (all strongly
multilingual), and declares exactly ``["en"]`` for Qwen2.5-7B-Instruct and
Phi-4. Absence and ``["en"]`` are equally worthless as evidence against Spanish.

Worse, reading it through Ollama INVERTS the evidence. ``server/routes.go``
blanks any array longer than 5 entries unless ``verbose: true`` is passed, so
Llama 3.1's real 8-language list *containing* ``es`` reads as ``[]`` while
Phi-4's misleading 1-element ``["en"]`` survives intact. A naive reader
concludes "no languages" for the Spanish-capable model and "English only" for
the one that is not. This module therefore reads no language metadata at all.

WHY TOKENIZER FERTILITY IS NOT USED
===================================
The attractive cheap measurement is the "token tax": tokens for Spanish over
tokens for equivalent English. It is genuinely measurable - Ollama returns
``prompt_eval_count`` - and it is genuinely useless here.

Measured on this project's own models (2026-07-28), Spanish-per-character
efficiency spanned 0.74-0.83 across seven models, including 0.76 for
``glm-5.2:cloud``, a 756B frontier model with excellent Spanish. Any threshold
separating that band mislabels the best model available.

The literature explains why. Fertility predicts accuracy where the range is
huge - 10 LLMs x 16 African languages give regression slopes of -0.08 to -0.18
accuracy per additional token/word (arXiv 2509.05486). It fails where the range
is narrow: a Ukrainian zero-shot study reports rho = -0.43, p = 0.34, NOT
significant (arXiv 2605.14890). Spanish is decisively the narrow case: across
24 European languages and six tokenizers, English averages 1.23 tokens/word and
Spanish 1.46 - an 8-29% band (arXiv 2605.24718). There is also a structural
ceiling: every model in a family shares one tokenizer and therefore one
fertility number, while differing enormously in Spanish output.

Two counterexamples finish it. Phi-4 has a 100,352-entry vocabulary and
declares itself English-only; Mistral-7B-v0.3 has 32,768 and handles Spanish.
The metric orders them backwards.

Fertility measures COST. Keep it for context budgeting. It does not gate here.

THE RESOLUTION LADDER
=====================
    L0  SEED       a name-shaped prior. NOT an authority - see below.
    L1  PROBE      four graded tasks, once per identity, cached forever.
    L2  OBSERVE    the same grader run free on real production responses.

L1 is the authority. L0 only orders the unknown. L2 can DEMOTE a standing
verdict but never promote one - promotion requires evidence, and a run of
easy Spanish answers is not evidence.

THE SEED IS NOT AN AUTHORITY  (this is the correction that matters)
===================================================================
An earlier revision let a regex over the model id decide the tier outright.
That is the hardcoded name table wearing a different hat, and it is exactly
what the evidence above forbids. The seed now obeys three hard rules,
each pinned by a test:

    1. A probe verdict ALWAYS overrides the seed.
    2. The seed may never produce WEAK. Demotion requires measurement,
       because a false "cannot do Spanish" is unrecoverable - the model is
       never tried again, and the user sees silent degradation with no error.
    3. Absence from the seed table means UNKNOWN, never "no Spanish".

FAIL-OPEN, AND WHY IT POINTS THIS WAY
=====================================
Every failure resolves to ASSIST (the safe middle), never to "fluent, leave it
alone". The asymmetry is the argument: a wrong ASSIST costs some hint tokens
and slightly noisier scoring, and is corrected by the next probe. A wrong
FLUENT silently withholds the help a weak model needed, produces "no tool
matched", and looks to the user like Tlamatini simply failing in Spanish.

Nothing in this module raises into a caller, and nothing blocks a request.

REPRODUCIBILITY
===============
Probes run at temperature 0 with a fixed seed where the transport supports it,
and every grader is a pure function of the response string - no model judges
another model, so a verdict cannot drift between runs. The RAW per-check
features are persisted alongside the verdict so thresholds can be retuned
later without re-probing anything.

THIS MODULE NEVER CALLS AN LLM
==============================
``run_probe`` takes an ``invoke(prompt) -> str`` callable. The module is
stdlib-only, importable from a pool subprocess, testable with a fake, and
structurally incapable of stalling the application.
"""

from __future__ import annotations

import json
import os
import re
import sys
import threading
import unicodedata

__all__ = [
    "FLUENT", "ASSIST", "WEAK", "UNKNOWN",
    "PROBE_VERSION",
    "identity", "seed_tier", "tier_for", "policy_for", "assist_enabled_for",
    "profile", "known", "record", "invalidate", "cache_path",
    "run_probe", "probe_in_background", "PROBE_BATTERY",
    "is_embedder", "active_model",
    "observe", "grade_response",
]

# ---------------------------------------------------------------------------
# Tiers.  ASSIST replaces the former "partial": the name should say what the
# system DOES, not how good the model is thought to be.
# ---------------------------------------------------------------------------
FLUENT = "fluent"     # measured competent -> leave the user's words alone
ASSIST = "assist"     # help with canonical English keys
WEAK = "weak"         # help, and boost the English hints
UNKNOWN = "unknown"   # no evidence -> behaves exactly as ASSIST

# tier -> (fold, expand, boost).  Folding is free and always on.
_POLICY = {
    FLUENT:  (True, False, False),
    ASSIST:  (True, True,  False),
    WEAK:    (True, True,  True),
    UNKNOWN: (True, True,  False),   # identical to ASSIST, deliberately
}

# Bump when the battery or the graders change; a verdict from an older version
# is treated as absent rather than trusted, because its features are not
# comparable.
PROBE_VERSION = 2

# ---------------------------------------------------------------------------
# L0 - the SEED.  Ordering only.  Cannot emit WEAK.  Overridden by any probe.
#
# This exists for exactly one purpose: to avoid assisting a model that is
# almost certainly fluent during the seconds before its first probe returns.
# It is not evidence and it is not consulted once a probe exists.
# ---------------------------------------------------------------------------
_SEED_FLUENT = (
    r"^glm[-_.]?[5-9]", r"^qwen[-_.]?([3-9]|\d{2})", r"^gemma[-_.]?([4-9]|\d{2})",
    r"^claude", r"^gpt[-_.]?([4-9]|\d{2})", r"^gpt-oss", r"^o[1-9](\b|[-_.])",
    r"^mixtral", r"^mistral[-_.]?large", r"^command[-_.]?r",
    r"^deepseek[-_.]?(v[3-9]|r[1-9])", r"^llama[-_.]?([4-9]|\d{2})",
    r"^kimi", r"^minimax",
)
_SEED_RE = tuple(re.compile(p, re.I) for p in _SEED_FLUENT)

# Embedding models never produce prose. Probing them is meaningless and
# /api/generate rejects them outright, so they are excluded from the ladder.
_EMBEDDER_RE = re.compile(r"embed|^nomic", re.I)

# ---------------------------------------------------------------------------
# The graders.  Pure functions of the response string.
# ---------------------------------------------------------------------------
_ES_MARKERS = (
    " el ", " la ", " los ", " las ", " un ", " una ", " de ", " del ",
    " que ", " con ", " para ", " por ", " en ", " y ", " es ", " son ",
    " se ", " su ", " lo ", " al ",
)
_EN_MARKERS = (
    " the ", " of ", " and ", " to ", " is ", " are ", " it ", " that ",
    " this ", " with ", " for ", " you ", " your ",
)
_ACCENTED = re.compile("[áéíóúñü]")
_MOJIBAKE = re.compile("Ã[ -¿]|�")
# Over-translations of the two terms Angela named explicitly.
_OVERTRANSLATED = ("contenedor", "contenedores", "vaina", "vainas")


def _spanish_ratio(text: str) -> float:
    """Share of language-marker hits that are Spanish rather than English."""
    t = " " + re.sub(r"\s+", " ", (text or "").lower().strip()) + " "
    es = sum(t.count(m) for m in _ES_MARKERS)
    en = sum(t.count(m) for m in _EN_MARKERS)
    if es + en == 0:
        return 0.5          # too short to tell - neither credit nor blame
    return es / float(es + en)


def _g_language(answer: str, _expect=None) -> float:
    """Asked in Spanish - did it ANSWER in Spanish, or drift to English?

    This is the single most common real failure and no metadata field on earth
    detects it.
    """
    r = _spanish_ratio(answer)
    if r >= 0.75:
        return 1.0
    if r >= 0.55:
        return 0.5
    return 0.0


def _g_register(answer: str, _expect=None) -> float:
    """Angela's rule: verbs Spanish, American technical nouns English.

    The prompt explicitly instructs it, so this grades INSTRUCTION-FOLLOWING
    in Spanish, not merely vocabulary.
    """
    low = (answer or "").lower()
    if any(w in low for w in _OVERTRANSLATED):
        return 0.0
    kept = sum(1 for w in ("container", "pod") if w in low)
    if kept >= 2:
        return 1.0
    if kept == 1:
        return 0.75
    return 0.5          # dodged the question - unproven, not failed


def _g_semantic(answer: str, expect: str = "") -> float:
    """Spanish intent -> the correct tool name.  This IS the job.

    Graded strictly: naming the right tool AND no other tool. A model that
    lists all four candidates has not selected anything.
    """
    a = (answer or "").lower()
    if not expect:
        return 0.5
    others = [t for t in ("chat_agent_deleter", "chat_agent_emailer",
                          "chat_agent_gitter", "chat_agent_shoter")
              if t != expect.lower()]
    if expect.lower() not in a:
        return 0.0
    return 0.5 if any(o in a for o in others) else 1.0


def _g_charset(answer: str, _expect=None) -> float:
    """Do the diacritics survive the round trip, or come back as mojibake?

    Tests the PIPE, not the intelligence: a copy task.
    """
    a = answer or ""
    if not a.strip():
        return 0.0
    if _MOJIBAKE.search(a):
        return 0.0
    hits = len(_ACCENTED.findall(a))
    if hits >= 4:
        return 1.0
    if hits >= 1:
        return 0.75
    return 0.25         # copied it flat - real loss, but not corruption


PROBE_BATTERY: tuple[dict, ...] = (
    {
        "key": "language",
        "weight": 1.0,
        "expect": "",
        "grade": _g_language,
        "prompt": "Responde en espanol, en una sola frase corta: "
                  "¿que hace el comando 'git push'?",
    },
    {
        "key": "register",
        "weight": 1.5,
        "expect": "",
        "grade": _g_register,
        "prompt": "En espanol de Mexico, explica en una frase corta que es un "
                  "Docker container y que es un Kubernetes pod. Los terminos "
                  "tecnicos en ingles se quedan en ingles.",
    },
    {
        "key": "semantic",
        "weight": 2.0,
        "expect": "chat_agent_deleter",
        "grade": _g_semantic,
        "prompt": "Tienes estas tools: chat_agent_deleter, chat_agent_emailer, "
                  "chat_agent_gitter, chat_agent_shoter. El usuario dice: "
                  "'borra los archivos viejos de la carpeta de logs'. "
                  "Responde SOLO con el nombre exacto de la tool correcta.",
    },
    {
        "key": "charset",
        "weight": 1.0,
        "expect": "",
        "grade": _g_charset,
        "prompt": "Escribe exactamente esta frase, sin cambiar nada: "
                  "El niño pequeño compró un pingüino en España.",
    },
)

# Verdict thresholds. Deliberately generous: WEAK requires real failure, not
# merely an unimpressive score, because demotion is the unrecoverable
# direction. UNVALIDATED against any external Spanish benchmark - they encode
# the failure modes above, not a correlation with MMLU-es.
_FLUENT_AT = 0.85
_ASSIST_AT = 0.45

# L2 - passive verification. A standing verdict is demoted only on a
# sustained failure rate over a meaningful sample, never on one bad answer.
_OBSERVE_MIN_SAMPLE = 12
_OBSERVE_DEMOTE_BELOW = 0.60
_OBSERVE_WINDOW = 200

_lock = threading.RLock()
_cache: dict | None = None
_probing: set = set()
_cfg_cache: str | None = None
_cfg_stamp: tuple | None = None


# ---------------------------------------------------------------------------
# Identity.  The cache key.
# ---------------------------------------------------------------------------
def identity(model_name: str, digest: str = "") -> str:
    """A key that changes if and only if the artifact changes.

    For a LOCAL model the GGUF blob digest is exact: it moves when the weights
    or the tokenizer move, and not otherwise. For a cloud model there is no
    digest, so the EXACT model id is used - including the ``:cloud`` suffix and
    any size tag.

    Never the family name. ``glm-5.2:cloud`` and a hypothetical local
    ``glm-5.2`` are different artifacts served by different stacks and must not
    share a verdict; an earlier revision collapsed both to ``glm-5.2``.
    """
    if digest:
        d = str(digest).strip().lower()
        if d.startswith("sha256:"):
            d = d.split(":", 1)[1]
        if d:
            return "sha256:" + d[:32]
    n = unicodedata.normalize("NFKC", str(model_name or "")).strip().lower()
    return n.rsplit("/", 1)[-1]          # drop only the registry namespace


def active_model() -> str:
    """The model the Multi-Turn executor is actually configured to use.

    This is what makes the gate live without threading a model name up through
    the planner and executor signatures. ``normalize_request`` serves the
    tool-selection path, and that path runs on ``unified_agent_model``.

    Read fresh-ish from config.json with an mtime cache, so changing the model
    in the GUI takes effect without a restart. Fail-open to "" - an unknown
    model resolves to UNKNOWN, which behaves exactly as ASSIST.
    """
    global _cfg_cache, _cfg_stamp
    try:
        path = _config_path()
        try:
            st = os.stat(path)
            stamp = (st.st_mtime_ns, st.st_size)
        except OSError:
            return ""
        if _cfg_cache is not None and stamp == _cfg_stamp:
            return _cfg_cache
        with open(path, "r", encoding="utf-8-sig") as fh:
            raw = json.load(fh)
        model = str(raw.get("unified_agent_model") or "").strip()
        with _lock:
            _cfg_cache, _cfg_stamp = model, stamp
        return model
    except Exception:
        return ""


def _config_path() -> str:
    env = (os.environ.get("CONFIG_PATH") or "").strip()
    if env:
        return env
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "config.json")
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, "config.json")


def is_embedder(model_name: str) -> bool:
    return bool(_EMBEDDER_RE.search(str(model_name or "")))


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
def cache_path() -> str:
    env = (os.environ.get("CONFIG_PATH") or "").strip()
    if env:
        return os.path.join(os.path.dirname(env), "model_caps.json")
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "model_caps.json")
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, "model_caps.json")


def _load() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    data: dict = {}
    try:
        with open(cache_path(), "r", encoding="utf-8-sig") as fh:
            raw = json.load(fh)
        if isinstance(raw, dict):
            data = {str(k): v for k, v in raw.items() if isinstance(v, dict)}
    except Exception:
        data = {}
    _cache = data
    return data


def _save(data: dict) -> None:
    """Atomic-ish write. A crashed write must not corrupt a good verdict."""
    path = cache_path()
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1, sort_keys=True)
        os.replace(tmp, path)
    except Exception:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass


def invalidate() -> None:
    global _cache
    with _lock:
        _cache = None


def known(model_name: str, digest: str = "") -> dict | None:
    """The persisted record for this identity, if it is still current."""
    try:
        rec = _load().get(identity(model_name, digest))
        if not rec:
            return None
        if int(rec.get("probe_version", 0)) != PROBE_VERSION:
            return None          # stale battery -> features incomparable
        return rec
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------
def seed_tier(model_name: str) -> str:
    """L0. Returns FLUENT or UNKNOWN. **Never WEAK, never ASSIST-by-name.**

    Emitting WEAK here would let a regex demote a model without evidence,
    which is the unrecoverable direction.
    """
    n = identity(model_name)
    if not n or n.startswith("sha256:"):
        return UNKNOWN
    for rx in _SEED_RE:
        try:
            if rx.search(n):
                return FLUENT
        except Exception:
            continue
    return UNKNOWN


def tier_for(model_name: str, digest: str = "") -> str:
    """Probe verdict wins; the seed only fills the gap before one exists."""
    try:
        rec = known(model_name, digest)
        if rec:
            t = rec.get("effective_tier") or rec.get("tier")
            if t in _POLICY:
                return t
        return seed_tier(model_name)
    except Exception:
        return UNKNOWN


def policy_for(model_name: str, digest: str = "") -> dict:
    """What the ladder should do. Never raises, never blocks, never probes."""
    try:
        rec = known(model_name, digest)
        tier = tier_for(model_name, digest)
        fold, expand, boost = _POLICY.get(tier, _POLICY[UNKNOWN])
        if rec:
            source = "observed" if rec.get("demoted") else "probe"
        elif seed_tier(model_name) != UNKNOWN:
            source = "seed"
        else:
            source = "default"
        return {
            "identity": identity(model_name, digest),
            "tier": tier,
            "fold": fold,
            "expand": expand,
            "boost_english": boost,
            "source": source,
            "authoritative": bool(rec),
        }
    except Exception:
        fold, expand, boost = _POLICY[UNKNOWN]
        return {"identity": "", "tier": UNKNOWN, "fold": fold,
                "expand": expand, "boost_english": boost,
                "source": "error", "authoritative": False}


def assist_enabled_for(model_name: str, digest: str = "") -> bool:
    """The one question ``normalize_request`` needs answered."""
    return bool(policy_for(model_name, digest).get("expand", True))


def profile(model_name: str, digest: str = "") -> dict:
    """Everything known about this identity - for the operator, not the gate."""
    pol = policy_for(model_name, digest)
    rec = known(model_name, digest) or {}
    pol["seed"] = seed_tier(model_name)
    pol["probe"] = {k: rec.get(k) for k in
                    ("tier", "score", "checks", "probe_version")} if rec else None
    pol["observations"] = rec.get("observations")
    return pol


# ---------------------------------------------------------------------------
# L1 - the probe
# ---------------------------------------------------------------------------
def _tier_from_score(score: float) -> str:
    if score >= _FLUENT_AT:
        return FLUENT
    if score >= _ASSIST_AT:
        return ASSIST
    return WEAK


def run_probe(model_name: str, invoke) -> dict:
    """Run the battery and return a verdict. Never raises.

    ``invoke`` is any callable taking a prompt and returning the answer.
    Raw per-check features are kept so thresholds stay retunable.
    """
    checks: dict = {}
    total = 0.0
    weight = 0.0
    errors = 0

    for item in PROBE_BATTERY:
        w = float(item["weight"])
        weight += w
        try:
            answer = invoke(item["prompt"]) or ""
        except Exception as exc:
            checks[item["key"]] = {"score": 0.0, "error": str(exc)[:180],
                                   "answer": ""}
            errors += 1
            continue
        try:
            s = float(item["grade"](answer, item.get("expect", "")))
        except Exception:
            s = 0.0
        s = max(0.0, min(1.0, s))
        checks[item["key"]] = {"score": s, "answer": str(answer)[:500]}
        total += s * w

    # A transport failure is not evidence about the model's Spanish. If more
    # than one check could not run at all, decline to judge.
    if errors > 1:
        return {"tier": UNKNOWN, "score": 0.0, "inconclusive": True,
                "reason": "%d/%d probes failed to reach the model"
                          % (errors, len(PROBE_BATTERY)),
                "checks": checks, "probe_version": PROBE_VERSION,
                "seed": seed_tier(model_name)}

    score = (total / weight) if weight else 0.0
    return {
        "tier": _tier_from_score(score),
        "score": round(score, 4),
        "inconclusive": False,
        "checks": checks,
        "probe_version": PROBE_VERSION,
        "seed": seed_tier(model_name),
    }


def record(model_name: str, verdict: dict, digest: str = "") -> None:
    """Persist a verdict, preserving any observation history."""
    try:
        key = identity(model_name, digest)
        if not key or not isinstance(verdict, dict):
            return
        if verdict.get("inconclusive"):
            return          # never cache a non-answer as an answer
        with _lock:
            data = dict(_load())
            prev = data.get(key) or {}
            rec = dict(verdict)
            rec["identity"] = key
            rec["model_name"] = str(model_name or "")
            rec["effective_tier"] = rec.get("tier")
            rec["demoted"] = False
            # A fresh probe RESETS the observation window.
            #
            # Carrying it over silently broke the module's own central claim.
            # A model demoted on a poisoned window (n=20, rate=0.00), then
            # re-probed and found FLUENT, was re-demoted by the very NEXT
            # response - because the stale counters still satisfied the
            # demotion test. The probe was nominally the authority and
            # actually powerless.
            #
            # The old observations describe the artifact's behaviour BEFORE
            # this evidence. They are kept for audit, but they no longer vote.
            if prev.get("observations"):
                rec["previous_observations"] = prev["observations"]
            data[key] = rec
            global _cache
            _cache = data
            _save(data)
    except Exception:
        pass


def probe_in_background(model_name: str, invoke, digest: str = "",
                        on_done=None) -> bool:
    """Probe off the hot path, once per identity per process.

    Returns True if a probe was started. A chat request never waits for it.
    """
    try:
        if is_embedder(model_name):
            return False
        key = identity(model_name, digest)
        if not key or known(model_name, digest):
            return False
        with _lock:
            if key in _probing:
                return False
            _probing.add(key)

        def _work():
            try:
                verdict = run_probe(model_name, invoke)
                if verdict.get("inconclusive"):
                    print("--- [NEPANTLA] %s -> inconclusive (%s)"
                          % (key, verdict.get("reason")))
                    return
                record(model_name, verdict, digest)
                print("--- [NEPANTLA] %s -> %s (score %.2f, seed %s)"
                      % (key, verdict.get("tier"), verdict.get("score", 0.0),
                         verdict.get("seed")))
                if on_done:
                    on_done(verdict)
            except Exception:
                pass
            finally:
                with _lock:
                    _probing.discard(key)

        threading.Thread(target=_work, name="nepantla-probe",
                         daemon=True).start()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# L2 - passive verification on real traffic.  Free.  Demotes only.
# ---------------------------------------------------------------------------
def grade_response(response_text: str) -> dict:
    """Grade a REAL production response with the probe's own graders.

    Only the two checks that need no fixed prompt apply: did it answer in
    Spanish, and did the diacritics survive. Pure local string work.
    """
    lang = _g_language(response_text)
    char = _g_charset(response_text)
    return {"language": lang, "charset": char,
            "pass": bool(lang >= 0.5 and char > 0.0)}


def observe(model_name: str, request_text: str, response_text: str,
            digest: str = "") -> dict | None:
    """Record one real Spanish exchange. Returns the verdict change, if any.

    Contract, and the reason it is safe to run on every response:

      * It runs ONLY when the user's request was itself Spanish - grading an
        English answer to an English question would be meaningless.
      * It can DEMOTE a standing FLUENT verdict, never promote anything.
        Promotion requires a probe; a run of easy answers is not evidence.
      * It demotes only on a sustained failure rate over a real sample, so one
        odd response cannot flip the gate.
      * It never raises and never blocks.
    """
    try:
        if not response_text or not str(response_text).strip():
            return None
        if _spanish_ratio(request_text) < 0.6:
            return None                       # not a Spanish request
        rec = known(model_name, digest)
        if not rec:
            return None                       # nothing to correct yet

        g = grade_response(response_text)
        with _lock:
            data = dict(_load())
            key = identity(model_name, digest)
            cur = dict(data.get(key) or {})
            obs = dict(cur.get("observations") or {"n": 0, "passed": 0})
            obs["n"] = int(obs.get("n", 0)) + 1
            obs["passed"] = int(obs.get("passed", 0)) + (1 if g["pass"] else 0)

            # bounded window: halve on overflow so an old failure run cannot
            # hold a model down forever, and a good model cannot bank credit
            if obs["n"] > _OBSERVE_WINDOW:
                obs["n"] //= 2
                obs["passed"] //= 2

            rate = obs["passed"] / float(obs["n"]) if obs["n"] else 1.0
            obs["rate"] = round(rate, 4)
            cur["observations"] = obs

            change = None
            if (obs["n"] >= _OBSERVE_MIN_SAMPLE
                    and rate < _OBSERVE_DEMOTE_BELOW
                    and cur.get("effective_tier") != ASSIST):
                cur["effective_tier"] = ASSIST
                cur["demoted"] = True
                cur["demoted_reason"] = (
                    "live Spanish pass rate %.0f%% over %d responses"
                    % (rate * 100, obs["n"]))
                change = {"from": cur.get("tier"), "to": ASSIST,
                          "rate": rate, "n": obs["n"]}
                print("--- [NEPANTLA] %s DEMOTED to assist: %s"
                      % (key, cur["demoted_reason"]))

            data[key] = cur
            global _cache
            _cache = data
            _save(data)
        return change
    except Exception:
        return None
