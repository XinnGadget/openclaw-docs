---
read_when:
    - Implementar o actualizar clientes WS del gateway
    - Depurar incompatibilidades de protocolo o fallos de conexión
    - Regenerar el esquema/modelos del protocolo
summary: 'Protocolo WebSocket del Gateway: handshake, frames y versionado'
title: Protocolo del Gateway
x-i18n:
    generated_at: "2026-04-11T02:44:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 83c820c46d4803d571c770468fd6782619eaa1dca253e156e8087dec735c127f
    source_path: gateway/protocol.md
    workflow: 15
---

# Protocolo del Gateway (WebSocket)

El protocolo WS del Gateway es el **plano de control único + transporte de nodos** para
OpenClaw. Todos los clientes (CLI, UI web, app de macOS, nodos iOS/Android, nodos
headless) se conectan por WebSocket y declaran su **role** + **scope** en el momento
del handshake.

## Transporte

- WebSocket, frames de texto con cargas JSON.
- El primer frame **debe** ser una solicitud `connect`.

## Handshake (connect)

Gateway → Cliente (desafío previo a la conexión):

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

Cliente → Gateway:

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

Gateway → Cliente:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": { "type": "hello-ok", "protocol": 3, "policy": { "tickIntervalMs": 15000 } }
}
```

Cuando se emite un token de dispositivo, `hello-ok` también incluye:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

Durante el traspaso de bootstrap confiable, `hello-ok.auth` también puede incluir
entradas de rol adicionales acotadas en `deviceTokens`:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "node",
    "scopes": [],
    "deviceTokens": [
      {
        "deviceToken": "…",
        "role": "operator",
        "scopes": ["operator.approvals", "operator.read", "operator.talk.secrets", "operator.write"]
      }
    ]
  }
}
```

Para el flujo bootstrap integrado de nodo/operator, el token principal del nodo se mantiene con
`scopes: []` y cualquier token de operator transferido sigue acotado a la allowlist
del operator de bootstrap (`operator.approvals`, `operator.read`,
`operator.talk.secrets`, `operator.write`). Las comprobaciones de scope de bootstrap siguen
prefijadas por rol: las entradas de operator solo satisfacen solicitudes de operator, y los roles
que no son operator siguen necesitando scopes bajo su propio prefijo de rol.

### Ejemplo de nodo

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## Enmarcado

- **Solicitud**: `{type:"req", id, method, params}`
- **Respuesta**: `{type:"res", id, ok, payload|error}`
- **Evento**: `{type:"event", event, payload, seq?, stateVersion?}`

Los métodos con efectos secundarios requieren **claves de idempotencia** (consulta el esquema).

## Roles + scopes

### Roles

- `operator` = cliente del plano de control (CLI/UI/automatización).
- `node` = host de capacidades (camera/screen/canvas/system.run).

### Scopes (operator)

Scopes comunes:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

`talk.config` con `includeSecrets: true` requiere `operator.talk.secrets`
(o `operator.admin`).

Los métodos RPC del gateway registrados por plugins pueden solicitar su propio scope de operator, pero
los prefijos reservados de administración del núcleo (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) siempre se resuelven a `operator.admin`.

El scope del método es solo la primera barrera. Algunos comandos con barra alcanzados mediante
`chat.send` aplican comprobaciones más estrictas a nivel de comando además de eso. Por ejemplo, las escrituras
persistentes de `/config set` y `/config unset` requieren `operator.admin`.

`node.pair.approve` también tiene una comprobación de scope adicional en el momento de la aprobación
además del scope base del método:

- solicitudes sin comando: `operator.pairing`
- solicitudes con comandos de nodo que no son exec: `operator.pairing` + `operator.write`
- solicitudes que incluyen `system.run`, `system.run.prepare` o `system.which`:
  `operator.pairing` + `operator.admin`

### Caps/commands/permissions (node)

Los nodos declaran las capacidades reclamadas al conectarse:

- `caps`: categorías de capacidades de alto nivel.
- `commands`: allowlist de comandos para invoke.
- `permissions`: alternadores granulares (p. ej., `screen.record`, `camera.capture`).

