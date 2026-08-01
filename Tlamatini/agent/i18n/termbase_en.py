"""Do-Not-Translate termbase: every term that stays ENGLISH in the Spanish GUI.

THE REGISTER RULE
-----------------
When Tlamatini is localized to Spanish, the GUI changes only the MINIMUM
necessary. **Spanish supplies the GRAMMAR; English supplies the TECHNICAL
LEXICON.** This is how Mexican developers actually speak. Angela Lopez
Mendoza's canonical example:

    "Haciendo un Pod en Dockerer y creando un Container en Kubernetes
     y haciendo el deployment en la LPAR"

Spanish carries it: *haciendo, creando, en, la, y*. English stays put:
*Pod, Dockerer, Container, Kubernetes, deployment, LPAR*.

WHY (Matrix Language Frame)
---------------------------
This is not a style preference, it is a documented bilingual grammar.
Myers-Scotton's Matrix Language Frame model (``Duelling Languages``,
Oxford: Clarendon Press, 1993) says the MATRIX language supplies the
morphosyntax and the system morphemes, while the EMBEDDED language
supplies the content morphemes. Here Spanish is the matrix (articles,
prepositions, inflection: *un* Pod, *la* LPAR) and English is embedded
(the content nouns). Multi-word feature names such as ``Exec Report`` are
EL islands. Iakovenko & Hain (2024, arXiv:2410.02521) confirm empirically
that in real English/Spanish code-switching Spanish is preferred as the
matrix language.

The correctness argument is also already in the literature: Lazaro
Carreter (1998: 587), cited in Garriga Escribano, 'Anglicismos en la
ciencia y en la tecnica' (in Rodriguez Gonzalez, ed., *Anglicismos en el
espanol contemporaneo*, Peter Lang, 2022, pp. 117-138), endorses
UNADAPTED technical anglicisms precisely because they preserve
*biunivocidad* -- one term to one concept, internationally. Every term
that does NOT shift between locales is one less surface on which a
Spanish request and an English request can diverge. Keeping this list
large makes the correctness guarantee STRONGER, not weaker.

SCOPE
-----
* Protected here  -> render verbatim, in English, in Spanish UI strings.
* NOT protected   -> translate freely (generic verbs, connectives, prose).
  See ``SPANISH_PREFERRED`` for terms that deliberately DO become Spanish.
* ``tlamatini.log`` is an engineering artifact, not user-facing prose:
  it stays English and mixed English/Spanish output there is expected.
* All internals are always English and are never localized: source code,
  identifiers, comments, config keys, CLI flags, protocol sentinels,
  agent display names, tool names, CSS classes, environment variables.

CONTRACT
--------
DATA ONLY. Standard library only. This module imports NOTHING, so it
loads identically inside Django, inside a pool subprocess, and inside a
bare test harness.

Machine-derived families (AGENT_DISPLAY_NAMES, TOOL_NAMES) are HARVESTED
from the source of truth, never hand-typed:
  * ``agent/services/agent_paths.py::display_name_from_agent_type``
  * ``agent/chat_agent_registry.py::ChatWrappedAgentSpec``
  * ``agent/acpx/tools.py``, ``agent/tools.py``,
    ``agent/external_mcp_manager.py`` (@tool functions)
Regenerate rather than edit those two families by hand.
"""


# ===========================================================================
# 1. MACHINE SENTINELS
# ---------------------------------------------------------------------------
# Protocol literals parsed by code, by regex, or by a downstream Forker.
# Translating ANY of these silently breaks parsing -- they are wire format,
# not prose. Verified against source, not assumed.
# ===========================================================================
MACHINE_SENTINELS = (
    'END-RESPONSE',
    'BEGIN-CODE',
    'END-CODE',
    'INI_SECTION_',
    'END_SECTION_',
    '<!--TLAMATINI_EXEC_REPORT_BOUNDARY-->',
    'TLM_VERDICT::',
    'FRAME_VERDICT',
    'FINAL_VERDICT',
    'CONFIDENCE',
    'VERDICT:',
    'PASS_OK',
    'FAIL_NO_MOTION',
    'FAIL_WRONG_MOTION',
    'UNCLEAR',
    'ANALYSIS_ERROR',
    'APPROVE',
    'REQUEST_CHANGES',
    'COMMENT',
    'completed',
    'failed',
    'stopped',
    'running',
    'SUCCESS',
    'FAILURE',
)


