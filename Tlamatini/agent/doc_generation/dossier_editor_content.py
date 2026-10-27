# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Canvas, Interactor and configuration chapters shared by the PDF and deck."""


def editor_sections(section):
    return [
        section("interaction_settings", "CONFIGURACIÓN · v1.91.0", "Elige cómo escribe y cómo enseña",
                "Config → Live Editor & Terminater abre un diálogo compartido en el chat y en los paneles de control.",
                body=[
                    "Live Editor controla de 40 a 160 WPM, una pausa de 0 a 3 segundos después de cada segmento, el detalle de la enseñanza, "
                    "las sugerencias de campos, texto fantasma contra opciones, y seguir el cursor que escribe. Desplazarte a "
                    "mano suspende el seguimiento en ese segmento. La fuente, los números de línea y el ajuste de líneas afectan "
                    "al editor real. El detalle de la enseñanza le da instrucciones al modelo; la redacción exacta todavía varía.",
                    "Los presets Estándar y Aprendizaje guiado llenan un borrador. Vista previa escribe y dice una muestra inofensiva "
                    "sin editar archivos ni ejecutar comandos. Guardar aplica el comportamiento a la siguiente acción. "
                    "Cancelar, Escape y Cerrar descartan el borrador. Detener, silenciar y el acceso al editor de la pestaña actual son inmediatos.",
                ], points=[
                    ("Ritmo", "Velocidades separadas o un ajuste ligado de 40 a 160 WPM; sin escribir de golpe."),
                    ("Enseñanza", "Guía breve, equilibrada o detallada, con sugerencias locales opcionales."),
                    ("Apariencia", "La presentación del editor y de la terminal se guarda por cuenta/browser."),
                    ("Cuenta", "El comportamiento persiste en el servidor; los guardados simultáneos detectan conflictos de revisión."),
                ]),
        section("terminal_settings", "CONFIGURACIÓN DE TERMINATER", "Un comando sigue los controles de quien aprende",
                "Un solo TerminalHub resuelve las preferencias de la cuenta en el chat, el ACP, el Prompt Flow y las acciones del browser.",
                body=[
                    "Elige de 20 a 160 WPM, un shell predeterminado disponible, el asesor para terminales nuevas, una ventana de espera "
                    "del comando, un umbral sin output y una espera para entregar el teclado al usuario. Los valores predeterminados de shell y asesor afectan "
                    "a las terminales nuevas. Agotar una espera no mata el proceso. Los cambios de distribución, fuente y cursor "
                    "se aplican a las vistas existentes; los prompts redimensionados conservan una lectura honesta basada en la pantalla.",
                    "Yo siempre presiono Enter impide el envío automático, incluidos alias, texto codificado y "
                    "caracteres de control; el teclado del usuario sigue funcionando. Los flows nuevos pueden usar los valores predeterminados de la cuenta. "
                    "Los archivos de flow más viejos conservan sus valores explícitos. El Enter manual y la narración siguen siendo elecciones de la cuenta, "
                    "y el chat tecleado respeta un shell que la tarea pidió explícitamente.",
                ], points=[
                    ("Escribir", "Una tecla a la vez, de 20 a 160 WPM; sin pegar ni escribir de golpe."),
                    ("Enviar", "Ejecución controlada por la tarea o Enter sólo del usuario, que el hub hace cumplir."),
                    ("Esperar", "Las ventanas de comando, sin output y de entrega del teclado tienen significados distintos."),
                    ("Heredar", "use_my_defaults aplica las preferencias de la cuenta sin reescribir flows más viejos."),
                ]),
        section("interaction_voice", "VOZ PARA COMANDOS Y LECCIONES", "Escucha el paso antes de la primera tecla",
                "La narración usa la voz existente del browser y una cola de voz compartida y cancelable.",
                body=[
                    "Activa la narración por separado para los comandos de Terminater y para los segmentos de Live Editor. Elige "
                    "una explicación, el comando/código literal o ambos, dichos antes, durante o después de escribir. Cuando "
                    "está activado esperar antes de escribir, se necesita un recibo real de que la voz terminó o un salto "
                    "explícito. Una voz no disponible ofrece Continuar sin voz o Detener.",
                    "Una sola pestaña enfocada de la cuenta dice cada evento de la terminal. Los recibos pertenecen a esa "
                    "conexión exacta; desconectar, Detener y el plazo acotado pueden cancelar antes de cualquier tecla. Una reconexión "
                    "nunca repite un comando. El texto marcado como secreto y los valores que entrega el usuario se excluyen. Los avisos "
                    "de resultado describen el status de la acción del comando sin leer en voz alta el output de la terminal.",
                ], points=[
                    ("Voz compartida", "Reutiliza la elección de voz, la velocidad, el volumen y el tono de Config → Voz."),
                    ("Prioridad", "El silencio global y la escucha del micrófono tienen prioridad sobre la narración."),
                    ("Momento", "Antes/durante/después; opcionalmente, terminar antes de escribir."),
                    ("Control", "Escape detiene la voz; Ctrl+Shift+M activa o desactiva el silencio global."),
                ]),
        section("canvas_edit", "EDITOR DEL CANVAS · v1.89.0", "Edita el documento del que estás hablando",
                "Un editor CodeMirror 6 local mantiene editables el texto, el código, el JSON y el Source de Markdown en el canvas del chat.",
                body=[
                    "Abre o suelta un archivo, haz un cambio y usa la barra del nombre del archivo: Guardar, Guardar como, Deshacer, Rehacer, "
                    "Buscar/reemplazar y Ajustar líneas. Copiar y Usar como contexto toman el source editado. Ctrl/Cmd+S guarda; "
                    "Ctrl/Cmd+Shift+S elige un destino. Tab normalmente navega; Ctrl+[ y Ctrl+] cambian la sangría.",
                    "La Vista previa de Markdown se sanitiza con el renderizador existente de Marked/DOMPurify. Source y Vista previa "
                    "comparten un buffer y un historial de deshacer. HTML y SVG se quedan como texto, nunca como una página web activa. Los PDFs "
                    "siguen siendo visores de sólo lectura y exportan sus bytes originales; los flows y las imágenes conservan sus propios caminos.",
                    "La marca de cambios sin guardar sobrevive a los guardados con error o cancelados. Abrir, Limpiar y Actualizar preguntan antes de "
                    "descartar ediciones. El texto sin guardar vive en memoria, así que guarda antes de cerrar. El tamaño automático "
                    "reserva 320 píxeles de CSS para el canvas y acomoda los controles; las divisiones manuales siguen siendo elección del usuario.",
                ], points=[
                    ("Un solo documento", "El código, la configuración y el texto plano comparten la misma autoridad de edición."),
                    ("Markdown", "El source editable y la vista previa sanitizada conservan el historial de deshacer."),
                    ("Controles", "Guardar, Guardar como, Deshacer/Rehacer, Buscar/reemplazar y Ajustar líneas."),
                    ("Distribución", "Un ancho reservado para el canvas y un editor que llena su altura disponible."),
                ]),
        section("canvas_save", "GUARDADO NATIVO", "Guarda en la carpeta del proyecto que elijas",
                "El selector nativo local de Windows hace que Descargas sea opcional.",
                body=[
                    "Guardar usa un handle de escritura que concede el browser o un destino nativo ya autorizado. "
                    "Sin uno, pregunta. Guardar como y el Guardar de la barra de navegación abren un diálogo nativo Guardar como de Windows en "
                    "una conexión local; los Guardar siguientes de la barra de herramientas escriben ahí y Actualizar lo lee. Las exportaciones de PDF "
                    "siguen siendo copias. Los browsers remotos necesitan su propio selector soportado de File System Access.",
                    "Una revisión completa de la revisión rechaza los cambios externos. Las escrituras se preparan en el volumen de destino, "
                    "se vacían y se vuelven a revisar antes de reemplazar. ReplaceFileW conserva la seguridad existente de Windows, los streams "
                    "con nombre y la hora de creación; una falla parcial conserva un original recuperable. El camino protegido "
                    "de backup/restauración de la base de datos no cambia.",
                    "Los archivos sin editar conservan los bytes exactos. Los archivos editados conservan la codificación/BOM y los saltos de línea existentes; "
                    "las líneas nuevas usan el primer terminador original. UTF-8 y UTF-16 marcado con BOM se decodifican estrictamente. "
                    "Los datos mal formados/binarios se rechazan. La edición de texto y el guardado nativo se limitan a 64 MiB.",
                ], points=[
                    ("Elegir", "Guardar como nativo en cualquier carpeta local con permiso de escritura."),
                    ("Autorizar", "Capacidad ligada a la cuenta/sesión; 12 horas de inactividad, se pierde al reiniciar."),
                    ("Comparar", "Los cambios externos en el disco rechazan la sobrescritura; Guardar como conserva una copia aparte."),
                    ("Conservar", "Codificación, BOM, saltos de línea y metadatos existentes de Windows."),
                ]),
        section("interactor_tutor", "INTERACTOR · v1.90.0", "Enseña dentro del documento vivo sin guardar",
                "Interactor es un módulo y un tool integrado, no un agent de workflow ni una terminal.",
                body=[
                    "Activa Multi-Turn, Interactor en Configurar MCPs/Tools y el Live editor sobre el canvas. "
                    "Pide: Ayúdame a crear un Dockerfile para una aplicación de servlets de Java usando tu editor de texto; "
                    "enséñame un paso a la vez. Los alias del editor en inglés/español se enseñan en prompt.pmt.",
                    "Primero lee el buffer actual exacto, la selección, el ID del documento y la revisión. Si no se pide un "
                    "path, new crea un archivo vacío en Temp/interactor/<account>/<random>/ con el nombre de archivo "
                    "pedido. Los archivos existentes nunca se sobrescriben. Tlamatini escribe un segmento corto conocido, y luego "
                    "guide le entrega el siguiente campo a quien aprende e impide más cambios en ese turno.",
                    "Continuar envía una nueva solicitud normal al chat y vuelve a leer antes de revisar la respuesta de quien "
                    "aprende. Otra pista y Explicar selección también usan el chat normal sin reemplazar un borrador "
                    "existente. Escribir no guarda ni ejecuta código. El snapshot normal de Usar como contexto es aparte "
                    "de la lectura fresca que hace Interactor del texto sin guardar.",
                ], points=[
                    ("Leer", "Texto y selección exactos sin guardar, nunca un sustituto viejo del disco."),
                    ("Escribir", "Un pequeño segmento visible de enseñanza; una edición que se puede deshacer."),
                    ("Entregar", "Explica el siguiente campo de quien aprende, y luego detiene los cambios del tool."),
                    ("Revisar", "Continuar empieza una lectura fresca en un nuevo turno del chat."),
                ]),
        section("interactor_latency", "COMPLETADO DEL TUTOR", "Ayuda inmediata mientras quien aprende escribe",
                "El modelo planea el siguiente campo una vez; la coincidencia local evita una solicitud al modelo en cada tecla.",
                body=[
                    "El texto fantasma aparece sólo con un prefijo que coincide entre opciones acotadas preparadas para el campo "
                    "actual. Tab acepta, Ctrl+Derecha acepta una palabra y Escape descarta. Las sugerencias son opcionales; "
                    "quien aprende puede escribir un valor alternativo. Es apoyo de enseñanza con contexto, no una afirmación "
                    "de autocompletado predictivo sin límites ni de la latencia de benchmarks de proveedores.",
                    "El input del usuario, la selección, Detener, Escape, la cancelación del chat y la desconexión interrumpen la escritura de la IA. "
                    "El prefijo escrito sigue siendo editable. Una pestaña oculta o tapada temporalmente pausa la misma acción "
                    "hasta dos minutos extra y continúa exactamente en el siguiente carácter cuando es visible. Agotar el tiempo "
                    "nunca repite una edición parcial. Cambiar Markdown a Vista previa u ocultar el canvas regresa el control.",
                    "La enseñanza en vivo acepta a lo más 262,144 unidades UTF-16 y revisa el documento/la revisión antes de "
                    "los cambios. Un presupuesto configurado más pequeño de resultado del tool/contexto puede rechazar el recibo. El contenido "
                    "demasiado grande se rechaza explícitamente, nunca se recorta para dar un contexto engañoso.",
                ], points=[
                    ("Coincidencia local", "Opciones de campo preparadas; sin llamada al modelo por tecla."),
                    ("Opcional", "Acepta una sugerencia, toma una palabra, descártala o escribe tu propio valor."),
                    ("Prioridad del usuario", "Las interrupciones conservan el prefijo escrito e invalidan el trabajo viejo."),
                    ("Latencia honesta", "Las preguntas nuevas todavía esperan el procesamiento del chat/modelo."),
                ]),
    ]


