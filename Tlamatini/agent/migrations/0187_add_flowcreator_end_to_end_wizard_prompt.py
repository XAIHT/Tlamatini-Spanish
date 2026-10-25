# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#   Created by  Angela López Mendoza · @angelahack1
# ═══════════════════════════════════════════════════════════════════
"""Catalog of Prompts — the FLOWCREATOR END-TO-END wizard (Angela, 2026-07-23).

A richer companion to the simple "make me a .flw" demo (#107 from 0186). This is
a full **Step-by-Step** wizard that walks the user all the way from a sentence to
a RUNNING flow:

  a) CREATE a flow with `chat_agent_flowcreator` — "monitor a GlassFish log and,
     on an ERROR, send me a Telegram with a summary" -> a real `.flw` on disk.
  b) OPEN that `.flw` in the Agentic Control Panel (agentic_control_panel.html).
  c) GUIDE the user, one action at a time, to change EVERY parameter that matters
     — the Monitor-Log file path, and the Telegrammer identity / recipient /
     api_id+api_hash or bot token / message — then VALIDATE, optionally fire a
     safe test error, and START the flow so it runs completely.

Contract compliance:
  * Category `agents_flows`; `sort_rank = 90` so it sits right after the simple
    FlowCreator create-demo (#107, rank 85) and the ALARM FLOW FORGE demo
    (#33, rank 80) — least-complex -> most-complex within the section.
  * Appended at the next free `idPrompt` (never renumber). It is a genuine
    Step-by-Step wizard (ticks Multi-Turn + Step-by-Step, ONE action per turn,
    STOP and WAIT for the user's READY between steps).
  * Drives `chat_agent_flowcreator` with a realistic, SAFE objective.
  * SECURITY: the wizard NEVER asks the user to type a Telegram api_id / api_hash
    / bot token into the chat — those go straight into the Telegrammer node's
    config dialog on the canvas. The live "fire a test error" step is opt-in and
    gated on the user confirming their own authorized credentials.
  * Parameter grammar (v1.44.0): `[[ ]]` = a value the USER fills in at the TOP;
    `< >` = a report slot only. No `{{ }}` needed here.

Reverse deletes exactly this row (matched by its unique promptContent).
"""
from django.db import migrations

