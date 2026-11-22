# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Canvas, Interactor and configuration chapters shared by the PDF and deck."""


def editor_sections(section):
    return [
        *canvas_document_sections(section),
        section("torrent_workspace", "TORRENTER", "Del magnet a los archivos verificados",
                "El chat, el panel agéntico y XT comparten la cola de Jobs de cada cuenta.",
                body=["Inspecciona los metadatos y selecciona los archivos por ID. El recibo permite volver al trabajo. En un flujo, activa la espera de descarga si los nodos siguientes necesitan los archivos.",
                      "Un quinto magnet puede esperar un espacio de metadatos. Conserva el ID de inspección. El manifiesto verificado identifica la copia en Descargas o en la carpeta alternativa de la edición."], deck_points=[
                    ('Inspeccionar', 'Conserva el ID de inspección mientras espera.'),
                    ('Elegir', 'Selecciona los archivos por sus IDs.'),
                    ('Consultar', 'Reconecta con el ID del trabajo de Jobs.'),
                    ('Verificar', 'Lee la ruta de entrega y el SHA-256 del manifiesto.'),
                ]),
        section("interaction_settings", "CONFIGURACIÓN · v1.91.0", "Elige cómo escribe y cómo enseña",
                "Config → Live Editor & Terminater abre un diálogo compartido en el chat y en los paneles de control.",
                body=[
                    "Live Editor controla de 40 a 250 WPM, una pausa de 0 a 3 segundos después de cada segmento, el detalle de la enseñanza, "
                    "las sugerencias de campos, texto fantasma contra opciones, y seguir el cursor que escribe. Desplazarte a "
                    "mano suspende el seguimiento en ese segmento. La fuente, los números de línea y el ajuste de líneas afectan "
                    "al editor real. El detalle de la enseñanza le da instrucciones al modelo; la redacción exacta todavía varía.",
                    "Los presets Estándar y Aprendizaje guiado llenan un borrador. Vista previa escribe y dice una muestra inofensiva "
                    "sin editar archivos ni ejecutar comandos. Guardar aplica el comportamiento a la siguiente acción. "
                    "Cancelar, Escape y Cerrar descartan el borrador. Detener, silenciar y el acceso al editor de la pestaña actual son inmediatos.",
                ], points=[
                    ("Ritmo", "Velocidades separadas o un ajuste ligado de 40 a 250 WPM; sin escribir de golpe."),
                    ("Enseñanza", "Guía breve, equilibrada o detallada, con sugerencias locales opcionales."),
                    ("Apariencia", "La presentación del editor y de la terminal se guarda por cuenta/browser."),
                    ("Cuenta", "El comportamiento persiste en el servidor; los guardados simultáneos detectan conflictos de revisión."),
                ]),
        section("terminal_settings", "CONFIGURACIÓN DE TERMINATER", "Un comando sigue los controles de quien aprende",
                "Un solo TerminalHub resuelve las preferencias de la cuenta en el chat, el ACP, el Prompt Flow y las acciones del browser.",
                body=[
                    "Elige de 20 a 250 WPM, un shell predeterminado disponible, el asesor para terminales nuevas, una ventana de espera "
                    "del comando, un umbral sin output y una espera para entregar el teclado al usuario. Los valores predeterminados de shell y asesor afectan "
                    "a las terminales nuevas. Agotar una espera no mata el proceso. Los cambios de distribución, fuente y cursor "
                    "se aplican a las vistas existentes; los prompts redimensionados conservan una lectura honesta basada en la pantalla.",
                    "Yo siempre presiono Enter impide el envío automático, incluidos alias, texto codificado y "
                    "caracteres de control; el teclado del usuario sigue funcionando. Los flows nuevos pueden usar los valores predeterminados de la cuenta. "
                    "Los archivos de flow más viejos conservan sus valores explícitos. El Enter manual y la narración siguen siendo elecciones de la cuenta, "
                    "y el chat tecleado respeta un shell que la tarea pidió explícitamente.",
                ], points=[
                    ("Escribir", "Una tecla a la vez, de 20 a 250 WPM; sin pegar ni escribir de golpe."),
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
        section("canvas_edit", "EDITOR DEL CANVAS · v1.97.0", "Edita el documento del que estás hablando",
                "Un editor CodeMirror 6 local mantiene editables el texto, el código, el JSON y el Source de Markdown en el canvas del chat.",
                body=[
                    "Abre o suelta un archivo, haz un cambio y usa la barra del nombre del archivo: Guardar, Guardar como, Deshacer, Rehacer, "
                    "Buscar/reemplazar y Ajustar líneas. Copiar y Usar como contexto toman el source editado. Ctrl/Cmd+S guarda; "
                    "Ctrl/Cmd+Shift+S elige un destino. Tab normalmente navega; Ctrl+[ y Ctrl+] cambian la sangría.",
                    "La Vista previa de Markdown se sanitiza con el renderizador existente de Marked/DOMPurify. Source y Vista previa "
                    "comparten un buffer y un historial de deshacer. HTML y SVG se quedan como texto, nunca como una página web activa. Los PDFs "
                    "siguen siendo visores de sólo lectura y exportan sus bytes originales; los flows y las imágenes conservan sus propios caminos.",
                    "Abrir y soltar archivos agrega documentos sin reemplazar los demás. La marca de cambios sin guardar "
                    "sobrevive a errores y cancelaciones; cerrar o actualizar documentos editados pide confirmación. "
                    "El texto sin guardar vive en memoria, así que guarda antes de cerrar. El tamaño automático "
                    "reserva 320 píxeles de CSS para el canvas y acomoda los controles; las divisiones manuales siguen siendo elección del usuario.",
                ], points=[
                    ("Documentos independientes", "Cada pestaña conserva su texto, historial, revisión y destino de guardado."),
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
                    "Continuar y Otra pista envían solicitudes normales de tutoría al chat. Explicar selección usa "
                    "una solicitud separada de sólo lectura: captura los intervalos sin guardar sin depender de "
                    "las casillas ni del Editor en vivo, y conserva el borrador. Escribir no guarda ni ejecuta "
                    "código. Usar como contexto conserva su instantánea separada de las lecturas de Interactor.",
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
                    "El prefijo escrito sigue siendo editable. Una pestaña del navegador oculta o tapada temporalmente pausa la misma acción "
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


def canvas_document_sections(section):
    return [
        section("canvas_documents", "CANVAS MULTIDOCUMENTO · v1.97.0", "Mantén toda la tarea junto a la conversación",
                "Abre hasta 32 documentos en un Canvas; cambiar de pestaña no cambia el contexto del chat.",
                body=[
                    "Abrir, soltar archivos y cargar texto generado agrega pestañas. Cada documento conserva "
                    "su texto, historial de deshacer/rehacer, selección, desplazamiento, codificación, revisión "
                    "y destino autorizado. Dos archivos con el mismo nombre siguen siendo documentos distintos. "
                    "Guardar afecta al archivo activo; las demás pestañas modificadas conservan su asterisco.",
                    "Markdown conserva su vista de código fuente o vista previa. Cada PDF mantiene su visor, "
                    "página, zoom, rotación y desplazamiento. Los PDF son de sólo lectura y Guardar como exporta "
                    "los bytes originales. Abrir un documento no lo guarda ni lo incluye en la conversación.",
                    "Una respuesta de guardado tardía no puede borrar la marca de ediciones posteriores. Un "
                    "guardado pendiente bloquea el cambio de documento; un error o cancelación conserva los "
                    "cambios. El texto generado empieza sin guardar. Las pestañas viven en memoria: no son "
                    "recuperación ante fallos ni restauración de sesiones del navegador.",
                ], points=[
                    ("32 pestañas", "Texto, código y PDF juntos, sin reemplazar los documentos abiertos."),
                    ("Por documento", "Historial, selección, vista y destino de guardado independientes."),
                    ("Guardar", "Escribe el archivo activo; conserva las marcas de los demás."),
                    ("PDF", "Retiene la vista y exporta los bytes originales sin cambios."),
                ]),
        section("canvas_context_set", "CONTEXTO EXPLÍCITO", "Elige las fuentes que guían la respuesta",
                "Usar como contexto selecciona una instantánea confirmada, independiente del documento activo.",
                body=[
                    "Abre A, B y C. Selecciona Usar como contexto en A y después en B: el conjunto contiene "
                    "A y B; abrir o activar C no lo agrega. Las insignias de las pestañas y la franja de "
                    "contexto identifican las fuentes seleccionadas. Cerrar una pestaña del editor conserva "
                    "su instantánea seleccionada hasta que la retires explícitamente.",
                    "Editar una fuente, renombrar texto mediante Guardar como o actualizar un PDF marca la instantánea "
                    "como anterior. Actualizar contexto la reemplaza explícitamente. Puedes retirar una fuente "
                    "sin descartar las demás. La preparación de PDF pregunta por las imágenes, desactivadas "
                    "de forma predeterminada, y usa un token ligado a la cuenta; leer un PDF no prepara contexto.",
                    "El servidor acepta hasta 32 instantáneas de forma atómica, con un presupuesto compartido "
                    "de 32 MiB en UTF-8 que incluye las etiquetas. Un rechazo conserva el último conjunto "
                    "confirmado. Una desconexión elimina "
                    "las marcas de confirmación e indica incertidumbre, pero conserva los documentos; una "
                    "respuesta tardía no confirma otra selección. Revisa el contexto restaurado antes de usarlo.",
                ], points=[
                    ("Elegir", "Sólo las selecciones explícitas entran al paquete de contexto."),
                    ("Reconocer", "Las insignias y la franja muestran las fuentes confirmadas."),
                    ("Actualizar", "La instantánea anterior permanece hasta confirmar su actualización."),
                    ("Retirar", "Quitar una fuente y cerrar su editor son acciones diferentes."),
                ]),
        section("canvas_context_example", "TRES DOCUMENTOS, DOS FUENTES", "Abrir no equivale a seleccionar contexto",
                "Mantén notes.md, main.py y manual.pdf abiertos; sólo notes.md y manual.pdf guían este chat.",
                body=[
                    "Pulsa Usar como contexto en notes.md; después prepara manual.pdf sin procesar imágenes "
                    "y confirma. Espera la respuesta del servidor para considerar activo el nuevo conjunto. "
                    "Cambiar a main.py permite editarlo sin agregarlo al contexto seleccionado.",
                    "Editar notes.md marca su instantánea como anterior. La versión confirmada sigue vigente "
                    "hasta que Actualizar contexto termina correctamente; retirar manual.pdf sólo quita esa fuente.",
                ], visual="steps", visual_data={"steps": [
                    ("Abre tres", "notes.md + main.py + manual.pdf conservan pestañas y vistas independientes."),
                    ("Elige dos", "notes.md + manual.pdf entran al conjunto de contexto después de la confirmación."),
                    ("Edita", "main.py sigue abierto sin seleccionar. Editar notes.md marca su contexto como anterior."),
                    ("Actualiza", "Actualiza notes.md para reemplazar su instantánea, o retira manual.pdf sin quitar notes.md."),
                ]}, deck="visual"),
        section("canvas_navigation", "NAVEGACIÓN Y CAMBIOS SIN GUARDAR", "Cambia de documento sin perder el aviso de salida",
                "Los atajos del Canvas actúan dentro de él; el navegador mantiene el control de sus propios atajos.",
                body=[
                    "Pulsa una pestaña, o usa Alt+RePág y Alt+AvPág con el foco dentro del Canvas, incluido "
                    "su visor PDF activo. Ctrl+Tab y Ctrl+Mayús+Tab funcionan sólo si el navegador entrega "
                    "esas teclas a la página. Chrome en Windows reserva Ctrl+Tab físico para sus pestañas: "
                    "en ese caso usa el atajo con Alt.",
                    "Un asterisco identifica cada documento sin guardar, incluso los inactivos. Cerrar una "
                    "pestaña modificada pide confirmación. Salir o recargar solicita el aviso estándar del "
                    "navegador si cualquier pestaña tiene cambios o hay un guardado pendiente. El navegador "
                    "decide si muestra el aviso y el usuario todavía puede salir o forzar el cierre.",
                    "Guarda cada archivo editado en almacenamiento persistente antes de salir. Una página "
                    "no puede garantizar recuperación tras un fallo, un cierre forzado o un aviso descartado. "
                    "Las teclas fuera del Canvas y los mensajes de visores PDF ocultos no cambian sus documentos.",
                ], points=[
                    ("Navegar", "Pulsa pestañas o usa Alt+RePág / Alt+AvPág dentro del Canvas."),
                    ("Límite del navegador", "No es posible quitarle a Chrome su Ctrl+Tab de navegación."),
                    ("Asterisco", "Cada pestaña sin guardar lo muestra, aunque esté en segundo plano."),
                    ("Salir con cuidado", "Guarda los archivos; el navegador controla el aviso final de salida."),
                ]),
        section("interactor_documents", "EDITOR EN VIVO ENTRE DOCUMENTOS", "Enseña en un archivo y continúa en otro",
                "Interactor separa la conexión de la cuenta de la identidad de cada documento del Canvas.",
                body=[
                    "documents enumera identificadores, nombres, revisiones, tipo y estado activo/modificado/"
                    "contexto; no expone contenido, rutas del equipo ni permisos de escritura. read obtiene "
                    "el documento activo y su revisión. activate recibe un target_document_id exacto y "
                    "devuelve una instantánea verificada del destino antes de que type pueda editarlo.",
                    "Cambiar conserva los cambios del origen. Interactor puede abrir o crear texto mientras "
                    "un PDF está activo; el PDF y las demás pestañas permanecen abiertos. La activación "
                    "solicitada por la herramienta continúa la lección. Un cambio manual devuelve el control "
                    "al usuario e interrumpe la escritura; una orden antigua no cruza documentos ni revisiones.",
                    "Explicar selección lee los intervalos exactos sin guardar del documento activo, "
                    "independientemente de las instantáneas elegidas para el chat. El permiso del Editor en "
                    "vivo, Detener, cancelar, Ask Execs y la autorización nativa conservan sus responsabilidades.",
                ], points=[
                    ("Descubrir", "documents enumera metadatos; read captura la revisión activa."),
                    ("Activar", "Elige el ID exacto y verifica el documento de destino."),
                    ("Continuar", "Escribe en ese destino y conserva los demás documentos."),
                    ("Tomar el control", "Un cambio manual interrumpe la escritura y conserva lo escrito."),
                ]),
    ]


def bridge_section(section):
    return section("interactor_architecture", "PUENTE DEL EDITOR EN VIVO", "Una conexión, identidades de documento distintas",
                   "La conexión autenticada del navegador transporta el ID y la revisión exactos de cada acción.",
                   points=[
                       ("Navegador", "Las pestañas retienen editores y visores PDF independientes; el documento activo produce el recibo."),
                       ("Transporte", "ws/interactor/ autentica la sesión y el Origin/Host exactos; el servidor asigna la identidad de la pestaña."),
                       ("Herramienta", "ContextVar lleva conexión/cuenta/sesión; documents/read/activate eligen documentos exactos."),
                       ("Hub", "Colas acotadas, IDs de comandos, plazos, revisiones de la revisión y verificación del buffer completo."),
                       ("Persistencia", "Ask Execs controla new/save; el acceso al host por loopback usa las protecciones existentes de paths y de capacidades de archivo."),
                       ("Transporte al release", "Migración 0218, tool_gate_table, reglas del prompt, módulos congelados e inventarios sin conexión de source/estáticos."),
                   ], deck="list")


def wizard_section(section):
    return section("wizard_intent", "ASISTENTE DE CUENTAS", "Crear la cuenta en esta instancia",
                   "La tarjeta conocida usa un controlador nativo de consola, sin generar comandos con un modelo.",
                   body=[
                       "El controlador lanza createuserconsole, una subclase acotada de createsuperuser de Django, "
                       "con el entorno y la base de datos actuales y shell=False. Conserva la validación normal "
                       "de cuentas, nombres duplicados y contraseñas. Las tarjetas personalizadas se conservan.",
                       "El chat cede el turno mientras se introducen usuario, correo opcional y contraseña en "
                       "la consola propia. Las contraseñas no pasan por el chat ni por argumentos de comandos. "
                       "Se mantienen autenticación, Preguntar ejecuciones, cancelación e identidad del proceso.",
                       "HECHO/DONE verifica una nueva cuenta administrativa persistida antes de informar éxito. "
                       "Las consultas de usuario y estado pertenecen sólo a esa conversación; la finalización "
                       "retira su estado. El campo de correo o la respuesta de finalización no autorizan notificaciones.",
                       "El 9 de noviembre, las cohortes visibles finales crearon y autenticaron diez cuentas "
                       "en inglés y diez en español, con las 260 comprobaciones correctas. Son pruebas del "
                       "código fuente, separadas de la aceptación de paquetes instalados.",
                   ], points=[
                       ("Lanzar", "Tarjeta conocida, entorno y base de datos actuales; sin comandos del modelo."),
                       ("Introducir", "Usuario, correo opcional y contraseña en la consola propia."),
                       ("Confirmar", "Verificar la cuenta administrativa nueva después de HECHO/DONE."),
                       ("Autorizar", "Conservar confirmación y cancelación; notificar requiere otra petición."),
                   ])


def release_sections(section, facts):
    return [
        section("release1970_canvas", f"PUBLICADO · v{facts['version']}", "Varios documentos, contexto explícito y cambios seguros",
                "Los Canvas en inglés y español comparten el modelo de documentos y ofrecen controles localizados.",
                body=[
                    "Hasta 32 pestañas conservan el estado independiente de textos y PDF. La selección "
                    "explícita de varias fuentes tiene insignias, avisos de instantáneas anteriores, "
                    "actualización y eliminación. Interactor puede enumerar y activar documentos sin perder ediciones.",
                    "Verificado el 21 de noviembre de 2026: la ejecución completa en inglés pasó 28 controles "
                    "más una prueba específica de Interactor al abrir texto desde un PDF; la ejecución completa "
                    "en español pasó 29 controles. Cada edición pasó 46 pruebas de transacciones de contexto, "
                    "40 de protocolo/pertenencia de Interactor y lint dirigido de Python/JavaScript. Se "
                    "comprobó texto realmente renderizado y visible en los visores PDF de ambas ediciones.",
                    "Las confirmaciones del contexto se inyectaron explícitamente en el navegador; pertenencia "
                    "y persistencia atómica se probaron por separado sustituyendo las fronteras de modelo/red. "
                    "Las escrituras nativas, la preparación de texto PDF y las acciones autenticadas de Interactor "
                    "usaron sus implementaciones locales reales. Es evidencia del código fuente, no de ingestión "
                    "con un modelo real ni de aceptación de un ejecutable instalado.",
                ], deck_points=[
                    ("Documentos", "32 pestañas con texto, historial y vistas PDF independientes."),
                    ("Contexto", "A+B seleccionados, C sólo abierto; actualizar y retirar explícitamente."),
                    ("Enseñanza", "Interactor descubre y activa identificadores exactos."),
                    ("Evidencia", "Resultados fechados del navegador, servidor y lint, con sus límites."),
                ]),
        section("release1961_catalog", f"PUBLICADA · v{facts['version']}", "La voz pasa al micrófono",
                "El Catálogo de prompts ya no tiene la sección Comandos de voz.",
                body=[
                    "El botón de micrófono junto a Enviar graba, transcribe y envía un prompt directamente, así que "
                    "las dos tarjetas de Comandos de voz (prompts 121 y 122) salieron del Catálogo de prompts. "
                    "La migración 0228 las oculta sin renumerar y el catálogo empieza ahora por Primeros pasos.",
                    "Esta versión también incluye el trabajo de Tlamatini-RC publicado como v1.94.0, v1.95.0 y "
                    "v1.96.0: control remoto alojado, sincronización de aprobaciones y endurecimiento. El modelo "
                    "predeterminado de Talker es legraphista/Orpheus:latest.",
                ], deck_points=[
                    ("Hablar", "Usa el botón de micrófono junto a Enviar."),
                    ("Catálogo", "Sin Comandos de voz; el catálogo empieza por Primeros pasos."),
                    ("Datos", "La migración 0228 oculta los prompts 121 y 122 sin renumerar."),
                    ("Remoto", "Incluye las versiones de Tlamatini-RC v1.94.0 a v1.96.0."),
                ]),
        section("release1935_selection", f"PUBLICADA · v{facts['version']}", "Explica exactamente la selección",
                "El botón del lienzo funciona independientemente de las casillas del chat y del Editor en vivo.",
                body=[
                    "Explicar selección captura todos los intervalos seleccionados del editor sin guardar "
                    "al hacer clic. Sin selección, explica el archivo completo actual. Conserva el borrador "
                    "del chat, las selecciones, el documento y las casillas.",
                    "La solicitud autenticada va directamente al modelo configurado sin herramientas, historial, "
                    "contexto cargado, internet, compactación ni instrucciones de automodificación. Sigue disponible "
                    "mientras se reconstruyen las herramientas del chat normal. La cancelación, la entrega "
                    "de mensajes y el registro de uso conservan los servicios normales de la aplicación.",
                    "Admite hasta 64 intervalos y 262.144 unidades UTF-16, sujetos a la capacidad real del modelo. "
                    "El resto del archivo no consume el límite de la selección y ningún fragmento se trunca "
                    "silenciosamente. La tutoría de Interactor conserva su contrato separado de documento completo.",
                    "El 12 de noviembre pasaron 58 regresiones y las 256 combinaciones de casillas en cada "
                    "edición. El modelo configurado explicó el valor seleccionado sin guardar en ambos idiomas "
                    "sin herramientas. Estas pruebas de código no certifican un nuevo ejecutable instalado.",
                ], deck_points=[
                    ("Seleccionar", "Capturar los intervalos sin guardar; sin selección, el archivo completo."),
                    ("Explicar", "Sin dependencia de casillas, herramientas, historial ni contexto cargado."),
                    ("Conservar", "Mantener borrador, documento, selección y preferencias."),
                    ("Límites", "64 intervalos; 262.144 unidades UTF-16; capacidad real del modelo."),
                ]),
        section("release1935_execution", f"PUBLICADA · v{facts['version']}", "Responder al terminar el script lanzador",
                "Executer deja de esperar tuberías de salida heredadas por un proceso hijo separado.",
                body=[
                    "Un comando start de Windows lanzó el cubo original de Rust durante 90 segundos, pero la "
                    "salida llegó después de cerrarse: la captura esperaba el fin de una tubería que seguía "
                    "abierta en el hijo separado aunque el script exterior ya había terminado.",
                    "La ruta de scripts bloqueantes dirige stdout y stderr a archivos únicos conservados en "
                    "el directorio aislado, espera al script directo y lee una instantánea acotada con "
                    "manejadores de lectura separados. Los comandos directos siguen bloqueando; los hijos "
                    "separados explícitamente pueden continuar. No se añadió un límite de ciclos ni una "
                    "decisión de progreso basada en modelos.",
                    "La reproducción del 12 de noviembre usó el mismo ejecutable y sus shaders incorporados "
                    "mediante llamadas MCP reales a Executer, Windower y Shoter. El tiempo observado pasó de "
                    "100,50 segundos a 5,05 en inglés y 5,06 en español, con el cubo aún vivo. Pasaron las "
                    "65 regresiones seleccionadas en cada edición.",
                    "El bloqueo posterior de entrega de la respuesta final del registro original sigue sin "
                    "diagnóstico concluyente. Esta corrección no determina su causa ni promete resolver toda "
                    "tarea repetida. El registro de cambios de Executer del 12 de noviembre conserva pruebas y límites.",
                ], deck_points=[
                    ("Causa", "Los manejadores heredados retrasaban la salida tras terminar el script."),
                    ("Corrección", "Captura en archivos; esperar al script directo y leer la instantánea."),
                    ("Prueba", "Mismos recursos: 100,50 segundos antes; 5,05/5,06 después."),
                    ("Alcance", "65 pruebas por edición; la entrega final conserva un incidente sin resolver."),
                ]),
        section("release1935_voice", f"PUBLICADA · v{facts['version']}", "Seguir hablando al cambiar de ventana",
                "Una página cubierta, oculta o minimizada ya no pausa la voz ni limita el mensaje a 100 segundos.",
                body=[
                    "La cola compartida reintenta un fragmento fallido y puede transferir el texto restante "
                    "a la voz de Windows cuando el navegador no puede continuar. Cerrar o recargar la página "
                    "transfiere la voz pendiente del chat normal; la narración interactiva no usa esa transferencia.",
                    "La voz del equipo usa ajustes y controles de la cuenta, conserva la política de voces "
                    "femeninas y el idioma español de esta edición, y no abre otra consola. Modo silencioso, "
                    "Escape, clic en el avatar y cancelación siguen deteniendo la voz explícitamente.",
                    "Tlamatini debe seguir ejecutándose y disponer de una voz adecuada. Un reintento puede "
                    "repetir parte de un fragmento; la solicitud al equipo conserva el límite de 20.000 "
                    "caracteres. La guía de reproducción de voz detalla la recuperación y sus límites.",
                ], deck_points=[
                    ("Continuar", "Hablar con la página cubierta, oculta o minimizada."),
                    ("Recuperar", "Reintentar fragmentos; transferir el resto a la voz de Windows."),
                    ("Controlar", "Silencio, Escape, clic en el avatar y cancelación siguen disponibles."),
                    ("Límites", "La aplicación y el audio deben estar disponibles; el texto está acotado."),
                ]),
        section("release1935_downloads", f"PUBLICADA · v{facts['version']}", "Seguir descargas con estados fieles",
                "Vistas ordenables por cuenta, orientación de recuperación y esperas acotadas muestran el progreso.",
                body=[
                    "El espacio de trabajo ofrece ordenación por varias columnas, filtros, paginación y vistas "
                    "guardadas por cuenta. Una descarga verificada sigue completada aunque se detenga su sesión "
                    "de pares. Se separan los errores históricos de los actuales; las acciones afectan sólo "
                    "selecciones aptas e informan de los trabajos omitidos.",
                    "La espera de finalización termina al pausar, detener o cancelar. Tolera hasta 600 segundos "
                    "sin API, concede 180 segundos de recuperación a un fallo de entrega, renueva credenciales "
                    "caducadas y deja de esperar tras dos horas sin progreso. Terminar la espera no cancela "
                    "la transferencia subyacente de Jobs.",
                    "Las lecturas JSON vacías o truncadas tienen reintentos acotados; las modificaciones de "
                    "torrents nunca se repiten automáticamente. Antes de recuperar, lee la revisión actual y "
                    "verifica la ruta y el SHA-256 de entrega. Las correcciones de planificación y escritura "
                    "del motor requieren actualizar por separado el servicio Tlachihuani Jobs.",
                ], deck_points=[
                    ("Inspeccionar", "Ordenar, filtrar y paginar la cola; conservar vistas por cuenta."),
                    ("Confiar", "Mantener completado; distinguir errores antiguos de fallos actuales."),
                    ("Esperar", "Pausa, parada o cancelación terminan la espera, sin cancelar la transferencia."),
                    ("Verificar", "Revisiones y hashes actuales; la actualización del servicio es aparte."),
                ]),
        section("release1935_requests", f"PUBLICADA · v{facts['version']}", "Resolver solicitudes concretas directamente",
                "La creación de cuentas y las preguntas puras sobre directorios usan contratos explícitos.",
                body=[
                    "La tarjeta conocida del catálogo lanza createuserconsole con el entorno y la base de datos "
                    "de esta instancia. El chat cede el turno para introducir datos privados en la consola; "
                    "conserva Preguntar ejecuciones y cancelación. HECHO/DONE verifica una cuenta administrativa "
                    "nueva persistida antes de informar éxito. Las tarjetas personalizadas se conservan.",
                    "Una pregunta pura sobre directorios permitidos lee la instantánea actual de path_guard, "
                    "sin clasificador ni exploración del disco y sin conceder permisos. Una petición mixta "
                    "continúa por el procesamiento normal, sin convertirse en una lista de directorios.",
                    "Los valores centrales usan deepseek-v4.1-flash:cloud para texto y mistral-large-4:cloud "
                    "junto con gemma4:cloud para visión; las elecciones configuradas siguen siendo la autoridad. "
                    "legraphista/Orpheus:latest es el modelo de voz predeterminado. Las cohortes visibles "
                    "del 9 de noviembre "
                    "crearon y autenticaron 20 cuentas con 260 comprobaciones entre ambas ediciones.",
                ], deck_points=[
                    ("Crear", "La tarjeta conocida usa el entorno actual y entrada privada en consola."),
                    ("Confirmar", "Verificar la cuenta nueva persistida antes de anunciar el resultado."),
                    ("Listar", "Consultar las raíces permitidas, sin explorar ni conceder permisos."),
                    ("Configurar", "Los valores centrales respetan los ajustes explícitos de modelos."),
                ]),
        section("release1924", f"PUBLICADA · v{facts['version']}", "Versiones coincidentes antes de compilar",
                "Un mismo número previsto para ambas ediciones y una modalidad explícita en cada paquete.",
                body=[
                    "BuildTlamatinis.cmd consulta el resolvedor de cada repositorio y anticipa en memoria su "
                    "generador de versión. Compara el número que informará el ejecutable, sin exigir una etiqueta "
                    "en HEAD. Fija el valor común mediante --version antes de iniciar los generadores completos.",
                    "La modalidad Privada o Pública ejecuta ambas ediciones en paralelo con --self-modify. Los "
                    "ZIP nuevos se verifican por CRC y SHA-256 y se trasladan a carpetas por edición, modalidad "
                    "y minuto de inicio. Cada edición correcta conserva su archivo aunque falle la otra; en ese "
                    "caso el comando conjunto devuelve error.",
                    "Los generadores incorporan release_type en el módulo de versión. El registro empieza con "
                    "la versión y la modalidad Privada/Pública. Los modos de desarrollo y sin especificar se "
                    "indican expresamente; no se deduce la modalidad de carpetas, variables ni credenciales.",
                ], deck_points=[
                    ("Anticipar", "Consultar los resolvedores reales antes del trabajo costoso."),
                    ("Fijar", "Un mismo --version; compilaciones paralelas con --self-modify."),
                    ("Entregar", "ZIP separados por edición y modalidad, con sus comprobantes."),
                    ("Identificar", "Leer la modalidad incorporada al comienzo del registro."),
                ]),
        section("release1924_recovery", f"PUBLICADA · v{facts['version']}", "Recuperación aislada y Markdown legible",
                "Las dependencias de compilación y la lectura fiel del texto forman parte del contrato.",
                body=[
                    "Las compilaciones independientes usan Temp/build-env de la aplicación; el lanzador "
                    "combinado asigna cachés separadas bajo la carpeta de versiones. Si falla la preparación "
                    "sin un entorno aislado válido, la compilación se detiene antes de limpiar NumPy o usar "
                    "pip --user en el Python de la máquina. Una caché aislada válida puede reutilizarse.",
                    "Los README.md legibles con controles aislados siguen siendo editables. La decodificación "
                    "estricta reconoce la BOM y conserva los bytes. Un NUL decodificado, un exceso de controles "
                    "o una codificación malformada siguen provocando el rechazo antes de sustituir el lienzo.",
                    "Evidencia fechada: la campaña del 8 de noviembre verificó las cuatro compilaciones reales "
                    "y sus ejecutables empaquetados con versión 1.92.3 y modalidades correctas. Pasaron la "
                    "integridad, las auditorías de datos públicos, 26 pruebas de aislamiento y el lint específico. "
                    "Esta actualización documental no renombra esos paquetes ni certifica otra instalación, "
                    "reinicio o ejecución con modelos en vivo.",
                ], deck_points=[
                    ("Caché", "Entornos aislados de la aplicación; sin temporales en perfiles de usuario."),
                    ("Fallo", "Detenerse antes de tocar el Python global si no hay caché válida."),
                    ("Lienzo", "Conservar texto y bytes legibles; rechazar los binarios reales."),
                    ("Evidencia", "Cuatro compilaciones del 8 de noviembre, con su identidad real 1.92.3."),
                ]),
        section("release1923", "CONSERVADO DE v1.92.3", "Descargas, escritura y distribución en Windows",
                "Descargas, tecleo, actualizaciones y ejecución en Windows",
                body=["Torrenter permite gestionar las descargas de cada cuenta desde el chat y el panel de control agéntico. El Editor en vivo y Terminater admiten hasta 250 WPM. El actualizador distribuye el desinstalador y conserva la bóveda. Cada compilación mantiene un bloqueo sobre el entorno de Python correspondiente a sus dependencias.",
                      "Las compilaciones con dependencias distintas pueden coexistir. Un bloqueo del sistema operativo protege la preparación y toda la compilación. El paquete 1.92.3 entrega el desinstalador verificado y conserva la bóveda data.keys existente."], deck_points=[
                    ('Tecleo', 'Editor en vivo: 40–250 WPM. Terminater: 20–250 WPM.'),
                    ('Descargas', 'El chat, ACP y XT comparten la cola de Jobs de la cuenta.'),
                    ('Actualización', 'Distribuye el desinstalador verificado y conserva la bóveda.'),
                    ('Compilación', 'Bloquea el entorno que corresponde a la huella de dependencias.'),
                ]),
        section("release1911", "OCTUBRE DE 2026 · v1.91.1", "Arreglos del Prompt Flow y nombres cortos de tools",
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
                    ("Inventario de esa versión", "86 agents; 110 tools; 220 migraciones; "
                     "64 módulos JS; 29 hojas de estilo."),
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
                    ("Inventario de esa versión", "86 agents; 110 tools; 220 migraciones; "
                     "64 módulos JS; 29 hojas de estilo."),
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
                    ("Inventario de esa versión", "86 agents; 67 wrapped; 110 tools integrados; "
                     "219 migraciones. Conteos de la revisión de octubre de 2026."),
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
