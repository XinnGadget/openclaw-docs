---
read_when:
    - Configurar Matrix en OpenClaw
    - Configurar E2EE y verificación de Matrix
summary: Estado de compatibilidad de Matrix, configuración y ejemplos de configuración
title: Matrix
x-i18n:
    generated_at: "2026-04-06T05:14:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 06f833bf0ede81bad69f140994c32e8cc5d1635764f95fc5db4fc5dc25f2b85e
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix es el plugin de canal integrado de Matrix para OpenClaw.
Usa el `matrix-js-sdk` oficial y admite MD, salas, hilos, multimedia, reacciones, encuestas, ubicación y E2EE.

## Plugin integrado

Matrix se incluye como plugin integrado en las versiones actuales de OpenClaw, por lo que las compilaciones empaquetadas normales no necesitan una instalación aparte.

Si usas una compilación antigua o una instalación personalizada que excluye Matrix, instálalo manualmente:

Instalar desde npm:

```bash
openclaw plugins install @openclaw/matrix
```

Instalar desde una copia local:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

Consulta [Plugins](/es/tools/plugin) para ver el comportamiento de los plugins y las reglas de instalación.

## Configuración

1. Asegúrate de que el plugin de Matrix esté disponible.
   - Las versiones empaquetadas actuales de OpenClaw ya lo incluyen.
   - Las instalaciones antiguas o personalizadas pueden añadirlo manualmente con los comandos anteriores.
2. Crea una cuenta de Matrix en tu homeserver.
3. Configura `channels.matrix` con una de estas opciones:
   - `homeserver` + `accessToken`, o
   - `homeserver` + `userId` + `password`.
4. Reinicia el gateway.
5. Inicia un MD con el bot o invítalo a una sala.

Rutas de configuración interactiva:

```bash
openclaw channels add
openclaw configure --section channels
```

Lo que realmente pregunta el asistente de Matrix:

- URL del homeserver
- método de autenticación: token de acceso o contraseña
- ID de usuario solo cuando eliges autenticación por contraseña
- nombre opcional del dispositivo
- si se debe habilitar E2EE
- si se debe configurar ahora el acceso a salas de Matrix

Comportamiento del asistente que importa:

- Si las variables de entorno de autenticación de Matrix ya existen para la cuenta seleccionada, y esa cuenta todavía no tiene autenticación guardada en la configuración, el asistente ofrece un atajo por variable de entorno y solo escribe `enabled: true` para esa cuenta.
- Cuando añades otra cuenta de Matrix de forma interactiva, el nombre de cuenta introducido se normaliza en el ID de cuenta usado en la configuración y en las variables de entorno. Por ejemplo, `Ops Bot` se convierte en `ops-bot`.
- Las solicitudes de lista de permitidos para MD aceptan inmediatamente valores completos `@user:server`. Los nombres para mostrar solo funcionan cuando la búsqueda en el directorio en vivo encuentra una coincidencia exacta; en caso contrario, el asistente te pide que vuelvas a intentarlo con un ID completo de Matrix.
- Las solicitudes de lista de permitidos de salas aceptan directamente IDs y alias de sala. También pueden resolver en vivo nombres de salas unidas, pero los nombres sin resolver solo se conservan tal como se escribieron durante la configuración y luego se ignoran en la resolución de lista de permitidos en tiempo de ejecución. Usa preferiblemente `!room:server` o `#alias:server`.
- La identidad de sala/sesión en tiempo de ejecución usa el ID estable de la sala de Matrix. Los alias declarados por la sala solo se usan como entradas de búsqueda, no como clave de sesión a largo plazo ni como identidad estable de grupo.
- Para resolver nombres de salas antes de guardarlos, usa `openclaw channels resolve --channel matrix "Project Room"`.

Configuración mínima basada en token:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      dm: { policy: "pairing" },
    },
  },
}
```

Configuración basada en contraseña (el token se almacena en caché después de iniciar sesión):

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: allowlist secret
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

Matrix almacena las credenciales en caché en `~/.openclaw/credentials/matrix/`.
La cuenta predeterminada usa `credentials.json`; las cuentas con nombre usan `credentials-<account>.json`.
Cuando allí existen credenciales en caché, OpenClaw trata Matrix como configurado para configuración inicial, doctor y detección del estado del canal, aunque la autenticación actual no esté establecida directamente en la configuración.

Equivalentes de variables de entorno (usados cuando la clave de configuración no está establecida):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

Para cuentas no predeterminadas, usa variables de entorno con ámbito de cuenta:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

Ejemplo para la cuenta `ops`:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

Para el ID de cuenta normalizado `ops-bot`, usa:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix escapa la puntuación en los IDs de cuenta para evitar colisiones en las variables de entorno con ámbito.
Por ejemplo, `-` se convierte en `_X2D_`, por lo que `ops-prod` se asigna a `MATRIX_OPS_X2D_PROD_*`.

El asistente interactivo solo ofrece el atajo de variables de entorno cuando esas variables de autenticación ya están presentes y la cuenta seleccionada todavía no tiene autenticación de Matrix guardada en la configuración.

## Ejemplo de configuración

Esta es una configuración base práctica con emparejamiento de MD, lista de permitidos de salas y E2EE habilitado:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,

      dm: {
        policy: "pairing",
        sessionScope: "per-room",
        threadReplies: "off",
      },

      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },

      autoJoin: "allowlist",
      autoJoinAllowlist: ["!roomid:example.org"],
      threadReplies: "inbound",
      replyToMode: "off",
      streaming: "partial",
    },
  },
}
```

`autoJoin` se aplica a las invitaciones de Matrix en general, no solo a invitaciones de salas o grupos.
Eso incluye invitaciones nuevas de estilo MD. En el momento de la invitación, OpenClaw no sabe de forma fiable si la
sala invitada terminará tratándose como un MD o como un grupo, así que todas las invitaciones pasan primero por la misma
decisión de `autoJoin`. `dm.policy` sigue aplicándose después de que el bot se haya unido y la sala se
clasifique como MD, por lo que `autoJoin` controla el comportamiento de unión mientras que `dm.policy` controla el comportamiento
de respuesta y acceso.

## Vistas previas de streaming

El streaming de respuestas de Matrix es opcional.

