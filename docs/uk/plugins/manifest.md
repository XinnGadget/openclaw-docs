---
read_when:
    - Ви створюєте plugin для OpenClaw
    - Вам потрібно надати схему конфігурації plugin або налагодити помилки валідації plugin
summary: Вимоги до маніфесту Plugin + JSON schema (сувора валідація конфігурації)
title: Маніфест Plugin
x-i18n:
    generated_at: "2026-04-12T09:53:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: 08745ead2c2ab83e56dc041ec3187deead6f0439cb8c8423db03c2e3f5c78e9e
    source_path: plugins/manifest.md
    workflow: 15
---

# Маніфест Plugin (`openclaw.plugin.json`)

Ця сторінка стосується лише **власного маніфесту Plugin для OpenClaw**.

Сумісні компонування пакетів описано в [Plugin bundles](/uk/plugins/bundles).

Сумісні формати пакетів використовують інші файли маніфесту:

- Пакет Codex: `.codex-plugin/plugin.json`
- Пакет Claude: `.claude-plugin/plugin.json` або стандартне компонування компонентів Claude
  без маніфесту
- Пакет Cursor: `.cursor-plugin/plugin.json`

OpenClaw також автоматично виявляє ці компонування пакетів, але вони не проходять валідацію
відповідно до схеми `openclaw.plugin.json`, описаної тут.

Для сумісних пакетів OpenClaw наразі читає метадані пакета разом з оголошеними
коренями skill, коренями команд Claude, типовими значеннями `settings.json` для пакетів Claude,
типовими значеннями LSP для пакетів Claude та підтримуваними наборами hook, коли компонування відповідає
очікуванням середовища виконання OpenClaw.

Кожен власний Plugin для OpenClaw **повинен** містити файл `openclaw.plugin.json` у
**корені plugin**. OpenClaw використовує цей маніфест для валідації конфігурації
**без виконання коду plugin**. Відсутні або невалідні маніфести вважаються
помилками plugin і блокують валідацію конфігурації.

