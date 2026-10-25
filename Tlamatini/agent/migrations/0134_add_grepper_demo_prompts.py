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
Seed a Catalog-of-Prompts demo for **Grepper** - Tlamatini's read-only regex
content searcher - run through the wrapped **chat_agent_grepper** Multi-Turn tool.
Mandatory catalog prompt (CLAUDE.md / create_new_agent.md Step 7.8 /
tlamatini-agent-creation Phase 19).

    77  CONTENT HUNT   basic   File-Creator seeds 2 throwaway files under the app
                               Temp dir -> chat_agent_grepper finds a regex across
                               them -> report matches/files_searched.

SAFE to run repeatedly: it only writes two throwaway files under the app Temp
directory and searches THAT directory (read-only). Slots 1-76 are occupied (0131
appended the Editor demo at 76); this APPENDS at 77 with no renumber. Reverse
deletes 77. (MAX_PROMPTS=100.)
"""
from django.db import migrations


# Grepper banner palette - mirrors the ``.canvas-item.grepper-agent`` indigo gradient.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#0b1d3a 0%,#1e3a8a 33%,#3b82f6 66%,#93c5fd 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


CONTENT_HUNT_DEMO = (
    "Tlamatini, ejecuta la demo **CONTENT HUNT**, por favor &mdash; una muestra básica de tu propio "
    "buscador de contenido por regex, controlado desde el chat a través del tool wrapper **chat_agent_grepper** "
    "(el equivalente de grep / find-in-files que devuelve las líneas que coinciden como file:line:match). "
    "Marca SÓLO la casilla **Multi-Turn** antes de enviar. Usa SÓLO chat_agent_file_creator "
    "(para sembrar los archivos de prueba) y chat_agent_grepper (para buscar en ellos). "
    "\\n\\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128269; CAZA DE CONTENIDO</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini Grepper &mdash; regex de entrada, file:line:match de salida</div></div>. "
    "\\n\\n"
    "Paso 1 (semilla A): llama a **chat_agent_file_creator** con el request \"Run File Creator with "
    "file_path='<TEMP>/grepper_demo/a.txt' and content='alpha TODO_MARK one'\", donde <TEMP> es "
    "tu directorio Temp (el path absoluto que te da el system prompt). "
    "\\n\\n"
    "Paso 2 (semilla B): llama a **chat_agent_file_creator** con el request \"Run File Creator with "
    "file_path='<TEMP>/grepper_demo/b.txt' and content='beta TODO_MARK two'\". "
    "\\n\\n"
    "Paso 3 (busca): llama a **chat_agent_grepper** con el request \"Run Grepper with "
    "pattern='TODO_MARK', path='<TEMP>/grepper_demo', glob='*.txt', output_mode='content'\". Del "
    "bloque INI_SECTION_GREPPER del log_excerpt de la ejecución captura status (matches | no_matches | "
    "not_found | error), matches y files_searched, además de las líneas file:line:match del body. "
    "\\n\\n"
    "Paso 4: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Content Hunt &mdash; Coincidencias</strong>' y con las columnas <em>archivo</em>, <em>línea</em>, "
    "<em>texto</em> &mdash; una fila por cada línea file:line:match del body de INI_SECTION_GREPPER (NO la "
    "reclasifiques). Celdas del cuerpo claras (background:#ffffff;color:#0f172a). "
    "\\n\\n"
    "Paso 5: cierra con un banner HTML que reutilice el estilo del Paso 0 y muestre, en letras grandes, "
    "'&#9989; ENCONTRÉ <matches>' (status matches) o '&#128269; SIN COINCIDENCIAS' (status no_matches), y "
    "debajo una métrica de una línea 'pattern: TODO_MARK &middot; archivos buscados: <files_searched>'. "
    "Termina con END-RESPONSE."
)


_NEW_PROMPTS = (
    (77, CONTENT_HUNT_DEMO),
)


def add_grepper_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_grepper_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0133_add_chat_agent_grepper_tool'),
    ]

    operations = [
        migrations.RunPython(add_grepper_demo_prompt, remove_grepper_demo_prompt),
    ]
