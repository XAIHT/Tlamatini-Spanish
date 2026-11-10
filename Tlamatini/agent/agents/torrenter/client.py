# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Transport for the installed Windows Jobs service. Never follows redirects or proxies."""

import base64
import http.client
import json
import os
import subprocess
import time
import uuid
from pathlib import Path

if __package__:
    from .contract import TorrentError
else:
    from contract import TorrentError


def compact(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True)


# A copied pool agent runs under the carried Python. Its current directory and
# executable are not the application's output root. Carry the server's choice
# in the existing protected activation grant instead of accepting a browser path.
_pool_content_root = None


def content_root():
    if __package__:
        from ...rag.config import default_application_path

        return str(Path(default_application_path()) / "content_generated")
    return _pool_content_root


def issue(profile, **options):
    request_data = {"op": "issue", "profile": profile, **options}
    root = content_root()
    if root:
        request_data["application_content_root"] = root
    return native(request_data)


def private_directory(profile):
    """Edition-owned private data; no home-directory lookup or Windows temp fallback."""
    root = content_root()
    if not root:
        raise TorrentError("Vuelve a abrir Torrenter desde esta edición para renovar su activación.")
    base = Path(root).parent / "TorrenterData"
    account = base / str(uuid.UUID(profile))
    try:
        if account.resolve() != account:
            raise OSError("Redirected application data directory.")
        base.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            import pywintypes
            import win32api
            import win32file
            import win32security as sec

            token = sec.OpenProcessToken(win32api.GetCurrentProcess(), 8)
            sid = sec.ConvertSidToStringSid(sec.GetTokenInformation(token, sec.TokenUser)[0])
            attrs = pywintypes.SECURITY_ATTRIBUTES()
            attrs.SECURITY_DESCRIPTOR = sec.ConvertStringSecurityDescriptorToSecurityDescriptor(
                f"D:P(A;OICI;FA;;;{sid})(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)", 1)
            try:
                win32file.CreateDirectory(str(account), attrs)
            except pywintypes.error as exc:
                if exc.winerror != 183:
                    raise
            if not account.is_dir() or account.resolve(strict=True) != account:
                raise OSError("Invalid account data directory.")
            descriptor = sec.GetFileSecurity(str(account), sec.OWNER_SECURITY_INFORMATION | sec.DACL_SECURITY_INFORMATION)
            allowed = {sid, "S-1-5-18", "S-1-5-32-544"}
            acl = descriptor.GetSecurityDescriptorDacl()
            if (acl is None or not descriptor.GetSecurityDescriptorControl()[0] & 0x1000
                    or sec.ConvertSidToStringSid(descriptor.GetSecurityDescriptorOwner()) not in allowed
                    or any(sec.ConvertSidToStringSid(acl.GetAce(i)[-1]) not in allowed for i in range(acl.GetAceCount()))):
                raise OSError("The account data directory is not private.")
        else:
            account.mkdir(mode=0o700, exist_ok=True)
    except OSError as exc:
        raise TorrentError("No se puede acceder a la carpeta TorrenterData de esta edición: " + str(account)) from exc
    return account


def known_folder(folder_id):
    from win32com.shell import shell

    return Path(shell.SHGetFolderPath(0, folder_id, 0, 0))


def installation():
    try:
        ident = json.loads(
            (known_folder(35) / "XAIHT/Tlachihuani.Jobs/installation.json").read_text(
                encoding="utf-8-sig"
            )
        )
        return str(uuid.UUID(ident["installation_id"]))
    except (OSError, ValueError, KeyError) as exc:
        raise TorrentError(
            "Instala Tlachihuani Jobs e inicia su proveedor Torrenter desde XT."
        ) from exc


