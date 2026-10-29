# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
# agent/constants.py

# ── Tlamatini speaks in the FIRST PERSON (Angela, 2026-10-09) ──────────────
# Every fixed line below is a chat message FROM Tlamatini, and the chat avatar
# reads each one aloud word for word (avatar.js). So they are written the way
# she talks: in the first person, warmly, and to the user by NAME.
#
#   ``{name}`` is filled by ``say(template, name)`` at the send site, with
#   ``display_name(user)``. With no name it drops out cleanly.
#
# ⚠️ Several of these lines are RECOGNISED BY THEIR WORDS. Change a phrase
# here and update its matchers in the same pass, or the chat page stops
# knowing it is busy / ready / restored:
#   * agent_page_ui.js   isBusyMessageRequest / isBusyMessageContext /
#                        isSessionRestoredInfoMessage
#   * agent_page_chat.js the context-directory error branch
#   * avatar.js          classify()
#   * agents/teletlamatini/teletlamatini.py  _NOISE / _FAILURE substrings
#   * .claude/skills/tlamatini-daily-chat-test/harness/config.py markers
# The old (third-person) phrases stay in those matchers on purpose, so a
# chat history or an older server still reads correctly.


from .agents.talker.spanish_pronunciation import accent_name


def display_name(user):
    """The name Tlamatini calls the user by: the first word of the first
    name, else the username with a capital letter, else ''. Never raises."""
    try:
        first = str(getattr(user, 'first_name', '') or '').strip()
        if first:
            return accent_name(first.split()[0])
        raw = str(getattr(user, 'username', '') or '').strip()
        return accent_name(raw[:1].upper() + raw[1:])
    except Exception:  # noqa: BLE001 - a greeting must never break a send
        return ''


def say(template, name=''):
    """Fill ``{name}`` in one of the lines below. With no name the
    placeholder and its comma vanish: "I'm ready, {name}!" -> "I'm ready!"."""
    text = str(template or '')
    name = str(name or '').strip()
    if name:
        return text.replace('{name}', name)
    for gap, keep in ((', {name},', ','), (', {name}', ''), (' {name}', ''), ('{name}', '')):
        text = text.replace(gap, keep)
    return text


# Error messages
ERROR_AGENT_NOT_READY = "Lo siento, {name}, ahorita no puedo procesar tus solicitudes. <br> Revisa que no me hayas dado un contexto fuera del directorio raíz. <br> Y asegúrate de que tu solicitud quepa en mi CONTEXT-WINDOW: mira el medidor CONTEXT-WINDOW arriba del cuadro de mensaje; si está en rojo o pasa del 100%, desmarca agents o tools en Config > Configurar Agents / Configurar MCPs, o activa Compact mode. <br> Si todo se ve bien, revisa que Ollama esté corriendo y que mi archivo config.json esté correcto."
ERROR_NOT_AUTHENTICATED = "Lo siento, pero no has iniciado sesión, así que todavía no puedo ayudarte. Vuelve a iniciar sesión."
ERROR_AGENT_NOT_READY_SIMPLE = "Todavía no estoy lista, {name}. Dame un momento y vuelve a intentarlo."
ERROR_DIRECTORY_OUTSIDE_ROOT = "Lo siento, {name}, ese directorio está fuera del path raíz de mi aplicación, así que no tengo permitido usarlo."
ERROR_FILE_OUTSIDE_ROOT = "Lo siento, {name}, ese archivo está fuera del path raíz de mi aplicación, así que no tengo permitido usarlo."
ERROR_NOT_A_DIRECTORY = "Lo siento, {name}, lo que elegiste no es un directorio válido."
ERROR_INVALID_CANVAS_FILENAME = "Lo siento, {name}, recibí un nombre de archivo de canvas inválido, así que no pude usarlo."
ERROR_DETAIL_PREFIX = "Este es el error que encontré: "

