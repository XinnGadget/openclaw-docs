---
read_when:
    - Necesitas la semántica exacta o los valores predeterminados de la configuración a nivel de campo
    - Estás validando bloques de configuración de canales, modelos, gateway o herramientas
summary: Referencia completa de cada clave de configuración de OpenClaw, valores predeterminados y ajustes de canales
title: Referencia de configuración
x-i18n:
    generated_at: "2026-04-06T05:17:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6ae6c19666f65433361e1c8b100ae710448c8aa055a60c140241a8aea09b98a5
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# Referencia de configuración

Cada campo disponible en `~/.openclaw/openclaw.json`. Para una visión general orientada a tareas, consulta [Configuración](/es/gateway/configuration).

El formato de configuración es **JSON5** (se permiten comentarios y comas finales). Todos los campos son opcionales: OpenClaw usa valores predeterminados seguros cuando se omiten.

---

## Canales

Cada canal se inicia automáticamente cuando existe su sección de configuración (a menos que `enabled: false`).

### Acceso a mensajes directos y grupos

Todos los canales admiten políticas de MD y políticas de grupo:

| Política de MD      | Comportamiento                                                |
| ------------------- | ------------------------------------------------------------- |
| `pairing` (predeterminada) | Los remitentes desconocidos reciben un código de vinculación de un solo uso; el propietario debe aprobar |
| `allowlist`         | Solo remitentes en `allowFrom` (o en el almacén de permitidos emparejados) |
| `open`              | Permitir todos los MD entrantes (requiere `allowFrom: ["*"]`) |
| `disabled`          | Ignorar todos los MD entrantes                                |

| Política de grupo     | Comportamiento                                         |
| --------------------- | ------------------------------------------------------ |
| `allowlist` (predeterminada) | Solo grupos que coincidan con la allowlist configurada |
| `open`                | Omitir las allowlists de grupo (la exigencia de mención sigue aplicándose) |
| `disabled`            | Bloquear todos los mensajes de grupo/sala              |

<Note>
`channels.defaults.groupPolicy` establece el valor predeterminado cuando `groupPolicy` de un proveedor no está configurado.
Los códigos de vinculación expiran después de 1 hora. Las solicitudes pendientes de vinculación de MD están limitadas a **3 por canal**.
Si falta por completo un bloque de proveedor (`channels.<provider>` ausente), la política de grupo en tiempo de ejecución vuelve a `allowlist` (fallo cerrado) con una advertencia al iniciar.
</Note>

### Sobrescrituras de modelo por canal

Usa `channels.modelByChannel` para fijar IDs de canal específicos a un modelo. Los valores aceptan `provider/model` o alias de modelo configurados. La asignación del canal se aplica cuando una sesión no tiene ya una sobrescritura de modelo (por ejemplo, establecida mediante `/model`).

```json5
{
  channels: {
    modelByChannel: {
      discord: {
        "123456789012345678": "anthropic/claude-opus-4-6",
      },
      slack: {
        C1234567890: "openai/gpt-4.1",
      },
      telegram: {
        "-1001234567890": "openai/gpt-4.1-mini",
        "-1001234567890:topic:99": "anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

### Valores predeterminados de canal y heartbeat

Usa `channels.defaults` para compartir el comportamiento de política de grupo y heartbeat entre proveedores:

```json5
{
  channels: {
    defaults: {
      groupPolicy: "allowlist", // open | allowlist | disabled
      contextVisibility: "all", // all | allowlist | allowlist_quote
      heartbeat: {
        showOk: false,
        showAlerts: true,
        useIndicator: true,
      },
    },
  },
}
```

- `channels.defaults.groupPolicy`: política de grupo de respaldo cuando `groupPolicy` a nivel de proveedor no está configurado.
- `channels.defaults.contextVisibility`: modo predeterminado de visibilidad de contexto suplementario para todos los canales. Valores: `all` (predeterminado, incluir todo el contexto citado/de hilo/historial), `allowlist` (incluir solo contexto de remitentes en allowlist), `allowlist_quote` (igual que allowlist pero manteniendo el contexto explícito de cita/respuesta). Sobrescritura por canal: `channels.<channel>.contextVisibility`.
- `channels.defaults.heartbeat.showOk`: incluir estados de canales saludables en la salida de heartbeat.
- `channels.defaults.heartbeat.showAlerts`: incluir estados degradados/con error en la salida de heartbeat.
- `channels.defaults.heartbeat.useIndicator`: mostrar salida de heartbeat compacta con estilo de indicador.

### WhatsApp

WhatsApp se ejecuta a través del canal web del gateway (Baileys Web). Se inicia automáticamente cuando existe una sesión vinculada.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // doble marca azul (false en modo self-chat)
      groups: {
        "*": { requireMention: true },
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
  web: {
    enabled: true,
    heartbeatSeconds: 60,
    reconnect: {
      initialMs: 2000,
      maxMs: 120000,
      factor: 1.4,
      jitter: 0.2,
      maxAttempts: 0,
    },
  },
}
```

<Accordion title="WhatsApp con varias cuentas">

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: {},
        personal: {},
        biz: {
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

- Los comandos salientes usan por defecto la cuenta `default` si existe; en caso contrario, la primera ID de cuenta configurada (ordenada).
- `channels.whatsapp.defaultAccount` opcional sobrescribe esa selección predeterminada de cuenta si coincide con una ID de cuenta configurada.
- El directorio heredado de autenticación Baileys de una sola cuenta se migra mediante `openclaw doctor` a `whatsapp/default`.
- Sobrescrituras por cuenta: `channels.whatsapp.accounts.<id>.sendReadReceipts`, `channels.whatsapp.accounts.<id>.dmPolicy`, `channels.whatsapp.accounts.<id>.allowFrom`.

</Accordion>

### Telegram

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groups: {
        "*": { requireMention: true },
        "-1001234567890": {
          allowFrom: ["@admin"],
          systemPrompt: "Mantén las respuestas breves.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Mantente en el tema.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Respaldo de Git" },
        { command: "generate", description: "Crear una imagen" },
      ],
      historyLimit: 50,
      replyToMode: "first", // off | first | all | batched
      linkPreview: true,
      streaming: "partial", // off | partial | block | progress (predeterminado: off; actívalo explícitamente para evitar límites de frecuencia de edición de vista previa)
      actions: { reactions: true, sendMessage: true },
      reactionNotifications: "own", // off | own | all
      mediaMaxMb: 100,
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: {
        autoSelectFamily: true,
        dnsResultOrder: "ipv4first",
      },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

- Token del bot: `channels.telegram.botToken` o `channels.telegram.tokenFile` (solo archivo regular; se rechazan symlinks), con `TELEGRAM_BOT_TOKEN` como respaldo para la cuenta predeterminada.
- `channels.telegram.defaultAccount` opcional sobrescribe la selección de cuenta predeterminada cuando coincide con una ID de cuenta configurada.
- En configuraciones con varias cuentas (2 o más IDs de cuenta), establece un valor predeterminado explícito (`channels.telegram.defaultAccount` o `channels.telegram.accounts.default`) para evitar el enrutamiento por respaldo; `openclaw doctor` advierte cuando falta o es inválido.
- `configWrites: false` bloquea escrituras de configuración iniciadas desde Telegram (migraciones de ID de supergrupo, `/config set|unset`).
- Las entradas `bindings[]` de nivel superior con `type: "acp"` configuran enlaces ACP persistentes para temas de foros (usa el formato canónico `chatId:topic:topicId` en `match.peer.id`). La semántica de campos se comparte en [Agentes ACP](/es/tools/acp-agents#channel-specific-settings).
- Las vistas previas de streaming de Telegram usan `sendMessage` + `editMessageText` (funciona en chats directos y de grupo).
- Política de reintento: consulta [Política de reintento](/es/concepts/retry).

### Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 100,
      allowBots: false,
      actions: {
        reactions: true,
        stickers: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        roles: false,
        channelInfo: true,
        voiceStatus: true,
        events: true,
        moderation: false,
      },
      replyToMode: "off", // off | first | all | batched
      dmPolicy: "pairing",
      allowFrom: ["1234567890", "123456789012345678"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["openclaw-dm"] },
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
          ignoreOtherMentions: true,
          reactionNotifications: "own",
          users: ["987654321098765432"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["docs"],
              systemPrompt: "Solo respuestas breves.",
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length", // length | newline
      streaming: "off", // off | partial | block | progress (progress se mapea a partial en Discord)
      maxLinesPerMessage: 17,
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // activación opcional para sessions_spawn({ thread: true })
      },
      voice: {
        enabled: true,
        autoJoin: [
          {
            guildId: "123456789012345678",
            channelId: "234567890123456789",
          },
        ],
        daveEncryption: true,
        decryptionFailureTolerance: 24,
        tts: {
          provider: "openai",
          openai: { voice: "alloy" },
        },
      },
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["987654321098765432"],
        agentFilter: ["default"],
        sessionFilter: ["discord:"],
        target: "dm", // dm | channel | both
        cleanupAfterResolve: false,
      },
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

- Token: `channels.discord.token`, con `DISCORD_BOT_TOKEN` como respaldo para la cuenta predeterminada.
- Las llamadas salientes directas que proporcionan un `token` explícito de Discord usan ese token para la llamada; los ajustes de reintento/política de cuenta siguen viniendo de la cuenta seleccionada en la instantánea activa de tiempo de ejecución.
- `channels.discord.defaultAccount` opcional sobrescribe la selección de cuenta predeterminada cuando coincide con una ID de cuenta configurada.
- Usa `user:<id>` (MD) o `channel:<id>` (canal de guild) para los destinos de entrega; se rechazan los IDs numéricos sin prefijo.
- Los slugs de guild están en minúsculas con espacios reemplazados por `-`; las claves de canal usan el nombre en slug (sin `#`). Prefiere IDs de guild.
- Los mensajes escritos por bots se ignoran de forma predeterminada. `allowBots: true` los habilita; usa `allowBots: "mentions"` para aceptar solo mensajes de bots que mencionen al bot (los mensajes propios siguen filtrándose).
- `channels.discord.guilds.<id>.ignoreOtherMentions` (y sus sobrescrituras de canal) descarta mensajes que mencionan a otro usuario o rol pero no al bot (excluyendo @everyone/@here).
- `maxLinesPerMessage` (predeterminado 17) divide mensajes altos incluso si tienen menos de 2000 caracteres.
- `channels.discord.threadBindings` controla el enrutamiento ligado a hilos de Discord:
  - `enabled`: sobrescritura de Discord para funciones de sesión ligadas a hilos (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`, y entrega/enrutamiento vinculados)
  - `idleHours`: sobrescritura de Discord para desenfoque automático por inactividad en horas (`0` lo desactiva)
  - `maxAgeHours`: sobrescritura de Discord para antigüedad máxima estricta en horas (`0` lo desactiva)
  - `spawnSubagentSessions`: interruptor opcional para creación/enlace automático de hilos con `sessions_spawn({ thread: true })`
- Las entradas `bindings[]` de nivel superior con `type: "acp"` configuran enlaces ACP persistentes para canales e hilos (usa el id de canal/hilo en `match.peer.id`). La semántica de campos se comparte en [Agentes ACP](/es/tools/acp-agents#channel-specific-settings).
- `channels.discord.ui.components.accentColor` establece el color de acento para contenedores de componentes v2 de Discord.
- `channels.discord.voice` habilita conversaciones en canales de voz de Discord y sobrescrituras opcionales de autoentrada + TTS.
- `channels.discord.voice.daveEncryption` y `channels.discord.voice.decryptionFailureTolerance` se transfieren a las opciones DAVE de `@discordjs/voice` (`true` y `24` de forma predeterminada).
- OpenClaw además intenta recuperar la recepción de voz saliendo y volviendo a entrar en una sesión de voz tras repetidos fallos de descifrado.
- `channels.discord.streaming` es la clave canónica para el modo de streaming. Los valores heredados `streamMode` y booleanos `streaming` se migran automáticamente.
- `channels.discord.autoPresence` asigna la disponibilidad del tiempo de ejecución al estado del bot (healthy => online, degraded => idle, exhausted => dnd) y permite sobrescrituras opcionales de texto de estado.
- `channels.discord.dangerouslyAllowNameMatching` vuelve a habilitar la coincidencia por nombre/tag mutable (modo de compatibilidad break-glass).
- `channels.discord.execApprovals`: entrega nativa de aprobaciones exec en Discord y autorización de aprobadores.
  - `enabled`: `true`, `false` o `"auto"` (predeterminado). En modo auto, las aprobaciones exec se activan cuando se pueden resolver aprobadores desde `approvers` o `commands.ownerAllowFrom`.
  - `approvers`: IDs de usuario de Discord autorizados para aprobar solicitudes exec. Usa `commands.ownerAllowFrom` como respaldo si se omite.
  - `agentFilter`: allowlist opcional de IDs de agente. Omítelo para reenviar aprobaciones para todos los agentes.
  - `sessionFilter`: patrones opcionales de clave de sesión (subcadena o regex).
  - `target`: dónde enviar las solicitudes de aprobación. `"dm"` (predeterminado) las envía a los MD del aprobador, `"channel"` las envía al canal de origen, `"both"` las envía a ambos. Cuando el destino incluye `"channel"`, los botones solo pueden usarlos los aprobadores resueltos.
  - `cleanupAfterResolve`: cuando es `true`, elimina los MD de aprobación después de aprobar, rechazar o agotar el tiempo.

**Modos de notificación de reacciones:** `off` (ninguno), `own` (mensajes del bot, predeterminado), `all` (todos los mensajes), `allowlist` (desde `guilds.<id>.users` en todos los mensajes).

### Google Chat

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url", // app-url | project-number
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890",
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["users/1234567890"],
      },
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": { allow: true, requireMention: true },
      },
      actions: { reactions: true },
      typingIndicator: "message",
      mediaMaxMb: 20,
    },
  },
}
```

- JSON de cuenta de servicio: en línea (`serviceAccount`) o basado en archivo (`serviceAccountFile`).
- También se admite SecretRef para cuenta de servicio (`serviceAccountRef`).
- Variables de entorno de respaldo: `GOOGLE_CHAT_SERVICE_ACCOUNT` o `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- Usa `spaces/<spaceId>` o `users/<userId>` para destinos de entrega.
- `channels.googlechat.dangerouslyAllowNameMatching` vuelve a habilitar la coincidencia mutable de principal de correo electrónico (modo de compatibilidad break-glass).

### Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",
      dmPolicy: "pairing",
      allowFrom: ["U123", "U456", "*"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["G123"] },
      channels: {
        C123: { allow: true, requireMention: true, allowBots: false },
        "#general": {
          allow: true,
          requireMention: true,
          allowBots: false,
          users: ["U123"],
          skills: ["docs"],
          systemPrompt: "Solo respuestas breves.",
        },
      },
      historyLimit: 50,
      allowBots: false,
      reactionNotifications: "own",
      reactionAllowlist: ["U123"],
      replyToMode: "off", // off | first | all | batched
      thread: {
        historyScope: "thread", // thread | channel
        inheritParent: false,
      },
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true,
      },
      slashCommand: {
        enabled: true,
        name: "openclaw",
        sessionPrefix: "slack:slash",
        ephemeral: true,
      },
      typingReaction: "hourglass_flowing_sand",
      textChunkLimit: 4000,
      chunkMode: "length",
      streaming: "partial", // off | partial | block | progress (modo de vista previa)
      nativeStreaming: true, // usar la API nativa de streaming de Slack cuando streaming=partial
      mediaMaxMb: 20,
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["U123"],
        agentFilter: ["default"],
        sessionFilter: ["slack:"],
        target: "dm", // dm | channel | both
      },
    },
  },
}
```

- El **modo socket** requiere tanto `botToken` como `appToken` (`SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` para el respaldo por entorno de la cuenta predeterminada).
- El **modo HTTP** requiere `botToken` más `signingSecret` (en la raíz o por cuenta).
- `botToken`, `appToken`, `signingSecret` y `userToken` aceptan cadenas
  de texto plano u objetos SecretRef.
- Las instantáneas de cuentas de Slack exponen campos por credencial de origen/estado como
  `botTokenSource`, `botTokenStatus`, `appTokenStatus` y, en modo HTTP,
  `signingSecretStatus`. `configured_unavailable` significa que la cuenta está
  configurada mediante SecretRef pero la ruta actual de comando/tiempo de ejecución no pudo
  resolver el valor del secreto.
- `configWrites: false` bloquea escrituras de configuración iniciadas desde Slack.
- `channels.slack.defaultAccount` opcional sobrescribe la selección de cuenta predeterminada cuando coincide con una ID de cuenta configurada.
- `channels.slack.streaming` es la clave canónica para el modo de streaming. Los valores heredados `streamMode` y booleanos `streaming` se migran automáticamente.
- Usa `user:<id>` (MD) o `channel:<id>` para destinos de entrega.

**Modos de notificación de reacciones:** `off`, `own` (predeterminado), `all`, `allowlist` (desde `reactionAllowlist`).

**Aislamiento de sesión por hilo:** `thread.historyScope` es por hilo (predeterminado) o compartido en todo el canal. `thread.inheritParent` copia la transcripción del canal padre a los nuevos hilos.

- `typingReaction` agrega una reacción temporal al mensaje entrante de Slack mientras se ejecuta una respuesta, y luego la elimina al completarse. Usa un shortcode de emoji de Slack como `"hourglass_flowing_sand"`.
- `channels.slack.execApprovals`: entrega nativa de aprobaciones exec en Slack y autorización de aprobadores. Mismo esquema que Discord: `enabled` (`true`/`false`/`"auto"`), `approvers` (IDs de usuario de Slack), `agentFilter`, `sessionFilter` y `target` (`"dm"`, `"channel"` o `"both"`).

| Grupo de acciones | Predeterminado | Notas                    |
| ----------------- | -------------- | ------------------------ |
| reactions         | habilitado     | Reaccionar + listar reacciones |
| messages          | habilitado     | Leer/enviar/editar/eliminar |
| pins              | habilitado     | Fijar/desfijar/listar    |
| memberInfo        | habilitado     | Información de miembro   |
| emojiList         | habilitado     | Lista de emojis personalizados |

### Mattermost

Mattermost se distribuye como plugin: `openclaw plugins install @openclaw/mattermost`.

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
      chatmode: "oncall", // oncall | onmessage | onchar
      oncharPrefixes: [">", "!"],
      groups: {
        "*": { requireMention: true },
        "team-channel-id": { requireMention: false },
      },
      commands: {
        native: true, // activación opcional
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // URL explícita opcional para despliegues detrás de proxy inverso/públicos
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

Modos de chat: `oncall` (responder con mención @, predeterminado), `onmessage` (cada mensaje), `onchar` (mensajes que empiezan con prefijo disparador).

Cuando los comandos nativos de Mattermost están habilitados:

- `commands.callbackPath` debe ser una ruta (por ejemplo `/api/channels/mattermost/command`), no una URL completa.
- `commands.callbackUrl` debe resolverse al endpoint del gateway de OpenClaw y ser accesible desde el servidor de Mattermost.
- Los callbacks nativos de slash se autentican con los tokens por comando devueltos
  por Mattermost durante el registro del slash command. Si el registro falla o no
  se activan comandos, OpenClaw rechaza los callbacks con
  `Unauthorized: invalid command token.`
- Para hosts de callback privados/tailnet/internos, Mattermost puede requerir
  que `ServiceSettings.AllowedUntrustedInternalConnections` incluya el host/dominio del callback.
  Usa valores de host/dominio, no URLs completas.
- `channels.mattermost.configWrites`: permitir o denegar escrituras de configuración iniciadas desde Mattermost.
- `channels.mattermost.requireMention`: requerir `@mention` antes de responder en canales.
- `channels.mattermost.groups.<channelId>.requireMention`: sobrescritura por canal para exigencia de mención (`"*"` para el valor predeterminado).
- `channels.mattermost.defaultAccount` opcional sobrescribe la selección de cuenta predeterminada cuando coincide con una ID de cuenta configurada.

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // enlace de cuenta opcional
      dmPolicy: "pairing",
      allowFrom: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      configWrites: true,
      reactionNotifications: "own", // off | own | all | allowlist
      reactionAllowlist: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      historyLimit: 50,
    },
  },
}
```

**Modos de notificación de reacciones:** `off`, `own` (predeterminado), `all`, `allowlist` (desde `reactionAllowlist`).

- `channels.signal.account`: fija el inicio del canal a una identidad de cuenta de Signal específica.
- `channels.signal.configWrites`: permitir o denegar escrituras de configuración iniciadas desde Signal.
- `channels.signal.defaultAccount` opcional sobrescribe la selección de cuenta predeterminada cuando coincide con una ID de cuenta configurada.

### BlueBubbles

BlueBubbles es la ruta recomendada para iMessage (respaldada por plugin, configurada en `channels.bluebubbles`).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl, password, webhookPath, controles de grupo y acciones avanzadas:
      // consulta /channels/bluebubbles
    },
  },
}
```

