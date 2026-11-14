# Corrección de dependencias de migración · 13 de noviembre de 2026

La versión permanece en **1.93.5**. El compilador combinado anticipó correctamente
ese número para ambas ediciones. English terminó; Spanish falló al ejecutar
`migrate` en el ejecutable porque `0224_remote_controller` dependía de
`0223_create_superuser_console_handoff`, que solo existe en la edición inglesa.

Spanish ahora utiliza su predecesor real, `0227_create_superuser_console_handoff`.
English conserva su dependencia correcta. Se mantienen las identidades de las
migraciones: no hay migración ficticia, renumeración, reescritura del historial ni
cambios en respaldos o restauraciones.

## Detección temprana

Los compiladores privado/público y la entrada directa de ambas ediciones utilizan
`build_runtime_assets.validate_migration_dependencies`. La función lee la sintaxis
sin importar la aplicación ni conectarse a una base de datos. Informa los
predecesores locales literales ausentes antes de modificar archivos. Django sigue
verificando las dependencias externas o dinámicas. El compilador combinado revisa
ambas ediciones antes de iniciar cualquiera; forzar una versión no omite un archivo
de migración ausente. También informa el error de una edición inmediatamente,
mientras permite que la otra termine y conserve su ZIP correcto.

## Verificación

Ejecuta por separado `Tests/test_build_migrations.py`, `Tests/test_migration_graph.py`
y `Tests/test_release_version_pinning.py` con el entorno preparado de Python/Django
en una consola visible y verificada. Ejecuta `BuildTlamatinis.Tests.py` con Python
3.12 del sistema desde el directorio padre. Los archivos temporales quedan en
directorios de la aplicación, nunca dentro del perfil de Windows.

La prueba de Django carga el grafo real y aplica las migraciones reales a bases
SQLite nuevas y aisladas. Comprueba el esquema inicial, la actualización desde el
predecesor, los modelos de perfil/revocación y la reversión/reaplicación conservando
una cuenta de prueba y su prompt personalizado. No ejecuta los inicializadores de
producción ni utiliza las bases habituales de ninguna edición.

La prueba del compilador utiliza ZIP de prueba explícitos para concurrencia,
fallos y archivado; no son aplicaciones compiladas. La inclusión en ejecución y
en el código para automodificación se verifica por separado. Esta verificación
no incluye recompilar ejecutables completos, instalar, etiquetar, hacer commit
ni publicar.

### Resultados observados

- Pasaron 67 pruebas de regresión entre ambas ediciones y el compilador combinado:
  26 comprobaciones de fuentes de migración, 6 pruebas reales de migraciones con
  Django, 12 de fijación de versión y 23 del compilador combinado.
- Django cargó 242 nodos en inglés y 246 en español. Ambos grafos tienen el nodo
  final esperado de Remote-Controller y ninguna rama de agent en conflicto.
- Las invocaciones reales privada y pública de `BuildTlamatinis.cmd --check`
  informan **1.93.5** en ambas ediciones y validan 224/228 archivos de migración local.
- Pasó el lint de todos los archivos Python modificados. La generación del código
  para automodificación y las revisiones de inclusión para autoactualización
  pasaron sin hallazgos en ambas ediciones. Los avisos sobre la galería omitida y
  la regeneración de archivos estáticos/salidas de compilación corresponden a
  políticas existentes, no a fuentes de migración ausentes.
- La migración inglesa permanece idéntica byte por byte. La corrección española
  no modifica bases de datos reales, credenciales ni mecanismos de respaldo/restauración.

El fallo original se reprodujo y queda cubierto por estas comprobaciones. Los
ejecutables e instaladores nuevos todavía requieren una compilación completa
normal; estos resultados no certifican un ZIP que no se ha generado.
