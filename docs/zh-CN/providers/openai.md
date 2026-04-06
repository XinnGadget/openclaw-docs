---
read_when:
    - 你想在 OpenClaw 中使用 OpenAI 模型
    - 你想使用 Codex 订阅认证而不是 API 密钥
summary: 通过 API 密钥或 Codex 订阅在 OpenClaw 中使用 OpenAI
title: OpenAI
x-i18n:
    generated_at: "2026-04-06T00:04:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: d9a024b102f24a2f690efdbe633a01fbe00f500a74a8007af3245b8b948394ef
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI 为 GPT 模型提供开发者 API。Codex 支持使用 **ChatGPT 登录** 进行订阅访问，或使用 **API 密钥** 登录进行按量计费访问。Codex cloud 需要使用 ChatGPT 登录。
OpenAI 明确支持在 OpenClaw 这类外部工具/工作流中使用订阅 OAuth。

## 默认交互风格

OpenClaw 可以为 `openai/*` 和
`openai-codex/*` 运行添加一个小型的 OpenAI 专用提示词叠加层。默认情况下，这个叠加层会让助手保持更温暖、
更具协作性、更简洁、更直接，并带有稍强一点的情感表达，
同时不会替换 OpenClaw 的基础系统提示词。这个友好的叠加层还
允许在自然合适的情况下偶尔使用 emoji，同时保持整体
输出简洁。

配置键：

`plugins.entries.openai.config.personality`

允许的值：

- `"friendly"`：默认；启用 OpenAI 专用叠加层。
- `"off"`：禁用叠加层，仅使用基础 OpenClaw 提示词。

作用范围：

- 适用于 `openai/*` 模型。
- 适用于 `openai-codex/*` 模型。
- 不影响其他提供商。

此行为默认启用。如果你希望它在未来本地配置变动后
仍然保留，请显式保留 `"friendly"`：

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "friendly",
        },
      },
    },
  },
}
```

### 禁用 OpenAI 提示词叠加层

如果你想使用未修改的基础 OpenClaw 提示词，请将叠加层设置为 `"off"`：

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "off",
        },
      },
    },
  },
}
```

你也可以直接使用配置 CLI 设置：

```bash
openclaw config set plugins.entries.openai.config.personality off
```

## 选项 A：OpenAI API 密钥（OpenAI Platform）

**最适合：** 直接 API 访问和按量计费。
请从 OpenAI 控制台获取你的 API 密钥。

### CLI 设置

```bash
openclaw onboard --auth-choice openai-api-key
# 或非交互方式
openclaw onboard --openai-api-key "$OPENAI_API_KEY"
```

### 配置片段

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

OpenAI 当前的 API 模型文档列出了 `gpt-5.4` 和 `gpt-5.4-pro` 供直接
OpenAI API 使用。OpenClaw 通过 `openai/*` Responses 路径转发这两个模型。
OpenClaw 会有意隐藏过时的 `openai/gpt-5.3-codex-spark` 条目，
因为直接 OpenAI API 调用在真实流量中会拒绝它。

OpenClaw **不会** 在直接 OpenAI
API 路径中暴露 `openai/gpt-5.3-codex-spark`。`pi-ai` 仍然为该模型内置了一个条目，但真实 OpenAI API
请求目前会拒绝它。在 OpenClaw 中，Spark 被视为仅限 Codex。

## 图像生成

内置的 `openai` 插件还通过共享的
`image_generate` 工具注册了图像生成功能。

- 默认图像模型：`openai/gpt-image-1`
- 生成：每次请求最多 4 张图像
- 编辑模式：已启用，最多支持 5 张参考图像
- 支持 `size`
- 当前 OpenAI 专有限制：OpenClaw 目前不会将 `aspectRatio` 或
  `resolution` 覆盖值转发到 OpenAI Images API

要将 OpenAI 用作默认图像提供商：

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
      },
    },
  },
}
```

有关共享工具参数、提供商选择和故障切换行为，请参阅 [图像生成](/zh-CN/tools/image-generation)。

## 视频生成

内置的 `openai` 插件还通过共享的
`video_generate` 工具注册了视频生成功能。

- 默认视频模型：`openai/sora-2`
- 模式：文生视频、图生视频，以及单视频参考/编辑流程
- 当前限制：仅支持 1 张图像或 1 段视频作为参考输入
- 当前 OpenAI 专有限制：OpenClaw 目前仅会为原生 OpenAI 视频生成转发 `size`
  覆盖值。不受支持的可选覆盖值
  如 `aspectRatio`、`resolution`、`audio` 和 `watermark` 会被忽略，
  并作为工具警告返回。

要将 OpenAI 用作默认视频提供商：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "openai/sora-2",
      },
    },
  },
}
```

有关共享工具参数、提供商选择和故障切换行为，请参阅 [视频生成](/zh-CN/tools/video-generation)。

## 选项 B：OpenAI Code（Codex）订阅

**最适合：** 使用 ChatGPT/Codex 订阅访问，而不是 API 密钥。
Codex cloud 需要使用 ChatGPT 登录，而 Codex CLI 支持使用 ChatGPT 或 API 密钥登录。