# System messages
MSG_AGENT_LOADING = "Espera un momento, {name}: me estoy preparando."
MSG_AGENT_LOADING_CONTEXT = "Espera un momento, {name}: estoy cargando el contexto que me diste."
MSG_AGENT_STILL_LOADING = "Todavía me estoy preparando, {name}. Espera un momento y vuelve a intentarlo."
MSG_AGENT_READY = "¡Estoy lista, {name}! Ya puedes empezar a platicar conmigo."
MSG_AGENT_FALLBACK = "Tuve un problema, {name}, así que cambié a mi Basic Prompt Only Chain: por ahora voy a responder sin contexto."
MSG_OVERSIZED_DOCS_WARNING = "¡Estoy lista, {name}! Pero algunos de tus documentos son demasiado grandes, así que quizá no pueda cargarlos completos."
MSG_PROCESSING_REQUEST = "Estoy trabajando en tu solicitud, {name}. Espera un momento."
MSG_LLM_CANCELLED = "Está bien, {name}: lo cancelaste, así que dejé de generar. No voy a enviar esa respuesta y ya borré el contexto."
MSG_LLM_CONNECTION_DESTROYED = "✓ Cerré mi conexión con Ollama, así que Ollama ya está libre."
MSG_LLM_REBUILDING = "⏳ Me estoy reconstruyendo con una conexión nueva..."
MSG_LLM_REESTABLISHED = "✓ Ya volví y estoy lista, {name}. Podemos seguir platicando."
MSG_LLM_CANCEL_WARNING = "⚠ Terminé de cancelar, {name}, pero con una advertencia: "
MSG_LLM_RECONNECT = "Ya hice la reconexión que me pediste, {name}. Borré el contexto y estoy conectada otra vez."
MSG_LLM_CLEARCONTEXT = "Ya limpié el contexto como me pediste, {name}, y estoy conectada otra vez."
MSG_LLM_HISTORY_CLEANED = "Ya borré nuestro historial del chat, {name}, y estoy conectada otra vez. ¡Empezamos de cero!"
MSG_SESSION_RESTORED = "¡Qué gusto verte de nuevo, {name}! Restauré nuestra sesión."
MSG_SESSION_AND_CONTEXT_RESTORED = "¡Qué gusto verte de nuevo, {name}! Restauré nuestra sesión y tu contexto."
MSG_GREETING_RESPONSE = "¡Es un gusto, {name}! Aquí estoy para ayudarte."
MSG_OMISSIONS_EMPTY = "Necesito al menos una extensión de archivo, {name}. Dámelas en este formato: jpg,bmp,etc."
# {omissions} is filled AFTER say(), so the user's own text is never expanded.
MSG_OMISSIONS_SAVED = "Ya guardé las extensiones de archivo que voy a omitir al cargar el contexto: {omissions}.\n\nReconéctame para que pueda aplicar los cambios, {name}."
MSG_SKILLS_SAVED = "Ya actualicé tus skills, {name} ({touched} skill(s)). Voy a usar el cambio desde tu siguiente solicitud."
MSG_TOGGLES_LINKED = "\n\nTambién cambié estos para que coincidan: "
MSG_TOGGLES_APPLY = "\n\nLo voy a usar desde tu siguiente mensaje, {name}; no hace falta reiniciar."
MSG_COMPACT_BUSY = "No cambié Compact mode, {name}: todavía estoy respondiendo. Vuelve a intentarlo cuando termine."
MSG_COMPACT_ERROR = "No pude cambiar Compact mode, {name}: "
MSG_COMPACT_ON = ("¡Listo, {name}! Compact mode está ACTIVADO: desmarqué todos los MCPs, tools, agents y skills excepto "
                  "System-Metrics, Files-Search y Current-Time. Marca lo que necesites en "
                  "Config > Configurar MCPs / Configurar Agents; el medidor CONTEXT-WINDOW muestra "
                  "cuánto cuesta.")
MSG_COMPACT_OFF = ("¡Listo, {name}! Compact mode está DESACTIVADO: volví a marcar todos los MCPs, tools, agents y skills, "
                   "y tus External MCPs regresaron.")
