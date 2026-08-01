# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""Tests for the create-superuser wizard catalog prompt (migration 0145).

The wizard is INSERTED at catalog slot #1 (prompt-1) by 0145, which shifts every
pre-existing prompt up by one. These tests pin the contract the frontend relies
on: the wizard is genuinely first, the catalog stays gap-free, and the prompt
carries the exact keywords the catalog classifier (static/agent/js/tools_dialog.js
::classifyPromptModes) keys on to badge it Multi-turn + Step-by-Step + Exec-report
(and NOT ACPX) and to run createsuperuser in both frozen and source modes.
"""
from django.test import TestCase

from agent.models import Prompt


class CreateSuperuserWizardPromptTests(TestCase):
    def _wizard(self):
        return Prompt.objects.get(idPrompt=1)

    def test_wizard_is_catalog_slot_one(self):
        p = self._wizard()
        self.assertEqual(p.promptName, 'prompt-1')
        self.assertIn('createsuperuser', p.promptContent)
        # Angela's opening phrasing + the placeholder the user edits before sending.
        # The catalog moved to the standardized parameter grammar (migrations
        # 0182-0185): `[[ ... ]]` marks a value the USER types. The old
        # `----<set name here>----` marker no longer exists anywhere.
        # Edición en español (migración 0191): el catálogo se tradujo, así que
        # se acepta cualquiera de los dos idiomas. Lo que NO cambia y sí se
        # exige es la GRAMÁTICA de parámetros: `[[ ]]` = lo llena la usuaria.
        self.assertTrue(
            '[[ TYPE THE USERNAME HERE' in p.promptContent
            or '[[ ESCRIBE AQUÍ EL NOMBRE DE USUARIO' in p.promptContent,
            'falta el marcador [[ ]] del nombre de usuario',
        )
        # `{{ ... }}` marks a value TLAMATINI fills at runtime (the standardized
        # grammar); the old `<USERNAME>` angle form is now a REPORT slot only.
        self.assertTrue(
            'treat that reply as {{ the username }} and continue to Step 1' in p.promptContent
            or 'toma esa respuesta como {{ the username }} y sigue al Paso 1' in p.promptContent,
            'falta el marcador {{ the username }} de runtime',
        )

    def test_catalog_is_contiguous_and_wizard_first(self):
        ids = sorted(Prompt.objects.values_list('idPrompt', flat=True))
        self.assertEqual(ids[0], 1, 'the wizard must be the very first catalog prompt')
        gaps = [n for n in range(ids[0], ids[-1] + 1) if n not in ids]
        self.assertEqual(gaps, [], 'the catalog must stay gap-free for the dropdown')

    def test_classifier_keywords_present(self):
        # Mirrors tools_dialog.js::classifyPromptModes — these substrings are what
        # make the card badge Multi-turn + Step-by-Step + Exec-report and tick the
        # three toolbar checkboxes on click.
        c = self._wizard().promptContent
        self.assertIn('Multi-Turn', c)            # -> Multi-turn (+ Exec-report)
        self.assertIn('chat_agent_executer', c)   # -> Multi-turn (operator tool)
        # -> Step-by-Step (hyphenated form + intent word; the spaced "step by step"
        #    used elsewhere in the catalog must NOT trip the same detector).
        #    Edición en español: la casilla se llama "Paso-a-Paso" y el detector
        #    de tools_dialog.js L132-137 YA es bilingüe. Este patrón refleja las
        #    dos ramas reales del clasificador — si lo cambias, cambia también
        #    classifyPromptModes en el MISMO paso o la card deja de marcar la
        #    casilla sola.
        self.assertRegex(
            c,
            r'[Ss]tep-by-[Ss]tep\s+(?:setup|wizard|checkbox)'
            r'|(?:asistente|casilla|modo|gu[íi]a)\s+(?:de\s+)?[Pp]aso-a-[Pp]aso'
            r'|(?:activ|marc|habilit)\w*[^.\n]{0,80}[Pp]aso-a-[Pp]aso',
        )
        # Must NOT look like an ACPX prompt.
        self.assertNotIn('acp_spawn', c)
        self.assertNotIn('invoke_skill', c)

    def test_runs_in_both_frozen_and_source(self):
        c = self._wizard().promptContent
        self.assertIn('Tlamatini.exe" createsuperuser', c)      # frozen branch
        self.assertIn('python manage.py createsuperuser', c)    # source branch
        self.assertIn('execute_forked_window=true', c)          # visible console
        self.assertIn('non_blocking=true', c)                   # detached, returns
        # restart guidance — "restart" en inglés, "reinicia" en español
        low = c.lower()
        self.assertTrue('restart' in low or 'reinicia' in low,
                        'el wizard debe decirle cómo reiniciar Tlamatini')
