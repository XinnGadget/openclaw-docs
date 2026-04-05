---
read_when:
    - Вам потрібні точні семантики або значення за замовчуванням конфігурації на рівні полів
    - Ви перевіряєте блоки конфігурації каналів, моделей, шлюзу або інструментів
summary: Повний довідник для кожного ключа конфігурації OpenClaw, значень за замовчуванням і налаштувань каналів
title: Довідник з конфігурації
x-i18n:
    generated_at: "2026-04-05T19:23:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: b2ac0b26762d642cd3667b3f18b11938947968e79d9cd363e86e31312ce7e981
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# Довідник з конфігурації

Кожне поле, доступне в `~/.openclaw/openclaw.json`. Для огляду, орієнтованого на завдання, див. [Configuration](/uk/gateway/configuration).

Формат конфігурації — **JSON5** (дозволені коментарі та кінцеві коми). Усі поля необов'язкові — OpenClaw використовує безпечні значення за замовчуванням, якщо їх не вказано.

---

## Канали

Кожен канал запускається автоматично, коли існує його розділ конфігурації (якщо не вказано `enabled: false`).

### Доступ до особистих і групових чатів

Усі канали підтримують політики для особистих повідомлень і політики для груп:

| Політика особистих повідомлень | Поведінка                                                       |
| ------------------------------ | --------------------------------------------------------------- |
| `pairing` (за замовчуванням)   | Невідомі відправники отримують одноразовий код сполучення; власник має схвалити |
| `allowlist`                    | Лише відправники з `allowFrom` (або зі сховища дозволів для сполучених) |
| `open`                         | Дозволити всі вхідні особисті повідомлення (потрібно `allowFrom: ["*"]`) |
| `disabled`                     | Ігнорувати всі вхідні особисті повідомлення                     |

| Політика груп        | Поведінка                                               |
| -------------------- | ------------------------------------------------------- |
| `allowlist` (за замовчуванням) | Лише групи, що відповідають налаштованому списку дозволів |
| `open`               | Обходити списки дозволів для груп (обмеження за згадками все одно застосовується) |
| `disabled`           | Блокувати всі повідомлення груп/кімнат                  |

<Note>
`channels.defaults.groupPolicy` задає значення за замовчуванням, коли `groupPolicy` постачальника не встановлено.
Коди сполучення закінчують дію через 1 годину. Кількість очікуваних запитів на сполучення для особистих повідомлень обмежена **3 на канал**.
Якщо блок постачальника повністю відсутній (`channels.<provider>` відсутній), політика груп під час виконання повертається до `allowlist` (fail-closed) із попередженням під час запуску.
</Note>

### Перевизначення моделей для каналів

Використовуйте `channels.modelByChannel`, щоб прив'язати конкретні ідентифікатори каналів до моделі. Значення приймають `provider/model` або налаштовані псевдоніми моделей. Відображення каналу застосовується, коли для сесії ще не встановлено перевизначення моделі (наприклад, через `/model`).

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

### Значення каналів за замовчуванням і heartbeat

Використовуйте `channels.defaults` для спільної поведінки політики груп і heartbeat у різних постачальників:

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
- `channels.defaults.contextVisibility`: режим видимості додаткового контексту за замовчуванням для всіх каналів. Значення: `all` (за замовчуванням, включати весь процитований/потоковий/історичний контекст), `allowlist` (включати контекст лише від відправників зі списку дозволів), `allowlist_quote` (як allowlist, але зберігати явний контекст цитування/відповіді). Перевизначення для каналу: `channels.<channel>.contextVisibility`.
- `channels.defaults.heartbeat.showOk`: включати статуси справних каналів у вивід heartbeat.
- `channels.defaults.heartbeat.showAlerts`: включати деградовані/помилкові статуси у вивід heartbeat.
- `channels.defaults.heartbeat.useIndicator`: відображати компактний heartbeat у стилі індикатора.

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
      sendReadReceipts: true, // сині галочки (false у режимі self-chat)
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

- Вихідні команди за замовчуванням використовують обліковий запис `default`, якщо він є; інакше — перший налаштований `accountId` (відсортовано).
- Необов'язковий `channels.whatsapp.defaultAccount` перевизначає цей резервний вибір облікового запису за замовчуванням, якщо він відповідає налаштованому `accountId`.
- Застарілий каталог автентифікації Baileys для одного облікового запису переноситься командою `openclaw doctor` до `whatsapp/default`.
- Перевизначення для облікового запису: `channels.whatsapp.accounts.<id>.sendReadReceipts`, `channels.whatsapp.accounts.<id>.dmPolicy`, `channels.whatsapp.accounts.<id>.allowFrom`.

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
          systemPrompt: "Відповідай коротко.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Тримайся теми.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Резервна копія Git" },
        { command: "generate", description: "Створити зображення" },
      ],
      historyLimit: 50,
      replyToMode: "first", // off | first | all
      linkPreview: true,
      streaming: "partial", // off | partial | block | progress (за замовчуванням: off; вмикайте явно, щоб уникнути обмежень на частоту редагування попереднього перегляду)
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

- Токен бота: `channels.telegram.botToken` або `channels.telegram.tokenFile` (лише звичайний файл; символьні посилання відхиляються), з `TELEGRAM_BOT_TOKEN` як резервним варіантом для облікового запису за замовчуванням.
- Необов'язковий `channels.telegram.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він відповідає налаштованому `accountId`.
- У багатьох облікових записах (2+ `accountId`) установіть явний типово вибраний обліковий запис (`channels.telegram.defaultAccount` або `channels.telegram.accounts.default`), щоб уникнути резервної маршрутизації; `openclaw doctor` попереджає, якщо його немає або він недійсний.
- `configWrites: false` блокує ініційовані з Telegram записи конфігурації (міграції ID супергруп, `/config set|unset`).
- Записи верхнього рівня `bindings[]` із `type: "acp"` налаштовують постійні ACP-прив'язки для тем форуму (використовуйте канонічний `chatId:topic:topicId` у `match.peer.id`). Семантика полів спільна з [ACP Agents](/uk/tools/acp-agents#channel-specific-settings).
- Попередній перегляд потоків Telegram використовує `sendMessage` + `editMessageText` (працює в особистих і групових чатах).
- Політика повторних спроб: див. [Retry policy](/uk/concepts/retry).

### Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 8,
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
      replyToMode: "off", // off | first | all
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
              systemPrompt: "Лише короткі відповіді.",
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length", // length | newline
      streaming: "off", // off | partial | block | progress (progress відображається як partial у Discord)
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
        spawnSubagentSessions: false, // opt-in для sessions_spawn({ thread: true })
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
- Прямі вихідні виклики, які передають явний Discord `token`, використовують цей токен для виклику; налаштування повторних спроб/політики облікового запису все одно беруться з вибраного облікового запису в активному знімку середовища виконання.
- Необов'язковий `channels.discord.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він відповідає налаштованому `accountId`.
- Використовуйте `user:<id>` (особисті повідомлення) або `channel:<id>` (канал гільдії) як цілі доставки; прості числові ID відхиляються.
- Slug-и гільдій містять лише малі літери, а пробіли замінюються на `-`; ключі каналів використовують slug-ім'я (без `#`). Віддавайте перевагу ID гільдій.
- Повідомлення, створені ботом, типово ігноруються. `allowBots: true` вмикає їх; використовуйте `allowBots: "mentions"`, щоб приймати лише повідомлення ботів, які згадують бота (власні повідомлення все одно відфільтровуються).
- `channels.discord.guilds.<id>.ignoreOtherMentions` (і перевизначення каналів) відкидає повідомлення, які згадують іншого користувача або роль, але не бота (без урахування @everyone/@here).
- `maxLinesPerMessage` (за замовчуванням 17) розбиває високі повідомлення, навіть якщо вони коротші за 2000 символів.
- `channels.discord.threadBindings` керує маршрутизацією, прив'язаною до потоків Discord:
  - `enabled`: перевизначення Discord для функцій сесій, прив'язаних до потоку (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` і прив'язана доставка/маршрутизація)
  - `idleHours`: перевизначення Discord для авто-скасування фокусу через неактивність у годинах (`0` вимикає)
  - `maxAgeHours`: перевизначення Discord для жорсткого максимального віку в годинах (`0` вимикає)
  - `spawnSubagentSessions`: перемикач opt-in для автоматичного створення/прив'язки потоків через `sessions_spawn({ thread: true })`
