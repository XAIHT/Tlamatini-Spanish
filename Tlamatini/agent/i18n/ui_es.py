"""Spanish GUI catalog - Spanish carrier, English technical lexicon.

Every entry maps an ENGLISH source string, extracted verbatim from the
templates, to its Spanish rendering. The rule applied to every single line:

    Spanish supplies the grammar. English supplies the technical vocabulary.

so the GUI reads the way its users actually speak:

    "Haciendo un Pod en Dockerer y creando un Container en Kubernetes."
    "Envia un email por SMTP cuando se detecta un pattern en el log."

WHAT NEVER MOVES, AND WHY
-------------------------
* ASSET NAMES - Emailer, Executer, STM32er, Kyber-KeyGen, De-Compresser,
  Monitor-Log. These are the NAMES OF THINGS in this system. A GUI that calls
  Emailer *Correero* is describing software that does not exist, and the
  hyphens are functional besides: the canvas connection handler compares the
  hyphenated literal, so a "translated" spacing silently breaks the wiring.
* PRODUCT TERMS - MCP, MCPs, ACPX, Multi-Turn, Exec report, Ask Execs,
  Step-by-Step, Skills, Flow, Canvas, Wizard, Catalog of prompts. Angela's
  instruction names MCPs and Wizard explicitly.
* THE SHARED TECHNICAL LEXICON - log, commit, push, repo, Pod, Container,
  deployment, screenshot, browser, firmware, timeout, backup, script, prompt,
  token, endpoint. A Mexican developer says these in English; translating them
  makes a colleague stop and re-read.
* ANGELA'S NAME - "CREATED BY ANGELA LOPEZ MENDOZA" maps to ITSELF, listed
  explicitly below so the catalog is proof, not merely an omission.

WHAT DOES MOVE
--------------
Articles, prepositions, connectives, generic verbs (guardar, abrir, buscar,
limpiar, detener), and the explanatory prose around the terms above - plus the
genuinely Spanish nouns: archivo, carpeta, pantalla, usuario, contrasena.

MECHANICALLY ENFORCED
---------------------
``agent/i18n/dnt.py::missing_terms`` checks every pair here: any
do-not-translate term present in the English source MUST be present, BYTE
IDENTICAL, in the Spanish target. ``test_ui_dnt.py`` fails the build otherwise.
That turns "keep the terms in English" from a style note into an invariant.

REGISTER NOTES
--------------
* Mexican Spanish, neutral enough for the wider region. Second person singular
  ("tu"), which is what a developer tool uses.
* Gender-neutral where the user is addressed: "Te damos la bienvenida", never
  "Bienvenido" / "Bienvenida", because the user may be anyone.
* Inverted opening punctuation is used, since it is correct Spanish.
"""

from __future__ import annotations

from typing import Dict

__all__ = ["UI_ES", "translate"]