El Gateway trata estas como **claims** y aplica allowlists del lado del servidor.

## Presencia

- `system-presence` devuelve entradas con clave por identidad del dispositivo.
- Las entradas de presencia incluyen `deviceId`, `roles` y `scopes` para que las UI puedan mostrar una sola fila por dispositivo
  incluso cuando se conecta como **operator** y **node**.

## Familias comunes de métodos RPC

Esta página no es un volcado completo generado, pero la superficie WS pública es más amplia
que los ejemplos de handshake/auth anteriores. Estas son las principales familias de métodos que el
Gateway expone hoy.

`hello-ok.features.methods` es una lista conservadora de descubrimiento construida a partir de
`src/gateway/server-methods-list.ts` más las exportaciones de métodos de plugins/canales cargados.
Trátala como descubrimiento de características, no como un volcado generado de cada helper invocable
implementado en `src/gateway/server-methods/*.ts`.

### Sistema e identidad

- `health` devuelve la instantánea de salud del gateway en caché o sondeada de forma reciente.
- `status` devuelve el resumen del gateway con estilo `/status`; los campos sensibles se
  incluyen solo para clientes operator con scope de admin.
- `gateway.identity.get` devuelve la identidad del dispositivo del gateway usada por relay y
  los flujos de pairing.
- `system-presence` devuelve la instantánea de presencia actual para dispositivos
  operator/node conectados.
- `system-event` agrega un evento del sistema y puede actualizar/transmitir contexto de presencia.
- `last-heartbeat` devuelve el evento heartbeat persistido más reciente.
- `set-heartbeats` activa o desactiva el procesamiento de heartbeat en el gateway.

### Modelos y uso

- `models.list` devuelve el catálogo de modelos permitido en tiempo de ejecución.
- `usage.status` devuelve resúmenes de ventanas de uso del proveedor/cuota restante.
- `usage.cost` devuelve resúmenes agregados de uso de costos para un rango de fechas.
- `doctor.memory.status` devuelve el estado de preparación de vector-memory / embeddings para el
  workspace activo del agente predeterminado.
- `sessions.usage` devuelve resúmenes de uso por sesión.
- `sessions.usage.timeseries` devuelve series temporales de uso para una sesión.
- `sessions.usage.logs` devuelve entradas de log de uso para una sesión.

### Canales y helpers de login

- `channels.status` devuelve resúmenes de estado de canales/plugins incluidos + empaquetados.
- `channels.logout` cierra sesión en un canal/cuenta específicos cuando el canal
  admite cierre de sesión.
- `web.login.start` inicia un flujo de login QR/web para el proveedor actual de canal web
  compatible con QR.
- `web.login.wait` espera a que ese flujo de login QR/web se complete e inicia el
  canal si tiene éxito.
- `push.test` envía un push APNs de prueba a un nodo iOS registrado.
- `voicewake.get` devuelve los disparadores de palabra de activación almacenados.
- `voicewake.set` actualiza los disparadores de palabra de activación y transmite el cambio.

### Mensajería y logs

- `send` es el RPC directo de entrega saliente para envíos dirigidos a canal/cuenta/hilo
  fuera del ejecutor de chat.
- `logs.tail` devuelve la cola configurada del log de archivos del gateway con controles de cursor/límite y
  bytes máximos.

### Talk y TTS

- `talk.config` devuelve la carga efectiva de configuración de Talk; `includeSecrets`
  requiere `operator.talk.secrets` (o `operator.admin`).
- `talk.mode` establece/transmite el estado actual del modo Talk para clientes de WebChat/Control UI.
- `talk.speak` sintetiza voz mediante el proveedor activo de voz de Talk.
- `tts.status` devuelve el estado de TTS habilitado, el proveedor activo, los proveedores de respaldo
  y el estado de configuración del proveedor.
- `tts.providers` devuelve el inventario visible de proveedores de TTS.
- `tts.enable` y `tts.disable` activan o desactivan el estado de preferencia de TTS.
- `tts.setProvider` actualiza el proveedor de TTS preferido.
- `tts.convert` ejecuta una conversión puntual de texto a voz.

