/* Tlamatini Author Banner — Angela López Mendoza */
/* Accessible native modal; all behavior lives outside the HTML template. */
(() => {
    'use strict';
    const dialog = document.getElementById('pdf-context-progress');
    const message = document.getElementById('pdf-context-progress-message');
    const action = document.getElementById('pdf-context-progress-action');
    const proceed = document.getElementById('pdf-context-continue');
    const processImages = document.getElementById('pdf-context-process-images');
    const elapsed = document.getElementById('pdf-context-progress-elapsed');
    const stages = ['upload', 'extract', 'analyze', 'rag'];
    let cancel = null;
    let timer = null;
    let started = 0;
    let expectedToken = null;
    let pendingChoice = null;
    let fileSize = 0;
    let failureReported = false;

    function tick() {
        const seconds = Math.floor((performance.now() - started) / 1000);
        elapsed.textContent = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
    }
    function stopTimer() { clearInterval(timer); timer = null; }
    function close() {
        if (pendingChoice) {
            pendingChoice.reject(new DOMException('Se canceló la preparación del contexto del PDF.', 'AbortError'));
            pendingChoice = null;
        }
        const callback = cancel;
        cancel = null;
        stopTimer();
        // Closing during RAG only hides the dialog; that work is still active.
        if (callback) setTitleBusy(false, 'pdf-context');
        dialog.close();
        callback?.();
    }
    function update(stage, completed, total, detail) {
        const position = stages.indexOf(stage);
        stages.forEach((name, index) => {
            const row = dialog.querySelector(`[data-pdf-stage="${name}"]`);
            const bar = row.querySelector('progress');
            const count = row.querySelector('output');
            if (name === 'analyze' && !processImages.checked) {
                row.dataset.state = 'skipped';
                bar.max = 1; bar.value = 0; count.textContent = 'Omitido';
                return;
            }
            row.dataset.state = index < position ? 'complete' : index === position ? 'active' : 'pending';
            if (index < position) { bar.max = 1; bar.value = 1; count.textContent = 'Listo'; }
            else if (index === position) {
                if (total > 0) {
                    bar.max = total; bar.value = completed;
                    count.textContent = stage === 'upload' ? `${Math.round(completed / total * 100)}%` : `${completed} / ${total}`;
                } else { bar.removeAttribute('value'); count.textContent = 'Procesando…'; }
            }
        });
        if (detail) message.textContent = detail;
    }
    function open(file, onCancel) {
        if (dialog.open) dialog.close();
        stopTimer();
        cancel = onCancel;
        expectedToken = null;
        failureReported = false;
        fileSize = file.size;
        processImages.checked = false;
        processImages.disabled = false;
        proceed.hidden = false;
        document.getElementById('pdf-context-progress-file').textContent = file.name;
        document.getElementById('pdf-context-progress-size').textContent = file.size < 1024 * 1024
            ? `${(file.size / 1024).toFixed(1)} KB` : `${(file.size / 1024 / 1024).toFixed(1)} MB`;
        stages.forEach(name => {
            const row = dialog.querySelector(`[data-pdf-stage="${name}"]`);
            row.dataset.state = 'pending';
            row.querySelector('progress').value = 0;
            row.querySelector('progress').max = 1;
            row.querySelector('output').textContent = 'Pendiente';
        });
        action.textContent = 'Cancelar';
        elapsed.textContent = '0:00';
        updateImageOption();
        const choice = new Promise((resolve, reject) => { pendingChoice = { resolve, reject }; });
        dialog.showModal();
        return choice;
    }
    function updateImageOption() {
        document.getElementById('pdf-context-extract-label').textContent = processImages.checked
            ? '2. Leer el texto y extraer las imágenes' : '2. Leer el texto del documento';
        const row = dialog.querySelector('[data-pdf-stage="analyze"]');
        row.dataset.state = processImages.checked ? 'pending' : 'skipped';
        row.querySelector('output').textContent = processImages.checked ? 'Pendiente' : 'Omitido';
        message.textContent = processImages.checked
            ? 'Todo listo para preparar el texto y analizar las imágenes. Presiona Continuar para empezar.'
            : 'Todo listo para preparar el texto seleccionable. Presiona Continuar para empezar.';
    }
    function loadingContext(token) {
        expectedToken = token;
        cancel = null;
        action.textContent = 'Cerrar';
        update('rag', 0, 0, (processImages.checked
            ? 'Terminó el procesamiento del PDF. Cargando su texto y los análisis de imágenes en el contexto de Tlamatini…'
            : 'Terminó la extracción del texto del PDF. Cargando su texto en el contexto de Tlamatini…'));
    }
    function finish(token, success) {
        if (token !== expectedToken) return;
        expectedToken = null;
        setTitleBusy(false, 'pdf-context');
        stopTimer();
        action.textContent = 'Cerrar';
        cancel = null;
        if (success) {
            update('rag', 1, 1, 'El contexto de tu PDF está listo. Ya puedes preguntarle a Tlamatini sobre el documento.');
            dialog.close();
        } else fail('El PDF se procesó, pero hubo un error al cargar el contexto. Vuelve a intentarlo y, si el problema sigue, revisa el servicio de modelos configurado.');
    }
    function fail(detail) {
        if (processImages.checked && !failureReported) {
            failureReported = true;
            // A native modal occupies the browser top layer. Release it so the
            // shared accumulating dialog is visible and the chat stays usable.
            cancel = null;
            if (dialog.open) dialog.close();
            window.SharedRuntimeDialogs.renderFatalError({ source_agent: 'PDF Image-Interpreter', message: detail });
        }
        if (pendingChoice) { pendingChoice.reject(new Error(detail)); pendingChoice = null; }
        // The step that was running did not finish: say so, instead of leaving
        // "Working…" and a moving bar on screen after the failure (2026-10-08).
        stages.forEach(name => {
            const row = dialog.querySelector(`[data-pdf-stage="${name}"]`);
            if (!row || row.dataset.state !== 'active') return;
            row.dataset.state = 'failed';
            const bar = row.querySelector('progress');
            bar.max = 1; bar.value = 0;
            row.querySelector('output').textContent = 'Error';
        });
        proceed.hidden = true;
        processImages.disabled = true;
        stopTimer(); cancel = null; action.textContent = 'Cerrar';
        expectedToken = null;
        setTitleBusy(false, 'pdf-context');
        message.textContent = detail;
    }
    function connectionLost() {
        if (expectedToken) fail('Se perdió la conexión en vivo mientras se cargaba el contexto. Vuelve a conectarte para revisar el status del contexto.');
    }
    action.addEventListener('click', close);
    processImages.addEventListener('change', updateImageOption);
    proceed.addEventListener('click', () => {
        if (!pendingChoice) return;
        const { resolve } = pendingChoice;
        pendingChoice = null;
        processImages.disabled = true;
        proceed.hidden = true;
        setTitleBusy(true, 'pdf-context');
        started = performance.now(); tick(); timer = setInterval(tick, 1000);
        update('upload', 0, fileSize, 'Subiendo el PDF a Tlamatini…');
        resolve(processImages.checked);
    });
    dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });
    // Also handle dismissal through the native close API or another UI control.
    // A queued close event from an earlier run must not cancel a newly opened one.
    dialog.addEventListener('close', () => { if (!dialog.open && cancel) close(); });
    window.TlamatiniPdfProgress = { open, update, loadingContext, finish, fail, connectionLost, cancelPreparation: close };
})();
