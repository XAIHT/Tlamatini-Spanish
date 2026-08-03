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
// agent_page_init.js  –  Initialization, event wiring & actions
// ============================================================
/* global syncClearContextMenuState, isMultiTurnEnabled, applyStoredMultiTurnState, multiTurnCheckbox, persistMultiTurnState, isExecReportEnabled, applyStoredExecReportState, execReportCheckbox, persistExecReportState, isAcpxEnabled, applyStoredAcpxState, acpxCheckbox, persistAcpxState, isAskExecsEnabled, applyStoredAskExecsState, syncAskExecsAvailability, askExecsCheckbox, persistAskExecsState, isStepByStepEnabled, applyStoredStepByStepState, stepByStepCheckbox, persistStepByStepState, dismissExecPermissionDialogForRuntimeProceed, dismissExecPermissionDialogSilently, openAccessKeysWizardDialog */

// --- Prevent accidental close during long operations ---
window.addEventListener('beforeunload', (event) => {
    if (inLongOperation) {
        event.preventDefault();
        event.returnValue = '';
        sendPostBeacon('/agent/clear_session_state/'); // eslint-disable-line no-undef
        console.log('--- Page closing during long operation: Sent session cleanup via beacon');
    }
});

// ----------------------------------------------------------------
// Top-level actions
// ----------------------------------------------------------------

function Reconnect(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();
    if (reConnectEnabled === false) {
        console.log("Reconnect is not allowed at this moment...");
        return;
    }
    if (!isChatSocketOpen()) {
        console.log("--- WebSocket is closed, reloading page to rebuild the live session.");
        window.location.reload();
        return;
    }
    reConnectEnabled = true;
    reConnectButton.disabled = true;

    setTitleBusy(false);
    contextEnabled = true;
    contextButton.style.backgroundColor = "darkgreen";
    contextButton.disabled = false;
    contextButtonClicked = false;
    contextButton.textContent = "Usar como contexto";
    chatInput.readOnly = false;
    chatInput.style.backgroundColor = '#40414F';
    const existingSpinner = document.getElementById(spinnerId);

    if (existingSpinner && existingSpinner.parentNode) {
        existingSpinner.parentNode.removeChild(existingSpinner);
    }

    agents = [];
    tools = [];
    skills = [];
    openEnabled = true;
    reConnectEnabled = true;
    contextEnabled = true;
    cleanCanvasEnabled = true;
    contextButtonClicked = false;
    canvasSettedAsContext = false;
    reConnectButton.disabled = false;
    contextMenuButton.removeAttribute('disabled', 'disabled');
    contextMenuButton.setAttribute('data-bs-toggle', 'dropdown');
    mcpsMenuButton.removeAttribute('disabled', 'disabled');
    mcpsMenuButton.setAttribute('data-bs-toggle', 'dropdown');
    agentsMenuButton.removeAttribute('disabled', 'disabled');
    agentsMenuButton.setAttribute('data-bs-toggle', 'dropdown');

    contextButton.textContent = "Usar como contexto";
    contextButton.disabled = false;
    contextButton.style.backgroundColor = "darkgreen";

    if (canvasLoaded === true) {
        enableCanvasButtons();
    } else {
        disableCanvasButtons();
    }

    chatSubmitButton.textContent = 'Enviar';
    inLongOperation = false;
    userCancelledRun = false;   // full UI reset — re-arm the normal busy behaviour
    actualContextDir = null;
    updateViewContextDirMenuState();
    console.log("--- actualContextDir reset to null on reconnect.");
    if (!sendChatSocketMessage(JSON.stringify({
        'type': 'reconnect-llm-agent',
        'message': 'reconnect'
    }))) {
        return;
    }
    clearContextEnabled = false;
    clearContextButton.setAttribute("style", "display: none !important;");
    contextDataSpan.innerText = "<<<" + "..." + ">>>  ";
    contextInfoDiv.setAttribute("class", "col-md-2 col-lg-3 col-xl-4 col-xxl-4 flex-nowrap p-0 m-0 context-info-invisible");
    console.log("--- Reconnect message sent to server.");
}

function CleanHistory(e) {
    e.preventDefault();
    if (cleanHistoryEnabled === false) {
        console.log("Clean history is not allowed at this moment...");
        return;
    }

    const callbackOnCont = () => {
        const cleanHistorySent = sendChatSocketMessage(JSON.stringify({
            'type': 'clean-history-and-reconnect',
            'message': 'clean-history'
        }));
        if (!cleanHistorySent) {
            return false;
        }

        chatLog.innerHTML = '';
        chatHistory = [];
        historyIndex = 0;
        tempInput = '';
        sessionStorage.removeItem('chatHistory');

        setTitleBusy(false);
        agents = [];
        tools = [];
        openEnabled = true;
        reConnectEnabled = true;
        contextEnabled = true;
        cleanCanvasEnabled = true;
        cleanHistoryEnabled = true;
        contextButtonClicked = false;
        canvasSettedAsContext = false;
        reConnectButton.disabled = false;
        cleanHistoryButton.disabled = false;
        cleanHistoryButton.style.backgroundColor = "darkgreen";
        contextMenuButton.removeAttribute('disabled', 'disabled');
        contextMenuButton.setAttribute('data-bs-toggle', 'dropdown');
        mcpsMenuButton.removeAttribute('disabled', 'disabled');
        mcpsMenuButton.setAttribute('data-bs-toggle', 'dropdown');
        agentsMenuButton.removeAttribute('disabled', 'disabled');
        agentsMenuButton.setAttribute('data-bs-toggle', 'dropdown');

        contextButton.textContent = "Usar como contexto";
        contextButton.disabled = false;
        contextButton.style.backgroundColor = "darkgreen";

        if (canvasLoaded === true) {
            enableCanvasButtons();
        } else {
            disableCanvasButtons();
        }

        chatSubmitButton.textContent = 'Enviar';
        inLongOperation = false;
        actualContextDir = null;
        updateViewContextDirMenuState();
        clearContextEnabled = false;
        clearContextButton.setAttribute("style", "display: none !important;");
        contextDataSpan.innerText = "<<<" + "..." + ">>>  ";
        contextInfoDiv.setAttribute("class", "col-md-2 col-lg-3 col-xl-4 col-xxl-4 flex-nowrap p-0 m-0 context-info-invisible");

        console.log("--- Clean history message sent to server.");
        return true;
    };

    const callbackOnCanc = () => {
        confirmationByUser = false;
        console.log("Clean history was dismissed...");
        return false;
    };

    confirmationByUser = false;
    preRenderConfirmationDialog('Confirmación...', '¿Seguro que quieres limpiar el historial?', 'Esto borra el contexto actual que sigue Tlamatini y reinicia la conversación.', callbackOnCont, callbackOnCanc);
    renderConfirmationDialog();
}

function CancelAllAndLogout(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();

    const callbackOnCont = () => {
        try {
            sendChatSocketMessage(JSON.stringify({
                'type': 'cancel-all',
                'message': 'cancel'
            }));
            confirmationByUser = true;
            console.log("--- Cancel all message sent to server.");
        } catch (err) {
            console.error('Failed to send cancel message:', err);
        } finally {
            const addr = logoutButton.getAttribute('param');
            const debouncedFunction = debounce(() => { window.top.location.href = addr; });
            debouncedFunction();
        }
        return true;
    };

    const callbackOnCanc = () => {
        confirmationByUser = false;
        console.log("Cancel and Logout was dismissed...");
        return false;
    };

    if (inLongOperation === true) {
        confirmationByUser = false;
        preRenderConfirmationDialog('Confirmación...', '¿Seguro que quieres cancelar ahora?', 'Cancelar rompe la operación en curso y descarta el contexto actual', callbackOnCont, callbackOnCanc);
        renderConfirmationDialog();
    } else {
        const logoutBtn = document.getElementById('logout-button');
        const addr = logoutBtn.getAttribute('param');
        const debouncedFunction = debounce(() => { window.top.location.href = addr; });
        debouncedFunction();
    }
}

