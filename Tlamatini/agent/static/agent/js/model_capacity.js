/*
 * ═══════════════════════════════════════════════════════════════════
 *   ✦  T L A M A T I N I  ✦   —   "one who knows"
 *
 *   Created by  Angela López Mendoza   ·   @angelahack1
 *   Developer · Architect · Creator of Tlamatini
 * ═══════════════════════════════════════════════════════════════════
 *   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
 *
 * model_capacity.js — the COMPACT MODE box, told to the user
 * (Angela, 2026-10-01; the switch 2026-10-02).
 *
 * The toolbar's "Compact mode" box (#compact-mode-enabled) is the switch in
 * agent/compact_mode.py.  Ticking it REALLY unticks every MCP, tool, agent
 * and skill row (Config ▸ Configure MCPs / Configure Agents / ACPX-Skills)
 * except System-Metrics, Files-Search and Current-Time; the user then ticks
 * back - one by one - only what she needs.  Unticking it ticks them ALL
 * again.  A model that cannot hold EVERYTHING activated locks the box ON
 * (strict): it cannot be unticked until a larger model is chosen.
 *
 * Two sources of truth, both from the server:
 *   - `compact-mode-state` frames (re-dispatched as tlm:compact-mode-state):
 *     the switch {active, strict, locked, model, window_tokens,
 *     everything_tokens, version};
 *   - `detail.capacity` on every context-gauge frame: what the last request
 *     really sent (mode, tools_kept, toggles_version, ...).
 * This module turns them into:
 *   1. the box itself - checked = ON; greyed + 🔒 = locked ON;
 *   2. a dialog that explains, in plain words, what the model can hold and
 *      how to add what she needs - opened once per model per browser session
 *      when a small model locks the box, and on a click of the locked box;
 *   3. a short notice when the switch changes and when Ollama cuts a request;
 *   4. a resync request when a gauge frame carries a newer rows version, so
 *      the Configure dialogs always show the REAL rows.
 *
 * Contracts: self-contained IIFE, NO cross-file globals (exports only
 * window.TlmModelCapacity); every step is fail-open — a broken notice must
 * never cost the user the chat; the dialog follows dialog_policy.js (✕,
 * Escape and the buttons close it, an outside click does not) and wears the
 * shared .tlmpop-* identity from dialog_theme.css.
 */
