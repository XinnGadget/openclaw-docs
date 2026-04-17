---
read_when:
    - Ви створюєте новий Plugin каналу обміну повідомленнями
    - Ви хочете підключити OpenClaw до платформи обміну повідомленнями
    - Вам потрібно зрозуміти поверхню адаптера ChannelPlugin
sidebarTitle: Channel Plugins
summary: Покроковий посібник зі створення Plugin каналу обміну повідомленнями для OpenClaw
title: Створення Plugin каналів
x-i18n:
    generated_at: "2026-04-15T16:36:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 80e47e61d1e47738361692522b79aff276544446c58a7b41afe5296635dfad4b
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# Створення Plugin каналів

Цей посібник описує створення Plugin каналу, який підключає OpenClaw до
платформи обміну повідомленнями. Наприкінці у вас буде робочий канал із
безпекою DM, сполученням, потоками відповідей і вихідними повідомленнями.

<Info>
  Якщо ви ще не створювали жодного Plugin для OpenClaw, спочатку прочитайте
  [Початок роботи](/uk/plugins/building-plugins) про базову структуру пакета та
  налаштування маніфесту.
</Info>

## Як працюють Plugin каналів

Plugin каналів не потребують власних інструментів send/edit/react. OpenClaw
зберігає один спільний інструмент `message` у ядрі. Ваш Plugin відповідає за:

- **Конфігурацію** — визначення облікового запису та майстер налаштування
- **Безпеку** — політику DM і списки дозволених
- **Сполучення** — потік підтвердження DM
- **Граматику сесії** — як специфічні для провайдера ідентифікатори розмов зіставляються з базовими чатами, ідентифікаторами потоків і резервними батьківськими значеннями
- **Вихідні повідомлення** — надсилання тексту, медіа та опитувань на платформу
- **Потоки** — як організовуються відповіді у потоки

Ядро відповідає за спільний інструмент повідомлень, підключення prompt, зовнішню форму ключа сесії, загальний облік `:thread:` і диспетчеризацію.

Якщо ваш канал додає параметри інструмента повідомлень, які містять джерела медіа, експонуйте ці
назви параметрів через `describeMessageTool(...).mediaSourceParams`. Ядро використовує
цей явний список для нормалізації шляху sandbox і політики доступу до вихідних медіа,
тому Plugin не потребують винятків у спільному ядрі для специфічних для провайдера
параметрів аватарів, вкладень або обкладинок.
Надавайте перевагу поверненню мапи з ключами дій, наприклад
`{ "set-profile": ["avatarUrl", "avatarPath"] }`, щоб несуміжні дії не
успадковували медіа-аргументи іншої дії. Плоский масив також працює для параметрів, які
навмисно спільні для кожної експонованої дії.

Якщо ваша платформа зберігає додаткову область у межах ідентифікаторів розмов, залишайте цей парсинг
у Plugin за допомогою `messaging.resolveSessionConversation(...)`. Це
канонічний хук для зіставлення `rawId` з базовим ідентифікатором розмови, необов’язковим
ідентифікатором потоку, явним `baseConversationId` і будь-якими
`parentConversationCandidates`.
Коли ви повертаєте `parentConversationCandidates`, зберігайте їх упорядкованими від
найвужчого батьківського елемента до найширшої/базової розмови.

Bundled Plugin, яким потрібен той самий парсинг до запуску реєстру каналів,
також можуть експонувати файл верхнього рівня `session-key-api.ts` із відповідним
експортом `resolveSessionConversation(...)`. Ядро використовує цю безпечну для bootstrap поверхню
лише тоді, коли реєстр Plugin під час виконання ще недоступний.

`messaging.resolveParentConversationCandidates(...)` залишається доступним як
застарілий резервний механізм сумісності, коли Plugin потрібні лише
резервні батьківські значення поверх загального/raw id. Якщо обидва хуки існують, ядро використовує
спочатку `resolveSessionConversation(...).parentConversationCandidates` і лише
потім повертається до `resolveParentConversationCandidates(...)`, якщо канонічний хук
їх не вказує.

