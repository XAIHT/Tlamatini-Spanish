# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Repair shipped catalog identities, execution modes and window-probe calls.

Match the original defaults exactly; keep user edits, IDs, visibility and order.
"""
from importlib import import_module

from django.db import migrations


interactor = import_module('agent.migrations.0218_add_interactor_tool')
torrenter = import_module('agent.migrations.0221_torrenter')
TORRENTER_PROMPT = torrenter.PROMPT.replace(
    'Usa Torrenter', 'Usa chat_agent_torrenter (Torrenter)', 1,
) + '\n\nANTES DE EMPEZAR: marca Multi-Turn y Exec report.'
desktop = import_module('agent.migrations.0095_add_windower_playwrighter_demo_prompts')
director = import_module('agent.migrations.0096_add_director_virtuoso_demo_prompts')
openers = import_module('agent.migrations.0182_add_step_by_step_section_openers')
WINDOW_PROBE_REPAIRS = tuple(
    (content, content.replace('**chat_agent_window_present** (window_title=', '**window_present** (title=')
     .replace('chat_agent_window_present con window_title=', 'window_present con title=')
     .replace('chat_agent_window_present', 'window_present'))
    for content in (desktop.WINDOWER_BASIC_DEMO, desktop.WINDOWER_MEDIUM_DEMO,
                    director.WINDOWER_DIRECTOR_DEMO, openers.DESKTOP_UI)
)


def repair(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    rows = Prompt.objects.using(schema_editor.connection.alias)
    for row in rows.filter(promptName=interactor.PROMPT_NAME, promptContent=interactor.PROMPT):
        rows.filter(pk=row.pk).update(promptName=f'prompt-{row.pk}')
    rows.filter(promptContent=torrenter.PROMPT).update(promptContent=TORRENTER_PROMPT)
    for old, new in WINDOW_PROBE_REPAIRS:
        rows.filter(promptContent=old).update(promptContent=new)


def reverse(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    rows = Prompt.objects.using(schema_editor.connection.alias)
    for row in rows.filter(promptContent=interactor.PROMPT):
        rows.filter(pk=row.pk, promptName=f'prompt-{row.pk}').update(promptName=interactor.PROMPT_NAME)
    rows.filter(promptContent=TORRENTER_PROMPT).update(promptContent=torrenter.PROMPT)
    for old, new in WINDOW_PROBE_REPAIRS:
        rows.filter(promptContent=new).update(promptContent=old)


class Migration(migrations.Migration):
    dependencies = [('agent', '0221_torrenter')]
    operations = [migrations.RunPython(repair, reverse)]
