# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Append Video-Analyzer audio-track and summary examples to Media & Voice.

Created by Angela López Mendoza · @angelahack1 — Tlamatini.
"""
from django.db import migrations


PROMPTS = (
    (125, 35, 'transcription',
     'Transcribe cada pista de audio del video seleccionado. Conserva los timestamps y los índices de pista; '
     'devuelve la transcripción, los idiomas detectados, audio_status y los paths de los artefactos. No captures ningún micrófono.'),
    (126, 37, 'summary',
     'Resume el video seleccionado usando el habla y evidencia visual con timestamps. Incluye un resumen general, cronología, '
     'texto legible en pantalla, datos clave, pasos demostrados, decisiones, action items y limitaciones de '
     'cobertura. Reporta con honestidad si falta audio o hay resultados parciales; enlaza el reporte guardado.'),
)


def add_prompts(apps, schema_editor):
    prompt = apps.get_model('agent', 'Prompt')
    for pid, rank, mode, task in PROMPTS:
        content = (
            f'Video-Analyzer — {mode}\n\n'
            '[[ VIDEO FILE — REQUERIDO: path a un video existente ]]\n\n'
            'Si VIDEO FILE está sin llenar, pide su path antes de ejecutar. Nunca inventes un archivo.\n\n'
            f'{task}\nUsa chat_agent_video_analyzer con analysis_type="{mode}", '
            'video_pathfilenames apuntando a VIDEO FILE y audio_tracks="all". '
            'Usa chat_agent_run_status/log para esperar a que termine e inspeccionar el resultado. '
            'No uses los tokens de veredicto de robótica para esta tarea. '
            '\nPRE-FLIGHT: marca sólo Multi-Turn y Exec report. Termina con END-RESPONSE.'
        )
        prompt.objects.update_or_create(idPrompt=pid, defaults={
            'promptName': f'prompt-{pid}', 'promptContent': content,
            'category': 'media_voice', 'sort_rank': rank,
        })


def remove_prompts(apps, schema_editor):
    apps.get_model('agent', 'Prompt').objects.filter(idPrompt__in=[125, 126]).delete()


class Migration(migrations.Migration):
    dependencies = [('agent', '0206_qwen35_cloud_model_tag_rename')]
    operations = [migrations.RunPython(add_prompts, remove_prompts)]