def native(request):
    binary = known_folder(38) / "XAIHT/Tlachihuani/Jobs/Tlachihuani.Jobs.exe"
    try:
        result = subprocess.run(
            [str(binary), "--control"],
            input=compact(request),
            text=True,
            capture_output=True,
            timeout=12,
            check=True,
            # Internal IPC helper: a windowless agent must never allocate a console
            # for each credential refresh. Developer test consoles stay visible.
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        return json.loads(result.stdout)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        raise TorrentError(
            "No se pudo acceder al pipe de control de Jobs. Revisa Services en XT y la cuenta del operador de Windows."
        ) from exc


def scope_grant(profile, directory):
    import win32crypt

    claim = [
        profile,
        installation(),
        str(Path(directory).resolve()),
        int(time.time()) + 8 * 3600,
        content_root(),
    ]
    raw = win32crypt.CryptProtectData(
        compact(claim).encode(), "Torrenter activation", None, None, None, 1
    )
    return base64.urlsafe_b64encode(raw).decode("ascii")


def read_grant(directory):
    import win32crypt
    global _pool_content_root
    _pool_content_root = None

    try:
        envelope = base64.urlsafe_b64decode(os.environ["TLAMATINI_TORRENTER_GRANT"])
        _, data = win32crypt.CryptUnprotectData(envelope, None, None, None, 1)
        profile, host, bound, expires, *roots = json.loads(data)
        pool = Path(directory).resolve()
        if (
            host == installation()
            and expires >= time.time()
            and (
                Path(bound) == pool
                or (Path(bound) == pool.parent and pool.name.startswith("torrenter_"))
            )
        ):
            if roots and roots[0] and Path(roots[0]).is_absolute() and Path(roots[0]).name == "content_generated":
                _pool_content_root = roots[0]
            elif not roots:
                # Already installed controllers can issue an older four-field
                # grant. Follow its authenticated pool to the real install,
                # never the Windows owner's home or the process working directory.
                for parent in pool.parents:
                    if ((parent / "runtime-assets.json").is_file()
                            and (parent / "config.json").is_file()
                            and pool.is_relative_to(parent / "agents")):
                        _pool_content_root = str(parent / "content_generated")
                        break
            return str(uuid.UUID(profile))
    except Exception:
        pass
    raise TorrentError(
        "Esta activación necesita una sesión de Tlamatini. Iníciala desde el chat o Agentic Control Panel."
    )


class JobsHttpError(TorrentError):
    def __init__(self, status, message):
        self.status = status
        super().__init__(message)


def publication_status(data):
    """An older service's verified private copy is not a delivered Downloads file."""
    if "job_id" in data and "selected_bytes" in data and "phase" in data:
        data = dict(data)
        complete = bool(data.get("completed_at"))
        data["download_complete"] = complete
        if complete and data["phase"] in ("completed", "stopped", "paused"):
            # Older Jobs snapshots retained a cleared verification error and
            # displayed the stopped peer session as an unfinished download.
            if data["phase"] != "completed":
                data["transfer_state"] = data["phase"]
            data["phase"] = "completed"
            if data.get("error"):
                data["previous_error"] = data.pop("error")
        phase = data["phase"]
        data["restart_action"] = "recheck" if phase == "failed" else None if complete else {
            "stopped": "start", "paused": "resume", "failed": "recheck",
        }.get(phase)
        data["recovery_note"] = (
            "Recheck verifica las piezas conservadas y reintenta. Consulta primero el error actual."
            if phase == "failed" else
            "Descarga terminada; no necesita reiniciarse. Consulta el manifiesto para localizar los archivos guardados."
            if complete else
            "En cola para otro intento tras ceder su espacio por falta de progreso."
            if data.get("queue_reason") == "stalled_retry" else
            "Sin pares conectados ahora. Las semillas reportadas no son semillas conectadas; reiniciar no garantiza disponibilidad."
            if phase == "waiting_for_peers" else
            "Start continúa con los archivos parciales conservados; no descarga otra copia."
            if phase == "stopped" else
            "Resume continúa esta descarga pausada."
            if phase == "paused" else ""
        )
    if isinstance(data.get("items"), list):
        data = {**data, "items": [publication_status(item) if isinstance(item, dict) else item
                                  for item in data["items"]]}
    if "output_root" in data and data.get("delivery_state") in (None, "service_store"):
        data = {**data, "download_verified": data.get("verified", False),
                "verified": False, "delivery_state": "unavailable",
                "delivery_error": "Actualiza Tlachihuani Jobs para guardar los archivos verificados en Descargas de Windows."}
    if isinstance(data.get("publication"), dict):
        data = {**data, "publication": publication_status(data["publication"])}
    return data


def request(method, path, body=None, *, bearer=None, key=None, revision=None):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if bearer:
        headers["Authorization"] = "Bearer " + bearer
    if key:
        headers["Idempotency-Key"] = key
    if revision is not None:
        headers["If-Match"] = '"' + str(revision) + '"'
    conn = http.client.HTTPConnection("127.0.0.1", 12064, timeout=10)
    try:
        conn.request(
            method,
            "/api/v1/" + path,
            compact(body).encode() if body is not None else None,
            headers,
        )
        res = conn.getresponse()
        raw = res.read(4 * 1024 * 1024 + 1)
        if len(raw) > 4 * 1024 * 1024:
            raise TorrentError(
                "La respuesta de Jobs supera el límite. Solicita una página más pequeña."
            )
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise TorrentError("Jobs devolvió una respuesta inesperada.")
        if not 200 <= res.status < 300:
            if (res.status == 409 and method == "POST" and path == "torrents"
                    and data.get("error") == "Wait for reviewed metadata."):
                raise JobsHttpError(409,
                    "Jobs HTTP 409. No se envió ninguna descarga. Primero consulta list para ver si el job ya existe. "
                    "Consulta inspection con el mismo inspection_id hasta que esté listo y muestre los archivos. "
                    "Si caducó, inspecciona el magnet original completo como source_ref para conservar los trackers. "
                    "No inventes ID ni repitas download mientras se resuelven los metadatos."
                )
            advice = {
                401: "Abre el espacio de descargas desde tu sesión de Tlamatini.",
                403: "Revisa los permisos de acceso o la aprobación de los archivos específicos en XT.",
                404: "Comprueba que el ID pertenezca a tu cuenta.",
                409: "Consulta el job o la operación actual antes de reintentar.",
                412: "Consulta la revisión más reciente antes de modificar el job.",
            }
            raise JobsHttpError(res.status,
                f"Jobs HTTP {res.status}. {str(data.get('error', 'Solicitud rechazada.'))[:250]} {advice.get(res.status, '')}".strip()
            )
        return res.status, publication_status(data)
    except (OSError, http.client.HTTPException, json.JSONDecodeError) as exc:
        raise TorrentError(
            "No se pudo consultar la API de Jobs. Revisa Services en XT. Si no sabes si se guardó el cambio, reintenta con la misma clave de operación."
        ) from exc
    finally:
        conn.close()


def session(profile):
    """Only the authenticated Windows operator pipe can mint this account-scoped token."""
    account = "tlm-" + str(uuid.UUID(profile))
    response = issue(account, scope="read submit control remove erase")
    token = response.get("body", {}).get("access_token")
    if not token:
        raise TorrentError("Inicia Jobs y el proveedor Torrenter desde XT.")
    return token
