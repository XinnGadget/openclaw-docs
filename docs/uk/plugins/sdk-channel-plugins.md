---
read_when:
    - Ви створюєте новий плагін каналу обміну повідомленнями
    - Ви хочете підключити OpenClaw до платформи обміну повідомленнями
    - Вам потрібно зрозуміти поверхню адаптера ChannelPlugin
sidebarTitle: Channel Plugins
summary: Покроковий посібник зі створення плагіна каналу обміну повідомленнями для OpenClaw
title: Створення плагінів каналів
x-i18n:
    generated_at: "2026-04-06T18:56:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 25ac0591d9b0ba401925b29ae4b9572f18b2cbffc2b6ca6ed5252740e7cf97e9
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# Створення плагінів каналів

Цей посібник описує створення плагіна каналу, який підключає OpenClaw до
платформи обміну повідомленнями. Наприкінці у вас буде робочий канал із DM-безпекою,
сполученням, потоками відповідей і вихідними повідомленнями.

<Info>
  Якщо ви ще не створювали жодного плагіна OpenClaw, спочатку прочитайте
  [Початок роботи](/uk/plugins/building-plugins) про базову структуру пакета
  та налаштування маніфесту.
</Info>

## Як працюють плагіни каналів

Плагінам каналів не потрібні власні інструменти send/edit/react. OpenClaw зберігає
один спільний інструмент `message` у core. Ваш плагін відповідає за:

- **Конфігурація** — визначення облікового запису та майстер налаштування
- **Безпека** — політика DM та списки дозволених
- **Сполучення** — потік підтвердження DM
- **Граматика сесії** — як ідентифікатори розмов, специфічні для провайдера, зіставляються з базовими чатами, ідентифікаторами потоків та резервними батьківськими значеннями
- **Вихідні повідомлення** — надсилання тексту, медіа та опитувань на платформу
- **Потоки** — як упорядковуються відповіді

Core відповідає за спільний інструмент повідомлень, підключення промптів, зовнішню форму ключа сесії,
загальний облік `:thread:` і диспетчеризацію.

Якщо ваша платформа зберігає додаткову область дії всередині ідентифікаторів розмов, залишайте цей розбір
у плагіні за допомогою `messaging.resolveSessionConversation(...)`. Це
канонічний хук для зіставлення `rawId` з базовим ідентифікатором розмови, необов’язковим ідентифікатором потоку,
явним `baseConversationId` і будь-якими `parentConversationCandidates`.
Коли ви повертаєте `parentConversationCandidates`, зберігайте їх порядок від
найвужчого батьківського елемента до найширшої/базової розмови.

Вбудовані плагіни, яким потрібен той самий розбір до запуску реєстру каналів,
також можуть експортувати файл верхнього рівня `session-key-api.ts` з відповідним
експортом `resolveSessionConversation(...)`. Core використовує цю безпечну для bootstrap поверхню
лише тоді, коли реєстр плагінів runtime ще недоступний.

`messaging.resolveParentConversationCandidates(...)` залишається доступним як
застарілий резервний механізм сумісності, коли плагіну потрібні лише
резервні батьківські значення поверх загального/raw id. Якщо існують обидва хуки, core використовує
спочатку `resolveSessionConversation(...).parentConversationCandidates` і лише потім
повертається до `resolveParentConversationCandidates(...)`, якщо канонічний хук
їх не включає.

## Підтвердження та можливості каналу

Більшості плагінів каналів не потрібен код, специфічний для підтверджень.

