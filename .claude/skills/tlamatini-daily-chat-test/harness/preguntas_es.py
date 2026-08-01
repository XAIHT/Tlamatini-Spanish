# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""
Corpus of 1000 SPANISH questions for the Tlamatini Spanish edition.

This is not a bag of random sentences. Every category targets one specific
claim the Spanish localization (NEPANTLA) makes, so a failure points at the
stage that broke:

  saludo        the Spanish greeting path (REGEX_GREETING in constants.py)
  identidad     self-knowledge answered in Spanish
  concepto      technical Q&A -- the REGISTER rule (English nouns survive)
  registro      register probes that actively TEMPT a wrong translation
  acentos       N1 accent folding: 60 pairs, accented vs stripped, same ask
  frase_limite  N2 boundary matching: a trigger phrase quoted mid-sentence
                that must NOT be acted on (she is asked to explain, not do)
  mexicano      Angela's Mexican colloquial register
  mixto         Spanish grammar carrying English technical clauses
  largo         long multi-clause requests (context budgeting under Spanish)
  seguimiento   terse follow-ups (short-follow-up planner scoring, in Spanish)

Every question is READ-ONLY and SAFE: nothing here deletes, sends, scans or
overwrites anything. The `frase_limite` set deliberately quotes action
phrases, but always asks for an explanation -- acting on one is itself the
bug that category hunts.

Contract of each record:
    id        stable, sortable  (ES0001 ...)
    category  one of the ten above
    text      what is typed into the chat box
    expect    substrings that SHOULD appear (case-insensitive)
    keep_en   technical nouns that MUST stay in English (the register rule)
    min_len   minimum believable answer length
    twin      for `acentos`, the id of the other half of the pair
