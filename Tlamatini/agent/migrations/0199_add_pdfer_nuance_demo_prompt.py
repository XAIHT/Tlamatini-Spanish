# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Catálogo de Prompts — el demo de NUANCE de PDFer (Angela, 2026-09-06).

La revisión de PDFer de 2026-09 le dio dos parámetros nuevos — ``nuance`` y
``predominant_color`` — y la capacidad de LEER un documento y decidir cómo debe
VERSE antes de renderizarlo. Nada de eso se descubre desde las cinco tarjetas
de PDFer que ya existían, escritas cuando todos los PDF salían en el mismo
esquema café y con la misma tipografía. Ésta es la tarjeta que lo enseña.

Renderiza A PROPÓSITO el MISMO contenido DOS VECES, con el tratamiento como
única variable, porque ésa es la demostración: el punto no es "PDFer puede
hacer un PDF oscuro", es "PDFer decide, y tú le puedes ganar".

NEPANTLA — qué se tradujo y qué no. El texto del prompt es Canal A (lo lee la
usuaria), así que va en español. NO se tocó nada del canal de máquina: el
nombre de la tool ``chat_agent_pdfer``, las llaves (``mode``, ``input_text``,
``title``, ``filename``, ``nuance``, ``predominant_color``), los valores de
catálogo (``markdown``, ``academic_paper``), los nombres de campo del reporte
(``nuance_confidence``, ``layout_clean``, ``overlaps``, ``font_pairing``…),
``Multi-Turn`` / ``Exec report`` y el centinela ``END-RESPONSE``. Traducir
cualquiera de ésos rompería la ejecución o el badge de modos.

Cumplimiento del contrato (todo, a propósito):
  * id APPEND-ONLY. La 0198 dejó el catálogo en 119, así que ésta es **120** —
    se agrega al final, jamás se renumera.
  * ``category='documents'`` — la sección donde ya viven las otras cinco
    tarjetas de PDFer y las cuatro de LaTeXer.
  * ``sort_rank = 55`` — y NO el siguiente hueco libre en 100, que es lo que
    habría elegido un "agrégalo al final" ingenuo. La sección tiene a PDFer en
    10-50 y a LaTeXer en 60-90, y la regla de Angela es que **toda tarjeta de
    PDFer va antes de toda tarjeta de LaTeXer**: PDFer no necesita nada
    instalado, LaTeXer necesita MiKTeX, y una sección se lee de cero-setup
    hacia prerequisito. Ésta es tarjeta de PDFer, así que va con su familia —
    los ranks se siembran de diez en diez justo para dejar espacio así. El 55
    la pone al final de las de PDFer (es la más compleja: dos renders y una
    comparación) manteniendo las familias contiguas. El rank 10 sigue
    RESERVADO para el abridor Step-by-Step de la sección.
  * Gramática de parámetros v1.44.0: ``[[ … — OPCIONAL, por omisión: X ]]``
    juntos ARRIBA con la frase-guardia debajo, para que el demo de un clic
    corra igual; ``< >`` marca huecos de REPORTE, nunca entradas. Sin rutas de
    scratch hardcodeadas (Reglas 15/16) — PDFer escribe en su propia carpeta
    de Documentos.
  * SEGURO y repetible: escribe dos PDF nuevos con nombres explícitos que no
    chocan, en la carpeta de salida de PDFer; no muta nada más, no necesita
    red, ni llave, ni instalación.
  * MODOS DEL CLASIFICADOR: la línea final de PRE-VUELO nombra sólo las
    casillas **Multi-Turn** y **Exec report**, para que ``classifyPromptModes``
    (``tools_dialog.js``) marque la tarjeta como Multi-turn + Exec-report y al
    hacer clic se palomeen exactamente ésas dos. No aparece ninguna tool
    ``acp_*`` ni la frase "step-by-step", que marcarían ACPX / Step-by-Step por
    error.

