# NEPANTLA Terminology Reference

**The complete term inventory for Tlamatini's Spanish edition, read out of the live files.** Every count and every list below is produced by `generate_terminology.py`, which imports `agent/i18n/termbase_en.py`, `lexicon_es.py`, `ui_es.py` and `terms.csv` directly. Nothing is hand-transcribed, so this document cannot drift from what the code actually enforces.

## The rule

> Spanish supplies the grammar. English supplies the technical vocabulary.

The register Tlamatini's users already speak:

> *"Haciendo un Pod en Dockerer y creando un Container en Kubernetes y haciendo el deployment en la LPAR"*

This is the **Matrix Language Frame** configuration (Myers-Scotton 1993): Spanish is the *matrix* language supplying morphosyntax and system morphemes; English is the *embedded* language supplying content morphemes, with multi-word feature names such as **Exec Report** entering whole as embedded-language islands. Iakovenko and Hain (2024, arXiv:2410.02521) confirm the direction empirically for this exact language pair: in real English/Spanish code-switching, Spanish is preferred as the matrix.

The rule extends past nouns: Spanish supplies the **verbs** too. *"Aguántame tantito"*, *"ya merito"*, *"ahorita"* — the Mexican register is the carrier, and the English technical noun rides inside it untouched.

## The adjudication criterion: *biunivocidad*

Where a term is contested, the decision is not taste. Lazaro Carreter (1998: 587), quoted in Garriga Escribano (2022), endorses **unadapted** technical anglicisms precisely because doing so *"facilita internacionalmente la biunivocidad que conviene a la terminologia cientifica"* - it preserves the one-term-to-one-concept mapping technical vocabulary depends on. That gives a test:

| | Rule |
|---|---|
| **KEEP ENGLISH** | when a Spanish rendering would BREAK the 1:1 mapping - the term names a specific technical concept whose Spanish form is invented, ambiguous, or collides with another domain. *Pod, Container, deployment, commit, log, pattern, token, endpoint.* |
| **USE SPANISH** | when an exact, unambiguous, everyday equivalent already exists and every speaker uses it. *ruta, comando, puerto, contexto, carpeta, archivo, pantalla, ventana.* |

Nothing is lost by *"la ruta del archivo"*. Everything is lost by *"la vaina"* for a Pod.

## Summary

| Family | N | Moves? | Purpose |
|---|---:|---|---|
| `MACHINE_SENTINELS` | 25 | **no** | Literals the MACHINE reads back. Translating one does not spoil the style, it breaks the protocol. |
| `PRODUCT_TERMS` | 29 | **no** | Tlamatini's own product vocabulary. Angela named MCPs and Wizard explicitly; the toolbar toggles are feature NAMES. |
| `AGENT_DISPLAY_NAMES` | 93 | **no** | The asset names. Case and hyphenation are FUNCTIONAL - the canvas connection handler compares the hyphenated literal. |
| `TOOL_NAMES` | 94 | **no** | Wrapped tool identifiers and their Tool-row descriptions. Pure machine surface that happens to be visible in the Exec Report. |
| `TECH_CONTAINERS` | 17 | **no** | Containers and orchestration. Angela's own example sentence lives here: Pod, Container, Kubernetes, deployment, LPAR. |
| `TECH_VCS` | 16 | **no** | Version control. 'Haz un commit y push' is how it is said. |
| `TECH_BUILD` | 13 | **no** | Build and release vocabulary. |
| `TECH_RUNTIME` | 20 | **no** | Runtime and diagnostics. 'log' is the load-bearing one. |
| `TECH_WEB` | 18 | **no** | Web and API vocabulary. |
| `TECH_DATA` | 13 | **no** | Data and persistence. |
| `TECH_FILES_OS` | 22 | **no** | Files, OS and shell. |
| `TECH_AI` | 18 | **no** | AI / LLM vocabulary - the newest and least calqued domain. |
| `TECH_FIRMWARE` | 15 | **no** | Hardware and firmware (STM32er / ESP32er / Arduiner). |
| `TECH_SECURITY` | 15 | **no** | Security (Kalier / Nmapper / Discoverer). |
| `SPANISH_PREFERRED` | 26 | **yes** | English -> the Spanish rendering we DO want. |
| `FORBIDDEN_SPANISH_RENDERINGS` | 34 | n/a | Wrong Spanish -> the English required instead. The 'Exclusions' half of a Microsoft-style termbase. |

