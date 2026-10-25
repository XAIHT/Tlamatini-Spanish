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
Seed two ADVANCED demo prompts that go beyond the basic/medium Windower &
Playwrighter showcases (0095) by conducting several desktop-UI / browser agents
together in one flow — far more *visual*: a real window is staged, clicked into
with the mouse and typed into with the keyboard before it dances around the
screen; a real browser types a query key-by-key, submits with the Enter key,
scrolls with the keyboard and captures three staged screenshots.

    55  DESKTOP DIRECTOR    Windower+Mouser+Keyboarder   advanced
                            (stage -> mouse-click-to-focus -> live keyboard typing
                             -> tile/maximize/restore/pin choreography -> list -> close)
    56  BROWSER VIRTUOSO    Playwrighter                 advanced
                            (visible per-key typing -> Enter-key submit -> article
                             -> attribute extract -> keyboard scroll -> 3 screenshots)

Placement (append, no renumber)
-------------------------------
The catalog dropdown (static/agent/js/tools_dialog.js::loadPrompts) enumerates
promptName 'prompt-1', 'prompt-2', ... and BREAKS at the first missing slot, so
the catalog must stay a contiguous, gap-free 'prompt-1..N'. Slots 1-54 are fully
occupied (0095 appended the four desktop/browser demos at 51-54). These two demos
therefore APPEND at the tail (55-56) — contiguity is preserved with no shift of
any existing prompt, so no other Prompt row's idPrompt/promptName changes.
Reverse simply deletes 55-56. (MAX_PROMPTS=100, so there is ample room.)

