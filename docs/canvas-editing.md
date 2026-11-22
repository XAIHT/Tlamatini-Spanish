<!-- Tlamatini Author Banner — Angela López Mendoza -->
# Editar y guardar documentos del Canvas

> Última versión publicada: **[v1.97.0](changes/2026-11-21-v1.97.0.md)**.

Introduced in v1.89.0 (2026-10-21), carried by v1.91.0 with configurable editor behavior. The tests below retain their actual dates; source verification does not certify a newly rebuilt installed executable.

Abre documentos de texto, código, Markdown y PDF en pestañas separadas del
Canvas del chat. Cada pestaña conserva su documento, estado de edición e
identidad de archivo. La barra ofrece **Guardar**, **Guardar como…**,
**Deshacer**, **Rehacer**, **Buscar** (con reemplazo) y **Ajustar**, junto a
Copiar, Actualizar, Limpiar canvas y Usar como contexto. El estado indica los
cambios sin guardar, la codificación y los finales de línea. Ctrl/Cmd+S guarda;
Ctrl/Cmd+Shift+S elige otro destino. Tab conserva la navegación por teclado;
Ctrl+[ / Ctrl+] cambia la sangría. El editor no ejecuta código.

El editor de código es CodeMirror 6, distribuido localmente con sus lenguajes y
licencias. Código, JSON, configuración y texto plano comparten el mismo modelo
de edición. Las extensiones de texto desconocidas siguen siendo editables, sin
coloreado de sintaxis. Markdown conserva **Vista previa** saneada y **Source**
editable sobre un mismo documento; cambiar de vista conserva los cambios y el
historial de deshacer. Copiar y Usar como contexto leen el texto editado. HTML y
SVG permanecen como código, nunca como páginas activas. PDF conserva su visor
completo: Guardar exporta una copia de los bytes originales sin cambiar el
documento mostrado ni su contexto preparado. Los flujos y las imágenes mantienen
sus rutas especializadas.

## Trabajar con varios documentos

Abre o suelta otro documento compatible para añadir una pestaña sin sustituir
las que ya están abiertas. Puedes mantener hasta **32 pestañas**. Pulsa una
para volver a ella: el texto conserva sus cambios, historial de deshacer,
selección y posición de desplazamiento. Markdown conserva su vista Previa o
Source. Cada PDF conserva su visor, estado de navegación y contexto preparado;
no se convierte en un editor de texto. La barra actúa sobre el documento activo;
**Limpiar canvas** cierra esa pestaña.

Con el foco dentro del Canvas o su barra de pestañas, **Alt+PageUp / Alt+PageDown**
cambia de documento. Ctrl+Tab / Ctrl+Shift+Tab también funciona si el navegador
entrega esas teclas a la página. Chrome normalmente reserva Ctrl+Tab para sus
propias pestañas: usa los atajos con Alt o pulsa una pestaña del Canvas. Estos
atajos no cambian documentos cuando el foco está en el chat, una terminal o un
diálogo abierto.

El **asterisco (*)** de una pestaña indica cambios aún no guardados en disco.
Abrir o cambiar de pestaña no los descarta. Guardar un documento no elimina el
asterisco de otro. Espera a que termine un guardado antes de cambiar de documento;
si falla o se cancela, los cambios se conservan. Cerrar una pestaña modificada
pide confirmación antes de descartarla. La protección al abandonar la página
comprueba **todas las pestañas**, incluidas las inactivas y los guardados pendientes.
El navegador controla la advertencia final y aun así puede cerrarse o fallar:
guarda todo antes de salir. No se garantiza recuperar pestañas sin guardar
después de recargar la página.

Editor en vivo e [Interactor](interactor.md) identifican el documento sobre el
que trabajan. Cambiar de documento cancela el tecleo en curso para impedir que
continúe en la siguiente pestaña. Interactor puede seleccionar otro documento
abierto para continuar una explicación; abrirlo no lo añade al contexto del chat.

