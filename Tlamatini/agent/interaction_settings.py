# Tlamatini Author Banner — Angela López Mendoza · @angelahack1
"""Account preferences for real editor/terminal actions; presentation stays local."""
from __future__ import annotations

import json
import math

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


# The API supplies this same schema to the dialog. No parallel browser defaults.
FIELDS = {
    "editor_wpm": dict(tab="editor", label="Velocidad de escritura (WPM)", default=100, min=40, max=250, step=1),
    "link_speeds": dict(tab="editor", label="Usar la misma velocidad de escritura para ambos", default=False),
    "segment_pause": dict(tab="editor", label="Pausa después de cada segmento (segundos)", default=0, min=0, max=3, step=.1),
    "teaching_detail": dict(tab="editor", label="Nivel de detalle de la enseñanza", default="balanced", options={"brief": "Breve", "balanced": "Equilibrado", "detailed": "Detallado"}),
    "suggestions": dict(tab="editor", label="Ofrecer sugerencias para cada campo nuevo", default=True),
    "suggestion_display": dict(tab="editor", label="Presentación de las sugerencias", default="both", options={"both": "Texto fantasma y opciones", "choices": "Solo opciones"}),
    "follow_typing": dict(tab="editor", label="Seguir la escritura de Tlamatini", default=True),
    "editor_font": dict(tab="editor", label="Tamaño de letra del Editor (px)", default=13, min=12, max=24, step=1, local=True),
    "line_numbers": dict(tab="editor", label="Mostrar números de línea", default=True, local=True),
    "wrap": dict(tab="editor", label="Ajustar las líneas largas", default=False, local=True),
    "terminal_wpm": dict(tab="terminal", label="Velocidad de escritura (WPM)", default=50, min=20, max=250, step=1),
    "shell": dict(tab="terminal", label="Shell predeterminado", default="powershell", options={"powershell": "PowerShell", "cmd": "CMD", "pwsh": "PowerShell 7"}),
    "execution": dict(tab="terminal", label="Ejecución del comando", default="task", options={"task": "Seguir las instrucciones de la tarea", "manual": "Yo siempre presiono Enter"}),
    "advisor": dict(tab="terminal", label="Activar el asesor en las nuevas terminales", default=True),
    "wait_seconds": dict(tab="terminal", label="Ventana de espera del comando (segundos)", default=120, min=1, max=3600, step=1, advanced=True),
    "hang_seconds": dict(tab="terminal", label="Umbral sin output (segundos)", default=45, min=3, max=3600, step=1, advanced=True),
    "user_wait_seconds": dict(tab="terminal", label="Espera de traspaso al usuario (segundos)", default=300, min=5, max=3600, step=1, advanced=True),
    "terminal_font": dict(tab="terminal", label="Tamaño de letra de la terminal (px)", default=13, min=12, max=24, step=1, local=True),
    "cursor_style": dict(tab="terminal", label="Estilo del cursor", default="block", options={"block": "Bloque", "bar": "Barra", "underline": "Subrayado"}, local=True),
    "cursor_blink": dict(tab="terminal", label="Parpadear el cursor de la terminal", default=True, local=True),
    "terminal_layout": dict(tab="terminal", label="Disposición preferida de las terminales", default="tabs", options={"tabs": "Pestañas", "tile": "Mosaico", "tile-h": "Lado a lado", "tile-v": "Apiladas", "grid": "Cuadrícula"}, local=True),
    "narrate_terminal": dict(tab="voice", label="Narrar cada comando de Terminater", default=False),
    "narrate_editor": dict(tab="voice", label="Narrar cada segmento de enseñanza del Editor en vivo", default=False),
    "narration_content": dict(tab="voice", label="Qué decir", default="explanation", options={"explanation": "Explicación breve", "literal": "Comando o código", "both": "Ambos"}),
    "narration_when": dict(tab="voice", label="Cuándo hablar", default="before", options={"before": "Antes de escribir", "during": "Mientras escribo", "after": "Después de escribir"}),
    "narration_wait": dict(tab="voice", label="Esperar la narración antes de escribir", default=True),
    "announce_outcomes": dict(tab="voice", label="Anunciar los resultados de los comandos", default="errors", options={"errors": "Errores y solicitudes de entrada del usuario", "all": "Todos los resultados", "off": "Desactivado"}),
}
DEFAULTS = {key: field["default"] for key, field in FIELDS.items()}
ACCOUNT_DEFAULTS = {key: value for key, value in DEFAULTS.items() if not FIELDS[key].get("local")}
DETAIL = {
    "brief": "Use one short explanation and one clear question for each field.",
    "balanced": "Explain what the field does, recommend a value, and ask the learner to choose.",
    "detailed": "Explain why the field matters, alternatives and one example, then ask the learner to choose. Keep edits small.",
}


