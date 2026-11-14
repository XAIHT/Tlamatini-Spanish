<!-- Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1 -->
# Tlamatini y Remote-Controller

> Última versión publicada: **[v1.93.5](changes/2026-11-12-v1.93.5.md)**.

La integración en código fuente del 13 de noviembre conecta tu cuenta de Tlamatini
con **Tlachihuani-RC Server**, un servidor independiente administrado en XT como
**Remote-Controller**. Incluye conversaciones de texto vinculadas a la cuenta,
aprobaciones de ejecución, cancelación y el inicio de la aplicación instalada.
Las ediciones en inglés y español tienen el mismo comportamiento y mantienen
identidades de cuenta separadas.

El perfil actual funciona **solo en esta PC**, normalmente en
`http://127.0.0.1:12481`. El acceso por red, el transporte poscuántico, la distribución
de un cliente nativo con confianza independiente y la captura del micrófono del
teléfono siguen sin estar disponibles. Las pruebas del código fuente no
certifican un paquete instalado actualizado ni todo el diseño de acceso remoto
aprobado. Usa compilaciones compatibles que incluyan ambas integraciones.

## Habilitar tu cuenta y conectar un dispositivo

1. Abre **XT → Show panel → Services → Remote-Controller** e inicia el servicio.
   La instalación lo deja con inicio Manual y detenido. Torrenter conserva sus
   propios controles.
2. En esta PC, inicia sesión en la cuenta deseada de Tlamatini y abre
   **Paneles → Tlachihuani · Remote-Controller**. La página de cuenta se abre en otra
   pestaña y permanece disponible mientras el chat principal está ocupado.
3. Confirma tu contraseña actual de Tlamatini y pulsa **Habilitar esta cuenta**.
   Esto hace que la cuenta esté disponible en XT; no aprueba dispositivos ni inicia
   servicios. Tlamatini comprueba la contraseña y no la envía al cliente RC.
4. En la pestaña **Access** de Remote-Controller en XT, selecciona la cuenta, elige
   sus permisos y crea una invitación. Abre el cliente RC desde XT, introduce la
   invitación y compara la **huella completa del dispositivo** en ambos lugares.
   Aprueba en XT el dispositivo cuya huella coincida.

La invitación dura cinco minutos y solo puede usarse una vez. El dispositivo
aprobado puede reconectarse con su clave de firma sin otra invitación. El nombre
visible es una etiqueta: la autorización utiliza identificadores inmutables y la
edición. Una cuenta en inglés y otra en español con el mismo nombre son distintas.

La dirección anterior es local: abrirla en un teléfono apunta al propio teléfono.
Esta implementación no hace que la PC sea accesible por la red local o Internet.

## Conversación y control de ejecución

Envía texto en la vista **Conversation** del cliente RC. Se utilizan el motor de
chat, el historial y la configuración existentes de esa cuenta de Tlamatini. Una
solicitud aceptada se distingue de una respuesta terminada. El chat de escritorio
y el remoto no pueden ejecutar simultáneamente solicitudes al modelo para la
misma cuenta.

Pulsa **Load recent conversation** para recuperar los mensajes guardados de esta
cuenta sin enviar un prompt nuevo. La respuesta incluye como máximo 40 mensajes
dentro de un límite de 24,000 bytes JSON e indica cualquier contenido truncado.
El contenido anterior permanece disponible en Tlamatini; nunca se incluye el
historial de otra cuenta.

Cuando una operación necesite aprobación, revisa los detalles y elige **Proceed**
para continuar o **Deny** para rechazarla. La decisión pertenece únicamente a esa
conversación y a esa solicitud pendiente. Un mensaje posterior de progreso no
oculta la aprobación. Si sus detalles están incompletos o exceden el límite, la
ejecución se rechaza; no se autoriza silenciosamente un comando. Perder el canal
de aprobación o la autorización cierra el consentimiento y solicita la cancelación.

Cancelar solicita detener la operación existente. La confirmación de que el
trabajo terminó es un resultado separado; cancelar no deshace acciones completadas.
El adaptador conserva la propiedad hasta que termina el trabajo activo, de modo
que otra solicitud no pueda apropiarse de una conversación que sigue ejecutándose.

