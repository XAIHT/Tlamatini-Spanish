# Porteo de Torrenter · 31 de octubre de 2026

> Última versión publicada: **[v1.92.4](../../docs/changes/2026-11-08-v1.92.4.md)**.

Solicitud de Angela, conservada para la bitácora de cambios:

> Now, deeply sweep every line changed in Tlamatini (english) and implement the corresponding changes in Tlamatini-Spanish *of course load all of the skills and every memory from Tlamatini-Spanish codebase in order to be sure you implement everything according to Tlamatini-Spanish design, so make a surgically GOD-LEVEL IMPLEMENTATION of Torrenter and everything related into Tlamatini-Spanish at 'c:\Development\XAIHT\Tlamatini-Spanish', go!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

La base inglesa de la edición es `1d13922ded76a1a9526e8a3edd2684f4a0785f02`.
La revisión de Torrenter corresponde al árbol de trabajo inglés sobre
`17844abcc01db1d475e5c0bdb44be1202cfbd361`. El parche cuyo SHA-256 figura en
`../BASE_INGLES.json` conserva las diferencias completas de los 46 archivos
de la función (incluidos los nuevos) contra la base. Los archivos de configuración
personal de los dos checkouts no forman parte de ese parche.

Para reconstruir el estado anterior, la referencia española inmediatamente anterior
al porteo es `f821866`. Para reconstruir el actual, aplica el parche sobre la base
inglesa y los pares exactos `en`/`es` de `../memoria/` a través de `portar.py`.
Así se conservan los cambios españoles de Talker, sus recursos de build y los
sufijos de caché de pronunciación y velocidad de escritura. La prueba de Exec Report
usa las etiquetas que ya presentaba la edición española.

## Verificación

Se aplicó la migración 0221 en una base de desarrollo aislada, se recopilaron los
archivos estáticos y se abrió **Fuentes de Torrenter** en Chrome. El tool
`chat_agent_torrenter` envió la descarga a una instancia real de Jobs con estado
temporal. El reintento devolvió el mismo ID de operación. El manifiesto confirmó
13,936 bytes y el SHA-256 del archivo publicado coincidió con el del peer local:
`9139336560ce669bc16c5ea9114cc10ca0c0964d0dee90c9a836fd232910658d`.
La prueba usó el canal de control de desarrollo de Jobs; los servicios de Windows
instalados siguieron detenidos.

Con el mismo job se probaron las acciones `pause`, `resume`, `stop` y `start`.
Jobs rechazó el borrado de contenido sin aprobación en XT. Al eliminar el registro,
el archivo publicado siguió en disco.

Pasaron 90 pruebas de regresión de Django y ESLint en los cinco módulos de
JavaScript del porteo. El catálogo generado coincidió con los 87 tipos de agent
y conservó los campos de voz propios de Talker. En un ejecutable de prueba de
PyInstaller, el validador de Torrenter devolvió el mensaje esperado en español,
se cargaron `win32cred` y `win32crypt` y DPAPI recuperó los bytes cifrados.
