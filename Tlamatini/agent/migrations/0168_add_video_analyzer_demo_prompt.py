# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""One Catalog-of-Prompts example for the new Video-Analyzer agent (#84).

It drives the whole record-then-judge path SAFELY (no special hardware): record a
short webcam clip with Camcorder, then have Video-Analyzer return a verdict on
whether something moved — the same loop that verifies an STM32-driven servo in
Robotic-Loop-Training.

Appended at MAX+1 (contiguity contract: the #prompts-catalog dropdown enumerates
prompt-1..N and BREAKS at the first gap, so we never renumber and never leave a
hole; MAX_PROMPTS=256). The wording ("Multi-Turn checkbox" + "chat_agent_...")
makes the catalog mode-classifier light up Multi-Turn.
"""
from django.db import migrations


VIDEO_ANALYZER_DEMO_PROMPT = (
    "Tlamatini, ejecuta la **VIDEO-ANALYZER ROBOTIC-LOOP DEMO**, por favor — marca SÓLO la "
    "casilla Multi-Turn. PASO 1: graba un clip corto de 6 segundos de lo que vea la webcam con "
    "chat_agent_camcorder (capture_mode='video', video_duration_seconds=6) — mueve la mano o "
    "un objeto frente a la cámara mientras graba; el resultado trae un output_path de nivel "
    "superior. PASO 2: evalúa ese clip con chat_agent_video_analyzer con "
    "video_pathfilenames='<the output_path from STEP 1>' y expected_motion='a hand or object "
    "visibly moves across the frame' y num_frames=10 — primero corre una compuerta de movimiento "
    "DETERMINISTA con OpenCV (sin movimiento -> FAIL_NO_MOTION sin llamar a ningún modelo), luego interpreter_model_1 "
    "(qwen3-vl:235b-cloud) and interpreter_model_2 (jcyhsiao/qwen3.5cloud:latest) IN PARALLEL on two dedicated "
    "Ollama connections, then fuses them with merging_model (glm-5.3:cloud). STEP 3: report the "
    "veredicto (PASS_OK / FAIL_NO_MOTION / FAIL_WRONG_MOTION / UNCLEAR), la confianza y el "
    "motion_score determinista, y luego explica en UNA línea cómo este mismo loop verifica un "
    "servo manejado por STM32 (STM32er flashea el firmware -> Camcorder graba la placa -> Video-Analyzer "
    "juzga el movimiento -> un Forker se ramifica según TLM_VERDICT:: para reprogramar o terminar). Usa SÓLO "
    "chat_agent_camcorder y chat_agent_video_analyzer. Termina con END-RESPONSE."
)

_NEW_PROMPTS = (VIDEO_ANALYZER_DEMO_PROMPT,)


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
    dependencies = [('agent', '0167_add_chat_agent_video_analyzer_tool')]
    operations = [migrations.RunPython(add_prompts, remove_prompts)]
