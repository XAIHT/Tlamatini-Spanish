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
            yaml, r'(?m)^language:\s*"es"', 
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
        self.assertRegex(yaml, r'(?m)^document_language:\s*"es"')


if __name__ == "__main__":
    unittest.main()


class ElNavegadorFiltraElTextoNoSoloLaVoz(unittest.TestCase):
    """avatar.js — la mitad que faltaba (Angela, 2026-08-27).

    Hasta hoy `speak()` elegia QUE VOZ usar y nada mas. Eso arregla el
    ACENTO y solamente el acento: si la LLM contestaba en ingles, la frase
    inglesa se le entregaba igual a `speechSynthesis` con `u.lang='es-MX'`
    y se oia INGLES con boca mexicana. El camino del servidor
    (`tts_piper.a_castellano`) si miraba el texto y devolvia
    'refused:ingles'; el del navegador no miraba nada. La regla se aplicaba
    en un camino y en el otro no, que es como no aplicarla.
    """

    def setUp(self):
        self.js = _sin_comentarios_js(_lee(_JS, "avatar.js"))

    def test_speak_mira_el_texto_antes_de_pronunciarlo(self):
        cuerpo = _cuerpo(self.js, "speak")
        self.assertTrue(cuerpo, "no encontre speak() en avatar.js")
        self.assertIn(
            "pareceCastellano", cuerpo,
            "speak() volvio a filtrar SOLO la voz: sin mirar el texto, una "
            "respuesta en ingles se pronuncia igual, con acento mexicano.")

    def test_el_texto_se_juzga_antes_que_la_voz(self):
        cuerpo = _cuerpo(self.js, "speak")
        self.assertLess(
            cuerpo.index("pareceCastellano"), cuerpo.index("spanishVoiceAvailable"),
            "el texto tiene que juzgarse ANTES de elegir voz: al reves, una "
            "frase inglesa con voz espanola disponible se pronuncia y ya.")

    def test_lo_que_no_es_castellano_va_a_traducirse_no_al_silencio(self):
        cuerpo = _cuerpo(self.js, "speak")
        pos = cuerpo.index("pareceCastellano")
        rama = cuerpo[pos:pos + 160]
        self.assertIn(
            "speakViaServer", rama,
            "lo que no viene en castellano debe ir a Piper, que PRIMERO "
            "intenta traducirlo. Callar de entrada tira texto que si se "
            "podia decir en castellano.")

    def test_la_funcion_exige_marca_positiva_no_ausencia_de_ingles(self):
        cuerpo = _cuerpo(self.js, "pareceCastellano")
        self.assertTrue(cuerpo, "falta pareceCastellano() en avatar.js")
        self.assertIn("_SET_ES", cuerpo)
        self.assertIn("_RE_ACENTO", cuerpo)
        self.assertNotIn(
            "_PALABRAS_INGLESAS", cuerpo,
            "no se pregunta '¿parece ingles?': esa pregunta contesta que no "
            "ante cualquier duda, y por eso se colaban 'Save' y 'Please wait'.")


class LasListasDelNavegadorNoSeDesincronizan(unittest.TestCase):
    """La copia en JS es un SUBCONJUNTO de la del servidor — nunca al reves.

    Las listas viven dos veces: en `tts_piper` (la autoridad) y en
    `avatar.js` (la copia barata que evita un viaje al servidor por cada
    frase). Dos copias se separan solas, asi que la direccion del error
    importa: quedarse CORTO en JS solo manda mas texto a Piper, que sabe
    traducir; PASARSE deja salir ingles por la bocina. Por eso se exige
    subconjunto y no igualdad: la lista de Python puede crecer sin romper
    esta prueba, pero una palabra inventada en el JS la pone roja.
    """

    def _palabras_js(self):
        js = _lee(_JS, "avatar.js")
        m = re.search(r"var\s+_PAL_ES\s*=\s*\[(.*?)\]", js, re.S)
        self.assertTrue(m, "no encontre _PAL_ES en avatar.js")
        return set(re.findall(r"'([^']+)'", m.group(1)))

    def test_toda_palabra_del_js_existe_en_el_servidor(self):
        from . import tts_piper as tp
        autoridad = set(tp._MARCAS_ES) | set(tp._PALABRAS_ES_CONTENIDO)
        sobra = self._palabras_js() - autoridad
        self.assertFalse(
            sobra,
            "estas palabras estan en avatar.js y NO en tts_piper: %s. Una "
            "palabra de mas en el navegador deja pasar texto que el servidor "
            "habria mandado a traducir." % sorted(sobra))

    def test_las_terminaciones_tambien_son_subconjunto(self):
        from . import tts_piper as tp
        js = _lee(_JS, "avatar.js")
        m = re.search(r"var\s+_SUF_ES\s*=\s*\[(.*?)\]", js, re.S)
        self.assertTrue(m, "no encontre _SUF_ES en avatar.js")
        sobra = set(re.findall(r"'([^']+)'", m.group(1))) - set(tp._SUFIJOS_ES)
        self.assertFalse(sobra, "terminaciones de mas en el JS: %s" % sorted(sobra))

    def test_la_copia_no_se_quedo_vacia(self):
        # Un subconjunto vacio pasaria las dos pruebas de arriba y mandaria
        # TODO al servidor: correcto pero lentisimo, y mudo sin Piper.
        self.assertGreater(len(self._palabras_js()), 100)


