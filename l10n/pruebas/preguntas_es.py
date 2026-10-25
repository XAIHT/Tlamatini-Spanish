# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Banco de 100 prompts EN ESPAÑOL para la prueba visible de Tlamatini-Spanish.

CONTRATO DE SEGURIDAD (igual que el banco en inglés, más la regla de voz):
el modo fijado es Multi-Turn ON, así que Tlamatini puede EJECUTAR tools. Por eso
cada prompt está curado para ser SEGURO de correr en la máquina de la
desarrolladora:

  * conocimiento / explicación         -> el LLM responde directo, sin efectos
  * autoconocimiento                   -> describe a la propia Tlamatini
  * una pizca de ops de SOLO-LECTURA   -> la hora actual, listar skills
  * NADA que borre/mueva/escriba archivos, mate procesos, escanee hosts, mande
    mensajes, abra ventanas en bloque o toque estado remoto.

REGLA DE VOZ (edición en español): NINGÚN prompt pide hablar, dictar, grabar ni
reproducir audio. La prueba corre con TLAMATINI_SIN_AUDIO=1 y el avatar en modo
silencioso, pero además ningún prompt invoca a Talker/AudioPlayer/Whisperer —
Tlamatini-Spanish jamás debe sonar en inglés (ni en ningún idioma) en la prueba.

Cada prompt es un dict con la misma forma que el banco inglés, para que el
calificador del harness (heuristic_qualify) funcione sin cambios:
    {"id","category","text","expect":[...],"min_len":int}
