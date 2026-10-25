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
Seed three Catalog-of-Prompts demos for **STM32F firmware programming** through
the wrapped **chat_agent_stm32er** Multi-Turn tool (the STM32 Template Project
MCP bridge). They run basic -> high complexity and showcase STM32er's full,
zero-config, fail-safe behavior:

    63  STM32 GENESIS         basic   bootstrap (STM32er DOWNLOADS + installs +
                                      validates the MCP itself) -> validate (full
                                      environment preflight) -> create_project ->
                                      build -> list_artifacts. NO board required.
    64  STM32 BLINKY          medium  validate -> create_project -> write_source
                                      (HAL GPIO blink main.c) -> build ->
                                      list_artifacts -> build_and_flash. The flash
                                      is board-OPTIONAL: the safety preflight
                                      refuses it cleanly if no ST-LINK is present.
    65  STM32 HIL OBSERVATORY  hard   validate (REQUIRES a connected board) ->
                                      create_project -> write_source (counter+UART
                                      firmware) -> build -> build_and_flash (REAL
                                      upload+verify) -> serial_session (VCP boot
                                      banner) -> live_monitor (sample g_blink_count
                                      from the RUNNING MCU over SWD) -> reset.
                                      Demo #3 USES THE HARDWARE end-to-end.

What changed vs. the first cut of these prompts: they now lead with STM32er's
**zero-config self-provisioning** (action='bootstrap' downloads the MCP from its
git repo and pip-installs/validates it — the user installs ONLY STM32CubeIDE) and
its **safety preflight** (action='validate' + the automatic pre-build/pre-flash
gate that validates the arm-none-eabi-gcc toolchain / STM32CubeIDE / programmer /
ST-LINK driver + probe / target device family, and REFUSES rather than producing
or flashing mis-targeted firmware). Compile-only actions need NO board; hardware
actions (flash/serial/SWD) require a positively-confirmed ST-LINK — so demo 63/64
run boardless and demo 65 drives a real STM32F407G-DISC1.

