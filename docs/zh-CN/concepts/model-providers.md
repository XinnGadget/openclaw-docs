---
read_when:
    - 你需要按提供商区分的模型设置参考
    - 你想查看模型提供商的示例配置或 CLI 新手引导命令
summary: 模型提供商概览，包含示例配置和 CLI 流程
title: 模型提供商
x-i18n:
    generated_at: "2026-04-05T18:14:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 24e6275b0bf137fa8143baa2a1d729439ecec6a0d7c0c14fed78c522f691476f
    source_path: concepts/model-providers.md
    workflow: 15
---

# 模型提供商

本页介绍 **LLM/模型提供商**（不是像 WhatsApp/Telegram 这样的聊天渠道）。
关于模型选择规则，请参见 [/concepts/models](/zh-CN/concepts/models)。

## 快速规则

- 模型引用使用 `provider/model`（例如：`opencode/claude-opus-4-6`）。
- 如果你设置了 `agents.defaults.models`，它就会成为允许列表。
- CLI 助手：`openclaw onboard`、`openclaw models list`、`openclaw models set <provider/model>`。
- 回退运行时规则、冷却探测和会话覆盖持久化记录在 [/concepts/model-failover](/zh-CN/concepts/model-failover) 中。
- `models.providers.*.models[].contextWindow` 是原生模型元数据；`models.providers.*.models[].contextTokens` 是生效的运行时上限。
- 提供商插件可以通过 `registerProvider({ catalog })` 注入模型目录；OpenClaw 会在写入 `models.json` 之前将该输出合并到 `models.providers` 中。
- 提供商清单可以声明 `providerAuthEnvVars`，这样基于通用环境变量的认证探测就不需要加载插件运行时。剩余的核心环境变量映射现在仅用于非插件/核心提供商，以及少数通用优先级场景，例如 Anthropic 的“API 密钥优先”新手引导。
- 提供商插件还可以通过 `normalizeModelId`、`normalizeTransport`、`normalizeConfig`、`applyNativeStreamingUsageCompat`、`resolveConfigApiKey`、`resolveSyntheticAuth`、`shouldDeferSyntheticProfileAuth`、`resolveDynamicModel`、`prepareDynamicModel`、`normalizeResolvedModel`、`contributeResolvedModelCompat`、`capabilities`、`normalizeToolSchemas`、`inspectToolSchemas`、`resolveReasoningOutputMode`、`prepareExtraParams`、`createStreamFn`、`wrapStreamFn`、`resolveTransportTurnState`、`resolveWebSocketSessionPolicy`、`createEmbeddingProvider`、`formatApiKey`、`refreshOAuth`、`buildAuthDoctorHint`、`matchesContextOverflowError`、`classifyFailoverReason`、`isCacheTtlEligible`、`buildMissingAuthMessage`、`suppressBuiltInModel`、`augmentModelCatalog`、`isBinaryThinking`、`supportsXHighThinking`、`resolveDefaultThinkingLevel`、`applyConfigDefaults`、`isModernModelRef`、`prepareRuntimeAuth`、`resolveUsageAuth`、`fetchUsageSnapshot` 以及 `onModelSelected` 来接管提供商运行时行为。
- 注意：提供商运行时 `capabilities` 是共享的运行器元数据（提供商家族、转录/工具差异、传输/缓存提示）。它与[公共能力模型](/zh-CN/plugins/architecture#public-capability-model)不同，后者描述的是插件注册了什么内容（文本推理、语音等）。

## 插件自有的提供商行为

现在，提供商插件可以接管大多数提供商特定逻辑，而 OpenClaw 保留通用推理循环。

典型划分如下：

- `auth[].run` / `auth[].runNonInteractive`：提供商负责 `openclaw onboard`、`openclaw models auth` 和无头设置的 onboarding/登录流程
- `wizard.setup` / `wizard.modelPicker`：提供商负责认证选项标签、旧别名、onboarding 允许列表提示，以及 onboarding/模型选择器中的设置项
- `catalog`：提供商会出现在 `models.providers` 中
- `normalizeModelId`：提供商会在查找或规范化之前规范旧版/预览模型 ID
- `normalizeTransport`：提供商会在通用模型组装之前规范传输族的 `api` / `baseUrl`；OpenClaw 会先检查匹配的提供商，再检查其他支持此 Hook 的提供商插件，直到某个插件实际更改了传输
- `normalizeConfig`：提供商会在运行时使用前规范 `models.providers.<id>` 配置；OpenClaw 会先检查匹配的提供商，再检查其他支持此 Hook 的提供商插件，直到某个插件实际更改了配置。如果没有提供商 Hook 重写配置，内置的 Google 系列助手仍会规范受支持的 Google 提供商条目。
- `applyNativeStreamingUsageCompat`：提供商会对配置提供商应用由端点驱动的原生流式用量兼容重写
- `resolveConfigApiKey`：提供商会为配置提供商解析环境变量标记认证，而无需强制加载完整运行时认证。`amazon-bedrock` 在这里还内置了 AWS 环境变量标记解析器，尽管 Bedrock 运行时认证使用的是 AWS SDK 默认链。
- `resolveSyntheticAuth`：提供商可以暴露本地/自托管或其他基于配置的可用认证，而无需持久化明文密钥
- `shouldDeferSyntheticProfileAuth`：提供商可以将已存储的合成配置档占位符标记为优先级低于环境变量/配置支持的认证
- `resolveDynamicModel`：提供商可以接受尚未出现在本地静态目录中的模型 ID
- `prepareDynamicModel`：提供商在重试动态解析前需要刷新元数据
- `normalizeResolvedModel`：提供商需要进行传输或基础 URL 重写
- `contributeResolvedModelCompat`：即使供应商模型是通过另一种兼容传输到达的，提供商也能为其贡献兼容标志
- `capabilities`：提供商发布转录/工具/提供商家族差异信息
- `normalizeToolSchemas`：提供商会在嵌入式运行器看到工具模式前对其进行清理
- `inspectToolSchemas`：提供商会在规范化后暴露特定于传输的模式警告
- `resolveReasoningOutputMode`：提供商选择原生或带标签的推理输出契约
- `prepareExtraParams`：提供商为每个模型的请求参数设置默认值或进行规范化
- `createStreamFn`：提供商使用完全自定义的传输替换常规流路径
- `wrapStreamFn`：提供商应用请求头/请求体/模型兼容包装器
- `resolveTransportTurnState`：提供商为每一轮提供原生传输请求头或元数据
- `resolveWebSocketSessionPolicy`：提供商提供原生 WebSocket 会话请求头或会话冷却策略
- `createEmbeddingProvider`：当内存嵌入行为更适合归属提供商插件而不是核心嵌入分发器时，由提供商接管
- `formatApiKey`：提供商将已存储的认证配置档格式化为传输所期望的运行时 `apiKey` 字符串
- `refreshOAuth`：当共享的 `pi-ai` 刷新器不足时，由提供商负责 OAuth 刷新
- `buildAuthDoctorHint`：当 OAuth 刷新失败时，由提供商追加修复指导
- `matchesContextOverflowError`：提供商识别通用启发式规则遗漏的、特定于提供商的上下文窗口溢出错误
- `classifyFailoverReason`：提供商将特定于提供商的原始传输/API 错误映射为回退原因，例如速率限制或过载
- `isCacheTtlEligible`：提供商决定哪些上游模型 ID 支持提示缓存 TTL
- `buildMissingAuthMessage`：提供商用特定于提供商的恢复提示替换通用认证存储错误
- `suppressBuiltInModel`：提供商隐藏过时的上游条目，并且可以在直接解析失败时返回供应商自有错误
- `augmentModelCatalog`：提供商在发现和配置合并之后追加合成/最终目录条目
- `isBinaryThinking`：提供商接管二元开/关 thinking 体验
- `supportsXHighThinking`：提供商让选定模型启用 `xhigh`
- `resolveDefaultThinkingLevel`：提供商接管某个模型家族的默认 `/think` 策略
- `applyConfigDefaults`：提供商根据认证模式、环境变量或模型家族，在配置具体化期间应用提供商特定的全局默认值
- `isModernModelRef`：提供商接管 live/smoke 首选模型匹配
- `prepareRuntimeAuth`：提供商将已配置凭证转换为短时效运行时令牌
- `resolveUsageAuth`：提供商为 `/usage` 及相关状态/报告界面解析用量/配额凭证
- `fetchUsageSnapshot`：提供商接管用量端点获取/解析，而核心仍负责摘要外壳和格式化
- `onModelSelected`：提供商在模型选定后运行后续副作用，例如遥测或提供商自有的会话簿记

当前内置示例：

- `anthropic`：Claude 4.6 前向兼容回退、认证修复提示、用量端点抓取、缓存 TTL/提供商家族元数据，以及具备认证感知的全局配置默认值
- `amazon-bedrock`：提供商自有的上下文溢出匹配和针对 Bedrock 特有节流/未就绪错误的回退原因分类，外加共享的 `anthropic-by-model` 重放家族，用于 Anthropic 流量上的仅 Claude 重放策略保护
- `anthropic-vertex`：面向 Anthropic-message 流量的仅 Claude 重放策略保护
- `openrouter`：透传模型 ID、请求包装器、提供商能力提示、代理 Gemini 流量上的 Gemini thought-signature 清理、通过 `openrouter-thinking` 流家族注入代理推理、路由元数据转发，以及缓存 TTL 策略
- `github-copilot`：onboarding/设备登录、前向兼容模型回退、Claude-thinking 转录提示、运行时令牌交换，以及用量端点抓取
- `openai`：GPT-5.4 前向兼容回退、直接 OpenAI 传输规范化、具备 Codex 感知的缺失认证提示、Spark 抑制、合成 OpenAI/Codex 目录条目、thinking/live-model 策略、用量令牌别名规范化（`input` / `output` 和 `prompt` / `completion` 家族）、共享的 `openai-responses-defaults` 流家族用于原生 OpenAI/Codex 包装器，以及提供商家族元数据
- `google`：Gemini 3.1 前向兼容回退、原生 Gemini 重放验证、引导重放清理、带标签的推理输出模式，以及现代模型匹配
- `moonshot`：共享传输、插件自有的 thinking 负载规范化
- `kilocode`：共享传输、插件自有的请求头、推理负载规范化、代理 Gemini thought-signature 清理，以及缓存 TTL 策略
- `zai`：GLM-5 前向兼容回退、`tool_stream` 默认值、缓存 TTL 策略、二元 thinking/live-model 策略，以及用量认证 + 配额抓取；未知的 `glm-5*` ID 会基于内置的 `glm-4.7` 模板合成
- `xai`：原生 Responses 传输规范化、针对 Grok 快速变体的 `/fast` 别名重写、默认 `tool_stream`，以及 xAI 特有的工具模式 / 推理负载清理
- `mistral`：插件自有的能力元数据
- `opencode` 和 `opencode-go`：插件自有的能力元数据，外加代理 Gemini thought-signature 清理
- `byteplus`、`cloudflare-ai-gateway`、`huggingface`、`kimi`、`nvidia`、`qianfan`、`stepfun`、`synthetic`、`together`、`venice`、`vercel-ai-gateway` 和 `volcengine`：仅插件自有目录
- `qwen`：文本模型的插件自有目录，以及用于其多模态界面的共享媒体理解和视频生成提供商注册；Qwen 视频生成使用标准 DashScope 视频端点和内置的 Wan 模型，例如 `wan2.6-t2v` 和 `wan2.7-r2v`
- `minimax`：插件自有目录、混合 Anthropic/OpenAI 重放策略选择，以及用量认证/快照逻辑
- `xiaomi`：插件自有目录，以及用量认证/快照逻辑

内置的 `openai` 插件现在同时拥有两个提供商 ID：`openai` 和 `openai-codex`。

以上涵盖了仍适配 OpenClaw 常规传输方式的提供商。若某个提供商需要完全自定义的请求执行器，那就是另一层更深入的扩展接口了。

## API 密钥轮换

- 支持为选定提供商进行通用提供商轮换。
- 通过以下方式配置多个密钥：
  - `OPENCLAW_LIVE_<PROVIDER>_KEY`（单个 live 覆盖，最高优先级）
  - `<PROVIDER>_API_KEYS`（逗号或分号分隔列表）
  - `<PROVIDER>_API_KEY`（主密钥）
  - `<PROVIDER>_API_KEY_*`（编号列表，例如 `<PROVIDER>_API_KEY_1`）
- 对于 Google 提供商，`GOOGLE_API_KEY` 也会作为回退值包含在内。
- 密钥选择顺序会保留优先级并对值去重。
- 仅在速率限制响应时，请求才会使用下一个密钥重试（例如 `429`、`rate_limit`、`quota`、`resource exhausted`、`Too many concurrent requests`、`ThrottlingException`、`concurrency limit reached`、`workers_ai ... quota limit exceeded` 或周期性用量限制消息）。
- 非速率限制失败会立即失败；不会尝试密钥轮换。
- 当所有候选密钥都失败时，会返回最后一次尝试的最终错误。

## 内置提供商（pi-ai 目录）

OpenClaw 附带 pi‑ai 目录。这些提供商**不需要** `models.providers` 配置；只需设置认证并选择一个模型。

### OpenAI

- 提供商：`openai`
- 认证：`OPENAI_API_KEY`
- 可选轮换：`OPENAI_API_KEYS`、`OPENAI_API_KEY_1`、`OPENAI_API_KEY_2`，以及 `OPENCLAW_LIVE_OPENAI_KEY`（单个覆盖）
- 示例模型：`openai/gpt-5.4`、`openai/gpt-5.4-pro`
- CLI：`openclaw onboard --auth-choice openai-api-key`
- 默认传输是 `auto`（优先 WebSocket，回退到 SSE）
- 可通过 `agents.defaults.models["openai/<model>"].params.transport` 为每个模型覆盖（`"sse"`、`"websocket"` 或 `"auto"`）
- OpenAI Responses WebSocket 预热默认通过 `params.openaiWsWarmup` 启用（`true`/`false`）
- 可通过 `agents.defaults.models["openai/<model>"].params.serviceTier` 启用 OpenAI 优先处理
- `/fast` 和 `params.fastMode` 会将直接 `openai/*` Responses 请求映射到 `api.openai.com` 上的 `service_tier=priority`
- 如果你想使用显式层级而不是共享的 `/fast` 开关，请使用 `params.serviceTier`
- 隐藏的 OpenClaw 归属请求头（`originator`、`version`、`User-Agent`）仅适用于发往 `api.openai.com` 的原生 OpenAI 流量，不适用于通用的 OpenAI 兼容代理
- 原生 OpenAI 路由还会保留 Responses `store`、提示缓存提示以及 OpenAI 推理兼容负载整形；代理路由则不会
- `openai/gpt-5.3-codex-spark` 在 OpenClaw 中被有意抑制，因为 live OpenAI API 会拒绝它；Spark 被视为仅限 Codex

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- 提供商：`anthropic`
- 认证：`ANTHROPIC_API_KEY`
- 可选轮换：`ANTHROPIC_API_KEYS`、`ANTHROPIC_API_KEY_1`、`ANTHROPIC_API_KEY_2`，以及 `OPENCLAW_LIVE_ANTHROPIC_KEY`（单个覆盖）
- 示例模型：`anthropic/claude-opus-4-6`
- CLI：`openclaw onboard --auth-choice apiKey`
- 直接公共 Anthropic 请求支持共享的 `/fast` 开关和 `params.fastMode`，包括发送到 `api.anthropic.com` 的 API 密钥和 OAuth 认证流量；OpenClaw 会将其映射为 Anthropic `service_tier`（`auto` 与 `standard_only`）
- 计费说明：对于 Anthropic 在 OpenClaw 中的使用，实际区分是 **API 密钥** 或 **带 Extra Usage 的 Claude 订阅**。Anthropic 在 **2026 年 4 月 4 日下午 12:00（PT）/ 晚上 8:00（BST）** 通知 OpenClaw 用户，**OpenClaw** 的 Claude 登录路径会被计为第三方工具链使用，因此需要单独于订阅计费的 **Extra Usage**。我们的本地复现还表明，Anthropic SDK + API 密钥路径不会复现 OpenClaw 标识提示字符串。
- Anthropic setup-token 现已再次作为旧版/手动 OpenClaw 路径提供。使用它时，请预期 Anthropic 已告知 OpenClaw 用户，此路径需要 **Extra Usage**。

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code（Codex）

- 提供商：`openai-codex`
- 认证：OAuth（ChatGPT）
- 示例模型：`openai-codex/gpt-5.4`
- CLI：`openclaw onboard --auth-choice openai-codex` 或 `openclaw models auth login --provider openai-codex`
- 默认传输是 `auto`（优先 WebSocket，回退到 SSE）
- 可通过 `agents.defaults.models["openai-codex/<model>"].params.transport` 为每个模型覆盖（`"sse"`、`"websocket"` 或 `"auto"`）
- `params.serviceTier` 也会转发到原生 Codex Responses 请求（`chatgpt.com/backend-api`）
- 隐藏的 OpenClaw 归属请求头（`originator`、`version`、`User-Agent`）仅会附加到发往 `chatgpt.com/backend-api` 的原生 Codex 流量，不适用于通用的 OpenAI 兼容代理
- 与直接 `openai/*` 共享相同的 `/fast` 开关和 `params.fastMode` 配置；OpenClaw 会将其映射为 `service_tier=priority`
- 当 Codex OAuth 目录暴露 `openai-codex/gpt-5.3-codex-spark` 时，它仍可用；是否可用取决于 entitlement
- `openai-codex/gpt-5.4` 保留原生 `contextWindow = 1050000` 和默认运行时 `contextTokens = 272000`；可通过 `models.providers.openai-codex.models[].contextTokens` 覆盖运行时上限
- 策略说明：OpenAI Codex OAuth 明确支持用于 OpenClaw 这类外部工具/工作流。

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [{ id: "gpt-5.4", contextTokens: 160000 }],
      },
    },
  },
}
```

### 其他订阅式托管选项

- [Qwen Cloud](/zh-CN/providers/qwen)：Qwen Cloud 提供商界面，以及 Alibaba DashScope 和 Coding Plan 端点映射
- [MiniMax](/zh-CN/providers/minimax)：MiniMax Coding Plan OAuth 或 API 密钥访问
- [GLM Models](/zh-CN/providers/glm)：Z.AI Coding Plan 或通用 API 端点

### OpenCode

- 认证：`OPENCODE_API_KEY`（或 `OPENCODE_ZEN_API_KEY`）
- Zen 运行时提供商：`opencode`
- Go 运行时提供商：`opencode-go`
- 示例模型：`opencode/claude-opus-4-6`、`opencode-go/kimi-k2.5`
- CLI：`openclaw onboard --auth-choice opencode-zen` 或 `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini（API 密钥）