def validate(values):
    if not isinstance(values, dict) or set(values) - set(ACCOUNT_DEFAULTS):
        raise ValueError("Unknown account preference. Reload the settings dialog.")
    clean = dict(ACCOUNT_DEFAULTS)
    for key, value in values.items():
        field, default = FIELDS[key], DEFAULTS[key]
        if isinstance(default, bool):
            valid = type(value) is bool
        elif isinstance(default, str):
            valid = isinstance(value, str) and value in field["options"]
        else:
            valid = type(value) in (int, float) and math.isfinite(value) and field["min"] <= value <= field["max"]
            if valid and field["step"] == 1:
                valid = int(value) == value
        if not valid:
            raise ValueError(f"Invalid {field['label'].lower()}.")
        clean[key] = value
    if clean["link_speeds"]:
        clean["terminal_wpm"] = clean["editor_wpm"]
    return clean


def snapshot(user_id):
    """No cache: each action sees the last committed account preferences."""
    from .models import InteractionSettings
    if not str(user_id or "").isdigit():
        return dict(ACCOUNT_DEFAULTS), 0
    row = InteractionSettings.objects.filter(user_id=int(user_id)).values("preferences", "revision").first()
    return (validate(row["preferences"]), row["revision"]) if row else (dict(ACCOUNT_DEFAULTS), 0)


@require_http_methods(["GET", "POST"])
def settings_view(request):
    from .models import InteractionSettings
    if request.method == "POST":
        if len(request.body) > 16_384:
            return JsonResponse({"error": "La solicitud de configuración es demasiado grande."}, status=413)
        try:
            data = json.loads(request.body)
            clean = validate(data["preferences"])
            revision = data["revision"]
            if type(revision) is not int or revision < 0:
                raise ValueError("Invalid settings revision.")
        except (ValueError, TypeError, KeyError, UnicodeError):
            return JsonResponse({"error": "Configuración no válida. Revisa los valores y recarga si es necesario."}, status=400)
        with transaction.atomic():
            row, _ = InteractionSettings.objects.get_or_create(user=request.user)
            updated = InteractionSettings.objects.filter(pk=row.pk, revision=revision).update(preferences=clean, revision=revision + 1)
            if not updated:
                return JsonResponse({"error": "La configuración cambió en otra pestaña. Recárgala antes de guardar."}, status=409)
    preferences, revision = snapshot(request.user.pk)
    from .terminal_hub import terminal_kinds
    return JsonResponse({"preferences": preferences, "revision": revision, "fields": FIELDS,
                         "defaults": DEFAULTS, "user": str(request.user.pk), "shells": terminal_kinds()})


def terminal_preferences(action, params, engine):
    """Called by the ONE hub before dispatch, including jobs and in-process flows."""
    preferences, revision = snapshot(params.get("user"))
    params = dict(params)
    inherit = engine._tx.parse_flag(params.get("use_my_defaults"), False, False)[0]
    if inherit and revision:
        for target, source in {"typing_wpm": "terminal_wpm", "kind": "shell", "advisor": "advisor",
                               "wait_seconds": "wait_seconds", "hang_seconds": "hang_seconds",
                               "user_wait_seconds": "user_wait_seconds"}.items():
            params[target] = preferences[source]
    # Omitted fields inherit even on an explicit flow; old saved fields remain explicit.
    for target, source in {"typing_wpm": "terminal_wpm", "kind": "shell", "advisor": "advisor",
                           "wait_seconds": "wait_seconds", "hang_seconds": "hang_seconds",
                           "user_wait_seconds": "user_wait_seconds"}.items():
        params.setdefault(target, preferences[source])
    if preferences["execution"] == "manual":
        if action in {"run", "type", "handover"}:
            text = engine.TerminalHub._text(params)
            if any(ord(c) < 32 for c in text):
                raise engine.TerminaterError("I always press Enter is on. Send one line without control characters; the user submits it.", "manual_enter")
            params["submit"] = False
        if action == "send_key":
            keys = engine._tx.parse_key_sequence(str(params.get("keys") or params.get("text") or ""))[0]
            if any("\r" in key or "\n" in key for key in keys):
                raise engine.TerminaterError("I always press Enter is on. Only the user may submit the command.", "manual_enter")
    params["_interaction"] = preferences
    return params


def chat_preferences(config, explicit, user_id):
    """Preserve a typed call's shell choice while applying the user's pacing.

    The template's literal defaults cannot distinguish an omitted model field.
    Resolve at the authenticated launcher, where the explicit fields are known.
    """
    preferences, revision = snapshot(user_id)
    if not revision:
        return config
    resolved = dict(config)
    for target, source in {'typing_wpm': 'terminal_wpm', 'advisor': 'advisor',
                           'wait_seconds': 'wait_seconds', 'hang_seconds': 'hang_seconds',
                           'user_wait_seconds': 'user_wait_seconds'}.items():
        resolved[target] = preferences[source]
    resolved['kind'] = explicit.get('kind') or preferences['shell']
    resolved['use_my_defaults'] = False
    return resolved


def spoken_text(text, explanation, preferences, *, secret=False, editor=False):
    """Never send secret text or handoff values to a browser speech queue."""
    if secret or "<<USER" in text:
        return "I’ll prepare this step. Enter the private value yourself when prompted."
    explanation = (explanation or ("I’ll write the next teaching segment." if editor else "I’ll prepare this command."))[:1000]
    content = preferences["narration_content"]
    return explanation if content == "explanation" else text[:4000] if content == "literal" else explanation + " " + text[:4000]
