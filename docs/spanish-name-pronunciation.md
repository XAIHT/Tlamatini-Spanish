<!-- Tlamatini Author Banner — Angela López Mendoza · @angelahack1 -->
# Nombres pronunciados en Tlamatini-Spanish

Implementación de fuente, 28 de octubre de 2026. Exclusiva de este repositorio;
no es una nueva aceptación de un instalador ni modifica la instalación existente.

## Comportamiento

`angela`, `Angela`, `ANGELA`, `angéla` y `Angéla` se preparan con la tilde en la
primera sílaba: **Ángela**. El catálogo compartido restaura las grafías de 143
nombres y apellidos, incluidos José, María, Jesús, Sofía, Raúl, Héctor, Mónica,
Ángel, Angélica, López y García. Se conserva la capitalización y se normaliza
Unicode NFC. No se añade una tilde a Ana, Luis, Guadalupe o Ximena.

Los logins y la autenticación permanecen intactos. Django admite nombres de
usuario Unicode con tildes; no hace falta renombrar una cuenta para que hable
bien. El nombre de pila del perfil tiene prioridad y el login sirve de respaldo,
como ya hacía el servidor. Avatar y Talker reciben ahora la misma interpretación
del nombre de la cuenta actual. No se usa el último usuario que inició sesión.

La preparación ocurre antes de dividir y sintetizar el texto, en el módulo
compartido `agent/agents/talker/spanish_pronunciation.py` y su catálogo serializado
para el navegador. Abarca chat, avatar, narración del editor/terminal, Agentic
Control Panel y Prompt Flow Panel mediante `voice_runtime.js`; Talker la aplica
antes de despachar a cualquiera de sus dos motores.

No se reescriben mensajes guardados, URLs, correos, rutas, bloques de código ni
identificadores técnicos. Los nombres desconocidos y las tildes explícitas se
respetan, salvo la corrección solicitada de **Angéla → Ángela**. Palabras ambiguas
en minúsculas, como `cesar` o `leon`, no se cambian en prosa ordinaria. Un login
opaco no permite adivinar universalmente el nombre de una persona.

Para excepciones personales de Talker existe el mapa de configuración:

```yaml
name_pronunciations:
  login_persona: María José
  Miriam: Miriam
```

Estas excepciones tienen prioridad sobre el catálogo. El nombre del perfil es
la opción compartida con el avatar para asociar un login opaco a un nombre.

## Motores y voces

**Avatar:** la selección automática prefiere es-MX, después otras variantes
latinoamericanas y finalmente es-ES. Una preferencia antigua de voz inglesa no
desplaza una voz española cuando el idioma solicitado es español. Sin una voz
femenina española disponible, devuelve `unavailable`. El selector de la edición
española muestra las voces femeninas españolas disponibles.

**Piper:** mantiene la voz mexicana `es_MX-claude-high`, cuyo modelo declara el
fonetizador **es-419**. El subproceso recibe UTF-8 explícito mediante
`PYTHONIOENCODING=utf-8` y `PYTHONUTF8=1`: en Windows una tubería de entrada no
debe reinterpretar las tildes con la página de códigos ANSI. El entorno del
proceso padre no cambia. Se conserva la frecuencia nativa y el modelo original.

**Orpheus:** Tara, Leah, Jess, Mia y Zoe reciben la misma corrección. Para
`legraphista/Orpheus` y los modelos ingleses de origen conocidos se respeta el
formato documentado `voz: texto`; no se les envía un supuesto control `<es>`.
Los modelos personalizados conservan su opción de etiqueta de idioma.
La síntesis correcta de un WAV no prueba su pronunciación: este modelo se entrenó
para inglés y las tildes no lo convierten en un modelo mexicano. Se registra esa
limitación y se ofrece Piper explícitamente, sin sustituir a escondidas el motor.

Se mantiene el contrato existente de voces femeninas; no se habilitan las voces
masculinas ni las de género no verificado.

## Evidencia de esta implementación

Todo se ejecutó desde consolas visibles confirmadas y Chrome con
`headless=False`; la síntesis automatizada guardó audio sin reproducirlo.

