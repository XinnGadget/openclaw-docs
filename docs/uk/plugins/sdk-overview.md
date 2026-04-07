---
read_when:
    - Вам потрібно знати, з якого підшляху SDK імпортувати
    - Вам потрібен довідник для всіх методів реєстрації в OpenClawPluginApi
    - Ви шукаєте конкретний експорт SDK
sidebarTitle: SDK Overview
summary: Карта імпортів, довідник API реєстрації та архітектура SDK
title: Огляд Plugin SDK
x-i18n:
    generated_at: "2026-04-07T06:42:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: be651251bc1d8fc6548cb9efd4b7940be093f7f7cdd70d94dc31d5a1ebde80f3
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Огляд Plugin SDK

Plugin SDK — це типізований контракт між plugin-ами та ядром. Ця сторінка —
довідник про **що імпортувати** і **що можна реєструвати**.

<Tip>
  **Шукаєте практичний посібник?**
  - Перший plugin? Почніть із [Getting Started](/uk/plugins/building-plugins)
  - Plugin каналу? Дивіться [Channel Plugins](/uk/plugins/sdk-channel-plugins)
  - Plugin провайдера? Дивіться [Provider Plugins](/uk/plugins/sdk-provider-plugins)
</Tip>

## Угода про імпорт

Завжди імпортуйте з конкретного підшляху:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Кожен підшлях — це невеликий самодостатній модуль. Це зберігає швидкий запуск і
запобігає проблемам із циклічними залежностями. Для допоміжних засобів
входу/збирання, специфічних для каналу, віддавайте перевагу
`openclaw/plugin-sdk/channel-core`; залишайте `openclaw/plugin-sdk/core` для
ширшої узагальненої поверхні та спільних допоміжних засобів, таких як
`buildChannelConfigSchema`.

Не додавайте й не використовуйте зручні проміжні поверхні, названі на честь
провайдерів, такі як `openclaw/plugin-sdk/slack`,
`openclaw/plugin-sdk/discord`, `openclaw/plugin-sdk/signal`,
`openclaw/plugin-sdk/whatsapp`, або допоміжні поверхні з брендингом каналів.
Вбудовані plugin-и мають компонувати загальні підшляхи SDK у власних barrel-файлах
`api.ts` або `runtime-api.ts`, а ядро має або використовувати ці локальні
barrel-файли plugin-а, або додавати вузький загальний контракт SDK, коли така
потреба справді є міжканальною.

Згенерована карта експортів усе ще містить невеликий набір допоміжних поверхонь
для вбудованих plugin-ів, таких як `plugin-sdk/feishu`,
`plugin-sdk/feishu-setup`, `plugin-sdk/zalo`, `plugin-sdk/zalo-setup` і
`plugin-sdk/matrix*`. Ці підшляхи існують лише для підтримки сумісності та
обслуговування вбудованих plugin-ів; їх навмисно не включено до загальної
таблиці нижче, і вони не є рекомендованим шляхом імпорту для нових сторонніх
plugin-ів.

## Довідник підшляхів

Найуживаніші підшляхи, згруповані за призначенням. Згенерований повний список із
понад 200 підшляхів міститься у `scripts/lib/plugin-sdk-entrypoints.json`.

Зарезервовані допоміжні підшляхи для вбудованих plugin-ів усе ще з’являються в
цьому згенерованому списку. Розглядайте їх як поверхні деталей реалізації /
сумісності, якщо якась сторінка документації явно не позначає одну з них як
публічну.

### Вхід plugin-а