function OpenOmissionsDialog(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();

    if (inLongOperation === true) {
        console.log("Dialog omissions can't be opened during a long operation...");
        return;
    }

    const callbackOnCont = () => {
        try {
            fileTypeOmissions = omissionContentInput.value;
            sendChatSocketMessage(JSON.stringify({
                'type': 'set-file-omissions',
                'message': fileTypeOmissions
            }));
            console.log("--- Sent set-file-omissions message sent to server.");
        } catch (err) {
            console.error('--- Failed to send omissions message:', err);
        }
        return true;
    };

    const callbackOnCanc = () => {
        console.log("--- Omissions dialog was dismissed...");
        return false;
    };

    preRenderOmissionsDialog("Omisiones...", "Especifica las extensiones o los nombres de archivo a omitir, separados por coma", "La omisión hace que Tlamatini ignore por completo esos archivos en el proceso de retrieval.", callbackOnCont, callbackOnCanc);
    renderOmissionsDialog();
}

function OpenMcpsDialog(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();

    if (inLongOperation === true) {
        console.log("Dialog mcps can't be opened during a long operation...");
        return;
    }

    const callbackOnCont = () => {
        try {
            const mcp1Checked = $("#mcp-1").is(":checked");
            const mcp2Checked = $("#mcp-2").is(":checked");
            const message2send = JSON.stringify({
                'type': 'set-mcps',
                'message': '1=' + label_mcp1.innerText + "=" + mcp1Checked + "," + '2=' + label_mcp2.innerText + "=" + mcp2Checked
            });
            sendChatSocketMessage(message2send);
            console.log("Message sent to socket: ", message2send);
            console.log("--- Sent set-mcps message sent to server.");
        } catch (err) {
            console.error('--- Failed to send mcps message:', err);
        }

        console.log("--->>> tools: ", tools);
        if (tools.length > 0) {
            let completeTools = "";
            for (const tool of tools) {
                if (!tool || !tool.name) {
                    continue;
                }
                const checked = $("#" + tool.name).is(":checked");
                completeTools = completeTools + tool.name + "=" + tool.description + "=" + checked + ",";
            }
            console.log("--->>> complete tools: ", completeTools);
            sendChatSocketMessage(JSON.stringify({
                'type': 'set-tools',
                'message': completeTools
            }));
            console.log("--- Sent set-tools message sent to server, complete tools: ", completeTools);
        }
        return true;
    };

    const callbackOnCanc = () => {
        console.log("--- Mcps dialog was dismissed...");
        return false;
    };

    preRenderMcpsDialog("Configurar MCPs...", "Los MCPs le dan información adicional a Tlamatini.", "Especifica los Rag-MCPs que se van a usar:", "Especifica los Tool-MCPs que se van a usar:", callbackOnCont, callbackOnCanc);
    renderMcpsDialog();
}

function OpenAgentsDialog(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();

    if (inLongOperation === true) {
        console.log("Dialog Agents can't be opened during a long operation...");
        return;
    }

    const callbackOnCont = () => {
        console.log("--->>> agents: ", agents);
        if (agents.length > 0) {
            let completeAgents = "";
            for (const agent of agents) {
                if (!agent || !agent.name) {
                    continue;
                }
                const checked = $("#" + agent.name).is(":checked");
                completeAgents = completeAgents + agent.name + "=" + agent.description + "=" + checked + ",";
            }
            console.log("--->>> complete agents: ", completeAgents);
            sendChatSocketMessage(JSON.stringify({
                'type': 'set-agents',
                'message': completeAgents
            }));
            console.log("--- Sent set-agents message sent to server, complete agents: ", completeAgents);
        }
        return true;
    };

    const callbackOnCanc = () => {
        console.log("--- Agents dialog was dismissed...");
        return false;
    };

    preRenderAgentsDialog("Configurar Agents...", "Los Agents le dan información adicional a Tlamatini.", "Especifica los Rag-Agents que se van a usar:", callbackOnCont, callbackOnCanc);
    renderAgentsDialog();
}

// ----------------------------------------------------------------
// ACPX-Skills dropdown handlers — see skills_dialog.js for the
// jQuery-UI dialog implementations they delegate to.
// ----------------------------------------------------------------
function OpenSkillsConfigureDialog(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();
    if (inLongOperation === true) {
        console.log("Dialog Skills can't be opened during a long operation...");
        return;
    }
    const callbackOnCont = () => {
        if (!Array.isArray(skills) || skills.length === 0) {
            console.log("--- No skills to save.");
            return true;
        }
        // Payload mirrors set-tools / set-agents: `name=description=true/false,...`
        // The skill name is the SKILL.md frontmatter `name` directly (no
        // `skill-N` prefix because the Skill DB row keys on `name`).
        let completeSkills = "";
        for (const skill of skills) {
            if (!skill || !skill.name) continue;
            const checked = $("#skill-checkbox-" + CSS.escape(skill.name)).is(":checked");
            const desc = (skill.description || '').replace(/[,=]/g, ' ');
            completeSkills += skill.name + "=" + desc + "=" + checked + ",";
        }
        sendChatSocketMessage(JSON.stringify({
            'type': 'set-skills',
            'message': completeSkills
        }));
        console.log("--- Sent set-skills message:", completeSkills);
        return true;
    };
    const callbackOnCanc = () => false;
    preRenderSkillsConfigureDialog(
        "Configurar ACPX-Skills...",
        "Activa o desactiva los packages SKILL.md. Los skills desactivados no aparecen en list_skills y invoke_skill los rechaza.",
        callbackOnCont, callbackOnCanc
    );
    renderSkillsConfigureDialog();
}

function OpenSkillsBrowseDialog(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();
    if (inLongOperation === true) {
        console.log("Dialog Skills-Browse can't be opened during a long operation...");
        return;
    }
    openSkillsBrowseDialog();
}

function OpenSkillsDiagnosticsDialog(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();
    if (inLongOperation === true) {
        console.log("Dialog Skills-Diagnostics can't be opened during a long operation...");
        return;
    }
    openSkillsDiagnosticsDialog();
}

function ReloadSkillRegistry(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();
    reloadSkillRegistry();
}

// ----------------------------------------------------------------
// Chat form submit handler
// ----------------------------------------------------------------