Дивіться повний посібник із системи plugin: [Plugins](/uk/tools/plugin).
Для власної моделі capability та поточних вказівок щодо зовнішньої сумісності:
[Модель capability](/uk/plugins/architecture#public-capability-model).

## Що робить цей файл

`openclaw.plugin.json` — це метадані, які OpenClaw читає перед завантаженням коду
вашого plugin.

Використовуйте його для:

- ідентифікації plugin
- валідації конфігурації
- метаданих auth і onboarding, які мають бути доступні без запуску середовища виконання plugin
- недорогих підказок активації, які поверхні control-plane можуть перевіряти до завантаження runtime
- недорогих дескрипторів налаштування, які поверхні setup/onboarding можуть перевіряти до
  завантаження runtime
- метаданих alias та auto-enable, які мають визначатися до завантаження runtime plugin
- скорочених метаданих володіння сімействами моделей, які мають автоматично активувати
  plugin до завантаження runtime
- статичних знімків володіння capability, що використовуються для вбудованої compat-обв’язки та
  перевірки контрактів
- метаданих конфігурації, специфічних для channel, які мають об’єднуватися в каталог і поверхні
  валідації без завантаження runtime
- підказок UI для конфігурації

Не використовуйте його для:

- реєстрації поведінки runtime
- оголошення entrypoint коду
- метаданих встановлення npm

Для цього призначені код вашого plugin і `package.json`.

## Мінімальний приклад

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## Розширений приклад

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "OpenRouter provider plugin",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "OpenRouter API key",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter API key",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## Довідник полів верхнього рівня

| Поле                                | Обов’язкове | Тип                              | Що воно означає                                                                                                                                                                                              |
| ----------------------------------- | ----------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Так         | `string`                         | Канонічний id plugin. Це id, який використовується в `plugins.entries.<id>`.                                                                                                                                |
| `configSchema`                      | Так         | `object`                         | Вбудована JSON Schema для конфігурації цього plugin.                                                                                                                                                         |
| `enabledByDefault`                  | Ні          | `true`                           | Позначає вбудований plugin як увімкнений за замовчуванням. Пропустіть це поле або встановіть будь-яке значення, відмінне від `true`, щоб plugin залишався вимкненим за замовчуванням.                     |
| `legacyPluginIds`                   | Ні          | `string[]`                       | Застарілі id, які нормалізуються до цього канонічного id plugin.                                                                                                                                             |
| `autoEnableWhenConfiguredProviders` | Ні          | `string[]`                       | id provider, які мають автоматично вмикати цей plugin, коли auth, config або посилання на модель згадують їх.                                                                                               |
| `kind`                              | Ні          | `"memory"` \| `"context-engine"` | Оголошує ексклюзивний тип plugin, що використовується `plugins.slots.*`.                                                                                                                                     |
| `channels`                          | Ні          | `string[]`                       | id channel, якими володіє цей plugin. Використовується для виявлення та валідації конфігурації.                                                                                                             |
| `providers`                         | Ні          | `string[]`                       | id provider, якими володіє цей plugin.                                                                                                                                                                       |
| `modelSupport`                      | Ні          | `object`                         | Скорочені метадані сімейств моделей, якими володіє маніфест і які використовуються для автоматичного завантаження plugin до runtime.                                                                        |
| `cliBackends`                       | Ні          | `string[]`                       | id backend CLI, якими володіє цей plugin. Використовується для автоматичної активації під час запуску на основі явних посилань у config.                                                                    |
| `commandAliases`                    | Ні          | `object[]`                       | Імена команд, якими володіє цей plugin і які мають формувати діагностику config і CLI з урахуванням plugin до завантаження runtime.                                                                        |
| `providerAuthEnvVars`               | Ні          | `Record<string, string[]>`       | Недорогі метадані змінних середовища для auth provider, які OpenClaw може перевіряти без завантаження коду plugin.                                                                                          |
| `providerAuthAliases`               | Ні          | `Record<string, string>`         | id provider, які мають повторно використовувати інший id provider для пошуку auth, наприклад coding-provider, який спільно використовує базовий API key provider та профілі auth.                         |
| `channelEnvVars`                    | Ні          | `Record<string, string[]>`       | Недорогі метадані змінних середовища для channel, які OpenClaw може перевіряти без завантаження коду plugin. Використовуйте це для setup channel через env або поверхонь auth, які мають бачити загальні helpers startup/config. |
| `providerAuthChoices`               | Ні          | `object[]`                       | Недорогі метадані варіантів auth для засобів вибору в onboarding, визначення preferred-provider і простої обв’язки прапорців CLI.                                                                           |
| `activation`                        | Ні          | `object`                         | Недорогі підказки активації для завантаження, яке запускається provider, командою, channel, маршрутом або capability. Лише метадані; фактична поведінка, як і раніше, належить runtime plugin.            |
| `setup`                             | Ні          | `object`                         | Недорогі дескриптори setup/onboarding, які поверхні виявлення та налаштування можуть перевіряти без завантаження runtime plugin.                                                                            |
| `contracts`                         | Ні          | `object`                         | Статичний знімок вбудованих capability для speech, realtime transcription, realtime voice, media-understanding, image-generation, music-generation, video-generation, web-fetch, web search і володіння tools. |
| `channelConfigs`                    | Ні          | `Record<string, object>`         | Метадані конфігурації channel, якими володіє маніфест і які об’єднуються в поверхні виявлення та валідації до завантаження runtime.                                                                         |
| `skills`                            | Ні          | `string[]`                       | Каталоги Skills для завантаження, відносно кореня plugin.                                                                                                                                                    |
| `name`                              | Ні          | `string`                         | Зрозуміла людині назва plugin.                                                                                                                                                                               |
| `description`                       | Ні          | `string`                         | Короткий опис, що показується в поверхнях plugin.                                                                                                                                                            |
| `version`                           | Ні          | `string`                         | Інформаційна версія plugin.                                                                                                                                                                                  |
| `uiHints`                           | Ні          | `Record<string, object>`         | Підписи UI, placeholders і підказки щодо чутливості для полів конфігурації.                                                                                                                                  |

## Довідник `providerAuthChoices`

Кожен запис `providerAuthChoices` описує один варіант onboarding або auth.
OpenClaw читає це до завантаження runtime provider.

| Поле                  | Обов’язкове | Тип                                             | Що воно означає                                                                                          |
| --------------------- | ----------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `provider`            | Так         | `string`                                        | id provider, до якого належить цей варіант.                                                              |
| `method`              | Так         | `string`                                        | id методу auth, до якого слід маршрутизувати.                                                            |
| `choiceId`            | Так         | `string`                                        | Стабільний id варіанта auth, який використовується в потоках onboarding і CLI.                           |
| `choiceLabel`         | Ні          | `string`                                        | Підпис для користувача. Якщо поле пропущено, OpenClaw використовує `choiceId`.                           |
| `choiceHint`          | Ні          | `string`                                        | Короткий допоміжний текст для засобу вибору.                                                             |
| `assistantPriority`   | Ні          | `number`                                        | Менші значення сортуються раніше в інтерактивних засобах вибору, керованих асистентом.                  |
| `assistantVisibility` | Ні          | `"visible"` \| `"manual-only"`                  | Приховує варіант у засобах вибору асистента, але все одно дозволяє ручний вибір через CLI.              |
| `deprecatedChoiceIds` | Ні          | `string[]`                                      | Застарілі id варіантів, які мають перенаправляти користувачів на цей варіант-заміну.                    |
| `groupId`             | Ні          | `string`                                        | Необов’язковий id групи для групування пов’язаних варіантів.                                             |
| `groupLabel`          | Ні          | `string`                                        | Підпис цієї групи для користувача.                                                                       |
| `groupHint`           | Ні          | `string`                                        | Короткий допоміжний текст для групи.                                                                     |
| `optionKey`           | Ні          | `string`                                        | Внутрішній ключ option для простих потоків auth з одним прапорцем.                                       |
| `cliFlag`             | Ні          | `string`                                        | Назва прапорця CLI, наприклад `--openrouter-api-key`.                                                    |
| `cliOption`           | Ні          | `string`                                        | Повна форма option CLI, наприклад `--openrouter-api-key <key>`.                                          |
| `cliDescription`      | Ні          | `string`                                        | Опис, що використовується в довідці CLI.                                                                  |
| `onboardingScopes`    | Ні          | `Array<"text-inference" \| "image-generation">` | У яких поверхнях onboarding має показуватися цей варіант. Якщо поле пропущено, використовується `["text-inference"]` за замовчуванням. |

## Довідник `commandAliases`

Використовуйте `commandAliases`, коли plugin володіє назвою runtime-команди, яку користувачі можуть
помилково помістити в `plugins.allow` або спробувати запустити як кореневу команду CLI. OpenClaw
використовує ці метадані для діагностики без імпорту коду runtime plugin.

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| Поле         | Обов’язкове | Тип               | Що воно означає                                                          |
| ------------ | ----------- | ----------------- | ------------------------------------------------------------------------ |
| `name`       | Так         | `string`          | Назва команди, яка належить цьому plugin.                                |
| `kind`       | Ні          | `"runtime-slash"` | Позначає alias як чат-команду slash, а не кореневу команду CLI.          |
| `cliCommand` | Ні          | `string`          | Пов’язана коренева команда CLI, яку можна запропонувати для операцій CLI, якщо вона існує. |

## Довідник `activation`

Використовуйте `activation`, коли plugin може недорого оголосити, які події control-plane
мають активувати його пізніше.

Цей блок містить лише метадані. Він не реєструє поведінку runtime і не
замінює `register(...)`, `setupEntry` або інші entrypoint runtime/plugin.
Поточні споживачі використовують його як підказку для звуження перед ширшим завантаженням plugin, тому
відсутність метаданих активації зазвичай впливає лише на продуктивність; вона не має
змінювати коректність, поки ще існують застарілі fallback-и володіння маніфестом.

```json
{
  "activation": {
    "onProviders": ["openai"],
    "onCommands": ["models"],
    "onChannels": ["web"],
    "onRoutes": ["gateway-webhook"],
    "onCapabilities": ["provider", "tool"]
  }
}
```

| Поле             | Обов’язкове | Тип                                                  | Що воно означає                                                     |
| ---------------- | ----------- | ---------------------------------------------------- | ------------------------------------------------------------------- |
| `onProviders`    | Ні          | `string[]`                                           | id provider, які мають активувати цей plugin за запитом.            |
| `onCommands`     | Ні          | `string[]`                                           | id команд, які мають активувати цей plugin.                         |
| `onChannels`     | Ні          | `string[]`                                           | id channel, які мають активувати цей plugin.                        |
| `onRoutes`       | Ні          | `string[]`                                           | Типи маршрутів, які мають активувати цей plugin.                    |
| `onCapabilities` | Ні          | `Array<"provider" \| "channel" \| "tool" \| "hook">` | Загальні підказки capability, що використовуються для планування активації control-plane. |

Поточні активні споживачі:

- планування CLI, що запускається командою, використовує як fallback застарілі
  `commandAliases[].cliCommand` або `commandAliases[].name`
- планування setup/runtime, що запускається provider, використовує як fallback застаріле
  володіння `providers[]` і верхньорівневим `cliBackends[]`, коли явні
  метадані активації provider відсутні

## Довідник `setup`

Використовуйте `setup`, коли поверхням setup та onboarding потрібні недорогі метадані plugin,
що належать plugin, до завантаження runtime.

```json
{
  "setup": {
    "providers": [
      {
        "id": "openai",
        "authMethods": ["api-key"],
        "envVars": ["OPENAI_API_KEY"]
      }
    ],
    "cliBackends": ["openai-cli"],
    "configMigrations": ["legacy-openai-auth"],
    "requiresRuntime": false
  }
}
```

Верхньорівневе `cliBackends` залишається валідним і надалі описує backend-и
інференсу CLI. `setup.cliBackends` — це поверхня дескрипторів, специфічна для setup,
для потоків control-plane/setup, які мають залишатися лише метаданими.

Якщо вони присутні, `setup.providers` і `setup.cliBackends` є бажаною
поверхнею пошуку setup у стилі descriptor-first для виявлення setup. Якщо дескриптор лише
звужує кандидатний plugin, а setup все ще потребує багатших hook runtime на етапі setup,
встановіть `requiresRuntime: true` і залиште `setup-api` як
fallback-шлях виконання.

Оскільки пошук setup може виконувати код `setup-api`, що належить plugin,
нормалізовані значення `setup.providers[].id` і `setup.cliBackends[]` мають залишатися унікальними серед
виявлених plugin. Неоднозначне володіння завершується без вибору замість того, щоб
обирати переможця за порядком виявлення.

### Довідник `setup.providers`

| Поле          | Обов’язкове | Тип        | Що воно означає                                                                          |
| ------------- | ----------- | ---------- | ---------------------------------------------------------------------------------------- |
| `id`          | Так         | `string`   | id provider, який відкривається під час setup або onboarding. Зберігайте нормалізовані id глобально унікальними. |
| `authMethods` | Ні          | `string[]` | id методів setup/auth, які цей provider підтримує без завантаження повного runtime.     |
| `envVars`     | Ні          | `string[]` | Змінні середовища, які загальні поверхні setup/status можуть перевіряти до завантаження runtime plugin. |

### Поля `setup`

| Поле               | Обов’язкове | Тип        | Що воно означає                                                                                      |
| ------------------ | ----------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| `providers`        | Ні          | `object[]` | Дескриптори setup provider, що відкриваються під час setup та onboarding.                            |
| `cliBackends`      | Ні          | `string[]` | id backend-ів на етапі setup, що використовуються для пошуку setup у стилі descriptor-first. Зберігайте нормалізовані id глобально унікальними. |
| `configMigrations` | Ні          | `string[]` | id міграцій config, які належать поверхні setup цього plugin.                                        |
| `requiresRuntime`  | Ні          | `boolean`  | Чи потребує setup виконання `setup-api` навіть після пошуку за дескриптором.                         |

## Довідник `uiHints`

`uiHints` — це мапа від назв полів конфігурації до невеликих підказок для відображення.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "help": "Used for OpenRouter requests",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Кожна підказка для поля може містити:

| Поле          | Тип        | Що воно означає                         |
| ------------- | ---------- | -------------------------------------- |
| `label`       | `string`   | Підпис поля для користувача.           |
| `help`        | `string`   | Короткий допоміжний текст.             |
| `tags`        | `string[]` | Необов’язкові UI-теги.                 |
| `advanced`    | `boolean`  | Позначає поле як розширене.            |
| `sensitive`   | `boolean`  | Позначає поле як секретне або чутливе. |
| `placeholder` | `string`   | Текст placeholder для полів форми.     |

## Довідник `contracts`

Використовуйте `contracts` лише для статичних метаданих володіння capability, які OpenClaw може
читати без імпорту runtime plugin.

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

Кожен список є необов’язковим:

| Поле                             | Тип        | Що воно означає                                               |
| -------------------------------- | ---------- | ------------------------------------------------------------- |
| `speechProviders`                | `string[]` | id speech-provider, якими володіє цей plugin.                 |
| `realtimeTranscriptionProviders` | `string[]` | id provider для realtime-transcription, якими володіє цей plugin. |
| `realtimeVoiceProviders`         | `string[]` | id provider для realtime-voice, якими володіє цей plugin.     |
| `mediaUnderstandingProviders`    | `string[]` | id provider для media-understanding, якими володіє цей plugin. |
| `imageGenerationProviders`       | `string[]` | id provider для image-generation, якими володіє цей plugin.   |
| `videoGenerationProviders`       | `string[]` | id provider для video-generation, якими володіє цей plugin.   |
| `webFetchProviders`              | `string[]` | id provider для web-fetch, якими володіє цей plugin.          |
| `webSearchProviders`             | `string[]` | id provider для web-search, якими володіє цей plugin.         |
| `tools`                          | `string[]` | Назви agent tool, якими володіє цей plugin для перевірок вбудованих контрактів. |

## Довідник `channelConfigs`

Використовуйте `channelConfigs`, коли plugin channel потребує недорогих метаданих конфігурації до
завантаження runtime.

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "Homeserver URL",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Matrix homeserver connection",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Кожен запис channel може містити:

| Поле          | Тип                      | Що воно означає                                                                            |
| ------------- | ------------------------ | ------------------------------------------------------------------------------------------ |
| `schema`      | `object`                 | JSON Schema для `channels.<id>`. Обов’язкова для кожного оголошеного запису конфігурації channel. |
| `uiHints`     | `Record<string, object>` | Необов’язкові підписи UI/placeholders/підказки чутливості для цього розділу конфігурації channel. |
| `label`       | `string`                 | Підпис channel, що об’єднується в поверхні вибору та inspect, коли метадані runtime ще не готові. |
| `description` | `string`                 | Короткий опис channel для поверхонь inspect і catalog.                                     |
| `preferOver`  | `string[]`               | id застарілих plugin або plugin з нижчим пріоритетом, які цей channel має випереджати в поверхнях вибору. |

## Довідник `modelSupport`

Використовуйте `modelSupport`, коли OpenClaw має визначати ваш plugin provider за
скороченими id моделей на кшталт `gpt-5.4` або `claude-sonnet-4.6` до завантаження runtime plugin.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw застосовує такий пріоритет:

- явні посилання `provider/model` використовують метадані маніфесту `providers`, що належать відповідному provider
- `modelPatterns` мають вищий пріоритет за `modelPrefixes`
- якщо збігаються один невбудований plugin і один вбудований plugin, перемагає невбудований
  plugin
- решта неоднозначностей ігнорується, доки користувач або config не вкаже provider

Поля:

| Поле            | Тип        | Що воно означає                                                                     |
| --------------- | ---------- | ----------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Префікси, які звіряються через `startsWith` зі скороченими id моделей.             |
| `modelPatterns` | `string[]` | Джерела regex, які звіряються зі скороченими id моделей після видалення суфікса профілю. |

Застарілі ключі capability верхнього рівня застаріли. Використовуйте `openclaw doctor --fix`, щоб
перемістити `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` і `webSearchProviders` під `contracts`; звичайне
завантаження маніфесту більше не трактує ці поля верхнього рівня як
володіння capability.

## Маніфест порівняно з package.json

Ці два файли виконують різні задачі:

| Файл                   | Для чого його використовувати                                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Виявлення, валідація config, метадані варіантів auth і підказки UI, які мають існувати до запуску коду plugin                     |
| `package.json`         | Метадані npm, встановлення залежностей і блок `openclaw`, який використовується для entrypoint, обмежень встановлення, setup або метаданих catalog |

Якщо ви не впевнені, куди має належати певний фрагмент метаданих, використовуйте таке правило:

- якщо OpenClaw має знати це до завантаження коду plugin, помістіть це в `openclaw.plugin.json`
- якщо це стосується пакування, entry-файлів або поведінки встановлення npm, помістіть це в `package.json`

### Поля `package.json`, які впливають на виявлення

Деякі метадані plugin до запуску runtime навмисно зберігаються в `package.json` у блоці
`openclaw`, а не в `openclaw.plugin.json`.

Важливі приклади:

| Поле                                                              | Що воно означає                                                                                                                               |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Оголошує власні entrypoint plugin.                                                                                                            |
| `openclaw.setupEntry`                                             | Легковаговий entrypoint лише для setup, який використовується під час onboarding і відкладеного запуску channel.                             |
| `openclaw.channel`                                                | Недорогі метадані catalog channel, як-от підписи, шляхи до документації, alias і текст для вибору.                                          |
| `openclaw.channel.configuredState`                                | Легковагові метадані перевірки configured-state, які можуть відповісти на запитання «чи вже існує налаштування лише через env?» без завантаження повного runtime channel. |
| `openclaw.channel.persistedAuthState`                             | Легковагові метадані перевірки persisted-auth, які можуть відповісти на запитання «чи вже десь виконано вхід?» без завантаження повного runtime channel. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Підказки встановлення/оновлення для вбудованих і зовнішньо опублікованих plugin.                                                             |
| `openclaw.install.defaultChoice`                                  | Бажаний шлях встановлення, коли доступно кілька джерел встановлення.                                                                          |
| `openclaw.install.minHostVersion`                                 | Мінімальна підтримувана версія хоста OpenClaw із semver-нижньою межею на кшталт `>=2026.3.22`.                                               |
| `openclaw.install.allowInvalidConfigRecovery`                     | Дозволяє вузький шлях відновлення через перевстановлення вбудованого plugin, коли config невалідний.                                         |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Дозволяє завантажувати поверхні channel лише для setup до повного plugin channel під час startup.                                            |

`openclaw.install.minHostVersion` застосовується під час встановлення та
завантаження реєстру маніфестів. Невалідні значення відхиляються; новіші, але валідні значення пропускають
plugin на старіших хостах.

`openclaw.install.allowInvalidConfigRecovery` є навмисно вузьким. Воно
не робить довільно зламані config придатними до встановлення. Наразі воно лише дозволяє
потокам встановлення відновлюватися після певних застарілих збоїв оновлення вбудованих plugin, таких як
відсутній шлях до вбудованого plugin або застарілий запис `channels.<id>` для цього ж
вбудованого plugin. Не пов’язані помилки config, як і раніше, блокують встановлення та спрямовують операторів
до `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` — це метадані пакета для маленького модуля перевірки:

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

Використовуйте це, коли потоки setup, doctor або configured-state потребують недорогої перевірки auth
у форматі так/ні до завантаження повного plugin channel. Цільовий export має бути невеликою
функцією, яка читає лише збережений стан; не спрямовуйте її через повний barrel runtime
channel.

`openclaw.channel.configuredState` використовує ту саму форму для недорогих перевірок
configured лише через env:

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

Використовуйте це, коли channel може визначити configured-state через env або інші невеликі
вхідні дані, не пов’язані з runtime. Якщо перевірка потребує повного визначення config або реального
runtime channel, залиште цю логіку в hook plugin `config.hasConfiguredState`.

## Вимоги до JSON Schema

- **Кожен plugin повинен містити JSON Schema**, навіть якщо він не приймає config.
- Порожня схема допустима (наприклад, `{ "type": "object", "additionalProperties": false }`).
- Схеми проходять валідацію під час читання/запису config, а не під час runtime.

## Поведінка валідації

- Невідомі ключі `channels.*` є **помилками**, якщо тільки id channel не оголошено
  в маніфесті plugin.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` і `plugins.slots.*`
  мають посилатися на id plugin, які **можна виявити**. Невідомі id є **помилками**.
- Якщо plugin встановлено, але він має зламаний або відсутній маніфест чи схему,
  валідація завершується помилкою, а Doctor повідомляє про помилку plugin.
- Якщо config plugin існує, але plugin **вимкнено**, config зберігається, і
  у Doctor + логах відображається **попередження**.

Дивіться [Довідник конфігурації](/uk/gateway/configuration) для повної схеми `plugins.*`.

## Примітки

- Маніфест **обов’язковий для власних Plugin OpenClaw**, зокрема для завантаження з локальної файлової системи.
- Runtime, як і раніше, окремо завантажує модуль plugin; маніфест використовується лише для
  виявлення + валідації.
- Власні маніфести розбираються за допомогою JSON5, тому коментарі, завершальні коми та
  ключі без лапок допускаються, якщо кінцеве значення все одно є об’єктом.
- Завантажувач маніфесту читає лише задокументовані поля маніфесту. Уникайте додавання
  власних ключів верхнього рівня.
- `providerAuthEnvVars` — це недорогий шлях метаданих для перевірок auth, валідації
  env-маркерів та подібних поверхонь auth provider, які не повинні запускати runtime plugin
  лише для перевірки назв env.
- `providerAuthAliases` дозволяє варіантам provider повторно використовувати auth
  env vars, профілі auth, auth на основі config та варіант onboarding API key іншого provider
  без жорсткого кодування цього зв’язку в core.
- `channelEnvVars` — це недорогий шлях метаданих для fallback через shell-env, запитів setup
  та подібних поверхонь channel, які не повинні запускати runtime plugin
  лише для перевірки назв env.
- `providerAuthChoices` — це недорогий шлях метаданих для засобів вибору варіантів auth,
  визначення `--auth-choice`, зіставлення preferred-provider і простої реєстрації
  прапорців CLI для onboarding до завантаження runtime provider. Для метаданих wizard runtime,
  які потребують коду provider, див.
  [Hook runtime provider](/uk/plugins/architecture#provider-runtime-hooks).
- Ексклюзивні типи plugin вибираються через `plugins.slots.*`.
  - `kind: "memory"` вибирається через `plugins.slots.memory`.
  - `kind: "context-engine"` вибирається через `plugins.slots.contextEngine`
    (типово: вбудований `legacy`).
- `channels`, `providers`, `cliBackends` і `skills` можна пропустити, якщо
  plugin їх не потребує.
- Якщо ваш plugin залежить від native-модулів, задокументуйте кроки збирання та всі
  вимоги до allowlist менеджера пакетів (наприклад, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Пов’язане

- [Створення Plugins](/uk/plugins/building-plugins) — початок роботи з plugins
- [Архітектура Plugin](/uk/plugins/architecture) — внутрішня архітектура
- [Огляд SDK](/uk/plugins/sdk-overview) — довідник SDK Plugin
