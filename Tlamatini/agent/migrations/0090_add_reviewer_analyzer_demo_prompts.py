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
Seed two fancy, single-skill demo prompts that showcase the v1.4.2
**Reviewer** (code-review) and **Analyzer** (security-audit) agents from the
chat, then place them BEFORE the Multi-Turn sample prompts.

Both agents are canvas-only (no wrapped chat_agent_* tool); their chat-facing
surface is the SKILL.md twins `code-review` and `security-audit`, invoked via
`invoke_skill`. Each demo is therefore a single guided skill call rendered into
a banner + exec-report table + verdict/status banner, matching the fancy
house style of the Unrealer demo (slot 25) that immediately precedes them.

Placement & renumber
--------------------
The catalog dropdown (static/agent/js/tools_dialog.js) enumerates promptName
'prompt-1', 'prompt-2', ... and BREAKS at the first missing slot, so the
catalog must stay a contiguous, gap-free 'prompt-1..N' and its display order is
the numeric suffix. Slots 1-25 are fully occupied (Unrealer owns 25), so to
land the two new demos at 26-27 (right after Unrealer, right before the
Multi-Turn demos) this migration first shifts every existing Prompt with
idPrompt >= 26 UP by +2 -- renumbering BOTH idPrompt and promptName, processed
in collision-safe order -- then writes the two new prompts into the freed
slots. Post-shift catalog map:

    1-20    tiers 1-8 (context Q&A ... project-wide code mod)   (0002)
    21-23   agent control                                       (0062)
    24      telegrammer parametrize                             (0063)
    25      Unrealer end-to-end editor drive                    (0087)
    26      Reviewer / code-review showcase     <-- NEW          (THIS)
    27      Analyzer / security-audit showcase  <-- NEW          (THIS)
    28-30   Multi-Turn demos          (was 26-28)               (0002)
    31-37   simplified ACPX demos     (was 29-35)               (0074)
    38-43   rich-HTML ACPX demos      (was 36-41)               (0072)
    44-50   Gemini-pinned ACPX demos  (was 42-48)               (0073)

Reverse: delete 26-27, then shift idPrompt >= 28 back DOWN by -2, restoring the
pre-migration catalog (contiguous 1..48) exactly.

