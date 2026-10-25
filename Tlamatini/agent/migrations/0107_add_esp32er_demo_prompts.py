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
Seed three Catalog-of-Prompts demos for **ESP32 firmware programming** through
the wrapped **chat_agent_esp32er** Multi-Turn tool (the PlatformIO Core / `pio`
CLI bridge). They run basic -> high complexity and mirror the STM32er demos
(0103), but built to ESP32er's grain: ESP32er drives the `pio` CLI DIRECTLY (no
MCP server), so "provisioning" means auto-installing PlatformIO Core, the project
is a plain PlatformIO project, and the firmware is Arduino-framework C++:

    66  ESP32 GENESIS         basic   bootstrap (ESP32er DOWNLOADS + installs +
                                      validates PlatformIO Core itself via the
                                      official get-platformio.py) -> validate (full
                                      environment preflight) -> create_project
                                      (esp32dev/arduino) -> write_source (blink
                                      main.cpp) -> build -> list_artifacts. NO
                                      board required (pure provision + build).
    67  ESP32 BLINKY          medium  validate -> create_project -> write_source
                                      (Arduino GPIO-2 blink + Serial prints) ->
                                      build -> list_artifacts -> build_and_upload.
                                      The upload is board-OPTIONAL: ESP32er's
                                      safety preflight refuses it cleanly with
                                      'No serial port detected' if no board is
                                      attached (expected + routable, not a crash).
    68  ESP32 HIL OBSERVATORY  hard   validate (REQUIRES a connected serial port)
                                      -> device_list -> create_project ->
                                      write_source (counter firmware that prints
                                      'BOOT tlamatini esp32 count=<n>' over Serial)
                                      -> build -> build_and_upload (REAL flash over
                                      the onboard USB-serial bootloader) -> monitor
                                      (read the RUNNING board's serial stream and
                                      watch the counter climb). Demo #3 UPLOADS TO
                                      AND OBSERVES THE HARDWARE end-to-end.

ESP32 vs STM32 hardware nuance baked into demo #68: an ESP32 flashes over its
*onboard USB-serial bootloader*, and that SAME USB-serial port carries the
firmware's `Serial.print` output — so unlike the STM32F4-Discovery (whose ST-LINK
VCP is NOT routed to the MCU USART, see 0104), the ESP32's serial monitor reads
the firmware's output natively with NO extra wiring. The serial `monitor` is
therefore the authoritative hardware-in-the-loop proof here.

