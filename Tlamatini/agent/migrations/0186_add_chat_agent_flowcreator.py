# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#   Created by  Angela López Mendoza · @angelahack1
# ═══════════════════════════════════════════════════════════════════
"""FlowCreator becomes callable from CHAT: prompt in -> .flw file out.

Angela, 2026-07-22: "I JUST NEED A FLOWCREATOR AGENT WRAPPED TO CREATE .FLW
FILES BASED IN A PROMPT ... INPUT: A PROMPT, OUTPUT: A SIMPLE .flw FILE".

Until now FlowCreator was canvas-only: the node's Save button POSTed to
execute_flowcreator/, and the browser JS rendered flow_result.json onto the
canvas. There was no way to say "create me a flow that does X" in chat and get
a file back.

This migration seeds the two DB rows the wrapped tool needs. The code side is:
  * chat_agent_registry.py  -> ChatWrappedAgentSpec(key="flowcreator", ...)
  * agents/flowcreator/flowcreator.py -> now ALSO writes a real .flw (via the
    vendored result_to_flw.convert) and exits NON-ZERO on failure
  * agents/flowcreator/result_to_flw.py -> vendored converter (pool agents can
    never import agent.*, so it ships inside the template dir)

WHY THE EXIT-CODE CHANGE MATTERED: chat_agent_runtime maps exit 0 -> "completed".
flowcreator.py used to `sys.exit(0)` on EVERY path — including "no prompt",
"Ollama unreachable" and "unparseable response" — so a wrapped run that created
nothing would have been reported to the user as a SUCCESS, with a green Exec
Report row. The canvas path is unaffected: check_flowcreator_result_view keys
off the PID file + flow_result.json, never the exit code.

Rows seeded here:
  1. Tool row 'Chat-Agent-FlowCreator' — the wrapper half of the dual enable
     gate (the Agent row 'FlowCreator' already exists from migration 0031), so
     the tool is toggleable under Configure Mcps/Tools.
  2. Catalog prompt — MANDATORY for every Multi-Turn agent. Appended at the
     next free idPrompt (never renumber) with sort_rank 85 so it lands right
     after the ALARM FLOW FORGE demo (#33, rank 80) inside Agents & Flows.
"""
from django.db import migrations

TOOL_DESCRIPTION = 'Chat-Agent-FlowCreator'

DEMO_PROMPT = (
    "Tlamatini, usa <b>FlowCreator</b> para CREARME UN FLOW, por favor - quiero un archivo "
    "<code>.flw</code> real que pueda abrir en el Agentic Control Panel.<br><br>"
    "LLENA ESTO - reemplaza el texto dentro de los corchetes [[ ]]:<br>"
    "- QUÉ DEBE HACER EL FLOW: [[ DESCRIBE EL OBJETIVO EN PALABRAS SENCILLAS - incluye los "
    "paths, patterns, destinatarios y umbrales reales. OPCIONAL, predeterminado: monitorear el log del "
    "servidor GlassFish en C:/glassfish/domains/domain1/logs/server.log y, cuando aparezca una línea ERROR, "
    "resumirla y enviarme ese resumen por Telegram ]]<br>"
    "- NOMBRE DE ARCHIVO: [[ EL NOMBRE DEL ARCHIVO .flw - OPCIONAL, predeterminado: my_flow.flw ]]<br><br>"
    "Si dejé los corchetes sin tocar, sólo usa los valores predeterminados de arriba - NO me preguntes, adelante.<br><br>"
    "Marca SÓLO la casilla <b>Multi-Turn</b>. Usa SÓLO el tool <code>chat_agent_flowcreator</code> "
    ": llámalo con <code>prompt='&lt;el objetivo de arriba, completo&gt;'</code> y "
    "<code>flow_filename='&lt;el nombre de archivo de arriba&gt;'</code>. Pasa TODO mi objetivo en "
    "<code>prompt</code> - el diseñador de flows sólo ve ese texto, así que cualquier path o destinatario que "
    "dejes fuera faltará en el flow.<br><br>"
    "Cuando termine, lee el bloque <code>INI_SECTION_FLOWCREATOR</code> y dime: el "
    "<code>status</code>, el <b><code>flw_path</code> completo</b> (para que pueda abrir el archivo), el "
    "<code>agent_count</code> y <code>connection_count</code>, y luego lista los agents que "
    "eligió en orden de ejecución, con una línea para cada uno explicando por qué está ahí. Si "
    "<code>status</code> es <code>error</code>, dilo con claridad y cita el mensaje - NO "
    "afirmes que se creó un flow. Termina con END-RESPONSE."
)


def add_rows(apps, schema_editor):
    Tool = apps.get_model('agent', 'Tool')
    Prompt = apps.get_model('agent', 'Prompt')

    if not Tool.objects.filter(toolDescription=TOOL_DESCRIPTION).exists():
        next_id = (Tool.objects.order_by('-idTool').values_list('idTool', flat=True).first() or 0) + 1
        Tool.objects.create(
            idTool=next_id,
            toolName=f'tool-{next_id}',
            toolDescription=TOOL_DESCRIPTION,
            toolContent='true',
        )

    if not Prompt.objects.filter(promptContent=DEMO_PROMPT).exists():
        next_pid = (Prompt.objects.order_by('-idPrompt').values_list('idPrompt', flat=True).first() or 0) + 1
        Prompt.objects.update_or_create(
            idPrompt=next_pid,
            defaults={
                'promptName': f'prompt-{next_pid}',
                'promptContent': DEMO_PROMPT,
                'category': 'agents_flows',
                'hidden': False,
                # 33 (ALARM FLOW FORGE) sits at rank 80; this is its natural sibling.
                'sort_rank': 85,
            },
        )


def remove_rows(apps, schema_editor):
    apps.get_model('agent', 'Tool').objects.filter(toolDescription=TOOL_DESCRIPTION).delete()
    apps.get_model('agent', 'Prompt').objects.filter(promptContent=DEMO_PROMPT).delete()


class Migration(migrations.Migration):

    dependencies = [('agent', '0185_standardize_prompt_params_batch3')]

    operations = [migrations.RunPython(add_rows, remove_rows)]