| Підшлях                    | Ключові експорти                                                                                                                       |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Підшляхи каналів">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Експорт кореневої Zod-схеми `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, а також `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Спільні допоміжні засоби майстра налаштування, запити allowlist, побудовники стану налаштування |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Допоміжні засоби багатокористувацької конфігурації / шлюзу дій і резервного облікового запису за замовчуванням |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, допоміжні засоби нормалізації account-id |
    | `plugin-sdk/account-resolution` | Допоміжні засоби пошуку облікових записів + резервного вибору за замовчуванням |
    | `plugin-sdk/account-helpers` | Вузькі допоміжні засоби списку облікових записів / дій з обліковими записами |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Типи схеми конфігурації каналу |
    | `plugin-sdk/telegram-command-config` | Допоміжні засоби нормалізації/валідації користувацьких команд Telegram із резервним використанням контракту вбудованого plugin-а |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Спільні допоміжні засоби маршрутизації вхідних повідомлень + побудови envelope |
    | `plugin-sdk/inbound-reply-dispatch` | Спільні допоміжні засоби запису та диспетчеризації вхідних повідомлень |
    | `plugin-sdk/messaging-targets` | Допоміжні засоби розбору/зіставлення цілей |
    | `plugin-sdk/outbound-media` | Спільні допоміжні засоби завантаження вихідних медіа |
    | `plugin-sdk/outbound-runtime` | Допоміжні засоби вихідної ідентичності / делегата надсилання |
    | `plugin-sdk/thread-bindings-runtime` | Допоміжні засоби життєвого циклу та адаптера thread binding |
    | `plugin-sdk/agent-media-payload` | Застарілий побудовник agent media payload |
    | `plugin-sdk/conversation-runtime` | Допоміжні засоби прив’язки розмови/потоку, pairинг та configured-binding |
    | `plugin-sdk/runtime-config-snapshot` | Допоміжний засіб знімка конфігурації середовища виконання |
    | `plugin-sdk/runtime-group-policy` | Допоміжні засоби визначення group-policy у середовищі виконання |
    | `plugin-sdk/channel-status` | Спільні допоміжні засоби знімка/підсумку стану каналу |
    | `plugin-sdk/channel-config-primitives` | Вузькі примітиви schema конфігурації каналу |
    | `plugin-sdk/channel-config-writes` | Допоміжні засоби авторизації запису конфігурації каналу |
    | `plugin-sdk/channel-plugin-common` | Спільні prelude-експорти plugin-ів каналів |
    | `plugin-sdk/allowlist-config-edit` | Допоміжні засоби читання/редагування конфігурації allowlist |
    | `plugin-sdk/group-access` | Спільні допоміжні засоби рішень щодо доступу до груп |
    | `plugin-sdk/direct-dm` | Спільні допоміжні засоби авторизації/захисту прямих DM |
    | `plugin-sdk/interactive-runtime` | Допоміжні засоби нормалізації/скорочення payload інтерактивних відповідей |
    | `plugin-sdk/channel-inbound` | Допоміжні засоби debounce, зіставлення згадок, envelope |
    | `plugin-sdk/channel-send-result` | Типи результатів відповіді |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Допоміжні засоби розбору/зіставлення цілей |
    | `plugin-sdk/channel-contract` | Типи контракту каналу |
    | `plugin-sdk/channel-feedback` | Зв’язування feedback/reaction |
    | `plugin-sdk/channel-secret-runtime` | Вузькі допоміжні засоби secret-контракту, такі як `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment`, і типи secret target |
  </Accordion>

  <Accordion title="Підшляхи провайдерів">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Кураторські допоміжні засоби налаштування локальних / self-hosted провайдерів |
    | `plugin-sdk/self-hosted-provider-setup` | Сфокусовані допоміжні засоби налаштування self-hosted провайдерів, сумісних з OpenAI |
    | `plugin-sdk/cli-backend` | Стандартні значення бекенда CLI + константи watchdog |
    | `plugin-sdk/provider-auth-runtime` | Допоміжні засоби визначення API-ключа у середовищі виконання для plugin-ів провайдерів |
    | `plugin-sdk/provider-auth-api-key` | Допоміжні засоби onboarding/запису профілю API-ключа, такі як `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | Стандартний побудовник результату OAuth-автентифікації |
    | `plugin-sdk/provider-auth-login` | Спільні допоміжні засоби інтерактивного входу для plugin-ів провайдерів |
    | `plugin-sdk/provider-env-vars` | Допоміжні засоби пошуку змінних середовища для автентифікації провайдера |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, спільні побудовники replay-policy, допоміжні засоби endpoint провайдерів і нормалізації model-id, такі як `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Загальні допоміжні засоби HTTP/endpoint capability провайдерів |
    | `plugin-sdk/provider-web-fetch` | Допоміжні засоби реєстрації/кешування провайдерів web-fetch |
    | `plugin-sdk/provider-web-search-contract` | Вузькі допоміжні засоби контракту конфігурації/облікових даних web-search, такі як `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig`, і засоби встановлення/отримання облікових даних з обмеженою областю |
    | `plugin-sdk/provider-web-search` | Допоміжні засоби реєстрації/кешування/середовища виконання провайдерів web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, очищення схеми Gemini + діагностика, а також допоміжні засоби сумісності xAI, такі як `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` та подібні |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, типи stream wrapper і спільні допоміжні обгортки для Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Допоміжні засоби виправлення конфігурації під час onboarding |
    | `plugin-sdk/global-singleton` | Допоміжні засоби process-local singleton/map/cache |
  </Accordion>

  <Accordion title="Підшляхи автентифікації та безпеки">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, допоміжні засоби реєстру команд, допоміжні засоби авторизації відправника |
    | `plugin-sdk/approval-auth-runtime` | Допоміжні засоби визначення approver та авторизації дій у тому самому чаті |
    | `plugin-sdk/approval-client-runtime` | Допоміжні засоби native exec approval profile/filter |
    | `plugin-sdk/approval-delivery-runtime` | Адаптери native approval capability/delivery |
    | `plugin-sdk/approval-native-runtime` | Допоміжні засоби native approval target + account-binding |
    | `plugin-sdk/approval-reply-runtime` | Допоміжні засоби payload відповідей для схвалення exec/plugin |
    | `plugin-sdk/command-auth-native` | Допоміжні засоби native command auth + native session-target |
    | `plugin-sdk/command-detection` | Спільні допоміжні засоби виявлення команд |
    | `plugin-sdk/command-surface` | Нормалізація тіла команди та допоміжні засоби command-surface |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Вузькі допоміжні засоби збирання secret-контрактів для поверхонь секретів channel/plugin |
    | `plugin-sdk/secret-ref-runtime` | Вузькі допоміжні засоби `coerceSecretRef` і типізації SecretRef для розбору secret-контрактів/конфігурації |
    | `plugin-sdk/security-runtime` | Спільні допоміжні засоби довіри, шлюзу DM, зовнішнього вмісту та збирання секретів |
    | `plugin-sdk/ssrf-policy` | Допоміжні засоби policy SSRF для allowlist хостів і приватних мереж |
    | `plugin-sdk/ssrf-runtime` | Допоміжні засоби pinned-dispatcher, SSRF-захищеного fetch та policy SSRF |
    | `plugin-sdk/secret-input` | Допоміжні засоби розбору secret input |
    | `plugin-sdk/webhook-ingress` | Допоміжні засоби запитів/цілей webhook |
    | `plugin-sdk/webhook-request-guards` | Допоміжні засоби обмеження розміру тіла запиту / тайм-ауту |
  </Accordion>

  <Accordion title="Підшляхи середовища виконання та сховища">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/runtime` | Широкі допоміжні засоби середовища виконання / логування / резервного копіювання / встановлення plugin-ів |
    | `plugin-sdk/runtime-env` | Вузькі допоміжні засоби env середовища виконання, logger, timeout, retry та backoff |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Спільні допоміжні засоби plugin command/hook/http/interactive |
    | `plugin-sdk/hook-runtime` | Спільні допоміжні засоби конвеєра webhook/internal hook |
    | `plugin-sdk/lazy-runtime` | Допоміжні засоби лінивого імпорту/прив’язки середовища виконання, такі як `createLazyRuntimeModule`, `createLazyRuntimeMethod` і `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Допоміжні засоби виконання процесів |
    | `plugin-sdk/cli-runtime` | Допоміжні засоби форматування CLI, очікування та версій |
    | `plugin-sdk/gateway-runtime` | Допоміжні засоби клієнта gateway і виправлення стану каналу |
    | `plugin-sdk/config-runtime` | Допоміжні засоби завантаження/запису конфігурації |
    | `plugin-sdk/telegram-command-config` | Нормалізація імен/описів команд Telegram та перевірки дублікатів/конфліктів, навіть коли поверхня контракту вбудованого Telegram недоступна |
    | `plugin-sdk/approval-runtime` | Допоміжні засоби схвалення exec/plugin, побудовники approval-capability, допоміжні засоби auth/profile, native routing/runtime |
    | `plugin-sdk/reply-runtime` | Спільні допоміжні засоби середовища виконання для inbound/reply, chunking, dispatch, heartbeat, planner відповідей |
    | `plugin-sdk/reply-dispatch-runtime` | Вузькі допоміжні засоби dispatch/finalize відповідей |
    | `plugin-sdk/reply-history` | Спільні допоміжні засоби short-window reply-history, такі як `buildHistoryContext`, `recordPendingHistoryEntry` і `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Вузькі допоміжні засоби chunking тексту/markdown |
    | `plugin-sdk/session-store-runtime` | Допоміжні засоби шляху session store + updated-at |
    | `plugin-sdk/state-paths` | Допоміжні засоби шляхів до каталогів state/OAuth |
    | `plugin-sdk/routing` | Допоміжні засоби route/session-key/account binding, такі як `resolveAgentRoute`, `buildAgentSessionKey` і `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Спільні допоміжні засоби підсумків стану каналу/облікового запису, стандартів runtime-state та метаданих issue |
    | `plugin-sdk/target-resolver-runtime` | Спільні допоміжні засоби target resolver |
    | `plugin-sdk/string-normalization-runtime` | Допоміжні засоби нормалізації slug/рядків |
    | `plugin-sdk/request-url` | Витягування рядкових URL із fetch/request-подібних входів |
    | `plugin-sdk/run-command` | Запуск команди з тайм-аутом і нормалізованими результатами stdout/stderr |
    | `plugin-sdk/param-readers` | Загальні читачі параметрів tool/CLI |
    | `plugin-sdk/tool-send` | Витягування канонічних полів цілі надсилання з аргументів tool |
    | `plugin-sdk/temp-path` | Спільні допоміжні засоби шляхів для тимчасових завантажень |
    | `plugin-sdk/logging-core` | Допоміжні засоби subsystem logger та редагування конфіденційних даних |
    | `plugin-sdk/markdown-table-runtime` | Допоміжні засоби режиму markdown-таблиць |
    | `plugin-sdk/json-store` | Невеликі допоміжні засоби читання/запису JSON state |
    | `plugin-sdk/file-lock` | Допоміжні засоби повторного входу file-lock |
    | `plugin-sdk/persistent-dedupe` | Допоміжні засоби дискового dedupe cache |
    | `plugin-sdk/acp-runtime` | Допоміжні засоби ACP runtime/session і reply-dispatch |
    | `plugin-sdk/agent-config-primitives` | Вузькі примітиви schema конфігурації середовища виконання agent |
    | `plugin-sdk/boolean-param` | Читач нестрогих булевих параметрів |
    | `plugin-sdk/dangerous-name-runtime` | Допоміжні засоби визначення збігів небезпечних назв |
    | `plugin-sdk/device-bootstrap` | Допоміжні засоби початкового налаштування пристрою та токенів pairинг |
    | `plugin-sdk/extension-shared` | Спільні примітиви для passive-channel, status та ambient proxy helper |
    | `plugin-sdk/models-provider-runtime` | Допоміжні засоби відповіді команди `/models` / провайдера |
    | `plugin-sdk/skill-commands-runtime` | Допоміжні засоби виведення списку команд Skills |
    | `plugin-sdk/native-command-registry` | Допоміжні засоби реєстру/build/serialize native command |
    | `plugin-sdk/provider-zai-endpoint` | Допоміжні засоби виявлення endpoint Z.AI |
    | `plugin-sdk/infra-runtime` | Допоміжні засоби системних подій / heartbeat |
    | `plugin-sdk/collection-runtime` | Невеликі допоміжні засоби обмеженого кешу |
    | `plugin-sdk/diagnostic-runtime` | Допоміжні засоби діагностичних прапорців і подій |
    | `plugin-sdk/error-runtime` | Граф помилок, форматування, спільні допоміжні засоби класифікації помилок, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Обгорнуті допоміжні засоби fetch, proxy і pinned lookup |
    | `plugin-sdk/host-runtime` | Допоміжні засоби нормалізації hostname і SCP host |
    | `plugin-sdk/retry-runtime` | Допоміжні засоби конфігурації retry та запуску retry |
    | `plugin-sdk/agent-runtime` | Допоміжні засоби каталогу / ідентичності / workspace agent-а |
    | `plugin-sdk/directory-runtime` | Запит/усунення дублікатів каталогу на основі конфігурації |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Підшляхи можливостей і тестування">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Спільні допоміжні засоби fetch/transform/store медіа, а також побудовники media payload |
    | `plugin-sdk/media-generation-runtime` | Спільні допоміжні засоби failover для генерації медіа, вибір кандидатів і повідомлення про відсутню модель |
    | `plugin-sdk/media-understanding` | Типи провайдерів media understanding, а також допоміжні експорти для зображень/аудіо, орієнтовані на провайдерів |
    | `plugin-sdk/text-runtime` | Спільні допоміжні засоби text/markdown/logging, такі як видалення видимого для асистента тексту, render/chunking/table для markdown, редагування конфіденційних даних, допоміжні засоби directive-tag і safe-text utilities |
    | `plugin-sdk/text-chunking` | Допоміжний засіб chunking вихідного тексту |
    | `plugin-sdk/speech` | Типи провайдерів мовлення, а також допоміжні засоби директив, реєстру та валідації, орієнтовані на провайдерів |
    | `plugin-sdk/speech-core` | Спільні типи провайдерів мовлення, допоміжні засоби реєстру, директив і нормалізації |
    | `plugin-sdk/realtime-transcription` | Типи провайдерів realtime transcription і допоміжні засоби реєстру |
    | `plugin-sdk/realtime-voice` | Типи провайдерів realtime voice і допоміжні засоби реєстру |
    | `plugin-sdk/image-generation` | Типи провайдерів генерації зображень |
    | `plugin-sdk/image-generation-core` | Спільні типи генерації зображень, допоміжні засоби failover, auth і реєстру |
    | `plugin-sdk/music-generation` | Типи провайдерів / запитів / результатів генерації музики |
    | `plugin-sdk/music-generation-core` | Спільні типи генерації музики, допоміжні засоби failover, пошуку провайдера та розбору model-ref |
    | `plugin-sdk/video-generation` | Типи провайдерів / запитів / результатів генерації відео |
    | `plugin-sdk/video-generation-core` | Спільні типи генерації відео, допоміжні засоби failover, пошуку провайдера та розбору model-ref |
    | `plugin-sdk/webhook-targets` | Допоміжні засоби реєстру webhook target і встановлення маршрутів |
    | `plugin-sdk/webhook-path` | Допоміжні засоби нормалізації webhook path |
    | `plugin-sdk/web-media` | Спільні допоміжні засоби завантаження віддалених/локальних медіа |
    | `plugin-sdk/zod` | Повторно експортований `zod` для користувачів plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Підшляхи пам’яті">
    | Підшлях | Ключові експорти |
    | --- | --- |
    | `plugin-sdk/memory-core` | Поверхня допоміжних засобів вбудованого memory-core для manager/config/file/CLI helpers |
    | `plugin-sdk/memory-core-engine-runtime` | Фасад середовища виконання для memory index/search |
    | `plugin-sdk/memory-core-host-engine-foundation` | Експорти foundation engine хоста пам’яті |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Експорти embedding engine хоста пам’яті |
    | `plugin-sdk/memory-core-host-engine-qmd` | Експорти QMD engine хоста пам’яті |
    | `plugin-sdk/memory-core-host-engine-storage` | Експорти storage engine хоста пам’яті |
    | `plugin-sdk/memory-core-host-multimodal` | Допоміжні засоби multimodal хоста пам’яті |
    | `plugin-sdk/memory-core-host-query` | Допоміжні засоби query хоста пам’яті |
    | `plugin-sdk/memory-core-host-secret` | Допоміжні засоби secret хоста пам’яті |
    | `plugin-sdk/memory-core-host-events` | Допоміжні засоби журналу подій хоста пам’яті |
    | `plugin-sdk/memory-core-host-status` | Допоміжні засоби стану хоста пам’яті |
    | `plugin-sdk/memory-core-host-runtime-cli` | Допоміжні засоби CLI runtime хоста пам’яті |
    | `plugin-sdk/memory-core-host-runtime-core` | Допоміжні засоби core runtime хоста пам’яті |
    | `plugin-sdk/memory-core-host-runtime-files` | Допоміжні засоби файлів/runtime хоста пам’яті |
    | `plugin-sdk/memory-host-core` | Вендорно-нейтральний псевдонім для допоміжних засобів core runtime хоста пам’яті |
    | `plugin-sdk/memory-host-events` | Вендорно-нейтральний псевдонім для допоміжних засобів журналу подій хоста пам’яті |
    | `plugin-sdk/memory-host-files` | Вендорно-нейтральний псевдонім для допоміжних засобів файлів/runtime хоста пам’яті |
    | `plugin-sdk/memory-host-markdown` | Спільні допоміжні засоби managed-markdown для plugin-ів, пов’язаних із пам’яттю |
    | `plugin-sdk/memory-host-search` | Активний фасад runtime пам’яті для доступу до search-manager |
    | `plugin-sdk/memory-host-status` | Вендорно-нейтральний псевдонім для допоміжних засобів стану хоста пам’яті |
    | `plugin-sdk/memory-lancedb` | Поверхня допоміжних засобів вбудованого memory-lancedb |
  </Accordion>

  <Accordion title="Зарезервовані підшляхи допоміжних засобів вбудованих plugin-ів">
    | Родина | Поточні підшляхи | Призначення |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Допоміжні засоби підтримки вбудованого browser plugin-а (`browser-support` залишається barrel-ом сумісності) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Поверхня допоміжних засобів/runtime вбудованого Matrix |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Поверхня допоміжних засобів/runtime вбудованого LINE |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Поверхня допоміжних засобів вбудованого IRC |
    | Допоміжні засоби для конкретних каналів | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Поверхні сумісності/допоміжних засобів вбудованих каналів |
    | Допоміжні засоби автентифікації / специфічні для plugin-ів | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Поверхні допоміжних засобів вбудованих функцій/plugin-ів; `plugin-sdk/github-copilot-token` наразі експортує `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` і `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API реєстрації

Зворотний виклик `register(api)` отримує об’єкт `OpenClawPluginApi` з такими
методами:

### Реєстрація можливостей

| Метод                                           | Що він реєструє                 |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | Текстовий inference (LLM)        |
| `api.registerCliBackend(...)`                    | Локальний CLI-бекенд inference   |
| `api.registerChannel(...)`                       | Канал обміну повідомленнями      |
| `api.registerSpeechProvider(...)`                | Синтез text-to-speech / STT      |
| `api.registerRealtimeTranscriptionProvider(...)` | Потокова realtime-транскрипція   |
| `api.registerRealtimeVoiceProvider(...)`         | Дуплексні сеанси realtime voice  |
| `api.registerMediaUnderstandingProvider(...)`    | Аналіз зображень/аудіо/відео     |
| `api.registerImageGenerationProvider(...)`       | Генерація зображень              |
| `api.registerMusicGenerationProvider(...)`       | Генерація музики                 |
| `api.registerVideoGenerationProvider(...)`       | Генерація відео                  |
| `api.registerWebFetchProvider(...)`              | Провайдер web fetch / scrape     |
| `api.registerWebSearchProvider(...)`             | Web search                       |

### Інструменти та команди

| Метод                          | Що він реєструє                              |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | Agent tool (обов’язковий або `{ optional: true }`) |
| `api.registerCommand(def)`      | Користувацька команда (обходить LLM)          |

### Інфраструктура

| Метод                                         | Що він реєструє                       |
| ---------------------------------------------- | --------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Event hook                              |
| `api.registerHttpRoute(params)`                | HTTP endpoint gateway                   |
| `api.registerGatewayMethod(name, handler)`     | RPC-метод gateway                       |
| `api.registerCli(registrar, opts?)`            | Підкоманда CLI                          |
| `api.registerService(service)`                 | Фонова служба                           |
| `api.registerInteractiveHandler(registration)` | Інтерактивний обробник                  |
| `api.registerMemoryPromptSupplement(builder)`  | Адитивний розділ prompt-а, суміжний із пам’яттю |
| `api.registerMemoryCorpusSupplement(adapter)`  | Адитивний корпус для memory search/read |

Зарезервовані простори імен адміністрування ядра (`config.*`, `exec.approvals.*`,
`wizard.*`, `update.*`) завжди залишаються `operator.admin`, навіть якщо plugin
намагається призначити вужчу область gateway method. Для методів, що належать
plugin-у, віддавайте перевагу префіксам, специфічним для plugin-а.

### Метадані реєстрації CLI

`api.registerCli(registrar, opts?)` приймає два види метаданих верхнього рівня:

- `commands`: явні корені команд, що належать registrar
- `descriptors`: дескриптори команд на етапі розбору, які використовуються для кореневої довідки CLI,
  маршрутизації та лінивої реєстрації CLI plugin-а

Якщо ви хочете, щоб команда plugin-а залишалася ліниво завантажуваною у
звичайному кореневому шляху CLI, надайте `descriptors`, які охоплюють кожен
корінь команди верхнього рівня, що експонується цим registrar.

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
        description: "Manage Matrix accounts, verification, devices, and profile state",
        hasSubcommands: true,
      },
    ],
  },
);
```

