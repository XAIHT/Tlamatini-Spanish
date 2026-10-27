# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""The written content of the project dossier, shared by the PDF and the deck.

Every chapter is built from ``facts`` — numbers derived from the source tree at
generation time — so no count in the finished documents is typed by hand. The
prose describes behaviour documented in the repository (README, the Book,
``docs/``, ``agents_descriptions.md``, the self-knowledge file and the source).
It never reproduces a configuration value, credential or private address.

Inline marks: ``**bold**``, ```code``` and ``_italic_`` (see dossier_theme.runs).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Section:
    key: str
    kicker: str
    title: str
    lede: str
    body: list[str] = field(default_factory=list)
    points: list[tuple[str, str]] = field(default_factory=list)
    table: dict | None = None
    callout: tuple[str, str] | None = None
    visual: str | None = None
    visual_data: dict = field(default_factory=dict)
    deck: str = "cards"          # deck layout: cards | list | table | visual | none
    deck_points: list[tuple[str, str]] | None = None
    code: str | None = None


@dataclass
class Chapter:
    key: str
    numeral: str
    title: str
    tagline: str
    sections: list[Section]
    accent: str = "jade"


# ── The bestiary ────────────────────────────────────────────────────
# Families group the installed agent directories; the generator verifies that
# every installed agent appears exactly once, so a new agent cannot be missed.
AGENT_FAMILIES: list[tuple[str, str, str, list[tuple[str, str]]]] = [
    ("Control del flow", "jade", "Inicia, pausa, agenda y termina un flow.", [
        ("starter", "El punto de entrada de cada flow; lanza sus targets cuando presionas Iniciar."),
        ("ender", "Termina un flow con gracia: mata sus targets, luego inicia los backups y los cleaners."),
        ("stopper", "Vigila los logs buscando un pattern y detiene exactamente esos source agents."),
        ("cleaner", "Conserje de post-ejecución que quita los logs y los archivos PID de los agents terminados."),
        ("sleeper", "Espera una cantidad configurada de milisegundos, luego inicia sus targets."),
        ("croner", "Un disparador de reloj diario que inicia sus targets a una hora HH:MM configurada."),
    ]),
    ("Ruteo y lógica", "copper", "Deciden a dónde va el flow después.", [
        ("raiser", "Dispara sus targets en el momento en que aparece un pattern en un log vigilado."),
        ("forker", "Ruteador A/B automático: el primero de dos patterns en aparecer elige el camino."),
        ("asker", "Te pregunta en el chat que elijas el Camino A o el Camino B: un humano en el loop."),
        ("counter", "Un conteo persistente que rutea por debajo, o en y por encima, de un umbral."),
        ("and", "Compuerta de dos entradas que dispara cuando ambos sources han coincidido."),
        ("or", "Compuerta de dos entradas que dispara en cuanto cualquiera de los dos sources coincide."),
        ("barrier", "Fan-in de N entradas que se libera cuando ha llegado cada source configurado."),
    ]),
    ("Orquestación e inteligencia", "gold", "Diseña, conecta, supervisa y razona.", [
        ("parametrizer", "Mapea el output estructurado de un agent hacia la configuración del siguiente agent."),
        ("flowcreator", "Diseña un workflow .flw completo y validado a partir de un objetivo simple."),
        ("flowhypervisor", "Un watchdog de modelo que lee un flow en ejecución: OK o ATTENTION NEEDED."),
        ("flowbacker", "Hace backup de los logs y las configuraciones de una sesión antes de la limpieza."),
        ("prompter", "Envía un prompt a un modelo y registra una respuesta estructurada."),
        ("summarizer", "Resume el texto una vez, o vigila los logs y dispara ante un evento detectado."),
        ("acpxer", "Ejecuta un turno de un CLI de coding-agent externo en el canvas y captura su respuesta."),
        ("mcp_doctor", "Diagnostica un servidor MCP externo en papel, antes de cualquier conexión en vivo."),
    ]),
    ("Código, archivos y shell", "cyan", "Encuentra, lee, cambia y ejecuta.", [
        ("executer", "Ejecuta un comando de shell, opcionalmente en su propia consola visible."),
        ("pythonxer", "Ejecuta Python inline detrás de una compuerta de corrección con compile() y Ruff."),
        ("terminater", "Escribe comandos en una terminal real de CMD o PowerShell que el usuario observa, y puede entregar el teclado."),
        ("editor", "Buscar-y-reemplazar byte-exacto en un archivo; rechaza una coincidencia ambigua."),
        ("grepper", "Búsqueda regex consciente de la codificación, más lecturas literales de un rango de líneas."),
        ("globber", "Encuentra archivos por glob pattern, del más nuevo al más viejo."),
        ("file_creator", "Crea un archivo con contenido exacto, incluyendo un canal base64."),
        ("mover", "Mueve o copia archivos por glob pattern."),
        ("deleter", "Elimina por glob dentro de un directorio de trabajo protegido."),
        ("file_interpreter", "Lee DOCX, PPTX, XLSX, PDF y más, opcionalmente resumiéndolos."),
        ("file_extractor", "Extrae texto crudo de PDF, DOCX y documentos similares."),
        ("de_compresser", "Comprime o descomprime archivos .zip, .7z, .gz y tar."),
        ("j_decompiler", "Descompila archivos JAR y WAR con el jd-cli incluido."),
        ("gitter", "Ejecuta operaciones de git y comandos git personalizados."),
    ]),
    ("Documentos", "magenta", "Componen, tipografían y presentan.", [
        ("pdfer", "Compone PDFs a partir de texto, Markdown, HTML e imágenes: 24 estilos, 20 temas."),
        ("pptxer", "Construye decks editables de PowerPoint cuyo texto se mide, nunca se trunca."),
        ("latexer", "Tipografía proyectos de LaTeX, con una escalera de reparación auto-sanadora de ocho peldaños."),
    ]),
    ("Web, datos y APIs", "jade", "Busca, navega, llama y mide.", [
        ("googler", "Búsqueda web resiliente de dos niveles con un constructor estructurado de Google-dorks."),
        ("crawler", "Trae una página en crudo o como texto y la analiza con un modelo."),
        ("playwrighter", "Maneja un browser real a través de pasos con script: inicia sesión, llena, hace clic, extrae."),
        ("apirer", "Llama APIs REST con cualquier método, headers, body y timeout."),
        ("sqler", "Ejecuta Python contra Microsoft SQL Server con un cursor listo."),
        ("mongoxer", "Ejecuta Python contra MongoDB con un handle de base de datos listo."),
        ("netspeed_calculator", "Mide tu conexión con intervalos de confianza y bufferbloat."),
    ]),
    ("DevOps e infraestructura", "copper", "Containers, clusters, pipelines y hosts.", [
        ("dockerer", "Un front-end de Docker y docker-compose."),
        ("kuberneter", "Un front-end de kubectl con un resultado estructurado y veraz."),
        ("jenkinser", "Dispara jobs de Jenkins, manejando el crumb de CSRF."),
        ("ssher", "Ejecuta un comando en un host remoto por SSH."),
        ("scper", "Envía o recibe archivos por SCP."),
        ("pser", "Encuentra un proceso en ejecución a partir de un nombre difuso con ayuda de un modelo."),
    ]),
    ("Calidad y seguridad", "rose", "Revisa, analiza, evalúa y protege.", [
        ("reviewer", "Revisión guiada por modelo de un git diff con un veredicto APPROVE o REQUEST_CHANGES."),
        ("analyzer", "Análisis estático determinista: bandit, semgrep, ruff, eslint, gitleaks, pip-audit."),
        ("kalier", "Herramientas autorizadas de Kali Linux a través de MCP-Kali-Server."),
        ("discoverer", "La suite de reconocimiento de ProjectDiscovery sobre un toolchain de Go privado y autoinstalable."),
        ("nmapper", "Un puente de nmap local y de sólo uso; escaneo connect sin privilegios de forma predeterminada."),
        ("kyber_keygen", "Genera pares de claves poscuánticas CRYSTALS-Kyber."),
        ("kyber_cipher", "Cifra con criptografía poscuántica Kyber."),
        ("kyber_decipher", "Descifra datos protegidos con Kyber."),
    ]),
    ("Firmware y engines", "gold", "Placas reales y editores en vivo.", [
        ("stm32er", "Firmware de STM32 desde la Blue Pill hasta la H7: compilar, flashear, observar, fail-safe."),
        ("esp32er", "Firmware de ESP32 a través de PlatformIO, desde una plantilla que compila de inmediato."),
        ("arduiner", "Firmware de Arduino a través de arduino-cli, con los cores instalados automáticamente."),
        ("esphomer", "Dispositivos de domótica ESPHome desde YAML, sin C++ requerido."),
        ("unrealer", "Maneja un editor de Unreal Engine 5 en vivo: 53 comandos en nueve categorías."),
        ("blenderer", "Maneja Blender a través del socket del add-on oficial de Blender MCP."),
    ]),
    ("Escritorio y captura", "cyan", "Ve la pantalla, mueve el puntero, escribe.", [
        ("mouser", "Mueve y hace clic en espacios de coordenadas declarados explícitamente."),
        ("keyboarder", "Escribe Unicode en una ventana de primer plano verificada."),
        ("windower", "Enfoca, acomoda en mosaico, redimensiona, lista y cierra ventanas por título."),
        ("shoter", "Screenshots de todo el escritorio con geometría de captura publicada."),
        ("camcorder", "Foto o video de webcam a la resolución nativa de la cámara."),
    ]),
    ("Voz, audio y visión", "magenta", "Oye, habla, reproduce y mira.", [
        ("recorder", "Captura de micrófono a WAV a la frecuencia de muestreo nativa del dispositivo."),
        ("whisperer", "De voz a texto que sigue escuchando hasta que dejas de hablar."),
        ("talker", "De texto a voz, siempre en la voz femenina de Tlamatini."),
        ("audioplayer", "Reproduce archivos de audio con control de volumen, truncado y loop."),
        ("videoplayer", "Reproduce video con su audio en una pantalla elegida."),
        ("image_interpreter", "Dos modelos de visión en paralelo, fusionados por un tercero en un solo reporte."),
        ("video_analyzer", "Dictamina sobre el movimiento de un robot, transcribe pistas de audio, o resume un video."),
    ]),
    ("Mensajería y monitoreo", "rose", "Alcanza personas y vigila sistemas.", [
        ("notifier", "Muestra una notificación dentro del browser, opcionalmente con un sonido."),
        ("emailer", "Envía correo por SMTP."),
        ("recmailer", "Vigila un buzón IMAP en busca de mensajes nuevos."),
        ("telegrammer", "Telegram como el bot o como tu propia cuenta."),
        ("whatsapper", "WhatsApp a través de la Cloud API de Meta, o explícitamente desde tu propio número."),
        ("teletlamatini", "Lleva el chat completo de Tlamatini, Multi-Turn incluido, a Telegram."),
        ("instant_messaging_doctor", "Diagnostica y repara de forma segura la disponibilidad de Telegram y WhatsApp."),
        ("monitor_log", "Monitor de logs impulsado por modelo."),
        ("monitor_netstat", "Monitor de puertos de red impulsado por modelo."),
    ]),
]


def validate_families(installed: list[str]) -> None:
    listed = [name for _, _, _, members in AGENT_FAMILIES for name, _ in members]
    duplicates = sorted({n for n in listed if listed.count(n) > 1})
    missing = sorted(set(installed) - set(listed))
    stale = sorted(set(listed) - set(installed))
    if duplicates or missing or stale:
        raise RuntimeError(
            f"Bestiary drift: duplicates={duplicates} missing={missing} stale={stale}")


