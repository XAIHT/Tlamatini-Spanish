"""NEPANTLA runtime switches, read from config.json.

Stdlib only. Never imports ``agent.*`` - this module is reachable from
``capability_registry``, which sits on the request hot path, and from a pool
agent that has no path back into the Django package.

FAIL-OPEN CONTRACT
------------------
A missing file, a BOM, unparseable JSON, a wrong type or an unknown key
resolves to the built-in default for that ONE key and never raises. A config
typo must never stop the scorer from working.

The defaults are chosen so a config.json predating this feature - for example
one preserved across a self-update - behaves exactly like a fresh one.
"""

from __future__ import annotations

import json
import os
import sys
import threading

__all__ = ["scoring_enabled", "lexicon_enabled", "settings", "invalidate"]

_DEFAULTS = {
    # N1 folding + N2 boundary-aware phrase matching in capability_registry.
    # Both are the identity on pure-ASCII English input.
    "nepantla_scoring_enabled": True,
    # N3 expansion of a Spanish-carrier request into canonical English hints.
    "nepantla_lexicon_enabled": True,
}

_lock = threading.Lock()
_cache: dict | None = None
_cache_stamp: tuple | None = None


def _config_path() -> str:
    """Resolve config.json the way the rest of Tlamatini does."""
    env = (os.environ.get("CONFIG_PATH") or "").strip()
    if env:
        return env
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "config.json")
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, "config.json")


def _stamp(path: str):
    try:
        st = os.stat(path)
        return (st.st_mtime_ns, st.st_size)
    except OSError:
        return None


def settings() -> dict:
    """Resolved switches. Cached per process, refreshed when config.json changes."""
    global _cache, _cache_stamp
    path = _config_path()
    stamp = _stamp(path)
    if _cache is not None and stamp == _cache_stamp:
        return _cache

    resolved = dict(_DEFAULTS)
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            raw = json.load(fh)
        if isinstance(raw, dict):
            for key in _DEFAULTS:
                if key not in raw:
                    continue
                value = raw[key]
                if isinstance(value, bool):
                    resolved[key] = value
                elif isinstance(value, str) and value.strip().lower() in ("true", "false"):
                    resolved[key] = value.strip().lower() == "true"
                else:
                    print("--- [NEPANTLA] config fallback %s (bad type)" % key)
    except Exception:
        # Missing / unreadable / unparseable -> every default. Never raises.
        pass

    with _lock:
        _cache = resolved
        _cache_stamp = stamp
    return resolved


def invalidate() -> None:
    """Drop the cache (tests)."""
    global _cache, _cache_stamp
    with _lock:
        _cache = None
        _cache_stamp = None


def scoring_enabled() -> bool:
    try:
        return bool(settings()["nepantla_scoring_enabled"])
    except Exception:
        return True


def lexicon_enabled() -> bool:
    try:
        return bool(settings()["nepantla_lexicon_enabled"])
    except Exception:
        return True
