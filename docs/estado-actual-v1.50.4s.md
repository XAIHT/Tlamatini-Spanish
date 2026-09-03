<!--
═══════════════════════════════════════════════════════════════════
  ✦  T L A M A T I N I  ✦   —   "one who knows"
  Created by  Angela López Mendoza   ·   @angelahack1
  Developer · Architect · Creator of Tlamatini
  Tlamatini Author Banner — do not remove
═══════════════════════════════════════════════════════════════════
-->
# Estado técnico actual de Tlamatini-Spanish — `v1.50.4s`

Este documento es el punto de reconciliación entre el source, la documentación, los prompts, los skills y los artefactos generados. El español es la **lengua matriz** según NEPANTLA; nombres de agents/tools, fields, keys, enums, sentinels, paths, código y términos técnicos estables permanecen en inglés y byte-stable.

## Identidad comprobable

| Dato | Valor | Fuente |
|---|---:|---|
| Tag anotado actual | `v1.50.4s` | `git describe --tags --exact-match HEAD` |
| Commit del tag al iniciar la auditoría | `1339fc7` | `git rev-parse --short HEAD` |
| Workflow agents | 88 | directorios completos `agent/agents/<name>/<name>.py + config.yaml` |
| Launchers wrapped `chat_agent_*` | 66 | `chat_agent_registry.WRAPPED_CHAT_AGENT_SPECS` |
| Tools directas/core | 20 | decorators `@tool` activos |
| Tools ACPX/Skill | 12 | `agent/acpx/tools.py` |
| Supervisores External-MCP | 10 | `_SUPERVISOR_TOOL_NAMES` |
| Tools integradas de Multi-Turn | 108 | 20 + 66 + 12 + 10 |
| Tools del MCP stdio raíz | 105 | 88 launchers + 7 management + 10 ACPX |
| Skills | 29 | packages con `SKILL.md` bajo `agent/skills_pkg/` |
| Migrations | 198 | `agent/migrations/*.py`, sin `__init__.py` |
| Frontend | 37 JS · 11 CSS · 4 templates HTML | inventario del tree |

El inventario del dossier del 2026-09-01, incluyendo cuatro adiciones visibles y no ignoradas del working tree, midió 1,134 files, 248,088 líneas efectivas y 354,763 líneas físicas de texto. El appendix de árbol distribuible se limita a files tracked; las adiciones del working tree se reportan aparte para no fingir que ya pertenecen a un release.

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
- `v1.50.4s` nombra el tag `1339fc7`; cambios no commiteados se describen como **working tree posterior al tag**, no como contenido ya publicado.
- Los configs con secrets no se transcriben en documentos ni artefactos.
- Los PDFs/PPTX generados incluyen el tree tracked completo, inventario de líneas, arquitectura, uso, cambios recientes y evidencia de validación.

## Gates de verificación

- `python -m unittest` para contratos de versión, self-knowledge, NEPANTLA, build lean, Ctrl+C, build público, Googler, Deleter y artifacts.
- `python Tlamatini/manage.py makemigrations --check --dry-run`.
- `npm run lint`.
- Regeneración determinista del dossier con `TLAMATINI_VERSION=1.50.4s`.
- Extracción y render de todos los PDFs; render de todas las slides y prueba de geometría/overlap del PPTX.
- Ejecución de `build_complete_private_release.py --self-modify` sólo después de que los gates rápidos sean verdes, sin imprimir secrets.
