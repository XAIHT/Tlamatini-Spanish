# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Catalog of Prompts — the NEW **VOICE COMMANDS** section (Angela, 2026-09-12).

WHAT THIS IS. A voice command is not "record some audio" and it is not "read this
text aloud" — it is **driving Tlamatini BY speaking**: the microphone becomes the
keyboard, Whisperer's transcript becomes the prompt, and Tlamatini then executes
that prompt with her full tool surface. That is a different thing from everything
in *Media & Voice* (which is about PRODUCING or CONSUMING media: record a WAV,
play a file, speak a sentence, transcribe a clip), so it gets its own section.

WHY IT IS ONLY POSSIBLE NOW. Until v1.51.7 Whisperer recorded a FIXED block of
``record_seconds`` (default 30). A spoken prompt that ran long was cut in half,
and a short one left you talking to an empty room — so "say your prompt out loud"
was never trustworthy enough to put on a card. The **sound gate**
(``record_seconds: 0``, the new default) keeps recording while you are still
talking and stops on its own after ``silence_timeout_seconds`` of silence. THAT is
what makes "speak until you are done" a real, shippable feature, and this section
is its user-facing face.

WHY IT IS FIRST IN THE CATALOG. Angela's explicit instruction: this section goes
at the **VERY BEGINNING**, ahead of *Getting Started*. Speaking is the shortest
path to using Tlamatini at all — you talk, she does it — so it is the first thing
a new user should meet. ``views.PROMPT_CATEGORY_ORDER`` therefore gains
``('voice_commands', 'Voice Commands')`` as entry ZERO. The section header renders
uppercase (``.prompt-category-label { text-transform: uppercase }``), so on screen
it reads exactly **VOICE COMMANDS**.

TWO CARDS, DELIBERATELY:

  * **121 — YOUR FIRST VOICE COMMAND** (``sort_rank`` 10). The section's
    Step-by-Step opener. ⚠️ This is NOT optional padding: Angela's standing rule
    is that *every* section opens with a guided wizard, and
    ``test_prompt_catalog_contiguous.py`` enforces it in two places
    (``test_known_section_openers`` fails for any live section missing from its
    map, and ``test_every_section_opens_with_a_genuine_step_by_step_wizard``
    checks the opener's CONTENT names the Step-by-Step checkbox and promises to
    WAIT). A new section shipped with only one card would go RED.
  * **122 — SPEAK YOUR PROMPT** (``sort_rank`` 20). Angela's card, carrying her
    sentence VERBATIM:
        "Tlamatini, using Whisperer record my voice till I finish to tell you a
         prompt, then use the text extracted as a prompt and invoke it, go!."

MODE BADGES — the natures Angela asked for, produced by CONTENT not by a flag.
``tools_dialog.js::classifyPromptModes`` reads the text and decides, and clicking
the card then ticks exactly those boxes (``applyPromptModesToToggles``):

  * 122 names ``invoke_skill`` / ``acp_spawn`` / ``acp_send_and_wait`` in a
    NON-forbidding sentence ⇒ **ACPX** ⇒ ``['multiturn', 'acpx', 'execreport']``
    = Multi-turn + ACPX + Exec-report, exactly as requested. The ACPX tick is not
    decoration: neither the user nor the model knows what the spoken instruction
    will turn out to need, so the ACPX/Skills surface must ALREADY be bound when
    the transcript lands — with ACPX unchecked, ``filter_acpx_tools`` strips it
    before the executor ever sees it, and a spoken "ask Codex about X" would die
    with no tool to serve it. 122 contains NO hyphenated "step-by-step" token, so
    it is never mis-badged as a wizard.
  * 121 names the Step-by-Step checkbox (and says "Step-by-Step mode"), drives
    ``chat_agent_whisperer``, and contains no ``acp_*`` token ⇒
    ``['multiturn', 'stepbystep', 'execreport']`` — the same shape as every other
    section opener.

CONTRACT COMPLIANCE (all of it, on purpose):
  * APPEND-ONLY ids. 0198 left the catalog at 120, so these are **121** and
    **122** — appended, never renumbered
    (``test_ids_are_contiguous_1_to_n_no_gaps``).
  * ``sort_rank`` 10 / 20. Rank 10 is the RESERVED opener slot; ranks are unique
    inside a section; the section reads least-complex → most-complex (rehearse
    with a guided wizard first, then hand the microphone the real controls).
  * Parameter grammar v1.44.0: ``[[ … — OPTIONAL, default: X ]]`` collected at the
    TOP with the unfilled-guard sentence beneath, so a one-click run still works;
    ``< >`` marks REPORT slots only, never inputs.
  * No hardcoded scratch path (Rules 15/16) — Whisperer writes to its own
    Documents folder.
  * SAFE: the opener rehearses with READ-ONLY actions only, and 122 carries an
    explicit brake — an irreversible spoken instruction is quoted back for
    written confirmation instead of being executed blind.

