---
read_when:
    - 你需要调试会话 id、转录 JSONL 或 sessions.json 字段
    - 你正在修改自动压缩行为，或添加“压缩前”维护逻辑
    - 你想实现记忆刷新或静默系统轮次
summary: 深入解析：会话存储 + 转录、生命周期，以及（自动）压缩内部机制
title: 会话管理深入解析
x-i18n:
    generated_at: "2026-04-05T18:15:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0d8c2d30be773eac0424f7a4419ab055fdd50daac8bc654e7d250c891f2c3b8
    source_path: reference/session-management-compaction.md
    workflow: 15
---

# 会话管理与压缩（深入解析）

本文档解释 OpenClaw 如何端到端管理会话：

- **会话路由**（入站消息如何映射到 `sessionKey`）
- **会话存储**（`sessions.json`）及其跟踪内容
- **转录持久化**（`*.jsonl`）及其结构
- **转录清理**（运行前的提供商专用修正）
- **上下文限制**（上下文窗口 vs 已跟踪 token）
- **压缩**（手动 + 自动压缩）以及在何处挂接压缩前逻辑
- **静默维护**（例如不应产生用户可见输出的记忆写入）

如果你想先看更高层的概览，请从以下文档开始：

- [/concepts/session](/zh-CN/concepts/session)
- [/concepts/compaction](/zh-CN/concepts/compaction)
- [/concepts/memory](/zh-CN/concepts/memory)
- [/concepts/memory-search](/zh-CN/concepts/memory-search)
- [/concepts/session-pruning](/zh-CN/concepts/session-pruning)
- [/reference/transcript-hygiene](/zh-CN/reference/transcript-hygiene)

---

## 事实来源：Gateway 网关

OpenClaw 的设计围绕一个拥有会话状态的单一 **Gateway 网关进程**。

- UI（macOS 应用、web Control UI、TUI）应向 Gateway 网关查询会话列表和 token 计数。
- 在远程模式下，会话文件位于远程主机上；“检查你本地 Mac 上的文件”并不能反映 Gateway 网关实际使用的内容。

---

## 两层持久化

OpenClaw 通过两层持久化保存会话：

1. **会话存储（`sessions.json`）**
   - 键值映射：`sessionKey -> SessionEntry`
   - 体积小、可变、安全，可编辑（或删除条目）
   - 跟踪会话元数据（当前会话 id、最近活动时间、开关、token 计数器等）

2. **转录（`<sessionId>.jsonl`）**
   - 采用树结构的追加式转录（条目包含 `id` + `parentId`）
   - 存储实际对话 + 工具调用 + 压缩摘要
   - 用于为未来轮次重建模型上下文

---

## 磁盘位置

在 Gateway 网关主机上，按智能体区分：

- 存储：`~/.openclaw/agents/<agentId>/sessions/sessions.json`
- 转录：`~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Telegram 话题会话：`.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw 通过 `src/config/sessions.ts` 解析这些路径。

---

## 存储维护和磁盘控制

会话持久化为 `sessions.json` 和转录产物提供了自动维护控制（`session.maintenance`）：

- `mode`：`warn`（默认）或 `enforce`
- `pruneAfter`：过期条目的年龄阈值（默认 `30d`）
- `maxEntries`：`sessions.json` 中的条目上限（默认 `500`）
- `rotateBytes`：当 `sessions.json` 过大时轮转（默认 `10mb`）
- `resetArchiveRetention`：`*.reset.<timestamp>` 转录归档的保留期（默认：与 `pruneAfter` 相同；`false` 表示禁用清理）
- `maxDiskBytes`：可选的会话目录磁盘预算
- `highWaterBytes`：清理后的可选目标值（默认是 `maxDiskBytes` 的 `80%`）

磁盘预算清理的执行顺序（`mode: "enforce"`）：

1. 优先删除最旧的归档或孤立转录产物。
2. 如果仍高于目标值，则驱逐最旧的会话条目及其转录文件。
3. 持续执行，直到使用量小于等于 `highWaterBytes`。

在 `mode: "warn"` 下，OpenClaw 会报告潜在驱逐项，但不会修改存储/文件。

按需运行维护：

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## 定时任务会话和运行日志

隔离的 cron 运行也会创建会话条目/转录，并且它们有专门的保留控制：

- `cron.sessionRetention`（默认 `24h`）会从会话存储中清理旧的隔离 cron 运行会话（`false` 表示禁用）。
- `cron.runLog.maxBytes` + `cron.runLog.keepLines` 会清理 `~/.openclaw/cron/runs/<jobId>.jsonl` 文件（默认：`2_000_000` 字节和 `2000` 行）。

---

## 会话键（`sessionKey`）

`sessionKey` 用于标识你当前处于 _哪个对话桶_ 中（路由 + 隔离）。

常见模式：

