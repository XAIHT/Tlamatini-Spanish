# Atlas de arquitectura: regenerar `Tlamatini-Architecture.pdf`

> Última versión publicada: **[v1.97.0](../../docs/changes/2026-11-21-v1.97.0.md)**.

`Tlamatini-Architecture.pdf`, en la raíz del repositorio, es un atlas de
arquitectura en hojas A3. **Cada archivo de aplicación de su inventario declarado**
aparece dos veces: como tarjeta enlazada en su grupo arquitectónico y como entrada
en el índice, con una descripción obtenida del propio archivo. Los mapas de
ejecución, solicitudes, agentes, integración, interfaz, datos, compilación,
calidad y dependencias Python se reconstruyen a partir del código fuente.

La vista del Canvas explica el estado independiente de cada documento, las
instantáneas de contexto explícitas y el cambio de documento mediante Interactor.

## Regenerar después de un cambio

```
python scripts/architecture_atlas/build_architecture_pdf.py
```

El inventario incluye todas las rutas devueltas por `git ls-files`, incluido el
historial de migraciones. Durante el trabajo de documentación también incluye
estas rutas exactas del Canvas cuando existen como archivos nuevos no ignorados:

- `Tlamatini/agent/canvas_documents_context.py`
- `Tlamatini/agent/static/agent/css/canvas_tabs.css`
- `Tlamatini/agent/static/agent/js/agent_page_canvas_tabs.js`

La portada y el informe indican cuántos archivos se agregaron. Una vez
versionados, aparecen una sola vez. Otros archivos sin seguimiento, cachés y
datos privados no se incluyen silenciosamente. El proceso no agrega archivos al
índice de Git, no hace commits y no modifica sus metadatos. La generación y la
verificación final usan el mismo inventario.

El comando realiza tres pasos:

1. `gen_architecture.py` escribe `Temp/architecture/Tlamatini-Architecture.tex`
   y `Temp/architecture/generator_report.txt` con la biblioteca estándar.
2. Una copia privada del agente **LaTeXer** compone el documento con `pdflatex`
   y escribe `Tlamatini-Architecture.pdf` en la raíz.
3. PyMuPDF verifica que el índice incluya todas las rutas inventariadas y que
   las hojas del atlas muestren todos los nombres de archivo.

Código de salida: `0`, terminado y verificado; `1`, fallo de composición; `2`,
un archivo no pudo ubicarse (revisa `generator_report.txt`); `3`, faltan archivos
en el PDF. `--output <ruta>` elige otro destino y `--skip-verify` omite el tercer
paso. Usa `TLAMATINI_REPO` para seleccionar otra copia del repositorio.

La nueva hoja del Canvas muestra `notes.md`, `main.py` y `manual.pdf` abiertos,
con sólo `notes.md` y `manual.pdf` seleccionados como contexto. Distingue la
conexión del navegador de los identificadores de documento, conserva el estado
modificado y explica confirmar, actualizar y retirar contexto. Amplía la hoja
existente del editor, que conserva el guardado nativo y la tutoría.

## Requisitos

- `git` disponible en PATH.
- Una distribución TeX, preferentemente **MiKTeX**. Puede descargar paquetes
  faltantes durante la primera ejecución.
- PyYAML y PyMuPDF, incluidos en `requirements.txt`.

## Si el generador termina con código 2

Una carpeta o tipo de archivo nuevo puede carecer de grupo. Agrega la regla a
`assign()` en `gen_architecture.py` y, si necesita un grupo nuevo, a `META` y
`ORDER`. Repite la generación. Los archivos intermedios quedan en `Temp/`; el
único resultado final que este comando reemplaza es el PDF.

## Regenerar la guía y la presentación complementarias

Desde la raíz de esta edición, ejecuta en la consola de desarrollo visible:

```powershell
python Tlamatini/agent/doc_generation/refresh_project_docs.py
```

Reescribe `tlamatini_app_summary.pdf` y
`Tlamatini_eXtended_Artificial_Intelligence_Humanly_Tempered.pptx`. Sus capítulos
compartidos mantienen alineado el comportamiento del Canvas de la versión
1.97.0. El dossier inventaría archivos versionados y todas las incorporaciones
no ignoradas; su alcance es más amplio que las tres incorporaciones explícitas
del atlas. Informes, inventarios e imágenes quedan en
`build/documentation_refresh`; los intermedios del atlas, en `Temp/architecture`.

Revisa todas las páginas y diapositivas después de generar. El dossier comprueba
límites de página y correspondencia del árbol PDF, además de geometría y texto
del PPTX. La verificación nativa requiere PowerPoint/COM; su ausencia se informa
como omitida, nunca como aprobada. Un renderizado adicional con otro motor sirve
de evidencia visual si se identifica el motor y se conserva esta limitación.

Parte de Tlamatini, creada por Angela López Mendoza.