All three drive ONLY chat_agent_stm32er and remind the user to tick ONLY the
**Multi-Turn** checkbox (chat_agent_stm32er is NOT behind the ACPX/Skill surface,
so ACPX is not required — same as the Kalier 0099 and Unrealer 0100 demos).

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js) enumerates promptName
'prompt-1','prompt-2',... and BREAKS at the first missing slot, so the catalog
must stay a contiguous, gap-free 'prompt-1..N'. Slots 1-62 are occupied (0100
appended the Unreal demos at 60-62); these three APPEND at 63-65 with no shift of
any existing prompt. Reverse deletes 63-65. (MAX_PROMPTS=100.)
"""
from django.db import migrations


# ST-blue banner palette (deep navy -> ST royal blue -> cyan), the same family as
# the ``.canvas-item.stm32er-agent`` gradient, with a text-shadow so the white
# label stays legible across the bright cyan end.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#061029 0%,#0B3A8F 40%,#1E63FF 72%,#22D3EE 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.45);'>"
)


STM32_GENESIS_DEMO = (
    "Tlamatini, ejecuta la demo **STM32 GENESIS**, por favor &mdash; una muestra básica, de principio a fin, "
    "del *autoaprovisionamiento zero-config* y del *preflight de seguridad* de STM32er, "
    "controlada por completo desde el chat a través del tool wrapper **chat_agent_stm32er**: desde una "
    "máquina limpia DESCARGA e instala el STM32 Template Project MCP ella misma, "
    "valida todo el entorno de build, arma un proyecto STM32F4 y luego compila "
    "+ ENLAZA a un .elf y lista el .elf/.hex/.bin &mdash; todo SIN una placa "
    "conectada (esta es una demo pura de aprovisionar + construir). "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques &mdash; confía en ellas y ve "
    "directo al Paso 1): (a) **el usuario instaló SÓLO STM32CubeIDE** (trae el "
    "toolchain GNU Arm + el driver ST-LINK) &mdash; NO necesitas instalar ni configurar "
    "el servidor MCP, STM32er lo descarga automáticamente; (b) NO hace falta hardware STM32 "
    "&mdash; no se flashea nada; (c) marca SÓLO la casilla **Multi-Turn** antes de enviar "
    "(NO se necesita ACPX &mdash; chat_agent_stm32er es el ÚNICO tool que puedes usar; no "
    "uses chat_agent_executer / chat_agent_pythonxer ni tools de ACPX). "
    "Cada paso es exactamente UNA llamada a chat_agent_stm32er con la forma \"Run STM32er with "
    "action='<action>' and <k>='<v>' ...\". Después de cada llamada lee el JSON que devuelve (un "
    "bloque INI_SECTION_STM32ER bajo el log_excerpt de la ejecución) y captura action / ok / "
    "returncode / success / project_dir / stage, además del body. Si un paso devuelve "
    "ok=false / success=false, regístralo tal cual, NO canceles, continúa. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#9881;&#65039; STM32 GÉNESIS &#128295;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini STM32er &mdash; aprovisionar &middot; validar &middot; compilar &middot; enlazar</div></div>. "
    "\n\n"
    "Paso 1 (aprovisionamiento ZERO-CONFIG): llama a **chat_agent_stm32er** con el request "
    "\"Run STM32er with action='bootstrap'\". Esto hace que STM32er DESCARGUE el STM32 "
    "Template Project MCP de su repo git a una caché por usuario, haga pip-install de sus deps "
    "(mcp, pyserial) si faltan, y valide &mdash; SIN configuración manual del servidor. Del "
    "body captura la acción de descarga (cloned / present), las deps (already-installed / "
    "pip-install), el install_dir y 'overall : OK'. Si overall es FAILED, lo más probable es que el host "
    "no tenga internet / git &mdash; salta al banner de cierre con un veredicto 'ERROR DE "
    "APROVISIONAMIENTO'. "
    "\n\n"
    "Paso 2 (preflight de seguridad): llama a **chat_agent_stm32er** con el request "
    "\"Run STM32er with action='validate'\". Esto valida el entorno SIN "
    "construir: captura cada comprobación &mdash; arm_none_eabi_gcc, stm32cubeide, make, cmake, "
    "programmer_cli, device_family_supported (y el path descubierto de arm-none-eabi-gcc). "
    "Si arm_none_eabi_gcc es False, STM32CubeIDE no está instalado/detectable &mdash; "
    "anótalo y continúa al reporte. "
    "\n\n"
    "Paso 3 (scaffold): llama a **chat_agent_stm32er** con el request \"Run STM32er with "
    "action='create_project' and name='tlamatini_genesis' and dest_parent='C:/Temp/stm32' "
    "and overwrite='true'\". CAPTURA el **project_dir** &mdash; pásalo a cada paso posterior. "
    "\n\n"
    "Paso 4 (compila + ENLAZA &rarr; .elf): llama a **chat_agent_stm32er** con el request "
    "\"Run STM32er with action='build' and project_dir='<the project_dir from Step 3>' and "
    "system='make' and clean_first='true'\". Confirma returncode=0 y que el stdout muestre a "
    "arm-none-eabi-gcc compilando objetos y enlazando el firmware (la línea del linker script -T ...FLASH.ld "
    "es la prueba de la etapa de enlace). "
    "\n\n"
    "Paso 5 (artefactos): llama a **chat_agent_stm32er** con el request \"Run STM32er with "
    "action='list_artifacts' and project_dir='<project_dir>'\". Captura los paths .elf / .hex / "
    ".bin del mapa de artefactos. "
    "\n\n"
    "Paso 6: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>STM32 Genesis &mdash; Reporte de aprovisionamiento y build</strong>' y con las columnas "
    "<em>paso</em>, <em>stage</em> (bootstrap|validate|project|build), <em>stm32_action</em>, "
    "<em>status</em> (ok|error), <em>resumen</em> (install_dir para bootstrap; el path de gcc "
    "para validate; project_dir para create; returncode para build; los paths de artefactos para "
    "list_artifacts) &mdash; una fila por cada llamada en orden de ejecución, status tal cual del "
    "bloque INI_SECTION_STM32ER (NO lo reclasifiques). Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a; o rayado #f1f5f9), tono verde ok, rojo suave error. "
    "\n\n"
    "Paso 7: cierra con un banner HTML que reutilice el estilo del Paso 0, en letras grandes, "
    "'&#9989; TOOLCHAIN APROVISIONADO &amp; FIRMWARE CONSTRUIDO' (bootstrap OK, validate encontró el "
    "compilador, build returncode=0 y artefactos listados), '&#9888;&#65039; GÉNESIS PARCIAL' "
    "(algunos pasos ok, algunos error) o '&#10060; ERROR DE APROVISIONAMIENTO' (overall de bootstrap FAILED), "
    "y debajo una métrica de una línea 'mcp: <download action> &middot; gcc: <...arm-none-eabi-gcc> "
    "&middot; project: <project_dir> &middot; build rc: <0> &middot; artefactos: .elf/.hex/.bin'. "
    "Termina con END-RESPONSE."
)


STM32_BLINKY_DEMO = (
    "Tlamatini, ejecuta la demo **STM32 BLINKY**, por favor &mdash; una versión de complejidad media del "
    "clásico 'hello world' embebido, controlada por completo desde el chat a través del tool wrapper "
    "**chat_agent_stm32er**: valida el entorno en preflight, arma un proyecto, "
    "ESCRIBE un main.c de blink con HAL GPIO, lo compila + enlaza, lista los artefactos y luego intenta "
    "subirlo a una placa STM32F4 por ST-LINK para que el LED on-board parpadee. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques; ve directo al Paso 1): (a) el usuario "
    "instaló SÓLO STM32CubeIDE &mdash; STM32er auto-descarga/instala el MCP ella misma en el primer "
    "uso, así que NUNCA configuras paths del servidor; (b) el build NO necesita placa; el paso de FLASH "
    "necesita una placa STM32F4 (p. ej. una STM32F407G-DISC1) por ST-LINK &mdash; PERO el preflight de seguridad de STM32er "
    "RECHAZARÁ el flash con 'No ST-LINK probe detected' si no hay placa conectada, "
    "lo cual es ESPERADO y enrutable, NO un crash: regístralo tal cual y CONTINÚA; (c) marca SÓLO "
    "la casilla **Multi-Turn** (NO se necesita ACPX). Usa SÓLO chat_agent_stm32er, UNA llamada "
    "por paso con la forma \"Run STM32er with action='<action>' and <k>='<v>' ...\". Lee cada JSON "
    "que devuelve (bloque INI_SECTION_STM32ER bajo log_excerpt), captura "
    "action/ok/returncode/success/project_dir/stage, y con ok=false regístralo tal cual y CONTINÚA. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128161; STM32 BLINKY &#128161;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini STM32er &mdash; validar &middot; escribir &middot; build &middot; flash</div></div>. "
    "\n\n"
    "Paso 1 (preflight de seguridad): \"Run STM32er with action='validate'\" &mdash; captura "
    "arm_none_eabi_gcc / make / programmer_cli / device_family_supported y el path de gcc descubierto "
    "como la base 'before' (STM32er auto-aprovisiona el MCP como parte de esto si hace falta). "
    "\n\n"
    "Paso 2 (scaffold): \"Run STM32er with action='create_project' and name='tlamatini_blinky' "
    "and dest_parent='C:/Temp/stm32' and overwrite='true'\". CAPTURA el **project_dir**. "
    "\n\n"
    "Paso 3 (escribe el firmware &mdash; escribe main.c): \"Run STM32er with action='write_source' "
    "and project_dir='<project_dir>' and rel_path='Core/Src/main.c' and content='''<CODE>'''\". "
    "Para <CODE> escribe un main.c de blink STM32F4 HAL MÍNIMO y COMPILABLE que incluya el header "
    "de HAL, llame a HAL_Init() + el SystemClock_Config() del proyecto, habilite el clock del puerto GPIO, "
    "configure el/los pin(es) del LED on-board (p. ej. PD12&ndash;PD15 en una F407 Discovery) como salidas "
    "push-pull, y en el loop while(1) los conmute y llame a HAL_Delay(500). Pásalo como un literal "
    "content con comillas triples (content='''...''') para que los newlines y las llaves sobrevivan al "
    "parser de asignaciones. Mantenlo autocontenido y construible contra la HAL del scaffold. "
    "\n\n"
    "Paso 4 (compila + ENLAZA): \"Run STM32er with action='build' and project_dir='<project_dir>' "
    "and system='make' and clean_first='true'\". Confirma returncode=0 y el enlace de firmware.elf. "
    "Si returncode es distinto de cero, captura el diagnóstico del compilador del stderr &mdash; evidencia "
    "enrutable; puedes detenerte después del reporte con un veredicto 'ERROR DE BUILD'. "
    "\n\n"
    "Paso 5 (artefactos): \"Run STM32er with action='list_artifacts' and project_dir='<project_dir>'\". "
    "Captura los paths .hex y .bin. "
    "\n\n"
    "Paso 6 (flash &mdash; upload por ST-LINK): \"Run STM32er with action='build_and_flash' and "
    "project_dir='<project_dir>'\". Si hay una placa conectada, el body muestra al programmer "
    "verificando la descarga; si no, el preflight de STM32er devuelve ok=false con 'No ST-LINK probe "
    "detected (... compile-only actions do NOT need a board)' &mdash; regístralo tal cual y "
    "CONTINÚA (placa ausente es el soft-fail esperado de esta demo). "
    "\n\n"
    "Paso 7: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>STM32 Blinky &mdash; Reporte de ejecución</strong>' y con las columnas <em>paso</em>, <em>stage</em> "
    "(validate|project|build|flash), <em>stm32_action</em>, <em>status</em> (ok|error), "
    "<em>resumen</em> (gcc encontrado; project_dir; build returncode; path del hex; flash verify o "
    "'preflight refused: no board') &mdash; una fila por cada llamada en orden de ejecución, status tal cual "
    "del bloque INI_SECTION_STM32ER. Celdas del cuerpo claras (background:#ffffff;color:#0f172a; o "
    "rayado #f1f5f9); tono verde ok, rojo suave error. "
    "\n\n"
    "Paso 8: cierra con un banner HTML que reutilice el estilo del Paso 0 "
    "'&#9989; BLINKY EN VIVO' (build returncode=0 AND flash verified), "
    "'&#9888;&#65039; CONSTRUIDO, SIN PLACA' (build ok pero el preflight rechazó el flash / sin placa), "
    "o '&#10060; ERROR DE BUILD' (build returncode &ne; 0), y debajo una métrica de una línea "
    "'project: <project_dir> &middot; build rc: <0> &middot; flash: <verified|no-board> &middot; "
    "led: PD12&ndash;PD15 @ 500&nbsp;ms'. Termina con END-RESPONSE."
)


STM32_HIL_OBSERVATORY_DEMO = (
    "Tlamatini, ejecuta la demo **STM32 HIL OBSERVATORY**, por favor &mdash; una muestra avanzada "
    "**hardware-in-the-loop** que USA UNA PLACA REAL de principio a fin, controlada por completo desde el "
    "chat a través del tool wrapper **chat_agent_stm32er**: valida en preflight que haya un ST-LINK "
    "conectado, arma y ESCRIBE un firmware que incrementa un contador global y lo transmite "
    "por UART, lo construye + flashea en la placa y luego PRUEBA que está corriendo en silicio real de dos "
    "formas independientes &mdash; lee el banner de arranque por el Virtual COM Port del ST-LINK (serial), "
    "AND muestrea una variable global en vivo de la RAM del MCU EN EJECUCIÓN por SWD (memoria en vivo) &mdash; "
    "antes de hacer un reset por hardware de la placa. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques; ve directo al Paso 1): (a) el usuario "
    "instaló SÓLO STM32CubeIDE (STM32er auto-aprovisiona el MCP por su cuenta); (b) **hay una placa STM32F407 "
    "(p. ej. STM32F407G-DISC1) CONECTADA** por ST-LINK con su Virtual COM Port habilitado "
    "&mdash; esta demo REQUIERE hardware; (c) marca SÓLO la casilla **Multi-Turn** (ACPX NO se "
    "necesita). Usa SÓLO chat_agent_stm32er, UNA llamada por paso con la forma \"Run STM32er with "
    "action='<action>' and <k>='<v>' ...\". Lee cada JSON que devuelve (bloque INI_SECTION_STM32ER bajo "
    "log_excerpt), captura action/ok/returncode/success/project_dir/session_id/stage, y con "
    "ok=false regístralo tal cual y CONTINÚA. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128300; STM32 HIL OBSERVATORY &#9889;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini STM32er &mdash; validate &middot; flash &middot; VCP serial &middot; memoria SWD en vivo</div></div>. "
    "\n\n"
    "Paso 1 (preflight de seguridad &mdash; CONFIRMA LA PLACA): \"Run STM32er with action='validate' and "
    "device='STM32F407VG'\". Esto auto-aprovisiona el MCP si hace falta y valida el entorno "
    "INCLUIDO el ST-LINK. Del reporte captura stlink_connected y device_family_supported. "
    "**Si stlink_connected es False, DETENTE**: salta al banner de cierre con un veredicto 'SIN PLACA' "
    "y dile al usuario que conecte la STM32F407G-DISC1 (esto es una demo de hardware). Sólo pasa al "
    "Paso 2 cuando stlink_connected sea True. "
    "\n\n"
    "Paso 2 (scaffold): \"Run STM32er with action='create_project' and name='tlamatini_hil' and "
    "dest_parent='C:/Temp/stm32' and overwrite='true'\". CAPTURA el **project_dir**. "
    "\n\n"
    "Paso 3 (escribe el firmware &mdash; escribe main.c): \"Run STM32er with action='write_source' "
    "and project_dir='<project_dir>' and rel_path='Core/Src/main.c' and content='''<CODE>'''\". "
    "Para <CODE> escribe un programa STM32F4 HAL MÍNIMO y COMPILABLE que declare, a nivel de archivo, un "
    "`volatile uint32_t g_blink_count = 0;`, inicialice HAL + el system clock + el GPIO del LED on-board "
    "+ USART2 (el VCP del ST-LINK, 115200 8N1), y en el loop while(1): incremente "
    "g_blink_count, conmute el LED, transmita una sola línea de status terminada en newline con la forma "
    "'BOOT tlamatini hil count=<n>' por USART2 con HAL_UART_Transmit, y HAL_Delay(500). Pásalo "
    "como un literal content con comillas triples (content='''...''') para que los newlines y las llaves sobrevivan al "
    "parser. Mantenlo autocontenido y construible contra la HAL del scaffold. "
    "\n\n"
    "Paso 4 (compila + ENLAZA): \"Run STM32er with action='build' and project_dir='<project_dir>' and "
    "system='make' and clean_first='true'\". Exige returncode=0 (el .elf lleva el "
    "símbolo g_blink_count que lee el paso de memoria en vivo). Si el build falla, captura el diagnóstico "
    "y puedes detenerte después del reporte con 'ERROR DE BUILD'. "
    "\n\n"
    "Paso 5 (flash &mdash; upload REAL por ST-LINK): \"Run STM32er with action='build_and_flash' "
    "and project_dir='<project_dir>'\". El preflight ya confirmó la placa en el Paso 1; el "
    "body debería mostrar al programmer reportando 'File download complete' / 'Verifying...'. Captura "
    "el resultado del verify. "
    "\n\n"
    "Paso 6 (HIL #1 &mdash; banner de arranque por VCP serial): \"Run STM32er with action='serial_session' and "
    "port='COM7' and baud='115200' and serial_timeout='3'\" (sustituye el puerto VCP real del ST-LINK "
    "&mdash; si no estás segura PUEDES primero llamar action='serial_list_ports' y elegir el puerto marcado como "
    "VCP de ST-LINK). Sin `data` puesto, serial_session conecta, LEE el output de la placa, luego "
    "desconecta &mdash; captura la línea 'BOOT tlamatini hil count=<n>' como prueba de que el firmware está "
    "alive. "
    "\n\n"
    "Paso 7 (HIL #2 &mdash; memoria SWD en vivo): \"Run STM32er with action='live_monitor' and "
    "variables='[\"g_blink_count\"]' and project_dir='<project_dir>' and monitor_seconds='4' and "
    "last_n='8'\". Esto inicia un stream de OpenOCD de la RAM del MCU EN EJECUCIÓN, muestrea el global por 4 "
    "segundos, devuelve las 8 muestras más recientes y se detiene. Captura la PRIMERA y la ÚLTIMA muestra de g_blink_count "
    "y confirma que el valor va AUMENTANDO &mdash; prueba directa, sobre silicio, de que el loop while(1) "
    "se está ejecutando (no sólo que el .hex se flasheó). "
    "\n\n"
    "Paso 8 (HIL #3 &mdash; reset): \"Run STM32er with action='reset' and project_dir='<project_dir>'\" "
    "para hacer un reset por hardware del MCU y dejar la placa en un estado limpio. "
    "\n\n"
    "Paso 9: muestra un MARCADOR DE STATUS &mdash; una fila de chips HTML con la forma "
    "<span style='display:inline-block;padding:8px 16px;margin:3px;border-radius:10px;"
    "font-weight:800;background:CHIP_BG;color:#ffffff;'>LABEL</span>: un chip 'validate: <ok|err>', "
    "un chip 'build: <ok|err>', un chip 'flash: <ok|err>', un chip 'serial: <ok|err>', un "
    "chip 'live_mem: <ok|err>', un chip 'reset: <ok|err>' (CHIP_BG #16a34a cuando es ok, si no #dc2626), y "
    "un chip 'count: <first>&rarr;<last>' (CHIP_BG #2563EB). "
    "\n\n"
    "Paso 10: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>STM32 HIL Observatory &mdash; Reporte de ejecución</strong>' y con las columnas <em>paso</em>, "
    "<em>stage</em> (validate|project|build|flash|serial|live_memory|reset), <em>stm32_action</em>, "
    "<em>status</em> (ok|error), <em>resumen</em> (stlink_connected; project_dir; build returncode; "
    "flash verify; la línea de arranque VCP capturada; g_blink_count first&rarr;last; reset ok) &mdash; una "
    "fila por cada llamada en orden de ejecución, status tal cual del bloque INI_SECTION_STM32ER (NO lo "
    "reclasifiques). Celdas del cuerpo claras (background:#ffffff;color:#0f172a; o rayado #f1f5f9). "
    "\n\n"
    "Paso 11: cierra con un banner HTML que reutilice el estilo del Paso 0 "
    "'&#9989; SILICIO VERIFICADO' (build returncode=0 AND flash AND serial AND live_memory todos ok "
    "&mdash; el contador se observó SUBIENDO por SWD), '&#9888;&#65039; SIN PLACA' (el Paso 1 no encontró "
    "ST-LINK conectado) o '&#10060; ERROR DE BUILD' (build returncode &ne; 0), y debajo una "
    "métrica de una línea 'project: <project_dir> &middot; build rc: <0> &middot; flash: <verified> "
    "&middot; VCP: \"<boot line>\" &middot; g_blink_count por SWD: <first>&rarr;<last>'. Termina con "
    "END-RESPONSE."
)


_NEW_PROMPTS = (
    (63, STM32_GENESIS_DEMO),
    (64, STM32_BLINKY_DEMO),
    (65, STM32_HIL_OBSERVATORY_DEMO),
)


def add_stm32er_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_stm32er_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0102_add_chat_agent_stm32er_tool'),
    ]

    operations = [
        migrations.RunPython(add_stm32er_demo_prompts, remove_stm32er_demo_prompts),
    ]