UI_ES: Dict[str, str] = {
    # ── Navbar: Context ────────────────────────────────────────────────────
    "Context": "Contexto",
    "Context:": "Contexto:",
    "Open in...": "Abrir en...",
    "Open": "Abrir",
    "Save": "Guardar",
    "Set directory as context": "Usar un directorio como contexto",
    "Set file as context": "Usar un archivo como contexto",
    "View context directory in": "Ver el directorio de contexto en",
    "canvas": "canvas",
    "Clear context": "Limpiar el contexto",
    "Set file type omissions": "Omitir tipos de archivo",

    # ── Navbar: MCPs / Agents / Skills / External ──────────────────────────
    # "MCP", "MCPs", "ACPX", "Skills", "Agents", "Tools" stay English:
    # they are product terms, and Angela named MCPs explicitly.
    "MCPs": "MCPs",
    "Configure MCPs": "Configurar MCPs",
    "Agents": "Agents",
    "Configure Agents": "Configurar Agents",
    "Agentic Control Panel": "Agentic Control Panel",
    "ACPX-Skills": "ACPX-Skills",
    "Browse Skills": "Ver Skills",
    "Configure Skills": "Configurar Skills",
    "Diagnostics": "Diagnóstico",
    "Reload Registry": "Recargar el Registry",
    "External": "Externos",
    "Tools": "Tools",

    # ── Navbar: Config / DB / Admin / About ────────────────────────────────
    "Config": "Configuración",
    "Models": "Modelos",
    "URLs": "URLs",
    "Contacts": "Contactos",
    "Voice": "Voz",
    "DB": "DB",
    "Backup database": "Backup de la base de datos",
    "Set DB": "Elegir la DB",
    "Admin": "Administración",
    "Open Admin page": "Abrir la página de Admin",
    "Reconnect": "Reconectar",
    "About": "Acerca de",
    "Check for updates": "Buscar actualizaciones",
    "Logout": "Cerrar sesión",
    "Catalog of prompts": "Catálogo de prompts",
    "Clear history": "Limpiar el historial",

    # ── Chat toolbar ──────────────────────────────────────────────────────
    # Every toggle name is a product term and stays exactly as it is.
    "Multi-Turn": "Multi-Turn",
    "Exec report": "Exec report",
    "ACPX": "ACPX",
    "Ask Execs": "Ask Execs",
    "Step-by-Step": "Paso-a-Paso",
    "Add internet context": "Agregar contexto de internet",
    "Send": "Enviar",
    "Send a message...": "Escribe un mensaje...",
    "Append per-agent execution tables to the answer. Enabled only when Multi-Turn is on.":
        "Agrega al final de la respuesta una tabla de ejecución por cada Agent. "
        "Solo se habilita cuando Multi-Turn esta activado.",
    "Ask permission before each Multi-Turn tool/agent execution. Enabled only when Multi-Turn is on.":
        "Pide permiso antes de cada ejecución de tool o Agent en Multi-Turn. "
        "Solo se habilita cuando Multi-Turn esta activado.",
    "Guide setup and troubleshooting one user-confirmed step at a time.":
        "Guía el setup y el troubleshooting un paso a la vez, "
        "confirmando contigo antes de seguir.",
    "Drop an image — Tlamatini saves it to Temp and puts the path in your message":
        "Suelta una imagen — Tlamatini la guarda en Temp y pone el path en tu mensaje",
    "Click me - I will tell you how it is going":
        "Haz click - te cuento cómo va",
    "Tlamatini avatar - click to hear a status update":
        "Avatar de Tlamatini - haz click para escuchar cómo va",
    "Toggle navigation": "Abrir o cerrar el menú",
    "Close": "Cerrar",
    "Cancel": "Cancelar",
    "Continue": "Continuar",
    "Apply": "Aplicar",
    "Clear": "Limpiar",
    "Copy": "Copiar",
    "Reopen": "Reabrir",
    "Clear canvas": "Limpiar el canvas",
    "Use as context": "Usar como contexto",

    # ── Ask Execs permission dialog ───────────────────────────────────────
    "Execution permission required": "Se requiere permiso de ejecución",
    # PRIMERA PERSONA: es Tlamatini pidiéndole permiso a Angela, así que habla
    # de sí misma como "yo", no como "Tlamatini". El inglés dice "Tlamatini
    # wants to…" porque el diálogo se redactó desde afuera; en español, hablar
    # de sí misma en tercera persona la vuelve un aparato del que alguien más
    # informa. La MISMA frase está literal en agent_page.html:280 — las dos se
    # cambian juntas o se separan sin que nadie lo note.
    "Tlamatini wants to run the following before continuing the Multi-Turn chain.":
        "Tlamatini quiere ejecutar lo siguiente antes de continuar el chain de Multi-Turn.",
    "Review what is about to execute and choose":
        "Revisa lo que está a punto de ejecutarse y elige",
    "Proceed": "Continuar",
    "or": "o",
    "Deny": "Denegar",
    "Tlamatini Tool / MCP / Agent": "Tool / MCP / Agent de Tlamatini",
    "Underlying tool": "Tool subyacente",
    "Parameters of execution": "Parámetros de ejecución",
    "Program to be executed": "Programa que se va a ejecutar",
    "Shell to be executed": "Shell donde se va a ejecutar",

    # ── External MCPs dialog ──────────────────────────────────────────────
    # "System-Metrics" and "Files-Search" are MCP service NAMES: never moved.
    "System-Metrics": "System-Metrics",
    "Files-Search": "Files-Search",
    "External MCPs": "MCPs Externos",
    "Activate MCPs": "Activar MCPs",
    "MCP catalog": "Catálogo de MCPs",
    "Active MCP services": "MCP services activos",
    "Active - sent with your prompt": "Activo - se envía con tu prompt",
    "Search services...": "Buscar services...",
    "Service": "Service",
    "Transport": "Transport",
    "Status": "Status",
    "Drop an MCP": "Suelta un MCP",
    "anywhere on the page to add it.": "en cualquier parte de la página para agregarlo.",
    "Only active services connect; inactive ones stay in the catalog.":
        "Solo los services activos se conectan; los inactivos se quedan en el catálogo.",

    # ── Contacts book ─────────────────────────────────────────────────────
    "Contacts book": "Libreta de contactos",
    "Contacts list": "Lista de contactos",
    "Contact editor": "Editor de contactos",
    "Search contacts...": "Buscar contactos...",
    "+ New": "+ Nuevo",
    "Pick a contact, or press “New”": "Elige un contacto, o presiona “Nuevo”",
    "Name": "Nombre",
    "Full name": "Nombre completo",
    "Aliases": "Alias",
    "Telegram": "Telegram",
    "WhatsApp": "WhatsApp",
    "Email": "Email",
    "Note": "Nota",
    "Optional note": "Nota opcional",
    "Comma-separated, e.g. Ana, Ana Lazcano":
        "Separados por comas, p. ej. Ana, Ana Lazcano",
    "Edits stay local until you press": "Los cambios quedan locales hasta que presiones",
    "below.": "abajo.",
    "Stored in": "Se guarda en",
    "next to config — preserved across updates.":
        "junto al config — se conserva entre actualizaciones.",

    # ── Skills dialog ─────────────────────────────────────────────────────
    "Select a skill from the list to see its details.":
        "Selecciona un Skill de la lista para ver sus detalles.",
    "Search by name or description...": "Buscar por nombre o descripción...",

    # ── Config ▸ Models ───────────────────────────────────────────────────
    "Embedding": "Embedding",
    "Chained": "Chained",
    "Access aimed": "Access aimed",
    "Unified": "Unified",
    "Image interpreter 1": "Image interpreter 1",
    "Image interpreter 2": "Image interpreter 2",
    "Image merger": "Image merger",
    "MCP Files search": "MCP Files search",
    "Internet classifier": "Clasificador de internet",
    "Summarizer": "Summarizer",

    # ── Config ▸ URLs ─────────────────────────────────────────────────────
    "Ollama base": "Base de Ollama",
    "Unified base": "Base de Unified",
    "Image interpreter base": "Base del Image interpreter",
    "MCP System server IP": "IP del MCP System server",
    "MCP System Server port": "Puerto del MCP System Server",
    "MCP System Client Uri": "Uri del MCP System Client",
    "MCP Files Server IP": "IP del MCP Files Server",
    "MCP Files Server Port": "Puerto del MCP Files Server",
    "MCP Files Client Uri": "Uri del MCP Files Client",
    "Kali server (Kalier)": "Kali server (Kalier)",

    # ── Access Keys Wizard ────────────────────────────────────────────────
    "Access Keys Wizard": "Access Keys Wizard",
    "Access keys wizard sections": "Secciones del Access Keys Wizard",
    "Configure provider keys, bridge passwords, and ACPX commands in one place.":
        "Configura las provider keys, los passwords de los bridges y "
        "los comandos de ACPX en un solo lugar.",

    # ── DB / backup ───────────────────────────────────────────────────────
    "Target directory:": "Directorio destino:",
    "Browse": "Examinar",
    "Browse for a folder": "Buscar una carpeta",
    "Browse for a db.sqlite3 file": "Buscar un archivo db.sqlite3",
    "db.sqlite3 file:": "Archivo db.sqlite3:",
    "e.g. C:\\Backups\\Tlamatini": "p. ej. C:\\Backups\\Tlamatini",
    "e.g. C:\\Backups\\Tlamatini\\db.sqlite3": "p. ej. C:\\Backups\\Tlamatini\\db.sqlite3",

    # ── Catalog of prompts ────────────────────────────────────────────────
    "Pre-established prompts...": "Prompts pre-establecidos...",
    "Search prompts by words, initials (imd) or a #number...":
        "Busca prompts por palabras, iniciales (imd) o un #número...",
    "Search the catalog of prompts": "Buscar en el Catalog of prompts",
    "Clear search": "Limpiar la búsqueda",
    "File extensions separated by commas (,)":
        "Extensiones de archivo separadas por comas (,)",

    # ── About ─────────────────────────────────────────────────────────────
    # Angela's name and XAIHT's expansion are NAMES. They never move.
    "CREATED BY ANGELA LÓPEZ MENDOZA": "Creada por Ángela López Mendoza",
    "XAIHT: eXtended Artificial Intelligence Humanly Tempered (a Mexican company)":
        "XAIHT: eXtended Artificial Intelligence Humanly Tempered "
        "(una empresa mexicana)",
    "Installed version:": "Versión instalada:",
    "Checking for updates…": "Buscando actualizaciones…",
    "View releases on GitHub": "Ver los releases en GitHub",
    "Update now": "Actualizar ahora",

    # ── Voice settings ────────────────────────────────────────────────────
    "Voice settings": "Configuración de la voz",
    "Tlamatini's voice is": "La voz de Tlamatini es",
    "always female": "siempre femenina",
    ", and works the same in Chrome & Edge.":
        ", y funciona igual en Chrome y Edge.",
    "Volume": "Volumen",
    "Speed": "Velocidad",
    "Pitch": "Tono",
    "Pan (stereo)": "Pan (estéreo)",
    "Mono in the browser - available with the Orpheus voice.":
        "Mono en el browser - disponible con la voz Orpheus.",
    "When an answer arrives": "Cuando llega una respuesta",
    "Automatically speak answers": "Leer las respuestas automáticamente",
    "Notify answer complete": "Avisar cuando la respuesta termine",
    "Silent": "En silencio",
    "Test voice": "Probar la voz",

    # ── Agentic Control Panel ─────────────────────────────────────────────
    "Tlamatini (Agentic Control Panel)": "Tlamatini (Agentic Control Panel)",
    "File": "Archivo",
    "Save as": "Guardar como",
    "Agents:": "Agents:",
    "Flow Control Panel:": "Flow Control Panel:",
    "Validate": "Validar",
    "Start": "Iniciar",
    "Stop": "Detener",
    "Pause": "Pausar",
    "Restart": "Reiniciar",
    "Configure": "Configurar",
    "Description": "Descripción",
    "Agent Description": "Descripción del Agent",
    "See log": "Ver el log",
    "Explore dir...": "Explorar el directorio...",
    "Open cmd...": "Abrir cmd...",
    "Log Viewer": "Visor del log",
    "Last 100 lines": "Últimas 100 líneas",
    "Live": "En vivo",
    "Loading...": "Cargando...",
    "Cleaning In Progress": "Limpieza en progreso",
    "🧹 Cleaning Operations In Progress...":
        "🧹 Operaciones de limpieza en progreso...",
    "Clearing pool directory and resetting canvas. Please wait.":
        "Limpiando el pool directory y reiniciando el canvas. Espera por favor.",

    # ── Login / welcome ───────────────────────────────────────────────────
    "Login - Tlamatini": "Entrar - Tlamatini",
    "Tlamatini Login": "Entrar a Tlamatini",
    "Username": "Usuario",
    "Password": "Contraseña",
    "Login": "Entrar",
    "Enter your username": "Escribe tu usuario",
    "Enter your password": "Escribe tu contraseña",
    "Welcome - Tlamatini": "Bienvenida - Tlamatini",
    # Gender-neutral on purpose: the user may be anyone.
    "Welcome, !": "¡Te damos la bienvenida, !",
    "You have successfully logged in.": "Iniciaste sesión correctamente.",
    "Go to Chat": "Ir al Chat",
}


def translate(text: str) -> str:
    """Return the Spanish rendering, or the input unchanged when unknown.

    FAIL-OPEN by design: an untranslated string shows in English, which is
    imperfect but usable. A KeyError here would blank a control.
    """
    if not text:
        return text
    try:
        return UI_ES.get(text, text)
    except Exception:
        return text
