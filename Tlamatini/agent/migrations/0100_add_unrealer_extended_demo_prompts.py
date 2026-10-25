# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""
Seed three Catalog-of-Prompts demos that exercise the **extended** Unreal MCP
command surface — the System / Level / Asset / Material categories plus
``take_screenshot`` — none of which the original Unrealer demo (idPrompt 25,
migration 0087) touches. 0087 drives editor / blueprint / node / umg only; these
three drive the rest, at basic / medium / hard complexity:

    60  UNREAL SNAPSHOT          basic     get_current_level -> spawn_actor ->
                                           take_screenshot -> save_current_level
                                           (the observe->act loop, shortest new win)
    61  UNREAL SCENE FORGE       medium    get_current_level -> list_assets ->
                                           create_folder -> create_material ->
                                           create_material_instance ->
                                           set_material_parameter -> spawn_actor ->
                                           assign_material -> take_screenshot ->
                                           save_current_level (content authoring)
    62  UNREAL PYTHON & INTROSPECT  hard   execute_console_command (via the agent's
                                           console_command remap) -> get_class_info ->
                                           list_assets -> execute_python (the universal
                                           in-editor escape hatch, multi-line code passed
                                           as a triple-quoted params.code) -> take_screenshot

All three drive the wrapped **chat_agent_unrealer** Multi-Turn tool, exactly like
idPrompt 25. They are deliberately runnable against the same live editor: each opens
with the preconditions (UE5 open in dev mode, the Unreal MCP plugin's TCP listener
bound to 127.0.0.1:55557) and reminds the user to tick ONLY the **Multi-Turn**
checkbox — chat_agent_unrealer is NOT behind the ACPX / Skill surface, so ACPX is not
required (same as the Kalier 0099 and Windower 0095/0096 demos).

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js::loadPrompts) enumerates
promptName 'prompt-1', 'prompt-2', ... and BREAKS at the first missing slot, so the
catalog must stay a contiguous, gap-free 'prompt-1..N'. Slots 1-59 are fully occupied
(0099 appended the three KALI demos at 57-59). These three therefore APPEND at the tail
(60-62) — contiguity is preserved with no shift of any existing prompt, so no other
Prompt row's idPrompt/promptName changes. Reverse simply deletes 60-62.
(MAX_PROMPTS=100, so there is ample room.)