- 提供商：`google`
- 认证：`GEMINI_API_KEY`
- 可选轮换：`GEMINI_API_KEYS`、`GEMINI_API_KEY_1`、`GEMINI_API_KEY_2`、`GOOGLE_API_KEY` 回退，以及 `OPENCLAW_LIVE_GEMINI_KEY`（单个覆盖）
- 示例模型：`google/gemini-3.1-pro-preview`、`google/gemini-3-flash-preview`
- 兼容性：使用 `google/gemini-3.1-flash-preview` 的旧版 OpenClaw 配置会被规范为 `google/gemini-3-flash-preview`
- CLI：`openclaw onboard --auth-choice gemini-api-key`
- 直接 Gemini 运行也接受 `agents.defaults.models["google/<model>"].params.cachedContent`（或旧版 `cached_content`），以转发提供商原生的 `cachedContents/...` 句柄；Gemini 缓存命中会以 OpenClaw `cacheRead` 形式显示

### Google Vertex

- 提供商：`google-vertex`
- 认证：gcloud ADC
  - Gemini CLI JSON 回复从 `response` 解析；用量会回退到 `stats`，其中 `stats.cached` 会被规范化为 OpenClaw `cacheRead`。

### Z.AI（GLM）

- 提供商：`zai`
- 认证：`ZAI_API_KEY`
- 示例模型：`zai/glm-5`
- CLI：`openclaw onboard --auth-choice zai-api-key`
  - 别名：`z.ai/*` 和 `z-ai/*` 会被规范为 `zai/*`
  - `zai-api-key` 会自动检测匹配的 Z.AI 端点；`zai-coding-global`、`zai-coding-cn`、`zai-global` 和 `zai-cn` 会强制使用特定界面

