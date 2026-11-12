<!-- Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1 -->
# Verificación del asistente de cuentas — 2026-11-09

Versión registrada durante la verificación del 2026-11-09: **1.92.4**. [Guía del asistente](user-creation-wizard.md).

## Grupo final de aceptación visible

La ejecución final creó **10 cuentas inglesas reales y 10 cuentas españolas
reales** y autenticó cada una en la página de inicio de sesión de la aplicación.
Se aprobaron las **260 comprobaciones de aceptación**. Cada edición realizó
las mismas 13 comprobaciones para cada una de sus 10 cuentas:
**0 diferencias de aprobación o fallo en las 130 comprobaciones emparejadas**.
Esta comparación se limita al asistente de cuentas; no acredita los 127 prompts
del catálogo ni la totalidad de ambos productos.

| Edición | Grupo final | Cuentas reales creadas y autenticadas | Comprobaciones | Envío → campo de nombre legible | Envío → primer plano comprobado |
| --- | --- | --- | --- | --- | --- |
| Inglés | `visible-en-20261109-161020` | 10/10 | 130/130 | 2,351–3,961 s | 2,356–3,966 s |
| Español | `visible-es-20261109-160742` | 10/10 | 130/130 | 2,241–3,153 s | 2,245–3,156 s |

Las 20 consolas ya estaban al frente cuando las comprobó el verificador:
`foreground_before_test_focus=true` y `test_focus_requested=false` en todos
los registros. Por tanto, ninguna medición final de apertura dependió de que
la prueba trajera al frente una consola oculta. La disponibilidad del campo
legible y la exposición real en primer plano se midieron por separado, ambas
desde el envío real en el navegador y por debajo del límite de 30 segundos.

Son los **grupos finales**, no el total de cuentas existentes en las bases de
prueba. Los grupos de QA anteriores y el operador preparado por separado no se
suman a estas 20 cuentas. Ese operador pertenece a la preparación del entorno;
no cuenta como creación interactiva de aceptación.

## Mediciones españolas

Los nombres van de `qa_wiz_es_20261109160742_01` a
`qa_wiz_es_20261109160742_10`. Los tiempos están expresados en segundos.

| Prueba | Campo de nombre disponible | Primer plano real | Verificación HECHO | Enfoque solicitado por la prueba | Resultado |
| --- | --- | --- | --- | --- | --- |
| 1 | 2,985 | 2,987 | 0,164 | No | PASS |
| 2 | 3,153 | 3,156 | 0,097 | No | PASS |
| 3 | 2,389 | 2,392 | 0,083 | No | PASS |
| 4 | 2,424 | 2,427 | 0,088 | No | PASS |
| 5 | 2,519 | 2,522 | 0,181 | No | PASS |
| 6 | 2,391 | 2,396 | 0,093 | No | PASS |
| 7 | 2,241 | 2,245 | 0,227 | No | PASS |
| 8 | 2,409 | 2,413 | 0,080 | No | PASS |
| 9 | 2,474 | 2,478 | 0,077 | No | PASS |
| 10 | 2,301 | 2,305 | 0,117 | No | PASS |

La verificación DONE de cada cuenta inglesa también terminó en
0,080–0,198 segundos. Ambas ediciones comprobaron la
cuenta recién persistida antes de confirmar su creación.

## Qué se comprobó

1. Seleccionar la tarjeta real del catálogo y sus modos en el navegador visible.
2. Enviarla mediante el WebSocket real de la aplicación.
3. Observar el campo de nombre de la consola propia de Django antes de 30 segundos.
4. Comprobar que su ventana es visible, no está minimizada y está realmente al frente.
5. Comprobar que el chat devuelve el control mientras la consola espera los datos.
6. Escribir el nombre y observar el campo de correo de Django.
7. Escribir el correo y observar el campo real de contraseña.
8. Observar el campo de repetición de contraseña.
9. Observar el mensaje real de creación satisfactoria de Django.
10. Comprobar que la contraseña no aparece en el texto de la consola.
11. Leer la base de prueba para comprobar la cuenta, los permisos administrativos
    y el hash almacenado de la contraseña.
12. Enviar HECHO/DONE por el chat y comprobar la cuenta recién creada.
13. Autenticar esa cuenta mediante el formulario normal del navegador.

No se inyectaron cookies de sesión ni se sustituyeron respuestas de herramientas.
La prueba escribió en la consola real propiedad de esta ejecución y utilizó la
validación de contraseñas, persistencia y autenticación reales. La inspección
de la base comprobó el resultado; no creó las 20 cuentas de aceptación.

La ruta cerrada del asistente no llama a un modelo ni a un agente de visión para
construir o ejecutar su orden. El inicio normal de la aplicación y el indicador
de contexto pueden efectuar llamadas a modelos por otras rutas; este informe
no afirma que todo el servidor estuviera libre de esas llamadas. La contraseña
se escribió solamente en la consola y en el formulario normal de acceso,
nunca como contenido del chat ni como argumento de un comando.

## Correcciones cubiertas

- Se sustituyó la secuencia de órdenes generada por el modelo para la tarjeta
  predeterminada por un controlador nativo que reconoce su texto completo.
  Usa el ejecutable, directorio y base de Django de esta instancia, con
  `shell=False`.
- Se eliminaron, para esta operación, la ambigüedad PowerShell/CMD y el ciclo
  posterior de consultas a modelos o agentes de visión.