document.getElementById('chat-form').onsubmit = function (e) {
    e.preventDefault();

    const callbackOnCont = () => {
        console.log("--- Cancel confirmed by user, sending cancel-current message...");

        const cancelMsg = JSON.stringify({
            'type': 'cancel-current',
            'message': 'cancel'
        });
        console.log("--- Sending cancel message:", cancelMsg);
        if (!sendChatSocketMessage(cancelMsg, 'Se perdió la conexión en vivo. Usa Reconectar o refresca la página antes de cancelar el request actual.')) {
            return;
        }
        console.log("--- cancel-current message sent to server successfully");
        // The cancel is now in flight. From here on, ANY late self-healing "Tactic #…"
        // status frame belongs to a run the user has already killed and must NOT be
        // allowed to re-disable the controls. Set BEFORE the UI reset below so no late
        // frame can race it. Cleared on the next submit.
        userCancelledRun = true;
        // Close any OPEN Ask-Execs Proceed/Deny prompt. The backend auto-denies it
        // (the run is latched dead), so leaving it up would force the user to answer a
        // question that has already been answered — and the dialog is modal with no
        // Esc and no X, so a button is her only way out. (Angela hit this: "I had to
        // push Deny, but the denial was already done.") No decision frame is sent.
        if (typeof dismissExecPermissionDialogSilently === 'function') {
            dismissExecPermissionDialogSilently('cancelled');
        }
        const debouncedFunction = debounce(unsetContextButton);
        debouncedFunction();
        // Reset UI state after cancellation
        chatInput.readOnly = false;
        chatInput.style.backgroundColor = '#40414F';
        if (chatSubmitButton) chatSubmitButton.textContent = 'Enviar';
        chatSubmitButton.disabled = false;
        inLongOperation = false;
        lapseLoadingContext = false;
        const spinner = document.getElementById('wait-spinner');
        if (spinner && spinner.parentNode) spinner.parentNode.removeChild(spinner);
        contextEnabled = true;
        contextMenuButton.removeAttribute('disabled');
        contextMenuButton.setAttribute('data-bs-toggle', 'dropdown');
        mcpsMenuButton.removeAttribute('disabled', 'disabled');
        mcpsMenuButton.setAttribute('data-bs-toggle', 'dropdown');
        agentsMenuButton.removeAttribute('disabled', 'disabled');
        agentsMenuButton.setAttribute('data-bs-toggle', 'dropdown');
        cleanCanvasButton.style.backgroundColor = "darkgreen";
        cleanCanvasButton.disabled = false;
        cleanCanvasEnabled = true;
        reopenOpenCanvasButton.style.backgroundColor = "darkgreen";
        reopenOpenCanvasButton.disabled = false;
        copyCanvasButton.style.backgroundColor = "darkgreen";
        copyCanvasButton.disabled = false;
        clearContextEnabled = false;
        clearContextButton.setAttribute("style", "display: none !important;");
        setContextText("<<<" + "..." + ">>>  ");
        contextInfoDiv.setAttribute("class", "col-md-2 col-lg-3 col-xl-4 col-xxl-4 flex-nowrap p-0 m-0 context-info-invisible");
        actualContextDir = null;
        updateViewContextDirMenuState();
        console.log("--- actualContextDir reset to null on cancel.");
    };

    const callbackOnCanc = () => {
        console.log("Cancel was dismissed...");
        return false;
    };

    if ((inLongOperation === true && (chatSubmitButton && chatSubmitButton.textContent === 'Cancelar')) || lapseLoadingContext === true) {
        console.log("--- Cancel dialog triggered. inLongOperation: " + inLongOperation + ", lapseLoadingContext: " + lapseLoadingContext);
        confirmationByUser = false;
        preRenderConfirmationDialog('Confirmación...', '¿Seguro que quieres cancelar ahora?', 'Cancelar rompe la operación en curso y descarta el contexto actual', callbackOnCont, callbackOnCanc);
        renderConfirmationDialog();
    } else {
        const rawMessage = chatInput.value;
        const message = rawMessage;
        console.log("message: " + message);
        if (rawMessage.trim() === '') return;
        const messageSent = sendChatSocketMessage(JSON.stringify({
            'message': rawMessage,
            'multi_turn_enabled': isMultiTurnEnabled(),
            'exec_report_enabled': isExecReportEnabled(),
            'acpx_enabled': isAcpxEnabled(),
            'ask_execs_enabled': isAskExecsEnabled(),
            'step_by_step_enabled': isStepByStepEnabled()
        }));
        if (!messageSent) {
            return;
        }
        // A NEW run owns the UI now — re-arm the normal busy behaviour. (A FAILED send
        // deliberately leaves the latch as it was.) Forgetting this line would leave
        // the busy UI permanently disabled after the first cancel: the button would
        // never show "Cancel" again for any later request.
        userCancelledRun = false;
        chatHistory.push(rawMessage);
        historyIndex = chatHistory.length;
        tempInput = '';
        try {
            sessionStorage.setItem('chatHistory', JSON.stringify(chatHistory));
            sessionStorage.setItem('historyIndex', String(historyIndex));
        } catch (err) {
            console.error("Catched error in onsubmit(): " + err);
        }
        chatInput.value = '';
    }
};

// ----------------------------------------------------------------
// window.onload  –  wire up all event listeners
// ----------------------------------------------------------------

