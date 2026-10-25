/* Tlamatini — "one who knows"
 * Created by Angela López Mendoza · @angelahack1
 * Tlamatini Author Banner — do not remove */
(() => {
    'use strict';
    const M = window.PromptFlowPanelModel, UI = window.FlowCanvasInteractions;
    const $id = id => document.getElementById(id);
    const viewport = $id('submonitor-container'), content = $id('canvas-content'), world = $id('pmt-world');
    const layer = $id('connections-layer'), nodesLayer = $id('pmt-nodes');
    // Preserve saved drafts across the panel rename.
    const storeKey = `tlamatini.prompting-flow.draft.v1.${document.body.dataset.userId}`;
    let flow = M.blank(), filename = 'Untitled.fpmt', clean = JSON.stringify(flow);
    let selected = new Set(), selectedEdge = null;
    const selectedEdges = new Set();
    let zoom = 1, undo = [], redo = [], gesture = null, dirty = false;
    let commentEditor = null;
    let socket = null, connecting = null, runId = null, runState = 'idle', activeNode = null;
    let inputDialog = null, internalClose = false, draftTimer = null, socketReady = false;
    const nodeStates = new Map(), traversed = new Set();
    const commentarySizes = new WeakMap();
    const nodeSize = node => commentarySizes.get(node) || M.size(node);
    const playbackActive = () => ['starting', 'running', 'paused', 'stopping'].includes(runState);
    const editable = () => !commentEditor && !playbackActive();
    const status = message => { $id('pmt-status').textContent = message; };
    const alertMessage = (message, title = 'Prompt Flow Panel') => window.tlmAlert(String(message), title);
    const confirm = (message, detail = '') => window.tlmConfirm(message, detail, 'Prompt Flow Panel');
    const svgNS = 'http://www.w3.org/2000/svg';
    function element(tag, className, text) {
        const el = document.createElement(tag);
        if (className) el.className = className;
        if (text !== undefined) el.textContent = text;
        return el;
    }
    function svg(tag, attrs = {}) {
        const el = document.createElementNS(svgNS, tag);
        for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
        return el;
    }
    function shape(type) {
        const info = M.operations[type], graphic = svg('svg', { viewBox: '0 0 200 128', 'aria-hidden': 'true' });
        graphic.style.setProperty('--pmt-color', info.color); graphic.style.setProperty('--pmt-fill', info.fill);
        graphic.append(svg('path', { d: info.path, class: 'pmt-shape' }));
        if (type === 'terminater') graphic.append(svg('path', { d: 'M66 36L80 47L66 58M88 60H108', fill: 'none', stroke: '#8ff5bd', 'stroke-width': 3.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', class: 'pmt-term-glyph' }));
        if (type === 'programmed_prompt') {
            graphic.append(svg('circle', { cx: 174, cy: 40, r: 20, class: 'pmt-clock' }), svg('path', { d: 'M174 25V40L185 46', fill: 'none', stroke: '#f3df9f', 'stroke-width': 2 }));
            for (let angle = 0; angle < 360; angle += 30) {
                const rad = angle * Math.PI / 180;
                graphic.append(svg('circle', { cx: 174 + Math.sin(rad) * 16, cy: 40 + Math.cos(rad) * 16, r: 1, fill: '#f3df9f' }));
            }
        }
        return graphic;
    }
    function snapshot() { return JSON.stringify(flow); }
    function persist() {
        clearTimeout(draftTimer);
        draftTimer = setTimeout(() => {
            try { localStorage.setItem(storeKey, JSON.stringify({ flow: commentEditor ? JSON.parse(commentEditor.before) : flow, filename, zoom })); }
            catch (error) { status(`No se pudo guardar el borrador en este browser. Guarda un archivo .fpmt: ${error.message}`); }
        }, 250);
    }
    function changed(before) {
        if (before !== snapshot()) {
            undo.push(before); if (undo.length > 100) undo.shift(); redo = [];
            nodeStates.clear(); traversed.clear(); dirty = snapshot() !== clean; persist();
        }
        render();
    }
    function mutate(fn) {
        if (!editable()) return;
        cancelConnection();
        const before = snapshot(); fn(); changed(before);
    }
    function resetSelection() { selected.clear(); selectedEdges.clear(); selectedEdge = null; }
    function position(event) {
        const rect = world.getBoundingClientRect();
        return { x: (event.clientX - rect.left) / zoom, y: (event.clientY - rect.top) / zoom };
    }
    const snap = value => Math.min(100000, Math.max(0, value));
    function extent() {
        const width = Math.max(1000, viewport.clientWidth / zoom, ...flow.nodes.map(n => n.x + nodeSize(n).width + 150));
        const height = Math.max(700, viewport.clientHeight / zoom, ...flow.nodes.map(n => n.y + nodeSize(n).height + 150));
        world.style.width = `${width}px`; world.style.height = `${height}px`;
        world.style.transform = `scale(${zoom})`;
        content.style.width = `${width * zoom}px`; content.style.height = `${height * zoom}px`;
        $id('pmt-zoom').textContent = `${Math.round(zoom * 100)}%`;
        updateButtons();
    }
    function anchor(node, port) {
        const info = M.operations[node.type], point = info[port === 'next' ? 'output' : port];
        // ACP wires join the centers of its 10 x 16 CSS triangles.
        return [node.x + point[0] + (port === 'input' ? -5 : 5), node.y + point[1]];
    }
    const connectionPath = UI.connectionPath;
    function selectEdge(event, edge) {
        if (event.button !== 0) return;
        event.preventDefault(); event.stopPropagation(); cancelConnection();
        if (!UI.modified(event)) resetSelection();
        if (UI.modified(event) && selectedEdges.has(edge.id)) selectedEdges.delete(edge.id); else selectedEdges.add(edge.id);
        selectedEdge = selectedEdges.size === 1 ? [...selectedEdges][0] : null;
        paintSelection();
    }
    function paintSelection() {
        nodesLayer.querySelectorAll('.pmt-node').forEach(n => n.classList.toggle('selected', selected.has(n.dataset.nodeId)));
        layer.querySelectorAll('.pmt-edge').forEach(e => e.classList.toggle('selected', selectedEdges.has(e.dataset.edgeId)));
        updateButtons();
    }
    function configureSelectedNode(node, event) {
        event?.preventDefault();
        if (editable()) { resetSelection(); selected.add(node.id); render(); if (M.isComment(node)) editCommentary(node); else configureNode(node); }
    }
    function showNodeMenu(node, event) {
        event.preventDefault(); event.stopPropagation(); endGesture();
        if (!selected.has(node.id)) { resetSelection(); selected.add(node.id); paintSelection(); }
        const menu = $id('agent-context-menu');
        menu.replaceChildren();
        for (const [icon, label, command] of [[M.isComment(node) ? '✎' : '⚙️', M.isComment(node) ? 'Editar comentario' : 'Configurar', () => configureNode(node)], ['ℹ️', 'Descripción', () => alertMessage(M.operations[node.type].help, node.label)], ['▣', 'Duplicar', duplicate], ['⌫', 'Eliminar', deleteSelection]]) {
            const item = element('div', 'context-menu-item');
            const disabled = label !== 'Descripción' && !editable();
            item.classList.toggle('context-menu-item-disabled', disabled);
            item.append(element('span', 'context-menu-icon', icon), element('span', '', label));
            item.addEventListener('click', () => { menu.style.display = 'none'; if (!disabled) command(); });
            menu.append(item);
        }
        UI.showMenu(menu, event.clientX, event.clientY);
    }
    document.addEventListener('click', event => { if (!event.target.closest('#agent-context-menu')) $id('agent-context-menu').style.display = 'none'; });
    document.addEventListener('keydown', event => { if (event.key === 'Escape') $id('agent-context-menu').style.display = 'none'; });
    viewport.addEventListener('scroll', () => { $id('agent-context-menu').style.display = 'none'; positionCommentTools(); });
    function nodeKey(event, node) {
        if (event.target.closest('.pmt-port, .pmt-comment-handle, button, textarea')) return;
        if (event.key === 'Enter') configureSelectedNode(node, event);
    }
    function renderEdges() {
        layer.replaceChildren();
        const byId = new Map(flow.nodes.map(n => [n.id, n]));
        for (const edge of flow.edges) {
            const source = byId.get(edge.source), target = byId.get(edge.target);
            const [sx, sy] = anchor(source, edge.branch), [tx, ty] = anchor(target, 'input');
            const d = connectionPath(sx, sy, tx, ty);
            const group = svg('g', { class: `pmt-edge connection-group${selectedEdges.has(edge.id) ? ' selected' : ''}${traversed.has(edge.id) ? ' traversed' : ''}`, 'data-edge-id': edge.id });
            group.append(svg('path', { d, class: 'pmt-wire connection-path' }), svg('path', { d, class: 'pmt-wire-hit connection-hit-area' }));
            group.addEventListener('pointerdown', event => selectEdge(event, edge));
            group.addEventListener('dblclick', () => configureEdge(edge));
            layer.append(group);
        }
        if (connection.active) layer.append(connection.active.data.preview);
    }
    // Notes are edited on the canvas. Their controls never cover the text.
    let commentToolbar = null, commentToolbarKey = '';
    function commentElement(node) { return [...nodesLayer.children].find(el => el.dataset.nodeId === node.id); }
    function commentTypography(text, config) {
        Object.assign(text.style, { fontFamily: config.font_family, fontSize: `${config.font_size}px`, fontWeight: config.bold ? '700' : '400', fontStyle: config.italic ? 'italic' : 'normal', textAlign: config.align || '', color: config.text_color || '#202938', textDecoration: config.underline ? 'underline' : 'none' });
    }
    function paintCommentText(text, config, editing = false) {
        text.replaceChildren();
        M.commentRuns(config).forEach((run, index) => {
            const span = element('span', '', run.text); span.dataset.commentRun = index;
            commentTypography(span, run); text.append(span);
        });
        if (editing && (!config.text || config.text.endsWith('\n'))) text.append(document.createElement('br'));
        if (!editing && !config.text) text.textContent = 'Escribe una nota…';
    }
    function commentSelection() {
        const editor = commentEditor, selection = window.getSelection();
        if (!editor || !selection.rangeCount) return editor?.selection;
        const range = selection.getRangeAt(0);
        if (!editor.input.contains(range.startContainer) || !editor.input.contains(range.endContainer)) return editor.selection;
        const offset = (container, end) => {
            const prefix = document.createRange(); prefix.selectNodeContents(editor.input); prefix.setEnd(container, end); return prefix.toString().length;
        };
        const next = { start: offset(range.startContainer, range.startOffset), end: offset(range.endContainer, range.endOffset) };
        if (next.start !== editor.selection.start || next.end !== editor.selection.end) editor.typingStyle = null;
        editor.selection = next;
        return next;
    }
    function restoreCommentSelection() {
        const editor = commentEditor;
        if (!editor) return;
        const point = offset => {
            const walker = document.createTreeWalker(editor.input, NodeFilter.SHOW_TEXT);
            let text, last;
            while ((text = walker.nextNode())) {
                last = text;
                if (offset <= text.length) return [text, offset];
                offset -= text.length;
            }
            return last ? [last, last.length] : [editor.input, 0];
        };
        const range = document.createRange();
        range.setStart(...point(editor.selection.start)); range.setEnd(...point(editor.selection.end));
        const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
    }
    function selectedCommentStyle() {
        const c = currentComment()?.config;
        if (!c) return {};
        const editor = commentEditor;
        if (editor?.typingStyle && editor.selection.start === editor.selection.end) return editor.typingStyle;
        const { start, end } = editor?.selection || { start: 0, end: c.text.length };
        const runs = M.sliceCommentRuns(M.commentRuns(c), start === end ? Math.max(0, start - 1) : start, start === end ? Math.max(1, end) : end);
        if (!runs.length) return M.commentStyle(c);
        return Object.fromEntries(M.commentStyleKeys.map(key => [key, runs.every(run => run[key] === runs[0][key]) ? runs[0][key] : null]));
    }
    function editorState() {
        return { x: commentEditor.node.x, y: commentEditor.node.y, config: M.copy(commentEditor.node.config), selection: { ...commentEditor.selection }, typingStyle: commentEditor.typingStyle && { ...commentEditor.typingStyle } };
    }
    function rememberCommentEdit() {
        const editor = commentEditor; editor.undo.push(editorState());
        if (editor.undo.length > 100) editor.undo.shift();
        editor.redo = [];
    }
    function replayCommentEdit(backwards) {
        const editor = commentEditor, source = backwards ? editor.undo : editor.redo, target = backwards ? editor.redo : editor.undo;
        if (!source.length) return;
        target.push(editorState()); const saved = source.pop();
        editor.node.config = saved.config; editor.node.x = saved.x; editor.node.y = saved.y; editor.selection = saved.selection; editor.typingStyle = saved.typingStyle;
        repaintCommentEditor();
    }
    function repaintCommentEditor() {
        const editor = commentEditor;
        paintCommentText(editor.input, editor.node.config, true);
        editor.renderedRuns = M.copy(M.commentRuns(editor.node.config));
        refreshComment(editor.node); restoreCommentSelection(); syncCommentTools();
    }
    function formatCommentText(patch) {
        const node = currentComment(); if (!node || playbackActive()) return;
        const c = node.config, editor = commentEditor;
        if (editor) commentSelection();
        const { start, end } = editor?.selection || { start: 0, end: c.text.length };
        const apply = () => {
            if (start === end && editor) {
                editor.typingStyle = { ...selectedCommentStyle(), ...patch };
                if (!c.text) Object.assign(c, patch);
            } else {
                const replacement = M.sliceCommentRuns(M.commentRuns(c), start, end).map(run => ({ ...run, ...patch }));
                const candidate = M.copy(c); M.replaceCommentRange(candidate, start, end, replacement);
                if (candidate.runs.length > 10000) { status('Este comentario llegó a su límite de formato.'); return; }
                c.runs = candidate.runs; c.text = candidate.text;
                if (start === 0 && end === c.text.length) Object.assign(c, patch);
                if (editor) editor.typingStyle = null;
            }
        };
        if (editor) { rememberCommentEdit(); apply(); repaintCommentEditor(); editor.input.focus({ preventScroll: true }); restoreCommentSelection(); }
        else mutate(() => { apply(); if (!c.text) Object.assign(c, patch); });
    }
    function insertCommentText(text, range = commentSelection(), formatted = null) {
        const editor = commentEditor, c = editor.node.config;
        text = text.replace(/\r\n?/g, '\n');
        if (c.text.length - (range.end - range.start) + text.length > 100000) { status('Un comentario puede tener hasta 100,000 caracteres.'); return; }
        const style = editor.typingStyle || M.commentStyle(M.sliceCommentRuns(M.commentRuns(c), range.start, range.start + 1)[0] || c);
        const candidate = M.copy(c);
        M.replaceCommentRange(candidate, range.start, range.end, formatted || (text ? [{ text, ...style }] : []));
        if (candidate.runs.length > 10000) { status('Este comentario llegó a su límite de formato.'); return; }
        rememberCommentEdit(); c.text = candidate.text; c.runs = candidate.runs;
        editor.selection = { start: range.start + text.length, end: range.start + text.length };
        editor.typingStyle = style;
        repaintCommentEditor();
    }
    function commentBeforeInput(event) {
        const editor = commentEditor;
        if (editor.composing || event.isComposing) return;
        commentSelection();
        const type = event.inputType;
        if (type === 'historyUndo' || type === 'historyRedo') { event.preventDefault(); replayCommentEdit(type === 'historyUndo'); return; }
        if (['formatBold', 'formatItalic', 'formatUnderline'].includes(type)) {
            event.preventDefault(); const key = type.slice(6).toLowerCase(); formatCommentText({ [key]: !selectedCommentStyle()[key] }); return;
        }
        if (['insertText', 'insertParagraph', 'insertLineBreak'].includes(type)) {
            event.preventDefault(); insertCommentText(type === 'insertParagraph' || type === 'insertLineBreak' ? '\n' : event.data || ''); return;
        }
        if (type.startsWith('delete')) {
            event.preventDefault(); let { start, end } = editor.selection;
            const targets = event.getTargetRanges?.();
            if (targets?.length) {
                const range = targets[0], prefix = document.createRange(); prefix.selectNodeContents(editor.input);
                prefix.setEnd(range.startContainer, range.startOffset); start = prefix.toString().length;
                prefix.setEnd(range.endContainer, range.endOffset); end = prefix.toString().length;
            } else if (start === end) {
                const boundaries = [...new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(editor.node.config.text)].map(part => part.index);
                boundaries.push(editor.node.config.text.length);
                if (type.includes('Backward')) start = boundaries.filter(index => index < start).pop() ?? 0;
                else end = boundaries.find(index => index > end) ?? end;
            }
            if (start !== end) insertCommentText('', { start, end });
        }
    }
    function readNativeCommentEdit() {
        const editor = commentEditor;
        if (!editor || editor.composing) return;
        commentSelection();
        const runs = [], walker = document.createTreeWalker(editor.input, NodeFilter.SHOW_TEXT);
        let text;
        while ((text = walker.nextNode())) {
            const index = text.parentElement.closest('[data-comment-run]')?.dataset.commentRun;
            runs.push({ text: text.data, ...M.commentStyle(editor.renderedRuns[index] || editor.node.config) });
        }
        const value = runs.map(run => run.text).join('');
        if (value.length > 100000) { repaintCommentEditor(); status('Un comentario puede tener hasta 100,000 caracteres.'); return; }
        rememberCommentEdit(); editor.node.config.text = value; editor.node.config.runs = M.mergeCommentRuns(runs);
        repaintCommentEditor();
    }
    document.addEventListener('selectionchange', () => {
        if (!commentEditor || commentEditor.composing) return;
        commentSelection(); syncCommentTools();
    });
    function fitCommentary(el, node, text) {
        // Measure in document coordinates, so changing zoom never changes wrapping.
        el.style.width = `${node.config.width}px`;
        commentTypography(text, node.config); text.style.textDecoration = 'none';
        text.style.height = '0px';
        const textHeight = Math.ceil(text.scrollHeight);
        const height = Math.max(node.config.height, textHeight + 82);
        text.style.height = `${height - 82}px`;
        commentarySizes.set(node, { width: node.config.width, height });
        el.style.height = `${height}px`;
        el.style.setProperty('--comment-color', node.config.color);
        const width = node.config.width, bottom = height - 18, graphic = el.querySelector('svg');
        graphic.setAttribute('viewBox', `0 0 ${width} ${height}`);
        graphic.style.setProperty('--pmt-fill', node.config.color);
        // Constant corner radius and tail: the drawing does not stretch with the text.
        graphic.querySelector('path').setAttribute('d', `M20 1H${width - 20}Q${width - 1} 1 ${width - 1} 20V${bottom - 19}Q${width - 1} ${bottom} ${width - 20} ${bottom}H72L53 ${height - 1}L35 ${bottom}H20Q1 ${bottom} 1 ${bottom - 19}V20Q1 1 20 1Z`);
    }
    function refreshComment(node) {
        const el = commentElement(node);
        if (!el) return;
        fitCommentary(el, node, el.querySelector('.pmt-comment-text'));
        el.style.left = `${node.x}px`; el.style.top = `${node.y}px`;
        extent();
    }
    function changeComment(node, patch) {
        if (playbackActive()) return;
        if (commentEditor?.node === node) {
            rememberCommentEdit(); Object.assign(node.config, patch); refreshComment(node); syncCommentTools();
        } else mutate(() => Object.assign(node.config, patch));
    }
    function fitCommentText(node) {
        changeComment(node, { height: 128 });
        status('El comentario se ajustó a su texto. Arrastra cualquier borde o esquina para cambiar su forma.');
    }
    function resizeComment(drag, dx, dy) {
        const { node, direction, x, y, width, height, minimum } = drag;
        const east = direction.includes('e'), west = direction.includes('w');
        const north = direction.includes('n'), south = direction.includes('s');
        if (east || west) {
            node.config.width = Math.max(200, Math.min(2400, width + (west ? -dx : dx), west ? x + width : 2400));
            node.x = west ? x + width - node.config.width : x;
        }
        node.config.height = north || south ? Math.max(128, Math.min(2400, height + (north ? -dy : dy), north ? y + height : 2400)) : minimum;
        refreshComment(node);
        if (north) { node.y = Math.max(0, y + height - nodeSize(node).height); refreshComment(node); }
    }
    function beginCommentResize(event, node, direction) {
        event.preventDefault(); event.stopPropagation();
        if (event.button !== 0 || playbackActive() || (commentEditor && commentEditor.node !== node)) return;
        endGesture();
        if (commentEditor) rememberCommentEdit();
        selected = new Set([node.id]); selectedEdges.clear(); selectedEdge = null;
        gesture = { kind: 'resize', node, direction, before: snapshot(), x: node.x, y: node.y,
            ...nodeSize(node), minimum: node.config.height, fromX: event.clientX, fromY: event.clientY, scale: zoom, pointerId: event.pointerId };
        viewport.setPointerCapture(event.pointerId);
        document.body.style.cursor = `${direction}-resize`;
        commentElement(node).classList.add('comment-resizing'); paintSelection();
    }
    function renderCommentary(el, node) {
        const heading = element('div', 'pmt-comment-heading');
        heading.append(element('span', 'pmt-comment-kicker', node.label === 'User Commentary' ? 'Comentario' : node.label));
        const edit = element('button', 'pmt-comment-edit', 'Editar');
        edit.type = 'button'; edit.title = 'Editar comentario'; edit.setAttribute('aria-label', 'Editar comentario'); edit.disabled = playbackActive();
        edit.addEventListener('click', event => { event.stopPropagation(); editCommentary(node); });
        edit.addEventListener('dblclick', event => event.stopPropagation()); heading.append(edit); el.append(heading);
        const text = element('div', 'pmt-comment-text'); paintCommentText(text, node.config);
        text.classList.toggle('pmt-comment-empty', !node.config.text); el.append(text); fitCommentary(el, node, text);
        const directions = { n: 'el borde superior', e: 'el borde derecho', s: 'el borde inferior', w: 'el borde izquierdo', nw: 'la esquina superior izquierda', ne: 'la esquina superior derecha', sw: 'la esquina inferior izquierda', se: 'la esquina inferior derecha' };
        for (const [direction, label] of Object.entries(directions)) {
            const handle = element('button', `pmt-comment-handle handle-${direction}`);
            handle.type = 'button'; handle.dataset.resize = direction; handle.disabled = playbackActive();
            handle.title = `Cambiar el tamaño del comentario desde ${label}`; handle.setAttribute('aria-label', handle.title);
            handle.addEventListener('pointerdown', event => beginCommentResize(event, node, direction));
            handle.addEventListener('dblclick', event => { event.preventDefault(); event.stopPropagation(); fitCommentText(node); });
            handle.addEventListener('keydown', event => resizeCommentKey(event, node, direction));
            el.append(handle);
        }
    }
    function resizeCommentKey(event, node, direction) {
        if (!event.key.startsWith('Arrow') || playbackActive()) return;
        event.preventDefault(); event.stopPropagation();
        const before = snapshot(), amount = event.shiftKey ? 40 : 10;
        if (commentEditor) rememberCommentEdit();
        resizeComment({ node, direction, x: node.x, y: node.y, ...nodeSize(node), minimum: node.config.height },
            event.key === 'ArrowRight' ? amount : event.key === 'ArrowLeft' ? -amount : 0,
            event.key === 'ArrowDown' ? amount : event.key === 'ArrowUp' ? -amount : 0);
        if (!commentEditor) { changed(before); commentElement(node)?.querySelector(`[data-resize="${direction}"]`)?.focus({ preventScroll: true }); }
    }
    function finishCommentary(save) {
        if (!commentEditor) return;
        if (gesture?.kind === 'resize') endGesture();
        const { node, before } = commentEditor;
        commentEditor = null;
        if (save) { changed(before); }
        else { flow = JSON.parse(before); persist(); render(); }
        commentElement(node)?.focus({ preventScroll: true });
        status(save ? 'Comentario guardado.' : 'Se descartaron los cambios del comentario.');
    }
    function editCommentary(node) {
        if (commentEditor?.node === node) { commentEditor.input.focus({ preventScroll: true }); return; }
        if (!editable()) return;
        endGesture(); resetSelection(); selected.add(node.id);
        const el = commentElement(node), display = el.querySelector('.pmt-comment-text');
        const input = element('div', 'pmt-comment-text pmt-comment-editor');
        input.contentEditable = 'true'; input.spellcheck = true; input.setAttribute('role', 'textbox'); input.setAttribute('aria-multiline', 'true');
        input.setAttribute('aria-label', 'Texto del comentario estático');
        commentEditor = { node, input, before: snapshot(), selection: { start: 0, end: 0 }, typingStyle: null, undo: [], redo: [], composing: false, renderedRuns: M.copy(M.commentRuns(node.config)) };
        paintCommentText(input, node.config, true);
        display.replaceWith(input); el.classList.add('editing');
        input.addEventListener('pointerdown', event => event.stopPropagation());
        input.addEventListener('dblclick', event => event.stopPropagation());
        input.addEventListener('beforeinput', commentBeforeInput);
        input.addEventListener('input', readNativeCommentEdit);
        input.addEventListener('compositionstart', () => { commentEditor.composing = true; });
        input.addEventListener('compositionend', () => { commentEditor.composing = false; readNativeCommentEdit(); });
        const clipboardType = 'application/x-tlamatini-comment-runs+json';
        const copySelection = event => {
            const range = commentSelection();
            if (range.start === range.end) return;
            event.preventDefault();
            const runs = M.sliceCommentRuns(M.commentRuns(node.config), range.start, range.end);
            event.clipboardData.setData('text/plain', runs.map(run => run.text).join(''));
            event.clipboardData.setData(clipboardType, JSON.stringify(runs));
            if (event.type === 'cut') insertCommentText('', range);
        };
        input.addEventListener('copy', copySelection); input.addEventListener('cut', copySelection);
        input.addEventListener('paste', event => {
            event.preventDefault();
            const text = event.clipboardData.getData('text/plain');
            let runs = null;
            try {
                const encoded = event.clipboardData.getData(clipboardType);
                if (encoded && encoded.length <= 5 * 1024 * 1024) {
                    const note = M.copy(node); note.config.text = text; note.config.runs = JSON.parse(encoded);
                    runs = M.validate({ ...M.blank(), nodes: [note] }).nodes[0].config.runs;
                }
            } catch { /* Unrecognized clipboard formatting falls back to literal text. */ }
            insertCommentText(text, commentSelection(), runs);
        });
        input.addEventListener('drop', event => { event.preventDefault(); });
        input.addEventListener('keydown', event => {
            event.stopPropagation();
            if (event.isComposing) return;
            const control = event.ctrlKey || event.metaKey, key = event.key.toLowerCase();
            if (event.key === 'Escape') { event.preventDefault(); if (gesture) endGesture(); else finishCommentary(false); }
            else if (control && event.key === 'Enter') { event.preventDefault(); finishCommentary(true); }
            else if (control && ['b', 'i', 'u'].includes(key)) { event.preventDefault(); const property = { b: 'bold', i: 'italic', u: 'underline' }[key]; formatCommentText({ [property]: !selectedCommentStyle()[property] }); }
            else if (control && (key === 'z' || key === 'y')) { event.preventDefault(); replayCommentEdit(key === 'z' && !event.shiftKey); }
        });
        refreshComment(node); paintSelection(); input.focus({ preventScroll: true });
        status('Escribe directamente en la nota. Arrastra sus bordes para cambiar el tamaño; Listo guarda y Esc cancela.');
    }
    function syncCommentTools() {
        const node = selected.size === 1 && !selectedEdges.size ? flow.nodes.find(n => selected.has(n.id) && M.isComment(n)) : null;
        if (!commentToolbar) {
            commentToolbar = element('div', 'pmt-comment-toolbar'); commentToolbar.id = 'pmt-comment-toolbar';
            commentToolbar.setAttribute('role', 'region'); commentToolbar.setAttribute('aria-label', 'Formato del comentario');
            document.body.append(commentToolbar);
            commentToolbar.addEventListener('pointerdown', event => {
                if (!commentEditor) return;
                commentSelection();
                if (event.target.closest('button')) event.preventDefault();
            });
            commentToolbar.addEventListener('keydown', event => {
                event.stopPropagation();
                if (event.key === 'Escape' && commentEditor) { event.preventDefault(); finishCommentary(false); }
                else if ((event.ctrlKey || event.metaKey) && event.key === 'Enter' && commentEditor) { event.preventDefault(); finishCommentary(true); }
            });
        }
        const visible = !!node && !playbackActive();
        commentToolbar.hidden = !visible;
        if (!visible) { commentToolbarKey = ''; return; }
        const key = `${node.id}:${!!commentEditor}`;
        if (commentToolbarKey !== key) {
            commentToolbarKey = key; commentToolbar.replaceChildren();
            const title = element('span', 'pmt-comment-tools-title', commentEditor ? 'Selecciona texto para darle formato' : 'Comentario');
            commentToolbar.append(title);
            const colors = element('div', 'pmt-comment-swatches'); colors.setAttribute('role', 'group'); colors.setAttribute('aria-label', 'Color del comentario');
            for (const [value, name] of M.commentColors) {
                const button = element('button', 'pmt-comment-swatch'); button.type = 'button'; button.dataset.color = value;
                button.style.setProperty('--swatch', value); button.title = name; button.setAttribute('aria-label', `Comentario ${name}`);
                button.addEventListener('click', () => changeComment(currentComment(), { color: value })); colors.append(button);
            }
            commentToolbar.append(colors);
            const typography = element('div', 'pmt-comment-tool-group');
            const font = element('select', 'pmt-comment-font'); font.setAttribute('aria-label', 'Fuente del comentario');
            for (const family of M.commentFonts) { const option = new Option(family, family); option.style.fontFamily = family; font.append(option); }
            font.prepend(new Option('Fuentes mixtas', '')); font.options[0].disabled = true;
            font.addEventListener('change', () => formatCommentText({ font_family: font.value }));
            const size = element('select', 'pmt-comment-size'); size.setAttribute('aria-label', 'Tamaño del texto del comentario');
            for (const [value, label] of [[10, 'Muy pequeño'], [12, 'Pequeño'], [16, 'Normal'], [20, 'Grande'], [28, 'Encabezado'], [36, 'Título'], [48, 'Muy grande']]) size.append(new Option(label, value));
            size.prepend(new Option('Tamaños mixtos', '')); size.options[0].disabled = true;
            size.addEventListener('change', () => formatCommentText({ font_size: Number(size.value) }));
            typography.append(font, size);
            const ink = element('details', 'pmt-comment-ink');
            const inkToggle = element('summary', '', 'A'); inkToggle.title = 'Color del texto'; inkToggle.setAttribute('aria-label', 'Color del texto');
            const inkColors = element('div', 'pmt-comment-ink-colors'); inkColors.setAttribute('role', 'group'); inkColors.setAttribute('aria-label', 'Paleta de colores del texto');
            for (const [value, name] of M.commentTextColors) {
                const button = element('button', 'pmt-comment-swatch'); button.type = 'button'; button.dataset.textColor = value; button.style.setProperty('--swatch', value);
                button.title = name; button.setAttribute('aria-label', `Texto ${name}`);
                button.addEventListener('click', () => { formatCommentText({ text_color: value }); ink.open = false; }); inkColors.append(button);
            }
            ink.append(inkToggle, inkColors); typography.append(ink);
            for (const [property, label, glyph] of [['bold', 'Negrita', 'B'], ['italic', 'Cursiva', 'I'], ['underline', 'Subrayado', 'U']]) {
                const button = toolButton(glyph, label, () => formatCommentText({ [property]: !selectedCommentStyle()[property] }));
                button.dataset.emphasis = property; typography.append(button);
            }
            commentToolbar.append(typography);
            const alignment = element('div', 'pmt-comment-tool-group'); alignment.setAttribute('role', 'group'); alignment.setAttribute('aria-label', 'Alineación del comentario');
            for (const value of ['left', 'center', 'right']) {
                const button = toolButton('', `Alinear: ${value}`, () => changeComment(currentComment(), { align: value }));
                button.dataset.align = value;
                const icon = svg('svg', { viewBox: '0 0 20 20', 'aria-hidden': 'true' });
                const short = value === 'left' ? 3 : value === 'right' ? 8 : 5.5;
                icon.append(svg('path', { d: `M3 4H17M${short} 8h9M3 12H17M${short} 16h9`, fill: 'none', stroke: 'currentColor', 'stroke-width': 1.7, 'stroke-linecap': 'round' }));
                button.append(icon); alignment.append(button);
            }
            commentToolbar.append(alignment, toolButton('Ajustar al texto', 'Ajusta la burbuja al texto', () => fitCommentText(currentComment())));
            const actions = element('div', 'pmt-comment-actions');
            if (commentEditor) {
                actions.append(toolButton('Cancelar', 'Cancela los cambios del comentario', () => finishCommentary(false)), toolButton('Listo', 'Listo', () => finishCommentary(true), 'primary'));
            } else actions.append(toolButton('Editar texto', 'Edita el texto del comentario', () => editCommentary(currentComment()), 'primary'));
            commentToolbar.append(actions);
        }
        const c = { ...node.config, ...selectedCommentStyle() };
        for (const button of commentToolbar.querySelectorAll('[data-text-color]')) button.setAttribute('aria-pressed', String(button.dataset.textColor === (c.text_color || '#202938')));
        commentToolbar.querySelector('.pmt-comment-ink summary').style.textDecorationColor = c.text_color || '#202938';
        for (const button of commentToolbar.querySelectorAll('[data-color]')) button.setAttribute('aria-pressed', String(button.dataset.color === c.color));
        commentToolbar.querySelector('.pmt-comment-font').value = c.font_family || '';
        const size = commentToolbar.querySelector('.pmt-comment-size');
        size.querySelector('[data-saved-size]')?.remove();
        if (c.font_size !== null && ![...size.options].some(option => Number(option.value) === c.font_size)) {
            const option = new Option('Tamaño guardado', c.font_size); option.dataset.savedSize = ''; size.append(option);
        }
        size.value = c.font_size ?? '';
        for (const button of commentToolbar.querySelectorAll('[data-emphasis]')) button.setAttribute('aria-pressed', c[button.dataset.emphasis] === null ? 'mixed' : String(c[button.dataset.emphasis]));
        for (const button of commentToolbar.querySelectorAll('[data-align]')) button.setAttribute('aria-pressed', String(button.dataset.align === c.align));
        positionCommentTools();
    }
    function positionCommentTools() {
        if (!commentToolbar || commentToolbar.hidden) return;
        const node = currentComment(), el = node && commentElement(node);
        if (!el) return;
        const box = el.getBoundingClientRect(), view = viewport.getBoundingClientRect();
        const margin = 12, width = Math.min(420, view.width - margin * 2);
        commentToolbar.style.width = Math.max(260, width) + 'px';
        const height = commentToolbar.offsetHeight;
        const lowX = Math.max(margin, view.left + margin), highX = Math.min(window.innerWidth - margin, view.right - margin) - commentToolbar.offsetWidth;
        const lowY = Math.max(margin, view.top + margin), highY = Math.min(window.innerHeight - margin, view.bottom - margin) - height;
        let left = box.left, top = box.top - height - margin;
        if (top < lowY) {
            if (box.right + margin <= highX) { left = box.right + margin; top = box.top; }
            else if (box.left - margin - commentToolbar.offsetWidth >= lowX) { left = box.left - margin - commentToolbar.offsetWidth; top = box.top; }
            else top = box.bottom + margin;
        }
        commentToolbar.style.left = Math.max(lowX, Math.min(highX, left)) + 'px';
        commentToolbar.style.top = Math.max(lowY, Math.min(highY, top)) + 'px';
    }
    function currentComment() { return flow.nodes.find(n => selected.has(n.id) && M.isComment(n)); }
    function toolButton(text, label, action, extra = '') {
        const button = element('button', `pmt-comment-tool ${extra}`, text); button.type = 'button';
        button.title = label; button.setAttribute('aria-label', label); button.addEventListener('click', action); return button;
    }

    function addPort(el, node, name, point) {
        const direction = name === 'input' ? 'input' : 'output';
        const slot = name === 'yes' ? ' output-1' : name === 'no' ? ' output-2' : '';
        const button = element('button', `pmt-port ${direction} ${direction}-triangle${slot}`);
        button.type = 'button'; button.style.left = `${point[0]}px`; button.style.top = `${point[1]}px`;
        button.dataset.port = name;
        button.title = `${node.label}: ${name === 'next' ? 'output' : name}`;
        button.setAttribute('aria-label', button.title); button.disabled = !editable();
        button.addEventListener('pointerdown', event => {
            event.stopPropagation();
            if (event.button !== 0 || !editable()) return;
            event.preventDefault();
            if (name !== 'input') startConnection(node, name, button, event.pointerId);
        });
        // Keyboard users can activate an output, Tab to an input, then activate it.
        button.addEventListener('click', event => {
            event.stopPropagation();
            if (event.detail !== 0 || !editable()) return;
            if (name !== 'input') startConnection(node, name, button);
            else if (connection.active?.pointerId === undefined) connection.finish(button);
        });
        button.addEventListener('dblclick', event => event.stopPropagation());
        el.append(button);
        if (name === 'yes' || name === 'no') {
            const label = element('span', 'pmt-port-label output-label', name === 'yes' ? 'Y' : 'N');
            label.style.right = `${200 - point[0] + 6}px`; label.style.top = `${point[1]}px`; el.append(label);
        }
    }
    function render() {
        cancelConnection();
        nodesLayer.replaceChildren();
        for (const node of flow.nodes) {
            const info = M.operations[node.type], state = nodeStates.get(node.id) || '';
            const el = element('div', `pmt-node${selected.has(node.id) ? ' selected' : ''} ${state}`);
            el.dataset.nodeId = node.id; el.dataset.type = node.type; el.tabIndex = 0;
            el.setAttribute('role', 'group'); el.setAttribute('aria-label', `${node.label}, ${info.label}`);
            el.style.left = `${node.x}px`; el.style.top = `${node.y}px`; el.append(shape(node.type));
            nodesLayer.append(el);
            if (M.isComment(node)) renderCommentary(el, node);
            else {
                const label = element('div', 'pmt-node-label'); label.append(element('strong', '', node.label));
                if (node.label !== info.label && !['decision', 'feed_embeddings', 'flush_embeddings'].includes(node.type)) label.append(element('small', '', info.label));
                el.append(label);
            }
            if (flow.start === node.id) el.append(element('span', 'pmt-start-badge', 'START'));
            if (state) el.append(element('span', 'pmt-node-status', state));
            if (!M.isComment(node)) {
                addPort(el, node, 'input', info.input);
                if (node.type === 'decision') { addPort(el, node, 'yes', info.yes); addPort(el, node, 'no', info.no); }
                else addPort(el, node, 'next', info.output);
            }
            el.addEventListener('pointerdown', event => nodeDown(event, node));
            el.addEventListener('dblclick', event => configureSelectedNode(node, event));
            el.addEventListener('contextmenu', event => showNodeMenu(node, event));
            el.addEventListener('keydown', event => nodeKey(event, node));
        }
        renderEdges(); extent();
        $id('pmt-empty').hidden = flow.nodes.length > 0;
        $id('filename').textContent = `${filename}${dirty ? ' •' : ''}`;
        document.title = `${dirty ? '• ' : ''}${flow.name} — Prompt Flow Panel`;
        const operations = flow.nodes.filter(n => !M.isComment(n));
        const counted = (n, word) => `${n} ${n === 1 ? word : ({ 'operación': 'operaciones', 'conexión': 'conexiones' }[word] || word + 's')}`;
        $id('pmt-count').textContent = `${counted(operations.length, 'operación')} · ${counted(flow.nodes.length - operations.length, 'comentario')} · ${counted(flow.edges.length, 'conexión')}`;
        const select = $id('pmt-start'); select.replaceChildren();
        if (!operations.length) select.append(new Option('Agregar una operación', ''));
        for (const n of operations) select.append(new Option(n.label, n.id));
        select.value = flow.start || ''; select.disabled = !editable();
        updateButtons();
    }
    function updateButtons() {
        for (const button of document.querySelectorAll('[data-action]')) {
            const action = button.dataset.action;
            if (['new', 'open', 'example', 'settings', 'validate'].includes(action)) button.disabled = !editable();
            if (action === 'undo') button.disabled = !editable() || !undo.length;
            if (action === 'redo') button.disabled = !editable() || !redo.length;
            if (action === 'zoom-out') button.disabled = zoom <= .25;
            if (action === 'zoom-in') button.disabled = zoom >= 2;
            if (action === 'configure') {
                button.disabled = !editable() || selected.size + selectedEdges.size !== 1;
                button.textContent = currentComment() && selected.size === 1 && !selectedEdges.size ? '✎ Editar comentario' : '⚙ Configurar';
            }
            if (action === 'duplicate') button.disabled = !editable() || !selected.size;
            if (action === 'delete') button.disabled = !editable() || !(selected.size || selectedEdges.size);
            if (action === 'play') button.disabled = !socketReady || !editable() || !flow.nodes.some(n => !M.isComment(n));
            if (action === 'save') button.disabled = !!commentEditor;
            if (action === 'reconnect') button.disabled = !!connecting || socketReady;
            if (action === 'pause') { button.disabled = !['running', 'paused'].includes(runState); button.textContent = runState === 'paused' ? '▶ Reanudar' : 'Ⅱ Pausar'; }
            if (action === 'stop') button.disabled = !['running', 'paused'].includes(runState);
        }
        for (const button of document.querySelectorAll('.agent-tool-item')) { button.disabled = !editable(); button.draggable = editable(); }
        syncCommentTools();
    }
    function palette() {
        const list = $id('agents-list'); list.replaceChildren();
        for (const [type, info] of Object.entries(M.operations)) {
            const button = element('button', 'agent-tool-item'); button.type = 'button'; button.dataset.type = type; button.title = info.help;
            button.append(shape(type)); button.draggable = true;
            button.append(element('span', '', info.label));
            button.addEventListener('dragstart', event => { if (!editable()) { event.preventDefault(); return; } event.dataTransfer.setData('application/x-tlamatini-operation', type); event.dataTransfer.effectAllowed = 'copy'; });
            button.addEventListener('click', () => addNode(type));
            list.append(button);
        }
        updateButtons();
    }
    function addNode(type, point) {
        if (!Object.hasOwn(M.operations, type) || flow.nodes.length >= 500) return;
        const offset = (flow.nodes.length % 6) * 30;
        point = point || { x: viewport.scrollLeft / zoom + 70 + offset, y: viewport.scrollTop / zoom + 65 + offset };
        mutate(() => {
            const n = M.node(type, snap(point.x), snap(point.y));
            const labels = new Set(flow.nodes.map(node => node.label));
            if (labels.has(n.label)) n.label = M.uniqueLabel(n.label, labels);
            flow.nodes.push(n); if (!M.isComment(n)) flow.start ||= n.id; selected = new Set([n.id]); selectedEdge = null; selectedEdges.clear();
        });
        status(type === 'user_commentary' ? 'Comentario agregado. Haz doble clic para escribir; arrastra cualquier borde o esquina para cambiar el tamaño.' : 'Operación agregada. Haz doble clic en ella para configurarla.');
    }
    const connection = UI.connectionDrag({
        viewport, canEdit: editable,
        targetAt: event => {
            const port = document.elementFromPoint(event.clientX, event.clientY)?.closest('.pmt-port.input');
            return port && nodesLayer.contains(port) && !port.disabled ? port : null;
        },
        begin: port => {
            const node = flow.nodes.find(n => n.id === port.closest('.pmt-node').dataset.nodeId);
            const branch = port.dataset.port, [sx, sy] = anchor(node, branch);
            const preview = svg('path', { class: 'pmt-connection-preview connection-preview connection-path', d: connectionPath(sx, sy, sx, sy) });
            layer.append(preview);
            status('Arrastra hasta un triángulo de input. Esc cancela.');
            return { source: node.id, branch, preview, sx, sy };
        },
        move: (data, event) => {
            const p = position(event);
            data.preview.setAttribute('d', connectionPath(data.sx, data.sy, p.x, p.y));
        },
        complete: (source, port) => {
            const targetId = port.closest('.pmt-node').dataset.nodeId;
            mutate(() => {
                const existing = flow.edges.find(e => e.source === source.source && e.branch === source.branch);
                if (existing) existing.target = targetId;
                else flow.edges.push({ id: M.id(), source: source.source, target: targetId, branch: source.branch });
            });
            status('Conexión guardada. Cada output lleva a una sola operación siguiente.');
        },
        dispose: data => data.preview.remove()
    });
    function cancelConnection() { return connection.cancel(); }
    function startConnection(_node, _branch, port, pointerId) {
        endGesture(); connection.start(port, pointerId);
    }
    const nodeMove = UI.nodeDrag({
        viewport,
        duplicate: data => {
            const copies = duplicateNodes(0);
            data.origins = new Map(copies.map(n => [n.id, { x: n.x, y: n.y }]));
        },
        move: (data, dx, dy) => {
            for (const n of flow.nodes) if (data.origins.has(n.id)) {
                const origin = data.origins.get(n.id);
                n.x = snap(origin.x + dx / data.zoom); n.y = snap(origin.y + dy / data.zoom);
            }
            render();
        },
        finish: (data, cancelled) => {
            if (cancelled) { flow = JSON.parse(data.before); selected = data.selection; render(); }
            else changed(data.before);
        },
        failed: error => { status(error.message); alertMessage(error.message); }
    });
    function nodeDown(event, node) {
        if (commentEditor) return;
        if (event.button !== 0 || event.target.closest('button')) return;
        event.stopPropagation();
        if (nodeMove.active) return;
        cancelConnection();
        if (!UI.modified(event) && !selected.has(node.id)) resetSelection();
        selected.add(node.id);
        if (editable() && selected.has(node.id)) {
            nodeMove.start(event, { before: snapshot(), zoom, selection: new Set(selected),
                origins: new Map(flow.nodes.filter(n => selected.has(n.id)).map(n => [n.id, { x: n.x, y: n.y }])) });
        }
        paintSelection(); event.preventDefault(); viewport.focus({ preventScroll: true });
    }
    function deleteSelection() {
        mutate(() => {
            flow.nodes = flow.nodes.filter(n => !selected.has(n.id));
            flow.edges = flow.edges.filter(e => !selectedEdges.has(e.id) && !selected.has(e.source) && !selected.has(e.target));
            if (selected.has(flow.start)) flow.start = flow.nodes.find(n => !M.isComment(n))?.id || null;
            resetSelection();
        });
    }
    function duplicateNodes(offset = 40) {
            if (flow.nodes.length + selected.size > 500) throw new Error('El canvas admite hasta 500 operaciones.');
            const labels = new Set(flow.nodes.map(n => n.label));
            const mapping = new Map(), copies = flow.nodes.filter(n => selected.has(n.id)).map(n => {
                const clone = M.copy(n); clone.id = M.id(); clone.label = M.uniqueLabel(n.label, labels);
                labels.add(clone.label); clone.x = snap(n.x + offset); clone.y = snap(n.y + offset); mapping.set(n.id, clone.id); return clone;
            });
            const links = flow.edges.filter(e => mapping.has(e.source) && mapping.has(e.target)).map(e => ({ ...e, id: M.id(), source: mapping.get(e.source), target: mapping.get(e.target) }));
            flow.nodes.push(...copies); flow.edges.push(...links); selected = new Set(mapping.values()); selectedEdge = null; selectedEdges.clear();
            return copies;
    }
    function duplicate() {
        mutate(() => duplicateNodes());
    }
    function restoreHistory(from, to) {
        if (!editable() || !from.length) return;
        to.push(snapshot()); flow = JSON.parse(from.pop()); dirty = snapshot() !== clean;
        selected = new Set([...selected].filter(id => flow.nodes.some(node => node.id === id)));
        for (const id of selectedEdges) if (!flow.edges.some(edge => edge.id === id)) selectedEdges.delete(id);
        selectedEdge = selectedEdges.size === 1 ? [...selectedEdges][0] : null;
        nodeStates.clear(); traversed.clear(); persist(); render();
    }
    function formDialog(title, build, accept, options = {}) {
        const form = element('form', 'pmt-form'); const fields = {};
        function field(name, label, type, value, choices) {
            const row = element('label', type === 'checkbox' ? 'pmt-checkbox' : '');
            const input = element(type === 'textarea' ? 'textarea' : type === 'select' ? 'select' : 'input');
            if (input.tagName === 'INPUT') input.type = type;
            if (choices) for (const [v, text] of choices) input.append(new Option(text, v));
            if (type === 'checkbox') input.checked = Boolean(value); else input.value = value ?? '';
            input.name = name; input.id = `pmt-field-${name}`; row.htmlFor = input.id;
            if (type === 'checkbox') row.append(input, document.createTextNode(label)); else row.append(document.createTextNode(label), input);
            form.append(row); fields[name] = input; return input;
        }
        build({ form, field, fields });
        const error = element('p', 'pmt-form-error'); error.setAttribute('role', 'alert'); form.append(error);
        document.body.append(form);
        let accepted = false;
        const close = () => window.jQuery(form).dialog('close');
        const submit = async () => {
            try {
                if (!form.reportValidity()) return;
                await accept(fields); accepted = true; close();
            } catch (e) { error.textContent = e.message; }
        };
        form.addEventListener('submit', event => { event.preventDefault(); submit(); });
        const buttons = options.buttons ? options.buttons(fields, close, () => { accepted = true; }) : [{ text: options.acceptLabel || 'Guardar', click: submit }, { text: 'Cancelar', click: close }];
        window.jQuery(form).dialog({ title, modal: true, resizable: false, width: Math.min(640, window.innerWidth - 24), closeOnEscape: true,
            buttons,
            close() { window.jQuery(form).dialog('destroy'); form.remove(); options.onClose?.(accepted); },
            open() { form.querySelector('textarea, input, select')?.focus(); },
        });
        return { close, form };
    }
    function configureNode(node) {
        if (M.isComment(node)) { editCommentary(node); return; }
        if (!editable()) return;
        const draft = M.copy(node), config = draft.config, kind = draft.type;
        formDialog(`Configurar · ${M.operations[kind].label}`, ({ form, field, fields }) => {
            form.append(element('p', '', M.operations[kind].help));
            field('label', 'Etiqueta', 'text', draft.label).maxLength = 120;
            if (!['flush_embeddings', 'clean_history'].includes(kind)) {
                const title = kind === 'decision' ? 'Pregunta (si se le pregunta al usuario)' : kind === 'user_input' ? 'Mensaje para el usuario' : kind === 'feed_embeddings' ? 'Texto para los embeddings' : kind === 'terminater' ? 'Comando que se va a escribir (usa <<USER:hint>> para darle el teclado al usuario)' : 'Prompt';
                field('text', title, 'textarea', config.text).maxLength = 100000;
                form.append(element('small', '', 'Usa {{last_output}} para insertar la respuesta del prompt anterior o la del usuario.'));
            }
            if (['prompt', 'programmed_prompt'].includes(kind)) {
                field('multi_turn', 'Multi-Turn — permitir los tools y agents activados', 'checkbox', config.multi_turn);
                field('acpx', 'ACPX — permitir agents de programación externos', 'checkbox', config.acpx).disabled = !config.multi_turn;
                fields.multi_turn.addEventListener('change', () => { fields.acpx.disabled = !fields.multi_turn.checked; if (!fields.multi_turn.checked) fields.acpx.checked = false; });
            }
            if (kind === 'programmed_prompt') {
                const delay = field('delay_seconds', 'Retraso antes de enviar (segundos de ejecución activa)', 'number', config.delay_seconds); delay.min = 0; delay.max = 86400; delay.step = 'any';
                let local = '';
                if (config.scheduled_at) { const date = new Date(config.scheduled_at); local = new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 19); }
                field('scheduled_at', 'Hora programada (opcional, en tu zona horaria local)', 'datetime-local', local).step = '1';
                form.append(element('small', '', 'Espera hasta esta hora y luego aplica el retraso. Las horas que ya pasaron se ejecutan de inmediato. Mantén abiertos la página y Tlamatini.'));
            }
            if (kind === 'terminater') {
                const inherited = field('use_my_defaults', 'Use my defaults (speed, shell, waiting and advisor)', 'checkbox', config.use_my_defaults);
                const inheritedFields = [];
                field('explanation', 'Spoken explanation (optional; never include private values)', 'text', config.explanation || '').maxLength = 1000;
                field('action', 'Qué hacer', 'select', config.action, [['run', 'Ejecutar un comando (escribirlo, esperar y leer el resultado)'], ['open', 'Abrir una terminal nueva'], ['type', 'Escribir en una terminal'], ['handover', 'Escribir parte de un comando y luego pasarle el control al usuario'], ['send_key', 'Presionar teclas (Ctrl+C, Enter, ...)'], ['wait', 'Esperar el comando en ejecución'], ['read', 'Leer el output de la terminal'], ['abort', 'Interrumpir el comando en ejecución'], ['kill', 'Cerrar una terminal'], ['force_kill', 'Forzar el cierre de una terminal'], ['kill_all', 'Forzar el cierre de todas las terminales'], ['list', 'Listar las terminales'], ['focus', 'Enfocar una terminal'], ['layout', 'Cambiar la distribución (pestañas, mosaico, ...)'], ['clear', 'Limpiar una pantalla'], ['watch_user', 'Observar lo que escribe el usuario'], ['warn_user', 'Avisar al usuario']]);
                inheritedFields.push(field('kind', 'Tipo de terminal', 'select', config.kind, [['cmd', 'CMD'], ['powershell', 'PowerShell'], ['pwsh', 'PowerShell 7']]));
                field('terminal', 'Terminal (id o título; vacío = la activa)', 'text', config.terminal).maxLength = 80;
                field('cwd', 'Carpeta inicial (opcional)', 'text', config.cwd).maxLength = 1000;
                field('submit', 'Presionar Enter después de escribir', 'checkbox', config.submit);
                field('secret', 'Texto secreto (nunca se guarda en el log ni se devuelve)', 'checkbox', config.secret);
                field('wait', 'Esperar a que termine el comando', 'checkbox', config.wait);
                field('close_after', 'Cerrar la terminal cuando termine', 'checkbox', config.close_after);
                for (const [name, label, min, max] of [['typing_wpm', 'Velocidad de escritura (palabras por minuto, 20-160)', 20, 160], ['wait_seconds', 'Dejar de esperar después de (segundos)', 1, 3600], ['hang_seconds', 'Sin output durante este tiempo = colgado (segundos)', 3, 3600], ['user_wait_seconds', "Esperar la parte del usuario (segundos)", 5, 3600]]) {
                    const input = field(name, label, 'number', config[name]); input.min = min; input.max = max; input.step = 'any';
                    inheritedFields.push(input);
                }
                const syncInherited = () => { for (const input of inheritedFields) input.disabled = inherited.checked; };
                inherited.addEventListener('change', syncInherited); syncInherited();
            }
            if (kind === 'decision') {
                field('comparison', 'Regla de decisión', 'select', config.comparison, [['contains', 'El último output contiene'], ['not_contains', 'El último output no contiene'], ['equals', 'El último output es igual a'], ['is_empty', 'El último output está vacío'], ['user', 'Preguntar al usuario: Sí o No']]);
                field('value', 'Valor de comparación', 'text', config.value).maxLength = 10000;
                field('case_sensitive', 'Distinguir mayúsculas y minúsculas', 'checkbox', config.case_sensitive);
            }
        }, fields => {
            if (!editable()) throw new Error('Detén la ejecución antes de editar.');
            draft.label = fields.label.value.trim() || M.operations[kind].label;
            if (fields.text) config.text = fields.text.value;
            for (const name of ['multi_turn', 'acpx', 'case_sensitive', 'submit', 'secret', 'wait', 'close_after', 'use_my_defaults']) if (fields[name]) config[name] = fields[name].checked;
            for (const name of ['comparison', 'value', 'action', 'kind', 'terminal', 'cwd', 'explanation']) if (fields[name]) config[name] = fields[name].value;
            for (const name of ['typing_wpm', 'wait_seconds', 'hang_seconds', 'user_wait_seconds']) if (fields[name]) config[name] = Number(fields[name].value);
            if (fields.delay_seconds) config.delay_seconds = Number(fields.delay_seconds.value);
            if (fields.scheduled_at) config.scheduled_at = fields.scheduled_at.value ? new Date(fields.scheduled_at.value).toISOString() : '';
            const candidate = M.copy(flow); candidate.nodes[candidate.nodes.findIndex(n => n.id === node.id)] = draft;
            M.validate(candidate); mutate(() => { flow = candidate; });
        });
    }
    function configureEdge(edge) {
        if (!editable()) return;
        const source = flow.nodes.find(n => n.id === edge.source);
        formDialog('Configurar la conexión', ({ field }) => {
            field('target', 'Destino', 'select', edge.target, flow.nodes.filter(n => !M.isComment(n)).map(n => [n.id, n.label]));
            field('branch', 'Output', 'select', edge.branch, source.type === 'decision' ? [['yes', 'Sí'], ['no', 'No']] : [['next', 'Siguiente']]);
        }, fields => {
            const candidate = M.copy(flow), item = candidate.edges.find(e => e.id === edge.id);
            item.target = fields.target.value; item.branch = fields.branch.value; M.validate(candidate);
            mutate(() => { flow = candidate; });
        });
    }
    async function mayReplace() { return editable() && (!dirty || await confirm('¿Quieres reemplazar el diagrama actual?', 'Se van a reemplazar los cambios sin guardar. Para conservarlos, primero guarda un archivo .fpmt.')); }
    function load(value, name, saved = true) {
        flow = M.validate(value); filename = M.flowFilename(name); clean = saved ? snapshot() : ''; dirty = !saved;
        undo = []; redo = []; resetSelection(); nodeStates.clear(); traversed.clear();
        viewport.scrollTo(0, 0); persist(); render(); status(`Se abrió ${filename}`);
    }
    async function openFile(file) {
        if (!file || !editable()) return;
        if (!M.isFlowFilename(file.name)) throw new Error('Elige un archivo .fpmt de Prompt Flow Panel.');
        if (file.size > 5 * 1024 * 1024) throw new Error('El archivo .fpmt debe pesar menos de 5 MiB.');
        let value;
        try { value = M.validate(JSON.parse((await file.text()).replace(/^\uFEFF/, ''))); }
        catch (e) { throw new Error(`No se pudo abrir ${file.name}: ${e.message}`, { cause: e }); }
        if (await mayReplace()) load(value, file.name);
    }
    function save() {
        formDialog('Guardar el prompt flow', ({ field, form }) => {
            field('filename', 'Nombre del archivo', 'text', filename).maxLength = 150;
            form.append(element('p', '', 'El archivo .fpmt incluye el diagrama y la configuración de las operaciones. El output de la ejecución se queda en esta página.'));
        }, fields => {
            let name = fields.filename.value.trim();
            if (!name || /[<>:"/\\|?*]/.test(name) || Array.from(name).some(c => c.charCodeAt(0) < 32)) throw new Error('Escribe un nombre de archivo sin separadores de path ni caracteres reservados.');
            name = M.flowFilename(name);
            const validated = M.validate(flow), data = JSON.stringify(validated, null, 2), blob = new Blob([data], { type: 'application/json;charset=utf-8' });
            if (blob.size > 5 * 1024 * 1024) throw new Error('El diagrama supera el límite de 5 MiB por archivo.');
            const url = URL.createObjectURL(blob), a = element('a'); a.href = url; a.download = name; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 60000);
            filename = name; clean = snapshot(); dirty = false; persist(); render(); status(`Se descargó ${name}`);
        }, { acceptLabel: 'Descargar .fpmt' });
    }
    function settings() {
        formDialog('Configuración del flow', ({ field, form }) => {
            field('name', 'Nombre del flow', 'text', flow.name).maxLength = 120;
            const steps = field('max_steps', 'Máximo de operaciones por ejecución', 'number', flow.max_steps); steps.min = 1; steps.max = 5000; steps.step = 1;
            form.append(element('p', '', 'Se admiten ciclos. El límite de pasos detiene un flow que se queda dando vueltas.'));
        }, fields => {
            const candidate = { ...flow, name: fields.name.value.trim() || 'Untitled', max_steps: Number(fields.max_steps.value) }; M.validate(candidate); mutate(() => { flow = candidate; });
        });
    }
    function log(title, text, error = false) {
        const item = element('article', error ? 'error' : ''); item.append(element('strong', '', title), element('pre', '', text));
        const target = $id('pmt-run-log'); target.querySelector('.pmt-log-hint')?.remove(); target.append(item);
        while (target.children.length > 150) target.firstElementChild.remove(); target.scrollTop = target.scrollHeight;
    }
    function connectionLost(message) {
        socketReady = false;
        const bar = $id('connection-status');
        bar.textContent = 'Se perdió la conexión en vivo. Usa Reconectar o actualiza la página antes de continuar.';
        bar.classList.remove('connection-status-hidden', 'connection-status-ok');
        bar.classList.add('connection-status-warning');
        status(message);
        if (playbackActive()) {
            runState = 'failed'; $id('pmt-run-state').textContent = runState;
            if (activeNode && nodeStates.get(activeNode) === 'running') nodeStates.set(activeNode, 'failed');
            closeInput();
            status('Se perdió la conexión. Se detuvo el flow; el servidor cancela la ejecución activa.');
            log('Desconectado', 'Se perdió la conexión. Guarda tu diagrama, vuelve a conectarte e inicia de forma explícita una ejecución nueva.', true);
            render();
        } else updateButtons();
    }
    function send(action, data = {}) {
        try {
            if (!socketReady || socket?.readyState !== WebSocket.OPEN) throw new Error('La conexión en vivo no está disponible. Usa Reconectar o actualiza la página antes de continuar.');
            socket.send(JSON.stringify({ action, run_id: runId, ...data }));
        } catch (error) {
            connectionLost(error.message); socket?.close(); throw error;
        }
    }
    function connectSocket() {
        if (connecting) return connecting;
        if (socketReady && socket?.readyState === WebSocket.OPEN) return Promise.resolve();
        socketReady = false;
        connecting = new Promise((resolve, reject) => {
            const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws/prompt-flow-panel/`);
            socket = ws;
            let failed = false, heartbeat = null, pongTimer = null;
            const timer = setTimeout(() => fail(new Error('Hubo un timeout al conectar con Tlamatini.')), 15000);
            function fail(error) {
                if (failed) return;
                failed = true; clearTimeout(timer); clearInterval(heartbeat); clearTimeout(pongTimer);
                if (socket === ws) { socket = null; connectionLost(error.message); }
                ws.close(); reject(error);
            }
            function ping() {
                if (pongTimer !== null) return;
                if (ws.readyState !== WebSocket.OPEN) { fail(new Error('La conexión en vivo no está disponible.')); return; }
                pongTimer = setTimeout(() => fail(new Error('Tlamatini dejó de responder. Usa Reconectar cuando el servidor esté disponible.')), 15000);
                try { ws.send(JSON.stringify({ action: 'ping' })); }
                catch (error) { fail(error); }
            }
            ws.onerror = () => fail(new Error('No se pudo conectar con Tlamatini. Revisa que el servidor esté corriendo.'));
            ws.onmessage = event => {
                if (socket !== ws || failed) return;
                try {
                    const data = JSON.parse(event.data);
                    if (data.event === 'ready') {
                        clearTimeout(timer); socketReady = true;
                        const bar = $id('connection-status'), wasDisconnected = bar.classList.contains('connection-status-warning');
                        bar.textContent = ''; bar.classList.add('connection-status-hidden'); bar.classList.remove('connection-status-warning', 'connection-status-ok');
                        if (wasDisconnected) status('Conexión establecida con Tlamatini. Presiona Ejecutar para iniciar una ejecución nueva.');
                        clearInterval(heartbeat); heartbeat = setInterval(ping, 8000);
                        updateButtons(); resolve();
                    } else if (data.event === 'pong') { clearTimeout(pongTimer); pongTimer = null; }
                    else receive(data);
                } catch (e) { log('Error de conexión', e.message, true); }
            };
            ws.onclose = () => fail(new Error('Se cerró la conexión. Inicia sesión en Tlamatini y usa Reconectar para intentarlo otra vez.'));
        }).catch(error => { connectionLost(error.message); throw error; }).finally(() => { connecting = null; updateButtons(); });
        updateButtons();
        return connecting;
    }
    async function play() {
        if (!editable() || !socketReady) return;
        const validated = M.validate(flow, true);
        if (new Blob([JSON.stringify(validated)]).size > 5 * 1024 * 1024) throw new Error('El flow supera el límite de 5 MiB para ejecutarse.');
        runState = 'starting'; runId = null; activeNode = null; nodeStates.clear(); traversed.clear();
        render(); $id('pmt-run-state').textContent = runState; $id('pmt-run-panel').open = true; $id('pmt-run-log').replaceChildren(); status('Conectando con Tlamatini…');
        try { await connectSocket(); send('start', { flow: validated }); }
        catch (e) { runState = 'failed'; $id('pmt-run-state').textContent = runState; render(); throw e; }
    }
    function closeInput() { if (inputDialog) { internalClose = true; inputDialog.close(); inputDialog = null; internalClose = false; } }
    function receive(data) {
        if (data.event === 'pong') return;
        if (data.event === 'state' && data.status === 'running' && runState === 'starting') runId = data.run_id;
        if (runId && data.run_id !== runId) return;
        if (data.event === 'state') {
            runState = data.status; $id('pmt-run-state').textContent = runState;
            const hints = { running: 'El flow se está ejecutando', paused: 'En pausa. La solicitud actual al modelo puede terminar; la siguiente operación espera.', stopping: 'Deteniendo. Esperando a que la solicitud activa termine de cancelarse…' };
            status(data.message || hints[runState] || runState);
            if (editable()) {
                closeInput();
                if (activeNode && nodeStates.get(activeNode) === 'running') nodeStates.set(activeNode, runState === 'failed' ? 'failed' : 'stopped');
                log(runState === 'failed' ? 'Error en el flow' : 'Ejecución terminada', data.message || runState, runState === 'failed');
            }
            render();
        } else if (data.event === 'node') {
            activeNode = data.node_id; nodeStates.set(data.node_id, data.status); render();
            const node = flow.nodes.find(n => n.id === data.node_id);
            if (data.status === 'running') { status(`Paso ${data.step}: ${node?.label || data.node_id}`); log(`Paso ${data.step}`, `${node?.label || data.node_id} — ${M.operations[node?.type]?.label || ''}`); }
        } else if (data.event === 'edge') { traversed.add(data.edge_id); renderEdges(); }
        else if (data.event === 'output') log(flow.nodes.find(n => n.id === data.node_id)?.label || 'Output', data.text);
        else if (data.event === 'progress' || data.event === 'waiting') { status(data.message); log('Progreso', data.message); }
        else if (data.event === 'error') {
            log('Error del flow', data.message, true); status(data.message);
            if (runState === 'starting') { runState = 'failed'; $id('pmt-run-state').textContent = runState; render(); }
        } else if (data.event === 'input') showInput(data);
    }
    function showInput(data) {
        closeInput();
        const decision = data.kind === 'decision';
        inputDialog = formDialog(decision ? 'Decisión · elige un branch' : 'Input del usuario', ({ form, field }) => {
            form.append(element('p', '', data.message || (decision ? '¿Qué branch debe tomar el flow?' : 'Escribe tu respuesta para continuar.')));
            if (!decision) field('reply', 'Tu respuesta', 'textarea', '').maxLength = 100000;
        }, fields => send('reply', { request_id: data.request_id, value: fields.reply.value }), {
            acceptLabel: 'Continuar el flow',
            buttons: decision ? (_fields, close, accepted) => [
                { text: 'Sí', click() { send('reply', { request_id: data.request_id, value: 'yes' }); accepted(); close(); } },
                { text: 'No', click() { send('reply', { request_id: data.request_id, value: 'no' }); accepted(); close(); } },
                { text: 'Cancelar', click: close },
            ] : undefined,
            onClose(accepted) { inputDialog = null; if (!accepted && !internalClose && !editable()) { try { send('stop'); } catch (e) { status(e.message); } } },
        });
    }
    function setZoom(value) {
        cancelConnection();
        const centerX = (viewport.scrollLeft + viewport.clientWidth / 2) / zoom, centerY = (viewport.scrollTop + viewport.clientHeight / 2) / zoom;
        zoom = UI.clampZoom(value); extent();
        viewport.scrollLeft = Math.max(0, centerX * zoom - viewport.clientWidth / 2); viewport.scrollTop = Math.max(0, centerY * zoom - viewport.clientHeight / 2); persist();
    }
    function fit() {
        cancelConnection();
        if (!flow.nodes.length) { setZoom(1); viewport.scrollTo(0, 0); return; }
        const minX = Math.min(...flow.nodes.map(n => n.x)), minY = Math.min(...flow.nodes.map(n => n.y));
        const maxX = Math.max(...flow.nodes.map(n => n.x + nodeSize(n).width)), maxY = Math.max(...flow.nodes.map(n => n.y + nodeSize(n).height));
        const view = UI.fitView(viewport, { left: minX, top: minY, right: maxX, bottom: maxY });
        zoom = view.zoom; extent(); viewport.scrollLeft = view.left; viewport.scrollTop = view.top; persist();
    }
    async function action(name) {
        try {
            if (name === 'new' && await mayReplace()) load(M.blank(), 'Untitled.fpmt');
            else if (name === 'open' && editable()) $id('pmt-file-input').click();
            else if (name === 'save') save();
            else if (name === 'example' && await mayReplace()) { load(M.example(), 'Prompting kickoff.fpmt', false); fit(); }
            else if (name === 'undo') restoreHistory(undo, redo);
            else if (name === 'redo') restoreHistory(redo, undo);
            else if (name === 'duplicate') duplicate();
            else if (name === 'delete') deleteSelection();
            else if (name === 'configure') { if (selectedEdge) configureEdge(flow.edges.find(e => e.id === selectedEdge)); else if (selected.size === 1) configureNode(flow.nodes.find(n => selected.has(n.id))); }
            else if (name === 'settings' && editable()) settings();
            else if (name === 'validate') { M.validate(flow, true); await alertMessage('El flow está listo para ejecutarse. Los ciclos se detienen en el límite de pasos configurado.', 'Flow validado'); }
            else if (name === 'play') await play();
            else if (name === 'reconnect') await connectSocket();
            else if (name === 'pause') send(runState === 'paused' ? 'resume' : 'pause');
            else if (name === 'stop') { send('stop'); closeInput(); }
            else if (name === 'zoom-in') setZoom(zoom + .1);
            else if (name === 'zoom-out') setZoom(zoom - .1);
            else if (name === 'fit') fit();
            else if (name === 'help') await alertMessage('Arrastra una operación o haz clic en ella para agregarla. Haz doble clic en una figura para editar su configuración. Arrastra un triángulo de output del lado derecho hasta un triángulo de input del lado izquierdo y suéltalo para conectarlos, igual que en Agentic Control Panel. La curva sigue a tu puntero y los triángulos se resaltan. Suelta sobre el canvas vacío o presiona Esc para cancelar. Si vuelves a conectar un output ocupado, se reemplaza esa conexión. Las figuras de Decisión tienen a la derecha los outputs Y (sí) y N (no). Con el teclado, activa un output, ve con Tab hasta un input y actívalo.\n\nCtrl+clic selecciona varias figuras; arrastra sobre el canvas vacío para seleccionar un grupo. Delete elimina la selección, Ctrl+D duplica, Ctrl+Z deshace y Ctrl+Shift+Z rehace. Usa las flechas del teclado para mover las figuras seleccionadas.\n\n“Comentario del usuario” es una nota estática en forma de burbuja de diálogo. Haz doble clic para escribir en ella; “Listo” o Ctrl+Enter guarda y Esc cancela. Selecciona un fragmento para combinar fuentes, tamaños, colores de texto, negrita, cursiva y subrayado con la mini barra de herramientas flotante. Si no hay selección, el formato se aplica al texto que escribas a continuación. El color de la burbuja y la alineación se aplican a toda la nota. Arrastra cualquier borde o esquina para cambiar el tamaño; “Ajustar al texto” quita el espacio vertical sobrante. Los comentarios no tienen diálogo de configuración. La burbuja crece hasta que quepa el texto, sin barras de desplazamiento. Las notas se guardan con el diagrama y nunca se ejecutan. “Input del usuario” usa la figura con muesca y pide una respuesta durante la ejecución.\n\nElige la operación de Inicio, presiona Validar y luego Ejecutar. Cada ejecución tiene su propia conversación y sus propios embeddings. {{last_output}} inserta la última respuesta o el último input del usuario. “Limpiar historial” borra la conversación y el último output de esa ejecución; “Vaciar embeddings” borra su contexto de recuperación.\n\nLa pausa surte efecto entre una operación y otra. Detener pide la cancelación y espera a que termine la llamada activa al modelo. Si cierras un diálogo de input, el flow se detiene. Mantén abiertos esta página y Tlamatini para los prompts programados. Los archivos nunca se ejecutan sólo por abrirlos.\n\nGuardar descarga un diagrama .fpmt con versión. El panel también guarda un borrador local en este browser. Los antiguos archivos de texto prompt.pmt del system prompt se manejan por separado.', 'Cómo usar Prompt Flow Panel');
        } catch (e) { status(e.message); await alertMessage(e.message); }
    }
    document.querySelectorAll('[data-action]').forEach(button => button.addEventListener('click', event => { event.preventDefault(); action(button.dataset.action); }));
    $id('pmt-start').addEventListener('change', event => mutate(() => { flow.start = event.target.value || null; }));
    $id('pmt-file-input').addEventListener('change', async event => { try { await openFile(event.target.files[0]); } catch (e) { await alertMessage(e.message); } finally { event.target.value = ''; } });
    viewport.addEventListener('dragover', event => { if (editable()) { event.preventDefault(); event.dataTransfer.dropEffect = 'copy'; } });
    // Palette drags (an operation dropped on the canvas) stay here. FILES are claimed
    // by file_drop_router.js before this handler can see them; they arrive below.
    viewport.addEventListener('drop', async event => {
        if (event.dataTransfer.files.length) return;
        event.preventDefault(); if (!editable()) return;
        try {
            const point = position(event);
            addNode(event.dataTransfer.getData('application/x-tlamatini-operation'), { x: point.x - 100, y: point.y - 64 });
        } catch (e) { await alertMessage(e.message); }
    });
    if (window.TlamatiniFileDrop) {
        window.TlamatiniFileDrop.register('flow-prompt', async files => {
            if (!editable()) {
                return { ignored: files, note: 'No se puede reemplazar el diagrama mientras hay una ejecución activa o se está editando una nota.' };
            }
            try { await openFile(files[0]); } catch (e) { await alertMessage(e.message); }
            return files.length > 1
                ? { ignored: files.slice(1), note: 'Se abrió ' + files[0].name + '; el panel admite un solo diagrama, así que no se abrieron los demás.' }
                : {};
        }, { label: 'Prompt flow (.fpmt) → se abre como el diagrama actual' });
    }
    viewport.addEventListener('pointerdown', event => {
        if (commentEditor || event.button !== 0 || event.target.closest('.pmt-node, .pmt-edge, button')) return;
        const p = position(event);
        if (!event.ctrlKey && !event.metaKey) resetSelection();
        endGesture(); gesture = { kind: 'select', from: p, initial: new Set(selected), initialEdges: new Set(selectedEdges) }; render(); event.preventDefault(); viewport.focus({ preventScroll: true });
    });
    document.addEventListener('pointermove', event => {
        if (!gesture) return;
        if (gesture.kind === 'resize') {
            resizeComment(gesture, (event.clientX - gesture.fromX) / gesture.scale, (event.clientY - gesture.fromY) / gesture.scale);
            return;
        }
        const p = position(event);
        {
            const left = Math.min(p.x, gesture.from.x), top = Math.min(p.y, gesture.from.y), width = Math.abs(p.x - gesture.from.x), height = Math.abs(p.y - gesture.from.y);
            const box = $id('pmt-marquee'); box.hidden = false; Object.assign(box.style, { left: `${left}px`, top: `${top}px`, width: `${width}px`, height: `${height}px` });
            selected = new Set(gesture.initial);
            selectedEdges.clear(); gesture.initialEdges.forEach(id => selectedEdges.add(id));
            if (width > 5 || height > 5) {
                const bounds = box.getBoundingClientRect();
                nodesLayer.querySelectorAll('.pmt-node').forEach(n => { if (UI.intersects(bounds, n.getBoundingClientRect())) selected.add(n.dataset.nodeId); });
                layer.querySelectorAll('.pmt-edge').forEach(edge => { if (UI.intersects(bounds, edge.querySelector('.connection-path').getBoundingClientRect())) selectedEdges.add(edge.dataset.edgeId); });
            }
            selectedEdge = selectedEdges.size === 1 ? [...selectedEdges][0] : null;
            paintSelection();
        }
    });
    function endGesture() {
        if (cancelConnection()) return;
        nodeMove.cancel();
        if (!gesture) return;
        const previous = gesture; gesture = null; $id('pmt-marquee').hidden = true; document.body.classList.remove('resizing');
        if (previous.kind === 'resize') {
            document.body.style.cursor = ''; commentElement(previous.node)?.classList.remove('comment-resizing');
            if (commentEditor) { Object.assign(previous.node, JSON.parse(previous.before).nodes.find(n => n.id === previous.node.id)); refreshComment(previous.node); }
            else { flow = JSON.parse(previous.before); render(); }
        }
        if (previous.pointerId !== undefined && viewport.hasPointerCapture(previous.pointerId)) viewport.releasePointerCapture(previous.pointerId);
        paintSelection();
    }
    document.addEventListener('pointerup', () => {
        if (gesture?.kind === 'resize') {
            const previous = gesture; gesture = null; document.body.style.cursor = '';
            commentElement(previous.node)?.classList.remove('comment-resizing');
            if (viewport.hasPointerCapture(previous.pointerId)) viewport.releasePointerCapture(previous.pointerId);
            if (!commentEditor) changed(previous.before); else syncCommentTools();
        }
        else if (gesture) endGesture();
    });
    viewport.addEventListener('lostpointercapture', () => { if (gesture) endGesture(); });
    document.addEventListener('pointercancel', endGesture); window.addEventListener('blur', endGesture);
    function sizeSidebar(value) {
        const percent = Math.max(15, Math.min(70, value));
        document.body.style.setProperty('--pmt-sidebar', percent + '%');
        window.TlmSplitters.describe($id('drag-divider'), percent, 15, 70,
            `Barra de operaciones ${Math.round(percent)}%, canvas ${Math.round(100 - percent)}%`);
        extent();
    }
    UI.bindDivider({
        element: $id('drag-divider'), before: endGesture,
        min: 15, max: 70,
        value: () => $id('main-agents-container').getBoundingClientRect().width / $id('agents-container').clientWidth * 100,
        atPointer: x => (x - $id('agents-container').getBoundingClientRect().left) / $id('agents-container').clientWidth * 100,
        apply: sizeSidebar
    });
    sizeSidebar($id('main-agents-container').getBoundingClientRect().width / $id('agents-container').clientWidth * 100);
    // Layout is a per-user browser preference, never a flow edit or a zoom operation.
    const workspace = $id('pmt-workspace'), outputPanel = $id('pmt-run-panel'), outputDivider = $id('pmt-output-divider');
    const layoutKey = `tlamatini.prompting-flow.layout.v1.${document.body.dataset.userId}`;
    let outputPercent = 20, layoutTimer = null;
    try {
        const saved = JSON.parse(localStorage.getItem(layoutKey) || 'null');
        if (typeof saved?.outputPercent === 'number' && Number.isFinite(saved.outputPercent)) outputPercent = Math.max(5, Math.min(95, saved.outputPercent));
    } catch (_) { /* A blocked or invalid preference must not prevent editing. */ }
    function paneHeight() {
        return Math.max(0, workspace.clientHeight - workspace.querySelector('.pmt-status-strip').offsetHeight - outputDivider.offsetHeight);
    }
    function sizeOutput() {
        outputDivider.hidden = !outputPanel.open;
        const height = paneHeight() * outputPercent / 100;
        outputPanel.style.height = outputPanel.open ? `${height}px` : '';
        // Native details has an anonymous content wrapper: percentage log heights
        // resolve against that wrapper rather than the pane in some browsers.
        $id('pmt-run-log').style.height = outputPanel.open ? `${Math.max(0, height - outputPanel.querySelector('summary').offsetHeight)}px` : '';
        outputDivider.setAttribute('aria-valuenow', String(Math.round(outputPercent)));
        outputDivider.setAttribute('aria-valuetext', `${Math.round(outputPercent)}% Output de la ejecución`);
        extent();
    }
    function setOutputPercent(value) {
        outputPercent = Math.max(5, Math.min(95, value));
        sizeOutput();
        clearTimeout(layoutTimer);
        layoutTimer = setTimeout(() => {
            try { localStorage.setItem(layoutKey, JSON.stringify({ outputPercent })); }
            catch (_) { /* Resizing remains available without browser storage. */ }
        }, 150);
    }
    UI.bindDivider({
        element: outputDivider, axis: 'y', keyDirection: -1, before: endGesture,
        min: 5, max: 95,
        value: () => outputPercent,
        atPointer: y => (workspace.getBoundingClientRect().bottom - y - outputDivider.offsetHeight / 2) / Math.max(1, paneHeight()) * 100,
        apply: setOutputPercent
    });
    outputPanel.addEventListener('toggle', sizeOutput);
    const paneObserver = new ResizeObserver(sizeOutput);
    paneObserver.observe(workspace);
    paneObserver.observe(workspace.querySelector('.pmt-status-strip'));
    sizeOutput();
    viewport.addEventListener('wheel', event => { if (event.ctrlKey || event.metaKey) { event.preventDefault(); setZoom(zoom + (event.deltaY < 0 ? .1 : -.1)); } }, { passive: false });
    document.addEventListener('keydown', event => {
        if (commentEditor) {
            if (event.key === 'Escape') { event.preventDefault(); if (gesture) endGesture(); else finishCommentary(false); }
            else if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); finishCommentary(true); }
            return;
        }
        if (UI.isTyping(event)) return;
        const key = event.key.toLowerCase(), mod = event.ctrlKey || event.metaKey;
        if (mod && ['s', 'o', 'z', 'y', 'd', 'a'].includes(key)) {
            event.preventDefault();
            if (key === 'a') { selected = new Set(flow.nodes.map(n => n.id)); selectedEdge = null; selectedEdges.clear(); render(); }
            else action({ s: 'save', o: 'open', z: event.shiftKey ? 'redo' : 'undo', y: 'redo', d: 'duplicate' }[key]);
        } else if (event.key === 'Delete' || event.key === 'Backspace') { event.preventDefault(); action('delete'); }
        else if (event.key === 'Escape') { endGesture(); resetSelection(); render(); status('Se quitó la selección'); }
        else if (event.key === 'Enter' && selected.size === 1 && !event.target.closest('button, a')) { event.preventDefault(); action('configure'); }
        else if (event.key.startsWith('Arrow') && selected.size && editable()) {
            event.preventDefault(); const amount = event.shiftKey ? 40 : 10;
            mutate(() => { for (const n of flow.nodes) if (selected.has(n.id)) { n.x = snap(n.x + (event.key === 'ArrowRight' ? amount : event.key === 'ArrowLeft' ? -amount : 0)); n.y = snap(n.y + (event.key === 'ArrowDown' ? amount : event.key === 'ArrowUp' ? -amount : 0)); } });
        }
    });
    window.addEventListener('beforeunload', event => { if (dirty || !editable()) { event.preventDefault(); event.returnValue = ''; } });
    window.addEventListener('resize', extent);
    try {
        const saved = JSON.parse(localStorage.getItem(storeKey) || 'null');
        if (saved) { flow = M.validate(saved.flow); filename = M.flowFilename(typeof saved.filename === 'string' && saved.filename.trim() ? saved.filename : 'Recovered.fpmt'); zoom = Math.min(2, Math.max(.25, Number(saved.zoom) || 1)); clean = ''; dirty = true; status('Se restauró tu borrador local. Guarda un archivo .fpmt para conservar una copia portátil.'); }
    } catch (e) { status(`No se pudo restaurar el borrador local: ${e.message}`); }
    palette(); render();
    async function openIncomingFile() {
        const incoming = $id('server-fpmt-data'), error = $id('flow-open-error');
        if (!incoming && !error) return;
        const address = new URL(window.location.href);
        address.searchParams.delete('open');
        history.replaceState(null, '', address);
        if (error) { await alertMessage(JSON.parse(error.textContent), 'No se pudo abrir el flow'); return; }
        try {
            const value = M.validate(JSON.parse(incoming.textContent));
            if (await mayReplace()) load(value, JSON.parse($id('server-fpmt-filename').textContent));
            else status('Se canceló la apertura. Se conservó tu diagrama actual.');
        } catch (error) { await alertMessage(error.message, 'No se pudo abrir el flow'); }
    }
    openIncomingFile();
    document.fonts.ready.then(() => {
        if (commentEditor) { fitCommentary(commentEditor.input.closest('.pmt-node'), commentEditor.node, commentEditor.input); extent(); }
        else if (!gesture) render();
    });
    // Monitor idle pages too. A connection never starts or resumes a flow.
    connectSocket().catch(error => status(error.message));
})();
