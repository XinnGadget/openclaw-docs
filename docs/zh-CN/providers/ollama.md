---
read_when:
    - 你想通过 Ollama 使用云端或本地模型运行 OpenClaw
    - 你需要 Ollama 的安装与配置指南
summary: 使用 Ollama（云端和本地模型）运行 OpenClaw
title: Ollama
x-i18n:
    generated_at: "2026-04-07T19:39:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 222ec68f7d4bb29cc7796559ddef1d5059f5159e7a51e2baa3a271ddb3abb716
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

Ollama 是一个本地 LLM 运行时，让你可以轻松在自己的设备上运行开源模型。OpenClaw 集成了 Ollama 的原生 API（`/api/chat`），支持流式传输和工具调用，并且当你选择启用 `OLLAMA_API_KEY`（或凭证配置）且未定义显式的 `models.providers.ollama` 条目时，它可以自动发现本地 Ollama 模型。

<Warning>
**远程 Ollama 用户**：不要在 OpenClaw 中使用 `/v1` 的 OpenAI 兼容 URL（`http://host:11434/v1`）。这会破坏工具调用，模型还可能把原始工具 JSON 当作纯文本输出。请改用原生 Ollama API URL：`baseUrl: "http://host:11434"`（不要加 `/v1`）。
</Warning>

## 快速开始

### 新手引导（推荐）

设置 Ollama 的最快方式是通过新手引导：

```bash
openclaw onboard
```

从提供商列表中选择 **Ollama**。新手引导将会：

1. 询问你的 Ollama 基础 URL，即你的实例可访问的地址（默认是 `http://127.0.0.1:11434`）。
2. 让你选择 **Cloud + Local**（云端模型和本地模型）或 **Local**（仅本地模型）。
3. 如果你选择 **Cloud + Local** 且尚未登录 ollama.com，则打开浏览器登录流程。
4. 发现可用模型并推荐默认值。
5. 如果所选模型在本地不可用，则自动拉取该模型。

也支持非交互模式：

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --accept-risk
```

你也可以选择指定自定义基础 URL 或模型：

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --custom-base-url "http://ollama-host:11434" \
  --custom-model-id "qwen3.5:27b" \
  --accept-risk
```

### 手动设置

1. 安装 Ollama：[https://ollama.com/download](https://ollama.com/download)

2. 如果你想使用本地推理，先拉取一个本地模型：

```bash
ollama pull gemma4
# 或
ollama pull gpt-oss:20b
# 或
ollama pull llama3.3
```

3. 如果你也想使用云端模型，请先登录：

```bash
ollama signin
```

4. 运行新手引导并选择 `Ollama`：

```bash
openclaw onboard
```

- `Local`：仅本地模型
- `Cloud + Local`：本地模型加云端模型
- `kimi-k2.5:cloud`、`minimax-m2.7:cloud` 和 `glm-5.1:cloud` 这类云端模型 **不需要** 在本地执行 `ollama pull`

OpenClaw 当前推荐：

- 本地默认：`gemma4`
- 云端默认：`kimi-k2.5:cloud`、`minimax-m2.7:cloud`、`glm-5.1:cloud`

5. 如果你更喜欢手动设置，也可以直接为 OpenClaw 启用 Ollama（任意值都可以；Ollama 不要求真实密钥）：

```bash
# 设置环境变量
export OLLAMA_API_KEY="ollama-local"

# 或在配置文件中设置
openclaw config set models.providers.ollama.apiKey "ollama-local"
```

6. 查看或切换模型：

```bash
openclaw models list
openclaw models set ollama/gemma4
```

7. 或者在配置中设置默认模型：

```json5
{
  agents: {
    defaults: {
      model: { primary: "ollama/gemma4" },
    },
  },
}
```

## 模型发现（隐式提供商）

当你设置了 `OLLAMA_API_KEY`（或凭证配置），并且**没有**定义 `models.providers.ollama` 时，OpenClaw 会从位于 `http://127.0.0.1:11434` 的本地 Ollama 实例发现模型：

- 查询 `/api/tags`
- 尽力使用 `/api/show` 查询来读取 `contextWindow`（如果可用）
- 使用模型名称启发式规则标记 `reasoning`（`r1`、`reasoning`、`think`）
- 将 `maxTokens` 设置为 OpenClaw 使用的默认 Ollama 最大 token 上限
- 将所有成本设为 `0`

这样无需手动填写模型条目，同时还能让模型目录与本地 Ollama 实例保持一致。

如需查看有哪些可用模型：

```bash
ollama list
openclaw models list
```

要添加新模型，只需使用 Ollama 拉取它：

```bash
ollama pull mistral
```

新模型会被自动发现并可立即使用。

如果你显式设置了 `models.providers.ollama`，则会跳过自动发现，你必须手动定义模型（见下文）。

## 配置

### 基本设置（隐式发现）

启用 Ollama 的最简单方式是通过环境变量：

```bash
export OLLAMA_API_KEY="ollama-local"
```

### 显式设置（手动模型）

以下情况请使用显式配置：

- Ollama 运行在其他主机或端口上。
- 你想强制指定特定的上下文窗口或模型列表。
- 你想完全手动定义模型。

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434",
        apiKey: "ollama-local",
        api: "ollama",
        models: [
          {
            id: "gpt-oss:20b",
            name: "GPT-OSS 20B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 8192,
            maxTokens: 8192 * 10
          }
        ]
      }
    }
  }
}
```

如果设置了 `OLLAMA_API_KEY`，你可以在提供商条目中省略 `apiKey`，OpenClaw 会自动补上它以进行可用性检查。

### 自定义基础 URL（显式配置）

如果 Ollama 运行在不同的主机或端口上（显式配置会禁用自动发现，因此你需要手动定义模型）：

```json5
{
  models: {
    providers: {
      ollama: {
        apiKey: "ollama-local",
        baseUrl: "http://ollama-host:11434", // 不要加 /v1 - 使用原生 Ollama API URL
        api: "ollama", // 显式设置以确保使用原生工具调用行为
      },
    },
  },
}
```

<Warning>
不要在 URL 中添加 `/v1`。`/v1` 路径使用 OpenAI 兼容模式，而该模式下工具调用并不可靠。请使用不带路径后缀的 Ollama 基础 URL。
</Warning>

### 模型选择

完成配置后，你的所有 Ollama 模型都会可用：

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## 云端模型

云端模型让你可以在本地模型之外，再使用云端托管模型（例如 `kimi-k2.5:cloud`、`minimax-m2.7:cloud`、`glm-5.1:cloud`）。

要使用云端模型，请在设置过程中选择 **Cloud + Local** 模式。向导会检查你是否已登录，并在需要时打开浏览器登录流程。如果无法验证身份，向导会回退到本地模型默认值。

你也可以直接在 [ollama.com/signin](https://ollama.com/signin) 登录。

## Ollama Web 搜索

OpenClaw 还支持将 **Ollama Web 搜索** 作为内置的 `web_search`
提供商使用。

- 它会使用你配置的 Ollama 主机（设置了 `models.providers.ollama.baseUrl` 时使用该值，否则使用 `http://127.0.0.1:11434`）。
- 它不需要密钥。
- 它要求 Ollama 正在运行，并且你已经通过 `ollama signin` 登录。

