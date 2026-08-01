# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""
Voz en español para Tlamatini — Piper TTS, SIN permisos de administrador.

WHY THIS EXISTS
    Tlamatini's Spanish edition had no voice. Measured on Angela's machine
    (2026-07-29): Windows exposes exactly three TTS voices — David, Mark and
    Zira — all ``en-US``. Chrome and Edge each expose the same three; the
    Microsoft "Online (Natural)" Spanish voices are NOT reachable through the
    Web Speech API. So the browser had nothing Spanish to speak with and fell
    back to English, which is how she ended up reading Spanish with an English
    accent.

    The obvious fix, ``Install-Language es-MX``, needs ADMINISTRATOR, and the
    Tlamatini installer must never require it. Windows speech voices are
    machine-wide, so there is no per-user way to add one.

    Piper resolves the conflict: a single self-contained executable plus a
    voice model, both of which live under %LOCALAPPDATA% and need no elevation
    whatsoever. It is the same self-provisioning pattern Tlamatini already uses
    for Discoverer's private Go toolchain, ESP32er's PlatformIO and Arduiner's
    arduino-cli — download into the user's own profile, never touch the system.

CONTRACT
    * NO ADMIN, EVER. Everything lands in
      ``%LOCALAPPDATA%/Tlamatini/piper``. Nothing is written outside the user
      profile, no registry, no PATH change, no service.
    * FAIL-OPEN AND SILENT-BY-CHOICE. Every failure returns a structured
      ``status`` instead of raising. If synthesis is impossible Tlamatini says
      NOTHING rather than mispronouncing Spanish with an English voice — the
      same rule the Talker agent applies to a male voice.
    * OFFLINE AFTER SETUP. The download happens once; after that synthesis is
      local, with no network and no per-utterance cost.
    * NEVER BLOCKS THE CHAT. Bootstrapping is opt-in via ``ensure_ready`` and
      is expected to be driven by the installer, not by a chat request.

VOICE
    Default ``es_MX-claude-high`` — a Mexican Spanish female voice, matching
    Tlamatini's register (she is female by design; see the Talker agent).
    Override with ``piper_voice`` / ``piper_voice_url`` in config.json.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from typing import Dict, Optional, Tuple

__all__ = [
    "install_root", "piper_exe", "voice_paths", "is_ready", "status",
    "ensure_ready", "synthesize",
]

# --- where everything lives (user profile only — no admin) -----------------
_DIR_NAME = "piper"
_DEFAULT_VOICE = "es_MX-claude-high"

# Piper Windows build. Pinned to a release so a silent upstream change cannot
# alter behaviour; overridable from config.json for air-gapped installs.
_PIPER_URL = (
    "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/"
    "piper_windows_amd64.zip"
)
# rhasspy/piper-voices layout: <lang>/<locale>/<name>/<quality>/<file>
_VOICE_BASE = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    "es/es_MX/claude/high/es_MX-claude-high.onnx"
)

_TIMEOUT = 180


def _local_appdata() -> str:
    return (os.environ.get("LOCALAPPDATA")
            or os.path.join(os.path.expanduser("~"), "AppData", "Local"))


def install_root() -> str:
    """%LOCALAPPDATA%/Tlamatini/piper — writable by the user, no elevation."""
    return os.path.join(_local_appdata(), "Tlamatini", _DIR_NAME)


def piper_exe() -> Optional[str]:
    """Path to piper.exe if present, else None. Never raises."""
    try:
        root = install_root()
        for cand in (os.path.join(root, "piper", "piper.exe"),
                     os.path.join(root, "piper.exe")):
            if os.path.isfile(cand):
                return cand
    except Exception:
        pass
    return None


def voice_paths(voice: str = _DEFAULT_VOICE) -> Tuple[str, str]:
    """(model, config) paths for a voice — they may not exist yet."""
    root = os.path.join(install_root(), "voices")
    return (os.path.join(root, voice + ".onnx"),
            os.path.join(root, voice + ".onnx.json"))


def is_ready(voice: str = _DEFAULT_VOICE) -> bool:
    """True when a synthesis would actually work. Never raises."""
    try:
        model, cfg = voice_paths(voice)
        return bool(piper_exe()) and os.path.isfile(model) and os.path.isfile(cfg)
    except Exception:
        return False


