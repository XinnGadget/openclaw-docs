---
read_when:
    - 解释 token 用量、成本或上下文窗口
    - 调试上下文增长或压缩行为
summary: OpenClaw 如何构建提示词上下文并报告 token 用量与成本
title: Token 用量与成本
x-i18n:
    generated_at: "2026-04-06T15:31:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0683693d6c6fcde7d5fba236064ba97dd4b317ae6bea3069db969fcd178119d9
    source_path: reference/token-use.md
    workflow: 15
---

# Token 用量与成本

OpenClaw 跟踪的是 **token**，而不是字符。Token 是模型特定的，但大多数 OpenAI 风格模型对英文文本的平均值约为每个 token 4 个字符。

## 系统提示词是如何构建的

OpenClaw 会在每次运行时组装自己的系统提示词。它包括：

- 工具列表 + 简短描述
- Skills 列表（仅元数据；说明会按需通过 `read` 加载）
- 自我更新说明
- 工作区 + bootstrap 文件（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、新建时的 `BOOTSTRAP.md`，以及在存在时的 `MEMORY.md` 或作为小写回退的 `memory.md`）。大文件会被 `agents.defaults.bootstrapMaxChars` 截断（默认：20000），bootstrap 注入总量受 `agents.defaults.bootstrapTotalMaxChars` 限制（默认：150000）。`memory/*.md` 文件通过 memory 工具按需加载，不会自动注入。
- 时间（UTC + 用户时区）
- 回复标签 + heartbeat 行为
- 运行时元数据（主机/OS/模型/thinking）

完整拆分请参见 [System Prompt](/zh-CN/concepts/system-prompt)。

## 什么会计入上下文窗口

模型接收到的所有内容都会计入上下文限制：

- 系统提示词（上面列出的所有部分）
- 对话历史（用户 + assistant 消息）
- 工具调用和工具结果
- 附件/转录内容（图片、音频、文件）
- 压缩摘要和裁剪产物
- provider 包装器或安全标头（不可见，但仍会计入）

对于图片，OpenClaw 会在调用 provider 之前对转录/工具图片负载进行缩放。使用 `agents.defaults.imageMaxDimensionPx`（默认：`1200`）来调整：

- 较低的值通常会减少视觉 token 用量和负载大小。
- 较高的值会为 OCR/UI 密集型截图保留更多视觉细节。

如需查看实用拆分（按注入文件、工具、Skills 和系统提示词大小），请使用 `/context list` 或 `/context detail`。参见 [Context](/zh-CN/concepts/context)。

## 如何查看当前 token 用量

在聊天中使用这些命令：

- `/status` → 显示**富含 emoji 的状态卡片**，包含会话模型、上下文用量、上次响应的输入/输出 token，以及**估算成本**（仅 API 密钥）。
- `/usage off|tokens|full` → 在每条回复后附加**按响应统计的用量页脚**。
  - 按会话持久化（存储为 `responseUsage`）。
  - OAuth 身份验证**隐藏成本**（仅显示 token）。
- `/usage cost` → 显示基于 OpenClaw 会话日志的本地成本摘要。

其他界面：

- **TUI/Web TUI：** 支持 `/status` + `/usage`。
- **CLI：** `openclaw status --usage` 和 `openclaw channels list` 显示
  标准化后的 provider 配额窗口（`X% left`，而不是按响应成本）。
  当前支持用量窗口的 provider：Anthropic、GitHub Copilot、Gemini CLI、
  OpenAI Codex、MiniMax、Xiaomi 和 z.ai。

