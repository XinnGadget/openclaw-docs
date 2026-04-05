---
read_when:
    - 你想在 OpenClaw 中使用 OpenAI 模型
    - 你想使用 Codex 订阅凭证而不是 API 密钥
summary: 在 OpenClaw 中通过 API 密钥或 Codex 订阅使用 OpenAI
title: OpenAI
x-i18n:
    generated_at: "2026-04-05T22:23:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 914836e35eb538d8ce758884fe4b0a6f5d0d0cfea483e1fe53f4a08709a16864
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI 为 GPT 模型提供开发者 API。Codex 支持使用 **ChatGPT 登录** 进行订阅访问，或使用 **API 密钥** 登录进行按量计费访问。Codex cloud 需要使用 ChatGPT 登录。
OpenAI 明确支持在 OpenClaw 这类外部工具/工作流中使用订阅 OAuth。

## 默认交互风格

OpenClaw 可以为 `openai/*` 和
`openai-codex/*` 运行添加一个小型的 OpenAI 专用提示词叠加层。默认情况下，该叠加层会让助手表现得更热情、
更具协作性、更简洁、更直接，并带有稍强一些的情感表达，
同时不会替换 OpenClaw 的基础系统提示词。这个友好叠加层还
允许在自然合适的时候偶尔使用 emoji，同时保持整体
输出简洁。

配置键：

`plugins.entries.openai.config.personality`

允许的值：

- `"friendly"`：默认；启用 OpenAI 专用叠加层。
- `"off"`：禁用该叠加层，仅使用 OpenClaw 的基础提示词。

作用范围：

- 适用于 `openai/*` 模型。
- 适用于 `openai-codex/*` 模型。
- 不影响其他提供商。

此行为默认开启。如果你希望它在未来本地配置变动后
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

如果你想使用未修改的 OpenClaw 基础提示词，请将叠加层设置为 `"off"`：

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

你也可以直接通过配置 CLI 设置它：

```bash
openclaw config set plugins.entries.openai.config.personality off
```

## 选项 A：OpenAI API 密钥（OpenAI Platform）

**最适合：** 直接 API 访问和按量计费。
可从 OpenAI 控制台获取你的 API 密钥。

### CLI 设置

```bash
openclaw onboard --auth-choice openai-api-key
# 或使用非交互模式
openclaw onboard --openai-api-key "$OPENAI_API_KEY"
```

### 配置片段

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

OpenAI 当前的 API 模型文档将 `gpt-5.4` 和 `gpt-5.4-pro` 列为可直接
通过 OpenAI API 使用的模型。OpenClaw 会通过 `openai/*` Responses 路径转发这两个模型。
OpenClaw 有意隐藏过时的 `openai/gpt-5.3-codex-spark` 条目，
因为直接 OpenAI API 调用在真实流量中会拒绝它。

OpenClaw **不会** 在直接 OpenAI
API 路径上暴露 `openai/gpt-5.3-codex-spark`。`pi-ai` 仍然内置了该模型的一项条目，但实时 OpenAI API
请求目前会拒绝它。在 OpenClaw 中，Spark 被视为仅限 Codex。

## 图像生成

内置的 `openai` 插件还会通过共享的
`image_generate` 工具注册图像生成功能。

- 默认图像模型：`openai/gpt-image-1`
- 生成：每个请求最多 4 张图像
- 编辑模式：已启用，最多 5 张参考图像
- 支持 `size`
- 当前 OpenAI 专有限制：OpenClaw 目前不会将 `aspectRatio` 或
  `resolution` 覆盖项转发到 OpenAI Images API

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

有关共享工具参数、
提供商选择和故障切换行为，请参见 [图像生成](/zh-CN/tools/image-generation)。

## 视频生成

内置的 `openai` 插件还会通过共享的
`video_generate` 工具注册视频生成功能。

- 默认视频模型：`openai/sora-2`
- 模式：文生视频、图生视频，以及单视频参考/编辑流程
- 当前限制：1 张图像或 1 个视频参考输入
- 当前 OpenAI 专有限制：OpenClaw 目前不会将 `aspectRatio` 或
  `resolution` 覆盖项转发到原生 OpenAI 视频 API

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

