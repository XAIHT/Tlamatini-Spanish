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
#: ⛔ NI LA VOZ NI LAS PRUEBAS HABLAN INGLES (Angela, 2026-08-23).
#: Palabras suyas: *"Tlamatini in its voices and automated tests must always
#: speak Spanish. If it can't, then NOT SPEAK"*.
#:
#: La voz es mexicana, pero eso solo arregla el ACENTO: una voz es_MX leyendo
#: una frase inglesa sigue siendo Tlamatini hablando ingles, nada mas que mal
#: pronunciado. Por eso el filtro mira el TEXTO, no la voz.
#:
#: Palabras funcion inglesas que casi no aparecen en castellano. Se piden
#: VARIAS y una proporcion alta para que un tecnicismo suelto ("el buffer",
#: "hazme un backup", "corre el test") NO calle a Tlamatini: eso es
#: Spanglish normal y SI se habla.
_PALABRAS_INGLESAS = frozenset("""
the and you are was were will would should could have has had been being
this that these those with from they them their there here what when where
which while about after before because between into through during without
your yours mine ours theirs isn't don't can't won't didn't doesn't
""".split())

#: Marcas inequivocas de castellano: si aparecen, no es ingles y se habla.
_MARCAS_ES = frozenset("""
el la los las un una unos unas de del al que para por con sin sobre entre
es son era eran ser estar tengo tiene hacer hago muy pero porque cuando
donde como esto esta este ese esa aqui alli ya no si mas menos
""".split())


def _es_ingles(texto: str) -> bool:
    """True cuando el texto es INGLES corrido y por tanto no se pronuncia.

    FAIL-OPEN A PROPOSITO: ante la duda devuelve False (se habla). Callar a
    Tlamatini por error es peor que dejar pasar una frase rara; lo que se
    persigue es el ingles evidente, no el Spanglish de todos los dias.
    """
    palabras = [p.strip(".,;:!?¡¿()[]\"'").lower()
                for p in (texto or "").split()]
    palabras = [p for p in palabras if p.isalpha()]
    if len(palabras) < 4:
        return False                     # muy corto para juzgar: se habla
    if any(p in _MARCAS_ES for p in palabras):
        return False                     # trae castellano: se habla
    inglesas = sum(1 for p in palabras if p in _PALABRAS_INGLESAS)
    # dos o mas palabras funcion inglesas Y al menos el 15% del texto
    return inglesas >= 2 and (inglesas / len(palabras)) >= 0.15


#: ⛔ NO SE CALLA: LO DICE EN CASTELLANO (Angela, 2026-08-23).
#: Palabras suyas: *"make the fucking Piper ... and all the shit speak
#: spanish"*. Antes, un texto en ingles devolvia 'refused:ingles' y no salia
#: audio. Mejor que el silencio es DECIRLO EN CASTELLANO: se traduce y se
#: pronuncia. El silencio queda solo para cuando no hay con que traducir.
#:
#: Escalera, de lo barato y seguro a lo caro:
#:   1. el catalogo NEPANTLA (agent/i18n/ui_es.py) — exacto, instantaneo
#:   2. el lexico NEPANTLA, palabra por palabra
#:   3. Ollama en local, si esta prendido
#:   4. si nada de eso puede: NO SE HABLA (jamas en ingles)
_OLLAMA_TIMEOUT = 20


def _catalogo_nepantla():
    """El catalogo de la interfaz, {ingles: castellano}. Fail-open a {}."""
    try:
        from .i18n.ui_es import UI_ES
        return UI_ES
    except Exception:
        try:
            import importlib.util
            ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "i18n", "ui_es.py")
            spec = importlib.util.spec_from_file_location("_ui_es", ruta)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return getattr(mod, "UI_ES", {})
        except Exception:
            return {}


def _traduce_con_catalogo(texto):
    """Coincidencia exacta en el catalogo NEPANTLA. '' si no esta."""
    cat = _catalogo_nepantla()
    if not cat:
        return ""
    limpio = (texto or "").strip()
    if limpio in cat:
        return cat[limpio]
    for en, es in cat.items():                      # sin distinguir mayusculas
        if en.strip().lower() == limpio.lower():
            return es
    return ""


