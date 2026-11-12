<!-- Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1 -->
# Consultar los directorios disponibles

> Última versión publicada: **[v1.93.5](changes/2026-11-12-v1.93.5.md)**.

Pregunta **«Muéstrame los directorios disponibles»** o
**«Show me the available directories»**. Tlamatini responde con las raíces
permitidas por el control de rutas activo de esta instancia. No necesitas
indicar una ruta para pedir esa lista.

Una pregunta completa dedicada únicamente a ese inventario se responde
directamente, sin clasificar la intención con un modelo ni explorar el disco.
La lista usa la misma instantánea resuelta que aplica los permisos actuales;
no vuelve a leer una configuración modificada que todavía no esté en vigor.
Elimina raíces repetidas, escapa las rutas para mostrarlas e informa
explícitamente si la lista está vacía.

La respuesta no concede acceso, no demuestra que exista el directorio ni omite
los permisos de Windows. Una pregunta con otra acción o una ruta explícita
continúa por el procesamiento y las comprobaciones habituales. Tras modificar
las rutas permitidas, sigue el procedimiento normal de recarga o reconexión de
la aplicación antes de esperar cambios en la lista activa.

Implementación: `agent/rag/directory_listing.py`, invocada desde
`agent/rag/interface.py`. Cobertura: `agent.test_available_directories`
(preguntas en ambos idiomas, exclusión de solicitudes mixtas, escape, listas
vacías y coherencia con la instantánea activa). Consulta la
[configuración de modelos](model_configuration.md) para las rutas que usan modelos.
