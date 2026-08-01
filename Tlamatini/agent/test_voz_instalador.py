# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""Contratos de la voz mexicana + del instalador/desinstalador en español.

DOS COSAS SE FIJAN AQUÍ:

1. **La copia del instalador no puede separarse del runtime.**
   ``install.py`` corre como su propio ``.exe``, ANTES de que exista la
   instalación, así que NO puede importar ``agent.tts_piper``. Por eso trae
   una copia mínima del contrato (URLs, nombre de la voz, carpeta destino).
   Dos copias del mismo dato es exactamente la clase de bug que se pudre en
   silencio: alguien mueve la URL en un lado y el instalador se queda bajando
   un 404 para siempre. Estas pruebas comparan las dos y truenan si se
   separan.

2. **El instalador NUNCA debe pedir permisos de administrador.**
   Es un requisito duro de Angela. Toda la voz vive dentro de
   ``%LOCALAPPDATA%``, que es del usuario — nada de rutas del sistema, nada
   de elevación.

Y de pasada: los pasos que ve el usuario tienen que seguir en español, y los
pesos de la barra de progreso tienen que sumar 1.0 (si no, la barra miente).

``install.py`` / ``uninstall.py`` NO se pueden importar en el proceso de
pruebas (levantan Tkinter), así que se leen con ``ast`` — el mismo truco que
usa ``test_django_port_config.py`` con ``manage.py``.
"""
from __future__ import annotations

import ast
import os
import re
import unittest

from agent import tts_piper

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_INSTALL = os.path.join(_REPO_ROOT, "install.py")
_UNINSTALL = os.path.join(_REPO_ROOT, "uninstall.py")


def _module_ast(path):
    with open(path, encoding="utf-8") as fh:
        return ast.parse(fh.read())


def _top_level_str(tree, name):
    """Value of a module-level ``NAME = "..."`` (joined implicit concatenation)."""
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    return ast.literal_eval(node.value)
    raise AssertionError(f"{name} no existe al nivel del módulo")


def _steps(tree):
    """The STEPS list of the single GUI class in the module."""
    for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
        for node in ast.walk(cls):
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and tgt.id == "STEPS":
                        return [(e.elts[0].value, e.elts[1].value)
                                for e in node.value.elts]
    raise AssertionError("no encontré STEPS")


def _step_indices(tree):
    """Every literal ``step_idx = N`` assigned inside the GUI class."""
    out = set()
    for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
        for node in ast.walk(cls):
            if (isinstance(node, ast.Assign)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, int)):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and tgt.id == "step_idx":
                        out.add(node.value.value)
    return sorted(out)


class VoiceContractMirrorTests(unittest.TestCase):
    """install.py's inlined copy must agree with agent/tts_piper.py."""

    @classmethod
    def setUpClass(cls):
        cls.tree = _module_ast(_INSTALL)

    def test_piper_engine_url_matches_runtime(self):
        self.assertEqual(_top_level_str(self.tree, "VOICE_PIPER_URL"),
                         tts_piper._PIPER_URL)

    def test_voice_model_url_matches_runtime(self):
        self.assertEqual(_top_level_str(self.tree, "VOICE_MODEL_URL"),
                         tts_piper._VOICE_BASE)

    def test_voice_name_matches_runtime(self):
        self.assertEqual(_top_level_str(self.tree, "VOICE_NAME"),
                         tts_piper._DEFAULT_VOICE)

    def test_install_dir_name_matches_runtime(self):
        self.assertEqual(_top_level_str(self.tree, "VOICE_DIR_NAME"),
                         tts_piper._DIR_NAME)

    def test_voice_is_mexican_spanish(self):
        # Una voz que no sea es_MX reintroduce justo el acento que esto arregla.
        self.assertTrue(tts_piper._DEFAULT_VOICE.startswith("es_MX-"),
                        f"la voz por defecto debe ser es_MX: {tts_piper._DEFAULT_VOICE}")


class NoAdminRequiredTests(unittest.TestCase):
    """The installer must never need elevation — hard requirement."""

    def test_voice_lives_under_localappdata(self):
        root = tts_piper.install_root()
        local = (os.environ.get("LOCALAPPDATA")
                 or os.path.join(os.path.expanduser("~"), "AppData", "Local"))
        self.assertTrue(
            os.path.normcase(root).startswith(os.path.normcase(local)),
            f"la voz debe vivir dentro de %LOCALAPPDATA%, no en {root}")

    def test_status_declares_no_admin(self):
        self.assertIs(tts_piper.status().get("needs_admin"), False)

    def test_installer_never_asks_for_elevation(self):
        with open(_INSTALL, encoding="utf-8") as fh:
            src = fh.read()
        for needle in ("requireAdministrator", "ShellExecuteW", "runas",
                       "IsUserAnAdmin"):
            self.assertNotIn(
                needle, src,
                f"install.py no debe pedir permisos de admin (encontré {needle!r})")