DEMO_PROMPT = (
    "Tlamatini, sé mi <b>WIZARD DE FLOWCREATOR DE PRINCIPIO A FIN</b> — llévame desde una "
    "oración sencilla hasta un flow EN EJECUCIÓN que vigile mi log de GlassFish y "
    "me avise por Telegram cuando vea un error. Hazlo <b>un paso a la "

    "vez</b>.<br><br>PRECONDICIONES: marca <b>Multi-Turn</b> y <b>Paso a paso</b> en la barra de herramientas (al hacer "
    "clic en esta tarjeta ya se marcan). Deja ACPX, Ask Execs y Add-internet sin "

    "marcar.<br><br>LLENA ESTOS — reemplaza el texto dentro de los corchetes [[ ]] (todos OPCIONALES; si "
    "dejo un corchete sin tocar, USA EL PREDETERMINADO y NO me preguntes):<br>• "
    "GLASSFISH LOG PATH: [[ el path completo a tu server.log — OPCIONAL, predeterminado: "
    "C:/glassfish7/glassfish/domains/domain1/logs/server.log "
    "]]<br>• SEND THE ALERT TO: [[ tu @username de Telegram, +teléfono, o un nombre de contacto guardado "
    "— OPCIONAL, predeterminado: @your_telegram_username "
    "]]<br>• SEND AS: [[ <b>me</b> (desde tu propia cuenta de Telegram) o <b>bot</b> (desde un bot de "
    "BotFather ) — OPCIONAL, predeterminado: bot "
    "]]<br>• ALERT MESSAGE PREFIX: [[ un prefijo corto que se muestra antes del resumen del error — "
    "OPCIONAL, predeterminado: \"⚠️ GlassFish ALERT —\" "
    "]]<br>• FLOW FILE NAME: [[ OPCIONAL, predeterminado: glassfish_error_alert.flw "

    "]]<br><br>🔒 REGLA DE SEGURIDAD (nunca la rompas): NUNCA me vas a pedir que escriba "
    "mi <code>api_id</code> / <code>api_hash</code> / <code>bot_token</code> de Telegram en este chat. Las "
    "keys secretas SÓLO se escriben directamente en el diálogo de config del nodo Telegrammer en el "
    "canvas. Si un paso necesitara un secreto, me dices dónde pegarlo en el canvas — nunca "
    "lo recolectas "

    "aquí.<br><br>CÓMO DEBES COMPORTARTE — este es el punto, es el modo Paso a paso: haz EXACTAMENTE UNA acción por turno, "
    "luego DETENTE y ESPÉRAME. Después de cada acción, muéstrame el resultado concreto, luego termina con "
    "la única línea que me dice exactamente qué responder (normalmente <code>READY</code>). Nunca encadenes "
    "dos pasos. Nunca supongas mi respuesta. Si algo falla, dime claramente qué salió mal y "
    "qué revisar, y espera — nunca te saltes pasos.<br><br>LOS "

    "PASOS:<br><br><b>PASO "

    "1 — CREA EL FLOW.</b> Llama a <code>chat_agent_flowcreator</code> EXACTAMENTE UNA VEZ "
    "con <code>prompt='Monitor the GlassFish server log file at &lt;GLASSFISH LOG PATH&gt; for "
    "lines containing ERROR, SEVERE, FATAL or Exception; when one is found, summarize the error "
    "and send the summary to &lt;SEND THE ALERT TO&gt; on Telegram'</code> "
    "y <code>flow_filename='&lt;FLOW FILE NAME&gt;'</code> (sustituye mis llenados). Lee "
    "el bloque <code>INI_SECTION_FLOWCREATOR</code> y reporta: el <code>status</code>, "
    "el <code>flw_path</code> COMPLETO &lt;flw_path&gt; (lo necesito para abrir el archivo), el <code>agent_count</code> "
    "y el <code>connection_count</code>, y los agents que eligió en orden de ejecución (deberías "
    "ver aproximadamente Starter → Monitor-Log → Raiser → Summarizer → Parametrizer → Telegrammer → Ender). "
    "Si <code>status</code> es <code>error</code>, dilo y cita el mensaje — NO finjas que "
    "un flow fue creado. Luego pídeme que responda <code>READY</code>. ESPERA.<br><br><b>PASO "

    "2 — ABRE EL FLOW EN EL CONTROL PANEL.</b> NO llames a ningún tool. Dime que abra "
    "el <b>Agentic Control Panel</b> (el link de la navbar, o la URL <code>/agent/agentic_control_panel/</code>), "
    "luego <b>Archivo ▸ Abrir</b> y elija el <code>.flw</code> en el &lt;flw_path&gt; del PASO "
    "1. Dime que ahora debería ver toda la cadena dibujada de izquierda a derecha en el canvas. Pídeme que responda "
    "<code>READY</code> en cuanto pueda ver el flow. ESPERA.<br><br><b>PASO "

    "3 — PON EL PATH DEL ARCHIVO DE LOG (Monitor-Log).</b> Dime que haga doble clic en "
    "el nodo <b>Monitor-Log</b> para abrir su config, ponga <code>logfile_path</code> en mi GLASSFISH LOG "
    "PATH y (opcionalmente) ponga <code>keywords</code> en <code>ERROR, SEVERE, FATAL, Exception</code>, "
    "y luego Guarde. Explica en una línea que este es el archivo que va a vigilar. Pídeme que responda "
    "<code>READY</code>. ESPERA.<br><br><b>PASO "

    "4 — PON LA IDENTIDAD + EL DESTINATARIO DE TELEGRAM (Telegrammer).</b> Dime que haga doble clic "
    "en el nodo <b>Telegrammer</b> y ponga: <code>telegram.provider</code> = <code>user</code> "
    "si elegí 'me' o <code>bot</code> si elegí 'bot'; <code>telegram.chat_id</code> "
    "(o <code>contact_name</code>) = mi valor de SEND-THE-ALERT-TO; y <code>message</code> = mi ALERT "
    "MESSAGE PREFIX (nota: el Parametrizer del flow auto-rellena el resumen real del error en "
    "el message en tiempo de ejecución, así que el prefijo es sólo la entrada). Guarda. Pídeme que responda <code>READY</code>. "
    "ESPERA.<br><br><b>PASO "

    "5 — ESCRIBE LAS KEYS SECRETAS DE TELEGRAM EN EL CANVAS (nunca en el chat).</b> Dime, en "
    "el MISMO diálogo del nodo Telegrammer: si elegí <b>bot</b>, que pegue mi <code>telegram.bot_token</code> de BotFather "
    "(y que me asegure de haber presionado Start / escrito al bot una vez desde la cuenta del destinatario); "
    "si elegí <b>me</b>, que pegue mi <code>telegram.api_id</code> y mi <code>telegram.api_hash</code> "
    "de <code>https://my.telegram.org</code> (la primera vez aparecerá una ventana de login de Telegram con interfaz). "
    "Señálame <b>Config ▸ Access Keys Wizard</b> como la forma fácil de ponerlas de una "
    "vez. Recuérdame que son secretos — los escribo en el nodo, NUNCA en este chat. Guarda. Pídeme "
    "que responda <code>READY</code> en cuanto las keys estén puestas. ESPERA.<br><br><b>PASO "

    "6 — VALIDA EL FLOW.</b> Dime que presione <b>Validar</b> en el canvas y me "
    "lea el resultado. Si está limpio, dilo. Si muestra warnings/errores, ayúdame a interpretar el primero "
    "y qué arreglar (una conexión faltante, un campo requerido vacío). Pídeme que responda <code>READY</code> "
    "en cuanto Validar esté limpio. ESPERA.<br><br><b>PASO "

    "7 — PRUEBA EN VIVO OPCIONAL (opt-in, segura).</b> Pregúntame si quiero probarlo de principio a fin "
    "escribiendo una sola línea <code>ERROR</code> falsa en el log para que Monitor-Log se dispare y un Telegram "
    "real salga. Sólo si respondo <code>TESTNOW</code> Y confirmo que mis keys son reales y el "
    "destinatario está autorizado: usa <code>chat_agent_file_creator</code> (o "
    "<code>chat_agent_executer</code>) para agregar una línea como "
    "<code>[2026-01-01T00:00:00] SEVERE  Test error injected by the Tlamatini wizard</code> a mi "
    "path de log de GlassFish, luego dime que esté pendiente del Telegram. Si respondo <code>SKIP</code>, salta "
    "este paso por completo y NO escribas nada. ESPERA por <code>TESTNOW</code> o <code>SKIP</code>.<br><br><b>PASO "

    "8 — EJECÚTALO.</b> Dime que presione <b>Iniciar</b> (▶) en el canvas y confirme que los LEDs de los nodos "
    "se ponen verdes y el Starter arranca Monitor-Log, que ahora vigila mi archivo. Explica en una línea "
    "que el flow va a seguir corriendo y me va a mandar un Telegram cada vez que aparezca un error que coincida. Pídeme que "
    "responda <code>READY</code> en cuanto esté corriendo. ESPERA.<br><br><b>PASO "

    "9 — CIERRE.</b> Muestra una tabla HTML con class='exec-report-table' titulada "
    "'GlassFish → Telegram — Lo que construimos' con las columnas paso / nodo / qué pusiste — una fila por cada paso "
    "2..8, cada valor el real que usé. Mantén las celdas del cuerpo claras (background:#ffffff;color:#0f172a). "
    "Debajo, imprime: el &lt;flw_path&gt; COMPLETO, un recordatorio de una línea de que puedo volver a abrirlo y ajustarlo "
    "cuando quiera desde el Control Panel, y cómo DETENERLO (el botón Stop/⏹). Termina con END-RESPONSE."
)


def add_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    if Prompt.objects.filter(promptContent=DEMO_PROMPT).exists():
        return
    next_pid = (Prompt.objects.order_by('-idPrompt').values_list('idPrompt', flat=True).first() or 0) + 1
    Prompt.objects.update_or_create(
        idPrompt=next_pid,
        defaults={
            'promptName': f'prompt-{next_pid}',
            'promptContent': DEMO_PROMPT,
            'category': 'agents_flows',
            'hidden': False,
            # 33 (ALARM FLOW FORGE) = rank 80, 107 (simple FlowCreator create-demo)
            # = rank 85; this full end-to-end wizard is the most advanced, so 90.
            'sort_rank': 90,
        },
    )


def remove_prompt(apps, schema_editor):
    apps.get_model('agent', 'Prompt').objects.filter(promptContent=DEMO_PROMPT).delete()


class Migration(migrations.Migration):

    dependencies = [('agent', '0186_add_chat_agent_flowcreator')]

    operations = [migrations.RunPython(add_prompt, remove_prompt)]
