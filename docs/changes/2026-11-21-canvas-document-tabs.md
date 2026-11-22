<!-- Tlamatini Author Banner — Angela López Mendoza · @angelahack1 -->
# Canvas con varias pestañas y contexto explícito

> Última versión publicada: **[1.97.0](2026-11-21-v1.97.0.md)**. Documentación actualizada el 21 de noviembre de 2026.

## Qué cambia para el usuario

El Canvas del chat admite hasta **32 documentos abiertos**: texto, código,
Markdown y PDF. Abrir o soltar otro documento añade una pestaña. Cada archivo
mantiene sus cambios, historial de deshacer y rehacer, selección, desplazamiento,
codificación, finales de línea y destino de guardado. Markdown conserva su vista
y sus recursos autorizados; cada PDF conserva su visor, página, zoom, rotación,
modo de desplazamiento y preparación de contexto. Guardar un PDF exporta una
copia de sus bytes originales; no convierte el visor en un editor.

Los botones actúan sobre la pestaña activa. **Limpiar canvas** la cierra. Un
**asterisco** indica trabajo sin guardar y el cierre pide confirmación antes de
descartarlo. Un guardado pendiente impide cambiar de documento. Al abandonar la
página se consideran todas las pestañas, incluidas las inactivas y los guardados
pendientes. El navegador controla la advertencia final: no se promete impedir
su cierre ni recuperar documentos sin guardar después de recargar o de un fallo.

Con el foco dentro del Canvas, **Alt+PageUp / Alt+PageDown** cambia de documento.
**Ctrl+Tab / Ctrl+Shift+Tab** funciona cuando el navegador entrega esas teclas a
la página; Chrome normalmente las reserva para sus propias pestañas. No se
capturan estos atajos desde el chat, las terminales ni los diálogos.

## Qué contenido recibe Tlamatini

Abrir un archivo **no** lo añade al contexto del chat. **Usar como contexto**
selecciona expresamente una captura; varias capturas pueden coexistir con otras
pestañas abiertas sin seleccionar. La franja **Contexto del chat** y las insignias
de las pestañas muestran el conjunto aceptado. Se admiten hasta **32 documentos
y 32 MiB de texto UTF-8 preparado**, incluidos los separadores; el presupuesto
del modelo es un límite adicional. Los excesos se rechazan sin recortar contenido.

Editar, actualizar desde disco o renombrar un documento seleccionado puede dejar
su captura anterior: **Contexto · anterior** y **Actualizar contexto** permiten
revisar y sustituirla. Guardar no actualiza el contexto; seleccionar contexto no
guarda el original. **Quitar del contexto** o la etiqueta correspondiente elimina
solo esa captura. Cerrar una pestaña conserva su captura en la franja hasta que
se quite expresamente. Elegir otro archivo o carpeta con los controles generales
de contexto sustituye el conjunto del Canvas.

El servidor publica el conjunto completo únicamente después de prepararlo y
aceptarlo. Un rechazo conserva el contexto anterior; una desconexión elimina
las insignias no confirmadas y pide reconectar para verificar el estado. No se
presenta una respuesta perdida como éxito. Las respuestas tardías de otra
petición no desbloquean una operación nueva. La reconexión espera a que termine
una actualización de contexto pendiente.

## Editor en vivo e Interactor

`read` obtiene el documento activo, incluidos sus cambios sin guardar.
`documents` lista metadatos de las pestañas, sin leer su contenido ni añadirlo al
contexto. Tras leer el origen, `activate` usa un `target_document_id` exacto y
devuelve la lectura verificada del destino. La identidad del documento es distinta
de la sesión del navegador. Las ediciones siguientes quedan vinculadas a esa
identidad y revisión. Cambiar manualmente de documento detiene el tecleo pendiente;
no se repite en otro archivo. Los PDF siguen siendo de solo lectura para Interactor.

**Explicar selección** sigue siendo independiente: captura los fragmentos del
documento activo al pulsar el botón, conserva el borrador del chat y no modifica
las capturas elegidas como contexto. Actualizar un archivo desde disco invalida
las lecturas anteriores; una respuesta tardía nunca sustituye otra pestaña.

## Implementación y comprobación

`agent_page_canvas_tabs.js` coordina los documentos y sus capturas; los adaptadores
de edición, Markdown y PDF conservan su estado. `canvas_documents_context.py`
valida la cuenta, los límites y los tokens PDF, y publica el contexto de forma
transaccional. Interactor mantiene sus comprobaciones de identidad, revisión y
cancelación. Los inventarios de recursos, importaciones del ejecutable y copia
del código fuente incluyen los nuevos archivos en ambas ediciones.

Las comprobaciones del 21 de noviembre de 2026 separan **46 pruebas del contexto**,
**40 pruebas de Interactor** y los recorridos de navegador visibles. El recorrido
inglés registró 28 comprobaciones, más dos comprobaciones de teclado nativo y
una de extracción PDF; el español registró 29, más una de extracción PDF. Se
ejercitaron guardados y lecturas de archivos reales, visores PDF y los controles
de documentos. Los mensajes del chat usados para comprobar las confirmaciones
del contexto se inyectaron de forma deliberada: no constituyen una conversación
completa con el modelo. No se compiló ni se certificó un nuevo ejecutable instalado.

Guías: [edición y contexto](../canvas-editing.md), [actualización desde disco](../canvas-refresh.md),
[Markdown](../markdown-canvas.md), [PDF](../pdf-canvas.md), [Interactor](../interactor.md)
y [referencia rápida](../canvas-and-interactor-quick-reference.txt).
