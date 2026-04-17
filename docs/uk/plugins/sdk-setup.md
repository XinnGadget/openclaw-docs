---
read_when:
    - Ви додаєте майстер налаштування до Plugin
    - Вам потрібно зрозуміти різницю між setup-entry.ts і index.ts
    - Ви визначаєте схеми конфігурації Plugin або метадані openclaw у package.json
sidebarTitle: Setup and Config
summary: Майстри налаштування, setup-entry.ts, схеми конфігурації та метадані package.json
title: Налаштування Plugin та конфігурація
x-i18n:
    generated_at: "2026-04-15T16:36:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: ddf28e25e381a4a38ac478e531586f59612e1a278732597375f87c2eeefc521b
    source_path: plugins/sdk-setup.md
    workflow: 15
---

# Налаштування Plugin та конфігурація

Довідка щодо пакування plugin (`package.json` metadata), маніфестів
(`openclaw.plugin.json`), записів налаштування та схем конфігурації.

<Tip>
  **Шукаєте покроковий приклад?** Практичні посібники охоплюють пакування в контексті:
  [Channel Plugins](/uk/plugins/sdk-channel-plugins#step-1-package-and-manifest) і
  [Provider Plugins](/uk/plugins/sdk-provider-plugins#step-1-package-and-manifest).
</Tip>

## Метадані пакунка

Ваш `package.json` має містити поле `openclaw`, яке повідомляє системі plugin, що саме
надає ваш plugin:

**Channel plugin:**

```json
{
  "name": "@myorg/openclaw-my-channel",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "blurb": "Short description of the channel."
    }
  }
}
```

**Provider plugin / базовий шаблон публікації ClawHub:**

```json openclaw-clawhub-package.json
{
  "name": "@myorg/openclaw-my-plugin",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
    "compat": {
      "pluginApi": ">=2026.3.24-beta.2",
      "minGatewayVersion": "2026.3.24-beta.2"
    },
    "build": {
      "openclawVersion": "2026.3.24-beta.2",
      "pluginSdkVersion": "2026.3.24-beta.2"
    }
  }
}
```

Якщо ви публікуєте plugin зовнішньо в ClawHub, поля `compat` і `build`
є обов’язковими. Канонічні фрагменти для публікації знаходяться в
`docs/snippets/plugin-publish/`.

### Поля `openclaw`

| Поле         | Тип        | Опис                                                                                                   |
| ------------ | ---------- | ------------------------------------------------------------------------------------------------------ |
| `extensions` | `string[]` | Файли точок входу (відносно кореня пакунка)                                                            |
| `setupEntry` | `string`   | Полегшена точка входу лише для налаштування (необов’язково)                                            |
| `channel`    | `object`   | Метадані каталогу channel для налаштування, вибору, швидкого старту та поверхонь статусу              |
| `providers`  | `string[]` | Ідентифікатори provider, зареєстрованих цим plugin                                                     |
| `install`    | `object`   | Підказки встановлення: `npmSpec`, `localPath`, `defaultChoice`, `minHostVersion`, `allowInvalidConfigRecovery` |
| `startup`    | `object`   | Прапори поведінки під час запуску                                                                      |

### `openclaw.channel`

`openclaw.channel` — це недорогі метадані пакунка для виявлення channel і поверхонь
налаштування до завантаження runtime.

| Поле                                   | Тип        | Що це означає                                                                |
| -------------------------------------- | ---------- | ---------------------------------------------------------------------------- |
| `id`                                   | `string`   | Канонічний ідентифікатор channel.                                            |
| `label`                                | `string`   | Основна мітка channel.                                                       |
| `selectionLabel`                       | `string`   | Мітка у виборі/налаштуванні, якщо вона має відрізнятися від `label`.         |
| `detailLabel`                          | `string`   | Додаткова детальна мітка для багатших каталогів channel і поверхонь статусу. |
| `docsPath`                             | `string`   | Шлях до документації для посилань у налаштуванні та виборі.                  |
| `docsLabel`                            | `string`   | Перевизначення мітки для посилань на документацію, якщо вона має відрізнятися від ідентифікатора channel. |
| `blurb`                                | `string`   | Короткий опис для онбордингу/каталогу.                                       |
| `order`                                | `number`   | Порядок сортування в каталогах channel.                                      |
| `aliases`                              | `string[]` | Додаткові псевдоніми для пошуку під час вибору channel.                      |
| `preferOver`                           | `string[]` | Ідентифікатори plugin/channel з нижчим пріоритетом, які цей channel має випереджати. |
| `systemImage`                          | `string`   | Необов’язкова назва піктограми/system-image для каталогів UI channel.        |
| `selectionDocsPrefix`                  | `string`   | Текст-префікс перед посиланнями на документацію в поверхнях вибору.          |
| `selectionDocsOmitLabel`               | `boolean`  | Показувати шлях документації безпосередньо замість підписаного посилання в тексті вибору. |
| `selectionExtras`                      | `string[]` | Додаткові короткі рядки, що додаються в тексті вибору.                       |
| `markdownCapable`                      | `boolean`  | Позначає channel як сумісний з markdown для рішень щодо вихідного форматування. |
| `exposure`                             | `object`   | Керування видимістю channel для налаштування, списків налаштованих елементів і поверхонь документації. |
| `quickstartAllowFrom`                  | `boolean`  | Додає цей channel до стандартного потоку налаштування quickstart `allowFrom`. |
| `forceAccountBinding`                  | `boolean`  | Вимагає явної прив’язки облікового запису, навіть якщо існує лише один обліковий запис. |
| `preferSessionLookupForAnnounceTarget` | `boolean`  | Віддавати перевагу пошуку сесії під час визначення цілей announce для цього channel. |

Приклад:

```json
{
  "openclaw": {
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "selectionLabel": "My Channel (self-hosted)",
      "detailLabel": "My Channel Bot",
      "docsPath": "/channels/my-channel",
      "docsLabel": "my-channel",
      "blurb": "Webhook-based self-hosted chat integration.",
      "order": 80,
      "aliases": ["mc"],
      "preferOver": ["my-channel-legacy"],
      "selectionDocsPrefix": "Guide:",
      "selectionExtras": ["Markdown"],
      "markdownCapable": true,
      "exposure": {
        "configured": true,
        "setup": true,
        "docs": true
      },
      "quickstartAllowFrom": true
    }
  }
}
```

`exposure` підтримує:

- `configured`: включати channel у поверхні списків налаштованих елементів/статусів
- `setup`: включати channel в інтерактивні засоби вибору налаштування/конфігурації
- `docs`: позначати channel як публічно видимий у поверхнях документації/навігації

`showConfigured` і `showInSetup` залишаються підтримуваними як застарілі псевдоніми. Рекомендовано
використовувати `exposure`.

### `openclaw.install`

`openclaw.install` — це метадані пакунка, а не метадані маніфесту.

| Поле                         | Тип                  | Що це означає                                                                   |
| ---------------------------- | -------------------- | ------------------------------------------------------------------------------- |
| `npmSpec`                    | `string`             | Канонічний npm spec для потоків встановлення/оновлення.                         |
| `localPath`                  | `string`             | Локальний шлях встановлення для розробки або вбудованого пакета.                |
| `defaultChoice`              | `"npm"` \| `"local"` | Бажане джерело встановлення, коли доступні обидва варіанти.                     |
| `minHostVersion`             | `string`             | Мінімально підтримувана версія OpenClaw у форматі `>=x.y.z`.                    |
| `allowInvalidConfigRecovery` | `boolean`            | Дозволяє потокам перевстановлення вбудованого plugin відновлюватися після окремих збоїв через застарілу конфігурацію. |

Якщо задано `minHostVersion`, і встановлення, і завантаження реєстру маніфестів
застосовують цю перевірку. Старіші хости пропускають plugin; некоректні рядки версій відхиляються.

`allowInvalidConfigRecovery` не є загальним обходом для зламаних конфігурацій. Воно
призначене лише для вузького сценарію відновлення вбудованого plugin, щоб перевстановлення/налаштування
могли виправити відомі залишки після оновлення, як-от відсутній шлях до вбудованого plugin або застарілий запис `channels.<id>`
для цього самого plugin. Якщо конфігурація зламана з інших причин, встановлення
усе одно завершується з відмовою і пропонує оператору виконати `openclaw doctor --fix`.

### Відкладене повне завантаження

Channel plugins можуть увімкнути відкладене завантаження так:

```json
{
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

Коли це ввімкнено, OpenClaw завантажує лише `setupEntry` під час фази запуску до
початку прослуховування, навіть для вже налаштованих channel. Повна точка входу завантажується після того,
як Gateway починає прослуховування.

<Warning>
  Увімкнюйте відкладене завантаження лише тоді, коли ваш `setupEntry` реєструє все,
  що Gateway потрібно до початку прослуховування (реєстрація channel, HTTP-маршрути,
  методи Gateway). Якщо повна точка входу володіє потрібними можливостями запуску, залиште
  поведінку за замовчуванням.
</Warning>

Якщо ваш запис налаштування/повний запис реєструє методи Gateway RPC, використовуйте для них
префікс, специфічний для plugin. Зарезервовані простори імен основного адміністратора (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) залишаються під керуванням core і завжди зіставляються
з `operator.admin`.

## Маніфест Plugin

Кожен native plugin має постачати `openclaw.plugin.json` у корені пакунка.
OpenClaw використовує це для перевірки конфігурації без виконання коду plugin.

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "description": "Adds My Plugin capabilities to OpenClaw",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "webhookSecret": {
        "type": "string",
        "description": "Webhook verification secret"
      }
    }
  }
}
```

Для channel plugins додайте `kind` і `channels`:

```json
{
  "id": "my-channel",
  "kind": "channel",
  "channels": ["my-channel"],
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

Навіть plugins без конфігурації мають постачати схему. Порожня схема є валідною:

```json
{
  "id": "my-plugin",
  "configSchema": {
    "type": "object",
    "additionalProperties": false
  }
}
```

Див. [Plugin Manifest](/uk/plugins/manifest) для повної довідки щодо схеми.

## Публікація в ClawHub

Для пакунків plugin використовуйте команду ClawHub, специфічну для пакунків:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

Застарілий псевдонім публікації лише для Skills призначений для skills. Пакунки plugin
завжди мають використовувати `clawhub package publish`.

## Точка входу налаштування

Файл `setup-entry.ts` — це полегшена альтернатива `index.ts`, яку
OpenClaw завантажує, коли йому потрібні лише поверхні налаштування (онбординг, відновлення конфігурації,
перевірка вимкненого channel).

```typescript
// setup-entry.ts
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
import { myChannelPlugin } from "./src/channel.js";

export default defineSetupPluginEntry(myChannelPlugin);
```

Це дає змогу уникнути завантаження важкого runtime-коду (криптографічних бібліотек, реєстрацій CLI,
фонових сервісів) під час потоків налаштування.

Вбудовані workspace channel, які тримають безпечні для налаштування експорти в sidecar-модулях, можуть
використовувати `defineBundledChannelSetupEntry(...)` з
`openclaw/plugin-sdk/channel-entry-contract` замість
`defineSetupPluginEntry(...)`. Цей вбудований контракт також підтримує необов’язковий експорт
`runtime`, щоб підключення runtime під час налаштування залишалося полегшеним і явним.

**Коли OpenClaw використовує `setupEntry` замість повної точки входу:**

- Channel вимкнено, але потрібні поверхні налаштування/онбордингу
- Channel увімкнено, але не налаштовано
- Увімкнено відкладене завантаження (`deferConfiguredChannelFullLoadUntilAfterListen`)

**Що має реєструвати `setupEntry`:**

- Об’єкт channel plugin (через `defineSetupPluginEntry`)
- Будь-які HTTP-маршрути, потрібні до початку прослуховування Gateway
- Будь-які методи Gateway, потрібні під час запуску

Ці методи Gateway для запуску все одно мають уникати зарезервованих
просторів імен core admin, таких як `config.*` або `update.*`.

**Що НЕ має містити `setupEntry`:**

- Реєстрації CLI
- Фонові сервіси
- Важкі імпорти runtime (crypto, SDKs)
- Методи Gateway, потрібні лише після запуску

### Вузькі імпорти допоміжних засобів налаштування

Для гарячих шляхів лише для налаштування надавайте перевагу вузьким швам допоміжних засобів налаштування замість ширшого
парасолькового `plugin-sdk/setup`, коли вам потрібна лише частина поверхні налаштування:

| Шлях імпорту                      | Для чого використовувати                                                                  | Ключові експорти                                                                                                                                                                                                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/setup-runtime`        | допоміжні засоби runtime під час налаштування, які лишаються доступними в `setupEntry` / відкладеному запуску channel | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
| `plugin-sdk/setup-adapter-runtime` | адаптери налаштування облікових записів з урахуванням середовища                          | `createEnvPatchedAccountSetupAdapter`                                                                                                                                                                                                                                                        |
| `plugin-sdk/setup-tools`          | допоміжні засоби CLI/архіву/документації для налаштування та встановлення                 | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR`                                                                                                                                                                              |

Використовуйте ширший шов `plugin-sdk/setup`, коли вам потрібен повний спільний
набір інструментів для налаштування, включно з допоміжними засобами patch для конфігурації, такими як
`moveSingleAccountChannelSectionToDefaultAccount(...)`.

Адаптери patch для налаштування залишаються безпечними для гарячого шляху під час імпорту. Їхній вбудований
ледачий пошук поверхні контракту для просування одного облікового запису є відкладеним, тому імпорт
`plugin-sdk/setup-runtime` не завантажує завчасно виявлення поверхні вбудованого контракту до фактичного використання адаптера.

### Просування одного облікового запису, що належить channel

Коли channel оновлюється з верхньорівневої конфігурації одного облікового запису до
`channels.<id>.accounts.*`, типова спільна поведінка полягає в переміщенні значень,
що належать області облікового запису, до `accounts.default`.

Вбудовані channels можуть звузити або перевизначити це просування через свою
поверхню контракту налаштування:

- `singleAccountKeysToMove`: додаткові верхньорівневі ключі, які потрібно перемістити до
  просунутого облікового запису
- `namedAccountPromotionKeys`: якщо іменовані облікові записи вже існують, лише ці
  ключі переміщуються до просунутого облікового запису; спільні ключі policy/delivery залишаються в корені
  channel
- `resolveSingleAccountPromotionTarget(...)`: вибір наявного облікового запису, який
  отримає просунуті значення

Matrix — поточний вбудований приклад. Якщо вже існує рівно один іменований обліковий запис Matrix,
або якщо `defaultAccount` вказує на наявний неканонічний ключ
на кшталт `Ops`, просування зберігає цей обліковий запис замість створення нового
запису `accounts.default`.

## Схема конфігурації

Конфігурація plugin проходить перевірку за JSON Schema у вашому маніфесті. Користувачі
налаштовують plugins через:

```json5
{
  plugins: {
    entries: {
      "my-plugin": {
        config: {
          webhookSecret: "abc123",
        },
      },
    },
  },
}
```

Ваш plugin отримує цю конфігурацію як `api.pluginConfig` під час реєстрації.

Для конфігурації, специфічної для channel, використовуйте натомість розділ конфігурації channel:

```json5
{
  channels: {
    "my-channel": {
      token: "bot-token",
      allowFrom: ["user1", "user2"],
    },
  },
}
```

### Побудова схем конфігурації channel

Використовуйте `buildChannelConfigSchema` з `openclaw/plugin-sdk/core`, щоб перетворити
схему Zod на обгортку `ChannelConfigSchema`, яку перевіряє OpenClaw:

```typescript
import { z } from "zod";
import { buildChannelConfigSchema } from "openclaw/plugin-sdk/core";

const accountSchema = z.object({
  token: z.string().optional(),
  allowFrom: z.array(z.string()).optional(),
  accounts: z.object({}).catchall(z.any()).optional(),
  defaultAccount: z.string().optional(),
});

const configSchema = buildChannelConfigSchema(accountSchema);
```

## Майстри налаштування

Channel plugins можуть надавати інтерактивні майстри налаштування для `openclaw onboard`.
Майстер — це об’єкт `ChannelSetupWizard` у `ChannelPlugin`:

```typescript
import type { ChannelSetupWizard } from "openclaw/plugin-sdk/channel-setup";

const setupWizard: ChannelSetupWizard = {
  channel: "my-channel",
  status: {
    configuredLabel: "Connected",
    unconfiguredLabel: "Not configured",
    resolveConfigured: ({ cfg }) => Boolean((cfg.channels as any)?.["my-channel"]?.token),
  },
  credentials: [
    {
      inputKey: "token",
      providerHint: "my-channel",
      credentialLabel: "Bot token",
      preferredEnvVar: "MY_CHANNEL_BOT_TOKEN",
      envPrompt: "Use MY_CHANNEL_BOT_TOKEN from environment?",
      keepPrompt: "Keep current token?",
      inputPrompt: "Enter your bot token:",
      inspect: ({ cfg, accountId }) => {
        const token = (cfg.channels as any)?.["my-channel"]?.token;
        return {
          accountConfigured: Boolean(token),
          hasConfiguredValue: Boolean(token),
        };
      },
    },
  ],
};
```

Тип `ChannelSetupWizard` підтримує `credentials`, `textInputs`,
`dmPolicy`, `allowFrom`, `groupAccess`, `prepare`, `finalize` тощо.
Повні приклади дивіться у вбудованих пакунках plugin (наприклад, у plugin Discord `src/channel.setup.ts`).

Для запитів allowlist у DM, яким потрібен лише стандартний
потік `note -> prompt -> parse -> merge -> patch`, надавайте перевагу спільним допоміжним засобам налаштування
з `openclaw/plugin-sdk/setup`: `createPromptParsedAllowFromForAccount(...)`,
`createTopLevelChannelParsedAllowFromPrompt(...)` і
`createNestedChannelParsedAllowFromPrompt(...)`.

Для блоків статусу налаштування channel, які відрізняються лише мітками, оцінками та необов’язковими
додатковими рядками, надавайте перевагу `createStandardChannelSetupStatus(...)` з
`openclaw/plugin-sdk/setup` замість ручного створення того самого об’єкта `status` у
кожному plugin.

Для необов’язкових поверхонь налаштування, які мають з’являтися лише в певних контекстах, використовуйте
`createOptionalChannelSetupSurface` з `openclaw/plugin-sdk/channel-setup`:

```typescript
import { createOptionalChannelSetupSurface } from "openclaw/plugin-sdk/channel-setup";

const setupSurface = createOptionalChannelSetupSurface({
  channel: "my-channel",
  label: "My Channel",
  npmSpec: "@myorg/openclaw-my-channel",
  docsPath: "/channels/my-channel",
});
// Returns { setupAdapter, setupWizard }
```

`plugin-sdk/channel-setup` також надає низькорівневі
конструктори `createOptionalChannelSetupAdapter(...)` і
`createOptionalChannelSetupWizard(...)`, коли вам потрібна лише одна половина
цієї необов’язкової поверхні встановлення.

Згенеровані необов’язкові adapter/wizard завершуються з відмовою для реальних записів конфігурації. Вони
повторно використовують одне повідомлення про обов’язковість встановлення в `validateInput`,
`applyAccountConfig` і `finalize`, а також додають посилання на документацію, якщо задано `docsPath`.

Для UI налаштування, що спираються на двійкові файли, надавайте перевагу спільним делегованим допоміжним засобам замість
копіювання однакового glue-коду для binary/status у кожен channel:

- `createDetectedBinaryStatus(...)` для блоків статусу, що відрізняються лише мітками,
  підказками, оцінками та виявленням двійкового файла
- `createCliPathTextInput(...)` для текстових полів, прив’язаних до шляху
- `createDelegatedSetupWizardStatusResolvers(...)`,
  `createDelegatedPrepare(...)`, `createDelegatedFinalize(...)` і
  `createDelegatedResolveConfigured(...)`, коли `setupEntry` має ледачо пересилати до
  важчого повного майстра
- `createDelegatedTextInputShouldPrompt(...)`, коли `setupEntry` потрібно лише
  делегувати рішення `textInputs[*].shouldPrompt`

## Публікація та встановлення

**Зовнішні plugins:** публікуйте в [ClawHub](/uk/tools/clawhub) або npm, а потім встановлюйте:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

OpenClaw спочатку пробує ClawHub і автоматично переходить до npm у разі невдачі. Ви також можете
явно примусово використати ClawHub:

```bash
openclaw plugins install clawhub:@myorg/openclaw-my-plugin   # лише ClawHub
```

Відповідного перевизначення `npm:` не існує. Використовуйте звичайний npm package spec, коли
потрібен шлях npm після fallback із ClawHub:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

**Plugins у репозиторії:** розміщуйте їх у дереві workspace вбудованих plugin, і вони будуть автоматично
виявлені під час збірки.

**Користувачі можуть встановлювати:**

```bash
openclaw plugins install <package-name>
```

<Info>
  Для встановлень із npm `openclaw plugins install` виконує
  `npm install --ignore-scripts` (без lifecycle scripts). Зберігайте дерева залежностей plugin
  чистими JS/TS і уникайте пакунків, які потребують збірки через `postinstall`.
</Info>

## Пов’язане

- [SDK Entry Points](/uk/plugins/sdk-entrypoints) -- `definePluginEntry` і `defineChannelPluginEntry`
- [Plugin Manifest](/uk/plugins/manifest) -- повна довідка щодо схеми маніфесту
- [Building Plugins](/uk/plugins/building-plugins) -- покроковий посібник для початку роботи
