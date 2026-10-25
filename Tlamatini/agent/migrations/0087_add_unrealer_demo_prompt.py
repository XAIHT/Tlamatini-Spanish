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
Seed one end-to-end Unreal MCP demo prompt that exercises the
chat_agent_unrealer wrapped Multi-Turn tool across every Unreal MCP
command category (editor / blueprint / node / umg) in a single guided
Multi-Turn run.

Preconditions documented in the prompt body:
- An Unreal Engine 5 project is already running in dev mode (PIE not
  required — the editor itself listens).
- The Unreal MCP plugin is installed and the in-engine TCP listener
  is bound to 127.0.0.1:55557.

Slot: idPrompt 25 — placed BEFORE the Multi-Turn demos (26-28) and the ACPX
demos (29-48) because driving Unreal's editor with a single chat_agent_unrealer
verb per step is less complex than orchestrating multi-tool Multi-Turn flows
or external coding-agent CLIs through ACPX.
"""
from django.db import migrations


PROMPT_CONTENT = (
    "Tlamatini, ejecuta la demo **Recorrido completo por el Editor con Unreal MCP**, por favor. "
    "Precondiciones que puedes dar por CIERTAS en esta ejecución (NO las verifiques — "
    "confía en ellas y ve directo al Paso 1): "
    "(a) Unreal Engine 5 está abierto en modo dev con un proyecto cargado; "
    "(b) el plugin Unreal MCP está instalado y su listener TCP dentro del engine está "
    "escuchando en **127.0.0.1:55557**; "
    "(c) el tool wrapper **chat_agent_unrealer** de Tlamatini está activado "
    "(lo está de forma predeterminada) y es el ÚNICO tool que puedes usar para hablar con Unreal — "
    "NO levantes chat_agent_pythonxer ni execute_command con código de sockets crudo, "
    "y NO hagas spawn con ACPX (eso es para CLIs externos de coding agents, no para "
    "el plugin del editor de Unreal). "
    "Cada paso de abajo DEBE ser exactamente UNA llamada a chat_agent_unrealer cuyo "
    "request tenga esta forma "
    "\"Run Unreal command with command='<verb>' and params.<k1>='<v1>' and params.<k2>=<v2> ...\". "
    "Después de cada llamada, lee el JSON que devuelve el tool wrapper — la respuesta de Unreal "
    "viene dentro del `log_excerpt` de la ejecución como un bloque INI_SECTION_UNREALER — "
    "y captura host/port/command/status/error, además del "
    "`response_body` visible para el asistente, para que puedas armar la fila de cada paso en el Paso 9. "
    "Si algún paso devuelve status='error', registra el error tal cual, NO canceles "
    "y sigue con el siguiente paso para que la tabla final muestre la ejecución completa. "
    "\n\n"
    "Paso 0: muestra un banner HTML de apertura: "
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,#0B1220 0%,#1F3A8A 33%,#10B981 66%,#22D3EE 100%);color:#fff;font-family:Inter,Segoe UI,sans-serif;text-align:center;'>"
    "<h2 style='margin:0;letter-spacing:2px;'>&#127918; RECORRIDO COMPLETO POR EL EDITOR CON UNREAL MCP &#127918;</h2>"
    "<div style='opacity:.9;margin-top:4px;'>Tlamatini Unrealer &mdash; chat_agent_unrealer sobre 127.0.0.1:55557</div></div>. "
    "\n\n"
    "Paso 1 (editor &mdash; prueba rápida de la conexión): llama a "
    "**chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='get_actors_in_level'\". "
    "Esta es tu prueba definitiva de que el socket TCP está vivo; el response_body "
    "es un dict JSON cuyo array `actors` (o `result.actors`) lista cada actor "
    "que hay en el nivel activo. Captura el conteo para la tabla final. "
    "\n\n"
    "Paso 2 (editor &mdash; haz spawn de una primitiva directo en el nivel): llama a "
    "**chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='spawn_actor' and params.name='TlamatiniProbe_Cube' "
    "and params.type='StaticMeshActor' and params.location=[0,0,150] and params.rotation=[0,0,0]\". "
    "Esto coloca un StaticMeshActor vacío llamado TlamatiniProbe_Cube 150 unidades arriba del origen del mundo. "
    "Todavía no tiene mesh asignado &mdash; es lo esperado con este comando. "
    "\n\n"
    "Paso 3 (editor &mdash; verifica que el spawn funcionó): llama a "
    "**chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='find_actors_by_name' and params.pattern='TlamatiniProbe_Cube'\". "
    "La respuesta debe listar al menos una coincidencia; si no hay ninguna, registra la discrepancia "
    "pero no canceles. "
    "\n\n"
    "Paso 4 (blueprint &mdash; crea la estructura de una nueva clase Blueprint): llama a "
    "**chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='create_blueprint' and params.name='BP_TlamatiniProbe' "
    "and params.parent_class='Actor'\". "
    "Esto crea un Blueprint Actor BP_TlamatiniProbe totalmente nuevo en el path de contenido "
    "predeterminado del plugin Unreal MCP. "
    "\n\n"
    "Paso 5 (blueprint &mdash; agrégale un componente static-mesh): llama a "
    "**chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='add_component_to_blueprint' and params.blueprint_name='BP_TlamatiniProbe' "
    "and params.component_type='StaticMeshComponent' and params.component_name='ProbeMesh' "
    "and params.location=[0,0,0] and params.rotation=[0,0,0] and params.scale=[1,1,1]\". "
    "\n\n"
    "Paso 6 (blueprint &mdash; compila para que el editor acepte el nuevo BP): llama a "
    "**chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='compile_blueprint' and params.blueprint_name='BP_TlamatiniProbe'\". "
    "Captura el status de compilación de la respuesta; algunos builds del plugin devuelven "
    "`{\"success\": true}` y otros devuelven `{\"status\": \"ok\"}`. Cualquiera de las dos formas significa OK. "
    "\n\n"
    "Paso 7 (editor &mdash; haz spawn de una instancia del BP recién compilado): llama a "
    "**chat_agent_unrealer** con el request "
    "\"Run Unreal command with command='spawn_blueprint_actor' and params.blueprint_name='BP_TlamatiniProbe' "
    "and params.actor_name='TlamatiniProbe_Spawned' and params.location=[200,0,150] and params.rotation=[0,0,0]\". "
    "Esto pone una instancia de BP_TlamatiniProbe en el nivel, junto al cubo vacío del Paso 2. "
    "\n\n"
    "Paso 8 (umg &mdash; arma un widget de HUD sencillo y muéstralo): haz CUATRO llamadas a chat_agent_unrealer "
    "en orden y captura la respuesta JSON de cada una: "
    "(8a) \"Run Unreal command with command='create_umg_widget_blueprint' and params.widget_name='WBP_TlamatiniProbeHUD' "
    "and params.parent_class='UserWidget' and params.path='/Game/UI'\"; "
    "(8b) \"Run Unreal command with command='add_text_block_to_widget' and params.widget_name='WBP_TlamatiniProbeHUD' "
    "and params.text_block_name='ProbeLabel' and params.text='Tlamatini Probe Active' and params.position=[40,40] "
    "and params.size=[320,48] and params.font_size=24 and params.color=[1,1,1,1]\"; "
    "(8c) \"Run Unreal command with command='add_button_to_widget' and params.widget_name='WBP_TlamatiniProbeHUD' "
    "and params.button_name='ProbeDismiss' and params.text='Dismiss' and params.position=[40,108] "
    "and params.size=[160,40] and params.font_size=16 and params.color=[1,1,1,1] "
    "and params.background_color=[0.1,0.1,0.1,1]\"; "
    "(8d) \"Run Unreal command with command='add_widget_to_viewport' and params.widget_name='WBP_TlamatiniProbeHUD' "
    "and params.z_order=10\". "
    "Después de 8d el widget queda en el viewport del juego &mdash; visible si el usuario presionó Play; si no, queda en cola "
    "para la siguiente sesión PIE. No trates la ausencia de PIE como un error. "
    "\n\n"
    "Paso 9 (muestra el reporte de la ejecución): muestra una tabla HTML con class='exec-report-table' "
    "titulada '<strong>Reporte de ejecución de Unreal MCP &mdash; chat_agent_unrealer sobre 127.0.0.1:55557</strong>' "
    "y con las columnas "
    "<em>paso</em>, <em>categoría</em>, <em>unreal_command</em>, <em>params (JSON compacto)</em>, "
    "<em>status</em> (ok|error), <em>resumen</em> (resumen de una línea del response_body o del error). "
    "Una fila por cada llamada a Unreal (o sea, 12 filas en total: 1 del Paso 1, 1 del Paso 2, 1 del Paso 3, "
    "1 del Paso 4, 1 del Paso 5, 1 del Paso 6, 1 del Paso 7 y 4 de los Pasos 8a-d). "
    "Ordena las filas según el orden de ejecución. Usa tal cual la columna **status** del bloque INI_SECTION_UNREALER "
    "(su campo status); NO la reclasifiques. Tono sugerido: fondo de celda verde para ok, "
    "rojo suave para error, sin ocultar ninguna fila &mdash; el objetivo de esta demo es mostrar la "
    "superficie COMPLETA de comandos de una sola vez. "
    "\n\n"
    "Paso 10: cierra con un banner HTML que muestre, en letras grandes, "
    "'&#9989; UNREAL MCP TOTALMENTE OPERATIVO' (si todos los pasos devolvieron status='ok'), "
    "'&#9888;&#65039; UNREAL MCP PARCIALMENTE OPERATIVO' (si al menos un paso funcionó pero "
    "algún paso devolvió error) o '&#10060; UNREAL MCP INACCESIBLE' (si el propio Paso 1 dio error "
    "&mdash; en ese caso la causa más común es que el listener TCP del plugin dentro del engine "
    "todavía no está escuchando; sugiere revisar en el Output Log de Unreal la línea 'UnrealMCP listening on 127.0.0.1:55557'). "
    "Debajo del banner, muestra una métrica de una línea: "
    "'Total de llamadas a Unreal: <N>, ok: <K>, error: <N-K>, delta del conteo de actores del nivel: "
    "<count after Step 7 minus count after Step 1>'. "
    "\n\n"
    "Nota de limpieza (informativa, NO es un paso): la demo deja tres artefactos nuevos en el proyecto "
    "(el actor TlamatiniProbe_Cube, el blueprint BP_TlamatiniProbe con una instancia generada "
    "TlamatiniProbe_Spawned y el widget /Game/UI/WBP_TlamatiniProbeHUD). Se conservan a propósito "
    "para que el usuario pueda revisarlos en el editor. Para limpiarlos después, abre un chat "
    "de seguimiento con llamadas de chat_agent_unrealer a delete_actor para cada uno, más un "
    "clic derecho > Delete normal en el editor sobre BP_TlamatiniProbe y WBP_TlamatiniProbeHUD en el Content Browser. "
    "Termina con END-RESPONSE."
)


def add_unrealer_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.get_or_create(
        idPrompt=25,
        defaults={
            'promptName': 'prompt-25',
            'promptContent': PROMPT_CONTENT,
        }
    )


def remove_unrealer_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(promptName='prompt-25').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0086_add_chat_agent_unrealer_tool'),
    ]

    operations = [
        migrations.RunPython(add_unrealer_demo_prompt, remove_unrealer_demo_prompt),
    ]
