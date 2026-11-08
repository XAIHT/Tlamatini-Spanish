# Compilación conjunta de las ediciones inglesa y española

> Última versión publicada: **[v1.92.4](changes/2026-11-08-v1.92.4.md)**.

## v1.92.4 — Versiones coincidentes, identidad explícita y Markdown legible

El compilador combinado anticipa el número que informará cada edición antes de compilar, fija una versión común, ejecuta las parejas Privada/Pública en paralelo con `--self-modify` y archiva los ZIP verificados por edición, modalidad y minuto. El registro identifica la modalidad incorporada en el paquete. La preparación de dependencias usa cachés aisladas dentro de ubicaciones de la aplicación y se detiene si no existe un entorno válido. El Markdown legible con controles aislados se abre conservando sus bytes; el contenido binario sigue rechazándose. Consulta las [notas de 1.92.4](changes/2026-11-08-v1.92.4.md).

Creado para Angela López Mendoza · XAIHT

El punto de entrada de esta estación de trabajo es
`C:\Development\XAIHT\BuildTlamatinis.cmd`; conserva `BuildTlamatinis.py`
a su lado. La guía detallada está en `C:\Development\XAIHT\BuildTlamatinis.md`.
Estos archivos viven fuera de ambos repositorios y no forman parte de la aplicación instalada.

Desde una ventana visible del Símbolo del sistema:

```bat
cd /d C:\Development\XAIHT
BuildTlamatinis.cmd --build_type public --check
BuildTlamatinis.cmd --build_type public
```

Sustituye `public` por `private` para compilar una versión privada con claves.
Ambas modalidades ejecutan los scripts completos de las dos ediciones **en paralelo**,
siempre con `--self-modify` y la misma versión explícita. Antes de iniciar cualquiera,
el lanzador ejecuta `resolve_build_version()` de cada repositorio y simula en memoria
las salidas de su emisor real de versión. Deben coincidir exactamente los números
que mostrarán las aplicaciones. Se respeta `TLAMATINI_VERSION` como hacen los
compiladores originales; no se exige una etiqueta en HEAD. Se pasa una misma
versión mediante `--version` a ambos. `--Override_versioning X.Y.Z` fuerza un
número común; sin número, usa el detectado en inglés para ambas ediciones.
`--check` permite comprobarlo sin compilar. No se crean commits, etiquetas ni publicaciones. Los cambios
locales del árbol de trabajo se incluyen.

