# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Catalog of Prompts — the PDFer NUANCE demo (Angela, 2026-09-06).

PDFer's 2026-09 overhaul gave it two new parameters — ``nuance`` and
``predominant_color`` — and the ability to read a document and decide how it
should LOOK before rendering it. None of that is discoverable from the five
existing PDFer cards, which were written when every PDF came out in the same
brown scheme and the same font. This card is the one that shows it.

It deliberately renders the SAME content TWICE, with the treatment as the only
variable, because that is the demonstration: the point is not "PDFer can make a
dark PDF", it is "PDFer decides, and you can overrule it".

Contract compliance (all of it, deliberately):
  * APPEND-ONLY id. 0197 left the catalog at 119, so this is **120** — appended,
    never renumbered (``test_ids_are_contiguous_1_to_n_no_gaps``).
  * ``category='documents'`` — the section PDFer's other five cards and
    LaTeXer's four already live in.
  * ``sort_rank = 55`` — and NOT the next free slot at 100, which is what a
    naive "append at the end" would have chosen. The section holds PDFer at
    10-50 and LaTeXer at 60-90, and
    ``test_latexer_prompts_sit_after_pdfer_in_the_documents_section`` enforces
    Angela's rule that **every PDFer card must precede every LaTeXer card**:
    PDFer needs nothing installed, LaTeXer needs MiKTeX, and a section reads
    zero-setup before prerequisite-bearing. This is a PDFer card, so it belongs
    with the PDFer family — the ranks are seeded in steps of ten precisely to
    leave insertion room like this. 55 places it last among the PDFer cards
    (it is the most complex of them: two renders and a comparison) while
    keeping the tool families contiguous. Rank 10 stays RESERVED for the
    section's Step-by-Step opener; ranks are unique within a section
    (``test_ranks_are_unique_within_a_section``).
  * Parameter grammar v1.44.0: ``[[ ... — OPTIONAL, default: X ]]`` collected at
    the TOP with the unfilled-guard sentence beneath, so a one-click demo still
    runs; ``< >`` marks REPORT slots only, never inputs. No hardcoded scratch
    path (Rules 15/16) — PDFer writes to its own Documents folder.
  * SAFE and repeatable: it writes two new PDFs with explicit non-colliding
    names into PDFer's own output folder, mutates nothing else, needs no
    network, no key and no installation.
  * CLASSIFIER MODES: the closing PRE-FLIGHT line names the **Multi-Turn** and
    **Exec report** checkboxes only, so ``classifyPromptModes``
    (``tools_dialog.js``) badges the card Multi-turn + Exec-report and clicking
    it ticks exactly those two. No ``acp_*`` tool and no "step-by-step" wording
    appears, either of which would wrongly tick ACPX / Step-by-Step.

