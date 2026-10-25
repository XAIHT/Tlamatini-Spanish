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


# REDESIGN of the messaging demo prompts (Telegrammer + Whatsapper).
#
# The first version hardcoded `contact_name='me'`, which confused users: they
# edited the story ("send to Cosapi") but the actual recipient stayed 'me', so
# the message went to themselves. These rewrites put a CLEAR, fill-in-the-blank
# [[ ... ]] placeholder for the TARGET CONTACT NAME, and state plainly that the
# name must already be saved in the contacts book (contacts.json).
#
# Style mirrors the proven 0155 contact-scaffold prompt: while the [[ ... ]]
# brackets are still present (unfilled), the agent STOPS and sends nothing — so
# these remain SAFE for the daily chat regression. [[ ]] (no angle brackets) so
# an HTML card preview can't eat the markers.

TG_AS_ME = (
    "Tlamatini, manda UN mensaje de Telegram DESDE MI PROPIA cuenta (como yo, NO como el bot).\n"
    "\n"
    "LLENA ESTOS CAMPOS — reemplaza el texto dentro de los corchetes [[ ]]:\n"
    "- ENVIAR A:  [[ ESCRIBE AQUÍ EL NOMBRE DEL CONTACTO — esta persona YA DEBE estar guardada "
    "en mi libreta de contactos (contacts.json) con un @username de Telegram ]]\n"
    "- MENSAJE:  [[ ESCRIBE AQUÍ EL MENSAJE QUE QUIERES MANDAR ]]\n"
    "\n"
    "PRIMERO, REVISIÓN DE SEGURIDAD: si la línea ENVIAR A todavía muestra los corchetes [[ "
    "]] (no la he llenado), NO mandes nada — sólo dime que escriba un nombre de contacto que exista "
    "en mi libreta de contactos, y detente. Si escribí un nombre que NO está en contacts.json, NO adivines "
    "ni inventes un handle — dime que ese nombre no está en mis contactos para que lo agregue primero, y detente.\n"
    "\n"
    "LUEGO mándalo usando SOLO el tool chat_agent_telegrammer con mode='send', provider='me' "
    "(así sale desde MI PROPIA cuenta de Telegram — la primera vez se abre una ventana de inicio de sesión "
    "con el teléfono, sólo esa vez), contact_name = el nombre que escribí en ENVIAR A, y message = el "
    "texto que escribí en MENSAJE.\n"
    "\n"
    "Marca SOLO la casilla Multi-Turn; usa SOLO chat_agent_telegrammer. Termina con END-RESPONSE."
)

TG_AS_BOT = (
    "Tlamatini, manda UN mensaje de Telegram COMO EL BOT (NO desde mi propia cuenta).\n"
    "\n"
    "LLENA ESTOS CAMPOS — reemplaza el texto dentro de los corchetes [[ ]]:\n"
    "- ENVIAR A:  [[ ESCRIBE AQUÍ EL NOMBRE DEL CONTACTO — esta persona YA DEBE estar guardada "
    "en mi libreta de contactos (contacts.json) con un @username de Telegram, Y debe haber presionado "
    "Start / escrito a mi bot al menos una vez (un bot no le puede escribir a un desconocido) ]]\n"
    "- MENSAJE:  [[ ESCRIBE AQUÍ EL MENSAJE QUE QUIERES MANDAR ]]\n"
    "\n"
    "PRIMERO, REVISIÓN DE SEGURIDAD: si la línea ENVIAR A todavía muestra los "
    "corchetes [[ ]] (no la he llenado), NO mandes nada — sólo dime que escriba un nombre de "
    "contacto que exista en mi libreta de contactos, y detente. Si escribí un nombre que NO está en "
    "contacts.json, NO adivines ni inventes un handle — dime que ese nombre no está en mis contactos para que lo agregue primero, y detente.\n"
    "\n"
    "LUEGO mándalo usando SOLO el tool chat_agent_telegrammer con mode='send', "
    "provider='bot' (así sale DESDE EL BOT por la Bot API oficial), contact_name = el nombre que "
    "escribí en ENVIAR A, y message = el texto que escribí en MENSAJE.\n"
    "\n"
    "Marca SOLO la casilla Multi-Turn; usa SOLO chat_agent_telegrammer. Termina con END-RESPONSE."
)

WA_AS_ME = (
    "Tlamatini, manda UN mensaje de WhatsApp DESDE MI PROPIO número (como yo, modo personal de WhatsApp Web).\n"
    "\n"
    "LLENA ESTOS CAMPOS — reemplaza el texto dentro de los corchetes [[ ]]:\n"
    "- ENVIAR A:  [[ ESCRIBE AQUÍ EL NOMBRE DEL CONTACTO — esta persona YA DEBE estar guardada "
    "en mi libreta de contactos (contacts.json) con un número de WhatsApp ]]\n"
    "- MENSAJE:  [[ ESCRIBE AQUÍ EL MENSAJE QUE QUIERES MANDAR ]]\n"
    "\n"
    "PRIMERO, REVISIÓN DE SEGURIDAD: si la línea ENVIAR A todavía muestra los corchetes "
    "[[ ]] (no la he llenado), NO mandes nada — sólo dime que escriba un nombre de contacto que "
    "exista en mi libreta de contactos, y detente. Si escribí un nombre que NO está en contacts.json, NO "
    "adivines ni inventes un número — dime que ese nombre no está en mis contactos para que lo agregue primero, y detente.\n"
    "\n"
    "LUEGO mándalo usando SOLO el tool chat_agent_whatsapper con mode='send', "
    "provider='me' (así sale desde MI PROPIO número por WhatsApp Web — la primera vez necesita el inicio de "
    "sesión con QR, sólo esa vez), contact_name = el nombre que escribí en ENVIAR A, y message = el texto "
    "que escribí en MENSAJE.\n"
    "\n"
    "Marca SOLO la casilla Multi-Turn; usa SOLO chat_agent_whatsapper. Termina con END-RESPONSE."
)

# old distinctive marker (from migrations 0156/0157) -> the redesigned content.
_REWRITES = (
    ("**TELEGRAM 'AS ME' demo**", TG_AS_ME),
    ("**TELEGRAM 'AS THE BOT' demo**", TG_AS_BOT),
    ("**WHATSAPP 'AS ME' demo**", WA_AS_ME),
)


def redesign_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for marker, new_text in _REWRITES:
        # Update the row 0156/0157 seeded (matched by its old title marker),
        # preserving its idPrompt / promptName so the catalog stays contiguous.
        for row in Prompt.objects.filter(promptContent__contains=marker):
            row.promptContent = new_text
            row.save(update_fields=['promptContent'])


def noop(apps, schema_editor):
    # No need to restore the old, confusing text on reverse.
    pass


class Migration(migrations.Migration):
    dependencies = [('agent', '0157_add_whatsapper_identity_demo_prompt')]
    operations = [migrations.RunPython(redesign_prompts, noop)]