### Secrets, config, update y wizard

- `secrets.reload` vuelve a resolver los SecretRefs activos e intercambia el estado secreto en tiempo de ejecución
  solo si todo se completa con éxito.
- `secrets.resolve` resuelve asignaciones de secretos dirigidas por comando para un conjunto específico
  de comando/destino.
- `config.get` devuelve la instantánea actual de configuración y el hash.
- `config.set` escribe una carga de configuración validada.
- `config.patch` fusiona una actualización parcial de configuración.
- `config.apply` valida + reemplaza la carga completa de configuración.
- `config.schema` devuelve la carga del esquema activo de configuración usada por Control UI y
  herramientas CLI: esquema, `uiHints`, versión y metadatos de generación, incluidos
  metadatos de esquema de plugins + canales cuando el runtime puede cargarlos. El esquema
  incluye metadatos de campo `title` / `description` derivados de las mismas etiquetas
  y texto de ayuda usados por la UI, incluidos objeto anidado, wildcard, elemento de array
  y ramas de composición `anyOf` / `oneOf` / `allOf` cuando existe documentación
  de campo coincidente.
- `config.schema.lookup` devuelve una carga de búsqueda acotada por ruta para una ruta de configuración:
  ruta normalizada, un nodo superficial del esquema, una sugerencia coincidente + `hintPath`, y
  resúmenes inmediatos de hijos para navegación UI/CLI.
  - Los nodos del esquema de búsqueda conservan la documentación orientada al usuario y los campos comunes
    de validación: `title`, `description`, `type`, `enum`, `const`, `format`, `pattern`,
    límites numéricos/de string/de array/de objeto, y flags booleanos como
    `additionalProperties`, `deprecated`, `readOnly`, `writeOnly`.
  - Los resúmenes de hijos exponen `key`, `path` normalizada, `type`, `required`,
    `hasChildren`, además de `hint` / `hintPath`.
- `update.run` ejecuta el flujo de actualización del gateway y programa un reinicio solo cuando
  la actualización en sí tuvo éxito.
- `wizard.start`, `wizard.next`, `wizard.status` y `wizard.cancel` exponen el
  asistente de onboarding por WS RPC.

### Familias principales existentes

#### Helpers de agente y workspace

- `agents.list` devuelve las entradas de agentes configuradas.
- `agents.create`, `agents.update` y `agents.delete` administran registros de agentes y
  la conexión del workspace.
- `agents.files.list`, `agents.files.get` y `agents.files.set` administran los
  archivos bootstrap del workspace expuestos para un agente.
- `agent.identity.get` devuelve la identidad efectiva del asistente para un agente o
  sesión.
- `agent.wait` espera a que una ejecución termine y devuelve la instantánea terminal cuando
  está disponible.

#### Control de sesión

- `sessions.list` devuelve el índice actual de sesiones.
- `sessions.subscribe` y `sessions.unsubscribe` activan o desactivan las suscripciones a eventos de cambio de sesión
  para el cliente WS actual.
- `sessions.messages.subscribe` y `sessions.messages.unsubscribe` activan o desactivan
  las suscripciones a eventos de transcripción/mensajes para una sesión.
- `sessions.preview` devuelve vistas previas acotadas de transcripciones para claves de sesión
  específicas.
- `sessions.resolve` resuelve o canoniza un destino de sesión.
- `sessions.create` crea una nueva entrada de sesión.
- `sessions.send` envía un mensaje a una sesión existente.
- `sessions.steer` es la variante de interrumpir y redirigir para una sesión activa.
- `sessions.abort` aborta el trabajo activo de una sesión.
- `sessions.patch` actualiza metadatos/anulaciones de la sesión.
- `sessions.reset`, `sessions.delete` y `sessions.compact` realizan tareas de mantenimiento
  de sesión.
- `sessions.get` devuelve la fila completa de la sesión almacenada.
- la ejecución del chat sigue usando `chat.history`, `chat.send`, `chat.abort` y
  `chat.inject`.
