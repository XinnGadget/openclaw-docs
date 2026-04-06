---
read_when:
    - Ви бачите попередження OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - Ви бачите попередження OPENCLAW_EXTENSION_API_DEPRECATED
    - Ви оновлюєте плагін до сучасної архітектури плагінів
    - Ви підтримуєте зовнішній плагін OpenClaw
sidebarTitle: Migrate to SDK
summary: Перейдіть із застарілого шару зворотної сумісності на сучасний SDK плагінів
title: Міграція SDK плагінів
x-i18n:
    generated_at: "2026-04-06T00:53:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: b71ce69b30c3bb02da1b263b1d11dc3214deae5f6fc708515e23b5a1c7bb7c8f
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Міграція SDK плагінів

OpenClaw перейшов від широкого шару зворотної сумісності до сучасної
архітектури плагінів із вузькоспрямованими, документованими імпортами. Якщо ваш
плагін було створено до появи нової архітектури, цей посібник допоможе вам
виконати міграцію.

## Що змінюється

Стара система плагінів надавала дві надто широкі поверхні, які дозволяли
плагінам імпортувати все необхідне з однієї точки входу:

- **`openclaw/plugin-sdk/compat`** — один імпорт, який повторно експортував
  десятки допоміжних функцій. Його було додано, щоб старі плагіни на основі
  хуків продовжували працювати, поки створювалася нова архітектура плагінів.
- **`openclaw/extension-api`** — міст, який надавав плагінам прямий доступ до
  допоміжних функцій на боці хоста, таких як вбудований запускальник агентів.

Обидві поверхні тепер **застарілі**. Вони досі працюють під час виконання, але
нові плагіни не повинні їх використовувати, а наявні плагіни мають перейти на
новий підхід до того, як у наступному мажорному релізі їх буде вилучено.

<Warning>
  Шар зворотної сумісності буде вилучено в одному з майбутніх мажорних релізів.
  Плагіни, які все ще імпортують із цих поверхонь, перестануть працювати, коли
  це станеться.
</Warning>

## Чому це змінилося

Старий підхід спричиняв проблеми:

- **Повільний запуск** — імпорт однієї допоміжної функції завантажував десятки
  не пов’язаних між собою модулів
- **Циклічні залежності** — широкі повторні експорти спрощували створення циклів імпорту
- **Нечітка поверхня API** — не було способу зрозуміти, які експорти стабільні, а які внутрішні

Сучасний SDK плагінів виправляє це: кожен шлях імпорту (`openclaw/plugin-sdk/\<subpath\>`)
є невеликим, самодостатнім модулем із чітким призначенням і документованим контрактом.

