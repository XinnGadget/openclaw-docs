---
read_when:
    - Ви бачите попередження OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - Ви бачите попередження OPENCLAW_EXTENSION_API_DEPRECATED
    - Ви оновлюєте плагін до сучасної архітектури плагінів
    - Ви підтримуєте зовнішній плагін OpenClaw
sidebarTitle: Migrate to SDK
summary: Перехід із застарілого шару зворотної сумісності на сучасний Plugin SDK
title: Міграція Plugin SDK
x-i18n:
    generated_at: "2026-04-08T08:06:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7d86c9b03e01ddee25aa1c065ebf7fda2785242f8ee63d567b67521f35c8b2e3
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Міграція Plugin SDK

OpenClaw перейшов від широкого шару зворотної сумісності до сучасної
архітектури плагінів із цілеспрямованими, документованими імпортами. Якщо ваш
плагін було створено до появи нової архітектури, цей посібник допоможе вам
виконати міграцію.

## Що змінюється

Стара система плагінів надавала дві дуже широкі поверхні, які дозволяли
плагінам імпортувати все потрібне з єдиної точки входу:

- **`openclaw/plugin-sdk/compat`** — єдиний імпорт, який повторно експортував
  десятки допоміжних засобів. Його було запроваджено, щоб старіші плагіни на
  основі хуків продовжували працювати, поки будувалася нова архітектура
  плагінів.
- **`openclaw/extension-api`** — міст, який надавав плагінам прямий доступ до
  допоміжних засобів на стороні хоста, як-от вбудований засіб запуску агента.

Обидві поверхні тепер **застарілі**. Вони все ще працюють під час виконання,
але нові плагіни не повинні їх використовувати, а наявні плагіни мають
мігрувати до того, як наступний мажорний реліз їх прибере.

<Warning>
  Шар зворотної сумісності буде вилучено в одному з майбутніх мажорних релізів.
  Плагіни, які все ще імпортують із цих поверхонь, перестануть працювати, коли
  це станеться.
</Warning>

## Чому це змінилося

Старий підхід спричиняв проблеми:

- **Повільний запуск** — імпорт одного допоміжного засобу завантажував десятки
  не пов’язаних між собою модулів
- **Циклічні залежності** — широкі повторні експорти полегшували створення
  циклів імпорту
- **Нечітка API-поверхня** — не було способу зрозуміти, які експорти є
  стабільними, а які внутрішніми

Сучасний Plugin SDK це виправляє: кожен шлях імпорту (`openclaw/plugin-sdk/\<subpath\>`)
є невеликим, самодостатнім модулем із чітким призначенням і документованим
контрактом.

