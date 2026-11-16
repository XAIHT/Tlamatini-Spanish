# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Local, authenticated account enrollment for the independent RC service."""

import ipaddress
import logging
import uuid
from urllib.parse import urlsplit

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .models import RemoteControllerProfile
from .remote_controller_bridge import (
    RcBridgeError, bind_profile, enrollment_lock, service_status, unbind_profile,
)

logger = logging.getLogger(__name__)
_enrollment_lock = enrollment_lock

TEXT = {
    "language": "es", "edition": "Edición en español",
    "title": "Remote-Controller", "eyebrow": "TLAMATINI / TLACHIHUANI",
    "intro": "Conecta esta cuenta de Tlamatini con Tlamatini-RC. Tú eliges en XT qué dispositivos pueden usarla.",
    "back": "Volver al chat", "refresh": "Actualizar estado",
    "service": "Servicio Remote-Controller", "ready": "En ejecución", "unavailable": "Sin conexión",
    "setup": "Requiere configuración", "stopping": "Deteniéndose",
    "service_help": "Haz clic derecho en el icono XT → Remote-Controller para iniciar, detener o reiniciar el servidor.",
    "account": "Tu cuenta", "enabled": "Acceso remoto habilitado", "disabled": "Acceso remoto deshabilitado",
    "pending": "El acceso remoto está deshabilitado aquí. La revocación del servicio terminará cuando Remote-Controller esté disponible.",
    "enabled_help": "Los dispositivos aprobados pueden usar los permisos que otorgues en XT. El chat remoto usa el historial y las aprobaciones de ejecución de esta cuenta.",
    "disabled_help": "Habilita esta cuenta antes de crear una invitación para un dispositivo en XT.",
    "password_label": "Confirma tu contraseña actual de Tlamatini", "enable": "Habilitar esta cuenta",
    "disable": "Deshabilitar acceso remoto", "retry": "Reintentar revocación del servicio",
    "consent": "Al habilitarla, esta cuenta estará disponible en XT. Esto no aprueba dispositivos ni inicia servicios.",
    "disable_help": "Al deshabilitarla, se cancela su trabajo remoto y se revoca el acceso de sus dispositivos. Tlamatini permanece abierto.",
    "steps": "Conectar un dispositivo", "step_one": "Habilita esta cuenta aquí y selecciónala en la pestaña Access de Remote-Controller en XT.",
    "step_two": "Elige los permisos y crea una invitación. Abre el cliente RC desde XT e introduce la invitación.",
    "step_three": "Compara la huella completa del dispositivo en ambos lugares y apruébalo en XT.",
    "local_profile": "Esta versión solo se conecta en esta PC. El acceso por red seguirá deshabilitado hasta que esté instalado el transporte seguro requerido.",
    "independence": "Remote-Controller y Torrenter tienen controles separados. Detener uno mantiene independiente al otro.",
    "enabled_notice": "Esta cuenta está lista para crear una invitación en XT.",
    "disabled_notice": "Se revocaron el acceso remoto y los permisos de dispositivos de esta cuenta.",
    "password_error": "La contraseña no coincide. Introduce la contraseña actual de esta cuenta.",
    "request_error": "No se pudo aceptar esta solicitud. Actualiza la página e inténtalo de nuevo.",
    "local_error": "Abre esta página en la PC que ejecuta Tlamatini para administrar el acceso remoto.",
    "service_error": "Remote-Controller no está disponible o rechazó el cambio. Revisa su pestaña Runtime en XT e inténtalo de nuevo.",
    "revoke_first": "Esta cuenta aún tiene acceso de dispositivos que Remote-Controller no ha revocado. Inicia Remote-Controller desde el icono XT y vuelve a habilitar la cuenta.",
    "inactive_error": "Esta cuenta de Tlamatini está inactiva.",
}


def _local_request(request):
    """Trust the actual connection, never a forwarded address supplied by a client."""
    try:
        return ipaddress.ip_address(request.META.get("REMOTE_ADDR", "")).is_loopback
    except ValueError:
        return False


def _same_origin(request):
    origin = request.META.get("HTTP_ORIGIN", "")
    try:
        parsed = urlsplit(origin)
        expected = urlsplit(request.scheme + "://" + request.get_host())
        return (
            bool(origin) and parsed.scheme in {"http", "https"}
            and not parsed.username and not parsed.password
            and not parsed.path and not parsed.query and not parsed.fragment
            and parsed.scheme == expected.scheme
            and parsed.hostname == expected.hostname
            and (parsed.port or (443 if parsed.scheme == "https" else 80))
            == (expected.port or (443 if expected.scheme == "https" else 80))
        )
    except ValueError:
        return False


def _profile_for(user):
    return RemoteControllerProfile.objects.filter(user=user).first()


