---
read_when:
    - 你看到一个 ``.experimental`` 配置键，想知道它是否稳定。
    - 你想试用预览版运行时功能，同时不把它们与正常默认设置混淆。
    - 你想在一个地方找到当前已记录的实验性标志。
summary: OpenClaw 中的实验性标志是什么意思，以及当前已记录了哪些实验性标志？
title: 实验性功能
x-i18n:
    generated_at: "2026-04-15T10:48:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2d1c7b3d4cd56ef8a0bdab1deb9918e9b2c9a33f956d63193246087f8633dcf3
    source_path: concepts/experimental-features.md
    workflow: 15
---

# 实验性功能

OpenClaw 中的实验性功能是**需主动启用的预览能力**。它们被放在显式标志之后，是因为这些功能在成为稳定默认设置或长期公开契约之前，仍需要经过真实世界的使用验证。

请将它们与普通配置区别对待：

- 除非相关文档明确告诉你要尝试，否则默认应**保持关闭**。
- 预期它们的**结构和行为变化速度**会快于稳定配置。
- 如果已经有稳定路径，优先使用稳定路径。
- 如果你要大范围部署 OpenClaw，请先在较小环境中测试实验性标志，再将其纳入共享基线配置。

## 当前已记录的标志

| 能力面                  | 键名                                                      | 适用场景                                                                                                       | 更多信息                                                                                       |
| ----------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 本地模型运行时          | `agents.defaults.experimental.localModelLean`             | 较小或更严格的本地后端无法处理 OpenClaw 完整的默认工具能力面                                                  | [本地模型](/zh-CN/gateway/local-models)                                                              |
| 记忆搜索                | `agents.defaults.memorySearch.experimental.sessionMemory` | 你希望 `memory_search` 为先前的会话转录建立索引，并接受额外的存储和索引开销                                   | [记忆配置参考](/zh-CN/reference/memory-config#session-memory-search-experimental)                    |
| 结构化规划工具          | `tools.experimental.planTool`                             | 你希望在兼容的运行时和 UI 中公开结构化的 `update_plan` 工具，用于多步骤工作跟踪                               | [Gateway 网关配置参考](/zh-CN/gateway/configuration-reference#toolsexperimental)                     |

## 本地模型精简模式

`agents.defaults.experimental.localModelLean: true` 是为较弱的本地模型配置提供的减压阀。它会裁剪掉像 `browser`、`cron` 和 `message` 这类重量级默认工具，从而让提示词结构更小，并降低其在小上下文或更严格的 OpenAI 兼容后端中的脆弱性。

这**并不是**正常路径。如果你的后端能够干净地处理完整运行时，请保持此项关闭。

## 实验性不等于隐藏

如果某项功能是实验性的，OpenClaw 就应该在文档和配置路径本身中明确说明。**不应该**做的是，把预览行为偷偷塞进一个看起来稳定的默认开关里，然后假装这很正常。配置能力面正是这样变得混乱的。
