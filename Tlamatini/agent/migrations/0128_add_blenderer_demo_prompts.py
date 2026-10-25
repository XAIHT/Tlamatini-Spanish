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
Seed a Catalog-of-Prompts demo for **Blenderer** — Tlamatini's BLENDER bridge —
run through the wrapped **chat_agent_blenderer** Multi-Turn tool. This is the
MANDATORY catalog prompt every Multi-Turn-capable agent must ship (CLAUDE.md
directive / create_new_agent.md Step 7.8 / tlamatini-agent-creation Phase 19).

    75  BLENDER FORGE   basic   create a Suzanne (monkey) -> give it a colour ->
                                render a still to the Temp dir -> report
                                version/object/render-path + status.

SAFE to run repeatedly (the daily chat test may execute it): it only adds one
object + one material to the live scene and renders a small still under the app
Temp dir. Blenderer talks to the OFFICIAL Blender MCP add-on socket
(localhost:9876); if Blender is not running / the add-on server is not started,
chat_agent_blenderer returns status `error` with an actionable connection
message (a documented degraded mode, NOT a crash) — the prompt records that
verbatim and finishes gracefully.

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js) enumerates promptName
'prompt-1','prompt-2',... and BREAKS at the first missing slot, so the catalog
must stay a contiguous, gap-free 'prompt-1..N'. Slots 1-74 are occupied (0125
appended the Whisperer demo at 74); this APPENDS at 75 with no shift of any
existing prompt. Reverse deletes 75. (MAX_PROMPTS=100.)
"""
from django.db import migrations


# Blenderer banner palette — mirrors the ``.canvas-item.blenderer-agent``
# gradient (deep blue -> Blender blue -> Blender orange -> warm amber).
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#15334f 0%,#2a6fb3 33%,#ea7600 66%,#f7b733 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


BLENDER_FORGE_DEMO = (
    "Tlamatini, ejecuta la demo **BLENDER FORGE**, por favor &mdash; una muestra básica de tu propio "
    "puente de modelado 3D, controlado por completo desde el chat a través del tool wrapper **chat_agent_blenderer**, "
    "que habla el protocolo de socket del add-on OFICIAL de Blender MCP (TÚ ERES el cliente &mdash; "
    "no hace falta un cliente LLM externo). "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques &mdash; ve directo al Paso 1): "
    "(a) marca SÓLO la casilla **Multi-Turn** antes de enviar (NO se necesita ACPX &mdash; "
    "chat_agent_blenderer es el ÚNICO tool que puedes usar; no uses chat_agent_executer / "
    "chat_agent_pythonxer ni tools de ACPX); (b) se espera que Blender esté corriendo con el add-on Blender MCP "
    "activado, con 'Online access' encendido y el servidor iniciado &mdash; pero si NO está accesible, "
    "chat_agent_blenderer devuelve status `error` con un mensaje de conexión claro (un modo degradado "
    "documentado, NO un error): regístralo tal cual, OMITE los pasos restantes de Blender y ve "
    "directo al banner de cierre. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#127912; BLENDER FORGE &#129412;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini Blenderer &mdash; chat de entrada, 3D de salida</div></div>. "
    "\n\n"
    "Paso 1 (prueba): llama a **chat_agent_blenderer** con el request \"Run Blender command with "
    "command='ping'\". Del bloque INI_SECTION_BLENDERER del log_excerpt de la ejecución captura status "
    "(ok | error) y, si es ok, el blender_version_string y la scene. Si status es error, anota el "
    "mensaje y SALTA al Paso 5. "
    "\n\n"
    "Paso 2 (modela): llama a **chat_agent_blenderer** con el request \"Run Blender command with "
    "command='create_object' and params.type='monkey' and params.name='ForgeSuzanne' and "
    "params.location=[0,0,2]\". Captura el nombre del objeto creado de la respuesta. "
    "\n\n"
    "Paso 3 (color): llama a **chat_agent_blenderer** con el request \"Run Blender command with "
    "command='set_material' and params.object_name='ForgeSuzanne' and params.color=[0.92,0.46,0.0] "
    "and params.material='ForgeOrange'\". Captura el nombre del material. "
    "\n\n"
    "Paso 4 (render): llama a **chat_agent_blenderer** con el request \"Run Blender command with "
    "command='render'\" (sin output_path &mdash; Blenderer pone el .png de forma predeterminada en la Temp de la app). "
    "Del bloque INI_SECTION_BLENDERER captura el path del archivo renderizado y si existe. "
    "\n\n"
    "Paso 5: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Blender Forge &mdash; Reporte de construcción</strong>' y con las columnas <em>paso</em>, <em>command</em>, "
    "<em>status</em>, <em>detalle</em> &mdash; una fila por cada llamada a chat_agent_blenderer que hiciste, cada "
    "valor tal cual de su bloque INI_SECTION_BLENDERER (NO lo reclasifiques). Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a), tono verde para status ok, tono rojo para status error. "
    "\n\n"
    "Paso 6: cierra con un banner HTML que reutilice el estilo del Paso 0 y muestre, en letras grandes, "
    "'&#9989; FORJADO' (todos los pasos de Blender devolvieron ok &mdash; muestra el path renderizado) o "
    "'&#9881;&#65039; BLENDER INACCESIBLE' (el Paso 1 dio error &mdash; cita el mensaje de conexión y "
    "el arreglo de una línea 'activa el add-on Blender MCP, enciende Online access e inicia el servidor'), "
    "y debajo una métrica de una línea 'versión: <blender_version_string> &middot; objeto: "
    "<created> &middot; render: <rendered path>'. "
    "Termina con END-RESPONSE."
)


_NEW_PROMPTS = (
    (75, BLENDER_FORGE_DEMO),
)


def add_blenderer_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_blenderer_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0127_add_chat_agent_blenderer_tool'),
    ]

    operations = [
        migrations.RunPython(add_blenderer_demo_prompt, remove_blenderer_demo_prompt),
    ]