# ===========================================================================
# 2. AGENT DISPLAY NAMES
# ---------------------------------------------------------------------------
# HARVESTED. Union of:
#   (a) display_name_from_agent_type() applied to every agents/<dir>/<dir>.py
#       -- the override map, else ``normalized.replace('_',' ').title()``;
#   (b) every ChatWrappedAgentSpec.display_name in chat_agent_registry.py.
#
# Casing is LOAD-BEARING and must never be 'corrected':
#   * STM32er is never STM32Er / STM32ER / Stm32er.
#   * Kyber-KeyGen / Video-Analyzer / File-Creator / Monitor-Log keep their
#     HYPHEN: acp-canvas-core.js lowercases the display name WITHOUT
#     collapsing whitespace and tests only the hyphenated literal, so a
#     spaced variant matches nothing and the canvas connection is silently
#     never saved.
#
# AUDIT NOTE -- the two sources disagree for these template_dirs. Both forms
# ship in the product, so BOTH are protected here:
#   emailer                  agent_paths='Emailer'        registry='Send Email'
#   kyber_cipher             agent_paths='Kyber-Cipher'   registry='Kyber Cipher'
#   kyber_decipher           agent_paths='Kyber-DeCipher' registry='Kyber Deciph'
#   kyber_keygen             agent_paths='Kyber-KeyGen'   registry='Kyber Keygen'
#   mover                    agent_paths='Mover'          registry='Move File'
#   recmailer                agent_paths='RecMailer'      registry='Recmailer'
#   summarizer               agent_paths='Summarizer'     registry='Summarize Text'
# ===========================================================================
AGENT_DISPLAY_NAMES = (
    'ACPXer',
    'AND',
    'Analyzer',
    'Apirer',
    'Arduiner',
    'Asker',
    'AudioPlayer',
    'Barrier',
    'Blenderer',
    'Camcorder',
    'Cleaner',
    'Counter',
    'Crawler',
    'Croner',
    'De-Compresser',
    'Deleter',
    'Discoverer',
    'Dockerer',
    'ESP32er',
    'ESPHomer',
    'Editor',
    'Emailer',
    'Ender',
    'Executer',
    'File-Creator',
    'File-Extractor',
    'File-Interpreter',
    'FlowBacker',
    'FlowCreator',
    'FlowHypervisor',
    'Forker',
    'Gateway Relayer',
    'Gatewayer',
    'Gitter',
    'Globber',
    'Googler',
    'Grepper',
    'Image-Interpreter',
    'Instant Messaging Doctor',
    'J-Decompiler',
    'Jenkinser',
    'Kalier',
    'Keyboarder',
    'Kuberneter',
    'Kyber Cipher',
    'Kyber Deciph',
    'Kyber Keygen',
    'Kyber-Cipher',
    'Kyber-DeCipher',
    'Kyber-KeyGen',
    'MCP Doctor',
    'Mongoxer',
    'Monitor Netstat',
    'Monitor-Log',
    'Mouser',
    'Move File',
    'Mover',
    'Nmapper',
    'Node Manager',
    'Notifier',
    'OR',
    'PDFer',
    'PSer',
    'Parametrizer',
    'Playwrighter',
    'Prompter',
    'Pythonxer',
    'Raiser',
    'RecMailer',
    'Recmailer',
    'Recorder',
    'Reviewer',
    'SCPer',
    'SQLer',
    'SSHer',
    'STM32er',
    'Send Email',
    'Shoter',
    'Sleeper',
    'Starter',
    'Stopper',
    'Summarize Text',
    'Summarizer',
    'Talker',
    'TeleTlamatini',
    'Telegrammer',
    'Unrealer',
    'Video-Analyzer',
    'VideoPlayer',
    'Whatsapper',
    'Whisperer',
    'Windower',
    'Zavuerer',
)


