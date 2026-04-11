---
read_when:
    - 你想在 OpenClaw 中使用 OpenAI 模型
    - 你想使用 Codex 订阅认证，而不是 API 密钥
    - 你需要更严格的 GPT-5 智能体执行行为
summary: 在 OpenClaw 中通过 API 密钥或 Codex 订阅使用 OpenAI
title: OpenAI
x-i18n:
    generated_at: "2026-04-11T16:15:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7aa06fba9ac901e663685a6b26443a2f6aeb6ec3589d939522dc87cbb43497b4
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI 提供用于 GPT 模型的开发者 API。Codex 支持通过 **ChatGPT 登录** 获取订阅访问，或通过 **API 密钥** 登录获取按使用量计费的访问。Codex cloud 需要使用 ChatGPT 登录。
OpenAI 明确支持在 OpenClaw 这类外部工具/工作流中使用基于订阅的 OAuth。

## 默认交互风格

OpenClaw 可以为 `openai/*` 和
`openai-codex/*` 运行添加一个小型的 OpenAI 专属提示词叠加层。默认情况下，这个叠加层会让助手显得更温暖、
更具协作性、更简洁、更直接，并带有一点更强的情绪表达，
但不会替换 OpenClaw 的基础系统提示词。这个友好叠加层还
允许在自然合适的情况下偶尔使用 emoji，同时保持整体
输出简洁。

配置键：

`plugins.entries.openai.config.personality`

允许的值：

- `"friendly"`：默认；启用 OpenAI 专属叠加层。
- `"on"`：`"friendly"` 的别名。
- `"off"`：禁用叠加层，仅使用基础 OpenClaw 提示词。

适用范围：

- 适用于 `openai/*` 模型。
- 适用于 `openai-codex/*` 模型。
- 不影响其他提供商。

此行为默认开启。如果你希望即使未来本地配置发生变动也继续保留 `"friendly"`，
请显式写上：

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

你也可以直接通过配置 CLI 设置：

```bash
openclaw config set plugins.entries.openai.config.personality off
```

OpenClaw 会在运行时以不区分大小写的方式规范化此设置，因此像
`"Off"` 这样的值也会禁用友好叠加层。

## 选项 A：OpenAI API 密钥（OpenAI Platform）

**最适合：** 直接访问 API，并按使用量计费。
请从 OpenAI 控制台获取你的 API 密钥。

路由摘要：

- `openai/gpt-5.4` = 直接 OpenAI Platform API 路由
- 需要 `OPENAI_API_KEY`（或等效的 OpenAI 提供商配置）
- 在 OpenClaw 中，ChatGPT/Codex 登录通过 `openai-codex/*` 路由，而不是 `openai/*`

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

OpenAI 当前的 API 模型文档列出了 `gpt-5.4` 和 `gpt-5.4-pro` 可用于直接
OpenAI API 调用。OpenClaw 会通过 `openai/*` Responses 路径转发这两者。
OpenClaw 会有意隐藏已过时的 `openai/gpt-5.3-codex-spark` 条目，
因为直接 OpenAI API 调用在真实流量中会拒绝它。

OpenClaw **不会** 在直接 OpenAI
API 路径中暴露 `openai/gpt-5.3-codex-spark`。`pi-ai` 仍然为该模型内置了一个条目，但真实的 OpenAI API
请求目前会拒绝它。在 OpenClaw 中，Spark 被视为仅限 Codex。

## 图像生成

内置的 `openai` 插件还会通过共享的
`image_generate` 工具注册图像生成功能。

- 默认图像模型：`openai/gpt-image-1`
- 生成：每次请求最多 4 张图片
- 编辑模式：已启用，最多支持 5 张参考图片
- 支持 `size`
- 当前 OpenAI 专属限制：OpenClaw 目前不会将 `aspectRatio` 或
  `resolution` 覆盖项转发到 OpenAI Images API