Honesty note baked into the prompts: a freshly-created (blank) Material declares no
named parameters, so ``set_material_parameter`` may legitimately return status='error'
("parameter not found"). Demo 61 records that verbatim and continues — the goal is to
show the full Material command surface and its real failure modes, mirroring how the
0087 demo treats a meshless spawn as "expected, not a failure".
"""
from django.db import migrations


# A reusable Unreal-themed banner palette (navy -> royal-blue -> emerald -> cyan),
# the same family the original idPrompt-25 demo uses so the Unreal MCP demos read as
# one branded set in the catalog.
_BANNER_OPEN = (
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,"
    "#0B1220 0%,#1F3A8A 33%,#10B981 66%,#22D3EE 100%);color:#fff;font-family:Inter,"
    "Segoe UI,sans-serif;text-align:center;'>"
)


UNREAL_SNAPSHOT_DEMO = (
    "Tlamatini, ejecuta la demo **UNREAL SNAPSHOT**, por favor &mdash; una muestra básica, de principio a fin, "
    "del *loop observar&rarr;actuar* en un editor de Unreal Engine 5 en vivo: lee "
    "el nivel actual, genera un actor, captura un screenshot del viewport en disco para que "
    "puedas VER el cambio, y guarda el nivel &mdash; todo desde el chat a través del tool wrapper "
    "**chat_agent_unrealer**. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques &mdash; confía en ellas y ve "
    "directo al Paso 1): (a) UE5 está abierto en modo dev con un proyecto cargado; (b) el "
    "plugin Unreal MCP está instalado y su listener TCP dentro del engine está escuchando en "
    "**127.0.0.1:55557**; (c) marca SÓLO la casilla **Multi-Turn** antes de enviar "
    "(NO se necesita ACPX &mdash; chat_agent_unrealer es el ÚNICO tool que puedes usar para "
    "hablar con Unreal; no uses chat_agent_pythonxer / execute_command ni tools de ACPX). "
    "Cada paso es exactamente UNA llamada a chat_agent_unrealer con la forma "
    "\"Run Unreal command with command='<verb>' and params.<k>=<v> ...\". Después de cada llamada, "
    "lee el JSON que devuelve (la respuesta de Unreal es un bloque INI_SECTION_UNREALER bajo el "
    "log_excerpt de la ejecución) y captura command/status/error más response_body. Si un paso "
    "devuelve status='error', regístralo tal cual, NO canceles, continúa. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128247; UNREAL SNAPSHOT &#128247;</h2>"
    "<div style='opacity:.9;margin-top:4px;'>Tlamatini Unrealer &mdash; spawn &rarr; screenshot &rarr; guardar</div></div>. "
    "\n\n"
    "Paso 1 (nivel &mdash; dónde estamos): llama a **chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='get_current_level'\". Captura el nombre del nivel / "
    "el package path / el conteo de actores de response_body. Si ESTO da error, el listener del plugin "
    "casi seguro no está escuchando &mdash; salta al banner de cierre con un "
    "veredicto 'INACCESIBLE' y sugiere revisar el UE Output Log en busca de "
    "'UnrealMCP listening on 127.0.0.1:55557'. "
    "\n\n"
    "Paso 2 (editor &mdash; genera algo que mirar): llama a **chat_agent_unrealer** con "
    "el request \"Run Unreal command with command='spawn_actor' and "
    "params.name='SnapshotProbe_Cube' and params.type='StaticMeshActor' and "
    "params.location=[0,0,200] and params.rotation=[0,0,0]\". "
    "\n\n"
    "Paso 3 (editor &mdash; OBSERVA el cambio): llama a **chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='take_screenshot' and "
    "params.filepath='C:/Temp/unreal_snapshot.png'\". Nota que params.filepath es un path de DISCO "
    "en la máquina donde corre el editor (NO un path de contenido /Game), así que el agent no "
    "lo reescribe. Captura el path guardado que devuelve el plugin. "
    "\n\n"
    "Paso 4 (nivel &mdash; persiste): llama a **chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='save_current_level'\". "
    "\n\n"
    "Paso 5: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Unreal Snapshot &mdash; Reporte de ejecución</strong>' y con las columnas <em>paso</em>, "
    "<em>categoría</em>, <em>unreal_command</em>, <em>status</em> (ok|error), "
    "<em>resumen</em> (resumen de una línea del response_body o del error) &mdash; una fila por cada "
    "llamada en orden de ejecución. Usa el status tal cual del bloque INI_SECTION_UNREALER; "
    "NO lo reclasifiques. Celdas del cuerpo claras (background:#ffffff;color:#0f172a; o rayado "
    "#f1f5f9), tono verde para ok y rojo suave para error, sin ocultar ninguna fila. "
    "\n\n"
    "Paso 6: cierra con un banner HTML que reutilice el estilo del Paso 0 y muestre, en letras "
    "grandes, '&#9989; SNAPSHOT CAPTURADO' (si todos los pasos devolvieron ok), "
    "'&#9888;&#65039; SNAPSHOT PARCIAL' (si algunos ok, algunos error) o "
    "'&#10060; UNREAL INACCESIBLE' (si el Paso 1 dio error), y debajo una métrica de una línea "
    "'nivel: <name> &middot; llamadas ok: <K>/<N> &middot; screenshot: "
    "C:/Temp/unreal_snapshot.png'. Termina con END-RESPONSE."
)


UNREAL_SCENE_FORGE_DEMO = (
    "Tlamatini, ejecuta la demo **UNREAL SCENE FORGE**, por favor &mdash; un pipeline de creación de "
    "contenido de complejidad media que ejercita las categorías **Asset** y **Material** de Unreal MCP "
    "(más una lectura/guardado de nivel y un screenshot), controlado por completo desde el chat "
    "a través del tool wrapper **chat_agent_unrealer**: inventaría el proyecto, crea una "
    "carpeta de contenido, escribe un material + una material instance, tiñe la instance, genera un "
    "actor de mesh, le asigna el material, le toma un screenshot al resultado y guarda el nivel. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques; ve directo al Paso 1): (a) UE5 "
    "abierto en modo dev con un proyecto cargado; (b) el listener TCP del plugin Unreal MCP está "
    "escuchando en **127.0.0.1:55557**; (c) marca SÓLO la casilla **Multi-Turn** (ACPX NO se "
    "necesita). Usa SÓLO chat_agent_unrealer para hablar con Unreal, UNA llamada por paso con la forma "
    "\"Run Unreal command with command='<verb>' and params.<k>=<v> ...\". Lee cada JSON "
    "que devuelve (la respuesta de Unreal es un bloque INI_SECTION_UNREALER bajo el log_excerpt), "
    "captura command/status/error/response_body, y con status='error' regístralo tal cual "
    "y CONTINÚA (no canceles). "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#127912; UNREAL SCENE FORGE &#127912;</h2>"
    "<div style='opacity:.9;margin-top:4px;'>Tlamatini Unrealer &mdash; carpeta &middot; material &middot; asignar &middot; disparar</div></div>. "
    "\n\n"
    "Paso 1 (nivel): \"Run Unreal command with command='get_current_level'\" &mdash; captura "
    "el nombre del nivel y el conteo de actores como la base 'before'. "
    "\n\n"
    "Paso 2 (system &mdash; inventario): \"Run Unreal command with command='list_assets' and "
    "params.path='/Game' and params.recursive=true\". Captura el conteo de assets de "
    "response_body (count o result.count). "
    "\n\n"
    "Paso 3 (asset &mdash; hazle un hogar a nuestro contenido): \"Run Unreal command with "
    "command='create_folder' and params.path='/Game/TlamatiniForge'\". "
    "\n\n"
    "Paso 4 (material &mdash; crea el material base): \"Run Unreal command with "
    "command='create_material' and params.name='M_TlamatiniForge' and "
    "params.path='/Game/TlamatiniForge'\". Captura el path del material creado. "
    "\n\n"
    "Paso 5 (material &mdash; deriva una instance): \"Run Unreal command with "
    "command='create_material_instance' and params.name='MI_TlamatiniForge' and "
    "params.parent_material='/Game/TlamatiniForge/M_TlamatiniForge' and "
    "params.path='/Game/TlamatiniForge'\". "
    "\n\n"
    "Paso 6 (material &mdash; tíñelo): \"Run Unreal command with "
    "command='set_material_parameter' and "
    "params.material='/Game/TlamatiniForge/MI_TlamatiniForge' and params.parameter='BaseColor' "
    "and params.value=[1,0,0]\". IMPORTANTE &mdash; un material EN BLANCO recién creado no declara "
    "parámetros con nombre, así que este paso PUEDE legítimamente devolver status='error' "
    "(\"parameter 'BaseColor' not found\"). Eso es ESPERADO para un material creado en el "
    "Paso 4 sin grafo de parámetros; registra el error tal cual y CONTINÚA. (En un proyecto "
    "real apuntarías params.material a un material padre que de verdad exponga un "
    "parámetro BaseColor, o agregarías el parámetro con un paso de execute_python primero.) "
    "\n\n"
    "Paso 7 (editor &mdash; algo que pintar): \"Run Unreal command with "
    "command='spawn_actor' and params.name='ForgeProbe_Cube' and "
    "params.type='StaticMeshActor' and params.location=[0,0,200]\". "
    "\n\n"
    "Paso 8 (material &mdash; asigna): \"Run Unreal command with command='assign_material' "
    "and params.actor='ForgeProbe_Cube' and "
    "params.material='/Game/TlamatiniForge/MI_TlamatiniForge' and params.slot=0\". "
    "\n\n"
    "Paso 9 (editor &mdash; OBSERVA): \"Run Unreal command with command='take_screenshot' "
    "and params.filepath='C:/Temp/unreal_scene_forge.png'\" (un path de disco en el host del editor; "
    "no normalizado). "
    "\n\n"
    "Paso 10 (nivel &mdash; persiste material + nivel): \"Run Unreal command with "
    "command='save_all'\" para que la nueva carpeta de contenido, el material, la instance y el nivel "
    "se escriban todos a disco. "
    "\n\n"
    "Paso 11: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Unreal Scene Forge &mdash; Reporte de ejecución</strong>' y con las columnas <em>paso</em>, "
    "<em>categoría</em> (level|system|asset|material|editor), <em>unreal_command</em>, "
    "<em>params (JSON compacto)</em>, <em>status</em> (ok|error), <em>resumen</em> "
    "&mdash; una fila por cada llamada en orden de ejecución, status tal cual del "
    "bloque INI_SECTION_UNREALER (NO lo reclasifiques). Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a; o rayado #f1f5f9); tono verde ok, rojo suave "
    "error, nada oculto. "
    "\n\n"
    "Paso 12: cierra con un banner HTML que reutilice el estilo del Paso 0 "
    "'&#9989; ESCENA FORJADA' (todos los pasos ok), '&#9888;&#65039; SCENE FORGE PARCIAL' "
    "(set_material_parameter es el soft-fail esperado; si SÓLO ese dio error, igual puedes "
    "llamarlo una demo exitosa de la superficie) o '&#10060; UNREAL INACCESIBLE' (el Paso 1 "
    "dio error), y debajo una métrica de una línea 'assets antes: <N> &middot; creados: "
    "folder+material+instance &middot; llamadas ok: <K>/<N> &middot; screenshot: "
    "C:/Temp/unreal_scene_forge.png'. Termina con END-RESPONSE."
)


UNREAL_PYTHON_INTROSPECT_DEMO = (
    "Tlamatini, ejecuta la demo **UNREAL PYTHON & INTROSPECTION**, por favor &mdash; una muestra avanzada "
    "de la categoría **System** de Unreal MCP: corre un comando de consola del editor, "
    "refleja una clase del engine, enumera assets y luego usa **execute_python** &mdash; "
    "el escape hatch universal dentro del editor que puede alcanzar CUALQUIER COSA de la API Python `unreal` "
    "de UE5 &mdash; antes de hacer un screenshot del viewport, todo desde el chat a través del tool wrapper "
    "**chat_agent_unrealer**. "
    "PRECONDICIONES que puedes dar por CIERTAS (NO las verifiques; ve directo al Paso 1): (a) UE5 "
    "abierto en modo dev con un proyecto cargado; (b) el listener TCP del plugin Unreal MCP está "
    "escuchando en **127.0.0.1:55557**; (c) el proyecto tiene el **Python Editor Script Plugin** "
    "activado (requerido para execute_python); (d) marca SÓLO la casilla **Multi-Turn** "
    "(NO se necesita ACPX). Usa SÓLO chat_agent_unrealer, UNA llamada por paso. Lee cada "
    "JSON que devuelve (bloque INI_SECTION_UNREALER bajo log_excerpt), captura "
    "command/status/error/response_body, y con status='error' regístralo tal cual y "
    "CONTINUE. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; " + _BANNER_OPEN +
    "<h2 style='margin:0;letter-spacing:2px;'>&#128013; UNREAL PYTHON &amp; INTROSPECTION &#128013;</h2>"
    "<div style='opacity:.9;margin-top:4px;'>Tlamatini Unrealer &mdash; consola &middot; reflejar &middot; listar &middot; execute_python</div></div>. "
    "\n\n"
    "Paso 1 (system &mdash; consola / CVar): llama a **chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='execute_console_command' and "
    "params.console_command='stat fps'\". NOTA: la línea de consola va en "
    "params.console_command (NO en params.command) &mdash; el agent Unrealer la remapea al "
    "params.command del wire automáticamente para que no choque con el command selector de "
    "nivel superior. Esto conmuta el stat de FPS en pantalla. "
    "\n\n"
    "Paso 2 (system &mdash; reflexión): llama a **chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='get_class_info' and params.class_name='StaticMeshActor'\". "
    "De response_body captura la clase padre y algunos de los nombres de propiedad que reporta "
    "&mdash; así es como descubres nombres de propiedad válidos antes de una llamada a set_actor_property. "
    "\n\n"
    "Paso 3 (system &mdash; enumeración de assets): llama a **chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='list_assets' and params.path='/Game' and "
    "params.recursive=true\". Captura el conteo de assets. "
    "\n\n"
    "Paso 4 (system &mdash; EL escape hatch, execute_python): llama a **chat_agent_unrealer** "
    "con un request cuyo params.code sea un literal Python multilínea con comillas triples (usa "
    "''' ... ''' para que los newlines y las comillas internas sobrevivan al parser), exactamente: "
    "\"Run Unreal command with command='execute_python' and params.code='''import unreal\n"
    "actors = unreal.EditorLevelLibrary.get_all_level_actors()\n"
    "unreal.log('Tlamatini execute_python: %d actors in the active level' % len(actors))\n"
    "ver = unreal.SystemLibrary.get_engine_version()\n"
    "unreal.log('Engine version: %s' % ver)\n"
    "len(actors)'''\". "
    "El handler de execute_python devuelve `success`, `result` (el repr de la última "
    "expresión &mdash; aquí el conteo de actores) y `log` (las líneas de unreal.log). Captura el "
    "conteo de actores y la línea de log de la versión del engine de response_body. Si este paso da error "
    "con un mensaje de 'Python' / 'plugin', el Python Editor Script Plugin probablemente está "
    "deshabilitado &mdash; regístralo y continúa. "
    "\n\n"
    "Paso 5 (editor &mdash; OBSERVA): llama a **chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='take_screenshot' and "
    "params.filepath='C:/Temp/unreal_python_introspection.png'\". "
    "\n\n"
    "Paso 6: muestra un MARCADOR DE STATUS &mdash; una fila de chips HTML con la forma "
    "<span style='display:inline-block;padding:8px 16px;margin:3px;border-radius:10px;"
    "font-weight:800;background:CHIP_BG;color:#ffffff;'>LABEL</span>: un chip 'console: <ok|err>', "
    "un chip 'reflect: <ok|err>', un chip 'list_assets: <ok|err>', un "
    "chip 'execute_python: <ok|err>' (CHIP_BG #16a34a cuando es ok, si no #dc2626), y un "
    "chip 'actors: <N>' (CHIP_BG #2563EB). "
    "\n\n"
    "Paso 7: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Unreal Python &amp; Introspection &mdash; Reporte de ejecución</strong>' y con las columnas "
    "<em>paso</em>, <em>unreal_command</em>, <em>status</em> (ok|error), <em>resumen</em> "
    "(clase padre para get_class_info; conteo de assets para list_assets; conteo de actores + versión del "
    "engine para execute_python; etc.) &mdash; una fila por cada llamada en orden de ejecución, status "
    "tal cual del bloque INI_SECTION_UNREALER. Celdas del cuerpo claras "
    "(background:#ffffff;color:#0f172a; o rayado #f1f5f9). "
    "\n\n"
    "Paso 8: cierra con un banner HTML que reutilice el estilo del Paso 0 "
    "'&#9989; PUENTE DE PYTHON EN VIVO' (si execute_python devolvió ok), "
    "'&#9888;&#65039; SUPERFICIE SYSTEM PARCIAL' (algunas llamadas de system ok, algunas error) o "
    "'&#10060; UNREAL INACCESIBLE' (si el Paso 1 dio error), y debajo una métrica de una línea "
    "'engine: <version> &middot; actors: <N> &middot; assets: <M> &middot; llamadas de system ok: "
    "<K>/4 &middot; screenshot: C:/Temp/unreal_python_introspection.png'. Termina con "
    "END-RESPONSE."
)


_NEW_PROMPTS = (
    (60, UNREAL_SNAPSHOT_DEMO),
    (61, UNREAL_SCENE_FORGE_DEMO),
    (62, UNREAL_PYTHON_INTROSPECT_DEMO),
)


def add_unrealer_extended_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_unrealer_extended_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0099_add_kalier_demo_prompts'),
    ]

    operations = [
        migrations.RunPython(
            add_unrealer_extended_demo_prompts,
            remove_unrealer_extended_demo_prompts,
        ),
    ]
