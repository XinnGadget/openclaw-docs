---
read_when:
    - Робота над функціями каналу Discord
summary: Статус підтримки Discord бота, можливості та конфігурація
title: Discord
x-i18n:
    generated_at: "2026-04-05T20:19:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7fc471394b4fd2384779487f7ea5249897e826d2964094c0780613f3aea13946
    source_path: channels/discord.md
    workflow: 15
---

# Discord (Bot API)

Статус: готовий для приватних повідомлень і каналів сервера через офіційний шлюз Discord.

<CardGroup cols={3}>
  <Card title="Підключення" icon="link" href="/uk/channels/pairing">
    Для Discord DM за замовчуванням використовується режим підключення.
  </Card>
  <Card title="Слеш-команди" icon="terminal" href="/uk/tools/slash-commands">
    Власна поведінка команд і каталог команд.
  </Card>
  <Card title="Усунення проблем із каналом" icon="wrench" href="/uk/channels/troubleshooting">
    Діагностика між каналами та процес відновлення.
  </Card>
</CardGroup>

## Швидке налаштування

Вам потрібно створити новий застосунок із ботом, додати бота на свій сервер і підключити його до OpenClaw. Ми рекомендуємо додати бота на власний приватний сервер. Якщо у вас його ще немає, [спочатку створіть сервер](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server) (виберіть **Create My Own > For me and my friends**).

<Steps>
  <Step title="Створіть застосунок Discord і бота">
    Перейдіть до [Discord Developer Portal](https://discord.com/developers/applications) і натисніть **New Application**. Назвіть його, наприклад, "OpenClaw".

    На бічній панелі натисніть **Bot**. У полі **Username** вкажіть назву вашого агента OpenClaw.

  </Step>

  <Step title="Увімкніть привілейовані intents">
    На сторінці **Bot** прокрутіть до розділу **Privileged Gateway Intents** і увімкніть:

    - **Message Content Intent** (обов’язково)
    - **Server Members Intent** (рекомендовано; потрібно для allowlist ролей і зіставлення імен з ID)
    - **Presence Intent** (необов’язково; потрібне лише для оновлень присутності)

  </Step>

  <Step title="Скопіюйте токен бота">
    Прокрутіть угору на сторінці **Bot** і натисніть **Reset Token**.

    <Note>
    Попри назву, це створює ваш перший токен — нічого насправді не "скидається".
    </Note>

    Скопіюйте токен і збережіть його десь. Це ваш **Bot Token**, і він знадобиться вам за мить.

  </Step>

  <Step title="Згенеруйте URL-запрошення і додайте бота на свій сервер">
    На бічній панелі натисніть **OAuth2**. Ви згенеруєте URL-запрошення з правильними дозволами, щоб додати бота на свій сервер.

    Прокрутіть до **OAuth2 URL Generator** і увімкніть:

    - `bot`
    - `applications.commands`

    Нижче з’явиться розділ **Bot Permissions**. Увімкніть:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (необов’язково)

    Скопіюйте згенерований URL унизу, вставте його в браузер, виберіть свій сервер і натисніть **Continue**, щоб підключити. Тепер ви маєте побачити свого бота на Discord-сервері.

  </Step>

  <Step title="Увімкніть Developer Mode і зберіть свої ID">
    Повернувшись до застосунку Discord, вам потрібно ввімкнути Developer Mode, щоб можна було копіювати внутрішні ID.

    1. Натисніть **User Settings** (іконка шестерні поруч із вашим аватаром) → **Advanced** → увімкніть **Developer Mode**
    2. Натисніть правою кнопкою миші на **іконці сервера** на бічній панелі → **Copy Server ID**
    3. Натисніть правою кнопкою миші на **своєму аватарі** → **Copy User ID**

    Збережіть свої **Server ID** і **User ID** разом із Bot Token — на наступному кроці ви передасте всі три значення до OpenClaw.

  </Step>

  <Step title="Дозвольте DM від учасників сервера">
    Щоб підключення працювало, Discord має дозволяти вашому боту надсилати вам DM. Натисніть правою кнопкою миші на **іконці сервера** → **Privacy Settings** → увімкніть **Direct Messages**.

    Це дозволяє учасникам сервера (включно з ботами) надсилати вам DM. Залиште цю опцію увімкненою, якщо хочете використовувати Discord DM з OpenClaw. Якщо ви плануєте використовувати лише канали сервера, після підключення DM можна вимкнути.

  </Step>

  <Step title="Безпечно задайте токен бота (не надсилайте його в чат)">
    Токен вашого Discord бота — це секрет (як пароль). Задайте його на машині, де працює OpenClaw, перш ніж писати своєму агенту.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN --dry-run
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN
openclaw config set channels.discord.enabled true --strict-json
openclaw gateway
```

    Якщо OpenClaw уже працює як фонова служба, перезапустіть його через застосунок OpenClaw для Mac або зупинивши й знову запустивши процес `openclaw gateway run`.

  </Step>

  <Step title="Налаштуйте OpenClaw і виконайте підключення">

    <Tabs>
      <Tab title="Запитайте свого агента">
        Напишіть своєму агенту OpenClaw у будь-якому вже наявному каналі (наприклад, Telegram) і повідомте йому про це. Якщо Discord — це ваш перший канал, натомість використайте вкладку CLI / config.

        > "Я вже задав токен Discord бота в конфігурації. Будь ласка, заверши налаштування Discord з User ID `<user_id>` і Server ID `<server_id>`."
      </Tab>
      <Tab title="CLI / config">
        Якщо ви віддаєте перевагу конфігурації на основі файлу, задайте:

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: {
        source: "env",
        provider: "default",
        id: "DISCORD_BOT_TOKEN",
      },
    },
  },
}
```

        Резервне env-значення для облікового запису за замовчуванням:

```bash
DISCORD_BOT_TOKEN=...
```

        Підтримуються відкриті значення `token`. Значення SecretRef також підтримуються для `channels.discord.token` у провайдерах env/file/exec. Див. [Керування секретами](/uk/gateway/secrets).

      </Tab>
    </Tabs>

  </Step>

  <Step title="Схваліть перше підключення через DM">
    Дочекайтеся, поки шлюз запуститься, а потім надішліть DM своєму боту в Discord. Він відповість кодом підключення.

    <Tabs>
      <Tab title="Запитайте свого агента">
        Надішліть код підключення своєму агенту в уже наявному каналі:

        > "Схвали цей код підключення Discord: `<CODE>`"
      </Tab>
      <Tab title="CLI">

```bash
openclaw pairing list discord
openclaw pairing approve discord <CODE>
```

      </Tab>
    </Tabs>

    Термін дії кодів підключення спливає через 1 годину.

    Тепер ви маєте змогу спілкуватися зі своїм агентом у Discord через DM.

  </Step>
</Steps>

<Note>
Визначення токена залежить від облікового запису. Значення токена в конфігурації мають пріоритет над резервним env-значенням. `DISCORD_BOT_TOKEN` використовується лише для облікового запису за замовчуванням.
Для розширених вихідних викликів (дії message tool/channel) явний `token` для виклику використовується саме для цього виклику. Це стосується дій надсилання та дій у стилі читання/перевірки (наприклад read/search/fetch/thread/pins/permissions). Політика облікового запису й налаштування повторних спроб як і раніше беруться з вибраного облікового запису в активному знімку runtime.
</Note>

## Рекомендовано: налаштуйте простір роботи сервера

Коли DM уже працюють, ви можете налаштувати свій Discord-сервер як повноцінний простір роботи, де кожен канал отримує власну сесію агента з власним контекстом. Це рекомендовано для приватних серверів, де є лише ви та ваш бот.

<Steps>
  <Step title="Додайте свій сервер до allowlist серверів">
    Це дозволить вашому агенту відповідати в будь-якому каналі на вашому сервері, а не лише в DM.

    <Tabs>
      <Tab title="Запитайте свого агента">
        > "Додай мій Discord Server ID `<server_id>` до allowlist серверів"
      </Tab>
      <Tab title="Конфігурація">

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: true,
          users: ["YOUR_USER_ID"],
        },
      },
    },
  },
}
```

      </Tab>
    </Tabs>

  </Step>

  <Step title="Дозвольте відповіді без @mention">
    За замовчуванням ваш агент відповідає в каналах сервера лише тоді, коли його згадують через @mention. Для приватного сервера, імовірно, вам потрібно, щоб він відповідав на кожне повідомлення.

    <Tabs>
      <Tab title="Запитайте свого агента">
        > "Дозволь моєму агенту відповідати на цьому сервері без обов’язкової @mention"
      </Tab>
      <Tab title="Конфігурація">
        Установіть `requireMention: false` у конфігурації сервера:

```json5
{
  channels: {
    discord: {
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: false,
        },
      },
    },
  },
}
```

      </Tab>
    </Tabs>

  </Step>

  <Step title="Продумайте пам’ять у каналах сервера">
    За замовчуванням довготривала пам’ять (MEMORY.md) завантажується лише в DM-сесіях. У каналах сервера MEMORY.md не завантажується автоматично.

    <Tabs>
      <Tab title="Запитайте свого агента">
        > "Коли я ставлю запитання в каналах Discord, використовуй memory_search або memory_get, якщо тобі потрібен довготривалий контекст із MEMORY.md."
      </Tab>
      <Tab title="Вручну">
        Якщо вам потрібен спільний контекст у кожному каналі, розмістіть стабільні інструкції в `AGENTS.md` або `USER.md` (вони додаються в кожну сесію). Довготривалі нотатки зберігайте в `MEMORY.md` і звертайтеся до них за потреби через інструменти пам’яті.
      </Tab>
    </Tabs>

  </Step>
</Steps>

Тепер створіть кілька каналів на своєму Discord-сервері й починайте спілкування. Ваш агент бачить назву каналу, і кожен канал отримує власну ізольовану сесію — тож ви можете налаштувати `#coding`, `#home`, `#research` або будь-що, що відповідає вашому процесу роботи.

