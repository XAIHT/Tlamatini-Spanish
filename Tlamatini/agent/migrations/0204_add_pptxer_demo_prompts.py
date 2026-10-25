# ══════════════════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ══════════════════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Catalog of Prompts — the two PPTXer cards (Angela, 2026-09-14).

PPTXer is Multi-Turn-capable, so it is INCOMPLETE without at least one catalog
prompt (``create_new_agent.md`` Step 7.8, a hard completion gate). Two are
seeded because PPTXer has two genuinely different audiences and one card cannot
show both: a plain business deck, and the loud gaming/marketing deck it was
actually built for.

Contract compliance, deliberately all of it:

  * APPEND-ONLY ids. 0201 left the catalog at 122, so these are **123** and
    **124** — appended, never renumbered.

  * ``category='documents'`` — the section PDFer's six cards and LaTeXer's four
    already live in. PPTXer is the third member of the document-authoring
    family and belongs beside them, not in a section of its own.

  * ``sort_rank`` 56 and 58, and NOT the next free slot at 100. The section is
    ordered least-complex → most-complex and zero-setup → prerequisite-bearing:
    PDFer occupies 10-55 and needs nothing installed; LaTeXer occupies 60-90 and
    REQUIRES MiKTeX. PPTXer needs nothing installed either (python-pptx already
    ships), so it sits with the zero-setup half — after PDFer, before LaTeXer.
    That also keeps ``test_latexer_prompts_sit_after_pdfer_in_the_documents_section``
    satisfied and each tool family contiguous. Ranks are seeded in tens
    precisely to leave insertion room like this; rank 10 stays RESERVED for the
    section's existing Step-by-Step opener (prompt 109), and ranks are unique
    within a section.

  * Parameter grammar v1.44.0: ``[[ ... — OPTIONAL, default: X ]]`` collected at
    the TOP with the unfilled-guard sentence beneath, so a one-click demo still
    runs on the stated defaults; ``< >`` marks REPORT slots only, never inputs.
    No hardcoded scratch path (Rules 15/16) — PPTXer writes to its own
    Documents folder.

  * SAFE and repeatable: each card writes ONE new .pptx with an explicit
    non-colliding name into PPTXer's own output folder, mutates nothing else,
    and needs no network, no key and no installation. The daily chat test may
    run them.

  * CLASSIFIER MODES: each card's closing PRE-FLIGHT line names the
    **Multi-Turn** and **Exec report** checkboxes only, so
    ``tools_dialog.js::classifyPromptModes`` badges them Multi-turn +
    Exec-report and clicking one ticks exactly those two. Neither card contains
    an ``acp_*`` token or the hyphenated "step-by-step" token, either of which
    would wrongly tick ACPX / Step-by-Step.

