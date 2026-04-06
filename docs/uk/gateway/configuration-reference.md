---
read_when:
    - Вам потрібна точна семантика полів конфігурації або значення за замовчуванням на рівні полів
    - Ви перевіряєте блоки конфігурації каналів, моделей, шлюзу або інструментів
summary: Повний довідник для кожного ключа конфігурації OpenClaw, значень за замовчуванням і налаштувань каналів
title: Довідник з конфігурації
x-i18n:
    generated_at: "2026-04-06T04:36:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6ae6c19666f65433361e1c8b100ae710448c8aa055a60c140241a8aea09b98a5
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# Довідник з конфігурації

Усі поля, доступні в `~/.openclaw/openclaw.json`. Для огляду, орієнтованого на завдання, див. [Configuration](/uk/gateway/configuration).

Формат конфігурації — **JSON5** (дозволені коментарі та коми в кінці). Усі поля необов'язкові — OpenClaw використовує безпечні значення за замовчуванням, якщо їх пропущено.

---

## Канали

Кожен канал запускається автоматично, коли існує його секція конфігурації (якщо не вказано `enabled: false`).

### Доступ до DM і груп

Усі канали підтримують політики DM і політики груп:

| Політика DM         | Поведінка                                                       |
| ------------------- | --------------------------------------------------------------- |
| `pairing` (default) | Невідомі відправники отримують одноразовий код прив'язки; власник має схвалити |
| `allowlist`         | Лише відправники з `allowFrom` (або зі сховища дозволів після прив'язки) |
| `open`              | Дозволити всі вхідні DM (потрібен `allowFrom: ["*"]`)           |
| `disabled`          | Ігнорувати всі вхідні DM                                        |

| Політика груп         | Поведінка                                             |
| --------------------- | ----------------------------------------------------- |
| `allowlist` (default) | Лише групи, що відповідають налаштованому списку дозволів |
| `open`                | Обходити списки дозволів для груп (перевірка згадувань усе ще застосовується) |
| `disabled`            | Блокувати всі повідомлення груп/кімнат                |

<Note>
`channels.defaults.groupPolicy` задає значення за замовчуванням, коли `groupPolicy` постачальника не встановлено.
Коди прив'язки спливають через 1 годину. Кількість очікувальних запитів на прив'язку DM обмежена **3 на канал**.
Якщо блок постачальника повністю відсутній (`channels.<provider>` відсутній), політика груп під час виконання повертається до `allowlist` (fail-closed) з попередженням під час запуску.
</Note>

### Перевизначення моделей для каналів

Використовуйте `channels.modelByChannel`, щоб закріпити конкретні ID каналів за моделлю. Значення приймають `provider/model` або налаштовані псевдоніми моделей. Відображення каналів застосовується, коли сесія ще не має перевизначення моделі (наприклад, встановленого через `/model`).

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

### Значення за замовчуванням для каналів і heartbeat

Використовуйте `channels.defaults` для спільної політики груп і поведінки heartbeat у всіх постачальників:

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

- `channels.defaults.groupPolicy`: резервна політика груп, коли `groupPolicy` на рівні постачальника не встановлено.
- `channels.defaults.contextVisibility`: режим видимості додаткового контексту за замовчуванням для всіх каналів. Значення: `all` (default, включає весь процитований/потоковий/історичний контекст), `allowlist` (включає контекст лише від відправників зі списку дозволів), `allowlist_quote` (як `allowlist`, але зберігає явний контекст цитати/відповіді). Перевизначення на рівні каналу: `channels.<channel>.contextVisibility`.
- `channels.defaults.heartbeat.showOk`: включати стани здорових каналів у вивід heartbeat.
- `channels.defaults.heartbeat.showAlerts`: включати стани деградації/помилок у вивід heartbeat.
- `channels.defaults.heartbeat.useIndicator`: рендерити компактний вивід heartbeat у стилі індикатора.

### WhatsApp

WhatsApp працює через вебканал шлюзу (Baileys Web). Він запускається автоматично, коли існує прив'язана сесія.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // blue ticks (false in self-chat mode)
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

<Accordion title="Багатообліковий WhatsApp">

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

- Вихідні команди за замовчуванням використовують обліковий запис `default`, якщо він є; інакше — перший налаштований ID облікового запису (відсортований).
- Необов'язковий `channels.whatsapp.defaultAccount` перевизначає цей резервний вибір облікового запису за замовчуванням, якщо він збігається з налаштованим ID облікового запису.
- Застарілий каталог автентифікації Baileys для одного облікового запису мігрується `openclaw doctor` у `whatsapp/default`.
- Перевизначення на рівні облікового запису: `channels.whatsapp.accounts.<id>.sendReadReceipts`, `channels.whatsapp.accounts.<id>.dmPolicy`, `channels.whatsapp.accounts.<id>.allowFrom`.

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
      streaming: "partial", // off | partial | block | progress (default: off; opt in explicitly to avoid preview-edit rate limits)
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

- Токен бота: `channels.telegram.botToken` або `channels.telegram.tokenFile` (лише звичайний файл; симлінки відхиляються), з `TELEGRAM_BOT_TOKEN` як резервним варіантом для облікового запису за замовчуванням.
- Необов'язковий `channels.telegram.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він збігається з налаштованим ID облікового запису.
- У конфігураціях із кількома обліковими записами (2+ ID облікових записів) встановіть явний обліковий запис за замовчуванням (`channels.telegram.defaultAccount` або `channels.telegram.accounts.default`), щоб уникнути резервної маршрутизації; `openclaw doctor` попереджає, якщо цього немає або значення недійсне.
- `configWrites: false` блокує записи конфігурації, ініційовані з Telegram (міграції ID супергруп, `/config set|unset`).
- Записи верхнього рівня `bindings[]` з `type: "acp"` налаштовують постійні прив'язки ACP для тем форуму (використовуйте канонічний `chatId:topic:topicId` у `match.peer.id`). Семантика полів спільна з [ACP Agents](/uk/tools/acp-agents#channel-specific-settings).
- Попередній перегляд потоків Telegram використовує `sendMessage` + `editMessageText` (працює в прямих і групових чатах).
- Політика повторних спроб: див. [Retry policy](/uk/concepts/retry).

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
      streaming: "off", // off | partial | block | progress (progress maps to partial on Discord)
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
        spawnSubagentSessions: false, // opt-in for sessions_spawn({ thread: true })
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

- Токен: `channels.discord.token`, з `DISCORD_BOT_TOKEN` як резервним варіантом для облікового запису за замовчуванням.
- Прямі вихідні виклики, що передають явний Discord `token`, використовують цей токен для виклику; налаштування повторних спроб/політик облікового запису все одно беруться з вибраного облікового запису в активному знімку середовища виконання.
- Необов'язковий `channels.discord.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він збігається з налаштованим ID облікового запису.
- Використовуйте `user:<id>` (DM) або `channel:<id>` (канал guild) для цілей доставки; прості числові ID відхиляються.
- Slug guild завжди в нижньому регістрі, а пробіли замінюються на `-`; ключі каналів використовують назву у вигляді slug (без `#`). Надавайте перевагу ID guild.
- Повідомлення, створені ботами, за замовчуванням ігноруються. `allowBots: true` вмикає їх; використовуйте `allowBots: "mentions"`, щоб приймати лише повідомлення ботів, які згадують бота (власні повідомлення все одно фільтруються).
- `channels.discord.guilds.<id>.ignoreOtherMentions` (і перевизначення для каналів) відкидає повідомлення, що згадують іншого користувача чи роль, але не бота (окрім @everyone/@here).
- `maxLinesPerMessage` (default 17) розбиває високі повідомлення, навіть якщо вони коротші за 2000 символів.
- `channels.discord.threadBindings` керує маршрутизацією, прив'язаною до потоків Discord:
  - `enabled`: перевизначення Discord для можливостей сесій, прив'язаних до потоку (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` і прив'язана доставка/маршрутизація)
  - `idleHours`: перевизначення Discord для автоматичного зняття фокусу через неактивність у годинах (`0` вимикає)
  - `maxAgeHours`: перевизначення Discord для жорсткого максимального віку в годинах (`0` вимикає)
  - `spawnSubagentSessions`: перемикач opt-in для автоматичного створення/прив'язки потоків через `sessions_spawn({ thread: true })`
- Записи верхнього рівня `bindings[]` з `type: "acp"` налаштовують постійні ACP-прив'язки для каналів і потоків (використовуйте id каналу/потоку в `match.peer.id`). Семантика полів спільна з [ACP Agents](/uk/tools/acp-agents#channel-specific-settings).
- `channels.discord.ui.components.accentColor` задає колір акценту для контейнерів компонентів Discord v2.
- `channels.discord.voice` вмикає розмови у голосових каналах Discord і необов'язкові перевизначення auto-join + TTS.
- `channels.discord.voice.daveEncryption` і `channels.discord.voice.decryptionFailureTolerance` напряму передаються в параметри DAVE для `@discordjs/voice` (`true` і `24` за замовчуванням).
- OpenClaw додатково намагається відновити приймання голосу, виходячи та знову входячи в голосову сесію після повторних помилок дешифрування.
- `channels.discord.streaming` — канонічний ключ режиму потокової передачі. Застарілі `streamMode` і булеві значення `streaming` мігруються автоматично.
- `channels.discord.autoPresence` відображає доступність середовища виконання на статус бота (healthy => online, degraded => idle, exhausted => dnd) і дозволяє необов'язкові перевизначення тексту статусу.
- `channels.discord.dangerouslyAllowNameMatching` знову вмикає зіставлення за змінними іменами/тегами (режим сумісності break-glass).
- `channels.discord.execApprovals`: нативна доставка погоджень exec у Discord та авторизація тих, хто погоджує.
  - `enabled`: `true`, `false` або `"auto"` (default). В auto mode погодження exec активуються, коли тих, хто погоджує, можна визначити з `approvers` або `commands.ownerAllowFrom`.
  - `approvers`: ID користувачів Discord, яким дозволено погоджувати exec-запити. Якщо не вказано, використовується `commands.ownerAllowFrom`.
  - `agentFilter`: необов'язковий список дозволених ID агентів. Якщо пропущено, погодження пересилаються для всіх агентів.
  - `sessionFilter`: необов'язкові шаблони ключів сесій (підрядок або regex).
  - `target`: куди надсилати запити на погодження. `"dm"` (default) надсилає в DM тих, хто погоджує, `"channel"` — у вихідний канал, `"both"` — в обидва місця. Коли target включає `"channel"`, кнопками можуть користуватися лише визначені ті, хто погоджує.
  - `cleanupAfterResolve`: коли `true`, видаляє DM-повідомлення про погодження після погодження, відхилення або тайм-ауту.