Reverse deletes exactly this one row.
"""
from django.db import migrations

NUANCE_DEMO = (
    "<div style=\"background:linear-gradient(135deg,#07090F 0%,#1E3A8A 40%,"
    "#38BDF8 70%,#22D3EE 100%);color:#ffffff;padding:10px 14px;"
    "border-radius:8px;font-weight:600;\">📕 PDFer — las mismas palabras, dos "
    "documentos distintos</div>\n\n"
    "LLENA LOS CAMPOS (opcional — déjalos exactamente como están para una demo de un "
    "demo):\n"
    "  · Un color para el segundo documento: "
    "[[ predominant_color — OPCIONAL, predeterminado: #B4451F ]]\n"
    "  · Un tratamiento para forzar en el segundo documento: "
    "[[ nuance — OPCIONAL, predeterminado: academic_paper ]]\n"
    "Si dejaste los espacios de arriba sin tocar, usa los valores predeterminados indicados y ejecútala "
    "de todos modos — no me pidas que los llene.\n\n"
    "Tlamatini, quiero ver a PDFer ELEGIR un diseño y luego verme a mí anularlo. "
    "Renderiza el MISMO contenido dos veces con chat_agent_pdfer, cambiando "
    "nada más que el tratamiento.\n\n"
    "Usa este contenido para AMBOS documentos, exactamente como está escrito:\n\n"
    "---\n"
    "# Confinement Physics of the Spherical Tokamak\n\n"
    "A tokamak confines a deuterium-tritium plasma using a toroidal magnetic "
    "field of roughly 5 T combined with a poloidal field induced by a 15 MA "
    "plasma current. The superconducting magnets operate at 4 K, cooled by "
    "supercritical helium.\n\n"
    "## Measured parameters\n\n"
    "| Parameter | Symbol | Value | Unit | Notes |\n"
    "|---|---|---|---|---|\n"
    "| Toroidal field | B_t | 5.3 | T | at the magnetic axis |\n"
    "| Plasma current | I_p | 15.0 | MA | flat-top |\n"
    "| Confinement time | tau_E | 3.7 | s | H-mode, ELMy |\n"
    "| Stored magnetic energy | W_mag | 40 | GJ | quench-relevant |\n\n"
    "## Diagnostics\n\n"
    "The quench detector is configured through "
    "`C:/Users/angel/AppData/Local/Programs/Tlamatini/config/"
    "quench_detector.yaml` and validated against "
    "https://raw.githubusercontent.com/XAIHT/Tlamatini/main/docs/plasma/"
    "quench.json\n\n"
    "**Warning:** a quench deposits 40 GJ in milliseconds.\n"
    "---\n\n"
    "**DOCUMENTO 1 — deja que PDFer decida.** Llama a chat_agent_pdfer con "
    "mode='markdown', ese contenido como input_text, "
    "title='Confinement Physics of the Spherical Tokamak', "
    "filename='tokamak_auto.pdf', y NADA sobre la apariencia. No "
    "pases nuance y no pases predominant_color: quiero ver qué "
    "elige por su cuenta.\n\n"
    "**DOCUMENTO 2 — anúlalo.** Llama a chat_agent_pdfer otra vez con el MISMO "
    "contenido y título, filename='tokamak_forced.pdf', más el nuance y el "
    "predominant_color del bloque de llenado de arriba.\n\n"
    "Luego dime, en lenguaje sencillo y en una tabla HTML pequeña:\n"
    "  · qué tratamiento eligió PDFer por sí mismo, y qué tan seguro estaba → "
    "<nuance / nuance_confidence / nuance_source>\n"
    "  · cómo salieron las dos paletas → <palette and predominant_color "
    "para cada uno>\n"
    "  · con qué tipografías se compuso cada documento → <font_pairing for each>\n"
    "  · si decidió que la decoración era segura aquí → <decorations>\n"
    "  · **si el layout se verificó limpio** — PDFer vuelve a abrir cada "
    "PDF terminado y mide las letras reales en la página buscando texto que se encime "
    "y cualquier cosa que se salga de la hoja → <layout_clean and overlaps for "
    "each>\n"
    "  · los dos archivos que escribió → <output_path for each>\n\n"
    "Pon atención a esa tabla del contenido: tiene un path de Windows y "
    "una URL larga, que es exactamente la forma que antes se imprimía encimada en la "
    "siguiente columna. Confirma desde el audit si lo hizo.\n\n"
    "PRE-FLIGHT: marca SÓLO las casillas Multi-Turn y Exec report. Usa "
    "SÓLO chat_agent_pdfer — sin shell, sin Python, sin ningún otro agent. Nada aquí "
    "necesita internet, una key ni una instalación. Termina con END-RESPONSE."
)

# (idPrompt, sort_rank, promptContent) — the id is APPENDED after 119 (0197) and
# never renumbered; the RANK is 55, which slots this card in with the other
# PDFer cards (10-50) and BEFORE LaTeXer's (60-90) rather than at the end of the
# section. See the module docstring: ids append, ranks are placed.
_NEW_PROMPTS = (
    (120, 55, NUANCE_DEMO),
)


def add_demo_prompts(apps, schema_editor):
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


def remove_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(
        idPrompt__in=[prompt_id for prompt_id, _rank, _c in _NEW_PROMPTS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0197_add_netspeed_calculator_demo_prompt'),
    ]

    operations = [
        migrations.RunPython(add_demo_prompts, remove_demo_prompts),
    ]
