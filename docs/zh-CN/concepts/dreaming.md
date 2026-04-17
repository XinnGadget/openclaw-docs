---
read_when:
    - 你希望记忆提升自动运行
    - 你想了解每个 Dreaming 阶段的作用
    - 你想在不污染 `MEMORY.md` 的情况下调整巩固过程
summary: 通过浅层、深层和 REM 阶段进行后台记忆巩固，并配有梦境日记
title: Dreaming
x-i18n:
    generated_at: "2026-04-15T10:48:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5bcaec80f62e7611ed533094ef1917bd72c885f57252824db910e1f0496adc6
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming

Dreaming 是 `memory-core` 中的后台记忆巩固系统。  
它帮助 OpenClaw 将强烈的短期信号转入持久记忆，同时让整个过程保持可解释和可审查。

Dreaming 是**可选启用**功能，默认处于禁用状态。

## Dreaming 会写入什么

Dreaming 会保留两类输出：

- `memory/.dreams/` 中的**机器状态**（召回存储、阶段信号、摄取检查点、锁）。
- `DREAMS.md`（或现有的 `dreams.md`）中的**人类可读输出**，以及位于 `memory/dreaming/<phase>/YYYY-MM-DD.md` 下的可选阶段报告文件。

长期提升仍然只会写入 `MEMORY.md`。

## 阶段模型

Dreaming 使用三个协同阶段：

| 阶段 | 目的 | 持久写入 |
| ----- | ----------------------------------------- | ----------------- |
| Light | 对近期短期材料进行整理和暂存 | 否 |
| Deep  | 对持久候选项进行评分并提升 | 是（`MEMORY.md`） |
| REM   | 反思主题和反复出现的想法 | 否 |

这些阶段是内部实现细节，并不是单独的用户可配置“模式”。

### Light 阶段

Light 阶段会摄取近期的每日记忆信号和召回轨迹，对其去重，并暂存候选条目。

- 在可用时，从短期召回状态、近期每日记忆文件以及已脱敏的会话转录中读取内容。
- 当存储包含内联输出时，会写入一个受管理的 `## Light Sleep` 区块。
- 记录强化信号，供后续 Deep 排名使用。
- 绝不会写入 `MEMORY.md`。

### Deep 阶段

Deep 阶段决定哪些内容会成为长期记忆。

- 使用加权评分和阈值门槛对候选项进行排序。
- 要求通过 `minScore`、`minRecallCount` 和 `minUniqueQueries`。
- 在写入前，会从实时的每日文件中重新提取片段，因此过时或已删除的片段会被跳过。
- 将提升后的条目追加到 `MEMORY.md`。
- 将 `## Deep Sleep` 摘要写入 `DREAMS.md`，并可选写入 `memory/dreaming/deep/YYYY-MM-DD.md`。

### REM 阶段

REM 阶段会提取模式和反思信号。

- 从近期短期轨迹中构建主题和反思摘要。
- 当存储包含内联输出时，会写入一个受管理的 `## REM Sleep` 区块。
- 记录供 Deep 排名使用的 REM 强化信号。
- 绝不会写入 `MEMORY.md`。

## 会话转录摄取

Dreaming 可以将已脱敏的会话转录摄取到 dreaming 语料中。  
当转录可用时，它们会与每日记忆信号和召回轨迹一起输入到 Light 阶段。在摄取之前，个人内容和敏感内容会被脱敏。

## 梦境日记

Dreaming 还会在 `DREAMS.md` 中保留一份叙事性的**梦境日记**。  
在每个阶段积累了足够材料后，`memory-core` 会以尽力而为的方式运行一次后台子智能体轮次（使用默认运行时模型），并追加一条简短的日记条目。

这份日记是供人类在 Dreams UI 中阅读的，不是提升来源。  
由 Dreaming 生成的日记/报告工件会从短期提升中排除。只有有依据的记忆片段才有资格被提升到 `MEMORY.md`。

此外，还有一条基于事实依据的历史回填通道，用于审查和恢复工作：

