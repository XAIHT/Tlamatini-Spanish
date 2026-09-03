import os
import sys
import time
import datetime
sys.path.insert(0, os.getcwd())
from playwright.sync_api import sync_playwright
from shoter_foto import toma_foto

SALIDA = os.path.join("reports", "skills_es_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
os.makedirs(SALIDA, exist_ok=True)
u = c = ""
for ln in open(".creds.env", encoding="utf-8"):
    if "=" in ln and not ln.strip().startswith("#"):
        k, v = ln.split("=", 1)
        if k.strip() == "TLAMATINI_USER":
            u = v.strip()
        if k.strip() == "TLAMATINI_PASS":
            c = v.strip()

with sync_playwright() as pw:
    nav = pw.chromium.launch(headless=False, channel="chrome", args=["--start-maximized"])
    page = nav.new_context(no_viewport=True).new_page()
    page.goto("http://127.0.0.1:8000/", wait_until="domcontentloaded")
    page.fill("#id_username", u)
    page.fill("#id_password", c)
    page.click("form button[type=submit]")
    page.wait_for_load_state("domcontentloaded")
    page.goto("http://127.0.0.1:8000/agent/agent/", wait_until="domcontentloaded")
    page.wait_for_selector("#skills-menu-button", timeout=25000)
    time.sleep(2.0)
    page.click("#skills-menu-button")
    time.sleep(0.5)
    page.click("#configure-skills")
    time.sleep(1.5)
    page.bring_to_front()
    time.sleep(0.4)
    toma_foto(os.path.abspath(SALIDA), "00_configurar_skills.png")
    txt = page.evaluate("""() => {
        const w = Array.from(document.querySelectorAll('.ui-dialog')).filter(d=>d.offsetParent!==null).pop();
        return w ? (w.innerText||'').trim() : '';
    }""")
    ing = [p for p in ("Summarize a long text","Route plain-language","Look up current weather",
                       "Review a git diff","Run whichever SAST","Manage Trello boards") if p in txt]
    esp = [p for p in ("Resume un texto largo","Enruta peticiones","Administra boards",
                       "Revisa un git diff") if p in txt]
    print("=" * 60)
    print("descripciones en ESPANOL visibles : %d  %s" % (len(esp), esp))
    print("descripciones en INGLES visibles  : %d  %s" % (len(ing), ing))
    print("VEREDICTO: %s" % ("TODO BIEN" if esp and not ing else "HAY FALLAS"))
    print("=" * 60)
    time.sleep(2)
    nav.close()
