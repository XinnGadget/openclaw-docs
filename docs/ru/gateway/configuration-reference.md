-----

title: "Справочник по конфигурации"
summary: "Справочник конфигурации шлюза для основных ключей OpenClaw, значений по умолчанию и ссылок на выделенные справочники подсистем"
read_when:

  - Вам нужны точные семантики конфигурации на уровне полей или значения по умолчанию
  - Вы проверяете блоки конфигурации каналов, моделей, шлюзов или инструментов

-----

# Справочник по конфигурации

Основной справочник конфигурации для `~/.openclaw/openclaw.json`. Для обзора, ориентированного на задачи, см. [Конфигурация](https://www.google.com/search?q=/gateway/configuration).

Эта страница охватывает основные поверхности конфигурации OpenClaw и содержит ссылки на разделы, когда подсистема имеет собственный глубокий справочник. Здесь **не** предпринимается попытка вставить каждый каталог команд, принадлежащий каналу/плагину, или каждую глубокую настройку памяти/QMD на одной странице.

Техническая спецификация (Code truth):

  - `openclaw config schema` выводит актуальную схему JSON Schema, используемую для валидации и Control UI, с объединенными метаданными бандлов/плагинов/каналов, если они доступны
  - `config.schema.lookup` возвращает один узел схемы с ограниченной областью пути для инструментов детализации
  - `pnpm config:docs:check` / `pnpm config:docs:gen` проверяют соответствие базового хеша документации текущей поверхности схемы

Специализированные справочники:

  - [Справочник конфигурации памяти](https://www.google.com/search?q=/reference/memory-config) для `agents.defaults.memorySearch.*`, `memory.qmd.*`, `memory.citations` и настроек дриминга в `plugins.entries.memory-core.config.dreaming`
  - [Слэш-команды](https://www.google.com/search?q=/tools/slash-commands) для текущего каталога встроенных и поставляемых в комплекте команд
  - Страницы соответствующих каналов/плагинов для поверхностей команд, специфичных для канала

Формат конфигурации — **JSON5** (разрешены комментарии и замыкающие запятые). Все поля необязательны — OpenClaw использует безопасные значения по умолчанию, если они опущены.

-----

## Каналы (Channels)

Каждый канал запускается автоматически, если существует его секция конфигурации (за исключением случаев `enabled: false`).

### Доступ к DM и группам

Все каналы поддерживают политики DM (личных сообщений) и групп:

| Политика DM         | Поведение                                                                           |
| ------------------- | ----------------------------------------------------------------------------------- |
| `pairing` (по умолчанию) | Неизвестные отправители получают разовый код сопряжения; владелец должен подтвердить |
| `allowlist`         | Только отправители из `allowFrom` (или хранилища разрешенных сопряжений)            |
| `open`              | Разрешить все входящие DM (требуется `allowFrom: ["*"]`)                            |
| `disabled`          | Игнорировать все входящие DM                                                        |

| Политика групп        | Поведение                                                                   |
| --------------------- | --------------------------------------------------------------------------- |
| `allowlist` (по умолчанию) | Только группы, соответствующие настроенному белому списку                   |
| `open`                | Обход белых списков групп (фильтрация по упоминанию по-прежнему применяется) |
| `disabled`            | Блокировать все сообщения в группах/комнатах                                |

<Note\>
`channels.defaults.groupPolicy` устанавливает значение по умолчанию, если `groupPolicy` провайдера не задано.
Коды сопряжения истекают через 1 час. Ожидающие запросы на сопряжение DM ограничены **3 на канал**.
Если блок провайдера полностью отсутствует (`channels.&lt;provider&gt;` отсутствует), политика групп во время выполнения откатывается к `allowlist` (закрытый режим) с предупреждением при запуске.
</Note\>

### Переопределение моделей каналов

Используйте `channels.modelByChannel`, чтобы закрепить конкретные ID каналов за определенной моделью. Значения принимают формат `provider/model` или настроенные алиасы моделей. Сопоставление каналов применяется, когда сессия еще не имеет переопределения модели (например, установленного через `/model`).

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

### Настройки каналов по умолчанию и Heartbeat

Используйте `channels.defaults` для общей политики групп и поведения heartbeat (контрольного сигнала) для всех провайдеров:

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

  - `channels.defaults.groupPolicy`: резервная политика групп, когда `groupPolicy` на уровне провайдера не задана.
  - `channels.defaults.contextVisibility`: режим видимости дополнительного контекста по умолчанию для всех каналов. Значения: `all` (по умолчанию, включать весь контекст цитат/тредов/истории), `allowlist` (включать контекст только от разрешенных отправителей), `allowlist_quote` (аналогично allowlist, но сохранять явный контекст цитат/ответов). Переопределение для конкретного канала: `channels.<channel>.contextVisibility`.
  - `channels.defaults.heartbeat.showOk`: включать статусы исправных каналов в вывод heartbeat.
  - `channels.defaults.heartbeat.showAlerts`: включать статусы деградации/ошибок в вывод heartbeat.
  - `channels.defaults.heartbeat.useIndicator`: отрисовывать компактный вывод heartbeat в виде индикатора.

### WhatsApp

WhatsApp работает через веб-канал шлюза (Baileys Web). Он запускается автоматически при наличии связанной сессии.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // синие галочки (false в режиме чата с самим собой)
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

<Accordion title="Мультиаккаунт WhatsApp"\>

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

  - Исходящие команды по умолчанию используют аккаунт `default`, если он присутствует; в противном случае — первый настроенный ID аккаунта (отсортированный).
  - Необязательный параметр `channels.whatsapp.defaultAccount` переопределяет этот выбор аккаунта по умолчанию, если он совпадает с настроенным ID аккаунта.
  - Устаревший каталог аутентификации Baileys для одного аккаунта мигрирует с помощью `openclaw doctor` в `whatsapp/default`.
  - Переопределения для каждого аккаунта: `channels.whatsapp.accounts.<id>.sendReadReceipts`, `channels.whatsapp.accounts.<id>.dmPolicy`, `channels.whatsapp.accounts.<id>.allowFrom`.

</Accordion\>

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
          systemPrompt: "Keep answers brief.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Stay on topic.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" },
      ],
      historyLimit: 50,
      replyToMode: "first", // off | first | all | batched
      linkPreview: true,
      streaming: "partial", // off | partial | block | progress (по умолчанию off; включите явно, чтобы избежать лимитов на редактирование превью)
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

  - Токен бота: `channels.telegram.botToken` или `channels.telegram.tokenFile` (только обычный файл; симлинки отклоняются), с `TELEGRAM_BOT_TOKEN` в качестве резервного варианта для аккаунта по умолчанию.
  - Необязательный параметр `channels.telegram.defaultAccount` переопределяет выбор аккаунта по умолчанию.
  - В мультиаккаунтных конфигурациях (2+ ID аккаунтов) установите явный аккаунт по умолчанию (`channels.telegram.defaultAccount` или `channels.telegram.accounts.default`), чтобы избежать ошибок маршрутизации; `openclaw doctor` выдает предупреждение, если он отсутствует или невалиден.
  - `configWrites: false` блокирует запись конфигурации, инициированную из Telegram (миграции ID супергрупп, `/config set|unset`).
  - Записи `bindings[]` верхнего уровня с `type: "acp"` настраивают постоянные привязки ACP для тем форумов (используйте канонический `chatId:topic:topicId` в `match.peer.id`). Семантика полей описана в [ACP Агенты](https://www.google.com/search?q=/tools/acp-agents%23channel-specific-settings).
  - Стриминг превью в Telegram использует `sendMessage` + `editMessageText` (работает в личных и групповых чатах).
  - Политика повторов: см. [Политика повторов](https://www.google.com/search?q=/concepts/retry).

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
              systemPrompt: "Short answers only.",
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length", // length | newline
      streaming: "off", // off | partial | block | progress (progress соответствует partial в Discord)
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
        spawnSubagentSessions: false, // включение для sessions_spawn({ thread: true })
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

  - Токен: `channels.discord.token`, с `DISCORD_BOT_TOKEN` в качестве резервного варианта.
  - Прямые исходящие вызовы, предоставляющие явный `token` Discord, используют этот токен для вызова; настройки повторов/политик аккаунта по-прежнему берутся из выбранного аккаунта в активном снимке выполнения.
  - Необязательный `channels.discord.defaultAccount` переопределяет выбор аккаунта по умолчанию.
  - Используйте `user:<id>` (DM) или `channel:<id>` (канал гильдии) для целей доставки; чистые числовые ID отклоняются.
  - Слаги (slugs) гильдий пишутся в нижнем регистре с заменой пробелов на `-`; ключи каналов используют имя в виде слага (без `#`). Предпочтительнее использовать ID гильдий.
  - Сообщения, созданные ботами, по умолчанию игнорируются. `allowBots: true` разрешает их; используйте `allowBots: "mentions"`, чтобы принимать только те сообщения ботов, которые упоминают текущего бота.
  - `channels.discord.guilds.<id>.ignoreOtherMentions` (и переопределения каналов) отбрасывает сообщения, которые упоминают другого пользователя или роль, но не бота (исключая @everyone/@here).
  - `maxLinesPerMessage` (по умолчанию 17) разделяет длинные сообщения, даже если они меньше 2000 символов.
  - `channels.discord.threadBindings` управляет маршрутизацией, привязанной к тредам Discord:
      - `enabled`: переопределение Discord для функций сессий, привязанных к тредам.
      - `idleHours`: переопределение для авто-отключения при неактивности (в часах, `0` — отключено).
      - `maxAgeHours`: переопределение для жесткого максимального возраста (в часах, `0` — отключено).
      - `spawnSubagentSessions`: переключатель для автоматического создания тредов/привязки при `sessions_spawn({ thread: true })`.
  - `channels.discord.ui.components.accentColor` устанавливает акцентный цвет для контейнеров компонентов Discord v2.
  - `channels.discord.voice` включает голосовые беседы в каналах и опциональные переопределения автоподключения и TTS.
  - `channels.discord.voice.daveEncryption` и `channels.discord.voice.decryptionFailureTolerance` передаются в опции DAVE `@discordjs/voice` (`true` и `24` по умолчанию).
  - OpenClaw дополнительно пытается восстановить прием голоса, покидая и снова присоединяясь к голосовой сессии после повторяющихся ошибок расшифровки.
  - `channels.discord.streaming` — канонический ключ режима стриминга. Устаревшие значения `streamMode` и булево `streaming` мигрируют автоматически.
  - `channels.discord.autoPresence` сопоставляет доступность среды выполнения с присутствием бота (исправен =\> online, деградирован =\> idle, исчерпан =\> dnd) и позволяет переопределять текст статуса.

**Режимы уведомлений о реакциях:** `off` (нет), `own` (сообщения бота, по умолчанию), `all` (все сообщения), `allowlist` (из `guilds.<id>.users` на всех сообщениях).

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

  - JSON сервисного аккаунта: встроенный (`serviceAccount`) или файловый (`serviceAccountFile`).
  - Также поддерживается ссылка на секрет сервисного аккаунта (`serviceAccountRef`).
  - Резервные переменные окружения: `GOOGLE_CHAT_SERVICE_ACCOUNT` или `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
  - Используйте `spaces/<spaceId>` или `users/<userId>` для целей доставки.
  - `channels.googlechat.dangerouslyAllowNameMatching` снова включает сопоставление по email (режим экстренной совместимости).

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
          systemPrompt: "Short answers only.",
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
      streaming: {
        mode: "partial", // off | partial | block | progress
        nativeTransport: true, // использовать Slack native streaming API при mode=partial
      },
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

  - **Socket mode** требует наличия и `botToken`, и `appToken`.
  - **HTTP mode** требует `botToken` плюс `signingSecret`.
  - Токены и секреты принимают обычные строки или объекты SecretRef.
  - Аккаунты Slack предоставляют поля источника/статуса для учетных данных. `configured_unavailable` означает, что аккаунт настроен через SecretRef, но текущий путь выполнения не смог разрешить значение секрета.
  - `configWrites: false` блокирует запись конфигурации из Slack.
  - `channels.slack.streaming.mode` — канонический ключ режима стриминга для Slack.

**Режимы уведомлений о реакциях:** `off`, `own` (по умолчанию), `all`, `allowlist`.

**Изоляция сессий тредов:** `thread.historyScope` работает на уровне треда (по умолчанию) или разделяется на весь канал. `thread.inheritParent` копирует транскрипт родительского канала в новые треды.

  - Нативный стриминг Slack и статус треда "печатает..." в стиле ассистента требуют доставки в тред. DM верхнего уровня по умолчанию остаются вне треда.
  - `typingReaction` добавляет временную реакцию на входящее сообщение Slack, пока готовится ответ, и удаляет ее по завершении.

| Группа действий | По умолчанию | Примечания                         |
| --------------- | ------------ | ---------------------------------- |
| reactions       | включено     | Реакции + список реакций           |
| messages        | включено     | Чтение/отправка/правка/удаление    |
| pins            | включено     | Закрепление/открепление/список     |
| memberInfo      | включено     | Информация об участниках           |
| emojiList       | включено     | Список пользовательских эмодзи     |

### Mattermost

Mattermost поставляется как плагин: `openclaw plugins install @openclaw/mattermost`.

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
        native: true, // включение
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

Режимы чата: `oncall` (ответ при @-упоминании, по умолчанию), `onmessage` (на каждое сообщение), `onchar` (сообщения, начинающиеся с триггерного префикса).

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // опциональная привязка аккаунта
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

### BlueBubbles

BlueBubbles — рекомендуемый путь для iMessage (на базе плагина, настраивается в `channels.bluebubbles`).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
    },
  },
}
```

### iMessage

OpenClaw запускает `imsg rpc` (JSON-RPC через stdio). Демон или порт не требуются.

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

  - Требуется Full Disk Access (полный доступ к диску) для БД сообщений.
  - Предпочтительнее цели `chat_id:<id>`. Используйте `imsg chats --limit 20` для вывода списка чатов.

### Matrix

Matrix работает на базе расширения и настраивается в `channels.matrix`.

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

### Microsoft Teams

Microsoft Teams работает на базе расширения и настраивается в `channels.msteams`.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
    },
  },
}
```

### IRC

IRC работает на базе расширения и настраивается в `channels.irc`.

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

-----

## Настройки агентов по умолчанию (Agent defaults)

### `agents.defaults.workspace`

По умолчанию: `~/.openclaw/workspace`.

### `agents.defaults.skills`

Список разрешенных навыков по умолчанию для агентов, которые не устанавливают `agents.list[].skills`.

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // наследует github, weather
      { id: "docs", skills: ["docs-search"] }, // заменяет значения по умолчанию
      { id: "locked-down", skills: [] }, // навыков нет
    ],
  },
}
```