# ── Content ─────────────────────────────────────────────────────────
def build_chapters(f: dict) -> list[Chapter]:
    """Return every chapter of the dossier, filled with source-derived facts."""
    agents = f["agents"]
    tools = f["tools"]
    wrapped = f["wrapped"]
    skills = f["skills"]
    version = f["version"]
    sections_count = len(f["catalog_sections"])
    catalog_names = ", ".join(label for _, label in f["catalog_sections"])
    peers = f["acpx_peers"]
    model_fields = f["model_fields"]
    model_groups = f["model_groups"]
    model_agents = f["model_agents"]
    groups_text = ", ".join(f"{name} {count}" for name, count in model_groups)

    identity = Chapter("identity", "I", "Quién es ella",
        "Una asistente de desarrollo self-hosted que lee, razona, construye y actúa, y te deja diseñar el cómo.",
        accent="jade", sections=[
        Section("identity", "IDENTIDAD", "Tlamatini, la que sabe",
            "Tlamatini es una asistente de desarrollo con IA, self-hosted, para Windows 10 y 11: una aplicación de Django "
            "que conversa, recupera, planea, ejecuta agents y te deja dibujar workflows completos de agents en un canvas.",
            body=[
                "Su nombre es náhuatl. En el mundo nahua una _tlamatini_ era una sabia, literalmente “la que "
                "sabe”: guardiana de los libros pintados que cargaba el conocimiento y enseñaba a otros a ver. El "
                "nombre es una promesa sobre su comportamiento. Debe saber lo que hace, decir lo que de verdad "
                "hizo, y nunca fingir.",
                "Tlamatini fue concebida, diseñada y construida por **Angela López Mendoza** (`@angelahack1`), "
                "quien le dio el nombre. Su cumpleaños es el 29 de octubre de 2025. Es femenina por diseño, incluida "
                "su voz hablada, que siempre es una voz femenina, y se refiere a sí misma como _ella_.",
                f"Es software libre y de código abierto bajo la licencia MIT, publicada en "
                f"`github.com/XAIHT/Tlamatini`. El repositorio lleva la aplicación y cada uno de sus "
                f"{agents} programas de workflow-agent como Python simple y legible.",
            ],
            points=[
                ("Creadora", "Angela López Mendoza · @angelahack1"),
                ("Nacida", "29 de octubre de 2025"),
                ("Plataforma", "Windows 10 y 11 · Python 3.12.10 · Django 5.2.15"),
                ("Licencia", "MIT: libre y de código abierto"),
            ], deck="identity"),
        Section("planes", "DÓNDE CORREN LAS COSAS", "Control local, razonamiento en la nube",
            "“Local-first” describe dónde vive el control: la aplicación, la base de datos, los workflows, "
            "las credenciales, el código de los agents y el modelo de embedding pequeño se quedan en tu máquina, mientras que el "
            "razonamiento exigente lo hacen modelos en la nube a los que se llega por Ollama.",
            body=[
                "Tres planos cooperan. El **plano de control local** es la aplicación de Django con su chat, "
                "canvases, base de datos SQLite, programas de agents, permisos, archivos y conexiones de hardware. "
                "La **recuperación local** construye embeddings con `nomic-embed-text` para que el contexto del proyecto se encuentre "
                "rápido. El **razonamiento en la nube** — modelos `:cloud` configurados y servidos por Ollama — hace "
                "chat, llamado de tools, contexto largo, visión y planeación de Multi-Turn. Un modelo local más pequeño también funciona: "
                "una solicitud que no cabe se envía en Compact mode, y el Model Brain afina cada modelo con su "
                "configuración publicada por su creador.",
                "Debido a que la experiencia completa se diseñó alrededor de la capacidad de modelos en la nube de Ollama, un "
                "**plan Ollama Pro o superior** activo es parte de los requisitos de sistema previstos. Esta es una "
                "recomendación técnica independiente: Tlamatini y XAIHT no están patrocinados por, afiliados a ni "
                "compensados por Ollama.",
                "Lo que envíes a un modelo en la nube configurado lo procesa ese proveedor. El uso directo de la Claude API, "
                "los CLIs de coding-agent externos y los servidores MCP remotos se configuran por separado, así que tú "
                "decides qué material sale de tu máquina.",
            ],
            visual="planes", deck="visual"),
        Section("pillars", "LOS PILARES", "Siete subsistemas, una asistente",
            "Todo lo que hace Tlamatini descansa en siete subsistemas que cooperan.",
            points=[
                ("RAG híbrido", "vectores FAISS, palabras clave BM25, extracción de metadatos, presupuesto de contexto y un "
                 "guard de contenido binario mantienen las respuestas ancladas a tu proyecto real."),
                ("Multi-Turn", f"Un planner y un tool loop de hasta 4,096 iteraciones sobre toda la superficie habilitada "
                 f"de {tools} tools integradas, pasos auto-sanadores y Compact mode para modelos pequeños."),
                ("Agentic Control Panel", f"{agents} tipos de agent de arrastrar-y-soltar conectados en workflows "
                 f"`.flw` ejecutables y guardables."),
                ("Prompt Flow Panel", "Nuevo en v1.70.0: prompts, decisiones y embeddings dibujados como un diagrama, "
                 "guardados como `.fpmt`, y ejecutados contra tus modelos."),
                ("ACPX", f"{len(peers)} CLIs de coding-agent externos, desde Claude Code hasta Codex y Gemini, "
                 f"generados como hijos y brokeados a través de 12 tools."),
                ("External MCPs", "Un cliente universal para cualquier servidor MCP sobre cuatro transportes, con hasta "
                 "cinco servidores activos a la vez."),
                ("Skills", f"{skills} runbooks `SKILL.md`, desde code review hasta el onboarding de MCP, entregados al "
                 f"modelo como procedimientos completos."),
            ], deck="cards"),
        Section("jewels", "LO QUE LA DISTINGUE", "Las joyas",
            "Las asistentes de código editan archivos de texto. Tlamatini también lo hace, y luego alcanza engines, placas "
            "y redes, y te deja conectar todo eso de forma visual.",
            points=[
                ("Diseño visual de workflows", f"{agents} tipos de agent en un canvas que conectas, validas, ejecutas, "
                 "pausas y guardas."),
                ("Unreal Engine", "Maneja un editor UE5 en vivo desde el chat o el canvas: actores, Blueprints, niveles, "
                 "assets y materiales."),
                ("Blender", "Escenas, objetos, materiales, renders y código bpy crudo a través del socket del add-on "
                 "oficial."),
                ("Firmware real", "Haz scaffold, compila y flashea placas STM32, ESP32, Arduino y ESPHome detrás de "
                 "preflights fail-safe."),
                ("Proyectos completos", "Encuentra, lee, edita y reconstruye codebases completos con recuperación anclada."),
                ("Cualquier servidor MCP", "Un cliente para el ecosistema MCP: stdio, streamable HTTP, SSE y "
                 "WebSocket."),
                ("Evaluación de seguridad", "Trabajo autorizado de Kali, ProjectDiscovery y nmap, manejado desde el chat."),
                ("Defensa blue-hat", "Un toolkit de monitoreo y respuesta de Windows ejecutado por un administrador."),
            ], deck="cards"),
        Section("glance", "DE UN VISTAZO", "Los números, derivados de la fuente",
            "Cada cifra de abajo se contó desde el repositorio mientras se generaba este dossier.",
            body=[
                f"La superficie Multi-Turn integrada es {f['core']} tools core + {wrapped} lanzadores de agents "
                f"wrapped + {f['acpx_tools']} tools de ACPX y Skill + {f['supervisors']} supervisores de External-MCP "
                f"= **{tools} tools**. Los servidores MCP externos sanos y activos agregan encima sus propios "
                f"tools `ext__<server>__<tool>`.",
                f"La aplicación lleva {f['js']} módulos de JavaScript, {f['css']} hojas de estilo y "
                f"{f['templates']} plantillas de página, {f['migrations']} migraciones de base de datos y "
                f"{f['requirements']} requirements de Python fijados.",
            ],
            visual="metrics", deck="metrics"),
    ])

    architecture = Chapter("architecture", "II", "Cómo funciona",
        "De una tecla en el browser a un resultado verificado en el disco: las capas, el ciclo y el veredicto.",
        accent="copper", sections=[
        Section("layers", "ARQUITECTURA", "Cinco capas, de la casilla al tool",
            "Una solicitud pasa por cinco capas, cada una con una responsabilidad, entre el browser de arriba "
            "y los back-ends de modelo de abajo.",
            body=[
                "Arriba de las capas están las páginas del browser — el chat, el Agentic Control Panel y el Prompt "
                "Flow Panel — que hablan con Django Channels sobre WebSockets bajo el servidor ASGI Daphne. Abajo "
                "de ellas están los back-ends de modelo de lenguaje: Ollama (local y en la nube), Anthropic Claude y Qwen vision.",
                "Una fila en la base de datos sólo activa o desactiva una capacidad. Nunca crea una: un proveedor MCP "
                "necesita su servicio de runtime y su context chain, y un tool necesita su implementación.",
            ],
            visual="layers",
            visual_data={"layers": [
                ("Casillas persistentes", "Las filas de Mcp, Tool, Agent y Skill deciden qué está habilitado; los "
                 "diálogos de Configurar los cambian."),
                ("Servicios MCP", "System-Metrics (WebSocket :8765) y Files-Search (gRPC :50051) "
                 "arrancan con la aplicación."),
                ("Sidecars de contexto", "Chains que deciden si se necesita contexto de sistema o de archivo e "
                 "lo inyectan en el payload."),
                ("Chains de respuesta", "Los chains Basic, history-aware RAG y unified-agent componen el prompt y "
                 "producen la respuesta."),
                ("Tools de unified-agent", f"{f['core']} core, {wrapped} agents wrapped, {f['acpx_tools']} "
                 f"tools de ACPX/Skill y {f['supervisors']} tools supervisores de External-MCP."),
            ]}, deck="visual"),
        Section("journey", "RECORRIDO DE UNA SOLICITUD", "La vida de un mensaje",
            "Once pasos llevan un mensaje del browser a un resultado verificado y reportado.",
            visual="steps",
            visual_data={"steps": [
                ("Enviar", "El browser envía el texto y sus flags de la barra de herramientas sobre el WebSocket del chat."),
                ("Rutear", "AgentConsumer la recibe, la atribuye al usuario y encola la recuperación."),
                ("Contexto", "Decide si se carga contexto RAG y si se necesita búsqueda web."),
                ("Cadena", "Se elige el chain RAG, Basic o Unified-Agent y se ajusta al modelo."),
                ("Compuerta", "Multi-Turn elige la ejecución planeada; ACPX filtra sus doce tools dentro o fuera."),
                ("Permiso", "Con Ask Execs activado, un tool riesgoso espera Permitir o Denegar."),
                ("Precarga", "Los sidecars de System-metrics y file-search agregan contexto cuando ayuda."),
                ("Ciclo", "Las llamadas a tools corren, los agents wrapped se lanzan, cada paso del modelo se auto-sana."),
                ("Veredicto", "El auto-reporte de cada agent decide SUCCESS o FAILED."),
                ("Respuesta", "La respuesta regresa en streaming con las tablas del Exec Report y Create Flow."),
                ("Limpieza", "El orphan reaper barre los console hosts que dejan los procesos hijos."),
            ]}, deck="visual"),
        Section("multiturn", "MULTI-TURN", "El loop del operador",
            "Con Multi-Turn marcado, Tlamatini deja de ser una asesora y se vuelve una operadora: planea, "
            "llama tools, lee sus resultados y continúa hasta que la tarea está hecha.",
            body=[
                "Un planner de ejecución global construye un plan con alcance de solicitud y pistas de capacidad, pero el executor "
                "ata la **superficie completa de tools habilitada**: cada tool, agent wrapped y skill habilitado, con ACPX "
                "todavía filtrado por su propia casilla. Un diseño anterior ataba sólo un subconjunto estrecho del planner y "
                "podía dejar al loop sin el único tool que necesitaba.",
                "El loop corre hasta 4,096 iteraciones. Las llamadas idénticas a un agent wrapped en una solicitud se "
                "deduplican, un rompedor de repetición empuja a un modelo que da vueltas, y cada agent wrapped corre en "
                "su propia carpeta de runtime aislada, así que las plantillas nunca se modifican.",
                "Cuando al menos un agent tuvo éxito, la respuesta trae un botón **Create Flow**. Convierte exactamente "
                "las llamadas a tools exitosas en un workflow `.flw` cargable en el canvas, normalizado y con secretos redactados "
                "por el backend, así que una conversación puede volverse un workflow reutilizable.",
            ],
            points=[
                ("Paso a paso", "Una acción concreta a la vez; espera tu READY o tu output."),
                ("Ask Execs", "Una compuerta humana de Permitir/Denegar antes de cada paso riesgoso."),
                ("Exec Report", "Una tabla por familia de agent, una fila por cada llamada real a un tool."),
                ("ACPX", "Agrega los tools de coding-agent externo y de Skill a la superficie."),
            ], deck="split"),
        Section("healing", "AUTO-SANACIÓN", "Nunca colgarse, nunca descartar, nunca mentir",
            "Cada llamada al modelo dentro del loop pasa por un invocador auto-sanador por solicitud que cambia "
            "a una táctica genuinamente distinta cada vez que ocurre una falla transitoria.",
            body=[
                "Cada intento corre bajo un watchdog. La configuración que se envía permite 900 segundos, deliberadamente "
                "más que el timeout de 600 segundos del cliente del modelo, así que el watchdog nunca abandona una llamada que el "
                "cliente todavía terminaría; el botón Cancelar se sondea cada cuarto de segundo, así que nunca se "
                "bloquea para siempre. La escalera recorre seis tácticas y sigue hasta 4,096 de ellas. Sólo "
                "tú, con Cancelar, la detienes.",
                "Si la escalera alguna vez se agota después de que ya corrieron agents, termina con gracia a partir de ese trabajo "
                "real: el botón Create Flow y el Exec Report sobreviven, y la respuesta dice qué pasó.",
                "La recuperación se narra en vivo. Las líneas de estado como “Tactic #3 … I will NOT hang” llegan en "
                "streaming al chat conforme pasan, y una SELF-HEALING NOTE abre la respuesta final.",
            ],
            callout=("Los bugs reales no se ocultan",
                     "Sólo las fallas transitorias — timeouts, resets, HTTP 429 y 5xx — disparan nuevas "
                     "tácticas. Un error determinista como un schema malo se lanza de inmediato para que se arregle."),
            visual="ladder",
            visual_data={"rungs": [
                ("1", "normal", "La solicitud completa otra vez."),
                ("2", "reintento", "La misma solicitud con tools atados; la mayoría de los parpadeos se resuelven aquí."),
                ("3", "reintento paciente", "Espera, luego reintenta con paciencia extra."),
                ("4", "recortar contexto", "Conserva los mensajes de sistema y los últimos doce."),
                ("5", "mínimo", "Conserva los últimos seis mensajes; los tools quedan atados."),
                ("6", "resumen simple", "Último recurso: resume con la verdad lo que se reunió."),
            ]}, deck="visual"),
        Section("compact", "COMPACT MODE", "Cada solicitud cabe en el modelo al que se envía",
            "Un modelo cuya ventana real no puede contener la solicitud completa recibe una compacta; un modelo "
            "que sí puede contenerla recibe exactamente la solicitud que siempre recibió.",
            body=[
                "Ollama no rechaza una solicitud demasiado grande para un modelo local: se queda con el final y responde "
                "a partir de eso. Un qwen2.5 local cuyos 32,768 tokens se dividieron entre dos slots de solicitud leyó "
                "16,386 tokens de una solicitud de unos 52,000, perdió las métricas de sistema en vivo, y respondió una "
                "pregunta de CPU con la hora.",
                "El propio conteo de Ollama es ahora la prueba. Cuando los caracteres enviados no caben en los tokens que Ollama "
                "dice que leyó, la solicitud se cortó, y ese conteo se aprende como la ventana real del modelo. El "
                "context length reportado de un modelo local nunca se toma como su ventana por solicitud, porque "
                "los slots de solicitud paralelos la dividen.",
                "Una solicitud que cabe en la ventana usable se envía byte por byte, como antes. Si no, el Compact "
                "mode conserva System-Metrics y Files-Search, cuyo contexto viaja dentro de la pregunta, y "
                "ata sólo las filas que marcas. Desde v1.75.0 eso es un switch de la barra de herramientas: marcarlo desmarca cada "
                "fila de Configurar menos esas tres y pausa los External MCPs, y cada fila muestra su precio. El "
                "system prompt se reconstruye por prioridad de reglas y se cierra con una "
                "nota de siete reglas, y el historial conserva los seis mensajes más nuevos. Un primer paso que Ollama aun así "
                "cortó se reajusta y se reenvía antes de que corra cualquier tool.",
            ],
            points=[
                ("Completo", "Un modelo que puede contener la solicitud la recibe sin cambios, byte por byte."),
                ("Compact", "Un switch de la barra de herramientas: sólo se atan las filas que marcas, cada una con su precio."),
                ("Bloqueado", "Un modelo demasiado pequeño para todo activa Compact por sí mismo y lo bloquea."),
                ("Tu decisión", "`context_compact_mode` es auto de forma predeterminada, o always o never, obedecido exactamente."),
            ],
            callout=("Falla hacia la solicitud completa",
                     "Cada parte del ajustador falla abierto: cuando algo es incierto, la solicitud completa se "
                     "envía exactamente como antes."),
            deck="cards"),
        Section("brain", "MODEL BRAIN", "Cada modelo afinado desde fuentes formales",
            "Desde v1.76.0 cada modelo recibe su propio sampling, nivel de thinking y tamaño de contexto, tomados de "
            "fuentes formales, en vez de un conjunto fijo de valores para cada modelo.",
            body=[
                "Los valores vienen, en este orden, de tu propio `model_brain_overrides`; de una base de conocimiento integrada "
                "cuyos perfiles citan cada uno su model card del fabricante o el `generation_config.json` de Hugging Face (GLM-5, "
                "DeepSeek-V4, MiniMax-M3, Gemma 4, Qwen 3.5, Qwen 2.5, gpt-oss, Kimi, Mistral Large 3 y "
                "Nemotron 3); de un perfil aprendido una vez, en segundo plano, para un modelo que todavía no conoce y "
                "guardado fuera de la instalación para que sobreviva a las actualizaciones; de los parámetros que Ollama publica para el "
                "modelo; y finalmente de los valores predeterminados del propio modelo. El contexto solicitado nunca excede lo que el modelo "
                "puede leer de verdad.",
                "Dentro de una respuesta, entre llamadas a tools, un modelo que piensa recibe de vuelta su propio razonamiento anterior, como "
                "lo requiere su fabricante, en vez de empezar de cero en cada paso; se descarta entre tus "
                "preguntas, y el medidor de contexto lo cuenta. En Config ▸ Models, Guardar abre un diálogo de Auto-tuning "
                "que afina cada modelo configurado frente a ti, con la fuente de cada valor.",
                "Los relojes de estancamiento que abandonaban un modelo lento y empezaban otra vez desde cero se quitaron. "
                "Medido con los propios números de Ollama, leer incluso un prompt muy largo no es el cuello de botella en "
                "Ollama cloud: el tiempo es el razonamiento que el modelo genera, y un reloj no puede distinguir una llamada muerta "
                "de un modelo que todavía está pensando. El watchdog de auto-sanación y el límite de tiempo del cliente se mantienen.",
            ],
            points=[
                ("Fuentes formales", "Tus overrides, perfiles citados, perfiles aprendidos, Ollama, valores predeterminados del modelo."),
                ("Contexto real", "La ventana solicitada nunca excede lo que el modelo puede leer."),
                ("Razonamiento conservado", "Los modelos que piensan conservan su hilo de pensamiento entre llamadas a tools."),
                ("Auto-tuning", "Config ▸ Models ▸ Guardar muestra cada modelo afinado, con sus fuentes."),
                ("Sin relojes de estancamiento", "Un modelo lento nunca se tira y se reinicia."),
                ("Tu decisión", "`model_brain: off` restaura el sampler fijo heredado exactamente."),
            ],
            callout=("Ningún nombre de modelo en el código",
                     "Un modelo nuevo obtiene sus valores de la base de conocimiento, la investigación, Ollama o sus propios valores predeterminados, "
                     "nunca de un branch escrito para un nombre de modelo, y un valor que tú estableces siempre gana."),
            deck="cards"),
        Section("verdict", "EXEC REPORT", "Un veredicto en el que puedes confiar",
            "Un código de salida es un bit. El auto-reporte estructurado del propio agent es un registro tipado, y "
            "supera al código de salida.",
            body=[
                "`agent_verdict.py` analiza el bloque `INI_SECTION` de cada agent en un árbol tipado y corre una tabla de reglas ordenada "
                "sobre él. No hay llamada a modelo ni heurística, así que la misma entrada siempre da "
                "el mismo color. El vocabulario de status es cerrado: cinco conjuntos disjuntos, unidos como "
                "`KNOWN_STATUSES`, y una prueba de todo el repositorio rechaza cualquier token de status que un agent invente.",
                "Un diagnóstico de sólo lectura que reporta un problema tuvo éxito, porque el hallazgo es el "
                "entregable. El trabajo degradado, el trabajo no hecho y los errores de agent quedan en rojo. Una fila roja por lo tanto "
                "significa que no existe un entregable solicitado limpio, nunca sólo que una revisión encontró algo.",
            ],
            table={"columns": ["Regla", "Se dispara cuando", "Veredicto"], "widths": [0.10, 0.66, 0.24], "rows": [
                ["R1", "El agent no escribió auto-reporte", "Decide el código de salida"],
                ["R2", "El agent declara error o failed", "FAILED"],
                ["R3", "Trabajo no hecho: refused, not_found, engine_unavailable …", "FAILED"],
                ["R3b", "Degradado: tokens_only, compiled_with_errors, operator_required …", "FAILED"],
                ["R4", "Un diagnóstico terminó: invalid, findings, no_matches, listed …", "SUCCESS"],
                ["R5", "Un flag explícito de success u ok", "Ese flag"],
                ["R6", "Un conteo de errors distinto de cero", "FAILED"],
                ["R7", "Nada decisivo y un código de salida distinto de cero", "FAILED"],
                ["R7b", "Una terminación nombrada: ok, created, sent …", "SUCCESS"],
                ["R8b", "Un token de status fuera del vocabulario", "SUCCESS, marcado"],
                ["R8", "Ninguna señal de falla en absoluto", "SUCCESS"],
            ]},
            callout=("Por qué R4 supera a R5 y R6",
                     "Un linter que funcionó perfectamente reporta `status: invalid`, `success: False` y "
                     "`errors: 2` juntos. Los últimos dos describen el documento, no el agent."),
            deck="table"),
        Section("askexecs", "PERMISO", "Ask Execs: una compuerta humana antes de pasos riesgosos",
            "Con Ask Execs activado, el executor se bloquea antes de cada tool riesgoso y espera Permitir o Denegar en "
            "el browser. Un solo Denegar detiene toda la cadena y deja un banner rojo "
            "“Execution interrupted”.",
            body=[
                "La compuerta es un allowlist explícito, elegido tier por tier. Todo camino dudoso se resuelve en Denegar: un "
                "prompt fallido, un Cancelar o un browser desconectado nunca deja correr un tool riesgoso sin confirmar. "
                "Desmarcar Ask Execs durante una ejecución relaja esa ejecución; marcarlo otra vez rearma los prompts.",
            ],
            table={"columns": ["Nivel", "¿Pregunta?", "Agents"], "widths": [0.26, 0.16, 0.58], "rows": [
                ["Comandos y runners de script", "Sí", "Terminater, Executer, Pythonxer, SSHer, Kalier, Dockerer, "
                 "Kuberneter, SQLer, Mongoxer, Gitter, Jenkinser, PSer, J-Decompiler"],
                ["Persistencia del Editor", "Sí", "Interactor nuevo/guardar; las lecturas y la escritura guiada no persisten un archivo."],
                ["A · destruye o sobrescribe", "Sí", "Deleter, Mover, File-Creator, Editor, De-Compresser, "
                 "unzip, PDFer, LaTeXer"],
                ["D · sistemas remotos", "Sí", "SCPer, Apirer, Nmapper, Discoverer, Crawler, "
                 "NetSpeed-Calculator"],
                ["B · mensajería", "No", "Emailer, Whatsapper, Telegrammer, Instant Messaging "
                 "Doctor: todavía se requiere autorización del usuario"],
                ["C · escritorio y hardware", "No", "Keyboarder, Mouser, Windower, Playwrighter, agents de firmware"
                 ", Blenderer, Unrealer: visibles mientras actúan"],
            ]}, deck="table"),
        Section("rag", "RECUPERACIÓN", "Anclada en tu proyecto, y sólo en su texto",
            "La recuperación híbrida combina vectores FAISS con palabras clave BM25, extrae metadatos, presupuesta el "
            "contexto y cae con gracia cuando un chain no puede recuperar.",
            body=[
                "Cuando cargas un directorio o archivo, ese contexto cargado supera su auto-conocimiento: una solicitud "
                "de “resumir el proyecto” se responde desde tu proyecto, no desde una descripción de "
                "ella misma.",
                "Antes de que cualquier archivo se incruste, un guard de contenido binario revisa sus bytes en una cascada de cortocircuito "
                "que lee a lo más un bloque de 8 KiB. Los archivos binarios se descartan exactamente como un nombre que "
                "elegiste omitir, y cada descarte se nombra en `tlamatini.log` bajo `--- [BINARY-GUARD]`.",
                "El guard falla abierto: cualquier duda significa “cárgalo como texto”, porque borrar silenciosamente "
                "contexto real es peor que incrustar un archivo raro. La etapa del byte-order-mark corre antes de la del byte "
                "NUL, o cada documento UTF-16 desaparecería.",
            ],
            visual="cascade",
            visual_data={"stages": [
                ("Extensión", "Sufijo binario conocido, sin I/O"),
                ("Muestra", "Una lectura de 8 KiB"),
                ("Vacío", "Nada que incrustar"),
                ("BOM", "UTF-8/16/32 es texto"),
                ("Firma", "45 números mágicos"),
                ("Byte NUL", "Prueba binaria clásica"),
                ("Proporción de control", "Proporción de bytes no-texto"),
                ("UTF-8", "Indescodificable y sucio"),
            ]}, deck="visual"),
        Section("compiler", "COMPILADOR DE FLOW", "Un compilador para el canvas y el chat",
            "Los snapshots del canvas y los borradores generados en el chat compilan a través del mismo registro de Agent Contract "
            "antes de que cualquier archivo llegue al pool de sesión.",
            body=[
                "El contrato de cada agent declara qué campo de configuración escribe una conexión en cada slot, "
                "qué campos puede leer Parametrizer, qué paths son secretos a redactar, y si es un "
                "singleton, de larga duración o nunca inicia sus targets. Ambas superficies se normalizan en un solo "
                "`FlowSpec` (schema versión 2).",
                "El botón Iniciar del canvas compila el snapshot en vivo en modo escritura, así que un flow editado pero sin guardar "
                "corre bajo la misma validación que un archivo recién cargado. Validar usa un dry run que previsualiza "
                "la configuración compilada sin tocar el disco.",
                f"Los agents que alimentan a Parametrizer emiten un bloque `INI_SECTION` atómico por resultado. "
                f"{f['parametrizer_sources']} agents actualmente declaran outputs estructurados.",
            ],
            code=("INI_SECTION_APIRER<<<\n"
                  "url: https://example.org/status\n"
                  "status: 200\n"
                  "\n"
                  "{\"service\": \"ok\"}\n"
                  ">>>END_SECTION_APIRER"),
            deck="split",
            deck_points=[
                ("Contratos", "Slots de conexión, campos de Parametrizer, paths secretos, flags de ciclo de vida."),
                ("Iniciar", "Compila el canvas en vivo en modo escritura antes de que corra cualquier agent."),
                ("Validar", "Un dry run que previsualiza la configuración compilada."),
                ("Create Flow", "Los borradores del chat pasan el mismo normalizador y redacción."),
            ]),
        Section("resilience", "CONFIABILIDAD", "Construida para seguir corriendo",
            "Mecanismos pequeños y deliberados mantienen vivo el core bajo las condiciones que antes lo detenían.",
            points=[
                ("Escudo de consola", "El archivo de log se escribe primero; la salida de consola pasa por una cola "
                 "acotada, así que hacer clic en la consola no puede congelarla. Desde v1.76.0 las líneas se colorean por nivel."),
                ("Limpiador de huérfanos", "Tres niveles barren descendientes muertos y console hosts huérfanos después de los tools, "
                 "después de las respuestas y al apagar, sin nunca lanzar una excepción al chat."),
                ("Líneas de log por usuario", "Las líneas llevan una etiqueta de cinco caracteres como [a3] para que los usuarios "
                 "y turnos concurrentes nunca se confundan."),
                ("Ctrl+C limpio", "El manejador de señal sólo pone un evento; un worker limpia, un watchdog "
                 "garantiza la salida, y un segundo Ctrl+C sale de inmediato."),
                ("Puerto configurable", "`django_port` mueve el puerto web sin recompilar y cae de vuelta a "
                 "8000 ante cualquier valor malo."),
                ("Temp y Templates", "Los archivos temporales viven bajo la carpeta Temp de la aplicación; los proyectos "
                 "generados usan de forma predeterminada su carpeta Templates."),
            ], deck="cards"),
    ])

    surfaces = Chapter("surfaces", "III", "Dónde trabajas con ella",
        "El chat, los dos canvases, el catálogo y los diálogos que operan todo lo demás.",
        accent="gold", sections=[
        Section("chat", "LA PÁGINA DEL CHAT", "Conversación con modos",
            "La página del chat es donde hablas con ella. Hasta ocho switches de la barra de herramientas deciden cómo corre cada solicitud.",
            body=[
                "Junto a la conversación hay un canvas que muestra código, texto y PDFs. Pega un screenshot con "
                "Ctrl+V o suelta imágenes en cualquier página: ella los guarda en su carpeta Temp y escribe el path completo "
                "en tu mensaje, listo para Image-Interpreter. Un anillo de contexto entre la barra de herramientas y el "
                "cuadro de mensaje muestra cuánto de la ventana del modelo usa la solicitud real, medido por el "
                "backend en bytes. Los tokens usan el propio prompt_eval_count de Ollama para la solicitud; un "
                "estimado se etiqueta hasta que llega un conteo medido. Cuando Ollama cortó una solicitud el anillo lo dice, "
                "y una respuesta construida a partir de una solicitud cortada lleva una advertencia CONTEXT-WINDOW.",
                "Su avatar dice las respuestas en voz alta cuando se lo pides. Desde v1.72.3, un movimiento de sílabas más claro y "
                "un cierre más rápido hacen sus labios más fáciles de seguir, con la apertura limitada a su retrato. Después de "
                "iniciar sesión, presionar Enter en la página de bienvenida te lleva directo al chat.",
                "Las tablas de respuesta se mantienen legibles con cada modelo: sólo una celda cuyo texto caería por debajo de 3:1 "
                "de contraste se recolorea, mientras que las tablas legibles, las tablas del Exec Report y los fondos con gradiente "
                "conservan sus colores.",
            ],
            table={"columns": ["Interruptor", "Qué hace"], "widths": [0.24, 0.76], "rows": [
                ["Multi-Turn", "Modo operador planeado con llamado de tools; sin marcar significa respuestas directas de un solo tiro."],
                ["Exec Report", "Agrega tablas de ejecución por agent; disponible mientras Multi-Turn está activado."],
                ["ACPX", "Agrega los doce tools de ACPX y Skill a la superficie atada; desactivado de forma predeterminada."],
                ["Ask Execs", "Permitir/Denegar antes de cada tool riesgoso; un Denegar detiene la cadena."],
                ["Paso a paso", "Una acción concreta a la vez, esperando tu respuesta antes de la siguiente."],
                ["Internet", "Permite que una búsqueda web agregue contexto a la respuesta."],
                ["Compact mode", "Ata sólo las filas que marcas; bloqueado en activado cuando el modelo no puede contener todo."],
                ["Self-modify", "Ejecuciones de source y builds self-modify; envía el auto-conocimiento, bloqueado en desactivado si es muy grande."],
            ]}, deck="table"),
        Section("composer", "EL CUADRO DE MENSAJE", "Más espacio para escribir, o más espacio para leer",
            "Arrastra el divisor arriba del cuadro de mensaje. Con su avatar desacoplado, el cuadro puede encogerse hasta sus botones.",
            body=[
                "El divisor entre la conversación y el cuadro de mensaje sigue el puntero y el teclado. "
                "Las teclas de flecha lo mueven un paso y Shift+flechas cinco; Home o un doble clic encogen el cuadro a "
                "su mínimo, End lo hace tan alto como se permite, y Escape termina un arrastre. Los lectores de pantalla oyen la "
                "altura del cuadro. La barra de herramientas, el medidor de contexto, las filas de adjuntos y de dictado se miden, así que ninguna de "
                "ellas se corta.",
                "Acoplado, su retrato conserva su espacio arriba de los botones de acción. Desacoplado, el cuadro puede encogerse hasta "
                "esos botones más un guardia de seis píxeles, y acoplarla de nuevo le devuelve su espacio al retrato. "
                "En una ventana corta el cuadro se desplaza dentro de sí mismo, y en una pantalla angosta el espacio de trabajo se desplaza mientras "
                "la página y sus diálogos se quedan en su lugar.",
                "Acoplado, su retrato ahora también sigue el divisor: arrastrar la barra hacia abajo lo encoge a un cuadrado de 120 píxeles y arrastrar hacia arriba lo devuelve. Se envió en v1.83.0.",
                "En v1.85.0, el retrato y su marco se quedan centrados sobre la fila completa de Mic a Send. "
                "Vistas → Canvas puede darle al chat el ancho completo; Vistas → Restablecer distribución restaura ambos paneles "
                "y acopla el retrato conservando el documento, el borrador y el contexto.",
            ],
            points=[
                ("Arrastra o escribe", "El puntero, las flechas, Shift+flechas, Home y End mueven el divisor."),
                ("Desacoplado", "El cuadro de mensaje puede encogerse hasta sus propios botones de acción."),
                ("Acoplado", "Un retrato centrado arriba de Mic a Send, hasta un cuadrado de 120 píxeles."),
                ("Ventanas chicas", "El cuadro se desplaza solo; los diálogos se quedan dentro de la ventana."),
            ], deck="cards"),
        Section("drop", "HISTORIAL DEL CHAT", "Descarta un mensaje de la conversación",
            "Cada tarjeta de mensaje tiene Descartar junto a Copiar, para tus prompts y las respuestas de Tlamatini.",
            body=[
                "Presiona Descartar y lee la confirmación con el tema. Cancelar empieza con el foco, así que Enter cancela de forma "
                "predeterminada. El botón rojo Descartar confirma el borrado. Escape y el botón de cerrar también cancelan. "
                "El mensaje guardado desaparece del chat y del historial de la base de datos que se usa para solicitudes futuras.",
                "Los demás mensajes se quedan. Descartar sólo un prompt deja su respuesta; descartar sólo una respuesta "
                "deja su prompt. Quita ambas tarjetas para quitar el intercambio. Un prompt del usuario también se lleva las "
                "filas de Referenced Rephrase que lo siguen directamente, así que una recarga no puede mostrar esas palabras duplicadas.",
                "Las pestañas conectadas del mismo usuario quitan las tarjetas guardadas después de que el servidor confirma. Una tarjeta de status, "
                "de error o de reintento sin un id de mensaje guardado sólo desaparece de la pantalla actual. "
                "La conexión rechaza Descartar mientras está respondiendo, y un chat desconectado te pide reconectar.",
            ],
            points=[
                ("Elegir", "Descartar está junto a Copiar en las tarjetas de mensajes del usuario y de la asistente."),
                ("Confirmar", "Cancelar empieza con el foco. Descartar en rojo confirma; Escape y cerrar cancelan."),
                ("Quitar", "Borra el mensaje guardado del historial del chat. Su prompt o respuesta pareada se queda."),
                ("Continuar", "La siguiente solicitud lee el historial actualizado sin reconectar."),
            ], deck="cards"),
        Section("drop_scope", "MEMORIA Y EFECTOS", "Qué queda después de Descartar",
            "Borrar una tarjeta del chat cambia el contexto de la conversación futura. Las notas guardadas por separado y el trabajo terminado se quedan.",
            body=[
                "Cada solicitud recarga hasta las ocho filas de AgentMessage más nuevas con DBChatHistoryLoader, y luego "
                "filtra el contenido de status y de rephrase. No hay un resumen de conversación en caché ni un checkpoint de LangGraph "
                "que haya que limpiar. Quitar una fila deja que la ventana alcance una fila más vieja cuando existe.",
                "Un tool de memoria de External MCP habilitado guarda notas aparte de AgentMessage. Descartar "
                "no borra ese grafo de conocimiento; pídele a Tlamatini que también olvide la nota guardada. Los mensajes que se quedan "
                "también pueden repetir un dato de una tarjeta borrada, así que Descartar no garantiza un olvido completo.",
                "Los archivos creados, los mensajes enviados, las ejecuciones de agents y las filas del Exec Report siguen siendo trabajo real terminado. "
                "Descartar su prompt o su respuesta no puede deshacer esos efectos. Un botón Create Flow pertenece a "
                "su tarjeta de respuesta y desaparece con ella, así que descarga el .flw que necesites antes de borrar la tarjeta.",
            ],
            points=[
                ("Historial", "Cada solicitud recarga una ventana de hasta las ocho filas más nuevas de la base de datos."),
                ("Notas guardadas", "La memoria de External MCP va aparte. Pídele que también olvide su nota."),
                ("Otros mensajes", "La respuesta o el prompt pareado se queda y puede repetir la misma información."),
                ("Trabajo terminado", "Los archivos y los mensajes enviados se quedan. Guarda un flow que necesites antes de descartar su tarjeta."),
            ], deck="cards"),
        Section("dictation", "INPUT DE VOZ DIRECTO", "Habla junto a Enviar",
            "El micrófono captura primero; ningún paso de selección de tools por el modelo se interpone entre el clic y la grabación.",
            body=[
                "Haz clic en Micrófono junto a Enviar, espera a que diga Escuchando, y habla al micrófono del "
                "host de Tlamatini. El nivel real de entrada, el tiempo transcurrido y la cuenta regresiva de silencio se quedan en el chat. "
                "Después de la ventana de silencio configurada (3.5 segundos predeterminados de fábrica), corre el reconocimiento y el "
                "texto se agrega al borrador existente. Config > Micrófono elige el envío automático normal del formulario "
                "o un borrador editable para Enviar a mano.",
                "El modo de revisión no inicia ninguna tarea hasta Enviar. Un segundo clic o Escape cancela; un reconocimiento vacío o "
                "con error no envía nada. Los modos actuales y el comportamiento de permisos siguen vigentes. "
                "El avatar confirma el envío con la voz del browser y respeta el modo Silencio.",
            ],
            points=[
                ("Clic", "Inicio directo de Whisperer; el micrófono del host sólo se abre para una grabación."),
                ("Escuchar", "Las muestras en vivo mueven el indicador del chat y la compuerta de silencio configurada."),
                ("Reconocer", "faster-whisper local o el motor de voz en la nube configurado explícitamente."),
                ("Enviar o revisar", "Envía una vez con los modos actuales, o revisa el borrador editable y presiona Enviar tú."),
            ], deck="cards"),
        Section("micsettings", "CONFIGURACIÓN", "Config termina con Micrófono",
            "Elige Enviar automáticamente o un borrador editable, con el mismo estilo de diálogo que el resto de Tlamatini.",
            body=[
                "La etiqueta del botón es Micrófono. Config > Micrófono va después de Voz y controla qué pasa después del reconocimiento. "
                "Enviar automáticamente es lo predeterminado. Dejar en el input del chat restaura la edición sin lanzar "
                "una tarea ni la confirmación de procesamiento; corrige las palabras y luego presiona Enviar.",
                "Las preferencias se guardan en este browser para la siguiente grabación. Cada grabación tiene su propio snapshot. "
                "Los campos sin valor heredan la plantilla actual de Whisperer; Restablecer y luego Guardar restaura esa herencia. "
                "Cancelar, cerrar y Escape descartan los cambios sin guardar; los clics afuera dejan el diálogo abierto. "
                "Config > Voz controla la reproducción del avatar; Config > Modelos > Voz elige el reconocedor.",
            ],
            points=[
                ("Input", "Dispositivo del host configurado/predeterminado/listado, actualizar y ganancia por software de 0 a 300%."),
                ("Compuerta de sonido", "Silencio de 0.3-20 segundos, tope de 5-600 segundos, sensibilidad adaptativa o manual."),
                ("Reconocimiento", "Idioma, traducción al inglés, tasa/canales de captura, beam size local y VAD."),
                ("Barandales", "Valida la configuración antes de capturar; los dispositivos guardados que se quitaron o son ambiguos no pueden cambiar las entradas en silencio."),
            ], deck="cards"),
        Section("dictationruntime", "SERVICIO INTERNO", "Una consola principal, sin ventanas extra",
            "Los requisitos de visibilidad para desarrolladores no se convierten en ventanas adicionales del producto.",
            body=[
                "La conexión autenticada del mismo origen /ws/chat-voice/ prepara un worker residente por "
                "proceso web. El Python source/incluido corre chat_worker.py; el proceso congelado de Django se queda "
                "libre del stack de ML de voz. Un socket loopback privado autenticado por token lleva los frames de control "
                "y de resultado. La preparación no abre el micrófono.",
                "No intervienen PowerShell, conhost, activación de foco ni requisitos de visibilidad de consola. "
                "El stdout/stderr del worker fluye por agent.chat_voice_runtime hacia la consola/log principal. "
                "Un arranque con error y el apagado recogen al hijo. La Config se recarga por trabajo; los modelos compatibles se "
                "guardan en caché, y los resultados cancelados tardíos no pueden enviarse.",
            ],
            points=[
                ("Dueño de la UI", "El composer muestra la grabación y la transcripción; sin segunda consola."),
                ("Configuración", "Herencia de modelo/plantilla más overrides de captura de Micrófono validados por grabación."),
                ("Frontera", "El botón directo es input, no un tool wrapped ni una fila del Exec Report."),
                ("Release", "Incluye los módulos de consumer/runtime/settings, el validador y el worker incluidos, el JS/CSS de Micrófono y la plantilla."),
            ], deck="cards"),
        Section("dictationevidence", "ALCANCE DE LA VERIFICACIÓN", "Comportamiento medido del source",
            "Las revisiones fechadas del source son evidencia, no la afirmación de que un instalador anterior contiene el cambio.",
            body=[
                "El 27 de septiembre de 2026 pasaron 108 regresiones de voz y 42 pruebas existentes del tema de diálogos. "
                "El worker actualizó 16 entradas del host y se reinició dos veces sin ventanas extra ni cambios de foco. "
                "Una captura real anterior en el host dio muestras en 297 ms después del inicio directo; "
                "se observaron la cancelación y la salida normal del worker. Dos ciclos de arranque/apagado no crearon "
                "ventanas visibles adicionales y dejaron sin cambio el foco en primer plano.",
                "La suite actualizada de browser visible pasó 62 revisiones con transporte controlado, incluidos ambos modos, "
                "la persistencia de la configuración, los estilos de control compartidos y las distribuciones angostas. Antes, el reconocimiento en caché "
                "de un archivo de voz sintética de 5.768 segundos tardó 0.203 segundos, contra 11.094 "
                "segundos en la primera decodificación. Son observaciones separadas, no garantías de latencia de punta a punta. "
                "Esas revisiones no certificaron ninguna tarea nueva en vivo de Ollama ni un instalador recompilado.",
            ],
            points=[
                ("Source actual", "108 regresiones de voz, 42 pruebas de tema y sondeos reales de metadatos/ciclo de vida del worker."),
                ("Evidencia del browser", "62 revisiones visibles con transporte controlado; aparte del ASR en vivo."),
                ("Límites", "La carga en frío del modelo, la latencia del proveedor y el hardware varían; no hay promesa de latencia cero."),
                ("Guía detallada", "docs/chat-microphone-design.md registra la configuración, el protocolo y la evidencia."),
            ], deck="cards"),
        Section("navbar", "NAVEGACIÓN", "La barra de menús en v1.91.1",
            "Vistas controla el espacio de trabajo, Paneles abre los editores de flows, y Config guarda la configuración.",
            table={"columns": ["Menú", "Qué encuentras ahí"], "widths": [0.20, 0.80], "rows": [
                ["Abrir · Guardar", "Abre un archivo en el canvas; Guardar en el menú elige un destino con el Guardar como nativo."],
                ["Vistas", "Muestra Canvas o Terminals; Restablecer distribución restaura el espacio de trabajo."],
                ["Contexto", "Carga un directorio o archivo como contexto, y fija las omisiones por tipo de archivo."],
                ["Paneles", "Agentic Control Panel, Prompt Flow Panel y, para el staff, el Admin Panel. "
                 "Se puede usar mientras ella está ocupada."],
                ["ACPX-Skills", "Examina, configura, diagnostica y recarga el catálogo de skills."],
                ["Externos", "El diálogo de External MCPs: catálogo, activación y disponibilidad de runtimes."],
                ["Config", "Configurar MCPs, Configurar Agents, Modelos, URLs, Contactos, Access Keys Wizard, "
                 "Voz, Micrófono y Live Editor & Terminater (ritmo, narración y preferencias de interacción)."],
                ["DB", "Backup de base de datos seguro con WAL y reemplazo por etapas."],
                ["Reconectar · Acerca de", "Reconstruye la conexión del chat; versión, créditos de la autora y Buscar "
                 "actualizaciones. Desde v1.78.0, Acerca de también abre Uso, incluso mientras ella está ocupada."],
            ]}, deck="table"),
        Section("usage", "ACERCA DE → USO · NUEVO EN v1.78.0", "Consulta el uso mientras trabaja",
            "ACERCA DE USO sigue el tema de diálogos compartido y sigue disponible durante una respuesta larga.",
            body=[
                "Abre Acerca de → Uso, y luego elige Créditos en la nube, Actividad del chat o Modelos. La primera pestaña lee "
                "la cuenta de Ollama configurada; las otras vistas identifican la actividad medida del chat principal del "
                "usuario de Tlamatini con sesión iniciada. El registro empieza con esta función y no reconstruye el historial "
                "anterior ni incluye agents hijos ni otras aplicaciones.",
                "El diálogo de escritorio mide 80vw por 74dvh, con un tope de 1440 píxeles de ancho: a lo más 59.2% del área "
                "del cliente. Las pantallas angostas usan 94vw por 63dvh. El texto sigue el tamaño normal de los diálogos, los botones tienen bordes "
                "claros y el cuerpo se desplaza entre controles fijos. Las cifras fraccionarias tienen a lo más dos "
                "decimales. Las barras de color ofrecen tooltips con el foco del teclado y el puntero, además de tablas exactas.",
            ],
            points=[
                ("Créditos en la nube", "Saldo reportado, uso mensual, asignación y semanas/fecha de recarga."),
                ("Actividad del chat", "Tus llamadas medidas, tokens de input/output y tendencias diarias."),
                ("Modelos", "Actividad registrada de modelos y fechas UTC pico; el inventario del servidor a un lado."),
                ("Mientras está ocupada", "Abre y actualiza sin interrumpir la solicitud al modelo."),
                ("Tamaño normal", "Menos del 60% del área del cliente; tipografía común y botones claros."),
                ("Accesible", "Pestañas con teclado, tooltips en las gráficas, trampa de foco y comportamiento normal de Escape/Cerrar."),
            ], deck="cards"),
        Section("usage_truth", "DATOS DE LA CUENTA", "Alcances distintos, claramente identificados",
            "Los créditos mensuales, el uso rodante en la nube y la actividad local registrada responden preguntas distintas.",
            body=[
                "La respuesta autoritativa de /api/balance da la asignación incluida y el saldo restante, "
                "los créditos comprados y el periodo de recarga UTC. Los créditos usados son la asignación menos el saldo "
                "incluido; el total disponible suma los créditos comprados sólo cuando se reportan ambos valores. Los nombres de "
                "plan nunca dan una asignación supuesta. Las semanas/fecha de recarga vienen del periodo devuelto, "
                "no de un ciclo supuesto de 30 días.",
                "/api/usage en la nube da un historial rodante de 7/30 días, incluido el día UTC parcial de hoy. "
                "Ese gasto no son los créditos mensuales usados. El input en caché ya es parte del input. Las fechas "
                "de calendario 7/30 del registro local incluyen hoy y tienen un alcance de medición más estrecho.",
                "La API documentada de Ollama todavía no expone el historial completo por modelo del sitio web ni los vencimientos "
                "individuales de los créditos comprados. El diálogo enlaza a Ollama Usage para los detalles que sólo están en el sitio web. Los campos "
                "que faltan se explican, nunca se reemplazan con valores inventados. Los saldos siguen la cuenta del servidor "
                "configurado, que puede ser distinta del inicio de sesión del usuario en el sitio web.",
            ],
            points=[
                ("Saldo mensual", "Créditos incluidos y comprados reales de /api/balance."),
                ("Historial rodante", "Gasto y tokens en la nube de 7/30 días; aparte del periodo de facturación."),
                ("Gráficas de modelos locales", "Actividad medida del chat principal de Tlamatini, no el historial de todo el sitio web."),
                ("Actualizar", "Los datos sanos se guardan en caché 60 s; una caída breve se reintenta después de 15 s."),
                ("Datos faltantes", "Explica los valores no disponibles o viejos; sin saldos ni conteos de tokens adivinados."),
                ("Referencias", "docs.ollama.com/api/balance y /api/cloud-usage; docs/usage-dashboard.md."),
            ], deck="cards"),
        Section("usage_plans", "DISTRIBUCIÓN ADAPTABLE", "Reporta lo que da la cuenta",
            "La forma de la respuesta elige la distribución; una etiqueta de plan no es un derecho a créditos.",
            body=[
                "Las cuentas Free, Pro y Max con campos de saldo mensual usan tarjetas de créditos. Las respuestas heredadas de sesión y "
                "semanales usan los porcentajes restantes reportados y las horas de reinicio; los campos de costo y "
                "de tokens no soportados se omiten. Las respuestas sólo de compras muestran sólo el saldo dado. Una asignación "
                "mensual de cero no produce un porcentaje inventado.",
                "Según lo revisado el 10 de octubre de 2026, Ollama lista Free, Pro, Max, Team y Enterprise, sin ningún "
                "plan en la nube llamado Unlimited. La ejecución local ilimitada es otra afirmación. Los saldos de Team "
                "se comparten, mientras que este adaptador pide el uso predeterminado del miembro, no el alcance de equipo del administrador. "
                "Los términos comerciales se quedan en ollama.com/pricing; no están fijos en el código del diálogo.",
            ],
            points=[
                ("Mensual", "Asignación, saldo, créditos comprados y periodo de reinicio devueltos."),
                ("Heredado", "Porcentajes restantes de sesión/semanales; sin conversión adivinada a dólares."),
                ("Sólo compras", "Sólo el saldo comprado reportado; sin cuota incluida inventada."),
                ("Free o cero", "Reporta los datos reales y omite los porcentajes cuando la asignación es cero."),
                ("Team", "El saldo de créditos compartido es distinto del uso con alcance de miembro."),
                ("Etiqueta Unlimited", "Nunca se interpreta como créditos ilimitados en la nube."),
            ], deck="cards"),
        Section("acp", "AGENTIC CONTROL PANEL", "Diseña workflows de agents de forma visual",
            f"Arrastra cualquiera de los {agents} tipos de agent al canvas, conecta los triángulos de output con los triángulos "
            "de input, configura cada nodo, valida y presiona Iniciar.",
            body=[
                "Los Agents corren como procesos separados que emiten logs y se comunican por sus archivos `config.yaml`, "
                "con un LED en vivo para cada uno. Los flows se pueden pausar, reanudar y detener, y guardar o cargar como "
                "archivos `.flw`. FlowCreator puede diseñar un flow a partir de una oración, y FlowHypervisor vigila un "
                "flow en ejecución y levanta una alerta cuando algo se ve mal.",
                "Desde v1.70.0 el canvas es un editor real. Duplicar copia los agents junto con su configuración "
                "guardada y las conexiones entre ellos; Deshacer también restaura la configuración de un agent. "
                "La edición se bloquea mientras un flow corre, así que nunca se cambia un flow debajo de sus propios procesos.",
            ],
            points=[
                ("Deshacer y Rehacer", "Hasta 1,024 pasos, configuración incluida."),
                ("Duplicar", "Copia la configuración y las conexiones internas."),
                ("Zoom", "De 25 a 200 por ciento, y Ajustar."),
                ("Búsqueda de agents", f"Filtra por nombre los {agents} tipos de agent."),
                ("Starters", "Ubica cada Starter en un canvas grande."),
                ("Ayuda", "Explica cada gesto; • marca los cambios sin guardar."),
            ], deck="split"),
        Section("pfp", "PROMPT FLOW PANEL", "Dibuja una conversación y luego presiona Ejecutar",
            "El Prompt Flow Panel convierte una cadena de prompts en un diagrama de ocho operaciones ejecutables más notas "
            "estáticas de revisión, guardado como un archivo `.fpmt` portátil y ejecutado contra tus modelos configurados.",
            visual="operations",
            visual_data={"ops": [
                ("prompt", "Prompt", "Envía su texto al modelo; admite Multi-Turn y ACPX."),
                ("programmed", "Prompt programado", "Espera una hora o un retraso, y luego envía."),
                ("decision", "Decisión", "Toma Sí o No de la última respuesta, o te pregunta."),
                ("feed", "Agregar embeddings", "Agrega texto de referencia a la recuperación."),
                ("flush", "Vaciar embeddings", "Limpia el contexto de recuperación."),
                ("clean", "Limpiar historial", "Limpia la conversación y el último output."),
                ("input", "Input del usuario", "Te pregunta algo; tu respuesta se une a la ejecución."),
                ("terminal", "Terminater", "Escribe comandos en una terminal visible y lee el resultado."),
                ("commentary", "Comentario del usuario", "Nota estática en burbuja para revisar; nunca se ejecuta."),
            ]}, deck="visual"),
        Section("pfprun", "PROMPT FLOW PANEL", "Una ejecución que se queda en su propio carril",
            "Validar revisa el diagrama, Ejecutar lo corre, y cada ejecución conserva su propia conversación, sus embeddings "
            "y su identidad de cancelación, así que nunca molesta a tu chat.",
            body=[
                "Escribe `{{last_output}}` para pasar la respuesta anterior hacia adelante. Las Decisiones comparan cadenas: "
                "contiene, no contiene, es igual, vacía, con distinción opcional de mayúsculas; y nunca evalúan "
                "expresiones de un archivo. Se permiten ciclos, limitados por un número máximo de operaciones "
                "ejecutadas: 500 de forma predeterminada y hasta 5,000.",
                "La figura en ejecución se ilumina y las conexiones recorridas se resaltan. Pausar deja que la operación actual "
                "termine y retiene la siguiente; Detener drena el worker en ejecución antes de que pueda empezar otra "
                "ejecución. Abrir un archivo nunca lo ejecuta, y una nota de Comentario del usuario nunca se ejecuta.",
                "Agregar embeddings requiere un vector store real. Un error del proveedor no puede volverse éxito "
                "por el fallback sólo de prompt del stack del chat, incluso con tools habilitados. El flow "
                "reporta el error antes de su siguiente operación y conserva cualquier contexto aceptado antes.",
            ],
            points=[
                ("Formato", "JSON `tlamatini-prompting-flow`, versión 2; los archivos de la versión 1 se migran."),
                ("Límites", "5 MiB, 500 elementos, 1,000 conexiones."),
                ("Aislamiento", "Historial y embeddings vacíos en cada inicio."),
                ("Validación", "Se revisa en el browser y otra vez en el servidor."),
                ("No es .pmt", "Los prompts de sistema en texto plano conservan .pmt y se rechazan."),
                ("Borradores", "Se guardan por usuario en el almacenamiento del browser."),
            ], deck="cards"),
        Section("pfpnotes", "NOTAS ESTÁTICAS DE REVISIÓN", "Escribir y dar formato a un comentario",
            "Comentario del usuario es una nota de revisión en el canvas. Input del usuario es la operación que pausa "
            "la ejecución para esperar una respuesta, con la figura de muesca.",
            body=[
                "Haz doble clic en una burbuja o presiona Enter para escribir directo en ella. Selecciona palabras o párrafos, "
                "y luego usa la mini barra de herramientas flotante para fuente, tamaño, color de texto, negritas, cursivas y subrayado. "
                "Por ejemplo, una burbuja puede tener un encabezado grande en Verdana, una oración en Arial cursiva y un "
                "párrafo en Georgia. Con sólo un cursor, el formato se aplica a lo que escribas después. Fuera de la "
                "edición, se aplica a toda la nota seleccionada. El color y la alineación de la burbuja afectan a la nota.",
                "Arrastra cualquiera de los ocho bordes o esquinas para cambiar el tamaño, incluso mientras escribes. Las manijas también "
                "aceptan las flechas del teclado. Ajustar al texto quita la altura sobrante, y la burbuja crece para contener todo "
                "el texto ajustado. No hay barras de desplazamiento internas, campos numéricos de tamaño ni diálogos de "
                "configuración del comentario.",
                "Listo o Ctrl+Enter guarda la edición completa. Cancelar o Escape restaura su texto, "
                "estilos, dimensiones y posición originales. Ctrl+Z/Y funciona dentro del editor. Las ediciones terminadas, los movimientos, "
                "los cambios de tamaño y los duplicados participan en el Deshacer/Rehacer del diagrama. Copiar entre editores "
                "de comentarios conserva el formato. El texto del portapapeles externo se queda literal.",
            ], deck="list", deck_points=[
                ("Escribe en su lugar", "Doble clic o Enter edita la burbuja. Sin diálogo de configuración ni dimensiones numéricas."),
                ("Estilos mezclados", "Barra flotante: fuente, tamaño, color de texto, negritas, cursivas y subrayado para cada pasaje."),
                ("Selección o cursor", "Da formato al texto seleccionado o a lo que escribas después; fuera de la edición, a toda la nota."),
                ("Tamaño directo", "Arrastra cualquier borde o esquina, incluso mientras escribes. Ajustar al texto quita la altura sobrante. Sin barras internas."),
                ("Terminar o restaurar", "Listo/Ctrl+Enter guarda; Cancelar/Escape restaura texto, estilos y geometría. Deshacer/Rehacer del editor y del flow."),
            ]),
        Section("pfpfiles", "ARCHIVOS DE FLOW PORTÁTILES", "Los comentarios sobreviven a guardar, abrir y recuperar el borrador",
            "Los archivos .fpmt de la versión 2 conservan notas independientes con todo su texto, formato y geometría.",
            body=[
                "Cada nota guarda fragmentos de texto de una lista permitida más el texto literal correspondiente. Los fragmentos llevan fuente, tamaño, "
                "color de texto, negritas, cursivas y subrayado. Las notas simples más viejas de la versión 2 se normalizan a un solo fragmento. "
                "El comentario ejecutable de la versión 1 se migra a Input del usuario con sus identificadores, conexiones, "
                "configuración y comportamiento de respuesta/cancelación intactos. Abrir un archivo nunca inicia la ejecución.",
                "Una nota no tiene puertos de conexión ni estado de Start, y nunca entra al contexto del modelo, al historial "
                "de la conversación ni al conteo de pasos de la ejecución. Los tokens como {{last_output}} y el texto parecido a HTML se quedan "
                "literales en un comentario. Varias notas con estilos independientes pueden compartir un diagrama.",
                "El borrador del browser por usuario conserva la llave .draft.v1 existente por compatibilidad. Los archivos "
                "portátiles conservan la extensión .fpmt. Los archivos .pmt de nombre parecido pertenecen a los prompts de sistema "
                "y siguen siendo un formato aparte. Los límites son 5 MiB por flow, 500 elementos, 1,000 conexiones, "
                "100,000 caracteres y 10,000 fragmentos con formato por nota.",
            ], deck="list", deck_points=[
                ("Versión 2", "El texto literal y los fragmentos permitidos conservan el formato mezclado."),
                ("Archivos más viejos", "Las notas v2 simples se normalizan. Los pasos de respuesta de la versión 1 se vuelven Input del usuario con IDs, conexiones y configuración intactos."),
                ("Aislamiento estático", "Sin puertos, Start ni pasos de ejecución. El texto se queda literal y nunca entra al contexto ni al historial."),
                ("Recuperación", "Las notas independientes conservan texto, estilos y geometría. Abrir nunca ejecuta el flow; la llave del borrador sigue siendo compatible."),
            ]),
        Section("flowopen", "ABRIR ARCHIVOS DE FLOW", "El editor correcto, desde el chat o desde Windows",
            "Las asociaciones de archivo incluidas abren los agent flows .flw y los prompting flows .fpmt. Abrirlos nunca los ejecuta.",
            body=[
                "El chat principal envía ambos formatos a sus propias pestañas de editor y conserva su documento actual. "
                "Abrir un archivo desde fuera valida un snapshot acotado y reutiliza un servidor en ejecución que coincida "
                "antes de cualquier trabajo de arranque de la base de datos. Un arranque en frío inicia la aplicación en su puerto configurado.",
                "El inicio de sesión regresa al archivo pedido. Los links de apertura de corta duración y de un solo uso llevan un token "
                "aleatorio en vez de un path del sistema de archivos; las cargas del browser quedan ligadas al usuario con sesión iniciada. "
                "Los formatos inválidos, las versiones no soportadas y los archivos de más de 5 MiB se rechazan antes de reemplazar.",
                "Los diagramas sin guardar y los borradores recuperados piden confirmación. Los fragmentos de comentario enriquecido conservan "
                "sus fuentes, estilos y distribución al guardar/abrir el .fpmt. Abrir un agent flow ahora espera "
                "la validación y la preparación de la sesión; si la redacción de credenciales no funciona, se bloquean las descargas .flw inseguras.",
            ],
            points=[
                ("Desde el chat", "Abre cualquiera de los dos flows en su editor y conserva el documento del chat."),
                ("Desde Windows", "Arranca una vez o reutiliza la app en ejecución; regresa por el inicio de sesión."),
                ("Conservar el trabajo", "Valida antes de reemplazar; confirma los cambios sin guardar."),
                ("Sin ejecución automática", "Abrir prepara el diagrama. Ejecutar sigue siendo una acción del usuario."),
            ], deck="cards"),
        Section("flowwindows", "TIPOS DE ARCHIVO DE WINDOWS", "Registra, repara y quita ambos formatos",
            "Asociaciones por usuario, dueño de la instalación y elecciones de apps predeterminadas de Windows.",
            body=[
                "Un helper compartido de PowerShell registra .flw y .fpmt con ProgIDs separados, nombres amigables, "
                "íconos, entradas de Abrir con y capacidades de Apps predeterminadas. Status reporta el registro actual; "
                "DefaultApps abre la Configuración de Windows para que el usuario elija una app predeterminada.",
                "La instalación registra ambos formatos. Update Repair respeta la desinscripción explícita y nunca "
                "toma la entrada propia de otra instalación. La eliminación borra sólo los valores de esta instalación, "
                "y conserva el UserChoice de Windows y las entradas de Abrir con de otras aplicaciones. Los wrappers históricos de .flw "
                "cubren ambos formatos, así que los binarios existentes del instalador/desinstalador siguen siendo compatibles.",
                "Los scripts y los módulos de apertura se incluyen en el empaquetado congelado y en el de self-modify. Las revisiones "
                "nativas del registro usan una llave de prueba aislada, y las pruebas visibles en Chrome ejercitan la apertura real de archivos "
                "y el inicio de sesión. La campaña de release del 4 de octubre también recompiló los ejecutables locales principal y desinstalador. "
                "El trabajo se hizo commit a main ese día y lo lleva el tag v1.76.0; la aceptación compilada se "
                "registra aparte de las pruebas del source. "
                "Consulta docs/windows-flow-files.md para los comandos, los contratos y la verificación.",
            ],
            points=[
                ("Instalar", "Registra ambos tipos con nombres, íconos y los destinos de editor correctos."),
                ("Administrar", "Revisa Status, registra o quita un tipo, o abre Apps predeterminadas."),
                ("Actualizar", "Repara las entradas propias sin deshacer la exclusión del usuario."),
                ("Desinstalar", "Quita los registros propios; conserva otras apps y los documentos del usuario."),
            ], deck="cards"),
        Section("uninstallworkers", "CICLO DE VIDA EN WINDOWS", "Quita la aplicación y sus workers propios",
            "Confirmación, dueño de la instalación, errores que se pueden reintentar y contenido del usuario conservado.",
            body=[
                "El error real de registro del instalador vino de un InstallDir omitido cuyo valor predeterminado de parámetro "
                "se evaluaba antes de que Windows PowerShell llenara PSScriptRoot. Ahora los wrappers "
                "resuelven ese valor predeterminado dentro del script. Las pruebas nuevas con powershell.exe -File ejercitan el "
                "mismo punto de entrada desde un directorio de trabajo no relacionado.",
                "Primero, el desinstalador exige que la aplicación principal se cierre. Después de la confirmación, detiene "
                "los workers que pertenecen a la instalación elegida y a sus descendientes. Los límites exactos de path, "
                "las horas de creación y el TLAMATINI_AGENTS_ROOT heredado identifican a los hijos de los agents incluso después de "
                "cambiar de padre; los procesos no relacionados y Explorer siguen corriendo.",
                "Una copia temporal independiente permite quitar el propio desinstalador instalado. "
                "Los helpers y el marcador de la instalación se quedan hasta que la eliminación de archivos y del registro propio tiene éxito, "
                "así que una falla parcial se puede reintentar. Los archivos bloqueados y el borrado denegado del registro reportan error. "
                "Se rechazan las raíces de unidad, las carpetas compartidas, los checkouts del source y los destinos redirigidos.",
                "Desde v1.76.0, cuando Windows todavía tiene tomado el propio Uninstaller.exe, el archivo se reintenta, se mueve aparte "
                "y lo quita una limpieza oculta después de que el desinstalador sale, así que la desinstalación termina limpia.",
                "Los agents y los directorios de contenido del usuario que no están vacíos se quedan bajo el contrato de conservación existente. "
                "Un reinicio completo de directorio/registro es una acción autorizada aparte. La verificación distingue "
                "los resultados reales de la GUI compilada de las pruebas del backend y registra explícitamente cualquier arranque nativo bloqueado.",
            ], deck="cards", points=[
                ("Puntos de entrada del instalador", "Resuelven el directorio de instalación dentro del cuerpo de los scripts de PowerShell."),
                ("Workers propios", "Detiene los agents de esta instalación y los descendientes que sobrevivan, después de la confirmación."),
                ("Reintento honesto", "Conserva el soporte de eliminación hasta tener éxito; reporta archivos bloqueados y errores del registro."),
                ("Conservar el trabajo del usuario", "Conserva los agents y el contenido no vacío; avisa al shell sin reiniciar Explorer."),
            ]),
        Section("setupwizard", "VENTANAS DE INSTALACIÓN · v1.82.0", "Instala y quita con una forma de regresar",
            "El Instalador y el Desinstalador comparten una ventana que prepara una copia de recuperación antes de cambiar cualquier cosa.",
            body=[
                "Ambos ejecutables usan una sola ventana de instalación: la paleta de Tlamatini, controles de teclado, una página de destino "
                "y de revisión, progreso real y detalles del resultado que se quedan en pantalla. La fila de acciones es su "
                "propia fila de la ventana, así que los botones nunca se recortan, y las fuentes grandes o los paths largos desplazan el cuerpo. "
                "Los errores se quedan en la ventana con Reintentar y Cambiar carpeta, y cada ejecución escribe un log privado "
                "en %LOCALAPPDATA%\\Tlamatini\\SetupLogs.",
                "Antes de que la instalación o la eliminación cambie un archivo, se prepara y verifica una copia de recuperación; su "
                "journal vive en la carpeta Temp de la instalación, y la siguiente ejecución restaura primero una "
                "transacción interrumpida. Una restauración con error se reporta, nunca se presenta como rollback. Un archivo "
                "bloqueado recibe cinco segundos de reintento y luego se nombra junto con el programa que lo tiene, que nunca "
                "se cierra por ti. Sólo se toma snapshot de los valores de registro propios de Tlamatini y de su acceso directo en el Escritorio.",
                "Son mecanismos de recuperación propios de un EXE, no transacciones MSI. En la campaña visible del 11-12 de octubre "
                "pasaron 52 puntos de revisión de la interfaz, 28 revisiones de recuperación, 21 revisiones de ciclo de vida y 61 pruebas "
                "de mecánica; cinco instalaciones reales y cuatro eliminaciones reales pasaron sus auditorías independientes. "
                "La quinta eliminación se detuvo de forma segura antes de borrar nada, porque un browser de prueba tenía tomado un archivo "
                "en la carpeta Temp de la instalación.",
            ], deck="cards", points=[
                ("Una ventana", "Pantallas compartidas del Instalador y el Desinstalador que nunca recortan sus botones."),
                ("Copia de recuperación", "Preparada y verificada antes de cambiar cualquier archivo; restaurada después de una interrupción."),
                ("Bloqueos con nombre", "Se nombra un archivo bloqueado y a quien lo tiene; nada se cierra a la fuerza."),
                ("Alcance propio", "Sólo los valores de registro y el acceso directo de Tlamatini; nunca UserChoice."),
                ("Helpers acotados", "Los helpers de PowerShell terminan en 120 segundos dentro de un job de Windows."),
                ("Conteo honesto", "Pasaron cinco instalaciones y cuatro eliminaciones; una se detuvo de forma segura."),
            ]),
        Section("release_repair", "VALIDACIÓN LOCAL DEL RELEASE", "Repara la frontera y luego repite la operación real",
            "Las reparaciones del 4 de octubre, que ahora lleva v1.76.0, tienen evidencia aparte del source, del congelado, del paquete y visual"
            ".",
            body=[
                "La campaña visible revisa el instalador real, las asociaciones de Windows, la apertura autenticada "
                "de archivos, la administración, el chat principal y ambos paneles de flows. También compara varios "
                "comentarios enriquecidos a lo largo de escrituras y lecturas repetidas de archivos, ejecuta agents locales y audita "
                "los workers propios después del apagado. Que se abra un diálogo de configuración no prueba que un "
                "agent de hardware o de servicio externo se haya ejecutado con éxito.",
                "System-Metrics y Files-Search ahora respetan la configuración efectiva y los puertos "
                "no predeterminados, incluidos los archivos UTF-8 con BOM. Los lectores de seguridad de paths y de la cadena del chat aceptan la misma "
                "codificación sin debilitar los límites de directorio. Las dos cadenas de contexto auxiliares usan los mismos "
                "paths y endpoints efectivos; los sockets del sistema se cierran después de cada solicitud y los RPC de archivos tienen plazos. "
                "Parametrizer restaura las conexiones cuando un archivo guardado "
                "contiene mapeos sin listas explícitas de conexiones. Los agents sin modelo evitan lecturas no relacionadas "
                "de la configuración de modelos. Los identificadores numéricos de mensajería conservan el mismo contrato "
                "de cadena/entero en las plantillas públicas y con llaves.",
                "Una solicitud de embedding rechazada debe hacer que el flow falle antes de su siguiente operación. El proveedor "
                "de la campaña devolvió HTTP 401; esto se registra como una capacidad bloqueada con un camino de error "
                "probado. El tool de control del escritorio también bloqueó el arranque del desinstalador compilado. Las pruebas de "
                "limpieza del backend no certifican sus pantallas nativas de confirmación y de término, que no se observaron.",
                "Los resultados detallados y los intentos con error que se conservaron están en "
                "docs/changes/2026-10-04-release-validation.md. El perfil de revisión que pidió Angela "
                "lista cada archivo cambiado y cada segmento de código. El trabajo se hizo commit el 4 de octubre y lo lleva "
                "el tag v1.76.0.",
            ], deck="cards", points=[
                ("Caminos reales del usuario", "Instalador, inicio de sesión, Admin, chat, ambos paneles y apertura de archivos en Windows."),
                ("Fidelidad de archivos", "Estilos mezclados, geometría y texto renderizado revisados en ciclos de guardar/abrir."),
                ("Fronteras del runtime", "Endpoints de MCP configurados, valores predeterminados de agents, mapeos y tipos de identificadores."),
                ("Límites explícitos", "El error del proveedor y el arranque nativo bloqueado se quedan visibles en el veredicto."),
            ]),
        Section("pfpoutput", "OUTPUT DE LA EJECUCIÓN", "Más espacio para el canvas o para el log",
            "Arrastra el divisor horizontal sobre Output de la ejecución para darle del 5% al 95% de la altura disponible del panel.",
            body=[
                "El porcentaje usa la altura combinada del canvas y del output, sin contar encabezados, la franja "
                "de status ni el divisor. La asignación inicial es 20%. El canvas y el Output de la ejecución conservan cada uno "
                "su propia barra de desplazamiento. Mover el divisor conserva el zoom del canvas, las dimensiones de los nodos y el tamaño "
                "del texto. La Barra de operaciones conserva su control aparte de tamaño horizontal.",
                "Llega al divisor con Tab y usa Arriba/Abajo para un punto porcentual, o Shift+Arriba/Abajo para cinco. "
                "Inicio elige 5% y Fin elige 95%. Escape termina un arrastre. Haz clic en el encabezado de Output de la ejecución para "
                "colapsarlo. Al volver a abrirlo se restaura la altura elegida, y cambiar el tamaño de la ventana conserva la proporción.",
                "El browser recuerda la altura del output por usuario con sesión iniciada. Esta preferencia de distribución no "
                "modifica un archivo de flow, no marca el diagrama como editado ni agrega un paso de Deshacer. Cambiar el tamaño del panel "
                "también deja sin cambio la ejecución y su output.",
            ], deck="list", deck_points=[
                ("Del 5% al 95%", "Parte de la altura del canvas/output, sin encabezados, status ni divisor. Parte inicial: 20%."),
                ("Contenido estable", "Desplazamiento independiente. El zoom del canvas y los tamaños de texto no cambian."),
                ("Teclado", "Arriba/Abajo: 1 punto; Shift: 5. Inicio: 5%; Fin: 95%. Escape termina el arrastre."),
                ("Distribución recordada", "Colapsar/reabrir y cambiar el tamaño de la ventana conservan la proporción. Se guarda por usuario, fuera de los archivos de flow y de Deshacer/Rehacer."),
            ]),
        Section("catalog", "CATÁLOGO DE PROMPTS", "Prompts listos para usar, agrupados por propósito",
            f"El Catálogo de prompts se abre con {sections_count} secciones; cada una empieza con un asistente guiado "
            f"Paso a paso y crece de lo simple a lo avanzado.",
            body=[
                f"Secciones: {catalog_names}. VOICE COMMANDS va primero, porque hablar es la forma más corta "
                f"de usarla: tú hablas, Whisperer transcribe y la transcripción se vuelve el prompt. "
                "Estos workflows del catálogo usan el tool wrapped mediado por el modelo y los modos propios de cada tarjeta; "
                "son distintos del botón directo de micrófono junto a Enviar.",
                "Las insignias de modo de cada tarjeta se derivan del texto mismo del prompt, y hacer clic en una tarjeta pone "
                "los interruptores de la barra de herramientas exactamente en esos modos. Todos los prompts usan una sola gramática, así que siempre "
                "queda claro de quién es cada espacio en blanco.",
            ],
            table={"columns": ["Marca", "Lo llena", "Significado"], "widths": [0.18, 0.22, 0.60], "rows": [
                ["[[ … ]]", "Tú", "Un valor que tú das, reunido arriba con un valor predeterminado seguro."],
                ["{{ … }}", "Tlamatini", "Un valor que ella llena al momento de ejecutar."],
                ["< … >", "Espacio del reporte", "Donde se imprime una respuesta; nunca es un input."],
            ]}, deck="split",
            deck_points=[
                ("Secciones", f"{sections_count}, empezando con VOICE COMMANDS."),
                ("Aperturas", "Cada sección empieza con un asistente guiado Paso a paso."),
                ("Insignias", "Derivadas del texto del prompt; un clic pone los modos."),
                ("Gramática", "[[ tú ]], {{ runtime }}, < espacio del reporte >."),
            ]),
        Section("pdfcanvas", "CANVAS DE PDF", "Lee un PDF y luego dale el documento completo",
            "Abre un PDF junto al chat en un visor Mozilla PDF.js incluido, y luego úsalo como contexto.",
            body=[
                "Leer no sube nada ni llama a ningún modelo: el visor lee rangos de bytes directo de tu "
                "disco, así que del lado de Tlamatini no hay límite de tamaño ni de páginas. La selección de texto, la navegación, el zoom, "
                "el ajuste, la rotación y las contraseñas dentro del visor se comportan como esperas; Copiar toma el texto de todas las páginas "
                "y Guardar como devuelve los bytes originales.",
                "**Usar como contexto** hace primero una pregunta: ¿Procesar imágenes? Empieza sin marcar cada vez, y "
                "nada corre hasta que presionas Continuar. Sin marcar, ella lee sólo el texto seleccionable. Marcada, ella "
                "también renderiza cada página y analiza cada imagen incrustada con Image-Interpreter. El progreso es "
                "honesto, Cancelar de verdad cancela, y los errores parciales de imágenes se reportan, no se esconden. Una "
                "contraseña de PDF se usa sólo en memoria: nunca se escribe a disco, al texto del contexto ni al log.",
                "Una segunda cuenta que inicia sesión desde el mismo browser toma todas las pestañas abiertas, mientras que un chat abierto "
                "conserva su primera cuenta, así que la carga se rechaza. Desde v1.76.0 el mensaje nombra esa causa y "
                "el arreglo, recargar con F5; el encabezado regresa y el diálogo de progreso marca el paso con error.",
            ], deck="list",
            deck_points=[
                ("Lectura privada", "Rangos de bytes de tu disco; no se sube nada ni se llama a ningún modelo."),
                ("Visor", "Mozilla PDF.js 6.3.289, incluido bajo Apache-2.0; sin CDN."),
                ("Usar como contexto", "Sólo texto de forma predeterminada; imágenes sólo cuando marcas la casilla."),
                ("Progreso honesto", "Cuatro filas de progreso, un Cancelar real, errores reportados."),
                ("Contraseñas", "Se usan sólo en memoria; nunca se guardan ni van al log."),
            ]),
        Section("mdcanvas", "CANVAS DE MARKDOWN", "El Markdown se abre como página y sigue siendo tu source",
            "Abre o suelta un archivo .md y el canvas lo renderiza; Source abre el documento editable.",
            body=[
                "Abrir, Actualizar, un archivo soltado, un link a un archivo generado y Contexto ▸ Usar archivo como contexto "
                "reconocen .md y .markdown. La vista previa renderiza CommonMark y Markdown al estilo GitHub: "
                "encabezados, tablas, listas de tareas, código cercado con el resaltador existente y HTML incrustado "
                "seguro, como los detalles desplegables. Source edita el texto actual con números de línea.",
                "El renderizado es local: Marked 18.1.0 y DOMPurify 3.4.16 van incluidos con integridad fija, "
                "así que nada se trae de un CDN. El sanitizador usa listas permitidas de HTML y atributos, delimita los ids y "
                "restringe los protocolos de recursos. Elegir carpeta resuelve las imágenes y los links relativos desde archivos que "
                "seleccionas; se quedan en tu equipo, y una URL relativa nunca llega a un endpoint de la aplicación.",
                "Copiar, Usar como contexto y Guardar siempre toman el source en Markdown, nunca la vista previa aplanada; "
                "guardar sin editar conserva los bytes originales; las ediciones conservan la codificación/BOM y los saltos de línea. La vista previa salió en v1.82.0 y se revisó "
                "el 11 de octubre con 30 de 30 puntos de revisión visibles en el browser.",
            ], deck="list",
            deck_points=[
                ("Vista previa y Source", "Página renderizada, o source editable con números de línea."),
                ("Sin conexión", "Marked y DOMPurify incluidos; sin CDN al ejecutar."),
                ("HTML seguro", "Marcado de una lista permitida; los links relativos nunca llegan a la app."),
                ("Tu source", "Copiar, contexto y Guardar usan el buffer actual del source."),
                ("Evidencia", "30 de 30 puntos de revisión visibles el 11 de octubre."),
            ]),
        Section("filedrop", "SOLTAR ARCHIVOS · v1.83.0", "Suelta un archivo en cualquier lugar, y ella sabe qué es",
            "Un solo listener en cada página lee cada archivo soltado y lo envía al mecanismo que le corresponde.",
            body=[
                "Arrastra un archivo desde el Explorador de Windows al chat, al Agentic Control Panel, al Prompt Flow Panel, "
                "a las páginas de bienvenida y de inicio de sesión, a las páginas de admin o al visor de PDF. Un pequeño overlay dice qué va a "
                "pasar en esa página. El listener sólo toma arrastres de archivos, así que el texto que arrastras, como el nombre de un "
                "agent o un elemento de la paleta, nunca se toca, y lo que sueltas sobre un input de archivo se le deja al browser.",
                "Decide por los bytes, no por el nombre: la extensión, el tipo MIME, los números mágicos, una prueba de texto o binario "
                "que reconoce la marca de orden de bytes y un parseo real de JSON que reconoce una configuración de MCP en todas las formas "
                "comunes, incluidos los archivos UTF-16 de PowerShell. Un mapa simple de nombres a servidores cuenta sólo cuando todos "
                "los valores son servidores, así que el JSON común nunca se secuestra. Una importación de MCP nunca es silenciosa: una confirmación "
                "lista los servidores y avisa que pueden arrancar programas en esta computadora.",
                "Cada página le dice al listener qué puede hacer, y el mismo registro escribe el overlay de arrastre. Hasta "
                "25 archivos a la vez; no se puede soltar una carpeta porque los browsers no revelan su path. Salió en "
                "v1.83.0 y se revisó el 14 de octubre con 138 revisiones del router, 22 pruebas nuevas y 58 revisiones visibles en el browser.",
            ],
            table={"columns": ["Sueltas", "Qué pasa"], "widths": [0.30, 0.70], "rows": [
                ["Un .json de MCP", "Confirma, y luego se une al catálogo de External MCPs; funciona en todas las páginas."],
                ["Un flow .flw", "Se carga en el canvas del Agentic Control Panel, o abre ese panel en una pestaña nueva."],
                ["Un flow .fpmt", "Se carga en el Prompt Flow Panel, preguntando primero por el trabajo sin guardar, o en una pestaña nueva."],
                ["Una imagen", "Se adjunta a tu mensaje: se guarda en Temp y su path se escribe en el mensaje."],
                ["PDF, Markdown, código, JSON simple", "Se abre en el canvas del chat."],
                ["Una carpeta, un zip o un programa", "Se explica con palabras sencillas; no se abre nada."],
            ]}, deck="table"),
        Section("models", "CONFIG ▸ MODELOS", "Todas las elecciones de modelo en un solo lugar",
            f"El diálogo Modelos expone {model_fields} configuraciones de modelo, motor y voz para los servicios principales "
            f"y {model_agents} agents con modelo, en seis categorías con búsqueda.",
            body=[
                f"Categorías: {groups_text}. Guardar envía todos los valores, conserva la configuración no relacionada y "
                "no descarga nada. Reconecta el chat para reconstruir sus clientes; los agents toman una elección en su "
                "siguiente carga de configuración. La lista de modelos viene de los servidores de Ollama configurados, consultados por "
                "el backend con su token, así que se ofrecen y se aceptan los modelos de un servidor remoto. Desde v1.76.0 "
                "Guardar también abre el diálogo de Autoajuste del Model Brain, que ajusta cada modelo configurado frente "
                "a ti y nombra la fuente de cada valor.",
                "Las plantillas de agents marcadas `\"@config\"` siguen la elección global, mientras que un valor literal en un "
                "workflow sigue siendo un override explícito. Los arranques de chat wrapped siembran las elecciones globales antes de "
                "cualquier argumento explícito del tool, y el build congelado prueba que cada cargador de modelos corre antes de "
                "empaquetar.",
            ],
            visual="bars_models", deck="split",
            deck_points=[
                ("Configuraciones", f"{model_fields} elecciones de modelo, motor y voz."),
                ("Agents", f"{model_agents} agents con modelo, configurados de forma central."),
                ("Herencia", "\"@config\" sigue la elección global; los literales la reemplazan."),
                ("Guardar", "Conserva la configuración no relacionada, no descarga nada y luego autoajusta cada modelo."),
                ("Catálogo", "Lo listan los servidores de Ollama configurados, consultados con su token."),
            ]),
        Section("onelook", "UN SOLO ASPECTO · v1.80.0", "Todas las páginas comparten un tema y una forma de cambiar el tamaño",
            "El chat, ambos paneles, el inicio de sesión, la bienvenida, Uso, el visor de PDF y las páginas de admin comparten una identidad.",
            body=[
                "Un solo juego de design tokens define las superficies de pizarra, el acento verde azulado, el texto legible, los bordes, "
                "las fuentes y las barras de desplazamiento de cada página propia, incluido un admin de Django con tema que conserva "
                "sus modos claro, oscuro y automático. Los colores de los diálogos siguen los mismos tokens, y el tema de los diálogos "
                "siempre se carga al final.",
                "Los cinco divisores de paneles comparten una manija y un modelo de gestos: captura del puntero, flechas para un "
                "por ciento, Shift para cinco, Inicio y Fin, y una cancelación limpia con Escape, al perder el foco o al perder el "
                "puntero. Los diálogos que cambian de tamaño aceptan los ocho bordes y esquinas y el teclado, y un modal "
                "ya no se puede deslizar debajo del menú expandido con zoom de 400 por ciento.",
            ], deck="cards", points=[
                ("Tokens compartidos", "Una paleta, un juego de fuentes y un estilo de barra de desplazamiento para todas las páginas."),
                ("Cinco divisores", "Una manija, un modelo de teclado, una cancelación limpia."),
                ("Diálogos", "Ocho direcciones de cambio de tamaño, cambio de tamaño con teclado, botones que combinan."),
                ("Zoom alto", "Un modal se queda arriba del menú al 400 por ciento."),
                ("Evidencia", "175 pruebas del source y revisiones visibles pasaron el 11 de octubre."),
            ]),
        Section("dialogs", "DIÁLOGOS DEL OPERADOR", "Todo lo demás, sin editar archivos",
            "La configuración, las credenciales, las bases de datos y las actualizaciones se manejan desde el browser.",
            points=[
                ("Access Keys Wizard", "Un lugar guiado para las llaves de los proveedores; los campos en blanco conservan lo que ya está."),
                ("Contactos", "Los nombres se resuelven a direcciones, teléfonos y @usernames para los agents de mensajería."),
                ("Menú DB", "Backup seguro con WAL, y una base de datos verificada preparada para el siguiente arranque."),
                ("Externos ▸ MCPs", "Busca en el catálogo, activa hasta cinco servidores, instala runtimes."),
                ("ACPX-Skills", "Examina, habilita, diagnostica y recarga skills."),
                ("Buscar actualizaciones", "Prepara el último release publicado y lo cambia de forma segura."),
            ],
            callout=("Una sola regla para cerrar en todas partes",
                     "Escape significa exactamente lo mismo que la ✕ de un diálogo, y un clic afuera nunca cierra "
                     "nada. Un actualizador que está descargando es el único diálogo que se niega a cerrarse."),
            deck="cards"),
    ])

    bestiary_sections = []
    for name, accent, blurb, members in AGENT_FAMILIES:
        bestiary_sections.append(Section(
            "family_" + name.lower().replace(" ", "_").replace(",", ""), "FAMILIA DE AGENTS",
            name, blurb,
            points=[(f["display_names"][key], text) for key, text in members],
            visual_data={"accent": accent, "count": len(members)}, deck="family"))
    bestiary = Chapter("bestiary", "IV", "El Bestiario",
        f"{agents} tipos de agent en doce familias. Cada uno es un programa en Python simple que puedes leer, auditar y cambiar.",
        accent="magenta", sections=[
            Section("bestiary_intro", "LOS AGENTS", f"{agents} agents, doce familias",
                "Cada agent sigue un mismo esqueleto: un directorio de plantilla, un `config.yaml`, una copia en el pool "
                "con alcance de sesión, archivos PID y de log, y conexiones explícitas de origen y de destino.",
                body=[
                    f"{wrapped} de ellos también corren desde el chat como tools wrapped `chat_agent_*`, cada uno en su propia "
                    "carpeta de runtime aislada. Cada agent wrapped aparece automáticamente en el Exec Report, y "
                    "cada uno incluye al menos un prompt de ejemplo en el catálogo.",
                    "Los nombres para mostrar conservan su uso exacto de mayúsculas tal como se diseñó: STM32er, PDFer, LaTeXer, ACPXer; mientras que "
                    "los directorios, los pools y las clases de estilo usan formas en minúsculas.",
                ],
                visual="family_wheel", deck="visual"),
            *bestiary_sections,
        ])

    capabilities = Chapter("capabilities", "V", "Capacidades profundas",
        "Los subsistemas que le dan alcance: otros agents, otros servidores, documentos, tarjetas, motores y sentidos.",
        accent="cyan", sections=[
        Section("acpx", "ACPX", "Otros agents de programación como sus hijos",
            "ACPX arranca CLIs externos de agents de programación como hijos fuera del proceso, habla con ellos por "
            "stdin y stdout, guarda una transcripción NDJSON de cada turno, y lo pone todo a disposición del modelo como "
            "doce tools.",
            body=[
                f"Hay {len(peers)} pares registrados: {', '.join(peers)}. Los pares de una sola ejecución reciben el prompt como "
                "argumento de la línea de comandos y se leen hasta el final; el self-host de Tlamatini habla JSON estricto; "
                "los pares interactivos se drenan con una regla de inactividad que conoce el transporte. ACPX es un port en Python del "
                "plugin ACPX de OpenClaw, así que sus identificadores de agents y su contrato de skills son compatibles.",
                "ACPX dice la verdad sobre sus pares. Una revisión de versión no es salud, y el código de salida 0 no es "
                "éxito: un clasificador que sólo usa la stdlib decide si un hijo de verdad entregó, y una negativa se "
                "devuelve como `ok: false` con un código con nombre en vez de una fila verde. `acp_doctor(deep=True)` envía "
                "un prompt real de una línea a cada par y nombra lo que está roto.",
                "Los hijos nunca se arrancan por el shell, porque cmd.exe corta en silencio una línea de comandos en "
                "su primer salto de línea. Los shims de npm y pnpm se reescriben a `node.exe` con el path del script.",
            ],
            table={"columns": ["Código de no entrega", "Significado"], "widths": [0.42, 0.58], "rows": [
                ["PERMISSION_BLOCKED", "El hijo se detuvo en su propio aviso de permisos."],
                ["AUTH_FAILED · CONFIG_INVALID", "No pudo autenticarse, o rechazó su propia configuración."],
                ["NO_CREDIT · USAGE_LIMIT", "Sin crédito, o se alcanzó un límite del plan o de tasa."],
                ["UPSTREAM_ERROR", "El proveedor del modelo devolvió un error del lado del servidor."],
                ["NO_OUTPUT · CHILD_ERROR", "No regresó nada legible, o tuvo un error sin dar respuesta."],
                ["WORKSPACE_NOT_TRUSTED", "Su carpeta de trabajo no es de confianza, así que se ignoraron los permisos."],
            ]}, deck="split",
            deck_points=[
                ("Pares", f"{len(peers)} CLIs, incluidos Claude Code, Codex, Gemini, Cursor y Qwen."),
                ("Doce tools", "Arrancar, enviar, esperar, relevar, transcripción, status, matar, doctor, skills."),
                ("Veraz", "Una negativa devuelve ok: false con un código con nombre."),
                ("Sin shell", "Los shims se reescriben para que los prompts largos nunca se corten."),
            ]),
        Section("mcps", "EXTERNAL MCPS", "Un cliente MCP universal",
            "Conecta Tlamatini a cualquier servidor MCP declarado en un catálogo JSON y usa sus tools de inmediato, sin "
            "escribir código para el servidor.",
            body=[
                "El catálogo usa la forma estándar `mcpServers` y vive junto a `config.json`, conservado "
                "entre actualizaciones. Se conectan cuatro transportes (stdio, HTTP streamable, SSE y WebSocket) de forma diferida "
                "en un hilo de fondo, así que un servidor lento nunca puede retrasar una respuesta. Hasta cinco servidores están "
                "activos a la vez, y cada tool remoto aparece como `ext__<server>__<tool>`.",
                "La mayoría de los servidores arrancan con `npx` o `uvx`, que una máquina recién instalada no tiene. Un aprovisionador privado "
                "de runtimes descarga Node y uv una sola vez desde sus fuentes oficiales al perfil del usuario, "
                "verifica checksums, instala de forma atómica, no necesita derechos de administrador y nunca cambia el "
                "PATH del sistema.",
                "Memory y Sequential Thinking vienen en cada instalación, inactivos. Un servidor predeterminado que borras se "
                "recuerda y nunca se revive; uno que editas nunca se sobrescribe.",
            ],
            visual="chain",
            visual_data={"chain": ["Clasificar", "Importar", "Diagnosticar", "Activar", "Esperar", "Listar", "Llamar"],
                         "caption": "La skill adding-external-mcp: una secuencia de incorporación protegida."},
            deck="split",
            deck_points=[
                ("Transportes", "stdio, HTTP streamable, SSE y WebSocket."),
                ("Diez supervisores", "Status, reconectar, doctor, runtimes, importar, listar, llamar, activar, esperar."),
                ("Runtimes privados", "Node y uv aprovisionados por usuario, sin admin, sin cambiar el PATH."),
                ("Predeterminados", "Memory y Sequential Thinking, inactivos hasta que tú elijas."),
            ]),
        Section("skills", "SKILLS", "Procedimientos, entregados completos",
            f"{skills} paquetes `SKILL.md` se cargan al arrancar y se le ofrecen al modelo por medio de "
            "`list_skills` e `invoke_skill`.",
            body=[
                "Invocar una skill en proceso es una entrega de planeación, no una ejecución escondida. Devuelve el "
                "procedimiento completo, el contrato de outputs que todavía se deben y una declaración honesta de lo que se "
                "hace cumplir (revisión de argumentos, redacción de secretos y presupuestos de tiempo) y de lo que queda como política "
                "declarada, protegida por las superficies normales de Configurar y de Ask Execs.",
                "Las skills incluyen revisión de código, auditoría de seguridad, el runbook de pentest con Kali, creación de flows, creación "
                "de skills, resumen, el runbook adding-external-mcp, Roblox Studio, auditoría del repositorio y "
                "helpers de refactorización, y guías de integración para GitHub, Gmail, Slack, Jira, Notion, Todoist, "
                "Trello y el clima. El menú ACPX-Skills las habilita, las diagnostica y las recarga sin reiniciar.",
            ],
            callout=("Las credenciales se quedan adentro",
                     "Un input marcado como sensible, o con nombre de credencial, se redacta de todos los eventos "
                     "de auditoría y del resultado devuelto: sin prefijo, sin longitud, sin hash."),
            deck="list",
            deck_points=[
                ("Catálogo", f"{skills} paquetes, validados por una sola rutina compartida."),
                ("Entrega", "invoke_skill devuelve el procedimiento completo y los outputs que todavía se deben."),
                ("Cumplimiento honesto", "Dice qué se hace cumplir y qué es política declarada."),
                ("Administradas", "Examinar, Configurar, Diagnósticos y Recargar desde el menú."),
            ]),
        Section("documents", "LA FAMILIA DE DOCUMENTOS", "Componer, presentar, tipografiar",
            "Tres agents producen documentos, cada uno con su propio oficio, y ninguno da por limpio un archivo "
            "sólo porque se creó.",
            table={"columns": ["Agent", "Oficio", "Funciones distintivas"], "widths": [0.14, 0.24, 0.62], "rows": [
                ["PDFer", "Compone PDFs a partir de texto, Markdown, HTML e imágenes",
                 "24 estilos visuales en cinco familias sobre 20 temas de contenido; tablas y portadas medidas; una "
                 "auditoría de distribución que vuelve a abrir el archivo y revisa encimados, texto fuera de la página, páginas en blanco y "
                 "contraste."],
                ["PPTXer", "Construye presentaciones editables de PowerPoint",
                 "36 tratamientos con nombre y 17 combinaciones de fuentes; el texto se mide antes de colocarlo, así que el contenido "
                 "largo continúa en una diapositiva nueva; verificación nativa en PowerPoint cuando está instalado."],
                ["LaTeXer", "Tipografía LaTeX real",
                 "Ocho plantillas y 30 estilos distintivos; builds de proyectos completos con convergencia de bibliografía e "
                 "índice; diagnósticos legibles; una escalera de reparación de ocho peldaños; un build mayormente recortado se entrega como "
                 "`<name>.DEGRADED.pdf`; se recomienda MiKTeX."],
            ]},
            callout=("Creado no es verificado",
                     "Un archivo guardado sólo prueba que existe. Lee, de PDFer, `layout_clean`; de PPTXer, "
                     "`ground_truth`; o de LaTeXer, `status`, antes de dar un documento por limpio."),
            deck="table"),
        Section("ladder", "LATEXER", "Una escalera de reparación que protege tus palabras",
            "Cuando un build falla, LaTeXer sube ocho peldaños en un orden fijo; cada uno se intenta sólo si el "
            "anterior no produjo un PDF.",
            body=[
                "Cada reparación se aplica a una copia y se vuelve a revisar con lint; una reparación que empeora el lint se revierte. "
                "El archivo del autor nunca se sobrescribe a menos que se active `repair_write_back`, cada peldaño se registra "
                "en una traza de auditoría, y cualquier bloque que se aparta se nombra con su número de línea.",
                "Bisect va estrictamente al final porque es el único peldaño que quita contenido, y se salta cuando "
                "el peldaño del modelo sólo no se pudo alcanzar. Un build limpio le dice al modelo claramente que el "
                "documento está terminado, así que un buen PDF nunca se “mejora” hasta romperlo.",
                "Desde v1.76.0 un PDF se reporta sólo cuando el archivo entregado de verdad existe. Un build que tuvo que "
                "cortar una cuarta parte o más de su cuerpo se entrega como `<name>.DEGRADED.pdf`, nunca con el nombre que "
                "pediste, y en un documento de más de 8,000 caracteres el peldaño del modelo primero repara sólo las líneas "
                "alrededor del error del compilador con una solicitud acotada; una respuesta que nunca llegó prohíbe el bisect.",
            ],
            visual="ladder",
            visual_data={"rungs": [
                ("1", "lint", "Reparación estructural estática antes de que corra cualquier compilador."),
                ("2", "preamble", "Deduce los paquetes a partir de los comandos que de verdad se usan."),
                ("3", "rules", "Reescrituras deterministas de construcciones que se sabe que están mal."),
                ("4", "log-directed", "Compila, lee el error real y arregla esa línea."),
                ("5", "acquire", "Instala un paquete que de verdad falta."),
                ("6", "engine swap", "Reintenta con XeLaTeX o LuaLaTeX."),
                ("7", "model", "Pregunta a un modelo; su respuesta vuelve a entrar en el peldaño 1."),
                ("8", "bisect", "Al final: aparta el bloque con error, y lo dice."),
            ]}, deck="visual"),
        Section("firmware", "FIRMWARE", "Tarjetas reales, a prueba de errores por diseño",
            "Cuatro agents llevan el firmware desde el andamiaje hasta una tarjeta funcionando, y cada uno se niega antes que flashear "
            "algo que no puede estar bien.",
            table={"columns": ["Agent", "Toolchain", "Lo más destacado"], "widths": [0.14, 0.26, 0.60], "rows": [
                ["STM32er", "PlatformIO ststm32 y el STM32 Template Project MCP",
                 "De la Blue Pill a F7, G, L, H7, U5 y WB; bootstrap sin configuración; revisiones de la sonda ST-LINK; "
                 "el silicio más nuevo se rechaza limpiamente hasta que exista su backend nativo."],
                ["ESP32er", "PlatformIO Core, llamado directamente",
                 "Copia una plantilla de parpadeo e impresión para que un proyecto nuevo compile de inmediato; preflight que conoce el puerto serial."],
                ["Arduiner", "arduino-cli, descargado cuando se necesita",
                 "La tarjeta se elige por su FQBN; el core de la tarjeta se instala automáticamente."],
                ["ESPHomer", "El CLI de esphome",
                 "Dispositivos de casa inteligente a partir de YAML; generador de configuración sin interfaz; primer flasheo por USB, luego OTA."],
            ]},
            callout=("Sólo hardware autorizado",
                     "Flashear, borrar, reiniciar y subir cambian un dispositivo real conectado. STM32er maneja "
                     "firmware crítico de robots, y por eso su preflight falla de forma segura."),
            deck="table"),
        Section("engines", "MOTORES CREATIVOS", "Unreal Engine y Blender, en vivo",
            "Dos agents manejan editores en ejecución por sus propios sockets, desde el chat o desde el canvas.",
            points=[
                ("Unrealer", "Habla con el plugin Unreal MCP por TCP: 53 comandos en nueve categorías "
                 "(editor, Blueprint, nodos, proyecto, UMG, sistema, nivel, asset y material)."),
                ("El fork de Unreal de Tlamatini", "XaihtUnrealEngineMCP incluye toda la superficie más un generador de andamiaje para "
                 "un proyecto C++ de UE 5.8 listo para compilar con una solución de Visual Studio 2026."),
                ("Blenderer", "Habla el protocolo de ejecución de código del add-on oficial Blender MCP en su socket "
                 "local, con un catálogo rico de acciones, así que la mayoría de las tareas no necesitan Python escrito a mano."),
                ("Encadenables", "Ambos devuelven bloques estructurados, así que Parametrizer puede llevar un resultado al "
                 "siguiente paso y un Forker puede ramificarse según él."),
            ], deck="cards"),
        Section("security", "SEGURIDAD", "Evaluación para objetivos autorizados",
            "Las herramientas ofensivas y defensivas son parte del catálogo, siempre limitadas a sistemas que son tuyos o que tienes "
            "autorización explícita para probar.",
            points=[
                ("Kalier", "Herramientas de Kali Linux por medio de MCP-Kali-Server: nmap, gobuster, nikto, sqlmap y más."),
                ("Discoverer", "subfinder, httpx, naabu, katana, nuclei y vulnx sobre un toolchain privado de Go."),
                ("Nmapper", "Usa el nmap que tú instalaste; nunca lo incluye; el connect scan no necesita admin."),
                ("Analyzer", "bandit, semgrep, ruff, eslint, gitleaks y pip-audit, de forma determinista."),
                ("Reviewer", "Una revisión de un diff a nivel senior, con un veredicto según el cual un flow puede ramificarse."),
                ("Kyber", "Generación de llaves, cifrado y descifrado poscuánticos."),
            ], deck="cards"),
        Section("bluehat", "KIT BLUE-HAT", "Defensa de Windows, operada por una persona",
            "El kit `security/` es un conjunto de monitoreo y respuesta que corre un administrador, no un tool del chat: una "
            "persona lo lanza, lee su evidencia y decide.",
            body=[
                "Habilitarlo hace cambios persistentes. Defender y el firewall siguen corriendo, pero la "
                "instalación se excluye de los escaneos, se permite en Controlled Folder Access, y seis reglas de reducción "
                "de la superficie de ataque pasan a modo Audit. Esas excepciones son concesiones reales, así que registra una "
                "línea base antes de elevar privilegios; no hay rollback automático.",
                "El monitor vigila diez familias de señales, desde la salud de Defender y los inicios de sesión hasta la persistencia, "
                "los indicadores de ransomware y los cambios en el grupo de administradores. Empieza con una línea base sólo de detección, "
                "investiga, y ármalo sólo cuando se justifique. Un harness visible no destructivo valida los "
                "propios activos.",
            ],
            table={"columns": ["Modo", "Comportamiento"], "widths": [0.28, 0.72], "rows": [
                ["-DetectOnly", "Reporta lo que bloquearía o detendría; la primera ejecución segura."],
                ["default", "Un barrido armado; puede bloquear una IP atacante y detener tools de atacantes conocidos."],
                ["-Watch", "Barridos continuos hasta Ctrl+C, cada 60 segundos de forma predeterminada."],
                ["-Aggressive", "También detiene tools de doble uso fuera de los paths de Tlamatini; sólo en incidentes."],
            ]}, deck="split",
            deck_points=[
                ("Operado por una persona", "Una persona lo lanza y es dueña de cada cambio de política."),
                ("Diez familias", "Defender, inicios de sesión, red, procesos, persistencia, ransomware, cuentas."),
                ("Detectar primero", "Línea base con -DetectOnly antes de armar."),
                ("Concesiones", "Las exclusiones y las reglas en modo Audit se registran y se explican."),
            ]),
        Section("voice", "VOZ", "Te escucha hasta que paras, y te contesta con su voz",
            "El dictado directo en el chat, el Whisperer de workflows, Talker y los comandos del catálogo tienen contratos de voz distintos.",
            body=[
                "En el Whisperer independiente o de workflow, si no hay duración la compuerta graba mientras hablas y se detiene "
                "después de 3.5 segundos de silencio, con un tope de 300 segundos. `record_seconds: 0` es el interruptor; di "
                "una duración y se respeta exactamente. La compuerta empieza en un nivel sensible para que se oiga a quien "
                "empieza a hablar de inmediato, y si un driver de sonido rechaza el stream en vivo, ella graba una duración "
                "fija y lo dice. El dictado directo en el chat, en cambio, exige la compuerta y rechaza ese fallback.",
                "La transcripción corre localmente con faster-whisper, en una GPU cuando hay y en el CPU si no, "
                "o por medio de un proveedor de Whisper en la nube. Talker habla con un modelo compatible con Orpheus en una "
                "voz femenina: tara, leah, jess, mia o zoe. Una voz masculina se rechaza por diseño.",
                "La primera sección del catálogo, VOICE COMMANDS, convierte el micrófono en el teclado: ella transcribe "
                "tu instrucción, te la lee de vuelta, y sólo entonces actúa. Cualquier cosa irreversible sigue necesitando tu "
                "confirmación por escrito según esas instrucciones del catálogo. Config > Micrófono elige el envío automático "
                "o un borrador editable. El envío real usa la voz del browser para confirmar, y respeta el modo Silencio.",
            ], deck="list",
            deck_points=[
                ("Compuerta de sonido", "Graba mientras hablas; se detiene después de 3.5 s de silencio."),
                ("Duración en workflows", "La grabación independiente o de workflow puede usar una duración fija explícita."),
                ("Primero lo local", "faster-whisper en GPU o CPU, o un proveedor en la nube."),
                ("Su voz", "Sólo femenina: tara, leah, jess, mia o zoe."),
                ("Micrófono directo", "Compuerta, reconocimiento, y luego enviar o conservar un borrador editable; sin consola extra."),
                ("Comandos del catálogo", "Las tarjetas mediadas por el modelo pueden pedir que se lea de vuelta antes de actuar."),
            ]),
        Section("vision", "VISIÓN Y VIDEO", "Ojos que reportan sus límites",
            "El análisis de imágenes y de video combina observadores independientes, así que la suposición de un modelo nunca se presenta "
            "como un hecho.",
            points=[
                ("Image-Interpreter", "Dos modelos de visión leen cada imagen en paralelo con sus propias conexiones; "
                 "un tercero combina ambos. Una lista separada por comas lee varias imágenes."),
                ("Video-Analyzer · robótica", "Una compuerta de movimiento determinista más dos modelos de visión; PASS sólo "
                 "cuando ambos coinciden."),
                ("Video-Analyzer · transcripción", "Voz con marcas de tiempo de las pistas de audio elegidas o de un link web, de forma local."),
                ("Video-Analyzer · resumen", "Voz más evidencia visual muestreada: escenas, texto, hechos, "
                 "decisiones y límites; un link web se descarga primero."),
                ("Captura", "Shoter, Camcorder y Recorder guardan en tus carpetas conocidas con nombres exactos."),
                ("Pegar en el chat", "Un screenshot pegado en el chat se vuelve un path que ella puede analizar."),
            ], deck="cards"),
        Section("desktop", "ESCRITORIO Y BROWSER", "Manos precisas en un escritorio real",
            "Los agents de escritorio declaran sus espacios de coordenadas y su evidencia, porque un clic que cae en "
            "el lugar equivocado es peor que no hacer clic.",
            points=[
                ("Mouser", "Las coordenadas se declaran: pantalla física, escritorio, normalizadas, ventana o "
                 "screenshot."),
                ("Shoter", "Publica el rectángulo exacto capturado, el tamaño de la imagen y la geometría del monitor."),
                ("Keyboarder", "Liga cada tecla a una ventana verificada y se detiene si se pierde el foco."),
                ("Entregar no es aceptar", "`input_sent` sólo prueba la entrega; el input interrumpido se "
                 "inspecciona antes de repetir."),
                ("Playwrighter", "Un browser real con pasos declarados, con un ajuste para dejarlo abierto y mirarlo."),
                ("Windower", "Enfoca, mueve, cambia de tamaño, acomoda en mosaico, fija y cierra ventanas por su título."),
            ], deck="cards"),
        Section("web", "BÚSQUEDA WEB", "Tres niveles de búsqueda, un solo presupuesto de tiempo",
            "El tool de búsqueda del chat y el agent del pool usan la misma implementación de Googler, con un presupuesto "
            "predeterminado de 120 segundos y resultados explícitos.",
            body=[
                "Sin un motor fijo, seis vías de HTTP simple compiten por resultados relevantes. Si ninguna contesta, "
                "el Chrome real instalado usa un perfil persistente en ocho vías del browser. Las fuentes de conocimiento abierto "
                "forman el último nivel: Wikipedia, arXiv, OpenAlex, Hacker News, GitHub, Internet Archive "
                "y Project Gutenberg. El log nombra el motor y el nivel que contestaron.",
                "Un registro compartido de salud pone en descanso a los motores que se niegan por 3, 10 o 30 minutos; un resultado fuera de tema "
                "se rechaza, y una vía que se niega no se vuelve a consultar en la misma ejecución. Bloqueado, tiempo agotado, "
                "inalcanzable y sin coincidencias son resultados distintos. El wrapper del chat soporta Cancelar y "
                "hace cumplir un límite de tiempo del proceso con un margen para limpiar.",
                "Los dorks estructurados conservan presets, filtros agrupados y la entrega de URLs con links_only. Una lista explícita "
                "de engines se salta los niveles de HTTP y de fuentes abiertas. Fija Google cuando importen los operadores "
                "exclusivos de Google; los motores alternativos pueden ampliar su significado. Las licencias y la autorización siguen siendo tu responsabilidad.",
            ], deck="list",
            deck_points=[
                ("Nivel 0", "Seis vías HTTP en paralelo; la relevancia se revisa antes de aceptar."),
                ("Nivel 1", "Ocho vías del browser en el orden del registro de salud; perfil persistente de Chrome."),
                ("Nivel 2", "Fuentes de conocimiento abierto claramente atribuidas cuando las vías de búsqueda no funcionan."),
                ("Trabajo acotado", "120 segundos de forma predeterminada, cancelación y resultados de error con nombre."),
                ("Contrato de dorks", "Los engines explícitos se saltan los niveles alternativos; links_only entrega URLs."),
            ]),
        Section("crawler_current", "LECTURA WEB", "Lee la página pedida, reporta lo que pasó",
            "Crawler empieza con la página dada, acota su trabajo y mantiene las páginas de rechazo lejos del modelo.",
            body=[
                "El crawl_type predeterminado es page, con include_seed habilitado. Un crawl por rango usa de forma predeterminada "
                "25 páginas y un presupuesto de 900 segundos para toda la ejecución. Cada descarga tiene un límite predeterminado de 45 segundos de reloj "
                "y un tope de 8,000,000 de bytes. Son valores predeterminados configurables; cero desactiva el conteo de páginas "
                "o el límite de todo el crawl, así que la operación ilimitada tiene que ser una elección deliberada.",
                "Los encabezados se leen sin distinguir mayúsculas. Los muros de bots, las páginas CAPTCHA y los rechazos de acceso se "
                "reportan antes del análisis; los tiempos agotados y las páginas inalcanzables siguen siendo resultados con nombre. Si no se "
                "analizó nada, el reporte final lo dice. Crawler lee el HTML descargado; no ejecuta JavaScript.",
                "Desde v1.72.4, Crawler y Googler usan una pila de regiones HTML saltadas, manejan los finales de head "
                "omitidos y las etiquetas que se cierran solas, y comparan la extracción con un fallback de texto plano. "
                "Cuando ese fallback tiene al menos 200 caracteres y el parser conservó menos del 25 por ciento, "
                "el fallback toma el control. Crawler avisa en su log; Googler devuelve un extraction_note. "
                "Las excepciones del parser también usan el fallback; las extracciones sanas no cambian.",
            ], deck="cards",
            points=[
                ("Primero la página", "Lee la URL semilla de forma predeterminada; el crawl por rango es explícito."),
                ("Presupuestos", "Valores predeterminados: 25 páginas, 900 segundos en total, 45 segundos por descarga."),
                ("Resultado veraz", "Los rechazos nunca se vuelven contenido fuente; la falta de análisis se reporta claramente."),
                ("Red de seguridad de texto", "Debajo del 25% de un fallback de más de 200 caracteres: recupera y avisa."),
            ]),
        Section("network_measurement", "MEDICIÓN DE RED", "Velocidad medida con su barra de error",
            "NetSpeed-Calculator publica una velocidad con un intervalo de confianza y mide la latencia bajo carga.",
            body=[
                "Varios proveedores sin llave corren en paralelo. La medición descarta la rampa de slow-start "
                "de TCP, muestrea el throughput como una derivada, rechaza valores atípicos y fusiona los proveedores con un "
                "metaanálisis de efectos aleatorios. Califica el bufferbloat de A+ a F. Una ejecución completa transfiere unos "
                "100 a 200 MB, así que pregunta antes de correr.",
            ], deck="list",
            deck_points=[
                ("Throughput", "Streams en paralelo, intervalos t de Student, fusión de efectos aleatorios."),
                ("Bufferbloat", "Latencia bajo carga, calificada de A+ a F."),
                ("Con medidor", "Unos 100 a 200 MB por ejecución completa; pregunta primero."),
            ]),
        Section("messaging", "MENSAJERÍA", "Llegar a las personas de forma deliberada",
            "Los agents de mensajería usan superficies oficiales de forma predeterminada y hacen de cada vía no oficial una elección "
            "explícita.",
            points=[
                ("Telegrammer", "Envía como el bot o como tu propia cuenta; “envíalo como yo” elige la tuya."),
                ("Whatsapper", "La Cloud API oficial de Meta de forma predeterminada; tu propio número sólo cuando lo dices."),
                ("TeleTlamatini", "El chat completo en Telegram, en una cuenta dedicada."),
                ("Instant Messaging Doctor", "Revisa tokens, contactos, plantillas y ventanas de política."),
                ("Contactos", "El nombre de un contacto se resuelve a la dirección real cuando se envía un mensaje."),
            ], deck="cards"),
    ])

    trust = Chapter("trust", "VI", "Las promesas que cumple",
        "Honestidad, consentimiento, seguridad y control, escritos en el código y no en un folleto.",
        accent="rose", sections=[
        Section("honesty", "HONESTIDAD", "La verdad antes que la comodidad",
            "Donde un sistema puede equivocarse con total seguridad, Tlamatini está construida para decir lo que sabe y lo que "
            "no sabe.",
            points=[
                ("Primero el autorreporte", "El resultado tipado de un agent pesa más que un código de salida de un bit."),
                ("Degradado es rojo", "Un entregable comprometido nunca se pinta de verde."),
                ("El silencio tiene nombre", "Los archivos saltados, las transferencias muertas y los rechazos llevan una razón."),
                ("La recuperación se narra", "Los reintentos se muestran en vivo y se resumen en la respuesta."),
                ("Creado no es limpio", "Los documentos reportan sus auditorías antes de darse por terminados."),
                ("Entregado no es aceptado", "La evidencia de input del escritorio se mantiene aparte del éxito."),
            ], deck="cards"),
        Section("failmodes", "MODOS DE FALLA", "Fallar abierto o fallar seguro, a propósito",
            "Cada protección elige su dirección de falla deliberadamente, preguntándose qué error te dañaría "
            "más.",
            table={"columns": ["Mecanismo", "Dirección", "Por qué"], "widths": [0.30, 0.16, 0.54], "rows": [
                ["Protección de contenido binario", "Abierto", "Tirar contexto real es peor que incrustar un archivo raro."],
                ["Análisis del veredicto", "Abierto", "Un error de parseo pasa a la siguiente regla; nunca lanza una excepción."],
                ["Configuración de puerto y consola", "Abierto", "Un error de dedo nunca debe impedir que el servidor arranque."],
                ["Aprovisionador de runtimes", "Abierto", "Una descarga con error nunca bloquea el arranque."],
                ["Ajustador de Compact mode", "Abierto", "Ante cualquier duda envía la solicitud completa, exactamente como antes."],
                ["Ask Execs", "Seguro", "Ante cualquier duda se resuelve como Denegar."],
                ["Copias de la base de datos", "Seguro", "Una copia dudosa o sin revisar se reporta como error."],
                ["Protección del bisect de LaTeXer", "Seguro", "En caso de duda, protege el contenido del autor."],
                ["Preflights de firmware", "Seguro", "Se niegan antes que compilar o flashear el destino equivocado."],
                ["Deleter", "Seguro", "Rechaza carpetas protegidas, raíces de repositorios y raíces de unidades."],
            ]}, deck="table"),
        Section("responsibility", "RESPONSABILIDAD", "Tus agents, tu jurisdicción",
            "Cada agent es un programa en Python simple, así que puedes leerlo, auditarlo, editarlo, restringirlo o desactivarlo. Esa "
            "transparencia es un medio de control, no una garantía de seguridad.",
            body=[
                "Los agents no tienen autoridad propia. Tú decides si corren, dónde, cómo y con qué permisos "
                "lo hacen. Cuando habilitas, configuras, modificas, encadenas o ejecutas un agent, esa ejecución está bajo "
                "tu control y tu jurisdicción.",
                "Eres responsable de revisar el código y la configuración, limitar los secretos y los permisos, "
                "autorizar cada archivo, destino, browser, shell, API, servidor MCP, máquina y dispositivo que un agent "
                "pueda alcanzar, supervisar su output y cumplir con las leyes, políticas, licencias y "
                "acuerdos que apliquen.",
                "Al ejecutar un agent aceptas la responsabilidad de sus acciones y sus consecuencias. Lo que Tlamatini ofrece en "
                "orquestación, documentación y barandales no autoriza el acceso a sistemas de terceros y "
                "no pueden reemplazar tu propia revisión de seguridad, tus controles de permisos, tu monitoreo ni tu cumplimiento legal.",
            ], deck="list",
            deck_points=[
                ("Legible", "Cada agent es Python simple que puedes auditar y cambiar."),
                ("Tu decisión", "Tú eliges si un agent corre, dónde y cómo."),
                ("Tu alcance", "Tú autorizas cada archivo, destino, máquina y dispositivo."),
                ("Tu responsabilidad", "Ejecutar un agent es aceptar sus consecuencias."),
            ]),
        Section("datasafety", "SEGURIDAD DE LOS DATOS", "Tus datos, manejados con cuidado",
            "Las bases de datos, los secretos y los archivos temporales tienen cada uno un camino bien definido.",
            points=[
                ("Base de datos segura con WAL", "Los backups leen a través del write-ahead log con el API de backup en línea de SQLite "
                 "y se verifican con quick_check."),
                ("Reemplazo por etapas", "Una base de datos nueva espera en DB/ToLoad; la vieja se archiva con sus "
                 "archivos acompañantes antes de que arranque Django."),
                ("Secretos", "Los campos secretos conocidos se redactan de los archivos .flw exportados y de los builds públicos."),
                ("Contactos privados", "Los builds públicos y los snapshots del source no llevan datos de contactos."),
                ("Archivos temporales", "Los archivos temporales se quedan dentro de la propia carpeta Temp de la aplicación."),
                ("Contraseñas", "Las contraseñas de PDF viven sólo en memoria."),
            ], deck="cards"),
        Section("visible", "PROBADO A LA VISTA", "Nada corre donde nadie lo puede ver",
            "La regla de desarrollo de Tlamatini es que cada prueba, build y diagnóstico corra de forma visible, en un escritorio "
            "real, donde su creadora puede ver cada paso.",
            body=[
                "Las pruebas de browser corren con ventana en Chrome real, las consolas se abren en primer plano, y las fotos de todo el "
                "escritorio las toma el propio agent Shoter de Tlamatini, porque usar el agent es la prueba "
                "del agent. Una respuesta vieja, transitoria o con tiempo agotado nunca se registra como aprobada.",
                "Las protecciones derivadas del source detienen la deriva antes de publicarse: el vocabulario de status, los nombres para mostrar, el cierre "
                "de diálogos, el orden del catálogo, la lista permitida de Ask Execs, la compuerta de self-modify y la prueba de módulos "
                "del bundle congelado se revisan con pruebas que leen el source real.",
            ], deck="list",
            deck_points=[
                ("Visible", "Sólo browsers con ventana y consolas en primer plano."),
                ("Fotografiado", "Evidencia de todo el escritorio tomada por el agent Shoter."),
                ("Veraz", "Los resultados viejos o con tiempo agotado nunca cuentan como aprobados."),
                ("Protecciones contra la deriva", "Las pruebas leen el source real para detener la deriva silenciosa."),
            ]),
    ])

    running = Chapter("running", "VII", "Instalar, configurar, ejecutar",
        "De una máquina Windows recién instalada a una asistente funcionando, y del source a un release aprobado.",
        accent="jade", sections=[
        Section("start", "PRIMEROS PASOS", "Cinco pasos para tener Tlamatini funcionando",
            "Tlamatini en sí es gratis. La única compra es un plan de Ollama, comprado directamente a Ollama.",
            visual="steps",
            visual_data={"steps": [
                ("Instalar", "Ejecuta el instalador recuperable del release (con Python 3.12.10 incluido), o clona el source."),
                ("Ollama", "Instala Ollama para Windows."),
                ("Plan Pro", "Activa Ollama Pro o superior, y luego ejecuta `ollama signin`."),
                ("Modelos", "Descarga nomic-embed-text y los modelos en la nube que usa Tlamatini."),
                ("Configurar", "Abre Config ▸ Modelos y el Access Keys Wizard, y luego marca Multi-Turn."),
            ]},
            code=("git clone https://github.com/XAIHT/Tlamatini.git\n"
                  "cd Tlamatini\n"
                  "python -m venv venv && venv\\Scripts\\activate\n"
                  "pip install -r requirements.txt\n"
                  "python Tlamatini/manage.py migrate\n"
                  "python Tlamatini/manage.py runserver --noreload\n"
                  "# abre http://127.0.0.1:8000/   (login predeterminado: user / changeme)"),
            deck="visual"),
        Section("dependencies", "COBERTURA DE DEPENDENCIAS", "Cada librería de Python referida está contemplada",
            "La auditoría de dependencias del 18 de octubre cubre los 85 agents, los helpers de build, los imports opcionales y las pruebas.",
            body=[
                "La protección estática actualizada revisó 855 archivos de Python y 72 distribuciones referidas directamente. El "
                "archivo completo de requirements fija las 263 distribuciones, incluido PyTorch para CPU. Pasaron una instalación "
                "limpia de Python, una revisión de consistencia de dependencias y los imports en runtime.",
                "ESPHome tiene un manifiesto aparte, requirements-esphome.txt, porque sus versiones fijas de py7zr y PlatformIO "
                "chocan con el entorno principal. Mantenlo en su runtime privado. bpy de Blender, "
                "unreal de Unreal, los toolchains de dispositivos, los paquetes npm y los pesos de los modelos siguen sus propios contratos "
                "de runtime; no son paquetes pip faltantes.",
            ],
            points=[
                ("Protección de cobertura", "scripts/check_requirements_coverage.py revisa los inventarios del source y del build."),
                ("Verificación", "18 de octubre: sin declaraciones faltantes, errores de sintaxis ni imports dinámicos sin revisar."),
                ("Evidencia anterior", "27 de septiembre: pasaron las ejecuciones de prueba de main/ESPHome y las revisiones rápidas de dependencias en un entorno temporal."),
                ("Límites", "Una instalación limpia de las dependencias de Python no certifica el instalador compilado ni cada integración externa."),
            ], deck="cards"),
        Section("modes", "RUNTIME", "Dos modos y sus puertos de servicio",
            "Tlamatini corre desde el source o como un ejecutable congelado construido con PyInstaller. Sólo cambia la resolución "
            "de paths, y `CONFIG_PATH` reemplaza la ubicación de la configuración en ambos.",
            body=[
                "Un build instalado resuelve `config.json` junto a `Tlamatini.exe`; una ejecución desde el source usa "
                "`Tlamatini/agent/config.json`. Un segundo eje independiente es la automodificación: un build hecho "
                "con `--self-modify` lleva su source completo y recompilable junto al ejecutable, y su "
                "autoconocimiento viaja con él. Sin la bandera, no se incluye ninguno. Una ejecución desde el source siempre "
                "puede automodificarse, y un interruptor Self-modify de la barra de herramientas decide por solicitud si se envía "
                "su autoconocimiento; se bloquea apagado cuando el modelo no puede contenerlo.",
                "El dictado directo además usa un listener loopback privado y efímero para el saludo "
                "de su worker. Se cierra después de la autenticación; no es un cuarto servicio público ni un puerto fijo.",
                "Ambos servicios MCP respetan sus hosts y puertos configurados en modo source y congelado; "
                "las URIs de sus clientes deben coincidir. Files-Search también respeta su número de workers y acota las esperas "
                "de RPC. Ambos clientes soportan archivos de configuración UTF-8 con BOM y los overrides de CONFIG_PATH.",
            ],
            table={"columns": ["Puerto", "Protocolo", "Servicio"], "widths": [0.20, 0.22, 0.58], "rows": [
                ["8000 (predeterminado)", "HTTP + WebSocket", "Interfaz web y chat; cámbialo con django_port."],
                ["8765 (predeterminado)", "WebSocket", "MCP System-Metrics; haz coincidir el puerto del servidor y la URI del cliente."],
                ["50051 (predeterminado)", "gRPC", "MCP Files-Search; haz coincidir el puerto del servidor y la URI del cliente."],
            ]}, deck="split",
            deck_points=[
                ("Source", "Corre desde el repositorio con manage.py."),
                ("Congelado", "Un ejecutable de PyInstaller con su propio Python."),
                ("Self-modify", "Siempre desde el source; opcional en un build; un interruptor lo envía."),
                ("Puertos", "Predeterminados: 8000, 8765 y 50051; configura los clientes y los servidores juntos."),
            ]),
        Section("settings", "CONFIGURACIÓN", "Las configuraciones que más importan",
            "Unas cuantas llaves de `config.json` dan forma a su comportamiento; todo lo demás tiene valores predeterminados sensatos.",
            table={"columns": ["Llave", "Predeterminado", "Propósito"], "widths": [0.37, 0.16, 0.47], "rows": [
                ["django_port", "8000", "Puerto web para todas las formas de arranque; si falla, vuelve a 8000."],
                ["unified_agent_max_iterations", "4096", "Límite superior de vueltas del ciclo de tools de Multi-Turn."],
                ["unified_agent_llm_step_timeout_seconds", "900", "Watchdog para un intento del modelo."],
                ["llm_client_timeout_seconds", "600", "Cuánto puede tardar una llamada al modelo."],
                ["model_brain", "auto", "Ajusta cada modelo a partir de fuentes formales; off restaura el sampler heredado."],
                ["ollama_repeat_penalty", "1.2", "Sampler heredado, enviado sólo cuando model_brain está en off."],
                ["ollama_num_ctx", "1048576", "Ventana pedida heredada; el brain la limita a la real."],
                ["context_sidecar_llm_timeout_seconds", "60", "Límite de tiempo para las propias llamadas al modelo de los helpers de contexto."],
                ["context_compact_mode", "auto", "Compact mode se bloquea encendido para los modelos que no pueden contenerlo todo."],
                ["binary_context_detection", "true", "Revisa los archivos por su contenido antes de hacer embeddings."],
                ["console_quick_edit", "false", "Evita que un clic pause una consola congelada."],
                ["console_colors", "true", "Colorea las líneas de la consola por nivel; el log se queda en texto plano."],
                ["runtime_autoprovision", "true", "Deja que los servidores MCP aprovisionen Node o uv de forma privada."],
            ]},
            callout=("Medido, no elegido por gusto",
                     "El sampler heredado viene de pruebas repetidas con cargas de trabajo reales, y una sola ejecución rápida nunca "
                     "justifica un cambio. "
                     "El Model Brain ahora ajusta cada modelo a partir de fuentes formales."),
            deck="table"),
        Section("pipeline", "BUILD Y RELEASE", "Del árbol del source al instalador",
            "Tres scripts de build producen un release independiente para Windows, y el build prueba lo que incluye "
            "antes de empaquetar cualquier cosa.",
            visual="chain",
            visual_data={"chain": ["build.py", "Revisiones del congelado", "Desinstalador", "Instalador", "pkg.zip",
                                   "Release"],
                         "caption": "Cada etapa verifica la anterior."},
            points=[
                ("Bundle de PyInstaller", "Archivos estáticos recolectados, plantillas, agents, skills y helpers, con "
                 "numpy y OpenCV incluidos en los dos Pythons que se distribuyen."),
                ("Prueba de transporte", "El build abre el archivo que produjo y se detiene si falta un módulo "
                 "requerido de los que fallan abiertos."),
                ("Compuertas de runtime", "Cada runtime de agent y cada cargador de modelos se ejecuta dentro del nuevo "
                 "ejecutable congelado, y la revisión del Prompt Flow Panel también corre ahí."),
                ("Recibo de integridad", "Un recibo SHA-256 cubre cada archivo del payload y se vuelve a revisar cuando "
                 "se arma el instalador."),
                ("Tope de tamaño", "El ZIP final del release se queda debajo de 1,990,000,000 bytes; los archivos requeridos "
                 "nunca se quitan para que quepa."),
            ], deck="split",
            deck_points=[
                ("Bundle", "Archivos estáticos, plantillas, agents, skills y ambos Pythons."),
                ("Prueba de transporte", "Se detiene si falta un módulo requerido de los que fallan abiertos."),
                ("Compuertas de runtime", "Cada runtime de agent y cada cargador de modelos corre congelado."),
                ("Recibo", "SHA-256 para cada archivo del payload y todos los helpers raíz requeridos, revisado antes de usarse."),
                ("Tope", "Debajo de 1,990,000,000 bytes, sin quitar nada para que quepa."),
            ]),
        Section("root_carriage", "REPARACIÓN DEL BUILD · 27 DE SEPTIEMBRE", "Un solo inventario incluye cada helper requerido",
            "Una reparación del 27 de septiembre, incluida desde v1.72.1, lleva el helper de configuración de Whisperer sin debilitar la verificación del paquete.",
            body=[
                "Un build rechazó correctamente un recibo de runtime porque faltaba chat_voice_settings.py. "
                "El verificador exigía el helper suelto, pero build.py usaba un diccionario de copia aparte que "
                "lo omitía. Compilar agent.chat_voice_settings no satisface al worker independiente de Whisperer "
                "que corre con el Python incluido.",
                "build.py ahora llama a copy_root_sources con el inventario ROOT_SOURCES del verificador. Todos "
                "los inputs se revisan antes de copiar. Cada destino mapeado es obligatorio tanto en los recibos del ZIP como "
                "en los de la etapa extraída, así que quitar un archivo requerido y su entrada en el recibo sigue fallando. "
                "La línea base de hashes previa al congelado sigue rechazando cambios en el source durante un build.",
            ],
            points=[
                ("Un solo transportador", "La copia y la verificación comparten ROOT_SOURCES; un nuevo helper requerido no necesita una segunda lista."),
                ("Import del worker", "Lleva chat_voice_settings.py en la raíz de la instalación además de compilar el módulo de Django."),
                ("Integridad", "Rechaza archivos faltantes, editados o fuera del manifiesto, incluidos los recibos incompletos que por lo demás son consistentes."),
                ("Inputs de recompilación", "Los barridos espejo de self-update/self-modify incluyen el inventario compartido y reportan las revisiones de Git omitidas."),
            ], deck="cards"),
        Section("carriage_evidence", "VERIFICACIÓN REGISTRADA", "La evidencia del empaquetado y sus límites",
            "Las revisiones a nivel de archivos del 27 de septiembre establecen el transporte y la integridad; un instalador completo es una verificación aparte.",
            body=[
                "La suite enfocada registrada corrió 146 pruebas: 145 pasaron y un censo que depende de Git se saltó. "
                "Ejercitó el transportador real con archivos del source, importó el worker desde una instalación preparada, "
                "y verificó la creación del ZIP, la extracción y los recibos con binarios de runtime sintéticos. "
                "Se rechazaron los helpers faltantes o corruptos y los archivos extra.",
                "El barrido de self-update registrado con --no-git no tuvo hallazgos. Un snapshot de self-modify copió "
                "1,579 archivos sin errores de copia y contempló los 778 inputs de source del runtime. "
                "Son los conteos fechados de esa auditoría. Ni esas revisiones ni esta regeneración del dossier corrieron "
                "un build completo de PyInstaller, instalaron un release ni hicieron un cambio de actualización en vivo.",
            ],
            points=[
                ("Suite enfocada", "146 pruebas registradas: 145 pasaron, una se saltó; el harness sólo de archivos salió con éxito."),
                ("Archivos reales", "Cada destino de source mapeado coincidió; el worker preparado resolvió su helper de configuración."),
                ("Snapshot", "Auditoría registrada: 1,579 archivos, 11 redactados, 778 inputs de runtime cubiertos, cero errores de copia."),
                ("Evidencia", "docs/build-root-assets-verification.md registra el alcance, las revisiones saltadas y las transcripciones locales."),
            ], deck="cards"),
        Section("update", "AUTOACTUALIZACIÓN", "Actualizarse sin perderte",
            "Acerca de ▸ Buscar actualizaciones trae el último release publicado, lo prepara y le pasa "
            "el cambio de archivos bloqueados a un script externo.",
            body=[
                "El cambio conserva `config.json`, la base de datos, los contactos, el catálogo de External MCPs, Temp, "
                "Templates, el contenido generado y el desinstalador que se construye por separado. La base de datos se copia "
                "con el API de backup en línea de SQLite antes del apagado, y luego se le aplican las nuevas migraciones en "
                "el siguiente arranque, así que el historial del chat y la configuración sobreviven mientras llegan agents y prompts nuevos.",
                "Las descargas y los recibos de la preparación se verifican antes del apagado, y un prerrequisito con error se detiene "
                "antes de reemplazar cualquier archivo. Mientras corre la descarga, el diálogo de actualización está sellado y se niega "
                "a cerrarse.",
            ], deck="list",
            deck_points=[
                ("Releases publicados", "Sólo se ofrecen los releases publicados en GitHub."),
                ("Conservado", "Configuración, base de datos, contactos, catálogos, contenido."),
                ("Migrado", "Tu base de datos recibe las migraciones nuevas en el siguiente arranque."),
                ("Verificado", "Los recibos se revisan antes de reemplazar cualquier cosa."),
            ]),
        Section("versioning", "VERSIONADO", "Un número, de una sola fuente",
            "Tlamatini sigue el Versionado Semántico, con tags anotados de Git como única fuente de verdad.",
            body=[
                "El resolvedor del runtime, la ventana Acerca de, el endpoint `/agent/version/` y cada artefacto del build "
                "reportan el mismo tag base. La versión reportada nunca lleva un sufijo de desarrollo ni de cambios sin commit, "
                "y `TLAMATINI_VERSION` puede documentar un release antes de que se cree su tag.",
                f"Este dossier reporta la versión {version} e indica el tag, el commit y el estado de publicación exactos "
                f"en su capítulo Release.",
            ], deck="list",
            deck_points=[
                ("SemVer", "MAJOR.MINOR.PATCH a partir de tags anotados de Git."),
                ("Un solo resolvedor", "version.py, la ventana Acerca de y /agent/version/."),
                ("Sólo el tag base", "Sin sufijos .devN, +gSHA ni .dirty."),
                ("Override", "TLAMATINI_VERSION documenta un release antes de su tag."),
            ]),
    ])

    release = Chapter("release", "VIII", "Release actual",
        f"Release del source {f['release_tag']}; la entrega del paquete y la aceptación en runtime necesitan evidencia aparte.",
        accent="gold", sections=[
        Section("release188", "HEREDADO DE v1.88.0", "Terminales a la vista y un release privado con tus datos",
            "Tlamatini v1.88.0 introdujo Terminater; su tag se creó el 20 de octubre.",
            body=[
                f"Terminater es el agent de workflow número {f['agents']}. Abre terminales reales de CMD y PowerShell en una nueva "
                "área Terminals (Vistas → Terminals, o Ctrl+`) en las páginas del chat, del Agentic Control Panel y del Prompt Flow Panel"
                ". Tlamatini teclea cada tecla como una persona, unas 50 palabras por minuto y nunca pegando, espera el "
                "comando, lee todo su output y reporta el código de salida. Esc toma el teclado; un comando te lo puede pasar "
                "a propósito con <<USER:hint>>.",
                f"Un comando que deja de responder se marca como colgado y se puede detener sin perder la terminal; uno que "
                f"sale con error es una fila roja del Exec Report aunque la terminal haya funcionado. Un solo hub en el proceso de Django "
                f"es dueño de los shells, así que cerrar una página nunca cierra uno. Es el agent de chat wrapped número {f['wrapped']}, "
                f"la octava operación del Prompt Flow Panel, y tiene tres tarjetas seguras en el Catálogo de prompts.",
                "Ahora el build lo prueba dentro de la app congelada: check_terminater maneja un PowerShell real, un cmd.exe real, "
                "el agent del pool incluido con el Python incluido y un viaje de ida y vuelta por WebSocket, y el empaquetado se detiene si "
                "falla. El 19 de octubre pasaron 774 pruebas unitarias, y 1,668 pasaron después de la revisión de la documentación. Las "
                "suites visibles guardadas de la página del chat y del canvas no se volvieron a correr como una sola pasada limpia después de sus últimos arreglos.",
                "El tag v1.88.0 se creó el 20 de octubre y apunta al commit anterior a este trabajo; el trabajo llegó a "
                "main en el siguiente commit, así que un build de main reportaba entonces 1.88.0 y lo llevaba todo.",
                "El release privado (con llaves) ahora lleva los datos de la máquina que lo construye: cada servidor de External MCP "
                "de la copia instalada y su elección activa, combinados en un catálogo privado ignorado por git, y toda la "
                "bóveda data.keys. El builder público rechaza ambos. Una actualización desde la app no conserva data.keys.",
            ],
            points=[
                ("Terminales", "CMD y PowerShell reales que puedes ver, tecleados como una persona, con entrega del teclado."),
                ("Conteos actuales", f"{f['agents']} agents · {f['wrapped']} wrapped · {f['tools']} tools · {f['migrations']} migraciones."),
                ("Compuerta", "check_terminater corre dentro de la app congelada; el empaquetado se detiene si falla."),
                ("Release privado", "Los servidores de External MCP y data.keys viajan sólo en el build con llaves."),
            ], deck="cards"),
        Section("release187", "HEREDADO DE v1.87.0", "Menos agents, eliminación segura, release más chico",
            "Con tag del 18 de octubre: el catálogo bajó a 85 agents, y la eliminación se volvió rápida y recuperable.",
            body=[
                "Ese release tenía 85 agents de workflow: se quitaron Gatewayer, Gateway-Relayer, Node-Manager y "
                "Zavuerer. La migración 0214 borra sus filas y sus prompts del catálogo sin "
                "renumerar nada de lo que queda.",
                "El Desinstalador mueve la instalación aparte en la misma unidad en vez de copiarla, y "
                "ofrece Reintentar limpieza cuando queda atrás un archivo bloqueado. El release congelado ya no lleva "
                "las librerías de medios y de browser dos veces. Acerca de → Uso espera datos reales, y cada archivo "
                "de Python con seguimiento tiene una compuerta de calidad.",
                "El tag v1.87.0 se creó un minuto antes del trabajo que nombra. Los dos commits siguientes "
                "llegaron a main justo después, así que un build de main reportaba entonces 1.87.0 y lo llevaba todo.",
            ],
            points=[
                ("85 agents", "Cuatro agents retirados quitados con una migración hacia adelante."),
                ("Eliminación", "Mover aparte, verificar, Reintentar limpieza para lo bloqueado que queda."),
                ("Tamaño del release", "Las librerías de medios y de browser se incluyen una sola vez, en el Python incluido."),
                ("Calidad", "npm run lint:python revisa cada archivo de Python con seguimiento."),
            ], deck="cards"),
        Section("removal187", "NUEVO EN v1.87.0", "Desinstalar es rápido y recuperable",
            "El Desinstalador mueve las entradas a una carpeta de recuperación en vez de copiarlas y sacarles hash.",
            body=[
                "Cada movimiento se registra en un journal de esquema 2 antes y después de que pase. Una colisión "
                "en el destino se rechaza, y el journal se queda hasta que la limpieza tiene éxito. Si un paso reversible "
                "falla, las entradas y el estado de Windows se regresan a su lugar.",
                "Si se quita la aplicación pero queda un archivo bloqueado, la ventana dice Aplicación quitada; "
                "limpieza incompleta, lista lo que queda y ofrece Reintentar limpieza. Volver a abrir el Desinstalador puede "
                "terminar el trabajo después. Se conservan agents/ y las seis carpetas de contenido que tienen archivos.",
                "Una prueba de rendimiento del sistema de archivos quitó 64,264 archivos del paquete (3.88 GB) en 22.3 segundos con los 254 "
                "hashes conservados sin cambio. Mide la fase del sistema de archivos; una ejecución con el cliente compilado sigue siendo "
                "la prueba de aceptación.",
            ], points=[
                ("Journal", "Cada movimiento se registra antes y después."),
                ("Reintentar", "Lo bloqueado que queda se puede terminar después."),
                ("Se conserva", "agents/ y las carpetas de contenido que tienen archivos."),
                ("Prueba de rendimiento", "64,264 archivos en 22.3 s, 18 de octubre."),
            ], deck="cards"),
        Section("payload187", "NUEVO EN v1.87.0", "Un dueño para cada librería",
            "El proceso web congelado deja de llevar librerías que sólo usan los agents del pool.",
            body=[
                "cv2, ffpyplayer, av, playwright, faster_whisper, ctranslate2 y onnxruntime corren con el "
                "Python incluido, así que build.py los deja fuera del intérprete congelado. Las revisiones de Chromium y FFmpeg "
                "vienen del manifiesto de Playwright incluido.",
                "Sólo se quitan los cachés de bytecode cuyo source está a su lado, se descartan los archivos copiados por Git "
                "del desinstalador y el paquete se escribe con DEFLATE nivel 9. Una prueba del payload del release fija quién "
                "es dueño de cada librería.",
                "Acerca de → Uso muestra Revisando el uso… hasta que llegan datos reales del reporte, explica una conexión con error "
                "en Detalles de la conexión y reintenta por sí sola. Su solicitud de la cuenta es un "
                "POST /api/me sin cuerpo: un cuerpo {} hacía que el servidor local reiniciara la conexión.",
            ], points=[
                ("Propiedad", "Las librerías sólo del pool viven en el Python incluido."),
                ("Paquete", "Bytecode, copias del desinstalador y compresión ajustados."),
                ("Uso", "Revisando el uso… hasta que llegan datos reales."),
                ("Cuenta", "Un POST /api/me sin cuerpo."),
            ], deck="cards"),
        Section("sweep187", "DESPUÉS DEL TAG v1.87.0", "Barrido de consistencia",
            "Un barrido de todo el source volvió a derivar cada conteo y arregló lo que encontró.",
            body=[
                "El glob de Grepper y el pattern de Globber ahora entienden conjuntos con llaves como *.{js,py}, listas como "
                "*.py,*.js y globs de carpetas como src/**/*.py. Antes, cada uno buscaba en cero archivos y "
                "contestaba no_matches. Globber recorre el árbol una sola vez para varios patterns: tres minutos se volvieron "
                "diez segundos.",
                "Seis tools wrapped cuya etiqueta nombra una acción (Send Email, Move File, Summarize Text y los "
                "tres tools de Kyber) ahora obedecen la casilla de su agent en Configurar Agents. Un flow cargado conserva "
                "la etiqueta de FlowCreator, y la compuerta de calidad de Python corre en Windows Terminal.",
                "La prueba diaria del chat vuelve a leer este repositorio en vez de una copia vieja, y sus bancos de "
                "preguntas cubren los 85 agents y los 66 tools wrapped. Configurar Agents y Configurar MCPs ahora se abren "
                "con las casillas que guardó el servidor, así que un Continuar rápido ya no puede apagar la mayoría de los agents.",
            ], points=[
                ("Patterns", "Conjuntos con llaves, listas y globs de carpetas en Grepper y Globber."),
                ("Compuertas", "Seis tools wrapped siguen la casilla de su agent; Configurar se abre con las marcas guardadas."),
                ("Harness", "La prueba diaria del chat lee este repositorio."),
                ("Compuerta de calidad", "Corre en Windows Terminal, la predeterminada de Windows 11."),
            ], deck="cards"),
        Section("release186", "HEREDADO DE v1.86.0", "Carpetas de Mover y el atlas",
            "Con tag del 17 de octubre: un destino faltante se vuelve carpeta, y el atlas se reconstruye solo.",
            body=[
                "Mover crea un destino que todavía no existe, como scripts/architecture_atlas, como una "
                "carpeta, y el archivo conserva su propio nombre. Un renombre sigue pasando cuando el destino nombra un "
                "archivo: existe como archivo, tiene extensión, o el origen tampoco tiene. Una diagonal al final "
                "siempre significa una carpeta.",
                "python scripts/architecture_atlas/build_architecture_pdf.py regenera "
                "Tlamatini-Architecture.pdf con el propio LaTeXer de Tlamatini y verifica que cada archivo con seguimiento "
                "aparezca en él. Los códigos de salida 0, 1, 2 y 3 significan ok, error de tipografía, un archivo sin colocar y un "
                "archivo faltante.",
            ], points=[
                ("Mover", "Un nombre de destino nuevo se vuelve una carpeta."),
                ("Renombre", "Sólo cuando el destino nombra un archivo."),
                ("Atlas", "Lo reconstruye LaTeXer a partir del repositorio."),
                ("Prueba", "Cada archivo con seguimiento aparece en el atlas."),
            ], deck="cards"),
        Section("release185", "HEREDADO DE v1.85.0", "Actualizar, Vistas y un avatar centrado",
            "Con tag y publicado el 16 de octubre, con un espacio de trabajo del chat más flexible.",
            body=[
                "Actualizar vuelve a leer el documento abierto. Vistas hace espacio para el chat a todo lo ancho sin apagar el "
                "canvas. Restablecer distribución restaura la distribución sin borrar contenido. El retrato y su "
                "marco quedan centrados sobre Micrófono hasta Enviar mientras la caja de mensaje se encoge.",
                "El release conserva el router para soltar archivos en toda la página, la recuperación de la instalación, el renderizado de Markdown, "
                "el tablero de Uso, el Model Brain, Compact mode, el dictado por voz y los dos editores de flows.",
            ],
            points=[
                ("Actualizar", "El documento original, leído otra vez sin un selector."),
                ("Vistas", "Muestra u oculta el canvas y conserva su estado."),
                ("Restablecer distribución", "Restaura ambos paneles y acopla el avatar."),
                ("Retrato", "Centra todo el marco sobre la fila de acciones completa."),
            ], deck="cards"),
        Section("refresh185", "HEREDADO DE v1.85.0", "Actualiza el documento original",
            "Abrir elige un archivo. Actualizar vuelve a leer esa misma fuente, sin escribir en ella.",
            body=[
                "El acceso con el selector nativo conserva un handle que concede el browser. Lo que se suelta conserva su handle o su entrada "
                "durante el evento original, incluido el relevo del frame de PDF. Una fuente que sólo es snapshot explica "
                "por qué Actualizar no está disponible. Un documento generado vuelve a leer su endpoint autenticado de contenido guardado.",
                "El texto y el Markdown se comparan completos, incluidos los archivos vacíos. El mismo tamaño o la misma marca de tiempo nunca "
                "prueban que el contenido sea igual. Un documento sin cambios se queda en su lugar sin reconstruir el contexto. "
                "El contenido cambiado reemplaza el documento completo sólo cuando la preparación tiene éxito.",
                "Los estados de ocupado, sin cambios, actualizado, permiso y error tienen respuesta visible. Cancelar, Limpiar, "
                "abrir otro documento y una operación nueva invalidan las lecturas pendientes. Un error conserva el "
                "documento anterior y explica la siguiente acción.",
            ], points=[
                ("Abrir", "Elige un documento y conserva el acceso de lectura."),
                ("Actualizar", "Vuelve a leer la fuente conservada sin otro selector."),
                ("Error", "Conserva el contenido anterior y permite reintentar."),
                ("Contexto", "Prepara el contenido cambiado antes de reemplazar el contexto activo."),
            ], deck="cards"),
        Section("refreshviews185", "HEREDADO DE v1.85.0", "Mantén tu lugar de lectura",
            "Actualizar un Markdown o un PDF conserva la vista mientras cambia el documento de fondo.",
            body=[
                "El Markdown conserva Vista previa o Source, la posición de lectura y los recursos elegidos explícitamente. "
                "Sus bytes de source siguen siendo la base de Guardar. Los archivos de recursos elegidos por carpeta siguen siendo snapshots "
                "y se pueden elegir otra vez cuando esos archivos aparte cambien.",
                "Actualizar un PDF prepara un nuevo visor PDF.js respaldado por rangos antes de retirar el viejo. Conserva "
                "la página, el zoom, la rotación y el modo de desplazamiento, y ajusta la página a un documento más corto. Un PDF corrupto "
                "o una contraseña cancelada dejan visible el visor anterior. El iframe preparado sigue conectado "
                "durante el cambio para que el browser no lo recargue.",
                "Los PDFs siempre se recargan con Actualizar. No se introduce ningún hash de archivo completo, ninguna lectura anticipada del documento completo ni ninguna afirmación "
                "de igualdad sólo por metadatos. El reemplazo del contexto activo conserva las opciones establecidas de texto/imagen.",
            ], points=[
                ("Markdown", "Vista previa/Source, posición y recursos elegidos se quedan."),
                ("PDF", "Página, zoom, rotación y modo de desplazamiento se quedan."),
                ("Recuperación", "Un reemplazo con error conserva el visor anterior."),
                ("Evidencia", "20 revisiones visibles en Chrome el 15 de octubre."),
            ], deck="cards"),
        Section("views185", "HEREDADO DE v1.85.0", "Chat a todo lo ancho",
            "Vistas → Canvas muestra u oculta el canvas sin descargarlo.",
            body=[
                "Ocultar el canvas le da al chat todo el ancho. El documento, el visor de PDF, el modo de Markdown, "
                "la fuente de Actualizar, el borrador, el historial y el contexto cargado se quedan intactos. Abrir, soltar un documento "
                "soportado y un link a un archivo generado muestran el canvas cuando su resultado lo necesita.",
                "La elección se guarda por cuenta en ese browser y se sincroniza entre sus pestañas. Sobrevive "
                "a la recarga y al reinicio del browser. Otro perfil o origen del browser tiene preferencias aparte.",
                "Cambiar la visibilidad cancela los gestos de los divisores. El foco se mueve al menú Vistas sólo cuando su "
                "región actual desaparece, y la palomita expone su estado a la tecnología de asistencia.",
            ], points=[
                ("Todo lo ancho", "Oculta el canvas para darle más espacio al chat."),
                ("Continuidad", "Conserva el documento abierto y el contexto activo."),
                ("Preferencia", "Se guarda por cuenta y por origen del browser."),
                ("Navegación", "Abrir un documento muestra su canvas."),
            ], deck="cards"),
        Section("avatar185", "HEREDADO DE v1.85.0", "Un retrato centrado a cualquier altura",
            "El retrato y su marco comparten el centro de toda la fila de acciones de Micrófono a Enviar.",
            body=[
                "Antes, reducir la altura del composer encogía el retrato pero lo dejaba anclado a la "
                "orilla derecha. Ahora la distribución mide desde la orilla izquierda de Micrófono hasta la orilla derecha de Enviar y centra "
                "todo el dock sobre ese tramo. Los dos divisores, las distribuciones angostas y el zoom siguen la misma medida.",
                "El retrato sigue siendo cuadrado con un mínimo de 120 píxeles. Su tamaño flotante sigue siendo independiente. "
                "Ocultar el canvas acopla el retrato y desactiva el cambio de tamaño flotante por puntero, teclado "
                "y API. Mostrar el canvas vuelve a permitir el cambio de tamaño y deja el retrato acoplado.",
                "Vistas → Restablecer distribución muestra ambos paneles, restaura sus tamaños iniciales y acopla el avatar. "
                "No borra el documento, el borrador, el historial ni el contexto.",
            ], points=[
                ("Alineación", "De la orilla izquierda de Micrófono a la orilla derecha de Enviar."),
                ("Tamaño", "Un retrato cuadrado, nunca de menos de 120 píxeles."),
                ("Restablecer", "Restaura la distribución y conserva el contenido."),
                ("Evidencia", "19 revisiones visibles; error de centrado menor a 0.02 px de CSS, 16 de octubre."),
            ], deck="cards"),
        Section("carriage185", "HEREDADO DE v1.85.0", "La función completa viaja junta",
            "Los inventarios requeridos del runtime y de self-modify cubren la plantilla y los scripts de Vistas.",
            body=[
                "El recibo del runtime exige agent_page.html más agent_page_layout.js, avatar_size.js, "
                "agent_page_canvas.js y agent_page_init.js. El snapshot también exige los dos harnesses visibles de Vistas "
                "y las instrucciones de identidad. Actualizar conserva los transportadores existentes de PDF y Markdown.",
                "No hay migración nueva ni dependencia de Python. Su sufijo de caché era -avatar-center-1 y el "
                "sufijo de la plantilla de Vistas es _views1. La visibilidad es local del browser y no depende de Self-modify.",
                "La evidencia fechada incluye 160 pruebas de empaquetado/self-update/self-modify y 13 revisiones visibles del frontend "
                "congelado el 16 de octubre. Estas últimas usaron un ejecutable real con assets del frontend "
                "actuales verificados byte por byte en un fixture desechable. La guía de transporte registra el alcance exacto.",
            ], points=[
                ("Runtime", "La plantilla requerida y cuatro scripts que cooperan."),
                ("Snapshot", "Sources, identidad y los dos harnesses de Vistas."),
                ("Base de datos", "v1.85.0 no introdujo ninguna migración." ),
                ("Versión", "v1.85.0 en toda la aplicación en ese momento."),
            ], deck="cards"),
        Section("maintenance184", "HEREDADO DE v1.84.0", "Mantenimiento de catálogo y fixtures",
            "El commit de mantenimiento del 14 de octubre actualizó los datos del catálogo y de la configuración y limpió los fixtures de prueba.",
            body=[
                "El commit 1a8c5093 cambió los datos del catálogo de FlowCreator, el catálogo local de External MCPs y "
                "los fixtures de prueba. No introdujo ningún subsistema de producto, tipo de agent, migración ni dependencia nuevos. "
                "Los valores privados del catálogo se excluyen de este dossier.",
                "La auditoría actual lee la implementación real y mantiene fechados los resultados de pruebas históricas. "
                "Un valor de fixture es dato de prueba, no una credencial desplegada ni evidencia de que un proveedor corrió.",
            ], points=[
                ("Mantenimiento", "Los datos del catálogo y los fixtures de prueba cambiaron en el commit 1a8c5093."),
                ("Superficie del producto", "Ningún subsistema, tipo de agent, migración ni dependencia nuevos."),
                ("Privacidad", "Los documentos públicos excluyen los valores privados del catálogo."),
            ], deck="list"),
        Section("working_dropfiles", "HEREDADO DE v1.83.0", "Un listener para cada archivo que sueltas",
            "Con tag y publicado el 14 de octubre: un archivo soltado nunca da error, nunca se abre como texto por equivocación y nunca hace salir de la página.",
            body=[
                "Soltar un .json de MCP en el chat antes reportaba un error, en el canvas se abría como texto plano y "
                "mataba la importación, y en cualquier otra página el browser se iba al archivo. Ahora un solo listener está en "
                "el head del chat, de ambos paneles, de las páginas de bienvenida y de inicio de sesión, de las páginas de admin y del frame "
                "del visor de PDF, como describe la sección Soltar archivos. Sólo toma arrastres de archivos.",
                "Decide por los bytes, no por el nombre, y envía cada tipo a su propio mecanismo: un .json de MCP a una "
                "confirmación y al catálogo de External MCPs, un flow .flw o .fpmt a su editor, una imagen al "
                "mensaje, un PDF, Markdown o archivo de código al canvas del chat, y cualquier otra cosa a una explicación sencilla.",
                "Reemplazó cuatro manejadores por página. Revisado con 138 revisiones del router contra el script real, 22 pruebas "
                "nuevas de Django y una ejecución visible en Chrome de 58 revisiones con 24 fotos de Shoter, todo el 14 de octubre.",
            ],
            points=[
                ("Un solo listener", "Fase de captura, sólo arrastres de archivos; los arrastres de texto no se tocan."),
                ("Por los bytes", "Extensión, MIME, números mágicos, prueba de texto que conoce el BOM, parseo real de JSON."),
                ("Importación de MCP", "Nunca silenciosa: una confirmación lista primero los servidores."),
                ("En todas partes", "Chat, ambos paneles, bienvenida, inicio de sesión, admin y el frame de PDF."),
                ("Evidencia", "138 revisiones del router, 22 pruebas, 58 revisiones visibles, 24 fotos."),
                ("Tag", "v1.83.0 en a2914019, con push y publicado el 14 de octubre."),
            ], deck="cards"),
        Section("working_dockedavatar", "HEREDADO DE v1.83.0", "El retrato se encoge con la caja de mensaje",
            "Commit 63a62cc1 del 13 de octubre, acreditado a Tlamatini's-AutoBot; incluido en v1.83.0.",
            body=[
                "El divisor sobre la caja de mensaje antes reservaba el ancho actual del retrato como la altura mínima "
                "de la caja, así que un retrato ancho no dejaba que la caja se encogiera. Ahora reserva sólo un retrato de 120 píxeles "
                "más sus controles, y el retrato acoplado sigue al divisor: su lado es el menor entre "
                "un cuarto del ancho del formulario y la altura sobre la fila de Enviar y Micrófono, nunca de menos de 120 píxeles.",
                "Con la ventana inicial de 1440 píxeles el retrato pasó de 282 a 120 píxeles, y le regresó unos 162 "
                "píxeles al historial del chat. Pasaron diecinueve puntos de revisión del avatar acoplado y los dieciocho puntos "
                "de revisión existentes del composer en una ventana visible de Chrome.",
            ],
            points=[
                ("Abajo", "Arrastrar el divisor hacia abajo encoge el retrato a un cuadrado de 120 píxeles."),
                ("Arriba", "Arrastrarlo hacia arriba le regresa espacio al retrato, hasta su columna original."),
                ("Teclado", "Flechas, Shift+flechas, Inicio, Fin, doble clic y Escape siguen funcionando."),
                ("Evidencia", "Pasaron 19 puntos de revisión del avatar acoplado y 18 del composer."),
            ], deck="cards"),
        Section("working_aftertag", "HEREDADO DE v1.83.0", "Una solicitud mal redactada no es fatal",
            "Commit 91ff8453 del 12 de octubre, acreditado a Tlamatini's-AutoBot; incluido en v1.83.0.",
            body=[
                "Cuando el lanzador rechaza una llamada a Image-Interpreter o a Video-Analyzer antes de que arranque el agent, "
                "porque una configuración no existe o falta una obligatoria, el rechazo se marca como un "
                "error de la solicitud. Ya no levanta el diálogo rojo de análisis fatal ni su sonido; el modelo "
                "simplemente corrige la llamada. Una falla real de arranque sigue levantando el diálogo.",
                "La descripción de Video-Analyzer ahora dice que no tiene configuración de motor de transcripción, que le pertenece "
                "a Whisperer. Cinco pruebas nuevas fijan el comportamiento, y llega a las instalaciones con v1.83.0.",
            ],
            points=[
                ("Errores de solicitud", "Rechazados antes de que corriera algún modelo; el modelo reintenta."),
                ("Fallas reales", "Siguen levantando el diálogo fatal acumulado."),
                ("Sin configuración de motor", "engine= le pertenece a Whisperer, no a Video-Analyzer."),
                ("Pruebas", "Cinco pruebas en RequestRefusalIsNotFatalTests."),
            ], deck="cards"),
        Section("working_setup", "HEREDADO DE v1.82.0", "Instalar y quitar con vuelta atrás",
            "Con tag y publicado el 12 de octubre: ventanas de instalación nuevas, y Markdown que se abre como página.",
            body=[
                "El Instalador y el Desinstalador comparten una ventana que prepara y verifica una copia de recuperación "
                "antes de cambiar cualquier archivo, restaura una ejecución interrumpida, nombra un archivo bloqueado y deja cada "
                "error en pantalla con Reintentar, como describe la sección Ventanas de instalación. Los archivos Markdown ahora se abren "
                "en el canvas del chat como una página renderizada con su source intacto.",
                "El release se publicó en GitHub el 12 de octubre y fue el más reciente hasta que v1.83.0 lo reemplazó "
                "el 14 de octubre. Su zip era un build de self-modify cuyo paquete llevaba las ventanas de instalación, el "
                "canvas de Markdown, el tema compartido de v1.80.0 y los links web de v1.79.0. No hay tag v1.81.0.",
                "La campaña de instalación corrió de forma visible el 11 y el 12 de octubre: pasaron 52 puntos de revisión de la interfaz, 28 revisiones "
                "de recuperación, 21 revisiones de ciclo de vida y 61 pruebas de mecánica, con cinco instalaciones reales y "
                "cuatro eliminaciones reales que pasaron sus auditorías independientes. El canvas de Markdown pasó 30 de 30 "
                "puntos de revisión visibles. La campaña no instaló el zip publicado.",
            ],
            points=[
                ("Ventanas de instalación", "Una ventana recuperable para instalar y quitar."),
                ("Markdown", "Vista previa renderizada, Source original, sanitizador sin conexión."),
                ("Publicado", "12 de octubre; el release más reciente hasta v1.83.0."),
                ("Sin v1.81.0", "Ese número se saltó; v1.80.0 y v1.79.0 vienen antes."),
                ("Campaña", "Pasaron cinco instalaciones y cuatro eliminaciones; una eliminación se detuvo de forma segura."),
                ("Seguido de", "v1.83.0, del 14 de octubre, lleva los tres cambios posteriores."),
            ], deck="cards"),
        Section("working_onelook", "HEREDADO DE v1.80.0", "Un aspecto y una forma de arrastrar",
            "Con tag del 11 de octubre sin release propio; llega a los usuarios por medio de v1.82.0 y v1.83.0.",
            body=[
                "Cada página propia ahora toma de un solo juego de design tokens, y los cinco divisores de paneles "
                "comparten una manija y un modelo de gestos, como describe la sección Un solo aspecto. Primero se hizo que el divisor "
                "lateral coincidiera con el divisor del composer, y luego todo el sitio lo siguió esa misma noche.",
                "La campaña del source pasó 175 pruebas con dos saltos por plataforma, 17 puntos de revisión del composer, 38 "
                "puntos de revisión de zoom y adaptables del 25 al 400 por ciento, 13 puntos de revisión de comentarios y las ocho "
                "direcciones de cambio de tamaño de diálogos, en una ventana visible de Chrome. Certifica las páginas del source, no una "
                "respuesta del modelo ni un build instalado.",
            ],
            points=[
                ("Tag", "v1.80.0 en 82099963, con push; sin release publicado."),
                ("Tokens", "Superficies de pizarra, acento verde azulado, un juego de fuentes, una barra de desplazamiento."),
                ("Divisores", "Cinco uniones, una manija, flechas y Shift, Inicio y Fin."),
                ("Diálogos", "Cambio de tamaño en ocho direcciones y con teclado; botones que combinan."),
                ("Evidencia", "175 pruebas y revisiones visibles de zoom, composer y diálogos."),
                ("Entregado por", "Los releases publicados v1.82.0 y v1.83.0."),
            ], deck="cards"),
        Section("working_links", "HEREDADO DE v1.79.0", "Video-Analyzer acepta un link web",
            "Con tag del 11 de octubre sin release propio; llega a los usuarios por medio de v1.82.0 y v1.83.0.",
            body=[
                "Con un link de YouTube u otro sitio web, Video-Analyzer descarga un elemento por sí mismo: sólo el sonido "
                "para una transcripción, la imagen para un resumen o una revisión de robótica. Tiene un descargador privado "
                "que se actualiza solo, lo actualiza una vez y reintenta cuando falla una descarga, une imagen "
                "y sonido sin ffmpeg, y nombra cada error en vez de devolver silencio.",
                "El parser del chat ya no confunde el ?v= de un link con una configuración, una solicitud escrita en palabras "
                "sencillas llena el link y el modo, y el resultado agrega la dirección y el título de la fuente. Al "
                "modelo se le dice que pase los links a Video-Analyzer y que nunca instale un descargador por sí mismo. "
                "Pasaron 141 pruebas unitarias y una ejecución visible del chat de 12 de 12 el 11 de octubre.",
            ],
            points=[
                ("Un elemento", "Sonido para la transcripción, imagen para el resumen o la robótica."),
                ("Se actualiza solo", "Un descargador privado, renovado una vez cuando falla."),
                ("Errores con nombre", "No disponible, requiere inicio de sesión, red, tiempo agotado y más."),
                ("Funciona con prosa", "Las solicitudes en lenguaje sencillo llenan el link y el modo."),
                ("Evidencia", "141 pruebas unitarias y una ejecución visible del chat de 12 de 12."),
                ("Entregado por", "Los releases publicados v1.82.0 y v1.83.0."),
            ], deck="cards"),
        Section("working_usage", "HEREDADO DE v1.78.0", "Uso: créditos y actividad, mientras trabaja",
            "Con tag del 10 de octubre; el commit de Uso llega un commit después del tag. El zip publicado de v1.78.0 lo lleva.",
            body=[
                "La primera campaña del 10 de octubre pasó 18 pruebas de Uso, 202 regresiones existentes y 24 revisiones visibles "
                "en el browser, además de la paridad byte por byte entre el source y los estáticos recolectados. La cuenta Pro en vivo se comparó "
                "con la Configuración de Ollama antes y después de una solicitud real al modelo, y Uso se abrió y se actualizó mientras "
                "esa solicitud corría. Los casos de otros planes, de errores y de cambio de cuenta usaron fixtures explícitamente sintéticos, "
                "no suscripciones en vivo de Free, Max o Unlimited.",
                "Una continuación ese mismo día hizo que Uso se recupere cuando Ollama arranca tarde. Los errores temporales de conexión, "
                "de tiempo agotado y de respuesta inválida ahora reintentan después de 15 segundos en vez de un minuto completo, un "
                "Retry-After del servidor se respeta incluso cuando se hace clic varias veces en Actualizar, y una conexión rechazada "
                "se vuelve a revisar de inmediato al Actualizar o al reabrir. Pasó 27 pruebas de Uso y 12 "
                "revisiones visibles en el browser: Actualizar se recuperó en 0.47 segundos, reabrir en 0.52 segundos y el "
                "reintento automático en 15.02 segundos.",
                "UsageDaily, la migración 0213, registra contadores por usuario/modelo/día UTC con una cola de worker "
                "acotada; es telemetría de mejor esfuerzo, no un libro de facturación. Pasaron los dos barridos de inclusión. Esas "
                "campañas corrieron desde el source. Esta actualización revisó que el zip publicado coincide con el build local "
                "byte por byte (SHA-256); no instaló el release ni volvió a correr las pruebas del browser.",
            ],
            points=[
                ("220 pruebas", "Pasaron 18 de Uso más 202 regresiones existentes el 10 de octubre."),
                ("24 revisiones en el browser", "Comparaciones visibles en vivo con Pro más casos límite claramente sintéticos."),
                ("Recuperación", "27 pruebas de Uso y 12 revisiones visibles; las caídas se reintentan después de 15 s."),
                ("Durante una solicitud", "Uso se abrió/actualizó mientras se completaba una respuesta real del modelo."),
                ("En el release", "Los archivos del zip publicado coinciden con el último commit del 10 de octubre."),
                ("Privacidad", "Las observaciones de la cuenta y los screenshots autenticados se quedan fuera de este dossier."),
            ], deck="cards"),
        Section("working_composer", "HEREDADO DE v1.78.0", "Desacóplala y la caja de mensaje se encoge",
            "Dos commits después del tag v1.78.0, y llevado por el zip publicado: el área de input cambia de tamaño cuando ella flota.",
            body=[
                "Con el avatar desacoplado, el formulario de input ahora se puede arrastrar hacia abajo hasta sus propios botones de acción más "
                "un margen de seis píxeles; el viejo piso del 30% desapareció. La barra de herramientas, el medidor de contexto y las filas de adjuntos y de dictado "
                "cuentan con sus alturas medidas. Volver a acoplarla restaura el espacio para el retrato. El "
                "divisor responde al puntero, a las flechas, a Shift+flechas, a Inicio, a Fin y al doble clic, y "
                "le reporta su altura a los lectores de pantalla.",
                "Las ventanas bajas desplazan el composer dentro de sí mismo y conservan el historial del chat. La página ocupa el "
                "viewport real: la navegación colapsada se abre sobre el espacio de trabajo en vez de empujarlo hacia abajo, y un "
                "espacio de trabajo mínimo de 640 píxeles conserva ambos paneles en pantallas angostas. Los diálogos de jQuery UI se quedan dentro de la "
                "ventana después de abrirse, arrastrarse o cambiar de tamaño, los diálogos nativos bajos se desplazan como tarjetas completas, y el "
                "avatar nunca tapa un diálogo modal.",
                "En una ventana verificada de Chrome en primer plano pasaron 18 revisiones del composer y 38 revisiones del viewport al 100%, "
                "con zoom nativo de 400% y de 25% y en una ventana del tamaño de un teléfono, con ocho diálogos en cada tamaño. Es un "
                "browser de escritorio con dimensiones de teléfono, no un teléfono físico; el zoom de 20% no estaba disponible y no "
                "se afirma. Estas revisiones de distribución no certifican la inferencia del modelo ni la captura de audio.",
            ],
            points=[
                ("Se encoge para caber", "Desacoplado, el área de input se puede encoger hasta sus botones; sin piso del 30%."),
                ("Acoplar de nuevo", "Acoplarla restaura el espacio para su retrato sobre los botones."),
                ("Teclado", "Flechas, Shift+flechas, Inicio, Fin y doble clic en el divisor."),
                ("Ventanas bajas", "El composer se desplaza dentro de sí mismo; el historial del chat sigue visible."),
                ("Pantallas angostas", "Un espacio de trabajo de 640 píxeles se desplaza; la página y los diálogos se quedan anclados."),
                ("Evidencia", "Pasaron 18 revisiones del composer y 38 del viewport, de forma visible, el 10 de octubre."),
            ], deck="cards"),
        Section("working_selfrepair", "HEREDADO DE v1.78.0", "Reparó uno de sus propios agents",
            "Image-Interpreter ahora lee una lista de imágenes separada por comas, un cambio acreditado a la propia Tlamatini.",
            body=[
                "El commit 0e6fc72d se titula \u201cTlamatini's self-repair Image-Interpreter, by Tlamatini's-AutoBot\u201d "
                "y es el commit al que apunta el tag v1.78.0. Cuando el campo de imágenes tiene varios paths "
                "separados por comas, cada entrada se resuelve por su cuenta, los resultados se combinan, y los paths "
                "repetidos se quitan conservando el orden original.",
                "La lista se divide sólo cuando el valor completo no es en sí un archivo existente, así que una sola imagen "
                "cuyo nombre contiene una coma sigue resolviéndose. Una entrada que no coincide con nada se registra como advertencia "
                "y las demás imágenes se siguen analizando. El cambio de 22 líneas llegó sin una nueva prueba "
                "automatizada; se incluye en el release publicado v1.78.0.",
            ],
            points=[
                ("Varias imágenes", "Los paths separados por comas se resuelven uno por uno y se combinan."),
                ("Sin duplicados", "Los paths repetidos se quitan; se conserva el orden original."),
                ("Comas en los nombres", "Un solo archivo existente nunca se divide en su coma."),
                ("Advertencia honesta", "Una entrada que no se resuelve a nada se registra, no se esconde."),
                ("Autorreparación", "El commit acredita a Tlamatini's-AutoBot, su propio trabajo de self-modify."),
                ("En v1.78.0", "El tag apunta a este commit; todavía sin prueba dedicada."),
            ], deck="cards"),
        Section("working_firstperson", "HEREDADO DE v1.77.0", "Te habla a ti, por tu nombre",
            "Con tag y publicado el 9 de octubre; v1.78.0 lo reemplazó como el release Latest el 10 de octubre.",
            body=[
                "Cada línea fija que Tlamatini envía al chat, y que su avatar lee en voz alta, ahora está escrita en "
                "primera persona y dirigida al usuario por su nombre: “¡Estoy lista, Angela! Ya puedes empezar a platicar "
                "conmigo.” reemplaza a “Tu agent está listo.” Las líneas viven en un solo lugar, `agent/constants.py`; un helper "
                "llena el primer nombre, o el nombre de usuario cuando no hay primer nombre, y quita el nombre "
                "limpiamente cuando no hay ninguno.",
                "Algunas de estas líneas se reconocen por sus palabras: la página del chat las usa para saber si está ocupada o "
                "lista, el avatar para decidir qué decir, y el puente de Telegram para filtrar sus respuestas. Cada uno "
                "de esos reconocedores cambió en el mismo commit y sigue aceptando la redacción vieja, así que un historial "
                "de chat guardado y un servidor más viejo se siguen leyendo correctamente.",
                "El desinstalador ya no borra el trabajo propio del usuario. Desinstalar una instalación había borrado los "
                "proyectos guardados en `Templates/`, donde STM32er, ESP32er, Arduiner, ESPHomer, Unrealer y LaTeXer "
                "crean sus proyectos de forma predeterminada. Ahora conserva `application`, `applications`, `content_generated`, "
                "`context_files`, `doc_generated` y `Templates` siempre que tengan un archivo, siempre borra `Temp/`, "
                "y sigue conservando `agents/`. Sólo un Uninstaller.exe recompilado lleva esto: una instalación nueva o una "
                "reinstalación lo copia, mientras que una actualización desde la app conserva el viejo.",
                "Ambos cambios están cubiertos por pruebas unitarias (las pruebas de mensajes en `test_compact_mode_switch.py` y "
                "`test_uninstaller_mechanics.py`), registradas como aprobadas en la actualización de la documentación del 9 de octubre.",
            ],
            points=[
                ("Primera persona", "Las líneas fijas del chat dicen “yo” y usan tu nombre."),
                ("Una sola fuente", "Cada línea fija vive en agent/constants.py."),
                ("Redacción vieja conservada", "Los reconocedores aceptan ambas, así que los historiales viejos se siguen leyendo."),
                ("Templates conservado", "Desinstalar conserva los proyectos en Templates/."),
                ("Temp borrado", "Lo temporal se va; las carpetas con tus archivos se quedan."),
                ("Desinstalador recompilado", "Una reinstalación lleva el arreglo; una actualización desde la app no."),
            ], deck="cards"),
        Section("working_brain", "HEREDADO DE v1.76.0", "El Model Brain ajusta cada modelo",
            "Con tag del 8 de octubre; el commit del Model Brain llega a main un commit después del tag. El release "
            "publicado v1.76.0 se construyó desde main y lo lleva.",
            body=[
                "Cada modelo que Tlamatini llama ahora recibe su propio muestreo, nivel de razonamiento y tamaño de contexto a partir de "
                "fuentes formales, como describe el capítulo Cómo funciona. Config ▸ Modelos ▸ Guardar abre un "
                "diálogo de Autoajuste que ajusta cada modelo configurado frente a ti, los modelos que razonan conservan su "
                "propio razonamiento entre llamadas a tools dentro de una respuesta, y los relojes de bloqueo que tiraban trabajo terminado "
                "desaparecieron.",
                "La ventana de la consola pinta cada línea según su nivel: errores en rojo, errores fatales en blanco sobre rojo, advertencias "
                "en amarillo, debug en gris y éxitos en verde, mientras que `tlamatini.log` se queda en texto plano. Al arrancar ella "
                "registra qué programa dibuja la ventana, la consola clásica o Windows Terminal, la predeterminada en "
                "Windows 11. `console_colors` y la variable estándar `NO_COLOR` apagan los colores.",
                "Dos reparaciones más pequeñas vienen junto. Un PDF rechazado porque una segunda cuenta inició sesión desde el "
                "mismo browser ahora nombra esa causa y el arreglo, recargar con F5, y el diálogo de progreso marca "
                "el paso con error. Dos páginas de chat con dos modelos distintos ya no se hacen volver a medir una a la otra "
                "para siempre: el veredicto de un modelo actualiza las casillas y se detiene. En dos páginas de prueba inactivas los reenvíos bajaron "
                "de 1,081 en un minuto a ninguno.",
                "El 8 de octubre la prueba visible del Model Brain pasó 25 de 25 revisiones en una ejecución desde el source y la prueba visible "
                "de la cuenta del PDF pasó 20 de 20. Son resultados fechados, no una afirmación de que esta actualización "
                "de la documentación los volvió a correr. El estado de publicación se indica en la sección Identidad del release.",
            ],
            points=[
                ("Model Brain", "Configuración por modelo a partir de fuentes citadas; Autoajuste muestra cada una."),
                ("Razonamiento conservado", "Los modelos que piensan conservan su hilo de pensamiento entre llamadas a tools."),
                ("Consola a colores", "Líneas coloreadas por nivel; el archivo de log se queda en texto plano."),
                ("Rechazo veraz", "Un PDF rechazado por una segunda cuenta dice por qué y cómo arreglarlo."),
                ("Pestañas tranquilas", "Dos páginas con dos modelos ya no se vuelven a medir una a la otra."),
                ("Evidencia", "25 de 25 y 20 de 20 revisiones visibles el 8 de octubre."),
            ], deck="cards"),
        Section("working_truth", "HEREDADO DE v1.76.0", "Documentos y archivos que dicen la verdad",
            "7 y 8 de octubre: LaTeXer, Mover y los agents de documentos reportan lo que de verdad pasó.",
            body=[
                "LaTeXer reporta un PDF sólo cuando el archivo entregado de verdad existe y no está vacío, y un PDF cuyo "
                "texto sobresale más de cinco puntos del margen se reporta como creado con hallazgos, no "
                "como limpio. Cuando tuvo que cortar una cuarta parte o más del cuerpo de un documento roto para producir algún PDF, "
                "guarda el resultado como `<name>.DEGRADED.pdf` y deja intacto el nombre pedido. En un "
                "documento de más de 8,000 caracteres el peldaño del modelo primero repara sólo las líneas alrededor del "
                "error del compilador con una solicitud acotada; una respuesta inútil vuelve a la solicitud del documento "
                "completo, y una respuesta que nunca llegó prohíbe el peldaño bisect.",
                "Mover ya no borra una carpeta de destino para copiar en ella: las carpetas se combinan, cada archivo se "
                "prepara y se publica completo, un movimiento quita su origen sólo después, y un error termina con un "
                "recibo de error y una salida distinta de cero en vez de un éxito. Los agents de documentos y de captura conservan un "
                "archivo terminado cuando el Controlled Folder Access de Windows bloquea la carpeta, y el script de lista blanca "
                "de seguridad ahora encuentra cada instalación de Tlamatini y deja que su Python guarde archivos.",
                "El cambio de LaTeXer del 8 de octubre agregó 37 pruebas, y las 549 pruebas de LaTeXer pasaron con él. El trabajo de entrega "
                "de Mover y LaTeXer del 7 de octubre pasó 126 pruebas enfocadas.",
            ],
            points=[
                ("PDFs reales", "Éxito sólo cuando el archivo entregado existe y no está vacío."),
                ("Hallazgos de distribución", "El texto que pasa el margen se reporta, nunca se llama limpio."),
                ("Nombre DEGRADED", "Un build mayormente recortado nunca lleva el nombre que pediste."),
                ("Reparación por región", "Documentos grandes: primero se reparan las líneas alrededor del error."),
                ("Mover", "Los destinos se combinan, nunca se borran; los errores se reportan."),
                ("Carpetas protegidas", "Los archivos terminados sobreviven a Controlled Folder Access."),
            ], deck="cards"),
        Section("working_fixes", "EN v1.76.0 · 5 Y 8 DE OCTUBRE", "Arreglos que mantienen el chat en marcha",
            "Hechos commit después del tag v1.75.0 y llevados por el tag v1.76.0.",
            body=[
                "Los helpers Files-Search y System-Metrics le hacen a Ollama sus propias preguntas antes de la respuesta principal. "
                "Esas llamadas ahora tienen un límite de tiempo, `context_sidecar_llm_timeout_seconds`, 60 segundos de forma predeterminada; "
                "al llegar al límite, o cuando presionas Cancelar, un helper se salta su contexto y la respuesta sigue adelante, así que una "
                "respuesta lenta ya no puede congelar el chat.",
                "Cuando Windows todavía tiene tomado `Uninstaller.exe` mientras el desinstalador termina, el archivo se reintenta, "
                "se mueve aparte y lo borra una limpieza oculta después de salir, así que la desinstalación se completa. File-Creator "
                "ganó `append`: true agrega el contenido al final de un archivo, byte por byte, en vez de "
                "sobrescribirlo.",
            ],
            points=[
                ("Helpers de contexto", "Sus propias llamadas al modelo se detienen en un límite de tiempo o con Cancelar."),
                ("Desinstalador", "Un Uninstaller.exe tomado se mueve aparte y se quita después de salir."),
                ("File-Creator", "`append: true` agrega a un archivo en vez de sobrescribirlo."),
            ], deck="cards"),
        Section("working_canvas", "EN v1.76.0 · 4 DE OCTUBRE", "Notas gráficas y Output ajustable",
            "Hecho commit a main el 4 de octubre y llevado por el tag v1.76.0; los ejecutables locales se recompilaron para validarlos.",
            body=[
                "Comentario del usuario se edita por completo en el canvas. Haz doble clic o presiona Enter para escribir, "
                "y luego da formato a las palabras seleccionadas con la mini barra de herramientas flotante. Una sola nota puede combinar "
                "distintas fuentes, tamaños, colores de texto, negritas, cursivas y subrayado. Un cursor da estilo al siguiente "
                "texto que escribes. El color y la alineación de la burbuja se aplican a toda la nota.",
                "Arrastra cualquier borde o esquina, incluso mientras escribes. Ajustar al texto quita la altura sobrante. "
                "Cada línea ajustada se queda dentro de la burbuja sin una barra de desplazamiento interna. Listo o "
                "Ctrl+Enter guarda la edición. Cancelar o Escape restaura su texto, estilos, tamaño y posición.",
                "El divisor sobre Output de la ejecución asigna del 5% al 95% de la altura útil del canvas/output. "
                "Sólo cambian las dos áreas visibles. El zoom del canvas, las dimensiones de las figuras y los tamaños de texto se quedan fijos, "
                "y cada panel se desplaza de forma independiente. El browser recuerda la proporción por usuario con sesión iniciada.",
                "La verificación de comentarios del 4 de octubre pasó 29 pruebas de diagrama/ejecutor, 3 pruebas de transporte "
                "y 23 puntos de revisión visibles en Chrome, incluidos tres comentarios con estilos mezclados a lo largo de tres "
                "ciclos de guardar/abrir el archivo con datos idénticos y cajas de líneas renderizadas idénticas. La verificación del divisor "
                "del output pasó por separado 14 puntos de revisión visibles en Chrome y 3 pruebas de transporte. "
                "Son resultados fechados, no una afirmación de que esta actualización de la documentación los volvió a correr.",
            ], deck="list", deck_points=[
                ("Notas enriquecidas", "El texto seleccionado conserva sus propias fuentes, tamaños, colores y énfasis."),
                ("Edición directa", "Herramientas flotantes y cambio de tamaño por todos los bordes. Sin diálogo de comentarios."),
                ("Output de la ejecución", "Del 5% al 95% de la altura. Desplazamiento independiente con los tamaños del contenido conservados."),
                ("Fidelidad de archivos", "Tres notas con estilos mezclados se renderizaron igual en tres ciclos de guardar/abrir."),
                ("Entrega", "Hecho commit el 4 de octubre y llevado por v1.76.0; los builds se validaron por separado."),
            ]),
        Section("working_main", "EN v1.76.0 · 3 DE OCTUBRE", "Cuatro paradas y un Prompt Flow Panel más claro",
            "Hecho commit en main después del tag v1.75.0 y llevado por el tag v1.76.0.",
            body=[
                "Los modelos en la nube de Ollama rechazan una solicitud que lleva más de cuatro secuencias de parada, y el modelo "
                "del chat antes enviaba nueve, así que el resumen del historial del chat, la primera llamada cuando una conversación se vuelve "
                "larga, hacía fallar toda la solicitud. Ahora cada lista de paradas pasa por un solo ajustador que conserva "
                "cuando mucho cuatro, las más importantes primero, y un resumen con error ya no hace fallar la respuesta: la solicitud "
                "sigue sin él, mientras que Cancelar todavía la detiene.",
                "El Prompt Flow Panel separa dos cosas que compartían un nombre. Input del usuario es la operación "
                "que se detiene a preguntarte algo; conserva exactamente su comportamiento anterior con una nueva figura de muesca. "
                "Comentario del usuario ahora es una nota estática en burbuja de diálogo para quien revisa: escrita en su lugar, con color "
                "y estilo libres, crece para contener todo su texto sin barra de desplazamiento, y nunca se ejecuta. Los archivos "
                "nuevos se guardan como versión 2; los archivos de la versión 1 se abren con sus viejos pasos de comentario convertidos en "
                "Input del usuario, conservando identificadores y conexiones.",
                "La actualización del 3 de octubre volvió a correr 430 pruebas unitarias enfocadas, la revisión sin conexión del Prompt Flow, ESLint con cero "
                "errores, el inventario de skills y los dos barridos de inclusión; todo pasó, y ruff ahora reporta un "
                "árbol limpio. En un Chrome visible en el escritorio real, la prueba de comentarios pasó los nueve "
                "puntos de revisión: notas largas sin barras de desplazamiento, fuentes y colores, cambio de tamaño con Deshacer y Rehacer, "
                "guardar y reabrir, una ejecución real de Input del usuario, Escape deteniéndola y un archivo de versión 1 migrando.",
            ],
            points=[
                ("Cuatro secuencias de parada", "Cada solicitud a Ollama; un resumen con error nunca hace fallar la respuesta."),
                ("Input del usuario", "El paso que te pregunta: mismo mecanismo, nueva figura."),
                ("Comentario del usuario", "Una nota estática de revisión; nunca se ejecuta y nunca llega al modelo."),
                ("Archivos versión 2", "Los flows de la versión 1 se migran al abrirse; se conservan los identificadores y los enlaces."),
                ("Evidencia del 3 de octubre", "430 pruebas unitarias; 9 de 9 puntos de revisión visibles en Chrome."),
            ], deck="cards"),
        Section("working_switches", "HEREDADO DE v1.75.0", "Compact mode y Self-modify, ahora interruptores",
            "Con tag del 3 de octubre: Compact mode es un interruptor de la barra de herramientas; el interruptor Self-modify vino después y se incluye en v1.76.0.",
            body=[
                "Compact mode, tal como quedó en el tag v1.74.0, era un veredicto tomado a espaldas del usuario. En v1.75.0 es "
                "una casilla de la barra de herramientas. Marcarla desmarca todas las filas en Configurar MCPs, Configurar Agents y "
                "ACPX-Skills excepto System-Metrics, Files-Search y Current-Time, y pausa los External "
                "MCPs; desmarcarla vuelve a marcar todas las filas. Cada fila muestra los tokens que agrega, un modelo que "
                "no puede contenerlo todo enciende la casilla y la bloquea, y una respuesta construida a partir de una solicitud recortada "
                "lleva una advertencia CONTEXT-WINDOW.",
                "Justo después del tag, el commit 70aeeb87 agregó la casilla Self-modify, que se incluye en v1.76.0. Una ejecución "
                "desde el source siempre la muestra; "
                "un build congelado la muestra sólo cuando se construyó con --self-modify. Encendida, envía su autoconocimiento, "
                "unos 28,900 tokens por solicitud; apagada, una línea le dice que no cambie su propio código. Un modelo "
                "que no puede contenerlo muestra la casilla bloqueada en apagado.",
                "La ejecución visible del interruptor Compact pasó 57 de 57 revisiones con un qwen2.5 local y un modelo gratuito en la nube. "
                "La ejecución visible de Self-modify pasó 28 de 28: con los mismos 119 tools, la solicitud con "
                "el autoconocimiento fue 117,517 bytes más grande que sin él. Pasaron 473 pruebas unitarias, incluido "
                "un renderizado de la página como build congelado.",
            ],
            points=[
                ("Interruptor Compact", "Sólo las filas que marcas; bloqueado en encendido cuando el modelo no puede contenerlo todo."),
                ("Precios", "Cada fila de Configurar muestra los tokens que agrega a cada solicitud."),
                ("Self-modify", "Su autoconocimiento encendido o apagado; bloqueado en apagado cuando no cabe."),
                ("Prueba", "57/57 y 28/28 revisiones visibles; 473 pruebas unitarias."),
            ], deck="cards"),
        Section("working_compact", "HEREDADO DE v1.74.0", "Compact mode y tablas legibles",
            "Con tag del 1 de octubre: cada solicitud se ajusta al modelo al que se envía.",
            body=[
                "Un modelo que puede contener la solicitud completa de Tlamatini sigue recibiéndola byte por byte. Un modelo "
                "cuya ventana real es más pequeña recibe Compact mode, que describe el capítulo Cómo funciona, "
                "con un diálogo una vez por modelo, una insignia Compact y una casilla ACPX bloqueada, reemplazados en v1.75.0 por un interruptor.",
                "La ejecución visible con un qwen2.5 local expuso tres problemas más, arreglados en el mismo release. En "
                "Compact mode la protección de archivos de una sola ejecución ahora dice la razón real por la que no se puede abrir un archivo, y una "
                "tabla que el usuario pidió ver se muestra como tabla en vez de como código cercado. Para cada modelo, una "
                "celda de tabla de respuesta cuyo texto sería ilegible se vuelve a colorear.",
                "El 1 de octubre la ejecución visible de Compact con el qwen2.5:latest instalado pasó 37 de 37 revisiones con "
                "unos 8,100 tokens por solicitud, sin recortes. Con nemotron-3-ultra:cloud cada solicitud se mantuvo "
                "completa, con Ollama leyendo de 102,539 a 104,259 tokens. Un modelo pequeño todavía puede a veces "
                "volver a contestar una pregunta anterior antes de la nueva. La actualización del dossier de v1.74.0 volvió a correr las 43 "
                "pruebas de regresión de Compact mode; todas pasaron.",
            ],
            points=[
                ("Ajustado", "Completo cuando el modelo puede contener la solicitud; Compact cuando no puede."),
                ("Prueba de Compact", "37/37 revisiones visibles con un qwen2.5 local, unos 8.1K tokens, sin recortes."),
                ("Prueba completa", "Un modelo grande en la nube leyó completa cada solicitud: unos 103K tokens."),
                ("Tablas legibles", "Las celdas con contraste menor a 3:1 se vuelven a colorear, para cada modelo."),
            ], deck="cards"),
        Section("working_catalog", "HEREDADO DE v1.73.1", "Modelos del servidor que configuraste",
            "Con tag del 1 de octubre: Config ▸ Modelos consulta a los servidores de Ollama configurados, con su token.",
            body=[
                "Config ▸ Modelos antes le pedía la lista de modelos al propio Ollama del browser, en una dirección fijada "
                "cuando cargaba la página. Después de que Config ▸ URLs apuntaba Tlamatini a un servidor remoto, un modelo "
                "instalado sólo ahí se marcaba en rojo y no se podía guardar.",
                "Un endpoint protegido por inicio de sesión ahora lee config.json en cada llamada, consulta en paralelo cada dirección distinta de "
                "Ollama configurada con el mismo bearer token que envía el chat, y combina los nombres de sus modelos. "
                "Cada servidor reporta su propio status, y el diálogo nombra el servidor y la razón "
                "cuando uno no puede contestar, como un HTTP 401 que apunta al token.",
                "El mismo release hizo que el paso de GPU al arrancar también envíe el token, así que un servidor remoto protegido por token "
                "ya no contesta 401 en cada arranque. Una ejecución visible contra un servidor simulado "
                "protegido por token pasó 16 de 16 revisiones, con cada solicitud llevando el token. La "
                "actualización del dossier de v1.74.0 volvió a correr las 18 pruebas de regresión del catálogo de modelos; todas pasaron.",
            ],
            points=[
                ("Dirección actual", "Se lee de config.json en cada llamada, nunca se fija al cargar la página."),
                ("Token", "Cada servidor configurado se consulta con el propio bearer token del chat."),
                ("Errores claros", "Cada servidor reporta su status; un 401 apunta al token."),
                ("Arranque", "El calentamiento de la GPU también envía el token: sin 401 en cada arranque."),
            ], deck="cards"),
        Section("working_drop", "HEREDADO DE v1.73.0", "Una tarjeta quitada del contexto futuro",
            "Con tag y publicado el 30 de septiembre: Descartar en todo el chat, con confirmación y actualización del historial.",
            body=[
                "Los saludos guardados, los prompts del usuario y las respuestas llevan su id de AgentMessage desde el primer renderizado "
                "de la página y en los frames de WebSocket que siguen. La solicitud drop-message valida ese id contra "
                "el dueño de la conversación con sesión iniciada antes de borrar filas. Una protección de ocupado revisa la ejecución "
                "activa de esta conexión; no es un bloqueo global entre todas las pestañas del usuario.",
                "Un borrado exitoso transmite message-dropped con todos los ids borrados a las pestañas del usuario, "
                "y luego programa una actualización del medidor de contexto. Descartar un prompt del usuario también quita hasta veinte "
                "filas de Referenced Rephrase que lo siguen directamente, y se detiene en la primera fila distinta. Una respuesta "
                "o el mensaje de otro usuario nunca se incluyen en esa limpieza.",
                "Las 23 pruebas de regresión enfocadas de Descartar pasaron el 30 de septiembre, cubriendo la propiedad, ambos roles de mensaje, las filas vecinas, "
                "la ventana del historial, el rechazo cuando está ocupada, los rephrases y los contratos del protocolo browser/servidor. El "
                "registro de mantenimiento del 30 de septiembre reporta 42/42 revisiones en el harness extendido visible del browser, "
                "incluido un nuevo conteo real de contexto después de cada descarte que termina más bajo que antes; "
                "esta actualización del dossier vuelve a correr la suite enfocada sin escribir en el grafo de memoria real.",
            ],
            points=[
                ("Filas propias", "El borrado en el servidor se limita a la conversación del usuario con sesión iniciada."),
                ("Pestañas y medidor", "Los ids confirmados quitan las tarjetas guardadas en todas las pestañas y actualizan la estimación de contexto."),
                ("Copias de rephrase", "La limpieza del prompt quita las copias de rephrase que siguen y conserva la respuesta."),
                ("Protección de ejecución", "Una respuesta activa bloquea Descartar en esa conexión. Otras pestañas tienen ejecuciones aparte."),
            ], deck="cards"),
        Section("working_web", "HEREDADO DE v1.72.4", "Páginas web que no desaparecen en silencio",
            "Con tag y publicado el 29 de septiembre: ninguna página web pierde su texto sin decirlo.",
            body=[
                "Crawler y Googler reducen una página a sus palabras saltándose scripts, estilos y bloques "
                "parecidos. Un bloque que nunca se cerraba, como una etiqueta de cierre de head omitida o una "
                "descarga cortada, antes se tragaba el resto de la página. Ahora ambos siguen los bloques abiertos con una pila, "
                "y una red de seguridad de texto plano reemplaza cualquier resultado que conservó muy poco, registrando una advertencia "
                "cuando lo hace.",
                "Dos tags viajan con él. v1.72.2 agregó valores predeterminados con plazos a ambos agents, y un "
                "CAPTCHA o un muro de bots se reporta como bloqueado, nunca se lee como contenido. "
                "v1.72.3 hizo que los labios del avatar del chat se movieran claramente mientras habla, nunca más abiertos que su "
                "propio retrato.",
            ],
            points=[
                ("Sin pérdida silenciosa", "Una pila de etiquetas abiertas reemplaza a un contador en ambos agents."),
                ("Red de seguridad", "Una lectura simple toma el control cuando un parseo conserva muy poco."),
                ("Valores acotados", "v1.72.2: presupuestos de búsqueda y de crawl, cancelación y resultados explícitos."),
                ("Rechazos con nombre", "Un CAPTCHA o un muro de bots regresa como bloqueado, nunca como contenido."),
                ("Labios visibles", "v1.72.3: sus labios se abren y se cierran claramente, sin quedarse muy abiertos."),
            ], deck="cards"),
        Section("working_gauge", "HEREDADO DE v1.72.1", "Un medidor de contexto veraz",
            "Con tag y publicado el 28 de septiembre: el anillo junto a la caja de mensaje muestra el propio conteo de Ollama.",
            body=[
                "El anillo ahora reporta la solicitud exacta que envía la cadena principal de Tlamatini. Los bytes se miden; "
                "la cifra de tokens es el propio prompt_eval_count de Ollama para esa solicitud, y el tope es la "
                "longitud de contexto que reporta Ollama. Una estimación se muestra sólo hasta que Ollama contesta, y lo dice.",
                "Entre preguntas el anillo muestra lo que va a costar la siguiente solicitud, recalculado cada vez que cambia el "
                "estado: al abrir la página, al Limpiar historial, al Descartar, al Limpiar contexto, al cargar un contexto, al terminar una respuesta "
                "o al cambiar un modo. Es exacto tanto en una sola ejecución como en Multi-Turn, por usuario conectado, y "
                "las preguntas de una sola ejecución ya no llevan una línea vacía de System-Metrics.",
            ],
            points=[
                ("Tokens reales", "El prompt_eval_count de Ollama, emparejado con su propia solicitud."),
                ("Exacto en ambos modos", "En vivo = predicción en reposo + la pregunta + el plan de Multi-Turn."),
                ("Sólo la cadena principal", "Las llamadas fuera de banda nunca llegan al anillo; cada usuario ve las suyas."),
                ("Menos desperdicio", "La pregunta se envía una vez; la línea de relleno de una sola ejecución desapareció."),
                ("Prueba", "Un laboratorio visible pasó 60 de 60 revisiones contra tlamatini.log."),
            ], deck="cards"),
        Section("working_voice", "HEREDADO DE v1.72.0", "Dictado directo y dependencias",
            "Estos cambios del 27 de septiembre llevaron el tag v1.72.0 y se publicaron el 28 de septiembre.",
            body=[
                "El micrófono del chat arranca Whisperer directamente, se detiene en la compuerta de silencio configurada, "
                "reconoce la voz y envía o deja un borrador editable según lo elegido en Config > Micrófono. "
                "El diálogo también guarda preferencias locales del browser de entrada, ganancia, compuerta y reconocimiento. El worker usa el logger "
                "principal de la aplicación y no crea una segunda consola. Las pruebas de desarrollo siguen corriendo de forma visible.",
                "El manifiesto raíz de dependencias y el manifiesto aparte de ESPHome ahora contemplan las librerías referidas "
                "en los agents y en el source. La protección estática y la auditoría detallada de dependencias registran "
                "la cobertura y las fronteras del runtime. Se incluyeron en el release publicado v1.72.0; la "
                "reparación del transportador compartido de assets raíz que siguió está hecha commit y la lleva v1.72.1.",
            ],
            points=[
                ("Guía del usuario", "README.md y BookOfTlamatini.md explican la configuración de Micrófono, la grabación, la cancelación y ambos modos."),
                ("Contrato del runtime", "docs/chat-microphone-design.md registra la propiedad, el protocolo, la configuración y los límites."),
                ("Dependencias", "docs/dependency-coverage-audit.md registra las declaraciones, el aislamiento y la verificación."),
                ("Entrega", "Publicado como v1.72.0 y llevado por v1.72.1, con la reparación del transportador de assets raíz."),
            ], deck="cards"),
        Section("whatsnew", "RELEASE HEREDADO", "v1.70.0: el Prompt Flow Panel",
            "La versión 1.70.0 trata de diseñar conversaciones y editar flows con la misma facilidad.",
            points=[
                ("Prompt Flow Panel", "Siete operaciones, archivos `.fpmt`, ejecución validada, ejecuciones aisladas."),
                ("Paneles y Config", "Los canvases viven en Paneles; cada diálogo Configurar, en Config."),
                ("Un editor de verdad", "Deshacer y Rehacer, Duplicar con configuración, zoom, Ajustar, búsqueda de agents, Ayuda."),
                ("Mecánica compartida", "Ambos canvases conectan, arrastran, seleccionan y hacen zoom de la misma forma."),
                ("Menús a prueba de ocupación", "Paneles sigue disponible mientras ella contesta; un solo camino reactiva los menús."),
                ("Línea de contexto heredada", "El medidor de contexto, el Context Governor y el indicador de contexto de v1.65."),
            ], deck="cards"),
        Section("lineage", "LINAJE", "Cómo llegó la línea aquí",
            "Tags recientes, del más viejo al más nuevo, leídos de Git.",
            visual="timeline", deck="visual"),
        Section("identity_release", "IDENTIDAD DEL RELEASE", f"Una versión publicada: v{version}",
            "La aplicación, las guías del usuario, el PDF y el PowerPoint identifican el mismo release actual. "
            "Los metadatos del repositorio registran la implementación inspeccionada para este dossier.",
            body=f["release_statements"],
            table={"columns": ["Dato", "Valor"], "widths": [0.40, 0.60], "rows": f["release_rows"]},
            deck="split", deck_points=f["release_points"]),
    ])

    facts = Chapter("facts", "IX", "Datos del repositorio",
        "El árbol del source medido: archivos, lenguajes, líneas efectivas, los archivos más grandes y la historia reciente.",
        accent="copper", sections=[
        Section("facts_table", "INVENTARIO", "El repositorio en números",
            "Los conteos vienen de Git y de los archivos del source al momento de generarse.",
            table={"columns": ["Medida", "Valor"], "widths": [0.46, 0.54], "rows": f["fact_rows"]},
            deck="table"),
        Section("languages", "INVENTARIO DE LÍNEAS", "Líneas efectivas por lenguaje",
            f"{f['total_effective']:,} líneas efectivas en {f['text_files']:,} archivos de texto; "
            f"{f['total_physical']:,} líneas físicas.",
            visual="language_bars", deck="visual"),
        Section("language_table", "INVENTARIO DE LÍNEAS", "Cada lenguaje, contado",
            "Las líneas efectivas excluyen las líneas en blanco, las líneas que sólo tienen comentarios y los docstrings de Python.",
            table={"columns": ["Lenguaje", "Archivos", "Físicas", "Efectivas", "Proporción"],
                   "widths": [0.34, 0.12, 0.18, 0.18, 0.18], "rows": f["language_rows"],
                   "align": ["LEFT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"]},
            deck="table"),
        Section("authored", "PROCEDENCIA", "Escrito y de terceros",
            "Las librerías de frontend de terceros van incluidas para que la aplicación no necesite un CDN al ejecutarse; sus "
            "líneas se cuentan aparte aquí para que nunca se confundan con la lógica propia de Tlamatini.",
            table={"columns": ["Porción", "Archivos", "Líneas efectivas"], "widths": [0.50, 0.20, 0.30],
                   "rows": f["provenance_rows"], "align": ["LEFT", "RIGHT", "RIGHT"]},
            deck="table"),
        Section("largest", "ARCHIVOS MÁS GRANDES", "Los archivos de source más grandes",
            "Ordenados por líneas efectivas.",
            table={"columns": ["Archivo", "Lenguaje", "Efectivas"], "widths": [0.64, 0.18, 0.18],
                   "rows": f["largest_rows"], "align": ["LEFT", "LEFT", "RIGHT"]},
            deck="table"),
        Section("commits", "HISTORIA", "Commits recientes",
            "Los commits más recientes en la branch inspeccionada, del más nuevo al más viejo.",
            table={"columns": ["Commit", "Fecha", "Asunto"], "widths": [0.12, 0.14, 0.74],
                   "rows": f["commit_rows"]},
            deck="table"),
        Section("method", "MÉTODO", "Cómo se produjeron estos números",
            "El inventario es reproducible: vuelve a correr el generador y el mismo árbol da los mismos conteos.",
            points=[
                ("Alcance", "Cada archivo con seguimiento en Git más las adiciones no ignoradas del árbol de trabajo; se excluyen el output "
                 "ignorado del build, los cachés y el estado del runtime."),
                ("Sólo texto", "Los assets binarios como imágenes, fuentes y archivos comprimidos se cuentan como archivos, nunca "
                 "como líneas."),
                ("Python", "Tokenizado: se excluyen los comentarios, las líneas en blanco y los docstrings de módulos, clases y funciones"
                 "."),
                ("Otros lenguajes", "Se quitan los comentarios de bloque y de línea, y luego se cuentan las líneas que no están en blanco."),
                ("Sin valores privados", "Los valores de configuración, las credenciales y las direcciones nunca se reproducen."),
                ("Regenerar", "`python Tlamatini\\agent\\doc_generation\\refresh_project_docs.py`"),
            ], deck="cards"),
    ])

    from dossier_editor_content import bridge_section, editor_sections, release_sections, wizard_section

    architecture.sections.insert(0, bridge_section(Section))
    surfaces.sections[0:0] = editor_sections(Section)
    trust.sections.insert(0, wizard_section(Section))
    release.sections[0:0] = release_sections(Section, f)
    return [identity, architecture, surfaces, bestiary, capabilities, trust, running, release, facts]
