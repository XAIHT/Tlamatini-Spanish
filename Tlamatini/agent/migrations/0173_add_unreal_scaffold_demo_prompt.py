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


# Catalog-of-prompts SCAFFOLD: lets a user create a BRAND-NEW Unreal Engine 5.8
# C++ project — fully wired with the UnrealMCP editor plugin and ready to open in
# Visual Studio 2026 — by filling ONLY two [[ ... ]] markers: the project NAME and
# the DIRECTORY it goes in. Tlamatini (Multi-Turn) runs the deterministic scaffolder
# scaffold_unreal_project.py (in the XaihtUnrealEngineMCP repo), which copies +
# renames the MCPGameProject template, sets EngineAssociation 5.8, auto-discovers
# the UE 5.8 engine, and generates the Visual Studio solution. SAFE for the daily
# chat test: if a marker is unfilled (or the name is not a valid C++ module id) it
# creates NOTHING and just asks the user to fix it. Markers use [[ ]] (no angle
# brackets) so an HTML card preview can't eat them.
#
# Preconditions (documented in the prompt body): the user has Unreal Engine 5.8 and
# Visual Studio 2026 (with the C++ / Game-dev workload) installed. The scaffolder is
# registry-independent (it finds UE 5.8 on disk), so it works even when 5.8 is not
# registered as an engine association.
DEMO = (
    "Tlamatini, SCAFFOLD A NEW UNREAL ENGINE 5.8 C++ PROJECT para mí, listo para abrir en "
    "Visual Studio 2026 con el plugin UnrealMCP ya conectado. Ya llené los dos "
    "campos de abajo — las ÚNICAS dos cosas que necesitas de mí: el NOMBRE del proyecto y el "
    "DIRECTORIO donde debe crearse.\n"
    "\n"
    "PROYECTO UNREAL NUEVO\n"
    "- project name:        [[ ESCRIBE AQUÍ EL NOMBRE DEL PROYECTO, p. ej. MyAwesomeGame — SÓLO letras, dígitos y guiones bajos, sin espacios ni guiones, no debe empezar con un dígito ]]\n"
    "- directory location:  [[ LA CARPETA PADRE DONDE CREARLO, p. ej. C:\\Users\\angel\\Documents\\UnrealProjects ]]\n"
    "\n"
    "PRIMERO, una revisión de seguridad — hazla antes de tocar nada: si CUALQUIERA de las líneas de arriba todavía "
    "muestra un marcador [[ ... ]] (o sea que no la llené), NO crees nada ni ejecutes "
    "nada — sólo dime qué campo llenar y detente. Además, si el nombre del proyecto tiene un "
    "espacio o un guión, o empieza con un dígito, NO continúes — explícame que debe ser un "
    "nombre de módulo C++ de Unreal válido (letras / dígitos / guión bajo, sin dígito inicial) y pídeme "
    "que lo renombre. Continúa sólo cuando AMBOS campos estén llenos AND el nombre sea válido.\n"
    "\n"
    "LUEGO, en Multi-Turn, usando SÓLO tus propios tools (Executer / Gitter / File-Interpreter), "
    "haz exactamente esto, en orden:\n"
    "\n"
    "1) UBICA EL SCAFFOLDER. El scaffolder determinista está en "
    "C:\\Development\\XaihtUnrealEngineMCP\\scaffold_unreal_project.py (su repo también tiene "
    "la plantilla MCPGameProject y el plugin de editor UnrealMCP). Usa Executer para revisar "
    "si ese archivo existe (p. ej. `if exist \"C:\\Development\\XaihtUnrealEngineMCP\\scaffold_unreal_project.py\" (echo FOUND) else (echo MISSING)`). "
    "Si está MISSING, clona primero el repo con Gitter (command='custom', custom_command="
    "'clone https://github.com/XAIHT/XaihtUnrealEngineMCP.git C:\\Development\\XaihtUnrealEngineMCP') "
    "— crea C:\\Development primero si hace falta. NO continúes hasta que el archivo del scaffolder exista.\n"
    "\n"
    "2) CORRE EL SCAFFOLDER (un comando lo hace todo). Usa Executer para correr EXACTAMENTE esto, "
    "sustituyendo mis dos valores y MANTENIENDO las comillas alrededor del directorio (puede contener "
    "spaces):\n"
    "   python \"C:\\Development\\XaihtUnrealEngineMCP\\scaffold_unreal_project.py\" --name <PROJECT NAME> --dest \"<DIRECTORY LOCATION>\"\n"
    "Ese único comando copia la plantilla, renombra cada archivo de módulo y token a mi "
    "nombre de proyecto, empaqueta el plugin UnrealMCP, pone EngineAssociation en 5.8, encuentra solo "
    "mi engine UE 5.8 instalado y GENERA la solución de Visual Studio (.sln). Su línea final de "
    "stdout empieza con `SCAFFOLD_RESULT:` seguido de JSON — LEE ese JSON. Si su "
    "\"ok\" es false, muéstrame el \"error\" tal cual y detente. Si \"ok\" es true, captura "
    "\"project_dir\", \"uproject\" y \"solution\" para el reporte.\n"
    "\n"
    "3) ÁBRELO EN VISUAL STUDIO. Si \"solution\" es un path .sln real, usa Executer para abrirlo "
    "en mi escritorio:\n"
    "   start \"\" \"<solution>\"\n"
    "(eso lanza Visual Studio 2026 sobre el .sln). Si \"solution\" está vacío, NO inventes "
    "uno — muéstrame la nota que el script imprimió bajo \"notes\" y señálame el .uproject "
    "para hacerle clic derecho y elegir 'Generate Visual Studio project files' yo mismo.\n"
    "\n"
    "4) CONFIRMA + INSTRUYE. Muestra un resumen HTML corto y ordenado que presente: la CARPETA del proyecto, el "
    "path del .uproject, el path del .sln y el engine root que se usó. Luego dame estos "
    "pasos siguientes exactos para Visual Studio 2026: (a) pon la configuración en 'Development "
    "Editor' y la plataforma en 'Win64'; (b) build MY PROJECT ONLY, NOT the whole solution "
    "— in Solution Explorer right-click the project named after my game (under the 'Games' "
    "folder) and choose Build; do NOT use 'Build Solution', because a full-solution build "
    "also compiles unrelated engine targets (LiveLinkHub, test harnesses, etc.) that fail "
    "for reasons that have nothing to do with my game and just clutter the Error List with "
    "red herrings. This first project build compiles the UnrealMCP plugin and takes several "
    "minutes; (c) press F5 (or Ctrl+F5) to launch the "
    "Unreal Editor con mi proyecto. Agrega esta nota tal cual: una vez que el editor está corriendo, el "
    "plugin UnrealMCP incluido inicia AUTOMÁTICAMENTE su listener TCP en 127.0.0.1:55557 (es "
    "un UEditorSubsystem cuyo Initialize() inicia el servidor), así que tú — Tlamatini — puedes "
    "manejar de inmediato el editor en vivo con el tool chat_agent_unrealer; no hay un paso extra "
    "de 'start server'.\n"
    "\n"
    "NO intentes compilar ni lanzar el engine tú misma desde el chat (un build completo del editor "
    "es largo y pertenece a Visual Studio). Tu trabajo en este prompt es PRODUCIR el "
    "proyecto listo para abrir y listo para compilar y entregármelo en Visual Studio 2026.\n"
    "\n"
    "Marca SÓLO la casilla Multi-Turn. Termina con END-RESPONSE."
)


def add_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    if Prompt.objects.filter(promptContent=DEMO).exists():
        return
    next_id = (Prompt.objects.order_by('-idPrompt').values_list('idPrompt', flat=True).first() or 0) + 1
    Prompt.objects.update_or_create(
        idPrompt=next_id,
        defaults={'promptName': f'prompt-{next_id}', 'promptContent': DEMO},
    )


def remove_demo_prompt(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')
    Prompt.objects.filter(promptContent=DEMO).delete()


class Migration(migrations.Migration):
    dependencies = [('agent', '0172_add_nmapper_demo_prompts')]
    operations = [migrations.RunPython(add_demo_prompt, remove_demo_prompt)]
