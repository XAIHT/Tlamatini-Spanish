<!-- Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1 -->
# Reproducción de voz y entrega al sistema

> Última versión publicada: **[v1.93.5](changes/2026-11-12-v1.93.5.md)**.

En **Config → Voz**, elige leer las respuestas, anunciar la finalización o
permanecer en silencio. Cubrir, minimizar o quitar el foco al navegador no
pausa deliberadamente la voz. El chat y la narración del editor y de la terminal
comparten una cola.

Si el navegador no consigue iniciar o terminar un fragmento, lo reintenta y
puede entregar el texto restante a la voz de Windows del equipo que ejecuta
Tlamatini. Cerrar o recargar la página durante una lectura normal del chat
también intenta esa entrega. Si termina una respuesta sin ninguna página de
chat abierta para la cuenta, el sistema lee la respuesta o anuncia que terminó
según el último modo de voz comunicado por esa cuenta. Tlamatini debe continuar
en ejecución.

## Controles y requisitos

- **Silencio**, volumen cero y la escucha del micrófono suprimen la voz. Escape
  la detiene salvo que un diálogo haya usado esa tecla para cerrarse. El avatar
  y la cancelación conservan sus controles de detención. Ctrl+Shift+M alterna
  el silencio.
- El navegador comunica la voz, idioma, velocidad, tono y volumen al sistema.
  Los ajustes y trabajos pertenecen a la cuenta autenticada. Las rutas de voz
  mantienen la autenticación y protección CSRF de la aplicación.
- La reproducción del sistema usa Windows System.Speech y el dispositivo de
  audio del equipo que ejecuta Tlamatini, no las bocinas de un navegador remoto.
  Necesita una voz femenina habilitada. La edición en español exige idioma
  español; no sustituye una voz inglesa. La edición inglesa puede usar otra voz
  femenina instalada si no encuentra coincidencia de idioma. Sin una voz
  compatible, la reproducción queda indisponible.
- El proceso auxiliar es interno y no abre otra consola. Envía sus diagnósticos
  al registro de la aplicación. Los ajustes y trabajos del sistema permanecen
  en memoria; no sobreviven al reinicio de la aplicación.
- Cada mensaje del sistema admite hasta 20,000 caracteres. Un fragmento fallido
  o interrumpido puede repetirse porque el navegador no sabe qué palabras llegó
  a pronunciar el motor. La entrega al cerrar la página es un intento: no
  garantiza audio ante un fallo del navegador, pérdida de red o cierre de la
  aplicación.

## Narración de las interacciones

La narración del editor y de la terminal comparte la cola y los controles de
silencio y detención. Conserva la cancelación de la acción, la propiedad de la
pestaña y la confirmación anterior a la escritura. Cerrar la página **no**
convierte esa narración en un mensaje independiente para la voz del sistema.
Silenciar o activar la escucha omite la narración; cancelarla explícitamente
detiene el paso. Sin voz disponible se ofrece continuar sin voz o detenerse. Consulta
[Editor en vivo y Terminater](interaction-settings.md).

## Implementación y verificación

`static/agent/js/voice_runtime.js` administra la cola y recuperación del
navegador; `host_voice.py`, los trabajos por cuenta y la voz de Windows;
`host_voice_views.py`, los ajustes, reproducción, estado y detención. El proceso
administrado invoca su propio PowerShell sin intérprete intermedio ni consola
visible. Los alias de pronunciación españoles se aplican antes de hablar.

Ejecuta las comprobaciones desde una consola de desarrollo visible y verificada:

```powershell
# Desde la raíz del repositorio:
node scripts/voice_runtime_cases.mjs
# Desde el directorio Django Tlamatini de esta edición:
python manage.py test agent.test_host_voice
```

Los casos de navegador usan un motor controlado para verificar recuperación,
orden, entrega al sistema y cancelación. Los casos Python cubren aislamiento
de cuentas, ajustes, ciclo del proceso y protección de rutas. No demuestran
audio audible en todos los dispositivos. El arnés de navegador real es
`.claude/skills/tlamatini-daily-chat-test/harness/voice_unstoppable_visible.py`;
úsalo con una voz real configurada y revisa su evidencia de escritorio.
