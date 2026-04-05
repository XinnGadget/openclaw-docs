---
read_when:
    - 你想了解 OpenClaw 中“上下文”的含义
    - 你正在调试为什么模型“知道”某些内容（或忘记了它）
    - 你想减少上下文开销（`/context`、`/status`、`/compact`）
summary: 上下文：模型会看到什么、它是如何构建的，以及如何检查它
title: 上下文
x-i18n:
    generated_at: "2026-04-05T18:13:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: fe7dfe52cb1a64df229c8622feed1804df6c483a6243e0d2f309f6ff5c9fe521
    source_path: concepts/context.md
    workflow: 15
---

# 上下文

“上下文”是 **OpenClaw 在一次运行中发送给模型的全部内容**。它受限于模型的 **上下文窗口**（token 限制）。

适合初学者的理解方式：

- **系统提示词**（由 OpenClaw 构建）：规则、工具、Skills 列表、时间/运行时信息，以及注入的工作区文件。
- **对话历史**：你在此会话中的消息，以及助手的消息。
- **工具调用/结果 + 附件**：命令输出、文件读取、图片/音频等。

上下文 _并不等同于_ “记忆”：记忆可以存储在磁盘上并在之后重新加载；上下文则是模型当前窗口中的内容。

## 快速开始（检查上下文）

- `/status` → 快速查看“我的窗口用了多少？”以及会话设置。
- `/context list` → 查看注入了什么 + 粗略大小（每个文件 + 总计）。
- `/context detail` → 更深入的细分：每个文件、每个工具 schema 的大小、每个 skill 条目的大小，以及系统提示词大小。
- `/usage tokens` → 在普通回复后附加每次回复的用量页脚。
- `/compact` → 将较早的历史总结为一条紧凑条目，以释放窗口空间。

另见：[Slash commands](/zh-CN/tools/slash-commands)、[Token 用量与成本](/zh-CN/reference/token-use)、[压缩](/zh-CN/concepts/compaction)。

## 示例输出

具体数值会因模型、提供商、工具策略以及你的工作区内容而异。

### `/context list`

```
🧠 Context breakdown
Workspace: <workspaceDir>
Bootstrap max/file: 20,000 chars
Sandbox: mode=non-main sandboxed=false
System prompt (run): 38,412 chars (~9,603 tok) (Project Context 23,901 chars (~5,976 tok))

Injected workspace files:
- AGENTS.md: OK | raw 1,742 chars (~436 tok) | injected 1,742 chars (~436 tok)
- SOUL.md: OK | raw 912 chars (~228 tok) | injected 912 chars (~228 tok)
- TOOLS.md: TRUNCATED | raw 54,210 chars (~13,553 tok) | injected 20,962 chars (~5,241 tok)
- IDENTITY.md: OK | raw 211 chars (~53 tok) | injected 211 chars (~53 tok)
- USER.md: OK | raw 388 chars (~97 tok) | injected 388 chars (~97 tok)
- HEARTBEAT.md: MISSING | raw 0 | injected 0
- BOOTSTRAP.md: OK | raw 0 chars (~0 tok) | injected 0 chars (~0 tok)

Skills list (system prompt text): 2,184 chars (~546 tok) (12 skills)
Tools: read, edit, write, exec, process, browser, message, sessions_send, …
Tool list (system prompt text): 1,032 chars (~258 tok)
Tool schemas (JSON): 31,988 chars (~7,997 tok) (counts toward context; not shown as text)
Tools: (same as above)

Session tokens (cached): 14,250 total / ctx=32,000
```

### `/context detail`

```
🧠 Context breakdown (detailed)
…
Top skills (prompt entry size):
- frontend-design: 412 chars (~103 tok)
- oracle: 401 chars (~101 tok)
… (+10 more skills)

Top tools (schema size):
- browser: 9,812 chars (~2,453 tok)
- exec: 6,240 chars (~1,560 tok)
… (+N more tools)
```

## 哪些内容会计入上下文窗口

模型接收到的所有内容都会计入，包括：

- 系统提示词（所有部分）。
- 对话历史。
- 工具调用 + 工具结果。
- 附件/转录内容（图片/音频/文件）。
- 压缩摘要和裁剪产物。
- 提供商“包装层”或隐藏头信息（不可见，但仍会计入）。

## OpenClaw 如何构建系统提示词

系统提示词由 **OpenClaw 持有**，并会在每次运行时重新构建。它包括：

