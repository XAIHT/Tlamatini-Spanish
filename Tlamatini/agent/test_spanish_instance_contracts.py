# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Spanish catalog, runtime identity and real parameter-parser regressions.

No agent is launched and no installed database, account or service is changed.
"""
import json
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.apps import apps
from django.conf import settings
from django.db import connection
from django.test import SimpleTestCase, TestCase

from agent.rag.config import runtime_instance_context, apply_self_modify_switch


class SpanishInstanceIdentityTests(SimpleTestCase):
    def decode(self, text):
        return json.loads(text[text.index('{'):text.rindex('}') + 1])

    def test_source_uses_own_interpreter_and_custom_cli_port(self):
        cfg = {'django_port': 9052, 'mcp_system_server_port': 9752,
               'mcp_files_search_server_port': 51052, 'api_key': 'SECRET_MUST_NOT_LEAK'}
        with patch('sys.frozen', False, create=True), \
             patch('sys.executable', 'C:/Spanish/python/python.exe'), \
             patch('sys.argv', ['manage.py', 'runserver', '127.0.0.1:10052']):
            text = runtime_instance_context('C:/Spanish/Tlamatini/agent', cfg)
        data = self.decode(text)
        self.assertEqual(data['runtime'], 'SOURCE')
        self.assertEqual(data['django_port'], 10052)
        self.assertEqual(data['mcp_system_server_port'], 9752)
        self.assertEqual(data['mcp_files_search_server_port'], 51052)
        self.assertEqual(Path(data['management_argv'][0]), Path('C:/Spanish/python/python.exe'))
        self.assertEqual(Path(data['management_argv'][1]), Path('C:/Spanish/Tlamatini/manage.py'))
        self.assertEqual(Path(data['application_root']), Path('C:/Spanish'))
        self.assertNotIn('SECRET_MUST_NOT_LEAK', text)

    def test_frozen_ignores_english_environment_and_file_presence(self):
        with patch('sys.frozen', True, create=True), \
             patch('sys.executable', 'C:/Spanish/Tlamatini-Spanish.exe'), \
             patch('sys.argv', ['Tlamatini-Spanish.exe']), \
             patch.dict('os.environ', {'TLAMATINI_TEMP': 'C:/English/Temp', 'CONFIG_PATH': 'C:/English/config.json'}), \
             patch('os.path.isfile', return_value=True):
            data = self.decode(runtime_instance_context('C:/Spanish', {}))
        self.assertEqual(data['runtime'], 'FROZEN')
        self.assertEqual(len(data['management_argv']), 1)
        self.assertEqual(Path(data['config_path']), Path('C:/Spanish/config.json'))
        self.assertEqual(data['django_port'], 8052)
        self.assertEqual(data['mcp_system_server_port'], 8752)
        self.assertEqual(data['mcp_files_search_server_port'], 50052)
        self.assertNotIn('English', json.dumps(data))

    def test_source_is_not_frozen_just_because_an_executable_exists(self):
        with patch('sys.frozen', False, create=True), patch('os.path.isfile', return_value=True):
            data = self.decode(runtime_instance_context('C:/Spanish/Tlamatini/agent', {}))
        self.assertEqual(data['runtime'], 'SOURCE')
        self.assertEqual(len(data['management_argv']), 2)

    def test_invalid_ports_are_not_sent_as_commands(self):
        data = self.decode(runtime_instance_context(config={
            'django_port': '8052 & echo BAD', 'mcp_system_server_port': True,
            'mcp_files_search_server_port': 70000}))
        self.assertIsNone(data['django_port'])
        self.assertIsNone(data['mcp_system_server_port'])
        self.assertIsNone(data['mcp_files_search_server_port'])

    def test_identity_survives_self_modify_off_and_compact(self):
        from agent.mcp_agent import _build_system_prompt, _build_compact_system_prompt
        initial = runtime_instance_context(config={})
        self.assertIn('<instancia_tlamatini_spanish>', apply_self_modify_switch(initial, False))
        full = _build_system_prompt('BASE\n' + initial, [], self_knowledge=False,
                                    step_by_step_enabled=True)
        compact, _ = _build_compact_system_prompt('BASE\n' + initial, [], budget_chars=100,
                                                  step_by_step_enabled=True)
        for result in (full, compact):
            self.assertEqual(result.count('<instancia_tlamatini_spanish>'), 1)
            self.assertIn('Tlamatini-Spanish', result)
            self.assertIn('management_argv', result)
            self.assertIn('HECHO', result)
            self.assertIn('SIN VENTANA', result)
        # Full prompts are used as format templates; literal JSON/path braces survive.
        full.format(input='LISTO')

    def test_spanish_cookies_do_not_share_english_cookie_names(self):
        self.assertEqual(settings.SESSION_COOKIE_NAME, 'tlm_session_es_mx')
        self.assertEqual(settings.CSRF_COOKIE_NAME, 'tlm_csrf_es_mx')
        self.assertNotEqual(settings.CSRF_COOKIE_NAME, 'csrftoken')

    def test_csrf_accepts_spanish_cookie_with_english_cookie_present(self):
        from django.http import HttpResponse
        from django.middleware.csrf import CsrfViewMiddleware, _get_new_csrf_string
        from django.test import RequestFactory
        spanish, english = _get_new_csrf_string(), _get_new_csrf_string()
        for supplied, accepted in ((spanish, True), (english, False)):
            request = RequestFactory().post('/agent/test/', HTTP_X_CSRFTOKEN=supplied)
            request.COOKIES = {settings.CSRF_COOKIE_NAME: spanish, 'csrftoken': english}
            middleware = CsrfViewMiddleware(lambda req: HttpResponse('ok'))
            middleware.process_request(request)
            response = middleware.process_view(request, lambda req: HttpResponse('ok'), (), {})
            self.assertEqual(response is None, accepted)

    def test_all_browser_cookie_readers_use_the_spanish_cookie(self):
        scripts = Path(__file__).parent/'static/agent/js'
        names = ('agent_page_editing.js','external_mcps_dialog.js','agent_page_canvas.js',
                 'acp-session.js','agent_page_state.js','chat_page_runtime_poller.js',
                 'contacts_dialog.js','skills_dialog.js','model_brain_tuning.js',
                 'file_drop_router.js','shared-runtime-dialogs.js','voice_runtime.js')
        for name in names:
            with self.subTest(script=name):
                source = (scripts/name).read_text(encoding='utf-8')
                self.assertIn(settings.CSRF_COOKIE_NAME, source)
                self.assertNotIn('csrftoken', source)
                if name in ('agent_page_editing.js','agent_page_canvas.js'):
                    self.assertIn("slice('tlm_csrf_es_mx='.length)", source)


class SpanishCatalogMigrationTests(TestCase):
    def test_new_migrations_and_regressions_are_in_release_carriage(self):
        root = Path(__file__).resolve().parents[2]
        build = (root/'build.py').read_text(encoding='utf-8')
        snapshot = (root/'copy_source_assets.py').read_text(encoding='utf-8')
        for name in ('0222_repair_prompt_catalog', '0223_spanish_catalog_instance_contracts'):
            self.assertIn('"agent.migrations.'+name+'"', build)
            self.assertIn('"Tlamatini/agent/migrations/'+name+'.py"', snapshot)
        self.assertIn('"Tlamatini/agent/test_spanish_instance_contracts.py"', snapshot)

    def test_every_shipped_card_has_a_scoped_contract_and_spanish_checkpoints(self):
        from agent.models import Prompt
        rows = list(Prompt.objects.order_by('pk'))
        self.assertEqual(len(rows), 127)
        for row in rows:
            with self.subTest(card=row.pk):
                if row.pk != 8:  # Scope inventory is handled by the active guard, not an LLM.
                    self.assertIn('ÁMBITO DE ESTA TARJETA: Tlamatini-Spanish', row.promptContent)
                self.assertNotRegex(row.promptContent, r'\b(?:READY|DONE|NOWINDOW|TESTNOW|SKIP)\b')
                self.assertNotIn('http://localhost:8000', row.promptContent)
                self.assertNotIn('C:/Development/Tlamatini', row.promptContent)
                self.assertNotIn('~/.tlamatini/skill-audit', row.promptContent)
                self.assertNotIn("with filepath", row.promptContent)

    def test_exact_default_repair_preserves_user_text_metadata_and_ids(self):
        from agent.models import Prompt
        migration = import_module('agent.migrations.0223_spanish_catalog_instance_contracts')
        editor = SimpleNamespace(connection=connection)
        migration.reverse(apps, editor)
        custom = Prompt.objects.get(pk=1)
        custom.promptContent += '\nMi instrucción personalizada.'
        custom.hidden = True
        custom.sort_rank = 777
        custom.save()
        before = list(Prompt.objects.order_by('pk').values('idPrompt','promptName','category','sort_rank','hidden'))
        migration.repair(apps, editor)
        once = list(Prompt.objects.order_by('pk').values())
        migration.repair(apps, editor)
        self.assertEqual(once, list(Prompt.objects.order_by('pk').values()))
        self.assertEqual(before, list(Prompt.objects.order_by('pk').values('idPrompt','promptName','category','sort_rank','hidden')))
        custom.refresh_from_db()
        self.assertTrue(custom.promptContent.endswith('Mi instrucción personalizada.'))
        self.assertTrue(custom.hidden)
        migration.reverse(apps, editor)
        custom.refresh_from_db()
        self.assertTrue(custom.promptContent.endswith('Mi instrucción personalizada.'))


class SpanishRealParameterParserTests(SimpleTestCase):
    def test_corrected_requests_resolve_against_actual_agent_yaml(self):
        import yaml
        from agent.tools import _apply_requested_assignments_to_config
        recipes = {
            'telegrammer': "mode='send' and telegram.provider='user' and contact_name='Ejemplo' and message='Hola'",
            'whatsapper': "mode='send' and provider='web' and contact_name='Ejemplo' and message='Hola'",
            'file_creator': "file_path='C:/Spanish/Temp/prueba.txt' and content='Texto' and append=true",
            'file_extractor': "path_filenames='C:/Spanish/Temp/prueba.txt'",
            'notifier': "target.mode='oneshot' and target.search_strings='Usuario listo' and target.outcome_detail='Confirmado' and target.sound_enabled=true",
            'windower': "action='move_resize' and window_title='Tlamatini-Spanish-demo-123.txt - Bloc de notas' and match_mode='exact' and pos_x=220 and pos_y=160 and width=900 and height=600 and activate_after=true",
            'nmapper': "action='scripts' and target='127.0.0.1' and timing='T4' and ports='22,80' and nse_scripts='banner,http-title,ssh2-enum-algos'",
            'discoverer': "tool='naabu' and target='127.0.0.1' and naabu_top_ports='100' and naabu_scan_type='c' and json_output=true",
            'kalier': "action='nmap' and target='127.0.0.1' and scan_type='-sCV' and ports='1-1000' and additional_args='-T4 -Pn'",
            'whisperer': "input_source='mic' and language='es' and engine='faster-whisper' and model='base' and device='auto'",
            'terminater': "action='type' and terminal='t123' and text='Get-Date' and submit=true and wait=true",
            'image_interpreter': "images_pathfilenames='C:/Spanish/Temp/image.png'",
            'instant_messaging_doctor': "platform='both' and mode='diagnose' and retry_send=false",
        }
        for agent, request in recipes.items():
            with self.subTest(agent=agent):
                source = Path(__file__).parent / 'agents' / agent / 'config.yaml'
                config = yaml.safe_load(source.read_text(encoding='utf-8'))
                result, error, changed = _apply_requested_assignments_to_config(config, request)
                self.assertIsNone(error, error)
                self.assertIsNotNone(result)
                self.assertTrue(changed)
