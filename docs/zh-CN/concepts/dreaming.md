---
read_when:
    - 你希望记忆提升能够自动运行
    - 你希望了解 Dreaming 的三个阶段
    - 你希望在不污染 MEMORY.md 的情况下调整整合行为
summary: 通过 light、deep 和 REM 三个协同阶段进行后台记忆整合
title: Dreaming（实验性）
x-i18n:
    generated_at: "2026-04-05T22:59:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: e6a82edf0b8630b48f458dacc270b0afc4032d5756baf39e28bf142e53cd8080
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming（实验性）

Dreaming 是 `memory-core` 中的后台记忆整合系统。它会重新查看对话中出现的内容，并决定哪些内容值得保留为持久上下文。

Dreaming 使用三个协同工作的**阶段**，而不是彼此竞争的模式。每个阶段都有不同的职责、写入不同的目标，并按照自己的计划运行。

## 三个阶段

### Light

Light Dreaming 会整理最近的杂乱内容。它会扫描最近的记忆轨迹，按 Jaccard 相似度去重，对相关条目进行聚类，并在启用 inline 存储时，将候选记忆暂存到共享的 Dreaming 轨迹文件（`DREAMS.md`）中。

Light **不会**向 `MEMORY.md` 写入任何内容。它只负责组织和暂存。可以理解为：“今天哪些内容以后可能会重要？”

### Deep

Deep Dreaming 会决定哪些内容会成为持久记忆。它运行真正的提升逻辑：基于六种信号的加权评分、阈值门槛、召回次数、唯一查询多样性、近期性衰减以及最大年龄过滤。

Deep 是**唯一**允许将持久事实写入 `MEMORY.md` 的阶段。
它还负责在记忆不足时进行恢复（当健康度低于配置阈值时）。可以理解为：“哪些内容足够真实，值得保留？”

### REM

REM Dreaming 会寻找模式并进行反思。它检查最近的材料，通过概念标签聚类识别反复出现的主题，并在启用 inline 存储时，将更高层次的笔记和反思写入 `DREAMS.md`。

REM 在 inline 模式下会写入 `DREAMS.md`，**不会**写入 `MEMORY.md`。
它的输出是解释性的，而不是规范性的。可以理解为：“我注意到了什么模式？”

## 明确边界

| 阶段 | 职责     | 写入位置                  | 不会写入 |
| ----- | -------- | ------------------------- | -------- |
| Light | 整理     | `DREAMS.md`（inline 模式） | MEMORY.md |
| Deep  | 保留     | MEMORY.md                 | --       |
| REM   | 解释     | `DREAMS.md`（inline 模式） | MEMORY.md |

## 快速开始

启用全部三个阶段（推荐）：

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