要将 OpenAI 作为默认图像提供商使用：

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

有关共享工具参数、提供商选择和故障切换行为，请参阅 [Image Generation](/zh-CN/tools/image-generation)。

## 视频生成

内置的 `openai` 插件还会通过共享的
`video_generate` 工具注册视频生成功能。

- 默认视频模型：`openai/sora-2`
- 模式：文生视频、图生视频，以及单视频参考/编辑流程
- 当前限制：1 张图片或 1 个视频参考输入
- 当前 OpenAI 专属限制：OpenClaw 目前仅会为原生 OpenAI 视频生成转发 `size`
  覆盖项。不受支持的可选覆盖项，
  例如 `aspectRatio`、`resolution`、`audio` 和 `watermark`，会被忽略，
  并作为工具警告返回。

要将 OpenAI 作为默认视频提供商使用：

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

有关共享工具参数、提供商选择和故障切换行为，请参阅 [Video Generation](/zh-CN/tools/video-generation)。

## 选项 B：OpenAI Code（Codex）订阅

**最适合：** 使用 ChatGPT/Codex 订阅访问，而不是 API 密钥。
Codex cloud 需要使用 ChatGPT 登录，而 Codex CLI 支持使用 ChatGPT 或 API 密钥登录。

路由摘要：

- `openai-codex/gpt-5.4` = ChatGPT/Codex OAuth 路由
- 使用 ChatGPT/Codex 登录，而不是直接使用 OpenAI Platform API 密钥
- `openai-codex/*` 的提供商侧限制可能与 ChatGPT 网页版/应用中的体验不同

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

OpenAI 当前的 Codex 文档将 `gpt-5.4` 列为当前 Codex 模型。OpenClaw
会将其映射为 `openai-codex/gpt-5.4`，用于 ChatGPT/Codex OAuth 访问。

这一路由与 `openai/gpt-5.4` 是有意分开的。如果你想使用
直接 OpenAI Platform API 路径，请使用带 API 密钥的 `openai/*`。如果你想使用
ChatGPT/Codex 登录，请使用 `openai-codex/*`。

如果新手引导复用了现有的 Codex CLI 登录，这些凭证将继续由 Codex CLI 管理。
过期后，OpenClaw 会先重新读取外部 Codex 来源；如果提供商可以刷新它，
则会将刷新后的凭证写回 Codex 存储，而不是在单独的 OpenClaw 专用副本中接管管理。

如果你的 Codex 账户拥有 Codex Spark 权限，OpenClaw 还支持：

- `openai-codex/gpt-5.3-codex-spark`

OpenClaw 将 Codex Spark 视为仅限 Codex。它不会暴露直接的
`openai/gpt-5.3-codex-spark` API 密钥路径。

当 `pi-ai`
发现 `openai-codex/gpt-5.3-codex-spark` 时，OpenClaw 也会保留它。请将其视为依赖权限且仍属实验性：Codex Spark 与 GPT-5.4 `/fast` 是分开的，而可用性取决于当前已登录的 Codex /
ChatGPT 账户。

### Codex 上下文窗口上限

OpenClaw 将 Codex 模型元数据和运行时上下文上限视为两个独立的
值。

对于 `openai-codex/gpt-5.4`：

- 原生 `contextWindow`：`1050000`
- 默认运行时 `contextTokens` 上限：`272000`

这样既能保持模型元数据真实，又能保留实践中在延迟和质量方面表现更好的较小默认运行时窗口。

如果你想使用不同的实际生效上限，请设置 `models.providers.<provider>.models[].contextTokens`：

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

仅当你要声明或覆盖原生模型元数据时，才使用 `contextWindow`。
如果你想限制运行时上下文预算，请使用 `contextTokens`。

### 默认传输方式

OpenClaw 使用 `pi-ai` 进行模型流式传输。对于 `openai/*` 和
`openai-codex/*`，默认传输方式为 `"auto"`（优先 WebSocket，其次回退到 SSE）。

