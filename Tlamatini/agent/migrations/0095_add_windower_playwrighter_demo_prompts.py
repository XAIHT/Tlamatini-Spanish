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
Seed four fancy demo prompts that showcase the **Windower** (Win32 window
manager) and **Playwrighter** (scripted browser automation) agents from chat,
so the user can pick them from the Catalog of Prompts and watch each agent
*physically perform* on screen (a real window snapping/maximizing; a real
browser driving itself with headless=false).

Two prompts per agent — one basic, one medium:

    51  WINDOW SPOTLIGHT        Windower    basic   (focus+maximize+list+close)
    52  WINDOW CHOREOGRAPHY     Windower    medium  (restore->tile->move->list->close)
    53  BROWSER SPOTLIGHT       Playwrighter basic  (open example.com, extract+assert+shot)
    54  BROWSER WIZARD          Playwrighter medium (Wikipedia search: fill->click->wait->extract->assert->shot)

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js::loadPrompts) enumerates
promptName 'prompt-1', 'prompt-2', ... and BREAKS at the first missing slot, so
the catalog must stay a contiguous, gap-free 'prompt-1..N'. Slots 1-50 are
fully occupied (0090 shifted the Multi-Turn/ACPX block down so the last demo is
the Gemini-pinned ACPX showcase at 50). These four demos therefore APPEND at the
tail (51-54) — contiguity is preserved with no shift of any existing prompt, so
no other Prompt row's idPrompt/promptName changes. Reverse simply deletes 51-54.

