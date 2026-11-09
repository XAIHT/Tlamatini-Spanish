# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Use this instance's integrated account console and yield to private input.

Repair only the exact shipped account-wizard card. Historical migrations and
operator-edited prompts remain untouched; the update is reversible/idempotent.
"""
from importlib import import_module

from django.db import migrations


_catalog = import_module('agent.migrations.0224_restore_catalog_execution_parity')
_models = import_module('agent.migrations.0226_replace_mistral_large3')
OLD_WIZARD_PROMPT = next(new for number, old, new in _catalog.REPAIRS if number == 1)
for _retired, _replacement in _models.MODEL_REPLACEMENTS.items():
    OLD_WIZARD_PROMPT = OLD_WIZARD_PROMPT.replace(_retired, _replacement)


def _replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('The shipped account-wizard text no longer matches its migration baseline')
    return text.replace(old, new, 1)


WIZARD_PROMPT = _replace_once(
    OLD_WIZARD_PROMPT,
    'Para PowerShell usa Set-Location -LiteralPath y el operador &, escapando cada comilla simple '
    'de una ruta como dos comillas simples. Envuelve la orden para el shell real de Executer; '
    'no copies pseudocódigo ni marcadores.',
    'En Windows, script de Executer es un archivo CMD .bat, no un script de PowerShell. '
    'Usa sintaxis CMD: @echo off, setlocal DisableDelayedExpansion, cd /d seguido de '
    'management_cwd entre comillas dobles, y después cada elemento de management_argv entre '
    'comillas dobles seguido de createsuperuser. Conserva los saltos de línea y escapa los '
    'porcentajes literales de las rutas como %%. No escribas Set-Location ni el operador & '
    'de PowerShell directamente en ese .bat. No copies pseudocódigo ni marcadores. '
    'Si usas PowerShell explícitamente, invócalo desde CMD con un argumento de comando '
    'completo y correctamente escapado; nunca mezcles los dos dialectos.',
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    "target.outcome_detail='Completa los datos en la consola de Tlamatini-Spanish. La contraseña "
    "no va en el chat.', target.sound_enabled=true. ESPERA.",
    "target.outcome_detail='Completa los datos en la consola de Tlamatini-Spanish. La contraseña "
    "no va en el chat.', target.sound_enabled=true. Devuelve de inmediato una respuesta breve "
    "con HECHO, ERROR y SIN VENTANA y termina este turno con END-RESPONSE. ESPERA mi entrada "
    "en la consola y mi respuesta en el chat. No tomes capturas de la consola de credenciales, "
    "no llames a Shoter ni a Image-Interpreter, no uses chat_agent_run_wait para esperar "
    "que yo complete createsuperuser y no abras otra consola. Esta espera es una frontera "
    "de interacción humana, no una tarea de verificación visual del modelo.",
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    'Usa chat_agent_executer para abrir la consola y chat_agent_notifier para los avisos locales.',
    'Usa el asistente de cuentas integrado de esta instancia para abrir la consola y mostrar '
    'los avisos locales. La tarjeta completa se atiende directamente, sin pedir a un modelo '
    'que construya o ejecute la orden. No invoques agentes auxiliares para tramitar esta tarjeta.',
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    'Paso 2 (ejecución del primer paso operativo) — Construye una sola orden para abrir una '
    'consola interactiva con chat_agent_executer, script={{ orden concreta }}, '
    'execute_forked_window=true y non_blocking=true.',
    'Paso 2 (ejecución del primer paso operativo) — Abre una única consola interactiva '
    'mediante el asistente de cuentas integrado; su orden canónica procede de esta instancia. '
    'No solicites chat_agent_executer en la ruta integrada. En solicitudes personalizadas '
    'que sí usen Executer, la alternativa compatible conserva execute_forked_window=true '
    'y non_blocking=true.',
)
WIZARD_PROMPT = _replace_once(
    WIZARD_PROMPT,
    'Ejecuta la orden con Executer ahora: escribirla en el chat no sustituye la llamada a la herramienta.',
    'El asistente integrado abre la consola ahora y devuelve el control al chat; escribir '
    'una orden en el chat no sustituye su ejecución. No solicites otro lanzamiento por una '
    'comprobación de estado ni mientras esta consola siga abierta.',
)

# Keep the earlier uncommitted 0227 card recognizable in existing conversations
# and isolated source-test databases. Its contradictory Notifier/CMD prose must
# not remain the current catalog default, and customized variants are not edited.
LEGACY_WIZARD_PROMPT = WIZARD_PROMPT
WIZARD_PROMPT = """Tlamatini-Spanish, ayúdame a crear una cuenta ADMINISTRATIVA nueva con tu asistente de cuentas integrado.
Nombre: [[ ESCRIBE AQUÍ EL NOMBRE DE USUARIO — OBLIGATORIO ]]
Este es un asistente de configuración Paso a paso. Marca Multi-Turn, Exec report y Paso a paso. La contraseña la escribiré solamente en la ventana de consola, nunca en el chat.