def bridge_section(section):
    return section("interactor_architecture", "PUENTE DEL LIVE EDITOR", "Una pestaña autenticada, un buffer exacto",
                   "El editor del browser y el ciclo síncrono de tools comparten un puente ligado a la cuenta/sesión.",
                   points=[
                       ("Browser", "CodeMirror es la autoridad; bridge.js envía recibos/acceso/detener, no comandos con paths del host."),
                       ("Transporte", "ws/interactor/ autentica la sesión y el Origin/Host exactos; el servidor asigna la identidad de la pestaña."),
                       ("Contexto del tool", "ContextVar lleva la identidad de pestaña/cuenta/sesión a los workers; read obtiene el buffer vivo."),
                       ("Hub", "Colas acotadas, IDs de comandos, plazos, revisiones de la revisión y verificación del buffer completo."),
                       ("Persistencia", "Ask Execs controla new/save; el acceso al host por loopback usa las protecciones existentes de paths y de capacidades de archivo."),
                       ("Transporte al release", "Migración 0218, tool_gate_table, reglas del prompt, módulos congelados e inventarios sin conexión de source/estáticos."),
                   ], deck="list")


def wizard_section(section):
    return section("wizard_intent", "PROTECCIONES DE INTENCIÓN · v1.90.0", "Un aviso de contraseña no debe desviar al asistente",
                   "El asistente de cuentas lanza createsuperuser por medio de Executer y espera el input en su consola.",
                   body=[
                       "El log instalado mostró dos falsos positivos independientes. 'I will type it' se refería a una "
                       "contraseña pero reservaba todos los comandos para el usuario. Una frase de término más el campo opcional "
                       "de email creaban por error una deuda de notificación. Estas protecciones del runtime anularon una selección "
                       "inicialmente correcta de Executer y desviaron al asistente.",
                       "La propiedad de escribir/teclear ahora exige un objeto de comando; el input ambiguo es neutral. Un "
                       "lanzamiento explícito, por la asistente, de un programa con nombre levanta una lección anterior. Los tutoriales genuinos "
                       "donde el usuario ejecuta siguen rechazando los ejecutores de comandos y mantienen desactivado el Enter de Terminater.",
                       "Una notificación de término exige una instrucción positiva de envío ligada al término "
                       "en la misma oración. Los campos de email, las explicaciones normales del chat, los ejemplos citados, las negaciones "
                       "y la respuesta DONE del usuario no autorizan el envío. Las contraseñas se quedan fuera del chat. El asistente "
                       "del catálogo crea un superusuario administrativo, no una cuenta común restringida.",
                   ], points=[
                       ("Lanzar", "Executer abre el comando interactivo de source o congelado en una consola visible."),
                       ("Input", "El nombre de usuario, el email opcional y la contraseña pertenecen a la interacción del usuario con la consola."),
                       ("Esperar", "DONE / ERROR / NOWINDOW manejan el siguiente paso; sin afirmar éxito automáticamente."),
                       ("Notificar", "Sólo una solicitud explícita de envío crea una deuda de notificación de término."),
                   ])


