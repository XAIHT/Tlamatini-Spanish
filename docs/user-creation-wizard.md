<!-- Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1 -->
# Crear una cuenta administrativa en Tlamatini-Spanish

> Última versión publicada: **[v1.92.4](changes/2026-11-08-v1.92.4.md)**.

El asistente integrado abre la consola real de cuentas de Django de esta
instancia. Devuelve el control al chat mientras introduces los datos. La
contraseña se escribe exclusivamente en la consola; un lanzamiento aceptado
no demuestra que la cuenta ya exista.

## Uso desde el catálogo

1. Abre **Catálogo de prompts**, elige la primera tarjeta de creación de cuentas
   y escribe el nombre deseado. Mantén Multi-Turn, Exec report y Paso a paso.
2. Envía la tarjeta. Con el nombre disponible, el asistente abre la consola en
   el mismo turno. Si falta el nombre o es inválido, lo solicita y admite tu
   corrección sin enviar ese intercambio a un modelo.
3. Introduce el nombre deseado, el correo opcional, la contraseña y su repetición
   en la consola. Se crea un superusuario administrativo, no una cuenta ordinaria
   con permisos restringidos.
4. Cuando Django confirme realmente la creación, responde **HECHO**. Usa **ERROR**
   con el error sin secretos si falla, o **SIN VENTANA** si la consola no es
   visible. También se aceptan DONE y NOWINDOW por compatibilidad.
5. HECHO comprueba en la base de datos de esta instancia que el superusuario
   indicado está activo y fue creado durante este asistente. Una vez confirmado,
   cierra sesión y entra con esa cuenta en la misma dirección del navegador.
   No es necesario reiniciar el servidor.

La tarjeta predeterminada no espera a que esté listo el modelo, incluso cuando
un cambio de las opciones del chat provoca su reconstrucción. El chat ordinario
conserva sus comprobaciones normales de disponibilidad del modelo. El asistente
no pide a un modelo generar órdenes de shell, no ejecuta Image-Interpreter,
no captura la consola de credenciales y no consulta agentes mientras escribes.

## Permisos, conversación y procesos

Se requiere una cuenta con sesión activa. **Ask Execs** sigue solicitando
permiso antes del lanzamiento: la denegación, la ausencia del mecanismo de
aprobación o la cancelación impiden abrir otra consola. Se vuelve a comprobar
la cancelación después de recibir la aprobación.

La respuesta de nombre o estado debe continuar la respuesta inmediatamente
anterior de este asistente. Una conversación diferente no reactiva una solicitud
vieja. Un nombre inválido se vuelve a solicitar. La confirmación de creación
retira este contexto de conversación, pero conserva el identificador del proceso
vivo que pertenece al asistente para protegerlo del recolector de huérfanos y
del supervisor de comandos hasta que cierre la consola.

Reenviar la tarjeta mientras esa consola siga abierta reutiliza la misma.
SIN VENTANA intenta traerla al frente sin crear otra. Si ya se cerró, reenviar
la tarjeta es un reintento explícito. ERROR no declara éxito ni repite
automáticamente la creación. La consola permanece abierta después del comando
para que puedas leer el resultado; pulsa Intro para cerrarla.

## Selección de la instancia y de la base de datos

El lanzador utiliza el ejecutable del proceso actual y la ruta absoluta de su
proyecto Django. No selecciona otro entorno mediante PATH, una búsqueda global,
una variable temporal heredada ni una orden proporcionada en el chat.

| Modo | Comando integrado |
| --- | --- |
| Desarrollo | Python exacto de la instancia + ruta absoluta a `Tlamatini/manage.py createuserconsole` |
| Instalado | `Tlamatini-Spanish.exe createuserconsole` de esta instalación |

`createuserconsole` es una subclase específica del comando real
`createsuperuser` de Django. Conserva las comprobaciones de modelos y
migraciones, nombres duplicados y validación de contraseñas. Las comprobaciones
de direcciones web ajenas a la creación de cuentas no retrasan la entrada de
datos. El nombre y la contraseña nunca se interpolan como código de shell.