window.onload = () => {
    chatLog.scrollTop = chatLog.scrollHeight;
    updateViewContextDirMenuState();
    applyStoredMultiTurnState();
    applyStoredExecReportState();
    applyStoredAcpxState();
    applyStoredAskExecsState();
    applyStoredStepByStepState();
    syncAskExecsAvailability();
    syncExecReportAvailability();
    if (openButton) {
        openButton.addEventListener('click', (e) => {
            e.preventDefault();
            openCanvas();
        });
    }
    if (reopenOpenCanvasButton) {
        reopenOpenCanvasButton.addEventListener('click', (e) => {
            e.preventDefault();
            if (openEnabled === false) {
                console.log("Reopen canvas is not allowed at this moment...");
                return;
            }
            reopenCanvas();
        });
    }
    if (setDirContextMenu) {
        setDirContextMenu.addEventListener('click', async (e) => {
            e.preventDefault();
            if (contextEnabled === false) {
                return;
            }
            try {
                // Native server-side picker returns the FULL absolute path,
                // so a project nested any number of levels deep under the
                // application root loads correctly (the old
                // window.showDirectoryPicker() only sent the leaf folder name
                // and broke every non-direct-child directory).
                const chosenPath = await _pickContextDirectory();
                if (!chosenPath) {
                    // User canceled, or picker unavailable and no path typed.
                    return;
                }
                const sent = sendChatSocketMessage(JSON.stringify({
                    'type': 'set-directory-as-context',
                    'message': chosenPath
                }));
                if (!sent) {
                    return;
                }
                const dirLabel = chosenPath.split(/[\\/]/).filter(Boolean).pop() || chosenPath;
                actualContextDir = null;
                updateViewContextDirMenuState();
                clearContextEnabled = false;
                clearContextButton.setAttribute("style", "display: none !important;");
                setContextText("<<< contexto de directorio pendiente: " + dirLabel + " >>>");
                contextInfoDiv.setAttribute("class", "col-md-2 col-lg-3 col-xl-4 col-xxl-4 flex-nowrap p-0 m-0 context-info-visible");
                console.log("--- Waiting for server confirmation of directory context: " + chosenPath);
            } catch (err) {
                console.error("Catched error in listener of setDirContextMenu: " + err);
            }
        });
    }
    if (setFileContextMenu) {
        setFileContextMenu.addEventListener('click', async (e) => {
            e.preventDefault();
            if (contextEnabled === false) {
                return;
            }

            const callback2SetFileAsContext = () => {
                const type = "set-canvas-as-context";
                const codeRegex = /<<< ([\w.-]+) >>>/s;
                const result = filenameSpan.textContent.match(codeRegex);
                const content = textEditorCode.textContent;
                const tokensNumber = genericTokenCounting(content);
                console.log("--- The number of tokens in file is: " + tokensNumber);
                if (tokensNumber > maximalTheoricTokens) {
                    console.log("--- The number of tokens in file (if used as context) may not be completely processed by Tlamatini, it wont fit the context window.");
                    alert("Puede que Tlamatini no procese por completo todos los tokens del archivo cargado (si se usa como contexto): no caben en la ventana de contexto.");
                }
                console.log("--- The content is: " + content);
                if (result) {
                    const filename = result[1];
                    const sent = sendChatSocketMessage(JSON.stringify({
                        'type': type,
                        'message': filename,
                        'content': content
                    }));
                    if (!sent) {
                        return;
                    }
                    clearContextEnabled = false;
                    clearContextButton.setAttribute("style", "display: none !important;");
                    actualContextDir = null;
                    updateViewContextDirMenuState();
                    setContextText("<<< contexto pendiente: " + filename + " >>>");
                    contextInfoDiv.setAttribute("class", "col-md-2 col-lg-3 col-xl-4 col-xxl-4 flex-nowrap p-0 m-0 context-info-visible");
                    setContextButton();
                    console.log("--- Waiting for server confirmation of file context: " + filename);
                    console.log("...Rebuild rag action sent.");
                }
            };
            loadFileContent(true, callback2SetFileAsContext);
        });
    }
    if (viewContextDirInCanvasMenu) {
        viewContextDirInCanvasMenu.addEventListener('click', async (e) => {
            e.preventDefault();
            if (contextEnabled === false) {
                return;
            }
            if (actualContextDir === null || actualContextDir === '') {
                console.log("--- actualContextDir is null or empty, menu action ignored.");
                return;
            }
            if (actualContextDir !== null) {
                try {
                    const sent = sendChatSocketMessage(JSON.stringify({
                        'type': 'view-context-dir-in-canvas',
                        'message': actualContextDir
                    }));
                    if (!sent) {
                        return;
                    }
                    console.log("--- actualContextDir is: " + actualContextDir + ", message 'view-context-dir-in-canvas' has been sent.");
                    return;
                } catch (err) {
                    console.error("--- Catched error in listener of viewContextDirInCanvasMenu: " + err);
                }
            }
            if (actualContextDir == null)
                console.log("--- actualContextDir is null, message 'view-context-dir-in-canvas' not sent.");
        });
    }
    if (clearContextButton) {
        clearContextButton.addEventListener('click', async (e) => {
            e.preventDefault();
            ClearContext(e);
        });
    }
    if (cleanCanvasButton) {
        cleanCanvasButton.addEventListener('click', (e) => {
            e.preventDefault();
            if (cleanCanvasEnabled === false) {
                return;
            }
            cleanCanvas();
        });
    }
    if (cleanHistoryButton) {
        cleanHistoryButton.addEventListener('click', (e) => {
            CleanHistory(e);
        });
    }
    const initialDataScript = document.getElementById('initial_messages');
    if (initialDataScript && initialDataScript.textContent) {
        try {
            const initialMessages = JSON.parse(initialDataScript.textContent);
            renderInitialMessages(initialMessages);
            if (Array.isArray(initialMessages)) {
                chatHistory = initialMessages
                    .filter(m => m && m.username === userUsername && typeof m.message === 'string' && m.message.trim() !== '')
                    .map(m => m.message);
                historyIndex = chatHistory.length;
            }
            try {
                const stored = sessionStorage.getItem('chatHistory');
                if (stored) {
                    const parsed = JSON.parse(stored);
                    if (Array.isArray(parsed)) {
                        chatHistory = parsed;
                        const storedIndex = parseInt(sessionStorage.getItem('historyIndex') || String(parsed.length), 10);
                        historyIndex = isNaN(storedIndex) ? parsed.length : storedIndex;
                    }
                }
            } catch (err) {
                console.error("Catched error at getItem of ChatHistory: " + err);
            }
        } catch (e) {
            console.error('Failed to parse initial messages JSON:', e);
        }
    }
    rotateTitle();

    $('#internetEnabled').click(function () {
        const isChecked = this.checked;
        console.log('InternetEnabled is:', isChecked);
        if (isChecked) {
            sendChatSocketMessage(JSON.stringify({
                'type': 'enable-llm-internet-access',
                'message': ''
            }));
        } else {
            sendChatSocketMessage(JSON.stringify({
                'type': 'disable-llm-internet-access',
                'message': ''
            }));
        }
    });
    if (multiTurnCheckbox) {
        multiTurnCheckbox.addEventListener('change', function () {
            persistMultiTurnState(!!this.checked);
            // Ask-Execs AND Exec-report availability both depend on Multi-Turn —
            // re-sync the enabled/disabled state of both checkboxes on every toggle.
            syncAskExecsAvailability();
            syncExecReportAvailability();
        });
    }
    if (execReportCheckbox) {
        execReportCheckbox.addEventListener('change', function () {
            persistExecReportState(!!this.checked);
        });
    }
    if (acpxCheckbox) {
        acpxCheckbox.addEventListener('change', function () {
            persistAcpxState(!!this.checked);
        });
    }
    if (askExecsCheckbox) {
        askExecsCheckbox.addEventListener('change', function () {
            const enabled = !!this.checked;
            persistAskExecsState(enabled);
            // If a Multi-Turn run is already in flight, propagate the new
            // choice to the live broker so it takes effect for the REMAINDER
            // of that run (uncheck → stop asking / auto-proceed; re-check →
            // resume asking). Harmless if no run is in flight — the backend
            // no-ops without a registered broker.
            if (inLongOperation === true) {
                sendChatSocketMessage(JSON.stringify({
                    // 'message' is required by the consumer's receive() (it
                    // reads text_data_json['message'] unconditionally).
                    message: 'set-ask-execs-runtime',
                    type: 'set-ask-execs-runtime',
                    ask_execs_runtime_enabled: enabled
                }));
                // When relaxing mid-run, dismiss any open permission prompt so
                // the user isn't left staring at a dialog the backend has
                // already auto-proceeded.
                if (!enabled && typeof dismissExecPermissionDialogForRuntimeProceed === 'function') {
                    dismissExecPermissionDialogForRuntimeProceed();
                }
            }
        });
    }
    if (stepByStepCheckbox) {
        stepByStepCheckbox.addEventListener('change', function () {
            const enabled = !!this.checked;
            persistStepByStepState(enabled);
            if (enabled && multiTurnCheckbox && !multiTurnCheckbox.checked) {
                multiTurnCheckbox.checked = true;
                persistMultiTurnState(true);
                syncAskExecsAvailability();
                syncExecReportAvailability();
            }
        });
    }
    syncClearContextMenuState();
    updateViewContextDirMenuState();

    // Detect installed apps for "Open in..." dropdown
    detectInstalledApps();
};

// ----------------------------------------------------------------
// Ollama helper
// ----------------------------------------------------------------

function getConfiguredOllamaBaseUrl() {
    const ollamaConfigScript = document.getElementById('ollama_config');
    let ollamaBaseUrl = 'http://localhost:11434';

    if (ollamaConfigScript && ollamaConfigScript.textContent) {
        try {
            ollamaBaseUrl = JSON.parse(ollamaConfigScript.textContent);
        } catch (e) {
            console.error('Error parsing ollama_base_url from config:', e);
        }
    }
    return ollamaBaseUrl;
}

/**
 * Fetch the model catalog from the configured Ollama server and return the
 * list of model names as a Promise. Resolves to ``string[]`` on success.
 * Rejects when the server is unreachable or returns a malformed payload —
 * callers use that rejection to surface the "Ollama not running" alert.
 *
 * The function ALSO keeps its legacy side effect of logging the catalog to
 * the console so existing diagnostic flows that called it without awaiting
 * the result still work the same way.
 */
function listOllamaModels(options = {}) {
    const { silent = false, overrideBaseUrl = null, timeoutMs = 10000 } = options;
    const ollamaBaseUrl = overrideBaseUrl || getConfiguredOllamaBaseUrl();

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    return fetch(`${ollamaBaseUrl}/api/tags`, { signal: controller.signal })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ollama returned HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data || !Array.isArray(data.models)) {
                throw new Error('Ollama response has no "models" array');
            }
            const names = data.models
                .map(m => (m && typeof m.name === 'string') ? m.name : null)
                .filter(n => !!n);
            if (!silent) {
                console.log('Available Ollama models:');
                names.forEach(n => console.log(" - " + n));
            }
            return names;
        })
        .finally(() => clearTimeout(timer));
}

// ----------------------------------------------------------------
// Config dialog handlers (Models / URLs)
// ----------------------------------------------------------------

let _configModelsBaseline = null;
let _configUrlsBaseline = null;

function _snapshotConfigValues(values) {
    const snapshot = {};
    Object.keys(values || {}).forEach(key => {
        snapshot[key] = String(values[key] == null ? '' : values[key]);
    });
    return snapshot;
}

function _configValuesDiffer(baseline, current) {
    if (!baseline || !current) return false;
    const keys = new Set([...Object.keys(baseline), ...Object.keys(current)]);
    for (const key of keys) {
        const a = String(baseline[key] == null ? '' : baseline[key]);
        const b = String(current[key] == null ? '' : current[key]);
        if (a !== b) return true;
    }
    return false;
}