Para ello usa `read`, consulta los metadatos con `documents` y activa un
`target_document_id` exacto mediante `activate`. La respuesta verificada identifica
el destino y su revisión; no se reutiliza la identidad de la sesión del navegador
como identidad del archivo. El historial y la selección de las otras pestañas
permanecen separados. Los PDF no admiten tecleo de Interactor.

## Elegir exactamente qué documentos serán contexto

**Abrir no significa usar como contexto.** Pulsa **Usar como contexto** en cada
documento que deba usar el chat normal. Por ejemplo, abre `notas.md`, `main.py`
y `manual.pdf`, y selecciona sólo `notas.md` y `manual.pdf`: `main.py` permanece
como pestaña del editor y no se incluye en ese conjunto de contexto. Preparar
un PDF sigue preguntando si deseas procesar imágenes; la opción predeterminada
utiliza únicamente el texto seleccionable.

La franja **Contexto del chat** enumera las capturas aceptadas. Sus pestañas
también muestran la insignia **Contexto**. Una selección sólo cambia cuando el
servidor acepta el conjunto completo; si rechaza la actualización, conserva el
contexto anterior. Una cuenta no puede sustituir el contexto mientras su chat
está ejecutándose. Se admiten hasta 32 documentos y 32 MiB de texto UTF-8
preparado, incluidos los separadores. Un exceso se rechaza sin recortarlo en
silencio; la capacidad de contexto del modelo es un límite adicional.

Editar un documento seleccionado muestra **Contexto · anterior** y cambia el
botón a **Actualizar contexto**. El modelo conserva la captura anterior hasta
que pulses ese botón y la sustitución termine correctamente. **Guardar no
actualiza el contexto; seleccionar contexto no guarda el archivo original.**
Una captura vigente ofrece **Quitar del contexto**, y cada etiqueta de la franja
permite quitar su captura. Cerrar una pestaña conserva su captura seleccionada
en esa franja: cerrar una vista no cambia silenciosamente lo que puede leer el
chat. Quita la etiqueta expresamente cuando ya no deba ser contexto. Elegir otro
archivo o carpeta como contexto sustituye la selección del Canvas mediante los
controles de contexto existentes.

**Actualizar** vuelve a leer únicamente el archivo de la pestaña activa y no
sustituye su captura de contexto. Si la conexión se pierde durante una selección,
desaparecen las insignias no confirmadas y se pide reconectar para verificar el
estado. Una respuesta tardía de otra petición no cambia la selección ni desbloquea
un trabajo nuevo. La reconexión espera a que termine una actualización pendiente.
Consulta el [registro de esta mejora y sus comprobaciones](changes/2026-11-21-canvas-document-tabs.md).

## Explicar el texto seleccionado

Selecciona uno o varios rangos y pulsa **Explicar selección**. Tlamatini explica
el texto exacto del momento del clic, incluidos los cambios sin guardar. Sin
selección explica el archivo actual. Conserva el borrador del chat y la selección
del editor; esta acción no edita ni guarda el archivo.

El botón funciona con cualquier combinación de Multi-Turn, Exec report, ACPX,
Ask Execs, Paso a paso, Modo compacto, Automodificación y contexto de internet.
Editor en vivo puede estar en pausa e Interactor desactivado. La explicación no
usa herramientas, historial ni contexto cargado previamente, y no espera la
reconstrucción del contexto provocada por las casillas. Aparece en el chat normal.

Una selección pequeña se envía sin el resto de un archivo grande. Se admiten
hasta 64 rangos y 262,144 unidades UTF-16 en total, sujetos a la capacidad real
del modelo configurado. Si la selección excede ese límite, se informa del problema
sin recortarla silenciosamente. La explicación no conoce el código fuera de los
fragmentos enviados. Consulta [Interactor](interactor.md) y la
[verificación del 12 de noviembre](changes/2026-11-12-canvas-selection-explanation.md).

## Dónde se guarda