| Artifact | Count |
|---|---:|
| Termbase entries (with cross-family overlap) | 408 |
| Distinct terms after de-duplication | 394 |
| Spanish carrier terms mapped to English hints (`lexicon_es`) | 209 |
| Distinct canonical hints those map onto | 102 |
| GUI strings catalogued (`ui_es`) | 198 |
| ... rendered into Spanish | 164 |
| ... deliberately kept identical (they ARE terms) | 34 |
| Reviewable rows in `terms.csv` | 420 |

## `terms.csv` — the reviewable source of truth

The Python families above are what the runtime imports; `terms.csv` is the same inventory in a form a human translator can review, diff and argue with in a pull request. Each row carries a **policy**:

| Policy | N | Meaning |
|---|---:|---|
| `KEEP` | 178 | stays English — translating it would break *biunivocidad* |
| `TRANSLATE` | 32 | has an exact everyday Spanish equivalent, so it moves |
| `ASSET` | 92 | an agent / product name — byte-exact, case and hyphens are functional |
| `MACHINE` | 118 | a protocol literal the machine reads back — translating it breaks parsing |

### Every `TRANSLATE` row (32)

These are the only terms in the whole inventory that change language. Everything else is KEEP, ASSET or MACHINE.

| English | Spanish | Domain |
|---|---|---|
| `Cancel` | **Cancelar** | ui |
| `Close` | **Cerrar** | ui |
| `Command` | **comando** | ui |
| `container image` | **imagen de container** | containers |
| `Context` | **contexto** | ai |
| `Continue` | **Continuar** | ui |
| `Date` | **fecha** | ui |
| `Delete` | **Eliminar** | ui |
| `Directory` | **directorio** | ui |
| `Docker image` | **imagen de Docker** | containers |
| `External MCPs` | **MCPs Externos** | product |
| `File` | **archivo** | ui |
| `Folder` | **carpeta** | ui |
| `Help` | **Ayuda** | ui |
| `Image` | **imagen** | containers |
| `Images` | **imágenes** | containers |
| `Line` | **línea** | ui |
| `Name` | **nombre** | ui |
| `Network` | **red** | ui |
| `Open` | **Abrir** | ui |
| `Page` | **página** | ui |
| `Password` | **contraseña** | ui |
| `Port` | **puerto** | firmware |
| `Save` | **Guardar** | ui |
| `Screen` | **pantalla** | ui |
| `Search` | **Buscar** | ui |
| `Send` | **Enviar** | ui |
| `Size` | **tamaño** | ui |
| `Step-by-Step` | **Paso-a-Paso** | product |
| `User` | **usuario** | ui |
| `Version` | **versión** | ui |
| `Window` | **ventana** | ui |

## Families that never move

### `MACHINE_SENTINELS` — 25 terms

Literals the MACHINE reads back. Translating one does not spoil the style, it breaks the protocol.

- `END-RESPONSE` · `BEGIN-CODE` · `END-CODE` · `INI_SECTION_` · `END_SECTION_` · `<!--TLAMATINI_EXEC_REPORT_BOUNDARY-->`
- `TLM_VERDICT::` · `FRAME_VERDICT` · `FINAL_VERDICT` · `CONFIDENCE` · `VERDICT:` · `PASS_OK`
- `FAIL_NO_MOTION` · `FAIL_WRONG_MOTION` · `UNCLEAR` · `ANALYSIS_ERROR` · `APPROVE` · `REQUEST_CHANGES`
- `COMMENT` · `completed` · `failed` · `stopped` · `running` · `SUCCESS`
- `FAILURE`

### `PRODUCT_TERMS` — 29 terms

Tlamatini's own product vocabulary. Angela named MCPs and Wizard explicitly; the toolbar toggles are feature NAMES.

- `Tlamatini` · `XAIHT` · `ACPX` · `ACPXer` · `MCP` · `MCPs`
- `Multi-Turn` · `Exec report` · `Exec Report` · `Ask Execs` · `Skills` · `Skill`
- `Flow` · `FlowCreator` · `FlowHypervisor` · `FlowBacker` · `Wizard` · `Access Keys Wizard`
- `Prompt Catalog` · `Catalogo de Prompts` · `System-Metrics` · `Files-Search` · `MCP Doctor` · `Parametrizer`
- `Create Flow` · `Exec` · `TeleTlamatini` · `Angela Lopez Mendoza` · `Angela López Mendoza`