(function () {
    'use strict';

    const EVENT_NAME = 'tlm:context-gauge';
    const STATE_EVENT = 'tlm:compact-mode-state';
    const OVERLAY_ID = 'tlm-compact-overlay';
    const BOX_ID = 'compact-mode-enabled';
    const LABEL_ID = 'compact-mode-toggle';
    const TOAST_ID = 'tlm-capacity-toast';
    const SUPPRESS_PREFIX = 'tlm_compact_dialog_hidden:';
    const SEEN_PREFIX = 'tlm_compact_dialog_seen:';

    const state = {
        sw: null,            // the switch, from compact-mode-state frames
        capacity: null,      // what the last request really sent (gauge frames)
        shownFor: {},        // model -> true (dialog already shown this page)
        lastActive: null,
        knownVersion: 0,
        syncAt: 0,
        cutNoticeAt: 0,
        pending: false,      // a set-compact-mode request is on its way
        pendingTimer: null
    };

    function byId(id) {
        return document.getElementById(id);
    }

    function fmt(n) {
        const v = Number(n) || 0;
        try {
            return v.toLocaleString('es-MX');
        } catch (err) {
            return String(v);
        }
    }

    function el(tag, cls, text) {
        const node = document.createElement(tag);
        if (cls) { node.className = cls; }
        if (text !== undefined && text !== null) { node.textContent = String(text); }
        return node;
    }

    function storageGet(key) {
        try { return window.localStorage.getItem(key); } catch (err) { return null; }
    }

    function storageSet(key, value) {
        try {
            if (value === null) { window.localStorage.removeItem(key); }
            else { window.localStorage.setItem(key, value); }
        } catch (err) { /* private window / blocked storage: fine */ }
    }

    function sessionGet(key) {
        try { return window.sessionStorage.getItem(key); } catch (err) { return null; }
    }

    function sessionSet(key, value) {
        try { window.sessionStorage.setItem(key, value); } catch (err) { /* blocked storage: fine */ }
    }

    function send(payload) {
        try {
            if (typeof window.isChatSocketOpen === 'function' && !window.isChatSocketOpen()) { return false; }
            if (typeof window.sendChatSocketMessage !== 'function') { return false; }
            window.sendChatSocketMessage(payload);
            return true;
        } catch (err) {
            return false;
        }
    }

    function sw() {
        return state.sw || {};
    }

    function isLocked() {
        const s = sw();
        return !!(s.active && s.locked);
    }

    // ── The box ────────────────────────────────────────────────────────────
    function titleFor(s) {
        if (s.active && s.locked) {
            return 'Compact mode está ACTIVADO y bloqueado: ' + (s.model || 'este modelo') + ' sólo lee ' +
                fmt(s.window_tokens) + ' tokens, y todo lo activado necesita unos ' +
                fmt(s.everything_tokens) + '. Marca lo que necesites en Config ▸ Configurar MCPs / ' +
                'Configurar Agents; el medidor CONTEXT-WINDOW muestra cuánto cuesta. Haz clic para ver los detalles.';
        }
        if (s.active) {
            return 'Compact mode está ACTIVADO: sólo se envía lo que marcaste en Config ▸ Configurar MCPs / ' +
                'Configurar Agents. Desmarca esta casilla para volver a activar TODO.';
        }
        return 'Compact mode: desmarca todos los MCPs, tools, agents y skills excepto System-Metrics, ' +
            'Files-Search y Current-Time, para que le envíes al modelo sólo lo que elijas. Desmárcalo ' +
            'después para volver a activar todo.';
    }

    function paintBox() {
        const box = byId(BOX_ID);
        const label = byId(LABEL_ID);
        if (!box) { return; }
        const s = sw();
        const locked = isLocked();
        box.checked = !!s.active;
        box.disabled = locked || state.pending;
        if (label) {
            label.classList.toggle('compact-locked', locked);
            label.classList.toggle('compact-on', !!s.active);
            label.classList.toggle('toolbar-toggle-disabled', locked || state.pending);
            const text = label.querySelector('span');
            if (text) { text.textContent = locked ? 'Compact mode 🔒' : 'Compact mode'; }
            label.setAttribute('title', titleFor(s));
            label.setAttribute('aria-disabled', locked ? 'true' : 'false');
        }
    }

    function setPending(on) {
        state.pending = !!on;
        if (state.pendingTimer) {
            window.clearTimeout(state.pendingTimer);
            state.pendingTimer = null;
        }
        if (on) {
            // Never leave the box greyed out if the answer is lost.
            state.pendingTimer = window.setTimeout(function () { setPending(false); }, 8000);
        }
        paintBox();
    }

    function onBoxChange() {
        const box = byId(BOX_ID);
        if (!box) { return; }
        const want = !!box.checked;
        if (!want && isLocked()) {
            box.checked = true;
            openDialog(true);
            return;
        }
        const sent = send({ type: 'set-compact-mode', message: 'set-compact-mode', enabled: want });
        if (!sent) {
            box.checked = !want;
            toast('No se cambió Compact mode: la conexión no está abierta. Usa Reconectar y vuelve a intentarlo.', 'warn');
            return;
        }
        setPending(true);
    }

    function onLabelClick(event) {
        if (isLocked()) {
            // The box is greyed out: a click explains why instead of doing nothing.
            try { event.preventDefault(); } catch (err) { /* noop */ }
            openDialog(true);
        }
    }

    function wireBox() {
        const box = byId(BOX_ID);
        const label = byId(LABEL_ID);
        if (box && !box.dataset.tlmCompactWired) {
            box.dataset.tlmCompactWired = '1';
            box.addEventListener('change', onBoxChange);
        }
        if (label && !label.dataset.tlmCompactWired) {
            label.dataset.tlmCompactWired = '1';
            label.addEventListener('click', onLabelClick);
        }
        paintBox();
    }

    // ── Toast ──────────────────────────────────────────────────────────────
    function toast(text, tone) {
        try {
            const old = byId(TOAST_ID);
            if (old && old.parentNode) { old.parentNode.removeChild(old); }
            const t = el('div', 'tlm-capacity-toast' + (tone ? ' tlm-capacity-toast-' + tone : ''), text);
            t.id = TOAST_ID;
            t.setAttribute('role', 'status');
            document.body.appendChild(t);
            window.setTimeout(function () { t.classList.add('is-leaving'); }, 6500);
            window.setTimeout(function () { if (t.parentNode) { t.parentNode.removeChild(t); } }, 7200);
        } catch (err) { /* a notice must never break the page */ }
    }

    // ── Dialog ─────────────────────────────────────────────────────────────
    function closeDialog() {
        const overlay = byId(OVERLAY_ID);
        if (!overlay) { return; }
        const box = overlay.querySelector('.tlmcap-dontshow input');
        const model = sw().model || '';
        if (box && model) {
            storageSet(SUPPRESS_PREFIX + model, box.checked ? '1' : null);
        }
        if (overlay.parentNode) { overlay.parentNode.removeChild(overlay); }
        try {
            const input = byId('chat-message-input');
            if (input && !input.disabled) { input.focus(); }
        } catch (err) { /* noop */ }
    }

    function row(list, icon, name, detail, tone) {
        const li = el('li', 'tlmcap-row tlmcap-' + tone);
        li.appendChild(el('span', 'tlmcap-icon', icon));
        const copy = el('span', 'tlmcap-copy');
        copy.appendChild(el('strong', 'tlmcap-name', name));
        if (detail) { copy.appendChild(el('span', 'tlmcap-detail', detail)); }
        li.appendChild(copy);
        list.appendChild(li);
    }

    function openConfigure(fnName) {
        closeDialog();
        try {
            if (typeof window[fnName] === 'function') {
                // The menu handlers call e.preventDefault() first.
                window[fnName]({ preventDefault: function () {} });
            }
        } catch (err) { /* the dialog itself is optional */ }
    }

    function openDialog(fromUser) {
        if (byId(OVERLAY_ID)) { return; }
        const s = sw();
        const cap = state.capacity || {};
        const model = s.model || cap.model || 'Este modelo';
        const locked = isLocked();

        const overlay = el('div', 'tlmpop-overlay tlmcap-overlay');
        overlay.id = OVERLAY_ID;
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.setAttribute('aria-labelledby', 'tlmcap-title');

        const card = el('div', 'tlmpop-card tlmcap-card');
        const head = el('div', 'tlmpop-head');
        const title = el('span', 'tlmpop-title',
            locked ? 'Compact mode — ACTIVADO y bloqueado para este modelo' : (s.active ? 'Compact mode está ACTIVADO' : 'Compact mode'));
        title.id = 'tlmcap-title';
        const x = el('button', 'tlmpop-x', '×');
        x.type = 'button';
        x.setAttribute('aria-label', 'Cerrar');
        x.addEventListener('click', closeDialog);
        head.appendChild(title);
        head.appendChild(x);

        const body = el('div', 'tlmpop-body tlmcap-body');

        const win = Number(s.window_tokens || cap.window_tokens) || 0;
        const every = Number(s.everything_tokens || cap.everything_tokens) || 0;
        const meter = el('div', 'tlmcap-meter');
        const pct = every > 0 ? Math.max(4, Math.min(100, Math.round(win * 100 / every))) : 100;
        const bar = el('div', 'tlmcap-bar');
        const fill = el('div', 'tlmcap-bar-fill');
        fill.style.width = pct + '%';
        bar.appendChild(fill);
        meter.appendChild(bar);
        const legend = el('div', 'tlmcap-legend');
        legend.appendChild(el('span', 'tlmcap-legend-win', model + ' lee ' + fmt(win) + ' tokens'));
        legend.appendChild(el('span', 'tlmcap-legend-full', 'Todo lo activado ≈ ' + fmt(every)));
        meter.appendChild(legend);

        const lead = el('p', 'tlmpop-msg tlmcap-lead');
        if (locked) {
            lead.textContent = model + ' puede leer unos ' + fmt(win) + ' tokens a la vez, y ' +
                'Tlamatini con todo activado necesita unos ' + fmt(every) + '. Si se lo enviara todo, ' +
                'Ollama descartaría en silencio la mayor parte, así que Compact mode está ACTIVADO y bloqueado: ' +
                'se desmarcaron todos los MCPs, tools, agents y skills excepto System-Metrics, Files-Search ' +
                'y Current-Time, y tú vuelves a agregar sólo lo que necesitas.';
        } else {
            lead.textContent = 'Compact mode está ACTIVADO: Tlamatini le envía a ' + model + ' sólo lo que ' +
                'marcaste. Desmarca la casilla Compact mode para activar todos los MCPs, tools, agents y skills ' +
                'de nuevo.';
        }

        const grid = el('div', 'tlmcap-grid');
        const keep = el('div', 'tlmcap-col');
        keep.appendChild(el('div', 'tlmcap-col-title tlmcap-on', 'Se envía con tu siguiente mensaje'));
        const keepList = el('ul', 'tlmcap-list');
        const kept = (cap.tools_kept || []).filter(function (n) { return !!n; });
        row(keepList, '✓', 'System-Metrics · Files-Search', 'según lo marcado en Config ▸ Configurar MCPs', 'on');
        if (kept.length) {
            row(keepList, '✓', kept.length + ' tool(s) que marcaste', kept.slice(0, 8).join(', ') +
                (kept.length > 8 ? ', …' : ''), 'on');
        } else {
            row(keepList, '–', 'Ningún tool', 'marca Current-Time o un agent para agregar uno', 'off');
        }
        row(keepList, '✓', 'Tu contexto cargado y el chat reciente',
            'ajustados a la ventana (' + fmt(cap.history_kept) + ' de ' + fmt(cap.history_total) + ' mensajes recientes)', 'on');
        keep.appendChild(keepList);

        const how = el('div', 'tlmcap-col');
        how.appendChild(el('div', 'tlmcap-col-title tlmcap-off', 'Agrega lo que necesites'));
        const howList = el('ul', 'tlmcap-list');
        row(howList, '1', 'Config ▸ Configurar Agents', 'marca un agent (por ejemplo PDFer o ESPHomer) y su tool se marca con él', 'off');
        row(howList, '2', 'Config ▸ Configurar MCPs', 'marca o desmarca tools, System-Metrics y Files-Search', 'off');
        row(howList, '3', 'Observa el medidor CONTEXT-WINDOW', 'verde: cabe; rojo o más de 100%: no todo va a funcionar', 'off');
        const ext = cap.external_mcps_paused || [];
        row(howList, '⏸', 'External MCPs (' + ext.length + ' en pausa)',
            ext.length ? ext.join(', ') + ' - se restauran cuando se desactiva Compact mode' : 'no había ninguno activo', 'off');
        how.appendChild(howList);
        grid.appendChild(keep);
        grid.appendChild(how);

        const back = el('p', 'tlmpop-sub tlmcap-back');
        back.textContent = locked
            ? 'El bloqueo se quita solo cuando eliges en Config ▸ Modelos un modelo que pueda con todo (por ejemplo, un modelo :cloud).'
            : 'Tus elecciones se conservan tal como las dejes hasta que desmarques Compact mode.';

        const src = el('p', 'tlmcap-source');
        src.textContent = 'Origen de la ventana: ' + (cap.window_source || 'measured') +
            '. Reservado para la respuesta: ' + fmt(cap.reserve_tokens) + ' tokens.';

        const dont = el('label', 'tlmcap-dontshow');
        const dontBox = document.createElement('input');
        dontBox.type = 'checkbox';
        dontBox.checked = storageGet(SUPPRESS_PREFIX + (s.model || '')) === '1';
        dont.appendChild(dontBox);
        dont.appendChild(el('span', null, ' No volver a abrir esto automáticamente para ' + model));

        body.appendChild(meter);
        body.appendChild(lead);
        body.appendChild(grid);
        body.appendChild(back);
        body.appendChild(src);
        body.appendChild(dont);

        const foot = el('div', 'tlmpop-foot');
        const agents = el('button', 'tlmpop-btn tlmcap-agents', 'Abrir Configurar Agents');
        agents.type = 'button';
        agents.addEventListener('click', function () { openConfigure('OpenAgentsDialog'); });
        const models = el('button', 'tlmpop-btn tlmcap-models', 'Abrir Config ▸ Modelos');
        models.type = 'button';
        models.addEventListener('click', function () { openConfigure('OpenConfigModelsDialog'); });
        const ok = el('button', 'tlmpop-btn tlmpop-btn-primary tlmcap-ok', 'Aceptar');
        ok.type = 'button';
        ok.addEventListener('click', closeDialog);
        foot.appendChild(agents);
        foot.appendChild(models);
        foot.appendChild(ok);

        card.appendChild(head);
        card.appendChild(body);
        card.appendChild(foot);
        overlay.appendChild(card);
        // dialog_policy.js: Escape invokes the dialog's own dismiss path.
        overlay.tlmDismiss = closeDialog;
        document.body.appendChild(overlay);
        try { ok.focus(); } catch (err) { /* noop */ }
        if (!fromUser) {
            try { window.console.info('[compact-mode] dialog shown for', model); } catch (err) { /* noop */ }
        }
    }

    function maybeOpenForModel(s) {
        if (!(s.active && s.locked)) { return; }
        const model = s.model || '';
        if (!model || state.shownFor[model]) { return; }
        state.shownFor[model] = true;
        if (storageGet(SUPPRESS_PREFIX + model) === '1' || sessionGet(SEEN_PREFIX + model) === '1') {
            return;
        }
        sessionSet(SEEN_PREFIX + model, '1');
        openDialog(false);
    }

    // ── The switch ─────────────────────────────────────────────────────────
    function applySwitch(s, kind) {
        if (!s || typeof s !== 'object') { return; }
        const prevActive = state.lastActive;
        state.sw = s;
        state.lastActive = !!s.active;
        if (Number(s.version) > state.knownVersion) { state.knownVersion = Number(s.version); }
        setPending(false);
        document.documentElement.setAttribute('data-tlm-compact',
            s.active ? (s.locked ? 'locked' : 'on') : 'off');
        if (prevActive !== null && prevActive !== !!s.active) {
            if (s.active) {
                toast('Compact mode está ACTIVADO: sólo se envía lo que marques en Config ▸ Configurar MCPs / ' +
                      'Configurar Agents.', 'warn');
            } else {
                toast('Compact mode está DESACTIVADO: volvieron todos los MCPs, tools, agents y skills.', 'ok');
            }
        }
        if (kind === 'refused' && s.locked) {
            toast('Compact mode sigue ACTIVADO: ' + (s.model || 'este modelo') + ' no puede con todo lo activado.', 'warn');
        }
        maybeOpenForModel(s);
    }

    function onState(event) {
        try {
            const data = event && event.detail ? event.detail : null;
            if (data && data.state) { applySwitch(data.state, data.kind || 'state'); }
        } catch (err) {
            try { window.console.warn('[compact-mode] state skipped:', err); } catch (e) { /* noop */ }
        }
    }

    // ── The verdict on every gauge frame ───────────────────────────────────
    function applyCapacity(cap, frame) {
        if (!cap || typeof cap !== 'object') { return; }
        state.capacity = cap;
        document.documentElement.setAttribute('data-tlm-capacity', cap.mode || 'full');
        // A frame can be newer than the switch this tab knows (another tab, or
        // the automatic switch): ask for the switch and the REAL rows.
        const version = Number(cap.toggles_version) || 0;
        const s = sw();
        const stale = version > state.knownVersion ||
            (typeof cap.compact_active === 'boolean' && state.sw && cap.compact_active !== !!s.active) ||
            (typeof cap.strict === 'boolean' && state.sw && cap.strict !== !!s.strict);
        if (stale && Date.now() - state.syncAt > 1500) {
            state.syncAt = Date.now();
            if (version > state.knownVersion) { state.knownVersion = version; }
            send({ type: 'compact-mode-sync', message: 'compact-mode-sync' });
        }
        if (frame && frame.truncated && Date.now() - state.cutNoticeAt > 20000) {
            state.cutNoticeAt = Date.now();
            toast('Se excedió CONTEXT-WINDOW: ' + (cap.model || 'el modelo') + ' sólo leyó ' +
                  fmt(frame.window_real || frame.tokens_real) + ' de unos ' +
                  fmt(frame.tokens_sent_estimate || frame.tokens_estimated) +
                  ' tokens enviados. Desmarca agents o tools para que la solicitud quepa.', 'warn');
        }
    }

    function onFrame(event) {
        try {
            const frame = event && event.detail ? event.detail : null;
            if (frame && frame.capacity) { applyCapacity(frame.capacity, frame); }
        } catch (err) {
            try { window.console.warn('[compact-mode] frame skipped:', err); } catch (e) { /* noop */ }
        }
    }

    document.addEventListener(EVENT_NAME, onFrame);
    document.addEventListener(STATE_EVENT, onState);
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', wireBox);
    } else {
        wireBox();
    }

    window.TlmModelCapacity = {
        isCompact: function () { return !!sw().active; },
        isLocked: function () { return isLocked(); },
        capacity: function () { return state.capacity ? JSON.parse(JSON.stringify(state.capacity)) : null; },
        state: function () { return state.sw ? JSON.parse(JSON.stringify(state.sw)) : null; },
        open: function () { openDialog(true); }
    };
}());