Застарілі зручні шви провайдерів для вбудованих каналів також прибрано.
Імпорти на кшталт `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
фірмові допоміжні шви каналів і
`openclaw/plugin-sdk/telegram-core` були приватними ярликами моносховища, а не
стабільними контрактами плагінів. Натомість використовуйте вузькі узагальнені
підшляхи SDK. Усередині робочого простору вбудованих плагінів зберігайте
допоміжні засоби, що належать провайдеру, у власному `api.ts` або
`runtime-api.ts` цього плагіна.

Поточні приклади вбудованих провайдерів:

- Anthropic зберігає допоміжні засоби потоку, специфічні для Claude, у власному
  шві `api.ts` / `contract-api.ts`
- OpenAI зберігає засоби побудови провайдерів, допоміжні засоби для моделей за
  замовчуванням і засоби побудови realtime-провайдерів у власному `api.ts`
- OpenRouter зберігає засіб побудови провайдера та допоміжні засоби
  онбордингу/конфігурації у власному `api.ts`

## Як виконати міграцію

<Steps>
  <Step title="Перенесіть обробники з native approval на факти можливостей">
    Плагіни каналів із підтримкою погодження тепер розкривають власну native-логіку погодження через
    `approvalCapability.nativeRuntime` разом зі спільним реєстром контексту виконання.

    Основні зміни:

    - Замініть `approvalCapability.handler.loadRuntime(...)` на
      `approvalCapability.nativeRuntime`
    - Перенесіть auth і доставку, специфічні для погоджень, із застарілої
      прив’язки `plugin.auth` / `plugin.approvals` до `approvalCapability`
    - `ChannelPlugin.approvals` було вилучено з публічного контракту
      channel-plugin; перенесіть поля delivery/native/render до `approvalCapability`
    - `plugin.auth` залишається лише для потоків входу/виходу каналу; хук auth
      для погоджень там більше не зчитується ядром
    - Реєструйте об’єкти часу виконання, що належать каналу, як-от клієнти,
      токени або Bolt apps, через `openclaw/plugin-sdk/channel-runtime-context`
    - Не надсилайте сповіщення про перенаправлення, що належать плагіну, з native-обробників погодження;
      тепер ядро відповідає за сповіщення про доставку в інше місце на основі фактичних результатів доставки
    - Під час передавання `channelRuntime` у `createChannelManager(...)`
      надавайте реальну поверхню `createPluginRuntime().channel`. Часткові стаби відхиляються.

    Див. `/plugins/sdk-channel-plugins`, щоб ознайомитися з поточною
    структурою можливостей погодження.

  </Step>

  <Step title="Перевірте резервну поведінку Windows wrapper">
    Якщо ваш плагін використовує `openclaw/plugin-sdk/windows-spawn`, нерозв’язані Windows-обгортки
    `.cmd`/`.bat` тепер завершуються закритою відмовою, якщо ви явно не передасте
    `allowShellFallback: true`.

    ```typescript
    // До
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Після
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Установлюйте це лише для довірених сумісних викликів, які свідомо
      // допускають резервний варіант через оболонку.
      allowShellFallback: true,
    });
    ```

    Якщо ваш код виклику свідомо не покладається на резервний варіант через
    оболонку, не встановлюйте `allowShellFallback`, а натомість обробляйте
    викинуту помилку.

  </Step>

  <Step title="Знайдіть застарілі імпорти">
    Знайдіть у своєму плагіні імпорти з будь-якої із застарілих поверхонь:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Замініть їх цілеспрямованими імпортами">
    Кожен експорт зі старої поверхні відповідає певному сучасному шляху імпорту:

    ```typescript
    // До (застарілий шар зворотної сумісності)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // Після (сучасні цілеспрямовані імпорти)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Для допоміжних засобів на стороні хоста використовуйте інжектований runtime плагіна
    замість прямого імпорту:

    ```typescript
    // До (застарілий міст extension-api)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Після (інжектований runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Такий самий шаблон застосовується й до інших допоміжних засобів застарілого моста:

    | Старий імпорт | Сучасний еквівалент |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | helpers сховища сесій | `api.runtime.agent.session.*` |

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
  | `plugin-sdk/plugin-entry` | Канонічний допоміжний засіб точки входу плагіна | `definePluginEntry` |
  | `plugin-sdk/core` | Застарілий зонтичний повторний експорт для визначень/конструкторів входу каналів | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Експорт кореневої схеми конфігурації | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Допоміжний засіб точки входу одного провайдера | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Цілеспрямовані визначення та конструктори входу каналів | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Спільні допоміжні засоби майстра налаштування | Запити allowlist, конструктори статусу налаштування |
  | `plugin-sdk/setup-runtime` | Допоміжні засоби часу виконання для налаштування | Адаптери патчів налаштування, безпечні для імпорту, допоміжні засоби lookup-note, `promptResolvedAllowFrom`, `splitSetupEntries`, делеговані проксі налаштування |
  | `plugin-sdk/setup-adapter-runtime` | Допоміжні засоби адаптера налаштування | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Допоміжні засоби інструментарію налаштування | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Допоміжні засоби для кількох облікових записів | Допоміжні засоби списку облікових записів/конфігурації/action-gate |
  | `plugin-sdk/account-id` | Допоміжні засоби account-id | `DEFAULT_ACCOUNT_ID`, нормалізація account-id |
  | `plugin-sdk/account-resolution` | Допоміжні засоби пошуку облікових записів | Допоміжні засоби пошуку облікових записів + fallback до значення за замовчуванням |
  | `plugin-sdk/account-helpers` | Вузькі допоміжні засоби облікових записів | Допоміжні засоби списку облікових записів/account-action |
  | `plugin-sdk/channel-setup` | Адаптери майстра налаштування | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, а також `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Примітиви DM pairing | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Префікс відповіді + логіка typing | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Фабрики адаптерів конфігурації | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Конструктори схем конфігурації | Типи схем конфігурації каналу |
  | `plugin-sdk/telegram-command-config` | Допоміжні засоби конфігурації команд Telegram | Нормалізація назв команд, обрізання описів, валідація дублікатів/конфліктів |
  | `plugin-sdk/channel-policy` | Визначення політик груп/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Відстеження статусу облікових записів | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Допоміжні засоби вхідного конверта | Спільні допоміжні засоби побудови маршруту + конверта |
  | `plugin-sdk/inbound-reply-dispatch` | Допоміжні засоби вхідних відповідей | Спільні допоміжні засоби запису й диспетчеризації |
  | `plugin-sdk/messaging-targets` | Парсинг цілей повідомлень | Допоміжні засоби парсингу/зіставлення цілей |
  | `plugin-sdk/outbound-media` | Допоміжні засоби вихідних медіа | Спільне завантаження вихідних медіа |
  | `plugin-sdk/outbound-runtime` | Допоміжні засоби вихідного runtime | Допоміжні засоби ідентичності/делегування надсилання |
  | `plugin-sdk/thread-bindings-runtime` | Допоміжні засоби thread-binding | Життєвий цикл thread-binding і допоміжні засоби адаптера |
  | `plugin-sdk/agent-media-payload` | Застарілі допоміжні засоби media payload | Конструктор media payload агента для застарілих макетів полів |
  | `plugin-sdk/channel-runtime` | Застарілий shim сумісності | Лише застарілі утиліти runtime каналу |
  | `plugin-sdk/channel-send-result` | Типи результатів надсилання | Типи результатів відповіді |
  | `plugin-sdk/runtime-store` | Постійне сховище плагіна | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Широкі допоміжні засоби runtime | Допоміжні засоби runtime/логування/резервного копіювання/встановлення плагінів |
  | `plugin-sdk/runtime-env` | Вузькі допоміжні засоби runtime env | Logger/runtime env, тайм-аут, retry і допоміжні засоби backoff |
  | `plugin-sdk/plugin-runtime` | Спільні допоміжні засоби runtime плагіна | Допоміжні засоби команд/хуків/http/interactive плагіна |
  | `plugin-sdk/hook-runtime` | Допоміжні засоби конвеєра хуків | Спільні допоміжні засоби конвеєра webhook/internal hook |
  | `plugin-sdk/lazy-runtime` | Допоміжні засоби lazy runtime | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Допоміжні засоби процесів | Спільні допоміжні засоби exec |
  | `plugin-sdk/cli-runtime` | Допоміжні засоби runtime CLI | Форматування команд, очікування, допоміжні засоби версії |
  | `plugin-sdk/gateway-runtime` | Допоміжні засоби gateway | Клієнт gateway і допоміжні засоби патчів статусу каналу |
  | `plugin-sdk/config-runtime` | Допоміжні засоби конфігурації | Допоміжні засоби завантаження/запису конфігурації |
  | `plugin-sdk/telegram-command-config` | Допоміжні засоби команд Telegram | Допоміжні засоби валідації команд Telegram зі стабільним fallback, коли поверхня контракту вбудованого Telegram недоступна |
  | `plugin-sdk/approval-runtime` | Допоміжні засоби запитів на погодження | Payload exec/plugin approval, допоміжні засоби capability/profile погодження, native-маршрутизація погодження/допоміжні засоби runtime |
  | `plugin-sdk/approval-auth-runtime` | Допоміжні засоби auth для погодження | Визначення approver, auth дій у тому самому чаті |
  | `plugin-sdk/approval-client-runtime` | Допоміжні засоби клієнта погодження | Допоміжні засоби profile/filter для native exec approval |
  | `plugin-sdk/approval-delivery-runtime` | Допоміжні засоби доставки погодження | Адаптери native approval capability/delivery |
  | `plugin-sdk/approval-gateway-runtime` | Допоміжні засоби gateway погодження | Спільний допоміжний засіб визначення approval gateway |
  | `plugin-sdk/approval-handler-adapter-runtime` | Допоміжні засоби адаптера погодження | Полегшені допоміжні засоби завантаження native-адаптера погодження для гарячих точок входу каналів |
  | `plugin-sdk/approval-handler-runtime` | Допоміжні засоби обробника погодження | Ширші допоміжні засоби runtime для обробника погодження; надавайте перевагу вужчим швам adapter/gateway, якщо їх достатньо |
  | `plugin-sdk/approval-native-runtime` | Допоміжні засоби цілей погодження | Допоміжні засоби прив’язки цілі/облікового запису для native approval |
  | `plugin-sdk/approval-reply-runtime` | Допоміжні засоби відповіді на погодження | Допоміжні засоби payload відповіді exec/plugin approval |
  | `plugin-sdk/channel-runtime-context` | Допоміжні засоби контексту runtime каналу | Узагальнені допоміжні засоби register/get/watch для контексту runtime каналу |
  | `plugin-sdk/security-runtime` | Допоміжні засоби безпеки | Спільні допоміжні засоби trust, DM gating, external-content і збирання секретів |
  | `plugin-sdk/ssrf-policy` | Допоміжні засоби політики SSRF | Допоміжні засоби allowlist хостів і політики приватної мережі |
  | `plugin-sdk/ssrf-runtime` | Допоміжні засоби runtime SSRF | Pinned-dispatcher, guarded fetch, допоміжні засоби політики SSRF |
  | `plugin-sdk/collection-runtime` | Допоміжні засоби обмеженого кешу | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Допоміжні засоби діагностичного gate | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Допоміжні засоби форматування помилок | `formatUncaughtError`, `isApprovalNotFoundError`, допоміжні засоби графа помилок |
  | `plugin-sdk/fetch-runtime` | Допоміжні засоби обгорнутого fetch/proxy | `resolveFetch`, допоміжні засоби proxy |
  | `plugin-sdk/host-runtime` | Допоміжні засоби нормалізації хоста | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Допоміжні засоби retry | `RetryConfig`, `retryAsync`, засоби запуску політик |
  | `plugin-sdk/allow-from` | Форматування allowlist | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Відображення вводу allowlist | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Command gating і допоміжні засоби поверхні команд | `resolveControlCommandGate`, допоміжні засоби авторизації відправника, допоміжні засоби реєстру команд |
  | `plugin-sdk/secret-input` | Парсинг вводу секретів | Допоміжні засоби вводу секретів |
  | `plugin-sdk/webhook-ingress` | Допоміжні засоби запитів webhook | Утиліти цілей webhook |
  | `plugin-sdk/webhook-request-guards` | Допоміжні засоби захисту тіла запиту webhook | Допоміжні засоби читання/обмеження тіла запиту |
  | `plugin-sdk/reply-runtime` | Спільний runtime відповіді | Вхідна диспетчеризація, heartbeat, планувальник відповідей, чанкування |
  | `plugin-sdk/reply-dispatch-runtime` | Вузькі допоміжні засоби диспетчеризації відповідей | Finalize + допоміжні засоби диспетчеризації провайдера |
  | `plugin-sdk/reply-history` | Допоміжні засоби історії відповідей | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Планування посилань на відповіді | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Допоміжні засоби чанкування відповідей | Допоміжні засоби чанкування тексту/markdown |
  | `plugin-sdk/session-store-runtime` | Допоміжні засоби сховища сесій | Допоміжні засоби шляху сховища + updated-at |
  | `plugin-sdk/state-paths` | Допоміжні засоби шляхів стану | Допоміжні засоби каталогів стану та OAuth |
  | `plugin-sdk/routing` | Допоміжні засоби маршрутизації/session-key | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, допоміжні засоби нормалізації session-key |
  | `plugin-sdk/status-helpers` | Допоміжні засоби статусу каналу | Конструктори зведень статусу каналу/облікового запису, значення runtime-state за замовчуванням, допоміжні засоби метаданих проблем |
  | `plugin-sdk/target-resolver-runtime` | Допоміжні засоби визначення цілей | Спільні допоміжні засоби визначення цілей |
  | `plugin-sdk/string-normalization-runtime` | Допоміжні засоби нормалізації рядків | Допоміжні засоби нормалізації slug/рядків |
  | `plugin-sdk/request-url` | Допоміжні засоби URL запитів | Витягання рядкових URL з input, подібних до запиту |
  | `plugin-sdk/run-command` | Допоміжні засоби команд із тайм-аутом | Запуск команд із тайм-аутом і нормалізованими stdout/stderr |
  | `plugin-sdk/param-readers` | Зчитувачі параметрів | Поширені зчитувачі параметрів tool/CLI |
  | `plugin-sdk/tool-send` | Витягання tool send | Витягання канонічних полів цілі надсилання з аргументів tool |
  | `plugin-sdk/temp-path` | Допоміжні засоби тимчасових шляхів | Спільні допоміжні засоби тимчасових шляхів завантаження |
  | `plugin-sdk/logging-core` | Допоміжні засоби логування | Logger підсистеми та допоміжні засоби редагування |
  | `plugin-sdk/markdown-table-runtime` | Допоміжні засоби markdown-table | Допоміжні засоби режимів markdown table |
  | `plugin-sdk/reply-payload` | Типи відповідей повідомлень | Типи payload відповіді |
  | `plugin-sdk/provider-setup` | Кураторовані допоміжні засоби налаштування локальних/self-hosted провайдерів | Допоміжні засоби виявлення/конфігурації self-hosted провайдерів |
  | `plugin-sdk/self-hosted-provider-setup` | Цілеспрямовані допоміжні засоби налаштування self-hosted провайдерів, сумісних з OpenAI | Ті самі допоміжні засоби виявлення/конфігурації self-hosted провайдерів |
  | `plugin-sdk/provider-auth-runtime` | Допоміжні засоби runtime auth провайдера | Допоміжні засоби визначення API-ключа під час виконання |
  | `plugin-sdk/provider-auth-api-key` | Допоміжні засоби налаштування API-ключа провайдера | Допоміжні засоби онбордингу/запису профілю API-ключа |
  | `plugin-sdk/provider-auth-result` | Допоміжні засоби auth-result провайдера | Стандартний конструктор OAuth auth-result |
  | `plugin-sdk/provider-auth-login` | Допоміжні засоби інтерактивного входу провайдера | Спільні допоміжні засоби інтерактивного входу |
  | `plugin-sdk/provider-env-vars` | Допоміжні засоби env var провайдера | Допоміжні засоби пошуку env var auth провайдера |
  | `plugin-sdk/provider-model-shared` | Спільні допоміжні засоби моделі/повтору провайдера | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, спільні конструктори replay-policy, допоміжні засоби endpoint провайдера та нормалізації model-id |
  | `plugin-sdk/provider-catalog-shared` | Спільні допоміжні засоби каталогу провайдерів | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Патчі онбордингу провайдера | Допоміжні засоби конфігурації онбордингу |
  | `plugin-sdk/provider-http` | Допоміжні засоби HTTP провайдера | Загальні допоміжні засоби HTTP/можливостей endpoint провайдера |
  | `plugin-sdk/provider-web-fetch` | Допоміжні засоби web-fetch провайдера | Допоміжні засоби реєстрації/кешування web-fetch провайдера |
  | `plugin-sdk/provider-web-search-config-contract` | Допоміжні засоби конфігурації web-search провайдера | Вузькі допоміжні засоби конфігурації/облікових даних web-search для провайдерів, яким не потрібна прив’язка ввімкнення плагіна |
  | `plugin-sdk/provider-web-search-contract` | Допоміжні засоби контракту web-search провайдера | Вузькі допоміжні засоби контракту конфігурації/облікових даних web-search, як-от `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` і scoped setter/getter облікових даних |
  | `plugin-sdk/provider-web-search` | Допоміжні засоби web-search провайдера | Допоміжні засоби реєстрації/кешування/runtime web-search провайдера |
  | `plugin-sdk/provider-tools` | Допоміжні засоби сумісності tool/schema провайдера | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, cleanup і діагностика схеми Gemini, а також допоміжні засоби сумісності xAI, як-от `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Допоміжні засоби usage провайдера | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` та інші допоміжні засоби usage провайдера |
  | `plugin-sdk/provider-stream` | Допоміжні засоби обгортки потоку провайдера | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, типи обгорток потоку та спільні допоміжні засоби обгортки для Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Упорядкована асинхронна черга | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Спільні допоміжні засоби медіа | Допоміжні засоби fetch/transform/store медіа плюс конструктори media payload |
  | `plugin-sdk/media-generation-runtime` | Спільні допоміжні засоби генерації медіа | Спільні допоміжні засоби failover, вибору кандидатів і повідомлень про відсутню модель для генерації зображень/відео/музики |
  | `plugin-sdk/media-understanding` | Допоміжні засоби media-understanding | Типи провайдерів media understanding плюс експорти допоміжних засобів для зображень/аудіо, орієнтовані на провайдера |
  | `plugin-sdk/text-runtime` | Спільні допоміжні засоби тексту | Видалення видимого для асистента тексту, допоміжні засоби рендерингу/чанкування/table для markdown, засоби редагування, допоміжні засоби тегів директив, утиліти безпечного тексту та пов’язані допоміжні засоби тексту/логування |
  | `plugin-sdk/text-chunking` | Допоміжні засоби чанкування тексту | Допоміжний засіб чанкування вихідного тексту |
  | `plugin-sdk/speech` | Допоміжні засоби speech | Типи speech-провайдерів плюс орієнтовані на провайдера експорти директив, реєстру та валідації |
  | `plugin-sdk/speech-core` | Спільне ядро speech | Типи speech-провайдерів, реєстр, директиви, нормалізація |
  | `plugin-sdk/realtime-transcription` | Допоміжні засоби realtime transcription | Типи провайдерів і допоміжні засоби реєстру |
  | `plugin-sdk/realtime-voice` | Допоміжні засоби realtime voice | Типи провайдерів і допоміжні засоби реєстру |
  | `plugin-sdk/image-generation-core` | Спільне ядро генерації зображень | Типи генерації зображень, failover, auth і допоміжні засоби реєстру |
  | `plugin-sdk/music-generation` | Допоміжні засоби генерації музики | Типи провайдера/запиту/результату генерації музики |
  | `plugin-sdk/music-generation-core` | Спільне ядро генерації музики | Типи генерації музики, допоміжні засоби failover, пошуку провайдера та парсингу model-ref |
  | `plugin-sdk/video-generation` | Допоміжні засоби генерації відео | Типи провайдера/запиту/результату генерації відео |
  | `plugin-sdk/video-generation-core` | Спільне ядро генерації відео | Типи генерації відео, допоміжні засоби failover, пошуку провайдера та парсингу model-ref |
  | `plugin-sdk/interactive-runtime` | Допоміжні засоби interactive reply | Нормалізація/скорочення payload інтерактивної відповіді |
  | `plugin-sdk/channel-config-primitives` | Примітиви конфігурації каналу | Вузькі примітиви channel config-schema |
  | `plugin-sdk/channel-config-writes` | Допоміжні засоби запису конфігурації каналу | Допоміжні засоби авторизації запису конфігурації каналу |
  | `plugin-sdk/channel-plugin-common` | Спільна преамбула каналу | Експорти спільної преамбули channel plugin |
  | `plugin-sdk/channel-status` | Допоміжні засоби статусу каналу | Спільні допоміжні засоби snapshot/summary статусу каналу |
  | `plugin-sdk/allowlist-config-edit` | Допоміжні засоби конфігурації allowlist | Допоміжні засоби редагування/читання конфігурації allowlist |
  | `plugin-sdk/group-access` | Допоміжні засоби доступу до груп | Спільні допоміжні засоби прийняття рішень щодо group-access |
  | `plugin-sdk/direct-dm` | Допоміжні засоби direct-DM | Спільні допоміжні засоби auth/guard для direct-DM |
  | `plugin-sdk/extension-shared` | Спільні допоміжні засоби розширень | Примітиви passive-channel/status і ambient proxy helper |
  | `plugin-sdk/webhook-targets` | Допоміжні засоби цілей webhook | Реєстр цілей webhook і допоміжні засоби встановлення маршруту |
  | `plugin-sdk/webhook-path` | Допоміжні засоби шляхів webhook | Допоміжні засоби нормалізації шляхів webhook |
  | `plugin-sdk/web-media` | Спільні допоміжні засоби web media | Допоміжні засоби завантаження віддалених/локальних медіа |
  | `plugin-sdk/zod` | Повторний експорт zod | Повторно експортований `zod` для користувачів Plugin SDK |
  | `plugin-sdk/memory-core` | Вбудовані допоміжні засоби memory-core | Поверхня допоміжних засобів менеджера пам’яті/конфігурації/файлів/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | Фасад runtime рушія пам’яті | Фасад runtime індексу/пошуку пам’яті |
  | `plugin-sdk/memory-core-host-engine-foundation` | Foundation engine хоста пам’яті | Експорти foundation engine хоста пам’яті |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Embedding engine хоста пам’яті | Експорти embedding engine хоста пам’яті |
  | `plugin-sdk/memory-core-host-engine-qmd` | QMD engine хоста пам’яті | Експорти QMD engine хоста пам’яті |
  | `plugin-sdk/memory-core-host-engine-storage` | Storage engine хоста пам’яті | Експорти storage engine хоста пам’яті |
  | `plugin-sdk/memory-core-host-multimodal` | Допоміжні засоби multimodal хоста пам’яті | Допоміжні засоби multimodal хоста пам’яті |
  | `plugin-sdk/memory-core-host-query` | Допоміжні засоби запитів хоста пам’яті | Допоміжні засоби запитів хоста пам’яті |
  | `plugin-sdk/memory-core-host-secret` | Допоміжні засоби секретів хоста пам’яті | Допоміжні засоби секретів хоста пам’яті |
  | `plugin-sdk/memory-core-host-events` | Допоміжні засоби журналу подій хоста пам’яті | Допоміжні засоби журналу подій хоста пам’яті |
  | `plugin-sdk/memory-core-host-status` | Допоміжні засоби статусу хоста пам’яті | Допоміжні засоби статусу хоста пам’яті |
  | `plugin-sdk/memory-core-host-runtime-cli` | CLI runtime хоста пам’яті | Допоміжні засоби CLI runtime хоста пам’яті |
  | `plugin-sdk/memory-core-host-runtime-core` | Core runtime хоста пам’яті | Допоміжні засоби core runtime хоста пам’яті |
  | `plugin-sdk/memory-core-host-runtime-files` | Допоміжні засоби файлів/runtime хоста пам’яті | Допоміжні засоби файлів/runtime хоста пам’яті |
  | `plugin-sdk/memory-host-core` | Псевдонім core runtime хоста пам’яті | Нейтральний до постачальника псевдонім допоміжних засобів core runtime хоста пам’яті |
  | `plugin-sdk/memory-host-events` | Псевдонім журналу подій хоста пам’яті | Нейтральний до постачальника псевдонім допоміжних засобів журналу подій хоста пам’яті |
  | `plugin-sdk/memory-host-files` | Псевдонім файлів/runtime хоста пам’яті | Нейтральний до постачальника псевдонім допоміжних засобів файлів/runtime хоста пам’яті |
  | `plugin-sdk/memory-host-markdown` | Допоміжні засоби керованого markdown | Спільні допоміжні засоби керованого markdown для memory-adjacent плагінів |
  | `plugin-sdk/memory-host-search` | Фасад активного пошуку в пам’яті | Лінивий фасад runtime менеджера активного пошуку в пам’яті |
  | `plugin-sdk/memory-host-status` | Псевдонім статусу хоста пам’яті | Нейтральний до постачальника псевдонім допоміжних засобів статусу хоста пам’яті |
  | `plugin-sdk/memory-lancedb` | Вбудовані допоміжні засоби memory-lancedb | Поверхня допоміжних засобів memory-lancedb |
  | `plugin-sdk/testing` | Утиліти тестування | Допоміжні засоби тестування та mocks |
