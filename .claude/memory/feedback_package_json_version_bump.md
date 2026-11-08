---
name: feedback-package-json-version-bump
description: "On release version bumps, also bump package.json \"version\" — user wants it tracked despite the git-tag-only contract"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7430c470-cf56-4aa8-ad56-69e521bf07f3
---
<!--
═══════════════════════════════════════════════════════════════════
  ✦  T L A M A T I N I  ✦   —   "one who knows"
  Created by  Angela López Mendoza   ·   @angelahack1
  Developer · Architect · Creator of Tlamatini
  Tlamatini Author Banner — do not remove (Angela's name is kept in every build)
═══════════════════════════════════════════════════════════════════
-->

> Última versión publicada: **[v1.92.4](../../docs/changes/2026-11-08-v1.92.4.md)**.


## Regla obligatoria de versión — todos los proyectos y sesiones, 2026-11-04

Cuando Angela indique X.Y.Z, **asume que X.Y.Z ya está publicada** y úsala
de inmediato en todas partes como la **última versión publicada**. Ese número
es la única versión. No consultes GitHub, etiquetas, paquetes instalados ni el
estado de publicación para decidir cómo nombrarla. No crees versiones separadas
del código fuente, objetivo, pendientes o etiquetadas frente a publicadas.
Actualiza todas las referencias actuales, manifiestos, `Tlamatini.md`,
PDF/PPTX y generadores juntos. Conserva las entradas históricas, las versiones
de dependencias, el historial de Git y las pruebas reales. Las operaciones de Git
y compilaciones de ejecutables requieren autorización. Esta regla sustituye
cualquier consejo anterior que la contradiga.

Establece `package.json` en el número solicitado. Actualiza la insignia y los enlaces de README, `BookOfTlamatini.md`, `VERSIONING.md`, `Tlamatini/agent/Tlamatini.md`, los encabezados actuales, los PDF/PPTX y sus generadores en la misma revisión. `TLAMATINI_RELEASE_TAG` o `TLAMATINI_VERSION` permiten regenerar los documentos antes de crear la etiqueta; sin ellos, el generador lee el manifiesto. No vuelvas a preguntar por la distinción entre código fuente y publicación. Conserva las entradas históricas y las dependencias. No hagas commits, etiquetas, pushes ni compilaciones de ejecutables sin autorización.