### Vercel AI Gateway 网关

- 提供商：`vercel-ai-gateway`
- 认证：`AI_GATEWAY_API_KEY`
- 示例模型：`vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI：`openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway 网关

- 提供商：`kilocode`
- 认证：`KILOCODE_API_KEY`
- 示例模型：`kilocode/kilo/auto`
- CLI：`openclaw onboard --auth-choice kilocode-api-key`
- 基础 URL：`https://api.kilo.ai/api/gateway/`
- 静态回退目录附带 `kilocode/kilo/auto`；live `https://api.kilo.ai/api/gateway/models` 发现可进一步扩展运行时目录。
- `kilocode/kilo/auto` 背后的确切上游路由由 Kilo Gateway 网关负责，不在 OpenClaw 中硬编码。

设置详情请参见 [/providers/kilocode](/zh-CN/providers/kilocode)。

### 其他内置提供商插件

- OpenRouter：`openrouter`（`OPENROUTER_API_KEY`）
- 示例模型：`openrouter/auto`
- 仅当请求实际指向 `openrouter.ai` 时，OpenClaw 才会应用 OpenRouter 文档中的应用归属请求头
- OpenRouter 特有的 Anthropic `cache_control` 标记同样仅限已验证的 OpenRouter 路由，不适用于任意代理 URL
- OpenRouter 仍使用代理式 OpenAI 兼容路径，因此不会转发原生 OpenAI 专属请求整形（`serviceTier`、Responses `store`、提示缓存提示、OpenAI 推理兼容负载）
- 基于 Gemini 的 OpenRouter 引用仅保留代理 Gemini thought-signature 清理；原生 Gemini 重放验证和引导重写不会启用
- Kilo Gateway 网关：`kilocode`（`KILOCODE_API_KEY`）
- 示例模型：`kilocode/kilo/auto`
- 基于 Gemini 的 Kilo 引用保留相同的代理 Gemini thought-signature 清理路径；`kilocode/kilo/auto` 及其他不支持代理推理提示的路径会跳过代理推理注入
- MiniMax：`minimax`（API 密钥）和 `minimax-portal`（OAuth）
- 认证：`MINIMAX_API_KEY` 用于 `minimax`；`MINIMAX_OAUTH_TOKEN` 或 `MINIMAX_API_KEY` 用于 `minimax-portal`
- 示例模型：`minimax/MiniMax-M2.7` 或 `minimax-portal/MiniMax-M2.7`
- MiniMax onboarding/API 密钥设置会写入显式的 M2.7 模型定义，并带有 `input: ["text", "image"]`；在该提供商配置具体化之前，内置提供商目录会将聊天引用保持为仅文本
- Moonshot：`moonshot`（`MOONSHOT_API_KEY`）
- 示例模型：`moonshot/kimi-k2.5`
- Kimi Coding：`kimi`（`KIMI_API_KEY` 或 `KIMICODE_API_KEY`）
- 示例模型：`kimi/kimi-code`
- Qianfan：`qianfan`（`QIANFAN_API_KEY`）
- 示例模型：`qianfan/deepseek-v3.2`
- Qwen Cloud：`qwen`（`QWEN_API_KEY`、`MODELSTUDIO_API_KEY` 或 `DASHSCOPE_API_KEY`）
- 示例模型：`qwen/qwen3.5-plus`
- NVIDIA：`nvidia`（`NVIDIA_API_KEY`）
- 示例模型：`nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun：`stepfun` / `stepfun-plan`（`STEPFUN_API_KEY`）
- 示例模型：`stepfun/step-3.5-flash`、`stepfun-plan/step-3.5-flash-2603`
- Together：`together`（`TOGETHER_API_KEY`）
- 示例模型：`together/moonshotai/Kimi-K2.5`
- Venice：`venice`（`VENICE_API_KEY`）
- Xiaomi：`xiaomi`（`XIAOMI_API_KEY`）
- 示例模型：`xiaomi/mimo-v2-flash`
- Vercel AI Gateway 网关：`vercel-ai-gateway`（`AI_GATEWAY_API_KEY`）
- Hugging Face Inference：`huggingface`（`HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN`）
- Cloudflare AI Gateway 网关：`cloudflare-ai-gateway`（`CLOUDFLARE_AI_GATEWAY_API_KEY`）
- Volcengine：`volcengine`（`VOLCANO_ENGINE_API_KEY`）
- 示例模型：`volcengine-plan/ark-code-latest`
- BytePlus（国际版）：`byteplus`（`BYTEPLUS_API_KEY`）
- 示例模型：`byteplus-plan/ark-code-latest`
- xAI：`xai`（`XAI_API_KEY`）
  - 原生内置 xAI 请求使用 xAI Responses 路径
  - `/fast` 或 `params.fastMode: true` 会将 `grok-3`、`grok-3-mini`、`grok-4` 和 `grok-4-0709` 重写为对应的 `*-fast` 变体
  - `tool_stream` 默认开启；将 `agents.defaults.models["xai/<model>"].params.tool_stream` 设为 `false` 可关闭
- Mistral：`mistral`（`MISTRAL_API_KEY`）
- 示例模型：`mistral/mistral-large-latest`
- CLI：`openclaw onboard --auth-choice mistral-api-key`
- Groq：`groq`（`GROQ_API_KEY`）
- Cerebras：`cerebras`（`CEREBRAS_API_KEY`）
  - Cerebras 上的 GLM 模型使用 ID `zai-glm-4.7` 和 `zai-glm-4.6`。
  - OpenAI 兼容基础 URL：`https://api.cerebras.ai/v1`。