- **74 pruebas Python aprobadas:** catálogo, variantes de Ángela, Unicode,
  cuentas, identificadores protegidos, las cinco voces de Orpheus, payload real
  de Ollama, entrega a Piper y UTF-8 incluso con un padre configurado en cp1252,
  además de regresiones existentes de Talker.
- **151 casos Python/navegador coincidentes**, sin errores de JavaScript.
- **Inventario nativo completo del navegador:** David, Mark, Zira, Raúl y Sabina.
  Sabina fue la única voz femenina española instalada y terminó una síntesis
  nativa con volumen cero. Raúl está excluido por el contrato de género; las
  voces inglesas no son candidatas para el avatar en español. El comprobador
  recorre todas las voces femeninas españolas que el navegador exponga.
- **Síntesis real de las seis voces permitidas:** Jess, Leah, Mia, Tara y Zoe
  con `legraphista/Orpheus:3b-ft-q8`, y Piper `es_MX-claude-high`.
  Las seis produjeron WAV con audio. El primer intento de Piper detectó una
  dependencia ausente del entorno aislado de pruebas (`pathvalidate`); se
  instaló allí y la repetición pasó.
- **Fonemas reales de Piper:** Angela/Angéla/Ángela → `ˈaŋxela`;
  Jose → `xosˈe`; Maria → `maɾˈiʲa`; Jesus → `xesˈus`;
  Sofia → `sofˈiʲa`; Raul → `raˈul`.
  También coincidieron las variantes en minúsculas y mayúsculas, y los 143
  nombres restaurados produjeron los mismos fonemas que sus grafías canónicas.
- Ruff y ESLint aprobados; 107 archivos JavaScript analizados sin errores.
  `collectstatic` copió los dos JS modificados y Chrome verificó sus bytes
  servidos desde `staticfiles` con el nuevo sufijo de caché. Se usaron ajustes
  aislados de staticfiles, sin conectar una base de datos ni iniciar AgentConfig.
- Muestras y manifiesto: `Temp/name-voice-audio/results.json`.
  Reproductores para las seis muestras: `Temp/name-voice-audio/comparacion.html`.
  Evidencia de Chrome: `Temp/spanish-names-visible/results.json` y `completed.png`.
  Estas pruebas no afirman una evaluación auditiva humana de Orpheus.

Comprobadores reproducibles: `scripts/spanish_names_visible.py` y
`scripts/spanish_names_synthesis_visible.py`. Ejecutarlos solamente desde una
consola visible, siguiendo `TestsVisiblesAndVisibleExecutionFromClaude2Codex.md`.
El segundo usa el Piper de validación en `Temp/piper-validation-runtime`, el
modelo local de Ollama y guarda los modelos Piper de prueba dentro de `Temp`.
El primero deja el navegador abierto hasta crear
`Temp/spanish-names-visible/close.confirmed`. Rechaza opciones headless.

El helper, las pruebas y esta guía están incluidos en los inventarios de
fuente/runtime; el import requerido se lleva también al ejecutable congelado.
Se añadió el sufijo de caché `-spanish-names-1` sin reemplazar la expresión
dinámica de `STATIC_VERSION`. No se ejecutó `build.py`, no hubo migración y no
se tocaron las mecánicas protegidas de respaldo/restauración.

## Fuentes de la investigación

- [Django: validación Unicode del usuario](https://docs.djangoproject.com/en/4.2/_modules/django/contrib/auth/validators/).
- [Ficha oficial de legraphista/Orpheus en Ollama](https://ollama.com/legraphista/Orpheus): modelo en inglés.
- [Orpheus-TTS, repositorio del autor](https://github.com/canopyai/Orpheus-TTS): distingue los modelos ingleses de la familia multilingüe de investigación.
- [Piper, implementación de voz](https://github.com/OHF-Voice/piper1-gpl/blob/main/src/piper/voice.py): fonetización basada en la configuración del modelo.
- [Piper mexicano Claude, ficha del modelo](https://huggingface.co/rhasspy/piper-voices/blob/main/es/es_MX/claude/high/MODEL_CARD).