- Записи верхнього рівня `bindings[]` із `type: "acp"` налаштовують постійні ACP-прив'язки для каналів і потоків (використовуйте ID каналу/потоку в `match.peer.id`). Семантика полів спільна з [ACP Agents](/uk/tools/acp-agents#channel-specific-settings).
- `channels.discord.ui.components.accentColor` задає колір акценту для контейнерів Discord components v2.
- `channels.discord.voice` вмикає розмови в голосових каналах Discord і необов'язкові перевизначення auto-join + TTS.
- `channels.discord.voice.daveEncryption` і `channels.discord.voice.decryptionFailureTolerance` напряму передаються в параметри DAVE `@discordjs/voice` (`true` і `24` за замовчуванням).
- OpenClaw також намагається відновити прийом голосу, виходячи та повторно входячи в голосову сесію після повторних помилок дешифрування.
- `channels.discord.streaming` — канонічний ключ режиму потоку. Застарілі `streamMode` і булеві значення `streaming` автоматично переносяться.
- `channels.discord.autoPresence` відображає доступність середовища виконання у присутність бота (healthy => online, degraded => idle, exhausted => dnd) і дозволяє необов'язкові перевизначення тексту статусу.
- `channels.discord.dangerouslyAllowNameMatching` знову вмикає зіставлення за змінюваними іменами/тегами (режим сумісності break-glass).
- `channels.discord.execApprovals`: доставка схвалень exec у стилі Discord і авторизація схвалювачів.
  - `enabled`: `true`, `false` або `"auto"` (за замовчуванням). В автоматичному режимі схвалення exec активуються, коли схвалювачів можна визначити через `approvers` або `commands.ownerAllowFrom`.
  - `approvers`: ID користувачів Discord, яким дозволено схвалювати запити exec. Якщо не вказано, використовується `commands.ownerAllowFrom`.
  - `agentFilter`: необов'язковий список дозволених ID агентів. Якщо опустити, пересилаються схвалення для всіх агентів.
  - `sessionFilter`: необов'язкові шаблони ключів сесій (підрядок або regex).
  - `target`: куди надсилати запити на схвалення. `"dm"` (за замовчуванням) надсилає в особисті повідомлення схвалювачів, `"channel"` — у канал походження, `"both"` — в обидва місця. Коли target містить `"channel"`, кнопки можуть використовувати лише визначені схвалювачі.
  - `cleanupAfterResolve`: коли `true`, видаляє особисті повідомлення зі схваленням після схвалення, відмови або тайм-ауту.

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

- JSON облікового запису служби: вбудований (`serviceAccount`) або з файлу (`serviceAccountFile`).
- Також підтримується SecretRef для облікового запису служби (`serviceAccountRef`).
- Резервні значення з env: `GOOGLE_CHAT_SERVICE_ACCOUNT` або `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- Використовуйте `spaces/<spaceId>` або `users/<userId>` як цілі доставки.
- `channels.googlechat.dangerouslyAllowNameMatching` знову вмикає зіставлення за змінюваним email principal (режим сумісності break-glass).

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
          systemPrompt: "Лише короткі відповіді.",
        },
      },
      historyLimit: 50,
      allowBots: false,
      reactionNotifications: "own",
      reactionAllowlist: ["U123"],
      replyToMode: "off", // off | first | all
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
      streaming: "partial", // off | partial | block | progress (режим попереднього перегляду)
      nativeStreaming: true, // використовувати нативний API потокової передачі Slack, коли streaming=partial
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

- **Режим Socket** потребує і `botToken`, і `appToken` (`SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` як резервне значення env для облікового запису за замовчуванням).
- **HTTP-режим** потребує `botToken` плюс `signingSecret` (на кореневому рівні або для окремого облікового запису).
- `botToken`, `appToken`, `signingSecret` і `userToken` приймають прості текстові
  рядки або об'єкти SecretRef.
- Знімки облікових записів Slack показують поля джерела/стану для кожного облікового даного, такі як
  `botTokenSource`, `botTokenStatus`, `appTokenStatus` і, в HTTP-режимі,
  `signingSecretStatus`. `configured_unavailable` означає, що обліковий запис
  налаштований через SecretRef, але поточний шлях команди/середовища виконання не зміг
  отримати значення секрету.
- `configWrites: false` блокує ініційовані зі Slack записи конфігурації.
- Необов'язковий `channels.slack.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він відповідає налаштованому `accountId`.
- `channels.slack.streaming` — канонічний ключ режиму потоку. Застарілі `streamMode` і булеві значення `streaming` автоматично переносяться.
- Використовуйте `user:<id>` (особисті повідомлення) або `channel:<id>` як цілі доставки.

**Режими сповіщень про реакції:** `off`, `own` (за замовчуванням), `all`, `allowlist` (із `reactionAllowlist`).

**Ізоляція сесій потоків:** `thread.historyScope` — для кожного потоку окремо (за замовчуванням) або спільно в межах каналу. `thread.inheritParent` копіює транскрипт батьківського каналу в нові потоки.

- `typingReaction` додає тимчасову реакцію до вхідного повідомлення Slack, поки виконується відповідь, а потім прибирає її після завершення. Використовуйте скорочений код емодзі Slack, наприклад `"hourglass_flowing_sand"`.
- `channels.slack.execApprovals`: доставка схвалень exec у стилі Slack і авторизація схвалювачів. Та сама схема, що і для Discord: `enabled` (`true`/`false`/`"auto"`), `approvers` (ID користувачів Slack), `agentFilter`, `sessionFilter` і `target` (`"dm"`, `"channel"` або `"both"`).

| Група дій   | За замовчуванням | Примітки               |
| ----------- | ---------------- | ---------------------- |
| reactions   | увімкнено        | Реакції + список реакцій |
| messages    | увімкнено        | Читання/надсилання/редагування/видалення |
| pins        | увімкнено        | Закріпити/відкріпити/перелік |
| memberInfo  | увімкнено        | Інформація про учасника |
| emojiList   | увімкнено        | Список власних емодзі   |

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
        // Необов'язковий явний URL для reverse-proxy/публічних розгортань
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

Режими чату: `oncall` (відповідати на @-згадку, за замовчуванням), `onmessage` (на кожне повідомлення), `onchar` (повідомлення, що починаються з префікса-тригера).

Коли увімкнено нативні команди Mattermost:

- `commands.callbackPath` має бути шляхом (наприклад `/api/channels/mattermost/command`), а не повним URL.
- `commands.callbackUrl` має вказувати на кінцеву точку шлюзу OpenClaw і бути доступним із сервера Mattermost.
- Нативні зворотні виклики slash-команд автентифікуються за токенами
  для кожної команди, які Mattermost повертає під час реєстрації slash-команд. Якщо реєстрація не вдається або жодну
  команду не активовано, OpenClaw відхиляє зворотні виклики з
  `Unauthorized: invalid command token.`
- Для приватних/tailnet/внутрішніх хостів зворотного виклику Mattermost може вимагати,
  щоб `ServiceSettings.AllowedUntrustedInternalConnections` містив хост/домен зворотного виклику.
  Використовуйте значення хоста/домену, а не повні URL.
- `channels.mattermost.configWrites`: дозволити або заборонити ініційовані з Mattermost записи конфігурації.
- `channels.mattermost.requireMention`: вимагати `@mention` перед відповіддю в каналах.
- `channels.mattermost.groups.<channelId>.requireMention`: перевизначення обмеження за згадками для окремого каналу (`"*"` для значення за замовчуванням).
- Необов'язковий `channels.mattermost.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він відповідає налаштованому `accountId`.

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // необов'язкова прив'язка облікового запису
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

**Режими сповіщень про реакції:** `off`, `own` (за замовчуванням), `all`, `allowlist` (із `reactionAllowlist`).

- `channels.signal.account`: прив'язати запуск каналу до конкретної ідентичності облікового запису Signal.
- `channels.signal.configWrites`: дозволити або заборонити ініційовані з Signal записи конфігурації.
- Необов'язковий `channels.signal.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він відповідає налаштованому `accountId`.

### BlueBubbles

BlueBubbles — рекомендований шлях для iMessage (на основі plugin, налаштовується в `channels.bluebubbles`).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl, password, webhookPath, елементи керування групами та розширені дії:
      // див. /channels/bluebubbles
    },
  },
}
```

- Тут охоплено основні шляхи ключів: `channels.bluebubbles`, `channels.bluebubbles.dmPolicy`.
- Необов'язковий `channels.bluebubbles.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він відповідає налаштованому `accountId`.
- Записи верхнього рівня `bindings[]` із `type: "acp"` можуть прив'язувати розмови BlueBubbles до постійних ACP-сесій. Використовуйте BlueBubbles handle або цільовий рядок (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) у `match.peer.id`. Спільна семантика полів: [ACP Agents](/uk/tools/acp-agents#channel-specific-settings).
- Повну конфігурацію каналу BlueBubbles описано в [BlueBubbles](/uk/channels/bluebubbles).

### iMessage

OpenClaw запускає `imsg rpc` (JSON-RPC через stdio). Демон або порт не потрібні.

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

- Необов'язковий `channels.imessage.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він відповідає налаштованому `accountId`.

- Потрібен Full Disk Access до БД Messages.
- Віддавайте перевагу цілям `chat_id:<id>`. Використовуйте `imsg chats --limit 20`, щоб переглянути список чатів.
- `cliPath` може вказувати на SSH-обгортку; установіть `remoteHost` (`host` або `user@host`) для отримання вкладень через SCP.
- `attachmentRoots` і `remoteAttachmentRoots` обмежують шляхи вхідних вкладень (за замовчуванням: `/Users/*/Library/Messages/Attachments`).
- SCP використовує сувору перевірку ключа хоста, тому переконайтеся, що ключ хоста ретранслятора вже є в `~/.ssh/known_hosts`.
- `channels.imessage.configWrites`: дозволити або заборонити ініційовані з iMessage записи конфігурації.
- Записи верхнього рівня `bindings[]` із `type: "acp"` можуть прив'язувати розмови iMessage до постійних ACP-сесій. Використовуйте нормалізований handle або явну ціль чату (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) у `match.peer.id`. Спільна семантика полів: [ACP Agents](/uk/tools/acp-agents#channel-specific-settings).

