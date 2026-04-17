---
read_when:
    - 安排后台作业或唤醒任务
    - 将外部触发器（webhook、Gmail）接入 OpenClaw
    - 为计划任务在 heartbeat 和 cron 之间做选择
summary: Gateway 网关调度器的计划任务、webhook 和 Gmail PubSub 触发器
title: 计划任务
x-i18n:
    generated_at: "2026-04-12T04:25:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: f42bcaeedd0595d025728d7f236a724a0ebc67b6813c57233f4d739b3088317f
    source_path: automation/cron-jobs.md
    workflow: 15
---

# 计划任务（Cron）

Cron 是 Gateway 网关的内置调度器。它会持久化作业，在正确的时间唤醒智能体，并可将输出回传到聊天渠道或 webhook 端点。

## 快速开始

```bash
# 添加一次性提醒
openclaw cron add \
  --name "Reminder" \
  --at "2026-02-01T16:00:00Z" \
  --session main \
  --system-event "Reminder: check the cron docs draft" \
  --wake now \
  --delete-after-run

# 查看你的作业
openclaw cron list

# 查看运行历史
openclaw cron runs --id <job-id>
```

## cron 的工作方式

- Cron **在 Gateway 网关进程内部**运行（而不是在模型内部）。
- 作业持久化保存在 `~/.openclaw/cron/jobs.json`，因此重启不会丢失计划。
- 所有 cron 执行都会创建[后台任务](/zh-CN/automation/tasks)记录。
- 一次性作业（`--at`）默认会在成功后自动删除。
- 隔离的 cron 运行会在运行完成时，尽力关闭其 `cron:<jobId>` 会话所跟踪的浏览器标签页/进程，这样分离的浏览器自动化就不会留下孤儿进程。
- 隔离的 cron 运行还会防止过期的确认回复。如果第一次结果只是中间状态更新（如 `on it`、`pulling everything together` 以及类似提示），并且没有任何后代子智能体运行仍负责最终答案，OpenClaw 会在交付前再次提示一次，以获取实际结果。

<a id="maintenance"></a>

cron 的任务协调由运行时负责：只要 cron 运行时仍将该作业跟踪为正在运行，活动中的 cron 任务就会保持存活，即使仍存在旧的子会话记录行也是如此。一旦运行时不再拥有该作业，并且 5 分钟宽限期到期，维护流程就可以将该任务标记为 `lost`。

## 计划类型

| 类型    | CLI 标志  | 说明 |
| ------- | --------- | ---- |
| `at`    | `--at`    | 一次性时间戳（ISO 8601 或类似 `20m` 的相对时间） |
| `every` | `--every` | 固定间隔 |
| `cron`  | `--cron`  | 5 字段或 6 字段的 cron 表达式，可选 `--tz` |

不带时区的时间戳会被视为 UTC。添加 `--tz America/New_York` 可按本地墙上时钟时间调度。

每小时整点的循环表达式会自动错开最多 5 分钟，以减少负载峰值。使用 `--exact` 可强制精确时间，或使用 `--stagger 30s` 指定显式窗口。

### day-of-month 和 day-of-week 使用 OR 逻辑