## Підтвердження та можливості каналу

Більшості Plugin каналів не потрібен код, специфічний для підтверджень.

- Ядро відповідає за `/approve` у тому самому чаті, спільні payload кнопок підтвердження та загальну резервну доставку.
- Надавайте перевагу одному об’єкту `approvalCapability` у Plugin каналу, коли каналу потрібна поведінка, специфічна для підтверджень.
- `ChannelPlugin.approvals` видалено. Розміщуйте факти доставки/native/render/auth для підтверджень у `approvalCapability`.
- `plugin.auth` призначений лише для входу/виходу; ядро більше не читає з цього об’єкта auth-хуки підтверджень.
- `approvalCapability.authorizeActorAction` і `approvalCapability.getActionAvailabilityState` — це канонічний шов auth підтверджень.
- Використовуйте `approvalCapability.getActionAvailabilityState` для доступності auth підтверджень у тому самому чаті.
- Якщо ваш канал експонує native exec-підтвердження, використовуйте `approvalCapability.getExecInitiatingSurfaceState` для стану initiating-surface/native-client, коли він відрізняється від auth підтверджень у тому самому чаті. Ядро використовує цей специфічний для exec хук, щоб розрізняти `enabled` і `disabled`, вирішувати, чи підтримує ініціюючий канал native exec-підтвердження, і включати канал до резервних вказівок для native-client. `createApproverRestrictedNativeApprovalCapability(...)` заповнює це для типового випадку.
- Використовуйте `outbound.shouldSuppressLocalPayloadPrompt` або `outbound.beforeDeliverPayload` для специфічної для каналу поведінки життєвого циклу payload, як-от приховування дубльованих локальних prompt підтвердження або надсилання індикаторів набору тексту перед доставкою.
- Використовуйте `approvalCapability.delivery` лише для маршрутизації native-підтверджень або пригнічення резервної доставки.
- Використовуйте `approvalCapability.nativeRuntime` для фактів native-підтверджень, якими володіє канал. Залишайте його лінивим на гарячих entrypoint каналу за допомогою `createLazyChannelApprovalNativeRuntimeAdapter(...)`, який може імпортувати ваш runtime-модуль за потреби, водночас даючи ядру змогу зібрати життєвий цикл підтвердження.
- Використовуйте `approvalCapability.render` лише тоді, коли каналу справді потрібні власні payload підтвердження замість спільного renderer.
- Використовуйте `approvalCapability.describeExecApprovalSetup`, коли канал хоче, щоб відповідь для шляху `disabled` пояснювала точні параметри конфігурації, потрібні для ввімкнення native exec-підтверджень. Хук отримує `{ channel, channelLabel, accountId }`; канали з іменованими обліковими записами мають рендерити шляхи з областю облікового запису, як-от `channels.<channel>.accounts.<id>.execApprovals.*`, а не верхньорівневі значення за замовчуванням.
- Якщо канал може виводити стабільні DM-ідентичності, подібні до власника, з наявної конфігурації, використовуйте `createResolvedApproverActionAuthAdapter` з `openclaw/plugin-sdk/approval-runtime`, щоб обмежити `/approve` у тому самому чаті без додавання специфічної для підтверджень логіки в ядро.
- Якщо каналу потрібна доставка native-підтверджень, зосередьте код каналу на нормалізації цілі та фактах транспорту/представлення. Використовуйте `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver` і `createApproverRestrictedNativeApprovalCapability` з `openclaw/plugin-sdk/approval-runtime`. Розміщуйте специфічні для каналу факти за `approvalCapability.nativeRuntime`, бажано через `createChannelApprovalNativeRuntimeAdapter(...)` або `createLazyChannelApprovalNativeRuntimeAdapter(...)`, щоб ядро могло зібрати обробник і самостійно керувати фільтрацією запитів, маршрутизацією, дедуплікацією, строком дії, підпискою Gateway і сповіщеннями про маршрутизацію в інше місце. `nativeRuntime` поділено на кілька менших швів:
- `availability` — чи налаштовано обліковий запис і чи слід обробляти запит
- `presentation` — перетворення спільної view model підтвердження на pending/resolved/expired native payload або фінальні дії
- `transport` — підготовка цілей плюс надсилання/оновлення/видалення native-повідомлень підтвердження
- `interactions` — необов’язкові хуки bind/unbind/clear-action для native-кнопок або реакцій
- `observe` — необов’язкові хуки діагностики доставки
- Якщо каналу потрібні об’єкти, що належать runtime, як-от client, token, Bolt app або receiver Webhook, реєструйте їх через `openclaw/plugin-sdk/channel-runtime-context`. Загальний реєстр runtime-context дає ядру змогу bootstrap capability-driven handlers зі стану запуску каналу без додавання glue-коду wrapper, специфічного для підтверджень.
- Використовуйте нижчорівневі `createChannelApprovalHandler` або `createChannelNativeApprovalRuntime` лише тоді, коли capability-driven seam ще недостатньо виразний.
- Канали native-підтверджень повинні маршрутизувати і `accountId`, і `approvalKind` через ці helper-и. `accountId` зберігає область політики підтверджень для кількох облікових записів прив’язаною до правильного облікового запису бота, а `approvalKind` зберігає доступність поведінки exec проти Plugin-підтверджень для каналу без жорстко закодованих розгалужень у ядрі.
- Ядро тепер також відповідає за сповіщення про перенаправлення підтверджень. Plugin каналів не повинні надсилати власні follow-up повідомлення на кшталт «підтвердження перейшло в DM / інший канал» з `createChannelNativeApprovalRuntime`; натомість експонуйте точну маршрутизацію origin + approver-DM через спільні helper-и можливостей підтверджень і дайте ядру агрегувати фактичні доставки перед публікацією будь-якого сповіщення назад в ініціюючий чат.
- Зберігайте тип delivered approval id від початку до кінця. Native clients не повинні
  вгадувати або переписувати маршрутизацію exec чи Plugin-підтверджень на основі локального стану каналу.