Establece `channels.matrix.streaming` en `"partial"` cuando quieras que OpenClaw envíe una única vista previa en vivo
de la respuesta, edite esa vista previa en el mismo lugar mientras el modelo genera texto y luego la finalice cuando la
respuesta haya terminado:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` es el valor predeterminado. OpenClaw espera la respuesta final y la envía una sola vez.
- `streaming: "partial"` crea un mensaje de vista previa editable para el bloque actual del asistente usando mensajes de texto normales de Matrix. Esto conserva el comportamiento heredado de Matrix de notificar primero por vista previa, por lo que los clientes estándar pueden notificar con el primer texto de vista previa transmitido en lugar del bloque terminado.
- `streaming: "quiet"` crea un aviso de vista previa silencioso y editable para el bloque actual del asistente. Úsalo solo cuando también configures reglas push del destinatario para las ediciones finalizadas de la vista previa.
- `blockStreaming: true` habilita mensajes de progreso de Matrix separados. Con el streaming de vista previa habilitado, Matrix conserva el borrador en vivo del bloque actual y mantiene los bloques completados como mensajes separados.
- Cuando la vista previa está activada y `blockStreaming` está desactivado, Matrix edita el borrador en vivo en el mismo lugar y finaliza ese mismo evento cuando termina el bloque o el turno.
- Si la vista previa deja de caber en un solo evento de Matrix, OpenClaw detiene el streaming de vista previa y vuelve a la entrega final normal.
- Las respuestas con multimedia siguen enviando adjuntos normalmente. Si una vista previa obsoleta ya no puede reutilizarse de forma segura, OpenClaw la redacta antes de enviar la respuesta multimedia final.
- Las ediciones de vista previa cuestan llamadas adicionales a la API de Matrix. Deja el streaming desactivado si quieres el comportamiento más conservador respecto a límites de tasa.

`blockStreaming` no habilita por sí solo las vistas previas de borrador.
Usa `streaming: "partial"` o `streaming: "quiet"` para las ediciones de vista previa; luego añade `blockStreaming: true` solo si también quieres que los bloques completados del asistente permanezcan visibles como mensajes de progreso separados.

Si necesitas notificaciones estándar de Matrix sin reglas push personalizadas, usa `streaming: "partial"` para el comportamiento de vista previa primero o deja `streaming` desactivado para entrega solo final. Con `streaming: "off"`:

- `blockStreaming: true` envía cada bloque terminado como un mensaje normal de Matrix con notificación.
- `blockStreaming: false` envía solo la respuesta final completada como un mensaje normal de Matrix con notificación.

### Reglas push autoalojadas para vistas previas silenciosas finalizadas

Si ejecutas tu propia infraestructura de Matrix y quieres que las vistas previas silenciosas notifiquen solo cuando un bloque o la
respuesta final haya terminado, establece `streaming: "quiet"` y añade una regla push por usuario para las ediciones finalizadas de la vista previa.

Normalmente esto es una configuración del usuario destinatario, no un cambio global de configuración del homeserver:

Mapa rápido antes de empezar:

- usuario destinatario = la persona que debe recibir la notificación
- usuario bot = la cuenta de Matrix de OpenClaw que envía la respuesta
- usa el token de acceso del usuario destinatario para las llamadas a la API de abajo
- haz coincidir `sender` en la regla push con el MXID completo del usuario bot

1. Configura OpenClaw para usar vistas previas silenciosas:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. Asegúrate de que la cuenta destinataria ya reciba notificaciones push normales de Matrix. Las reglas de vista previa silenciosa
   solo funcionan si ese usuario ya tiene pushers/dispositivos funcionando.

3. Obtén el token de acceso del usuario destinatario.
   - Usa el token del usuario que recibe, no el token del bot.
   - Reutilizar un token de una sesión existente del cliente suele ser lo más fácil.
   - Si necesitas emitir un token nuevo, puedes iniciar sesión mediante la API estándar Client-Server de Matrix:

```bash
curl -sS -X POST \
  "https://matrix.example.org/_matrix/client/v3/login" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "m.login.password",
    "identifier": {
      "type": "m.id.user",
      "user": "@alice:example.org"
    },
    "password": "REDACTED"
  }'
```

4. Verifica que la cuenta destinataria ya tenga pushers:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

Si esto no devuelve pushers/dispositivos activos, corrige primero las notificaciones normales de Matrix antes de añadir la
regla de OpenClaw de abajo.

OpenClaw marca las ediciones finalizadas de vista previa de solo texto con:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. Crea una regla push de anulación para cada cuenta destinataria que deba recibir estas notificaciones:

```bash
curl -sS -X PUT \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname" \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "conditions": [
      { "kind": "event_match", "key": "type", "pattern": "m.room.message" },
      {
        "kind": "event_property_is",
        "key": "content.m\\.relates_to.rel_type",
        "value": "m.replace"
      },
      {
        "kind": "event_property_is",
        "key": "content.com\\.openclaw\\.finalized_preview",
        "value": true
      },
      { "kind": "event_match", "key": "sender", "pattern": "@bot:example.org" }
    ],
    "actions": [
      "notify",
      { "set_tweak": "sound", "value": "default" },
      { "set_tweak": "highlight", "value": false }
    ]
  }'
```

Sustituye estos valores antes de ejecutar el comando:

- `https://matrix.example.org`: la URL base de tu homeserver
- `$USER_ACCESS_TOKEN`: el token de acceso del usuario receptor
- `openclaw-finalized-preview-botname`: un ID de regla único para este bot para este usuario receptor
- `@bot:example.org`: el MXID de tu bot de Matrix de OpenClaw, no el MXID del usuario receptor

Importante para configuraciones con varios bots:

- Las reglas push se indexan por `ruleId`. Volver a ejecutar `PUT` contra el mismo ID de regla actualiza esa misma regla.
- Si un usuario receptor debe recibir notificaciones de varias cuentas de bot de Matrix de OpenClaw, crea una regla por bot con un ID de regla único para cada coincidencia de remitente.
- Un patrón sencillo es `openclaw-finalized-preview-<botname>`, como `openclaw-finalized-preview-ops` o `openclaw-finalized-preview-support`.

La regla se evalúa contra el remitente del evento:

- autentícate con el token del usuario receptor
- haz coincidir `sender` con el MXID del bot de OpenClaw

6. Verifica que la regla exista:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. Prueba una respuesta transmitida. En modo silencioso, la sala debería mostrar una vista previa de borrador silenciosa y la
   edición final en el mismo lugar debería notificar una vez que el bloque o el turno haya terminado.

Si necesitas eliminar la regla después, elimina ese mismo ID de regla con el token del usuario receptor:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Notas:

- Crea la regla con el token de acceso del usuario receptor, no con el del bot.
- Las nuevas reglas `override` definidas por el usuario se insertan antes de las reglas de supresión predeterminadas, así que no se necesita ningún parámetro adicional de orden.
- Esto solo afecta a las ediciones de vista previa de solo texto que OpenClaw puede finalizar de forma segura en el mismo lugar. Las rutas alternativas de multimedia y de vista previa obsoleta siguen usando la entrega normal de Matrix.
- Si `GET /_matrix/client/v3/pushers` no muestra pushers, el usuario todavía no tiene una entrega push de Matrix funcional para esta cuenta o dispositivo.

