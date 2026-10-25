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

# Insert a new catalog request at slot #5 (between the current 4th and 5th
# requests). The #prompts-catalog dropdown enumerates prompt-1, prompt-2, … and
# breaks at the first gap, so a true mid-list insert must SHIFT every prompt
# whose id is >= 5 up by one before the new row is written, and shift them back
# down on reverse. promptName stays in lock-step with idPrompt (prompt-<id>).
INSERT_AT = 5

# A Multi-Turn operator request (Java 1.8 -> 17 + Maven project migration). The
# trailing directive line makes the catalog classifier badge it Multi-turn AND
# Exec-report, and clicking the card ticks the Multi-Turn + Exec Report toggles.
NEW_PROMPT_CONTENT = (
    'Tlamatini, partiendo del proyecto que está en el directorio '
    '"Tlamatini/applications/<CurrentProjectFolderName>", **debes crear un nuevo proyecto en '
    '"Tlamatini/applications/<NewProjectFolderName>**" siguiendo estrictamente estos REQUISITOS:\n'
    '- Migrar de Java 1.8 a Java 17\n'
    '- Migrar para usar Maven (- ...\n'
    '- ...----... \n'
    '**Debes crear el directorio del nuevo proyecto como '
    '"Tlamatini/applications/<NewProjectFolderName>"; como ya sabes, el directorio Tlamatini '
    'está pensado para aplicaciones; por lo tanto, a partir de cada elemento de los recursos '
    'originales debes crear/copiar/etc. (según corresponda en cada caso) de '
    '"Tlamatini/applications/<CurrentProjectFolderName>" a '
    '"Tlamatini/applications/<NewProjectFolderName>" para cumplir los requisitos. REQUISITOS '
    'listed.**\n'
    '\n'
    '(modo Multi-Turn: mantén marcadas las casillas Multi-Turn y Exec Report; esta solicitud '
    'requiere verificación por Exec report.) Termina con END-RESPONSE.'
)


def insert_at_5(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    # Shift highest-first so each destination id is always free (no PK clash).
    ids = list(
        Prompt.objects.filter(idPrompt__gte=INSERT_AT)
        .order_by('-idPrompt')
        .values_list('idPrompt', flat=True)
    )
    for pid in ids:
        Prompt.objects.filter(idPrompt=pid).update(
            idPrompt=pid + 1, promptName=f'prompt-{pid + 1}'
        )
    Prompt.objects.update_or_create(
        idPrompt=INSERT_AT,
        defaults={'promptName': f'prompt-{INSERT_AT}', 'promptContent': NEW_PROMPT_CONTENT},
    )


def remove_at_5(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt=INSERT_AT).delete()
    # Shift lowest-first back down to close the gap.
    ids = list(
        Prompt.objects.filter(idPrompt__gt=INSERT_AT)
        .order_by('idPrompt')
        .values_list('idPrompt', flat=True)
    )
    for pid in ids:
        Prompt.objects.filter(idPrompt=pid).update(
            idPrompt=pid - 1, promptName=f'prompt-{pid - 1}'
        )


class Migration(migrations.Migration):
    dependencies = [('agent', '0143_add_mcp_doctor_demo_prompt')]
    operations = [migrations.RunPython(insert_at_5, remove_at_5)]
