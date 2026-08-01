# -*- coding: utf-8 -*-
"""What Spanish voices does the BROWSER actually expose? (no admin needed)

The Windows SAPI inventory said "no Spanish voice", but browsers ship their
own: Edge has the Microsoft *Online (Natural)* voices and Chrome has the
Google network voices. Those need no install and no administrator, so they
decide whether Tlamatini needs an installer step at all.

Headed on purpose (Angela's rule: no invisible automated runs).
"""
import json

from playwright.sync_api import sync_playwright

JS = """() => new Promise(resolve => {
  const grab = () => (speechSynthesis.getVoices() || []).map(v => ({
    name: v.name, lang: v.lang, local: v.localService, uri: v.voiceURI }));
  let v = grab();
  if (v.length) { resolve(v); return; }
  speechSynthesis.onvoiceschanged = () => resolve(grab());
  setTimeout(() => resolve(grab()), 4000);
})"""


def probe(channel):
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel=channel, headless=False)
        except Exception as exc:
            print("  (%s unavailable: %s)" % (channel, str(exc)[:70]))
            return []
        try:
            pg = b.new_context().new_page()
            # A REAL origin: about:blank does not reliably populate the voice
            # list, and network voices only appear on a proper page.
            try:
                pg.goto("http://127.0.0.1:8000/", wait_until="domcontentloaded",
                        timeout=20000)
            except Exception:
                pg.goto("data:text/html,<h1>voces</h1>")
            pg.wait_for_timeout(3000)
            voices = pg.evaluate(JS)
            if not voices:          # one more nudge; Chrome populates lazily
                pg.wait_for_timeout(3000)
                voices = pg.evaluate(JS)
        finally:
            b.close()
    return voices


for channel in ("chrome", "msedge"):
    print("=" * 70)
    print("  %s" % channel.upper())
    print("=" * 70)
    voices = probe(channel)
    if not voices:
        continue
    es = [v for v in voices if (v.get("lang") or "").lower().startswith("es")]
    print("  total voices : %d" % len(voices))
    print("  SPANISH      : %d" % len(es))
    for v in es:
        kind = "local" if v.get("local") else "NETWORK (no install)"
        print("     %-46s %-8s %s" % (v["name"][:44], v["lang"], kind))
    if not es:
        print("     -- none --")
    mx = [v for v in es if (v.get("lang") or "").lower().replace("_", "-") == "es-mx"]
    print("  es-MX exactly: %d" % len(mx))
    print()
    with open("voces_%s.json" % channel, "w", encoding="utf-8") as fh:
        json.dump(voices, fh, ensure_ascii=False, indent=1)