- `memory rem-harness --path ... --grounded` 会从历史 `YYYY-MM-DD.md` 笔记中预览有依据的日记输出。
- `memory rem-backfill --path ...` 会将可逆的有依据日记条目写入 `DREAMS.md`。
- `memory rem-backfill --path ... --stage-short-term` 会将有依据的持久候选项暂存到与正常 Deep 阶段已使用的同一短期证据存储中。
- `memory rem-backfill --rollback` 和 `--rollback-short-term` 会移除这些已暂存的回填工件，而不会触碰普通日记条目或实时短期召回。

Control UI 公开了相同的日记回填/重置流程，因此你可以先在 Dreams 场景中检查结果，再决定这些有依据的候选项是否值得提升。该场景还会显示一条独立的有依据通道，这样你就能看到哪些已暂存的短期条目来自历史回放、哪些已提升条目由 grounded 流程引导生成，并且可以只清除仅限 grounded 的已暂存条目，而不影响普通的实时短期状态。

## Deep 排名信号

Deep 排名使用六个带权重的基础信号，再加上阶段强化：

| 信号 | 权重 | 说明 |
| ------------------- | ------ | ------------------------------------------------- |
| 频率 | 0.24 | 该条目累积了多少短期信号 |
| 相关性 | 0.30 | 该条目的平均检索质量 |
| 查询多样性 | 0.15 | 使其出现的不同查询/日期上下文 |
| 时新性 | 0.15 | 经过时间衰减的新鲜度分数 |
| 巩固度 | 0.10 | 跨多日重复出现的强度 |
| 概念丰富度 | 0.06 | 来自片段/路径的概念标签密度 |

Light 和 REM 阶段命中会从 `memory/.dreams/phase-signals.json` 增加一个小幅的、按时新性衰减的提升。

## 调度

启用后，`memory-core` 会自动管理一个 cron 任务，用于执行完整的 dreaming 扫描。  
每次扫描都会按顺序运行各阶段：light -> REM -> deep。

默认频率行为：

| 设置 | 默认值 |
| -------------------- | ----------- |
| `dreaming.frequency` | `0 3 * * *` |

## 快速开始

启用 dreaming：

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true
          }
        }
      }
    }
  }
}
```

使用自定义扫描频率启用 dreaming：

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true,
            "timezone": "America/Los_Angeles",
            "frequency": "0 */6 * * *"
          }
        }
      }
    }
  }
}
```

## 斜杠命令

```
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

## CLI 工作流

使用 CLI 提升进行预览或手动应用：

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

手动执行 `memory promote` 时，默认会使用 Deep 阶段阈值，除非你通过 CLI 标志覆盖。

说明某个特定候选项为什么会或不会被提升：

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

在不写入任何内容的情况下，预览 REM 反思、候选事实和 Deep 提升输出：

```bash
openclaw memory rem-harness
openclaw memory rem-harness --json
```

## 关键默认值

所有设置都位于 `plugins.entries.memory-core.config.dreaming` 下。

| 键 | 默认值 |
| ----------- | ----------- |
| `enabled`   | `false`     |
| `frequency` | `0 3 * * *` |

阶段策略、阈值和存储行为都属于内部实现细节（不是面向用户的配置）。

完整键名列表请参阅 [记忆配置参考](/zh-CN/reference/memory-config#dreaming)。

## Dreams UI

启用后，Gateway 网关的 **Dreams** 选项卡会显示：

- 当前 dreaming 启用状态
- 阶段级状态和受管理扫描的存在情况
- 短期、有依据、信号以及当日已提升计数
- 下一次计划运行时间
- 一条用于暂存历史回放条目的独立 grounded 场景通道
- 由 `doctor.memory.dreamDiary` 支持的可展开梦境日记阅读器

## 相关内容

- [记忆](/zh-CN/concepts/memory)
- [记忆搜索](/zh-CN/concepts/memory-search)
- [memory CLI](/cli/memory)
- [记忆配置参考](/zh-CN/reference/memory-config)
