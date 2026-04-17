---
read_when:
    - Реалізація або оновлення клієнтів Gateway WS
    - Налагодження невідповідностей протоколу або збоїв підключення
    - Повторне генерування схеми/моделей протоколу
summary: 'Протокол Gateway WebSocket: рукостискання, кадри, керування версіями'
title: Протокол Gateway
x-i18n:
    generated_at: "2026-04-17T07:50:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4f0eebcfdd8c926c90b4753a6d96c59e3134ddb91740f65478f11eb75be85e41
    source_path: gateway/protocol.md
    workflow: 15
---

# Протокол Gateway (WebSocket)

Протокол Gateway WS — це **єдина площина керування + транспорт вузлів** для
OpenClaw. Усі клієнти (CLI, веб-інтерфейс, застосунок macOS, вузли iOS/Android,
безголові вузли) підключаються через WebSocket і оголошують свою **роль** +
**область** під час рукостискання.

## Транспорт

- WebSocket, текстові кадри з JSON-навантаженнями.
- Перший кадр **має** бути запитом `connect`.

## Рукостискання (connect)

Gateway → Client (виклик до підключення):

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

Client → Gateway:

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

Gateway → Client:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": {
    "type": "hello-ok",
    "protocol": 3,
    "server": { "version": "…", "connId": "…" },
    "features": { "methods": ["…"], "events": ["…"] },
    "snapshot": { "…": "…" },
    "policy": {
      "maxPayload": 26214400,
      "maxBufferedBytes": 52428800,
      "tickIntervalMs": 15000
    }
  }
}
```

`server`, `features`, `snapshot` і `policy` є обов’язковими згідно зі схемою
(`src/gateway/protocol/schema/frames.ts`). `canvasHostUrl` є необов’язковим. `auth`
повідомляє про узгоджені роль/області, коли вони доступні, а також містить `deviceToken`,
коли gateway його видає.

Коли токен пристрою не видається, `hello-ok.auth` усе одно може повідомляти про узгоджені
дозволи:

```json
{
  "auth": {
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

Коли токен пристрою видається, `hello-ok` також містить:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

Під час передавання довіреного bootstrap `hello-ok.auth` також може містити додаткові
обмежені записи ролей у `deviceTokens`:

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

Для вбудованого bootstrap-потоку node/operator основний токен вузла зберігає
`scopes: []`, а будь-який переданий токен оператора залишається обмеженим списком дозволів
bootstrap-оператора (`operator.approvals`, `operator.read`,
`operator.talk.secrets`, `operator.write`). Перевірки областей bootstrap і надалі
залишаються прив’язаними до префікса ролі: записи operator задовольняють лише запити operator, а ролі,
що не є operator, усе одно потребують областей під власним префіксом ролі.

### Приклад Node

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

## Формат кадрів

- **Запит**: `{type:"req", id, method, params}`
- **Відповідь**: `{type:"res", id, ok, payload|error}`
- **Подія**: `{type:"event", event, payload, seq?, stateVersion?}`

Методи з побічними ефектами вимагають **ключів ідемпотентності** (див. схему).

## Ролі + області

### Ролі

- `operator` = клієнт площини керування (CLI/UI/автоматизація).
- `node` = хост можливостей (camera/screen/canvas/system.run).

### Області (operator)

Поширені області:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

`talk.config` з `includeSecrets: true` вимагає `operator.talk.secrets`
(або `operator.admin`).

Методи Gateway RPC, зареєстровані Plugin, можуть запитувати власну область operator, але
зарезервовані префікси core admin (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) завжди зіставляються з `operator.admin`.

Область методу — це лише перший рівень перевірки. Деякі slash-команди, викликані через
`chat.send`, додатково застосовують суворіші перевірки на рівні команд. Наприклад, сталі
записи `/config set` і `/config unset` вимагають `operator.admin`.

`node.pair.approve` також має додаткову перевірку області під час схвалення поверх
базової області методу:

- запити без команди: `operator.pairing`
- запити з невиконавчими node-командами: `operator.pairing` + `operator.write`
- запити, що містять `system.run`, `system.run.prepare` або `system.which`:
  `operator.pairing` + `operator.admin`

### Caps/commands/permissions (node)

Вузли оголошують заявлені можливості під час підключення:

- `caps`: високорівневі категорії можливостей.
- `commands`: allowlist команд для invoke.
- `permissions`: детальні перемикачі (наприклад, `screen.record`, `camera.capture`).

Gateway сприймає їх як **заяви** і застосовує серверні allowlist.

## Присутність

- `system-presence` повертає записи, ключовані за ідентичністю пристрою.
- Записи присутності містять `deviceId`, `roles` і `scopes`, щоб UI могли показувати один рядок на пристрій,
  навіть якщо він підключається і як **operator**, і як **node**.

## Поширені сімейства методів RPC

Ця сторінка не є згенерованим повним дампом, але публічна поверхня WS ширша,
ніж наведені вище приклади рукостискання/автентифікації. Ось основні сімейства методів,
які Gateway надає сьогодні.

`hello-ok.features.methods` — це консервативний список виявлення, зібраний із
`src/gateway/server-methods-list.ts` плюс експортів методів завантажених plugin/channel.
Сприймайте його як виявлення можливостей, а не як згенерований дамп кожного доступного helper,
реалізованого в `src/gateway/server-methods/*.ts`.

### Система та ідентичність

- `health` повертає кешований або щойно перевірений знімок стану gateway.
- `status` повертає зведення gateway у стилі `/status`; чутливі поля
  включаються лише для operator-клієнтів з admin-областю.
- `gateway.identity.get` повертає ідентичність пристрою gateway, яка використовується в потоках relay і
  pairing.
- `system-presence` повертає поточний знімок присутності підключених
  пристроїв operator/node.
- `system-event` додає системну подію та може оновлювати/транслювати контекст
  присутності.
- `last-heartbeat` повертає останню збережену подію Heartbeat.
- `set-heartbeats` перемикає обробку Heartbeat на gateway.

### Моделі та використання

- `models.list` повертає каталог моделей, дозволених у runtime.
- `usage.status` повертає зведення вікон використання постачальників/залишкової квоти.
- `usage.cost` повертає агреговані зведення вартості використання за діапазон дат.
- `doctor.memory.status` повертає готовність векторної пам’яті / embedding для
  активного робочого простору агента за замовчуванням.
- `sessions.usage` повертає зведення використання по сесіях.
- `sessions.usage.timeseries` повертає часовий ряд використання для однієї сесії.
- `sessions.usage.logs` повертає записи журналу використання для однієї сесії.

### Канали та helper для входу

- `channels.status` повертає зведення стану вбудованих і комплектних channel/plugin.
- `channels.logout` виконує вихід із певного каналу/облікового запису, якщо канал
  підтримує вихід.
- `web.login.start` запускає потік входу через QR/web для поточного QR-сумісного веб-
  постачальника каналу.
- `web.login.wait` очікує завершення цього потоку входу через QR/web і запускає
  канал у разі успіху.
- `push.test` надсилає тестовий APNs push до зареєстрованого вузла iOS.
- `voicewake.get` повертає збережені тригери wake-word.
- `voicewake.set` оновлює тригери wake-word і транслює зміну.

### Повідомлення та журнали

- `send` — це прямий RPC вихідної доставки для
  надсилань, адресованих channel/account/thread, поза chat runner.
- `logs.tail` повертає tail налаштованого файлу журналу gateway з cursor/limit і
  елементами керування максимальною кількістю байтів.

### Talk і TTS

- `talk.config` повертає ефективне навантаження конфігурації Talk; `includeSecrets`
  вимагає `operator.talk.secrets` (або `operator.admin`).
- `talk.mode` встановлює/транслює поточний стан режиму Talk для клієнтів WebChat/Control UI.
- `talk.speak` синтезує мовлення через активного постачальника мовлення Talk.
- `tts.status` повертає стан увімкнення TTS, активного постачальника, резервних постачальників
  і стан конфігурації постачальника.
- `tts.providers` повертає видимий інвентар постачальників TTS.
- `tts.enable` і `tts.disable` перемикають стан налаштувань TTS.
- `tts.setProvider` оновлює бажаного постачальника TTS.
- `tts.convert` виконує одноразове перетворення тексту на мовлення.

### Секрети, конфігурація, оновлення та wizard

- `secrets.reload` повторно розв’язує активні SecretRef і змінює стан секретів runtime
  лише за повного успіху.
- `secrets.resolve` розв’язує призначення секретів для конкретного
  набору команд/цілей.
- `config.get` повертає поточний знімок конфігурації та хеш.
- `config.set` записує валідоване навантаження конфігурації.
- `config.patch` зливає часткове оновлення конфігурації.
- `config.apply` валідує та замінює повне навантаження конфігурації.
- `config.schema` повертає payload схеми живої конфігурації, який використовують Control UI та
  інструменти CLI: схема, `uiHints`, версія та метадані генерації, включно з
  метаданими схем plugin + channel, коли runtime може їх завантажити. Схема
  містить метадані полів `title` / `description`, похідні від тих самих підписів
  і довідкового тексту, що використовуються в UI, включно з вкладеними об’єктами,
  wildcard, елементами масиву та гілками композиції `anyOf` / `oneOf` / `allOf`,
  коли існує відповідна документація поля.
- `config.schema.lookup` повертає payload пошуку в межах одного шляху конфігурації:
  нормалізований шлях, поверхневий вузол схеми, відповідний hint + `hintPath` і
  зведення безпосередніх дочірніх елементів для деталізації в UI/CLI.
  - Вузли схеми пошуку зберігають користувацьку документацію та поширені поля валідації:
    `title`, `description`, `type`, `enum`, `const`, `format`, `pattern`,
    числові/рядкові/масивні/об’єктні межі та булеві прапори, як-от
    `additionalProperties`, `deprecated`, `readOnly`, `writeOnly`.
  - Зведення дочірніх елементів містять `key`, нормалізований `path`, `type`, `required`,
    `hasChildren`, а також відповідні `hint` / `hintPath`.
- `update.run` запускає потік оновлення gateway і планує перезапуск лише тоді,
  коли саме оновлення завершилося успішно.
- `wizard.start`, `wizard.next`, `wizard.status` і `wizard.cancel` надають
  onboarding wizard через WS RPC.

### Наявні основні сімейства

#### Helper агента та робочого простору

- `agents.list` повертає налаштовані записи агентів.
- `agents.create`, `agents.update` і `agents.delete` керують записами агентів і
  підключенням робочого простору.
- `agents.files.list`, `agents.files.get` і `agents.files.set` керують файлами
  bootstrap-робочого простору, доступними для агента.
- `agent.identity.get` повертає ефективну ідентичність помічника для агента або
  сесії.
- `agent.wait` очікує завершення запуску й повертає термінальний знімок, коли
  він доступний.

#### Керування сесією

- `sessions.list` повертає поточний індекс сесій.
- `sessions.subscribe` і `sessions.unsubscribe` перемикають підписки на події
  зміни сесій для поточного WS-клієнта.
- `sessions.messages.subscribe` і `sessions.messages.unsubscribe` перемикають
  підписки на події transcript/message для однієї сесії.
- `sessions.preview` повертає обмежені попередні перегляди transcript для вказаних
  ключів сесій.
- `sessions.resolve` розв’язує або канонізує ціль сесії.
- `sessions.create` створює новий запис сесії.
- `sessions.send` надсилає повідомлення в наявну сесію.
- `sessions.steer` — це варіант переривання й спрямування для активної сесії.
- `sessions.abort` перериває активну роботу для сесії.
- `sessions.patch` оновлює метадані/перевизначення сесії.
- `sessions.reset`, `sessions.delete` і `sessions.compact` виконують
  обслуговування сесій.
- `sessions.get` повертає повний збережений рядок сесії.
- виконання чату й надалі використовує `chat.history`, `chat.send`, `chat.abort` і
  `chat.inject`.
- `chat.history` нормалізується для відображення для UI-клієнтів: вбудовані теги директив
  прибираються з видимого тексту, XML-навантаження викликів інструментів у звичайному тексті (включно з
  `<tool_call>...</tool_call>`, `<function_call>...</function_call>`,
  `<tool_calls>...</tool_calls>`, `<function_calls>...</function_calls>` і
  усіченими блоками викликів інструментів) та витеклі ASCII/повноширинні токени керування моделі
  прибираються, чисті рядки помічника з безшумними токенами, як-от точне `NO_REPLY` /
  `no_reply`, пропускаються, а надто великі рядки можуть замінюватися заповнювачами.

#### Pairing пристроїв і токени пристроїв

- `device.pair.list` повертає очікувальні та схвалені спарені пристрої.
- `device.pair.approve`, `device.pair.reject` і `device.pair.remove` керують
  записами pairing пристроїв.
- `device.token.rotate` ротує токен спареного пристрою в межах його схваленої ролі
  та обмежень областей.
- `device.token.revoke` відкликає токен спареного пристрою.

#### Pairing вузлів, invoke і відкладена робота

- `node.pair.request`, `node.pair.list`, `node.pair.approve`,
  `node.pair.reject` і `node.pair.verify` охоплюють pairing вузлів і bootstrap-
  перевірку.
- `node.list` і `node.describe` повертають стан відомих/підключених вузлів.
- `node.rename` оновлює мітку спареного вузла.
- `node.invoke` пересилає команду підключеному вузлу.
- `node.invoke.result` повертає результат для запиту invoke.
- `node.event` переносить події, що походять від вузла, назад у gateway.
- `node.canvas.capability.refresh` оновлює токени можливостей canvas з обмеженою областю.
- `node.pending.pull` і `node.pending.ack` — це API черги підключеного вузла.
- `node.pending.enqueue` і `node.pending.drain` керують стійкою відкладеною роботою
  для офлайн/відключених вузлів.

#### Сімейства схвалення

- `exec.approval.request`, `exec.approval.get`, `exec.approval.list` і
  `exec.approval.resolve` охоплюють одноразові запити на схвалення exec плюс
  пошук/повторення очікувальних схвалень.
- `exec.approval.waitDecision` очікує рішення щодо одного очікувального схвалення exec і повертає
  фінальне рішення (або `null` у разі тайм-ауту).
- `exec.approvals.get` і `exec.approvals.set` керують знімками політики
  схвалення exec gateway.
- `exec.approvals.node.get` і `exec.approvals.node.set` керують локальною для вузла exec-
  політикою схвалення через relay-команди вузла.
- `plugin.approval.request`, `plugin.approval.list`,
  `plugin.approval.waitDecision` і `plugin.approval.resolve` охоплюють
  потоки схвалення, визначені Plugin.

#### Інші основні сімейства

- automation:
  - `wake` планує негайне або наступне введення тексту пробудження Heartbeat
  - `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`,
    `cron.run`, `cron.runs`
- skills/tools: `commands.list`, `skills.*`, `tools.catalog`, `tools.effective`

### Поширені сімейства подій

- `chat`: оновлення чату UI, такі як `chat.inject` та інші
  події чату лише для transcript.
- `session.message` і `session.tool`: оновлення transcript/event-stream для
  сесії, на яку оформлено підписку.
- `sessions.changed`: індекс сесій або метадані змінилися.
- `presence`: оновлення знімка системної присутності.
- `tick`: періодична подія keepalive / liveness.
- `health`: оновлення знімка стану gateway.
- `heartbeat`: оновлення потоку подій Heartbeat.
- `cron`: подія зміни запуску/завдання cron.
- `shutdown`: сповіщення про вимкнення gateway.
- `node.pair.requested` / `node.pair.resolved`: життєвий цикл pairing вузла.
- `node.invoke.request`: трансляція запиту invoke вузла.
- `device.pair.requested` / `device.pair.resolved`: життєвий цикл спареного пристрою.
- `voicewake.changed`: змінено конфігурацію тригерів wake-word.
- `exec.approval.requested` / `exec.approval.resolved`: життєвий цикл
  схвалення exec.
- `plugin.approval.requested` / `plugin.approval.resolved`: життєвий цикл схвалення
  Plugin.

### Helper-методи вузла

- Вузли можуть викликати `skills.bins`, щоб отримати поточний список виконуваних файлів skill
  для перевірок auto-allow.

### Helper-методи operator

- Operator можуть викликати `commands.list` (`operator.read`), щоб отримати
  інвентар команд runtime для агента.
  - `agentId` є необов’язковим; опустіть його, щоб читати робочий простір агента за замовчуванням.
  - `scope` керує тим, яку поверхню використовує основний `name`:
    - `text` повертає основний текстовий токен команди без початкового `/`
    - `native` і типовий шлях `both` повертають обізнані про постачальника native-імена,
      коли вони доступні
  - `textAliases` містить точні slash-аліаси, такі як `/model` і `/m`.
  - `nativeName` містить обізнане про постачальника native-ім’я команди, якщо воно існує.
  - `provider` є необов’язковим і впливає лише на native-іменування та доступність native-команд
    Plugin.
  - `includeArgs=false` пропускає серіалізовані метадані аргументів із відповіді.
- Operator можуть викликати `tools.catalog` (`operator.read`), щоб отримати каталог інструментів runtime для
  агента. Відповідь містить згруповані інструменти та метадані походження:
  - `source`: `core` або `plugin`
  - `pluginId`: власник Plugin, коли `source="plugin"`
  - `optional`: чи є інструмент Plugin необов’язковим
- Operator можуть викликати `tools.effective` (`operator.read`), щоб отримати ефективний у runtime
  інвентар інструментів для сесії.
  - `sessionKey` є обов’язковим.
  - Gateway виводить довірений контекст runtime із сесії на сервері замість того, щоб приймати
    наданий викликачем контекст auth або доставки.
  - Відповідь прив’язана до сесії та відображає те, що активна розмова може використовувати просто зараз,
    включно з інструментами core, Plugin і channel.
- Operator можуть викликати `skills.status` (`operator.read`), щоб отримати видимий
  інвентар Skills для агента.
  - `agentId` є необов’язковим; опустіть його, щоб читати робочий простір агента за замовчуванням.
  - Відповідь містить придатність, відсутні вимоги, перевірки конфігурації та
    санітизовані параметри встановлення без розкриття сирих значень секретів.
- Operator можуть викликати `skills.search` і `skills.detail` (`operator.read`) для
  метаданих виявлення ClawHub.
- Operator можуть викликати `skills.install` (`operator.admin`) у двох режимах:
  - Режим ClawHub: `{ source: "clawhub", slug, version?, force? }` встановлює
    теку skill у каталог `skills/` робочого простору агента за замовчуванням.
  - Режим встановлювача Gateway: `{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    запускає оголошену дію `metadata.openclaw.install` на хості gateway.
- Operator можуть викликати `skills.update` (`operator.admin`) у двох режимах:
  - Режим ClawHub оновлює один відстежуваний slug або всі відстежувані встановлення ClawHub у
    робочому просторі агента за замовчуванням.
  - Режим Config вносить зміни до значень `skills.entries.<skillKey>`, таких як `enabled`,
    `apiKey` і `env`.

## Схвалення exec

- Коли запит exec потребує схвалення, gateway транслює `exec.approval.requested`.
- Клієнти operator виконують підтвердження, викликаючи `exec.approval.resolve` (потрібна область `operator.approvals`).
- Для `host=node` `exec.approval.request` має містити `systemRunPlan` (канонічні `argv`/`cwd`/`rawCommand`/метадані сесії). Запити без `systemRunPlan` відхиляються.
- Після схвалення переслані виклики `node.invoke system.run` повторно використовують цей канонічний
  `systemRunPlan` як авторитетний контекст команди/cwd/сесії.
- Якщо викликач змінює `command`, `rawCommand`, `cwd`, `agentId` або
  `sessionKey` між підготовкою та фінальним пересиланням схваленого `system.run`,
  gateway відхиляє запуск замість того, щоб довіряти зміненому payload.

## Резервна доставка агента

- Запити `agent` можуть містити `deliver=true`, щоб запитати вихідну доставку.
- `bestEffortDeliver=false` зберігає строгий режим: нерозв’язані або лише внутрішні цілі доставки повертають `INVALID_REQUEST`.
- `bestEffortDeliver=true` дозволяє резервний перехід до виконання лише в межах сесії, коли неможливо визначити зовнішній маршрут доставки (наприклад, для внутрішніх/вебчат-сесій або неоднозначних багатоканальних конфігурацій).

## Керування версіями

- `PROTOCOL_VERSION` міститься в `src/gateway/protocol/schema/protocol-schemas.ts`.
- Клієнти надсилають `minProtocol` + `maxProtocol`; сервер відхиляє невідповідності.
- Схеми + моделі генеруються з визначень TypeBox:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

### Константи клієнта

Еталонний клієнт у `src/gateway/client.ts` використовує ці значення за замовчуванням. Вони
сталі в межах протоколу v3 і є очікуваною базою для сторонніх клієнтів.

| Константа                                 | Значення за замовчуванням                              | Джерело                                                    |
| ----------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------- |
| `PROTOCOL_VERSION`                        | `3`                                                    | `src/gateway/protocol/schema/protocol-schemas.ts`          |
| Тайм-аут запиту (на RPC)                  | `30_000` ms                                            | `src/gateway/client.ts` (`requestTimeoutMs`)               |
| Тайм-аут preauth / connect-challenge      | `10_000` ms                                            | `src/gateway/handshake-timeouts.ts` (clamp `250`–`10_000`) |
| Початковий backoff повторного підключення | `1_000` ms                                             | `src/gateway/client.ts` (`backoffMs`)                      |
| Максимальний backoff повторного підключення | `30_000` ms                                          | `src/gateway/client.ts` (`scheduleReconnect`)              |
| Обмеження швидкого повтору після закриття device-token | `250` ms                                    | `src/gateway/client.ts`                                    |
| Grace-період примусової зупинки перед `terminate()` | `250` ms                                     | `FORCE_STOP_TERMINATE_GRACE_MS`                            |
| Тайм-аут за замовчуванням для `stopAndWait()` | `1_000` ms                                         | `STOP_AND_WAIT_TIMEOUT_MS`                                 |
| Типовий інтервал tick (до `hello-ok`)     | `30_000` ms                                            | `src/gateway/client.ts`                                    |
| Закриття через тайм-аут tick              | код `4000`, коли тиша перевищує `tickIntervalMs * 2`   | `src/gateway/client.ts`                                    |
| `MAX_PAYLOAD_BYTES`                       | `25 * 1024 * 1024` (25 MB)                             | `src/gateway/server-constants.ts`                          |

Сервер оголошує ефективні `policy.tickIntervalMs`, `policy.maxPayload`
і `policy.maxBufferedBytes` у `hello-ok`; клієнти повинні дотримуватися цих значень,
а не типових значень до рукостискання.

## Автентифікація

- Автентифікація gateway через спільний секрет використовує `connect.params.auth.token` або
  `connect.params.auth.password`, залежно від налаштованого режиму автентифікації.
- Режими з ідентичністю, як-от Tailscale Serve
  (`gateway.auth.allowTailscale: true`) або не-loopback
  `gateway.auth.mode: "trusted-proxy"`, проходять перевірку автентифікації connect на основі
  заголовків запиту замість `connect.params.auth.*`.
- `gateway.auth.mode: "none"` для приватного ingress повністю пропускає автентифікацію connect через спільний секрет; не відкривайте цей режим на публічному/ненадійному ingress.
- Після pairing Gateway видає **токен пристрою**, обмежений роллю + областями
  підключення. Він повертається в `hello-ok.auth.deviceToken` і має
  зберігатися клієнтом для майбутніх підключень.
- Клієнти мають зберігати основний `hello-ok.auth.deviceToken` після будь-якого
  успішного підключення.
- Під час повторного підключення з цим **збереженим** токеном пристрою також слід повторно використовувати збережений
  набір схвалених областей для цього токена. Це зберігає вже наданий доступ на
  читання/probe/status і не дає повторним підключенням непомітно звузитися до
  вужчої неявної області лише для admin.
- Збирання автентифікації connect на боці клієнта (`selectConnectAuth` у
  `src/gateway/client.ts`):
  - `auth.password` є ортогональним і завжди пересилається, якщо його встановлено.
  - `auth.token` заповнюється в такому порядку пріоритету: спочатку явний спільний токен,
    далі явний `deviceToken`, потім збережений токен для пристрою (із ключем за
    `deviceId` + `role`).
  - `auth.bootstrapToken` надсилається лише тоді, коли жоден із наведених вище варіантів не визначив
    `auth.token`. Спільний токен або будь-який визначений токен пристрою його приглушує.
  - Автоматичне підвищення збереженого токена пристрою під час одноразового
    повтору `AUTH_TOKEN_MISMATCH` дозволено лише для **довірених endpoint** —
    loopback або `wss://` із закріпленим `tlsFingerprint`. Публічний `wss://`
    без pinning не підходить.
- Додаткові записи `hello-ok.auth.deviceTokens` — це токени передавання bootstrap.
  Зберігайте їх лише тоді, коли підключення використовувало bootstrap-автентифікацію на довіреному транспорті,
  такому як `wss://` або loopback/local pairing.
- Якщо клієнт надає **явний** `deviceToken` або явні `scopes`, цей
  набір областей, запитаний викликачем, залишається авторитетним; кешовані області повторно використовуються лише тоді, коли клієнт повторно використовує збережений токен конкретного пристрою.
- Токени пристроїв можна ротувати/відкликати через `device.token.rotate` і
  `device.token.revoke` (потрібна область `operator.pairing`).
- Видача/ротація токенів і надалі обмежується схваленим набором ролей, записаним у
  записі pairing цього пристрою; ротація токена не може розширити пристрій до
  ролі, яку схвалення pairing ніколи не надавало.
- Для сесій із токеном спареного пристрою керування пристроєм прив’язане до власного контексту, якщо
  викликач також не має `operator.admin`: не-admin викликачі можуть видаляти/відкликати/ротувати
  лише **власний** запис пристрою.
- `device.token.rotate` також перевіряє запитаний набір областей operator щодо
  поточних областей сесії викликача. Не-admin викликачі не можуть ротувати токен до
  ширшого набору областей operator, ніж вони вже мають.
- Помилки автентифікації містять `error.details.code` плюс підказки для відновлення:
  - `error.details.canRetryWithDeviceToken` (boolean)
  - `error.details.recommendedNextStep` (`retry_with_device_token`, `update_auth_configuration`, `update_auth_credentials`, `wait_then_retry`, `review_auth_configuration`)
- Поведінка клієнта для `AUTH_TOKEN_MISMATCH`:
  - Довірені клієнти можуть виконати одну обмежену повторну спробу з кешованим токеном конкретного пристрою.
  - Якщо ця повторна спроба не вдалася, клієнти мають зупинити автоматичні цикли повторного підключення й показати вказівки для дій оператора.

## Ідентичність пристрою + pairing

- Вузли мають включати стабільну ідентичність пристрою (`device.id`), похідну від
  відбитка keypair.
- Gateway видають токени для кожного поєднання пристрій + роль.
- Для нових `device.id` потрібне схвалення pairing, якщо не увімкнено локальне автоматичне схвалення.
- Автоматичне схвалення pairing зосереджене на прямих локальних loopback-підключеннях.
- OpenClaw також має вузький шлях self-connect для trusted shared-secret helper flows у backend/container-local.
- Підключення tailnet або LAN з того самого хоста все одно вважаються віддаленими для pairing і
  потребують схвалення.
- Усі WS-клієнти мають включати ідентичність `device` під час `connect` (і operator, і node).
  Control UI може її пропускати лише в таких режимах:
  - `gateway.controlUi.allowInsecureAuth=true` для сумісності з небезпечним HTTP лише для localhost.
  - успішна автентифікація operator Control UI з `gateway.auth.mode: "trusted-proxy"`.
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true` (аварійний режим, серйозне зниження безпеки).
- Усі підключення мають підписувати наданий сервером nonce `connect.challenge`.

### Діагностика міграції автентифікації пристрою

Для застарілих клієнтів, які все ще використовують поведінку підписування до challenge, `connect` тепер повертає
коди деталей `DEVICE_AUTH_*` у `error.details.code` зі стабільним `error.details.reason`.

Поширені збої міграції:

| Повідомлення                 | details.code                     | details.reason           | Значення                                             |
| ---------------------------- | -------------------------------- | ------------------------ | ---------------------------------------------------- |
| `device nonce required`      | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | Клієнт пропустив `device.nonce` (або надіслав порожнє значення). |
| `device nonce mismatch`      | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | Клієнт підписав застарілим/неправильним nonce.       |
| `device signature invalid`   | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | Навантаження підпису не відповідає payload v2.       |
| `device signature expired`   | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | Підписана часова позначка виходить за межі дозволеного зміщення. |
| `device identity mismatch`   | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id` не відповідає відбитку публічного ключа. |
| `device public key invalid`  | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | Формат/канонізація публічного ключа не вдалися.      |

Ціль міграції:

- Завжди чекайте на `connect.challenge`.
- Підписуйте payload v2, який включає nonce сервера.
- Надсилайте той самий nonce у `connect.params.device.nonce`.
- Бажане навантаження підпису — `v3`, яке прив’язує `platform` і `deviceFamily`
  на додачу до полів device/client/role/scopes/token/nonce.
- Застарілі підписи `v2` і надалі приймаються для сумісності, але pinning метаданих
  спареного пристрою все одно керує політикою команд під час повторного підключення.

## TLS + pinning

- TLS підтримується для WS-підключень.
- Клієнти можуть за бажанням закріпити відбиток сертифіката gateway (див. конфігурацію `gateway.tls`
  плюс `gateway.remote.tlsFingerprint` або CLI `--tls-fingerprint`).

## Область

Цей протокол надає **повний API gateway** (status, channels, models, chat,
agent, sessions, nodes, approvals тощо). Точна поверхня визначається
схемами TypeBox у `src/gateway/protocol/schema.ts`.
