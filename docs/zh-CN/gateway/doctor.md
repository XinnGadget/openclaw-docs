---
read_when:
    - 添加或修改 Doctor 迁移时
    - 引入破坏性配置变更时
summary: Doctor 命令：健康检查、配置迁移和修复步骤
title: Doctor
x-i18n:
    generated_at: "2026-04-06T15:29:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: a834dc7aec79c20d17bc23d37fb5f5e99e628d964d55bd8cf24525a7ee57130c
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor` 是 OpenClaw 的修复 + 迁移工具。它会修复过时的配置 / 状态、检查健康状况，并提供可执行的修复步骤。

## 快速开始

```bash
openclaw doctor
```

### 无头 / 自动化

```bash
openclaw doctor --yes
```

接受默认选项而不提示（包括在适用时的重启 / 服务 / 沙箱修复步骤）。

```bash
openclaw doctor --repair
```

不经提示应用推荐修复（在安全情况下执行修复 + 重启）。

```bash
openclaw doctor --repair --force
```

也应用激进修复（会覆盖自定义 supervisor 配置）。

```bash
openclaw doctor --non-interactive
```

无提示运行，并且只应用安全迁移（配置规范化 + 磁盘状态迁移）。跳过需要人工确认的重启 / 服务 / 沙箱操作。
检测到旧状态迁移时会自动运行。

```bash
openclaw doctor --deep
```

扫描系统服务中的额外 Gateway 网关安装（launchd/systemd/schtasks）。

如果你想在写入前先查看变更，请先打开配置文件：

```bash
cat ~/.openclaw/openclaw.json
```

## 它会做什么（摘要）

- git 安装的可选预检更新（仅交互模式）。
- UI 协议新鲜度检查（当协议 schema 更新时重建 Control UI）。
- 健康检查 + 重启提示。
- Skills 状态摘要（可用 / 缺失 / 被阻止）和插件状态。
- 旧版值的配置规范化。
- 将旧版扁平 `talk.*` 字段迁移为 `talk.provider` + `talk.providers.<provider>` 的 Talk 配置迁移。
- 针对旧版 Chrome 扩展配置和 Chrome MCP 就绪状态的浏览器迁移检查。
- OpenCode 提供商覆盖警告（`models.providers.opencode` / `models.providers.opencode-go`）。
- OpenAI Codex OAuth 配置文件的 OAuth TLS 前提条件检查。
- 旧版磁盘状态迁移（sessions / agent 目录 / WhatsApp 认证）。
- 旧版插件清单契约键迁移（`speechProviders`、`realtimeTranscriptionProviders`、`realtimeVoiceProviders`、`mediaUnderstandingProviders`、`imageGenerationProviders`、`videoGenerationProviders`、`webFetchProviders`、`webSearchProviders` → `contracts`）。
- 旧版 cron 存储迁移（`jobId`、`schedule.cron`、顶层 delivery / payload 字段、payload `provider`、简单的 `notify: true` webhook 回退任务）。
- 会话锁文件检查和过时锁清理。
- 状态完整性和权限检查（sessions、transcripts、状态目录）。
- 本地运行时的配置文件权限检查（`chmod 600`）。
- 模型认证健康检查：检查 OAuth 过期、可刷新即将过期的令牌，并报告 auth-profile 冷却 / 禁用状态。
- 额外工作区目录检测（`~/openclaw`）。
- 启用沙箱隔离时的沙箱镜像修复。
- 旧版服务迁移和额外 Gateway 网关检测。
- Matrix 渠道旧版状态迁移（在 `--fix` / `--repair` 模式下）。
- Gateway 网关运行时检查（服务已安装但未运行；缓存的 launchd 标签）。
- 渠道状态警告（从正在运行的 Gateway 网关探测）。
- supervisor 配置审计（launchd/systemd/schtasks）并可选修复。
- Gateway 网关运行时最佳实践检查（Node 与 Bun、版本管理器路径）。
- Gateway 网关端口冲突诊断（默认 `18789`）。
- 针对开放私信策略的安全警告。
- 本地令牌模式下的 Gateway 网关认证检查（当没有令牌来源时提供生成令牌；不会覆盖令牌 SecretRef 配置）。
- Linux 上的 systemd linger 检查。
- 工作区 bootstrap 文件大小检查（针对上下文文件的截断 / 接近上限警告）。
- Shell 补全状态检查和自动安装 / 升级。
- Memory search embedding 提供商就绪状态检查（本地模型、远程 API 密钥或 QMD 二进制文件）。
- 源码安装检查（pnpm workspace 不匹配、缺失 UI 资源、缺失 tsx 二进制文件）。
- 写入更新后的配置 + 向导元数据。

## 详细行为和原理

### 0) 可选更新（git 安装）

如果这是一个 git 检出，并且 Doctor 正在以交互模式运行，它会先提供更新（fetch / rebase / build），然后再运行 Doctor。

### 1) 配置规范化

如果配置中包含旧版值形状（例如没有渠道专用覆盖的 `messages.ackReaction`），Doctor 会将它们规范化为当前 schema。

这也包括旧版的 Talk 扁平字段。当前公开的 Talk 配置是
`talk.provider` + `talk.providers.<provider>`。Doctor 会将旧的
`talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` 形状重写到提供商映射中。

### 2) 旧版配置键迁移

当配置包含已弃用的键时，其他命令会拒绝运行，并要求你运行
`openclaw doctor`。

Doctor 将会：

- 说明发现了哪些旧版键。
- 显示它所应用的迁移。
- 使用更新后的 schema 重写 `~/.openclaw/openclaw.json`。

当 Gateway 网关在启动时检测到旧版配置格式，也会自动运行 Doctor 迁移，因此无需手动干预就能修复过时配置。
Cron 任务存储迁移由 `openclaw doctor --fix` 处理。

当前迁移包括：

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → 顶层 `bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- 旧版 `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `messages.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `messages.tts.providers.<provider>`
- `channels.discord.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.voice.tts.providers.<provider>`
- `channels.discord.accounts.<id>.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.accounts.<id>.voice.tts.providers.<provider>`
- `plugins.entries.voice-call.config.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `plugins.entries.voice-call.config.tts.providers.<provider>`
- `plugins.entries.voice-call.config.provider: "log"` → `"mock"`
- `plugins.entries.voice-call.config.twilio.from` → `plugins.entries.voice-call.config.fromNumber`
- `plugins.entries.voice-call.config.streaming.sttProvider` → `plugins.entries.voice-call.config.streaming.provider`
- `plugins.entries.voice-call.config.streaming.openaiApiKey|sttModel|silenceDurationMs|vadThreshold`
  → `plugins.entries.voice-call.config.streaming.providers.openai.*`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- 对于配置了命名 `accounts`、但仍保留单账户顶层渠道值的渠道，将这些账户范围的值移动到该渠道所选的提升账户中（大多数渠道使用 `accounts.default`；Matrix 可以保留现有匹配的命名 / 默认目标）
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*`（tools / elevated / exec / sandbox / subagents）
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- 删除 `browser.relayBindHost`（旧版扩展 relay 设置）