### `AGENT_DISPLAY_NAMES` — 93 terms

The asset names. Case and hyphenation are FUNCTIONAL - the canvas connection handler compares the hyphenated literal.

- `ACPXer` · `AND` · `Analyzer` · `Apirer` · `Arduiner` · `Asker`
- `AudioPlayer` · `Barrier` · `Blenderer` · `Camcorder` · `Cleaner` · `Counter`
- `Crawler` · `Croner` · `De-Compresser` · `Deleter` · `Discoverer` · `Dockerer`
- `ESP32er` · `ESPHomer` · `Editor` · `Emailer` · `Ender` · `Executer`
- `File-Creator` · `File-Extractor` · `File-Interpreter` · `FlowBacker` · `FlowCreator` · `FlowHypervisor`
- `Forker` · `Gateway Relayer` · `Gatewayer` · `Gitter` · `Globber` · `Googler`
- `Grepper` · `Image-Interpreter` · `Instant Messaging Doctor` · `J-Decompiler` · `Jenkinser` · `Kalier`
- `Keyboarder` · `Kuberneter` · `Kyber Cipher` · `Kyber Deciph` · `Kyber Keygen` · `Kyber-Cipher`
- `Kyber-DeCipher` · `Kyber-KeyGen` · `MCP Doctor` · `Mongoxer` · `Monitor Netstat` · `Monitor-Log`
- `Mouser` · `Move File` · `Mover` · `Nmapper` · `Node Manager` · `Notifier`
- `OR` · `PDFer` · `PSer` · `Parametrizer` · `Playwrighter` · `Prompter`
- `Pythonxer` · `Raiser` · `RecMailer` · `Recmailer` · `Recorder` · `Reviewer`
- `SCPer` · `SQLer` · `SSHer` · `STM32er` · `Send Email` · `Shoter`
- `Sleeper` · `Starter` · `Stopper` · `Summarize Text` · `Summarizer` · `Talker`
- `TeleTlamatini` · `Telegrammer` · `Unrealer` · `Video-Analyzer` · `VideoPlayer` · `Whatsapper`
- `Whisperer` · `Windower` · `Zavuerer`

### `TOOL_NAMES` — 94 terms

Wrapped tool identifiers and their Tool-row descriptions. Pure machine surface that happens to be visible in the Exec Report.

- `acp_doctor` · `acp_kill` · `acp_list_sessions` · `acp_relay` · `acp_send` · `acp_send_and_wait`
- `acp_session_status` · `acp_spawn` · `acp_transcript` · `agent_parametrizer` · `agent_starter` · `agent_stat_getter`
- `agent_stopper` · `chat_agent_apirer` · `chat_agent_arduiner` · `chat_agent_asker` · `chat_agent_audioplayer` · `chat_agent_blenderer`
- `chat_agent_camcorder` · `chat_agent_crawler` · `chat_agent_de_compresser` · `chat_agent_deleter` · `chat_agent_discoverer` · `chat_agent_dockerer`
- `chat_agent_editor` · `chat_agent_esp32er` · `chat_agent_esphomer` · `chat_agent_executer` · `chat_agent_file_creator` · `chat_agent_file_extractor`
- `chat_agent_file_interpreter` · `chat_agent_flowcreator` · `chat_agent_gitter` · `chat_agent_globber` · `chat_agent_grepper` · `chat_agent_image_interpreter`
- `chat_agent_instant_messaging_doctor` · `chat_agent_j_decompiler` · `chat_agent_jenkinser` · `chat_agent_kalier` · `chat_agent_keyboarder` · `chat_agent_kuberneter`
- `chat_agent_kyber_cipher` · `chat_agent_kyber_deciph` · `chat_agent_kyber_keygen` · `chat_agent_mcp_doctor` · `chat_agent_mongoxer` · `chat_agent_monitor_log`
- `chat_agent_monitor_netstat` · `chat_agent_mouser` · `chat_agent_move_file` · `chat_agent_nmapper` · `chat_agent_notifier` · `chat_agent_pdfer`
- `chat_agent_playwrighter` · `chat_agent_prompter` · `chat_agent_pser` · `chat_agent_pythonxer` · `chat_agent_recmailer` · `chat_agent_recorder`
- `chat_agent_run_list` · `chat_agent_run_log` · `chat_agent_run_status` · `chat_agent_run_stop` · `chat_agent_run_wait` · `chat_agent_scper`
- `chat_agent_send_email` · `chat_agent_shoter` · `chat_agent_sleeper` · `chat_agent_sqler` · `chat_agent_ssher` · `chat_agent_stm32er`
- `chat_agent_summarize_text` · `chat_agent_talker` · `chat_agent_telegrammer` · `chat_agent_unrealer` · `chat_agent_video_analyzer` · `chat_agent_videoplayer`
- `chat_agent_whatsapper` · `chat_agent_whisperer` · `chat_agent_windower` · `chat_agent_zavuerer` · `decompile_java` · `execute_command`
- `execute_file` · `execute_netstat` · `get_current_time` · `googler` · `invoke_skill` · `launch_view_image`
- `list_acp_agents` · `list_skills` · `unzip_file` · `window_present`

