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
Fix the **STM32 HIL OBSERVATORY** demo (catalog prompt #65, seeded by 0103).

WHY
---
Live run on a real STM32F407G-DISC1 exposed a board-specific flaw in the demo as
first written. The board flashed cleanly (green LED blinking) and the firmware
WAS running — proven by ``live_monitor`` reading ``g_blink_count`` climbing over
SWD (30 -> 31 -> 32). But the demo made the **serial VCP boot-banner read** a
PRIMARY proof step, and that read returns 0 bytes forever on this board:

    On the STM32F4-Discovery family (including the STM32F407G-DISC1) the on-board
    ST-LINK does NOT bridge its Virtual COM Port to the MCU's USART pins (unlike
    ST Nucleo boards, which route VCP <-> USART2 / PA2-PA3). A firmware that
    transmits on USART2 therefore produces NOTHING on the VCP, no matter the
    baud or timeout.

Because the demo gave the model no "empty VCP read is EXPECTED here, do NOT
retry" guidance, it thrashed: ~6 ``serial_session`` retries with escalating
timeouts (5/6/8/10/12 s, even injecting ``data='\\n'``), plus ``serial_connect``
+ ``serial_read`` + a stray ``reset`` — 21 STM32er calls for what should be ~9.

THE FIX (this migration rewrites prompt #65 only)
-------------------------------------------------
1. **live SWD memory (``live_monitor``) is now the PRIMARY, authoritative HIL
   proof** (it works on every ST-LINK board). It runs as Step 6, before serial.
2. **The serial VCP read is now best-effort, board-aware, and AT-MOST-ONCE.** The
   prompt states the F4-Discovery VCP-not-routed fact up front, tells the model an
   empty read (bytes=0) is the EXPECTED outcome on this board, and forbids the
   retry / connect-read loop. (Real UART would need an external USB-TTL adapter on
   PA2/PA3 — out of scope for an ST-LINK-only demo.)
3. **The "SILICON VERIFIED" verdict is re-keyed on build + flash + live_memory.**
   Serial is a bonus chip (green = data, amber = expected-empty, red = real connect
   error), never a gate, so the demo reaches a clean success on a Discovery board.

This is a content-only update of one ``Prompt`` row via ``update_or_create`` —
no schema change. Reverse restores the original 0103 text verbatim.
"""
import importlib

from django.db import migrations


_HIL_PROMPT_ID = 65


# Reuse the exact ST-blue banner palette from 0103 so the demo keeps its look.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#061029 0%,#0B3A8F 40%,#1E63FF 72%,#22D3EE 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.45);'>"
)


STM32_HIL_OBSERVATORY_DEMO_V2 = (
    "Tlamatini, ejecuta la demo **STM32 HIL OBSERVATORY**, por favor &mdash; una muestra avanzada "
    "**hardware-in-the-loop** que USA UNA PLACA REAL de principio a fin, controlada por completo desde el "
    "chat a través del tool wrapper **chat_agent_stm32er**: valida en preflight que haya un ST-LINK "
    "conectado, arma y ESCRIBE un firmware que incrementa un contador global (y también "
    "lo transmite por UART), lo construye + flashea en la placa y luego PRUEBA que está corriendo en silicio "
    "real &mdash; PRINCIPALMENTE muestreando una variable global en vivo de la RAM del MCU EN EJECUCIÓN por "
    "SWD (esto funciona en TODA placa con ST-LINK), y como BONUS de mejor esfuerzo leyendo el Virtual COM Port "
    "del ST-LINK &mdash; antes de hacer un reset por hardware de la placa. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques; ve directo al Paso 1): (a) el usuario "
    "instaló SÓLO STM32CubeIDE (STM32er auto-aprovisiona el MCP por su cuenta); (b) **hay una placa STM32F407 "
    "(p. ej. STM32F407G-DISC1) CONECTADA** por ST-LINK &mdash; esta demo REQUIERE hardware; "
    "(c) **DATO IMPORTANTE DE LA PLACA &mdash; LÉELO:** en la familia STM32F4-Discovery (incluida la "
    "STM32F407G-DISC1) el ST-LINK on-board **NO** puentea su Virtual COM Port a los pines USART del MCU "
    "como lo hacen las placas ST **Nucleo** (Nucleo enruta VCP&harr;USART2 en PA2/PA3). Así que, aunque "
    "el firmware corra y transmita en USART2, leer el VCP en una placa Discovery devuelve "
    "**EMPTY (bytes=0)** &mdash; esto es ESPERADO, NO un error. Por lo tanto, la prueba sobre silicio AUTORITATIVA "
    "en esta demo es la **lectura en vivo del contador en memoria por SWD**, NO la línea serial. "
    "(Capturar UART real en una Discovery requeriría cablear un adaptador USB-TTL externo a PA2/PA3 "
    "&mdash; fuera de alcance para esta demo de sólo ST-LINK.) (d) marca SÓLO la casilla **Multi-Turn** "
    "(NO se necesita ACPX). Usa SÓLO chat_agent_stm32er, UNA llamada por paso con la forma \"Run STM32er with "
    "action='<action>' and <k>='<v>' ...\". Lee cada JSON que devuelve (bloque INI_SECTION_STM32ER bajo "
    "log_excerpt), captura action/ok/returncode/success/project_dir/session_id/stage, y con "
    "ok=false regístralo tal cual y CONTINÚA. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128300; STM32 HIL OBSERVATORY &#9889;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini STM32er &mdash; validate &middot; flash &middot; memoria SWD en vivo &middot; VCP serial (bonus)</div></div>. "
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
    "+ USART2 (115200 8N1, en PA2/PA3), y en el loop while(1): incremente g_blink_count, "
    "conmute el LED, transmita una sola línea de status terminada en newline con la forma "
    "'BOOT tlamatini hil count=<n>' por USART2 con HAL_UART_Transmit, y HAL_Delay(500). "
    "**El contador `g_blink_count` es la prueba que importa (leída en vivo por SWD en el Paso 6); la "
    "línea UART es de mejor esfuerzo &mdash; es inofensiva en una placa Discovery y es lo que una placa Nucleo "
    "ECHARÍA en su VCP.** Pásalo como un literal content con comillas triples (content='''...''') para que "
    "los newlines y las llaves sobrevivan al parser. Mantenlo autocontenido y construible contra la "
    "HAL del scaffold. "
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
    "Paso 6 (HIL #1 &mdash; PRUEBA PRINCIPAL: memoria SWD en vivo): \"Run STM32er with action='live_monitor' "
    "and variables='[\"g_blink_count\"]' and project_dir='<project_dir>' and monitor_seconds='4' "
    "and last_n='8'\". Esto inicia un stream de OpenOCD de la RAM del MCU EN EJECUCIÓN, muestrea el global por "
    "4 segundos, devuelve las 8 muestras más recientes y se detiene. Captura la PRIMERA y la ÚLTIMA muestra de g_blink_count "
    "y confirma que el valor va AUMENTANDO &mdash; esta es la prueba directa, agnóstica de la placa, "
    "sobre silicio de que el loop while(1) se está ejecutando (no sólo que el .hex se flasheó). ESTA es la "
    "prueba HIL autoritativa de esta demo. "
    "\n\n"
    "Paso 7 (HIL #2 &mdash; VCP serial de mejor esfuerzo, A LO MÁS UNA VEZ, NO REINTENTES): opcionalmente lee el "
    "VCP del ST-LINK UNA sola vez: \"Run STM32er with action='serial_session' and port='<the ST-LINK VCP "
    "port>' and baud='115200' and serial_timeout='5'\" (PUEDES primero llamar action='serial_list_ports' "
    "y elegir el puerto marcado stlink_vcp=true). Sin `data` puesto, serial_session conecta, LEE, "
    "y luego desconecta. **Si la lectura devuelve data, captura la línea 'BOOT tlamatini hil count=' como un "
    "BONUS. Si devuelve EMPTY (bytes=0) &mdash; que es el resultado ESPERADO en la STM32F407G-DISC1, "
    "cuyo ST-LINK no enruta el VCP al USART del MCU &mdash; registra 'no VCP route on this board "
    "(Discovery)' y SIGUE. Llama a serial_session A LO MÁS UNA VEZ: NO lo reintentes con timeouts más largos, "
    "NO inyectes newlines, NO caigas en bucles de serial_connect/serial_read. Un VCP vacío aquí "
    "es normal, no una falla, y la lectura SWD en vivo del Paso 6 ya probó que el firmware está "
    "alive.** "
    "\n\n"
    "Paso 8 (HIL #3 &mdash; reset): \"Run STM32er with action='reset' and project_dir='<project_dir>'\" "
    "para hacer un reset por hardware del MCU y dejar la placa en un estado limpio. "
    "\n\n"
    "Paso 9: muestra un MARCADOR DE STATUS &mdash; una fila de chips HTML con la forma "
    "<span style='display:inline-block;padding:8px 16px;margin:3px;border-radius:10px;"
    "font-weight:800;background:CHIP_BG;color:#ffffff;'>LABEL</span>: un chip 'validate: <ok|err>', "
    "un chip 'build: <ok|err>', un chip 'flash: <ok|err>', un chip 'live_mem: <ok|err>' (LA prueba clave), "
    "un chip 'serial: <ok|n/a>', un chip 'reset: <ok|err>' y un chip 'count: <first>&rarr;<last>'. "
    "CHIP_BG es #16a34a (verde) cuando es ok; #dc2626 (rojo) ante un error real; para el chip 'serial' usa "
    "#d97706 (ámbar) con label 'serial: n/a (no VCP route)' cuando la lectura fue EXPECTED-empty en esta "
    "placa (ámbar NO es un error); el chip 'count' es #2563EB (azul). "
    "\n\n"
    "Paso 10: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>STM32 HIL Observatory &mdash; Reporte de ejecución</strong>' y con las columnas <em>paso</em>, "
    "<em>stage</em> (validate|project|build|flash|live_memory|serial|reset), <em>stm32_action</em>, "
    "<em>status</em> (ok|error), <em>resumen</em> (stlink_connected; project_dir; build returncode; "
    "flash verify; g_blink_count first&rarr;last; la línea VCP capturada OR 'no VCP route on this board'; "
    "reset ok) &mdash; una fila por cada llamada en orden de ejecución, status tal cual del bloque INI_SECTION_STM32ER "
    "(NO lo reclasifiques). Celdas del cuerpo claras (background:#ffffff;color:#0f172a; o rayado #f1f5f9). "
    "\n\n"
    "Paso 11: cierra con un banner HTML que reutilice el estilo del Paso 0 "
    "'&#9989; SILICIO VERIFICADO' (build returncode=0 AND flash verified AND live_memory mostró "
    "g_blink_count SUBIENDO por SWD &mdash; la línea VCP serial es un BONUS y NO se requiere para este "
    "veredicto), '&#9888;&#65039; SIN PLACA' (el Paso 1 no encontró ST-LINK conectado) o '&#10060; ERROR DE BUILD' "
    "(build returncode &ne; 0), y debajo una métrica de una línea 'project: <project_dir> &middot; "
    "build rc: <0> &middot; flash: <verified> &middot; g_blink_count por SWD: <first>&rarr;<last> "
    "&middot; VCP: <\"<boot line>\" | n/a (no VCP route on F4-Discovery)>'. Termina con END-RESPONSE."
)


def _restore_original_0103_text():
    """Best-effort load of the original prompt-65 text from migration 0103 for the reverse."""
    try:
        m0103 = importlib.import_module("agent.migrations.0103_add_stm32er_demo_prompts")
        return getattr(m0103, "STM32_HIL_OBSERVATORY_DEMO", None)
    except Exception:
        return None


def fix_hil_serial_proof(apps, schema_editor):
    Prompt = apps.get_model("agent", "Prompt")
    Prompt.objects.update_or_create(
        idPrompt=_HIL_PROMPT_ID,
        defaults={"promptName": f"prompt-{_HIL_PROMPT_ID}", "promptContent": STM32_HIL_OBSERVATORY_DEMO_V2},
    )


def revert_hil_serial_proof(apps, schema_editor):
    original = _restore_original_0103_text()
    if not original:
        # 0103 unavailable (e.g. squashed) — leave the corrected text in place rather than wiping it.
        return
    Prompt = apps.get_model("agent", "Prompt")
    Prompt.objects.update_or_create(
        idPrompt=_HIL_PROMPT_ID,
        defaults={"promptName": f"prompt-{_HIL_PROMPT_ID}", "promptContent": original},
    )


class Migration(migrations.Migration):
    dependencies = [
        ("agent", "0103_add_stm32er_demo_prompts"),
    ]

    operations = [
        migrations.RunPython(fix_hil_serial_proof, revert_hil_serial_proof),
    ]