- Різні типи підтверджень можуть навмисно експонувати різні native-поверхні.
  Поточні bundled-приклади:
  - Slack зберігає доступність native-маршрутизації підтверджень як для exec, так і для plugin id.
  - Matrix зберігає однакову native DM/канальну маршрутизацію і UX реакцій для exec
    і Plugin-підтверджень, водночас усе ще даючи змогу auth відрізнятися за типом підтвердження.
- `createApproverRestrictedNativeApprovalAdapter` усе ще існує як wrapper сумісності, але новий код має надавати перевагу builder можливостей і експонувати `approvalCapability` у Plugin.

Для гарячих entrypoint каналу надавайте перевагу вужчим runtime subpath, коли вам потрібна лише
одна частина цієї родини:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-gateway-runtime`
- `openclaw/plugin-sdk/approval-handler-adapter-runtime`
- `openclaw/plugin-sdk/approval-handler-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`
- `openclaw/plugin-sdk/channel-runtime-context`

Так само надавайте перевагу `openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference` і
`openclaw/plugin-sdk/reply-chunking`, коли вам не потрібна ширша
узагальнена поверхня.

Зокрема для налаштування:

- `openclaw/plugin-sdk/setup-runtime` охоплює безпечні для runtime helper-и налаштування:
  безпечні для import адаптери patch налаштування (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), виведення приміток пошуку,
  `promptResolvedAllowFrom`, `splitSetupEntries` і delegated
  builder-и setup-proxy
- `openclaw/plugin-sdk/setup-adapter-runtime` — це вузький env-aware adapter
  seam для `createEnvPatchedAccountSetupAdapter`
- `openclaw/plugin-sdk/channel-setup` охоплює builder-и optional-install setup
  плюс кілька безпечних для setup примітивів:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,

Якщо ваш канал підтримує налаштування або auth через env і загальні потоки startup/config
мають знати ці назви env до завантаження runtime, оголосіть їх у
маніфесті Plugin через `channelEnvVars`. Залишайте runtime `envVars` каналу або локальні
константи лише для copy, орієнтованого на операторів.
`createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
`createTopLevelChannelDmPolicy`, `setSetupChannelEnabled` і
`splitSetupEntries`

