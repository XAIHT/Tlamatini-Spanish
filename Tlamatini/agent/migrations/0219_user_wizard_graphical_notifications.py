# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Make the account wizard explicitly request its local graphical checkpoints."""

import base64
import importlib
import json

from django.db import migrations


# Compare with the exact shipped text, so an installation's edited catalog card
# is never silently replaced. Keep historical migrations immutable.
_previous = importlib.import_module(
    "agent.migrations.0185_standardize_prompt_params_batch3"
)
OLD_WIZARD_PROMPT = json.loads(base64.b64decode(_previous._NEW_B64).decode("utf-8"))["1"]

LOCAL_ALERTS = """Avisos gráficos: Pido explícitamente alertas gráficas locales del Notifier durante este wizard. Usa chat_agent_notifier para las alertas de los puntos de control de abajo, además de chat_agent_executer para los comandos. Cada alerta debe ser una llamada real al tool con target.mode='oneshot', target.search_strings con la etiqueta del punto de control, target.outcome_detail con su instrucción corta y sin secretos, y target.sound_enabled=true. Son diálogos locales dentro del browser, no correo, Telegram, WhatsApp ni otros mensajes externos. Nunca sustituyas el Notifier gráfico con un panel HTML en el chat. El campo opcional de correo de la cuenta no autoriza ningún mensaje externo. Si el tool del Notifier da un error real, repórtalo en el chat sin decir que se entregó y sin repetir el comando que crea la cuenta. Sólo una alerta cada vez que ocurra un punto de control; un nuevo Continuar o una respuesta que no tenga que ver no la repite. El wizard está incompleto mientras espera mi respuesta, y no se permite ninguna alerta de éxito antes de la confirmación de éxito descrita en el Paso 3.

"""


def _replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("The shipped user-wizard checkpoint no longer matches its migration baseline")
    return text.replace(old, new, 1)


WIZARD_PROMPT = _replace_once(
    OLD_WIZARD_PROMPT, "Paso 0 (banner y el nombre de usuario):",
    LOCAL_ALERTS + "Paso 0 (banner y el nombre de usuario):",
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    "si TODAVÍA muestra los corchetes [[ ]], respóndeme pidiéndome el nombre de usuario que quiero y DETENTE",
    "si TODAVÍA muestra los corchetes [[ ]], llama a chat_agent_notifier con "
    "target.mode='oneshot' y target.search_strings='Falta el nombre de usuario' y "
    "target.outcome_detail='Elige en el chat el nombre de usuario de la nueva cuenta de Tlamatini. Las "
    "contraseñas van sólo en la consola.' y target.sound_enabled=true, luego "
    "respóndeme pidiéndome el nombre de usuario que quiero y DETENTE",
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    "Cuando lo abras, dime — en un solo bloque corto y amable — exactamente esto:",
    "Si el tool de lanzamiento reporta un error, sigue el branch ERROR de abajo y no "
    "anuncies que se abrió una consola. Después de un resultado de lanzamiento exitoso, "
    "llama a chat_agent_notifier con target.mode='oneshot' "
    "y target.search_strings='Escribe en la consola' "
    "y target.outcome_detail='Completa los prompts de la cuenta en la consola. Tu contraseña "
    "se queda ahí. Responde DONE en el chat sólo después de que la consola reporte "
    "éxito; responde ERROR si algo falla o NOWINDOW si la consola no apareció.' "
    "y target.sound_enabled=true. Luego dime — en un solo bloque corto y amable — esto:",
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    "Se acaba de abrir una ventana de consola en tu escritorio. En esa ventana: (1) aparece el prompt "
    "del nombre de usuario — presiona Enter para aceptar {{ el nombre de usuario }} (o escríbelo si está vacío)",
    "Se pidió abrir la consola. En esa ventana: (1) lee el prompt del nombre de usuario y escribe "
    "{{ el nombre de usuario }} si el valor predeterminado que muestra es otro; presiona Enter sólo "
    "cuando esté seleccionado el nombre de usuario correcto",
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    " - Si respondo DONE → ve al Paso 4.",
    " - Si respondo DONE después de ver el mensaje real de la consola 'Superuser "
    "created successfully' → llama a chat_agent_notifier con target.mode='oneshot' "
    "y target.search_strings='Usuario listo' y target.outcome_detail='Confirmaste "
    "que la consola creó la cuenta con éxito. Sigue en el chat las "
    "instrucciones para reiniciar e iniciar sesión.' y target.sound_enabled=true, luego ve "
    "al Paso 4. Si DONE es ambiguo o no vi ese mensaje de éxito, pide esa "
    "confirmación y ESPERA; una ventana abierta o un comando escrito no es éxito.",
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    " - Si respondo ERROR y pego el mensaje → dime la corrección en una línea",
    " - Si respondo ERROR y pego el mensaje sin secretos, o el tool de lanzamiento reporta "
    "un error → llama a chat_agent_notifier con target.mode='oneshot' y "
    "target.search_strings='Error al crear el usuario' y target.outcome_detail='La "
    "configuración de la cuenta necesita atención. Lee en el chat el error sin "
    "secretos y el siguiente paso; la creación de la cuenta no está confirmada.' y "
    "target.sound_enabled=true. Luego dime la corrección en una línea",
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    "luego VUELVE A ABRIR la consola exactamente como en el Paso 2 y ESPERA otra vez.",
    "luego revisa si la consola que ya está abierta sigue aceptando lo que escribo. Si es así, "
    "guíame ahí y ESPERA. Si no, ofrece un solo reintento del Paso 2 después de que "
    "yo lo confirme; no abras consolas una y otra vez ni vuelvas a crear la cuenta.",
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    " - Si respondo NOWINDOW → dame esta alternativa manual y ESPERA:",
    " - Si respondo NOWINDOW → llama a chat_agent_notifier con target.mode='oneshot' y "
    "target.search_strings='Aviso: la consola no se ve' y "
    "target.outcome_detail='La consola de la cuenta no apareció. Sigue en el chat las instrucciones "
    "manuales de la consola; la creación de la cuenta no está confirmada.' "
    "y target.sound_enabled=true. Luego dame esta alternativa manual y ESPERA:",
)


def apply_update(apps, schema_editor):
    Prompt = apps.get_model("agent", "Prompt")
    Prompt.objects.filter(idPrompt=1, promptContent=OLD_WIZARD_PROMPT).update(
        promptContent=WIZARD_PROMPT
    )


def reverse_update(apps, schema_editor):
    Prompt = apps.get_model("agent", "Prompt")
    Prompt.objects.filter(idPrompt=1, promptContent=WIZARD_PROMPT).update(
        promptContent=OLD_WIZARD_PROMPT
    )


class Migration(migrations.Migration):
    dependencies = [("agent", "0218_add_interactor_tool")]
    operations = [migrations.RunPython(apply_update, reverse_update)]
