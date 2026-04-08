---
read_when:
    - Вам потрібно знати, з якого підшляху SDK імпортувати
    - Вам потрібен довідник для всіх методів реєстрації в OpenClawPluginApi
    - Ви шукаєте конкретний експорт SDK
sidebarTitle: SDK Overview
summary: Карта імпорту, довідник API реєстрації та архітектура SDK
title: Огляд Plugin SDK
x-i18n:
    generated_at: "2026-04-08T08:06:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: b5dd7a49caa262dd48d18b52782f1c2be3bdf25ec04494ccba38d4ed5b7956ea
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Огляд Plugin SDK

Plugin SDK — це типізований контракт між plugin і ядром. Ця сторінка є
довідником щодо **що імпортувати** і **що можна реєструвати**.

<Tip>
  **Шукаєте покроковий посібник?**
  - Перший plugin? Почніть із [Getting Started](/uk/plugins/building-plugins)
  - Channel plugin? Див. [Channel Plugins](/uk/plugins/sdk-channel-plugins)
  - Provider plugin? Див. [Provider Plugins](/uk/plugins/sdk-provider-plugins)
</Tip>

## Угода щодо імпорту

Завжди імпортуйте з конкретного підшляху:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Кожен підшлях — це невеликий самодостатній модуль. Це забезпечує швидкий
запуск і запобігає проблемам із циклічними залежностями. Для специфічних для channel
допоміжних засобів entry/build надавайте перевагу `openclaw/plugin-sdk/channel-core`; `openclaw/plugin-sdk/core`
залишайте для ширшої поверхні-парасольки та спільних допоміжних засобів, таких як
`buildChannelConfigSchema`.