- використовуйте ширший seam `openclaw/plugin-sdk/setup` лише тоді, коли вам також потрібні
  важчі спільні helper-и setup/config, як-от
  `moveSingleAccountChannelSectionToDefaultAccount(...)`

Якщо ваш канал хоче лише оголошувати «спочатку встановіть цей Plugin» у поверхнях налаштування,
надавайте перевагу `createOptionalChannelSetupSurface(...)`. Згенеровані
adapter/wizard закриваються безпечно під час запису конфігурації та фіналізації, і вони повторно використовують
те саме повідомлення про необхідність встановлення в copy перевірки, finalize і docs-link.

Для інших гарячих шляхів каналу надавайте перевагу вузьким helper-ам замість ширших застарілих
поверхонь:

- `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution` і
  `openclaw/plugin-sdk/account-helpers` для конфігурації кількох облікових записів і
  резервного повернення до облікового запису за замовчуванням
- `openclaw/plugin-sdk/inbound-envelope` і
  `openclaw/plugin-sdk/inbound-reply-dispatch` для wiring маршруту/конверта вхідних повідомлень і
  record-and-dispatch
- `openclaw/plugin-sdk/messaging-targets` для парсингу/зіставлення цілей
- `openclaw/plugin-sdk/outbound-media` і
  `openclaw/plugin-sdk/outbound-runtime` для завантаження медіа плюс
  делегатів ідентичності/надсилання вихідних повідомлень
- `openclaw/plugin-sdk/thread-bindings-runtime` для життєвого циклу прив’язок потоків
  і реєстрації адаптерів
- `openclaw/plugin-sdk/agent-media-payload` лише тоді, коли все ще потрібна
  застаріла структура полів payload агента/медіа
- `openclaw/plugin-sdk/telegram-command-config` для нормалізації користувацьких команд Telegram, перевірки дублювання/конфліктів і стабільного при резервному поверненні контракту конфігурації команд

Канали лише з auth зазвичай можуть зупинитися на стандартному шляху: ядро обробляє підтвердження, а Plugin лише експонує можливості outbound/auth. Канали native-підтверджень, як-от Matrix, Slack, Telegram і власні chat-транспорти, мають використовувати спільні native helper-и замість того, щоб самостійно реалізовувати життєвий цикл підтверджень.

## Політика вхідних згадок

Розділяйте обробку вхідних згадок на два шари:

- збирання доказів, яким володіє Plugin
- оцінювання спільної політики

Для спільного шару використовуйте `openclaw/plugin-sdk/channel-inbound`.

Добре підходить для локальної логіки Plugin:

- виявлення reply-to-bot
- виявлення quoted-bot
- перевірки участі в потоці
- виключення службових/системних повідомлень
- platform-native кеші, потрібні для підтвердження участі бота

Добре підходить для спільного helper-а:

- `requireMention`
- явний результат згадки
- список дозволених неявних згадок
- обхід команд
- фінальне рішення про пропуск

Бажаний потік:

1. Обчисліть локальні факти згадок.
2. Передайте ці факти в `resolveInboundMentionDecision({ facts, policy })`.
3. Використовуйте `decision.effectiveWasMentioned`, `decision.shouldBypassMention` і `decision.shouldSkip` у вашому вхідному шлюзі.