### `TECH_CONTAINERS` — 17 terms

Containers and orchestration. Angela's own example sentence lives here: Pod, Container, Kubernetes, deployment, LPAR.

- `Pod` · `Container` · `Cluster` · `Deployment` · `Namespace` · `Docker image`
- `container image` · `Compose` · `Registry` · `Kubernetes` · `Docker` · `Helm`
- `Node` · `Ingress` · `Sidecar` · `Orchestration` · `LPAR`

### `TECH_VCS` — 16 terms

Version control. 'Haz un commit y push' is how it is said.

- `Commit` · `Branch` · `Merge` · `Pull Request` · `Rebase` · `Push`
- `Pull` · `Repo` · `Repository` · `Checkout` · `Diff` · `Tag`
- `Stash` · `Fork` · `Remote` · `Upstream`

### `TECH_BUILD` — 13 terms

Build and release vocabulary.

- `Build` · `Release` · `Deploy` · `Pipeline` · `Rollback` · `Artifact`
- `CI` · `CD` · `Job` · `Runner` · `Stage` · `Installer`
- `Package`

### `TECH_RUNTIME` — 20 terms

Runtime and diagnostics. 'log' is the load-bearing one.

- `Pattern` · `Log` · `Debug` · `Trace` · `Timeout` · `Thread`
- `Process` · `Daemon` · `Cache` · `Buffer` · `Stack` · `Heap`
- `Crash` · `Core dump` · `Handler` · `Callback` · `Worker` · `Runtime`
- `Overhead` · `Deadlock`

### `TECH_WEB` — 18 terms

Web and API vocabulary.

- `Endpoint` · `API` · `REST` · `Webhook` · `Request` · `Response`
- `Header` · `Payload` · `Token` · `Query` · `Socket` · `WebSocket`
- `Proxy` · `Gateway` · `Status code` · `Rate limit` · `Polling` · `Streaming`

### `TECH_DATA` — 13 terms

Data and persistence.

- `Data mining` · `Schema` · `Index` · `Backup` · `Dump` · `Row`
- `Record` · `Dataset` · `Migration` · `Transaction` · `Rollback` · `Chunk`
- `Batch`

### `TECH_FILES_OS` — 22 terms

Files, OS and shell.

- `Path` · `Screenshot` · `Script` · `Shell` · `Prompt` · `Pipe`
- `Symlink` · `Mount` · `Glob` · `Wildcard` · `Binary` · `Output`
- `Input` · `Hardware` · `Software` · `Router` · `Byte` · `Kilobyte`
- `Megabyte` · `Gigabyte` · `Terabyte` · `Spam`

### `TECH_AI` — 18 terms

AI / LLM vocabulary - the newest and least calqued domain.

- `Prompt` · `Token` · `Embedding` · `Context` · `Chain` · `Agent`
- `Tool` · `Model` · `Fine-tuning` · `RAG` · `LLM` · `Inference`
- `Checkpoint` · `Dataset` · `Temperature` · `Multi-Turn` · `Streaming` · `Vision`

> **Contradiction:** `Context` also appears in `SPANISH_PREFERRED`. Runtime resolves this correctly (the Spanish rendering wins, because `dnt.py` subtracts `SPANISH_PREFERRED` from both the strict and the loose sets), but the file asserts two things at once.

### `TECH_FIRMWARE` — 15 terms