有关共享工具参数、
提供商选择和故障切换行为，请参见 [视频生成](/zh-CN/tools/video-generation)。

## 选项 B：OpenAI Code（Codex）订阅

**最适合：** 使用 ChatGPT/Codex 订阅访问，而不是 API 密钥。
Codex cloud 需要 ChatGPT 登录，而 Codex CLI 支持使用 ChatGPT 或 API 密钥登录。

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

如果新手引导复用了现有的 Codex CLI 登录，这些凭证将继续
由 Codex CLI 管理。凭证过期时，OpenClaw 会优先重新读取外部 Codex 来源；
当该提供商可以刷新凭证时，会将刷新的凭证写回
Codex 存储，而不是在 OpenClaw 中单独接管并保存一份副本。

如果你的 Codex 账户有 Codex Spark 权限，OpenClaw 还支持：

- `openai-codex/gpt-5.3-codex-spark`

OpenClaw 将 Codex Spark 视为仅限 Codex。它不会暴露直接的
`openai/gpt-5.3-codex-spark` API 密钥路径。

当 `pi-ai`
发现 `openai-codex/gpt-5.3-codex-spark` 时，OpenClaw 也会保留它。请将其视为依赖权限且具有实验性质：Codex Spark 与 GPT-5.4 `/fast` 相互独立，其可用性取决于已登录的 Codex /
ChatGPT 账户。

### Codex 上下文窗口上限

OpenClaw 将 Codex 模型元数据与运行时上下文上限视为两个独立的
值。

对于 `openai-codex/gpt-5.4`：

- 原生 `contextWindow`：`1050000`
- 默认运行时 `contextTokens` 上限：`272000`

这样既能保证模型元数据真实准确，又能保留更小的默认运行时
窗口，因为它在实践中具有更好的延迟和质量表现。

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
元数据时使用 `contextWindow`。如果你想限制运行时上下文预算，请使用 `contextTokens`。

### 默认传输方式

OpenClaw 使用 `pi-ai` 进行模型流式传输。对于 `openai/*` 和
`openai-codex/*`，默认传输方式为 `"auto"`（优先 WebSocket，其次 SSE
回退）。

在 `"auto"` 模式下，OpenClaw 还会在回退到 SSE 之前，
对一次发生得较早且可重试的 WebSocket 失败进行重试。
强制 `"websocket"` 模式仍会直接暴露传输错误，而不是通过回退将其隐藏。

在 `"auto"` 模式下，发生连接失败或首轮早期 WebSocket 失败后，OpenClaw 会将
该会话的 WebSocket 路径标记为降级状态，持续约 60 秒，并在冷却期间
通过 SSE 发送后续轮次，而不是在多种传输方式之间反复切换。

对于原生 OpenAI 系列端点（`openai/*`、`openai-codex/*` 和 Azure
OpenAI Responses），OpenClaw 还会将稳定的会话和轮次身份状态附加到
请求中，以便重试、重连和 SSE 回退都能与同一
会话身份保持一致。在原生 OpenAI 系列路由中，这包括稳定的
会话/轮次请求身份标头以及匹配的传输元数据。

在这些信息到达会话/状态界面之前，OpenClaw 还会统一不同传输方式下的 OpenAI 使用量计数器。
原生 OpenAI/Codex Responses 流量可能将使用量报告为 `input_tokens` / `output_tokens`，也可能是
`prompt_tokens` / `completion_tokens`；OpenClaw 会将它们视为相同的输入
和输出计数器，用于 `/status`、`/usage` 和会话日志。当原生
WebSocket 流量省略 `total_tokens`（或报告为 `0`）时，OpenClaw 会回退到
规范化后的输入 + 输出总数，以便会话/状态显示保持有值。

你可以设置 `agents.defaults.models.<provider/model>.params.transport`：

- `"sse"`：强制使用 SSE
- `"websocket"`：强制使用 WebSocket
- `"auto"`：先尝试 WebSocket，然后回退到 SSE