```typescript
import {
  implicitMentionKindWhen,
  matchesMentionWithExplicit,
  resolveInboundMentionDecision,
} from "openclaw/plugin-sdk/channel-inbound";

const mentionMatch = matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const facts = {
  canDetectMention: true,
  wasMentioned: mentionMatch.matched,
  hasAnyMention: mentionMatch.hasExplicitMention,
  implicitMentionKinds: [
    ...implicitMentionKindWhen("reply_to_bot", isReplyToBot),
    ...implicitMentionKindWhen("quoted_bot", isQuoteOfBot),
  ],
};

const decision = resolveInboundMentionDecision({
  facts,
  policy: {
    isGroup,
    requireMention,
    allowedImplicitMentionKinds: requireExplicitMention ? [] : ["reply_to_bot", "quoted_bot"],
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});

if (decision.shouldSkip) return;
```

`api.runtime.channel.mentions` експонує ті самі спільні helper-и згадок для
bundled Plugin каналів, які вже залежать від injection під час runtime:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

Старіші helper-и `resolveMentionGating*` залишаються в
`openclaw/plugin-sdk/channel-inbound` лише як експорти сумісності. Новий код
має використовувати `resolveInboundMentionDecision({ facts, policy })`.

## Покроковий розбір

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Пакет і маніфест">
    Створіть стандартні файли Plugin. Поле `channel` у `package.json`
    робить це Plugin каналу. Повний опис поверхні метаданих пакета дивіться в
    [Налаштування Plugin і конфігурація](/uk/plugins/sdk-setup#openclaw-channel):

    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-chat",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "setupEntry": "./setup-entry.ts",
        "channel": {
          "id": "acme-chat",
          "label": "Acme Chat",
          "blurb": "Connect OpenClaw to Acme Chat."
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-chat",
      "kind": "channel",
      "channels": ["acme-chat"],
      "name": "Acme Chat",
      "description": "Acme Chat channel plugin",
      "configSchema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "acme-chat": {
            "type": "object",
            "properties": {
              "token": { "type": "string" },
              "allowFrom": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    }
    ```
    </CodeGroup>

  </Step>

  <Step title="Створіть об’єкт Plugin каналу">
    Інтерфейс `ChannelPlugin` має багато необов’язкових поверхонь адаптерів. Почніть із
    мінімуму — `id` і `setup` — і додавайте адаптери за потреби.

    Створіть `src/channel.ts`:

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // your platform API client

    type ResolvedAccount = {
      accountId: string | null;
      token: string;
      allowFrom: string[];
      dmPolicy: string | undefined;
    };

    function resolveAccount(
      cfg: OpenClawConfig,
      accountId?: string | null,
    ): ResolvedAccount {
      const section = (cfg.channels as Record<string, any>)?.["acme-chat"];
      const token = section?.token;
      if (!token) throw new Error("acme-chat: token is required");
      return {
        accountId: accountId ?? null,
        token,
        allowFrom: section?.allowFrom ?? [],
        dmPolicy: section?.dmSecurity,
      };
    }

    export const acmeChatPlugin = createChatChannelPlugin<ResolvedAccount>({
      base: createChannelPluginBase({
        id: "acme-chat",
        setup: {
          resolveAccount,
          inspectAccount(cfg, accountId) {
            const section =
              (cfg.channels as Record<string, any>)?.["acme-chat"];
            return {
              enabled: Boolean(section?.token),
              configured: Boolean(section?.token),
              tokenStatus: section?.token ? "available" : "missing",
            };
          },
        },
      }),

      // DM security: who can message the bot
      security: {
        dm: {
          channelKey: "acme-chat",
          resolvePolicy: (account) => account.dmPolicy,
          resolveAllowFrom: (account) => account.allowFrom,
          defaultPolicy: "allowlist",
        },
      },

      // Pairing: approval flow for new DM contacts
      pairing: {
        text: {
          idLabel: "Acme Chat username",
          message: "Send this code to verify your identity:",
          notify: async ({ target, code }) => {
            await acmeChatApi.sendDm(target, `Pairing code: ${code}`);
          },
        },
      },

      // Threading: how replies are delivered
      threading: { topLevelReplyToMode: "reply" },

      // Outbound: send messages to the platform
      outbound: {
        attachedResults: {
          sendText: async (params) => {
            const result = await acmeChatApi.sendMessage(
              params.to,
              params.text,
            );
            return { messageId: result.id };
          },
        },
        base: {
          sendMedia: async (params) => {
            await acmeChatApi.sendFile(params.to, params.filePath);
          },
        },
      },
    });
    ```

    <Accordion title="Що `createChatChannelPlugin` робить для вас">
      Замість ручної реалізації низькорівневих інтерфейсів адаптерів ви передаєте
      декларативні параметри, а builder компонує їх:

      | Параметр | Що він підключає |
      | --- | --- |
      | `security.dm` | Scoped resolver безпеки DM з полів конфігурації |
      | `pairing.text` | Потік текстового сполучення DM з обміном кодами |
      | `threading` | Resolver режиму reply-to (фіксований, з областю облікового запису або власний) |
      | `outbound.attachedResults` | Функції надсилання, які повертають метадані результату (ідентифікатори повідомлень) |

      Ви також можете передавати сирі об’єкти адаптерів замість декларативних параметрів,
      якщо вам потрібен повний контроль.
    </Accordion>

  </Step>

  <Step title="Підключіть entrypoint">
    Створіть `index.ts`:

    ```typescript index.ts
    import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineChannelPluginEntry({
      id: "acme-chat",
      name: "Acme Chat",
      description: "Acme Chat channel plugin",
      plugin: acmeChatPlugin,
      registerCliMetadata(api) {
        api.registerCli(
          ({ program }) => {
            program
              .command("acme-chat")
              .description("Acme Chat management");
          },
          {
            descriptors: [
              {
                name: "acme-chat",
                description: "Acme Chat management",
                hasSubcommands: false,
              },
            ],
          },
        );
      },
      registerFull(api) {
        api.registerGatewayMethod(/* ... */);
      },
    });
    ```

    Розміщуйте дескриптори CLI, якими володіє канал, у `registerCliMetadata(...)`, щоб OpenClaw
    міг показувати їх у довідці кореневого рівня без активації повного runtime каналу,
    тоді як звичайне повне завантаження все одно підхоплюватиме ті самі дескриптори для реєстрації
    реальних команд. Зберігайте `registerFull(...)` для роботи лише під час runtime.
    Якщо `registerFull(...)` реєструє методи Gateway RPC, використовуйте
    префікс, специфічний для Plugin. Простори імен адміністрування ядра (`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`) залишаються зарезервованими й завжди
    зіставляються з `operator.admin`.
    `defineChannelPluginEntry` автоматично обробляє поділ режимів реєстрації. Усі
    параметри дивіться в [Entry Points](/uk/plugins/sdk-entrypoints#definechannelpluginentry).

  </Step>

  <Step title="Додайте entry setup">
    Створіть `setup-entry.ts` для легкого завантаження під час онбордингу:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClaw завантажує це замість повного entry, коли канал вимкнений
    або не налаштований. Це дозволяє не підтягувати важкий runtime-код під час потоків setup.
    Докладніше дивіться в [Налаштування і конфігурація](/uk/plugins/sdk-setup#setup-entry).

    Bundled workspace канали, які виносять безпечні для setup експорти в sidecar-модулі,
    можуть використовувати `defineBundledChannelSetupEntry(...)` з
    `openclaw/plugin-sdk/channel-entry-contract`, коли їм також потрібен
    явний setter runtime під час setup.

  </Step>

  <Step title="Обробляйте вхідні повідомлення">
    Ваш Plugin має отримувати повідомлення з платформи й пересилати їх до
    OpenClaw. Типовий шаблон — це Webhook, який перевіряє запит і
    диспетчеризує його через вхідний обробник вашого каналу:

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // plugin-managed auth (verify signatures yourself)
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // Your inbound handler dispatches the message to OpenClaw.
          // The exact wiring depends on your platform SDK —
          // see a real example in the bundled Microsoft Teams or Google Chat plugin package.
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      Обробка вхідних повідомлень є специфічною для каналу. Кожен Plugin каналу
      володіє власним вхідним конвеєром. Подивіться на bundled Plugin каналів
      (наприклад, пакет Plugin Microsoft Teams або Google Chat) як на реальні шаблони.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="Тестування">
Пишіть colocated тести в `src/channel.test.ts`:

    ```typescript src/channel.test.ts
    import { describe, it, expect } from "vitest";
    import { acmeChatPlugin } from "./channel.js";

    describe("acme-chat plugin", () => {
      it("resolves account from config", () => {
        const cfg = {
          channels: {
            "acme-chat": { token: "test-token", allowFrom: ["user1"] },
          },
        } as any;
        const account = acmeChatPlugin.setup!.resolveAccount(cfg, undefined);
        expect(account.token).toBe("test-token");
      });

      it("inspects account without materializing secrets", () => {
        const cfg = {
          channels: { "acme-chat": { token: "test-token" } },
        } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(true);
        expect(result.tokenStatus).toBe("available");
      });

      it("reports missing config", () => {
        const cfg = { channels: {} } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(false);
      });
    });
    ```

    ```bash
    pnpm test -- <bundled-plugin-root>/acme-chat/
    ```

    Для спільних test helper-ів дивіться [Тестування](/uk/plugins/sdk-testing).

  </Step>
</Steps>

## Структура файлів

```
<bundled-plugin-root>/acme-chat/
├── package.json              # метадані openclaw.channel
├── openclaw.plugin.json      # Маніфест зі схемою конфігурації
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Публічні експорти (необов’язково)
├── runtime-api.ts            # Внутрішні runtime-експорти (необов’язково)
└── src/
    ├── channel.ts            # ChannelPlugin через createChatChannelPlugin
    ├── channel.test.ts       # Тести
    ├── client.ts             # API client платформи
    └── runtime.ts            # Runtime store (за потреби)
```

## Розширені теми

<CardGroup cols={2}>
  <Card title="Параметри потоків" icon="git-branch" href="/uk/plugins/sdk-entrypoints#registration-mode">
    Фіксовані, з областю облікового запису або власні режими відповіді
  </Card>
  <Card title="Інтеграція інструмента повідомлень" icon="puzzle" href="/uk/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool і виявлення дій
  </Card>
  <Card title="Визначення цілі" icon="crosshair" href="/uk/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="Runtime helper-и" icon="settings" href="/uk/plugins/sdk-runtime">
    TTS, STT, медіа, subagent через api.runtime
  </Card>
</CardGroup>

<Note>
Деякі bundled helper seam-и все ще існують для супроводу bundled-plugin і
сумісності. Вони не є рекомендованим шаблоном для нових Plugin каналів;
надавайте перевагу загальним subpath channel/setup/reply/runtime зі спільної
поверхні SDK, якщо тільки ви безпосередньо не підтримуєте цю родину bundled Plugin.
</Note>

## Наступні кроки

- [Provider Plugins](/uk/plugins/sdk-provider-plugins) — якщо ваш Plugin також надає моделі
- [Огляд SDK](/uk/plugins/sdk-overview) — повний довідник з import subpath
- [Тестування SDK](/uk/plugins/sdk-testing) — тестові утиліти та contract-тести
- [Маніфест Plugin](/uk/plugins/manifest) — повна схема маніфесту
