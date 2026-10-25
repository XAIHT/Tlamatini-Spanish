/* Tlamatini Author Banner — Angela López Mendoza */
/* PDF canvas lifecycle and request bridge. PDF.js runs in an isolated frame. */
(() => {
    'use strict';
    const CHANNEL = 'tlamatini-pdf-canvas';
    const host = document.getElementById('pdf-canvas-host');
    const editor = document.getElementById('editor-container');
    let current = null;
    let pending = null;
    let requestId = 0;

    function createRequestId() {
        if (typeof crypto.randomUUID === 'function') return crypto.randomUUID();
        // Frozen Tlamatini also serves plain HTTP over LAN addresses, where
        // randomUUID is unavailable. getRandomValues still provides secure bytes.
        const bytes = crypto.getRandomValues(new Uint8Array(16));
        bytes[6] = (bytes[6] & 0x0f) | 0x40;
        bytes[8] = (bytes[8] & 0x3f) | 0x80;
        const hex = Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('');
        return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
    }

    function cancelPreparation(state) {
        state.contextAbort?.abort();
        if (state.contextRequestId && state.contextJobPending) {
            const form = new FormData();
            form.append('request_id', state.contextRequestId);
            void fetch('/agent/cancel_pdf_context/', {
                method: 'POST', credentials: 'same-origin', keepalive: true,
                headers: { 'X-CSRFToken': getCsrfToken() }, body: form,
            }).catch(() => {});
        }
    }

    function uploadContext(form, state) {
        return new Promise((resolve, reject) => {
            const request = new XMLHttpRequest();
            const signal = state.contextAbort.signal;
            const abort = () => request.abort();
            request.open('POST', '/agent/prepare_pdf_context/');
            request.setRequestHeader('X-CSRFToken', getCsrfToken());
            request.responseType = 'json';
            request.upload.onprogress = event => {
                window.TlamatiniPdfProgress?.update('upload', event.loaded, event.lengthComputable ? event.total : 0);
            };
            request.onload = () => {
                signal.removeEventListener('abort', abort);
                if (request.status >= 200 && request.status < 300 && request.response?.job) resolve(request.response);
                else reject(new Error(request.response?.error || 'Error al subir el PDF. Vuelve a intentarlo.'));
            };
            request.onerror = () => { signal.removeEventListener('abort', abort); reject(new Error('Error al subir el PDF. Revisa la conexión.')); };
            request.onabort = () => { signal.removeEventListener('abort', abort); reject(new DOMException('Se canceló la preparación del contexto del PDF.', 'AbortError')); };
            signal.addEventListener('abort', abort, { once: true });
            request.send(form);
            if (signal.aborted) abort();
        });
    }

    function syncButtons() {
        if (!current) return;
        for (const button of [copyCanvasButton, contextButton]) {
            button.disabled = !current.ready || inLongOperation || !contextEnabled ||
                (button === contextButton && current.contextBusy);
            button.style.backgroundColor = button.disabled ? '#808080' : 'darkgreen';
        }
        if (canvasSettedAsContext) {
            contextButton.style.backgroundColor = 'gray';
            contextButtonClicked = true;
            contextButton.textContent = 'Usado como contexto';
        }
        window.TlamatiniCanvasRefresh?.sync();
    }

    function dispose(state) {
        if (!state) return;
        state.resolve(false);
        state.textRequest?.reject(new Error('Se cerró el PDF.'));
        if (state.contextBusy) window.TlamatiniPdfProgress?.cancelPreparation();
        cancelPreparation(state);
        // Removing the browsing context terminates its worker, rendering tasks,
        // range reads and observers, even during password/loading/extraction.
        state.frame.remove();
    }

    function close() {
        pending?.cancel();
        if (!current) return;
        dispose(current);
        current = null;
        host.hidden = true;
        editor.hidden = false;
    }

    function open(file) {
        close();
        const frame = document.createElement('iframe');
        frame.title = `PDF: ${file.name}`;
        frame.src = host.dataset.viewerUrl;
        const ready = new Promise(resolve => {
            current = { file, frame, resolve, ready: false, textRequest: null, preparedByMode: new Map() };
        });
        frame.addEventListener('error', () => {
            if (current?.frame === frame) current.resolve(false);
        });
        editor.hidden = true;
        host.hidden = false;
        host.replaceChildren(frame);
        syncButtons();
        return ready;
    }

    function refresh(file, signal) {
        if (!current?.ready) return Promise.reject(new Error('El PDF no está listo para actualizarse.'));
        pending?.cancel();
        const frame = document.createElement('iframe');
        frame.title = `Actualizando el PDF: ${file.name}`;
        frame.src = host.dataset.viewerUrl;
        // Keep the old frame until the replacement is usable. The candidate has
        // full layout dimensions; reveal it only if password entry is needed.
        host.style.position = 'relative';
        frame.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;visibility:hidden';
        return new Promise((resolve, reject) => {
            const state = { file, frame, resolve, ready: false, textRequest: null,
                preparedByMode: new Map(), password: current.password, view: current.view };
            const finish = error => {
                signal.removeEventListener('abort', state.cancel);
                if (pending !== state) return;
                pending = null;
                frame.remove();
                reject(error);
            };
            state.cancel = () => finish(new DOMException('Se canceló la actualización del PDF.', 'AbortError'));
            state.fail = message => finish(new Error(message));
            state.commit = () => {
                if (pending !== state || signal.aborted) return;
                signal.removeEventListener('abort', state.cancel);
                dispose(current);
                current = state;
                pending = null;
                frame.style.cssText = '';
                frame.title = `PDF: ${file.name}`;
                // It is already attached. Moving an iframe through
                // replaceChildren would reload its browsing context and lose
                // the freshly prepared document and restored view.
                syncButtons();
                resolve(true);
            };
            pending = state;
            frame.addEventListener('error', () => state.fail('No se pudo cargar el visor del PDF de reemplazo.'));
            signal.addEventListener('abort', state.cancel, { once: true });
            host.appendChild(frame);
            if (signal.aborted) state.cancel();
        });
    }

    function getText() {
        if (!current?.ready) return Promise.reject(new Error('El PDF todavía se está cargando o no se pudo abrir.'));
        if (current.textRequest) return current.textRequest.promise;
        const id = ++requestId;
        let resolve, reject;
        const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
        current.textRequest = { id, promise, resolve, reject };
        current.frame.contentWindow.postMessage({ channel: CHANNEL, type: 'text', requestId: id }, window.location.origin);
        return promise;
    }

    function prepareContext() {
        if (!current?.ready) return Promise.reject(new Error('El PDF no está listo.'));
        if (current.contextRequest) return current.contextRequest;
        const state = current;
        state.contextAbort = new AbortController();
        state.contextRequestId = null;
        state.contextJobPending = false;
        state.contextBusy = true;
        syncButtons();
        const showStatus = message => state.frame.contentWindow?.postMessage({
            channel: CHANNEL, type: 'context-status', message,
        }, window.location.origin);
        let prepared = null;
        state.contextRequest = (async () => {
            try {
                const processImages = await window.TlamatiniPdfProgress.open(state.file, () => cancelPreparation(state));
                if (current !== state || state.contextAbort.signal.aborted) {
                    throw new DOMException('Se canceló la preparación del contexto del PDF.', 'AbortError');
                }
                prepared = state.preparedByMode.get(processImages);
                if (prepared) {
                    state.prepared = prepared;
                    return prepared;
                }
                state.contextRequestId = createRequestId();
                state.contextJobPending = true;
                showStatus(processImages ? 'Preparando el contexto del PDF: extrayendo todas las páginas, el texto y las imágenes…' : 'Preparando el contexto del PDF: extrayendo el texto seleccionable…');
                const form = new FormData();
                form.append('process_images', String(processImages));
                form.append('request_id', state.contextRequestId);
                form.append('pdf', state.file, state.file.name);
                // Kept only in this document's memory, never localStorage or logs.
                form.append('password', state.password || '');
                const started = await uploadContext(form, state);
                state.contextJob = started.job;
                if (current !== state || state.contextAbort.signal.aborted) cancelPreparation(state);
                while (current === state && !state.contextAbort.signal.aborted) {
                    const poll = await fetch(`/agent/pdf_context_status/?job=${encodeURIComponent(started.job)}`, {
                        credentials: 'same-origin', signal: state.contextAbort.signal,
                    });
                    const result = await poll.json();
                    if (!poll.ok || ['error', 'cancelled'].includes(result.status)) {
                        throw new Error(result.error || result.message || 'Error al preparar el contexto del PDF.');
                    }
                    if (result.status === 'complete') {
                        state.contextJobPending = false;
                        prepared = result.result;
                        state.prepared = prepared;
                        state.preparedByMode.set(processImages, prepared);
                        return prepared;
                    }
                    showStatus(result.message || 'Preparando el contexto del PDF…');
                    window.TlamatiniPdfProgress?.update(result.stage || 'extract', result.completed || 0, result.total || 0, result.message);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
                throw new DOMException('Se canceló la preparación del contexto del PDF.', 'AbortError');
            } catch (error) {
                if (error.name !== 'AbortError' && current === state) window.TlamatiniPdfProgress?.fail(error.message);
                cancelPreparation(state);
                throw error;
            } finally {
                state.contextBusy = false;
                state.contextJobPending = false;
                state.contextRequest = null;
                if (current === state) {
                    showStatus(prepared?.analysis_warnings
                        ? `El contexto del PDF incluye ${prepared.analysis_warnings} advertencias del análisis de imágenes. Revisa los reportes de análisis guardados.` : '');
                    syncButtons();
                }
            }
        })();
        return state.contextRequest;
    }

    window.addEventListener('message', event => {
        if (pending && event.source === pending.frame.contentWindow && event.origin === window.location.origin && event.data?.channel === CHANNEL) {
            const message = event.data;
            if (message.type === 'initialized') {
                pending.frame.contentWindow.postMessage({ channel: CHANNEL, type: 'open', file: pending.file,
                    password: pending.password, view: pending.view }, window.location.origin);
            } else if (message.type === 'ready') {
                pending.ready = true;
                pending.password = message.password || '';
                pending.commit();
            } else if (message.type === 'password-required') {
                pending.frame.style.visibility = 'visible';
            } else if (message.type === 'error') pending.fail(message.message);
            else if (message.type === 'view') pending.view = message.view;
            return;
        }
        if (!current || event.source !== current.frame.contentWindow || event.origin !== window.location.origin || event.data?.channel !== CHANNEL) return;
        const message = event.data;
        if (message.type === 'initialized') {
            current.frame.contentWindow.postMessage({ channel: CHANNEL, type: 'open', file: current.file }, window.location.origin);
        } else if (message.type === 'ready') {
            current.ready = true;
            current.password = message.password || '';
            syncButtons();
            current.resolve(true);
        } else if (message.type === 'error') {
            current.ready = false;
            syncButtons();
            current.resolve(false);
            current.textRequest?.reject(new Error(message.message));
            current.textRequest = null;
        } else if (message.type === 'view') {
            current.view = message.view;
        } else if (['text', 'text-error'].includes(message.type) && current.textRequest?.id === message.requestId) {
            if (message.type === 'text') current.textRequest.resolve(message.text);
            else current.textRequest.reject(new Error(message.message));
            current.textRequest = null;
        }
    });
    window.TlamatiniPdfCanvas = {
        open, close, refresh, getText, prepareContext, syncButtons,
        get active() { return current !== null; },
        get file() { return current?.file || null; },
        get contextFilename() { return current?.prepared?.context_filename || null; },
    };
})();