- `chat.history` está normalizado para visualización en clientes UI: las etiquetas de directiva inline se
  eliminan del texto visible, las cargas XML de llamadas a herramientas en texto plano (incluyendo
  `<tool_call>...</tool_call>`, `<function_call>...</function_call>`,
  `<tool_calls>...</tool_calls>`, `<function_calls>...</function_calls>` y
  bloques truncados de llamadas a herramientas) y los tokens de control del modelo filtrados en ASCII/de ancho completo
  se eliminan, se omiten las filas del asistente compuestas solo por tokens silenciosos como `NO_REPLY` /
  `no_reply`, y las filas sobredimensionadas pueden reemplazarse con marcadores de posición.

#### Emparejamiento de dispositivos y tokens de dispositivo

- `device.pair.list` devuelve dispositivos emparejados pendientes y aprobados.
- `device.pair.approve`, `device.pair.reject` y `device.pair.remove` administran
  los registros de emparejamiento de dispositivos.
- `device.token.rotate` rota un token de dispositivo emparejado dentro de sus límites aprobados
  de role y scope.
- `device.token.revoke` revoca un token de dispositivo emparejado.

#### Emparejamiento de nodos, invoke y trabajo pendiente

- `node.pair.request`, `node.pair.list`, `node.pair.approve`,
  `node.pair.reject` y `node.pair.verify` cubren el emparejamiento de nodos y la
  verificación bootstrap.
- `node.list` y `node.describe` devuelven el estado de nodos conocidos/conectados.
- `node.rename` actualiza la etiqueta de un nodo emparejado.
- `node.invoke` reenvía un comando a un nodo conectado.
- `node.invoke.result` devuelve el resultado de una solicitud invoke.
- `node.event` transporta eventos originados en el nodo de vuelta al gateway.
- `node.canvas.capability.refresh` actualiza tokens de capacidad de canvas con scope.
- `node.pending.pull` y `node.pending.ack` son las API de cola para nodos conectados.
- `node.pending.enqueue` y `node.pending.drain` administran trabajo pendiente duradero
  para nodos desconectados/sin conexión.

#### Familias de aprobaciones

- `exec.approval.request`, `exec.approval.get`, `exec.approval.list` y
  `exec.approval.resolve` cubren solicitudes puntuales de aprobación exec más la
  búsqueda/repetición de aprobaciones pendientes.
- `exec.approval.waitDecision` espera una aprobación exec pendiente y devuelve
  la decisión final (o `null` en caso de timeout).
- `exec.approvals.get` y `exec.approvals.set` administran instantáneas de la política
  de aprobación exec del gateway.
- `exec.approvals.node.get` y `exec.approvals.node.set` administran la política local del nodo para exec
  mediante comandos relay del nodo.
- `plugin.approval.request`, `plugin.approval.list`,
  `plugin.approval.waitDecision` y `plugin.approval.resolve` cubren
  flujos de aprobación definidos por plugins.

#### Otras familias principales

- automatización:
  - `wake` programa una inyección de texto de activación inmediata o en el próximo heartbeat
  - `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`,
    `cron.run`, `cron.runs`
- Skills/herramientas: `commands.list`, `skills.*`, `tools.catalog`, `tools.effective`

### Familias comunes de eventos

- `chat`: actualizaciones de chat de la UI como `chat.inject` y otros
  eventos de chat solo de transcripción.
- `session.message` y `session.tool`: actualizaciones de transcripción/flujo de eventos para una
  sesión suscrita.
- `sessions.changed`: cambió el índice o los metadatos de la sesión.
- `presence`: actualizaciones de la instantánea de presencia del sistema.
- `tick`: evento periódico de keepalive / actividad.
- `health`: actualización de la instantánea de salud del gateway.
- `heartbeat`: actualización del flujo de eventos heartbeat.
- `cron`: evento de cambio de ejecución/trabajo cron.
- `shutdown`: notificación de apagado del gateway.
- `node.pair.requested` / `node.pair.resolved`: ciclo de vida del emparejamiento de nodos.
- `node.invoke.request`: difusión de solicitud invoke del nodo.
- `device.pair.requested` / `device.pair.resolved`: ciclo de vida del dispositivo emparejado.
- `voicewake.changed`: cambió la configuración de los disparadores de palabra de activación.
- `exec.approval.requested` / `exec.approval.resolved`: ciclo de vida de la aprobación exec.
- `plugin.approval.requested` / `plugin.approval.resolved`: ciclo de vida de la aprobación de plugins.