Abre la consola como primer paso operativo. Con el nombre disponible, ábrela en este mismo turno; no me pidas confirmar la identidad de la instancia ni esperes un análisis de capturas. Esta instancia atiende directamente la tarjeta predeterminada completa, sin pedir a un modelo que construya una orden ni invocar agentes auxiliares.
Si falta el nombre, pide solo ese dato y espera. Toma mi siguiente respuesta con el nombre como la contestación y continúa abriendo la consola. Explica que createsuperuser crea una cuenta administrativa.

Usa el ejecutable canónico de esta instancia y su directorio de proyecto Django. En desarrollo, usa el Python exacto del proceso y la ruta absoluta a Tlamatini/manage.py. En una instalación, usa el ejecutable propio de esta instancia. Ejecuta el comando integrado createuserconsole: utiliza la interacción real, el modelo, las comprobaciones de migraciones, los controles de nombres duplicados y la validación de contraseñas de createsuperuser de Django. Nunca selecciones otra instalación mediante PATH, variables temporales heredadas o una búsqueda global. Nunca interpoles el nombre ni la contraseña como código de shell.

Abre una sola consola interactiva visible y devuelve el control inmediatamente. Allí escribiré el nombre, el correo opcional, la contraseña y su repetición. Espera HECHO, ERROR o SIN VENTANA. No captures la consola de credenciales, no ejecutes Image-Interpreter, no consultes agentes ni abras otra consola mientras esta siga abierta. Un lanzamiento solicitado no confirma por sí mismo que apareció una ventana ni que se creó una cuenta.

HECHO: comprueba que la cuenta administrativa indicada se creó realmente en esta instancia durante este asistente. Si no está confirmado, explícalo y espera; nunca declares éxito a partir del resultado de lanzamiento.
ERROR: conserva la consola existente si admite entrada; informa del error sin secretos y espera. Nunca envíes una contraseña por el chat.
SIN VENTANA: intenta traer al frente la consola que pertenece a este asistente; no crees ventanas repetidamente. Si se cerró, puedo reenviar esta tarjeta para reintentar.

Cuando la creación esté confirmada, muestra USUARIO LISTO e indica que cierre sesión y entre con la nueva cuenta en la MISMA dirección del navegador. Una cuenta nueva de Django funciona sin reiniciar el servidor. Nunca cierres la edición inglesa ni los procesos de otra aplicación.
Termina con END-RESPONSE.
"""
KNOWN_PREVIOUS_DEFAULTS = (OLD_WIZARD_PROMPT, LEGACY_WIZARD_PROMPT)


def repair(apps, schema_editor):
    rows = apps.get_model('agent', 'Prompt').objects.using(schema_editor.connection.alias)
    rows.filter(pk=1, promptContent__in=KNOWN_PREVIOUS_DEFAULTS).update(promptContent=WIZARD_PROMPT)


def reverse(apps, schema_editor):
    rows = apps.get_model('agent', 'Prompt').objects.using(schema_editor.connection.alias)
    rows.filter(pk=1, promptContent=WIZARD_PROMPT).update(promptContent=OLD_WIZARD_PROMPT)


class Migration(migrations.Migration):
    dependencies = [('agent', '0226_replace_mistral_large3')]
    operations = [migrations.RunPython(repair, reverse)]
