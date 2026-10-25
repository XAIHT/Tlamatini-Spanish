/* Tlamatini — "one who knows"
 * Created by Angela López Mendoza · @angelahack1
 * Tlamatini Author Banner — do not remove */
(() => {
    'use strict';
    // The JSON contract stays stable when a flow file is renamed to .fpmt.
    const FORMAT = 'tlamatini-prompting-flow';
    const EXTENSION = '.fpmt';
    const VERSION = 2;
    const commentColors = [['#fbcfe8', 'Rosa'], ['#fef3c7', 'Amarillo'], ['#dcfce7', 'Verde'], ['#dbeafe', 'Azul'], ['#ede9fe', 'Morado'], ['#ffedd5', 'Naranja'], ['#ffffff', 'Blanco'], ['#e5e7eb', 'Gris']];
    const commentTextColors = [['#202938', 'Tinta'], ['#000000', 'Negro'], ['#1d4ed8', 'Azul'], ['#166534', 'Verde'], ['#7e22ce', 'Morado'], ['#b91c1c', 'Rojo'], ['#92400e', 'Café'], ['#ffffff', 'Blanco']];
    const commentFonts = ['Nunito', 'Arial', 'Verdana', 'Georgia', 'Times New Roman', 'Courier New'];
    // Terminater: a visible CMD / PowerShell terminal step (the parallelogram). Keep these lists
    // identical to agent/services/prompt_flow_panel.py.
    const terminaterActions = ['run', 'open', 'type', 'send_key', 'wait', 'read', 'commands', 'abort', 'kill', 'force_kill', 'kill_all', 'list', 'status', 'focus', 'rename', 'layout', 'clear', 'watch_user', 'warn_user', 'handover'];
    const terminaterKinds = ['cmd', 'powershell', 'pwsh'];
    const terminaterTextActions = ['run', 'type', 'handover'];
    const terminaterDefaults = { action: 'run', kind: 'powershell', terminal: '', title: '', cwd: '', keys: '', message: '', severity: 'warning', suggestion: '', hint: '', which: 'last', until: '', pattern: '', layout: '', area: '', submit: true, secret: false, wait: true, close_after: false, load_profile: true, advisor: true, typing_wpm: 50, wait_seconds: 120, hang_seconds: 45, user_wait_seconds: 300, idle_seconds: 2, use_my_defaults: false, explanation: '' };
    const terminaterTextLimits = { terminal: 80, title: 80, cwd: 1000, keys: 500, message: 2000, suggestion: 1000, hint: 200, which: 40, until: 20, pattern: 500, explanation: 1000 };
    const terminaterNumbers = { typing_wpm: [20, 160, true], wait_seconds: [1, 3600, false], hang_seconds: [3, 3600, false], user_wait_seconds: [5, 3600, false], idle_seconds: [0.2, 600, false] };
    const isFlowFilename = name => /\.fpmt$/i.test(name);
    // Migrate old flow draft/save names without changing system prompt files.
    const flowFilename = name => isFlowFilename(name) ? name : name.replace(/\.pmt$/i, '') + EXTENSION;
    const operations = {
        // Side ports sit on each outline; Decision uses ACP's 33%/66% dual outputs.
        prompt: { label: 'Prompt', color: '#83c0f3', fill: '#304965', path: 'M4 20H196V108H4Z', input: [4, 64], output: [196, 64], help: 'Envía un prompt al modelo de Tlamatini configurado.' },
        programmed_prompt: { label: 'Prompt programado', color: '#d7b9f5', fill: '#4d3867', path: 'M4 20H196V108H4Z', input: [4, 64], output: [196, 64], help: 'Espera un tiempo o una hora programada y luego envía un prompt.' },
        decision: { label: 'Decisión', color: '#f0cf72', fill: '#61512e', path: 'M100 4L196 64L100 124L4 64Z', input: [4, 64], yes: [161.184, 42.24], no: [163.232, 84.48], help: 'Sigue por Sí o por No según el último output, o le pregunta al usuario.' },
        feed_embeddings: { label: 'Agregar embeddings', color: '#77d8b2', fill: '#285849', path: 'M100 4L196 120H4Z', input: [100 - 96 * 60 / 116, 64], output: [100 + 96 * 60 / 116, 64], help: 'Agrega texto al contexto de recuperación de esta ejecución.' },
        flush_embeddings: { label: 'Vaciar embeddings', color: '#f0a88b', fill: '#684237', path: 'M4 8H196L100 124Z', input: [4 + 96 * 56 / 116, 64], output: [196 - 96 * 56 / 116, 64], help: 'Quita los embeddings de esta ejecución y conserva su conversación.' },
        clean_history: { label: 'Limpiar historial', color: '#90cddc', fill: '#315665', path: 'M4 14H196L160 114H40Z', input: [22, 64], output: [178, 64], help: 'Borra la conversación y el último output de esta ejecución; conserva sus embeddings.' },
        user_input: { label: 'Input del usuario', color: '#eaaed6', fill: '#653d59', path: 'M52 4L100 38L148 4V88L100 124L52 88Z', input: [52, 64], output: [148, 64], help: 'Hace una pausa para pedir una respuesta al usuario y la agrega a la conversación.' },
        terminater: { label: 'Terminater', color: '#7ee8a6', fill: '#1e4d38', path: 'M52 20H196L148 108H4Z', input: [28, 64], output: [172, 64], help: 'Ejecuta un comando en una terminal visible de CMD o PowerShell, escrito a velocidad humana. Usa <<USER:hint>> para darle el teclado al usuario durante una parte del comando.' },
        user_commentary: { label: 'Comentario del usuario', color: '#eaaed6', fill: '#653d59', path: 'M28 10H172Q196 10 196 34V82Q196 106 172 106H70L48 124L33 106H28Q4 106 4 82V34Q4 10 28 10Z', static: true, help: 'Una nota estática de revisión. Haz doble clic para escribir. Usa la barra de herramientas flotante para darle formato; arrastra cualquier borde o esquina para cambiar el tamaño. Nunca se ejecuta.' },
    };
    const copy = value => JSON.parse(JSON.stringify(value));
    function uniqueLabel(label, used) {
        const base = label.replace(/ \(\d+\)$/, '');
        let index = 2, candidate;
        do {
            const suffix = ` (${index++})`;
            candidate = base.slice(0, 120 - suffix.length) + suffix;
        } while (used.has(candidate));
        return candidate;
    }
    const id = () => 'pmt_' + (globalThis.crypto?.randomUUID?.() || Date.now().toString(36) + Math.random().toString(36).slice(2));
    const blank = () => ({ format: FORMAT, version: VERSION, name: 'Untitled', start: null, max_steps: 500, nodes: [], edges: [] });
    const isComment = n => n.type === 'user_commentary';
    const size = n => isComment(n) ? { width: n.config.width, height: n.config.height } : { width: 200, height: 128 };
    function node(type, x, y) {
        const config = { text: '' };
        if (type === 'prompt' || type === 'programmed_prompt') Object.assign(config, { multi_turn: false, acpx: false });
        if (type === 'programmed_prompt') Object.assign(config, { delay_seconds: 5, scheduled_at: '' });
        if (type === 'decision') Object.assign(config, { comparison: 'contains', value: '', case_sensitive: false });
        if (type === 'terminater') Object.assign(config, terminaterDefaults, { use_my_defaults: true });
        if (type === 'user_commentary') Object.assign(config, { width: 360, height: 160, color: '#fef3c7', text_color: '#202938', font_family: 'Nunito', font_size: 16, bold: false, italic: false, underline: false, align: 'left', runs: [] });
        return { id: id(), type, label: operations[type].label, x, y, config };
    }
    const commentStyleKeys = ['font_family', 'font_size', 'text_color', 'bold', 'italic', 'underline'];
    const commentStyle = c => Object.fromEntries(commentStyleKeys.map(key => [key, key === 'underline' ? !!c[key] : c[key]]));
    function mergeCommentRuns(runs) {
        const merged = [];
        for (const run of runs) {
            if (!run.text) continue;
            const last = merged[merged.length - 1];
            if (last && commentStyleKeys.every(key => last[key] === run[key])) last.text += run.text;
            else merged.push({ text: run.text, ...commentStyle(run) });
        }
        return merged;
    }
    function sliceCommentRuns(runs, start, end) {
        let offset = 0;
        return runs.flatMap(run => {
            const from = Math.max(0, start - offset), to = Math.min(run.text.length, end - offset);
            offset += run.text.length;
            return to > from ? [{ ...run, text: run.text.slice(from, to) }] : [];
        });
    }
    const commentRuns = c => c.runs || (c.text ? [{ text: c.text, ...commentStyle(c) }] : []);
    function replaceCommentRange(c, start, end, replacement) {
        const runs = commentRuns(c);
        c.runs = mergeCommentRuns([...sliceCommentRuns(runs, 0, start), ...replacement, ...sliceCommentRuns(runs, end, c.text.length)]);
        c.text = c.runs.map(run => run.text).join('');
    }
    function validate(value, playable = false) {
        const fail = message => { throw new Error(message); };
        if (!value || value.format !== FORMAT) fail('Este no es un documento de Prompt Flow Panel. El texto antiguo de prompt.pmt no es un diagrama.');
        if (![1, VERSION].includes(value.version)) fail('Versión de .fpmt no compatible. Este panel admite las versiones 1 y 2.');
        const legacy = value.version === 1;
        const flow = copy(value);
        const text = (s, max, label) => { if (typeof s !== 'string' || s.length > max) fail(`${label} debe ser un texto de ${max.toLocaleString()} caracteres como máximo.`); return s; };
        const number = (n, min, max, label) => { if (typeof n !== 'number' || !Number.isFinite(n) || n < min || n > max) fail(`${label} debe estar entre ${min} y ${max}.`); return n; };
        text(flow.name, 120, 'Nombre del flow');
        number(flow.max_steps, 1, 5000, 'Límite de pasos');
        if (!Number.isInteger(flow.max_steps)) fail('El límite de pasos debe ser un número entero.');
        if (!Array.isArray(flow.nodes) || flow.nodes.length > 500 || !Array.isArray(flow.edges) || flow.edges.length > 1000) fail('Usa hasta 500 operaciones y 1,000 conexiones.');
        const known = new Map(), slots = new Set(), edgeIds = new Set();
        for (const n of flow.nodes) {
            if (!n || typeof n.id !== 'string' || !/^[A-Za-z0-9_-]{1,80}$/.test(n.id) || known.has(n.id)) fail('Los IDs de las operaciones deben ser únicos y usar sólo letras, dígitos, guiones bajos o guiones.');
            if (legacy && n.type === 'user_commentary') { n.type = 'user_input'; if (n.label === 'User Commentary') n.label = 'Input del usuario'; }
            if (!Object.hasOwn(operations, n.type)) fail('Tipo de operación desconocido.');
            text(n.label, 120, 'Etiqueta'); number(n.x, 0, 100000, 'X'); number(n.y, 0, 100000, 'Y');
            if (!n.config || typeof n.config !== 'object' || Array.isArray(n.config)) fail('Falta la configuración de la operación.');
            text(n.config.text, 100000, 'Texto de la operación');
            if (isComment(n)) {
                const c = n.config;
                for (const [key, fallback, min, max] of [['width', 320, 200, 2400], ['height', 200, 128, 2400], ['font_size', 16, 10, 48]]) { if (c[key] === undefined) c[key] = fallback; number(c[key], min, max, `${key} del comentario`); }
                for (const [key, fallback] of [['color', '#fbcfe8'], ['text_color', '#202938'], ['font_family', 'Nunito'], ['align', 'left'], ['bold', false], ['italic', false], ['underline', false]]) if (c[key] === undefined) c[key] = fallback;
                if (!commentColors.some(([color]) => color === c.color) || !commentTextColors.some(([color]) => color === c.text_color) || !commentFonts.includes(c.font_family) || !['left', 'center', 'right'].includes(c.align)) fail('Elige un color, una fuente y una alineación compatibles para el comentario.');
                if (typeof c.bold !== 'boolean' || typeof c.italic !== 'boolean' || typeof c.underline !== 'boolean') fail('Los interruptores de estilo del comentario deben ser true o false.');
                if (c.runs === undefined) c.runs = c.text ? [{ text: c.text, ...commentStyle(c) }] : [];
                if (!Array.isArray(c.runs) || c.runs.length > 10000) fail('Usa como máximo 10,000 fragmentos de texto con formato por comentario.');
                c.runs = c.runs.map(run => {
                    if (!run || typeof run !== 'object' || Array.isArray(run)) fail('Un fragmento de texto con formato debe ser un objeto.');
                    text(run.text, 100000, 'Texto del fragmento del comentario');
                    const style = { ...commentStyle(c), ...run };
                    number(style.font_size, 10, 48, 'Tamaño de fuente del fragmento del comentario');
                    if (!commentFonts.includes(style.font_family) || !commentTextColors.some(([color]) => color === style.text_color)) fail('Elige una fuente y un color de texto compatibles para el comentario.');
                    if (['bold', 'italic', 'underline'].some(key => typeof style[key] !== 'boolean')) fail('Los interruptores de estilo de los fragmentos del comentario deben ser true o false.');
                    return { text: run.text, ...commentStyle(style) };
                });
                if (c.runs.map(run => run.text).join('') !== c.text) fail('Los fragmentos deben contener exactamente el texto del comentario.');
                c.runs = mergeCommentRuns(c.runs);
                n.config = Object.fromEntries(['text', 'runs', 'width', 'height', 'color', 'text_color', 'font_family', 'font_size', 'bold', 'italic', 'underline', 'align'].map(key => [key, c[key]]));
            }
            if (['prompt', 'programmed_prompt'].includes(n.type)) {
                if (typeof n.config.multi_turn !== 'boolean' || typeof n.config.acpx !== 'boolean') fail('Los interruptores del prompt deben ser true o false.');
                if (n.config.acpx && !n.config.multi_turn) fail('ACPX requiere Multi-Turn.');
            }
            if (playable && ['prompt', 'programmed_prompt', 'feed_embeddings'].includes(n.type) && !n.config.text.trim()) fail(`${n.label} necesita texto. Haz doble clic en la operación para configurarla.`);
            if (n.type === 'programmed_prompt') {
                number(n.config.delay_seconds, 0, 86400, 'Retraso');
                text(n.config.scheduled_at, 60, 'Hora programada');
                if (n.config.scheduled_at && (!Number.isFinite(Date.parse(n.config.scheduled_at)) || !/(Z|[+-]\d{2}:\d{2})$/.test(n.config.scheduled_at))) fail('La hora programada necesita una fecha y una zona horaria válidas.');
            }
            if (n.type === 'decision') {
                if (!['contains', 'not_contains', 'equals', 'is_empty', 'user'].includes(n.config.comparison)) fail('Comparación de decisión desconocida.');
                text(n.config.value, 10000, 'Valor de comparación');
                if (typeof n.config.case_sensitive !== 'boolean') fail('La distinción entre mayúsculas y minúsculas debe ser true o false.');
                if (playable && ['contains', 'not_contains', 'equals'].includes(n.config.comparison) && !n.config.value) fail(`${n.label} necesita un valor de comparación.`);
            }
            if (n.type === 'terminater') {
                const c = n.config;
                for (const [key, fallback] of Object.entries(terminaterDefaults)) if (c[key] === undefined) c[key] = fallback;
                if (!terminaterActions.includes(c.action)) fail('Acción de Terminater desconocida.');
                if (!terminaterKinds.includes(c.kind)) fail('Elige CMD, PowerShell o PowerShell 7.');
                for (const [key, max] of Object.entries(terminaterTextLimits)) text(c[key], max, `Terminater ${key}`);
                if (!['info', 'hint', 'warning', 'danger'].includes(c.severity)) fail('Severidad de Terminater desconocida.');
                if (!['', 'tabs', 'tile', 'tile-h', 'tile-v', 'grid'].includes(c.layout) || !['', 'dock', 'full'].includes(c.area)) fail('Distribución o área de Terminater desconocida.');
                for (const key of ['submit', 'secret', 'wait', 'close_after', 'load_profile', 'advisor', 'use_my_defaults']) if (typeof c[key] !== 'boolean') fail(`Terminater ${key} debe ser true o false.`);
                for (const [key, [min, max, integer]] of Object.entries(terminaterNumbers)) {
                    number(c[key], min, max, `Terminater ${key}`);
                    if (integer && !Number.isInteger(c[key])) fail(`Terminater ${key} debe ser un número entero.`);
                }
                if (playable && terminaterTextActions.includes(c.action) && !n.config.text.trim()) fail(`${n.label} necesita un comando para escribir.`);
                if (playable && c.action === 'send_key' && !c.keys.trim()) fail(`${n.label} necesita las teclas que se van a presionar.`);
                n.config = Object.fromEntries(['text', ...Object.keys(terminaterDefaults)].map(key => [key, c[key]]));
            }
            known.set(n.id, n);
        }
        for (const e of flow.edges) {
            if (!e || typeof e.id !== 'string' || !/^[A-Za-z0-9_-]{1,80}$/.test(e.id) || edgeIds.has(e.id)) fail('El ID de la conexión no es válido o está duplicado.');
            edgeIds.add(e.id);
            if (!known.has(e.source) || !known.has(e.target)) fail('Una conexión apunta a una operación que no existe.');
            if (isComment(known.get(e.source)) || isComment(known.get(e.target))) fail('Los elementos estáticos de Comentario del usuario no pueden tener conexiones.');
            const allowed = known.get(e.source).type === 'decision' ? ['yes', 'no'] : ['next'];
            const slot = `${e.source}:${e.branch}`;
            if (!allowed.includes(e.branch) || slots.has(slot)) fail('Cada output admite una sola conexión; las decisiones usan Sí y No.');
            slots.add(slot);
        }
        if (flow.start !== null && !known.has(flow.start)) fail('Falta la operación de Inicio.');
        if (flow.start !== null && isComment(known.get(flow.start))) fail('Un Comentario del usuario estático no puede ser la operación de Inicio.');
        if (playable) {
            if (!known.size || !flow.start) fail('Agrega una operación y elígela en Inicio.');
            const reached = new Set(), pending = [flow.start];
            while (pending.length) {
                const current = pending.pop();
                if (reached.has(current)) continue;
                reached.add(current);
                pending.push(...flow.edges.filter(e => e.source === current).map(e => e.target));
            }
            if (reached.size !== flow.nodes.filter(n => !isComment(n)).length) fail('No se puede llegar a algunas operaciones desde el Inicio. Conéctalas o elige otra en Inicio.');
            for (const n of flow.nodes) if (n.type === 'decision' && !['yes', 'no'].every(b => slots.has(`${n.id}:${b}`))) fail('Conecta los outputs Sí y No de cada decisión.');
        }
        // Keep the document a data contract, discarding any unrelated fields.
        return { format: FORMAT, version: VERSION, name: flow.name, start: flow.start, max_steps: flow.max_steps, nodes: flow.nodes.map(n => ({ id: n.id, type: n.type, label: n.label, x: n.x, y: n.y, config: n.config })), edges: flow.edges.map(e => ({ id: e.id, source: e.source, target: e.target, branch: e.branch })) };
    }
    function example() {
        const flow = blank(); flow.name = 'Prompting kickoff';
        const a = node('user_input', 80, 60), b = node('decision', 80, 260), c = node('prompt', 370, 440), d = node('programmed_prompt', 40, 620);
        a.label = 'Elige un tema'; a.config.text = '¿Qué te gustaría explorar? Incluye la palabra “code” para tomar el branch de programación.';
        b.label = '¿Es sobre código?'; b.config.value = 'code';
        c.label = 'Explicar el código'; c.config.text = 'Explica este tema de programación y da un ejemplo breve: {{last_output}}';
        d.label = 'Explorar el tema'; d.config.text = 'Explica este tema en tres puntos claros: {{last_output}}'; d.config.delay_seconds = 2;
        flow.nodes = [a, b, c, d]; flow.start = a.id;
        flow.edges = [{ id: id(), source: a.id, target: b.id, branch: 'next' }, { id: id(), source: b.id, target: c.id, branch: 'yes' }, { id: id(), source: b.id, target: d.id, branch: 'no' }];
        return flow;
    }
    window.PromptFlowPanelModel = Object.freeze({ FORMAT, VERSION, EXTENSION, terminaterActions, terminaterKinds, terminaterDefaults, commentColors, commentTextColors, commentFonts, commentStyleKeys, commentStyle, commentRuns, mergeCommentRuns, sliceCommentRuns, replaceCommentRange, isComment, size, isFlowFilename, flowFilename, operations, copy, uniqueLabel, id, blank, node, validate, example });
})();
