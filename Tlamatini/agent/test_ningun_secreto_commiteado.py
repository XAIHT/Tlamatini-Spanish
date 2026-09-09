# -*- coding: utf-8 -*-
"""Que ningun secreto vivo llegue a un commit. Nunca mas.

QUE PASO (2026-09-08): `212b0bd` se llevo 12 secretos vivos porque los nueve
archivos de configuracion estan TRACKEADOS y tienen que contener llaves reales
para que la app funcione. Un `git add -A` normal los mete. No hubo aviso: lo
descubrio el push protection de GitHub cuando ya estaban en la historia local, y
sacarlos exigio reescribir commits.

POR QUE NO SE DES-TRACKEAN Y YA: `config.json` es input de build, es user state
preservado por el self-update, y el arbol INGLES tambien lo trackea. Sacarlo de
git aqui rompe un clone limpio y abre una divergencia permanente con el otro
arbol. La proteccion tiene que vivir en otro lado.

DONDE VIVE, ENTONCES — tres capas, y esta prueba es la que VIAJA:

  1. `skip-worktree` en los nueve archivos: local, inmediato, y no viaja.
  2. El hook `pre-commit`: bloquea el commit en el momento, y tampoco viaja
     (los hooks no se clonan) — por eso existe `scripts/instala_hooks.py`.
  3. ESTA prueba: viaja con el repository y falla en cualquier maquina si lo
     COMMITEADO trae un secreto vivo.

Se mira lo que git tiene guardado (`git show HEAD:<archivo>`), no lo que hay en
disco: en disco DEBE haber llaves reales para que Tlamatini funcione. Confundir
las dos cosas es exactamente lo que hizo falla esto la primera vez.
"""
import json
import os
import re
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Los nueve archivos que llevan credenciales y que git SI trackea.
ARCHIVOS = (
    "Tlamatini/agent/config.json",
    "Tlamatini/agent/external_mcps.json",
    "Tlamatini/agent/agents/telegrammer/config.yaml",
    "Tlamatini/agent/agents/whatsapper/config.yaml",
    "Tlamatini/agent/agents/teletlamatini/config.yaml",
    "Tlamatini/agent/agents/emailer/config.yaml",
    "Tlamatini/agent/agents/recmailer/config.yaml",
    "Tlamatini/agent/agents/zavuerer/config.yaml",
    "Tlamatini/agent/agents/discoverer/config.yaml",
)

# Formas de credencial que un proveedor emite de verdad. Deliberadamente
# especificas: un patron ancho como `[A-Za-z0-9]{20,}` marcaria cualquier hash
# de prueba y la guarda acabaria desactivada.
FORMAS = (
    ("Anthropic",      re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI",         re.compile(r"sk-proj-[A-Za-z0-9_\-]{20,}")),
    ("Google/Gemini",  re.compile(r"AIza[A-Za-z0-9_\-]{30,}")),
    ("GitHub PAT",     re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}")),
    ("Meta/WhatsApp",  re.compile(r"EAA[A-Za-z0-9]{50,}")),
    ("Slack",          re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}")),
)

PLACEHOLDER = re.compile(r"goes here|<[^>]*>|your[_ -]|xxx+|placeholder|example|^$", re.I)
CLAVE = re.compile(r"key|token|secret|password|passwd|credential", re.I)


def _git(*args):
    return subprocess.run(("git", "-C", RAIZ) + args, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


class NingunSecretoCommiteadoTests(unittest.TestCase):
    """Se juzga lo COMMITEADO, no el disco. En disco las llaves deben estar."""

    def _contenido_commiteado(self, rel):
        r = _git("show", "HEAD:%s" % rel)
        return r.stdout if r.returncode == 0 else None

    def test_ningun_archivo_commiteado_trae_una_credencial_reconocible(self):
        hallazgos = []
        for rel in ARCHIVOS:
            texto = self._contenido_commiteado(rel)
            if texto is None:
                continue                      # no trackeado en esta edicion: correcto tambien
            for proveedor, patron in FORMAS:
                if patron.search(texto):
                    hallazgos.append("%s -> parece una credencial de %s" % (rel, proveedor))
        self.assertEqual(
            hallazgos, [], "HAY SECRETOS EN LO COMMITEADO: %s. No los quites con un "
            "commit hacia adelante y ya: GitHub escanea TODA la historia, asi que "
            "el push seguira bloqueado. Rota la llave, y decide con Angela si se "
            "reescribe el commit." % "; ".join(hallazgos))

    def test_ningun_campo_de_credencial_commiteado_tiene_valor(self):
        """Mas amplio que las formas: cualquier campo `*key*`/`*token*` con valor."""
        con_valor = []
        for rel in ARCHIVOS:
            if not rel.endswith(".json"):
                continue
            texto = self._contenido_commiteado(rel)
            if texto is None:
                continue
            try:
                datos = json.loads(texto)
            except ValueError:
                continue

            def recorre(nodo, ruta):
                if isinstance(nodo, dict):
                    for k, v in nodo.items():
                        recorre(v, ruta + [k])
                elif isinstance(nodo, str) and ruta and CLAVE.search(ruta[-1]):
                    if nodo and not PLACEHOLDER.search(nodo):
                        con_valor.append("%s :: %s" % (rel, ".".join(ruta)))

            recorre(datos, [])
        self.assertEqual(
            con_valor, [],
            "estos campos de credencial estan commiteados CON VALOR: %s. Corre "
            "`python regen_secrets.py --mode push-able` antes de commitear; tus "
            "llaves reales viven en `data.keys` y vuelven con `--mode keyed`."
            % "; ".join(con_valor))

    def test_data_keys_nunca_se_trackea(self):
        r = _git("ls-files", "--error-unmatch", "data.keys")
        self.assertNotEqual(
            r.returncode, 0,
            "`data.keys` esta TRACKEADO. Ahi viven todas las llaves reales en "
            "claro: es el unico archivo que no puede entrar a git jamas.")

    def test_el_hook_que_bloquea_el_commit_sigue_existiendo_en_el_repo(self):
        # El hook instalado vive en .git/hooks y no se clona; lo que viaja es la
        # plantilla + el instalador. Si alguien los borra, esto avisa.
        for rel in ("scripts/hooks/pre-commit", "scripts/instala_hooks.py"):
            self.assertTrue(
                os.path.isfile(os.path.join(RAIZ, rel.replace("/", os.sep))),
                "falta `%s`. Sin el, un clone nuevo no tiene como instalar la "
                "barrera que impide commitear una llave viva." % rel)