### `agents.defaults.imageMaxDimensionPx`

Максимальный размер пикселей для длинной стороны изображения перед вызовами провайдера. По умолчанию: `1200`.

### `agents.defaults.model`

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
      },
      // ... настройки моделей для генерации видео/аудио/PDF
      params: { cacheRetention: "long" },
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
      thinkingDefault: "low",
      verboseDefault: "off",
      elevatedDefault: "on",
      timeoutSeconds: 600,
      contextTokens: 200000,
      maxConcurrent: 3,
    },
  },
}
```

  - `model`: принимает либо строку (`"provider/model"`), либо объект (`{ primary, fallbacks }`).
  - `imageGenerationModel`: используется встроенной способностью генерации изображений.
  - `maxConcurrent`: максимальное количество параллельных запусков агентов в сессиях.

**Встроенные алиасы (сокращения):**

| Алиас               | Модель                                  |
| ------------------- | -------------------------------------- |
| `opus`              | `anthropic/claude-opus-4-6`            |
| `sonnet`            | `anthropic/claude-sonnet-4-6`          |
| `gpt`               | `openai/gpt-5.4`                       |
| `gemini`            | `google/gemini-3.1-pro-preview`        |

### `agents.defaults.heartbeat`

Периодические запуски контрольных сигналов (heartbeat).

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        model: "openai/gpt-5.4-mini",
        isolatedSession: false,
        prompt: "Read HEARTBEAT.md if it exists...",
      },
    },
  },
}
```

