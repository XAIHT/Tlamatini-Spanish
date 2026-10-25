# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Update obsolete seeded visual-result wording without replacing user prompts.

Created by Angela López Mendoza · @angelahack1 — Tlamatini.

Keep historical migrations intact: later migrations match their exact text.
Only known literal fragments change; prompt identity, ordering and other text
remain intact. The live database is updated by the normal migration lifecycle.
"""
from django.db import migrations


REPLACEMENTS = (
    (
        'merged / partial_interpreter_1_only / partial_interpreter_2_only / merge_fallback_concat',
        'merged / error; los modelos configurados que fallan acumulan un error fatal visible; conserva '
        'los reintentos de Tlamatini y los caminos de recuperación configurados con los mismos modelos; '
        'nunca aceptes observadores parciales ni concatenación cruda como éxito',
    ),
    (
        'Reporta con honestidad si falta audio o hay resultados parciales; enlaza el reporte guardado.',
        'Reporta con honestidad el audio que de verdad falte; enlaza un reporte completo. '
        'Cualquier observador o fusionador configurado que falle rechaza ese intento y acumula un '
        'error fatal visible. Conserva los reintentos de Tlamatini y la recuperación del flow con los '
        'modelos configurados; nunca sustituyas un modelo ni un resumen incompleto.',
    ),
)


def update_prompts(apps, schema_editor):
    prompt = apps.get_model('agent', 'Prompt')
    for old, new in REPLACEMENTS:
        for row in prompt.objects.filter(promptContent__contains=old):
            row.promptContent = row.promptContent.replace(old, new)
            row.save(update_fields=['promptContent'])


class Migration(migrations.Migration):
    dependencies = [('agent', '0209_retire_qwen35_vision_model')]
    operations = [migrations.RunPython(update_prompts, migrations.RunPython.noop)]
