# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "la que sabe"
#
#   Creado por  Angela López Mendoza   ·   @angelahack1
#   Desarrolladora · Arquitecta · Creadora de Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
"""Lectura rápida de los originales ingleses del commit base (git cat-file --batch)."""
import hashlib
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=2)
def originales_del_parche(ingles, commit, huella):
    """Reconstruye sólo los originales en revisión, sin escribir en ninguno de los repos."""
    if not huella:
        return {}
    if len(huella) != 64 or any(letra not in "0123456789abcdef" for letra in huella):
        raise ValueError("Se esperaba la huella SHA-256 del parche inglés")
    parche = Path(__file__).resolve().parents[1] / "bases" / (huella + ".patch")
    datos = parche.read_bytes()
    if hashlib.sha256(datos).hexdigest() != huella:
        raise ValueError("El parche inglés no corresponde a la huella registrada")
    with tempfile.TemporaryDirectory(prefix="tlamatini-origen-") as tmp:
        orden = ["git", "apply", "--no-index", "-p2", "--whitespace=nowarn"]
        lista = subprocess.check_output([*orden, "--numstat", "-z", str(parche)], cwd=tmp)
        rutas = [fila.split(b"\t", 2)[2].decode("utf-8") for fila in lista.split(b"\0") if fila]
        with OriginalesIngles(ingles, commit) as origen:
            for ruta in rutas:
                destino = (Path(tmp) / ruta).resolve()
                if not destino.is_relative_to(Path(tmp).resolve()):
                    raise ValueError(f"Ruta no válida en el parche: {ruta}")
                anterior = origen.leer(ruta)
                if anterior is not None:
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    destino.write_bytes(anterior)
        subprocess.run([*orden, str(parche)], cwd=tmp, check=True)
        return {ruta: (Path(tmp) / ruta).read_bytes() for ruta in rutas}


class OriginalesIngles:
    def __init__(self, ingles: str | Path, commit: str, parche=None):
        self.commit = commit
        self.parche = originales_del_parche(ingles, commit, parche) if parche else {}
        self._proc = subprocess.Popen(["git", "-C", str(ingles), "cat-file", "--batch"],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def leer(self, ruta: str) -> bytes | None:
        if ruta in self.parche:
            return self.parche[ruta]
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