#### Synapse

Para Synapse, la configuración anterior suele ser suficiente por sí sola:

- No se requiere ningún cambio especial en `homeserver.yaml` para las notificaciones de vista previa finalizada de OpenClaw.
- Si tu implementación de Synapse ya envía notificaciones push normales de Matrix, el token de usuario + la llamada a `pushrules` anterior es el paso principal de configuración.
- Si ejecutas Synapse detrás de un proxy inverso o workers, asegúrate de que `/_matrix/client/.../pushrules/` llegue correctamente a Synapse.
- Si ejecutas workers de Synapse, asegúrate de que los pushers estén en buen estado. La entrega push la gestiona el proceso principal o `synapse.app.pusher` / los workers de pusher configurados.

#### Tuwunel

Para Tuwunel, usa el mismo flujo de configuración y la misma llamada a la API `push-rule` mostrados arriba:

- No se requiere ninguna configuración específica de Tuwunel para el marcador de vista previa finalizada.
- Si las notificaciones normales de Matrix ya funcionan para ese usuario, el token de usuario + la llamada a `pushrules` anterior es el paso principal de configuración.
- Si las notificaciones parecen desaparecer mientras el usuario está activo en otro dispositivo, comprueba si `suppress_push_when_active` está habilitado. Tuwunel añadió esta opción en Tuwunel 1.4.2 el 12 de septiembre de 2025, y puede suprimir intencionadamente los push hacia otros dispositivos mientras uno de ellos está activo.

## Cifrado y verificación

En salas cifradas (E2EE), los eventos salientes de imagen usan `thumbnail_file` para que las vistas previas de imagen se cifren junto con el adjunto completo. Las salas no cifradas siguen usando `thumbnail_url` sin cifrar. No se necesita ninguna configuración: el plugin detecta automáticamente el estado de E2EE.

### Salas de bot a bot

De forma predeterminada, los mensajes de otras cuentas configuradas de OpenClaw Matrix se ignoran.

Usa `allowBots` cuando quieras intencionadamente tráfico Matrix entre agentes:

