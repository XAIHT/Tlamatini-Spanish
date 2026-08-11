# ═══════════════════════════════════════════════════════════════════
#   ✦  T L A M A T I N I  ✦   —   "one who knows"
#
#   Created by  Angela López Mendoza   ·   @angelahack1
#   Developer · Architect · Creator of Tlamatini
# ═══════════════════════════════════════════════════════════════════
#   Tlamatini Author Banner — do not remove
"""Daily backup of Tlamatini's database."""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import sqlite3
import sys
import traceback

REPO = os.path.dirname(os.path.abspath(__file__))
LIVE_DB = os.path.join(REPO, "Tlamatini", "db.sqlite3")
DEST_DIR = os.path.join(REPO, "Backups")
LOG_PATH = os.path.join(DEST_DIR, "backup_db.log")

# Tablas cuyo conteo se registra: si un día el respaldo trae 0 usuarios,
# el log lo va a estar gritando desde antes de que haga falta restaurar.
CHECK_TABLES = ("auth_user", "agent_prompt", "agent_agent", "agent_tool",
                "agent_skill", "django_migrations")


def log(msg: str) -> None:
    line = "%s  %s" % (_dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    try:
        os.makedirs(DEST_DIR, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def verificar(path: str) -> tuple[bool, dict]:
    """Abre el respaldo de verdad y lo revisa. Devuelve (ok, conteos)."""
    conteos: dict = {}
    try:
        con = sqlite3.connect(path)
        try:
            estado = con.execute("pragma integrity_check").fetchone()[0]
            if estado != "ok":
                log("!! integrity_check dijo: %s" % estado)
                return False, conteos
            for t in CHECK_TABLES:
                try:
                    conteos[t] = con.execute(
                        "select count(*) from %s" % t).fetchone()[0]
                except sqlite3.Error:
                    conteos[t] = -1
        finally:
            con.close()
    except Exception as exc:
        log("!! no pude verificar el respaldo: %s" % exc)
        return False, conteos
    return True, conteos


def podar(keep: int) -> None:
    """Conserva los `keep` respaldos más nuevos y borra el resto."""
    try:
        archivos = sorted(
            (os.path.join(DEST_DIR, f) for f in os.listdir(DEST_DIR)
             if f.startswith("db_") and f.endswith(".sqlite3")),
            key=os.path.getmtime, reverse=True)
    except OSError:
        return
    for viejo in archivos[keep:]:
        try:
            os.remove(viejo)
            log("   podado: %s" % os.path.basename(viejo))
        except OSError as exc:
            log("   no pude podar %s: %s" % (os.path.basename(viejo), exc))


def respaldar(keep: int) -> int:
    if not os.path.isfile(LIVE_DB):
        log("!! NO existe la DB viva: %s" % LIVE_DB)
        return 2

    # Se niega a respaldar una DB rota: con retencion, guardar basura
    # empuja fuera la ultima copia buena.
    try:
        tam = os.path.getsize(LIVE_DB)
    except OSError as exc:
        log("!! ME NIEGO: no puedo leer el tamaño de la DB viva: %s" % exc)
        return 2
    if tam <= 0:
        log("!! ME NIEGO: la DB viva está vacía (0 bytes)")
        return 2

    ok_viva, conteos_viva = verificar(LIVE_DB)
    if not ok_viva:
        log("!! ME NIEGO: la DB viva no pasó la verificación")
        return 2
    if conteos_viva.get("auth_user", -1) == 0:
        log("!! ME NIEGO: la DB viva tiene CERO usuarios - no es algo que se deba guardar")
        return 2

    os.makedirs(DEST_DIR, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(DEST_DIR, "db_%s.sqlite3" % stamp)

    try:
        # modo read-only sobre la DB viva: jamás la tocamos para escribir.
        uri = "file:%s?mode=ro" % LIVE_DB.replace("\\", "/")
        src = sqlite3.connect(uri, uri=True)
        dst = sqlite3.connect(dest)
        try:
            with dst:
                src.backup(dst)
        finally:
            dst.close()
            src.close()
    except Exception:
        log("!! FALLÓ el respaldo:\n%s" % traceback.format_exc())
        try:
            if os.path.exists(dest):
                os.remove(dest)          # no dejes un respaldo a medias
        except OSError:
            pass
        return 1

    ok, conteos = verificar(dest)
    if not ok:
        log("!! el respaldo salió CORRUPTO, lo borro: %s" % dest)
        try:
            os.remove(dest)
        except OSError:
            pass
        return 1

    mb = os.path.getsize(dest) / 1048576.0
    log("respaldo OK  %s  (%.2f MB)" % (os.path.basename(dest), mb))
    log("   " + "  ".join("%s=%d" % (t, conteos.get(t, -1)) for t in CHECK_TABLES))
    if conteos.get("auth_user", 0) == 0:
        log("   ⚠️ OJO: el respaldo NO trae ningún usuario "
            "(no vas a poder entrar si restauras esto).")
    podar(keep)
    return 0


def revisar_ultimo() -> int:
    try:
        archivos = sorted(
            (os.path.join(DEST_DIR, f) for f in os.listdir(DEST_DIR)
             if f.startswith("db_") and f.endswith(".sqlite3")),
            key=os.path.getmtime, reverse=True)
    except OSError:
        archivos = []
    if not archivos:
        log("no hay ningún respaldo todavía.")
        return 1
    ultimo = archivos[0]
    ok, conteos = verificar(ultimo)
    log("%s  %s  %s" % ("OK " if ok else "MAL", os.path.basename(ultimo),
                        "  ".join("%s=%d" % (t, conteos.get(t, -1))
                                  for t in CHECK_TABLES)))
    log("respaldos guardados: %d" % len(archivos))
    return 0 if ok else 1


ALARMA_PATH = os.path.join(REPO, ".backup_status")


def _prender_alarma(rc: int) -> None:
    """Deja una marca mientras el respaldo falla; la borra al primer exito."""
    try:
        if rc == 0:
            if os.path.exists(ALARMA_PATH):
                os.remove(ALARMA_PATH)
            return
        with open(ALARMA_PATH, "w", encoding="utf-8") as fh:
            fh.write(
                "respaldo: no completado (codigo %d)\n"
                "ultimo intento: %s\n"
                "detalles: Backups/backup_db.log\n"
                "se borra solo en el proximo respaldo exitoso\n"
                % (rc, _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    except OSError:
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Respaldo diario de la DB de Tlamatini")
    ap.add_argument("--keep", type=int, default=30,
                    help="cuántos respaldos conservar (default 30)")
    ap.add_argument("--check", action="store_true",
                    help="sólo verifica el respaldo más reciente")
    args = ap.parse_args()
    if args.check:
        return revisar_ultimo()
    rc = respaldar(max(1, args.keep))
    _prender_alarma(rc)
    return rc


if __name__ == "__main__":
    sys.exit(main())