Використовуйте лише `commands`, коли вам не потрібна лінива реєстрація
кореневого CLI. Цей eager-шлях сумісності й далі підтримується, але він не
встановлює резервні placeholder-и на основі дескрипторів для лінивого
завантаження під час розбору.

### Реєстрація CLI-бекенда

`api.registerCliBackend(...)` дозволяє plugin-у володіти стандартною
конфігурацією локального AI CLI-бекенда, такого як `codex-cli`.

- `id` бекенда стає префіксом провайдера в model ref на кшталт `codex-cli/gpt-5`.
- `config` бекенда використовує ту саму форму, що й `agents.defaults.cliBackends.<id>`.
- Конфігурація користувача все одно має пріоритет. OpenClaw об’єднує `agents.defaults.cliBackends.<id>` поверх
  стандартного значення plugin-а перед запуском CLI.
- Використовуйте `normalizeConfig`, коли бекенду потрібні переписування для сумісності після об’єднання
  (наприклад, нормалізація старих форм прапорців).

### Ексклюзивні слоти

| Метод                                     | Що він реєструє                      |
| ------------------------------------------ | ------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Контекстний рушій (лише один активний одночасно) |
| `api.registerMemoryPromptSection(builder)` | Побудовник розділу memory prompt      |
| `api.registerMemoryFlushPlan(resolver)`    | Резолвер плану очищення пам’яті       |
| `api.registerMemoryRuntime(runtime)`       | Адаптер runtime пам’яті               |

