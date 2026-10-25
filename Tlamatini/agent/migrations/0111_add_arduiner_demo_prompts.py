# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""
Seed three Catalog-of-Prompts demos for **Arduino firmware programming** through
the wrapped **chat_agent_arduiner** Multi-Turn tool (the Arduino CLI / `arduino-cli`
bridge). They run basic -> high complexity and mirror the ESP32er demos (0107) and
STM32er demos (0103), but built to Arduiner's grain: Arduiner drives the
`arduino-cli` binary DIRECTLY (no MCP server), the microcontroller is chosen by the
**FQBN** (e.g. arduino:avr:uno), "provisioning" means auto-downloading the
arduino-cli binary AND auto-installing the board's core, the project is a plain
Arduino sketch scaffolded from the bundled **ArduinoTemplateProject**, and the
firmware is Arduino-core C++ (.ino):

    70  ARDUINO GENESIS        basic   bootstrap (Arduiner DOWNLOADS + installs +
                                       validates the arduino-cli binary itself) ->
                                       validate -> create_project (from the bundled
                                       ArduinoTemplateProject) -> write_source (blink
                                       .ino) -> build (auto-installs arduino:avr) ->
                                       list_artifacts. NO board required.
    71  ARDUINO BLINKY         medium  validate -> create_project -> write_source
                                       (pin-13 blink + Serial prints) -> build ->
                                       list_artifacts -> build_and_upload. The upload
                                       is board-OPTIONAL: Arduiner's safety preflight
                                       refuses it cleanly with 'No serial port
                                       detected' if no board is attached (expected +
                                       routable, not a crash).
    72  ARDUINO HIL OBSERVATORY  hard  validate (REQUIRES a connected serial port)
                                       -> device_list -> create_project ->
                                       write_source (counter firmware that prints
                                       'BOOT tlamatini arduino count=<n>' over Serial)
                                       -> build -> build_and_upload (REAL flash over
                                       USB-serial) -> monitor (read the RUNNING
                                       board's serial stream and watch the counter
                                       climb). Demo #3 UPLOADS TO AND OBSERVES THE
                                       HARDWARE end-to-end.

Arduino hardware nuance baked into demo #72: a classic Arduino (Uno/Nano/Mega)
flashes over its USB-serial bridge (ATmega16U2 / CH340 / FTDI), and that SAME port
carries the firmware's `Serial.print` output — so, like the ESP32 (and unlike the
STM32F4-Discovery whose ST-LINK VCP is not routed to the MCU USART, see 0104), the
serial monitor reads the firmware output natively with NO extra wiring. The serial
`monitor` is therefore the authoritative hardware-in-the-loop proof here.

