# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Lectura rápida de los originales ingleses del commit base (git cat-file --batch)."""
import subprocess
from pathlib import Path


class OriginalesIngles:
    def __init__(self, ingles: str | Path, commit: str):
        self.commit = commit
        self._proc = subprocess.Popen(["git", "-C", str(ingles), "cat-file", "--batch"],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def leer(self, ruta: str) -> bytes | None:
        self._proc.stdin.write(f"{self.commit}:{ruta}\n".encode("utf-8"))
        self._proc.stdin.flush()
        cabecera = self._proc.stdout.readline().split()
        if len(cabecera) < 3 or cabecera[1] == b"missing":
            return None
        datos = self._proc.stdout.read(int(cabecera[2]))
        self._proc.stdout.read(1)
        return datos

    def cerrar(self):
        if self._proc.stdin:
            self._proc.stdin.close()
        self._proc.wait()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.cerrar()