## Модель runtime

- Підключенням до Discord керує шлюз.
- Маршрутизація відповідей детермінована: вхідні повідомлення Discord отримують відповіді назад у Discord.
- За замовчуванням (`session.dmScope=main`) прямі чати використовують спільну основну сесію агента (`agent:main:main`).
- Канали сервера мають ізольовані ключі сесій (`agent:<agentId>:discord:channel:<channelId>`).
- Групові DM ігноруються за замовчуванням (`channels.discord.dm.groupEnabled=false`).
- Власні слеш-команди запускаються в ізольованих командних сесіях (`agent:<agentId>:discord:slash:<userId>`), водночас несучи `CommandTargetSessionKey` до спрямованої сесії розмови.

## Канали форуму

Discord forum і media channels приймають лише публікації у тредах. OpenClaw підтримує два способи їх створення:

- Надішліть повідомлення до батьківського форуму (`channel:<forumId>`), щоб автоматично створити тред. Заголовок треду використовує перший непорожній рядок вашого повідомлення.
- Використайте `openclaw message thread create`, щоб створити тред безпосередньо. Не передавайте `--message-id` для каналів форуму.

Приклад: надсилання до батьківського форуму для створення треду

```bash
openclaw message send --channel discord --target channel:<forumId> \
  --message "Topic title\nBody of the post"
```

Приклад: явне створення треду форуму

```bash
openclaw message thread create --channel discord --target channel:<forumId> \
  --thread-name "Topic title" --message "Body of the post"
```

