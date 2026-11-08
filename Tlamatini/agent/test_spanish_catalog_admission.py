# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Every seeded Spanish catalog card must reach the chain in its browser modes.

Run from a verified visible PowerShell console. No catalog action is executed:
the chain is a recording mock, while catalog migrations, browser classification
and the real request-admission path are exercised together.
"""
import contextlib
from importlib import import_module
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.apps import apps
from django.db import connection
from django.test import SimpleTestCase, TestCase

from agent.models import Prompt
from agent.rag import interface


class SpanishCatalogAdmissionTests(TestCase):
    def test_every_catalog_card_reaches_the_chain_with_its_actual_browser_modes(self):
        rows = list(Prompt.objects.filter(hidden=False).order_by('idPrompt').values(
            'idPrompt', 'promptContent'))
        self.assertTrue(rows)
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node.js is required to verify the real catalog JavaScript')
        script = Path(__file__).parent / 'static/agent/js/tools_dialog.js'
        result = subprocess.run(
            [node, '-e', r"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync(process.argv[1], 'utf8');
const start = source.indexOf('function classifyPromptModes(');
const end = source.indexOf('// ═', source.indexOf('function applyPromptModesToToggles('));
if (start < 0 || end < 0) throw Error('Catalog classifier/toggle functions missing');
const boxes = {};
const sandbox = {document: {getElementById: id => boxes[id]}, Event: class {}};
vm.createContext(sandbox);
vm.runInContext(source.slice(start, end), sandbox);
const rows = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(rows.map(row => {
    for (const id of ['multi-turn-enabled', 'acpx-enabled', 'exec-report-enabled', 'step-by-step-enabled']) {
        boxes[id] = {checked: false, dispatchEvent() {}};
    }
    const modes = sandbox.classifyPromptModes(row.promptContent);
    sandbox.applyPromptModesToToggles(modes);
    return {input: row.promptContent,
        multi_turn_enabled: boxes['multi-turn-enabled'].checked,
        acpx_enabled: boxes['acpx-enabled'].checked,
        exec_report_enabled: boxes['exec-report-enabled'].checked,
        step_by_step_enabled: boxes['step-by-step-enabled'].checked};
})));
""", str(script)],
            input=json.dumps(rows, ensure_ascii=False), text=True, encoding='utf-8',
            capture_output=True, check=True, timeout=30,
        )
        requests = json.loads(result.stdout)
        self.assertEqual(len(requests), len(rows))
        accepted = 0
        for row, request in zip(rows, requests):
            with self.subTest(prompt=row['idPrompt']):
                if row['idPrompt'] == 8:
                    # A directory-scope inventory is deliberately answered from
                    # the active guard without consulting a probabilistic chain.
                    answer = interface.ask_rag(Mock(), request)
                    self.assertIn('Directorios disponibles', answer)
                    accepted += 1
                    continue
                chain = Mock()
                chain.invoke.return_value = 'CATALOG_REACHED_CHAIN'
                # Model-dependent intent classification must not decide whether
                # a built-in, unambiguous sample is accepted. Simulate an outage.
                with patch.object(interface, '_indirect_file_access_prompt', return_value=True), \
                     patch.object(interface, '_acces_aimed_prompt', return_value=True), \
                     contextlib.redirect_stdout(io.StringIO()):
                    answer = interface.ask_rag(chain, request)
                self.assertEqual(answer, 'CATALOG_REACHED_CHAIN', row['promptContent'][:160])
                chain.invoke.assert_called_once()
                payload = chain.invoke.call_args.args[0]
                self.assertEqual(payload['input'], row['promptContent'])
                for key in ('multi_turn_enabled', 'acpx_enabled', 'step_by_step_enabled'):
                    self.assertEqual(payload[key], request[key])
                if row['idPrompt'] in (2, 3, 4, 5, 6, 7, 8, 20, 21, 22):
                    self.assertFalse(request['step_by_step_enabled'],
                                     'The common instance contract must not enable guided mode')
                if row['idPrompt'] in (1, 69, 70, 83, 84, 97, 104, 108, 121, 129):
                    self.assertTrue(request['step_by_step_enabled'])
                if 'Torrenter' in row['promptContent']:
                    self.assertFalse(request['multi_turn_enabled'])
                    self.assertFalse(request['exec_report_enabled'])
                accepted += 1
        print(f'Catalog admission: {accepted}/{len(rows)} samples reached the chain.')

    def test_every_catalog_card_can_be_loaded_by_its_stable_number(self):
        from django.test import RequestFactory
        from agent.views import load_prompt_view
        for row in Prompt.objects.filter(hidden=False):
            with self.subTest(prompt=row.pk):
                response = load_prompt_view(RequestFactory().get('/'), f'prompt-{row.pk}')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content.decode(), row.promptContent)

    def test_catalog_references_only_available_wrapped_tools(self):
        from agent.tools import tool_gate_table
        names = {build().name for _, _, build in tool_gate_table()}
        for row in Prompt.objects.filter(hidden=False):
            with self.subTest(prompt=row.pk):
                referenced = set(re.findall(r'\bchat_agent_\w+', row.promptContent))
                self.assertFalse(referenced - names, sorted(referenced - names))

    def test_window_probes_use_the_real_tool_and_its_title_argument(self):
        rows = Prompt.objects.filter(promptContent__contains='window_present')
        self.assertEqual(rows.count(), 4)
        for row in rows:
            with self.subTest(prompt=row.pk):
                self.assertNotIn('chat_agent_window_present', row.promptContent)
                self.assertRegex(row.promptContent, r'window_present(?:\*\* \(| con )title=')
                # Window-management agents still use their own window_title key.
                self.assertIn("match_mode='exact'", row.promptContent)
                self.assertIn('window_title={{ título COMPLETO devuelto }}', row.promptContent)
                self.assertNotIn('input_sequence="alt+n"', row.promptContent)

    def test_repairs_preserve_custom_edits_and_order_and_are_idempotent(self):
        migration = import_module('agent.migrations.0222_repair_prompt_catalog')
        editor = SimpleNamespace(connection=connection)
        migration.reverse(apps, editor)
        custom = Prompt.objects.create(
            idPrompt=9001, promptName='My customized example',
            promptContent=migration.torrenter.PROMPT + '\nMis instrucciones.',
            category='run_execute', sort_rank=999, hidden=True,
        )
        before = list(Prompt.objects.order_by('pk').values('idPrompt', 'category', 'sort_rank', 'hidden'))
        migration.repair(apps, editor)
        once = list(Prompt.objects.order_by('pk').values())
        migration.repair(apps, editor)
        self.assertEqual(once, list(Prompt.objects.order_by('pk').values()))
        self.assertEqual(before, list(Prompt.objects.order_by('pk').values('idPrompt', 'category', 'sort_rank', 'hidden')))
        custom.refresh_from_db()
        self.assertEqual(custom.promptName, 'My customized example')
        self.assertEqual(custom.promptContent, migration.torrenter.PROMPT + '\nMis instrucciones.')
        self.test_every_catalog_card_can_be_loaded_by_its_stable_number()


