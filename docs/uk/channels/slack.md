---
read_when:
    - Налаштування Slack або налагодження режиму socket/HTTP у Slack
summary: Налаштування Slack і поведінка під час роботи (Socket Mode + HTTP Events API)
title: Slack
x-i18n:
    generated_at: "2026-04-05T20:43:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7e4ff2ce7d92276d62f4f3d3693ddb56ca163d5fdc2f1082ff7ba3421fada69c
    source_path: channels/slack.md
    workflow: 15
---

# Slack

Статус: готовий до використання у production для особистих повідомлень і каналів через інтеграції застосунку Slack. Типовий режим — Socket Mode; режим HTTP Events API також підтримується.

<CardGroup cols={3}>
  <Card title="Сполучення" icon="link" href="/uk/channels/pairing">
    Особисті повідомлення Slack типово використовують режим сполучення.
  </Card>
  <Card title="Slash-команди" icon="terminal" href="/uk/tools/slash-commands">
    Вбудована поведінка команд і каталог команд.
  </Card>
  <Card title="Усунення проблем із каналами" icon="wrench" href="/uk/channels/troubleshooting">
    Міжканальна діагностика та сценарії відновлення.
  </Card>
</CardGroup>

## Швидке налаштування

<Tabs>
  <Tab title="Socket Mode (типово)">
    <Steps>
      <Step title="Створіть застосунок Slack і токени">
        У налаштуваннях застосунку Slack:

        - увімкніть **Socket Mode**
        - створіть **App Token** (`xapp-...`) з `connections:write`
        - установіть застосунок і скопіюйте **Bot Token** (`xoxb-...`)
      </Step>

      <Step title="Налаштуйте OpenClaw">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "socket",
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

        Резервне значення з env (лише для облікового запису за замовчуванням):

