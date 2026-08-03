# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creada por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no quitar
r"""
LAS FOTOS DE LAS PRUEBAS LAS TOMA **SHOTER**, EL AGENT DE TLAMATINI
===================================================================

REGLA DE ANGELA (2026-08-02), SIN EXCEPCIONES
    Está PROHIBIDO usar `PIL.ImageGrab` en las pruebas. Toda captura de
    pantalla la toma el agent **Shoter** de Tlamatini. Punto.

POR QUÉ IMPORTA (no es capricho)
    Las pruebas de Tlamatini se hacen CON Tlamatini. Cuando una prueba se toma
    sus fotos por su cuenta con Pillow, nunca ejercita a Shoter — y los defectos
    de Shoter no aparecen. Fue exactamente lo que pasó: Shoter llamaba a
    `ImageGrab.grab()` SIN `all_screens`, o sea que en una máquina con dos
    monitores capturaba nada más el principal y perdía la mitad del escritorio
    en silencio. Ese hueco vivió ahí hasta que Angela preguntó por qué las
    pruebas no usaban Shoter. Usarlo es la prueba de Shoter.

CÓMO FUNCIONA
    Este módulo es el LANZADOR: copia la plantilla del agent a un directorio de
    trabajo (una sola vez por corrida), le escribe su `config.yaml` con el
    `output_dir`, el `filename` y `all_screens: true`, y ejecuta
    `python shoter.py`. El agent hace el trabajo y deja la imagen donde se le
    pidió. Es el mismo camino que usa Tlamatini en producción.

FAIL-OPEN
    Si Shoter no se puede lanzar, `toma_foto()` devuelve None y lo REPORTA.
    Nunca cae de regreso a Pillow: una prueba sin foto es un problema visible;
    una prueba que miente sobre quién tomó la foto es peor.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

PLANTILLA = r"C:\Development\Tlamatini-Spanish\Tlamatini\agent\agents\shoter"

_RUNTIME: str = ""


def _preparar(runtime_base: str) -> str:
    """Copia la plantilla de Shoter a un directorio de trabajo. Una sola vez."""
    global _RUNTIME
    if _RUNTIME and os.path.isdir(_RUNTIME):
        return _RUNTIME
    destino = os.path.join(runtime_base, "_shoter_runtime")
    if os.path.isdir(destino):
        shutil.rmtree(destino, ignore_errors=True)
    shutil.copytree(PLANTILLA, destino,
                    ignore=shutil.ignore_patterns("__pycache__", "*.log",
                                                  "*.pid", "shoter_*"))
    _RUNTIME = destino
    return destino


def toma_foto(output_dir: str, nombre: str, runtime_base: str = "",
              timeout: int = 60) -> str | None:
    """
    Toma una captura del ESCRITORIO COMPLETO con el agent Shoter.

    output_dir  carpeta donde va la imagen (se crea si falta)
    nombre      nombre exacto del archivo, p. ej. '02_ventana_validar.png'

    Devuelve la ruta absoluta de la imagen, o None si Shoter no pudo.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        base = runtime_base or output_dir
        rt = _preparar(base)

        # config.yaml del agent para ESTA foto
        cfg = os.path.join(rt, "config.yaml")
        with open(cfg, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("output_dir: %s\n" % output_dir.replace("\\", "/"))
            fh.write("all_screens: true\n")
            fh.write("filename: %s\n" % nombre)
            fh.write("target_agents: []\n")

        # encoding utf-8 EXPLICITO: Shoter imprime emoji (📸 🖥️ ✅) y sin esto
        # Python decodifica su salida con la codepage de Windows (cp1252), que
        # no los conoce — el hilo lector truena con UnicodeDecodeError y ensucia
        # la consola aunque la foto sí se haya tomado.
        r = subprocess.run([sys.executable, "shoter.py"], cwd=rt,
                           capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")

        esperada = os.path.join(output_dir, nombre)
        if os.path.isfile(esperada):
            return os.path.abspath(esperada)

        # Shoter escribe su resultado en su propio log; si la ruta esperada no
        # existe, se busca ahí antes de darse por vencido.
        log = os.path.join(rt, os.path.basename(rt) + ".log")
        if os.path.isfile(log):
            for ln in open(log, encoding="utf-8", errors="replace"):
                if "output_path:" in ln:
                    ruta = ln.split("output_path:", 1)[1].strip()
                    if os.path.isfile(ruta):
                        return ruta
        print("   !! Shoter no dejó la foto (%s). rc=%s %s"
              % (nombre, r.returncode, (r.stderr or "")[:120]))
        return None
    except Exception as exc:                      # noqa: BLE001 - fail-open
        print("   !! no se pudo lanzar Shoter para %s: %s" % (nombre, str(exc)[:120]))
        return None