**Режими сповіщень про реакції:** `off` (немає), `own` (повідомлення бота, за замовчуванням), `all` (усі повідомлення), `allowlist` (від `guilds.<id>.users` для всіх повідомлень).

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

- JSON облікового запису служби: вбудовано (`serviceAccount`) або через файл (`serviceAccountFile`).
- Також підтримується SecretRef для облікового запису служби (`serviceAccountRef`).
- Резервні змінні середовища: `GOOGLE_CHAT_SERVICE_ACCOUNT` або `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- Використовуйте `spaces/<spaceId>` або `users/<userId>` для цілей доставки.
- `channels.googlechat.dangerouslyAllowNameMatching` знову вмикає зіставлення за змінним email-principal (режим сумісності break-glass).

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
      streaming: "partial", // off | partial | block | progress (preview mode)
      nativeStreaming: true, // use Slack native streaming API when streaming=partial
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

- **Socket mode** потребує і `botToken`, і `appToken` (`SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` як резервні змінні середовища для облікового запису за замовчуванням).
- **HTTP mode** потребує `botToken` плюс `signingSecret` (у корені або для окремого облікового запису).
- `botToken`, `appToken`, `signingSecret` і `userToken` приймають відкриті
  рядки або об'єкти SecretRef.
- Знімки облікових записів Slack показують поля джерела/статусу облікових даних, як-от
  `botTokenSource`, `botTokenStatus`, `appTokenStatus` і, в HTTP mode,
  `signingSecretStatus`. `configured_unavailable` означає, що обліковий запис
  налаштований через SecretRef, але поточний шлях команди/середовища виконання не зміг
  отримати значення секрету.
- `configWrites: false` блокує записи конфігурації, ініційовані зі Slack.
- Необов'язковий `channels.slack.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він збігається з налаштованим ID облікового запису.
- `channels.slack.streaming` — канонічний ключ режиму потокової передачі. Застарілі `streamMode` і булеві значення `streaming` мігруються автоматично.
- Використовуйте `user:<id>` (DM) або `channel:<id>` для цілей доставки.

**Режими сповіщень про реакції:** `off`, `own` (default), `all`, `allowlist` (з `reactionAllowlist`).

**Ізоляція сесій потоків:** `thread.historyScope` — окремо для потоку (за замовчуванням) або спільно для каналу. `thread.inheritParent` копіює транскрипт батьківського каналу в нові потоки.

- `typingReaction` додає тимчасову реакцію до вхідного повідомлення Slack, поки виконується відповідь, а після завершення видаляє її. Використовуйте shortcode емодзі Slack, наприклад `"hourglass_flowing_sand"`.
- `channels.slack.execApprovals`: нативна доставка погоджень exec у Slack та авторизація тих, хто погоджує. Та сама схема, що й у Discord: `enabled` (`true`/`false`/`"auto"`), `approvers` (ID користувачів Slack), `agentFilter`, `sessionFilter` і `target` (`"dm"`, `"channel"` або `"both"`).

| Група дій    | За замовчуванням | Примітки                 |
| ------------ | ---------------- | ------------------------ |
| reactions    | увімкнено        | Реакції + список реакцій |
| messages     | увімкнено        | Читання/надсилання/редагування/видалення |
| pins         | увімкнено        | Закріпити/відкріпити/перелічити |
| memberInfo   | увімкнено        | Інформація про учасника  |
| emojiList    | увімкнено        | Список користувацьких емодзі |

### Mattermost

Mattermost постачається як plugin: `openclaw plugins install @openclaw/mattermost`.

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
        native: true, // opt-in
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // Optional explicit URL for reverse-proxy/public deployments
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

Режими чату: `oncall` (відповідати на @-згадування, за замовчуванням), `onmessage` (на кожне повідомлення), `onchar` (на повідомлення, що починаються з префікса-тригера).

Коли нативні команди Mattermost увімкнено:

- `commands.callbackPath` має бути шляхом (наприклад, `/api/channels/mattermost/command`), а не повним URL.
- `commands.callbackUrl` має вказувати на endpoint шлюзу OpenClaw і бути доступним із сервера Mattermost.
- Нативні callbacks slash-команд автентифікуються через токени для кожної команди, які Mattermost повертає
  під час реєстрації slash-команди. Якщо реєстрація не вдасться або жодні
  команди не будуть активовані, OpenClaw відхилятиме callbacks з
  `Unauthorized: invalid command token.`
- Для приватних/tailnet/internal хостів callback Mattermost може вимагати,
  щоб `ServiceSettings.AllowedUntrustedInternalConnections` містив хост/домен callback.
  Використовуйте значення хоста/домену, а не повні URL.
- `channels.mattermost.configWrites`: дозволити або заборонити записи конфігурації, ініційовані з Mattermost.
- `channels.mattermost.requireMention`: вимагати `@mention` перед відповіддю в каналах.
- `channels.mattermost.groups.<channelId>.requireMention`: перевизначення перевірки згадувань для окремого каналу (`"*"` для значення за замовчуванням).
- Необов'язковий `channels.mattermost.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він збігається з налаштованим ID облікового запису.

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // optional account binding
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

**Режими сповіщень про реакції:** `off`, `own` (default), `all`, `allowlist` (з `reactionAllowlist`).

- `channels.signal.account`: прив'язати запуск каналу до конкретної ідентичності облікового запису Signal.
- `channels.signal.configWrites`: дозволити або заборонити записи конфігурації, ініційовані з Signal.
- Необов'язковий `channels.signal.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він збігається з налаштованим ID облікового запису.

### BlueBubbles

BlueBubbles — рекомендований шлях для iMessage (на базі plugin, налаштовується в `channels.bluebubbles`).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl, password, webhookPath, group controls, and advanced actions:
      // see /channels/bluebubbles
    },
  },
}
```

- Основні шляхи ключів, описані тут: `channels.bluebubbles`, `channels.bluebubbles.dmPolicy`.
- Необов'язковий `channels.bluebubbles.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він збігається з налаштованим ID облікового запису.
- Записи верхнього рівня `bindings[]` з `type: "acp"` можуть прив'язувати розмови BlueBubbles до постійних сесій ACP. Використовуйте BlueBubbles handle або рядок цілі (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) у `match.peer.id`. Спільна семантика полів: [ACP Agents](/uk/tools/acp-agents#channel-specific-settings).
- Повну конфігурацію каналу BlueBubbles описано в [BlueBubbles](/uk/channels/bluebubbles).

### iMessage

OpenClaw запускає `imsg rpc` (JSON-RPC через stdio). Жоден daemon або порт не потрібен.

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

- Необов'язковий `channels.imessage.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він збігається з налаштованим ID облікового запису.

- Потрібен Full Disk Access до БД Messages.
- Надавайте перевагу цілям `chat_id:<id>`. Використовуйте `imsg chats --limit 20`, щоб переглянути список чатів.
- `cliPath` може вказувати на SSH-wrapper; установіть `remoteHost` (`host` або `user@host`) для отримання вкладень через SCP.
- `attachmentRoots` і `remoteAttachmentRoots` обмежують шляхи вхідних вкладень (за замовчуванням: `/Users/*/Library/Messages/Attachments`).
- SCP використовує сувору перевірку ключа хоста, тож переконайтеся, що ключ relay-host уже існує в `~/.ssh/known_hosts`.
- `channels.imessage.configWrites`: дозволити або заборонити записи конфігурації, ініційовані з iMessage.
- Записи верхнього рівня `bindings[]` з `type: "acp"` можуть прив'язувати розмови iMessage до постійних сесій ACP. Використовуйте нормалізований handle або явну ціль чату (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) у `match.peer.id`. Спільна семантика полів: [ACP Agents](/uk/tools/acp-agents#channel-specific-settings).

<Accordion title="Приклад SSH-wrapper для iMessage">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix працює через extension і налаштовується в `channels.matrix`.

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

- Автентифікація токеном використовує `accessToken`; автентифікація паролем використовує `userId` + `password`.
- `channels.matrix.proxy` маршрутизує HTTP-трафік Matrix через явно заданий HTTP(S)-proxy. Іменовані облікові записи можуть перевизначити це через `channels.matrix.accounts.<id>.proxy`.
- `channels.matrix.allowPrivateNetwork` дозволяє приватні/internal homeserver. `proxy` і `allowPrivateNetwork` — незалежні механізми керування.
- `channels.matrix.defaultAccount` вибирає пріоритетний обліковий запис у конфігураціях із кількома обліковими записами.
- `channels.matrix.execApprovals`: нативна доставка погоджень exec у Matrix та авторизація тих, хто погоджує.
  - `enabled`: `true`, `false` або `"auto"` (default). В auto mode погодження exec активуються, коли тих, хто погоджує, можна визначити з `approvers` або `commands.ownerAllowFrom`.
  - `approvers`: ID користувачів Matrix (наприклад, `@owner:example.org`), яким дозволено погоджувати exec-запити.
  - `agentFilter`: необов'язковий список дозволених ID агентів. Якщо пропущено, погодження пересилаються для всіх агентів.
  - `sessionFilter`: необов'язкові шаблони ключів сесій (підрядок або regex).
  - `target`: куди надсилати запити на погодження. `"dm"` (default), `"channel"` (вихідна кімната) або `"both"`.
  - Перевизначення на рівні облікового запису: `channels.matrix.accounts.<id>.execApprovals`.