对于 `openai/*`（Responses API），OpenClaw 在使用
WebSocket 传输时还会默认启用 WebSocket 预热（`openaiWsWarmup: true`）。

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
`openai/*` 启用它，以减少使用 WebSocket 传输时的首轮延迟。

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

OpenAI 的 API 通过 `service_tier=priority` 提供优先级处理能力。在
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

支持的值有 `auto`、`default`、`flex` 和 `priority`。

当这些模型指向原生 OpenAI/Codex 端点时，OpenClaw 会将 `params.serviceTier` 转发到直接的 `openai/*` Responses
请求以及 `openai-codex/*` Codex Responses 请求。

重要行为：

- 直接 `openai/*` 必须指向 `api.openai.com`
- `openai-codex/*` 必须指向 `chatgpt.com/backend-api`
- 如果你通过其他 base URL 或代理路由任一提供商，OpenClaw 会保留 `service_tier` 不变

### OpenAI 快速模式

OpenClaw 为 `openai/*` 和
`openai-codex/*` 会话提供统一的快速模式开关：

- 聊天/UI：`/fast status|on|off`
- 配置：`agents.defaults.models["<provider>/<model>"].params.fastMode`

启用快速模式后，OpenClaw 会将其映射为 OpenAI 优先级处理：

- 发往 `api.openai.com` 的直接 `openai/*` Responses 调用会发送 `service_tier = "priority"`
- 发往 `chatgpt.com/backend-api` 的 `openai-codex/*` Responses 调用也会发送 `service_tier = "priority"`
- 会保留现有负载中的 `service_tier` 值
- 快速模式不会重写 `reasoning` 或 `text.verbosity`

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

会话覆盖优先于配置。在 Sessions UI 中清除会话覆盖后，
该会话会恢复为配置中的默认值。

### 原生 OpenAI 与 OpenAI 兼容路由

OpenClaw 对直接 OpenAI、Codex 和 Azure OpenAI 端点的处理方式
与通用 OpenAI 兼容 `/v1` 代理不同：

- 原生 `openai/*`、`openai-codex/*` 和 Azure OpenAI 路由会保留
  `reasoning: { effort: "none" }`，当你显式禁用推理时不会改写它
- 原生 OpenAI 系列路由默认将工具 schema 设为 strict 模式
- 隐藏的 OpenClaw 归因标头（`originator`、`version` 和
  `User-Agent`）只会附加到已验证的原生 OpenAI 主机
  （`api.openai.com`）和原生 Codex 主机（`chatgpt.com/backend-api`）上
- 原生 OpenAI/Codex 路由会保留 OpenAI 专属的请求整形，例如
  `service_tier`、Responses `store`、OpenAI 推理兼容负载，以及
  prompt-cache 提示
- 代理风格的 OpenAI 兼容路由会保留更宽松的兼容行为，并且
  不会强制 strict 工具 schema、原生专属请求整形或隐藏的
  OpenAI/Codex 归因标头

Azure OpenAI 在传输和兼容性
行为方面仍属于原生路由类别，但它不会接收隐藏的 OpenAI/Codex 归因标头。

这样可以保留当前原生 OpenAI Responses 的行为，同时不会将旧式
OpenAI 兼容 shim 强加给第三方 `/v1` 后端。

### OpenAI Responses 服务端压缩

对于直接 OpenAI Responses 模型（使用
`api: "openai-responses"` 且 `baseUrl` 指向 `api.openai.com` 的 `openai/*`），OpenClaw 现在会自动启用 OpenAI 服务端
压缩负载提示：

- 强制 `store: true`（除非模型兼容性设置 `supportsStore: false`）
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

`responsesServerCompaction` 仅控制 `context_management` 的注入。
直接 OpenAI Responses 模型仍会强制 `store: true`，除非兼容性设置
`supportsStore: false`。

## 说明

- 模型引用始终使用 `provider/model`（参见 [/concepts/models](/zh-CN/concepts/models)）。
- 凭证详情和复用规则见 [/concepts/oauth](/zh-CN/concepts/oauth)。
