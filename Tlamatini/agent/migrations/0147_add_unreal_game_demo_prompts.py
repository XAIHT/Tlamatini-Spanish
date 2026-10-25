# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
from django.db import migrations
from django.db.models import Max

# Three catalog prompts that build a small PLAYABLE Unreal game ("ForgeArena")
# end to end via the Unrealer agent, in three Multi-Turn runs: (1) the arena
# (folder + colored materials + lights + player start + floor + walls), (2)
# spinning collectible coins as a BP_Coin blueprint + confirm playable, (3)
# polish + screenshot + reliable save. They bake in every lesson learned live:
# canonical param names (material_path / parameter_name / actor_name), "already
# exists" treated as success, a Cube mesh assigned to spawned StaticMeshActors
# via execute_python, rotation done with a RotatingMovementComponent (a plain
# placed actor cannot spin), scaling via set_actor_scale3d, and a save via
# save_dirty_packages + save_current_level because save_all is flaky.
#
# Catalog classifier (tools_dialog.js::classifyPromptModes) badges them
# Multi-turn / Exec-report from the keywords ("Multi-Turn", "Exec Report",
# "operator", "chat_agent_unrealer"); there are NO acp_* / skill tokens, so they
# are NOT badged ACPX. Raw triple-quoted so the embedded [..] arrays, /Game/..
# paths and quotes need no escaping.
#
# CONTIGUITY: the #prompts-catalog dropdown enumerates prompt-1, prompt-2, ...
# and BREAKS at the first gap, so these are APPENDED at max(idPrompt)+1.. with
# no renumber. The start slot is computed at apply time (the dev/live catalog
# size shifts as inserts land), which always keeps the list gap-free.

PROMPT_BUILD = r"""Tlamatini, modo operador — CONSTRUYE CONMIGO UN JUEGO BÁSICO DE UNREAL (la "ForgeArena"). Mantén marcadas las casillas Multi-Turn y Exec Report. Usa SÓLO el tool chat_agent_unrealer (Unreal MCP en 127.0.0.1:55557). Esta es la parte 1 de 3 — la arena en sí.

Reglas de base:
- Un comando de Unreal por cada llamada al tool. Usa EXACTAMENTE estos nombres de parámetro: spawn_actor -> name/type/location/rotation/scale; create_material -> name/path; create_material_instance -> name/parent_material/path; set_material_parameter -> material_path/parameter_name/value; assign_material -> actor_name/material_path/slot.
- PRIMERO llama a get_current_level. Si Unreal NO responde, dime que Unreal no está accesible (abre el proyecto de UE e inicia el servidor Unreal MCP en 127.0.0.1:55557) y DETENTE — no sigas reintentando.
- Trata "already exists" o "failed to create folder" como SUCCESS y continúa.
- Un StaticMeshActor recién generado NO tiene mesh — dale un mesh Cube con execute_python (el módulo `unreal`: pon su StaticMeshComponent en /Engine/BasicShapes/Cube).

Construye, un paso a la vez:
1. get_current_level (prueba de conectividad).
2. create_folder path=/Game/ForgeArena
3. create_material name=M_ForgeBase path=/Game/ForgeArena
4. create_material_instance name=MI_Floor parent_material=/Game/ForgeArena/M_ForgeBase path=/Game/ForgeArena
5. create_material_instance name=MI_Wall parent_material=/Game/ForgeArena/M_ForgeBase path=/Game/ForgeArena
6. create_material_instance name=MI_Coin parent_material=/Game/ForgeArena/M_ForgeBase path=/Game/ForgeArena
7. set_material_parameter material_path=/Game/ForgeArena/MI_Floor parameter_name=BaseColor value=[0.05,0.1,0.3]
8. set_material_parameter material_path=/Game/ForgeArena/MI_Wall parameter_name=BaseColor value=[0.2,0.2,0.2]
9. set_material_parameter material_path=/Game/ForgeArena/MI_Coin parameter_name=BaseColor value=[1.0,0.8,0.0]
10. spawn_actor name=Sun type=DirectionalLight location=[0,0,800] rotation=[-45,30,0]
11. spawn_actor name=Sky type=SkyLight location=[0,0,800]
12. spawn_actor name=PlayerStart_1 type=PlayerStart location=[0,0,120]
13. spawn_actor name=Arena_Floor type=StaticMeshActor location=[0,0,0] scale=[20,20,1] — luego dale a Arena_Floor un mesh Cube (execute_python) y assign_material actor_name=Arena_Floor material_path=/Game/ForgeArena/MI_Floor slot=0.
14. Genera 4 muros como StaticMeshActors, dale a cada uno un mesh Cube + assign MI_Wall: Wall_N location=[0,1000,150] scale=[20,1,3]; Wall_S [0,-1000,150] [20,1,3]; Wall_E [1000,0,150] [1,20,3]; Wall_W [-1000,0,150] [1,20,3].

Termina con UNA tabla HTML (columnas: paso | categoría | unreal_command | params | status | resumen) que resuma cada comando. Luego END-RESPONSE.
"""


