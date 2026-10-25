# ═══════════════════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Catalog of Prompts — the three Terminater cards.

Terminater is Multi-Turn-capable, so it is INCOMPLETE without at least one catalog
prompt (``create_new_agent.md`` Step 7.8, a hard completion gate).  Three are
seeded because Terminater has three genuinely different stories and one card
cannot show them all:

  127  FIRST LOOK    — raise a terminal, watch Tlamatini type a read-only command.
  128  HAND-OVER     — Tlamatini types part of a command, the USER types the rest.
  129  GUIDED TOUR   — CMD + PowerShell side by side (tiled), then Tlamatini watches
                       what the user types and warns about a mistake.

Contract compliance:

  * APPEND-ONLY ids: the catalog's highest live id was 126, so these are 127-129.
  * ``category='run_execute'`` ("Run & Execute"): Terminater is the VISIBLE sibling
    of Executer, which already lives there.  ``sort_rank`` 62/64/66 keeps the tool
    families contiguous (Executer-style cards 20-60, then Terminater, then
    NetSpeed at 70) and ranks are unique inside the section; rank 10 stays the
    section's Step-by-Step opener.
  * Parameter grammar v1.44.0: user inputs are ``[[ ... — OPTIONAL, default: X ]]``
    at the TOP with the unfilled-guard sentence beneath, so a one-click demo runs on
    the stated defaults.  ``< >`` marks REPORT slots only.  No hardcoded scratch
    path (Rules 15/16): nothing here writes a file.
  * SAFE and repeatable: the commands only LIST, ECHO or PING; nothing is changed,
    deleted or installed.  The daily chat test may run them.
  * CLASSIFIER MODES (``tools_dialog.js::classifyPromptModes``): 127 and 128 name
    only the Multi-Turn and Exec report checkboxes (no ``acp_*`` token, no
    hyphenated step-by-step token); 129 deliberately names the hyphenated
    Step-by-Step mode, because a guided tour is exactly the cadence Step-by-Step
    exists for.  The literal ``<<USER:...>>`` marker inside 128 is the hand-over
    syntax Tlamatini must pass to the tool; it is not a REPORT slot.