### CLI 设置（Codex OAuth）

```bash
# 在向导中运行 Codex OAuth
openclaw onboard --auth-choice openai-codex

# 或直接运行 OAuth
openclaw models auth login --provider openai-codex
```

### 配置片段（Codex 订阅）

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

OpenAI 当前的 Codex 文档将 `gpt-5.4` 列为当前的 Codex 模型。OpenClaw
将其映射为 `openai-codex/gpt-5.4`，用于 ChatGPT/Codex OAuth 访问。

如果新手引导复用了现有的 Codex CLI 登录，这些凭证将继续
由 Codex CLI 管理。凭证过期时，OpenClaw 会优先重新读取外部 Codex 来源，
并且当该提供商能够刷新它时，会把刷新的凭证写回
Codex 存储，而不是在单独的仅 OpenClaw 副本中接管管理。

如果你的 Codex 账户有资格使用 Codex Spark，OpenClaw 还支持：

- `openai-codex/gpt-5.3-codex-spark`

OpenClaw 将 Codex Spark 视为仅限 Codex。它不会暴露直接的
`openai/gpt-5.3-codex-spark` API 密钥路径。

当 `pi-ai`
发现 `openai-codex/gpt-5.3-codex-spark` 时，OpenClaw 也会保留它。请将其视为依赖资格且带有实验性质：Codex Spark
独立于 GPT-5.4 `/fast`，是否可用取决于当前登录的 Codex /
ChatGPT 账户。

### Codex 上下文窗口上限

OpenClaw 将 Codex 模型元数据和运行时上下文上限视为两个独立的
值。

对于 `openai-codex/gpt-5.4`：

- 原生 `contextWindow`：`1050000`
- 默认运行时 `contextTokens` 上限：`272000`

这样既能保持模型元数据真实准确，又能保留实践中在延迟和质量方面表现更好的较小默认运行时窗口。

