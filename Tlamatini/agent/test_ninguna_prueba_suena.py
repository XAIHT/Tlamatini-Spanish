# -*- coding: utf-8 -*-
"""Guard: NINGUNA PRUEBA SUENA, Y NADA HABLA INGLES.

Lo que paso el 2026-08-26, y que esta clase existe para que no se repita:

    `python manage.py test agent` corrio al agent Talker DE VERDAD — su
    `play_audio` viene en True por omision — y Tlamatini hablo POR LAS BOCINAS
    de Angela, de noche, sin que nadie se lo pidiera. Y hablo EN INGLES.

Son dos fallas distintas y las dos son graves:

1. Una suite de pruebas capaz de manejar las bocinas reales de una persona es
   un defecto EN CUALQUIER IDIOMA. Una prueba se mira, no se oye.
2. Que lo que sono fuera INGLES rompio la regla de oro de esta edicion en voz
   alta, que es la unica manera en que la usuaria puede enterarse.

Las rejas que ya existian miraban el MODELO y la VOZ *antes* de sintetizar.
Ninguna miraba el instante en que el audio sale por la bocina, que es lo unico
que la usuaria oye de verdad. Estas pruebas fijan esa ultima reja.
"""

import ast
import os
import unittest
from pathlib import Path

AGENTE = Path(__file__).resolve().parent
RAIZ_DJANGO = AGENTE.parent
TALKER = AGENTE / "agents" / "talker" / "talker.py"
AUDIOPLAYER = AGENTE / "agents" / "audioplayer" / "audioplayer.py"
MANAGE = RAIZ_DJANGO / "manage.py"


def _leer(ruta):
    return ruta.read_text(encoding="utf-8", errors="replace")


class LaSuiteSeMarcaComoMudaTests(unittest.TestCase):
    """`manage.py` tiene que marcar la corrida ANTES de que Django arranque."""

    def test_manage_marca_sin_audio_cuando_el_comando_es_test(self):
        src = _leer(MANAGE)
        self.assertIn("TLAMATINI_SIN_AUDIO", src,
                      "manage.py ya no marca las corridas de prueba como mudas")
        self.assertIn("_silenciar_las_pruebas", src)

    def test_la_marca_se_pone_antes_de_arrancar_django(self):
        # Si se pusiera despues, un agent lanzado durante el arranque ya
        # habria sonado. El orden es el contrato.
        # Se comparan las LLAMADAS a nivel de modulo (ancladas a inicio de
        # linea), no la primera aparicion del nombre: la definicion de
        # `_enforce_app_temp_dir` vive mucho mas arriba en el archivo y
        # comparar contra ella medía cualquier cosa menos el orden real.
        src = _leer(MANAGE)
        marca = src.find("\n_silenciar_las_pruebas()")
        temp = src.find("\n_enforce_app_temp_dir()")
        self.assertNotEqual(marca, -1, "no se llama a _silenciar_las_pruebas()")
        self.assertNotEqual(temp, -1, "no se llama a _enforce_app_temp_dir()")
        self.assertLess(marca, temp,
                        "la marca de sin-audio tiene que ir antes que todo lo demas")

    def test_esta_corrida_esta_marcada_como_muda(self):
        # Esta prueba se esta ejecutando AHORA MISMO bajo `manage.py test`, asi
        # que la variable tiene que estar puesta. Si esto falla, el mecanismo
        # completo no sirve.
        valor = str(os.environ.get("TLAMATINI_SIN_AUDIO", "")).strip().lower()
        self.assertTrue(valor and valor not in ("0", "false", "no"),
                        "esta corrida de pruebas NO esta marcada como muda: "
                        "un agent podria sonar en las bocinas de la usuaria")


class ElTalkerNoSuenaEnPruebasTests(unittest.TestCase):
    def setUp(self):
        self.src = _leer(TALKER)

    def test_existe_la_reja_de_pruebas(self):
        self.assertIn("def _corriendo_pruebas(", self.src)

    def test_la_reja_va_antes_de_sd_play(self):
        reja = self.src.find("_corriendo_pruebas()")
        play = self.src.find("sd.play(")
        self.assertNotEqual(reja, -1, "el Talker ya no revisa si esta en pruebas")
        self.assertNotEqual(play, -1)
        self.assertLess(reja, play,
                        "la revision tiene que ir ANTES de sd.play, no despues")

    def test_play_pcm_es_el_unico_lugar_que_reproduce(self):
        # Si aparece un segundo sd.play fuera de play_pcm, la reja se puede
        # rodear sin querer. Que se entere quien lo agregue.
        arbol = ast.parse(self.src)
        fuera = []
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.FunctionDef) or nodo.name == "play_pcm":
                continue
            for hijo in ast.walk(nodo):
                if (isinstance(hijo, ast.Call)
                        and isinstance(hijo.func, ast.Attribute)
                        and hijo.func.attr == "play"):
                    fuera.append(nodo.name)
        self.assertEqual(sorted(set(fuera)), [],
                         "hay reproduccion fuera de play_pcm: %s" % sorted(set(fuera)))


class MatarAntesQueHablarInglesTests(unittest.TestCase):
    """La regla de oro, aplicada en el ultimo instante posible."""

    def setUp(self):
        self.src = _leer(TALKER)

    def test_existe_la_reja_final_de_idioma(self):
        self.assertIn("def _matar_si_va_a_sonar_en_ingles(", self.src)

    def test_mata_el_proceso_no_solo_avisa(self):
        # Degradar, traducir a medias o avisar y seguir NO son opciones: el
        # audio ya habria salido. Se muere, como con la voz masculina.
        i = self.src.find("def _matar_si_va_a_sonar_en_ingles(")
        j = self.src.find("\ndef ", i + 10)
        cuerpo = self.src[i:j if j != -1 else len(self.src)]
        self.assertIn("os._exit(", cuerpo,
                      "la reja avisa pero no mata: el ingles alcanzaria a sonar")

    def test_la_reja_de_idioma_va_antes_de_sd_play(self):
        reja = self.src.find("_matar_si_va_a_sonar_en_ingles(config)")
        play = self.src.find("sd.play(")
        self.assertNotEqual(reja, -1, "no se llama a la reja de idioma")
        self.assertLess(reja, play, "la reja de idioma va ANTES de reproducir")

    def test_sigue_muriendo_por_voz_masculina(self):
        # La regla vieja no se debilita al agregar la nueva.
        self.assertIn("MaleVoiceForbiddenError", self.src)
        self.assertIn("EnglishVoiceForbiddenError", self.src)


class ElAudioPlayerTampocoSuenaTests(unittest.TestCase):
    def test_el_audioplayer_respeta_la_marca(self):
        src = _leer(AUDIOPLAYER)
        self.assertIn("TLAMATINI_SIN_AUDIO", src,
                      "el AudioPlayer puede sonar durante una prueba")


if __name__ == "__main__":
    unittest.main()
