<!--
═══════════════════════════════════════════════════════════════════
  ✦  T L A M A T I N I  ✦   —   "one who knows"
  Created by  Angela López Mendoza   ·   @angelahack1
  Developer · Architect · Creator of Tlamatini
  Tlamatini Author Banner — do not remove (Angela's name is kept in every build)
═══════════════════════════════════════════════════════════════════
-->
# ⛔ REGLA DE ORO — TLAMATINI-SPANISH SIEMPRE HABLA ESPAÑOL ⛔

**TLAMATINI-SPANISH SIEMPRE HABLA ESPAÑOL. POR NINGUNA RAZÓN VA A HABLAR
INGLÉS. SI HAY QUE CAER A UN RESPALDO, ES MEJOR QUE AVIENTE UN ERROR Y SE
QUEDE MUDA QUE HABLAR INGLÉS. SIEMPRE ESPAÑOL: NI MÁS, NI MENOS.**

Palabras de Angela, 2026-08-23.

**⚠️ ESTA REGLA ES SÓLO DE ESTA EDICIÓN.** Angela lo dijo con todas sus
letras: *"THIS GOLDEN RULE ONLY APPLIES TO TLAMATINI-SPANISH. NOT TLAMATINI
(English)."* El árbol inglés (`C:\Development\Tlamatini`) **no se toca**: allá
el inglés es el idioma correcto y no se le pone ningún filtro.

Aplica a **TODO lo que suene** en esta edición: su voz de accesibilidad, la
voz del LLM (Talker), **las pruebas automatizadas**, los harness visibles y
cualquier cosa que se escriba después. **Ni las pruebas hablan inglés.**

**LA JERARQUÍA — Y NO TIENE CUARTO ESCALÓN:**

1. **Español latinoamericano** (mexicano) — lo preferido.
2. **Castellano de España** — si no hay latino, sirve; se entiende.
3. **ERROR Y SILENCIO** — se avienta el error, se reporta, y NO sale ni un
   byte de audio.

**NUNCA hay un escalón en inglés.** No existe, no se agrega, y no se
"restaura por compatibilidad". Angela lo explicó así: *si una hispanohablante
oye inglés, no va a pasar el milagro de que de repente lo entienda*. Un
respaldo al inglés no es una degradación elegante: es una FALLA que además
suena a que funcionó.

**DÓNDE VIVE (no lo debilites):**

- `agent/tts_piper.py` → `a_castellano()` / `_es_ingles()`. **El catálogo
  NEPANTLA (`agent/i18n/ui_es.py`) se consulta PRIMERO, a cualquier
  longitud**, y sólo después se juzga el idioma. Al revés NO sirve:
  `_es_ingles` necesita ≥4 palabras, así que `Save` / `Please wait` se
  colaban y se pronunciaban en inglés.
- `agent/agents/talker/talker.py` → `EnglishVoiceForbiddenError` (cierra el
  proceso, igual que la voz masculina) y `piper_sintetiza()` con una **copia
  inline** del mismo filtro. Va copiada A PROPÓSITO: un agente del pool corre
  como subproceso y **no puede importar `agent.*`**; si el filtro viviera
  sólo en `tts_piper`, el Talker sería un hueco por donde sale inglés.
- `static/agent/js/avatar.js` → es-MX → LatAm → castellano → Piper →
  **silencio**. Sin rama en inglés, y `speak()` NO deja hablar al navegador
  cuando `pickVoice()` devuelve null (usaría su voz por defecto, que es
  inglesa).
- `agents/whatsapper/whatsapper.py` → `_LANGUAGE_FALLBACKS` empieza en
  `es_MX`/`es`.

**CÓMO SE ROMPIÓ ANTES (para no repetirlo):** el código *juraba en sus
comentarios* que se quedaba callado y hacía lo contrario — `spanishPool()`
cerraba con `return en.length?en:vs` y `pickVoice()` prefería
`zira|jenny|aria|samantha|hazel`. Zira pasa el filtro de "voz femenina", así
que Tlamatini leía castellano con boca inglesa. **Un comentario no es un
guard.** La causa de raíz: Piper nunca se había instalado y el respaldo al
inglés lo tapaba. Se instala sin admin con
`python -c "from agent import tts_piper; tts_piper.ensure_ready()"`.

Guard: `agent/test_sin_respaldo_ingles.py`.

---

<!-- ==================================================================== -->
<!-- ===================  PRIVATE DATA GUARD: ON  ======================== -->
<!-- ==================================================================== -->

**`1.50.4s` es el release actual del package y la documentación de esta edición en español**; el tag anotado más reciente de ESTE árbol es `v1.50.4s` y apunta a `1339fc7` (también `HEAD` al iniciar esta auditoría). La **`s` es la letra de edición** que diferencia este build del árbol inglés `v1.50.4`: se conserva en toda superficie humana y `agent/version.py::strip_edition_suffix` la elimina donde la versión debe volverse numérica; véase `VERSIONING.md`, fijado por `agent/test_edition_version_suffix.py`. No cites hashes del árbol inglés: no existen aquí. La verdad derivada del source es **88 workflow agents**, **66 launchers `chat_agent_*`**, **108 tools integradas de Multi-Turn** (20 core + 66 wrapped + 12 ACPX/Skill + 10 supervisores External-MCP), **105 tools del MCP stdio raíz**, **29 skills** y **198 migrations**. No escribas estas cifras por intuición: `agent/test_self_knowledge_is_current.py` las deriva y falla si `agent/Tlamatini.md` se desvía.

The target adds **NetSpeed-Calculator** (multi-provider RFC-6349-style throughput, Student-t confidence intervals, random-effects fusion, I², bufferbloat, named zero-byte failures, and Ask-Execs tier-D bandwidth gating); **WAL-safe SQLite data movement** (`sqlite_copy.py` online backup API + DELETE-journal destination + `quick_check` + sidecar hygiene for Backup DB, Set DB, and pre-Django swap); Googler's **structured Google-dork builder** plus a two-tier resilience path (four plain-HTTP server-rendered routes first, then visible installed Chrome/bundled Chromium across seven direct-results routes, bounded retries, answer-route logging, lawful-source/`links_only` workflows, and explicit Google-only operator semantics); the **External MCP Adder** skill's classify/import/doctor/activate/wait/list/call lifecycle; migration 0194's append-only **Deep Internet Research** starter; Ollama Pro-or-higher complete-operation guidance; and private-build contact synchronization into gitignored `contacts.private.json` while public builds/snapshots remain contact-empty.

## ⌨️ Uniform Dialog Dismissal — ESCAPE CLOSES EVERY DIALOG (2026-08-16, v1.48.17)

**Angela REVERSED the previous rule.** Until 2026-08-13 `dialog_policy.js` deliberately SWALLOWED Escape. The policy is now one line, on **both** pages, for **every** dialog:

> A dialog closes by its titlebar ✕, its Cancel/dismiss button, its Continue/OK button, **or ESCAPE** — and **Escape === ✕ === Cancel**.

The other half is UNCHANGED and must not be relaxed: **an outside click still never dismisses anything.**

**⚠️ THE DISPATCHER NEVER HIDES A NODE.** `dialog_policy.js` §4 is a **bubble-phase `document` keydown** handler that finds the *topmost open dialog* (shape-based selector — `[id$="-overlay"]`, `[class*="-overlay"]`, `[role="dialog"]`, `.ui-dialog`, `.modal.show`, … — ranked by z-index, backdrops excluded) and **invokes THAT dialog's own dismiss control**: the click the user would have made. That is why nothing had to be rewired per dialog and every fail-safe survives Escape — the Ask-Execs prompt still answers **DENY** through its `close:` handler, `acpConfirm` / `tlmConfirm` still resolve **false**, every `body.style.overflow` is restored by the dialog's own close, and the **sealed updater still refuses** (`CloseUpdateDialog` → `mayClose`). A blind hide would have silently skipped all four.

**Contracts that must NOT be reverted:** BUBBLE phase, not capture (the Catalog's search box clears the query on the FIRST Escape; only the SECOND closes the catalog) · `stopImmediatePropagation()` when it dismisses, so one keystroke never closes two stacked layers · `dialog_policy.js` stays the FIRST document keydown handler on both pages · it bails when no dialog is open (Escape still belongs to the page) · Escape can never press an **affirmative** button (the label scan matches only cancel/close/dismiss/cancelar/cerrar/no and the × glyphs; a one-button acknowledgement box uses that button) · backdrops are excluded · a dialog with no ✕ and no Cancel must expose **`el.tlmDismiss`** (the Catalog of Prompts is the one such dialog — a blind hide there leaves the whole chat page unscrollable). **`closeOnEscape: false` is now a FORBIDDEN pattern tree-wide** (seven dialogs carried their own and were flipped).

**The ONE exception — the updater is INVULNERABLE while it downloads.** Not a special case bolted onto the dispatcher: a dialog declares **`el.tlmSealKey`**, and while that key is sealed `dismissDialog()` refuses **FIRST**, before any other path (checked later, the "hide the node" last resort would kill exactly the dialog it must protect). Escape is **swallowed** (`preventDefault` + `stopImmediatePropagation`) plus a 600 ms shake instead of nagging; F5 / Ctrl+R / Ctrl+F4 are guarded too; and a **failed start ALWAYS unseals** (a permanent seal is strictly worse than the interruption it prevents). ⚠️ The seal guard is **CAPTURE** phase — deliberately the opposite of the dispatcher's bubble phase, and both are pinned so neither gets "made consistent" by mistake. Honest limit: Alt+F4, the window ✕, and Chrome-reserved Ctrl+W can never be blocked from a web page — but the swap runs in an **external PowerShell process**, so a closed tab costs the progress bar, not the update.

**No native browser pop-ups inside a themed dialog.** `alert()` / `confirm()` / `prompt()` paint OS chrome carrying the page URL, block the page, and cannot be photographed by a headed Playwright run. Use **`tlmAlert(message, title)` / `tlmConfirm(primary, secondary, title)`** — chat + canvas, exported by `dialog_policy.js`, Promise-based (`tlmConfirm` → `Promise<boolean>`; anything but Continue is `false`), styled from `dialog_theme.css` `.tlmpop-*` tokens, overlay at z-index **100001**, **fail-open** to the native popup — or `acpAlert` / `acpConfirm` on the canvas. ⚠️ They are deliberately **NOT** jQuery-UI dialogs: they are raised BY native modals at `z-index: 20000` (`.emx-dialog` / `.ctb-dialog`) while `.ui-front` is ~100, so a jQuery-UI confirm would render *under* the dialog that asked for it — an invisible modal, i.e. a hang. When you migrate a module, add it to `_THEMED_DIALOG_MODULES` in the test.

Coverage: `agent/test_dialog_dismissal_policy.py` (**35 tests** — bubble phase, `stopImmediatePropagation`, no-affirmative-button, backdrop exclusion, the `tlmDismiss` hook, script load ORDER on both pages, the seal-check index, and the forbidden patterns) + the **visible** headed-Chrome runner `.claude/skills/tlamatini-daily-chat-test/harness/dialog_policy_visible.py` (Playwrighter drives, Shoter photographs). Full contract: `docs/claude/frontend.md`; full story: `docs/claude/recent-fixes.md` (2026-08-16).

---

## Temp & Templates Directory Policy (2026-06-02)

Every **transient** file Tlamatini writes lives under ONE directory — `Temp` at the application root (`<exe-dir>/Temp` frozen, `<repo-root>/Temp` source) — and **never** outside Tlamatini (no `C:\Temp`, no `%TEMP%`, no system temp). `Tlamatini/manage.py::_enforce_app_temp_dir()` (before Django) and `tlamatini/settings.py::_pin_temp_directory()` (covers a direct `daphne`/`asgi` launch) pin `TMP`/`TEMP`/`TMPDIR` + Python's `tempfile.tempdir` to it and export `TLAMATINI_TEMP`, which every spawned pool agent inherits (`get_agent_env` does `os.environ.copy()`). The resolver is `agent/path_guard.py` (`get_app_temp_root` / `enforce_app_temp_dir` / `is_within_app_temp` / `resolve_temp_path`). The temp-creating agents (executer, de_compresser, esp32er, stm32er, arduiner, plus historical TelegramRX templates in older installs) also carry an explicit module-top `if (os.environ.get('TLAMATINI_TEMP')…)` guard (an `if`-block, never a top-level `def` — that trips ruff E402 before the imports).

**Chat screenshots land in `Temp` too (2026-07-14).** An image pasted with **Ctrl+V** — or dropped onto the chat column — is persisted by `views.paste_image_view` through `path_guard.resolve_temp_path()` as `<app>/Temp/image_<YYYYmmdd>_<HHMMSS>_<ms>.jpg` (Pillow → JPEG), and its **absolute path is spliced into the chat box at the caret** so the user can immediately ask Tlamatini to analyze it (Image-Interpreter / `launch_view_image`). Frontend: `agent/static/agent/js/chat_image_paste.js` — see `docs/claude/frontend.md` and the 2026-07-14 entry in `docs/claude/recent-fixes.md`.

Separately, the **default parent for the project trees the firmware/engine agents (STM32er / ESP32er / Arduiner / Unrealer) scaffold** is `Templates` at the application root (`TLAMATINI_TEMPLATES`; `path_guard.get_app_templates_root`), **unless the user names another path**. `Temp` = throwaway scratch; `Templates` = deliverable project trees (so it never touches `tempfile`).

The LLM is told this in `prompt.pmt` **Rule 15** (Temp) and **Rule 16** (Templates), with the absolute paths injected as `{temp_directory}` / `{templates_directory}` by `agent/rag/config.py`. `build.py` ships both dirs empty next to the `.exe`; `.gitignore` ignores both. **When you author a new agent/tool/skill that writes scratch, route it through `<app>/Temp`; a new firmware/engine agent that scaffolds projects defaults to `<app>/Templates`.** Full "do-NOT-revert" contract: `docs/claude/recent-fixes.md` (2026-06-02). The `create-new-agent` / `create-new-mcp` / `skill-creator` skills and the two `@`-imported workflow guides carry the same indication.

---

## Specialized Docs (auto-imported)

The rest of the onboarding material is split into topic files under `docs/claude/`. Each `@` line below is imported by Claude Code into your context automatically, so treat the full set as a single document. See `docs/claude/INDEX.md` for one-line descriptions of each file.

- **Architecture & core systems** — config, system prompt & identity, the Five Layers, application log, doc generation, database models: @docs/claude/architecture.md
- **Multi-Turn, Create Flow, Parametrizer** — Multi-Turn mode, short follow-up scoring, Create-Flow pipeline, `INI_SECTION_*` format: @docs/claude/multi-turn.md
- **Exec Report** — per-agent execution tables, capture/render pipeline, strict ordering contract, styling, adding new agents: @docs/claude/exec-report.md
- **Agents** — creating a new agent (8-step), naming conventions, lifecycle, all 88 agent types, FlowCreator, FlowHypervisor: @docs/claude/agents.md
- **ACPX** — definition, agent registry, 12 LLM-facing tools, transport profiles, canonical flows, runtime mechanics, ACPX toolbar toggle, "when the user says ACPX" decision matrix: @docs/claude/acpx.md
- **MCPs & Tools** — tool-only vs MCP context provider workflows, Skills system (SKILL.md packages), key warnings: @docs/claude/mcp-tools.md
- **Frontend** — chat modules, ACP modules, ACP Canvas DOM Contract: @docs/claude/frontend.md
- **Gotchas & reference** — Claude API client, build/lint, versioning, hardcoded assumptions, roadmap, work-style preferences: @docs/claude/gotchas.md
- **Creating a new agent (full 8-step guide)** — backend script + view + migration + CSS gradient + 4 JS files + docs + lint; naming-convention table; lifecycle; connection-field semantics: @Tlamatini/.agents/workflows/create_new_agent.md
- **Creating a new MCP or tool (full guide)** — tool-only vs MCP context-provider vs both; per-workflow checklists; `factory.py` / sidecar chain / `Mcp` row wiring; hardcoded-assumption warnings: @Tlamatini/.mcps/create_new_mcp.md

**Consult-on-demand (deliberately NOT `@`-imported, to keep the auto-loaded context lean):**

- **Recent Fixes / fix log** — `docs/claude/recent-fixes.md`. The dated chronological log of surgical fixes and "do NOT revert this / keep these surfaces aligned" contracts (ACPX, Flow Compiler, planner, Exec Report, ACP canvas, wrapped chat-agent parsing, desktop-UI agents, the STM32er zero-config bootstrap + fail-safe hardware preflight, `prompt.pmt`, `regen_secrets.py`, logging filters). **Read it before modifying or reverting code in any of those subsystems**, and prepend new fix entries there rather than to `gotchas.md`.
- **Creating a new Skill (SKILL.md package)** — `Tlamatini/.skills/create_new_skill.md`. The dedicated authoring guide for a `SKILL.md` (the two runtimes — `in-process` vs `acpx`; the frontmatter contract + schema ranges; discovery / 30 s staleness cache; lint + `quick_validate`; ACPX-surface gotchas). NOT auto-imported — read it when adding or editing a skill. The `flow-making` skill (`agent/skills_pkg/flow_making/`) is the canonical worked example of an in-process skill that shells out to a shipped `scripts/*.py`.
- **Companion-app discovery** — `docs/companion-app-discovery.md`. How Tlamatini lets XAIHT companion apps (**Tlamatini-FlowPills**) find the agents catalog without Python/scans: the `HKCU\Software\XAIHT\Tlamatini` registry key + `<agents_root>\_tlamatini_agents_manifest.json` + the `.tlamatini-preserved-agents.json` preserved marker. Engine `agent/agent_manifest.py` + `agent/windows_app_registration.py`, wired in `apps.py` / `install.py` / `uninstall.py` / `build.py`; HKCU-only, no-admin, fail-open. Implements `Tlamatini-FlowPills-Lookup.md` §15.

│   │   │   ├── pdfer/              # PDFer — DOCUMENT COMPOSER, the WRITE side of the document family (File-Extractor/File-Interpreter READ, PDFer AUTHORS). Tlamatini's answer / Markdown / HTML / text / images / existing PDFs → ONE styled PDF. ZERO new deps (markdown+xhtml2pdf+pymupdf+reportlab+pillow+pypdf already ship; md→pdf pipeline ported INLINE from doc_generation/mardown_to_pdf.py). mode: auto|markdown|html|text|images|mixed|merge|info|validate; optional Ollama polish (default OFF, never loses the doc); saves to Documents/TlamatiniPDF, collision-proof; fail-safe preflight REFUSES rather than write an empty PDF; INI_SECTION_PDFER; Exec Report + Ask-Execs tier A (canvas + chat_agent_pdfer)
│   │   │   ├── latexer/            # LaTeXer — LaTeX TYPESETTING, the typesetting sibling of PDFer (PDFer COMPOSES from Markdown/HTML/images; LaTeXer TYPESETS from .tex: real maths, bibliographies, cross-refs, index). Embeds the WHOLE mcp-latex-server surface NATIVELY (create/template/edit/read/list/validate/structure/compile) — NO MCP server, NO sidecar, NO new dependency (stdlib only: subprocess+shutil+glob+re+urllib) — PLUS whole-PROJECT compile of a .tex SET (master auto-detected, \input followed), a real BibTeX/Biber + makeindex + makeglossaries convergence loop, latexmk pass-through, and LaTeX-log diagnostics a human can read. **REQUIRES MiKTeX** (https://miktex.org/download) — Tlamatini bundles NO TeX distribution (several GB; the release must stay <2 GB); MiKTeX is preferred because `--enable-installer` installs a missing .sty ON DEMAND mid-compile, so any document builds. ⚠️ latexmk is probed for USABILITY not presence (it ships with MiKTeX but is a PERL script; most Windows boxes have no Perl → auto-fallback to the built-in loop). action: compile|compile_project|scaffold_compile|create_file|create_from_template|edit_file|read_file|list_files|validate_tex|structure|clean|validate|install; auto_preamble wraps a bare fragment; shell_escape OFF by default (\write18 = RCE); saves to Documents/TlamatiniLaTeX, projects to <app>/Templates/LaTeXer; fail-safe preflight REFUSES rather than mis-typeset; **EIGHT-RUNG REPAIR LADDER (v1.48.2) so a failed build self-heals — lint → preamble → rules → log_directed → acquire → engine_swap → model → bisect, each repair applied to a COPY and re-linted (a repair that worsens the lint is REVERTED), the author's file untouched unless `repair_write_back`, every rung audit-traced, quarantined blocks named; ⚠️ the DESTRUCTIVE `bisect` rung is strictly LAST (reordered 2026-08-05) — do NOT swap it back ahead of `model`**; a DEGRADED build never claims clean success; INI_SECTION_LATEXER; Exec Report + Ask-Execs tier A (canvas + chat_agent_latexer)
│   │   │   ├── editor/             # Surgical in-place find-and-replace on ONE text file (Claude-Edit equivalent; byte-exact, refuses a non-unique match unless replace_all, base64 channel; emits INI_SECTION_EDITOR) (canvas + chat_agent_editor)
│   │   │   ├── grepper/            # Read-only regex CONTENT search across a file/dir tree (Claude-Grep equivalent; file:line:match, glob filter, prunes noise dirs; emits INI_SECTION_GREPPER). ⚠️ ENCODING-AWARE since 2026-08-16 (`_read_text_lines`): BOM tested BEFORE the NUL byte (UTF-16/32 text is legitimately full of 0x00 — same ordering contract as rag/binary_guard.py; _BOM_CODECS longest-prefix-first), then UTF-8 → cp1252 → latin-1. It used to open() strict-UTF-8 and swallow the UnicodeDecodeError as "binary", so it answered a confident `no_matches` about files it never opened (PowerShell's UTF-16 logs, accented Spanish sources). Pinned by test_grepper_encodings.py (canvas + chat_agent_grepper)
│   │   │   ├── globber/            # Read-only filename glob search (Claude-Glob equivalent; find files by pattern, newest-first, ** recursive; emits INI_SECTION_GLOBBER) (canvas + chat_agent_globber)
---

## ⛔ MANDATORY DIRECTIVE - Angela 2026-07-07 - FORBIDDEN HEADLESS TESTS: ALL AUTOMATED TESTS MUST BE VISIBLE (HEADED PLAYWRIGHT)

**HEADLESS / INVISIBLE AUTOMATED TESTS ARE FORBIDDEN. EVERY automated test MUST run VISIBLE — a HEADED browser (Playwright `headless=False`, prefer real Chrome) on Angela's REAL desktop, so she can SEE every step live.** This is HARD, NON-NEGOTIABLE, FOREVER.

- **Playwright**: launch HEADED. **NEVER** pass `--headless`. The chat-test harness `--headless` flag is disabled (refuses to run). Drive the **real Tlamatini chat GUI** (`http://127.0.0.1:8000/agent/agent/`, login `angela`) — never fake or bypass the UI.
- **Run it in a VISIBLE FOREGROUND window** (`Start-Process powershell -NoExit …`, `dangerouslyDisableSandbox:true`) so it renders on her screen — never `run_in_background`, never a hidden/detached job. (Same spirit as the foreground-windows rule.)
- **Verify each step with a FULL-SCREEN screenshot** (the ENTIRE desktop, taskbar **clock** visible) — one photo per test + a live `SUMMARY.html`.
- **NEVER LIE**: a stale chat-history scrape, a transient self-healing "🔁 Tactic #…" status, or a timed-out answer must NEVER be recorded as a pass. Clear chat history per test, re-assert **Multi-Turn ON at every send**, reject already-seen answers.
- If a test cannot be made visible, **do NOT run it** — tell Angela.
- Enforced by: SessionStart hook `~/.claude/hooks/visible_tests_rule_banner.py` (prints every session), memory `feedback_forbidden_headless_visible_tests`, global `~/.claude/CLAUDE.md`, and the `tlamatini-daily-chat-test` skill. Reference runner: `.claude/skills/tlamatini-daily-chat-test/harness/discoverer_1000.py`.

---

## MANDATORY DIRECTIVE - Angela 2026-06-14 - USE ONLY TLAMATINI'S SKILLS/TOOLS/AGENTS, NOT CLAUDE CODE'S BUILT-IN TOOLS

Every session, from the very start, Claude MUST perform the work with Tlamatini's OWN agents, tools and skills - Executer, Pythonxer, File-Creator, Mover, Deleter, Playwrighter, Blenderer, the mcp__tlamatini__ wrapped tools, and the SKILL.md skills - and MUST NOT use Claude Code's built-in tools - Bash, Read, Write, Edit, Grep, Glob, the built-in Playwright - to do the task. Claude's shell is ONLY a launcher of last resort. The purpose is to DOGFOOD Tlamatini's tools: exercise them on real work, surface their errors, and keep fixing them. If a Tlamatini tool lacks a capability, fix or extend that tool instead of falling back to a Claude tool.

### Tool correspondence — Claude built-in → the Tlamatini tool to use INSTEAD

The Tlamatini tools are exposed over MCP as `mcp__tlamatini__<name>` (their schemas are deferred — load them on demand with `ToolSearch`, e.g. `ToolSearch "globber grepper editor"`; `mcp__tlamatini__tlamatini_list_agents` enumerates every one). **Before reaching for ANY Claude built-in, map the action to its Tlamatini tool here and use that:**

| Claude built-in | Use INSTEAD | Key params / notes |
|---|---|---|
| **Write** (create a file) | `mcp__tlamatini__file_creator` (File-Creator) | `file_path`, `content` (or `content_b64` for binary); creates parent dirs |
| **Edit** (find/replace) | `mcp__tlamatini__editor` (Editor) | exact-unique `old_string`→`new_string`; `replace_all`; `old_string_b64`/`new_string_b64` for byte-exact edits |
| **Grep** (content search) | `mcp__tlamatini__grepper` (Grepper) | `pattern` (regex), `path`, `glob`, `case_insensitive`, `output_mode` |
| **Glob** (find files) | `mcp__tlamatini__globber` (Globber) | `pattern`, `path`, `sort_by`, `max_results` |
| **Bash** (shell command) | `mcp__tlamatini__executer` (Executer) | `script`; `non_blocking:true` to detach a long-running server; `execute_forked_window:true` for a visible console window |
| **Bash** (run Python) | `mcp__tlamatini__pythonxer` (Pythonxer) | inline Python behind a compile()/ruff gate |
| **Playwright** / browse a site | `mcp__tlamatini__playwrighter` (Playwrighter) | `start_url` + `steps_json` (goto/click/fill/extract/screenshot) |
| move / copy a file | `mcp__tlamatini__mover` (Mover) | glob-capable |
| delete a file | `mcp__tlamatini__deleter` (Deleter) | glob-capable |
| git commands | `mcp__tlamatini__gitter` (Gitter) | use `command='custom'` to pass a raw git subcommand |
| web search | `mcp__tlamatini__googler` (Googler) | Manual Google operators go in `query`; the visual/pool agent adds structured presets, grouped site/filetype filters, and `links_only` file-hunt output |
| audio / video / camera / mic, TTS / STT, firmware, 3D | the matching agent — `talker`, `whisperer`, `recorder`, `camcorder`, `audioplayer`, `videoplayer`, `stm32er`, `esp32er`, `arduiner`, `blenderer`, `kalier`, `windower`, `mouser`, `keyboarder`, `shoter`, … | **no Claude equivalent exists — always the agent** |

**Reading files:** there is no raw-`cat` Tlamatini agent (File-Interpreter / File-Extractor read-and-interpret via the LLM or extract from PDF/DOCX; Grepper / Globber are for search). So prefer Grepper/Globber to locate code and File-Interpreter to summarize a file; Claude's **Read** is the narrow last-resort exception **only** when you need the exact bytes of a region to author an Editor `old_string` and no Tlamatini tool yields them.

**Transient-outage fallback (allowed, must be stated):** if a `mcp__tlamatini__*` tool is briefly blocked (e.g. the safety classifier is temporarily unavailable) and you have already retried, you MAY fall back to the matching Claude built-in to avoid stalling — but say so explicitly in your reply and treat it as an outage workaround, not a substitution. The instant the Tlamatini tool is reachable again, switch back.

**Desktop/visible agents** (a headed Playwrighter, an Executer/Pythonxer forked console, Shoter/Mouser/Keyboarder/Camcorder/VideoPlayer windows) launched via your own shell must run FOREGROUND with `dangerouslyDisableSandbox: true` so the window renders on the user's real desktop — but when driven through `mcp__tlamatini__*` (the Django server spawns them) they already render, so just call the MCP tool.
