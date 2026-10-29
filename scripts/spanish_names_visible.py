# Tlamatini Author Banner — Angela López Mendoza · @angelahack1
"""Visible Chrome component checks for the real avatar/voice runtime.

Run from a verified foreground PowerShell -NoExit console. Never headless.
No account database or model call. Every available Spanish female voice runs
through native synthesis at zero volume; the final page offers manual listening. Shoter captures evidence; close by creating close.confirmed.
"""
import functools
import ctypes
import ast
import html as html_tools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import threading
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Temp/spanish-names-visible'


def main():
    if any('headless' in arg.lower() for arg in sys.argv[1:]):
        raise SystemExit('HEADLESS IS FORBIDDEN.')
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    from markdown_canvas_visible import visible_console
    # Windows can reject a foreground request transiently. Retry the complete
    # verifier, never continue on an unverified window or suppress its verdict.
    for attempt in range(3):
        try:
            visible_console()
            break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(.5)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'close.confirmed').unlink(missing_ok=True)
    sys.path.insert(0, str(ROOT / 'Tlamatini'))
    from agent.agents.talker.spanish_pronunciation import NAME_ACCENTS, browser_payload, speech_text
    from django.conf import settings
    if not settings.configured:
        settings.configure(USE_I18N=False)
    from django.utils.html import json_script
    payload = browser_payload(SimpleNamespace(username='angela', first_name=''))
    settings_tree = ast.parse((ROOT / 'Tlamatini/tlamatini/settings.py').read_text(encoding='utf-8'))
    version_node = next(node for node in settings_tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == 'STATIC_VERSION' for target in node.targets))
    version = (os.environ.get('STATIC_VERSION') or str(int(time.time()))) + version_node.value.right.value
    collected = '--collected' in sys.argv[1:]
    assets = '/Tlamatini/staticfiles/agent/js' if collected else '/Tlamatini/agent/static/agent/js'
    samples = ''
    manifest = ROOT / 'Temp/name-voice-audio/results.json'
    if manifest.exists():
        for row in json.loads(manifest.read_text(encoding='utf-8'))['voices']:
            if row.get('passed'):
                wav = Path(row['result']['output_path']).relative_to(ROOT).as_posix()
                samples += ('<p>' + html_tools.escape(row['voice']) + '</p><audio controls preload="none" src="/'
                            + html_tools.escape(wav, quote=True) + '"></audio>')
    cases = [(name, speech_text(name, payload['aliases'])) for name in NAME_ACCENTS]
    cases += [(text, speech_text(text, payload['aliases'])) for text in (
        'Hola Angela y Angéla.', 'Jose Maria, Jesus, Sofia y Raul.',
        'ANGELA, Ángela y A\u0301ngela.', 'cesar el tránsito en leon.',
        r'@angela angela@example.mx C:\Users\angela angela.py maria_01 angela42 JoseLuis',
        '`Angela` https://example.mx/angela', 'Ana, Luis y Ximena', 'Ángel y Angélica')]
    html = '''<!doctype html><html lang="es-MX"><meta charset="utf-8">
<title>Tlamatini-Spanish · Pronunciación de nombres</title>
<style>body{font:20px system-ui;background:#152034;color:#e8f1ff;margin:4rem;line-height:1.6}
button{font:inherit;padding:.7rem;background:#87dfc4;border:0;border-radius:8px}pre{white-space:pre-wrap}</style>
<h1>Ángela, con la fuerza en «Án»</h1><p>Prueba del módulo real de voz de Tlamatini-Spanish.</p>
<p>Login conservado: <code>angela</code> · Pronunciación: <strong>Ángela</strong></p>
<pre id="results">Verificando…</pre><p id="voice"></p>
<select id="voices" aria-label="Voz para escuchar"></select>
<button id="listen">Escuchar nombres (acción manual)</button>
<h2>Muestras reales: Piper y las cinco voces de Orpheus</h2>
<p>Reproducción manual. Generar un WAV no certifica de oído su pronunciación.</p>SAMPLES
<div id="tlm-avatar-bubble"></div><button id="chat-message-submit" hidden>Enviar</button>
<textarea id="chat-message-input" hidden></textarea><div id="chat-log"></div>
PAYLOAD<script src="ASSETS/voice_runtime.js?v=VERSION"></script>
<script src="ASSETS/avatar.js?v=VERSION"></script>
<script>document.getElementById('listen').onclick=()=>TLM_VOICE.speak(
'Hola Angela. Jose, Maria, Jesus, Sofia, Raul, Hector y Monica.', {force:true,
settings:{...TLM_VOICE.loadSettings(),voiceURI:document.getElementById('voices').value}});</script></html>'''
    html = html.replace('PAYLOAD', str(json_script(payload, 'tlm-speech-pronunciation')))
    html = html.replace('ASSETS', assets).replace('VERSION', version).replace('SAMPLES', samples)
    (OUT / 'index.html').write_text(html, encoding='utf-8')
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    # Existing repository hook prevents a browser child from being hidden on Windows.
    os.environ['NODE_OPTIONS'] = (os.environ.get('NODE_OPTIONS', '') + f' --require="{(ROOT / "scripts/playwright_real_visibility.cjs").as_posix()}"').strip()
    from playwright.sync_api import sync_playwright
    from chat_composer_visible_window import VisibleWindow
    import drag_divider_look_visible as photos
    photos.OUT = OUT
    result = {'checks': [], 'passed': False}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel='chrome', headless=False, slow_mo=100)
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        errors = []
        def on_error(error):
            errors.append(str(error))
            print('PAGE ERROR:', error, flush=True)
        page.on('pageerror', on_error)
        window = VisibleWindow(page, context)
        window.resize(1200, 850)
        window.activate()
        window.verify()
        page.goto(f'http://127.0.0.1:{server.server_port}/Temp/spanish-names-visible/index.html')
        page.wait_for_function('!!window.TLM_VOICE && typeof window.OpenVoiceDialog === "function"')
        page.wait_for_function('speechSynthesis.getVoices().length > 0', timeout=10000)
        window.activate()
        window.verify()
        photos.shoter('browser-visible.png')
        print('VISIBLE BROWSER VERIFIED', page.title(), flush=True)
        for name in ('voice_runtime.js', 'avatar.js'):
            delivered = page.request.get(f'http://127.0.0.1:{server.server_port}{assets}/{name}?v={version}')
            assert delivered.ok
            assert delivered.body() == (ROOT / 'Tlamatini/agent/static/agent/js' / name).read_bytes()
        result['checks'].append('Served assets match current source, with the new cache stamp')
        for text, expected in cases:
            actual = page.evaluate('(text)=>TLM_VOICE.prepareSpeech(text)', text)
            assert actual == expected, (text, expected, actual)
        result['checks'].append(f'{len(cases)} Python/browser pronunciation parity cases')
        # Verify every advertised Spanish female voice with its real native
        # utterance, preserving silence during automated development checks.
        page.locator('#results').click()
        receipt = page.evaluate('''async () => {
            const originalVoices=speechSynthesis.getVoices.bind(speechSynthesis);
            const originalSpeak=speechSynthesis.speak.bind(speechSynthesis);
            const fixtures=[{name:'Microsoft Zira',lang:'en-US',voiceURI:'old-en'},
                {name:'Microsoft Helena',lang:'es-ES',voiceURI:'es-spain'},
                {name:'Microsoft Sabina',lang:'es-MX',voiceURI:'es-mexico'}];
            speechSynthesis.getVoices=()=>fixtures;
            const selected=TLM_VOICE.pickVoice({...TLM_VOICE.loadSettings(),voiceURI:'old-en'});
            speechSynthesis.getVoices=()=>[fixtures[0]];
            const unavailable=TLM_VOICE.pickVoice();
            speechSynthesis.getVoices=originalVoices;
            const available=TLM_VOICE.femaleVoices().filter(v=>/^es(?:[-_]|$)/i.test(v.lang));
            const inventory=originalVoices().map(v=>({name:v.name,lang:v.lang,uri:v.voiceURI}));
            const tested=[];
            for(const voice of available){
                const row={name:voice.name,lang:voice.lang,uri:voice.voiceURI,utterances:[]};
                speechSynthesis.speak=u=>{
                    row.utterances.push({text:u.text,lang:u.lang,voice:u.voice.name});
                    u.volume=0;
                    originalSpeak(u);
                };
                let timeout;
                row.status=await Promise.race([
                    TLM_VOICE.speak('Hola Angela y Jose.', {force:true,
                        settings:{...TLM_VOICE.loadSettings(),voiceURI:voice.voiceURI}}),
                    new Promise(resolve=>{timeout=setTimeout(()=>{TLM_VOICE.stop();resolve('timeout');},15000);})
                ]);
                clearTimeout(timeout);
                tested.push(row);
                const option=document.createElement('option');
                option.value=voice.voiceURI;option.textContent=voice.name;
                document.getElementById('voices').append(option);
            }
            speechSynthesis.speak=originalSpeak;
            return {selected:selected.voiceURI,unavailable,inventory,tested};
        }''')
        assert receipt['selected'] == 'es-mexico', receipt
        assert receipt['unavailable'] is None, receipt
        for row in receipt['tested']:
            assert row['utterances'][0]['text'] == 'Hola Ángela y José.', row
            assert row['utterances'][0]['voice'] == row['name'], row
            assert row['utterances'][0]['lang'] == 'es-mx', row
        result['checks'].extend(['Spanish beats stale English preference', 'No English fallback for Spanish names',
                                 f"All {len(receipt['tested'])} available Spanish female voices exercised"])
        result['native_synthesis_failures'] = [row for row in receipt['tested'] if row['status'] != 'spoken']
        assert page.evaluate('TLM_VOICE.accountName') == 'Ángela'
        assert not errors, errors
        result.update(passed=not result['native_synthesis_failures'], pronunciation_cases=len(cases),
                      speech=receipt, page_errors=errors, collected=collected, static_version=version)
        (OUT / 'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        page.locator('#results').inner_text()
        page.evaluate('(t)=>document.getElementById("results").textContent=t', '\n'.join('✓ ' + item for item in result['checks']))
        page.evaluate('(t)=>document.getElementById("voice").textContent=t', 'Voces comprobadas: ' + ', '.join(row['name'] + ' (' + row['status'] + ')' for row in receipt['tested']))
        photos.shoter('completed.png')
        print(json.dumps(result, ensure_ascii=False), flush=True)
        print('Browser remains open. Create Temp/spanish-names-visible/close.confirmed to finish.', flush=True)
        while not (OUT / 'close.confirmed').exists():
            page.wait_for_timeout(500)
        browser.close()
    server.shutdown()
    if not result['passed']:
        raise SystemExit('Some native voices failed; see results.json.')


if __name__ == '__main__':
    main()