- Core відповідає за `/approve` у тому самому чаті, спільні payload кнопок підтвердження та загальну резервну доставку.
- Віддавайте перевагу одному об’єкту `approvalCapability` у плагіні каналу, коли каналу потрібна поведінка, специфічна для підтверджень.
- `approvalCapability.authorizeActorAction` і `approvalCapability.getActionAvailabilityState` — це канонічний seam автентифікації підтверджень.
- Якщо ваш канал надає нативні підтвердження exec, реалізуйте `approvalCapability.getActionAvailabilityState` навіть тоді, коли нативний транспорт повністю живе в `approvalCapability.native`. Core використовує цей хук доступності, щоб розрізняти `enabled` і `disabled`, визначати, чи підтримує ініціюючий канал нативні підтвердження, і включати канал до інструкцій резервного сценарію для нативних клієнтів.
- Використовуйте `outbound.shouldSuppressLocalPayloadPrompt` або `outbound.beforeDeliverPayload` для поведінки життєвого циклу payload, специфічної для каналу, наприклад приховування дубльованих локальних запитів підтвердження або надсилання індикаторів набору тексту перед доставкою.
- Використовуйте `approvalCapability.delivery` лише для маршрутизації нативних підтверджень або придушення резервного сценарію.
- Використовуйте `approvalCapability.render` лише тоді, коли каналу справді потрібні власні payload підтвердження замість спільного рендерера.
- Використовуйте `approvalCapability.describeExecApprovalSetup`, якщо канал хоче, щоб відповідь для вимкненого шляху пояснювала точні параметри конфігурації, потрібні для ввімкнення нативних підтверджень exec. Хук отримує `{ channel, channelLabel, accountId }`; канали з іменованими обліковими записами мають відображати шляхи з областю облікового запису, такі як `channels.<channel>.accounts.<id>.execApprovals.*`, замість значень верхнього рівня за замовчуванням.
- Якщо канал може вивести стабільні DM-ідентичності на кшталт власника з наявної конфігурації, використовуйте `createResolvedApproverActionAuthAdapter` з `openclaw/plugin-sdk/approval-runtime`, щоб обмежити `/approve` в тому самому чаті без додавання логіки core, специфічної для підтверджень.
- Якщо каналу потрібна доставка нативних підтверджень, зосередьте код каналу на нормалізації цілей і хуках транспорту. Використовуйте `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver`, `createApproverRestrictedNativeApprovalCapability` і `createChannelNativeApprovalRuntime` з `openclaw/plugin-sdk/approval-runtime`, щоб core відповідав за фільтрацію запитів, маршрутизацію, дедуплікацію, термін дії та підписку gateway.
- Канали нативних підтверджень мають маршрутизувати і `accountId`, і `approvalKind` через ці helper-и. `accountId` зберігає область політики підтверджень для кількох облікових записів у межах правильного облікового запису бота, а `approvalKind` зберігає доступність поведінки exec і plugin підтверджень для каналу без жорстко закодованих гілок у core.
- Зберігайте тип доставленого id підтвердження від початку до кінця. Нативні клієнти не повинні
  вгадувати або переписувати маршрутизацію підтверджень exec чи plugin на основі локального стану каналу.
- Різні типи підтверджень можуть навмисно мати різні нативні поверхні.
  Поточні вбудовані приклади:
  - Slack зберігає доступність нативної маршрутизації підтверджень як для exec, так і для id plugin.
  - Matrix зберігає нативну маршрутизацію DM/каналу лише для підтверджень exec і залишає
    підтвердження plugin на спільному шляху `/approve` в тому самому чаті.
- `createApproverRestrictedNativeApprovalAdapter` досі існує як обгортка сумісності, але новий код має віддавати перевагу builder-у capability і експортувати `approvalCapability` у плагіні.

