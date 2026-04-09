---
read_when:
    - 扩展 qa-lab 或 qa-channel
    - 添加仓库支持的 QA 场景
    - 围绕 Gateway 网关仪表板构建更高真实性的 QA 自动化
summary: 用于 qa-lab、qa-channel、种子场景和协议报告的私有 QA 自动化形态
title: QA 端到端自动化
x-i18n:
    generated_at: "2026-04-09T22:54:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 357d6698304ff7a8c4aa8a7be97f684d50f72b524740050aa761ac0ee68266de
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA 端到端自动化

私有 QA 栈旨在以比单个单元测试更贴近真实、渠道形态化的方式来验证 OpenClaw。

当前组成部分：

- `extensions/qa-channel`：合成消息渠道，提供私信、渠道、线程、反应、编辑和删除等交互界面。
- `extensions/qa-lab`：调试器 UI 和 QA 总线，用于观察转录内容、注入入站消息以及导出 Markdown 报告。
- `qa/`：由仓库支持的启动任务种子资源和基线 QA 场景。

当前的 QA 操作流程是一个双窗格 QA 站点：

- 左侧：带有智能体的 Gateway 网关仪表板（Control UI）。
- 右侧：QA Lab，显示类似 Slack 的转录内容和场景计划。

使用以下命令运行：

```bash
pnpm qa:lab:up
```

该命令会构建 QA 站点，启动基于 Docker 的 Gateway 网关执行通道，并暴露 QA Lab 页面，供操作员或自动化循环为智能体分配 QA 任务、观察真实渠道行为，并记录哪些内容正常工作、失败或仍被阻塞。

如果你想更快地迭代 QA Lab UI，而不必每次都重新构建 Docker 镜像，请使用带有绑定挂载 QA Lab 构建产物的方式启动该栈：

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` 会让 Docker 服务继续使用预构建镜像，并将 `extensions/qa-lab/web/dist` 绑定挂载到 `qa-lab` 容器中。`qa:lab:watch` 会在变更时重新构建该产物，当 QA Lab 资源哈希发生变化时，浏览器会自动重新加载。

如果你想使用一次性的 Linux VM 执行通道，而不将 Docker 引入 QA 路径，请运行：

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

这会启动一个全新的 Multipass 来宾系统，安装依赖，在来宾系统内构建 OpenClaw，运行 `qa suite`，然后将常规 QA 报告和摘要复制回宿主机上的 `.artifacts/qa-e2e/...`。
它会复用与宿主机上 `qa suite` 相同的场景选择行为。
实时运行会转发适合来宾环境使用的受支持 QA 凭证输入：基于环境变量的提供商密钥、QA 实时提供商配置路径，以及存在时的 `CODEX_HOME`。请将 `--output-dir` 保持在仓库根目录下，以便来宾系统能够通过已挂载的工作区写回内容。

## 由仓库支持的种子资源

种子资源位于 `qa/` 中：

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

这些内容有意保存在 git 中，以便人类和智能体都能看到 QA 计划。基线列表应保持足够广泛，以覆盖：

- 私信和渠道聊天
- 线程行为
- 消息操作生命周期
- cron 回调
- 记忆召回
- 模型切换
- 子智能体交接
- 读取仓库和读取文档
- 一个小型构建任务，例如 Lobster Invaders

## 报告

`qa-lab` 会根据观察到的总线时间线导出 Markdown 协议报告。
该报告应回答：

- 哪些内容正常工作
- 哪些内容失败
- 哪些内容仍被阻塞
- 值得补充哪些后续场景

对于角色和风格检查，请在多个实时模型引用上运行同一个场景，并写出一份经评判的 Markdown 报告：

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

该命令运行的是本地 QA Gateway 网关子进程，而不是 Docker。角色评估场景应通过 `SOUL.md` 设置 persona，然后运行普通用户轮次，例如聊天、工作区帮助和小型文件任务。候选模型不应被告知自己正在接受评估。该命令会保留每份完整转录内容，记录基础运行统计信息，然后要求评判模型在快速模式下以 `xhigh` 推理强度按自然度、氛围和幽默感对这些运行结果进行排序。
在比较提供商时，请使用 `--blind-judge-models`：评判提示仍会获取每份转录内容和运行状态，但候选引用会被替换为中性标签，例如 `candidate-01`；在解析完成后，报告会将排序结果映射回真实引用。
候选运行默认使用 `high` 推理强度，对于支持它的 OpenAI 模型则使用 `xhigh`。你可以使用
`--model provider/model,thinking=<level>` 为特定候选内联覆盖。`--thinking <level>` 仍会设置全局回退值，而较旧的 `--model-thinking <provider/model=level>` 形式会出于兼容性而保留。
OpenAI 候选引用默认使用快速模式，因此在提供商支持时会启用优先处理。如果某个单独候选或评判需要覆盖，请内联添加 `,fast`、`,no-fast` 或 `,fast=false`。只有当你想为每个候选模型都强制启用快速模式时，才传递 `--fast`。报告中会记录候选和评判的耗时以供基准分析，但评判提示会明确说明不要按速度进行排序。
候选运行和评判模型运行默认都使用 16 的并发度。当提供商限制或本地 Gateway 网关压力使运行噪声过大时，请调低 `--concurrency` 或 `--judge-concurrency`。
当未传入候选 `--model` 时，角色评估默认使用
`openai/gpt-5.4`、`openai/gpt-5.2`、`openai/gpt-5`、`anthropic/claude-opus-4-6`、
`anthropic/claude-sonnet-4-6`、`zai/glm-5.1`、
`moonshot/kimi-k2.5` 和
`google/gemini-3.1-pro-preview`。
当未传入 `--judge-model` 时，评判默认使用
`openai/gpt-5.4,thinking=xhigh,fast` 和
`anthropic/claude-opus-4-6,thinking=high`。

## 相关文档

- [测试](/zh-CN/help/testing)
- [QA 渠道](/zh-CN/channels/qa-channel)
- [仪表板](/web/dashboard)