### Métodos helper de nodo

- Los nodos pueden llamar a `skills.bins` para obtener la lista actual de ejecutables de Skills
  para comprobaciones de autoallow.

### Métodos helper de operator

- Los operator pueden llamar a `commands.list` (`operator.read`) para obtener el inventario de comandos en runtime de un agente.
  - `agentId` es opcional; omítelo para leer el workspace del agente predeterminado.
  - `scope` controla a qué superficie apunta el `name` principal:
    - `text` devuelve el token principal del comando de texto sin la `/` inicial
    - `native` y la ruta predeterminada `both` devuelven nombres nativos dependientes del proveedor
      cuando están disponibles
  - `textAliases` contiene alias exactos con barra, como `/model` y `/m`.
  - `nativeName` contiene el nombre nativo dependiente del proveedor cuando existe.
  - `provider` es opcional y solo afecta el nombre nativo más la disponibilidad de comandos
    nativos del plugin.
  - `includeArgs=false` omite de la respuesta los metadatos serializados de argumentos.
- Los operator pueden llamar a `tools.catalog` (`operator.read`) para obtener el catálogo de herramientas en runtime de un
  agente. La respuesta incluye herramientas agrupadas y metadatos de procedencia:
  - `source`: `core` o `plugin`
  - `pluginId`: propietario del plugin cuando `source="plugin"`
  - `optional`: si una herramienta del plugin es opcional
- Los operator pueden llamar a `tools.effective` (`operator.read`) para obtener el inventario efectivo en runtime de herramientas
  para una sesión.
  - `sessionKey` es obligatorio.
  - El gateway deriva el contexto de runtime confiable del lado del servidor a partir de la sesión, en lugar de aceptar
    contexto de auth o de entrega proporcionado por el llamador.
  - La respuesta tiene scope de sesión y refleja lo que la conversación activa puede usar en este momento,
    incluidas herramientas de core, plugin y canal.
- Los operator pueden llamar a `skills.status` (`operator.read`) para obtener el inventario visible
  de Skills para un agente.
  - `agentId` es opcional; omítelo para leer el workspace del agente predeterminado.
  - La respuesta incluye elegibilidad, requisitos faltantes, comprobaciones de configuración y
    opciones de instalación saneadas sin exponer valores secretos sin procesar.
- Los operator pueden llamar a `skills.search` y `skills.detail` (`operator.read`) para obtener
  metadatos de descubrimiento de ClawHub.
