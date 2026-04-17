---
read_when:
    - 解释 token 使用量、成本或上下文窗口
    - 调试上下文增长或压缩行为
summary: OpenClaw 如何构建提示词上下文，并报告 token 使用量与成本
title: Token 使用量与成本
x-i18n:
    generated_at: "2026-04-15T18:07:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9a706d3df8b2ea1136b3535d216c6b358e43aee2a31a4759824385e1345e6fe5
    source_path: reference/token-use.md
    workflow: 15
---

# Token 使用量与成本

OpenClaw 跟踪的是 **token**，而不是字符。token 取决于具体模型，但对大多数 OpenAI 风格的模型来说，英文文本平均约为每个 token 4 个字符。

## 系统提示词是如何构建的

OpenClaw 会在每次运行时组装自己的系统提示词。它包括：

- 工具列表 + 简短说明
- Skills 列表（仅包含元数据；说明会在需要时通过 `read` 按需加载）。
  紧凑的 Skills 块受 `skills.limits.maxSkillsPromptChars` 限制，
  并可在每个智能体上通过
  `agents.list[].skillsLimits.maxSkillsPromptChars` 进行可选覆盖。
- 自更新说明
- 工作区 + 启动文件（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、新的 `BOOTSTRAP.md`，以及存在时的 `MEMORY.md`，或作为小写回退的 `memory.md`）。大文件会按 `agents.defaults.bootstrapMaxChars`（默认值：12000）截断，而启动内容的总注入量受 `agents.defaults.bootstrapTotalMaxChars`（默认值：60000）限制。`memory/*.md` 每日文件不属于常规启动提示词的一部分；在普通轮次中，它们仍通过 memory 工具按需访问，但纯 `/new` 和 `/reset` 可在首轮前附加一个一次性的启动上下文块，其中包含最近的每日 memory。该启动前导由 `agents.defaults.startupContext` 控制。
- 时间（UTC + 用户时区）
- 回复标签 + heartbeat 行为
- 运行时元数据（主机 / OS / 模型 / thinking）

完整拆解请参见 [System Prompt](/zh-CN/concepts/system-prompt)。

## 上下文窗口中包含哪些内容

模型接收到的所有内容都会计入上下文限制：

- 系统提示词（上面列出的所有部分）
- 对话历史（用户消息 + 助手消息）
- 工具调用和工具结果
- 附件 / 转录内容（图片、音频、文件）
- 压缩摘要和裁剪产物
- 提供商包装层或安全头（不可见，但仍会计入）

某些运行时负载较重的表面还有各自明确的上限：

- `agents.defaults.contextLimits.memoryGetMaxChars`
- `agents.defaults.contextLimits.memoryGetDefaultLines`
- `agents.defaults.contextLimits.toolResultMaxChars`
- `agents.defaults.contextLimits.postCompactionMaxChars`

每个智能体的覆盖项位于 `agents.list[].contextLimits` 下。这些旋钮
用于受限的运行时摘录和由运行时注入的内容块。它们
与启动内容限制、启动上下文限制和 Skills 提示词限制是分开的。

对于图片，OpenClaw 会在调用提供商之前，对转录内容 / 工具图片负载进行缩放。
使用 `agents.defaults.imageMaxDimensionPx`（默认值：`1200`）来调整这一点：

- 较低的值通常会减少视觉 token 使用量和负载大小。
- 较高的值会保留更多视觉细节，适合 OCR / UI 较重的截图。

如果你需要实用的拆解信息（按每个注入文件、工具、Skills 以及系统提示词大小），请使用 `/context list` 或 `/context detail`。参见 [Context](/zh-CN/concepts/context)。

## 如何查看当前 token 使用情况

在聊天中使用以下命令：

- `/status` → **富含 emoji 的状态卡片**，显示当前会话模型、上下文使用情况、
  上一次回复的输入 / 输出 token，以及 **估算成本**（仅 API key）。
- `/usage off|tokens|full` → 在每次回复后附加一个**按回复统计的使用量页脚**。
  - 按会话持久化（存储为 `responseUsage`）。
  - OAuth 认证 **隐藏成本**（仅显示 token）。
- `/usage cost` → 从 OpenClaw 会话日志中显示本地成本汇总。

其他表面：

- **TUI / Web TUI：** 支持 `/status` + `/usage`。
- **CLI：** `openclaw status --usage` 和 `openclaw channels list` 会显示
  归一化后的提供商配额窗口（`X% left`，而不是按回复统计的成本）。
  当前支持使用量窗口的提供商有：Anthropic、GitHub Copilot、Gemini CLI、
  OpenAI Codex、MiniMax、Xiaomi 和 z.ai。

