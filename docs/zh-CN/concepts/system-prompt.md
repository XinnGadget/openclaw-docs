---
read_when:
    - 编辑系统提示词文本、工具列表或时间/心跳部分时
    - 更改工作区引导或 Skills 注入行为时
summary: OpenClaw 系统提示词包含哪些内容以及如何组装
title: 系统提示词
x-i18n:
    generated_at: "2026-04-07T23:53:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: e55fc886bc8ec47584d07c9e60dfacd964dc69c7db976ea373877dc4fe09a79a
    source_path: concepts/system-prompt.md
    workflow: 15
---

# 系统提示词

OpenClaw 会为每次智能体运行构建一个自定义系统提示词。该提示词由 **OpenClaw 自有**，不使用 pi-coding-agent 的默认提示词。

提示词由 OpenClaw 组装，并注入到每次智能体运行中。

提供商插件可以贡献具备缓存感知能力的提示词指导，而无需替换完整的 OpenClaw 自有提示词。提供商运行时可以：

- 替换一小组已命名的核心部分（`interaction_style`、`tool_call_style`、`execution_bias`）
- 在提示词缓存边界之上注入一个**稳定前缀**
- 在提示词缓存边界之下注入一个**动态后缀**

将提供商自有的贡献用于特定模型家族的调优。保留传统的
`before_prompt_build` 提示词变更机制，以用于兼容性需求或真正的全局提示词变更，而不是常规的提供商行为。

## 结构

该提示词刻意保持紧凑，并使用固定部分：

- **Tooling**：结构化工具的权威来源提醒，以及运行时工具使用指导。
- **Safety**：简短的护栏提醒，避免寻求权力的行为或绕过监督。
- **Skills**（可用时）：告诉模型如何按需加载 skill 指令。
- **OpenClaw Self-Update**：如何使用 `config.schema.lookup` 安全检查配置，使用 `config.patch` 修补配置，使用 `config.apply` 替换完整配置，以及仅在用户明确请求时运行 `update.run`。仅所有者可用的 `gateway` 工具也会拒绝重写 `tools.exec.ask` / `tools.exec.security`，包括会被规范化为这些受保护 exec 路径的旧版 `tools.bash.*` 别名。
- **Workspace**：工作目录（`agents.defaults.workspace`）。
- **Documentation**：OpenClaw 文档的本地路径（仓库或 npm 包）以及何时应阅读它们。
- **Workspace Files (injected)**：表示引导文件已包含在下方。
- **Sandbox**（启用时）：表示处于沙箱隔离运行时、沙箱路径，以及是否提供提权 exec。
- **Current Date & Time**：用户本地时间、时区和时间格式。
- **Reply Tags**：受支持提供商的可选回复标签语法。
- **Heartbeats**：心跳提示词与确认行为，以及何时为默认智能体启用心跳。
- **Runtime**：主机、操作系统、node、模型、仓库根目录（检测到时）、思考级别（一行）。
- **Reasoning**：当前可见性级别 + `/reasoning` 切换提示。

Tooling 部分还包含针对长时间运行任务的运行时指导：

- 对于将来的后续跟进（`check back later`、提醒、周期性工作），使用 cron，而不是 `exec` 睡眠循环、`yieldMs` 延迟技巧或重复的 `process` 轮询
- 仅将 `exec` / `process` 用于那些现在启动并将在后台继续运行的命令
- 启用自动完成唤醒时，只启动命令一次，并在其输出结果或失败时依赖基于推送的唤醒路径
- 当你需要检查正在运行的命令时，使用 `process` 查看日志、状态、输入或进行干预
- 如果任务更大，优先使用 `sessions_spawn`；子智能体完成采用基于推送的方式，并会自动向请求方通告
- 不要仅为了等待完成而循环轮询 `subagents list` / `sessions_list`

启用实验性 `update_plan` 工具时，Tooling 还会告诉模型：仅将其用于非平凡的多步骤工作，始终只保留一个 `in_progress` 步骤，并避免在每次更新后重复整个计划。

系统提示词中的 Safety 护栏属于建议性质。它们会引导模型行为，但不强制执行策略。需要使用工具策略、exec 审批、沙箱隔离和渠道允许列表来实现硬性约束；操作员可以按设计禁用这些机制。

在具有原生审批卡片/按钮的渠道上，运行时提示词现在会告诉智能体优先依赖该原生审批 UI。只有当工具结果表明聊天审批不可用，或手动审批是唯一途径时，它才应包含手动 `/approve` 命令。

## 提示词模式

