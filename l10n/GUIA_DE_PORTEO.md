<!--
═══════════════════════════════════════════════════════════════════
  ✦  T L A M A T I N I  ✦   —   "la que sabe"
  Creado por  Angela López Mendoza   ·   @angelahack1
  Desarrolladora · Arquitecta · Creadora de Tlamatini
  Tlamatini Author Banner — no se quita (el nombre de Angela va en cada build)
═══════════════════════════════════════════════════════════════════
-->
# Guía de porteo: Tlamatini al español de México

Esta guía explica cómo se construye y cómo se mantiene **Tlamatini-Spanish** a partir de
**Tlamatini** (inglés). Reúne el estilo, la terminología, el alcance, el método y el control
de calidad. Se basa en la investigación del 22 de octubre de 2026 sobre cómo llegan al
español las aplicaciones técnicas más conocidas del mundo. Las fuentes están al final.

---

## 1. Principio rector: un solo código, una memoria de traducción

**El código vive en un solo lugar: el árbol inglés.** Tlamatini-Spanish no es una copia que
se edita a mano. Es el resultado reproducible de tres piezas:

1. **Un commit del árbol inglés**, anotado en `l10n/BASE_INGLES.json`.
2. **La memoria de traducción** (`l10n/memoria/`): pares *texto inglés exacto → texto en
   español*, archivo por archivo, con el número de veces que debe aparecer cada uno.
3. **Las herramientas de `l10n/`**, que copian, aplican, verifican y reportan lo pendiente.

Así trabajan los proyectos que no se quedan atrás. Mozilla localiza Firefox desde un único
repositorio para todos sus canales, "para que una corrección se haga una vez y llegue a
todas las versiones". Kubernetes traduce contra una versión concreta del inglés y tiene
scripts que listan los archivos desactualizados. Los autores de po4a lo dicen sin rodeos:
seguir los cambios a mano "se vuelve una pesadilla", y una traducción desactualizada suele
ser peor que ninguna.

Consecuencias prácticas:

- **Nadie edita a mano el árbol en español.** `portar.py verificar` marca como error
  cualquier archivo que no sea exactamente *original inglés + memoria*.
- **Una versión nueva del inglés se porta en minutos**: se copia el commit nuevo, se aplica
  la memoria y sólo los textos que cambiaron quedan pendientes (sección 7).
- **Si un texto inglés cambia, su traducción no se aplica a ciegas**: el par deja de
  coincidir y el texto aparece en `pendientes`. Es el mismo criterio de gettext ("fuzzy") y
  de Firefox (un texto que cambia de sentido recibe un identificador nuevo).

---

## 2. Lo que enseña la investigación

### 2.1 Ingeniería de localización

- **El código nunca compara contra textos de pantalla.** El W3C define la
  internacionalización como "evitar que el código dependa de los textos de la interfaz".
  Cuando Tlamatini sí lo hace (un mensaje que otro archivo reconoce por sus palabras), el
  texto se traduce **en los dos lados a la vez** y `verificar` exige que coincidan
  (sección 6, "acoplamientos").
- **Oraciones completas, con marcadores.** gettext, Mozilla y Microsoft coinciden: no armar
  frases concatenando pedazos (asumen el orden del inglés), usar marcadores (`{name}`,
  `%(x)s`, `${…}`) y no reutilizar una misma cadena en dos contextos.
- **Plurales.** El español tiene dos formas (`n != 1`); CLDR agrega una tercera, "many",
  para los millones ("1.000.000 de días").
- **Django.** `es-mx` viene integrado. Con `LANGUAGE_CODE = 'es-mx'` y sin
  `LocaleMiddleware`, ese idioma rige para todos los usuarios, consumers de WebSocket
  incluidos. Se usa `es-mx` y no `es`: el formato de `es` (España) pone coma decimal y
  cambiaría en silencio cada número que la máquina vuelve a leer.
- **HTML.** Sólo se traducen los nodos de texto y los atributos que la especificación
  WHATWG declara traducibles: `alt`, `title`, `placeholder`, `label`, `value` de los
  botones y `lang`. Nunca `class`, `id`, `data-*`, `href` ni `name`. `aria-label` no lo
  traducen los navegadores: lo traducimos nosotros, igual que el texto visible al que
  acompaña (WCAG 2.5.3, la etiqueta visible debe estar contenida en el nombre accesible).
