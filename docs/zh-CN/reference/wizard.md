---
read_when:
    - 查找特定的新手引导步骤或标志
    - 使用非交互模式自动化新手引导
    - 调试新手引导行为
sidebarTitle: Onboarding Reference
summary: CLI 新手引导的完整参考：每一步、每个标志和每个配置字段
title: 新手引导参考
x-i18n:
    generated_at: "2026-04-06T15:31:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: a142b9ec4323fabb9982d05b64375d2b4a4007dffc910acbee3a38ff871a7236
    source_path: reference/wizard.md
    workflow: 15
---

# 新手引导参考

这是 `openclaw onboard` 的完整参考。
如需高层概览，请参见 [新手引导（CLI）](/zh-CN/start/wizard)。

## 流程详情（本地模式）

<Steps>
  <Step title="现有配置检测">
    - 如果 `~/.openclaw/openclaw.json` 存在，可选择 **保留 / 修改 / 重置**。
    - 重新运行新手引导**不会**清除任何内容，除非你明确选择 **重置**
      （或传入 `--reset`）。
    - CLI `--reset` 默认范围是 `config+creds+sessions`；使用 `--reset-scope full`
      还会删除工作区。
    - 如果配置无效或包含旧版键名，向导会停止并要求
      你先运行 `openclaw doctor` 再继续。
    - 重置使用 `trash`（绝不使用 `rm`），并提供以下范围：
      - 仅配置
      - 配置 + 凭证 + 会话
      - 完全重置（也会删除工作区）
  </Step>
  <Step title="模型/凭证">
    - **Anthropic API 密钥**：如果存在则使用 `ANTHROPIC_API_KEY`，否则提示输入密钥，然后保存以供守护进程使用。
    - **Anthropic API 密钥**：在新手引导/配置中是 Anthropic 助手的首选选项。
    - **Anthropic setup-token**：在新手引导/配置中仍然可用，不过 OpenClaw 现在在可用时更倾向于复用 Claude CLI。
    - **OpenAI Code（Codex）订阅（Codex CLI）**：如果 `~/.codex/auth.json` 存在，新手引导可以复用它。被复用的 Codex CLI 凭证仍由 Codex CLI 管理；过期时，OpenClaw 会先重新读取该来源，并在提供商能够刷新时，将刷新后的凭证写回 Codex 存储，而不是自行接管。
    - **OpenAI Code（Codex）订阅（OAuth）**：浏览器流程；粘贴 `code#state`。
      - 当模型未设置或为 `openai/*` 时，将 `agents.defaults.model` 设置为 `openai-codex/gpt-5.4`。
    - **OpenAI API 密钥**：如果存在则使用 `OPENAI_API_KEY`，否则提示输入密钥，然后将其存储到凭证配置文件中。
      - 当模型未设置、为 `openai/*` 或 `openai-codex/*` 时，将 `agents.defaults.model` 设置为 `openai/gpt-5.4`。
    - **xAI（Grok）API 密钥**：提示输入 `XAI_API_KEY` 并将 xAI 配置为模型提供商。
    - **OpenCode**：提示输入 `OPENCODE_API_KEY`（或 `OPENCODE_ZEN_API_KEY`，可在 https://opencode.ai/auth 获取），并让你选择 Zen 或 Go 目录。
    - **Ollama**：提示输入 Ollama base URL，提供 **Cloud + Local** 或 **Local** 模式，发现可用模型，并在需要时自动拉取所选本地模型。
    - 更多细节：[Ollama](/zh-CN/providers/ollama)
    - **API 密钥**：为你存储该密钥。
    - **Vercel AI Gateway（多模型代理）**：提示输入 `AI_GATEWAY_API_KEY`。
    - 更多细节：[Vercel AI Gateway](/zh-CN/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**：提示输入 Account ID、Gateway ID 和 `CLOUDFLARE_AI_GATEWAY_API_KEY`。
    - 更多细节：[Cloudflare AI Gateway](/zh-CN/providers/cloudflare-ai-gateway)
    - **MiniMax**：会自动写入配置；托管默认模型是 `MiniMax-M2.7`。
      API 密钥设置使用 `minimax/...`，而 OAuth 设置使用
      `minimax-portal/...`。
    - 更多细节：[MiniMax](/zh-CN/providers/minimax)
    - **StepFun**：会为中国或全球端点上的 StepFun standard 或 Step Plan 自动写入配置。
    - 标准版当前包含 `step-3.5-flash`，Step Plan 还包含 `step-3.5-flash-2603`。
    - 更多细节：[StepFun](/zh-CN/providers/stepfun)
    - **Synthetic（Anthropic 兼容）**：提示输入 `SYNTHETIC_API_KEY`。
    - 更多细节：[Synthetic](/zh-CN/providers/synthetic)
    - **Moonshot（Kimi K2）**：会自动写入配置。
    - **Kimi Coding**：会自动写入配置。
    - 更多细节：[Moonshot AI（Kimi + Kimi Coding）](/zh-CN/providers/moonshot)
    - **跳过**：暂不配置凭证。
    - 从检测到的选项中选择一个默认模型（或手动输入 provider/model）。为了获得最佳质量并降低提示注入风险，请选择你提供商栈中可用的最强最新一代模型。
    - 新手引导会执行模型检查，并在配置的模型未知或缺少凭证时发出警告。
    - API 密钥存储模式默认使用明文 auth-profile 值。使用 `--secret-input-mode ref` 可改为存储基于环境变量的引用（例如 `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`）。
    - 凭证配置文件位于 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（API 密钥 + OAuth）。`~/.openclaw/credentials/oauth.json` 仅用于导入旧版数据。
    - 更多细节：[/concepts/oauth](/zh-CN/concepts/oauth)
    <Note>
    无头/服务器提示：可先在有浏览器的机器上完成 OAuth，然后复制
    该智能体的 `auth-profiles.json`（例如
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`，或对应的
    `$OPENCLAW_STATE_DIR/...` 路径）到 Gateway 网关主机上。`credentials/oauth.json`
    只是旧版导入来源。
    </Note>
  </Step>
  <Step title="工作区">
    - 默认是 `~/.openclaw/workspace`（可配置）。
    - 会初始化智能体 bootstrap ritual 所需的工作区文件。
    - 完整工作区布局和备份指南：[智能体工作区](/zh-CN/concepts/agent-workspace)
  </Step>
  <Step title="Gateway 网关">
    - 端口、绑定、凭证模式、Tailscale 暴露。
    - 凭证建议：即使是 loopback，也请保留 **Token**，这样本地 WS 客户端仍必须进行身份验证。
    - 在 token 模式下，交互式设置提供：
      - **生成/存储明文 token**（默认）
      - **使用 SecretRef**（可选启用）
      - 快速开始会在新手引导探测/仪表板 bootstrap 过程中复用现有的 `gateway.auth.token` SecretRef，支持 `env`、`file` 和 `exec` 提供商。
      - 如果已配置该 SecretRef 但无法解析，新手引导会尽早失败并给出清晰的修复信息，而不是静默降级运行时凭证。
    - 在密码模式下，交互式设置也支持明文或 SecretRef 存储。
    - 非交互 token SecretRef 路径：`--gateway-token-ref-env <ENV_VAR>`。
      - 要求新手引导进程环境中存在非空环境变量。
      - 不能与 `--gateway-token` 一起使用。
    - 仅当你完全信任所有本地进程时才禁用凭证。
    - 非 loopback 绑定仍然需要凭证。
  </Step>
  <Step title="渠道">
    - [WhatsApp](/zh-CN/channels/whatsapp)：可选 QR 登录。
    - [Telegram](/zh-CN/channels/telegram)：机器人令牌。
    - [Discord](/zh-CN/channels/discord)：机器人令牌。
    - [Google Chat](/zh-CN/channels/googlechat)：服务账号 JSON + webhook audience。
    - [Mattermost](/zh-CN/channels/mattermost)（插件）：机器人令牌 + base URL。
    - [Signal](/zh-CN/channels/signal)：可选 `signal-cli` 安装 + 账户配置。
    - [BlueBubbles](/zh-CN/channels/bluebubbles)：**推荐用于 iMessage**；服务器 URL + 密码 + webhook。
    - [iMessage](/zh-CN/channels/imessage)：旧版 `imsg` CLI 路径 + DB 访问。
    - 私信安全：默认启用配对。首次私信会发送一个代码；通过 `openclaw pairing approve <channel> <code>` 批准，或使用允许列表。
  </Step>
  <Step title="Web 搜索">
    - 选择一个受支持的提供商，例如 Brave、DuckDuckGo、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Ollama Web 搜索、Perplexity、SearXNG 或 Tavily（也可以跳过）。
    - 基于 API 的提供商可以使用环境变量或现有配置快速设置；无需密钥的提供商则使用其各自的前置条件。
    - 使用 `--skip-search` 跳过。
    - 稍后配置：`openclaw configure --section web`。
  </Step>
  <Step title="守护进程安装">
    - macOS：LaunchAgent
      - 需要已登录的用户会话；对于无头场景，请使用自定义 LaunchDaemon（未内置）。
    - Linux（以及通过 WSL2 的 Windows）：systemd 用户单元
      - 新手引导会尝试通过 `loginctl enable-linger <user>` 启用 lingering，这样 Gateway 网关在登出后仍能保持运行。
      - 可能会提示 sudo（会写入 `/var/lib/systemd/linger`）；会先尝试不使用 sudo。
    - **运行时选择：** Node（推荐；WhatsApp/Telegram 必需）。**不推荐** Bun。
    - 如果 token 凭证需要 token 且 `gateway.auth.token` 由 SecretRef 管理，守护进程安装会验证它，但不会把解析后的明文 token 值持久化到 supervisor 服务环境元数据中。
    - 如果 token 凭证需要 token 且配置的 token SecretRef 未解析，守护进程安装会被阻止，并给出可操作的指导。
    - 如果同时配置了 `gateway.auth.token` 和 `gateway.auth.password`，而 `gateway.auth.mode` 未设置，则会阻止守护进程安装，直到明确设置 mode。
  </Step>
  <Step title="健康检查">
    - 启动 Gateway 网关（如有需要）并运行 `openclaw health`。
    - 提示：`openclaw status --deep` 会将 live Gateway 网关健康探测添加到状态输出中，在支持时也包括渠道探测（需要能访问到 Gateway 网关）。
  </Step>
  <Step title="Skills（推荐）">
    - 读取可用的 Skills 并检查要求。
    - 让你选择一个 node 管理器：**npm / pnpm**（不推荐 bun）。
    - 安装可选依赖（有些会在 macOS 上使用 Homebrew）。
  </Step>
  <Step title="完成">
    - 显示摘要和后续步骤，包括 iOS/Android/macOS 应用以启用更多功能。
  </Step>
</Steps>

<Note>
如果未检测到 GUI，新手引导会打印用于 Control UI 的 SSH 端口转发说明，而不是打开浏览器。
如果缺少 Control UI 资源，新手引导会尝试构建它们；回退命令是 `pnpm ui:build`（会自动安装 UI 依赖）。
</Note>

## 非交互模式

使用 `--non-interactive` 来自动化或脚本化新手引导：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

添加 `--json` 可获得机器可读的摘要。

非交互模式中的 Gateway 网关 token SecretRef：

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token` 和 `--gateway-token-ref-env` 互斥。

<Note>
`--json` **不**意味着非交互模式。脚本中请使用 `--non-interactive`（以及 `--workspace`）。
</Note>

提供商专用命令示例位于 [CLI 自动化](/zh-CN/start/wizard-cli-automation#provider-specific-examples)。
本参考页用于说明标志语义和步骤顺序。

### 添加智能体（非交互）

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## Gateway 网关向导 RPC

Gateway 网关通过 RPC 暴露新手引导流程（`wizard.start`、`wizard.next`、`wizard.cancel`、`wizard.status`）。
客户端（macOS 应用、Control UI）可以渲染步骤，而无需重新实现新手引导逻辑。

## Signal 设置（signal-cli）

新手引导可以从 GitHub releases 安装 `signal-cli`：

- 下载合适的发布资源。
- 将其存储到 `~/.openclaw/tools/signal-cli/<version>/`。
- 将 `channels.signal.cliPath` 写入你的配置。

说明：

- JVM 构建需要 **Java 21**。
- 在可用时会使用原生构建。
- Windows 使用 WSL2；`signal-cli` 安装会在 WSL 内遵循 Linux 流程。

## 向导会写入什么

`~/.openclaw/openclaw.json` 中的典型字段：

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（如果选择了 Minimax）
- `tools.profile`（本地新手引导在未设置时默认使用 `"coding"`；现有的显式值会被保留）
- `gateway.*`（mode、bind、auth、tailscale）
- `session.dmScope`（行为细节：[CLI 设置参考](/zh-CN/start/wizard-cli-reference#outputs-and-internals)）
- `channels.telegram.botToken`、`channels.discord.token`、`channels.matrix.*`、`channels.signal.*`、`channels.imessage.*`
- 当你在提示中选择启用时，会写入渠道允许列表（Slack/Discord/Matrix/Microsoft Teams）（在可能时会将名称解析为 ID）。
- `skills.install.nodeManager`
  - `setup --node-manager` 接受 `npm`、`pnpm` 或 `bun`。
  - 手动配置仍可通过直接设置 `skills.install.nodeManager` 使用 `yarn`。
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` 会写入 `agents.list[]` 和可选的 `bindings`。

WhatsApp 凭证位于 `~/.openclaw/credentials/whatsapp/<accountId>/`。
会话存储在 `~/.openclaw/agents/<agentId>/sessions/` 下。

某些渠道以插件形式交付。当你在设置期间选择其中一个时，新手引导
会先提示安装它（npm 或本地路径），然后才能进行配置。

## 相关文档

- 新手引导概览：[新手引导（CLI）](/zh-CN/start/wizard)
- macOS 应用新手引导：[新手引导](/zh-CN/start/onboarding)
- 配置参考：[Gateway 网关配置](/zh-CN/gateway/configuration)
- 提供商：[WhatsApp](/zh-CN/channels/whatsapp)、[Telegram](/zh-CN/channels/telegram)、[Discord](/zh-CN/channels/discord)、[Google Chat](/zh-CN/channels/googlechat)、[Signal](/zh-CN/channels/signal)、[BlueBubbles](/zh-CN/channels/bluebubbles)（iMessage）、[iMessage](/zh-CN/channels/imessage)（旧版）
- Skills：[Skills](/zh-CN/tools/skills)、[Skills 配置](/zh-CN/tools/skills-config)