Note: invoke_skill lives behind the ACPX/Skill tool surface, so both prompts
remind the user to tick BOTH the Multi-Turn and ACPX toolbar checkboxes before
sending.
"""
from django.db import migrations


FIRST_SHIFTED_ID = 26
SHIFT = 2


# ── Demo-prompt content ────────────────────────────────────────────────

REVIEWER_DEMO = (
    "Tlamatini, ejecuta la demo **REVISIÓN DE CÓDIGO BAJO EL REFLECTOR**, por favor &mdash; una muestra vistosa, "
    "de principio a fin, del nuevo agent **Reviewer**, controlado desde el chat a través de "
    "su Skill **code-review** (una revisión de git diff como la de un ingeniero senior, que devuelve un "
    "veredicto más hallazgos anclados a líneas). "
    "PRECONDICIONES (márcalas en la barra de herramientas ANTES de enviar): la casilla **Multi-Turn** "
    "AND la casilla **ACPX** deben estar activadas las dos, porque invoke_skill "
    "vive detrás de la superficie de tools ACPX/Skill; el objetivo debe ser un repositorio "
    "git con al menos un commit previo. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; "
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,#0E7490 0%,#2563EB 33%,#4F46E5 66%,#7C3AED 100%);color:#ffffff;font-family:Inter,Segoe UI,sans-serif;text-align:center;'>"
    "<h2 style='margin:0;letter-spacing:2px;color:#ffffff;'>&#128269; REVISIÓN DE CÓDIGO BAJO EL REFLECTOR &#128269;</h2>"
    "<div style='opacity:.92;margin-top:4px;color:#ffffff;'>Tlamatini Reviewer &mdash; el Skill code-review, veredicto de ingeniero senior</div></div>. "
    "\n\n"
    "Paso 1: llama a **invoke_skill** con skill_name='code-review' y "
    "args_json='{\"repo_path\":\"C:/Development/Tlamatini\",\"diff_ref\":\"HEAD~1\","
    "\"focus\":\"security and correctness regressions\"}'. Si el summary que devuelve "
    "dice que el diff estaba vacío, llámalo una vez más con "
    "args_json='{\"repo_path\":\"C:/Development/Tlamatini\",\"diff_ref\":\"\","
    "\"focus\":\"uncommitted working-tree and staged changes\"}' para que la demo siempre "
    "tenga algo que revisar. "
    "\n\n"
    "Paso 2: analiza el envelope del skill y captura tres cosas: el veredicto "
    "(APPROVE | REQUEST_CHANGES | COMMENT), el array findings (cada uno es "
    "{file, line, severity, category, message, suggestion}) y el summary. "
    "\n\n"
    "Paso 3: muestra un CHIP DE VEREDICTO grande &mdash; un bloque HTML "
    "<div style='display:inline-block;padding:10px 22px;border-radius:999px;"
    "font-weight:800;letter-spacing:1px;color:#ffffff;background:VERDICT_COLOR;'> "
    "que muestre el texto del veredicto, donde VERDICT_COLOR es #16a34a para APPROVE, "
    "#d97706 para COMMENT y #dc2626 para REQUEST_CHANGES. "
    "\n\n"
    "Paso 4: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Hallazgos de la revisión de código</strong>' y con las columnas "
    "<em>archivo</em>, <em>línea</em>, <em>severidad</em>, <em>categoría</em>, "
    "<em>mensaje</em>, <em>sugerencia</em>. Una fila por hallazgo, ordenadas de la más "
    "severa a la menos (critical, luego high, luego medium, luego low y luego nit). Deja "
    "cada celda del cuerpo con fondo claro y texto oscuro "
    "(background:#ffffff;color:#0f172a; o rayado #f1f5f9) y colorea SÓLO la "
    "celda de severidad (critical #fee2e2, high #ffedd5, medium #fef9c3, low/nit "
    "#ecfccb) sin dejar de mantener su texto oscuro. Si el array findings está vacío, muestra "
    "una sola fila de celebración que abarque toda la tabla y diga 'Sin hallazgos "
    "importantes &mdash; el diff está limpio.' "
    "\n\n"
    "Paso 5: muestra el summary del skill dentro de un elemento HTML "
    "<blockquote style='border-left:6px solid #4F46E5;padding:12px 18px;"
    "background:#ffffff;color:#0f172a;border-radius:8px;'>...summary...</blockquote>. "
    "\n\n"
    "Paso 6: cierra con un banner HTML que reutilice el gradiente del Paso 0 y muestre "
    "el veredicto en letras blancas grandes y, debajo, una métrica de una línea "
    "'Veredicto: <verdict> &middot; hallazgos: <N> (critical <c>, high <h>, medium "
    "<m>, low/nit <l>)'. Termina con END-RESPONSE."
)

ANALYZER_DEMO = (
    "Tlamatini, ejecuta la demo **AUDITORÍA DE SEGURIDAD A PLENA LUZ**, por favor &mdash; una "
    "muestra vistosa, de principio a fin, del nuevo agent **Analyzer**, controlado desde el chat "
    "a través de su Skill **security-audit** (SAST determinista + escaneo de secretos + "
    "escaneo de dependencias, sin que el LLM adivine). "
    "PRECONDICIONES (márcalas en la barra de herramientas ANTES de enviar): la casilla **Multi-Turn** "
    "AND la casilla **ACPX** deben estar activadas las dos, porque invoke_skill "
    "vive detrás de la superficie de tools ACPX/Skill. El skill ejecuta los que estén en el PATH de "
    "bandit, semgrep, ruff, eslint, gitleaks y pip-audit &mdash; los que "
    "falten se reportan como huecos de cobertura en lugar de hacer que la ejecución termine en error. "
    "\n\n"
    "Paso 0: abre con un banner HTML &mdash; "
    "<div style='padding:18px;border-radius:14px;background:linear-gradient(135deg,#7F1D1D 0%,#DC2626 33%,#F59E0B 66%,#FACC15 100%);color:#ffffff;font-family:Inter,Segoe UI,sans-serif;text-align:center;'>"
    "<h2 style='margin:0;letter-spacing:2px;color:#ffffff;'>&#128737;&#65039; AUDITORÍA DE SEGURIDAD A PLENA LUZ &#128737;&#65039;</h2>"
    "<div style='opacity:.92;margin-top:4px;color:#ffffff;'>Tlamatini Analyzer &mdash; el Skill security-audit, cada scanner del PATH</div></div>. "
    "\n\n"
    "Paso 1: llama a **invoke_skill** con skill_name='security-audit' y "
    "args_json='{\"path\":\"C:/Development/Tlamatini/Tlamatini/agent\","
    "\"min_severity\":\"low\"}'. "
    "\n\n"
    "Paso 2: analiza el envelope del skill y captura: el array findings (cada uno es "
    "{tool, file, line, severity, rule_id, message}), el objeto severity_counts "
    "({critical, high, medium, low}), el summary y &mdash; a partir del summary "
    "&mdash; qué scanners corrieron de verdad y cuáles no estaban disponibles. "
    "\n\n"
    "Paso 3: muestra un MARCADOR DE SEVERIDAD &mdash; una fila de cuatro chips HTML con la "
    "forma <span style='display:inline-block;padding:8px 16px;margin:3px;"
    "border-radius:10px;font-weight:800;background:CHIP_BG;color:CHIP_FG;'>"
    "<count> <label></span> para critical (CHIP_BG #7F1D1D / CHIP_FG #ffffff), high "
    "(CHIP_BG #DC2626 / CHIP_FG #ffffff), medium (CHIP_BG #F59E0B / CHIP_FG "
    "#0f172a) y low (CHIP_BG #FACC15 / CHIP_FG #0f172a). "
    "\n\n"
    "Paso 4: muestra una tabla HTML con class='exec-report-table' titulada "
    "'<strong>Hallazgos del análisis estático y del escaneo de secretos</strong>' y con las columnas "
    "<em>tool</em>, <em>archivo</em>, <em>línea</em>, <em>severidad</em>, "
    "<em>rule_id</em>, <em>mensaje</em>. Una fila por hallazgo, ordenadas de la más severa "
    "a la menos (critical, luego high, luego medium y luego low). Deja cada celda del cuerpo "
    "con fondo claro y texto oscuro (background:#ffffff;color:#0f172a; o rayado "
    "#f1f5f9) y colorea SÓLO la celda de severidad (critical #fee2e2, high #ffedd5, "
    "medium #fef9c3, low #ecfccb) sin dejar de mantener su texto oscuro. Si el array "
    "findings está vacío, muestra una sola fila de celebración que abarque toda la tabla y diga "
    "'Sin hallazgos en el umbral low o por encima &mdash; escaneo limpio.' "
    "\n\n"
    "Paso 5: muestra el resumen de remediación del skill dentro de un elemento HTML "
    "<blockquote style='border-left:6px solid #DC2626;padding:12px 18px;"
    "background:#ffffff;color:#0f172a;border-radius:8px;'>...summary...</blockquote>, "
    "y debajo una lista HTML <ul> con dos viñetas <li>: 'Scanners ejecutados: <list>' y "
    "'Scanners no disponibles (huecos de cobertura): <list>'. "
    "\n\n"
    "Paso 6: cierra con un banner HTML que reutilice el gradiente del Paso 0 y muestre, "
    "en letras blancas grandes, 'SEGURIDAD: LIMPIO' (si no hay ningún hallazgo) o "
    "'SEGURIDAD: <total> HALLAZGOS' (en caso contrario) y, debajo, una métrica de una línea "
    "'critical <c> &middot; high <h> &middot; medium <m> &middot; low <l> &middot; "
    "escaneado: C:/Development/Tlamatini/Tlamatini/agent'. Termina con END-RESPONSE."
)


# ── Shift helper ───────────────────────────────────────────────────────

def _shift_block(Prompt, threshold, delta):
    """Shift every Prompt with idPrompt >= threshold by `delta`, renumbering
    both idPrompt and promptName. Processed largest-first when moving up and
    smallest-first when moving down so the primary-key reassignment never
    collides with an as-yet-unmoved row."""
    ids = list(
        Prompt.objects.filter(idPrompt__gte=threshold).values_list('idPrompt', flat=True)
    )
    ids.sort(reverse=(delta > 0))
    for old_id in ids:
        new_id = old_id + delta
        Prompt.objects.filter(idPrompt=old_id).update(
            idPrompt=new_id,
            promptName=f'prompt-{new_id}',
        )


# ── Migration ops ──────────────────────────────────────────────────────

def add_reviewer_analyzer_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')

    # 1) make room: 26..N -> 28..(N+2) so the Multi-Turn/ACPX block slides down
    _shift_block(Prompt, FIRST_SHIFTED_ID, SHIFT)

    # 2) seed the two new demos into the freed slots (idempotent on re-run)
    Prompt.objects.update_or_create(
        idPrompt=26,
        defaults={'promptName': 'prompt-26', 'promptContent': REVIEWER_DEMO},
    )
    Prompt.objects.update_or_create(
        idPrompt=27,
        defaults={'promptName': 'prompt-27', 'promptContent': ANALYZER_DEMO},
    )


def remove_reviewer_analyzer_demo_prompts(apps, schema_editor):
    Prompt = apps.get_model('agent', 'Prompt')

    # drop the two new demos, then slide the Multi-Turn/ACPX block back up
    Prompt.objects.filter(idPrompt__in=(26, 27)).delete()
    _shift_block(Prompt, FIRST_SHIFTED_ID + SHIFT, -SHIFT)


class Migration(migrations.Migration):
    dependencies = [
        ('agent', '0089_add_analyzer'),
    ]

    operations = [
        migrations.RunPython(
            add_reviewer_analyzer_demo_prompts,
            remove_reviewer_analyzer_demo_prompts,
        ),
    ]