Doctor 警告还包括针对多账户渠道的账户默认值指导：

- 如果配置了两个或更多 `channels.<channel>.accounts` 条目，但没有 `channels.<channel>.defaultAccount` 或 `accounts.default`，Doctor 会警告回退路由可能会选择意外的账户。
- 如果 `channels.<channel>.defaultAccount` 设置为未知账户 ID，Doctor 会发出警告并列出已配置的账户 ID。

### 2b) OpenCode 提供商覆盖

如果你手动添加了 `models.providers.opencode`、`opencode-zen` 或 `opencode-go`，
它会覆盖来自 `@mariozechner/pi-ai` 的内置 OpenCode 目录。
这可能会把模型强制路由到错误的 API，或将成本清零。Doctor 会发出警告，以便你移除覆盖并恢复按模型的 API 路由 + 成本。

### 2c) 浏览器迁移和 Chrome MCP 就绪状态

如果你的浏览器配置仍然指向已移除的 Chrome 扩展路径，Doctor 会将其规范化为当前的主机本地 Chrome MCP 附加模型：

- `browser.profiles.*.driver: "extension"` 会变为 `"existing-session"`
- `browser.relayBindHost` 会被移除

当你使用 `defaultProfile:
"user"` 或已配置的 `existing-session` 配置文件时，Doctor 还会审计主机本地 Chrome MCP 路径：

