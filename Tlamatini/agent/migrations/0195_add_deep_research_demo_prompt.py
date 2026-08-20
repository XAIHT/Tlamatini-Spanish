# ══════════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ══════════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Catalogo de Prompts — el demo de DEEP INTERNET RESEARCH (Angela, 2026-08-17).

Puerto del 0194 de Tlamatini (ingles). Dos cosas cambian en esta edicion y
NINGUNA es cosmetica:

  * EL NUMERO DE MIGRACION. El arbol espanol lleva una migracion extra
    (``0191_translate_prompt_catalog_to_spanish``), asi que aqui la cadena va
    un paso adelante: la que alla es 0194 aqui es **0195**, y depende de
    ``0194_add_latexer_demo_prompts``, no de la 0193. Copiar el numero del
    ingles romperia el grafo de migraciones.
  * EL TEXTO. El catalogo de esta edicion esta en castellano (0191), asi que
    la tarjeta se lee en castellano — pero el VOCABULARIO DE MAQUINA se queda
    en ingles tal cual: ``Multi-Turn``, ``Exec report``, ``sequential-thinking
    mcp`` y ``memory mcp`` NO se traducen. Son lo que la maquina lee.

Lo que NO cambia (mismo contrato que el ingles, verificado contra esta base):
  * ``idPrompt=118`` — APPEND: el catalogo espanol tambien termina en 117, asi
    que el 118 lo deja contiguo 1..N. Jamas se renumera.
  * ``sort_rank=100`` — la seccion ``getting_started`` llega hasta el rank 90
    (id 4), y el rank 10 sigue RESERVADO para el abridor Step-by-Step.
  * Gramatica de parametros v1.44.0: ``[[ ... ]]`` es el UNICO hueco que llena
    la usuaria. Sin rutas de scratch a mano (politica Temp/Templates, reglas
    15/16).
  * SEGURO: buscar y pensar son de solo lectura.

Contrato del clasificador (``tools_dialog.js::classifyPromptModes``): nombrar
la casilla **Multi-Turn** hace que la tarjeta se marque Multi-turn + Exec-report
y que al hacerle click se palomeen esas dos casillas. Por eso aqui NO puede
aparecer ninguna herramienta ``acp_*`` ni la frase "step-by-step": marcarian
tambien ACPX o Step-by-Step. Ojo tambien con el limpiador de clausulas
prohibitivas del clasificador (``no|nunca|jamas`` + ``uses|utilices|emplees``):
el texto dice "no menos", que no cae en esa regla.

La reversa borra exactamente esta fila.
"""
from django.db import migrations

DEEP_RESEARCH = (
    "Tlamatini, busca a fondo por todo el Internet acerca de lo siguiente: "
    "**[[ Pon aquí tu tema ... ]]**, dame cientos de links completos, "
    "quédate buscando **por lo menos 30 min, no menos**, y piensa "
    "secuencialmente (sequential-thinking mcp) y muy inteligentemente "
    "siguiendo todas nuestras golden rules de memory (memory mcp); además "
    "siéntete libre de usar todos los Mcps y Agents que tienes disponibles "
    "para cumplir por completo esta tarea, ¡go!\n\n"
    # Contrato del clasificador: nombrar la casilla **Multi-Turn** marca la
    # tarjeta Multi-turn + Exec-report, y al hacerle click se palomean AMBAS
    # casillas de la barra. Ninguna herramienta acp_* ni "step-by-step" aqui.
    "PRE-FLIGHT: esta corrida necesita el modo **Multi-Turn** con el "
    "**Exec report** — al hacer click en esta tarjeta se te palomean las dos "
    "casillas de la barra."
)


def add_deep_research_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.update_or_create(
        idPrompt=118,
        defaults={
            'promptName': 'prompt-118',
            'promptContent': DEEP_RESEARCH,
            'category': 'getting_started',
            'hidden': False,
            'sort_rank': 100,
        },
    )


def remove_deep_research_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt=118).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0194_add_latexer_demo_prompts'),
    ]

    operations = [
        migrations.RunPython(add_deep_research_prompt,
                             remove_deep_research_prompt),
    ]