Застарілі зручні шви провайдерів для вбудованих каналів також зникли. Імпорти
на кшталт `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
канально-брендовані допоміжні шви та
`openclaw/plugin-sdk/telegram-core` були приватними скороченнями для монорепозиторію, а не
стабільними контрактами плагінів. Натомість використовуйте вузькі загальні
підшляхи SDK. Усередині робочого простору вбудованих плагінів зберігайте
допоміжні функції, що належать провайдеру, у власному `api.ts` або
`runtime-api.ts` цього плагіна.

Поточні приклади вбудованих провайдерів:

- Anthropic зберігає специфічні для Claude допоміжні функції потоків у власному шві `api.ts` /
  `contract-api.ts`
- OpenAI зберігає побудовники провайдерів, допоміжні функції моделей за замовчуванням і побудовники провайдерів реального часу
  у власному `api.ts`
- OpenRouter зберігає побудовник провайдера та допоміжні функції онбордингу/конфігурації у власному
  `api.ts`

## Як виконати міграцію

<Steps>
  <Step title="Перевірте поведінку запасного режиму оболонки Windows wrapper">
    Якщо ваш плагін використовує `openclaw/plugin-sdk/windows-spawn`, невизначені Windows
    wrapper-и `.cmd`/`.bat` тепер аварійно завершуються в закритому режимі, якщо ви явно не передасте
    `allowShellFallback: true`.

    ```typescript
    // До
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Після
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Встановлюйте це лише для довірених сумісних викликів, які навмисно
      // допускають запасний режим через оболонку.
      allowShellFallback: true,
    });
    ```

    Якщо ваш виклик не покладається навмисно на запасний режим оболонки, не
    встановлюйте `allowShellFallback`, а натомість обробіть викинуту помилку.

  </Step>

  <Step title="Знайдіть застарілі імпорти">
    Знайдіть у своєму плагіні імпорти з будь-якої із застарілих поверхонь:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Замініть на вузькоспрямовані імпорти">
    Кожен експорт зі старої поверхні відповідає певному сучасному шляху імпорту:

    ```typescript
    // До (застарілий шар зворотної сумісності)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // Після (сучасні вузькоспрямовані імпорти)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Для допоміжних функцій на боці хоста використовуйте впроваджене середовище
    виконання плагіна замість прямого імпорту:

    ```typescript
    // До (застарілий міст extension-api)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Після (впроваджене середовище виконання)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Той самий шаблон застосовується й до інших застарілих допоміжних функцій моста:

    | Старий імпорт | Сучасний еквівалент |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | допоміжні функції сховища сесій | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Зберіть і протестуйте">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## Довідник шляхів імпорту

<Accordion title="Таблиця поширених шляхів імпорту">
  | Шлях імпорту | Призначення | Ключові експорти |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Канонічна допоміжна функція точки входу плагіна | `definePluginEntry` |
  | `plugin-sdk/core` | Застарілий повторний umbrella-експорт для визначень/побудовників входу каналу | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Експорт кореневої схеми конфігурації | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Допоміжна функція точки входу для одного провайдера | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Вузькоспрямовані визначення та побудовники входу каналу | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Спільні допоміжні функції майстра налаштування | Запити allowlist, побудовники статусу налаштування |
  | `plugin-sdk/setup-runtime` | Допоміжні функції середовища виконання під час налаштування | Безпечні для імпорту адаптери латок налаштування, допоміжні функції нотаток пошуку, `promptResolvedAllowFrom`, `splitSetupEntries`, делеговані проксі налаштування |
  | `plugin-sdk/setup-adapter-runtime` | Допоміжні функції адаптера налаштування | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Допоміжні інструменти налаштування | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Допоміжні функції для кількох облікових записів | Допоміжні функції списку/конфігурації/гейтів дій облікових записів |
  | `plugin-sdk/account-id` | Допоміжні функції account-id | `DEFAULT_ACCOUNT_ID`, нормалізація account-id |
  | `plugin-sdk/account-resolution` | Допоміжні функції пошуку облікового запису | Допоміжні функції пошуку облікового запису + запасного значення за замовчуванням |
  | `plugin-sdk/account-helpers` | Вузькі допоміжні функції облікових записів | Допоміжні функції списку облікових записів/дій над обліковими записами |
  | `plugin-sdk/channel-setup` | Адаптери майстра налаштування | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, а також `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Примітиви парування DM | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Налаштування префікса відповіді + набору тексту | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Фабрики адаптерів конфігурації | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Побудовники схем конфігурації | Типи схем конфігурації каналу |
  | `plugin-sdk/telegram-command-config` | Допоміжні функції конфігурації команд Telegram | Нормалізація назв команд, обрізання опису, перевірка дублікатів/конфліктів |
  | `plugin-sdk/channel-policy` | Визначення політики груп/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Відстеження статусу облікових записів | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Допоміжні функції вхідного envelope | Спільні допоміжні функції маршрутизації + побудовника envelope |
  | `plugin-sdk/inbound-reply-dispatch` | Допоміжні функції вхідних відповідей | Спільні допоміжні функції запису та диспетчеризації |
  | `plugin-sdk/messaging-targets` | Розбір цілей повідомлень | Допоміжні функції розбору/зіставлення цілей |
  | `plugin-sdk/outbound-media` | Допоміжні функції вихідних медіа | Спільне завантаження вихідних медіа |
  | `plugin-sdk/outbound-runtime` | Допоміжні функції середовища виконання вихідних операцій | Допоміжні функції ідентичності вихідних операцій/делегування надсилання |
  | `plugin-sdk/thread-bindings-runtime` | Допоміжні функції прив’язки потоків | Життєвий цикл прив’язки потоків і допоміжні функції адаптерів |
  | `plugin-sdk/agent-media-payload` | Застарілі допоміжні функції корисного навантаження медіа | Побудовник корисного навантаження медіа агента для застарілих макетів полів |
  | `plugin-sdk/channel-runtime` | Застарілий shim сумісності | Лише застарілі утиліти середовища виконання каналу |
  | `plugin-sdk/channel-send-result` | Типи результату надсилання | Типи результатів відповідей |
  | `plugin-sdk/runtime-store` | Постійне сховище плагіна | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Широкі допоміжні функції середовища виконання | Допоміжні функції середовища виконання/логування/резервного копіювання/встановлення плагіна |
  | `plugin-sdk/runtime-env` | Вузькі допоміжні функції runtime env | Допоміжні функції logger/runtime env, timeout, retry і backoff |
  | `plugin-sdk/plugin-runtime` | Спільні допоміжні функції runtime плагіна | Допоміжні функції команд/хуків/http/інтерактивності плагіна |
  | `plugin-sdk/hook-runtime` | Допоміжні функції конвеєра хуків | Спільні допоміжні функції конвеєра webhook/внутрішніх хуків |
  | `plugin-sdk/lazy-runtime` | Допоміжні функції ледачого середовища виконання | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Допоміжні функції процесів | Спільні допоміжні функції exec |
  | `plugin-sdk/cli-runtime` | Допоміжні функції середовища виконання CLI | Форматування команд, очікування, допоміжні функції версій |
  | `plugin-sdk/gateway-runtime` | Допоміжні функції Gateway | Клієнт Gateway і допоміжні функції латок статусу каналу |
  | `plugin-sdk/config-runtime` | Допоміжні функції конфігурації | Допоміжні функції завантаження/запису конфігурації |
  | `plugin-sdk/telegram-command-config` | Допоміжні функції команд Telegram | Допоміжні функції перевірки команд Telegram зі стабільним fallback, коли поверхня контракту вбудованого Telegram недоступна |
  | `plugin-sdk/approval-runtime` | Допоміжні функції запитів на схвалення | Корисне навантаження схвалення exec/плагіна, допоміжні функції можливостей/профілів схвалення, нативна маршрутизація схвалення/допоміжні функції runtime |
  | `plugin-sdk/approval-auth-runtime` | Допоміжні функції auth для схвалення | Визначення схвалювача, auth дій у тому самому чаті |
  | `plugin-sdk/approval-client-runtime` | Допоміжні функції клієнта схвалення | Допоміжні функції профілю/фільтра нативного схвалення exec |
  | `plugin-sdk/approval-delivery-runtime` | Допоміжні функції доставки схвалення | Адаптери можливостей/доставки нативного схвалення |
  | `plugin-sdk/approval-native-runtime` | Допоміжні функції цілей схвалення | Допоміжні функції прив’язки цілі/облікового запису нативного схвалення |
  | `plugin-sdk/approval-reply-runtime` | Допоміжні функції відповіді на схвалення | Допоміжні функції корисного навантаження відповіді для схвалення exec/плагіна |
  | `plugin-sdk/security-runtime` | Допоміжні функції безпеки | Спільні допоміжні функції довіри, DM gating, external-content і збирання секретів |
  | `plugin-sdk/ssrf-policy` | Допоміжні функції політики SSRF | Допоміжні функції allowlist хостів і політики приватних мереж |
  | `plugin-sdk/ssrf-runtime` | Допоміжні функції runtime SSRF | Pinned-dispatcher, guarded fetch, допоміжні функції політики SSRF |
  | `plugin-sdk/collection-runtime` | Допоміжні функції обмеженого кешу | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Допоміжні функції діагностичного gating | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Допоміжні функції форматування помилок | `formatUncaughtError`, `isApprovalNotFoundError`, допоміжні функції графа помилок |
  | `plugin-sdk/fetch-runtime` | Допоміжні функції обгорнутого fetch/proxy | `resolveFetch`, допоміжні функції proxy |
  | `plugin-sdk/host-runtime` | Допоміжні функції нормалізації хоста | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Допоміжні функції retry | `RetryConfig`, `retryAsync`, виконавці політик |
  | `plugin-sdk/allow-from` | Форматування allowlist | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Мапування вхідних даних allowlist | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Gating команд і допоміжні функції поверхні команд | `resolveControlCommandGate`, допоміжні функції авторизації відправника, допоміжні функції реєстру команд |
  | `plugin-sdk/secret-input` | Розбір секретного введення | Допоміжні функції секретного введення |
  | `plugin-sdk/webhook-ingress` | Допоміжні функції запитів webhook | Утиліти цілей webhook |
  | `plugin-sdk/webhook-request-guards` | Допоміжні функції guard для тіла webhook | Допоміжні функції читання/обмеження тіла запиту |
  | `plugin-sdk/reply-runtime` | Спільне середовище виконання відповідей | Вхідна диспетчеризація, heartbeat, планувальник відповіді, chunking |
  | `plugin-sdk/reply-dispatch-runtime` | Вузькі допоміжні функції диспетчеризації відповідей | Допоміжні функції фіналізації + диспетчеризації провайдера |
  | `plugin-sdk/reply-history` | Допоміжні функції історії відповідей | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Планування посилань відповіді | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Допоміжні функції chunk відповіді | Допоміжні функції chunking тексту/markdown |
  | `plugin-sdk/session-store-runtime` | Допоміжні функції сховища сесій | Допоміжні функції шляху сховища + updated-at |
  | `plugin-sdk/state-paths` | Допоміжні функції шляхів стану | Допоміжні функції каталогів state і OAuth |
  | `plugin-sdk/routing` | Допоміжні функції маршрутизації/session-key | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, допоміжні функції нормалізації session-key |
  | `plugin-sdk/status-helpers` | Допоміжні функції статусу каналу | Побудовники зведень статусу каналу/облікового запису, значення runtime-state за замовчуванням, допоміжні функції метаданих проблем |
  | `plugin-sdk/target-resolver-runtime` | Допоміжні функції визначення цілі | Спільні допоміжні функції визначення цілі |
  | `plugin-sdk/string-normalization-runtime` | Допоміжні функції нормалізації рядків | Допоміжні функції нормалізації slug/рядків |
  | `plugin-sdk/request-url` | Допоміжні функції URL запиту | Витягнення рядкових URL із вхідних даних, схожих на запит |
  | `plugin-sdk/run-command` | Допоміжні функції команд із тайм-аутом | Виконавець команд із тайм-аутом і нормалізованими stdout/stderr |
  | `plugin-sdk/param-readers` | Зчитувачі параметрів | Поширені зчитувачі параметрів інструментів/CLI |
  | `plugin-sdk/tool-send` | Витягнення надсилання інструменту | Витягнення канонічних полів цілі надсилання з аргументів інструменту |
  | `plugin-sdk/temp-path` | Допоміжні функції тимчасових шляхів | Спільні допоміжні функції шляхів для тимчасових завантажень |
  | `plugin-sdk/logging-core` | Допоміжні функції логування | Логер підсистеми та допоміжні функції редагування |
  | `plugin-sdk/markdown-table-runtime` | Допоміжні функції markdown-таблиць | Допоміжні функції режиму markdown-таблиць |
  | `plugin-sdk/reply-payload` | Типи корисного навантаження відповіді | Типи корисного навантаження відповіді |
  | `plugin-sdk/provider-setup` | Кураторські допоміжні функції налаштування локального/self-hosted провайдера | Допоміжні функції виявлення/конфігурації self-hosted провайдера |
  | `plugin-sdk/self-hosted-provider-setup` | Вузькоспрямовані допоміжні функції налаштування self-hosted провайдера, сумісного з OpenAI | Ті самі допоміжні функції виявлення/конфігурації self-hosted провайдера |
  | `plugin-sdk/provider-auth-runtime` | Допоміжні функції runtime auth провайдера | Допоміжні функції визначення API-ключа під час виконання |
  | `plugin-sdk/provider-auth-api-key` | Допоміжні функції налаштування API-ключа провайдера | Допоміжні функції онбордингу API-ключа/запису профілю |
  | `plugin-sdk/provider-auth-result` | Допоміжні функції результату auth провайдера | Стандартний побудовник результату auth OAuth |
  | `plugin-sdk/provider-auth-login` | Допоміжні функції інтерактивного входу провайдера | Спільні допоміжні функції інтерактивного входу |
  | `plugin-sdk/provider-env-vars` | Допоміжні функції env vars провайдера | Допоміжні функції пошуку env vars для auth провайдера |
  | `plugin-sdk/provider-model-shared` | Спільні допоміжні функції моделей/повторів провайдера | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, спільні побудовники replay-policy, допоміжні функції endpoint провайдера та нормалізації model-id |
  | `plugin-sdk/provider-catalog-shared` | Спільні допоміжні функції каталогу провайдера | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Латки онбордингу провайдера | Допоміжні функції конфігурації онбордингу |
  | `plugin-sdk/provider-http` | Допоміжні функції HTTP провайдера | Загальні допоміжні функції HTTP/можливостей endpoint провайдера |
  | `plugin-sdk/provider-web-fetch` | Допоміжні функції web-fetch провайдера | Допоміжні функції реєстрації/кешу провайдера web-fetch |
  | `plugin-sdk/provider-web-search` | Допоміжні функції web-search провайдера | Допоміжні функції реєстрації/кешу/конфігурації провайдера web-search |
  | `plugin-sdk/provider-tools` | Допоміжні функції сумісності інструментів/схем провайдера | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, очищення схем Gemini + діагностика та допоміжні функції сумісності xAI, такі як `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Допоміжні функції використання провайдера | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` та інші допоміжні функції використання провайдера |
  | `plugin-sdk/provider-stream` | Допоміжні функції обгорток потоків провайдера | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, типи обгорток потоків і спільні допоміжні функції обгорток Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Впорядкована асинхронна черга | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Спільні допоміжні функції медіа | Допоміжні функції отримання/перетворення/зберігання медіа, а також побудовники корисного навантаження медіа |
  | `plugin-sdk/media-understanding` | Допоміжні функції media-understanding | Типи провайдерів media-understanding та експорти допоміжних функцій для зображень/аудіо, орієнтовані на провайдерів |
  | `plugin-sdk/text-runtime` | Спільні допоміжні функції тексту | Видалення видимого для помічника тексту, допоміжні функції рендерингу/chunking/table для markdown, редагування, теги директив, утиліти безпечного тексту та пов’язані допоміжні функції тексту/логування |
  | `plugin-sdk/text-chunking` | Допоміжні функції chunking тексту | Допоміжна функція chunking вихідного тексту |
  | `plugin-sdk/speech` | Допоміжні функції speech | Типи провайдерів speech та експорти допоміжних функцій директив, реєстру й перевірки, орієнтовані на провайдерів |
  | `plugin-sdk/speech-core` | Спільне ядро speech | Типи провайдерів speech, реєстр, директиви, нормалізація |
  | `plugin-sdk/realtime-transcription` | Допоміжні функції транскрипції в реальному часі | Типи провайдерів і допоміжні функції реєстру |
  | `plugin-sdk/realtime-voice` | Допоміжні функції голосу в реальному часі | Типи провайдерів і допоміжні функції реєстру |
  | `plugin-sdk/image-generation-core` | Спільне ядро генерації зображень | Допоміжні функції типів, failover, auth і реєстру для генерації зображень |
  | `plugin-sdk/music-generation` | Допоміжні функції генерації музики | Типи провайдера/запиту/результату генерації музики |
  | `plugin-sdk/music-generation-core` | Спільне ядро генерації музики | Допоміжні функції типів, failover, пошуку провайдера та розбору model-ref для генерації музики |
  | `plugin-sdk/video-generation` | Допоміжні функції генерації відео | Типи провайдера/запиту/результату генерації відео |
  | `plugin-sdk/video-generation-core` | Спільне ядро генерації відео | Допоміжні функції типів, failover, пошуку провайдера та розбору model-ref для генерації відео |
  | `plugin-sdk/interactive-runtime` | Допоміжні функції інтерактивних відповідей | Нормалізація/зведення корисного навантаження інтерактивних відповідей |
  | `plugin-sdk/channel-config-primitives` | Примітиви конфігурації каналу | Вузькі примітиви channel config-schema |
  | `plugin-sdk/channel-config-writes` | Допоміжні функції запису конфігурації каналу | Допоміжні функції авторизації запису конфігурації каналу |
  | `plugin-sdk/channel-plugin-common` | Спільний channel prelude | Експорти спільного channel prelude плагіна |
  | `plugin-sdk/channel-status` | Допоміжні функції статусу каналу | Спільні допоміжні функції snapshot/summary статусу каналу |
  | `plugin-sdk/allowlist-config-edit` | Допоміжні функції конфігурації allowlist | Допоміжні функції редагування/читання конфігурації allowlist |
  | `plugin-sdk/group-access` | Допоміжні функції доступу до груп | Спільні допоміжні функції рішень щодо доступу до груп |
  | `plugin-sdk/direct-dm` | Допоміжні функції прямих DM | Спільні допоміжні функції auth/guard для прямих DM |
  | `plugin-sdk/extension-shared` | Спільні допоміжні функції розширень | Примітиви допоміжних функцій пасивного каналу/статусу |
  | `plugin-sdk/webhook-targets` | Допоміжні функції цілей webhook | Реєстр цілей webhook і допоміжні функції встановлення маршрутів |
  | `plugin-sdk/webhook-path` | Допоміжні функції шляхів webhook | Допоміжні функції нормалізації шляхів webhook |
  | `plugin-sdk/web-media` | Спільні допоміжні функції web media | Допоміжні функції завантаження віддалених/локальних медіа |
  | `plugin-sdk/zod` | Повторний експорт zod | Повторно експортований `zod` для споживачів SDK плагінів |
  | `plugin-sdk/memory-core` | Допоміжні функції вбудованого memory-core | Поверхня допоміжних функцій memory manager/config/file/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | Фасад runtime рушія пам’яті | Фасад runtime індексації/пошуку пам’яті |
  | `plugin-sdk/memory-core-host-engine-foundation` | Foundation-рушій хоста пам’яті | Експорти foundation-рушія хоста пам’яті |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Рушій embeddings хоста пам’яті | Експорти рушія embeddings хоста пам’яті |
  | `plugin-sdk/memory-core-host-engine-qmd` | QMD-рушій хоста пам’яті | Експорти QMD-рушія хоста пам’яті |
  | `plugin-sdk/memory-core-host-engine-storage` | Рушій зберігання хоста пам’яті | Експорти рушія зберігання хоста пам’яті |
  | `plugin-sdk/memory-core-host-multimodal` | Мультимодальні допоміжні функції хоста пам’яті | Мультимодальні допоміжні функції хоста пам’яті |
  | `plugin-sdk/memory-core-host-query` | Допоміжні функції запитів хоста пам’яті | Допоміжні функції запитів хоста пам’яті |
  | `plugin-sdk/memory-core-host-secret` | Допоміжні функції секретів хоста пам’яті | Допоміжні функції секретів хоста пам’яті |
  | `plugin-sdk/memory-core-host-status` | Допоміжні функції статусу хоста пам’яті | Допоміжні функції статусу хоста пам’яті |
  | `plugin-sdk/memory-core-host-runtime-cli` | CLI runtime хоста пам’яті | Допоміжні функції CLI runtime хоста пам’яті |
  | `plugin-sdk/memory-core-host-runtime-core` | Core runtime хоста пам’яті | Допоміжні функції core runtime хоста пам’яті |
  | `plugin-sdk/memory-core-host-runtime-files` | Допоміжні функції файлів/runtime хоста пам’яті | Допоміжні функції файлів/runtime хоста пам’яті |
  | `plugin-sdk/memory-lancedb` | Допоміжні функції вбудованого memory-lancedb | Поверхня допоміжних функцій memory-lancedb |
  | `plugin-sdk/testing` | Тестові утиліти | Допоміжні функції та мок-об’єкти для тестування |