def _page(request, *, error="", notice="", status=200):
    profile = _profile_for(request.user)
    service_label = TEXT["unavailable"]
    service_ready = False
    try:
        observed = service_status()
        health = observed.get("health")
        service_ready = health == "ready" and observed.get("listener") is True
        service_label = TEXT["ready"] if service_ready else TEXT.get(
            {"stopping": "stopping", "setup_required": "setup"}.get(health, "unavailable")
        )
    except RcBridgeError:
        pass
    response = render(request, "agent/remote_controller.html", {
        "copy": TEXT, "profile": profile, "error": error, "notice": notice,
        "service_label": service_label, "service_ready": service_ready,
        "pending_revocation": bool(profile and not profile.enabled and profile.binding_id),
    }, status=status)
    response["Cache-Control"] = "no-store, private"
    # Same-origin form posts must retain their Origin for strict CSRF checks.
    # No account detail or password is placed in the page URL.
    response["Referrer-Policy"] = "same-origin"
    response["X-Frame-Options"] = "DENY"
    return response


@login_required
@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def account(request):
    if not _local_request(request):
        return HttpResponseForbidden(TEXT["local_error"])
    if not request.user.is_active:
        return HttpResponseForbidden(TEXT["inactive_error"])
    if request.method == "GET":
        return _page(request)
    if (not _same_origin(request) or request.content_type != "application/x-www-form-urlencoded"
            or len(request.body) > 8192):
        return HttpResponseForbidden(TEXT["request_error"])
    if (set(request.POST) - {"action", "password", "csrfmiddlewaretoken"}
            or any(len(request.POST.getlist(key)) != 1 for key in request.POST)):
        return _page(request, error=TEXT["request_error"], status=400)
    action = request.POST.get("action")
    if action not in {"enable", "disable"}:
        return _page(request, error=TEXT["request_error"], status=400)
    if action == "enable":
        password = request.POST.get("password", "")
        if not password or len(password) > 4096 or not request.user.check_password(password):
            return _page(request, error=TEXT["password_error"], status=403)

    # Enrollment is rare. Serialize local changes so two tabs cannot race a
    # successful enable against a disable for the same authenticated account.
    with _enrollment_lock:
        profile = _profile_for(request.user)
        if action == "enable":
            if profile is None:
                profile, _ = RemoteControllerProfile.objects.get_or_create(user=request.user)
            if not profile.enabled and profile.binding_id:
                # A disable whose service revocation never finished must finish
                # first. Binding again could otherwise restore the old device
                # grants that disabling promised to revoke.
                try:
                    unbind_profile(profile)
                except RcBridgeError as exc:
                    if exc.code != "not_found":
                        logger.warning("Remote-Controller re-enable is waiting for a pending revocation")
                        return _page(request, error=TEXT["revoke_first"], status=503)
                profile.binding_id = ""
                profile.save(update_fields=["binding_id"])
            try:
                binding = bind_profile(profile)
                binding_id = binding.get("id", "")
                if len(binding_id) != 32 or uuid.UUID(hex=binding_id).int == 0:
                    raise ValueError("Invalid native account binding")
                profile.binding_id = binding_id
                profile.enabled = True
                profile.save(update_fields=["binding_id", "enabled"])
            except (RcBridgeError, ValueError, TypeError):
                logger.warning("Remote-Controller account enrollment was not completed")
                return _page(request, error=TEXT["service_error"], status=503)
            return _page(request, notice=TEXT["enabled_notice"])

        if profile is not None:
            # Persist local denial before any native request. The worker also
            # retries disabled profiles with an outstanding service binding.
            profile.enabled = False
            profile.save(update_fields=["enabled"])
            if profile.binding_id:
                try:
                    unbind_profile(profile)
                    profile.binding_id = ""
                    profile.save(update_fields=["binding_id"])
                except RcBridgeError:
                    return _page(request, error=TEXT["pending"], status=503)
        return _page(request, notice=TEXT["disabled_notice"])


@never_cache
@require_http_methods(["GET"])
def session_identity(request):
    """Confirm a normal Django login against an enrolled immutable RC account.

    The mobile gateway uses this read-only check; it never fabricates a Django
    session or substitutes a display name for the account identity.
    """
    from django.http import JsonResponse
    from .remote_controller_bridge import EDITION
    if not _local_request(request):
        return HttpResponseForbidden(TEXT["local_error"])
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False}, status=401)
    profile = _profile_for(request.user)
    return JsonResponse({
        "authenticated": True, "active": bool(request.user.is_active),
        "enabled": bool(profile and profile.enabled), "edition": EDITION,
        "account_id": profile.account.hex if profile else None,
        "binding_id": profile.binding_id if profile else None,
    })
