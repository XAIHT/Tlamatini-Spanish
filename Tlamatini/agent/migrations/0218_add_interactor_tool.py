# Tlamatini Author Banner — Angela López Mendoza · @angelahack1
"""One module tool and a guided-editor catalog example; no Agent row."""
from django.db import migrations


PROMPT_NAME = "INTERACTOR — Crear un Dockerfile juntos"
PROMPT = (
    "Tlamatini, ayúdame a crear un Dockerfile para una aplicación Java con un servlet y una página de inicio, "
    "con tu editor de texto. Usa el módulo Interactor y Multi-Turn. No te doy ningún path: crea el "
    "Dockerfile en la Temp de Tlamatini. Lee primero el canvas actual y conserva cualquier trabajo sin guardar. "
    "Escribe sólo el primer segmento pequeño que ya se conozca y luego detente en el primer campo que yo deba elegir. Explica "
    "la elección en el chat, con recomendaciones y opciones de completado local para ese campo. "
    "Déjame escribir mi respuesta y hacer clic en Continuar en el chat. Lee mi texto nuevo sin guardar antes de cada "
    "paso siguiente. No termines el archivo ni ejecutes Docker por mí. Termina cada turno de enseñanza con END-RESPONSE."
)


def seed(apps, schema_editor):
    Tool = apps.get_model("agent", "Tool")
    if not Tool.objects.filter(toolDescription="Interactor").exists():
        last = Tool.objects.order_by("-idTool").first()
        number = last.idTool + 1 if last else 1
        Tool.objects.create(idTool=number, toolName=f"tool-{number}", toolDescription="Interactor", toolContent="true")
    Prompt = apps.get_model("agent", "Prompt")
    if not Prompt.objects.filter(promptName=PROMPT_NAME).exists():
        last = Prompt.objects.order_by("-idPrompt").first()
        Prompt.objects.create(idPrompt=last.idPrompt + 1 if last else 1, promptName=PROMPT_NAME,
                              promptContent=PROMPT, category="code_gen", sort_rank=95)


def reverse(apps, schema_editor):
    apps.get_model("agent", "Tool").objects.filter(toolDescription="Interactor").delete()
    apps.get_model("agent", "Prompt").objects.filter(promptName=PROMPT_NAME).delete()


class Migration(migrations.Migration):
    dependencies = [("agent", "0217_add_terminater_demo_prompts")]
    operations = [migrations.RunPython(seed, reverse)]