Cron 表达式由 [croner](https://github.com/Hexagon/croner) 解析。当 day-of-month 和 day-of-week 字段都不是通配符时，croner 会在**任一**字段匹配时触发——而不是两者都匹配时。这是标准的 Vixie cron 行为。

```
# 预期："15 日上午 9 点，且仅当这天是周一"
# 实际："每月 15 日上午 9 点，以及每周一上午 9 点"
0 9 15 * 1
```

这会使它每月触发约 5–6 次，而不是 0–1 次。OpenClaw 在这里使用 Croner 默认的 OR 行为。若要同时要求两个条件，请使用 Croner 的 `+` day-of-week 修饰符（`0 9 15 * +1`），或只在一个字段上调度，并在你的作业提示或命令中对另一个条件进行保护判断。

## 执行方式

| 方式            | `--session` 值      | 运行位置                 | 最适合 |
| --------------- | ------------------- | ------------------------ | ------ |
| 主会话          | `main`              | 下一次 heartbeat 轮次    | 提醒、系统事件 |
| 隔离            | `isolated`          | 专用 `cron:<jobId>`      | 报告、后台杂务 |
| 当前会话        | `current`           | 在创建时绑定             | 依赖上下文的循环工作 |
| 自定义会话      | `session:custom-id` | 持久化命名会话           | 基于历史构建的工作流 |

**主会话**作业会将系统事件加入队列，并可选择唤醒 heartbeat（`--wake now` 或 `--wake next-heartbeat`）。**隔离**作业会使用全新的会话运行专用的智能体轮次。**自定义会话**（`session:xxx`）会在多次运行之间保留上下文，从而支持如基于此前摘要持续构建的每日站会等工作流。

对于隔离作业，运行时拆除流程现在包含对此 cron 会话的浏览器尽力清理。清理失败会被忽略，以确保实际的 cron 结果仍然优先。

当隔离的 cron 运行编排子智能体时，交付也会优先使用最终的后代输出，而不是过期的父级中间文本。如果后代仍在运行，OpenClaw 会抑制该部分父级更新，而不是提前宣布它。

### 隔离作业的负载选项

- `--message`：提示文本（隔离模式必需）
- `--model` / `--thinking`：模型和 thinking 级别覆盖
- `--light-context`：跳过工作区引导文件注入
- `--tools exec,read`：限制作业可使用的工具

`--model` 会为该作业使用所选的允许模型。如果请求的模型不被允许，cron 会记录警告，并回退到该作业的智能体/默认模型选择。已配置的回退链仍然适用，但仅指定模型覆盖而未显式提供按作业定义的回退列表时，不再把智能体主模型作为隐藏的额外重试目标附加进去。

隔离作业的模型选择优先级如下：

1. Gmail hook 模型覆盖（当运行来自 Gmail 且该覆盖被允许时）
2. 按作业定义的负载 `model`
3. 已保存的 cron 会话模型覆盖
4. 智能体/默认模型选择

快速模式也会遵循解析后的实际选择。如果所选模型配置带有 `params.fastMode`，隔离的 cron 会默认使用它。已保存的会话 `fastMode` 覆盖在任一方向上都仍优先于配置。

如果隔离运行遇到实时模型切换交接，cron 会使用切换后的提供商/模型重试，并在重试前持久化该实时选择。当切换同时携带新的凭证配置文件时，cron 也会持久化该凭证配置文件覆盖。重试次数是有上限的：初次尝试后最多再进行 2 次切换重试，之后 cron 会中止，而不是无限循环。

## 交付与输出

| 模式       | 发生的情况 |
| ---------- | ---------- |
| `announce` | 将摘要交付到目标渠道（隔离模式的默认值） |
| `webhook`  | 将完成事件负载 POST 到某个 URL |
| `none`     | 仅内部使用，不交付 |

使用 `--announce --channel telegram --to "-1001234567890"` 可进行渠道交付。对于 Telegram forum topic，请使用 `-1001234567890:topic:123`。Slack/Discord/Mattermost 目标应使用显式前缀（`channel:<id>`、`user:<id>`）。

对于由 cron 拥有的隔离作业，运行器拥有最终交付路径。系统会提示智能体返回纯文本摘要，然后该摘要会通过 `announce`、`webhook` 发送，或在 `none` 模式下仅保留在内部。`--no-deliver` 不会把交付重新交还给智能体；它只会让本次运行保持内部化。

如果原始任务明确说明要给某个外部接收方发送消息，智能体应在其输出中注明该消息应发送给谁/发送到哪里，而不是尝试直接发送。

失败通知遵循单独的目标路径：

- `cron.failureDestination` 设置失败通知的全局默认目标。
- `job.delivery.failureDestination` 会按作业覆盖该设置。
- 如果两者都未设置，且作业已经通过 `announce` 交付，失败通知现在会回退到该主 announce 目标。
- `delivery.failureDestination` 仅在 `sessionTarget="isolated"` 的作业上受支持，除非主交付模式是 `webhook`。

## CLI 示例

一次性提醒（主会话）：

```bash
openclaw cron add \
  --name "Calendar check" \
  --at "20m" \
  --session main \
  --system-event "Next heartbeat: check calendar." \
  --wake now
```

带交付的循环隔离作业：

```bash
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize overnight updates." \
  --announce \
  --channel slack \
  --to "channel:C1234567890"
```

带模型和 thinking 覆盖的隔离作业：

```bash
openclaw cron add \
  --name "Deep analysis" \
  --cron "0 6 * * 1" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Weekly deep analysis of project progress." \
  --model "opus" \
  --thinking high \
  --announce
```

## Webhooks

Gateway 网关可以暴露 HTTP webhook 端点，用于外部触发器。在配置中启用：

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
  },
}
```

### 身份验证

每个请求都必须通过请求头携带 hook token：

- `Authorization: Bearer <token>`（推荐）
- `x-openclaw-token: <token>`

查询字符串中的 token 会被拒绝。

### POST /hooks/wake

为主会话加入一个系统事件：

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"text":"New email received","mode":"now"}'
```