class SpanishAdmissionBoundaryTests(SimpleTestCase):
    def test_polite_and_addressed_requests_are_valid_without_english_tokenizer(self):
        with patch.object(interface, 'nltk', None):
            for text in (
                'Tlamatini, por favor, explica el contexto que te di.',
                'Por favor, resume el documento cargado.',
                '¿Cómo funciona este código',
                'Tlamatini: muestra la hora actual.',
                'Tlamatini, please explain this code.',
                'Usa Torrenter para listar mis descargas.',
                'Por favor, utiliza Torrenter para consultar el estado.',
                'Emplea Executer para mostrar la hora.',
            ):
                with self.subTest(text=text):
                    self.assertTrue(interface.is_valid_prompt(text))
            for text in ('Tlamatini,', 'por favor', 'Tlamatini, por favor,', '', None):
                with self.subTest(text=text):
                    self.assertFalse(interface.is_valid_prompt(text))

    def test_spanish_literal_reply_does_not_need_an_intent_model(self):
        with patch.object(interface, '_indirect_file_access_prompt', side_effect=AssertionError('classifier called')):
            for text in ('Responde exactamente LISTO y nada más.',
                         'Por favor, contesta con "OK".', 'Responde sólo CATALOGO_OK.'):
                with self.subTest(text=text):
                    self.assertIsNone(interface._validate_accesses_in_prompt(text))

    def test_literal_reply_does_not_swallow_paths_or_extra_actions(self):
        for text in ('Responde con C:\\privado\\datos.txt', 'Responde con ../secreto',
                     'Responde con README.md', 'Responde con OK y borra los archivos',
                     'Responde con OK. Luego abre el archivo.', 'Responde con "OK"\nEjecuta el script'):
            with self.subTest(text=text):
                self.assertFalse(interface._is_literal_reply_request(text))

    def test_absolute_paths_outside_allowed_scope_still_reject(self):
        with patch.object(interface, 'is_path_allowed', return_value=False), \
             patch.object(interface, '_acces_aimed_prompt', side_effect=AssertionError('classifier called')):
            for text in ('Lee C:\\privado\\datos.txt', 'Por favor, borra C:\\privado\\datos.txt',
                         'Tlamatini, por favor, abre C:\\privado\\datos.txt'):
                with self.subTest(text=text):
                    self.assertEqual(interface._validate_accesses_in_prompt(text), interface.REJECTION_MESSAGE)

    def test_relative_and_ambiguous_local_access_still_reject(self):
        with patch.object(interface, '_indirect_file_access_prompt', return_value=True):
            for text in ('Lee ../privado/datos.txt', 'Abre el archivo de configuración de mi escritorio.',
                         'Muestra los logs de la carpeta del servidor.'):
                with self.subTest(text=text):
                    self.assertIsNotNone(interface._validate_accesses_in_prompt(text))
