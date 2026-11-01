# Torrenter

Torrenter es un agent de flow de Tlamatini y se puede invocar desde el chat con `chat_agent_torrenter`. Controla las descargas del servicio de Windows Tlachihuani Jobs, que se instala por separado y expone su API en `http://127.0.0.1:12064/api/v1`. Jobs administra la transferencia, sus archivos y el registro de operaciones. Puedes cerrar el chat, Agentic Control Panel o el browser y volver al mismo job.

The signed-in page is carried with Tlamatini in `agent/torrenter_workspace/`.
Self-update replaces its HTML, JavaScript and CSS together with the controller.
A self-modification snapshot includes the same files for rebuilding. Jobs and XT
remain separately installed. Changes to their API must remain compatible with the
workspace protocol or provide a coordinated service update.

## Vincular una cuenta

1. Selecciona **Start Services** en el menú de XT e inicia sesión en Tlamatini.
2. Abre **Paneles → Descargas de Torrenter** para ver las mismas descargas que en el chat. También puedes entrar desde XT. Si ambas ediciones están abiertas, elige una. Recargar conserva tu sesión. Al cerrarla termina el acceso a su cola desde el navegador.
3. Activa **Torrenter** en Configurar Agents y **Chat-Agent-Torrenter** en Configurar MCPs/Tools. Si usas Compact mode, selecciona ambos. El chat admite Multi-Turn, Ask Execs y Exec Report.

El servidor asigna a cada cuenta de Django un perfil estable de Jobs. El canal de control autenticado de Windows emite una credencial limitada a esa cuenta. El navegador usa su sesión de Django y su token CSRF. Cada edición tiene su propia cookie de sesión.

## Files in Windows Downloads

The updated Jobs service publishes a hash-verified copy to the Windows operator's
actual Downloads folder under `Torrenter/<account UUID>/<job ID>/`. The account
heading identifies the signed-in Tlamatini user; the location above the queue and
**Verified output** show the destination. Windows folder redirection is respected.
The private service copy remains available for resume and recheck.

The ordinary local controller prepares only that account's output directory and
grants the Jobs service write access there. Neither edition needs administrator
rights for routine delivery. The private journal remains protected. An existing
completed job is copied on reconnect after the service update, without downloading
it again. Copies survive service shutdown, browser closure and record removal.
Explicit **Erase files** approval lists both the private and delivered copies.

`verified=true` in a delivered manifest means the copy was checked and published.
Si Windows rechaza Descargas, Jobs intenta guardar en
`content_generated/Torrenter/<account>/<job>/` de esta edición. El panel y el registro
muestran el destino efectivo. Si ambos destinos fallan, la espera informa del error
y el original verificado sigue disponible. Una copia de usuario modificada o ausente
copy is reported rather than silently overwritten or recreated. An older Jobs
version produces **Se requiere actualizar el servicio**, not a claim that a private service
file was saved to Downloads.

The workspace fills the browser viewport and keeps its footer at the bottom. The
queue receives the unused height; selecting a transfer opens the details pane.
**Preferences → Altura del panel de detalles** adjusts that pane. Scrolling is retained
where the content actually exceeds the available pane or viewport.

Native credential calls are internal IPC and do not allocate console windows.
Development verification still runs in a visible foreground console and headed
Chrome. Full Tlamatini executables must be rebuilt to deliver frozen Python
changes; updating Jobs alone does not replace either Tlamatini executable.

## Iniciar una transferencia

Abre **Paneles → Fuentes de Torrenter**. Elige un archivo `.torrent` o pega un vínculo magnet y selecciona **Revisar metadatos**. Copia el ID de inspección en el chat. También puedes pegar un magnet en un mensaje: Tlamatini lo sustituye por una referencia cifrada de corta duración antes de guardar el historial o enviar la solicitud al modelo.

Ejemplo de conversación, en orden:

1. «Usa Torrenter para revisar la inspección `<inspection_id>`. Muéstrame los IDs y tamaños de sus archivos».
2. «Descarga el archivo 0 de esa inspección en downloads. Deja desactivado el seeding».
3. «Consulta el job `<job_id>`. Indica el estado solicitado, la fase observada y los bytes seleccionados y verificados».
4. «Muéstrame el manifiesto verificado del job con la ubicación del archivo y su SHA-256».

Es posible que un magnet necesite peers antes de mostrar los archivos. Vuelve a consultar la inspección con el mismo ID. Un manifiesto publicado con `verified=true` identifica el archivo terminado. Si una pieza compartida contiene bytes de archivos que no elegiste, Torrenter conserva el conteo del motor en `engine_verified_bytes` y reporta los bytes verificados de tu selección después de publicar el archivo. Que la tasa sea cero, que Jobs acepte la operación o que el agent termine su turno no prueba que la descarga haya terminado.

## Acciones

En Agentic Control Panel, **Esperar a que termine la descarga** tiene el valor inicial **No**. El nodo devuelve su recibo y activa los agents conectados cuando Jobs admite la transferencia. Elige **Sí** para esperar hasta que Jobs publique el manifiesto verificado de los archivos seleccionados. Pausar conserva la espera. Detener, cancelar o fallar la descarga termina la espera con un error. En YAML usa `wait_for_completion: true` o `false`.

Haz clic derecho en el nodo Torrenter y abre su log para ver los nombres, archivos seleccionados, tamaños, magnet completo, rutas verificadas y hashes. Los metadatos cargados tienen un magnet generado. El archivo de actividad pertenece al flow de esa cuenta. El chat recibe un comprobante por separado.