Reverse deletes exactly these two rows.
"""
from django.db import migrations


_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#160a2e 0%,#5B21B6 33%,#2563EB 66%,#22D3EE 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;text-shadow:0 1px 3px rgba(0,0,0,.5);'>"
)


# ─────────────────────────────────────────────────────────────────────
#  121 · the section's Step-by-Step opener
# ─────────────────────────────────────────────────────────────────────
FIRST_VOICE_COMMAND = (
    "LLENA LOS CAMPOS (opcional — déjalos exactamente como están para una demo de un solo clic):\n"
    "  · En qué micrófono escuchar: [[ "
    "device_name — OPCIONAL, predeterminado: el micrófono predeterminado del sistema ]]\n"
    "  · Cuántos segundos de silencio significan que dejé de hablar: [[ "
    "silence_timeout_seconds — OPCIONAL, predeterminado: 10 ]]\n"
    "Si una línea de llenado de arriba sigue sin llenar, USA SU VALOR PREDETERMINADO "
    "y continúa — nunca te detengas a preguntarme.\n\n"

    "Tlamatini, ejecuta la demo TU PRIMER COMANDO DE VOZ, por favor — la introducción "
    "guiada a hablarte en lugar de escribir. Marca las casillas **Multi-Turn**, "
    "**Exec report** y **Paso a paso** antes de enviar. "
    "El modo Paso a paso es el punto central de esta tarjeta: haz UNA acción, luego "
    "DETENTE y ESPERA mi respuesta antes de hacer la siguiente. Nunca pongas dos pasos "
    "en una sola respuesta, y nunca respondas un paso al que no he llegado todavía.\n\n"

    "Paso 0 — abre con un banner HTML: " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>🎙️ TU PRIMER COMANDO DE VOZ</h2><div "
    "style='opacity:.92;margin-top:4px;'>el micrófono es el teclado</div></div>. "
    "Debajo, explica en DOS oraciones cortas qué es en realidad un comando de voz : "
    "yo hablo, tú transcribes lo que dije con chat_agent_whisperer, y "
    "las palabras que hablé se vuelven la instrucción que luego ejecutas — el "
    "micrófono reemplaza al teclado, nada más cambia. Luego pídeme que responda READY "
    "en cuanto mi micrófono esté conectado y el cuarto esté razonablemente en silencio. DETENTE "
    "AHÍ y ESPERA mi READY.\n\n"

    "Paso 1 (SÓLO después de que responda READY) — una prueba de escucha, para descubrir si la máquina "
    "puede oírme siquiera antes de confiarle una instrucción. Llama a "
    "**chat_agent_whisperer** con el request \"Transcribe with input_source='mic' and "
    "silence_timeout_seconds={{ventana de silencio}} and engine='faster-whisper' and "
    "model='base' and device='auto'\", agregando device_name='{{nombre del dispositivo}}' "
    "sólo si nombré uno. ⚠️ **Deja record_seconds fuera por completo.** "
    "Omitirlo es lo que arma la SOUND GATE, así que la grabación dura exactamente lo que "
    "yo siga hablando y termina sola después de la ventana de silencio; pasar cualquier "
    "número apagaría la compuerta y grabaría un bloque fijo en su lugar. Antes de llamarla, "
    "dime en UNA línea que diga en voz alta una oración corta de prueba ahora. "
    "Después lee el bloque INI_SECTION_WHISPERER del "
    "log_excerpt de la ejecución y reporta, en una tabla HTML pequeña: status <status>, lo que "
    "escuchaste <el texto reconocido>, cómo se detuvo <stop_reason>, cuánto tiempo "
    "escuchó <duration_seconds>, cuánto de eso fue mi voz <speech_seconds>, "
    "y qué engine y device lo corrieron <engine / device>. Luego pídeme que responda "
    "YES si eso es lo que dije, o NO si está mal. DETENTE y ESPERA.\n\n"

    "Paso 2 (SÓLO después de que responda) — si dije NO, dime las dos cosas que lo arreglan "
    "casi siempre (elige otro micrófono con device_name, o usa un "
    "modelo más grande como 'small' o 'large-v3-turbo') y ofrécete a repetir el Paso 1; "
    "luego DETENTE y ESPERA. Si dije YES, ahora ensaya un comando de voz REAL: dime "
    "que hable una instrucción esta vez en lugar de una oración, y sugiéreme una "
    "inofensiva en voz alta, por ejemplo preguntarte qué hora es o cuántos "
    "agents tienes. Llama a chat_agent_whisperer exactamente como en el Paso 1, cítame el "
    "transcript de regreso palabra por palabra en un blockquote, y luego EJECUTA lo que "
    "dije — pero para este ensayo limítate a trabajo de SÓLO LECTURA "
    "(responder, listar, contar, resumir). Si lo que hablé fuera a escribir, "
    "borrar, enviar, instalar, gastar dinero o tocar una máquina que no es mía, "
    "detente: cítalo de regreso, di claramente que el ensayo se queda en sólo lectura, y "
    "señálame la tarjeta DI TU PROMPT de esta misma sección, que está hecha para "
    "lo de verdad. Luego pídeme que responda DONE. DETENTE y ESPERA.\n\n"

    "Paso 3 (SÓLO después de que responda DONE) — cierra con un REPORTE DE PREPARACIÓN DE VOZ: "
    "una tabla HTML en los colores del Paso 0 con el micrófono <device>, engine "
    "y model <engine / model>, ventana de silencio <silence_timeout_seconds>, "
    "la calidad de la transcripción según la juzgué <YES o NO del Paso 1>, y "
    "si el comando ensayado corrió <sí / detenido porque no era de sólo lectura>. "
    "Debajo, UNA oración diciéndome que la siguiente tarjeta a probar es DI TU "
    "PROMPT, donde lo que yo diga se vuelve el prompt que de verdad ejecutas. "
    "Termina con END-RESPONSE."
)


# ─────────────────────────────────────────────────────────────────────
#  122 · Angela's card — her sentence is the operative instruction
# ─────────────────────────────────────────────────────────────────────
SPEAK_YOUR_PROMPT = (
    "LLENA LOS CAMPOS (opcional — déjalos exactamente como están para una demo de un solo clic):\n"
    "  · Cuántos segundos de silencio significan que terminé de hablar: [[ "
    "silence_timeout_seconds — OPCIONAL, predeterminado: 10 ]]\n"
    "  · El idioma en el que voy a hablar: "
    "[[ language — OPCIONAL, predeterminado: detección automática ]]\n"
    "Si una línea de llenado de arriba sigue sin llenar, USA SU VALOR PREDETERMINADO "
    "y continúa — nunca te detengas a preguntarme.\n\n"

    "Tlamatini, ejecuta la demo DI TU PROMPT, por favor. Esta es la tarjeta donde "
    "mi VOZ es el prompt, y aquí está la instrucción, en mis propias palabras:\n\n"
    "  «Tlamatini, usando Whisperer graba mi voz hasta que termine de decirte un "
    "prompt, luego usa el texto extraído como prompt e invócalo, ¡dale!.»\n\n"

    "Paso 0 — abre con un banner HTML: " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>🗣️ DI TU PROMPT</h2><div "
    "style='opacity:.92;margin-top:4px;'>dilo — yo lo hago</div></div>. "
    "Debajo, UNA línea diciéndome que la grabación empieza ahora mismo, que debo "
    "hablar cuando esté listo, y que te detendrás sola en cuanto haya estado en "
    "silencio durante la ventana de silencio — para que nunca me quede sin saber cuánto "
    "esperar.\n\n"

    "Paso 1 (ESCUCHA HASTA QUE TERMINE) — llama a **chat_agent_whisperer** con el request "
    "\"Transcribe with input_source='mic' and "
    "silence_timeout_seconds={{ventana de silencio}} and engine='faster-whisper' and "
    "model='base' and device='auto' and language='{{idioma}}'\". ⚠️ **Deja "
    "record_seconds fuera por completo.** Ese parámetro es el interruptor de modo: omitirlo "
    "(0) es lo que arma la SOUND GATE, así que puedo tardar lo que necesite en decir "
    "lo que quiero y la grabación termina sola en cuanto me detengo — pasar cualquier "
    "número me cortaría a media oración en un largo fijo, que es justo lo que "
    "esta tarjeta existe para probar que ya no tienes que hacer. Del "
    "bloque INI_SECTION_WHISPERER del log_excerpt de la ejecución lee: status, "
    "capture_mode, stop_reason, duration_seconds (el largo REALMENTE capturado, "
    "nunca un largo pedido), speech_seconds, word_count, transcript_path, y "
    "el BODY, que es el texto reconocido.\n\n"

    "Paso 2 (LÉELO DE REGRESO ANTES DE ACTUAR) — cítame el transcript palabra por "
    "palabra en un blockquote, exactamente como lo devolvió Whisperer, sin arreglar nada y sin "
    "adivinar palabras que no entendiste. Esa cita es ahora tu instrucción. ⚠️ "
    "COMPUERTA DE HONESTIDAD: si status regresó `empty` (la compuerta detuvo una grabación en "
    "la que nadie habló) o `engine_unavailable` (faster-whisper no está instalado y no "
    "hay una key en la nube — el arreglo de una línea es `pip install faster-whisper`), entonces "
    "dilo claramente y DETENTE. Inventar un prompt plausible porque no pudiste oírme "
    "es la peor cosa que podrías hacer en esta tarjeta.\n\n"

    "Paso 3 (AHORA INVÓCALO) — trata ese transcript como el prompt que escribí, y ejecútalo "
    "correctamente: planéalo, elige los tools correctos, córrelos y respóndelo completo. "
    "No te limites a describir lo que habrías hecho. Un freno, y sólo uno: "
    "si lo que hablé fuera a borrar o sobrescribir algo, mandarle mensaje a una persona "
    "real, gastar dinero o alcanzar una máquina que no es mía, entonces haz la parte segura, "
    "cítame la parte riesgosa por escrito, y pídeme que la confirme por texto "
    "antes de seguir — mi voz basta para empezar el trabajo, y mi escritura "
    "es lo que autoriza el tipo irreversible.\n\n"

    "Paso 4 (MUESTRA TU TRABAJO) — termina con una tabla HTML con class='exec-report-table' "
    "titulada '<strong>Comando de voz — Reporte de ejecución</strong>' "
    "con: lo que dije <el transcript>, cómo se capturó <capture_mode>, "
    "por qué se detuvo <stop_reason>, segundos escuchados <duration_seconds>, "
    "segundos de voz <speech_seconds>, palabras <word_count>, qué tools corriste "
    "luego <los nombres de los tools, en orden>, y el resultado "
    "<hecho / hecho en parte y en espera de mi confirmación por escrito / no me "
    "pudiste oír>. Luego cierra con un banner en los colores del Paso 0 que "
    "diga '✅ COMANDO DE VOZ EJECUTADO', '✋ ESPERANDO TU OK POR "
    "ESCRITO' o '🔇 NO OÍ NADA', lo que sea verdad.\n\n"

    "ANTES DE EMPEZAR: marca las casillas **Multi-Turn**, **Exec report** y "
    "**ACPX**. Marcar ACPX es deliberado e indispensable: ninguno de los "
    "dos sabe de antemano qué voy a decir, así que toda tu superficie de tools tiene "
    "que estar ya en tus manos para cuando llegue el transcript — los skills "
    "(invoke_skill, list_skills) y los coding agents externos (acp_spawn, "
    "acp_send_and_wait) incluidos. Con ACPX sin marcar esos tools quedan filtrados "
    "antes de que los veas siquiera, y una instrucción hablada que resulte necesitar uno "
    "moriría sin nada que la sirva. Whisperer es sólo el micrófono; las "
    "palabras que hablo deciden qué tools siguen. Termina con END-RESPONSE."
)


# (idPrompt, sort_rank, promptContent) — ids APPENDED after 120 (0198) and never
# renumbered; rank 10 is the reserved Step-by-Step opener slot, 20 is Angela's
# card. Both land in the brand-new 'voice_commands' section.
_NEW_PROMPTS = (
    (121, 10, FIRST_VOICE_COMMAND),
    (122, 20, SPEAK_YOUR_PROMPT),
)


def add_voice_command_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, rank, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={
                'promptName': 'prompt-%d' % prompt_id,
                'promptContent': content,
                'category': 'voice_commands',
                'sort_rank': rank,
            },
        )


def remove_voice_command_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(
        idPrompt__in=[prompt_id for prompt_id, _rank, _content in _NEW_PROMPTS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0200_whisperer_demo_prompt_sound_gate'),
    ]

    operations = [
        migrations.RunPython(add_voice_command_prompts, remove_voice_command_prompts),
    ]