# ===========================================================================
# 3. TOOL NAMES
# ---------------------------------------------------------------------------
# HARVESTED. ChatWrappedAgentSpec.tool_name + every @tool-decorated function
# in acpx/tools.py, tools.py and external_mcp_manager.py. These are Python
# identifiers bound for the LLM; they are NEVER translated, and they surface
# to the user verbatim in the Exec Report and the Ask Execs dialog.
# ===========================================================================
TOOL_NAMES = (
    'acp_doctor',
    'acp_kill',
    'acp_list_sessions',
    'acp_relay',
    'acp_send',
    'acp_send_and_wait',
    'acp_session_status',
    'acp_spawn',
    'acp_transcript',
    'agent_parametrizer',
    'agent_starter',
    'agent_stat_getter',
    'agent_stopper',
    'chat_agent_apirer',
    'chat_agent_arduiner',
    'chat_agent_asker',
    'chat_agent_audioplayer',
    'chat_agent_blenderer',
    'chat_agent_camcorder',
    'chat_agent_crawler',
    'chat_agent_de_compresser',
    'chat_agent_deleter',
    'chat_agent_discoverer',
    'chat_agent_dockerer',
    'chat_agent_editor',
    'chat_agent_esp32er',
    'chat_agent_esphomer',
    'chat_agent_executer',
    'chat_agent_file_creator',
    'chat_agent_file_extractor',
    'chat_agent_file_interpreter',
    'chat_agent_flowcreator',
    'chat_agent_gitter',
    'chat_agent_globber',
    'chat_agent_grepper',
    'chat_agent_image_interpreter',
    'chat_agent_instant_messaging_doctor',
    'chat_agent_j_decompiler',
    'chat_agent_jenkinser',
    'chat_agent_kalier',
    'chat_agent_keyboarder',
    'chat_agent_kuberneter',
    'chat_agent_kyber_cipher',
    'chat_agent_kyber_deciph',
    'chat_agent_kyber_keygen',
    'chat_agent_mcp_doctor',
    'chat_agent_mongoxer',
    'chat_agent_monitor_log',
    'chat_agent_monitor_netstat',
    'chat_agent_mouser',
    'chat_agent_move_file',
    'chat_agent_nmapper',
    'chat_agent_notifier',
    'chat_agent_pdfer',
    'chat_agent_playwrighter',
    'chat_agent_prompter',
    'chat_agent_pser',
    'chat_agent_pythonxer',
    'chat_agent_recmailer',
    'chat_agent_recorder',
    'chat_agent_run_list',
    'chat_agent_run_log',
    'chat_agent_run_status',
    'chat_agent_run_stop',
    'chat_agent_run_wait',
    'chat_agent_scper',
    'chat_agent_send_email',
    'chat_agent_shoter',
    'chat_agent_sleeper',
    'chat_agent_sqler',
    'chat_agent_ssher',
    'chat_agent_stm32er',
    'chat_agent_summarize_text',
    'chat_agent_talker',
    'chat_agent_telegrammer',
    'chat_agent_unrealer',
    'chat_agent_video_analyzer',
    'chat_agent_videoplayer',
    'chat_agent_whatsapper',
    'chat_agent_whisperer',
    'chat_agent_windower',
    'chat_agent_zavuerer',
    'decompile_java',
    'execute_command',
    'execute_file',
    'execute_netstat',
    'get_current_time',
    'googler',
    'invoke_skill',
    'launch_view_image',
    'list_acp_agents',
    'list_skills',
    'unzip_file',
    'window_present',
)


