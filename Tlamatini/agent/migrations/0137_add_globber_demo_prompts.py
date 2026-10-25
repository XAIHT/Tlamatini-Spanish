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
Seed a Catalog-of-Prompts demo for **Globber** - Tlamatini's read-only filename
pattern searcher - run through the wrapped **chat_agent_globber** Multi-Turn tool.
Mandatory catalog prompt (CLAUDE.md / create_new_agent.md Step 7.8 /
tlamatini-agent-creation Phase 19).

    78  FILE FINDER   basic   File-Creator seeds 2 throwaway files in a Temp subdir
                              -> chat_agent_globber lists them by glob (newest-first)
                              -> report matches.

SAFE to run repeatedly: it only writes two throwaway files under the app Temp
directory and globs THAT directory (read-only). Slots 1-77 are occupied (0134
appended the Grepper demo at 77); this APPENDS at 78. Reverse deletes 78.
(MAX_PROMPTS=100.)
"""
from django.db import migrations


# Globber banner palette - mirrors the ``.canvas-item.globber-agent`` violet gradient.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#1e0a3c 0%,#4c1d95 33%,#8b5cf6 66%,#c4b5fd 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


FILE_FINDER_DEMO = (
    "Tlamatini, ejecuta la demo **FILE FINDER**, por favor &mdash; una muestra básica de tu propio "
    "buscador de archivos por pattern, controlado desde el chat a través del tool wrapper **chat_agent_globber** "
    "(el equivalente de glob / find-files que lista los paths de archivo que coinciden, del más nuevo al más viejo). Marca SÓLO "
    "la casilla **Multi-Turn** antes de enviar. Usa SÓLO chat_agent_file_creator (para sembrar los "
    "archivos de prueba) y chat_agent_globber (para listarlos). "
    "\\n\\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128193; BUSCADOR DE ARCHIVOS</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini Globber &mdash; glob de entrada, paths de archivo de salida</div></div>. "
    "\\n\\n"
    "Paso 1 (semilla A): llama a **chat_agent_file_creator** con el request \"Run File Creator with "
    "file_path='<TEMP>/globber_demo/one.txt' and content='first file'\", donde <TEMP> es tu directorio "
    "Temp (el path absoluto que te da el system prompt). "
    "\\n\\n"
    "Paso 2 (semilla B): llama a **chat_agent_file_creator** con el request \"Run File Creator with "
    "file_path='<TEMP>/globber_demo/sub/two.txt' and content='second file'\". "
    "\\n\\n"
    "Paso 3 (busca): llama a **chat_agent_globber** con el request \"Run Globber with "
    "pattern='**/*.txt', path='<TEMP>/globber_demo', sort_by='mtime'\". Del "
    "bloque INI_SECTION_GLOBBER del log_excerpt de la ejecución captura status (matches | no_matches | "
    "not_found | error) y matches, además de los paths de archivo del body (del más nuevo primero). "
    "\\n\\n"
    "Paso 4: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>File Finder &mdash; Coincidencias</strong>' y con las columnas <em>#</em>, <em>path</em> &mdash; "
    "una fila por cada path de archivo del body de INI_SECTION_GLOBBER, en el orden en que se devolvieron. Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a). "
    "\\n\\n"
    "Paso 5: cierra con un banner HTML que reutilice el estilo del Paso 0 y muestre, en letras grandes, "
    "'&#9989; ENCONTRÉ <matches>' (status matches) o '&#128193; NINGUNO' (status no_matches), y "
    "debajo una métrica de una línea 'pattern: **/*.txt &middot; coincidencias: <matches>'. "
    "Termina con END-RESPONSE."
)


_NEW_PROMPTS = (
    (78, FILE_FINDER_DEMO),
)


def add_globber_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_globber_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0136_add_chat_agent_globber_tool'),
    ]

    operations = [
        migrations.RunPython(add_globber_demo_prompt, remove_globber_demo_prompt),
    ]