`expect` usa términos técnicos en inglés (que se quedan en inglés por NEPANTLA)
o nombres de agents, porque ésos aparecen igual en una respuesta en español.
"""
from typing import Any, Dict, List

# (nombre del agent, [palabras que la respuesta podría mencionar]) — los nombres
# nunca se traducen, así que sirven igual como `expect` en una respuesta en español.
_AGENTS = [
    ("Executer", ["comando", "shell"]),
    ("Pythonxer", ["python", "script"]),
    ("Gitter", ["git", "commit"]),
    ("Grepper", ["regex", "buscar"]),
    ("Globber", ["glob", "archivos"]),
    ("File-Creator", ["crear", "archivo"]),
    ("Editor", ["editar", "archivo"]),
    ("Mover", ["mover", "archivo"]),
    ("PDFer", ["PDF", "documento"]),
    ("LaTeXer", ["LaTeX", "PDF"]),
    ("PPTXer", ["PowerPoint", "slide"]),
    ("Dockerer", ["Docker", "container"]),
    ("Kuberneter", ["Kubernetes", "kubectl"]),
    ("SSHer", ["SSH", "remoto"]),
    ("SQLer", ["SQL", "query"]),
    ("Crawler", ["web", "crawl"]),
    ("Googler", ["Google", "search"]),
    ("Playwrighter", ["browser", "Playwright"]),
    ("Apirer", ["API", "HTTP"]),
    ("STM32er", ["STM32", "firmware"]),
    ("ESP32er", ["ESP32", "firmware"]),
    ("Arduiner", ["Arduino", "firmware"]),
    ("Kalier", ["Kali", "pentest"]),
    ("Nmapper", ["nmap", "port"]),
    ("Image-Interpreter", ["imagen", "vision"]),
    ("FlowCreator", ["flow", "diseña"]),
    ("Parametrizer", ["map", "config"]),
    ("Reviewer", ["review", "diff"]),
    ("Summarizer", ["resumen", "LLM"]),
    ("Kyber-KeyGen", ["Kyber", "llave"]),
]

# Preguntas de conocimiento general de programación / IT (se responden en prosa).
_GENERAL = [
    ("¿Qué es un pod en Kubernetes y en qué se diferencia de un container?", ["pod", "container"]),
    ("Explícame qué es un commit en Git y para qué sirve.", ["commit", "git"]),
    ("¿Cuál es la diferencia entre un branch y un tag en Git?", ["branch", "tag"]),
    ("¿Qué es una API REST y cuáles son sus verbos HTTP más comunes?", ["REST", "HTTP"]),
    ("Explícame qué es un endpoint en el contexto de una API web.", ["endpoint", "API"]),
    ("¿Qué es un prompt en el contexto de un LLM?", ["prompt", "LLM"]),
    ("¿Qué es un token cuando se habla de modelos de lenguaje?", ["token"]),
    ("Explícame brevemente qué es la ventana de contexto de un modelo.", ["contexto", "ventana"]),
    ("¿Qué significa hacer deployment de una aplicación?", ["deployment"]),
    ("¿Qué es un timeout y por qué es útil en una llamada de red?", ["timeout"]),
    ("Explícame qué es un backup y por qué conviene tener más de una copia.", ["backup"]),
    ("¿Qué es una expresión regular (regex) y da un ejemplo sencillo?", ["regex"]),
    ("¿Qué diferencia hay entre compilar e interpretar un programa?", ["compil", "interpret"]),
    ("¿Qué es la recursividad en programación? Da un ejemplo corto.", ["recursiv"]),
    ("Explícame qué es un hash y para qué se usa.", ["hash"]),
    ("¿Qué es un socket y para qué sirve en redes?", ["socket"]),
    ("¿Qué es un webhook y cómo se diferencia de un polling?", ["webhook"]),
    ("Explícame qué es la caché y por qué acelera un sistema.", ["caché"]),
    ("¿Qué es un thread y en qué se diferencia de un proceso?", ["thread", "proceso"]),
    ("¿Qué es un contenedor Docker? (puedes decir container)", ["container", "Docker"]),
    ("Escribe un ejemplo corto en Python de una función que sume una lista de números.", ["def", "python"]),
    ("Escribe un ejemplo de un bucle for en JavaScript que imprima del 1 al 5.", ["for"]),
    ("Escribe una consulta SQL que seleccione todos los registros de una tabla llamada usuarios.", ["SELECT"]),
    ("Explícame la diferencia entre una lista y una tupla en Python.", ["lista", "tupla"]),
    ("¿Qué es el patrón Modelo-Vista-Controlador (MVC)?", ["modelo", "vista"]),
    ("Explícame qué es la programación orientada a objetos en pocas palabras.", ["objeto", "clase"]),
    ("¿Qué es un linter y para qué sirve al escribir código?", ["linter"]),
    ("¿Qué es la integración continua (CI)?", ["CI", "integración"]),
    ("Explícame qué hace el comando git status.", ["git", "status"]),
    ("¿Qué es un entorno virtual de Python y por qué conviene usarlo?", ["python", "entorno"]),
    ("¿Qué es JSON y para qué se usa al intercambiar datos?", ["JSON"]),
    ("Explícame la diferencia entre HTTP y HTTPS.", ["HTTP"]),
    ("¿Qué es una variable de entorno y cómo se usa?", ["variable", "entorno"]),
    ("Escribe un ejemplo corto de un diccionario en Python.", ["dict", "{"]),
    ("¿Qué es el control de versiones y por qué es importante en un proyecto?", ["version"]),
]

# Preguntas de electrónica / firmware (prosa).
_ELECTRONICA = [
    ("¿Qué es un microcontrolador STM32 y para qué se usa?", ["STM32"]),
    ("Explícame qué es el firmware de un dispositivo embebido.", ["firmware"]),
    ("¿Qué diferencia hay entre un ESP32 y un Arduino Uno?", ["ESP32", "Arduino"]),
    ("¿Qué es la comunicación serial (UART) entre una computadora y una board?", ["serial", "UART"]),
    ("Explícame qué es el baud rate en una conexión serial.", ["baud"]),
    ("¿Qué es un pin GPIO en un microcontrolador?", ["GPIO", "pin"]),
    ("¿Qué es PWM y para qué se usa en electrónica?", ["PWM"]),
    ("Explícame qué es un bootloader en un microcontrolador.", ["bootloader"]),
    ("¿Qué es el protocolo I2C y cuántas líneas usa?", ["I2C"]),
    ("¿Qué es un toolchain cuando compilas firmware?", ["toolchain"]),
]

# Preguntas sobre la propia Tlamatini y su interfaz en español (autoconocimiento).
_PRODUCTO = [
    ("¿Qué es Tlamatini y para qué sirve?", ["Tlamatini"]),
    ("¿Qué significa el modo Multi-Turn en Tlamatini?", ["Multi-Turn"]),
    ("¿Qué es el Exec report en Tlamatini?", ["Exec report"]),
    ("Explícame qué hace el Compact mode.", ["Compact mode"]),
    ("¿Qué es el Self-modify en Tlamatini?", ["Self-modify"]),
    ("¿Qué es el Agentic Control Panel?", ["Agentic Control Panel"]),
    ("¿Qué es el Prompt Flow Panel y para qué se usa?", ["Prompt Flow Panel", "flow"]),
    ("¿Qué es un flow de agents en Tlamatini?", ["flow", "agents"]),
    ("¿Qué es el canvas en la interfaz de Tlamatini?", ["canvas"]),
    ("¿Qué es el medidor CONTEXT-WINDOW que aparece arriba del chat?", ["CONTEXT-WINDOW"]),
    ("¿Qué es ACPX en Tlamatini?", ["ACPX"]),
    ("¿Qué son los MCPs en Tlamatini?", ["MCP"]),
    ("¿Qué es un skill en el contexto de Tlamatini?", ["skill"]),
    ("¿Qué es el Catálogo de prompts?", ["prompt", "catálogo"]),
    ("¿Quién es la creadora de Tlamatini?", ["Angela"]),
    ("¿Qué es el área Terminals (Views ▸ Terminals) en Tlamatini?", ["Terminals", "terminal"]),
    ("¿Para qué sirve el Access Keys Wizard?", ["Access Keys Wizard", "key"]),
    ("¿Qué hace el botón Reconectar en la barra de herramientas?", ["reconect"]),
    ("¿Qué es el Interactor (el tutor del editor en vivo)?", ["Interactor", "editor"]),
    ("¿En qué idioma me vas a responder a partir de ahora?", ["español"]),
]

# Una pizca de operaciones de SOLO-LECTURA, seguras de repetir.
_OPS_SEGURAS = [
    ("¿Qué hora es en este momento?", ["hora"]),
    ("¿Qué día de la semana es hoy?", ["día"]),
    ("Enlístame los skills que tienes disponibles.", ["skill"]),
    ("¿Cuántos agents tienes en tu catálogo, más o menos?", ["agent"]),
    ("Dame una lista corta de tres cosas que puedes hacer por mí.", ["puedo", "ayud"]),
]


def _agent_q(i: int, nombre: str, kws: List[str]) -> Dict[str, Any]:
    return {"id": f"P{i:03d}", "category": "conocimiento-agent",
            "text": f"¿Qué hace el agent {nombre} y cuándo lo usarías?",
            "expect": [nombre] + kws, "min_len": 30}


def construir_preguntas() -> List[Dict[str, Any]]:
    """Exactamente 100 prompts en español, en orden estable."""
    out: List[Dict[str, Any]] = []
    for nombre, kws in _AGENTS:  # 30
        out.append(_agent_q(len(out) + 1, nombre, kws))
    for texto, kws in _GENERAL:  # 30
        out.append({"id": f"P{len(out) + 1:03d}", "category": "general", "text": texto,
                    "expect": kws, "min_len": 40})
    for texto, kws in _ELECTRONICA:  # 10
        out.append({"id": f"P{len(out) + 1:03d}", "category": "electronica", "text": texto,
                    "expect": kws, "min_len": 30})
    for texto, kws in _PRODUCTO:  # 20
        out.append({"id": f"P{len(out) + 1:03d}", "category": "producto", "text": texto,
                    "expect": kws, "min_len": 25})
    for texto, kws in _OPS_SEGURAS:  # 5
        out.append({"id": f"P{len(out) + 1:03d}", "category": "op-segura", "text": texto,
                    "expect": kws, "min_len": 10})
    return out


if __name__ == "__main__":
    import sys
    qs = construir_preguntas()
    sys.stdout.reconfigure(encoding="utf-8")
    assert len(qs) == 100, f"se esperaban 100, hay {len(qs)}"
    assert len({q['id'] for q in qs}) == 100, "ids duplicados"
    print(f"{len(qs)} prompts en español, ids {qs[0]['id']}..{qs[-1]['id']}")
    for q in qs[:3] + qs[-3:]:
        print(q["id"], q["category"], "|", q["text"])
