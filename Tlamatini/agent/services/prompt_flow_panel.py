# Tlamatini — "one who knows"
# Created by Angela López Mendoza · @angelahack1
# Tlamatini Author Banner — do not remove
"""Versioned .fpmt graph contract and deterministic prompt-flow-panel interpreter.

No Django or model imports: the runner receives an adapter for model/context work.
Files are data, never executable Python/JavaScript. A decision evaluates only the
documented string comparisons; cycles have an explicit execution budget.
"""
from __future__ import annotations

import asyncio
import math
import re
from datetime import datetime, timezone

# Keep the JSON contract stable when existing flow files are renamed to .fpmt.
FORMAT = "tlamatini-prompting-flow"
VERSION = 2
MAX_FILE_BYTES = 5 * 1024 * 1024
OPERATIONS = {
    "prompt", "programmed_prompt", "decision", "feed_embeddings",
    "flush_embeddings", "clean_history", "user_input", "user_commentary", "terminater",
}
COMMENT_COLORS = {"#fbcfe8", "#fef3c7", "#dcfce7", "#dbeafe", "#ede9fe", "#ffedd5", "#ffffff", "#e5e7eb"}
COMMENT_TEXT_COLORS = {"#202938", "#000000", "#1d4ed8", "#166534", "#7e22ce", "#b91c1c", "#92400e", "#ffffff"}
COMMENT_FONTS = {"Nunito", "Arial", "Verdana", "Georgia", "Times New Roman", "Courier New"}
COMPARISONS = {"contains", "not_contains", "equals", "is_empty", "user"}
# Terminater (the parallelogram): one action in the user's visible CMD / PowerShell terminals.
# Keep these tables identical to prompt-flow-panel-model.js.
TERMINATER_ACTIONS = (
    "run", "open", "type", "send_key", "wait", "read", "commands", "abort", "kill", "force_kill",
    "kill_all", "list", "status", "focus", "rename", "layout", "clear", "watch_user", "warn_user", "handover",
)
TERMINATER_KINDS = ("cmd", "powershell", "pwsh")
TERMINATER_TEXT_ACTIONS = ("run", "type", "handover")
TERMINATER_DEFAULTS = {
    "action": "run", "kind": "powershell", "terminal": "", "title": "", "cwd": "", "keys": "", "message": "",
    "severity": "warning", "suggestion": "", "hint": "", "which": "last", "until": "", "pattern": "",
    "layout": "", "area": "", "submit": True, "secret": False, "wait": True, "close_after": False,
    "load_profile": True, "advisor": True, "typing_wpm": 50, "wait_seconds": 120, "hang_seconds": 45,
    "user_wait_seconds": 300, "idle_seconds": 2, "use_my_defaults": False, "explanation": "",
}
TERMINATER_TEXT_LIMITS = {
    "terminal": 80, "title": 80, "cwd": 1000, "keys": 500, "message": 2000, "suggestion": 1000,
    "hint": 200, "which": 40, "until": 20, "pattern": 500, "explanation": 1000,
}
TERMINATER_NUMBERS = {
    "typing_wpm": (20, 160, True), "wait_seconds": (1, 3600, False), "hang_seconds": (3, 3600, False),
    "user_wait_seconds": (5, 3600, False), "idle_seconds": (0.2, 600, False),
}
TERMINATER_BOOLEANS = ("submit", "secret", "wait", "close_after", "load_profile", "advisor", "use_my_defaults")


class FlowError(ValueError):
    """A malformed document or an operation that could not complete."""


class FlowStopped(Exception):
    """Cooperative stop: no subsequent operation may start."""


def _text(value, label, maximum=100_000):
    if not isinstance(value, str) or len(value) > maximum:
        raise FlowError(f"{label} debe ser un texto de {maximum:,} caracteres como máximo.")
    return value


