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


MCP_DOCTOR_DEMO = (
    "Tlamatini, ejecuta la demo **MCP DOCTOR**, por favor &mdash; un diagnóstico seguro del catálogo "
    "de External MCPs, controlado por completo a través del tool wrapper **chat_agent_mcp_doctor**. "
    "Marca SÓLO la casilla **Multi-Turn** antes de enviar. Usa SÓLO "
    "chat_agent_mcp_doctor; no uses chat_agent_executer, chat_agent_pythonxer "
    "ni acp_spawn. "
    "\\n\\n"
    "Paso 0: abre con un banner HTML: "
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#0F3D3E 0%,#1E7B73 33%,#E0A83A 66%,#FFF2C6 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.45);'>"
    "<h2 style='margin:0;letter-spacing:2px;'>MCP DOCTOR</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Catálogo de External MCPs &middot; runtime &middot; transport &middot; disponibilidad de la configuración</div></div>. "
    "\\n\\n"
    "Paso 1: llama a **chat_agent_mcp_doctor** con el request "
    "\"Run MCP Doctor with mode='catalog'\". Lee el JSON que devuelve y el "
    "bloque INI_SECTION_MCP_DOCTOR del log_excerpt. Captura status, server_key, "
    "transport, runtime, supported, catalog_path y el response_body. "
    "\\n\\n"
    "Paso 2: muestra una tabla HTML compacta con class='exec-report-table' titulada "
    "'<strong>MCP Doctor &mdash; Disponibilidad del catálogo</strong>' y con las columnas "
    "<em>campo</em> y <em>valor</em>. Incluye al menos catalog_path, status, "
    "server_key, transport, runtime, supported y la primera oración del siguiente paso "
    "del response body. "
    "\\n\\n"
    "Paso 3: cierra con una oración que le diga al usuario la siguiente acción de configuración de MCP. "
    "Termina con END-RESPONSE."
)

_NEW_PROMPTS = (
    (81, MCP_DOCTOR_DEMO),
)


def add_mcp_doctor_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_mcp_doctor_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0142_add_chat_agent_mcp_doctor_tool'),
    ]

    operations = [
        migrations.RunPython(add_mcp_doctor_demo_prompt, remove_mcp_doctor_demo_prompt),
    ]
