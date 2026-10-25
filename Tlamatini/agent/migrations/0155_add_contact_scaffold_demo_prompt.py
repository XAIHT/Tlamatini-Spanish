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


# Catalog-of-prompts SCAFFOLD: lets a user ADD A NEW PERSON to contacts.json by filling
# the [[ ... ]] markers, then sending the prompt. Tlamatini (Multi-Turn) locates
# contacts.json next to config.json (works in BOTH the frozen install and the dev source)
# and appends/updates the contact, preserving existing entries. SAFE for the daily chat
# test: if any marker is still unfilled it changes NOTHING and just asks the user to fill
# it in. Markers use [[ ]] (no angle brackets) so an HTML card preview can't eat them.
DEMO = (
    "Tlamatini, AGREGA UN CONTACTO NUEVO a mi libreta de contactos. Ya llené los campos de abajo. "
    "Un contacto nuevo necesita un NOMBRE más al menos un @username de Telegram OR un número de WhatsApp.\n"
    "\n"
    "CONTACTO NUEVO\n"
    "- name:     [[ ESCRIBE AQUÍ EL NOMBRE COMPLETO ]]\n"
    "- aliases:  [[ OTROS NOMBRES QUE PUEDO USAR, SEPARADOS POR COMAS - OPCIONAL ]]\n"
    "- telegram: [[ SU @username, p. ej. @maria_lopez - OPCIONAL ]]\n"
    "- whatsapp: [[ TELÉFONO CON CÓDIGO DE PAÍS, p. ej. +5215555555555 - OPCIONAL ]]\n"
    "- email:    [[ SU CORREO - OPCIONAL ]]\n"
    "\n"
    "PRIMERO, una revisión de seguridad: si ALGUNA línea de arriba todavía muestra un marcador [[ ... ]] (o sea que no la "
    "llené), NO cambies ningún archivo; sólo dime qué campos llenar y detente. "
    "Continúa sólo cuando el name esté lleno Y al menos uno de telegram o whatsapp esté "
    "lleno. Cualquier campo OPCIONAL que deje como marcador o en blanco, simplemente omítelo.\n"
    "\n"
    "LUEGO, en Multi-Turn, usando tus propios tools:\n"
    "1) Encuentra mi archivo de contactos: usa Globber para contacts.json y elige el ÚNICO que está junto a mi "
    "config.json en la raíz de la aplicación (NO una copia dentro de alguna carpeta "
    "TlamatiniSourceCode). Así funciona igual en la app instalada y en el código fuente de desarrollo.\n"
    "2) Agrega a esta persona al array de contactos SIN quitar ni alterar ningún contacto "
    "existente. Guarda telegram exactamente como @username, y whatsapp como un signo de más, el código "
    "de país y luego el número (por ejemplo +5215555555555). Si ya existe un contacto con el mismo nombre, "
    "ACTUALIZA ese en lugar de duplicarlo. Edita con cuidado: carga el JSON, "
    "agrega o actualiza y luego vuelve a escribirlo con indent=2 para que siga siendo JSON válido.\n"
    "3) Vuelve a leer el archivo y muéstrame la nueva entrada de contacto para confirmar que se guardó.\n"
    "\n"
    "Marca SÓLO la casilla Multi-Turn. Termina con END-RESPONSE."
)


def add_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    if Prompt.objects.filter(promptContent=DEMO).exists():
        return
    next_id = (Prompt.objects.order_by('-idPrompt').values_list('idPrompt', flat=True).first() or 0) + 1
    Prompt.objects.update_or_create(
        idPrompt=next_id,
        defaults={'promptName': f'prompt-{next_id}', 'promptContent': DEMO},
    )


def remove_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(promptContent=DEMO).delete()


class Migration(migrations.Migration):
    dependencies = [('agent', '0154_add_instant_messaging_doctor_demo_prompt')]
    operations = [migrations.RunPython(add_demo_prompt, remove_demo_prompt)]