</Accordion>

Ця таблиця навмисно охоплює поширену підмножину для міграції, а не всю
поверхню SDK. Повний список із понад 200 точок входу міститься у
`scripts/lib/plugin-sdk-entrypoints.json`.

Цей список усе ще містить деякі допоміжні шви вбудованих плагінів, такі як
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` і `plugin-sdk/matrix*`. Вони й надалі експортуються для
підтримки та сумісності вбудованих плагінів, але навмисно
не включені до поширеної таблиці міграції й не є рекомендованою ціллю для
нового коду плагінів.

Те саме правило застосовується й до інших сімейств вбудованих допоміжних засобів, таких як:

- допоміжні засоби підтримки браузера: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- поверхні вбудованих helper/plugin, такі як `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` і `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` наразі надає вузьку поверхню допоміжних
засобів токенів `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` і `resolveCopilotApiToken`.

Використовуйте якнайвужчий імпорт, що відповідає потрібному завданню. Якщо ви
не можете знайти експорт, перевірте вихідний код у `src/plugin-sdk/` або
запитайте в Discord.

## Графік видалення

| Коли | Що відбувається |
| ---------------------- | ----------------------------------------------------------------------- |
| **Зараз** | Застарілі поверхні видають попередження під час виконання |
| **Наступний мажорний реліз** | Застарілі поверхні буде вилучено; плагіни, які все ще їх використовують, перестануть працювати |

Усі основні плагіни вже було мігровано. Зовнішнім плагінам слід виконати
міграцію до наступного мажорного релізу.

## Тимчасове приховування попереджень

Під час роботи над міграцією встановіть ці змінні середовища:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Це тимчасовий обхідний шлях, а не постійне рішення.

## Пов’язане

- [Початок роботи](/uk/plugins/building-plugins) — створіть свій перший плагін
- [Огляд SDK](/uk/plugins/sdk-overview) — повний довідник імпортів підшляхів
- [Плагіни каналів](/uk/plugins/sdk-channel-plugins) — створення плагінів каналів
- [Плагіни провайдерів](/uk/plugins/sdk-provider-plugins) — створення плагінів провайдерів
- [Внутрішня будова плагінів](/uk/plugins/architecture) — глибоке занурення в архітектуру
- [Маніфест плагіна](/uk/plugins/manifest) — довідник схеми маніфесту
