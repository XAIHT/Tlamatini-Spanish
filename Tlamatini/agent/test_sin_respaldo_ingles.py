# ══════════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ══════════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove (releases scrub the name automatically)
"""EN LA EDICION EN CASTELLANO NO HAY RESPALDO EN INGLES (Angela, 2026-08-19).

Angela, palabras suyas: *"si una hispanohablante oye ingles, no va a pasar
el milagro de que de repente lo entienda"*. Un respaldo al ingles NO es una
degradacion elegante: es una FALLA que ademas suena a que funciono. La unica
alternativa aceptable a la voz correcta es el SILENCIO — la misma regla que
el agent Talker ya aplica a una voz masculina.

LO QUE ESTABA PASANDO. Angela oia acento ingles en las pruebas, y el codigo
juraba en sus comentarios que se quedaba callado. Hacian lo contrario:

  * ``avatar.js::spanishPool()`` cerraba con
    ``var en=by(/^en(-|_|$)/i); return en.length?en:vs;`` — o sea que en una
    maquina sin voces en castellano (un Windows de fabrica trae David, Mark y
    Zira, las tres en-US) el pool ERA el ingles.
  * ``avatar.js::pickVoice()`` cerraba prefiriendo
    ``/zira|jenny|aria|samantha|hazel/`` "para que una maquina sin voz en
    espanol igual hablara". Hablaba: en ingles.
  * ``talker.py`` resolvia ``config.get('language') or 'en'``.
  * ``whatsapper.py`` probaba las plantillas en ``("en", "en_US", …)``, o sea
    que a un destinatario hispanohablante le llegaba la inglesa.

Zira pasa el filtro de "voz femenina", asi que nada la frenaba.

ESTA PRUEBA ES LA ESTACA. Si alguien vuelve a meter un escalon en ingles en
cualquiera de esos cuatro lugares, se pone roja.
"""
import os
import re
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))
_JS = os.path.join(_AQUI, "static", "agent", "js")
_AGENTES = os.path.join(_AQUI, "agents")


