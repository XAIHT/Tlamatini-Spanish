# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""
Seed a Catalog-of-Prompts demo for **Talker** — Tlamatini's TEXT-TO-SPEECH — run
through the wrapped **chat_agent_talker** Multi-Turn tool. This is the MANDATORY
catalog prompt every Multi-Turn-capable agent must ship (CLAUDE.md ⚠️ directive /
create_new_agent.md Step 7.8 / tlamatini-agent-creation skill Phase 19); Talker
(#75, migrations 0120/0121) shipped without one, so this closes that gap.

    73  TLAMATINI SPEAKS   basic   speak a greeting with voice='tara' -> speak a
                                   second line with voice='leah' -> report a small
                                   table of each call's voice/status/seconds/path.

FEMALE VOICE ONLY by design: Tlamatini is female, so the demo uses ONLY her
permitted female voices (tara/leah/jess/mia/zoe). Talker enforces this itself —
a non-female voice makes it close its execution entirely (see prompt.pmt Rule 17
and talker.py::resolve_voice) — so the demo never asks for anything else.

SAFE to run repeatedly (the daily chat test may execute it): TTS is
observational/output (it plays + saves a WAV), it mutates no persistent state,
and its wrapped Multi-Turn call is captured in the Exec Report. Audible sound
needs snac+torch + a reachable Ollama serving the Orpheus model; without them
Talker reports status `tokens_only`, a degraded red row because no audible
deliverable exists even though the canvas block remains routable.

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js) enumerates promptName
'prompt-1','prompt-2',... and BREAKS at the first missing slot, so the catalog
must stay a contiguous, gap-free 'prompt-1..N'. Slots 1-72 are occupied (0111
appended the Arduiner demos at 70-72); this APPENDS at 73 with no shift of any
existing prompt. Reverse deletes 73. (MAX_PROMPTS=100.)
"""
from django.db import migrations


# Talker banner palette — mirrors the ``.canvas-item.talker-agent`` gradient
# (deep wine -> terracotta -> warm amber -> cream), with a text-shadow so the
# white label stays legible across the bright cream end.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#5b1d2e 0%,#c1462e 33%,#f2a35e 66%,#ffe3a3 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


TALKER_SPEAKS_DEMO = (
    "Tlamatini, ejecuta la demo **TLAMATINI SPEAKS**, por favor &mdash; una muestra básica de tu propia "
    "voz TEXT-TO-SPEECH, controlada por completo desde el chat a través del tool wrapper **chat_agent_talker**: "
    "sintetizas líneas cortas de habla con dos de tus voces FEMENINAS y las reproduces en "
    "las bocinas, y luego reportas lo que se dijo. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques &mdash; ve directo al Paso 1): "
    "(a) marca SÓLO la casilla **Multi-Turn** antes de enviar (NO se necesita ACPX &mdash; "
    "chat_agent_talker es el ÚNICO tool que puedes usar; no uses chat_agent_executer / "
    "chat_agent_pythonxer ni tools de ACPX); (b) oír el audio necesita un Ollama accesible sirviendo "
    "el modelo Orpheus más `snac`+`torch` instalados &mdash; si no están, Talker igual corre "
    "y devuelve status `tokens_only` (un modo degradado documentado, NO un error): regístralo "
    "tal cual y CONTINÚA. "
    "REGLA DE VOZ (por diseño, no negociable): eres MUJER y hablas SÓLO con voz de mujer "
    "&mdash; tara (preferida), leah, jess, mia o zoe. Usa SÓLO estas. "
    "Cada paso es exactamente UNA llamada a chat_agent_talker con la forma \"Speak with input_text='<text>' and "
    "voice='<female voice>'\". Después de cada llamada lee el JSON que devuelve (un bloque INI_SECTION_TALKER "
    "del log_excerpt de la ejecución) y captura voice / gender / status / audio_seconds / "
    "output_path, además del body. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128483;&#65039; TLAMATINI HABLA &#127908;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini Talker &mdash; su propia voz, siempre de mujer</div></div>. "
    "\n\n"
    "Paso 1 (saludo con su voz predeterminada): llama a **chat_agent_talker** con el request "
    "\"Speak with input_text='Hello, I am Tlamatini. This is my voice.' and voice='tara'\". "
    "Del bloque INI_SECTION_TALKER captura voice (tara), gender (female), status "
    "(spoken / saved / tokens_only), audio_seconds y output_path. "
    "\n\n"
    "Paso 2 (una segunda voz femenina): llama a **chat_agent_talker** con el request "
    "\"Speak with input_text='And this is another of my voices.' and voice='leah'\". "
    "Captura los mismos campos (voice=leah, gender=female). "
    "\n\n"
    "Paso 3: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Tlamatini Speaks &mdash; Reporte de voz</strong>' y con las columnas <em>paso</em>, "
    "<em>voice</em>, <em>gender</em>, <em>status</em> (spoken|saved|tokens_only|error), "
    "<em>segundos</em>, <em>WAV guardado</em> &mdash; una fila por cada llamada en orden de ejecución, cada valor "
    "tal cual del bloque INI_SECTION_TALKER (NO lo reclasifiques). Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a; o rayado #f1f5f9), tono verde para spoken, tono ámbar para "
    "tokens_only. "
    "\n\n"
    "Paso 4: cierra con un banner HTML que reutilice el estilo del Paso 0 y muestre, en letras grandes, "
    "'&#9989; HABLÓ' (ambas llamadas devolvieron status spoken &mdash; el audio se reprodujo), "
    "'&#128266; GUARDADO, NO REPRODUCIDO' (status saved) o '&#128221; SÓLO TOKENS' (status tokens_only "
    "&mdash; sin vocoder/Ollama, en su lugar se guardaron los tokens de audio), y debajo una métrica de una línea "
    "'voces: tara, leah &middot; status: <s1>/<s2> &middot; audio: <sec1>s + <sec2>s'. "
    "Termina con END-RESPONSE."
)


_NEW_PROMPTS = (
    (73, TALKER_SPEAKS_DEMO),
)


def add_talker_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_talker_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0121_add_chat_agent_talker_tool'),
    ]

    operations = [
        migrations.RunPython(add_talker_demo_prompt, remove_talker_demo_prompt),
    ]
