---
read_when:
    - 扩展 qa-lab 或 qa-channel
    - 添加仓库支持的 QA 场景
    - 围绕 Gateway 网关仪表板构建更高真实性的 QA 自动化
summary: 用于 qa-lab、qa-channel、种子场景和协议报告的私有 QA 自动化形态
title: QA 端到端自动化
x-i18n:
    generated_at: "2026-04-12T18:04:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 355ddac0122a1981973b03ef42dd99403347507ffbe8d27a03c318a831dd62d7
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA 端到端自动化

私有 QA 栈旨在以比单个单元测试更贴近真实渠道形态的方式来验证 OpenClaw。

当前组成部分：

- `extensions/qa-channel`：合成消息渠道，提供私信、渠道、线程、表情反应、编辑和删除等交互面。
- `extensions/qa-lab`：调试器 UI 和 QA 总线，用于观察转录记录、注入入站消息以及导出 Markdown 报告。
- `qa/`：为启动任务和基线 QA 场景提供仓库支持的种子资源。

当前的 QA 操作流程是一个双窗格 QA 站点：

- 左侧：带有智能体的 Gateway 网关仪表板（Control UI）。
- 右侧：QA Lab，显示类似 Slack 的转录记录和场景计划。

运行方式：

```bash
pnpm qa:lab:up
```

该命令会构建 QA 站点、启动基于 Docker 的 Gateway 网关测试通道，并暴露 QA Lab 页面，供操作员或自动化循环为智能体分配 QA 任务、观察真实渠道行为，并记录哪些内容成功、失败或仍然受阻。

如果你想更快地迭代 QA Lab UI，而不必每次都重建 Docker 镜像，可使用带绑定挂载 QA Lab bundle 的方式启动整个栈：

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` 会让 Docker 服务继续使用预构建镜像，并将 `extensions/qa-lab/web/dist` 绑定挂载到 `qa-lab` 容器中。`qa:lab:watch` 会在文件变更时重新构建该 bundle，当 QA Lab 资源哈希变化时，浏览器会自动重新加载。

若要运行一个基于真实传输的 Matrix 冒烟测试通道，请执行：

```bash
pnpm openclaw qa matrix
```

该通道会在 Docker 中预配一个一次性的 Tuwunel homeserver，注册临时的 driver、SUT 和 observer 用户，创建一个私有房间，然后在 QA gateway 子进程中运行真实的 Matrix 插件。这个实时传输通道会将子进程配置限定在待测传输上，因此 Matrix 会在子进程配置中不包含 `qa-channel` 的情况下运行。

若要运行一个基于真实传输的 Telegram 冒烟测试通道，请执行：

```bash
pnpm openclaw qa telegram
```

该通道会针对一个真实的私有 Telegram 群组，而不是预配一次性服务器。它需要 `OPENCLAW_QA_TELEGRAM_GROUP_ID`、`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` 和 `OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`，并要求两个不同的 bot 位于同一个私有群组中。SUT bot 必须拥有 Telegram 用户名，并且当两个 bot 都在 `@BotFather` 中启用了 Bot-to-Bot Communication Mode 时，bot 对 bot 的观察效果最佳。

实时传输通道现在共享一个更小的统一契约，而不再由每条通道各自定义自己的场景列表形态：

`qa-channel` 仍然是覆盖面更广的合成产品行为测试套件，不属于实时传输覆盖矩阵的一部分。

| 通道 | Canary | 提及门控 | Allowlist 阻止 | 顶层回复 | 重启恢复 | 线程后续跟进 | 线程隔离 | 表情反应观察 | 帮助命令 |
| ---- | ------ | -------- | -------------- | -------- | -------- | ------------ | -------- | ------------ | -------- |
| Matrix   | x      | x              | x               | x               | x              | x                | x                | x                    |              |
| Telegram | x      |                |                 |                 |                |                  |                  |                      | x            |

这使 `qa-channel` 保持为覆盖面广泛的产品行为测试套件，而 Matrix、Telegram 以及未来的实时传输则共享一个明确的传输契约检查清单。

若要运行一个一次性的 Linux VM 通道，而不把 Docker 引入 QA 路径，请执行：

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

这会启动一个全新的 Multipass guest，在 guest 内安装依赖、构建 OpenClaw、运行 `qa suite`，然后将标准 QA 报告和摘要复制回宿主机上的 `.artifacts/qa-e2e/...`。
它复用了与宿主机上 `qa suite` 相同的场景选择行为。
宿主机和 Multipass 的 suite 运行默认都会并行执行多个已选场景，并使用隔离的 Gateway 网关 worker，最多 64 个 worker，或等于所选场景数量。使用 `--concurrency <count>` 可调整 worker 数量，或使用 `--concurrency 1` 进行串行执行。
实时运行会转发适合 guest 环境的受支持 QA 凭证输入：基于环境变量的提供商密钥、QA 实时提供商配置路径，以及存在时的 `CODEX_HOME`。请将 `--output-dir` 保持在仓库根目录下，以便 guest 能通过挂载的工作区回写结果。

## 仓库支持的种子资源

种子资源位于 `qa/`：

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

这些资源有意保存在 git 中，以便人类和智能体都能查看 QA 计划。基线列表应保持足够广泛，以覆盖：

- 私信和渠道聊天
- 线程行为
- 消息操作生命周期
- cron 回调
- 记忆召回
- 模型切换
- 子智能体交接
- 读取仓库和读取文档
- 一个小型构建任务，例如 Lobster Invaders

## 传输适配器

`qa-lab` 为 Markdown QA 场景提供一个通用传输接缝。
`qa-channel` 是该接缝上的第一个适配器，但设计目标更广：
未来无论是真实渠道还是合成渠道，都应接入同一个 suite runner，而不是再新增一个特定于传输的 QA runner。

在架构层面，拆分如下：

- `qa-lab` 负责场景执行、worker 并发、制品写入和报告。
- 传输适配器负责 Gateway 网关配置、就绪性、入站和出站观察、传输操作以及标准化的传输状态。
- 场景继续以 Markdown 优先的方式保存在 `qa/scenarios/` 下。

面向维护者的新渠道适配器采用指南位于
[测试](/zh-CN/help/testing#adding-a-channel-to-qa)。

## 报告

`qa-lab` 会根据观察到的总线时间线导出 Markdown 协议报告。
报告应回答以下问题：

- 哪些内容成功了
- 哪些内容失败了
- 哪些内容仍然受阻
- 值得添加哪些后续场景

对于角色与风格检查，可在多个实时模型引用上运行同一个场景，并写出一份经过评判的 Markdown 报告：

```bash
pnpm openclaw qa character-eval \
  --model openai/gpt-5.4,thinking=xhigh \
  --model openai/gpt-5.2,thinking=xhigh \
  --model openai/gpt-5,thinking=xhigh \
  --model anthropic/claude-opus-4-6,thinking=high \
  --model anthropic/claude-sonnet-4-6,thinking=high \
  --model zai/glm-5.1,thinking=high \
  --model moonshot/kimi-k2.5,thinking=high \
  --model google/gemini-3.1-pro-preview,thinking=high \
  --judge-model openai/gpt-5.4,thinking=xhigh,fast \
  --judge-model anthropic/claude-opus-4-6,thinking=high \
  --blind-judge-models \
  --concurrency 16 \
  --judge-concurrency 16