# ===========================================================================
# 4. PRODUCT TERMS
# ---------------------------------------------------------------------------
# Tlamatini's own feature and surface names. These are TOPIC NAMES: a
# Mexican developer says 'el Exec Report', 'el Access Keys Wizard',
# 'el Catalogo de Prompts' -- Spanish article, English noun.
# ===========================================================================
PRODUCT_TERMS = (
    'Tlamatini',
    'XAIHT',
    'ACPX',
    'ACPXer',
    'MCP',
    'MCPs',
    'Multi-Turn',
    'Exec report',
    'Exec Report',
    'Ask Execs',
    # 'Step-by-Step' REMOVED 2026-07-28: Angela ordered the toolbar
    # checkbox shown as 'Paso-a-Paso', so it is a carrier string now.
    'Skills',
    'Skill',
    'Flow',
    'FlowCreator',
    'FlowHypervisor',
    'FlowBacker',
    'Wizard',
    'Access Keys Wizard',
    'Prompt Catalog',
    'Catalogo de Prompts',
    'System-Metrics',
    'Files-Search',
    # 'External MCPs' REMOVED 2026-07-28: Angela ordered the navbar shown
    # as 'MCPs Externos' ('External' -> 'Externos'). 'MCPs' alone STAYS.
    'MCP Doctor',
    'Parametrizer',
    'Create Flow',
    'Exec',
    'TeleTlamatini',
    'Angela Lopez Mendoza',
    'Angela López Mendoza',
)


# ===========================================================================
# 5. TECH LEXICON
# ---------------------------------------------------------------------------
# General computing vocabulary a Mexican developer keeps in English inside
# an otherwise Spanish sentence. Organised by domain; TECH_LEXICON is the
# concatenation. Informatica is the #1 anglicism domain in Spanish (167
# entries in the Gran diccionario de anglicismos, ahead of telecomunicacion
# at 111), and the RAE's own dictionary already admits byte, hardware,
# software, router, spam and friends UNADAPTED.
# ===========================================================================

# --- Containers and orchestration ---
TECH_CONTAINERS = (
    'Pod',
    'Container',
    'Cluster',
    'Deployment',
    'Namespace',
    'Docker image',
    'container image',
    'Compose',
    'Registry',
    'Kubernetes',
    'Docker',
    'Helm',
    'Node',
    'Ingress',
    'Sidecar',
    'Orchestration',
    'LPAR',
)

# --- Version control ---
TECH_VCS = (
    'Commit',
    'Branch',
    'Merge',
    'Pull Request',
    'Rebase',
    'Push',
    'Pull',
    'Repo',
    'Repository',
    'Checkout',
    'Diff',
    'Tag',
    'Stash',
    'Fork',
    'Remote',
    'Upstream',
)

# --- Build and release ---
TECH_BUILD = (
    'Build',
    'Release',
    'Deploy',
    'Pipeline',
    'Rollback',
    'Artifact',
    'CI',
    'CD',
    'Job',
    'Runner',
    'Stage',
    'Installer',
    'Package',
)

# --- Runtime and diagnostics ---
TECH_RUNTIME = (
    # "Pattern" was forbidden in Spanish but never DECLARED in English, so
    # the rule had no target. It is the word in the canonical GUI sentence:
    # "cuando se detecta un pattern en el log".
    "Pattern",
    'Log',
    'Debug',
    'Trace',
    'Timeout',
    'Thread',
    'Process',
    'Daemon',
    'Cache',
    'Buffer',
    'Stack',
    'Heap',
    'Crash',
    'Core dump',
    'Handler',
    'Callback',
    'Worker',
    'Runtime',
    'Overhead',
    'Deadlock',
)

# --- Web and API ---
TECH_WEB = (
    'Endpoint',
    'API',
    'REST',
    'Webhook',
    'Request',
    'Response',
    'Header',
    'Payload',
    'Token',
    'Query',
    'Socket',
    'WebSocket',
    'Proxy',
    'Gateway',
    'Status code',
    'Rate limit',
    'Polling',
    'Streaming',
)

