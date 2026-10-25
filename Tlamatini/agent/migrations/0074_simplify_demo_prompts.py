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
Plain-text-only versions of the seven ACPX demos. The rich-HTML siblings
in 0072 (idPrompt 36-41) and 0073 (idPrompt 42-48) embed literal banner
blocks (<div style='...'>...) into the prompt text so the LLM would
mimic them; in practice that HTML leaks into the chat-message input box
and the user-message bubble in the chat history as raw, unreadable noise.

This migration adds short, readable paragraph versions (10-20 seconds
to scan) at slots idPrompt 29-35 — the FIRST ACPX block in the catalog,
ahead of the rich-HTML (36-41) and Gemini-pinned (42-48) blocks, because
"plain-text only, works against ANY resolvable agent_id, no API key
pin" is the lowest-complexity ACPX entry point. The LLM is still told
to render its OUTPUT with banners and tables (the chat output supports
HTML); only the *prompt text the user sends* is now plain-text-only.

Order within the group follows the same Health Parade → Skill Catalog →
Permission Gate → End-to-End Pipeline → ACPX Auditor → Multi-CLI Relay →
Gemini Live Reasoning learning progression used by the two sibling groups.

idempotent via update_or_create.
"""
from django.db import migrations


P25_HEALTH_PARADE = (
    "Tlamatini, ejecuta la demo Desfile de salud y roster de ACPX, por favor. "
    "Paso 1: llama a acp_doctor y captura su array details. "
    "Paso 2: llama a list_acp_agents y captura cada entrada, poniendo "
    "especial atención al flag resolvable. "
    "Paso 3: muestra una tabla HTML titulada 'Roster ACPX de Tlamatini vs. "
    "acp-router de OpenClaw' con las columnas agent_id, command, description, "
    "resolvable_on_this_machine, openclaw_compatible. Todas las filas llevan "
    "openclaw_compatible YES porque las llaves agent_id son idénticas "
    "en ambos proyectos. "
    "Paso 4: llama a invoke_skill con skill_name 'hello-world' y "
    "args_json '{\"who\":\"angel\"}' para comprobar que el harness de Skills "
    "en proceso está vivo. "
    "Paso 5: cierra con una línea breve de veredicto que diga "
    "'ACPX TOTALMENTE OPERATIVO' si acp_doctor.ok es true, o "
    "'RUNTIME DE ACPX ACTIVO, AGENT DE PRUEBA NO INSTALADO' en caso contrario. "
    "Termina con END-RESPONSE."
)

P26_SKILL_CARNIVAL = (
    "Tlamatini, ejecuta la demo Carnaval del catálogo de Skills, por favor. "
    "Paso 1: llama a list_skills sin filtro y captura cada entrada. "
    "Paso 2: muestra una tabla HTML titulada 'Catálogo de Skills de Tlamatini "
    "(semilla de la fase 3)' con las columnas name, description, runtime, "
    "acpx_agent_or_in_process, openclaw_droppable. Todas las filas llevan "
    "openclaw_droppable YES porque el contrato del frontmatter de SKILL.md "
    "es compatible con OpenClaw tal cual. "
    "Paso 3: llama a invoke_skill con skill_name 'summarize' y "
    "args_json '{\"text\":\"Tlamatini ACPX implements the same agent_id "
    "mapping and the same permissionMode vocabulary as OpenClaw, so "
    "any acp-router skill written for one project runs unmodified on "
    "the other.\",\"target_words\":40}'. Cita el resumen que resulte. "
    "Paso 4: llama a invoke_skill con skill_name 'acp-router' y "
    "args_json '{\"intent\":\"reason about a complex codebase\","
    "\"prefer\":\"gemini\"}' y captura qué agent_id elige. "
    "Paso 5: cierra con un veredicto de una línea que nombre el agent_id elegido. "
    "Termina con END-RESPONSE."
)

P27_PIPELINE = (
    "Tlamatini, ejecuta la demo Pipeline ACPX de principio a fin, por favor. "
    "Paso 1: llama a acp_doctor. Si ok es false, recurre a invoke_skill "
    "summarize para cada paso de razonamiento en lugar de acp_spawn / acp_send, "
    "y anuncia el fallback en una línea breve. "
    "Paso 2: llama a acp_spawn con agent_id 'gemini' y task 'Lee el "
    "árbol de directorios de C:/Development/Tlamatini/agent/ como un ingeniero "
    "senior que revisa un framework multi-agent. En 6 oraciones, "
    "identifica qué subdirectorio es el más importante en la arquitectura "
    "y explica por qué de forma concreta.' y cwd 'C:/Development/Tlamatini'. "
    "Captura session_id y transcript_path. "
    "Paso 3: llama a acp_send sobre ese session_id con text 'Ahora propón una "
    "mejora concreta para ese subdirectorio en 4 oraciones, "
    "priorizando cambios que ayuden a alguien que recién empieza a contribuir.' Captura los events. "
    "Paso 4: llama a acp_kill sobre el session_id y confirma killed=true. "
    "Paso 5: llama a invoke_skill con skill_name 'summarize' y args_json "
    "'{\"text\":\"<paste joined text from spawn + send events>\","
    "\"target_words\":80}' para comprimir la transcripción. "
    "Paso 6: llama a chat_agent_file_creator con filepath "
    "'C:/Development/Tlamatini/_acpx_pipeline_demo_report.md' y "
    "content con el markdown resumido más una línea de pie "
    "que diga que Tlamatini ACPX generó el reporte. "
    "Paso 7: llama a chat_agent_notifier con title 'Demo del pipeline ACPX' "
    "y un mensaje de cierre de una línea. "
    "Paso 8: muestra una tabla HTML titulada 'ACPX vs. OpenClaw - esta ejecución' "
    "con las columnas behavior, covered_by_tlamatini, evidence y estas filas: "
    "lanzar un proceso hijo de un CLI externo; conversación de varios turnos; kill ordenado; "
    "transcripción guardada en disco; skill encadenado después. Todas las filas "
    "llevan YES; evidence cita session_id, el path de la transcripción o audit_id. "
    "Termina con END-RESPONSE."
)

P28_PERMISSION_TOUR = (
    "Tlamatini, ejecuta la demo Recorrido por la compuerta de permisos y la auditoría, por favor. "
    "Paso 1: llama a acp_doctor y reporta el permissionMode activo y "
    "nonInteractivePermissions de sus details. "
    "Paso 2: muestra una tabla HTML titulada 'Modos de permiso de ACPX - "
    "Tlamatini implementa la matriz de OpenClaw tal cual' con tres "
    "filas (approve-reads, approve-all, deny-all) y cuatro columnas "
    "(mode, what_it_does, when_to_use, openclaw_equivalent). La "
    "columna openclaw_equivalent es igual a la columna mode en todas las filas. "
    "Paso 3: llama a invoke_skill con skill_name 'hello-world' y "
    "args_json '{\"who\":\"audit-tour\"}'. Esto va a funcionar y va a devolver "
    "un audit_id; captúralo y repórtalo tal cual. "
    "Paso 4: llama a invoke_skill con skill_name "
    "'__definitely_does_not_exist__' y args_json '{}'. Esto debe "
    "dar error con code UNKNOWN_SKILL; cita code y reason tal cual. "
    "Paso 5: llama a list_skills con filter_keywords 'kyber' para "
    "demostrar el filtrado por palabras clave en el registro. "
    "Paso 6: cierra con un veredicto de una línea que nombre el audit_id del "
    "Paso 3 para que yo pueda ubicar el archivo NDJSON de esa invocación en "
    "~/.tlamatini/skill-audit/. Termina con END-RESPONSE."
)

P29_RELAY = (
    "Tlamatini, ejecuta la demo Relevo ACPX entre varios CLIs, por favor. "
    "Paso 1: llama a acp_doctor y captura su array details. "
    "Paso 2: llama a list_acp_agents. Fija el tramo A en agent_id 'gemini'. Para "
    "el tramo B, elige el primer agent_id resolvable de la lista que no "
    "sea gemini. Si sólo gemini es resolvable, simula el tramo B con "
    "invoke_skill con skill_name 'summarize' y anuncia el fallback en "
    "una línea breve. "
    "Paso 3 (TRAMO A - gemini): llama a acp_spawn con agent_id 'gemini' "
    "y task 'Eres un arquitecto de sistemas senior. En un párrafo "
    "(máximo 6 oraciones), describe los trade-offs de un gateway de webhooks "
    "basado en HTTP vs. un gateway de chat basado en WebSocket para disparar "
    "pipelines de automatización. Sé concreto y opina con firmeza.' Captura "
    "session_id_A y los events. Luego llama a acp_kill sobre session_id_A. "
    "Paso 4 (TRAMO B - par): llama a acp_spawn con el segundo agent_id "
    "(o simúlalo con invoke_skill summarize según el Paso 2) y task "
    "'Lee el siguiente análisis de un agent ACP par y produce un "
    "veredicto de 4 viñetas que diga si CONCUERDA, REFUTA o AMPLÍA cada "
    "punto. Sé específico. Análisis: <paste leg A text here>'. Captura "
    "session_id_B y los events; luego llama a acp_kill sobre session_id_B. "
    "Paso 5: muestra una tabla HTML titulada 'Relevo entre varios CLIs - comportamientos "
    "cubiertos' con las columnas behavior, leg_a_agent, leg_b_agent, "
    "openclaw_pattern_match y estas filas (lanzar el primer proceso hijo, recolectar la "
    "transcripción, pasar el contenido, lanzar el segundo proceso hijo con la primera "
    "transcripción como input, doble kill ordenado). openclaw_pattern_match "
    "es YES en todas las filas. "
    "Paso 6: cierra con un veredicto de una línea que nombre los dos agent_ids "
    "que realmente se usaron. Termina con END-RESPONSE."
)

P30_AUDITOR = (
    "Tlamatini, ejecuta la demo Repetición del auditor de ACPX, por favor. "
    "Paso 1: llama a invoke_skill con skill_name 'hello-world' y "
    "args_json '{\"who\":\"auditor\"}' para garantizar un registro de auditoría "
    "nuevo en disco. Captura el audit_id que devuelva. "
    "Paso 2: llama a acp_doctor y reporta el stateDir activo de sus "
    "details. "
    "Paso 3: llama a execute_command con command 'dir /b /o:-d "
    "%USERPROFILE%\\.tlamatini\\skill-audit 2>NUL || ls -1t "
    "~/.tlamatini/skill-audit/ 2>/dev/null' para listar, por mes de auditoría, los "
    "subdirectorios. "
    "Paso 4: llama a execute_command con command 'dir /b /s /o:-d "
    "%USERPROFILE%\\.tlamatini\\skill-audit\\*hello_world*auditor* "
    "2>NUL || find ~/.tlamatini/skill-audit -name "
    "\"*hello_world*auditor*\" 2>/dev/null | head -1 || true' para "
    "ubicar el archivo NDJSON que coincide con el audit_id del Paso 1. "
    "Paso 5: llama a chat_agent_file_extractor con filepath igual al "
    "path del NDJSON que ubicaste, para que podamos leer el stream estructurado de events. "
    "Paso 6: llama a invoke_skill con skill_name 'summarize' y "
    "args_json '{\"text\":\"<paste joined NDJSON event lines here>\","
    "\"target_words\":60}' para producir una narración legible de la repetición. "
    "Paso 7: muestra una tabla HTML titulada 'Rastro de auditoría - lo que hay "
    "en disco' con las columnas artifact, location, format, "
    "openclaw_equivalent_present y tres filas para "
    "skill_invocation_audit, acp_session_transcript, "
    "acp_session_record (todas NDJSON o JSON, todas YES). "
    "Paso 8: cierra con un veredicto de una línea que nombre el audit_id del "
    "Paso 1 y el path absoluto del NDJSON que ubicaste en el Paso 4. Termina con "
    "END-RESPONSE."
)

P31_GEMINI_LIVE = (
    "Tlamatini, ejecuta la demo Muestra de razonamiento en vivo con Gemini, por favor. "
    "Paso 1: llama a acp_doctor y confirma que el agent de prueba es gemini. "
    "Si ok es false, reporta 'Gemini no está en el PATH - instala "
    "@google/gemini-cli y vuelve a intentarlo.' y pon END-RESPONSE de inmediato. "
    "Si no, continúa. "
    "Paso 2 (TURNO 1): llama a acp_spawn con agent_id 'gemini', cwd "
    "'C:/Development/Tlamatini' y task 'Estás asesorando a una persona que desarrolla "
    "sola un asistente de IA autoalojado para desarrolladores. Enumera, "
    "en un párrafo breve, los tres pilares de arquitectura más subestimados "
    "de un sistema así - pilares cuya importancia sólo se vuelve "
    "evidente después de más de 12 meses de uso. Sé concreto; cita modos de "
    "falla específicos que aparecen si falta un pilar.' Captura "
    "session_id y los events; cítalos bajo el encabezado 'Turno 1 - "
    "Gemini habla'. "
    "Paso 3 (TURNO 2): llama a acp_send sobre el mismo session_id con text "
    "'De esos tres pilares, elige el ÚNICO que priorizarías para "
    "los próximos 30 días de trabajo y escribe un plan de acción de 4 líneas "
    "que describa qué entregar, en qué orden y con qué métrica de "
    "éxito.' Cita los events bajo el encabezado 'Turno 2 - el plan'. "
    "Paso 4 (TURNO 3): llama a acp_send sobre el mismo session_id con text "
    "'Ahora anticipa la forma más probable en que ese plan de 30 días va a fracasar. "
    "Escribe un registro de riesgos de 3 líneas: cada línea nombra el modo de falla, "
    "la señal de alerta temprana y la mitigación más barata.' Cita "
    "los events bajo el encabezado 'Turno 3 - el registro de riesgos'. "
    "Paso 5: llama a acp_kill sobre session_id y confirma killed=true. "
    "Paso 6: llama a invoke_skill con skill_name 'summarize' y "
    "args_json '{\"text\":\"<paste joined text from turns 1+2+3>\","
    "\"target_words\":120}'. Cita el resumen bajo el encabezado "
    "'Resumen ejecutivo'. "
    "Paso 7: llama a chat_agent_file_creator con filepath "
    "'C:/Development/Tlamatini/_gemini_live_reasoning.md' y content "
    "igual a un reporte en markdown con los tres turnos y el "
    "resumen ejecutivo, con un pie que indique que el reporte lo generó "
    "Tlamatini ACPX a través de un proceso hijo real de Gemini. "
    "Paso 8: llama a chat_agent_notifier con title 'Razonamiento en vivo "
    "con Gemini' y un mensaje de cierre de una línea. "
    "Paso 9: muestra una tabla HTML titulada 'Razonamiento en vivo con Gemini - "
    "Marcador de capacidades' con las columnas capability, "
    "demonstrated_this_run, evidence y estas filas: real_external_LLM_spawned; "
    "api_key_injected_via_acpx_env; multi_turn_conversation_3_turns; "
    "transcript_persisted_NDJSON; downstream_skill_chained; "
    "audit_trail_written; openclaw_protocol_compatible. "
    "demonstrated_this_run es YES en todas las filas; evidence cita "
    "session_id, el path de la transcripción, audit_id o el filepath del output. "
    "Termina con END-RESPONSE."
)


DEMO_PROMPTS = [
    (29, P25_HEALTH_PARADE),
    (30, P26_SKILL_CARNIVAL),
    (31, P28_PERMISSION_TOUR),
    (32, P27_PIPELINE),
    (33, P30_AUDITOR),
    (34, P29_RELAY),
    (35, P31_GEMINI_LIVE),
]


def simplify_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for id_prompt, content in DEMO_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=id_prompt,
            defaults={
                'promptName': f'prompt-{id_prompt}',
                'promptContent': content,
            },
        )


def downgrade_simplified_demo_prompts(apps, schema_editor):
    # Drop the plain-text slots this migration introduced (29-35).
    # The rich-HTML versions at 36-41 (from 0072) and Gemini-pinned
    # versions at 42-48 (from 0073) are untouched, so a partial rollback
    # leaves a coherent catalog (1-28 + 36-48).
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=(29, 30, 31, 32, 33, 34, 35)).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0073_acpx_demo_gemini_uplift'),
    ]

    operations = [
        migrations.RunPython(
            simplify_demo_prompts,
            downgrade_simplified_demo_prompts,
        ),
    ]
