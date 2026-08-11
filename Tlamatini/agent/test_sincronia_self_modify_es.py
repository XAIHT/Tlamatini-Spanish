# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
#
#   Every line of this file was written by Angela López Mendoza.
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""Guardas de la SINCRONÍA entre Tlamatini (inglés) y esta edición.

Qué se portó de la rama inglesa (commit `3ca135ad` y compañía) y qué prueba
cada clase de aquí:

1. **El gate de `--self-modify`** — `Tlamatini.md` y `TlamatiniSourceCode/`
   viajan JUNTOS o no viajan. Sin el flag, el prompt del sistema ya no carga
   la auto-descripción completa en CADA request.
2. **El parser de tool calls locales** — los models locales escriben la tool
   call como TEXTO en `.content` en vez de usar el campo estructurado. Sin la
   recuperación, ese JSON crudo se le mostraba al usuario como respuesta final.
3. **Los models por defecto** pasaron a `gpt-oss:20b` (local) — que es justo
   POR QUÉ existe el parser de arriba — y después se regresaron a
   `glm-5.2:cloud` en las DOS ediciones. El parser se queda: es fail-open (solo
   entra cuando `tool_calls` viene vacío, cosa que un model cloud nunca hace),
   así que no estorba y sigue cubriendo a quien apunte a un model local.
4. **La ventana forked de Executer** dejó de usar `@pause` (un pool agent no
   tiene stdin de consola, así que `pause` ve EOF y regresa al instante: la
   ventana parpadeaba y desaparecía mientras el log cantaba éxito).

⚠️ La clase que más importa aquí es `MensajeAlUsuarioEnEspanolTests`. El
resto se puede verificar contra el árbol inglés, pero el mensaje que LEE la
usuaria y las marcas de fuga traducidas son propios de esta edición: si
alguien vuelve a copiar el archivo inglés encima, esas pruebas se ponen rojas
y nadie se entera tarde.