- `text`（必填）：事件描述
- `mode`（可选）：`now`（默认）或 `next-heartbeat`

### POST /hooks/agent

运行一个隔离的智能体轮次：

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","model":"openai/gpt-5.4-mini"}'
```

字段：`message`（必填）、`name`、`agentId`、`wakeMode`、`deliver`、`channel`、`to`、`model`、`thinking`、`timeoutSeconds`。

### 映射 hooks（POST /hooks/\<name\>）

自定义 hook 名称会通过配置中的 `hooks.mappings` 解析。映射可以通过模板或代码转换，将任意负载转换为 `wake` 或 `agent` 动作。

### 安全性

- 将 hook 端点放在 loopback、tailnet 或受信任的反向代理之后。
- 使用专用 hook token；不要复用 Gateway 网关身份验证 token。
- 将 `hooks.path` 保持在专用子路径下；`/` 会被拒绝。
- 设置 `hooks.allowedAgentIds` 以限制显式的 `agentId` 路由。
- 除非你需要让调用方选择会话，否则保持 `hooks.allowRequestSessionKey=false`。
- 如果你启用了 `hooks.allowRequestSessionKey`，也要设置 `hooks.allowedSessionKeyPrefixes`，以约束允许的会话键形态。
- 默认情况下，hook 负载会被安全边界包装。

## Gmail PubSub 集成

通过 Google PubSub 将 Gmail 收件箱触发器接入 OpenClaw。

**前置条件**：`gcloud` CLI、`gog`（gogcli）、已启用 OpenClaw hooks，以及用于公共 HTTPS 端点的 Tailscale。

### 向导设置（推荐）

```bash
openclaw webhooks gmail setup --account openclaw@gmail.com
```

这会写入 `hooks.gmail` 配置、启用 Gmail 预设，并为推送端点使用 Tailscale Funnel。

### Gateway 网关自动启动

当 `hooks.enabled=true` 且设置了 `hooks.gmail.account` 时，Gateway 网关会在启动时运行 `gog gmail watch serve`，并自动续订 watch。设置 `OPENCLAW_SKIP_GMAIL_WATCHER=1` 可选择退出。

### 手动一次性设置

1. 选择拥有 `gog` 所用 OAuth 客户端的 GCP 项目：

```bash
gcloud auth login
gcloud config set project <project-id>
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

2. 创建 topic 并授予 Gmail 推送访问权限：

```bash
gcloud pubsub topics create gog-gmail-watch
gcloud pubsub topics add-iam-policy-binding gog-gmail-watch \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
```

3. 启动 watch：

```bash
gog gmail watch start \
  --account openclaw@gmail.com \
  --label INBOX \
  --topic projects/<project-id>/topics/gog-gmail-watch
```

### Gmail 模型覆盖