- 检查默认自动连接配置文件所在的同一主机上是否安装了 Google Chrome
- 检查检测到的 Chrome 版本，并在低于 Chrome 144 时发出警告
- 提醒你在浏览器 inspect 页面启用远程调试（例如
  `chrome://inspect/#remote-debugging`、`brave://inspect/#remote-debugging`，
  或 `edge://inspect/#remote-debugging`）

Doctor 无法替你启用 Chrome 侧设置。主机本地 Chrome MCP 仍然需要：

- Gateway 网关 / 节点主机上安装 Chromium 内核浏览器 144+
- 浏览器在本地运行
- 在该浏览器中启用远程调试
- 在浏览器中批准首次附加同意提示

这里的就绪状态仅涉及本地附加前提条件。Existing-session 仍保留当前 Chrome MCP 路由限制；像 `responsebody`、PDF 导出、下载拦截和批处理操作等高级路由仍然需要托管浏览器或原始 CDP 配置文件。

此检查**不**适用于 Docker、沙箱、remote-browser 或其他无头流程。这些流程仍继续使用原始 CDP。

### 2d) OAuth TLS 前提条件

当配置了 OpenAI Codex OAuth 配置文件时，Doctor 会探测 OpenAI 授权端点，以验证本地 Node / OpenSSL TLS 栈是否可以校验证书链。如果探测因证书错误失败（例如 `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`、证书过期或自签名证书），Doctor 会打印平台专用修复指引。在 macOS 上，如果使用 Homebrew Node，修复通常是 `brew postinstall ca-certificates`。使用 `--deep` 时，即使 Gateway 网关健康，该探测也会运行。

### 3) 旧版状态迁移（磁盘布局）

Doctor 可以将旧版磁盘布局迁移到当前结构：

- Sessions 存储 + transcripts：
  - 从 `~/.openclaw/sessions/` 到 `~/.openclaw/agents/<agentId>/sessions/`
- Agent 目录：
  - 从 `~/.openclaw/agent/` 到 `~/.openclaw/agents/<agentId>/agent/`
- WhatsApp 认证状态（Baileys）：
  - 从旧版 `~/.openclaw/credentials/*.json`（不包括 `oauth.json`）
  - 到 `~/.openclaw/credentials/whatsapp/<accountId>/...`（默认账户 id：`default`）

这些迁移尽力而为且具有幂等性；如果保留了任何旧版文件夹作为备份，Doctor 会发出警告。
Gateway 网关 / CLI 也会在启动时自动迁移旧版 sessions + agent 目录，因此历史记录 / 认证 / 模型会落到按智能体划分的路径中，而无需手动运行 Doctor。WhatsApp 认证有意只通过 `openclaw doctor` 迁移。Talk provider / provider-map 规范化现在按结构相等性比较，因此仅键顺序不同的差异不再触发重复的无操作 `doctor --fix` 变更。

### 3a) 旧版插件清单迁移

Doctor 会扫描所有已安装插件清单中已弃用的顶层能力键
（`speechProviders`、`realtimeTranscriptionProviders`、
`realtimeVoiceProviders`、`mediaUnderstandingProviders`、
`imageGenerationProviders`、`videoGenerationProviders`、`webFetchProviders`、
`webSearchProviders`）。发现后，它会提示将它们移动到 `contracts`
对象中，并原地重写清单文件。此迁移是幂等的；
如果 `contracts` 键中已经有相同值，就会删除旧版键，
而不会重复数据。

### 3b) 旧版 cron 存储迁移

Doctor 还会检查 cron 任务存储（默认为 `~/.openclaw/cron/jobs.json`，
若有覆盖则使用 `cron.store`）中旧版任务形状，这些形状调度器仍为兼容性而接受。

当前 cron 清理包括：

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- 顶层 payload 字段（`message`、`model`、`thinking`、...）→ `payload`
- 顶层 delivery 字段（`deliver`、`channel`、`to`、`provider`、...）→ `delivery`
- payload `provider` delivery 别名 → 显式 `delivery.channel`
- 简单的旧版 `notify: true` webhook 回退任务 → 显式 `delivery.mode="webhook"` 且 `delivery.to=cron.webhook`