def _lee(*partes):
    with open(os.path.join(*partes), encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def _sin_comentarios_js(texto):
    """Quita // y /* */ para que un comentario que EXPLICA el bug no cuente
    como si fuera el bug."""
    texto = re.sub(r"/\*.*?\*/", " ", texto, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", ln) for ln in texto.splitlines())


def _cuerpo(texto, nombre):
    """El cuerpo de una function JS, por conteo de llaves."""
    m = re.search(r"function\s+%s\s*\(" % re.escape(nombre), texto)
    if not m:
        return ""
    i = texto.index("{", m.end() - 1)
    prof = 0
    for j in range(i, len(texto)):
        if texto[j] == "{":
            prof += 1
        elif texto[j] == "}":
            prof -= 1
            if prof == 0:
                return texto[i:j + 1]
    return texto[i:]


class LaVozNuncaCaeEnIngles(unittest.TestCase):
    """avatar.js — la voz de accesibilidad del navegador."""

    def setUp(self):
        self.js = _sin_comentarios_js(_lee(_JS, "avatar.js"))

    def test_el_pool_de_voces_no_tiene_escalon_en_ingles(self):
        cuerpo = _cuerpo(self.js, "spanishPool")
        self.assertTrue(cuerpo, "no encontre spanishPool() en avatar.js")
        self.assertNotRegex(
            cuerpo, r"\^en\b|\^en\(",
            "spanishPool() volvio a caer en voces en ingles: sin voz en "
            "castellano tiene que devolver VACIO, no el pool ingles.")

    def test_el_pool_devuelve_vacio_cuando_no_hay_castellano(self):
        cuerpo = _cuerpo(self.js, "spanishPool")
        self.assertRegex(
            cuerpo.replace(" ", ""), r"return\[\];",
            "spanishPool() debe terminar en `return [];` — vacio manda a "
            "Piper (es_MX) y, si no esta, al silencio.")
        self.assertNotRegex(
            cuerpo.replace(" ", ""), r"return(en\.length\?en:)?vs;",
            "spanishPool() no puede devolver TODAS las voces: ahi se cuela "
            "el ingles.")

    def test_pickvoice_no_prefiere_voces_inglesas(self):
        cuerpo = _cuerpo(self.js, "pickVoice")
        self.assertTrue(cuerpo, "no encontre pickVoice() en avatar.js")
        for nombre in ("zira", "jenny", "aria", "samantha", "hazel"):
            self.assertNotIn(
                nombre, cuerpo.lower(),
                "pickVoice() volvio a preferir la voz inglesa %r. Ninguna voz "
                "que no sea en castellano sale por esta boca." % nombre)

    def test_pickvoice_termina_en_null_no_en_una_voz_cualquiera(self):
        cuerpo = _cuerpo(self.js, "pickVoice")
        self.assertNotRegex(
            cuerpo.replace(" ", ""), r"return\(?pref\[0\]\|\|fem\[0\]",
            "pickVoice() no puede terminar devolviendo `fem[0]`: si no hay "
            "voz en castellano tiene que devolver null.")

    def test_el_castellano_de_espana_si_es_un_escalon_valido(self):
        # Angela, 2026-08-19: "SPANISH IN ACCESIBILITY AND SPANISH IN LLM
        # (IF NOT POSSIBLE SPANISH IN LATINAMERICAN OF CASTILLAN IS OK),
        # BUT NOT ENGLISH". El latinoamericano va primero; si no hay, el de
        # Espana sirve. Lo unico prohibido es el ingles. (Yo lo habia quitado
        # de mas: esta prueba existe para que no lo vuelva a quitar nadie.)
        cuerpo = _cuerpo(self.js, "spanishPool")
        self.assertRegex(
            cuerpo, r"\^es\(",
            "spanishPool() perdio el escalon de castellano general: si no hay "
            "voz latinoamericana, la de Espana SI se usa antes que callarse.")

    def test_si_no_hay_voz_elegida_no_habla_el_navegador(self):
        cuerpo = _cuerpo(self.js, "speak")
        self.assertRegex(
            cuerpo.replace(" ", ""), r"if\(!v\)\{speakViaServer",
            "speak() volvio a dejar hablar al navegador sin voz elegida: con "
            "`v` en null usa su voz POR DEFECTO, que es inglesa.")

    def test_la_pregunta_y_el_pool_miden_lo_mismo(self):
        cuerpo = _cuerpo(self.js, "spanishVoiceAvailable")
        self.assertIn(
            "spanishPool()", cuerpo,
            "spanishVoiceAvailable() tiene que preguntar exactamente lo que "
            "spanishPool() acepta; si se separan, una maquina puede decir "
            "'si hay espanol' y terminar hablando con la voz inglesa "
            "por defecto del navegador.")

    def test_una_voz_guardada_en_ingles_no_revive(self):
        cuerpo = _cuerpo(self.js, "pickVoice")
        bloque = cuerpo[:cuerpo.find("var mex")] if "var mex" in cuerpo else cuerpo
        self.assertIn(
            "voiceURI", bloque,
            "pickVoice() dejo de mirar la voz guardada por la usuaria.")
        self.assertRegex(
            bloque, r"\^es\(",
            "la voz guardada tiene que verificarse en castellano: si quedo "
            "grabada una inglesa de una version vieja, se ignora.")


class ElTalkerHablaCastellanoPorDefecto(unittest.TestCase):
    """El agent Talker — la voz que sintetiza el modelo."""

    def test_el_idioma_por_defecto_es_es(self):
        py = _lee(_AGENTES, "talker", "talker.py")
        self.assertNotIn(
            "config.get('language') or 'en'", py,
            "talker.py volvio a caer en 'en' cuando el config viene vacio.")
        self.assertIn("config.get('language') or 'es'", py)

    def test_el_config_yaml_dice_es(self):
        yaml = _lee(_AGENTES, "talker", "config.yaml")
        self.assertRegex(
            yaml, r'^language:\s*"es"', 
            "talker/config.yaml tiene que decir language: \"es\" en esta "
            "edicion.")

    def test_el_reporte_no_declara_en(self):
        py = _lee(_AGENTES, "talker", "talker.py")
        self.assertNotIn('config.get(\'language\', \'en\')', py)


class LasPlantillasPruebanCastellanoPrimero(unittest.TestCase):
    """Whatsapper — a quien habla espanol se le manda en espanol."""

    def test_la_escalera_empieza_en_castellano(self):
        py = _lee(_AGENTES, "whatsapper", "whatsapper.py")
        m = re.search(r"_LANGUAGE_FALLBACKS\s*=\s*\(([^)]*)\)", py)
        self.assertTrue(m, "no encontre _LANGUAGE_FALLBACKS en whatsapper.py")
        escalera = [x.strip().strip('"\'') for x in m.group(1).split(",")
                    if x.strip()]
        self.assertTrue(
            escalera[0].lower().startswith("es"),
            "la escalera de plantillas empieza en %r: en la edicion en "
            "castellano el primer intento tiene que ser es_MX/es." % escalera[0])


class ElPdfSaleEnCastellano(unittest.TestCase):

    def test_document_language_por_defecto_es(self):
        yaml = _lee(_AGENTES, "pdfer", "config.yaml")
        self.assertRegex(yaml, r'^document_language:\s*"es"')


if __name__ == "__main__":
    unittest.main()
