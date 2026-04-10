---
read_when:
    - 你想使用内置的 Codex app-server 测试工具
    - 你需要 Codex 模型引用和配置示例
    - 你想为仅使用 Codex 的部署禁用 PI 回退机制
summary: 通过内置的 Codex app-server 测试工具运行 OpenClaw 嵌入式智能体轮次
title: Codex 测试工具
x-i18n:
    generated_at: "2026-04-10T21:05:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: b1babe5b3498eb2a963f3e66a46975bd261886398499453d0d240e1fbc309bf4
    source_path: plugins/codex-harness.md
    workflow: 15
---

# Codex 测试工具

内置的 `codex` 插件让 OpenClaw 通过 Codex app-server 运行嵌入式智能体轮次，而不是使用内置的 PI 测试工具。

当你希望由 Codex 接管底层智能体会话时使用此功能：模型发现、原生线程恢复、原生压缩，以及 app-server 执行。OpenClaw 仍然负责聊天渠道、会话文件、模型选择、工具、审批、媒体传输，以及可见的对话记录镜像。

该测试工具默认关闭。只有在启用 `codex` 插件且解析后的模型是 `codex/*` 模型时，或者你显式强制设置 `embeddedHarness.runtime: "codex"` 或 `OPENCLAW_AGENT_RUNTIME=codex` 时，才会选用它。如果你从不配置 `codex/*`，现有的 PI、OpenAI、Anthropic、Gemini、本地和自定义提供商运行方式都会保持当前行为。

## 选择正确的模型前缀

OpenClaw 为 OpenAI 和 Codex 风格的访问提供了不同的路由：

| 模型引用               | 运行时路径                                   | 适用场景                                                                |
| ---------------------- | -------------------------------------------- | ----------------------------------------------------------------------- |
| `openai/gpt-5.4`       | 通过 OpenClaw/PI 管道的 OpenAI 提供商路径    | 你希望使用 `OPENAI_API_KEY` 直接访问 OpenAI Platform API。              |
| `openai-codex/gpt-5.4` | 通过 PI 的 OpenAI Codex OAuth 提供商路径     | 你希望使用 ChatGPT/Codex OAuth，但不使用 Codex app-server 测试工具。    |
| `codex/gpt-5.4`        | 内置 Codex 提供商 + Codex 测试工具           | 你希望在嵌入式智能体轮次中使用原生 Codex app-server 执行。              |

Codex 测试工具只接管 `codex/*` 模型引用。现有的 `openai/*`、`openai-codex/*`、Anthropic、Gemini、xAI、本地和自定义提供商引用都会继续走各自的正常路径。

## 要求

- OpenClaw，且内置的 `codex` 插件可用。
- Codex app-server `0.118.0` 或更高版本。
- app-server 进程可用的 Codex 认证信息。

该插件会阻止较旧版本或未带版本信息的 app-server 握手。这可确保 OpenClaw 始终运行在它已测试过的协议接口上。

对于实时测试和 Docker 冒烟测试，认证通常来自 `OPENAI_API_KEY`，以及可选的 Codex CLI 文件，例如 `~/.codex/auth.json` 和 `~/.codex/config.toml`。请使用与你本地 Codex app-server 相同的认证材料。

## 最小配置

使用 `codex/gpt-5.4`，启用内置插件，并强制使用 `codex` 测试工具：

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

如果你的配置使用了 `plugins.allow`，也请将 `codex` 包含进去：