Like 0095 (and unlike the 0090 Reviewer/Analyzer skill demos), these drive the
wrapped chat_agent_* tools, which are NOT behind the ACPX/Skill surface — so each
prompt reminds the user to tick ONLY the **Multi-Turn** checkbox (ACPX is not
required). DESKTOP DIRECTOR is Windows-only (Win32 + PyAutoGUI). BROWSER VIRTUOSO
needs Playwright installed (`pip install playwright && playwright install`) and
uses headless=false so the browser is visible.
"""
from django.db import migrations


# ── Demo-prompt content ────────────────────────────────────────────────

WINDOWER_DIRECTOR_DEMO = (
    "Tlamatini, ejecuta la demo **DIRECTOR DEL ESCRITORIO**, por favor &mdash; una muestra completa "
    "y totalmente visible que dirige a TODO el trío de UI del escritorio en un solo flow: "
    "el agent **Windower** acomoda y mueve una ventana real, el agent **Mouser** "
    "hace clic dentro para colocar el cursor y el agent **Keyboarder** escribe en vivo "
    "texto en ella &mdash; luego Windower hace bailar la ventana, ya llena de texto, "
    "por la pantalla. Todo se controla desde el chat con los tools "
    "**chat_agent_windower** / **chat_agent_mouser** / **chat_agent_keyboarder** "
    "(wrappers). "
    "PRECONDICIONES: marca SÓLO la casilla **Multi-Turn** en la barra de herramientas antes "
    "de enviar (ACPX NO es necesario). Sólo para Windows (Windower usa la API "
    "Win32, Mouser usa PyAutoGUI). Haz cada operación de ventana como una llamada SEPARADA "
    "a chat_agent_windower y haz una pausa breve entre ellas para que cada movimiento "
    "sea "
    "visible. \n\n"
    "Paso 0: abre con un banner HTML "
    "&mdash; <div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,#0B1E3A 0%,#1E6FB8 38%,#22D3EE 72%,#A7F3D0 100%);color:#ffffff;font-family:Inter,Segoe UI,sans-serif;text-align:center;'><h2 "
    "style='margin:0;letter-spacing:2px;color:#ffffff;'>&#127916; DIRECTOR DEL ESCRITORIO "
    "&#127916;</h2><div style='opacity:.92;margin-top:4px;color:#ffffff;'>Tlamatini &mdash; ventana, mouse y teclado, dirigidos como uno solo</div></div>. "
    "\n\n"
    "Paso 1: abre Notepad para que haya una ventana que dirigir &mdash; "
    "llama a **chat_agent_executer** con script='notepad' y non_blocking=true y "
    "luego confirma que la ventana está arriba con **chat_agent_window_present** "
    "(window_title='Notepad'). "
    "\n\n"
    "Paso 2: COLOCA la ventana al centro de la pantalla &mdash; llama a **chat_agent_windower** "
    "con action='move_resize' y window_title='Notepad' y pos_x=360 "
    "y pos_y=180 y width=900 y height=560 y activate_after=true. Captura los campos "
    "promovidos state/left/top/width/height. "
    "\n\n"
    "Paso 3: enfoca el área de edición con el MOUSE &mdash; llama a "
    "**chat_agent_mouser** con movement_type='click_at_window' y "
    "window_title='Notepad' y window_anchor='center' y button_click='left'. Captura "
    "los campos promovidos located_via, clicked, end_posx, end_posy (esto coloca "
    "el cursor de texto para que el siguiente paso escriba en la ventana correcta). \n\nPaso "
    "4"
    ": escribe en vivo con el TECLADO &mdash; llama a **chat_agent_keyboarder** con "
    "input_sequence=\"'TLAMATINI', enter, 'in ixtli, in yollotl', enter, 'the "
    "face, the heart -- that is wisdom', enter, enter, 'window, mouse and "
    "keyboard in concert.'\" y stride_delay=70 (el ritmo deliberado hace que las teclas "
    "se vean conforme van cayendo). \n\nPaso "
    "5"
    ": ahora haz BAILAR la ventana llena de texto &mdash; UNA llamada a chat_agent_windower por "
    "movimiento, cada una con window_title='Notepad' y activate_after=true, y "
    "captura los campos promovidos state/left/top/width/height después de cada llamada: (a) "
    "action='arrange' y arrange_mode='left' (se ajusta a la mitad izquierda); (b) "
    "action='arrange' y arrange_mode='right' (se ajusta a la mitad derecha); (c) "
    "action='arrange' y arrange_mode='top-right' (cuadrante superior derecho); (d) "
    "action='maximize' (llena la pantalla); (e) "
    "action='restore' (regresa al tamaño normal); (f) "
    "action='topmost' (la fija siempre encima). \n\nPaso "
    "6"
    ": enumera todo el escritorio con **chat_agent_windower** action='list' (deja "
    "window_title vacío) y captura match_count (el número de ventanas "
    "abiertas). \n\nPaso "
    "7"
    ": muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Rastro del director del escritorio</strong>' y con las columnas <em>paso</em>, "
    "<em>agent</em>, <em>action</em>, <em>detalle</em>, <em>state</em>, "
    "<em>left</em>, <em>top</em>, <em>width</em>, <em>height</em> &mdash; una fila para "
    "el clic de enfoque de Mouser (agent 'Mouser', action 'click_at_window', detalle "
    "'located_via=<located_via>, en (<end_posx>,<end_posy>)'), una fila para lo "
    "que escribió Keyboarder (agent 'Keyboarder', action 'type', detalle '4 líneas, ritmo de "
    "70ms') y luego una fila para CADA uno de los seis movimientos de ventana (a)..(f) (agent "
    "'Windower') con los campos promovidos de esa llamada. Deja cada celda del cuerpo con "
    "fondo claro y texto oscuro (background:#ffffff;color:#0f172a; o rayado "
    "#f1f5f9). "
    "\n\n"
    "Paso 8: limpia &mdash; **chat_agent_windower** action='untopmost' y "
    "window_title='Notepad' (la desfija) y luego **chat_agent_windower** action='close' y "
    "window_title='Notepad'. Si aparece un diálogo 'Save changes?', descártalo SIN "
    "guardar con **chat_agent_keyboarder** input_sequence=\"alt+n\". "
    "\n\n"
    "Paso 9: cierra con un banner HTML que reutilice el gradiente del Paso 0 y muestre, en "
    "letras blancas grandes, 'ESCRITORIO DIRIGIDO &#10003;' y, debajo, una métrica de una "
    "línea 'movimientos hechos: 6 &middot; ventanas abiertas vistas: <match_count> &middot; "
    "estado final: <state> &middot; clic del cursor: <clicked>'. Termina con END-RESPONSE."
)

PLAYWRIGHTER_VIRTUOSO_DEMO = (
    "Tlamatini, ejecuta la demo **VIRTUOSO DEL BROWSER**, por favor &mdash; una muestra completa y "
    "totalmente visible del agent **Playwrighter** manejando un browser REAL "
    "como mecanógrafo experto: escribe un query de búsqueda carácter por carácter (tú "
    "VES caer cada tecla), lo envía con la TECLA Enter (no con un clic), sigue el "
    "resultado hasta el artículo, lo lee, saca un atributo de la página, baja hasta el "
    "final con el teclado, hace asserts y toma tres screenshots escalonados "
    "&mdash; todo a través de su tool wrapper **chat_agent_playwrighter**. "
    "PRECONDICIONES: marca SÓLO la casilla **Multi-Turn** antes de enviar (ACPX "
    "NO es necesario). Playwright debe estar instalado (`pip install playwright && "
    "playwright install`). La demo usa headless=false para que VEAS cómo el browser "
    "escribe y navega, y hold_open_seconds=12 para que siga visible 12 "
    "segundos antes de cerrarse. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; "
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,#3D1766 0%,#D90368 38%,#0FA3B1 72%,#6EE7B7 100%);color:#ffffff;font-family:Inter,Segoe UI,sans-serif;text-align:center;'><h2 "
    "style='margin:0;letter-spacing:2px;color:#ffffff;'>&#127908; VIRTUOSO DEL BROWSER &#127908;</h2><div "
    "style='opacity:.92;margin-top:4px;color:#ffffff;'>Tlamatini Playwrighter &mdash; un browser real escribe, envía y lee, tecla por tecla</div></div>. "
    "\n\n"
    "Paso 1: llama a **chat_agent_playwrighter** con start_url='https://www.wikipedia.org' "
    "y headless=false y hold_open_seconds=12 y "
    "steps_json='[{\"action\":\"wait_for\",\"selector\":\"#searchInput\"},{\"action\":\"type\",\"selector\":\"#searchInput\",\"text\":\"Nahuatl\",\"delay\":140},{\"action\":\"screenshot\",\"path\":\"C:/Temp/virtuoso_1_typed.png\"},{\"action\":\"press\",\"key\":\"Enter\",\"selector\":\"#searchInput\"},{\"action\":\"wait_for\",\"selector\":\"#firstHeading\"},{\"action\":\"extract_text\",\"selector\":\"#firstHeading\",\"name\":\"article_title\"},{\"action\":\"extract_text\",\"selector\":\"#mw-content-text "
    "p"
    "\""
    ","
    "\""
    "n"
    "ame\":\"lead_paragraph\"},{\"action\":\"extract_attr\",\"selector\":\"link[rel=canonical]\",\"attr\":\"href\",\"name\":\"canonical_url\"},{\"action\":\"assert_text\",\"selector\":\"#firstHeading\",\"contains\":\"Nahuatl\"},{\"action\":\"assert_visible\",\"selector\":\"#bodyContent\"},{\"action\":\"screenshot\",\"path\":\"C:/Temp/virtuoso_2_article.png\",\"full_page\":false},{\"action\":\"press\",\"key\":\"End\"},{\"action\":\"wait\",\"ms\":800},{\"action\":\"screenshot\",\"path\":\"C:/Temp/virtuoso_3_bottom.png\",\"full_page\":true}]'. "
    "\n"
    "\n"
    "P"
    "a"
    "s"
    "o"
    " "
    "2"
    ": analiza el resultado de la ejecución y captura los campos promovidos status, "
    "final_url, steps_run, assert_result, además de los valores extraídos "
    "'article_title', 'lead_paragraph' y 'canonical_url' y los paths de los tres "
    "screenshots. "
    "\n\n"
    "Paso 3: muestra un MARCADOR DE PASOS &mdash; una fila de chips HTML con la forma <span "
    "style='display:inline-block;padding:8px "
    "16px;margin:3px;border-radius:10px;font-weight:800;background:CHIP_BG;color:#ffffff;'>LABEL</span>: un chip 'status: "
    "<status>' (CHIP_BG #16a34a si es ok, si no #dc2626), un chip 'assert: "
    "<assert_result>' (CHIP_BG #16a34a si es pass, si no #dc2626), un chip 'pasos: "
    "<steps_run>' (CHIP_BG #2563EB) y un chip 'screenshots: 3' (CHIP_BG #0FA3B1). "
    "\n\n"
    "Paso 4: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Resultado del virtuoso del browser</strong>' y dos columnas <em>campo</em> / "
    "<em>valor</em>, una fila para cada uno de start_url, final_url, status, steps_run, "
    "assert_result, article_title, canonical_url, y una fila por cada path de screenshot "
    "(virtuoso_1_typed / virtuoso_2_article / virtuoso_3_bottom). Deja cada celda del "
    "cuerpo con fondo claro y texto oscuro (background:#ffffff;color:#0f172a; o "
    "rayado #f1f5f9). "
    "\n\n"
    "Paso 5: muestra el lead_paragraph extraído dentro de un elemento HTML "
    "<blockquote style='border-left:6px solid #0FA3B1;padding:12px "
    "18px;background:#ffffff;color:#0f172a;border-radius:8px;'>...lead_paragraph...</blockquote>. "
    "\n\n"
    "Paso 6: cierra con un banner HTML que reutilice el gradiente del Paso 0 y muestre, "
    "en letras blancas grandes, 'ACTUACIÓN VIRTUOSA &#10003;' (si status es ok y "
    "assert_result es pass) o, en caso contrario, 'VIRTUOSO: <status>' y, debajo, una "
    "métrica de una línea 'artículo: <article_title> &middot; status: <status> &middot; "
    "assert: <assert_result> &middot; pasos: <steps_run> &middot; screenshots: 3'. Termina "
    "con END-RESPONSE."
)


# ── Migration ops ──────────────────────────────────────────────────────

_NEW_PROMPTS = (
    (55, WINDOWER_DIRECTOR_DEMO),
    (56, PLAYWRIGHTER_VIRTUOSO_DEMO),
)


def add_director_virtuoso_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    for prompt_id, content in _NEW_PROMPTS:
        Prompt.objects.update_or_create(
            idPrompt=prompt_id,
            defaults={'promptName': f'prompt-{prompt_id}', 'promptContent': content},
        )


def remove_director_virtuoso_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(idPrompt__in=[pid for pid, _ in _NEW_PROMPTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0095_add_windower_playwrighter_demo_prompts'),
    ]

    operations = [
        migrations.RunPython(
            add_director_virtuoso_demo_prompts,
            remove_director_virtuoso_demo_prompts,
        ),
    ]