Doctor 仅在能够不改变行为的前提下自动迁移 `notify: true` 任务。如果某个任务将旧版 notify 回退与现有的非 webhook 传递模式结合使用，Doctor 会发出警告，并将该任务留待手动审查。

### 3c) 会话锁清理

Doctor 会扫描每个智能体会话目录中的过时写锁文件 —— 这些文件是会话异常退出时残留的。对每个找到的锁文件，它会报告：
路径、PID、PID 是否仍存活、锁龄，以及是否被视为过时（PID 已死或已超过 30 分钟）。在 `--fix` / `--repair`
模式下，它会自动移除过时锁文件；否则它会打印说明，并指导你使用 `--fix` 重新运行。

### 4) 状态完整性检查（会话持久化、路由和安全）

状态目录是运行时的中枢神经。如果它消失了，你会丢失
sessions、凭证、日志和配置（除非你在其他地方有备份）。

Doctor 会检查：

- **状态目录缺失**：警告灾难性的状态丢失，提示重新创建目录，并提醒你它无法恢复缺失数据。
- **状态目录权限**：验证可写性；提供修复权限的选项
  （并在检测到 owner / group 不匹配时给出 `chown` 提示）。
- **macOS 云同步状态目录**：当状态路径解析到 iCloud Drive
  （`~/Library/Mobile Documents/com~apple~CloudDocs/...`）或
  `~/Library/CloudStorage/...` 下时发出警告，因为同步支持路径可能导致更慢的 I/O
  以及锁 / 同步竞争。
- **Linux SD 或 eMMC 状态目录**：当状态路径解析为 `mmcblk*`
  挂载源时发出警告，因为由 SD 或 eMMC 支持的随机 I/O 在 session 和凭证写入下可能更慢且磨损更快。
- **Session 目录缺失**：`sessions/` 和 session 存储目录是持久化历史记录并避免 `ENOENT` 崩溃所必需的。
- **Transcript 不匹配**：当最近的 session 条目缺少 transcript 文件时发出警告。
- **主 Session “单行 JSONL”**：当主 transcript 只有一行时标记出来（历史没有持续累积）。
- **多个状态目录**：当不同 home 目录中存在多个 `~/.openclaw` 文件夹，或 `OPENCLAW_STATE_DIR` 指向其他位置时发出警告（历史可能会在不同安装之间拆分）。
- **远程模式提醒**：如果 `gateway.mode=remote`，Doctor 会提醒你在远程主机上运行它（状态保存在那里）。
- **配置文件权限**：如果 `~/.openclaw/openclaw.json`
  对组 / 所有人可读，会发出警告并提供收紧到 `600` 的选项。

### 5) 模型认证健康状态（OAuth 过期）

Doctor 会检查认证存储中的 OAuth 配置文件，在令牌即将过期 / 已过期时发出警告，并在安全时刷新它们。如果 Anthropic
OAuth / 令牌配置文件已过时，它会建议使用 Anthropic API 密钥或
Anthropic setup-token 路径。
刷新提示仅在交互模式（TTY）下出现；`--non-interactive`
会跳过刷新尝试。

Doctor 还会报告因以下原因而暂时不可用的认证配置文件：

- 短期冷却（限流 / 超时 / 认证失败）
- 较长时间禁用（计费 / 额度失败）

### 6) Hooks 模型校验

如果设置了 `hooks.gmail.model`，Doctor 会根据目录和 allowlist 校验模型引用，并在其无法解析或不被允许时发出警告。

### 7) 沙箱镜像修复

启用沙箱隔离时，Doctor 会检查 Docker 镜像，并在当前镜像缺失时提供构建或切换到旧版名称的选项。

### 7b) 内置插件运行时依赖

Doctor 会验证内置插件运行时依赖（例如
Discord 插件运行时包）是否存在于 OpenClaw 安装根目录中。
如果有缺失，Doctor 会报告这些包，并在
`openclaw doctor --fix` / `openclaw doctor --repair` 模式下安装它们。

