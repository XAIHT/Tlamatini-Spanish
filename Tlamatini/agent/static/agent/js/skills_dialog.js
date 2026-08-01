/*
 * ═══════════════════════════════════════════════════════════════════
 *   ✦  T L A M A T I N I  ✦   —   "one who knows"
 *
 *   Created by  Angela López Mendoza   ·   @angelahack1
 *   Developer · Architect · Creator of Tlamatini
 *
 *   Every line of this file was written by Angela López Mendoza.
 * ═══════════════════════════════════════════════════════════════════
 *   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
 */

// ============================================================
// skills_dialog.js — jQuery-UI dialogs for the ACPX-Skills menu
// ============================================================
//
// Four entry points (exposed for agent_page_init.js to call):
//
//   preRenderSkillsConfigureDialog(title, body, contCb, cancCb)
//   renderSkillsConfigureDialog()
//     -- Checkbox-grid toggle of skills[]. Continue sends set-skills via
//        the chat WebSocket. Mirrors the Mcps/Agents/Tools dialog pattern.
//
//   openSkillsBrowseDialog()
//     -- Read-only list+detail pane fetched from GET /agent/skills/.
//        Clicking a row hits GET /agent/skills/<name>/ for the full body.
//
//   openSkillsDiagnosticsDialog()
//     -- Cross-check report from GET /agent/skills/_/diagnostics/.
//        Flags missing tools/mcps/acpx-agent dependencies + orphan rows.
//
//   reloadSkillRegistry()
//     -- POST /agent/skills/_/reload/. Re-runs boot_skills() so freshly
//        edited SKILL.md files appear without a server restart. Shows a
//        toast-style message in the chat stream.

// ----------------------------------------------------------------
// Configure dialog (checkbox grid)
// ----------------------------------------------------------------

function preRenderSkillsConfigureDialog(title, body, callbackOnContinue, callbackOnCancel) { // eslint-disable-line no-unused-vars
    const dlg = document.getElementById('skills-configure-dialog-message');
    const titleEl = document.getElementById('skills-configure-primary-dialog-legend');
    const bodyEl = document.getElementById('skills-configure-secondary-dialog-legend');
    const listEl = document.getElementById('skills-configure-list');
    if (!dlg || !titleEl || !bodyEl || !listEl) {
        console.error('skills-configure-dialog: required DOM nodes missing');
        return;
    }
    dlg.title = title || 'Configurar Skills';
    titleEl.innerText = title || 'Configurar Skills';
    bodyEl.innerText = body || 'Prende o apaga los paquetes SKILL.md.';

    // Build checkboxes from the in-memory skills[] cache populated by the
    // 'type: skill' WebSocket establishment messages.
    listEl.innerHTML = '';
    const sorted = (Array.isArray(skills) ? skills : [])
        .slice()
        .sort((a, b) => (a.name || '').localeCompare(b.name || ''));
    for (const skill of sorted) {
        if (!skill || !skill.name) continue;
        const li = document.createElement('li');
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.id = 'skill-checkbox-' + skill.name;
        cb.checked = (skill.content === 'true');
        const label = document.createElement('label');
        label.setAttribute('for', cb.id);
        label.className = 'skill-config-label';
        const nameSpan = document.createElement('span');
        nameSpan.className = 'skill-config-name';
        nameSpan.textContent = skill.name;
        const descSpan = document.createElement('span');
        descSpan.className = 'skill-config-desc';
        descSpan.textContent = skill.description ? ' — ' + skill.description : '';
        label.appendChild(nameSpan);
        label.appendChild(descSpan);
        li.appendChild(cb);
        li.appendChild(label);
        listEl.appendChild(li);
    }

    $('#skills-configure-dialog-message').dialog({
        autoOpen: false,
        modal: true,
        width: 600,
        resizable: false,
        draggable: true,
        closeText: '',
        open: function () {
            document.body.style.overflow = 'hidden';
            const { cols, width: dialogWidth } = computeCheckboxGridLayout(sorted.length, {
                minDialogWidth: 520,
                minColWidth: 240,
            });
            $(this).dialog('option', 'width', dialogWidth);
            $(this).dialog('option', 'maxWidth', Math.floor(window.innerWidth * 0.9));
            $(this).dialog('option', 'maxHeight', Math.floor(window.innerHeight * 0.9));
            listEl.style.display = 'grid';
            listEl.style.gridTemplateColumns = `repeat(${cols}, minmax(0, 1fr))`;
            listEl.style.gap = '8px 18px';
            listEl.style.listStyleType = 'none';
            listEl.style.padding = '0';
            listEl.style.margin = '15px 0';
            listEl.style.maxHeight = '60vh';
            listEl.style.overflowY = 'auto';
            listEl.style.overflowX = 'hidden';
        },
        close: function () { document.body.style.overflow = ''; },
        create: function () {
            // Mirror the agent_page_dialogs.js pattern — apply the
            // standardized teal-button CSS to Continue / Cancel at create
            // time so the buttons match every other dialog in the app
            // (Mcps, Tools, Agents, Backup-DB, Set-DB, Config-Models, ...).
            $(this).parent().find('.ui-dialog-buttonpane button:contains("Continuar")').css(DIALOG_BUTTON_CSS);
            $(this).parent().find('.ui-dialog-buttonpane button:contains("Cancelar")').css(DIALOG_BUTTON_CSS);
        },
        buttons: makeDialogButtons(callbackOnContinue, callbackOnCancel)
    });
}

