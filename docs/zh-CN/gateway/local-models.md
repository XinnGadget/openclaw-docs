---
read_when:
    - 你想从你自己的 GPU 机器提供模型服务
    - 你正在连接 LM Studio 或兼容 OpenAI 的代理
    - 你需要最安全的本地模型使用指南
summary: 在本地 LLM（LM Studio、vLLM、LiteLLM、自定义 OpenAI 端点）上运行 OpenClaw
title: 本地模型
x-i18n:
    generated_at: "2026-04-15T10:48:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7a506ff83e4c2870d3878339f646c906584454a156ecd618c360f592cf3b0011
    source_path: gateway/local-models.md
    workflow: 15
---

# 本地模型

本地部署是可行的，但 OpenClaw 需要大上下文窗口以及强有力的提示注入防护。小显存显卡会截断上下文，并削弱安全性。目标配置应尽量高：**至少 2 台满配 Mac Studio 或同等级别的 GPU 设备（约 3 万美元以上）**。单张 **24 GB** GPU 仅适用于较轻的提示，并且延迟会更高。尽量使用**你能运行的最大 / 全尺寸模型变体**；激进量化或“小型”检查点会提高提示注入风险（参见 [Security](/zh-CN/gateway/security)）。

如果你想要摩擦最低的本地配置方式，建议从 [LM Studio](/zh-CN/providers/lmstudio) 或 [Ollama](/zh-CN/providers/ollama) 配合 `openclaw onboard` 开始。本页是面向更高端本地方案以及自定义兼容 OpenAI 的本地服务器的偏好指南。

## 推荐：LM Studio + 大型本地模型（Responses API）

这是当前最推荐的本地方案。在 LM Studio 中加载一个大型模型（例如全尺寸的 Qwen、DeepSeek 或 Llama 构建），启用本地服务器（默认是 `http://127.0.0.1:1234`），并使用 Responses API 将推理过程与最终文本分离。

```json5
{
  agents: {
    defaults: {
      model: { primary: “lmstudio/my-local-model” },
      models: {
        “anthropic/claude-opus-4-6”: { alias: “Opus” },
        “lmstudio/my-local-model”: { alias: “Local” },
      },
    },
  },
  models: {
    mode: “merge”,
    providers: {
      lmstudio: {
        baseUrl: “http://127.0.0.1:1234/v1”,
        apiKey: “lmstudio”,
        api: “openai-responses”,
        models: [
          {
            id: “my-local-model”,
            name: “Local Model”,
            reasoning: false,
            input: [“text”],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**设置检查清单**

- 安装 LM Studio：[https://lmstudio.ai](https://lmstudio.ai)
- 在 LM Studio 中，下载**可用的最大模型构建版本**（避免使用 “small”/重度量化变体），启动服务器，并确认 `http://127.0.0.1:1234/v1/models` 能列出该模型。
- 将 `my-local-model` 替换为 LM Studio 中显示的实际模型 ID。
- 保持模型处于已加载状态；冷启动加载会增加启动延迟。
- 如果你的 LM Studio 构建不同，请调整 `contextWindow`/`maxTokens`。
- 对于 WhatsApp，建议坚持使用 Responses API，这样只会发送最终文本。

即使你在运行本地模型，也建议保留托管模型配置；使用 `models.mode: "merge"`，这样回退模型仍然可用。

### 混合配置：托管模型为主，本地模型为回退

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["lmstudio/my-local-model", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "lmstudio/my-local-model": { alias: "Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### 本地优先，并保留托管安全兜底

交换 primary 和 fallback 的顺序即可；保留相同的 providers 配置块以及 `models.mode: "merge"`，这样当本地设备不可用时，你仍可回退到 Sonnet 或 Opus。

### 区域托管 / 数据路由

- 托管的 MiniMax/Kimi/GLM 变体也可通过 OpenRouter 使用带区域锁定的端点（例如美国托管）。你可以在那里选择区域版本，在使用 `models.mode: "merge"` 的同时保留 Anthropic/OpenAI 回退模型，并将流量限制在你选择的司法辖区内。
- 纯本地仍然是隐私性最强的路径；如果你需要提供商特性但又想控制数据流向，那么托管的区域路由是中间方案。

## 其他兼容 OpenAI 的本地代理

vLLM、LiteLLM、OAI-proxy 或自定义 Gateway 网关 只要暴露兼容 OpenAI 风格的 `/v1` 端点即可使用。将上面的 provider 配置块替换为你的端点和模型 ID：

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

保留 `models.mode: "merge"`，这样托管模型仍可作为回退使用。

关于本地 / 代理 `/v1` 后端的行为说明：

- OpenClaw 会将这些后端视为代理风格的兼容 OpenAI 路由，而不是原生 OpenAI 端点
- 仅适用于原生 OpenAI 的请求整形不会在这里生效：没有 `service_tier`、没有 Responses `store`、没有 OpenAI reasoning 兼容载荷整形，也没有提示缓存提示
- 隐藏的 OpenClaw 归因请求头（`originator`、`version`、`User-Agent`）不会注入到这些自定义代理 URL 中

针对更严格的兼容 OpenAI 后端的兼容性说明：

- 某些服务器在 Chat Completions 中只接受字符串类型的 `messages[].content`，而不接受结构化的内容片段数组。对于这些端点，请设置 `models.providers.<provider>.models[].compat.requiresStringContent: true`。
- 某些更小型或更严格的本地后端在面对 OpenClaw 完整的智能体运行时提示结构时会不稳定，尤其是在包含工具 schema 时。如果后端能处理很小的直接 `/v1/chat/completions` 调用，却无法处理正常的 OpenClaw 智能体轮次，请先尝试设置 `agents.defaults.experimental.localModelLean: true`，以移除 `browser`、`cron` 和 `message` 等重量级默认工具；这是实验性标志，不是稳定默认模式设置。参见 [Experimental Features](/zh-CN/concepts/experimental-features)。如果仍然失败，再尝试 `models.providers.<provider>.models[].compat.supportsTools: false`。
- 如果后端仍然只会在较大的 OpenClaw 运行中失败，剩余问题通常是上游模型 / 服务器容量不足，或后端本身存在 bug，而不是 OpenClaw 的传输层问题。

## 故障排除

- Gateway 网关 能访问代理吗？`curl http://127.0.0.1:1234/v1/models`
- LM Studio 模型未加载？重新加载；冷启动是常见的“卡住”原因。
- 当检测到的上下文窗口低于 **32k** 时，OpenClaw 会发出警告；低于 **16k** 时会直接阻止运行。如果你遇到这个预检，请提高服务器 / 模型的上下文限制，或选择更大的模型。
- 上下文报错？降低 `contextWindow` 或提高你的服务器限制。
- 兼容 OpenAI 的服务器返回 `messages[].content ... expected a string`？
  请在该模型项中添加 `compat.requiresStringContent: true`。
- 很小的直接 `/v1/chat/completions` 调用可以工作，但 `openclaw infer model run` 在 Gemma 或其他本地模型上失败？先通过 `compat.supportsTools: false` 禁用工具 schema，然后重新测试。如果服务器仍然只会在较大的 OpenClaw 提示下崩溃，就应将其视为上游服务器 / 模型限制。
- 安全性：本地模型会跳过提供商侧过滤；请保持智能体职责收窄，并开启 compaction，以限制提示注入的影响范围。