### 8) Gateway 网关服务迁移和清理提示

Doctor 会检测旧版 Gateway 网关服务（launchd/systemd/schtasks），
并提供移除它们以及使用当前 Gateway 网关端口安装 OpenClaw 服务的选项。
它还可以扫描额外的类似 Gateway 网关服务并打印清理提示。
带 profile 名称的 OpenClaw Gateway 网关服务被视为一等公民，不会被标记为“额外”。

### 8b) 启动时 Matrix 迁移

当 Matrix 渠道账户存在待处理或可执行的旧版状态迁移时，
Doctor（在 `--fix` / `--repair` 模式下）会先创建迁移前快照，
然后运行尽力而为的迁移步骤：旧版 Matrix 状态迁移和旧版加密状态准备。这两步都不是致命的；错误会被记录，启动会继续进行。在只读模式下（不带 `--fix` 的 `openclaw doctor`），此检查会被完全跳过。

### 9) 安全警告

当某个提供商对私信开放但没有 allowlist，或某项策略配置方式存在危险时，Doctor 会发出警告。

### 10) systemd linger（Linux）

如果作为 systemd 用户服务运行，Doctor 会确保启用了 lingering，这样 Gateway 网关在注销后仍能保持运行。

### 11) 工作区状态（Skills、插件和旧版目录）

Doctor 会打印默认智能体的工作区状态摘要：

- **Skills 状态**：统计可用、缺少要求和被 allowlist 阻止的 Skills 数量。
- **旧版工作区目录**：当 `~/openclaw` 或其他旧版工作区目录与当前工作区并存时发出警告。
- **插件状态**：统计已加载 / 已禁用 / 出错的插件；列出所有错误对应的插件 ID；报告内置插件能力。
- **插件兼容性警告**：标记与当前运行时存在兼容性问题的插件。
- **插件诊断信息**：展示插件注册表在加载时发出的任何警告或错误。

### 11b) Bootstrap 文件大小

Doctor 会检查工作区 bootstrap 文件（例如 `AGENTS.md`、
`CLAUDE.md` 或其他注入的上下文文件）是否接近或超过已配置的字符预算。它会报告每个文件的原始字符数与注入字符数、截断百分比、截断原因（`max/file` 或 `max/total`），以及总注入字符数占总预算的比例。当文件被截断或接近上限时，Doctor 会打印关于调整 `agents.defaults.bootstrapMaxChars`
和 `agents.defaults.bootstrapTotalMaxChars` 的提示。

### 11c) Shell 补全

Doctor 会检查当前 shell
（zsh、bash、fish 或 PowerShell）是否已安装 Tab 补全：

- 如果 shell 配置文件使用较慢的动态补全模式
  （`source <(openclaw completion ...)`），Doctor 会将其升级为更快的缓存文件变体。
- 如果配置文件中已配置补全，但缓存文件缺失，
  Doctor 会自动重新生成缓存。
- 如果根本未配置补全，Doctor 会提示安装它
  （仅交互模式；`--non-interactive` 时跳过）。

运行 `openclaw completion --write-state` 可手动重新生成缓存。

### 12) Gateway 网关认证检查（本地令牌）

Doctor 会检查本地 Gateway 网关令牌认证的就绪状态。

- 如果令牌模式需要令牌且没有令牌来源，Doctor 会提供生成令牌的选项。
- 如果 `gateway.auth.token` 由 SecretRef 管理但不可用，Doctor 会发出警告，并且不会用明文覆盖它。
- `openclaw doctor --generate-gateway-token` 仅在未配置令牌 SecretRef 时强制生成。

### 12b) 只读 SecretRef 感知修复

某些修复流程需要检查已配置凭证，而不削弱运行时快速失败行为。

- `openclaw doctor --fix` 现在使用与 status 系列命令相同的只读 SecretRef 摘要模型，以执行定向配置修复。
- 例如：Telegram `allowFrom` / `groupAllowFrom` 的 `@username` 修复会在可用时尝试使用已配置的 bot 凭证。
- 如果 Telegram bot 令牌通过 SecretRef 配置，但在当前命令路径中不可用，Doctor 会报告该凭证为“已配置但不可用”，并跳过自动解析，而不是崩溃或错误地将令牌报告为缺失。