用量界面会在显示前标准化常见的 provider 原生字段别名。
对于 OpenAI 系列 Responses 流量，这包括 `input_tokens` /
`output_tokens` 和 `prompt_tokens` / `completion_tokens`，因此特定传输的字段名不会改变 `/status`、`/usage` 或会话摘要。
Gemini CLI JSON 用量也会被标准化：回复文本来自 `response`，并且 `stats.cached` 会映射为 `cacheRead`，当 CLI 省略显式 `stats.input` 字段时，会使用 `stats.input_tokens - stats.cached`。
对于原生 OpenAI 系列 Responses 流量，WebSocket/SSE 用量别名也会以相同方式标准化，当 `total_tokens` 缺失或为 `0` 时，总量会回退到标准化后的输入 + 输出。
当当前会话快照信息较少时，`/status` 和 `session_status` 还可以从最近的转录用量日志中恢复 token/缓存计数器和活动运行时模型标签。现有的非零实时值仍然优先于转录回退值，而当存储总量缺失或更小时，较大的面向提示词的转录总量可以胜出。
用于 provider 配额窗口的用量身份验证优先来自 provider 特定 hooks；否则 OpenClaw 会回退为使用来自 auth profile、环境变量或配置中匹配的 OAuth/API 密钥凭证。

## 成本估算（显示时）

成本是根据你的模型定价配置估算的：

```
models.providers.<provider>.models[].cost
```

这些值表示 `input`、`output`、`cacheRead` 和
`cacheWrite` 的**每 100 万 token 的美元价格**。如果缺少定价，OpenClaw 只显示 token。OAuth token 永远不会显示美元成本。

## 缓存 TTL 和裁剪的影响

Provider 提示词缓存只会在缓存 TTL 窗口内生效。OpenClaw 可以选择运行**缓存 TTL 裁剪**：一旦缓存 TTL 过期，它就会裁剪会话，然后重置缓存窗口，这样后续请求就能重用刚刚重新缓存的上下文，而不是重新缓存完整历史。这可以在会话空闲超过 TTL 时降低缓存写入成本。

请在 [Gateway 网关配置](/zh-CN/gateway/configuration) 中进行配置，并在
[会话裁剪](/zh-CN/concepts/session-pruning) 中查看行为细节。

Heartbeat 可以在空闲间隔期间保持缓存**预热**。如果你的模型缓存 TTL
是 `1h`，将 heartbeat 间隔设置为略低于该值（例如 `55m`）可以避免重新缓存完整提示词，从而减少缓存写入成本。

在多智能体设置中，你可以保留一个共享模型配置，并通过 `agents.list[].params.cacheRetention` 为每个智能体调整缓存行为。

如需完整的逐项参数指南，请参见 [Prompt Caching](/zh-CN/reference/prompt-caching)。

对于 Anthropic API 定价，缓存读取比输入 token 便宜得多，而缓存写入则按更高倍数计费。最新费率和 TTL 倍数请参见 Anthropic 的提示词缓存定价：
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### 示例：使用 heartbeat 保持 1 小时缓存预热

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long"
    heartbeat:
      every: "55m"
```

### 示例：带有按智能体缓存策略的混合流量

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long" # 大多数智能体的默认基线
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # 为深度会话保持长缓存预热
    - id: "alerts"
      params:
        cacheRetention: "none" # 避免为突发通知写入缓存
```

`agents.list[].params` 会在所选模型的 `params` 之上合并，因此你可以只覆盖 `cacheRetention`，而让其他模型默认值保持不变。

### 示例：启用 Anthropic 1M 上下文 beta 标头

Anthropic 的 1M 上下文窗口当前仍受 beta 限制。启用受支持的 Opus
或 Sonnet 模型上的 `context1m` 后，OpenClaw 可以注入所需的
`anthropic-beta` 值。

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

这会映射到 Anthropic 的 `context-1m-2025-08-07` beta 标头。

这仅在该模型条目上设置了 `context1m: true` 时生效。

要求：该凭证必须具备长上下文使用资格。否则，Anthropic 会对该请求返回 provider 侧速率限制错误。

如果你使用 OAuth/订阅 token（`sk-ant-oat-*`）对 Anthropic 进行身份验证，OpenClaw 会跳过 `context-1m-*` beta 标头，因为 Anthropic 当前会以 HTTP 401 拒绝这种组合。

## 减少 token 压力的技巧

- 使用 `/compact` 总结较长的会话。
- 在你的工作流中裁剪较大的工具输出。
- 对截图密集型会话降低 `agents.defaults.imageMaxDimensionPx`。
- 保持 skill 描述简短（skill 列表会被注入到提示词中）。
- 对冗长、探索性工作优先使用更小的模型。

精确的 skill 列表开销公式请参见 [Skills](/zh-CN/tools/skills)。