class UninstallRemovesTheVoiceTests(unittest.TestCase):
    """Uninstalling must not orphan ~85 MB under %LOCALAPPDATA%."""

    @classmethod
    def setUpClass(cls):
        with open(_UNINSTALL, encoding="utf-8") as fh:
            cls.src = fh.read()

    def test_has_a_remove_voice_step(self):
        self.assertIn("_remove_voice", self.src)

    def test_removes_only_the_piper_folder(self):
        # Borrar el padre se llevaría de corbata OTRAS cosas del usuario
        # (por ejemplo el PlatformIO de ESP32er/STM32er, que vive en
        # %LOCALAPPDATA%\Tlamatini\platformio).
        # Ojo: hay que partir en "def _remove_voice", NO en "_remove_voice" —
        # la primera ocurrencia es la LLAMADA, no la definición.
        block = self.src.split("def _remove_voice", 1)[1][:1400]
        self.assertIn('"Tlamatini", "piper"', block,
                      "el desinstalador debe borrar SÓLO …\\Tlamatini\\piper")

    def test_voice_removal_cannot_break_the_uninstall(self):
        block = self.src.split("def _remove_voice", 1)[1][:1400]
        self.assertIn("except Exception", block,
                      "borrar la voz tiene que ser fail-open")


class InstallerIsInSpanishTests(unittest.TestCase):
    """The steps the user actually reads must stay in Spanish."""

    # Palabras que delatan que un paso se volvió a escribir en inglés.
    _ENGLISH = re.compile(
        r"\b(creating|copying|removing|extracting|preparing|writing|"
        r"registering|unregistering|refreshing|cleaning|installing|"
        r"skipping|waiting|complete|shortcuts|files|directory)\b", re.I)

    def test_install_steps_are_spanish(self):
        for desc, _w in _steps(_module_ast(_INSTALL)):
            self.assertIsNone(self._ENGLISH.search(desc),
                              f"paso del instalador en inglés: {desc!r}")

    def test_uninstall_steps_are_spanish(self):
        for desc, _w in _steps(_module_ast(_UNINSTALL)):
            self.assertIsNone(self._ENGLISH.search(desc),
                              f"paso del desinstalador en inglés: {desc!r}")

    def test_install_mentions_the_voice_step(self):
        descs = [d for d, _ in _steps(_module_ast(_INSTALL))]
        self.assertTrue(any("voz" in d.lower() for d in descs),
                        f"falta el paso de la voz en el instalador: {descs}")

    def test_uninstall_mentions_the_voice_step(self):
        descs = [d for d, _ in _steps(_module_ast(_UNINSTALL))]
        self.assertTrue(any("voz" in d.lower() for d in descs),
                        f"falta el paso de la voz en el desinstalador: {descs}")


class ProgressWeightsTests(unittest.TestCase):
    """A progress bar whose weights don't sum to 1.0 lies to the user."""

    def test_install_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(w for _d, w in _steps(_module_ast(_INSTALL))),
                               1.0, places=9)

    def test_uninstall_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(w for _d, w in _steps(_module_ast(_UNINSTALL))),
                               1.0, places=9)

    def test_install_runs_every_declared_step(self):
        tree = _module_ast(_INSTALL)
        self.assertEqual(_step_indices(tree), list(range(len(_steps(tree)))),
                         "un paso declarado en STEPS no se ejecuta (o al revés)")

    def test_uninstall_runs_every_declared_step(self):
        tree = _module_ast(_UNINSTALL)
        self.assertEqual(_step_indices(tree), list(range(len(_steps(tree)))),
                         "un paso declarado en STEPS no se ejecuta (o al revés)")


class SynthesisFailsQuietTests(unittest.TestCase):
    """Silence beats an English accent — the whole point of this feature."""

    def test_empty_text_is_not_an_error(self):
        wav, state = tts_piper.synthesize("   ")
        self.assertEqual(state, "empty")
        self.assertEqual(wav, b"")

    def test_missing_voice_reports_not_ready_instead_of_raising(self):
        wav, state = tts_piper.synthesize("hola", voice="no-existe-esta-voz")
        self.assertEqual(state, "not_ready")
        self.assertEqual(wav, b"")

    def test_classifiers_never_raise(self):
        # Fail-open: pase lo que pase, nada de excepciones hacia el llamador.
        self.assertIsInstance(tts_piper.is_ready("lo-que-sea"), bool)
        self.assertIsInstance(tts_piper.status("lo-que-sea"), dict)


if __name__ == "__main__":
    unittest.main()
