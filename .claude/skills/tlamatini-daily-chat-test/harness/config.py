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
Central configuration + DOM contract for the Tlamatini daily chat test.

Everything the harness needs to know about *how to drive agent_page.html* lives
here, in one place, so a future UI change is a one-file fix. The selectors and
the "answer-complete" signal were derived directly from the live source:

  * Login        -> agent/templates/agent/login.html  (#id_username / #id_password)
  * Login view   -> agent/views.py::login_view  (POST '/', redirect 'welcome')
  * Chat page    -> '/agent/'  (agent/urls.py -> views.agent_page)
  * Chat DOM     -> agent/templates/agent/agent_page.html
                      input  = #chat-message-input  (textarea)
                      send   = #chat-message-submit (submit button)
                      log    = #chat-log
                      bot    = div.message.bot-message  (body: .automated-message-body)
  * Mode toggles -> #multi-turn-enabled / #acpx-enabled / #exec-report-enabled /
                    #ask-execs-enabled / #internetEnabled
  * Busy/idle    -> agent/static/agent/js/agent_page_ui.js
                      disableControlsDuringOperation(): chatInput.readOnly = true,
                          appends img#wait-spinner to #chat-log
                      enableControlsAfterOperation():  chatInput.readOnly = false,
                          removes #wait-spinner
                    => ANSWER COMPLETE  <=>  input not readOnly  AND  no #wait-spinner
                    (spinner id 'wait-spinner' from agent_page_state.js)

The run-mode the user pinned for this test:
    Multi-Turn  ON   (operator mode -- tools really execute)
    ACPX        OFF
    Ask-Execs   OFF
    Exec-Report OFF
    Internet    OFF
"""

import os

# --- Target ---------------------------------------------------------------
BASE_URL = os.environ.get("TLAMATINI_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
LOGIN_PATH = "/"            # project urls: path('', login_view, name='home')
# agent.urls is include()d under '/agent/', and agent_page is path('agent/'),
# so the chat page resolves to '/agent/agent/'. ('/agent/' itself is the login
# page again -- agent.urls also has path('', login_view, name='home').)
CHAT_PATH = "/agent/agent/"  # name='agent_page'

# --- Credentials (installer default: user / changeme) ---------------------
USERNAME = os.environ.get("TLAMATINI_USER", "user")
PASSWORD = os.environ.get("TLAMATINI_PASS", "changeme")

# --- DOM selectors --------------------------------------------------------
SEL = {
    # login
    "login_user": "#id_username",
    "login_pass": "#id_password",
    "login_submit": "form button[type=submit]",
    # chat
    "chat_input": "#chat-message-input",
    "chat_submit": "#chat-message-submit",
    "chat_log": "#chat-log",
    "bot_message": "#chat-log .message.bot-message",
    "bot_body": ".automated-message-body",
    "bot_any": ".automated-message",
    "spinner": "#wait-spinner",
    # toolbar mode toggles
    "t_multi_turn": "#multi-turn-enabled",
    "t_acpx": "#acpx-enabled",
    "t_exec_report": "#exec-report-enabled",
    "t_ask_execs": "#ask-execs-enabled",
    "t_internet": "#internetEnabled",
    # housekeeping
    "clean_history": "#clean-history",
}

# --- The pinned run configuration -----------------------------------------
# (key -> desired .checked state on the corresponding toolbar checkbox)
TOGGLE_STATE = {
    "t_multi_turn": True,
    "t_acpx": False,
    "t_exec_report": False,
    "t_ask_execs": False,
    "t_internet": False,
}

# --- Timing defaults (milliseconds unless noted) --------------------------
NAV_TIMEOUT_MS = 30_000
# "operation started" grace -- how long we wait to observe readOnly flip true /
# the spinner appear after we click Send. Fast direct answers may skip it.
STARTED_TIMEOUT_MS = 20_000
# "operation done" -- the per-question hard cap. Multi-Turn tool loops can be
# slow, so this is generous and CLI-overridable (--timeout, in seconds).
DONE_TIMEOUT_MS = 240_000
# small settle after the done-signal before we scrape the answer text
SETTLE_MS = 400

# --- "Agent is busy / not ready" banners ----------------------------------
# These are NOT real answers. They appear when a previous request is still
# being processed server-side (the per-user chain is single-lane), e.g. right
# after a slow question that timed out client-side but kept running on the
# server. When we see one, we must WAIT and RETRY the same question -- never
# record it as the answer (that is the bug that produced 100 junk rows once).
#
# BILINGUAL (Spanish edition): the Spanish build emits these banners in
# Spanish (agent/constants.py ERROR_AGENT_NOT_READY*). A harness that only
# knew the English wording would scrape a busy banner and record it as the
# answer -- the exact "never record a stale/transient answer as a pass"
# failure. Both languages are matched; matching is accent-insensitive at the
# call site, so an accent difference can never silently un-match.
NOT_READY_MARKERS = (
    # English (upstream build)
    "Agent is not ready. Please try again later.",
    "Agent is not ready",
    "is still being processed",
    # Spanish, FIRST PERSON (2026-07-29) — she says "Todavia no estoy lista"
    "todavia no estoy lista",
    "no puedo procesar tus requests",
    # Spanish, older third-person forms (harmless to keep)
    "Tlamatini todavia no esta lista",
    "Tlamatini no puede procesar tus requests",
    "sigue procesando",
)

# --- System / busy banners that are NOT the real answer -------------------
# (filtered out when we scrape the bot messages produced for a question)
BUSY_MARKERS = (
    # English (upstream build)
    "Your request is being processed by Tlamatini.",
    "Your agent is loading the context.",
    # El centinela de reformulacion es CANAL DE MAQUINA y va en ingles
    # (Angela, 2026-09-03). Se dejan LOS DOS: un arbol viejo todavia puede
    # emitir el espanol, y un marcador de mas nunca hace dano.
    "referenced rephrase:",
    "pregunta reformulada:",
    "Welcome back, session and context restored",
    "Welcome back, session restored",
    # Spanish, FIRST PERSON (2026-07-29) -- agent/constants.py MSG_*
    "estoy procesando tu request",
    "estoy cargando el context",
    "me estoy cargando",
    "esperame tantito",
    "soy tlamatini, estoy lista para platicar",
    "limpie el historial del chat",
    "me estoy reconstruyendo",
    "ya me restableci",
    # Spanish, older third-person forms (harmless to keep)
    "Tlamatini esta procesando tu request",
    "Tlamatini esta cargando el context",
    "Tlamatini se esta cargando",
    "Tlamatini esta lista, ahora puedes platicar con ella",
    "Que bueno que volviste",
    "Se limpio el historial del chat",
    "Reconstruyendo a Tlamatini",
    "Tlamatini se restablecio correctamente",
) + NOT_READY_MARKERS


# --- Accent-insensitive banner matching -----------------------------------
# The markers above are written WITHOUT accents on purpose, and every
# comparison folds both sides. Spanish banners carry accents ("está", "Qué",
# "limpió"); if the harness compared raw strings, a single missing accent
# would silently un-match a busy banner and the runner would record it as a
# real answer. Folding removes that entire failure mode.
def fold(text: str) -> str:
    """Lowercase + strip diacritics, so 'está' == 'esta'."""
    import unicodedata

    decomposed = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def is_busy_banner(text: str) -> bool:
    """True when `text` is a system/busy banner, NOT a real answer."""
    folded = fold(text)
    return any(fold(m) in folded for m in BUSY_MARKERS)


def is_not_ready(text: str) -> bool:
    """True when `text` says the agent is busy -- wait and RETRY, never record."""
    folded = fold(text)
    return any(fold(m) in folded for m in NOT_READY_MARKERS)

# --- Reports --------------------------------------------------------------
DEFAULT_OUT_DIR = os.path.join(os.path.dirname(__file__), "reports")