Не додавайте і не покладайтеся на зручні шви, названі на честь provider, такі як
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`, або
допоміжні шви з брендингом channel. Вбудовані plugins мають компонувати узагальнені
підшляхи SDK у власних barrel-файлах `api.ts` або `runtime-api.ts`, а ядро
має або використовувати ці локальні barrel-файли plugin, або додавати вузький узагальнений контракт SDK,
коли потреба справді є між channel.

Згенерована карта експорту все ще містить невеликий набір допоміжних
швів для вбудованих plugins, таких як `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` і `plugin-sdk/matrix*`. Ці
підшляхи існують лише для супроводу вбудованих plugins і сумісності; їх
навмисно пропущено в загальній таблиці нижче, і вони не є рекомендованим
шляхом імпорту для нових сторонніх plugins.

## Довідник підшляхів

Найуживаніші підшляхи, згруповані за призначенням. Повний згенерований список
із понад 200 підшляхів міститься в `scripts/lib/plugin-sdk-entrypoints.json`.

Зарезервовані допоміжні підшляхи для вбудованих plugins усе ще з’являються в цьому
згенерованому списку. Розглядайте їх як поверхні деталей реалізації/сумісності, якщо лише сторінка документації
явно не просуває одну з них як публічну.

### Plugin entry

| Підшлях                    | Ключові експорти                                                                                                                     |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                  |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                     |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                    |

<AccordionGroup>
  <Accordion title="Підшляхи channel">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Експорт кореневої Zod-схеми `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, а також `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Спільні допоміжні засоби майстра налаштування, запити allowlist, побудовники статусу налаштування |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Допоміжні засоби для багатoакаунтної конфігурації/контролю дій, допоміжні засоби резервного акаунта за замовчуванням |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, допоміжні засоби нормалізації ID акаунта |
    | `plugin-sdk/account-resolution` | Допоміжні засоби пошуку акаунта + резервного використання значення за замовчуванням |
    | `plugin-sdk/account-helpers` | Вузькі допоміжні засоби для списку акаунтів/дій з акаунтом |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Типи схеми конфігурації channel |
    | `plugin-sdk/telegram-command-config` | Допоміжні засоби нормалізації/валідації користувацьких команд Telegram із резервною підтримкою контракту вбудованого plugin |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Спільні допоміжні засоби побудови вхідного route + envelope |
    | `plugin-sdk/inbound-reply-dispatch` | Спільні допоміжні засоби запису та диспетчеризації inbound |
    | `plugin-sdk/messaging-targets` | Допоміжні засоби розбору/зіставлення цілей |
    | `plugin-sdk/outbound-media` | Спільні допоміжні засоби завантаження вихідних медіа |
    | `plugin-sdk/outbound-runtime` | Допоміжні засоби для outbound identity/send delegate |
    | `plugin-sdk/thread-bindings-runtime` | Допоміжні засоби життєвого циклу thread-binding і адаптерів |
    | `plugin-sdk/agent-media-payload` | Застарілий побудовник медіапейлоаду агента |
    | `plugin-sdk/conversation-runtime` | Допоміжні засоби прив’язки conversation/thread, pairing і налаштованих binding |
    | `plugin-sdk/runtime-config-snapshot` | Допоміжний засіб знімка конфігурації runtime |
    | `plugin-sdk/runtime-group-policy` | Допоміжні засоби визначення group-policy у runtime |
    | `plugin-sdk/channel-status` | Спільні допоміжні засоби знімка/зведення статусу channel |
    | `plugin-sdk/channel-config-primitives` | Вузькі примітиви схеми конфігурації channel |
    | `plugin-sdk/channel-config-writes` | Допоміжні засоби авторизації запису конфігурації channel |
    | `plugin-sdk/channel-plugin-common` | Спільні prelude-експорти channel plugin |
    | `plugin-sdk/allowlist-config-edit` | Допоміжні засоби редагування/читання конфігурації allowlist |
    | `plugin-sdk/group-access` | Спільні допоміжні засоби рішень щодо group-access |
    | `plugin-sdk/direct-dm` | Спільні допоміжні засоби auth/guard для direct-DM |
    | `plugin-sdk/interactive-runtime` | Допоміжні засоби нормалізації/скорочення payload інтерактивних відповідей |
    | `plugin-sdk/channel-inbound` | Допоміжні засоби debounce для inbound, зіставлення mention, mention-policy та envelope |
    | `plugin-sdk/channel-send-result` | Типи результатів reply |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Допоміжні засоби розбору/зіставлення цілей |
    | `plugin-sdk/channel-contract` | Типи контракту channel |
    | `plugin-sdk/channel-feedback` | Інтеграція feedback/reaction |
    | `plugin-sdk/channel-secret-runtime` | Вузькі допоміжні засоби secret-contract, такі як `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment`, і типи secret target |
  </Accordion>

  <Accordion title="Підшляхи provider">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Кураторські допоміжні засоби налаштування local/self-hosted provider |
    | `plugin-sdk/self-hosted-provider-setup` | Сфокусовані допоміжні засоби налаштування self-hosted provider, сумісного з OpenAI |
    | `plugin-sdk/cli-backend` | Значення за замовчуванням для бекенда CLI + константи watchdog |
    | `plugin-sdk/provider-auth-runtime` | Допоміжні засоби визначення API-ключа у runtime для provider plugins |
    | `plugin-sdk/provider-auth-api-key` | Допоміжні засоби онбордингу/запису профілю API-ключа, такі як `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | Стандартний побудовник результату OAuth auth |
    | `plugin-sdk/provider-auth-login` | Спільні інтерактивні допоміжні засоби входу для provider plugins |
    | `plugin-sdk/provider-env-vars` | Допоміжні засоби пошуку env vars для auth provider |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, спільні побудовники replay-policy, допоміжні засоби endpoint provider та допоміжні засоби нормалізації model-id, такі як `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Узагальнені допоміжні засоби HTTP/можливостей endpoint для provider |
    | `plugin-sdk/provider-web-fetch-contract` | Вузькі допоміжні засоби контракту конфігурації/вибору web-fetch, такі як `enablePluginInConfig` і `WebFetchProviderPlugin` |
    | `plugin-sdk/provider-web-fetch` | Допоміжні засоби реєстрації/кешування provider web-fetch |
    | `plugin-sdk/provider-web-search-config-contract` | Вузькі допоміжні засоби конфігурації/облікових даних web-search для provider, яким не потрібна інтеграція ввімкнення plugin |
    | `plugin-sdk/provider-web-search-contract` | Вузькі допоміжні засоби контракту конфігурації/облікових даних web-search, такі як `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` і scoped setters/getters облікових даних |
    | `plugin-sdk/provider-web-search` | Допоміжні засоби реєстрації/кешування/runtime provider web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, очищення схеми Gemini + діагностика та допоміжні засоби сумісності xAI, такі як `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` та подібні |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, типи stream wrapper і спільні допоміжні засоби wrapper для Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Допоміжні засоби патчів конфігурації онбордингу |
    | `plugin-sdk/global-singleton` | Допоміжні засоби process-local singleton/map/cache |
  </Accordion>

  <Accordion title="Підшляхи auth і безпеки">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, допоміжні засоби реєстру команд, допоміжні засоби авторизації відправника |
    | `plugin-sdk/approval-auth-runtime` | Допоміжні засоби визначення approver і auth дій у тому самому чаті |
    | `plugin-sdk/approval-client-runtime` | Допоміжні засоби профілю/фільтра native exec approval |
    | `plugin-sdk/approval-delivery-runtime` | Native approval capability/delivery adapters |
    | `plugin-sdk/approval-gateway-runtime` | Спільний допоміжний засіб визначення approval gateway |
    | `plugin-sdk/approval-handler-adapter-runtime` | Полегшені допоміжні засоби завантаження native approval adapter для гарячих channel entrypoint |
    | `plugin-sdk/approval-handler-runtime` | Ширші допоміжні засоби runtime approval handler; надавайте перевагу вужчим adapter/gateway seams, коли їх достатньо |
    | `plugin-sdk/approval-native-runtime` | Допоміжні засоби native approval target + прив’язки акаунта |
    | `plugin-sdk/approval-reply-runtime` | Допоміжні засоби payload відповіді на exec/plugin approval |
    | `plugin-sdk/command-auth-native` | Допоміжні засоби native command auth + native session-target |
    | `plugin-sdk/command-detection` | Спільні допоміжні засоби виявлення команд |
    | `plugin-sdk/command-surface` | Нормалізація command-body і допоміжні засоби command-surface |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Вузькі допоміжні засоби збирання secret-contract для поверхонь секретів channel/plugin |
    | `plugin-sdk/secret-ref-runtime` | Вузькі допоміжні засоби `coerceSecretRef` і типізації SecretRef для парсингу secret-contract/config |
    | `plugin-sdk/security-runtime` | Спільні допоміжні засоби довіри, DM gating, зовнішнього вмісту та збирання секретів |
    | `plugin-sdk/ssrf-policy` | Допоміжні засоби allowlist хостів і політики SSRF для приватних мереж |
    | `plugin-sdk/ssrf-runtime` | Допоміжні засоби pinned-dispatcher, fetch із захистом SSRF і політики SSRF |
    | `plugin-sdk/secret-input` | Допоміжні засоби парсингу secret input |
    | `plugin-sdk/webhook-ingress` | Допоміжні засоби запиту/цілі webhook |
    | `plugin-sdk/webhook-request-guards` | Допоміжні засоби для розміру body/timeout запиту |
  </Accordion>

  <Accordion title="Підшляхи runtime і зберігання">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/runtime` | Широкі допоміжні засоби runtime/logging/backup/plugin-install |
    | `plugin-sdk/runtime-env` | Вузькі допоміжні засоби env runtime, logger, timeout, retry і backoff |
    | `plugin-sdk/channel-runtime-context` | Узагальнені допоміжні засоби реєстрації та пошуку channel runtime-context |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Спільні допоміжні засоби для команд/hook/http/interactive plugin |
    | `plugin-sdk/hook-runtime` | Спільні допоміжні засоби pipeline внутрішніх hook/webhook |
    | `plugin-sdk/lazy-runtime` | Допоміжні засоби lazy runtime import/binding, такі як `createLazyRuntimeModule`, `createLazyRuntimeMethod` і `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Допоміжні засоби exec процесів |
    | `plugin-sdk/cli-runtime` | Допоміжні засоби форматування CLI, wait і version |
    | `plugin-sdk/gateway-runtime` | Допоміжні засоби клієнта gateway і патчів статусу channel |
    | `plugin-sdk/config-runtime` | Допоміжні засоби завантаження/запису конфігурації |
    | `plugin-sdk/telegram-command-config` | Нормалізація назви/опису команд Telegram і перевірки дублікатів/конфліктів, навіть коли поверхня контракту вбудованого Telegram недоступна |
    | `plugin-sdk/approval-runtime` | Допоміжні засоби exec/plugin approval, побудовники approval-capability, допоміжні засоби auth/profile, native routing/runtime |
    | `plugin-sdk/reply-runtime` | Спільні допоміжні засоби inbound/reply runtime, chunking, dispatch, heartbeat, планувальник reply |
    | `plugin-sdk/reply-dispatch-runtime` | Вузькі допоміжні засоби dispatch/finalize reply |
    | `plugin-sdk/reply-history` | Спільні допоміжні засоби коротковіконної історії reply, такі як `buildHistoryContext`, `recordPendingHistoryEntry` і `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Вузькі допоміжні засоби chunking тексту/markdown |
    | `plugin-sdk/session-store-runtime` | Допоміжні засоби шляху до session store + updated-at |
    | `plugin-sdk/state-paths` | Допоміжні засоби шляхів до каталогу state/OAuth |
    | `plugin-sdk/routing` | Допоміжні засоби прив’язки route/session-key/акаунта, такі як `resolveAgentRoute`, `buildAgentSessionKey` і `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Спільні допоміжні засоби зведення статусу channel/акаунта, значення за замовчуванням для runtime-state і допоміжні засоби метаданих проблем |
    | `plugin-sdk/target-resolver-runtime` | Спільні допоміжні засоби resolver цілей |
    | `plugin-sdk/string-normalization-runtime` | Допоміжні засоби нормалізації slug/рядків |
    | `plugin-sdk/request-url` | Витягування рядкових URL з fetch/request-подібних вхідних даних |
    | `plugin-sdk/run-command` | Виконавець команд із таймером і нормалізованими результатами stdout/stderr |
    | `plugin-sdk/param-readers` | Поширені читачі параметрів tool/CLI |
    | `plugin-sdk/tool-send` | Витягування канонічних полів цілі надсилання з аргументів tool |
    | `plugin-sdk/temp-path` | Спільні допоміжні засоби шляхів до тимчасових завантажень |
    | `plugin-sdk/logging-core` | Допоміжні засоби logger підсистеми та редагування чутливих даних |
    | `plugin-sdk/markdown-table-runtime` | Допоміжні засоби режиму таблиць Markdown |
    | `plugin-sdk/json-store` | Невеликі допоміжні засоби читання/запису JSON state |
    | `plugin-sdk/file-lock` | Реентерабельні допоміжні засоби file-lock |
    | `plugin-sdk/persistent-dedupe` | Допоміжні засоби дискового кешу dedupe |
    | `plugin-sdk/acp-runtime` | Допоміжні засоби ACP runtime/session і reply-dispatch |
    | `plugin-sdk/agent-config-primitives` | Вузькі примітиви схеми конфігурації runtime агента |
    | `plugin-sdk/boolean-param` | Читач нечітких boolean-параметрів |
    | `plugin-sdk/dangerous-name-runtime` | Допоміжні засоби визначення збігів небезпечних імен |
    | `plugin-sdk/device-bootstrap` | Допоміжні засоби bootstrap пристрою та токенів pairing |
    | `plugin-sdk/extension-shared` | Спільні примітиви допоміжних засобів passive-channel, status і ambient proxy |
    | `plugin-sdk/models-provider-runtime` | Допоміжні засоби відповіді provider/команди `/models` |
    | `plugin-sdk/skill-commands-runtime` | Допоміжні засоби переліку команд Skills |
    | `plugin-sdk/native-command-registry` | Допоміжні засоби реєстру/build/serialize native команд |
    | `plugin-sdk/provider-zai-endpoint` | Допоміжні засоби виявлення endpoint Z.AI |
    | `plugin-sdk/infra-runtime` | Допоміжні засоби системних подій/heartbeat |
    | `plugin-sdk/collection-runtime` | Невеликі допоміжні засоби обмеженого кешу |
    | `plugin-sdk/diagnostic-runtime` | Допоміжні засоби діагностичних прапорців і подій |
    | `plugin-sdk/error-runtime` | Граф помилок, форматування, спільні допоміжні засоби класифікації помилок, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Допоміжні засоби обгорнутого fetch, proxy і pinned lookup |
    | `plugin-sdk/host-runtime` | Допоміжні засоби нормалізації hostname і SCP host |
    | `plugin-sdk/retry-runtime` | Допоміжні засоби конфігурації retry та запуску retry |
    | `plugin-sdk/agent-runtime` | Допоміжні засоби каталогу/ідентичності/workspace агента |
    | `plugin-sdk/directory-runtime` | Запит/усунення дублікатів каталогу на основі конфігурації |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Підшляхи можливостей і тестування">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Спільні допоміжні засоби fetch/transform/store медіа, а також побудовники медіапейлоадів |
    | `plugin-sdk/media-generation-runtime` | Спільні допоміжні засоби failover для генерації медіа, вибір кандидатів і повідомлення про відсутню модель |
    | `plugin-sdk/media-understanding` | Типи provider для розуміння медіа, а також експорти допоміжних засобів для зображень/аудіо з боку provider |
    | `plugin-sdk/text-runtime` | Спільні допоміжні засоби для тексту/markdown/logging, такі як видалення видимого для асистента тексту, допоміжні засоби render/chunking/table для markdown, редагування чутливих даних, допоміжні засоби тегів директив і утиліти безпечного тексту |
    | `plugin-sdk/text-chunking` | Допоміжний засіб chunking вихідного тексту |
    | `plugin-sdk/speech` | Типи provider мовлення, а також допоміжні засоби директив, реєстру і валідації з боку provider |
    | `plugin-sdk/speech-core` | Спільні допоміжні засоби типів, реєстру, директив і нормалізації для provider мовлення |
    | `plugin-sdk/realtime-transcription` | Типи provider транскрипції в реальному часі та допоміжні засоби реєстру |
    | `plugin-sdk/realtime-voice` | Типи provider голосу в реальному часі та допоміжні засоби реєстру |
    | `plugin-sdk/image-generation` | Типи provider генерації зображень |
    | `plugin-sdk/image-generation-core` | Спільні допоміжні засоби типів, failover, auth і реєстру для генерації зображень |
    | `plugin-sdk/music-generation` | Типи provider/request/result для генерації музики |
    | `plugin-sdk/music-generation-core` | Спільні допоміжні засоби типів, failover, пошуку provider і парсингу model-ref для генерації музики |
    | `plugin-sdk/video-generation` | Типи provider/request/result для генерації відео |
    | `plugin-sdk/video-generation-core` | Спільні допоміжні засоби типів, failover, пошуку provider і парсингу model-ref для генерації відео |
    | `plugin-sdk/webhook-targets` | Реєстр цілей webhook і допоміжні засоби встановлення route |
    | `plugin-sdk/webhook-path` | Допоміжні засоби нормалізації шляху webhook |
    | `plugin-sdk/web-media` | Спільні допоміжні засоби завантаження віддалених/локальних медіа |
    | `plugin-sdk/zod` | Повторно експортований `zod` для споживачів Plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Підшляхи пам’яті">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/memory-core` | Поверхня допоміжних засобів вбудованого memory-core для менеджера/конфігурації/файлів/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Фасад runtime для індексації/пошуку пам’яті |
    | `plugin-sdk/memory-core-host-engine-foundation` | Експорти foundation engine для хоста пам’яті |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Експорти embedding engine для хоста пам’яті |
    | `plugin-sdk/memory-core-host-engine-qmd` | Експорти QMD engine для хоста пам’яті |
    | `plugin-sdk/memory-core-host-engine-storage` | Експорти storage engine для хоста пам’яті |
    | `plugin-sdk/memory-core-host-multimodal` | Допоміжні засоби multimodal для хоста пам’яті |
    | `plugin-sdk/memory-core-host-query` | Допоміжні засоби запитів для хоста пам’яті |
    | `plugin-sdk/memory-core-host-secret` | Допоміжні засоби секретів для хоста пам’яті |
    | `plugin-sdk/memory-core-host-events` | Допоміжні засоби журналу подій для хоста пам’яті |
    | `plugin-sdk/memory-core-host-status` | Допоміжні засоби статусу для хоста пам’яті |
    | `plugin-sdk/memory-core-host-runtime-cli` | Допоміжні засоби CLI runtime для хоста пам’яті |
    | `plugin-sdk/memory-core-host-runtime-core` | Допоміжні засоби core runtime для хоста пам’яті |
    | `plugin-sdk/memory-core-host-runtime-files` | Допоміжні засоби файлів/runtime для хоста пам’яті |
    | `plugin-sdk/memory-host-core` | Vendor-neutral псевдонім для допоміжних засобів core runtime хоста пам’яті |
    | `plugin-sdk/memory-host-events` | Vendor-neutral псевдонім для допоміжних засобів журналу подій хоста пам’яті |
    | `plugin-sdk/memory-host-files` | Vendor-neutral псевдонім для допоміжних засобів файлів/runtime хоста пам’яті |
    | `plugin-sdk/memory-host-markdown` | Спільні допоміжні засоби керованого markdown для plugins, суміжних із пам’яттю |
    | `plugin-sdk/memory-host-search` | Активний фасад runtime пам’яті для доступу до search-manager |
    | `plugin-sdk/memory-host-status` | Vendor-neutral псевдонім для допоміжних засобів статусу хоста пам’яті |
    | `plugin-sdk/memory-lancedb` | Поверхня допоміжних засобів вбудованого memory-lancedb |
  </Accordion>

  <Accordion title="Зарезервовані підшляхи вбудованих helper">
    | Сімейство | Поточні підшляхи | Призначення |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Допоміжні засоби підтримки вбудованого browser plugin (`browser-support` залишається barrel-файлом сумісності) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Поверхня helper/runtime для вбудованого Matrix |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Поверхня helper/runtime для вбудованого LINE |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Поверхня helper для вбудованого IRC |
    | Допоміжні засоби, специфічні для channel | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Шви сумісності/допоміжні засоби для вбудованих channel |
    | Допоміжні засоби, специфічні для auth/plugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Шви допоміжних засобів для вбудованих функцій/plugins; `plugin-sdk/github-copilot-token` зараз експортує `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` і `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API реєстрації

Зворотний виклик `register(api)` отримує об’єкт `OpenClawPluginApi` з такими
методами:

### Реєстрація можливостей

| Метод                                           | Що реєструє                     |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | Текстовий inference (LLM)        |
| `api.registerCliBackend(...)`                    | Локальний inference-бекенд CLI   |
| `api.registerChannel(...)`                       | Канал обміну повідомленнями      |
| `api.registerSpeechProvider(...)`                | Синтез text-to-speech / STT      |
| `api.registerRealtimeTranscriptionProvider(...)` | Потокову транскрипцію в реальному часі |
| `api.registerRealtimeVoiceProvider(...)`         | Дуплексні голосові сеанси в реальному часі |
| `api.registerMediaUnderstandingProvider(...)`    | Аналіз зображень/аудіо/відео     |
| `api.registerImageGenerationProvider(...)`       | Генерацію зображень              |
| `api.registerMusicGenerationProvider(...)`       | Генерацію музики                 |
| `api.registerVideoGenerationProvider(...)`       | Генерацію відео                  |
| `api.registerWebFetchProvider(...)`              | Provider web fetch / scrape      |
| `api.registerWebSearchProvider(...)`             | Вебпошук                         |

### Tools і команди

| Метод                          | Що реєструє                                  |
| ------------------------------- | -------------------------------------------- |
| `api.registerTool(tool, opts?)` | Tool агента (обов’язковий або `{ optional: true }`) |
| `api.registerCommand(def)`      | Користувацьку команду (обходить LLM)         |

### Інфраструктура

| Метод                                         | Що реєструє                            |
| ---------------------------------------------- | -------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook події                             |
| `api.registerHttpRoute(params)`                | HTTP endpoint gateway                  |
| `api.registerGatewayMethod(name, handler)`     | RPC-метод gateway                      |
| `api.registerCli(registrar, opts?)`            | Підкоманду CLI                         |
| `api.registerService(service)`                 | Фоновий сервіс                         |
| `api.registerInteractiveHandler(registration)` | Інтерактивний handler                  |
| `api.registerMemoryPromptSupplement(builder)`  | Додаткову секцію prompt, суміжну з пам’яттю |
| `api.registerMemoryCorpusSupplement(adapter)`  | Додатковий корпус для пошуку/читання пам’яті |

Зарезервовані простори імен адміністратора ядра (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) завжди залишаються `operator.admin`, навіть якщо plugin намагається призначити
вужчу область gateway method. Для методів, що належать plugin,
надавайте перевагу префіксам, специфічним для plugin.

### Метадані реєстрації CLI

`api.registerCli(registrar, opts?)` приймає два види метаданих верхнього рівня:

- `commands`: явні корені команд, якими володіє registrar
- `descriptors`: дескриптори команд на етапі парсингу, які використовуються для довідки кореневого CLI,
  маршрутизації та лінивої реєстрації CLI plugin

Якщо ви хочете, щоб команда plugin залишалася ледачо завантажуваною у звичайному шляху кореневого CLI,
надайте `descriptors`, які охоплюють кожен корінь команди верхнього рівня, доступний через цей
registrar.

```typescript
api.registerCli(
  async ({ program }) => {
    const { registerMatrixCli } = await import("./src/cli.js");
    registerMatrixCli({ program });
  },
  {
    descriptors: [
      {
        name: "matrix",
        description: "Керування акаунтами Matrix, верифікацією, пристроями та станом профілю",
        hasSubcommands: true,
      },
    ],
  },
);
```

Використовуйте лише `commands`, якщо вам не потрібна лінива реєстрація кореневого CLI.
Цей eager-шлях сумісності залишається підтримуваним, але він не встановлює
placeholders, підкріплені descriptor, для ледачого завантаження під час парсингу.

### Реєстрація бекенда CLI

`api.registerCliBackend(...)` дозволяє plugin володіти конфігурацією за замовчуванням для локального
бекенда CLI AI, такого як `codex-cli`.

- `id` бекенда стає префіксом provider у model ref, таких як `codex-cli/gpt-5`.
- `config` бекенда використовує ту саму форму, що й `agents.defaults.cliBackends.<id>`.
- Конфігурація користувача все одно має пріоритет. OpenClaw зливає `agents.defaults.cliBackends.<id>` поверх
  значення за замовчуванням plugin перед запуском CLI.
- Використовуйте `normalizeConfig`, коли бекенду потрібні переписування сумісності після злиття
  (наприклад, нормалізація старих форм прапорців).

### Ексклюзивні слоти

| Метод                                     | Що реєструє                                                                                                                                         |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Контекстний рушій (одночасно активний лише один). Зворотний виклик `assemble()` отримує `availableTools` і `citationsMode`, щоб рушій міг адаптувати додавання до prompt. |
| `api.registerMemoryCapability(capability)` | Уніфіковану можливість пам’яті                                                                                                                      |
| `api.registerMemoryPromptSection(builder)` | Побудовник секції prompt для пам’яті                                                                                                                |
| `api.registerMemoryFlushPlan(resolver)`    | Resolver плану flush для пам’яті                                                                                                                    |
| `api.registerMemoryRuntime(runtime)`       | Адаптер runtime пам’яті                                                                                                                             |

### Адаптери embedding для пам’яті

| Метод                                         | Що реєструє                                   |
| ---------------------------------------------- | --------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Адаптер embedding пам’яті для активного plugin |

- `registerMemoryCapability` — це рекомендований API ексклюзивного plugin пам’яті.
- `registerMemoryCapability` також може надавати `publicArtifacts.listArtifacts(...)`,
  щоб супровідні plugins могли використовувати експортовані артефакти пам’яті через
  `openclaw/plugin-sdk/memory-host-core` замість звернення до приватної
  структури конкретного plugin пам’яті.
- `registerMemoryPromptSection`, `registerMemoryFlushPlan` і
  `registerMemoryRuntime` — це застарілі, але сумісні API ексклюзивного plugin пам’яті.
- `registerMemoryEmbeddingProvider` дозволяє активному plugin пам’яті реєструвати один
  або більше ID адаптерів embedding (наприклад, `openai`, `gemini` або власний ID,
  визначений plugin).
- Конфігурація користувача, така як `agents.defaults.memorySearch.provider` і
  `agents.defaults.memorySearch.fallback`, визначається відносно зареєстрованих
  ID цих адаптерів.

### Події та життєвий цикл

| Метод                                       | Що робить                    |
| -------------------------------------------- | ---------------------------- |
| `api.on(hookName, handler, opts?)`           | Типізований hook життєвого циклу |
| `api.onConversationBindingResolved(handler)` | Зворотний виклик прив’язки conversation |

### Семантика рішень hook

- `before_tool_call`: повернення `{ block: true }` є термінальним. Щойно будь-який handler встановлює його, handler-и з нижчим пріоритетом пропускаються.
- `before_tool_call`: повернення `{ block: false }` вважається відсутністю рішення (так само, як і пропуск `block`), а не перевизначенням.
- `before_install`: повернення `{ block: true }` є термінальним. Щойно будь-який handler встановлює його, handler-и з нижчим пріоритетом пропускаються.
- `before_install`: повернення `{ block: false }` вважається відсутністю рішення (так само, як і пропуск `block`), а не перевизначенням.
- `reply_dispatch`: повернення `{ handled: true, ... }` є термінальним. Щойно будь-який handler заявляє про диспетчеризацію, handler-и з нижчим пріоритетом і типовий шлях диспетчеризації моделі пропускаються.
- `message_sending`: повернення `{ cancel: true }` є термінальним. Щойно будь-який handler встановлює його, handler-и з нижчим пріоритетом пропускаються.
- `message_sending`: повернення `{ cancel: false }` вважається відсутністю рішення (так само, як і пропуск `cancel`), а не перевизначенням.

### Поля об’єкта API

| Поле                    | Тип                       | Опис                                                                                           |
| ------------------------ | ------------------------- | ---------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | ID plugin                                                                                      |
| `api.name`               | `string`                  | Відображувана назва                                                                            |
| `api.version`            | `string?`                 | Версія plugin (необов’язково)                                                                  |
| `api.description`        | `string?`                 | Опис plugin (необов’язково)                                                                    |
| `api.source`             | `string`                  | Шлях до джерела plugin                                                                         |
| `api.rootDir`            | `string?`                 | Кореневий каталог plugin (необов’язково)                                                       |
| `api.config`             | `OpenClawConfig`          | Поточний знімок конфігурації (активний знімок runtime у пам’яті, якщо доступний)              |
| `api.pluginConfig`       | `Record<string, unknown>` | Конфігурація plugin з `plugins.entries.<id>.config`                                            |
| `api.runtime`            | `PluginRuntime`           | [Допоміжні засоби runtime](/uk/plugins/sdk-runtime)                                               |
| `api.logger`             | `PluginLogger`            | Logger з областю видимості (`debug`, `info`, `warn`, `error`)                                  |
| `api.registrationMode`   | `PluginRegistrationMode`  | Поточний режим завантаження; `"setup-runtime"` — це полегшене вікно запуску/налаштування до повного entry |
| `api.resolvePath(input)` | `(string) => string`      | Визначення шляху відносно кореня plugin                                                        |

## Угода щодо внутрішніх модулів

У межах вашого plugin використовуйте локальні barrel-файли для внутрішніх імпортів:

```
my-plugin/
  api.ts            # Публічні експорти для зовнішніх споживачів
  runtime-api.ts    # Внутрішні експорти лише для runtime
  index.ts          # Точка входу plugin
  setup-entry.ts    # Полегшена точка входу лише для налаштування (необов’язково)