Reverse deletes exactly these two rows.
"""
from django.db import migrations


PPTXER_SIMPLE = (
    "<div style=\"background:linear-gradient(135deg,#0B1F3A 0%,#5A1FB8 "
    "38%,#EC4899 70%,#22D3EE 100%);color:#ffffff;padding:10px "
    "14px;border-radius:8px;font-weight:600;\">🖼️ PPTXer — convierte una respuesta en una "
    "presentación real</div>\n\n"
    "LLENA LOS CAMPOS (opcional — déjalos exactamente como están para una demo de un solo clic):\n"
    "  [[ SUBJECT — OPCIONAL, predeterminado: \"How Tlamatini builds a presentation\" ]]\n"
    "  [[ BRAND COLOUR — OPCIONAL, predeterminado: #5A1FB8 ]]\n"
    "Si dejaste esos sin llenar, usa los valores predeterminados exactamente como están escritos arriba y "
    "no me los pidas.\n\n"
    "Tlamatini, por favor haz esto en orden:\n\n"
    "1. Escríbeme un briefing corto y bien estructurado sobre el SUBJECT — un título, "
    "tres o cuatro secciones, unas cuantas viñetas cada una y una tabla pequeña. Que quede "
    "en menos de 400 palabras.\n\n"
    "2. Luego llama a chat_agent_pptxer UNA VEZ, pasando ese briefing VERBATIM como "
    "input_text, con predominant_color puesto en el BRAND COLOUR y "
    "filename='tlamatini_briefing.pptx'. NO pongas nuance — quiero ver "
    "qué tratamiento elige PPTXer por su cuenta.\n\n"
    "3. Cuando termine, repórtame claramente:\n"
    "   · el path completo del .pptx que escribió            → <path>\n"
    "   · cuántas slides hizo                                → <slide_count>\n"
    "   · qué tratamiento eligió, y por qué                  → <nuance>\n"
    "   · qué fuente de display usó                          → <font_display>\n"
    "   · si el layout se verificó LIMPIO                    → <layout_clean>\n"
    "   · y si ese veredicto vino del propio render de PowerPoint "
    "→ <ground_truth>\n\n"
    "Ese último punto es el que me importa: PPTXer vuelve a abrir el deck que acaba de "
    "escribir y lo MIRA. Si layout_clean es true Y ground_truth es true, "
    "dímelo en palabras claras — significa que las slides se midieron sobre los mismos "
    "pixeles que vería una audiencia, no sólo que se escribieron. Si en cambio reporta hallazgos, "
    "léemelos; no llames limpio al deck.\n\n"
    "PRE-FLIGHT: marca Multi-Turn y Exec report. No se necesita nada más — sin "
    "red, sin API key, sin instalación. Termina con END-RESPONSE."
)


PPTXER_GAMING = (
    "<div style=\"background:linear-gradient(135deg,#04060C 0%,#7B2FF7 34%,"
    "#F72585 66%,#00F0FF 100%);color:#ffffff;padding:10px 14px;"
    "border-radius:8px;font-weight:600;\">🎮 PPTXer — el mismo deck, dos "
    "mundos distintos</div>\n\n"
    "LLENA LOS CAMPOS (opcional — déjalos exactamente como están para una demo de un solo clic):\n"
    "  [[ GAME OR PRODUCT NAME — OPCIONAL, predeterminado: \"Nexus Protocol\" ]]\n"
    "Si dejaste eso sin llenar, usa el valor predeterminado exactamente como está escrito arriba y "
    "no me lo pidas.\n\n"
    "Tlamatini, esta muestra para qué sirve de verdad PPTXer. Por favor:\n\n"
    "1. Inventa un deck corto de lanzamiento de temporada para el GAME OR PRODUCT NAME — un "
    "título, una sección 'What Changed' con cuatro viñetas, una sección 'By The Numbers' "
    "escrita como cuatro líneas en la forma NÚMERO y luego ETIQUETA (por ejemplo "
    "'3.4M Registered players', '12ms Median server latency'), una tabla pequeña de precios "
    "y una cita corta de un jugador. Mantenlo compacto; una slide no es una "
    "page.\n\n"
    "2. Llama a chat_agent_pptxer con ese contenido como input_text, "
    "nuance='esports_tournament', predominant_color='#12E2A3', "
    "filename='launch_esports.pptx'.\n\n"
    "3. Llama a chat_agent_pptxer una SEGUNDA vez con el MISMO input_text, pero "
    "nuance='cyberpunk_tech', predominant_color='#00F0FF', "
    "filename='launch_cyberpunk.pptx'.\n\n"
    "4. Luego compáralos para mí. Las mismas palabras, dos decks distintos — dime "
    "qué tipografía de display eligió cada uno, cómo salieron las dos paletas, "
    "qué ornamento usó cada uno y si AMBOS se verificaron limpios:\n"
    "   · esports    → <font_display>, <palette>, <layout_clean>\n"
    "   · cyberpunk  → <font_display>, <palette>, <layout_clean>\n\n"
    "Fíjate en lo que PPTXer hizo con las líneas de 'By The Numbers': cuatro viñetas paralelas "
    "NÚMERO-luego-ETIQUETA se promueven automáticamente a grandes stat tiles, "
    "porque eso es lo que son. Dime si eso pasó.\n\n"
    "PRE-FLIGHT: marca Multi-Turn y Exec report. Ambos decks se escriben en "
    "la propia carpeta Documents de PPTXer con nombres que no van a chocar con "
    "nada, así que es seguro ejecutarla las veces que quieras. Termina con "
    "END-RESPONSE."
)


_NEW_PROMPTS = (
    (123, 56, PPTXER_SIMPLE),
    (124, 58, PPTXER_GAMING),
)


def add_pptxer_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, rank, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={
                'promptName': 'prompt-%d' % prompt_id,
                'promptContent': content,
                'category': 'documents',
                'sort_rank': rank,
            },
        )


def remove_pptxer_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(
        idPrompt__in=[prompt_id for prompt_id, _rank, _content in _NEW_PROMPTS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0203_add_chat_agent_pptxer_tool'),
    ]

    operations = [
        migrations.RunPython(add_pptxer_demo_prompts, remove_pptxer_demo_prompts),
    ]