### `agents.defaults.compaction` (Компактизация)

Управление сжатием истории контекста.

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        timeoutSeconds: 900,
        notifyUser: true,
        memoryFlush: {
          enabled: true,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
        },
      },
    },
  },
}
```

### `agents.defaults.sandbox`

Опциональная изоляция в песочнице для встроенного агента.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        backend: "docker", // docker | ssh | openshell
        workspaceAccess: "none", // none | ro | rw
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          memory: "1g",
          cpus: 1,
        },
      },
    },
  },
}
```

-----

## Мультиагентная маршрутизация

Запуск нескольких изолированных агентов внутри одного Шлюза.

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

-----

## Сессия (Session)

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main",
    reset: {
      mode: "daily",
      atHour: 4,
    },
    maintenance: {
      mode: "warn",
      pruneAfter: "30d",
      maxDiskBytes: "500mb",
    },
  },
}
```

  - `scope`: базовая стратегия группировки сессий для контекстов групповых чатов (`per-sender` или `global`).
  - `dmScope`: как группируются личные сообщения (DMs).

-----

## Сообщения (Messages)

```json5
{
  messages: {
    responsePrefix: "🦞",
    ackReaction: "👀",
    tts: {
      auto: "off",
      provider: "elevenlabs",
    },
  },
}
```

### Префикс ответа (Response prefix)

Разрешение (наиболее специфичное побеждает): аккаунт → канал → глобально. `""` отключает префикс.

### Реакция подтверждения (Ack reaction)

  - По умолчанию — эмодзи `identity` активного агента, иначе `"👀"`. Установите `""` для отключения.
  - Область действия: `group-mentions` (по умолчанию), `group-all`, `direct`, `all`.

-----

## Инструменты (Tools)

### Профили инструментов

`tools.profile` устанавливает базовый белый список перед применением `tools.allow`/`tools.deny`:

| Профиль     | Включает                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | только `session_status`                                                                                                         |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                       |
| `full`      | без ограничений                                                                                                                 |

### Определение циклов инструментов (Loop detection)

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      warningThreshold: 10,
      criticalThreshold: 20,
    },
  },
}
```

