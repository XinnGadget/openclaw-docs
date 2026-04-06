---
read_when:
    - Ви хочете створити новий plugin для OpenClaw
    - Вам потрібен швидкий старт для розробки plugin
    - Ви додаєте новий канал, провайдера, інструмент або іншу можливість до OpenClaw
sidebarTitle: Getting Started
summary: Створіть свій перший plugin для OpenClaw за лічені хвилини
title: Створення Plugins
x-i18n:
    generated_at: "2026-04-06T00:52:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9be344cb300ecbcba08e593a95bcc93ab16c14b28a0ff0c29b26b79d8249146c
    source_path: plugins/building-plugins.md
    workflow: 15
---

# Створення Plugins

Plugins розширюють OpenClaw новими можливостями: канали, провайдери моделей,
мовлення, транскрипція в реальному часі, голос у реальному часі, розуміння медіа, генерація зображень,
генерація відео, отримання вебсторінок, вебпошук, інструменти агента або будь-яка
комбінація.

Вам не потрібно додавати свій plugin до репозиторію OpenClaw. Опублікуйте його в
[ClawHub](/uk/tools/clawhub) або npm, а користувачі встановлять його за допомогою
`openclaw plugins install <package-name>`. OpenClaw спочатку пробує ClawHub, а потім
автоматично переходить до npm.

## Передумови

- Node >= 22 і менеджер пакетів (npm або pnpm)
- Знайомство з TypeScript (ESM)
- Для plugin у репозиторії: клонований репозиторій і виконано `pnpm install`

## Який тип plugin?

<CardGroup cols={3}>
  <Card title="Channel plugin" icon="messages-square" href="/uk/plugins/sdk-channel-plugins">
    Підключає OpenClaw до платформи обміну повідомленнями (Discord, IRC тощо)
  </Card>
  <Card title="Provider plugin" icon="cpu" href="/uk/plugins/sdk-provider-plugins">
    Додає провайдера моделей (LLM, проксі або власну кінцеву точку)
  </Card>
  <Card title="Tool / hook plugin" icon="wrench">
    Реєструє інструменти агента, хуки подій або сервіси — продовжуйте нижче
  </Card>
</CardGroup>

Якщо channel plugin є необов'язковим і може бути не встановлений під час
onboarding/налаштування, використовуйте `createOptionalChannelSetupSurface(...)` з
`openclaw/plugin-sdk/channel-setup`. Він створює пару адаптера налаштування та майстра,
яка повідомляє про вимогу встановлення і блокує реальний запис конфігурації,
доки plugin не буде встановлено.

## Швидкий старт: tool plugin

У цьому прикладі створюється мінімальний plugin, який реєструє інструмент агента. Для channel
і provider plugins є окремі посібники, посилання на які наведено вище.