Батьківські форуми не приймають компоненти Discord. Якщо вам потрібні компоненти, надсилайте повідомлення в сам тред (`channel:<threadId>`).

## Інтерактивні компоненти

OpenClaw підтримує Discord components v2 containers для повідомлень агента. Використовуйте message tool з payload `components`. Результати взаємодії спрямовуються назад до агента як звичайні вхідні повідомлення та дотримуються наявних налаштувань Discord `replyToMode`.

Підтримувані блоки:

- `text`, `section`, `separator`, `actions`, `media-gallery`, `file`
- Рядки дій допускають до 5 кнопок або одне меню вибору
- Типи вибору: `string`, `user`, `role`, `mentionable`, `channel`

За замовчуванням компоненти одноразові. Установіть `components.reusable=true`, щоб дозволити багаторазове використання кнопок, списків вибору й форм до завершення терміну їх дії.

Щоб обмежити коло користувачів, які можуть натискати кнопку, задайте `allowedUsers` для цієї кнопки (ID користувачів Discord, теги або `*`). Якщо налаштовано, користувачі, які не збігаються, отримують ефемерну відмову.

Слеш-команди `/model` і `/models` відкривають інтерактивний вибір моделі зі списками провайдера й моделі, а також кроком Submit. Відповідь вибору є ефемерною, і використовувати її може лише користувач, який викликав команду.

Вкладення файлів:

- Блоки `file` мають вказувати на посилання на вкладення (`attachment://<filename>`)
- Надайте вкладення через `media`/`path`/`filePath` (один файл); для кількох файлів використовуйте `media-gallery`
- Використовуйте `filename`, щоб перевизначити ім’я завантаження, коли воно має збігатися з посиланням на вкладення

Модальні форми:

- Додайте `components.modal` із максимум 5 полями
- Типи полів: `text`, `checkbox`, `radio`, `select`, `role-select`, `user-select`
- OpenClaw автоматично додає кнопку запуску

Приклад:

```json5
{
  channel: "discord",
  action: "send",
  to: "channel:123456789012345678",
  message: "Optional fallback text",
  components: {
    reusable: true,
    text: "Choose a path",
    blocks: [
      {
        type: "actions",
        buttons: [
          {
            label: "Approve",
            style: "success",
            allowedUsers: ["123456789012345678"],
          },
          { label: "Decline", style: "danger" },
        ],
      },
      {
        type: "actions",
        select: {
          type: "string",
          placeholder: "Pick an option",
          options: [
            { label: "Option A", value: "a" },
            { label: "Option B", value: "b" },
          ],
        },
      },
    ],
    modal: {
      title: "Details",
      triggerLabel: "Open form",
      fields: [
        { type: "text", label: "Requester" },
        {
          type: "select",
          label: "Priority",
          options: [
            { label: "Low", value: "low" },
            { label: "High", value: "high" },
          ],
        },
      ],
    },
  },
}
```

## Керування доступом і маршрутизація

