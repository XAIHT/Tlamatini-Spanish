# -*- coding: utf-8 -*-
"""Guard: Tlamatini NO se queda muda en su propio idioma.

La regla de oro dice *mejor muda que en ingles*, y esta bien. Pero el
2026-08-26 la PRUEBA de "¿esto es castellano?" era tan estrecha que callaba al
castellano mismo:

    `_MARCAS_ES` traia UNICAMENTE palabras funcion (el, la, de, que, para...).
    Una frase corta de puro contenido no trae ninguna, asi que `hola`,
    `Gracias` y `Hola Angela` no daban marca positiva, se mandaban a traducir,
    y sin Ollama prendido Tlamatini SE QUEDABA CALLADA.

Angela, al ver la tabla: *"so only when there are no accent it will be
muted??? ja ja ja"*. Tenia razon en reirse: la voz mexicana estaba instalada y
lista (`es_MX-claude-high`), y aun asi no decia "hola".

Estas pruebas fijan las DOS direcciones a la vez, porque arreglar una sin
mirar la otra es como se rompio esto en primer lugar:

  * lo que ES castellano SE HABLA (aunque sea corto y sin acentos);
  * lo que ES ingles NO se pronuncia tal cual, jamas.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import tts_piper as tp  # noqa: E402


#: Castellano cotidiano. Ninguna de estas puede quedarse muda.
CASTELLANO = (
    "hola", "Hola", "Hola Angela", "Gracias", "Adios", "Listo",
    "Buenos dias", "Buenas noches", "Archivo guardado", "Carpeta creada",
    "Ayuda", "Mensaje enviado", "Prueba terminada",
    # Por terminacion, que es lo que ninguna lista alcanza a enumerar.
    "configuracion", "guardando", "rapidamente", "seguridad",
    # Con acento y frases largas: lo que ya funcionaba, no se debe romper.
    "Buenos días", "Sí", "El archivo se guardó correctamente",
    "No pude completar eso",
    "Hola, soy Tlamatini y estoy lista para ayudarte",
)

#: Ingles. Ninguna se puede pronunciar TAL CUAL.
INGLES = (
    "Hello", "Hello, I am Lia", "Please wait", "Delete contact",
    "Unsaved changes", "The file was saved correctly", "Settings",
    "Download complete", "Loading", "Are you sure you want to continue",
)


class NoSeQuedaMudaEnCastellanoTests(unittest.TestCase):
    def test_el_castellano_corto_y_sin_acentos_se_habla(self):
        mudas = []
        for frase in CASTELLANO:
            _texto, como = tp.a_castellano(frase)
            if not como:
                mudas.append(frase)
        self.assertEqual(
            mudas, [],
            "Tlamatini se queda MUDA en su propio idioma con: %s.\n"
            "La regla es 'mejor muda que en ingles', NO 'muda en castellano'."
            % mudas)

    def test_hola_y_gracias_no_necesitan_traductor(self):
        # Se pronuncian tal cual, sin depender de que Ollama este prendido:
        # si dependieran, con Ollama apagado volveria el silencio.
        for frase in ("hola", "Gracias", "Hola Angela"):
            with self.subTest(frase=frase):
                texto, como = tp.a_castellano(frase)
                self.assertEqual(como, "ya-en-castellano",
                                 "'%s' deberia reconocerse como castellano" % frase)
                self.assertEqual(texto, frase)

    def test_la_marca_positiva_reconoce_contenido_no_solo_palabras_funcion(self):
        for frase in ("hola", "gracias", "archivo", "carpeta", "listo"):
            with self.subTest(frase=frase):
                self.assertTrue(tp._tiene_marca_de_castellano(frase),
                                "'%s' es castellano inequivoco" % frase)

    def test_las_terminaciones_castellanas_cuentan_como_marca(self):
        for frase in ("configuracion", "guardando", "rapidamente", "seguridad"):
            with self.subTest(frase=frase):
                self.assertTrue(tp._tiene_marca_de_castellano(frase))


class ElInglesSigueSinPronunciarseTests(unittest.TestCase):
    """Arreglar el silencio NO puede abrir la puerta al ingles."""

    def test_ninguna_frase_inglesa_se_pronuncia_tal_cual(self):
        fugas = []
        for frase in INGLES:
            texto, como = tp.a_castellano(frase)
            if como and texto.strip().lower() == frase.strip().lower():
                fugas.append(frase)
        self.assertEqual(
            fugas, [],
            "SE FUGO INGLES sin traducir: %s. Es lo unico prohibido." % fugas)

    def test_el_ingles_evidente_no_da_marca_de_castellano(self):
        for frase in ("Hello, I am Lia", "The file was saved correctly",
                      "Are you sure you want to continue"):
            with self.subTest(frase=frase):
                self.assertFalse(tp._tiene_marca_de_castellano(frase),
                                 "'%s' NO es castellano" % frase)

    def test_las_listas_no_traen_palabras_que_tambien_son_inglesas(self):
        # Una palabra identica en los dos idiomas (red, version, total, error,
        # final, real, capital) dejaria pasar ingles como si fuera castellano.
        ambiguas = {'red', 'version', 'total', 'error', 'final', 'real',
                    'capital', 'animal', 'natural', 'general', 'local',
                    'social', 'material', 'personal', 'principal', 'actual',
                    'no', 'me', 'van', 'son', 'sea', ' salt'}
        coladas = sorted(tp._PALABRAS_ES_CONTENIDO & ambiguas)
        self.assertEqual(
            coladas, [],
            "estas palabras existen igual en ingles y no pueden servir de "
            "marca de castellano: %s" % coladas)


class LaVozEspanolaSigueSiendoLaPorOmisionTests(unittest.TestCase):
    def test_la_voz_por_omision_es_mexicana(self):
        self.assertTrue(tp._DEFAULT_VOICE.lower().startswith("es_"),
                        "la voz por omision dejo de ser española: %s"
                        % tp._DEFAULT_VOICE)
        self.assertIn("es_MX", tp._DEFAULT_VOICE)


if __name__ == "__main__":
    unittest.main()