**Guardar** escribe en el archivo autorizado por el navegador después de
comprobar el permiso y comparar todos sus bytes con la versión cargada. Si no
existe ese acceso, pide un destino. **Guardar como…** y **Guardar** en la barra
principal abren el diálogo nativo de Windows al usar Tlamatini localmente.
Elige cualquier carpeta con permiso de escritura, incluida la de tu proyecto;
no es obligatorio usar Descargas. Después de Guardar como nativo, Guardar usa
ese destino sin abrir otro selector y Actualizar lo vuelve a leer. Cada
exportación de PDF es una copia y vuelve a pedir destino.

Los navegadores remotos con File System Access usan su propio selector, en su
equipo. Las combinaciones no compatibles informan de la limitación; la
aplicación no sustituye en silencio el guardado por una descarga ni declara
guardado un archivo que no lo está.

Cancelar, rechazar permisos o sufrir un error de disco conserva el documento y
su marcador. Si otro programa cambia el destino, Guardar rechaza sobrescribirlo;
usa Guardar como para conservar tus cambios aparte o Actualizar para leer la
versión en disco. Cerrar una pestaña, Limpiar canvas y Actualizar piden permiso
antes de descartar sus cambios; abrir otro documento añade una pestaña. Los
cambios realizados durante un guardado siguen pendientes después de escribir
esa captura. Editar durante una carga pendiente invalida esa sustitución.
Un documento modificado en cualquier pestaña activa también la advertencia al
abandonar la página; guarda antes de cerrar para no perder sus documentos en
memoria.

Editar no actualiza silenciosamente el contexto ya cargado por el modelo.
**Actualizar contexto** entrega el texto actual del documento seleccionado;
Guardar conserva la indicación de contexto pendiente. Guardar con otro nombre
no declara ese nombre como contexto ya cargado.

UTF-8, UTF-8 BOM and BOM-marked UTF-16 LE/BE decode strictly. Unsupported or
malformed encodings and binary content are refused before replacing the canvas.
Unedited files retain exact bytes. Edited files retain encoding and BOM; existing
line terminators are retained by line, and additional lines use the first
original terminator (LF for a file without one). Empty files can be saved. Text
editing and native saves have a 64 MiB limit.

Desde la corrección del 2026-11-07, un carácter de control aislado (por ejemplo,
BEL o retroceso dentro de un README generado desde PowerShell) no convierte
todo el documento en binario. Después de decodificar estrictamente, el editor
rechaza NUL y contenido con más de un 30 % de controles no blancos. Los controles
aislados se conservan, no se eliminan ni se «reparan» al abrir o guardar.

## Implementation and safeguards

`agent_page_canvas_tabs.js` administra las identidades de las pestañas, el estado
suspendido de cada documento y la selección explícita de contexto.
`canvas_documents_context.py` valida cada conjunto completo, resuelve los tokens
PDF para el usuario autenticado y escribe un paquete separado dentro de la
aplicación. Publicar es una operación atómica: un fallo conserva la selección
anterior. Una reserva de ejecución por cuenta impide que un chat u otra
sustitución de contexto compita con esa publicación.

`agent_page_canvas.js` retains document loading, refresh, context and generation
ownership. `agent_page_editing.js` owns the editable snapshot, saved baseline,
encoding, toolbar, write flow and dirty guard. The original code element remains
a hidden, synchronized compatibility mirror; CodeMirror state is the editing
authority. `agent_page_markdown.js` accepts source changes and sanitizes each
preview through the existing Marked/DOMPurify pipeline.

`canvas_file_views.py` exposes authenticated, CSRF-protected, loopback-only POSTs
at `/agent/canvas/save/` and `/agent/canvas/read/`. A first save grants a random,
expiring capability for the path chosen in the native dialog. Tokens belong to
both the account and login session; browser-supplied absolute paths are refused.
Subsequent writes require the last accepted content revision. Reading a newer
revision does not implicitly approve overwriting it. The browser adopts it only
when that refresh commits. Capabilities are bounded, expire after 12 idle hours,
and disappear at server restart; Save as… grants access again.

