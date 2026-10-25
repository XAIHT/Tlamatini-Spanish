# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Catalog of Prompts — the NEW 'Documents & PDF' section for PDFer (Angela, 2026-07-26).

PDFer is the first agent in a genuinely new capability family (document AUTHORING),
so it gets its own catalog section — ``documents`` / "Documents & PDF", registered in
``views.PROMPT_CATEGORY_ORDER`` between 'Code & Project Generation' and
'Images & Vision'.

Contract compliance (all of it, deliberately):
  * APPEND-ONLY ids. 0187 left the catalog at 108, so these are 109..113. No existing
    ``idPrompt`` / ``promptName`` / ``category`` / ``sort_rank`` is touched, so the
    catalog stays contiguous and the gap-tolerant offline probe keeps working.
  * ``sort_rank`` decides the order INSIDE the section (migration 0181), so the cards
    read least-complex -> most-complex:
        10  (RESERVED slot) Step-by-Step wizard opener            -> id 109
        20  Markdown -> PDF, zero setup, one call                 -> id 110
        30  turn Tlamatini's OWN answer into a report             -> id 111
        40  images -> a PDF album (needs image files)             -> id 112
        50  full mixed report: capture + prose + cover + polish   -> id 113
    Rank 10 is the reserved Step-by-Step opener slot Angela requires in EVERY section,
    and it is pinned by ``test_prompt_catalog_contiguous`` in BOTH directions
    (``expected_first['documents'] = 109`` plus the content check that the opener
    actually names Step-by-Step and promises to WAIT).
  * Parameter grammar v1.44.0: ``[[ ]]`` = a value the USER fills in, always collected
    in a fill-in block at the TOP with an unfilled-guard line beneath so a one-click
    demo still runs on the stated defaults; ``< >`` = a REPORT slot only. No hardcoded
    scratch path anywhere — PDFer's own default (Documents/TlamatiniPDF) is used, which
    respects the Temp/Templates policy (Rules 15/16).
  * Every prompt drives ``chat_agent_pdfer`` with a realistic, SAFE, repeatable task:
    nothing is deleted, nothing is overwritten (PDFer's ``overwrite`` stays false, so a
    colliding name becomes _2/_3), and nothing is sent to a human.

