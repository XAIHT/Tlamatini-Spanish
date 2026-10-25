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
Seed one Catalog-of-Prompts demo for the **flow-making** skill — turning a plain
objective into a downloadable, canvas-loadable `.flw` by driving the FlowCreator
engine (full 83-agent catalog) end-to-end from chat, through `invoke_skill`.

    69  ALARM FLOW FORGE   builds `alarm_every_3_hours.flw` (a recurring
                           "every 3 hours, Telegram me that another 3-hour lap
                           passed" workflow) and saves it to the user's Desktop
                           Flows folder. ONE invoke_skill('flow-making', ...) call.

Why this prompt is phrased around `invoke_skill` (not just "create a flow"):
- `list_skills` / `invoke_skill` are ACPX-surface tools (`agent.acpx.ACPX_TOOL_NAMES`);
  with the ACPX toolbar toggle OFF they are filtered out and the skill is invisible.
- The catalog auto-sets the toolbar toggles from the prompt text via
  `tools_dialog.js::classifyPromptModes` — which tags a prompt **ACPX** (⇒ also
  Multi-Turn) only when it literally mentions `invoke_skill` / `list_skills` /
  an `acp_*` tool. Naming `invoke_skill` here makes the catalog click auto-enable
  BOTH **Multi-Turn** and **ACPX**, and pushes the planner to select `invoke_skill`.

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js) enumerates promptName
'prompt-1','prompt-2',... and BREAKS at the first missing slot, so the catalog
must stay a contiguous, gap-free 'prompt-1..N'. Slots 1-68 are occupied (0107
appended the ESP32er demos at 66-68); this APPENDS at 69 with no shift of any
existing prompt. Reverse deletes 69. (MAX_PROMPTS=100.)
"""
from django.db import migrations


# Flow / water banner palette (deep navy -> teal -> aqua -> sea-foam), echoing the
# "flow" theme, with a text-shadow so the white label stays legible over the
# bright sea-foam end.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#06283D 0%,#0E7C86 38%,#1CA7AB 68%,#9BE7D9 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


ALARM_FLOW_FORGE_DEMO = (
    "Tlamatini, ejecuta la demo **ALARM FLOW FORGE**, por favor &mdash; una muestra de una sola llamada del "
    "skill **flow-making** que convierte un objetivo en lenguaje natural en un workflow `.flw` real, "
    "cargable en el canvas, manejando el engine FlowCreator (ya conoce todo el catálogo de 69 agents "
    "y las reglas de conexión). El objetivo: construir un flow llamado "
    "**alarm_every_3_hours.flw** que, cada 3 horas, me envíe un mensaje de Telegram diciendo que "
    "pasó otra vuelta de 3 horas &mdash; y guardarlo en mi carpeta Flows del escritorio. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques &mdash; confía en ellas y ve directo "
    "al Paso 1): (a) marca **Multi-Turn** AND **ACPX** antes de enviar (esta entrada del catálogo "
    "activa las dos automáticamente &mdash; al skill flow-making se llega con **invoke_skill**, un "
    "tool de la superficie ACPX); (b) Ollama está corriendo localmente y el modelo de FlowCreator está disponible "
    "(el skill lo consulta para diseñar el flow); (c) NO escribas el `.flw` tú mismo y "
    "NO uses acp_spawn / chat_agent_executer &mdash; el ÚNICO tool que llamas es **invoke_skill**. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#127754; ALARM FLOW FORGE &#9200;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini flow-making &mdash; objetivo &middot; FlowCreator &middot; .flw</div></div>. "
    "\n\n"
    "Paso 1 (forja el flow): llama a **invoke_skill** con skill_name='flow-making' y "
    "args_json='{\"objective\":\"Every 3 hours, send me a Telegram message telling me that "
    "another 3-hour lap has passed.\",\"out_path\":\"C:/Users/angel/OneDrive/Desktop/Flows/"
    "alarm_every_3_hours.flw\",\"flow_name\":\"alarm_every_3_hours.flw\"}'. El skill copia "
    "la plantilla de FlowCreator a un directorio de runtime aislado, escribe su config, ejecuta FlowCreator "
    "(que diseña un flow de alertas recurrentes de Telegram &mdash; normalmente Starter &rarr; Telegrammer "
    "&rarr; un Sleeper de 3 horas que regresa en bucle, terminado de forma limpia) y convierte el resultado en un "
    "`.flw` de schemaVersion 2. La carpeta Escritorio\\Flows se crea automáticamente si no "
    "exist. "
    "\n\n"
    "Paso 2 (lee el resultado): del return de invoke_skill, captura **flw_path**, "
    "**agent_count** y **connection_count** y repórtalos en una tabla HTML corta. Si el "
    "skill devuelve ok=false (o su log muestra una línea que empieza con `ERROR`), muestra ese "
    "mensaje TAL CUAL y DETENTE &mdash; la causa habitual es 'Cannot reach Ollama' / 'FlowCreator "
    "timed out' (inicia Ollama o pasa otro modelo) &mdash; NO inventes un `.flw`. "
    "\n\n"
    "Paso 3: cierra con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:1px;'>&#9989; FLOW FORJADO</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Ábrelo en el diseñador de ACP (Abrir &#9656; elige el "
    ".flw) &mdash; luego llena el bot-token de Telegrammer y el destinatario `@username` y presiona Iniciar.</div></div>. "
    "Recuérdame que el nodo Telegrammer generado trae credenciales de ejemplo que debo configurar "
    "antes de que la alarma pueda enviar de verdad."
)


_NEW_PROMPTS = (
    (69, ALARM_FLOW_FORGE_DEMO),
)


def add_flow_making_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_flow_making_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0107_add_esp32er_demo_prompts'),
    ]
    operations = [
        migrations.RunPython(add_flow_making_demo_prompt, remove_flow_making_demo_prompt),
    ]