- 主/直接聊天（每个智能体）：`agent:<agentId>:<mainKey>`（默认 `main`）
- 群组：`agent:<agentId>:<channel>:group:<id>`
- 房间/渠道（Discord/Slack）：`agent:<agentId>:<channel>:channel:<id>` 或 `...:room:<id>`
- Cron：`cron:<job.id>`
- Webhook：`hook:<uuid>`（除非被覆盖）

规范规则见 [/concepts/session](/zh-CN/concepts/session)。

---

## 会话 id（`sessionId`）

每个 `sessionKey` 都指向当前的 `sessionId`（即继续该对话的转录文件）。

经验规则：

- **重置**（`/new`、`/reset`）会为该 `sessionKey` 创建新的 `sessionId`。
- **每日重置**（默认是 Gateway 网关主机本地时间凌晨 4:00）会在越过重置边界后的下一条消息上创建新的 `sessionId`。
- **空闲过期**（`session.reset.idleMinutes` 或旧版 `session.idleMinutes`）会在消息于空闲窗口之后到达时创建新的 `sessionId`。当同时配置每日重置和空闲过期时，以先到者为准。
- **线程父级分叉保护**（`session.parentForkMaxTokens`，默认 `100000`）会在父会话已过大时跳过父转录分叉；新线程将从空白开始。设为 `0` 可禁用。

实现细节：该决策发生在 `src/auto-reply/reply/session.ts` 的 `initSessionState()` 中。

---

## 会话存储 schema（`sessions.json`）

存储的值类型是 `src/config/sessions.ts` 中的 `SessionEntry`。

关键字段（非完整列表）：

- `sessionId`：当前转录 id（除非设置了 `sessionFile`，否则文件名由它推导）
- `updatedAt`：最近活动时间戳
- `sessionFile`：可选的显式转录路径覆盖
- `chatType`：`direct | group | room`（帮助 UI 和发送策略）
- `provider`、`subject`、`room`、`space`、`displayName`：用于群组/渠道标签的元数据
- 开关：
  - `thinkingLevel`、`verboseLevel`、`reasoningLevel`、`elevatedLevel`
  - `sendPolicy`（按会话覆盖）
- 模型选择：
  - `providerOverride`、`modelOverride`、`authProfileOverride`
- token 计数器（尽力而为 / 依赖提供商）：
  - `inputTokens`、`outputTokens`、`totalTokens`、`contextTokens`
- `compactionCount`：此会话键完成自动压缩的次数
- `memoryFlushAt`：最近一次压缩前记忆刷新的时间戳
- `memoryFlushCompactionCount`：上一次刷新运行时的压缩计数

该存储可以安全编辑，但 Gateway 网关是权威来源：会话运行时它可能重写或重新填充条目。

---

## 转录结构（`*.jsonl`）

转录由 `@mariozechner/pi-coding-agent` 的 `SessionManager` 管理。

该文件为 JSONL 格式：

- 第一行：会话头（`type: "session"`，包含 `id`、`cwd`、`timestamp`、可选的 `parentSession`）
- 后续：带有 `id` + `parentId` 的会话条目（树结构）

值得注意的条目类型：

- `message`：用户/助手/`toolResult` 消息
- `custom_message`：由扩展注入、_会_ 进入模型上下文的消息（可对 UI 隐藏）
- `custom`：_不会_ 进入模型上下文的扩展状态
- `compaction`：持久化的压缩摘要，带有 `firstKeptEntryId` 和 `tokensBefore`
- `branch_summary`：导航树分支时持久化的摘要

OpenClaw 有意**不会**“修正”转录；Gateway 网关使用 `SessionManager` 读写它们。

---

## 上下文窗口 vs 已跟踪 token

这里有两个不同的概念：

1. **模型上下文窗口**：每个模型的硬上限（模型可见的 token）
2. **会话存储计数器**：写入 `sessions.json` 的滚动统计（用于 `/status` 和仪表板）

如果你正在调整限制：

- 上下文窗口来自模型目录（也可通过配置覆盖）。
- 存储中的 `contextTokens` 是运行时估算/报告值；不要把它当作严格保证。

更多信息请参见 [/token-use](/zh-CN/reference/token-use)。

---

## 压缩：它是什么

压缩会将较早的对话总结成转录中的持久化 `compaction` 条目，并保留最近消息不变。

压缩后，未来轮次会看到：

- 压缩摘要
- `firstKeptEntryId` 之后的消息

压缩是**持久的**（不同于会话裁剪）。参见 [/concepts/session-pruning](/zh-CN/concepts/session-pruning)。

## 压缩分块边界和工具配对

当 OpenClaw 将长转录拆分为压缩分块时，它会保持
助手工具调用与其对应 `toolResult` 条目配对。

- 如果 token 占比分割点落在工具调用和其结果之间，OpenClaw
  会将边界移动到助手工具调用消息处，而不是拆散这一对。
- 如果尾部的工具结果块原本会将分块推过目标大小，OpenClaw
  会保留这段待处理工具块，并保持未总结的尾部完整。
- 已中止/报错的工具调用块不会让待处理分割持续保持打开状态。

---

## 自动压缩何时发生（Pi 运行时）

