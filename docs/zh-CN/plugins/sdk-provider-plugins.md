---
read_when:
    - 你正在构建一个新的模型 provider 插件
    - 你想为 OpenClaw 添加一个与 OpenAI 兼容的代理或自定义 LLM
    - 你需要了解 provider 身份验证、目录和运行时 hooks
sidebarTitle: Provider Plugins
summary: 构建 OpenClaw 模型 provider 插件的分步指南
title: 构建提供商插件
x-i18n:
    generated_at: "2026-04-06T15:30:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4da82a353e1bf4fe6dc09e14b8614133ac96565679627de51415926014bd3990
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# 构建提供商插件

本指南将带你构建一个 provider 插件，为 OpenClaw 添加一个模型 provider
（LLM）。完成后，你将拥有一个具备模型目录、API 密钥身份验证和动态模型解析的 provider。

<Info>
  如果你之前从未构建过任何 OpenClaw 插件，请先阅读
  [入门指南](/zh-CN/plugins/building-plugins) 以了解基本包结构和清单设置。
</Info>

## 演练

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="包和清单">
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

    清单声明了 `providerAuthEnvVars`，这样 OpenClaw 就可以在不加载你的插件运行时的情况下检测凭证。`modelSupport` 是可选的，它允许 OpenClaw 在运行时 hooks 存在之前，就根据像 `acme-large` 这样的简写模型 id 自动加载你的 provider 插件。如果你要在 ClawHub 上发布 provider，那么 `package.json` 中的这些 `openclaw.compat` 和 `openclaw.build` 字段是必需的。

  </Step>

  <Step title="注册 provider">
    一个最小可用的 provider 需要 `id`、`label`、`auth` 和 `catalog`：

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

    这就是一个可工作的 provider。用户现在可以
    `openclaw onboard --acme-ai-api-key <key>` 并选择
    `acme-ai/acme-large` 作为他们的模型。

    对于只注册一个文本 provider、使用 API 密钥身份验证并带有单个目录支持运行时的内置 provider，优先使用更窄的
    `defineSingleProviderPluginEntry(...)` 辅助函数：

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

    如果你的身份验证流程在新手引导期间还需要修补 `models.providers.*`、别名以及智能体默认模型，请使用 `openclaw/plugin-sdk/provider-onboard` 中的预设辅助函数。最窄的辅助函数是
    `createDefaultModelPresetAppliers(...)`、
    `createDefaultModelsPresetAppliers(...)` 和
    `createModelCatalogPresetAppliers(...)`。

    当 provider 的原生端点在常规 `openai-completions` 传输上支持流式 usage 块时，优先使用
    `openclaw/plugin-sdk/provider-catalog-shared` 中的共享目录辅助函数，而不是硬编码 provider-id 检查。`supportsNativeStreamingUsageCompat(...)` 和
    `applyProviderNativeStreamingUsageCompat(...)` 会从端点能力映射中检测支持情况，因此即使插件使用的是自定义 provider id，原生 Moonshot/DashScope 风格端点也仍然可以选择接入。

  </Step>

  <Step title="添加动态模型解析">
    如果你的 provider 接受任意模型 ID（例如代理或路由器），请添加 `resolveDynamicModel`：

    ```typescript
    api.registerProvider({
      // ... 上面的 id、label、auth、catalog

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

    如果解析需要网络调用，请使用 `prepareDynamicModel` 进行异步预热——在它完成后，`resolveDynamicModel` 会再次运行。

  </Step>

  <Step title="添加运行时 hooks（按需）">
    大多数 provider 只需要 `catalog` + `resolveDynamicModel`。根据你的 provider 需求逐步添加 hooks。

    共享辅助构建器现在已经覆盖了最常见的 replay/tool-compat
    家族，因此插件通常不需要再逐个手工接线每个 hook：

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

    当前可用的 replay 家族：

    | Family | 接入内容 |
    | --- | --- |
    | `openai-compatible` | 面向与 OpenAI 兼容传输的共享 OpenAI 风格 replay 策略，包括 tool-call-id 清理、assistant 优先顺序修正，以及在传输需要时的通用 Gemini 轮次校验 |
    | `anthropic-by-model` | 按 `modelId` 选择的 Claude 感知 replay 策略，因此 Anthropic-message 传输只有在解析出的模型实际是 Claude id 时，才会获得 Claude 专属的 thinking 块清理 |
    | `google-gemini` | 原生 Gemini replay 策略，加上 bootstrap replay 清理和带标签的 reasoning-output 模式 |
    | `passthrough-gemini` | 针对通过与 OpenAI 兼容代理传输运行的 Gemini 模型的 Gemini thought-signature 清理；不会启用原生 Gemini replay 校验或 bootstrap 重写 |
    | `hybrid-anthropic-openai` | 适用于在单个插件中混合 Anthropic-message 和与 OpenAI 兼容模型表面的 provider 的混合策略；可选的仅 Claude thinking-block 丢弃仍然限定在 Anthropic 一侧 |

    真实的内置示例：

    - `google` 和 `google-gemini-cli`：`google-gemini`
    - `openrouter`、`kilocode`、`opencode` 和 `opencode-go`：`passthrough-gemini`
    - `amazon-bedrock` 和 `anthropic-vertex`：`anthropic-by-model`
    - `minimax`：`hybrid-anthropic-openai`
    - `moonshot`、`ollama`、`xai` 和 `zai`：`openai-compatible`

    当前可用的流式家族：

    | Family | 接入内容 |
    | --- | --- |
    | `google-thinking` | 共享流路径上的 Gemini thinking 负载标准化 |
    | `kilocode-thinking` | 共享代理流路径上的 Kilo reasoning 包装器，其中 `kilo/auto` 和不支持的代理 reasoning id 会跳过注入的 thinking |
    | `moonshot-thinking` | 基于配置和 `/think` 级别的 Moonshot 二进制原生 thinking 负载映射 |
    | `minimax-fast-mode` | 共享流路径上的 MiniMax fast-mode 模型重写 |
    | `openai-responses-defaults` | 共享的原生 OpenAI/Codex Responses 包装器：归属标头、`/fast`/`serviceTier`、文本详细度、原生 Codex Web 搜索、reasoning 兼容负载整形，以及 Responses 上下文管理 |
    | `openrouter-thinking` | 面向代理路由的 OpenRouter reasoning 包装器，其中不支持模型/`auto` 跳过由中心统一处理 |
    | `tool-stream-default-on` | 针对像 Z.AI 这类 provider 的默认开启 `tool_stream` 包装器，除非显式禁用 |

    真实的内置示例：

    - `google` 和 `google-gemini-cli`：`google-thinking`
    - `kilocode`：`kilocode-thinking`
    - `moonshot`：`moonshot-thinking`
    - `minimax` 和 `minimax-portal`：`minimax-fast-mode`
    - `openai` 和 `openai-codex`：`openai-responses-defaults`
    - `openrouter`：`openrouter-thinking`
    - `zai`：`tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared` 还导出了 replay-family
    枚举，以及这些家族构建所复用的共享辅助函数。常见公共导出包括：

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - 共享 replay 构建器，例如 `buildOpenAICompatibleReplayPolicy(...)`、
      `buildAnthropicReplayPolicyForModel(...)`、
      `buildGoogleGeminiReplayPolicy(...)` 和
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - Gemini replay 辅助函数，例如 `sanitizeGoogleGeminiReplayHistory(...)`
      和 `resolveTaggedReasoningOutputMode()`
    - 端点/模型辅助函数，例如 `resolveProviderEndpoint(...)`、
      `normalizeProviderId(...)`、`normalizeGooglePreviewModelId(...)` 和
      `normalizeNativeXaiModelId(...)`

    `openclaw/plugin-sdk/provider-stream` 同时暴露家族构建器和这些家族复用的公共包装辅助函数。常见公共导出包括：

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - 共享 OpenAI/Codex 包装器，例如
      `createOpenAIAttributionHeadersWrapper(...)`、
      `createOpenAIFastModeWrapper(...)`、
      `createOpenAIServiceTierWrapper(...)`、
      `createOpenAIResponsesContextManagementWrapper(...)` 和
      `createCodexNativeWebSearchWrapper(...)`
    - 共享代理/provider 包装器，例如 `createOpenRouterWrapper(...)`、
      `createToolStreamWrapper(...)` 和 `createMinimaxFastModeWrapper(...)`

    某些流式辅助函数会有意保留为 provider 本地。当前内置
    示例：`@openclaw/anthropic-provider` 从其公共 `api.ts` /
    `contract-api.ts` 接缝中导出
    `wrapAnthropicProviderStream`、`resolveAnthropicBetas`、
    `resolveAnthropicFastMode`、`resolveAnthropicServiceTier` 以及更底层的 Anthropic 包装器构建器。这些辅助函数仍然保持 Anthropic 专属，因为它们还编码了 Claude OAuth beta 处理和 `context1m` gating。

    其他内置 provider 也会在行为无法在家族间干净共享时，将传输专属包装器保留为本地。当前示例：内置 xAI 插件将原生 xAI Responses 整形保留在自己的
    `wrapStreamFn` 中，包括 `/fast` 别名重写、默认 `tool_stream`、
    不支持的 strict-tool 清理，以及 xAI 专属 reasoning 负载移除。

    `openclaw/plugin-sdk/provider-tools` 当前暴露一个共享
    tool-schema 家族，以及共享的 schema/compat 辅助函数：

    - `ProviderToolCompatFamily` 记录当前共享家族清单。
    - `buildProviderToolCompatFamilyHooks("gemini")` 为需要 Gemini 安全工具 schema 的 provider 接入 Gemini schema 清理 + 诊断。
    - `normalizeGeminiToolSchemas(...)` 和 `inspectGeminiToolSchemas(...)`
      是底层公开的 Gemini schema 辅助函数。
    - `resolveXaiModelCompatPatch()` 返回内置 xAI compat 补丁：
      `toolSchemaProfile: "xai"`、不支持的 schema 关键字、原生
      `web_search` 支持，以及 HTML 实体 tool-call 参数解码。
    - `applyXaiModelCompat(model)` 会在模型进入运行器前，将同一份 xAI compat 补丁应用到已解析模型上。

    真实的内置示例：xAI 插件使用 `normalizeResolvedModel` 加上
    `contributeResolvedModelCompat`，以保持该 compat 元数据由 provider 自己拥有，而不是在核心中硬编码 xAI 规则。

    同样的包根模式也支撑其他内置 provider：

    - `@openclaw/openai-provider`：`api.ts` 导出 provider 构建器、
      默认模型辅助函数和 realtime provider 构建器
    - `@openclaw/openrouter-provider`：`api.ts` 导出 provider 构建器
      以及新手引导/配置辅助函数

    <Tabs>
      <Tab title="令牌交换">
        对于需要在每次推理调用前进行令牌交换的 provider：

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
      <Tab title="自定义标头">
        对于需要自定义请求标头或请求体修改的 provider：

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
      <Tab title="原生传输标识">
        对于需要在通用 HTTP 或 WebSocket 传输上附加原生请求/会话标头或元数据的 provider：

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
      <Tab title="用量和计费">
        对于暴露用量/计费数据的 provider：

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

    <Accordion title="所有可用的 provider hooks">
      OpenClaw 按以下顺序调用 hooks。大多数 provider 只会使用 2-3 个：

      | # | Hook | 使用时机 |
      | --- | --- | --- |
      | 1 | `catalog` | 模型目录或 base URL 默认值 |
      | 2 | `applyConfigDefaults` | 在配置实体化期间应用 provider 自有的全局默认值 |
      | 3 | `normalizeModelId` | 在查找前清理旧版/预览版模型 id 别名 |
      | 4 | `normalizeTransport` | 在通用模型组装前清理 provider-family 的 `api` / `baseUrl` |
      | 5 | `normalizeConfig` | 标准化 `models.providers.<id>` 配置 |
      | 6 | `applyNativeStreamingUsageCompat` | 面向配置 provider 的原生流式 usage compat 重写 |
      | 7 | `resolveConfigApiKey` | provider 自有的环境变量标记身份验证解析 |
      | 8 | `resolveSyntheticAuth` | 本地/自托管或配置支持的 synthetic auth |
      | 9 | `shouldDeferSyntheticProfileAuth` | 将 synthetic 的已存储 profile 占位符降到 env/config auth 之后 |
      | 10 | `resolveDynamicModel` | 接受任意上游模型 ID |
      | 11 | `prepareDynamicModel` | 在解析前异步获取元数据 |
      | 12 | `normalizeResolvedModel` | 在运行器前进行传输重写 |

    运行时回退说明：

    - `normalizeConfig` 会先检查匹配的 provider，然后再检查其他
      具备 hook 能力的 provider 插件，直到其中一个实际修改了配置。
      如果没有任何 provider hook 重写受支持的 Google-family 配置条目，
      则仍会应用内置 Google 配置标准化器。
    - `resolveConfigApiKey` 在暴露该 hook 时会使用 provider hook。内置的
      `amazon-bedrock` 路径在这里也有一个内建 AWS 环境变量标记解析器，
      即便 Bedrock 运行时身份验证本身仍然使用 AWS SDK 默认链。
      | 13 | `contributeResolvedModelCompat` | 面向运行在另一种兼容传输后的厂商模型的 compat 标志 |
      | 14 | `capabilities` | 旧版静态能力包；仅为兼容性保留 |
      | 15 | `normalizeToolSchemas` | 在注册前由 provider 自有进行工具 schema 清理 |
      | 16 | `inspectToolSchemas` | 由 provider 自有进行工具 schema 诊断 |
      | 17 | `resolveReasoningOutputMode` | 带标签与原生 reasoning-output 合约 |
      | 18 | `prepareExtraParams` | 默认请求参数 |
      | 19 | `createStreamFn` | 完全自定义的 StreamFn 传输 |
      | 20 | `wrapStreamFn` | 常规流路径上的自定义标头/请求体包装器 |
      | 21 | `resolveTransportTurnState` | 原生逐轮标头/元数据 |
      | 22 | `resolveWebSocketSessionPolicy` | 原生 WS 会话标头/冷却策略 |
      | 23 | `formatApiKey` | 自定义运行时令牌形态 |
      | 24 | `refreshOAuth` | 自定义 OAuth 刷新 |
      | 25 | `buildAuthDoctorHint` | 身份验证修复指引 |
      | 26 | `matchesContextOverflowError` | provider 自有的上下文溢出检测 |
      | 27 | `classifyFailoverReason` | provider 自有的速率限制/过载分类 |
      | 28 | `isCacheTtlEligible` | 提示词缓存 TTL gating |
      | 29 | `buildMissingAuthMessage` | 自定义缺失身份验证提示 |
      | 30 | `suppressBuiltInModel` | 隐藏过时的上游条目 |
      | 31 | `augmentModelCatalog` | synthetic 前向兼容条目 |
      | 32 | `isBinaryThinking` | 二进制 thinking 开/关 |
      | 33 | `supportsXHighThinking` | `xhigh` reasoning 支持 |
      | 34 | `resolveDefaultThinkingLevel` | 默认 `/think` 策略 |
      | 35 | `isModernModelRef` | 实时/smoke 模型匹配 |
      | 36 | `prepareRuntimeAuth` | 推理前的令牌交换 |
      | 37 | `resolveUsageAuth` | 自定义用量凭证解析 |
      | 38 | `fetchUsageSnapshot` | 自定义用量端点 |
      | 39 | `createEmbeddingProvider` | 面向 memory/search 的 provider 自有嵌入适配器 |
      | 40 | `buildReplayPolicy` | 自定义转录 replay/压缩策略 |
      | 41 | `sanitizeReplayHistory` | 通用清理后的 provider 专属 replay 重写 |
      | 42 | `validateReplayTurns` | 嵌入式运行器前的严格 replay 轮次校验 |
      | 43 | `onModelSelected` | 选择模型后的回调（例如遥测） |

      提示词调优说明：

      - `resolveSystemPromptContribution` 允许 provider 为某个模型家族注入缓存感知的系统提示词指导。对于属于某个 provider/模型家族并且应该保留稳定/动态缓存拆分的行为，优先使用它，而不是
        `before_prompt_build`。

      有关详细说明和真实示例，请参见
      [内部机制：提供商运行时 Hooks](/zh-CN/plugins/architecture#provider-runtime-hooks)。
    </Accordion>

  </Step>

  <Step title="添加额外能力（可选）">
    <a id="step-5-add-extra-capabilities"></a>
    provider 插件除了文本推理外，还可以注册 speech、realtime transcription、realtime
    voice、media understanding、image generation、video generation、web fetch
    和 web search：

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

    OpenClaw 会将其归类为**混合能力**插件。这是公司级插件（每个厂商一个插件）的推荐模式。参见
    [内部机制：能力归属](/zh-CN/plugins/architecture#capability-ownership-model)。

    对于视频生成，优先使用上面展示的模式感知能力形态：
    `generate`、`imageToVideo` 和 `videoToVideo`。像
    `maxInputImages`、`maxInputVideos` 和 `maxDurationSeconds` 这样的扁平聚合字段，不足以干净地表达变换模式支持或已禁用模式。

    音乐生成 provider 也应遵循同样的模式：
    `generate` 用于仅提示词生成，`edit` 用于基于参考图像的生成。像 `maxInputImages`、
    `supportsLyrics` 和 `supportsFormat` 这样的扁平聚合字段，不足以表达 edit 支持；显式的 `generate` / `edit` 块才是预期合约。

  </Step>

  <Step title="测试">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // 从 index.ts 或单独文件导出你的 provider 配置对象
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

## 发布到 ClawHub

Provider 插件的发布方式与任何其他外部代码插件相同：

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

这里不要使用旧版仅 Skills 的发布别名；插件包应使用
`clawhub package publish`。

## 文件结构

```
<bundled-plugin-root>/acme-ai/
├── package.json              # openclaw.providers 元数据
├── openclaw.plugin.json      # 带有 providerAuthEnvVars 的清单
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # 测试
    └── usage.ts              # 用量端点（可选）
```

## 目录顺序参考

`catalog.order` 控制你的目录相对于内置 provider 的合并时机：

| Order | 时机 | 使用场景 |
| --------- | ------------- | ----------------------------------------------- |
| `simple`  | 第一轮 | 纯 API 密钥 provider |
| `profile` | 在 simple 之后 | 由 auth profile 控制的 provider |
| `paired`  | 在 profile 之后 | 合成多个相关条目 |
| `late`    | 最后一轮 | 覆盖现有 provider（冲突时胜出） |

## 后续步骤

- [渠道插件](/zh-CN/plugins/sdk-channel-plugins) — 如果你的插件还提供一个渠道
- [插件运行时](/zh-CN/plugins/sdk-runtime) — `api.runtime` 辅助函数（TTS、搜索、子智能体）
- [SDK 概览](/zh-CN/plugins/sdk-overview) — 完整子路径导入参考
- [插件内部机制](/zh-CN/plugins/architecture#provider-runtime-hooks) — hook 细节和内置示例