Envía al tool del chat una `action` y un objeto `arguments`. En un nodo del canvas, escribe el mismo objeto JSON en el campo **arguments**. Cada invocación hace una solicitud lógica a Jobs. La espera consulta el job por un máximo de 30 segundos. Usa su ID para seguir consultándolo.

| Objetivo | Acciones | Campos y comportamiento |
|---|---|---|
| Descubrir e inspeccionar | `capabilities`, `list`, `inspect`, `inspection` | La lista acepta filtros, `limit` y `cursor`. Para inspeccionar, usa un `info_hash` público v1 o una `source_ref` privada. Consulta la inspección con `inspection_id`. |
| Iniciar una descarga | `download` | Indica `inspection_id`, `metadata_revision`, los IDs explícitos en `selected_file_ids` y una `destination_root_id` (`downloads` o `archive`). Las prioridades y políticas opcionales respetan los valores false y cero. |
| Volver a consultar | `status`, `wait`, `operation`, `events` | Usa el ID del job para consultar o esperar, el ID de operación para recuperar el comprobante y el cursor para leer eventos. Si el cursor vence, vuelve a consultar la lista. |
| Inspeccionar un job | `files`, `peers`, `trackers`, `web_seeds`, `statistics`, `manifest` | Indica el ID del job. El manifiesto devuelve paths verificados una vez que Jobs ha publicado los archivos. |
| Controlar | `pause`, `resume`, `stop`, `start`, `cancel`, `recheck`, `reseed`, `move` | Indica `job_id` y la última `revision`. Puedes pausar y reanudar. Detener conserva los datos parciales para continuar después. Cancelar termina la transferencia incompleta. Detén el job antes de moverlo a otra carpeta autorizada. |
| Editar | `select`, `update`, `set_trackers`, `set_web_seeds` | Con el job detenido puedes cambiar los archivos seleccionados y sus prioridades. Actualiza etiquetas, posición en cola, velocidades o políticas. Prepara las fuentes privadas en Fuentes de Torrenter y envía la referencia al job detenido. |
| Configurar la cuenta | `categories`, `tags`, `label`, `settings`, `update_settings`, `totals` | Crea, renombra o elimina etiquetas por colección. Usa la revisión actual al cambiar los ajustes predeterminados. Los totales corresponden a tu cuenta. |
| Varios jobs | `batch` | Indica la `transition` (pause, resume, stop o start) y `jobs`, una lista de IDs con la revisión de cada job. Revisa el resultado de cada elemento. |
| Eliminar un registro | `remove_job` | Indica el ID y la revisión de un job detenido, cancelado o terminado. Los archivos permanecen en el disco. |
| Borrar archivos propios | `delete_preview`, `delete_content` | Revisa los archivos exactos de un job detenido o terminado y aprueba esa vista en XT. Envía `preview_id` y la revisión original y consulta la operación. Solo XT puede aprobar el borrado. |

Las escrituras persistentes aceptan una `operation_key` de 32 dígitos hexadecimales en minúsculas. Si no sabes si se aplicó el cambio, reintenta con la misma clave y los mismos argumentos para recuperar el comprobante original. Una solicitud distinta necesita otra clave. Si la revisión está desactualizada, vuelve a consultarla. El `run_id` del chat identifica el proceso cliente; Jobs usa `job_id`, `inspection_id` y `operation_id` para identificar sus propios recursos.

## Flows y diagnóstico

Arrastra **Torrenter** a Agentic Control Panel, abre la configuración y elige una acción. Por ejemplo, selecciona `list` en **action** e introduce `{"limit":10}` en **arguments**. Conecta el output a Parametrizer o Forker. Cada activación genera un registro `INI_SECTION_TORRENTER` con el resultado y el cuerpo JSON de la respuesta. Cada escritura nueva usa su propia clave. Si se reanima una escritura interrumpida, utiliza la clave guardada.

A search result passes its complete magnet, including trackers, as a private source reference. Poll the inspection until its file list is ready before submitting. For HTTP 401, check the signed-in account. For 403 check scopes or XT approval, for 404 check the owned ID, and for 412 re-read the revision. When Jobs is unavailable, check the XT Services panel. A transfer waiting for a peer remains a live service job.


## Repetir las pruebas de desarrollo

Las referencias de origen y los registros se guardan en la carpeta privada
`TorrenterData` de la edición. Jobs mantiene las descargas incompletas en su
carpeta de estado. No se usan perfiles de Windows ni `%TEMP%` para trabajo temporal.
Al publicar, el destino final puede contener un archivo provisional hasta el cambio de nombre.

From a verified visible foreground PowerShell console, keep the server running in its own visible window. The live check opens headed Chrome, asks for the signed-in development account’s password, uploads a generated torrent, submits it through the real wrapped tool, replays its receipt and independently checks the SHA-256 of the published 13,936-byte fixture. It prints the completed job ID for inspection.

```powershell
Set-Location -LiteralPath 'C:\Development\XAIHT\Tlamatini-Spanish\Tlamatini'
python manage.py test agent.test_torrenter agent.test_ask_execs_allowlist agent.test_agent_display_names agent.tests.ExecReportCaptureTests
python tests_e2e/torrenter_console_windows.py
python tests_e2e/torrenter_live.py --username YOUR_USERNAME --port 18084
```
