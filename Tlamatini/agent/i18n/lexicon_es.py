"""DATA ONLY. Spanish CARRIER terms -> canonical English hints that already exist.

WHAT THIS TABLE IS FOR
----------------------
``normalize.expand_request`` lifts a Spanish request into the canonical key
space the deterministic capability scorer was tuned on, so the scorer ranks on
INTENT rather than on the language the intent arrived in.

THE REGISTER THIS SERVES - AND WHY THE TABLE IS SMALL ON PURPOSE
----------------------------------------------------------------
Spanish is the MATRIX language; English is the EMBEDDED technical lexicon. A
Mexican developer writes:

    "Haciendo un Pod en Dockerer y creando un Container en Kubernetes
     y haciendo el deployment en la LPAR"

Spanish supplies the grammar - haciendo, creando, un, en, la, y. English
supplies every technical term - Pod, Dockerer, Container, Kubernetes,
deployment, LPAR.

Read the consequence for THIS file carefully, because it is the correction that
the first version of this lexicon got wrong: that sentence needs NO ENTRY HERE
AT ALL. Pod, Container, Kubernetes and deployment are already English and
already hit the registry hints directly. Adding *contenedor -> container* or
*despliegue -> deployment* would be modelling a language nobody in this audience
speaks, and every such row is a chance to be wrong for zero measurable gain.

So this table covers ONLY what is genuinely Spanish in such a sentence:

  * the MATRIX VERBS   - crea, borra, envia, busca, muestra, ejecuta, ...
  * the few NOUNS that really have no English form in this register -
    archivo, carpeta, correo, ruta, ventana, raton, teclado, bocinas, camara,
    microfono, voz, navegador
  * a handful of PHRASES - captura de pantalla, base de datos, en voz alta

Deliberately ABSENT, because the user writes them in English already:
    pod  container  deployment  commit  push  build  log  prompt  token
    endpoint  firmware  screenshot  browser  query  webcam  zip  pdf  cluster

THE CLOSURE RULE (the hard one)
-------------------------------
Every value on the right-hand side ALREADY EXISTS in the registry's own hint
corpus - ``capability_registry._EXTRA_HINTS_BY_TOOL_NAME``,
``capability_registry._CONTEXT_HINTS``, or a ``ChatWrappedAgentSpec``'s
``aliases`` / ``security_hints``. Nothing is invented. A test re-derives the
legal set from those sources and fails on any violation.

This is what keeps the guarantee one-directional: the scorer's tuned ENGLISH
behaviour remains the only behaviour. A Spanish request is translated into keys
the scorer already knows, and is then scored by exactly the code an English
request is scored by. No Spanish-specific scoring path exists.

CORRECT-AGENT RULE
------------------
A value must be a hint the RIGHT agent owns, not merely a legal string. Three
worked consequences, each of which cost a deliberate decision:

  * ``pantalla`` has NO bare entry. The only owner of the token ``screen`` is
    VideoPlayer, so *captura de pantalla* would have boosted the video player.
    The screenshot meaning is carried by the PHRASE instead, and the fullscreen
    meaning by ``pantalla completa``.
  * ``foto`` maps to ``take a photo`` (Camcorder) and NOT to ``photo``, whose
    owner is Image-Interpreter - the agent that LOOKS AT an existing image, not
    the one that takes a new one.
  * ``copia`` maps to ``move file`` (Mover, which copies) and not to
    ``copy file``, whose owner is SCPer - a remote transfer, not a local copy.

DELIBERATE OMISSIONS - no legal target exists, so no row is written
-------------------------------------------------------------------
    detener / parar / matar    no agent owns stop / kill / terminate
    contrasena                 no agent owns password
    copia de seguridad         no agent owns backup (FlowBacker has no hints)
    traducir                   no agent owns translate
    video                      ambiguous between record and play; the verb
                               ``graba`` and the noun ``webcam`` already carry
                               both readings

Inventing a hint for any of these would break the closure and, worse, would
send the request to an agent that cannot serve it.

NOT A GUI STRING TABLE
----------------------
Nothing here is ever shown to a user, and nothing here renames an asset. Agent
display names (Emailer, Asker, Apirer, STM32er, ...), tool names, config keys,
CLI flags and protocol sentinels are byte-identical in every locale.

KEYS ARE FOLDED
---------------
Keys are accent-free and lowercase, because the caller folds with
``normalize.fold_text`` before lookup. Single-word keys are matched as whole
tokens; multi-word keys are matched by ``normalize.phrase_hit``, which is
boundary-aware.

Stdlib only. No imports from ``agent.*``, ever - this file is read from the
scoring hot path.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Tuple

__all__ = [
    "ES_TO_CANONICAL",
    "CONTINUATION_WORDS_ES",
    "FAILURE_PREFIXES_ES",
    "INTERNET_HINTS_ES",
]


# ---------------------------------------------------------------------------
# The lexicon
# ---------------------------------------------------------------------------

ES_TO_CANONICAL: Dict[str, Tuple[str, ...]] = {

    # === MATRIX VERBS ======================================================
    # The action family. The NOUN in the same sentence picks the agent; the
    # verb only says what kind of thing is being done.

    # create -> File-Creator
    "crea": ("create file", "write file"),
    "crear": ("create file", "write file"),
    "creame": ("create file", "write file"),
    "creando": ("create file", "write file"),

    # delete -> Deleter
    "borra": ("delete file", "erase file", "remove file"),
    "borrar": ("delete file", "erase file", "remove file"),
    "borrame": ("delete file", "erase file", "remove file"),
    "borrando": ("delete file", "erase file", "remove file"),
    "elimina": ("delete file", "erase file", "remove file"),
    "eliminar": ("delete file", "erase file", "remove file"),
    "eliminame": ("delete file", "erase file", "remove file"),
    "eliminando": ("delete file", "erase file", "remove file"),
    "suprime": ("delete file", "erase file", "remove file"),
    "suprimir": ("delete file", "erase file", "remove file"),

    # send -> Emailer.
    # ``send email`` is owned ONLY by chat_agent_send_email; Zavuerer spells
    # its own variant ``send an email``. That precision is the point: a
    # channel-less "envia/manda" means e-mail in this product, and when a
    # channel noun IS present (whatsapp, telegram, sms) that noun outranks it.
    "envia": ("send email",),
    "enviar": ("send email",),
    "enviame": ("send email",),
    "enviale": ("send email",),
    "enviando": ("send email",),
    "manda": ("send email",),
    "mandar": ("send email",),
    "mandame": ("send email",),
    "mandale": ("send email",),
    "remite": ("send email",),
    "remitir": ("send email",),

    # search -> Grepper (content search)
    "busca": ("search", "find in files"),
    "buscar": ("search", "find in files"),
    "buscame": ("search", "find in files"),
    "buscando": ("search", "find in files"),
    "encuentra": ("search", "find in files"),
    "encontrar": ("search", "find in files"),
    "localiza": ("search", "locate"),
    "localizar": ("search", "locate"),

    # enumerate -> Globber (filename search)
    "lista": ("list files", "find files"),
    "listar": ("list files", "find files"),
    "listame": ("list files", "find files"),

    # show - intentionally weak: files_context owns ``show``, no tool does,
    # so it never steals a ranking from the noun.
    "muestra": ("show",),
    "muestrame": ("show",),
    "mostrar": ("show",),
    "mostrando": ("show",),
    "ensename": ("show",),
    "ensenar": ("show",),

    # run -> execute_command / Executer.
    # ONE hint on purpose. Three would outrank ``ssh`` on
    # "conectate por SSH ... y corre uptime", where SSHer must win.
    "ejecuta": ("run command",),
    "ejecutar": ("run command",),
    "ejecutame": ("run command",),
    "ejecutando": ("run command",),
    "corre": ("run command",),
    "correr": ("run command",),
    # "corriendo" is DELIBERATELY not mapped. As a gerund it almost
    # always reports a STATE - "los pods que estan corriendo" = the
    # pods that are running - not an instruction to run something.
    # Mapping it to "run command" handed execute_command a +10 boost
    # and beat Kuberneter 24-21 on exactly that sentence. The
    # imperative sense is already carried by corre / ejecuta / lanza.
    "lanza": ("run command",),
    "lanzar": ("run command",),
    "arranca": ("run command",),
    "arrancar": ("run command",),

    "abre": ("open",),
    "abrir": ("open",),
    "abreme": ("open",),
    "abriendo": ("open",),

    "guarda": ("save file",),
    "guardar": ("save file",),
    "guardame": ("save file",),
    "guardando": ("save file",),
    "almacena": ("save file",),
    "almacenar": ("save file",),

    "lee": ("read", "read document"),
    "leer": ("read", "read document"),
    "leeme": ("read", "read document"),
    "leyendo": ("read", "read document"),

    # inspect - neutral by design. "revisa" spans netstat, logs and files, so
    # both values are files_context tokens that no single tool owns.
    "revisa": ("read", "show"),
    "revisar": ("read", "show"),
    "revisame": ("read", "show"),
    "revisando": ("read", "show"),

    "analiza": ("analyze file", "analyze document"),
    "analizar": ("analyze file", "analyze document"),
    "analizame": ("analyze file", "analyze document"),
    "analizando": ("analyze file", "analyze document"),

    # capture - symmetric on purpose: Recorder and Camcorder get one hint
    # each, and the noun (microfono / camara / webcam) breaks the tie.
    "graba": ("record audio", "record video"),
    "grabar": ("record audio", "record video"),
    "grabame": ("record audio", "record video"),
    "grabando": ("record audio", "record video"),

    "toma": ("take a photo",),
    "tomar": ("take a photo",),
    "tomame": ("take a photo",),

    "descarga": ("download",),
    "descargar": ("download",),
    "descargando": ("download",),
    "baja": ("download",),
    "bajar": ("download",),

    # upload -> SCPer, the agent that actually pushes a file to a host.
    "sube": ("transfer file",),
    "subir": ("transfer file",),
    "subiendo": ("transfer file",),

    "mueve": ("move file", "relocate file"),
    "mover": ("move file", "relocate file"),
    "moviendo": ("move file", "relocate file"),
    # Mover copies too; ``copy file`` belongs to SCPer (a REMOTE transfer).
    "copia": ("move file",),
    "copiar": ("move file",),
    "copiando": ("move file",),

    "conecta": ("remote host",),
    "conectar": ("remote host",),
    "conectate": ("remote host",),
    "conectando": ("remote host",),

    "instala": ("install",),
    "instalar": ("install",),
    "instalando": ("install",),

    "compila": ("compile", "build"),
    "compilar": ("compile", "build"),
    "compilando": ("compile", "build"),
    # Spanglish, and extremely common in the firmware flow.
    "flashea": ("flash firmware",),
    "flashear": ("flash firmware",),

    "genera": ("generate a document",),
    "generar": ("generate a document",),
    "generame": ("generate a document",),
    "generando": ("generate a document",),

    "resume": ("summarize", "summary"),
    "resumir": ("summarize", "summary"),
    "resumeme": ("summarize", "summary"),

    "escribe": ("write file",),
    "escribir": ("write file",),
    "escribeme": ("write file",),
    "escribiendo": ("write file",),

    # add / change / replace -> Editor
    "agrega": ("edit file",),
    "agregar": ("edit file",),
    "anade": ("edit file",),
    "anadir": ("edit file",),
    "cambia": ("modify file", "edit file"),
    "cambiar": ("modify file", "edit file"),
    "modifica": ("modify file", "edit file"),
    "modificar": ("modify file", "edit file"),
    "reemplaza": ("replace", "find and replace", "replace in file"),
    "reemplazar": ("replace", "find and replace", "replace in file"),
    "sustituye": ("replace", "find and replace", "replace in file"),
    "sustituir": ("replace", "find and replace", "replace in file"),

    "comprime": ("zip",),
    "comprimir": ("zip",),
    "descomprime": ("unzip", "decompress", "extract archive"),
    "descomprimir": ("unzip", "decompress", "extract archive"),

    "decompila": ("decompile",),
    "decompilar": ("decompile",),
    "descompila": ("decompile",),
    "descompilar": ("decompile",),

    "transcribe": ("transcribe", "speech to text"),
    "transcribir": ("transcribe", "speech to text"),

    # speak -> Talker. ``di`` is short but matched as a WHOLE TOKEN, so it
    # cannot fire inside dime, dia, disco, dir.
    "di": ("say", "say out loud"),
    "dilo": ("say", "say out loud"),
    "decir": ("say", "say out loud"),

    # play - symmetric; the noun (mp3, bocinas, mp4) breaks the tie.
    "reproduce": ("play audio", "play video"),
    "reproducir": ("play audio", "play video"),

    "escanea": ("port scan",),
    "escanear": ("port scan",),

    "notifica": ("notify", "notification"),
    "notificar": ("notify", "notification"),
    "avisa": ("notify", "notification"),
    "avisar": ("notify", "notification"),

    # === NOUNS =============================================================
    # Only the ones a Mexican developer would NOT already write in English.

    "archivo": ("file", "files"),
    "archivos": ("file", "files"),
    "carpeta": ("folder", "directory"),
    "carpetas": ("folder", "directory"),
    "directorio": ("directory", "folder"),
    "directorios": ("directory", "folder"),
    "ruta": ("path", "paths"),
    "rutas": ("path", "paths"),
    "codigo": ("source code",),
    "proyecto": ("project",),

    "correo": ("email", "mail"),
    "correos": ("email", "mail"),
    # ``chat message`` is Whatsapper's, so a WhatsApp request keeps its agent.
    "mensaje": ("send a message", "chat message"),
    "mensajes": ("send a message", "chat message"),

    "imagen": ("image", "picture"),
    "imagenes": ("image", "picture"),
    # NOT ``photo`` - that token's owner is Image-Interpreter, which LOOKS AT
    # an image. Taking one is Camcorder.
    "foto": ("take a photo",),
    "fotos": ("take a photo",),
    "camara": ("camera", "webcam"),
    "microfono": ("microphone", "mic"),
    "voz": ("voice",),
    "sonido": ("play sound", "record sound"),
    "bocina": ("speaker", "speakers"),
    "bocinas": ("speaker", "speakers"),
    "altavoz": ("speaker", "speakers"),
    "altavoces": ("speaker", "speakers"),

    "ventana": ("window", "windows"),
    "ventanas": ("window", "windows"),
    "raton": ("mouse",),
    "teclado": ("keyboard",),

    "navegador": ("browser",),
    "pagina": ("web page",),
    "paginas": ("web page",),
    "sitio": ("website",),
    "red": ("network",),
    "redes": ("network",),
    "puerto": ("port", "ports"),
    "puertos": ("port", "ports"),
    "servidor": ("remote host",),
    "servidores": ("remote host",),

    "comando": ("command", "run command"),
    "comandos": ("command", "run command"),
    "consulta": ("query",),
    "proceso": ("process",),
    "procesos": ("process",),
    "resumen": ("summarize", "summary"),
    # NOT ``reporte`` / ``informe``. Measured: on "envia un email a soporte
    # con el subject Reporte" it handed PDFer a hit on a pure e-mail request,
    # and it bought nothing on "generame un PDF con el reporte", where ``pdf``
    # and ``genera`` already decide it. Smaller and correct beats larger.

    # === PHRASES ===========================================================
    # Matched by normalize.phrase_hit, which is boundary-aware.

    "captura de pantalla": ("screenshot", "screen capture", "take a screenshot"),
    "capturas de pantalla": ("screenshot", "screen capture", "take a screenshot"),
    "pantalla completa": ("fullscreen video",),
    "base de datos": ("database", "sql", "query"),
    "linea de comandos": ("command", "terminal", "shell"),
    "linea de comando": ("command", "terminal", "shell"),
    "correo electronico": ("email", "mail", "send email"),
    "disco duro": ("disk", "storage"),
    "en voz alta": ("say out loud", "read aloud", "text to speech"),
    "pagina web": ("web page", "website"),
    "codigo fuente": ("source code", "source"),
    "maquina remota": ("remote host",),
}


# ---------------------------------------------------------------------------
# Short-follow-up detection
# ---------------------------------------------------------------------------
# The planner boosts a SHORT follow-up with the tail of the chat history, so a
# Spanish "continua" must be recognised exactly as an English "continue" is -
# otherwise the Spanish user silently loses the history boost.
#
# ADDITIVE ONLY: the caller keeps its English set and unions this one. Every
# entry is a word a Spanish speaker actually types as a bare continuation.
# ``ok`` and ``si`` are shared spellings and are intentionally present, because
# they are what a Mexican user types.
CONTINUATION_WORDS_ES: FrozenSet[str] = frozenset({
    "continua", "continuar", "continuemos",
    "sigue", "seguir", "siguiente",
    "adelante", "procede", "proceder",
    "dale", "hazlo", "hagalo", "hazle",
    "listo", "ya", "ok", "oka", "okey",
    "si", "claro", "correcto", "perfecto", "va",
})


# ---------------------------------------------------------------------------
# Failure-prefix detection
# ---------------------------------------------------------------------------
# A tool result is classified as a failure when it STARTS WITH one of these.
# Two populations are covered: Spanish prose a Spanish-speaking agent writes,
# and the literal strings a Spanish-locale Windows emits - which are what a
# Mexican developer's shell actually returns, and which the English prefixes
# cannot match at all.
#
# Folded, accent-free, lowercase - compare against fold_text(result).
#
# CURATION RULE: every entry must be a phrase that can ONLY introduce a
# failure. A successful output must never begin with one, or a good run is
# reported as broken - the more expensive error of the two.
FAILURE_PREFIXES_ES: Tuple[str, ...] = (
    # Spanish prose
    "fallo", "fallido", "fallida", "fracaso",
    "no se pudo", "no se puede", "no pudo", "no puede",
    "no fue posible",
    "no existe", "no encontrado", "no se encontro", "no se encontraron",
    "no hay",
    "acceso denegado", "permiso denegado", "permisos insuficientes",
    "excepcion", "error fatal", "errores:",
    # Spanish-locale Windows / cmd.exe
    "el sistema no puede", "el sistema no puede encontrar",
    "no se reconoce", "no se reconoce como un comando",
    "ruta de acceso no encontrada",
    "archivo no encontrado",
    "nombre de archivo, nombre de directorio",
    "operacion no valida", "argumento no valido",
)


# ---------------------------------------------------------------------------
# Internet-context detection
# ---------------------------------------------------------------------------
# Markers that a request needs FRESH information the model cannot hold. The
# English determiner keys on "today", "latest", "current", "price" and friends;
# these are the Spanish carriers of the same intent.
#
# Note what is NOT here: a Spanish user asking about technology writes the
# technology's English name, so no product term needs a row. Only the
# TIME-and-MARKET carrier is Spanish.
INTERNET_HINTS_ES: FrozenSet[str] = frozenset({
    # freshness
    "hoy", "ahora", "actual", "actualmente", "actualizado",
    "reciente", "recientes", "ultima", "ultimo", "ultimas", "ultimos",
    "ultimas noticias", "noticias", "hoy en dia",
    "esta semana", "este mes", "este ano",
    # weather
    "clima", "pronostico", "pronostico del tiempo", "temperatura",
    # markets
    "precio", "precios", "cotizacion", "cotizaciones",
    "tipo de cambio", "dolar", "bolsa", "acciones",
})