- **YAML.** Un valor sin comillas no puede contener `: ` ni ` #`. Además, PyYAML lee
  `No`, `Yes`, `On` y `Off` sin comillas como booleanos: un "No" traducido se vuelve
  `False`. Por eso el YAML se verifica parseando los dos lados.
- **Revisión automática al estilo pofilter** (Translate Toolkit): marcadores, etiquetas
  HTML, URLs, términos que no se traducen, traducciones vacías, delimitadores.
- **Expansión del texto.** El español ocupa más: hasta 300 % en etiquetas de 10
  caracteres o menos, 200 % entre 11 y 20, y alrededor de 130 % en textos de más de 70
  (tablas de IBM, citada por el W3C, y de Adobe Spectrum). Los botones son lo primero que
  se desborda: en la prueba visible se revisan.
- **LLM.** Los estudios muestran que, para el español, un system prompt en inglés funciona
  casi igual que uno traducido, pero los modelos a veces contestan en otro idioma; la
  recomendación es decir explícitamente el idioma de la respuesta.

### 2.2 Cómo lo hacen las herramientas técnicas

| Proyecto | Tratamiento | Términos técnicos |
|---|---|---|
| Git (catálogo `es.po` oficial) | tú | "realiza un commit", "hacer push/pull/merge"; HEAD, upstream en inglés; *branch* = rama |
| FastAPI (docs en español) | tú | conserva framework, path, request, response, header, plugin, worker |
| Kubernetes (docs en español) | — | los objetos de la API en inglés y con mayúscula: el Pod, el Deployment (masculino) |
| python-docs-es | — | acepta el *spanglish* cuando se lee mejor que el calco ("git unir"); script, token sin traducir |
| Firefox es-MX | tú | "Haz clic", "subir", "Ajustes"; es-ES usa usted |
| VS Code | usted | traduce etiquetas; deja los verbos de Git entre comillas: hacer "push" |
| GitHub Docs | mezcla | traduce commit → "confirmación", push → "insertar"; las palabras inglesas se le cuelan igual |
| GNOME, Debian | usted | traducen casi todo ("intérprete de órdenes") |

**Errores documentados de quienes tradujeron los términos técnicos:** Microsoft Learn
convirtió "Pods" en "Cápsulas" y "always pull before you push" en "tirar antes de
presionar"; GitHub Docs tradujo *prompt* como "símbolo del sistema" o "avisos"; GitLab
etiquetó dos pestañas distintas (commits y diffs) como "Cambios"; VS Code tradujo
*checkout* de tres maneras. También se documentan catálogos regionales que se quedan atrás:
el catálogo `es_MX` del admin de Django tiene 48 entradas vacías y su última revisión es de
2022.

### 2.3 El español de México en las interfaces

- **Microsoft, guía es-MX (2024):** tú; *computadora*, *mouse*, *video*, *la PC*, *la API*;
  *predeterminado* (no "por defecto"); *aplicación*; mejor *selecciona* que "da clic";
  lenguaje neutro sin `@`, `x` ni `e`.
- **Apple es-MX y Google es-419:** *Configuración*, *computadora*, *vínculo*, *selecciona*,
  *descargar*, *audífonos y bocinas*.
- **CLDR es-MX:** `1,234.56`, `10%` (sin espacio), día/mes/año, reloj de 12 horas con
  *a.m.* y *p.m.*: los mismos separadores numéricos que el inglés de EE. UU.