- Se añadió `createuserconsole`, subclase específica del comando real
  `createsuperuser` de Django. Conserva las comprobaciones de modelos,
  migraciones, nombres duplicados y contraseñas; no espera comprobaciones
  web ni inicializaciones de modelos ajenas a la creación de la cuenta.
- El proceso de la cuenta no trunca el registro del servidor ni copia la
  entrada privada al mecanismo compartido de registro.
- Las solicitudes conocidas se atienden antes de esperar al modelo o preparar
  contexto, conservando autenticación, Ask Execs y cancelación. Si un candidato
  antiguo resulta ajeno al asistente, no utiliza un modelo anterior mientras
  se reconstruye la cadena.
- Las respuestas de nombre y estado pertenecen a la respuesta previa del
  asistente. La confirmación retira ese contexto. Los manejadores de procesos
  vivos protegen la espera intencional frente a la limpieza de huérfanos y
  el supervisor de procesos.
- Se conservan las tarjetas personalizadas; la migración 0227 repara sólo los
  valores predeterminados conocidos. La ruta integrada informa en el chat
  y no afirma haber mostrado los antiguos diálogos de Notifier.
- Se añadieron importaciones explícitas y comprobaciones del archivo congelado
  para el controlador, el comando y los módulos de catálogo actuales e
  históricos importados dinámicamente. Estos contratos de fuentes no equivalen
  a una nueva compilación congelada.

## Pruebas unitarias y lint

| Verificación | Inglés | Español |
| --- | --- | --- |
| Regresiones enfocadas | 218 aprobadas; 7,138 s | 252 aprobadas; 6,972 s |
| Compilación Python | 948 fuentes propias | 976 fuentes propias |
| Reglas predeterminadas de Ruff | Aprobadas; salida 0 | Aprobadas; salida 0 |
| ESLint JavaScript | Aprobado; salida 0 | Aprobado; salida 0 |
| Análisis sintáctico JavaScript | 108 archivos; salida 0 | 110 archivos; salida 0 |
| Espacios y finales de línea de fuentes acotadas | Aprobado; salida 0 | Aprobado; salida 0 |

Las suites cubren reconocimiento, estado, autorización y cancelación del
controlador nativo; enrutamiento durante la reconstrucción del modelo;
despacho, privacidad y preparación congelada del comando Django; contratos del
catálogo y reglas previas de intención del asistente. Español añade las
comprobaciones de sus migraciones de paridad de ejecución del catálogo.
Esos casos propios de cada edición explican los distintos totales. Los casos
con lanzamiento u operaciones del sistema simuladas **no** son cuentas reales
adicionales ni pruebas visuales.

Registros bajo el directorio de evidencia: `unit-en-proof.log` y
`unit-es-proof.log`; `lint-python-en-proof.log` y
`lint-python-es-proof.log`; `lint-js-en-final.log` y
`lint-js-es-final.log`. Todos sus archivos `.exit` correspondientes contienen 0.
`source-diff-en-proof.exit` y `source-diff-es-proof.exit` también contienen 0;
esa revisión se limita a las fuentes de esta reparación y admite CRLF de
Windows mediante `cr-at-eol`. No se modificaron fuentes JavaScript después
de sus comprobaciones registradas.

El lote visible final concluyó el **2026-11-09 a las 16:14:36 -06:00**, según
`final-verification-complete.txt`. Su inventario final encontró **0 puertos
de prueba en escucha y 0 procesos de los entornos de prueba**. La consola
visible de desarrollo quedó abierta con los resultados; se conservaron la
evidencia y las bases aisladas.

## Evidencia y límites

Directorio de evidencia local de esta máquina:

`C:\Development\XAIHT\Tlamatini-Spanish\Temp\wizard-repair-20261109`

- Inglés: `visible-en-20261109-161020\result.json`.
- Español: `visible-es-20261109-160742\result.json`.
- Cada grupo contiene capturas de consola, creación satisfactoria, navegador
  autenticado y chat verificado, además del texto de cada consola.
- Registros: `visible-proof-en.log` y `visible-proof-es.log`.

La edición inglesa ejecutó una copia de las fuentes actuales en
`source-instance-en`, puerto `http://127.0.0.1:18058`. La española utilizó
`source-instance`, puerto `http://127.0.0.1:18059`. Cada entorno tuvo su
propia base. Las aplicaciones ya instaladas y sus bases de usuarios no fueron
los objetivos de aceptación. La evidencia permanece en almacenamiento de
desarrollo de la aplicación, no en directorios temporales de perfiles de Windows;
no se incluye en instalaciones para usuarios finales.

El intento español reforzado de las 16:04 se conserva por separado en
`visible-es-20261109-160409`, marcado FAIL. Su quinta comprobación seleccionó
la última tarjeta del bot: un aviso asíncrono de modelo listo que llegó después
de la respuesta real del asistente. La comprobación corregida busca la respuesta
de la solicitud actual y verifica que el chat haya devuelto el control.
Ese fallo no se convirtió en aprobación ni se sumó al grupo final de 20 cuentas.

Aquí no se generó un nuevo ejecutable ni se aprobó un paquete instalado.
Es necesario reconstruir e instalar las fuentes corregidas antes de atribuir
el resultado a una instalación congelada existente. Esta reparación y
verificación no realizaron commits ni pushes.

