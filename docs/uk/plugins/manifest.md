---
read_when:
    - Ви створюєте plugin для OpenClaw
    - Вам потрібно постачати схему конфігурації plugin або налагодити помилки валідації plugin
summary: Вимоги до маніфесту plugin + JSON Schema (сувора валідація конфігурації)
title: Маніфест Plugin
x-i18n:
    generated_at: "2026-04-06T00:52:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: f6f915a761cdb5df77eba5d2ccd438c65445bd2ab41b0539d1200e63e8cf2c3a
    source_path: plugins/manifest.md
    workflow: 15
---

# Маніфест plugin (`openclaw.plugin.json`)

Ця сторінка стосується лише **нативного маніфесту plugin OpenClaw**.

Сумісні макети bundle описано тут: [Набори plugin](/uk/plugins/bundles).

Сумісні формати bundle використовують інші файли маніфесту:

- bundle Codex: `.codex-plugin/plugin.json`
- bundle Claude: `.claude-plugin/plugin.json` або типовий макет компонента Claude
  без маніфесту
- bundle Cursor: `.cursor-plugin/plugin.json`

OpenClaw також автоматично визначає ці макети bundle, але вони не проходять
валідацію за схемою `openclaw.plugin.json`, описаною тут.

Для сумісних bundle OpenClaw зараз читає метадані bundle, а також оголошені
корені Skills, корені команд Claude, типові значення `settings.json` bundle Claude,
типові значення LSP bundle Claude і підтримувані набори hooks, якщо макет
відповідає очікуванням середовища виконання OpenClaw.

Кожен нативний plugin OpenClaw **повинен** містити файл `openclaw.plugin.json` у
**корені plugin**. OpenClaw використовує цей маніфест, щоб валідувати конфігурацію
**без виконання коду plugin**. Відсутні або невалідні маніфести вважаються
помилками plugin і блокують валідацію конфігурації.

