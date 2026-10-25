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


# MANDATORY catalog-of-prompts example for the Multi-Turn agent
# `chat_agent_instant_messaging_doctor` (create_new_agent.md Step 7.8).
# SAFE by design: mode='diagnose' + retry_send=false => the agent only validates
# readiness (tokens / contacts / reachability / templates / webhook) and sends
# NOTHING, so the daily chat regression can run it without messaging anyone.
DEMO = (
    "Tlamatini, ejecuta la demo **INSTANT MESSAGING DOCTOR**, por favor: usa SÓLO el "
    "tool chat_agent_instant_messaging_doctor para hacer un diagnóstico SEGURO y de sólo lectura de mi "
    "disponibilidad de mensajería. Pon platform='both', mode='diagnose' y retry_send=false para que "
    "NO se envíe NADA; sólo revisa la configuración de Telegrammer y Whatsapper (el bot token, "
    "el access token de Meta, la libreta de contactos, si se puede alcanzar al destinatario, la ventana de 24 horas de WhatsApp / "
    "las plantillas aprobadas y la configuración del webhook) y luego resume qué está bien y qué todavía "
    "hay que arreglar. Marca SÓLO la casilla Multi-Turn; usa SÓLO "
    "chat_agent_instant_messaging_doctor. Termina con END-RESPONSE."
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
    dependencies = [('agent', '0153_add_chat_agent_instant_messaging_doctor_tool')]
    operations = [migrations.RunPython(add_demo_prompt, remove_demo_prompt)]
