# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

PROMPT = (
    "Usa Torrenter para listar mis descargas. Indica el estado solicitado, la fase observada y los bytes verificados. "
    "Si te doy un ID de inspección, revisa los archivos y pregúntame cuáles quiero antes de iniciar la descarga. "
    "Dame el ID persistente del job y consulta el manifiesto verificado antes de indicar que un archivo está completo."
)


def seed(apps, schema_editor):
    compact = (
        apps.get_model("agent", "CompactState")
        .objects.filter(pk=1, active=True)
        .exists()
    )
    for model, label in (("Agent", "Torrenter"), ("Tool", "Chat-Agent-Torrenter")):
        table = apps.get_model("agent", model)
        prefix = model.lower()
        pk = "id" + model
        if not table.objects.filter(**{prefix + "Description": label}).exists():
            n = (
                table.objects.order_by("-" + pk).values_list(pk, flat=True).first() or 0
            ) + 1
            table.objects.create(
                **{
                    pk: n,
                    prefix + "Name": f"{prefix}-{n}",
                    prefix + "Description": label,
                    prefix + "Content": "false" if compact else "true",
                }
            )
    table = apps.get_model("agent", "Prompt")
    if not table.objects.filter(promptContent=PROMPT).exists():
        n = (
            table.objects.order_by("-idPrompt")
            .values_list("idPrompt", flat=True)
            .first()
            or 0
        ) + 1
        table.objects.create(
            idPrompt=n,
            promptName=f"prompt-{n}",
            promptContent=PROMPT,
            category="run_execute",
            sort_rank=68,
        )


def unseed(apps, schema_editor):
    apps.get_model("agent", "Agent").objects.filter(
        agentDescription="Torrenter"
    ).delete()
    apps.get_model("agent", "Tool").objects.filter(
        toolDescription="Chat-Agent-Torrenter"
    ).delete()
    apps.get_model("agent", "Prompt").objects.filter(promptContent=PROMPT).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("agent", "0220_interaction_settings"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="TorrenterProfile",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "account",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
            ],
        ),
        migrations.AddField(
            model_name="chatagentrun",
            name="owner",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(seed, unseed),
    ]
