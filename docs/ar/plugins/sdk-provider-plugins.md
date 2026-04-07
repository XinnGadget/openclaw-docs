---
read_when:
    - أنت تبني إضافة مزوّد نماذج جديدة
    - تريد إضافة وكيل متوافق مع OpenAI أو LLM مخصص إلى OpenClaw
    - تحتاج إلى فهم مصادقة المزوّد، والفهارس، وخطافات وقت التشغيل
sidebarTitle: Provider Plugins
summary: دليل خطوة بخطوة لبناء إضافة مزوّد نماذج لـ OpenClaw
title: بناء إضافات المزوّدين
x-i18n:
    generated_at: "2026-04-07T07:21:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4da82a353e1bf4fe6dc09e14b8614133ac96565679627de51415926014bd3990
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# بناء إضافات المزوّدين

يرشدك هذا الدليل خلال بناء إضافة مزوّد تضيف مزوّد نماذج
(LLM) إلى OpenClaw. وبحلول النهاية سيكون لديك مزوّد يتضمن فهرس نماذج،
ومصادقة بمفتاح API، وحلًا ديناميكيًا للنماذج.

<Info>
  إذا لم تكن قد بنيت أي إضافة OpenClaw من قبل، فاقرأ
  [البدء](/ar/plugins/building-plugins) أولًا للاطلاع على بنية الحزمة الأساسية
  وإعداد البيان.
</Info>

