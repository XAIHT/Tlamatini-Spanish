# Recuperación y estados fiables de Torrenter — 10 de noviembre de 2026

La última versión publicada sigue siendo **1.92.4**. Este registro documenta
correcciones de desarrollo y sus pruebas; no certifica un paquete recién instalado.

## Cambios

- Una descarga terminada sigue informando `completed` aunque su sesión de pares
  esté detenida o pausada. `desired_state` conserva la intención del usuario. Un
  error de verificación antiguo pasa a `previous_error`; los fallos actuales y
  los errores de entrega permanecen visibles.
- Las consultas de estado y lista incluyen `download_complete`, `restart_action`
  y `recovery_note`. Start continúa una descarga incompleta detenida, Resume una
  pausada y Recheck verifica una fallida. Consulta la revisión actual antes de
  enviar cambios.
- El panel aplica acciones únicamente a los trabajos elegibles e informa los
  omitidos. Una descarga terminada no permite Start ni Cancel. Sus controles de
  selección de archivos y fuentes siguen disponibles cuando está detenida.
  Recheck comprueba las piezas conservadas; Reseed vuelve a habilitar el envío.
- El panel reintenta una respuesta JSON de sesión vacía o truncada hasta dos
  veces, con intervalos de 200 ms. Nunca repite automáticamente modificaciones de
  torrents. Se conservan el inicio de sesión, CSRF y el aislamiento por cuenta.
- El registro de actividad distingue errores actuales e históricos e incluye la
  acción de recuperación. `Tlamatini.md` enseña esas mismas reglas al chat.

## Cambios coordinados de Tlachihuani Jobs

El servicio mantiene dos transferencias activas por cuenta y cuatro por equipo.
Tras 180 segundos sin progreso de datos, una transferencia cede su espacio solo
si otra descarga elegible está bloqueada en la cola. Conserva los archivos
parciales y la intención de ejecutar. Espera al menos 60 segundos y reintenta
después de los trabajos pendientes. No rota trabajos detenidos, pausados, en
comprobación, en verificación ni terminados. La consulta de metadatos tiene una
cola independiente; son límites distintos.

Antes de publicar SHA-256, Jobs espera la confirmación de libtorrent de que la
pausa terminó las operaciones de disco; si no llega en 60 segundos, informa un
fallo recuperable. Los cambios de etiquetas o revisión conservan esa confirmación.
Stop/Start rápidos terminan de liberar el identificador anterior antes de abrir
otro. Recheck borra el error actual y comprueba las piezas sin eliminar parciales.

Estos cambios requieren **actualizar Jobs por separado**. Actualizar solo
Tlamatini no los activa. En esta intervención no se compiló, instaló, reinició
ningún servicio instalado, modificó la cola real ni creó ningún commit.

## Diagnóstico instalado, separado de las pruebas de código

La observación de solo lectura de la cuenta de Angela del 10 de noviembre encontró
24 registros: 21 descargas terminadas y tres incompletas. Los **432 archivos
entregados** de las terminadas coincidieron con sus SHA-256 del manifiesto mediante
una comprobación independiente. Una descarga terminada figuraba detenida y otra
conservaba un error de verificación antiguo. Ninguno demostraba archivos ausentes.

Dos trabajos incompletos estaban detenidos por su estado solicitado (0% y cerca
del 61%); el tercero esperaba pares al 0%. Las semillas reportadas no son semillas
conectadas. Reiniciar no garantiza que regresen los pares, y probar mediante TCP
un puerto de tracker UDP no demuestra su disponibilidad. El código permite una
carrera histórica de escritura, pero los registros disponibles no identifican al
escritor exacto que provocó aquel mensaje.

## Pruebas y reproducción

- **64 comprobaciones automáticas aprobadas:** 12 de recuperación del motor,
  2 de cola de magnets, 8 de entrega, 30 de tabla y 6 del cliente por edición.
- El ensayo de recuperación terminó **cuatro transferencias BitTorrent reales**
  desde pares locales controlados mientras dos enjambres sin fuentes competían
  por los espacios. Los bytes guardados y SHA-256 coincidieron de forma
  independiente. Solo la prueba reduce los tiempos; producción conserva 180/60 s.
- **48 comprobaciones con Chrome visible aprobadas** entre ambas interfaces de desarrollo, Django autenticado y
  la API y el registro de Jobs con datos de prueba aislados: recuperación, reintento
  de lectura de sesión, doce columnas ordenables, teclado, filtros, vistas,
  aislamiento de cuentas y tamaños de 1600/390/320 píxeles. Los registros
  históricos de la interfaz no prueban descargas; eso lo demuestra el ensayo de pares.
- Ruff aprobó los archivos Python modificados de cliente, actividad, pruebas y
  Jobs. ESLint aprobó el JavaScript del panel en ambas ediciones.

Ejecutar desde una consola de desarrollo visible verificada, con el entorno
Python preparado y espacio de pruebas propiedad de la aplicación:

```powershell
# Desde el directorio Django Tlamatini de esta edición:
python -m unittest agent.test_torrenter_recovery -v
# Desde el proyecto separado Tlachihuani, con su runtime privado de libtorrent:
python tests/integration/test_transfer_recovery.py
python tests/integration/test_magnet_queue.py
python tests/integration/test_delivery.py
node --test tests/unit/workspace_table.test.cjs
python tests/desktop/torrenter_table.py --output artifacts/verification/torrenter-recovery --english C:\Development\XAIHT\Tlamatini --spanish C:\Development\XAIHT\Tlamatini-Spanish
```

La evidencia local se conserva en
`C:\Development\XAIHT\Tlachihuani\artifacts\verification\torrenter-state-20261110`:
`session.log`, registros de pruebas, `visual/results.json`, `visual/SUMMARY.html`,
capturas del escritorio y `download-file-checks.json`. No forma parte de una
distribución ni demuestra la actualización de un ejecutable instalado.

Consulta la [guía de Torrenter](../torrenter.md).