PROMPT_COINS = r"""Tlamatini, modo operador — parte 2 de 3 del juego ForgeArena: MONEDAS COLECCIONABLES GIRATORIAS que de verdad giran, y confirma que el nivel se puede jugar. Mantén marcadas las casillas Multi-Turn y Exec Report. Usa SÓLO chat_agent_unrealer. Las mismas reglas que en la parte 1 (nombres de parámetro exactos, "already exists" = success, llama primero a get_current_level y DETENTE si Unreal no está accesible).

Un cubo colocado sin más NO PUEDE girar, así que arma un Blueprint y genéralo:
1. create_blueprint name=BP_Coin parent_class=Actor path=/Game/ForgeArena
2. add_component_to_blueprint blueprint_name=BP_Coin component_type=StaticMeshComponent component_name=Mesh
3. set_static_mesh_properties blueprint_name=BP_Coin component_name=Mesh static_mesh=/Engine/BasicShapes/Cube
4. add_component_to_blueprint blueprint_name=BP_Coin component_type=RotatingMovementComponent component_name=Spin
5. set_component_property blueprint_name=BP_Coin component_name=Spin property_name=RotationRate property_value=[0,180,0]
6. compile_blueprint blueprint_name=BP_Coin
7. Genera 6 instancias de BP_Coin (spawn_blueprint_actor) en [400,400,200], [-400,400,200], [400,-400,200], [-400,-400,200], [0,600,200], [0,-600,200]. Luego ponlas del tamaño de una moneda: con execute_python (el módulo `unreal`) haz set_actor_scale3d(unreal.Vector(0.5,0.5,0.5)) en cada actor BP_Coin, y asigna MI_Coin donde se pueda.
8. Si en este build algún comando de blueprint tiene otro nombre o no existe, recurre a execute_python para crear BP_Coin (un Actor con un StaticMeshComponent + RotatingMovementComponent) y genera las 6 instancias de la misma forma.

Luego dime que se puede jugar: abre /Game/ForgeArena y presiona Play — el pawn predeterminado aparece en PlayerStart_1 para que yo pueda moverme.
Termina con UNA tabla HTML (paso | categoría | unreal_command | params | status | resumen). Luego END-RESPONSE.
"""


PROMPT_POLISH = r"""Tlamatini, modo operador — parte 3 de 3: PULE la ForgeArena, toma un screenshot y guárdala. Mantén marcadas las casillas Multi-Turn y Exec Report. Usa SÓLO chat_agent_unrealer; PREFIERE execute_python (el módulo `unreal`) por confiabilidad. Llama primero a get_current_level y DETENTE si Unreal no está accesible.

1. Asegúrate de que las monedas tengan tamaño de moneda: para cada actor cuyo label empiece con "Coin" o "BP_Coin", haz set_actor_scale3d(unreal.Vector(0.5,0.5,0.5)).
2. Corrige la advertencia de "multiple directional lights": deja exactamente UNA DirectionalLight (el Sun) y elimina cualquier otro actor DirectionalLight; elimina también cualquier PlayerStart duplicado para que quede exactamente uno.
3. take_screenshot filepath=C:/Temp/forge_arena.png (para que podamos ver el resultado).
4. Guarda de forma confiable — save_all puede fallar, así que usa execute_python: unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True) y luego unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level().
5. Dime exactamente cómo probarla: abre /Game/ForgeArena, presiona Play y recorre/vuela la arena desde PlayerStart_1.
Termina con UNA tabla HTML (paso | categoría | unreal_command | params | status | resumen). Luego END-RESPONSE.
"""


_NEW_PROMPTS = (PROMPT_BUILD, PROMPT_COINS, PROMPT_POLISH)


def add_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    start = (Prompt.objects.aggregate(m=Max('idPrompt'))['m'] or 0) + 1
    for offset, content in enumerate(_NEW_PROMPTS):
        pid = start + offset
        Prompt.objects.update_or_create(
            idPrompt=pid,
            defaults={'promptName': f'prompt-{pid}', 'promptContent': content},
        )


def remove_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    # These were appended at the end; remove the top len(_NEW_PROMPTS) rows.
    ids = list(
        Prompt.objects.order_by('-idPrompt').values_list('idPrompt', flat=True)[:len(_NEW_PROMPTS)]
    )
    Prompt.objects.filter(idPrompt__in=ids).delete()


class Migration(migrations.Migration):
    dependencies = [('agent', '0146_update_createsuperuser_wizard_continuation')]
    operations = [migrations.RunPython(add_demo_prompts, remove_demo_prompts)]
