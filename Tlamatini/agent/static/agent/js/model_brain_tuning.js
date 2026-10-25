/*
 * ═══════════════════════════════════════════════════════════════════
 *   ✦  T L A M A T I N I  ✦   —   "one who knows"
 *
 *   Created by  Angela López Mendoza   ·   @angelahack1
 *   Developer · Architect · Creator of Tlamatini
 * ═══════════════════════════════════════════════════════════════════
 *   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
 *
 * model_brain_tuning.js — the AUTO-TUNING dialog of the MODEL BRAIN
 * (agent/model_brain.py), opened after Config ▸ Models ▸ Save.
 *
 * Every model the user configured is tuned FOR REAL, one after the other:
 *   1. Ask Ollama      - /api/show: capabilities, thinking levels, context window
 *   2. Vendor settings - the formal profile (model_profiles.json, with sources),
 *                        or research of the vendor's generation_config.json
 *   3. Calibrate       - the sampling the brain will really send
 *   4. Reasoning       - thinking level + reasoning kept inside the tool loop
 * Nothing on screen is invented: each stage shows what the server answered
 * (POST /agent/model_brain/tune/).  The four stages of one model are revealed
 * one by one after the server finished them, so the user can read them.
 *
 * Self-contained IIFE: no cross-file globals.  Exports window.TlmModelBrainTuning
 * = { open(options), close() }.  Escape and the ✕ close it (dialog_policy.js
 * calls overlay.tlmDismiss); an outside click never does.  Fail-open: a broken
 * dialog never blocks saving the models.
 */
