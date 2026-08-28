"""Guardas de PARIDAD FUNCIONAL con el arbol ingles (2026-08-27).

Tlamatini-Spanish es una EDICION, no una copia con retraso: cuando el arbol
ingles arregla algo, esta edicion tiene que traerlo tambien. Este archivo fija
las tres cosas que el barrido del 2026-08-27 encontro DESFASADAS, para que no
se vuelvan a caer sin que nadie se entere:

  1. dialog_policy.js USABA `bindSeal` y `sealedElements` sin DECLARARLOS.
     El export final (`bindSeal: bindSeal`) corre al cargar el archivo, asi que
     tronaba con ReferenceError y `window.TlamatiniDialogPolicy` NUNCA se
     asignaba: la pagina de chat en espanol se quedaba SIN politica de Escape,
     SIN tlmAlert y SIN tlmConfirm. Un archivo que no carga no avisa: se ve
     igualito, nomas ya no hace nada.

  2. El actualizador se sellaba pero NO se amarraba (faltaba la llamada
     `bindSeal(overlay, 'update')`), asi que Escape lo cerraba a media
     actualizacion — justo lo que el sello existe para impedir.

  3. response_parser.py no traia el arreglo de perdida-de-datos del 2026-08-15:
     un diagrama podia llegar al navegador como el texto pelon "DGRM_0".

Ninguna de estas guardas puede pasar en vacio: si el simbolo o el arreglo no
esta, la prueba se pone roja y dice exactamente que archivo abrir.
"""

import os
import re

from django.test import SimpleTestCase

_AQUI = os.path.dirname(os.path.abspath(__file__))
_JS_FUENTE = os.path.join(_AQUI, 'static', 'agent', 'js')
_JS_SERVIDO = os.path.join(os.path.dirname(_AQUI), 'staticfiles', 'agent', 'js')


def _leer(*partes):
    with open(os.path.join(*partes), encoding='utf-8', errors='replace') as fh:
        return fh.read()


class PoliticaDeDialogosSeCargaTests(SimpleTestCase):
    """dialog_policy.js debe DECLARAR todo lo que usa, o no carga."""

    def test_bindSeal_esta_declarado_no_solo_usado(self):
        src = _leer(_JS_FUENTE, 'dialog_policy.js')
        self.assertIn(
            'function bindSeal(', src,
            'dialog_policy.js exporta `bindSeal` pero no lo define: el objeto '
            'window.TlamatiniDialogPolicy truena al cargar y la pagina se '
            'queda sin politica de dialogos.')

    def test_sealedElements_esta_declarado_no_solo_usado(self):
        src = _leer(_JS_FUENTE, 'dialog_policy.js')
        self.assertIn(
            'var sealedElements', src,
            'dialog_policy.js hace `delete sealedElements[key]` sin declarar '
            'sealedElements: ReferenceError en cuanto alguien des-sella.')

    def test_todo_identificador_del_export_existe_en_el_archivo(self):
        """El export corre al cargar: un nombre suelto ahi mata el modulo."""
        src = _leer(_JS_FUENTE, 'dialog_policy.js')
        bloque = src[src.index('window.TlamatiniDialogPolicy = {'):]
        bloque = bloque[:bloque.index('};') + 2]
        # Toma el lado DERECHO de cada `clave: valor,` del export.
        valores = re.findall(r':\s*([A-Za-z_$][\w$]*)\s*[,}]', bloque)
        self.assertTrue(valores, 'no se pudo leer el bloque de export')
        for nombre in sorted(set(valores)):
            declarado = (
                ('function %s(' % nombre) in src
                or ('var %s' % nombre) in src
                or ('function %s (' % nombre) in src
            )
            self.assertTrue(
                declarado,
                'dialog_policy.js exporta `%s` pero no lo declara en ningun '
                'lado: el modulo entero truena al cargarse.' % nombre)

    def test_el_actualizador_se_amarra_al_sello(self):
        src = _leer(_JS_FUENTE, 'agent_page_dialogs.js')
        self.assertIn(
            "bindSeal(overlay, 'update')", src,
            'OpenCheckUpdatesDialog sella pero no AMARRA el overlay: un '
            'dialogo sellado pero no amarrado se sigue cerrando con Escape a '
            'media actualizacion.')