<Accordion title="Приклад SSH-обгортки для iMessage">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix підтримується розширенням і налаштовується в `channels.matrix`.

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
- `channels.matrix.proxy` спрямовує HTTP-трафік Matrix через явний HTTP(S)-проксі. Іменовані облікові записи можуть перевизначати його через `channels.matrix.accounts.<id>.proxy`.
- `channels.matrix.allowPrivateNetwork` дозволяє приватні/внутрішні homeserver-и. `proxy` і `allowPrivateNetwork` — незалежні елементи керування.
- `channels.matrix.defaultAccount` вибирає бажаний обліковий запис у багатьох облікових записах.
- `channels.matrix.execApprovals`: доставка схвалень exec у стилі Matrix і авторизація схвалювачів.
  - `enabled`: `true`, `false` або `"auto"` (за замовчуванням). В автоматичному режимі схвалення exec активуються, коли схвалювачів можна визначити через `approvers` або `commands.ownerAllowFrom`.
  - `approvers`: ID користувачів Matrix (наприклад `@owner:example.org`), яким дозволено схвалювати запити exec.
  - `agentFilter`: необов'язковий список дозволених ID агентів. Якщо опустити, пересилаються схвалення для всіх агентів.
  - `sessionFilter`: необов'язкові шаблони ключів сесій (підрядок або regex).
  - `target`: куди надсилати запити на схвалення. `"dm"` (за замовчуванням), `"channel"` (кімната походження) або `"both"`.
  - Перевизначення для облікового запису: `channels.matrix.accounts.<id>.execApprovals`.
- `channels.matrix.dm.sessionScope` керує тим, як особисті повідомлення Matrix групуються в сесії: `per-user` (за замовчуванням) ділиться за маршрутизованим співрозмовником, а `per-room` ізолює кожну кімнату особистих повідомлень.
- Перевірки статусу Matrix і пошук у live directory використовують ту саму політику проксі, що й трафік середовища виконання.
- Повну конфігурацію Matrix, правила цільового спрямування та приклади налаштування описано в [Matrix](/uk/channels/matrix).

### Microsoft Teams