(function () {
    'use strict';

    const OVERLAY_ID = 'tlm-tuning-overlay';
    const REDUCED = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    const REVEAL_MS = REDUCED ? 0 : 280;
    const STAGES = [
        { key: 'ollama', name: 'Consultar a Ollama', wait: '¿qué puede hacer este modelo?' },
        { key: 'profile', name: "Configuración del fabricante", wait: 'perfil formal o investigación' },
        { key: 'sampling', name: 'Calibrar el sampling', wait: 'los valores que se envían' },
        { key: 'reasoning', name: 'Pensamiento y razonamiento', wait: 'niveles y memoria del tool loop' }
    ];

    let runToken = 0;
    let onClose = null;
    let lastFocus = null;

    function el(tag, cls, text) {
        const node = document.createElement(tag);
        if (cls) { node.className = cls; }
        if (text !== undefined && text !== null) { node.textContent = String(text); }
        return node;
    }

    function sleep(ms) {
        return new Promise(function (resolve) { setTimeout(resolve, ms); });
    }

    function csrfToken() {
        const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    async function fetchJson(url, options) {
        const init = Object.assign({ credentials: 'same-origin' }, options || {});
        if (init.method === 'POST') {
            init.headers = { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() };
        }
        const response = await fetch(url, init);
        let body;
        try { body = await response.json(); } catch (err) { body = null; }
        if (!response.ok || !body || body.success !== true) {
            throw new Error((body && body.error) || ('HTTP ' + response.status));
        }
        return body;
    }

    function close() {
        runToken += 1;
        const overlay = document.getElementById(OVERLAY_ID);
        if (overlay && overlay.parentNode) { overlay.parentNode.removeChild(overlay); }
        try { if (lastFocus && lastFocus.focus) { lastFocus.focus(); } } catch (err) { /* noop */ }
        const callback = onClose;
        onClose = null;
        if (typeof callback === 'function') {
            try { callback(); } catch (err) { /* the follow-up dialog is optional */ }
        }
    }

    // ── one model card ────────────────────────────────────────────────
    function buildCard(row) {
        const card = el('li', 'tlmtune-model');
        card.setAttribute('data-model', row.model);
        const head = el('div', 'tlmtune-model-head');
        head.appendChild(el('span', 'tlmtune-model-name', row.model));
        head.appendChild(row.applied
            ? el('span', 'tlmtune-chip tlmtune-chip-applied', 'APLICADO AL CEREBRO')
            : el('span', 'tlmtune-chip tlmtune-chip-profiled', 'PERFILADO'));
        card.appendChild(head);
        card.appendChild(el('div', 'tlmtune-used-by', 'Usado por: ' + (row.used_by || []).join(' · ')));
        const stages = el('div', 'tlmtune-stages');
        STAGES.forEach(function (stage) {
            const box = el('div', 'tlmtune-stage');
            box.setAttribute('data-stage', stage.key);
            box.appendChild(el('span', 'tlmtune-dot'));
            const text = el('span', 'tlmtune-stage-text');
            text.appendChild(el('span', 'tlmtune-stage-name', stage.name));
            text.appendChild(el('span', 'tlmtune-stage-detail', stage.wait));
            box.appendChild(text);
            stages.appendChild(box);
        });
        card.appendChild(stages);
        const result = el('div', 'tlmtune-result');
        result.hidden = true;
        card.appendChild(result);
        card.appendChild(el('div', 'tlmtune-sources'));
        return card;
    }

    function setStage(card, key, state, detail) {
        const box = card.querySelector('[data-stage="' + key + '"]');
        if (!box) { return; }
        box.classList.remove('is-running', 'is-done', 'is-warn');
        if (state) { box.classList.add('is-' + state); }
        const dot = box.querySelector('.tlmtune-dot');
        if (dot) { dot.textContent = state === 'done' ? '✓' : (state === 'warn' ? '!' : ''); }
        if (detail !== undefined) {
            const text = box.querySelector('.tlmtune-stage-detail');
            if (text) { text.textContent = detail; }
        }
    }

    function param(container, key, value) {
        const chip = el('span', 'tlmtune-param');
        chip.appendChild(el('span', 'tlmtune-param-key', key));
        chip.appendChild(el('span', null, value));
        container.appendChild(chip);
    }

    function thinkingText(data) {
        const facts = data.facts || {};
        if (!(facts.capabilities || []).includes('thinking')) { return 'no piensa'; }
        const levels = (facts.thinking_values || []).map(String).join(' · ') || '?';
        return 'niveles ' + levels + ' — ' + (data.think_note || 'predeterminado del modelo');
    }

    function renderResult(card, data) {
        const result = card.querySelector('.tlmtune-result');
        const sampling = data.sampling || {};
        Object.keys(sampling).sort().forEach(function (key) { param(result, key, sampling[key]); });
        if (!Object.keys(sampling).length) { param(result, 'sampling', "los valores predeterminados del modelo"); }
        const facts = data.facts || {};
        if ((facts.capabilities || []).includes('thinking')) {
            param(result, 'thinking', String(facts.thinking_default) + ' (predeterminado del modelo)');
            param(result, 'razonamiento en tool loops', data.keep_reasoning ? 'se conserva' : 'ninguno (thinking desactivado)');
        }
        if (data.num_ctx) { param(result, 'contexto', Number(data.num_ctx).toLocaleString() + ' tokens'); }
        result.hidden = false;
        const sources = card.querySelector('.tlmtune-sources');
        const links = (data.sources || []).filter(function (url) { return /^https:\/\//i.test(String(url)); });
        if (links.length) {
            sources.appendChild(document.createTextNode('Fuentes: '));
            links.forEach(function (url, index) {
                const a = el('a', null, url.replace(/^https:\/\//i, ''));
                a.href = url;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                sources.appendChild(a);
                if (index < links.length - 1) { sources.appendChild(document.createTextNode('  ·  ')); }
            });
        } else if (data.sampling_origin) {
            sources.textContent = 'Origen: ' + data.sampling_origin;
        }
    }

    async function tuneOne(card, row, token) {
        card.classList.add('is-running');
        setStage(card, 'ollama', 'running');
        let data;
        try {
            data = await fetchJson('/agent/model_brain/tune/', { method: 'POST', body: JSON.stringify({ model: row.model }) });
        } catch (err) {
            if (token !== runToken) { return null; }
            setStage(card, 'ollama', 'warn', 'no se pudo ajustar: ' + err.message);
            card.classList.remove('is-running');
            card.classList.add('is-warn');
            return { ok: false };
        }
        if (token !== runToken) { return null; }
        const steps = data.steps || [];
        const step = function (key) { return steps.find(function (s) { return s.step === key; }); };

        const asked = step('ollama');
        setStage(card, 'ollama', asked && asked.ok ? 'done' : 'warn', asked ? asked.detail : '');
        await sleep(REVEAL_MS);
        if (token !== runToken) { return null; }

        if (!data.tunable) {
            const skip = step('skip');
            ['profile', 'sampling', 'reasoning'].forEach(function (key) {
                setStage(card, key, 'done', key === 'profile' && skip ? skip.detail : 'no hace falta');
            });
            card.classList.remove('is-running');
            card.classList.add('is-skip');
            return { ok: true, skipped: true };
        }

        const research = step('research');
        const profile = step('profile');
        if (research) {
            setStage(card, 'profile', 'running', research.detail);
            await sleep(REVEAL_MS * 2);
            if (token !== runToken) { return null; }
        }
        setStage(card, 'profile', profile && profile.ok ? 'done' : 'warn', profile ? profile.detail : '');
        await sleep(REVEAL_MS);
        if (token !== runToken) { return null; }

        const keys = Object.keys(data.sampling || {}).sort();
        setStage(card, 'sampling', keys.length ? 'done' : 'warn',
            keys.length ? keys.map(function (k) { return k + ' ' + data.sampling[k]; }).join(', ') : "los valores predeterminados del modelo");
        await sleep(REVEAL_MS);
        if (token !== runToken) { return null; }

        setStage(card, 'reasoning', 'done', thinkingText(data));
        renderResult(card, data);
        card.classList.remove('is-running');
        card.classList.add(profile && profile.ok ? 'is-done' : 'is-warn');
        return { ok: true, profiled: !!(profile && profile.ok), researched: !!research, applied: !!row.applied };
    }

    // ── the dialog ────────────────────────────────────────────────────
    async function open(options) {
        const opts = options || {};
        const existing = document.getElementById(OVERLAY_ID);
        if (existing && existing.parentNode) { existing.parentNode.removeChild(existing); }
        runToken += 1;
        const token = runToken;
        onClose = typeof opts.onClose === 'function' ? opts.onClose : null;
        lastFocus = document.activeElement;

        const overlay = el('div', 'tlmpop-overlay tlmtune-overlay');
        overlay.id = OVERLAY_ID;
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.setAttribute('aria-labelledby', 'tlmtune-title');

        const card = el('div', 'tlmpop-card tlmtune-card');
        const head = el('div', 'tlmpop-head');
        const title = el('span', 'tlmpop-title tlmtune-title');
        title.id = 'tlmtune-title';
        title.appendChild(el('span', 'tlmtune-mark'));
        const titleText = el('span', null, "Ajustando automáticamente el cerebro de Tlamatini");
        title.appendChild(titleText);
        const x = el('button', 'tlmpop-x', '×');
        x.type = 'button';
        x.setAttribute('aria-label', 'Cerrar');
        x.addEventListener('click', close);
        head.appendChild(title);
        head.appendChild(x);

        const body = el('div', 'tlmpop-body');
        body.appendChild(el('p', 'tlmtune-lead',
            'Tlamatini se está ajustando para cada modelo que elegiste: le pregunta a Ollama qué puede hacer cada modelo, ' +
            "aplica la configuración que publica su fabricante (o la investiga) y conserva el razonamiento de un modelo con thinking " +
            'entre los pasos de tools, como lo documentan los fabricantes.'));
        const progress = el('div', 'tlmtune-progress');
        const bar = el('div', 'tlmtune-bar');
        const fill = el('div', 'tlmtune-bar-fill');
        bar.appendChild(fill);
        const progressText = el('div', 'tlmtune-progress-text');
        const counter = el('span', null, 'Leyendo tus modelos…');
        counter.setAttribute('aria-live', 'polite');
        const current = el('span', null, '');
        progressText.appendChild(counter);
        progressText.appendChild(current);
        progress.appendChild(bar);
        progress.appendChild(progressText);
        body.appendChild(progress);
        const list = el('ul', 'tlmtune-list');
        body.appendChild(list);

        const foot = el('div', 'tlmpop-foot');
        const note = el('span', 'tlmtune-foot-note', '');
        const ok = el('button', 'tlmpop-btn tlmpop-btn-primary', 'Aceptar');
        ok.type = 'button';
        ok.addEventListener('click', close);
        foot.appendChild(note);
        foot.appendChild(ok);

        card.appendChild(head);
        card.appendChild(body);
        card.appendChild(foot);
        overlay.appendChild(card);
        overlay.tlmDismiss = close;          // dialog_policy.js: Escape -> our own close
        document.body.appendChild(overlay);
        try { ok.focus(); } catch (err) { /* noop */ }

        let rows;
        try {
            const data = await fetchJson('/agent/model_brain/models/');
            rows = data.models || [];
            if (data.enabled === false) {
                counter.textContent = 'Model Brain está DESACTIVADO (model_brain = "off" en config.json): se usan los parámetros fijos de antes.';
                card.classList.add('tlmtune-done');
                return;
            }
        } catch (err) {
            counter.textContent = 'No se pudieron leer los modelos configurados: ' + err.message;
            card.classList.add('tlmtune-done');
            return;
        }
        if (token !== runToken) { return; }
        if (!rows.length) {
            counter.textContent = 'No hay modelos de Ollama configurados.';
            card.classList.add('tlmtune-done');
            return;
        }

        const cards = rows.map(function (row) {
            const node = buildCard(row);
            list.appendChild(node);
            return node;
        });
        let done = 0;
        let profiled = 0;
        let researched = 0;
        for (let i = 0; i < rows.length; i += 1) {
            if (token !== runToken) { return; }
            counter.textContent = 'Ajustando ' + (i + 1) + ' de ' + rows.length;
            current.textContent = rows[i].model;
            try { cards[i].scrollIntoView({ block: 'nearest', behavior: REDUCED ? 'auto' : 'smooth' }); } catch (err) { /* noop */ }
            const outcome = await tuneOne(cards[i], rows[i], token);
            if (token !== runToken) { return; }
            done += 1;
            if (outcome && outcome.profiled) { profiled += 1; }
            if (outcome && outcome.researched) { researched += 1; }
            fill.style.width = Math.round(done * 100 / rows.length) + '%';
        }
        counter.textContent = 'Se ajustaron ' + done + ' de ' + rows.length + ' modelos';
        current.textContent = '';
        titleText.textContent = "El cerebro de Tlamatini quedó ajustado";
        card.classList.add('tlmtune-done');
        note.textContent = profiled + ' con la configuración publicada por el fabricante' +
            (researched ? ' · ' + researched + ' con investigación nueva' : '') +
            ' · se aplica en la siguiente solicitud';
        try { ok.focus(); } catch (err) { /* noop */ }
    }

    window.TlmModelBrainTuning = { open: open, close: close };
})();