<Tabs>
  <Tab title="Політика DM">
    `channels.discord.dmPolicy` керує доступом до DM (застаріле: `channels.discord.dm.policy`):

    - `pairing` (за замовчуванням)
    - `allowlist`
    - `open` (потребує, щоб `channels.discord.allowFrom` містив `"*"`; застаріле: `channels.discord.dm.allowFrom`)
    - `disabled`

    Якщо політика DM не є open, невідомі користувачі блокуються (або отримують запит на підключення в режимі `pairing`).

    Пріоритет для кількох облікових записів:

    - `channels.discord.accounts.default.allowFrom` застосовується лише до облікового запису `default`.
    - Іменовані облікові записи успадковують `channels.discord.allowFrom`, якщо їхній власний `allowFrom` не задано.
    - Іменовані облікові записи не успадковують `channels.discord.accounts.default.allowFrom`.

    Формат цілі DM для доставки:

    - `user:<id>`
    - згадка `<@id>`

    Прості числові ID неоднозначні й відхиляються, якщо явно не вказано тип цілі користувача/каналу.

  </Tab>

  <Tab title="Політика сервера">
    Обробка сервера керується через `channels.discord.groupPolicy`:

    - `open`
    - `allowlist`
    - `disabled`

    Безпечний базовий режим, коли існує `channels.discord`, — `allowlist`.

    Поведінка `allowlist`:

    - сервер має відповідати `channels.discord.guilds` (бажано `id`, також приймається slug)
    - необов’язкові allowlist відправників: `users` (рекомендовано стабільні ID) і `roles` (лише ID ролей); якщо налаштовано будь-який із них, відправники дозволяються, коли збігаються з `users` АБО `roles`
    - пряме зіставлення за іменем/тегом вимкнене за замовчуванням; увімкніть `channels.discord.dangerouslyAllowNameMatching: true` лише як аварійний режим сумісності
    - для `users` підтримуються імена/теги, але ID безпечніші; `openclaw security audit` попереджає, коли використовуються записи з іменами/тегами
    - якщо для сервера налаштовано `channels`, канали, яких немає у списку, забороняються
    - якщо для сервера немає блоку `channels`, дозволяються всі канали цього сервера з allowlist

    Приклад:

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        "123456789012345678": {
          requireMention: true,
          ignoreOtherMentions: true,
          users: ["987654321098765432"],
          roles: ["123456789012345678"],
          channels: {
            general: { allow: true },
            help: { allow: true, requireMention: true },
          },
        },
      },
    },
  },
}
```

    Якщо ви лише задаєте `DISCORD_BOT_TOKEN` і не створюєте блок `channels.discord`, резервний режим runtime буде `groupPolicy="allowlist"` (із попередженням у логах), навіть якщо `channels.defaults.groupPolicy` дорівнює `open`.

  </Tab>

  <Tab title="Згадки і групові DM">
    Повідомлення сервера за замовчуванням проходять через перевірку згадки.

    Виявлення згадки включає:

    - явну згадку бота
    - налаштовані шаблони згадок (`agents.list[].groupChat.mentionPatterns`, резервно — `messages.groupChat.mentionPatterns`)
    - неявну поведінку reply-to-bot у підтримуваних випадках

    `requireMention` налаштовується для кожного сервера/каналу (`channels.discord.guilds...`).
    `ignoreOtherMentions` за потреби відкидає повідомлення, які згадують іншого користувача/роль, але не бота (за винятком @everyone/@here).

    Групові DM:

    - за замовчуванням: ігноруються (`dm.groupEnabled=false`)
    - необов’язковий allowlist через `dm.groupChannels` (ID каналів або slug)

  </Tab>
</Tabs>

### Маршрутизація агентів за ролями

Використовуйте `bindings[].match.roles`, щоб спрямовувати учасників Discord-сервера до різних агентів за ID ролі. Прив’язки за ролями приймають лише ID ролей і обчислюються після прив’язок peer або parent-peer та перед прив’язками лише за сервером. Якщо прив’язка також задає інші поля зіставлення (наприклад, `peer` + `guildId` + `roles`), мають збігатися всі налаштовані поля.

```json5
{
  bindings: [
    {
      agentId: "opus",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
        roles: ["111111111111111111"],
      },
    },
    {
      agentId: "sonnet",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
      },
    },
  ],
}
```

## Налаштування Developer Portal

<AccordionGroup>
  <Accordion title="Створення застосунку і бота">

    1. Discord Developer Portal -> **Applications** -> **New Application**
    2. **Bot** -> **Add Bot**
    3. Скопіюйте токен бота

  </Accordion>

  <Accordion title="Привілейовані intents">
    У **Bot -> Privileged Gateway Intents** увімкніть:

    - Message Content Intent
    - Server Members Intent (рекомендовано)

    Presence intent є необов’язковим і потрібне лише якщо ви хочете отримувати оновлення присутності. Налаштування присутності бота (`setPresence`) не потребує ввімкнення оновлень присутності для учасників.

  </Accordion>

  <Accordion title="OAuth scopes і базові дозволи">
    Генератор OAuth URL:

    - scopes: `bot`, `applications.commands`

    Типові базові дозволи:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (необов’язково)

    Уникайте `Administrator`, якщо це не потрібно явно.

  </Accordion>

  <Accordion title="Копіювання ID">
    Увімкніть Discord Developer Mode, а потім скопіюйте:

    - ID сервера
    - ID каналу
    - ID користувача

    Для надійних аудитів і перевірок у конфігурації OpenClaw надавайте перевагу числовим ID.

  </Accordion>
</AccordionGroup>

## Власні команди і авторизація команд

- `commands.native` за замовчуванням має значення `"auto"` і ввімкнене для Discord.
- Перевизначення для каналу: `channels.discord.commands.native`.
- `commands.native=false` явно очищає раніше зареєстровані власні команди Discord.
- Авторизація власних команд використовує ті самі allowlist/політики Discord, що й звичайна обробка повідомлень.
- Команди все ще можуть бути видимі в UI Discord для користувачів, які не мають доступу; виконання однаково перевіряє авторизацію OpenClaw і повертає "not authorized".

Див. [Слеш-команди](/uk/tools/slash-commands), щоб переглянути каталог команд і їхню поведінку.

Налаштування слеш-команд за замовчуванням:

- `ephemeral: true`

## Деталі функцій

<AccordionGroup>
  <Accordion title="Теги відповіді і власні відповіді">
    Discord підтримує теги відповіді у вихідних повідомленнях агента:

    - `[[reply_to_current]]`
    - `[[reply_to:<id>]]`

    Керується через `channels.discord.replyToMode`:

    - `off` (за замовчуванням)
    - `first`
    - `all`
    - `batched`

    Примітка: `off` вимикає неявне розгалуження відповідей. Явні теги `[[reply_to_*]]` все одно враховуються.
    `first` завжди прикріплює неявне власне посилання на відповідь до першого вихідного повідомлення Discord у поточному ході.
    `batched` прикріплює неявне власне посилання Discord на відповідь лише тоді, коли
    вхідний хід був відкладеним пакетом із кількох повідомлень. Це зручно,
    коли власні відповіді потрібні переважно для неоднозначних чатів із частими серіями повідомлень, а не для кожного
    окремого ходу з одним повідомленням.

    ID повідомлень додаються до контексту/історії, щоб агенти могли націлюватися на конкретні повідомлення.

  </Accordion>

  <Accordion title="Попередній перегляд потоку в реальному часі">
    OpenClaw може потоково показувати чернетки відповідей, надсилаючи тимчасове повідомлення й редагуючи його в міру надходження тексту.

    - `channels.discord.streaming` керує потоковим попереднім переглядом (`off` | `partial` | `block` | `progress`, за замовчуванням: `off`).
    - За замовчуванням лишається `off`, бо редагування попереднього перегляду в Discord може швидко впиратися в обмеження частоти, особливо коли кілька ботів або шлюзів використовують той самий обліковий запис чи трафік сервера.
    - `progress` приймається для узгодженості між каналами та в Discord зіставляється з `partial`.
    - `channels.discord.streamMode` — це застарілий псевдонім, який мігрується автоматично.
    - `partial` редагує одне повідомлення попереднього перегляду в міру надходження токенів.
    - `block` видає фрагменти розміру чернетки (розмір і точки розриву налаштовуються через `draftChunk`).

    Приклад:

```json5
{
  channels: {
    discord: {
      streaming: "partial",
    },
  },
}
```

    Значення за замовчуванням для розбиття в режимі `block` (обмежуються `channels.discord.textChunkLimit`):

```json5
{
  channels: {
    discord: {
      streaming: "block",
      draftChunk: {
        minChars: 200,
        maxChars: 800,
        breakPreference: "paragraph",
      },
    },
  },
}
```

    Потоковий попередній перегляд працює лише з текстом; відповіді з медіа повертаються до звичайної доставки.

    Примітка: потоковий попередній перегляд — це окрема функція від block streaming. Коли block streaming явно
    увімкнено для Discord, OpenClaw пропускає попередній перегляд потоку, щоб уникнути подвійного потокового передавання.

  </Accordion>

  <Accordion title="Історія, контекст і поведінка тредів">
    Контекст історії сервера:

    - `channels.discord.historyLimit` за замовчуванням `20`
    - резервне значення: `messages.groupChat.historyLimit`
    - `0` вимикає

    Елементи керування історією DM:

    - `channels.discord.dmHistoryLimit`
    - `channels.discord.dms["<user_id>"].historyLimit`

    Поведінка тредів:

    - Discord-треди спрямовуються як сесії каналів
    - метадані батьківського треду можуть використовуватися для зв’язку з батьківською сесією
    - конфігурація треду успадковує конфігурацію батьківського каналу, якщо немає запису, специфічного для треду

    Теми каналів додаються як **недовірений** контекст (не як system prompt).
    Контекст відповіді та цитованого повідомлення наразі зберігається в отриманому вигляді.
    Allowlist Discord передусім обмежують, хто може запускати агента, а не є повною межею редагування додаткового контексту.

  </Accordion>

  <Accordion title="Сесії, прив’язані до тредів, для субагентів">
    Discord може прив’язати тред до цілі сесії, щоб подальші повідомлення в цьому треді й далі спрямовувалися до тієї самої сесії (зокрема сесій субагентів).

    Команди:

    - `/focus <target>` прив’язує поточний/новий тред до цілі субагента/сесії
    - `/unfocus` прибирає поточну прив’язку треду
    - `/agents` показує активні запуски і стан прив’язки
    - `/session idle <duration|off>` переглядає/оновлює автоматичне зняття фокуса через неактивність для сфокусованих прив’язок
    - `/session max-age <duration|off>` переглядає/оновлює жорсткий максимальний вік для сфокусованих прив’язок

    Конфігурація:

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // opt-in
      },
    },
  },
}
```

    Примітки:

    - `session.threadBindings.*` задає глобальні значення за замовчуванням.
    - `channels.discord.threadBindings.*` перевизначає поведінку Discord.
    - `spawnSubagentSessions` має бути true, щоб автоматично створювати/прив’язувати треди для `sessions_spawn({ thread: true })`.
    - `spawnAcpSessions` має бути true, щоб автоматично створювати/прив’язувати треди для ACP (`/acp spawn ... --thread ...` або `sessions_spawn({ runtime: "acp", thread: true })`).
    - Якщо прив’язки тредів вимкнено для облікового запису, `/focus` і пов’язані операції прив’язки тредів недоступні.

    Див. [Sub-agents](/uk/tools/subagents), [ACP Agents](/uk/tools/acp-agents) і [Configuration Reference](/uk/gateway/configuration-reference).

  </Accordion>

  <Accordion title="Постійні ACP-прив’язки каналів">
    Для стабільних "завжди активних" просторів роботи ACP налаштуйте типізовані ACP-прив’язки верхнього рівня, націлені на розмови Discord.

    Шлях конфігурації:

    - `bindings[]` із `type: "acp"` і `match.channel: "discord"`

    Приклад:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": {
              requireMention: false,
            },
          },
        },
      },
    },
  },
}
```

    Примітки:

    - `/acp spawn codex --bind here` прив’язує поточний канал або тред Discord на місці та зберігає маршрутизацію майбутніх повідомлень до тієї самої ACP-сесії.
    - Це все ще може означати "запустити нову ACP-сесію Codex", але саме по собі не створює новий тред Discord. Наявний канал залишається поверхнею чату.
    - Codex усе одно може працювати у власному `cwd` або робочому просторі backend на диску. Цей робочий простір є станом runtime, а не тредом Discord.
    - Повідомлення в треді можуть успадковувати ACP-прив’язку батьківського каналу.
    - У прив’язаному каналі або треді `/new` і `/reset` скидають ту саму ACP-сесію на місці.
    - Тимчасові прив’язки тредів як і раніше працюють і можуть перевизначати визначення цілі, поки активні.
    - `spawnAcpSessions` потрібне лише тоді, коли OpenClaw має створити/прив’язати дочірній тред через `--thread auto|here`. Воно не потрібне для `/acp spawn ... --bind here` у поточному каналі.

    Докладніше про поведінку прив’язок див. у [ACP Agents](/uk/tools/acp-agents).

  </Accordion>

  <Accordion title="Сповіщення про реакції">
    Режим сповіщень про реакції для кожного сервера:

    - `off`
    - `own` (за замовчуванням)
    - `all`
    - `allowlist` (використовує `guilds.<id>.users`)

    Події реакцій перетворюються на системні події й прикріплюються до спрямованої Discord-сесії.

  </Accordion>

  <Accordion title="Реакції-підтвердження">
    `ackReaction` надсилає emoji-підтвердження, поки OpenClaw обробляє вхідне повідомлення.

    Порядок визначення:

    - `channels.discord.accounts.<accountId>.ackReaction`
    - `channels.discord.ackReaction`
    - `messages.ackReaction`
    - резервне emoji ідентичності агента (`agents.list[].identity.emoji`, інакше "👀")

    Примітки:

    - Discord приймає unicode emoji або назви кастомних emoji.
    - Використовуйте `""`, щоб вимкнути реакцію для каналу або облікового запису.

  </Accordion>

  <Accordion title="Запис конфігурації">
    Запис конфігурації, ініційований із каналу, увімкнено за замовчуванням.

    Це впливає на потоки `/config set|unset` (коли функції команд увімкнено).

    Вимкнути:

```json5
{
  channels: {
    discord: {
      configWrites: false,
    },
  },
}
```

  </Accordion>

  <Accordion title="Проксі шлюзу">
    Спрямовуйте трафік WebSocket шлюзу Discord і початкові REST-запити (ID застосунку + визначення allowlist) через HTTP(S)-проксі за допомогою `channels.discord.proxy`.

```json5
{
  channels: {
    discord: {
      proxy: "http://proxy.example:8080",
    },
  },
}
```

    Перевизначення для облікового запису:

```json5
{
  channels: {
    discord: {
      accounts: {
        primary: {
          proxy: "http://proxy.example:8080",
        },
      },
    },
  },
}
```

  </Accordion>

  <Accordion title="Підтримка PluralKit">
    Увімкніть визначення PluralKit, щоб зіставляти проксовані повідомлення з ідентичністю учасника системи:

```json5
{
  channels: {
    discord: {
      pluralkit: {
        enabled: true,
        token: "pk_live_...", // optional; needed for private systems
      },
    },
  },
}
```

    Примітки:

    - allowlist можуть використовувати `pk:<memberId>`
    - відображувані імена учасників зіставляються за name/slug лише коли `channels.discord.dangerouslyAllowNameMatching: true`
    - пошук використовує ID початкового повідомлення й обмежується часовим вікном
    - якщо пошук не вдається, проксовані повідомлення вважаються повідомленнями бота й відкидаються, якщо тільки не `allowBots=true`

  </Accordion>

  <Accordion title="Конфігурація присутності">
    Оновлення присутності застосовуються, коли ви задаєте поле статусу або активності, або коли вмикаєте автоматичну присутність.

    Приклад лише зі статусом:

```json5
{
  channels: {
    discord: {
      status: "idle",
    },
  },
}
```

    Приклад активності (custom status — це тип активності за замовчуванням):

```json5
{
  channels: {
    discord: {
      activity: "Focus time",
      activityType: 4,
    },
  },
}
```

    Приклад трансляції:

```json5
{
  channels: {
    discord: {
      activity: "Live coding",
      activityType: 1,
      activityUrl: "https://twitch.tv/openclaw",
    },
  },
}
```

    Відповідність типів активності:

    - 0: Playing
    - 1: Streaming (потрібен `activityUrl`)
    - 2: Listening
    - 3: Watching
    - 4: Custom (використовує текст активності як стан статусу; emoji необов’язкове)
    - 5: Competing

    Приклад автоматичної присутності (сигнал працездатності runtime):

```json5
{
  channels: {
    discord: {
      autoPresence: {
        enabled: true,
        intervalMs: 30000,
        minUpdateIntervalMs: 15000,
        exhaustedText: "token exhausted",
      },
    },
  },
}
```

    Автоматична присутність зіставляє доступність runtime зі статусом Discord: healthy => online, degraded або unknown => idle, exhausted або unavailable => dnd. Необов’язкові перевизначення тексту:

    - `autoPresence.healthyText`
    - `autoPresence.degradedText`
    - `autoPresence.exhaustedText` (підтримує заповнювач `{reason}`)

  </Accordion>

  <Accordion title="Погодження в Discord">
    Discord підтримує обробку погоджень через кнопки в DM і може за бажанням публікувати запити на погодження у вихідному каналі.

    Шлях конфігурації:

    - `channels.discord.execApprovals.enabled`
    - `channels.discord.execApprovals.approvers` (необов’язково; за можливості резервно використовується `commands.ownerAllowFrom`)
    - `channels.discord.execApprovals.target` (`dm` | `channel` | `both`, за замовчуванням: `dm`)
    - `agentFilter`, `sessionFilter`, `cleanupAfterResolve`

    Discord автоматично вмикає власні погодження виконання, коли `enabled` не задано або має значення `"auto"` і можна визначити принаймні одного затверджувача — або з `execApprovals.approvers`, або з `commands.ownerAllowFrom`. Discord не визначає затверджувачів виконання з `allowFrom` каналу, застарілого `dm.allowFrom` чи `defaultTo` прямих повідомлень. Установіть `enabled: false`, щоб явно вимкнути Discord як власний клієнт погоджень.

    Коли `target` має значення `channel` або `both`, запит на погодження видно в каналі. Лише визначені затверджувачі можуть використовувати кнопки; інші користувачі отримують ефемерну відмову. Запити на погодження містять текст команди, тому вмикайте доставку в канал лише в довірених каналах. Якщо ID каналу неможливо вивести з ключа сесії, OpenClaw повертається до доставки через DM.

    Discord також відображає спільні кнопки погодження, що використовуються іншими чат-каналами. Власний адаптер Discord головно додає маршрутизацію погоджень затверджувачам у DM і fanout у канал.
    Коли ці кнопки присутні, вони є основним UX для погодження; OpenClaw
    повинен включати ручну команду `/approve` лише тоді, коли результат інструмента каже,
    що погодження в чаті недоступні або ручне погодження — єдиний шлях.

    Авторизація шлюзу для цього обробника використовує той самий спільний контракт визначення облікових даних, що й інші клієнти Gateway:

    - локальна авторизація env-first (`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`, далі `gateway.auth.*`)
    - у локальному режимі `gateway.remote.*` може використовуватися як резервний варіант лише коли `gateway.auth.*` не задано; налаштовані, але не визначені локальні SecretRef закриваються в безпечний режим відмови
    - підтримка remote-mode через `gateway.remote.*`, де це застосовно
    - перевизначення URL безпечні щодо перевизначень: перевизначення CLI не повторно використовують неявні облікові дані, а перевизначення env використовують лише env-облікові дані

    Поведінка визначення погоджень:

    - ID з префіксом `plugin:` визначаються через `plugin.approval.resolve`.
    - Інші ID визначаються через `exec.approval.resolve`.
    - Discord не робить тут додаткового резервного переходу exec-to-plugin; тип
      префікса ID визначає, який метод шлюзу буде викликано.

    Термін дії погоджень виконання за замовчуванням спливає через 30 хвилин. Якщо погодження завершуються помилкою з
    невідомими ID погоджень, перевірте визначення затверджувачів, увімкнення функції і
    те, що доставлений тип ID погодження збігається з очікуваним запитом.

    Пов’язана документація: [Exec approvals](/uk/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## Інструменти і gate дій

Дії повідомлень Discord включають повідомлення, адміністрування каналів, модерацію, присутність і дії з метаданими.

Основні приклади:

- повідомлення: `sendMessage`, `readMessages`, `editMessage`, `deleteMessage`, `threadReply`
- реакції: `react`, `reactions`, `emojiList`
- модерація: `timeout`, `kick`, `ban`
- присутність: `setPresence`

Gate дій розміщені в `channels.discord.actions.*`.

Типова поведінка gate:

| Група дій                                                                                                                                                                | За замовчуванням |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------- |
| reactions, messages, threads, pins, polls, search, memberInfo, roleInfo, channelInfo, channels, voiceStatus, events, stickers, emojiUploads, stickerUploads, permissions | увімкнено        |
| roles                                                                                                                                                                    | вимкнено         |
| moderation                                                                                                                                                               | вимкнено         |
| presence                                                                                                                                                                 | вимкнено         |

## UI Components v2

OpenClaw використовує Discord components v2 для погоджень виконання і маркерів між контекстами. Дії повідомлень Discord також можуть приймати `components` для власного UI (розширений сценарій; потребує побудови payload компонента через discord tool), тоді як застарілі `embeds` залишаються доступними, але не рекомендовані.

- `channels.discord.ui.components.accentColor` задає акцентний колір, який використовується контейнерами компонентів Discord (hex).
- Для окремого облікового запису задається через `channels.discord.accounts.<id>.ui.components.accentColor`.
- `embeds` ігноруються, коли присутні components v2.

Приклад:

```json5
{
  channels: {
    discord: {
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
    },
  },
}
```

## Голосові канали

OpenClaw може приєднуватися до голосових каналів Discord для розмов у реальному часі без перерв. Це окрема функція від вкладень голосових повідомлень.

Вимоги:

- Увімкніть власні команди (`commands.native` або `channels.discord.commands.native`).
- Налаштуйте `channels.discord.voice`.
- Бот повинен мати дозволи Connect + Speak у цільовому голосовому каналі.

Використовуйте власну Discord-команду `/vc join|leave|status` для керування сесіями. Команда використовує агента облікового запису за замовчуванням і дотримується тих самих правил allowlist і group policy, що й інші команди Discord.

Приклад автоматичного приєднання:

```json5
{
  channels: {
    discord: {
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
    },
  },
}
```

Примітки:

- `voice.tts` перевизначає `messages.tts` лише для відтворення голосу.
- Ходи транскрипції голосу визначають статус власника з Discord `allowFrom` (або `dm.allowFrom`); користувачі, які не є власниками, не можуть отримувати доступ до інструментів тільки для власника (наприклад `gateway` і `cron`).
- Голос увімкнено за замовчуванням; установіть `channels.discord.voice.enabled=false`, щоб вимкнути його.
- `voice.daveEncryption` і `voice.decryptionFailureTolerance` напряму передаються в параметри приєднання `@discordjs/voice`.
- Якщо не задано, `@discordjs/voice` використовує значення за замовчуванням `daveEncryption=true` і `decryptionFailureTolerance=24`.
- OpenClaw також відстежує помилки дешифрування під час прийому й автоматично відновлюється, виходячи з голосового каналу та повторно приєднуючись після повторних помилок у короткому вікні часу.
- Якщо журнали прийому неодноразово показують `DecryptionFailed(UnencryptedWhenPassthroughDisabled)`, це може бути висхідною помилкою прийому `@discordjs/voice`, яку відстежено в [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419).

## Голосові повідомлення

Голосові повідомлення Discord відображають попередній перегляд форми хвилі й вимагають аудіо OGG/Opus разом із метаданими. OpenClaw генерує форму хвилі автоматично, але на хості шлюзу мають бути доступні `ffmpeg` і `ffprobe`, щоб аналізувати й конвертувати аудіофайли.

Вимоги й обмеження:

- Вкажіть **локальний шлях до файлу** (URL відхиляються).
- Не додавайте текстовий вміст (Discord не дозволяє текст + голосове повідомлення в одному payload).
- Підтримується будь-який аудіоформат; OpenClaw за потреби конвертує його в OGG/Opus.

Приклад:

```bash
message(action="send", channel="discord", target="channel:123", path="/path/to/audio.mp3", asVoice=true)
```

## Усунення проблем

<AccordionGroup>
  <Accordion title="Використано заборонені intents або бот не бачить повідомлення сервера">

    - увімкніть Message Content Intent
    - увімкніть Server Members Intent, якщо ви залежите від визначення користувача/учасника
    - перезапустіть шлюз після зміни intents

  </Accordion>

  <Accordion title="Повідомлення сервера неочікувано блокуються">

    - перевірте `groupPolicy`
    - перевірте allowlist серверів у `channels.discord.guilds`
    - якщо існує мапа `channels` сервера, дозволені лише канали зі списку
    - перевірте поведінку `requireMention` і шаблони згадок

    Корисні перевірки:

```bash
openclaw doctor
openclaw channels status --probe
openclaw logs --follow
```

  </Accordion>

  <Accordion title="Потрібна згадка вимкнена, але все одно блокується">
    Типові причини:

    - `groupPolicy="allowlist"` без відповідного allowlist сервера/каналу
    - `requireMention` налаштовано в неправильному місці (має бути в `channels.discord.guilds` або в записі каналу)
    - відправника блокує allowlist `users` сервера/каналу

  </Accordion>

  <Accordion title="Довгі обробники завершуються за тайм-аутом або дублюють відповіді">

    Типові журнали:

    - `Listener DiscordMessageListener timed out after 30000ms for event MESSAGE_CREATE`
    - `Slow listener detected ...`
    - `discord inbound worker timed out after ...`

    Параметр бюджету listener:

    - один обліковий запис: `channels.discord.eventQueue.listenerTimeout`
    - кілька облікових записів: `channels.discord.accounts.<accountId>.eventQueue.listenerTimeout`

    Параметр тайм-ауту запуску worker:

    - один обліковий запис: `channels.discord.inboundWorker.runTimeoutMs`
    - кілька облікових записів: `channels.discord.accounts.<accountId>.inboundWorker.runTimeoutMs`
    - за замовчуванням: `1800000` (30 хвилин); установіть `0`, щоб вимкнути

    Рекомендований базовий варіант:

```json5
{
  channels: {
    discord: {
      accounts: {
        default: {
          eventQueue: {
            listenerTimeout: 120000,
          },
          inboundWorker: {
            runTimeoutMs: 1800000,
          },
        },
      },
    },
  },
}
```

    Використовуйте `eventQueue.listenerTimeout` для повільного налаштування listener, а `inboundWorker.runTimeoutMs`
    лише якщо вам потрібен окремий запобіжник для черги ходів агента.

  </Accordion>

  <Accordion title="Невідповідності аудиту дозволів">
    Перевірки дозволів `channels status --probe` працюють лише для числових ID каналів.

    Якщо ви використовуєте ключі slug, зіставлення в runtime усе ще може працювати, але probe не може повністю перевірити дозволи.

  </Accordion>

  <Accordion title="Проблеми з DM і підключенням">

    - DM вимкнено: `channels.discord.dm.enabled=false`
    - політика DM вимкнена: `channels.discord.dmPolicy="disabled"` (застаріле: `channels.discord.dm.policy`)
    - очікується схвалення підключення в режимі `pairing`

  </Accordion>

  <Accordion title="Цикли бот-до-бота">
    За замовчуванням повідомлення, створені ботами, ігноруються.

    Якщо ви встановлюєте `channels.discord.allowBots=true`, використовуйте суворі правила згадок і allowlist, щоб уникнути циклічної поведінки.
    Надавайте перевагу `channels.discord.allowBots="mentions"`, щоб приймати лише повідомлення ботів, які згадують бота.

  </Accordion>

  <Accordion title="Голосовий STT пропадає з DecryptionFailed(...)">

    - підтримуйте актуальну версію OpenClaw (`openclaw update`), щоб була наявна логіка відновлення прийому голосу Discord
    - підтвердьте `channels.discord.voice.daveEncryption=true` (за замовчуванням)
    - почніть із `channels.discord.voice.decryptionFailureTolerance=24` (значення upstream за замовчуванням) і змінюйте лише за потреби
    - стежте за журналами:
      - `discord voice: DAVE decrypt failures detected`
      - `discord voice: repeated decrypt failures; attempting rejoin`
    - якщо помилки тривають після автоматичного повторного приєднання, зберіть журнали й порівняйте з [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419)

  </Accordion>
</AccordionGroup>

## Вказівники до довідника з конфігурації

Основний довідник:

- [Configuration reference - Discord](/uk/gateway/configuration-reference#discord)

Ключові поля Discord:

- запуск/авторизація: `enabled`, `token`, `accounts.*`, `allowBots`
- політика: `groupPolicy`, `dm.*`, `guilds.*`, `guilds.*.channels.*`
- команди: `commands.native`, `commands.useAccessGroups`, `configWrites`, `slashCommand.*`
- черга подій: `eventQueue.listenerTimeout` (бюджет listener), `eventQueue.maxQueueSize`, `eventQueue.maxConcurrency`
- inbound worker: `inboundWorker.runTimeoutMs`
- відповідь/історія: `replyToMode`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
- доставка: `textChunkLimit`, `chunkMode`, `maxLinesPerMessage`
- потокова передача: `streaming` (застарілий псевдонім: `streamMode`), `draftChunk`, `blockStreaming`, `blockStreamingCoalesce`
- медіа/повторні спроби: `mediaMaxMb`, `retry`
  - `mediaMaxMb` обмежує вихідні завантаження Discord (за замовчуванням: `8MB`)
- дії: `actions.*`
- присутність: `activity`, `status`, `activityType`, `activityUrl`
- UI: `ui.components.accentColor`
- функції: `threadBindings`, верхньорівневі `bindings[]` (`type: "acp"`), `pluralkit`, `execApprovals`, `intents`, `agentComponents`, `heartbeat`, `responsePrefix`

## Безпека і експлуатація

- Вважайте токени ботів секретами (`DISCORD_BOT_TOKEN` є бажаним варіантом у контрольованих середовищах).
- Надавайте Discord дозволи за принципом найменших привілеїв.
- Якщо розгортання/стан команд застаріли, перезапустіть шлюз і повторно перевірте за допомогою `openclaw channels status --probe`.

## Пов’язане

- [Підключення](/uk/channels/pairing)
- [Групи](/uk/channels/groups)
- [Маршрутизація каналів](/uk/channels/channel-routing)
- [Безпека](/uk/gateway/security)
- [Маршрутизація кількох агентів](/uk/concepts/multi-agent)
- [Усунення проблем](/uk/channels/troubleshooting)
- [Слеш-команди](/uk/tools/slash-commands)
