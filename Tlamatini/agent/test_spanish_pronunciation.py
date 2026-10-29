# Tlamatini Author Banner — Angela López Mendoza · @angelahack1
"""Run from a verified visible console; no model, account writes or audio needed."""
from pathlib import Path
from types import SimpleNamespace
import unicodedata
import unittest
from unittest.mock import patch

from agent.agents.talker.spanish_pronunciation import (
    NAME_ACCENTS, accent_name, browser_payload, speech_text,
)
from agent.constants import display_name


class SpanishNameTests(unittest.TestCase):
    def test_angela_stress_and_case(self):
        for raw, expected in [('angela', 'ángela'), ('Angela', 'Ángela'),
                              ('ANGELA', 'ÁNGELA'), ('angéla', 'ángela'),
                              ('Angéla', 'Ángela'), ('Ángela', 'Ángela')]:
            with self.subTest(raw=raw):
                self.assertEqual(speech_text('Hola, ' + raw + '!'), 'Hola, ' + expected + '!')

    def test_catalog_round_trip_and_decomposed_unicode(self):
        for raw, expected in NAME_ACCENTS.items():
            with self.subTest(name=raw):
                self.assertEqual(accent_name(raw.title()), expected)
                self.assertEqual(accent_name(expected), expected)
                self.assertEqual(accent_name(unicodedata.normalize('NFD', expected)), expected)

    def test_mexican_names_and_compounds(self):
        self.assertEqual(speech_text('Jose Maria, Jesus, Sofia, Raul y Angelica Lopez.'),
                         'José María, Jesús, Sofía, Raúl y Angélica López.')
        self.assertEqual(speech_text('Ana, Luis, Guadalupe, Itzel, Ximena, Juan Carlos.'),
                         'Ana, Luis, Guadalupe, Itzel, Ximena, Juan Carlos.')

    def test_explicit_stress_unknown_names_and_common_words(self):
        text = 'Ólga, Josefa, Leonora, Máriam, Ximena: cesar el tránsito en leon.'
        self.assertEqual(speech_text(text), text)
        self.assertEqual(speech_text('Jose', language='en-US'), 'Jose')

    def test_technical_identifiers_remain_verbatim(self):
        text = (r'angela@example.mx https://example.mx/angela C:\Users\angela '
                r'/home/jose ./maria.txt angela.py maria_01 JoseLuis '
                r'@angela `Angela` ```Jose``` <Angela> angela42')
        self.assertEqual(speech_text(text), text)

    def test_account_name_and_login_are_separate(self):
        user = SimpleNamespace(username='angela', first_name='')
        self.assertEqual(display_name(user), 'Ángela')
        self.assertEqual(user.username, 'angela')
        user.first_name = 'María José'
        self.assertEqual(display_name(user), 'María')
        payload = browser_payload(user)
        self.assertEqual(speech_text('Hola angela.', payload['aliases']), 'Hola María.')
        self.assertEqual(user.username, 'angela')

    def test_per_person_override_and_opaque_login(self):
        self.assertEqual(speech_text('Hola user_2024.', {'user_2024': 'María José'}),
                         'Hola María José.')
        self.assertEqual(speech_text('Miriam y Jose', {'Miriam': 'Miriam', 'Jose': 'Jose'}),
                         'Miriam y Jose')
        self.assertEqual(browser_payload(None)['display_name'], '')

    def test_username_validator_accepts_accents(self):
        from django.contrib.auth.validators import UnicodeUsernameValidator
        for name in ('ángela', 'Ángela', 'josé', 'maría.garcía'):
            UnicodeUsernameValidator()(name)

    def test_safe_json_and_all_speech_templates(self):
        from django.template import Context, Engine
        payload = browser_payload(SimpleNamespace(username='test', first_name='</script>'))
        html = Engine().from_string('{{ p|json_script:"tlm-speech-pronunciation" }}').render(Context({'p': payload}))
        self.assertNotIn('</script></script>', html)
        self.assertIn('\\u003C/script\\u003E', html)
        root = Path(__file__).parent
        for name in ('agent_page', 'agentic_control_panel', 'prompt_flow_panel'):
            template = (root / 'templates/agent' / (name + '.html')).read_text(encoding='utf-8')
            self.assertLess(template.index('tlm-speech-pronunciation'), template.index('js/voice_runtime.js'))


class TalkerSpanishNamesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from agent.test_talker_agent import _load_talker_module
        cls.talker = _load_talker_module()

    def test_real_orpheus_payload_uses_accents_without_fake_language_tag(self):
        from agent.test_talker_agent import _FakeResp, _ndjson
        config = {'voice': 'tara', 'model': 'legraphista/Orpheus:3b-ft-q8', 'language': 'es-MX'}
        prompt = self.talker.build_orpheus_prompt(config, 'Hola Angela, Jose y Sofia.')
        self.assertEqual(prompt, 'tara: Hola Ángela, José y Sofía.')
        with patch.object(self.talker.urllib.request, 'urlopen', return_value=_FakeResp(_ndjson({'response': '', 'done': True}))) as call:
            self.talker.query_ollama_tts(config, prompt)
        import json
        payload = json.loads(call.call_args.args[0].data)
        self.assertIn('Ángela, José y Sofía', payload['prompt'])
        self.assertNotIn('<es-MX>', payload['prompt'])

    def test_every_orpheus_voice_gets_the_same_name_correction(self):
        voices = set(self.talker._FEMALE_VOICES) - self.talker._PIPER_FEMALE_VOICES
        self.assertEqual(voices, {'tara', 'leah', 'jess', 'mia', 'zoe'})
        for voice in voices:
            for spelling in ('angela', 'Angela', 'angéla', 'Angéla', 'Ángela'):
                with self.subTest(voice=voice, name=spelling):
                    prompt = self.talker.build_orpheus_prompt(
                        {'voice': voice, 'model': 'legraphista/Orpheus:3b-ft-q8', 'language': 'es'}, spelling)
                    self.assertEqual(prompt, voice + ': ' + accent_name(spelling))

    def test_piper_receives_same_normalized_text_without_mutating_input(self):
        config = {'input_text': 'Hola Angela y Jose.', 'tts_engine': 'piper',
                  'voice': 'es_MX-claude-high', 'language': 'es'}
        with patch.object(self.talker, 'synthesize_piper', return_value={'status': 'saved'}) as synth:
            self.talker.synthesize(config)
        self.assertEqual(synth.call_args.args[1], 'Hola Ángela y José.')
        self.assertEqual(config['input_text'], 'Hola Angela y Jose.')

    def test_piper_child_reads_utf8_even_when_parent_uses_windows_ansi(self):
        import os
        import tempfile
        import wave
        root = Path(__file__).resolve().parents[2]
        def run(argv, **kwargs):
            self.assertEqual(kwargs['input'].decode('utf-8'), 'Hola Ángela, José y Raúl.')
            self.assertEqual(kwargs['env']['PYTHONIOENCODING'], 'utf-8')
            self.assertEqual(kwargs['env']['PYTHONUTF8'], '1')
            with wave.open(argv[-1], 'wb') as output:
                output.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
                output.writeframes(b'\x00\x00' * 22050)
            return SimpleNamespace(returncode=0, stderr=b'')
        with tempfile.TemporaryDirectory(dir=root / 'Temp') as folder:
            config = {'tts_engine': 'piper', 'voice': 'es_MX-claude-high',
                      'input_text': 'Hola Angela, Jose y Raul.', 'language': 'es',
                      'output_dir': folder, 'play_audio': False}
            with patch.dict(os.environ, {'PYTHONIOENCODING': 'cp1252', 'PYTHONUTF8': '0'}), \
                    patch.object(self.talker, '_ensure_piper_module', return_value=True), \
                    patch.object(self.talker, '_ensure_piper_voice', return_value=str(Path(folder) / 'voice.onnx')), \
                    patch.object(self.talker.subprocess, 'run', side_effect=run):
                result = self.talker.synthesize(config)
                self.assertEqual(result['status'], 'saved')
                self.assertEqual(os.environ['PYTHONIOENCODING'], 'cp1252')
                self.assertEqual(os.environ['PYTHONUTF8'], '0')

    def test_custom_model_and_explicit_english_keep_their_contract(self):
        self.assertEqual(self.talker.build_orpheus_prompt(
            {'voice': 'tara', 'model': 'custom', 'language': 'es'}, 'Angela'), 'tara <es>: Ángela')
        self.assertEqual(self.talker.build_orpheus_prompt(
            {'voice': 'tara', 'language': 'en'}, 'Angela'), 'tara: Angela')

    def test_pool_copy_carries_standalone_lexicon(self):
        import importlib.util
        import shutil
        import tempfile
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(dir=root / 'Temp') as folder:
            copied = Path(shutil.copy(Path(__file__).parent / 'agents/talker/spanish_pronunciation.py', folder))
            spec = importlib.util.spec_from_file_location('copied_pronunciation', copied)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertEqual(module.speech_text('Angela'), 'Ángela')
