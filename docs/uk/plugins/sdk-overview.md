---
read_when:
    - Потрібно знати, з якого підшляху SDK імпортувати
    - Потрібен довідник для всіх методів реєстрації в OpenClawPluginApi
    - Ви шукаєте конкретний експорт SDK
sidebarTitle: SDK Overview
summary: Карта імпортів, довідник API реєстрації та архітектура SDK
title: Огляд Plugin SDK
x-i18n:
    generated_at: "2026-04-06T00:53:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: d801641f26f39dc21490d2a69a337ff1affb147141360916b8b58a267e9f822a
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Огляд Plugin SDK

Plugin SDK — це типізований контракт між plugins і core. Ця сторінка —
довідник про **що імпортувати** і **що можна зареєструвати**.

<Tip>
  **Шукаєте практичний посібник?**
  - Перший plugin? Почніть із [Getting Started](/uk/plugins/building-plugins)
  - Channel plugin? Дивіться [Channel Plugins](/uk/plugins/sdk-channel-plugins)
  - Provider plugin? Дивіться [Provider Plugins](/uk/plugins/sdk-provider-plugins)
</Tip>

## Угода щодо імпорту

Завжди імпортуйте з конкретного підшляху:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Кожен підшлях — це невеликий самодостатній модуль. Це пришвидшує запуск і
запобігає проблемам із циклічними залежностями. Для специфічних для channel
хелперів входу/збірки надавайте перевагу `openclaw/plugin-sdk/channel-core`; `openclaw/plugin-sdk/core`
залишайте для ширшої поверхні-парасольки та спільних хелперів, таких як
`buildChannelConfigSchema`.

