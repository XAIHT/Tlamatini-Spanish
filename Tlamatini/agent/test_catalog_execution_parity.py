# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Migration, toolbar and orchestration parity; not a substitute for visible runs."""
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

from django.apps import apps
from django.db import connection
from django.test import TestCase, SimpleTestCase

from agent.models import Prompt
from agent.mcp_agent import _STEP_BY_STEP_SYSTEM_GUIDANCE


class CatalogExecutionParityTests(TestCase):
    def test_all_127_shipped_cards_have_the_forward_repair(self):
        migration = import_module('agent.migrations.0224_restore_catalog_execution_parity')
        followup = import_module('agent.migrations.0225_align_catalog_execution_modes')
        latest = {number: new for number, old, new in followup.REPAIRS}
        model_upgrade = import_module('agent.migrations.0226_replace_mistral_large3')
        self.assertEqual(len(migration.REPAIRS), 127)
        for number, old, new in migration.REPAIRS:
            with self.subTest(card=number):
                expected = latest.get(number, new)
                for retired, replacement in model_upgrade.MODEL_REPLACEMENTS.items():
                    expected = expected.replace(retired, replacement)
                self.assertEqual(Prompt.objects.get(pk=number).promptContent, expected)
                self.assertIn('aunque una lista agrupe varias llamadas', old)
                self.assertNotIn('aunque una lista agrupe varias llamadas', new)
                self.assertIn('No añadas confirmaciones entre llamadas', new)

    def test_repair_preserves_customizations_metadata_and_other_rows(self):
        migration = import_module('agent.migrations.0224_restore_catalog_execution_parity')
        editor = SimpleNamespace(connection=connection)
        migration.reverse(apps, editor)
        customized = Prompt.objects.get(pk=1)
        customized.promptContent += '\nMi instrucción propia.'
        customized.hidden = True
        customized.sort_rank = 999
        customized.save()
        metadata = list(Prompt.objects.order_by('pk').values('idPrompt', 'promptName', 'category', 'sort_rank', 'hidden'))
        migration.repair(apps, editor)
        once = list(Prompt.objects.order_by('pk').values())
        migration.repair(apps, editor)
        self.assertEqual(once, list(Prompt.objects.order_by('pk').values()))
        self.assertEqual(metadata, list(Prompt.objects.order_by('pk').values('idPrompt', 'promptName', 'category', 'sort_rank', 'hidden')))
        customized.refresh_from_db()
        self.assertTrue(customized.promptContent.endswith('Mi instrucción propia.'))
        migration.reverse(apps, editor)
        customized.refresh_from_db()
        self.assertTrue(customized.promptContent.endswith('Mi instrucción propia.'))

    def test_wizard_opens_before_waiting_for_console_input(self):
        text = Prompt.objects.get(pk=1).promptContent
        self.assertIn('abre createsuperuser EN ESTE MISMO TURNO', text)
        self.assertIn('sin pausa independiente', text)
        self.assertNotIn('ESPERA LISTO', text)
        self.assertIn('execute_forked_window=true', text)
        self.assertIn('non_blocking=true', text)
        self.assertIn('Si falta la identidad, DETENTE', text)
        self.assertIn('Si falta el nombre, pide solo ese dato', text)
        self.assertIn('La contraseña no va en el chat', text)
        self.assertIn('Un lanzamiento no acredita la creación', text)

    def test_forward_migration_is_carried_by_both_release_paths(self):
        root = Path(__file__).resolve().parents[2]
        self.assertIn('agent.migrations.0224_restore_catalog_execution_parity', (root/'build.py').read_text(encoding='utf-8'))
        source = (root/'copy_source_assets.py').read_text(encoding='utf-8')
        self.assertIn('Tlamatini/agent/migrations/0224_restore_catalog_execution_parity.py', source)
        self.assertIn('Tlamatini/agent/test_catalog_execution_parity.py', source)


class ExecutionBoundaryTests(SimpleTestCase):
    def test_system_does_not_split_english_mcp_sequence_into_extra_turns(self):
        text = _STEP_BY_STEP_SYSTEM_GUIDANCE
        self.assertNotIn('divide external_mcp_import', text)
        self.assertIn('sin exigir LISTO entre esas llamadas', text)
        self.assertIn('Un paso puede requerir varias llamadas', text)
        self.assertIn('no llames más herramientas hasta la respuesta solicitada', text)
        self.assertIn('no afirmes', text.replace('ni afirmes', 'no afirmes'))