Hardware and firmware (STM32er / ESP32er / Arduiner).

- `Firmware` · `Board` · `Serial` · `Port` · `Baud` · `Flash`
- `Chip` · `Bootloader` · `Sketch` · `Toolchain` · `Debugger` · `Probe`
- `Pin` · `Upload` · `Monitor`

> **Contradiction:** `Port` also appears in `SPANISH_PREFERRED`. Runtime resolves this correctly (the Spanish rendering wins, because `dnt.py` subtracts `SPANISH_PREFERRED` from both the strict and the loose sets), but the file asserts two things at once.

### `TECH_SECURITY` — 15 terms

Security (Kalier / Nmapper / Discoverer).

- `Hash` · `Key` · `Secret` · `Scan` · `Exploit` · `Payload`
- `Hacker` · `Cracker` · `Malware` · `Firewall` · `Certificate` · `Credential`
- `Vulnerability` · `Pentest` · `Scope`

## `SPANISH_PREFERRED` — the 26 terms that DO become Spanish

| English | Spanish | Why it is safe |
|---|---|---|
| `Cancel` | **Cancelar** | generic verb - carrier |
| `Close` | **Cerrar** | generic verb - carrier |
| `Command` | **comando** | *comando* is in the RAE dictionary and said by everyone |
| `Context` | **contexto** | *contexto* is a direct cognate |
| `Continue` | **Continuar** | generic verb - carrier |
| `Date` | **fecha** | everyday noun |
| `Delete` | **Eliminar** | generic verb - carrier |
| `Directory` | **directorio** | cognate, unambiguous |
| `File` | **archivo** | everyday noun, exact equivalent |
| `Folder` | **carpeta** | everyday noun, exact equivalent |
| `Help` | **Ayuda** | generic noun - carrier |
| `Line` | **línea** | everyday noun |
| `Name` | **nombre** | everyday noun |
| `Network` | **red** | *red* is universal |
| `Open` | **Abrir** | generic verb - carrier |
| `Page` | **página** | everyday noun |
| `Password` | **contraseña** | *contraseña* is universal |
| `Port` | **puerto** | *puerto* is universal |
| `Save` | **Guardar** | generic verb - carrier, not lexicon |
| `Screen` | **pantalla** | *pantalla* is universal |
| `Search` | **Buscar** | generic verb - carrier |
| `Send` | **Enviar** | generic verb - carrier |
| `Size` | **tamaño** | everyday noun |
| `User` | **usuario** | *usuario* is universal |
| `Version` | **versión** | direct cognate |
| `Window` | **ventana** | *ventana* is universal |

## `FORBIDDEN_SPANISH_RENDERINGS` — the 34 mistranslations the build rejects

These are the words a careless translator reaches for. Each one breaks *biunivocidad*: the Spanish either names a different thing, or names nothing at all.

| Never write | Required instead |
|---|---|
| *asistente* | **Wizard** |
| *bitacora* | **Log** |
| *bitácora* | **Log** |
| *cadena* | **Chain** |
| *captura de pantalla* | **Screenshot** |
| *confirmacion* | **Commit** |
| *confirmación* | **Commit** |
| *consulta* | **Query** |
| *contenedor* | **Container** |
| *cumulo* | **Cluster** |
| *cúmulo* | **Cluster** |
| *despliegue* | **Deployment** |
| *entrada* | **Input** |
| *estado* | **Status** |
| *exito* | **SUCCESS** |
| *fallo* | **FAILURE** |
| *ficha* | **Token** |
| *guion* | **Script** |
| *indicacion* | **Prompt** |
| *indicaciones* | **Prompts** |
| *instantanea* | **Screenshot** |
| *instantánea* | **Screenshot** |
| *mineria de datos* | **Data mining** |
| *minería de datos* | **Data mining** |
| *patron* | **pattern** |
| *patrón* | **pattern** |
| *punto final* | **Endpoint** |
| *rama* | **Branch** |
| *registro* | **Log** |
| *respaldo* | **Backup** |
| *ruta* | **Path** |
| *salida* | **Output** |
| *vaina* | **Pod** |
| *éxito* | **SUCCESS** |

## `lexicon_es` — 209 Spanish CARRIER terms mapped to English hints

