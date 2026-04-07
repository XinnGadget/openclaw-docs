---
read_when:
    - 回答常见的设置、安装、新手引导或运行时支持问题
    - 在进行更深入调试前，对用户报告的问题进行初步分诊
summary: 关于 OpenClaw 设置、配置和使用的常见问题解答
title: 常见问题
x-i18n:
    generated_at: "2026-04-07T19:46:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: 001b4605966b45b08108606f76ae937ec348c2179b04cf6fb34fef94833705e6
    source_path: help/faq.md
    workflow: 15
---

# 常见问题

为真实世界部署场景提供快速答案以及更深入的故障排除（本地开发、VPS、多智能体、OAuth/API 密钥、模型故障转移）。如需运行时诊断，请参阅 [故障排除](/zh-CN/gateway/troubleshooting)。如需完整配置参考，请参阅 [Configuration](/zh-CN/gateway/configuration)。

## 如果出了问题，最初的六十秒

1. **快速状态（第一步检查）**

   ```bash
   openclaw status
   ```

   快速本地摘要：操作系统 + 更新、Gateway 网关/服务可达性、智能体/会话、提供商配置 + 运行时问题（当 Gateway 网关可达时）。

2. **可直接粘贴的报告（可安全分享）**

   ```bash
   openclaw status --all
   ```

   只读诊断，包含日志尾部（令牌已脱敏）。

3. **守护进程 + 端口状态**

   ```bash
   openclaw gateway status
   ```

   显示监督器运行状态与 RPC 可达性、探测目标 URL，以及服务可能使用的是哪份配置。

4. **深度探测**

   ```bash
   openclaw status --deep
   ```

   运行实时 Gateway 网关健康探测，包括支持时的渠道探测
   （需要 Gateway 网关可达）。参阅 [Health](/zh-CN/gateway/health)。

5. **查看最新日志尾部**

   ```bash
   openclaw logs --follow
   ```

   如果 RPC 不可用，则退回到：

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   文件日志与服务日志是分开的；参阅 [Logging](/zh-CN/logging) 和 [故障排除](/zh-CN/gateway/troubleshooting)。

6. **运行 Doctor（修复）**

   ```bash
   openclaw doctor
   ```

   修复/迁移配置与状态 + 运行健康检查。参阅 [Doctor](/zh-CN/gateway/doctor)。

7. **Gateway 网关快照**

   ```bash
   openclaw health --json
   openclaw health --verbose   # 出错时显示目标 URL + 配置路径
   ```

   向正在运行的 Gateway 网关请求完整快照（仅限 WS）。参阅 [Health](/zh-CN/gateway/health)。

## 快速开始和首次运行设置

