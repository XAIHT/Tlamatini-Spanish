<!--
═══════════════════════════════════════════════════════════════════
  ✦  T L A M A T I N I  ✦   —   "one who knows"
  Created by  Angela López Mendoza   ·   @angelahack1
  Developer · Architect · Creator of Tlamatini
  Tlamatini Author Banner — do not remove (Angela's name is kept in every build)
═══════════════════════════════════════════════════════════════════
-->
<p align="center">
  <img src="Tlamatini.jpg" alt="Tlamatini" width="180" height="180" />
</p>

<h1 align="center">Tlamatini</h1>

<p align="center">
  <b>La asistente de desarrollo con IA local-first, con un diseñador visual de flows — y el alcance para tocar hardware, motores 3D y cualquier herramienta externa.</b><br/>
  <i>"la que sabe" — no se limita a editar código. Flashea tu board, maneja tu motor y orquesta flows completos de agents sobre un canvas. En tu propia máquina.</i>
</p>

<p align="center">
  <b>💰 Unos $200 al AÑO — no $200 al MES.</b><br/>
  Los planes frontera como GPT-5.4 o Claude Opus cuestan alrededor de <b>$200 al mes</b>. <b>Tlamatini es gratuita y de código abierto</b> — tu única factura es <b>Ollama Pro (~$200 al <i>año</i>, pagados a Ollama, no a nosotros)</b>, y encima de eso ella apila <b>87 agent types y 75+ tools</b>: potencia comparable por cerca de <b>una doceava parte</b> del precio, todo en tu propia máquina.
</p>

<p align="center">
  <a href="https://discord.gg/WFQsrskgc"><img src="https://img.shields.io/badge/DISCORD-JOIN%20US-5865F2?style=for-the-badge&labelColor=2D2D2D&logo=discord&logoColor=white" alt="Únete a nuestro Discord"/></a>
  <a href="https://github.com/XAIHT/Tlamatini/releases/tag/v1.48.2s"><img src="https://img.shields.io/badge/VERSION-v1.48.2s-1E90FF?style=for-the-badge&labelColor=2D2D2D" alt="Versión"/></a>
  <a href="https://www.python.org/downloads/release/python-31210/"><img src="https://img.shields.io/badge/PYTHON-3.12.10-3776AB?style=for-the-badge&labelColor=2D2D2D&logo=python&logoColor=white" alt="Python"/></a>
  <a href="#instalación"><img src="https://img.shields.io/badge/PLATFORM-WIN%2010%20%7C%2011-0078D6?style=for-the-badge&labelColor=2D2D2D&logo=windows&logoColor=white" alt="Plataforma"/></a>
  <a href="#-la-lista-completa-de-capacidades"><img src="https://img.shields.io/badge/AGENT%20TYPES-87-8A2BE2?style=for-the-badge&labelColor=2D2D2D" alt="87 agent types"/></a>
  <a href="#-la-lista-completa-de-capacidades"><img src="https://img.shields.io/badge/TOOLS-75-16A34A?style=for-the-badge&labelColor=2D2D2D" alt="75 tools"/></a>
  <a href="https://github.com/XAIHT/Tlamatini/blob/main/LICENSE"><img src="https://img.shields.io/badge/LICENSE-MIT-1E90FF?style=for-the-badge&labelColor=2D2D2D" alt="Licencia"/></a>
</p>

<p align="center">
  <a href="https://xaiht.org">🌐 Sitio web</a> ·
  <a href="https://www.youtube.com/watch?v=4MyRXBahHuU&t=41s">▶️ Teaser de un minuto</a> ·
  <a href="BookOfTlamatini.md">📖 Documentación completa</a> ·
  <a href="https://discord.gg/WFQsrskgc">💬 Discord</a>
</p>

<p align="center">
  <b>💬 <a href="https://discord.gg/WFQsrskgc">Únete a la comunidad de Tlamatini en Discord</a></b> — pide ayuda, muestra lo que construyes, reporta bugs y da forma al roadmap.
</p>

---

## 🚀 Empieza aquí — 5 pasos para una Tlamatini con potencia en la nube

La idea completa en una línea: **no pagues $200 al mes por un modelo frontera.** **Tlamatini es gratuita** — tu único costo es **Ollama Pro (~$200 al año, pagados a Ollama, no a nosotros)**; apunta Tlamatini hacia él y maneja **87 agent types y 75+ tools** desde tu propia máquina. Esta es la instalación completa.

### 1 · Instala Tlamatini

Elige **una** de las dos rutas. **Tlamatini en sí es gratuita** — a nosotros nunca nos pagas nada; el único costo es Ollama (Paso 3).

#### 🟢 Opción A — Instalador de la release (recomendado · sin necesidad de Python)

Lo mejor para la mayoría. El instalador trae su propio **Python 3.12.10** y todas las dependencias, así que no instalas nada más.

1. Abre la **[página de Releases](https://github.com/XAIHT/Tlamatini/releases)** y descarga el instalador más reciente (`.exe`).
2. Ejecútalo y sigue el asistente.
3. Lanza **Tlamatini** desde el acceso directo del menú Inicio.
4. Tu navegador se abre en **`http://127.0.0.1:8000/`** — inicia sesión con **user / changeme**. *(`8000` es el puerto por defecto; si está ocupado o si Windows lo tiene reservado, define `django_port` en `config.json` — mira la nota sobre el puerto más abajo.)*

> 🔄 Actualizar después es un solo clic: **About ▸ Check for updates** dentro de la app — conserva tu config, tu base de datos y tus keys.

#### 🔵 Opción B — Desde el código fuente (para desarrolladores)

Lo mejor si quieres leer, modificar o contribuir al código. Requiere **Python 3.12.10** y **git** ya instalados.

```bash
git clone https://github.com/XAIHT/Tlamatini.git
cd Tlamatini
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python Tlamatini/manage.py migrate
python Tlamatini/manage.py runserver --noreload
# then open http://127.0.0.1:8000/   (default login: user / changeme)
```

> **`--noreload` es opcional (desde 2026-07-11):** ahora `python Tlamatini/manage.py runserver` a secas arranca limpio y se recarga sola cuando editas el código. Antes levantaba dos veces los puertos auxiliares del MCP `:8765` / `:50051` y reventaba con `WinError 10048`; se corrigió con una compuerta consciente del reloader en `agent/apps.py`.

<details>
<summary><b>🔌 ¿El puerto 8000 ya está ocupado? ¿Tlamatini no arranca? (<code>WinError 10013</code>) — cambia una línea</b></summary>

<br>

**`8000` es solo el valor por defecto.** Desde **v1.40.1** el puerto web vive en tu **`config.json`**:

```jsonc
"django_port": 8000     // ← put any free port here, e.g. 9000
```

Reinicia Tlamatini y ella levanta en el puerto nuevo — **sin recompilar, sin editar código**. Todas las rutas de arranque lo respetan: el acceso directo del escritorio, el doble clic sobre un archivo `.flw`, el navegador que se abre solo, y `runserver` / `startserver` desde el código fuente.

**Por qué podrías necesitarlo.** Si Windows (normalmente **Hyper-V / WSL / Docker**) tiene *reservado* el puerto 8000, Tlamatini no puede enlazarlo y muere al arrancar con:

> `WinError 10013` — *an attempt was made to access a socket in a way forbidden by its access permissions*

Para confirmar que eso fue lo que pasó, lista los puertos que Windows tiene reservados:

```powershell
netsh interface ipv4 show excludedportrange protocol=tcp
```

Si `8000` cae dentro de alguno de esos rangos, elige un puerto fuera de ellos (9000 es una opción segura y común).

**Bueno saberlo**
- Un puerto pasado por línea de comandos sigue ganando: `python Tlamatini/manage.py runserver 9100`.
- Es **fail-safe** — si escribes mal el valor, Tlamatini regresa a 8000 y arranca de todos modos (imprime una línea `--- [PORT] …` explicando por qué).
- ¿Dónde está `config.json`? Junto a `Tlamatini.exe` en una build instalada; en `Tlamatini/agent/config.json` desde el código fuente.
- Si además corres el puente de Telegram **TeleTlamatini**, apunta su `tlamatini.base_url` al mismo puerto.

</details>

### 2 · Instala Ollama

Instala **[Ollama](https://ollama.com/download)** para Windows. Ollama es el motor que le sirve todos los modelos a Tlamatini — el modelo local de embeddings **y** los modelos de chat en la nube.

### 3 · Suscríbete a Ollama Pro (~$200 / año)

Entra a **[ollama.com](https://ollama.com)**, inicia sesión y toma el plan **Ollama Pro** (unos **$200 al año**). Pro desbloquea los **modelos `:cloud`** — modelos de clase frontera que corren en los servidores de Ollama — por un precio *anual* cercano a lo que cuesta una sola suscripción frontera en un *único mes*. Después conecta tu máquina:

```bash
ollama signin
```

### 4 · Descarga los modelos

Haz pull del pequeño modelo local de embeddings, más los modelos de chat en la nube que usará Tlamatini:

```bash
# Local embedding model (small, runs on your own GPU/CPU)
ollama pull nomic-embed-text

# Cloud models (served by Ollama Pro) — pull, or just sign in to use
ollama pull glm-5.2:cloud
ollama pull qwen3.5:cloud
```

Cualquier modelo en la nube funciona — estos dos son la pareja recomendada hoy (algunas capturas de más abajo pueden mostrar todavía nombres de modelos anteriores).

### 5 · Apunta Tlamatini hacia los modelos

En la navbar de Tlamatini, abre el menú **Config**:

<p align="center"><img src="Tlamatini/agent/images/MenuConfig.jpg" alt="Menú Config — Models, URLs, Access Keys Wizard" width="420"/></p>

**a) Config ▸ Models** — define el modelo de Ollama para cada subsistema (cada uno debe existir ya en tu catálogo de Ollama), y luego haz clic en **Save**:

<p align="center"><img src="Tlamatini/agent/images/ConfigureModels.jpg" alt="Diálogo Configure Models" width="480"/></p>

**b) Config ▸ Access Keys Wizard** — que necesites o no un **token de Ollama** depende de *dónde* corre Ollama:

> - 🖥️ **¿Ollama en tu propia máquina (localhost)?** Deja el token **vacío** — un Ollama local no necesita autenticación.
> - ☁️ **¿Ollama en un servidor remoto (por ejemplo [Vast.ai](https://vast.ai))?** Pega el **token de Ollama** para que Tlamatini pueda alcanzarlo.

Agrega aquí también cualquier key de CLI en la nube — más las keys de mensajería, la URL del servidor Kali, y la key **OPCIONAL** de ProjectDiscovery Cloud (PDCP) bajo **"Security Recon (ProjectDiscovery)"**. Los campos vacíos conservan lo que ya está configurado; haz clic en **Save**:

<p align="center"><img src="Tlamatini/agent/images/ACPXKeysConfigureWizard.jpg" alt="Access Keys Wizard" width="640"/></p>

Listo — marca **Multi-Turn** en la toolbar del chat y pon a Tlamatini a trabajar.

## 💎 Las joyas — lo que ningún otro puede hacer

Claude Code, Codex, Cursor, Gemini — editan archivos de texto. Tlamatini hace eso **y además** alcanza el mundo físico y creativo, y luego te deja *cablearlo todo visualmente*:

| | Capacidad | Por qué es rara |
|---|---|---|
| 🎮 | **Control de Unreal Engine** | Maneja el engine/editor desde el chat — ningún otro coding agent lo toca. |
| 🎬 | **Control de Blender** | Escena, objetos, render y ejecución de código sobre el socket oficial del Blender MCP. |
| 🔌 | **Manejo universal de MCPs externos** | Conéctate a **cualquier** servidor MCP externo (stdio · streamable-http · sse · websocket), hasta 5 a la vez, y usa sus tools al instante. Un solo client para todo el ecosistema MCP. |
| 🛠️ | **Modificar proyectos de software enteros** | Lee, busca, refactoriza, edita y reconstruye codebases completas — no sólo archivos sueltos — con el grounding del RAG híbrido. |
| 🛡️ | **Evaluaciones de seguridad** | Runbooks autorizados de Kali Linux / pentest + skills de auditoría de seguridad de código, dirigidos desde el chat. |
| 📟 | **Firmware STM32 · ESP32 · Arduino** | Andamiaje → build → **flashear una tarjeta real conectada** → leer el serial, con un preflight de seguridad que se niega a grabar firmware mal dirigido. |
| 🧩 | **UN DISEÑADOR VISUAL DE WORKFLOWS** | **87 tipos de agent** de arrastrar y soltar sobre un canvas que cableas hasta volverlo un flow ejecutable y guardable en `.flw`. *Ningún otro coding agent — ni Claude Code, ni Codex, ninguno — te da esto.* Ésta es la joya de la corona. |

> **El titular que ningún competidor puede copiar:** Tlamatini es el único asistente de desarrollo con IA local-first donde *diseñas el workflow de agents visualmente*, y luego lo pones a flashear firmware, manejar Unreal/Blender, correr herramientas de seguridad y comandar cualquier MCP externo — todo desde una sola máquina.

---

## 🔒 Y es sólo tuya

Los embeddings y el chat corren en tu instalación local de [Ollama](https://ollama.com). Los modelos en la nube (Claude API, Ollama Pro/Max) y la delegación a CLIs en la nube son **opcionales, petición por petición, nunca lo predeterminado.** Tu código y tu firmware no salen de la máquina a menos que tú misma los saques.

## ⚠️ CLEAR DISCLAIMER — USER CONTROL, JURISDICTION, AND RESPONSIBILITY FOR AGENTS

> **Nota / Note:** el texto en inglés que sigue es la versión **autoritativa** de este aviso. La traducción al español que aparece más abajo se ofrece **únicamente como cortesía** y no constituye el mismo instrumento legal. *The English text below is the **authoritative** version of this disclaimer; the Spanish rendering that follows it is a **courtesy translation only**.*

Every agent in `Tlamatini/agent/agents/` is intentionally provided as a **plain-Python program** so its operating code can be read, audited, edited, restricted, or disabled by the user. This transparency is a user-control mechanism, **not a warranty that an agent is secure or suitable for a particular environment**. The agents do not have independent authority or jurisdiction: the user alone decides whether, where, how, and with which permissions they run.

When you enable, configure, modify, chain, or execute an agent, **that agent and its execution are under your control and your jurisdiction**. You are solely responsible for reviewing its code and configuration; protecting and limiting its secrets, credentials, and permissions; selecting and authorizing every file, folder, network target, browser, shell, API, external MCP server, machine, hardware device, and downstream system it can access; supervising its output; and complying with every law, policy, license, contract, and authorization that applies to your use.

**BY RUNNING AN AGENT, YOU ACCEPT RESPONSIBILITY FOR ITS ACTIONS AND CONSEQUENCES. TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, ANY SECURITY BREACH, DATA EXPOSURE OR LOSS, UNAUTHORIZED ACTION, CREDENTIAL LEAK, UNSAFE AUTOMATION, POLICY OR LEGAL VIOLATION, SYSTEM COMPROMISE, DEVICE DAMAGE, FINANCIAL LOSS, OR OTHER HARM ARISING FROM YOUR USE, CONFIGURATION, MODIFICATION, OR EXECUTION OF AN AGENT OR AGENT WORKFLOW IS THE RESPONSIBILITY OF THE USER WHO RUNS IT.** Tlamatini's orchestration, documentation, examples, and guardrails do not authorize access to third-party systems and cannot replace the user's own security review, permission controls, monitoring, or legal compliance.

### 🇲🇽 Traducción de cortesía al español (no autoritativa)

Cada agent de `Tlamatini/agent/agents/` se entrega deliberadamente como un **programa de Python plano**, para que el usuario pueda leer, auditar, editar, restringir o deshabilitar su código de operación. Esta transparencia es un mecanismo de control del usuario, **no una garantía de que un agent sea seguro o adecuado para un entorno determinado**. Los agents no tienen autoridad ni jurisdicción independiente: el usuario, y sólo el usuario, decide si se ejecutan, dónde, cómo y con qué permisos.

Cuando habilitas, configuras, modificas, encadenas o ejecutas un agent, **ese agent y su ejecución quedan bajo tu control y tu jurisdicción**. Eres la única persona responsable de revisar su código y su configuración; de proteger y limitar sus secretos, credenciales y permisos; de seleccionar y autorizar cada archivo, carpeta, objetivo de red, browser, shell, API, servidor MCP externo, máquina, dispositivo de hardware y sistema posterior al que pueda acceder; de supervisar su salida; y de cumplir con toda ley, política, licencia, contrato y autorización que aplique a tu uso.

**AL EJECUTAR UN AGENT, ACEPTAS LA RESPONSABILIDAD POR SUS ACCIONES Y SUS CONSECUENCIAS. EN LA MÁXIMA MEDIDA PERMITIDA POR LA LEY APLICABLE, CUALQUIER BRECHA DE SEGURIDAD, EXPOSICIÓN O PÉRDIDA DE DATOS, ACCIÓN NO AUTORIZADA, FUGA DE CREDENCIALES, AUTOMATIZACIÓN INSEGURA, VIOLACIÓN LEGAL O DE POLÍTICAS, COMPROMISO DEL SISTEMA, DAÑO A DISPOSITIVOS, PÉRDIDA FINANCIERA U OTRO PERJUICIO QUE SURJA DE TU USO, CONFIGURACIÓN, MODIFICACIÓN O EJECUCIÓN DE UN AGENT O DE UN WORKFLOW DE AGENTS ES RESPONSABILIDAD DEL USUARIO QUE LO EJECUTA.** La orquestación, la documentación, los ejemplos y las salvaguardas de Tlamatini no autorizan el acceso a sistemas de terceros y no pueden sustituir la revisión de seguridad, los controles de permisos, el monitoreo ni el cumplimiento legal del propio usuario.

---

## 📋 La lista completa de capacidades

Todo lo que Tlamatini puede hacer, agrupado:

**🧩 Orquestación y diseño**
- **Diseñador Visual de Workflows (ACP)** — 87 tipos de agent de arrastrar y soltar, cableados en flows ejecutables; guarda y carga archivos `.flw`; el Flow Compiler valida el canvas y lo convierte en `config.yaml`.
- **Orquestación Multi-Turn** — un loop de tool-calling con **75 tools** y un planificador global de ejecución; el modo **Step-by-Step** marca el ritmo de una instalación práctica, una acción a la vez; los **model steps auto-reparables** hacen que un tropiezo de red o del modelo nunca la congele — reintenta bajo un watchdog, termina con gracia a partir del trabajo ya hecho, y siempre te cuenta qué pasó.
- **FlowCreator / FlowHypervisor** — deja que un LLM diseñe un flow; un watchdog vigila su salud. FlowCreator ahora también se **invoca desde el chat** (`chat_agent_flowcreator`): describe un flow con palabras normales y escribe en disco un archivo `.flw` real, cargable en el canvas.
- **Parametrizer / Gatewayer / Gateway-Relayer / Node Manager** — encadena la salida de un agent hacia la configuración del siguiente; dispara flows desde webhooks, carpetas vigiladas o GitHub/GitLab.
- **ACPX** — lanza CLIs externos de coding agents (Claude Code, Codex, Cursor, Gemini, Qwen y más) como tools, y hace de relevo entre ellos.

**📟 Firmware y hardware**
- **STM32er** — build/flash/observación STM32 sin configuración a lo largo de toda la línea de 32 bits de ST (Blue Pill → F7/G/L/H7/U5/WB) mediante un backend dual (PlatformIO `ststm32` + el template MCP del STM32F407VG), con un preflight de seguridad de misión crítica.
- **ESP32er** — build/flash/monitor directo con PlatformIO, bootstrap sin configuración.
- **Arduiner** — `arduino-cli` directo, instala solo el binario y el core, build/upload.
- **ESPHomer** — configuraciones ESPHome para dispositivos de casa inteligente (YAML, sin C++), sin configuración.

**🎬 Engines 3D y creativos**
- **Unrealer** — control de Unreal Engine desde el chat.
- **Blenderer** — escena/objetos/render/código de Blender sobre el socket MCP oficial.

**🛠️ Código y proyectos**
- **PDFer** — el **compositor de documentos**: convierte la propia respuesta de Tlamatini, algo de Markdown/HTML, texto plano, una carpeta de imágenes o varios PDFs existentes en UN solo PDF con estilo — con portada, tablas reales, números de página y un índice opcional. Es el lado de ESCRITURA de la familia documental (File-Extractor / File-Interpreter *leen* documentos; PDFer los *escribe*). **No necesita instalación** — todos los motores que usa ya vienen dentro de Tlamatini. Modos: `auto` (olfatea el contenido por ti) / `markdown` / `html` / `text` / `images` (uno por página, ajustado, o en cuadrícula) / `mixed` (prosa + figuras incrustadas) / `merge` / `info` / `validate`. Opcionalmente deja que un modelo de Ollama pula antes el texto a Markdown limpio (apagado por defecto; un pulido fallido nunca pierde tu documento). Los PDFs aterrizan en **Documents/TlamatiniPDF** con un nombre a prueba de colisiones, y un preflight a prueba de fallos prefiere negarse antes que escribir un archivo vacío o equivocado.
- **LaTeXer** — el **tipógrafo de LaTeX**, y el hermano tipográfico de PDFer: PDFer *compone* un PDF a partir de Markdown, HTML e imágenes; LaTeXer *tipografía* uno desde código `.tex` de verdad — matemáticas como Dios manda, una bibliografía real, referencias cruzadas numeradas, un índice analítico. Pásale una carpeta entera de archivos `.tex` y él solo encuentra el documento maestro, sigue cada `\input`, corre `biber`/`bibtex` y `makeindex`, y vuelve a correr el compilador las veces que haga falta hasta que las referencias cruzadas se estabilizan — y luego convierte el famoso log ilegible de LaTeX en una lista corta de errores reales. También puedes darle un fragmento pelón (aunque sea nada más `$E = mc^2$`) y él lo envuelve en un preámbulo completo por ti. Ocho templates incluidos (article, report, book, beamer, letter, cv, homework, spanish-article), más acciones de autoría para crear, editar, leer, listar, revisar y analizar archivos `.tex`. Los PDFs aterrizan en **Documents/TlamatiniLaTeX**.

  > ### ⚠️ LaTeXer necesita **MiKTeX** — y eso es lo *único* que necesita
  >
  > Tlamatini **no** trae una distribución de TeX: una completa pesa varios gigabytes, y el release se mantiene chico a propósito. Así que instala **MiKTeX** una sola vez — **https://miktex.org/download** — y luego instala Tlamatini. Ya con eso: **MiKTeX + Tlamatini = LaTeXer funciona, para siempre, sin nada más que configurar.**
  >
  > **¿Por qué MiKTeX en específico?** Porque cuando un documento pide un package de LaTeX que nunca instalaste, **MiKTeX lo descarga e instala él solo, a media compilación** — así que el documento igual sale. Esa única característica es la que le permite a LaTeXer tipografiar *lo que sea* sin configuración previa. TeX Live y MacTeX se detectan y se usan si ya tienes alguno, pero ninguno de los dos puede hacer eso, así que tendrías que ir cazando los packages faltantes tú mismo. **MiKTeX es la opción recomendada.**
  >
  > ¿No tienes LaTeX instalado? LaTeXer te lo dice claramente y se niega — nunca truena ni finge que hizo un PDF. Pídele que corra `action: validate` para ver exactamente qué encontró, o `action: install` y él descarga y lanza el instalador oficial de **MiKTeX** por ti.
- **Editor / Grepper / Globber** — búsqueda y reemplazo quirúrgico, búsqueda de contenido por regex, glob de nombres de archivo (equivalentes de Claude-Edit/Grep/Glob).
- **File-Creator / Mover / Deleter / File-Interpreter / File-Extractor** — crear, mover, borrar, leer-e-interpretar, extraer de PDF/DOCX.
- **Executer / Pythonxer** — ejecutan comandos de shell y Python con compuerta de validación.
- **Gitter** — control total de git. **Googler** — búsqueda web + extracción.
- **RAG híbrido** — recuperación con FAISS + BM25, extracción de metadatos, presupuesto de contexto, todo anclado a tu codebase.
- **Skills** — paquetes `SKILL.md`: code-review, security-audit, kali-pentest, flow-making, skill-creator, summarize, ayudantes de auditoría/lint/refactor, y stubs de integración (GitHub, Gmail, Slack, Jira, Notion, Todoist, Trello, Weather).

**🛡️ Seguridad**
- **Kalier** — evaluaciones de seguridad ofensiva autorizadas con Kali Linux / MCP-Kali-Server.
- **Discoverer** — la suite de reconocimiento de ProjectDiscovery (subfinder/httpx/naabu/katana/nuclei/cvemap — la búsqueda de CVEs corre el `vulnx` de ProjectDiscovery, ya que la API propia de cvemap fue retirada en agosto de 2025) mediante una toolchain privada de Go que se instala sola en `<install_dir>/Go`; reconocimiento autorizado, mapeo de superficie de ataque y descubrimiento de vulnerabilidades. La **llave de ProjectDiscovery Cloud (PDCP) es OPCIONAL** (levanta los límites de tasa de cvemap/vulnx, habilita `-ai`/subida a la nube de nuclei) — configúrala una sola vez en **Config ▸ Access Keys Wizard ▸ "Security Recon (ProjectDiscovery)"** (se inyecta sola en cada corrida; se redacta de los exports `.flw` y por `regen_secrets.py` antes de un push).
- **Nmapper** — puente LOCAL, de **sólo uso**, hacia nmap para pentesters / CTF: ejecuta un `nmap` real que la usuaria instaló ella misma (Nmapper **NUNCA empaqueta ni redistribuye nmap** — la NPSL de nmap prohíbe incrustarlo en un producto sin una licencia OEM de paga), resolviéndolo desde PATH → `C:\Program Files\Nmap` → una copia en `%LOCALAPPDATA%\Tlamatini\nmap`; si no está, se niega con gracia y `action='install'` baja el instalador OFICIAL y gratuito de nmap (admin/UAC; también trae Npcap). El valor por defecto es un escaneo TCP connect SIN privilegios (`-sT`, sin Npcap, sin admin), así que una instalación recién hecha escanea de inmediato; SYN / `-O` / UDP se degradan solos a un connect scan en Windows sin Npcap. Acciones: `quick` / `full` / `top_ports` / `version` / `scripts` (NSE) / `host_discovery` / `udp` / `custom` / `validate` / `install`; emite `INI_SECTION_NMAPPER`. Distinto de **Kalier** (una caja Kali remota) y de **Discoverer** (ProjectDiscovery). **Sólo objetivos autorizados.**
- **NetSpeed-Calculator** — mide **tu** conexión a Internet y te da la respuesta *con su barra de error*: bajada, subida, latencia, jitter, pérdida de paquetes y **bufferbloat**. No le cree a un solo sitio de speed-test: mide contra **varios proveedores públicos sin llave a la vez** (Cloudflare, Ookla, Fast.com, LibreSpeed, Hetzner, CacheFly; sin cuenta y sin API key) y luego los fusiona con un meta-análisis de efectos aleatorios de verdad, así que obtienes un intervalo de confianza del 95% y te dice claramente si los proveedores de veras *coincidieron*. Sigue el RFC 6349: varios streams TCP en paralelo, la rampa de slow-start descartada, el throughput muestreado como derivada en vez del ingenuo total÷tiempo, y los outliers rechazados. **El bufferbloat es el que casi nadie está midiendo** — se califica de A+ a F y suele ser la razón real de que una conexión "rápida" tenga videollamadas entrecortadas. Los endpoints muertos o movidos se saltan **con una razón por nombre**, nunca como un `0.00 Mbps` silencioso. ⚠️ Consume ancho de banda REAL, que puede ser **medido** (~100-200 MB por corrida completa), así que pregunta antes de correr.
- **Zavuerer** — mensajería unificada **Zavu**: SMS / WhatsApp / Telegram / Email / Voz desde UNA sola llave de API (`channel: auto` enruta con inteligencia al mejor canal, con respaldo automático). Configura la llave una vez en **Config ▸ Access Keys Wizard ▸ "Unified Messaging (Zavu)"**; HTTP directo, preflight a prueba de fallos, se niega con seguridad cuando no hay llave. **Precios de Zavu:** el registro es gratis (sin tarjeta), pero el envío es de pago por uso — Zavu cobra por mensaje.
- Skills de **security-audit / kali-pentest**.

**🔌 Integración externa**
- **Client universal de MCPs externos** — conéctate a cualquier servidor MCP sobre 4 transportes, hasta 5 activos, con 8 tools supervisores y un agent **MCP Doctor** que hace el triage de un servidor antes de que lo cablees.
- **Descubrimiento de apps compañeras (Tlamatini-FlowPills)** — las apps hermanas de XAIHT localizan el catálogo de plantillas de agent de Tlamatini al instante, **sin Python y sin escanear el disco**: al instalar y en cada arranque, Tlamatini publica una llave de registro por usuario `HKCU\Software\XAIHT\Tlamatini` + un `_tlamatini_agents_manifest.json` (con el `sha256` de cada agent) junto a los agents, y deja una marca de agents preservados si desinstalas pero los conservas. Sólo HKCU, sin admin, a prueba de fallos.

**🖥️ Automatización de escritorio y browser**
- **Playwrighter** — automatización de browser por script.
- **Windower** — gestor de ventanas Win32 (enfocar/mover/redimensionar/mosaico/cerrar).
- **Shoter / Mouser / Keyboarder** — capturas de pantalla, mouse, teclado.

**🎙️ Audio, video, visión y habla**
- **Talker (TTS)** — texto a voz mediante Ollama. **Whisperer (STT)** — voz a texto (faster-whisper local + respaldo en la nube).
- **Recorder / Camcorder** — captura de micrófono y de webcam.
- **AudioPlayer / VideoPlayer** — reproducción de audio y video con control de volumen y de repetición.
- **Image-Interpreter** — análisis de visión con triple modelo: qwen3.5:cloud + gemma4:cloud interpretan cada imagen **en paralelo** sobre dos conexiones Ollama dedicadas, y luego glm-5.2:cloud fusiona ambas interpretaciones en un solo informe definitivo (inventarios de mockup/GUI en coordenadas %, OCR completo, personas descritas exhaustivamente con pistas de identidad tomadas del nombre del archivo de imagen).

- **Captura de pantalla → chat (pegar o soltar)** — presiona Impr Pant (o recorta), regresa a Tlamatini con Alt+Tab y oprime **Ctrl+V** — o arrastra archivos de imagen a la columna del chat. Ella guarda la imagen en su propia carpeta `Temp` como `image_<timestamp>.jpg`, muestra una miniatura arriba del campo de texto, y suelta la **ruta completa dentro de tu mensaje, justo en el cursor**, para que termines la frase — *"…¿qué está mal en esta captura?"* — y la envíes. Esa ruta es lo que lee Image-Interpreter.

**📨 Mensajería, puentes y plataforma**
- **Telegrammer** — envío/recepción de Telegram que puede mandar bajo **dos identidades**, elegidas mensaje por mensaje con `provider`: **como el bot** (`provider=bot`, Bot API + un token de `@BotFather`) o **como tu propia cuenta** (`provider=user`, sesión oficial de usuario de Telegram). El español normal funciona — di *"mándalo como yo"* (→ tu cuenta) o *"como el bot"*. `auto` (el valor por defecto) usa tu cuenta para `@usernames`/`+phone` privados y el bot para ids numéricos y canales. Mandar como tú requiere un login de una sola vez; las configuraciones para humanos se quedan legibles como `@username`.
- **Whatsapper** — envío/recepción de WhatsApp con un interruptor `provider` para **qué número manda**: **`cloud`** (por defecto, la WhatsApp Cloud API oficial de Meta — número de negocio, plantillas, System User) o **`web`** (di *"mándalo como yo"* / *"desde mi propio WhatsApp"*), que manda desde **tu número personal** automatizando WhatsApp Web tras un login por QR de una sola vez — sin plantillas, sin System User. La ruta `web` es no oficial (maneja WhatsApp Web) y conlleva riesgo de baneo por parte de Meta; la ruta `cloud` sigue siendo la vía oficial y soportada.
- **Instant Messaging Doctor** — diagnostica automáticamente las fallas de Telegrammer/Whatsapper y se puede llamar directamente antes de un envío crítico; valida tokens oficiales, contactos, el enrutamiento legible por `@username`, las plantillas y webhooks de Meta, y emite acciones de reparación listas para el Parametrizer.
- **TeleTlamatini** — puente de Telegram hacia el chat completo.
- **Multi-modelo** — Ollama (local), Anthropic Claude (nube), Qwen (visión).
- **Autoconocimiento y automodificación** — puede leer, modificar y reconstruir su propio código fuente.
- **Empaquetado con PyInstaller** — se distribuye como un `.exe` autónomo de Windows.

---

## 🧹 Tu contexto se mantiene limpio — detección automática de binarios

Cuando le apuntas a Tlamatini una carpeta (**Context ▸ Set directory as context**), los proyectos reales están llenos de archivos que no son texto: binarios compilados, imágenes, archivos comprimidos, pesos de modelos, bases de datos, artefactos de build. Meter eso a un índice de embeddings es puro daño — desperdicia VRAM y tiempo, y entierra tu código real bajo el ruido.

Tlamatini revisa **cada** archivo por sus bytes reales antes de cargarlo, y se salta en silencio los binarios. Viene encendido por defecto y no necesita configuración.

- **Rápida por diseño** — como máximo una lectura de 8 KiB por archivo, y las extensiones binarias conocidas ni siquiera se abren. Revisar un video de 4 GB cuesta lo mismo que revisar un README.
- **Basada en el contenido, no en el nombre** — un PNG renombrado a `notes.md` igual queda atrapado. Esto funciona *junto con* **Context ▸ Set file type omissions**, que sigue exactamente igual para los archivos que *tú* eliges ignorar.
- **Nunca silenciosa** — cada archivo omitido queda listado en `tlamatini.log` con la razón por la que se omitió, así siempre sabes por qué algo no está en tu contexto:

```
--- [BINARY-GUARD] 3 binary file(s) OMITTED from the context / embedding chain
--- [BINARY-GUARD]   ✗ OMITTED C:\proj\assets\logo.png  [extension: known binary extension .png]
```

- **Segura por defecto** — si algo es incierto o ilegible, el archivo se carga como texto en vez de descartarse. Tu contexto nunca se elimina por una suposición. Los archivos de texto con acentos o codificaciones heredadas (español, francés, cp1252 …) siempre se conservan.

Apágala con `"binary_context_detection": false` en `config.json`; ajústala con `binary_detection_control_ratio`, o rescata una extensión concreta con `binary_detection_force_text_extensions`.

## Mírala en acción

- ▶️ **[Teaser de un minuto](https://www.youtube.com/watch?v=4MyRXBahHuU&t=41s)** · 🎬 más demos en **[xaiht.org](https://xaiht.org)**.

---

## Instalación

Consulta **[la documentación completa](BookOfTlamatini.md)** para la instalación completa — modelos en la nube (Ollama Pro/Max, Claude API), el diseñador visual de workflows, y cómo construir una distribución congelada de Windows con PyInstaller. En corto: instala Ollama → clona, venv, `pip install -r requirements.txt`, `migrate` → `runserver` (`--noreload` es opcional desde el 2026-07-11) → abre `http://127.0.0.1:8000/`.

---

## Stack tecnológico

Python 3.12 · Django 5.2.4 · Django Channels (Daphne ASGI) · LangChain / LangGraph · FAISS + rank-bm25 · Ollama / Anthropic Claude / Qwen vision · SQLite · PyInstaller. **Plataforma: Windows 10/11.**

---

## Contribuir

¿La probaste en tu tarjeta, en tu engine o en el canvas? **[Abre un issue](https://github.com/XAIHT/Tlamatini/issues)** y cuéntame qué funcionó y qué no — esa retroalimentación es lo más útil ahorita. Los PRs son bienvenidos.

---

## Licencia

[MIT](https://github.com/XAIHT/Tlamatini/blob/main/LICENSE) · Hecho por [@XAIHT](https://github.com/XAIHT) · [xaiht.org](https://xaiht.org)
