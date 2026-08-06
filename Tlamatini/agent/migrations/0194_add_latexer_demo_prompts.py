# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Seed the LaTeXer Catalog-of-Prompts demos, IN SPANISH (Angela, 2026-08-05).

MANDATORY GATE: a Multi-Turn agent shipped WITHOUT at least one catalog prompt is
INCOMPLETE. LaTeXer gets four, appended at ids 114-117 after PDFer's 109-113 — ids are
APPENDED, never renumbered.

They live in the existing ``documents`` category alongside PDFer and are ranked 60/70/
80/90, i.e. AFTER every PDFer card. That ordering is deliberate and follows the
least-complex → most-complex rule: PDFer needs NOTHING installed, whereas LaTeXer needs
**MiKTeX** on the machine, so a reader meets the zero-setup document tool first and the
one with a prerequisite second. Rank 10 of this section is already held by PDFer's
Step-by-Step opener (a section has exactly one), so LaTeXer's own wizard takes 60.

SPANISH EDITION — TWO DIFFERENCES FROM UPSTREAM, BOTH DELIBERATE
----------------------------------------------------------------
1. **RENUMBERED.** Upstream (English) ships this as 0193; here 0191 is already taken by
   ``0191_translate_prompt_catalog_to_spanish``, so the LaTeXer trio is 0192/0193/0194.
   This file depends on 0193 and therefore runs AFTER the catalog is Spanish — the four
   cards below are appended to an already-translated catalog, so it stays 100% Spanish.

2. **TRANSLATED.** ``promptContent`` is Mexican Spanish, following exactly the contract
   0191 established: Spanish supplies the grammar, English supplies the technical
   vocabulary, and every FUNCTIONAL token is preserved BYTE-EXACT — tool names
   (``chat_agent_latexer`` / ``chat_agent_file_creator``), the agent display name
   ``LaTeXer``, action values, ``INI_SECTION_LATEXER``, the ``[[ ]]`` user-input blocks,
   the ``&lt; &gt;`` report slots and the closing ``END-RESPONSE``.

   ⚠️ THE CLASSIFIER IS WHY THE WORDING IS NOT FREE. ``tools_dialog.js::
   classifyPromptModes`` decides which toolbar checkboxes a card ticks by READING THIS
   TEXT, and it is bilingual. Two consequences enforced below:
     * The WIZARD must tick Step-by-Step, which in Spanish requires an activation verb
       (marca / activa / prende / …) within 80 non-period characters of the HYPHENATED
       toolbar name ``Paso-a-Paso``. "paso a paso" with spaces deliberately does NOT
       match, so descriptive prose can never trip it — hence the hyphens here.
     * The other three must NOT tick it, so they never name Paso-a-Paso at all.
   Neither may contain an ``acp_*`` token, or the card would falsely light up ACPX.