function _showReconnectRequiredAfterDialogClose() {
    setTimeout(() => {
        preRenderReconnectRequiredDialog(
            'Se requiere reconexión...',
            'Debes ejecutar una reconexión (Reconectar) para leer/aplicar los nuevos valores configurados.',
            'Presiona el botón Reconectar del toolbar para aplicar los cambios a la sesión en vivo.'
        );
        renderReconnectRequiredDialog();
    }, 100);
}

async function _loadConfigSectionValues(section) {
    const response = await fetch(`/agent/load_config_section/${section}/`, {
        credentials: 'same-origin'
    });
    if (!response.ok) {
        throw new Error(`Failed to load ${section} config: HTTP ${response.status}`);
    }
    const data = await response.json();
    if (!data || data.success !== true || !data.values) {
        throw new Error(`Failed to load ${section} config: bad payload`);
    }
    return data.values;
}

function _populateConfigForm(form, values) {
    if (!form) return;
    const inputs = form.querySelectorAll('input[data-config-key]');
    inputs.forEach(input => {
        const key = input.getAttribute('data-config-key');
        input.value = (values && Object.prototype.hasOwnProperty.call(values, key)) ? String(values[key]) : '';
        input.classList.remove('config-form-invalid');
    });
}

function _collectConfigFormValues(form) {
    const values = {};
    if (!form) return values;
    const inputs = form.querySelectorAll('input[data-config-key]');
    inputs.forEach(input => {
        const key = input.getAttribute('data-config-key');
        values[key] = input.value.trim();
    });
    return values;
}

function _markInvalidInputs(form, invalidKeys) {
    if (!form) return;
    const inputs = form.querySelectorAll('input[data-config-key]');
    inputs.forEach(input => {
        const key = input.getAttribute('data-config-key');
        if (invalidKeys.has(key)) {
            input.classList.add('config-form-invalid');
        } else {
            input.classList.remove('config-form-invalid');
        }
    });
}

async function _saveConfigSection(endpoint, payload) {
    const response = await fetch(endpoint, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(payload)
    });
    let body = null;
    try {
        body = await response.json();
    } catch (_e) {
        // Non-JSON body (e.g. 500 HTML page); fall through with body=null.
    }
    if (!response.ok) {
        const err = new Error(`No se pudo guardar: HTTP ${response.status}`);
        err.body = body;
        throw err;
    }
    if (!body || body.success !== true) {
        const err = new Error('El server no pudo guardar la configuración');
        err.body = body;
        throw err;
    }
    return body;
}

function OpenConfigModelsDialog(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();
    if (inLongOperation === true) {
        console.log("Config Models dialog can't be opened during a long operation...");
        return;
    }

    _loadConfigSectionValues('models')
        .then(values => {
            _populateConfigForm(configModelsForm, values);
            _configModelsBaseline = _snapshotConfigValues(_collectConfigFormValues(configModelsForm));
            preRenderConfigModelsDialog(
                'Configurar Modelos...',
                'Elige el model de Ollama que usa cada subsistema.',
                'Cada model ya debe existir en el catálogo de Ollama antes de guardar.'
            );
            renderConfigModelsDialog();
        })
        .catch(err => {
            console.error('Failed to load Models config:', err);
            alert('No pude cargar la configuración actual desde el server. Inténtalo otra vez.');
        });
}

function OpenConfigUrlsDialog(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();
    if (inLongOperation === true) {
        console.log("Config URLs dialog can't be opened during a long operation...");
        return;
    }

    _loadConfigSectionValues('urls')
        .then(values => {
            _populateConfigForm(configUrlsForm, values);
            _configUrlsBaseline = _snapshotConfigValues(_collectConfigFormValues(configUrlsForm));
            preRenderConfigUrlsDialog(
                'Configurar URLs...',
                'Define las URLs base, los hosts y los ports que usa Tlamatini.',
                'Las URLs deben incluir un scheme http(s):// o ws(s)://; los ports van de 1 a 65535.'
            );
            renderConfigUrlsDialog();
        })
        .catch(err => {
            console.error('Failed to load URLs config:', err);
            alert('No pude cargar la configuración actual desde el server. Inténtalo otra vez.');
        });
}

function OpenAccessKeysWizard(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();
    if (inLongOperation === true) {
        console.log("Access Keys Wizard can't be opened during a long operation...");
        return;
    }
    if (typeof openAccessKeysWizardDialog !== 'function') {
        alert('El Access Keys Wizard no está disponible en este build.');
        return;
    }
    openAccessKeysWizardDialog();
}

/**
 * Validate the URLs form client-side, by data-config-type. Returns
 * { ok, errors } where errors is { key: humanReason } when ok is false.
 */