All three drive ONLY chat_agent_arduiner and remind the user to tick ONLY the
**Multi-Turn** checkbox (chat_agent_arduiner is NOT behind the ACPX/Skill surface,
so ACPX is not required — same as the ESP32er 0107, STM32er 0103, Kalier 0099 demos).

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js) enumerates promptName
'prompt-1','prompt-2',... and BREAKS at the first missing slot, so the catalog must
stay a contiguous, gap-free 'prompt-1..N'. Slots 1-69 are occupied (0108 appended
the flow-making demo at 69); these three APPEND at 70-72 with no shift of any
existing prompt. Reverse deletes 70-72. (MAX_PROMPTS=100.)
"""
from django.db import migrations


# Arduino teal banner palette (deep teal -> Arduino teal -> bright cyan -> pale aqua),
# the same family as the ``.canvas-item.arduiner-agent`` gradient, with a text-shadow
# so the white label stays legible across the bright aqua end.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#00363A 0%,#008184 38%,#00C4CC 70%,#C8F2F0 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


ARDUINO_GENESIS_DEMO = (
    "Tlamatini, ejecuta la demo **ARDUINO GENESIS**, por favor &mdash; una muestra básica, de principio a fin, "
    "del *autoaprovisionamiento zero-config*, la *auto-instalación del core* y el *preflight de seguridad* de Arduiner, "
    "controlada por completo desde el chat a través del tool wrapper **chat_agent_arduiner**: desde una máquina limpia "
    "DESCARGA e instala el binario arduino-cli ella misma, valida el entorno de build, arma "
    "un sketch de Arduino a partir del ArduinoTemplateProject incluido, ESCRIBE un pequeño .ino de blink y luego "
    "compila + ENLAZA a una imagen de firmware (auto-instalando el core AVR en el camino) y lista el "
    ".hex/.elf &mdash; todo SIN una placa conectada (una demo pura de aprovisionar + construir). "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques &mdash; confía en ellas y ve directo al "
    "Paso 1): (a) **el usuario instaló SÓLO Tlamatini** (más, para un upload real después, el "
    "driver USB-serial de la placa) &mdash; NO instalas ni configuras arduino-cli, Arduiner lo descarga "
    "automáticamente; (b) NO hace falta hardware Arduino &mdash; no se flashea nada; (c) marca SÓLO la "
    "casilla **Multi-Turn** antes de enviar (ACPX NO se requiere &mdash; chat_agent_arduiner es el "
    "ÚNICO tool que puedes usar; no uses chat_agent_executer / chat_agent_pythonxer ni tools de ACPX). Cada "
    "paso es exactamente UNA llamada a chat_agent_arduiner con la forma \"Run Arduiner with action='<action>' and "
    "<k>='<v>' ...\". Después de cada llamada lee el JSON que devuelve (un bloque INI_SECTION_ARDUINER bajo el "
    "log_excerpt de la ejecución) y captura action / tool / ok / returncode / success / fqbn / sketch_path / "
    "stage, además del body. Si un paso devuelve ok=false / success=false, regístralo tal cual, NO "
    "canceles, continúa. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128268; ARDUINO GÉNESIS &#128295;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini Arduiner &mdash; aprovisionar &middot; validar &middot; escribir &middot; compilar</div></div>. "
    "\n\n"
    "Paso 1 (aprovisionamiento ZERO-CONFIG): llama a **chat_agent_arduiner** con el request "
    "\"Run Arduiner with action='bootstrap'\". Esto hace que Arduiner DESCARGUE el binario oficial de release de arduino-cli "
    "en un directorio de instalación por usuario y corra config init + core update-index &mdash; con "
    "NINGUNA configuración manual. Del body captura la acción de instalación (present / download-extract), el "
    "install_dir y 'overall : OK'. Si overall es FAILED, lo más probable es que el host no tenga internet &mdash; "
    "salta al banner de cierre con un veredicto 'ERROR DE APROVISIONAMIENTO'. "
    "\n\n"
    "Paso 2 (preflight de seguridad): llama a **chat_agent_arduiner** con el request "
    "\"Run Arduiner with action='validate'\". Esto valida el entorno SIN construir: "
    "captura arduino_cli_resolvable y (como validate también sondea el hardware) el resumen del serial "
    "(present / arduino_like). Que falte un puerto serial está BIEN aquí &mdash; esta demo nunca flashea. "
    "\n\n"
    "Paso 3 (scaffold desde la plantilla): llama a **chat_agent_arduiner** con el request \"Run Arduiner "
    "with action='create_project' and sketch_path='C:/Temp/arduino/tlamatini_genesis' and "
    "fqbn='arduino:avr:uno'\". Esto copia el ArduinoTemplateProject incluido, renombra su .ino al "
    "nombre de la carpeta y estampa el FQBN en sketch.yaml; CAPTURA el **sketch_path** &mdash; pásalo "
    "a cada paso posterior. "
    "\n\n"
    "Paso 4 (escribe el firmware &mdash; sobrescribe el .ino): llama a **chat_agent_arduiner** con el "
    "request \"Run Arduiner with action='write_source' and "
    "sketch_path='C:/Temp/arduino/tlamatini_genesis' and rel_path='tlamatini_genesis.ino' and "
    "content='''<CODE>'''\". Para <CODE> escribe un sketch de blink de core Arduino MÍNIMO y COMPILABLE: un "
    "`setup()` que llame a pinMode(LED_BUILTIN, OUTPUT) y Serial.begin(115200), y un `loop()` que "
    "conmute el LED con digitalWrite + delay(500). Pásalo como un literal content con comillas triples "
    "(content='''...''') para que los newlines y las llaves sobrevivan al parser de asignaciones. (NOTA: arduino-cli "
    "requiere que el basename del .ino principal sea igual al nombre de la carpeta del sketch &mdash; de ahí "
    "'tlamatini_genesis.ino'.) "
    "\n\n"
    "Paso 5 (compila + ENLAZA &rarr; firmware): llama a **chat_agent_arduiner** con el request \"Run Arduiner "
    "with action='build' and sketch_path='C:/Temp/arduino/tlamatini_genesis' and "
    "fqbn='arduino:avr:uno'\". Arduiner primero AUTO-INSTALA el core arduino:avr (arduino-cli no "
    "auto-instala plataformas al compilar), luego compila. Confirma returncode=0 y que el stdout muestre "
    "'Sketch uses ... program storage space'. NOTA: la primera instalación del core + compile descarga el toolchain AVR, "
    "así que puede tardar un minuto &mdash; eso es normal. "
    "\n\n"
    "Paso 6 (artefactos): llama a **chat_agent_arduiner** con el request \"Run Arduiner with "
    "action='list_artifacts' and sketch_path='C:/Temp/arduino/tlamatini_genesis'\". Captura los "
    "paths .hex / .elf del body (el build corre con --export-binaries, así que quedan bajo "
    "<sketch>/build/). "
    "\n\n"
    "Paso 7: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Arduino Genesis &mdash; Reporte de aprovisionamiento y build</strong>' y con las columnas "
    "<em>paso</em>, <em>stage</em> (bootstrap|validate|project|author|build), <em>arduiner_action</em>, "
    "<em>status</em> (ok|error), <em>resumen</em> (install_dir para bootstrap; arduino_cli_resolvable "
    "para validate; sketch_path para create; .ino escrito para author; returncode para build; los paths de firmware "
    "para list_artifacts) &mdash; una fila por cada llamada en orden de ejecución, status tal cual del "
    "bloque INI_SECTION_ARDUINER (NO lo reclasifiques). Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a; o rayado #f1f5f9), tono verde ok, rojo suave error. "
    "\n\n"
    "Paso 8: cierra con un banner HTML que reutilice el estilo del Paso 0, en letras grandes, "
    "'&#9989; ARDUINO-CLI APROVISIONADO &amp; FIRMWARE CONSTRUIDO' (bootstrap OK, validate resolvió el CLI, "
    "build returncode=0 y artefactos listados), '&#9888;&#65039; GÉNESIS PARCIAL' (algunos pasos ok, algunos "
    "error) o '&#10060; ERROR DE APROVISIONAMIENTO' (overall de bootstrap FAILED), y debajo una métrica "
    "de una línea 'arduino-cli: <install action> &middot; install_dir: <...> &middot; sketch: <sketch_path> "
    "&middot; build rc: <0> &middot; artefactos: .hex/.elf'. Termina con END-RESPONSE."
)


ARDUINO_BLINKY_DEMO = (
    "Tlamatini, ejecuta la demo **ARDUINO BLINKY**, por favor &mdash; una versión de complejidad media del "
    "clásico 'hello world' embebido, controlada por completo desde el chat a través del tool wrapper "
    "**chat_agent_arduiner**: valida el entorno en preflight, arma un sketch desde "
    "el ArduinoTemplateProject incluido, ESCRIBE un .ino de blink en el pin 13 que también imprime por Serial, "
    "lo compila + enlaza (auto-instalando el core AVR), lista los artefactos y luego intenta subirlo "
    "a una placa Arduino para que el LED on-board parpadee. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques; ve directo al Paso 1): (a) el usuario "
    "instaló SÓLO Tlamatini &mdash; Arduiner auto-descarga/instala arduino-cli ella misma en el primer "
    "uso, así que NUNCA configuras paths de tools; (b) el build NO necesita placa; el paso de UPLOAD necesita un "
    "Arduino por USB (flashea por el puente USB-serial de la placa &mdash; SIN programmer externo "
    "para el camino común) &mdash; PERO el preflight de seguridad de Arduiner RECHAZARÁ el upload "
    "con 'No serial port detected' si no hay placa conectada, lo cual es ESPERADO y enrutable, NO un "
    "crash: regístralo tal cual y CONTINÚA; (c) marca SÓLO la casilla **Multi-Turn** (ACPX NO se "
    "requiere). Usa SÓLO chat_agent_arduiner, UNA llamada por paso con la forma \"Run Arduiner with "
    "action='<action>' and <k>='<v>' ...\". Lee cada JSON que devuelve (bloque INI_SECTION_ARDUINER bajo "
    "log_excerpt), captura action/tool/ok/returncode/success/fqbn/sketch_path/port/stage, y con "
    "ok=false regístralo tal cual y CONTINÚA. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128161; ARDUINO BLINKY &#128161;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini Arduiner &mdash; validar &middot; escribir &middot; build &middot; upload</div></div>. "
    "\n\n"
    "Paso 1 (preflight de seguridad): \"Run Arduiner with action='validate'\" &mdash; captura "
    "arduino_cli_resolvable y el resumen del serial (present / arduino_like) como la base 'before' "
    "(Arduiner auto-aprovisiona arduino-cli como parte de esto si hace falta). "
    "\n\n"
    "Paso 2 (scaffold): \"Run Arduiner with action='create_project' and "
    "sketch_path='C:/Temp/arduino/tlamatini_blinky' and fqbn='arduino:avr:uno'\". CAPTURA el "
    "**sketch_path**. "
    "\n\n"
    "Paso 3 (escribe el firmware &mdash; sobrescribe el .ino): \"Run Arduiner with "
    "action='write_source' and sketch_path='C:/Temp/arduino/tlamatini_blinky' and "
    "rel_path='tlamatini_blinky.ino' and content='''<CODE>'''\". Para <CODE> escribe un sketch MÍNIMO y "
    "COMPILABLE de core Arduino: setup() con pinMode(LED_BUILTIN, OUTPUT) + Serial.begin(115200) "
    "+ un banner 'ARDUINO BLINKY starting', y un loop() que ponga el LED en HIGH "
    "(Serial.println \"LED ON\"), delay(500), LED en LOW (Serial.println \"LED OFF\"), delay(500). Pásalo "
    "como un literal content con comillas triples (content='''...''') para que los newlines y las llaves sobrevivan al "
    "parser. (arduino-cli requiere que el basename del .ino sea igual al nombre de la carpeta &mdash; de ahí "
    "'tlamatini_blinky.ino'.) "
    "\n\n"
    "Paso 4 (compila + ENLAZA): \"Run Arduiner with action='build' and "
    "sketch_path='C:/Temp/arduino/tlamatini_blinky' and fqbn='arduino:avr:uno'\". Arduiner "
    "auto-instala primero el core arduino:avr, luego compila. Confirma returncode=0 y la línea 'Sketch "
    "uses ... program storage space'. (La primera instalación del core + build jala el toolchain AVR &mdash; "
    "puede tardar un minuto.) Si returncode es distinto de cero, captura el diagnóstico del compilador del stderr "
    "&mdash; evidencia enrutable; puedes detenerte después del reporte con un veredicto 'ERROR DE BUILD'. "
    "\n\n"
    "Paso 5 (artefactos): \"Run Arduiner with action='list_artifacts' and "
    "sketch_path='C:/Temp/arduino/tlamatini_blinky'\". Captura el path del .hex. "
    "\n\n"
    "Paso 6 (upload &mdash; flashea por USB-serial): \"Run Arduiner with action='build_and_upload' and "
    "sketch_path='C:/Temp/arduino/tlamatini_blinky' and fqbn='arduino:avr:uno'\". Si hay una placa "
    "conectada, el body muestra a avrdude escribiendo + verificando el firmware por el puente USB-serial; si "
    "no, el preflight de Arduiner devuelve ok=false con 'No serial port detected' &mdash; regístralo tal cual "
    "y CONTINÚA (placa ausente es el soft-fail esperado de esta demo). "
    "\n\n"
    "Paso 7: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Arduino Blinky &mdash; Reporte de ejecución</strong>' y con las columnas <em>paso</em>, <em>stage</em> "
    "(validate|project|author|build|upload), <em>arduiner_action</em>, <em>status</em> (ok|error), "
    "<em>resumen</em> (cli resolved; sketch_path; build returncode; path del .hex; upload verify o "
    "'preflight refused: no board') &mdash; una fila por cada llamada en orden de ejecución, status tal cual de "
    "el bloque INI_SECTION_ARDUINER. Celdas del cuerpo claras (background:#ffffff;color:#0f172a; o rayado "
    "#f1f5f9); tono verde ok, rojo suave error. "
    "\n\n"
    "Paso 8: cierra con un banner HTML que reutilice el estilo del Paso 0 "
    "'&#9989; BLINKY EN VIVO' (build returncode=0 AND upload verified), "
    "'&#9888;&#65039; CONSTRUIDO, SIN PLACA' (build ok pero el preflight rechazó el upload / sin placa) o "
    "'&#10060; ERROR DE BUILD' (build returncode &ne; 0), y debajo una métrica de una línea "
    "'sketch: <sketch_path> &middot; build rc: <0> &middot; upload: <verified|no-board> &middot; led: "
    "pin&nbsp;13 @ 500&nbsp;ms'. Termina con END-RESPONSE."
)


ARDUINO_HIL_OBSERVATORY_DEMO = (
    "Tlamatini, ejecuta la demo **ARDUINO HIL OBSERVATORY**, por favor &mdash; una muestra avanzada "
    "**hardware-in-the-loop** que SUBE A UNA PLACA REAL y la OBSERVA de principio a fin, "
    "controlada por completo desde el chat a través del tool wrapper **chat_agent_arduiner**: valida en preflight"
    "que haya un puerto serial conectado, arma y ESCRIBE un firmware que incrementa un "
    "contador global y lo transmite por Serial, lo construye + SUBE al Arduino y luego PRUEBA que está "
    "corriendo en silicio real leyendo el stream serial en vivo de la placa EN EJECUCIÓN y viendo "
    "subir el contador. "
    "Nota de hardware del Arduino (no la omitas): un Arduino clásico (Uno/Nano/Mega) flashea por su "
    "**puente USB-serial** (ATmega16U2 / CH340 / FTDI), y ESE MISMO puerto USB-serial lleva el "
    "output `Serial.print` del firmware &mdash; así que, como el ESP32 (y A DIFERENCIA de la STM32F4-Discovery "
    "cuyo VCP del ST-LINK no se enruta al USART del MCU), el serial monitor lee el output del firmware "
    "de forma nativa SIN cableado extra. El serial monitor es, por lo tanto, la prueba HIL autoritativa "
    "aquí. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques; ve directo al Paso 1): (a) el usuario "
    "instaló SÓLO Tlamatini + el driver USB-serial de la placa (Arduiner auto-aprovisiona arduino-cli "
    "ella misma); (b) **hay una placa Arduino CONECTADA** por USB y se enumera como un puerto serial &mdash; "
    "esta demo REQUIERE hardware; (c) marca SÓLO la casilla **Multi-Turn** (ACPX NO se requiere). "
    "Usa SÓLO chat_agent_arduiner, UNA llamada por paso con la forma \"Run Arduiner with action='<action>' and "
    "<k>='<v>' ...\". Lee cada JSON que devuelve (bloque INI_SECTION_ARDUINER bajo log_excerpt), captura "
    "action/tool/ok/returncode/success/fqbn/sketch_path/port/stage, y con ok=false regístralo tal cual "
    "y CONTINÚA. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128300; ARDUINO HIL OBSERVATORY &#9889;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini Arduiner &mdash; validate &middot; upload &middot; observar serial en vivo</div></div>. "
    "\n\n"
    "Paso 1 (preflight de seguridad &mdash; CONFIRMA LA PLACA): \"Run Arduiner with action='validate'\". "
    "Esto auto-aprovisiona arduino-cli si hace falta y valida el entorno INCLUIDO el serial "
    "port (validate sondea un adaptador conectado). Del reporte captura arduino_cli_resolvable "
    "y el resumen del serial (present / arduino_like / ports / matched FQBN). **Si no hay puerto serial "
    "presente, DETENTE**: salta al banner de cierre con un veredicto 'SIN PLACA' y dile al usuario que "
    "conecte el Arduino por USB (esto es una demo de hardware). Sólo pasa al Paso 2 cuando haya un puerto serial "
    "presente. "
    "\n\n"
    "Paso 2 (enumera puertos + descubre el FQBN): \"Run Arduiner with action='device_list'\". Del "
    "JSON captura el puerto(s) serial conectado(s) (p. ej. COM3 en Windows) y cualquier FQBN de matching_boards. "
    "Elige el puerto del Arduino &mdash; pásalo como **port** a los pasos de upload/monitor &mdash; y, "
    "si se reportó un FQBN que coincide, prefiérelo; si no, usa **fqbn='arduino:avr:uno'**. "
    "\n\n"
    "Paso 3 (scaffold): \"Run Arduiner with action='create_project' and "
    "sketch_path='C:/Temp/arduino/tlamatini_hil' and fqbn='<the FQBN from Step 2>'\". CAPTURA el "
    "**sketch_path**. "
    "\n\n"
    "Paso 4 (escribe el firmware &mdash; sobrescribe el .ino): \"Run Arduiner with "
    "action='write_source' and sketch_path='C:/Temp/arduino/tlamatini_hil' and "
    "rel_path='tlamatini_hil.ino' and content='''<CODE>'''\". Para <CODE> escribe un programa MÍNIMO y COMPILABLE "
    "de core Arduino que declare, a nivel de archivo, un `unsigned long g_count = 0;`, en setup() llame a "
    "Serial.begin(115200) y pinMode(LED_BUILTIN, OUTPUT), y en loop() incremente g_count, conmute "
    "el LED, imprima una sola línea de status terminada en newline con la forma EXACTA "
    "'BOOT tlamatini arduino count=<n>' con Serial.println, y delay(500). Pásalo como un literal "
    "content con comillas triples (content='''...''') para que los newlines y las llaves sobrevivan al parser. "
    "(arduino-cli requiere que el basename del .ino sea igual al nombre de la carpeta &mdash; de ahí "
    "'tlamatini_hil.ino'.) "
    "\n\n"
    "Paso 5 (compila + ENLAZA): \"Run Arduiner with action='build' and "
    "sketch_path='C:/Temp/arduino/tlamatini_hil' and fqbn='<the FQBN from Step 2>'\". Arduiner "
    "auto-instala primero el core de la placa. Exige returncode=0. (La primera instalación del core + build jala "
    "el toolchain &mdash; puede tardar un minuto.) Si el build falla, captura el diagnóstico y puedes "
    "detenerte después del reporte con 'ERROR DE BUILD'. "
    "\n\n"
    "Paso 6 (UPLOAD &mdash; flash REAL por USB-serial): \"Run Arduiner with "
    "action='build_and_upload' and sketch_path='C:/Temp/arduino/tlamatini_hil' and fqbn='<the FQBN "
    "from Step 2>' and port='<the port from Step 2>'\". El preflight ya confirmó la placa en el "
    "Paso 1; el body debería mostrar a avrdude 'writing' / 'reading on-chip flash data' / 'verified' por "
    "el puente USB-serial. Captura el resultado del verify &mdash; este es el UPLOAD real del programa "
    "a la placa Arduino. "
    "\n\n"
    "Paso 7 (prueba HIL &mdash; observa el stream serial en vivo): \"Run Arduiner with action='monitor' "
    "and sketch_path='C:/Temp/arduino/tlamatini_hil' and port='<the port from Step 2>' and "
    "baud='115200' and monitor_seconds='6'\". Esto abre un `arduino-cli monitor "
    "--config baudrate=115200` acotado, drena el output serial de la placa EN EJECUCIÓN por 6 segundos, luego se detiene. "
    "Captura la PRIMERA y la ÚLTIMA línea 'BOOT tlamatini arduino count=<n>' y confirma que el count va "
    "AUMENTANDO &mdash; prueba directa, sobre silicio, de que el loop() se está ejecutando en hardware real (no sólo "
    "que el .hex se flasheó). "
    "\n\n"
    "Paso 8: muestra un MARCADOR DE STATUS &mdash; una fila de chips HTML con la forma "
    "<span style='display:inline-block;padding:8px 16px;margin:3px;border-radius:10px;"
    "font-weight:800;background:CHIP_BG;color:#ffffff;'>LABEL</span>: un chip 'validate: <ok|err>', un "
    "chip 'port: <COMx>', un chip 'build: <ok|err>', un chip 'upload: <ok|err>', un chip 'monitor: <ok|err>' "
    "(CHIP_BG #16a34a cuando es ok, si no #dc2626), y un chip 'count: <first>&rarr;<last>' "
    "(CHIP_BG #008184). "
    "\n\n"
    "Paso 9: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Arduino HIL Observatory &mdash; Reporte de ejecución</strong>' y con las columnas <em>paso</em>, "
    "<em>stage</em> (validate|device_list|project|author|build|upload|monitor), <em>arduiner_action</em>, "
    "<em>status</em> (ok|error), <em>resumen</em> (serial present; puerto elegido; sketch_path; build "
    "returncode; upload verify; las líneas de count serial capturadas first&rarr;last) &mdash; una fila por "
    "cada llamada en orden de ejecución, status tal cual del bloque INI_SECTION_ARDUINER (NO lo reclasifiques). "
    "Celdas del cuerpo claras (background:#ffffff;color:#0f172a; o rayado #f1f5f9). "
    "\n\n"
    "Paso 10: cierra con un banner HTML que reutilice el estilo del Paso 0 "
    "'&#9989; SILICIO VERIFICADO' (build returncode=0 AND upload AND monitor todos ok &mdash; el contador "
    "se observó SUBIENDO por el stream serial en vivo), '&#9888;&#65039; SIN PLACA' (el Paso 1 no encontró "
    "un puerto serial conectado) o '&#10060; ERROR DE BUILD' (build returncode &ne; 0), y debajo una "
    "métrica de una línea 'sketch: <sketch_path> &middot; port: <COMx> &middot; build rc: <0> &middot; "
    "upload: <verified> &middot; serial count: <first>&rarr;<last>'. Termina con END-RESPONSE."
)


_NEW_PROMPTS = (
    (70, ARDUINO_GENESIS_DEMO),
    (71, ARDUINO_BLINKY_DEMO),
    (72, ARDUINO_HIL_OBSERVATORY_DEMO),
)


def add_arduiner_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_arduiner_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0110_add_chat_agent_arduiner_tool'),
    ]

    operations = [
        migrations.RunPython(add_arduiner_demo_prompts, remove_arduiner_demo_prompts),
    ]
