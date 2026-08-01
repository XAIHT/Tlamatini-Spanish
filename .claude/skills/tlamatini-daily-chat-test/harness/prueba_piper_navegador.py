# -*- coding: utf-8 -*-
"""¿El navegador REALMENTE recibe y reproduce el audio de Piper?

La prueba anterior vio HTTP 200 pero 0 bytes. Un 200 sólo puede salir del
camino en el que la síntesis SÍ funcionó (si no hay voz, tts_view responde
204), así que lo más probable es que Playwright no pueda releer un body que
la página ya consumió con fetch().

Aquí no se supone nada: se mide DESDE LA PÁGINA — el tamaño real del blob y
si el elemento <audio> de veras se puso a sonar.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("TLAMATINI_BASE", "http://127.0.0.1:8000")
OUT = Path(__file__).resolve().parent / "resultados_voz"
OUT.mkdir(exist_ok=True)


def _creds():
    user, pwd = os.environ.get("TLAMATINI_USER", ""), os.environ.get("TLAMATINI_PASS", "")
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


def main() -> int:
    user, pwd = _creds()
    if not pwd:
        print("Sin contraseña. No corro.")
        return 2

    with sync_playwright() as p:
        nav = p.chromium.launch(
            headless=False, channel="chrome",
            args=["--autoplay-policy=no-user-gesture-required", "--start-maximized"])
        ctx = nav.new_context(no_viewport=True, locale="es-MX")
        pg = ctx.new_page()
        pg.on("console", lambda m: print("   [console]", m.text[:160]))

        pg.goto(f"{BASE}/agent/", wait_until="domcontentloaded", timeout=60000)
        pg.fill("input[name='username']", user)
        pg.fill("input[name='password']", pwd)
        pg.click("button[type='submit'], input[type='submit']")
        pg.wait_for_load_state("domcontentloaded", timeout=60000)
        pg.goto(f"{BASE}/agent/agent/", wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(5000)
        try:
            pg.click("#tlm-avatar-dock", timeout=8000)
        except Exception:
            pg.mouse.click(600, 400)
        pg.wait_for_timeout(800)

        # Medir el POST a /agent/tts/ DESDE la página: tamaño real del blob
        # y si el <audio> se puso a sonar de verdad.
        print("\nPidiendo el audio a /agent/tts/ desde la página…")
        res = pg.evaluate("""async () => {
            const csrf = (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)||[])[1] || '';
            const r = await fetch('/agent/tts/', {
                method:'POST', credentials:'same-origin',
                headers:{'Content-Type':'application/json',
                         'X-CSRFToken': decodeURIComponent(csrf)},
                body: JSON.stringify({text:'Esta es mi propia voz mexicana, la que traigo conmigo.'})
            });
            if (r.status !== 200) return {status:r.status, bytes:0, sono:false};
            const blob = await r.blob();
            const a = new Audio(URL.createObjectURL(blob));
            a.volume = 1;
            let sono = false;
            await new Promise(res2 => {
                a.onplaying = () => { sono = true; };
                a.onended   = () => res2();
                a.onerror   = () => res2();
                a.play().catch(() => res2());
                setTimeout(res2, 15000);
            });
            return {status:r.status, tipo:r.headers.get('content-type'),
                    bytes: blob.size, sono: sono, duro: a.duration};
        }""")
        print("\nMedido desde la página:", json.dumps(res, ensure_ascii=False))

        ok = (res.get("status") == 200 and res.get("bytes", 0) > 1000
              and res.get("sono") is True)
        print("\n" + "=" * 60)
        print("PASÓ: el navegador recibió y REPRODUJO mi voz Piper."
              if ok else f"FALLÓ: {res}")
        print("=" * 60)

        (OUT / "resultado_piper_navegador.json").write_text(
            json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
        pg.wait_for_timeout(8000)
        ctx.close()
        nav.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
