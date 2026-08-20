# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""LA VOZ DE TLAMATINI: FEMENINA SIEMPRE, ESPAÑOL LATINO SIEMPRE.

Regla de Angela, absoluta y sin excepciones: **UNA VOZ MASCULINA ESTÁ
PROHIBIDA EN TODAS PARTES**. Tlamatini es mujer. Cuando no hay una voz
femenina disponible, la única alternativa aceptable es EL SILENCIO — nunca
un hombre, nunca un acento inglés leyendo español.

Hay TRES caminos por los que sale voz en la edición en español, y este
archivo vigila los tres, porque cerrar dos de tres no sirve de nada:

  1. NAVEGADOR  — ``static/agent/js/avatar.js`` (speechSynthesis del browser)
  2. SERVIDOR   — ``agent/tts_piper.py`` (Piper, voz mexicana es_MX)
  3. GPU / LLM  — ``agents/talker/talker.py`` (Ollama + Orpheus)

EL HOYO QUE ESTE ARCHIVO EXISTE PARA IMPEDIR
--------------------------------------------
``femaleVoices()`` terminaba con ``if(!fem.length) fem=pool.slice();`` — es
decir, si ningún nombre coincidía con el patrón femenino devolvía el pool
COMPLETO, voces masculinas incluidas. En una máquina cuyas voces en español
son todas masculinas, Tlamatini hablaba con voz de HOMBRE. Silenciosamente,
sin error, sin aviso.

Los otros dos caminos ya se negaban correctamente (Talker lanza
``MaleVoiceForbiddenError`` y cierra el proceso; Piper fija una voz
``es_MX`` femenina), así que el navegador era la única puerta abierta.