如果你想使用不同的实际上限，请设置 `models.providers.<provider>.models[].contextTokens`：

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [
          {
            id: "gpt-5.4",
            contextTokens: 160000,
          },
        ],
      },
    },
  },
}
```

仅当你在声明或覆盖原生模型
元数据时，才使用 `contextWindow`。当你想限制运行时上下文预算时，请使用 `contextTokens`。

### 传输默认值

OpenClaw 使用 `pi-ai` 进行模型流式传输。对于 `openai/*` 和
`openai-codex/*`，默认传输方式为 `"auto"`（优先 WebSocket，然后回退到 SSE）。

在 `"auto"` 模式下，OpenClaw 还会在回退到 SSE 之前，
对一次发生在早期且可重试的 WebSocket 故障进行重试。
强制使用 `"websocket"` 模式时，传输错误会直接暴露出来，而不会被回退机制掩盖。

在 `"auto"` 模式下，如果连接阶段或会话早期轮次发生 WebSocket 故障，OpenClaw 会将
该会话的 WebSocket 路径标记为降级状态，持续约 60 秒，并在冷却期间通过 SSE 发送
后续轮次，而不是在不同传输方式之间来回抖动。

对于原生 OpenAI 系列端点（`openai/*`、`openai-codex/*` 和 Azure
OpenAI Responses），OpenClaw 还会为请求附加稳定的会话和轮次身份状态，
以便重试、重连和 SSE 回退都能对齐到同一个
对话身份。在原生 OpenAI 系列路由中，这包括稳定的
会话/轮次请求身份头，以及匹配的传输元数据。

在使用量计数到达会话/状态界面之前，OpenClaw 还会跨不同传输变体统一 OpenAI 的用量计数器。原生 OpenAI/Codex Responses 流量
可能将用量报告为 `input_tokens` / `output_tokens`，也可能为
`prompt_tokens` / `completion_tokens`；对于 `/status`、`/usage` 和会话日志，OpenClaw 会将它们视为相同的输入
和输出计数器。当原生
WebSocket 流量省略 `total_tokens`（或报告为 `0`）时，OpenClaw 会回退到
标准化后的输入 + 输出总数，以保持会话/状态显示内容完整。

你可以设置 `agents.defaults.models.<provider/model>.params.transport`：

- `"sse"`：强制使用 SSE
- `"websocket"`：强制使用 WebSocket
- `"auto"`：先尝试 WebSocket，然后回退到 SSE

对于 `openai/*`（Responses API），当使用 WebSocket 传输时，OpenClaw 还会默认启用 WebSocket 预热（`openaiWsWarmup: true`）。

相关 OpenAI 文档：

- [使用 WebSocket 的 Realtime API](https://platform.openai.com/docs/guides/realtime-websocket)
- [流式 API 响应（SSE）](https://platform.openai.com/docs/guides/streaming-responses)

```json5
{
  agents: {
    defaults: {
      model: { primary: "openai-codex/gpt-5.4" },
      models: {
        "openai-codex/gpt-5.4": {
          params: {
            transport: "auto",
          },
        },
      },
    },
  },
}
```

### OpenAI WebSocket 预热

OpenAI 文档将预热描述为可选项。对于
`openai/*`，OpenClaw 默认启用它，以在使用 WebSocket 传输时降低首轮延迟。

### 禁用预热

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: false,
          },
        },
      },
    },
  },
}
```

### 显式启用预热

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: true,
          },
        },
      },
    },
  },
}
```

### OpenAI 和 Codex 优先处理

OpenAI 的 API 通过 `service_tier=priority` 提供优先处理能力。在
OpenClaw 中，设置 `agents.defaults.models["<provider>/<model>"].params.serviceTier`
即可将该字段透传到原生 OpenAI/Codex Responses 端点。

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

支持的值为 `auto`、`default`、`flex` 和 `priority`。

当这些模型指向原生 OpenAI/Codex 端点时，OpenClaw 会将 `params.serviceTier` 同时转发到直接 `openai/*` Responses
请求和 `openai-codex/*` Codex Responses 请求。

重要行为：

- 直接 `openai/*` 必须指向 `api.openai.com`
- `openai-codex/*` 必须指向 `chatgpt.com/backend-api`
- 如果你通过其他 base URL 或代理路由任一提供商，OpenClaw 会保持 `service_tier` 原样不变

### OpenAI 快速模式

OpenClaw 为 `openai/*` 和
`openai-codex/*` 会话都提供了一个共享的快速模式开关：

- Chat/UI：`/fast status|on|off`
- 配置：`agents.defaults.models["<provider>/<model>"].params.fastMode`

启用快速模式后，OpenClaw 会将其映射为 OpenAI 优先处理：

- 发送到 `api.openai.com` 的直接 `openai/*` Responses 调用会发送 `service_tier = "priority"`
- 发送到 `chatgpt.com/backend-api` 的 `openai-codex/*` Responses 调用也会发送 `service_tier = "priority"`
- 现有负载中的 `service_tier` 值会被保留
- 快速模式不会改写 `reasoning` 或 `text.verbosity`

示例：

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
      },
    },
  },
}
```

会话覆盖值优先于配置。在 Sessions UI 中清除会话覆盖值后，
该会话会恢复为配置中的默认值。

### 原生 OpenAI 与 OpenAI 兼容路由的区别

OpenClaw 对直接 OpenAI、Codex 和 Azure OpenAI 端点的处理方式
与通用的 OpenAI 兼容 `/v1` 代理不同：

- 原生 `openai/*`、`openai-codex/*` 和 Azure OpenAI 路由会在你显式禁用推理时保留
  `reasoning: { effort: "none" }`
- 原生 OpenAI 系列路由默认将工具 schema 设为严格模式
- 隐藏的 OpenClaw 归属头（`originator`、`version` 和
  `User-Agent`）仅会附加到已验证的原生 OpenAI 主机
  （`api.openai.com`）和原生 Codex 主机（`chatgpt.com/backend-api`）
- 原生 OpenAI/Codex 路由会保留 OpenAI 专用请求整形，例如
  `service_tier`、Responses `store`、OpenAI 推理兼容负载，以及
  prompt-cache 提示
- 代理风格的 OpenAI 兼容路由会保留更宽松的兼容行为，并且
  不会强制使用严格工具 schema、原生专用请求整形或隐藏的
  OpenAI/Codex 归属头

Azure OpenAI 在传输和兼容行为上仍属于原生路由类别，但它不会接收隐藏的 OpenAI/Codex 归属头。

这样可以保留当前原生 OpenAI Responses 的行为，而不会把旧版
OpenAI 兼容垫片强加到第三方 `/v1` 后端上。

### OpenAI Responses 服务端压缩

对于直接 OpenAI Responses 模型（`openai/*`，使用 `api: "openai-responses"` 且
`baseUrl` 指向 `api.openai.com`），OpenClaw 现在会自动启用 OpenAI 服务端
压缩负载提示：

- 强制 `store: true`（除非模型兼容性设置了 `supportsStore: false`）
- 注入 `context_management: [{ type: "compaction", compact_threshold: ... }]`

默认情况下，`compact_threshold` 为模型 `contextWindow` 的 `70%`（若不可用则为 `80000`）。

### 显式启用服务端压缩

当你想在兼容的
Responses 模型上强制注入 `context_management` 时使用此项（例如 Azure OpenAI Responses）：

```json5
{
  agents: {
    defaults: {
      models: {
        "azure-openai-responses/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
          },
        },
      },
    },
  },
}
```

### 使用自定义阈值启用

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
            responsesCompactThreshold: 120000,
          },
        },
      },
    },
  },
}
```

### 禁用服务端压缩

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: false,
          },
        },
      },
    },
  },
}
```

`responsesServerCompaction` 仅控制 `context_management` 注入。
直接 OpenAI Responses 模型仍会强制启用 `store: true`，除非兼容性设置了
`supportsStore: false`。

## 说明

- 模型引用始终使用 `provider/model`（参见 [/concepts/models](/zh-CN/concepts/models)）。
- 认证细节和复用规则见 [/concepts/oauth](/zh-CN/concepts/oauth)。