```json5
{
  hooks: {
    gmail: {
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

## 管理作业

```bash
# 列出所有作业
openclaw cron list

# 编辑作业
openclaw cron edit <jobId> --message "Updated prompt" --model "opus"

# 立即强制运行作业
openclaw cron run <jobId>

# 仅在到期时运行
openclaw cron run <jobId> --due

# 查看运行历史
openclaw cron runs --id <jobId> --limit 50

# 删除作业
openclaw cron remove <jobId>

# 智能体选择（多智能体设置）
openclaw cron add --name "Ops sweep" --cron "0 6 * * *" --session isolated --message "Check ops queue" --agent ops
openclaw cron edit <jobId> --clear-agent
```

模型覆盖说明：

- `openclaw cron add|edit --model ...` 会更改作业所选的模型。
- 如果该模型被允许，那个精确的提供商/模型会传递到隔离的智能体运行中。
- 如果不被允许，cron 会发出警告，并回退到作业的智能体/默认模型选择。
- 已配置的回退链仍然适用，但普通的 `--model` 覆盖如果没有显式的按作业定义的回退列表，就不再静默地回退到智能体主模型作为额外重试目标。

## 配置

```json5
{
  cron: {
    enabled: true,
    store: "~/.openclaw/cron/jobs.json",
    maxConcurrentRuns: 1,
    retry: {
      maxAttempts: 3,
      backoffMs: [60000, 120000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "server_error"],
    },
    webhookToken: "replace-with-dedicated-webhook-token",
    sessionRetention: "24h",
    runLog: { maxBytes: "2mb", keepLines: 2000 },
  },
}
```

禁用 cron：`cron.enabled: false` 或 `OPENCLAW_SKIP_CRON=1`。

**一次性作业重试**：临时错误（速率限制、过载、网络、服务器错误）最多重试 3 次，并使用指数退避。永久性错误会立即禁用。

**循环作业重试**：重试之间使用指数退避（30 秒到 60 分钟）。在下一次成功运行后，退避会重置。

**维护**：`cron.sessionRetention`（默认 `24h`）会清理隔离运行的会话条目。`cron.runLog.maxBytes` / `cron.runLog.keepLines` 会自动清理运行日志文件。

## 故障排除

### 命令阶梯

```bash
openclaw status
openclaw gateway status
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
openclaw doctor
```

### Cron 未触发

- 检查 `cron.enabled` 和 `OPENCLAW_SKIP_CRON` 环境变量。
- 确认 Gateway 网关在持续运行。
- 对于 `cron` 计划，核对时区（`--tz`）与主机时区是否一致。
- 运行输出中的 `reason: not-due` 表示手动运行是通过 `openclaw cron run <jobId> --due` 检查的，而该作业尚未到期。

### Cron 已触发但没有交付

- 如果交付模式是 `none`，则不会有外部消息。
- 如果交付目标缺失/无效（`channel`/`to`），则会跳过对外发送。
- 渠道身份验证错误（`unauthorized`、`Forbidden`）表示由于凭证问题，交付被阻止。
- 如果隔离运行只返回静默令牌（`NO_REPLY` / `no_reply`），OpenClaw 会抑制直接对外发送，也会抑制后备的排队摘要路径，因此不会有任何内容回发到聊天中。
- 对于由 cron 拥有的隔离作业，不要期望智能体将 message 工具作为后备。运行器拥有最终交付；`--no-deliver` 会让它保持内部化，而不是允许直接发送。

### 时区注意事项

- 不带 `--tz` 的 cron 使用 gateway 主机时区。
- 不带时区的 `at` 计划会被视为 UTC。
- Heartbeat 的 `activeHours` 使用已配置的时区解析。

## 相关内容

- [自动化与任务](/zh-CN/automation) — 所有自动化机制总览
- [后台任务](/zh-CN/automation/tasks) — cron 执行的任务台账
- [Heartbeat](/zh-CN/gateway/heartbeat) — 定期主会话轮次
- [时区](/zh-CN/concepts/timezone) — 时区配置