- 工具列表 + 简短描述。
- Skills 列表（仅元数据；见下文）。
- 工作区位置。
- 时间（UTC + 如果已配置则包含转换后的用户时区时间）。
- 运行时元数据（主机/OS/模型/思考设置）。
- 在 **Project Context** 下注入的工作区引导文件。

完整细分请参见：[System Prompt](/zh-CN/concepts/system-prompt)。

## 注入的工作区文件（Project Context）

默认情况下，OpenClaw 会注入一组固定的工作区文件（如果存在）：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（仅首次运行）

大型文件会按文件依据 `agents.defaults.bootstrapMaxChars`（默认 `20000` 个字符）进行截断。OpenClaw 还会通过 `agents.defaults.bootstrapTotalMaxChars`（默认 `150000` 个字符）对所有文件的总引导注入量施加上限。`/context` 会显示 **原始大小 vs 注入后大小**，以及是否发生了截断。

发生截断时，运行时可以在 Project Context 下方注入一个提示词内警告块。可通过 `agents.defaults.bootstrapPromptTruncationWarning` 进行配置（`off`、`once`、`always`；默认 `once`）。

## Skills：默认注入与按需加载

系统提示词中包含一个紧凑的 **skills 列表**（名称 + 描述 + 位置）。这个列表会带来真实的上下文开销。

Skill 指令默认 _不会_ 被包含进去。模型应当只在需要时才 `read` 该 skill 的 `SKILL.md`。

## 工具：有两种成本

工具会通过两种方式影响上下文：

1. 系统提示词中的 **工具列表文本**（也就是你看到的 “Tooling”）。
2. **工具 schemas**（JSON）。这些会发送给模型，以便它调用工具。即使你看不到它们的纯文本形式，它们也会计入上下文。

`/context detail` 会拆分出最大的工具 schema，让你看清哪些部分占比最高。

## 命令、指令和“行内快捷方式”

Slash commands 由 Gateway 网关处理。这里有几种不同的行为：

- **独立命令**：一条只包含 `/...` 的消息会作为命令运行。
- **指令**：`/think`、`/verbose`、`/reasoning`、`/elevated`、`/model`、`/queue` 会在消息被模型看到之前被剥离。
  - 仅包含指令的消息会持久化会话设置。
  - 普通消息中的行内指令会作为单条消息级别的提示。
- **行内快捷方式**（仅限于白名单发送者）：普通消息中的某些 `/...` token 可以立即运行（例如：“hey /status”），并会在模型看到剩余文本之前被剥离。

详情请参见：[Slash commands](/zh-CN/tools/slash-commands)。

## 会话、压缩和裁剪（哪些内容会持久化）

跨消息持久化哪些内容，取决于所使用的机制：

- **普通历史** 会保留在会话转录中，直到根据策略被压缩/裁剪。
- **压缩** 会将摘要持久化到转录中，并保留最近的消息不变。
- **裁剪** 会从某次运行的 _内存中_ 提示词里移除旧的工具结果，但不会重写转录。

文档：[Session](/zh-CN/concepts/session)、[压缩](/zh-CN/concepts/compaction)、[会话裁剪](/zh-CN/concepts/session-pruning)。

默认情况下，OpenClaw 使用内置的 `legacy` 上下文引擎进行组装和
压缩。如果你安装了一个提供 `kind: "context-engine"` 的插件，并通过
`plugins.slots.contextEngine` 选择它，OpenClaw 就会将上下文组装、
`/compact` 以及相关的子智能体上下文生命周期钩子委托给该
引擎处理。`ownsCompaction: false` 不会自动回退到 legacy
引擎；当前激活的引擎仍必须正确实现 `compact()`。完整的
可插拔接口、生命周期钩子和配置请参见
[Context Engine](/zh-CN/concepts/context-engine)。

## `/context` 实际报告的是什么

在可用时，`/context` 会优先使用最新的 **按运行构建** 的系统提示词报告：

- `System prompt (run)` = 从最近一次嵌入式（支持工具）运行中捕获，并持久化到会话存储中的数据。
- `System prompt (estimate)` = 当还没有运行报告时，动态计算得出的估算值。

无论哪种方式，它报告的都是大小和主要贡献项；它**不会**输出完整的系统提示词或工具 schema。

## 相关内容

- [Context Engine](/zh-CN/concepts/context-engine) —— 通过插件实现自定义上下文注入
- [压缩](/zh-CN/concepts/compaction) —— 对长对话进行总结
- [System Prompt](/zh-CN/concepts/system-prompt) —— 系统提示词是如何构建的
- [Agent Loop](/zh-CN/concepts/agent-loop) —— 完整的智能体执行周期