Reverse deletes exactly these three rows.
"""
from django.db import migrations


FIRST_LOOK = (
    "Tlamatini, ejecuta el **PRIMER VISTAZO A TERMINATER**, por favor — una terminal REAL que "
    "puedes ver mientras yo trabajo en ella.\n\n"
    "[[ terminal type — OPCIONAL, predeterminado: powershell (o escribe: cmd) ]]\n"
    "(Si el valor de arriba sigue sin llenar, usa su predeterminado y continúa sin preguntar.)\n\n"
    "Usa SÓLO chat_agent_terminater para esto. NO uses Executer — el punto es que yo "
    "VEA los comandos mientras se escriben.\n"
    "1. Levanta una terminal: action='open', kind=<el tipo de arriba>, title='Terminater first "
    "look'. El área Terminals aparece debajo del canvas.\n"
    "2. En esa terminal, con action='type', ESCRIBE — tecla por tecla, como una persona, nunca "
    "pegado — el comando que lista los cinco elementos cambiados más recientemente de la carpeta "
    "actual. Para powershell: Get-ChildItem | Sort-Object LastWriteTime -Descending | "
    "Select-Object -First 5 Name, LastWriteTime — para cmd: dir /o-d\n"
    "3. Espera a que termine, lee el output COMPLETO y reporta:\n"
    "   · el id de la terminal y su tipo: <terminal_id>, <kind>\n"
    "   · el comando exacto que escribiste: <typed>\n"
    "   · el status y el exit code (di claramente que CMD no puede reportar un exit code "
    "cuando está vacío): <status>, <exit_code>\n"
    "   · cuánto tardó y las primeras tres líneas del output: <duration>, "
    "<first_lines>\n"
    "4. Deja la terminal ABIERTA para que yo pueda leerla.\n\n"
    "ANTES DE EMPEZAR: marca Multi-Turn y Exec report. Este comando sólo LISTA archivos; no "
    "cambia nada. Termina con END-RESPONSE."
)

HAND_OVER = (
    "Tlamatini, ejecuta el **RELEVO CON TERMINATER**, por favor — tú escribes el inicio de un "
    "comando y yo escribo el resto.\n\n"
    "[[ number of echo requests — OPCIONAL, predeterminado: 2 ]]\n"
    "(Si el valor de arriba sigue sin llenar, usa su predeterminado y continúa sin preguntar.)\n\n"
    "Usa SÓLO chat_agent_terminater. NO uses Executer.\n"
    "1. Con action='run', kind='cmd', title='Hand-over demo', escribe este TEXTO EXACTO (el "
    "marcador <<USER:...>> es la sintaxis que me pasa el teclado — pásalo literal): "
    "ping <<USER:el host al que hacer ping, p. ej. 127.0.0.1>> -n <el número de arriba>\n"
    "2. Dime en una oración, ANTES de la llamada, que vas a escribir 'ping ' y luego "
    "me das el teclado. En la terminal yo escribo el host y presiono Enter; "
    "tú luego terminas la línea y la ejecutas.\n"
    "3. Espera el comando, lee el output COMPLETO y reporta:\n"
    "   · lo que escribiste tú y lo que escribí yo: <typed>, <user_part>\n"
    "   · el status: <status>\n"
    "   · las últimas dos líneas de las estadísticas del ping: <statistics>\n"
    "4. Si no termino mi parte a tiempo, el status es operator_required — dilo en "
    "lugar de adivinar un host. Deja la terminal ABIERTA.\n\n"
    "ANTES DE EMPEZAR: marca Multi-Turn y Exec report. El ping sólo manda unos pocos echo requests; "
    "no se cambia nada. Termina con END-RESPONSE."
)

GUIDED_TOUR = (
    "Tlamatini, dame el **RECORRIDO GUIADO DE TERMINATER**, por favor — dos terminales "
    "lado a lado, y luego miras lo que escribo y me ayudas.\n\n"
    "[[ el comando que quieres practicar — OPCIONAL, predeterminado: Get-Date ]]\n"
    "(Si el valor de arriba sigue sin llenar, usa su predeterminado y continúa.)\n\n"
    "Usa SÓLO chat_agent_terminater, y ve UNA acción a la vez: dame un paso concreto, "
    "espera mi READY, luego haz el siguiente.\n"
    "PASO 1 — abre una terminal CMD titulada 'Tour CMD' y una terminal PowerShell titulada "
    "'Tour PS' (dos llamadas action='open' separadas).\n"
    "PASO 2 — acomódalas lado a lado: action='layout', layout='tile-h'. Dime qué "
    "debería ver.\n"
    "PASO 3 — en 'Tour CMD' escribe: ver — y en 'Tour PS' escribe: "
    "$PSVersionTable.PSVersion — y luego dime qué versión reportó cada una y que "
    "CMD no da exit code.\n"
    "PASO 4 — dime que entre a 'Tour PS' haciendo clic y empiece a escribir el comando de práctica de arriba SIN "
    "presionar Enter. Luego llama a action='watch_user' (terminal='Tour PS', "
    "until='idle') y dime exactamente qué me viste escribir. Si se ve peligroso o mal "
    "escrito, llama a action='warn_user' en lugar de ejecutar nada.\n"
    "PASO 5 — pregúntame si cerrar el tour; con mi READY usa action='kill' en ambas "
    "terminals.\n\n"
    "ANTES DE EMPEZAR: marca Multi-Turn, Exec report y la casilla Paso a paso. Nada en este tour "
    "cambia la máquina. Termina con END-RESPONSE."
)

_NEW_PROMPTS = (
    (127, 62, FIRST_LOOK),
    (128, 64, HAND_OVER),
    (129, 66, GUIDED_TOUR),
)


def add_terminater_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, rank, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={
                'promptName': 'prompt-%d' % prompt_id,
                'promptContent': content,
                'category': 'run_execute',
                'sort_rank': rank,
            },
        )


def remove_terminater_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(
        idPrompt__in=[prompt_id for prompt_id, _rank, _content in _NEW_PROMPTS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0216_add_chat_agent_terminater_tool'),
    ]

    operations = [
        migrations.RunPython(add_terminater_demo_prompts, remove_terminater_demo_prompts),
    ]
