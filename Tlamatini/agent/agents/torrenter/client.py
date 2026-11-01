# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Transport for the installed Windows Jobs service. Never follows redirects or proxies."""

import base64
import hashlib
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
        )
        return json.loads(result.stdout)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        raise TorrentError(
            "No se pudo acceder al pipe de control de Jobs. Revisa Services en XT y la cuenta del operador de Windows."
        ) from exc


def credential_name(profile):
    return "XAIHT/Tlamatini/Torrenter/" + installation() + "/" + str(uuid.UUID(profile))


def enroll(profile):
    import win32cred

    target = credential_name(profile)
    account = "tlm-" + profile
    data = native(
        {
            "op": "issue",
            "gateway": True,
            "profile": account,
            "scope": "read submit control remove erase",
        }
    ).get("body", {})
    if (
        data.get("account") != account
        or not data.get("signing_key")
        or not data.get("gateway_id")
    ):
        raise TorrentError("Jobs rechazó el registro del gateway.")
    win32cred.CredWrite(
        {
            "Type": win32cred.CRED_TYPE_GENERIC,
            "TargetName": target,
            "UserName": account,
            "CredentialBlob": compact(data),
            "Persist": win32cred.CRED_PERSIST_LOCAL_MACHINE,
        },
        0,
    )
    return account


def scope_grant(profile, directory):
    import win32crypt

    claim = [
        profile,
        installation(),
        str(Path(directory).resolve()),
        int(time.time()) + 8 * 3600,
    ]
    raw = win32crypt.CryptProtectData(
        compact(claim).encode(), "Torrenter activation", None, None, None, 1
    )
    return base64.urlsafe_b64encode(raw).decode("ascii")


def read_grant(directory):
    import win32crypt

    try:
        envelope = base64.urlsafe_b64decode(os.environ["TLAMATINI_TORRENTER_GRANT"])
        _, data = win32crypt.CryptUnprotectData(envelope, None, None, None, 1)
        profile, host, bound, expires = json.loads(data)
        pool = Path(directory).resolve()
        if (
            host == installation()
            and expires >= time.time()
            and (
                Path(bound) == pool
                or (Path(bound) == pool.parent and pool.name.startswith("torrenter_"))
            )
        ):
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
        return res.status, data
    except (OSError, http.client.HTTPException, json.JSONDecodeError) as exc:
        raise TorrentError(
            "No se pudo consultar la API de Jobs. Revisa Services en XT. Si no sabes si se guardó el cambio, reintenta con la misma clave de operación."
        ) from exc
    finally:
        conn.close()


def session(profile):
    """Only the authenticated Windows operator pipe can mint this account-scoped token."""
    account = "tlm-" + str(uuid.UUID(profile))
    response = native({"op": "issue", "profile": account, "scope": "read submit control remove erase"})
    token = response.get("body", {}).get("access_token")
    if not token:
        raise TorrentError("Inicia Jobs y el proveedor Torrenter desde XT.")
    return token
