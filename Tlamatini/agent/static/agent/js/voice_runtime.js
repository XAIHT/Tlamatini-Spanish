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
    const foldName = value => value.toLowerCase().normalize('NFD').replace(/\u0301/g, '').normalize('NFC');
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
        if (memory.mode === 'silent') stop('muted');
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
        // with a male voice. Spanish pages remain silent if no Spanish female
        // voice is available; they never fall back to an English pronunciation.
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
    function finish(item, status) {
        if (item.done) return;
        item.done = true;
        clearTimeout(item.timer);
        item.signal?.removeEventListener('abort', item.abort);
        if (active === item) active = null;
        item.resolve(status);
        queueMicrotask(pump);
    }
    function stop(reason = 'cancelled') {
        const pending = queue.splice(0);
        if (active) pending.unshift(active);
        pending.forEach(item => finish(item, reason));
        try { window.speechSynthesis?.cancel(); } catch { /* Speech may be unavailable. */ }
        window.dispatchEvent(new CustomEvent('tlm:voice-stopped', { detail: reason }));
    }
    function pump() {
        if (active || !queue.length) return;
        const item = queue.shift();
        active = item;
        const settings = item.settings || loadSettings();
        if (item.signal?.aborted) return finish(item, 'cancelled');
        if (listening || settings.mode === 'silent' && !item.force || Number(settings.volume) === 0) return finish(item, 'muted');
        const voice = pickVoice(settings);
        if (!voice || !window.speechSynthesis || !window.SpeechSynthesisUtterance) return finish(item, 'unavailable');
        // Queue a chunk only after the previous chunk ends. Cancel never leaves stale chunks.
        const pieces = prepareSpeech(item.text, settings).match(/[\s\S]{1,170}(?:\s|$)|[\s\S]{1,170}/g) || [];
        let index = 0;
        item.timer = setTimeout(() => { stop('unavailable'); }, 100000);
        function next() {
            if (item.done) return;
            if (index >= pieces.length) return finish(item, 'spoken');
            const utterance = new SpeechSynthesisUtterance(pieces[index++]);
            utterance.voice = voice;
            // Tag the utterance with the preferred regional locale when the voice's base
            // language matches, so a generic 'es' voice is rendered as es-MX.
            const want = preferredLang(settings);
            utterance.lang = (want && langBase(voice.lang) === langBase(want)) ? want : (voice.lang || want || '');
            utterance.volume = Math.max(0, Math.min(1, settings.volume / 100));
            utterance.rate = Math.max(.5, Math.min(2, settings.rate));
            utterance.pitch = Math.max(0, Math.min(2, settings.pitch));
            utterance.onend = next;
            utterance.onerror = () => finish(item, 'unavailable');
            try { window.speechSynthesis.speak(utterance); } catch { finish(item, 'unavailable'); }
        }
        next();
    }
    function speak(text, options = {}) {
        text = String(text || '').trim();
        if (!text) return Promise.resolve('spoken');
        if (!options.queue && !active?.interaction) stop();
        return new Promise(resolve => {
            const item = { ...options, text, resolve, done: false };
            item.abort = () => {
                if (active === item) stop();
                else { const index = queue.indexOf(item); if (index >= 0) queue.splice(index, 1); finish(item, 'cancelled'); }
            };
            item.signal?.addEventListener('abort', item.abort, { once: true });
            queue.push(item);
            pump();
        });
    }
    function setSilent(on) { const settings = loadSettings(); settings.mode = on ? 'silent' : 'notify'; saveSettings(settings); return settings.mode; }
    // Speech begins only from a user-enabled feature. A click can resume a paused browser engine.
    function prime() { try { window.speechSynthesis?.resume(); } catch { /* Optional browser capability. */ } }
    window.TLM_VOICE = { speak, stop, prime, loadSettings, saveSettings, femaleVoices, pickVoice, setSilent,
        prepareSpeech, accountName: pronunciation.display_name || '',
        notify: () => speak('Ya terminé tu solicitud.'),
        setListening: on => { listening = !!on; if (on) stop('muted'); },
        get listening() { return listening; } };
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') stop();
        if (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === 'm') {
            event.preventDefault(); event.stopImmediatePropagation(); setSilent(loadSettings().mode !== 'silent');
        }
    }, true);
    window.addEventListener('storage', event => { if (event.key === 'tlm_voice_settings' && loadSettings().mode === 'silent') stop('muted'); });
    document.addEventListener('click', prime, { once: true });
})();