# --- Data and persistence ---
TECH_DATA = (
    "Data mining",   # forbidden in Spanish; now declared

    'Schema',
    'Index',
    'Backup',
    'Dump',
    'Row',
    'Record',
    'Dataset',
    'Migration',
    'Transaction',
    'Rollback',
    'Chunk',
    'Batch',
)

# --- Files, OS and shell ---
TECH_FILES_OS = (
    'Path',
    'Screenshot',
    'Script',
    'Shell',
    'Prompt',
    'Pipe',
    'Symlink',
    'Mount',
    'Glob',
    'Wildcard',
    'Binary',
    'Output',
    'Input',
    'Hardware',
    'Software',
    'Router',
    'Byte',
    'Kilobyte',
    'Megabyte',
    'Gigabyte',
    'Terabyte',
    'Spam',
)

# --- AI and LLM ---
TECH_AI = (
    'Prompt',
    'Token',
    'Embedding',
    'Context',
    'Chain',
    'Agent',
    'Tool',
    'Model',
    'Fine-tuning',
    'RAG',
    'LLM',
    'Inference',
    'Checkpoint',
    'Dataset',
    'Temperature',
    'Multi-Turn',
    'Streaming',
    'Vision',
)

# --- Hardware and firmware ---
TECH_FIRMWARE = (
    'Firmware',
    'Board',
    'Serial',
    'Port',
    'Baud',
    'Flash',
    'Chip',
    'Bootloader',
    'Sketch',
    'Toolchain',
    'Debugger',
    'Probe',
    'Pin',
    'Upload',
    'Monitor',
)

# --- Security ---
TECH_SECURITY = (
    'Hash',
    'Key',
    'Secret',
    'Scan',
    'Exploit',
    'Payload',
    'Hacker',
    'Cracker',
    'Malware',
    'Firewall',
    'Certificate',
    'Credential',
    'Vulnerability',
    'Pentest',
    'Scope',
)

TECH_LEXICON = (
    TECH_CONTAINERS
    + TECH_VCS
    + TECH_BUILD
    + TECH_RUNTIME
    + TECH_WEB
    + TECH_DATA
    + TECH_FILES_OS
    + TECH_AI
    + TECH_FIRMWARE
    + TECH_SECURITY
)


# ===========================================================================
# AUXILIARY -- negative space (NOT part of all_terms())
# ---------------------------------------------------------------------------
# SPANISH_PREFERRED: terms that deliberately DO become Spanish. Generic
# verbs and everyday nouns are the carrier, not the lexicon. Angela's rule
# is explicit that 'folder' is Spanish-acceptable as 'carpeta'.
# ===========================================================================
# Emitted as a DICT on purpose: dnt.py::dnt_terms() sweeps every public
# TUPLE in this module into the do-not-translate set, so a tuple here would
# inject junk like "('Folder', 'carpeta')" as if it were a protected term.
SPANISH_PREFERRED = {
    'Folder': 'carpeta',
    'File': 'archivo',
    'Save': 'Guardar',
    'Cancel': 'Cancelar',
    'Close': 'Cerrar',
    'Search': 'Buscar',
    'Continue': 'Continuar',
    'Delete': 'Eliminar',
    'Open': 'Abrir',
    'Send': 'Enviar',
    'Directory': 'directorio',
    'User': 'usuario',
    'Name': 'nombre',
    'Date': 'fecha',
    'Help': 'Ayuda',
    # --- Added after the BIUNIVOCIDAD adjudication -------------------
    # Each of these has an exact, unambiguous, universally-used Spanish
    # form, so rendering it in Spanish costs no term-to-concept fidelity.
    # Contrast the entries kept English below (Pod, Container, log,
    # pattern, commit), where the Spanish would be invented or ambiguous.
    'Context': 'contexto',
    'Port': 'puerto',
    'Command': 'comando',
    'Screen': 'pantalla',
    'Window': 'ventana',
    'Network': 'red',
    # ⚠️ ACCENTS ARE NOT OPTIONAL (fixed 2026-07-29, Angela).
    # These five shipped accent-stripped — 'contrasena', 'tamano', 'pagina' —
    # while the reviewed terms.csv had them correct all along. Nobody noticed
    # because nothing compared the two copies. `test_termbase_agreement.py`
    # now does, so this cannot silently regress.
    # A Spanish product that writes "contrasena" is not a Spanish product.
    'Version': 'versión',
    'Size': 'tamaño',
    'Line': 'línea',
    'Page': 'página',
    'Password': 'contraseña',
}


