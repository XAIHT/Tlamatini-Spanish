<!-- Tlamatini Author Banner — Angela López Mendoza · @angelahack1 -->
# Explicar la selección del canvas — 12 de noviembre de 2026

El botón explica el texto seleccionado exacto, incluidos los cambios sin guardar,
con cualquier combinación de casillas del chat. Primero se corrigió y verificó
la edición inglesa; después se aplicó el mismo comportamiento en español.

## Causa y corrección

El registro instalado de C:\Tlamatini\tlamatini.log muestra que una lectura de
Interactor excedió el límite de 24,000 caracteres de los resultados de herramientas.
El botón anterior enviaba una petición genérica de chat que leía todo el documento
de unos 46,855 caracteres. Además, exigía Multi-Turn y Editor en vivo, rechazaba
un borrador existente y dependía de una cadena RAG que podía estar reconstruyéndose
tras cambiar las casillas. La selección nunca llegaba al modelo al fallar esa lectura.

Ahora se capturan todos los rangos seleccionados al pulsar el botón, o el archivo
completo si no hay selección. Una petición autenticada y validada canvas-explain
envía esos fragmentos exactos al modelo configurado sin herramientas, contexto
cargado, historial, internet, compactación ni instrucciones de automodificación.
Se conservan la cancelación, recuperación, entrega al chat y medición de contexto
y uso habituales. Los bloques de código de la explicación se muestran sin crear
registros de programas o fragmentos. Se conservan el borrador, la selección,
el archivo y los ajustes de las casillas.

El límite es de 262,144 unidades UTF-16 en 64 rangos, sujeto a la capacidad real
del modelo. El resto del archivo no consume ese límite. No se recorta texto en
silencio. Las lecturas de tutoría de Interactor conservan su contrato y límites.

## Verificación desde el código fuente

- 58 pruebas Django aprobadas en cada edición: 32 combinaciones de opciones del
  backend, Unicode, varios rangos, selección pequeña dentro de cinco millones de
  caracteres, entradas inválidas, independencia de RAG y persistencia de solo lectura.
- Lint de JavaScript y Python aprobado. Se regeneraron ambos paquetes del editor,
  con 40 dependencias licenciadas cada uno. Se verificaron los bytes de 459 archivos
  estáticos en cada edición.
- Chrome visible comprobó las 256 combinaciones de las ocho casillas del chat en
  cada edición, con Editor en vivo en pausa y un borrador existente. Once puntos
  de verificación aprobados por edición, incluido el envío del archivo completo
  cuando no hay selección.
- El modelo real configurado deepseek-v4.1-flash:cloud explicó el valor sin guardar
  1536 de un archivo de 52,049 unidades cuyo archivo de prueba guardado conservaba
  1280. Las respuestas inglesa y española usaron el valor sin guardar; cero
  herramientas y RAG marcado deliberadamente como no listo. La última llamada
  inglesa usó 370 tokens de entrada; la española, 419.
- La prueba del navegador captura el transporte de chat para recorrer las casillas
  de forma determinista. Después pasa la petición capturada por el consumidor y
  modelo de producción y entrega su respuesta al renderizador normal del chat.
  Usa cuentas y bases aisladas y Chrome real en primer plano, sin modo headless.
  Evidencia: Temp/canvas-explanation-visible/final-result.json y run-*/ en cada
  repositorio. Última ejecución inglesa: 7; española: 1.
- Una prueba española existente aún buscaba la etiqueta inglesa del enlace para
  cargar programas. Su aserción ahora usa la etiqueta española existente; no
  cambió el comportamiento de los enlaces del producto.

Estos resultados corresponden a ejecuciones desde el código fuente. No se
recompilaron ni reemplazaron los ejecutables instalados, ni se cambió la versión,
la configuración del usuario o los mecanismos de respaldo/restauración de la base.
Las listas de módulos del ejecutable y del código fuente distribuido incluyen el
nuevo servicio.