```json5
{
  channels: {
    matrix: {
      allowBots: "mentions", // true | "mentions"
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

- `allowBots: true` acepta mensajes de otras cuentas configuradas de bot de Matrix en salas permitidas y en MD.
- `allowBots: "mentions"` acepta esos mensajes solo cuando mencionan visiblemente a este bot en salas. Los MD siguen permitidos.
- `groups.<room>.allowBots` reemplaza la configuración a nivel de cuenta para una sala.
- OpenClaw sigue ignorando los mensajes del mismo ID de usuario de Matrix para evitar bucles de autorrespuesta.
- Matrix no expone aquí una marca nativa de bot; OpenClaw trata "escrito por bot" como "enviado por otra cuenta configurada de Matrix en este gateway de OpenClaw".

Usa listas de permitidos estrictas de sala y requisitos de mención cuando habilites tráfico bot a bot en salas compartidas.

Habilitar cifrado:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

Comprobar el estado de verificación:

```bash
openclaw matrix verify status
```

Estado detallado (diagnósticos completos):

```bash
openclaw matrix verify status --verbose
```

Incluir la clave de recuperación almacenada en la salida legible por máquina:

```bash
openclaw matrix verify status --include-recovery-key --json
```

Inicializar el estado de cross-signing y verificación:

```bash
openclaw matrix verify bootstrap
```

Compatibilidad con varias cuentas: usa `channels.matrix.accounts` con credenciales por cuenta y `name` opcional. Consulta [Configuration reference](/es/gateway/configuration-reference#multi-account-all-channels) para el patrón compartido.

Diagnósticos detallados de bootstrap:

```bash
openclaw matrix verify bootstrap --verbose
```

Forzar un restablecimiento completo de la identidad de cross-signing antes de la inicialización:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

Verificar este dispositivo con una clave de recuperación:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

Detalles detallados de verificación del dispositivo:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

Comprobar el estado del respaldo de claves de sala:

```bash
openclaw matrix verify backup status
```

Diagnósticos detallados del estado del respaldo:

```bash
openclaw matrix verify backup status --verbose
```

Restaurar claves de sala desde el respaldo del servidor:

```bash
openclaw matrix verify backup restore
```

Diagnósticos detallados de restauración:

```bash
openclaw matrix verify backup restore --verbose
```

Eliminar el respaldo actual del servidor y crear una base nueva de respaldo. Si la
clave de respaldo almacenada no puede cargarse limpiamente, este restablecimiento también puede recrear el almacenamiento de secretos para que
los futuros arranques en frío puedan cargar la nueva clave de respaldo:

```bash
openclaw matrix verify backup reset --yes
```

Todos los comandos `verify` son concisos de forma predeterminada (incluido el registro interno silencioso del SDK) y solo muestran diagnósticos detallados con `--verbose`.
Usa `--json` para obtener la salida completa legible por máquina al automatizar scripts.

En configuraciones de varias cuentas, los comandos de Matrix CLI usan la cuenta predeterminada implícita de Matrix, a menos que pases `--account <id>`.
Si configuras varias cuentas con nombre, primero establece `channels.matrix.defaultAccount` o esas operaciones implícitas de CLI se detendrán y te pedirán que elijas una cuenta explícitamente.
Usa `--account` siempre que quieras que las operaciones de verificación o de dispositivo apunten explícitamente a una cuenta con nombre:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Cuando el cifrado está deshabilitado o no está disponible para una cuenta con nombre, las advertencias de Matrix y los errores de verificación apuntan a la clave de configuración de esa cuenta, por ejemplo `channels.matrix.accounts.assistant.encryption`.

### Qué significa "verified"

OpenClaw trata este dispositivo de Matrix como verificado solo cuando está verificado por tu propia identidad de cross-signing.
En la práctica, `openclaw matrix verify status --verbose` expone tres señales de confianza:

- `Locally trusted`: este dispositivo es de confianza solo para el cliente actual
- `Cross-signing verified`: el SDK informa que el dispositivo está verificado mediante cross-signing
- `Signed by owner`: el dispositivo está firmado por tu propia clave self-signing

`Verified by owner` pasa a ser `yes` solo cuando existe verificación por cross-signing o firma del propietario.
La confianza local por sí sola no basta para que OpenClaw trate el dispositivo como totalmente verificado.

### Qué hace bootstrap

`openclaw matrix verify bootstrap` es el comando de reparación y configuración para cuentas cifradas de Matrix.
Hace todo lo siguiente en este orden:

- inicializa el almacenamiento de secretos, reutilizando una clave de recuperación existente cuando es posible
- inicializa cross-signing y sube las claves públicas de cross-signing que falten
- intenta marcar y firmar mediante cross-signing el dispositivo actual
- crea un nuevo respaldo del lado del servidor para claves de sala si todavía no existe uno

Si el homeserver requiere autenticación interactiva para subir claves de cross-signing, OpenClaw intenta la subida primero sin autenticación, luego con `m.login.dummy`, y después con `m.login.password` cuando `channels.matrix.password` está configurado.

Usa `--force-reset-cross-signing` solo cuando quieras descartar intencionadamente la identidad actual de cross-signing y crear una nueva.

Si intencionadamente quieres descartar el respaldo actual de claves de sala y empezar una nueva
base de respaldo para mensajes futuros, usa `openclaw matrix verify backup reset --yes`.
Hazlo solo si aceptas que el historial cifrado antiguo irrecuperable seguirá
sin estar disponible y que OpenClaw puede recrear el almacenamiento de secretos si el secreto de respaldo actual
no puede cargarse de forma segura.

### Base nueva de respaldo

Si quieres mantener funcionando los futuros mensajes cifrados y aceptas perder el historial antiguo irrecuperable, ejecuta estos comandos en orden:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Añade `--account <id>` a cada comando cuando quieras apuntar explícitamente a una cuenta de Matrix con nombre.

### Comportamiento al iniciar

Cuando `encryption: true`, Matrix establece por defecto `startupVerification` en `"if-unverified"`.
Al iniciar, si este dispositivo sigue sin verificar, Matrix solicitará la autoverificación en otro cliente de Matrix,
omitirá solicitudes duplicadas mientras ya haya una pendiente y aplicará un tiempo de espera local antes de reintentar tras reinicios.
Los intentos fallidos de solicitud se reintentan antes que la creación exitosa de solicitudes, de forma predeterminada.
Establece `startupVerification: "off"` para desactivar las solicitudes automáticas al iniciar, o ajusta `startupVerificationCooldownHours`
si quieres una ventana de reintento más corta o más larga.

El inicio también realiza automáticamente una pasada conservadora de bootstrap criptográfico.
Esa pasada intenta primero reutilizar el almacenamiento de secretos y la identidad actual de cross-signing, y evita restablecer cross-signing salvo que ejecutes un flujo explícito de reparación de bootstrap.

Si al iniciar se detecta un estado roto de bootstrap y `channels.matrix.password` está configurado, OpenClaw puede intentar una ruta de reparación más estricta.
Si el dispositivo actual ya está firmado por el propietario, OpenClaw conserva esa identidad en lugar de restablecerla automáticamente.

Actualizar desde el plugin público anterior de Matrix:

- OpenClaw reutiliza automáticamente la misma cuenta de Matrix, el token de acceso y la identidad del dispositivo cuando es posible.
- Antes de ejecutar cualquier cambio de migración de Matrix que requiera acción, OpenClaw crea o reutiliza una instantánea de recuperación en `~/Backups/openclaw-migrations/`.
- Si usas varias cuentas de Matrix, establece `channels.matrix.defaultAccount` antes de actualizar desde el antiguo diseño de almacenamiento plano para que OpenClaw sepa qué cuenta debe recibir ese estado heredado compartido.
- Si el plugin anterior almacenaba localmente una clave de descifrado del respaldo de claves de sala de Matrix, el inicio o `openclaw doctor --fix` la importarán automáticamente al nuevo flujo de clave de recuperación.
- Si el token de acceso de Matrix cambió después de preparar la migración, ahora el inicio busca raíces vecinas de almacenamiento por hash de token en busca de estado heredado pendiente de restauración antes de abandonar la restauración automática del respaldo.
- Si el token de acceso de Matrix cambia más tarde para la misma cuenta, homeserver y usuario, OpenClaw ahora prefiere reutilizar la raíz existente por hash de token más completa en lugar de empezar desde un directorio vacío de estado de Matrix.
- En el siguiente arranque del gateway, las claves de sala respaldadas se restauran automáticamente en el nuevo almacén criptográfico.
- Si el plugin antiguo tenía claves de sala solo locales que nunca se respaldaron, OpenClaw lo advertirá claramente. Esas claves no pueden exportarse automáticamente desde el almacén criptográfico anterior de Rust, por lo que parte del historial cifrado antiguo puede seguir sin estar disponible hasta recuperarse manualmente.
- Consulta [Matrix migration](/es/install/migrating-matrix) para ver el flujo completo de actualización, límites, comandos de recuperación y mensajes comunes de migración.

El estado cifrado en tiempo de ejecución se organiza en raíces por cuenta, usuario y hash de token en
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`.
Ese directorio contiene el almacén de sincronización (`bot-storage.json`), el almacén criptográfico (`crypto/`),
el archivo de clave de recuperación (`recovery-key.json`), la instantánea de IndexedDB (`crypto-idb-snapshot.json`),
las vinculaciones de hilos (`thread-bindings.json`) y el estado de verificación al iniciar (`startup-verification.json`)
cuando esas funciones están en uso.
Cuando el token cambia pero la identidad de la cuenta sigue siendo la misma, OpenClaw reutiliza la mejor
raíz existente para esa tupla de cuenta/homeserver/usuario, de modo que el estado previo de sincronización, estado criptográfico, vinculaciones de hilos
y estado de verificación al iniciar sigan siendo visibles.

### Modelo de almacén criptográfico de Node

La E2EE de Matrix en este plugin usa la ruta criptográfica Rust oficial de `matrix-js-sdk` en Node.
Esa ruta espera persistencia basada en IndexedDB cuando quieres que el estado criptográfico sobreviva a los reinicios.

Actualmente OpenClaw la proporciona en Node de esta forma:

- usa `fake-indexeddb` como el shim de API de IndexedDB que espera el SDK
- restaura el contenido de IndexedDB criptográfico de Rust desde `crypto-idb-snapshot.json` antes de `initRustCrypto`
- persiste el contenido actualizado de IndexedDB de vuelta en `crypto-idb-snapshot.json` después de la inicialización y durante la ejecución
- serializa la restauración y persistencia de instantáneas frente a `crypto-idb-snapshot.json` con un bloqueo de archivo consultivo para que la persistencia del gateway en tiempo de ejecución y el mantenimiento por CLI no compitan por el mismo archivo de instantánea