class CopiasServidasAlDiaTests(SimpleTestCase):
    """Lo que se sirve es staticfiles/, no la fuente: no basta con arreglar."""

    ARCHIVOS = ('dialog_policy.js', 'agent_page_dialogs.js')

    def test_las_copias_recolectadas_traen_lo_mismo_que_la_fuente(self):
        for nombre in self.ARCHIVOS:
            servido = os.path.join(_JS_SERVIDO, nombre)
            if not os.path.isfile(servido):
                continue  # arbol sin recolectar todavia: no es un fallo
            self.assertEqual(
                _leer(_JS_FUENTE, nombre), _leer(_JS_SERVIDO, nombre),
                'staticfiles/%s quedo atras de la fuente. Corre '
                '`python manage.py collectstatic --noinput`.' % nombre)


class DiagramasNoSePierdenTests(SimpleTestCase):
    """El arreglo de perdida-de-datos del 2026-08-15, portado el 2026-08-27."""

    CASOS = {
        'marcador absorbido': (
            'BEGIN-DIAGRAM\n+---------+\n| inside  |\nEND-DIAGRAM\n'
            '| attached |\n+----------+\n'),
        'diagrama y regla markdown': (
            '+-----+\n| uno |\n+-----+\n\n---\n\ntexto despues\n'),
        'dos bloques separados': (
            'BEGIN-DIAGRAM\n+--a--+\nEND-DIAGRAM\n\n'
            'BEGIN-DIAGRAM\n+--b--+\nEND-DIAGRAM\n'),
        'dos diagramas con regla cada uno': (
            'BEGIN-DIAGRAM\n+--a--+\n| a  |\nEND-DIAGRAM\n\n---\n\n'
            'BEGIN-DIAGRAM\n+--b--+\n| b  |\nEND-DIAGRAM\n\n---\n'),
    }

    def _tubo(self, crudo):
        from agent.services.response_parser import (
            _restore_diagram_placeholders,
            _wrap_diagram_blocks,
        )
        envuelto, marcadores = _wrap_diagram_blocks(crudo)
        return _restore_diagram_placeholders(envuelto, marcadores)

    def test_ningun_marcador_llega_al_navegador(self):
        for nombre, crudo in self.CASOS.items():
            with self.subTest(caso=nombre):
                salida = self._tubo(crudo)
                self.assertNotIn(
                    'DGRM_', salida,
                    'se fugo un marcador de diagrama al chat (%s)' % nombre)
                self.assertNotIn(
                    chr(0), salida,
                    'se fugo un byte NUL centinela al chat (%s)' % nombre)

    def test_un_bloque_absorbido_no_pierde_su_contenido(self):
        salida = self._tubo(self.CASOS['marcador absorbido'])
        self.assertIn('inside', salida, 'se perdio el arte del bloque explicito')
        self.assertIn('attached', salida, 'se perdio el arte pegado')

    def test_un_marcador_huerfano_se_borra_en_vez_de_publicarse(self):
        from agent.services.response_parser import _restore_diagram_placeholders
        salida = _restore_diagram_placeholders(
            'antes ' + chr(0) + 'DGRM_7' + chr(0) + ' despues', [])
        self.assertNotIn('DGRM_', salida)
        self.assertNotIn(chr(0), salida)

    def test_existen_las_piezas_del_arreglo(self):
        from agent.services import response_parser as rp
        for pieza in ('_is_soft_diagram_line', '_THEMATIC_BREAK_RE',
                      '_DIAGRAM_PLACEHOLDER_CAPTURE_RE', '_PLACEHOLDER_PREFIX'):
            self.assertTrue(
                hasattr(rp, pieza),
                'response_parser.py perdio `%s`: volvio el bug de 2026-08-15 '
                'en el que un diagrama entero salia como el texto "DGRM_0".'
                % pieza)


class McpDoctorConoceElRuntimePrivadoTests(SimpleTestCase):
    """Sin esto el doctor manda a instalar Node que Tlamatini YA instalo."""

    def _fuente(self):
        return _leer(_AQUI, 'agents', 'mcp_doctor', 'mcp_doctor.py')

    def test_busca_el_runtime_propio_antes_que_el_PATH(self):
        src = self._fuente()
        for pieza in ('_tlamatini_runtimes_root', '_tlamatini_runtime_bins',
                      '_MANAGED_TOOLS'):
            self.assertIn(
                'def %s' % pieza if pieza.startswith('_tlamatini') else pieza,
                src,
                'mcp_doctor.py no conoce el runtime privado de Tlamatini (%s): '
                'reporta un npx perfectamente instalado como ausente.' % pieza)

    def test_un_gestor_provisionable_no_cuenta_como_bloqueo(self):
        src = self._fuente()
        self.assertIn(
            'not probe.get("provisionable")', src,
            'mcp_doctor.py marca como BLOQUEO un npx/uvx que Tlamatini se '
            'instala ella sola al activar el servidor.')
