# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Seed the LaTeXer Catalog-of-Prompts demos (Angela, 2026-08-05).

MANDATORY GATE: a Multi-Turn agent shipped WITHOUT at least one catalog prompt is
INCOMPLETE. LaTeXer gets four, appended at ids 114-117 after PDFer's 109-113 — ids are
APPENDED, never renumbered.

They live in the existing ``documents`` category alongside PDFer and are ranked 60/70/
80/90, i.e. AFTER every PDFer card. That ordering is deliberate and follows the
least-complex → most-complex rule: PDFer needs NOTHING installed, whereas LaTeXer needs
**MiKTeX** on the machine, so a reader meets the zero-setup document tool first and the
one with a prerequisite second. Rank 10 of this section is already held by PDFer's
Step-by-Step opener (a section has exactly one), so LaTeXer's own wizard takes 60.

Every prompt drives ``chat_agent_latexer`` with a realistic, SAFE, repeatable task:
they only ever write into LaTeXer's own output folder, never delete anything the user
cares about, and never enable ``shell_escape``. The daily chat test may run them.
Reverse deletes exactly these four rows.
"""
from django.db import migrations


# ── rank 60 · id 114 — LaTeXer's guided Step-by-Step tour ────────────────────
WIZARD = (
    "Tlamatini, sé mi <b>WIZARD PASO A PASO DE LaTeXer</b> — llévame de cero a un PDF LaTeX real "
    "y compuesto en mi disco, <b>una acción a la "

    "vez</b>.<br><br>PRECONDICIONES: marca <b>Multi-Turn</b> y <b>Paso a paso</b> en la barra de herramientas (al hacer clic en "
    "esta tarjeta ya se marcan). Deja ACPX y Add-internet sin marcar. <b>Ask Execs</b> es tu "
    "decisión — LaTeXer está en la allowlist de Ask-Execs porque escribe archivos y corre un "
    "compilador real, así que con él marcado tendrás un prompt de Proceed/Deny antes de cada run.<br><br>EL "

    "ÚNICO PRERREQUISITO: <b>MiKTeX</b> (https://miktex.org/download). Tlamatini no "
    "incluye una distribución de TeX — pesan varios gigabytes. MiKTeX se instala una vez y "
    "luego LaTeXer funciona para siempre, porque MiKTeX descarga cualquier paquete LaTeX faltante "
    "automáticamente mientras un documento se construye. El PASO 1 revisa esto por mí.<br><br>LLENA "

    "ESTOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS OPCIONALES; si dejo un "
    "corchete sin tocar, USA EL PREDETERMINADO y NO me preguntes):<br>• "
    "DOCUMENT TITLE: [[ el título en la primera página — OPCIONAL, predeterminado: My "
    "First LaTeX Document ]]<br>• "
    "MY NAME: [[ la línea de autor — OPCIONAL, predeterminado: Tlamatini ]]<br>• "
    "LANGUAGE: [[ en o es — OPCIONAL, predeterminado: en ]]<br><br>CÓMO "

    "DEBES COMPORTARTE — este es el punto: haz EXACTAMENTE UNA acción por turno, luego "
    "DETENTE y ESPÉRAME. Después de cada acción, muéstrame el resultado concreto, luego termina con la "
    "única línea que me dice exactamente qué responder (normalmente <code>READY</code>). Nunca encadenes dos "
    "pasos. Nunca supongas mi respuesta. Si un paso falla, di claramente qué salió mal y qué revisar, y "
    "ESPERA — nunca te saltes pasos, y NUNCA afirmes que un PDF se produjo cuando "
    "<code>status</code> diga lo contrario.<br><br>LOS "

    "PASOS:<br><br><b>PASO "

    "1 — ¿LaTeX ESTÁ INSTALADO?</b> Llama a <code>chat_agent_latexer</code> UNA VEZ con "
    "<code>action='validate'</code>. Esto NO escribe ningún archivo. Lee el "
    "bloque <code>INI_SECTION_LATEXER</code> y muéstrame &lt;distribution&gt;, el path del engine y "
    "cuáles de latexmk / biber / bibtex / makeindex se encontraron. Si "
    "&lt;distribution&gt; es <code>miktex</code>, dime que estoy totalmente listo. Si es "
    "<code>none</code>, dime claramente que debo instalar <b>MiKTeX</b> desde "
    "https://miktex.org/download (o que puedo responder <code>INSTALL</code> y llamarás a "
    "<code>action='install'</code> para descargar y lanzar el instalador oficial por mí), y "
    "DETENTE ahí. Si no, pídeme que responda <code>READY</code>. ESPERA.<br><br><b>PASO "

    "2 — COMPÓN ALGO EN UNA LLAMADA.</b> Llama a <code>chat_agent_latexer</code> UNA VEZ con "
    "<code>action='compile'</code>, <code>title='&lt;DOCUMENT TITLE&gt;'</code>, "
    "<code>author='&lt;MY NAME&gt;'</code>, <code>document_language='&lt;LANGUAGE&gt;'</code>, "
    "<code>filename='latexer_wizard_step2.pdf'</code> y este exacto "
    "<code>input_text</code>: <code>Hola desde Tlamatini. LaTeX compone matemáticas reales: "
    "$E = mc^2$.</code><br>Señala "
    "que pasé un FRAGMENTO pelón — sin <code>\\\\documentclass</code>, sin "
    "<code>\\\\begin{document}</code> — y LaTeXer lo envolvió en un preámbulo propio por mí "
    "(eso es <code>auto_preamble</code>). Reporta &lt;status&gt;, el &lt;output_path&gt; COMPLETO, "
    "&lt;page_count&gt; y &lt;passes&gt;. Dime que abra el archivo. Pídeme que responda "
    "<code>READY</code>. ESPERA.<br><br><b>PASO "

    "3 — MATEMÁTICAS REALES Y UNA REFERENCIA CRUZADA.</b> Llama a "
    "<code>chat_agent_latexer</code> UNA VEZ con <code>action='compile'</code>, "
    "<code>filename='latexer_wizard_step3.pdf'</code> y un <code>input_text</code> que "
    "contenga un entorno <code>equation</code> numerado con un <code>\\\\label</code>, y una "
    "oración que haga referencia a él con <code>\\\\eqref</code>. Reporta &lt;passes&gt; y "
    "explica en UN párrafo corto por qué LaTeX necesitó más de una pasada: la primera pasada aún no "
    "conoce el número de la ecuación, así que LaTeXer sigue re-ejecutando hasta que las referencias dejan "
    "de cambiar. Pídeme que responda <code>READY</code>. ESPERA.<br><br><b>PASO "

    "4 — LINT SIN COMPILAR.</b> Llama a <code>chat_agent_latexer</code> UNA VEZ con "
    "<code>action='validate_tex'</code> y un <code>input_text</code> que esté deliberadamente roto "
    "— un <code>\\\\begin{itemize}</code> sin su <code>\\\\end</code> correspondiente. Muéstrame el "
    "error que nombra y el número de línea. Explica que esta comprobación es ESTÁTICA: lee el "
    "código y no necesita ningún LaTeX instalado. Pídeme que responda <code>READY</code>. "
    "ESPERA.<br><br><b>PASO "

    "5 — VE EL FAIL-SAFE RECHAZAR (nada se rompe).</b> Llama a "
    "<code>chat_agent_latexer</code> UNA VEZ con <code>action='compile'</code> y SIN código "
    "alguno — sin <code>input_text</code>, sin <code>tex_path</code>, sin <code>project_dir</code>. "
    "NO va a hacer crash y NO va a escribir un PDF vacío: su preflight rechaza. Muéstrame "
    "&lt;status&gt; = <code>refused</code> y cita el blocker. Explica que esto es LaTeXer "
    "funcionando como está DISEÑADO, y que un Forker en el canvas puede ramificarse según ese "
    "<code>{status}</code>. Pídeme que responda <code>READY</code>. ESPERA.<br><br><b>PASO "

    "6 — CIERRE.</b> NO llames a ningún tool. Imprime una tabla corta de los archivos que hiciste "
    "con sus paths completos y conteos de páginas, luego una línea que liste las actions que puedo usar después "
    "(<code>compile</code>, <code>compile_project</code>, <code>scaffold_compile</code>, "
    "<code>create_from_template</code>, <code>edit_file</code>, <code>structure</code>, "
    "<code>clean</code>). Termina con END-RESPONSE."
)

# ── rank 70 · id 115 — the simplest possible one-call demo ───────────────────
SIMPLE = (
    "Tlamatini, ejecuta la demo <b>LaTeXer EXPRÉS</b>, por favor — compón un PDF LaTeX real en una "
    "sola llamada. Marca SÓLO la casilla <b>Multi-Turn</b>; usa SÓLO "
    "<code>chat_agent_latexer</code>.<br><br>LLENA "

    "ESTOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS OPCIONALES; si dejo un "
    "corchete sin tocar, USA EL PREDETERMINADO y NO me preguntes primero):<br>• "
    "TITLE: [[ el título del documento — OPCIONAL, predeterminado: Mathematics, Set Properly ]]<br>• "
    "LANGUAGE: [[ en o es — OPCIONAL, predeterminado: en ]]<br><br>REVISIÓN "

    "DE SEGURIDAD — esto sólo escribe UN PDF nuevo en la propia carpeta de salida de LaTeXer. "
    "No sobrescribe nada mío y no borra nada. Requiere <b>MiKTeX</b> "
    "(https://miktex.org/download); si falta, LaTeXer RECHAZARÁ limpiamente y me lo dirá "
    "— reporta eso en lugar de fingir que un PDF existe.<br><br>LA "

    "TAREA: llama a <code>chat_agent_latexer</code> EXACTAMENTE UNA VEZ con "
    "<code>action='compile'</code>, <code>title='&lt;TITLE&gt;'</code>, "
    "<code>document_language='&lt;LANGUAGE&gt;'</code>, "
    "<code>filename='latexer_quick_demo.pdf'</code>, y un <code>input_text</code> con una "
    "sección corta que luzca lo que LaTeX hace mejor — una fórmula en línea, una "
    "integral mostrada y una lista <code>itemize</code> pequeña. Luego reporta los "
    "valores de <code>INI_SECTION_LATEXER</code>: &lt;status&gt;, el &lt;output_path&gt; COMPLETO que "
    "debo abrir, &lt;page_count&gt;, &lt;bytes&gt;, &lt;engine&gt; y &lt;distribution&gt;. "
    "Si &lt;status&gt; es algo distinto de <code>compiled</code>, cita el blocker o los "
    "errores de LaTeX tal cual y NO lo llames éxito. Termina con END-RESPONSE."
)

# ── rank 80 · id 116 — a real paper: bibliography + cross-references ─────────
PAPER = (
    "Tlamatini, ejecuta la demo <b>ARTÍCULO ACADÉMICO CON LaTeXer</b>, por favor — construye un artículo "
    "pequeño con una bibliografía real y referencias cruzadas que funcionan, para lo que LaTeX existe. Marca "
    "SÓLO la casilla <b>Multi-Turn</b>; usa SÓLO <code>chat_agent_latexer</code> "
    "y <code>chat_agent_file_creator</code>.<br><br>LLENA "

    "ESTOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS OPCIONALES; si "
    "dejo un corchete sin tocar, USA EL PREDETERMINADO y NO me preguntes primero):<br>• "
    "TÍTULO DEL ARTÍCULO: [[ el título — OPCIONAL, predeterminado: Una nota breve sobre "
    "tipografía ]]<br>• AUTHOR: [[ la línea de autor — OPCIONAL, predeterminado: "

    "Tlamatini ]]<br><br>REVISIÓN DE SEGURIDAD — todo se escribe en una carpeta NUEVA bajo el directorio Templates propio "
    "de Tlamatini. Nada existente se toca. Requiere "
    "<b>MiKTeX</b> (https://miktex.org/download); en el primer run MiKTeX puede pausar para "
    "descargar el paquete biblatex automáticamente — eso es normal y sólo pasa una "

    "vez.<br><br>PASO 1 — ESCRIBE LA BIBLIOGRAFÍA. Usa <code>chat_agent_file_creator</code> UNA VEZ "
    "para escribir <code>refs.bib</code> en una carpeta nueva <code>latexer_paper_demo</code> bajo el directorio Templates de "
    "Tlamatini, con DOS entradas <code>@book</code> con "
    "las keys <code>knuth1984</code> y <code>lamport1994</code> (The TeXbook de "
    "Knuth, y LaTeX: A Document Preparation System de "

    "Lamport).<br><br>PASO 2 — ESCRIBE EL ARTÍCULO. Usa <code>chat_agent_file_creator</code> UNA VEZ para "
    "escribir <code>main.tex</code> en ESA MISMA carpeta: un <code>article</code> "
    "que cargue <code>biblatex</code> con <code>backend=biber</code>, "
    "llame a <code>\\\\addbibresource{refs.bib}</code>, tenga una sección con título "
    "con un <code>\\\\label</code>, una segunda sección que haga referencia a "
    "ella con <code>\\\\ref</code>, cite AMBAS keys con <code>\\\\cite</code>, y termine "
    "con <code>\\\\printbibliography</code>.<br><br>PASO "

    "3 — COMPÓN TODO EL PROYECTO. Llama a <code>chat_agent_latexer</code> EXACTAMENTE UNA "
    "VEZ con <code>action='compile_project'</code> y <code>project_dir</code> puesto "
    "en esa carpeta. NO nombres un archivo principal — deja que LaTeXer auto-detecte el documento maestro.<br><br>LUEGO "

    "REPORTA: &lt;status&gt;, el &lt;output_path&gt; COMPLETO, &lt;page_count&gt;, "
    "&lt;bibliography&gt; (debería decir <code>biber</code>, elegido automáticamente desde "
    "el código) y &lt;passes&gt;. Explica en UN párrafo corto qué hicieron esas pasadas: "
    "componer una vez, correr biber para resolver las citas, luego componer de nuevo hasta que los números "
    "dejen de moverse. Dime que abra el PDF y revise que las dos citas aparezcan como [1] y "
    "[2] con una lista de referencias real al final. Si &lt;status&gt; no es "
    "<code>compiled</code>, cita los errores tal cual. Termina con END-RESPONSE."
)

# ── rank 90 · id 117 — templates, in one call ────────────────────────────────
TEMPLATE = (
    "Tlamatini, ejecuta la demo <b>PLANTILLAS DE LaTeXer</b>, por favor — convierte una de las plantillas "
    "integradas en un PDF terminado en una sola llamada. Marca SÓLO la casilla <b>Multi-Turn</b> "
    "; usa SÓLO <code>chat_agent_latexer</code>.<br><br>LLENA "

    "ESTOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS OPCIONALES; si dejo "
    "un corchete sin tocar, USA EL PREDETERMINADO y NO me preguntes primero):<br>• "
    "PLANTILLA: [[ uno de article, report, book, beamer, letter, cv, homework, "
    "spanish-article — OPCIONAL, predeterminado: beamer "
    "]]<br>• TITLE: [[ el título — OPCIONAL, predeterminado: Tlamatini Typesets "
    "]]<br>• AUTHOR: [[ la línea de autor — OPCIONAL, predeterminado: Tlamatini "

    "]]<br><br>REVISIÓN DE SEGURIDAD — esto crea UN .tex nuevo en una carpeta fresca bajo el directorio Templates de Tlamatini "
    "y UN PDF nuevo en la carpeta de salida de LaTeXer. Nada existente se sobrescribe. "
    "Requiere <b>MiKTeX</b> (https://miktex.org/download); con beamer el primer build puede "
    "pausar mientras MiKTeX descarga la clase beamer automáticamente — normal, y sólo "
    "once.<br><br>LA "

    "TAREA: llama a <code>chat_agent_latexer</code> EXACTAMENTE UNA VEZ con "
    "<code>action='scaffold_compile'</code>, <code>template='&lt;PLANTILLA&gt;'</code>, "
    "<code>title='&lt;TITLE&gt;'</code>, <code>author='&lt;AUTHOR&gt;'</code>, "
    "<code>content</code> puesto en una o dos oraciones que le queden a esa plantilla, y "
    "<code>filename='latexer_template_demo.pdf'</code>. Esa única action arma el "
    "código desde la plantilla, lo compone y entrega el PDF.<br><br>LUEGO "

    "REPORTA: &lt;status&gt;, el &lt;tex_path&gt; del código que generó (para que yo pueda "
    "editarlo después), el &lt;output_path&gt; COMPLETO del PDF y &lt;page_count&gt;. Termina "
    "con UNA línea diciéndome cómo cambiar ese código después — "
    "<code>action='edit_file'</code> con <code>edit_mode</code>, <code>find_text</code> y "
    "<code>replace_text</code> — y luego re-ejecutar <code>action='compile'</code> sobre el mismo "
    "<code>tex_path</code>. Si &lt;status&gt; no es <code>compiled</code>, cita el blocker o "
    "los errores de LaTeX tal cual. Termina con END-RESPONSE."
)


# (idPrompt, sort_rank, promptContent) — ids APPENDED after 113 (0190), never renumbered.
_NEW_PROMPTS = (
    (114, 60, WIZARD),
    (115, 70, SIMPLE),
    (116, 80, PAPER),
    (117, 90, TEMPLATE),
)


def add_latexer_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for pid, rank, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=pid,
            defaults={
                'promptName': f'prompt-{pid}',
                'promptContent': content,
                'category': 'documents',
                'hidden': False,
                'sort_rank': rank,
            },
        )


def remove_latexer_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _rank, _c in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0192_add_chat_agent_latexer_tool'),
    ]

    operations = [
        migrations.RunPython(add_latexer_demo_prompts, remove_latexer_demo_prompts),
    ]