Esto es compatibilidad y plomería de almacenamiento, no una implementación criptográfica personalizada.
El archivo de instantánea es estado sensible en tiempo de ejecución y se almacena con permisos de archivo restrictivos.
Según el modelo de seguridad de OpenClaw, el host del gateway y el directorio local de estado de OpenClaw ya están dentro del límite de confianza del operador, así que esto es principalmente una cuestión de durabilidad operativa más que un límite de confianza remoto separado.

Mejora planificada:

- añadir compatibilidad con SecretRef para el material persistente de claves de Matrix, de modo que las claves de recuperación y los secretos relacionados de cifrado del almacén puedan obtenerse de proveedores de secretos de OpenClaw en lugar de solo de archivos locales

## Gestión de perfil

Actualiza el perfil propio de Matrix para la cuenta seleccionada con:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Añade `--account <id>` cuando quieras apuntar explícitamente a una cuenta de Matrix con nombre.

Matrix acepta directamente URLs de avatar `mxc://`. Cuando pasas una URL de avatar `http://` o `https://`, OpenClaw la sube primero a Matrix y almacena la URL `mxc://` resuelta de vuelta en `channels.matrix.avatarUrl` (o en la anulación de la cuenta seleccionada).

## Avisos automáticos de verificación

Matrix ahora publica avisos del ciclo de vida de la verificación directamente en la sala estricta de MD de verificación como mensajes `m.notice`.
Eso incluye:

- avisos de solicitud de verificación
- avisos de verificación lista (con indicación explícita de "Verificar por emoji")
- avisos de inicio y finalización de verificación
- detalles SAS (emoji y decimal) cuando están disponibles

Las solicitudes entrantes de verificación desde otro cliente de Matrix se rastrean y OpenClaw las acepta automáticamente.
Para flujos de autoverificación, OpenClaw también inicia automáticamente el flujo SAS cuando la verificación por emoji está disponible y confirma su propio lado.
Para solicitudes de verificación de otro usuario o dispositivo de Matrix, OpenClaw acepta automáticamente la solicitud y luego espera a que el flujo SAS continúe normalmente.
Aun así, debes comparar el SAS de emoji o decimal en tu cliente de Matrix y confirmar allí "They match" para completar la verificación.

OpenClaw no acepta automáticamente a ciegas flujos duplicados iniciados por él mismo. Al iniciar se omite crear una nueva solicitud cuando ya hay una solicitud de autoverificación pendiente.

Los avisos de verificación de protocolo/sistema no se reenvían al flujo de chat del agente, por lo que no producen `NO_REPLY`.

### Higiene de dispositivos

Los dispositivos antiguos de Matrix gestionados por OpenClaw pueden acumularse en la cuenta y dificultar la comprensión de la confianza en salas cifradas.
Enuméralos con:

```bash
openclaw matrix devices list
```

Elimina los dispositivos obsoletos gestionados por OpenClaw con:

```bash
openclaw matrix devices prune-stale
```

### Reparación directa de salas

Si el estado de mensajes directos se desincroniza, OpenClaw puede terminar con asignaciones `m.direct` obsoletas que apuntan a salas individuales antiguas en lugar del MD activo. Inspecciona la asignación actual para un par con:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Repárala con:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

La reparación mantiene la lógica específica de Matrix dentro del plugin:

- prefiere un MD estricto 1:1 que ya esté asignado en `m.direct`
- en caso contrario, recurre a cualquier MD estricto 1:1 actualmente unido con ese usuario
- si no existe un MD sano, crea una nueva sala directa y reescribe `m.direct` para que apunte a ella

El flujo de reparación no elimina automáticamente las salas antiguas. Solo elige el MD correcto y actualiza la asignación para que los nuevos envíos de Matrix, avisos de verificación y otros flujos de mensajes directos vuelvan a apuntar a la sala correcta.

## Hilos

Matrix admite hilos nativos de Matrix tanto para respuestas automáticas como para envíos con la herramienta de mensajes.

