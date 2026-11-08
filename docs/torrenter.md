# Torrenter

> Última versión publicada: **[v1.92.4](changes/2026-11-08-v1.92.4.md)**.

Torrenter es un agent de flow de Tlamatini y se puede invocar desde el chat con `chat_agent_torrenter`. Controla las descargas del servicio de Windows Tlachihuani Jobs, que se instala por separado y expone su API en `http://127.0.0.1:12064/api/v1`. Jobs administra la transferencia, sus archivos y el registro de operaciones. Puedes cerrar el chat, Agentic Control Panel o el browser y volver al mismo job.

La página de descargas está en `agent/torrenter_workspace/`. El actualizador sustituye su HTML, JavaScript y CSS junto con el controlador. La copia para automodificación incluye los mismos archivos. Jobs y XT se instalan por separado y deben comprender la versión del protocolo que usa el panel.

## Vincular una cuenta

1. Selecciona **Start Services** en el menú de XT e inicia sesión en Tlamatini.
2. Abre **Paneles → Descargas de Torrenter** para ver las mismas descargas que en el chat. También puedes entrar desde XT. Si ambas ediciones están abiertas, elige una. Recargar conserva tu sesión. Al cerrarla termina el acceso a su cola desde el navegador.
3. Activa **Torrenter** en Configurar Agents y **Chat-Agent-Torrenter** en Configurar MCPs/Tools. Si usas Compact mode, selecciona ambos. El chat admite Multi-Turn, Ask Execs y Exec Report.

El servidor asigna a cada cuenta de Django un perfil estable de Jobs. El canal de control autenticado de Windows emite una credencial limitada a esa cuenta. El navegador usa su sesión de Django y su token CSRF. Cada edición tiene su propia cookie de sesión.

## Archivos en Descargas de Windows

Jobs comprueba el hash y publica la copia en la carpeta Descargas real del usuario de Windows, incluso si está redirigida. Cada entrega queda en `Torrenter/<UUID de cuenta>/<ID de trabajo>/`. La cabecera identifica la cuenta y el panel indica el destino efectivo. El servicio conserva su copia privada para reanudar o volver a verificar la transferencia.

El controlador prepara únicamente la carpeta de salida de esa cuenta y concede acceso al servicio. La entrega ordinaria no requiere privilegios de administrador. Al reconectar, Jobs puede publicar un trabajo ya terminado sin descargarlo otra vez. Cerrar el navegador, detener el servicio o quitar el registro conserva las copias. La vista previa de borrado enumera tanto la copia privada como la entregada.

Un manifiesto con `verified=true` acredita la copia publicada. Si Windows rechaza Descargas, Jobs intenta usar `content_generated/Torrenter/<cuenta>/<trabajo>/` de esta edición. Si ambos destinos fallan, el panel muestra el error y se conserva el original privado. El servicio señala las copias modificadas o ausentes. Si la versión instalada solo conoce su almacén privado, el panel pide actualizar Jobs.

Al seleccionar una transferencia se abre su panel de detalles. Puedes ajustar su altura en Preferencias. La cola aprovecha el espacio disponible de la ventana. Las solicitudes de credenciales usan comunicación interna de Windows sin abrir consolas. Los cambios en el controlador Python se distribuyen con el ejecutable de Tlamatini.

## Iniciar una transferencia

Abre **Paneles → Fuentes de Torrenter**. Elige un archivo `.torrent` o pega un vínculo magnet y selecciona **Revisar metadatos**. Copia el ID de inspección en el chat. También puedes pegar un magnet en un mensaje: Tlamatini lo sustituye por una referencia cifrada de corta duración antes de guardar el historial o enviar la solicitud al modelo.

Ejemplo de conversación, en orden:

1. «Usa Torrenter para revisar la inspección `<inspection_id>`. Muéstrame los IDs y tamaños de sus archivos».
2. «Descarga el archivo 0 de esa inspección en downloads. Deja desactivado el seeding».
3. «Consulta el job `<job_id>`. Indica el estado solicitado, la fase observada y los bytes seleccionados y verificados».
4. «Muéstrame el manifiesto verificado del job con la ubicación del archivo y su SHA-256».

Es posible que un magnet necesite peers antes de mostrar los archivos. Vuelve a consultar la inspección con el mismo ID. Un manifiesto publicado con `verified=true` identifica el archivo terminado. Si una pieza compartida contiene bytes de archivos que no elegiste, Torrenter conserva el conteo del motor en `engine_verified_bytes` y reporta los bytes verificados de tu selección después de publicar el archivo. Que la tasa sea cero, que Jobs acepte la operación o que el agent termine su turno no prueba que la descarga haya terminado.

Si los cuatro espacios de consulta de metadatos están ocupados, Jobs puede responder con `lookup_state: queued`. Consulta el mismo ID de inspección. Cuando se resuelvan los metadatos podrás elegir los archivos. La cola de inspección es independiente de la entrega verificada.

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

El resultado de búsqueda conserva el magnet completo y sus trackers en una referencia privada. Consulta la misma inspección hasta que estén disponibles los archivos. Ante un 401, comprueba la sesión. Un 403 requiere revisar los permisos o la aprobación en XT. Un 404 exige comprobar el ID de la cuenta y un 412, volver a leer la revisión. Si Jobs no responde, consulta Servicios en XT. Un trabajo a la espera de pares sigue activo.


## Repetir las pruebas de desarrollo

Las referencias de origen y los registros se guardan en la carpeta privada
`TorrenterData` de la edición. Jobs mantiene las descargas incompletas en su
carpeta de estado. No se usan perfiles de Windows ni `%TEMP%` para trabajo temporal.
Al publicar, el destino final puede contener un archivo provisional hasta el cambio de nombre.

Usa una consola PowerShell visible y verificada. Mantén el servidor en otra ventana visible. La prueba abre Chrome, solicita la contraseña de la cuenta de desarrollo, carga un torrent de prueba y lo envía mediante la herramienta real del chat. Recupera el recibo y comprueba por separado el SHA-256 del archivo publicado de 13 936 bytes. Al finalizar muestra el ID del trabajo.

```powershell
Set-Location -LiteralPath 'C:\Development\XAIHT\Tlamatini-Spanish\Tlamatini'
python manage.py test agent.test_torrenter agent.test_ask_execs_allowlist agent.test_agent_display_names agent.tests.ExecReportCaptureTests
python tests_e2e/torrenter_console_windows.py
python tests_e2e/torrenter_live.py --username YOUR_USERNAME --port 18084
```