## Iniciar Tlamatini desde el cliente RC

Otorga **Start Tlamatini** al crear la invitación del dispositivo. La bandeja XT
normal debe estar abierta en la sesión iniciada del usuario de Windows delegado,
sin elevación administrativa. Bloquear el escritorio o desconectar la sesión no
deshabilita esta función del producto. XT no desbloquea Windows ni selecciona otro
usuario de Windows.

XT localiza el ejecutable instalado de la edición seleccionada y verifica su
identidad. En esta edición es `Tlamatini-Spanish.exe`; la edición en inglés utiliza
`Tlamatini.exe`. El cliente no puede proporcionar un comando, una ruta, un PID ni
un nombre de servicio. Una instancia de desarrollo ya abierta puede proporcionar
su adaptador de cuenta, pero el intermediario de inicio no busca ni inicia copias
del código fuente.

El inicio del proceso y su disponibilidad son observaciones diferentes. **Starting**
significa que el proceso existe y su adaptador de cuenta todavía carga o no está
disponible. El estado listo requiere una señal de actividad vigente del adaptador.
La aplicación conserva su consola principal normal; los ayudantes internos de RC
no abren otra. El almacenamiento temporal del inicio debe estar en una ubicación
escribible de la aplicación fuera de los perfiles de usuario de Windows.

## Deshabilitar el acceso o detener el servidor

En la página de cuenta, pulsa **Deshabilitar acceso remoto**. Primero se guarda la
denegación local; después el adaptador solicita cancelar el trabajo remoto de esa
cuenta y revoca su vínculo con el servicio, sus dispositivos y sus invitaciones
pendientes. Si Remote-Controller no está disponible, la página indica que falta
completar la revocación del servicio. Se reintentará cuando vuelva; también está
disponible **Reintentar revocación del servicio**.

Eliminar la cuenta local también guarda una intención de revocación duradera.
Sobrevive a la indisponibilidad del servicio RC y a un reinicio de la aplicación,
por lo que borrar la cuenta no pierde la obligación de revocar sus dispositivos
cuando vuelva el servicio.

Al habilitar de nuevo la cuenta se conserva su identidad inmutable, pero sus
dispositivos e invitaciones anteriores no recuperan validez. Inscribe y aprueba
el dispositivo otra vez.

Usa la pestaña **Runtime** de Remote-Controller en XT para detener o reiniciar el
servidor. Detener RC desconecta sus clientes y suspende su planificador; Tlamatini
permanece abierto y Torrenter sigue siendo independiente. Cerrar la pestaña de
cuenta o salir de XT no detiene el servicio RC. Un servidor detenido no puede ser
reiniciado por su propio cliente desconectado.

## Implementación y verificación

`RemoteControllerProfile`, `RemoteControllerRevocation` y la migración
`0224_remote_controller` guardan el consentimiento explícito de la cuenta, UUID
inmutables separados para cuenta y adaptador, y registros duraderos de su eliminación.
La integración no reutiliza identidades de Torrenter, no agrega un
agente de workflow ni modifica la mecánica de respaldo y restauración de la base.

Esta migración depende de `0227_create_superuser_console_handoff` en español.
La edición inglesa utiliza `0223_create_superuser_console_handoff`. Conserva el
predecesor real de cada edición: la paridad de comportamiento no exige números
de migración idénticos. [Corrección y verificación de la compilación](changes/2026-11-13-build-migration-preflight.md).

La página local en `/agent/remote-controller/` utiliza `remote_controller_views.py`,
`templates/agent/remote_controller.html` y `static/agent/css/remote_controller.css`.
Exige cuenta autenticada, conexión local, formularios del mismo origen y protección
CSRF. `remote_controller_bridge.py` utiliza exclusivamente el controlador nativo
instalado en su ruta fija y mensajes tipados con límites. El trabajador de cuenta
mantiene la propiedad exclusiva de su adaptador y solicita cancelar el trabajo
remoto cuando se pierde la autorización o el transporte.

