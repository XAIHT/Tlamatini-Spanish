# Tlamatini Blue-hat Security Toolkit (`security/`)

Este directorio contiene el **kit defensivo de Windows, operado por una
persona**, de Tlamatini. Úsalo únicamente en una máquina Windows 10/11 que sea
tuya o que tengas autorización explícita para defender. No es un Agent nuevo
del chat ni del canvas, ni un antivirus, ni un EDR, ni un SIEM, ni un producto
forense, ni un reemplazo de Microsoft Defender y de un proceso real de
respuesta a incidentes.

> Creado por **Angela López Mendoza** (`@angelahack1`). Tlamatini — *la que
> sabe*.

> **Edición en español.** Esta es la copia del árbol `Tlamatini-Spanish`. Su
> arnés de pruebas toma las fotos con `toma_foto()` (el árbol en inglés la
> llama `take_shot()`) y todas sus superficies visibles están en español. Los
> dos `.ps1` conservan sus mensajes en inglés **a propósito**: el arnés hace
> aserciones sobre frases exactas de esos archivos (por ejemplo
> `verified in Audit mode`), así que traducirlas dejaría la prueba en verde
> sin comprobar nada. Ver `docs/claude/recent-fixes.md` (2026-08-26).

`tlamatini_whitelist_v2.ps1` makes persistent host changes. Defender and firewall
services remain running, but the script adds Defender path/process exclusions,
allows Tlamatini through Controlled Folder Access, changes six selected ASR rules
to **Audit** instead of Block, creates broad outbound allow rules, changes the
current user's PowerShell execution policy, grants Security-log visibility, and
enables additional auditing/logging. These exceptions reduce enforcement around
Tlamatini and can become a blind spot if an attacker writes into the excluded tree.

`tlamatini_whitelist_v2.ps1` hace cambios **permanentes** en el equipo.
Defender y el firewall siguen encendidos, pero el script agrega exclusiones de
ruta/proceso en Defender, permite a Tlamatini pasar por Controlled Folder
Access, cambia seis reglas ASR seleccionadas a **Auditoría** en vez de Bloqueo,
crea reglas amplias de salida, cambia la política de ejecución de PowerShell
del usuario actual, otorga visibilidad del registro de Seguridad y activa
auditoría/registro adicionales. Esas excepciones **reducen la protección**
alrededor de Tlamatini y pueden convertirse en un punto ciego si un atacante
logra escribir dentro del árbol excluido.

Por ahora **no hay script de reversión**. Anota el estado actual de Defender,
ASR, CFA, política de ejecución, firewall, política de auditoría y registro de
Seguridad **antes** de correr la whitelist, y protege el directorio de
Tlamatini como una frontera de confianza privilegiada.

## Activos

| Archivo | Para qué sirve |
|---|---|
| `enable_tlamatini_v2.bat` | Se autoeleva y corre una sola vez la configuración de whitelist/visibilidad. |
| `tlamatini_whitelist_v2.ps1` | Aplica las excepciones permanentes de Windows, la auditoría y el acceso al registro de Seguridad; verifica visibilidad de WMI/tareas/registro/servicios. |
| `run_defender.bat` | Se autoeleva y corre **un** barrido del defender en modo armado (el modo por defecto). |
| `tlamatini_defender.ps1` | Monitor de diez familias de señales, con modos detect-only, armado, watch y agresivo. |
| `automated_tests_of_security_assets.py` | Arnés de regresión **visible y no destructivo**: sintaxis, clasificador, configuración y lanzadores. No aplica la whitelist ni corre un barrido armado. |
| `README.md` | Esta referencia rápida para quien opera. |

## Secuencia de despliegue más segura

