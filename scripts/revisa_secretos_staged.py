# -*- coding: utf-8 -*-
"""Revisa lo STAGED y aborta el commit si trae una credencial viva.

Lo llama el hook `pre-commit`. Mira `git diff --cached`, es decir exactamente lo
que se va a guardar — no el disco, donde las llaves reales DEBEN estar para que
Tlamatini funcione. Confundir esas dos cosas fue el bug original.

Salida 0 = adelante. Salida 1 = commit abortado, con el archivo y el proveedor
nombrados y la salida exacta escrita.

NUNCA imprime el valor del secreto: un hook que filtra la llave a la consola
(y de ahi al scrollback, y al log de la sesion) es peor que el problema.
"""
import re
import subprocess
import sys

# Formas que un proveedor emite de verdad. Especificas a proposito: un patron
# ancho marcaria cualquier hash de prueba y el hook acabaria desactivado con
# `--no-verify` por costumbre, que es como muere una barrera.
FORMAS = (
    ("Anthropic",     re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI",        re.compile(r"sk-proj-[A-Za-z0-9_\-]{20,}")),
    ("Google/Gemini", re.compile(r"AIza[A-Za-z0-9_\-]{30,}")),
    ("GitHub",        re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}")),
    ("Meta/WhatsApp", re.compile(r"EAA[A-Za-z0-9]{50,}")),
    ("Slack",         re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("Telegram bot",  re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_\-]{30,}")),
)


def main():
    diff = subprocess.run(
        ("git", "diff", "--cached", "--unified=0", "--no-color"),
        capture_output=True, text=True, encoding="utf-8", errors="replace").stdout

    archivo, hallazgos = None, []
    for linea in diff.splitlines():
        if linea.startswith("+++ b/"):
            archivo = linea[6:]
            continue
        if not linea.startswith("+") or linea.startswith("+++"):
            continue
        for proveedor, patron in FORMAS:
            if patron.search(linea):
                # Se guarda el ARCHIVO y el PROVEEDOR. El valor jamas.
                hallazgos.append((archivo or "(desconocido)", proveedor))
                break

    if not hallazgos:
        return 0

    vistos, unicos = set(), []
    for par in hallazgos:
        if par not in vistos:
            vistos.add(par)
            unicos.append(par)

    print("")
    print("  COMMIT ABORTADO: hay credenciales vivas en lo que ibas a guardar.")
    print("")
    for arch, proveedor in unicos:
        print("     %-58s  llave de %s" % (arch, proveedor))
    print("")
    print("  Sacarlas despues NO alcanza: GitHub escanea toda la historia, asi")
    print("  que el push queda bloqueado igual y habria que reescribir commits.")
    print("")
    print("  Salida:")
    print("     python regen_secrets.py --mode push-able     (deja placeholders)")
    print("     git add -u  &&  git commit ...")
    print("     python regen_secrets.py --mode keyed         (te devuelve tus llaves)")
    print("")
    print("  Tus llaves reales viven en data.keys, que no se trackea nunca.")
    print("")
    return 1


if __name__ == "__main__":
    sys.exit(main())