Cada ZIP nuevo y correcto se valida mediante CRC, recibe su huella SHA-256 y se mueve a
`C:\Development\XAIHT\Tlamatinis-Releases\<edición>\Public-o-Private\AAAA-MM-DD_HH-mm\`.
`<edición>` es `Tlamatini` o `Tlamatini-Spanish`; los nombres reales de las carpetas
son `Public` y `Private`. Si se repite el minuto se añade un sufijo numérico.
Los registros y comprobantes quedan en `.runs\<fecha>\`, separados de los ZIP.
Cada edición utiliza su propia caché fuera de los perfiles de usuario. Un fallo en
una edición no elimina el ZIP correcto de la otra; el resultado general solo es cero
si ambas terminan correctamente. Los ZIP antiguos o fallidos no se mueven.

Los compiladores existentes conservan sus requisitos, controles de privacidad y efectos,
incluida la recreación de la base de datos de desarrollo y las salidas de compilación.
Guarda tu trabajo antes de una compilación real. Los ZIP privados contienen datos y
claves privados: no se deben publicar como versiones públicas. Mantén las consolas
abiertas hasta que finalice la limpieza.

## Primeras líneas del registro de la aplicación

Los scripts completos pasan `--release-type private` o `--release-type public`
a `build.py`. El tipo queda integrado en el módulo existente `agent._version`,
incluso si no se usa el lanzador conjunto. El registro `tlamatini.log` comienza con:

```text
--- [VERSION] Tlamatini-Spanish <versión>
--- [RELEASE] Tlamatini-Spanish | PRIVADA (Private)
```

La compilación pública muestra `PUBLICA (Public)`; el código fuente muestra
`DESARROLLO`; los binarios anteriores y las compilaciones sin tipo explícito muestran
`NO ESPECIFICADA`. El valor no se deduce de variables de entorno, rutas o credenciales.
`get_version_info()` también incluye `release_type`. Es información del origen de la
compilación, no una certificación independiente de privacidad.

Es necesario recompilar e instalar para ver el cambio en una aplicación congelada.
Las instalaciones existentes no se modifican. La distribución actual del módulo de
versión y la copia de código fuente llevan este cambio sin nuevas dependencias ni
cambios en el registro de Windows o las reglas de conservación de datos.

## Verificación — 2026-11-07

Las pruebas visibles del lanzador utilizan procesos paralelos reales con archivos de
prueba aislados. Cubren ambas modalidades, etiquetas, argumentos, fallos parciales,
ZIP antiguos o dañados, colisiones, bloqueos y sintaxis de PowerShell. Ambas ediciones
pasan `Tests/test_release_version_pinning.py` (6 pruebas) y
`Tests/test_release_type_banner.py` (5 pruebas, incluido el mecanismo real del registro),
el lint de Python y las dos revisiones de inclusión de archivos. No se ejecutó una
compilación real, instalación, recreación de base de datos ni operaciones de commit o
etiquetado en los repositorios del producto.

### Verificación final de la versión anticipada — 2026-11-07

El lanzador recreado pasó 21 pruebas visibles y el lint de Python. Las comprobaciones
reales mediante CMD para las modalidades privada y pública anticipan **1.92.3**
en ambas ediciones, sin exigir una etiqueta en HEAD. Se probaron los emisores reales,
etiquetas anteriores, prioridad del entorno, sobrescritura explícita, metadatos,
consulta sin escritura, procesos paralelos de prueba, fallos parciales y archivos ZIP.
Evidencia: `C:\Development\XAIHT\Tlachihuani\artifacts\verification\combined-builder-final-20261107\console.log`.
Esta verificación no ejecutó compilaciones completas de las aplicaciones congeladas.

### Recuperación de dependencias — 2026-11-08

Un fallo de DNS o del índice de paquetes no debe llevar la compilación a la
limpieza antigua de NumPy ni a `pip --user` en el Python de la máquina. Ahora
`build_env.py` se detiene antes de esas operaciones si no existe un entorno
aislado válido; las cachés aisladas sanas siguen siendo reutilizables. Las
compilaciones individuales usan `Temp/build-env` dentro de la aplicación. El
lanzador conjunto asigna `.build-cache/<edición>/python-envs` bajo la carpeta
de distribuciones. Ninguna ubicación predeterminada crea una caché nueva en
el perfil de Windows del usuario.

### Compilaciones completas privadas y públicas — 2026-11-08

Pasaron las cuatro compilaciones reales: inglés y español privados, seguidos de
inglés y español públicos; cada pareja se compiló en paralelo en consolas visibles
verificadas. Los cuatro ejecutables extraídos de sus ZIP finales informan
**1.92.3** y la modalidad Privada/Pública correcta. Los ZIP y sus archivos SHA-256
están bajo `C:\Development\XAIHT\Tlamatinis-Releases\<edición>\Private\2026-11-08_00-25`
y `...\<edición>\Public\2026-11-08_00-56`.

Pasaron la integridad de los paquetes, las auditorías de datos públicos, las
comprobaciones del runtime congelado, 26 pruebas de aislamiento y el lint específico.
Evidencia y nombres completos:
`C:\Development\XAIHT\Tlachihuani\artifacts\verification\complete-builds-20261107\VALIDATION.md`.
Se verificaron compilaciones y ejecutables empaquetados; esto no certifica una
instalación limpia ni pruebas de chat/modelo en vivo. No se hicieron commits,
etiquetas ni pushes.