- GitHub Copilot：`github-copilot`（`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`）
- Hugging Face Inference 示例模型：`huggingface/deepseek-ai/DeepSeek-R1`；CLI：`openclaw onboard --auth-choice huggingface-api-key`。参见 [Hugging Face（Inference）](/zh-CN/providers/huggingface)。

## 通过 `models.providers` 使用的提供商（自定义/基础 URL）

使用 `models.providers`（或 `models.json`）添加**自定义**提供商或 OpenAI/Anthropic 兼容代理。

下面许多内置提供商插件已经发布了默认目录。
仅当你想覆盖默认基础 URL、请求头或模型列表时，才使用显式 `models.providers.<id>` 条目。

### Moonshot AI（Kimi）

Moonshot 作为内置提供商插件提供。默认请使用内置提供商，仅当你需要覆盖基础 URL 或模型元数据时，才添加显式 `models.providers.moonshot` 条目：

- 提供商：`moonshot`
- 认证：`MOONSHOT_API_KEY`
- 示例模型：`moonshot/kimi-k2.5`
- CLI：`openclaw onboard --auth-choice moonshot-api-key` 或 `openclaw onboard --auth-choice moonshot-api-key-cn`

Kimi K2 模型 ID：

[//]: # "moonshot-kimi-k2-model-refs:start"

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
- `moonshot/kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-model-refs:end"

```json5
{
  agents: {
    defaults: { model: { primary: "moonshot/kimi-k2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5" }],
      },
    },
  },
}
```

### Kimi Coding

Kimi Coding 使用 Moonshot AI 的 Anthropic 兼容端点：

- 提供商：`kimi`
- 认证：`KIMI_API_KEY`
- 示例模型：`kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

