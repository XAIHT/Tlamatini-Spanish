/* Tlamatini Author Banner — Angela López Mendoza */
/* Shared speech lifecycle for chat, editor tutoring and the two flow panels. */
(() => {
    'use strict';
    if (window.TLM_VOICE) return;
    const FEMALE = /female|zira|jenny|aria|michelle|clara|nanami|sara|hazel|heera|catherine|hedda|elsa|paulina|helena|laura|isabel|sabina|dalia|renata|ximena|google espa[nñ]ol|woman|girl|monica|google us english|google uk english female|samantha|victoria|karen|tessa|fiona|moira|serena|allison|ava|susan|zoe|nora|mia|jess|tara|leah/i;
    const MALE = /\bmale\b|david|mark|guy|ryan|george|james|richard|paul\b|thomas|daniel|alex\b|fred|diego|jorge|pablo|javi|sergio|raul|miguel|andres|\bman\b|\bboy\b/i;
    const defaults = { mode: 'notify', voiceURI: '', volume: 100, rate: 1, pitch: 1.05, lang: '' };
    let memory = { ...defaults }, active = null, listening = false;
    const queue = [];
    let pronunciation = {};
    try { pronunciation = JSON.parse(document.getElementById('tlm-speech-pronunciation')?.textContent || '{}'); }
    catch { /* A missing optional payload must not break text chat. */ }
    const foldName = value => value.toLowerCase().normalize('NFD').replace(/́/g, '').normalize('NFC');
    const names = pronunciation.names || {};
    const ambiguous = new Set(pronunciation.ambiguous || []);
    const aliases = new Map(Object.entries(pronunciation.aliases || {}).map(([key, value]) => [key.normalize('NFC').toLowerCase(), value]));
    // Python and JS have different definitions of \w. Use Unicode properties
    // in the browser so a name never matches inside another script's identifier.
    const tokenPattern = pronunciation.token_pattern?.replaceAll('[^\\W\\d_]+', '[\\p{L}\\p{M}]+')
        .replaceAll('[\\w', '[\\p{L}\\p{M}\\p{N}_')
        .replaceAll('\\w', '[\\p{L}\\p{M}\\p{N}_]');
    const nameTokens = tokenPattern ? new RegExp(tokenPattern, 'gu') : null;
    function prepareSpeech(text, settings = loadSettings()) {
        text = String(text || '').normalize('NFC');
        if (langBase(preferredLang(settings)) !== 'es' || !nameTokens) return text;
        return text.replace(nameTokens, token => {
            const alias = aliases.get(token.toLowerCase());
            if (alias && !/[@/\\<>`]/.test(token)) return alias;
            if (!/^[\p{L}\p{M}]+$/u.test(token)) return token;
            const key = foldName(token);
            if (token === token.toLowerCase() && ambiguous.has(key)) return token;
            if (key !== 'angela' && /[áéíóú]/i.test(token)) return token;
            const replacement = names[key];
            if (!replacement) return token;
            if (token === token.toUpperCase()) return replacement.toUpperCase();
            if (token === token.toLowerCase()) return replacement.toLowerCase();
            return replacement;
        });
    }
    function loadSettings() {
        try { memory = { ...defaults, ...JSON.parse(localStorage.getItem('tlm_voice_settings') || '{}') }; }
        catch { /* Keep the usable in-memory settings. */ }
        return { ...memory };
    }
    function saveSettings(value) {
        memory = { ...defaults, ...value };
        try { localStorage.setItem('tlm_voice_settings', JSON.stringify(memory)); } catch { /* This tab retains the choice. */ }
        if (memory.mode === 'silent') halt('muted', true);
        syncHost();
        window.dispatchEvent(new CustomEvent('tlm:voice-settings'));
    }
    // Preferred speech language: an explicit setting, else the page's own <html lang>
    // (es-MX in the Spanish edition, en-US in the English edition), else the browser locale.
    // Keeps this logic language-NEUTRAL — the edition's own page tag drives it.
    function preferredLang(settings) {
        const s = settings || memory;
        return String((s && s.lang) || document.documentElement.lang || navigator.language || '').trim().toLowerCase().replace('_', '-');
    }
    function langBase(tag) { return String(tag || '').toLowerCase().split('-')[0]; }
    function voiceLang(voice) { return String(voice && voice.lang || '').toLowerCase().replace('_', '-'); }
    // Latin-American Spanish regions, most-preferred first; es-ES (Castilian) sorts last.
    const LATAM_ES = ['es-mx', 'es-us', 'es-419', 'es-ar', 'es-co', 'es-cl', 'es-pe', 'es-ve', 'es-ec', 'es-gt', 'es-cr', 'es-pa', 'es-do', 'es-uy', 'es-py', 'es-bo', 'es-hn', 'es-ni', 'es-sv', 'es-pr'];
    function femaleVoices() {
        // STRICTLY female: a voice is offered ONLY when its name is a verified-female
        // name (FEMALE above — which includes the Latin-American es voices Sabina/Dalia
        // and Google's Spanish voices) AND not a male name. Tlamatini must NEVER speak
        // with a male voice. Spanish pages never fall back to an English
        // pronunciation; with no Spanish female browser voice, her host voice speaks.
        // A gender-neutral/unknown voice is deliberately NOT accepted.
        return (window.speechSynthesis?.getVoices() || []).filter(voice => FEMALE.test(voice.name) && !MALE.test(voice.name));
    }
    function pickVoice(settings = loadSettings()) {
        const voices = femaleVoices();
        if (!voices.length) return null;
        const want = preferredLang(settings), base = langBase(want);
        const saved = voices.find(voice => voice.voiceURI === settings.voiceURI);
        // A saved English default from another edition must not anglicize names.
        if (saved && (base !== 'es' || langBase(saved.lang) === 'es')) return saved;
        if (base) {
            const exact = voices.find(voice => voiceLang(voice) === want);   // es-MX beats es-US/es-ES
            if (exact) return exact;
            const sameBase = voices.filter(voice => langBase(voice.lang) === base);
            if (sameBase.length) {
                if (base === 'es') {   // prefer a Latin-American region; Castilian (es-ES) last
                    const rank = v => { const i = LATAM_ES.indexOf(voiceLang(v)); return i < 0 ? 99 : i; };
                    sameBase.sort((a, b) => rank(a) - rank(b));
                }
                return sameBase[0];
            }
        }
        if (base === 'es') return null;
        return voices.find(voice => /zira|jenny|aria|samantha|google us english|hazel/i.test(voice.name)) || voices[0] || null;
    }
    // Tag the utterance with the preferred regional locale when the voice's base
    // language matches, so a generic 'es' voice is rendered as es-MX.
    function utteranceLang(voice, settings) {
        const want = preferredLang(settings);
        return (want && langBase(voice.lang) === langBase(want)) ? want : (voice.lang || want || '');
    }

    // ── SHE FINISHES WHAT SHE STARTS (Angela, 2026-11-11) ─────────────────────
    // "if I change the application focus the voice stops and that should not
    // happen ... make her unstoppable once she started to speak". This engine
    // used to pause whenever the page was hidden (Windows reports a covered
    // window as hidden), ended every message after 100 seconds, and dropped the
    // rest of a message the moment one chunk failed - so the queue behind it,
    // including "I'm working on your request", went silent too. Now:
    //   * nothing pauses her: a hidden, covered or unfocused page keeps talking;
    //   * a chunk the engine drops, interrupts or never starts is spoken again;
    //   * a browser that still cannot speak, and a page that closes in the
    //     middle of a sentence, hand the rest to her HOST VOICE - Windows on this
    //     computer's speakers (agent/host_voice.py) - in the user's settings.
    // Only the user stops her: Silent mode, Escape, clicking her, Cancel.
    const HOST_URL = '/agent/voice/host/';
    const START_MS = 8000;        // a chunk must begin this long after the engine is free
    const START_MAX_MS = 60000;   // ...or this long at most while another voice holds the engine
    const RETRIES = 3;            // a failing chunk is spoken again this many times
    const OUTSIDE_LIMIT = 20;     // interruptions from another page before the host takes over
    let hostBusy = true;          // a page that closed may have handed its speech to the host
    let hostSpeaking = false;
    let channel = null;
    function chunks(text) { return text.match(/[\s\S]{1,170}(?:\s|$)|[\s\S]{1,170}/g) || []; }
    function csrfToken() {
        // The Spanish edition has its own cookie, so it never sends the English one.
        const match = document.cookie.match(/(?:^|;\s*)tlm_csrf_es_mx=([^;]*)/);
        return match ? decodeURIComponent(match[1]) : '';
    }
    function hostCall(path, body) {
        const init = { credentials: 'same-origin', headers: { 'X-CSRFToken': csrfToken() } };
        if (body !== undefined) {
            init.method = 'POST';
            init.headers['Content-Type'] = 'application/json';
            init.body = JSON.stringify(body);
        }
        return fetch(HOST_URL + path, init).then(response => response.ok ? response.json() : Promise.reject(new Error('HTTP ' + response.status)));
    }
    function hostSettings(settings, voice) {
        return { mode: settings.mode, volume: Number(settings.volume), rate: Number(settings.rate), pitch: Number(settings.pitch),
            voice: voice?.name || '', lang: voice?.lang || preferredLang(settings) };
    }
    let syncTimer = null;
    function syncHost() {
        clearTimeout(syncTimer);
        syncTimer = setTimeout(() => {
            const settings = loadSettings();
            hostCall('settings/', hostSettings(settings, pickVoice(settings))).catch(() => { /* The host voice is optional. */ });
        }, 400);
    }
    function refreshHost() {
        return hostCall('status/').then(reply => { hostSpeaking = hostBusy = !!reply.busy; return hostBusy; })
            .catch(() => { hostSpeaking = hostBusy = false; return false; });
    }
    function finish(item, status) {
        if (item.done) return;
        item.done = true;
        clearTimeout(item.watch);
        item.signal?.removeEventListener('abort', item.abort);
        if (active === item) active = null;
        item.resolve(status);
        queueMicrotask(pump);
    }
    // Stops this page's speech; `everywhere` also stops her in the user's other
    // pages and on the host, because the user asked her to stop talking.
    function halt(reason = 'cancelled', everywhere = false) {
        const pending = queue.splice(0);
        if (active) pending.unshift(active);
        const hosted = pending.some(item => item.hostJob);
        pending.forEach(item => finish(item, reason));
        try { window.speechSynthesis?.cancel(); } catch { /* Speech may be unavailable. */ }
        if (hosted || everywhere && hostSpeaking) { hostSpeaking = false; hostCall('stop/', {}).catch(() => { /* The host voice is optional. */ }); }
        if (everywhere) { try { channel?.postMessage({ type: 'stop', reason }); } catch { /* Other pages keep their own controls. */ } }
        window.dispatchEvent(new CustomEvent('tlm:voice-stopped', { detail: reason }));
    }
    function pump() {
        if (active || !queue.length) return;
        const item = queue.shift();
        active = item;
        const settings = item.settings || loadSettings();
        item.settings = settings;
        if (item.signal?.aborted) return finish(item, 'cancelled');
        if (listening || settings.mode === 'silent' && !item.force || Number(settings.volume) === 0) return finish(item, 'muted');
        item.pieces = chunks(prepareSpeech(item.text, settings));
        item.index = 0;
        // While her host voice is still finishing a closed page's sentence,
        // queue behind it there: one voice, in order, never two at once.
        if (hostBusy) {
            return refreshHost().then(busy => {
                if (item.done) return;
                if (busy) toHost(item, 'host voice already speaking'); else browserSpeak(item);
            });
        }
        browserSpeak(item);
    }
    function browserSpeak(item) {
        const synth = window.speechSynthesis;
        if (!synth || !window.SpeechSynthesisUtterance) return toHost(item, 'no browser speech');
        item.voice = pickVoice(item.settings);
        if (item.voice) return speakPiece(item);
        if (synth.getVoices().length) return toHost(item, 'no female browser voice');
        // Chrome lists its voices a moment after the page loads: wait for them.
        let settled = false;
        const ready = () => {
            if (settled) return;
            settled = true;
            synth.removeEventListener?.('voiceschanged', ready);
            if (item.done) return;
            item.voice = pickVoice(item.settings);
            if (item.voice) speakPiece(item); else toHost(item, 'no female browser voice');
        };
        synth.addEventListener?.('voiceschanged', ready);
        item.watch = setTimeout(ready, 3000);
    }
    function speakPiece(item) {
        if (item.done) return;
        clearTimeout(item.watch);
        if (item.index >= item.pieces.length) return finish(item, 'spoken');
        const synth = window.speechSynthesis, settings = item.settings, voice = item.voice;
        try { if (synth.paused) synth.resume(); } catch { /* Resume is best-effort. */ }
        const text = item.pieces[item.index];
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = voice; utterance.lang = utteranceLang(voice, settings);
        utterance.volume = Math.max(0, Math.min(1, settings.volume / 100));
        utterance.rate = Math.max(.5, Math.min(2, settings.rate));
        utterance.pitch = Math.max(0, Math.min(2, settings.pitch));
        item.utterance = utterance;
        const owns = () => item.utterance === utterance && !item.done;
        const queuedAt = Date.now();
        const waitStart = () => {
            item.watch = setTimeout(() => {
                if (!owns()) return;
                let busy = false;
                try { busy = synth.speaking; } catch { /* Treat an unreadable engine as idle. */ }
                // Another page may hold the shared engine; give it time before retrying.
                if (busy && Date.now() - queuedAt < START_MAX_MS) return waitStart();
                item.utterance = null;
                try { if (busy) synth.cancel(); } catch { /* A stuck engine is cleared best-effort. */ }
                retry(item, 'never started');
            }, START_MS);
        };
        utterance.onstart = () => {
            if (!owns()) return;
            clearTimeout(item.watch);
            const rate = Math.max(.5, Number(settings.rate) || 1);
            item.watch = setTimeout(() => {
                if (!owns()) return;
                item.utterance = null;
                try { synth.cancel(); } catch { /* A stuck engine is cleared best-effort. */ }
                retry(item, 'stalled');
            }, 15000 + Math.ceil(text.length / (5 * rate)) * 1000);
        };
        utterance.onend = () => {
            if (!owns()) return;
            clearTimeout(item.watch);
            item.utterance = null;
            item.attempts = 0;
            item.index += 1;
            speakPiece(item);
        };
        utterance.onerror = event => {
            if (!owns()) return;
            clearTimeout(item.watch);
            item.utterance = null;
            retry(item, event?.error || 'error');
        };
        waitStart();
        try { synth.speak(utterance); }
        catch { if (owns()) { clearTimeout(item.watch); item.utterance = null; retry(item, 'speak failed'); } }
    }
    function retry(item, why) {
        if (item.done) return;
        // No click or key on this page yet: the browser refuses, the host can speak.
        if (why === 'not-allowed') return toHost(item, why);
        // Another page of the same site cancelled the shared engine: keep going.
        if (why === 'interrupted' || why === 'canceled') {
            item.outside = (item.outside || 0) + 1;
            if (item.outside <= OUTSIDE_LIMIT) return void setTimeout(() => speakPiece(item), 200);
        }
        item.attempts = (item.attempts || 0) + 1;
        if (item.attempts > RETRIES) return toHost(item, why);
        setTimeout(() => speakPiece(item), 300 * item.attempts);
    }
    function toHost(item, why) {
        if (item.done) return;
        clearTimeout(item.watch);
        const text = (item.pieces || []).slice(item.index || 0).join('').trim();
        if (!text) return finish(item, 'spoken');
        hostCall('speak/', { text, settings: hostSettings(item.settings, item.voice || pickVoice(item.settings)), reason: why })
            .then(reply => {
                if (!reply.job_id) throw new Error('The host voice is unavailable.');
                if (item.done) { hostCall('stop/', {}).catch(() => { /* Optional. */ }); return; }
                item.hostJob = reply.job_id;
                hostSpeaking = hostBusy = true;
                const poll = () => {
                    if (item.done) return;
                    hostCall('status/?job=' + encodeURIComponent(item.hostJob)).then(state => {
                        if (item.done) return;
                        if (state.state === 'queued' || state.state === 'speaking') return void setTimeout(poll, 700);
                        hostSpeaking = hostBusy = !!state.busy;
                        finish(item, state.state === 'done' ? 'spoken' : state.state === 'stopped' ? 'cancelled' : 'unavailable');
                    }).catch(() => setTimeout(poll, 1500));
                };
                poll();
            })
            .catch(() => finish(item, 'unavailable'));
    }
    function speak(text, options = {}) {
        text = String(text || '').trim();
        if (!text) return Promise.resolve('spoken');
        if (!options.queue && !active?.interaction) halt();
        return new Promise(resolve => {
            const item = { ...options, text, resolve, done: false };
            item.abort = () => {
                if (active === item) halt();
                else { const index = queue.indexOf(item); if (index >= 0) queue.splice(index, 1); finish(item, 'cancelled'); }
            };
            item.signal?.addEventListener('abort', item.abort, { once: true });
            queue.push(item);
            pump();
        });
    }
    // A page that closes mid-sentence hands the rest to her host voice.
    function handOff() {
        const settings = loadSettings();
        if (settings.mode === 'silent' || listening || Number(settings.volume) === 0) return;
        const parts = [];
        if (active && !active.done && !active.hostJob && !active.interaction && active.pieces) parts.push(active.pieces.slice(active.index).join(''));
        for (const item of queue) if (!item.done && !item.interaction && !item.signal?.aborted) parts.push(prepareSpeech(item.text, item.settings || settings));
        const text = parts.join(' ').trim();
        if (!text) return;
        const body = new FormData();
        body.append('csrfmiddlewaretoken', csrfToken());
        body.append('payload', JSON.stringify({ text, settings: hostSettings(settings, active?.voice || pickVoice(settings)), reason: 'page closed while speaking' }));
        try { navigator.sendBeacon(HOST_URL + 'speak/', body); } catch { /* The page is already closing. */ }
    }
    function isSpeaking() {
        let engine = false;
        try { engine = !!(window.speechSynthesis && (window.speechSynthesis.speaking || window.speechSynthesis.pending)); } catch { /* Treat an unavailable engine as idle. */ }
        return !!active || queue.length > 0 || engine || hostSpeaking;
    }
    function setSilent(on) { const settings = loadSettings(); settings.mode = on ? 'silent' : 'notify'; saveSettings(settings); return settings.mode; }
    // Speech begins only from a user-enabled feature. A click can resume a paused browser engine.
    function prime() { try { window.speechSynthesis?.resume(); } catch { /* Optional browser capability. */ } }
    const stop = (reason = 'cancelled') => halt(reason, true);
    window.TLM_VOICE = { speak, stop, prime, loadSettings, saveSettings, femaleVoices, pickVoice, setSilent, isSpeaking,
        prepareSpeech, accountName: pronunciation.display_name || '',
        notify: () => speak('Ya terminé tu solicitud.'),
        setListening: on => { listening = !!on; if (on) halt('muted', true); },
        get listening() { return listening; } };
    try {
        channel = new BroadcastChannel('tlm-voice');
        channel.onmessage = event => { if (event.data?.type === 'stop') halt(event.data.reason || 'cancelled', false); };
    } catch { /* A browser without BroadcastChannel keeps per-page controls. */ }
    // Escape stops her, unless a dialog used that Escape to close itself.
    window.addEventListener('keydown', event => { if (event.key === 'Escape' && !event.defaultPrevented) stop(); });
    document.addEventListener('keydown', event => {
        if (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === 'm') {
            event.preventDefault(); event.stopImmediatePropagation(); setSilent(loadSettings().mode !== 'silent');
        }
    }, true);
    window.addEventListener('storage', event => {
        if (event.key !== 'tlm_voice_settings') return;
        if (loadSettings().mode === 'silent') halt('muted', false);
        syncHost();
    });
    // Never pause her when the page is hidden or covered; wake a paused engine.
    document.addEventListener('visibilitychange', () => { try { if (window.speechSynthesis?.paused) window.speechSynthesis.resume(); } catch { /* Best-effort. */ } });
    setInterval(() => { try { if (active && window.speechSynthesis?.paused) window.speechSynthesis.resume(); } catch { /* Best-effort. */ } }, 5000);
    window.addEventListener('pagehide', handOff);
    try { window.speechSynthesis?.addEventListener?.('voiceschanged', syncHost); } catch { /* Optional. */ }
    document.addEventListener('click', prime, { once: true });
    syncHost();
    refreshHost();
})();