### Адаптери вбудовування пам’яті

| Метод                                         | Що він реєструє                               |
| ---------------------------------------------- | ---------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Адаптер memory embedding для активного plugin-а |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan` і
  `registerMemoryRuntime` є ексклюзивними для plugin-ів пам’яті.
- `registerMemoryEmbeddingProvider` дозволяє активному plugin-у пам’яті
  реєструвати один або кілька id адаптерів embedding (наприклад, `openai`,
  `gemini` або власний id, визначений plugin-ом).
- Користувацька конфігурація, така як `agents.defaults.memorySearch.provider` і
  `agents.defaults.memorySearch.fallback`, визначається відносно зареєстрованих
  id цих адаптерів.

### Події та життєвий цикл

| Метод                                       | Що він робить               |
| -------------------------------------------- | ----------------------------- |
| `api.on(hookName, handler, opts?)`           | Типізований lifecycle hook    |
| `api.onConversationBindingResolved(handler)` | Зворотний виклик прив’язки розмови |

### Семантика рішень hook-ів

- `before_tool_call`: повернення `{ block: true }` є термінальним. Щойно будь-який обробник встановлює це значення, обробники з нижчим пріоритетом пропускаються.
- `before_tool_call`: повернення `{ block: false }` вважається відсутністю рішення (так само, як і пропуск `block`), а не перевизначенням.
- `before_install`: повернення `{ block: true }` є термінальним. Щойно будь-який обробник встановлює це значення, обробники з нижчим пріоритетом пропускаються.
- `before_install`: повернення `{ block: false }` вважається відсутністю рішення (так само, як і пропуск `block`), а не перевизначенням.
- `reply_dispatch`: повернення `{ handled: true, ... }` є термінальним. Щойно будь-який обробник заявляє про dispatch, обробники з нижчим пріоритетом і стандартний шлях dispatch моделі пропускаються.
- `message_sending`: повернення `{ cancel: true }` є термінальним. Щойно будь-який обробник встановлює це значення, обробники з нижчим пріоритетом пропускаються.
- `message_sending`: повернення `{ cancel: false }` вважається відсутністю рішення (так само, як і пропуск `cancel`), а не перевизначенням.

### Поля об’єкта API

| Поле                    | Тип                       | Опис                                                                                         |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | id plugin-а                                                                                  |
| `api.name`               | `string`                  | Відображувана назва                                                                          |
| `api.version`            | `string?`                 | Версія plugin-а (необов’язково)                                                              |
| `api.description`        | `string?`                 | Опис plugin-а (необов’язково)                                                                |
| `api.source`             | `string`                  | Шлях до джерела plugin-а                                                                     |
| `api.rootDir`            | `string?`                 | Кореневий каталог plugin-а (необов’язково)                                                   |
| `api.config`             | `OpenClawConfig`          | Поточний знімок конфігурації (активний знімок у пам’яті середовища виконання, якщо доступний) |
| `api.pluginConfig`       | `Record<string, unknown>` | Конфігурація plugin-а з `plugins.entries.<id>.config`                                        |
| `api.runtime`            | `PluginRuntime`           | [Допоміжні засоби runtime](/uk/plugins/sdk-runtime)                                             |
| `api.logger`             | `PluginLogger`            | Logger з областю видимості (`debug`, `info`, `warn`, `error`)                                |
| `api.registrationMode`   | `PluginRegistrationMode`  | Поточний режим завантаження; `"setup-runtime"` — це легковагоме вікно запуску/налаштування до повного входу |
| `api.resolvePath(input)` | `(string) => string`      | Визначення шляху відносно кореня plugin-а                                                    |

## Угода про внутрішні модулі

Усередині вашого plugin-а використовуйте локальні barrel-файли для внутрішніх
імпортів:

```
my-plugin/
  api.ts            # Публічні експорти для зовнішніх користувачів
  runtime-api.ts    # Внутрішні експорти runtime
  index.ts          # Точка входу plugin-а
  setup-entry.ts    # Легка точка входу лише для налаштування (необов’язково)