仅启用 deep 提升：

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true,
            "phases": {
              "light": { "enabled": false },
              "deep": { "enabled": true },
              "rem": { "enabled": false }
            }
          }
        }
      }
    }
  }
}
```

## 配置

所有 Dreaming 设置都位于 `openclaw.json` 中的 `plugins.entries.memory-core.config.dreaming` 下。
完整键名列表请参见 [记忆配置参考](/zh-CN/reference/memory-config#dreaming-experimental)。

### 全局设置

| 键名             | 类型      | 默认值     | 说明                                                         |
| ---------------- | --------- | ---------- | ------------------------------------------------------------ |
| `enabled`        | `boolean` | `true`     | 所有阶段的总开关                                             |
| `timezone`       | `string`  | 未设置     | 用于计划评估和 Dreaming 日期分桶的时区                       |
| `verboseLogging` | `boolean` | `false`    | 输出每次运行的详细 Dreaming 日志                             |
| `storage.mode`   | `string`  | `"inline"` | 使用 inline `DREAMS.md`、独立报告，或两者同时使用            |

### Light 阶段配置

| 键名               | 类型       | 默认值                          | 说明                       |
| ------------------ | ---------- | ------------------------------- | -------------------------- |
| `enabled`          | `boolean`  | `true`                          | 启用 Light 阶段            |
| `cron`             | `string`   | `0 */6 * * *`                   | 计划（默认：每 6 小时）    |
| `lookbackDays`     | `number`   | `2`                             | 扫描多少天内的轨迹         |
| `limit`            | `number`   | `100`                           | 每次运行最多暂存的候选数   |
| `dedupeSimilarity` | `number`   | `0.9`                           | 去重的 Jaccard 阈值        |
| `sources`          | `string[]` | `["daily","sessions","recall"]` | 要扫描的数据源             |

### Deep 阶段配置

| 键名                  | 类型       | 默认值                                          | 说明                                 |
| --------------------- | ---------- | ----------------------------------------------- | ------------------------------------ |
| `enabled`             | `boolean`  | `true`                                          | 启用 Deep 阶段                       |
| `cron`                | `string`   | `0 3 * * *`                                     | 计划（默认：每天凌晨 3 点）          |
| `limit`               | `number`   | `10`                                            | 每个周期最多提升的候选数             |
| `minScore`            | `number`   | `0.8`                                           | 提升所需的最低加权分数               |
| `minRecallCount`      | `number`   | `3`                                             | 最低召回次数阈值                     |
| `minUniqueQueries`    | `number`   | `3`                                             | 最低不同查询数量                     |
| `recencyHalfLifeDays` | `number`   | `14`                                            | 近期性分数减半所需的天数             |
| `maxAgeDays`          | `number`   | `30`                                            | 可提升的每日笔记最大年龄             |
| `sources`             | `string[]` | `["daily","memory","sessions","logs","recall"]` | 数据源                               |

### Deep 恢复配置

当长期记忆健康度低于某个阈值时，会触发恢复。

| 键名                              | 类型      | 默认值  | 说明                             |
| --------------------------------- | --------- | ------- | -------------------------------- |
| `recovery.enabled`                | `boolean` | `true`  | 启用自动恢复                     |
| `recovery.triggerBelowHealth`     | `number`  | `0.35`  | 触发恢复的健康度分数阈值         |
| `recovery.lookbackDays`           | `number`  | `30`    | 向前查找恢复材料的范围           |
| `recovery.maxRecoveredCandidates` | `number`  | `20`    | 每次运行最多恢复的候选数         |
| `recovery.minRecoveryConfidence`  | `number`  | `0.9`   | 恢复候选所需的最低置信度         |
| `recovery.autoWriteMinConfidence` | `number`  | `0.97`  | 自动写入阈值（跳过人工审查）     |

### REM 阶段配置

| 键名                 | 类型       | 默认值                      | 说明                                 |
| -------------------- | ---------- | --------------------------- | ------------------------------------ |
| `enabled`            | `boolean`  | `true`                      | 启用 REM 阶段                        |
| `cron`               | `string`   | `0 5 * * 0`                 | 计划（默认：每周日凌晨 5 点）        |
| `lookbackDays`       | `number`   | `7`                         | 反思多少天内的材料                   |
| `limit`              | `number`   | `10`                        | 最多写入的模式或主题数量             |
| `minPatternStrength` | `number`   | `0.75`                      | 最低标签共现强度                     |
| `sources`            | `string[]` | `["memory","daily","deep"]` | 用于反思的数据源                     |

### 执行覆盖

每个阶段都支持一个 `execution` 块，用于覆盖全局默认值：

| 键名              | 类型     | 默认值       | 说明                           |
| ----------------- | -------- | ------------ | ------------------------------ |
| `speed`           | `string` | `"balanced"` | `fast`、`balanced` 或 `slow`   |
| `thinking`        | `string` | `"medium"`   | `low`、`medium` 或 `high`      |
| `budget`          | `string` | `"medium"`   | `cheap`、`medium` 或 `expensive` |
| `model`           | `string` | 未设置       | 覆盖此阶段使用的模型           |
| `maxOutputTokens` | `number` | 未设置       | 限制输出 token 数              |
| `temperature`     | `number` | 未设置       | 采样温度（0-2）                |
| `timeoutMs`       | `number` | 未设置       | 阶段超时时间（毫秒）           |

## 提升信号（Deep 阶段）

Deep Dreaming 会组合六种加权信号。要完成提升，所有已配置的阈值门槛都必须同时通过。

| 信号               | 权重 | 说明                                               |
| ------------------ | ---- | -------------------------------------------------- |
| 频率               | 0.24 | 同一条目被召回的频率                               |
| 相关性             | 0.30 | 被检索到时的平均召回分数                           |
| 查询多样性         | 0.15 | 使其浮现出来的不同查询意图数量                     |
| 近期性             | 0.15 | 时间衰减（`recencyHalfLifeDays`，默认 14）         |
| 整合度             | 0.10 | 奖励跨多天重复出现的召回                           |
| 概念丰富度         | 0.06 | 奖励派生概念标签更丰富的条目                       |

## 聊天命令

```
/dreaming status                 # 显示阶段配置和执行频率
/dreaming on                     # 启用所有阶段
/dreaming off                    # 禁用所有阶段
/dreaming enable light|deep|rem  # 启用特定阶段
/dreaming disable light|deep|rem # 禁用特定阶段
/dreaming help                   # 显示使用指南
```

## CLI 命令

从命令行预览并应用 deep 提升：

```bash
# 预览提升候选
openclaw memory promote