def _traduce_con_ollama(texto):
    """Traduce con el Ollama local. '' si no esta prendido o si falla.

    Se le pide castellano LATINOAMERICANO y que NO toque los nombres propios
    del sistema (Tlamatini, Executer, Exec report...), que son canal de
    maquina y no se traducen nunca.
    """
    try:
        import json as _json
        import urllib.request as _req
        base = "http://127.0.0.1:11434"
        try:
            cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "config.json")
            with open(cfg, encoding="utf-8-sig") as fh:
                base = (_json.load(fh).get("ollama_base_url") or base).rstrip("/")
        except Exception:
            pass
        modelo = os.environ.get("TLAMATINI_TRAD_MODEL", "llama3.2:3b")
        instruccion = (
            "Traduce al espanol latinoamericano. Responde SOLO con la "
            "traduccion, sin comillas ni explicaciones. NO traduzcas nombres "
            "propios ni terminos tecnicos (Tlamatini, Executer, Exec report, "
            "Multi-Turn, log, backup, script, token).\n\nTexto: " + texto)
        cuerpo = _json.dumps({"model": modelo, "prompt": instruccion,
                              "stream": False}).encode("utf-8")
        pet = _req.Request(base + "/api/generate", data=cuerpo,
                           headers={"Content-Type": "application/json"})
        with _req.urlopen(pet, timeout=_OLLAMA_TIMEOUT) as r:
            got = _json.loads(r.read().decode("utf-8", "replace"))
        return (got.get("response") or "").strip()
    except Exception:
        return ""


def _tiene_marca_de_castellano(texto):
    """True si el texto trae una senal POSITIVA de castellano.

    No es "¿parece ingles?" al reves: aquello contesta que no ante cualquier
    duda y por eso dejaba pasar frases cortas en ingles. Esto exige ver algo
    nuestro — acento, enye, signo de apertura, o una palabra funcion del
    castellano — antes de dejar que se pronuncie sin traducir.
    """
    s = (texto or "")
    if any(c in s for c in "áéíóúüñÁÉÍÓÚÜÑ¿¡"):
        return True
    palabras = [p.strip('.,;:!?()[]"\'').lower() for p in s.split()]
    return any(p in _MARCAS_ES for p in palabras if p.isalpha())


def a_castellano(texto):
    """(texto_a_hablar, como). `como` == '' cuando NO se puede y hay que callar.

    ⚠️ EL CATALOGO SE CONSULTA PRIMERO, ANTES DE JUZGAR EL IDIOMA. Sonaba
    razonable preguntar "¿esto es ingles?" y solo entonces traducir, pero
    `_es_ingles` necesita al menos cuatro palabras para no equivocarse, asi
    que "Save", "Contacts book" o "Please wait" se colaban como si ya
    estuvieran en castellano... y se pronunciaban EN INGLES. Justo lo unico
    prohibido. El catalogo NEPANTLA acierta con esas cadenas cortas sin tener
    que adivinar nada, asi que va primero y el largo deja de importar.
    """
    if not (texto or "").strip():
        return texto, "vacio"

    # 1) el catalogo, a cualquier longitud
    try:
        got = _traduce_con_catalogo(texto)
    except Exception:
        got = ""
    if got:
        return got, "catalogo"

    # 2) MODO ESTRICTO: para decirlo tal cual hay que estar SEGUROS de que
    #    es castellano, no solo de que "no parece ingles". `_es_ingles` pide
    #    >=4 palabras, asi que con esa pregunta sola se colaban "Please
    #    wait", "Unsaved changes" o "Delete contact" y se pronunciaban EN
    #    INGLES. Ahora se exige una marca POSITIVA de castellano (un acento,
    #    una enye, un signo de apertura o una palabra funcion nuestra).
    #    Sin esa marca no se arriesga: se manda a traducir, y si no hay con
    #    que, se calla. Mejor muda que en ingles.
    if _tiene_marca_de_castellano(texto):
        return texto, "ya-en-castellano"

    # 3) ingles de verdad: que lo traduzca el Ollama local
    try:
        got = _traduce_con_ollama(texto)
    except Exception:
        got = ""
    if got and not _es_ingles(got):
        return got, "ollama"

    # 4) no hubo con que: SE CALLA. En ingles no se habla jamas.
    return "", ""


def synthesize(text: str, voice: str = _DEFAULT_VOICE) -> Tuple[bytes, str]:
    """text -> (wav_bytes, status). Never raises.

    status: 'ok' | 'empty' | 'refused:ingles' | 'not_ready' | 'error:<detail>'
    On anything other than 'ok' the caller MUST stay silent rather than fall
    back to an English voice.
    """
    if not text or not text.strip():
        return b"", "empty"
    text, _como = a_castellano(text)
    if not text:
        # No hubo con que traducir. Callarse es correcto; hablar ingles no.
        return b"", "refused:ingles"
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