function _validateUrlsForm(form) {
    const errors = {};
    if (!form) return { ok: false, errors };
    const inputs = form.querySelectorAll('input[data-config-key]');
    inputs.forEach(input => {
        const key = input.getAttribute('data-config-key');
        const type = input.getAttribute('data-config-type') || 'url';
        const raw = (input.value || '').trim();
        if (!raw) {
            errors[key] = 'no puede estar vacío';
            return;
        }
        if (type === 'url') {
            let parsed;
            try {
                parsed = new URL(raw);
            } catch (_e) {
                errors[key] = 'no es una URL válida';
                return;
            }
            const scheme = (parsed.protocol || '').replace(':', '').toLowerCase();
            if (!['http', 'https', 'ws', 'wss'].includes(scheme)) {
                errors[key] = 'debe usar un scheme http(s):// o ws(s)://';
                return;
            }
            if (!parsed.host) {
                errors[key] = 'debe incluir un host';
                
            }
        } else if (type === 'host') {
            const ipv4 = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
            const hostname = /^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(?:\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$/;
            if (!ipv4.test(raw) && !hostname.test(raw)) {
                errors[key] = 'debe ser un hostname (p. ej. localhost) o una dirección IPv4';
            }
        } else if (type === 'port') {
            const port = Number(raw);
            if (!Number.isInteger(port) || port < 1 || port > 65535) {
                errors[key] = 'debe ser un número entero entre 1 y 65535';
            }
        }
    });
    return { ok: Object.keys(errors).length === 0, errors };
}

function _labelForConfigInput(input) {
    if (!input || !input.id) return '';
    const label = document.querySelector(`label[for="${input.id}"]`);
    return label ? label.textContent.trim() : input.id;
}

function _formatErrorsForAlert(form, errors) {
    const lines = [];
    Object.keys(errors).forEach(key => {
        const input = form ? form.querySelector(`input[data-config-key="${key}"]`) : null;
        const label = input ? _labelForConfigInput(input) : key;
        lines.push(`  • ${label}: ${errors[key]}`);
    });
    return lines.join('\n');
}

/**
 * Save handler for the Models dialog. Returns a Promise that resolves to
 * ``true`` on success (so the dialog can close) or ``false`` on validation
 * failure (so the dialog stays open and the user can correct the inputs).
 */
async function _saveConfigModels() {
    const values = _collectConfigFormValues(configModelsForm);

    // 1) Basic non-empty check before bothering Ollama
    const invalidKeys = new Set();
    const emptyErrors = {};
    Object.keys(values).forEach(key => {
        if (!values[key]) {
            emptyErrors[key] = 'no puede estar vacío';
            invalidKeys.add(key);
        }
    });
    if (invalidKeys.size > 0) {
        _markInvalidInputs(configModelsForm, invalidKeys);
        alert('Los siguientes campos son obligatorios:\n\n' + _formatErrorsForAlert(configModelsForm, emptyErrors));
        return false;
    }

    // 2) Fetch the live Ollama catalog. If this fails, Ollama is likely down.
    let catalog;
    try {
        catalog = await listOllamaModels({ silent: true });
    } catch (err) {
        console.error('Failed to query Ollama for model catalog:', err);
        alert('No se pudo conectar con el Ollama server.\n\nAsegúrate de que el Ollama server esté corriendo antes de presionar "Guardar" otra vez.');
        return false;
    }

    if (!Array.isArray(catalog) || catalog.length === 0) {
        alert('El Ollama server respondió con un catálogo vacío.\n\nAsegúrate de tener al menos un model instalado en Ollama antes de presionar "Guardar" otra vez.');
        return false;
    }

    const catalogSet = new Set(catalog);

    // 3) Every model in the form must be in the catalog.
    const missing = {};
    Object.keys(values).forEach(key => {
        if (!catalogSet.has(values[key])) {
            missing[key] = `el model "${values[key]}" no está instalado en Ollama`;
            invalidKeys.add(key);
        }
    });
    if (Object.keys(missing).length > 0) {
        _markInvalidInputs(configModelsForm, invalidKeys);
        alert('Los siguientes models NO están instalados en Ollama:\n\n'
            + _formatErrorsForAlert(configModelsForm, missing)
            + '\n\nCorrígelos (o instálalos en Ollama) antes de presionar "Guardar" otra vez.');
        return false;
    }

    // 4) All validated — persist on the server.
    try {
        await _saveConfigSection('/agent/save_config_models/', values);
    } catch (err) {
        console.error('Failed to save Models config:', err);
        const serverErrors = err && err.body && err.body.errors;
        if (serverErrors && typeof serverErrors === 'object') {
            _markInvalidInputs(configModelsForm, new Set(Object.keys(serverErrors)));
            alert('La validación del servidor falló:\n\n' + _formatErrorsForAlert(configModelsForm, serverErrors));
        } else {
            alert('No se pudo guardar la configuración: ' + (err.message || 'error desconocido'));
        }
        return false;
    }

    _markInvalidInputs(configModelsForm, new Set());
    console.log('--- Saved Models config.');

    const changed = _configValuesDiffer(_configModelsBaseline, _snapshotConfigValues(values));
    _configModelsBaseline = null;
    if (changed) {
        _showReconnectRequiredAfterDialogClose();
    }
    return true;
}

/**
 * Save handler for the URLs dialog. Same return convention as Models.
 */
async function _saveConfigUrls() {
    const { ok, errors } = _validateUrlsForm(configUrlsForm);
    if (!ok) {
        _markInvalidInputs(configUrlsForm, new Set(Object.keys(errors)));
        alert('Los siguientes campos son inválidos:\n\n'
            + _formatErrorsForAlert(configUrlsForm, errors)
            + '\n\nCorrígelos antes de presionar "Guardar" otra vez.');
        return false;
    }

    const values = _collectConfigFormValues(configUrlsForm);
    // Send ports as numbers (the server is strict about it).
    const payload = { ...values };
    const portInputs = configUrlsForm.querySelectorAll('input[data-config-type="port"]');
    portInputs.forEach(input => {
        const key = input.getAttribute('data-config-key');
        payload[key] = Number(values[key]);
    });

    try {
        await _saveConfigSection('/agent/save_config_urls/', payload);
    } catch (err) {
        console.error('Failed to save URLs config:', err);
        const serverErrors = err && err.body && err.body.errors;
        if (serverErrors && typeof serverErrors === 'object') {
            _markInvalidInputs(configUrlsForm, new Set(Object.keys(serverErrors)));
            alert('La validación del servidor falló:\n\n' + _formatErrorsForAlert(configUrlsForm, serverErrors));
        } else {
            alert('No se pudo guardar la configuración: ' + (err.message || 'error desconocido'));
        }
        return false;
    }

    _markInvalidInputs(configUrlsForm, new Set());
    console.log('--- Saved URLs config.');

    const changed = _configValuesDiffer(_configUrlsBaseline, _snapshotConfigValues(values));
    _configUrlsBaseline = null;
    if (changed) {
        _showReconnectRequiredAfterDialogClose();
    }
    return true;
}

// ----------------------------------------------------------------
// DB -> Backup database dialog
// ----------------------------------------------------------------

let _backupDbValidationTimer = null;
let _backupDbInputListenerAttached = false;

function _setBackupDbStatus(text, kind) {
    if (!backupDbStatusElement) return;
    backupDbStatusElement.innerText = text || '';
    backupDbStatusElement.classList.remove('backup-db-status-ok', 'backup-db-status-warn', 'backup-db-status-error');
    if (kind === 'ok') {
        backupDbStatusElement.classList.add('backup-db-status-ok');
    } else if (kind === 'warn') {
        backupDbStatusElement.classList.add('backup-db-status-warn');
    } else if (kind === 'error') {
        backupDbStatusElement.classList.add('backup-db-status-error');
    }
}

async function _checkBackupDbDirectory(rawPath) {
    const url = '/agent/check_backup_directory/?path=' + encodeURIComponent(rawPath);
    const response = await fetch(url, {
        method: 'GET',
        credentials: 'same-origin'
    });
    let body = null;
    try {
        body = await response.json();
    } catch (_e) {
        // Non-JSON; fall through.
    }
    if (!response.ok) {
        const err = new Error(`No se pudo validar: HTTP ${response.status}`);
        err.body = body;
        throw err;
    }
    return body || {};
}

function _onBackupDbInputChanged() {
    if (!backupDbTargetDirInput) return;
    const raw = (backupDbTargetDirInput.value || '').trim();
    if (_backupDbValidationTimer) {
        clearTimeout(_backupDbValidationTimer);
        _backupDbValidationTimer = null;
    }
    backupDbTargetDirInput.classList.remove('config-form-invalid');
    if (!raw) {
        _setBackupDbStatus('', '');
        return;
    }
    _setBackupDbStatus('Verificando el path...', '');
    _backupDbValidationTimer = setTimeout(() => {
        _checkBackupDbDirectory(raw)
            .then(info => {
                const currentRaw = (backupDbTargetDirInput.value || '').trim();
                if (currentRaw !== raw) {
                    return; // user kept typing; a newer check will fire
                }
                if (info.kind === 'directory') {
                    _setBackupDbStatus('El directorio existe. Aquí se guardará db.sqlite3.', 'ok');
                    backupDbTargetDirInput.classList.remove('config-form-invalid');
                } else if (info.kind === 'file') {
                    _setBackupDbStatus('Especificaste un nombre de archivo — indica solo el directorio.', 'warn');
                    backupDbTargetDirInput.classList.add('config-form-invalid');
                } else {
                    _setBackupDbStatus('El directorio no existe.', 'error');
                    backupDbTargetDirInput.classList.add('config-form-invalid');
                }
            })
            .catch(err => {
                console.error('Failed to validate backup directory:', err);
                _setBackupDbStatus('No pude validar el directorio.', 'error');
            });
    }, 350);
}

// Friendly handler for a failed native picker. When the server reports the
// picker is unavailable (no GUI, or a frozen build whose Tcl/Tk data tree
// wasn't bundled — "Can't find a usable init.tcl"), we steer the user to
// the manual path field instead of dumping a raw multi-line Tcl error in
// an alert. The dialog stays usable either way: the path can always be
// typed. `inputEl` is the dialog's manual-path field; `kindLabel` is
// 'folder' or 'file' for the generic fallback wording.
function _notifyPickerUnavailable(body, fallbackReason, inputEl, kindLabel) {
    const unavailable = !!(body && body.picker_unavailable);
    const friendly = (body && body.message)
        || ('No pude abrir el ' + kindLabel + ' picker: '
            + (fallbackReason || 'error desconocido'));
    if (unavailable && inputEl) {
        // Make the manual path field the obvious next step.
        try { inputEl.focus(); } catch (_e) { /* ignore */ }
        try {
            inputEl.setAttribute(
                'placeholder',
                'El file browser nativo no está disponible — escribe aquí el path completo'
            );
        } catch (_e) { /* ignore */ }
    }
    alert(friendly);
}

// Native server-side folder picker for the chat "Set directory as context"
// menu. Returns the chosen ABSOLUTE path, or '' when the user canceled or no
// path was provided.
//
// Why not window.showDirectoryPicker(): that browser API only exposes the
// LEAF folder name (FileSystemDirectoryHandle.name), never the full path, so
// the server could only locate a directory that was a direct child of the
// runtime root. A project nested several levels deep
// (<app>/applications/proj/src) was impossible to load. The native Win32
// picker returns the real full path, which path_guard accepts for any depth
// under the application root. On hosts without a native dialog (e.g.
// non-Windows) we fall back to a manual path prompt.
async function _pickContextDirectory() {
    try {
        const response = await fetch('/agent/pick_context_directory/', {
            method: 'GET',
            credentials: 'same-origin'
        });
        let body = null;
        try { body = await response.json(); } catch (_e) { /* non-JSON */ }
        if (response.ok && body) {
            if (typeof body.path === 'string' && body.path) {
                return body.path;
            }
            if (body.canceled) {
                return '';  // user closed the dialog — respect it, no fallback
            }
            if (body.error || body.picker_unavailable) {
                return _promptForContextDirectory(body);
            }
        }
        if (!response.ok) {
            return _promptForContextDirectory(body);
        }
    } catch (err) {
        console.error('Native context-directory picker failed:', err);
        return _promptForContextDirectory(null);
    }
    return '';
}

// Manual-entry fallback used when the native folder picker is unavailable
// (no GUI / non-Windows). Mirrors the Set-DB / Backup-DB "type the path"
// guidance. Returns the trimmed path the user typed, or '' if canceled.
function _promptForContextDirectory(body) {
    const friendly = (body && body.message)
        || ('El file browser nativo no está disponible en esta máquina. '
            + 'Escribe o pega el path absoluto COMPLETO del directorio '
            + 'del proyecto (debe estar bajo la raíz de la aplicación).');
    try {
        const typed = window.prompt(friendly, '');
        return (typed && typed.trim()) ? typed.trim() : '';
    } catch (_e) {
        return '';
    }
}

// Browse button — opens a native folder picker on the server host and
// drops the chosen absolute path into the dialog's input so the existing
// live-validation pipeline (`_onBackupDbInputChanged`) classifies it.
async function _browseBackupDbDirectory() {  
    const browseBtn = document.getElementById('backup-db-browse-btn');
    if (!backupDbTargetDirInput) return;
    if (browseBtn) browseBtn.disabled = true;
    try {
        const response = await fetch('/agent/pick_backup_directory/', {
            method: 'GET',
            credentials: 'same-origin'
        });
        let body = null;
        try { body = await response.json(); } catch (_e) { /* non-JSON */ }
        if (!response.ok) {
            _notifyPickerUnavailable(body, 'HTTP ' + response.status, backupDbTargetDirInput, 'folder');
            return;
        }
        if (body && (body.error || body.picker_unavailable)) {
            _notifyPickerUnavailable(body, body.error, backupDbTargetDirInput, 'folder');
            return;
        }
        const chosen = (body && typeof body.path === 'string') ? body.path : '';
        if (!chosen) {
            // User canceled the dialog — leave the input untouched.
            return;
        }
        backupDbTargetDirInput.value = chosen;
        backupDbTargetDirInput.dispatchEvent(new Event('input', { bubbles: true }));
        backupDbTargetDirInput.focus();
    } catch (err) {
        console.error('Browse for backup directory failed:', err);
        alert('No pude abrir el folder picker: ' + (err.message || 'error de red'));
    } finally {
        if (browseBtn) browseBtn.disabled = false;
    }
}

function OpenBackupDbDialog(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();
    if (inLongOperation === true) {
        console.log("Backup DB dialog can't be opened during a long operation...");
        return;
    }

    if (backupDbTargetDirInput) {
        backupDbTargetDirInput.value = '';
        backupDbTargetDirInput.classList.remove('config-form-invalid');
        if (!_backupDbInputListenerAttached) {
            backupDbTargetDirInput.addEventListener('input', _onBackupDbInputChanged);
            _backupDbInputListenerAttached = true;
        }
    }
    _setBackupDbStatus('', '');

    preRenderBackupDbDialog(
        'Backup de la base de datos...',
        'Especifica el directorio destino donde se va a respaldar db.sqlite3.',
        'Indica SOLO el directorio — Tlamatini guarda el archivo como "db.sqlite3" para poder cargarlo de vuelta correctamente.'
    );
    renderBackupDbDialog();
}

async function _saveBackupDb() {  
    const raw = (backupDbTargetDirInput ? backupDbTargetDirInput.value : '').trim();

    if (!raw) {
        backupDbTargetDirInput.classList.add('config-form-invalid');
        _setBackupDbStatus('El directorio destino no puede estar vacío.', 'error');
        alert('El directorio destino no puede estar vacío.\n\nEspecifica un directorio existente antes de presionar "Backup".');
        return false;
    }

    let info;
    try {
        info = await _checkBackupDbDirectory(raw);
    } catch (err) {
        console.error('Failed to validate backup directory:', err);
        alert('No pude validar el directorio destino: ' + (err.message || 'error desconocido'));
        return false;
    }

    if (info.kind === 'file') {
        backupDbTargetDirInput.classList.add('config-form-invalid');
        _setBackupDbStatus('Especificaste un nombre de archivo — indica solo el directorio.', 'warn');
        alert('NO se recomienda cambiar el nombre del archivo.\n\nSi renombras db.sqlite3 el sistema no podrá cargarlo de vuelta correctamente. Indica solo el directorio destino — Tlamatini guarda el archivo como "db.sqlite3".');
        return false;
    }

    if (info.kind !== 'directory') {
        backupDbTargetDirInput.classList.add('config-form-invalid');
        _setBackupDbStatus('El directorio no existe.', 'error');
        alert('El directorio destino no existe:\n\n' + raw + '\n\nEspecifica un directorio existente antes de presionar "Backup".');
        return false;
    }

    let response;
    try {
        response = await fetch('/agent/backup_db/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ target_dir: raw })
        });
    } catch (err) {
        console.error('Backup request failed:', err);
        alert('El backup falló: ' + (err.message || 'error de red'));
        return false;
    }

    let body = null;
    try {
        body = await response.json();
    } catch (_e) {
        // Non-JSON body; body stays null.
    }

    if (!response.ok || !body || body.success !== true) {
        const reason = (body && (body.error || body.reason)) || ('HTTP ' + response.status);
        if (body && body.kind === 'file') {
            backupDbTargetDirInput.classList.add('config-form-invalid');
            alert('NO se recomienda cambiar el nombre del archivo.\n\nSi renombras db.sqlite3 el sistema no podrá cargarlo de vuelta correctamente. Indica solo el directorio destino — Tlamatini guarda el archivo como "db.sqlite3".');
        } else {
            alert('El backup falló: ' + reason);
        }
        return false;
    }

    console.log('--- Backup completed at:', body.path);
    alert('La base de datos se respaldó correctamente en:\n\n' + body.path);
    return true;
}