El reverso borra exactamente esta fila.
"""
from django.db import migrations

NUANCE_DEMO = (
    "<div style=\"background:linear-gradient(135deg,#07090F 0%,#1E3A8A 40%,"
    "#38BDF8 70%,#22D3EE 100%);color:#ffffff;padding:10px 14px;"
    "border-radius:8px;font-weight:600;\">📕 PDFer — las mismas palabras, dos "
    "documentos distintos</div>\n\n"
    "LLENA (opcional — déjalos tal cual para un demo de un solo clic):\n"
    "  · Un color para el segundo documento: "
    "[[ predominant_color — OPCIONAL, por omisión: #B4451F ]]\n"
    "  · Un tratamiento para forzarle al segundo documento: "
    "[[ nuance — OPCIONAL, por omisión: academic_paper ]]\n"
    "Si dejaste los espacios de arriba sin tocar, usa los valores por omisión y "
    "corre de todos modos — no me pidas que los llene.\n\n"
    "Tlamatini, quiero ver a PDFer ELEGIR un diseño, y luego verme ganarle. "
    "Renderiza el MISMO contenido dos veces con chat_agent_pdfer, cambiando "
    "nada más el tratamiento.\n\n"
    "Usa este contenido para AMBOS documentos, tal como está escrito:\n\n"
    "---\n"
    "# Física de confinamiento del tokamak esférico\n\n"
    "Un tokamak confina un plasma de deuterio-tritio con un campo magnético "
    "toroidal de unos 5 T combinado con un campo poloidal inducido por una "
    "corriente de plasma de 15 MA. Los imanes superconductores operan a 4 K, "
    "enfriados con helio supercrítico.\n\n"
    "## Parámetros medidos\n\n"
    "| Parámetro | Símbolo | Valor | Unidad | Notas |\n"
    "|---|---|---|---|---|\n"
    "| Campo toroidal | B_t | 5.3 | T | en el eje magnético |\n"
    "| Corriente de plasma | I_p | 15.0 | MA | flat-top |\n"
    "| Tiempo de confinamiento | tau_E | 3.7 | s | H-mode, ELMy |\n"
    "| Energía magnética almacenada | W_mag | 40 | GJ | relevante al quench |\n\n"
    "## Diagnósticos\n\n"
    "El detector de quench se configura desde "
    "`C:/Users/angel/AppData/Local/Programs/Tlamatini/config/"
    "quench_detector.yaml` y se valida contra "
    "https://raw.githubusercontent.com/XAIHT/Tlamatini/main/docs/plasma/"
    "quench.json\n\n"
    "**Advertencia:** un quench deposita 40 GJ en milisegundos.\n"
    "---\n\n"
    "**DOCUMENTO 1 — deja que PDFer decida.** Llama a chat_agent_pdfer con "
    "mode='markdown', ese contenido como input_text, "
    "title='Física de confinamiento del tokamak esférico', "
    "filename='tokamak_auto.pdf', y NADA sobre la apariencia. No pases nuance "
    "y no pases predominant_color: quiero ver qué escoge por su cuenta.\n\n"
    "**DOCUMENTO 2 — gánale.** Llama a chat_agent_pdfer otra vez con el MISMO "
    "contenido y título, filename='tokamak_forzado.pdf', más el nuance y el "
    "predominant_color del bloque de arriba.\n\n"
    "Luego dime, en lenguaje llano y en una tablita HTML:\n"
    "  · qué tratamiento eligió PDFer solo, y qué tan seguro estaba → "
    "<nuance / nuance_confidence / nuance_source>\n"
    "  · cómo quedaron las dos paletas → <palette y predominant_color de cada "
    "uno>\n"
    "  · con qué tipografías quedó cada documento → <font_pairing de cada uno>\n"
    "  · si decidió que aquí la decoración era segura → <decorations>\n"
    "  · **si el layout quedó verificado limpio** — PDFer vuelve a abrir cada "
    "PDF terminado y mide las letras REALES de la página buscando texto "
    "encimado y cualquier cosa que se salga de la hoja → <layout_clean y "
    "overlaps de cada uno>\n"
    "  · los dos archivos que escribió → <output_path de cada uno>\n\n"
    "Fíjate en esa tabla del contenido: trae una ruta de Windows y una URL "
    "larga, que es justo la forma que antes se imprimía encima de la siguiente "
    "columna. Confírmame desde el audit si lo hizo.\n\n"
    "PRE-VUELO: palomea SÓLO las casillas Multi-Turn y Exec report. Usa ÚNICAMENTE "
    "chat_agent_pdfer — sin shell, sin Python, sin ningún otro agent. Nada de "
    "esto necesita internet, ni llave, ni instalación. Termina con END-RESPONSE."
)

# (idPrompt, sort_rank, promptContent) — el id se AGREGA después del 119 (0198)
# y jamás se renumera; el RANK es 55, que mete esta tarjeta con las otras de
# PDFer (10-50) y ANTES de las de LaTeXer (60-90) en vez de al final de la
# sección. Ver el docstring del módulo: los ids se agregan, los ranks se colocan.
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
        ('agent', '0198_add_netspeed_calculator_demo_prompt'),
    ]

    operations = [
        migrations.RunPython(add_demo_prompts, remove_demo_prompts),
    ]