All three drive ONLY chat_agent_esp32er and remind the user to tick ONLY the
**Multi-Turn** checkbox (chat_agent_esp32er is NOT behind the ACPX/Skill surface,
so ACPX is not required — same as the STM32er 0103, Kalier 0099, Unrealer 0100
demos).

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js) enumerates promptName
'prompt-1','prompt-2',... and BREAKS at the first missing slot, so the catalog
must stay a contiguous, gap-free 'prompt-1..N'. Slots 1-65 are occupied (0103
appended the STM32er demos at 63-65); these three APPEND at 66-68 with no shift of
any existing prompt. Reverse deletes 66-68. (MAX_PROMPTS=100.)
"""
from django.db import migrations


# Espressif red/amber banner palette (near-black -> ESP red -> warm amber ->
# cream), the same family as the ``.canvas-item.esp32er-agent`` gradient, with a
# text-shadow so the white label stays legible across the bright cream end.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#1A1A1A 0%,#E7352C 38%,#FF8A3D 70%,#FFE2C2 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


ESP32_GENESIS_DEMO = (
    "Tlamatini, ejecuta la demo **ESP32 GENESIS**, por favor &mdash; una muestra básica, de principio a fin, "
    "del *autoaprovisionamiento zero-config* y del *preflight de seguridad* de ESP32er, controlada "
    "por completo desde el chat a través del tool wrapper **chat_agent_esp32er**: desde una "
    "máquina limpia DESCARGA e instala PlatformIO Core ella misma, valida todo el entorno de "
    "build, arma un proyecto ESP32 de PlatformIO, ESCRIBE un pequeño sketch de blink y luego "
    "compila + ENLAZA a una imagen de firmware y lista el .elf/.bin &mdash; todo SIN una "
    "placa conectada (esta es una demo pura de aprovisionar + construir). "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques &mdash; confía en ellas y ve "
    "directo al Paso 1): (a) **el usuario instaló SÓLO Tlamatini** (más, para un "
    "upload real después, el driver USB-serial de la placa) &mdash; NO necesitas instalar ni "
    "configurar PlatformIO, ESP32er descarga PlatformIO Core automáticamente; (b) NO hace falta hardware "
    "ESP32 &mdash; no se flashea nada; (c) marca SÓLO la casilla **Multi-Turn** "
    "antes de enviar (ACPX NO se requiere &mdash; chat_agent_esp32er es el ÚNICO "
    "tool que puedes usar; no uses chat_agent_executer / chat_agent_pythonxer ni tools de ACPX). "
    "Cada paso es exactamente UNA llamada a chat_agent_esp32er con la forma \"Run ESP32er with "
    "action='<action>' and <k>='<v>' ...\". Después de cada llamada lee el JSON que devuelve (un "
    "bloque INI_SECTION_ESP32ER bajo el log_excerpt de la ejecución) y captura action / tool / ok / "
    "returncode / success / project_dir / stage, además del body. Si un paso devuelve ok=false / "
    "success=false, regístralo tal cual, NO canceles, continúa. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#9889; ESP32 GÉNESIS &#128295;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini ESP32er &mdash; aprovisionar &middot; validar &middot; escribir &middot; compilar</div></div>. "
    "\n\n"
    "Paso 1 (aprovisionamiento ZERO-CONFIG): llama a **chat_agent_esp32er** con el request "
    "\"Run ESP32er with action='bootstrap'\". Esto hace que ESP32er DESCARGUE el instalador oficial "
    "get-platformio.py e instale PlatformIO Core en un "
    "PLATFORMIO_CORE_DIR por usuario (con un fallback `pip install platformio`) &mdash; SIN configuración "
    "manual. Del body captura la acción de instalación (present / installer-script / "
    "pip-install), el core_dir y 'overall : OK'. Si overall es FAILED, lo más probable es que el host "
    "no tenga internet &mdash; salta al banner de cierre con un veredicto 'ERROR DE APROVISIONAMIENTO'. "
    "\n\n"
    "Paso 2 (preflight de seguridad): llama a **chat_agent_esp32er** con el request "
    "\"Run ESP32er with action='validate'\". Esto valida el entorno SIN "
    "construir: captura pio_resolvable y (como validate también sondea el hardware) el "
    "resumen del serial (present / esp_like). Que falte un puerto serial está BIEN aquí &mdash; esta "
    "demo nunca flashea. "
    "\n\n"
    "Paso 3 (scaffold): llama a **chat_agent_esp32er** con el request \"Run ESP32er with "
    "action='create_project' and project_dir='C:/Temp/esp32/tlamatini_genesis' and "
    "board='esp32dev' and framework='arduino'\". Esto corre `pio project init`; CAPTURA el "
    "**project_dir** &mdash; pásalo a cada paso posterior. "
    "\n\n"
    "Paso 4 (escribe el firmware &mdash; escribe src/main.cpp): llama a **chat_agent_esp32er** con el "
    "request \"Run ESP32er with action='write_source' and "
    "project_dir='C:/Temp/esp32/tlamatini_genesis' and rel_path='src/main.cpp' and "
    "content='''<CODE>'''\". Para <CODE> escribe un sketch de blink ESP32 de framework Arduino "
    "MÍNIMO y COMPILABLE: `#include <Arduino.h>`, un `#define LED_PIN 2`, un setup() que llame a "
    "pinMode(LED_PIN, OUTPUT) y Serial.begin(115200), y un loop() que conmute el LED con "
    "digitalWrite + delay(500). Pásalo como un literal content con comillas triples (content='''...''') "
    "para que los newlines y las llaves sobrevivan al parser de asignaciones. "
    "\n\n"
    "Paso 5 (compila + ENLAZA &rarr; firmware): llama a **chat_agent_esp32er** con el request "
    "\"Run ESP32er with action='build' and project_dir='C:/Temp/esp32/tlamatini_genesis'\". "
    "Confirma returncode=0 y que el stdout muestre a la plataforma espressif32 compilando y "
    "enlazando (la línea 'Linking .pio/build/esp32dev/firmware.elf' es la prueba de la etapa de "
    "enlace). NOTA: el PRIMER build descarga la plataforma espressif32 + el toolchain (cientos de "
    "MB), así que puede tardar unos minutos &mdash; eso es normal. "
    "\n\n"
    "Paso 6 (artefactos): llama a **chat_agent_esp32er** con el request \"Run ESP32er with "
    "action='list_artifacts' and project_dir='C:/Temp/esp32/tlamatini_genesis'\". Captura los "
    "paths firmware.elf / firmware.bin del body. "
    "\n\n"
    "Paso 7: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>ESP32 Genesis &mdash; Reporte de aprovisionamiento y build</strong>' y con las columnas "
    "<em>paso</em>, <em>stage</em> (bootstrap|validate|project|author|build), <em>esp32_action</em>, "
    "<em>status</em> (ok|error), <em>resumen</em> (core_dir para bootstrap; pio_resolvable para "
    "validate; project_dir para create; src/main.cpp escrito para author; returncode para build; los "
    "paths de firmware para list_artifacts) &mdash; una fila por cada llamada en orden de ejecución, status tal cual "
    "del bloque INI_SECTION_ESP32ER (NO lo reclasifiques). Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a; o rayado #f1f5f9), tono verde ok, rojo suave error. "
    "\n\n"
    "Paso 8: cierra con un banner HTML que reutilice el estilo del Paso 0, en letras grandes, "
    "'&#9989; PLATFORMIO APROVISIONADO &amp; FIRMWARE CONSTRUIDO' (bootstrap OK, validate resolvió pio, "
    "build returncode=0 y artefactos listados), '&#9888;&#65039; GÉNESIS PARCIAL' (algunos pasos ok, "
    "algunos error) o '&#10060; ERROR DE APROVISIONAMIENTO' (overall de bootstrap FAILED), y debajo una "
    "métrica de una línea 'pio: <install action> &middot; core_dir: <...> &middot; project: <project_dir> "
    "&middot; build rc: <0> &middot; artefactos: firmware.elf/.bin'. Termina con END-RESPONSE."
)


ESP32_BLINKY_DEMO = (
    "Tlamatini, ejecuta la demo **ESP32 BLINKY**, por favor &mdash; una versión de complejidad media del "
    "clásico 'hello world' embebido, controlada por completo desde el chat a través del tool wrapper "
    "**chat_agent_esp32er**: valida el entorno en preflight, arma un proyecto de PlatformIO, "
    "ESCRIBE un sketch de blink en GPIO-2 de Arduino que también imprime por Serial, lo compila + "
    "enlaza, lista los artefactos y luego intenta subirlo a una placa ESP32 para que el LED on-board "
    "parpadee. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques; ve directo al Paso 1): (a) el usuario "
    "instaló SÓLO Tlamatini &mdash; ESP32er auto-descarga/instala PlatformIO Core ella misma en el "
    "primer uso, así que NUNCA configuras paths de tools; (b) el build NO necesita placa; el paso de UPLOAD "
    "necesita una placa ESP32 por USB (ESP32 flashea por su bootloader USB-serial on-board &mdash; SIN "
    "probe JTAG externo) &mdash; PERO el preflight de seguridad de ESP32er RECHAZARÁ el upload con 'No "
    "serial port detected' si no hay placa conectada, lo cual es ESPERADO y enrutable, NO un crash: "
    "regístralo tal cual y CONTINÚA; (c) marca SÓLO la casilla **Multi-Turn** (ACPX NO se "
    "requiere). Usa SÓLO chat_agent_esp32er, UNA llamada por paso con la forma \"Run ESP32er with "
    "action='<action>' and <k>='<v>' ...\". Lee cada JSON que devuelve (bloque INI_SECTION_ESP32ER bajo "
    "log_excerpt), captura action/tool/ok/returncode/success/project_dir/port/stage, y con "
    "ok=false regístralo tal cual y CONTINÚA. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128161; ESP32 BLINKY &#128161;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini ESP32er &mdash; validar &middot; escribir &middot; build &middot; upload</div></div>. "
    "\n\n"
    "Paso 1 (preflight de seguridad): \"Run ESP32er with action='validate'\" &mdash; captura "
    "pio_resolvable y el resumen del serial (present / esp_like) como la base 'before' (ESP32er "
    "auto-aprovisiona PlatformIO Core como parte de esto si hace falta). "
    "\n\n"
    "Paso 2 (scaffold): \"Run ESP32er with action='create_project' and "
    "project_dir='C:/Temp/esp32/tlamatini_blinky' and board='esp32dev' and framework='arduino'\". "
    "CAPTURA el **project_dir**. "
    "\n\n"
    "Paso 3 (escribe el firmware &mdash; escribe src/main.cpp): \"Run ESP32er with "
    "action='write_source' and project_dir='C:/Temp/esp32/tlamatini_blinky' and "
    "rel_path='src/main.cpp' and content='''<CODE>'''\". Para <CODE> escribe un programa MÍNIMO y COMPILABLE "
    "de framework Arduino para ESP32: `#include <Arduino.h>`, `#define LED_PIN 2` (el LED on-board "
    "en la mayoría de placas ESP32 DevKitC), setup() con pinMode(LED_PIN, OUTPUT) + Serial.begin(115200) + "
    "un banner 'ESP32 BLINKY starting', y un loop() que ponga el LED en HIGH (Serial.println "
    "\"LED ON\"), delay(500), LED en LOW (Serial.println \"LED OFF\"), delay(500). Pásalo como un literal "
    "content con comillas triples (content='''...''') para que los newlines y las llaves sobrevivan al parser. "
    "\n\n"
    "Paso 4 (compila + ENLAZA): \"Run ESP32er with action='build' and "
    "project_dir='C:/Temp/esp32/tlamatini_blinky'\". Confirma returncode=0 y el enlace de "
    "firmware.elf/firmware.bin. (El primer build jala el toolchain espressif32 &mdash; puede tardar unos "
    "minutos; eso es normal.) Si returncode es distinto de cero, captura el diagnóstico del compilador del "
    "stderr &mdash; evidencia enrutable; puedes detenerte después del reporte con un veredicto 'ERROR DE BUILD'. "
    "\n\n"
    "Paso 5 (artefactos): \"Run ESP32er with action='list_artifacts' and "
    "project_dir='C:/Temp/esp32/tlamatini_blinky'\". Captura el path de firmware.bin. "
    "\n\n"
    "Paso 6 (upload &mdash; flashea por USB-serial): \"Run ESP32er with action='build_and_upload' and "
    "project_dir='C:/Temp/esp32/tlamatini_blinky'\". Si hay una placa conectada, el body muestra a esptool "
    "escribiendo + verificando el firmware por el bootloader USB-serial; si no, el preflight de ESP32er "
    "devuelve ok=false con 'No serial port detected' &mdash; regístralo tal cual y CONTINÚA "
    "(placa ausente es el soft-fail esperado de esta demo). "
    "\n\n"
    "Paso 7: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>ESP32 Blinky &mdash; Reporte de ejecución</strong>' y con las columnas <em>paso</em>, <em>stage</em> "
    "(validate|project|author|build|upload), <em>esp32_action</em>, <em>status</em> (ok|error), "
    "<em>resumen</em> (pio resolved; project_dir; build returncode; path de firmware.bin; upload "
    "verify o 'preflight refused: no board') &mdash; una fila por cada llamada en orden de ejecución, status "
    "tal cual del bloque INI_SECTION_ESP32ER. Celdas del cuerpo claras (background:#ffffff;color:#0f172a; "
    "o rayado #f1f5f9); tono verde ok, rojo suave error. "
    "\n\n"
    "Paso 8: cierra con un banner HTML que reutilice el estilo del Paso 0 "
    "'&#9989; BLINKY EN VIVO' (build returncode=0 AND upload verified), "
    "'&#9888;&#65039; CONSTRUIDO, SIN PLACA' (build ok pero el preflight rechazó el upload / sin placa), "
    "o '&#10060; ERROR DE BUILD' (build returncode &ne; 0), y debajo una métrica de una línea "
    "'project: <project_dir> &middot; build rc: <0> &middot; upload: <verified|no-board> &middot; "
    "led: GPIO&nbsp;2 @ 500&nbsp;ms'. Termina con END-RESPONSE."
)


ESP32_HIL_OBSERVATORY_DEMO = (
    "Tlamatini, ejecuta la demo **ESP32 HIL OBSERVATORY**, por favor &mdash; una muestra avanzada "
    "**hardware-in-the-loop** que SUBE A UNA PLACA REAL y la OBSERVA de principio a fin, "
    "controlada por completo desde el chat a través del tool wrapper **chat_agent_esp32er**: valida en preflight"
    "que haya un puerto serial conectado, arma y ESCRIBE un firmware que incrementa un "
    "contador global y lo transmite por Serial, lo construye + SUBE al ESP32 y luego PRUEBA que "
    "está corriendo en silicio real leyendo el stream serial en vivo de la placa EN EJECUCIÓN y "
    "viendo subir el contador. "
    "Nota de hardware del ESP32 (no la omitas): un ESP32 flashea por su **bootloader USB-serial "
    "on-board**, y ESE MISMO puerto USB-serial lleva el output `Serial.print` del firmware "
    "&mdash; así que, A DIFERENCIA de la STM32F4-Discovery (cuyo VCP del ST-LINK no se enruta al USART del MCU), "
    "el serial monitor del ESP32 lee el output del firmware de forma nativa SIN cableado extra. El "
    "serial monitor es, por lo tanto, la prueba HIL autoritativa aquí. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques; ve directo al Paso 1): (a) el usuario "
    "instaló SÓLO Tlamatini + el driver USB-serial de la placa (ESP32er auto-aprovisiona PlatformIO "
    "Core ella misma); (b) **hay una placa ESP32 CONECTADA** por USB y se enumera como un puerto serial "
    "&mdash; esta demo REQUIERE hardware; (c) marca SÓLO la casilla **Multi-Turn** (ACPX NO se "
    "requiere). Usa SÓLO chat_agent_esp32er, UNA llamada por paso con la forma \"Run ESP32er with "
    "action='<action>' and <k>='<v>' ...\". Lee cada JSON que devuelve (bloque INI_SECTION_ESP32ER bajo "
    "log_excerpt), captura action/tool/ok/returncode/success/project_dir/port/stage, y con "
    "ok=false regístralo tal cual y CONTINÚA. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128300; ESP32 HIL OBSERVATORY &#9889;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini ESP32er &mdash; validate &middot; upload &middot; observar serial en vivo</div></div>. "
    "\n\n"
    "Paso 1 (preflight de seguridad &mdash; CONFIRMA LA PLACA): \"Run ESP32er with action='validate'\". "
    "Esto auto-aprovisiona PlatformIO Core si hace falta y valida el entorno INCLUIDO el "
    "puerto serial (validate sondea un adaptador conectado). Del reporte captura pio_resolvable "
    "y el resumen del serial (present / esp_like / ports). **Si no hay puerto serial presente, DETENTE**: "
    "salta al banner de cierre con un veredicto 'SIN PLACA' y dile al usuario que conecte el ESP32 "
    "por USB (esto es una demo de hardware). Sólo pasa al Paso 2 cuando haya un puerto serial presente. "
    "\n\n"
    "Paso 2 (enumera puertos): \"Run ESP32er with action='device_list'\". Del JSON captura el "
    "puerto(s) serial conectado(s) (p. ej. COM5 en Windows) y elige el puerto del ESP32 &mdash; pásalo como "
    "**port** a los pasos de upload/monitor. "
    "\n\n"
    "Paso 3 (scaffold): \"Run ESP32er with action='create_project' and "
    "project_dir='C:/Temp/esp32/tlamatini_hil' and board='esp32dev' and framework='arduino'\". "
    "CAPTURA el **project_dir**. "
    "\n\n"
    "Paso 4 (escribe el firmware &mdash; escribe src/main.cpp): \"Run ESP32er with "
    "action='write_source' and project_dir='C:/Temp/esp32/tlamatini_hil' and "
    "rel_path='src/main.cpp' and content='''<CODE>'''\". Para <CODE> escribe un programa MÍNIMO y COMPILABLE "
    "de framework Arduino para ESP32 que declare, a nivel de archivo, un `uint32_t g_count = 0;`, en setup() "
    "llame a Serial.begin(115200) y pinMode(2, OUTPUT), y en loop() incremente g_count, conmute "
    "el LED de GPIO-2, imprima una sola línea de status terminada en newline con la forma EXACTA "
    "'BOOT tlamatini esp32 count=<n>' con Serial.println, y delay(500). Pásalo como un literal "
    "content con comillas triples (content='''...''') para que los newlines y las llaves sobrevivan al parser. "
    "\n\n"
    "Paso 5 (compila + ENLAZA): \"Run ESP32er with action='build' and "
    "project_dir='C:/Temp/esp32/tlamatini_hil'\". Exige returncode=0. (El primer build jala el "
    "toolchain espressif32 &mdash; puede tardar unos minutos.) Si el build falla, captura el "
    "diagnóstico y puedes detenerte después del reporte con 'ERROR DE BUILD'. "
    "\n\n"
    "Paso 6 (UPLOAD &mdash; flash REAL por USB-serial): \"Run ESP32er with "
    "action='build_and_upload' and project_dir='C:/Temp/esp32/tlamatini_hil' and port='<the port "
    "from Step 2>'\". El preflight ya confirmó la placa en el Paso 1; el body debería mostrar "
    "a esptool 'Writing at 0x...' / 'Hash of data verified' por el bootloader USB-serial. Captura "
    "el resultado del verify &mdash; este es el UPLOAD real del programa a la placa ESP32. "
    "\n\n"
    "Paso 7 (prueba HIL &mdash; observa el stream serial en vivo): \"Run ESP32er with action='monitor' "
    "and project_dir='C:/Temp/esp32/tlamatini_hil' and port='<the port from Step 2>' and baud='115200' "
    "and monitor_seconds='6'\". Esto abre un `pio device monitor` acotado, drena el output serial de la "
    "placa EN EJECUCIÓN por 6 segundos y luego se detiene. Captura la PRIMERA y la ÚLTIMA línea 'BOOT tlamatini esp32 "
    "count=<n>' y confirma que el count va AUMENTANDO &mdash; prueba directa, sobre silicio, de que el loop() "
    "se está ejecutando en hardware real (no sólo que el .bin se flasheó). "
    "\n\n"
    "Paso 8: muestra un MARCADOR DE STATUS &mdash; una fila de chips HTML con la forma "
    "<span style='display:inline-block;padding:8px 16px;margin:3px;border-radius:10px;"
    "font-weight:800;background:CHIP_BG;color:#ffffff;'>LABEL</span>: un chip 'validate: <ok|err>', "
    "un chip 'port: <COMx>', un chip 'build: <ok|err>', un chip 'upload: <ok|err>', un "
    "chip 'monitor: <ok|err>' (CHIP_BG #16a34a cuando es ok, si no #dc2626), y un "
    "chip 'count: <first>&rarr;<last>' (CHIP_BG #E7352C). "
    "\n\n"
    "Paso 9: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>ESP32 HIL Observatory &mdash; Reporte de ejecución</strong>' y con las columnas <em>paso</em>, "
    "<em>stage</em> (validate|device_list|project|author|build|upload|monitor), <em>esp32_action</em>, "
    "<em>status</em> (ok|error), <em>resumen</em> (serial present; puerto elegido; project_dir; build "
    "returncode; upload verify; las líneas de count serial capturadas first&rarr;last) &mdash; una fila por "
    "cada llamada en orden de ejecución, status tal cual del bloque INI_SECTION_ESP32ER (NO lo reclasifiques). "
    "Celdas del cuerpo claras (background:#ffffff;color:#0f172a; o rayado #f1f5f9). "
    "\n\n"
    "Paso 10: cierra con un banner HTML que reutilice el estilo del Paso 0 "
    "'&#9989; SILICIO VERIFICADO' (build returncode=0 AND upload AND monitor todos ok &mdash; el contador "
    "se observó SUBIENDO por el stream serial en vivo), '&#9888;&#65039; SIN PLACA' (el Paso 1 no encontró "
    "un puerto serial conectado) o '&#10060; ERROR DE BUILD' (build returncode &ne; 0), y debajo una "
    "métrica de una línea 'project: <project_dir> &middot; port: <COMx> &middot; build rc: <0> &middot; "
    "upload: <verified> &middot; serial count: <first>&rarr;<last>'. Termina con END-RESPONSE."
)


_NEW_PROMPTS = (
    (66, ESP32_GENESIS_DEMO),
    (67, ESP32_BLINKY_DEMO),
    (68, ESP32_HIL_OBSERVATORY_DEMO),
)


def add_esp32er_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_esp32er_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0106_add_chat_agent_esp32er_tool'),
    ]

    operations = [
        migrations.RunPython(add_esp32er_demo_prompts, remove_esp32er_demo_prompts),
    ]
