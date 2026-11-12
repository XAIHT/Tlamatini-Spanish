<!-- Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1 -->
# Executer: devolver el resultado al terminar el script lanzador

La ejecución instalada `executer_149_fae77897` comenzó a las 14:21:47.846
del 12 de noviembre de 2026. Su comando usó `start ... cmd /c` para abrir
el cubo durante 90 segundos, esperó unos tres segundos y ejecutó `tasklist`.
La lista mostraba el cubo vivo, pero Executer no entregó esa salida ya
producida hasta las 14:23:22.306.

`subprocess.run(capture_output=True)` esperaba el fin de los pipes de salida.
El shell hijo conservaba los handles heredados después de terminar el batch
exterior. Por eso la siguiente inspección podía llegar cuando la aplicación
ya se había cerrado.

El modo bloqueante ahora captura stdout y stderr en archivos únicos dentro
del directorio aislado de ejecución y espera al proceso del script. Lee una
instantánea de tamaño acotado mediante handles independientes, sin cambiar
la posición de escritura de los hijos. Registra y conserva las capturas.
Los comandos directos siguen bloqueando; los hijos abiertos con `start`
pueden continuar. No se agregó un límite de ciclos, una decisión de progreso
basada en modelos ni una regla nueva de prompt.

## Reproducción con los mismos recursos

Se llamaron los tools reales `executer`, `windower` y `shoter` mediante el
servidor MCP stdio de cada edición. El código original de Executer coincidía
byte por byte con el código inglés anterior al cambio. No se recompiló ni editó:

`C:\Tlamatini-Spanish\applications\dxr_cube_cuda_rust\target\release\dxr_cube_cuda_rust.exe`

SHA-256: `c6e5071412d2477c51d6af7aa184fe064ca85db51fc402487afe27e60498a558`.
El shader DXIL y el PTX de CUDA están integrados en ese ejecutable.

| Reproducción | Script exterior terminado al observar | Executer terminado al observar | Cubo vivo al recibir el resultado |
|---|---:|---:|---|
| Código original | 5,03 s | 100,50 s | No |
| Corrección inglesa | 5,05 s | 5,05 s | Sí |
| Corrección española | 5,06 s | 5,06 s | Sí |

Los tiempos son observaciones muestreadas. Las tres ejecuciones terminaron
naturalmente con código 0 y registraron los cuadros renderizados. Se conservaron
el programa, el argumento de 90 segundos y la estructura `start`, `cmd /c`,
ping y tasklist. Se omitió la terminación masiva por nombre, se utilizó otro
archivo de salida y se agregó un marcador del final del script exterior.
Los registros originales de la aplicación se conservaron.

`agent.test_executer_capture` verifica START, START /B con streams compartidos,
salida tardía, espera de hijos directos y códigos de error con procesos Windows
reales y barreras explícitas. Usa almacenamiento temporal de la aplicación
y handles nativos cuya identidad se verifica para limpiar las pruebas.

El 12 de noviembre de 2026 pasaron las 65 pruebas seleccionadas de captura,
comandos, ventanas, limpieza y watchdog en cada edición. Los archivos Python
modificados también pasaron las comprobaciones de errores fatales de Ruff;
el diff pasó la comprobación de espacios en blanco.

Evidencia: `C:\Development\XAIHT\scratch\cube-loop-20261112`.
Son resultados del código de desarrollo, no de un paquete instalado nuevo.
La falta posterior de entrega de la respuesta final en el registro original
es una observación separada sin resolver: no se conservó el borrador completo
ni una traza viva que permita identificar su causa.
