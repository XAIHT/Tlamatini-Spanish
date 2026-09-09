<!-- THE USER IS ANGELA, A WOMAN - always address her by name. -->
<!-- Este índice sólo enlaza memorias tracked que existen. -->

# Memoria operativa de Tlamatini-Spanish

## Contrato vigente

- **Idioma:** responde a Angela con español como lengua matriz. Conserva byte-stable English para agents/tools, parameters, fields, keys, enums, sentinels, paths y code según NEPANTLA. Una memoria histórica que pida inglés no supera este contrato.
- **Identidad:** release `v1.51.3s` en `212b0bd`; `HEAD` de `main` en el mismo commit, cero commits posterior. No muevas ni reinventes el tag.
- **Superficie:** 88 workflow agents, 66 wrapped launchers, 108 built-in Multi-Turn tools, 105 root-MCP tools, 29 Skills y 200 migrations.
- **Git:** Angela controla commits, tags, pushes, branches y cambios de history. Las inspecciones read-only sí son normales.
- **Estado actual:** descripciones españolas con fallback agent por agent; Playwrighter encuentra Shoter mediante `TLAMATINI_AGENTS_ROOT`; harnesses visibles de dialogs/tema/toggles y 1,000 preguntas; `Referenced Rephrase:` es sentinel machine único.
- **Diseño prospectivo:** el rediseño transaccional del updater y la instalación/abstracción de Memory MCP no se anuncian como runtime hasta existir source ejecutable y tests.

## Preferencias y disciplina

- [Convención de nombres de agents](feedback_agent_naming_conventions.md)
- [No sobrediseñar la seguridad de Exec](feedback_dont_overbuild_exec_safety.md)
- [Pruebas con escenarios reales](feedback_hard_real_scenario_tests.md)
- [Trabajo sobre main](feedback_main_branch_only.md)
- [Bump de package.json](feedback_package_json_version_bump.md)
- [Agents propios visibles](feedback_run_tlamatini_agents_visible.md)
- [Restricciones primero](feedback_state_constraints_upfront.md)
- [Pivot file para cambios](feedback_track_changes_pivot_file.md)
- [Actualizar documentación de agents](feedback_update_agent_docs.md)
- [Angela controla las escrituras Git](feedback_user_owns_git.md)

## Orquestación, ACPX y UI

- [ACPX oneshot prompt](project_acpx_oneshot_prompt.md)
- [Menú ACPX-Skills](project_acpx_skills_menu.md)
- [Toggle de Skills](project_acpx_toggle_skills.md)
- [Agent ACPXer](project_acpxer_added.md)
- [Tabla Agent reconstruida al arrancar](project_agent_table_wiped_on_boot.md)
- [Ask Execs](project_ask_execs_feature.md)
- [Conjunction parser](project_conjunction_parser_fix.md)
- [Daily chat test](project_daily_chat_test_skill.md)
- [Desktop UI lifecycle](project_desktop_ui_lifecycle.md)
- [Flow compiler y prioridad del dialog](project_flow_compiler_dialog_wins.md)
- [Living Canvas descartado](project_living_canvas_dropped.md)
- [Planner follow-up](project_planner_followup.md)
- [Badges del Prompt catalog](project_prompt_catalog_mode_badges.md)
- [Taskbar flash](project_taskbar_flash_attention.md)
- [TeleTlamatini y ACPX](project_teletlamatini_acpx.md)

## Agents de ejecución, medios y documentos

- [Arduiner](project_arduiner_agent.md)
- [AudioPlayer](project_audioplayer_agent.md)
- [Camcorder](project_camcorder_agent.md)
- [Director/Virtuoso prompts](project_director_virtuoso_demo_prompts.md)
- [Emailer/Recmailer oneshot](project_emailer_recmailer_oneshot.md)
- [Execute Command acotado](project_execute_command_bounded_fix.md)
- [Execute File foreground](project_execute_file_foreground_fix.md)
- [Keyboarder wrapped](project_keyboarder_wrapped_2026_05_07.md)
- [LaTeXer](project_latexer_agent.md)
- [Mouser wrapped](project_mouser_wrapped_2026_05_07.md)
- [Native picker sin Tcl/Tk](project_native_picker_tcltk_fix.md)
- [Native toast histórico](project_native_toast.md)
- [PDFer](project_pdfer_agent.md)
- [Playwrighter](project_playwrighter_agent.md)
- [Playwrighter hold-open](project_playwrighter_hold_open.md)
- [Pythonxer fork-bomb fix](project_pythonxer_forkbomb_fix.md)
- [Pythonxer strict ruff gate](project_pythonxer_strict_ruff_gate.md)
- [Quote/apostrophe fix](project_quote_apostrophe_fix_2026_05_07.md)
- [Recorder](project_recorder_agent.md)
- [Reviewer y Analyzer](project_reviewer_analyzer_agents.md)
- [Reviewer/Analyzer demo prompts](project_reviewer_analyzer_demo_prompts.md)
- [Reviewer committed-secrets false positive](project_reviewer_committed_secrets_falsepos.md)
- [Summarizer oneshot](project_summarizer_oneshot_mode.md)
- [VideoPlayer](project_videoplayer_agent.md)
- [Windower](project_windower_agent.md)

## Hardware, engines y networking

- [ESP32er](project_esp32er_agent.md)
- [Kalier](project_kalier_agent.md)
- [NetSpeed-Calculator](project_netspeed_calculator_agent.md)
- [STM32er](project_stm32er_agent.md)
- [STM32er bootstrap/preflight](project_stm32er_bootstrap_preflight.md)
- [STM32er demo prompts](project_stm32er_demo_prompts.md)
- [STM32er docs/libs/Parametrizer](project_stm32er_docs_libs_parametrizer.md)
- [STM32er HIL serial proof](project_stm32er_hil_serial_proof_fix.md)
- [STM32er tests](project_stm32er_tests.md)
- [Unity MCP declinado](project_unity_mcp_declined.md)
- [Unrealer expanded surface](project_unrealer_expanded_surface.md)

## Build, runtime, datos y seguridad

- [Build concurrency guard](project_build_concurrency_guard.md)
- [Build tests y Enter del installer](project_build_tests_and_installer_enterkey.md)
- [Python acarreado](project_carried_python_for_agents.md)
- [Embedding memory guard](project_embedding_memory_guard.md)
- [External Exec safety layer](project_external_exec_safety_layer.md)
- [Ghost dist-info audit](project_ghost_distinfo_dependency_audit.md)
- [NumPy/PyInstaller](project_numpy_pyinstaller.md)
- [Ollama source build y embeddings](project_ollama_source_build_breaks_embeddings.md)
- [Reaper console window](project_reaper_console_window_fix.md)
- [Recuperación de leak histórico](project_secret_leak_recovery.md)
- [Temp/Templates policy](project_temp_templates_policy.md)
- [Versioning](project_versioning_2026_05_15.md)

## Historial de refresh documental

- [Refresh 2026-05-06](project_doc_refresh_2026_05_06.md)
- [Ocho fixes 2026-05-07](project_eight_fixes_2026_05_07.md)
- [Refresh 2026-05-08](project_doc_refresh_2026_05_08.md)
- [Refresh 2026-05-09](project_doc_refresh_2026_05_09.md)
- [Perfil de Angela](user_profile.md)
