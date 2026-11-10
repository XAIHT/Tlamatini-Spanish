# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Human-readable operator log. Its private source URIs never enter the model result."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import uuid


def record_directory(profile, pool, node):
    if __package__:
        from .client import private_directory
    else:
        from client import private_directory
    # Pool folders are disposable. Their identity, scoped by the Django account,
    # identifies the canvas node without accepting a browser-supplied file path.
    key = hashlib.sha256((Path(pool).name + "/" + node).encode()).hexdigest()
    return private_directory(profile) / "activity" / key


def latest_record(profile, pool, node):
    folder = record_directory(profile, pool, node)
    try:
        ident = (folder / "latest").read_text(encoding="ascii")
        return folder / (uuid.UUID(hex=ident).hex + ".log")
    except (FileNotFoundError, ValueError):
        return None


class ActivityLog:
    def __init__(self, directory, action, wait, profile=None):
        self.path = directory / (directory.name + ".activity.log")
        folder = None
        if profile and directory.parent.name != "_chat_runs_":
            folder = record_directory(profile, directory.parent, directory.name)
            folder.mkdir(parents=True, exist_ok=True)
            self.path = folder / (uuid.uuid4().hex + ".log")
        self.path.write_text("", encoding="utf-8")
        self.write("TORRENTER", f"Acción: {action}", "Inicio (UTC): " + self.now(),
                   "Esperar a que termine la descarga: " + ("Sí" if wait else "No"))
        if folder:
            pointer = self.path.with_suffix(".pointer")
            pointer.write_text(self.path.stem, encoding="ascii")
            pointer.replace(folder / "latest")

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def write(self, *lines):
        with self.path.open("a", encoding="utf-8") as stream:
            for line in lines:
                print(line, file=stream)

    def assets(self, details):
        self.write("", "TORRENT", details.get("name") or "En espera de los metadatos")
        files = details.get("files") or []
        published = details.get("publication", {})
        if published.get("delivery_state"):
            self.write("Entrega: " + published["delivery_state"])
            if published.get("saved_to"):
                label = "content_generated: " if published.get("delivery_location") == "content_generated" else "Destino en Descargas de Windows: "
                self.write(label + published["saved_to"])
            if published.get("downloads_error"):
                self.write("Windows Downloads: " + published["downloads_error"])
            if published.get("delivery_error"):
                self.write("Error al guardar: " + published["delivery_error"])
        verified = {f["id"]: f for f in published.get("files", [])}
        self.write("ARCHIVOS", f"Archivos en los metadatos: {len(files)}")
        for item in files:
            state = ("seleccionado" if item["selected"] else "excluido") if "selected" in item else "disponible para seleccionar"
            self.write(f'[{item["id"]}] {item["path"]}', f'    {item["size"]:,} bytes · {state}')
            verified_file = verified.get(item["id"])
            if verified_file and published.get("output_root") and published.get("verified"):
                self.write("    Archivo guardado: " + str(Path(published["output_root"]) / verified_file["path"]),
                           "    SHA-256: " + verified_file["sha256"])
        if details.get("magnet"):
            title = "Enlace magnet original" if details["source_kind"] == "magnet" else "Magnet generado a partir del .torrent cargado"
            self.write("", title, details["magnet"])
        self.write("")

    def publication(self, manifest):
        if not manifest.get("verified"):
            self.write("", "SALIDA AÚN NO GUARDADA", manifest.get("delivery_error") or "Esperando la entrega verificada.")
            return
        self.write("", "ARCHIVOS VERIFICADOS")
        for item in manifest["files"]:
            self.write(str(Path(manifest["output_root"]) / item["path"]),
                       f'    {item["size"]:,} bytes', "    SHA-256: " + item["sha256"])

    def swarm(self, state, trackers, web_seeds, peers):
        def value(key, unit=""):
            raw = state.get(key)
            return "sin datos" if raw is None else f"{raw}{unit}"

        self.write("", "TRANSFERENCIA Y ENJAMBRE", "Observación (UTC): " + self.now(),
                   "Job: " + value("job_id"), "Info hash: " + value("info_hash"),
                   "State: " + value("phase") + " / " + value("desired_state"),
                   "Semillas conectadas: " + value("seeds"), "Semillas reportadas por el enjambre: " + value("known_seeds"),
                   "Pares conectados: " + value("peers"), "Pares incompletos reportados: " + value("known_peers"),
                   "Disponibilidad: " + value("availability"), "Proporción compartida: " + value("ratio"),
                   "Velocidad de descarga: " + value("download_rate_bps", " B/s"), "Velocidad de subida: " + value("upload_rate_bps", " B/s"),
                   "Tamaño total: " + value("total_bytes", " bytes"), "Seleccionados: " + value("selected_bytes", " bytes"),
                   "Verificados: " + value("verified_bytes", " bytes"), "ETA: " + value("eta_seconds", " s"),
                   "Destino: " + value("destination_root_id"))
        if state.get("error"):
            self.write("Error actual: " + str(state["error"]))
        if state.get("previous_error"):
            self.write("Error anterior (descarga completada después): " + str(state["previous_error"]))
        if state.get("recovery_note"):
            self.write("Recuperación: " + state["recovery_note"])
        if state.get("restart_action"):
            self.write("Acción de recuperación disponible: " + state["restart_action"])
        if state.get("completed_at"):
            stamp = datetime.fromtimestamp(state["completed_at"], timezone.utc)
            self.write("Completado (UTC): " + stamp.isoformat(timespec="seconds"))
        for heading, entries in (("Trackers", trackers), ("Semillas HTTP", web_seeds), ("Pares conectados (hasta 100)", peers)):
            if entries is None:
                self.write(heading + ": not reported")
            else:
                self.write(f"{heading}: {len(entries)}")
                for entry in entries:
                    self.write("    " + " · ".join(f"{key}={val}" for key, val in entry.items()))

    def receipt(self, result):
        self.write("", "RESULTADO", "Estado: " + str(result["status"]))
        for key in ("job_id", "operation_id", "inspection_id", "operation_key", "phase", "lookup_state", "message"):
            if key in result:
                self.write(f"{key}: {result[key]}")
        self.write("Fin (UTC): " + self.now())

    def response(self, data):
        self.write(json.dumps(data, indent=2, ensure_ascii=False))

