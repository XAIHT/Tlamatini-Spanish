"""Measurement harness for NEPANTLA Step 1.

Runs the REAL ``capability_registry`` scorer - not a reimplementation - over
two corpora and prints a JSON verdict, so the same script can be pointed at the
unmodified tree and at the patched tree and the two results diffed.

    python -m agent.i18n.eval_step1            # from <tree>/Tlamatini
    python agent/i18n/eval_step1.py --json     # machine-readable

WHY BOTH CORPORA
----------------
The Spanish corpus measures the gain. The English corpus measures the PRICE:
every row where the English top-1 moves must be adjudicated by hand as a fix or
a regression. Reporting only the gain would be dishonest, because N2 boundary
matching deliberately removes accidental substring hits, and some of those hits
were load-bearing for an English prompt's ranking.

THE SPANISH CORPUS IS WRITTEN IN THE REAL REGISTER
--------------------------------------------------
Spanish is the matrix language; English supplies the technical lexicon. So the
prompts below say *commit*, *push*, *repo*, *pods*, *containers*, *query*,
*screenshot*, *webcam*, *firmware*, *browser*, *zip*, *PDF* - exactly as a
Mexican developer writes them - inside Spanish grammar. A corpus that said
*confirmacion*, *empujar*, *repositorio* and *instantanea* would be measuring a
language nobody speaks, and would flatter the lexicon by giving it work that
reality does not send it.

A consequence worth reading off the results: several Spanish rows are expected
to pass on the ENGLISH nouns alone, with the lexicon contributing nothing. That
is the register doing the work, and it is the strongest form of the parity
argument - the smaller the share of vocabulary that moves between locales, the
smaller the surface on which the two languages can diverge.
"""

from __future__ import annotations

import json
import os
import sys

# --------------------------------------------------------------------------
# Django bootstrap. capability_registry reaches chat_agent_registry, which may
# touch settings; do the minimum and keep going if it is not needed.
# --------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))

# NEPANTLA_EVAL_TREE lets the SAME corpus be scored against a DIFFERENT tree -
# specifically the untouched original - so the BEFORE baseline and the AFTER
# result are produced by identical code and are directly comparable. Without
# this the harness could only ever measure the tree it happens to live in.
_TREE = (os.environ.get("NEPANTLA_EVAL_TREE") or "").strip() \
    or os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _TREE)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tlamatini.settings")
try:
    import django

    django.setup()
except Exception as exc:  # pragma: no cover - the scorer may not need Django
    print("--- [eval] django.setup() skipped: %s" % exc, file=sys.stderr)


# --------------------------------------------------------------------------
# Corpora
# --------------------------------------------------------------------------

# English. Expected top-1 is NOT asserted; what matters is BEFORE vs AFTER.
EN_CORPUS = [
    "Take a screenshot of the desktop",
    "Run the command dir in C:/temp and show me the output",
    "Create a file notes.txt with the content hello",
    "Delete every .tmp file in that folder",
    "Send an email to support with subject Report",
    "Commit and push the changes to the repo",
    "Show me the pods and containers that are running",
    "Start the nginx container in Docker",
    "Search the code for where the normalize function is used",
    "List every .py file in the project",
    "SSH into the server 10.0.0.5 and run uptime",
    "Run a query against the database and show me the rows",
    "Record a 5 second video with the webcam",
    "Record 10 seconds of audio from the microphone",
    "Transcribe that audio to text",
    "Read report.pdf and summarize it for me",
    "Run an nmap scan against scanme.nmap.org",
    "Build and flash the firmware to the ESP32",
    "Open the browser and navigate to example.com",
    "Unzip the archive in C:/temp",
    "Generate a PDF with the report",
    "Replace that line in config.py",
    "Send a WhatsApp message to Juan",
    "Decompile the jar at C:/tmp/app.jar",
    "Move all the logs into the archive folder",
    "Take a photo with the camera",
    "Play that mp3 through the speakers",
    "Say hello out loud",
    "Check the open ports with netstat",
    "Summarize this log file",
]