## الشرح العملي

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="الحزمة والبيان">
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
      "description": "مزوّد نماذج Acme AI",
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
          "choiceLabel": "مفتاح API لـ Acme AI",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "مفتاح API لـ Acme AI"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    يصرّح البيان بـ `providerAuthEnvVars` حتى يتمكن OpenClaw من اكتشاف
    بيانات الاعتماد من دون تحميل وقت تشغيل الإضافة. ويعد `modelSupport` اختياريًا
    ويسمح لـ OpenClaw بتحميل إضافة المزوّد الخاصة بك تلقائيًا من معرّفات نماذج مختصرة
    مثل `acme-large` قبل وجود خطافات وقت التشغيل. وإذا كنت تنشر
    المزوّد على ClawHub، فإن حقلي `openclaw.compat` و `openclaw.build`
    مطلوبان في `package.json`.

  </Step>

  <Step title="تسجيل المزوّد">
    يحتاج المزوّد الأدنى إلى `id` و `label` و `auth` و `catalog`:

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

    هذا مزوّد يعمل بالفعل. يمكن للمستخدمين الآن تنفيذ
    `openclaw onboard --acme-ai-api-key <key>` ثم اختيار
    `acme-ai/acme-large` كنموذج لهم.

    بالنسبة إلى المزوّدين المضمّنين الذين يسجلون مزوّد نص واحد فقط مع
    مصادقة مفتاح API بالإضافة إلى وقت تشغيل واحد مدعوم بالفهرس، ففضّل
    المساعد الأضيق `defineSingleProviderPluginEntry(...)`:

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

    إذا كان تدفق المصادقة لديك يحتاج أيضًا إلى تعديل `models.providers.*`،
    والأسماء المستعارة، والنموذج الافتراضي للوكيل أثناء التهيئة، فاستخدم
    مساعدات القوالب الجاهزة من
    `openclaw/plugin-sdk/provider-onboard`. أضيق المساعدات هي
    `createDefaultModelPresetAppliers(...)`,
    و`createDefaultModelsPresetAppliers(...)`, و
    `createModelCatalogPresetAppliers(...)`.

    عندما تدعم نقطة النهاية الأصلية للمزوّد كتل الاستخدام المتدفقة على
    النقل العادي `openai-completions`، ففضّل مساعدات الفهرس المشتركة في
    `openclaw/plugin-sdk/provider-catalog-shared` بدلًا من ترميز
    فحوصات معرّف المزوّد بشكل ثابت. تقوم
    `supportsNativeStreamingUsageCompat(...)` و
    `applyProviderNativeStreamingUsageCompat(...)` باكتشاف الدعم من خريطة قدرات
    نقطة النهاية، بحيث تظل نقاط نهاية أصلية على نمط Moonshot/DashScope
    منضمة حتى عندما تستخدم الإضافة معرّف مزوّد مخصصًا.

  </Step>

  <Step title="إضافة حل ديناميكي للنماذج">
    إذا كان مزوّدك يقبل معرّفات نماذج عشوائية (مثل وكيل أو موجّه)،
    فأضف `resolveDynamicModel`:

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

    إذا كان الحل يتطلب استدعاء شبكة، فاستخدم `prepareDynamicModel` من أجل
    الإحماء غير المتزامن — حيث يُشغَّل `resolveDynamicModel` مرة أخرى بعد اكتماله.

  </Step>

  <Step title="إضافة خطافات وقت التشغيل (عند الحاجة)">
    تحتاج معظم المزوّدات فقط إلى `catalog` و `resolveDynamicModel`. أضف
    الخطافات تدريجيًا حسب ما يتطلبه مزوّدك.

    تغطي بانيات المساعدات المشتركة الآن أكثر عائلات توافق
    إعادة التشغيل/الأدوات شيوعًا، لذلك لا تحتاج الإضافات عادةً إلى توصيل كل خطاف يدويًا
    واحدًا تلو الآخر:

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

    عائلات إعادة التشغيل المتاحة اليوم:

    | العائلة | ما الذي تقوم بتوصيله |
    | --- | --- |
    | `openai-compatible` | سياسة إعادة تشغيل مشتركة على نمط OpenAI للنواقل المتوافقة مع OpenAI، بما في ذلك تنظيف `tool-call-id`، وإصلاحات ترتيب assistant-first، والتحقق العام من أدوار Gemini عندما يحتاج النقل إلى ذلك |
    | `anthropic-by-model` | سياسة إعادة تشغيل مدركة لـ Claude تُختار بواسطة `modelId`، بحيث لا تحصل نواقل رسائل Anthropic على تنظيف كتل التفكير الخاصة بـ Claude إلا عندما يكون النموذج المحلول هو بالفعل معرّف Claude |
    | `google-gemini` | سياسة إعادة تشغيل Gemini الأصلية بالإضافة إلى تنظيف إعادة التشغيل عند التمهيد ووضع مخرجات التفكير الموسومة |
    | `passthrough-gemini` | تنظيف توقيع أفكار Gemini للنماذج التي تعمل عبر نواقل وكيلة متوافقة مع OpenAI؛ ولا يفعّل التحقق الأصلي من إعادة تشغيل Gemini أو إعادة كتابة التمهيد |
    | `hybrid-anthropic-openai` | سياسة هجينة للمزوّدين الذين يخلطون بين أسطح نماذج رسائل Anthropic والأسطح المتوافقة مع OpenAI في إضافة واحدة؛ ويظل إسقاط كتل التفكير الخاصة بـ Claude فقط اختياريًا ومحصورًا بجانب Anthropic |

    أمثلة مضمّنة حقيقية:

    - `google` و `google-gemini-cli`: ‏`google-gemini`
    - `openrouter` و `kilocode` و `opencode` و `opencode-go`: ‏`passthrough-gemini`
    - `amazon-bedrock` و `anthropic-vertex`: ‏`anthropic-by-model`
    - `minimax`: ‏`hybrid-anthropic-openai`
    - `moonshot` و `ollama` و `xai` و `zai`: ‏`openai-compatible`

    عائلات البث المتاحة اليوم:

    | العائلة | ما الذي تقوم بتوصيله |
    | --- | --- |
    | `google-thinking` | تطبيع حمولة التفكير في Gemini على مسار البث المشترك |
    | `kilocode-thinking` | غلاف التفكير في Kilo على مسار البث الوكيل المشترك، مع تجاوز التفكير المحقون لمعرّفات `kilo/auto` ومعرّفات التفكير الوكيل غير المدعومة |
    | `moonshot-thinking` | ربط حمولة التفكير الأصلي الثنائي في Moonshot من الإعدادات + مستوى `/think` |
    | `minimax-fast-mode` | إعادة كتابة نموذج الوضع السريع في MiniMax على مسار البث المشترك |
    | `openai-responses-defaults` | أغلفة Responses الأصلية المشتركة لـ OpenAI/Codex: روؤس الإسناد، و`/fast`/`serviceTier`، وإسهاب النص، والبحث الأصلي على الويب في Codex، وتشكيل الحمولة المتوافق مع التفكير، وإدارة سياق Responses |
    | `openrouter-thinking` | غلاف التفكير في OpenRouter للمسارات الوكيلة، مع معالجة تجاوزات `auto`/النماذج غير المدعومة مركزيًا |
    | `tool-stream-default-on` | غلاف `tool_stream` المفعّل افتراضيًا لمزوّدين مثل Z.AI الذين يريدون بث الأدوات ما لم يُعطّل صراحةً |

    أمثلة مضمّنة حقيقية:

    - `google` و `google-gemini-cli`: ‏`google-thinking`
    - `kilocode`: ‏`kilocode-thinking`
    - `moonshot`: ‏`moonshot-thinking`
    - `minimax` و `minimax-portal`: ‏`minimax-fast-mode`
    - `openai` و `openai-codex`: ‏`openai-responses-defaults`
    - `openrouter`: ‏`openrouter-thinking`
    - `zai`: ‏`tool-stream-default-on`

    يصدّر `openclaw/plugin-sdk/provider-model-shared` أيضًا تعداد
    عائلات إعادة التشغيل بالإضافة إلى المساعدات المشتركة التي تُبنى منها تلك العائلات. ومن
    التصديرات العامة الشائعة:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - بانيات إعادة التشغيل المشتركة مثل `buildOpenAICompatibleReplayPolicy(...)`,
      و`buildAnthropicReplayPolicyForModel(...)`,
      و`buildGoogleGeminiReplayPolicy(...)`, و
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - مساعدات إعادة تشغيل Gemini مثل `sanitizeGoogleGeminiReplayHistory(...)`
      و `resolveTaggedReasoningOutputMode()`
    - مساعدات نقطة النهاية/النموذج مثل `resolveProviderEndpoint(...)`,
      و`normalizeProviderId(...)`, و`normalizeGooglePreviewModelId(...)`, و
      `normalizeNativeXaiModelId(...)`

    يوفّر `openclaw/plugin-sdk/provider-stream` كلاً من باني العائلة
    ومساعدات الأغلفة العامة التي تعيد تلك العائلات استخدامها. ومن
    التصديرات العامة الشائعة:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - أغلفة OpenAI/Codex المشتركة مثل
      `createOpenAIAttributionHeadersWrapper(...)`,
      و`createOpenAIFastModeWrapper(...)`,
      و`createOpenAIServiceTierWrapper(...)`,
      و`createOpenAIResponsesContextManagementWrapper(...)`, و
      `createCodexNativeWebSearchWrapper(...)`
    - أغلفة الوكلاء/المزوّدين المشتركة مثل `createOpenRouterWrapper(...)`,
      و`createToolStreamWrapper(...)`, و`createMinimaxFastModeWrapper(...)`

    تبقى بعض مساعدات البث محلية للمزوّد عمدًا. مثال مضمّن حالي:
    يصدّر `@openclaw/anthropic-provider`
    `wrapAnthropicProviderStream`, و `resolveAnthropicBetas`,
    و `resolveAnthropicFastMode`, و `resolveAnthropicServiceTier`, و
    بانيات الأغلفة الأدنى الخاصة بـ Anthropic من خلال المسار العام `api.ts` /
    `contract-api.ts`. وتبقى هذه المساعدات خاصة بـ Anthropic
    لأنها تشفّر أيضًا التعامل مع Claude OAuth beta وتقييد `context1m`.

    كما تحتفظ مزوّدات مضمّنة أخرى أيضًا بأغلفة محلية خاصة بالنقل عندما
    لا يمكن مشاركة السلوك بوضوح عبر العائلات. مثال حالي: تحتفظ إضافة xAI
    المضمّنة بتشكيل xAI Responses الأصلي داخل
    `wrapStreamFn` الخاص بها، بما في ذلك إعادة كتابة الأسماء المستعارة `/fast`،
    و`tool_stream` الافتراضي، وتنظيف الأدوات الصارمة غير المدعومة، وإزالة
    حمولة التفكير الخاصة بـ xAI.

    يكشف `openclaw/plugin-sdk/provider-tools` حاليًا عائلة مشتركة واحدة
    لمخطط الأدوات بالإضافة إلى مساعدات مشتركة للمخطط/التوافق:

    - يوثّق `ProviderToolCompatFamily` مخزون العائلات المشتركة الحالية.
    - يقوم `buildProviderToolCompatFamilyHooks("gemini")` بتوصيل تنظيف
      مخطط Gemini + التشخيصات للمزوّدين الذين يحتاجون إلى مخططات أدوات آمنة مع Gemini.
    - `normalizeGeminiToolSchemas(...)` و `inspectGeminiToolSchemas(...)`
      هما مساعدا مخطط Gemini العامان الأساسيان.
    - يعيد `resolveXaiModelCompatPatch()` تصحيح توافق xAI المضمّن:
      `toolSchemaProfile: "xai"`، والكلمات المفتاحية غير المدعومة في المخطط، ودعم
      `web_search` الأصلي، وفك ترميز وسائط استدعاء الأدوات المشفّرة بكيانات HTML.
    - يطبّق `applyXaiModelCompat(model)` تصحيح توافق xAI نفسه على
      نموذج محلول قبل أن يصل إلى المشغّل.

    مثال مضمّن حقيقي: تستخدم إضافة xAI كلاً من `normalizeResolvedModel` و
    `contributeResolvedModelCompat` للحفاظ على ملكية بيانات هذا التوافق
    داخل المزوّد بدلًا من ترميز قواعد xAI بشكل ثابت في الأساس.

    يدعم النمط نفسه القائم على جذر الحزمة أيضًا مزوّدات مضمّنة أخرى:

    - `@openclaw/openai-provider`: يصدّر `api.ts` بانيات المزوّد،
      ومساعدات النموذج الافتراضي، وبانيات المزوّد الفوري
    - `@openclaw/openrouter-provider`: يصدّر `api.ts` باني المزوّد
      بالإضافة إلى مساعدات التهيئة/الإعداد

    <Tabs>
      <Tab title="تبادل الرموز">
        بالنسبة إلى المزوّدين الذين يحتاجون إلى تبادل رمز قبل كل استدعاء استدلال:

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
      <Tab title="روؤس مخصصة">
        بالنسبة إلى المزوّدين الذين يحتاجون إلى روؤس طلبات مخصصة أو تعديلات على جسم الطلب:

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
      <Tab title="هوية النقل الأصلية">
        بالنسبة إلى المزوّدين الذين يحتاجون إلى روؤس أو بيانات تعريفية أصلية للطلبات/الجلسات على
        نواقل HTTP أو WebSocket العامة:

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
      <Tab title="الاستخدام والفوترة">
        بالنسبة إلى المزوّدين الذين يوفّرون بيانات الاستخدام/الفوترة:

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

    <Accordion title="جميع خطافات المزوّد المتاحة">
      يستدعي OpenClaw الخطافات بهذا الترتيب. تستخدم معظم المزوّدات 2-3 فقط:

      | # | الخطاف | متى يُستخدم |
      | --- | --- | --- |
      | 1 | `catalog` | فهرس النماذج أو القيم الافتراضية لعنوان URL الأساسي |
      | 2 | `applyConfigDefaults` | قيم افتراضية عامة مملوكة للمزوّد أثناء إنشاء الإعدادات |
      | 3 | `normalizeModelId` | تنظيف الأسماء المستعارة القديمة/المعاينة لمعرّف النموذج قبل البحث |
      | 4 | `normalizeTransport` | تنظيف `api` / `baseUrl` لعائلة المزوّد قبل التجميع العام للنموذج |
      | 5 | `normalizeConfig` | تطبيع إعدادات `models.providers.<id>` |
      | 6 | `applyNativeStreamingUsageCompat` | إعادة كتابة توافق استخدام البث الأصلي لمزوّدي الإعدادات |
      | 7 | `resolveConfigApiKey` | حل مصادقة علامات البيئة المملوك للمزوّد |
      | 8 | `resolveSyntheticAuth` | مصادقة تركيبية محلية/مستضافة ذاتيًا أو مدعومة بالإعدادات |
      | 9 | `shouldDeferSyntheticProfileAuth` | خفض أولوية العناصر النائبة المحفوظة للملفات التعريفية التركيبية خلف مصادقة البيئة/الإعدادات |
      | 10 | `resolveDynamicModel` | قبول معرّفات نماذج upstream عشوائية |
      | 11 | `prepareDynamicModel` | جلب بيانات تعريفية غير متزامن قبل الحل |
      | 12 | `normalizeResolvedModel` | إعادة كتابة النقل قبل المشغّل |

    ملاحظات التراجع في وقت التشغيل:

    - يتحقق `normalizeConfig` أولًا من المزوّد المطابق، ثم من إضافات
      المزوّد الأخرى القادرة على الخطافات حتى تغيّر إحداها الإعدادات فعلًا.
      وإذا لم يُعد أي خطاف مزوّد كتابة إدخال إعدادات مدعوم من Google-family،
      فسيظل مطبّع إعدادات Google المضمّن مطبقًا.
    - يستخدم `resolveConfigApiKey` خطاف المزوّد عند توفره. كما أن
      المسار المضمّن `amazon-bedrock` يحتوي هنا أيضًا على محلّل
      مضمّن لعلامات بيئة AWS، على الرغم من أن مصادقة وقت تشغيل Bedrock نفسها ما تزال تستخدم
      سلسلة AWS SDK الافتراضية.
      | 13 | `contributeResolvedModelCompat` | أعلام توافق لنماذج المورّد خلف نقل متوافق آخر |
      | 14 | `capabilities` | حقيبة قدرات ثابتة قديمة؛ للتوافق فقط |
      | 15 | `normalizeToolSchemas` | تنظيف مخطط الأدوات المملوك للمزوّد قبل التسجيل |
      | 16 | `inspectToolSchemas` | تشخيصات مخطط الأدوات المملوكة للمزوّد |
      | 17 | `resolveReasoningOutputMode` | عقد مخرجات التفكير الموسومة مقابل الأصلية |
      | 18 | `prepareExtraParams` | معلمات الطلب الافتراضية |
      | 19 | `createStreamFn` | نقل StreamFn مخصص بالكامل |
      | 20 | `wrapStreamFn` | أغلفة مخصصة للروؤس/الجسم على مسار البث العادي |
      | 21 | `resolveTransportTurnState` | روؤس/بيانات تعريفية أصلية لكل دور |
      | 22 | `resolveWebSocketSessionPolicy` | روؤس جلسة WS أصلية/فترة تهدئة |
      | 23 | `formatApiKey` | شكل رمز وقت تشغيل مخصص |
      | 24 | `refreshOAuth` | تحديث OAuth مخصص |
      | 25 | `buildAuthDoctorHint` | إرشادات إصلاح المصادقة |
      | 26 | `matchesContextOverflowError` | اكتشاف التجاوز المملوك للمزوّد |
      | 27 | `classifyFailoverReason` | تصنيف حد المعدل/زيادة الحمل المملوك للمزوّد |
      | 28 | `isCacheTtlEligible` | تقييد TTL للتخزين المؤقت للمطالبات |
      | 29 | `buildMissingAuthMessage` | تلميح مخصص للمصادقة المفقودة |
      | 30 | `suppressBuiltInModel` | إخفاء صفوف upstream القديمة |
      | 31 | `augmentModelCatalog` | صفوف تركيبية للتوافق المستقبلي |
      | 32 | `isBinaryThinking` | تشغيل/إيقاف التفكير الثنائي |
      | 33 | `supportsXHighThinking` | دعم التفكير `xhigh` |
      | 34 | `resolveDefaultThinkingLevel` | سياسة `/think` الافتراضية |
      | 35 | `isModernModelRef` | مطابقة النماذج المباشرة/الاختبارية |
      | 36 | `prepareRuntimeAuth` | تبادل الرموز قبل الاستدلال |
      | 37 | `resolveUsageAuth` | تحليل بيانات اعتماد الاستخدام المخصص |
      | 38 | `fetchUsageSnapshot` | نقطة نهاية استخدام مخصصة |
      | 39 | `createEmbeddingProvider` | مهايئ تضمين مملوك للمزوّد للذاكرة/البحث |
      | 40 | `buildReplayPolicy` | سياسة مخصصة لإعادة تشغيل/ضغط النص |
      | 41 | `sanitizeReplayHistory` | إعادة كتابة إعادة التشغيل الخاصة بالمزوّد بعد التنظيف العام |
      | 42 | `validateReplayTurns` | تحقق صارم من أدوار إعادة التشغيل قبل المشغّل المضمّن |
      | 43 | `onModelSelected` | استدعاء لاحق للاختيار (مثل القياس عن بُعد) |

      ملاحظة ضبط المطالبات:

      - يتيح `resolveSystemPromptContribution` للمزوّد حقن
        إرشادات مطالبة نظام مدركة للتخزين المؤقت لعائلة نموذج. فضّل استخدامه بدلًا من
        `before_prompt_build` عندما ينتمي السلوك إلى عائلة مزوّد/نموذج واحدة
        ويجب أن يحافظ على الفصل المستقر/الديناميكي للتخزين المؤقت.

      للحصول على أوصاف مفصلة وأمثلة من الواقع، راجع
      [الداخليات: خطافات وقت تشغيل المزوّد](/ar/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="إضافة قدرات إضافية (اختياري)">
    <a id="step-5-add-extra-capabilities"></a>
    يمكن لإضافة المزوّد تسجيل مزوّدات الكلام، والنسخ الفوري، والصوت
    الفوري، وفهم الوسائط، وتوليد الصور، وتوليد الفيديو، وجلب الويب،
    والبحث في الويب إلى جانب الاستدلال النصي:

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
        hint: "جلب الصفحات عبر الواجهة الخلفية للعرض الخاصة بـ Acme.",
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
          description: "جلب صفحة عبر Acme Fetch.",
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

    يصنف OpenClaw هذا على أنه إضافة **hybrid-capability**. وهذا هو
    النمط الموصى به لإضافات الشركات (إضافة واحدة لكل مورّد). راجع
    [الداخليات: ملكية القدرات](/ar/plugins/architecture#capability-ownership-model).

    بالنسبة إلى توليد الفيديو، ففضّل شكل القدرات المراعي للأوضاع الموضح أعلاه:
    `generate` و `imageToVideo` و `videoToVideo`. أما الحقول التجميعية المسطحة مثل
    `maxInputImages` و `maxInputVideos` و `maxDurationSeconds` فليست
    كافية للإعلان بوضوح عن دعم أوضاع التحويل أو الأوضاع المعطلة.

    ينبغي أن تتبع مزوّدات توليد الموسيقى النمط نفسه:
    `generate` للتوليد المعتمد على المطالبة فقط و `edit` للتوليد القائم على
    صورة مرجعية. أما الحقول التجميعية المسطحة مثل `maxInputImages`,
    و`supportsLyrics`, و`supportsFormat` فليست كافية للإعلان عن
    دعم التحرير؛ إذ إن كتل `generate` / `edit` الصريحة هي العقد المتوقع.

  </Step>

  <Step title="الاختبار">
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

## النشر إلى ClawHub

تُنشر إضافات مزوّدي النماذج بالطريقة نفسها التي تُنشر بها أي إضافة كود خارجية أخرى:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

لا تستخدم الاسم المستعار القديم الخاص بالنشر عبر Skills هنا؛ إذ يجب أن تستخدم
حزم الإضافات `clawhub package publish`.

## بنية الملفات

```
<bundled-plugin-root>/acme-ai/
├── package.json              # بيانات تعريف openclaw.providers
├── openclaw.plugin.json      # البيان مع providerAuthEnvVars
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # الاختبارات
    └── usage.ts              # نقطة نهاية الاستخدام (اختياري)
```

## مرجع ترتيب الفهرس

يتحكم `catalog.order` في وقت دمج الفهرس الخاص بك بالنسبة إلى
المزوّدين المضمّنين:

| الترتيب   | التوقيت         | حالة الاستخدام                                  |
| --------- | --------------- | ----------------------------------------------- |
| `simple`  | التمرير الأول   | مزوّدو مفاتيح API البسيطون                      |
| `profile` | بعد `simple`    | المزوّدون المقيدون بملفات تعريف المصادقة        |
| `paired`  | بعد `profile`   | إنشاء إدخالات متعددة مترابطة                    |
| `late`    | التمرير الأخير  | تجاوز المزوّدين الموجودين (يفوز عند التعارض)    |

## الخطوات التالية

- [إضافات القنوات](/ar/plugins/sdk-channel-plugins) — إذا كانت إضافتك توفّر قناة أيضًا
- [وقت تشغيل SDK](/ar/plugins/sdk-runtime) — مساعدات `api.runtime` ‏(TTS والبحث والوكيل الفرعي)
- [نظرة عامة على SDK](/ar/plugins/sdk-overview) — مرجع الاستيراد الكامل للمسارات الفرعية
- [داخليات الإضافة](/ar/plugins/architecture#provider-runtime-hooks) — تفاصيل الخطافات والأمثلة المضمّنة
