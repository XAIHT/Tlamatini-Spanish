# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Seed the ``Chat-Agent-NetSpeed-Calculator`` Tool row.

This is the OTHER half of the dual enable-gate: ``get_mcp_tools()`` binds
``chat_agent_netspeed_calculator`` for the LLM only when BOTH this Tool row
(Configure Mcps/Tools) AND the ``NetSpeed-Calculator`` Agent row (Configure
Agents) are enabled. Both gates fail OPEN, so a missing row defaults to
enabled — this migration exists so the user actually gets a CHECKBOX to turn
the agent off, not so it works at all.

The description must stay byte-identical to
``ChatWrappedAgentSpec.tool_description`` in ``chat_agent_registry.py``.
"""
#
# ⚠️ NUMERACION: esta edicion lleva una migracion de mas
# (``0191_translate_prompt_catalog_to_spanish``), asi que toda la cadena va un
# paso adelante que la inglesa. Alla esta es la 0196; aqui es la 0197 y depende de
# ``0196_add_netspeed_calculator``. Copiar el numero del ingles rompe el grafo de migraciones.

from django.db import migrations


WRAPPED_TOOL_DESCRIPTION = "Chat-Agent-NetSpeed-Calculator"


def add_chat_agent_netspeed_calculator_tool(apps, schema_editor):
    Tool = apps.get_model("agent", "Tool")

    if Tool.objects.filter(toolDescription=WRAPPED_TOOL_DESCRIPTION).exists():
        return

    next_id = (Tool.objects.order_by("-idTool").first().idTool + 1) if Tool.objects.exists() else 1
    Tool.objects.create(
        idTool=next_id,
        toolName=f"tool-{next_id}",
        toolDescription=WRAPPED_TOOL_DESCRIPTION,
        toolContent="true",
    )


def remove_chat_agent_netspeed_calculator_tool(apps, schema_editor):
    Tool = apps.get_model("agent", "Tool")
    Tool.objects.filter(toolDescription=WRAPPED_TOOL_DESCRIPTION).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("agent", "0196_add_netspeed_calculator"),
    ]

    operations = [
        migrations.RunPython(add_chat_agent_netspeed_calculator_tool,
                             remove_chat_agent_netspeed_calculator_tool),
    ]