Reverse deletes exactly these five rows.
"""
from django.db import migrations


# ── rank 10 · id 109 — the section's Step-by-Step opener (RESERVED slot) ──────
WIZARD = (
    "Tlamatini, sé mi <b>WIZARD PASO A PASO DE PDFer</b> — llévame de cero a un PDF real "
    "y con estilo en mi disco, <b>una acción a la vez</b>. Este es el recorrido guiado de la "
    "sección Documents &amp; "

    "PDF.<br><br>PRECONDICIONES: marca <b>Multi-Turn</b> y <b>Paso a paso</b> en la barra de herramientas (al hacer clic en "
    "esta tarjeta ya se marcan). Deja ACPX y Add-internet sin marcar. <b>Ask Execs</b> es tu "
    "decisión — PDFer está en la allowlist de Ask-Execs porque escribe un archivo, así que con él "
    "marcado tendrás un prompt de Proceed/Deny antes de cada render.<br><br>LLENA "

    "ESTOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS OPCIONALES; si dejo un "
    "corchete sin tocar, USA EL PREDETERMINADO y NO me preguntes):<br>• "
    "DOCUMENT TITLE: [[ el título impreso en la portada — OPCIONAL, predeterminado: My "
    "First Tlamatini Document ]]<br>• "
    "WHERE TO SAVE IT: [[ un path de carpeta — OPCIONAL, predeterminado: déjalo vacío para que PDFer use su "
    "propia carpeta Documents/TlamatiniPDF ]]<br>• "
    "PAGE SIZE: [[ A4 o Letter — OPCIONAL, predeterminado: A4 ]]<br><br>CÓMO "

    "DEBES COMPORTARTE — este es el punto: haz EXACTAMENTE UNA acción por turno, luego "
    "DETENTE y ESPÉRAME. Después de cada acción, muéstrame el resultado concreto, luego termina con la "
    "única línea que me dice exactamente qué responder (normalmente <code>READY</code>). Nunca encadenes dos "
    "pasos. Nunca supongas mi respuesta. Si un paso falla, di claramente qué salió mal y qué revisar, y "
    "ESPERA — nunca te saltes pasos, nunca finjas que un PDF fue creado.<br><br>LOS "

    "PASOS:<br><br><b>PASO "

    "1 — REVISA EL ENGINE.</b> Llama a <code>chat_agent_pdfer</code> UNA VEZ con "
    "<code>mode='validate'</code>. Esto NO escribe ningún archivo; sólo reporta qué backends de PDF son "
    "importables. Lee el bloque <code>INI_SECTION_PDFER</code> y muéstrame los seis backends "
    "(markdown, xhtml2pdf, pymupdf, reportlab, pillow, pypdf), el <code>status</code> "
    "&lt;status&gt; y la carpeta donde PDFer va a guardar &lt;output_dir&gt;. Dime claramente "
    "que PDFer NO necesita instalación — los seis ya vienen con Tlamatini. Pídeme que responda "
    "<code>READY</code>. ESPERA.<br><br><b>PASO "

    "2 — HAZ EL PDF MÁS SIMPLE POSIBLE.</b> Llama a <code>chat_agent_pdfer</code> UNA VEZ "
    "con <code>mode='markdown'</code>, <code>title='&lt;DOCUMENT TITLE&gt;'</code>, "
    "<code>page_size='&lt;PAGE SIZE&gt;'</code>, <code>filename='pdfer_wizard_step2.pdf'</code> "
    "(y <code>output_dir</code> sólo si te di una), y este exacto "
    "<code>input_text</code>:<br><code># "
    "Hola desde Tlamatini<br><br>Este documento lo escribió el agent **PDFer**.<br><br>| "
    "Parte | Qué hace |<br>|---|---|<br>| markdown | texto a HTML |<br>| "
    "xhtml2pdf | HTML a PDF |<br></code><br>Reporta "
    "el <code>status</code> &lt;status&gt;, el <code>output_path</code> COMPLETO "
    "&lt;output_path&gt;, <code>page_count</code> &lt;page_count&gt; y <code>bytes</code> "
    "&lt;bytes&gt;. Dime que abra ese archivo y confirme que veo el título, el texto en negrita "
    "y una tabla REAL de dos columnas. Pídeme que responda <code>READY</code>. ESPERA.<br><br><b>PASO "

    "3 — AGREGA UNA PORTADA Y NÚMEROS DE PÁGINA.</b> Explica en un párrafo corto qué "
    "hacen <code>title</code>, <code>subtitle</code> y <code>page_numbers</code>, luego llama a "
    "<code>chat_agent_pdfer</code> UNA VEZ con el mismo texto pero "
    "<code>subtitle='Made step by step with Tlamatini'</code>, <code>page_numbers=true</code>, "
    "<code>toc=true</code> y <code>filename='pdfer_wizard_step3.pdf'</code>. Reporta el nuevo "
    "&lt;output_path&gt; y &lt;page_count&gt;, y dime que la primera página ahora es una portada y el "
    "pie de página dice 'page N of M'. Pídeme que responda <code>READY</code>. ESPERA.<br><br><b>PASO "

    "4 — VE EL FAIL-SAFE RECHAZAR (nada se rompe).</b> Llama a "
    "<code>chat_agent_pdfer</code> UNA VEZ con <code>mode='markdown'</code> y un "
    "<code>input_text</code> VACÍO. NO va a hacer crash y NO va a escribir un archivo vacío — su "
    "preflight rechaza. Muéstrame <code>status</code> = <code>refused</code> y cita la "
    "línea del blocker. Explica que esto es PDFer funcionando como está DISEÑADO, y que un "
    "Forker aguas abajo en el canvas puede ramificarse según ese <code>{status}</code>. Pídeme que responda "
    "<code>READY</code>. ESPERA.<br><br><b>PASO "

    "5 — INSPECCIONA LO QUE CONSTRUISTE.</b> Llama a <code>chat_agent_pdfer</code> UNA VEZ con "
    "<code>mode='info'</code> y <code>input_file</code> puesto en el &lt;output_path&gt; del "
    "PASO 3. Muéstrame el conteo de páginas, el tamaño en bytes y los metadatos Title/Author/Producer que PDFer "
    "estampó. Pídeme que responda <code>READY</code>. ESPERA.<br><br><b>PASO "

    "6 — CIERRE.</b> NO llames a ningún tool. Imprime una tabla corta de los tres archivos que "
    "hiciste con sus paths completos y conteos de páginas, luego un recordatorio de una línea de los modes que puedo "
    "usar después (<code>markdown</code>, <code>html</code>, <code>text</code>, <code>images</code>, "
    "<code>mixed</code>, <code>merge</code>, <code>info</code>, <code>validate</code>) y que "
    "<code>mode='auto'</code> elige por mí. Termina con END-RESPONSE."
)

# ── rank 20 · id 110 — the simplest possible one-call demo ───────────────────
SIMPLE = (
    "Tlamatini, ejecuta la demo <b>PDFer EXPRÉS</b>, por favor — hazme un PDF con estilo en una sola "
    "llamada. Marca SÓLO la casilla <b>Multi-Turn</b>; usa SÓLO "
    "<code>chat_agent_pdfer</code>.<br><br>LLENA "

    "ESTOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS OPCIONALES; si dejo un "
    "corchete sin tocar, USA EL PREDETERMINADO y NO me preguntes primero):<br>• "
    "TITLE: [[ el título del documento — OPCIONAL, predeterminado: Tlamatini Agent Cheat-Sheet ]]<br>• "
    "FILE NAME: [[ OPCIONAL, predeterminado: tlamatini_cheatsheet.pdf ]]<br><br>Llama "

    "a <code>chat_agent_pdfer</code> EXACTAMENTE UNA VEZ con <code>mode='markdown'</code>, "
    "<code>title='&lt;TITLE&gt;'</code>, <code>filename='&lt;FILE NAME&gt;'</code>, "
    "<code>page_numbers=true</code>, y un <code>input_text</code> que sea un cheat-sheet corto en Markdown "
    "que escribas tú misma: un encabezado <code># </code>, una oración de intro y una "
    "tabla en Markdown de CINCO agents de Tlamatini con una descripción de una línea cada uno (elige cinco que "
    "de verdad tengas, p. ej. Globber, Grepper, Editor, Shoter, PDFer). Deja "
    "<code>output_dir</code> VACÍO para que PDFer guarde en su propia carpeta Documents/TlamatiniPDF — "
    "NO inventes un path de prueba.<br><br>Luego "

    "reporta, en una tabla HTML pequeña: <code>status</code> &lt;status&gt;, el "
    "<code>output_path</code> COMPLETO &lt;output_path&gt;, <code>page_count</code> &lt;page_count&gt;, "
    "<code>bytes</code> &lt;bytes&gt; y <code>engine</code> &lt;engine&gt;. Si "
    "<code>status</code> no es <code>created</code>, dilo claramente y cita la razón — "
    "nunca afirmes que un PDF existe cuando no existe. Termina con END-RESPONSE."
)

# ── rank 30 · id 111 — the headline use case: your OWN answer becomes a report ─
ANSWER_TO_PDF = (
    "Tlamatini, ejecuta la demo <b>RESPUESTA → PDF</b>, por favor — responde una pregunta y luego convierte "
    "<b>tu propia respuesta</b> en un reporte PDF real. Marca SÓLO la casilla <b>Multi-Turn</b>; "
    "usa SÓLO <code>chat_agent_pdfer</code>.<br><br>LLENA "

    "ESTO — reemplaza el texto dentro de los corchetes [[ ]] (OPCIONAL; si lo dejo "
    "sin tocar, USA EL PREDETERMINADO y NO me preguntes primero):<br>• "
    "TOPIC: [[ de qué debe tratar el reporte — OPCIONAL, predeterminado: cómo Tlamatini hace que su "
    "modo Multi-Turn, el Exec Report y Ask Execs trabajen juntos ]]<br><br>PASO "

    "1 — ESCRÍBELO. Primero compón una respuesta genuina y bien estructurada sobre &lt;TOPIC&gt; "
    "en Markdown: un título <code># </code>, tres secciones <code>## </code>, al menos una "
    "lista de viñetas y al menos una tabla en Markdown. Muéstramela en el chat.<br><br>PASO "

    "2 — IMPRÍMELO. Luego llama a <code>chat_agent_pdfer</code> EXACTAMENTE UNA VEZ, pasando ese "
    "MISMO texto VERBATIM como <code>input_text</code> — no lo resumas, no lo reescribas, "
    "no quites la tabla. Usa <code>mode='auto'</code> (PDFer olfatea Markdown vs HTML "
    "por sí mismo), <code>title</code> puesto en el título de tu reporte, "
    "<code>subtitle='Generated by Tlamatini'</code>, <code>toc=true</code>, "
    "<code>page_numbers=true</code> y <code>filename='tlamatini_report.pdf'</code>. Deja "
    "<code>output_dir</code> VACÍO para que caiga en Documents/TlamatiniPDF.<br><br>PASO "

    "3 — REPORTA. Dime a qué mode resolvió <code>auto</code> &lt;mode&gt;, el "
    "<code>status</code> &lt;status&gt;, el <code>output_path</code> COMPLETO &lt;output_path&gt; y "
    "el <code>page_count</code> &lt;page_count&gt;. Termina con una línea diciéndome que la "
    "tabla que escribí es una tabla REAL en el PDF, no una imagen. Termina con END-RESPONSE."
)

# ── rank 40 · id 112 — images -> a PDF album (needs image files) ─────────────
IMAGES = (
    "Tlamatini, ejecuta la demo <b>ÁLBUM DE IMÁGENES CON PDFer</b>, por favor — convierte una carpeta de "
    "imágenes en un PDF. Marca SÓLO la casilla <b>Multi-Turn</b>.<br><br>LLENA "

    "ESTOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS OPCIONALES; si "
    "dejo un corchete sin tocar, USA EL PREDETERMINADO y NO me preguntes "
    "primero):<br>• PICTURES FOLDER: [[ una carpeta que contenga unos cuantos archivos .png/.jpg — OPCIONAL, predeterminado: "
    "tu carpeta Pictures "
    "]]<br>• HOW MANY: [[ cuántas imágenes incluir — OPCIONAL, predeterminado: 4 "
    "]]<br>• LAYOUT: [[ one-per-page, fit o grid — OPCIONAL, predeterminado: grid "

    "]]<br><br>PASO 1 — ENCUENTRA LAS IMÁGENES. Usa <code>chat_agent_globber</code> UNA VEZ "
    "con <code>pattern='*.png'</code> (y otra vez con <code>*.jpg</code> si no encuentras ninguna) "
    "y <code>path</code> puesto en &lt;PICTURES FOLDER&gt;, del más nuevo primero. Toma los primeros &lt;HOW "
    "MANY&gt; resultados. Si NO encuentras ninguna imagen, DETENTE y dímelo claramente — NO inventes "
    "paths de archivo y NO llames a PDFer con una lista vacía.<br><br>PASO "

    "2 — CONSTRUYE EL ÁLBUM. Llama a <code>chat_agent_pdfer</code> EXACTAMENTE UNA VEZ "
    "con <code>mode='images'</code>, <code>images</code> puesto en esos paths como una lista separada por comas, "
    "<code>image_layout='&lt;LAYOUT&gt;'</code>, <code>grid_columns=2</code>, "
    "<code>image_caption=true</code>, <code>title='My Album'</code> "
    "y <code>filename='pdfer_album.pdf'</code>. Deja <code>output_dir</code> VACÍO.<br><br>PASO "

    "3 — REPORTA. Dame una tabla HTML pequeña con <code>status</code> &lt;status&gt;, el "
    "<code>output_path</code> COMPLETO &lt;output_path&gt;, <code>images_used</code> "
    "&lt;images_used&gt;, <code>page_count</code> &lt;page_count&gt; y <code>engine</code> "
    "&lt;engine&gt; (debería decir pymupdf). Si algún path de imagen se omitió por faltante, di "
    "cuál. Termina con END-RESPONSE."
)

# ── rank 50 · id 113 — the full report: capture + prose + cover + polish ─────
MIXED = (
    "Tlamatini, ejecuta la demo <b>REPORTE COMPLETO CON PDFer</b>, por favor — captura la pantalla, escribe "
    "el comentario y une ambos en UN PDF ilustrado con portada. Esta es la tarjeta "
    "más avanzada de esta sección. Marca SÓLO la casilla <b>Multi-Turn</b>.<br><br>LLENA "

    "ESTOS — reemplaza el texto dentro de los corchetes [[ ]] (TODOS OPCIONALES; si dejo "
    "un corchete sin tocar, USA EL PREDETERMINADO y NO me preguntes primero):<br>• "
    "TÍTULO DEL REPORTE: [[ OPCIONAL, predeterminado: Reporte del estado "
    "del escritorio ]]<br>• PULE EL TEXTO CON OLLAMA PRIMERO: [[ yes o no — OPCIONAL, "
    "predeterminado: no ]]<br>• PAGE ORIENTATION: [[ portrait o landscape — OPCIONAL, predeterminado: "

    "landscape ]]<br><br>PASO 1 — CAPTURA. Llama a <code>chat_agent_shoter</code> UNA VEZ para tomar un "
    "solo screenshot de mi escritorio. Lee su <code>output_path</code> — ese path exacto es la "
    "imagen que vas a incrustar. Si Shoter falla, DETENTE y dilo; NO fabriques un path de "

    "imagen.<br><br>PASO 2 — DESCRIBE. Escribe un comentario corto en Markdown tú misma: un encabezado <code>## "
    "</code>, dos o tres oraciones diciendo qué es este reporte y cuándo se "
    "hizo, y una tabla pequeña en Markdown con dos filas (Captured at / Captured "

    "by).<br><br>PASO 3 — ÚNELO. Llama a <code>chat_agent_pdfer</code> EXACTAMENTE UNA "
    "VEZ con <code>mode='mixed'</code>, <code>input_text</code> = tu comentario del "
    "PASO 2, <code>images</code> = el <code>output_path</code> de Shoter del "
    "PASO 1, <code>title='&lt;TÍTULO DEL "
    "REPORTE&gt;'</code>, <code>subtitle='Captured and bound by "
    "Tlamatini'</code>, <code>orientation='&lt;PAGE ORIENTATION&gt;'</code>, <code>image_caption=true</code>, "
    "<code>page_numbers=true</code>, <code>filename='pdfer_full_report.pdf'</code>, "
    "y <code>ollama_polish</code> puesto en true SÓLO si respondí yes a la pregunta "
    "de TIDY (si no, false — false es más rápido y renderiza mis palabras verbatim). "
    "Deja <code>output_dir</code> "

    "VACÍO.<br><br>PASO 4 — REPORTA. Dame una tabla HTML con <code>status</code> &lt;status&gt;, "
    "<code>mode</code> &lt;mode&gt;, el <code>output_path</code> COMPLETO &lt;output_path&gt;, "
    "<code>page_count</code> &lt;page_count&gt;, <code>images_used</code> &lt;images_used&gt; "
    "y <code>bytes</code> &lt;bytes&gt;. Luego agrega UNA línea de cierre explicando que esta misma "
    "cadena funciona sin supervisión en el canvas como "
    "<code>Starter → Shoter → Parametrizer → PDFer → Ender</code>, porque PDFer emite un "
    "bloque <code>INI_SECTION_PDFER</code> que un Parametrizer puede leer. Termina con END-RESPONSE."
)


# (idPrompt, sort_rank, promptContent) — ids APPENDED after 108 (0187), never renumbered.
_NEW_PROMPTS = (
    (109, 10, WIZARD),          # RESERVED rank-10 slot: the section's Step-by-Step opener
    (110, 20, SIMPLE),
    (111, 30, ANSWER_TO_PDF),
    (112, 40, IMAGES),
    (113, 50, MIXED),
)


def add_pdfer_demo_prompts(apps, schema_editor):
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


def remove_pdfer_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _rank, _c in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0189_add_chat_agent_pdfer_tool'),
    ]

    operations = [
        migrations.RunPython(add_pdfer_demo_prompts, remove_pdfer_demo_prompts),
    ]
