/* Tlamatini Author Banner — Angela López Mendoza */
/* global textEditorCode, canvasSource, canvasSettedAsContext,
   filenameSpan, saveAsButton, getCanvasGeneration, rememberCanvasSource,
   unsetContextButton */
// File lifecycle stays in agent_page_canvas.js. This adapter owns the editable
// document and its saved snapshot; the DOM mirror is compatibility, never input.
(() => {
    'use strict';
    const editor = window.TlamatiniTextEditor;
    const container = document.getElementById('editor-container');
    const host = document.getElementById('text-editor');
    const status = document.getElementById('canvas-edit-status');
    const buttons = Object.fromEntries(['save', 'save-as', 'undo', 'redo', 'find', 'wrap']
        .map(name => [name, document.getElementById(`canvas-${name}-button`)]));
    const MAX_BYTES = 64 * 1024 * 1024;
    let current = null;
    let saving = false;
    let wrap = false;
    window.addEventListener('tlm:interaction-settings', event => {
        if (typeof event.detail?.wrap === 'boolean') { wrap = event.detail.wrap; editor.setWrap(wrap); sync(); }
    });
    window.TlamatiniInteractionSettings?.ready.then(() => {
        const settings = window.TlamatiniInteractionSettings.snapshot();
        if (typeof settings.wrap === 'boolean') { wrap = settings.wrap; editor.setWrap(wrap); sync(); }
        editor.configureAppearance?.(settings);
    });
    let notice = '';
    const normalize = value => String(value).replace(/\r\n?|\n/g, '\n');
    const dirty = () => !!current && editor.getText() !== current.baseline;
    const csrf = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
        decodeURIComponent(document.cookie.split('; ').find(v => v.startsWith('csrftoken='))?.slice(10) || '');

    function beforeUnload(event) {
        if (!dirty() && !saving) return;
        event.preventDefault();
        event.returnValue = '';
    }

    function sync() {
        const pdf = !!window.TlamatiniPdfCanvas?.file;
        const available = !!current || pdf;
        const changed = dirty();
        buttons.save.disabled = buttons['save-as'].disabled = !available || saving;
        buttons.save.textContent = saving ? 'Guardando…' : 'Guardar';
        buttons.save.setAttribute('aria-busy', String(saving));
        const history = current ? editor.historyState() : {};
        buttons.undo.disabled = !current || !history.undo;
        buttons.redo.disabled = !current || !history.redo;
        buttons.find.disabled = buttons.wrap.disabled = !current;
        buttons.wrap.setAttribute('aria-pressed', String(wrap));
        status.dataset.state = saving ? 'saving' : changed ? 'dirty' : 'saved';
        const message = saving ? 'Guardando el archivo…' : notice || (current
            ? `${changed ? '● Cambios sin guardar' : 'Contenido guardado'} · ${current.format.label} · ${current.format.eol === '\r\n' ? 'CRLF' : current.format.eol === '\r' ? 'CR' : 'LF'}`
            : pdf ? 'PDF · documento original (sólo lectura)' : 'Abre un archivo para editarlo.');
        if (status.textContent !== message) status.textContent = message;
        window.removeEventListener('beforeunload', beforeUnload);
        if (changed || saving) window.addEventListener('beforeunload', beforeUnload);
    }

    function inferFormat(raw, bytes = null) {
        const separators = raw.match(/\r\n|\r|\n/g) || [];
        const eol = separators[0] || '\n';
        return { encoding: 'utf-8', bom: false, label: 'UTF-8', eol, separators, bytes };
    }

    async function decodeFile(file) {
        if (file.size > MAX_BYTES) throw new Error('La edición de texto admite archivos de hasta 64 MiB.');
        const bytes = new Uint8Array(await file.arrayBuffer());
        let encoding = 'utf-8';
        let offset = 0;
        if ((bytes[0] === 0xff && bytes[1] === 0xfe && bytes[2] === 0 && bytes[3] === 0) ||
            (bytes[0] === 0 && bytes[1] === 0 && bytes[2] === 0xfe && bytes[3] === 0xff)) {
            throw new Error('Aquí no se puede editar UTF-32. Primero convierte una copia a UTF-8 o UTF-16.');
        }
        if (bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf) offset = 3;
        else if (bytes[0] === 0xff && bytes[1] === 0xfe) { encoding = 'utf-16le'; offset = 2; }
        else if (bytes[0] === 0xfe && bytes[1] === 0xff) { encoding = 'utf-16be'; offset = 2; }
        let text;
        try { text = new TextDecoder(encoding, { fatal: true, ignoreBOM: true }).decode(bytes.subarray(offset)); }
        catch (cause) { throw new Error('Este archivo no es UTF-8 válido ni UTF-16 con BOM. Convierte una copia antes de editarlo para no perder caracteres.', { cause }); }
        for (let i = 0; i < text.length; i++) {
            if (text.charCodeAt(i) < 32 && !'\t\n\r\f'.includes(text[i])) {
                throw new Error('Es un archivo binario. Ábrelo en su aplicación correspondiente.');
            }
        }
        const format = inferFormat(text, bytes);
        Object.assign(format, { encoding, bom: offset > 0,
            label: encoding.toUpperCase() + (offset ? ' BOM' : '') });
        return { text, format };
    }

    function encode(text, state) {
        if (text === state.baseline && state.format.bytes) return new Blob([state.format.bytes]);
        const format = state.format;
        // Preserve existing line terminators by line, including mixed files;
        // newly added lines use the document's first terminator.
        const lines = text.split('\n');
        const raw = lines.map((line, index) => line + (index < lines.length - 1
            ? (format.separators[index] || format.eol) : '')).join('');
        if (format.encoding === 'utf-8') return new Blob([format.bom ? '\ufeff' : '', raw]);
        const bytes = new Uint8Array(raw.length * 2 + (format.bom ? 2 : 0));
        const view = new DataView(bytes.buffer);
        const little = format.encoding === 'utf-16le';
        let offset = 0;
        if (format.bom) { view.setUint16(0, 0xfeff, little); offset = 2; }
        for (let i = 0; i < raw.length; i++) view.setUint16(offset + i * 2, raw.charCodeAt(i), little);
        return new Blob([bytes]);
    }

    function changed(text) {
        if (!current) return;
        if (textEditorCode.textContent !== text) {
            window.TlamatiniCanvasRefresh?.edited();
            textEditorCode.textContent = text;
            notice = '';
            window.TlamatiniMarkdownCanvas?.updateSource(text);
            if (canvasSettedAsContext) {
                unsetContextButton();
                if (canvasSource) canvasSource.contextPending = true;
            }
        }
        sync();
    }

    function open(name, raw, file = null, format = null) {
        current = { name, baseline: normalize(raw), format: format || inferFormat(raw), file };
        notice = '';
        container.classList.add('canvas-editable');
        editor.mount(host, current.baseline, name, changed);
        editor.setWrap(wrap);
        textEditorCode.textContent = current.baseline;
        sync();
    }

    function close() {
        current = null;
        notice = '';
        editor.destroy();
        container.classList.remove('canvas-editable');
        sync();
    }

    async function confirmDiscard() {
        if (saving) {
            await window.tlmAlert('Espera a que termine el guardado en curso antes de reemplazar este documento.', 'Guardando el archivo');
            return false;
        }
        if (!dirty()) return true;
        const state = current;
        const value = editor.getText();
        const confirmed = await window.tlmConfirm(`¿Quieres descartar los cambios sin guardar de ${state.name}?`,
            'Primero guarda para conservar tus cambios. Continuar los descarta; Cancelar deja el editor abierto.', 'Cambios sin guardar');
        // An edit arriving while the confirmation is open was not approved.
        return confirmed && state === current && value === editor.getText();
    }

    async function post(url, form, signal) {
        const response = await fetch(url, { method: 'POST', body: form, signal,
            credentials: 'same-origin', headers: { 'X-CSRFToken': csrf() } });
        if (response.redirected || response.status === 401) throw new Error('Tu sesión expiró. Vuelve a iniciar sesión antes de guardar.');
        if (!response.ok) {
            const result = await response.json().catch(() => ({}));
            throw new Error(result.error || `Error en la operación con el archivo (${response.status}).`);
        }
        return response;
    }

    async function nativeRead(source, signal) {
        const form = new FormData();
        form.append('token', source.native.token);
        const response = await post('/agent/canvas/read/', form, signal);
        const file = new File([await response.blob()], source.name);
        file.canvasRevision = response.headers.get('X-Canvas-Revision');
        return file;
    }

    async function sameBytes(file, expected) {
        if (!expected || file.size !== expected.length) return false;
        const actual = new Uint8Array(await file.arrayBuffer());
        return actual.every((byte, index) => byte === expected[index]);
    }

    async function save(saveAs = false) {
        if (saving || (!current && !window.TlamatiniPdfCanvas?.file)) return false;
        // A pending read must not replace the document behind its Save dialog.
        window.TlamatiniCanvasRefresh?.invalidateReads();
        const state = current;
        const generation = getCanvasGeneration();
        const pdf = window.TlamatiniPdfCanvas?.file;
        const text = state ? editor.getText() : null;
        const blob = pdf || encode(text, state);
        const source = canvasSource;
        const name = pdf?.name || state.name;
        let handle = !saveAs ? source?.handle : null;
        let native = !saveAs ? source?.native : null;
        saving = true;
        notice = '';
        sync();
        try {
            // Request write access directly from Save's user gesture. Browser
            // handles never disclose an absolute path to the local server.
            const permission = handle?.requestPermission
                ? handle.requestPermission({ mode: 'readwrite' }) : null;
            if (permission && await permission !== 'granted') throw new Error('No se concedió el permiso de escritura. Tus cambios se conservan; usa Guardar como… para elegir un destino.');
            let result, decoded;
            if (handle?.createWritable && !pdf) {
                decoded = await decodeFile(new File([blob], name));
                if (!await sameBytes(await handle.getFile(), state.format.bytes)) {
                    throw new Error('El archivo cambió fuera de este editor. Usa Guardar como… para conservar tus cambios por separado, o Actualizar para revisar la versión del disco.');
                }
                const writable = await handle.createWritable();
                try { await writable.write(blob); await writable.close(); }
                catch (error) { await writable.abort().catch(() => {}); throw error; }
                result = { saved: true, filename: name };
            } else if (!['localhost', '127.0.0.1', '[::1]'].includes(location.hostname) && window.showSaveFilePicker) {
                // Remote clients choose a file on THEIR device. This picker is
                // called without any preceding asynchronous work in this branch.
                handle = await window.showSaveFilePicker({ suggestedName: name });
                if (state) decoded = await decodeFile(new File([blob], name));
                const writable = await handle.createWritable();
                try { await writable.write(blob); await writable.close(); }
                catch (error) { await writable.abort().catch(() => {}); throw error; }
                native = null;
                result = { saved: true, filename: handle.name };
            } else {
                if (state) decoded = await decodeFile(new File([blob], name));
                const form = new FormData();
                form.append('file', blob, name);
                if (native) { form.append('token', native.token); form.append('revision', native.revision); }
                result = await (await post('/agent/canvas/save/', form)).json();
                if (!result.saved) { notice = 'Se canceló el guardado. Tu contenido se conserva.'; return false; }
                native = { token: result.token, revision: result.revision };
                handle = null;
            }
            if (state !== current || (!state && generation !== getCanvasGeneration())) return true;
            const savedName = result.filename || name;
            // PDF is a viewer, so saving exports a byte-identical copy. Its
            // original identity, prepared context and live viewer remain intact.
            if (pdf) { notice = `Copia del PDF guardada · ${savedName}`; return true; }
            const file = new File([blob], savedName, { type: pdf ? 'application/pdf' : 'text/plain' });
            const contextPending = !!source?.contextPending || (savedName !== name && canvasSettedAsContext);
            if (savedName !== name && canvasSettedAsContext) unsetContextButton();
            const next = { name: savedName, file, text: decoded.text, handle, native, contextPending };
            next.read = native ? signal => nativeRead(next, signal) : () => handle.getFile();
            rememberCanvasSource(next);
            filenameSpan.textContent = `<<< ${savedName} >>>`;
            filenameSpan.title = result.path || savedName;
            if (state) {
                state.baseline = text;
                state.name = savedName;
                state.file = file;
                state.format = decoded.format;
                editor.setFilename(savedName);
                if (/\.(md|markdown)$/i.test(savedName)) {
                    if (window.TlamatiniMarkdownCanvas?.active) window.TlamatiniMarkdownCanvas.updateFile(file);
                    else window.TlamatiniMarkdownCanvas?.open(savedName, editor.getText(), file);
                } else window.TlamatiniMarkdownCanvas?.close();
            }
            notice = dirty() ? 'Se guardó la revisión anterior · los cambios más recientes no están guardados.' : `Guardado · ${savedName}`;
            return true;
        } catch (error) {
            notice = error.name === 'AbortError' ? 'Se canceló el guardado. Tu contenido se conserva.' : `No se guardó · ${error.message}`;
            return false;
        } finally {
            saving = false;
            sync();
        }
    }

    buttons.save.addEventListener('click', () => save());
    buttons['save-as'].addEventListener('click', () => save(true));
    buttons.undo.addEventListener('click', () => { editor.undo(); editor.focus(); });
    buttons.redo.addEventListener('click', () => { editor.redo(); editor.focus(); });
    buttons.find.addEventListener('click', () => { window.TlamatiniMarkdownCanvas?.selectView(false); editor.find(); });
    buttons.wrap.addEventListener('click', () => { wrap = !wrap; editor.setWrap(wrap); sync(); });
    saveAsButton.addEventListener('click', event => { event.preventDefault(); save(true); });
    document.addEventListener('tlm:canvas-save', event => save(!!event.detail?.saveAs));
    document.addEventListener('keydown', event => {
        if (!(event.ctrlKey || event.metaKey) || event.altKey || event.key.toLowerCase() !== 's' || event.defaultPrevented) return;
        if (!current && !window.TlamatiniPdfCanvas?.file) return;
        if ([...document.querySelectorAll('dialog[open], [role="dialog"], [role="alertdialog"], .modal.show')]
            .some(dialog => dialog.getClientRects().length)) return;
        event.preventDefault();
        save(event.shiftKey);
    });
    window.TlamatiniCanvasEditing = { open, close, sync, decodeFile, confirmDiscard, save,
        openNative: (...args) => window.TlamatiniCanvasRefresh.openNative(...args),
        acceptFile: (file, format) => {
            if (current && !dirty()) { current.file = file; current.format = format; notice = ''; sync(); }
        },
        nativeRead,
        get nativeTarget() { return !!canvasSource?.native; },
        get notice() { return notice; },
        get dirty() { return dirty(); }, get busy() { return saving; },
        get text() { return current ? editor.getText() : textEditorCode.textContent; } };
    sync();
})();
