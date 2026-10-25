# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
from django.db import migrations


# Catalog-of-Prompts demo for STM32er's NEW PlatformIO backend (Phase 1 — the
# Blue Pill → whole-ST-line widening). Showcases the headline capability: build
# (and flash-if-connected) a classic LED blink for an STM32F103 Blue Pill in ONE
# call, choosing the target purely by `board` (which routes to the PlatformIO
# backend automatically). SAFE for the daily chat test: `scaffold_build_flash` is
# fail-safe — it CREATES the project and COMPILES the firmware, and only flashes
# over the ST-LINK when a probe is actually connected; with no board attached it
# reports "built OK — connect the ST-LINK and run action=flash", which is a SUCCESS,
# not an error. No destructive op. Appends at the next free idPrompt (gaps allowed
# since migration 0176) and tags the row into the existing 'firmware_iot' category.
DEMO = (
    "Tlamatini, ejecuta la **STM32er BLUE PILL DEMO** — construye (y flashéalo si hay una placa "
    "conectada) un clásico blink de LED para una **STM32F103 \"Blue Pill\"** usando tu nuevo "
    "backend de PlatformIO, en UNA sola llamada.\n"
    "\n"
    "En Multi-Turn, usando SÓLO el tool chat_agent_stm32er, llámalo EXACTAMENTE UNA VEZ con:\n"
    "  - action='scaffold_build_flash'\n"
    "  - stm32_backend='platformio'   (esto enruta al backend de PlatformIO — sin servidor MCP)\n"
    "  - board='bluepill_f103c8'      (el pio board id de la Blue Pill; fija el mapa de memoria/linker)\n"
    "  - framework='arduino'          (stm32duino — un blink de LED_BUILTIN agnóstico de la placa)\n"
    "  - project_dir='<your Templates directory>/bluepill_blink'  (usa de forma predeterminada TU directorio Templates salvo que yo indique otro path)\n"
    "  - content= este sketch de Arduino, pasado VERBATIM:\n"
    "\n"
    "        #include <Arduino.h>\n"
    "        void setup() { pinMode(LED_BUILTIN, OUTPUT); }\n"
    "        void loop() {\n"
    "          digitalWrite(LED_BUILTIN, HIGH); delay(500);\n"
    "          digitalWrite(LED_BUILTIN, LOW);  delay(500);\n"
    "        }\n"
    "\n"
    "ZERO-CONFIG: si PlatformIO Core todavía no está instalado, STM32er lo instala solo (compartido "
    "con ESP32er) en el primer uso — y el PRIMER build también descarga el toolchain de STM32 Arduino, "
    "así que puede tardar unos minutos; eso es normal, déjalo terminar.\n"
    "\n"
    "FAIL-SAFE: esto crea el proyecto y COMPILA el firmware; sólo flashea sobre el "
    "ST-LINK cuando hay una probe conectada. Sin placa reporta 'built OK — connect the "
    "ST-LINK and run action=flash', que es un SUCCESS. NO reintentes en bucle una descarga de toolchain "
    "fallida — reporta el stderr y detente.\n"
    "\n"
    "Cuando regrese, lee el resultado INI_SECTION_STM32ER y dame un resumen HTML corto y "
    "ordenado de: el backend usado, la placa, si el BUILD funcionó y si "
    "FLASHEÓ u omitió el flash (y por qué). Si quieres revisar primero el entorno, "
    "PUEDES hacer un action='validate' rápido con la misma placa antes del scaffold.\n"
    "\n"
    "Marca SÓLO la casilla Multi-Turn; usa SÓLO chat_agent_stm32er. Termina con END-RESPONSE."
)


def add_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    if Prompt.objects.filter(promptContent=DEMO).exists():
        return
    next_id = (Prompt.objects.order_by('-idPrompt').values_list('idPrompt', flat=True).first() or 0) + 1
    Prompt.objects.update_or_create(
        idPrompt=next_id,
        defaults={
            'promptName': f'prompt-{next_id}',
            'promptContent': DEMO,
            'category': 'firmware_iot',
        },
    )


def remove_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(promptContent=DEMO).delete()


class Migration(migrations.Migration):
    dependencies = [('agent', '0176_delete_duplicate_acpx_prompts')]
    operations = [migrations.RunPython(add_demo_prompt, remove_demo_prompt)]