1. Read and diff every asset in this directory.
2. Run the non-destructive visible test:

   ```powershell
   python security\automated_tests_of_security_assets.py
   ```

   Abre una ventana de PowerShell en primer plano y Chrome/Chromium **con
   interfaz**, captura todo el escritorio con Shoter y guarda la evidencia en
   `security_logs\asset_tests\`. Ojo: esas capturas pueden contener
   información sensible de tu escritorio.

3. Anota el estado actual de las políticas de seguridad de Windows, o crea un
   punto de restauración.
4. Corre `enable_tlamatini_v2.bat`, aprueba el UAC, revisa **cada** `[WARN]` y
   reinicia Tlamatini / abre una sesión nueva de PowerShell.
5. Establece los falsos positivos con un barrido elevado en modo detect-only:

   ```powershell
   cd <raíz-de-Tlamatini>\security
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tlamatini_defender.ps1 -DetectOnly
   ```

6. Revisa `security_logs\alerts.log` y `security_logs\monitor.log`. Lo que
   encuentres son **pistas**, no pruebas de que te comprometieron.
7. Arma la respuesta sólo cuando ya entiendas la línea base.

## Detalles de la activación

La whitelist pone estos seis comportamientos ASR de Microsoft en acción `6`
(Auditoría):

1. Aplicaciones de Office creando procesos hijos.
2. Robo de credenciales de LSASS.
3. Persistencia por suscripción a eventos WMI.
4. Contenido ejecutable venido de correo y webmail.
5. Procesos no confiables o sin firma corriendo desde USB.
6. Creación de procesos vía PSExec y WMI.

El script vuelve a leer de Defender los arreglos efectivos de reglas/acciones
después de cada escritura, e imprime `[OK]` sólo cuando verifica el GUID exacto
en modo Auditoría. Auditar **registra** un comportamiento; no lo bloquea. El
arnés de pruebas revisa esos identificadores y puedes compararlos con la
[referencia de reglas ASR de Microsoft](https://learn.microsoft.com/es-es/defender-endpoint/attack-surface-reduction-rules-reference).

La configuración de auditoría usa GUIDs estables de subcategoría de Windows en
vez de nombres para mostrar en inglés. Activa Inicio de sesión, Validación de
credenciales, Uso de privilegios confidenciales y Administración de cuentas de
usuario (éxito y error), más Creación de procesos (éxito), y revisa el código
de salida de cada `auditpol`. La línea de comandos de los procesos y el Script
Block Logging pueden conservar argumentos sensibles en los registros de eventos
de Windows.

Los lanzadores `.bat` preservan rutas con espacios durante la elevación por UAC
y devuelven el código de salida del proceso de PowerShell que acompañan. Aun
así, un lanzador puede aplicar la whitelist **de forma parcial**, porque el
script de PowerShell continúa después de cada advertencia: siempre lee la
salida de la consola.

## Defender modes

```powershell
.\tlamatini_defender.ps1 -DetectOnly
.\tlamatini_defender.ps1 -Watch -DetectOnly
.\tlamatini_defender.ps1 -Watch -IntervalSeconds 30 -DetectOnly
.\tlamatini_defender.ps1                 # una pasada, armado
.\tlamatini_defender.ps1 -Watch          # barridos armados cada 60 segundos
.\tlamatini_defender.ps1 -Aggressive     # además mata herramientas de doble uso fuera de las rutas propias
```

`Ctrl+C` detiene el modo watch. `-Watch` es un proceso en primer plano, no un
servicio instalado ni una tarea programada. `run_defender.bat` siempre elige el
modo armado de una pasada; para los demás interruptores usa el script de
PowerShell directamente. `-IntervalSeconds` acepta de `5` a `86400`.

## Qué se monitorea

El defender lee diez familias de señales:

1. Salud de Microsoft Defender, estado de tamper, antigüedad de firmas y
   detecciones recientes.
2. Inicios de sesión con éxito/error del registro de Seguridad y conteo de IPs
   de origen en ataques de fuerza bruta.
3. Conexiones TCP establecidas y puertos a la escucha sospechosos.
4. Nombres de proceso, rutas, patrones de herramientas de atacante conocidas y
   utilerías de doble uso.
5. Acciones y argumentos de tareas programadas que no son de Microsoft.
6. Servicios corriendo fuera de las rutas normales de Windows/Program Files.
7. Persistencia en Run/RunOnce, Winlogon, AppInit e IFEO.
8. Ejecutables/scripts modificados recientemente en Temp, Public y ubicaciones
   de Inicio.
9. Líneas de comando de ransomware / manipulación de recuperación, notas de
   rescate y ráfagas de extensiones cifradas.
10. Cuentas nuevas, altas en el grupo de administradores y administradores
    locales actuales.

## Límites de la respuesta

- El modo detect-only registra `WOULD BLOCK` y `WOULD KILL`; nunca ejecuta esas
  acciones.
- La respuesta armada a inicios de sesión crea reglas permanentes de entrada y
  salida en el Firewall de Windows tras al menos **cinco** eventos fallidos
  desde una misma IP no local en la muestra inspeccionada. Las reglas se llaman
  `Tlamatini Block <IP> Inbound|Outbound` y **no expiran solas**.
- La respuesta armada a procesos detiene por la fuerza los nombres base
  clasificados como herramientas de atacante conocidas. Las rutas reconocidas
  de Tlamatini se rechazan; los nombres de doble uso (`nmap`, `nc`, `john`,
  `hashcat` y otros) sólo alertan, y se detienen únicamente con `-Aggressive`.
- Puertos sospechosos, tareas, servicios, entradas de registro, archivos
  recientes, indicadores de ransomware y eventos de cuentas normalmente **sólo
  alertan**.
- Las heurísticas de nombre/ruta/puerto/extensión producen falsos positivos y
  falsos negativos. «Propio» es una comprobación de **ruta**, no una garantía
  de firma ni de procedencia.

Inspect persistent blocks with:

```powershell
Get-NetFirewallRule -DisplayName "Tlamatini Block *"
```

Elimina sólo el par de reglas de una IP ya validada después de revisar el
incidente; no borres todas las reglas de Tlamatini a ciegas.

## Logs and privacy

`alerts.log` y `monitor.log` son flujos de sólo-anexar bajo `security_logs/`; el
modo watch puede repetir hallazgos. No hay rotación, retención, base de datos de
deduplicación, desbloqueo automático ni reenvío a un SIEM. Los registros y la
auditoría de Windows pueden exponer nombres de usuario, IPs, membresía de
administradores, rutas de procesos, argumentos de registro/tareas, bloques de
script y líneas de comando completas. Restringe el acceso y redacta antes de
compartir.

`security_logs/` está en `.gitignore`, se excluye de las compilaciones públicas
y se poda de los snapshots de auto-modificación. `build.py` copia el resto de
`security/` junto al ejecutable; `copy_source_assets.py` lleva su código fuente
a los snapshots reconstruibles.

**Tu evidencia sobrevive a una actualización.** `security/` es código de la
aplicación, así que una versión nueva **reemplaza** los scripts — eso es lo
correcto: un defender corregido tiene que poder llegarte. Pero
`security/security_logs/` es **tuyo**, y vive dentro de ese directorio
reemplazado. Por eso `apply_update.ps1` lo mueve a
`Temp/_security_logs_carryover` antes de borrar (paso 3c) y lo regresa al nuevo
`security/` después (paso 5b). Las dos mitades fallan hacia adelante: si algo
sale mal la actualización termina igual y tu evidencia se queda en
`Temp/_security_logs_carryover` en lugar de perderse.

Para el modelo de amenazas completo, los comandos de línea base, la matriz de
monitoreo/acción, el comportamiento de empaquetado y la lista de verificación
del despliegue, lee **«Activa a Tlamatini como agente Blue-hat»** en
`README.md` y en `BookOfTlamatini.md`.
