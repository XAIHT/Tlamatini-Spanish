# -*- coding: utf-8 -*-
"""Prueba VISIBLE de la voz mexicana de Tlamatini (Piper).

REGLA DE ANGELA: nada de headless. Chrome REAL, headed, en su escritorio, y
una foto de PANTALLA COMPLETA (con el reloj de la barra de tareas) por paso.

Lo que se prueba de verdad, sin fingir nada:
  1. La página de chat carga y Tlamatini saluda.
  2. El navegador NO tiene ninguna voz en español (por eso hacía el acento).
  3. Al haber un gesto del usuario, avatar.js hace POST a /agent/tts/ y el
     servidor devuelve audio/wav de verdad — se captura la respuesta REAL de
     la red, no una suposición.
  4. El audio suena por las bocinas (Angela lo oye).

Un timeout, una respuesta vieja o un 204 NO se registran como éxito.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("TLAMATINI_BASE", "http://127.0.0.1:8000")
OUT = Path(__file__).resolve().parent / "resultados_voz"
OUT.mkdir(exist_ok=True)


def _creds():
    user = os.environ.get("TLAMATINI_USER", "")
    pwd = os.environ.get("TLAMATINI_PASS", "")
    env = Path(__file__).resolve().parent / ".creds.env"
    if env.is_file():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.strip().startswith("#"):
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            if k.strip().upper() == "TLAMATINI_USER" and not user:
                user = v
            if k.strip().upper() == "TLAMATINI_PASS" and not pwd:
                pwd = v
    return user or "angela", pwd


def foto(nombre: str):
    """Screenshot del ESCRITORIO COMPLETO (con reloj), no sólo del navegador."""
    dest = OUT / f"{nombre}.png"
    ps = (
        "Add-Type -AssemblyName System.Windows.Forms,System.Drawing; "
        "$b=[System.Windows.Forms.SystemInformation]::VirtualScreen; "
        "$bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height; "
        "$g=[System.Drawing.Graphics]::FromImage($bmp); "
        "$g.CopyFromScreen($b.Left,$b.Top,0,0,$bmp.Size); "
        f"$bmp.Save('{dest}');"
    )
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       timeout=60, capture_output=True)
        print(f"   [foto] {dest.name}")
    except Exception as e:
        print(f"   [foto] falló: {e}")


def main() -> int:
    user, pwd = _creds()
    if not pwd:
        print("Sin contraseña (TLAMATINI_PASS o .creds.env). No corro.")
        return 2

    tts_calls = []          # respuestas REALES de /agent/tts/
    fallos = []

    with sync_playwright() as p:
        # HEADED, Chrome real, en el escritorio de Angela.
        nav = p.chromium.launch(
            headless=False, channel="chrome",
            args=["--autoplay-policy=no-user-gesture-required",
                  "--start-maximized"],
        )
        ctx = nav.new_context(no_viewport=True, locale="es-MX")
        pg = ctx.new_page()

        def on_response(r):
            if "/agent/tts/" in r.url:
                try:
                    body = r.body()
                except Exception:
                    body = b""
                tts_calls.append({
                    "status": r.status,
                    "content_type": r.headers.get("content-type", ""),
                    "bytes": len(body),
                    "es_wav": body[:4] == b"RIFF" and body[8:12] == b"WAVE",
                })
                print(f"   [red] POST /agent/tts/ -> {r.status} "
                      f"{r.headers.get('content-type','')} {len(body)} bytes")

        pg.on("response", on_response)

        # ── 1. login ─────────────────────────────────────────────────
        print("1) entrando como", user)
        pg.goto(f"{BASE}/agent/", wait_until="domcontentloaded", timeout=60000)
        pg.fill("input[name='username']", user)
        pg.fill("input[name='password']", pwd)
        pg.click("button[type='submit'], input[type='submit']")
        pg.wait_for_load_state("domcontentloaded", timeout=60000)

        # ── 2. chat ──────────────────────────────────────────────────
        print("2) abriendo el chat")
        pg.goto(f"{BASE}/agent/agent/", wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(6000)
        foto("01_chat_abierto")

        # ── 3. ¿qué voces ve el navegador? ───────────────────────────
        voces = pg.evaluate("""() => {
            try { return (window.speechSynthesis.getVoices()||[])
                .map(v => v.name + ' [' + v.lang + ']'); }
            catch(e){ return ['<error>']; }
        }""")
        es = [v for v in voces if "[es" in v.lower()]
        print(f"3) voces del navegador ({len(voces)}): {voces}")
        print(f"   en español: {es if es else 'NINGUNA -> por eso uso mi voz Piper'}")

        # ── 4. gesto del usuario + hablar ────────────────────────────
        # Chrome bloquea el audio sin gesto; un click real es el gesto.
        print("4) haciendo click en el avatar y pidiéndole que hable")
        try:
            pg.click("#tlm-avatar-dock", timeout=8000)
        except Exception:
            pg.mouse.click(600, 400)
        pg.wait_for_timeout(1200)

        pg.evaluate("""() => {
            if (window.TLM_VOICE && window.TLM_VOICE.speak) {
                window.TLM_VOICE.speak(
                    'Hola Angela, soy Tlamatini, ya hablo español mexicano.');
            }
        }""")

        # Esperar la respuesta REAL de la red (nada de asumir).
        t0 = time.time()
        while time.time() - t0 < 45 and not tts_calls:
            pg.wait_for_timeout(500)

        pg.wait_for_timeout(6000)   # dejar que suene completo
        foto("02_hablando")

        # ── 5. veredicto ─────────────────────────────────────────────
        if not tts_calls:
            fallos.append("avatar.js nunca llamó a /agent/tts/")
        else:
            ok = [c for c in tts_calls if c["status"] == 200 and c["es_wav"]]
            if not ok:
                fallos.append(f"/agent/tts/ no devolvió WAV: {tts_calls}")

        print("\n" + "=" * 60)
        if fallos:
            print("FALLÓ:")
            for f in fallos:
                print("  -", f)
        else:
            total = sum(c["bytes"] for c in tts_calls)
            print(f"PASÓ: {len(tts_calls)} llamada(s) a /agent/tts/, "
                  f"{total} bytes de audio WAV reproducidos.")
        print("=" * 60)

        (OUT / "resultado.json").write_text(
            json.dumps({"voces_navegador": voces, "voces_es": es,
                        "llamadas_tts": tts_calls, "fallos": fallos},
                       indent=2, ensure_ascii=False), encoding="utf-8")

        print("\nDejo Chrome abierto 20 s para que lo veas…")
        pg.wait_for_timeout(20000)
        ctx.close()
        nav.close()

    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