// ----------------------------------------------------------------
// DB -> Set DB dialog
// ----------------------------------------------------------------

let _setDbValidationTimer = null;
let _setDbInputListenerAttached = false;

function _setSetDbStatus(text, kind) {
    if (!setDbStatusElement) return;
    setDbStatusElement.innerText = text || '';
    setDbStatusElement.classList.remove('set-db-status-ok', 'set-db-status-warn', 'set-db-status-error');
    if (kind === 'ok') {
        setDbStatusElement.classList.add('set-db-status-ok');
    } else if (kind === 'warn') {
        setDbStatusElement.classList.add('set-db-status-warn');
    } else if (kind === 'error') {
        setDbStatusElement.classList.add('set-db-status-error');
    }
}

async function _checkSetDbFile(rawPath) {
    const url = '/agent/check_set_db_file/?path=' + encodeURIComponent(rawPath);
    const response = await fetch(url, {
        method: 'GET',
        credentials: 'same-origin'
    });
    let body = null;
    try {
        body = await response.json();
    } catch (_e) {
        // Non-JSON; fall through.
    }
    if (!response.ok) {
        const err = new Error(`No se pudo validar: HTTP ${response.status}`);
        err.body = body;
        throw err;
    }
    return body || {};
}

function _renderSetDbValidationFeedback(info) {
    if (info.kind === 'file') {
        if (info.sqlite === false) {
            _setSetDbStatus('El archivo seleccionado no parece una base de datos SQLite.', 'error');
            setDbSourcePathInput.classList.add('config-form-invalid');
            return;
        }
        if (info.basename_ok === false) {
            _setSetDbStatus('Encontré el archivo, pero no se llama "db.sqlite3". Tlamatini lo dejará en staging como db.sqlite3.', 'warn');
            setDbSourcePathInput.classList.remove('config-form-invalid');
            return;
        }
        _setSetDbStatus('El archivo existe. Se cargará en el próximo arranque.', 'ok');
        setDbSourcePathInput.classList.remove('config-form-invalid');
    } else if (info.kind === 'directory') {
        _setSetDbStatus('Especifica el path completo a un archivo db.sqlite3, no un directorio.', 'warn');
        setDbSourcePathInput.classList.add('config-form-invalid');
    } else {
        _setSetDbStatus('El archivo no existe.', 'error');
        setDbSourcePathInput.classList.add('config-form-invalid');
    }
}

