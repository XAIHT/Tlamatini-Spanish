<!-- Tlamatini Author Banner — Angela López Mendoza · @angelahack1 -->
# Configuración del Editor en vivo y Terminater

Desde la v1.92.0, ambos controles admiten hasta 250 WPM. El Editor en vivo usa 100 WPM de forma predeterminada y Terminater usa 50.

Abre **Config → Editor en vivo y Terminater** o pulsa Configuración en el editor o la terminal. El diálogo contiene las pestañas Editor en vivo, Terminater y Voz. Guardar aplica los cambios a la siguiente acción. Cancelar o Escape descartan el borrador. Abrir la configuración interrumpe la lección activa. El permiso de acceso al editor se aplica de inmediato en esa pestaña.

Los preajustes Estándar y Aprendizaje guiado rellenan el borrador. Restablecer recupera los valores iniciales de la pestaña. Vista previa reproduce una muestra en el diálogo sin guardar cambios en la cuenta.

## Ajustes de la cuenta y del navegador

- **Editor en vivo:** 40–250 WPM, 100 de forma predeterminada. Puedes elegir una pausa de 0–3 segundos tras cada segmento, el detalle de las explicaciones, las sugerencias de campo y el seguimiento del cursor. Desplazar el documento a mano suspende el seguimiento durante ese segmento.
- **Terminater:** 20–250 WPM, 50 de forma predeterminada. Elige el intérprete, quién presiona Enter, el asesor y los tiempos de espera. Si vinculas las velocidades, ambas usan 40–250 WPM. El modo de Enter manual bloquea también los envíos automáticos mediante alias o comandos codificados. Cada tecla conserva una pausa.
- **Voz:** elige si se lee la explicación, el texto literal o ambos, y si la lectura ocurre antes, durante o después de escribir. Puedes hacer que la escritura espere el final de la narración. Silenciar y la escucha del micrófono tienen prioridad.
- **Apariencia:** la fuente, los números de línea, el ajuste de líneas, el cursor y la distribución de terminales se conservan por cuenta y navegador.

La migración 0220 guarda las preferencias de comportamiento por cuenta. `/agent/interaction-settings/` comprueba la sesión, CSRF, los límites y la revisión. Si dos pestañas intentan guardar revisiones distintas, vuelve a cargar el diálogo.

## Runtime contracts

The Django process's one TerminalHub resolves account preferences on dispatch
for chat, ACP, Prompt Flow and browser actions. New agent configurations and new
Prompt Flow nodes use `use_my_defaults`. Older flow files normalize this flag to
false and retain explicit settings. When enabled it overrides speed, shell,
advisor and waits. Manual Enter and narration remain account choices in either
mode. Shell/advisor affect newly opened terminals; waiting windows are applied
to each typing action. A wait timeout does not kill a process.
Typed chat calls preserve an explicitly requested shell. Their account pacing
and omitted shell are resolved at the authenticated launcher, where an explicit
model field can be distinguished from the template's default. Ask Execs uses
the same account shell when the task does not choose one.

The editor carries a settings snapshot through its existing authenticated tool
and receipt path. Typing retains document/revision checks, bounded visibility
pause, user takeover, fresh reads and small tutor mutations. No new Agent or
tool registration is required.

Terminal narration selects one visible, focused account tab. A receipt belongs
to that exact connection. Waiting before typing is bounded to 120 seconds and
cancellable; a missing listener cancels the step rather than silently running it.
An unavailable voice offers Continue without voice or Stop. No command is
replayed on reconnect. Secret-marked content and handoff values never enter
speech. Result notices describe status without reading command output aloud.
The shared speech queue prevents overlapping chat and interaction utterances.

## Validation

Run development commands only in a verified visible foreground console and
leave it open. `scripts/interaction_settings_visible.py` launches real Chrome
with `headless=False`, creates a disposable database, and requires visual
confirmation before exercising the UI. It uses the actual editor, WebSockets,
TerminalHub and CMD; it separates real OS voice receipts from deliberate voice
failure injection. Evidence is kept in `Temp/interaction-settings-visible`.
Backend tests cover account isolation, validation, concurrent saves, manual
Enter enforcement, settings delivery and narration ownership/cancellation.

Source verification on 2026-10-23 completed in a verified foreground console
and headed Chrome:

* All 17 browser acceptance checks passed, including real OS speech, narration
  finishing before the first terminal key, real CMD read-back, manual Enter,
  editor timing and appearance, saved preferences, draft cancellation, presets,
  validation, a narrow viewport, and access from both control panels.