- **Academias:** FundéuRAE acepta *token* en redonda; la RAE registra *hacer clic*; la
  Academia Mexicana de la Lengua es pragmática ("son los hablantes, no los académicos, los
  que norman la lengua").
- **Cómo escriben los desarrolladores mexicanos:** Platzi titula "Haciendo deployment a un
  servidor" y "Tu primer push"; EDteam escribe "hacer deploy"; los cursos hablan de
  *prompts* y de *ventana de contexto*. Un estudio con ingenieros de software (Íkala, 2013)
  encontró que los expertos prefieren el término inglés porque evita ambigüedades.
- **Tú en productos mexicanos:** Apple, Google, Mercado Pago, BBVA México, Platzi y UNAM.

---

## 3. Decisiones de estilo de Tlamatini-Spanish

### 3.1 Variante, registro y tratamiento

- **Variante:** español de México. Código de idioma: `es-mx` en Django, `es-MX` en HTML
  y JavaScript.
- **Registro técnico mexicano.** La regla de Angela: *el español pone la gramática y los
  verbos; el inglés pone el vocabulario técnico*. En sus palabras: "En México nunca decimos
  contenedor, decimos container; nunca decimos vaina, decimos pod". Los sustantivos
  cotidianos sí van en español (archivo, carpeta, ventana, contraseña). **Ante la duda, el
  término técnico se queda en inglés.**
- **Tuteo en todo el producto** (tú), sin mezclarlo nunca con usted. Es lo que piden hoy
  las guías de Microsoft para México, España y EE. UU., y lo que usan Apple y Google.
- **Los términos ingleses van en redonda**, sin cursivas ni comillas, con artículo español
  y plural en -s: *el commit*, *los logs*, *los prompts*, *los agents*. Género: el que ya
  usan los desarrolladores, masculino casi siempre (*el log*, *el path*, *el canvas*, *el
  flow*, *el token*, *el screenshot*); femenino en los ya asentados: *la API*, *la
  terminal*, *la PC*, *la GPU*, *la CPU*, *la web*, *la caché*.
- **Los nombres propios de funciones y del producto van sin artículo** (regla de
  Microsoft para nombres no traducidos): "Activa Compact mode", "Abre Agentic Control
  Panel". Los sustantivos técnicos comunes sí lo llevan: "el canvas", "el flow".

### 3.2 Lo que nunca se traduce

1. **Los nombres de los agents**, byte por byte: `Executer`, `File-Creator`, `STM32er`,
   `Kyber-KeyGen`, `Image-Interpreter`… El guion y las mayúsculas son funcionales: el
   nombre es la llave de la base de datos, de la clase CSS del canvas y del tool
   `chat_agent_<nombre>`. Sólo cambia la oración que lo rodea.
2. **El vocabulario del producto:** Tlamatini, XAIHT, ACPX, MCP/MCPs, Agents, Tools,
   Skills, Multi-Turn, Exec report, Ask Execs, Compact mode, Self-modify, canvas, flow,
   Flows, prompt, log, skill, Wizard, Access Keys Wizard, Agentic Control Panel, Prompt
   Flow Panel, Admin Panel, ACPX-Skills, System-Metrics, Files-Search, Current-Time,
   Terminater, Interactor.
3. **El vocabulario técnico** (lista base de Angela, ampliable): pod, container, cluster,
   deployment, commit, push, pull, merge, branch, repo, build, release, log, pattern, path,
   status, output, input, chain, prompt, token, embedding, fine-tuning, LLM, RAG, endpoint,
   screenshot, firmware, browser, timeout, backup, query, script, framework, plugin,
   dashboard, payload, header, webhook, socket, thread, cache, buffer, driver, kernel.
4. **El canal máquina:** centinelas de protocolo (`END-RESPONSE`, `BEGIN-CODE`,
   `Referenced Rephrase:`…), llaves JSON/YAML, valores de enums y de status (`running`,
   `completed`, `SUCCESS`, `FAILURE`), identificadores, URLs, nombres de archivo, comandos.
5. **Lo interno:** logs, mensajes de consola, comentarios y docstrings del código. El
   usuario no lee el log.
6. **Las etiquetas del Exec Report** (Command, Status, SUCCESS, FAILURE).
7. **El nombre de Angela:** "Angela López Mendoza" y "ANGELA LÓPEZ MENDOZA" en la ventana
   About.

### 3.3 Gramática de la interfaz

| Elemento | Forma | Ejemplos |
|---|---|---|
| Botones, comandos, opciones de menú | infinitivo | Guardar · Abrir · Cancelar · Iniciar sesión · Configurar MCPs |
| Títulos de ventanas, diálogos y secciones | sustantivo o infinitivo, sólo inicial mayúscula | Abrir archivo · Configuración del modelo |
| Tooltips | tercera persona del presente | Muestra u oculta el canvas. |
| Placeholders | imperativo de tú | Escribe tu contraseña |
| Casillas | infinitivo o frase nominal | Procesar imágenes |
| Estados | participio o adjetivo | Pendiente · En ejecución · Listo · Detenido |
| Confirmaciones | pregunta completa | ¿Quieres borrar este flow? · ¿Quieres continuar? |
| Errores | qué pasó, punto, y qué hacer; sin culpar | No se pudo abrir el archivo: {detalle} |
| Indicaciones al usuario | imperativo de tú | Selecciona un archivo. · Haz clic en Guardar. |

**Mensajes de error y aviso** (patrones de la guía de Microsoft para México):

- *Cannot / Unable to* → **No se puede** + infinitivo: "No se puede conectar con Ollama."
- *Could not* (pasado) → **No se pudo** + infinitivo: "No se pudo guardar el flow."
- *Failed to…* → **Error al** + infinitivo, o **Error de/en** + sustantivo: "Error al
  iniciar el agent", "Error de conexión".
- Nada de "fallo", "falló", "ha ocurrido", "ocurrió un error". Sin "por favor" de relleno
  en los mensajes del sistema (en la voz de Tlamatini, que habla en primera persona, la
  cortesía sí es parte de su manera de hablar).
- Estructura: el problema, punto, la solución: "La contraseña es incorrecta. Prueba otra
  vez."
- Antes de concordar las palabras de alrededor, averigua qué valor reemplaza al marcador
  (`{name}`, `${count}`): su género y número mandan.
- Calcos que se evitan: "realiza los siguientes pasos" → "haz lo siguiente"; "solicitar"
  → "pedir"; "proporcionar" → "dar"; "remover" → "quitar"; "checar" → "revisar";
  "abortar" → "cancelar".

### 3.4 Ortografía y tipografía

- **Mayúscula sólo al inicio** (el *Title Case* es del inglés): "Abrir archivo", no "Abrir
  Archivo". Los nombres del producto conservan sus mayúsculas: "Configurar Agents". Las
  mayúsculas llevan tilde.
- Días, meses e idiomas en minúscula.
- **Signos de apertura** ¿ ¡ siempre.
- Comillas: las que traiga el original; si hay que agregarlas, comillas curvas “ ” (las
  que usa Microsoft en México), que además no hay que escapar dentro del código.
- Puntos suspensivos pegados a la palabra ("Cargando..."), igual que el original; los
  emojis (`✓`, `⚠`, `⏳`) se quedan donde estaban.
- *clic* (nunca "click" en texto en español), *video* sin tilde, *e-mail* → *correo*.
- **Scripts de PowerShell (`.ps1`) sin BOM: español SIN acentos, ñ ni ¿ ¡.** Tlamatini los
  corre con Windows PowerShell 5.1, que lee como ANSI un archivo sin BOM: un acento se vería
  como basura ("Ã³") y los bytes de *Ó* y *Ñ* (0x93 y 0x91 en cp1252) son comillas para
  PowerShell y rompen el script. Se redacta buscando palabras sin acento ("Todo sigue igual",
  "Carpeta destino"); `verificar` lo hace cumplir.
- **Atajos de teclado: las mismas letras del inglés** (Ctrl+S, Ctrl+Z…). En una página
  web, cambiarlas chocaría con los atajos del navegador; Apple y Google tampoco las
  cambian. Las teclas, con el nombre impreso en el teclado: Ctrl, Shift, Alt, Esc, Enter,
  Tab.

### 3.5 Formatos

- es-MX usa los mismos separadores numéricos que en-US (`1,234.56`, `10%`). Los números
  que calcula el código no se tocan.
- Donde el código fija `'en-US'` para formatear fechas u horas, pasa a `'es-MX'`
  (día/mes/año, 12 horas con a.m./p.m.). Las llamadas sin locale usan el idioma del sistema
  del usuario, y así se quedan.
- `<html lang="es-MX">` en todas las plantillas: los lectores de pantalla cargan la
  pronunciación correcta (WCAG 3.1.1).

### 3.6 Lenguaje incluyente

Redacción neutra, sin `@`, `x` ni `e`: "Te damos la bienvenida" en vez de "Bienvenido";
"¡Hola, {name}!"; "tu cuenta" en vez de "el usuario". La RAE y la Academia Mexicana
rechazan esas marcas; Microsoft es-MX pide reformular. Platzi saluda: "Te damos la
bienvenida".

### 3.7 La voz de Tlamatini

Tlamatini habla en **primera persona**, cálida, y llama al usuario **por su nombre**
(`{name}`). Es **ella**: sus adjetivos concuerdan en femenino ("Estoy lista", "Ya estoy de
vuelta"). Tono mexicano y cercano, sin caer en la jerga: "Ahorita lo reviso" sí; groserías
o regionalismos marcados, no.

### 3.8 Glosario

La terminología completa (qué se queda en inglés, qué se dice en español y qué traducciones
están prohibidas) vive en [`GLOSARIO.md`](GLOSARIO.md). La lista que la máquina hace
cumplir está en [`verificacion.json`](verificacion.json).

---

## 4. Alcance

**Se traduce (es la interfaz):**

- Las plantillas Django (`templates/`): textos, `title`, `placeholder`, `aria-label`,
  `alt`, `value` de botones, `lang`.
- El JavaScript del frontend: todo texto que llega a la pantalla (`textContent`,
  `innerHTML`, `title`, alerts, `tlmAlert`/`acpAlert`, toasts, títulos y botones de los
  diálogos de jQuery UI).
- Los mensajes del backend que llegan a la pantalla: las líneas fijas del chat
  (`constants.py`), los mensajes de los consumers y los `message`/`error` que las vistas
  devuelven y la página muestra.
- Las descripciones de los agents (`agents_descriptions.md`: tooltips y diálogo
  Description), el Catálogo de Prompts y los textos de Tools y Skills que se leen en los
  diálogos.
- Las ventanas de escritorio: instalador, desinstalador, setup wizard y recuperación.
- La configuración regional (`LANGUAGE_CODE = 'es-mx'`, `lang="es-MX"`, formatos de fecha
  fijados en `'en-US'`).
- `README.md`, la portada pública del repositorio.
- Las respuestas fijas de TeleTlamatini en Telegram (contraseña, acceso, "Trabajando en tu
  solicitud…").

**Adaptaciones funcionales declaradas** (marca `"codigo"`, sección 5): el validador de forma
del prompt acepta español, y `prompt.pmt` pide al modelo responder en español de México
conservando el vocabulario técnico en inglés (la investigación recomienda decir el idioma de
salida de forma explícita). El atajo de saludo (`REGEX_GREETING`) NO se extiende a "hola":
se tragaría solicitudes como "hola, haz…".

**No se traduce:** lo de la sección 3.2, las pruebas (salvo donde comprueban un texto de
pantalla que se tradujo: se actualizan junto con él), la documentación de desarrollo
(`CLAUDE.md`, `AGENTS.md`, `docs/claude/`, `docs/changes/`), las memorias de los asistentes
(`.claude/`, `.gemini/`, `.codex/`) y los prompts y descripciones que lee el LLM
(`prompt.pmt`, `tools.py`, `chat_agent_registry.py`, `SKILL.md`).

**Se deja para después (por decisión de Angela): la voz.** Whisperer (faster-whisper), el
dictado del chat y Talker (voz basada en LLM) se portan tal cual, sin tocar su motor ni sus
idiomas. Las etiquetas de pantalla de sus controles sí se traducen.

---

## 5. Método

Todo se hace con `l10n/portar.py`, desde la raíz de Tlamatini-Spanish:

| Paso | Comando | Qué hace |
|---|---|---|
| 1 | `python l10n/portar.py copiar --ingles C:/Development/XAIHT/Tlamatini` | Copia los archivos versionados del commit inglés (por omisión HEAD) y anota la base. |
| 2 | `python l10n/portar.py pendientes [ruta…] [--json]` | Lista los textos de pantalla que no están ni traducidos ni conservados a propósito. |
| 3 | `python l10n/portar.py memorizar decisiones.json` | Agrega pares en→es (o "conservar") a la memoria; calcula cuántas veces aparece cada uno. |
| 4 | `python l10n/portar.py aplicar [ruta…]` | Parte SIEMPRE del original inglés y le aplica la memoria. Idempotente. |
| 5 | `python l10n/portar.py verificar [ruta…]` | Comprueba que sólo cambiaron textos (sección 6). |

**Cómo se arma un par.** El texto inglés va con sus delimitadores, para que el reemplazo
nunca alcance a un identificador vecino: con comillas en JavaScript y Python
(`'Save file'`), entre `>` y `<` en los nodos de texto HTML (`>Username<`) y con el nombre
del atributo (`placeholder="Enter your password"`). Los saltos de línea se guardan como
`\n` y coinciden con LF o CRLF: el reemplazo conserva el final de línea del archivo, y
ningún otro byte cambia.

**Decisiones de cada texto candidato:** traducirlo, o conservarlo con un motivo (es un
término técnico, un nombre o un valor de máquina). Así `pendientes` llega a cero sin
esconder nada.

**El archivo de respuestas** (`l10n/herramientas/decidir.py` lo convierte en decisiones):
un renglón por id, separado por tabulador. Sólo se escribe el texto visible; comillas,
delimitadores y espacios de las orillas salen del original.

| Renglón | Significa |
|---|---|
| `12⇥Guardar archivo` | traducción |
| `13⇥=término técnico` | se conserva en inglés, con su motivo |
| `14⇥!Estoy trabajando en tu solicitud` | traducción **acoplada**: el código compara esa cadena contra un mensaje que se tradujo igual (queda marcada `"maquina"` en la memoria) |

Dos marcas más existen sólo en decisiones escritas a mano (JSON):

- `"maquina"`: para cadenas de contexto máquina que se traducen a propósito junto con su
  productor (los selectores `button:contains("Guardar")`, los `includes(...)` que reconocen
  las líneas fijas de Tlamatini, `toLocaleString('es-MX')`).
- `"libres"`: términos de la lista de intocables que en ESE texto no son nombres (un "AND"
  enfático en un tooltip no es el agent AND), y por eso pueden desaparecer de la traducción.
- `"llm"`: el texto es un prompt del Catálogo de prompts. Sus `{{ … }}` son marcadores que
  llena el LLM (no plantillas Django), así que se traducen por dentro
  (`{{ tu directorio Templates }}`); `verificar` sólo exige la misma cantidad de marcadores.
- `"codigo"`: una **adaptación funcional declarada**, la única forma permitida de cambiar
  código. Hoy hay una: el validador de forma del prompt (`rag/interface.py`) también acepta
  preguntas y verbos en español, para que una solicitud como "Muéstrame el log" no reciba
  "Reformula tu input". `verificar` la prueba aparte (el archivo compila y el resto sólo
  cambió textos) y la muestra como aviso en cada corrida.

---

## 6. Control de calidad

`portar.py verificar` corre estas pruebas sobre cada archivo:

1. **Sin memoria ⇒ idéntico** al original inglés, byte por byte.
2. **Con memoria ⇒ exactamente `aplicar(original, memoria)`**: nada editado a mano.
3. **Sólo cambiaron textos:**
   - JavaScript: el flujo de tokens (acorn) es idéntico salvo el contenido de las cadenas,
     y ninguna cadena traducida está en un contexto de máquina (selectores,
     `addEventListener`, comparaciones, llaves, `fetch`, `classList`…).
   - Python: el flujo de tokens es idéntico, compila, y ninguna cadena traducida es llave
     de diccionario, operando de una comparación, argumento de `startswith`, `get`,
     `getattr`, etcétera.
   - HTML: el esqueleto de la plantilla es idéntico; las etiquetas Django dentro del texto
     no cambian; los `<script>` en línea pasan la prueba de JavaScript.
   - YAML y JSON: mismas llaves y tipos; sólo cambian valores declarados traducibles.
   - Markdown: mismos bloques de código, comentarios (banner de autora incluido), niveles de
     títulos, forma de las tablas, destinos de enlaces y fragmentos de `código`.
4. **Cada par en→es** (al estilo pofilter): mismos marcadores (`{name}`, `%s`, `${`,
   `{{ }}`, `{% %}`, entidades), mismas etiquetas HTML y URLs, mismos delimitadores, los
   nombres intocables sobreviven y no aparece ninguna traducción prohibida del glosario.
5. **Acoplamientos:** si una frase traducida aparece también en otro archivo de código (un
   matcher que la reconoce por sus palabras: `includes`, `===`, `in`, listas de
   subcadenas), ese otro archivo tiene que estar traducido igual. Así no se repite el caso
   de un centinela traducido de un solo lado.
6. **Etiquetas que el código compara:** un índice de todo el árbol inglés junta cada valor
   que aparece en una comparación (`=== 'Cancel'`, `button:contains("Save")`, `case`,
   `includes`, `== "…"` en Python). Si una etiqueta se traduce, cada comparación que la
   busca debe traducirse en el mismo paso (marca `!` o `"maquina"`), o la etiqueta se
   conserva. Por eso las etiquetas de botón tienen una traducción fija
   ([GLOSARIO §5](GLOSARIO.md)).

Después de la verificación estática viene la **prueba visible**: el servidor de
Tlamatini-Spanish en una ventana a la vista, Chrome real con Playwright *headed* recorriendo
la interfaz, y las fotos de pantalla completa las toma el agent **Shoter**.

---

## 7. Cómo sincronizar con una versión nueva del inglés

```
python l10n/portar.py copiar --ingles C:/Development/XAIHT/Tlamatini
python l10n/portar.py aplicar          # avisa qué pares ya no coinciden
python l10n/portar.py pendientes       # textos nuevos o cambiados
#   … traducir lo pendiente → decisiones.json → portar.py memorizar …
python l10n/portar.py aplicar
python l10n/portar.py verificar        # debe terminar con 0 errores
```

Los pares que dejaron de coincidir se revisan: si el inglés sólo cambió de lugar, el par
se sigue aplicando solo; si cambió el texto, se traduce de nuevo. Un archivo que
desapareció del inglés deja su memoria huérfana y `aplicar` lo reporta.

---

## 8. Fuentes

Ingeniería de localización

- W3C, *Localization vs. Internationalization*: https://www.w3.org/International/questions/qa-i18n
- GNU gettext, *Preparing Strings* y *Plural forms*: https://www.gnu.org/software/gettext/manual/html_node/Preparing-Strings.html · https://www.gnu.org/software/gettext/manual/html_node/Plural-forms.html
- Mozilla, *Localization best practices for developers*: https://mozilla-l10n.github.io/documentation/localization/dev_best_practices.html
- Microsoft, *Best practices for developing world-ready apps*: https://learn.microsoft.com/en-us/dotnet/core/extensions/best-practices-for-developing-world-ready-apps
- Microsoft, *Pseudolocalization*: https://learn.microsoft.com/en-us/globalization/methodology/pseudolocalization
- Django, *Translation* y *Format localization*: https://docs.djangoproject.com/en/stable/topics/i18n/translation/ · https://docs.djangoproject.com/en/stable/topics/i18n/formatting/
- Django, formatos `es_MX` y `es`: https://raw.githubusercontent.com/django/django/main/django/conf/locale/es_MX/formats.py · https://raw.githubusercontent.com/django/django/main/django/conf/locale/es/formats.py
- WHATWG, atributos traducibles: https://html.spec.whatwg.org/multipage/dom.html
- W3C, `lang` y declaración de idioma: https://www.w3.org/International/questions/qa-html-language-declarations
- WCAG 2.2, 3.1.1 y 2.5.3: https://www.w3.org/WAI/WCAG22/Understanding/language-of-page.html · https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html
- A. Roselli, *aria-label does not translate*: https://adrianroselli.com/2019/11/aria-label-does-not-translate.html
- YAML 1.2.2: https://yaml.org/spec/1.2.2/ · resolver de PyYAML: https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/resolver.py
- Translate Toolkit, pruebas de pofilter: https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pofilter_tests.html
- W3C, expansión del texto: https://www.w3.org/International/articles/article-text-size
- Adobe Spectrum, diseño internacional: https://spectrum.adobe.com/page/international-design/
- Microsoft, índice de guías de estilo: https://learn.microsoft.com/en-us/globalization/reference/microsoft-style-guides
- Microsoft, guías de estilo España y EE. UU.: https://download.microsoft.com/download/9/a/1/9a19beca-597c-417b-a2c2-0f1ea5a1e6c3/spa-esp-StyleGuide.pdf · https://download.microsoft.com/download/8/9/a/89ae1f7a-6c96-4f75-b51c-5590735ee810/spa-usa-StyleGuide.pdf
- Apple, *Human Interface Guidelines: Inclusion*: https://developer.apple.com/design/human-interface-guidelines/inclusion
- Unicode CLDR, formatos es-MX: https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/cldr-numbers-full/main/es-MX/numbers.json · https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/cldr-dates-full/main/es-MX/ca-gregorian.json
- msgmerge: https://man7.org/linux/man-pages/man1/msgmerge.1.html · po4a: https://po4a.org/man/man7/po4a.7.php
- Mozilla, localización desde Nightly: https://blog.mozilla.org/l10n/2017/04/18/localizing-nightly-by-default/
- Prompts multilingües: https://arxiv.org/abs/2512.02841 · https://arxiv.org/abs/2406.20052 · https://platform.claude.com/docs/en/build-with-claude/multilingual-support

Herramientas técnicas en español

- Git, `es.po`: https://code.googlesource.com/git/+/refs/tags/v2.33.2/po/es.po
- VS Code, paquete de idioma: https://github.com/microsoft/vscode-loc
- GitHub Docs, glosario: https://docs.github.com/es/get-started/learning-about-github/github-glossary
- python-docs-es, guía de contribución: https://python-docs-es.readthedocs.io/page/CONTRIBUTING.html
- Kubernetes, guía de localización al español: https://raw.githubusercontent.com/kubernetes/website/main/content/es/docs/contribute/localization_es.md
- Mozilla, guías de estilo (es-MX, es-ES, es-CL): https://github.com/mozilla-l10n/styleguides
- FastAPI, prompt de traducción al español: https://raw.githubusercontent.com/fastapi/fastapi/master/docs/es/llm-prompt.md
- GNOME, equipo de español: https://wiki.gnome.org/TranslationProject/SpanishTeam
- Debian, notas de traducción: https://www.debian.org/international/spanish/notas
- Microsoft Learn, ejemplos de traducción automática: https://learn.microsoft.com/es-mx/azure/aks/core-aks-concepts · https://learn.microsoft.com/es-mx/visualstudio/version-control/git-fetch-pull-sync
- GitLab, pestañas "Cambios": https://gitlab.com/gitlab-org/gitlab/-/issues/215956

Español de México

- Microsoft, guía de estilo es-MX: https://download.microsoft.com/download/9/0/1/9016efc5-6455-4a9d-ae78-ed3df93b2851/spa-mex-StyleGuide.pdf
- Apple es-MX: https://support.apple.com/es-mx/109323 · Google es-419: https://support.google.com/chrome/answer/95346?hl=es-419
- CLDR (datos de es-MX): https://github.com/unicode-org/cldr-json
- FundéuRAE sobre *token*: https://www.diariolibre.com/actualidad/internacional/fundeurae-token-en-redonda-o-toquen-adaptaciones-de-token-FB30313314
- RAE, *clic*: https://www.rae.es/dpd/clic
- Academia Mexicana de la Lengua: https://academia.org.mx/consultas/consultas-frecuentes/item/cookie · https://academia.org.mx/consultas/consultas-frecuentes/item/genero-y-lenguaje
- RAE, nota del 13 de febrero de 2024: https://www.rae.es/sites/default/files/2024-02/Nota%20de%20la%20RAE%2013%20de%20febrero%20de%202024.pdf
- Platzi: https://platzi.com/cursos/git-github/haciendo-deployment-a-un-servidor/ · https://platzi.com/cursos/prompt-engineering-2025/
- EDteam: https://ed.team/blog/que-es-deploy
- Alcalde y Gregorio Cano, *Íkala* (2013): https://revistas.udea.edu.co/index.php/ikala/article/download/13870/13830/53967
- Mercado Pago, guía de estilo: https://www.mercadopago.com.mx/developers/es/docs/style-guide/translations-language-specifics.md