Writes stage a sibling file on the destination volume, flush it, recheck the
revision and replace the destination. Existing Windows files use `ReplaceFileW`
to preserve their security settings, named streams and creation time. An original
backup supports recovery from partial Windows failures; if Windows refuses
recovery, the error names the retained recovery copy. Successful saves remove
that backup. New files use `os.replace`. Failed staging preserves the original
and removes the temporary file. Native Save As uses a
new independent `native_dialogs.pick_save_file` with Windows overwrite
confirmation, sharing the existing Win32 definitions and foreground helper.
The protected database backup/restore mechanics are unchanged.

The build and source snapshot inventories carry the adapter, style, bundle,
licenses, manifest, sources and harness. Rebuild the offline bundle with
`node scripts/build_canvas_editor.mjs` in a verified foreground PowerShell
`-NoExit` console. Pinned dependencies and the lockfile reproduce the bundle;
startup and installed use require no npm or CDN.

## Research before implementation

- [CodeMirror guide](https://codemirror.net/docs/guide/) and
  [bundling example](https://codemirror.net/examples/bundle/): use a real document
  model and an offline browser bundle.
- [CodeMirror keyboard navigation](https://codemirror.net/examples/tab/): avoid
  trapping keyboard users in the source editor.
- [Chrome File System Access](https://developer.chrome.com/docs/capabilities/web-apis/file-system-access/)
  and [MDN Save picker](https://developer.mozilla.org/en-US/docs/Web/API/Window/showSaveFilePicker):
  permission, user activation and browser-availability boundaries.
- [Windows Common Item Dialog](https://learn.microsoft.com/en-us/windows/win32/shell/common-file-dialog):
  native destination selection and overwrite confirmation. The surgical
  integration reuses Tlamatini's Win32 common-dialog family.
- [Windows replacement semantics](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew):
  preserve existing file metadata and retain recovery data on partial failure.
- [Django CSRF](https://docs.djangoproject.com/en/5.2/howto/csrf/),
  [Python replacement semantics](https://docs.python.org/3/library/os.html#os.replace),
  [Marked sanitization warning](https://marked.js.org/): request authorization,
  same-volume write staging and safe preview rendering.

## Verificación de varios documentos (2026-11-21)

Desde una consola de desarrollo visible y en primer plano, ejecuta
`python -B -u scripts/canvas_tabs_visible.py` en la raíz de esta edición.
La prueba usa Chrome visible, una cuenta/base de datos aislada, diálogos nativos
Abrir/Guardar y archivos en `Temp/canvas-tabs-visible`. Revisa
`browser-waiting.png` antes de crear allí `browser-visible-confirmed`.
Cada `run-N/SUMMARY.html` contiene los pasos y capturas del escritorio completo.
Crea `close.confirmed` para cerrar el navegador de prueba o `rerun.confirmed`
para repetir las comprobaciones.

La ejecución completa inglesa pasó 28 comprobaciones; una prueba posterior
también verificó que Interactor abre texto desde una pestaña PDF activa.
La ejecución completa española pasó las 29 comprobaciones. Cada edición pasó
46 pruebas de transacciones de contexto, 40 de protocolo/propiedad de Interactor
y el lint dirigido de Python/JavaScript. Se verifican A+B seleccionados con C
excluido, contexto anterior o rechazado, deshacer/guardado independientes,
carreras con guardados y lecturas demorados, aviso al salir por pestañas inactivas
sin guardar, estado PDF conservado y entrada real del teclado de Windows.

La prueba del navegador captura el WebSocket del chat normal e inyecta
explícitamente sus confirmaciones de contexto. El enrutamiento, la propiedad
por cuenta, la persistencia y la reversión del backend se prueban por separado,
sustituyendo las fronteras de modelo/red. Estos resultados no certifican la
ingesta con un modelo real ni un ejecutable instalado recompilado. El guardado
nativo, la preparación de texto PDF y las acciones autenticadas de Interactor
usan sus implementaciones locales reales.

## Verification

Follow [the visible execution policy](../TestsVisiblesAndVisibleExecutionFromClaude2Codex.md).
From the verified foreground console run `python -u scripts/canvas_editing_visible.py`.
It uses real Chrome (`headless=False`), an isolated database, native file dialogs,
keyboard editing and exact disk-byte assertions. Inspect Shoter's full-desktop
`Temp/canvas-editing-visible/browser-waiting.png` before creating the visibility
gate. Monitor `live.log` every 5–15 seconds. Results and photos appear in each
`run-N/SUMMARY.html`; `final-result.json` records the outcome. Chrome remains open
for inspection until `close.confirmed`; `rerun.confirmed` repeats the checks.
Delayed-response cases are labeled fault injection. The model WebSocket is
captured; these are source editing/save checks, not model or frozen-build tests.

Verified on 2026-10-21: **29 distinct browser checkpoints passed** across focused
visible Chrome runs 7, 9, 11 and 12. They cover native Save As outside Downloads,
original browser-handle Save and Ctrl+S with Chrome's real write-permission
dialog, Rust/Python/JSON/HTML/Markdown/plain text, Unicode and encoding retention,
empty files, Undo/Redo, cancellation, external conflicts, delayed operations,
malformed/binary refusal, failed generated loads, narrow layouts, and PDF copies.
The final browser process exited 0. Earlier harness failures remain in the log;
the consolidated report selects only verified checkpoints:
`Temp/canvas-editing-visible/ACCEPTANCE.html` and `acceptance.json`.

The final Django regression run passed **93 tests, with 2 skips** across canvas
saving, native dialogs, file-drop routing and PDF context. This includes the
real Windows named-stream/creation-time preservation check and simulated partial
replacement recovery. Full JavaScript lint and parsing (99 files), targeted
Python Ruff checks and `git diff --check` passed. Collected static assets were
refreshed before the regression run. Evidence is retained in
`Temp/canvas-editing-visible/final-validation-transcript.txt`.

## Regresión de Markdown y caracteres de control (2026-11-07)

Desde una consola visible y en primer plano, ejecuta
`node --test Tests/test_canvas_text_decoding.cjs`. Comprueba UTF-8, UTF-8 con
BOM, UTF-16 LE/BE, conservación exacta al guardar y rechazo de archivos binarios
o mal codificados. `npm test` incluye esta regresión. Las comprobaciones del
router de archivos ahora verifican los mensajes reales en español.

Para revisar el canvas visualmente, ejecuta
`python -u scripts/canvas_text_decoding_visible.py --file C:\proyecto\README.md`
en esa consola. El harness abre Chrome visible, usa el selector nativo y deja
la ventana abierta al terminar. Su base de datos, perfil de Chrome y evidencia
quedan aislados dentro de `Temp/canvas-text-decoding-visible` del repositorio.
No modifica el documento original ni la base de datos de la aplicación instalada.

Verificación del 2026-11-07 desde consola visible: **13/13** pruebas del decoder
y guardado, **138/138** comprobaciones del router, lint JavaScript y análisis de
**110** archivos JavaScript correctos. La revisión completa de Python compiló
y pasó Ruff para **960** archivos propios, incluido el pase de nombres no
definidos. Evidencia compartida de ambas ediciones:
`C:\Development\XAIHT\Tlamatini\Temp\canvas-readme-parity\lint-results.json`.
El wrapper local de `npm` se detuvo al solicitar aprobación de un script de
dependencia; ESLint se ejecutó directamente con las dependencias ya instaladas,
sin cambiar esa aprobación ni la configuración del gestor de paquetes.

La prueba visual de siete pasos del README de Ruster se realizó en la edición
inglesa; no constituye una aceptación visual de la edición española ni de un
ejecutable recompilado. Angela realizará la compilación y la prueba instalada.

## Editor appearance and tutoring settings (v1.91.0)

**Config → Live Editor & Terminater** and the canvas Settings button control the
real editor font (12–24 px, default 13), line numbers and wrapping. These appearance
choices persist per account in this browser and apply when a document is mounted.
They do not alter the file's contents or dirty baseline. The Live Editor tab also
configures Interactor pacing, segment pauses, suggestions and cursor following;
the Voice tab controls segment narration. Account behavior and local appearance
have separate storage. See [Interaction settings](interaction-settings.md).