This is a different mechanism and must not be confused with the termbase. It never renames anything and is never shown to a user: it lifts a Spanish **request** into the canonical English key space the capability scorer already understands, so *"borra los archivos"* scores like *"delete the files"*. Every value already exists in the registry's own hint corpus - nothing is invented.

Note the consequence of the register: a sentence like *"haciendo un Pod en Dockerer"* needs **no** entry here at all, because its technical nouns are already English and hit the hints directly. What this table covers is the Spanish carrier - the verbs and connectives.

| Spanish | -> canonical English hints |
|---|---|
| `abre` | `open` |
| `abreme` | `open` |
| `abriendo` | `open` |
| `abrir` | `open` |
| `agrega` | `edit file` |
| `agregar` | `edit file` |
| `almacena` | `save file` |
| `almacenar` | `save file` |
| `altavoces` | `speaker`, `speakers` |
| `altavoz` | `speaker`, `speakers` |
| `anade` | `edit file` |
| `anadir` | `edit file` |
| `analiza` | `analyze file`, `analyze document` |
| `analizame` | `analyze file`, `analyze document` |
| `analizando` | `analyze file`, `analyze document` |
| `analizar` | `analyze file`, `analyze document` |
| `archivo` | `file`, `files` |
| `archivos` | `file`, `files` |
| `arranca` | `run command` |
| `arrancar` | `run command` |
| `avisa` | `notify`, `notification` |
| `avisar` | `notify`, `notification` |
| `baja` | `download` |
| `bajar` | `download` |
| `base de datos` | `database`, `sql`, `query` |
| `bocina` | `speaker`, `speakers` |
| `bocinas` | `speaker`, `speakers` |
| `borra` | `delete file`, `erase file`, `remove file` |
| `borrame` | `delete file`, `erase file`, `remove file` |
| `borrando` | `delete file`, `erase file`, `remove file` |
| `borrar` | `delete file`, `erase file`, `remove file` |
| `busca` | `search`, `find in files` |
| `buscame` | `search`, `find in files` |
| `buscando` | `search`, `find in files` |
| `buscar` | `search`, `find in files` |
| `camara` | `camera`, `webcam` |
| `cambia` | `modify file`, `edit file` |
| `cambiar` | `modify file`, `edit file` |
| `captura de pantalla` | `screenshot`, `screen capture`, `take a screenshot` |
| `capturas de pantalla` | `screenshot`, `screen capture`, `take a screenshot` |
| `carpeta` | `folder`, `directory` |
| `carpetas` | `folder`, `directory` |
| `codigo` | `source code` |
| `codigo fuente` | `source code`, `source` |
| `comando` | `command`, `run command` |
| `comandos` | `command`, `run command` |
| `compila` | `compile`, `build` |
| `compilando` | `compile`, `build` |
| `compilar` | `compile`, `build` |
| `comprime` | `zip` |
| `comprimir` | `zip` |
| `conecta` | `remote host` |
| `conectando` | `remote host` |
| `conectar` | `remote host` |
| `conectate` | `remote host` |
| `consulta` | `query` |
| `copia` | `move file` |
| `copiando` | `move file` |
| `copiar` | `move file` |
| `corre` | `run command` |
| `correo` | `email`, `mail` |
| `correo electronico` | `email`, `mail`, `send email` |
| `correos` | `email`, `mail` |
| `correr` | `run command` |
| `crea` | `create file`, `write file` |
| `creame` | `create file`, `write file` |
| `creando` | `create file`, `write file` |
| `crear` | `create file`, `write file` |
| `decir` | `say`, `say out loud` |
| `decompila` | `decompile` |
| `decompilar` | `decompile` |
| `descarga` | `download` |
| `descargando` | `download` |
| `descargar` | `download` |
| `descompila` | `decompile` |
| `descompilar` | `decompile` |
| `descomprime` | `unzip`, `decompress`, `extract archive` |
| `descomprimir` | `unzip`, `decompress`, `extract archive` |
| `di` | `say`, `say out loud` |
| `dilo` | `say`, `say out loud` |
| `directorio` | `directory`, `folder` |
| `directorios` | `directory`, `folder` |
| `disco duro` | `disk`, `storage` |
| `ejecuta` | `run command` |
| `ejecutame` | `run command` |
| `ejecutando` | `run command` |
| `ejecutar` | `run command` |
| `elimina` | `delete file`, `erase file`, `remove file` |
| `eliminame` | `delete file`, `erase file`, `remove file` |
| `eliminando` | `delete file`, `erase file`, `remove file` |
| `eliminar` | `delete file`, `erase file`, `remove file` |
| `en voz alta` | `say out loud`, `read aloud`, `text to speech` |
| `encontrar` | `search`, `find in files` |
| `encuentra` | `search`, `find in files` |
| `ensename` | `show` |
| `ensenar` | `show` |
| `envia` | `send email` |
| `enviale` | `send email` |
| `enviame` | `send email` |
| `enviando` | `send email` |
| `enviar` | `send email` |
| `escanea` | `port scan` |
| `escanear` | `port scan` |
| `escribe` | `write file` |
| `escribeme` | `write file` |
| `escribiendo` | `write file` |
| `escribir` | `write file` |
| `flashea` | `flash firmware` |
| `flashear` | `flash firmware` |
| `foto` | `take a photo` |
| `fotos` | `take a photo` |
| `genera` | `generate a document` |
| `generame` | `generate a document` |
| `generando` | `generate a document` |
| `generar` | `generate a document` |
| `graba` | `record audio`, `record video` |
| `grabame` | `record audio`, `record video` |
| `grabando` | `record audio`, `record video` |
| `grabar` | `record audio`, `record video` |
| `guarda` | `save file` |
| `guardame` | `save file` |
| `guardando` | `save file` |
| `guardar` | `save file` |
| `imagen` | `image`, `picture` |
| `imagenes` | `image`, `picture` |
| `instala` | `install` |
| `instalando` | `install` |
| `instalar` | `install` |
| `lanza` | `run command` |
| `lanzar` | `run command` |
| `lee` | `read`, `read document` |
| `leeme` | `read`, `read document` |
| `leer` | `read`, `read document` |
| `leyendo` | `read`, `read document` |
| `linea de comando` | `command`, `terminal`, `shell` |
| `linea de comandos` | `command`, `terminal`, `shell` |
| `lista` | `list files`, `find files` |
| `listame` | `list files`, `find files` |
| `listar` | `list files`, `find files` |
| `localiza` | `search`, `locate` |
| `localizar` | `search`, `locate` |
| `manda` | `send email` |
| `mandale` | `send email` |
| `mandame` | `send email` |
| `mandar` | `send email` |
| `maquina remota` | `remote host` |
| `mensaje` | `send a message`, `chat message` |
| `mensajes` | `send a message`, `chat message` |
| `microfono` | `microphone`, `mic` |
| `modifica` | `modify file`, `edit file` |
| `modificar` | `modify file`, `edit file` |
| `mostrando` | `show` |
| `mostrar` | `show` |
| `mover` | `move file`, `relocate file` |
| `moviendo` | `move file`, `relocate file` |
| `muestra` | `show` |
| `muestrame` | `show` |
| `mueve` | `move file`, `relocate file` |
| `navegador` | `browser` |
| `notifica` | `notify`, `notification` |
| `notificar` | `notify`, `notification` |
| `pagina` | `web page` |
| `pagina web` | `web page`, `website` |
| `paginas` | `web page` |
| `pantalla completa` | `fullscreen video` |
| `proceso` | `process` |
| `procesos` | `process` |
| `proyecto` | `project` |
| `puerto` | `port`, `ports` |
| `puertos` | `port`, `ports` |
| `raton` | `mouse` |
| `red` | `network` |
| `redes` | `network` |
| `reemplaza` | `replace`, `find and replace`, `replace in file` |
| `reemplazar` | `replace`, `find and replace`, `replace in file` |
| `remite` | `send email` |
| `remitir` | `send email` |
| `reproduce` | `play audio`, `play video` |
| `reproducir` | `play audio`, `play video` |
| `resume` | `summarize`, `summary` |
| `resumeme` | `summarize`, `summary` |
| `resumen` | `summarize`, `summary` |
| `resumir` | `summarize`, `summary` |
| `revisa` | `read`, `show` |
| `revisame` | `read`, `show` |
| `revisando` | `read`, `show` |
| `revisar` | `read`, `show` |
| `ruta` | `path`, `paths` |
| `rutas` | `path`, `paths` |
| `servidor` | `remote host` |
| `servidores` | `remote host` |
| `sitio` | `website` |
| `sonido` | `play sound`, `record sound` |
| `sube` | `transfer file` |
| `subiendo` | `transfer file` |
| `subir` | `transfer file` |
| `suprime` | `delete file`, `erase file`, `remove file` |
| `suprimir` | `delete file`, `erase file`, `remove file` |
| `sustituir` | `replace`, `find and replace`, `replace in file` |
| `sustituye` | `replace`, `find and replace`, `replace in file` |
| `teclado` | `keyboard` |
| `toma` | `take a photo` |
| `tomame` | `take a photo` |
| `tomar` | `take a photo` |
| `transcribe` | `transcribe`, `speech to text` |
| `transcribir` | `transcribe`, `speech to text` |
| `ventana` | `window`, `windows` |
| `ventanas` | `window`, `windows` |
| `voz` | `voice` |

