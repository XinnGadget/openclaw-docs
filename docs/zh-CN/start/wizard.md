---
read_when:
    - 运行或配置 CLI 新手引导时
    - 设置一台新机器时
sidebarTitle: 'Onboarding: CLI'
summary: CLI 新手引导：用于 Gateway 网关、工作区、渠道和 Skills 的引导式设置
title: 设置向导（CLI）
x-i18n:
    generated_at: "2026-04-06T15:31:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6773b07afa8babf1b5ac94d857063d08094a962ee21ec96ca966e99ad57d107d
    source_path: start/wizard.md
    workflow: 15
---

# 设置向导（CLI）

CLI 新手引导是在 macOS、
Linux 或 Windows（通过 WSL2，强烈推荐）上设置 OpenClaw 的**推荐**方式。
它会通过一个引导式流程一次性配置本地 Gateway 网关或远程 Gateway 网关连接，以及渠道、Skills
和工作区默认值。

```bash
openclaw onboard
```

<Info>
最快开始第一次聊天的方法：打开 Control UI（无需设置任何渠道）。运行
`openclaw dashboard` 并在浏览器中聊天。文档： [Dashboard](/web/dashboard)。
</Info>

如果之后要重新配置：

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
`--json` 不代表非交互模式。对于脚本，请使用 `--non-interactive`。
</Note>

<Tip>
CLI 新手引导包含一个 Web 搜索步骤，你可以在其中选择提供商，
例如 Brave、DuckDuckGo、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、
Ollama Web 搜索、Perplexity、SearXNG 或 Tavily。有些提供商需要
API key，而另一些不需要。你也可以之后再用
`openclaw configure --section web` 进行配置。文档： [Web 工具](/zh-CN/tools/web)。
</Tip>

## 快速开始 vs 高级

新手引导一开始会让你选择**快速开始**（默认值）还是**高级**（完全控制）。

<Tabs>
  <Tab title="快速开始（默认值）">
    - 本地 Gateway 网关（loopback）
    - 默认工作区（或现有工作区）
    - Gateway 网关端口 **18789**
    - Gateway 网关认证 **Token**（即使在 loopback 上也会自动生成）
    - 新本地设置的默认工具策略：`tools.profile: "coding"`（已有的显式 profile 会被保留）
    - 私信隔离默认值：本地新手引导会在未设置时写入 `session.dmScope: "per-channel-peer"`。详情： [CLI 设置参考](/zh-CN/start/wizard-cli-reference#outputs-and-internals)
    - Tailscale 暴露 **关闭**
    - Telegram + WhatsApp 私信默认使用 **allowlist**（系统会提示你输入手机号）
  </Tab>
  <Tab title="高级（完全控制）">
    - 显示所有步骤（模式、工作区、Gateway 网关、渠道、守护进程、Skills）。
  </Tab>
</Tabs>

## 新手引导会配置什么

**本地模式（默认）**会引导你完成以下步骤：

1. **模型/认证** — 选择任意受支持的提供商/认证流程（API key、OAuth 或提供商专用手动认证），包括 Custom Provider
   （兼容 OpenAI、兼容 Anthropic，或 Unknown 自动检测）。选择一个默认模型。
   安全说明：如果此智能体将运行工具或处理 webhook/hooks 内容，请优先选择当前最强的新一代模型，并保持严格的工具策略。较弱/较旧的层级更容易受到提示注入攻击。
   对于非交互式运行，`--secret-input-mode ref` 会在认证 profile 中存储基于环境变量的引用，而不是明文 API key 值。
   在非交互式 `ref` 模式下，必须设置提供商环境变量；如果传入内联 key flags 但未设置相应环境变量，将会快速失败。
   在交互式运行中，选择 secret 引用模式后，你可以指向环境变量或已配置的提供商引用（`file` 或 `exec`），并在保存前进行快速预检验证。
   对于 Anthropic，交互式新手引导/配置会将 **Anthropic Claude CLI** 作为首选本地路径，并将 **Anthropic API key** 作为推荐的生产路径。Anthropic setup-token 也仍然可作为受支持的 token 认证路径。
2. **工作区** — 智能体文件的位置（默认 `~/.openclaw/workspace`）。会植入引导文件。
3. **Gateway 网关** — 端口、绑定地址、认证模式、Tailscale 暴露。
   在交互式 token 模式中，你可以选择默认的明文 token 存储，或改用 SecretRef。
   非交互式 token SecretRef 路径：`--gateway-token-ref-env <ENV_VAR>`。
4. **渠道** — 内置和内置打包的聊天渠道，例如 BlueBubbles、Discord、Feishu、Google Chat、Mattermost、Microsoft Teams、QQ Bot、Signal、Slack、Telegram、WhatsApp 等。
5. **守护进程** — 安装 LaunchAgent（macOS）、systemd 用户单元（Linux/WSL2），或原生 Windows 计划任务，并提供按用户 Startup 文件夹回退方案。
   如果 token 认证需要 token 且 `gateway.auth.token` 由 SecretRef 管理，守护进程安装会验证它，但不会将解析后的 token 持久化到 supervisor 服务环境元数据中。
   如果 token 认证需要 token 且已配置的 token SecretRef 无法解析，守护进程安装将被阻止，并给出可执行的指引。
   如果同时配置了 `gateway.auth.token` 和 `gateway.auth.password`，但 `gateway.auth.mode` 未设置，守护进程安装将被阻止，直到显式设置 mode。
6. **健康检查** — 启动 Gateway 网关并验证它是否正在运行。
7. **Skills** — 安装推荐的 Skills 和可选依赖。

<Note>
重新运行新手引导**不会**清除任何内容，除非你明确选择 **Reset**（或传入 `--reset`）。
CLI `--reset` 默认会重置 config、credentials 和 sessions；使用 `--reset-scope full` 可将 workspace 也包括进去。
如果配置无效或包含旧版键名，新手引导会要求你先运行 `openclaw doctor`。
</Note>

**远程模式**只会配置本地客户端去连接另一处的 Gateway 网关。
它**不会**在远程主机上安装或更改任何内容。

## 添加另一个智能体

使用 `openclaw agents add <name>` 创建一个拥有独立工作区、
会话和认证 profile 的单独智能体。不带 `--workspace` 运行时会启动新手引导。

它会设置：

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

说明：

- 默认工作区遵循 `~/.openclaw/workspace-<agentId>`。
- 添加 `bindings` 可路由入站消息（新手引导可以完成此操作）。
- 非交互式 flags：`--model`、`--agent-dir`、`--bind`、`--non-interactive`。

## 完整参考

有关详细的分步骤说明和配置输出，请参见
[CLI 设置参考](/zh-CN/start/wizard-cli-reference)。
有关非交互式示例，请参见 [CLI 自动化](/zh-CN/start/wizard-cli-automation)。
有关更深入的技术参考（包括 RPC 细节），请参见
[新手引导参考](/zh-CN/reference/wizard)。

## 相关文档

- CLI 命令参考：[`openclaw onboard`](/cli/onboard)
- 新手引导概览：[新手引导概览](/zh-CN/start/onboarding-overview)
- macOS 应用新手引导：[新手引导](/zh-CN/start/onboarding)
- 智能体首次运行仪式：[智能体引导](/zh-CN/start/bootstrapping)