# 将提升结果应用到 MEMORY.md
openclaw memory promote --apply

# 限制预览数量
openclaw memory promote --limit 5

# 包含已提升条目
openclaw memory promote --include-promoted

# 检查 Dreaming 状态
openclaw memory status --deep
```

完整 flag 参考请参见 [memory CLI](/cli/memory)。

## 工作原理

### Light 阶段流程

1. 从 `memory/.dreams/short-term-recall.json` 读取短期召回条目。
2. 过滤出在当前时间 `lookbackDays` 范围内的条目。
3. 按 Jaccard 相似度去重（阈值可配置）。
4. 按平均召回分数排序，最多取 `limit` 条目。
5. 在启用 inline 存储时，将暂存候选写入 `DREAMS.md` 的 `## Light Sleep` 区块下。

### Deep 阶段流程

1. 使用加权信号读取并排序短期召回候选。
2. 应用阈值门槛：`minScore`、`minRecallCount`、`minUniqueQueries`。
3. 按 `maxAgeDays` 过滤，并应用近期性衰减。
4. 扩展到所有已配置的记忆工作区。
5. 写入前重新读取实时每日笔记（跳过过期或已删除的片段）。
6. 将符合条件的条目连同提升时间戳追加到 `MEMORY.md`。
7. 标记已提升条目，以便在后续周期中将其排除。
8. 如果健康度低于 `recovery.triggerBelowHealth`，则运行恢复流程。

### REM 阶段流程

1. 读取 `lookbackDays` 范围内的近期记忆轨迹。
2. 按共现关系对概念标签进行聚类。
3. 按 `minPatternStrength` 过滤模式。
4. 在启用 inline 存储时，将主题和反思写入 `DREAMS.md` 的 `## REM Sleep` 区块下。

## 调度

每个阶段都会自动管理自己的 cron 任务。启用 Dreaming 后，
`memory-core` 会在 Gateway 网关启动时协调受管的 cron 任务。你无需手动创建 cron 条目。

| 阶段 | 默认计划         | 说明              |
| ----- | ---------------- | ----------------- |
| Light | `0 */6 * * *`    | 每 6 小时一次     |
| Deep  | `0 3 * * *`      | 每天凌晨 3 点     |
| REM   | `0 5 * * 0`      | 每周日凌晨 5 点   |

你可以使用阶段的 `cron` 键覆盖任意计划。所有计划都会遵循全局 `timezone` 设置。

## Dreams UI

启用 Dreaming 后，Gateway 网关侧边栏会显示一个 **Dreams** 标签页，其中包含记忆统计信息（短期数量、长期数量、已提升数量）以及下一次计划周期时间。每日计数在设置了 `dreaming.timezone` 时会遵循该时区，否则回退到已配置的用户时区。

手动运行 `openclaw memory promote` 时，默认会使用与 Deep 阶段相同的阈值，因此除非你传入 CLI 覆盖项，否则计划提升与按需提升会保持一致。

## 相关内容

- [记忆](/zh-CN/concepts/memory)
- [记忆搜索](/zh-CN/concepts/memory-search)
- [记忆配置参考](/zh-CN/reference/memory-config)
- [memory CLI](/cli/memory)