function renderSkillsConfigureDialog() { // eslint-disable-line no-unused-vars
    confirmationByUser = false;
    styleDialogButtons();
    $('#skills-configure-dialog-message').dialog('open');
    $('#skills-configure-dialog-message').dialog('option', 'position',
        { my: 'center', at: 'center', of: window });
}

/**
 * Build a single Close button shaped like the standard Continue button.
 * Used by the read-only Browse / Diagnostics dialogs where Continue/Cancel
 * wouldn't make semantic sense, but the visual identity still needs to
 * match the rest of the dialog family.
 */
function _makeCloseOnlyButton() {
    return [{
        text: 'Cerrar',
        click: function () { $(this).dialog('close'); }
    }];
}

/** Apply DIALOG_BUTTON_CSS to the single Close button of the active dialog. */
function _styleCloseOnlyButton($dialog) {
    $dialog.parent().find('.ui-dialog-buttonpane button:contains("Cerrar")').css(DIALOG_BUTTON_CSS);
}

// ----------------------------------------------------------------
// Browse dialog (list + detail pane, HTTP-backed)
// ----------------------------------------------------------------

function _csrfTokenForSkills() {
    const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
}

function openSkillsBrowseDialog() { // eslint-disable-line no-unused-vars
    const dlg = document.getElementById('skills-browse-dialog-message');
    if (!dlg) {
        console.error('skills-browse-dialog: container missing');
        return;
    }
    dlg.title = 'Ver ACPX-Skills';

    const listEl = document.getElementById('skills-browse-list');
    const countEl = document.getElementById('skills-browse-count');
    const searchEl = document.getElementById('skills-browse-search');
    const detailEmpty = document.getElementById('skills-browse-detail-empty');
    const detailContent = document.getElementById('skills-browse-detail-content');
    if (!listEl || !countEl || !searchEl || !detailEmpty || !detailContent) return;

    listEl.innerHTML = '<li class="skill-browse-loading">Cargando…</li>';
    countEl.textContent = '';
    detailEmpty.style.display = '';
    detailContent.style.display = 'none';
    detailContent.innerHTML = '';

    let allSkills = [];

    function applyFilter() {
        const q = (searchEl.value || '').trim().toLowerCase();
        listEl.innerHTML = '';
        let shown = 0;
        for (const s of allSkills) {
            if (q && !(s.name + ' ' + (s.description || '')).toLowerCase().includes(q)) continue;
            const li = document.createElement('li');
            li.className = 'skill-browse-row' + (s.enabled ? '' : ' disabled');
            li.dataset.skillName = s.name;
            const dot = document.createElement('span');
            dot.className = 'skill-browse-dot skill-browse-dot-' + (s.enabled ? 'on' : 'off');
            const name = document.createElement('span');
            name.className = 'skill-browse-name';
            name.textContent = s.name;
            const runtime = document.createElement('span');
            runtime.className = 'skill-browse-runtime';
            runtime.textContent = s.runtime;
            li.appendChild(dot);
            li.appendChild(name);
            li.appendChild(runtime);
            li.addEventListener('click', () => loadSkillDetail(s.name));
            listEl.appendChild(li);
            shown += 1;
        }
        countEl.textContent = shown + ' / ' + allSkills.length;
    }

    function loadSkillDetail(name) {
        detailEmpty.style.display = 'none';
        detailContent.style.display = '';
        detailContent.innerHTML = '<div class="skill-detail-loading">Cargando…</div>';
        fetch('/agent/skills/' + encodeURIComponent(name) + '/', {
            credentials: 'same-origin'
        }).then(r => r.json()).then(s => {
            if (s.error) {
                detailContent.innerHTML = '<div class="skill-detail-error">' + s.error + '</div>';
                return;
            }
            const enabledBadge = s.enabled
                ? '<span class="skill-detail-badge on">prendido</span>'
                : '<span class="skill-detail-badge off">apagado</span>';
            const triggers = (s.triggers_keywords || []).map(t => '<code>' + t + '</code>').join(' ');
            const reqTools = (s.requires_tools || []).map(t => '<code>' + t + '</code>').join(' ') || '<em>ninguno</em>';
            const reqMcps = (s.requires_mcps || []).map(t => '<code>' + t + '</code>').join(' ') || '<em>ninguno</em>';
            const inputs = (s.inputs || []).map(i => {
                const req = i.required ? ' <span class="skill-detail-req">obligatorio</span>' : '';
                return '<li><code>' + (i.name || '') + '</code> <small>(' + (i.type || 'string') + ')</small>' + req + '</li>';
            }).join('') || '<li><em>(ninguno)</em></li>';
            const outputs = (s.outputs || []).map(o => {
                return '<li><code>' + (o.name || '') + '</code> <small>(' + (o.type || 'string') + ')</small></li>';
            }).join('') || '<li><em>(ninguno)</em></li>';
            const safeBody = (s.body || '').replace(/[<>&]/g, ch => ({
                '<': '&lt;', '>': '&gt;', '&': '&amp;'
            })[ch]);
            detailContent.innerHTML =
                '<h4 class="skill-detail-title">' + s.name + ' ' + enabledBadge + '</h4>' +
                '<p class="skill-detail-desc">' + (s.description || '') + '</p>' +
                '<dl class="skill-detail-meta">' +
                '<dt>Runtime</dt><dd>' + s.runtime + (s.acpx_agent ? ' (' + s.acpx_agent + ')' : '') + '</dd>' +
                '<dt>Budget</dt><dd>' + s.max_iterations + ' iter · ' + s.max_seconds + ' s · ' + s.max_tokens + ' tokens</dd>' +
                '<dt>Triggers</dt><dd>' + (triggers || '<em>ninguno</em>') + '</dd>' +
                '<dt>Requiere tools</dt><dd>' + reqTools + '</dd>' +
                '<dt>Requiere MCPs</dt><dd>' + reqMcps + '</dd>' +
                '<dt>Path</dt><dd><code class="skill-detail-path">' + (s.skill_md_path || '') + '</code></dd>' +
                '<dt>SHA-256</dt><dd><code>' + (s.body_sha256 || '').slice(0, 16) + '…</code></dd>' +
                '</dl>' +
                '<h5>Inputs</h5><ul class="skill-detail-io">' + inputs + '</ul>' +
                '<h5>Outputs</h5><ul class="skill-detail-io">' + outputs + '</ul>' +
                '<h5>Body</h5><pre class="skill-detail-body">' + safeBody + '</pre>';
        }).catch(err => {
            detailContent.innerHTML = '<div class="skill-detail-error">' + err + '</div>';
        });
    }

    fetch('/agent/skills/', { credentials: 'same-origin' })
        .then(r => r.json())
        .then(payload => {
            allSkills = payload.skills || [];
            applyFilter();
            if (payload.orphan_db_rows && payload.orphan_db_rows.length) {
                countEl.textContent += '  ·  ' + payload.orphan_db_rows.length + ' rows huérfanos en la DB';
            }
        }).catch(err => {
            listEl.innerHTML = '<li class="skill-browse-error">No pude cargar: ' + err + '</li>';
        });

    searchEl.value = '';
    searchEl.oninput = applyFilter;

    $('#skills-browse-dialog-message').dialog({
        autoOpen: false,
        modal: true,
        width: Math.min(Math.floor(window.innerWidth * 0.85), 1100),
        height: Math.floor(window.innerHeight * 0.8),
        resizable: false,
        draggable: true,
        closeText: '',
        open: function () { document.body.style.overflow = 'hidden'; },
        close: function () { document.body.style.overflow = ''; },
        create: function () { _styleCloseOnlyButton($(this)); },
        buttons: _makeCloseOnlyButton()
    });
    _styleCloseOnlyButton($('#skills-browse-dialog-message'));
    $('#skills-browse-dialog-message').dialog('open');
    $('#skills-browse-dialog-message').dialog('option', 'position',
        { my: 'center', at: 'center', of: window });
}

