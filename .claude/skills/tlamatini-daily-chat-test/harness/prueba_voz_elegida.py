# -*- coding: utf-8 -*-
"""¿QUÉ voz escoge Tlamatini de verdad? Prueba VISIBLE, con audio.

Esto es lo que a Angela le importa: que NO suene con acento inglés.

Comprueba las dos rutas, sin fingir:
  A. La ruta del navegador — que pickVoice() escoja una voz es-* FEMENINA
     (Sabina, es-MX) y no una inglesa (Zira). Se oye.
  B. La ruta de respaldo (Piper) — se fuerza a propósito para comprobar que
     también funciona en una máquina SIN voces en español. Se oye.
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
    dest = OUT / f"{nombre}.png"
    ps = ("Add-Type -AssemblyName System.Windows.Forms,System.Drawing; "
          "$b=[System.Windows.Forms.SystemInformation]::VirtualScreen; "
          "$bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height; "
          "$g=[System.Drawing.Graphics]::FromImage($bmp); "
          "$g.CopyFromScreen($b.Left,$b.Top,0,0,$bmp.Size); "
          f"$bmp.Save('{dest}');")
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       timeout=60, capture_output=True)
        print(f"   [foto] {dest.name}")
    except Exception as e:
        print(f"   [foto] falló: {e}")


def main() -> int:
    user, pwd = _creds()
    if not pwd:
        print("Sin contraseña. No corro.")
        return 2

    tts_calls, fallos = [], []

    with sync_playwright() as p:
        nav = p.chromium.launch(
            headless=False, channel="chrome",
            args=["--autoplay-policy=no-user-gesture-required", "--start-maximized"])
        ctx = nav.new_context(no_viewport=True, locale="es-MX")
        pg = ctx.new_page()

        def on_response(r):
            if "/agent/tts/" in r.url:
                try:
                    body = r.body()
                except Exception:
                    body = b""
                tts_calls.append({"status": r.status, "bytes": len(body),
                                  "es_wav": body[:4] == b"RIFF"})
                print(f"   [red] /agent/tts/ -> {r.status} {len(body)} bytes")

        pg.on("response", on_response)

        pg.goto(f"{BASE}/agent/", wait_until="domcontentloaded", timeout=60000)
        pg.fill("input[name='username']", user)
        pg.fill("input[name='password']", pwd)
        pg.click("button[type='submit'], input[type='submit']")
        pg.wait_for_load_state("domcontentloaded", timeout=60000)
        pg.goto(f"{BASE}/agent/agent/", wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(6000)

        try:
            pg.click("#tlm-avatar-dock", timeout=8000)
        except Exception:
            pg.mouse.click(600, 400)
        pg.wait_for_timeout(1000)

        # ── A. ¿qué voz escoge? ──────────────────────────────────────
        elegida = pg.evaluate("""() => {
            try {
                const v = window.TLM_VOICE && window.TLM_VOICE.pickVoice
                        ? window.TLM_VOICE.pickVoice() : null;
                return v ? {name: v.name, lang: v.lang} : null;
            } catch(e){ return {error: String(e)}; }
        }""")
        print("\nA) voz que escoge Tlamatini:", elegida)

        if not elegida or not elegida.get("lang"):
            fallos.append(f"pickVoice() no devolvió ninguna voz: {elegida}")
        elif not str(elegida.get("lang", "")).lower().startswith("es"):
            fallos.append(
                f"ESCOGIÓ UNA VOZ QUE NO ES ESPAÑOLA -> acento inglés: {elegida}")
        else:
            print("   OK: es una voz en español ->", elegida["lang"])

        print("   hablando por la ruta del navegador… (escucha)")
        pg.evaluate("""() => window.TLM_VOICE.speak(
            'Hola Angela, soy Tlamatini y estoy hablando en español mexicano.')""")
        pg.wait_for_timeout(9000)
        foto("03_voz_navegador")

        # ── B. forzar la ruta Piper (máquina sin voces en español) ───
        print("\nB) forzando mi voz Piper (como en una PC sin voces es-*)…")
        pg.evaluate("""() => {
            // Simular que el navegador NO tiene ninguna voz en español.
            const real = window.speechSynthesis.getVoices.bind(window.speechSynthesis);
            window.speechSynthesis.getVoices = () =>
                real().filter(v => !/^es(-|_)/i.test(v.lang || ''));
        }""")
        pg.wait_for_timeout(500)
        pg.evaluate("""() => window.TLM_VOICE.speak(
            'Y esta es mi propia voz, la que traigo conmigo.')""")

        t0 = time.time()
        while time.time() - t0 < 45 and not tts_calls:
            pg.wait_for_timeout(500)
        pg.wait_for_timeout(8000)
        foto("04_voz_piper")

        if not tts_calls:
            fallos.append("la ruta Piper no llamó a /agent/tts/")
        elif not any(c["status"] == 200 and c["es_wav"] for c in tts_calls):
            fallos.append(f"/agent/tts/ no devolvió WAV: {tts_calls}")
        else:
            print("   OK: la voz Piper respondió con audio WAV de verdad")

        print("\n" + "=" * 60)
        if fallos:
            print("FALLÓ:")
            for f in fallos:
                print("  -", f)
        else:
            print("PASÓ: habla en español por las DOS rutas.")
        print("=" * 60)

        (OUT / "resultado_voz_elegida.json").write_text(
            json.dumps({"voz_elegida": elegida, "llamadas_tts": tts_calls,
                        "fallos": fallos}, indent=2, ensure_ascii=False),
            encoding="utf-8")

        pg.wait_for_timeout(15000)
        ctx.close()
        nav.close()

    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