def status(voice: str = _DEFAULT_VOICE) -> Dict[str, object]:
    """Structured readiness report — what the installer and the UI ask for."""
    try:
        model, cfg = voice_paths(voice)
        exe = piper_exe()
        return {
            "ready": bool(exe) and os.path.isfile(model) and os.path.isfile(cfg),
            "engine": exe or "",
            "voice": voice,
            "model": model if os.path.isfile(model) else "",
            "root": install_root(),
            "needs_admin": False,          # by construction
        }
    except Exception as exc:               # pragma: no cover - defensive
        return {"ready": False, "error": str(exc), "needs_admin": False}


# --------------------------------------------------------------- bootstrap
_CHUNK = 262144          # 256 KiB — small enough to report often, big enough to be fast


def _download(url: str, dest: str, log=None, resume: bool = True) -> bool:
    """Stream ``url`` to ``dest`` atomically, resumably, reporting progress.

    Streamed rather than buffered on purpose: the Mexican voice model is ~63 MB
    and the engine ~22 MB. Reading either one with a single ``.read()`` keeps
    the whole file in RAM AND leaves the install directory empty until the very
    last moment, so both the installer and anyone watching the folder see an
    apparently frozen program for minutes. Chunked writes give a growing
    ``.part`` file plus periodic progress, and the final ``os.replace`` keeps
    the destination atomic — an interrupted download can never masquerade as a
    finished one.

    Resumable for the same reason. Measured on Angela's connection
    (2026-07-29) GitHub, HuggingFace and PyPI all delivered ~10 KB/s, which
    puts these two files over two hours end to end; a drop somewhere in that
    window is the expected case, not the exception. So a failed attempt KEEPS
    its ``.part`` and the next one continues with an HTTP ``Range`` request.
    If the server ignores ``Range`` and answers ``200`` instead of ``206`` the
    transfer simply restarts — correctness never depends on resume working.
    """
    name = os.path.basename(dest)
    tmp = dest + ".part"
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        # Resume whatever a previous attempt already fetched.
        have = 0
        if resume:
            try:
                have = os.path.getsize(tmp)
            except OSError:
                have = 0

        headers = {"User-Agent": "Tlamatini"}
        if have:
            headers["Range"] = "bytes=%d-" % have
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            code = getattr(r, "status", 200) or 200
            try:
                clen = int(r.headers.get("Content-Length") or 0)
            except Exception:
                clen = 0

            if have and code == 206:
                total, mode = have + clen, "ab"
                if log:
                    log("reanudando %s desde %.1f MB" % (name, have / 1048576.0))
            else:
                # No .part, or the server ignored Range — start clean.
                have, total, mode = 0, clen, "wb"
                if log:
                    log("descargando %s (%s)" % (
                        name,
                        ("%.1f MB" % (total / 1048576.0)) if total else "tamaño desconocido"))

            got = have
            step = max(total // 20, 1) if total else 0
            nxt = got + step
            with open(tmp, mode) as fh:
                while True:
                    chunk = r.read(_CHUNK)
                    if not chunk:
                        break
                    fh.write(chunk)
                    got += len(chunk)
                    if log and step and got >= nxt:
                        log("   %s: %d%% (%.1f MB)" % (
                            name, int(got * 100 / total), got / 1048576.0))
                        nxt += step

        if not got:
            if log:
                log("%s llegó vacío" % name)
            return False
        if total and got < total:
            # Keep the .part: the next attempt resumes instead of restarting.
            if log:
                log("%s quedó incompleto (%.1f de %.1f MB) — se reanudará"
                    % (name, got / 1048576.0, total / 1048576.0))
            return False

        os.replace(tmp, dest)
        if log:
            log("   %s listo (%.1f MB)" % (name, got / 1048576.0))
        return True
    except Exception as exc:
        # The .part survives on purpose so a retry picks up where this stopped.
        if log:
            log("no se pudo descargar %s: %s" % (name, exc))
        return False


def _provision_once(voice: str, piper_url: str, voice_url: str, _log) -> None:
    """One provisioning pass. Resumable, so calling it again makes progress."""
    root = install_root()
    os.makedirs(root, exist_ok=True)

    # 1) engine
    if not piper_exe():
        zpath = os.path.join(root, "piper_windows.zip")
        if _download(piper_url or _PIPER_URL, zpath, _log):
            try:
                with zipfile.ZipFile(zpath) as zf:
                    zf.extractall(root)
            except Exception as exc:
                _log("el zip de Piper no se pudo abrir: %s" % exc)
            finally:
                try:
                    os.remove(zpath)
                except Exception:
                    pass

    # 2) voice model + its json sidecar
    model, cfg = voice_paths(voice)
    base = voice_url or _VOICE_BASE
    if not os.path.isfile(model):
        _download(base, model, _log)
    if not os.path.isfile(cfg):
        _download(base + ".json", cfg, _log)


def ensure_ready(voice: str = _DEFAULT_VOICE, log=None, piper_url: str = "",
                 voice_url: str = "", attempts: int = 3,
                 retry_wait: float = 5.0) -> Dict[str, object]:
    """Provision the engine + voice under %LOCALAPPDATA%. NO ADMIN.

    Idempotent and fail-open: returns a status dict, never raises. Safe to
    call from the installer, from a management command, or not at all.

    Retries because the download is ~85 MB and the connection it runs over is
    not guaranteed. Each attempt resumes the previous one's ``.part`` files, so
    N attempts genuinely converge instead of restarting from zero; a pass that
    downloads nothing new still costs only one round-trip. Nothing here can
    raise into the installer.
    """
    def _log(msg):
        if log:
            try:
                log(msg)
            except Exception:
                pass

    try:
        _log("instalando la voz mexicana de Tlamatini (sin permisos de admin)")
        for i in range(max(1, int(attempts or 1))):
            if i:
                _log("reintento %d de %d" % (i + 1, attempts))
                time.sleep(max(0.0, retry_wait))
            try:
                _provision_once(voice, piper_url, voice_url, _log)
            except Exception as exc:
                _log("falló el intento: %s" % exc)
            if is_ready(voice):
                break

        st = status(voice)
        _log("la voz quedó lista" if st.get("ready")
             else "la voz NO quedó lista — Tlamatini se quedará callada en vez de "
                  "hablar con acento inglés")
        return st
    except Exception as exc:               # pragma: no cover - defensive
        return {"ready": False, "error": str(exc), "needs_admin": False}


# -------------------------------------------------------------- synthesis
def synthesize(text: str, voice: str = _DEFAULT_VOICE) -> Tuple[bytes, str]:
    """text -> (wav_bytes, status). Never raises.

    status: 'ok' | 'empty' | 'not_ready' | 'error:<detail>'
    On anything other than 'ok' the caller MUST stay silent rather than fall
    back to an English voice.
    """
    if not text or not text.strip():
        return b"", "empty"
    if not is_ready(voice):
        return b"", "not_ready"
    exe = piper_exe()
    model, _cfg = voice_paths(voice)
    out = ""
    try:
        fd, out = tempfile.mkstemp(suffix=".wav", prefix="tlm_voz_")
        os.close(fd)
        creation = 0
        if sys.platform == "win32":
            creation = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        proc = subprocess.run(
            [exe, "-m", model, "-f", out],
            input=text.encode("utf-8"),
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            timeout=90, creationflags=creation,
        )
        if proc.returncode != 0:
            return b"", "error:piper rc=%s %s" % (
                proc.returncode, (proc.stderr or b"").decode("utf-8", "replace")[:160])
        with open(out, "rb") as fh:
            data = fh.read()
        return (data, "ok") if data else (b"", "error:empty wav")
    except subprocess.TimeoutExpired:
        return b"", "error:timeout"
    except Exception as exc:
        return b"", "error:%s" % exc
    finally:
        if out:
            try:
                os.remove(out)
            except Exception:
                pass


if __name__ == "__main__":          # manual check: python -m agent.tts_piper
    print(json.dumps(status(), indent=2, ensure_ascii=False))
    if "--install" in sys.argv:
        print(json.dumps(ensure_ready(log=lambda m: print("   " + m)),
                         indent=2, ensure_ascii=False))
    if "--say" in sys.argv:
        wav, st = synthesize("Hola, soy Tlamatini, estoy lista para platicar contigo.")
        print("synthesis:", st, len(wav), "bytes")
        if st == "ok":
            dest = os.path.join(tempfile.gettempdir(), "tlamatini_voz.wav")
            with open(dest, "wb") as fh:
                fh.write(wav)
            print("wrote", dest)
            shutil.which("powershell") and subprocess.run(
                ["powershell", "-c",
                 "(New-Object Media.SoundPlayer '%s').PlaySync()" % dest])