```bash
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
```

      </Step>

      <Step title="Підпишіть події застосунку">
        Підпишіть події бота для:

        - `app_mention`
        - `message.channels`, `message.groups`, `message.im`, `message.mpim`
        - `reaction_added`, `reaction_removed`
        - `member_joined_channel`, `member_left_channel`
        - `channel_rename`
        - `pin_added`, `pin_removed`

        Також увімкніть **Messages Tab** у App Home для особистих повідомлень.
      </Step>

      <Step title="Запустіть gateway">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="Режим HTTP Events API">
    <Steps>
      <Step title="Налаштуйте застосунок Slack для HTTP">

        - установіть режим HTTP (`channels.slack.mode="http"`)
        - скопіюйте **Signing Secret** Slack
        - установіть однаковий Request URL для Event Subscriptions, Interactivity і Slash command на той самий шлях webhook (типово `/slack/events`)

      </Step>

      <Step title="Налаштуйте HTTP-режим OpenClaw">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "your-signing-secret",
      webhookPath: "/slack/events",
    },
  },
}
```

      </Step>

      <Step title="Використовуйте унікальні шляхи webhook для HTTP з кількома обліковими записами">
        Режим HTTP для кількох облікових записів підтримується.

        Надайте кожному обліковому запису окремий `webhookPath`, щоб реєстрації не конфліктували.
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Контрольний список маніфесту та scope

<AccordionGroup>
  <Accordion title="Приклад маніфесту застосунку Slack" defaultOpen>

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    }
  }
}
```

  </Accordion>

  <Accordion title="Необов'язкові scope токена користувача (операції читання)">
    Якщо ви налаштовуєте `channels.slack.userToken`, типовими scope для читання є:

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read` (якщо ви залежите від читання пошуку Slack)

  </Accordion>
</AccordionGroup>

## Модель токенів

- `botToken` + `appToken` обов'язкові для Socket Mode.
- HTTP-режим потребує `botToken` + `signingSecret`.
- `botToken`, `appToken`, `signingSecret` і `userToken` приймають звичайні рядки
  або об'єкти SecretRef.
- Токени з конфігурації мають пріоритет над резервними значеннями з env.
- Резервні значення з env `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` застосовуються лише до облікового запису за замовчуванням.
- `userToken` (`xoxp-...`) доступний лише в конфігурації (без резервного значення з env) і типово працює в режимі лише для читання (`userTokenReadOnly: true`).
- Необов'язково: додайте `chat:write.customize`, якщо хочете, щоб вихідні повідомлення використовували ідентичність активного агента (власні `username` та icon). Для `icon_emoji` використовується синтаксис `:emoji_name:`.

Поведінка знімка стану:

- Перевірка облікового запису Slack відстежує поля `*Source` і `*Status`
  для кожних облікових даних (`botToken`, `appToken`, `signingSecret`, `userToken`).
- Статус може бути `available`, `configured_unavailable` або `missing`.
- `configured_unavailable` означає, що обліковий запис налаштовано через SecretRef
  або інше не-inline джерело секретів, але поточний шлях команди/виконання
  не зміг визначити фактичне значення.
- У HTTP-режимі включається `signingSecretStatus`; у Socket Mode
  обов'язковою парою є `botTokenStatus` + `appTokenStatus`.

<Tip>
Для дій/читання каталогів за наявності налаштування може надаватися перевага токену користувача. Для запису пріоритетним лишається токен бота; запис через токен користувача дозволено лише коли `userTokenReadOnly: false` і токен бота недоступний.
</Tip>

## Дії та обмеження

Дії Slack контролюються через `channels.slack.actions.*`.

Доступні групи дій у поточному інструментарії Slack:

| Група      | Типово |
| ---------- | ------- |
| messages   | увімкнено |
| reactions  | увімкнено |
| pins       | увімкнено |
| memberInfo | увімкнено |
| emojiList  | увімкнено |

Поточні дії з повідомленнями Slack включають `send`, `upload-file`, `download-file`, `read`, `edit`, `delete`, `pin`, `unpin`, `list-pins`, `member-info` та `emoji-list`.

## Контроль доступу та маршрутизація

<Tabs>
  <Tab title="Політика особистих повідомлень">
    `channels.slack.dmPolicy` контролює доступ до особистих повідомлень (застаріле: `channels.slack.dm.policy`):

    - `pairing` (типово)
    - `allowlist`
    - `open` (потребує, щоб `channels.slack.allowFrom` містив `"*"`; застаріле: `channels.slack.dm.allowFrom`)
    - `disabled`

    Прапорці особистих повідомлень:

    - `dm.enabled` (типово true)
    - `channels.slack.allowFrom` (рекомендовано)
    - `dm.allowFrom` (застаріле)
    - `dm.groupEnabled` (групові особисті повідомлення типово false)
    - `dm.groupChannels` (необов'язковий allowlist MPIM)

    Пріоритет для кількох облікових записів:

    - `channels.slack.accounts.default.allowFrom` застосовується лише до облікового запису `default`.
    - Іменовані облікові записи успадковують `channels.slack.allowFrom`, якщо їхній власний `allowFrom` не задано.
    - Іменовані облікові записи не успадковують `channels.slack.accounts.default.allowFrom`.

    Сполучення в особистих повідомленнях використовує `openclaw pairing approve slack <code>`.

  </Tab>

  <Tab title="Політика каналів">
    `channels.slack.groupPolicy` контролює обробку каналів:

    - `open`
    - `allowlist`
    - `disabled`

    Allowlist каналів міститься в `channels.slack.channels` і має використовувати стабільні ідентифікатори каналів.

    Примітка щодо виконання: якщо `channels.slack` повністю відсутній (налаштування лише через env), під час виконання використовується `groupPolicy="allowlist"` і записується попередження в журнал (навіть якщо задано `channels.defaults.groupPolicy`).

    Визначення імен/ідентифікаторів:

    - записи allowlist каналів і записи allowlist особистих повідомлень визначаються під час запуску, якщо доступ токена це дозволяє
    - нерозв'язані записи з іменами каналів зберігаються як налаштовані, але типово ігноруються для маршрутизації
    - вхідна авторизація та маршрутизація каналів типово працюють за ідентифікаторами; пряме зіставлення за username/slug потребує `channels.slack.dangerouslyAllowNameMatching: true`

  </Tab>

  <Tab title="Згадки та користувачі каналів">
    Повідомлення в каналах типово обмежуються згадками.

    Джерела згадок:

    - явна згадка застосунку (`<@botId>`)
    - шаблони regex для згадок (`agents.list[].groupChat.mentionPatterns`, резервне значення `messages.groupChat.mentionPatterns`)
    - неявна поведінка reply-to-bot у треді

    Керування для кожного каналу (`channels.slack.channels.<id>`; імена лише через визначення під час запуску або `dangerouslyAllowNameMatching`):

    - `requireMention`
    - `users` (allowlist)
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - формат ключів `toolsBySender`: `id:`, `e164:`, `username:`, `name:` або підстановочний знак `"*"`
      (застарілі ключі без префікса все ще зіставляються лише з `id:`)

  </Tab>
</Tabs>

## Треди, сесії та теги відповідей

- Особисті повідомлення маршрутизуються як `direct`; канали — як `channel`; MPIM — як `group`.
- Із типовим `session.dmScope=main` особисті повідомлення Slack згортаються до основної сесії агента.
- Сесії каналів: `agent:<agentId>:slack:channel:<channelId>`.
- Відповіді в треді можуть створювати суфікси сесій тредів (`:thread:<threadTs>`), якщо це застосовно.
- Типове значення `channels.slack.thread.historyScope` — `thread`; типове значення `thread.inheritParent` — `false`.
- `channels.slack.thread.initialHistoryLimit` визначає, скільки наявних повідомлень треду буде отримано під час запуску нової сесії треду (типово `20`; установіть `0`, щоб вимкнути).

Параметри тредів відповідей:

- `channels.slack.replyToMode`: `off|first|all|batched` (типово `off`)
- `channels.slack.replyToModeByChatType`: для `direct|group|channel`
- застаріле резервне значення для прямих чатів: `channels.slack.dm.replyToMode`

Підтримуються ручні теги відповідей:

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

Примітка: `replyToMode="off"` вимикає **усі** треди відповідей у Slack, включно з явними тегами `[[reply_to_*]]`. Це відрізняється від Telegram, де явні теги все ще враховуються в режимі `"off"`. Різниця відображає моделі тредів на цих платформах: у Slack треди приховують повідомлення з каналу, тоді як у Telegram відповіді лишаються видимими в основному потоці чату.

## Реакції-підтвердження

`ackReaction` надсилає emoji-підтвердження, поки OpenClaw обробляє вхідне повідомлення.

Порядок визначення:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- резервне значення emoji ідентичності агента (`agents.list[].identity.emoji`, інакше "👀")

Примітки:

- Slack очікує короткі коди (наприклад, `"eyes"`).
- Використовуйте `""`, щоб вимкнути реакцію для облікового запису Slack або глобально.

## Потокова передача тексту

`channels.slack.streaming` контролює поведінку попереднього перегляду в реальному часі:

- `off`: вимкнути потоковий попередній перегляд у реальному часі.
- `partial` (типово): замінювати текст попереднього перегляду останнім частковим результатом.
- `block`: додавати фрагментовані оновлення попереднього перегляду.
- `progress`: показувати текст стану прогресу під час генерації, а потім надсилати фінальний текст.

`channels.slack.nativeStreaming` контролює вбудовану потокову передачу тексту Slack, коли `streaming` має значення `partial` (типово: `true`).

- Щоб з'явилася вбудована потокова передача тексту, має бути доступний тред відповіді. Вибір треду й далі визначається `replyToMode`. Без нього використовується звичайний чернетковий попередній перегляд.
- Для медіа та нетекстових payload використовується звичайна доставка.
- Якщо потокова передача переривається посеред відповіді, OpenClaw повертається до звичайної доставки для решти payload.

Використовуйте чернетковий попередній перегляд замість вбудованої потокової передачі тексту Slack:

```json5
{
  channels: {
    slack: {
      streaming: "partial",
      nativeStreaming: false,
    },
  },
}
```

Застарілі ключі:

- `channels.slack.streamMode` (`replace | status_final | append`) автоматично мігрується до `channels.slack.streaming`.
- булеве значення `channels.slack.streaming` автоматично мігрується до `channels.slack.nativeStreaming`.

## Резервна реакція друку

`typingReaction` додає тимчасову реакцію до вхідного повідомлення Slack, поки OpenClaw обробляє відповідь, а потім видаляє її після завершення виконання. Це особливо корисно поза відповідями в тредах, де використовується типовий індикатор стану "друкує...".

Порядок визначення:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

Примітки:

- Slack очікує короткі коди (наприклад, `"hourglass_flowing_sand"`).
- Реакція виконується за принципом best-effort, а очищення автоматично намагається завершитися після відповіді або завершення шляху помилки.

## Медіа, розбиття на частини та доставка

<AccordionGroup>
  <Accordion title="Вхідні вкладення">
    Вкладення файлів Slack завантажуються з приватних URL, розміщених у Slack (потік запитів з автентифікацією токеном), і записуються до сховища медіа, якщо отримання успішне та дозволяють обмеження за розміром.

    Типове обмеження розміру вхідних даних під час виконання — `20MB`, якщо його не перевизначено через `channels.slack.mediaMaxMb`.

  </Accordion>

  <Accordion title="Вихідний текст і файли">
    - текстові частини використовують `channels.slack.textChunkLimit` (типово 4000)
    - `channels.slack.chunkMode="newline"` вмикає розбиття спершу за абзацами
    - надсилання файлів використовує API завантаження Slack і може включати відповіді в тредах (`thread_ts`)
    - обмеження вихідних медіа визначається через `channels.slack.mediaMaxMb`, якщо налаштовано; інакше надсилання в канали використовує типові MIME-обмеження з медіаконвеєра
  </Accordion>

  <Accordion title="Цілі доставки">
    Рекомендовані явні цілі:

    - `user:<id>` для особистих повідомлень
    - `channel:<id>` для каналів

    Особисті повідомлення Slack відкриваються через API розмов Slack під час надсилання до цілей користувача.

  </Accordion>
</AccordionGroup>

## Команди та поведінка slash-команд

- Вбудований автоматичний режим команд для Slack **вимкнено** (`commands.native: "auto"` не вмикає вбудовані команди Slack).
- Увімкніть вбудовані обробники команд Slack через `channels.slack.commands.native: true` (або глобально `commands.native: true`).
- Коли вбудовані команди ввімкнено, зареєструйте відповідні slash-команди в Slack (імена `/<command>`), з одним винятком:
  - зареєструйте `/agentstatus` для команди стану (Slack резервує `/status`)
- Якщо вбудовані команди не ввімкнено, ви можете виконувати одну налаштовану slash-команду через `channels.slack.slashCommand`.
- Вбудовані меню аргументів тепер адаптують свою стратегію відображення:
  - до 5 варіантів: блоки кнопок
  - 6-100 варіантів: статичне меню вибору
  - більше 100 варіантів: зовнішній вибір з асинхронною фільтрацією варіантів, якщо доступні обробники параметрів interactivity
  - якщо закодовані значення варіантів перевищують ліміти Slack, потік повертається до кнопок
- Для довгих payload варіантів меню аргументів slash-команд використовують діалог підтвердження перед передачею вибраного значення.

Типові параметри slash-команд:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

Сесії slash-команд використовують ізольовані ключі:

- `agent:<agentId>:slack:slash:<userId>`

і все одно спрямовують виконання команд до сесії цільової розмови (`CommandTargetSessionKey`).

## Інтерактивні відповіді

Slack може відображати інтерактивні елементи відповідей, створених агентом, але ця функція типово вимкнена.

Увімкніть її глобально:

```json5
{
  channels: {
    slack: {
      capabilities: {
        interactiveReplies: true,
      },
    },
  },
}
```

Або увімкніть лише для одного облікового запису Slack:

```json5
{
  channels: {
    slack: {
      accounts: {
        ops: {
          capabilities: {
            interactiveReplies: true,
          },
        },
      },
    },
  },
}
```

Коли функцію ввімкнено, агенти можуть виводити директиви відповідей лише для Slack:

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

Ці директиви компілюються в Slack Block Kit і повертають натискання або вибір назад через наявний шлях подій взаємодії Slack.

Примітки:

- Це UI, специфічний для Slack. Інші канали не перекладають директиви Slack Block Kit у власні системи кнопок.
- Значення інтерактивних callback — це непрозорі токени, згенеровані OpenClaw, а не сирі значення, створені агентом.
- Якщо згенеровані інтерактивні блоки перевищують обмеження Slack Block Kit, OpenClaw повертається до початкової текстової відповіді замість надсилання невалідного payload blocks.

## Підтвердження exec у Slack

Slack може виступати як вбудований клієнт підтвердження з інтерактивними кнопками та взаємодіями замість повернення до Web UI або термінала.

- Підтвердження exec використовують `channels.slack.execApprovals.*` для вбудованої маршрутизації в особисті повідомлення/канали.
- Підтвердження plugin також можуть визначатися через ту саму вбудовану поверхню кнопок Slack, коли запит уже надходить у Slack, а тип ідентифікатора підтвердження — `plugin:`.
- Авторизація затверджувачів і далі примусово застосовується: лише користувачі, визначені як затверджувачі, можуть схвалювати або відхиляти запити через Slack.

Для цього використовується та сама спільна поверхня кнопок підтвердження, що й для інших каналів. Коли у налаштуваннях застосунку Slack увімкнено `interactivity`, запити на підтвердження відображаються як кнопки Block Kit безпосередньо в розмові.
Коли ці кнопки присутні, вони є основним UX підтвердження; OpenClaw
має включати ручну команду `/approve` лише тоді, коли результат інструмента вказує, що підтвердження в чаті недоступні або ручне підтвердження є єдиним шляхом.

Шлях конфігурації:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers` (необов'язково; за можливості використовується резервне значення `commands.ownerAllowFrom`)
- `channels.slack.execApprovals.target` (`dm` | `channel` | `both`, типово: `dm`)
- `agentFilter`, `sessionFilter`

Slack автоматично вмикає вбудовані підтвердження exec, коли `enabled` не задано або має значення `"auto"` і визначається принаймні один
затверджувач. Установіть `enabled: false`, щоб явно вимкнути Slack як вбудований клієнт підтвердження.
Установіть `enabled: true`, щоб примусово ввімкнути вбудовані підтвердження, коли затверджувачі визначаються.

Типова поведінка без явної конфігурації підтверджень exec для Slack:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

Явна вбудована конфігурація Slack потрібна лише тоді, коли ви хочете перевизначити затверджувачів, додати фільтри або
використовувати доставку в початковий чат:

```json5
{
  channels: {
    slack: {
      execApprovals: {
        enabled: true,
        approvers: ["U12345678"],
        target: "both",
      },
    },
  },
}
```

Спільне переспрямування `approvals.exec` є окремим. Використовуйте його лише тоді, коли запити на підтвердження exec також мають
маршрутизуватися до інших чатів або явно позасмугових цілей. Спільне переспрямування `approvals.plugin` також є
окремим; вбудовані кнопки Slack все одно можуть визначати підтвердження plugin, коли ці запити вже надходять
у Slack.

У Slack-каналах і особистих повідомленнях, які вже підтримують команди, також працює `/approve` у тому самому чаті. Повну модель переспрямування підтверджень див. у [Підтвердження exec](/uk/tools/exec-approvals).

## Події та поведінка під час роботи

- Редагування/видалення повідомлень і thread broadcast відображаються в системні події.
- Події додавання/видалення реакцій відображаються в системні події.
- Події входу/виходу учасників, створення/перейменування каналу та додавання/видалення закріплень відображаються в системні події.
- `channel_id_changed` може мігрувати ключі конфігурації каналу, якщо ввімкнено `configWrites`.
- Метадані topic/purpose каналу вважаються недовіреним контекстом і можуть бути впроваджені в контекст маршрутизації.
- Початкове повідомлення треду та початкове заповнення контексту історії треду фільтруються за налаштованими allowlist відправників, якщо це застосовно.
- Дії блоків і взаємодії модальних вікон створюють структуровані системні події `Slack interaction: ...` із розширеними полями payload:
  - дії блоків: вибрані значення, мітки, значення picker і метадані `workflow_*`
  - події модальних вікон `view_submission` і `view_closed` з маршрутованими метаданими каналу та полями форм

## Вказівники на довідник конфігурації

Основний довідник:

- [Довідник конфігурації - Slack](/uk/gateway/configuration-reference#slack)

  Найважливіші поля Slack:
  - mode/auth: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - доступ до особистих повідомлень: `dm.enabled`, `dmPolicy`, `allowFrom` (застаріле: `dm.policy`, `dm.allowFrom`), `dm.groupEnabled`, `dm.groupChannels`
  - перемикач сумісності: `dangerouslyAllowNameMatching` (аварійний режим; тримайте вимкненим, якщо не потрібно)
  - доступ до каналів: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - треди/історія: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - доставка: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - операції/можливості: `configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## Усунення проблем

<AccordionGroup>
  <Accordion title="Немає відповідей у каналах">
    Перевірте в такому порядку:

    - `groupPolicy`
    - allowlist каналів (`channels.slack.channels`)
    - `requireMention`
    - allowlist `users` для конкретного каналу

    Корисні команди:

```bash
openclaw channels status --probe
openclaw logs --follow
openclaw doctor
```

  </Accordion>

  <Accordion title="Повідомлення в особистих повідомленнях ігноруються">
    Перевірте:

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy` (або застаріле `channels.slack.dm.policy`)
    - підтвердження сполучення / записи allowlist

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Режим Socket не підключається">
    Перевірте токени бота й застосунку та увімкнення Socket Mode в налаштуваннях застосунку Slack.

    Якщо `openclaw channels status --probe --json` показує `botTokenStatus` або
    `appTokenStatus: "configured_unavailable"`, обліковий запис Slack
    налаштовано, але поточне середовище виконання не змогло визначити значення,
    що зберігається через SecretRef.

  </Accordion>

  <Accordion title="HTTP-режим не отримує події">
    Перевірте:

    - signing secret
    - шлях webhook
    - Slack Request URL (Events + Interactivity + Slash Commands)
    - унікальний `webhookPath` для кожного HTTP-облікового запису

    Якщо `signingSecretStatus: "configured_unavailable"` з'являється у знімках
    облікового запису, HTTP-обліковий запис налаштовано, але поточне середовище виконання не змогло
    визначити signing secret, що зберігається через SecretRef.

  </Accordion>

  <Accordion title="Вбудовані/slash-команди не спрацьовують">
    Перевірте, що саме ви мали на увазі:

    - режим вбудованих команд (`channels.slack.commands.native: true`) з відповідними зареєстрованими в Slack slash-командами
    - або режим однієї slash-команди (`channels.slack.slashCommand.enabled: true`)

    Також перевірте `commands.useAccessGroups` і allowlist каналів/користувачів.

  </Accordion>
</AccordionGroup>

## Пов'язане

- [Сполучення](/uk/channels/pairing)
- [Групи](/uk/channels/groups)
- [Безпека](/uk/gateway/security)
- [Маршрутизація каналів](/uk/channels/channel-routing)
- [Усунення проблем](/uk/channels/troubleshooting)
- [Конфігурація](/uk/gateway/configuration)
- [Slash-команди](/uk/tools/slash-commands)