function _onSetDbInputChanged() {
    if (!setDbSourcePathInput) return;
    const raw = (setDbSourcePathInput.value || '').trim();
    if (_setDbValidationTimer) {
        clearTimeout(_setDbValidationTimer);
        _setDbValidationTimer = null;
    }
    setDbSourcePathInput.classList.remove('config-form-invalid');
    if (!raw) {
        _setSetDbStatus('', '');
        return;
    }
    _setSetDbStatus('Verificando el path...', '');
    _setDbValidationTimer = setTimeout(() => {
        _checkSetDbFile(raw)
            .then(info => {
                const currentRaw = (setDbSourcePathInput.value || '').trim();
                if (currentRaw !== raw) {
                    return; // newer keystroke will trigger its own check
                }
                _renderSetDbValidationFeedback(info);
            })
            .catch(err => {
                console.error('Failed to validate db file path:', err);
                _setSetDbStatus('No pude validar el path del archivo.', 'error');
            });
    }, 350);
}

// Browse button — opens a native file picker on the server host
// restricted to files named ``db.sqlite3`` and drops the chosen
// absolute path into the dialog's input so the existing live-validation
// pipeline (`_onSetDbInputChanged`) classifies it (SQLite-header check,
// basename match, etc.).
async function _browseSetDbFile() {  
    const browseBtn = document.getElementById('set-db-browse-btn');
    if (!setDbSourcePathInput) return;
    if (browseBtn) browseBtn.disabled = true;
    try {
        const response = await fetch('/agent/pick_db_sqlite_file/', {
            method: 'GET',
            credentials: 'same-origin'
        });
        let body = null;
        try { body = await response.json(); } catch (_e) { /* non-JSON */ }
        if (!response.ok) {
            _notifyPickerUnavailable(body, 'HTTP ' + response.status, setDbSourcePathInput, 'file');
            return;
        }
        if (body && (body.error || body.picker_unavailable)) {
            _notifyPickerUnavailable(body, body.error, setDbSourcePathInput, 'file');
            return;
        }
        const chosen = (body && typeof body.path === 'string') ? body.path : '';
        if (!chosen) {
            // User canceled the dialog — leave the input untouched.
            return;
        }
        setDbSourcePathInput.value = chosen;
        setDbSourcePathInput.dispatchEvent(new Event('input', { bubbles: true }));
        setDbSourcePathInput.focus();
    } catch (err) {
        console.error('Browse for db.sqlite3 file failed:', err);
        alert('No pude abrir el file picker: ' + (err.message || 'error de red'));
    } finally {
        if (browseBtn) browseBtn.disabled = false;
    }
}

function OpenSetDbDialog(e) { // eslint-disable-line no-unused-vars
    e.preventDefault();
    if (inLongOperation === true) {
        console.log("Set DB dialog can't be opened during a long operation...");
        return;
    }

    if (setDbSourcePathInput) {
        setDbSourcePathInput.value = '';
        setDbSourcePathInput.classList.remove('config-form-invalid');
        if (!_setDbInputListenerAttached) {
            setDbSourcePathInput.addEventListener('input', _onSetDbInputChanged);
            _setDbInputListenerAttached = true;
        }
    }
    _setSetDbStatus('', '');

    preRenderSetDbDialog(
        'Elegir la base de datos...',
        'Especifica el path completo a un archivo db.sqlite3 para cargarlo en el próximo arranque.',
        'Tlamatini deja el archivo en staging bajo DB/ToLoad/ e intercambia ANTES de que Django abra su base de datos en el próximo arranque. El db.sqlite3 actual se mueve a DB/Older/<timestamp>/ para poder recuperarlo después.'
    );
    renderSetDbDialog();
}

function _showSetDbLoadedNextSessionWarning() {
    preRenderSetDbWarningDialog(
        'Base de datos preparada para la próxima sesión',
        'La base de datos seleccionada se cargará la próxima vez que arranque Tlamatini.',
        'Si la quieres cargar de inmediato, reinicia Tlamatini por completo para que el intercambio ocurra ANTES de que Django abra la base de datos en vivo.'
    );
    renderSetDbWarningDialog();
}

async function _saveSetDb() {  
    const raw = (setDbSourcePathInput ? setDbSourcePathInput.value : '').trim();

    if (!raw) {
        setDbSourcePathInput.classList.add('config-form-invalid');
        _setSetDbStatus('El path del archivo no puede estar vacío.', 'error');
        alert('El path del archivo no puede estar vacío.\n\nEspecifica un archivo db.sqlite3 existente antes de presionar "Set".');
        return false;
    }

    let info;
    try {
        info = await _checkSetDbFile(raw);
    } catch (err) {
        console.error('Failed to validate db file path:', err);
        alert('No pude validar el path del archivo: ' + (err.message || 'error desconocido'));
        return false;
    }

    if (info.kind === 'directory') {
        setDbSourcePathInput.classList.add('config-form-invalid');
        _setSetDbStatus('Especifica el path completo a un archivo db.sqlite3, no un directorio.', 'warn');
        alert('El path apunta a un directorio.\n\nEspecifica el path completo a un archivo db.sqlite3 (p. ej. C:\\Backups\\Tlamatini\\db.sqlite3).');
        return false;
    }

    if (info.kind !== 'file') {
        setDbSourcePathInput.classList.add('config-form-invalid');
        _setSetDbStatus('El archivo no existe.', 'error');
        alert('El archivo no existe:\n\n' + raw + '\n\nEspecifica un archivo db.sqlite3 existente antes de presionar "Set".');
        return false;
    }

    if (info.sqlite === false) {
        setDbSourcePathInput.classList.add('config-form-invalid');
        _setSetDbStatus('El archivo seleccionado no parece una base de datos SQLite.', 'error');
        alert('El archivo seleccionado no parece una base de datos SQLite.\n\nEspecifica un archivo db.sqlite3 real.');
        return false;
    }

    let response;
    try {
        response = await fetch('/agent/set_db/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ source_path: raw })
        });
    } catch (err) {
        console.error('Set DB request failed:', err);
        alert('Set DB falló: ' + (err.message || 'error de red'));
        return false;
    }

    let body = null;
    try {
        body = await response.json();
    } catch (_e) {
        // Non-JSON body; body stays null.
    }

    if (!response.ok || !body || body.success !== true) {
        const reason = (body && (body.error || body.reason)) || ('HTTP ' + response.status);
        alert('Set DB falló:\n\n' + reason);
        return false;
    }

    console.log('--- Set DB staged at:', body.path);
    _showSetDbLoadedNextSessionWarning();
    return true;
}

