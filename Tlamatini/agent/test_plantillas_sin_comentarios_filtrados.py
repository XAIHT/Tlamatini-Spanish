# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""Ninguna nota de trabajo debe llegar a la pantalla de quien usa Tlamatini.

POR QUÉ EXISTE ESTE ARCHIVO (Angela, 2026-08-02): en `welcome.html` había un
comentario de varios renglones escrito con la sintaxis CORTA de Django (llave
seguida de gato). Esa sintaxis es de **UNA SOLA LÍNEA**: repartida en varios
renglones NO comenta nada, así que Django imprimió el comentario entero — una
nota interna sobre género neutro, con rutas de archivo y números de línea —
justo encima del "¡Te damos la bienvenida!". Angela lo vio al iniciar sesión.

Se guardan DOS cosas, porque son fallas distintas:

1. LA SINTAXIS — un comentario corto que abre y no cierra en el MISMO renglón.
   Es la causa mecánica exacta, y se revisa en TODAS las plantillas del
   proyecto, no sólo en la que falló.
2. EL RESULTADO — que el texto realmente visible de una plantilla no contenga
   jerga de nota de trabajo. Esto atrapa la misma falla aunque llegue por otro
   camino (una nota suelta fuera de todo comentario, por ejemplo).

Y además se RENDERIZA `welcome.html` de verdad, con Django, para no confiar en
que "se ve bien en el archivo": lo que importa es lo que sale en pantalla.
"""
from pathlib import Path
import re
import unittest

from django.contrib.auth import get_user_model
from django.test import TestCase


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent

# Directorios que NO son nuestros (Python empaquetado, dependencias, etc.).
NO_NUESTRO = ("node_modules", ".git", "venv", ".venv", "__pycache__",
              "dist", "build", "staticfiles", "python", "jre", "jd-cli")

ABRE_CORTO = "{" + "#"
CIERRA_CORTO = "#" + "}"

# Jerga que jamás debería leer una persona en la interfaz.
JERGA = (
    "GÉNERO NEUTRO", "OJO:", "NOTA:", "TODO:", "FIXME", "XXX:", "HACK:",
    "ui_es.py", "no revertir", "do not revert", "eslint-disable",
)

_RX_COMMENT = re.compile(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", re.S | re.I)
_RX_CORTO = re.compile(r"\{#.*?#\}", re.S)
_RX_HTML = re.compile(r"<!--.*?-->", re.S)
_RX_SCRIPT = re.compile(r"<script\b.*?</script>", re.S | re.I)
_RX_STYLE = re.compile(r"<style\b.*?</style>", re.S | re.I)
_RX_TAG = re.compile(r"<[^>]+>", re.S)


def _nuestras_plantillas():
    """Todas las plantillas .html que escribimos nosotros."""
    for ruta in PROJECT_ROOT.rglob("*.html"):
        if any(parte in NO_NUESTRO for parte in ruta.parts):
            continue
        yield ruta


def _texto_visible(html: str) -> str:
    """Lo que queda tras quitar comentarios, <script>, <style> y las etiquetas."""
    t = _RX_COMMENT.sub(" ", html)
    t = _RX_CORTO.sub(" ", t)
    t = _RX_HTML.sub(" ", t)
    t = _RX_SCRIPT.sub(" ", t)
    t = _RX_STYLE.sub(" ", t)
    return _RX_TAG.sub(" ", t)


def _cortos_sin_cerrar(texto: str):
    """(línea, muestra) donde se ABRE un comentario corto y no cierra ahí mismo."""
    fugas = []
    for numero, linea in enumerate(texto.split("\n"), 1):
        desde = 0
        while True:
            abre = linea.find(ABRE_CORTO, desde)
            if abre == -1:
                break
            cierra = linea.find(CIERRA_CORTO, abre + 2)
            if cierra == -1:
                fugas.append((numero, linea.strip()[:120]))
                break
            desde = cierra + 2
    return fugas


class ComentariosDePlantillaTests(unittest.TestCase):
    """La causa mecánica: el comentario corto multilínea que NO comenta."""

    def test_ningun_comentario_corto_se_reparte_en_varios_renglones(self):
        fugas = []
        revisadas = 0
        for ruta in _nuestras_plantillas():
            revisadas += 1
            texto = ruta.read_text(encoding="utf-8", errors="replace")
            for numero, muestra in _cortos_sin_cerrar(texto):
                relativa = ruta.relative_to(PROJECT_ROOT)
                fugas.append(f"{relativa}:{numero}  ->  {muestra}")
        self.assertGreater(revisadas, 0, "no encontré ninguna plantilla que revisar")
        self.assertEqual(
            fugas, [],
            msg="La sintaxis CORTA de comentario de Django es de UNA SOLA LÍNEA. "
                "Repartida en varios renglones NO comenta: el texto se IMPRIME en "
                "pantalla. Usa la etiqueta comment/endcomment. Fugas:\n  "
                + "\n  ".join(fugas),
        )

    def test_el_texto_visible_no_lleva_jerga_de_nota_de_trabajo(self):
        fugas = []
        for ruta in _nuestras_plantillas():
            visible = _texto_visible(
                ruta.read_text(encoding="utf-8", errors="replace"))
            for marca in JERGA:
                if marca in visible:
                    relativa = ruta.relative_to(PROJECT_ROOT)
                    fugas.append(f"{relativa}  ->  contiene {marca!r}")
        self.assertEqual(
            fugas, [],
            msg="Una nota de trabajo quedó en el texto que la persona LEE:\n  "
                + "\n  ".join(fugas),
        )


class BienvenidaRenderizadaTests(TestCase):
    """El resultado: lo que de verdad sale en pantalla al iniciar sesión."""

    def setUp(self):
        Usuario = get_user_model()
        self.usuario = Usuario.objects.create_user(
            username="angela", password="x-para-la-prueba")  # noqa: S106
        self.client.force_login(self.usuario)

    def test_la_pagina_de_bienvenida_no_filtra_la_nota_de_genero_neutro(self):
        respuesta = self.client.get("/agent/welcome/")
        self.assertEqual(respuesta.status_code, 200)
        html = respuesta.content.decode("utf-8")

        # Lo que SÍ debe verse.
        self.assertIn("Te damos la bienvenida", html)

        # Lo que NUNCA debe verse: la nota interna, en ninguno de sus pedazos.
        for filtrado in ("GÉNERO NEUTRO", "ui_es.py", "OJO:",
                         "endcomment", "{% comment %}"):
            self.assertNotIn(
                filtrado, html,
                msg=f"la página de bienvenida está imprimiendo {filtrado!r} "
                    "— una nota interna llegó a la pantalla de la usuaria",
            )

    def test_el_saludo_es_de_genero_neutro(self):
        """La regla que la nota describía sigue viva, aunque la nota ya no se vea."""
        html = self.client.get("/agent/welcome/").content.decode("utf-8")
        self.assertIn("Te damos la bienvenida", html)
        for con_genero in ("Bienvenido,", "Bienvenida,", "Bienvenida(o)"):
            self.assertNotIn(con_genero, html)


if __name__ == "__main__":
    unittest.main()