### 13) Gateway 网关健康检查 + 重启

Doctor 会运行健康检查，并在 Gateway 网关看起来不健康时提供重启选项。

### 13b) Memory search 就绪状态

Doctor 会检查默认智能体配置的 memory search embedding 提供商是否就绪。其行为取决于配置的后端和提供商：

- **QMD 后端**：探测 `qmd` 二进制文件是否可用且可启动。
  如果不可用，会打印修复指引，包括 npm 包和手动二进制路径选项。
- **显式本地提供商**：检查本地模型文件或可识别的远程 / 可下载模型 URL。
  如果缺失，会建议切换到远程提供商。
- **显式远程提供商**（`openai`、`voyage` 等）：验证环境中或认证存储中是否存在 API 密钥。若缺失，会打印可执行的修复提示。
- **自动提供商**：先检查本地模型可用性，再按自动选择顺序尝试各个远程提供商。

当 Gateway 网关探测结果可用时（检查时 Gateway 网关健康），Doctor 会将其结果与 CLI 可见配置交叉比对，并指出任何差异。

使用 `openclaw memory status --deep` 可在运行时验证 embedding 就绪状态。

### 14) 渠道状态警告

如果 Gateway 网关健康，Doctor 会运行渠道状态探测，并报告带有建议修复方案的警告。

### 15) Supervisor 配置审计 + 修复

Doctor 会检查已安装的 supervisor 配置（launchd/systemd/schtasks）是否缺少或过时默认值（例如 systemd network-online 依赖和重启延迟）。发现不匹配时，它会建议更新，并可将服务文件 / 任务重写为当前默认值。

说明：

- `openclaw doctor` 在重写 supervisor 配置前会提示。
- `openclaw doctor --yes` 会接受默认修复提示。
- `openclaw doctor --repair` 会不经提示应用推荐修复。
- `openclaw doctor --repair --force` 会覆盖自定义 supervisor 配置。
- 如果令牌认证需要令牌且 `gateway.auth.token` 由 SecretRef 管理，Doctor 在服务安装 / 修复时会校验 SecretRef，但不会把解析出的明文令牌值持久化到 supervisor 服务环境元数据中。
- 如果令牌认证需要令牌且配置的令牌 SecretRef 未解析，Doctor 会阻止安装 / 修复路径，并提供可执行的指引。
- 如果同时配置了 `gateway.auth.token` 和 `gateway.auth.password`，但未设置 `gateway.auth.mode`，Doctor 会阻止安装 / 修复，直到显式设置模式。
- 对于 Linux user-systemd 单元，Doctor 的令牌漂移检查现在同时包括 `Environment=` 和 `EnvironmentFile=` 来源，以比较服务认证元数据。
- 你始终可以通过 `openclaw gateway install --force` 强制执行完整重写。

### 16) Gateway 网关运行时 + 端口诊断

Doctor 会检查服务运行时（PID、上次退出状态），并在服务已安装但实际上未运行时发出警告。它还会检查 Gateway 网关端口（默认 `18789`）上的端口冲突，并报告可能原因（Gateway 网关已在运行、SSH 隧道）。

### 17) Gateway 网关运行时最佳实践

当 Gateway 网关服务运行在 Bun 上，或使用版本管理的 Node 路径
（`nvm`、`fnm`、`volta`、`asdf` 等）时，Doctor 会发出警告。WhatsApp + Telegram 渠道需要 Node，而版本管理器路径可能会在升级后失效，因为服务不会加载你的 shell init。Doctor 会在系统 Node 安装可用时提供迁移到该安装的选项（Homebrew / apt / choco）。

### 18) 配置写入 + 向导元数据

Doctor 会持久化所有配置变更，并写入向导元数据以记录此次 Doctor 运行。

### 19) 工作区提示（备份 + memory system）

当工作区缺少 memory system 时，Doctor 会建议添加；如果工作区尚未纳入 git，它还会打印备份提示。

有关工作区结构和 git 备份（推荐使用私有 GitHub 或 GitLab）的完整指南，请参阅 [/concepts/agent-workspace](/zh-CN/concepts/agent-workspace)。