def _number(value, label, minimum, maximum, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FlowError(f"{label} debe ser un número.")
    if not math.isfinite(value) or not minimum <= value <= maximum or (integer and value != int(value)):
        raise FlowError(f"{label} debe estar entre {minimum} y {maximum}.")
    return int(value) if integer else value


def scheduled_time(value):
    if not value:
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError("timezone missing")
        return result
    except (TypeError, ValueError) as exc:
        raise FlowError("La hora programada debe ser una fecha ISO con zona horaria.") from exc


def _terminater_config(config, label, text, playable):
    """Allowlist one Terminater step; the command text itself is validated by the caller."""
    out = {}
    action = config.get("action", TERMINATER_DEFAULTS["action"])
    if action not in TERMINATER_ACTIONS:
        raise FlowError("Acción de Terminater desconocida.")
    out["action"] = action
    shell = config.get("kind", TERMINATER_DEFAULTS["kind"])
    if shell not in TERMINATER_KINDS:
        raise FlowError("Elige CMD, PowerShell o PowerShell 7.")
    out["kind"] = shell
    for key, limit in TERMINATER_TEXT_LIMITS.items():
        out[key] = _text(config.get(key, TERMINATER_DEFAULTS[key]), f"Terminater {key}", limit)
    severity = config.get("severity", TERMINATER_DEFAULTS["severity"])
    if severity not in {"info", "hint", "warning", "danger"}:
        raise FlowError("Severidad de Terminater desconocida.")
    out["severity"] = severity
    layout, area = config.get("layout", ""), config.get("area", "")
    if layout not in {"", "tabs", "tile", "tile-h", "tile-v", "grid"} or area not in {"", "dock", "full"}:
        raise FlowError("Distribución o área de Terminater desconocida.")
    out["layout"], out["area"] = layout, area
    for key in TERMINATER_BOOLEANS:
        value = config.get(key, TERMINATER_DEFAULTS[key])
        if not isinstance(value, bool):
            raise FlowError(f"Terminater {key} debe ser true o false.")
        out[key] = value
    for key, (low, high, integer) in TERMINATER_NUMBERS.items():
        out[key] = _number(config.get(key, TERMINATER_DEFAULTS[key]), f"Terminater {key}", low, high, integer)
    if playable and action in TERMINATER_TEXT_ACTIONS and not text.strip():
        raise FlowError(f"{label} necesita un comando para escribir.")
    if playable and action == "send_key" and not out["keys"].strip():
        raise FlowError(f"{label} necesita las teclas que se van a presionar.")
    return out


def validate_flow(payload, *, playable=False):
    """Return a fresh, allowlisted document; do not mutate input or trust IDs."""
    if not isinstance(payload, dict) or payload.get("format") != FORMAT:
        raise FlowError("Abre un documento .fpmt de Prompt Flow Panel (el texto antiguo de prompt.pmt no es un diagrama).")
    legacy = payload.get("version") == 1
    if payload.get("version") not in (1, VERSION):
        raise FlowError("Versión de .fpmt no compatible. Este panel admite las versiones 1 y 2.")
    nodes, edges = payload.get("nodes"), payload.get("edges")
    if not isinstance(nodes, list) or len(nodes) > 500 or not isinstance(edges, list) or len(edges) > 1000:
        raise FlowError("Un flow puede tener hasta 500 operaciones y 1,000 conexiones.")
    result = {
        "format": FORMAT, "version": VERSION,
        "name": _text(payload.get("name", "Untitled"), "Nombre del flow", 120),
        "start": payload.get("start"),
        "max_steps": _number(payload.get("max_steps", 500), "Límite de pasos", 1, 5000, True),
        "nodes": [], "edges": [],
    }
    known = {}
    for node in nodes:
        if not isinstance(node, dict):
            raise FlowError("Cada operación debe ser un objeto.")
        node_id = _text(node.get("id"), "ID de la operación", 80)
        if not re.fullmatch(r"[A-Za-z0-9_-]+", node_id) or node_id in known:
            raise FlowError("Los IDs de las operaciones deben ser únicos y usar sólo letras, dígitos, guiones bajos o guiones.")
        kind = node.get("type")
        if legacy and kind == "user_commentary":
            kind = "user_input"
        if kind not in OPERATIONS:
            raise FlowError(f"Operación desconocida: {kind!r}.")
        config = node.get("config", {})
        if not isinstance(config, dict):
            raise FlowError("La configuración de la operación debe ser un objeto.")
        clean = {"text": _text(config.get("text", ""), "Texto de la operación")}
        if kind == "user_commentary":
            clean.update(
                width=_number(config.get("width", 320), "Ancho del comentario", 200, 2400),
                height=_number(config.get("height", 200), "Altura del comentario", 128, 2400),
                font_size=_number(config.get("font_size", 16), "Tamaño de fuente del comentario", 10, 48),
                color=_text(config.get("color", "#fbcfe8"), "Color del comentario", 20),
                text_color=_text(config.get("text_color", "#202938"), "Color del texto del comentario", 20),
                font_family=_text(config.get("font_family", "Nunito"), "Fuente del comentario", 80),
                align=_text(config.get("align", "left"), "Alineación del comentario", 10),
            )
            if clean["color"] not in COMMENT_COLORS or clean["text_color"] not in COMMENT_TEXT_COLORS or clean["font_family"] not in COMMENT_FONTS or clean["align"] not in {"left", "center", "right"}:
                raise FlowError("Elige un color, una fuente y una alineación compatibles para el comentario.")
            for key in ("bold", "italic", "underline"):
                clean[key] = config.get(key, False)
                if not isinstance(clean[key], bool):
                    raise FlowError(f"El estilo {key} del comentario debe ser true o false.")
            style_keys = ("font_family", "font_size", "text_color", "bold", "italic", "underline")
            runs = config.get("runs", [{"text": clean["text"]}] if clean["text"] else [])
            if not isinstance(runs, list) or len(runs) > 10000:
                raise FlowError("Usa como máximo 10,000 fragmentos de texto con formato por comentario.")
            clean["runs"] = []
            for run in runs:
                if not isinstance(run, dict):
                    raise FlowError("Un fragmento de texto con formato debe ser un objeto.")
                part = {"text": _text(run.get("text"), "Texto del fragmento del comentario")}
                part.update({key: run.get(key, clean[key]) for key in style_keys})
                _number(part["font_size"], "Tamaño de fuente del fragmento del comentario", 10, 48)
                if _text(part["font_family"], "Fuente del fragmento del comentario", 80) not in COMMENT_FONTS or _text(part["text_color"], "Color del fragmento del comentario", 20) not in COMMENT_TEXT_COLORS:
                    raise FlowError("Elige una fuente y un color de texto compatibles para el comentario.")
                if any(not isinstance(part[key], bool) for key in ("bold", "italic", "underline")):
                    raise FlowError("Los interruptores de estilo de los fragmentos del comentario deben ser true o false.")
                if not part["text"]:
                    continue
                last = clean["runs"][-1] if clean["runs"] else None
                if last and all(last[key] == part[key] for key in style_keys):
                    last["text"] += part["text"]
                else:
                    clean["runs"].append(part)
            if "".join(run["text"] for run in clean["runs"]) != clean["text"]:
                raise FlowError("Los fragmentos deben contener exactamente el texto del comentario.")
        if kind in {"prompt", "programmed_prompt"}:
            for key in ("multi_turn", "acpx"):
                clean[key] = config.get(key, False)
                if not isinstance(clean[key], bool):
                    raise FlowError(f"{key} debe ser true o false.")
            if clean["acpx"] and not clean["multi_turn"]:
                raise FlowError("ACPX requiere Multi-Turn.")
            if playable and not clean["text"].strip():
                raise FlowError(f"{node.get('label', kind)} necesita el texto del prompt.")
        if kind == "programmed_prompt":
            clean["delay_seconds"] = _number(config.get("delay_seconds", 0), "Retraso", 0, 86400)
            clean["scheduled_at"] = _text(config.get("scheduled_at", ""), "Hora programada", 60)
            scheduled_time(clean["scheduled_at"])
        if kind == "decision":
            clean["comparison"] = config.get("comparison", "contains")
            if clean["comparison"] not in COMPARISONS:
                raise FlowError("Comparación de decisión desconocida.")
            clean["value"] = _text(config.get("value", ""), "Valor de comparación", 10000)
            clean["case_sensitive"] = config.get("case_sensitive", False)
            if not isinstance(clean["case_sensitive"], bool):
                raise FlowError("La distinción entre mayúsculas y minúsculas debe ser true o false.")
            if playable and clean["comparison"] in {"contains", "not_contains", "equals"} and not clean["value"]:
                raise FlowError("Define un valor de comparación para la decisión o elige 'El último output está vacío'.")
        if kind == "feed_embeddings" and playable and not clean["text"].strip():
            raise FlowError("La operación Agregar embeddings necesita texto o {{last_output}}.")
        if kind == "terminater":
            clean.update(_terminater_config(config, node.get("label", kind), clean["text"], playable))
        item = {
            "id": node_id, "type": kind,
            "label": _text(node.get("label", kind.replace("_", " ").title()), "Etiqueta de la operación", 120),
            "x": _number(node.get("x", 0), "Posición X", 0, 100000),
            "y": _number(node.get("y", 0), "Posición Y", 0, 100000),
            "config": clean,
        }
        known[node_id] = item
        if legacy and node.get("type") == "user_commentary" and item["label"] == "User Commentary":
            item["label"] = "Input del usuario"
        result["nodes"].append(item)
    slots, edge_ids = set(), set()
    for edge in edges:
        if not isinstance(edge, dict):
            raise FlowError("Cada conexión debe ser un objeto.")
        edge_id = _text(edge.get("id"), "ID de la conexión", 80)
        if not re.fullmatch(r"[A-Za-z0-9_-]+", edge_id) or edge_id in edge_ids:
            raise FlowError("Los IDs de las conexiones deben ser únicos y usar sólo letras, dígitos, guiones bajos o guiones.")
        source, target = edge.get("source"), edge.get("target")
        if not isinstance(source, str) or not isinstance(target, str) or source not in known or target not in known:
            raise FlowError("Cada conexión debe unir operaciones existentes.")
        branch = edge.get("branch", "next")
        if any(known[key]["type"] == "user_commentary" for key in (source, target)):
            raise FlowError("Los elementos estáticos de Comentario del usuario no pueden tener conexiones.")
        allowed = {"yes", "no"} if known[source]["type"] == "decision" else {"next"}
        if branch not in allowed or (source, branch) in slots:
            raise FlowError("Cada output acepta una sola conexión. Las decisiones tienen outputs Sí y No separados.")
        slots.add((source, branch))
        edge_ids.add(edge_id)
        result["edges"].append({"id": edge_id, "source": source, "target": target, "branch": branch})
    if result["start"] is not None and (not isinstance(result["start"], str) or result["start"] not in known):
        raise FlowError("La operación de Inicio no existe.")
    if result["start"] is not None and known[result["start"]]["type"] == "user_commentary":
        raise FlowError("Un Comentario del usuario estático no puede ser la operación de Inicio.")
    if playable:
        if not nodes or result["start"] is None:
            raise FlowError("Agrega una operación y elige dónde empieza el flow.")
        reachable, pending = set(), [result["start"]]
        while pending:
            current = pending.pop()
            if current in reachable:
                continue
            reachable.add(current)
            pending.extend(e["target"] for e in result["edges"] if e["source"] == current)
        if len(reachable) != sum(n["type"] != "user_commentary" for n in result["nodes"]):
            raise FlowError("No se puede llegar a algunas operaciones desde el Inicio. Conéctalas o elige otra en Inicio.")
        for node in nodes:
            if node["type"] == "decision" and not all((node["id"], branch) in slots for branch in ("yes", "no")):
                raise FlowError("Conecta los outputs Sí y No de cada decisión.")
    return result


def expand_text(text, last_output):
    return text.replace("{{last_output}}", last_output)


_END_RESPONSE = re.compile(r"\bEND-RESPONSE\b")
_HTML_TAG = re.compile(r"<[^>]+>")
_MARKDOWN_MARKS = re.compile(r"[#*_`>~|]+")
_EDGE_PUNCTUATION = " \t\r\n.,;:!?\"'()[]{}—–-"
# What a Prompt step sends to the model when the next operation is an "equals" Decision.
VERDICT_FIRST_HINT = (
    "\n\n(This answer is read by an automatic Decision. Put your short answer - "
    "exactly the word or phrase this request asks for - alone on the first line, "
    "then any explanation.)"
)


def _plain(text):
    """An answer as a reader sees it: no END-RESPONSE, HTML tags or Markdown marks."""
    text = _HTML_TAG.sub(" ", _END_RESPONSE.sub(" ", text))
    text = _MARKDOWN_MARKS.sub(" ", text.replace("&nbsp;", " ").replace("&amp;", "&"))
    return " ".join(text.split()).strip(_EDGE_PUNCTUATION)


def _equals(output, value):
    """True when the answer IS the value, or opens with it as its verdict.

    A model asked to "answer YES, otherwise NOT" writes "## YES - the toolkit
    is current ..." (2026-10-26: a 6,055-character answer). An exact comparison
    called that "not YES" and the flow took the wrong branch. The verdict must
    stand alone at the start: "Yesterday" does not equal "yes".
    """
    if output.strip() == value.strip():
        return True
    answer, wanted = _plain(output), _plain(value)
    if not wanted:
        return False
    return answer == wanted or re.match(re.escape(wanted) + r"(?!\w)", answer) is not None


def decide(config, output):
    value = config["value"]
    if not config["case_sensitive"]:
        output, value = output.casefold(), value.casefold()
    return {"contains": lambda: value in output, "not_contains": lambda: value not in output,
            "equals": lambda: _equals(output, value), "is_empty": lambda: not output.strip()}[config["comparison"]]()


class FlowRunner:
    def __init__(self, flow, runtime, emit):
        self.flow = validate_flow(flow, playable=True)
        self.runtime, self.emit = runtime, emit
        self.stopped = asyncio.Event()
        self.resumed = asyncio.Event()
        self.resumed.set()
        self.reply_future = None
        self.reply_id = None
        self.last_output = ""
        self.step = 0

    async def gate(self):
        while not self.resumed.is_set() and not self.stopped.is_set():
            try:
                await asyncio.wait_for(self.stopped.wait(), 0.1)
            except asyncio.TimeoutError:
                pass
        if self.stopped.is_set():
            raise FlowStopped()

    def stop(self):
        self.stopped.set()
        self.resumed.set()
        self.runtime.cancel()
        if self.reply_future and not self.reply_future.done():
            self.reply_future.set_exception(FlowStopped())

    async def wait_delay(self, seconds):
        # Delay counts active time; a scheduled wall-clock time remains absolute.
        remaining = seconds
        while remaining > 0:
            await self.gate()
            interval = min(0.2, remaining)
            try:
                await asyncio.wait_for(self.stopped.wait(), interval)
            except asyncio.TimeoutError:
                remaining -= interval
        await self.gate()

    async def ask_user(self, node, kind):
        self.reply_id = f"{node['id']}-{self.step}"
        self.reply_future = asyncio.get_running_loop().create_future()
        await self.emit("input", node_id=node["id"], request_id=self.reply_id, kind=kind,
                        message=expand_text(node["config"]["text"], self.last_output))
        try:
            return await self.reply_future
        finally:
            self.reply_future = None
            self.reply_id = None

    def reply(self, request_id, value):
        if self.reply_future is None or self.reply_future.done() or request_id != self.reply_id:
            raise FlowError("Esta solicitud de input ya no está activa.")
        self.reply_future.set_result(_text(value, "Respuesta"))

    async def run(self):
        nodes = {n["id"]: n for n in self.flow["nodes"]}
        edges = {(e["source"], e["branch"]): e for e in self.flow["edges"]}
        current = self.flow["start"]
        while current:
            await self.gate()
            self.step += 1
            if self.step > self.flow["max_steps"]:
                raise FlowError("Se alcanzó el límite de pasos. Revisa el ciclo o sube el límite de pasos del flow.")
            node = nodes[current]
            kind, config = node["type"], node["config"]
            await self.emit("node", node_id=current, status="running", step=self.step)
            branch, output = "next", None
            if kind == "programmed_prompt":
                scheduled = scheduled_time(config["scheduled_at"])
                if scheduled:
                    await self.emit("waiting", node_id=current, message=f"Programado para {scheduled.isoformat()}")
                    while datetime.now(timezone.utc) < scheduled:
                        await self.wait_delay(min(0.5, (scheduled - datetime.now(timezone.utc)).total_seconds()))
                if config["delay_seconds"]:
                    await self.emit("waiting", node_id=current, message=f"Esperando {config['delay_seconds']:g} segundos activos")
                    await self.wait_delay(config["delay_seconds"])
            await self.gate()
            if kind in {"prompt", "programmed_prompt"}:
                text = expand_text(config["text"], self.last_output)
                following = edges.get((current, "next"))
                if following and nodes[following["target"]]["type"] == "decision" \
                        and nodes[following["target"]]["config"]["comparison"] == "equals":
                    text += VERDICT_FIRST_HINT
                output = await self.runtime.prompt(text, config)
            elif kind == "feed_embeddings":
                await self.runtime.feed(expand_text(config["text"], self.last_output))
            elif kind == "flush_embeddings":
                await self.runtime.flush()
            elif kind == "clean_history":
                await self.runtime.clean_history()
                self.last_output = ""
            elif kind == "terminater":
                output = await self.runtime.terminal(expand_text(config["text"], self.last_output), config)
            elif kind == "user_input":
                output = await self.ask_user(node, "commentary")
                await self.runtime.comment(output)
            elif kind == "decision":
                if config["comparison"] == "user":
                    response = await self.ask_user(node, "decision")
                    if response not in {"yes", "no"}:
                        raise FlowError("La respuesta de una decisión debe ser Sí o No.")
                    branch = response
                else:
                    branch = "yes" if decide(config, self.last_output) else "no"
            await self.gate()
            if output is not None:
                self.last_output = output
                await self.emit("output", node_id=current, text=output)
            await self.emit("node", node_id=current, status="completed", step=self.step)
            edge = edges.get((current, branch))
            if edge:
                await self.emit("edge", edge_id=edge["id"], branch=branch)
            current = edge["target"] if edge else None