# Spanish, in the register Angela actually uses. The expected tool is the
# GROUND TRUTH for top-1; ``notes`` records why the row is interesting.
ES_CORPUS = [
    ("Mu\u00e9strame una screenshot del desktop", "chat_agent_shoter",
     "English noun carries it"),
    ("Corre el comando dir en la carpeta C:/temp", "execute_command",
     "Spanish verb + English 'comando'"),
    ("Crea un archivo llamado notas.txt con el texto hola", "chat_agent_file_creator",
     "pure Spanish carrier - needs the lexicon"),
    ("Borra todos los archivos .tmp de esa carpeta", "chat_agent_deleter",
     "pure Spanish carrier - needs the lexicon"),
    ("Env\u00eda un email a soporte con el subject Reporte", "chat_agent_send_email",
     "THE HOMOGRAPH CASE - 'ue' inside prueba used to hand this to Unrealer"),
    ("Haz un commit y push de los cambios al repo", "chat_agent_gitter",
     "English nouns carry it"),
    ("Mu\u00e9strame los pods y los containers que est\u00e1n corriendo", "chat_agent_kuberneter",
     "English nouns carry it"),
    ("Levanta el container de nginx en Docker", "chat_agent_dockerer",
     "English nouns carry it"),
    ("B\u00fascame en el c\u00f3digo d\u00f3nde se usa la funci\u00f3n normalize", "chat_agent_grepper",
     "accented codigo/funcion - the folding case"),
    ("L\u00edstame todos los archivos .py del proyecto", "chat_agent_globber",
     "pure Spanish carrier"),
    ("Con\u00e9ctate por SSH al server 10.0.0.5 y corre uptime", "chat_agent_ssher",
     "English nouns carry it"),
    ("Hazme un query a la base de datos y mu\u00e9strame los resultados", "chat_agent_sqler",
     "English 'query' carries it"),
    ("Gr\u00e1bame un video con la webcam por 5 segundos", "chat_agent_camcorder",
     "English 'webcam' carries it"),
    ("Graba audio del micr\u00f3fono por 10 segundos", "chat_agent_recorder",
     "accented microfono - the folding case"),
    ("Transcribe ese audio a texto", "chat_agent_whisperer",
     "cognate verb"),
    ("Lee el archivo report.pdf y hazme un resumen", "chat_agent_file_extractor",
     "pure Spanish carrier"),
    ("Corre un scan de nmap contra scanme.nmap.org", "chat_agent_nmapper",
     "English nouns carry it"),
    ("Compila y flashea el firmware al ESP32", "chat_agent_esp32er",
     "Spanglish verb 'flashea' + English nouns"),
    ("\u00c1breme el browser y navega a example.com", "chat_agent_playwrighter",
     "English 'browser' carries it"),
    ("Descomprime el zip que est\u00e1 en C:/temp", "unzip_file",
     "Spanish verb + English 'zip'"),
    ("Gen\u00e9rame un PDF con el reporte", "chat_agent_pdfer",
     "English 'PDF' carries it"),
    ("Reemplaza esa l\u00ednea en el archivo config.py", "chat_agent_editor",
     "pure Spanish carrier"),
    ("Mand\u00e1le un mensaje de WhatsApp a Juan", "chat_agent_whatsapper",
     "English 'WhatsApp' carries it"),
    ("Decompila el jar que est\u00e1 en C:/tmp/app.jar", "decompile_java",
     "Spanish verb + English 'jar'"),
    ("Mueve todos los logs a la carpeta de archive", "chat_agent_move_file",
     "pure Spanish carrier + English 'logs'"),
    ("T\u00f3mame una foto con la c\u00e1mara", "chat_agent_camcorder",
     "pure Spanish carrier, accented camara"),
    ("Reproduce ese mp3 en las bocinas", "chat_agent_audioplayer",
     "Mexican 'bocinas' + English mp3"),
    ("Di hola en voz alta", "chat_agent_talker",
     "pure Spanish carrier"),
    ("Rev\u00edsame los puertos abiertos con netstat", "chat_agent_monitor_netstat",
     "English 'netstat' carries it"),
    ("Res\u00fameme este archivo de log", "chat_agent_summarize_text",
     "pure Spanish carrier + English 'log'; the wrapped agent is "
     "Summarize Text - an earlier revision of this corpus wrongly "
     "expected a non-existent 'Summarizer' tool"),
]


def _load_scorer():
    from agent import capability_registry as cr
    from agent.tools import get_mcp_tools

    return cr, get_mcp_tools


def _rank(cr, tools, text, top_n=3):
    """Return the top-N (tool_name, score) using the REAL scorer."""
    normalized = cr.normalize_request(text) if hasattr(cr, "normalize_request") \
        else cr._normalize_text(text)
    tokens = cr._tokenize(normalized)
    capabilities = cr.build_tool_capabilities(tools)
    scored = []
    for cap in capabilities:
        score = cr._score_capability(cap, normalized, tokens)
        scored.append((cap.tool_name, score))
    scored.sort(key=lambda row: (-row[1], row[0]))
    return scored[:top_n]


def main() -> int:
    cr, get_mcp_tools = _load_scorer()
    tools = get_mcp_tools()

    patched = hasattr(cr, "normalize_request")
    result = {
        "tree": _TREE,
        "patched": patched,
        "nepantla_scoring": getattr(cr, "_NEPANTLA_SCORING", None),
        "nepantla_lexicon": getattr(cr, "_NEPANTLA_LEXICON", None),
        "tool_count": len(tools),
        "english": [],
        "spanish": [],
    }

    for text in EN_CORPUS:
        top = _rank(cr, tools, text)
        result["english"].append({
            "prompt": text,
            "top1": top[0][0] if top else None,
            "top1_score": top[0][1] if top else 0,
            "top3": top,
        })

    hits = 0
    for text, expected, note in ES_CORPUS:
        top = _rank(cr, tools, text)
        top1 = top[0][0] if top else None
        ok = (top1 == expected)
        hits += 1 if ok else 0
        result["spanish"].append({
            "prompt": text,
            "expected": expected,
            "top1": top1,
            "top1_score": top[0][1] if top else 0,
            "hit": ok,
            "note": note,
            "top3": top,
        })
    result["spanish_top1"] = "%d/%d" % (hits, len(ES_CORPUS))

    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("tree              : %s" % result["tree"])
    print("patched           : %s" % patched)
    print("scoring / lexicon : %s / %s" % (result["nepantla_scoring"],
                                           result["nepantla_lexicon"]))
    print("tools bound       : %d" % result["tool_count"])
    print()
    print("SPANISH top-1     : %s" % result["spanish_top1"])
    print()
    for row in result["spanish"]:
        print("  %s %-34s  %s" % ("OK " if row["hit"] else "MISS",
                                  str(row["top1"])[:34], row["prompt"]))
        if not row["hit"]:
            print("       expected %s   (%s)" % (row["expected"], row["note"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