<AccordionGroup>
  <Accordion title="我卡住了，最快的脱困方法是什么？">
    使用一个可以**看到你的机器**的本地 AI 智能体。这比去 Discord 提问
    有效得多，因为大多数“我卡住了”的情况都是**本地配置或环境问题**，
    远程协助者无法直接检查。

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    这些工具可以读取仓库、运行命令、检查日志，并帮助修复你机器级别的
    设置（PATH、服务、权限、认证文件）。通过可修改的（git）安装方式，
    将**完整源码检出**提供给它们：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    这会**从 git 检出安装** OpenClaw，因此智能体可以读取代码 + 文档，
    并基于你正在运行的确切版本进行推理。你之后随时可以通过重新运行
    安装器且不带 `--install-method git` 切回稳定版。

    提示：让智能体**规划并监督**修复过程（按步骤进行），然后只执行
    必要的命令。这样改动会更小，也更容易审计。

    如果你发现了真实的 bug 或修复，请提交 GitHub issue 或发送 PR：
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    求助时先运行这些命令（并分享输出）：

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    它们的作用：

    - `openclaw status`: Gateway 网关/智能体健康状态 + 基础配置的快速快照。
    - `openclaw models status`: 检查提供商认证 + 模型可用性。
    - `openclaw doctor`: 验证并修复常见配置/状态问题。

    其他有用的 CLI 检查：`openclaw status --all`、`openclaw logs --follow`、
    `openclaw gateway status`、`openclaw health --verbose`。

    快速调试循环：[如果出了问题，最初的六十秒](#如果出了问题最初的六十秒)。
    安装文档：[Install](/zh-CN/install)、[Installer flags](/zh-CN/install/installer)、[Updating](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="Heartbeat 一直跳过。各种跳过原因是什么意思？">
    常见的 Heartbeat 跳过原因：

    - `quiet-hours`: 不在已配置的活跃时段窗口内
    - `empty-heartbeat-file`: `HEARTBEAT.md` 存在，但只包含空白/仅标题的脚手架内容
    - `no-tasks-due`: `HEARTBEAT.md` 任务模式已启用，但目前没有任何任务间隔到期
    - `alerts-disabled`: 所有 Heartbeat 可见性都已禁用（`showOk`、`showAlerts` 和 `useIndicator` 全部关闭）

    在任务模式下，只有在一次真实的 Heartbeat 运行
    完成后，到期时间戳才会推进。被跳过的运行不会把任务标记为已完成。

    文档：[Heartbeat](/zh-CN/gateway/heartbeat)、[自动化与任务](/zh-CN/automation)。

  </Accordion>

  <Accordion title="安装和设置 OpenClaw 的推荐方式">
    仓库推荐从源码运行并使用新手引导：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    向导也可以自动构建 UI 资源。完成新手引导后，你通常会在 **18789** 端口运行 Gateway 网关。

    从源码开始（贡献者/开发者）：

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # 首次运行时会自动安装 UI 依赖
    openclaw onboard
    ```

    如果你还没有全局安装，也可以通过 `pnpm openclaw onboard` 运行它。

  </Accordion>

  <Accordion title="完成新手引导后，我该如何打开控制面板？">
    向导会在新手引导结束后立即打开浏览器，访问一个干净的（不含令牌的）控制面板 URL，并且也会在摘要中打印该链接。保持这个标签页打开；如果它没有自动启动，就在同一台机器上复制/粘贴打印出的 URL。
  </Accordion>

  <Accordion title="我该如何在 localhost 和远程环境中为控制面板认证？">
    **Localhost（同一台机器）：**

    - 打开 `http://127.0.0.1:18789/`。
    - 如果它要求共享密钥认证，请将已配置的令牌或密码粘贴到 Control UI 设置中。
    - 令牌来源：`gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
    - 密码来源：`gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
    - 如果还没有配置共享密钥，可用 `openclaw doctor --generate-gateway-token` 生成令牌。

    **不在 localhost：**

    - **Tailscale Serve**（推荐）：保持绑定 loopback，运行 `openclaw gateway --tailscale serve`，打开 `https://<magicdns>/`。如果 `gateway.auth.allowTailscale` 为 `true`，身份头会满足 Control UI/WebSocket 认证要求（无需粘贴共享密钥，前提是信任 Gateway 网关主机）；HTTP API 仍然需要共享密钥认证，除非你有意使用私有入口 `none` 或 trusted-proxy HTTP 认证。
      来自同一客户端的并发错误 Serve 认证尝试会在失败认证限流器记录之前被串行化，因此第二次错误重试可能已经显示 `retry later`。
    - **Tailnet 绑定**：运行 `openclaw gateway --bind tailnet --token "<token>"`（或配置密码认证），打开 `http://<tailscale-ip>:18789/`，然后在控制面板设置中粘贴匹配的共享密钥。
    - **支持身份感知的反向代理**：将 Gateway 网关保留在非 loopback 的 trusted proxy 后面，配置 `gateway.auth.mode: "trusted-proxy"`，然后打开代理 URL。
    - **SSH 隧道**：`ssh -N -L 18789:127.0.0.1:18789 user@host` 然后打开 `http://127.0.0.1:18789/`。共享密钥认证在隧道上仍然有效；如有提示，请粘贴已配置的令牌或密码。

    参阅 [Dashboard](/web/dashboard) 和 [Web surfaces](/web) 了解绑定模式和认证细节。

  </Accordion>

  <Accordion title="为什么聊天审批有两个 exec approval 配置？">
    它们控制的是不同层：

    - `approvals.exec`: 将审批提示转发到聊天目标
    - `channels.<channel>.execApprovals`: 让该渠道作为 exec 审批的原生审批客户端

    主机的 exec 策略仍然是真正的审批关卡。聊天配置只控制审批
    提示出现在哪里，以及人们如何回应。

    在大多数设置中，你**不**需要同时用到两者：

    - 如果聊天本身已经支持命令和回复，那么同聊天中的 `/approve` 会通过共享路径生效。
    - 如果受支持的原生渠道能够安全推断审批人，OpenClaw 现在会在 `channels.<channel>.execApprovals.enabled` 未设置或为 `"auto"` 时，自动启用私信优先的原生审批。
    - 当提供原生审批卡片/按钮时，该原生 UI 是主要路径；只有当工具结果表明聊天审批不可用或手动审批是唯一方式时，智能体才应包含手动 `/approve` 命令。
    - 仅当提示也必须转发到其他聊天或明确的运维房间时，才使用 `approvals.exec`。
    - 仅当你明确希望审批提示也发回原始房间/话题时，才使用 `channels.<channel>.execApprovals.target: "channel"` 或 `"both"`。
    - 插件审批又是另一套：默认使用同聊天 `/approve`，可选 `approvals.plugin` 转发，并且只有部分原生渠道会在此基础上保留原生插件审批处理。

    简单来说：转发用于路由，原生客户端配置用于提供更丰富的渠道特定 UX。
    参阅 [Exec Approvals](/zh-CN/tools/exec-approvals)。

  </Accordion>

  <Accordion title="我需要什么运行时？">
    需要 Node **>= 22**。推荐使用 `pnpm`。**不推荐**为 Gateway 网关使用 Bun。
  </Accordion>

  <Accordion title="它能在 Raspberry Pi 上运行吗？">
    可以。Gateway 网关很轻量——文档列出的个人使用需求为 **512MB-1GB RAM**、**1 个核心** 和约 **500MB**
    磁盘空间，并说明 **Raspberry Pi 4 可以运行它**。

    如果你想要更多余量（日志、媒体、其他服务），推荐 **2GB**，但这
    不是硬性最低要求。

    提示：小型 Pi/VPS 可以托管 Gateway 网关，而你可以在笔记本/手机上配对**节点**以实现
    本地屏幕/摄像头/canvas 或命令执行。参阅 [Nodes](/zh-CN/nodes)。

  </Accordion>

  <Accordion title="Raspberry Pi 安装有什么建议吗？">
    简短版本：可以运行，但要预期会有一些边角问题。

    - 使用 **64 位**操作系统，并保持 Node >= 22。
    - 优先选择**可修改的（git）安装**，这样你可以查看日志并快速更新。
    - 开始时先不要加渠道/Skills，然后再逐个添加。
    - 如果你遇到奇怪的二进制问题，通常是 **ARM 兼容性**问题。

    文档：[Linux](/zh-CN/platforms/linux)、[Install](/zh-CN/install)。

  </Accordion>

  <Accordion title="它卡在 wake up my friend / onboarding will not hatch。现在怎么办？">
    这个界面依赖 Gateway 网关可达且已认证。TUI 也会在首次 hatch 时自动发送
    “Wake up, my friend!”。如果你看到这行文字却**没有回复**，
    并且令牌数保持为 0，说明智能体根本没有运行。

    1. 重启 Gateway 网关：

    ```bash
    openclaw gateway restart
    ```

    2. 检查状态 + 认证：

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. 如果仍然卡住，运行：

    ```bash
    openclaw doctor
    ```

    如果 Gateway 网关是远程的，请确保隧道/Tailscale 连接正常，且 UI
    指向的是正确的 Gateway 网关。参阅 [Remote access](/zh-CN/gateway/remote)。

  </Accordion>

  <Accordion title="我能把我的设置迁移到新机器（Mac mini）而不用重新做新手引导吗？">
    可以。复制**状态目录**和**工作区**，然后运行一次 Doctor。这会
    让你的机器人“完全保持不变”（记忆、会话历史、认证和渠道
    状态），前提是你复制了**这两个**位置：

    1. 在新机器上安装 OpenClaw。
    2. 从旧机器复制 `$OPENCLAW_STATE_DIR`（默认：`~/.openclaw`）。
    3. 复制你的工作区（默认：`~/.openclaw/workspace`）。
    4. 运行 `openclaw doctor` 并重启 Gateway 网关服务。

    这会保留配置、认证配置文件、WhatsApp 凭据、会话和记忆。如果你使用的是
    远程模式，请记住会话存储和工作区都由 gateway host 拥有。

    **重要：**如果你只是把工作区提交/推送到 GitHub，你备份的是
    **记忆 + 引导文件**，但**不是**会话历史或认证。那些内容位于
    `~/.openclaw/` 下（例如 `~/.openclaw/agents/<agentId>/sessions/`）。

    相关内容：[Migrating](/zh-CN/install/migrating)、[磁盘上的文件位置](#磁盘上的文件位置)、
    [智能体工作区](/zh-CN/concepts/agent-workspace)、[Doctor](/zh-CN/gateway/doctor)、
    [远程模式](/zh-CN/gateway/remote)。

  </Accordion>

  <Accordion title="我去哪里查看最新版本有哪些新内容？">
    查看 GitHub 更新日志：
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    最新条目在最上方。如果顶部部分标记为 **Unreleased**，那么下一个带日期的
    部分就是最近发布的版本。条目按 **Highlights**、**Changes** 和
    **Fixes** 分组（需要时还会包含文档/其他部分）。

  </Accordion>

  <Accordion title="无法访问 docs.openclaw.ai（SSL 错误）">
    某些 Comcast/Xfinity 连接会因为 Xfinity
    Advanced Security 错误地拦截 `docs.openclaw.ai`。请禁用它或将 `docs.openclaw.ai`
    加入允许列表，然后重试。
    也请帮我们通过这里报告以便解除拦截：[https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status)。

    如果你仍然无法访问该站点，文档在 GitHub 上也有镜像：
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="稳定版和 beta 的区别">
    **Stable** 和 **beta** 是 **npm dist-tag**，不是不同的代码分支：

    - `latest` = 稳定版
    - `beta` = 用于测试的早期构建

    通常，一个稳定版本会先发布到 **beta**，然后通过一个显式的
    提升步骤把同一个版本移动到 `latest`。维护者在需要时也可以
    直接发布到 `latest`。这就是为什么 beta 和稳定版在提升后可以
    指向**同一个版本**。

    查看改动内容：
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    关于安装单行命令以及 beta 和 dev 的区别，请参阅下面的折叠项。

  </Accordion>

  <Accordion title="我该如何安装 beta 版本，以及 beta 和 dev 有什么区别？">
    **Beta** 是 npm dist-tag `beta`（提升后可能与 `latest` 相同）。
    **Dev** 是 `main` 的移动头部（git）；发布时使用 npm dist-tag `dev`。

    单行命令（macOS/Linux）：

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Windows 安装器（PowerShell）：
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    更多细节：[Development channels](/zh-CN/install/development-channels) 和 [Installer flags](/zh-CN/install/installer)。

  </Accordion>

  <Accordion title="我该如何尝试最新内容？">
    有两种方式：

    1. **Dev 渠道（git 检出）：**

    ```bash
    openclaw update --channel dev
    ```

    这会切换到 `main` 分支并从源码更新。

    2. **可修改安装（来自安装站点）：**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    这样你就会得到一个可以本地编辑的仓库，然后通过 git 更新。

    如果你更喜欢手动做一次干净克隆，请使用：

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    文档：[Update](/cli/update)、[Development channels](/zh-CN/install/development-channels)、
    [Install](/zh-CN/install)。

  </Accordion>

  <Accordion title="安装和新手引导通常需要多长时间？">
    大致参考：

    - **安装：**2-5 分钟
    - **新手引导：**5-15 分钟，取决于你配置了多少渠道/模型

    如果卡住了，请查看 [安装器卡住了](#快速开始和首次运行设置)
    以及 [我卡住了](#快速开始和首次运行设置) 中的快速调试循环。

  </Accordion>

  <Accordion title="安装器卡住了？我该如何获取更多反馈？">
    使用**详细输出**重新运行安装器：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    带详细输出的 beta 安装：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    对于可修改的（git）安装：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Windows（PowerShell）等效方式：

    ```powershell
    # install.ps1 目前还没有专门的 -Verbose 标志。
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    更多选项：[Installer flags](/zh-CN/install/installer)。

  </Accordion>

  <Accordion title="Windows 安装时提示 git not found 或 openclaw not recognized">
    两个常见的 Windows 问题：

    **1) npm 错误 spawn git / git not found**

    - 安装 **Git for Windows** 并确保 `git` 在你的 PATH 中。
    - 关闭并重新打开 PowerShell，然后重新运行安装器。

    **2) 安装后 openclaw is not recognized**

    - 你的 npm 全局 bin 目录不在 PATH 中。
    - 检查路径：

      ```powershell
      npm config get prefix
      ```

    - 将该目录添加到你的用户 PATH 中（Windows 上不需要 `\bin` 后缀；大多数系统上是 `%AppData%\npm`）。
    - 更新 PATH 后，关闭并重新打开 PowerShell。

    如果你想获得最顺畅的 Windows 设置体验，请使用 **WSL2**，而不是原生 Windows。
    文档：[Windows](/zh-CN/platforms/windows)。

  </Accordion>

  <Accordion title="Windows exec 输出显示乱码中文 - 我该怎么办？">
    这通常是原生 Windows shell 的控制台代码页不匹配所致。

    症状：

    - `system.run`/`exec` 输出将中文显示为乱码
    - 同一命令在另一个终端配置中显示正常

    在 PowerShell 中的快速解决方法：

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    然后重启 Gateway 网关并重试你的命令：

    ```powershell
    openclaw gateway restart
    ```

    如果你在最新 OpenClaw 上仍然能复现，请在以下位置跟踪/报告：

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="文档没有回答我的问题 - 我该如何得到更好的答案？">
    使用**可修改的（git）安装**，这样你就能在本地拥有完整源码和文档，然后
    在_该文件夹内_向你的机器人（或 Claude/Codex）提问，这样它就可以读取仓库并给出精确回答。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    更多细节：[Install](/zh-CN/install) 和 [Installer flags](/zh-CN/install/installer)。

  </Accordion>

  <Accordion title="我该如何在 Linux 上安装 OpenClaw？">
    简短回答：按照 Linux 指南操作，然后运行新手引导。

    - Linux 快速路径 + 服务安装：[Linux](/zh-CN/platforms/linux)。
    - 完整演练：[入门指南](/zh-CN/start/getting-started)。
    - 安装器 + 更新：[Install & updates](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="我该如何在 VPS 上安装 OpenClaw？">
    任何 Linux VPS 都可以。在服务器上安装，然后使用 SSH/Tailscale 访问 Gateway 网关。

    指南：[exe.dev](/zh-CN/install/exe-dev)、[Hetzner](/zh-CN/install/hetzner)、[Fly.io](/zh-CN/install/fly)。
    远程访问：[Gateway remote](/zh-CN/gateway/remote)。

  </Accordion>

  <Accordion title="云端/VPS 安装指南在哪里？">
    我们维护了一个**托管中心**，列出常见提供商。选择一个并按照指南操作：

    - [VPS hosting](/zh-CN/vps)（所有提供商汇总在一个地方）
    - [Fly.io](/zh-CN/install/fly)
    - [Hetzner](/zh-CN/install/hetzner)
    - [exe.dev](/zh-CN/install/exe-dev)

    它在云端的工作方式：**Gateway 网关运行在服务器上**，你通过
    Control UI（或 Tailscale/SSH）从笔记本/手机访问它。你的状态 + 工作区
    也保存在服务器上，因此应将该主机视为事实来源并做好备份。

    你可以把**节点**（Mac/iOS/Android/无头设备）配对到这个云端 Gateway 网关，
    以访问本地屏幕/摄像头/canvas，或在笔记本上运行命令，同时将
    Gateway 网关保留在云端。

    中心页：[Platforms](/zh-CN/platforms)。远程访问：[Gateway remote](/zh-CN/gateway/remote)。
    节点：[Nodes](/zh-CN/nodes)、[Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="我能让 OpenClaw 自己更新自己吗？">
    简短回答：**可以，但不推荐**。更新流程可能会重启
    Gateway 网关（这会中断当前会话），可能需要一个干净的 git 检出，
    并且可能会要求确认。更安全的做法：由操作员在 shell 中运行更新。

    使用 CLI：

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    如果你必须从智能体中自动化：

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    文档：[Update](/cli/update)、[Updating](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="新手引导实际上会做什么？">
    `openclaw onboard` 是推荐的设置路径。在**本地模式**下，它会引导你完成：

    - **模型/认证设置**（提供商 OAuth、API 密钥、Anthropic setup-token，以及 LM Studio 等本地模型选项）
    - **工作区**位置 + 引导文件
    - **Gateway 网关设置**（绑定/端口/认证/tailscale）
    - **渠道**（WhatsApp、Telegram、Discord、Mattermost、Signal、iMessage，以及 QQ Bot 等内置渠道插件）
    - **守护进程安装**（macOS 上为 LaunchAgent；Linux/WSL2 上为 systemd user unit）
    - **健康检查** 和 **Skills** 选择

    如果你配置的模型未知或缺少认证，它还会发出警告。

  </Accordion>

  <Accordion title="运行这个需要 Claude 或 OpenAI 订阅吗？">
    不需要。你可以使用**API 密钥**（Anthropic/OpenAI/其他）运行 OpenClaw，或者使用
    **纯本地模型**，这样你的数据就能保留在设备上。这些订阅（Claude
    Pro/Max 或 OpenAI Codex）只是为这些提供商认证的可选方式。

    对于 OpenClaw 中的 Anthropic，实际区分如下：

    - **Anthropic API key**：正常的 Anthropic API 计费
    - **OpenClaw 中的 Claude CLI / Claude 订阅认证**：Anthropic 员工
      告诉我们，这种用法再次被允许，因此 OpenClaw 将 `claude -p`
      的使用视为此集成下被认可的用法，除非 Anthropic 发布新的
      政策

    对于长期运行的 gateway host，Anthropic API 密钥仍然是
    更可预测的设置方式。OpenAI Codex OAuth 则被明确支持用于
    OpenClaw 这类外部工具。

    OpenClaw 还支持其他托管型订阅选项，包括
    **Qwen Cloud Coding Plan**、**MiniMax Coding Plan** 和
    **Z.AI / GLM Coding Plan**。

    文档：[Anthropic](/zh-CN/providers/anthropic)、[OpenAI](/zh-CN/providers/openai)、
    [Qwen Cloud](/zh-CN/providers/qwen)、
    [MiniMax](/zh-CN/providers/minimax)、[GLM Models](/zh-CN/providers/glm)、
    [Local models](/zh-CN/gateway/local-models)、[Models](/zh-CN/concepts/models)。

  </Accordion>

  <Accordion title="我可以在没有 API key 的情况下使用 Claude Max 订阅吗？">
    可以。

    Anthropic 员工告诉我们，OpenClaw 风格的 Claude CLI 用法再次被允许，因此
    OpenClaw 将 Claude 订阅认证和 `claude -p` 用法视为此集成下被认可的方式，
    除非 Anthropic 发布新的政策。如果你想要
    最可预测的服务端设置，请改用 Anthropic API key。

  </Accordion>

  <Accordion title="你们支持 Claude 订阅认证（Claude Pro 或 Max）吗？">
    支持。

    Anthropic 员工告诉我们，这种用法再次被允许，因此 OpenClaw 将
    Claude CLI 复用和 `claude -p` 用法视为此集成下被认可的方式，
    除非 Anthropic 发布新的政策。

    Anthropic setup-token 仍然可作为受支持的 OpenClaw 令牌路径，但 OpenClaw 现在更偏好在可用时复用 Claude CLI 和 `claude -p`。
    对于生产环境或多用户工作负载，Anthropic API key 认证仍然是
    更安全、更可预测的选择。如果你想在 OpenClaw 中使用其他托管型订阅
    选项，请参阅 [OpenAI](/zh-CN/providers/openai)、[Qwen / Model
    Cloud](/zh-CN/providers/qwen)、[MiniMax](/zh-CN/providers/minimax) 和 [GLM
    Models](/zh-CN/providers/glm)。

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="为什么我会看到来自 Anthropic 的 HTTP 429 rate_limit_error？">
这意味着你当前窗口内的 **Anthropic 配额/速率限制** 已耗尽。如果你
使用 **Claude CLI**，请等待窗口重置或升级你的套餐。如果你
使用 **Anthropic API key**，请检查 Anthropic Console
中的使用量/计费情况，并按需提高限额。

    如果消息明确是：
    `Extra usage is required for long context requests`，则说明该请求正在尝试使用
    Anthropic 的 1M 上下文 beta（`context1m: true`）。这只有在你的
    凭据有资格进行长上下文计费时才有效（API key 计费，或者启用了 Extra Usage 的
    OpenClaw Claude 登录路径）。

    提示：设置一个**后备模型**，这样当某个提供商被限流时，OpenClaw 仍能继续回复。
    参阅 [Models](/cli/models)、[OAuth](/zh-CN/concepts/oauth) 和
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/zh-CN/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context)。

  </Accordion>

  <Accordion title="支持 AWS Bedrock 吗？">
    支持。OpenClaw 内置了 **Amazon Bedrock（Converse）** 提供商。当 AWS 环境标记存在时，OpenClaw 可以自动发现流式/文本 Bedrock 目录，并将其合并为隐式的 `amazon-bedrock` 提供商；否则你也可以显式启用 `plugins.entries.amazon-bedrock.config.discovery.enabled`，或手动添加一个提供商条目。参阅 [Amazon Bedrock](/zh-CN/providers/bedrock) 和 [Model providers](/zh-CN/providers/models)。如果你更偏好托管密钥流程，在 Bedrock 前面使用 OpenAI 兼容代理仍然是一个可行选择。
  </Accordion>

  <Accordion title="Codex 认证是如何工作的？">
    OpenClaw 通过 OAuth（ChatGPT 登录）支持 **OpenAI Code（Codex）**。新手引导可以运行 OAuth 流程，并会在适当时将默认模型设为 `openai-codex/gpt-5.4`。参阅 [Model providers](/zh-CN/concepts/model-providers) 和 [新手引导（CLI）](/zh-CN/start/wizard)。
  </Accordion>

  <Accordion title="为什么 ChatGPT GPT-5.4 不会在 OpenClaw 中解锁 openai/gpt-5.4？">
    OpenClaw 将这两种路径分开处理：

    - `openai-codex/gpt-5.4` = ChatGPT/Codex OAuth
    - `openai/gpt-5.4` = 直接 OpenAI Platform API

    在 OpenClaw 中，ChatGPT/Codex 登录绑定到 `openai-codex/*` 路由，
    而不是直接的 `openai/*` 路由。如果你希望在
    OpenClaw 中使用直接 API 路径，请设置 `OPENAI_API_KEY`（或等效的 OpenAI 提供商配置）。
    如果你希望在 OpenClaw 中使用 ChatGPT/Codex 登录，请使用 `openai-codex/*`。

  </Accordion>

  <Accordion title="为什么 Codex OAuth 限额可能与 ChatGPT Web 不同？">
    `openai-codex/*` 使用 Codex OAuth 路径，而其可用配额窗口由
    OpenAI 管理，并取决于你的套餐。实际上，这些限额可能与
    ChatGPT 网站/应用体验不同，即使两者都绑定在同一账户下。

    OpenClaw 可以在
    `openclaw models status` 中显示当前可见的提供商使用量/配额窗口，但它不会凭空创建
    或将 ChatGPT Web 权限标准化为直接 API 访问。如果你想使用直接的 OpenAI Platform
    计费/限额路径，请配合 API key 使用 `openai/*`。

  </Accordion>

  <Accordion title="你们支持 OpenAI 订阅认证（Codex OAuth）吗？">
    支持。OpenClaw 完全支持 **OpenAI Code（Codex）订阅 OAuth**。
    OpenAI 明确允许在 OpenClaw
    这类外部工具/工作流中使用订阅 OAuth。新手引导可以帮你运行该 OAuth 流程。

    参阅 [OAuth](/zh-CN/concepts/oauth)、[Model providers](/zh-CN/concepts/model-providers) 和 [新手引导（CLI）](/zh-CN/start/wizard)。

  </Accordion>

  <Accordion title="我该如何设置 Gemini CLI OAuth？">
    Gemini CLI 使用的是**插件认证流程**，而不是在 `openclaw.json` 中填写 `client id` 或 `secret`。

    步骤：

    1. 在本地安装 Gemini CLI，确保 `gemini` 在 `PATH` 中
       - Homebrew：`brew install gemini-cli`
       - npm：`npm install -g @google/gemini-cli`
    2. 启用插件：`openclaw plugins enable google`
    3. 登录：`openclaw models auth login --provider google-gemini-cli --set-default`
    4. 登录后的默认模型：`google-gemini-cli/gemini-3-flash-preview`
    5. 如果请求失败，请在 gateway host 上设置 `GOOGLE_CLOUD_PROJECT` 或 `GOOGLE_CLOUD_PROJECT_ID`

    这会将 OAuth 令牌存储在 gateway host 上的认证配置文件中。详情参阅：[Model providers](/zh-CN/concepts/model-providers)。

  </Accordion>

  <Accordion title="本地模型适合日常闲聊吗？">
    通常不适合。OpenClaw 需要大上下文 + 强安全性；小卡会发生截断和泄漏。如果你一定要这样做，请在本地运行你能承受的**最大**模型构建（LM Studio），并查看 [/gateway/local-models](/zh-CN/gateway/local-models)。更小/量化更重的模型会提高提示注入风险——参阅 [Security](/zh-CN/gateway/security)。
  </Accordion>

  <Accordion title="如何让托管模型流量保持在特定区域内？">
    选择固定区域的端点。OpenRouter 为 MiniMax、Kimi 和 GLM 提供美国托管选项；选择美国托管变体即可让数据保留在该区域内。你仍然可以通过使用 `models.mode: "merge"` 将 Anthropic/OpenAI 一并列出，这样在保留所选区域化提供商的同时，也能保留后备模型。
  </Accordion>

  <Accordion title="安装这个必须买一台 Mac Mini 吗？">
    不需要。OpenClaw 可以运行在 macOS 或 Linux 上（Windows 通过 WSL2）。Mac mini 只是可选项——有些人
    会买一台作为常开主机，但小型 VPS、家用服务器或 Raspberry Pi 级别的机器也可以。

    只有在你需要 **仅限 macOS 的工具**时才需要 Mac。对于 iMessage，请使用 [BlueBubbles](/zh-CN/channels/bluebubbles)（推荐）——BlueBubbles 服务器运行在任意 Mac 上，而 Gateway 网关可以运行在 Linux 或其他地方。如果你想使用其他仅限 macOS 的工具，可以在 Mac 上运行 Gateway 网关，或配对一个 macOS 节点。

    文档：[BlueBubbles](/zh-CN/channels/bluebubbles)、[Nodes](/zh-CN/nodes)、[Mac remote mode](/zh-CN/platforms/mac/remote)。

  </Accordion>

  <Accordion title="要支持 iMessage，我需要一台 Mac mini 吗？">
    你需要一台**已登录 Messages 的 macOS 设备**。它**不一定**是 Mac mini——
    任意 Mac 都可以。对于 iMessage，**请使用 [BlueBubbles](/zh-CN/channels/bluebubbles)**（推荐）——BlueBubbles 服务器运行在 macOS 上，而 Gateway 网关可以运行在 Linux 或其他地方。

    常见设置：

    - 在 Linux/VPS 上运行 Gateway 网关，在任意已登录 Messages 的 Mac 上运行 BlueBubbles 服务器。
    - 如果你想要最简单的单机设置，也可以将所有内容都运行在该 Mac 上。

    文档：[BlueBubbles](/zh-CN/channels/bluebubbles)、[Nodes](/zh-CN/nodes)、
    [Mac remote mode](/zh-CN/platforms/mac/remote)。

  </Accordion>

  <Accordion title="如果我买一台 Mac mini 来运行 OpenClaw，我可以把它连接到我的 MacBook Pro 吗？">
    可以。**Mac mini 可以运行 Gateway 网关**，而你的 MacBook Pro 可以作为
    **节点**（配套设备）连接。节点不会运行 Gateway 网关——它们提供额外
    功能，例如该设备上的屏幕/摄像头/canvas 和 `system.run`。

    常见模式：

    - Gateway 网关运行在 Mac mini 上（常开）。
    - MacBook Pro 运行 macOS 应用或节点主机，并与 Gateway 网关配对。
    - 使用 `openclaw nodes status` / `openclaw nodes list` 查看它。

    文档：[Nodes](/zh-CN/nodes)、[Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="我可以使用 Bun 吗？">
    **不推荐**使用 Bun。我们观察到运行时 bug，尤其是在 WhatsApp 和 Telegram 上。
    稳定的 Gateway 网关请使用 **Node**。

    如果你仍想试验 Bun，请在非生产 Gateway 网关上进行，
    且不要启用 WhatsApp/Telegram。

  </Accordion>

  <Accordion title="Telegram：allowFrom 里应该填什么？">
    `channels.telegram.allowFrom` 填的是**真实用户发送者的 Telegram user ID**（数字），而不是机器人用户名。

    新手引导接受 `@username` 输入并会将其解析为数字 ID，但 OpenClaw 授权仅使用数字 ID。

    更安全的方式（无需第三方机器人）：

    - 给你的机器人发私信，然后运行 `openclaw logs --follow` 并查看 `from.id`。

    官方 Bot API：

    - 给你的机器人发私信，然后调用 `https://api.telegram.org/bot<bot_token>/getUpdates` 并查看 `message.from.id`。

    第三方方式（隐私较差）：

    - 给 `@userinfobot` 或 `@getidsbot` 发私信。

    参阅 [/channels/telegram](/zh-CN/channels/telegram#access-control-and-activation)。

  </Accordion>

  <Accordion title="多个人可以使用同一个 WhatsApp 号码连接不同的 OpenClaw 实例吗？">
    可以，通过**多智能体路由**实现。将每个发送者的 WhatsApp **私信**（peer `kind: "direct"`，发送者 E.164 例如 `+15551234567`）绑定到不同的 `agentId`，这样每个人都会拥有自己的工作区和会话存储。回复仍然来自**同一个 WhatsApp 账户**，而私信访问控制（`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`）对每个 WhatsApp 账户来说是全局的。参阅 [Multi-Agent Routing](/zh-CN/concepts/multi-agent) 和 [WhatsApp](/zh-CN/channels/whatsapp)。
  </Accordion>

  <Accordion title='我可以运行一个“fast chat”智能体和一个“Opus for coding”智能体吗？'>
    可以。使用多智能体路由：为每个智能体设置各自的默认模型，然后将入站路由（提供商账户或特定 peers）绑定到各个智能体。示例配置见 [Multi-Agent Routing](/zh-CN/concepts/multi-agent)。另请参阅 [Models](/zh-CN/concepts/models) 和 [Configuration](/zh-CN/gateway/configuration)。
  </Accordion>

  <Accordion title="Homebrew 能在 Linux 上用吗？">
    可以。Homebrew 支持 Linux（Linuxbrew）。快速设置：

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    如果你通过 systemd 运行 OpenClaw，请确保服务 PATH 包含 `/home/linuxbrew/.linuxbrew/bin`（或你的 brew 前缀），以便 `brew` 安装的工具能在非登录 shell 中被解析。
    近期构建还会为 Linux systemd 服务预置常见用户 bin 目录（例如 `~/.local/bin`、`~/.npm-global/bin`、`~/.local/share/pnpm`、`~/.bun/bin`），并在设置时识别 `PNPM_HOME`、`NPM_CONFIG_PREFIX`、`BUN_INSTALL`、`VOLTA_HOME`、`ASDF_DATA_DIR`、`NVM_DIR` 和 `FNM_DIR`。

  </Accordion>

  <Accordion title="可修改的 git 安装和 npm install 的区别">
    - **可修改的（git）安装：**完整源码检出，可编辑，最适合贡献者。
      你在本地运行构建，也可以修补代码/文档。
    - **npm install：**全局 CLI 安装，没有仓库，最适合“只想直接运行”。
      更新来自 npm dist-tag。

    文档：[入门指南](/zh-CN/start/getting-started)、[Updating](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="之后我可以在 npm 安装和 git 安装之间切换吗？">
    可以。安装另一种形式后，运行 Doctor，让 gateway service 指向新的入口点。
    这**不会删除你的数据**——它只会更改 OpenClaw 代码的安装方式。你的状态
    （`~/.openclaw`）和工作区（`~/.openclaw/workspace`）保持不变。

    从 npm 切换到 git：

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    从 git 切换到 npm：

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor 会检测 gateway service 入口点不匹配，并提示将服务配置重写为与当前安装匹配（自动化时使用 `--repair`）。

    备份提示：参阅 [备份策略](#磁盘上的文件位置)。

  </Accordion>

  <Accordion title="我应该在笔记本上运行 Gateway 网关还是 VPS 上？">
    简短回答：**如果你想要 24/7 可靠性，就用 VPS**。如果你想要
    最低阻力，并且可以接受休眠/重启，那就在本地运行。

    **笔记本（本地 Gateway 网关）**

    - **优点：**没有服务器成本，直接访问本地文件，可见的浏览器窗口。
    - **缺点：**休眠/网络断开 = 连接中断，操作系统更新/重启会打断，机器必须保持唤醒。

    **VPS / 云端**

    - **优点：**始终在线，网络稳定，没有笔记本休眠问题，更容易保持运行。
    - **缺点：**通常是无头运行（需要用截图），只能远程访问文件，更新必须 SSH 进去。

    **OpenClaw 特定说明：**WhatsApp/Telegram/Slack/Mattermost/Discord 在 VPS 上都能正常工作。唯一真正的权衡是**无头浏览器**还是可见窗口。参阅 [Browser](/zh-CN/tools/browser)。

    **推荐默认方案：**如果你之前遇到过 gateway disconnect，使用 VPS。本地运行则非常适合你正在主动使用 Mac，且希望访问本地文件或使用可见浏览器做 UI 自动化的场景。

  </Accordion>

  <Accordion title="在专用机器上运行 OpenClaw 有多重要？">
    不是必须，但**出于可靠性和隔离性，推荐这样做**。

    - **专用主机（VPS/Mac mini/Pi）：**始终在线，更少休眠/重启中断，权限更干净，更容易保持运行。
    - **共享笔记本/台式机：**用于测试和主动使用完全没问题，但当机器休眠或更新时，预期会有暂停。

    如果你想两全其美，可以把 Gateway 网关放在专用主机上，再将笔记本配对为一个**节点**，用于本地屏幕/摄像头/exec 工具。参阅 [Nodes](/zh-CN/nodes)。
    有关安全指导，请阅读 [Security](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="最低 VPS 配置和推荐操作系统是什么？">
    OpenClaw 很轻量。对于基础 Gateway 网关 + 一个聊天渠道：

    - **绝对最低：**1 vCPU、1GB RAM、约 500MB 磁盘。
    - **推荐：**1-2 vCPU、2GB RAM 或更多余量（日志、媒体、多个渠道）。节点工具和浏览器自动化可能比较吃资源。

    操作系统：使用 **Ubuntu LTS**（或任意现代 Debian/Ubuntu）。Linux 安装路径在这些系统上测试最充分。

    文档：[Linux](/zh-CN/platforms/linux)、[VPS hosting](/zh-CN/vps)。

  </Accordion>

  <Accordion title="我可以在 VM 中运行 OpenClaw 吗？需要什么配置？">
    可以。把 VM 当作 VPS 来看：它需要始终运行、可访问，并且有足够的
    RAM 用于 Gateway 网关和你启用的任何渠道。

    基线建议：

    - **绝对最低：**1 vCPU、1GB RAM。
    - **推荐：**如果你运行多个渠道、浏览器自动化或媒体工具，建议 2GB RAM 或更多。
    - **操作系统：**Ubuntu LTS 或其他现代 Debian/Ubuntu。

    如果你在 Windows 上，**WSL2 是最简单的 VM 风格设置**，并且工具
    兼容性最好。参阅 [Windows](/zh-CN/platforms/windows)、[VPS hosting](/zh-CN/vps)。
    如果你在 VM 中运行 macOS，请参阅 [macOS VM](/zh-CN/install/macos-vm)。

  </Accordion>
</AccordionGroup>

## 什么是 OpenClaw？

<AccordionGroup>
  <Accordion title="用一段话解释，什么是 OpenClaw？">
    OpenClaw 是一个运行在你自己设备上的个人 AI 助手。它会在你已经使用的消息界面上回复你（WhatsApp、Telegram、Slack、Mattermost、Discord、Google Chat、Signal、iMessage、WebChat，以及 QQ Bot 等内置渠道插件），并且在受支持的平台上也能提供语音 + 实时 Canvas。**Gateway 网关**是始终在线的控制平面；这个助手才是产品本身。
  </Accordion>

  <Accordion title="价值主张">
    OpenClaw 并不只是“Claude 的一层封装”。它是一个**本地优先的控制平面**，让你可以在**自己的硬件**上运行一个
    能力强大的助手，并通过你已使用的聊天应用访问它，同时具备
    有状态会话、记忆和工具——而无需把你的工作流控制权交给托管式
    SaaS。

    亮点：

    - **你的设备，你的数据：**在任何你想要的地方运行 Gateway 网关（Mac、Linux、VPS），并将
      工作区 + 会话历史保留在本地。
    - **真实渠道，而不是 web 沙箱：**WhatsApp/Telegram/Slack/Discord/Signal/iMessage 等，
      以及受支持平台上的移动语音和 Canvas。
    - **模型无关：**使用 Anthropic、OpenAI、MiniMax、OpenRouter 等，并支持按智能体路由
      和故障转移。
    - **纯本地选项：**运行本地模型，这样**所有数据都可以保留在你的设备上**（如果你愿意）。
    - **多智能体路由：**按渠道、账户或任务拆分智能体，每个都有自己的
      工作区和默认设置。
    - **开源且可修改：**可自行检查、扩展和自托管，不受厂商锁定。

    文档：[Gateway 网关](/zh-CN/gateway)、[Channels](/zh-CN/channels)、[多智能体](/zh-CN/concepts/multi-agent)、
    [Memory](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="我刚设置好——我应该先做什么？">
    很适合一开始尝试的项目：

    - 构建一个网站（WordPress、Shopify，或一个简单的静态站点）。
    - 制作一个移动应用原型（大纲、页面、API 计划）。
    - 整理文件和文件夹（清理、命名、打标签）。
    - 连接 Gmail 并自动生成摘要或后续跟进。

    它可以处理大型任务，但当你把它们拆分成多个阶段，
    并使用子智能体并行工作时，效果通常最好。

  </Accordion>

  <Accordion title="OpenClaw 最常见的五个日常使用场景是什么？">
    日常收益通常体现在：

    - **个人简报：**总结收件箱、日历和你关心的新闻。
    - **研究与起草：**快速调研、摘要，以及邮件或文档的初稿。
    - **提醒与跟进：**由 cron 或 heartbeat 驱动的提醒和检查清单。
    - **浏览器自动化：**填写表单、收集数据、重复 web 任务。
    - **跨设备协作：**从手机发送任务，让 Gateway 网关在服务器上运行，然后在聊天中把结果发回给你。

  </Accordion>

  <Accordion title="OpenClaw 能帮我做 SaaS 的获客、外联、广告和博客吗？">
    可以用于**研究、资格筛选和起草**。它可以扫描网站、建立候选列表、
    总结潜在客户，并撰写外联或广告文案草稿。

    对于**外联或广告投放**，请始终让人工参与。避免垃圾信息，遵守当地法律和
    平台政策，并在发送前审核所有内容。最安全的模式是让
    OpenClaw 起草，由你批准。

    文档：[Security](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="相比 Claude Code，它在 web 开发方面有什么优势？">
    OpenClaw 是一个**个人助手**和协调层，不是 IDE 替代品。对于仓库内最快的直接编码循环，请使用
    Claude Code 或 Codex。对于
    需要持久记忆、跨设备访问和工具编排的场景，请使用 OpenClaw。

    优势：

    - **跨会话的持久记忆 + 工作区**
    - **多平台访问**（WhatsApp、Telegram、TUI、WebChat）
    - **工具编排**（浏览器、文件、调度、hooks）
    - **始终在线的 Gateway 网关**（可运行在 VPS 上，随处交互）
    - 用于本地浏览器/屏幕/摄像头/exec 的 **Nodes**

    展示页：[https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills 和自动化

<AccordionGroup>
  <Accordion title="如何自定义技能而不让仓库变脏？">
    使用托管覆盖，而不是直接编辑仓库副本。把你的改动放到 `~/.openclaw/skills/<name>/SKILL.md` 中（或通过 `~/.openclaw/openclaw.json` 中的 `skills.load.extraDirs` 添加一个文件夹）。优先级是 `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → 内置 → `skills.load.extraDirs`，因此托管覆盖仍然会优先于内置技能，而无需改动 git。如果你需要让某个技能全局安装但只对部分智能体可见，请将共享副本放在 `~/.openclaw/skills`，并通过 `agents.defaults.skills` 和 `agents.list[].skills` 控制可见性。只有值得上游合并的修改才应该放在仓库里并通过 PR 提交。
  </Accordion>

  <Accordion title="我可以从自定义文件夹加载技能吗？">
    可以。通过 `~/.openclaw/openclaw.json` 中的 `skills.load.extraDirs` 添加额外目录（最低优先级）。默认优先级是 `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → 内置 → `skills.load.extraDirs`。`clawhub` 默认安装到 `./skills`，OpenClaw 会在下一个会话中将其视为 `<workspace>/skills`。如果该技能只应对特定智能体可见，请结合 `agents.defaults.skills` 或 `agents.list[].skills` 一起使用。
  </Accordion>

  <Accordion title="如何为不同任务使用不同模型？">
    当前支持的模式有：

    - **Cron 作业**：隔离作业可为每个作业设置 `model` 覆盖。
    - **子智能体**：将任务路由到使用不同默认模型的独立智能体。
    - **按需切换**：随时使用 `/model` 切换当前会话模型。

    参阅 [Cron jobs](/zh-CN/automation/cron-jobs)、[Multi-Agent Routing](/zh-CN/concepts/multi-agent) 和 [Slash commands](/zh-CN/tools/slash-commands)。

  </Accordion>

  <Accordion title="机器人在执行重任务时会卡住。我该如何卸载这类负载？">
    对于耗时或并行任务，请使用**子智能体**。子智能体在各自独立的会话中运行，
    返回一个摘要，并保持你的主聊天保持响应。

    让你的机器人“为这个任务启动一个子智能体”，或者使用 `/subagents`。
    使用聊天中的 `/status` 查看 Gateway 网关当前在做什么（以及它是否繁忙）。

    令牌提示：长任务和子智能体都会消耗令牌。如果你关心成本，请通过 `agents.defaults.subagents.model` 为子智能体设置一个
    更便宜的模型。

    文档：[子智能体](/zh-CN/tools/subagents)、[后台任务](/zh-CN/automation/tasks)。

  </Accordion>

  <Accordion title="Discord 上绑定到线程的子智能体会话是如何工作的？">
    使用线程绑定。你可以将 Discord 线程绑定到某个子智能体或会话目标，这样该线程中的后续消息就会持续停留在该绑定会话上。

    基本流程：

    - 使用 `sessions_spawn` 并设置 `thread: true` 启动（也可选 `mode: "session"` 用于持久后续跟进）。
    - 或手动使用 `/focus <target>` 进行绑定。
    - 使用 `/agents` 查看绑定状态。
    - 使用 `/session idle <duration|off>` 和 `/session max-age <duration|off>` 控制自动取消聚焦。
    - 使用 `/unfocus` 从线程解绑。

    必需配置：

    - 全局默认值：`session.threadBindings.enabled`、`session.threadBindings.idleHours`、`session.threadBindings.maxAgeHours`。
    - Discord 覆盖：`channels.discord.threadBindings.enabled`、`channels.discord.threadBindings.idleHours`、`channels.discord.threadBindings.maxAgeHours`。
    - 生成时自动绑定：设置 `channels.discord.threadBindings.spawnSubagentSessions: true`。

    文档：[子智能体](/zh-CN/tools/subagents)、[Discord](/zh-CN/channels/discord)、[Configuration Reference](/zh-CN/gateway/configuration-reference)、[Slash commands](/zh-CN/tools/slash-commands)。

  </Accordion>

  <Accordion title="子智能体完成了，但完成更新发到了错误的位置，或者根本没发出来。我该检查什么？">
    先检查解析后的请求者路由：

    - 完成模式的子智能体投递会优先使用任何已绑定的线程或会话路由（如果存在）。
    - 如果完成来源只包含一个渠道，OpenClaw 会回退到请求者会话中存储的路由（`lastChannel` / `lastTo` / `lastAccountId`），以便直接投递仍然可以成功。
    - 如果既没有绑定路由，也没有可用的存储路由，直接投递可能会失败，结果会回退为排队的会话投递，而不是立即发到聊天中。
    - 无效或过期的目标仍可能导致队列回退或最终投递失败。
    - 如果子会话中最后一个可见的助手回复正好是静默令牌 `NO_REPLY` / `no_reply`，或正好是 `ANNOUNCE_SKIP`，OpenClaw 会有意抑制公告，而不是发布更早的陈旧进度。
    - 如果子会话在仅调用工具后超时，公告可能会将其折叠为简短的部分进度摘要，而不是回放原始工具输出。

    调试：

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    文档：[子智能体](/zh-CN/tools/subagents)、[后台任务](/zh-CN/automation/tasks)、[Session Tools](/zh-CN/concepts/session-tool)。

  </Accordion>

  <Accordion title="Cron 或提醒没有触发。我该检查什么？">
    Cron 在 Gateway 网关进程内运行。如果 Gateway 网关没有持续运行，
    定时作业就不会执行。

    检查清单：

    - 确认 cron 已启用（`cron.enabled`），且未设置 `OPENCLAW_SKIP_CRON`。
    - 检查 Gateway 网关是否 24/7 运行（没有休眠/重启）。
    - 验证作业的时区设置（`--tz` 与主机时区）。

    调试：

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    文档：[Cron jobs](/zh-CN/automation/cron-jobs)、[自动化与任务](/zh-CN/automation)。

  </Accordion>

  <Accordion title="Cron 触发了，但没有任何内容发到渠道。为什么？">
    先检查投递模式：

    - `--no-deliver` / `delivery.mode: "none"` 表示不会有外部消息输出。
    - 缺失或无效的公告目标（`channel` / `to`）表示运行器跳过了出站投递。
    - 渠道认证失败（`unauthorized`、`Forbidden`）表示运行器尝试投递了，但被凭据阻止。
    - 静默的隔离结果（仅 `NO_REPLY` / `no_reply`）会被视为有意不可投递，因此运行器也会抑制排队回退投递。

    对于隔离的 cron 作业，运行器负责最终投递。智能体应当
    返回一个纯文本摘要，由运行器发送。`--no-deliver` 会将
    结果保留在内部；它不会让智能体改为直接通过
    message 工具发送。

    调试：

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    文档：[Cron jobs](/zh-CN/automation/cron-jobs)、[后台任务](/zh-CN/automation/tasks)。

  </Accordion>

  <Accordion title="为什么一个隔离的 cron 运行会切换模型或重试一次？">
    通常这属于实时模型切换路径，而不是重复调度。

    隔离 cron 在活动运行抛出 `LiveSessionModelSwitchError` 时，
    可以持久化运行时模型切换并重试。重试会保留切换后的
    provider/model；如果切换还携带了新的认证配置文件覆盖，cron
    也会在重试前一并持久化它。

    相关选择规则：

    - 如果适用，Gmail hook 模型覆盖优先级最高。
    - 然后是每个作业的 `model`。
    - 然后是任何已存储的 cron 会话模型覆盖。
    - 再然后才是正常的智能体/默认模型选择。

    重试循环是有边界的。首次尝试之后最多再进行 2 次切换重试，
    超过后 cron 会中止，而不是无限循环。

    调试：

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    文档：[Cron jobs](/zh-CN/automation/cron-jobs)、[cron CLI](/cli/cron)。

  </Accordion>

  <Accordion title="如何在 Linux 上安装 Skills？">
    使用原生 `openclaw skills` 命令，或将 Skills 放入你的工作区。macOS 的 Skills UI 在 Linux 上不可用。
    可在 [https://clawhub.ai](https://clawhub.ai) 浏览 Skills。

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    原生 `openclaw skills install` 会写入当前工作区的 `skills/`
    目录。只有在你想发布或同步
    自己的 Skills 时，才需要单独安装 `clawhub` CLI。对于跨智能体共享安装，请把技能放到
    `~/.openclaw/skills` 下，并使用 `agents.defaults.skills` 或
    `agents.list[].skills` 来限制哪些智能体可以看到它。

  </Accordion>

  <Accordion title="OpenClaw 可以按计划运行任务，或持续在后台运行吗？">
    可以。使用 Gateway 网关调度器：

    - **Cron 作业**：用于计划性或周期性任务（跨重启持久保存）。
    - **Heartbeat**：用于“主会话”的周期性检查。
    - **隔离作业**：用于自主智能体，它们可以发布摘要或投递到聊天中。

    文档：[Cron jobs](/zh-CN/automation/cron-jobs)、[自动化与任务](/zh-CN/automation)、
    [Heartbeat](/zh-CN/gateway/heartbeat)。

  </Accordion>

  <Accordion title="我能在 Linux 上运行仅限 Apple macOS 的 Skills 吗？">
    不能直接运行。macOS Skills 会受 `metadata.openclaw.os` 和所需二进制文件限制，并且只有当它们在 **Gateway 网关主机**上符合条件时，才会出现在 system prompt 中。在 Linux 上，`darwin` 专属 Skills（如 `apple-notes`、`apple-reminders`、`things-mac`）不会加载，除非你覆盖这些限制。

    你有三种受支持的模式：

    **选项 A - 在 Mac 上运行 Gateway 网关（最简单）。**
    在具备 macOS 二进制文件的机器上运行 Gateway 网关，然后通过 [远程模式](#gateway-端口已经在运行以及远程模式) 或 Tailscale 从 Linux 连接。由于 Gateway 网关主机是 macOS，这些 Skills 会正常加载。

    **选项 B - 使用 macOS 节点（无需 SSH）。**
    在 Linux 上运行 Gateway 网关，配对一个 macOS 节点（菜单栏应用），并在 Mac 上将 **Node Run Commands** 设为 “Always Ask” 或 “Always Allow”。当节点上存在所需二进制文件时，OpenClaw 可以将这些仅限 macOS 的 Skills 视为符合条件。智能体会通过 `nodes` 工具运行这些 Skills。如果你选择 “Always Ask”，在提示中批准 “Always Allow” 会将该命令加入允许列表。

    **选项 C - 通过 SSH 代理 macOS 二进制文件（高级）。**
    保持 Gateway 网关在 Linux 上运行，但让所需 CLI 二进制文件解析为 SSH 包装器，从而在一台 Mac 上执行。然后覆盖该技能以允许 Linux，使其保持可用。

    1. 为该二进制创建一个 SSH 包装器（示例：Apple Notes 的 `memo`）：

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. 将该包装器放到 Linux 主机的 `PATH` 中（例如 `~/bin/memo`）。
    3. 覆盖技能元数据（工作区或 `~/.openclaw/skills`），允许 Linux：

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. 启动一个新会话，以刷新 Skills 快照。

  </Accordion>

  <Accordion title="你们有 Notion 或 HeyGen 集成吗？">
    目前没有内置。

    可选方案：

    - **自定义技能 / 插件：**最适合可靠的 API 访问（Notion/HeyGen 都有 API）。
    - **浏览器自动化：**无需写代码即可使用，但更慢也更脆弱。

    如果你想为每个客户保留上下文（例如代理机构工作流），一种简单模式是：

    - 为每个客户建一个 Notion 页面（上下文 + 偏好 + 当前工作）。
    - 让智能体在会话开始时拉取该页面。

    如果你想要原生集成，可以提交功能请求，或构建一个
    调用这些 API 的技能。

    安装 Skills：

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    原生安装会落到当前工作区的 `skills/` 目录中。若要在多个智能体之间共享 Skills，请将其放到 `~/.openclaw/skills/<name>/SKILL.md`。如果只希望部分智能体看到共享安装，请配置 `agents.defaults.skills` 或 `agents.list[].skills`。有些 Skills 需要通过 Homebrew 安装二进制；在 Linux 上这意味着 Linuxbrew（参见上面的 Homebrew Linux 常见问题条目）。参阅 [Skills](/zh-CN/tools/skills)、[Skills 配置](/zh-CN/tools/skills-config) 和 [ClawHub](/zh-CN/tools/clawhub)。

  </Accordion>

  <Accordion title="如何在 OpenClaw 中使用我已经登录的 Chrome？">
    使用内置的 `user` 浏览器配置，它会通过 Chrome DevTools MCP 进行连接：

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    如果你想用自定义名称，可以创建一个显式 MCP 配置：

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    这条路径是主机本地的。如果 Gateway 网关运行在别处，要么在浏览器所在机器上运行一个节点主机，要么改用远程 CDP。

    `existing-session` / `user` 当前限制：

    - 操作基于 ref，而不是 CSS 选择器
    - 上传需要 `ref` / `inputRef`，并且当前一次只支持一个文件
    - `responsebody`、PDF 导出、下载拦截和批量操作仍然需要托管浏览器或原始 CDP 配置

  </Accordion>
</AccordionGroup>

## 沙箱隔离和记忆

<AccordionGroup>
  <Accordion title="有专门的沙箱隔离文档吗？">
    有。参阅 [沙箱隔离](/zh-CN/gateway/sandboxing)。对于 Docker 特定设置（在 Docker 中运行完整 Gateway 网关或沙箱镜像），参阅 [Docker](/zh-CN/install/docker)。
  </Accordion>

  <Accordion title="Docker 感觉功能受限——我该如何启用完整功能？">
    默认镜像以安全优先方式运行，并以 `node` 用户身份执行，因此它不
    包含系统软件包、Homebrew 或内置浏览器。若要获得更完整的设置：

    - 持久化 `/home/node`，使用 `OPENCLAW_HOME_VOLUME`，这样缓存才能保留。
    - 使用 `OPENCLAW_DOCKER_APT_PACKAGES` 将系统依赖烘焙进镜像。
    - 通过内置 CLI 安装 Playwright 浏览器：
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - 设置 `PLAYWRIGHT_BROWSERS_PATH`，并确保该路径已持久化。

    文档：[Docker](/zh-CN/install/docker)、[Browser](/zh-CN/tools/browser)。

  </Accordion>

  <Accordion title="我能否在使用一个智能体的同时，让私信保持私人、群组变为公开/沙箱隔离？">
    可以——前提是你的私人流量来自**私信**，公开流量来自**群组**。

    使用 `agents.defaults.sandbox.mode: "non-main"`，这样群组/渠道会话（非主会话键）就在 Docker 中运行，而主私信会话则保留在主机上运行。然后通过 `tools.sandbox.tools` 限制沙箱隔离会话中可用的工具。

    设置演练 + 示例配置：[群组：个人私信 + 公开群组](/zh-CN/channels/groups#pattern-personal-dms-public-groups-single-agent)

    关键配置参考：[Gateway 网关配置](/zh-CN/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="如何将主机文件夹绑定到沙箱中？">
    设置 `agents.defaults.sandbox.docker.binds` 为 `["host:path:mode"]`（例如 `"/home/user/src:/src:ro"`）。全局绑定 + 每智能体绑定会合并；当 `scope: "shared"` 时，会忽略每智能体绑定。对任何敏感内容请使用 `:ro`，并记住绑定会绕过沙箱文件系统边界。

    OpenClaw 会根据规范化路径以及通过最深已存在祖先解析出的规范路径，同时验证绑定源。这意味着即使最后一个路径片段尚不存在，父级符号链接逃逸仍会以失败关闭方式被拦截，并且在符号链接解析后仍会应用允许根目录检查。

    示例和安全说明请参阅 [沙箱隔离](/zh-CN/gateway/sandboxing#custom-bind-mounts) 和 [Sandbox vs Tool Policy vs Elevated](/zh-CN/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check)。

  </Accordion>

  <Accordion title="记忆是如何工作的？">
    OpenClaw 记忆其实就是智能体工作区中的 Markdown 文件：

    - 每日笔记在 `memory/YYYY-MM-DD.md`
    - 筛选后的长期笔记在 `MEMORY.md` 中（仅主/私密会话）

    OpenClaw 还会运行一个**静默的预压缩记忆刷写**，提醒模型
    在自动压缩前写入持久笔记。只有在工作区可写时才会执行这一操作
    （只读沙箱会跳过）。参阅 [Memory](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="记忆老是忘事。如何让它记住？">
    让机器人**把这个事实写入记忆**。长期笔记应写入 `MEMORY.md`，
    短期上下文则写入 `memory/YYYY-MM-DD.md`。

    这是我们仍在持续改进的领域。提醒模型去保存记忆会很有帮助；
    它知道该怎么做。如果它仍然频繁遗忘，请确认 Gateway 网关每次运行时使用的是同一个
    工作区。

    文档：[Memory](/zh-CN/concepts/memory)、[智能体工作区](/zh-CN/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="记忆会永久保留吗？它的限制是什么？">
    记忆文件保存在磁盘上，除非你删除，否则会一直保留。限制来自你的
    存储空间，而不是模型。**会话上下文**仍然受模型上下文窗口
    限制，因此长对话可能会压缩或截断。这就是
    为什么有记忆搜索——它只会把相关部分重新拉回上下文。

    文档：[Memory](/zh-CN/concepts/memory)、[Context](/zh-CN/concepts/context)。

  </Accordion>

  <Accordion title="语义记忆搜索需要 OpenAI API key 吗？">
    只有在你使用**OpenAI embeddings** 时才需要。Codex OAuth 仅覆盖聊天/补全，
    并**不**提供 embeddings 访问，因此**使用 Codex 登录（OAuth 或
    Codex CLI 登录）**并不能帮助语义记忆搜索。OpenAI embeddings
    仍然需要真实的 API key（`OPENAI_API_KEY` 或 `models.providers.openai.apiKey`）。

    如果你没有显式设置 provider，OpenClaw 会在能够解析出 API key 时自动选择
    一个 provider（认证配置文件、`models.providers.*.apiKey` 或环境变量）。
    如果能解析出 OpenAI key，则优先 OpenAI；否则如果能解析出 Gemini key，则优先 Gemini；
    然后是 Voyage，再然后是 Mistral。如果没有可用的远程 key，记忆
    搜索会保持禁用，直到你完成配置。如果你已经配置并存在本地模型路径，OpenClaw
    会优先使用 `local`。当你显式设置
    `memorySearch.provider = "ollama"` 时，也支持 Ollama。

    如果你更希望保持本地，请设置 `memorySearch.provider = "local"`（也可选
    `memorySearch.fallback = "none"`）。如果你想使用 Gemini embeddings，请设置
    `memorySearch.provider = "gemini"` 并提供 `GEMINI_API_KEY`（或
    `memorySearch.remote.apiKey`）。我们支持 **OpenAI、Gemini、Voyage、Mistral、Ollama 或 local**
    的 embedding 模型——设置详情请参阅 [Memory](/zh-CN/concepts/memory)。

  </Accordion>
</AccordionGroup>

## 磁盘上的文件位置

<AccordionGroup>
  <Accordion title="OpenClaw 使用的所有数据都保存在本地吗？">
    不是——**OpenClaw 的状态在本地**，但**外部服务仍然能看到你发送给它们的内容**。

    - **默认保存在本地：**会话、记忆文件、配置和工作区保存在 Gateway 网关主机上
      （`~/.openclaw` + 你的工作区目录）。
    - **必须远程发送：**你发送给模型提供商（Anthropic/OpenAI 等）的消息会进入
      它们的 API，聊天平台（WhatsApp/Telegram/Slack 等）也会在
      它们的服务器上存储消息数据。
    - **足迹由你控制：**使用本地模型可以让提示保留在你的机器上，但渠道
      流量仍然会通过对应渠道的服务器。

    相关内容：[智能体工作区](/zh-CN/concepts/agent-workspace)、[Memory](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="OpenClaw 将数据存储在哪里？">
    所有内容都位于 `$OPENCLAW_STATE_DIR`（默认：`~/.openclaw`）下：

    | 路径                                                            | 用途                                                               |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | 主配置（JSON5）                                                     |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | 旧版 OAuth 导入（首次使用时复制到认证配置文件中）                  |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | 认证配置文件（OAuth、API 密钥，以及可选的 `keyRef`/`tokenRef`）     |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef provider 的可选文件型 secret 载荷                  |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | 旧版兼容文件（静态 `api_key` 条目已清理）                          |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | 提供商状态（例如 `whatsapp/<accountId>/creds.json`）               |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | 每个智能体的状态（agentDir + 会话）                                |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | 对话历史和状态（按智能体）                                         |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | 会话元数据（按智能体）                                             |

    旧版单智能体路径：`~/.openclaw/agent/*`（由 `openclaw doctor` 迁移）。

    你的**工作区**（AGENTS.md、记忆文件、Skills 等）是分开的，通过 `agents.defaults.workspace` 配置（默认：`~/.openclaw/workspace`）。

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md 应该放在哪里？">
    这些文件位于**智能体工作区**中，而不是 `~/.openclaw`。

    - **工作区（按智能体）**：`AGENTS.md`、`SOUL.md`、`IDENTITY.md`、`USER.md`、
      `MEMORY.md`（如果没有 `MEMORY.md`，则回退到旧版 `memory.md`），
      `memory/YYYY-MM-DD.md`，以及可选的 `HEARTBEAT.md`。
    - **状态目录（`~/.openclaw`）**：配置、渠道/提供商状态、认证配置文件、会话、日志，
      以及共享 Skills（`~/.openclaw/skills`）。

    默认工作区是 `~/.openclaw/workspace`，可通过以下方式配置：

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    如果机器人在重启后“遗忘”了，请确认 Gateway 网关每次启动时使用的是同一个
    工作区（并记住：远程模式使用的是**gateway host 的**
    工作区，而不是你本地笔记本上的工作区）。

    提示：如果你希望某种行为或偏好能够持久保留，请让机器人**把它写进
    AGENTS.md 或 MEMORY.md**，而不要仅依赖聊天历史。

    参阅 [智能体工作区](/zh-CN/concepts/agent-workspace) 和 [Memory](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="推荐的备份策略">
    将你的**智能体工作区**放入一个**私有** git 仓库，并备份到某个
    私密位置（例如 GitHub 私有仓库）。这样可以保存记忆 + AGENTS/SOUL/USER
    文件，并让你以后恢复助手的“心智”。

    **不要**提交 `~/.openclaw` 下的任何内容（凭据、会话、令牌或加密的 secret 载荷）。
    如果你需要完整恢复，请分别备份工作区和状态目录
    （参见上面的迁移问题）。

    文档：[智能体工作区](/zh-CN/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="如何彻底卸载 OpenClaw？">
    请参阅专门指南：[Uninstall](/zh-CN/install/uninstall)。
  </Accordion>

  <Accordion title="智能体可以在工作区之外工作吗？">
    可以。工作区是**默认 cwd** 和记忆锚点，而不是硬性沙箱。
    相对路径会在工作区内解析，但绝对路径可以访问主机上的其他
    位置，除非启用了沙箱隔离。如果你需要隔离，请使用
    [`agents.defaults.sandbox`](/zh-CN/gateway/sandboxing) 或按智能体设置沙箱。如果你
    希望某个仓库成为默认工作目录，请将该智能体的
    `workspace` 指向该仓库根目录。OpenClaw 仓库只是源码；除非你有意让智能体在其中工作，否则请将
    工作区与其分开。

    示例（将仓库作为默认 cwd）：

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="远程模式：会话存储在哪里？">
    会话状态由**gateway host** 持有。如果你使用远程模式，你需要关心的会话存储位于远程机器上，而不是你本地笔记本。参阅 [Session management](/zh-CN/concepts/session)。
  </Accordion>
</AccordionGroup>

## 配置基础

<AccordionGroup>
  <Accordion title="配置是什么格式？在哪里？">
    OpenClaw 会从 `$OPENCLAW_CONFIG_PATH` 读取可选的 **JSON5** 配置（默认：`~/.openclaw/openclaw.json`）：

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    如果该文件不存在，它会使用相对安全的默认值（包括默认工作区 `~/.openclaw/workspace`）。

  </Accordion>

  <Accordion title='我设置了 gateway.bind: "lan"（或 "tailnet"），现在没有任何监听 / UI 显示 unauthorized'>
    非 loopback 绑定**要求有有效的 gateway auth 路径**。实际意味着：

    - 共享密钥认证：令牌或密码
    - `gateway.auth.mode: "trusted-proxy"`，并且位于正确配置的非 loopback、支持身份感知的反向代理之后

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    注意：

    - `gateway.remote.token` / `.password` **本身不会**启用本地 gateway 认证。
    - 只有在 `gateway.auth.*` 未设置时，本地调用路径才会将 `gateway.remote.*` 用作回退。
    - 对于密码认证，请设置 `gateway.auth.mode: "password"` 并同时设置 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
    - 如果 `gateway.auth.token` / `gateway.auth.password` 通过 SecretRef 显式配置但无法解析，则解析会以失败关闭方式结束（不会被远程回退掩盖）。
    - 共享密钥 Control UI 设置通过 `connect.params.auth.token` 或 `connect.params.auth.password` 进行认证（保存在 app/UI 设置中）。像 Tailscale Serve 或 `trusted-proxy` 这样的带身份模式则使用请求头。避免把共享密钥放进 URL 中。
    - 使用 `gateway.auth.mode: "trusted-proxy"` 时，同主机 loopback 反向代理**仍然不能**满足 trusted-proxy 认证。trusted proxy 必须来自已配置的非 loopback 来源。

  </Accordion>

  <Accordion title="为什么现在 localhost 也需要令牌？">
    OpenClaw 默认强制执行 gateway auth，包括 loopback。在正常默认路径下，这意味着令牌认证：如果没有配置显式认证路径，gateway 启动时会解析为令牌模式并自动生成一个令牌，将其保存到 `gateway.auth.token` 中，因此**本地 WS 客户端也必须认证**。这可以阻止其他本地进程调用 Gateway 网关。

    如果你更喜欢其他认证路径，可以显式选择密码模式（或者，对于非 loopback 且支持身份感知的反向代理，使用 `trusted-proxy`）。如果你**真的**想开放 loopback，请在配置中显式设置 `gateway.auth.mode: "none"`。Doctor 也可以随时为你生成令牌：`openclaw doctor --generate-gateway-token`。

  </Accordion>

  <Accordion title="改完配置后需要重启吗？">
    Gateway 网关会监视配置并支持热重载：

    - `gateway.reload.mode: "hybrid"`（默认）：安全变更热应用，关键变更则重启
    - 也支持 `hot`、`restart`、`off`

  </Accordion>

  <Accordion title="如何关闭 CLI 里的搞笑标语？">
    在配置中设置 `cli.banner.taglineMode`：

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`：隐藏标语文本，但保留 banner 标题/版本行。
    - `default`：始终使用 `All your chats, one OpenClaw.`。
    - `random`：轮换搞笑/季节性标语（默认行为）。
    - 如果你想完全不显示 banner，请设置环境变量 `OPENCLAW_HIDE_BANNER=1`。

  </Accordion>

  <Accordion title="如何启用 web 搜索（以及 web 抓取）？">
    `web_fetch` 无需 API key 即可使用。`web_search` 则取决于你选择的
    provider：

    - Brave、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Perplexity 和 Tavily 等基于 API 的 provider 需要按其常规方式配置 API key。
    - Ollama Web 搜索 不需要 key，但它使用你配置的 Ollama 主机，并要求 `ollama signin`。
    - DuckDuckGo 不需要 key，但它是非官方的基于 HTML 的集成。
    - SearXNG 不需要 key，可自托管；请配置 `SEARXNG_BASE_URL` 或 `plugins.entries.searxng.config.webSearch.baseUrl`。

    **推荐：**运行 `openclaw configure --section web` 并选择一个 provider。
    环境变量替代方案：

    - Brave：`BRAVE_API_KEY`
    - Exa：`EXA_API_KEY`
    - Firecrawl：`FIRECRAWL_API_KEY`
    - Gemini：`GEMINI_API_KEY`
    - Grok：`XAI_API_KEY`
    - Kimi：`KIMI_API_KEY` 或 `MOONSHOT_API_KEY`
    - MiniMax Search：`MINIMAX_CODE_PLAN_KEY`、`MINIMAX_CODING_API_KEY` 或 `MINIMAX_API_KEY`
    - Perplexity：`PERPLEXITY_API_KEY` 或 `OPENROUTER_API_KEY`
    - SearXNG：`SEARXNG_BASE_URL`
    - Tavily：`TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // 可选；省略则自动检测
            },
          },
        },
    }
    ```

    provider 特定的 web 搜索配置现在位于 `plugins.entries.<plugin>.config.webSearch.*` 下。
    旧版 `tools.web.search.*` provider 路径暂时仍会出于兼容性目的被加载，但新配置不应继续使用它们。
    Firecrawl 的 web 抓取回退配置位于 `plugins.entries.firecrawl.config.webFetch.*` 下。

    注意：

    - 如果你使用允许列表，请添加 `web_search`/`web_fetch`/`x_search` 或 `group:web`。
    - `web_fetch` 默认启用（除非显式关闭）。
    - 如果省略 `tools.web.fetch.provider`，OpenClaw 会从可用凭据中自动检测第一个可用的抓取回退 provider。目前内置 provider 是 Firecrawl。
    - 守护进程会从 `~/.openclaw/.env`（或服务环境）中读取环境变量。

    文档：[Web tools](/zh-CN/tools/web)。

  </Accordion>

  <Accordion title="config.apply 把我的配置清空了。如何恢复并避免再次发生？">
    `config.apply` 会替换**整个配置**。如果你发送的是部分对象，其余
    内容都会被删除。

    恢复方法：

    - 从备份恢复（git 或复制的 `~/.openclaw/openclaw.json`）。
    - 如果没有备份，重新运行 `openclaw doctor`，并重新配置渠道/模型。
    - 如果这不是预期行为，请提交 bug，并附上你最后已知的配置或任何备份。
    - 本地编码智能体通常可以根据日志或历史重建一个可工作的配置。

    避免方法：

    - 对小改动使用 `openclaw config set`。
    - 对交互式编辑使用 `openclaw configure`。
    - 当你不确定确切路径或字段形状时，先使用 `config.schema.lookup`；它会返回一个浅层 schema 节点以及其直接子项摘要，以便逐层深入。
    - 对部分 RPC 编辑使用 `config.patch`；仅在你确实要完整替换配置时才使用 `config.apply`。
    - 如果你在智能体运行中使用 owner-only 的 `gateway` 工具，它仍然会拒绝写入 `tools.exec.ask` / `tools.exec.security`（包括会规范化到同一受保护 exec 路径的旧版 `tools.bash.*` 别名）。

    文档：[Config](/cli/config)、[Configure](/cli/configure)、[Doctor](/zh-CN/gateway/doctor)。

  </Accordion>

  <Accordion title="如何运行一个中心化 Gateway 网关，并让不同设备承担专门工作？">
    常见模式是**一个 Gateway 网关**（例如 Raspberry Pi）加上**节点**和**智能体**：

    - **Gateway 网关（中心）：**管理渠道（Signal/WhatsApp）、路由和会话。
    - **节点（设备）：**Mac/iOS/Android 作为外设连接，并暴露本地工具（`system.run`、`canvas`、`camera`）。
    - **智能体（工作节点）：**用于特殊角色的独立“大脑”/工作区（例如“Hetzner 运维”、“个人数据”）。
    - **子智能体：**当你需要并行时，从主智能体中派生后台任务。
    - **TUI：**连接到 Gateway 网关，并切换智能体/会话。

    文档：[Nodes](/zh-CN/nodes)、[远程访问](/zh-CN/gateway/remote)、[Multi-Agent Routing](/zh-CN/concepts/multi-agent)、[子智能体](/zh-CN/tools/subagents)、[TUI](/web/tui)。

  </Accordion>

  <Accordion title="OpenClaw 浏览器可以无头运行吗？">
    可以。这是一个配置项：

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    默认值是 `false`（有头模式）。无头模式更容易触发某些站点的反机器人检查。参阅 [Browser](/zh-CN/tools/browser)。

    无头模式使用**同一个 Chromium 引擎**，适用于大多数自动化任务（表单、点击、抓取、登录）。主要差异：

    - 没有可见的浏览器窗口（如果你需要视觉效果，请使用截图）。
    - 某些网站在无头模式下对自动化更严格（CAPTCHA、反机器人）。
      例如，X/Twitter 经常会阻止无头会话。

  </Accordion>

  <Accordion title="如何使用 Brave 进行浏览器控制？">
    将 `browser.executablePath` 设置为你的 Brave 二进制路径（或任意基于 Chromium 的浏览器），然后重启 Gateway 网关。
    完整配置示例见 [Browser](/zh-CN/tools/browser#use-brave-or-another-chromium-based-browser)。
  </Accordion>
</AccordionGroup>

## 远程 Gateway 网关和节点

<AccordionGroup>
  <Accordion title="命令如何在 Telegram、gateway 和节点之间传播？">
    Telegram 消息由**gateway**处理。gateway 会运行智能体，
    只有在需要节点工具时，才会通过**Gateway WebSocket** 调用节点：

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    节点看不到入站 provider 流量；它们只会接收节点 RPC 调用。

  </Accordion>

  <Accordion title="如果 Gateway 网关托管在远程，我的智能体如何访问我的电脑？">
    简短回答：**把你的电脑配对为一个节点**。Gateway 网关运行在别处，但它可以
    通过 Gateway WebSocket 调用你本地机器上的 `node.*` 工具（屏幕、摄像头、系统）。

    典型设置：

    1. 在始终在线的主机（VPS/家庭服务器）上运行 Gateway 网关。
    2. 将 Gateway 网关主机和你的电脑放在同一个 tailnet 中。
    3. 确保 Gateway WS 可达（tailnet 绑定或 SSH 隧道）。
    4. 在本地打开 macOS 应用，并以**Remote over SSH** 模式（或直接通过 tailnet）
       连接，这样它就能注册为一个节点。
    5. 在 Gateway 网关上批准该节点：

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    不需要单独的 TCP bridge；节点通过 Gateway WebSocket 连接。

    安全提醒：配对一个 macOS 节点意味着该机器上允许 `system.run`。仅
    配对你信任的设备，并查看 [Security](/zh-CN/gateway/security)。

    文档：[Nodes](/zh-CN/nodes)、[Gateway protocol](/zh-CN/gateway/protocol)、[macOS remote mode](/zh-CN/platforms/mac/remote)、[Security](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="Tailscale 已连接，但我收不到任何回复。怎么办？">
    先检查基础项：

    - Gateway 网关是否在运行：`openclaw gateway status`
    - Gateway 网关健康状态：`openclaw status`
    - 渠道健康状态：`openclaw channels status`

    然后验证认证和路由：

    - 如果你使用 Tailscale Serve，请确保 `gateway.auth.allowTailscale` 设置正确。
    - 如果你通过 SSH 隧道连接，请确认本地隧道已建立，并且指向正确端口。
    - 确认你的允许列表（私信或群组）包含你的账户。

    文档：[Tailscale](/zh-CN/gateway/tailscale)、[远程访问](/zh-CN/gateway/remote)、[Channels](/zh-CN/channels)。

  </Accordion>

  <Accordion title="两个 OpenClaw 实例可以互相通信吗（本地 + VPS）？">
    可以。虽然没有内置“机器人对机器人”桥接，但你可以通过几种
    可靠方式实现：

    **最简单：**使用两个机器人都能访问的普通聊天渠道（Telegram/Slack/WhatsApp）。
    让 Bot A 给 Bot B 发送消息，然后让 Bot B 像平时一样回复。

    **CLI 桥接（通用）：**运行一个脚本，通过
    `openclaw agent --message ... --deliver` 调用另一端 Gateway 网关，
    并将消息发往另一个机器人监听的聊天中。如果其中一个机器人在远程 VPS 上，请让你的 CLI
    通过 SSH/Tailscale 指向那个远程 Gateway 网关（参阅 [远程访问](/zh-CN/gateway/remote)）。

    示例模式（在能访问目标 Gateway 网关的机器上运行）：

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    提示：添加一个防护措施，避免两个机器人无限循环回复（例如仅在被提及时回复、渠道
    允许列表，或“不要回复机器人消息”的规则）。

    文档：[远程访问](/zh-CN/gateway/remote)、[Agent CLI](/cli/agent)、[Agent send](/zh-CN/tools/agent-send)。

  </Accordion>

  <Accordion title="多个智能体需要多个独立 VPS 吗？">
    不需要。一个 Gateway 网关可以托管多个智能体，每个智能体都有自己的工作区、模型默认值
    和路由。这是最常见的设置，也比为每个智能体运行
    一个 VPS 更便宜、更简单。

    只有当你需要硬隔离（安全边界）或非常
    不同、且不想共享的配置时，才应使用多个 VPS。否则，保留一个 Gateway 网关，
    并使用多个智能体或子智能体即可。

  </Accordion>

  <Accordion title="相比从 VPS 通过 SSH 连接，在我的个人笔记本上使用节点有什么好处吗？">
    有——节点是从远程 Gateway 网关访问你笔记本的一级方案，而且它们
    不仅仅提供 shell 访问。Gateway 网关运行在 macOS/Linux（Windows 通过 WSL2）上，且
    非常轻量（小型 VPS 或 Raspberry Pi 级设备就够了；4 GB RAM 已经很充足），因此一种常见
    配置是常开主机 + 你的笔记本作为一个节点。

    - **无需入站 SSH。**节点会主动连接到 Gateway WebSocket，并使用设备配对。
    - **更安全的执行控制。**`system.run` 会受该笔记本上的节点允许列表/审批保护。
    - **更多设备工具。**除了 `system.run` 外，节点还暴露 `canvas`、`camera` 和 `screen`。
    - **本地浏览器自动化。**可将 Gateway 网关放在 VPS 上，但通过笔记本上的节点主机在本地运行 Chrome，或通过 Chrome MCP 挂接到主机上的本地 Chrome。

    SSH 适合临时 shell 访问，但对持续性的智能体工作流和
    设备自动化来说，节点更简单。

    文档：[Nodes](/zh-CN/nodes)、[Nodes CLI](/cli/nodes)、[Browser](/zh-CN/tools/browser)。

  </Accordion>

  <Accordion title="节点会运行 gateway 服务吗？">
    不会。除非你有意运行隔离配置文件，否则每台主机上只应运行**一个 gateway**（参见 [Multiple gateways](/zh-CN/gateway/multiple-gateways)）。节点是连接到
    gateway 的外设（iOS/Android 节点，或菜单栏应用中的 macOS “node mode”）。关于无头节点
    主机和 CLI 控制，请参阅 [Node host CLI](/cli/node)。

    更改 `gateway`、`discovery` 和 `canvasHost` 后，必须执行完整重启。

  </Accordion>

  <Accordion title="有 API / RPC 方式应用配置吗？">
    有。

    - `config.schema.lookup`：在写入前检查某个配置子树及其浅层 schema 节点、匹配的 UI 提示和直接子项摘要
    - `config.get`：获取当前快照 + hash
    - `config.patch`：安全的部分更新（大多数 RPC 编辑的首选）；尽可能热重载，必要时重启
    - `config.apply`：校验 + 替换完整配置；尽可能热重载，必要时重启
    - owner-only 的 `gateway` 运行时工具仍然拒绝重写 `tools.exec.ask` / `tools.exec.security`；旧版 `tools.bash.*` 别名会规范化到同一受保护 exec 路径

  </Accordion>

  <Accordion title="首次安装的最小合理配置">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    这会设置你的工作区，并限制哪些人可以触发机器人。

  </Accordion>

  <Accordion title="如何在 VPS 上设置 Tailscale 并从我的 Mac 连接？">
    最少步骤：

    1. **在 VPS 上安装并登录**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **在你的 Mac 上安装并登录**
       - 使用 Tailscale 应用，并登录到同一个 tailnet。
    3. **启用 MagicDNS（推荐）**
       - 在 Tailscale 管理控制台中启用 MagicDNS，这样 VPS 就会有一个稳定名称。
    4. **使用 tailnet 主机名**
       - SSH：`ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS：`ws://your-vps.tailnet-xxxx.ts.net:18789`

    如果你想要 Control UI 而无需 SSH，可在 VPS 上使用 Tailscale Serve：

    ```bash
    openclaw gateway --tailscale serve
    ```

    这会让 gateway 保持绑定在 loopback 上，并通过 Tailscale 暴露 HTTPS。参阅 [Tailscale](/zh-CN/gateway/tailscale)。

  </Accordion>

  <Accordion title="如何将 Mac 节点连接到远程 Gateway 网关（Tailscale Serve）？">
    Serve 会暴露**Gateway Control UI + WS**。节点通过同一个 Gateway WS 端点连接。

    推荐设置：

    1. **确保 VPS 和 Mac 在同一个 tailnet 中**。
    2. **在 Remote 模式下使用 macOS 应用**（SSH 目标可以是 tailnet 主机名）。
       应用会为 Gateway 端口建立隧道，并以节点身份连接。
    3. **在 gateway 上批准节点**：

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    文档：[Gateway protocol](/zh-CN/gateway/protocol)、[Discovery](/zh-CN/gateway/discovery)、[macOS remote mode](/zh-CN/platforms/mac/remote)。

  </Accordion>

  <Accordion title="我应该安装到第二台笔记本上，还是只添加一个节点？">
    如果你只需要在第二台笔记本上使用**本地工具**（屏幕/摄像头/exec），就把它添加为一个
    **节点**。这样可以保持单一 Gateway 网关，避免重复配置。目前本地节点工具
    仅支持 macOS，但我们计划将其扩展到其他操作系统。

    只有当你需要**硬隔离**或两个完全独立的机器人时，才安装第二个 Gateway 网关。

    文档：[Nodes](/zh-CN/nodes)、[Nodes CLI](/cli/nodes)、[Multiple gateways](/zh-CN/gateway/multiple-gateways)。

  </Accordion>
</AccordionGroup>

## 环境变量和 .env 加载

<AccordionGroup>
  <Accordion title="OpenClaw 如何加载环境变量？">
    OpenClaw 会读取父进程中的环境变量（shell、launchd/systemd、CI 等），并额外加载：

    - 当前工作目录中的 `.env`
    - 来自 `~/.openclaw/.env`（即 `$OPENCLAW_STATE_DIR/.env`）的全局回退 `.env`

    两个 `.env` 文件都不会覆盖现有环境变量。

    你也可以在配置中定义内联环境变量（仅在进程环境中缺失时应用）：

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    完整优先级和来源参阅 [/environment](/zh-CN/help/environment)。

  </Accordion>

  <Accordion title="我通过服务启动了 Gateway 网关，结果环境变量不见了。现在怎么办？">
    两种常见修复方法：

    1. 将缺失的 key 放入 `~/.openclaw/.env`，这样即使服务没有继承你的 shell 环境，也能读取到。
    2. 启用 shell 导入（可选的便利功能）：

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    这会运行你的登录 shell，并仅导入缺失的预期键名（绝不覆盖现有值）。对应环境变量：
    `OPENCLAW_LOAD_SHELL_ENV=1`、`OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`。

  </Accordion>

  <Accordion title='我设置了 COPILOT_GITHUB_TOKEN，但 models status 显示 "Shell env: off."。为什么？'>
    `openclaw models status` 报告的是是否启用了**shell 环境导入**。“Shell env: off”
    **不**代表你的环境变量缺失——它只是表示 OpenClaw 不会
    自动加载你的登录 shell。

    如果 Gateway 网关作为服务运行（launchd/systemd），它不会继承你的 shell
    环境。你可以通过以下方式之一修复：

    1. 将令牌放入 `~/.openclaw/.env`：

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. 或启用 shell 导入（`env.shellEnv.enabled: true`）。
    3. 或将其添加到配置中的 `env` 块中（仅在缺失时应用）。

    然后重启 gateway 并重新检查：

    ```bash
    openclaw models status
    ```

    Copilot 令牌从 `COPILOT_GITHUB_TOKEN` 读取（也支持 `GH_TOKEN` / `GITHUB_TOKEN`）。
    参阅 [/concepts/model-providers](/zh-CN/concepts/model-providers) 和 [/environment](/zh-CN/help/environment)。

  </Accordion>
</AccordionGroup>

## 会话和多个聊天

<AccordionGroup>
  <Accordion title="如何开始一段全新的对话？">
    发送 `/new` 或 `/reset` 作为独立消息。参阅 [Session management](/zh-CN/concepts/session)。
  </Accordion>

  <Accordion title="如果我从不发送 /new，会话会自动重置吗？">
    会话可以在 `session.idleMinutes` 之后过期，但这个功能**默认关闭**（默认 **0**）。
    将其设置为正值即可启用空闲过期。启用后，空闲期后的**下一条**
    消息会为该聊天键启动一个新的会话 ID。
    这不会删除转录内容——只是开启一个新会话。

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="有没有办法组建一个 OpenClaw 实例团队（一个 CEO 和许多智能体）？">
    可以，通过**多智能体路由**和**子智能体**。你可以创建一个协调者
    智能体，以及多个具有各自工作区和模型的工作智能体。

    不过，最好把它看作一种**有趣的实验**。它非常消耗令牌，而且通常
    不如使用一个机器人配合不同会话高效。我们通常设想的模式
    是你只与一个机器人对话，用不同会话进行并行工作。这个
    机器人也可以在需要时派生子智能体。

    文档：[多智能体路由](/zh-CN/concepts/multi-agent)、[子智能体](/zh-CN/tools/subagents)、[Agents CLI](/cli/agents)。

  </Accordion>

  <Accordion title="为什么任务中途上下文被截断了？我该如何避免？">
    会话上下文受模型窗口限制。长聊天、大量工具输出或很多
    文件都可能触发压缩或截断。

    有帮助的做法：

    - 让机器人总结当前状态并写入文件。
    - 在长任务前使用 `/compact`，切换话题时使用 `/new`。
    - 将重要上下文保存在工作区中，并让机器人重新读取它。
    - 对于长任务或并行工作，使用子智能体，这样主聊天会更小。
    - 如果经常发生这种情况，请选择上下文窗口更大的模型。

  </Accordion>

  <Accordion title="如何彻底重置 OpenClaw，但保留安装？">
    使用 reset 命令：

    ```bash
    openclaw reset
    ```

    非交互式完整重置：

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    然后重新运行设置：

    ```bash
    openclaw onboard --install-daemon
    ```

    注意：

    - 如果新手引导发现已有配置，也会提供**Reset** 选项。参阅 [新手引导（CLI）](/zh-CN/start/wizard)。
    - 如果你使用了 profiles（`--profile` / `OPENCLAW_PROFILE`），请重置每个状态目录（默认是 `~/.openclaw-<profile>`）。
    - 开发重置：`openclaw gateway --dev --reset`（仅限开发；会清空开发配置 + 凭据 + 会话 + 工作区）。

  </Accordion>

  <Accordion title='我遇到了 "context too large" 错误——该如何重置或压缩？'>
    使用以下任一种：

    - **压缩**（保留对话，但总结旧轮次）：

      ```
      /compact
      ```

      或使用 `/compact <instructions>` 来引导摘要内容。

    - **重置**（为相同聊天键创建新的会话 ID）：

      ```
      /new
      /reset
      ```

    如果问题持续发生：

    - 启用或调整**会话修剪**（`agents.defaults.contextPruning`）以裁剪旧工具输出。
    - 使用上下文窗口更大的模型。

    文档：[Compaction](/zh-CN/concepts/compaction)、[Session pruning](/zh-CN/concepts/session-pruning)、[Session management](/zh-CN/concepts/session)。

  </Accordion>

  <Accordion title='为什么我会看到 "LLM request rejected: messages.content.tool_use.input field required"？'>
    这是一个 provider 校验错误：模型发出了一个缺少必需
    `input` 的 `tool_use` 块。通常表示会话历史已经陈旧或损坏（常见于长线程
    或工具/schema 变更之后）。

    修复方法：使用 `/new`（独立消息）开始一个全新会话。

  </Accordion>

  <Accordion title="为什么我每 30 分钟会收到一次 heartbeat 消息？">
    Heartbeat 默认每 **30m** 运行一次（使用 OAuth 认证时为 **1h**）。可以调整或禁用：

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // 或 "0m" 表示禁用
          },
        },
      },
    }
    ```

    如果 `HEARTBEAT.md` 存在但实际上为空（只有空行和 markdown
    标题如 `# Heading`），OpenClaw 会跳过 heartbeat 运行以节省 API 调用。
    如果该文件不存在，heartbeat 仍会运行，由模型决定该做什么。

    每个智能体的覆盖使用 `agents.list[].heartbeat`。文档：[Heartbeat](/zh-CN/gateway/heartbeat)。

  </Accordion>

  <Accordion title='我需要把“机器人账号”加入 WhatsApp 群组吗？'>
    不需要。OpenClaw 运行在**你自己的账号**上，因此只要你在群里，OpenClaw 就能看到它。
    默认情况下，群组回复会被阻止，直到你允许发送者（`groupPolicy: "allowlist"`）。

    如果你只希望**你自己**能够触发群组回复：

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="如何获取 WhatsApp 群组的 JID？">
    选项 1（最快）：查看日志尾部，并在群里发送一条测试消息：

    ```bash
    openclaw logs --follow --json
    ```

    查找以 `@g.us` 结尾的 `chatId`（或 `from`），例如：
    `1234567890-1234567890@g.us`。

    选项 2（如果已配置/加入允许列表）：从配置中列出群组：

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    文档：[WhatsApp](/zh-CN/channels/whatsapp)、[Directory](/cli/directory)、[Logs](/cli/logs)。

  </Accordion>

  <Accordion title="为什么 OpenClaw 在群组里不回复？">
    两个常见原因：

    - 提及门控已开启（默认）。你必须 @ 提及机器人（或匹配 `mentionPatterns`）。
    - 你配置了 `channels.whatsapp.groups` 但没有包含 `"*"`，且该群未加入允许列表。

    参阅 [Groups](/zh-CN/channels/groups) 和 [Group messages](/zh-CN/channels/group-messages)。

  </Accordion>

  <Accordion title="群组/线程会和私信共享上下文吗？">
    直接聊天默认会折叠到主会话。群组/渠道拥有各自独立的会话键，而 Telegram 话题 / Discord 线程也是独立会话。参阅 [Groups](/zh-CN/channels/groups) 和 [Group messages](/zh-CN/channels/group-messages)。
  </Accordion>

  <Accordion title="我可以创建多少个工作区和智能体？">
    没有硬性限制。几十个（甚至上百个）都没问题，但请注意：

    - **磁盘增长：**会话 + 转录内容保存在 `~/.openclaw/agents/<agentId>/sessions/` 下。
    - **令牌成本：**更多智能体意味着更多并发模型使用。
    - **运维开销：**按智能体划分的认证配置文件、工作区和渠道路由。

    提示：

    - 为每个智能体保留一个**活跃**工作区（`agents.defaults.workspace`）。
    - 如果磁盘增长，修剪旧会话（删除 JSONL 或存储条目）。
    - 使用 `openclaw doctor` 发现零散工作区和 profile 不匹配问题。

  </Accordion>

  <Accordion title="我能同时运行多个机器人或聊天（Slack）吗？应该如何设置？">
    可以。使用**多智能体路由**来运行多个隔离的智能体，并按
    channel/account/peer 路由入站消息。Slack 作为渠道受支持，也可以绑定到特定智能体。

    浏览器访问能力很强，但并不等于“人类能做的都能做”——反机器人机制、CAPTCHA 和 MFA
    仍然可能阻止自动化。若要获得最可靠的浏览器控制，请在主机上使用本地 Chrome MCP，
    或在实际运行浏览器的机器上使用 CDP。

    最佳实践设置：

    - 始终在线的 Gateway 网关主机（VPS/Mac mini）。
    - 每个角色一个智能体（bindings）。
    - 将 Slack 频道绑定到这些智能体。
    - 需要时通过 Chrome MCP 或节点访问本地浏览器。

    文档：[Multi-Agent Routing](/zh-CN/concepts/multi-agent)、[Slack](/zh-CN/channels/slack)、
    [Browser](/zh-CN/tools/browser)、[Nodes](/zh-CN/nodes)。

  </Accordion>
</AccordionGroup>

## 模型：默认值、选择、别名、切换

<AccordionGroup>
  <Accordion title='什么是“默认模型”？'>
    OpenClaw 的默认模型就是你在这里设置的内容：

    ```
    agents.defaults.model.primary
    ```

    模型以 `provider/model` 的形式引用（例如：`openai/gpt-5.4`）。如果你省略 provider，OpenClaw 会先尝试别名，然后尝试精确 model id 的唯一已配置 provider 匹配，最后才会回退到已配置默认 provider 的已弃用兼容路径。如果该 provider 已不再暴露所配置的默认模型，OpenClaw 会回退到第一个已配置的 provider/model，而不是继续暴露一个过期、已移除 provider 的默认值。你仍然应该**显式**设置 `provider/model`。

  </Accordion>

  <Accordion title="你推荐什么模型？">
    **推荐默认值：**使用你 provider 栈中可用的最强最新一代模型。
    **对于启用了工具或处理不可信输入的智能体：**优先考虑模型能力，而不是成本。
    **对于日常/低风险聊天：**使用更便宜的后备模型，并按智能体角色进行路由。

    MiniMax 有自己的文档：[MiniMax](/zh-CN/providers/minimax) 和
    [Local models](/zh-CN/gateway/local-models)。

    经验法则：高风险工作使用你**负担得起的最佳模型**，日常聊天或摘要则使用更便宜的
    模型。你可以按智能体路由模型，并使用子智能体来
    并行长任务（每个子智能体都会消耗令牌）。参阅 [Models](/zh-CN/concepts/models) 和
    [子智能体](/zh-CN/tools/subagents)。

    强烈警告：较弱/过度量化的模型更容易受到提示
    注入和不安全行为影响。参阅 [Security](/zh-CN/gateway/security)。

    更多背景：[Models](/zh-CN/concepts/models)。

  </Accordion>

  <Accordion title="如何在不清空配置的情况下切换模型？">
    使用**模型命令**，或只编辑**模型**字段。避免整份配置替换。

    安全方式：

    - 在聊天中使用 `/model`（快速，按会话）
    - `openclaw models set ...`（只更新模型配置）
    - `openclaw configure --section model`（交互式）
    - 编辑 `~/.openclaw/openclaw.json` 中的 `agents.defaults.model`

    除非你确实打算替换整个配置，否则不要对部分对象使用 `config.apply`。
    对于 RPC 编辑，先用 `config.schema.lookup` 检查，并优先使用 `config.patch`。lookup 载荷会提供规范化路径、浅层 schema 文档/约束，以及直接子项摘要，
    以便进行部分更新。
    如果你确实覆盖了配置，请从备份恢复，或重新运行 `openclaw doctor` 进行修复。

    文档：[Models](/zh-CN/concepts/models)、[Configure](/cli/configure)、[Config](/cli/config)、[Doctor](/zh-CN/gateway/doctor)。

  </Accordion>

  <Accordion title="我可以使用自托管模型（llama.cpp、vLLM、Ollama）吗？">
    可以。Ollama 是使用本地模型最简单的路径。

    最快设置：

    1. 从 `https://ollama.com/download` 安装 Ollama
    2. 拉取一个本地模型，例如 `ollama pull gemma4`
    3. 如果你也想使用云端模型，运行 `ollama signin`
    4. 运行 `openclaw onboard` 并选择 `Ollama`
    5. 选择 `Local` 或 `Cloud + Local`

    注意：

    - `Cloud + Local` 会同时提供云端模型和你的本地 Ollama 模型
    - 像 `kimi-k2.5:cloud` 这样的云端模型不需要本地拉取
    - 如需手动切换，使用 `openclaw models list` 和 `openclaw models set ollama/<model>`

    安全提示：更小或重度量化的模型更容易受到提示
    注入影响。对于任何可以使用工具的机器人，我们强烈建议使用**大模型**。
    如果你仍然想使用小模型，请启用沙箱隔离和严格的工具允许列表。

    文档：[Ollama](/zh-CN/providers/ollama)、[Local models](/zh-CN/gateway/local-models)、
    [Model providers](/zh-CN/concepts/model-providers)、[Security](/zh-CN/gateway/security)、
    [沙箱隔离](/zh-CN/gateway/sandboxing)。

  </Accordion>

  <Accordion title="OpenClaw、Flawd 和 Krill 使用什么模型？">
    - 这些部署可能彼此不同，并且会随时间变化；没有固定的 provider 推荐。
    - 在每个 gateway 上使用 `openclaw models status` 查看当前运行时设置。
    - 对于安全敏感/启用工具的智能体，请使用当前可用的最强最新一代模型。
  </Accordion>

  <Accordion title="如何动态切换模型（无需重启）？">
    将 `/model` 命令作为独立消息发送：

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    这些是内置别名。你也可以通过 `agents.defaults.models` 添加自定义别名。

    你可以使用 `/model`、`/model list` 或 `/model status` 列出可用模型。

    `/model`（以及 `/model list`）会显示一个紧凑的编号选择器。可按编号选择：

    ```
    /model 3
    ```

    你也可以为 provider 强制指定一个特定认证配置文件（按会话）：

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    提示：`/model status` 会显示当前活跃的是哪个智能体、正在使用哪个 `auth-profiles.json` 文件，以及接下来会尝试哪个认证配置文件。
    如果可用，它还会显示已配置的 provider 端点（`baseUrl`）和 API 模式（`api`）。

    **如何取消我用 @profile 固定的配置文件？**

    重新运行 `/model`，但**不要**带 `@profile` 后缀：

    ```
    /model anthropic/claude-opus-4-6
    ```

    如果你想回到默认值，请从 `/model` 中选择它（或发送 `/model <default provider/model>`）。
    使用 `/model status` 确认当前生效的认证配置文件。

  </Accordion>

  <Accordion title="我可以用 GPT 5.2 处理日常任务，用 Codex 5.3 编码吗？">
    可以。将一个设为默认值，并在需要时切换：

    - **快速切换（按会话）：**日常任务用 `/model gpt-5.4`，使用 Codex OAuth 编码时用 `/model openai-codex/gpt-5.4`。
    - **默认值 + 切换：**将 `agents.defaults.model.primary` 设为 `openai/gpt-5.4`，编码时切到 `openai-codex/gpt-5.4`（或者反过来）。
    - **子智能体：**将编码任务路由给默认模型不同的子智能体。

    参阅 [Models](/zh-CN/concepts/models) 和 [Slash commands](/zh-CN/tools/slash-commands)。

  </Accordion>

  <Accordion title="如何为 GPT 5.4 配置 fast mode？">
    可以使用会话开关或配置默认值：

    - **按会话：**当会话使用 `openai/gpt-5.4` 或 `openai-codex/gpt-5.4` 时，发送 `/fast on`。
    - **按模型默认值：**将 `agents.defaults.models["openai/gpt-5.4"].params.fastMode` 设为 `true`。
    - **Codex OAuth 也适用：**如果你也使用 `openai-codex/gpt-5.4`，请为它设置相同标志。

    示例：

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
            "openai-codex/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
          },
        },
      },
    }
    ```

    对于 OpenAI，fast mode 会在受支持的原生 Responses 请求中映射到 `service_tier = "priority"`。会话中的 `/fast` 覆盖优先于配置默认值。

    参阅 [Thinking and fast mode](/zh-CN/tools/thinking) 和 [OpenAI fast mode](/zh-CN/providers/openai#openai-fast-mode)。

  </Accordion>

  <Accordion title='为什么我会看到 "Model ... is not allowed"，然后就没有回复了？'>
    如果设置了 `agents.defaults.models`，它就会成为 `/model` 及任何
    会话覆盖的**允许列表**。选择一个不在该列表中的模型会返回：

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    这个错误会**替代**正常回复返回。修复方法：将该模型加入
    `agents.defaults.models`，移除允许列表，或从 `/model list` 中选择一个模型。

  </Accordion>

  <Accordion title='为什么我会看到 "Unknown model: minimax/MiniMax-M2.7"？'>
    这意味着**provider 没有配置**（未找到 MiniMax provider 配置或认证
    配置文件），因此模型无法解析。

    修复清单：

    1. 升级到当前 OpenClaw 版本（或直接运行源码 `main`），然后重启 gateway。
    2. 确保已配置 MiniMax（通过向导或 JSON），或者环境变量/认证配置文件中
       存在 MiniMax 认证，以便注入匹配的 provider
       （`minimax` 用 `MINIMAX_API_KEY`，`minimax-portal` 用 `MINIMAX_OAUTH_TOKEN` 或已存储的 MiniMax
       OAuth）。
    3. 对你的认证路径使用精确模型 id（区分大小写）：
       `minimax/MiniMax-M2.7` 或 `minimax/MiniMax-M2.7-highspeed` 用于 API key
       设置，或 `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed` 用于 OAuth 设置。
    4. 运行：

       ```bash
       openclaw models list
       ```

       并从列表中选择（或者在聊天中使用 `/model list`）。

    参阅 [MiniMax](/zh-CN/providers/minimax) 和 [Models](/zh-CN/concepts/models)。

  </Accordion>

  <Accordion title="我可以把 MiniMax 设为默认模型，把 OpenAI 留给复杂任务吗？">
    可以。把 **MiniMax 设为默认值**，并在需要时**按会话**切换模型。
    后备机制用于处理**错误**，而不是“高难任务”，因此请使用 `/model` 或单独的智能体。

    **选项 A：按会话切换**

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "minimax/MiniMax-M2.7" },
          models: {
            "minimax/MiniMax-M2.7": { alias: "minimax" },
            "openai/gpt-5.4": { alias: "gpt" },
          },
        },
      },
    }
    ```

    然后：

    ```
    /model gpt
    ```

    **选项 B：分离智能体**

    - 智能体 A 默认：MiniMax
    - 智能体 B 默认：OpenAI
    - 按智能体路由，或使用 `/agent` 切换

    文档：[Models](/zh-CN/concepts/models)、[Multi-Agent Routing](/zh-CN/concepts/multi-agent)、[MiniMax](/zh-CN/providers/minimax)、[OpenAI](/zh-CN/providers/openai)。

  </Accordion>

  <Accordion title="opus / sonnet / gpt 是内置快捷方式吗？">
    是。OpenClaw 自带一些默认简写（仅当模型存在于 `agents.defaults.models` 中时才生效）：

    - `opus` → `anthropic/claude-opus-4-6`
    - `sonnet` → `anthropic/claude-sonnet-4-6`
    - `gpt` → `openai/gpt-5.4`
    - `gpt-mini` → `openai/gpt-5.4-mini`
    - `gpt-nano` → `openai/gpt-5.4-nano`
    - `gemini` → `google/gemini-3.1-pro-preview`
    - `gemini-flash` → `google/gemini-3-flash-preview`
    - `gemini-flash-lite` → `google/gemini-3.1-flash-lite-preview`

    如果你设置了同名自定义别名，则以你的值为准。

  </Accordion>

  <Accordion title="如何定义/覆盖模型快捷方式（aliases）？">
    别名来自 `agents.defaults.models.<modelId>.alias`。示例：

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": { alias: "opus" },
            "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
            "anthropic/claude-haiku-4-5": { alias: "haiku" },
          },
        },
      },
    }
    ```

    然后 `/model sonnet`（或在支持时使用 `/<alias>`）就会解析为该模型 ID。

  </Accordion>

  <Accordion title="如何添加来自 OpenRouter 或 Z.AI 等其他 provider 的模型？">
    OpenRouter（按 token 计费；模型很多）：

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "openrouter/anthropic/claude-sonnet-4-6" },
          models: { "openrouter/anthropic/claude-sonnet-4-6": {} },
        },
      },
      env: { OPENROUTER_API_KEY: "sk-or-..." },
    }
    ```

    Z.AI（GLM 模型）：

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "zai/glm-5" },
          models: { "zai/glm-5": {} },
        },
      },
      env: { ZAI_API_KEY: "..." },
    }
    ```

    如果你引用了某个 provider/model，但缺少所需的 provider key，就会收到运行时认证错误（例如 `No API key found for provider "zai"`）。

    **添加新智能体后出现 No API key found for provider**

    这通常表示**新智能体**的认证存储是空的。认证是按智能体隔离的，
    存储在：

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    修复选项：

    - 运行 `openclaw agents add <id>`，并在向导中配置认证。
    - 或将主智能体 `agentDir` 中的 `auth-profiles.json` 复制到新智能体的 `agentDir` 中。

    **不要**在多个智能体之间复用 `agentDir`；这会导致认证/会话冲突。

  </Accordion>
</AccordionGroup>

## 模型故障转移和“All models failed”

<AccordionGroup>
  <Accordion title="故障转移是如何工作的？">
    故障转移分两个阶段：

    1. 同一 provider 内的**认证配置文件轮换**。
    2. 根据 `agents.defaults.model.fallbacks` 切换到下一个**后备模型**。

    对失败的 profile 会应用冷却时间（指数退避），因此即使 provider 被限流或暂时故障，OpenClaw 也能继续响应。

    速率限制桶不只包含普通的 `429` 响应。OpenClaw
    还会将诸如 `Too many concurrent requests`、
    `ThrottlingException`、`concurrency limit reached`、
    `workers_ai ... quota limit exceeded`、`resource exhausted` 以及周期性
    用量窗口限制（`weekly/monthly limit reached`）等消息视为值得触发故障转移的
    速率限制。

    某些看起来像计费问题的响应并不是 `402`，而某些 HTTP `402`
    响应也会留在那个瞬时错误桶中。如果 provider 在 `401` 或 `403` 上返回
    明确的计费文本，OpenClaw 仍然可以把它归入
    计费通道，但 provider 特定的文本匹配器仍然只作用于它们所属的
    provider（例如 OpenRouter 的 `Key limit exceeded`）。如果某个 `402`
    消息看起来像可重试的用量窗口或
    organization/workspace 花费上限（`daily limit reached, resets tomorrow`、
    `organization spending limit exceeded`），OpenClaw 会将其视为
    `rate_limit`，而不是长期计费禁用。

    上下文溢出错误则不同：如
    `request_too_large`、`input exceeds the maximum number of tokens`、
    `input token count exceeds the maximum number of input tokens`、
    `input is too long for the model` 或 `ollama error: context length
    exceeded` 之类的特征，会留在压缩/重试路径中，而不会推进模型故障转移。

    通用服务器错误文本的范围刻意比“凡是包含
    unknown/error 的都算”更窄。OpenClaw 确实会将 provider 语境下的瞬时形态
    视为值得故障转移的超时/过载信号，例如 Anthropic 的裸 `An unknown error occurred`、OpenRouter 的裸
    `Provider returned error`、停止原因错误如 `Unhandled stop reason:
    error`、带有瞬时服务器文本的 JSON `api_error` 载荷
    （`internal server error`、`unknown error, 520`、`upstream error`、`backend
    error`），以及 provider 繁忙错误如 `ModelNotReadyException`——前提是
    provider 上下文匹配。
    而通用内部回退文本 `LLM request failed with an unknown
    error.` 本身则保持保守，不会单独触发模型故障转移。

  </Accordion>

  <Accordion title='“No credentials found for profile anthropic:default” 是什么意思？'>
    这表示系统尝试使用认证配置文件 ID `anthropic:default`，但在预期的认证存储中找不到对应凭据。

    **修复清单：**

    - **确认认证配置文件的位置**（新路径 vs 旧路径）
      - 当前路径：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
      - 旧路径：`~/.openclaw/agent/*`（由 `openclaw doctor` 迁移）
    - **确认 Gateway 网关已加载你的环境变量**
      - 如果你在 shell 中设置了 `ANTHROPIC_API_KEY`，但 Gateway 网关通过 systemd/launchd 运行，它可能不会继承。请把它放入 `~/.openclaw/.env`，或启用 `env.shellEnv`。
    - **确认你编辑的是正确的智能体**
      - 多智能体设置意味着可能存在多个 `auth-profiles.json` 文件。
    - **做一次模型/认证状态检查**
      - 使用 `openclaw models status` 查看配置的模型，以及 provider 是否已经认证。

    **“No credentials found for profile anthropic” 的修复清单**

    这意味着当前运行被固定到一个 Anthropic 认证配置文件，但 Gateway 网关
    无法在它的认证存储中找到该配置文件。

    - **使用 Claude CLI**
      - 在 gateway host 上运行 `openclaw models auth login --provider anthropic --method cli --set-default`。
    - **如果你想改用 API key**
      - 将 `