-----

## Веб-инструменты (Tools Web)

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key",
      },
      fetch: {
        enabled: true,
        maxChars: 50000,
      },
    },
  },
}
```

-----

## Кастомные провайдеры и базовые URL

Добавьте собственных провайдеров через `models.providers` в конфиге или в `models.json` агента.

```json5
{
  models: {
    mode: "merge",
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions",
        models: [
          {
            id: "llama-3.1-8b",
            contextWindow: 128000,
          },
        ],
      },
    },
  },
}
```

-----

## Плагины (Plugins)

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    load: {
      paths: ["~/Projects/oss/voice-call-extension"],
    },
    entries: {
      "voice-call": {
        enabled: true,
        config: { provider: "twilio" },
      },
    },
  },
}
```

-----

## Браузер (Browser)

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    defaultProfile: "user",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
    },
  },
}
```

-----

## Шлюз (Gateway)

```json5
{
  gateway: {
    mode: "local",
    port: 18789,
    bind: "loopback",
    auth: {
      mode: "token",
      token: "your-token",
    },
    controlUi: {
      enabled: true,
      basePath: "/openclaw",
    },
  },
}
```

  - `mode`: `local` (запустить шлюз) или `remote` (подключиться к удаленному шлюзу).
  - `bind`: `auto`, `loopback` (по умолчанию), `lan` (`0.0.0.0`), `tailnet`.
  - `auth`: требуется по умолчанию для соединений не через loopback.

-----

## Хуки (Hooks)

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
    mappings: [
      {
        match: { path: "gmail" },
        action: "agent",
        agentId: "hooks",
        deliver: true,
      },
    ],
  },
}
```

-----

## Секреты (Secrets)

Используйте объекты `SecretRef` для безопасного хранения учетных данных.

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

-----

## Логирование (Logging)

```json5
{
  logging: {
    level: "info",
    file: "/tmp/openclaw/openclaw.log",
    consoleStyle: "pretty", // pretty | compact | json
    redactSensitive: "tools",
  },
}
```

-----

## Обновление (Update)

```json5
{
  update: {
    channel: "stable", // stable | beta | dev
    checkOnStart: true,
    auto: {
      enabled: false,
    },
  },
}
```

-----

## Включения в конфигурацию ($include)

Разделение конфигурации на несколько файлов:

```json5
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
}
```

-----

*Связанные разделы: [Конфигурация](https://www.google.com/search?q=/gateway/configuration) · [Примеры конфигурации](https://www.google.com/search?q=/gateway/configuration-examples) · [Doctor](https://www.google.com/search?q=/gateway/doctor)*