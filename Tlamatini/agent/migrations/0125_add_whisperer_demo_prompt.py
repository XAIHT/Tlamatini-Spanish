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
Seed a Catalog-of-Prompts demo for **Whisperer** — Tlamatini's SPEECH-TO-TEXT —
run through the wrapped **chat_agent_whisperer** Multi-Turn tool. This is the
MANDATORY catalog prompt every Multi-Turn-capable agent must ship (CLAUDE.md
directive / create_new_agent.md Step 7.8 / tlamatini-agent-creation Phase 19).

    74  TLAMATINI LISTENS   basic   record 30 seconds of the microphone ->
                                    transcribe the speech to a text string ->
                                    report engine/device/status + the transcript.

SAFE to run repeatedly (the daily chat test may execute it): STT is
observational (it records a short mic clip and writes a transcript .txt), it
mutates no persistent state. Transcription needs `faster-whisper` (local; auto
GPU with CPU fallback) OR a cloud key; if neither is present Whisperer still runs
and reports status `engine_unavailable` (a documented degraded mode, NOT a
crash) — the prompt records that verbatim and continues.

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js) enumerates promptName
'prompt-1','prompt-2',... and BREAKS at the first missing slot, so the catalog
must stay a contiguous, gap-free 'prompt-1..N'. Slots 1-73 are occupied (0122
appended the Talker demo at 73); this APPENDS at 74 with no shift of any existing
prompt. Reverse deletes 74. (MAX_PROMPTS=100.)
"""
from django.db import migrations


# Whisperer banner palette — mirrors the ``.canvas-item.whisperer-agent``
# gradient (deep indigo -> royal blue -> sonar cyan -> ice mint).
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#0a1a3f 0%,#1747c4 33%,#18b6c9 66%,#aef0e6 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


WHISPERER_LISTENS_DEMO = (
    "Tlamatini, ejecuta la demo **TLAMATINI ESCUCHA**, por favor &mdash; una muestra básica de tu propio "
    "SPEECH-TO-TEXT (reconocimiento de voz), controlado por completo desde el chat a través del tool wrapper "
    "**chat_agent_whisperer**: ABRES y GRABAS tu micrófono tú misma, corres el reconocedor "
    "neuronal y conviertes el audio hablado en una cadena de texto. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques &mdash; ve directo al Paso 1): "
    "(a) marca SÓLO la casilla **Multi-Turn** antes de enviar (NO se necesita ACPX &mdash; "
    "chat_agent_whisperer es el ÚNICO tool que puedes usar; no uses chat_agent_executer / "
    "chat_agent_pythonxer ni tools de ACPX); (b) Whisperer es 100% autosuficiente para el micrófono "
    "&mdash; lo abre, lo configura y lo graba por su cuenta (no hace falta Recorder); (c) la transcripción "
    "local necesita `faster-whisper` (usa la GPU automáticamente y SIEMPRE cae a CPU) OR una "
    "key de STT en la nube &mdash; si NINGUNA está presente, Whisperer devuelve status `engine_unavailable` (un "
    "modo degradado documentado, NO un error): regístralo tal cual y CONTINÚA. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#127908; TLAMATINI ESCUCHA &#128483;&#65039;</h2>"
    "<div style='opacity:.92;margin-top:4px;'>Tlamatini Whisperer &mdash; micrófono de entrada, texto de salida</div></div>. "
    "\n\n"
    "Paso 1 (graba y transcribe): llama a **chat_agent_whisperer** con el request "
    "\"Transcribe with input_source='mic' and record_seconds=30 and engine='faster-whisper' and "
    "model='base' and device='auto'\". Esto graba 30 segundos del micrófono predeterminado y lo "
    "transcribe. Del bloque INI_SECTION_WHISPERER del log_excerpt de la ejecución captura: engine, "
    "model, device (cuda/cpu), language, status (transcribed | empty | engine_unavailable | error), "
    "word_count, transcript_path y el BODY (el texto reconocido). "
    "\n\n"
    "Paso 2: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Tlamatini Listens &mdash; Reporte de transcripción</strong>' y con las columnas <em>engine</em>, "
    "<em>model</em>, <em>device</em>, <em>language</em>, <em>status</em>, <em>palabras</em>, "
    "<em>transcripción guardada</em> &mdash; una fila, cada valor tal cual del bloque INI_SECTION_WHISPERER "
    "(NO lo reclasifiques). Celdas del cuerpo claras (background:#ffffff;color:#0f172a), tono verde para "
    "status transcribed, tono ámbar para engine_unavailable. Debajo de la tabla, cita el texto "
    "reconocido en un blockquote (o '(no se detectó voz)' cuando esté vacío). "
    "\n\n"
    "Paso 3: cierra con un banner HTML que reutilice el estilo del Paso 0 y muestre, en letras grandes, "
    "'&#9989; TRANSCRITO' (status transcribed &mdash; muestra el conteo de palabras), "
    "'&#128266; SIN VOZ' (status empty) o '&#9881;&#65039; MOTOR NO DISPONIBLE' (status "
    "engine_unavailable &mdash; faster-whisper no instalado y sin key en la nube; anota el arreglo de una línea "
    "'pip install faster-whisper'), y debajo una métrica de una línea "
    "'engine: <engine> &middot; device: <device> &middot; palabras: <word_count>'. "
    "Termina con END-RESPONSE."
)


_NEW_PROMPTS = (
    (74, WHISPERER_LISTENS_DEMO),
)


def add_whisperer_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_whisperer_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0124_add_chat_agent_whisperer_tool'),
    ]

    operations = [
        migrations.RunPython(add_whisperer_demo_prompt, remove_whisperer_demo_prompt),
    ]