Не додавайте й не використовуйте зручні шви з назвами provider, як-от
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`, або
брендовані для channel хелпер-шви. Вбудовані plugins мають компонувати загальні
підшляхи SDK у власних barrel-файлах `api.ts` або `runtime-api.ts`, а core
має або використовувати ці локальні для plugin barrel-файли, або додавати вузький загальний SDK
контракт, коли потреба справді є міжканальною.

Згенерована карта експортів усе ще містить невеликий набір швів-хелперів для вбудованих plugin,
таких як `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` і `plugin-sdk/matrix*`. Ці
підшляхи існують лише для підтримки та сумісності вбудованих plugins; вони
навмисно не включені до загальної таблиці нижче й не є рекомендованим
шляхом імпорту для нових сторонніх plugins.

## Довідник підшляхів

Найуживаніші підшляхи, згруповані за призначенням. Згенерований повний список із
понад 200 підшляхів знаходиться в `scripts/lib/plugin-sdk-entrypoints.json`.

Зарезервовані підшляхи-хелпери для вбудованих plugins усе ще з’являються в цьому згенерованому списку.
Ставтеся до них як до деталей реалізації/поверхонь сумісності, якщо тільки сторінка документації
не позначає якийсь із них явно як публічний.

### Вхід plugin

| Subpath                     | Ключові експорти                                                                                                                      |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Підшляхи channel">
    | Subpath | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Експорт кореневої Zod-схеми `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, а також `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Спільні хелпери майстра налаштування, запити списку дозволених, збирачі статусу налаштування |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Хелпери gate дій/конфігурації для багатьох облікових записів, хелпери резервного вибору стандартного облікового запису |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, хелпери нормалізації ID облікового запису |
    | `plugin-sdk/account-resolution` | Хелпери пошуку облікового запису + резервного вибору стандартного |
    | `plugin-sdk/account-helpers` | Вузькі хелпери списку облікових записів/дій над обліковими записами |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Типи схем конфігурації channel |
    | `plugin-sdk/telegram-command-config` | Хелпери нормалізації/валідації користувацьких команд Telegram із резервною підтримкою контракту вбудованого plugin |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Спільні хелпери побудови вхідних маршрутів і envelope |
    | `plugin-sdk/inbound-reply-dispatch` | Спільні хелпери запису та диспетчеризації вхідних даних |
    | `plugin-sdk/messaging-targets` | Хелпери розбору/зіставлення цілей |
    | `plugin-sdk/outbound-media` | Спільні хелпери завантаження вихідних медіа |
    | `plugin-sdk/outbound-runtime` | Хелпери делегатів вихідної ідентичності/надсилання |
    | `plugin-sdk/thread-bindings-runtime` | Хелпери життєвого циклу та адаптера прив’язок потоків |
    | `plugin-sdk/agent-media-payload` | Застарілий збирач media payload агента |
    | `plugin-sdk/conversation-runtime` | Хелпери прив’язки розмови/потоку, спарювання та налаштованих прив’язок |
    | `plugin-sdk/runtime-config-snapshot` | Хелпер знімка runtime-конфігурації |
    | `plugin-sdk/runtime-group-policy` | Хелпери визначення політики груп у runtime |
    | `plugin-sdk/channel-status` | Спільні хелпери знімка/зведення статусу channel |
    | `plugin-sdk/channel-config-primitives` | Вузькі примітиви schema конфігурації channel |
    | `plugin-sdk/channel-config-writes` | Хелпери авторизації запису конфігурації channel |
    | `plugin-sdk/channel-plugin-common` | Спільні prelude-експорти plugin для channel |
    | `plugin-sdk/allowlist-config-edit` | Хелпери редагування/читання конфігурації списку дозволених |
    | `plugin-sdk/group-access` | Спільні хелпери рішень доступу до груп |
    | `plugin-sdk/direct-dm` | Спільні хелпери auth/guard для прямих DM |
    | `plugin-sdk/interactive-runtime` | Хелпери нормалізації/скорочення interactive reply payload |
    | `plugin-sdk/channel-inbound` | Хелпери debounce, зіставлення згадок та envelope |
    | `plugin-sdk/channel-send-result` | Типи результатів reply |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Хелпери розбору/зіставлення цілей |
    | `plugin-sdk/channel-contract` | Типи контракту channel |
    | `plugin-sdk/channel-feedback` | Підключення feedback/reaction |
  </Accordion>

  <Accordion title="Підшляхи provider">
    | Subpath | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Кураторські хелпери налаштування локальних/self-hosted provider |
    | `plugin-sdk/self-hosted-provider-setup` | Сфокусовані хелпери налаштування self-hosted provider, сумісних з OpenAI |
    | `plugin-sdk/provider-auth-runtime` | Хелпери визначення API-ключа в runtime для provider plugins |
    | `plugin-sdk/provider-auth-api-key` | Хелпери онбордингу/запису профілю API-ключа |
    | `plugin-sdk/provider-auth-result` | Стандартний збирач результату OAuth auth |
    | `plugin-sdk/provider-auth-login` | Спільні інтерактивні хелпери входу для provider plugins |
    | `plugin-sdk/provider-env-vars` | Хелпери пошуку env vars для auth provider |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, спільні збирачі replay-policy, хелпери endpoint provider та хелпери нормалізації model-id, такі як `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Загальні хелпери HTTP/endpoint capability для provider |
    | `plugin-sdk/provider-web-fetch` | Хелпери реєстрації/кешу provider web-fetch |
    | `plugin-sdk/provider-web-search` | Хелпери реєстрації/кешу/конфігурації provider web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, очищення схем Gemini + діагностика, а також xAI compat-хелпери, такі як `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` та подібне |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, типи stream wrapper і спільні хелпери wrapper для Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Хелпери патчів конфігурації онбордингу |
    | `plugin-sdk/global-singleton` | Хелпери локального для процесу singleton/map/cache |
  </Accordion>

  <Accordion title="Підшляхи auth і безпеки">
    | Subpath | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, хелпери реєстру команд, хелпери авторизації відправника |
    | `plugin-sdk/approval-auth-runtime` | Хелпери визначення approver та auth дій у тому самому чаті |
    | `plugin-sdk/approval-client-runtime` | Хелпери профілю/фільтра native exec approval |
    | `plugin-sdk/approval-delivery-runtime` | Адаптери delivery/capability native approval |
    | `plugin-sdk/approval-native-runtime` | Хелпери native approval target + прив’язки облікового запису |
    | `plugin-sdk/approval-reply-runtime` | Хелпери approval reply payload для exec/plugin |
    | `plugin-sdk/command-auth-native` | Native auth команд + хелпери native session-target |
    | `plugin-sdk/command-detection` | Спільні хелпери виявлення команд |
    | `plugin-sdk/command-surface` | Хелпери нормалізації тіла команди та поверхні команд |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/security-runtime` | Спільні хелпери довіри, gate DM, зовнішнього контенту та збору секретів |
    | `plugin-sdk/ssrf-policy` | Хелпери host allowlist та політики SSRF для приватних мереж |
    | `plugin-sdk/ssrf-runtime` | Хелпери pinned-dispatcher, fetch із захистом SSRF та політики SSRF |
    | `plugin-sdk/secret-input` | Хелпери розбору секретного вводу |
    | `plugin-sdk/webhook-ingress` | Хелпери запиту/цілі webhook |
    | `plugin-sdk/webhook-request-guards` | Хелпери розміру body/timeout запиту |
  </Accordion>

  <Accordion title="Підшляхи runtime і сховища">
    | Subpath | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/runtime` | Широкі хелпери runtime/logging/backup/встановлення plugin |
    | `plugin-sdk/runtime-env` | Вузькі хелпери runtime env, logger, timeout, retry і backoff |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Спільні хелпери команд/hook/http/interactive для plugin |
    | `plugin-sdk/hook-runtime` | Спільні хелпери конвеєра webhook/internal hook |
    | `plugin-sdk/lazy-runtime` | Хелпери лінивого імпорту/прив’язки runtime, такі як `createLazyRuntimeModule`, `createLazyRuntimeMethod` і `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Хелпери виконання процесів |
    | `plugin-sdk/cli-runtime` | Хелпери форматування CLI, очікування та версії |
    | `plugin-sdk/gateway-runtime` | Хелпери клієнта gateway і патчів статусу channel |
    | `plugin-sdk/config-runtime` | Хелпери завантаження/запису конфігурації |
    | `plugin-sdk/telegram-command-config` | Нормалізація назви/опису команд Telegram і перевірки дублікатів/конфліктів, навіть коли поверхня контракту вбудованого Telegram недоступна |
    | `plugin-sdk/approval-runtime` | Хелпери approval для exec/plugin, збирачі approval-capability, хелпери auth/profile, native routing/runtime |
    | `plugin-sdk/reply-runtime` | Спільні runtime-хелпери для inbound/reply, chunking, dispatch, heartbeat, планувальник reply |
    | `plugin-sdk/reply-dispatch-runtime` | Вузькі хелпери dispatch/finalize для reply |
    | `plugin-sdk/reply-history` | Спільні хелпери коротковіконної історії reply, такі як `buildHistoryContext`, `recordPendingHistoryEntry` і `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Вузькі хелпери chunking тексту/markdown |
    | `plugin-sdk/session-store-runtime` | Хелпери шляху сховища сесій + updated-at |
    | `plugin-sdk/state-paths` | Хелпери шляхів директорій стану/OAuth |
    | `plugin-sdk/routing` | Хелпери маршруту/ключа сесії/прив’язки облікового запису, такі як `resolveAgentRoute`, `buildAgentSessionKey` і `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Спільні хелпери зведення статусу channel/облікового запису, значення runtime-state за замовчуванням і хелпери метаданих issue |
    | `plugin-sdk/target-resolver-runtime` | Спільні хелпери визначення цілей |
    | `plugin-sdk/string-normalization-runtime` | Хелпери нормалізації slug/рядків |
    | `plugin-sdk/request-url` | Витягування рядкових URL із fetch/request-подібних входів |
    | `plugin-sdk/run-command` | Запуск команд із таймером і нормалізованими результатами stdout/stderr |
    | `plugin-sdk/param-readers` | Поширені рідери параметрів tool/CLI |
    | `plugin-sdk/tool-send` | Витягування канонічних полів цілі надсилання з аргументів tool |
    | `plugin-sdk/temp-path` | Спільні хелпери шляхів тимчасового завантаження |
    | `plugin-sdk/logging-core` | Хелпери logger підсистеми та редагування чутливих даних |
    | `plugin-sdk/markdown-table-runtime` | Хелпери режиму таблиць Markdown |
    | `plugin-sdk/json-store` | Невеликі хелпери читання/запису стану JSON |
    | `plugin-sdk/file-lock` | Хелпери повторно вхідного file-lock |
    | `plugin-sdk/persistent-dedupe` | Хелпери кешу дедуплікації зберігання на диску |
    | `plugin-sdk/acp-runtime` | Хелпери runtime/session і reply-dispatch для ACP |
    | `plugin-sdk/agent-config-primitives` | Вузькі примітиви schema runtime-конфігурації агента |
    | `plugin-sdk/boolean-param` | Нестрогий рідер boolean-параметрів |
    | `plugin-sdk/dangerous-name-runtime` | Хелпери визначення збігів небезпечних назв |
    | `plugin-sdk/device-bootstrap` | Хелпери початкового налаштування пристрою та токенів pairing |
    | `plugin-sdk/extension-shared` | Спільні примітиви хелперів пасивного channel і статусу |
    | `plugin-sdk/models-provider-runtime` | Хелпери reply для команди `/models`/provider |
    | `plugin-sdk/skill-commands-runtime` | Хелпери списку команд Skills |
    | `plugin-sdk/native-command-registry` | Хелпери реєстру/build/serialize native command |
    | `plugin-sdk/provider-zai-endpoint` | Хелпери виявлення endpoint Z.AI |
    | `plugin-sdk/infra-runtime` | Хелпери системних подій/heartbeat |
    | `plugin-sdk/collection-runtime` | Невеликі хелпери обмеженого кешу |
    | `plugin-sdk/diagnostic-runtime` | Хелпери діагностичних прапорців і подій |
    | `plugin-sdk/error-runtime` | Хелпери графа помилок, форматування, спільної класифікації помилок, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Обгорнутий fetch, proxy та хелпери pinned lookup |
    | `plugin-sdk/host-runtime` | Хелпери нормалізації hostname і SCP-host |
    | `plugin-sdk/retry-runtime` | Хелпери конфігурації retry та запуску retry |
    | `plugin-sdk/agent-runtime` | Хелпери директорії/ідентичності/робочого простору агента |
    | `plugin-sdk/directory-runtime` | Запит/дедуплікація директорій на основі конфігурації |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Підшляхи capability і тестування">
    | Subpath | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Спільні хелпери отримання/перетворення/збереження медіа плюс збирачі media payload |
    | `plugin-sdk/media-understanding` | Типи provider для media understanding плюс орієнтовані на provider експорти хелперів зображень/аудіо |
    | `plugin-sdk/text-runtime` | Спільні хелпери тексту/markdown/logging, такі як видалення видимого для асистента тексту, хелпери render/chunking/table для markdown, хелпери редагування чутливих даних, хелпери тегів directive і утиліти безпечного тексту |
    | `plugin-sdk/text-chunking` | Хелпер chunking вихідного тексту |
    | `plugin-sdk/speech` | Типи provider мовлення плюс орієнтовані на provider хелпери directive, registry і validation |
    | `plugin-sdk/speech-core` | Спільні типи provider мовлення, registry, directive і хелпери нормалізації |
    | `plugin-sdk/realtime-transcription` | Типи provider транскрипції в реальному часі та хелпери registry |
    | `plugin-sdk/realtime-voice` | Типи provider голосу в реальному часі та хелпери registry |
    | `plugin-sdk/image-generation` | Типи provider генерації зображень |
    | `plugin-sdk/image-generation-core` | Спільні типи генерації зображень, failover, auth і хелпери registry |
    | `plugin-sdk/music-generation` | Типи provider/request/result для генерації музики |
    | `plugin-sdk/music-generation-core` | Спільні типи генерації музики, хелпери failover, пошуку provider і розбору model-ref |
    | `plugin-sdk/video-generation` | Типи provider/request/result для генерації відео |
    | `plugin-sdk/video-generation-core` | Спільні типи генерації відео, хелпери failover, пошуку provider і розбору model-ref |
    | `plugin-sdk/webhook-targets` | Реєстр цілей webhook і хелпери встановлення маршрутів |
    | `plugin-sdk/webhook-path` | Хелпери нормалізації шляху webhook |
    | `plugin-sdk/web-media` | Спільні хелпери завантаження віддалених/локальних медіа |
    | `plugin-sdk/zod` | Повторно експортований `zod` для споживачів plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Підшляхи memory">
    | Subpath | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/memory-core` | Поверхня хелперів bundled memory-core для manager/config/file/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Runtime-фасад індексу/пошуку memory |
    | `plugin-sdk/memory-core-host-engine-foundation` | Експорти foundation engine для memory host |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Експорти embedding engine для memory host |
    | `plugin-sdk/memory-core-host-engine-qmd` | Експорти QMD engine для memory host |
    | `plugin-sdk/memory-core-host-engine-storage` | Експорти storage engine для memory host |
    | `plugin-sdk/memory-core-host-multimodal` | Мультимодальні хелпери memory host |
    | `plugin-sdk/memory-core-host-query` | Хелпери query для memory host |
    | `plugin-sdk/memory-core-host-secret` | Хелпери secret для memory host |
    | `plugin-sdk/memory-core-host-status` | Хелпери статусу memory host |
    | `plugin-sdk/memory-core-host-runtime-cli` | Хелпери CLI runtime для memory host |
    | `plugin-sdk/memory-core-host-runtime-core` | Хелпери core runtime для memory host |
    | `plugin-sdk/memory-core-host-runtime-files` | Хелпери файлів/runtime для memory host |
    | `plugin-sdk/memory-lancedb` | Поверхня хелперів bundled memory-lancedb |
  </Accordion>

  <Accordion title="Зарезервовані підшляхи вбудованих хелперів">
    | Family | Поточні підшляхи | Призначене використання |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Хелпери підтримки bundled browser plugin (`browser-support` залишається barrel-файлом сумісності) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Поверхня хелперів/runtime для bundled Matrix |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Поверхня хелперів/runtime для bundled LINE |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Поверхня хелперів для bundled IRC |
    | Хелпери, специфічні для channel | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Шви сумісності/хелперів для вбудованих channel |
    | Хелпери, специфічні для auth/plugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Шви хелперів для вбудованих функцій/plugins; `plugin-sdk/github-copilot-token` наразі експортує `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` і `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API реєстрації

Зворотний виклик `register(api)` отримує об’єкт `OpenClawPluginApi` з такими
методами:

### Реєстрація capability

| Method                                           | Що реєструє                     |
| ------------------------------------------------ | ------------------------------- |
| `api.registerProvider(...)`                      | Текстовий inference (LLM)       |
| `api.registerChannel(...)`                       | Messaging channel               |
| `api.registerSpeechProvider(...)`                | Синтез text-to-speech / STT     |
| `api.registerRealtimeTranscriptionProvider(...)` | Потокова транскрипція в реальному часі |
| `api.registerRealtimeVoiceProvider(...)`         | Дуплексні голосові сесії в реальному часі |
| `api.registerMediaUnderstandingProvider(...)`    | Аналіз зображень/аудіо/відео    |
| `api.registerImageGenerationProvider(...)`       | Генерація зображень             |
| `api.registerMusicGenerationProvider(...)`       | Генерація музики                |
| `api.registerVideoGenerationProvider(...)`       | Генерація відео                 |
| `api.registerWebFetchProvider(...)`              | Provider web fetch / scrape     |
| `api.registerWebSearchProvider(...)`             | Web search                      |

### Tools і команди

| Method                          | Що реєструє                                  |
| ------------------------------- | -------------------------------------------- |
| `api.registerTool(tool, opts?)` | Tool агента (обов’язковий або `{ optional: true }`) |
| `api.registerCommand(def)`      | Користувацьку команду (оминає LLM)           |

### Інфраструктура

| Method                                         | Що реєструє          |
| ---------------------------------------------- | -------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook подій           |
| `api.registerHttpRoute(params)`                | HTTP endpoint gateway |
| `api.registerGatewayMethod(name, handler)`     | RPC-метод gateway    |
| `api.registerCli(registrar, opts?)`            | Підкоманду CLI       |
| `api.registerService(service)`                 | Фоновий сервіс       |
| `api.registerInteractiveHandler(registration)` | Interactive handler  |

Зарезервовані простори імен адміністрування core (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) завжди залишаються `operator.admin`, навіть якщо plugin намагається призначити
вужчу область gateway method. Для методів, що належать plugin,
використовуйте префікси, специфічні для plugin.

### Метадані реєстрації CLI

`api.registerCli(registrar, opts?)` приймає два види метаданих верхнього рівня:

- `commands`: явні корені команд, якими володіє registrar
- `descriptors`: дескриптори команд для етапу парсингу, які використовуються для довідки кореневого CLI,
  маршрутизації та лінивої реєстрації CLI plugin

Якщо ви хочете, щоб команда plugin залишалася ліниво завантажуваною у звичайному кореневому шляху CLI,
надайте `descriptors`, які охоплюють кожен корінь команди верхнього рівня, що експонує
цей registrar.

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
        description: "Керування обліковими записами Matrix, верифікацією, пристроями та станом профілю",
        hasSubcommands: true,
      },
    ],
  },
);
```