Повний посібник із системи plugin дивіться тут: [Plugins](/uk/tools/plugin).
Щодо нативної моделі можливостей і актуальних рекомендацій із зовнішньої сумісності:
[Модель можливостей](/uk/plugins/architecture#public-capability-model).

## Що робить цей файл

`openclaw.plugin.json` — це метадані, які OpenClaw читає перед завантаженням коду
вашого plugin.

Використовуйте його для:

- ідентичності plugin
- валідації конфігурації
- метаданих auth і онбордингу, які мають бути доступні без запуску середовища виконання plugin
- метаданих псевдонімів і автоувімкнення, які мають визначатися до завантаження середовища виконання plugin
- скорочених метаданих належності до сімейств моделей, які мають автоматично активувати
  plugin до завантаження середовища виконання
- статичних знімків належності можливостей, що використовуються для сумісної логіки bundled plugin і
  покриття контрактів
- метаданих конфігурації, специфічних для channel, які мають об’єднуватися в поверхні каталогу та валідації
  без завантаження середовища виконання
- підказок UI для конфігурації

Не використовуйте його для:

- реєстрації поведінки середовища виконання
- оголошення code entrypoints
- метаданих встановлення npm

Для цього призначені код plugin і `package.json`.

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
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
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
| `id`                                | Так         | `string`                         | Канонічний id plugin. Це id, що використовується в `plugins.entries.<id>`.                                                                                                                                  |
| `configSchema`                      | Так         | `object`                         | Вбудована JSON Schema для конфігурації цього plugin.                                                                                                                                                         |
| `enabledByDefault`                  | Ні          | `true`                           | Позначає bundled plugin як увімкнений типово. Не вказуйте це поле або встановіть будь-яке значення, відмінне від `true`, щоб plugin був типово вимкнений.                                                  |
| `legacyPluginIds`                   | Ні          | `string[]`                       | Застарілі id, що нормалізуються до цього канонічного id plugin.                                                                                                                                              |
| `autoEnableWhenConfiguredProviders` | Ні          | `string[]`                       | Id provider, які мають автоматично вмикати цей plugin, коли auth, конфігурація або посилання на моделі згадують їх.                                                                                         |
| `kind`                              | Ні          | `"memory"` \| `"context-engine"` | Оголошує виключний тип plugin, що використовується `plugins.slots.*`.                                                                                                                                        |
| `channels`                          | Ні          | `string[]`                       | Id channel, що належать цьому plugin. Використовується для виявлення та валідації конфігурації.                                                                                                             |
| `providers`                         | Ні          | `string[]`                       | Id provider, що належать цьому plugin.                                                                                                                                                                       |
| `modelSupport`                      | Ні          | `object`                         | Скорочені метадані сімейств моделей, що належать маніфесту й використовуються для автоматичного завантаження plugin до запуску середовища виконання.                                                       |
| `providerAuthEnvVars`               | Ні          | `Record<string, string[]>`       | Недорогі метадані env для auth provider, які OpenClaw може перевіряти без завантаження коду plugin.                                                                                                         |
| `providerAuthChoices`               | Ні          | `object[]`                       | Недорогі метадані варіантів auth для селекторів онбордингу, визначення preferred provider і простого зв’язування CLI flags.                                                                                 |
| `contracts`                         | Ні          | `object`                         | Статичний bundled-знімок можливостей для speech, realtime transcription, realtime voice, media-understanding, image-generation, music-generation, video-generation, web-fetch, web search і належності tools. |
| `channelConfigs`                    | Ні          | `Record<string, object>`         | Метадані конфігурації channel, що належать маніфесту та об’єднуються з поверхнями виявлення й валідації до завантаження середовища виконання.                                                               |
| `skills`                            | Ні          | `string[]`                       | Каталоги Skills для завантаження, відносно кореня plugin.                                                                                                                                                    |
| `name`                              | Ні          | `string`                         | Зрозуміла людині назва plugin.                                                                                                                                                                               |
| `description`                       | Ні          | `string`                         | Короткий опис, що відображається в поверхнях plugin.                                                                                                                                                         |
| `version`                           | Ні          | `string`                         | Інформаційна версія plugin.                                                                                                                                                                                  |
| `uiHints`                           | Ні          | `Record<string, object>`         | Мітки UI, placeholder-и та підказки чутливості для полів конфігурації.                                                                                                                                       |

## Довідник `providerAuthChoices`

Кожен запис `providerAuthChoices` описує один варіант онбордингу або auth.
OpenClaw читає це до завантаження середовища виконання provider.

| Поле                 | Обов’язкове | Тип                                             | Що воно означає                                                                                      |
| -------------------- | ----------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `provider`           | Так         | `string`                                        | Id provider, до якого належить цей варіант.                                                          |
| `method`             | Так         | `string`                                        | Id методу auth, за яким виконується маршрутизація.                                                   |
| `choiceId`           | Так         | `string`                                        | Стабільний id варіанта auth, що використовується в онбордингу та потоках CLI.                       |
| `choiceLabel`        | Ні          | `string`                                        | Мітка для користувача. Якщо не вказано, OpenClaw використовує `choiceId`.                            |
| `choiceHint`         | Ні          | `string`                                        | Короткий допоміжний текст для селектора.                                                             |
| `assistantPriority`  | Ні          | `number`                                        | Менші значення сортуються раніше в інтерактивних селекторах, керованих асистентом.                  |
| `assistantVisibility`| Ні          | `"visible"` \| `"manual-only"`                  | Приховує варіант у селекторах асистента, але залишає можливість ручного вибору через CLI.           |
| `deprecatedChoiceIds`| Ні          | `string[]`                                      | Застарілі id варіантів, які мають перенаправляти користувачів на цей варіант-заміну.                |
| `groupId`            | Ні          | `string`                                        | Необов’язковий id групи для групування пов’язаних варіантів.                                         |
| `groupLabel`         | Ні          | `string`                                        | Мітка цієї групи для користувача.                                                                    |
| `groupHint`          | Ні          | `string`                                        | Короткий допоміжний текст для групи.                                                                 |
| `optionKey`          | Ні          | `string`                                        | Внутрішній ключ параметра для простих потоків auth з одним flag.                                     |
| `cliFlag`            | Ні          | `string`                                        | Назва CLI flag, наприклад `--openrouter-api-key`.                                                    |
| `cliOption`          | Ні          | `string`                                        | Повна форма параметра CLI, наприклад `--openrouter-api-key <key>`.                                   |
| `cliDescription`     | Ні          | `string`                                        | Опис, що використовується в довідці CLI.                                                             |
| `onboardingScopes`   | Ні          | `Array<"text-inference" \| "image-generation">` | У яких поверхнях онбордингу має з’являтися цей варіант. Якщо не вказано, типово використовується `["text-inference"]`. |

## Довідник `uiHints`

`uiHints` — це мапа від назв полів конфігурації до невеликих підказок рендерингу.

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

Кожна підказка поля може містити:

| Поле          | Тип        | Що воно означає                         |
| ------------- | ---------- | --------------------------------------- |
| `label`       | `string`   | Мітка поля для користувача.             |
| `help`        | `string`   | Короткий допоміжний текст.              |
| `tags`        | `string[]` | Необов’язкові теги UI.                  |
| `advanced`    | `boolean`  | Позначає поле як розширене.             |
| `sensitive`   | `boolean`  | Позначає поле як секретне або чутливе.  |
| `placeholder` | `string`   | Текст placeholder для полів форми.      |

## Довідник `contracts`

Використовуйте `contracts` лише для статичних метаданих належності можливостей, які OpenClaw може
прочитати без імпорту середовища виконання plugin.

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

Кожен список необов’язковий:

| Поле                             | Тип        | Що воно означає                                             |
| -------------------------------- | ---------- | ----------------------------------------------------------- |
| `speechProviders`                | `string[]` | Id provider speech, що належать цьому plugin.               |
| `realtimeTranscriptionProviders` | `string[]` | Id provider realtime-transcription, що належать цьому plugin. |
| `realtimeVoiceProviders`         | `string[]` | Id provider realtime-voice, що належать цьому plugin.       |
| `mediaUnderstandingProviders`    | `string[]` | Id provider media-understanding, що належать цьому plugin.  |
| `imageGenerationProviders`       | `string[]` | Id provider image-generation, що належать цьому plugin.     |
| `videoGenerationProviders`       | `string[]` | Id provider video-generation, що належать цьому plugin.     |
| `webFetchProviders`              | `string[]` | Id provider web-fetch, що належать цьому plugin.            |
| `webSearchProviders`             | `string[]` | Id provider web-search, що належать цьому plugin.           |
| `tools`                          | `string[]` | Назви agent tools, що належать цьому plugin для перевірок bundled-контрактів. |

## Довідник `channelConfigs`

Використовуйте `channelConfigs`, коли plugin channel потребує недорогих метаданих конфігурації до
завантаження середовища виконання.

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

| Поле          | Тип                      | Що воно означає                                                                                |
| ------------- | ------------------------ | ---------------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | JSON Schema для `channels.<id>`. Обов’язкова для кожного оголошеного запису конфігурації channel. |
| `uiHints`     | `Record<string, object>` | Необов’язкові мітки UI/placeholder-и/підказки чутливості для цього розділу конфігурації channel. |
| `label`       | `string`                 | Мітка channel, що об’єднується з поверхнями вибору та перевірки, коли метадані середовища виконання ще не готові. |
| `description` | `string`                 | Короткий опис channel для поверхонь перевірки та каталогу.                                     |
| `preferOver`  | `string[]`               | Застарілі або нижчого пріоритету id plugin, які цей channel має випереджати в поверхнях вибору. |

## Довідник `modelSupport`

Використовуйте `modelSupport`, коли OpenClaw має визначати ваш plugin provider за
скороченими id моделей, як-от `gpt-5.4` або `claude-sonnet-4.6`, до завантаження середовища виконання plugin.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw застосовує такий пріоритет:

- явні посилання `provider/model` використовують метадані маніфесту `providers`, що належать власнику
- `modelPatterns` мають вищий пріоритет, ніж `modelPrefixes`
- якщо збігаються один небандлований plugin і один bundled plugin, перемагає небандлований
  plugin
- решта неоднозначностей ігнорується, доки користувач або конфігурація не вкажуть provider

Поля:

| Поле            | Тип        | Що воно означає                                                                  |
| --------------- | ---------- | -------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Префікси, що зіставляються через `startsWith` зі скороченими id моделей.        |
| `modelPatterns` | `string[]` | Джерела regex, що зіставляються зі скороченими id моделей після видалення суфікса профілю. |

Застарілі ключі можливостей верхнього рівня не рекомендуються до використання. Використайте `openclaw doctor --fix`, щоб
перемістити `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` і `webSearchProviders` до `contracts`; звичайне
завантаження маніфесту більше не трактує ці поля верхнього рівня як
належність можливостей.

## Маніфест і `package.json`

Ці два файли виконують різні завдання:

| Файл                   | Для чого використовувати                                                                                                          |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Виявлення, валідація конфігурації, метадані варіантів auth і підказки UI, які мають існувати до запуску коду plugin             |
| `package.json`         | Метадані npm, встановлення залежностей і блок `openclaw`, що використовується для entrypoints, обмежень встановлення, налаштування або метаданих каталогу |

Якщо ви не впевнені, куди має належати певний фрагмент метаданих, користуйтеся таким правилом:

- якщо OpenClaw повинен знати це до завантаження коду plugin, помістіть це в `openclaw.plugin.json`
- якщо це стосується пакування, entry files або поведінки встановлення npm, помістіть це в `package.json`

### Поля `package.json`, які впливають на виявлення

Деякі метадані plugin до запуску середовища виконання навмисно розміщені в `package.json` у блоці
`openclaw`, а не в `openclaw.plugin.json`.

Важливі приклади:

| Поле                                                              | Що воно означає                                                                                                                                 |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Оголошує нативні entrypoints plugin.                                                                                                            |
| `openclaw.setupEntry`                                             | Легковажний entrypoint лише для налаштування, який використовується під час онбордингу та відкладеного запуску channel.                       |
| `openclaw.channel`                                                | Недорогі метадані каталогу channel, як-от мітки, шляхи до документації, псевдоніми та текст для вибору.                                      |
| `openclaw.channel.configuredState`                                | Недорогі метадані перевірки налаштованого стану, які можуть відповісти на питання "чи вже існує налаштування лише через env?" без завантаження повного середовища виконання channel. |
| `openclaw.channel.persistedAuthState`                             | Недорогі метадані перевірки збереженого auth, які можуть відповісти на питання "чи вже є активний вхід?" без завантаження повного середовища виконання channel. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Підказки для встановлення/оновлення bundled plugin і externally published plugin.                                                              |
| `openclaw.install.defaultChoice`                                  | Бажаний шлях встановлення, коли доступно кілька джерел встановлення.                                                                            |
| `openclaw.install.minHostVersion`                                 | Мінімальна підтримувана версія хоста OpenClaw з використанням нижньої межі semver, наприклад `>=2026.3.22`.                                   |
| `openclaw.install.allowInvalidConfigRecovery`                     | Дозволяє вузький шлях відновлення перевстановлення bundled plugin, коли конфігурація невалідна.                                                |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Дозволяє поверхням channel лише для налаштування завантажуватися до повного plugin channel під час запуску.                                   |

`openclaw.install.minHostVersion` застосовується під час встановлення та
завантаження реєстру маніфесту. Невалідні значення відхиляються; новіші, але валідні
значення пропускають plugin на старіших хостах.

`openclaw.install.allowInvalidConfigRecovery` навмисно має вузьке призначення. Воно
не робить довільно зламані конфігурації придатними до встановлення. Сьогодні воно лише дозволяє потокам встановлення
відновлюватися після конкретних застарілих збоїв оновлення bundled plugin, наприклад
відсутнього шляху до bundled plugin або застарілого запису `channels.<id>` для того самого
bundled plugin. Не пов’язані помилки конфігурації все одно блокують встановлення і направляють операторів
до `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` — це метадані package для маленького
модуля перевірки:

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

Використовуйте це, коли потокам setup, doctor або configured-state потрібна недорога
перевірка auth у форматі yes/no до завантаження повного plugin channel. Цільовий export має бути невеликою
функцією, яка читає лише збережений стан; не маршрутизуйте її через повний
barrel середовища виконання channel.

`openclaw.channel.configuredState` має таку саму форму для недорогих перевірок
налаштованого стану лише через env:

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

Використовуйте це, коли channel може визначити налаштований стан із env або інших малих
неruntime-джерел. Якщо перевірка потребує повного розв’язання конфігурації або реального
середовища виконання channel, залиште цю логіку в hook `config.hasConfiguredState`
plugin.

## Вимоги до JSON Schema

- **Кожен plugin повинен містити JSON Schema**, навіть якщо він не приймає конфігурацію.
- Порожня схема допустима (наприклад, `{ "type": "object", "additionalProperties": false }`).
- Схеми валідуються під час читання/запису конфігурації, а не під час виконання.

## Поведінка валідації

- Невідомі ключі `channels.*` є **помилками**, якщо тільки id channel не оголошено
  маніфестом plugin.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` і `plugins.slots.*`
  повинні посилатися на **виявлювані** id plugin. Невідомі id є **помилками**.
- Якщо plugin встановлено, але має зламаний або відсутній маніфест чи схему,
  валідація завершується помилкою, а Doctor повідомляє про помилку plugin.
- Якщо конфігурація plugin існує, але plugin **вимкнено**, конфігурація зберігається,
  а в Doctor і журналах відображається **попередження**.

Повну схему `plugins.*` дивіться в [Довіднику з конфігурації](/uk/gateway/configuration).

## Примітки

- Маніфест **обов’язковий для нативних plugin OpenClaw**, включно із завантаженням із локальної файлової системи.
- Середовище виконання, як і раніше, завантажує модуль plugin окремо; маніфест призначений лише для
  виявлення + валідації.
- Нативні маніфести розбираються за допомогою JSON5, тому коментарі, завершаючі коми та
  ключі без лапок допускаються, якщо фінальне значення все одно є object.
- Завантажувач маніфесту читає лише задокументовані поля маніфесту. Уникайте додавання
  власних ключів верхнього рівня сюди.
- `providerAuthEnvVars` — це недорогий шлях метаданих для перевірок auth, валідації маркерів env
  та подібних поверхонь auth provider, які не повинні запускати середовище виконання plugin
  лише для перевірки назв env.
- `providerAuthChoices` — це недорогий шлях метаданих для селекторів варіантів auth,
  визначення `--auth-choice`, мапінгу preferred provider і простої реєстрації CLI flags
  для онбордингу до завантаження середовища виконання provider. Метадані wizard середовища виконання,
  що потребують коду provider, дивіться в
  [Hooks середовища виконання provider](/uk/plugins/architecture#provider-runtime-hooks).
- Виключні типи plugin вибираються через `plugins.slots.*`.
  - `kind: "memory"` вибирається через `plugins.slots.memory`.
  - `kind: "context-engine"` вибирається через `plugins.slots.contextEngine`
    (типово: вбудований `legacy`).
- `channels`, `providers` і `skills` можна не вказувати, якщо
  plugin їх не потребує.
- Якщо ваш plugin залежить від нативних модулів, задокументуйте кроки збирання та будь-які
  вимоги до allowlist менеджера пакетів (наприклад, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Пов’язані сторінки

- [Створення Plugins](/uk/plugins/building-plugins) — початок роботи з plugins
- [Архітектура Plugin](/uk/plugins/architecture) — внутрішня архітектура
- [Огляд SDK](/uk/plugins/sdk-overview) — довідник Plugin SDK
