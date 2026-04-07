---
read_when:
    - 你想从你自己的 GPU 主机提供模型
    - 你正在连接 LM Studio 或兼容 OpenAI 的代理
    - 你需要最安全的本地模型指导
summary: 在本地 LLM 上运行 OpenClaw（LM Studio、vLLM、LiteLLM、自定义 OpenAI 端点）
title: 本地模型
x-i18n:
    generated_at: "2026-04-07T14:57:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: d619d72b0e06914ebacb7e9f38b746caf1b9ce8908c9c6638c3acdddbaa025e8
    source_path: gateway/local-models.md
    workflow: 15
---

# 本地模型

本地部署是可行的，但 OpenClaw 需要大上下文窗口以及对提示注入的强防护。小显卡会截断上下文并削弱安全性。尽量配置更高：**≥2 台满配 Mac Studio 或同等 GPU 主机（约 3 万美元以上）**。单张 **24 GB** GPU 只适用于较轻的提示词，而且延迟更高。使用**你能运行的最大 / 完整尺寸模型变体**；激进量化或“小型”检查点会提高提示注入风险（参见[安全](/zh-CN/gateway/security)）。

如果你想要最低摩擦的本地配置，先从 [Ollama](/zh-CN/providers/ollama) 和 `openclaw onboard` 开始。本页是面向更高端本地栈和自定义兼容 OpenAI 的本地服务器的推荐指南。

## 推荐：LM Studio + 大型本地模型（Responses API）

这是当前最推荐的本地方案。在 LM Studio 中加载一个大型模型（例如完整尺寸的 Qwen、DeepSeek 或 Llama 构建），启用本地服务器（默认 `http://127.0.0.1:1234`），并使用 Responses API 将推理内容与最终文本分离。

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

**设置清单**

- 安装 LM Studio：[https://lmstudio.ai](https://lmstudio.ai)
- 在 LM Studio 中，下载**可用的最大模型构建**（避免“小型”/重度量化变体），启动服务器，并确认 `http://127.0.0.1:1234/v1/models` 已列出该模型。
- 将 `my-local-model` 替换为 LM Studio 中显示的实际模型 ID。
- 保持模型处于已加载状态；冷加载会增加启动延迟。
- 如果你的 LM Studio 构建不同，请调整 `contextWindow` / `maxTokens`。
- 对于 WhatsApp，坚持使用 Responses API，这样只会发送最终文本。

即使在本地运行，也请保留托管模型配置；使用 `models.mode: "merge"`，这样回退模型仍然可用。

### 混合配置：托管模型为主，本地模型回退

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

### 本地优先，托管模型作安全兜底

交换 primary 和 fallback 的顺序；保留相同的 providers 配置块以及 `models.mode: "merge"`，这样当本地主机不可用时，你仍然可以回退到 Sonnet 或 Opus。

### 区域托管 / 数据路由

- 托管版的 MiniMax / Kimi / GLM 变体也可通过 OpenRouter 的区域固定端点提供（例如托管在美国的端点）。你可以在那里选择区域变体，使流量保留在你指定的司法辖区内，同时仍然使用 `models.mode: "merge"` 作为 Anthropic / OpenAI 的回退。
- 纯本地仍然是隐私性最强的方案；当你需要提供商功能，但又希望控制数据流向时，区域托管路由是折中方案。

## 其他兼容 OpenAI 的本地代理

只要 vLLM、LiteLLM、OAI-proxy 或自定义 Gateway 网关 暴露的是兼容 OpenAI 风格的 `/v1` 端点，就可以使用。将上面的 provider 配置块替换为你的端点和模型 ID：

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

保留 `models.mode: "merge"`，这样托管模型仍然可以作为回退使用。

关于本地 / 代理 `/v1` 后端的行为说明：

- OpenClaw 将这些视为代理风格的兼容 OpenAI 路由，而不是原生
  OpenAI 端点
- 仅适用于原生 OpenAI 的请求整形不会在这里生效：没有
  `service_tier`，没有 Responses `store`，没有 OpenAI 推理兼容负载
  整形，也没有提示缓存提示
- 隐藏的 OpenClaw 归因头（`originator`、`version`、`User-Agent`）
  不会注入到这些自定义代理 URL 上

对于更严格的兼容 OpenAI 后端的兼容性说明：

- 某些服务器在 Chat Completions 中只接受字符串类型的 `messages[].content`，而不接受
  结构化的内容片段数组。对于这类端点，请设置
  `models.providers.<provider>.models[].compat.requiresStringContent: true`。
- 某些更小型或更严格的本地后端无法稳定处理 OpenClaw 完整的
  智能体运行时提示结构，尤其是在包含工具 schema 时。如果该
  后端可以处理很小的直接 `/v1/chat/completions` 调用，但在正常
  OpenClaw 智能体轮次中失败，请先尝试设置
  `models.providers.<provider>.models[].compat.supportsTools: false`。
- 如果后端仅在更大的 OpenClaw 运行中仍然失败，剩余问题通常
  是上游模型 / 服务器容量不足，或后端自身的 bug，而不是 OpenClaw 的
  传输层问题。

## 故障排除

- Gateway 网关 能连接到代理吗？`curl http://127.0.0.1:1234/v1/models`。
- LM Studio 模型被卸载了？重新加载；冷启动是常见的“卡住”原因。
- 上下文报错？降低 `contextWindow` 或提高你的服务器限制。
- 兼容 OpenAI 的服务器返回 `messages[].content ... expected a string`？
  在该模型条目上添加 `compat.requiresStringContent: true`。
- 直接的小型 `/v1/chat/completions` 调用可以工作，但 `openclaw infer model run`
  在 Gemma 或其他本地模型上失败？先使用
  `compat.supportsTools: false` 禁用工具 schema，然后重新测试。如果服务器仍然只在
  更大的 OpenClaw 提示上崩溃，请将其视为上游服务器 / 模型限制。
- 安全性：本地模型会跳过提供商侧过滤；请保持智能体范围收窄，并启用压缩，以限制提示注入的影响范围。