- Rutas de claves principales cubiertas aquí: `channels.bluebubbles`, `channels.bluebubbles.dmPolicy`.
- `channels.bluebubbles.defaultAccount` opcional sobrescribe la selección de cuenta predeterminada cuando coincide con una ID de cuenta configurada.
- Las entradas `bindings[]` de nivel superior con `type: "acp"` pueden vincular conversaciones de BlueBubbles a sesiones ACP persistentes. Usa un handle o cadena de destino de BlueBubbles (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) en `match.peer.id`. Semántica compartida de campos: [Agentes ACP](/es/tools/acp-agents#channel-specific-settings).
- La configuración completa del canal BlueBubbles está documentada en [BlueBubbles](/es/channels/bluebubbles).

### iMessage

OpenClaw ejecuta `imsg rpc` (JSON-RPC sobre stdio). No requiere daemon ni puerto.

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host",
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123"],
      historyLimit: 50,
      includeAttachments: false,
      attachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      remoteAttachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      mediaMaxMb: 16,
      service: "auto",
      region: "US",
    },
  },
}
```

- `channels.imessage.defaultAccount` opcional sobrescribe la selección de cuenta predeterminada cuando coincide con una ID de cuenta configurada.

- Requiere acceso completo al disco para la base de datos de Mensajes.
- Prefiere destinos `chat_id:<id>`. Usa `imsg chats --limit 20` para listar chats.
- `cliPath` puede apuntar a un wrapper SSH; configura `remoteHost` (`host` o `user@host`) para obtener adjuntos por SCP.
- `attachmentRoots` y `remoteAttachmentRoots` restringen las rutas de adjuntos entrantes (predeterminado: `/Users/*/Library/Messages/Attachments`).
- SCP usa verificación estricta de clave de host, así que asegúrate de que la clave del host de retransmisión ya exista en `~/.ssh/known_hosts`.
- `channels.imessage.configWrites`: permitir o denegar escrituras de configuración iniciadas desde iMessage.
- Las entradas `bindings[]` de nivel superior con `type: "acp"` pueden vincular conversaciones de iMessage a sesiones ACP persistentes. Usa un handle normalizado o un destino explícito de chat (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) en `match.peer.id`. Semántica compartida de campos: [Agentes ACP](/es/tools/acp-agents#channel-specific-settings).

<Accordion title="Ejemplo de wrapper SSH para iMessage">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix está respaldado por extensiones y se configura en `channels.matrix`.

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
      encryption: true,
      initialSyncLimit: 20,
      defaultAccount: "ops",
      accounts: {
        ops: {
          name: "Ops",
          userId: "@ops:example.org",
          accessToken: "syt_ops_xxx",
        },
        alerts: {
          userId: "@alerts:example.org",
          password: "secret",
          proxy: "http://127.0.0.1:7891",
        },
      },
    },
  },
}
```

- La autenticación por token usa `accessToken`; la autenticación por contraseña usa `userId` + `password`.
- `channels.matrix.proxy` enruta el tráfico HTTP de Matrix a través de un proxy HTTP(S) explícito. Las cuentas con nombre pueden sobrescribirlo con `channels.matrix.accounts.<id>.proxy`.
- `channels.matrix.allowPrivateNetwork` permite homeservers privados/internos. `proxy` y `allowPrivateNetwork` son controles independientes.
- `channels.matrix.defaultAccount` selecciona la cuenta preferida en configuraciones de varias cuentas.
- `channels.matrix.execApprovals`: entrega nativa de aprobaciones exec en Matrix y autorización de aprobadores.
  - `enabled`: `true`, `false` o `"auto"` (predeterminado). En modo auto, las aprobaciones exec se activan cuando se pueden resolver aprobadores desde `approvers` o `commands.ownerAllowFrom`.
  - `approvers`: IDs de usuario de Matrix (por ejemplo `@owner:example.org`) autorizados para aprobar solicitudes exec.
  - `agentFilter`: allowlist opcional de IDs de agente. Omítelo para reenviar aprobaciones para todos los agentes.
  - `sessionFilter`: patrones opcionales de clave de sesión (subcadena o regex).
  - `target`: dónde enviar las solicitudes de aprobación. `"dm"` (predeterminado), `"channel"` (sala de origen) o `"both"`.
  - Sobrescrituras por cuenta: `channels.matrix.accounts.<id>.execApprovals`.
- `channels.matrix.dm.sessionScope` controla cómo se agrupan los MD de Matrix en sesiones: `per-user` (predeterminado) comparte por par enrutado, mientras que `per-room` aísla cada sala de MD.
- Las sondas de estado de Matrix y las búsquedas activas en el directorio usan la misma política de proxy que el tráfico en tiempo de ejecución.
- La configuración completa de Matrix, las reglas de destino y los ejemplos de instalación están documentados en [Matrix](/es/channels/matrix).

### Microsoft Teams

Microsoft Teams está respaldado por extensiones y se configura en `channels.msteams`.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId, appPassword, tenantId, webhook, políticas de equipo/canal:
      // consulta /channels/msteams
    },
  },
}
```

- Rutas de claves principales cubiertas aquí: `channels.msteams`, `channels.msteams.configWrites`.
- La configuración completa de Teams (credenciales, webhook, política de MD/grupo, sobrescrituras por equipo/canal) está documentada en [Microsoft Teams](/es/channels/msteams).

### IRC

IRC está respaldado por extensiones y se configura en `channels.irc`.

```json5
{
  channels: {
    irc: {
      enabled: true,
      dmPolicy: "pairing",
      configWrites: true,
      nickserv: {
        enabled: true,
        service: "NickServ",
        password: "${IRC_NICKSERV_PASSWORD}",
        register: false,
        registerEmail: "bot@example.com",
      },
    },
  },
}
```

- Rutas de claves principales cubiertas aquí: `channels.irc`, `channels.irc.dmPolicy`, `channels.irc.configWrites`, `channels.irc.nickserv.*`.
- `channels.irc.defaultAccount` opcional sobrescribe la selección de cuenta predeterminada cuando coincide con una ID de cuenta configurada.
- La configuración completa del canal IRC (host/puerto/TLS/canales/allowlists/exigencia de mención) está documentada en [IRC](/es/channels/irc).

### Varias cuentas (todos los canales)

Ejecuta varias cuentas por canal (cada una con su propio `accountId`):

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "Bot principal",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "Bot de alertas",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- `default` se usa cuando se omite `accountId` (CLI + enrutamiento).
- Los tokens por entorno solo se aplican a la cuenta **predeterminada**.
- Los ajustes base del canal se aplican a todas las cuentas salvo sobrescritura por cuenta.
- Usa `bindings[].match.accountId` para enrutar cada cuenta a un agente distinto.
- Si agregas una cuenta no predeterminada mediante `openclaw channels add` (o la incorporación del canal) cuando todavía usas una configuración de canal de una sola cuenta en nivel superior, OpenClaw primero promociona los valores de una sola cuenta con ámbito de cuenta al mapa de cuentas del canal para que la cuenta original siga funcionando. La mayoría de los canales los mueven a `channels.<channel>.accounts.default`; Matrix puede conservar en cambio un destino nombrado/predeterminado existente que coincida.
- Los enlaces existentes solo de canal (sin `accountId`) siguen coincidiendo con la cuenta predeterminada; los enlaces con ámbito de cuenta siguen siendo opcionales.
- `openclaw doctor --fix` también repara formas mixtas moviendo valores de una sola cuenta con ámbito de cuenta de nivel superior a la cuenta promocionada elegida para ese canal. La mayoría de los canales usan `accounts.default`; Matrix puede conservar en cambio un destino nombrado/predeterminado existente que coincida.

### Otros canales de extensiones

Muchos canales de extensiones se configuran como `channels.<id>` y están documentados en sus páginas de canal dedicadas (por ejemplo Feishu, Matrix, LINE, Nostr, Zalo, Nextcloud Talk, Synology Chat y Twitch).
Consulta el índice completo de canales: [Canales](/es/channels).

### Exigencia de mención en chats grupales

Los mensajes de grupo requieren **mención** de forma predeterminada (mención en metadatos o patrones regex seguros). Se aplica a chats grupales de WhatsApp, Telegram, Discord, Google Chat e iMessage.

**Tipos de mención:**

- **Menciones en metadatos**: @menciones nativas de la plataforma. Se ignoran en modo self-chat de WhatsApp.
- **Patrones de texto**: patrones regex seguros en `agents.list[].groupChat.mentionPatterns`. Los patrones inválidos y la repetición anidada insegura se ignoran.
- La exigencia de mención solo se aplica cuando la detección es posible (menciones nativas o al menos un patrón).

```json5
{
  messages: {
    groupChat: { historyLimit: 50 },
  },
  agents: {
    list: [{ id: "main", groupChat: { mentionPatterns: ["@openclaw", "openclaw"] } }],
  },
}
```

`messages.groupChat.historyLimit` establece el valor predeterminado global. Los canales pueden sobrescribirlo con `channels.<channel>.historyLimit` (o por cuenta). Establece `0` para desactivarlo.

#### Límites de historial de MD

```json5
{
  channels: {
    telegram: {
      dmHistoryLimit: 30,
      dms: {
        "123456789": { historyLimit: 50 },
      },
    },
  },
}
```

Resolución: sobrescritura por MD → predeterminado del proveedor → sin límite (se conserva todo).

Compatibles: `telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`.

#### Modo self-chat

Incluye tu propio número en `allowFrom` para habilitar el modo self-chat (ignora las @menciones nativas, solo responde a patrones de texto):

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: { mentionPatterns: ["reisponde", "@openclaw"] },
      },
    ],
  },
}
```

### Comandos (manejo de comandos de chat)

```json5
{
  commands: {
    native: "auto", // registrar comandos nativos cuando sea compatible
    text: true, // analizar /commands en mensajes de chat
    bash: false, // permitir ! (alias: /bash)
    bashForegroundMs: 2000,
    config: false, // permitir /config
    debug: false, // permitir /debug
    restart: false, // permitir /restart + herramienta de reinicio del gateway
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="Detalles de comandos">

- Los comandos de texto deben ser mensajes **independientes** con `/` inicial.
- `native: "auto"` activa comandos nativos para Discord/Telegram y deja Slack desactivado.
- Sobrescribir por canal: `channels.discord.commands.native` (bool o `"auto"`). `false` borra comandos registrados anteriormente.
- `channels.telegram.customCommands` agrega entradas extra al menú del bot de Telegram.
- `bash: true` habilita `! <cmd>` para el shell del host. Requiere `tools.elevated.enabled` y que el remitente esté en `tools.elevated.allowFrom.<channel>`.
- `config: true` habilita `/config` (lee/escribe `openclaw.json`). Para clientes `chat.send` del gateway, las escrituras persistentes `/config set|unset` también requieren `operator.admin`; el modo solo lectura `/config show` sigue disponible para clientes normales con permisos de escritura.
- `channels.<provider>.configWrites` controla las mutaciones de configuración por canal (predeterminado: true).
- Para canales con varias cuentas, `channels.<provider>.accounts.<id>.configWrites` también controla las escrituras que apuntan a esa cuenta (por ejemplo `/allowlist --config --account <id>` o `/config set channels.<provider>.accounts.<id>...`).
- `allowFrom` es por proveedor. Cuando se establece, es la **única** fuente de autorización (se ignoran las allowlists/emparejamiento del canal y `useAccessGroups`).
- `useAccessGroups: false` permite que los comandos omitan las políticas de grupos de acceso cuando `allowFrom` no está configurado.

</Accordion>

---

## Valores predeterminados del agente

### `agents.defaults.workspace`

Predeterminado: `~/.openclaw/workspace`.

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

Raíz opcional del repositorio mostrada en la línea Runtime del system prompt. Si no se establece, OpenClaw la detecta automáticamente subiendo desde el workspace.

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

Allowlist predeterminada opcional de Skills para agentes que no establecen
`agents.list[].skills`.

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // hereda github, weather
      { id: "docs", skills: ["docs-search"] }, // reemplaza los valores predeterminados
      { id: "locked-down", skills: [] }, // sin Skills
    ],
  },
}
```

- Omite `agents.defaults.skills` para permitir Skills sin restricciones de forma predeterminada.
- Omite `agents.list[].skills` para heredar los valores predeterminados.
- Establece `agents.list[].skills: []` para no tener Skills.
- Una lista no vacía en `agents.list[].skills` es el conjunto final para ese agente;
  no se fusiona con los valores predeterminados.

### `agents.defaults.skipBootstrap`

Desactiva la creación automática de archivos bootstrap del workspace (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`).

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

Controla cuándo se inyectan los archivos bootstrap del workspace en el system prompt. Predeterminado: `"always"`.

- `"continuation-skip"`: los turnos seguros de continuación (después de una respuesta completada del asistente) omiten la reinyección del bootstrap del workspace, reduciendo el tamaño del prompt. Las ejecuciones de heartbeat y los reintentos posteriores a la compactación siguen reconstruyendo el contexto.

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

Máximo de caracteres por archivo bootstrap del workspace antes del truncamiento. Predeterminado: `20000`.

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

Máximo total de caracteres inyectados entre todos los archivos bootstrap del workspace. Predeterminado: `150000`.

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

Controla el texto de advertencia visible para el agente cuando se trunca el contexto bootstrap.
Predeterminado: `"once"`.

- `"off"`: nunca inyectar texto de advertencia en el system prompt.
- `"once"`: inyectar la advertencia una vez por firma única de truncamiento (recomendado).
- `"always"`: inyectar la advertencia en cada ejecución cuando exista truncamiento.

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

Tamaño máximo en píxeles para el lado más largo de la imagen en bloques de imagen de transcript/tool antes de llamar al proveedor.
Predeterminado: `1200`.

Los valores más bajos suelen reducir el uso de tokens de visión y el tamaño de la carga útil de la solicitud.
Los valores más altos conservan más detalle visual.

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

Zona horaria para el contexto del system prompt (no para marcas de tiempo de mensajes). Usa la zona horaria del host como respaldo.

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

Formato horario en el system prompt. Predeterminado: `auto` (preferencia del SO).

```json5
{
  agents: { defaults: { timeFormat: "auto" } }, // auto | 12 | 24
}
```

### `agents.defaults.model`

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview"],
      },
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-i2v"],
      },
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.4-mini"],
      },
      params: { cacheRetention: "long" }, // parámetros globales predeterminados del proveedor
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
      thinkingDefault: "low",
      verboseDefault: "off",
      elevatedDefault: "on",
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      contextTokens: 200000,
      maxConcurrent: 3,
    },
  },
}
```

- `model`: acepta una cadena (`"provider/model"`) o un objeto (`{ primary, fallbacks }`).
  - La forma de cadena establece solo el modelo principal.
  - La forma de objeto establece el principal más los modelos de failover en orden.
- `imageModel`: acepta una cadena (`"provider/model"`) o un objeto (`{ primary, fallbacks }`).
  - Lo usa la ruta de la herramienta `image` como su configuración de modelo de visión.
  - También se usa como enrutamiento de respaldo cuando el modelo seleccionado/predeterminado no puede aceptar entrada de imagen.
- `imageGenerationModel`: acepta una cadena (`"provider/model"`) o un objeto (`{ primary, fallbacks }`).
  - Lo usa la capacidad compartida de generación de imágenes y cualquier futura superficie de herramienta/plugin que genere imágenes.
  - Valores típicos: `google/gemini-3.1-flash-image-preview` para generación nativa de imágenes con Gemini, `fal/fal-ai/flux/dev` para fal, o `openai/gpt-image-1` para OpenAI Images.
  - Si seleccionas directamente un provider/model, configura también la autenticación o clave API correspondiente del proveedor (por ejemplo `GEMINI_API_KEY` o `GOOGLE_API_KEY` para `google/*`, `OPENAI_API_KEY` para `openai/*`, `FAL_KEY` para `fal/*`).
  - Si se omite, `image_generate` todavía puede inferir un valor predeterminado del proveedor respaldado por autenticación. Primero prueba el proveedor predeterminado actual, luego los proveedores de generación de imágenes registrados restantes en orden de ID de proveedor.
- `musicGenerationModel`: acepta una cadena (`"provider/model"`) o un objeto (`{ primary, fallbacks }`).
  - Lo usa la capacidad compartida de generación musical y la herramienta incorporada `music_generate`.
  - Valores típicos: `google/lyria-3-clip-preview`, `google/lyria-3-pro-preview` o `minimax/music-2.5+`.
  - Si se omite, `music_generate` todavía puede inferir un valor predeterminado del proveedor respaldado por autenticación. Primero prueba el proveedor predeterminado actual, luego los proveedores de generación musical registrados restantes en orden de ID de proveedor.
  - Si seleccionas directamente un provider/model, configura también la autenticación o clave API correspondiente del proveedor.
- `videoGenerationModel`: acepta una cadena (`"provider/model"`) o un objeto (`{ primary, fallbacks }`).
  - Lo usa la capacidad compartida de generación de video y la herramienta incorporada `video_generate`.
  - Valores típicos: `qwen/wan2.6-t2v`, `qwen/wan2.6-i2v`, `qwen/wan2.6-r2v`, `qwen/wan2.6-r2v-flash` o `qwen/wan2.7-r2v`.
  - Si se omite, `video_generate` todavía puede inferir un valor predeterminado del proveedor respaldado por autenticación. Primero prueba el proveedor predeterminado actual, luego los proveedores de generación de video registrados restantes en orden de ID de proveedor.
  - Si seleccionas directamente un provider/model, configura también la autenticación o clave API correspondiente del proveedor.
  - El proveedor agrupado de generación de video Qwen actualmente admite hasta 1 video de salida, 1 imagen de entrada, 4 videos de entrada, duración de 10 segundos y opciones a nivel de proveedor `size`, `aspectRatio`, `resolution`, `audio` y `watermark`.
- `pdfModel`: acepta una cadena (`"provider/model"`) o un objeto (`{ primary, fallbacks }`).
  - Lo usa la herramienta `pdf` para el enrutamiento del modelo.
  - Si se omite, la herramienta PDF vuelve a `imageModel` y luego al modelo resuelto de sesión/predeterminado.
- `pdfMaxBytesMb`: límite predeterminado de tamaño PDF para la herramienta `pdf` cuando `maxBytesMb` no se pasa en la llamada.
- `pdfMaxPages`: número máximo predeterminado de páginas consideradas por el modo de respaldo de extracción en la herramienta `pdf`.
- `verboseDefault`: nivel verbose predeterminado para agentes. Valores: `"off"`, `"on"`, `"full"`. Predeterminado: `"off"`.
- `elevatedDefault`: nivel predeterminado de salida elevada para agentes. Valores: `"off"`, `"on"`, `"ask"`, `"full"`. Predeterminado: `"on"`.
- `model.primary`: formato `provider/model` (p. ej. `openai/gpt-5.4`). Si omites el proveedor, OpenClaw intenta primero un alias, luego una coincidencia única de proveedor configurado para ese ID exacto de modelo y solo entonces recurre al proveedor predeterminado configurado (comportamiento de compatibilidad obsoleto, así que prefiere `provider/model` explícito). Si ese proveedor ya no expone el modelo predeterminado configurado, OpenClaw vuelve al primer proveedor/modelo configurado en lugar de mostrar un valor predeterminado obsoleto de un proveedor eliminado.
- `models`: el catálogo y allowlist configurados de modelos para `/model`. Cada entrada puede incluir `alias` (atajo) y `params` (específicos del proveedor, por ejemplo `temperature`, `maxTokens`, `cacheRetention`, `context1m`).
- `params`: parámetros globales predeterminados del proveedor aplicados a todos los modelos. Se establecen en `agents.defaults.params` (p. ej. `{ cacheRetention: "long" }`).
- Precedencia de fusión de `params` (configuración): `agents.defaults.params` (base global) es sobrescrito por `agents.defaults.models["provider/model"].params` (por modelo), y luego `agents.list[].params` (ID de agente coincidente) sobrescribe por clave. Consulta [Prompt Caching](/es/reference/prompt-caching) para más detalles.
- Los escritores de configuración que mutan estos campos (por ejemplo `/models set`, `/models set-image` y comandos para agregar/quitar fallbacks) guardan la forma canónica de objeto y conservan las listas de fallback existentes cuando es posible.
- `maxConcurrent`: máximo de ejecuciones paralelas de agentes entre sesiones (cada sesión sigue serializada). Predeterminado: 4.

**Atajos de alias incorporados** (solo se aplican cuando el modelo está en `agents.defaults.models`):

| Alias               | Modelo                                 |
| ------------------- | -------------------------------------- |
| `opus`              | `anthropic/claude-opus-4-6`            |
| `sonnet`            | `anthropic/claude-sonnet-4-6`          |
| `gpt`               | `openai/gpt-5.4`                       |
| `gpt-mini`          | `openai/gpt-5.4-mini`                  |
| `gpt-nano`          | `openai/gpt-5.4-nano`                  |
| `gemini`            | `google/gemini-3.1-pro-preview`        |
| `gemini-flash`      | `google/gemini-3-flash-preview`        |
| `gemini-flash-lite` | `google/gemini-3.1-flash-lite-preview` |

Tus alias configurados siempre tienen prioridad sobre los predeterminados.

Los modelos Z.AI GLM-4.x habilitan automáticamente el modo thinking a menos que establezcas `--thinking off` o definas tú mismo `agents.defaults.models["zai/<model>"].params.thinking`.
Los modelos Z.AI habilitan `tool_stream` de forma predeterminada para streaming de llamadas a herramientas. Establece `agents.defaults.models["zai/<model>"].params.tool_stream` en `false` para desactivarlo.
Los modelos Anthropic Claude 4.6 usan `adaptive` por defecto para thinking cuando no se establece un nivel explícito de thinking.

- Se admiten sesiones cuando `sessionArg` está configurado.
- Se admite el paso directo de imágenes cuando `imageArg` acepta rutas de archivo.

### `agents.defaults.heartbeat`

Ejecuciones periódicas de heartbeat.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m desactiva
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        lightContext: false, // predeterminado: false; true conserva solo HEARTBEAT.md de los archivos bootstrap del workspace
        isolatedSession: false, // predeterminado: false; true ejecuta cada heartbeat en una sesión nueva (sin historial de conversación)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (predeterminado) | block
        target: "none", // predeterminado: none | opciones: last | whatsapp | telegram | discord | ...
        prompt: "Lee HEARTBEAT.md si existe...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
      },
    },
  },
}
```

- `every`: cadena de duración (ms/s/m/h). Predeterminado: `30m` (autenticación por clave API) o `1h` (autenticación OAuth). Establece `0m` para desactivar.
- `suppressToolErrorWarnings`: cuando es true, suprime las cargas de advertencia de errores de herramientas durante ejecuciones de heartbeat.
- `directPolicy`: política de entrega directa/MD. `allow` (predeterminada) permite entrega a destino directo. `block` la suprime y emite `reason=dm-blocked`.
- `lightContext`: cuando es true, las ejecuciones de heartbeat usan contexto bootstrap ligero y conservan solo `HEARTBEAT.md` de los archivos bootstrap del workspace.
- `isolatedSession`: cuando es true, cada ejecución de heartbeat se hace en una sesión nueva sin historial previo de conversación. Mismo patrón de aislamiento que cron `sessionTarget: "isolated"`. Reduce el costo por heartbeat de ~100K a ~2-5K tokens.
- Por agente: establece `agents.list[].heartbeat`. Cuando cualquier agente define `heartbeat`, **solo esos agentes** ejecutan heartbeats.
- Los heartbeats ejecutan turnos completos del agente: intervalos más cortos consumen más tokens.

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        timeoutSeconds: 900,
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "Conserva exactamente los ID de despliegue, ID de tickets y pares host:port.", // usado cuando identifierPolicy=custom
        postCompactionSections: ["Session Startup", "Red Lines"], // [] desactiva la reinyección
        model: "openrouter/anthropic/claude-sonnet-4-6", // sobrescritura opcional del modelo solo para compactación
        notifyUser: true, // enviar un aviso breve cuando comienza la compactación (predeterminado: false)
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "La sesión se acerca a la compactación. Almacena ahora memorias duraderas.",
          prompt: "Escribe cualquier nota duradera en memory/YYYY-MM-DD.md; responde con el token silencioso exacto NO_REPLY si no hay nada que guardar.",
        },
      },
    },
  },
}
```

- `mode`: `default` o `safeguard` (resumen por fragmentos para historiales largos). Consulta [Compactación](/es/concepts/compaction).
- `timeoutSeconds`: segundos máximos permitidos para una sola operación de compactación antes de que OpenClaw la aborte. Predeterminado: `900`.
- `identifierPolicy`: `strict` (predeterminado), `off` o `custom`. `strict` antepone orientación incorporada para conservar identificadores opacos durante el resumen de compactación.
- `identifierInstructions`: texto opcional personalizado de preservación de identificadores usado cuando `identifierPolicy=custom`.
- `postCompactionSections`: nombres opcionales de secciones H2/H3 de AGENTS.md para reinyectar después de la compactación. Predeterminado: `["Session Startup", "Red Lines"]`; establece `[]` para desactivar la reinyección. Cuando no está configurado o se establece explícitamente en ese par predeterminado, también se aceptan como respaldo heredado los encabezados antiguos `Every Session`/`Safety`.
- `model`: sobrescritura opcional `provider/model-id` solo para el resumen de compactación. Úsala cuando la sesión principal deba mantener un modelo pero los resúmenes de compactación deban ejecutarse con otro; cuando no está configurado, la compactación usa el modelo principal de la sesión.
- `notifyUser`: cuando es `true`, envía al usuario un aviso breve cuando comienza la compactación (por ejemplo, "Compacting context..."). Está desactivado de forma predeterminada para mantener la compactación silenciosa.
- `memoryFlush`: turno agéntico silencioso antes de la autocompactación para almacenar memorias duraderas. Se omite cuando el workspace es de solo lectura.

### `agents.defaults.contextPruning`

Poda **resultados antiguos de herramientas** del contexto en memoria antes de enviarlo al LLM. **No** modifica el historial de sesión en disco.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // duración (ms/s/m/h), unidad predeterminada: minutos
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Contenido antiguo del resultado de herramienta eliminado]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="Comportamiento del modo cache-ttl">

- `mode: "cache-ttl"` habilita pasadas de poda.
- `ttl` controla cada cuánto puede volver a ejecutarse la poda (después del último toque de caché).
- La poda primero recorta de forma suave los resultados sobredimensionados de herramientas y luego elimina por completo los resultados más antiguos si es necesario.

**Soft-trim** conserva el comienzo + el final e inserta `...` en medio.

**Hard-clear** reemplaza todo el resultado de la herramienta con el marcador.

Notas:

- Los bloques de imagen nunca se recortan ni se eliminan.
- Las proporciones se basan en caracteres (aproximadas), no en recuentos exactos de tokens.
- Si existen menos de `keepLastAssistants` mensajes del asistente, la poda se omite.

</Accordion>

Consulta [Poda de sesión](/es/concepts/session-pruning) para detalles de comportamiento.

### Streaming por bloques

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (usa minMs/maxMs)
    },
  },
}
```

- Los canales que no son Telegram requieren `*.blockStreaming: true` explícito para habilitar respuestas por bloques.
- Sobrescrituras por canal: `channels.<channel>.blockStreamingCoalesce` (y variantes por cuenta). Signal/Slack/Discord/Google Chat usan por defecto `minChars: 1500`.
- `humanDelay`: pausa aleatoria entre respuestas por bloques. `natural` = 800–2500ms. Sobrescritura por agente: `agents.list[].humanDelay`.

Consulta [Streaming](/es/concepts/streaming) para detalles de comportamiento y fragmentación.

### Indicadores de escritura

```json5
{
  agents: {
    defaults: {
      typingMode: "instant", // never | instant | thinking | message
      typingIntervalSeconds: 6,
    },
  },
}
```

- Valores predeterminados: `instant` para chats directos/menciones, `message` para grupos sin mención.
- Sobrescrituras por sesión: `session.typingMode`, `session.typingIntervalSeconds`.

Consulta [Indicadores de escritura](/es/concepts/typing-indicators).

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

Sandboxing opcional para el agente integrado. Consulta [Sandboxing](/es/gateway/sandboxing) para la guía completa.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        backend: "docker", // docker | ssh | openshell
        scope: "agent", // session | agent | shared
        workspaceAccess: "none", // none | ro | rw
        workspaceRoot: "~/.openclaw/sandboxes",
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          containerPrefix: "openclaw-sbx-",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: {
            nofile: { soft: 1024, hard: 2048 },
            nproc: 256,
          },
          seccompProfile: "/path/to/seccomp.json",
          apparmorProfile: "openclaw-sandbox",
          dns: ["1.1.1.1", "8.8.8.8"],
          extraHosts: ["internal.service:10.0.0.5"],
          binds: ["/home/user/source:/source:rw"],
        },
        ssh: {
          target: "user@gateway-host:22",
          command: "ssh",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // También se admiten SecretRefs / contenidos en línea:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
        browser: {
          enabled: false,
          image: "openclaw-sandbox-browser:bookworm-slim",
          network: "openclaw-sandbox-browser",
          cdpPort: 9222,
          cdpSourceRange: "172.21.0.1/32",
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          allowHostControl: false,
          autoStart: true,
          autoStartTimeoutMs: 12000,
        },
        prune: {
          idleHours: 24,
          maxAgeDays: 7,
        },
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        allow: [
          "exec",
          "process",
          "read",
          "write",
          "edit",
          "apply_patch",
          "sessions_list",
          "sessions_history",
          "sessions_send",
          "sessions_spawn",
          "session_status",
        ],
        deny: ["browser", "canvas", "nodes", "cron", "discord", "gateway"],
      },
    },
  },
}
```

<Accordion title="Detalles de sandbox">

**Backend:**

- `docker`: tiempo de ejecución local de Docker (predeterminado)
- `ssh`: tiempo de ejecución remoto genérico respaldado por SSH
- `openshell`: tiempo de ejecución OpenShell

Cuando se selecciona `backend: "openshell"`, los ajustes específicos del tiempo de ejecución pasan a
`plugins.entries.openshell.config`.

**Configuración del backend SSH:**

- `target`: destino SSH en formato `user@host[:port]`
- `command`: comando del cliente SSH (predeterminado: `ssh`)
- `workspaceRoot`: raíz remota absoluta usada para workspaces por ámbito
- `identityFile` / `certificateFile` / `knownHostsFile`: archivos locales existentes pasados a OpenSSH
- `identityData` / `certificateData` / `knownHostsData`: contenidos en línea o SecretRefs que OpenClaw materializa en archivos temporales en tiempo de ejecución
- `strictHostKeyChecking` / `updateHostKeys`: controles de política de clave de host de OpenSSH

**Precedencia de autenticación SSH:**

- `identityData` tiene prioridad sobre `identityFile`
- `certificateData` tiene prioridad sobre `certificateFile`
- `knownHostsData` tiene prioridad sobre `knownHostsFile`
- Los valores `*Data` respaldados por SecretRef se resuelven desde la instantánea activa del tiempo de ejecución de secretos antes de que comience la sesión sandbox

**Comportamiento del backend SSH:**

- inicializa el workspace remoto una vez después de crear o recrear
- luego mantiene como canónico el workspace SSH remoto
- enruta `exec`, las herramientas de archivos y las rutas de medios por SSH
- no sincroniza automáticamente de vuelta al host los cambios remotos
- no admite contenedores de navegador sandbox

**Acceso al workspace:**

- `none`: workspace sandbox por ámbito bajo `~/.openclaw/sandboxes`
- `ro`: workspace sandbox en `/workspace`, workspace del agente montado de solo lectura en `/agent`
- `rw`: workspace del agente montado en lectura/escritura en `/workspace`

**Ámbito:**

- `session`: contenedor + workspace por sesión
- `agent`: un contenedor + workspace por agente (predeterminado)
- `shared`: contenedor y workspace compartidos (sin aislamiento entre sesiones)

**Configuración del plugin OpenShell:**

```json5
{
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          mode: "mirror", // mirror | remote
          from: "openclaw",
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
          gateway: "lab", // opcional
          gatewayEndpoint: "https://lab.example", // opcional
          policy: "strict", // ID opcional de política OpenShell
          providers: ["openai"], // opcional
          autoProviders: true,
          timeoutSeconds: 120,
        },
      },
    },
  },
}
```

**Modo OpenShell:**

- `mirror`: inicializa el remoto desde el local antes de exec, sincroniza de vuelta después de exec; el workspace local sigue siendo canónico
- `remote`: inicializa el remoto una vez cuando se crea el sandbox y luego mantiene el workspace remoto como canónico

En modo `remote`, las ediciones locales del host hechas fuera de OpenClaw no se sincronizan automáticamente al sandbox después del paso inicial.
El transporte es SSH hacia el sandbox OpenShell, pero el plugin es responsable del ciclo de vida del sandbox y de la sincronización espejo opcional.

**`setupCommand`** se ejecuta una vez después de crear el contenedor (mediante `sh -lc`). Necesita salida de red, raíz escribible y usuario root.

**Los contenedores usan por defecto `network: "none"`**: cámbialo a `"bridge"` (o una red bridge personalizada) si el agente necesita acceso saliente.
`"host"` está bloqueado. `"container:<id>"` está bloqueado de forma predeterminada salvo que establezcas explícitamente
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` (break-glass).

**Los adjuntos entrantes** se preparan en `media/inbound/*` dentro del workspace activo.

**`docker.binds`** monta directorios adicionales del host; los binds globales y por agente se fusionan.

**Navegador sandbox** (`sandbox.browser.enabled`): Chromium + CDP en un contenedor. Se inyecta la URL de noVNC en el system prompt. No requiere `browser.enabled` en `openclaw.json`.
El acceso de observador noVNC usa autenticación VNC por defecto y OpenClaw emite una URL con token de corta duración (en lugar de exponer la contraseña en la URL compartida).

- `allowHostControl: false` (predeterminado) bloquea que las sesiones sandbox apunten al navegador del host.
- `network` usa por defecto `openclaw-sandbox-browser` (red bridge dedicada). Establécelo en `bridge` solo cuando quieras explícitamente conectividad global del bridge.
- `cdpSourceRange` restringe opcionalmente el ingreso CDP en el borde del contenedor a un rango CIDR (por ejemplo `172.21.0.1/32`).
- `sandbox.browser.binds` monta directorios adicionales del host solo dentro del contenedor del navegador sandbox. Cuando se configura (incluido `[]`), reemplaza `docker.binds` para el contenedor del navegador.
- Los valores predeterminados de lanzamiento están definidos en `scripts/sandbox-browser-entrypoint.sh` y ajustados para hosts con contenedores:
  - `--remote-debugging-address=127.0.0.1`
  - `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
  - `--user-data-dir=${HOME}/.chrome`
  - `--no-first-run`
  - `--no-default-browser-check`
  - `--disable-3d-apis`
  - `--disable-gpu`
  - `--disable-software-rasterizer`
  - `--disable-dev-shm-usage`
  - `--disable-background-networking`
  - `--disable-features=TranslateUI`
  - `--disable-breakpad`
  - `--disable-crash-reporter`
  - `--renderer-process-limit=2`
  - `--no-zygote`
  - `--metrics-recording-only`
  - `--disable-extensions` (habilitado por defecto)
  - `--disable-3d-apis`, `--disable-software-rasterizer` y `--disable-gpu` están
    habilitados de forma predeterminada y pueden desactivarse con
    `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` si el uso de WebGL/3D lo requiere.
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` vuelve a habilitar extensiones si tu flujo de trabajo
    depende de ellas.
  - `--renderer-process-limit=2` puede cambiarse con
    `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`; establece `0` para usar el
    límite de procesos predeterminado de Chromium.
  - más `--no-sandbox` y `--disable-setuid-sandbox` cuando `noSandbox` está habilitado.
  - Los valores predeterminados son la línea base de la imagen del contenedor; usa una imagen de navegador personalizada con un
    entrypoint personalizado para cambiar los valores predeterminados del contenedor.

</Accordion>

El sandboxing del navegador y `sandbox.docker.binds` actualmente solo están disponibles para Docker.

Construir imágenes:

```bash
scripts/sandbox-setup.sh           # imagen principal del sandbox
scripts/sandbox-browser-setup.sh   # imagen opcional del navegador
```

### `agents.list` (sobrescrituras por agente)

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Agente principal",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6", // o { primary, fallbacks }
        thinkingDefault: "high", // sobrescritura por agente del nivel de thinking
        reasoningDefault: "on", // sobrescritura por agente de la visibilidad de reasoning
        fastModeDefault: false, // sobrescritura por agente del modo rápido
        params: { cacheRetention: "none" }, // sobrescribe por clave los params de defaults.models coincidentes
        skills: ["docs-search"], // reemplaza agents.defaults.skills cuando está configurado
        identity: {
          name: "Samantha",
          theme: "perezoso servicial",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
        subagents: { allowAgents: ["*"] },
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
          elevated: { enabled: true },
        },
      },
    ],
  },
}
```

- `id`: ID estable de agente (obligatorio).
- `default`: cuando hay varios, gana el primero (se registra una advertencia). Si no hay ninguno, la primera entrada de la lista es la predeterminada.
- `model`: la forma de cadena sobrescribe solo `primary`; la forma de objeto `{ primary, fallbacks }` sobrescribe ambos (`[]` desactiva los fallbacks globales). Los trabajos cron que solo sobrescriben `primary` siguen heredando los fallbacks predeterminados salvo que establezcas `fallbacks: []`.
- `params`: parámetros de stream por agente fusionados sobre la entrada de modelo seleccionada en `agents.defaults.models`. Úsalo para sobrescrituras específicas del agente como `cacheRetention`, `temperature` o `maxTokens` sin duplicar todo el catálogo de modelos.
- `skills`: allowlist opcional de Skills por agente. Si se omite, el agente hereda `agents.defaults.skills` cuando está configurado; una lista explícita reemplaza los valores predeterminados en lugar de fusionarse, y `[]` significa sin Skills.
- `thinkingDefault`: nivel predeterminado opcional de thinking por agente (`off | minimal | low | medium | high | xhigh | adaptive`). Sobrescribe `agents.defaults.thinkingDefault` para este agente cuando no hay sobrescritura por mensaje o sesión.
- `reasoningDefault`: visibilidad predeterminada opcional de reasoning por agente (`on | off | stream`). Se aplica cuando no hay sobrescritura de reasoning por mensaje o sesión.
- `fastModeDefault`: valor predeterminado opcional por agente para el modo rápido (`true | false`). Se aplica cuando no hay sobrescritura del modo rápido por mensaje o sesión.
- `runtime`: descriptor opcional del tiempo de ejecución por agente. Usa `type: "acp"` con valores predeterminados de `runtime.acp` (`agent`, `backend`, `mode`, `cwd`) cuando el agente deba usar por defecto sesiones del arnés ACP.
- `identity.avatar`: ruta relativa al workspace, URL `http(s)` o URI `data:`.
- `identity` deriva valores predeterminados: `ackReaction` a partir de `emoji`, `mentionPatterns` a partir de `name`/`emoji`.
- `subagents.allowAgents`: allowlist de IDs de agente para `sessions_spawn` (`["*"]` = cualquiera; predeterminado: solo el mismo agente).
- Guardia de herencia de sandbox: si la sesión solicitante está en sandbox, `sessions_spawn` rechaza objetivos que se ejecutarían sin sandbox.
- `subagents.requireAgentId`: cuando es true, bloquea llamadas a `sessions_spawn` que omiten `agentId` (obliga a una selección explícita del perfil; predeterminado: false).

---

## Enrutamiento multagente

Ejecuta varios agentes aislados dentro de un mismo Gateway. Consulta [Multi-Agent](/es/concepts/multi-agent).

```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

### Campos de coincidencia de bindings

- `type` (opcional): `route` para enrutamiento normal (si falta el tipo, el valor predeterminado es route), `acp` para enlaces persistentes de conversación ACP.
- `match.channel` (obligatorio)
- `match.accountId` (opcional; `*` = cualquier cuenta; omitido = cuenta predeterminada)
- `match.peer` (opcional; `{ kind: direct|group|channel, id }`)
- `match.guildId` / `match.teamId` (opcional; específico del canal)
- `acp` (opcional; solo para entradas `type: "acp"`): `{ mode, label, cwd, backend }`

**Orden determinista de coincidencia:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId` (exacto, sin peer/guild/team)
5. `match.accountId: "*"` (para todo el canal)
6. Agente predeterminado

Dentro de cada nivel, gana la primera entrada coincidente de `bindings`.

Para las entradas `type: "acp"`, OpenClaw resuelve por identidad exacta de conversación (`match.channel` + cuenta + `match.peer.id`) y no usa el orden de niveles de route binding anterior.

### Perfiles de acceso por agente

<Accordion title="Acceso completo (sin sandbox)">

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="Herramientas + workspace de solo lectura">

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "ro" },
        tools: {
          allow: [
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="Sin acceso al sistema de archivos (solo mensajería)">

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "none" },
        tools: {
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
            "gateway",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

</Accordion>

Consulta [Sandbox y herramientas multagente](/es/tools/multi-agent-sandbox-tools) para detalles de precedencia.

---

## Sesión

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main", // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily", // daily | idle
      atHour: 4,
      idleMinutes: 60,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    parentForkMaxTokens: 100000, // omitir la bifurcación del hilo padre por encima de este recuento de tokens (0 desactiva)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // duración o false
      maxDiskBytes: "500mb", // presupuesto rígido opcional
      highWaterBytes: "400mb", // objetivo opcional de limpieza
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // desenfoque automático predeterminado por inactividad en horas (`0` lo desactiva)
      maxAgeHours: 0, // antigüedad máxima estricta predeterminada en horas (`0` la desactiva)
    },
    mainKey: "main", // heredado (el tiempo de ejecución siempre usa "main")
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="Detalles de los campos de sesión">

- **`scope`**: estrategia base de agrupación de sesiones para contextos de chat grupal.
  - `per-sender` (predeterminado): cada remitente obtiene una sesión aislada dentro de un contexto de canal.
  - `global`: todos los participantes de un contexto de canal comparten una sola sesión (úsalo solo cuando se quiera contexto compartido).
- **`dmScope`**: cómo se agrupan los MD.
  - `main`: todos los MD comparten la sesión principal.
  - `per-peer`: aislar por ID de remitente entre canales.
  - `per-channel-peer`: aislar por canal + remitente (recomendado para bandejas de entrada multiusuario).
  - `per-account-channel-peer`: aislar por cuenta + canal + remitente (recomendado para varias cuentas).
- **`identityLinks`**: asigna IDs canónicos a peers con prefijo de proveedor para compartir sesiones entre canales.
- **`reset`**: política principal de reinicio. `daily` reinicia a la hora local `atHour`; `idle` reinicia después de `idleMinutes`. Cuando ambos están configurados, gana el que expire primero.
- **`resetByType`**: sobrescrituras por tipo (`direct`, `group`, `thread`). Se acepta `dm` heredado como alias de `direct`.
- **`parentForkMaxTokens`**: máximo de `totalTokens` de la sesión padre permitido al crear una sesión de hilo bifurcado (predeterminado `100000`).
  - Si `totalTokens` del padre está por encima de este valor, OpenClaw inicia una sesión de hilo nueva en lugar de heredar el historial de transcripción del padre.
  - Establece `0` para desactivar esta protección y permitir siempre la bifurcación desde el padre.
- **`mainKey`**: campo heredado. El tiempo de ejecución ahora siempre usa `"main"` para el bucket principal de chat directo.
- **`agentToAgent.maxPingPongTurns`**: máximo de turnos de respuesta entre agentes durante intercambios agente a agente (entero, rango: `0`–`5`). `0` desactiva la cadena ping-pong.
- **`sendPolicy`**: coincide por `channel`, `chatType` (`direct|group|channel`, con alias heredado `dm`), `keyPrefix` o `rawKeyPrefix`. Gana la primera denegación.
- **`maintenance`**: controles de limpieza + retención del almacén de sesiones.
  - `mode`: `warn` solo emite advertencias; `enforce` aplica la limpieza.
  - `pruneAfter`: corte de antigüedad para entradas obsoletas (predeterminado `30d`).
  - `maxEntries`: número máximo de entradas en `sessions.json` (predeterminado `500`).
  - `rotateBytes`: rota `sessions.json` cuando supera este tamaño (predeterminado `10mb`).
  - `resetArchiveRetention`: retención para archivos de transcripción `*.reset.<timestamp>`. Usa `pruneAfter` como predeterminado; establece `false` para desactivar.
  - `maxDiskBytes`: presupuesto opcional de disco para el directorio de sesiones. En modo `warn` registra advertencias; en modo `enforce` elimina primero los artefactos/sesiones más antiguos.
  - `highWaterBytes`: objetivo opcional después de la limpieza por presupuesto. Predeterminado: `80%` de `maxDiskBytes`.
- **`threadBindings`**: valores predeterminados globales para funciones de sesión ligadas a hilos.
  - `enabled`: interruptor maestro predeterminado (los proveedores pueden sobrescribirlo; Discord usa `channels.discord.threadBindings.enabled`)
  - `idleHours`: desenfoque automático predeterminado por inactividad en horas (`0` lo desactiva; los proveedores pueden sobrescribirlo)
  - `maxAgeHours`: antigüedad máxima estricta predeterminada en horas (`0` la desactiva; los proveedores pueden sobrescribirla)

</Accordion>

---

## Mensajes

```json5
{
  messages: {
    responsePrefix: "🦞", // o "auto"
    ackReaction: "👀",
    ackReactionScope: "group-mentions", // group-mentions | group-all | direct | all
    removeAckAfterReply: false,
    queue: {
      mode: "collect", // steer | followup | collect | steer-backlog | steer+backlog | queue | interrupt
      debounceMs: 1000,
      cap: 20,
      drop: "summarize", // old | new | summarize
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
      },
    },
    inbound: {
      debounceMs: 2000, // 0 desactiva
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### Prefijo de respuesta

Sobrescrituras por canal/cuenta: `channels.<channel>.responsePrefix`, `channels.<channel>.accounts.<id>.responsePrefix`.

Resolución (gana el más específico): cuenta → canal → global. `""` lo desactiva y detiene la cascada. `"auto"` deriva `[{identity.name}]`.

**Variables de plantilla:**

| Variable          | Descripción            | Ejemplo                     |
| ----------------- | ---------------------- | --------------------------- |
| `{model}`         | Nombre corto del modelo | `claude-opus-4-6`           |
| `{modelFull}`     | Identificador completo del modelo | `anthropic/claude-opus-4-6` |
| `{provider}`      | Nombre del proveedor   | `anthropic`                 |
| `{thinkingLevel}` | Nivel actual de thinking | `high`, `low`, `off`        |
| `{identity.name}` | Nombre de la identidad del agente | (igual que `"auto"`)          |

Las variables no distinguen mayúsculas y minúsculas. `{think}` es un alias de `{thinkingLevel}`.

### Reacción de acuse

- Usa por defecto `identity.emoji` del agente activo, o `"👀"` en su defecto. Establece `""` para desactivarla.
- Sobrescrituras por canal: `channels.<channel>.ackReaction`, `channels.<channel>.accounts.<id>.ackReaction`.
- Orden de resolución: cuenta → canal → `messages.ackReaction` → respaldo de identidad.
- Ámbito: `group-mentions` (predeterminado), `group-all`, `direct`, `all`.
- `removeAckAfterReply`: elimina el acuse tras responder en Slack, Discord y Telegram.
- `messages.statusReactions.enabled`: habilita reacciones de estado del ciclo de vida en Slack, Discord y Telegram.
  En Slack y Discord, si no se configura explícitamente, las reacciones de estado siguen habilitadas cuando las reacciones de acuse están activas.
  En Telegram, establécelo explícitamente en `true` para habilitar reacciones de estado del ciclo de vida.

### Debounce de entrada

Agrupa mensajes rápidos de solo texto del mismo remitente en un único turno del agente. Los medios/adjuntos fuerzan vaciado inmediato. Los comandos de control omiten el debounce.

### TTS (texto a voz)

```json5
{
  messages: {
    tts: {
      auto: "always", // off | always | inbound | tagged
      mode: "final", // final | all
      provider: "elevenlabs",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: { enabled: true },
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
      elevenlabs: {
        apiKey: "elevenlabs_api_key",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 42,
        applyTextNormalization: "auto",
        languageCode: "en",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          style: 0.0,
          useSpeakerBoost: true,
          speed: 1.0,
        },
      },
      openai: {
        apiKey: "openai_api_key",
        baseUrl: "https://api.openai.com/v1",
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
    },
  },
}
```

- `auto` controla el TTS automático. `/tts off|always|inbound|tagged` sobrescribe por sesión.
- `summaryModel` sobrescribe `agents.defaults.model.primary` para el resumen automático.
- `modelOverrides` está habilitado de forma predeterminada; `modelOverrides.allowProvider` usa `false` por defecto (activación opcional).
- Las claves API usan `ELEVENLABS_API_KEY`/`XI_API_KEY` y `OPENAI_API_KEY` como respaldo.
- `openai.baseUrl` sobrescribe el endpoint TTS de OpenAI. El orden de resolución es configuración, luego `OPENAI_TTS_BASE_URL` y luego `https://api.openai.com/v1`.
- Cuando `openai.baseUrl` apunta a un endpoint que no es de OpenAI, OpenClaw lo trata como un servidor TTS compatible con OpenAI y relaja la validación de modelo/voz.

---

## Talk

Valores predeterminados para el modo Talk (macOS/iOS/Android).

```json5
{
  talk: {
    provider: "elevenlabs",
    providers: {
      elevenlabs: {
        voiceId: "elevenlabs_voice_id",
        voiceAliases: {
          Clawd: "EXAVITQu4vr4xnSDxMaL",
          Roger: "CwhRBWXzGAHq8TQ4Fs17",
        },
        modelId: "eleven_v3",
        outputFormat: "mp3_44100_128",
        apiKey: "elevenlabs_api_key",
      },
    },
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
  },
}
```

- `talk.provider` debe coincidir con una clave de `talk.providers` cuando se configuran varios proveedores Talk.
- Las claves planas heredadas de Talk (`talk.voiceId`, `talk.voiceAliases`, `talk.modelId`, `talk.outputFormat`, `talk.apiKey`) son solo de compatibilidad y se migran automáticamente a `talk.providers.<provider>`.
- Los IDs de voz usan `ELEVENLABS_VOICE_ID` o `SAG_VOICE_ID` como respaldo.
- `providers.*.apiKey` acepta cadenas de texto plano u objetos SecretRef.
- El respaldo `ELEVENLABS_API_KEY` solo se aplica cuando no hay ninguna clave API Talk configurada.
- `providers.*.voiceAliases` permite que las directivas Talk usen nombres amigables.
- `silenceTimeoutMs` controla cuánto espera el modo Talk después del silencio del usuario antes de enviar la transcripción. Si no se configura, se mantiene la ventana de pausa predeterminada de la plataforma (`700 ms en macOS y Android, 900 ms en iOS`).

---

## Herramientas

### Perfiles de herramientas

`tools.profile` establece una allowlist base antes de `tools.allow`/`tools.deny`:

La incorporación local configura por defecto nuevas configuraciones locales con `tools.profile: "coding"` cuando no está establecido (los perfiles explícitos existentes se conservan).

| Perfil      | Incluye                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | solo `session_status`                                                                                                           |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                       |
| `full`      | Sin restricción (igual que sin configurar)                                                                                      |

### Grupos de herramientas

| Grupo              | Herramientas                                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `group:runtime`    | `exec`, `process`, `code_execution` (`bash` se acepta como alias de `exec`)                                                   |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                                                         |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status`      |
| `group:memory`     | `memory_search`, `memory_get`                                                                                                  |
| `group:web`        | `web_search`, `x_search`, `web_fetch`                                                                                          |
| `group:ui`         | `browser`, `canvas`                                                                                                            |
| `group:automation` | `cron`, `gateway`                                                                                                              |
| `group:messaging`  | `message`                                                                                                                      |
| `group:nodes`      | `nodes`                                                                                                                        |
| `group:agents`     | `agents_list`                                                                                                                  |
| `group:media`      | `image`, `image_generate`, `video_generate`, `tts`                                                                             |
| `group:openclaw`   | Todas las herramientas incorporadas (excluye plugins de proveedor)                                                             |

### `tools.allow` / `tools.deny`

Política global de permitir/denegar herramientas (deny gana). No distingue mayúsculas y minúsculas, admite comodines `*`. Se aplica incluso cuando el sandbox Docker está desactivado.

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

Restringe aún más las herramientas para proveedores o modelos específicos. Orden: perfil base → perfil por proveedor → allow/deny.

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.4": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

### `tools.elevated`

Controla el acceso exec elevado fuera del sandbox:

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["1234567890123", "987654321098765432"],
      },
    },
  },
}
```

- La sobrescritura por agente (`agents.list[].tools.elevated`) solo puede restringir más.
- `/elevated on|off|ask|full` almacena el estado por sesión; las directivas en línea se aplican a un solo mensaje.
- `exec` elevado omite el sandbox y usa la ruta de escape configurada (`gateway` por defecto, o `node` cuando el objetivo exec es `node`).

### `tools.exec`

```json5
{
  tools: {
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
      notifyOnExitEmptySuccess: false,
      applyPatch: {
        enabled: false,
        allowModels: ["gpt-5.4"],
      },
    },
  },
}
```

### `tools.loopDetection`

Las verificaciones de seguridad de bucle de herramientas están **desactivadas de forma predeterminada**. Establece `enabled: true` para activar la detección.
Los ajustes pueden definirse globalmente en `tools.loopDetection` y sobrescribirse por agente en `agents.list[].tools.loopDetection`.

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

- `historySize`: máximo historial de llamadas de herramientas retenido para análisis de bucles.
- `warningThreshold`: umbral para advertencias de patrones repetitivos sin progreso.
- `criticalThreshold`: umbral superior para bloquear bucles críticos.
- `globalCircuitBreakerThreshold`: umbral de parada dura para cualquier ejecución sin progreso.
- `detectors.genericRepeat`: advierte sobre llamadas repetidas a la misma herramienta con los mismos argumentos.
- `detectors.knownPollNoProgress`: advierte/bloquea sobre herramientas de sondeo conocidas (`process.poll`, `command_status`, etc.).
- `detectors.pingPong`: advierte/bloquea sobre patrones alternados por pares sin progreso.
- Si `warningThreshold >= criticalThreshold` o `criticalThreshold >= globalCircuitBreakerThreshold`, la validación falla.

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // o BRAVE_API_KEY env
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // opcional; omitir para detección automática
        maxChars: 50000,
        maxCharsCap: 50000,
        maxResponseBytes: 2000000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        maxRedirects: 3,
        readability: true,
        userAgent: "custom-ua",
      },
    },
  },
}
```

### `tools.media`

Configura el entendimiento de medios entrantes (imagen/audio/video):

```json5
{
  tools: {
    media: {
      concurrency: 2,
      asyncCompletion: {
        directSend: false, // activación opcional: enviar música/video asíncronos terminados directamente al canal
      },
      audio: {
        enabled: true,
        maxBytes: 20971520,
        scope: {
          default: "deny",
          rules: [{ action: "allow", match: { chatType: "direct" } }],
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { type: "cli", command: "whisper", args: ["--model", "base", "{{MediaPath}}"] },
        ],
      },
      video: {
        enabled: true,
        maxBytes: 52428800,
        models: [{ provider: "google", model: "gemini-3-flash-preview" }],
      },
    },
  },
}
```

<Accordion title="Campos de entrada del modelo de medios">

**Entrada de proveedor** (`type: "provider"` u omitido):

- `provider`: ID del proveedor de API (`openai`, `anthropic`, `google`/`gemini`, `groq`, etc.)
- `model`: sobrescritura del ID del modelo
- `profile` / `preferredProfile`: selección de perfil de `auth-profiles.json`

**Entrada CLI** (`type: "cli"`):

- `command`: ejecutable a ejecutar
- `args`: argumentos con plantillas (admite `{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}`, etc.)

**Campos comunes:**

- `capabilities`: lista opcional (`image`, `audio`, `video`). Valores predeterminados: `openai`/`anthropic`/`minimax` → image, `google` → image+audio+video, `groq` → audio.
- `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`: sobrescrituras por entrada.
- Los fallos pasan a la siguiente entrada.

La autenticación del proveedor sigue el orden estándar: `auth-profiles.json` → variables de entorno → `models.providers.*.apiKey`.

**Campos de finalización asíncrona:**

- `asyncCompletion.directSend`: cuando es `true`, las tareas completadas de
  `music_generate` y `video_generate` intentan primero la entrega directa al canal. Predeterminado: `false`
  (ruta heredada de despertar sesión solicitante/entrega por modelo).

</Accordion>

### `tools.agentToAgent`

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },
}
```

### `tools.sessions`

Controla qué sesiones pueden ser objetivo de las herramientas de sesión (`sessions_list`, `sessions_history`, `sessions_send`).

Predeterminado: `tree` (sesión actual + sesiones generadas por ella, como subagentes).

```json5
{
  tools: {
    sessions: {
      // "self" | "tree" | "agent" | "all"
      visibility: "tree",
    },
  },
}
```

Notas:

- `self`: solo la clave de sesión actual.
- `tree`: sesión actual + sesiones generadas por la sesión actual (subagentes).
- `agent`: cualquier sesión perteneciente al ID del agente actual (puede incluir otros usuarios si ejecutas sesiones por remitente bajo el mismo ID de agente).
- `all`: cualquier sesión. El direccionamiento entre agentes sigue requiriendo `tools.agentToAgent`.
- Restricción por sandbox: cuando la sesión actual está en sandbox y `agents.defaults.sandbox.sessionToolsVisibility="spawned"`, la visibilidad se fuerza a `tree` incluso si `tools.sessions.visibility="all"`.

### `tools.sessions_spawn`

Controla la compatibilidad con adjuntos en línea para `sessions_spawn`.

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // activación opcional: establece true para permitir adjuntos de archivo en línea
        maxTotalBytes: 5242880, // 5 MB total entre todos los archivos
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 MB por archivo
        retainOnSessionKeep: false, // conservar adjuntos cuando cleanup="keep"
      },
    },
  },
}
```

Notas:

- Los adjuntos solo son compatibles con `runtime: "subagent"`. El tiempo de ejecución ACP los rechaza.
- Los archivos se materializan en el workspace hijo en `.openclaw/attachments/<uuid>/` con un `.manifest.json`.
- El contenido de los adjuntos se redacta automáticamente de la persistencia de la transcripción.
- Las entradas base64 se validan con comprobaciones estrictas de alfabeto/relleno y una protección de tamaño antes de descodificar.
- Los permisos de archivo son `0700` para directorios y `0600` para archivos.
- La limpieza sigue la política `cleanup`: `delete` siempre elimina los adjuntos; `keep` los conserva solo cuando `retainOnSessionKeep: true`.

### `tools.experimental`

Indicadores experimentales para herramientas incorporadas. Desactivado por defecto salvo que se aplique una regla automática específica del tiempo de ejecución.

```json5
{
  tools: {
    experimental: {
      planTool: true, // habilitar update_plan experimental
    },
  },
}
```

Notas:

- `planTool`: habilita la herramienta estructurada `update_plan` para seguimiento de trabajo no trivial de varios pasos.
- Predeterminado: `false` para proveedores que no sean OpenAI. Las ejecuciones de OpenAI y OpenAI Codex la habilitan automáticamente.
- Cuando está habilitada, el system prompt también agrega orientación de uso para que el modelo solo la use en trabajos sustanciales y mantenga como máximo un paso `in_progress`.

### `agents.defaults.subagents`

```json5
{
  agents: {
    defaults: {
      subagents: {
        allowAgents: ["research"],
        model: "minimax/MiniMax-M2.7",
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

- `model`: modelo predeterminado para subagentes generados. Si se omite, los subagentes heredan el modelo del llamador.
- `allowAgents`: allowlist predeterminada de IDs de agente objetivo para `sessions_spawn` cuando el agente solicitante no establece su propio `subagents.allowAgents` (`["*"]` = cualquiera; predeterminado: solo el mismo agente).
- `runTimeoutSeconds`: tiempo de espera predeterminado (segundos) para `sessions_spawn` cuando la llamada a la herramienta omite `runTimeoutSeconds`. `0` significa sin tiempo de espera.
- Política de herramientas por subagente: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.

---

## Proveedores personalizados y URLs base

OpenClaw usa el catálogo incorporado de modelos. Agrega proveedores personalizados mediante `models.providers` en la configuración o `~/.openclaw/agents/<agentId>/agent/models.json`.

```json5
{
  models: {
    mode: "merge", // merge (predeterminado) | replace
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions", // openai-completions | openai-responses | anthropic-messages | google-generative-ai
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            contextTokens: 96000,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

- Usa `authHeader: true` + `headers` para necesidades de autenticación personalizadas.
- Sobrescribe la raíz de configuración del agente con `OPENCLAW_AGENT_DIR` (o `PI_CODING_AGENT_DIR`, alias heredado de variable de entorno).
- Precedencia de fusión para IDs de proveedor coincidentes:
  - Los valores no vacíos de `baseUrl` en `models.json` del agente tienen prioridad.
  - Los valores no vacíos de `apiKey` del agente tienen prioridad solo cuando ese proveedor no está gestionado por SecretRef en el contexto actual de configuración/perfil de autenticación.
  - Los valores `apiKey` de proveedores gestionados por SecretRef se actualizan desde marcadores de origen (`ENV_VAR_NAME` para refs de entorno, `secretref-managed` para refs de archivo/exec) en lugar de persistir secretos resueltos.
  - Los valores de cabecera de proveedor gestionados por SecretRef se actualizan desde marcadores de origen (`secretref-env:ENV_VAR_NAME` para refs de entorno, `secretref-managed` para refs de archivo/exec).
  - `apiKey`/`baseUrl` vacíos o ausentes en el agente usan como respaldo `models.providers` de la configuración.
  - `contextWindow`/`maxTokens` del modelo coincidente usan el valor más alto entre la configuración explícita y los valores implícitos del catálogo.
  - `contextTokens` del modelo coincidente conserva un límite explícito de tiempo de ejecución cuando está presente; úsalo para limitar el contexto efectivo sin cambiar los metadatos nativos del modelo.
  - Usa `models.mode: "replace"` cuando quieras que la configuración reescriba completamente `models.json`.
  - La persistencia de marcadores es autoritativa según la fuente: los marcadores se escriben desde la instantánea activa de configuración de origen (previa a la resolución), no desde valores secretos resueltos en tiempo de ejecución.

### Detalles de campos del proveedor

- `models.mode`: comportamiento del catálogo del proveedor (`merge` o `replace`).
- `models.providers`: mapa de proveedores personalizados indexado por ID de proveedor.
- `models.providers.*.api`: adaptador de solicitudes (`openai-completions`, `openai-responses`, `anthropic-messages`, `google-generative-ai`, etc).
- `models.providers.*.apiKey`: credencial del proveedor (prefiere SecretRef/sustitución de entorno).
- `models.providers.*.auth`: estrategia de autenticación (`api-key`, `token`, `oauth`, `aws-sdk`).
- `models.providers.*.injectNumCtxForOpenAICompat`: para Ollama + `openai-completions`, inyecta `options.num_ctx` en las solicitudes (predeterminado: `true`).
- `models.providers.*.authHeader`: fuerza el transporte de credenciales en la cabecera `Authorization` cuando sea necesario.
- `models.providers.*.baseUrl`: URL base de la API ascendente.
- `models.providers.*.headers`: cabeceras estáticas extra para enrutamiento por proxy/inquilino.
- `models.providers.*.request`: sobrescrituras de transporte para solicitudes HTTP del proveedor de modelos.
  - `request.headers`: cabeceras extra (fusionadas con las predeterminadas del proveedor). Los valores aceptan SecretRef.
  - `request.auth`: sobrescritura de estrategia de autenticación. Modos: `"provider-default"` (usar la autenticación incorporada del proveedor), `"authorization-bearer"` (con `token`), `"header"` (con `headerName`, `value`, opcional `prefix`).
  - `request.proxy`: sobrescritura de proxy HTTP. Modos: `"env-proxy"` (usar variables de entorno `HTTP_PROXY`/`HTTPS_PROXY`), `"explicit-proxy"` (con `url`). Ambos modos aceptan un subobjeto opcional `tls`.
  - `request.tls`: sobrescritura TLS para conexiones directas. Campos: `ca`, `cert`, `key`, `passphrase` (todos aceptan SecretRef), `serverName`, `insecureSkipVerify`.
- `models.providers.*.models`: entradas explícitas del catálogo de modelos del proveedor.
- `models.providers.*.models.*.contextWindow`: metadatos de ventana de contexto nativa del modelo.
- `models.providers.*.models.*.contextTokens`: límite opcional de contexto en tiempo de ejecución. Úsalo cuando quieras un presupuesto efectivo de contexto menor que el `contextWindow` nativo del modelo.
- `models.providers.*.models.*.compat.supportsDeveloperRole`: pista opcional de compatibilidad. Para `api: "openai-completions"` con `baseUrl` no vacío y no nativo (host distinto de `api.openai.com`), OpenClaw fuerza esto a `false` en tiempo de ejecución. Un `baseUrl` vacío/omitido mantiene el comportamiento predeterminado de OpenAI.
- `plugins.entries.amazon-bedrock.config.discovery`: raíz de ajustes de autodetección de Bedrock.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: activar/desactivar la detección implícita.
- `plugins.entries.amazon-bedrock.config.discovery.region`: región AWS para la detección.
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: filtro opcional por ID de proveedor para detección dirigida.
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: intervalo de sondeo para la actualización de detección.
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: ventana de contexto de respaldo para modelos detectados.
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: máximo de tokens de salida de respaldo para modelos detectados.

### Ejemplos de proveedores

<Accordion title="Cerebras (GLM 4.6 / 4.7)">

```json5
{
  env: { CEREBRAS_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: {
        primary: "cerebras/zai-glm-4.7",
        fallbacks: ["cerebras/zai-glm-4.6"],
      },
      models: {
        "cerebras/zai-glm-4.7": { alias: "GLM 4.7 (Cerebras)" },
        "cerebras/zai-glm-4.6": { alias: "GLM 4.6 (Cerebras)" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      cerebras: {
        baseUrl: "https://api.cerebras.ai/v1",
        apiKey: "${CEREBRAS_API_KEY}",
        api: "openai-completions",
        models: [
          { id: "zai-glm-4.7", name: "GLM 4.7 (Cerebras)" },
          { id: "zai-glm-4.6", name: "GLM 4.6 (Cerebras)" },
        ],
      },
    },
  },
}
```

Usa `cerebras/zai-glm-4.7` para Cerebras; `zai/glm-4.7` para Z.AI directo.

</Accordion>

<Accordion title="OpenCode">

```json5
{
  agents: {
    defaults: {
      model: { primary: "opencode/claude-opus-4-6" },
      models: { "opencode/claude-opus-4-6": { alias: "Opus" } },
    },
  },
}
```

Establece `OPENCODE_API_KEY` (o `OPENCODE_ZEN_API_KEY`). Usa referencias `opencode/...` para el catálogo Zen o `opencode-go/...` para el catálogo Go. Atajo: `openclaw onboard --auth-choice opencode-zen` o `openclaw onboard --auth-choice opencode-go`.

</Accordion>

<Accordion title="Z.AI (GLM-4.7)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "zai/glm-4.7" },
      models: { "zai/glm-4.7": {} },
    },
  },
}
```

Establece `ZAI_API_KEY`. `z.ai/*` y `z-ai/*` se aceptan como alias. Atajo: `openclaw onboard --auth-choice zai-api-key`.

- Endpoint general: `https://api.z.ai/api/paas/v4`
- Endpoint de código (predeterminado): `https://api.z.ai/api/coding/paas/v4`
- Para el endpoint general, define un proveedor personalizado con la sobrescritura de URL base.

</Accordion>

<Accordion title="Moonshot AI (Kimi)">

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: { "moonshot/kimi-k2.5": { alias: "Kimi K2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
        ],
      },
    },
  },
}
```

Para el endpoint de China: `baseUrl: "https://api.moonshot.cn/v1"` o `openclaw onboard --auth-choice moonshot-api-key-cn`.

Los endpoints nativos de Moonshot anuncian compatibilidad de uso de streaming en el transporte compartido
`openai-completions`, y OpenClaw ahora lo decide según las
capacidades del endpoint en lugar de solo por el ID integrado del proveedor.

</Accordion>

<Accordion title="Kimi Coding">

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi/kimi-code" },
      models: { "kimi/kimi-code": { alias: "Kimi Code" } },
    },
  },
}
```

Compatible con Anthropic, proveedor integrado. Atajo: `openclaw onboard --auth-choice kimi-code-api-key`.

</Accordion>

<Accordion title="Synthetic (compatible con Anthropic)">

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

La URL base debe omitir `/v1` (el cliente Anthropic lo añade). Atajo: `openclaw onboard --auth-choice synthetic-api-key`.

</Accordion>

<Accordion title="MiniMax M2.7 (directo)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.7" },
      models: {
        "minimax/MiniMax-M2.7": { alias: "Minimax" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

Establece `MINIMAX_API_KEY`. Atajos:
`openclaw onboard --auth-choice minimax-global-api` o
`openclaw onboard --auth-choice minimax-cn-api`.
El catálogo de modelos ahora usa por defecto solo M2.7.
En la ruta de streaming compatible con Anthropic, OpenClaw desactiva el thinking de MiniMax
de forma predeterminada a menos que establezcas tú mismo `thinking`.
`/fast on` o `params.fastMode: true` reescribe `MiniMax-M2.7` a
`MiniMax-M2.7-highspeed`.

</Accordion>

<Accordion title="Modelos locales (LM Studio)">

Consulta [Modelos locales](/es/gateway/local-models). En resumen: ejecuta un modelo local grande mediante la API Responses de LM Studio en hardware serio; conserva los modelos alojados fusionados como respaldo.

</Accordion>

---

## Skills

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm", // npm | pnpm | yarn | bun
    },
    entries: {
      "image-lab": {
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // o cadena de texto plano
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: allowlist opcional solo para Skills agrupadas (las Skills administradas/del workspace no se ven afectadas).
- `load.extraDirs`: raíces extra de Skills compartidas (precedencia más baja).
- `install.preferBrew`: cuando es true, prefiere instaladores Homebrew cuando `brew` está
  disponible antes de recurrir a otros tipos de instalador.
- `install.nodeManager`: preferencia del instalador de Node para especificaciones `metadata.openclaw.install`
  (`npm` | `pnpm` | `yarn` | `bun`).
- `entries.<skillKey>.enabled: false` desactiva una Skill incluso si está agrupada/instalada.
- `entries.<skillKey>.apiKey`: campo de conveniencia para Skills que declaran una variable de entorno principal (cadena de texto plano u objeto SecretRef).

---

## Plugins

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: [],
    load: {
      paths: ["~/Projects/oss/voice-call-extension"],
    },
    entries: {
      "voice-call": {
        enabled: true,
        hooks: {
          allowPromptInjection: false,
        },
        config: { provider: "twilio" },
      },
    },
  },
}
```

- Se cargan desde `~/.openclaw/extensions`, `<workspace>/.openclaw/extensions`, más `plugins.load.paths`.
- La detección acepta plugins nativos de OpenClaw más paquetes compatibles de Codex y Claude, incluidos paquetes Claude sin manifest y con disposición predeterminada.
- **Los cambios de configuración requieren reiniciar el gateway.**
- `allow`: allowlist opcional (solo se cargan los plugins listados). `deny` tiene prioridad.
- `plugins.entries.<id>.apiKey`: campo de conveniencia de clave API a nivel de plugin (cuando el plugin lo admite).
- `plugins.entries.<id>.env`: mapa de variables de entorno con ámbito de plugin.
- `plugins.entries.<id>.hooks.allowPromptInjection`: cuando es `false`, el núcleo bloquea `before_prompt_build` e ignora campos que mutan prompts desde `before_agent_start` heredado, mientras preserva `modelOverride` y `providerOverride` heredados. Se aplica a hooks nativos de plugins y a directorios de hooks proporcionados por paquetes compatibles.
- `plugins.entries.<id>.subagent.allowModelOverride`: confía explícitamente en este plugin para solicitar sobrescrituras de `provider` y `model` por ejecución para ejecuciones en segundo plano de subagentes.
- `plugins.entries.<id>.subagent.allowedModels`: allowlist opcional de destinos canónicos `provider/model` para sobrescrituras confiables de subagentes. Usa `"*"` solo si intencionalmente quieres permitir cualquier modelo.
- `plugins.entries.<id>.config`: objeto de configuración definido por el plugin (validado por el esquema del plugin nativo de OpenClaw cuando está disponible).
- `plugins.entries.firecrawl.config.webFetch`: ajustes del proveedor de obtención web Firecrawl.
  - `apiKey`: clave API de Firecrawl (acepta SecretRef). Usa como respaldo `plugins.entries.firecrawl.config.webSearch.apiKey`, `tools.web.fetch.firecrawl.apiKey` heredado o la variable de entorno `FIRECRAWL_API_KEY`.
  - `baseUrl`: URL base de la API Firecrawl (predeterminado: `https://api.firecrawl.dev`).
  - `onlyMainContent`: extraer solo el contenido principal de las páginas (predeterminado: `true`).
  - `maxAgeMs`: antigüedad máxima de caché en milisegundos (predeterminado: `172800000` / 2 días).
  - `timeoutSeconds`: tiempo de espera de la solicitud de scraping en segundos (predeterminado: `60`).
- `plugins.entries.xai.config.xSearch`: ajustes de xAI X Search (búsqueda web de Grok).
  - `enabled`: habilitar el proveedor X Search.
  - `model`: modelo Grok que se usará para la búsqueda (p. ej. `"grok-4-1-fast"`).
- `plugins.entries.memory-core.config.dreaming`: ajustes de dreaming de memoria (experimental). Consulta [Dreaming](/es/concepts/dreaming) para fases y umbrales.
  - `enabled`: interruptor maestro de dreaming (predeterminado `false`).
  - `frequency`: cadencia cron para cada barrido completo de dreaming (`"0 3 * * *"` de forma predeterminada).
  - la política de fases y los umbrales son detalles de implementación (no claves de configuración orientadas al usuario).
- Los plugins habilitados de paquetes Claude también pueden aportar valores predeterminados Pi integrados desde `settings.json`; OpenClaw los aplica como ajustes saneados del agente, no como parches directos de configuración de OpenClaw.
- `plugins.slots.memory`: elige el ID del plugin de memoria activo, o `"none"` para desactivar plugins de memoria.
- `plugins.slots.contextEngine`: elige el ID del plugin de motor de contexto activo; el predeterminado es `"legacy"` salvo que instales y selecciones otro motor.
- `plugins.installs`: metadatos de instalación administrados por la CLI usados por `openclaw plugins update`.
  - Incluye `source`, `spec`, `sourcePath`, `installPath`, `version`, `resolvedName`, `resolvedVersion`, `resolvedSpec`, `integrity`, `shasum`, `resolvedAt`, `installedAt`.
  - Trata `plugins.installs.*` como estado administrado; prefiere comandos CLI antes que ediciones manuales.

Consulta [Plugins](/es/tools/plugin).

---

## Navegador

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    defaultProfile: "user",
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true, // modo predeterminado de red de confianza
      // allowPrivateNetwork: true, // alias heredado
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: { driver: "existing-session", attachOnly: true, color: "#00AA00" },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    color: "#FF4500",
    // headless: false,
    // noSandbox: false,
    // extraArgs: [],
    // executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    // attachOnly: false,
  },
}
```

- `evaluateEnabled: false` desactiva `act:evaluate` y `wait --fn`.
- `ssrfPolicy.dangerouslyAllowPrivateNetwork` usa `true` por defecto cuando no está configurado (modelo de red de confianza).
- Establece `ssrfPolicy.dangerouslyAllowPrivateNetwork: false` para navegación estricta del navegador solo a redes públicas.
- En modo estricto, los endpoints de perfil CDP remoto (`profiles.*.cdpUrl`) están sujetos al mismo bloqueo de red privada durante comprobaciones de alcance/detección.
- `ssrfPolicy.allowPrivateNetwork` sigue siendo compatible como alias heredado.
- En modo estricto, usa `ssrfPolicy.hostnameAllowlist` y `ssrfPolicy.allowedHostnames` para excepciones explícitas.
- Los perfiles remotos son solo de conexión (start/stop/reset desactivados).
- `profiles.*.cdpUrl` acepta `http://`, `https://`, `ws://` y `wss://`.
  Usa HTTP(S) cuando quieras que OpenClaw descubra `/json/version`; usa WS(S)
  cuando tu proveedor te dé una URL WebSocket directa de DevTools.
- Los perfiles `existing-session` son solo del host y usan Chrome MCP en lugar de CDP.
- Los perfiles `existing-session` pueden establecer `userDataDir` para apuntar a un perfil específico
  de navegador basado en Chromium como Brave o Edge.
- Los perfiles `existing-session` conservan los límites actuales de ruta de Chrome MCP:
  acciones basadas en snapshot/ref en lugar de direccionamiento por selector CSS, hooks de subida
  de un solo archivo, sin sobrescrituras de tiempo de espera para diálogos, sin `wait --load networkidle`,
  ni `responsebody`, exportación PDF, interceptación de descargas o acciones por lotes.
- Los perfiles locales administrados `openclaw` autoasignan `cdpPort` y `cdpUrl`; solo
  establece `cdpUrl` explícitamente para CDP remoto.
- Orden de autodetección: navegador predeterminado si está basado en Chromium → Chrome → Brave → Edge → Chromium → Chrome Canary.
- Servicio de control: solo loopback (puerto derivado de `gateway.port`, predeterminado `18791`).
- `extraArgs` agrega flags extra de lanzamiento al inicio local de Chromium (por ejemplo
  `--disable-gpu`, tamaño de ventana o flags de depuración).

---

## UI

```json5
{
  ui: {
    seamColor: "#FF4500",
    assistant: {
      name: "OpenClaw",
      avatar: "CB", // emoji, texto corto, URL de imagen o URI data
    },
  },
}
```

- `seamColor`: color de acento para el chrome de la UI de la app nativa (tono de la burbuja de Talk Mode, etc.).
- `assistant`: sobrescritura de identidad de la Control UI. Usa como respaldo la identidad del agente activo.

---

## Gateway

```json5
{
  gateway: {
    mode: "local", // local | remote
    port: 18789,
    bind: "loopback",
    auth: {
      mode: "token", // none | token | password | trusted-proxy
      token: "your-token",
      // password: "your-password", // o OPENCLAW_GATEWAY_PASSWORD
      // trustedProxy: { userHeader: "x-forwarded-user" }, // para mode=trusted-proxy; consulta /gateway/trusted-proxy-auth
      allowTailscale: true,
      rateLimit: {
        maxAttempts: 10,
        windowMs: 60000,
        lockoutMs: 300000,
        exemptLoopback: true,
      },
    },
    tailscale: {
      mode: "off", // off | serve | funnel
      resetOnExit: false,
    },
    controlUi: {
      enabled: true,
      basePath: "/openclaw",
      // root: "dist/control-ui",
      // allowedOrigins: ["https://control.example.com"], // requerido para Control UI no loopback
      // dangerouslyAllowHostHeaderOriginFallback: false, // modo peligroso de respaldo de origen por cabecera Host
      // allowInsecureAuth: false,
      // dangerouslyDisableDeviceAuth: false,
    },
    remote: {
      url: "ws://gateway.tailnet:18789",
      transport: "ssh", // ssh | direct
      token: "your-token",
      // password: "your-password",
    },
    trustedProxies: ["10.0.0.1"],
    // Opcional. Predeterminado false.
    allowRealIpFallback: false,
    tools: {
      // Denegaciones HTTP adicionales para /tools/invoke
      deny: ["browser"],
      // Eliminar herramientas de la lista predeterminada de denegación HTTP
      allow: ["gateway"],
    },
    push: {
      apns: {
        relay: {
          baseUrl: "https://relay.example.com",
          timeoutMs: 10000,
        },
      },
    },
  },
}
```

<Accordion title="Detalles de campos del Gateway">

- `mode`: `local` (ejecutar gateway) o `remote` (conectarse a un gateway remoto). Gateway se niega a iniciarse salvo que sea `local`.
- `port`: puerto multiplexado único para WS + HTTP. Precedencia: `--port` > `OPENCLAW_GATEWAY_PORT` > `gateway.port` > `18789`.
- `bind`: `auto`, `loopback` (predeterminado), `lan` (`0.0.0.0`), `tailnet` (solo IP de Tailscale) o `custom`.
- **Alias heredados de bind**: usa valores de modo bind en `gateway.bind` (`auto`, `loopback`, `lan`, `tailnet`, `custom`), no alias de host (`0.0.0.0`, `127.0.0.1`, `localhost`, `::`, `::1`).
- **Nota sobre Docker**: el bind predeterminado `loopback` escucha en `127.0.0.1` dentro del contenedor. Con redes bridge de Docker (`-p 18789:18789`), el tráfico llega por `eth0`, así que el gateway queda inaccesible. Usa `--network host`, o establece `bind: "lan"` (o `bind: "custom"` con `customBindHost: "0.0.0.0"`) para escuchar en todas las interfaces.
- **Auth**: requerida de forma predeterminada. Los binds que no son loopback requieren autenticación del gateway. En la práctica, eso significa un token/contraseña compartidos o un proxy inverso con identidad gestionada con `gateway.auth.mode: "trusted-proxy"`. El asistente de incorporación genera un token por defecto.
- Si tanto `gateway.auth.token` como `gateway.auth.password` están configurados (incluidos SecretRefs), establece `gateway.auth.mode` explícitamente en `token` o `password`. El inicio y los flujos de instalación/reparación del servicio fallan cuando ambos están configurados y no hay modo definido.
- `gateway.auth.mode: "none"`: modo explícito sin autenticación. Úsalo solo para configuraciones locales loopback de confianza; esto intencionalmente no se ofrece en los prompts de incorporación.
- `gateway.auth.mode: "trusted-proxy"`: delega la autenticación a un proxy inverso con identidad gestionada y confía en cabeceras de identidad desde `gateway.trustedProxies` (consulta [Trusted Proxy Auth](/es/gateway/trusted-proxy-auth)). Este modo espera una fuente de proxy **que no sea loopback**; los proxies inversos loopback en el mismo host no satisfacen la autenticación trusted-proxy.
- `gateway.auth.allowTailscale`: cuando es `true`, las cabeceras de identidad de Tailscale Serve pueden satisfacer la autenticación de Control UI/WebSocket (verificada mediante `tailscale whois`). Los endpoints HTTP API **no** usan esa autenticación por cabecera de Tailscale; siguen el modo normal de autenticación HTTP del gateway. Este flujo sin token asume que el host del gateway es de confianza. Usa `true` por defecto cuando `tailscale.mode = "serve"`.
- `gateway.auth.rateLimit`: limitador opcional de autenticaciones fallidas. Se aplica por IP cliente y por ámbito de autenticación (los secretos compartidos y los tokens de dispositivo se rastrean por separado). Los intentos bloqueados devuelven `429` + `Retry-After`.
  - En la ruta asíncrona de Tailscale Serve Control UI, los intentos fallidos del mismo `{scope, clientIp}` se serializan antes de escribir el fallo. Por tanto, intentos incorrectos concurrentes del mismo cliente pueden activar el limitador en la segunda solicitud en vez de dejar pasar ambas como simples discrepancias.
  - `gateway.auth.rateLimit.exemptLoopback` usa `true` por defecto; establece `false` cuando intencionalmente quieras limitar también el tráfico localhost (para entornos de prueba o despliegues estrictos con proxy).
- Los intentos de autenticación WS originados en navegador siempre se limitan con la exención de loopback desactivada (defensa en profundidad frente a ataques de fuerza bruta de localhost desde navegador).
- En loopback, esos bloqueos por origen de localhost se aíslan por valor `Origin`
  normalizado, de modo que fallos repetidos de un origen localhost no bloqueen automáticamente
  a otro origen distinto.
- `tailscale.mode`: `serve` (solo tailnet, bind loopback) o `funnel` (público, requiere auth).
- `controlUi.allowedOrigins`: allowlist explícita de origen de navegador para conexiones WebSocket del Gateway. Requerida cuando se esperan clientes de navegador desde orígenes que no sean loopback.
- `controlUi.dangerouslyAllowHostHeaderOriginFallback`: modo peligroso que habilita el respaldo de origen por cabecera Host para despliegues que dependen intencionalmente de esa política.
- `remote.transport`: `ssh` (predeterminado) o `direct` (ws/wss). Para `direct`, `remote.url` debe ser `ws://` o `wss://`.
- `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`: sobrescritura break-glass del lado cliente que permite `ws://` en texto plano hacia IP privadas de confianza; el valor predeterminado sigue siendo permitir texto plano solo en loopback.
- `gateway.remote.token` / `.password` son campos de credencial del cliente remoto. No configuran por sí mismos la autenticación del gateway.
- `gateway.push.apns.relay.baseUrl`: URL HTTPS base del relay APNs externo usado por compilaciones oficiales/TestFlight de iOS después de que publiquen registros respaldados por relay al gateway. Esta URL debe coincidir con la URL del relay compilada en la app iOS.
- `gateway.push.apns.relay.timeoutMs`: tiempo de espera en milisegundos para los envíos gateway→relay. Predeterminado: `10000`.
- Los registros respaldados por relay se delegan a una identidad específica del gateway. La app iOS emparejada obtiene `gateway.identity.get`, incluye esa identidad en el registro del relay y reenvía un permiso de envío con ámbito de registro al gateway. Otro gateway no puede reutilizar ese registro almacenado.
- `OPENCLAW_APNS_RELAY_BASE_URL` / `OPENCLAW_APNS_RELAY_TIMEOUT_MS`: sobrescrituras temporales por entorno para la configuración del relay anterior.
- `OPENCLAW_APNS_RELAY_ALLOW_HTTP=true`: escape hatch solo para desarrollo para URLs de relay HTTP en loopback. Las URLs de relay de producción deberían seguir usando HTTPS.
- `gateway.channelHealthCheckMinutes`: intervalo en minutos del monitor de salud de canales. Establece `0` para desactivar globalmente los reinicios del monitor de salud. Predeterminado: `5`.
- `gateway.channelStaleEventThresholdMinutes`: umbral en minutos para sockets obsoletos. Mantenlo mayor o igual que `gateway.channelHealthCheckMinutes`. Predeterminado: `30`.
- `gateway.channelMaxRestartsPerHour`: máximo de reinicios por canal/cuenta en una hora móvil. Pred