# ===========================================================================
# FORBIDDEN_SPANISH_RENDERINGS: (wrong_spanish, correct_english). The
# 'Exclusions' half of a Microsoft-style termbase -- these are the
# mistranslations to positively reject in review. 'patron', 'registro',
# 'contenedor', 'despliegue', 'asistente', 'indicaciones', 'instantanea'
# are the exact errors this register was written to prevent.
# ===========================================================================
# Also a DICT, for the same dnt_terms() reason as above.
FORBIDDEN_SPANISH_RENDERINGS = {
    # --- Angela's register correction, 2026-07-28 ----------------------
    # Mexican technical Spanish is tightly coupled to American English.
    # These are the terms I had wrongly rendered in Spanish.
    'ruta': 'Path',
    'estado': 'Status',
    'salida': 'Output',
    'entrada': 'Input',
    'cadena': 'Chain',
    # -------------------------------------------------------------------

    'patron': 'pattern',
    'patrón': 'pattern',
    'registro': 'Log',
    'bitácora': 'Log',
    'bitacora': 'Log',
    'contenedor': 'Container',
    'vaina': 'Pod',
    'despliegue': 'Deployment',
    'cúmulo': 'Cluster',
    'cumulo': 'Cluster',
    'asistente': 'Wizard',
    'indicaciones': 'Prompts',
    'indicacion': 'Prompt',
    'instantánea': 'Screenshot',
    'instantanea': 'Screenshot',
    'captura de pantalla': 'Screenshot',
    'éxito': 'SUCCESS',
    'exito': 'SUCCESS',
    'fallo': 'FAILURE',
    'confirmación': 'Commit',
    'confirmacion': 'Commit',
    'rama': 'Branch',
    'punto final': 'Endpoint',
    'ficha': 'Token',
    'respaldo': 'Backup',
    'consulta': 'Query',
    'guion': 'Script',
    'mineria de datos': 'Data mining',
    'minería de datos': 'Data mining',
}


# ===========================================================================
# HELPERS
# ===========================================================================
_ALL_FAMILIES = (
    MACHINE_SENTINELS,
    AGENT_DISPLAY_NAMES,
    TOOL_NAMES,
    PRODUCT_TERMS,
    TECH_LEXICON,
)

_ALL_TERMS = frozenset(t for fam in _ALL_FAMILIES for t in fam)
_FOLDED = {}
for _t in _ALL_TERMS:
    _FOLDED.setdefault(_t.lower(), _t)


def all_terms():
    """Every protected term, as one frozenset. Case preserved exactly."""
    return _ALL_TERMS


def is_protected(term, fold_case=False):
    """Is ``term`` a do-not-translate term?

    Case-PRESERVING by default: the comparison is exact, because the casing
    IS the contract (``STM32er`` is protected, ``Stm32Er`` is a bug we want
    a linter to catch, not to wave through). Pass ``fold_case=True`` for a
    lenient case-insensitive check when scanning free prose.
    """
    if not term or not isinstance(term, str):
        return False
    if term in _ALL_TERMS:
        return True
    if fold_case and term.lower() in _FOLDED:
        return True
    return False


def canonical_form(term):
    """Return the exactly-cased protected term matching ``term``, else None.

    Lets a linter report 'you wrote Stm32Er, write STM32er'.
    """
    if not term or not isinstance(term, str):
        return None
    if term in _ALL_TERMS:
        return term
    return _FOLDED.get(term.lower())