Unlike the 0090 Reviewer/Analyzer skill demos, these drive the **wrapped
chat_agent_windower / chat_agent_playwrighter tools**, which are NOT behind the
ACPX/Skill surface — so each prompt reminds the user to tick ONLY the
**Multi-Turn** checkbox (ACPX is not required). Windower is Windows-only (Win32);
Playwrighter needs Playwright installed (`pip install playwright && playwright
install`) and uses headless=false so the browser is visible.
"""
from django.db import migrations


# ── Demo-prompt content ────────────────────────────────────────────────

WINDOWER_BASIC_DEMO = (
    "Tlamatini, ejecuta la demo **VENTANA BAJO EL REFLECTOR**, por favor &mdash; una muestra breve y "
    "totalmente visible del agent **Windower** (el administrador de ventanas "
    "del escritorio), controlado desde el chat a través de su tool wrapper **chat_agent_windower**. "
    "PRECONDICIONES: marca SÓLO la casilla **Multi-Turn** en la barra de herramientas antes de "
    "enviar (NO se necesita ACPX &mdash; Windower es un tool Multi-Turn "
    "estándar). Esta demo es sólo para Windows (Windower usa la API Win32). "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; "
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,#0F2C4D 0%,#1E6FB8 50%,#4FC3F7 100%);color:#ffffff;font-family:Inter,Segoe UI,sans-serif;text-align:center;'><h2 "
    "style='margin:0;letter-spacing:2px;color:#ffffff;'>&#129003; VENTANA BAJO EL REFLECTOR &#129003;</h2><div "
    "style='opacity:.92;margin-top:4px;color:#ffffff;'>Tlamatini Windower &mdash; trae una ventana real al frente y mírala crecer</div></div>. "
    "\n\n"
    "Paso 1: abre Notepad para que haya una ventana que administrar &mdash; llama "
    "a **chat_agent_executer** con script='notepad' y non_blocking=true y luego "
    "confirma que la ventana está arriba con **chat_agent_window_present** (window_title='Notepad'). "
    "\n\n"
    "Paso 2: tráela al frente y maximízala para que el usuario VEA cómo se mueve "
    "&mdash; llama a **chat_agent_windower** con action='maximize' y "
    "window_title='Notepad' y activate_after=true. "
    "\n\n"
    "Paso 3: vuelve a leer la ventana en vivo con **chat_agent_windower** action='list' y "
    "window_title='Notepad'. De los campos promovidos del resultado, captura: matched, "
    "match_count, state, left, top, width, height. "
    "\n\n"
    "Paso 4: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Operación de ventana</strong>' y dos columnas <em>campo</em> / "
    "<em>valor</em>, una fila para cada uno de action, window_title, matched, state, left, "
    "top, width, height (los campos promovidos de INI_SECTION_WINDOWER). Deja cada celda "
    "del cuerpo con fondo claro y texto oscuro (background:#ffffff;color:#0f172a; o "
    "rayado #f1f5f9). "
    "\n\n"
    "Paso 5: limpia &mdash; cierra la ventana con **chat_agent_windower** "
    "action='close' y window_title='Notepad'. Si aparece un diálogo 'Save changes?', "
    "descártalo SIN guardar con **chat_agent_keyboarder** input_sequence=\"alt+n\". "
    "\n\n"
    "Paso 6: cierra con un banner HTML que reutilice el gradiente del Paso 0 y muestre, en "
    "letras blancas grandes, 'VENTANA ADMINISTRADA &#10003;' y, debajo, una "
    "métrica de una línea 'estado: <state> &middot; tamaño: <width>x<height> &middot; en "
    "(<left>,<top>)'. Termina con END-RESPONSE."
)

WINDOWER_MEDIUM_DEMO = (
    "Tlamatini, ejecuta la demo **COREOGRAFÍA DE VENTANAS**, por favor &mdash; una muestra más completa "
    "y totalmente visible que hace bailar una sola ventana por la pantalla "
    "con los verbos tile / move / list del agent **Windower**, a través de su tool wrapper "
    "**chat_agent_windower**. "
    "PRECONDICIONES: marca SÓLO la casilla **Multi-Turn** antes de enviar (ACPX "
    "NO es necesario). Sólo para Windows (Win32). Haz cada operación de ventana como una llamada "
    "SEPARADA a chat_agent_windower y haz una pausa breve entre ellas para que el movimiento "
    "sea visible. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; "
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,#0F2C4D 0%,#1E6FB8 50%,#4FC3F7 100%);color:#ffffff;font-family:Inter,Segoe UI,sans-serif;text-align:center;'><h2 "
    "style='margin:0;letter-spacing:2px;color:#ffffff;'>&#129003; COREOGRAFÍA DE VENTANAS "
    "&#129003;</h2><div style='opacity:.92;margin-top:4px;color:#ffffff;'>Tlamatini Windower &mdash; acomoda, ajusta y desliza una ventana en vivo</div></div>. "
    "\n\n"
    "Paso 1: abre Notepad con **chat_agent_executer** script='notepad' "
    "y non_blocking=true y luego confírmalo con **chat_agent_window_present** "
    "(window_title='Notepad'). "
    "\n\n"
    "Paso 2: haz esta coreografía, UNA llamada a chat_agent_windower por movimiento, cada "
    "una con window_title='Notepad' y activate_after=true, y captura los campos promovidos "
    "state/left/top/width/height después de cada "
    "llamada: (a) action='restore'; "
    "(b) action='arrange' y arrange_mode='left' (se ajusta a la mitad izquierda); "
    "(c) action='arrange' y arrange_mode='right' (se ajusta a la mitad derecha); "
    "(d) action='arrange' y arrange_mode='top-left' (cuadrante superior izquierdo); "
    "(e) action='move_resize' y pos_x=220 y pos_y=160 y width=900 y height=600 "
    "(un rectángulo explícito). \n\nPaso "
    "3"
    ": enumera todo el escritorio con **chat_agent_windower** action='list' (deja "
    "window_title vacío) y captura match_count (el número de ventanas abiertas). \n\nPaso "
    "4"
    ": muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Rastro de la coreografía de ventanas</strong>' y con las columnas <em>paso</em>, "
    "<em>action</em>, <em>modo / geometría</em>, <em>state</em>, <em>left</em>, "
    "<em>top</em>, <em>width</em>, <em>height</em> &mdash; una fila por cada uno de los cinco "
    "movimientos (a)..(e) con los campos promovidos de esa llamada. Deja cada celda del cuerpo con "
    "fondo claro y texto oscuro (background:#ffffff;color:#0f172a; o rayado "
    "#f1f5f9). "
    "\n\n"
    "Paso 5: limpia &mdash; **chat_agent_windower** action='close' y "
    "window_title='Notepad'; si aparece un diálogo 'Save changes?', descártalo SIN guardar "
    "con **chat_agent_keyboarder** input_sequence=\"alt+n\". "
    "\n\n"
    "Paso 6: cierra con un banner HTML que reutilice el gradiente del Paso 0 y muestre, en "
    "letras blancas grandes, 'COREOGRAFÍA COMPLETA &#10003;' y, debajo, una "
    "métrica de una línea 'movimientos hechos: 5 &middot; ventanas abiertas vistas: <match_count> "
    "&middot; tamaño final: <width>x<height>'. Termina con END-RESPONSE."
)

PLAYWRIGHTER_BASIC_DEMO = (
    "Tlamatini, ejecuta la demo **BROWSER BAJO EL REFLECTOR**, por favor &mdash; una muestra breve y "
    "totalmente visible del agent **Playwrighter** manejando un browser REAL a "
    "través de su tool wrapper **chat_agent_playwrighter**. "
    "PRECONDICIONES: marca SÓLO la casilla **Multi-Turn** antes de enviar (ACPX "
    "NO es necesario). Playwright debe estar instalado (`pip install playwright && "
    "playwright install`). La demo usa headless=false para que VEAS cómo el browser "
    "se abre y se maneja solo, y hold_open_seconds=10 para que siga visible 10 "
    "segundos antes de cerrarse. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; "
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,#3D1766 0%,#D90368 50%,#0FA3B1 100%);color:#ffffff;font-family:Inter,Segoe UI,sans-serif;text-align:center;'><h2 "
    "style='margin:0;letter-spacing:2px;color:#ffffff;'>&#127760; BROWSER BAJO EL REFLECTOR &#127760;</h2><div "
    "style='opacity:.92;margin-top:4px;color:#ffffff;'>Tlamatini Playwrighter &mdash; mira cómo un browser real lee una página por ti</div></div>. "
    "\n\n"
    "Paso 1: llama a **chat_agent_playwrighter** con start_url='https://example.com' "
    "y headless=false y hold_open_seconds=10 y "
    "steps_json='[{\"action\":\"wait_for\",\"selector\":\"h1\"},{\"action\":\"extract_text\",\"selector\":\"h1\",\"name\":\"heading\"},{\"action\":\"extract_text\",\"selector\":\"p\",\"name\":\"intro\"},{\"action\":\"assert_visible\",\"selector\":\"a\"},{\"action\":\"screenshot\",\"path\":\"C:/Temp/example_spotlight.png\",\"full_page\":true}]'. "
    "\n"
    "\n"
    "Paso "
    "2"
    ": analiza el resultado de la ejecución y captura los campos promovidos status, final_url, "
    "steps_run, assert_result, además de los valores extraídos 'heading' e 'intro' y el "
    "path del screenshot. "
    "\n\n"
    "Paso 3: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Ejecución del browser</strong>' y dos columnas <em>campo</em> / <em>valor</em>, una "
    "fila para cada uno de start_url, final_url, status, steps_run, assert_result, "
    "heading y el path del screenshot. Deja cada celda del cuerpo con fondo claro y texto oscuro "
    "(background:#ffffff;color:#0f172a; o rayado #f1f5f9). "
    "\n\n"
    "Paso 4: muestra el párrafo intro extraído dentro de un elemento HTML "
    "<blockquote style='border-left:6px solid #D90368;padding:12px "
    "18px;background:#ffffff;color:#0f172a;border-radius:8px;'>...intro...</blockquote>. "
    "\n\n"
    "Paso 5: cierra con un banner HTML que reutilice el gradiente del Paso 0 y muestre, en "
    "letras blancas grandes, 'PÁGINA CAPTURADA &#10003;' (si status es ok y "
    "assert_result es pass) o, en caso contrario, 'EJECUCIÓN DEL BROWSER: <status>' y, debajo, una "
    "métrica de una línea 'status: <status> &middot; assert: <assert_result> &middot; "
    "pasos: <steps_run> &middot; screenshot: C:/Temp/example_spotlight.png'. Termina con "
    "END-RESPONSE."
)

PLAYWRIGHTER_MEDIUM_DEMO = (
    "Tlamatini, ejecuta la demo **WIZARD DEL BROWSER**, por favor &mdash; una muestra más completa y "
    "totalmente visible del agent **Playwrighter** haciendo una búsqueda interactiva "
    "de varios pasos en Wikipedia (escribe un query, hace clic en buscar, espera el "
    "artículo, lo lee, hace un assert y toma un screenshot) a través de su tool wrapper "
    "**chat_agent_playwrighter**. "
    "PRECONDICIONES: marca SÓLO la casilla **Multi-Turn** antes de enviar (ACPX "
    "NO es necesario). Playwright debe estar instalado (`pip install playwright && "
    "playwright install`). La demo usa headless=false para que VEAS cómo el browser "
    "llena el formulario, hace clic y navega, y hold_open_seconds=10 para que siga "
    "visible 10 segundos antes de cerrarse. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; "
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,#3D1766 0%,#D90368 50%,#0FA3B1 100%);color:#ffffff;font-family:Inter,Segoe UI,sans-serif;text-align:center;'><h2 "
    "style='margin:0;letter-spacing:2px;color:#ffffff;'>&#127760; WIZARD DEL BROWSER &#127760;</h2><div "
    "style='opacity:.92;margin-top:4px;color:#ffffff;'>Tlamatini Playwrighter &mdash; un browser real busca en Wikipedia paso a paso</div></div>. "
    "\n\n"
    "Paso 1: llama a **chat_agent_playwrighter** con start_url='https://www.wikipedia.org' "
    "y headless=false y hold_open_seconds=10 y "
    "steps_json='[{\"action\":\"fill\",\"selector\":\"#searchInput\",\"value\":\"Nahuatl\"},{\"action\":\"click\",\"selector\":\"button[type=submit]\"},{\"action\":\"wait_for\",\"selector\":\"#firstHeading\"},{\"action\":\"extract_text\",\"selector\":\"#firstHeading\",\"name\":\"article_title\"},{\"action\":\"extract_text\",\"selector\":\"#mw-content-text "
    "p"
    "\""
    ",\"name\":\"first_paragraph\"},{\"action\":\"assert_text\",\"selector\":\"#firstHeading\",\"contains\":\"Nahuatl\"},{\"action\":\"screenshot\",\"path\":\"C:/Temp/wikipedia_wizard.png\",\"full_page\":false}]'. "
    "\n"
    "\nPaso "
    "2"
    ": analiza el resultado de la ejecución y captura los campos promovidos status, final_url, "
    "steps_run, assert_result, además de los valores extraídos 'article_title' y "
    "'first_paragraph' y el path del screenshot. \n\nPaso "
    "3"
    ": muestra un MARCADOR DE PASOS &mdash; una fila de tres chips HTML con la forma <span "
    "style='display:inline-block;padding:8px "
    "16px;margin:3px;border-radius:10px;font-weight:800;background:CHIP_BG;color:#ffffff;'>LABEL</span>: un chip 'status: "
    "<status>' (CHIP_BG #16a34a si es ok, si no #dc2626), un chip 'assert: "
    "<assert_result>' (CHIP_BG #16a34a si es pass, si no #dc2626) y un chip 'pasos: "
    "<steps_run>' (CHIP_BG #2563EB). "
    "\n\n"
    "Paso 4: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Resultado del wizard del browser</strong>' y dos columnas <em>campo</em> / "
    "<em>valor</em>, una fila para cada uno de start_url, final_url, status, steps_run, "
    "assert_result, article_title y el path del screenshot. Deja cada celda del cuerpo con "
    "fondo claro y texto oscuro (background:#ffffff;color:#0f172a; o rayado "
    "#f1f5f9). "
    "\n\n"
    "Paso 5: muestra el first_paragraph extraído dentro de un elemento HTML "
    "<blockquote style='border-left:6px solid #0FA3B1;padding:12px "
    "18px;background:#ffffff;color:#0f172a;border-radius:8px;'>...first_paragraph...</blockquote>. "
    "\n\n"
    "Paso 6: cierra con un banner HTML que reutilice el gradiente del Paso 0 y muestre, en "
    "letras blancas grandes, 'BÚSQUEDA COMPLETA &#10003;' (si status es ok y "
    "assert_result es pass) o, en caso contrario, 'WIZARD: <status>' y, debajo, una "
    "métrica de una línea 'artículo: <article_title> &middot; status: <status> &middot; "
    "assert: <assert_result> &middot; pasos: <steps_run> &middot; screenshot: "
    "C:/Temp/wikipedia_wizard.png'. Termina con END-RESPONSE."
)


# ── Migration ops ──────────────────────────────────────────────────────

_NEW_PROMPTS = (
    (51, WINDOWER_BASIC_DEMO),
    (52, WINDOWER_MEDIUM_DEMO),
    (53, PLAYWRIGHTER_BASIC_DEMO),
    (54, PLAYWRIGHTER_MEDIUM_DEMO),
)


def add_windower_playwrighter_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_windower_playwrighter_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0094_add_chat_agent_windower_tool'),
    ]

    operations = [
        migrations.RunPython(
            add_windower_playwrighter_demo_prompts,
            remove_windower_playwrighter_demo_prompts,
        ),
    ]
