# Tlamatini Author Banner — Angela López Mendoza · @angelahack1
"""Offline prompt-shape regressions; no model or filesystem access is invoked."""
import ast
from pathlib import Path
import re
import unittest
from unittest.mock import patch


class PromptShapeSentenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).parent / 'rag/interface.py'
        tree = ast.parse(source.read_text(encoding='utf-8'))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'is_valid_prompt')
        namespace = {'re': re, 'nltk': None}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), namespace)
        cls.validate = staticmethod(namespace['is_valid_prompt'])

    def test_context_before_clear_command(self):
        for text in (
            'This is a chat release check. Do not use tools. Reply with the exact token TLAMATINI-CHAT-42.',
            'The file failed yesterday. Please explain the error.',
            'Some background first.\nWrite a short summary.',
            'Reply with the result of 16 + 26.',
            'Please reply with the result.',
        ):
            with self.subTest(text=text):
                self.assertTrue(self.validate(text))

    def test_spanish_text_transformations_without_english_pos_tagger(self):
        for text in (
            'Devuelve la segunda palabra de: rojo verde azul',
            'Por favor, devuélveme el resultado.',
            'Devolver la palabra central de uno dos tres.',
            'Extrae la primera palabra de este texto.',
            'Selecciona el valor mayor entre dos y siete.',
            'Ordena banana, apple y cherry.',
            'Invierte las letras de abcdef.',
            'Reemplaza los guiones por barras.',
            'Separa las palabras con comas.',
            'Une norte y estrella con un guion bajo.',
            'Repite el token indicado.',
            'Resuelve la operación de suma.',
        ):
            with self.subTest(text=text):
                self.assertTrue(self.validate(text))

    def test_labeled_spanish_request_reaches_shape_admission(self):
        text = ('Aceptación ES016. Devuelve la segunda palabra de: rojo verde azul '
                'Responde solo con el resultado solicitado. '
                'No uses herramientas, comandos, archivos ni servicios externos.')
        self.assertTrue(self.validate(text))
        self.assertTrue(self.validate('Contexto previo. Devuelve únicamente la palabra central.'))

    def test_incomplete_fragments_still_need_clarification(self):
        for text in ('', '   ', 'please', 'README.md located in the project home, then summary', 'Some background. Nothing else.', None):
            with self.subTest(text=text):
                self.assertFalse(self.validate(text))

    def test_existing_questions_and_commands_remain_valid(self):
        for text in ('What is Tlamatini?', 'Show me the current time', 'Please summarize this text', 'Could you explain this?'):
            with self.subTest(text=text):
                self.assertTrue(self.validate(text))


class LiteralReplyAccessTests(unittest.TestCase):
    def test_literal_reply_never_asks_the_file_intent_classifier(self):
        from agent.rag import interface
        with patch.object(interface, '_indirect_file_access_prompt', side_effect=AssertionError('Unexpected classifier call')):
            for text in ('Reply with exactly SCHEDULED_OK and no other text.',
                         'Please respond with only "READY" and nothing else.',
                         'Answer with RELEASE-42.'):
                with self.subTest(text=text):
                    self.assertIsNone(interface._validate_accesses_in_prompt(text))

    def test_paths_and_additional_instructions_are_not_literal_replies(self):
        from agent.rag import interface
        for text in ('Reply with exactly C:\\private\\data.txt',
                     'Reply with exactly ../secret',
                     'Reply with exactly README.md',
                     'Reply with exactly OK. Then read the config file.',
                     'Reply with exactly OK and delete temp files',
                     'Reply with exactly "OK"\nRun the script', None):
            with self.subTest(text=text):
                self.assertFalse(interface._is_literal_reply_request(text))

    def test_ambiguous_local_access_still_uses_fail_closed_classification(self):
        from agent.rag import interface
        with patch.object(interface, '_indirect_file_access_prompt', return_value=True) as classifier:
            self.assertIsNotNone(interface._validate_accesses_in_prompt('Show me the logs from the server folder.'))
            classifier.assert_called_once()