Використовуйте `commands` окремо лише тоді, коли вам не потрібна лінива реєстрація кореневого CLI.
Цей eager-шлях сумісності залишається підтримуваним, але він не встановлює
placeholders на основі descriptor для лінивого завантаження під час парсингу.

### Ексклюзивні слоти

| Method                                     | Що реєструє                          |
| ------------------------------------------ | ------------------------------------ |
| `api.registerContextEngine(id, factory)`   | Context engine (одночасно активний лише один) |
| `api.registerMemoryPromptSection(builder)` | Збирач секції prompt для memory      |
| `api.registerMemoryFlushPlan(resolver)`    | Resolver плану flush для memory      |
| `api.registerMemoryRuntime(runtime)`       | Адаптер runtime для memory           |

### Адаптери memory embedding

| Method                                         | Що реєструє                                     |
| ---------------------------------------------- | ----------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Адаптер memory embedding для активного plugin   |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan` і
  `registerMemoryRuntime` ексклюзивні для plugins memory.
- `registerMemoryEmbeddingProvider` дозволяє активному plugin memory зареєструвати один
  або кілька ID адаптерів embedding (наприклад, `openai`, `gemini` або користувацький
  ID, визначений plugin).
- Конфігурація користувача, така як `agents.defaults.memorySearch.provider` і
  `agents.defaults.memorySearch.fallback`, визначається відносно цих зареєстрованих
  ID адаптерів.

### Події та життєвий цикл

| Method                                       | Що робить                    |
| -------------------------------------------- | ---------------------------- |
| `api.on(hookName, handler, opts?)`           | Типізований hook життєвого циклу |
| `api.onConversationBindingResolved(handler)` | Зворотний виклик прив’язки розмови |

### Семантика рішень hook

- `before_tool_call`: повернення `{ block: true }` є термінальним. Щойно будь-який handler встановлює це значення, handlers із нижчим пріоритетом пропускаються.
- `before_tool_call`: повернення `{ block: false }` вважається відсутністю рішення (так само, як пропуск `block`), а не перевизначенням.
- `before_install`: повернення `{ block: true }` є термінальним. Щойно будь-який handler встановлює це значення, handlers із нижчим пріоритетом пропускаються.
- `before_install`: повернення `{ block: false }` вважається відсутністю рішення (так само, як пропуск `block`), а не перевизначенням.
- `reply_dispatch`: повернення `{ handled: true, ... }` є термінальним. Щойно будь-який handler бере dispatch на себе, handlers із нижчим пріоритетом і стандартний шлях dispatch моделі пропускаються.
- `message_sending`: повернення `{ cancel: true }` є термінальним. Щойно будь-який handler встановлює це значення, handlers із нижчим пріоритетом пропускаються.
- `message_sending`: повернення `{ cancel: false }` вважається відсутністю рішення (так само, як пропуск `cancel`), а не перевизначенням.

### Поля об’єкта API

| Field                    | Type                      | Опис                                                                                       |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------ |
| `api.id`                 | `string`                  | ID plugin                                                                                  |
| `api.name`               | `string`                  | Відображувана назва                                                                        |
| `api.version`            | `string?`                 | Версія plugin (необов’язково)                                                              |
| `api.description`        | `string?`                 | Опис plugin (необов’язково)                                                                |
| `api.source`             | `string`                  | Шлях до джерела plugin                                                                     |
| `api.rootDir`            | `string?`                 | Коренева директорія plugin (необов’язково)                                                 |
| `api.config`             | `OpenClawConfig`          | Поточний знімок конфігурації (активний знімок runtime у пам’яті, коли доступний)          |
| `api.pluginConfig`       | `Record<string, unknown>` | Конфігурація plugin із `plugins.entries.<id>.config`                                       |
| `api.runtime`            | `PluginRuntime`           | [Хелпери runtime](/uk/plugins/sdk-runtime)                                                    |
| `api.logger`             | `PluginLogger`            | Logger з областю видимості (`debug`, `info`, `warn`, `error`)                              |
| `api.registrationMode`   | `PluginRegistrationMode`  | Поточний режим завантаження; `"setup-runtime"` — це легке вікно запуску/налаштування до повного входу |
| `api.resolvePath(input)` | `(string) => string`      | Визначення шляху відносно кореня plugin                                                    |

## Угода щодо внутрішніх модулів

Усередині вашого plugin використовуйте локальні barrel-файли для внутрішніх імпортів:

```
my-plugin/
  api.ts            # Публічні експорти для зовнішніх споживачів
  runtime-api.ts    # Лише внутрішні runtime-експорти
  index.ts          # Точка входу plugin
  setup-entry.ts    # Легка точка входу лише для налаштування (необов’язково)
