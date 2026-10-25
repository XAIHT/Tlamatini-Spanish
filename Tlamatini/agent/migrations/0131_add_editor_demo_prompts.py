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
Seed a Catalog-of-Prompts demo for **Editor** - Tlamatini's surgical in-place
file editor - run through the wrapped **chat_agent_editor** Multi-Turn tool.
Mandatory catalog prompt every Multi-Turn-capable agent must ship (CLAUDE.md
directive / create_new_agent.md Step 7.8 / tlamatini-agent-creation Phase 19).

    76  SURGICAL EDIT   basic   File-Creator seeds a throwaway file under the app
                                Temp dir -> chat_agent_editor replaces one exact
                                line -> a second edit proves the 'noop' path ->
                                report status/replacements.

SAFE to run repeatedly (the daily chat test may execute it): it only writes a
throwaway file under the app Temp directory and edits THAT file - no existing
project file is ever touched.

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js) enumerates promptName
'prompt-1','prompt-2',... and BREAKS at the first missing slot, so the catalog
must stay a contiguous, gap-free 'prompt-1..N'. Slots 1-75 are occupied (0128
appended the Blenderer demo at 75); this APPENDS at 76 with no shift of any
existing prompt. Reverse deletes 76. (MAX_PROMPTS=100.)
"""
from django.db import migrations


# Editor banner palette - mirrors the ``.canvas-item.editor-agent`` emerald gradient.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#022c22 0%,#064e3b 33%,#10b981 66%,#6ee7b7 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


SURGICAL_EDIT_DEMO = (
    "Tlamatini, ejecuta la demo **SURGICAL EDIT**, por favor &mdash; una muestra básica de tu propio "
    "editor de archivos quirúrgico, controlado desde el chat a través del tool wrapper **chat_agent_editor**: el "
    "operador de buscar y reemplazar que cambia un archivo intercambiando una cadena EXACTA SIN reescribir "
    "todo el archivo. Marca SÓLO la casilla **Multi-Turn** antes de enviar. Usa SÓLO "
    "chat_agent_file_creator (para sembrar el archivo de prueba) y chat_agent_editor (para editarlo). "
    "\\n\\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#9999;&#65039; EDICIÓN QUIRÚRGICA</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini Editor &mdash; buscar, reemplazar, byte-exacto</div></div>. "
    "\\n\\n"
    "Paso 1 (semilla): llama a **chat_agent_file_creator** con el request \"Run File Creator with "
    "file_path='<TEMP>/editor_demo.txt' and content='editor demo file -- status: draft'\", donde "
    "<TEMP> es tu directorio Temp de la app (el path absoluto que te da el system prompt). "
    "\\n\\n"
    "Paso 2 (edita): llama a **chat_agent_editor** con el request \"Run Editor with "
    "file_path='<TEMP>/editor_demo.txt', old_string='status: draft', new_string='status: final', "
    "replace_all=false\". Del bloque INI_SECTION_EDITOR del log_excerpt de la ejecución captura el "
    "status (edited | not_found | not_unique | noop | error) y el conteo replacements. "
    "\\n\\n"
    "Paso 3 (demuestra el no-op): llama a **chat_agent_editor** OTRA VEZ con el request \"Run Editor with "
    "file_path='<TEMP>/editor_demo.txt', old_string='status: draft', new_string='status: final', "
    "replace_all=false\" y confirma que ahora reporta status 'not_found' (la línea draft ya no está &mdash; "
    "prueba de que la primera edición sí se aplicó). "
    "\\n\\n"
    "Paso 4: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Surgical Edit &mdash; Reporte</strong>' y con las columnas <em>paso</em>, <em>old_string</em>, "
    "<em>new_string</em>, <em>status</em>, <em>replacements</em> &mdash; una fila por cada llamada a chat_agent_editor "
    "que hiciste, cada valor tal cual de su bloque INI_SECTION_EDITOR (NO lo reclasifiques). Celdas del "
    "cuerpo claras (background:#ffffff;color:#0f172a), tono verde para status edited, gris para not_found. "
    "\\n\\n"
    "Paso 5: cierra con un banner HTML que reutilice el estilo del Paso 0 y muestre, en letras grandes, "
    "'&#9989; EDITADO' (el Paso 2 devolvió status edited) o '&#10060; NO SE PUDO EDITAR' (cita el status y el "
    "mensaje), y debajo una métrica de una línea 'archivo: <TEMP>/editor_demo.txt &middot; replacements: <n>'. "
    "Termina con END-RESPONSE."
)


_NEW_PROMPTS = (
    (76, SURGICAL_EDIT_DEMO),
)


def add_editor_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_editor_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0130_add_chat_agent_editor_tool'),
    ]

    operations = [
        migrations.RunPython(add_editor_demo_prompt, remove_editor_demo_prompt),
    ]
