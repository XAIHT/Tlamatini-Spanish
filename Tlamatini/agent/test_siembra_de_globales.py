# -*- coding: utf-8 -*-
"""Que un agent NUNCA ignore en silencio lo que Angela configuro.

EL BUG QUE ESTO EXISTE PARA MATAR (PDFer, encontrado el 2026-09-09):
`_seed_global_agent_defaults` es una cadena de `if template_dir == "x"` escrita
a mano. A PDFer le faltaba su rama, asi que `ollama_design` y `ollama_polish`
hablaban con `localhost:11434` aunque `config.json` apuntara a otro lado.
No hubo error, ni log, ni un test rojo: el agent consultaba el cerebro
equivocado y decia que todo bien.

Una rama que falta no se queja. Por eso la comprobacion no puede ser "¿esta la
rama escrita?" sino **"¿llega el valor?"**: se LLAMA a la funcion con un
`config.json` de mentira y se mira lo que devuelve. Asi la prueba no se puede
engañar con un `if` que parsea bien y no hace nada.

TRES INVARIANTES:

  1. Todo agent que declare `ollama_url` en su `config.yaml` recibe el endpoint
     y el token configurados. Es la forma exacta del bug de PDFer.
  2. A Talker, Whisperer y LaTeXer NO se les siembra un modelo. Cada uno corre
     un modelo de OTRA especie — Orpheus (voz), faster-whisper (tamaño) y
     `repair_model` — y pisarlos con el modelo de chat rompe al agent mientras
     lo hace parecer configurado. Ese seria el mismo bug al reves.
  3. Un placeholder `<...>` nunca se siembra: un token falso convierte una
     llamada anonima que funcionaba en un rechazo por autenticacion.
"""
import io
import os
import unittest
from unittest import mock

import yaml

from agent import tools

_AGENTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents")

# Agents que declaran `ollama_url` pero NO deben recibirlo, con su motivo.
# Vacio a proposito: hoy no hay ninguno. Si mañana lo hay, se escribe aqui con
# la razon, no se afloja la prueba.
EXENTOS = {}


