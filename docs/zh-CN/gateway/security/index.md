---
read_when:
    - 添加会扩大访问范围或自动化程度的功能
summary: 运行具有 Shell 访问权限的 AI Gateway 网关时的安全注意事项和威胁模型
title: 安全性
x-i18n:
    generated_at: "2026-04-12T18:22:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7f3ef693813b696be2e24bcc333c8ee177fa56c3cb06c5fac12a0bd220a29917
    source_path: gateway/security/index.md
    workflow: 15
---

# 安全性

<Warning>
**个人助理信任模型：** 本指南假设每个 Gateway 网关只有一个受信任的操作员边界（单用户 / 个人助理模型）。
OpenClaw **不是** 用于多个对抗性用户共享同一个智能体 / Gateway 网关时的恶意多租户安全边界。
如果你需要混合信任或对抗性用户场景，请拆分信任边界（单独的 Gateway 网关 + 凭证，最好还要使用单独的 OS 用户 / 主机）。
</Warning>

**本页内容：** [信任模型](#scope-first-personal-assistant-security-model) | [快速审计](#quick-check-openclaw-security-audit) | [强化基线](#hardened-baseline-in-60-seconds) | [私信访问模型](#dm-access-model-pairing-allowlist-open-disabled) | [配置加固](#configuration-hardening-examples) | [事件响应](#incident-response)

## 首先明确范围：个人助理安全模型

OpenClaw 的安全指南假设你部署的是一个**个人助理**：一个受信任的操作员边界，可能包含多个智能体。

- 支持的安全姿态：每个 Gateway 网关一个用户 / 信任边界（最好每个边界对应一个 OS 用户 / 主机 / VPS）。
- 不受支持的安全边界：多个彼此不受信任或具有对抗关系的用户共享同一个 Gateway 网关 / 智能体。
- 如果需要对抗性用户隔离，请按信任边界拆分（单独的 Gateway 网关 + 凭证，最好还要使用单独的 OS 用户 / 主机）。
- 如果多个不受信任的用户都能向同一个启用了工具的智能体发消息，请把他们视为共享该智能体的同一组委派工具权限。

本页说明的是**在该模型内**如何加固。它并不声称单个共享 Gateway 网关可以提供恶意多租户隔离。

## 快速检查：`openclaw security audit`

另请参阅：[形式化验证（安全模型）](/zh-CN/security/formal-verification)

请定期运行它（尤其是在修改配置或暴露网络面之后）：

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
openclaw security audit --json
```

`security audit --fix` 的范围被刻意保持很窄：它会把常见的开放群组策略切换为 allowlist，恢复 `logging.redactSensitive: "tools"`，收紧状态 / 配置 / include 文件的权限，并在 Windows 上使用 Windows ACL 重置，而不是 POSIX `chmod`。

它会标记常见的易踩坑配置（Gateway 网关身份验证暴露、浏览器控制暴露、提升权限的 allowlist、文件系统权限、宽松的 exec 批准，以及开放渠道的工具暴露）。

OpenClaw 既是一个产品，也是一个实验：你正在把前沿模型行为接到真实的消息渠道和真实工具上。**不存在“绝对安全”的配置。** 目标是有意识地决定：

- 谁可以和你的机器人对话
- 机器人被允许在哪里执行操作
- 机器人可以接触什么

先从仍然可用的最小访问范围开始，随着信心增加再逐步放宽。

### 部署与主机信任

OpenClaw 假设主机和配置边界是受信任的：

- 如果有人可以修改 Gateway 网关主机状态 / 配置（`~/.openclaw`，包括 `openclaw.json`），请把他们视为受信任的操作员。
- 让多个彼此不受信任 / 具有对抗关系的操作员共用一个 Gateway 网关 **不是推荐配置**。
- 对于混合信任团队，请使用单独的 Gateway 网关 来拆分信任边界（至少也要使用单独的 OS 用户 / 主机）。
- 推荐默认做法：每台机器 / 主机（或 VPS）一个用户，该用户一个 Gateway 网关，该 Gateway 网关中可运行一个或多个智能体。
- 在单个 Gateway 网关实例内部，经过身份验证的操作员访问属于受信任的控制平面角色，而不是按用户区分的租户角色。
- 会话标识符（`sessionKey`、会话 ID、标签）是路由选择器，不是授权令牌。
- 如果多个人都可以向同一个启用了工具的智能体发消息，那么他们每个人都可以驱动同一组权限。按用户隔离的会话 / Memory 虽然有助于保护隐私，但并不能把共享智能体变成按用户授权的主机权限边界。

### 共享 Slack 工作区：真实风险

如果“Slack 中的所有人都可以给机器人发消息”，核心风险是委派工具权限：

- 任何被允许的发送者都可以在该智能体的策略范围内诱发工具调用（`exec`、浏览器、网络 / 文件工具）；
- 某个发送者的提示 / 内容注入，可能导致影响共享状态、设备或输出的操作；
- 如果某个共享智能体拥有敏感凭证 / 文件，那么任何被允许的发送者都可能通过工具使用驱动数据外泄。

对团队工作流，请使用工具最少化的单独智能体 / Gateway 网关；保存个人数据的智能体应保持私有。

### 公司共享智能体：可接受模式

当使用该智能体的所有人都位于同一信任边界内（例如同一个公司团队），并且该智能体严格限定在业务范围内时，这是可以接受的。

- 在专用机器 / VM / 容器中运行它；
- 为该运行时使用专用的 OS 用户 + 专用的浏览器 / 配置文件 / 账号；
- 不要让该运行时登录个人 Apple / Google 账号，或个人密码管理器 / 浏览器配置文件。

如果你在同一个运行时中混用个人身份与公司身份，就会打破这种隔离，并增加个人数据暴露风险。

## Gateway 网关与节点的信任概念

请将 Gateway 网关和节点视为同一个操作员信任域中的不同角色：

- **Gateway 网关** 是控制平面和策略层（`gateway.auth`、工具策略、路由）。
- **节点** 是与该 Gateway 网关配对的远程执行面（命令、设备操作、主机本地能力）。
- 通过 Gateway 网关身份验证的调用方，在 Gateway 网关范围内是受信任的。完成配对后，节点操作就属于该节点上的受信任操作员行为。
- `sessionKey` 是路由 / 上下文选择，不是按用户划分的身份验证。
- Exec 批准（allowlist + 询问）是为了约束操作员意图的护栏，而不是恶意多租户隔离。
- OpenClaw 针对受信任单操作员场景的产品默认值，是允许在 `gateway` / `node` 上直接执行主机命令而不弹出批准提示（`security="full"`、`ask="off"`，除非你主动收紧）。这是有意为之的 UX 默认值，本身并不是漏洞。
- Exec 批准会绑定精确的请求上下文，以及尽力识别的直接本地文件操作数；它不会对所有运行时 / 解释器加载路径进行语义建模。如果你需要强边界，请使用沙箱隔离和主机级隔离。

如果你需要恶意用户隔离，请按 OS 用户 / 主机拆分信任边界，并运行单独的 Gateway 网关。

## 信任边界矩阵

在进行风险分级时，可将其作为快速模型：

| 边界或控制项 | 它的含义 | 常见误解 |
| --------------------------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------- |
| `gateway.auth`（token / password / trusted-proxy / device auth） | 对 Gateway 网关 API 的调用方进行身份验证 | “要安全，就必须对每一帧消息都做签名” |
| `sessionKey` | 用于上下文 / 会话选择的路由键 | “会话 key 是用户身份验证边界” |
| 提示 / 内容护栏 | 降低模型被滥用的风险 | “仅凭提示注入就能证明身份验证被绕过” |
| `canvas.eval` / 浏览器 evaluate | 启用时属于有意提供给操作员的能力 | “任何 JS eval 原语在这个信任模型里都会自动构成漏洞” |
| 本地 TUI `!` shell | 由操作员显式触发的本地执行 | “本地 shell 便捷命令就是远程注入” |
| 节点配对与节点命令 | 对已配对设备进行操作员级远程执行 | “远程设备控制默认应视为不受信任用户访问” |

## 按设计不属于漏洞的情况

以下模式经常被报告，但通常会以无需处理关闭，除非能证明存在真实的边界绕过：

- 仅有提示注入链，而没有策略 / 身份验证 / 沙箱绕过。
- 假设在单一共享主机 / 配置上存在恶意多租户运行的主张。
- 把正常的操作员读取路径访问（例如 `sessions.list` / `sessions.preview` / `chat.history`）在共享 Gateway 网关场景下归类为 IDOR 的说法。
- 仅限 localhost 的部署问题（例如仅 loopback Gateway 网关上的 HSTS）。
- 针对本仓库中并不存在的入站路径而提出的 Discord 入站 webhook 签名问题。
- 把节点配对元数据视为 `system.run` 的隐藏第二层逐命令批准机制的报告，而实际执行边界仍然是 Gateway 网关的全局节点命令策略加上节点自身的 exec 批准。
- 把 `sessionKey` 当作身份验证令牌，并据此提出“缺少按用户授权”的发现。

## 研究人员预检查清单

在提交 GHSA 之前，请确认以下所有事项：

1. 在最新 `main` 或最新发布版本上仍可复现。
2. 报告包含精确的代码路径（`file`、函数、行范围）以及已测试的版本 / commit。
3. 影响跨越了某个文档化的信任边界（而不只是提示注入）。
4. 该主张未列在 [Out of Scope](https://github.com/openclaw/openclaw/blob/main/SECURITY.md#out-of-scope) 中。
5. 已检查现有安全通告是否重复（适用时复用规范的 GHSA）。
6. 已明确部署假设（loopback / 本地 还是对外暴露，受信任操作员还是不受信任操作员）。

## 在 60 秒内建立强化基线

先使用这套基线，然后再按受信任智能体逐项重新启用工具：

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    auth: { mode: "token", token: "replace-with-long-random-token" },
  },
  session: {
    dmScope: "per-channel-peer",
  },
  tools: {
    profile: "messaging",
    deny: ["group:automation", "group:runtime", "group:fs", "sessions_spawn", "sessions_send"],
    fs: { workspaceOnly: true },
    exec: { security: "deny", ask: "always" },
    elevated: { enabled: false },
  },
  channels: {
    whatsapp: { dmPolicy: "pairing", groups: { "*": { requireMention: true } } },
  },
}
```

这样会将 Gateway 网关保持为仅本地可访问，隔离私信，并默认禁用控制平面 / 运行时工具。

## 共享收件箱快速规则

如果有多个人可以给你的机器人发私信：

- 设置 `session.dmScope: "per-channel-peer"`（多账号渠道则用 `"per-account-channel-peer"`）。
- 保持 `dmPolicy: "pairing"` 或使用严格的 allowlist。
- 绝不要把共享私信和宽泛的工具访问结合起来。
- 这可以加固协作式 / 共享收件箱，但当用户共享主机 / 配置写权限时，它并不是为恶意共租户隔离而设计的。

## 上下文可见性模型

OpenClaw 区分两个概念：

- **触发授权**：谁可以触发智能体（`dmPolicy`、`groupPolicy`、allowlist、提及门控）。
- **上下文可见性**：哪些补充上下文会被注入模型输入（回复正文、引用文本、线程历史、转发元数据）。

Allowlists 用于控制触发和命令授权。`contextVisibility` 设置控制补充上下文（引用回复、线程根消息、拉取的历史记录）的过滤方式：

- `contextVisibility: "all"`（默认）会按接收到的内容保留全部补充上下文。
- `contextVisibility: "allowlist"` 会将补充上下文过滤为仅包含通过当前 allowlist 检查的发送者内容。
- `contextVisibility: "allowlist_quote"` 的行为类似 `allowlist`，但仍保留一条显式引用的回复。

你可以按渠道或按房间 / 会话设置 `contextVisibility`。具体配置细节请参阅 [群聊](/zh-CN/channels/groups#context-visibility-and-allowlists)。

安全通告分级指南：

- 如果报告只展示了“模型可以看到来自未列入 allowlist 的发送者的引用或历史文本”，这属于可通过 `contextVisibility` 处理的加固问题，而不是身份验证或沙箱边界绕过本身。
- 要构成安全影响，报告仍然需要证明跨越了某个信任边界（身份验证、策略、沙箱、批准机制，或其他文档化边界）。

## 审计会检查什么（高层级）

- **入站访问**（私信策略、群组策略、allowlist）：陌生人是否可以触发机器人？
- **工具爆炸半径**（提升权限工具 + 开放房间）：提示注入是否可能演变为 Shell / 文件 / 网络操作？
- **Exec 批准漂移**（`security=full`、`autoAllowSkills`、未启用 `strictInlineEval` 的解释器 allowlist）：主机 exec 护栏是否仍然按你的预期工作？
  - `security="full"` 是一种广义姿态警告，并不等于证明存在漏洞。它是受信任个人助理场景下有意选择的默认值；只有当你的威胁模型确实需要批准或 allowlist 护栏时，才需要收紧它。
- **网络暴露**（Gateway 网关 bind / auth、Tailscale Serve / Funnel、弱或过短的身份验证 token）。
- **浏览器控制暴露**（远程节点、中继端口、远程 CDP 端点）。
- **本地磁盘卫生**（权限、符号链接、配置 includes、“同步文件夹”路径）。
- **插件**（存在扩展，但没有显式 allowlist）。
- **策略漂移 / 配置错误**（已配置 sandbox docker 设置但沙箱模式关闭；无效的 `gateway.nodes.denyCommands` 模式，因为匹配仅针对精确命令名（例如 `system.run`），不会检查 Shell 文本；危险的 `gateway.nodes.allowCommands` 条目；全局 `tools.profile="minimal"` 被按智能体配置覆盖；在宽松工具策略下仍可访问扩展插件工具）。
- **运行时期望漂移**（例如误以为隐式 exec 仍表示 `sandbox`，而 `tools.exec.host` 现在默认是 `auto`；或者显式设置 `tools.exec.host="sandbox"`，但沙箱模式实际上已关闭）。
- **模型卫生**（当已配置模型看起来像旧模型时发出警告；不是硬性阻断）。

如果你运行 `--deep`，OpenClaw 还会尽力尝试进行实时 Gateway 网关探测。

## 凭证存储映射

在审计访问范围或决定备份内容时，可以参考这一节：

- **WhatsApp**：`~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
- **Telegram 机器人 token**：配置 / 环境变量，或 `channels.telegram.tokenFile`（仅接受常规文件；拒绝符号链接）
- **Discord 机器人 token**：配置 / 环境变量，或 SecretRef（env / file / exec providers）
- **Slack tokens**：配置 / 环境变量（`channels.slack.*`）
- **配对 allowlist**：
  - `~/.openclaw/credentials/<channel>-allowFrom.json`（默认账号）
  - `~/.openclaw/credentials/<channel>-<accountId>-allowFrom.json`（非默认账号）
- **模型 auth 配置文件**：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **基于文件的 secrets 负载（可选）**：`~/.openclaw/secrets.json`
- **旧版 OAuth 导入**：`~/.openclaw/credentials/oauth.json`

## 安全审计清单

当审计输出发现项时，请按以下优先顺序处理：

1. **任何“开放”且启用了工具的配置**：先锁定私信 / 群组（pairing / allowlist），然后收紧工具策略 / 沙箱隔离。
2. **公共网络暴露**（LAN bind、Funnel、缺少身份验证）：立即修复。
3. **浏览器控制的远程暴露**：将其视为操作员级访问（仅 tailnet、审慎配对节点、避免公开暴露）。
4. **权限**：确保状态 / 配置 / 凭证 / auth 文件对组用户或所有人都不可读。
5. **插件 / 扩展**：只加载你明确信任的内容。
6. **模型选择**：对于任何启用了工具的机器人，优先使用现代、具备更强指令防护能力的模型。

## 安全审计术语表

你在真实部署中最可能看到的一些高信号 `checkId` 值如下（并非完整列表）：

| `checkId` | 严重级别 | 重要原因 | 主要修复键 / 路径 | 自动修复 |
| ------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | -------- |
| `fs.state_dir.perms_world_writable` | critical | 其他用户 / 进程可以修改完整的 OpenClaw 状态 | `~/.openclaw` 的文件系统权限 | yes |
| `fs.state_dir.perms_group_writable` | warn | 组内用户可以修改完整的 OpenClaw 状态 | `~/.openclaw` 的文件系统权限 | yes |
| `fs.state_dir.perms_readable` | warn | 其他人可以读取状态目录 | `~/.openclaw` 的文件系统权限 | yes |
| `fs.state_dir.symlink` | warn | 状态目录目标变成另一个信任边界 | 状态目录文件系统布局 | no |
| `fs.config.perms_writable` | critical | 其他人可以更改 auth / 工具策略 / 配置 | `~/.openclaw/openclaw.json` 的文件系统权限 | yes |
| `fs.config.symlink` | warn | 配置目标变成另一个信任边界 | 配置文件文件系统布局 | no |
| `fs.config.perms_group_readable` | warn | 组内用户可以读取配置 token / 设置 | 配置文件的文件系统权限 | yes |
| `fs.config.perms_world_readable` | critical | 配置可能暴露 token / 设置 | 配置文件的文件系统权限 | yes |
| `fs.config_include.perms_writable` | critical | 配置 include 文件可被其他人修改 | `openclaw.json` 引用的 include 文件权限 | yes |
| `fs.config_include.perms_group_readable` | warn | 组内用户可以读取包含的 secrets / 设置 | `openclaw.json` 引用的 include 文件权限 | yes |
| `fs.config_include.perms_world_readable` | critical | 包含的 secrets / 设置对所有人可读 | `openclaw.json` 引用的 include 文件权限 | yes |
| `fs.auth_profiles.perms_writable` | critical | 其他人可以注入或替换已存储的模型凭证 | `agents/<agentId>/agent/auth-profiles.json` 的权限 | yes |
| `fs.auth_profiles.perms_readable` | warn | 其他人可以读取 API keys 和 OAuth tokens | `agents/<agentId>/agent/auth-profiles.json` 的权限 | yes |
| `fs.credentials_dir.perms_writable` | critical | 其他人可以修改渠道配对 / 凭证状态 | `~/.openclaw/credentials` 的文件系统权限 | yes |
| `fs.credentials_dir.perms_readable` | warn | 其他人可以读取渠道凭证状态 | `~/.openclaw/credentials` 的文件系统权限 | yes |
| `fs.sessions_store.perms_readable` | warn | 其他人可以读取会话转录 / 元数据 | 会话存储权限 | yes |
| `fs.log_file.perms_readable` | warn | 其他人可以读取虽经脱敏但仍然敏感的日志 | Gateway 网关日志文件权限 | yes |
| `fs.synced_dir` | warn | iCloud / Dropbox / Drive 中的状态 / 配置会扩大 token / 转录内容暴露范围 | 将配置 / 状态移出同步文件夹 | no |
| `gateway.bind_no_auth` | critical | 远程 bind 但没有共享密钥 | `gateway.bind`、`gateway.auth.*` | no |
| `gateway.loopback_no_auth` | critical | 经反向代理暴露的 loopback 可能变成无身份验证访问 | `gateway.auth.*`、代理设置 | no |
| `gateway.trusted_proxies_missing` | warn | 存在反向代理头，但未信任代理来源 | `gateway.trustedProxies` | no |
| `gateway.http.no_auth` | warn/critical | 可通过 `auth.mode="none"` 访问 Gateway 网关 HTTP API | `gateway.auth.mode`、`gateway.http.endpoints.*` | no |
| `gateway.http.session_key_override_enabled` | info | HTTP API 调用方可以覆盖 `sessionKey` | `gateway.http.allowSessionKeyOverride` | no |
| `gateway.tools_invoke_http.dangerous_allow` | warn/critical | 通过 HTTP API 重新启用了危险工具 | `gateway.tools.allow` | no |
| `gateway.nodes.allow_commands_dangerous` | warn/critical | 启用了高影响节点命令（相机 / 屏幕 / 通讯录 / 日历 / 短信） | `gateway.nodes.allowCommands` | no |
| `gateway.nodes.deny_commands_ineffective` | warn | 类似模式的 deny 条目不会匹配 Shell 文本或分组 | `gateway.nodes.denyCommands` | no |
| `gateway.tailscale_funnel` | critical | 公开互联网暴露 | `gateway.tailscale.mode` | no |
| `gateway.tailscale_serve` | info | 已通过 Serve 启用 tailnet 暴露 | `gateway.tailscale.mode` | no |
| `gateway.control_ui.allowed_origins_required` | critical | 非 loopback 的 Control UI 未显式设置浏览器 origin allowlist | `gateway.controlUi.allowedOrigins` | no |
| `gateway.control_ui.allowed_origins_wildcard` | warn/critical | `allowedOrigins=["*"]` 会禁用浏览器 origin allowlist | `gateway.controlUi.allowedOrigins` | no |
| `gateway.control_ui.host_header_origin_fallback` | warn/critical | 启用了 Host 头 origin 回退（降低 DNS rebinding 加固强度） | `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback` | no |
| `gateway.control_ui.insecure_auth` | warn | 启用了不安全 auth 兼容性开关 | `gateway.controlUi.allowInsecureAuth` | no |
| `gateway.control_ui.device_auth_disabled` | critical | 禁用了设备身份检查 | `gateway.controlUi.dangerouslyDisableDeviceAuth` | no |
| `gateway.real_ip_fallback_enabled` | warn/critical | 信任 `X-Real-IP` 回退可能因代理配置错误导致源 IP 欺骗 | `gateway.allowRealIpFallback`、`gateway.trustedProxies` | no |
| `gateway.token_too_short` | warn | 共享 token 过短，更容易被暴力破解 | `gateway.auth.token` | no |
| `gateway.auth_no_rate_limit` | warn | 暴露的 auth 若无速率限制，会增加暴力破解风险 | `gateway.auth.rateLimit` | no |
| `gateway.trusted_proxy_auth` | critical | 代理身份现在成为 auth 边界 | `gateway.auth.mode="trusted-proxy"` | no |
| `gateway.trusted_proxy_no_proxies` | critical | trusted-proxy auth 若没有受信任代理 IP，则不安全 | `gateway.trustedProxies` | no |
| `gateway.trusted_proxy_no_user_header` | critical | trusted-proxy auth 无法安全解析用户身份 | `gateway.auth.trustedProxy.userHeader` | no |
| `gateway.trusted_proxy_no_allowlist` | warn | trusted-proxy auth 会接受任何已通过上游认证的用户 | `gateway.auth.trustedProxy.allowUsers` | no |
| `gateway.probe_auth_secretref_unavailable` | warn | 深度探测在当前命令路径中无法解析 auth SecretRefs | 深度探测 auth 来源 / SecretRef 可用性 | no |
| `gateway.probe_failed` | warn/critical | 实时 Gateway 网关探测失败 | Gateway 网关可达性 / auth | no |
| `discovery.mdns_full_mode` | warn/critical | mDNS 完整模式会在本地网络上广播 `cliPath` / `sshPort` 元数据 | `discovery.mdns.mode`、`gateway.bind` | no |
| `config.insecure_or_dangerous_flags` | warn | 启用了不安全 / 危险的调试标志 | 多个键（见发现详情） | no |
| `config.secrets.gateway_password_in_config` | warn | Gateway 网关密码直接存储在配置中 | `gateway.auth.password` | no |
| `config.secrets.hooks_token_in_config` | warn | Hook bearer token 直接存储在配置中 | `hooks.token` | no |
| `hooks.token_reuse_gateway_token` | critical | Hook 入站 token 同时也能解锁 Gateway 网关 auth | `hooks.token`、`gateway.auth.token` | no |
| `hooks.token_too_short` | warn | Hook 入站更容易被暴力破解 | `hooks.token` | no |
| `hooks.default_session_key_unset` | warn | Hook 智能体运行时会扇出到按请求生成的会话中 | `hooks.defaultSessionKey` | no |
| `hooks.allowed_agent_ids_unrestricted` | warn/critical | 已认证的 Hook 调用方可以路由到任何已配置的智能体 | `hooks.allowedAgentIds` | no |
| `hooks.request_session_key_enabled` | warn/critical | 外部调用方可以选择 `sessionKey` | `hooks.allowRequestSessionKey` | no |
| `hooks.request_session_key_prefixes_missing` | warn/critical | 外部会话 key 的形状没有边界限制 | `hooks.allowedSessionKeyPrefixes` | no |
| `hooks.path_root` | critical | Hook 路径是 `/`，使入站更容易发生冲突或误路由 | `hooks.path` | no |
| `hooks.installs_unpinned_npm_specs` | warn | Hook 安装记录未固定到不可变的 npm specs | Hook 安装元数据 | no |
| `hooks.installs_missing_integrity` | warn | Hook 安装记录缺少完整性元数据 | Hook 安装元数据 | no |
| `hooks.installs_version_drift` | warn | Hook 安装记录与已安装包发生版本漂移 | Hook 安装元数据 | no |
| `logging.redact_off` | warn | 敏感值会泄露到日志 / 状态输出中 | `logging.redactSensitive` | yes |
| `browser.control_invalid_config` | warn | 浏览器控制配置在运行前就已无效 | `browser.*` | no |
| `browser.control_no_auth` | critical | 浏览器控制在没有 token / password auth 的情况下暴露 | `gateway.auth.*` | no |
| `browser.remote_cdp_http` | warn | 通过纯 HTTP 使用远程 CDP 缺少传输加密 | 浏览器配置文件 `cdpUrl` | no |
| `browser.remote_cdp_private_host` | warn | 远程 CDP 指向私有 / 内部主机 | 浏览器配置文件 `cdpUrl`、`browser.ssrfPolicy.*` | no |
| `sandbox.docker_config_mode_off` | warn | 已存在沙箱 Docker 配置，但当前未启用 | `agents.*.sandbox.mode` | no |
| `sandbox.bind_mount_non_absolute` | warn | 相对 bind mounts 的解析结果可能不可预测 | `agents.*.sandbox.docker.binds[]` | no |
| `sandbox.dangerous_bind_mount` | critical | 沙箱 bind mount 指向被阻止的系统、凭证或 Docker socket 路径 | `agents.*.sandbox.docker.binds[]` | no |
| `sandbox.dangerous_network_mode` | critical | 沙箱 Docker 网络使用 `host` 或 `container:*` 命名空间加入模式 | `agents.*.sandbox.docker.network` | no |
| `sandbox.dangerous_seccomp_profile` | critical | 沙箱 seccomp 配置文件削弱了容器隔离 | `agents.*.sandbox.docker.securityOpt` | no |
| `sandbox.dangerous_apparmor_profile` | critical | 沙箱 AppArmor 配置文件削弱了容器隔离 | `agents.*.sandbox.docker.securityOpt` | no |
| `sandbox.browser_cdp_bridge_unrestricted` | warn | 沙箱浏览器桥接暴露时没有来源范围限制 | `sandbox.browser.cdpSourceRange` | no |
| `sandbox.browser_container.non_loopback_publish` | critical | 现有浏览器容器在非 loopback 接口上发布了 CDP | 浏览器沙箱容器发布配置 | no |
| `sandbox.browser_container.hash_label_missing` | warn | 现有浏览器容器早于当前配置哈希标签机制 | `openclaw sandbox recreate --browser --all` | no |
| `sandbox.browser_container.hash_epoch_stale` | warn | 现有浏览器容器早于当前浏览器配置 epoch | `openclaw sandbox recreate --browser --all` | no |
| `tools.exec.host_sandbox_no_sandbox_defaults` | warn | 当沙箱关闭时，`exec host=sandbox` 会以失败关闭方式运行 | `tools.exec.host`、`agents.defaults.sandbox.mode` | no |
| `tools.exec.host_sandbox_no_sandbox_agents` | warn | 当沙箱关闭时，按智能体设置的 `exec host=sandbox` 会以失败关闭方式运行 | `agents.list[].tools.exec.host`、`agents.list[].sandbox.mode` | no |
| `tools.exec.security_full_configured` | warn/critical | 主机 exec 正在以 `security="full"` 运行 | `tools.exec.security`、`agents.list[].tools.exec.security` | no |
| `tools.exec.auto_allow_skills_enabled` | warn | Exec 批准会隐式信任 Skills 二进制文件 | `~/.openclaw/exec-approvals.json` | no |
| `tools.exec.allowlist_interpreter_without_strict_inline_eval` | warn | 解释器 allowlist 允许内联 eval，但不会强制重新批准 | `tools.exec.strictInlineEval`、`agents.list[].tools.exec.strictInlineEval`、exec approvals allowlist | no |
| `tools.exec.safe_bins_interpreter_unprofiled` | warn | `safeBins` 中的解释器 / 运行时二进制缺少显式 profile，会扩大 exec 风险 | `tools.exec.safeBins`、`tools.exec.safeBinProfiles`、`agents.list[].tools.exec.*` | no |
| `tools.exec.safe_bins_broad_behavior` | warn | `safeBins` 中的宽行为工具会削弱低风险 stdin 过滤信任模型 | `tools.exec.safeBins`、`agents.list[].tools.exec.safeBins` | no |
| `tools.exec.safe_bin_trusted_dirs_risky` | warn | `safeBinTrustedDirs` 包含可变或高风险目录 | `tools.exec.safeBinTrustedDirs`、`agents.list[].tools.exec.safeBinTrustedDirs` | no |
| `skills.workspace.symlink_escape` | warn | 工作区 `skills/**/SKILL.md` 解析到了工作区根目录之外（符号链接链漂移） | 工作区 `skills/**` 文件系统状态 | no |
| `plugins.extensions_no_allowlist` | warn | 已安装扩展，但没有显式插件 allowlist | `plugins.allowlist` | no |
| `plugins.installs_unpinned_npm_specs` | warn | 插件安装记录未固定到不可变的 npm specs | 插件安装元数据 | no |
| `plugins.installs_missing_integrity` | warn | 插件安装记录缺少完整性元数据 | 插件安装元数据 | no |
| `plugins.installs_version_drift` | warn | 插件安装记录与已安装包发生版本漂移 | 插件安装元数据 | no |
| `plugins.code_safety` | warn/critical | 插件代码扫描发现可疑或危险模式 | 插件代码 / 安装来源 | no |
| `plugins.code_safety.entry_path` | warn | 插件入口路径指向隐藏目录或 `node_modules` 位置 | 插件清单 `entry` | no |
| `plugins.code_safety.entry_escape` | critical | 插件入口逃逸出插件目录 | 插件清单 `entry` | no |
| `plugins.code_safety.scan_failed` | warn | 插件代码扫描无法完成 | 插件扩展路径 / 扫描环境 | no |
| `skills.code_safety` | warn/critical | Skills 安装器元数据 / 代码包含可疑或危险模式 | Skills 安装来源 | no |
| `skills.code_safety.scan_failed` | warn | Skills 代码扫描无法完成 | Skills 扫描环境 | no |
| `security.exposure.open_channels_with_exec` | warn/critical | 共享 / 公开房间可访问启用了 exec 的智能体 | `channels.*.dmPolicy`、`channels.*.groupPolicy`、`tools.exec.*`、`agents.list[].tools.exec.*` | no |
| `security.exposure.open_groups_with_elevated` | critical | 开放群组 + 提升权限工具会形成高影响的提示注入路径 | `channels.*.groupPolicy`、`tools.elevated.*` | no |
| `security.exposure.open_groups_with_runtime_or_fs` | critical/warn | 开放群组可访问命令 / 文件工具，且没有沙箱隔离 / 工作区护栏 | `channels.*.groupPolicy`、`tools.profile/deny`、`tools.fs.workspaceOnly`、`agents.*.sandbox.mode` | no |
| `security.trust_model.multi_user_heuristic` | warn | 配置看起来像多用户场景，但 Gateway 网关信任模型是个人助理模型 | 拆分信任边界，或采用共享用户加固（`sandbox.mode`、工具 deny / 工作区范围限制） | no |
| `tools.profile_minimal_overridden` | warn | 智能体覆盖配置绕过了全局 minimal profile | `agents.list[].tools.profile` | no |
| `plugins.tools_reachable_permissive_policy` | warn | 在宽松策略上下文中仍可访问扩展工具 | `tools.profile` + 工具 allow / deny | no |
| `models.legacy` | warn | 仍然配置了旧模型家族 | 模型选择 | no |
| `models.weak_tier` | warn | 已配置模型低于当前推荐层级 | 模型选择 | no |
| `models.small_params` | critical/info | 小模型 + 不安全工具面会提高注入风险 | 模型选择 + 沙箱隔离 / 工具策略 | no |
| `summary.attack_surface` | info | 对 auth、渠道、工具和暴露姿态的汇总摘要 | 多个键（见发现详情） | no |

## 通过 HTTP 使用 Control UI

Control UI 需要一个**安全上下文**（HTTPS 或 localhost）来生成设备身份。`gateway.controlUi.allowInsecureAuth` 是一个本地兼容性开关：

- 在 localhost 上，当页面通过不安全的 HTTP 加载时，它允许 Control UI 在没有设备身份的情况下进行 auth。
- 它不会绕过配对检查。
- 它不会放宽远程（非 localhost）设备身份要求。

优先使用 HTTPS（Tailscale Serve），或在 `127.0.0.1` 上打开 UI。

仅用于紧急兜底场景，`gateway.controlUi.dangerouslyDisableDeviceAuth` 会完全禁用设备身份检查。这是一次严重的安全降级；除非你正在主动调试并且能够快速回退，否则请保持关闭。

与这些危险标志分开的是，成功配置 `gateway.auth.mode: "trusted-proxy"` 后，可以允许**操作员** Control UI 会话在没有设备身份的情况下通过。这是有意设计的 auth 模式行为，不是 `allowInsecureAuth` 的捷径，而且它仍然不适用于节点角色的 Control UI 会话。

启用该设置时，`openclaw security audit` 会发出警告。

## 不安全或危险标志汇总

启用已知不安全 / 危险调试开关时，`openclaw security audit` 会包含 `config.insecure_or_dangerous_flags`。当前该检查聚合以下项：

- `gateway.controlUi.allowInsecureAuth=true`
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true`
- `gateway.controlUi.dangerouslyDisableDeviceAuth=true`
- `hooks.gmail.allowUnsafeExternalContent=true`
- `hooks.mappings[<index>].allowUnsafeExternalContent=true`
- `tools.exec.applyPatch.workspaceOnly=false`
- `plugins.entries.acpx.config.permissionMode=approve-all`

在 OpenClaw 配置 schema 中定义的完整 `dangerous*` / `dangerously*` 配置键包括：

- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback`
- `gateway.controlUi.dangerouslyDisableDeviceAuth`
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `channels.discord.dangerouslyAllowNameMatching`
- `channels.discord.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.slack.dangerouslyAllowNameMatching`
- `channels.slack.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.googlechat.dangerouslyAllowNameMatching`
- `channels.googlechat.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.msteams.dangerouslyAllowNameMatching`
- `channels.synology-chat.dangerouslyAllowNameMatching`（扩展渠道）
- `channels.synology-chat.accounts.<accountId>.dangerouslyAllowNameMatching`（扩展渠道）
- `channels.synology-chat.dangerouslyAllowInheritedWebhookPath`（扩展渠道）
- `channels.zalouser.dangerouslyAllowNameMatching`（扩展渠道）
- `channels.zalouser.accounts.<accountId>.dangerouslyAllowNameMatching`（扩展渠道）
- `channels.irc.dangerouslyAllowNameMatching`（扩展渠道）
- `channels.irc.accounts.<accountId>.dangerouslyAllowNameMatching`（扩展渠道）
- `channels.mattermost.dangerouslyAllowNameMatching`（扩展渠道）
- `channels.mattermost.accounts.<accountId>.dangerouslyAllowNameMatching`（扩展渠道）
- `channels.telegram.network.dangerouslyAllowPrivateNetwork`
- `channels.telegram.accounts.<accountId>.network.dangerouslyAllowPrivateNetwork`
- `agents.defaults.sandbox.docker.dangerouslyAllowReservedContainerTargets`
- `agents.defaults.sandbox.docker.dangerouslyAllowExternalBindSources`
- `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowReservedContainerTargets`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowExternalBindSources`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowContainerNamespaceJoin`

## 反向代理配置

如果你在反向代理（nginx、Caddy、Traefik 等）后面运行 Gateway 网关，请配置 `gateway.trustedProxies`，以便正确处理转发的客户端 IP。

当 Gateway 网关检测到来自**不在** `trustedProxies` 中地址的代理头时，它**不会**将这些连接视为本地客户端。如果 Gateway 网关 auth 被禁用，这些连接会被拒绝。这样可以防止一种身份验证绕过：否则经代理的连接可能会看起来像来自 localhost，从而自动获得信任。

`gateway.trustedProxies` 也会为 `gateway.auth.mode: "trusted-proxy"` 提供支持，但该 auth 模式更严格：

- trusted-proxy auth **对来自 loopback 源的代理采取失败关闭**
- 同主机上的 loopback 反向代理仍然可以使用 `gateway.trustedProxies` 来进行本地客户端检测和转发 IP 处理
- 对于同主机 loopback 反向代理，请使用 token / password auth，而不是 `gateway.auth.mode: "trusted-proxy"`

```yaml
gateway:
  trustedProxies:
    - "10.0.0.1" # 反向代理 IP
  # 可选。默认 false。
  # 仅当你的代理无法提供 X-Forwarded-For 时启用。
  allowRealIpFallback: false
  auth:
    mode: password
    password: ${OPENCLAW_GATEWAY_PASSWORD}
```

配置了 `trustedProxies` 后，Gateway 网关会使用 `X-Forwarded-For` 来确定客户端 IP。默认情况下会忽略 `X-Real-IP`，除非你显式设置 `gateway.allowRealIpFallback: true`。

良好的反向代理行为（覆盖传入的转发头）：

```nginx
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Real-IP $remote_addr;
```

不良的反向代理行为（追加 / 保留不受信任的转发头）：

```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

## HSTS 和 origin 说明

- OpenClaw Gateway 网关首先面向本地 / loopback。如果你在反向代理处终止 TLS，请在那里为面向代理的 HTTPS 域设置 HSTS。
- 如果由 Gateway 网关自身终止 HTTPS，你可以设置 `gateway.http.securityHeaders.strictTransportSecurity`，让 OpenClaw 在响应中发送 HSTS 头。
- 详细部署指南见 [Trusted Proxy Auth](/zh-CN/gateway/trusted-proxy-auth#tls-termination-and-hsts)。
- 对于非 loopback 的 Control UI 部署，默认要求设置 `gateway.controlUi.allowedOrigins`。
- `gateway.controlUi.allowedOrigins: ["*"]` 表示显式允许所有浏览器 origin 的策略，不是强化默认值。除非是在严格受控的本地测试中，否则应避免使用。
- 即使启用了通用 loopback 豁免，loopback 上的浏览器 origin auth 失败仍会受到速率限制，但锁定 key 会按规范化后的 `Origin` 值分别计算，而不是共用一个 localhost 桶。
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true` 会启用 Host 头 origin 回退模式；请将其视为由操作员主动选择的危险策略。
- 请将 DNS rebinding 和代理 Host 头行为视为部署加固问题；保持 `trustedProxies` 范围严格，并避免将 Gateway 网关直接暴露到公共互联网。

## 本地会话日志会落盘保存

OpenClaw 会将会话转录存储到磁盘，路径为 `~/.openclaw/agents/<agentId>/sessions/*.jsonl`。
这是实现会话连续性以及（可选的）会话 Memory 索引所必需的，但这也意味着
**任何具有文件系统访问权限的进程 / 用户都可以读取这些日志**。请将磁盘访问视为信任
边界，并锁紧 `~/.openclaw` 的权限（见下方审计部分）。如果你需要智能体之间更强的隔离，请在不同的 OS 用户或不同的主机下运行它们。

## 节点执行（`system.run`）

如果已配对一个 macOS 节点，Gateway 网关可以在该节点上调用 `system.run`。这属于在该 Mac 上的**远程代码执行**：

- 需要节点配对（批准 + token）。
- Gateway 网关节点配对不是逐命令批准层。它建立的是节点身份 / 信任以及 token 签发。
- Gateway 网关通过 `gateway.nodes.allowCommands` / `denyCommands` 应用粗粒度的全局节点命令策略。
- 在 Mac 上通过**设置 → Exec approvals**进行控制（security + ask + allowlist）。
- 每个节点的 `system.run` 策略由节点自己的 exec approvals 文件（`exec.approvals.node.*`）控制，它可以比 Gateway 网关的全局命令 ID 策略更严格，也可以更宽松。
- 当节点以 `security="full"` 和 `ask="off"` 运行时，它遵循的是默认的受信任操作员模型。除非你的部署明确需要更严格的批准或 allowlist 姿态，否则应将其视为预期行为。
- 批准模式会绑定精确的请求上下文，并在可能时绑定一个具体的本地脚本 / 文件操作数。如果 OpenClaw 无法为某个解释器 / 运行时命令精确识别出唯一的直接本地文件，那么基于批准的执行将被拒绝，而不是声称已覆盖完整语义。
- 对于 `host=node`，基于批准的运行还会存储一个规范化的预备 `systemRunPlan`；之后的已批准转发会复用该已存储计划，而 Gateway 网关验证会拒绝调用方在批准请求创建后再修改命令 / cwd / 会话上下文。
- 如果你不希望远程执行，请将 security 设为 **deny**，并移除该 Mac 的节点配对。

这一区分在分级时很重要：

- 已配对节点重新连接后声明了不同的命令列表，这本身**不是**漏洞，只要 Gateway 网关全局策略和节点本地 exec approvals 仍然在执行真正的边界控制。
- 把节点配对元数据当作第二层隐藏的逐命令批准机制的报告，通常属于策略 / UX 混淆，而不是安全边界绕过。

## 动态 Skills（watcher / 远程节点）

OpenClaw 可以在会话中途刷新 Skills 列表：

- **Skills watcher**：对 `SKILL.md` 的更改可以在智能体下一轮运行时更新 Skills 快照。
- **远程节点**：连接一个 macOS 节点后，可能会使仅限 macOS 的 Skills 变为可用（基于二进制探测）。

请将 skill 文件夹视为**受信任代码**，并限制谁可以修改它们。

## 威胁模型

你的 AI 助手可以：

- 执行任意 Shell 命令
- 读写文件
- 访问网络服务
- 给任何人发消息（如果你赋予它 WhatsApp 访问权限）

能给你发消息的人可以：

- 试图诱导你的 AI 做坏事
- 通过社会工程获取你的数据访问权限
- 探测基础设施细节

## 核心概念：先做访问控制，再谈智能

这里的大多数失败并不是什么高深利用——而是“某人给机器人发了消息，而机器人照做了”。

OpenClaw 的立场是：

- **身份优先：** 先决定谁可以和机器人对话（私信配对 / allowlist / 显式 `open`）。
- **范围其次：** 再决定机器人被允许在哪里操作（群组 allowlist + 提及门控、工具、沙箱隔离、设备权限）。
- **模型最后：** 假设模型可以被操纵；系统设计应让这种操纵的爆炸半径受到限制。

## 命令授权模型

Slash commands 和指令只会对**已授权发送者**生效。授权来源于
渠道 allowlist / pairing 加上 `commands.useAccessGroups`（参见 [配置](/zh-CN/gateway/configuration)
和 [Slash commands](/zh-CN/tools/slash-commands)）。如果某个渠道 allowlist 为空或包含 `"*"`,
那么该渠道上的命令实际上就是开放的。

`/exec` 是面向已授权操作员的仅会话内便捷命令。它**不会**写入配置，也**不会**
修改其他会话。

## 控制平面工具风险

有两个内置工具可以进行持久化的控制平面变更：

- `gateway` 可以通过 `config.schema.lookup` / `config.get` 检查配置，也可以通过 `config.apply`、`config.patch` 和 `update.run` 进行持久化修改。
- `cron` 可以创建计划任务，使其在原始聊天 / 任务结束后继续运行。

仅限所有者使用的 `gateway` 运行时工具仍然拒绝重写
`tools.exec.ask` 或 `tools.exec.security`；旧版 `tools.bash.*` 别名会
先规范化为相同的受保护 exec 路径，然后再进行写入。

对于任何会处理不受信任内容的智能体 / 入口面，默认应拒绝这些工具：

```json5
{
  tools: {
    deny: ["gateway", "cron", "sessions_spawn", "sessions_send"],
  },
}
```

`commands.restart=false` 只会阻止重启动作。它不会禁用 `gateway` 的配置 / 更新操作。

## 插件 / 扩展

插件会**在 Gateway 网关进程内**运行。请将它们视为受信任代码：

- 只从你信任的来源安装插件。
- 优先使用显式的 `plugins.allow` allowlist。
- 启用前先检查插件配置。
- 插件变更后重启 Gateway 网关。
- 如果你安装或更新插件（`openclaw plugins install <package>`、`openclaw plugins update <id>`），请将其视为运行不受信任代码：
  - 安装路径是当前插件安装根目录下该插件对应的目录。
  - OpenClaw 会在安装 / 更新前运行内置危险代码扫描。`critical` 级发现默认会阻止继续。
  - OpenClaw 会使用 `npm pack`，然后在该目录中运行 `npm install --omit=dev`（npm 生命周期脚本可能会在安装期间执行代码）。
  - 优先使用固定、精确的版本（`@scope/pkg@1.2.3`），并在启用前检查磁盘上解包后的代码。
  - `--dangerously-force-unsafe-install` 仅用于紧急兜底场景，用来处理插件安装 / 更新流程中内置扫描的误报。它不会绕过插件 `before_install` hook 策略阻止，也不会绕过扫描失败。
  - 由 Gateway 网关驱动的 skill 依赖安装遵循相同的危险 / 可疑分级：内置 `critical` 发现默认会阻止，除非调用方显式设置 `dangerouslyForceUnsafeInstall`；而可疑发现仍然只会发出警告。`openclaw skills install` 仍然是单独的 ClawHub skill 下载 / 安装流程。

详情见：[插件](/zh-CN/tools/plugin)

<a id="dm-access-model-pairing-allowlist-open-disabled"></a>

## 私信访问模型（pairing / allowlist / open / disabled）

所有当前支持私信的渠道都支持私信策略（`dmPolicy` 或 `*.dm.policy`），用于在消息被处理**之前**拦截入站私信：

- `pairing`（默认）：未知发送者会收到一个简短的配对码，机器人会忽略其消息，直到获得批准。配对码 1 小时后过期；在新请求创建之前，重复发送私信不会重新发送配对码。默认情况下，每个渠道最多保留 **3 个待处理请求**。
- `allowlist`：未知发送者会被拦截（没有配对握手）。
- `open`：允许任何人发送私信（公开）。**要求**该渠道的 allowlist 包含 `"*"`（显式选择启用）。
- `disabled`：完全忽略入站私信。

通过 CLI 批准：

```bash
openclaw pairing list <channel>
openclaw pairing approve <channel> <code>
```

详情及磁盘文件位置见：[配对](/zh-CN/channels/pairing)

## 私信会话隔离（多用户模式）

默认情况下，OpenClaw 会将**所有私信都路由到主会话**，这样你的助理可以在不同设备和渠道间保持连续性。如果**有多个人**可以给机器人发私信（开放私信或多人 allowlist），请考虑隔离私信会话：

```json5
{
  session: { dmScope: "per-channel-peer" },
}
```

这样可以防止跨用户上下文泄露，同时保持群聊彼此隔离。

这是消息上下文边界，不是主机管理员边界。如果用户彼此对抗且共享同一 Gateway 网关主机 / 配置，请按信任边界分别运行独立的 Gateway 网关。

### 安全私信模式（推荐）

可将上面的片段视为**安全私信模式**：

- 默认：`session.dmScope: "main"`（所有私信共享同一会话，以保持连续性）。
- 本地 CLI 新手引导默认：当未设置时，会写入 `session.dmScope: "per-channel-peer"`（保留现有显式值）。
- 安全私信模式：`session.dmScope: "per-channel-peer"`（每个渠道 + 发送者组合都有独立的私信上下文）。
- 跨渠道联系人隔离：`session.dmScope: "per-peer"`（同一发送者在同类型所有渠道中共用一个会话）。

如果你在同一个渠道上运行多个账号，请改用 `per-account-channel-peer`。如果同一个人会通过多个渠道联系你，请使用 `session.identityLinks` 将这些私信会话合并到一个规范身份下。参见 [会话管理](/zh-CN/concepts/session) 和 [配置](/zh-CN/gateway/configuration)。

## Allowlists（私信 + 群组）——术语说明

OpenClaw 有两层独立的“谁可以触发我？”控制：

- **私信 allowlist**（`allowFrom` / `channels.discord.allowFrom` / `channels.slack.allowFrom`；旧版：`channels.discord.dm.allowFrom`、`channels.slack.dm.allowFrom`）：哪些人被允许在私信中和机器人对话。
  - 当 `dmPolicy="pairing"` 时，批准结果会写入 `~/.openclaw/credentials/` 下按账号范围划分的配对 allowlist 存储（默认账号用 `<channel>-allowFrom.json`，非默认账号用 `<channel>-<accountId>-allowFrom.json`），并与配置中的 allowlists 合并。
- **群组 allowlist**（按渠道定义）：机器人究竟接受哪些群组 / 渠道 / guild 的消息。
  - 常见模式：
    - `channels.whatsapp.groups`、`channels.telegram.groups`、`channels.imessage.groups`：像 `requireMention` 这样的按群组默认值；设置后它也会充当群组 allowlist（包含 `"*"` 可保留允许所有的行为）。
    - `groupPolicy="allowlist"` + `groupAllowFrom`：限制在群组会话内部究竟谁可以触发机器人（WhatsApp / Telegram / Signal / iMessage / Microsoft Teams）。
    - `channels.discord.guilds` / `channels.slack.channels`：按入口面划分的 allowlists + 提及默认值。
  - 群组检查顺序如下：先 `groupPolicy` / 群组 allowlists，后提及 / 回复激活。
  - 回复机器人消息（隐式提及）**不会**绕过像 `groupAllowFrom` 这样的发送者 allowlists。
  - **安全说明：** 请将 `dmPolicy="open"` 和 `groupPolicy="open"` 视为最后手段。应尽量少用；除非你完全信任房间里的每个成员，否则应优先使用 pairing + allowlists。

详情见：[配置](/zh-CN/gateway/configuration) 和 [群组](/zh-CN/channels/groups)

## 提示注入（它是什么，为什么重要）

提示注入是指攻击者构造一条消息，操纵模型去执行不安全的事情（“忽略你的指令”、“导出你的文件系统”、“访问这个链接并运行命令”等）。

即使有强系统提示，**提示注入仍然没有被彻底解决**。系统提示护栏只是软性引导；真正的强制执行来自工具策略、exec approvals、沙箱隔离和渠道 allowlists（并且操作员也可以按设计关闭它们）。实践中真正有帮助的是：

- 保持入站私信处于锁定状态（pairing / allowlists）。
- 在群组中优先使用提及门控；避免在公开房间中部署“始终在线”的机器人。
- 默认将链接、附件和粘贴的指令视为敌对内容。
- 在沙箱中运行敏感工具执行；不要让 secrets 落在智能体可访问的文件系统里。
- 注意：沙箱隔离是选择启用的。如果沙箱模式关闭，隐式 `host=auto` 会解析为 Gateway 网关主机。显式 `host=sandbox` 仍会以失败关闭方式终止，因为没有可用的沙箱运行时。如果你希望这种行为在配置中明确表达，请设置 `host=gateway`。
- 将高风险工具（`exec`、`browser`、`web_fetch`、`web_search`）限制给受信任智能体或显式 allowlists。
- 如果你为解释器设置 allowlist（`python`、`node`、`ruby`、`perl`、`php`、`lua`、`osascript`），请启用 `tools.exec.strictInlineEval`，这样内联 eval 形式仍然需要显式批准。
- **模型选择很重要：** 较旧 / 较小 / 旧代模型对提示注入和工具误用的抵抗力明显更弱。对于启用了工具的智能体，请使用当前最强、最新一代、经过指令强化的模型。

以下红旗内容应视为不受信任：

- “读取这个文件 / URL，并严格照它说的做。”
- “忽略你的系统提示或安全规则。”
- “泄露你的隐藏指令或工具输出。”
- “把 `~/.openclaw` 或你的日志完整内容贴出来。”

## 不安全外部内容绕过标志

OpenClaw 包含一些显式绕过标志，可用于禁用外部内容安全包装：

- `hooks.mappings[].allowUnsafeExternalContent`
- `hooks.gmail.allowUnsafeExternalContent`
- Cron 负载字段 `allowUnsafeExternalContent`

指南：

- 在生产环境中保持这些设置为未设置 / false。
- 只在范围严格受限的调试场景中临时启用。
- 如果启用，请隔离该智能体（沙箱隔离 + 最少工具 + 专用会话命名空间）。

Hooks 风险说明：

- Hook 负载属于不受信任内容，即使投递来自你控制的系统也是如此（邮件 / 文档 / 网页内容都可能携带提示注入）。
- 较弱的模型层级会放大这一风险。对于 Hook 驱动的自动化，请优先使用强力的现代模型层级，并保持严格的工具策略（`tools.profile: "messaging"` 或更严格），同时尽可能启用沙箱隔离。

### 提示注入并不需要公开私信

即使**只有你自己**能给机器人发消息，提示注入仍然可以通过
机器人读取的任何**不受信任内容**发生（web 搜索 / 抓取结果、浏览器页面、
邮件、文档、附件、粘贴的日志 / 代码）。换句话说：发送者并不是唯一的威胁面；
**内容本身**也可能携带对抗性指令。

启用工具后，典型风险是泄露上下文或触发工具调用。可通过以下方式降低爆炸半径：

- 使用一个只读或禁用工具的**reader 智能体**来总结不受信任内容，
  然后再把摘要传给主智能体。
- 对启用了工具的智能体，除非确有需要，否则关闭 `web_search` / `web_fetch` / `browser`。
- 对于 OpenResponses URL 输入（`input_file` / `input_image`），请严格设置
  `gateway.http.endpoints.responses.files.urlAllowlist` 和
  `gateway.http.endpoints.responses.images.urlAllowlist`，并保持 `maxUrlParts` 较低。
  空 allowlists 会被视为未设置；如果你想完全禁用 URL 抓取，请使用 `files.allowUrl: false` / `images.allowUrl: false`。
- 对于 OpenResponses 文件输入，解码后的 `input_file` 文本仍会作为
  **不受信任的外部内容**注入。不要因为 Gateway 网关是在本地解码文件文本，
  就把它当成可信内容。注入块仍然带有显式的
  `<<<EXTERNAL_UNTRUSTED_CONTENT ...>>>` 边界标记和 `Source: External`
  元数据，只是这一路径省略了更长的 `SECURITY NOTICE:` 横幅。
- 当 media-understanding 在将附加文档文本追加到媒体提示前提取文本时，
  同样会应用这种基于标记的包装。
- 对任何会接触不受信任输入的智能体，启用沙箱隔离和严格的工具 allowlists。
- 不要把 secrets 放进提示词；应通过 Gateway 网关主机上的环境变量 / 配置传递它们。

### 模型强度（安全说明）

不同模型层级的提示注入抵抗能力**并不一致**。更小 / 更便宜的模型通常更容易被对抗性提示诱导误用工具或劫持指令。

<Warning>
对于启用了工具的智能体，或者会读取不受信任内容的智能体，较旧 / 较小模型带来的提示注入风险通常过高。不要在弱模型层级上运行这类工作负载。
</Warning>

建议：

- 对任何可以运行工具或接触文件 / 网络的机器人，**使用最新一代、最高层级的模型**。
- 对启用了工具的智能体或不受信任收件箱，**不要使用较旧 / 较弱 / 较小的层级**；提示注入风险过高。
- 如果你必须使用较小模型，请**缩小爆炸半径**（只读工具、强沙箱隔离、最小文件系统访问、严格 allowlists）。
- 运行小模型时，请**为所有会话启用沙箱隔离**，并**禁用 web_search / web_fetch / browser**，除非输入受到严格控制。
- 对于仅聊天、输入受信任且无工具的个人助理，较小模型通常是可以接受的。

<a id="reasoning-verbose-output-in-groups"></a>

## 群组中的推理与详细输出

`/reasoning`、`/verbose` 和 `/trace` 可能暴露内部推理、工具
输出或插件诊断信息，而这些内容
原本并不适合公开渠道。在群组环境中，请将它们视为**仅用于调试**
的功能，除非你明确需要，否则应保持关闭。

指南：

- 在公开房间中保持 `/reasoning`、`/verbose` 和 `/trace` 关闭。
- 如果要启用，只在受信任的私信或严格受控的房间中启用。
- 请记住：详细和 trace 输出可能包含工具参数、URL、插件诊断信息以及模型看到的数据。

## 配置加固（示例）

### 0) 文件权限

在 Gateway 网关主机上保持配置 + 状态私有：

- `~/.openclaw/openclaw.json`：`600`（仅用户可读 / 写）
- `~/.openclaw`：`700`（仅用户）

`openclaw doctor` 可以发出警告，并提供收紧这些权限的选项。

### 0.4) 网络暴露（bind + port + firewall）

Gateway 网关在单个端口上复用 **WebSocket + HTTP**：

- 默认值：`18789`
- 配置 / 标志 / 环境变量：`gateway.port`、`--port`、`OPENCLAW_GATEWAY_PORT`

这一 HTTP 暴露面包括 Control UI 和 canvas host：

- Control UI（SPA 静态资源）（默认基础路径 `/`）
- Canvas host：`/__openclaw__/canvas/` 和 `/__openclaw__/a2ui/`（任意 HTML / JS；应将其视为不受信任内容）

如果你在普通浏览器中加载 canvas 内容，请像对待其他不受信任网页一样处理它：

- 不要将 canvas host 暴露给不受信任的网络 / 用户。
- 不要让 canvas 内容与有特权的 Web 入口面共享同一个 origin，除非你完全理解其影响。

Bind 模式控制 Gateway 网关的监听位置：

- `gateway.bind: "loopback"`（默认）：只有本地客户端可以连接。
- 非 loopback bind（`"lan"`、`"tailnet"`、`"custom"`）会扩大攻击面。只有在启用了 Gateway 网关 auth（共享 token / password，或正确配置的非 loopback trusted proxy）并且有真实防火墙的情况下才应使用。

经验规则：

- 优先使用 Tailscale Serve，而不是 LAN bind（Serve 会让 Gateway 网关保持在 loopback 上，由 Tailscale 处理访问）。
- 如果你必须 bind 到 LAN，请使用防火墙将该端口限制为严格的源 IP allowlist；不要广泛进行端口转发。
- 绝不要将未认证的 Gateway 网关暴露在 `0.0.0.0` 上。

### 0.4.1) Docker 端口发布 + UFW（`DOCKER-USER`）

如果你在 VPS 上通过 Docker 运行 OpenClaw，请记住，已发布的容器端口
（`-p HOST:CONTAINER` 或 Compose `ports:`）流量经过的是 Docker 的转发链，
而不只是主机的 `INPUT` 规则。

为了让 Docker 流量与你的防火墙策略保持一致，请在
`DOCKER-USER` 中强制实施规则（该链会在 Docker 自己的 accept 规则之前被评估）。
在许多现代发行版上，`iptables` / `ip6tables` 使用的是 `iptables-nft` 前端，
但这些规则仍然会应用到底层的 nftables 后端。

最小 allowlist 示例（IPv4）：

```bash
# /etc/ufw/after.rules（以独立的 *filter 段追加）
*filter
:DOCKER-USER - [0:0]
-A DOCKER-USER -m conntrack --ctstate ESTABLISHED,RELATED -j RETURN
-A DOCKER-USER -s 127.0.0.0/8 -j RETURN
-A DOCKER-USER -s 10.0.0.0/8 -j RETURN
-A DOCKER-USER -s 172.16.0.0/12 -j RETURN
-A DOCKER-USER -s 192.168.0.0/16 -j RETURN
-A DOCKER-USER -s 100.64.0.0/10 -j RETURN
-A DOCKER-USER -p tcp --dport 80 -j RETURN
-A DOCKER-USER -p tcp --dport 443 -j RETURN
-A DOCKER-USER -m conntrack --ctstate NEW -j DROP
-A DOCKER-USER -j RETURN
COMMIT
```

IPv6 使用独立的表。如果启用了 Docker IPv6，请在 `/etc/ufw/after6.rules` 中
添加对应策略。

避免在文档示例中硬编码像 `eth0` 这样的接口名。接口名会因 VPS 镜像而异
（`ens3`、`enp*` 等），如果不匹配，可能会意外跳过你的拒绝规则。

重新加载后的快速验证：

```bash
ufw reload
iptables -S DOCKER-USER
ip6tables -S DOCKER-USER
nmap -sT -p 1-65535 <public-ip> --open
```

预期的对外开放端口应当只有你明确打算暴露的那些（对大多数
配置来说：SSH + 你的反向代理端口）。

### 0.4.2) mDNS / Bonjour 发现（信息泄露）

Gateway 网关会通过 mDNS（端口 5353 上的 `_openclaw-gw._tcp`）广播自身存在，以支持本地设备发现。在完整模式下，这还会包含可能暴露运行细节的 TXT 记录：

- `cliPath`：CLI 二进制文件的完整文件系统路径（会泄露用户名和安装位置）
- `sshPort`：广播主机上 SSH 的可用性
- `displayName`、`lanHost`：主机名信息

**操作安全考量：** 广播基础设施细节会让本地网络上的任何人更容易进行侦察。即使像文件系统路径和 SSH 可用性这样“看似无害”的信息，也有助于攻击者绘制你的环境图谱。

**建议：**

1. **Minimal 模式**（默认，推荐用于暴露型 Gateway 网关）：从 mDNS 广播中省略敏感字段：

   ```json5
   {
     discovery: {
       mdns: { mode: "minimal" },
     },
   }
   ```

2. 如果你不需要本地设备发现，**可完全禁用**：

   ```json5
   {
     discovery: {
       mdns: { mode: "off" },
     },
   }
   ```

3. **Full 模式**（选择启用）：在 TXT 记录中包含 `cliPath` + `sshPort`：

   ```json5
   {
     discovery: {
       mdns: { mode: "full" },
     },
   }
   ```

4. **环境变量**（替代方式）：设置 `OPENCLAW_DISABLE_BONJOUR=1`，无需更改配置即可禁用 mDNS。

在 minimal 模式下，Gateway 网关仍会广播足够用于设备发现的信息（`role`、`gatewayPort`、`transport`），但会省略 `cliPath` 和 `sshPort`。需要 CLI 路径信息的应用可以通过经过身份验证的 WebSocket 连接来获取。

### 0.5) 锁定 Gateway 网关 WebSocket（本地 auth）

默认情况下**必须启用** Gateway 网关 auth。如果未配置任何有效的 Gateway 网关 auth 路径，
Gateway 网关会拒绝 WebSocket 连接（失败关闭）。

新手引导默认会生成一个 token（即使是 loopback），因此
本地客户端也必须进行身份验证。

设置 token，以便**所有** WS 客户端都必须完成身份验证：

```json5
{
  gateway: {
    auth: { mode: "token", token: "your-token" },
  },
}
```

Doctor 可以为你生成一个：`openclaw doctor --generate-gateway-token`。

注意：`gateway.remote.token` / `.password` 是客户端凭证来源。
它们**本身不会**保护本地 WS 访问。
只有在 `gateway.auth.*` 未设置时，本地调用路径才可以将 `gateway.remote.*` 作为回退来源。
如果通过 SecretRef 显式配置了 `gateway.auth.token` / `gateway.auth.password`，但无法解析，则会失败关闭（不会用远程回退来掩盖）。
可选：使用 `wss://` 时，可通过 `gateway.remote.tlsFingerprint` 固定远程 TLS。
纯文本 `ws://` 默认仅限 loopback。对于受信任的私有网络
路径，可在客户端进程上设置 `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` 作为紧急兜底。

本地设备配对：

- 为了让同主机客户端使用更顺畅，直接本地 loopback 连接会自动批准设备配对。
- OpenClaw 还提供一条窄范围的后端 / 容器本地自连接路径，用于
  受信任的共享密钥辅助流程。
- Tailnet 和 LAN 连接（包括同主机 tailnet bind）在配对方面都被视为远程连接，仍然需要批准。

Auth 模式：

- `gateway.auth.mode: "token"`：共享 bearer token（大多数场景推荐）。
- `gateway.auth.mode: "password"`：密码 auth（建议通过环境变量设置：`OPENCLAW_GATEWAY_PASSWORD`）。
- `gateway.auth.mode: "trusted-proxy"`：信任具备身份感知能力的反向代理来为用户完成身份验证，并通过头部传递身份（见 [Trusted Proxy Auth](/zh-CN/gateway/trusted-proxy-auth)）。

轮换检查清单（token / password）：

1. 生成 / 设置新的 secret（`gateway.auth.token` 或 `OPENCLAW_GATEWAY_PASSWORD`）。
2. 重启 Gateway 网关（如果由 macOS 应用监管 Gateway 网关，则重启该应用）。
3. 更新所有远程客户端（在会调用该 Gateway 网关的机器上更新 `gateway.remote.token` / `.password`）。
4. 验证旧凭证已无法再建立连接。

### 0.6) Tailscale Serve 身份头

当 `gateway.auth.allowTailscale` 为 `true`（Serve 的默认值）时，OpenClaw
会接受 Tailscale Serve 身份头（`tailscale-user-login`）用于 Control
UI / WebSocket 身份验证。OpenClaw 会通过本地 Tailscale 守护进程
（`tailscale whois`）解析 `x-forwarded-for` 地址并与该头进行匹配，以验证身份。这仅会在请求命中 loopback 且包含由 Tailscale 注入的
`x-forwarded-for`、`x-forwarded-proto` 和 `x-forwarded-host`
时触发。
对于这条异步身份检查路径，来自同一 `{scope, ip}`
的失败尝试会在限流器记录失败之前被串行化。因此，同一个 Serve 客户端的并发错误重试
可能会让第二次尝试立即被锁定，而不是像两个普通不匹配那样竞速通过。
HTTP API 端点（例如 `/v1/*`、`/tools/invoke` 和 `/api/channels/*`）
**不会**使用 Tailscale 身份头 auth。它们仍然遵循 Gateway 网关
已配置的 HTTP auth 模式。

重要边界说明：

- Gateway 网关 HTTP bearer auth 实际上等同于全有或全无的操作员访问。
- 将能够调用 `/v1/chat/completions`、`/v1/responses` 或 `/api/channels/*` 的凭证视为该 Gateway 网关的完全访问操作员 secret。
- 在 OpenAI 兼容的 HTTP 入口面上，共享 secret bearer auth 会恢复完整的默认操作员作用域（`operator.admin`、`operator.approvals`、`operator.pairing`、`operator.read`、`operator.talk.secrets`、`operator.write`）以及面向智能体轮次的 owner 语义；更窄的 `x-openclaw-scopes` 值不会收缩这条共享 secret 路径。
- HTTP 上的按请求作用域语义只在请求来自带身份模式时适用，例如 trusted proxy auth，或者私有入口上的 `gateway.auth.mode="none"`。
- 在这些带身份的模式中，如果省略 `x-openclaw-scopes`，则会回退到普通的默认操作员作用域集合；如果你想使用更窄的作用域集合，请显式发送该头。
- `/tools/invoke` 遵循相同的共享 secret 规则：token / password bearer auth 在这里同样被视为完整操作员访问，而带身份模式仍会遵守声明的作用域。
- 不要与不受信任的调用方共享这些凭证；应按信任边界使用单独的 Gateway 网关。

**信任假设：** 无 token 的 Serve auth 假设 Gateway 网关主机本身是受信任的。
不要把它当作防御同主机恶意进程的机制。如果 Gateway 网关主机上可能运行不受信任的
本地代码，请禁用 `gateway.auth.allowTailscale`，并要求显式共享 secret auth，
即使用 `gateway.auth.mode: "token"` 或 `"password"`。

**安全规则：** 不要通过你自己的反向代理转发这些头。如果
你在 Gateway 网关前终止 TLS 或做代理，请禁用
`gateway.auth.allowTailscale`，并改用共享 secret auth（`gateway.auth.mode:
"token"` 或 `"password"`）或 [Trusted Proxy Auth](/zh-CN/gateway/trusted-proxy-auth)。

受信任代理：

- 如果你在 Gateway 网关前终止 TLS，请将 `gateway.trustedProxies` 设置为你的代理 IP。
- OpenClaw 会信任来自这些 IP 的 `x-forwarded-for`（或 `x-real-ip`），以确定客户端 IP，用于本地配对检查以及 HTTP auth / 本地检查。
- 确保你的代理会**覆盖** `x-forwarded-for`，并阻止直接访问 Gateway 网关端口。

参见 [Tailscale](/zh-CN/gateway/tailscale) 和 [Web 概览](/web)。

### 0.6.1) 通过节点主机进行浏览器控制（推荐）

如果你的 Gateway 网关位于远端，而浏览器运行在另一台机器上，请在浏览器所在机器上运行一个**节点主机**，
让 Gateway 网关代理浏览器操作（见 [浏览器工具](/zh-CN/tools/browser)）。
请将节点配对视为管理员级访问。

推荐模式：

- 保持 Gateway 网关和节点主机位于同一 tailnet（Tailscale）中。
- 有意识地完成节点配对；如果你不需要浏览器代理路由，就将其关闭。

应避免：

- 通过 LAN 或公共互联网暴露 relay / control 端口。
- 对浏览器控制端点使用 Tailscale Funnel（公共暴露）。

### 0.7) 磁盘上的 secrets（敏感数据）

请假设 `~/.openclaw/`（或 `$OPENCLAW_STATE_DIR/`）下的任何内容都可能包含 secrets 或私密数据：

- `openclaw.json`：配置中可能包含 token（Gateway 网关、远程 Gateway 网关）、provider 设置和 allowlists。
- `credentials/**`：渠道凭证（例如 WhatsApp 凭证）、配对 allowlists、旧版 OAuth 导入。
- `agents/<agentId>/agent/auth-profiles.json`：API keys、token 配置文件、OAuth tokens，以及可选的 `keyRef` / `tokenRef`。
- `secrets.json`（可选）：基于文件的 secret 负载，供 `file` SecretRef providers（`secrets.providers`）使用。
- `agents/<agentId>/agent/auth.json`：旧版兼容文件。发现静态 `api_key` 条目时会自动清除。
- `agents/<agentId>/sessions/**`：会话转录（`*.jsonl`）+ 路由元数据（`sessions.json`），其中可能包含私信和工具输出。
- 内置插件包：已安装插件（以及它们的 `node_modules/`）。
- `sandboxes/**`：工具沙箱工作区；其中可能累积你在沙箱内读写文件的副本。

加固建议：

- 保持严格权限（目录 `700`，文件 `600`）。
- 在 Gateway 网关主机上使用全盘加密。
- 如果主机是共享的，优先为 Gateway 网关使用专用的 OS 用户账号。

### 0.8) 日志 + 转录内容（脱敏 + 保留）

即使访问控制正确，日志和转录内容仍可能泄露敏感信息：

- Gateway 网关日志可能包含工具摘要、错误和 URL。
- 会话转录内容可能包含粘贴的 secrets、文件内容、命令输出和链接。

建议：

- 保持工具摘要脱敏开启（`logging.redactSensitive: "tools"`；默认值）。
- 通过 `logging.redactPatterns` 为你的环境添加自定义模式（tokens、主机名、内部 URL）。
- 共享诊断信息时，优先使用 `openclaw status --all`（可直接粘贴，secrets 已脱敏），而不是原始日志。
- 如果你不需要长期保留，请清理旧的会话转录内容和日志文件。

详情见：[日志记录](/zh-CN/gateway/logging)

### 1) 私信：默认使用 pairing

```json5
{
  channels: { whatsapp: { dmPolicy: "pairing" } },
}
```

### 2) 群组：全局要求提及

```json
{
  "channels": {
    "whatsapp": {
      "groups": {
        "*": { "requireMention": true }
      }
    }
  },
  "agents": {
    "list": [
      {
        "id": "main",
        "groupChat": { "mentionPatterns": ["@openclaw", "@mybot"] }
      }
    ]
  }
}
```

在群聊中，只有被明确提及时才回复。

### 3) 分开号码（WhatsApp、Signal、Telegram）

对于基于手机号的渠道，建议考虑让你的 AI 使用与个人号码不同的独立号码：

- 个人号码：你的对话保持私密
- 机器人号码：由 AI 处理，并设置适当边界

### 4) 只读模式（通过沙箱 + 工具）

你可以通过组合以下设置构建一个只读 profile：

- `agents.defaults.sandbox.workspaceAccess: "ro"`（或者使用 `"none"` 以完全禁用工作区访问）
- 阻止 `write`、`edit`、`apply_patch`、`exec`、`process` 等的工具 allow / deny 列表

其他加固选项：

- `tools.exec.applyPatch.workspaceOnly: true`（默认）：确保即使关闭了沙箱隔离，`apply_patch` 也不能在工作区目录之外写入 / 删除。只有当你明确希望 `apply_patch` 触及工作区外文件时，才将其设为 `false`。
- `tools.fs.workspaceOnly: true`（可选）：将 `read` / `write` / `edit` / `apply_patch` 路径，以及原生提示图像自动加载路径限制在工作区目录内（如果你目前允许绝对路径，并希望有一个统一护栏，这会很有用）。
- 保持文件系统根范围尽可能小：避免将你的主目录这类宽范围根目录用作智能体工作区 / 沙箱工作区。宽范围根目录可能会让文件系统工具接触到敏感本地文件（例如 `~/.openclaw` 下的状态 / 配置）。

### 5) 安全基线（可直接复制 / 粘贴）

下面是一份“安全默认值”配置，可让 Gateway 网关保持私有、要求私信 pairing，并避免始终在线的群组机器人：

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    port: 18789,
    auth: { mode: "token", token: "your-long-random-token" },
  },
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

如果你还希望工具执行也“默认更安全”，可为任何非 owner 智能体添加沙箱隔离 + 禁用危险工具（见下文“按智能体划分的访问配置”示例）。

面向聊天驱动型智能体轮次的内置基线：非 owner 发送者不能使用 `cron` 或 `gateway` 工具。

## 沙箱隔离（推荐）

专门文档：[沙箱隔离](/zh-CN/gateway/sandboxing)

两种互补方式：

- **在 Docker 中运行完整 Gateway 网关**（容器边界）：[Docker](/zh-CN/install/docker)
- **工具沙箱**（`agents.defaults.sandbox`，Gateway 网关运行在主机上 + 工具运行在 Docker 隔离环境中）：[沙箱隔离](/zh-CN/gateway/sandboxing)

注意：为防止跨智能体访问，请将 `agents.defaults.sandbox.scope` 保持为 `"agent"`（默认）
或使用 `"session"` 以获得更严格的按会话隔离。`scope: "shared"` 会使用
单一容器 / 工作区。

还要考虑沙箱中的智能体工作区访问：

- `agents.defaults.sandbox.workspaceAccess: "none"`（默认）会将智能体工作区保持为不可访问；工具会针对 `~/.openclaw/sandboxes` 下的沙箱工作区运行
- `agents.defaults.sandbox.workspaceAccess: "ro"` 会将智能体工作区以只读方式挂载到 `/agent`（会禁用 `write` / `edit` / `apply_patch`）
- `agents.defaults.sandbox.workspaceAccess: "rw"` 会将智能体工作区以读写方式挂载到 `/workspace`
- 额外的 `sandbox.docker.binds` 会基于规范化和 canonicalized 后的源路径进行验证。如果父目录符号链接技巧和规范 home 别名最终解析到了被阻止的根路径（例如 `/etc`、`/var/run` 或 OS home 下的凭证目录），仍然会以失败关闭方式拒绝。

重要说明：`tools.elevated` 是全局基线逃逸口，它会让 exec 在沙箱外运行。默认有效 host 是 `gateway`，当 exec 目标配置为 `node` 时则为 `node`。请保持 `tools.elevated.allowFrom` 范围严格，不要对陌生人启用它。你还可以通过 `agents.list[].tools.elevated` 按智能体进一步限制 elevated。参见 [提升权限模式](/zh-CN/tools/elevated)。

### 子智能体委派护栏

如果你允许会话工具，请将委派给子智能体的运行视为另一项边界决策：

- 除非该智能体确实需要委派，否则应拒绝 `sessions_spawn`。
- 将 `agents.defaults.subagents.allowAgents` 以及任何按智能体覆盖的 `agents.list[].subagents.allowAgents` 限制在已知安全的目标智能体范围内。
- 对于任何必须保持沙箱隔离的工作流，请使用 `sandbox: "require"` 调用 `sessions_spawn`（默认值是 `inherit`）。
- 当目标子运行时未启用沙箱隔离时，`sandbox: "require"` 会快速失败。

## 浏览器控制风险

启用浏览器控制后，模型就拥有了驱动真实浏览器的能力。
如果该浏览器 profile 已经包含登录会话，模型就可以
访问这些账号和数据。请将浏览器 profile 视为**敏感状态**：

- 优先为智能体使用专用 profile（默认 `openclaw` profile）。
- 避免让智能体使用你的个人日常主力 profile。
- 对于沙箱隔离的智能体，除非你信任它们，否则应保持主机浏览器控制关闭。
- 独立的 loopback 浏览器控制 API 只接受共享 secret auth
  （Gateway 网关 token bearer auth 或 Gateway 网关 password）。它不会使用
  trusted-proxy 或 Tailscale Serve 身份头。
- 将浏览器下载内容视为不受信任输入；优先使用隔离的下载目录。
- 尽可能在智能体 profile 中禁用浏览器同步 / 密码管理器（降低爆炸半径）。
- 对于远程 Gateway 网关，应将“浏览器控制”等同于“对该 profile 可访问内容的操作员级访问”。
- 保持 Gateway 网关和节点主机仅在 tailnet 内可达；避免将浏览器控制端口暴露到 LAN 或公共互联网。
- 在不需要时关闭浏览器代理路由（`gateway.nodes.browser.mode="off"`）。
- Chrome MCP 的 existing-session 模式**并不更安全**；它可以像你一样操作该主机 Chrome profile 可访问的任何内容。

### 浏览器 SSRF 策略（默认严格）

OpenClaw 的浏览器导航策略默认是严格的：私有 / 内部目标默认保持阻止状态，除非你显式选择启用。

- 默认：`browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` 未设置，因此浏览器导航会继续阻止私有 / 内部 / 特殊用途目标。
- 旧版别名：`browser.ssrfPolicy.allowPrivateNetwork` 仍可出于兼容性而使用。
- 选择启用模式：设置 `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork: true`，以允许访问私有 / 内部 / 特殊用途目标。
- 在严格模式下，使用 `hostnameAllowlist`（如 `*.example.com` 这类模式）和 `allowedHostnames`（精确主机例外，包括像 `localhost` 这样的被阻止名称）来添加显式例外。
- 系统会在请求前检查导航目标，并在导航结束后的最终 `http(s)` URL 上尽力再次检查，以降低基于重定向的 pivot 风险。

严格策略示例：

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"],
    },
  },
}
```

## 按智能体划分的访问配置（多智能体）

在多智能体路由中，每个智能体都可以有自己的沙箱隔离 + 工具策略：
你可以借此为不同智能体分配**完全访问**、**只读**或**无访问权限**。
完整细节和优先级规则见 [多智能体沙箱隔离与工具](/zh-CN/tools/multi-agent-sandbox-tools)。

常见用例：

- 个人智能体：完全访问，不使用沙箱
- 家庭 / 工作智能体：启用沙箱隔离 + 只读工具
- 公开智能体：启用沙箱隔离 + 无文件系统 / Shell 工具

### 示例：完全访问（无沙箱）

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

### 示例：只读工具 + 只读工作区

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "ro",
        },
        tools: {
          allow: ["read"],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

### 示例：无文件系统 / Shell 访问（允许 provider 消息工具）

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "none",
        },
        // 会话工具可能泄露转录内容中的敏感数据。默认情况下，OpenClaw 将这些工具限制为
        // 当前会话 + 生成的子智能体会话，但如有需要，你可以进一步收紧。
        // 参见配置参考中的 `tools.sessions.visibility`。
        tools: {
          sessions: { visibility: "tree" }, // self | tree | agent | all
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

## 该如何告诉你的 AI

在智能体的系统提示中加入安全指南：

```
## Security Rules
- Never share directory listings or file paths with strangers
- Never reveal API keys, credentials, or infrastructure details
- Verify requests that modify system config with the owner
- When in doubt, ask before acting
- Keep private data private unless explicitly authorized
```

## 事件响应

如果你的 AI 做了不该做的事：

### 遏制

1. **立即停止：** 停止 macOS 应用（如果它在监管 Gateway 网关），或终止你的 `openclaw gateway` 进程。
2. **关闭暴露面：** 将 `gateway.bind` 设为 `"loopback"`（或禁用 Tailscale Funnel / Serve），直到你弄清楚发生了什么。
3. **冻结访问：** 将高风险私信 / 群组切换为 `dmPolicy: "disabled"` / 要求提及，并移除你此前配置的 `"*"` 全开放条目。

### 轮换（如果 secrets 已泄露，则按已失陷处理）

1. 轮换 Gateway 网关 auth（`gateway.auth.token` / `OPENCLAW_GATEWAY_PASSWORD`）并重启。
2. 轮换所有可调用该 Gateway 网关机器上的远程客户端 secrets（`gateway.remote.token` / `.password`）。
3. 轮换 provider / API 凭证（WhatsApp 凭证、Slack / Discord tokens、`auth-profiles.json` 中的模型 / API keys，以及启用时的加密 secrets 负载值）。

### 审计

1. 检查 Gateway 网关日志：`/tmp/openclaw/openclaw-YYYY-MM-DD.log`（或 `logging.file`）。
2. 查看相关转录内容：`~/.openclaw/agents/<agentId>/sessions/*.jsonl`。
3. 查看最近的配置变更（任何可能扩大访问范围的项：`gateway.bind`、`gateway.auth`、私信 / 群组策略、`tools.elevated`、插件变更）。
4. 重新运行 `openclaw security audit --deep`，并确认 critical 级发现已全部解决。

### 为报告收集的信息

- 时间戳、Gateway 网关主机 OS + OpenClaw 版本
- 会话转录内容 + 一小段日志尾部（脱敏后）
- 攻击者发送了什么 + 智能体执行了什么
- Gateway 网关是否暴露到了 loopback 之外（LAN / Tailscale Funnel / Serve）

## Secret Scanning（detect-secrets）

CI 会在 `secrets` job 中运行 `detect-secrets` pre-commit hook。
推送到 `main` 时始终会执行全文件扫描。Pull request 会在有基准 commit 可用时
走已更改文件的快速路径，否则回退为全文件扫描。如果失败，说明出现了尚未写入 baseline 的新候选项。

### 如果 CI 失败

1. 在本地复现：

   ```bash
   pre-commit run --all-files detect-secrets
   ```

2. 了解这些工具：
   - pre-commit 中的 `detect-secrets` 会使用仓库的
     baseline 和 excludes 运行 `detect-secrets-hook`。
   - `detect-secrets audit` 会打开一个交互式审查界面，用于将 baseline
     中的每一项标记为真实 secret 或误报。
3. 对于真实 secrets：轮换 / 删除它们，然后重新运行扫描以更新 baseline。
4. 对于误报：运行交互式审查并将其标记为误报：

   ```bash
   detect-secrets audit .secrets.baseline
   ```

5. 如果你需要新增 excludes，请将其添加到 `.detect-secrets.cfg`，并使用匹配的 `--exclude-files` / `--exclude-lines` 标志重新生成
   baseline（该配置文件仅供参考；detect-secrets 不会自动读取它）。

当更新后的 `.secrets.baseline` 反映出预期状态后，请将其提交。

## 报告安全问题

在 OpenClaw 中发现了漏洞？请负责任地报告：

1. 电子邮件：[security@openclaw.ai](mailto:security@openclaw.ai)
2. 在修复前不要公开发布
3. 我们会为你署名致谢（除非你希望匿名）
