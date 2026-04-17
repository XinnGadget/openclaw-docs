---
read_when:
    - 你想了解内存是如何工作的
    - 你想知道应该写入哪些内存文件
summary: OpenClaw 如何在跨会话时记住内容
title: 内存概览
x-i18n:
    generated_at: "2026-04-15T10:48:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad1adafe1d81f1703d24f48a9c9da2b25a0ebbd4aad4f65d8bde5df78195d55b
    source_path: concepts/memory.md
    workflow: 15
---

# 内存概览

OpenClaw 通过在你的智能体工作区中写入**纯 Markdown 文件**来记住内容。模型只会“记住”已保存到磁盘的内容——不存在隐藏状态。

## 工作原理

你的智能体有三个与内存相关的文件：

- **`MEMORY.md`** —— 长期记忆。持久保存的事实、偏好和决定。会在每个私信会话开始时加载。
- **`memory/YYYY-MM-DD.md`** —— 每日笔记。持续记录的上下文和观察内容。系统会自动加载今天和昨天的笔记。
- **`DREAMS.md`**（可选）—— Dream Diary 和 Dreaming 扫描摘要，供人工审查，其中包括有据可依的历史回填条目。

这些文件位于智能体工作区中（默认是 `~/.openclaw/workspace`）。

<Tip>
如果你希望智能体记住某件事，只要直接告诉它：“记住我更喜欢 TypeScript。” 它会把内容写入合适的文件。
</Tip>

## 内存工具

智能体有两个用于处理内存的工具：

- **`memory_search`** —— 使用语义搜索查找相关笔记，即使措辞与原文不同也可以找到。
- **`memory_get`** —— 读取特定的内存文件或行范围。

这两个工具都由当前启用的内存插件提供（默认：`memory-core`）。

## Memory Wiki 配套插件

如果你希望持久记忆更像一个持续维护的知识库，而不只是原始笔记，请使用内置的 `memory-wiki` 插件。

`memory-wiki` 会将持久知识编译为一个 wiki 仓库，包含：

- 确定性的页面结构
- 结构化的主张与证据
- 矛盾与时效性跟踪
- 生成的仪表板
- 面向智能体/运行时消费者的编译摘要
- wiki 原生工具，如 `wiki_search`、`wiki_get`、`wiki_apply` 和 `wiki_lint`

它不会替代当前启用的内存插件。当前内存插件仍然负责召回、提升和 Dreaming。`memory-wiki` 则在其旁边增加了一层带有丰富溯源信息的知识层。

参见 [Memory Wiki](/zh-CN/plugins/memory-wiki)。

## 内存搜索

当已配置嵌入提供商时，`memory_search` 会使用**混合搜索**——将向量相似度（语义含义）与关键词匹配（如 ID 和代码符号等精确术语）结合起来。一旦你为任意受支持的提供商配置了 API 密钥，它就能开箱即用。

<Info>
OpenClaw 会根据可用的 API 密钥自动检测你的嵌入提供商。如果你已配置 OpenAI、Gemini、Voyage 或 Mistral 密钥，内存搜索会自动启用。
</Info>

有关搜索工作方式、调优选项和提供商设置的详细信息，请参见
[Memory Search](/zh-CN/concepts/memory-search)。

## 内存后端

<CardGroup cols={3}>
<Card title="内置（默认）" icon="database" href="/zh-CN/concepts/memory-builtin">
基于 SQLite。开箱即用，支持关键词搜索、向量相似度和混合搜索。无需额外依赖。
</Card>
<Card title="QMD" icon="search" href="/zh-CN/concepts/memory-qmd">
local-first sidecar，支持重排、查询扩展，以及为工作区外的目录建立索引。
</Card>
<Card title="Honcho" icon="brain" href="/zh-CN/concepts/memory-honcho">
AI 原生的跨会话内存，支持用户建模、语义搜索和多智能体感知。通过插件安装。
</Card>
</CardGroup>

## 知识 wiki 层

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/zh-CN/plugins/memory-wiki">
将持久记忆编译为一个带有丰富溯源信息的 wiki 仓库，包含主张、仪表板、桥接模式，以及对 Obsidian 友好的工作流。
</Card>
</CardGroup>

## 自动内存刷新

在 [compaction](/zh-CN/concepts/compaction) 对你的对话进行摘要之前，OpenClaw 会运行一个静默轮次，提醒智能体将重要上下文保存到内存文件中。此功能默认启用——你无需进行任何配置。

<Tip>
内存刷新可以防止在 compaction 期间丢失上下文。如果你的智能体在对话中包含重要事实但尚未写入文件，它们会在摘要发生前自动保存。
</Tip>

## Dreaming

Dreaming 是一个可选的后台内存整合流程。它会收集短期信号、为候选项打分，并且只将符合条件的内容提升到长期记忆（`MEMORY.md`）中。

它的设计目标是让长期记忆保持高信噪比：

- **选择启用**：默认关闭。
- **定时执行**：启用后，`memory-core` 会自动管理一个循环 cron 任务，用于执行完整的 Dreaming 扫描。
- **阈值控制**：提升必须通过分数、召回频率和查询多样性门槛。
- **可审查**：阶段摘要和日记条目会写入 `DREAMS.md`，供人工审查。

有关阶段行为、评分信号和 Dream Diary 详情，请参见
[Dreaming](/zh-CN/concepts/dreaming)。

## 有据可依的回填与实时提升

Dreaming 系统现在有两条紧密相关的审查路径：

- **实时 Dreaming** 基于 `memory/.dreams/` 下的短期 Dreaming 存储运行，这也是常规深度阶段在决定哪些内容可以进入 `MEMORY.md` 时使用的数据来源。
- **有据可依的回填** 会将历史的 `memory/YYYY-MM-DD.md` 笔记作为独立的每日文件读取，并将结构化审查输出写入 `DREAMS.md`。

当你希望重放旧笔记，并查看系统认为什么内容具有持久价值，而又不想手动编辑 `MEMORY.md` 时，有据可依的回填会很有用。

当你使用：

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

这些有据可依的持久候选项不会被直接提升。它们会被暂存到与常规深度阶段相同的短期 Dreaming 存储中。这意味着：

- `DREAMS.md` 仍然是供人工审查的界面。
- 短期存储仍然是面向机器的排序界面。
- `MEMORY.md` 仍然只会通过深度提升写入。

如果你决定这次重放没有帮助，你可以移除这些暂存产物，而不影响普通日记条目或常规召回状态：

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # 检查索引状态和提供商
openclaw memory search "query"  # 从命令行执行搜索
openclaw memory index --force   # 重建索引
```

## 延伸阅读

- [Builtin Memory Engine](/zh-CN/concepts/memory-builtin) —— 默认的 SQLite 后端
- [QMD Memory Engine](/zh-CN/concepts/memory-qmd) —— 高级 local-first sidecar
- [Honcho Memory](/zh-CN/concepts/memory-honcho) —— AI 原生跨会话内存
- [Memory Wiki](/zh-CN/plugins/memory-wiki) —— 编译型知识仓库和 wiki 原生工具
- [Memory Search](/zh-CN/concepts/memory-search) —— 搜索流水线、提供商和调优
- [Dreaming](/zh-CN/concepts/dreaming) —— 将短期召回内容后台提升到长期记忆
- [Memory configuration reference](/zh-CN/reference/memory-config) —— 所有配置项
- [Compaction](/zh-CN/concepts/compaction) —— compaction 如何与内存交互