def _config_yaml(agente):
    ruta = os.path.join(_AGENTS, agente, "config.yaml")
    try:
        return yaml.safe_load(io.open(ruta, encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}


def _agents_que_hablan_con_ollama():
    """Los que declaran `ollama_url`: leido del disco, no de una lista a mano."""
    encontrados = []
    for nombre in sorted(os.listdir(_AGENTS)):
        if not os.path.isdir(os.path.join(_AGENTS, nombre)):
            continue
        if "ollama_url" in _config_yaml(nombre):
            encontrados.append(nombre)
    return encontrados


class SiembraDeGlobalesTests(unittest.TestCase):

    #: valores de mentira, reconocibles a simple vista en un fallo
    FALSO = {
        "ollama_base_url": "http://ollama-de-prueba:9999",
        "ollama_token": "token-de-prueba-123",
        "unified_agent_model": "modelo-de-chat-de-prueba",
    }

    def _sembrar(self, agente, config=None):
        """Llama al sembrador con un config.json de mentira y devuelve el runtime."""
        runtime = dict(config or {})
        valores = dict(self.FALSO)
        with mock.patch.object(tools, "get_config_value",
                               side_effect=lambda k, d="": valores.get(k, d)):
            return tools._seed_global_agent_defaults(agente, runtime)

    # ── Invariante 1 ───────────────────────────────────────────────────────
    def test_todo_agent_que_habla_con_ollama_recibe_el_endpoint_configurado(self):
        hablan = _agents_que_hablan_con_ollama()
        self.assertGreaterEqual(
            len(hablan), 4,
            "se esperaban al menos 4 agents con `ollama_url` (pdfer, talker, "
            "whisperer, latexer); se encontraron %d — ¿cambio la ruta de "
            "agents/ o el nombre del campo?" % len(hablan))

        sin_sembrar = []
        for agente in hablan:
            if agente in EXENTOS:
                continue
            salida = self._sembrar(agente)
            if salida.get("ollama_url") != self.FALSO["ollama_base_url"]:
                sin_sembrar.append(agente)

        self.assertEqual(
            sin_sembrar, [],
            "estos agents declaran `ollama_url` y NO reciben el `ollama_base_url` "
            "de config.json: %s. Van a hablar con su default cableado aunque "
            "Angela haya configurado otro endpoint, y no lo van a decir. "
            "Agrega su rama en `_seed_global_agent_defaults` o declaralo en "
            "EXENTOS con el motivo." % ", ".join(sin_sembrar))

    def test_el_token_configurado_tambien_llega(self):
        sin_token = [a for a in _agents_que_hablan_con_ollama()
                     if a not in EXENTOS
                     and self._sembrar(a).get("ollama_token") != self.FALSO["ollama_token"]]
        self.assertEqual(
            sin_token, [],
            "estos agents no reciben `ollama_token`: %s. Contra un Ollama que "
            "pide autenticacion fallan, y el mensaje no dira que falto el token."
            % ", ".join(sin_token))

    # ── Invariante 2 ───────────────────────────────────────────────────────
    def test_no_se_pisa_el_modelo_de_un_agent_que_corre_otra_especie_de_modelo(self):
        # Talker corre una voz Orpheus, Whisperer un tamaño de faster-whisper,
        # LaTeXer un `repair_model`. Ninguno es el modelo de chat.
        for agente, campo, propio in (("talker", "model", "legraphista"),
                                      ("whisperer", "model", "base"),
                                      ("latexer", "repair_model", "glm")):
            with self.subTest(agente=agente):
                salida = self._sembrar(agente)
                self.assertNotEqual(
                    salida.get(campo), self.FALSO["unified_agent_model"],
                    "a `%s` se le sembro el modelo de chat en `%s`. Ese agent "
                    "corre un modelo de OTRA especie (%s...): pisarlo lo rompe "
                    "y ademas lo hace parecer bien configurado." % (agente, campo, propio))

    # ── Invariante 3 ───────────────────────────────────────────────────────
    def test_un_placeholder_nunca_se_siembra(self):
        valores = {"ollama_base_url": "http://ollama-de-prueba:9999",
                   "ollama_token": "<OLLAMA_TOKEN goes here>"}
        with mock.patch.object(tools, "get_config_value",
                               side_effect=lambda k, d="": valores.get(k, d)):
            salida = tools._seed_global_agent_defaults("pdfer", {})
        self.assertNotIn(
            "ollama_token", salida,
            "se sembro un placeholder como token. Un token falso es PEOR que "
            "ninguno: convierte una llamada anonima que funcionaba en un "
            "rechazo por autenticacion.")

    # ── Lo que ya se sembraba sigue sembrandose ───────────────────────────
    def test_pdfer_sigue_recibiendo_endpoint_modelo_y_token(self):
        salida = self._sembrar("pdfer")
        self.assertEqual(salida.get("ollama_url"), self.FALSO["ollama_base_url"])
        self.assertEqual(salida.get("ollama_model"), self.FALSO["unified_agent_model"],
                         "PDFer SI debe recibir el modelo de chat: su consulta de "
                         "diseño usa el modelo por defecto de Tlamatini.")
        self.assertEqual(salida.get("ollama_token"), self.FALSO["ollama_token"])

    def test_lo_que_el_llamador_ya_puso_gana_sobre_lo_global(self):
        # La siembra ocurre ANTES de las asignaciones del LLM, pero un valor
        # explicito en el runtime no debe perderse si el global esta vacio.
        with mock.patch.object(tools, "get_config_value", side_effect=lambda k, d="": ""):
            salida = tools._seed_global_agent_defaults(
                "talker", {"ollama_url": "http://el-que-pidio-el-usuario:1234"})
        self.assertEqual(
            salida.get("ollama_url"), "http://el-que-pidio-el-usuario:1234",
            "un global vacio borro el valor que ya traia el runtime")
