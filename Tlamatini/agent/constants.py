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

# ─────────────────────────────────────────────────────────────────────────
#  TLAMATINI SPEAKS IN THE FIRST PERSON  (Angela, 2026-07-29)
#
#  Every string below is something SHE says to the user, so she says it as
#  HERSELF: "estoy lista", "estoy procesando tu request", "ya me reconecté".
#  They used to be written ABOUT her in the third person — "Tlamatini está
#  lista, ahora puedes platicar con ella" — which reads like a status report
#  written by someone else standing next to her. She is the one in the
#  conversation; she should sound like it.
#
#  Two rules when you add or edit one of these:
#    1. FIRST PERSON. She is talking, not being described. Never "Tlamatini
#       hace X" in a chat message; write "hago X". (Her NAME may still appear
#       when she introduces herself — "Hola, soy Tlamatini" — that is her
#       speaking, not narration.)
#    2. Address the user as "tú", warmly and directly, and never as "el
#       usuario". "Cancelaste la generación", not "El usuario canceló".
#
#  ⚠️ COUPLED MATCHERS — these strings are READ by code, not only displayed:
#       agent/static/agent/js/avatar.js       (picks her facial expression)
#       agent/static/agent/js/agent_page_ui.js (busy/ready detection)
#       .claude/skills/.../harness/config.py   (busy-banner filter in tests)
#  Change the wording here and those must change in the SAME pass, or the
#  avatar shows the wrong mood and the test harness records a busy banner as
#  a real answer. They are kept tolerant of both the old and new phrasings.
# ─────────────────────────────────────────────────────────────────────────

# Error messages
ERROR_AGENT_NOT_READY = "No puedo procesar tus requests. <br> Revisa que no hayas puesto un context fuera del root directory. <br> Si todo está correcto, revisa que Ollama esté corriendo y que el archivo config.json sea correcto."
ERROR_NOT_AUTHENTICATED = "No has iniciado sesión."
ERROR_AGENT_NOT_READY_SIMPLE = "Todavía no estoy lista. Inténtalo de nuevo en un momento."
ERROR_DIRECTORY_OUTSIDE_ROOT = "El directorio que elegiste está fuera del root path de la aplicación, así que no lo puedo usar."

# System messages
MSG_AGENT_LOADING = "Me estoy cargando. Espérame tantito."
MSG_AGENT_LOADING_CONTEXT = "Estoy cargando el context. Espérame tantito."
MSG_AGENT_READY = "Hola, soy Tlamatini, estoy lista para platicar contigo."
MSG_AGENT_FALLBACK = "Hubo un problema, así que me pasé a una Basic Prompt Only Chain (no voy a usar ningún context)."
MSG_OVERSIZED_DOCS_WARNING = "Hola, soy Tlamatini, estoy lista para platicar contigo. Nada más que algunos documentos están muy grandes; puede que no logre cargarlos completos."
MSG_PROCESSING_REQUEST = "Estoy procesando tu request. Espérame tantito."
MSG_LLM_CANCELLED = 'Cancelaste lo que estaba generando, así que no te voy a mostrar nada. Voy a borrar el context.'
MSG_LLM_CONNECTION_DESTROYED = '✓ Cerré por completo mi conexión con Ollama. Ollama ya quedó libre.'
MSG_LLM_REBUILDING = '⏳ Me estoy reconstruyendo con una conexión nueva...'
MSG_LLM_REESTABLISHED = '✓ Ya me restablecí. Podemos seguir platicando.'
MSG_LLM_RECONNECT = "Me pediste reconectarme: ya lo hice y borré el context."
MSG_LLM_CLEARCONTEXT = "Me pediste limpiar mi context: ya lo borré y me reconecté."
MSG_LLM_HISTORY_CLEANED = "Limpié el historial del chat y me reconecté."
MSG_SESSION_RESTORED = "Qué bueno que volviste, ya restauré tu sesión."
MSG_SESSION_AND_CONTEXT_RESTORED = "Qué bueno que volviste, ya restauré tu sesión y tu context."
MSG_GREETING_RESPONSE = "¡Con mucho gusto, aquí estoy para ayudarte!"

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
REGEX_GREETING = r"^\s*(hello|hi|hey|thanks|thank you|you are awesome|awesome|hola|holis|qué onda|que onda|buenas|buenos días|buenas tardes|buenas noches|gracias|muchas gracias|eres increíble|eres genial)\b.*$"

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