<Steps>
  <Step title="Створіть пакет і маніфест">
    <CodeGroup>
    ```json package.json
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

    ```json openclaw.plugin.json
    {
      "id": "my-plugin",
      "name": "My Plugin",
      "description": "Adds a custom tool to OpenClaw",
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Кожному plugin потрібен маніфест, навіть без конфігурації. Дивіться
    [Manifest](/uk/plugins/manifest) для повної схеми. Канонічні фрагменти для публікації в ClawHub
    розміщено в `docs/snippets/plugin-publish/`.

  </Step>

  <Step title="Напишіть точку входу">

    ```typescript
    // index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { Type } from "@sinclair/typebox";

    export default definePluginEntry({
      id: "my-plugin",
      name: "My Plugin",
      description: "Adds a custom tool to OpenClaw",
      register(api) {
        api.registerTool({
          name: "my_tool",
          description: "Do a thing",
          parameters: Type.Object({ input: Type.String() }),
          async execute(_id, params) {
            return { content: [{ type: "text", text: `Got: ${params.input}` }] };
          },
        });
      },
    });
    ```

    `definePluginEntry` призначений для plugins, які не є каналами. Для каналів використовуйте
    `defineChannelPluginEntry` — див. [Channel Plugins](/uk/plugins/sdk-channel-plugins).
    Повний список параметрів точки входу див. у [Entry Points](/uk/plugins/sdk-entrypoints).

  </Step>

  <Step title="Протестуйте та опублікуйте">

    **Зовнішні plugins:** виконайте перевірку та опублікуйте через ClawHub, потім встановіть:

    ```bash
    clawhub package publish your-org/your-plugin --dry-run
    clawhub package publish your-org/your-plugin
    openclaw plugins install clawhub:@myorg/openclaw-my-plugin
    ```

    OpenClaw також перевіряє ClawHub перед npm для звичайних специфікацій пакетів, як-от
    `@myorg/openclaw-my-plugin`.

    **Plugins у репозиторії:** розміщуйте їх у дереві робочого простору bundled plugin — вони виявляються автоматично.

    ```bash
    pnpm test -- <bundled-plugin-root>/my-plugin/
    ```

  </Step>
</Steps>

## Можливості plugin

Один plugin може зареєструвати будь-яку кількість можливостей через об’єкт `api`:

| Можливість             | Метод реєстрації                               | Детальний посібник                                                             |
| ---------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------ |
| Текстовий inference (LLM) | `api.registerProvider(...)`                 | [Provider Plugins](/uk/plugins/sdk-provider-plugins)                              |
| Канал / обмін повідомленнями | `api.registerChannel(...)`              | [Channel Plugins](/uk/plugins/sdk-channel-plugins)                                |
| Мовлення (TTS/STT)     | `api.registerSpeechProvider(...)`              | [Provider Plugins](/uk/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Транскрипція в реальному часі | `api.registerRealtimeTranscriptionProvider(...)` | [Provider Plugins](/uk/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Голос у реальному часі | `api.registerRealtimeVoiceProvider(...)`       | [Provider Plugins](/uk/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Розуміння медіа        | `api.registerMediaUnderstandingProvider(...)`  | [Provider Plugins](/uk/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Генерація зображень    | `api.registerImageGenerationProvider(...)`     | [Provider Plugins](/uk/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Генерація музики       | `api.registerMusicGenerationProvider(...)`     | [Provider Plugins](/uk/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Генерація відео        | `api.registerVideoGenerationProvider(...)`     | [Provider Plugins](/uk/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Отримання вебсторінок  | `api.registerWebFetchProvider(...)`            | [Provider Plugins](/uk/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Вебпошук               | `api.registerWebSearchProvider(...)`           | [Provider Plugins](/uk/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Інструменти агента     | `api.registerTool(...)`                        | Нижче                                                                          |
| Власні команди         | `api.registerCommand(...)`                     | [Entry Points](/uk/plugins/sdk-entrypoints)                                       |
| Хуки подій             | `api.registerHook(...)`                        | [Entry Points](/uk/plugins/sdk-entrypoints)                                       |
| HTTP-маршрути          | `api.registerHttpRoute(...)`                   | [Internals](/uk/plugins/architecture#gateway-http-routes)                         |
| Підкоманди CLI         | `api.registerCli(...)`                         | [Entry Points](/uk/plugins/sdk-entrypoints)                                       |

Повний API реєстрації див. у [SDK Overview](/uk/plugins/sdk-overview#registration-api).

Якщо ваш plugin реєструє власні методи gateway RPC, використовуйте для них
префікс, специфічний для plugin. Простори назв адміністрування ядра (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) залишаються зарезервованими й завжди
прив’язуються до `operator.admin`, навіть якщо plugin запитує вужчу область доступу.

Семантика guard для hook, про яку варто пам’ятати:

- `before_tool_call`: `{ block: true }` є остаточним рішенням і зупиняє обробники з нижчим пріоритетом.
- `before_tool_call`: `{ block: false }` вважається відсутністю рішення.
- `before_tool_call`: `{ requireApproval: true }` призупиняє виконання агента та запитує схвалення користувача через накладення схвалення exec, кнопки Telegram, інтеракції Discord або команду `/approve` у будь-якому каналі.
- `before_install`: `{ block: true }` є остаточним рішенням і зупиняє обробники з нижчим пріоритетом.
- `before_install`: `{ block: false }` вважається відсутністю рішення.
- `message_sending`: `{ cancel: true }` є остаточним рішенням і зупиняє обробники з нижчим пріоритетом.
- `message_sending`: `{ cancel: false }` вважається відсутністю рішення.

Команда `/approve` обробляє і схвалення exec, і схвалення plugin з обмеженим fallback: коли ідентифікатор схвалення exec не знайдено, OpenClaw повторно пробує той самий ідентифікатор через схвалення plugin. Переспрямування схвалень plugin можна налаштувати окремо через `approvals.plugin` у конфігурації.

Якщо власній логіці схвалення потрібно виявляти цей самий випадок обмеженого fallback,
використовуйте `isApprovalNotFoundError` з `openclaw/plugin-sdk/error-runtime`,
замість ручного зіставлення рядків про завершення строку дії схвалення.

Докладніше див. у [семантиці рішень hook в SDK Overview](/uk/plugins/sdk-overview#hook-decision-semantics).

## Реєстрація інструментів агента

Інструменти — це типізовані функції, які може викликати LLM. Вони можуть бути обов’язковими (завжди
доступними) або необов’язковими (увімкнення користувачем):

```typescript
register(api) {
  // Required tool — always available
  api.registerTool({
    name: "my_tool",
    description: "Do a thing",
    parameters: Type.Object({ input: Type.String() }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });

  // Optional tool — user must add to allowlist
  api.registerTool(
    {
      name: "workflow_tool",
      description: "Run a workflow",
      parameters: Type.Object({ pipeline: Type.String() }),
      async execute(_id, params) {
        return { content: [{ type: "text", text: params.pipeline }] };
      },
    },
    { optional: true },
  );
}
```

Користувачі вмикають необов’язкові інструменти в конфігурації:

```json5
{
  tools: { allow: ["workflow_tool"] },
}
```

- Назви інструментів не повинні конфліктувати з інструментами ядра (конфліктні пропускаються)
- Використовуйте `optional: true` для інструментів із побічними ефектами або додатковими вимогами до двійкових файлів
- Користувачі можуть увімкнути всі інструменти з plugin, додавши ідентифікатор plugin до `tools.allow`

## Угоди щодо імпорту

Завжди імпортуйте з цільових шляхів `openclaw/plugin-sdk/<subpath>`:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";

// Wrong: monolithic root (deprecated, will be removed)
import { ... } from "openclaw/plugin-sdk";
```

Повний довідник підшляхів див. у [SDK Overview](/uk/plugins/sdk-overview).

Усередині вашого plugin використовуйте локальні barrel-файли (`api.ts`, `runtime-api.ts`) для
внутрішніх імпортів — ніколи не імпортуйте власний plugin через його шлях SDK.

Для provider plugins зберігайте допоміжні функції, специфічні для провайдера, у цих barrel-файлах
кореня пакета, якщо тільки межа не є справді універсальною. Поточні bundled приклади:

- Anthropic: обгортки потоків Claude і helper-функції для `service_tier` / beta
- OpenAI: builder-и провайдерів, helper-и моделей за замовчуванням, провайдери реального часу
- OpenRouter: builder провайдера плюс helper-и для onboarding/конфігурації

Якщо helper корисний лише в межах одного bundled provider package, залишайте його на цій
межі кореня пакета замість перенесення до `openclaw/plugin-sdk/*`.

Деякі згенеровані helper-межі `openclaw/plugin-sdk/<bundled-id>` усе ще існують для
підтримки bundled plugin і сумісності, наприклад
`plugin-sdk/feishu-setup` або `plugin-sdk/zalo-setup`. Вважайте їх зарезервованими
поверхнями, а не типовим шаблоном для нових сторонніх plugins.

## Контрольний список перед надсиланням

<Check>**package.json** має правильні метадані `openclaw`</Check>
<Check>Маніфест **openclaw.plugin.json** присутній і коректний</Check>
<Check>Точка входу використовує `defineChannelPluginEntry` або `definePluginEntry`</Check>
<Check>Усі імпорти використовують цільові шляхи `plugin-sdk/<subpath>`</Check>
<Check>Внутрішні імпорти використовують локальні модулі, а не self-imports через SDK</Check>
<Check>Тести проходять (`pnpm test -- <bundled-plugin-root>/my-plugin/`)</Check>
<Check>`pnpm check` проходить (для plugins у репозиторії)</Check>

## Тестування beta-релізів

1. Стежте за тегами релізів GitHub у [openclaw/openclaw](https://github.com/openclaw/openclaw/releases) і підпишіться через `Watch` > `Releases`. Beta-теги мають вигляд `v2026.3.N-beta.1`. Ви також можете ввімкнути сповіщення для офіційного акаунта OpenClaw у X [@openclaw](https://x.com/openclaw) для анонсів релізів.
2. Протестуйте свій plugin на beta-тегу щойно він з’явиться. Вікно до stable-релізу зазвичай триває лише кілька годин.
3. Після тестування напишіть у гілці вашого plugin у каналі Discord `plugin-forum`: або `all good`, або що саме зламалося. Якщо у вас ще немає гілки, створіть її.
4. Якщо щось зламалося, створіть або оновіть issue з назвою `Beta blocker: <plugin-name> - <summary>` і додайте мітку `beta-blocker`. Додайте посилання на issue у вашу гілку.
5. Відкрийте PR до `main` з назвою `fix(<plugin-id>): beta blocker - <summary>` і додайте посилання на issue і в PR, і у вашу гілку в Discord. Учасники не можуть додавати мітки до PR, тому назва є сигналом на боці PR для мейнтейнерів та автоматизації. Blocker-и з PR будуть злиті; blocker-и без PR можуть усе ж потрапити в реліз. Мейнтейнери стежать за цими гілками під час beta-тестування.
6. Тиша означає, що все добре. Якщо ви пропустите це вікно, ваш виправлення, ймовірно, потрапить уже в наступний цикл.

## Подальші кроки

<CardGroup cols={2}>
  <Card title="Channel Plugins" icon="messages-square" href="/uk/plugins/sdk-channel-plugins">
    Створіть plugin для каналу обміну повідомленнями
  </Card>
  <Card title="Provider Plugins" icon="cpu" href="/uk/plugins/sdk-provider-plugins">
    Створіть plugin для провайдера моделей
  </Card>
  <Card title="SDK Overview" icon="book-open" href="/uk/plugins/sdk-overview">
    Довідник з карти імпортів і API реєстрації
  </Card>
  <Card title="Runtime Helpers" icon="settings" href="/uk/plugins/sdk-runtime">
    TTS, пошук, subagent через api.runtime
  </Card>
  <Card title="Testing" icon="test-tubes" href="/uk/plugins/sdk-testing">
    Утиліти та шаблони для тестування
  </Card>
  <Card title="Plugin Manifest" icon="file-json" href="/uk/plugins/manifest">
    Повний довідник зі схеми маніфесту
  </Card>
</CardGroup>

## Пов’язане

- [Plugin Architecture](/uk/plugins/architecture) — детальний розбір внутрішньої архітектури
- [SDK Overview](/uk/plugins/sdk-overview) — довідник Plugin SDK
- [Manifest](/uk/plugins/manifest) — формат маніфесту plugin
- [Channel Plugins](/uk/plugins/sdk-channel-plugins) — створення channel plugins
- [Provider Plugins](/uk/plugins/sdk-provider-plugins) — створення provider plugins