## GUI strings deliberately kept identical (34 of 198)

Where the Spanish equals the English, it is because the string **is** a term - not because it was skipped. The test `test_intentional_identities_are_product_terms` fails the build if an identity cannot be justified by a do-not-translate term.

- `ACPX` · `ACPX-Skills` · `Access Keys Wizard` · `Access aimed`
- `Agentic Control Panel` · `Agents` · `Agents:` · `Ask Execs`
- `Chained` · `DB` · `Email` · `Embedding`
- `Exec report` · `Files-Search` · `Flow Control Panel:` · `Image interpreter 1`
- `Image interpreter 2` · `Image merger` · `Kali server (Kalier)` · `MCP Files search`
- `MCPs` · `Multi-Turn` · `Service` · `Status`
- `Summarizer` · `System-Metrics` · `Telegram` · `Tlamatini (Agentic Control Panel)`
- `Tools` · `Transport` · `URLs` · `Unified`
- `WhatsApp` · `canvas`

## Stage 0 — the per-model capability gate

Everything above assumes the model on the other end can actually hold Spanish. `agent/i18n/model_caps.py` is the gate that decides whether to trust it, and it sits BEFORE the N1/N2/N3 pipeline:

| Tier | What it means | Effect on this termbase |
|---|---|---|
| `FLUENT` | the model handles Spanish and the register | the user's own words pass through untouched — no English hint expansion |
| `ASSIST` | partial competence | the carrier terms from `lexicon_es` are expanded into English hints so the capability scorer still routes correctly |
| `WEAK` | cannot be trusted with Spanish | full expansion |
| `UNKNOWN` | not measured yet | treated as `ASSIST` — the recoverable direction |