Для гарячих точок входу каналу віддавайте перевагу вужчим runtime subpath-ам, коли вам потрібна лише одна частина цього сімейства:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`

Так само віддавайте перевагу `openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference` і
`openclaw/plugin-sdk/reply-chunking`, коли вам не потрібна ширша umbrella
поверхня.

Для налаштування зокрема:

- `openclaw/plugin-sdk/setup-runtime` охоплює безпечні для runtime helper-и налаштування:
  безпечні для імпорту patched-адаптери налаштування (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), вивід приміток пошуку,
  `promptResolvedAllowFrom`, `splitSetupEntries` і delegated
  builder-и setup-proxy
- `openclaw/plugin-sdk/setup-adapter-runtime` — це вузький env-aware adapter
  seam для `createEnvPatchedAccountSetupAdapter`
- `openclaw/plugin-sdk/channel-setup` охоплює builder-и optional-install setup
  плюс кілька безпечних для setup примітивів:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,

Якщо ваш канал підтримує налаштування або автентифікацію через env і загальні потоки startup/config
мають знати ці назви env до завантаження runtime, оголосіть їх у
маніфесті плагіна через `channelEnvVars`. Залишайте runtime `envVars` каналу або локальні
константи лише для тексту, орієнтованого на операторів.
`createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
`createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, і
`splitSetupEntries`

- використовуйте ширший seam `openclaw/plugin-sdk/setup` лише тоді, коли вам також потрібні
  важчі спільні helper-и setup/config, наприклад
  `moveSingleAccountChannelSectionToDefaultAccount(...)`

Якщо ваш канал хоче лише повідомляти в поверхнях setup
«спочатку встановіть цей плагін», віддавайте перевагу `createOptionalChannelSetupSurface(...)`. Згенерований
адаптер/майстер працює за принципом fail closed для записів у конфігурацію та фіналізації, і вони повторно використовують
те саме повідомлення про необхідність встановлення в копії для валідації, finalize та посилань на документацію.

Для інших гарячих шляхів каналу віддавайте перевагу вузьким helper-ам замість ширших застарілих
поверхонь:

- `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution` і
  `openclaw/plugin-sdk/account-helpers` для конфігурації кількох облікових записів і
  резервного сценарію облікового запису за замовчуванням
- `openclaw/plugin-sdk/inbound-envelope` і
  `openclaw/plugin-sdk/inbound-reply-dispatch` для маршруту/конверта inbound і
  підключення record-and-dispatch
- `openclaw/plugin-sdk/messaging-targets` для аналізу/зіставлення цілей
- `openclaw/plugin-sdk/outbound-media` і
  `openclaw/plugin-sdk/outbound-runtime` для завантаження медіа плюс outbound
  делегатів ідентичності/надсилання
- `openclaw/plugin-sdk/thread-bindings-runtime` для життєвого циклу thread-binding
  і реєстрації адаптерів
- `openclaw/plugin-sdk/agent-media-payload` лише тоді, коли все ще потрібна застаріла
  схема полів payload агента/медіа
- `openclaw/plugin-sdk/telegram-command-config` для нормалізації власних команд Telegram, перевірки дублювань/конфліктів і стабільного контракту конфігурації команд для резервного сценарію

Канали лише з автентифікацією зазвичай можуть зупинитися на шляху за замовчуванням: core обробляє підтвердження, а плагін просто надає можливості outbound/auth. Канали нативних підтверджень, такі як Matrix, Slack, Telegram і власні chat-транспорти, повинні використовувати спільні helper-и для native, а не реалізовувати власний життєвий цикл підтверджень.

## Покроковий приклад

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Пакет і маніфест">
    Створіть стандартні файли плагіна. Поле `channel` у `package.json`
    робить це плагіном каналу. Повну поверхню метаданих пакета
    дивіться в [Налаштування плагіна та конфігурація](/uk/plugins/sdk-setup#openclawchannel):

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

  <Step title="Створіть об’єкт плагіна каналу">
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

    <Accordion title="Що робить для вас createChatChannelPlugin">
      Замість того щоб вручну реалізовувати низькорівневі інтерфейси адаптерів, ви передаєте
      декларативні параметри, а builder компонує їх:

      | Параметр | Що він підключає |
      | --- | --- |
      | `security.dm` | Розпізнавач scoped DM security з полів конфігурації |
      | `pairing.text` | Потік текстового DM-сполучення з обміном кодами |
      | `threading` | Розпізнавач режиму reply-to (фіксований, у межах облікового запису або власний) |
      | `outbound.attachedResults` | Функції надсилання, які повертають метадані результату (ідентифікатори повідомлень) |

      Ви також можете передавати необроблені об’єкти адаптерів замість декларативних параметрів,
      якщо вам потрібен повний контроль.
    </Accordion>

  </Step>

  <Step title="Підключіть точку входу">
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

    Розміщуйте дескриптори CLI, що належать каналу, у `registerCliMetadata(...)`, щоб OpenClaw
    міг показувати їх у кореневій довідці без активації повного runtime каналу,
    тоді як звичайні повні завантаження все одно підхоплюватимуть ті самі дескриптори для реєстрації
    реальних команд. Залишайте `registerFull(...)` для роботи лише в runtime.
    Якщо `registerFull(...)` реєструє RPC-методи gateway, використовуйте
    префікс, специфічний для плагіна. Простори імен admin у core (`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`) залишаються зарезервованими й завжди
    зіставляються з `operator.admin`.
    `defineChannelPluginEntry` автоматично обробляє розділення режимів реєстрації. Усі
    параметри дивіться в [Точки входу](/uk/plugins/sdk-entrypoints#definechannelpluginentry).

  </Step>

  <Step title="Додайте точку входу для налаштування">
    Створіть `setup-entry.ts` для легкого завантаження під час онбордингу:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClaw завантажує це замість повної точки входу, коли канал вимкнений
    або не налаштований. Це дозволяє уникнути підвантаження важкого runtime-коду під час потоків налаштування.
    Докладніше дивіться в [Налаштування та конфігурація](/uk/plugins/sdk-setup#setup-entry).

  </Step>

  <Step title="Обробляйте вхідні повідомлення">
    Ваш плагін має отримувати повідомлення з платформи та пересилати їх до
    OpenClaw. Типовий шаблон — це webhook, який перевіряє запит і
    диспетчеризує його через inbound-обробник вашого каналу:

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
      Обробка вхідних повідомлень залежить від конкретного каналу. Кожен плагін каналу відповідає
      за власний inbound-пайплайн. Подивіться на вбудовані плагіни каналів
      (наприклад, пакет плагіна Microsoft Teams або Google Chat), щоб побачити реальні шаблони.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="Тестування">
Пишіть колоковані тести в `src/channel.test.ts`:

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

    Спільні helper-и для тестування дивіться в [Тестування](/uk/plugins/sdk-testing).

  </Step>
</Steps>

## Структура файлів

```
<bundled-plugin-root>/acme-chat/
├── package.json              # Метадані openclaw.channel
├── openclaw.plugin.json      # Маніфест зі схемою конфігурації
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Публічні експорти (необов’язково)
├── runtime-api.ts            # Внутрішні runtime-експорти (необов’язково)
└── src/
    ├── channel.ts            # ChannelPlugin через createChatChannelPlugin
    ├── channel.test.ts       # Тести
    ├── client.ts             # Клієнт API платформи
    └── runtime.ts            # Runtime-сховище (за потреби)