OpenClaw 可以为子智能体渲染更小的系统提示词。运行时会为每次运行设置一个
`promptMode`（不是面向用户的配置）：

- `full`（默认）：包含上述所有部分。
- `minimal`：用于子智能体；省略 **Skills**、**Memory Recall**、**OpenClaw Self-Update**、**Model Aliases**、**User Identity**、**Reply Tags**、**Messaging**、**Silent Replies** 和 **Heartbeats**。Tooling、**Safety**、Workspace、Sandbox、Current Date & Time（已知时）、Runtime 以及注入的上下文仍然可用。
- `none`：仅返回基础身份行。

当 `promptMode=minimal` 时，额外注入的提示词会标记为 **Subagent
Context**，而不是 **Group Chat Context**。

## 工作区引导注入

引导文件会被裁剪并附加在 **Project Context** 下，以便模型在无需显式读取的情况下看到身份和配置上下文：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（仅在全新工作区中）
- 存在时使用 `MEMORY.md`，否则使用小写回退文件 `memory.md`

除非某个文件适用特定门控条件，否则所有这些文件都会在每一轮**注入到上下文窗口中**。当默认智能体禁用心跳，或
`agents.defaults.heartbeat.includeSystemPromptSection` 为 false 时，正常运行中会省略 `HEARTBEAT.md`。请保持注入文件简洁——尤其是 `MEMORY.md`，它会随着时间增长，并可能导致上下文使用量意外升高以及更频繁的压缩。

> **注意：** `memory/*.md` 每日文件**不会**自动注入。它们按需通过 `memory_search` 和 `memory_get` 工具访问，因此除非模型显式读取，否则不会占用上下文窗口。

大文件会带标记被截断。每个文件的最大大小由
`agents.defaults.bootstrapMaxChars` 控制（默认：20000）。跨文件注入的引导内容总量上限由 `agents.defaults.bootstrapTotalMaxChars`
控制（默认：150000）。缺失文件会注入一个简短的缺失文件标记。发生截断时，OpenClaw 可以在 Project Context 中注入一个警告块；可通过
`agents.defaults.bootstrapPromptTruncationWarning` 控制（`off`、`once`、`always`；默认：`once`）。

子智能体会话只注入 `AGENTS.md` 和 `TOOLS.md`（其他引导文件会被过滤掉，以保持子智能体上下文较小）。

内部 hooks 可以通过 `agent:bootstrap` 拦截此步骤，以变更或替换注入的引导文件（例如将 `SOUL.md` 替换为另一种 persona）。

如果你想让智能体听起来不那么泛化，可以从
[SOUL.md Personality Guide](/zh-CN/concepts/soul) 开始。

若要检查每个注入文件贡献了多少内容（原始内容与注入内容、截断情况，以及工具 schema 开销），请使用 `/context list` 或 `/context detail`。参见 [Context](/zh-CN/concepts/context)。

## 时间处理

当已知用户时区时，系统提示词会包含一个专门的 **Current Date & Time** 部分。为了保持提示词缓存稳定，它现在只包含**时区**（不包含动态时钟或时间格式）。

当智能体需要当前时间时，请使用 `session_status`；状态卡片包含时间戳行。该工具还可以选择设置按会话生效的模型覆盖（`model=default` 会清除它）。

配置方式：

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat`（`auto` | `12` | `24`）

完整行为细节请参见 [Date & Time](/zh-CN/date-time)。

## Skills

当存在符合条件的 Skills 时，OpenClaw 会注入一个紧凑的**可用 Skills 列表**
（`formatSkillsForPrompt`），其中包含每个 skill 的**文件路径**。提示词会指示模型使用 `read` 在所列位置（工作区、托管或内置）加载 SKILL.md。若没有符合条件的 Skills，则省略 Skills 部分。

符合条件的判断包括 skill 元数据门控、运行时环境/配置检查，以及在配置了 `agents.defaults.skills` 或
`agents.list[].skills` 时生效的智能体 skill 允许列表。

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

这样可以在保持基础提示词精简的同时，仍支持有针对性的 skill 使用。

## 文档

可用时，系统提示词会包含一个 **Documentation** 部分，指向本地 OpenClaw 文档目录（仓库工作区中的 `docs/` 或内置 npm 包文档），并且还会说明公共镜像、源代码仓库、社区 Discord，以及用于发现 Skills 的 ClawHub（[https://clawhub.ai](https://clawhub.ai)）。提示词会指示模型在处理 OpenClaw 行为、命令、配置或架构时优先查阅本地文档，并在可能时自行运行
`openclaw status`（只有在无法访问时才询问用户）。