- `channels.matrix.dm.sessionScope` керує тим, як DM у Matrix групуються в сесії: `per-user` (за замовчуванням) ділить за маршрутизованим peer, а `per-room` ізолює кожну DM-кімнату.
- Перевірки статусу Matrix і пошуки в live-directory використовують ту саму політику proxy, що й трафік середовища виконання.
- Повну конфігурацію Matrix, правила адресації та приклади налаштування описано в [Matrix](/uk/channels/matrix).

### Microsoft Teams

Microsoft Teams працює через extension і налаштовується в `channels.msteams`.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId, appPassword, tenantId, webhook, team/channel policies:
      // see /channels/msteams
    },
  },
}
```

- Основні шляхи ключів, описані тут: `channels.msteams`, `channels.msteams.configWrites`.
- Повну конфігурацію Teams (облікові дані, webhook, політику DM/груп, перевизначення для окремих team/channel) описано в [Microsoft Teams](/uk/channels/msteams).

### IRC

IRC працює через extension і налаштовується в `channels.irc`.

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

- Основні шляхи ключів, описані тут: `channels.irc`, `channels.irc.dmPolicy`, `channels.irc.configWrites`, `channels.irc.nickserv.*`.
- Необов'язковий `channels.irc.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він збігається з налаштованим ID облікового запису.
- Повну конфігурацію каналу IRC (host/port/TLS/channels/allowlists/mention gating) описано в [IRC](/uk/channels/irc).

### Багатообліковість (усі канали)

Запускайте кілька облікових записів на канал (кожен зі своїм `accountId`):

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "Primary bot",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "Alerts bot",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- `default` використовується, коли `accountId` пропущено (CLI + маршрутизація).
- Токени з env застосовуються лише до облікового запису **default**.
- Базові налаштування каналу застосовуються до всіх облікових записів, якщо не перевизначені на рівні облікового запису.
- Використовуйте `bindings[].match.accountId`, щоб маршрутизувати кожен обліковий запис до іншого агента.
- Якщо ви додаєте не-default обліковий запис через `openclaw channels add` (або онбординг каналу), перебуваючи на top-level конфігурації каналу для одного облікового запису, OpenClaw спочатку переносить top-level значення для одного облікового запису, прив'язані до облікового запису, у карту облікових записів каналу, щоб початковий обліковий запис і надалі працював. Більшість каналів переміщують їх у `channels.<channel>.accounts.default`; Matrix натомість може зберегти вже наявну відповідну іменовану/default-ціль.
- Наявні прив'язки лише на рівні каналу (без `accountId`) і надалі відповідатимуть default-обліковому запису; прив'язки на рівні облікового запису залишаються необов'язковими.
- `openclaw doctor --fix` також виправляє змішані форми, переміщуючи top-level значення для одного облікового запису, прив'язані до облікового запису, у promoted-обліковий запис, вибраний для цього каналу. Більшість каналів використовують `accounts.default`; Matrix може зберегти вже наявну відповідну іменовану/default-ціль.

### Інші канали-extensions

Багато каналів-extension налаштовуються як `channels.<id>` і описані на окремих сторінках каналів (наприклад Feishu, Matrix, LINE, Nostr, Zalo, Nextcloud Talk, Synology Chat і Twitch).
Див. повний індекс каналів: [Channels](/uk/channels).

### Перевірка згадувань у групових чатах

Для групових повідомлень за замовчуванням **потрібне згадування** (метадані згадування або безпечні regex-патерни). Це стосується групових чатів WhatsApp, Telegram, Discord, Google Chat та iMessage.

**Типи згадувань:**

- **Згадування в метаданих**: нативні @-згадування платформи. Ігноруються в режимі self-chat WhatsApp.
- **Текстові патерни**: безпечні regex-патерни в `agents.list[].groupChat.mentionPatterns`. Недійсні патерни й небезпечні вкладені повторення ігноруються.
- Перевірка згадувань застосовується лише тоді, коли виявлення можливе (нативні згадування або щонайменше один патерн).

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

`messages.groupChat.historyLimit` задає глобальне значення за замовчуванням. Канали можуть перевизначати його через `channels.<channel>.historyLimit` (або на рівні облікового запису). Установіть `0`, щоб вимкнути.

#### Ліміти історії DM

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

Порядок визначення: перевизначення для конкретного DM → значення за замовчуванням постачальника → без ліміту (зберігається все).

Підтримується: `telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`.

#### Режим self-chat

Додайте власний номер до `allowFrom`, щоб увімкнути режим self-chat (ігнорує нативні @-згадування, відповідає лише на текстові патерни):

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

### Команди (обробка команд чату)

```json5
{
  commands: {
    native: "auto", // register native commands when supported
    text: true, // parse /commands in chat messages
    bash: false, // allow ! (alias: /bash)
    bashForegroundMs: 2000,
    config: false, // allow /config
    debug: false, // allow /debug
    restart: false, // allow /restart + gateway restart tool
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="Деталі команд">

- Текстові команди мають бути **окремими** повідомленнями, що починаються з `/`.
- `native: "auto"` вмикає нативні команди для Discord/Telegram, але лишає Slack вимкненим.
- Перевизначення для окремого каналу: `channels.discord.commands.native` (bool або `"auto"`). `false` очищає раніше зареєстровані команди.
- `channels.telegram.customCommands` додає додаткові записи меню бота Telegram.
- `bash: true` вмикає `! <cmd>` для shell хоста. Потрібні `tools.elevated.enabled` і відправник у `tools.elevated.allowFrom.<channel>`.
- `config: true` вмикає `/config` (читання/запис `openclaw.json`). Для клієнтів шлюзу `chat.send` постійні записи `/config set|unset` також потребують `operator.admin`; режим лише читання `/config show` залишається доступним для звичайних операторських клієнтів із правом запису.
- `channels.<provider>.configWrites` керує мутаціями конфігурації на рівні каналу (за замовчуванням: true).
- Для багатьох облікових записів `channels.<provider>.accounts.<id>.configWrites` також керує записами, що націлені на цей обліковий запис (наприклад `/allowlist --config --account <id>` або `/config set channels.<provider>.accounts.<id>...`).
- `allowFrom` задається окремо для постачальника. Якщо встановлено, це **єдине** джерело авторизації (списки дозволів каналів/прив'язка та `useAccessGroups` ігноруються).
- `useAccessGroups: false` дозволяє командам обходити політики access-group, коли `allowFrom` не задано.

</Accordion>

---

## Значення за замовчуванням для агентів

### `agents.defaults.workspace`

За замовчуванням: `~/.openclaw/workspace`.

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

Необов'язковий корінь репозиторію, що показується в рядку Runtime системного prompt. Якщо не встановлено, OpenClaw визначає його автоматично, піднімаючись вгору від workspace.

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

Необов'язковий список дозволених Skills за замовчуванням для агентів, які не задають
`agents.list[].skills`.

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // inherits github, weather
      { id: "docs", skills: ["docs-search"] }, // replaces defaults
      { id: "locked-down", skills: [] }, // no skills
    ],
  },
}
```

- Пропустіть `agents.defaults.skills`, щоб за замовчуванням Skills були без обмежень.
- Пропустіть `agents.list[].skills`, щоб успадкувати значення за замовчуванням.
- Установіть `agents.list[].skills: []`, щоб не дозволяти жодних Skills.
- Непорожній список `agents.list[].skills` є фінальним набором для цього агента;
  він не об'єднується зі значеннями за замовчуванням.

### `agents.defaults.skipBootstrap`