class LaLlmTieneOrdenDeContestarEnCastellano(unittest.TestCase):
    """prompt.pmt — la causa RAIZ, arriba de la voz (Angela, 2026-08-27).

    Filtrar la voz es curar el sintoma. Si la LLM contesta en ingles, el
    texto ingles ya existe: quedo escrito en la pantalla, se guardo en el
    historial y se copio al Exec Report. La voz es lo ultimo que pasa.
    Antes de hoy `prompt.pmt` no le pedia castellano ni una sola vez — la
    unica coincidencia de 'spanish' era el nombre de una plantilla de
    LaTeXer. El idioma de la respuesta dependia de la buena voluntad del
    modelo.
    """

    def setUp(self):
        self.pmt = _lee(_AQUI, "prompt.pmt")

    def test_la_orden_existe_y_es_explicita(self):
        # ⛔ LA REGLA AHORA ESTA ESCRITA EN CASTELLANO, y asi debe ser: la regla
        # que ordena hablar castellano no tenia por que estar en ingles. Se busca
        # la formula actual — "ESPAÑOL COMO LENGUA MATRIZ" — y de paso se acepta
        # la formula inglesa anterior, para que un arbol a medio migrar no de un
        # falso rojo. Lo que NO se acepta es que no este ninguna de las dos.
        tiene_orden = ("ESPAÑOL COMO LENGUA MATRIZ" in self.pmt
                       or "YOU ALWAYS ANSWER IN SPANISH" in self.pmt)
        self.assertTrue(
            tiene_orden,
            "prompt.pmt dejo de exigir castellano: sin esa linea el idioma "
            "de la respuesta queda a criterio del modelo.")

    def test_prohibe_el_ingles_sin_excepciones(self):
        # Misma razon: la prohibicion tambien esta en castellano.
        # La formula castellana dice "sin excepciones" de otra manera: la regla
        # PREVALECE sobre cualquier otra instruccion, y aplica "incluso cuando el
        # usuario o el contexto esten en ingles" — que es exactamente el caso que
        # esta prueba existe para blindar.
        bajo = self.pmt.lower()
        prohibe = (("prevalece sobre cualquier otra instrucci" in bajo
                    and "incluso cuando el usuario o el contexto" in bajo)
                   or "english is never acceptable" in bajo)
        self.assertTrue(prohibe,
                        "prompt.pmt dejo de prohibir el ingles sin excepciones")

    def test_protege_el_canal_de_maquina(self):
        # La orden de "todo en castellano" no debe llevarse por delante los
        # nombres que lee el codigo: traducir END-RESPONSE o INI_SECTION_*
        # rompe el parseo rio abajo.
        self.assertIn("END-RESPONSE", self.pmt)
        self.assertIn("INI_SECTION_", self.pmt)

    def test_la_orden_va_temprano_no_sepultada_al_final(self):
        marca = ("ESPAÑOL COMO LENGUA MATRIZ" if "ESPAÑOL COMO LENGUA MATRIZ" in self.pmt
                 else "YOU ALWAYS ANSWER IN SPANISH")
        pos = self.pmt.index(marca)
        self.assertLess(
            pos, len(self.pmt) * 0.10,
            "la regla del idioma quedo enterrada; va en el bloque de "
            "identidad, arriba, donde el modelo la pesa mas.")
