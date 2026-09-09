# -*- coding: utf-8 -*-
"""Instala los hooks de git de Tlamatini. Correr una vez por clone.

Los hooks viven en `.git/hooks`, que git NO clona — asi que la plantilla viaja
en `scripts/hooks/` y este instalador la copia. Sin esto, un clone nuevo (u otra
maquina de Angela) no tiene la barrera que impide commitear una llave viva.

    python scripts/instala_hooks.py

Tambien marca los nueve archivos de configuracion como `skip-worktree`, para que
`git add -A` no pueda stagearlos aunque contengan las llaves reales que la app
necesita en disco. Las dos capas son distintas: skip-worktree evita el `add`,
el hook evita el `commit`.
"""
import os
import shutil
import stat
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIGS_CON_SECRETOS = (
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


def git(*args):
    return subprocess.run(("git", "-C", RAIZ) + args, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def main():
    hooks_dir = git("rev-parse", "--git-path", "hooks").stdout.strip()
    if not hooks_dir:
        print("no parece un repository git; nada que instalar.")
        return 1
    if not os.path.isabs(hooks_dir):
        hooks_dir = os.path.join(RAIZ, hooks_dir)
    os.makedirs(hooks_dir, exist_ok=True)

    print("hooks ->", hooks_dir)
    instalados = 0
    origen_dir = os.path.join(RAIZ, "scripts", "hooks")
    for nombre in sorted(os.listdir(origen_dir)):
        origen = os.path.join(origen_dir, nombre)
        if not os.path.isfile(origen):
            continue
        destino = os.path.join(hooks_dir, nombre)
        shutil.copyfile(origen, destino)
        # En Windows git-bash igual respeta el bit ejecutable del hook.
        os.chmod(destino, os.stat(destino).st_mode | stat.S_IXUSR | stat.S_IXGRP)
        print("   instalado  %s" % nombre)
        instalados += 1

    print()
    print("marcando los archivos de configuracion como skip-worktree")
    print("(git deja de ver tus cambios locales en ellos, asi que `git add -A`")
    print(" no puede stagear tus llaves reales)")
    marcados = 0
    for rel in CONFIGS_CON_SECRETOS:
        if git("ls-files", "--error-unmatch", rel).returncode != 0:
            continue                      # no trackeado aqui: nada que marcar
        if git("update-index", "--skip-worktree", rel).returncode == 0:
            marcados += 1

    print("   marcados: %d de %d" % (marcados, len(CONFIGS_CON_SECRETOS)))
    print()
    print("listo. %d hook(s) instalado(s)." % instalados)
    print()
    print("Para comprobarlo: pon una llave falsa con forma real en config.json,")
    print("intenta commitearla, y el commit debe abortar solo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