```

## Розширені теми

<CardGroup cols={2}>
  <Card title="Параметри потоків" icon="git-branch" href="/uk/plugins/sdk-entrypoints#registration-mode">
    Фіксовані режими відповідей, режими в межах облікового запису або власні режими
  </Card>
  <Card title="Інтеграція інструмента повідомлень" icon="puzzle" href="/uk/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool і виявлення дій
  </Card>
  <Card title="Визначення цілі" icon="crosshair" href="/uk/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="Runtime-helper-и" icon="settings" href="/uk/plugins/sdk-runtime">
    TTS, STT, медіа, subagent через api.runtime
  </Card>
</CardGroup>

<Note>
Деякі вбудовані helper-seam-и все ще існують для супроводу вбудованих плагінів і
сумісності. Вони не є рекомендованим шаблоном для нових плагінів каналів;
віддавайте перевагу загальним channel/setup/reply/runtime subpath-ам зі спільної
поверхні SDK, якщо тільки ви не супроводжуєте безпосередньо це сімейство вбудованих плагінів.
</Note>

## Наступні кроки

- [Плагіни провайдерів](/uk/plugins/sdk-provider-plugins) — якщо ваш плагін також надає моделі
- [Огляд SDK](/uk/plugins/sdk-overview) — повний довідник імпортів subpath
- [Тестування SDK](/uk/plugins/sdk-testing) — утиліти тестування та контрактні тести
- [Маніфест плагіна](/uk/plugins/manifest) — повна схема маніфесту