在嵌入式 Pi 智能体中，自动压缩会在两种情况下触发：

1. **溢出恢复**：模型返回上下文溢出错误
   （`request_too_large`、`context length exceeded`、`input exceeds the maximum
number of tokens`、`input token count exceeds the maximum number of input
tokens`、`input is too long for the model`、`ollama error: context length
exceeded`，以及类似的提供商形式变体）→ 压缩 → 重试。
2. **阈值维护**：在一次成功轮次之后，当：

`contextTokens > contextWindow - reserveTokens`

其中：

- `contextWindow` 是模型的上下文窗口
- `reserveTokens` 是为提示词 + 下一次模型输出预留的余量

这些是 Pi 运行时语义（OpenClaw 会消费这些事件，但由 Pi 决定何时压缩）。

---

## 压缩设置（`reserveTokens`、`keepRecentTokens`）

Pi 的压缩设置位于 Pi settings 中：

```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,
    keepRecentTokens: 20000,
  },
}
```

OpenClaw 还会为嵌入式运行施加一个安全下限：

- 如果 `compaction.reserveTokens < reserveTokensFloor`，OpenClaw 会将其提高。
- 默认下限是 `20000` token。
- 设置 `agents.defaults.compaction.reserveTokensFloor: 0` 可禁用该下限。
- 如果它本来就更高，OpenClaw 不会改动。

原因：在压缩变得不可避免之前，为多轮“维护”操作（例如记忆写入）预留足够余量。

实现：`src/agents/pi-settings.ts` 中的 `ensurePiCompactionReserveTokens()`
（由 `src/agents/pi-embedded-runner.ts` 调用）。

---

## 面向用户的可见表面

你可以通过以下方式观察压缩和会话状态：

- `/status`（在任意聊天会话中）
- `openclaw status`（CLI）
- `openclaw sessions` / `sessions --json`
- 详细模式：`🧹 Auto-compaction complete` + 压缩计数

---

## 静默维护（`NO_REPLY`）

OpenClaw 支持“静默”轮次，用于用户不应看到中间输出的后台任务。

约定：

- 助手以精确的静默 token `NO_REPLY` /
  `no_reply` 开头输出，以表示“不要向用户发送回复”。
- OpenClaw 会在交付层将其剥离/抑制。
- 对精确静默 token 的抑制不区分大小写，因此当整个负载仅为该静默 token 时，`NO_REPLY` 和
  `no_reply` 都算有效。
- 这仅用于真正的后台/不交付轮次；它不是普通可执行用户请求的快捷方式。

自 `2026.1.10` 起，OpenClaw 还会在
部分分块以 `NO_REPLY` 开头时抑制**草稿/输入中流式传输**，这样静默操作就不会在轮次中途泄露部分输出。

---

## 压缩前“记忆刷新”（已实现）

目标：在自动压缩发生之前，运行一个静默的智能体轮次，将持久
状态写入磁盘（例如智能体工作区中的 `memory/YYYY-MM-DD.md`），这样压缩就不会
擦除关键上下文。

OpenClaw 使用**预阈值刷新**方案：

1. 监控会话上下文使用量。
2. 当它越过“软阈值”（低于 Pi 的压缩阈值）时，向智能体运行一个静默的
   “现在写入记忆”指令。
3. 使用精确的静默 token `NO_REPLY` / `no_reply`，这样用户就看不到
   任何内容。

配置（`agents.defaults.compaction.memoryFlush`）：

- `enabled`（默认：`true`）
- `softThresholdTokens`（默认：`4000`）
- `prompt`（刷新轮次的用户消息）
- `systemPrompt`（附加到刷新轮次的额外系统提示词）

说明：

- 默认的 prompt/system prompt 包含一个 `NO_REPLY` 提示，用于抑制
  交付。
- 每个压缩周期只运行一次刷新（在 `sessions.json` 中跟踪）。
- 刷新仅对嵌入式 Pi 会话运行。
- 当会话工作区为只读（`workspaceAccess: "ro"` 或 `"none"`）时，会跳过刷新。
- 关于工作区文件布局和写入模式，请参见 [Memory](/zh-CN/concepts/memory)。

Pi 在扩展 API 中也暴露了一个 `session_before_compact` hook，但 OpenClaw 的
刷新逻辑目前位于 Gateway 网关侧。

---

## 故障排除检查清单

- 会话键不对？从 [/concepts/session](/zh-CN/concepts/session) 开始，并在 `/status` 中确认 `sessionKey`。
- 存储与转录不匹配？确认 Gateway 网关主机和 `openclaw status` 显示的存储路径。
- 压缩过于频繁？检查：
  - 模型上下文窗口（是否过小）
  - 压缩设置（对于模型窗口而言，`reserveTokens` 过高会导致更早压缩）
  - 工具结果膨胀：启用/调整会话裁剪
- 静默轮次泄露了输出？确认回复以 `NO_REPLY` 开头（大小写不敏感的精确 token），并且你使用的是包含流式传输抑制修复的构建版本。