- Los operator pueden llamar a `skills.install` (`operator.admin`) en dos modos:
  - Modo ClawHub: `{ source: "clawhub", slug, version?, force? }` instala una
    carpeta de skill en el directorio `skills/` del workspace del agente predeterminado.
  - Modo instalador del gateway: `{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    ejecuta una acción declarada `metadata.openclaw.install` en el host del gateway.
- Los operator pueden llamar a `skills.update` (`operator.admin`) en dos modos:
  - El modo ClawHub actualiza un slug rastreado o todas las instalaciones rastreadas de ClawHub en
    el workspace del agente predeterminado.
  - El modo Config aplica un parche a valores de `skills.entries.<skillKey>` como `enabled`,
    `apiKey` y `env`.

## Aprobaciones exec

- Cuando una solicitud exec necesita aprobación, el gateway transmite `exec.approval.requested`.
- Los clientes operator resuelven llamando a `exec.approval.resolve` (requiere el scope `operator.approvals`).
- Para `host=node`, `exec.approval.request` debe incluir `systemRunPlan` (`argv`/`cwd`/`rawCommand`/metadatos de sesión canónicos). Las solicitudes sin `systemRunPlan` se rechazan.
- Después de la aprobación, las llamadas reenviadas `node.invoke system.run` reutilizan ese
  `systemRunPlan` canónico como contexto autoritativo para comando/cwd/sesión.
- Si un llamador modifica `command`, `rawCommand`, `cwd`, `agentId` o
  `sessionKey` entre prepare y el reenvío final aprobado de `system.run`, el
  gateway rechaza la ejecución en lugar de confiar en la carga modificada.

## Respaldo de entrega del agente

- Las solicitudes `agent` pueden incluir `deliver=true` para solicitar entrega saliente.
- `bestEffortDeliver=false` mantiene el comportamiento estricto: los destinos de entrega no resueltos o solo internos devuelven `INVALID_REQUEST`.
- `bestEffortDeliver=true` permite volver a la ejecución solo de sesión cuando no puede resolverse ninguna ruta externa entregable (por ejemplo, sesiones internas/webchat o configuraciones multicanal ambiguas).

## Versionado

- `PROTOCOL_VERSION` está en `src/gateway/protocol/schema.ts`.
- Los clientes envían `minProtocol` + `maxProtocol`; el servidor rechaza incompatibilidades.
- Los esquemas + modelos se generan a partir de definiciones TypeBox:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

## Auth

- La auth del gateway con secreto compartido usa `connect.params.auth.token` o
  `connect.params.auth.password`, según el modo de auth configurado.
- Los modos con identidad, como Tailscale Serve
  (`gateway.auth.allowTailscale: true`) o
  `gateway.auth.mode: "trusted-proxy"` sin loopback,
  satisfacen la comprobación de auth de connect desde encabezados de la solicitud en lugar de `connect.params.auth.*`.
- El modo de ingreso privado `gateway.auth.mode: "none"` omite por completo la auth de connect con secreto compartido; no expongas ese modo en ingresos públicos/no confiables.
- Después del emparejamiento, el Gateway emite un **token de dispositivo** con scope para el
  role + scopes de la conexión. Se devuelve en `hello-ok.auth.deviceToken` y el cliente
  debe persistirlo para conexiones futuras.
- Los clientes deben persistir el `hello-ok.auth.deviceToken` principal después de cualquier
  conexión correcta.
- Al reconectarse con ese token de dispositivo **almacenado**, también deben reutilizarse el conjunto de scopes aprobados
  almacenado para ese token. Esto preserva el acceso de lectura/sondeo/estado
  que ya se había concedido y evita reducir silenciosamente las reconexiones a un
  scope implícito más estrecho de solo admin.
- La precedencia normal de auth de connect es primero token/contraseña compartidos explícitos, luego
  `deviceToken` explícito, después token por dispositivo almacenado y, por último, token bootstrap.
- Las entradas adicionales de `hello-ok.auth.deviceTokens` son tokens de traspaso bootstrap.
  Persístelas solo cuando la conexión usó auth bootstrap en un transporte confiable
  como `wss://` o loopback/emparejamiento local.
- Si un cliente proporciona un `deviceToken` **explícito** o `scopes` explícitos, ese
  conjunto de scopes solicitado por el llamador sigue siendo autoritativo; los scopes en caché solo se
  reutilizan cuando el cliente reutiliza el token almacenado por dispositivo.
- Los tokens de dispositivo pueden rotarse/revocarse mediante `device.token.rotate` y
  `device.token.revoke` (requiere el scope `operator.pairing`).
- La emisión/rotación de tokens permanece acotada al conjunto de roles aprobados registrado en
  la entrada de emparejamiento de ese dispositivo; rotar un token no puede ampliar el dispositivo a un
  role que la aprobación del emparejamiento nunca concedió.
- Para sesiones de token de dispositivo emparejado, la administración del dispositivo tiene scope propio salvo que el
  llamador también tenga `operator.admin`: los llamadores que no son admin solo pueden eliminar/revocar/rotar
  su **propia** entrada de dispositivo.