```json5
{
  plugins: {
    allow: ["codex"],
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

将 `agents.defaults.model` 或某个智能体模型设置为 `codex/<model>` 也会自动启用内置的 `codex` 插件。显式添加插件条目在共享配置中仍然很有用，因为它能让部署意图更清晰。

## 在不替换其他模型的情况下添加 Codex

如果你希望 `codex/*` 模型使用 Codex，而其他所有模型仍使用 PI，请保持 `runtime: "auto"`：

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: {
        primary: "codex/gpt-5.4",
        fallbacks: ["openai/gpt-5.4", "anthropic/claude-opus-4-6"],
      },
      models: {
        "codex/gpt-5.4": { alias: "codex" },
        "codex/gpt-5.4-mini": { alias: "codex-mini" },
        "openai/gpt-5.4": { alias: "gpt" },
        "anthropic/claude-opus-4-6": { alias: "opus" },
      },
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
  },
}
```

采用这种配置后：

- `/model codex` 或 `/model codex/gpt-5.4` 会使用 Codex app-server 测试工具。
- `/model gpt` 或 `/model openai/gpt-5.4` 会使用 OpenAI 提供商路径。
- `/model opus` 会使用 Anthropic 提供商路径。
- 如果选择的是非 Codex 模型，PI 仍然是兼容性测试工具。

## 仅使用 Codex 的部署

如果你需要证明每个嵌入式智能体轮次都使用 Codex 测试工具，请禁用 PI 回退：

```json5
{
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

环境变量覆盖：

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

禁用回退后，如果 Codex 插件被禁用、请求的模型不是 `codex/*` 引用、app-server 版本过旧，或者 app-server 无法启动，OpenClaw 都会尽早失败。

## 按智能体使用 Codex

你可以让某一个智能体仅使用 Codex，而默认智能体继续保持正常的自动选择：

```json5
{
  agents: {
    defaults: {
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
    list: [
      {
        id: "main",
        default: true,
        model: "anthropic/claude-opus-4-6",
      },
      {
        id: "codex",
        name: "Codex",
        model: "codex/gpt-5.4",
        embeddedHarness: {
          runtime: "codex",
          fallback: "none",
        },
      },
    ],
  },
}
```

使用常规会话命令切换智能体和模型。`/new` 会创建一个新的 OpenClaw 会话，而 Codex 测试工具会按需创建或恢复它对应的 sidecar app-server 线程。`/reset` 会清除该线程的 OpenClaw 会话绑定。

## 模型发现

默认情况下，Codex 插件会向 app-server 请求可用模型。如果发现失败或超时，它会使用内置的回退目录：

- `codex/gpt-5.4`
- `codex/gpt-5.4-mini`
- `codex/gpt-5.2`

你可以在 `plugins.entries.codex.config.discovery` 下调整发现行为：

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: true,
            timeoutMs: 2500,
          },
        },
      },
    },
  },
}
```

如果你希望启动时避免探测 Codex，并始终使用回退目录，可以禁用发现：

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: false,
          },
        },
      },
    },
  },
}
```

## 工具、媒体和压缩

Codex 测试工具只会改变底层嵌入式智能体执行器。

OpenClaw 仍然会构建工具列表，并从测试工具接收动态工具结果。文本、图像、视频、音乐、TTS、审批以及消息工具输出，都会继续通过正常的 OpenClaw 传输路径处理。

当所选模型使用 Codex 测试工具时，原生线程压缩会委托给 Codex app-server。OpenClaw 会保留一份对话记录镜像，用于渠道历史、搜索、`/new`、`/reset`，以及未来的模型或测试工具切换。

媒体生成不依赖 PI。图像、视频、音乐、PDF、TTS 和媒体理解仍会继续使用匹配的提供商/模型设置，例如 `agents.defaults.imageGenerationModel`、`videoGenerationModel`、`pdfModel` 和 `messages.tts`。

## 故障排除

**Codex 没有出现在 `/model` 中：** 启用 `plugins.entries.codex.enabled`，设置一个 `codex/*` 模型引用，或检查 `plugins.allow` 是否排除了 `codex`。

**OpenClaw 回退到 PI：** 在测试时设置 `embeddedHarness.fallback: "none"` 或 `OPENCLAW_AGENT_HARNESS_FALLBACK=none`。

**app-server 被拒绝：** 升级 Codex，使 app-server 握手报告的版本为 `0.118.0` 或更高。

**模型发现速度很慢：** 降低 `plugins.entries.codex.config.discovery.timeoutMs`，或禁用发现。

**某个非 Codex 模型使用了 PI：** 这是预期行为。Codex 测试工具只接管 `codex/*` 模型引用。

## 相关内容

- [智能体测试工具插件](/zh-CN/plugins/sdk-agent-harness)
- [模型提供商](/zh-CN/concepts/model-providers)
- [配置参考](/zh-CN/gateway/configuration-reference)
- [测试](/zh-CN/help/testing#live-codex-app-server-harness-smoke)
