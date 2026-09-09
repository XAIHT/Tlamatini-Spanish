<!--
═══════════════════════════════════════════════════════════════════
  ✦  T L A M A T I N I  ✦   —   "one who knows"
  Created by  Angela López Mendoza   ·   @angelahack1
  Developer · Architect · Creator of Tlamatini
  Tlamatini Author Banner — do not remove
═══════════════════════════════════════════════════════════════════
-->
# Estado técnico actual de Tlamatini-Spanish — `v1.51.3s`

Este documento es el punto de reconciliación entre el source, la documentación, los prompts, los skills y los artefactos generados. El español es la **lengua matriz** según NEPANTLA; nombres de agents/tools, fields, keys, enums, sentinels, paths, código y términos técnicos estables permanecen en inglés y byte-stable.

## Identidad comprobable

| Dato | Valor | Fuente |
|---|---:|---|
| Release/tag vigente | `v1.51.3s` | `git describe --tags --abbrev=0 HEAD` |
| Commit del tag | `212b0bd` | `git rev-list -n 1 v1.51.3s` |
| `HEAD` de `main` | `212b0bd` | `git rev-parse --short HEAD` |
| `origin/main` (aún sin push) | `272d6ac` | `git rev-parse --short origin/main` |
| Commits de `main` posteriores al tag | 0 | `git rev-list --count v1.51.3s..HEAD` |
| Workflow agents | 88 | directorios completos `agent/agents/<name>/<name>.py + config.yaml` |
| Launchers wrapped `chat_agent_*` | 66 | `chat_agent_registry.WRAPPED_CHAT_AGENT_SPECS` |
| Tools directas/core | 20 | decorators `@tool` activos |
| Tools ACPX/Skill | 12 | `agent/acpx/tools.py` |
| Supervisores External-MCP | 10 | `_SUPERVISOR_TOOL_NAMES` |
| Tools integradas de Multi-Turn | 108 | 20 + 66 + 12 + 10 |
| Tools del MCP stdio raíz | 105 | 88 launchers + 7 management + 10 ACPX |
| Skills | 29 | packages con `SKILL.md` bajo `agent/skills_pkg/` |
| Migrations | 200 | `agent/migrations/*.py`, sin `__init__.py` |
| Frontend | 37 JS · 11 CSS · 4 templates HTML | inventario del tree |

El inventario reproducible del 2026-09-06 mide **1,143 files tracked**, **250,620 líneas efectivas** y **358,520 líneas físicas**. Hay 59 binarios y dos archivos de texto omitidos del conteo por tamaño/legibilidad. El appendix de árbol distribuible se limita exactamente a `git ls-files`; los cambios locales se reportan aparte y nunca se fingen como contenido del tag.

## Desarrollo actual derivado del source

### Proceso web frozen ligero y frontera de intérpretes

`build.py` excluye `transformers`, `torch`, `torchvision`, `torchaudio`, `torchtext`, `torchao`, `snac` y `whisper` del proceso Django frozen. El hook prioritario `pyinstaller_hooks/hook-torch.py` evita que el hook upstream copie DLLs de CUDA aun cuando los módulos estén excluidos. `verify_frozen_torch_absent()` rechaza una salida que conserve `torch/lib` o DLLs CUDA huérfanas, y `enforce_pkg_zip_size()` fija un techo decimal de 2.8 GB.

La voz no se elimina: `build.py::_probe_cpu_torch()` comprueba Torch CPU-only dentro del Python **acarreado**, el intérprete separado que ejecuta Talker y Whisperer. Esta frontera conserva TTS/STT y evita el arranque ruidoso del web process. La medición fijada por `test_web_process_stays_lean.py` pasó de 248 módulos `transformers` + 663 `torch` y 9.47 s a 0 + 0 y 3.62 s.

### Cierre Ctrl+C acotado

`agent/apps.py` ya no ejecuta cleanup complejo desde el signal handler. El handler sólo activa un `threading.Event`; un worker daemon preiniciado hace el cleanup; un watchdog fuerza la salida después de 12 s; y un segundo Ctrl+C sale inmediatamente. El cleanup de processes tracked usa un thread daemon con `join(5)` en lugar de un `ThreadPoolExecutor` cuyo `__exit__` esperaba sin límite. La forma se fija en `agent/test_ctrl_c_shutdown.py` y el comportamiento visible real en `tests_e2e/test_ctrl_c_quits_visible.py`.

### Build público desde clone limpio y privacidad fail-toward-safety

`build_complete_public_release.py` admite `.private_targets.json` sólo como input local de build; `private_targets.example.json` es un template inerte. `privacy_preflight()` busca `data.keys`, secrets vivos, PII, contacts y keys raíz antes de decidir si un tree sin targets es realmente limpio. Un clone limpio entra en **MODO ÁRBOL LIMPIO**; si hay evidencia privada y faltan targets, el build se niega salvo el override peligroso y explícito `--assume-clean-tree`. La verificación estructural sigue ejecutándose con sentinels y nunca afirma haber buscado PII cuando no lo hizo. Backup, restore y re-key se derivan de los files tocados por `regen_secrets.py`.

### Deleter: objetivo explícito y guardas de raíz

En Deleter, `target_path` es únicamente el directorio de trabajo; los objetivos viven en `files_to_delete`. Un tree completo requiere `allow_directory_delete: true`. Se rechazan nombres protegidos, cwd y ancestros, el propio tree de Deleter, Git roots y drive roots. Cada rechazo conserva la razón y `total_refused`, y aun así dispara `target_agents` para que el flow pueda ramificar. Un rechazo no autoriza a evadir la guarda mediante shell genérico.

### Googler y URLs de resultado