- `device.token.rotate` también comprueba el conjunto solicitado de scopes de operator frente a los
  scopes actuales de la sesión del llamador. Los llamadores que no son admin no pueden rotar un token a
  un conjunto más amplio de scopes de operator del que ya poseen.
- Los fallos de auth incluyen `error.details.code` más sugerencias de recuperación:
  - `error.details.canRetryWithDeviceToken` (boolean)
  - `error.details.recommendedNextStep` (`retry_with_device_token`, `update_auth_configuration`, `update_auth_credentials`, `wait_then_retry`, `review_auth_configuration`)
- Comportamiento del cliente para `AUTH_TOKEN_MISMATCH`:
  - Los clientes confiables pueden intentar un único reintento acotado con un token por dispositivo en caché.
  - Si ese reintento falla, los clientes deben detener los bucles automáticos de reconexión y mostrar orientación de acción al operator.

## Identidad del dispositivo + emparejamiento

- Los nodos deben incluir una identidad de dispositivo estable (`device.id`) derivada de la
  huella de un par de claves.
- Los gateways emiten tokens por dispositivo + role.
- Se requieren aprobaciones de emparejamiento para nuevos IDs de dispositivo, a menos que la autoaprobación local
  esté habilitada.
- La autoaprobación de emparejamiento se centra en conexiones directas de local loopback.
- OpenClaw también tiene una ruta estrecha de autoconexión local de backend/contenedor para
  flujos helper confiables con secreto compartido.
- Las conexiones tailnet o LAN en el mismo host siguen tratándose como remotas para el emparejamiento y
  requieren aprobación.
- Todos los clientes WS deben incluir identidad `device` durante `connect` (operator + node).
  Control UI puede omitirla solo en estos modos:
  - `gateway.controlUi.allowInsecureAuth=true` para compatibilidad con HTTP inseguro solo en localhost.
  - autenticación correcta de operator de Control UI con `gateway.auth.mode: "trusted-proxy"`.
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true` (opción de emergencia, degradación grave de seguridad).
- Todas las conexiones deben firmar el nonce `connect.challenge` proporcionado por el servidor.

### Diagnósticos de migración de auth de dispositivo

Para clientes heredados que todavía usan el comportamiento de firma previo al desafío, `connect` ahora devuelve
códigos de detalle `DEVICE_AUTH_*` en `error.details.code` con un `error.details.reason` estable.

Fallos comunes de migración:

| Mensaje                     | details.code                     | details.reason           | Significado                                        |
| --------------------------- | -------------------------------- | ------------------------ | -------------------------------------------------- |
| `device nonce required`     | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | El cliente omitió `device.nonce` (o lo envió vacío). |
| `device nonce mismatch`     | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | El cliente firmó con un nonce obsoleto/incorrecto. |
| `device signature invalid`  | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | La carga de la firma no coincide con la carga v2.  |
| `device signature expired`  | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | La marca de tiempo firmada está fuera del desfase permitido. |
| `device identity mismatch`  | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id` no coincide con la huella de la clave pública. |
| `device public key invalid` | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | Falló el formato/canonicalización de la clave pública. |

Objetivo de la migración:

- Espera siempre a `connect.challenge`.
- Firma la carga v2 que incluye el nonce del servidor.
- Envía el mismo nonce en `connect.params.device.nonce`.
- La carga de firma preferida es `v3`, que vincula `platform` y `deviceFamily`
  además de los campos de dispositivo/cliente/role/scopes/token/nonce.
- Las firmas heredadas `v2` siguen aceptándose por compatibilidad, pero la fijación de metadatos
  del dispositivo emparejado sigue controlando la política de comandos al reconectar.

## TLS + pinning

- TLS es compatible con conexiones WS.
- Los clientes pueden fijar opcionalmente la huella del certificado del gateway (consulta la configuración `gateway.tls`
  más `gateway.remote.tlsFingerprint` o la CLI `--tls-fingerprint`).

## Alcance

Este protocolo expone la **API completa del gateway** (status, canales, modelos, chat,
agent, sesiones, nodos, aprobaciones, etc.). La superficie exacta está definida por los
esquemas TypeBox en `src/gateway/protocol/schema.ts`.