La consola utiliza la base de datos de esta edición y los directorios de la
aplicación. Su inicio no trunca el `tlamatini.log` del servidor y los datos
privados introducidos no se copian a ese registro. El asistente no crea archivos
temporales bajo un perfil de usuario de Windows.

## Compatibilidad del catálogo y avisos locales

La migración **0227_create_superuser_console_handoff** reemplaza sólo la tarjeta
predeterminada anterior conocida. Conserva las tarjetas personalizadas y sus
metadatos. El controlador integrado también reconoce las tarjetas históricas
completas conocidas cuando se ha sustituido únicamente el nombre. Los ejemplos
citados, las explicaciones y las demás instrucciones personalizadas permanecen
como solicitudes normales; no autorizan por sí mismos abrir una consola.

El asistente integrado comunica la espera, los errores y la confirmación
**directamente en el chat**. No invoca Notifier, no reproduce sus sonidos ni
muestra sus antiguos diálogos de puntos de control. La migración 0219 introdujo
esos diálogos para el flujo anterior con Executer/Notifier. Esa redacción
histórica no describe el comportamiento de la ruta integrada actual. Las
solicitudes personalizadas que invoquen Notifier expresamente conservan las
reglas de sus herramientas y permisos.

## Verificación visible de fuentes — 2026-11-09

Las siguientes ejecuciones utilizaron navegadores reales, consolas reales de
Django y bases de datos aisladas de prueba de fuentes. Crearon cuentas
interactivamente y comprobaron su autenticación en la página real de inicio de
sesión. No sustituyeron respuestas de herramientas ni inyectaron cookies de
sesión.

| Edición | Cuentas reales creadas y autenticadas | Comprobaciones aprobadas | Envío → campo de nombre legible | Envío → primer plano real |
| --- | --- | --- | --- | --- |
| Inglés | 10/10 | 130/130 | 2,351–3,961 segundos | 2,356–3,966 segundos |
| Español | 10/10 | 130/130 | 2,241–3,153 segundos | 2,245–3,156 segundos |

Los grupos finales verificaron DONE/HECHO contra cada cuenta recién persistida
y después la autenticaron mediante el formulario real de acceso. Las 20 consolas
ya estaban al frente antes de cualquier solicitud de enfoque del verificador;
ninguna necesitó esa ayuda. Las comprobaciones emparejadas del asistente
tuvieron **0 diferencias de aprobación o fallo en 130 comparaciones**.

El [informe fechado de verificación](user-creation-verification-2026-11-09.md)
incluye los tiempos individuales, la distinción entre primer plano automático
y asistido, pruebas unitarias, lint, intentos fallidos anteriores y límites
exactos. Evidencia final:

- `C:\Development\XAIHT\Tlamatini-Spanish\Temp\wizard-repair-20261109\visible-en-20261109-161020\result.json`
- `C:\Development\XAIHT\Tlamatini-Spanish\Temp\wizard-repair-20261109\visible-es-20261109-160742\result.json`

Las 20 cuentas finales son distintas de los grupos anteriores de QA y del
operador de prueba; no representan el total de cuentas de esas bases.
Los resultados corresponden a instancias de fuentes, no a un ejecutable
congelado ni a un paquete instalado. Se mide desde el envío en el navegador,
no desde un lanzamiento aceptado. Los casos unitarios con operaciones del
sistema simuladas no cuentan como creaciones reales adicionales.

## Actualización de una instalación existente

Modificar las fuentes o esta guía no actualiza un ejecutable congelado.
Reconstruye e instala un paquete que incluya los módulos y las migraciones
corregidos antes de comprobar esa instalación. Mantén su evidencia separada de
las pruebas de fuentes anteriores. Esta verificación enfocada del asistente de
cuentas no acredita todos los demás prompts del catálogo.

Antecedente conservado: el 2026-10-22, la corrección de las reglas de intención
superó 179 pruebas enfocadas sin crear una cuenta real ni enviar mensajes
externos. Ese resultado fechado no constituye evidencia del nuevo asistente
integrado.