Every prompt drives ``chat_agent_latexer`` with a realistic, SAFE, repeatable task:
they only ever write into LaTeXer's own output folder, never delete anything the user
cares about, and never enable ``shell_escape``. The daily chat test may run them.
Reverse deletes exactly these four rows.
"""
from django.db import migrations


# ── rank 60 · id 114 — LaTeXer's guided Step-by-Step tour ────────────────────
WIZARD = (
    "Tlamatini, sé mi <b>ASISTENTE PASO-A-PASO DE LaTeXer</b> — llévame desde cero hasta un "
    "PDF de LaTeX de verdad, tipografiado y guardado en mi disco, <b>una acción a la vez</b>."
    "<br><br>"

    "REQUISITOS PREVIOS: marca <b>Multi-Turn</b> Y <b>Paso-a-Paso</b> en la barra de "
    "herramientas (darle clic a esta tarjeta ya te los marca). Deja ACPX y Add-internet sin "
    "marcar. <b>Ask Execs</b> queda a tu gusto — LaTeXer está en la lista de Ask Execs porque "
    "escribe archivos y corre un compilador de verdad, así que con esa casilla marcada te sale "
    "un Proceed/Deny antes de cada corrida.<br><br>"

    "EL ÚNICO REQUISITO: <b>MiKTeX</b> (https://miktex.org/download). Tlamatini no trae una "
    "distribución de TeX — pesan varios gigabytes. MiKTeX se instala una sola vez y de ahí en "
    "adelante LaTeXer funciona para siempre, porque MiKTeX descarga solo cualquier package de "
    "LaTeX que falte mientras el documento se está construyendo. El PASO 1 revisa justo "
    "esto.<br><br>"

    "LLENA ESTOS DATOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS SON "
    "OPCIONALES; si dejo un corchete sin tocar, USA EL DEFAULT y NO me preguntes):<br>"
    "• TÍTULO DEL DOCUMENTO: [[ el título de la primera página — OPCIONAL, default: "
    "Mi Primer Documento en LaTeX ]]<br>"
    "• MI NOMBRE: [[ la línea de autor — OPCIONAL, default: Tlamatini ]]<br>"
    "• IDIOMA: [[ en o es — OPCIONAL, default: es ]]<br><br>"

    "CÓMO TE DEBES COMPORTAR — esto es lo importante: haz EXACTAMENTE UNA acción por turno, "
    "luego DETENTE y ESPÉRAME. Después de cada acción muéstrame el resultado concreto, y "
    "termina con la única línea que me dice exactamente qué contestar (normalmente "
    "<code>READY</code>). Nunca encadenes dos pasos. Nunca supongas mi respuesta. Si un paso "
    "falla, dime claramente qué falló y qué revisar, y ESPERA — nunca te brinques adelante, y "
    "NUNCA digas que se produjo un PDF cuando <code>status</code> dice otra cosa.<br><br>"

    "LOS PASOS:<br><br>"

    "<b>PASO 1 — ¿ESTÁ INSTALADO LaTeX?</b> Llama <code>chat_agent_latexer</code> UNA sola vez "
    "con <code>action='validate'</code>. Esto NO escribe ningún archivo. Lee el bloque "
    "<code>INI_SECTION_LATEXER</code> y muéstrame &lt;distribution&gt;, la ruta del engine, y "
    "cuáles de latexmk / biber / bibtex / makeindex se encontraron. Si &lt;distribution&gt; es "
    "<code>miktex</code>, dime que ya estoy completamente listo. Si es <code>none</code>, dime "
    "claramente que debo instalar <b>MiKTeX</b> desde https://miktex.org/download (o que puedo "
    "contestar <code>INSTALL</code> y tú llamarás <code>action='install'</code> para descargar "
    "y lanzar el instalador oficial por mí), y DETENTE ahí. Si no, pídeme que conteste "
    "<code>READY</code>. ESPERA.<br><br>"

    "<b>PASO 2 — TIPOGRAFÍA ALGO EN UNA SOLA LLAMADA.</b> Llama "
    "<code>chat_agent_latexer</code> UNA sola vez con <code>action='compile'</code>, "
    "<code>title='&lt;TÍTULO DEL DOCUMENTO&gt;'</code>, "
    "<code>author='&lt;MI NOMBRE&gt;'</code>, <code>document_language='&lt;IDIOMA&gt;'</code>, "
    "<code>filename='latexer_wizard_step2.pdf'</code> y exactamente este "
    "<code>input_text</code>: <code>Hola desde Tlamatini. LaTeX compone matemáticas de verdad: "
    "$E = mc^2$.</code><br>"
    "Hazme notar que le pasé un FRAGMENTO pelón — sin <code>\\\\documentclass</code>, sin "
    "<code>\\\\begin{document}</code> — y que LaTeXer lo envolvió solo en un preámbulo completo "
    "(eso es <code>auto_preamble</code>). Repórtame &lt;status&gt;, el &lt;output_path&gt; "
    "COMPLETO, &lt;page_count&gt; y &lt;passes&gt;. Dime que abra el archivo. Pídeme que "
    "conteste <code>READY</code>. ESPERA.<br><br>"

    "<b>PASO 3 — MATEMÁTICAS DE VERDAD Y UNA REFERENCIA CRUZADA.</b> Llama "
    "<code>chat_agent_latexer</code> UNA sola vez con <code>action='compile'</code>, "
    "<code>filename='latexer_wizard_step3.pdf'</code> y un <code>input_text</code> que "
    "contenga un entorno <code>equation</code> numerado con su <code>\\\\label</code>, y una "
    "oración que se refiera a ella con <code>\\\\eqref</code>. Repórtame &lt;passes&gt; y "
    "explícame en UN párrafo corto por qué LaTeX necesitó más de una pasada: la primera pasada "
    "todavía no sabe qué número le tocó a la ecuación, así que LaTeXer sigue re-corriendo "
    "hasta que las referencias dejan de cambiar. Pídeme que conteste <code>READY</code>. "
    "ESPERA.<br><br>"

    "<b>PASO 4 — REVISAR SIN COMPILAR.</b> Llama <code>chat_agent_latexer</code> UNA sola vez "
    "con <code>action='validate_tex'</code> y un <code>input_text</code> roto a propósito — un "
    "<code>\\\\begin{itemize}</code> sin su <code>\\\\end</code> correspondiente. Muéstrame el "
    "error que nombra y el número de línea. Explícame que esta revisión es ESTÁTICA: lee el "
    "código fuente y no necesita LaTeX instalado para nada. Pídeme que conteste "
    "<code>READY</code>. ESPERA.<br><br>"

    "<b>PASO 5 — MIRA CÓMO SE NIEGA A PRUEBA DE FALLAS (no se rompe nada).</b> Llama "
    "<code>chat_agent_latexer</code> UNA sola vez con <code>action='compile'</code> y SIN "
    "ninguna fuente — sin <code>input_text</code>, sin <code>tex_path</code>, sin "
    "<code>project_dir</code>. NO va a tronar y NO va a escribir un PDF vacío: su preflight se "
    "niega. Muéstrame &lt;status&gt; = <code>refused</code> y cítame el bloqueo. Explícame que "
    "así es como LaTeXer está DISEÑADO para portarse, y que un Forker en el canvas puede "
    "ramificar sobre ese <code>{status}</code>. Pídeme que conteste <code>READY</code>. "
    "ESPERA.<br><br>"

    "<b>PASO 6 — CIERRE.</b> NO llames ninguna tool. Imprime una tabla corta con los archivos "
    "que hiciste, sus rutas completas y su número de páginas, y luego una línea que enliste "
    "las actions que puedo usar después (<code>compile</code>, <code>compile_project</code>, "
    "<code>scaffold_compile</code>, <code>create_from_template</code>, <code>edit_file</code>, "
    "<code>structure</code>, <code>clean</code>). Termina con END-RESPONSE."
)

# ── rank 70 · id 115 — the simplest possible one-call demo ───────────────────
SIMPLE = (
    "Tlamatini, corre el <b>DEMO RÁPIDO DE LaTeXer</b>, por favor — tipografía un PDF de LaTeX "
    "de verdad en una sola llamada. Marca SOLO la casilla de <b>Multi-Turn</b>; usa ÚNICAMENTE "
    "<code>chat_agent_latexer</code>.<br><br>"

    "LLENA ESTOS DATOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS SON "
    "OPCIONALES; si dejo un corchete sin tocar, USA EL DEFAULT y NO me preguntes primero):<br>"
    "• TÍTULO: [[ el título del documento — OPCIONAL, default: Matemáticas, Bien Compuestas "
    "]]<br>"
    "• IDIOMA: [[ en o es — OPCIONAL, default: es ]]<br><br>"

    "REVISIÓN DE SEGURIDAD — esto solo escribe UN PDF nuevo dentro de la carpeta de salida del "
    "propio LaTeXer. No sobrescribe nada mío y no borra nada. Requiere <b>MiKTeX</b> "
    "(https://miktex.org/download); si falta, LaTeXer se va a NEGAR con calma y me lo va a "
    "decir — repórtame eso en vez de fingir que el PDF existe.<br><br>"

    "LA TAREA: llama <code>chat_agent_latexer</code> EXACTAMENTE UNA VEZ con "
    "<code>action='compile'</code>, <code>title='&lt;TÍTULO&gt;'</code>, "
    "<code>document_language='&lt;IDIOMA&gt;'</code>, "
    "<code>filename='latexer_quick_demo.pdf'</code>, y un <code>input_text</code> con una "
    "sección corta que luzca lo que LaTeX hace mejor — una fórmula en línea, una integral "
    "desplegada, y una lista <code>itemize</code> chiquita. Luego repórtame los valores del "
    "<code>INI_SECTION_LATEXER</code>: &lt;status&gt;, el &lt;output_path&gt; COMPLETO que "
    "debo abrir, &lt;page_count&gt;, &lt;bytes&gt;, &lt;engine&gt; y &lt;distribution&gt;. Si "
    "&lt;status&gt; es cualquier cosa que no sea <code>compiled</code>, cítame el bloqueo o "
    "los errores de LaTeX tal cual y NO lo llames un éxito. Termina con END-RESPONSE."
)

# ── rank 80 · id 116 — a real paper: bibliography + cross-references ─────────
PAPER = (
    "Tlamatini, corre el <b>DEMO DE PAPER ACADÉMICO DE LaTeXer</b>, por favor — arma un paper "
    "chiquito con una bibliografía real y referencias cruzadas que sí funcionen, que es "
    "justamente para lo que existe LaTeX. Marca SOLO la casilla de <b>Multi-Turn</b>; usa "
    "ÚNICAMENTE <code>chat_agent_latexer</code> y <code>chat_agent_file_creator</code>.<br><br>"

    "LLENA ESTOS DATOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS SON "
    "OPCIONALES; si dejo un corchete sin tocar, USA EL DEFAULT y NO me preguntes primero):<br>"
    "• TÍTULO DEL PAPER: [[ el título — OPCIONAL, default: Una Nota Breve sobre Tipografía "
    "]]<br>"
    "• AUTOR: [[ la línea de autor — OPCIONAL, default: Tlamatini ]]<br><br>"

    "REVISIÓN DE SEGURIDAD — todo se escribe en una carpeta NUEVA dentro del directorio "
    "Templates del propio Tlamatini. No se toca nada de lo que ya existe. Requiere "
    "<b>MiKTeX</b> (https://miktex.org/download); en la primera corrida MiKTeX puede pausarse "
    "para descargar solo el package biblatex — eso es normal y pasa una sola vez.<br><br>"

    "PASO 1 — ESCRIBE LA BIBLIOGRAFÍA. Usa <code>chat_agent_file_creator</code> UNA sola vez "
    "para escribir <code>refs.bib</code> dentro de una carpeta nueva "
    "<code>latexer_paper_demo</code> bajo el directorio Templates de Tlamatini, con DOS "
    "entradas <code>@book</code> cuyas llaves sean <code>knuth1984</code> y "
    "<code>lamport1994</code> (The TeXbook de Knuth, y LaTeX: A Document Preparation System de "
    "Lamport).<br><br>"

    "PASO 2 — ESCRIBE EL PAPER. Usa <code>chat_agent_file_creator</code> UNA sola vez para "
    "escribir <code>main.tex</code> en ESA MISMA carpeta: un <code>article</code> que cargue "
    "<code>biblatex</code> con <code>backend=biber</code>, llame "
    "<code>\\\\addbibresource{refs.bib}</code>, tenga una sección con título y su "
    "<code>\\\\label</code>, una segunda sección que se refiera a ella con "
    "<code>\\\\ref</code>, cite AMBAS llaves con <code>\\\\cite</code>, y termine con "
    "<code>\\\\printbibliography</code>.<br><br>"

    "PASO 3 — TIPOGRAFÍA EL PROYECTO COMPLETO. Llama <code>chat_agent_latexer</code> "
    "EXACTAMENTE UNA VEZ con <code>action='compile_project'</code> y <code>project_dir</code> "
    "apuntando a esa carpeta. NO le nombres un archivo principal — deja que LaTeXer detecte "
    "solo el documento maestro.<br><br>"

    "LUEGO REPORTA: &lt;status&gt;, el &lt;output_path&gt; COMPLETO, &lt;page_count&gt;, "
    "&lt;bibliography&gt; (debe decir <code>biber</code>, escogido automáticamente a partir "
    "del código fuente) y &lt;passes&gt;. Explícame en UN párrafo corto qué hicieron esas "
    "pasadas: tipografiar una vez, correr biber para resolver las citas, y tipografiar otra "
    "vez hasta que los números dejan de moverse. Dime que abra el PDF y revise que las dos "
    "citas aparecen como [1] y [2] con una lista de referencias real al final. Si "
    "&lt;status&gt; no es <code>compiled</code>, cítame los errores tal cual. Termina con "
    "END-RESPONSE."
)

# ── rank 90 · id 117 — templates, in one call ────────────────────────────────
TEMPLATE = (
    "Tlamatini, corre el <b>DEMO DE TEMPLATES DE LaTeXer</b>, por favor — convierte uno de los "
    "templates que ya vienen incluidos en un PDF terminado, en una sola llamada. Marca SOLO la "
    "casilla de <b>Multi-Turn</b>; usa ÚNICAMENTE <code>chat_agent_latexer</code>.<br><br>"

    "LLENA ESTOS DATOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS SON "
    "OPCIONALES; si dejo un corchete sin tocar, USA EL DEFAULT y NO me preguntes primero):<br>"
    "• TEMPLATE: [[ uno de article, report, book, beamer, letter, cv, homework, "
    "spanish-article — OPCIONAL, default: beamer ]]<br>"
    "• TÍTULO: [[ el título — OPCIONAL, default: Tlamatini Tipografía ]]<br>"
    "• AUTOR: [[ la línea de autor — OPCIONAL, default: Tlamatini ]]<br><br>"

    "REVISIÓN DE SEGURIDAD — esto crea UN .tex nuevo en una carpeta nueva bajo el directorio "
    "Templates de Tlamatini y UN PDF nuevo en la carpeta de salida de LaTeXer. No se "
    "sobrescribe nada de lo que ya existe. Requiere <b>MiKTeX</b> "
    "(https://miktex.org/download); con beamer la primera construcción puede pausarse mientras "
    "MiKTeX descarga sola la clase beamer — es normal, y pasa una sola vez.<br><br>"

    "LA TAREA: llama <code>chat_agent_latexer</code> EXACTAMENTE UNA VEZ con "
    "<code>action='scaffold_compile'</code>, <code>template='&lt;TEMPLATE&gt;'</code>, "
    "<code>title='&lt;TÍTULO&gt;'</code>, <code>author='&lt;AUTOR&gt;'</code>, "
    "<code>content</code> con una o dos oraciones que le queden a ese template, y "
    "<code>filename='latexer_template_demo.pdf'</code>. Esa sola action genera el código "
    "fuente desde el template, lo tipografía, y entrega el PDF.<br><br>"

    "LUEGO REPORTA: &lt;status&gt;, el &lt;tex_path&gt; del código fuente que generó (para que "
    "yo lo pueda editar después), el &lt;output_path&gt; COMPLETO del PDF, y "
    "&lt;page_count&gt;. Cierra con UNA línea que me diga cómo cambiar ese código después — "
    "<code>action='edit_file'</code> con <code>edit_mode</code>, <code>find_text</code> y "
    "<code>replace_text</code> — y luego volver a correr <code>action='compile'</code> sobre "
    "el mismo <code>tex_path</code>. Si &lt;status&gt; no es <code>compiled</code>, cítame el "
    "bloqueo o los errores de LaTeX tal cual. Termina con END-RESPONSE."
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
        ('agent', '0193_add_chat_agent_latexer_tool'),
    ]

    operations = [
        migrations.RunPython(add_latexer_demo_prompts, remove_latexer_demo_prompts),
    ]