使用量表面会在显示前归一化常见的提供商原生字段别名。
对于 OpenAI 系列的 Responses 流量，这包括 `input_tokens` /
`output_tokens` 以及 `prompt_tokens` / `completion_tokens`，因此特定传输方式的
字段名不会影响 `/status`、`/usage` 或会话摘要。
Gemini CLI JSON 使用量也会被归一化：回复文本来自 `response`，并且
`stats.cached` 会映射为 `cacheRead`，当 CLI 省略显式的 `stats.input` 字段时，
会使用 `stats.input_tokens - stats.cached`。
对于原生 OpenAI 系列的 Responses 流量，WebSocket / SSE 的使用量别名也会以相同方式归一化，并且当
`total_tokens` 缺失或为 `0` 时，总量会回退为归一化后的输入 + 输出。
当当前会话快照信息较少时，`/status` 和 `session_status` 还可以
从最新的转录使用量日志中恢复 token / cache 计数器以及当前运行时模型标签。
现有的非零实时值仍然优先于转录回退值，并且当存储的总量缺失或更小时，
更大的面向提示词的转录总量可以胜出。
提供商配额窗口的使用量认证会在可用时来自提供商专用钩子；否则 OpenClaw 会回退为从认证配置文件、环境变量或配置中匹配 OAuth / API-key 凭证。

## 成本估算（显示时）

成本会根据你的模型定价配置进行估算：

```
models.providers.<provider>.models[].cost
```

这些值表示 `input`、`output`、`cacheRead` 和
`cacheWrite` 的**每 100 万 token 的美元价格**。如果缺少定价信息，OpenClaw 只显示 token。OAuth token
永远不会显示美元成本。

## Cache TTL 和裁剪的影响

提供商提示词缓存只会在 cache TTL 窗口内生效。OpenClaw 可选择运行 **cache-ttl 裁剪**：当 cache TTL
过期后，它会裁剪会话，然后重置缓存窗口，这样后续请求就可以重用新近缓存的上下文，而不是重新缓存完整历史。这样在会话空闲超过 TTL 后，可以降低 cache write 成本。

请在 [Gateway configuration](/zh-CN/gateway/configuration) 中进行配置，并在 [Session pruning](/zh-CN/concepts/session-pruning) 中查看行为细节。

Heartbeat 可以在空闲间隔期间让缓存保持**热状态**。如果你的模型 cache TTL
是 `1h`，将 heartbeat 间隔设置为略短于这个值（例如 `55m`）可以避免重新缓存完整提示词，从而降低 cache write 成本。

在多智能体设置中，你可以保留一个共享的模型配置，并通过 `agents.list[].params.cacheRetention` 按智能体调整缓存行为。

如需了解每个旋钮的完整指南，请参见 [Prompt Caching](/zh-CN/reference/prompt-caching)。

对于 Anthropic API 定价，cache read 比 input
token 便宜得多，而 cache write 则按更高倍数计费。最新费率和 TTL 倍率请参见 Anthropic 的提示词缓存定价：
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### 示例：用 heartbeat 保持 1h 缓存处于热状态

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
        every: "55m" # 为深度会话保持长缓存处于热状态
    - id: "alerts"
      params:
        cacheRetention: "none" # 对突发通知避免 cache write
```

`agents.list[].params` 会合并到所选模型的 `params` 之上，因此你可以
只覆盖 `cacheRetention`，并保持其他模型默认值不变。

### 示例：启用 Anthropic 1M 上下文 beta header

Anthropic 的 1M 上下文窗口目前仍受 beta 门控。OpenClaw 可以在你对受支持的 Opus
或 Sonnet 模型启用 `context1m` 时注入所需的
`anthropic-beta` 值。

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

这会映射到 Anthropic 的 `context-1m-2025-08-07` beta header。

这仅在该模型项上设置了 `context1m: true` 时适用。

要求：该凭证必须具备长上下文使用资格。否则，
Anthropic 会对该请求返回提供商侧的速率限制错误。

如果你使用 OAuth / 订阅 token（`sk-ant-oat-*`）对 Anthropic 进行认证，
OpenClaw 会跳过 `context-1m-*` beta header，因为 Anthropic 当前
会以 HTTP 401 拒绝这种组合。

## 减少 token 压力的提示

- 使用 `/compact` 来总结较长的会话。
- 在你的工作流中裁剪大型工具输出。
- 对于截图较多的会话，降低 `agents.defaults.imageMaxDimensionPx`。
- 保持 Skills 描述简短（Skills 列表会注入到提示词中）。
- 对冗长、探索性的工作，优先使用更小的模型。

有关确切的 Skills 列表开销公式，请参见 [Skills](/zh-CN/tools/skills)。