Three properties matter for terminology work, and each is test-pinned:

- **Identity is the model, not the family.** A local model is keyed by its GGUF sha256, a cloud model by its exact id (`:cloud` suffix preserved), so two builds of "the same" model are never confused for one another.
- **The seed can never demote.** A prior belief may only say `FLUENT` or `UNKNOWN`; only a measured probe or observed failures can lower a model.
- **Observation demotes, never promotes.** Passive verification watches real answers and can drop a model a tier, but earning a tier requires the graded probe.

Tokenizer *fertility* was measured as a competence signal and **rejected** — it tracks tokenizer design, not language ability. `model_caps.py` is asserted to contain no fertility heuristic.

## How this is enforced

| Mechanism | File | What it guarantees |
|---|---|---|
| DNT invariant | `agent/test_ui_dnt.py` | Every do-not-translate term present in an English GUI string is present, byte-identical, in its Spanish rendering. |
| Case enforcement | same | An asset name that survives in the WRONG case (`Stm32er` for `STM32er`) fails, which a case-insensitive reader would miss. |
| Angela's credit line | same | Angela López Mendoza's credit maps to itself, asserted explicitly rather than by omission. |
| Harvest, never transcribe | `agent/i18n/dnt.py` | The asset names are read at runtime from the registries that define them, so a second hand-maintained copy cannot rot. |
| Checker is not vacuous | `agent/test_ui_dnt.py` | Separate tests prove the checker DOES reject a renamed asset and an over-translated term. |
| Capability gate | `agent/test_model_caps.py` | Identity keying, seed-cannot-demote, observe-cannot-promote, fail-open, and the absence of any fertility heuristic. |
| This document | `generate_terminology.py` | Regenerated from the live modules; `--check` fails when the committed copy is stale. |

---

*Generated by `docs/research/spanish-localization/generate_terminology.py` from the live `agent/i18n/` files. Regenerate rather than edit by hand.*
