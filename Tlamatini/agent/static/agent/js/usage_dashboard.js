/* Tlamatini Author Banner — Angela López Mendoza */
(function () {
    'use strict';
    const overlay = document.getElementById('usage-overlay');
    const opener = document.getElementById('usage-button');
    if (!overlay || !opener) return;
    const dialog = document.getElementById('usage-dialog');
    const $ = id => document.getElementById('usage-' + id);
    const palette = ['#70c5ed', '#c0a0f3', '#75d8ba', '#f3b96e', '#ea9bbc', '#90aafa'];
    const integer = new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 });
    const compact = new Intl.NumberFormat(undefined, { notation: 'compact', maximumFractionDigits: 1 });
    const n = value => typeof value === 'number' && Number.isFinite(value);
    const count = value => n(value) ? integer.format(value) : '—';
    const money = value => n(value) ? '$' + value.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '—';
    const date = value => value ? String(value).slice(0, 10) : '—';
    const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
    let range = '7d', data = null, controller = null, scheduled = null, retry = null;
    let again = false, forceAgain = false, generation = 0, lastFocus = null, oldOverflow = '', inertSiblings = [];
    let sessionInvalid = false;
    let ready = false, lastCheck = 0;

    function menuState(available, message) {
        ready = available;
        opener.disabled = !available;
        opener.setAttribute('aria-disabled', String(!available));
        opener.title = message;
        const hint = $('menu-status');
        hint.textContent = message;
        hint.hidden = available;
    }
    function queueCheck(seconds) {
        clearTimeout(retry);
        retry = setTimeout(() => refresh(), Math.max(1, Math.min(seconds, 60)) * 1000 + 100);
    }

    function html(id, content) {
        const element = $(id);
        if (element.innerHTML === content) return;
        const focusedIndex = element.contains(document.activeElement) ? [...element.querySelectorAll('[data-tip]')].indexOf(document.activeElement) : -1;
        element.innerHTML = content;
        if (focusedIndex >= 0) element.querySelectorAll('[data-tip]')[focusedIndex]?.focus({ preventScroll: true });
    }
    function metrics(id, rows) {
        html(id, rows.map(([label, value, note]) => `<div class="usage-metric"><span class="usage-metric-label">${esc(label)}</span><strong>${esc(value)}</strong><small>${esc(note)}</small></div>`).join(''));
    }
    function table(id, headings, rows) {
        html(id, rows.length ? `<table><thead><tr>${headings.map(h => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table>` : '<p class="usage-empty">No hay datos disponibles para este periodo.</p>');
    }
    function chart(id, rows, keys, currency = false) {
        if (!rows.length || !rows.some(r => keys.some(k => n(r[k])))) {
            html(id, '<p class="usage-empty">No hay datos de uso disponibles para este periodo.</p>'); return;
        }
        const width = 600, height = 166, left = 48, top = 12, bottom = 144;
        const maximum = Math.max(0, ...rows.map(r => keys.reduce((sum, k) => sum + (r[k] || 0), 0)));
        const scale = maximum || 1, slot = (width - left - 8) / rows.length;
        let svg = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(currency ? 'Uso diario de créditos en USD' : 'Tokens diarios de input y output')}. Los valores exactos están en la tabla de abajo.">`;
        for (let i = 0; i <= 3; i++) {
            const y = bottom - (bottom - top) * i / 3, value = maximum * i / 3;
            svg += `<line class="usage-gridline" x1="${left}" x2="592" y1="${y}" y2="${y}"/><text x="40" y="${y + 3}" text-anchor="end">${esc(currency ? '$' + compact.format(value) : compact.format(value))}</text>`;
        }
        rows.forEach((row, index) => {
            let y = bottom;
            const detail = `${row.date}${row.partial ? ' · día parcial' : ''}\n` + keys.map(k => `${k.replaceAll('_', ' ')}: ${currency ? money(row[k]) : count(row[k])}`).join('\n');
            svg += `<g tabindex="0" data-tip="${esc(detail)}" aria-label="${esc(detail)}"><title>${esc(detail)}</title>`;
            keys.forEach((key, i) => {
                const h = (row[key] || 0) / scale * (bottom - top); y -= h;
                const color = row.partial && currency ? '#f3b96e' : currency ? palette[index % palette.length] : palette[i];
                svg += `<rect x="${left + index * slot + slot * .16}" y="${y}" width="${slot * .68}" height="${h}" rx="2" fill="${color}"/>`;
            });
            // A transparent full-height hit target keeps zero days inspectable without inventing a bar.
            svg += `<rect x="${left + index * slot}" y="${top}" width="${slot}" height="${bottom - top}" fill="transparent"/></g>`;
            if (index === 0 || index === rows.length - 1 || index % Math.ceil(rows.length / 7) === 0) svg += `<text x="${left + (index + .5) * slot}" y="162" text-anchor="middle">${esc(row.date.slice(5))}</text>`;
        });
        html(id, svg + '</svg>');
    }
    function peak(rows, key, formatter) {
        const valid = rows.filter(r => n(r[key]));
        const best = valid.reduce((a, b) => !a || b[key] > a[key] ? b : a, null);
        return best && best[key] > 0 ? `Pico: ${date(best.date)} · ${formatter(best[key])}${best.partial ? ' (día parcial)' : ''}` : 'No hay uso medido en este periodo.';
    }
    function modelBars(id, rows, calls) {
        const value = r => calls ? r.calls : r.input_tokens + r.output_tokens;
        const ordered = [...rows].sort((a, b) => value(b) - value(a));
        const maximum = Math.max(1, ...ordered.map(value));
        html(id, ordered.length ? ordered.map((row, i) => `<div class="usage-model-row" tabindex="0" data-tip="${esc(row.model + '\n' + count(row.calls) + ' llamadas · ' + count(row.input_tokens) + ' input · ' + count(row.output_tokens) + ' output')}"><div><span>${esc(row.model)}</span><strong>${count(value(row))}</strong></div><div class="usage-stack">${calls ? `<span style="width:${100 * row.calls / maximum}%;background:${palette[i % palette.length]}"></span>` : `<span style="width:${100 * row.input_tokens / maximum}%;background:${palette[0]}"></span><span style="width:${100 * row.output_tokens / maximum}%;background:${palette[1]}"></span>`}</div></div>`).join('') : '<p class="usage-empty">Las estadísticas de modelos aparecen después de tu primera llamada medida del chat.</p>');
    }
    function refillCaption(end, now = Date.now()) {
        const remaining = Date.parse(end) - now;
        if (!Number.isFinite(remaining)) return '';
        if (remaining <= 0) return 'Los créditos mensuales ya deberían recargarse; al actualizar la cuenta se confirmará el periodo nuevo.';
        const days = Math.max(1, Math.ceil(remaining / 86400000));
        const weeks = Math.floor(days / 7);
        return 'Los créditos mensuales se recargan en ' + (weeks ? weeks + (weeks === 1 ? ' semana' : ' semanas') : days + (days === 1 ? ' día' : ' días')) + '.';
    }
    function creditCards(balance, pending) {
        const cards = [];
        const card = (label, value, lines, color = palette[0], percent = null) => {
            cards.push(`<article class="usage-panel usage-credit-card" style="--usage-card-color:${color}"><span class="usage-credit-label">${esc(label)}</span><strong class="usage-credit-value">${esc(value)}</strong>${lines.filter(Boolean).map(line => `<p>${esc(line)}</p>`).join('')}${n(percent) ? `<div class="usage-credit-progress"><span style="width:${Math.min(100, Math.max(0, percent))}%"></span></div>` : ''}</article>`);
        };
        if (balance?.kind === 'credits') {
            if (n(balance.remaining)) card('Créditos de uso · disponibles', money(balance.remaining), ['Créditos mensuales restantes: ' + money(balance.monthly_remaining), 'Créditos agregados: ' + money(balance.purchased)], palette[2]);
            else card('Créditos mensuales · disponibles', money(balance.monthly_remaining), ['Ollama no devolvió el saldo de créditos agregados.'], palette[2]);
            card('Créditos mensuales usados', money(balance.used), [n(balance.percent) ? balance.percent.toFixed(2) + '% de la asignación mensual' : 'Sin asignación mensual de créditos'], palette[1], balance.percent);
            card('Asignación mensual', money(balance.allowance), [refillCaption(balance.end), balance.end ? 'Se recarga el ' + date(balance.end) + ' (UTC)' : 'Ollama no devolvió la fecha de recarga.'], palette[3]);
            $('plan-note').textContent = 'Primero se usan los créditos incluidos y luego los agregados. Los créditos mensuales que no uses no se acumulan.';
        } else if (balance?.kind === 'legacy') {
            balance.limits.forEach(limit => card(limit.name === 'session' ? 'Asignación restante de la sesión' : 'Asignación semanal restante', limit.remaining_percent.toFixed(2) + '%', [limit.resets_at ? 'Se restablece el ' + new Date(limit.resets_at).toLocaleString() : 'Ollama no devolvió la fecha de restablecimiento.'], palette[cards.length], limit.remaining_percent));
            if (n(balance.purchased)) card('Créditos agregados', money(balance.purchased), ['Créditos comprados vigentes'], palette[3]);
            $('plan-note').textContent = 'Esta cuenta usa los límites antiguos por sesión y por semana. Ollama da el número de solicitudes; los costos en dólares y los totales de tokens pueden faltar en las solicitudes antiguas.';
        } else if (balance?.kind === 'purchased') {
            card('Créditos agregados', money(balance.purchased), ['Créditos comprados vigentes'], palette[2]);
            $('plan-note').textContent = 'Ollama devolvió créditos comprados sin asignación mensual ni calendario de restablecimiento.';
        } else {
            if (pending) {
                ['Actualizando los créditos de tu cuenta…', 'Créditos mensuales usados', 'Asignación mensual'].forEach(label => {
                    cards.push(`<div class="usage-panel usage-credit-card"><span class="usage-credit-label">${label}</span><span class="usage-loading-line" aria-hidden="true"></span></div>`);
                });
            } else {
                cards.push('<div class="usage-panel usage-credit-message"><h3>Los créditos no están disponibles</h3><p>Se volverá a revisar automáticamente. También puedes usar Actualizar o abrir Uso en Ollama.</p></div>');
            }
            $('plan-note').textContent = '';
        }
        html('credit-cards', cards.join(''));
    }
    function health(state, label, message, detail = '', retryAccount = false) {
        $('health').dataset.state = state;
        $('connection-state').textContent = label;
        $('status').textContent = message;
        if (detail !== null) {
            $('connection-details').hidden = !detail;
            $('connection-reason').textContent = detail;
        }
        $('retry-account').hidden = !retryAccount;
    }
    function render() {
        const provider = data.provider || {}, cloud = provider.ranges?.[range] || {};
        const totals = cloud.data?.totals || {}, daily = cloud.data?.daily || [];
        const balance = provider.balance || {}, activity = data.activity || {}, chatTotals = activity.totals || {};
        const notes = [data.provider_error, balance.error, cloud.error, data.activity_error];
        if (activity.recording_failures) notes.push('No se pudieron guardar algunas llamadas del chat durante esta sesión de la app; los totales están incompletos.');
        if (activity.pending || provider.pending) schedule();
        clearTimeout(retry); retry = null;
        let retryNote = '';
        if (n(provider.retry_after_seconds) && provider.retry_after_seconds > 0) {
            const seconds = Math.ceil(provider.retry_after_seconds);
            const next = new Date(Date.now() + seconds * 1000).toLocaleTimeString();
            retryNote = `Próxima revisión automática: ${next}.`;
        }
        if (cloud.stale && cloud.data) notes.push('Se muestra el último snapshot disponible de la cuenta; las cifras pueden haber cambiado.');
        if (balance.stale && balance.data) notes.push('Los créditos muestran el último saldo verificado; usa Actualizar para volver a revisar.');
        if (chatTotals.missing_output_calls) notes.push(`${count(chatTotals.missing_output_calls)} llamadas medidas no reportaron tokens de output. Los totales de output son parciales.`);
        const details = [...new Set([...notes, provider.account_error, retryNote].filter(Boolean))].join('\n');
        const accountRetry = ['connection', 'connection_reset', 'timeout', 'invalid_json'].includes(provider.account_error_kind);
        if (provider.pending) {
            health('checking', 'Revisando', 'Actualizando tu cuenta. Las cifras disponibles siguen visibles.', details);
        } else if (notes.some(Boolean)) {
            health('attention', balance.data || cloud.data ? 'Datos parciales' : 'No disponible',
                'No se pudieron actualizar algunas cifras. Abajo se muestran los datos disponibles; los detalles explican qué requiere atención.', details, accountRetry);
        } else if (provider.account_error) {
            health('partial', 'Créditos disponibles',
                provider.account_error_kind === 'authentication'
                    ? 'Tus cifras se cargaron. Inicia sesión en Ollama para verificar el nombre de la cuenta.'
                    : 'Tus cifras se cargaron. El nombre de la cuenta no está disponible.', details, accountRetry);
        } else {
            health('connected', 'Conectado', 'Abajo se muestran las cifras más recientes de la cuenta. Tu actividad del chat se registra por separado.');
        }
        $('account-note').textContent = `${provider.account_available ? provider.account : 'Cuenta de Ollama'}${provider.plan ? ' · ' + provider.plan.toUpperCase() : ''} · La actividad de la cuenta incluye el uso fuera de Tlamatini. Las fechas están en UTC.`;
        creditCards(balance.data, provider.pending);
        const accountMetrics = [
            ['Gasto del periodo', totals.usage_usd, 'Últimos ' + range + ' · aparte de los créditos mensuales', money],
            ['Solicitudes', totals.request_count, 'Tu cuenta · últimos ' + range, count],
            ['Tokens de input', totals.input_tokens, 'Incluye el input en caché · últimos ' + range, count],
            ['Tokens de output', totals.output_tokens, 'Recibidos · últimos ' + range, count]
        ];
        metrics('cloud-totals', accountMetrics.filter(row => n(row[1])).map(([label, value, note, format]) => [label, format(value), note]));
        $('spend-panel').hidden = !daily.some(row => n(row.usage_usd));
        $('token-panel').hidden = !daily.some(row => n(row.input_tokens) || n(row.output_tokens));
        $('composition-panel').hidden = ![totals.input_tokens, totals.cached_input_tokens, totals.output_tokens].every(n);
        chart('spend-chart', daily, ['usage_usd'], true);
        chart('token-chart', daily, ['input_tokens', 'output_tokens']);
        $('spend-peak').textContent = peak(daily, 'usage_usd', money) + ' El ámbar marca los días parciales.';
        const input = totals.input_tokens, cached = totals.cached_input_tokens, output = totals.output_tokens;
        if ([input, cached, output].every(n) && cached <= input) {
            const grand = input + output, fresh = input - cached, denom = grand || 1;
            html('composition', `<div class="usage-stack" aria-label="Composición de tokens"><span style="width:${100 * fresh / denom}%;background:#70c5ed"></span><span style="width:${100 * cached / denom}%;background:#75d8ba"></span><span style="width:${100 * output / denom}%;background:#c0a0f3"></span></div><div class="usage-legend"><span class="usage-dot" style="--dot:#70c5ed">Input nuevo: ${count(fresh)}</span><span class="usage-dot" style="--dot:#75d8ba">Input en caché: ${count(cached)}</span><span class="usage-dot usage-output">Output: ${count(output)}</span></div><p>Total: ${count(grand)} tokens · Tasa de aciertos de caché: ${input ? (cached / input * 100).toFixed(1) + '%' : 'Sin tokens de input'}</p>`);
        } else html('composition', '<p>Esta respuesta no trae la composición completa de tokens.</p>');
        const fields = [['usage_usd', 'Créditos (USD)', money], ['request_count', 'Solicitudes', count], ['input_tokens', 'Input', count], ['cached_input_tokens', 'Input en caché', count], ['output_tokens', 'Output', count]].filter(([key]) => daily.some(row => n(row[key])));
        table('cloud-table', ['Fecha (UTC)', ...fields.map(row => row[1])], daily.map(r => [r.date + (r.partial ? ' · parcial' : ''), ...fields.map(([key, , format]) => format(r[key]))]));
        $('activity-note').textContent = (activity.scope || data.activity_error || 'Esperando el uso registrado.') + (activity.since ? ` Con registro desde ${date(activity.since)}.` : ' El registro empieza con tu siguiente llamada medida del chat.');
        metrics('chat-totals', [['Llamadas a modelos', count(chatTotals.calls), 'Llamadas completadas y medidas'], ['Tokens de input', count(chatTotals.input_tokens), 'Procesados por tus modelos del chat'], ['Tokens de output', count(chatTotals.output_tokens), chatTotals.missing_output_calls ? 'Parcial · algunas llamadas no reportaron conteos' : 'Reportados por tus modelos del chat'], ['Modelos usados', activity.models ? count(activity.models.length) : '—', 'Nombres de modelo distintos en este periodo']]);
        chart('chat-chart', activity.daily || [], ['input_tokens', 'output_tokens']);
        const maxCalls = Math.max(1, ...(activity.daily || []).map(r => r.calls));
        html('calendar', (activity.daily || []).map(r => `<div tabindex="0" class="usage-calendar-cell" style="--cell-bg:rgba(85,187,170,${.08 + r.calls / maxCalls * .6})" data-tip="${esc(r.date + ' UTC\n' + count(r.calls) + ' llamadas\n' + count(r.input_tokens + r.output_tokens) + ' tokens')}">${esc(r.date.slice(8))}<small>${count(r.calls)} llamadas</small></div>`).join(''));
        $('chat-peak').textContent = peak(activity.daily || [], 'calls', v => count(v) + ' llamadas');
        table('chat-table', ['Fecha (UTC)', 'Llamadas', 'Input', 'Output', 'Conteos de output faltantes'], (activity.daily || []).map(r => [r.date, count(r.calls), count(r.input_tokens), count(r.output_tokens), count(r.missing_output_calls)]));
        modelBars('model-chart', activity.models || [], false); modelBars('model-calls', activity.models || [], true);
        table('model-table', ['Modelo', 'Llamadas', 'Input', 'Output', 'Tokens totales', 'Fecha pico (UTC)', 'Llamadas en el pico', 'Conteos de output faltantes'], (activity.models || []).map(r => [r.model, count(r.calls), count(r.input_tokens), count(r.output_tokens), count(r.input_tokens + r.output_tokens), r.peak_day, count(r.peak_calls), count(r.missing_output_calls)]));
        $('ollama-version').textContent = provider.version ? 'Ollama ' + provider.version : '';
        const size = v => n(v) ? (v / 1024 ** 3).toFixed(2) + ' GiB' : 'No disponible';
        $('running').textContent = provider.running_error || ((provider.running || []).length ? 'Cargados: ' + provider.running.map(m => `${m.name} (${size(m.size)}, expira ${m.expires_at ? new Date(m.expires_at).toLocaleString() : 'sin reportar'})`).join(' · ') : 'No hay modelos cargados en este momento.');
        if (provider.models_error) html('inventory', `<p>${esc(provider.models_error)}</p>`);
        else table('inventory', ['Modelo', 'Origen', 'Estado', 'Tamaño', 'Familia', 'Parámetros', 'Cuantización', 'Modificado'], (provider.models || []).map(m => [m.name, m.cloud ? 'Nube · ' + m.remote_host : 'Local', m.loaded ? 'Cargado' : 'Disponible', size(m.size), m.family || '—', m.parameters || '—', m.quantization || '—', date(m.modified_at)]));
        $('updated').textContent = 'Chat revisado: ' + new Date().toLocaleTimeString() + (balance.updated_at ? ' · Créditos: ' + new Date(balance.updated_at).toLocaleTimeString() : ' · Hace falta actualizar la cuenta');
    }

    async function refresh(force = false) {
        if (document.hidden || sessionInvalid) return;
        if (controller) { again = true; forceAgain = forceAgain || force === true; return; }
        const current = generation, selected = range;
        const abort = new AbortController(); controller = abort;
        const timeout = setTimeout(() => abort.abort(), 15000);
        $('refresh').disabled = true;
        $('retry-account').disabled = true;
        $('refresh').textContent = 'Revisando…';
        dialog.setAttribute('aria-busy', 'true');
        health('checking', 'Revisando', 'Actualizando tu cuenta…', null);
        if (!ready) menuState(false, 'Revisando el uso…');
        if (!data) creditCards(null, true);
        let delay = 15;
        try {
            const response = await fetch(overlay.dataset.url + '?range=' + range + (force === true ? '&refresh=1' : ''), { credentials: 'same-origin', cache: 'no-store', signal: abort.signal });
            if (response.redirected || response.status === 401 || response.status === 403) {
                sessionInvalid = true;
                throw Error('Tu sesión expiró. Recarga el chat para volver a iniciar sesión.');
            }
            if (!response.ok) throw Error(`No se pudo actualizar el uso (HTTP ${response.status} del servidor). Se reintentará automáticamente en 15 segundos.`);
            const next = await response.json();
            if (String(next.user_id) !== overlay.dataset.userId) {
                data = null; sessionInvalid = true;
                dialog.querySelectorAll('[role="tabpanel"]').forEach(p => { p.hidden = true; });
                dialog.querySelectorAll('button:not(.usage-close)').forEach(button => { button.disabled = true; });
                throw Error('Cambió el usuario con sesión iniciada en este browser. Recarga el chat antes de ver el uso.');
            }
            if (current !== generation || selected !== range) return;
            // Both the core's data check and the real renderer must succeed
            // before a click can open this dialog. Preflight never opens it.
            data = next;
            try { render(); }
            catch (error) {
                menuState(false, 'No se pudo mostrar el uso. Se reintentará automáticamente.');
                throw error;
            }
            menuState(next.readiness?.ready === true, next.readiness?.message || 'Revisando el uso…');
            lastCheck = Date.now();
            delay = providerDelay(next);
        } catch (error) {
            if (current === generation) {
                const reason = error.name === 'AbortError' ? 'Hubo un timeout al actualizar. Las cifras actuales pueden estar desactualizadas. Se reintentará automáticamente en 15 segundos.' : error instanceof TypeError ? 'No se pudo contactar al servidor de Tlamatini. Se reintentará automáticamente en 15 segundos.' : error.message;
                if (sessionInvalid) {
                    data = null;
                    dialog.querySelectorAll('[role="tabpanel"]').forEach(p => { p.hidden = true; });
                    menuState(false, 'Recarga el chat para verificar tu sesión.');
                } else if (!ready) menuState(false, 'El uso no está disponible por ahora. Se volverá a revisar automáticamente.');
                health('attention', sessionInvalid ? 'La sesión cambió' : 'Conexión interrumpida',
                    'No se pudo actualizar el uso. ' + (sessionInvalid ? 'Recarga el chat para continuar.' : 'Se reintentará automáticamente; las cifras actuales pueden estar desactualizadas.'), reason);
            }
        } finally {
            clearTimeout(timeout);
            if (controller === abort) controller = null;
            $('refresh').disabled = sessionInvalid;
            $('retry-account').disabled = sessionInvalid;
            $('refresh').textContent = 'Actualizar';
            dialog.setAttribute('aria-busy', 'false');
            if (!sessionInvalid) queueCheck(delay);
            if (again) { again = false; schedule(); }
        }
    }
    function providerDelay(value) {
        if (value.provider?.pending || value.activity?.pending) return 1;
        const seconds = value.readiness?.retry_after_seconds;
        return n(seconds) && seconds > 0 ? Math.min(seconds, overlay.hidden ? 60 : 30) : overlay.hidden ? 60 : 30;
    }
    function schedule() {
        if (scheduled || sessionInvalid) return;
        scheduled = setTimeout(() => { scheduled = null; const force = forceAgain; forceAgain = false; refresh(force); }, 900);
    }
    function close() {
        generation++; overlay.hidden = true; controller?.abort(); again = false; forceAgain = false;
        clearTimeout(scheduled); clearTimeout(retry); scheduled = null; retry = null;
        $('tooltip').hidden = true; document.body.style.overflow = oldOverflow;
        inertSiblings.forEach(([el, inert]) => { el.inert = inert; }); inertSiblings = [];
        (lastFocus?.isConnected && !lastFocus.disabled && lastFocus.getClientRects().length ? lastFocus : document.getElementById('about-menu-button')).focus();
        if (!sessionInvalid) queueCheck(ready ? 60 : 15);
    }
    function open(event) {
        event?.preventDefault(); if (!overlay.hidden) return;
        if (!ready || sessionInvalid || opener.disabled) { schedule(); return; }
        generation++; lastFocus = document.activeElement; oldOverflow = document.body.style.overflow;
        // The overlay is a direct body child; preserve the existing inert states.
        inertSiblings = [...document.body.children].filter(el => el !== overlay && !['SCRIPT', 'STYLE'].includes(el.tagName)).map(el => [el, el.inert]);
        inertSiblings.forEach(([el]) => { el.inert = true; });
        document.body.style.overflow = 'hidden'; overlay.hidden = false;
        if (data?.readiness?.default_tab === 'activity') selectTab($('tab-activity'));
        dialog.querySelector('[data-tab][aria-selected="true"]').focus();
        if (Date.now() - lastCheck > 5000) refresh(true);
        else queueCheck(providerDelay(data));
    }
    overlay.tlmDismiss = close; dialog.tlmDismiss = close;
    opener.addEventListener('click', open);
    dialog.querySelectorAll('.usage-close').forEach(button => button.addEventListener('click', close));
    $('refresh').addEventListener('click', () => refresh(true));
    $('retry-account').addEventListener('click', () => refresh(true));
    dialog.querySelectorAll('[data-range]').forEach(button => button.addEventListener('click', () => {
        range = button.dataset.range;
        dialog.querySelectorAll('[data-range]').forEach(el => el.setAttribute('aria-pressed', String(el === button)));
        $('status').textContent = 'Cargando ' + range + ' de uso…'; refresh();
    }));
    function selectTab(button) {
        dialog.querySelectorAll('[data-tab]').forEach(el => { el.setAttribute('aria-selected', String(el === button)); el.tabIndex = el === button ? 0 : -1; });
        dialog.querySelectorAll('[role="tabpanel"]').forEach(el => { el.hidden = el.id !== 'usage-' + button.dataset.tab; });
        $('tooltip').hidden = true;
    }
    dialog.querySelectorAll('[data-tab]').forEach(button => {
        button.addEventListener('click', () => selectTab(button));
        button.addEventListener('keydown', event => {
            const tabs = [...dialog.querySelectorAll('[data-tab]')], index = tabs.indexOf(button);
            const next = { ArrowRight: (index + 1) % 3, ArrowLeft: (index + 2) % 3, Home: 0, End: 2 }[event.key];
            if (next !== undefined) { event.preventDefault(); selectTab(tabs[next]); tabs[next].focus(); }
        });
    });
    dialog.addEventListener('keydown', event => {
        if (event.key !== 'Tab') return;
        const focusable = [...dialog.querySelectorAll('button,a[href],input,summary,[tabindex="0"]')].filter(el => !el.disabled && el.getClientRects().length);
        const first = focusable[0], last = focusable[focusable.length - 1];
        if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog)) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    document.addEventListener('tlm:context-gauge', () => { if (!overlay.hidden || !ready) schedule(); });
    function recheck() { if (Date.now() - lastCheck > 3000) schedule(); }
    document.addEventListener('visibilitychange', () => { if (!document.hidden) recheck(); });
    window.addEventListener('focus', recheck);
    window.addEventListener('online', () => refresh(true));
    document.getElementById('about-menu-button')?.addEventListener('click', recheck);
    function tooltip(event) {
        const target = event.target.closest('[data-tip]'); if (!target) return;
        const tip = $('tooltip'), rect = target.getBoundingClientRect(); tip.textContent = target.dataset.tip; tip.hidden = false;
        tip.style.left = Math.max(8, Math.min(rect.left, innerWidth - tip.offsetWidth - 12)) + 'px';
        tip.style.top = Math.max(8, Math.min(rect.top - tip.offsetHeight - 8, innerHeight - tip.offsetHeight - 12)) + 'px';
    }
    dialog.addEventListener('pointerover', tooltip);
    dialog.addEventListener('focusin', event => requestAnimationFrame(() => tooltip(event)));
    dialog.addEventListener('pointerout', event => {
        if (event.target.closest('[data-tip]') !== event.relatedTarget?.closest?.('[data-tip]')) $('tooltip').hidden = true;
    });
    dialog.addEventListener('focusout', () => { $('tooltip').hidden = true; });
    dialog.querySelector('.usage-body').addEventListener('scroll', () => {
        $('tooltip').hidden = true;
        if (document.activeElement.closest('[data-tip]')) requestAnimationFrame(() => tooltip({ target: document.activeElement }));
    }, { passive: true });
    menuState(false, 'Revisando el uso…');
    refresh();
})();