```

<Warning>
  Ніколи не імпортуйте власний plugin через `openclaw/plugin-sdk/<your-plugin>`
  у production-коді. Спрямовуйте внутрішні імпорти через `./api.ts` або
  `./runtime-api.ts`. Шлях SDK — це лише зовнішній контракт.
</Warning>

Публічні поверхні вбудованих plugins, завантажувані через фасад (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` та подібні публічні entry-файли), тепер надають перевагу
активному знімку конфігурації runtime, якщо OpenClaw уже запущено. Якщо знімок runtime
ще не існує, вони повертаються до визначеного файла конфігурації на диску.

Provider plugins також можуть надавати вузький локальний barrel контракту plugin, коли
допоміжний засіб навмисно є специфічним для provider і ще не належить до узагальненого підшляху SDK.
Поточний вбудований приклад: provider Anthropic зберігає свої допоміжні засоби потоку Claude
у власному публічному шві `api.ts` / `contract-api.ts` замість
просування логіки Anthropic beta-header і `service_tier` до узагальненого
контракту `plugin-sdk/*`.

Інші поточні вбудовані приклади:

- `@openclaw/openai-provider`: `api.ts` експортує побудовники provider,
  допоміжні засоби моделей за замовчуванням і побудовники realtime provider
- `@openclaw/openrouter-provider`: `api.ts` експортує побудовник provider, а також
  допоміжні засоби онбордингу/конфігурації

<Warning>
  Production-код розширень також має уникати імпортів `openclaw/plugin-sdk/<other-plugin>`.
  Якщо допоміжний засіб справді є спільним, винесіть його до нейтрального підшляху SDK,
  такого як `openclaw/plugin-sdk/speech`, `.../provider-model-shared` або іншої
  поверхні, орієнтованої на можливість, замість зв’язування двох plugins між собою.
</Warning>

## Пов’язані матеріали

- [Entry Points](/uk/plugins/sdk-entrypoints) — параметри `definePluginEntry` і `defineChannelPluginEntry`
- [Runtime Helpers](/uk/plugins/sdk-runtime) — повний довідник простору імен `api.runtime`
- [Setup and Config](/uk/plugins/sdk-setup) — пакування, маніфести, схеми конфігурації
- [Testing](/uk/plugins/sdk-testing) — тестові утиліти та правила lint
- [SDK Migration](/uk/plugins/sdk-migration) — міграція із застарілих поверхонь
- [Plugin Internals](/uk/plugins/architecture) — докладна архітектура і модель можливостей