MSG_SELF_MODIFY_BUSY = "No cambié Self-modify, {name}: todavía estoy respondiendo. Vuelve a intentarlo cuando termine."
MSG_SELF_MODIFY_ERROR = "No pude cambiar Self-modify, {name}: "
MSG_SELF_MODIFY_ON = ("¡Listo, {name}! Self-modify está ACTIVADO: ahora mi autoconocimiento va con cada solicitud que mi modelo "
                      "pueda contener, así que puedo leer, cambiar y reconstruir mi propio código fuente.")
MSG_SELF_MODIFY_OFF = ("¡Listo, {name}! Self-modify está DESACTIVADO: ya no recibo mi autoconocimiento y no voy a "
                       "leer, editar ni reconstruir mi propio código fuente.")
MSG_DROP_NOT_SAVED = "Nunca guardé este mensaje en nuestro historial, {name}, así que no hay nada que descartar."
MSG_DROP_STILL_ANSWERING = "Todavía estoy respondiendo, {name}. Vuelve a descartar el mensaje cuando termine."

# Regex patterns for code extraction
REGEX_NAMED_CODE_BLOCK = r'(BEGIN-CODE<<<|begin-code)([-\w./\\]+)>>>([\s\S]*?)(END-CODE|end-code)'
REGEX_UNNAMED_CODE_BLOCK = r'(?:BEGIN-CODE|begin-code)\s*\r?\n([\s\S]*?)\r?\n?(?:END-CODE|end-code)'
REGEX_CODE_BEGIN = r'(BEGIN-CODE<<<|begin-code)([-\w./\\]+)>>>'
REGEX_CODE_BEGIN_NO_NAME = r'(?:BEGIN-CODE|begin-code)'
REGEX_CODE_END = r'(END-CODE|end-code)'
REGEX_CODE_APOS = r'```'
REGEX_SNIPPET_WITH_LANG = r'```(python|bash|javascript|java|c|c\+\+|c#|php|ruby|go|lisp|fortran|basic|assembler|html|css|sql|yaml|typescript|cuda|xml|json)\r?\n([\s\S]*?)\r?\n?```'
REGEX_DOUBLE_BR = r'(<br>\n?)+'
REGEX_LANG_MARKER = r'\r?\n[ \t]*(python|bash|javascript|java|c|c\+\+|c#|php|ruby|go|lisp|fortran|basic|assembler|html|css|sql|yaml|typescript|cuda|xml|json)\r?\n'

# Regex pattern for ASCII / box-drawing diagrams emitted by the LLM
# between BEGIN-DIAGRAM / END-DIAGRAM wrappers (rule 13 in prompt.pmt).
# Mirrors the BEGIN-CODE / END-CODE pair but without a filename slot.
REGEX_DIAGRAM_BLOCK = r'(?:BEGIN-DIAGRAM|begin-diagram)\s*\r?\n([\s\S]*?)\r?\n?(?:END-DIAGRAM|end-diagram)'

# Greeting patterns
REGEX_GREETING = r"^\s*(hello|hi|hey|thanks|thank you|you are awesome|awesome)\b.*$"

# File extension map for code snippets
EXTENSION_MAP = {
    'python': '.py',
    'bash': '.sh',
    'javascript': '.js',
    'java': '.java',
    'c': '.c',
    'c++': '.cpp',
    'c#': '.cs',
    'php': '.php',
    'ruby': '.rb',
    'go': '.go',
    'lisp': '.lisp',
    'fortran': '.f90',
    'basic': '.bas',
    'assembler': '.asm',
    'html': '.html',
    'css': '.css',
    'sql': '.sql',
    'typescript': '.ts',
    'yaml': '.yaml',
    'cuda': '.cu',
    'xml': '.xml',
    'json': '.json',
}

# Canvas Undo/Redo configuration
CANVAS_UNDO_HISTORY_LIMIT = 1024