"""

# --------------------------------------------------------------- 1. saludo
_SALUDOS = [
    "hola", "buenos días", "qué onda", "buenas tardes", "hey Tlamatini",
    "cómo estás", "qué tal", "buenas noches", "hola Tlamatini", "oye",
    "saludos", "qué hay",
]
_SALUDO_COLAS = [
    "", ", ¿cómo te va?", ", ¿me ayudas con algo?", ", ¿ya estás lista?",
    ", ¿qué puedes hacer por mí?",
]

# ------------------------------------------------------------ 2. identidad
_IDENTIDAD = [
    "¿quién eres?",
    "¿qué es Tlamatini?",
    "¿qué significa tu nombre?",
    "¿quién te creó?",
    "¿en qué lenguaje estás escrita?",
    "¿qué puedes hacer por mí?",
    "¿cuántos agents tienes?",
    "¿qué es un agent en tu sistema?",
    "¿qué es el modo Multi-Turn?",
    "¿qué es el Exec Report?",
    "¿qué es ACPX?",
    "¿qué es el canvas de flows?",
    "¿cómo se guarda un flow?",
    "¿qué es un skill?",
    "¿qué modelos de LLM usas?",
    "¿corres local o en la nube?",
]
_IDENT_COLAS = [
    "", " Explícamelo corto.", " Explícamelo con detalle.",
    " Dame un ejemplo.", " Respóndeme en español, por favor.",
]

# ------------------------------------------------------------- 3. concepto
# (pregunta, términos que DEBEN quedarse en inglés)
_CONCEPTOS = [
    ("¿qué es un container de Docker?", ["container"]),
    ("¿qué diferencia hay entre un container y una imagen?", ["container"]),
    ("¿qué es un pod de Kubernetes?", ["pod"]),
    ("¿para qué sirve un log?", ["log"]),
    ("¿qué es un path absoluto?", ["path"]),
    ("¿qué es el status de un proceso?", ["status"]),
    ("¿qué es el output de un comando?", ["output"]),
    ("¿qué es el input de una función?", ["input"]),
    ("¿qué es un token en un LLM?", ["token"]),
    ("¿qué es un endpoint de una API?", ["endpoint"]),
    ("¿qué es un commit en git?", ["commit"]),
    ("¿qué es un branch en git?", ["branch"]),
    ("¿qué es un merge en git?", ["merge"]),
    ("¿qué es un pull request?", ["pull request"]),
    ("¿qué es un buffer?", ["buffer"]),
    ("¿qué es un thread?", ["thread"]),
    ("¿qué es un deadlock?", ["deadlock"]),
    ("¿qué es una race condition?", ["race condition"]),
    ("¿qué es un socket?", ["socket"]),
    ("¿qué es un firewall?", ["firewall"]),
    ("¿qué es un backup?", ["backup"]),
    ("¿qué es un script?", ["script"]),
    ("¿qué es un framework?", ["framework"]),
    ("¿qué es un middleware?", ["middleware"]),
    ("¿qué es el cache?", ["cache"]),
    ("¿qué es un hash?", ["hash"]),
    ("¿qué es el payload de una petición?", ["payload"]),
    ("¿qué es un timeout?", ["timeout"]),
    ("¿qué es un deploy?", ["deploy"]),
    ("¿qué es el debugging?", ["debug"]),
    ("¿qué es un breakpoint?", ["breakpoint"]),
    ("¿qué es un stack trace?", ["stack trace"]),
    ("¿qué es una query de SQL?", ["query"]),
    ("¿qué es un index en una base de datos?", ["index"]),
    ("¿qué es un pipeline de CI?", ["pipeline"]),
    ("¿qué es un webhook?", ["webhook"]),
    ("¿qué es un proxy?", ["proxy"]),
    ("¿qué es el kernel de un sistema operativo?", ["kernel"]),
    ("¿qué es un driver?", ["driver"]),
    ("¿qué es la memoria RAM?", ["RAM"]),
]
_CONCEPTO_COLAS = [
    "", " Explícamelo en dos líneas.", " Dame un ejemplo práctico.",
    " ¿Para qué me sirve?", " Explícamelo como si tuviera diez años.",
]

# ------------------------------------------------------------- 4. registro
# Preguntas que TIENTAN a traducir el término técnico. El término debe
# quedarse en inglés (regla de registro de Angela).
_REGISTRO = [
    ("¿cómo reviso el log de un container?", ["log", "container"]),
    ("¿dónde queda el path del config?", ["path", "config"]),
    ("¿cómo veo el status de mis pods?", ["status", "pod"]),
    ("¿cómo guardo el output en un archivo?", ["output"]),
    ("¿cómo le paso un input a un script?", ["input", "script"]),
    ("¿cómo limpio el cache del browser?", ["cache"]),
    ("¿cómo leo el stack trace de un error?", ["stack trace"]),
    ("¿cómo cambio el timeout de una request?", ["timeout"]),
    ("¿cómo hago un backup de la base de datos?", ["backup"]),
    ("¿cómo veo los threads de un proceso?", ["thread"]),
    ("¿cómo abro un socket en Python?", ["socket"]),
    ("¿cómo configuro un proxy?", ["proxy"]),
    ("¿cómo instalo un driver nuevo?", ["driver"]),
    ("¿cómo mando un payload en JSON?", ["payload", "JSON"]),
    ("¿cómo pruebo un endpoint de mi API?", ["endpoint", "API"]),
    ("¿cómo deshago el último commit?", ["commit"]),
    ("¿cómo creo un branch nuevo?", ["branch"]),
    ("¿cómo corro un deploy sin tumbar el server?", ["deploy", "server"]),
    ("¿cómo pongo un breakpoint en mi código?", ["breakpoint"]),
    ("¿cómo optimizo una query lenta?", ["query"]),
    ("¿cómo agrego un index a una tabla?", ["index"]),
    ("¿cómo veo cuánta RAM está usando el proceso?", ["RAM"]),
    ("¿cómo escribo un webhook que reciba eventos?", ["webhook"]),
    ("¿cómo cuento los tokens que gasta mi prompt?", ["token", "prompt"]),
]
_REGISTRO_COLAS = [
    "", " Dime los pasos.", " Explícame el porqué.",
    " ¿Hay alguna forma más rápida?", " Dame el comando exacto.",
]

# -------------------------------------------------------------- 5. acentos
# 60 preguntas con acentos; el runner genera automáticamente la gemela sin
# acentos. Si NEPANTLA N1 funciona, las dos deben contestarse igual de bien.
_ACENTOS = [
    "¿cómo configuro la conexión?", "¿qué día es hoy para ti?",
    "¿cuál es tu función principal?", "¿cómo está la memoria del sistema?",
    "¿qué versión de Python usas?", "¿dónde está el archivo de configuración?",
    "¿cómo interpretas una imagen?", "¿qué información guardas de mí?",
    "¿cuántos días llevas corriendo?", "¿qué más puedes explicarme?",
    "¿cómo sé si un agent terminó?", "¿por qué falló mi última petición?",
    "¿qué diferencia hay entre sesión y contexto?", "¿cómo reinicio la conexión?",
    "¿cuál es tu límite de tokens?", "¿cómo mides tu propio rendimiento?",
    "¿qué pasa si se cae Ollama?", "¿cómo administro los permisos?",
    "¿qué es una petición sincrónica?", "¿cómo depuro un error rápido?",
    "¿cuál es la ruta más corta para aprender?", "¿qué características tienes?",
    "¿cómo defines una función en Python?", "¿qué hace la palabra clave async?",
    "¿cómo válido una entrada de usuario?", "¿qué es la programación funcional?",
    "¿cómo optimizo un algoritmo lento?", "¿qué es la complejidad algorítmica?",
    "¿cómo comparo dos versiones de un archivo?", "¿qué es una expresión regular?",
    "¿cómo automatizo una tarea repetitiva?", "¿qué es la inyección de dependencias?",
    "¿cómo protejo una contraseña?", "¿qué es el cifrado asimétrico?",
    "¿cómo genero un número aleatorio seguro?", "¿qué es la autenticación de dos factores?",
    "¿cómo migro una base de datos?", "¿qué es una transacción atómica?",
    "¿cómo escalo una aplicación web?", "¿qué es el balanceo de carga?",
    "¿cómo mido la latencia de una red?", "¿qué es el ancho de banda?",
    "¿cómo diagnostico una conexión lenta?", "¿qué es la resolución de nombres?",
    "¿cómo organizo un proyecto grande?", "¿qué es la deuda técnica?",
    "¿cómo escribo documentación útil?", "¿qué es una revisión de código?",
    "¿cómo estimo el tiempo de una tarea?", "¿qué es la integración continua?",
    "¿cómo aprendo un lenguaje nuevo rápido?", "¿qué libro me recomiendas?",
    "¿cómo mantengo la concentración?", "¿qué hago si me atoro en un bug?",
    "¿cómo explico algo técnico a alguien que no sabe?", "¿qué es un buen commit?",
    "¿cómo colaboro en un equipo remoto?", "¿qué es la programación en pareja?",
    "¿cómo pido ayuda sin sentirme mal?", "¿qué consejo le das a alguien que empieza?",
]

# --------------------------------------------------------- 6. frase_limite
# Una frase de acción QUOTED dentro de una petición de explicación. Actuar
# sobre ella es el bug. La respuesta correcta explica, no ejecuta.
_LIMITES = [
    'si yo te escribiera "borra los archivos viejos", ¿qué entenderías exactamente?',
    'cuando alguien dice "crea un archivo", ¿qué información te falta para hacerlo bien?',
    '¿qué diferencia hay entre decir "manda un correo" y "prepara un correo"?',
    'no lo hagas, sólo dime: ¿qué harías si te pido "reinicia el servidor"?',
    'explícame por qué "ejecuta el comando" es una instrucción peligrosa si no doy contexto',
    '¿cómo distingues "muéstrame el log" de "borra el log"?',
    'si te digo "corre el script", ¿qué preguntas me harías antes?',
    '¿qué entiendes por "limpia la carpeta" y por qué deberías confirmarlo?',
    'explícame la diferencia entre "instala la librería" y "dime cómo instalar la librería"',
    'no ejecutes nada: ¿qué significa para ti "haz un backup"?',
    '¿por qué "mueve los archivos" necesita que yo diga a dónde?',
    'si alguien escribe "apaga todo", ¿qué deberías responder?',
    '¿qué información pedirías ante "conéctate al servidor"?',
    'explícame por qué "descarga eso" es ambiguo',
    '¿cómo interpretas "haz un deploy" sin más contexto?',
    'sólo teoría: ¿qué pasos seguirías si te pido "arregla el bug"?',
    '¿qué diferencia hay entre "búscame archivos" y "borra archivos"?',
    'si te digo "abre el navegador", ¿qué agent usarías y por qué?',
    'explícame por qué no deberías actuar ante "hazlo ya" sin detalles',
    '¿qué harías si te pido "escanea la red" sin decirte de quién es?',
]
_LIMITE_COLAS = [
    "", " Sólo explícamelo, no lo hagas.", " Respóndeme en español claro.",
    " Dame tu razonamiento paso a paso.", " Sé breve.",
]

# ------------------------------------------------------------- 7. mexicano
_MEXICANO = [
    "échame la mano con una duda de programación",
    "¿me haces el paro explicándome qué es una API?",
    "órale, cuéntame qué sabes hacer",
    "ándale, explícame cómo funcionas por dentro",
    "oye, ¿está muy complicado aprender Python?",
    "no manches, ¿de verdad puedes correr comandos?",
    "¿qué onda con los agents, cómo jalan?",
    "ahorita nada más dime qué es un flow",
    "va, explícame lo del Multi-Turn",
    "¿me explicas rápido qué es el RAG, porfa?",
    "una pregunta rápida: ¿qué es un embedding?",
    "sale, ¿y cómo le hago para guardar un flow?",
    "¿cómo ves, me conviene usar la nube o local?",
    "chance y me ayudas: ¿qué es un vector store?",
    "nomás dime si puedes leer archivos",
    "¿qué tal si me explicas qué hace el Parametrizer?",
]
_MEXICANO_COLAS = [
    "", " porfa", " gracias", " explícamelo sencillo", " sin tecnicismos",
]

# ---------------------------------------------------------------- 8. mixto
_MIXTO = [
    ("necesito entender el request lifecycle, ¿me lo explicas?", ["request"]),
    ("¿cómo hago un rollback si el deploy falla?", ["rollback", "deploy"]),
    ("explícame el garbage collector de Python", ["garbage collector"]),
    ("¿qué es el event loop y por qué me bloquea?", ["event loop"]),
    ("¿cómo manejo un rate limit de una API?", ["rate limit", "API"]),
    ("¿qué es un race condition en un thread pool?", ["thread"]),
    ("necesito un health check para mi servicio, ¿cómo lo hago?", ["health check"]),
    ("¿qué es el cold start de una función serverless?", ["cold start"]),
    ("¿cómo configuro el logging level de mi app?", ["logging"]),
    ("¿qué es un memory leak y cómo lo encuentro?", ["memory leak"]),
    ("explícame qué es el load balancing", ["load balancing"]),
    ("¿cómo hago streaming de una respuesta larga?", ["streaming"]),
    ("¿qué es un dead letter queue?", ["dead letter queue"]),
    ("¿cómo funciona el connection pooling?", ["connection pool"]),
    ("¿qué es un circuit breaker en microservicios?", ["circuit breaker"]),
    ("¿cómo versiono mi API sin romper clientes?", ["API"]),
    ("¿qué es el schema de una base de datos?", ["schema"]),
    ("¿cómo hago profiling de mi código?", ["profiling"]),
    ("¿qué es un feature flag?", ["feature flag"]),
    ("¿cómo uso un linter en mi proyecto?", ["linter"]),
]
_MIXTO_COLAS = [
    "", " Con un ejemplo, por favor.", " En pocas palabras.",
    " ¿Qué error se comete más seguido?", " ¿Cuándo NO debería usarlo?",
]

# ----------------------------------------------------------------- 9. largo
_LARGOS = [
    "Estoy armando un proyecto en Python que va a leer archivos de una carpeta, "
    "procesarlos y guardar un resumen. Quiero que me expliques cómo lo estructuro, "
    "qué carpetas creo, dónde pongo la configuración y cómo manejo los errores.",
    "Tengo una aplicación web que se pone lenta cuando hay muchos usuarios al mismo "
    "tiempo. Explícame cómo encuentro el cuello de botella, qué mido primero y qué "
    "cambios suelen dar más resultado.",
    "Quiero aprender desarrollo backend desde cero pero ya sé algo de Python. "
    "Arma un plan de estudio de tres meses, dime qué temas van primero y por qué.",
    "Me encargaron revisar el código de un compañero. Explícame qué debo buscar, "
    "cómo doy retroalimentación sin ofender y qué cosas sí valen la pena señalar.",
    "Tengo un script que a veces falla y no sé por qué. Explícame cómo lo depuro "
    "paso a paso, qué información recojo y cómo descarto causas una por una.",
    "Quiero conectar mi aplicación con un servicio externo que tiene una API. "
    "Explícame cómo manejo las llaves, los errores de red y qué hago si el servicio "
    "se cae.",
    "Estoy diseñando una base de datos para una tienda pequeña. Explícame qué tablas "
    "necesito, cómo las relaciono y qué errores comunes debo evitar.",
    "Mi equipo quiere empezar a usar integración continua. Explícame qué es, qué "
    "necesitamos, cuánto trabajo es y qué ganamos realmente.",
    "Quiero automatizar una tarea que hago todos los días a mano: abrir un reporte, "
    "sacar unos datos y mandarlos por correo. Explícame cómo lo armo.",
    "Tengo miedo de borrar algo importante cuando uso la terminal. Explícame qué "
    "hábitos me protegen y qué comandos debo tratar con más respeto.",
    "Explícame cómo funciona un sistema RAG por dentro: cómo se parten los "
    "documentos, cómo se convierten en vectores y cómo se decide qué se le manda "
    "al modelo.",
    "Quiero entender la diferencia entre correr un modelo de lenguaje en mi máquina "
    "y usar uno en la nube. Compárame costo, velocidad, privacidad y calidad.",
    "Tengo un proyecto viejo sin documentación y nadie sabe cómo funciona. "
    "Explícame cómo lo abordo, por dónde empiezo a leer y cómo lo voy documentando.",
    "Explícame qué es la deuda técnica con un ejemplo real, cómo se acumula, cómo "
    "se mide y cómo convenzo a mi jefe de que hay que pagarla.",
    "Quiero montar un flujo de trabajo automático que revise mi código, corra las "
    "pruebas y me avise si algo se rompe. Explícame las piezas que necesito.",
    "Me interesa la seguridad. Explícame los errores más comunes que comete alguien "
    "que apenas empieza a exponer un servicio a internet y cómo se evitan.",
]
_LARGO_COLAS = [
    "", " Respóndeme ordenado por pasos.", " Usa una lista.",
    " Sé concreta y práctica.", " Al final dame un resumen de tres líneas.",
]

# ---------------------------------------------------------- 10. seguimiento
_SEGUIMIENTO = [
    "sigue", "continúa", "¿y luego?", "dame más detalle", "explícame eso otra vez",
    "no entendí, ¿me lo repites?", "dame un ejemplo", "¿algo más?",
    "resúmelo", "profundiza en el último punto", "¿por qué?", "¿estás segura?",
]
_SEG_COLAS = [
    "", " por favor", " pero más corto", " con un ejemplo", " en español sencillo",
]


# ------------------------------------------------------------------ builder
def _strip_accents(text):
    """Remove diacritics AND the Spanish opening marks, as a user would type
    on a keyboard without a Spanish layout."""
    import unicodedata

    decomposed = unicodedata.normalize("NFKD", text)
    plain = "".join(c for c in decomposed if not unicodedata.combining(c))
    return plain.replace("¿", "").replace("¡", "")


def _cross(bases, colas):
    """base × cola, preserving order, no duplicates."""
    out = []
    for base in bases:
        for cola in colas:
            out.append((base + cola).strip())
    return out


def build_corpus():
    """Return exactly 1000 question records."""
    rows = []
    n = 0

    def add(category, text, expect=None, keep_en=None, min_len=20, twin=None):
        nonlocal n
        n += 1
        rows.append({
            "id": "ES%04d" % n,
            "category": category,
            "text": text,
            "expect": expect or [],
            "keep_en": keep_en or [],
            "min_len": min_len,
            "twin": twin,
        })
        return rows[-1]

    # 1. saludo -- 60
    for t in _cross(_SALUDOS, _SALUDO_COLAS):
        add("saludo", t, min_len=8)

    # 2. identidad -- 80
    for base in _IDENTIDAD:
        for cola in _IDENT_COLAS:
            add("identidad", (base + cola).strip(), min_len=40)

    # 3. concepto -- 200
    for base, keep in _CONCEPTOS:
        for cola in _CONCEPTO_COLAS:
            add("concepto", (base + cola).strip(), keep_en=keep, min_len=50)

    # 4. registro -- 120
    for base, keep in _REGISTRO:
        for cola in _REGISTRO_COLAS:
            add("registro", (base + cola).strip(), keep_en=keep, min_len=50)

    # 5. acentos -- 120 (60 accented + 60 stripped twins, adjacent ids)
    for base in _ACENTOS:
        acc = add("acentos", base, min_len=40)
        plain = add("acentos", _strip_accents(base), min_len=40, twin=acc["id"])
        acc["twin"] = plain["id"]

    # 6. frase_limite -- 100
    for base in _LIMITES:
        for cola in _LIMITE_COLAS:
            add("frase_limite", (base + cola).strip(), min_len=40)

    # 7. mexicano -- 80
    for base in _MEXICANO:
        for cola in _MEXICANO_COLAS:
            add("mexicano", (base + cola).strip(), min_len=30)

    # 8. mixto -- 100
    for base, keep in _MIXTO:
        for cola in _MIXTO_COLAS:
            add("mixto", (base + cola).strip(), keep_en=keep, min_len=50)

    # 9. largo -- 80
    for base in _LARGOS:
        for cola in _LARGO_COLAS:
            add("largo", (base + cola).strip(), min_len=120)

    # 10. seguimiento -- 60
    for base in _SEGUIMIENTO:
        for cola in _SEG_COLAS:
            add("seguimiento", (base + cola).strip(), min_len=10)

    return rows


CORPUS = build_corpus()


if __name__ == "__main__":
    from collections import Counter

    counts = Counter(r["category"] for r in CORPUS)
    texts = [r["text"] for r in CORPUS]
    print("total preguntas :", len(CORPUS))
    print("únicas          :", len(set(texts)))
    print("con keep_en     :", sum(1 for r in CORPUS if r["keep_en"]))
    print("pares de acentos:", sum(1 for r in CORPUS if r["twin"]) // 2)
    print()
    for cat, c in counts.most_common():
        print("  %-14s %4d" % (cat, c))
    assert len(CORPUS) == 1000, "el corpus debe tener exactamente 1000"
    assert len(set(texts)) == 1000, "hay preguntas duplicadas"
    print("\nOK  1000 preguntas únicas")