El transporte nativo y la consulta de cuentas tienen cuatro espacios concurrentes.
El trabajo activo vigila su autorización con un plazo de 20 segundos, para que una
llamada nativa bloqueada no conserve indefinidamente el consentimiento. El servicio
cambia un recibo en ejecución a `outcome_unknown` tras 20 segundos sin actividad
de su aplicación, o 45 segundos sin actividad del intermediario de inicio. Ese
estado no demuestra que el trabajo haya terminado. Impide repetirlo automáticamente;
el adaptador propietario puede conciliar después el resultado real.

`remote_controller_runtime.py` reutiliza `AgentConsumer`, con el control de
propiedad en `remote_controller_guard.py`. El chat remoto transmite los seis modos
seleccionados: **Multiturn, Exec-Report, ACPX, Self-Modify, Ask Execs y Step by step**.
Su disponibilidad procede de la edición activa; se conservan los límites del
modelo y el consentimiento. El recibo registra los valores efectivos.
El canal propietario conserva la respuesta original antes del formato enriquecido,
manteniendo las etiquetas literales como texto inerte junto con los informes y
avisos de denegación. El mensaje enriquecido normal no cambia.
Solo se reenvía la salida del consumidor propio. El empaquetado debe incluir estos
módulos, `services/response_parser.py`, la migración, la página, los estilos y esta guía.

El espacio completo adapta Chat, Canvas, Downloads, Settings y More al uso táctil,
incluyendo Torrenter Sources y Torrenter Workspace. Solo se excluyen Agentic
Control Panel, Prompt Flow Panel y Admin Panel. Los controles de voz y micrófono
operan en la computadora anfitriona; no capturan el micrófono del teléfono.

El espacio renueva la sesión aprobada al abrirse, antes de caducar y al volver
a él. Las solicitudes simultáneas comparten una renovación; nunca se repite
automáticamente una acción interrumpida. Revocar el dispositivo sigue bloqueando
el acceso.

Con el permiso independiente **Stop Tlamatini**, el cliente solicita el cierre
normal de la edición instalada. XT verifica la identidad del proceso y señala
su consola dedicada, sin aceptar un PID proporcionado por el navegador. Un
reinicio inmediato verifica un nuevo proceso vivo y no acepta la observación
de actividad que dejó el proceso anterior.

Las ejecuciones registradas del 13 de noviembre aprobaron **159/159 pruebas
unitarias aisladas por edición**, antes de los últimos ajustes de revocación
duradera e historial. El servicio aprobó 195 pruebas del núcleo, 54 de HTTP/canal
nativo y una campaña de 14 verificaciones aisladas bajo SCM. Las pruebas y cambios
agregados después esperan su propia ejecución completa; estas cifras no certifican
las modificaciones más recientes. Las pruebas reales con navegador visible y la
aceptación integral instalada siguen siendo etapas separadas. El registro autoritativo es
`C:\Development\XAIHT\repo\Tlachihuani\docs\verification\2026-11-13-remote-controller.md`.

La validación posterior de conservación de respuestas aprobó **242/242 pruebas
de código por edición**. El par compilado `20261114-0255` se instaló con todos los
hashes verificados y sin cambiar los bytes de base de datos o configuración.
Los resultados instalados de prompts, interfaz móvil y ciclo de vida, incluidos
los fallos de formato de respuesta, se registran en
`C:\Development\XAIHT\repo\Tlachihuani\docs\verification\2026-11-13-installed-rc-acceptance.md`.

La aceptación local instalada final completó **50 prompts en inglés y 50 en
español**, con **99/100 verificaciones de respuesta exacta**, **170/170 pruebas
móviles** e inicio, reinicio y cierre remotos independientes en ambas ediciones.
Se conserva un fallo de formato de respuesta en español. La compilación del
controlador `20261114-033543-1abcb41e` se instaló después de desinstalar la anterior,
con 1,475 archivos coincidentes. Español usa `spanish-20261114-0457`, que corrige
el rechazo de instrucciones de una sola vuelta como «Devuelve»; sus **247/247
pruebas de código** aprobaron. La prueba instalada ES016 devolvió `verde` con
los seis modos desactivados. El registro de aceptación anterior contiene la
procedencia exacta y los límites de la validación; el trabajo de red sigue pendiente.