Вимикає автоматичне створення bootstrap-файлів workspace (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`).

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

Керує тим, коли bootstrap-файли workspace вбудовуються в системний prompt. За замовчуванням: `"always"`.

- `"continuation-skip"`: безпечні продовжувальні ходи (після завершеної відповіді асистента) пропускають повторне вбудовування bootstrap workspace, зменшуючи розмір prompt. Запуски heartbeat і повторні спроби після compaction все одно перебудовують контекст.

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

Максимальна кількість символів на один bootstrap-файл workspace до усічення. За замовчуванням: `20000`.

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

Максимальна загальна кількість символів, що вбудовуються з усіх bootstrap-файлів workspace. За замовчуванням: `150000`.

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

Керує видимим для агента текстом попередження, коли bootstrap-контекст усічено.
За замовчуванням: `"once"`.

- `"off"`: ніколи не вбудовувати текст попередження в системний prompt.
- `"once"`: вбудовувати попередження один раз для кожного унікального підпису усічення (рекомендовано).
- `"always"`: вбудовувати попередження при кожному запуску, коли є усічення.

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

Максимальний розмір у пікселях для найдовшої сторони зображення в блоках зображень transcript/tool перед викликами постачальника.
За замовчуванням: `1200`.

Менші значення зазвичай зменшують використання vision-token і розмір запиту для сценаріїв зі значною кількістю скриншотів.
Більші значення зберігають більше візуальних деталей.

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

Часовий пояс для контексту системного prompt (не для часових міток повідомлень). Якщо не вказано, використовується часовий пояс хоста.

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

Формат часу в системному prompt. За замовчуванням: `auto` (налаштування ОС).

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
      params: { cacheRetention: "long" }, // global default provider params
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

- `model`: приймає або рядок (`"provider/model"`), або об'єкт (`{ primary, fallbacks }`).
  - Рядкова форма задає лише primary model.
  - Об'єктна форма задає primary model і впорядкований failover-моделей.
- `imageModel`: приймає або рядок (`"provider/model"`), або об'єкт (`{ primary, fallbacks }`).
  - Використовується шляхом інструмента `image` як його конфігурація vision-model.
  - Також використовується як резервна маршрутизація, коли вибрана/default model не може приймати вхідні зображення.
- `imageGenerationModel`: приймає або рядок (`"provider/model"`), або об'єкт (`{ primary, fallbacks }`).
  - Використовується спільною можливістю генерації зображень і будь-якою майбутньою поверхнею tool/plugin, що генерує зображення.
  - Типові значення: `google/gemini-3.1-flash-image-preview` для нативної генерації зображень Gemini, `fal/fal-ai/flux/dev` для fal або `openai/gpt-image-1` для OpenAI Images.
  - Якщо ви безпосередньо вибираєте provider/model, також налаштуйте відповідну автентифікацію постачальника/API key (наприклад `GEMINI_API_KEY` або `GOOGLE_API_KEY` для `google/*`, `OPENAI_API_KEY` для `openai/*`, `FAL_KEY` для `fal/*`).
  - Якщо поле пропущено, `image_generate` усе одно може вивести provider default на основі автентифікації. Спочатку воно пробує поточного постачальника за замовчуванням, потім решту зареєстрованих постачальників генерації зображень у порядку provider-id.
- `musicGenerationModel`: приймає або рядок (`"provider/model"`), або об'єкт (`{ primary, fallbacks }`).
  - Використовується спільною можливістю генерації музики та вбудованим інструментом `music_generate`.
  - Типові значення: `google/lyria-3-clip-preview`, `google/lyria-3-pro-preview` або `minimax/music-2.5+`.
  - Якщо поле пропущено, `music_generate` усе одно може вивести provider default на основі автентифікації. Спочатку воно пробує поточного постачальника за замовчуванням, потім решту зареєстрованих постачальників генерації музики в порядку provider-id.
  - Якщо ви безпосередньо вибираєте provider/model, також налаштуйте відповідну автентифікацію постачальника/API key.
- `videoGenerationModel`: приймає або рядок (`"provider/model"`), або об'єкт (`{ primary, fallbacks }`).
  - Використовується спільною можливістю генерації відео та вбудованим інструментом `video_generate`.
  - Типові значення: `qwen/wan2.6-t2v`, `qwen/wan2.6-i2v`, `qwen/wan2.6-r2v`, `qwen/wan2.6-r2v-flash` або `qwen/wan2.7-r2v`.
  - Якщо поле пропущено, `video_generate` усе одно може вивести provider default на основі автентифікації. Спочатку воно пробує поточного постачальника за замовчуванням, потім решту зареєстрованих постачальників генерації відео в порядку provider-id.
  - Якщо ви безпосередньо вибираєте provider/model, також налаштуйте відповідну автентифікацію постачальника/API key.
  - Вбудований постачальник генерації відео Qwen зараз підтримує до 1 вихідного відео, 1 вхідного зображення, 4 вхідних відео, тривалість 10 секунд і параметри рівня постачальника `size`, `aspectRatio`, `resolution`, `audio` та `watermark`.
- `pdfModel`: приймає або рядок (`"provider/model"`), або об'єкт (`{ primary, fallbacks }`).
  - Використовується інструментом `pdf` для маршрутизації моделі.
  - Якщо поле пропущено, PDF-інструмент повертається до `imageModel`, а потім — до визначеної model сесії/default.
- `pdfMaxBytesMb`: default-ліміт розміру PDF для інструмента `pdf`, якщо `maxBytesMb` не передано під час виклику.
- `pdfMaxPages`: default максимальна кількість сторінок, яка враховується в режимі резервного витягування для інструмента `pdf`.
- `verboseDefault`: default рівень verbose для агентів. Значення: `"off"`, `"on"`, `"full"`. За замовчуванням: `"off"`.
- `elevatedDefault`: default рівень elevated-output для агентів. Значення: `"off"`, `"on"`, `"ask"`, `"full"`. За замовчуванням: `"on"`.
- `model.primary`: формат `provider/model` (наприклад `openai/gpt-5.4`). Якщо ви пропускаєте provider, OpenClaw спочатку пробує alias, потім — унікальний збіг exact model id серед налаштованих постачальників, і лише потім повертається до налаштованого постачальника за замовчуванням (застаріла сумісна поведінка, тож надавайте перевагу явному `provider/model`). Якщо цей постачальник більше не надає налаштовану default model, OpenClaw повертається до першого налаштованого provider/model замість того, щоб показувати застаріле default від видаленого постачальника.
- `models`: налаштований каталог моделей і список дозволів для `/model`. Кожен запис може містити `alias` (скорочення) і `params` (параметри, специфічні для постачальника, наприклад `temperature`, `maxTokens`, `cacheRetention`, `context1m`).
- `params`: глобальні параметри постачальника за замовчуванням, що застосовуються до всіх моделей. Встановлюються в `agents.defaults.params` (наприклад `{ cacheRetention: "long" }`).
- Пріоритет злиття `params` (конфіг): `agents.defaults.params` (глобальна база) перевизначається `agents.defaults.models["provider/model"].params` (для конкретної моделі), а потім `agents.list[].params` (для відповідного agent id) перевизначає за ключем. Детальніше див. у [Prompt Caching](/uk/reference/prompt-caching).
- Засоби запису конфігурації, які змінюють ці поля (наприклад `/models set`, `/models set-image` і команди додавання/видалення fallback), зберігають канонічну object form і по можливості зберігають наявні списки fallback.
- `maxConcurrent`: максимальна кількість паралельних запусків агентів у сесіях (кожна сесія все одно серіалізується). За замовчуванням: 4.

**Вбудовані скорочення alias** (працюють лише тоді, коли модель є в `agents.defaults.models`):

| Alias               | Модель                                 |
| ------------------- | -------------------------------------- |
| `opus`              | `anthropic/claude-opus-4-6`            |
| `sonnet`            | `anthropic/claude-sonnet-4-6`          |
| `gpt`               | `openai/gpt-5.4`                       |
| `gpt-mini`          | `openai/gpt-5.4-mini`                  |
| `gpt-nano`          | `openai/gpt-5.4-nano`                  |
| `gemini`            | `google/gemini-3.1-pro-preview`        |
| `gemini-flash`      | `google/gemini-3-flash-preview`        |
| `gemini-flash-lite` | `google/gemini-3.1-flash-lite-preview` |

Ваші налаштовані alias завжди мають пріоритет над значеннями за замовчуванням.

Моделі Z.AI GLM-4.x автоматично вмикають режим thinking, якщо ви не встановите `--thinking off` або не визначите `agents.defaults.models["zai/<model>"].params.thinking` самостійно.
Моделі Z.AI за замовчуванням вмикають `tool_stream` для потокової передачі викликів інструментів. Установіть `agents.defaults.models["zai/<model>"].params.tool_stream` у `false`, щоб вимкнути це.
Для моделей Anthropic Claude 4.6 за замовчуванням використовується `adaptive` thinking, якщо не задано явний рівень thinking.

- Сесії підтримуються, коли встановлено `sessionArg`.
- Пряме передавання зображень підтримується, коли `imageArg` приймає шляхи до файлів.

### `agents.defaults.heartbeat`

Періодичні запуски heartbeat.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m disables
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        lightContext: false, // default: false; true keeps only HEARTBEAT.md from workspace bootstrap files
        isolatedSession: false, // default: false; true runs each heartbeat in a fresh session (no conversation history)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (default) | block
        target: "none", // default: none | options: last | whatsapp | telegram | discord | ...
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
      },
    },
  },
}
```

- `every`: рядок тривалості (ms/s/m/h). За замовчуванням: `30m` (автентифікація через API key) або `1h` (OAuth-автентифікація). Установіть `0m`, щоб вимкнути.
- `suppressToolErrorWarnings`: якщо true, пригнічує payload попереджень про помилки інструментів під час запусків heartbeat.
- `directPolicy`: політика прямої/DM-доставки. `allow` (default) дозволяє доставку за прямою ціллю. `block` пригнічує доставку за прямою ціллю та видає `reason=dm-blocked`.
- `lightContext`: якщо true, запуски heartbeat використовують полегшений bootstrap-контекст і зберігають лише `HEARTBEAT.md` із bootstrap-файлів workspace.
- `isolatedSession`: якщо true, кожен запуск heartbeat виконується в новій сесії без попередньої історії розмови. Такий самий шаблон ізоляції, як у cron `sessionTarget: "isolated"`. Зменшує витрати токенів на heartbeat приблизно зі ~100K до ~2-5K токенів.
- Для окремого агента: установіть `agents.list[].heartbeat`. Якщо будь-який агент визначає `heartbeat`, heartbeat запускатиметься **лише для цих агентів**.
- Heartbeat виконує повні ходи агента — коротші інтервали спалюють більше токенів.

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
        identifierInstructions: "Preserve deployment IDs, ticket IDs, and host:port pairs exactly.", // used when identifierPolicy=custom
        postCompactionSections: ["Session Startup", "Red Lines"], // [] disables reinjection
        model: "openrouter/anthropic/claude-sonnet-4-6", // optional compaction-only model override
        notifyUser: true, // send a brief notice when compaction starts (default: false)
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with the exact silent token NO_REPLY if nothing to store.",
        },
      },
    },
  },
}
```

- `mode`: `default` або `safeguard` (підсумовування частинами для довгої історії). Див. [Compaction](/uk/concepts/compaction).
- `timeoutSeconds`: максимальна кількість секунд, дозволена для однієї операції compaction, після чого OpenClaw перериває її. За замовчуванням: `900`.
- `identifierPolicy`: `strict` (default), `off` або `custom`. `strict` додає вбудовані вказівки щодо збереження непрозорих ідентифікаторів під час compaction summarization.
- `identifierInstructions`: необов'язковий текст користувацьких вказівок щодо збереження ідентифікаторів, який використовується, коли `identifierPolicy=custom`.
- `postCompactionSections`: необов'язкові назви секцій H2/H3 з AGENTS.md, які повторно вбудовуються після compaction. За замовчуванням `["Session Startup", "Red Lines"]`; установіть `[]`, щоб вимкнути повторне вбудовування. Коли поле не задано або явно дорівнює цій парі за замовчуванням, старі заголовки `Every Session`/`Safety` також приймаються як застарілий резервний варіант.
- `model`: необов'язкове перевизначення `provider/model-id` лише для summarization під час compaction. Використовуйте це, коли основна сесія має лишатися на одній моделі, але summaries compaction мають виконуватися на іншій; якщо не задано, compaction використовує primary model сесії.
- `notifyUser`: якщо `true`, надсилає користувачу коротке повідомлення, коли починається compaction (наприклад, "Compacting context..."). За замовчуванням вимкнено, щоб compaction відбувався непомітно.
- `memoryFlush`: тихий agentic-хід перед auto-compaction для збереження довготривалої пам'яті. Пропускається, коли workspace лише для читання.

### `agents.defaults.contextPruning`

Очищає **старі результати інструментів** з in-memory-контексту перед відправленням до LLM. **Не** змінює історію сесії на диску.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // duration (ms/s/m/h), default unit: minutes
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Old tool result content cleared]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="Поведінка режиму cache-ttl">

- `mode: "cache-ttl"` вмикає проходи pruning.
- `ttl` керує тим, як часто pruning може запускатися знову (після останнього дотику до cache).
- Pruning спочатку м'яко обрізає надто великі результати інструментів, а потім за потреби жорстко очищає старіші результати інструментів.

**Soft-trim** зберігає початок і кінець та вставляє `...` посередині.

**Hard-clear** повністю замінює результат інструмента на placeholder.

Примітки:

- Блоки зображень ніколи не обрізаються/не очищаються.
- Співвідношення базуються на символах (приблизно), а не на точній кількості токенів.
- Якщо повідомлень assistant менше, ніж `keepLastAssistants`, pruning пропускається.

</Accordion>

Деталі поведінки див. у [Session Pruning](/uk/concepts/session-pruning).

### Блокова потокова передача

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (use minMs/maxMs)
    },
  },
}
```

- Не-Telegram канали потребують явного `*.blockStreaming: true`, щоб увімкнути блокові відповіді.
- Перевизначення для каналу: `channels.<channel>.blockStreamingCoalesce` (та варіанти на рівні облікового запису). Для Signal/Slack/Discord/Google Chat за замовчуванням `minChars: 1500`.
- `humanDelay`: випадкова пауза між блоковими відповідями. `natural` = 800–2500ms. Перевизначення для окремого агента: `agents.list[].humanDelay`.

Деталі поведінки та розбиття на частини див. у [Streaming](/uk/concepts/streaming).

### Індикатори набору

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

- За замовчуванням: `instant` для прямих чатів/згадувань, `message` для групових чатів без згадування.
- Перевизначення для сесії: `session.typingMode`, `session.typingIntervalSeconds`.

Див. [Typing Indicators](/uk/concepts/typing-indicators).

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

Необов'язкова ізоляція для вбудованого агента. Повний посібник див. у [Sandboxing](/uk/gateway/sandboxing).

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
          // SecretRefs / inline contents also supported:
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

<Accordion title="Деталі sandbox">

**Backend:**

- `docker`: локальне середовище виконання Docker (за замовчуванням)
- `ssh`: загальне віддалене середовище виконання на базі SSH
- `openshell`: середовище виконання OpenShell

Коли вибрано `backend: "openshell"`, налаштування, специфічні для середовища виконання, переносяться до
`plugins.entries.openshell.config`.

**Конфігурація backend SSH:**

- `target`: SSH-ціль у форматі `user@host[:port]`
- `command`: команда SSH-клієнта (за замовчуванням: `ssh`)
- `workspaceRoot`: абсолютний віддалений корінь для workspace за кожною областю
- `identityFile` / `certificateFile` / `knownHostsFile`: наявні локальні файли, передані в OpenSSH
- `identityData` / `certificateData` / `knownHostsData`: вбудований вміст або SecretRef, які OpenClaw матеріалізує у тимчасові файли під час виконання
- `strictHostKeyChecking` / `updateHostKeys`: параметри політики ключів хоста OpenSSH

**Пріоритет автентифікації SSH:**

- `identityData` має пріоритет над `identityFile`
- `certificateData` має пріоритет над `certificateFile`
- `knownHostsData` має пріоритет над `knownHostsFile`
- Значення `*Data` на основі SecretRef визначаються з активного знімка secrets runtime перед початком sandbox-сесії

**Поведінка backend SSH:**

- один раз ініціалізує віддалений workspace після створення або повторного створення
- далі зберігає віддалений SSH-workspace канонічним
- маршрутизує `exec`, файлові інструменти та шляхи до media через SSH
- не синхронізує автоматично віддалені зміни назад на хост
- не підтримує контейнерів браузера в sandbox

**Доступ до workspace:**

- `none`: workspace sandbox за кожною областю в `~/.openclaw/sandboxes`
- `ro`: workspace sandbox у `/workspace`, workspace агента змонтовано лише для читання в `/agent`
- `rw`: workspace агента змонтовано для читання/запису в `/workspace`

**Область:**

- `session`: окремий контейнер + workspace на сесію
- `agent`: один контейнер + workspace на агента (за замовчуванням)
- `shared`: спільний контейнер і workspace (без міжсесійної ізоляції)

**Конфігурація plugin OpenShell:**

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
          gateway: "lab", // optional
          gatewayEndpoint: "https://lab.example", // optional
          policy: "strict", // optional OpenShell policy id
          providers: ["openai"], // optional
          autoProviders: true,
          timeoutSeconds: 120,
        },
      },
    },
  },
}
```

**Режим OpenShell:**

- `mirror`: ініціалізувати віддалене середовище з локального перед exec, синхронізувати назад після exec; локальний workspace лишається канонічним
- `remote`: один раз ініціалізувати віддалене середовище під час створення sandbox, далі віддалений workspace лишається канонічним

У режимі `remote` локальні редагування на хості, зроблені поза OpenClaw, не синхронізуються в sandbox автоматично після кроку ініціалізації.
Транспортом є SSH до sandbox OpenShell, але plugin володіє життєвим циклом sandbox і необов'язковою синхронізацією mirror.

**`setupCommand`** виконується один раз після створення контейнера (через `sh -lc`). Потребує виходу в мережу, записуваного root і користувача root.

**Контейнери за замовчуванням мають `network: "none"`** — установіть `"bridge"` (або кастомну bridge-мережу), якщо агенту потрібен вихід назовні.
`"host"` заблоковано. `"container:<id>"` за замовчуванням теж заблоковано, якщо ви явно не встановите
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` (break-glass).

**Вхідні вкладення** staging'уються до `media/inbound/*` в активному workspace.

**`docker.binds`** монтує додаткові каталоги хоста; глобальні й агентські binds об'єднуються.

**Sandboxed browser** (`sandbox.browser.enabled`): Chromium + CDP у контейнері. URL noVNC вбудовується в системний prompt. Не потребує `browser.enabled` в `openclaw.json`.
Доступ спостерігача через noVNC за замовчуванням використовує VNC-автентифікацію, а OpenClaw видає URL із короткоживучим токеном (замість того, щоб показувати пароль у спільному URL).

- `allowHostControl: false` (default) блокує націлювання sandboxed-сесій на браузер хоста.
- `network` за замовчуванням дорівнює `openclaw-sandbox-browser` (виділена bridge-мережа). Установлюйте `bridge` лише тоді, коли вам справді потрібна глобальна bridge-зв'язність.
- `cdpSourceRange` за потреби обмежує вхід до CDP на межі контейнера CIDR-діапазоном (наприклад `172.21.0.1/32`).
- `sandbox.browser.binds` монтує додаткові каталоги хоста лише в контейнер sandbox-browser. Якщо параметр задано (включно з `[]`), він замінює `docker.binds` для контейнера браузера.
- Значення запуску за замовчуванням визначено в `scripts/sandbox-browser-entrypoint.sh` і налаштовано для контейнерних хостів:
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
  - `--disable-extensions` (за замовчуванням увімкнено)
  - `--disable-3d-apis`, `--disable-software-rasterizer` і `--disable-gpu`
    увімкнені за замовчуванням і можуть бути вимкнені через
    `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`, якщо для WebGL/3D це потрібно.
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` знову вмикає extensions, якщо від них
    залежить ваш сценарій роботи.
  - `--renderer-process-limit=2` можна змінити через
    `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`; установіть `0`, щоб використовувати
    стандартне обмеження процесів Chromium.
  - а також `--no-sandbox` і `--disable-setuid-sandbox`, коли увімкнено `noSandbox`.
  - Значення за замовчуванням є базовими для образу контейнера; використовуйте користувацький browser image з власним
    entrypoint, щоб змінити типові налаштування контейнера.

</Accordion>

Ізоляція браузера та `sandbox.docker.binds` наразі підтримуються лише для Docker.

Збирання образів:

```bash
scripts/sandbox-setup.sh           # main sandbox image
scripts/sandbox-browser-setup.sh   # optional browser image
```

### `agents.list` (перевизначення для окремого агента)

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6", // or { primary, fallbacks }
        thinkingDefault: "high", // per-agent thinking level override
        reasoningDefault: "on", // per-agent reasoning visibility override
        fastModeDefault: false, // per-agent fast mode override
        params: { cacheRetention: "none" }, // overrides matching defaults.models params by key
        skills: ["docs-search"], // replaces agents.defaults.skills when set
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
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

- `id`: стабільний ID агента (обов'язково).
- `default`: якщо встановлено для кількох, перший має пріоритет (записується попередження). Якщо не встановлено для жодного, default — перший елемент списку.
- `model`: рядкова форма перевизначає лише `primary`; об'єктна форма `{ primary, fallbacks }` перевизначає обидва (`[]` вимикає глобальні fallback). Cron jobs, які перевизначають лише `primary`, все одно успадковують default fallback, якщо ви не встановите `fallbacks: []`.
- `params`: параметри потоку для окремого агента, які зливаються поверх вибраного запису моделі в `agents.defaults.models`. Використовуйте це для агентоспецифічних перевизначень, наприклад `cacheRetention`, `temperature` або `maxTokens`, без дублювання всього каталогу моделей.
- `skills`: необов'язковий список дозволених Skills для окремого агента. Якщо його пропущено, агент успадковує `agents.defaults.skills`, якщо той задано; явний список замінює значення за замовчуванням, а `[]` означає відсутність Skills.
- `thinkingDefault`: необов'язковий default рівень thinking для окремого агента (`off | minimal | low | medium | high | xhigh | adaptive`). Перевизначає `agents.defaults.thinkingDefault` для цього агента, якщо не задано перевизначення на рівні повідомлення або сесії.
- `reasoningDefault`: необов'язкове default перевизначення видимості reasoning для окремого агента (`on | off | stream`). Застосовується, якщо не задано перевизначення reasoning на рівні повідомлення або сесії.
- `fastModeDefault`: необов'язкове default перевизначення fast mode для окремого агента (`true | false`). Застосовується, якщо не задано перевизначення fast-mode на рівні повідомлення або сесії.
- `runtime`: необов'язковий опис runtime для окремого агента. Використовуйте `type: "acp"` разом з default-значеннями `runtime.acp` (`agent`, `backend`, `mode`, `cwd`), коли агент має за замовчуванням використовувати ACP-harness sessions.
- `identity.avatar`: шлях відносно workspace, `http(s)` URL або `data:` URI.
- `identity` виводить значення за замовчуванням: `ackReaction` з `emoji`, `mentionPatterns` з `name`/`emoji`.
- `subagents.allowAgents`: список дозволених agent id для `sessions_spawn` (`["*"]` = будь-який; за замовчуванням: лише той самий агент).
- Захист успадкування sandbox: якщо сесія запитувача працює в sandbox, `sessions_spawn` відхиляє цілі, які працювали б без sandbox.
- `subagents.requireAgentId`: коли true, блокує виклики `sessions_spawn`, у яких пропущено `agentId` (вимагає явного вибору профілю; за замовчуванням: false).

---

## Маршрутизація кількох агентів

Запускайте кількох ізольованих агентів в одному Gateway. Див. [Multi-Agent](/uk/concepts/multi-agent).

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

### Поля match для binding

- `type` (необов'язково): `route` для звичайної маршрутизації (відсутній type означає route), `acp` для постійних ACP-прив'язок розмов.
- `match.channel` (обов'язково)
- `match.accountId` (необов'язково; `*` = будь-який обліковий запис; якщо пропущено = default-обліковий запис)
- `match.peer` (необов'язково; `{ kind: direct|group|channel, id }`)
- `match.guildId` / `match.teamId` (необов'язково; залежить від каналу)
- `acp` (необов'язково; лише для `type: "acp"`): `{ mode, label, cwd, backend }`

**Детермінований порядок збігу:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId` (точний, без peer/guild/team)
5. `match.accountId: "*"` (по всьому каналу)
6. Default-агент

У межах кожного рівня перший відповідний запис `bindings` має пріоритет.

Для записів `type: "acp"` OpenClaw виконує визначення за точною ідентичністю розмови (`match.channel` + account + `match.peer.id`) і не використовує порядок рівнів route binding, наведений вище.

### Профілі доступу для окремого агента

<Accordion title="Повний доступ (без sandbox)">

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

<Accordion title="Інструменти лише для читання + workspace">

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

<Accordion title="Без доступу до файлової системи (лише обмін повідомленнями)">

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

Деталі пріоритетів див. у [Multi-Agent Sandbox & Tools](/uk/tools/multi-agent-sandbox-tools).

---

## Session

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
    parentForkMaxTokens: 100000, // skip parent-thread fork above this token count (0 disables)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // duration or false
      maxDiskBytes: "500mb", // optional hard budget
      highWaterBytes: "400mb", // optional cleanup target
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // default inactivity auto-unfocus in hours (`0` disables)
      maxAgeHours: 0, // default hard max age in hours (`0` disables)
    },
    mainKey: "main", // legacy (runtime always uses "main")
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="Деталі полів session">

- **`scope`**: базова стратегія групування сесій для контекстів групового чату.
  - `per-sender` (за замовчуванням): кожен відправник отримує ізольовану сесію в межах контексту каналу.
  - `global`: усі учасники в контексті каналу ділять одну сесію (використовуйте лише тоді, коли потрібен спільний контекст).
- **`dmScope`**: як групуються DM.
  - `main`: усі DM використовують main session.
  - `per-peer`: ізоляція за sender id між каналами.
  - `per-channel-peer`: ізоляція за каналом + відправником (рекомендовано для inbox з багатьма користувачами).
  - `per-account-channel-peer`: ізоляція за обліковим записом + каналом + відправником (рекомендовано для багатообліковості).
- **`identityLinks`**: відображення канонічних id на peer з префіксом provider для спільного використання сесії між каналами.
- **`reset`**: основна політика reset. `daily` скидає о `atHour` за місцевим часом; `idle` скидає після `idleMinutes`. Якщо налаштовано обидва, спрацьовує те, що настане раніше.
- **`resetByType`**: перевизначення для типів (`direct`, `group`, `thread`). Застарілий `dm` приймається як alias для `direct`.
- **`parentForkMaxTokens`**: максимальний `totalTokens` батьківської сесії, дозволений під час створення forked thread session (за замовчуванням `100000`).
  - Якщо `totalTokens` батьківської сесії перевищує це значення, OpenClaw починає нову thread session замість успадкування історії transcript батьківської сесії.
  - Установіть `0`, щоб вимкнути цей запобіжник і завжди дозволяти fork від батьківської сесії.
- **`mainKey`**: застаріле поле. Тепер середовище виконання завжди використовує `"main"` для основного direct-chat bucket.
- **`agentToAgent.maxPingPongTurns`**: максимальна кількість зворотних ходів між агентами під час обмінів agent-to-agent (ціле число, діапазон: `0`–`5`). `0` вимикає ping-pong chaining.
- **`sendPolicy`**: збіг за `channel`, `chatType` (`direct|group|channel`, із застарілим alias `dm`), `keyPrefix` або `rawKeyPrefix`. Перший deny має пріоритет.
- **`maintenance`**: очищення сховища сесій + контроль retention.
  - `mode`: `warn` лише видає попередження; `enforce` застосовує очищення.
  - `pruneAfter`: віковий cutoff для застарілих записів (за замовчуванням `30d`).
  - `maxEntries`: максимальна кількість записів у `sessions.json` (за замовчуванням `500`).
  - `rotateBytes`: ротує `sessions.json`, коли його розмір перевищує це значення (за замовчуванням `10mb`).
  - `resetArchiveRetention`: retention для архівів transcript `*.reset.<timestamp>`. За замовчуванням дорівнює `pruneAfter`; установіть `false`, щоб вимкнути.
  - `maxDiskBytes`: необов'язковий ліміт дискового простору для каталогу сесій. У режимі `warn` логуються попередження; у режимі `enforce` спочатку видаляються найстаріші артефакти/сесії.
  - `highWaterBytes`: необов'язкова ціль після очищення за бюджетом. За замовчуванням дорівнює `80%` від `maxDiskBytes`.
- **`threadBindings`**: глобальні значення за замовчуванням для можливостей сесій, прив'язаних до потоків.
  - `enabled`: головний перемикач за замовчуванням (postачальники можуть перевизначати; Discord використовує `channels.discord.threadBindings.enabled`)
  - `idleHours`: default авто-зняття фокусу через неактивність у годинах (`0` вимикає; postачальники можуть перевизначати)
  - `maxAgeHours`: default жорсткий максимальний вік у годинах (`0` вимикає; postачальники можуть перевизначати)

</Accordion>

---

## Messages

```json5
{
  messages: {
    responsePrefix: "🦞", // or "auto"
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
      debounceMs: 2000, // 0 disables
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### Префікс відповіді

Перевизначення для каналу/облікового запису: `channels.<channel>.responsePrefix`, `channels.<channel>.accounts.<id>.responsePrefix`.

Порядок визначення (перемагає найспецифічніше): account → channel → global. `""` вимикає і зупиняє каскад. `"auto"` виводить `[{identity.name}]`.

**Змінні шаблону:**

| Змінна            | Опис                    | Приклад                     |
| ----------------- | ----------------------- | --------------------------- |
| `{model}`         | Коротка назва моделі    | `claude-opus-4-6`           |
| `{modelFull}`     | Повний ідентифікатор моделі | `anthropic/claude-opus-4-6` |
| `{provider}`      | Назва постачальника     | `anthropic`                 |
| `{thinkingLevel}` | Поточний рівень thinking | `high`, `low`, `off`        |
| `{identity.name}` | Назва identity агента   | (те саме, що `"auto"`)      |

Змінні нечутливі до регістру. `{think}` — alias для `{thinkingLevel}`.

### Ack reaction

- За замовчуванням використовується `identity.emoji` активного агента, інакше `"👀"`. Установіть `""`, щоб вимкнути.
- Перевизначення для каналу: `channels.<channel>.ackReaction`, `channels.<channel>.accounts.<id>.ackReaction`.
- Порядок визначення: account → channel → `messages.ackReaction` → резервний варіант з identity.
- Область: `group-mentions` (за замовчуванням), `group-all`, `direct`, `all`.
- `removeAckAfterReply`: видаляє ack після відповіді у Slack, Discord і Telegram.
- `messages.statusReactions.enabled`: вмикає реакції статусу життєвого циклу у Slack, Discord і Telegram.
  У Slack і Discord, якщо параметр не задано, реакції статусу лишаються увімкненими, коли активні ack reaction.
  У Telegram потрібно явно встановити `true`, щоб увімкнути реакції статусу життєвого циклу.

### Debounce для вхідних повідомлень

Об'єднує швидкі текстові повідомлення від того самого відправника в один хід агента. Media/вкладення скидаються одразу. Керувальні команди обходять debounce.

### TTS (text-to-speech)

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

- `auto` керує auto-TTS. `/tts off|always|inbound|tagged` перевизначає налаштування для сесії.
- `summaryModel` перевизначає `agents.defaults.model.primary` для auto-summary.
- `modelOverrides` увімкнено за замовчуванням; для `modelOverrides.allowProvider` за замовчуванням встановлено `false` (потрібне явне ввімкнення).
- API keys резервно беруться з `ELEVENLABS_API_KEY`/`XI_API_KEY` і `OPENAI_API_KEY`.
- `openai.baseUrl` перевизначає endpoint OpenAI TTS. Порядок визначення: config, потім `OPENAI_TTS_BASE_URL`, потім `https://api.openai.com/v1`.
- Коли `openai.baseUrl` вказує на не-OpenAI endpoint, OpenClaw розглядає його як OpenAI-compatible TTS server і послаблює перевірку model/voice.

---

## Talk

Значення за замовчуванням для режиму Talk (macOS/iOS/Android).

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

- `talk.provider` має відповідати ключу в `talk.providers`, коли налаштовано кілька Talk providers.
- Застарілі плоскі ключі Talk (`talk.voiceId`, `talk.voiceAliases`, `talk.modelId`, `talk.outputFormat`, `talk.apiKey`) сумісні лише для зворотної сумісності й автоматично мігруються в `talk.providers.<provider>`.
- Voice ID резервно беруться з `ELEVENLABS_VOICE_ID` або `SAG_VOICE_ID`.
- `providers.*.apiKey` приймає відкриті рядки або об'єкти SecretRef.
- Резервний `ELEVENLABS_API_KEY` застосовується лише тоді, коли API key Talk не налаштовано.
- `providers.*.voiceAliases` дозволяє директивам Talk використовувати дружні назви.
- `silenceTimeoutMs` визначає, скільки Talk mode чекатиме після мовчання користувача, перш ніж надіслати transcript. Якщо не встановлено, зберігається pause window платформи за замовчуванням (`700 ms на macOS і Android, 900 ms на iOS`).

---

## Tools

### Профілі інструментів

`tools.profile` задає базовий список дозволів перед `tools.allow`/`tools.deny`:

Під час локального онбордингу нові локальні конфігурації за замовчуванням отримують `tools.profile: "coding"`, якщо параметр не встановлено (наявні явні профілі зберігаються).

| Профіль     | Містить                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | лише `session_status`                                                                                                           |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                       |
| `full`      | Без обмежень (так само, як якщо не задано)                                                                                      |

### Групи інструментів

| Група              | Інструменти                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `group:runtime`    | `exec`, `process`, `code_execution` (`bash` приймається як alias для `exec`)                                            |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                                                   |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory`     | `memory_search`, `memory_get`                                                                                            |
| `group:web`        | `web_search`, `x_search`, `web_fetch`                                                                                    |
| `group:ui`         | `browser`, `canvas`                                                                                                      |
| `group:automation` | `cron`, `gateway`                                                                                                        |
| `group:messaging`  | `message`                                                                                                                |
| `group:nodes`      | `nodes`                                                                                                                  |
| `group:agents`     | `agents_list`                                                                                                            |
| `group:media`      | `image`, `image_generate`, `video_generate`, `tts`                                                                       |
| `group:openclaw`   | Усі вбудовані інструменти (без provider plugins)                                                                         |

### `tools.allow` / `tools.deny`

Глобальна політика allow/deny для інструментів (deny має пріоритет). Регістронезалежна, підтримує шаблони `*`. Застосовується, навіть коли Docker sandbox вимкнено.

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

Додатково обмежує інструменти для конкретних постачальників або моделей. Порядок: базовий profile → profile постачальника → allow/deny.

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

Керує elevated-доступом до exec поза sandbox:

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

- Перевизначення для окремого агента (`agents.list[].tools.elevated`) може лише додатково обмежувати.
- `/elevated on|off|ask|full` зберігає стан для кожної сесії; вбудовані директиви застосовуються до одного повідомлення.
- Elevated `exec` обходить sandbox і використовує налаштований шлях виходу (`gateway` за замовчуванням або `node`, коли ціллю exec є `node`).

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

Перевірки безпеки tool-loop **вимкнені за замовчуванням**. Установіть `enabled: true`, щоб активувати виявлення.
Налаштування можна визначити глобально в `tools.loopDetection` і перевизначити для окремого агента в `agents.list[].tools.loopDetection`.

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

- `historySize`: максимальна історія викликів інструментів, що зберігається для аналізу циклів.
- `warningThreshold`: поріг повторюваного шаблону без прогресу для попереджень.
- `criticalThreshold`: вищий поріг повторення для блокування критичних циклів.
- `globalCircuitBreakerThreshold`: жорсткий поріг зупинки для будь-якого запуску без прогресу.
- `detectors.genericRepeat`: попереджати про повторювані виклики того самого інструмента з тими самими аргументами.
- `detectors.knownPollNoProgress`: попереджати/блокувати відомі poll-інструменти (`process.poll`, `command_status` тощо).
- `detectors.pingPong`: попереджати/блокувати чергування без прогресу у парах викликів.
- Якщо `warningThreshold >= criticalThreshold` або `criticalThreshold >= globalCircuitBreakerThreshold`, валідація завершується помилкою.

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // or BRAVE_API_KEY env
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // optional; omit for auto-detect
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

Налаштовує розуміння вхідних media (зображення/аудіо/відео):

```json5
{
  tools: {
    media: {
      concurrency: 2,
      asyncCompletion: {
        directSend: false, // opt-in: send finished async music/video directly to the channel
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

<Accordion title="Поля запису media model">

**Запис постачальника** (`type: "provider"` або пропущено):

- `provider`: ID API-постачальника (`openai`, `anthropic`, `google`/`gemini`, `groq` тощо)
- `model`: перевизначення model id
- `profile` / `preferredProfile`: вибір profile у `auth-profiles.json`

**CLI-запис** (`type: "cli"`):

- `command`: виконуваний файл
- `args`: аргументи-шаблони (підтримуються `{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}` тощо)

**Спільні поля:**

- `capabilities`: необов'язковий список (`image`, `audio`, `video`). За замовчуванням: `openai`/`anthropic`/`minimax` → image, `google` → image+audio+video, `groq` → audio.
- `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`: перевизначення для конкретного запису.
- Помилки переводять виконання до наступного запису.

Автентифікація постачальників дотримується стандартного порядку: `auth-profiles.json` → env vars → `models.providers.*.apiKey`.

**Поля async completion:**

- `asyncCompletion.directSend`: коли `true`, завершені асинхронні завдання `music_generate`
  і `video_generate` спочатку намагаються доставити результат безпосередньо в канал. За замовчуванням: `false`
  (застарілий шлях requester-session wake/model-delivery).

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

Керує тим, які сесії можуть бути ціллю для session tools (`sessions_list`, `sessions_history`, `sessions_send`).

За замовчуванням: `tree` (поточна сесія + сесії, породжені нею, наприклад subagents).

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

Примітки:

- `self`: лише поточний session key.
- `tree`: поточна сесія + сесії, породжені поточною сесією (subagents).
- `agent`: будь-яка сесія, що належить поточному agent id (може включати інших користувачів, якщо ви використовуєте per-sender sessions під тим самим agent id).
- `all`: будь-яка сесія. Націлення між агентами все одно потребує `tools.agentToAgent`.
- Обмеження sandbox: коли поточна сесія працює в sandbox і `agents.defaults.sandbox.sessionToolsVisibility="spawned"`, visibility примусово встановлюється в `tree`, навіть якщо `tools.sessions.visibility="all"`.

### `tools.sessions_spawn`

Керує підтримкою inline-вкладень для `sessions_spawn`.

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // opt-in: set true to allow inline file attachments
        maxTotalBytes: 5242880, // 5 MB total across all files
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 MB per file
        retainOnSessionKeep: false, // keep attachments when cleanup="keep"
      },
    },
  },
}
```

Примітки:

- Вкладення підтримуються лише для `runtime: "subagent"`. ACP runtime їх відхиляє.
- Файли матеріалізуються в дочірньому workspace за шляхом `.openclaw/attachments/<uuid>/` разом із `.manifest.json`.
- Вміст вкладень автоматично редагується з transcript persistence.
- Base64-входи перевіряються за суворими правилами алфавіту/відступів і з перевіркою розміру до декодування.
- Права доступу до файлів: `0700` для каталогів і `0600` для файлів.
- Очищення дотримується політики `cleanup`: `delete` завжди видаляє вкладення; `keep` зберігає їх лише коли `retainOnSessionKeep: true`.

### `tools.experimental`

Експериментальні прапорці для вбудованих інструментів. За замовчуванням вимкнено, якщо не діє автоматичне ввімкнення, специфічне для runtime.

```json5
{
  tools: {
    experimental: {
      planTool: true, // enable experimental update_plan
    },
  },
}
```

Примітки:

- `planTool`: вмикає структурований інструмент `update_plan` для відстеження нетривіальної багатокрокової роботи.
- За замовчуванням: `false` для не-OpenAI постачальників. Під час запусків OpenAI і OpenAI Codex він вмикається автоматично.
- Коли ввімкнено, системний prompt також додає вказівки з використання, щоб модель застосовувала його лише для суттєвої роботи та тримала щонайбільше один крок у стані `in_progress`.

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

- `model`: default model для породжених sub-agent. Якщо пропущено, sub-agents успадковують model викликача.
- `allowAgents`: default список дозволених target agent id для `sessions_spawn`, коли агент-запитувач не задає власне `subagents.allowAgents` (`["*"]` = будь-який; за замовчуванням: лише той самий агент).
- `runTimeoutSeconds`: default timeout (у секундах) для `sessions_spawn`, коли у виклику інструмента пропущено `runTimeoutSeconds`. `0` означає відсутність timeout.
- Політика інструментів для subagent: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.

---

## Користувацькі постачальники та base URL

OpenClaw використовує вбудований каталог моделей. Додавайте користувацьких постачальників через `models.providers` у конфігурації або `~/.openclaw/agents/<agentId>/agent/models.json`.

```json5
{
  models: {
    mode: "merge", // merge (default) | replace
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

- Використовуйте `authHeader: true` + `headers` для спеціальних потреб автентифікації.
- Перевизначайте корінь конфігурації агента через `OPENCLAW_AGENT_DIR` (або `PI_CODING_AGENT_DIR`, застарілий alias змінної середовища).
- Пріоритет злиття для однакових provider ID:
  - Непорожні значення `baseUrl` з agent `models.json` мають пріоритет.
  - Непорожні значення `apiKey` з агента мають пріоритет лише тоді, коли цей provider не керується через SecretRef у поточному контексті config/auth-profile.
  - Значення `apiKey` для provider, керованих через SecretRef, оновлюються з source marker (`ENV_VAR_NAME` для env refs, `secretref-managed` для file/exec refs) замість збереження визначених секретів.
  - Значення заголовків provider, керованих через SecretRef, оновлюються з source marker (`secretref-env:ENV_VAR_NAME` для env refs, `secretref-managed` для file/exec refs).
  - Порожні або відсутні `apiKey`/`baseUrl` в агенті повертаються до `models.providers` у конфігурації.
  - Для однакових моделей `contextWindow`/`maxTokens` використовують більше значення між явною конфігурацією та неявними значеннями каталогу.
  - Для однакових моделей `contextTokens` зберігає явний runtime cap, коли той заданий; використовуйте його, щоб обмежити ефективний контекст без зміни нативних метаданих моделі.
  - Використовуйте `models.mode: "replace"`, якщо хочете, щоб конфігурація повністю переписала `models.json`.
  - Збереження marker є source-authoritative: markers записуються з активного знімка вихідної конфігурації (до визначення), а не з визначених runtime secret values.

### Деталі полів постачальника

- `models.mode`: поведінка каталогу постачальників (`merge` або `replace`).
- `models.providers`: карта користувацьких постачальників за ключем provider id.
- `models.providers.*.api`: адаптер запитів (`openai-completions`, `openai-responses`, `anthropic-messages`, `google-generative-ai` тощо).
- `models.providers.*.apiKey`: облікові дані постачальника (краще через SecretRef/env substitution).
- `models.providers.*.auth`: стратегія автентифікації (`api-key`, `token`, `oauth`, `aws-sdk`).
- `models.providers.*.injectNumCtxForOpenAICompat`: для Ollama + `openai-completions` вбудовувати `options.num_ctx` у запити (за замовчуванням: `true`).
- `models.providers.*.authHeader`: примусово передавати облікові дані в заголовку `Authorization`, якщо це потрібно.
- `models.providers.*.baseUrl`: базовий URL зовнішнього API.
- `models.providers.*.headers`: додаткові статичні заголовки для proxy/tenant-routing.
- `models.providers.*.request`: перевизначення транспорту для HTTP-запитів model-provider.
  - `request.headers`: додаткові заголовки (зливаються зі стандартними заголовками постачальника). Значення приймають SecretRef.
  - `request.auth`: перевизначення стратегії автентифікації. Режими: `"provider-default"` (використовувати вбудовану автентифікацію постачальника), `"authorization-bearer"` (з `token`), `"header"` (з `headerName`, `value`, необов'язковим `prefix`).
  - `request.proxy`: перевизначення HTTP-proxy. Режими: `"env-proxy"` (використовувати env vars `HTTP_PROXY`/`HTTPS_PROXY`), `"explicit-proxy"` (з `url`). Обидва режими приймають необов'язковий підоб'єкт `tls`.
  - `request.tls`: перевизначення TLS для прямих з'єднань. Поля: `ca`, `cert`, `key`, `passphrase` (усі приймають SecretRef), `serverName`, `insecureSkipVerify`.
- `models.providers.*.models`: явні записи каталогу моделей постачальника.
- `models.providers.*.models.*.contextWindow`: метадані нативного context window моделі.
- `models.providers.*.models.*.contextTokens`: необов'язкове runtime-обмеження контексту. Використовуйте це, коли хочете мати менший ефективний бюджет контексту, ніж нативний `contextWindow` моделі.
- `models.providers.*.models.*.compat.supportsDeveloperRole`: необов'язкова підказка сумісності. Для `api: "openai-completions"` з непорожнім не-нативним `baseUrl` (host не `api.openai.com`) OpenClaw примусово встановлює це в `false` під час виконання. Порожній/пропущений `baseUrl` зберігає стандартну поведінку OpenAI.
- `plugins.entries.amazon-bedrock.config.discovery`: корінь налаштувань auto-discovery Bedrock.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: увімкнути/вимкнути неявне discovery.
- `plugins.entries.amazon-bedrock.config.discovery.region`: AWS region для discovery.
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: необов'язковий фільтр provider-id для цільового discovery.
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: інтервал опитування для оновлення discovery.
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: резервне context window для виявлених моделей.
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: резервна максимальна кількість вихідних токенів для виявлених моделей.

### Приклади постачальників

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

Використовуйте `cerebras/zai-glm-4.7` для Cerebras; `zai/glm-4.7` — для прямого Z.AI.

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

Установіть `OPENCODE_API_KEY` (або `OPENCODE_ZEN_API_KEY`). Використовуйте посилання `opencode/...` для каталогу Zen або `opencode-go/...` для каталогу Go. Скорочення: `openclaw onboard --auth-choice opencode-zen` або `openclaw onboard --auth-choice opencode-go`.

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

Установіть `ZAI_API_KEY`. Приймаються alias `z.ai/*` і `z-ai/*`. Скорочення: `openclaw onboard --auth-choice zai-api-key`.

- Загальний endpoint: `https://api.z.ai/api/paas/v4`
- Endpoint для кодування (за замовчуванням): `https://api.z.ai/api/coding/paas/v4`
- Для загального endpoint визначте користувацького постачальника з перевизначенням base URL.

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

Для endpoint Китаю: `baseUrl: "https://api.moonshot.cn/v1"` або `openclaw onboard --auth-choice moonshot-api-key-cn`.

Нативні endpoint Moonshot декларують сумісність використання streaming на спільному
транспорті `openai-completions`, і OpenClaw тепер визначає це за можливостями endpoint,
а не лише за built-in provider id.

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

Вбудований постачальник, сумісний з Anthropic. Скорочення: `openclaw onboard --auth-choice kimi-code-api-key`.

</Accordion>

<Accordion title="Synthetic (Anthropic-compatible)">

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

Base URL має не містити `/v1` (клієнт Anthropic додає його сам). Скорочення: `openclaw onboard --auth-choice synthetic-api-key`.

</Accordion>

<Accordion title="MiniMax M2.7 (direct)">

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

Установіть `MINIMAX_API_KEY`. Скорочення:
`openclaw onboard --auth-choice minimax-global-api` або
`openclaw onboard --auth-choice minimax-cn-api`.
Каталог моделей тепер за замовчуванням містить лише M2.7.
На Anthropic-compatible streaming path OpenClaw за замовчуванням вимикає thinking для MiniMax,
якщо ви явно не встановите `thinking` самостійно. `/fast on` або
`params.fastMode: true` переписує `MiniMax-M2.7` у
`MiniMax-M2.7-highspeed`.

</Accordion>

<Accordion title="Локальні моделі (LM Studio)">

Див. [Local Models](/uk/gateway/local-models). Коротко: запускайте велику локальну модель через LM Studio Responses API на потужному обладнанні; залишайте hosted models злитими як резервний варіант.

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
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // or plaintext string
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: необов'язковий список дозволених лише для bundled Skills (managed/workspace Skills це не зачіпає).
- `load.extraDirs`: додаткові спільні корені Skills (найнижчий пріоритет).
- `install.preferBrew`: коли true, віддавати перевагу інсталяторам Homebrew, якщо
  `brew` доступний, перш ніж переходити до інших типів інсталяторів.
- `install.nodeManager`: пріоритет node-інсталятора для специфікацій `metadata.openclaw.install`
  (`npm` | `pnpm` | `yarn` | `bun`).
- `entries.<skillKey>.enabled: false` вимикає Skill, навіть якщо він bundled/installed.
- `entries.<skillKey>.apiKey`: зручне поле API key для Skills, які оголошують основну env var (відкритий рядок або об'єкт SecretRef).

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

- Завантажуються з `~/.openclaw/extensions`, `<workspace>/.openclaw/extensions` і `plugins.load.paths`.
- Discovery приймає нативні plugins OpenClaw, а також сумісні пакети Codex і Claude, включно з пакетами Claude без manifest у стандартному layout.
- **Зміни конфігурації потребують перезапуску шлюзу.**
- `allow`: необов'язковий список дозволених plugins (завантажуються лише перелічені plugins). `deny` має пріоритет.
- `plugins.entries.<id>.apiKey`: зручне поле API key на рівні plugin (коли plugin це підтримує).
- `plugins.entries.<id>.env`: карта env vars для окремого plugin.
- `plugins.entries.<id>.hooks.allowPromptInjection`: коли `false`, core блокує `before_prompt_build` і ігнорує поля legacy `before_agent_start`, що змінюють prompt, зберігаючи при цьому legacy `modelOverride` і `providerOverride`. Це стосується нативних plugin hooks і підтримуваних каталогів hooks, наданих пакетами.
- `plugins.entries.<id>.subagent.allowModelOverride