```

<Warning>
  Ніколи не імпортуйте власний plugin через `openclaw/plugin-sdk/<your-plugin>`
  з production-коду. Спрямовуйте внутрішні імпорти через `./api.ts` або
  `./runtime-api.ts`. Шлях SDK — це лише зовнішній контракт.
</Warning>

Публічні поверхні вбудованих plugins, завантажені через facade (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` та подібні публічні entry-файли), тепер надають перевагу
активному знімку runtime-конфігурації, коли OpenClaw уже запущено. Якщо знімок runtime
ще не існує, вони повертаються до визначеного файлу конфігурації на диску.

Provider plugins також можуть експонувати вузький локальний для plugin barrel-контракт, коли
хелпер навмисно є специфічним для provider і ще не належить до загального
підшляху SDK. Поточний вбудований приклад: provider Anthropic тримає свої Claude
stream-хелпери у власному публічному шві `api.ts` / `contract-api.ts`, замість того
щоб просувати логіку Anthropic beta-header і `service_tier` у загальний
контракт `plugin-sdk/*`.

Інші поточні вбудовані приклади:

- `@openclaw/openai-provider`: `api.ts` експортує збирачі provider,
  хелпери моделей за замовчуванням і збирачі provider для realtime
- `@openclaw/openrouter-provider`: `api.ts` експортує збирач provider плюс
  хелпери онбордингу/конфігурації

<Warning>
  Production-код extension також має уникати імпортів `openclaw/plugin-sdk/<other-plugin>`.
  Якщо хелпер справді спільний, винесіть його в нейтральний підшлях SDK,
  такий як `openclaw/plugin-sdk/speech`, `.../provider-model-shared` або іншу
  поверхню, орієнтовану на capability, замість зв’язування двох plugins між собою.
</Warning>

## Пов’язане

- [Entry Points](/uk/plugins/sdk-entrypoints) — параметри `definePluginEntry` і `defineChannelPluginEntry`
- [Runtime Helpers](/uk/plugins/sdk-runtime) — повний довідник простору імен `api.runtime`
- [Setup and Config](/uk/plugins/sdk-setup) — пакування, маніфести, схеми конфігурації
- [Testing](/uk/plugins/sdk-testing) — утиліти тестування та правила lint
- [SDK Migration](/uk/plugins/sdk-migration) — міграція із застарілих поверхонь
- [Plugin Internals](/uk/plugins/architecture) — поглиблена архітектура та модель capability