- `dm.sessionScope: "per-user"` (predeterminado) mantiene el enrutamiento de MD de Matrix con alcance al remitente, de modo que varias salas de MD puedan compartir una sesión cuando se resuelven al mismo par.
- `dm.sessionScope: "per-room"` aísla cada sala de MD de Matrix en su propia clave de sesión sin dejar de usar las comprobaciones normales de autenticación y lista de permitidos de MD.
- Las vinculaciones explícitas de conversación de Matrix siguen teniendo prioridad sobre `dm.sessionScope`, por lo que las salas e hilos vinculados conservan su sesión de destino elegida.
- `threadReplies: "off"` mantiene las respuestas en el nivel superior y mantiene los mensajes entrantes en hilo en la sesión principal.
- `threadReplies: "inbound"` responde dentro de un hilo solo cuando el mensaje entrante ya estaba en ese hilo.
- `threadReplies: "always"` mantiene las respuestas de sala en un hilo con raíz en el mensaje desencadenante y enruta esa conversación mediante la sesión con alcance de hilo correspondiente desde el primer mensaje desencadenante.
- `dm.threadReplies` reemplaza la configuración de nivel superior solo para MD. Por ejemplo, puedes mantener aislados los hilos de sala mientras mantienes los MD planos.
- Los mensajes entrantes en hilo incluyen el mensaje raíz del hilo como contexto adicional para el agente.
- Los envíos de la herramienta de mensajes ahora heredan automáticamente el hilo actual de Matrix cuando el destino es la misma sala o el mismo objetivo de usuario de MD, a menos que se proporcione un `threadId` explícito.
- La reutilización de objetivo de usuario de MD de misma sesión solo se activa cuando los metadatos de la sesión actual demuestran el mismo par de MD en la misma cuenta de Matrix; en caso contrario, OpenClaw vuelve al enrutamiento normal con alcance de usuario.
- Cuando OpenClaw ve que una sala de MD de Matrix entra en conflicto con otra sala de MD en la misma sesión compartida de MD de Matrix, publica un `m.notice` de una sola vez en esa sala con la vía de escape `/focus` cuando las vinculaciones de hilos están habilitadas y la pista `dm.sessionScope`.
- Las vinculaciones de hilos en tiempo de ejecución son compatibles con Matrix. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` y `/acp spawn` vinculado a hilo ahora funcionan en salas y MD de Matrix.
- `/focus` de sala/MD de Matrix de nivel superior crea un nuevo hilo de Matrix y lo vincula a la sesión de destino cuando `threadBindings.spawnSubagentSessions=true`.
- Ejecutar `/focus` o `/acp spawn --thread here` dentro de un hilo de Matrix existente vincula ese hilo actual en su lugar.

## Vinculaciones de conversación ACP

Las salas, los MD y los hilos existentes de Matrix pueden convertirse en espacios de trabajo ACP duraderos sin cambiar la superficie del chat.

Flujo rápido del operador:

- Ejecuta `/acp spawn codex --bind here` dentro del MD, la sala o el hilo existente de Matrix que quieras seguir usando.
- En un MD o sala de Matrix de nivel superior, el MD o la sala actuales siguen siendo la superficie del chat y los mensajes futuros se enrutan a la sesión ACP creada.
- Dentro de un hilo existente de Matrix, `--bind here` vincula ese hilo actual en el mismo lugar.
- `/new` y `/reset` restablecen la misma sesión ACP vinculada en el mismo lugar.
- `/acp close` cierra la sesión ACP y elimina la vinculación.

Notas:

- `--bind here` no crea un hilo hijo de Matrix.
- `threadBindings.spawnAcpSessions` solo es necesario para `/acp spawn --thread auto|here`, donde OpenClaw necesita crear o vincular un hilo hijo de Matrix.

### Configuración de vinculación de hilos

Matrix hereda los valores predeterminados globales de `session.threadBindings` y también admite reemplazos por canal:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Las banderas de creación vinculada a hilos de Matrix son opcionales:

- Establece `threadBindings.spawnSubagentSessions: true` para permitir que `/focus` de nivel superior cree y vincule nuevos hilos de Matrix.
- Establece `threadBindings.spawnAcpSessions: true` para permitir que `/acp spawn --thread auto|here` vincule sesiones ACP a hilos de Matrix.

## Reacciones

Matrix admite acciones de reacción salientes, notificaciones de reacción entrantes y reacciones de confirmación entrantes.

- La herramienta de reacciones salientes está controlada por `channels["matrix"].actions.reactions`.
- `react` añade una reacción a un evento específico de Matrix.
- `reactions` enumera el resumen actual de reacciones para un evento específico de Matrix.
- `emoji=""` elimina las reacciones de la propia cuenta del bot en ese evento.
- `remove: true` elimina solo la reacción con el emoji especificado de la cuenta del bot.

Las reacciones de confirmación usan el orden estándar de resolución de OpenClaw:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- emoji de reserva de identidad del agente

El alcance de la reacción de confirmación se resuelve en este orden:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

El modo de notificación de reacciones se resuelve en este orden:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- predeterminado: `own`

Comportamiento actual:

- `reactionNotifications: "own"` reenvía eventos `m.reaction` añadidos cuando apuntan a mensajes de Matrix escritos por el bot.
- `reactionNotifications: "off"` desactiva los eventos del sistema de reacciones.
- Las eliminaciones de reacciones todavía no se sintetizan en eventos del sistema porque Matrix las expone como redacciones, no como eliminaciones independientes de `m.reaction`.

## Contexto del historial

- `channels.matrix.historyLimit` controla cuántos mensajes recientes de la sala se incluyen como `InboundHistory` cuando un mensaje de sala de Matrix activa al agente.
- Recurre a `messages.groupChat.historyLimit`. Si ambos no están establecidos, el valor predeterminado efectivo es `0`, por lo que los mensajes de sala con requisito de mención no se almacenan en búfer. Establece `0` para desactivar.
- El historial de salas de Matrix es solo de sala. Los MD siguen usando el historial normal de sesión.
- El historial de salas de Matrix es solo pendiente: OpenClaw almacena en búfer los mensajes de sala que todavía no activaron una respuesta y luego toma una instantánea de esa ventana cuando llega una mención u otro activador.
- El mensaje activador actual no se incluye en `InboundHistory`; permanece en el cuerpo principal entrante para ese turno.
- Los reintentos del mismo evento de Matrix reutilizan la instantánea original del historial en lugar de avanzar hacia mensajes más nuevos de la sala.

## Visibilidad del contexto

Matrix admite el control compartido `contextVisibility` para el contexto suplementario de sala, como texto de respuesta recuperado, raíces de hilo e historial pendiente.

- `contextVisibility: "all"` es el valor predeterminado. El contexto suplementario se conserva tal como se recibe.
- `contextVisibility: "allowlist"` filtra el contexto suplementario a remitentes permitidos por las comprobaciones activas de lista de permitidos de sala/usuario.
- `contextVisibility: "allowlist_quote"` se comporta como `allowlist`, pero sigue conservando una respuesta citada explícita.

Esta configuración afecta la visibilidad del contexto suplementario, no si el propio mensaje entrante puede activar una respuesta.
La autorización del activador sigue viniendo de `groupPolicy`, `groups`, `groupAllowFrom` y la configuración de política de MD.

## Ejemplo de política de MD y sala

```json5
{
  channels: {
    matrix: {
      dm: {
        policy: "allowlist",
        allowFrom: ["@admin:example.org"],
        threadReplies: "off",
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

Consulta [Groups](/es/channels/groups) para conocer el comportamiento de requisito de mención y lista de permitidos.

Ejemplo de emparejamiento para MD de Matrix:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Si un usuario de Matrix no aprobado sigue enviándote mensajes antes de la aprobación, OpenClaw reutiliza el mismo código de emparejamiento pendiente y puede volver a enviar una respuesta de recordatorio tras un breve tiempo de espera en lugar de generar un código nuevo.

Consulta [Pairing](/es/channels/pairing) para ver el flujo compartido de emparejamiento de MD y el diseño de almacenamiento.

## Aprobaciones de ejecución

Matrix puede actuar como cliente de aprobación de ejecución para una cuenta de Matrix.

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (opcional; recurre a `channels.matrix.dm.allowFrom`)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, predeterminado: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Los aprobadores deben ser IDs de usuario de Matrix como `@owner:example.org`. Matrix habilita automáticamente las aprobaciones nativas de ejecución cuando `enabled` no está establecido o es `"auto"` y al menos puede resolverse un aprobador, ya sea desde `execApprovals.approvers` o desde `channels.matrix.dm.allowFrom`. Establece `enabled: false` para desactivar explícitamente Matrix como cliente nativo de aprobación. En caso contrario, las solicitudes de aprobación recurren a otras rutas de aprobación configuradas o a la política de reserva de aprobación de ejecución.

El enrutamiento nativo de Matrix hoy es solo para ejecución:

- `channels.matrix.execApprovals.*` controla el enrutamiento nativo de MD/canal para aprobaciones de ejecución únicamente.
- Las aprobaciones de plugin siguen usando `/approve` en el mismo chat compartido más cualquier reenvío configurado de `approvals.plugin`.
- Matrix todavía puede reutilizar `channels.matrix.dm.allowFrom` para la autorización de aprobación de plugins cuando puede inferir aprobadores de forma segura, pero no expone una ruta nativa separada de distribución en MD/canal para aprobación de plugins.

Reglas de entrega:

- `target: "dm"` envía solicitudes de aprobación a los MD de los aprobadores
- `target: "channel"` envía la solicitud de vuelta a la sala o MD de Matrix de origen
- `target: "both"` envía a los MD de los aprobadores y a la sala o MD de Matrix de origen

Las solicitudes de aprobación de Matrix generan atajos de reacción en el mensaje principal de aprobación:

- `✅` = permitir una vez
- `❌` = denegar
- `♾️` = permitir siempre cuando esa decisión esté permitida por la política de ejecución efectiva

Los aprobadores pueden reaccionar en ese mensaje o usar los comandos slash de reserva: `/approve <id> allow-once`, `/approve <id> allow-always` o `/approve <id> deny`.

Solo los aprobadores resueltos pueden aprobar o denegar. La entrega por canal incluye el texto del comando, así que habilita `channel` o `both` solo en salas de confianza.

Las solicitudes de aprobación de Matrix reutilizan el planificador compartido principal de aprobaciones. La superficie nativa específica de Matrix es solo el transporte para aprobaciones de ejecución: enrutamiento de sala/MD y comportamiento de envío/actualización/eliminación de mensajes.

Reemplazo por cuenta:

- `channels.matrix.accounts.<account>.execApprovals`

Documentación relacionada: [Exec approvals](/es/tools/exec-approvals)

## Ejemplo de varias cuentas

```json5
{
  channels: {
    matrix: {
      enabled: true,
      defaultAccount: "assistant",
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_xxx",
          encryption: true,
        },
        alerts: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_xxx",
          dm: {
            policy: "allowlist",
            allowFrom: ["@ops:example.org"],
            threadReplies: "off",
          },
        },
      },
    },
  },
}
```

Los valores de nivel superior `channels.matrix` actúan como valores predeterminados para las cuentas con nombre, salvo que una cuenta los reemplace.
Puedes limitar una entrada de sala heredada a una cuenta de Matrix con `groups.<room>.account` (o el heredado `rooms.<room>.account`).
Las entradas sin `account` permanecen compartidas entre todas las cuentas de Matrix, y las entradas con `account: "default"` siguen funcionando cuando la cuenta predeterminada se configura directamente en `channels.matrix.*` de nivel superior.
Los valores predeterminados parciales de autenticación compartida no crean por sí solos una cuenta predeterminada implícita separada. OpenClaw solo sintetiza la cuenta `default` de nivel superior cuando ese valor predeterminado tiene autenticación nueva (`homeserver` más `accessToken`, o `homeserver` más `userId` y `password`); las cuentas con nombre pueden seguir siendo detectables a partir de `homeserver` más `userId` cuando las credenciales en caché satisfagan la autenticación más adelante.
Si Matrix ya tiene exactamente una cuenta con nombre, o `defaultAccount` apunta a una clave existente de cuenta con nombre, la promoción de reparación/configuración de una sola cuenta a varias cuentas conserva esa cuenta en lugar de crear una nueva entrada `accounts.default`. Solo las claves de autenticación/bootstrap de Matrix se mueven a esa cuenta promovida; las claves de política de entrega compartida permanecen en el nivel superior.
Establece `defaultAccount` cuando quieras que OpenClaw prefiera una cuenta de Matrix con nombre para el enrutamiento implícito, sondeo y operaciones de CLI.
Si configuras varias cuentas con nombre, establece `defaultAccount` o pasa `--account <id>` para los comandos de CLI que dependen de la selección implícita de cuenta.
Pasa `--account <id>` a `openclaw matrix verify ...` y `openclaw matrix devices ...` cuando quieras reemplazar esa selección implícita para un comando.

## Homeservers privados/LAN

De forma predeterminada, OpenClaw bloquea los homeservers privados o internos de Matrix para protección SSRF, salvo que
aceptes explícitamente por cuenta.

Si tu homeserver se ejecuta en localhost, una IP de LAN/Tailscale o un nombre de host interno, habilita
`allowPrivateNetwork` para esa cuenta de Matrix:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      allowPrivateNetwork: true,
      accessToken: "syt_internal_xxx",
    },
  },
}
```

Ejemplo de configuración mediante CLI:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

Esta aceptación solo permite destinos privados o internos de confianza. Los homeservers públicos en texto plano, como
`http://matrix.example.org:8008`, siguen bloqueados. Usa `https://` siempre que sea posible.

## Proxy para tráfico de Matrix

Si tu implementación de Matrix necesita un proxy HTTP(S) saliente explícito, establece `channels.matrix.proxy`:

```json5
{
  channels: {
    matrix: {
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
    },
  },
}
```

Las cuentas con nombre pueden reemplazar el valor predeterminado de nivel superior con `channels.matrix.accounts.<id>.proxy`.
OpenClaw usa la misma configuración de proxy para el tráfico de Matrix en tiempo de ejecución y para los sondeos de estado de cuenta.

## Resolución de destino

Matrix acepta estas formas de destino en cualquier lugar donde OpenClaw te pida un objetivo de sala o usuario:

- Usuarios: `@user:server`, `user:@user:server` o `matrix:user:@user:server`
- Salas: `!room:server`, `room:!room:server` o `matrix:room:!room:server`
- Alias: `#alias:server`, `channel:#alias:server` o `matrix:channel:#alias:server`

La búsqueda en directorio en vivo usa la cuenta de Matrix con sesión iniciada:

- Las búsquedas de usuarios consultan el directorio de usuarios de Matrix en ese homeserver.
- Las búsquedas de salas aceptan directamente IDs y alias explícitos de sala, y luego recurren a buscar nombres de salas unidas para esa cuenta.
- La búsqueda de nombres de salas unidas es de mejor esfuerzo. Si un nombre de sala no puede resolverse a un ID o alias, se ignora en la resolución de lista de permitidos en tiempo de ejecución.

## Referencia de configuración

- `enabled`: habilita o deshabilita el canal.
- `name`: etiqueta opcional para la cuenta.
- `defaultAccount`: ID de cuenta preferido cuando se configuran varias cuentas de Matrix.
- `homeserver`: URL del homeserver, por ejemplo `https://matrix.example.org`.
- `allowPrivateNetwork`: permite que esta cuenta de Matrix se conecte a homeservers privados o internos. Habilítalo cuando el homeserver resuelva a `localhost`, una IP de LAN/Tailscale o un host interno como `matrix-synapse`.
- `proxy`: URL opcional de proxy HTTP(S) para tráfico de Matrix. Las cuentas con nombre pueden reemplazar el valor predeterminado de nivel superior con su propio `proxy`.
- `userId`: ID completo de usuario de Matrix, por ejemplo `@bot:example.org`.
- `accessToken`: token de acceso para autenticación basada en token. Se admiten valores en texto plano y valores SecretRef para `channels.matrix.accessToken` y `channels.matrix.accounts.<id>.accessToken` en proveedores env/file/exec. Consulta [Secrets Management](/es/gateway/secrets).
- `password`: contraseña para inicio de sesión basado en contraseña. Se admiten valores en texto plano y valores SecretRef.
- `deviceId`: ID explícito del dispositivo de Matrix.
- `deviceName`: nombre para mostrar del dispositivo para inicio de sesión por contraseña.
- `avatarUrl`: URL almacenada del avatar propio para sincronización de perfil y actualizaciones `set-profile`.
- `initialSyncLimit`: límite de eventos de sincronización al iniciar.
- `encryption`: habilita E2EE.
- `allowlistOnly`: fuerza comportamiento de solo lista de permitidos para MD y salas.
- `allowBots`: permite mensajes de otras cuentas configuradas de OpenClaw Matrix (`true` o `"mentions"`).
- `groupPolicy`: `open`, `allowlist` o `disabled`.
- `contextVisibility`: modo de visibilidad del contexto suplementario de sala (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: lista de permitidos de IDs de usuario para tráfico de sala.
- Las entradas de `groupAllowFrom` deben ser IDs completos de usuario de Matrix. Los nombres sin resolver se ignoran en tiempo de ejecución.
- `historyLimit`: máximo de mensajes de sala que se incluirán como contexto de historial de grupo. Recurre a `messages.groupChat.historyLimit`; si ambos no están establecidos, el valor predeterminado efectivo es `0`. Establece `0` para desactivar.
- `replyToMode`: `off`, `first` o `all`.
- `markdown`: configuración opcional de renderizado Markdown para texto saliente de Matrix.
- `streaming`: `off` (predeterminado), `partial`, `quiet`, `true` o `false`. `partial` y `true` habilitan actualizaciones de borrador de vista previa primero con mensajes normales de texto de Matrix. `quiet` usa avisos de vista previa sin notificación para configuraciones autoalojadas con reglas push.
- `blockStreaming`: `true` habilita mensajes de progreso separados para bloques completados del asistente mientras el streaming de borrador de vista previa está activo.
- `threadReplies`: `off`, `inbound` o `always`.
- `threadBindings`: reemplazos por canal para el enrutamiento y ciclo de vida de sesiones vinculadas a hilos.
- `startupVerification`: modo de solicitud automática de autoverificación al iniciar (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: tiempo de espera antes de reintentar solicitudes automáticas de verificación al iniciar.
- `textChunkLimit`: tamaño de fragmento de mensaje saliente.
- `chunkMode`: `length` o `newline`.
- `responsePrefix`: prefijo opcional de mensaje para respuestas salientes.
- `ackReaction`: reemplazo opcional de reacción de confirmación para este canal o cuenta.
- `ackReactionScope`: reemplazo opcional del alcance de la reacción de confirmación (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: modo de notificación de reacción entrante (`own`, `off`).
- `mediaMaxMb`: límite de tamaño de multimedia en MB para el manejo multimedia de Matrix. Se aplica a los envíos salientes y al procesamiento multimedia entrante.
- `autoJoin`: política de autoaceptación de invitaciones (`always`, `allowlist`, `off`). Predeterminado: `off`. Esto se aplica a las invitaciones de Matrix en general, incluidas las invitaciones de estilo MD, no solo a invitaciones de salas o grupos. OpenClaw toma esta decisión en el momento de la invitación, antes de poder clasificar de forma fiable la sala unida como MD o grupo.
- `autoJoinAllowlist`: salas o alias permitidos cuando `autoJoin` es `allowlist`. Las entradas de alias se resuelven a IDs de sala durante el manejo de invitaciones; OpenClaw no confía en el estado de alias declarado por la sala invitada.
- `dm`: bloque de política de MD (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- `dm.policy`: controla el acceso a MD después de que OpenClaw se haya unido a la sala y la haya clasificado como MD. No cambia si una invitación se autoacepta.
- Las entradas de `dm.allowFrom` deben ser IDs completos de usuario de Matrix, salvo que ya las hayas resuelto mediante búsqueda en directorio en vivo.
- `dm.sessionScope`: `per-user` (predeterminado) o `per-room`. Usa `per-room` cuando quieras que cada sala de MD de Matrix conserve un contexto separado aunque el par sea el mismo.
- `dm.threadReplies`: reemplazo de política de hilos solo para MD (`off`, `inbound`, `always`). Reemplaza la configuración de nivel superior `threadReplies` tanto para la colocación de respuestas como para el aislamiento de sesión en MD.
- `execApprovals`: entrega nativa de aprobación de ejecución de Matrix (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: IDs de usuario de Matrix autorizados para aprobar solicitudes de ejecución. Opcional cuando `dm.allowFrom` ya identifica a los aprobadores.
- `execApprovals.target`: `dm | channel | both` (predeterminado: `dm`).
- `accounts`: reemplazos con nombre por cuenta. Los valores de nivel superior `channels.matrix` actúan como predeterminados para estas entradas.
- `groups`: mapa de política por sala. Usa preferiblemente IDs o alias de sala; los nombres de sala sin resolver se ignoran en tiempo de ejecución. La identidad de sesión o grupo usa el ID estable de sala después de la resolución, mientras que las etiquetas legibles siguen viniendo de los nombres de sala.
- `groups.<room>.account`: restringe una entrada heredada de sala a una cuenta específica de Matrix en configuraciones de varias cuentas.
- `groups.<room>.allowBots`: reemplazo a nivel de sala para remitentes bot configurados (`true` o `"mentions"`).
- `groups.<room>.users`: lista de permitidos de remitentes por sala.
- `groups.<room>.tools`: reemplazos por sala para permitir o denegar herramientas.
- `groups.<room>.autoReply`: reemplazo a nivel de sala del requisito de mención. `true` desactiva el requisito de mención para esa sala; `false` vuelve a activarlo.
- `groups.<room>.skills`: filtro opcional de Skills a nivel de sala.
- `groups.<room>.systemPrompt`: fragmento opcional de prompt del sistema a nivel de sala.
- `rooms`: alias heredado de `groups`.
- `actions`: control por acción de herramientas (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## Relacionado

- [Channels Overview](/es/channels) — todos los canales compatibles
- [Pairing](/es/channels/pairing) — autenticación MD y flujo de emparejamiento
- [Groups](/es/channels/groups) — comportamiento del chat de grupo y requisito de mención
- [Channel Routing](/es/channels/channel-routing) — enrutamiento de sesión para mensajes
- [Security](/es/gateway/security) — modelo de acceso y endurecimiento