def release_sections(section, facts):
    return [
        section("release1911", "VERSIÓN ACTUAL · v1.91.1", "Arreglos del Prompt Flow y nombres cortos de tools",
                "Tag 9915938a, con fecha del 27 de octubre de 2026; publicado como el release Latest.",
                body=[
                    "Un parche sobre v1.91.0. Cada chain carga el historial de su propia conversación, así que una ejecución de Prompt "
                    "Flow conserva su propia memoria y nunca se contesta con otra conversación.",
                    "Una Decisión equals acepta una respuesta que empieza con la palabra esperada, y el Prompt "
                    "anterior pide sólo esa palabra en la primera línea. El uso de una ejecución de flow se registra para "
                    "la cuenta dueña de ella.",
                    "Telegrammer envía como el bot cuando la solicitud dice 'using the bot'. Un agent wrapped "
                    "llamado por su nombre corto se resuelve y se registra como [TOOL-ALIAS]. No se agregó ningún agent, tool, skill "
                    "ni migración.",
                ], points=[
                    ("Historial", "Cada ejecución y cada usuario leen sólo su propia conversación."),
                    ("Decisiones", "'## YES - ...' es igual a YES; 'Yesterday' no."),
                    ("Enrutamiento", "'Using the bot' envía como el bot; los nombres cortos de tools siguen funcionando."),
                    ("Inventario", f"{facts['agents']} agents; {facts['tools']} tools; {facts['migrations']} migraciones; "
                     f"{facts['js']} módulos JS; {facts['css']} hojas de estilo."),
                ]),
        section("release191", "HEREDADO DE v1.91.0", "Configuraciones reales para el comportamiento del editor y de la terminal",
                "Tag a771d27c, con fecha del 23 de octubre de 2026, y publicado en GitHub ese día.",
                body=[
                    "Las pestañas Live Editor, Terminater y Voz comparten un esquema, almacenamiento autenticado por cuenta "
                    "y revisiones optimistas. La migración 0220 agrega InteractionSettings. El comportamiento de la cuenta llega "
                    "al editor real y al único TerminalHub; la apariencia del browser/cuenta se queda local.",
                    "Evidencia del source del 23 de octubre: pasaron 17 revisiones visibles en el browser, incluida voz genuina del sistema operativo "
                    "terminando antes de la primera tecla de la terminal. La ejecución de regresión de la implementación pasó 929 de "
                    "931 pruebas; fallaron dos aserciones existentes de la documentación del README. Esta revisión de la documentación "
                    "restaura esas secciones; sus 94 pruebas enfocadas pasaron, incluidas las dos aserciones del README.",
                    "v1.91.0 se publicó en GitHub el 23 de octubre de 2026. Estos documentos regenerados no "
                    "afirman un nuevo build del ejecutable ni una aceptación instalada. El tag existente se conserva.",
                ], points=[
                    ("Diálogo", "Ritmo, enseñanza, comportamiento de la terminal, narración, apariencia y vistas previas del borrador."),
                    ("Runtime", "Snapshots reales de la configuración, revisiones de la revisión y recibos de narración cancelables."),
                    ("Compatibilidad", "Los flows heredados con valores explícitos los conservan; los flows nuevos pueden heredar los valores predeterminados."),
                    ("Inventario", f"{facts['agents']} agents; {facts['tools']} tools; {facts['migrations']} migraciones; "
                     f"{facts['js']} módulos JS; {facts['css']} hojas de estilo."),
                ]),
        section("release190", "HEREDADO DE v1.90.0", "Editar, enseñar y conservar el control de quien aprende",
                "v1.89.0 introdujo la edición y el guardado nativo; v1.90.0 lleva Interactor y las correcciones de intención.",
                body=[
                    "El tag anotado v1.90.0 apunta a ebc5c3b4; esta actualización de la documentación empezó en d274f89c, "
                    "el commit siguiente, también presente en origin/main. Un tag y las pruebas del source no establecen que "
                    "un ejecutable instalado por separado se haya recompilado o aceptado.",
                    "Interactor agrega un tool de módulo, no una plantilla de agent de workflow. La migración 0218 siembra su "
                    "fila de Tool y un ejemplo del catálogo. La vinculación completa de los tools habilitados, la selección de Compact mode y las etiquetas "
                    "de costo comparten tool_gate_table. El bundle del editor sin conexión incluye la extensión de enseñanza.",
                ], points=[
                    ("Edición", "Guardar como nativo, source exacto, historial de deshacer y persistencia que detecta conflictos."),
                    ("Enseñanza", "Lecturas frescas sin guardar, segmentos cortos de escritura, campos para quien aprende y sugerencias locales."),
                    ("Recuperación", "Pausas acotadas por visibilidad de la pestaña y una distribución usable con el canvas angosto."),
                    ("Inventario", f"{facts['agents']} agents; {facts['wrapped']} wrapped; {facts['tools']} tools integrados; "
                     f"{facts['migrations']} migraciones. Los conteos describen el source inspeccionado."),
                ]),
        section("editor_evidence", "VERIFICACIÓN FECHADA", "Mantén separadas las evidencias del source, del modelo y del congelado",
                "Son ejecuciones registradas del 21 al 22 de octubre, no pruebas que la generación de la documentación vuelve a correr en silencio.",
                table={"columns": ["Alcance", "Resultado registrado y límite"], "widths": [0.30, 0.70], "rows": [
                    ["Edición en el canvas / 21 oct", "29 puntos de revisión visibles distintos; guardado nativo, tipos de archivo, codificación, conflictos y copias de PDF."],
                    ["Interactor / 21 oct", "35/35 revisiones, incluidos tres casos configurados con un modelo real; ejecuciones posteriores de la UI agregan cobertura de interrupción y recuperación."],
                    ["Modos DEV finales / 21 oct", "19/19 revisiones visibles; 136 pasaron + 2 saltadas entre 138 pruebas enfocadas de Django."],
                    ["v1.89.0 congelado más viejo", "Ejecución real del cargador congelado: 16 pasaron, 2 fallaron después de la revisión visual (ausencia de pestaña y distribución angosta)."],
                    ["Protecciones del asistente / 22 oct", "179 pruebas pasaron; la repetición exacta de la solicitud instalada pasó. Efectos de tools controlados; sin cuenta ni notificación reales."],
                    ["Paquete nuevo de v1.90.0", "Esta revisión de la documentación no afirma ninguna nueva aceptación del paquete instalado."],
                ]}, deck="table"),
    ]