你可以在 `openclaw onboard` 或
`openclaw configure --section web` 期间选择 **Ollama Web 搜索**，或设置：

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

完整设置和行为详情，请参阅 [Ollama Web 搜索](/zh-CN/tools/ollama-search)。

## 高级

### 推理模型

OpenClaw 默认会将名称中包含 `deepseek-r1`、`reasoning` 或 `think` 的模型视为具备推理能力：

```bash
ollama pull deepseek-r1:32b
```

### 模型成本

Ollama 是免费的，并且在本地运行，因此所有模型成本都设置为 $0。

### 流式传输配置

OpenClaw 的 Ollama 集成默认使用**原生 Ollama API**（`/api/chat`），可同时完整支持流式传输和工具调用。无需额外配置。

#### 旧版 OpenAI 兼容模式

<Warning>
**在 OpenAI 兼容模式下，工具调用并不可靠。** 只有在你需要通过代理使用 OpenAI 格式，且不依赖原生工具调用行为时，才应使用此模式。
</Warning>

如果你确实需要改用 OpenAI 兼容端点（例如在仅支持 OpenAI 格式的代理之后），请显式设置 `api: "openai-completions"`：

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: true, // 默认值：true
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

此模式可能不支持同时进行流式传输 + 工具调用。你可能需要在模型配置中使用 `params: { streaming: false }` 来禁用流式传输。

当 `api: "openai-completions"` 与 Ollama 一起使用时，OpenClaw 默认会注入 `options.num_ctx`，以防止 Ollama 悄悄回退到 4096 的上下文窗口。如果你的代理或上游拒绝未知的 `options` 字段，请禁用此行为：

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: false,
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

### 上下文窗口

对于自动发现的模型，OpenClaw 会在 Ollama 提供相关信息时使用其报告的上下文窗口；否则会回退到 OpenClaw 使用的默认 Ollama 上下文窗口。你可以在显式提供商配置中覆盖 `contextWindow` 和 `maxTokens`。

## 故障排除

### 未检测到 Ollama

请确认 Ollama 正在运行，并且你已设置 `OLLAMA_API_KEY`（或凭证配置），同时**没有**定义显式的 `models.providers.ollama` 条目：

```bash
ollama serve
```

同时确认 API 可访问：

```bash
curl http://localhost:11434/api/tags
```

### 没有可用模型

如果你的模型未列出，可以：

- 在本地拉取该模型，或
- 在 `models.providers.ollama` 中显式定义该模型。

添加模型的方法：

```bash
ollama list  # 查看已安装的模型
ollama pull gemma4
ollama pull gpt-oss:20b
ollama pull llama3.3     # 或其他模型
```

### 连接被拒绝

请检查 Ollama 是否运行在正确的端口上：

```bash
# 检查 Ollama 是否正在运行
ps aux | grep ollama

# 或重启 Ollama
ollama serve
```

## 另请参阅

- [模型提供商](/zh-CN/concepts/model-providers) - 所有提供商的概览
- [模型选择](/zh-CN/concepts/models) - 如何选择模型
- [配置](/zh-CN/gateway/configuration) - 完整的配置参考
