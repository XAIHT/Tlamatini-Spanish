# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Retarget the TLAMATINI LISTENS demo (prompt 74) at the SOUND GATE (2026-09-11).

Whisperer's microphone capture stopped being a fixed block: `record_seconds: 0`
(the new default) turns on a sound gate that keeps recording while the speaker is
still talking and stops after `silence_timeout_seconds` of silence.

The demo written in migration 0125 told Tlamatini to pass `record_seconds=30` —
which now explicitly TURNS THE GATE OFF. Left alone, the single most-clicked
Whisperer prompt in the catalog would have demonstrated the OLD behaviour and
quietly taught both the user and the model the wrong pattern.

⚠️ CONTRACT: this migration rewrites ONLY `promptContent`, exactly like the
0182-0185 grammar batch. `idPrompt`, `promptName`, `category`, `sort_rank` and
`hidden` are untouched, so catalog ordering and contiguity are unaffected.
"""

from django.db import migrations


_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#0a1a3f 0%,#1747c4 33%,#18b6c9 66%,#aef0e6 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


WHISPERER_LISTENS_DEMO = (
    "[[ VENTANA DE SILENCIO &mdash; ¿cuántos segundos de silencio deben terminar la "
    "grabación? &mdash; OPCIONAL, "
    "predeterminado: 10 ]]\n"
    "[[ QUÉ DECIR &mdash; una oración para leer en voz alta en cuanto empiece "
    "la grabación &mdash; OPCIONAL, predeterminado: di lo "
    "que quieras ]]\n"
    "Si una línea de llenado de arriba sigue sin llenar, USA SU VALOR PREDETERMINADO "
    "y continúa &mdash; nunca te detengas "
    "a preguntar.\n\n"
    "Tlamatini, ejecuta la demo **TLAMATINI ESCUCHA**, por favor &mdash; una muestra básica de "
    "tu propio SPEECH-TO-TEXT (reconocimiento de voz), controlado por completo desde el chat a través del tool "
    "wrapper **chat_agent_whisperer**: ABRES y GRABAS tu micrófono tú misma, corres el "
    "reconocedor neuronal y conviertes el audio hablado en una cadena de "
    "texto. PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques &mdash; ve directo al "
    "Paso 1): (a) marca SÓLO la casilla **Multi-Turn** antes de enviar (NO se necesita ACPX "
    "&mdash; chat_agent_whisperer es el ÚNICO tool que puedes usar; no uses chat_agent_executer "
    "/ chat_agent_pythonxer ni tools de ACPX); (b) Whisperer es 100% autosuficiente para el micrófono "
    "&mdash; lo abre, lo configura y lo graba por su cuenta (no hace falta Recorder); (c) la transcripción "
    "local necesita `faster-whisper` (usa la GPU automáticamente y SIEMPRE cae a CPU) O una "
    "key de STT en la nube &mdash; si NINGUNA está presente, Whisperer devuelve status `engine_unavailable` (un "
    "modo degradado documentado, NO un error): regístralo tal cual y CONTINÚA. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#127908; TLAMATINI ESCUCHA &#128483;&#65039;</h2><div "
    "style='opacity:.92;margin-top:4px;'>Tlamatini Whisperer &mdash; la compuerta de sonido: "
    "sigo escuchando mientras hablas</div></div>. "
    "Debajo, dile al usuario en UNA línea que la grabación empieza ahora, que debe hablar "
    "cuando esté listo, y que te detendrás sola en cuanto haya estado en silencio durante la ventana de "
    "silencio &mdash; para que no se quede sin saber cuánto esperar. "
    "\n\n"
    "Paso 1 (ESCUCHA y transcribe): llama a **chat_agent_whisperer** con el request "
    "\"Transcribe with input_source='mic' and silence_timeout_seconds={{ventana de silencio}} and "
    "engine='faster-whisper' and model='base' and device='auto'\". "
    "&#9888;&#65039; **NO PASES record_seconds EN ABSOLUTO.** Ese parámetro es el interruptor de modo: "
    "dejarlo fuera (0) es lo que arma la COMPUERTA DE SONIDO, así que la grabación dura exactamente lo que "
    "el hablante siga hablando y termina después de la ventana de silencio. Pasar cualquier número apagaría "
    "la compuerta y grabaría un bloque fijo en su lugar &mdash; que es justo lo que esta demo "
    "existe para mostrarte que ya no tienes que hacer. "
    "Del bloque INI_SECTION_WHISPERER del log_excerpt de la ejecución lee y captura: engine, model, "
    "device (cuda/cpu), language, status (transcribed | empty | engine_unavailable | error), "
    "capture_mode (gated | fixed), stop_reason (silence | duration | max_duration | "
    "fixed_fallback), duration_seconds (la duración REALMENTE capturada, no una duración pedida), "
    "speech_seconds, word_count, transcript_path y el BODY (el texto reconocido). "
    "\n\n"
    "Paso 2: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Tlamatini escucha &mdash; Reporte de transcripción</strong>' y con las columnas <em>engine</em>, "
    "<em>model</em>, <em>device</em>, <em>language</em>, <em>modo de captura</em>, "
    "<em>se detuvo porque</em>, <em>grabado (s)</em>, <em>voz (s)</em>, <em>status</em>, "
    "<em>palabras</em>, <em>transcripción guardada</em> &mdash; una fila, cada valor tal cual del "
    "bloque INI_SECTION_WHISPERER (NO lo reclasifiques). Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a), tono verde para status transcribed, tono ámbar para "
    "engine_unavailable. Debajo de la tabla, cita el texto reconocido en un blockquote "
    "(o '(no se detectó voz)' cuando esté vacío). Luego agrega UNA oración corta que lea la compuerta en voz "
    "alta, p. ej. 'Escuché durante <duration_seconds>s, <speech_seconds>s de los cuales fueron tu voz, "
    "y me detuve porque <stop_reason>.' "
    "\n\n"
    "Paso 3: cierra con un banner HTML que reutilice el estilo del Paso 0, en letras grandes, "
    "'&#9989; TRANSCRITO' (status transcribed &mdash; muestra el conteo de palabras), "
    "'&#128266; SIN VOZ' (status empty &mdash; la compuerta detuvo una grabación en la que nadie habló, "
    "lo cual es la compuerta funcionando, no un error) o '&#9881;&#65039; MOTOR NO DISPONIBLE' (status "
    "engine_unavailable &mdash; faster-whisper no instalado y sin key en la nube; anota el arreglo de una línea "
    "'pip install faster-whisper'), y debajo una métrica de una línea "
    "'engine: <engine> &middot; device: <device> &middot; capturado: <duration_seconds>s "
    "&middot; se detuvo: <stop_reason> &middot; palabras: <word_count>'. "
    "Termina con END-RESPONSE."
)


_REWRITTEN_PROMPTS = (
    (74, WHISPERER_LISTENS_DEMO),
)


def retarget_whisperer_demo_at_the_gate(apps, schema_editor):
    """Rewrite ONLY promptContent for the listed ids. A missing row is skipped."""
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _REWRITTEN_PROMPTS:
        Prompt.objects.filter(idPrompt=prompt_id).update(promptContent=content)


def noop_reverse(apps, schema_editor):
    """Irreversible by design: the previous text taught a now-wrong pattern.

    Reversing is a no-op rather than an error so the migration can always be
    unapplied; re-running 0125 is the way back to the historical wording.
    """
    return None


class Migration(migrations.Migration):

    dependencies = [('agent', '0199_dedupe_llm_program_snippet_names')]

    operations = [
        migrations.RunPython(retarget_whisperer_demo_at_the_gate, noop_reverse),
    ]
