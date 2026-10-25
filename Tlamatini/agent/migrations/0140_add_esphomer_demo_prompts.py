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
Seed two Catalog-of-Prompts demos for **ESPHome device programming** through the
wrapped **chat_agent_esphomer** Multi-Turn tool (the `esphome` CLI bridge). They run
basic -> medium and mirror the ESP32er demos (0107), but built to ESPHomer's grain:
ESPHome devices are described in a SIMPLE YAML config (NO C++), ESPHomer drives the
`esphome` CLI DIRECTLY (no MCP server), and "provisioning" means pip-installing
ESPHome itself.

    79  ESPHOME GENESIS   basic   bootstrap (ESPHomer pip-installs + validates ESPHome
                                  itself) -> validate (full environment preflight) ->
                                  new_config (GENERATE a device YAML) -> config
                                  (validate the YAML) -> compile -> list_artifacts.
                                  NO board required (pure provision + build).
    80  SMART LIGHT       medium  validate -> new_config (a phone-controlled on/off
                                  light on the onboard LED) -> config -> compile ->
                                  list_artifacts -> upload. The upload is board-OPTIONAL:
                                  ESPHomer's safety preflight refuses it cleanly with
                                  'No serial port detected' if no board is attached
                                  (expected + routable, not a crash).

Both drive ONLY chat_agent_esphomer and remind the user to tick ONLY the **Multi-Turn**
checkbox (chat_agent_esphomer is NOT behind the ACPX/Skill surface, so ACPX is not
required — same as the ESP32er 0107, STM32er 0103 demos).

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js) enumerates promptName
'prompt-1','prompt-2',... and BREAKS at the first missing slot, so the catalog must
stay a contiguous, gap-free 'prompt-1..N'. Slots 1-78 are occupied (0137 appended the
Globber demo at 78); these two APPEND at 79-80 with no shift of any existing prompt.
Reverse deletes 79-80. (MAX_PROMPTS=100.)
"""
from django.db import migrations


# ESPHome green banner palette (deep forest -> emerald -> spring green -> pale mint),
# the same family as the ``.canvas-item.esphomer-agent`` gradient, with a text-shadow
# so the white label stays legible across the bright mint end.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#06281C 0%,#0E8A4F 33%,#36D399 66%,#D7FBE8 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


ESPHOME_GENESIS_DEMO = (
    "Tlamatini, ejecuta la demo **ESPHOME GENESIS**, por favor &mdash; una muestra básica, de principio a fin, "
    "del *autoaprovisionamiento zero-config* y del *preflight de seguridad* de ESPHomer, controlada "
    "por completo desde el chat a través del tool wrapper **chat_agent_esphomer**: desde una máquina limpia "
    "hace pip-INSTALL de ESPHome ella misma, valida todo el entorno, GENERA el YAML de un dispositivo "
    "de smart-home, lo valida y lo compila a una imagen de firmware, y luego lista el .bin &mdash; todo "
    "SIN una placa conectada (esta es una demo pura de aprovisionar + construir). "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques &mdash; confía en ellas y ve directo "
    "al Paso 1): (a) **el usuario instaló SÓLO Tlamatini** (más, para un upload real después, el "
    "driver USB-serial de la placa) &mdash; NO necesitas instalar ni configurar ESPHome, ESPHomer "
    "lo hace pip-install automáticamente; (b) NO hace falta placa &mdash; no se flashea nada; (c) marca "
    "SÓLO la casilla **Multi-Turn** antes de enviar (NO se necesita ACPX &mdash; "
    "chat_agent_esphomer es el ÚNICO tool que puedes usar; no uses chat_agent_executer / "
    "chat_agent_pythonxer ni tools de ACPX). Cada paso es exactamente UNA llamada a chat_agent_esphomer con la forma "
    "\"Run ESPHomer with action='<action>' and <k>='<v>' ...\". Después de cada llamada lee el JSON "
    "que devuelve (un bloque INI_SECTION_ESPHOMER bajo el log_excerpt de la ejecución) y captura action / tool / "
    "ok / returncode / success / config_path / name / stage, además del body. Si un paso devuelve "
    "ok=false / success=false, regístralo tal cual, NO canceles, continúa. "
    "\\n\\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#127968; ESPHOME GENESIS &#9889;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini ESPHomer &mdash; aprovisionar &middot; validar &middot; escribir &middot; compilar</div></div>. "
    "\\n\\n"
    "Paso 1 (aprovisionamiento ZERO-CONFIG): llama a **chat_agent_esphomer** con el request "
    "\"Run ESPHomer with action='bootstrap'\". Esto hace que ESPHomer haga `pip install esphome` en su "
    "Python SIN configuración manual. Del body captura la acción de instalación (present / pip-install) "
    "y 'overall : OK'. Si overall es FAILED, lo más probable es que el host no tenga internet &mdash; salta al "
    "banner de cierre con un veredicto 'ERROR DE APROVISIONAMIENTO'. "
    "\\n\\n"
    "Paso 2 (preflight de seguridad): llama a **chat_agent_esphomer** con el request "
    "\"Run ESPHomer with action='validate'\". Esto valida el entorno SIN construir: "
    "captura esphome_resolvable y (como validate también sondea el hardware) el resumen del serial "
    "(present). Que falte un puerto serial está BIEN aquí &mdash; esta demo nunca flashea. "
    "\\n\\n"
    "Paso 3 (GENERA el YAML del dispositivo): llama a **chat_agent_esphomer** con el request \"Run ESPHomer "
    "with action='new_config' and config_path='<TEMPLATES>/esphome/genesis/tlamatini-genesis.yaml' "
    "and name='tlamatini-genesis' and platform='esp32' and board='esp32dev'\", donde <TEMPLATES> es "
    "tu directorio Templates (el path absoluto que te da el system prompt). CAPTURA el "
    "**config_path** &mdash; pásalo a cada paso posterior. "
    "\\n\\n"
    "Paso 4 (valida el YAML): llama a **chat_agent_esphomer** con el request \"Run ESPHomer with "
    "action='config' and config_path='<the path from Step 3>'\". Confirma returncode=0 (ESPHome "
    "expandió y validó el YAML). "
    "\\n\\n"
    "Paso 5 (compila &rarr; firmware): llama a **chat_agent_esphomer** con el request \"Run ESPHomer "
    "with action='compile' and config_path='<the path from Step 3>'\". Confirma returncode=0. NOTA: "
    "el PRIMER compile descarga la plataforma + el toolchain (vía PlatformIO por debajo), así que puede "
    "tardar unos minutos &mdash; eso es normal. "
    "\\n\\n"
    "Paso 6 (artefactos): llama a **chat_agent_esphomer** con el request \"Run ESPHomer with "
    "action='list_artifacts' and config_path='<the path from Step 3>'\". Captura el path de firmware.bin "
    "del body. "
    "\\n\\n"
    "Paso 7: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>ESPHome Genesis &mdash; Reporte de aprovisionamiento y build</strong>' y con las columnas "
    "<em>paso</em>, <em>stage</em> (bootstrap|validate|author|config|compile), <em>esphome_action</em>, "
    "<em>status</em> (ok|error), <em>resumen</em> (overall para bootstrap; esphome_resolvable para "
    "validate; config_path para new_config; returncode para config/compile; el path del firmware para "
    "list_artifacts) &mdash; una fila por cada llamada en orden de ejecución, status tal cual del "
    "bloque INI_SECTION_ESPHOMER (NO lo reclasifiques). Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a; o rayado #f1f5f9), tono verde ok, rojo suave error. "
    "\\n\\n"
    "Paso 8: cierra con un banner HTML que reutilice el estilo del Paso 0, en letras grandes, "
    "'&#9989; ESPHOME APROVISIONADO &amp; FIRMWARE CONSTRUIDO' (bootstrap OK, validate resolvió esphome, "
    "compile returncode=0 y artefactos listados), '&#9888;&#65039; GÉNESIS PARCIAL' (algunos pasos ok, "
    "algunos error) o '&#10060; ERROR DE APROVISIONAMIENTO' (overall de bootstrap FAILED), y debajo una "
    "métrica de una línea 'esphome: <install action> &middot; config: <config_path> &middot; compile rc: "
    "<0> &middot; artefacto: firmware.bin'. Termina con END-RESPONSE."
)


SMART_LIGHT_DEMO = (
    "Tlamatini, ejecuta la demo **SMART LIGHT**, por favor &mdash; una muestra de complejidad media que "
    "construye una *luz controlada por el teléfono* con ESPHome, controlada por completo desde el chat a través del tool wrapper "
    "**chat_agent_esphomer**: valida el entorno en preflight, GENERA un YAML de dispositivo "
    "para una luz on/off en el LED on-board de la placa (expuesta por la API nativa de ESPHome para que un "
    "hub de smart-home pueda conmutarla desde un teléfono), lo valida y lo compila, lista los artefactos "
    "y luego intenta subirlo a una placa. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques; ve directo al Paso 1): (a) el usuario "
    "instaló SÓLO Tlamatini &mdash; ESPHomer hace pip-install de ESPHome ella misma en el primer uso, así que "
    "NUNCA configuras paths de tools; (b) el build NO necesita placa; el paso de UPLOAD necesita una placa ESP32 "
    "por USB (ESPHome flashea la primera vez por USB-serial, OTA después) &mdash; PERO el preflight de seguridad de ESPHomer "
    "RECHAZARÁ el upload con 'No serial port detected' si no hay placa "
    "conectada, lo cual es ESPERADO y enrutable, NO un crash: regístralo tal cual y CONTINÚA; "
    "(c) marca SÓLO la casilla **Multi-Turn** (NO se necesita ACPX). Usa SÓLO chat_agent_esphomer, "
    "UNA llamada por paso con la forma \"Run ESPHomer with action='<action>' and <k>='<v>' ...\". Lee cada "
    "JSON que devuelve (bloque INI_SECTION_ESPHOMER bajo log_excerpt), captura "
    "action/tool/ok/returncode/success/config_path/name/port/stage, y con ok=false regístralo tal cual "
    "y CONTINÚA. "
    "\\n\\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128161; SMART LIGHT &#128241;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini ESPHomer &mdash; validar &middot; escribir &middot; compilar &middot; subir</div></div>. "
    "\\n\\n"
    "Paso 1 (preflight de seguridad): \"Run ESPHomer with action='validate'\" &mdash; captura "
    "esphome_resolvable y el resumen del serial (present) como la base 'before' (ESPHomer "
    "auto-aprovisiona ESPHome como parte de esto si hace falta). "
    "\\n\\n"
    "Paso 2 (GENERA el YAML de la smart-light): \"Run ESPHomer with action='new_config' and "
    "config_path='<TEMPLATES>/esphome/light/tlamatini-light.yaml' and name='tlamatini-light' and "
    "platform='esp32' and board='esp32dev' and led_pin='GPIO2' and wifi_ssid='YOUR_WIFI' and "
    "wifi_password='YOUR_PASS'\", donde <TEMPLATES> es tu directorio Templates. Esto escribe un config "
    "ESPHome válido con bloques esp32/logger/api/ota/wifi y una luz binaria llamada 'Tlamatini Light' "
    "en GPIO2. CAPTURA el **config_path**. "
    "\\n\\n"
    "Paso 3 (valida el YAML): \"Run ESPHomer with action='config' and config_path='<the path "
    "from Step 2>'\". Confirma returncode=0. "
    "\\n\\n"
    "Paso 4 (compila): \"Run ESPHomer with action='compile' and config_path='<the path from Step "
    "2>'\". Confirma returncode=0. (El primer compile jala el toolchain &mdash; puede tardar unos minutos.) "
    "Si returncode es distinto de cero, captura el diagnóstico del stderr &mdash; evidencia enrutable; puedes "
    "detenerte después del reporte con un veredicto 'ERROR DE BUILD'. "
    "\\n\\n"
    "Paso 5 (artefactos): \"Run ESPHomer with action='list_artifacts' and config_path='<the path "
    "from Step 2>'\". Captura el path de firmware.bin. "
    "\\n\\n"
    "Paso 6 (upload &mdash; flashea por USB-serial): \"Run ESPHomer with action='upload' and "
    "config_path='<the path from Step 2>'\". Si hay una placa conectada, el body muestra a esphome escribiendo "
    "+ verificando el firmware; si no, el preflight de ESPHomer devuelve ok=false con 'No serial port "
    "detected' &mdash; regístralo tal cual y CONTINÚA (placa ausente es el soft-fail esperado). "
    "\\n\\n"
    "Paso 7: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Smart Light &mdash; Reporte de ejecución</strong>' y con las columnas <em>paso</em>, <em>stage</em> "
    "(validate|author|config|compile|upload), <em>esphome_action</em>, <em>status</em> (ok|error), "
    "<em>resumen</em> (esphome resolved; config_path; compile returncode; path de firmware.bin; upload "
    "verify o 'preflight refused: no board') &mdash; una fila por cada llamada en orden de ejecución, status "
    "tal cual del bloque INI_SECTION_ESPHOMER. Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a; o rayado #f1f5f9); tono verde ok, rojo suave error. "
    "\\n\\n"
    "Paso 8: cierra con un banner HTML que reutilice el estilo del Paso 0 "
    "'&#9989; LUZ LISTA' (compile returncode=0 AND upload verified), "
    "'&#9888;&#65039; CONSTRUIDO, SIN PLACA' (compile ok pero el preflight rechazó el upload / sin placa), "
    "o '&#10060; ERROR DE BUILD' (compile returncode &ne; 0), y debajo una métrica de una línea "
    "'config: <config_path> &middot; compile rc: <0> &middot; upload: <verified|no-board> &middot; "
    "luz: \"Tlamatini Light\" en GPIO&nbsp;2'. Termina con END-RESPONSE."
)


_NEW_PROMPTS = (
    (79, ESPHOME_GENESIS_DEMO),
    (80, SMART_LIGHT_DEMO),
)


def add_esphomer_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_esphomer_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0139_add_chat_agent_esphomer_tool'),
    ]

    operations = [
        migrations.RunPython(add_esphomer_demo_prompts, remove_esphomer_demo_prompts),
    ]