```

该命令运行的是本地 QA gateway 子进程，而不是 Docker。角色评估场景应通过 `SOUL.md` 设置 persona，然后运行常规用户轮次，例如聊天、工作区帮助和小型文件任务。候选模型不应被告知自己正在被评估。该命令会保留每一份完整转录记录，记录基本运行统计信息，然后让评审模型在 fast 模式下使用 `xhigh` 推理，按自然度、氛围和幽默感对这些运行结果进行排序。
在比较不同提供商时，请使用 `--blind-judge-models`：评审提示仍会收到每份转录记录和运行状态，但候选引用会被替换为中性标签，例如 `candidate-01`；报告会在解析完成后再将排名映射回真实引用。
候选运行默认使用 `high` thinking，而支持该能力的 OpenAI 模型则默认使用 `xhigh`。如需覆盖某个特定候选，可内联使用
`--model provider/model,thinking=<level>`。`--thinking <level>` 仍可设置全局后备值，而较旧的 `--model-thinking <provider/model=level>` 形式则保留以兼容旧用法。
OpenAI 候选引用默认使用 fast 模式，以便在提供商支持时启用优先处理。若某个单独候选或评审需要覆盖该行为，可内联添加 `,fast`、`,no-fast` 或 `,fast=false`。只有当你希望为所有候选模型强制启用 fast 模式时，才传入 `--fast`。候选和评审的耗时都会记录在报告中供基准分析使用，但评审提示中会明确说明不要按速度进行排序。
候选和评审模型运行默认都使用并发数 16。当提供商限制或本地 Gateway 网关压力使运行噪声过大时，可降低
`--concurrency` 或 `--judge-concurrency`。
当未传入候选 `--model` 时，角色评估默认使用
`openai/gpt-5.4`、`openai/gpt-5.2`、`openai/gpt-5`、`anthropic/claude-opus-4-6`、
`anthropic/claude-sonnet-4-6`、`zai/glm-5.1`、
`moonshot/kimi-k2.5` 和
`google/gemini-3.1-pro-preview`。
当未传入 `--judge-model` 时，评审默认使用
`openai/gpt-5.4,thinking=xhigh,fast` 和
`anthropic/claude-opus-4-6,thinking=high`。

## 相关文档

- [测试](/zh-CN/help/testing)
- [QA Channel](/zh-CN/channels/qa-channel)
- [仪表板](/web/dashboard)
