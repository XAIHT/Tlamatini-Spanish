# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""Shared model registry for the Models dialog and standalone workflow agents.

Created by Angela López Mendoza · @angelahack1 — Tlamatini.
Only model/engine/voice settings live here; credentials remain in their existing
configuration. ``@config`` in an agent YAML follows the saved global choice.
"""
import copy
import json
import logging
import os
from pathlib import Path


INHERIT = '@config'
FIELDS = []


def _field(key, label, group, default, *, agent='', path='', kind='ollama',
           optional=False, choices=(), fallback='', help_text=''):
    FIELDS.append(dict(key=key, label=label, group=group, default=default,
                       agent=agent, path=path, kind=kind, optional=optional,
                       choices=list(choices), fallback=fallback, help=help_text))


for key, label, default in (
    ('embeding-model', 'Embedding / memoria', 'Nomic-Embed-Text:latest'),
    ('chained-model', 'Razonamiento encadenado', 'glm-5.3:cloud'),
    ('access_aimed_prompt_model', 'Prompts orientados al acceso', 'glm-5.3:cloud'),
    ('unified_agent_model', 'Unified / Multi-Turn', 'glm-5.3:cloud'),
    ('mcp_files_search_model', 'Búsqueda de archivos de MCP', 'glm-5.3:cloud'),
    ('internet_classifier_model', 'Clasificador de internet', 'glm-5.3:cloud'),
    ('web_summarizer_model', 'Resúmenes de búsquedas web', 'glm-5.3:cloud'),
):
    _field(key, label, 'Principales', default)

for agent, prefix, first, second in (
    ('image_interpreter', 'image', 'mistral-large-3:675b-cloud', 'gemma4:cloud'),
    ('video_analyzer', 'video', 'gemma4:cloud', 'mistral-large-3:675b-cloud'),
):
    for suffix, label, path, default in (
        ('interpreter_model', '· intérprete 1', 'interpreter_model_1', first),
        ('interpreter_model_2', '· intérprete 2', 'interpreter_model_2', second),
        ('merging_model', '· combinador', 'merging_model', 'glm-5.3:cloud'),
    ):
        _field(f'{prefix}_{suffix}', f'{prefix.title()} {label}', 'Visión', default,
               agent=agent, path=path, help_text='Se requiere un modelo con visión.' if 'interpreter' in suffix
               else 'Modelo de texto que combina las dos interpretaciones.')
_field('claude_image_model', 'Análisis de imágenes con Claude', 'Visión', 'claude-opus-4-5-20251101',
       kind='provider', help_text='ID del modelo de Anthropic; requiere tus credenciales actuales de la API de Claude.')

_field('talker_model', 'Talker · generación de voz', 'Voz', 'legraphista/Orpheus:3b-ft-q8',
       agent='talker', path='model', help_text='Modelo de tokens de audio compatible con Orpheus; los modelos de chat comunes no pueden hablar.')
_field('talker_voice', 'Talker · voz', 'Voz', 'tara', agent='talker', path='voice',
       kind='choice', choices=('tara', 'leah', 'jess', 'mia', 'zoe'), help_text='Usa una voz femenina de Orpheus compatible.')
_field('whisperer_engine', 'Whisperer · motor de reconocimiento', 'Voz', 'faster-whisper',
       agent='whisperer', path='engine', kind='choice', choices=('faster-whisper', 'cloud-groq', 'cloud-openai'))
_field('whisperer_model', 'Whisperer · modelo de voz local', 'Voz', 'base',
       agent='whisperer', path='model', kind='local', help_text='Tamaño de Whisper, ID de modelo de Hugging Face o directorio de un modelo local.')
_field('whisperer_cloud_model', 'Whisperer · modelo de voz en la nube', 'Voz', '', optional=True,
       agent='whisperer', path='cloud_model', kind='provider', help_text='Opcional. Vacío usa el modelo predeterminado del proveedor de voz elegido; las credenciales se quedan en el agent.')
_field('whisperer_cleanup_model', 'Whisperer · limpieza de la transcripción', 'Voz', 'glm-5.3:cloud',
       agent='whisperer', path='cleanup_model', fallback='unified_agent_model',
       help_text='Sólo para el posprocesamiento en Ollama; esto no activa la limpieza ni envía el audio del micrófono a Ollama.')
_field('video_transcription_model', 'Video-Analyzer · pistas de audio', 'Voz', 'base',
       agent='video_analyzer', path='transcription.model', kind='local', help_text='Modelo local de faster-whisper para las pistas de audio de los videos.')

for agent, label, group, path in (
    ('crawler', 'Crawler', 'Flujos de trabajo', 'llm.model'),
    ('flowcreator', 'FlowCreator', 'Flujos de trabajo', 'llm.model'),
    ('flowhypervisor', 'FlowHypervisor', 'Flujos de trabajo', 'llm.model'),
    ('prompter', 'Prompter', 'Flujos de trabajo', 'llm.model'),
    ('pser', 'PSer', 'Flujos de trabajo', 'llm.model'),
    ('reviewer', 'Reviewer', 'Flujos de trabajo', 'llm.model'),
    ('file_interpreter', 'File-Interpreter', 'Documentos', 'llm.model'),
    ('summarizer', 'Summarizer', 'Documentos', 'llm.model'),
    ('pdfer', 'PDFer · diseño y pulido', 'Documentos', 'ollama_model'),
    ('pptxer', 'PPTXer · diseño y pulido', 'Documentos', 'ollama_model'),
    ('latexer', 'LaTeXer · reparación', 'Documentos', 'repair_model'),
    ('monitor_log', 'Monitor-Log', 'Monitoreo y mensajería', 'llm.model'),
    ('monitor_netstat', 'Monitor-Netstat', 'Monitoreo y mensajería', 'llm.model'),
    ('notifier', 'Notifier', 'Monitoreo y mensajería', 'llm.model'),
    ('recmailer', 'RecMailer', 'Monitoreo y mensajería', 'llm.model'),
    ('instant_messaging_doctor', 'Instant-Messaging-Doctor', 'Monitoreo y mensajería', 'ollama.model'),
    ('teletlamatini', 'TeleTlamatini · revisión de completitud', 'Monitoreo y mensajería', 'completeness_check.model'),
):
    _field(f'{agent}_model', label, group, 'glm-5.3:cloud', agent=agent, path=path,
           fallback='unified_agent_model', optional=agent == 'latexer',
           help_text='Opcional. Vacío desactiva la reparación con el modelo.' if agent == 'latexer' else '')

BY_KEY = {field['key']: field for field in FIELDS}
AGENTS = frozenset(field['agent'] for field in FIELDS if field['agent'])


def values_for_dialog(config):
    values = {}
    for field in FIELDS:
        value = config.get(field['key'])
        if value is None or (not str(value).strip() and not field['optional']):
            value = config.get(field['fallback']) if field['fallback'] else None
            if value is None or not str(value).strip():
                value = field['default']
        values[field['key']] = str(value).strip()
    return values


def validate_values(payload):
    errors, updates = {}, {}
    for field in FIELDS:
        key = field['key']
        value = payload.get(key)
        if not isinstance(value, str):
            errors[key] = 'debe ser una cadena de texto' if key in payload else 'missing'
            continue
        value = value.strip()
        if not value and not field['optional']:
            errors[key] = 'no puede quedar en blanco'
        elif value == INHERIT:
            errors[key] = 'elige un modelo aquí; @config sólo sirve para los ajustes por agent'
        elif field['choices'] and value not in field['choices']:
            errors[key] = 'elige uno de estos: ' + ', '.join(field['choices'])
        elif len(value) > 512 or any(ord(char) < 32 for char in value):
            errors[key] = 'debe ser un solo valor de 512 caracteres como máximo'
        else:
            updates[key] = value
    return updates, errors


def read_app_config(agent_file=None):
    explicit = os.environ.get('CONFIG_PATH', '').strip()
    root = next((p for p in Path(agent_file or __file__).resolve().parents if p.name == 'agents'), None)
    path = Path(explicit) if explicit else (root.parent / 'config.json' if root else None)
    if not path or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict):
            raise ValueError('expected a JSON object')
        return data
    except (OSError, ValueError) as exc:
        logging.warning('MODELS: could not read %s (%s); using initial defaults', path, type(exc).__name__)
        return {}


def resolve_agent_models(agent, config, app_config=None, *, agent_file=None, force=False):
    """Resolve only registered fields; explicit overrides and empty disable values win."""
    if not isinstance(config, dict):
        return config
    result = copy.deepcopy(config)
    values = values_for_dialog(read_app_config(agent_file) if app_config is None else app_config)
    for field in FIELDS:
        if field['agent'] != agent:
            continue
        parts = field['path'].split('.')
        target = result
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            if not isinstance(target[part], dict):
                break
            target = target[part]
        else:
            key = parts[-1]
            if force or key not in target or target[key] == INHERIT:
                target[key] = values[field['key']]
    return result
