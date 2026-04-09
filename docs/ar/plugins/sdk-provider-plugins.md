---
read_when:
    - أنت تبني plugin جديدًا لموفّر نماذج
    - تريد إضافة proxy متوافق مع OpenAI أو LLM مخصص إلى OpenClaw
    - تحتاج إلى فهم مصادقة الموفّر، والفهارس، وhooks وقت التشغيل
sidebarTitle: Provider Plugins
summary: دليل خطوة بخطوة لبناء plugin لموفّر نماذج في OpenClaw
title: بناء إضافات الموفّرين
x-i18n:
    generated_at: "2026-04-09T01:30:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 38d9af522dc19e49c81203a83a4096f01c2398b1df771c848a30ad98f251e9e1
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# بناء إضافات الموفّرين

يرشدك هذا الدليل خلال بناء plugin لموفّر يضيف موفّر نماذج
(LLM) إلى OpenClaw. وبحلول النهاية سيكون لديك موفّر مع فهرس نماذج،
ومصادقة بمفتاح API، وتحليل ديناميكي للنماذج.

<Info>
  إذا لم تكن قد بنيت أي plugin لـ OpenClaw من قبل، فاقرأ
  [البدء](/ar/plugins/building-plugins) أولًا للتعرّف إلى بنية
  الحزمة الأساسية وإعداد البيان.
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
      "description": "Acme AI model provider",
      "providers": ["acme-ai"],
      "modelSupport": {
        "modelPrefixes": ["acme-"]
      },
      "providerAuthEnvVars": {
        "acme-ai": ["ACME_AI_API_KEY"]
      },
      "providerAuthAliases": {
        "acme-ai-coding": "acme-ai"
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

    يعلن البيان `providerAuthEnvVars` بحيث يتمكن OpenClaw من اكتشاف
    بيانات الاعتماد من دون تحميل وقت تشغيل plugin الخاص بك. أضف `providerAuthAliases`
    عندما يجب أن يعيد متغير من الموفّر استخدام مصادقة معرّف موفّر آخر. ويُعد `modelSupport`
    اختياريًا ويتيح لـ OpenClaw تحميل plugin الموفّر تلقائيًا من
    معرّفات النماذج المختصرة مثل `acme-large` قبل وجود hooks وقت التشغيل. وإذا نشرت
    الموفّر على ClawHub، فإن حقول `openclaw.compat` و`openclaw.build`
    هذه تكون مطلوبة في `package.json`.

  </Step>

  <Step title="تسجيل الموفّر">
    يحتاج الحد الأدنى من الموفّر إلى `id` و`label` و`auth` و`catalog`:

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

    هذا موفّر عامل. يمكن للمستخدمين الآن تنفيذ
    `openclaw onboard --acme-ai-api-key <key>` واختيار
    `acme-ai/acme-large` كنموذج لهم.

    بالنسبة إلى الموفّرين المجمّعين الذين يسجّلون موفّر نص واحدًا فقط مع
    مصادقة بمفتاح API بالإضافة إلى وقت تشغيل واحد مدعوم بالفهرس، ففضّل
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

    إذا كان تدفق المصادقة لديك يحتاج أيضًا إلى تعديل `models.providers.*` والأسماء البديلة
    والنموذج الافتراضي للوكيل أثناء onboarding، فاستخدم المساعدات الجاهزة من
    `openclaw/plugin-sdk/provider-onboard`. وأضيق المساعدات هي
    `createDefaultModelPresetAppliers(...)`،
    و`createDefaultModelsPresetAppliers(...)`، و
    `createModelCatalogPresetAppliers(...)`.

    عندما تدعم نقطة النهاية الأصلية للموفّر كتل استخدام متدفقة على
    ناقل `openai-completions` العادي، ففضّل المساعدات المشتركة للفهرس في
    `openclaw/plugin-sdk/provider-catalog-shared` بدلًا من تضمين فحوصات
    معرّف الموفّر بشكل صريح. يكتشف
    `supportsNativeStreamingUsageCompat(...)` و
    `applyProviderNativeStreamingUsageCompat(...)` الدعم من خريطة قدرات
    نقطة النهاية، بحيث تظل نقاط النهاية الأصلية على نمط Moonshot/DashScope
    قادرة على التفعيل حتى عندما يستخدم plugin معرّف موفّر مخصصًا.

  </Step>

  <Step title="إضافة تحليل ديناميكي للنماذج">
    إذا كان موفّرك يقبل معرّفات نماذج عشوائية (مثل proxy أو router)،
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

    إذا كان التحليل يتطلب استدعاء شبكة، فاستخدم `prepareDynamicModel` من أجل
    التهيئة غير المتزامنة — إذ يعمل `resolveDynamicModel` مرة أخرى بعد اكتمالها.

  </Step>

  <Step title="إضافة hooks وقت التشغيل (عند الحاجة)">
    تحتاج معظم الموفّرات فقط إلى `catalog` + `resolveDynamicModel`. أضف hooks
    تدريجيًا بحسب ما يتطلبه موفّرك.

    تغطي أدوات البناء المساعدة المشتركة الآن أكثر عائلات
    إعادة التشغيل/توافق الأدوات شيوعًا، لذلك لا تحتاج plugins عادةً إلى توصيل
    كل hook يدويًا واحدًا تلو الآخر:

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

    | العائلة | ما الذي توصله |
    | --- | --- |
    | `openai-compatible` | سياسة إعادة تشغيل مشتركة بنمط OpenAI لوسائط النقل المتوافقة مع OpenAI، بما في ذلك تنظيف `tool-call-id`، وإصلاحات ترتيب assistant-first، والتحقق العام من أدوار Gemini عندما يحتاج ناقل النقل ذلك |
    | `anthropic-by-model` | سياسة إعادة تشغيل واعية بـ Claude يتم اختيارها بحسب `modelId`، بحيث لا تحصل وسائط نقل رسائل Anthropic على تنظيف كتل التفكير الخاصة بـ Claude إلا عندما يكون النموذج المحلول فعليًا معرّف Claude |
    | `google-gemini` | سياسة إعادة تشغيل Gemini الأصلية بالإضافة إلى تنظيف إعادة تشغيل التمهيد ووضع إخراج الاستدلال الموسوم |
    | `passthrough-gemini` | تنظيف توقيع التفكير في Gemini للنماذج التي تعمل عبر نواقل proxy المتوافقة مع OpenAI؛ ولا يفعّل التحقق الأصلي من إعادة تشغيل Gemini أو إعادة كتابة التمهيد |
    | `hybrid-anthropic-openai` | سياسة هجينة للموفّرين الذين يخلطون بين أسطح نماذج رسائل Anthropic والأسطح المتوافقة مع OpenAI داخل plugin واحد؛ ويظل إسقاط كتل التفكير الخاصة بـ Claude والمشروط اختياريًا محصورًا في جانب Anthropic |

    أمثلة فعلية من الموفّرين المجمّعين:

    - `google` و`google-gemini-cli`: ‏`google-gemini`
    - `openrouter` و`kilocode` و`opencode` و`opencode-go`: ‏`passthrough-gemini`
    - `amazon-bedrock` و`anthropic-vertex`: ‏`anthropic-by-model`
    - `minimax`: ‏`hybrid-anthropic-openai`
    - `moonshot` و`ollama` و`xai` و`zai`: ‏`openai-compatible`

    عائلات البث المتاحة اليوم:

    | العائلة | ما الذي توصله |
    | --- | --- |
    | `google-thinking` | تطبيع حمولة التفكير في Gemini على مسار البث المشترك |
    | `kilocode-thinking` | غلاف استدلال Kilo على مسار بث proxy المشترك، مع تجاوز التفكير المحقون لـ `kilo/auto` ومعرّفات التفكير غير المدعومة |
    | `moonshot-thinking` | تعيين حمولة التفكير الأصلية الثنائية في Moonshot من الإعدادات + مستوى `/think` |
    | `minimax-fast-mode` | إعادة كتابة نموذج MiniMax في الوضع السريع على مسار البث المشترك |
    | `openai-responses-defaults` | أغلفة Responses الأصلية المشتركة لـ OpenAI/Codex: رؤوس الإسناد، و`/fast`/`serviceTier`، وإسهاب النص، والبحث الأصلي على الويب في Codex، وتشكيل حمولة توافق الاستدلال، وإدارة سياق Responses |
    | `openrouter-thinking` | غلاف استدلال OpenRouter لمسارات proxy، مع معالجة تجاوزات `auto`/النماذج غير المدعومة مركزيًا |
    | `tool-stream-default-on` | غلاف `tool_stream` مفعل افتراضيًا لموفّرين مثل Z.AI يريدون بث الأدوات ما لم يتم تعطيله صراحةً |

    أمثلة فعلية من الموفّرين المجمّعين:

    - `google` و`google-gemini-cli`: ‏`google-thinking`
    - `kilocode`: ‏`kilocode-thinking`
    - `moonshot`: ‏`moonshot-thinking`
    - `minimax` و`minimax-portal`: ‏`minimax-fast-mode`
    - `openai` و`openai-codex`: ‏`openai-responses-defaults`
    - `openrouter`: ‏`openrouter-thinking`
    - `zai`: ‏`tool-stream-default-on`

    يصدّر `openclaw/plugin-sdk/provider-model-shared` أيضًا تعداد
    عائلات إعادة التشغيل بالإضافة إلى المساعدات المشتركة التي تُبنى منها
    تلك العائلات. وتشمل التصديرات العامة الشائعة:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - أدوات بناء إعادة التشغيل المشتركة مثل `buildOpenAICompatibleReplayPolicy(...)`،
      و`buildAnthropicReplayPolicyForModel(...)`،
      و`buildGoogleGeminiReplayPolicy(...)`، و
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - مساعدات إعادة تشغيل Gemini مثل `sanitizeGoogleGeminiReplayHistory(...)`
      و`resolveTaggedReasoningOutputMode()`
    - مساعدات نقطة النهاية/النموذج مثل `resolveProviderEndpoint(...)`،
      و`normalizeProviderId(...)`، و`normalizeGooglePreviewModelId(...)`، و
      `normalizeNativeXaiModelId(...)`

    يكشف `openclaw/plugin-sdk/provider-stream` كلًا من باني العائلة
    ومساعدات الأغلفة العامة التي تعيد هذه العائلات استخدامها. وتشمل
    التصديرات العامة الشائعة:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - الأغلفة المشتركة لـ OpenAI/Codex مثل
      `createOpenAIAttributionHeadersWrapper(...)`،
      و`createOpenAIFastModeWrapper(...)`،
      و`createOpenAIServiceTierWrapper(...)`،
      و`createOpenAIResponsesContextManagementWrapper(...)`، و
      `createCodexNativeWebSearchWrapper(...)`
    - أغلفة proxy/الموفّرين المشتركة مثل `createOpenRouterWrapper(...)`،
      و`createToolStreamWrapper(...)`، و`createMinimaxFastModeWrapper(...)`

    تبقى بعض مساعدات البث محلية للموفّر عمدًا. مثال مجمّع
    حالي: يصدّر `@openclaw/anthropic-provider`
    `wrapAnthropicProviderStream` و`resolveAnthropicBetas`،
    و`resolveAnthropicFastMode`، و`resolveAnthropicServiceTier`، و
    أدوات بناء أغلفة Anthropic منخفضة المستوى من خلال
    نقطة الوصل العامة `api.ts` / `contract-api.ts`. وتبقى هذه المساعدات
    خاصة بـ Anthropic لأنها ترمّز أيضًا معالجة Claude OAuth beta
    وبوابة `context1m`.

    وتحتفظ موفّرات مجمّعة أخرى أيضًا بأغلفة خاصة بناقل النقل محليًا عندما
    لا يكون السلوك مشتركًا بشكل نظيف عبر العائلات. مثال حالي: يحتفظ
    plugin المجمّع xAI بتشكيل Responses الأصلية لـ xAI ضمن
    `wrapStreamFn` الخاص به، بما في ذلك إعادة كتابة الأسماء البديلة `/fast`،
    و`tool_stream` الافتراضي، وتنظيف strict-tool غير المدعوم، وإزالة
    حمولة الاستدلال الخاصة بـ xAI.

    يكشف `openclaw/plugin-sdk/provider-tools` حاليًا عائلة واحدة مشتركة
    لمخطط الأدوات بالإضافة إلى مساعدات المخطط/التوافق المشتركة:

    - يوثق `ProviderToolCompatFamily` مخزون العائلات المشتركة الحالية.
    - يقوم `buildProviderToolCompatFamilyHooks("gemini")` بتوصيل
      تنظيف مخطط Gemini + التشخيصات للمزوّدين الذين يحتاجون إلى
      مخططات أدوات آمنة لـ Gemini.
    - إن `normalizeGeminiToolSchemas(...)` و`inspectGeminiToolSchemas(...)`
      هما مساعدا مخطط Gemini العامان الأساسيان.
    - يعيد `resolveXaiModelCompatPatch()` تصحيح التوافق المجمّع الخاص بـ xAI:
      ‏`toolSchemaProfile: "xai"`، والكلمات المفتاحية غير المدعومة في المخطط،
      ودعم `web_search` الأصلي، وفك ترميز وسيطات استدعاء الأدوات
      بكيانات HTML.
    - يطبّق `applyXaiModelCompat(model)` تصحيح التوافق نفسه الخاص بـ xAI على
      نموذج محلول قبل أن يصل إلى المشغّل.

    مثال فعلي مجمّع: يستخدم plugin الخاص بـ xAI
    `normalizeResolvedModel` بالإضافة إلى `contributeResolvedModelCompat`
    للحفاظ على ملكية بيانات التوافق هذه داخل الموفّر بدلًا من
    ترميز قواعد xAI بشكل صريح داخل النواة.

    ويدعم النمط نفسه من جذر الحزمة أيضًا موفّرين مجمّعين آخرين:

    - `@openclaw/openai-provider`: يصدّر `api.ts` أدوات بناء الموفّر،
      ومساعدات النموذج الافتراضي، وأدوات بناء موفّر الوقت الحقيقي
    - `@openclaw/openrouter-provider`: يصدّر `api.ts` أداة بناء الموفّر
      بالإضافة إلى مساعدات onboarding/config

    <Tabs>
      <Tab title="تبادل الرمز">
        بالنسبة إلى الموفّرين الذين يحتاجون إلى تبادل رمز قبل كل استدعاء استدلال:

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
      <Tab title="رؤوس مخصصة">
        بالنسبة إلى الموفّرين الذين يحتاجون إلى رؤوس طلبات مخصصة أو تعديلات على جسم الطلب:

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
        بالنسبة إلى الموفّرين الذين يحتاجون إلى رؤوس أو بيانات تعريف أصلية للطلب/الجلسة على
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
        بالنسبة إلى الموفّرين الذين يكشفون عن بيانات الاستخدام/الفوترة:

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

    <Accordion title="جميع hooks الموفّر المتاحة">
      يستدعي OpenClaw الـ hooks بهذا الترتيب. تستخدم معظم الموفّرات 2-3 فقط:

      | # | Hook | متى يُستخدم |
      | --- | --- | --- |
      | 1 | `catalog` | فهرس النماذج أو افتراضيات `baseUrl` |
      | 2 | `applyConfigDefaults` | افتراضيات عامة يملكها الموفّر أثناء تجسيد الإعدادات |
      | 3 | `normalizeModelId` | تنظيف الأسماء البديلة القديمة/المعاينة لمعرّف النموذج قبل البحث |
      | 4 | `normalizeTransport` | تنظيف `api` / `baseUrl` الخاص بعائلة الموفّر قبل تجميع النموذج العام |
      | 5 | `normalizeConfig` | تطبيع إعدادات `models.providers.<id>` |
      | 6 | `applyNativeStreamingUsageCompat` | إعادة كتابة توافق الاستخدام الأصلي المتدفق لموفّري الإعدادات |
      | 7 | `resolveConfigApiKey` | تحليل مصادقة علامة البيئة التي يملكها الموفّر |
      | 8 | `resolveSyntheticAuth` | مصادقة تركيبية محلية/مستضافة ذاتيًا أو مدعومة بالإعدادات |
      | 9 | `shouldDeferSyntheticProfileAuth` | تأخير العناصر النائبة التخزينية التركيبية لملفات التعريف خلف مصادقة البيئة/الإعدادات |
      | 10 | `resolveDynamicModel` | قبول معرّفات النماذج العشوائية في المنبع |
      | 11 | `prepareDynamicModel` | جلب بيانات تعريف غير متزامن قبل التحليل |
      | 12 | `normalizeResolvedModel` | إعادة كتابة ناقل النقل قبل المشغّل |

    ملاحظات الاحتياط في وقت التشغيل:

    - يفحص `normalizeConfig` أولًا الموفّر المطابق، ثم
      بقية plugins القادرة على الـ hook حتى يغيّر أحدها الإعداد فعليًا.
      وإذا لم يُعد أي hook لموفّر كتابة إدخال إعدادات مدعومًا من عائلة Google،
      فسيظل مطبّع إعدادات Google المجمّع مطبقًا.
    - يستخدم `resolveConfigApiKey` hook الموفّر عند كشفه. كما أن
      المسار المجمّع `amazon-bedrock` يحتوي أيضًا هنا على محلل
      مدمج لعلامات بيئة AWS، على الرغم من أن مصادقة وقت تشغيل Bedrock نفسها
      لا تزال تستخدم السلسلة الافتراضية لـ AWS SDK.
      | 13 | `contributeResolvedModelCompat` | علامات توافق لنماذج مورّدين خلف ناقل متوافق آخر |
      | 14 | `capabilities` | حزمة قدرات ثابتة قديمة؛ للتوافق فقط |
      | 15 | `normalizeToolSchemas` | تنظيف مخطط الأدوات المملوك للموفّر قبل التسجيل |
      | 16 | `inspectToolSchemas` | تشخيصات مخطط الأدوات المملوك للموفّر |
      | 17 | `resolveReasoningOutputMode` | عقد إخراج الاستدلال الموسوم مقابل الأصلي |
      | 18 | `prepareExtraParams` | معلمات الطلب الافتراضية |
      | 19 | `createStreamFn` | ناقل `StreamFn` مخصص بالكامل |
      | 20 | `wrapStreamFn` | أغلفة رؤوس/جسم مخصصة على مسار البث العادي |
      | 21 | `resolveTransportTurnState` | رؤوس/بيانات تعريف أصلية لكل دور |
      | 22 | `resolveWebSocketSessionPolicy` | رؤوس جلسة WS أصلية/تهدئة |
      | 23 | `formatApiKey` | شكل رمز وقت تشغيل مخصص |
      | 24 | `refreshOAuth` | تحديث OAuth مخصص |
      | 25 | `buildAuthDoctorHint` | إرشادات إصلاح المصادقة |
      | 26 | `matchesContextOverflowError` | اكتشاف تجاوز السعة المملوك للموفّر |
      | 27 | `classifyFailoverReason` | تصنيف حدود المعدل/التحميل الزائد المملوك للموفّر |
      | 28 | `isCacheTtlEligible` | بوابة TTL لذاكرة التخزين المؤقت للموجه |
      | 29 | `buildMissingAuthMessage` | تلميح مخصص عند غياب المصادقة |
      | 30 | `suppressBuiltInModel` | إخفاء الصفوف القديمة في المنبع |
      | 31 | `augmentModelCatalog` | صفوف تركيبية للتوافق المستقبلي |
      | 32 | `isBinaryThinking` | تشغيل/إيقاف التفكير الثنائي |
      | 33 | `supportsXHighThinking` | دعم الاستدلال `xhigh` |
      | 34 | `resolveDefaultThinkingLevel` | سياسة `/think` الافتراضية |
      | 35 | `isModernModelRef` | مطابقة النماذج الحية/اختبارات smoke |
      | 36 | `prepareRuntimeAuth` | تبادل الرمز قبل الاستدلال |
      | 37 | `resolveUsageAuth` | تحليل مخصص لبيانات اعتماد الاستخدام |
      | 38 | `fetchUsageSnapshot` | نقطة نهاية استخدام مخصصة |
      | 39 | `createEmbeddingProvider` | مكيّف embedding يملكه الموفّر للذاكرة/البحث |
      | 40 | `buildReplayPolicy` | سياسة مخصصة لإعادة تشغيل/ضغط السجل |
      | 41 | `sanitizeReplayHistory` | إعادة كتابة إعادة التشغيل الخاصة بالموفّر بعد التنظيف العام |
      | 42 | `validateReplayTurns` | تحقق صارم من أدوار إعادة التشغيل قبل المشغّل المضمّن |
      | 43 | `onModelSelected` | رد نداء بعد الاختيار (مثل القياس عن بُعد) |

      ملاحظة حول ضبط الـ prompt:

      - يتيح `resolveSystemPromptContribution` لموفّر ما حقن
        إرشادات system-prompt واعية بالتخزين المؤقت لعائلة نموذجية. ويفضّل استخدامه بدلًا من
        `before_prompt_build` عندما يكون السلوك تابعًا لموفّر/عائلة نموذج
        واحدة ويجب أن يحافظ على الفصل المستقر/الديناميكي للذاكرة المؤقتة.

      للحصول على أوصاف مفصلة وأمثلة من العالم الحقيقي، راجع
      [الداخليات: Hooks وقت تشغيل الموفّر](/ar/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="إضافة قدرات إضافية (اختياري)">
    <a id="step-5-add-extra-capabilities"></a>
    يمكن لـ plugin الموفّر تسجيل موفّرات speech، وrealtime transcription، وrealtime
    voice، وفهم الوسائط، وتوليد الصور، وتوليد الفيديو، وجلب الويب،
    والبحث على الويب إلى جانب استدلال النص:

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

    يصنّف OpenClaw هذا على أنه plugin **hybrid-capability**. وهذا هو
    النمط الموصى به لإضافات الشركات (plugin واحد لكل مورّد). راجع
    [الداخليات: ملكية القدرات](/ar/plugins/architecture#capability-ownership-model).

    بالنسبة إلى توليد الفيديو، ففضّل شكل القدرات الواعي بالنمط كما هو موضح أعلاه:
    `generate` و`imageToVideo` و`videoToVideo`. الحقول التجميعية المسطحة مثل
    `maxInputImages` و`maxInputVideos` و`maxDurationSeconds` ليست
    كافية للإعلان بوضوح عن دعم أوضاع التحويل أو الأوضاع المعطلة.

    يجب أن تتبع موفّرات توليد الموسيقى النمط نفسه:
    `generate` للتوليد المعتمد على prompt فقط و`edit` للتوليد
    القائم على صورة مرجعية. الحقول التجميعية المسطحة مثل `maxInputImages`،
    و`supportsLyrics`، و`supportsFormat` ليست كافية للإعلان عن دعم
    التحرير؛ فكتل `generate` / `edit` الصريحة هي العقد المتوقع.

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

تُنشر إضافات الموفّرين بالطريقة نفسها مثل أي plugin كود خارجي آخر:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

لا تستخدم الاسم البديل القديم الخاص بالنشر المعتمد على Skills هنا؛ ينبغي أن تستخدم
حزم plugin الأمر `clawhub package publish`.

## بنية الملفات

```
<bundled-plugin-root>/acme-ai/
├── package.json              # بيانات openclaw.providers الوصفية
├── openclaw.plugin.json      # بيان يتضمن بيانات مصادقة الموفّر الوصفية
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # اختبارات
    └── usage.ts              # نقطة نهاية الاستخدام (اختياري)
```

## مرجع ترتيب الفهرس

يتحكم `catalog.order` في توقيت دمج فهرسك بالنسبة إلى
الموفّرين المدمجين:

| الترتيب | متى | حالة الاستخدام |
| --------- | ------------- | ----------------------------------------------- |
| `simple`  | المرور الأول    | موفّرات بمفتاح API عادي                         |
| `profile` | بعد simple  | موفّرات مقيّدة بملفات تعريف المصادقة                |
| `paired`  | بعد profile | تركيب إدخالات مرتبطة متعددة             |
| `late`    | المرور الأخير     | تجاوز الموفّرين الحاليين (يفوز عند التعارض) |

## الخطوات التالية

- [إضافات القنوات](/ar/plugins/sdk-channel-plugins) — إذا كان plugin الخاص بك يوفّر قناة أيضًا
- [وقت تشغيل SDK](/ar/plugins/sdk-runtime) — مساعدات `api.runtime` ‏(TTS، والبحث، والوكيل الفرعي)
- [نظرة عامة على SDK](/ar/plugins/sdk-overview) — مرجع كامل لواردات المسارات الفرعية
- [داخليات Plugin](/ar/plugins/architecture#provider-runtime-hooks) — تفاصيل hooks وأمثلة من الموفّرين المجمّعين
