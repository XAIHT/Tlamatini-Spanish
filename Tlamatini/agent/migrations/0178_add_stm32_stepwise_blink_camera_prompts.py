# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Two STEP-BY-STEP LED-blink walkthroughs for the STM32er PlatformIO backend
(Angela, 2026-07-15): a Blue Pill (STM32F103) over an external ST-LINK V2, and an
STM32F407G-DISC1 over its embedded ST-Link. Both are Multi-Turn + Exec-report +
Step-by-Step and go from installing the ST-Link driver, through a per-step
VERIFICATION at each stage, to confirming the LED actually blinks with the default
camera (Camcorder). Category 'firmware_iot'. Appended at the next free idPrompt;
the very next migration (0179) re-groups/re-sorts the whole catalog with no gaps.

Badge inference (tools_dialog.js::classifyPromptModes): driving chat_agent_stm32er
gives the Multi-turn badge (and Exec-report rides along automatically); the
UNFORMATTED phrase "Step-by-Step mode" (hyphenated + a keyword) lights the
Step-by-Step badge.
"""
from django.db import migrations


BLUEPILL_STEP_DEMO = (
    "Tlamatini, guíame para programar el **clásico blink de LED en una Blue Pill "
    "(STM32F103C8), flasheada sobre un ST-LINK V2 externo**, UN paso a la vez, y comprueba que el "
    "LED de verdad parpadea con mi cámara predeterminada al final. Antes de empezar, marca **Multi-Turn**, "
    "**Exec report** y la **Step-by-Step** checkbox.\n"
    "\n"
    "Como el Step-by-Step mode está activado, haz EXACTAMENTE UN paso por turno, luego DETENTE y ESPERA a que yo "
    "responda `READY` (con el output/foto que me hayas pedido) antes del siguiente paso. VERIFICA cada paso "
    "tú misma antes de avanzar — si una comprobación falla, dime exactamente qué arreglar y vuelve a revisar; nunca "
    "te saltes pasos. Usa SÓLO tus propios agents: chat_agent_stm32er (backend de PlatformIO) para build/flash "
    "y chat_agent_camcorder para la cámara. El LED de usuario de la Blue Pill está en PC13; con "
    "el framework 'arduino' ese es LED_BUILTIN.\n"
    "\n"
    "STEP 1 — Instala el driver USB del ST-LINK V2. Dime que instale el driver del ST-Link (STSW-LINK009, "
    "o que simplemente instale STM32CubeProgrammer — trae el driver), que conecte el dongle ST-LINK V2 en un "
    "puerto USB y que responda READY. LUEGO verifica: corre chat_agent_stm32er con action='validate', "
    "stm32_backend='platformio', board='bluepill_f103c8', y confirma que STM32_Programmer_CLI es "
    "RESOLVABLE. (La placa aún no está conectada, así que la probe del ST-LINK puede leerse ausente aquí — eso es "
    "esperado; en este paso sólo necesitamos que el CLI/driver estén presentes.) Reporta la comprobación y espera.\n"
    "\n"
    "STEP 2 — Conecta la Blue Pill al ST-LINK V2 (SWD, 4 cables) y confirma que se ve la probe. Dime "
    "que conecte ST-LINK 3.3V→Blue Pill 3V3, GND→GND, SWDIO→DIO, SWCLK→CLK, y luego responda READY. LUEGO "
    "verifica: vuelve a correr action='validate' (mismos params) y confirma que la probe del ST-LINK ahora muestra PRESENT. "
    "Si sigue leyéndose ausente, ayúdame a resolverlo (cable, el jumper BOOT0 de regreso a 0, el driver) "
    "y vuelve a revisar. Espera.\n"
    "\n"
    "STEP 3 — Haz bootstrap de PlatformIO (zero-config). Corre chat_agent_stm32er con action='bootstrap', "
    "stm32_backend='platformio'. Confirma que PlatformIO Core está listo (se instala solo en el primer uso — "
    "esto puede tardar unos minutos). Reporta y espera.\n"
    "\n"
    "STEP 4 — Crea el proyecto y COMPILA el blink (no se necesita acceso a la placa para compilar). Corre "
    "chat_agent_stm32er con action='create_project', stm32_backend='platformio', "
    "board='bluepill_f103c8', framework='arduino', project_dir='<your Templates directory>/"
    "bluepill_blink'. Luego action='write_source', project_dir=<same>, rel_path='src/main.cpp', "
    "content= este sketch VERBATIM:\n"
    "\n"
    "    #include <Arduino.h>\n"
    "    void setup() { pinMode(LED_BUILTIN, OUTPUT); }\n"
    "    void loop() {\n"
    "      digitalWrite(LED_BUILTIN, HIGH); delay(500);\n"
    "      digitalWrite(LED_BUILTIN, LOW);  delay(500);\n"
    "    }\n"
    "\n"
    "Luego action='build', project_dir=<same>. Confirma que el build SUCCEEDED en el Exec report (el "
    "primer build descarga el toolchain de STM32 Arduino — déjalo terminar). Reporta y espera.\n"
    "\n"
    "STEP 5 — FLASHÉALO sobre el ST-LINK. Corre chat_agent_stm32er con action='flash', "
    "stm32_backend='platformio', board='bluepill_f103c8', project_dir=<same>. Confirma que el flash "
    "SUCCEEDED. (Si falla con un error de USB/OpenOCD, el ST-LINK puede necesitar el driver WinUSB vía "
    "Zadig — dime y vuelve a revisar.) El LED PC13 ahora debería parpadear ~1 Hz. Reporta y espera.\n"
    "\n"
    "STEP 6 — VERIFICA el parpadeo con mi cámara predeterminada. Dime que apunte el LED PC13 de la Blue Pill a "
    "mi webcam, luego responde READY. LUEGO corre chat_agent_camcorder con capture_mode='video', "
    "camera_index=0, video_duration_seconds=6 para grabar la placa. Inspecciona el clip guardado (PUEDES "
    "pasarlo a chat_agent_video_analyzer o chat_agent_image_interpreter) y dime PASS (el LED "
    "está parpadeando) o FAIL (fijo/apagado), con el path del archivo.\n"
    "\n"
    "Termina con un resumen HTML corto y ordenado de los seis pasos y el PASS/FAIL final. Termina con "
    "END-RESPONSE."
)


DISCO_STEP_DEMO = (
    "Tlamatini, guíame para programar el **clásico blink de LED en una placa STM32F407G-DISC1 "
    "Discovery, flasheada sobre su ST-Link/V2 EMBEBIDO (on-board)**, UN paso a la vez, y "
    "comprueba que el LED de verdad parpadea con mi cámara predeterminada al final. Antes de empezar, marca "
    "**Multi-Turn**, **Exec report** y la **Step-by-Step** checkbox.\n"
    "\n"
    "Como el Step-by-Step mode está activado, haz EXACTAMENTE UN paso por turno, luego DETENTE y ESPERA a que yo "
    "responda `READY` (con el output/foto que me hayas pedido) antes del siguiente paso. VERIFICA cada paso "
    "tú misma antes de avanzar — si una comprobación falla, dime exactamente qué arreglar y vuelve a revisar; nunca "
    "te saltes pasos. Usa SÓLO tus propios agents: chat_agent_stm32er (backend de PlatformIO) para build/flash "
    "y chat_agent_camcorder para la cámara. La F407-DISC1 tiene cuatro LEDs de usuario en PD12–PD15 "
    "(verde/naranja/rojo/azul); con el framework 'arduino' el LED verde (PD12) es LED_BUILTIN. No "
    "hace falta dongle externo ni cableado — el ST-Link está integrado en la placa.\n"
    "\n"
    "STEP 1 — Instala el driver del ST-Link AND conecta la placa. Dime que instale el driver USB del ST-Link/V2 "
    "(STSW-LINK009, o que simplemente instale STM32CubeProgrammer — trae el driver), y luego conecte "
    "la placa a mi PC usando su puerto USB de ST-LINK (el conector mini-USB CN1, rotulado "
    "'ST-LINK' — NO el puerto micro-USB OTG), y responda READY. LUEGO verifica: corre chat_agent_stm32er "
    "con action='validate', stm32_backend='platformio', board='disco_f407vg', y confirma TANTO que "
    "STM32_Programmer_CLI es resolvable AND que la probe del ST-Link embebido muestra PRESENT (la placa "
    "alimenta su ST-Link desde ese puerto USB). Si la probe se lee ausente, ayúdame a arreglarlo (puerto USB "
    "correcto, cable, driver) y vuelve a revisar. Espera.\n"
    "\n"
    "STEP 2 — Haz bootstrap de PlatformIO (zero-config). Corre chat_agent_stm32er con action='bootstrap', "
    "stm32_backend='platformio'. Confirma que PlatformIO Core está listo (se instala solo en el primer uso — unos "
    "minutos). Reporta y espera.\n"
    "\n"
    "STEP 3 — Crea el proyecto y COMPILA el blink. Corre chat_agent_stm32er con "
    "action='create_project', stm32_backend='platformio', board='disco_f407vg', framework='arduino', "
    "project_dir='<your Templates directory>/disc1_blink'. Luego action='write_source', "
    "project_dir=<same>, rel_path='src/main.cpp', content= este sketch VERBATIM:\n"
    "\n"
    "    #include <Arduino.h>\n"
    "    void setup() { pinMode(LED_BUILTIN, OUTPUT); }\n"
    "    void loop() {\n"
    "      digitalWrite(LED_BUILTIN, HIGH); delay(500);\n"
    "      digitalWrite(LED_BUILTIN, LOW);  delay(500);\n"
    "    }\n"
    "\n"
    "Luego action='build', project_dir=<same>. Confirma que el build SUCCEEDED en el Exec report (el "
    "primer build descarga el toolchain de STM32 Arduino — déjalo terminar). Reporta y espera.\n"
    "\n"
    "STEP 4 — FLASHÉALO sobre el ST-Link embebido. Corre chat_agent_stm32er con action='flash', "
    "stm32_backend='platformio', board='disco_f407vg', project_dir=<same>. Confirma que el flash "
    "SUCCEEDED. El LED verde (PD12) ahora debería parpadear ~1 Hz. Reporta y espera.\n"
    "\n"
    "STEP 5 — VERIFICA el parpadeo con mi cámara predeterminada. Dime que apunte el LED verde PD12 de la placa a "
    "mi webcam, luego responde READY. LUEGO corre chat_agent_camcorder con capture_mode='video', "
    "camera_index=0, video_duration_seconds=6. Inspecciona el clip (opcionalmente vía "
    "chat_agent_video_analyzer o chat_agent_image_interpreter) y dime PASS (parpadeando) o FAIL "
    "(fijo/apagado), con el path del archivo.\n"
    "\n"
    "Termina con un resumen HTML corto y ordenado de los cinco pasos y el PASS/FAIL final. Termina con "
    "END-RESPONSE."
)


_NEW_PROMPTS = (BLUEPILL_STEP_DEMO, DISCO_STEP_DEMO)


def add_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for content in _NEW_PROMPTS:
        if Prompt.objects.filter(promptContent=content).exists():
            continue
        next_id = (Prompt.objects.order_by('-idPrompt').values_list('idPrompt', flat=True).first() or 0) + 1
        Prompt.objects.update_or_create(
            idPrompt=next_id,
            defaults={
                'promptName': f'prompt-{next_id}',
                'promptContent': content,
                'category': 'firmware_iot',
            },
        )


def remove_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(promptContent__in=list(_NEW_PROMPTS)).delete()


class Migration(migrations.Migration):
    dependencies = [('agent', '0177_add_stm32er_platformio_demo_prompt')]
    operations = [migrations.RunPython(add_demo_prompts, remove_demo_prompts)]
