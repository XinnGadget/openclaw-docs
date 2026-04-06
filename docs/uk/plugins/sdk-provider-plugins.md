---
read_when:
    - Ви створюєте новий плагін постачальника моделей
    - Ви хочете додати сумісний з OpenAI проксі або власну LLM до OpenClaw
    - Вам потрібно зрозуміти автентифікацію постачальників, каталоги та runtime-хуки
sidebarTitle: Provider Plugins
summary: Покроковий посібник зі створення плагіна постачальника моделей для OpenClaw
title: Створення плагінів постачальників
x-i18n:
    generated_at: "2026-04-06T12:29:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 21c888a988f6128f2c77b73ee4962ae7ad7b8a6c1b7d302610788c81ad25b0db
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# Створення плагінів постачальників

У цьому посібнику розглянуто створення плагіна постачальника, який додає
постачальника моделей (LLM) до OpenClaw. Наприкінці у вас буде постачальник із каталогом моделей,
автентифікацією за API-ключем і динамічним визначенням моделей.

<Info>
  Якщо ви раніше не створювали жодного плагіна OpenClaw, спочатку прочитайте
  [Getting Started](/uk/plugins/building-plugins), щоб ознайомитися з базовою структурою
  пакета та налаштуванням маніфесту.
</Info>

## Покроковий розбір

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Пакет і маніфест">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-ai",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "providers": ["acme-ai"],
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
      "id": "acme-ai",
      "name": "Acme AI",
      "description": "Acme AI model provider",
      "providers": ["acme-ai"],
      "modelSupport": {
        "modelPrefixes": ["acme-"]
      },
      "providerAuthEnvVars": {
        "acme-ai": ["ACME_AI_API_KEY"]
      },
      "providerAuthChoices": [
        {
          "provider": "acme-ai",
          "method": "api-key",
          "choiceId": "acme-ai-api-key",
          "choiceLabel": "Acme AI API key",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "Acme AI API key"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Маніфест оголошує `providerAuthEnvVars`, щоб OpenClaw міг виявляти
    облікові дані без завантаження runtime вашого плагіна. `modelSupport` є необов’язковим
    і дозволяє OpenClaw автоматично завантажувати ваш плагін постачальника за скороченими ідентифікаторами моделей,
    такими як `acme-large`, ще до появи runtime-хуків. Якщо ви публікуєте
    постачальника в ClawHub, поля `openclaw.compat` і `openclaw.build`
    є обов’язковими в `package.json`.

  </Step>

  <Step title="Зареєструйте постачальника">
    Мінімальному постачальнику потрібні `id`, `label`, `auth` і `catalog`:

    ```typescript index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { createProviderApiKeyAuthMethod } from "openclaw/plugin-sdk/provider-auth";

    export default definePluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
      register(api) {
        api.registerProvider({
          id: "acme-ai",
          label: "Acme AI",
          docsPath: "/providers/acme-ai",
          envVars: ["ACME_AI_API_KEY"],

          auth: [
            createProviderApiKeyAuthMethod({
              providerId: "acme-ai",
              methodId: "api-key",
              label: "Acme AI API key",
              hint: "API key from your Acme AI dashboard",
              optionKey: "acmeAiApiKey",
              flagName: "--acme-ai-api-key",
              envVar: "ACME_AI_API_KEY",
              promptMessage: "Enter your Acme AI API key",
              defaultModel: "acme-ai/acme-large",
            }),
          ],

          catalog: {
            order: "simple",
            run: async (ctx) => {
              const apiKey =
                ctx.resolveProviderApiKey("acme-ai").apiKey;
              if (!apiKey) return null;
              return {
                provider: {
                  baseUrl: "https://api.acme-ai.com/v1",
                  apiKey,
                  api: "openai-completions",
                  models: [
                    {
                      id: "acme-large",
                      name: "Acme Large",
                      reasoning: true,
                      input: ["text", "image"],
                      cost: { input: 3, output: 15, cacheRead: 0.3, cacheWrite: 3.75 },
                      contextWindow: 200000,
                      maxTokens: 32768,
                    },
                    {
                      id: "acme-small",
                      name: "Acme Small",
                      reasoning: false,
                      input: ["text"],
                      cost: { input: 1, output: 5, cacheRead: 0.1, cacheWrite: 1.25 },
                      contextWindow: 128000,
                      maxTokens: 8192,
                    },
                  ],
                },
              };
            },
          },
        });
      },
    });
    ```

    Це вже робочий постачальник. Тепер користувачі можуть виконати
    `openclaw onboard --acme-ai-api-key <key>` і вибрати
    `acme-ai/acme-large` як свою модель.

    Для вбудованих постачальників, які реєструють лише одного текстового постачальника з
    автентифікацією за API-ключем плюс один runtime на основі каталогу, краще використовувати вужчий хелпер
    `defineSingleProviderPluginEntry(...)`:

    ```typescript
    import { defineSingleProviderPluginEntry } from "openclaw/plugin-sdk/provider-entry";

    export default defineSingleProviderPluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
      provider: {
        label: "Acme AI",
        docsPath: "/providers/acme-ai",
        auth: [
          {
            methodId: "api-key",
            label: "Acme AI API key",
            hint: "API key from your Acme AI dashboard",
            optionKey: "acmeAiApiKey",
            flagName: "--acme-ai-api-key",
            envVar: "ACME_AI_API_KEY",
            promptMessage: "Enter your Acme AI API key",
            defaultModel: "acme-ai/acme-large",
          },
        ],
        catalog: {
          buildProvider: () => ({
            api: "openai-completions",
            baseUrl: "https://api.acme-ai.com/v1",
            models: [{ id: "acme-large", name: "Acme Large" }],
          }),
        },
      },
    });
    ```

    Якщо ваш потік автентифікації також має змінювати `models.providers.*`, псевдоніми та
    модель агента за замовчуванням під час онбордингу, використовуйте preset-хелпери з
    `openclaw/plugin-sdk/provider-onboard`. Найвужчі хелпери:
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)` і
    `createModelCatalogPresetAppliers(...)`.

    Коли нативна кінцева точка постачальника підтримує потокові блоки usage у
    звичайному транспорті `openai-completions`, віддавайте перевагу спільним хелперам каталогу з
    `openclaw/plugin-sdk/provider-catalog-shared`, а не жорстко прописаним
    перевіркам ідентифікатора постачальника. `supportsNativeStreamingUsageCompat(...)` і
    `applyProviderNativeStreamingUsageCompat(...)` визначають підтримку за мапою можливостей
    кінцевої точки, тож нативні кінцеві точки у стилі Moonshot/DashScope також
    зможуть підключатися, навіть якщо плагін використовує власний ідентифікатор постачальника.

  </Step>

  <Step title="Додайте динамічне визначення моделей">
    Якщо ваш постачальник приймає довільні ідентифікатори моделей (наприклад, проксі або маршрутизатор),
    додайте `resolveDynamicModel`:

    ```typescript
    api.registerProvider({
      // ... id, label, auth, catalog from above

      resolveDynamicModel: (ctx) => ({
        id: ctx.modelId,
        name: ctx.modelId,
        provider: "acme-ai",
        api: "openai-completions",
        baseUrl: "https://api.acme-ai.com/v1",
        reasoning: false,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 128000,
        maxTokens: 8192,
      }),
    });
    ```

    Якщо для визначення потрібен мережевий виклик, використовуйте `prepareDynamicModel` для асинхронного
    прогрівання — після його завершення `resolveDynamicModel` виконується знову.

  </Step>

  <Step title="Додайте runtime-хуки (за потреби)">
    Більшості постачальників потрібні лише `catalog` + `resolveDynamicModel`. Додавайте хуки
    поступово, у міру того як це потрібно вашому постачальнику.

    Спільні builder-хелпери тепер охоплюють найпоширеніші сімейства replay/tool-compat,
    тому плагінам зазвичай не потрібно вручну підключати кожен хук окремо:

    ```typescript
    import { buildProviderReplayFamilyHooks } from "openclaw/plugin-sdk/provider-model-shared";
    import { buildProviderStreamFamilyHooks } from "openclaw/plugin-sdk/provider-stream";
    import { buildProviderToolCompatFamilyHooks } from "openclaw/plugin-sdk/provider-tools";

    const GOOGLE_FAMILY_HOOKS = {
      ...buildProviderReplayFamilyHooks({ family: "google-gemini" }),
      ...buildProviderStreamFamilyHooks("google-thinking"),
      ...buildProviderToolCompatFamilyHooks("gemini"),
    };

    api.registerProvider({
      id: "acme-gemini-compatible",
      // ...
      ...GOOGLE_FAMILY_HOOKS,
    });
    ```

    Доступні сьогодні сімейства replay:

    | Family | Що воно підключає |
    | --- | --- |
    | `openai-compatible` | Спільна політика replay у стилі OpenAI для транспортів, сумісних з OpenAI, включно з санітизацією ідентифікаторів викликів інструментів, виправленнями порядку assistant-first і загальною валідацією Gemini-turn там, де вона потрібна транспорту |
    | `anthropic-by-model` | Політика replay з урахуванням Claude, що обирається за `modelId`, тому транспорти Anthropic-message отримують очищення thinking-блоків, специфічне для Claude, лише коли визначена модель справді є ідентифікатором Claude |
    | `google-gemini` | Нативна політика replay для Gemini плюс bootstrap-санітизація replay і режим tagged reasoning-output |
    | `passthrough-gemini` | Санітизація thought-signature Gemini для моделей Gemini, що працюють через сумісні з OpenAI проксі-транспорти; не вмикає нативну валідацію replay Gemini або bootstrap-перезаписування |
    | `hybrid-anthropic-openai` | Гібридна політика для постачальників, які поєднують поверхні моделей Anthropic-message і OpenAI-compatible в одному плагіні; необов’язкове відкидання thinking-блоків лише для Claude залишається обмеженим стороною Anthropic |

    Реальні вбудовані приклади:

    - `google`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode` і `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` і `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai` і `zai`: `openai-compatible`

    Доступні сьогодні сімейства stream:

    | Family | Що воно підключає |
    | --- | --- |
    | `google-thinking` | Нормалізація payload thinking Gemini у спільному stream-шляху |
    | `kilocode-thinking` | Обгортка reasoning Kilo у спільному proxy stream-шляху, де `kilo/auto` та непідтримувані proxy reasoning id пропускають інжектований thinking |
    | `moonshot-thinking` | Мапінг бінарного payload native-thinking Moonshot з config + рівня `/think` |
    | `minimax-fast-mode` | Перезапис моделі fast-mode MiniMax у спільному stream-шляху |
    | `openai-responses-defaults` | Спільні нативні обгортки OpenAI/Codex Responses: attribution-заголовки, `/fast`/`serviceTier`, деталізація тексту, нативний вебпошук Codex, формування payload для сумісності reasoning і керування контекстом Responses |
    | `openrouter-thinking` | Обгортка reasoning OpenRouter для proxy-маршрутів, із централізованою обробкою пропусків для непідтримуваних моделей/`auto` |
    | `tool-stream-default-on` | Увімкнена за замовчуванням обгортка `tool_stream` для постачальників на кшталт Z.AI, які хочуть потокову передачу інструментів, якщо її не вимкнено явно |

    Реальні вбудовані приклади:

    - `google`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` і `minimax-portal`: `minimax-fast-mode`
    - `openai` і `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared` також експортує enum сімейств replay
    плюс спільні хелпери, з яких ці сімейства побудовані. Поширені публічні
    експорти включають:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - спільні builder-и replay, такі як `buildOpenAICompatibleReplayPolicy(...)`,
      `buildAnthropicReplayPolicyForModel(...)`,
      `buildGoogleGeminiReplayPolicy(...)` і
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - хелпери replay для Gemini, такі як `sanitizeGoogleGeminiReplayHistory(...)`
      і `resolveTaggedReasoningOutputMode()`
    - хелпери кінцевих точок/моделей, такі як `resolveProviderEndpoint(...)`,
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)` і
      `normalizeNativeXaiModelId(...)`

    `openclaw/plugin-sdk/provider-stream` надає і builder сімейств, і
    публічні wrapper-хелпери, які ці сімейства повторно використовують. Поширені публічні експорти
    включають:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - спільні обгортки OpenAI/Codex, такі як
      `createOpenAIAttributionHeadersWrapper(...)`,
      `createOpenAIFastModeWrapper(...)`,
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)` і
      `createCodexNativeWebSearchWrapper(...)`
    - спільні proxy/provider-обгортки, такі як `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)` і `createMinimaxFastModeWrapper(...)`

    Деякі stream-хелпери навмисно залишаються локальними для постачальника. Поточний вбудований
    приклад: `@openclaw/anthropic-provider` експортує
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` і
    низькорівневі builder-и обгорток Anthropic зі свого публічного seam `api.ts` /
    `contract-api.ts`. Ці хелпери залишаються специфічними для Anthropic, оскільки
    також кодують обробку Claude OAuth beta і gating `context1m`.

    Інші вбудовані постачальники також тримають специфічні для транспорту обгортки локально, коли
    цю поведінку неможливо чисто поділити між сімействами. Поточний приклад: вбудований
    плагін xAI зберігає нативне формування xAI Responses у власному
    `wrapStreamFn`, включно з перезаписуванням псевдонімів `/fast`, `tool_stream`
    за замовчуванням, очищенням непідтримуваних strict-tool і видаленням payload reasoning,
    специфічного для xAI.

    `openclaw/plugin-sdk/provider-tools` наразі надає одне спільне
    сімейство tool-schema плюс спільні хелпери schema/compat:

    - `ProviderToolCompatFamily` документує наявний сьогодні інвентар спільних сімейств.
    - `buildProviderToolCompatFamilyHooks("gemini")` підключає очищення Gemini schema
      + діагностику для постачальників, яким потрібні безпечні для Gemini схеми інструментів.
    - `normalizeGeminiToolSchemas(...)` і `inspectGeminiToolSchemas(...)`
      є базовими публічними Gemini schema-хелперами.
    - `resolveXaiModelCompatPatch()` повертає вбудований compat-патч xAI:
      `toolSchemaProfile: "xai"`, непідтримувані ключові слова schema, нативну підтримку
      `web_search` і декодування аргументів викликів інструментів із HTML-сутностями.
    - `applyXaiModelCompat(model)` застосовує той самий compat-патч xAI до
      визначеної моделі, перш ніж вона потрапить до runner-а.

    Реальний вбудований приклад: плагін xAI використовує `normalizeResolvedModel` плюс
    `contributeResolvedModelCompat`, щоб зберегти метадані compat у власності
    постачальника, а не жорстко прописувати правила xAI в core.

    Той самий шаблон на рівні кореня пакета також лежить в основі інших вбудованих постачальників:

    - `@openclaw/openai-provider`: `api.ts` експортує builder-и постачальника,
      хелпери моделі за замовчуванням і builder-и realtime-постачальника
    - `@openclaw/openrouter-provider`: `api.ts` експортує builder
      постачальника плюс хелпери онбордингу/конфігурації

    <Tabs>
      <Tab title="Обмін токенів">
        Для постачальників, яким потрібен обмін токенів перед кожним викликом inference:

        ```typescript
        prepareRuntimeAuth: async (ctx) => {
          const exchanged = await exchangeToken(ctx.apiKey);
          return {
            apiKey: exchanged.token,
            baseUrl: exchanged.baseUrl,
            expiresAt: exchanged.expiresAt,
          };
        },
        ```
      </Tab>
      <Tab title="Користувацькі заголовки">
        Для постачальників, яким потрібні користувацькі заголовки запитів або зміни тіла запиту:

        ```typescript
        // wrapStreamFn returns a StreamFn derived from ctx.streamFn
        wrapStreamFn: (ctx) => {
          if (!ctx.streamFn) return undefined;
          const inner = ctx.streamFn;
          return async (params) => {
            params.headers = {
              ...params.headers,
              "X-Acme-Version": "2",
            };
            return inner(params);
          };
        },
        ```
      </Tab>
      <Tab title="Ідентичність нативного транспорту">
        Для постачальників, яким потрібні нативні заголовки або метадані запитів/сесій на
        узагальнених HTTP- або WebSocket-транспортах:

        ```typescript
        resolveTransportTurnState: (ctx) => ({
          headers: {
            "x-request-id": ctx.turnId,
          },
          metadata: {
            session_id: ctx.sessionId ?? "",
            turn_id: ctx.turnId,
          },
        }),
        resolveWebSocketSessionPolicy: (ctx) => ({
          headers: {
            "x-session-id": ctx.sessionId ?? "",
          },
          degradeCooldownMs: 60_000,
        }),
        ```
      </Tab>
      <Tab title="Usage і білінг">
        Для постачальників, які надають дані usage/білінгу:

        ```typescript
        resolveUsageAuth: async (ctx) => {
          const auth = await ctx.resolveOAuthToken();
          return auth ? { token: auth.token } : null;
        },
        fetchUsageSnapshot: async (ctx) => {
          return await fetchAcmeUsage(ctx.token, ctx.timeoutMs);
        },
        ```
      </Tab>
    </Tabs>

    <Accordion title="Усі доступні хуки постачальника">
      OpenClaw викликає хуки в такому порядку. Більшість постачальників використовують лише 2-3:

      | # | Hook | Коли використовувати |
      | --- | --- | --- |
      | 1 | `catalog` | Каталог моделей або значення `baseUrl` за замовчуванням |
      | 2 | `applyConfigDefaults` | Глобальні значення за замовчуванням, що належать постачальнику, під час materialization конфігурації |
      | 3 | `normalizeModelId` | Очищення застарілих/preview псевдонімів ідентифікаторів моделей перед пошуком |
      | 4 | `normalizeTransport` | Очищення `api` / `baseUrl` для сімейства постачальника перед загальним складанням моделі |
      | 5 | `normalizeConfig` | Нормалізація конфігурації `models.providers.<id>` |
      | 6 | `applyNativeStreamingUsageCompat` | Перезаписування native streaming-usage compat для config-постачальників |
      | 7 | `resolveConfigApiKey` | Визначення автентифікації за env-marker, що належить постачальнику |
      | 8 | `resolveSyntheticAuth` | Синтетична автентифікація local/self-hosted або на основі config |
      | 9 | `shouldDeferSyntheticProfileAuth` | Опустити синтетичні placeholder-и збереженого профілю нижче за env/config auth |
      | 10 | `resolveDynamicModel` | Приймати довільні ідентифікатори моделей upstream |
      | 11 | `prepareDynamicModel` | Асинхронне отримання метаданих перед визначенням |
      | 12 | `normalizeResolvedModel` | Перезаписування транспорту перед runner-ом |

    Примітки щодо runtime fallback:

    - `normalizeConfig` спочатку перевіряє відповідного постачальника, а потім інші
      плагіни постачальників, здатні обробляти хуки, доки один із них справді не змінить конфігурацію.
      Якщо жоден хук постачальника не перепише підтримуваний запис конфігурації сімейства Google,
      усе одно буде застосовано вбудований нормалізатор конфігурації Google.
    - `resolveConfigApiKey` використовує хук постачальника, якщо він наданий. Вбудований
      шлях `amazon-bedrock` також має тут вбудований resolver AWS env-marker,
      хоча runtime-автентифікація Bedrock досі використовує стандартний
      AWS SDK chain.
      | 13 | `contributeResolvedModelCompat` | Compat-прапорці для вендорських моделей за іншим сумісним транспортом |
      | 14 | `capabilities` | Застарілий статичний набір можливостей; лише для сумісності |
      | 15 | `normalizeToolSchemas` | Очищення схеми інструментів, що належить постачальнику, перед реєстрацією |
      | 16 | `inspectToolSchemas` | Діагностика схем інструментів, що належить постачальнику |
      | 17 | `resolveReasoningOutputMode` | Контракт reasoning-output: tagged чи native |
      | 18 | `prepareExtraParams` | Параметри запиту за замовчуванням |
      | 19 | `createStreamFn` | Повністю користувацький транспорт StreamFn |
      | 20 | `wrapStreamFn` | Користувацькі обгортки заголовків/тіла в стандартному stream-шляху |
      | 21 | `resolveTransportTurnState` | Нативні заголовки/метадані для кожного turn |
      | 22 | `resolveWebSocketSessionPolicy` | Нативні заголовки сесії WS / охолодження |
      | 23 | `formatApiKey` | Користувацька форма runtime-токена |
      | 24 | `refreshOAuth` | Користувацьке оновлення OAuth |
      | 25 | `buildAuthDoctorHint` | Підказка щодо виправлення автентифікації |
      | 26 | `matchesContextOverflowError` | Виявлення переповнення, що належить постачальнику |
      | 27 | `classifyFailoverReason` | Класифікація rate-limit/overload, що належить постачальнику |
      | 28 | `isCacheTtlEligible` | Gating TTL кешу prompt-ів |
      | 29 | `buildMissingAuthMessage` | Користувацька підказка про відсутню автентифікацію |
      | 30 | `suppressBuiltInModel` | Приховати застарілі рядки upstream |
      | 31 | `augmentModelCatalog` | Синтетичні рядки для прямої сумісності вперед |
      | 32 | `isBinaryThinking` | Бінарне thinking увімк./вимк. |
      | 33 | `supportsXHighThinking` | Підтримка reasoning `xhigh` |
      | 34 | `resolveDefaultThinkingLevel` | Політика `/think` за замовчуванням |
      | 35 | `isModernModelRef` | Відповідність live/smoke моделей |
      | 36 | `prepareRuntimeAuth` | Обмін токенів перед inference |
      | 37 | `resolveUsageAuth` | Користувацький розбір облікових даних usage |
      | 38 | `fetchUsageSnapshot` | Користувацька кінцева точка usage |
      | 39 | `createEmbeddingProvider` | Адаптер embedding, що належить постачальнику, для memory/search |
      | 40 | `buildReplayPolicy` | Користувацька політика replay/compaction транскрипту |
      | 41 | `sanitizeReplayHistory` | Перезаписування replay, специфічні для постачальника, після загального очищення |
      | 42 | `validateReplayTurns` | Сувора валідація replay-turn перед вбудованим runner-ом |
      | 43 | `onModelSelected` | Зворотний виклик після вибору моделі (наприклад, telemetry) |

      Примітка щодо налаштування prompt-ів:

      - `resolveSystemPromptContribution` дозволяє постачальнику інжектувати
        cache-aware підказки системного prompt-а для сімейства моделей. Віддавайте йому перевагу перед
        `before_prompt_build`, коли поведінка належить одному сімейству постачальника/моделі
        і має зберігати стабільний/динамічний поділ кешу.

      Детальні описи та приклади з реального світу дивіться у
      [Internals: Provider Runtime Hooks](/uk/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="Додайте додаткові можливості (необов’язково)">
    <a id="step-5-add-extra-capabilities"></a>
    Плагін постачальника може реєструвати speech, realtime transcription, realtime
    voice, media understanding, image generation, video generation, web fetch
    і web search разом із текстовим inference:

    ```typescript
    register(api) {
      api.registerProvider({ id: "acme-ai", /* ... */ });

      api.registerSpeechProvider({
        id: "acme-ai",
        label: "Acme Speech",
        isConfigured: ({ config }) => Boolean(config.messages?.tts),
        synthesize: async (req) => ({
          audioBuffer: Buffer.from(/* PCM data */),
          outputFormat: "mp3",
          fileExtension: ".mp3",
          voiceCompatible: false,
        }),
      });

      api.registerRealtimeTranscriptionProvider({
        id: "acme-ai",
        label: "Acme Realtime Transcription",
        isConfigured: () => true,
        createSession: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerRealtimeVoiceProvider({
        id: "acme-ai",
        label: "Acme Realtime Voice",
        isConfigured: ({ providerConfig }) => Boolean(providerConfig.apiKey),
        createBridge: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          setMediaTimestamp: () => {},
          submitToolResult: () => {},
          acknowledgeMark: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerMediaUnderstandingProvider({
        id: "acme-ai",
        capabilities: ["image", "audio"],
        describeImage: async (req) => ({ text: "A photo of..." }),
        transcribeAudio: async (req) => ({ text: "Transcript..." }),
      });

      api.registerImageGenerationProvider({
        id: "acme-ai",
        label: "Acme Images",
        generate: async (req) => ({ /* image result */ }),
      });

      api.registerVideoGenerationProvider({
        id: "acme-ai",
        label: "Acme Video",
        capabilities: {
          generate: {
            maxVideos: 1,
            maxDurationSeconds: 10,
            supportsResolution: true,
          },
          imageToVideo: {
            enabled: true,
            maxVideos: 1,
            maxInputImages: 1,
            maxDurationSeconds: 5,
          },
          videoToVideo: {
            enabled: false,
          },
        },
        generateVideo: async (req) => ({ videos: [] }),
      });

      api.registerWebFetchProvider({
        id: "acme-ai-fetch",
        label: "Acme Fetch",
        hint: "Fetch pages through Acme's rendering backend.",
        envVars: ["ACME_FETCH_API_KEY"],
        placeholder: "acme-...",
        signupUrl: "https://acme.example.com/fetch",
        credentialPath: "plugins.entries.acme.config.webFetch.apiKey",
        getCredentialValue: (fetchConfig) => fetchConfig?.acme?.apiKey,
        setCredentialValue: (fetchConfigTarget, value) => {
          const acme = (fetchConfigTarget.acme ??= {});
          acme.apiKey = value;
        },
        createTool: () => ({
          description: "Fetch a page through Acme Fetch.",
          parameters: {},
          execute: async (args) => ({ content: [] }),
        }),
      });

      api.registerWebSearchProvider({
        id: "acme-ai-search",
        label: "Acme Search",
        search: async (req) => ({ content: [] }),
      });
    }
    ```

    OpenClaw класифікує це як плагін **hybrid-capability**. Це
    рекомендований шаблон для корпоративних плагінів (один плагін на вендора). Див.
    [Internals: Capability Ownership](/uk/plugins/architecture#capability-ownership-model).

    Для генерації відео віддавайте перевагу показаній вище структурі можливостей, що враховує режими:
    `generate`, `imageToVideo` і `videoToVideo`. Старіші пласкі поля, такі
    як `maxInputImages`, `maxInputVideos` і `maxDurationSeconds`, усе ще працюють
    як агреговані резервні обмеження, але вони не можуть так само чисто описувати
    обмеження для окремих режимів або вимкнені режими трансформації.

  </Step>

  <Step title="Тестування">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Export your provider config object from index.ts or a dedicated file
    import { acmeProvider } from "./provider.js";

    describe("acme-ai provider", () => {
      it("resolves dynamic models", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("returns catalog when key is available", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("returns null catalog when no key", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## Публікація в ClawHub

Плагіни постачальників публікуються так само, як і будь-які інші зовнішні кодові плагіни:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

Не використовуйте тут застарілий псевдонім публікації лише для Skills; пакети плагінів повинні використовувати
`clawhub package publish`.

## Структура файлів

```
<bundled-plugin-root>/acme-ai/
├── package.json              # openclaw.providers metadata
├── openclaw.plugin.json      # Manifest with providerAuthEnvVars
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Tests
    └── usage.ts              # Usage endpoint (optional)
```

## Довідка щодо порядку каталогу

`catalog.order` визначає, коли ваш каталог зливається відносно вбудованих
постачальників:

| Order     | Коли          | Випадок використання                           |
| --------- | ------------- | ---------------------------------------------- |
| `simple`  | Перший прохід | Звичайні постачальники з API-ключем            |
| `profile` | Після simple  | Постачальники, прив’язані до профілів автентифікації |
| `paired`  | Після profile | Синтез кількох пов’язаних записів              |
| `late`    | Останній прохід | Перевизначення наявних постачальників (перемагає при конфлікті) |

## Подальші кроки

- [Channel Plugins](/uk/plugins/sdk-channel-plugins) — якщо ваш плагін також надає канал
- [SDK Runtime](/uk/plugins/sdk-runtime) — хелпери `api.runtime` (TTS, search, subagent)
- [SDK Overview](/uk/plugins/sdk-overview) — повний довідник з імпорту subpath
- [Plugin Internals](/uk/plugins/architecture#provider-runtime-hooks) — деталі хуків і вбудовані приклади