旧版 `kimi/k2p5` 仍然作为兼容模型 ID 被接受。

### Volcano Engine（Doubao）

Volcano Engine（火山引擎）为中国用户提供 Doubao 和其他模型的访问。

- 提供商：`volcengine`（编程：`volcengine-plan`）
- 认证：`VOLCANO_ENGINE_API_KEY`
- 示例模型：`volcengine-plan/ark-code-latest`
- CLI：`openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

onboarding 默认使用编程界面，但同时也会注册通用 `volcengine/*` 目录。

在 onboarding/配置模型选择器中，Volcengine 认证选项会优先显示 `volcengine/*` 和 `volcengine-plan/*` 两类条目。如果这些模型尚未加载，OpenClaw 会回退到未过滤的目录，而不是显示一个空的提供商范围选择器。

可用模型：

- `volcengine/doubao-seed-1-8-251228`（Doubao Seed 1.8）
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127`（Kimi K2.5）
- `volcengine/glm-4-7-251222`（GLM 4.7）
- `volcengine/deepseek-v3-2-251201`（DeepSeek V3.2 128K）

编程模型（`volcengine-plan`）：

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus（国际版）

BytePlus ARK 为国际用户提供与 Volcano Engine 相同模型的访问。

- 提供商：`byteplus`（编程：`byteplus-plan`）
- 认证：`BYTEPLUS_API_KEY`
- 示例模型：`byteplus-plan/ark-code-latest`
- CLI：`openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

onboarding 默认使用编程界面，但同时也会注册通用 `byteplus/*` 目录。

在 onboarding/配置模型选择器中，BytePlus 认证选项会优先显示 `byteplus/*` 和 `byteplus-plan/*` 两类条目。如果这些模型尚未加载，OpenClaw 会回退到未过滤的目录，而不是显示一个空的提供商范围选择器。

可用模型：

- `byteplus/seed-1-8-251228`（Seed 1.8）
- `byteplus/kimi-k2-5-260127`（Kimi K2.5）
- `byteplus/glm-4-7-251222`（GLM 4.7）

编程模型（`byteplus-plan`）：

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic 通过 `synthetic` 提供商提供 Anthropic 兼容模型：

- 提供商：`synthetic`
- 认证：`SYNTHETIC_API_KEY`
- 示例模型：`synthetic/hf:MiniMaxAI/MiniMax-M2.5`
- CLI：`openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.5", name: "MiniMax M2.5" }],
      },
    },
  },
}
```

### MiniMax

MiniMax 通过 `models.providers` 配置，因为它使用自定义端点：

- MiniMax OAuth（全球）：`--auth-choice minimax-global-oauth`
- MiniMax OAuth（中国）：`--auth-choice minimax-cn-oauth`
- MiniMax API 密钥（全球）：`--auth-choice minimax-global-api`
- MiniMax API 密钥（中国）：`--auth-choice minimax-cn-api`
- 认证：`MINIMAX_API_KEY` 用于 `minimax`；`MINIMAX_OAUTH_TOKEN` 或 `MINIMAX_API_KEY` 用于 `minimax-portal`

设置详情、模型选项和配置片段请参见 [/providers/minimax](/zh-CN/providers/minimax)。

在 MiniMax 的 Anthropic 兼容流式路径上，OpenClaw 默认禁用 thinking，除非你显式设置它；而 `/fast on` 会将 `MiniMax-M2.7` 重写为 `MiniMax-M2.7-highspeed`。

插件自有能力划分：

- 文本/聊天默认保持在 `minimax/MiniMax-M2.7`
- 图像生成使用 `minimax/image-01` 或 `minimax-portal/image-01`
- 图像理解在两个 MiniMax 认证路径上都使用插件自有的 `MiniMax-VL-01`
- Web 搜索保持在提供商 ID `minimax`

### Ollama

Ollama 作为内置提供商插件提供，并使用 Ollama 原生 API：

- 提供商：`ollama`
- 认证：无需（本地服务器）
- 示例模型：`ollama/llama3.3`
- 安装：[https://ollama.com/download](https://ollama.com/download)

```bash
# 安装 Ollama，然后拉取一个模型：
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

当你通过 `OLLAMA_API_KEY` 选择启用时，Ollama 会在本地 `http://127.0.0.1:11434` 被检测到，内置提供商插件会将 Ollama 直接添加到 `openclaw onboard` 和模型选择器中。关于 onboarding、云端/本地模式和自定义配置，请参见 [/providers/ollama](/zh-CN/providers/ollama)。

### vLLM

vLLM 作为内置提供商插件提供，用于本地/自托管的 OpenAI 兼容服务器：

- 提供商：`vllm`
- 认证：可选（取决于你的服务器）
- 默认基础 URL：`http://127.0.0.1:8000/v1`

要选择启用本地自动发现（如果你的服务器不强制认证，任意值都可以）：

```bash
export VLLM_API_KEY="vllm-local"
```

然后设置一个模型（替换为 `/v1/models` 返回的某个 ID）：

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

详情请参见 [/providers/vllm](/zh-CN/providers/vllm)。

### SGLang

SGLang 作为内置提供商插件提供，用于高速自托管的 OpenAI 兼容服务器：

- 提供商：`sglang`
- 认证：可选（取决于你的服务器）
- 默认基础 URL：`http://127.0.0.1:30000/v1`

要选择启用本地自动发现（如果你的服务器不强制认证，任意值都可以）：

```bash
export SGLANG_API_KEY="sglang-local"
```

然后设置一个模型（替换为 `/v1/models` 返回的某个 ID）：

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

详情请参见 [/providers/sglang](/zh-CN/providers/sglang)。

### 本地代理（LM Studio、vLLM、LiteLLM 等）

示例（OpenAI 兼容）：

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "本地" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "LMSTUDIO_KEY",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "本地模型",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

说明：

- 对于自定义提供商，`reasoning`、`input`、`cost`、`contextWindow` 和 `maxTokens` 都是可选项。
  省略时，OpenClaw 默认值为：
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- 建议：设置与你的代理/模型限制匹配的显式值。
- 对于非原生端点上的 `api: "openai-completions"`（任意非空 `baseUrl`，且其主机不是 `api.openai.com`），OpenClaw 会强制设定 `compat.supportsDeveloperRole: false`，以避免提供商因不支持 `developer` 角色而返回 400 错误。
- 代理式 OpenAI 兼容路由也会跳过原生 OpenAI 专属请求整形：没有 `service_tier`，没有 Responses `store`，没有提示缓存提示，没有 OpenAI 推理兼容负载整形，也没有隐藏的 OpenClaw 归属请求头。
- 如果 `baseUrl` 为空或省略，OpenClaw 会保留默认 OpenAI 行为（解析到 `api.openai.com`）。
- 为了安全，在非原生 `openai-completions` 端点上，显式 `compat.supportsDeveloperRole: true` 仍会被覆盖。

## CLI 示例

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

另请参见：[/gateway/configuration](/zh-CN/gateway/configuration) 了解完整配置示例。

## 相关内容

- [Models](/zh-CN/concepts/models) — 模型配置和别名
- [Model Failover](/zh-CN/concepts/model-failover) — 回退链和重试行为
- [Configuration Reference](/zh-CN/gateway/configuration-reference#agent-defaults) — 模型配置键
- [Providers](/zh-CN/providers) — 各提供商设置指南