Sin base de datos y sin arrancar Django: se lee el código fuente y se analiza
con `ast`, igual que `test_django_port_config.py`.
"""

import ast
import json
import os
import re
import unittest

# ── Rutas de los dos árboles ────────────────────────────────────────────────
AQUI = os.path.dirname(os.path.abspath(__file__))          # .../Tlamatini/agent
RAIZ_APP = os.path.dirname(AQUI)                            # .../Tlamatini
RAIZ_REPO = os.path.dirname(RAIZ_APP)                       # raíz del repo

RUTA_MCP_AGENT = os.path.join(AQUI, "mcp_agent.py")
RUTA_PARSER = os.path.join(AQUI, "local_toolcall_parser.py")
RUTA_CONFIG_JSON = os.path.join(AQUI, "config.json")
RUTA_PROMPT = os.path.join(AQUI, "prompt.pmt")
RUTA_FACTORY = os.path.join(AQUI, "rag", "factory.py")
RUTA_RAG_CONFIG = os.path.join(AQUI, "rag", "config.py")
RUTA_EXECUTER = os.path.join(AQUI, "agents", "executer", "executer.py")
RUTA_BUILD = os.path.join(RAIZ_REPO, "build.py")
RUTA_UI_ES = os.path.join(AQUI, "i18n", "ui_es.py")
DIR_IMAGENES = os.path.join(AQUI, "images")


def leer(ruta):
    """Lee un archivo de texto del árbol. Falla la prueba si no existe."""
    with open(ruta, encoding="utf-8") as fh:
        return fh.read()


# ════════════════════════════════════════════════════════════════════════════
class MarcasDePromptTests(unittest.TestCase):
    """`prompt.pmt` trae los sentinels con los que el build recorta bloques.

    Son la mitad de RUNTIME del gate: `load_config_and_prompt` resuelve el XOR
    entre el bloque de auto-conocimiento y el bloque "esta build no se puede
    auto-modificar". Una marca de menos y se envía el bloque equivocado.
    """

    RE_MARCA = re.compile(
        r"<!--((?:SELF_KNOWLEDGE|NOT_SELF_MODIFY)_(?:BEGIN|END))-->")

    def setUp(self):
        self.marcas = self.RE_MARCA.findall(leer(RUTA_PROMPT))

    def test_estan_las_seis_marcas_en_orden(self):
        self.assertEqual(
            self.marcas,
            ["SELF_KNOWLEDGE_BEGIN", "SELF_KNOWLEDGE_END",
             "NOT_SELF_MODIFY_BEGIN", "NOT_SELF_MODIFY_END",
             "SELF_KNOWLEDGE_BEGIN", "SELF_KNOWLEDGE_END"],
            "la secuencia de sentinels de prompt.pmt no coincide con la inglesa",
        )

    def test_las_marcas_estan_balanceadas_y_sin_anidar(self):
        pila = []
        for marca in self.marcas:
            nombre, borde = marca.rsplit("_", 1)
            if borde == "BEGIN":
                self.assertFalse(pila, "sentinel anidado: %s dentro de %s"
                                 % (marca, pila))
                pila.append(nombre)
            else:
                self.assertTrue(pila and pila[-1] == nombre,
                                "END sin su BEGIN: %s" % marca)
                pila.pop()
        self.assertFalse(pila, "quedó un sentinel sin cerrar: %s" % pila)

    def test_el_bloque_not_self_modify_no_promete_auto_modificacion(self):
        texto = leer(RUTA_PROMPT)
        i = texto.index("<!--NOT_SELF_MODIFY_BEGIN-->")
        j = texto.index("<!--NOT_SELF_MODIFY_END-->")
        bloque = texto[i:j]
        self.assertIn("not-self-able-modify", bloque)
        # Si este bloque dijera que SÍ puede leerse a sí misma, mentiría
        # justo en la build donde no trae ni su código ni su descripción.
        self.assertNotIn("TlamatiniSourceCode/_REBUILD_INSTRUCTIONS.md", bloque)

    def test_el_marcador_de_plantilla_sigue_presente(self):
        # Si `{self_knowledge}` desapareciera, la rama con --self-modify ya no
        # tendría dónde inyectar el archivo.
        self.assertIn("{self_knowledge}", leer(RUTA_PROMPT))


# ════════════════════════════════════════════════════════════════════════════
class GateDeEmpaquetadoTests(unittest.TestCase):
    """`build.py`: el código fuente y la auto-descripción viajan JUNTOS."""

    def setUp(self):
        self.fuente = leer(RUTA_BUILD)

    def test_no_self_modify_le_gana_a_self_modify(self):
        # `--no-self-modify` es la forma EXPLÍCITA del default y debe ganar,
        # para que un wrapper pueda forzarlo aunque alguien pase el otro flag.
        self.assertIn(
            'self_modify = "--self-modify" in sys.argv '
            'and "--no-self-modify" not in sys.argv',
            self.fuente,
        )

    def test_tlamatini_md_ya_no_se_empaqueta_incondicionalmente(self):
        # La línea vieja metía la auto-descripción en TODAS las builds.
        self.assertNotIn(
            "f'--add-data=Tlamatini/agent/Tlamatini.md{separator}agent',",
            self.fuente,
            "Tlamatini.md volvió a empaquetarse sin condición: eso restaura "
            "el costo completo de contexto en la build por defecto",
        )
        self.assertIn("*self_knowledge_args,", self.fuente)

    def test_la_copia_a_la_raiz_esta_condicionada(self):
        arbol = ast.parse(self.fuente)
        copias_condicionadas = False
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.If):
                continue
            if not (isinstance(nodo.test, ast.Name)
                    and nodo.test.id == "self_modify"):
                continue
            if "Tlamatini.md" in ast.dump(nodo):
                copias_condicionadas = True
        self.assertTrue(
            copias_condicionadas,
            "la copia de Tlamatini.md a la raíz de instalación debe vivir "
            "dentro de un `if self_modify:`",
        )

    def test_el_idioma_espanol_sigue_siendo_obligatorio(self):
        # Propio de esta edición: un frozen español sin agents_descriptions.es.md
        # se ve entero en inglés en cada tooltip, y nadie se entera hasta que
        # la usuaria lo ve. Por eso va en required_file_copies, no en optional.
        self.assertIn('Path("agents_descriptions.es.md")', self.fuente)
        i = self.fuente.index("required_file_copies = {")
        j = self.fuente.index("}", i)
        self.assertIn("agents_descriptions.es.md", self.fuente[i:j])


# ════════════════════════════════════════════════════════════════════════════
class ModelosPorDefectoTests(unittest.TestCase):
    """Los models por defecto y las perillas de Ollama que trajo el sync."""

    MODELOS = (
        "chained-model", "access_aimed_prompt_model", "unified_agent_model",
        "image_merging_model", "mcp_files_search_model",
        "internet_classifier_model", "web_summarizer_model",
    )

    def setUp(self):
        with open(RUTA_CONFIG_JSON, encoding="utf-8-sig") as fh:
            self.cfg = json.load(fh)

    # El model que ambas ediciones usan hoy. Angela lo cambió a mano el
    # Los modelos deben ser glm-5.2:cloud, después de
    # probar el local `gpt-oss:20b`. Si vuelve a cambiarlo, se ajusta AQUÍ, en
    # un solo lugar.
    MODEL_ESPERADO = "glm-5.2:cloud"

    def test_los_siete_models_van_juntos(self):
        """Los siete apuntan al MISMO model.

        Esto es lo que de verdad se puede romper: cambiar unos cuantos y
        olvidar el resto deja la edición medio migrada, y el síntoma (una
        cadena respondiendo distinto a las demás) no se parece en nada a la
        causa. Se comprueba la CONSISTENCIA antes que el nombre concreto.
        """
        valores = {clave: self.cfg.get(clave) for clave in self.MODELOS}
        distintos = sorted(set(valores.values()))
        self.assertEqual(
            len(distintos), 1,
            "los models no van juntos, hay %d valores distintos: %s"
            % (len(distintos), valores))

    def test_los_models_son_los_mismos_que_en_ingles(self):
        """Y el valor es el que Angela eligió para las DOS ediciones."""
        for clave in self.MODELOS:
            self.assertEqual(
                self.cfg.get(clave), self.MODEL_ESPERADO,
                "%s quedó en %r; las dos ediciones deben usar %r"
                % (clave, self.cfg.get(clave), self.MODEL_ESPERADO))

    def test_estan_las_perillas_de_ollama(self):
        self.assertEqual(self.cfg.get("ollama_repeat_penalty"), 1.9)
        self.assertEqual(self.cfg.get("ollama_num_ctx"), 63536)

    def test_factory_lee_las_perillas_y_usa_num_ctx(self):
        fuente = leer(RUTA_FACTORY)
        # `context_window` NO es el parámetro real de ChatOllama; el correcto
        # es `num_ctx`. Mientras estuvo mal escrito, el valor se ignoraba.
        self.assertNotIn("context_window=", fuente,
                         "quedó un context_window=: ChatOllama lo ignora")
        self.assertEqual(fuente.count("config.get('ollama_num_ctx'"), 2)
        self.assertEqual(fuente.count("config.get('ollama_repeat_penalty'"), 2)

    def test_cada_cadena_conserva_su_propio_default(self):
        # Los dos sitios NO comparten default a propósito: la cadena de
        # recuperación pide una ventana más chica. Colapsarlos cambiaría
        # el comportamiento de una de las dos en silencio.
        fuente = leer(RUTA_FACTORY)
        for esperado in ("config.get('ollama_num_ctx', 128000)",
                         "config.get('ollama_num_ctx', 8192)",
                         "config.get('ollama_repeat_penalty', 1.9)",
                         "config.get('ollama_repeat_penalty', 1.1)"):
            self.assertIn(esperado, fuente, "falta el default %s" % esperado)


# ════════════════════════════════════════════════════════════════════════════
class ParserDeToolCallsLocalesTests(unittest.TestCase):
    """El módulo nuevo y su enganche en el executor de Multi-Turn."""

    def test_el_modulo_existe_y_expone_su_superficie(self):
        self.assertTrue(os.path.isfile(RUTA_PARSER),
                        "falta agent/local_toolcall_parser.py")
        arbol = ast.parse(leer(RUTA_PARSER))
        definidas = {n.name for n in ast.walk(arbol)
                     if isinstance(n, ast.FunctionDef)}
        for funcion in ("extract_text_tool_calls", "describe_toolcall_shape",
                        "looks_like_tool_call_attempt", "suggest_tool_names"):
            self.assertIn(funcion, definidas)

    def test_mcp_agent_lo_importa_y_lo_usa(self):
        fuente = leer(RUTA_MCP_AGENT)
        self.assertIn("from agent.local_toolcall_parser import", fuente)
        for marca in ("extract_text_tool_calls(", "describe_toolcall_shape(",
                      "looks_like_tool_call_attempt(", "suggest_tool_names("):
            self.assertIn(marca, fuente)

    def test_la_recuperacion_solo_corre_si_no_hubo_tool_calls(self):
        # Es lo que la hace SEGURA con models cloud: un model cloud siempre
        # llena tool_calls, así que nunca entra a esta rama.
        fuente = leer(RUTA_MCP_AGENT)
        i = fuente.index("_recovered = []")
        ventana = fuente[i:i + 400]
        self.assertIn("if not tool_calls:", ventana)

    def test_las_correcciones_por_tool_inventada_estan_acotadas(self):
        # Sin tope, un model terco reintentaría para siempre.
        fuente = leer(RUTA_MCP_AGENT)
        self.assertIn("self._hallucinated_tool_nudges < 3", fuente)
        self.assertIn("self._hallucinated_tool_nudges: int = 0", fuente)

    def test_toda_salida_pasa_por_el_saneador(self):
        fuente = leer(RUTA_MCP_AGENT)
        self.assertIn("answer = self._sanitize_user_facing_answer(answer)",
                      fuente)


# ════════════════════════════════════════════════════════════════════════════
class MensajeAlUsuarioEnEspanolTests(unittest.TestCase):
    """⚠️ LA CLASE QUE DEFIENDE ESTA EDICIÓN.

    El saneador reemplaza una fuga de plomería interna por un mensaje humano.
    Ese mensaje LO LEE la usuaria, así que aquí va en español — y apunta a los
    nombres REALES del menú español. Si alguien vuelve a copiar el archivo
    inglés encima, estas pruebas se ponen rojas.
    """

    def setUp(self):
        self.fuente = leer(RUTA_MCP_AGENT)
        arbol = ast.parse(self.fuente)
        self.metodo = None
        for nodo in ast.walk(arbol):
            if (isinstance(nodo, ast.FunctionDef)
                    and nodo.name == "_sanitize_user_facing_answer"):
                self.metodo = nodo
        self.assertIsNotNone(self.metodo, "falta _sanitize_user_facing_answer")
        self.cadenas = [n.value for n in ast.walk(self.metodo)
                        if isinstance(n, ast.Constant)
                        and isinstance(n.value, str)]
        self.texto_metodo = " ".join(self.cadenas)

    def test_el_mensaje_al_usuario_esta_en_espanol(self):
        self.assertIn("No pude completar eso", self.texto_metodo)
        self.assertNotIn("I could not complete that", self.texto_metodo,
                         "el mensaje volvió al inglés: la usuaria de esta "
                         "edición leería una respuesta en otro idioma")

    def test_apunta_al_nombre_real_del_menu_espanol(self):
        # Mandar a la usuaria a "Config ▸ Models" sería mandarla a un menú
        # que en esta edición NO se llama así.
        self.assertIn("Configuración ▸ Modelos", self.texto_metodo)
        self.assertNotIn("Config ▸ Models", self.texto_metodo)

    def test_el_menu_citado_existe_de_verdad_en_ui_es(self):
        ui = leer(RUTA_UI_ES)
        self.assertIn('"Config": "Configuración"', ui)
        self.assertIn('"Models": "Modelos"', ui)

    def test_el_vocabulario_tecnico_sigue_en_ingles(self):
        # Registro Spanglish: gramática y verbos en español, sustantivos
        # técnicos en inglés. "tool"/"model" NO se traducen.
        for termino in ("tools", "model"):
            self.assertIn(termino, self.texto_metodo,
                          "se tradujo un término técnico que debe quedar en "
                          "inglés: %s" % termino)
        for prohibido in ("herramientas disponibles", "modelo local"):
            self.assertNotIn(prohibido, self.texto_metodo)

    def test_concuerda_con_el_genero_que_ya_usa_el_archivo(self):
        # mcp_agent.py ya dice "ningún tool", "los tools", "el model". El
        # mensaje nuevo tiene que sonar igual: cambiar de género a media voz
        # se nota, y delata una traducción hecha aparte del resto del archivo.
        self.assertIn("los tools", self.texto_metodo)
        self.assertNotIn("las tools", self.texto_metodo)
        self.assertIn("un tool que no", self.texto_metodo)

    def test_detecta_la_fuga_tambien_traducida(self):
        # La corrección que inyectamos va en inglés, pero un model que contesta
        # en español puede parrotearla TRADUCIDA. Sin estas marcas el guard
        # queda medio ciego justo en esta edición.
        for marca in ("no existe la tool", "correccion interna del sistema",
                      "mecanismo de tool-calling"):
            self.assertIn(marca, self.cadenas,
                          "falta la marca de fuga en español: %s" % marca)

    def test_sigue_detectando_las_marcas_inglesas(self):
        # La corrección inyectada ES inglesa, así que estas no se pueden quitar.
        for marca in ("internal system correction", "there is no tool named"):
            self.assertIn(marca, self.cadenas)

    def test_compara_sin_acentos(self):
        # El model escribe "corrección" o "correccion" indistintamente; una
        # marca acentuada no cazaría a la otra.
        cuerpo = ast.dump(self.metodo)
        self.assertIn("_nepantla_fold", cuerpo,
                      "la comparación debe plegar acentos")
        self.assertIn("folded_low", cuerpo)

    def test_el_saneador_nunca_revienta(self):
        # Es la última línea de defensa antes del usuario: si lanzara, se
        # llevaría la respuesta entera por delante.
        self.assertTrue(
            any(isinstance(n, ast.Try) for n in ast.walk(self.metodo)),
            "_sanitize_user_facing_answer debe ser total (try/except)")


# ════════════════════════════════════════════════════════════════════════════
class VentanaForkedDeExecuterTests(unittest.TestCase):
    """La ventana forked se queda abierta de verdad y devuelve su exit code."""

    def setUp(self):
        self.fuente = leer(RUTA_EXECUTER)

    def test_ya_no_se_escribe_pause_en_el_wrapper(self):
        # `pause` ve EOF en un pool agent y regresa al instante: la ventana
        # parpadeaba y desaparecía mientras el log cantaba éxito.
        self.assertNotIn("wf.write('@pause", self.fuente)
        self.assertNotIn('wf.write("@pause', self.fuente)

    def test_la_espera_es_acotada_y_configurable(self):
        self.assertIn("FORKED_WINDOW_HOLD_SECONDS", self.fuente)
        self.assertIn("Start-Sleep -Seconds", self.fuente)
        # Acotada por los dos lados: ni una ventana que se cierra sola de
        # inmediato, ni una consola invisible colgada para siempre.
        self.assertIn("_hold = max(5, min(_hold, 86400))", self.fuente)

    def test_el_exit_code_viaja_por_el_archivo_centinela(self):
        # Así el agente regresa cuando el TRABAJO terminó, sin esperar a que
        # alguien cierre la ventana a mano.
        self.assertIn("temp_forked_exitcode.txt", self.fuente)
        self.assertIn("sentinel_path", self.fuente)

    def test_se_lanza_con_c_y_no_con_k(self):
        """`/c`, nunca `/k`.

        `/k` deja la consola viva para siempre; bajo el host MCP la ventana es
        invisible, así que sería un cmd.exe huérfano por cada corrida.

        Se mira la LISTA de argumentos con el AST, no el texto literal: la
        versión anterior fijaba la cadena exacta
        `['cmd.exe', '/c', wrapper_path]` y se puso roja en cuanto se añadió la
        marca TLAMATINI_KEEP_CONSOLE_ALIVE — se quejaba de un cambio correcto.
        Una prueba debe fijar la INTENCIÓN (`/c` sí, `/k` no), no el formato.
        """
        arbol = ast.parse(self.fuente)
        lanzamientos = []
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.List):
                continue
            partes = [e.value for e in nodo.elts
                      if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            if "cmd.exe" in partes:
                lanzamientos.append(partes)
        self.assertTrue(lanzamientos, "no encontré el lanzamiento de cmd.exe")
        for partes in lanzamientos:
            self.assertIn("/c", partes, "el lanzamiento perdió el /c: %s" % partes)
            self.assertNotIn("/k", partes,
                             "reapareció /k: la consola quedaría viva para "
                             "siempre y bajo el host MCP ni se ve: %s" % partes)

    def test_el_archivo_compila(self):
        compile(self.fuente, RUTA_EXECUTER, "exec")


# ════════════════════════════════════════════════════════════════════════════
class ActivosDelSyncTests(unittest.TestCase):
    """Los archivos que el sync trajo y que el build necesita encontrar."""

    def test_llegaron_las_cuatro_imagenes(self):
        for imagen in ("versions.png", "MenuConfig.jpg", "ConfigureModels.jpg",
                       "ACPXKeysConfigureWizard.jpg"):
            ruta = os.path.join(DIR_IMAGENES, imagen)
            self.assertTrue(os.path.isfile(ruta), "falta la imagen %s" % imagen)
            self.assertGreater(os.path.getsize(ruta), 1024,
                               "%s llegó vacía o truncada" % imagen)

    def test_rag_config_resuelve_el_gate_en_tiempo_de_ejecucion(self):
        """El gate tiene que estar CABLEADO, no solo definido.

        ⚠️ Esta prueba antes solo pedía que los nombres APARECIERAN en el
        archivo (`assertIn("is_self_able_modify", fuente)`), y eso era inútil:
        el nombre existe en la DEFINICIÓN, así que la prueba seguía verde
        aunque nadie llamara a la función — que es exactamente el bug del
        que esto debía cuidar. Una prueba que no puede ponerse roja
        no cuida nada. Ahora se busca la LLAMADA dentro de
        `load_config_and_prompt`, con el AST (inmune a un reformateo).
        """
        arbol = ast.parse(leer(RUTA_RAG_CONFIG))
        cargador = None
        for nodo in ast.walk(arbol):
            if (isinstance(nodo, ast.FunctionDef)
                    and nodo.name == "load_config_and_prompt"):
                cargador = nodo
        self.assertIsNotNone(cargador, "falta load_config_and_prompt")

        # 1) la llamada existe, y su resultado se ASIGNA a prompt_template
        #    (descartarlo equivaldría a no cablearlo).
        linea_llamada = None
        for nodo in ast.walk(cargador):
            if not isinstance(nodo, ast.Assign):
                continue
            if not (isinstance(nodo.value, ast.Call)
                    and getattr(nodo.value.func, "id", "")
                    == "apply_self_knowledge_blocks"):
                continue
            destinos = [t.id for t in nodo.targets if isinstance(t, ast.Name)]
            self.assertIn("prompt_template", destinos,
                          "el resultado de apply_self_knowledge_blocks se está "
                          "descartando: eso es no cablearlo")
            linea_llamada = nodo.lineno
        self.assertIsNotNone(
            linea_llamada,
            "load_config_and_prompt NO llama a apply_self_knowledge_blocks: "
            "las marcas se filtran al prompt y sobreviven los DOS bloques")

        # 2) EL ORDEN ES EL CONTRATO: resolver los bloques ANTES de sustituir
        #    el placeholder. Al revés, el archivo se inyecta en un bloque que
        #    está por borrarse y las marcas se filtran igual.
        linea_placeholder = None
        for nodo in ast.walk(cargador):
            if (isinstance(nodo, ast.If)
                    and "SELF_KNOWLEDGE_PLACEHOLDER" in ast.dump(nodo.test)):
                linea_placeholder = nodo.lineno
        self.assertIsNotNone(linea_placeholder,
                             "no encontré la sustitución del placeholder")
        self.assertLess(linea_llamada, linea_placeholder,
                        "el cableado quedó DESPUÉS de sustituir el placeholder")

    def test_el_gate_falla_cerrado(self):
        """Sin árbol de código fuente no se presume auto-modificación."""
        arbol = ast.parse(leer(RUTA_RAG_CONFIG))
        fn = None
        for nodo in ast.walk(arbol):
            if (isinstance(nodo, ast.FunctionDef)
                    and nodo.name == "is_self_able_modify"):
                fn = nodo
        self.assertIsNotNone(fn, "falta is_self_able_modify")
        cuerpo = ast.dump(fn)
        self.assertIn("isdir", cuerpo, "el marcador es el directorio en disco")
        # El except devuelve False: ante la duda, NO se promete nada.
        self.assertTrue(
            any(isinstance(n, ast.Return)
                and isinstance(n.value, ast.Constant) and n.value.value is False
                for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler)
                for n in ast.walk(h)),
            "is_self_able_modify debe fallar CERRADO (return False en el except)")

    def test_el_libro_ya_no_promete_un_repo_inexistente(self):
        libro = leer(os.path.join(RAIZ_REPO, "BookOfTlamatini.md"))
        self.assertIn("todavía no está publicada", libro)
        self.assertIn("todavía no publicado", libro)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