* The focused regression run executed 931 tests: 929 passed and two existing
  README documentation assertions failed (`test_blue_hat_section_exists` and
  `test_docs_describe_the_evidence_carryover`). The unchanged HEAD README also
  lacked both expected strings; these failures were unrelated to this feature.
  The later v1.91.0 documentation sweep restored both sections and both assertions
  passed in its separate 94-check validation run.
* JavaScript lint/parse checks, focused Python lint, migration consistency and
  `git diff --check` passed. The offline editor bundle was rebuilt.

The browser evidence is in `Temp/interaction-settings-visible/final-result.json`.
The regression transcript and baseline comparison are in
`Temp/interaction-settings-dev/regressions.log` and `baseline.log`.

The offline editor bundle and required runtime/source inventories include the
new dialog, speech lifecycle, migration and backend modules. Source validation
does not certify a rebuilt or installed executable. Never run the destructive
release builder solely to test this feature.

## Live Editor parameter reference

| Parameter | Default | Allowed values | Stored for |
|---|---|---|---|
| Velocidad de escritura (WPM) (`editor_wpm`) | 100 | 40–250 | Account |
| Use the same typing speed for both (`link_speeds`) | Off | On / Off | Account |
| Pause after each segment (seconds) (`segment_pause`) | 0 | 0–3 | Account |
| Teaching detail (`teaching_detail`) | Balanced | Brief, Balanced, Detailed | Account |
| Offer suggestions for each new field (`suggestions`) | On | On / Off | Account |
| Suggestion presentation (`suggestion_display`) | Ghost text and choices | Ghost text and choices, Choices only | Account |
| Follow Tlamatini’s typing (`follow_typing`) | On | On / Off | Account |
| Editor font size (px) (`editor_font`) | 13 | 12–24 | This account/browser |
| Show line numbers (`line_numbers`) | On | On / Off | This account/browser |
| Wrap long lines (`wrap`) | Off | On / Off | This account/browser |

## Terminater parameter reference

| Parameter | Default | Allowed values | Stored for |
|---|---|---|---|
| Velocidad de escritura (WPM) (`terminal_wpm`) | 50 | 20–250 | Account |
| Default shell (`shell`) | PowerShell | PowerShell, CMD, PowerShell 7 | Account |
| Command execution (`execution`) | Follow the task’s instructions | Follow the task’s instructions, I always press Enter | Account |
| Enable advisor in new terminals (`advisor`) | On | On / Off | Account |
| Command wait window (seconds) (`wait_seconds`) | 120 | 1–3600 | Account |
| No-output threshold (seconds) (`hang_seconds`) | 45 | 3–3600 | Account |
| User handoff wait (seconds) (`user_wait_seconds`) | 300 | 5–3600 | Account |
| Terminal font size (px) (`terminal_font`) | 13 | 12–24 | This account/browser |
| Cursor style (`cursor_style`) | Block | Block, Bar, Underline | This account/browser |
| Blink terminal cursor (`cursor_blink`) | On | On / Off | This account/browser |
| Preferred terminal layout (`terminal_layout`) | Tabs | Tabs, Tile, Side by side, Stacked, Grid | This account/browser |

## Voice parameter reference — v1.91.0

| Parameter | Default | Allowed values | Stored for |
|---|---|---|---|
| Narrate every Terminater command (`narrate_terminal`) | Off | On / Off | Account |
| Narrate each Live Editor teaching segment (`narrate_editor`) | Off | On / Off | Account |
| What to say (`narration_content`) | Brief explanation | Brief explanation, Command or code, Both | Account |
| When to speak (`narration_when`) | Before typing | Before typing, While typing, After typing | Account |
| Wait for narration before typing (`narration_wait`) | On | On / Off | Account |
| Announce command outcomes (`announce_outcomes`) | Errors and user-input requests | Errors and user-input requests, All results, Off | Account |

## Using voice and recovering from a refused save

Voice selection, rate, pitch and volume reuse **Config → Voice**. On a control
panel without that voice picker, choose the voice in the main chat in the same
browser. Ctrl+Shift+M toggles global mute; Escape stops speech. The wait-for-narration
setting applies when timing is Before typing. An explanation uses the optional tool
`explanation`; absent one, a generic step notice is spoken. Choose Command or code
to hear literal non-secret text. A muted or listening browser skips narration.

If another tab saved newer settings, reopen the dialog to load them before saving
your choices again. Invalid values reveal their tab and field. Save failure retains
the draft; it does not silently report success. Behavioral settings affect subsequent
actions, shell/advisor defaults affect new terminals, and appearance updates existing
views. See [the v1.91.0 release record](changes/2026-10-23-v1.91.0.md).
