# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""One Catalog-of-Prompts example for the upgraded TRIPLE-MODEL Image-Interpreter
(2026-07-04): interpreter_model_1 (jcyhsiao/qwen3.5cloud:latest) + interpreter_model_2
(gemma4:cloud) run IN PARALLEL on two dedicated Ollama connections, a BARRIER
waits for BOTH interpretations, then merging_model (glm-5.3:cloud) fuses them
into one definitive report.

Appended at MAX+1 (contiguity contract: the #prompts-catalog dropdown
enumerates prompt-1..N and BREAKS at the first gap, so we never renumber and
never leave a hole; MAX_PROMPTS=256). The wording ("Multi-Turn checkbox" +
"chat_agent_...") makes the catalog mode-classifier light up Multi-Turn.

The task is SAFE to run repeatedly (the daily chat test may execute it): one
silent screenshot + one read-only vision analysis, no destructive operations.
"""
from django.db import migrations


TRIPLE_MODEL_DEMO_PROMPT = (
    "Tlamatini, ejecuta la demo **TRIPLE MODELO DE IMAGE-INTERPRETER**, por favor — marca SÓLO la casilla "
    "Multi-Turn. PASO 1: toma un screenshot silencioso con chat_agent_shoter (sin ventana de "
    "visor — el resultado trae un output_path de nivel superior). PASO 2: pásale ese PNG guardado a "
    "chat_agent_image_interpreter con images_pathfilenames='<the output_path from PASO 1>' y "
    "prompt_user='Inventory every visible GUI element with its position (% of image), size (%), "
    "colors and exact text; if any person is visible, describe them exhaustively and hypothesize who "
    "they may be, using the file name as a clue.' — el agent ejecutará interpreter_model_1 "
    "(jcyhsiao/qwen3.5cloud:latest) e interpreter_model_2 (gemma4:cloud) EN PARALELO en dos conexiones de Ollama dedicadas, "
    "esperará en el BARRIER hasta que lleguen AMBAS interpretaciones y luego las fusionará con "
    "merging_model (glm-5.3:cloud). PASO 3: reporta los 5 hallazgos más interesantes del "
    "reporte fusionado y di qué `status` traía el bloque INI_SECTION_IMAGE_INTERPRETER "
    "(merged / partial_interpreter_1_only / partial_interpreter_2_only / merge_fallback_concat). "
    "Usa SÓLO chat_agent_shoter y chat_agent_image_interpreter. Termina con END-RESPONSE."
)

_NEW_PROMPTS = (TRIPLE_MODEL_DEMO_PROMPT,)


def add_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for content in _NEW_PROMPTS:
        if Prompt.objects.filter(promptContent=content).exists():
            continue
        next_id = (Prompt.objects.order_by('-idPrompt').values_list('idPrompt', flat=True).first() or 0) + 1
        Prompt.objects.update_or_create(
            idPrompt=next_id,
            defaults={'promptName': f'prompt-{next_id}', 'promptContent': content},
        )


def remove_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(promptContent__in=list(_NEW_PROMPTS)).delete()


class Migration(migrations.Migration):
    dependencies = [('agent', '0164_dedup_zavuerer_setup_wizards')]
    operations = [migrations.RunPython(add_prompts, remove_prompts)]