Googler ejecuta `html.unescape()` antes de analizar links, desenvuelve redirects de Bing `/ck/a?...u=a1<base64url>` y filtra domains propios, sociales o de newsletter de Mojeek. El decoder es fail-open: una URL desconocida se conserva en lugar de inventar un destino. La ruta complementa el compilador de dorks, el plain-HTTP-first y el browser fallback visible.

### Parametrizer y diagnósticos

`services/agent_contracts.py` mantiene los fields promovidos de Summarizer, Shoter, Reviewer, Analyzer, Telegrammer y Whatsapper alineados con sus bloques `INI_SECTION_*`. Para Globber, Grepper, Analyzer y demás agentes diagnósticos, `no_matches`, `findings`, `invalid` o `listed` pueden ser resultados exitosos porque la observación es el entregable; un `refused`, `not_found`, `engine_unavailable` o entregable degradado no es éxito limpio.

### Descripciones españolas con fallback granular

`agent/views.py` carga primero la tabla inglesa autoritativa de `agents_descriptions.md` y superpone `agents_descriptions.es.md` **agent por agent**. `AGENT_DESCRIPTIONS_LANGUAGE='es'` activa la capa; un file ausente, ilegible o incompleto falla hacia la tabla inglesa sin borrar tooltips ni el diálogo Description. Source y build frozen buscan ambos archivos en las mismas raíces. Ésta es localización de chrome/descripción, no traducción de IDs ni display names.

### Playwrighter, Shoter y pruebas visibles propias

`chat_agent_runtime._build_child_env()` exporta `TLAMATINI_AGENTS_ROOT` para que un wrapped agent iniciado desde `Temp/mcp_agent_runs/...` encuentre agents hermanos. La ruta desbloquea el paso `shoter` de Playwrighter también desde chat Multi-Turn, no sólo desde canvas. El harness `playwrighter_run.py` delega browser en Playwrighter y cada captura full-desktop en Shoter; no sustituye silenciosamente ninguno por una utilidad ajena.

La matriz visible agregada en `.claude/skills/tlamatini-daily-chat-test/harness/` cubre: nueve diálogos ACP, tema y geometría, toggles bulk, Playwrighter+Shoter, voz española y un corpus reanudable de **1,000 preguntas**. Este último vuelve a activar Multi-Turn antes de cada envío, limpia historial para evitar respuestas rancias, rechaza marcos transitorios de self-healing, compara gemelas con/sin acento, valida español y registro técnico, exige servidor mudo y persiste evidencia por pregunta.

### Sentinel de rephrase y contratos machine

`Referenced Rephrase:` reemplaza la frase visible española como sentinel de protocolo en productor, WebSocket, historial y prompt. Se mantiene en inglés por NEPANTLA, se filtra del historial y no se duplica si ya venía prefijado; `test_chat_history_window.py::ReferencedRephraseMarkerTests` fija ese contrato. Los campos promovidos nuevos incluyen `target_words`, `all_screens`, `error`, `min_severity`, `mode` y `direction` según el agent correspondiente.

### Seguridad Blue-hat y artefactos de diseño

El dossier documenta los assets defensivos de `security/`, su habilitación consciente, el modo armed/aggressive y la preservación privada de `security_logs`. `.scanning/finding-policy.json` registra excepciones Bandit/Semgrep justificadas y acotadas. `10000xRedesignOfUpdatingMechanicsOnTlamatini.md`, `DesignOfIncludingMemoryMCPS.txt` y `MCPMemoriesFlowCreation.flw` son **diseño/propuesta**: se inventarían capacidades si se presentaran como runtime implementado. La documentación los etiqueta como trabajo prospectivo hasta que source, migrations y tests prueben lo contrario.

## Contrato NEPANTLA

1. El chrome de GUI sí se localiza mediante `agent/i18n/ui_es.py` y la normalización N1/N2/N3.
2. El prompt del usuario llega al modelo sin traducción mecánica.
3. La respuesta del modelo nace en español; no se traduce después.
4. El español aporta gramática y prosa portadora.
5. El léxico técnico inglés incrustado permanece estable: `MCP`, `Multi-Turn`, `Exec Report`, `Ask Execs`, `Skill`, `Flow`, `Prompt`, `Log`, `Commit`, `Build`, `Deploy`, `Container`.
6. Identificadores, display names de agents, tool names, keys, fields, enums, sentinels, code y paths nunca se traducen.
7. Logs y outputs de tools pueden permanecer en inglés o mixtos; se explican al usuario en español sin alterar sus tokens machine.

## Límites de verdad documental

- Un número activo se deriva del source; no se copia de un handbook anterior.
- Las notas de release fechadas conservan sus cifras históricas.
- `v1.51.3s` nombra el tag `212b0bd`; `main`/`HEAD` auditado es `212b0bd`, cero commits posterior. Ninguno de esos commits posteriores se presenta como contenido ya publicado del tag.
- Los configs con secrets no se transcriben en documentos ni artefactos.
- Los PDFs/PPTX generados incluyen el tree tracked completo, inventario de líneas, arquitectura, uso, cambios recientes y evidencia de validación.

## Gates de verificación

- `python -m unittest` para contratos de versión, self-knowledge, NEPANTLA, build lean, Ctrl+C, build público, Googler, Deleter y artifacts.
- `python Tlamatini/manage.py makemigrations --check --dry-run`.
- `npm run lint`.
- Regeneración determinista del dossier con `TLAMATINI_VERSION=1.51.3s`.
- Extracción y render de todos los PDFs; render de todas las slides y prueba de geometría/overlap del PPTX.
- Ejecución de `build_complete_private_release.py --self-modify` sólo después de que los gates rápidos sean verdes, sin imprimir secrets.