在 `"auto"` 模式下，OpenClaw 还会在回退到 SSE 之前，
对一次早期且可重试的 WebSocket 失败进行重试。
强制 `"websocket"` 模式则仍会直接暴露传输错误，而不是用回退来掩盖它们。

在 `"auto"` 模式下，如果发生连接失败或前几轮对话中的 WebSocket 失败，OpenClaw 会将该
会话的 WebSocket 路径标记为降级状态，持续约 60 秒，并在冷却期间通过 SSE 发送
后续轮次，而不是在不同传输方式之间来回切换。

对于原生 OpenAI 系列端点（`openai/*`、`openai-codex/*` 以及 Azure
OpenAI Responses），OpenClaw 还会将稳定的会话和轮次身份状态附加到请求中，
使重试、重连和 SSE 回退都能与同一个会话身份保持一致。在原生 OpenAI 系列路由上，这包括稳定的
会话/轮次请求身份标头以及匹配的传输元数据。

OpenClaw 还会在 OpenAI 使用量计数器到达会话/状态界面之前，对不同传输变体中的计数进行规范化。原生 OpenAI/Codex Responses 流量可能会将用量报告为 `input_tokens` / `output_tokens`，或
`prompt_tokens` / `completion_tokens`；OpenClaw 会将它们视为相同的输入
和输出计数器，用于 `/status`、`/usage` 和会话日志。当原生
WebSocket 流量省略 `total_tokens`（或报告为 `0`）时，OpenClaw 会回退到
规范化后的输入 + 输出总量，这样会话/状态显示仍能保持有值。

你可以设置 `agents.defaults.models.<provider/model>.params.transport`：

- `"sse"`：强制使用 SSE
- `"websocket"`：强制使用 WebSocket
- `"auto"`：先尝试 WebSocket，再回退到 SSE

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

OpenAI 文档将预热描述为可选项。OpenClaw 默认会为
`openai/*` 启用它，以便在使用 WebSocket 传输时降低首轮延迟。

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

### OpenAI 和 Codex 优先级处理

OpenAI 的 API 通过 `service_tier=priority` 暴露优先级处理能力。在
OpenClaw 中，设置 `agents.defaults.models["<provider>/<model>"].params.serviceTier`
即可在原生 OpenAI/Codex Responses 端点上传递该字段。

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

当这些模型指向原生 OpenAI/Codex 端点时，OpenClaw 会将 `params.serviceTier` 同时转发到直接的 `openai/*` Responses
请求，以及 `openai-codex/*` Codex Responses 请求。

重要行为：

- 直接 `openai/*` 必须指向 `api.openai.com`
- `openai-codex/*` 必须指向 `chatgpt.com/backend-api`
- 如果你通过其他 base URL 或代理来路由任一提供商，OpenClaw 会保持 `service_tier` 原样不变

### OpenAI 快速模式

OpenClaw 为 `openai/*` 和
`openai-codex/*` 会话都提供了一个共享的快速模式开关：

- Chat/UI：`/fast status|on|off`
- 配置：`agents.defaults.models["<provider>/<model>"].params.fastMode`

启用快速模式后，OpenClaw 会将其映射为 OpenAI 优先级处理：

- 直接发往 `api.openai.com` 的 `openai/*` Responses 调用会发送 `service_tier = "priority"`
- 发往 `chatgpt.com/backend-api` 的 `openai-codex/*` Responses 调用也会发送 `service_tier = "priority"`
- 现有 payload 中的 `service_tier` 值会被保留
- 快速模式不会改写 `reasoning` 或 `text.verbosity`

对于 GPT 5.4，最常见的设置方式是：

- 在使用 `openai/gpt-5.4` 或 `openai-codex/gpt-5.4` 的会话中发送 `/fast on`
- 或设置 `agents.defaults.models["openai/gpt-5.4"].params.fastMode = true`
- 如果你也使用 Codex OAuth，那么也请设置 `agents.defaults.models["openai-codex/gpt-5.4"].params.fastMode = true`

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