</Accordion>

Ця таблиця навмисно охоплює поширену підмножину для міграції, а не всю
поверхню SDK. Повний список із понад 200 точок входу міститься у
`scripts/lib/plugin-sdk-entrypoints.json`.

Цей список усе ще включає деякі допоміжні шви вбудованих плагінів, наприклад
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` і `plugin-sdk/matrix*`. Вони й надалі експортуються для
підтримки вбудованих плагінів і сумісності, але навмисно не включені до
поширеної таблиці міграції й не є рекомендованою ціллю для
нового коду плагінів.

Те саме правило застосовується до інших сімейств вбудованих допоміжних функцій, зокрема:

- допоміжні функції підтримки браузера: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- поверхні вбудованих допоміжних функцій/плагінів, такі як `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` і `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` наразі надає вузьку
поверхню допоміжних функцій токенів `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` і `resolveCopilotApiToken`.

Використовуйте найвужчий імпорт, який відповідає завданню. Якщо ви не можете
знайти потрібний експорт, перевірте джерело в `src/plugin-sdk/` або запитайте в Discord.

## Графік вилучення

| Коли | Що відбувається |
| ---------------------- | ----------------------------------------------------------------------- |
| **Зараз** | Застарілі поверхні виводять попередження під час виконання |
| **Наступний мажорний реліз** | Застарілі поверхні буде вилучено; плагіни, які й далі їх використовують, перестануть працювати |

Усі core-плагіни вже перенесено. Зовнішнім плагінам слід виконати міграцію
до наступного мажорного релізу.

## Тимчасове вимкнення попереджень

Встановіть ці змінні середовища, поки працюєте над міграцією:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Це тимчасовий обхідний механізм, а не постійне рішення.

## Пов’язане

- [Початок роботи](/uk/plugins/building-plugins) — створіть свій перший плагін
- [Огляд SDK](/uk/plugins/sdk-overview) — повний довідник імпортів підшляхів
- [Плагіни каналів](/uk/plugins/sdk-channel-plugins) — створення плагінів каналів
- [Плагіни провайдерів](/uk/plugins/sdk-provider-plugins) — створення плагінів провайдерів
- [Внутрішня будова плагінів](/uk/plugins/architecture) — глибоке занурення в архітектуру
- [Маніфест плагіна](/uk/plugins/manifest) — довідник зі схеми маніфесту