```

<Warning>
  Ніколи не імпортуйте власний plugin через `openclaw/plugin-sdk/<your-plugin>`
  у production code. Спрямовуйте внутрішні імпорти через `./api.ts` або
  `./runtime-api.ts`. Шлях SDK — це лише зовнішній контракт.
</Warning>

Публічні поверхні вбудованих plugin-ів, завантажувані через facade (`api.ts`,
`runtime-api.ts`, `index.ts`, `setup-entry.ts` та подібні публічні файли
входу), тепер віддають перевагу активному знімку конфігурації runtime, коли
OpenClaw уже працює. Якщо знімок runtime ще не існує, вони повертаються до
визначеного файла конфігурації на диску.

Plugin-и провайдерів також можуть експонувати вузький локальний barrel-контракт
plugin-а, коли допоміжний засіб навмисно є специфічним для провайдера і ще не
належить до загального підшляху SDK. Поточний вбудований приклад: провайдер
Anthropic зберігає свої допоміжні засоби потоку Claude у власній публічній
поверхні `api.ts` / `contract-api.ts` замість просування логіки бета-заголовків
Anthropic і `service_tier` у загальний контракт `plugin-sdk/*`.

Інші поточні вбудовані приклади:

- `@openclaw/openai-provider`: `api.ts` експортує побудовники провайдерів,
  допоміжні засоби моделей за замовчуванням і побудовники realtime-провайдерів
- `@openclaw/openrouter-provider`: `api.ts` експортує побудовник провайдера, а також
  допоміжні засоби onboarding/конфігурації

<Warning>
  Production code розширень також має уникати імпортів
  `openclaw/plugin-sdk/<other-plugin>`. Якщо допоміжний засіб справді є спільним,
  перенесіть його до нейтрального підшляху SDK, такого як
  `openclaw/plugin-sdk/speech`, `.../provider-model-shared` або іншої
  поверхні, орієнтованої на можливість, замість зв’язування двох plugin-ів між собою.
</Warning>

## Пов’язане

- [Entry Points](/uk/plugins/sdk-entrypoints) — параметри `definePluginEntry` і `defineChannelPluginEntry`
- [Runtime Helpers](/uk/plugins/sdk-runtime) — повний довідник простору імен `api.runtime`
- [Setup and Config](/uk/plugins/sdk-setup) — пакування, маніфести, схеми конфігурації
- [Testing](/uk/plugins/sdk-testing) — утиліти тестування та правила lint
- [SDK Migration](/uk/plugins/sdk-migration) — міграція зі застарілих поверхонь
- [Plugin Internals](/uk/plugins/architecture) — детальна архітектура та модель можливостей