// ----------------------------------------------------------------
// Diagnostics dialog
// ----------------------------------------------------------------

function openSkillsDiagnosticsDialog() { // eslint-disable-line no-unused-vars
    const dlg = document.getElementById('skills-diagnostics-dialog-message');
    if (!dlg) return;
    dlg.title = 'Diagnóstico de ACPX-Skills';

    const summary = document.getElementById('skills-diagnostics-summary');
    const sections = document.getElementById('skills-diagnostics-sections');
    summary.innerHTML = '<em>Cargando el diagnóstico…</em>';
    sections.innerHTML = '';

    fetch('/agent/skills/_/diagnostics/', { credentials: 'same-origin' })
        .then(r => r.json())
        .then(d => {
            if (d.error) {
                summary.innerHTML = '<div class="skill-diag-error">' + d.error + '</div>';
                return;
            }
            summary.innerHTML =
                '<div class="skill-diag-summary-row">' +
                '<strong>' + d.skill_count + '</strong> skills en disco &nbsp;·&nbsp; ' +
                '<strong>' + d.db_row_count + '</strong> rows en la DB &nbsp;·&nbsp; ' +
                '<strong>' + d.tools_known + '</strong> tools registrados &nbsp;·&nbsp; ' +
                '<strong>' + d.mcps_known + '</strong> MCPs registrados &nbsp;·&nbsp; ' +
                '<strong>' + d.acpx_agents_known + '</strong> ACPX agents registrados' +
                '</div>';
            const render = (title, rows, fn, emptyOk) => {
                const ok = !rows || rows.length === 0;
                if (ok && !emptyOk) return '';
                const items = ok ? '<li><em>ninguno — todo bien</em></li>'
                    : rows.map(fn).join('');
                return '<section class="skill-diag-section ' +
                    (ok ? 'ok' : 'warn') + '"><h5>' + title +
                    (ok ? ' ✓' : ' ⚠ ' + rows.length) + '</h5><ul>' +
                    items + '</ul></section>';
            };
            sections.innerHTML =
                render('Faltan dependencias de tools', d.missing_tools, r =>
                    '<li><strong>' + r.skill + '</strong> — tools apagados: ' +
                    r.disabled_tools.map(t => '<code>' + t + '</code>').join(' ') + '</li>'
                , true) +
                render('Faltan dependencias de MCP', d.missing_mcps, r =>
                    '<li><strong>' + r.skill + '</strong> — MCPs apagados: ' +
                    r.disabled_mcps.map(t => '<code>' + t + '</code>').join(' ') + '</li>'
                , true) +
                render('ACPX agents desconocidos', d.unknown_acpx_agents, r =>
                    '<li><strong>' + r.skill + '</strong> requiere <code>' +
                    r.acpx_agent + '</code></li>'
                , true) +
                render('Rows huérfanos en la DB (sin SKILL.md en disco)', d.orphan_db_rows, n =>
                    '<li><code>' + n + '</code></li>'
                , true);
        }).catch(err => {
            summary.innerHTML = '<div class="skill-diag-error">No pude cargar: ' + err + '</div>';
        });

    $('#skills-diagnostics-dialog-message').dialog({
        autoOpen: false,
        modal: true,
        width: Math.min(Math.floor(window.innerWidth * 0.7), 820),
        resizable: false,
        draggable: true,
        closeText: '',
        open: function () { document.body.style.overflow = 'hidden'; },
        close: function () { document.body.style.overflow = ''; },
        create: function () { _styleCloseOnlyButton($(this)); },
        buttons: _makeCloseOnlyButton()
    });
    _styleCloseOnlyButton($('#skills-diagnostics-dialog-message'));
    $('#skills-diagnostics-dialog-message').dialog('open');
    $('#skills-diagnostics-dialog-message').dialog('option', 'position',
        { my: 'center', at: 'center', of: window });
}

// ----------------------------------------------------------------
// Reload registry
// ----------------------------------------------------------------

function reloadSkillRegistry() { // eslint-disable-line no-unused-vars
    fetch('/agent/skills/_/reload/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': _csrfTokenForSkills(),
            'Content-Type': 'application/json'
        }
    }).then(r => r.json()).then(d => {
        if (d.ok) {
            // Primera persona y gramática española: el compuesto a la inglesa
            // ("Skill registry recargado") y el "(s)" no son registro mexicano.
            const _pl = (n, uno, varios) => n + ' ' + (n === 1 ? uno : varios);
            const msg = 'Ya recargué el registry de skills — ' +
                _pl(d.skills_loaded, 'skill', 'skills') + ' en disco · ' +
                _pl(d.db_rows_after, 'row', 'rows') + ' en la DB.';
            console.log('--- ' + msg);
            // Inject a system message into the chat stream so the user
            // sees confirmation without opening another dialog.
            try {
                window.postMessage({ tlamatiniLocalNotice: msg }, '*');
            } catch (e) { /* best-effort */ }
            alert(msg);
        } else {
            alert('Falló la recarga: ' + (d.error || 'error desconocido'));
        }
    }).catch(err => alert('Falló la recarga: ' + err));
}