Microsoft Teams підтримується розширенням і налаштовується в `channels.msteams`.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId, appPassword, tenantId, webhook, політики команд/каналів:
      // див. /channels/msteams
    },
  },
}
```

- Тут охоплено основні шляхи ключів: `channels.msteams`, `channels.msteams.configWrites`.
- Повну конфігурацію Teams (облікові дані, webhook, політика особистих/групових чатів, перевизначення для окремих команд/каналів) описано в [Microsoft Teams](/uk/channels/msteams).

### IRC

IRC підтримується розширенням і налаштовується в `channels.irc`.

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

- Тут охоплено основні шляхи ключів: `channels.irc`, `channels.irc.dmPolicy`, `channels.irc.configWrites`, `channels.irc.nickserv.*`.
- Необов'язковий `channels.irc.defaultAccount` перевизначає вибір облікового запису за замовчуванням, якщо він відповідає налаштованому `accountId`.
- Повну конфігурацію IRC-каналу (host/port/TLS/channels/allowlists/обмеження за згадками) описано в [IRC](/uk/channels/irc).

### Багато облікових записів (усі канали)

Запускайте кілька облікових записів на канал (кожен із власним `accountId`):

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "Основний бот",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "Бот сповіщень",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- `default` використовується, коли `accountId` опущено (CLI + маршрутизація).
- Токени з env застосовуються лише до облікового запису **default**.
- Базові налаштування каналу застосовуються до всіх облікових записів, якщо їх не перевизначено окремо.
- Використовуйте `bindings[].match.accountId`, щоб спрямувати кожен обліковий запис до іншого агента.
- Якщо ви додаєте не-default обліковий запис через `openclaw channels add` (або онбординг каналу), поки все ще використовуєте конфігурацію верхнього рівня для одного облікового запису, OpenClaw спочатку переносить значення верхнього рівня, прив'язані до одного облікового запису, у карту облікових записів каналу, щоб початковий обліковий запис і далі працював. Для більшості каналів вони переміщуються в `channels.<channel>.accounts.default`; Matrix натомість може зберегти наявну відповідну іменовану/default-ціль.
- Наявні прив'язки лише для каналу (без `accountId`) продовжують відповідати обліковому запису за замовчуванням; прив'язки з областю облікового запису залишаються необов'язковими.
- `openclaw doctor --fix` також виправляє змішані форми, переміщуючи значення верхнього рівня для одного облікового запису в просунутий обліковий запис, вибраний для цього каналу. Для більшості каналів використовується `accounts.default`; Matrix може зберегти наявну відповідну іменовану/default-ціль.

### Інші канали розширень

Багато каналів розширень налаштовуються як `channels.<id>` і описані на окремих сторінках каналів (наприклад Feishu, Matrix, LINE, Nostr, Zalo, Nextcloud Talk, Synology Chat і Twitch).
Див. повний індекс каналів: [Channels](/uk/channels).

### Обмеження за згадками в групових чатах

Для групових повідомлень за замовчуванням **потрібна згадка** (метадані згадки або безпечні regex-шаблони). Застосовується до групових чатів WhatsApp, Telegram, Discord, Google Chat та iMessage.

**Типи згадок:**

- **Згадки в метаданих**: нативні @-згадки платформи. Ігноруються в режимі self-chat у WhatsApp.
- **Текстові шаблони**: безпечні regex-шаблони в `agents.list[].groupChat.mentionPatterns`. Недійсні шаблони та небезпечні вкладені повторення ігноруються.
- Обмеження за згадками застосовується лише тоді, коли виявлення можливе (нативні згадки або принаймні один шаблон).

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

`messages.groupChat.historyLimit` задає глобальне значення за замовчуванням. Канали можуть перевизначити його через `channels.<channel>.historyLimit` (або для окремого облікового запису). Установіть `0`, щоб вимкнути.

#### Ліміти історії особистих повідомлень

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

Порядок визначення: перевизначення для конкретного DM → значення постачальника за замовчуванням → без обмеження (зберігається все).

Підтримуються: `telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`.

#### Режим self-chat

Додайте власний номер до `allowFrom`, щоб увімкнути режим self-chat (ігнорує нативні @-згадки, відповідає лише на текстові шаблони):

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

### Команди (обробка команд у чаті)

```json5
{
  commands: {
    native: "auto", // реєструвати нативні команди, коли підтримується
    text: true, // розбирати /commands у повідомленнях чату
    bash: false, // дозволити ! (псевдонім: /bash)
    bashForegroundMs: 2000,
    config: false, // дозволити /config
    debug: false, // дозволити /debug
    restart: false, // дозволити /restart + інструмент перезапуску шлюзу
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="Деталі команд">

- Текстові команди мають бути **окремими** повідомленнями з початковим `/`.
- `native: "auto"` вмикає нативні команди для Discord/Telegram, залишає Slack вимкненим.
- Перевизначення для каналу: `channels.discord.commands.native` (bool або `"auto"`). `false` очищає раніше зареєстровані команди.
- `channels.telegram.customCommands` додає додаткові записи в меню бота Telegram.
- `bash: true` вмикає `! <cmd>` для shell хоста. Потрібно `tools.elevated.enabled` і відправник у `tools.elevated.allowFrom.<channel>`.
- `config: true` вмикає `/config` (читання/запис `openclaw.json`). Для клієнтів шлюзу `chat.send` постійні записи `/config set|unset` також вимагають `operator.admin`; режим лише читання `/config show` залишається доступним для звичайних операторських клієнтів із правом запису.
- `channels.<provider>.configWrites` керує мутаціями конфігурації для каналу (за замовчуванням: true).
- Для каналів із багатьма обліковими записами `channels.<provider>.accounts.<id>.configWrites` також керує записами, які стосуються цього облікового запису (наприклад `/allowlist --config --account <id>` або `/config set channels.<provider>.accounts.<id>...`).
- `allowFrom` задається окремо для постачальника. Якщо встановлено, це **єдине** джерело авторизації (списки дозволів/сполучення каналу і `useAccessGroups` ігноруються).
- `useAccessGroups: false` дозволяє командам обходити політики груп доступу, коли `allowFrom` не встановлено.

</Accordion>

---

## Значення агента за замовчуванням

### `agents.defaults.workspace`

За замовчуванням: `~/.openclaw/workspace`.

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

Необов'язковий корінь репозиторію, який показується в рядку Runtime системного prompt-а. Якщо не встановлено, OpenClaw автоматично визначає його, рухаючись угору від workspace.

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
      { id: "writer" }, // успадковує github, weather
      { id: "docs", skills: ["docs-search"] }, // замінює значення за замовчуванням
      { id: "locked-down", skills: [] }, // без Skills
    ],
  },
}
```

- Опустіть `agents.defaults.skills`, щоб за замовчуванням Skills не обмежувалися.
- Опустіть `agents.list[].skills`, щоб успадкувати значення за замовчуванням.
- Установіть `agents.list[].skills: []`, щоб не мати Skills.
- Непорожній список `agents.list[].skills` є фінальним набором для цього агента;
  він не об'єднується зі значеннями за замовчуванням.

### `agents.defaults.skipBootstrap`

Вимикає автоматичне створення bootstrap-файлів workspace (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`).

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.bootstrapMaxChars`

Максимум символів на один bootstrap-файл workspace перед обрізанням. За замовчуванням: `20000`.

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

Максимальна загальна кількість символів, що вставляються з усіх bootstrap-файлів workspace. За замовчуванням: `150000`.

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

Керує текстом попередження, видимим агенту, коли bootstrap-контекст обрізається.
За замовчуванням: `"once"`.

- `"off"`: ніколи не вставляти текст попередження в системний prompt.
- `"once"`: вставляти попередження один раз для кожного унікального підпису обрізання (рекомендовано).
- `"always"`: вставляти попередження на кожному запуску, якщо є обрізання.

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

Максимальний розмір у пікселях для довшої сторони зображення в блоках зображень transcript/tool перед викликами постачальника.
За замовчуванням: `1200`.

Нижчі значення зазвичай зменшують використання vision-токенів і розмір payload запиту для сценаріїв із великою кількістю знімків екрана.
Вищі значення зберігають більше візуальних деталей.

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

Часовий пояс для контексту системного prompt-а (не для часових позначок повідомлень). Якщо не вказано, використовується часовий пояс хоста.

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

Формат часу в системному prompt-і. За замовчуванням: `auto` (налаштування ОС).

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
      params: { cacheRetention: "long" }, // глобальні параметри постачальника за замовчуванням
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
  - Форма рядка задає лише основну модель.
  - Форма об'єкта задає основну модель плюс упорядковані failover-моделі.
- `imageModel`: приймає або рядок (`"provider/model"`), або об'єкт (`{ primary, fallbacks }`).
  - Використовується шляхом інструмента `image` як конфігурація vision-моделі.
  - Також використовується як резервна маршрутизація, коли вибрана/типова модель не може приймати зображення.
- `imageGenerationModel`: приймає або рядок (`"provider/model"`), або об'єкт (`{ primary, fallbacks }`).
  - Використовується спільною можливістю генерації зображень і будь-якою майбутньою поверхнею інструмента/plugin, що генерує зображення.
  - Типові значення: `google/gemini-3.1-flash-image-preview` для нативної генерації зображень Gemini, `fal/fal-ai/flux/dev` для fal або `openai/gpt-image-1` для OpenAI Images.
  - Якщо ви вибираєте конкретно постачальника/модель, також налаштуйте відповідну автентифікацію/API-ключ постачальника (наприклад `GEMINI_API_KEY` або `GOOGLE_API_KEY` для `google/*`, `OPENAI_API_KEY` для `openai/*`, `FAL_KEY` для `fal/*`).
  - Якщо опущено, `image_generate` усе одно може вивести типове значення постачальника з автентифікацією. Спочатку він пробує поточного типового постачальника, потім решту зареєстрованих постачальників генерації зображень у порядку provider-id.
- `videoGenerationModel`: приймає або рядок (`"provider/model"`), або об'єкт (`{ primary, fallbacks }`).
  - Використовується спільною можливістю генерації відео та вбудованим інструментом `video_generate`.
  - Типові значення: `qwen/wan2.6-t2v`, `qwen/wan2.6-i2v`, `qwen/wan2.6-r2v`, `qwen/wan2.6-r2v-flash` або `qwen/wan2.7-r2v`.
  - Якщо опущено, `video_generate` усе одно може вивести типове значення постачальника з автентифікацією. Спочатку він пробує поточного типового постачальника, потім решту зареєстрованих постачальників генерації відео в порядку provider-id.
  - Якщо ви вибираєте конкретно постачальника/модель, також налаштуйте відповідну автентифікацію/API-ключ постачальника.
  - Зараз комплектний постачальник генерації відео Qwen підтримує до 1 вихідного відео, 1 вхідного зображення, 4 вхідних відео, тривалість 10 секунд і параметри рівня постачальника `size`, `aspectRatio`, `resolution`, `audio` та `watermark`.
- `pdfModel`: приймає або рядок (`"provider/model"`), або об'єкт (`{ primary, fallbacks }`).
  - Використовується інструментом `pdf` для маршрутизації моделі.
  - Якщо опущено, інструмент PDF повертається до `imageModel`, а потім до визначеної моделі сесії/типової моделі.
- `pdfMaxBytesMb`: ліміт розміру PDF за замовчуванням для інструмента `pdf`, якщо `maxBytesMb` не передано під час виклику.
- `pdfMaxPages`: максимальна кількість сторінок за замовчуванням, що враховується в режимі резервного витягування інструмента `pdf`.
- `verboseDefault`: типовий рівень verbose для агентів. Значення: `"off"`, `"on"`, `"full"`. За замовчуванням: `"off"`.
- `elevatedDefault`: типовий рівень elevated-output для агентів. Значення: `"off"`, `"on"`, `"ask"`, `"full"`. За замовчуванням: `"on"`.
- `model.primary`: формат `provider/model` (наприклад `openai/gpt-5.4`). Якщо опустити постачальника, OpenClaw спочатку пробує alias, потім унікальний збіг серед налаштованих постачальників для цього exact model id і лише потім повертається до налаштованого типового постачальника (застаріла сумісна поведінка, тож краще явно вказувати `provider/model`). Якщо цей постачальник більше не надає налаштовану типову модель, OpenClaw переходить до першого налаштованого постачальника/моделі замість того, щоб показувати застаріле типове значення від вилученого постачальника.
- `models`: налаштований каталог моделей і список дозволів для `/model`. Кожен запис може містити `alias` (скорочення) і `params` (специфічні для постачальника, наприклад `temperature`, `maxTokens`, `cacheRetention`, `context1m`).
- `params`: глобальні параметри постачальника за замовчуванням, які застосовуються до всіх моделей. Задаються в `agents.defaults.params` (наприклад `{ cacheRetention: "long" }`).
- Порядок злиття `params` (конфігурація): `agents.defaults.params` (глобальна база) перевизначається `agents.defaults.models["provider/model"].params` (для окремої моделі), потім `agents.list[].params` (для відповідного ID агента) перевизначає по ключах. Докладніше див. [Prompt Caching](/uk/reference/prompt-caching).
- Писальники конфігурації, які змінюють ці поля (наприклад `/models set`, `/models set-image` і команди додавання/видалення резервних моделей), зберігають канонічну форму об'єкта та за можливості зберігають наявні списки fallback.
- `maxConcurrent`: максимальна кількість паралельних запусків агентів між сесіями (кожна сесія все одно серіалізується). За замовчуванням: 4.

**Вбудовані скорочені alias-и** (застосовуються лише тоді, коли модель є в `agents.defaults.models`):

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

Ваші налаштовані alias-и завжди мають пріоритет над типовими.

Для моделей Z.AI GLM-4.x автоматично вмикається режим thinking, якщо ви не задасте `--thinking off` або самостійно не визначите `agents.defaults.models["zai/<model>"].params.thinking`.
Моделі Z.AI типово вмикають `tool_stream` для потокової передачі викликів інструментів. Установіть `agents.defaults.models["zai/<model>"].params.tool_stream` у `false`, щоб вимкнути це.
Для моделей Anthropic Claude 4.6 типовим є `adaptive` thinking, коли явний рівень thinking не встановлено.

- Підтримка сесій доступна, коли встановлено `sessionArg`.
- Передача зображень підтримується, коли `imageArg` приймає шляхи до файлів.

### `agents.defaults.heartbeat`

Періодичні запуски heartbeat.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m вимикає
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        lightContext: false, // за замовчуванням: false; true залишає лише HEARTBEAT.md з bootstrap-файлів workspace
        isolatedSession: false, // за замовчуванням: false; true запускає кожен heartbeat у новій сесії (без історії розмови)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (за замовчуванням) | block
        target: "none", // за замовчуванням: none | варіанти: last | whatsapp | telegram | discord | ...
        prompt: "Прочитай HEARTBEAT.md, якщо він існує...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
      },
    },
  },
}
```

- `every`: рядок тривалості (ms/s/m/h). За замовчуванням: `30m` (автентифікація API-ключем) або `1h` (OAuth-автентифікація). Установіть `0m`, щоб вимкнути.
- `suppressToolErrorWarnings`: якщо true, придушує payload-и попереджень про помилки інструментів під час heartbeat.
- `directPolicy`: політика прямої/особистої доставки. `allow` (за замовчуванням) дозволяє доставку на пряму ціль. `block` пригнічує доставку на пряму ціль і видає `reason=dm-blocked`.
- `lightContext`: якщо true, heartbeat використовує полегшений bootstrap-контекст і зберігає лише `HEARTBEAT.md` із bootstrap-файлів workspace.
- `isolatedSession`: якщо true, кожен heartbeat запускається в новій сесії без попередньої історії розмови. Такий самий шаблон ізоляції, як у cron `sessionTarget: "isolated"`. Зменшує вартість токенів на heartbeat приблизно зі 100K до 2–5K токенів.
- Для окремого агента: встановіть `agents.list[].heartbeat`. Якщо будь-який агент визначає `heartbeat`, heartbeat запускаються **лише для цих агентів**.
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
        identifierInstructions: "Точно зберігай deployment ID, ticket ID і пари host:port.", // використовується, коли identifierPolicy=custom
        postCompactionSections: ["Session Startup", "Red Lines"], // [] вимикає повторне вставлення
        model: "openrouter/anthropic/claude-sonnet-4-6", // необов'язкове перевизначення моделі лише для compaction
        notifyUser: true, // надсилати коротке сповіщення, коли починається compaction (за замовчуванням: false)
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "Сесія наближається до compaction. Збережи стійкі спогади зараз.",
          prompt: "Запиши всі довготривалі нотатки в memory/YYYY-MM-DD.md; відповідай точним тихим токеном NO_REPLY, якщо нічого зберігати.",
        },
      },
    },
  },
}
```

- `mode`: `default` або `safeguard` (узагальнення довгих історій частинами). Див. [Compaction](/uk/concepts/compaction).
- `timeoutSeconds`: максимальна кількість секунд для однієї операції compaction, після якої OpenClaw її перериває. За замовчуванням: `900`.
- `identifierPolicy`: `strict` (за замовчуванням), `off` або `custom`. `strict` додає вбудовану інструкцію зі збереження непрозорих ідентифікаторів під час узагальнення compaction.
- `identifierInstructions`: необов'язковий власний текст про збереження ідентифікаторів, який використовується, коли `identifierPolicy=custom`.
- `postCompactionSections`: необов'язкові назви розділів H2/H3 з AGENTS.md, які потрібно повторно вставити після compaction. За замовчуванням `["Session Startup", "Red Lines"]`; установіть `[]`, щоб вимкнути повторне вставлення. Якщо не встановлено або явно встановлено цю типову пару, старіші заголовки `Every Session`/`Safety` теж приймаються як застарілий резервний варіант.
- `model`: необов'язкове перевизначення `provider/model-id` лише для узагальнення compaction. Використовуйте це, коли основна сесія має залишатися на одній моделі, а compaction summaries — виконуватися на іншій; якщо не встановлено, compaction використовує основну модель сесії.
- `notifyUser`: коли `true`, надсилає користувачеві коротке повідомлення, коли починається compaction (наприклад, "Compacting context..."). За замовчуванням вимкнено, щоб compaction була безшумною.
- `memoryFlush`: тихий агентний хід перед auto-compaction для збереження довготривалих спогадів. Пропускається, коли workspace доступний лише для читання.

### `agents.defaults.contextPruning`

Обрізає **старі результати інструментів** з контексту в пам'яті перед надсиланням до LLM. **Не** змінює історію сесії на диску.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // тривалість (ms/s/m/h), одиниця за замовчуванням: хвилини
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Вміст старого результату інструмента очищено]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="Поведінка режиму cache-ttl">

- `mode: "cache-ttl"` вмикає проходи обрізання.
- `ttl` контролює, як часто обрізання може запускатися знову (після останнього торкання кешу).
- Спочатку обрізання м'яко скорочує завеликі результати інструментів, а потім жорстко очищує старіші результати інструментів, якщо потрібно.

**М'яке обрізання** зберігає початок і кінець та вставляє `...` посередині.

**Жорстке очищення** замінює весь результат інструмента на placeholder.

Примітки:

- Блоки зображень ніколи не обрізаються і не очищуються.
- Співвідношення базуються на кількості символів (приблизно), а не на точній кількості токенів.
- Якщо існує менше ніж `keepLastAssistants` повідомлень assistant, обрізання пропускається.

</Accordion>

Докладніше про поведінку див. [Session Pruning](/uk/concepts/session-pruning).

### Блокова потокова передача

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (використовуйте minMs/maxMs)
    },
  },
}
```

- Для каналів, відмінних від Telegram, потрібен явний `*.blockStreaming: true`, щоб увімкнути блокові відповіді.
- Перевизначення для каналу: `channels.<channel>.blockStreamingCoalesce` (і варіанти для окремих облікових записів). Для Signal/Slack/Discord/Google Chat за замовчуванням `minChars: 1500`.
- `humanDelay`: випадкова пауза між блоковими відповідями. `natural` = 800–2500 мс. Перевизначення для окремого агента: `agents.list[].humanDelay`.

Див. [Streaming](/uk/concepts/streaming) для деталей поведінки та розбиття на чанки.

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

- За замовчуванням: `instant` для особистих чатів/згадок, `message` для групових чатів без згадки.
- Перевизначення для сесії: `session.typingMode`, `session.typingIntervalSeconds`.

Див. [Typing Indicators](/uk/concepts/typing-indicators).

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

Необов'язкове sandbox-ізолювання для вбудованого агента. Повний посібник див. у [Sandboxing](/uk/gateway/sandboxing).

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
          // SecretRef / вбудований вміст також підтримуються:
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
- `ssh`: універсальне віддалене середовище виконання на основі SSH
- `openshell`: середовище виконання OpenShell

Коли вибрано `backend: "openshell"`, налаштування, специфічні для середовища виконання, переміщуються до
`plugins.entries.openshell.config`.

**Конфігурація SSH backend:**

- `target`: SSH-ціль у форматі `user@host[:port]`
- `command`: команда SSH-клієнта (за замовчуванням: `ssh`)
- `workspaceRoot`: абсолютний віддалений корінь, який використовується для workspace у межах scope
- `identityFile` / `certificateFile` / `knownHostsFile`: наявні локальні файли, що передаються в OpenSSH
- `identityData` / `certificateData` / `knownHostsData`: вбудований вміст або SecretRef, який OpenClaw матеріалізує в тимчасові файли під час виконання
- `strictHostKeyChecking` / `updateHostKeys`: параметри політики ключів хоста OpenSSH

**Пріоритет автентифікації SSH:**

- `identityData` має пріоритет над `identityFile`
- `certificateData` має пріоритет над `certificateFile`
- `knownHostsData` має пріоритет над `knownHostsFile`
- Значення `*Data`, підкріплені SecretRef, визначаються з активного знімка secrets runtime перед початком sandbox-сесії

**Поведінка SSH backend:**

- один раз ініціалізує віддалений workspace після створення або повторного створення
- потім зберігає віддалений SSH-workspace як канонічний
- маршрутизує `exec`, файлові інструменти та шляхи медіа через SSH
- не синхронізує автоматично віддалені зміни назад на хост
- не підтримує браузерні контейнери sandbox

**Доступ до workspace:**

- `none`: workspace sandbox у межах scope під `~/.openclaw/sandboxes`
- `ro`: workspace sandbox у `/workspace`, workspace агента монтується лише для читання в `/agent`
- `rw`: workspace агента монтується для читання/запису в `/workspace`

**Scope:**

- `session`: контейнер + workspace для кожної сесії
- `agent`: один контейнер + workspace на агента (за замовчуванням)
- `shared`: спільний контейнер і workspace (без ізоляції між сесіями)

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
          gateway: "lab", // необов'язково
          gatewayEndpoint: "https://lab.example", // необов'язково
          policy: "strict", // необов'язковий ID політики OpenShell
          providers: ["openai"], // необов'язково
          autoProviders: true,
          timeoutSeconds: 120,
        },
      },
    },
  },
}
```

**Режим OpenShell:**

- `mirror`: перед `exec` ініціалізувати віддалене середовище з локального, після `exec` синхронізувати назад; локальний workspace залишається канонічним
- `remote`: один раз ініціалізувати віддалене середовище при створенні sandbox, потім зберігати віддалений workspace як канонічний

У режимі `remote` редагування на локальному хості, виконані поза OpenClaw, не синхронізуються в sandbox автоматично після кроку ініціалізації.
Транспортом є SSH до sandbox OpenShell, але plugin володіє життєвим циклом sandbox і необов'язковою синхронізацією mirror.

**`setupCommand`** запускається один раз після створення контейнера (через `sh -lc`). Потрібні мережевий вихід, записуваний root і root-користувач.

**Для контейнерів типовим є `network: "none"`** — установіть `"bridge"` (або власну bridge-мережу), якщо агенту потрібен вихід назовні.
`"host"` блокується. `"container:<id>"` блокується за замовчуванням, якщо ви явно не встановите
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` (break-glass).

**Вхідні вкладення** тимчасово розміщуються в `media/inbound/*` активного workspace.

**`docker.binds`** монтує додаткові каталоги хоста; глобальні binds і binds для окремого агента об'єднуються.

**Браузер у sandbox** (`sandbox.browser.enabled`): Chromium + CDP у контейнері. URL noVNC вставляється в системний prompt. Не потребує `browser.enabled` у `openclaw.json`.
Доступ спостерігача до noVNC за замовчуванням використовує автентифікацію VNC, і OpenClaw видає короткоживучий token URL (замість того, щоб розкривати пароль у спільному URL).

- `allowHostControl: false` (за замовчуванням) блокує сесіям у sandbox націлювання на браузер хоста.
- `network` за замовчуванням дорівнює `openclaw-sandbox-browser` (виділена bridge-мережа). Установлюйте `bridge` лише тоді, коли вам явно потрібне глобальне bridge-з'єднання.
- `cdpSourceRange` за бажанням обмежує вхід CDP на межі контейнера до діапазону CIDR (наприклад `172.21.0.1/32`).
- `sandbox.browser.binds` монтує додаткові каталоги хоста лише в контейнер браузера sandbox. Якщо встановлено (включно з `[]`), замінює `docker.binds` для контейнера браузера.
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
  - `--disable-extensions` (типово увімкнено)
  - `--disable-3d-apis`, `--disable-software-rasterizer` і `--disable-gpu`
    типово увімкнено, і їх можна вимкнути через
    `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`, якщо для WebGL/3D це потрібно.
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` знову вмикає розширення, якщо ваш робочий процес
    залежить від них.
  - `--renderer-process-limit=2` можна змінити через
    `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`; установіть `0`, щоб використовувати
    типове обмеження процесів Chromium.
  - плюс `--no-sandbox` і `--disable-setuid-sandbox`, коли увімкнено `noSandbox`.
  - Значення за замовчуванням є базовими для образу контейнера; використовуйте власний образ браузера з власним
    entrypoint, щоб змінити типові значення контейнера.

</Accordion>

Browser sandboxing і `sandbox.docker.binds` зараз підтримуються лише для Docker.

Збірка образів:

```bash
scripts/sandbox-setup.sh           # основний образ sandbox
scripts/sandbox-browser-setup.sh   # необов'язковий образ браузера
```

### `agents.list` (перевизначення для окремого агента)

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Головний агент",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6", // або { primary, fallbacks }
        thinkingDefault: "high", // перевизначення рівня thinking для окремого агента
        reasoningDefault: "on", // перевизначення видимості reasoning для окремого агента
        fastModeDefault: false, // перевизначення fast mode для окремого агента
        params: { cacheRetention: "none" }, // перевизначає matching defaults.models params за ключем
        skills: ["docs-search"], // замінює agents.defaults.skills, якщо задано
        identity: {
          name: "Samantha",
          theme: "корисливий лінивець",
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
- `default`: якщо встановлено в кількох місцях, перший перемагає (логуються попередження). Якщо не встановлено ніде, типовим стає перший запис у списку.
- `model`: форма рядка перевизначає лише `primary`; форма об'єкта `{ primary, fallbacks }` перевизначає обидва (`[]` вимикає глобальні fallback-и). Cron jobs, які перевизначають лише `primary`, усе одно успадковують типові fallback-и, якщо ви не встановите `fallbacks: []`.
- `params`: параметри потоку для окремого агента, злиті поверх вибраного запису моделі в `agents.defaults.models`. Використовуйте це для перевизначень, специфічних для агента, як-от `cacheRetention`, `temperature` або `maxTokens`, не дублюючи весь каталог моделей.
- `skills`: необов'язковий список дозволених Skills для окремого агента. Якщо опущено, агент успадковує `agents.defaults.skills`, якщо його встановлено; явний список замінює типові значення замість злиття, а `[]` означає відсутність Skills.
- `thinkingDefault`: необов'язковий типовий рівень thinking для окремого агента (`off | minimal | low | medium | high | xhigh | adaptive`). Перевизначає `agents.defaults.thinkingDefault` для цього агента, якщо не встановлено перевизначення для повідомлення або сесії.
- `reasoningDefault`: необов'язкове типове значення видимості reasoning для окремого агента (`on | off | stream`). Застосовується, якщо не встановлено перевизначення reasoning для повідомлення або сесії.
- `fastModeDefault`: необов'язкове типове значення fast mode для окремого агента (`true | false`). Застосовується, якщо не встановлено перевизначення fast-mode для повідомлення або сесії.
- `runtime`: необов'язковий дескриптор середовища виконання для окремого агента. Використовуйте `type: "acp"` із типовими значеннями `runtime.acp` (`agent`, `backend`, `mode`, `cwd`), коли агент має за замовчуванням працювати в ACP harness sessions.
- `identity.avatar`: шлях відносно workspace, URL `http(s)` або URI `data:`.
- `identity` виводить типові значення: `ackReaction` з `emoji`, `mentionPatterns` з `name`/`emoji`.
- `subagents.allowAgents`: список дозволених ID агентів для `sessions_spawn` (`["*"]` = будь-який; за замовчуванням: лише той самий агент).
- Захист успадкування sandbox: якщо сесія ініціатора працює в sandbox, `sessions_spawn` відхиляє цілі, які запускалися б без sandbox.
- `subagents.requireAgentId`: якщо true, блокує виклики `sessions_spawn`, які не містять `agentId` (вимагає явного вибору профілю; за замовчуванням: false).

---

## Маршрутизація між агентами

Запускайте кілька ізольованих агентів в одному Gateway. Див. [Multi-Agent](/uk/concepts/multi-agent).

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

### Поля збігу прив'язок

- `type` (необов'язково): `route` для звичайної маршрутизації (відсутній `type` за замовчуванням означає route), `acp` для постійних ACP-прив'язок розмов.
- `match.channel` (обов'язково)
- `match.accountId` (необов'язково; `*` = будь-який обліковий запис; якщо опущено = обліковий запис за замовчуванням)
- `match.peer` (необов'язково; `{ kind: direct|group|channel, id }`)
- `match.guildId` / `match.teamId` (необов'язково; залежить від каналу)
- `acp` (необов'язково; лише для `type: "acp"`): `{ mode, label, cwd, backend }`

**Детермінований порядок збігів:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId` (точний, без peer/guild/team)
5. `match.accountId: "*"` (у межах каналу)
6. Агент за замовчуванням

У межах кожного рівня перемагає перший відповідний запис у `bindings`.

Для записів `type: "acp"` OpenClaw визначає відповідність за точною ідентичністю розмови (`match.channel` + account + `match.peer.id`) і не використовує наведений вище порядок рівнів route-прив'язок.

### Профілі доступу для окремих агентів

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

<Accordion title="Інструменти та workspace лише для читання">

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

<Accordion title="Без доступу до файлової системи (лише повідомлення)">

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

Докладніше про пріоритети див. [Multi-Agent Sandbox & Tools](/uk/tools/multi-agent-sandbox-tools).

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
    parentForkMaxTokens: 100000, // пропустити форк батьківського потоку вище цього ліміту токенів (0 вимикає)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // тривалість або false
      maxDiskBytes: "500mb", // необов'язковий жорсткий бюджет
      highWaterBytes: "400mb", // необов'язкова ціль очищення
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // типове авто-скасування фокусу через неактивність у годинах (`0` вимикає)
      maxAgeHours: 0, // типовий жорсткий максимальний вік у годинах (`0` вимикає)
    },
    mainKey: "main", // застаріле (runtime завжди використовує "main")
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="Деталі полів session">

- **`scope`**: базова стратегія групування сесій для контекстів групових чатів.
  - `per-sender` (за замовчуванням): кожен відправник отримує ізольовану сесію в межах контексту каналу.
  - `global`: усі учасники в контексті каналу ділять одну спільну сесію (використовуйте лише тоді, коли спільний контекст дійсно потрібний).
- **`dmScope`**: як групуються особисті повідомлення.
  - `main`: усі особисті повідомлення ділять основну сесію.
  - `per-peer`: ізоляція за ID відправника між каналами.
  - `per-channel-peer`: ізоляція за каналом + відправником (рекомендовано для inbox із багатьма користувачами).
  - `per-account-channel-peer`: ізоляція за обліковим записом + каналом + відправником (рекомендовано для багатьох облікових записів).
- **`identityLinks`**: зіставлення канонічних ID із peer-ами з префіксом постачальника для спільного використання сесій між каналами.
- **`reset`**: основна політика скидання. `daily` скидає о `atHour` за місцевим часом; `idle` скидає після `idleMinutes`. Якщо налаштовано обидва, спрацьовує те, що закінчиться раніше.
- **`resetByType`**: перевизначення за типом (`direct`, `group`, `thread`). Застарілий `dm` приймається як alias для `direct`.
- **`parentForkMaxTokens`**: максимальне `totalTokens` батьківської сесії, дозволене при створенні сесії форкнутого потоку (за замовчуванням `100000`).
  - Якщо батьківське `totalTokens` перевищує це значення, OpenClaw починає нову сесію потоку замість успадкування історії транскрипту батьківської сесії.
  - Установіть `0`, щоб вимкнути цей захист і завжди дозволяти форк батьківської сесії.
- **`mainKey`**: застаріле поле. Runtime тепер завжди використовує `"main"` для основного кошика особистих чатів.
- **`agentToAgent.maxPingPongTurns`**: максимальна кількість відповідей назад між агентами під час обміну агент-до-агента (ціле число, діапазон: `0`–`5`). `0` вимикає ланцюжки ping-pong.
- **`sendPolicy`**: збіг за `channel`, `chatType` (`direct|group|channel`, із застарілим alias `dm`), `keyPrefix` або `rawKeyPrefix`. Перший deny перемагає.
- **`maintenance`**: очищення сховища сесій + елементи керування збереженням.
  - `mode`: `warn` лише видає попередження; `enforce` застосовує очищення.
  - `pruneAfter`: віковий поріг для застарілих записів (за замовчуванням `30d`).
  - `maxEntries`: максимальна кількість записів у `sessions.json` (за замовчуванням `500`).
  - `rotateBytes`: ротація `sessions.json`, коли його розмір перевищує це значення (за замовчуванням `10mb`).
  - `resetArchiveRetention`: час збереження архівів транскриптів `*.reset.<timestamp>`. За замовчуванням дорівнює `pruneAfter`; установіть `false`, щоб вимкнути.
  - `maxDiskBytes`: необов'язковий бюджет диска для каталогу сесій. У режимі `warn` лише логує попередження; у режимі `enforce` спочатку видаляє найстаріші артефакти/сесії.
  - `highWaterBytes`: необов'язкова ціль після очищення за бюджетом. За замовчуванням `80%` від `maxDiskBytes`.
- **`threadBindings`**: глобальні типові значення для функцій сесій, прив'язаних до потоків.
  - `enabled`: головний перемикач за замовчуванням (постачальники можуть перевизначати; Discord використовує `channels.discord.threadBindings.enabled`)
  - `idleHours`: типове авто-скасування фокусу через неактивність у годинах (`0` вимикає; постачальники можуть перевизначати)
  - `maxAgeHours`: типовий жорсткий максимальний вік у годинах (`0` вимикає; постачальники можуть перевизначати)

</Accordion>

---

## Messages

```json5
{
  messages: {
    responsePrefix: "🦞", // або "auto"
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
      debounceMs: 2000, // 0 вимикає
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

Порядок визначення (найспецифічніше перемагає): account → channel → global. `""` вимикає та зупиняє каскад. `"auto"` виводиться як `[{identity.name}]`.

**Змінні шаблону:**

| Змінна           | Опис                    | Приклад                     |
| ---------------- | ----------------------- | --------------------------- |
| `{model}`        | Коротка назва моделі    | `claude-opus-4-6`           |
| `{modelFull}`    | Повний ідентифікатор моделі | `anthropic/claude-opus-4-6` |
| `{provider}`     | Назва постачальника     | `anthropic`                 |
| `{thinkingLevel}`| Поточний рівень thinking | `high`, `low`, `off`        |
| `{identity.name}`| Ім'я identity агента    | (те саме, що `"auto"`)      |

Змінні нечутливі до регістру. `{think}` — alias для `{thinkingLevel}`.

### Ack reaction

- За замовчуванням дорівнює `identity.emoji` активного агента, інакше `"👀"`. Установіть `""`, щоб вимкнути.
- Перевизначення для каналу: `channels.<channel>.ackReaction`, `channels.<channel>.accounts.<id>.ackReaction`.
- Порядок визначення: account → channel → `messages.ackReaction` → fallback від identity.
- Scope: `group-mentions` (за замовчуванням), `group-all`, `direct`, `all`.
- `removeAckAfterReply`: прибирає ack після відповіді в Slack, Discord і Telegram.
- `messages.statusReactions.enabled`: вмикає реакції статусу життєвого циклу в Slack, Discord і Telegram.
  У Slack і Discord відсутнє значення зберігає реакції статусу увімкненими, коли активні ack reactions.
  У Telegram встановіть його явно в `true`, щоб увімкнути реакції статусу життєвого циклу.

### Inbound debounce

Об'єднує швидкі текстові повідомлення від того самого відправника в один хід агента. Медіа/вкладення скидають буфер одразу. Керівні команди обходять debounce.

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

- `auto` керує auto-TTS. `/tts off|always|inbound|tagged` перевизначає це для сесії.
- `summaryModel` перевизначає `agents.defaults.model.primary` для auto-summary.
- `modelOverrides` увімкнено за замовчуванням; `modelOverrides.allowProvider` за замовчуванням дорівнює `false` (opt-in).
- API-ключі використовують резервні значення `ELEVENLABS_API_KEY`/`XI_API_KEY` і `OPENAI_API_KEY`.
- `openai.baseUrl` перевизначає endpoint OpenAI TTS. Порядок визначення: конфігурація, потім `OPENAI_TTS_BASE_URL`, потім `https://api.openai.com/v1`.
- Коли `openai.baseUrl` вказує на endpoint, відмінний від OpenAI, OpenClaw трактує його як OpenAI-сумісний TTS-сервер і послаблює перевірку моделі/голосу.

---

## Talk

Типові значення для режиму Talk (macOS/iOS/Android).

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

- `talk.provider` має відповідати ключу в `talk.providers`, коли налаштовано кілька постачальників Talk.
- Застарілі плоскі ключі Talk (`talk.voiceId`, `talk.voiceAliases`, `talk.modelId`, `talk.outputFormat`, `talk.apiKey`) сумісні лише для сумісності та автоматично переносяться в `talk.providers.<provider>`.
- Voice ID використовують резервні значення `ELEVENLABS_VOICE_ID` або `SAG_VOICE_ID`.
- `providers.*.apiKey` приймає прості текстові рядки або об'єкти SecretRef.
- Резервне значення `ELEVENLABS_API_KEY` застосовується лише тоді, коли API-ключ Talk не налаштовано.
- `providers.*.voiceAliases` дозволяє директивам Talk використовувати дружні імена.
- `silenceTimeoutMs` керує тим, скільки Talk mode чекає після тиші користувача перед надсиланням транскрипту. Якщо не встановлено, зберігається типове вікно паузи платформи (`700 мс на macOS і Android, 900 мс на iOS`).

---

## Інструменти

### Профілі інструментів

`tools.profile` задає базовий список дозволів перед `tools.allow`/`tools.deny`:

Локальний онбординг за замовчуванням встановлює новим локальним конфігураціям `tools.profile: "coding"`, якщо значення не задано (наявні явні профілі зберігаються).

| Профіль      | Включає                                                                                                                        |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `minimal`    | лише `session_status`                                                                                                           |
| `coding`     | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging`  | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                       |
| `full`       | Без обмежень (те саме, що не встановлено)                                                                                       |

### Групи інструментів

| Група              | Інструменти                                                                                                            |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec`, `process`, `code_execution` (`bash` приймається як alias для `exec`)                                          |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                                                 |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory`     | `memory_search`, `memory_get`                                                                                          |
| `group:web`        | `web_search`, `x_search`, `web_fetch`                                                                                  |
| `group:ui`         | `browser`, `canvas`                                                                                                    |
| `group:automation` | `cron`, `gateway`                                                                                                      |
| `group:messaging`  | `message`                                                                                                              |
| `group:nodes`      | `nodes`                                                                                                                |
| `group:agents`     | `agents_list`                                                                                                          |
| `group:media`      | `image`, `image_generate`, `video_generate`, `tts`                                                                     |
| `group:openclaw`   | Усі вбудовані інструменти (без provider plugins)                                                                       |

### `tools.allow` / `tools.deny`

Глобальна політика allow/deny для інструментів (deny перемагає). Нечутлива до регістру, підтримує wildcard-и `*`. Застосовується навіть тоді, коли Docker sandbox вимкнений.

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

Додатково обмежує інструменти для певних постачальників або моделей. Порядок: базовий профіль → профіль постачальника → allow/deny.

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
- `/elevated on|off|ask|full` зберігає стан для кожної сесії; вбудовані директиви застосовуються лише до одного повідомлення.
- Elevated `exec` обходить sandbox і використовує налаштований шлях виходу (`gateway` за замовчуванням або `node`, коли ціль exec — `node`).

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

Перевірки безпеки для циклів інструментів **типово вимкнені**. Установіть `enabled: true`, щоб увімкнути виявлення.
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

- `historySize`: максимальний обсяг історії викликів інструментів, що зберігається для аналізу циклів.
- `warningThreshold`: поріг повторюваного шаблону без прогресу для попереджень.
- `criticalThreshold`: вищий поріг повторення для блокування критичних циклів.
- `globalCircuitBreakerThreshold`: жорсткий поріг зупинки для будь-якого запуску без прогресу.
- `detectors.genericRepeat`: попереджати про повторні виклики того самого інструмента з тими самими аргументами.
- `detectors.knownPollNoProgress`: попереджати/блокувати відомі poll-інструменти (`process.poll`, `command_status` тощо).
- `detectors.pingPong`: попереджати/блокувати чергування пар без прогресу.
- Якщо `warningThreshold >= criticalThreshold` або `criticalThreshold >= globalCircuitBreakerThreshold`, перевірка не проходить.

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // або BRAVE_API_KEY з env
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // необов'язково; опустіть для auto-detect
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

Налаштовує розуміння вхідних медіа (зображення/аудіо/відео):

```json5
{
  tools: {
    media: {
      concurrency: 2,
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

<Accordion title="Поля запису моделі медіа">

**Запис постачальника** (`type: "provider"` або опущено):

- `provider`: ID API-постачальника (`openai`, `anthropic`, `google`/`gemini`, `groq` тощо)
- `model`: перевизначення ID моделі
- `profile` / `preferredProfile`: вибір профілю `auth-profiles.json`

**CLI-запис** (`type: "cli"`):

- `command`: виконуваний файл
- `args`: шаблонізовані аргументи (підтримуються `{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}` тощо)

**Спільні поля:**

- `capabilities`: необов'язковий список (`image`, `audio`, `video`). За замовчуванням: `openai`/`anthropic`/`minimax` → image, `google` → image+audio+video, `groq` → audio.
- `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`: перевизначення для окремого запису.
- У разі помилки використовується наступний запис.

Автентифікація постачальника йде стандартним порядком: `auth-profiles.json` → env vars → `models.providers.*.apiKey`.

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

Керує тим, які сесії можна вибирати через session tools (`sessions_list`, `sessions_history`, `sessions_send`).

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

- `self`: лише поточний ключ сесії.
- `tree`: поточна сесія + сесії, породжені поточною сесією (subagents).
- `agent`: будь-яка сесія, що належить поточному ID агента (може включати інших користувачів, якщо ви використовуєте per-sender sessions під одним ID агента).
- `all`: будь-яка сесія. Для націлювання між агентами все ще потрібен `tools.agentToAgent`.
- Притискання sandbox: коли поточна сесія працює в sandbox і `agents.defaults.sandbox.sessionToolsVisibility="spawned"`, видимість примусово встановлюється в `tree`, навіть якщо `tools.sessions.visibility="all"`.

### `tools.sessions_spawn`

Керує підтримкою вбудованих вкладень для `sessions_spawn`.

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // opt-in: установіть true, щоб дозволити вбудовані файлові вкладення
        maxTotalBytes: 5242880, // 5 МБ сумарно для всіх файлів
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 МБ на файл
        retainOnSessionKeep: false, // зберігати вкладення, коли cleanup="keep"
      },
    },
  },
}
```

Примітки:

- Вкладення підтримуються лише для `runtime: "subagent"`. ACP runtime їх відхиляє.
- Файли матеріалізуються в дочірньому workspace у `.openclaw/attachments/<uuid>/` з `.manifest.json`.
- Вміст вкладень автоматично редагується під час збереження transcript.
- Входи Base64 перевіряються за строгими правилами алфавіту/вирівнювання та попереднім захистом розміру до декодування.
- Права файлів: `0700` для каталогів і `0600` для файлів.
- Очищення слідує політиці `cleanup`: `delete` завжди видаляє вкладення; `keep` зберігає їх лише тоді, коли `retainOnSessionKeep: true`.

### `tools.experimental`

Експериментальні прапори вбудованих інструментів. Типово вимкнені, якщо не застосовується правило auto-enable, специфічне для runtime.

```json5
{
  tools: {
    experimental: {
      planTool: true, // увімкнути експериментальний update_plan
    },
  },
}
```

Примітки:

- `planTool`: вмикає структурований інструмент `update_plan` для відстеження нетривіальної багатокрокової роботи.
- За замовчуванням: `false` для постачальників, відмінних від OpenAI. OpenAI і OpenAI Codex автоматично вмикають його.
- Коли він увімкнений, системний prompt також додає інструкції щодо використання, щоб модель застосовувала його лише для суттєвої роботи й підтримувала не більше одного кроку `in_progress`.

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

- `model`: типова модель для породжених sub-agent. Якщо не вказано, sub-agent успадковують модель викликача.
- `allowAgents`: типовий список дозволених ID цільових агентів для `sessions_spawn`, коли агент-запитувач не задає власний `subagents.allowAgents` (`["*"]` = будь-який; за замовчуванням: лише той самий агент).
- `runTimeoutSeconds`: типовий тайм-аут (секунди) для `sessions_spawn`, коли виклик інструмента не передає `runTimeoutSeconds`. `0` означає без тайм-ауту.
- Політика інструментів для subagent: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.

---

## Власні постачальники та base URL

OpenClaw використовує вбудований каталог моделей. Додавайте власних постачальників через `models.providers` у конфігурації або `~/.openclaw/agents/<agentId>/agent/models.json`.

```json5
{
  models: {
    mode: "merge", // merge (за замовчуванням) | replace
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

- Використовуйте `authHeader: true` + `headers` для нестандартних потреб автентифікації.
- Перевизначайте корінь конфігурації агента через `OPENCLAW_AGENT_DIR` (або `PI_CODING_AGENT_DIR`, застарілий alias env variable).
- Пріоритет злиття для відповідних ID постачальників:
  - Непорожні значення `baseUrl` в `models.json` агента мають пріоритет.
  - Непорожні значення `apiKey` агента мають пріоритет лише тоді, коли цей постачальник не керується через SecretRef у поточному контексті config/auth-profile.
  - Значення `apiKey` постачальника, керовані через SecretRef, оновлюються з маркерів джерела (`ENV_VAR_NAME` для env refs, `secretref-managed` для file/exec refs) замість збереження визначених секретів.
  - Значення заголовків постачальника, керовані через SecretRef, оновлюються з маркерів джерела (`secretref-env:ENV_VAR_NAME` для env refs, `secretref-managed` для file/exec refs).
  - Порожні або відсутні `apiKey`/`baseUrl` агента повертаються до `models.providers` у конфігурації.
  - Для відповідних моделей `contextWindow`/`maxTokens` використовують більше значення між явною конфігурацією та неявними значеннями каталогу.
  - Для відповідних моделей `contextTokens` зберігає явний runtime cap, якщо він заданий; використовуйте це, щоб обмежити ефективний контекст без зміни нативних метаданих моделі.
  - Використовуйте `models.mode: "replace"`, коли хочете, щоб конфігурація повністю переписала `models.json`.
  - Збереження маркерів визначається джерелом: маркери записуються з активного знімка конфігурації джерела (до визначення), а не з визначених секретних значень середовища виконання.

### Деталі полів постачальника

- `models.mode`: поведінка каталогу постачальників (`merge` або `replace`).
- `models.providers`: карта власних постачальників, ключем якої є ID постачальника.
- `models.providers.*.api`: адаптер запитів (`openai-completions`, `openai-responses`, `anthropic-messages`, `google-generative-ai` тощо).
- `models.providers.*.apiKey`: облікові дані постачальника (краще через SecretRef/env substitution).
- `models.providers.*.auth`: стратегія автентифікації (`api-key`, `token`, `oauth`, `aws-sdk`).
- `models.providers.*.injectNumCtxForOpenAICompat`: для Ollama + `openai-completions` вставляє `options.num_ctx` у запити (за замовчуванням: `true`).
- `models.providers.*.authHeader`: примусово передавати облікові дані в заголовку `Authorization`, коли це потрібно.
- `models.providers.*.baseUrl`: базовий URL API upstream.
- `models.providers.*.headers`: додаткові статичні заголовки для proxy/tenant routing.
- `models.providers.*.request`: транспортні перевизначення для HTTP-запитів model-provider.
  - `request.headers`: додаткові заголовки (зливаються з типовими значеннями постачальника). Значення приймають SecretRef.
  - `request.auth`: перевизначення стратегії автентифікації. Режими: `"provider-default"` (використовувати вбудовану автентифікацію постачальника), `"authorization-bearer"` (з `token`), `"header"` (з `headerName`, `value`, необов'язковим `prefix`).
  - `request.proxy`: перевизначення HTTP-проксі. Режими: `"env-proxy"` (використовувати env vars `HTTP_PROXY`/`HTTPS_PROXY`), `"explicit-proxy"` (з `url`). Обидва режими приймають необов'язковий підоб'єкт `tls`.
  - `request.tls`: перевизначення TLS для прямих з'єднань. Поля: `ca`, `cert`, `key`, `passphrase` (усі приймають SecretRef), `serverName`, `insecureSkipVerify`.
- `models.providers.*.models`: явні записи каталогу моделей постачальника.
- `models.providers.*.models.*.contextWindow`: метадані нативного контекстного вікна моделі.
- `models.providers.*.models.*.contextTokens`: необов'язковий runtime cap для контексту. Використовуйте, якщо вам потрібен менший ефективний бюджет контексту, ніж нативне `contextWindow` моделі.
- `models.providers.*.models.*.compat.supportsDeveloperRole`: необов'язкова підказка сумісності. Для `api: "openai-completions"` з непорожнім ненативним `baseUrl` (хост не `api.openai.com`) OpenClaw примусово встановлює це значення в `false` під час виконання. Порожній/відсутній `baseUrl` зберігає типову поведінку OpenAI.
- `plugins.entries.amazon-bedrock.config.discovery`: корінь налаштувань auto-discovery для Bedrock.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: увімкнути/вимкнути неявне виявлення.
- `plugins.entries.amazon-bedrock.config.discovery.region`: регіон AWS для виявлення.
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: необов'язковий фільтр provider-id для цільового виявлення.
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: інтервал опитування для оновлення виявлення.
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: резервне контекстне вікно для виявлених моделей.
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

Використовуйте `cerebras/zai-glm-4.7` для Cerebras; `zai/glm-4.7` для прямого Z.AI.

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

Установіть `ZAI_API_KEY`. `z.ai/*` і `z-ai/*` приймаються як alias-и. Скорочення: `openclaw onboard --auth-choice zai-api-key`.

- Загальний endpoint: `https://api.z.ai/api/paas/v4`
- Endpoint для кодування (за замовчуванням): `https://api.z.ai/api/coding/paas/v4`
- Для загального endpoint визначте власного постачальника з перевизначенням base URL.

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

Для китайського endpoint: `baseUrl: "https://api.moonshot.cn/v1"` або `openclaw onboard --auth-choice moonshot-api-key-cn`.

Нативні endpoints Moonshot рекламують сумісність використання streaming на спільному
транспорті `openai-completions`, і OpenClaw тепер визначає це за можливостями endpoint-а,
а не лише за вбудованим provider id.

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

Anthropic-сумісний, вбудований постачальник. Скорочення: `openclaw onboard --auth-choice kimi-code-api-key`.

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
На Anthropic-сумісному шляху streaming OpenClaw типово вимикає thinking MiniMax,
якщо ви явно самі не встановите `thinking`. `/fast on` або
`params.fastMode: true` переписує `MiniMax-M2.7` на
`MiniMax-M2.7-highspeed`.

</Accordion>

<Accordion title="Локальні моделі (LM Studio)">

Див. [Local Models](/uk/gateway/local-models). Коротко: запускайте велику локальну модель через LM Studio Responses API на серйозному обладнанні; залишайте хостовані моделі об'єднаними як резервний варіант.

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
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // або простий текстовий рядок
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: необов'язковий список дозволених лише для комплектних Skills (керовані/workspace Skills не зачіпаються).
- `load.extraDirs`: додаткові спільні корені Skills (найнижчий пріоритет).
- `install.preferBrew`: якщо true, надавати перевагу інсталяторам Homebrew, коли
  `brew` доступний, перед переходом до інших типів інсталяторів.
- `install.nodeManager`: пріоритет Node-інсталятора для специфікацій `metadata.openclaw.install`
  (`npm` | `pnpm` | `yarn` | `bun`).
- `entries.<skillKey>.enabled: false` вимикає Skill, навіть якщо він комплектний/встановлений.
- `entries.<skillKey>.apiKey`: зручне поле API-ключа для Skills, що оголошують основну env variable (простий текстовий рядок або об'єкт SecretRef).

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
- Виявлення приймає нативні plugins OpenClaw, а також сумісні пакети Codex і Claude, включно з пакетами Claude стандартного макета без manifest.
- **З