Las pruebas leen los ARCHIVOS FUENTE, no ejecutan JavaScript: lo que se
vigila es el contrato escrito, que es lo que se rompe en un refactor.
"""

import os
import re
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))
_JS = os.path.join(_AQUI, 'static', 'agent', 'js')


def _leer(*partes):
    ruta = os.path.join(_AQUI, *partes)
    with open(ruta, 'r', encoding='utf-8') as fh:
        return fh.read()


def _codigo_js(src):
    """El JS SIN sus comentarios de línea.

    Necesario porque estas pruebas buscan patrones que los propios
    comentarios CITAN. La primera versión de `test_no_hay_regreso_al_pool_
    completo` fallaba contra un archivo perfectamente correcto: el comentario
    que explica el hoyo escribe `fem=pool.slice()` textualmente, y la prueba
    se encontraba a sí misma. Una prueba que no distingue el código de la
    prosa que lo describe no vigila nada.
    """
    fuera = []
    for linea in src.splitlines():
        limpia = linea.strip()
        if limpia.startswith('//'):
            continue
        fuera.append(linea)
    return '\n'.join(fuera)


class VozDelNavegadorTests(unittest.TestCase):
    """avatar.js — el camino que tenía el hoyo."""

    def setUp(self):
        self.src = _leer('static', 'agent', 'js', 'avatar.js')

    def test_no_hay_regreso_al_pool_completo(self):
        """⛔ EL HOYO: devolver el pool entero admite voces masculinas."""
        codigo = _codigo_js(self.src).replace(' ', '')
        self.assertNotIn(
            'fem=pool.slice()', codigo,
            "femaleVoices() volvió a caer al pool COMPLETO. Esa rama deja "
            "pasar voces MASCULINAS cuando ningún nombre coincide con el "
            "patrón femenino. Debe devolver VACÍO: sin voz femenina, "
            "Tlamatini se queda CALLADA.")
        self.assertNotIn(
            'fem=pool.concat()', codigo,
            'Volvió a aparecer un regreso al pool completo, con otro nombre.')

    def test_existe_el_patron_masculino_y_se_aplica(self):
        self.assertIn('MALE_RE', self.src,
                      'Desapareció el patrón de nombres masculinos.')
        self.assertIn('!MALE_RE.test', self.src,
                      'MALE_RE ya no se usa para EXCLUIR voces.')

    def test_el_patron_masculino_cubre_las_voces_de_windows(self):
        """David / Mark son las voces masculinas que Windows sí trae."""
        # Se busca la LÍNEA de la declaración y se usa entera: intentar
        # recortar el interior del literal /(...)/i con otra expresión
        # regular es frágil (el patrón trae \b, | y acentos), y lo único
        # que importa es que esos nombres sigan reconociéndose ahí.
        #
        # ⚠️ `'MALE_RE' in linea` TAMBIÉN casa con `FEMALE_RE`: el nombre del
        # patrón femenino CONTIENE al masculino como subcadena. Sin excluir
        # FEMALE_RE esta prueba leía la línea equivocada (la de las voces de
        # mujer) y fallaba contra un archivo correcto.
        patron = ''
        for linea in self.src.splitlines():
            limpia = linea.strip()
            if limpia.startswith('//') or 'FEMALE_RE' in linea:
                continue
            if 'MALE_RE' in linea and '=' in linea:
                patron = linea.lower()
                break
        self.assertTrue(patron, 'No se pudo leer la declaración de MALE_RE.')
        for nombre in ('david', 'mark', 'diego', 'jorge', 'pablo'):
            self.assertIn(nombre, patron,
                          f'"{nombre}" ya no se reconoce como voz masculina.')

    def test_el_espanol_latino_va_primero(self):
        """es-MX antes que cualquier otra cosa; el inglés hasta el final."""
        self.assertIn('es[-_]MX', self.src,
                      'Se perdió la preferencia por español mexicano.')
        pos_mx = self.src.find('es[-_]MX')
        pos_en = self.src.find('^en(-|_|$)')
        if pos_en != -1:
            self.assertLess(pos_mx, pos_en,
                            'El inglés quedó ANTES que el español mexicano.')


class VozDelServidorPiperTests(unittest.TestCase):
    """tts_piper.py — la voz mexicana propia."""

    def setUp(self):
        self.src = _leer('tts_piper.py')

    def test_la_voz_por_defecto_es_mexicana(self):
        match = re.search(r'_DEFAULT_VOICE\s*=\s*["\']([^"\']+)["\']', self.src)
        self.assertIsNotNone(match, 'No se encontró _DEFAULT_VOICE.')
        voz = match.group(1)
        self.assertTrue(voz.startswith('es_MX'),
                        f'La voz por defecto "{voz}" no es mexicana (es_MX).')

    def test_el_modelo_se_baja_del_directorio_es_mx(self):
        self.assertIn('es/es_MX/', self.src,
                      'La URL del modelo ya no apunta al directorio es_MX.')

    def test_se_documenta_que_la_voz_es_femenina(self):
        self.assertIn('female', self.src.lower(),
                      'Se perdió la constancia de que la voz es femenina.')


class VozDeLaGpuTalkerTests(unittest.TestCase):
    """talker.py — Ollama/Orpheus. Ya se negaba; que siga negándose."""

    def setUp(self):
        self.src = _leer('agents', 'talker', 'talker.py')
        self.cfg = _leer('agents', 'talker', 'config.yaml')

    def test_la_voz_masculina_es_un_error_fatal(self):
        self.assertIn('class MaleVoiceForbiddenError', self.src,
                      'Desapareció la excepción que prohíbe la voz masculina.')
        self.assertIn('raise MaleVoiceForbiddenError', self.src,
                      'Ya nadie LANZA MaleVoiceForbiddenError.')

    def test_nunca_se_sustituye_por_una_voz_femenina(self):
        """Negarse es correcto; cambiar la voz a escondidas NO lo es."""
        self.assertIn('never substitute', self.src.lower().replace('-', ' '),
                      'Se perdió el contrato de "refuse, never substitute".')

    def test_el_idioma_configurado_es_espanol(self):
        match = re.search(r'^language:\s*["\']([^"\']*)["\']', self.cfg,
                          re.MULTILINE)
        self.assertIsNotNone(match, 'No se encontró `language` en config.yaml.')
        self.assertEqual(
            match.group(1), 'es',
            'La edición en ESPAÑOL tenía el Talker configurado en otro idioma. '
            'Le decía al modelo que hablara en inglés dentro de un producto '
            'en español.')

    def test_la_voz_por_defecto_es_femenina(self):
        match = re.search(r'^voice:\s*["\']([^"\']*)["\']', self.cfg,
                          re.MULTILINE)
        self.assertIsNotNone(match, 'No se encontró `voice` en config.yaml.')
        self.assertIn(match.group(1).lower(),
                      ('tara', 'leah', 'jess', 'mia', 'zoe'),
                      f'"{match.group(1)}" no está en las voces FEMENINAS '
                      f'permitidas.')


class NingunCaminoQuedaAbiertoTests(unittest.TestCase):
    """Los tres caminos a la vez: ninguno puede sonar como hombre."""

    def test_los_tres_archivos_existen(self):
        for partes in (('static', 'agent', 'js', 'avatar.js'),
                       ('tts_piper.py',),
                       ('agents', 'talker', 'talker.py')):
            self.assertTrue(os.path.isfile(os.path.join(_AQUI, *partes)),
                            f'Falta {partes[-1]}: un camino de voz sin vigilar.')

    def test_el_silencio_es_la_alternativa_documentada(self):
        """Sin voz femenina => callada. Nunca un hombre, nunca inglés."""
        avatar = _leer('static', 'agent', 'js', 'avatar.js')
        piper = _leer('tts_piper.py')
        self.assertIn('PROHIBIDA', avatar,
                      'avatar.js perdió la nota de que lo masculino está '
                      'prohibido.')
        self.assertIn('NOTHING rather than', piper,
                      'tts_piper.py perdió la regla de callarse antes que '
                      'leer español con voz inglesa.')


if __name__ == '__main__':
    unittest.main()