会话级覆盖优先于配置。清除 Sessions UI 中的会话级覆盖后，
该会话会恢复为使用已配置的默认值。

### 原生 OpenAI 与 OpenAI-compatible 路由

OpenClaw 对直接 OpenAI、Codex 和 Azure OpenAI 端点的处理方式，
不同于通用的 OpenAI-compatible `/v1` 代理：

- 原生 `openai/*`、`openai-codex/*` 和 Azure OpenAI 路由会在你显式禁用推理时，
  保持 `reasoning: { effort: "none" }` 不变
- 原生 OpenAI 系列路由默认将工具 schema 设为严格模式
- 隐藏的 OpenClaw 归因标头（`originator`、`version` 和
  `User-Agent`）仅会附加到已验证的原生 OpenAI 主机
  （`api.openai.com`）和原生 Codex 主机（`chatgpt.com/backend-api`）上
- 原生 OpenAI/Codex 路由会保留 OpenAI 专属请求塑形，例如
  `service_tier`、Responses `store`、OpenAI 推理兼容 payload，以及
  prompt-cache 提示
- 代理风格的 OpenAI-compatible 路由会保留更宽松的兼容行为，并且
  不会强制使用严格工具 schema、原生专属请求塑形或隐藏的
  OpenAI/Codex 归因标头

Azure OpenAI 在传输和兼容行为方面仍属于原生路由这一类，
但它不会接收隐藏的 OpenAI/Codex 归因标头。

这样可以保留当前原生 OpenAI Responses 的行为，同时不会把较旧的
OpenAI-compatible 兼容适配强加到第三方 `/v1` 后端上。

### 严格智能体式 GPT 模式

对于 `openai/*` 和 `openai-codex/*` 的 GPT-5 系列运行，OpenClaw 可以使用
更严格的内嵌 Pi 执行契约：

```json5
{
  agents: {
    defaults: {
      embeddedPi: {
        executionContract: "strict-agentic",
      },
    },
  },
}
```

启用 `strict-agentic` 后，当存在可执行的具体工具操作时，
OpenClaw 不再将仅给出计划的助手轮次视为成功推进。它会使用立即行动的引导重试该轮次，
在处理较大任务时自动启用结构化的 `update_plan` 工具，
并且如果模型持续只做计划而不行动，则会显式显示阻塞状态。

此模式仅适用于 OpenAI 和 OpenAI Codex 的 GPT-5 系列运行。其他提供商
和较旧的模型系列会继续使用默认的内嵌 Pi 行为，除非你选择为它们启用其他运行时设置。

### OpenAI Responses 服务端压缩

对于直接 OpenAI Responses 模型（使用 `api: "openai-responses"` 的 `openai/*`，且
`baseUrl` 为 `api.openai.com`），OpenClaw 现在会自动启用 OpenAI 服务端压缩
payload 提示：

- 强制设置 `store: true`（除非模型兼容性设置了 `supportsStore: false`）
- 注入 `context_management: [{ type: "compaction", compact_threshold: ... }]`

默认情况下，`compact_threshold` 为模型 `contextWindow` 的 `70%`（如果不可用则为 `80000`）。

### 显式启用服务端压缩

当你希望在兼容的 Responses 模型上强制注入 `context_management` 时使用此项（例如 Azure OpenAI Responses）：

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

`responsesServerCompaction` 仅控制 `context_management` 的注入。
直接 OpenAI Responses 模型仍会强制设置 `store: true`，除非兼容性设置了
`supportsStore: false`。

## 说明

- 模型引用始终使用 `provider/model`（参见 [/concepts/models](/zh-CN/concepts/models)）。
- 认证详情和复用规则见 [/concepts/oauth](/zh-CN/concepts/oauth)。
