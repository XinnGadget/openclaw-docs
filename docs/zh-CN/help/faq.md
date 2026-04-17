---
read_when:
    - 回答常见的设置、安装、新手引导或运行时支持问题
    - 在深入调试之前，对用户报告的问题进行分诊
summary: 关于 OpenClaw 设置、配置和使用的常见问题
title: 常见问题
x-i18n:
    generated_at: "2026-04-12T18:22:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: d2a78d0fea9596625cc2753e6dc8cc42c2379a3a0c91729265eee0261fe53eaa
    source_path: help/faq.md
    workflow: 15
---

# 常见问题

针对真实世界部署（本地开发、VPS、多智能体、OAuth/API 密钥、模型故障切换）的快速解答，以及更深入的故障排除。有关运行时诊断，请参阅 [故障排除](/zh-CN/gateway/troubleshooting)。有关完整配置参考，请参阅 [配置](/zh-CN/gateway/configuration)。

## 如果出了问题，最初的六十秒该做什么

1. **快速状态（第一项检查）**

   ```bash
   openclaw status
   ```

   快速本地摘要：操作系统 + 更新、Gateway 网关/服务可达性、智能体/会话、提供商配置 + 运行时问题（当 Gateway 网关可达时）。

2. **可粘贴的报告（可安全分享）**

   ```bash
   openclaw status --all
   ```

   只读诊断，附带日志尾部（令牌已脱敏）。

3. **守护进程 + 端口状态**

   ```bash
   openclaw gateway status
   ```

   显示监督器运行状态与 RPC 可达性、探测目标 URL，以及服务可能使用了哪个配置。

4. **深度探测**

   ```bash
   openclaw status --deep
   ```

   运行实时 Gateway 网关健康探测，包括在支持时的渠道探测
   （需要可访问的 Gateway 网关）。请参阅 [健康状态](/zh-CN/gateway/health)。

5. **查看最新日志**

   ```bash
   openclaw logs --follow
   ```

   如果 RPC 不可用，则回退到：

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   文件日志与服务日志是分开的；请参阅 [日志记录](/zh-CN/logging) 和 [故障排除](/zh-CN/gateway/troubleshooting)。

6. **运行 Doctor（修复）**

   ```bash
   openclaw doctor
   ```

   修复/迁移配置/状态 + 运行健康检查。请参阅 [Doctor](/zh-CN/gateway/doctor)。

7. **Gateway 网关快照**

   ```bash
   openclaw health --json
   openclaw health --verbose   # 在错误时显示目标 URL + 配置路径
   ```

   向正在运行的 Gateway 网关请求完整快照（仅 WS）。请参阅 [健康状态](/zh-CN/gateway/health)。

## 快速开始和首次运行设置

<AccordionGroup>
  <Accordion title="我卡住了，最快的解决方法是什么">
    使用一个能**看到你的机器**的本地 AI 智能体。这比在 Discord 里提问有效得多，
    因为大多数“我卡住了”的情况其实是**本地配置或环境问题**，
    远程协助者无法直接检查。

    - **Claude Code**： [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**： [https://openai.com/codex/](https://openai.com/codex/)

    这些工具可以读取仓库、运行命令、检查日志，并帮助修复机器级别的
    设置（PATH、服务、权限、认证文件）。通过可修改的（git）安装方式，
    把**完整源码检出**交给它们：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    这会**从 git 检出**安装 OpenClaw，因此智能体可以读取代码 + 文档，
    并针对你正在运行的确切版本进行分析。之后你随时都可以通过重新运行安装程序、
    并去掉 `--install-method git`，切回稳定版。

    提示：让智能体先**规划并监督**修复过程（逐步执行），然后只执行
    必要的命令。这样改动会更小，也更容易审计。

    如果你发现了真实的 bug 或修复，请提交 GitHub issue 或发送 PR：
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    先从这些命令开始（在寻求帮助时分享输出）：

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    它们的作用：

    - `openclaw status`：快速查看 Gateway 网关/智能体健康状态 + 基本配置。
    - `openclaw models status`：检查提供商认证 + 模型可用性。
    - `openclaw doctor`：验证并修复常见的配置/状态问题。

    其他有用的 CLI 检查：`openclaw status --all`、`openclaw logs --follow`、
    `openclaw gateway status`、`openclaw health --verbose`。

    快速调试循环： [如果出了问题，最初的六十秒该做什么](#如果出了问题最初的六十秒该做什么)。
    安装文档： [安装](/zh-CN/install)、[安装器标志](/zh-CN/install/installer)、[更新](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="Heartbeat 一直跳过。跳过原因分别是什么意思？">
    常见的 Heartbeat 跳过原因：

    - `quiet-hours`：不在已配置的活跃时段窗口内
    - `empty-heartbeat-file`：`HEARTBEAT.md` 存在，但只包含空白/仅标题的脚手架内容
    - `no-tasks-due`：`HEARTBEAT.md` 任务模式已启用，但目前没有任何任务间隔到期
    - `alerts-disabled`：所有 Heartbeat 可见性都已禁用（`showOk`、`showAlerts` 和 `useIndicator` 全部关闭）

    在任务模式下，只有在真实的 Heartbeat 运行
    完成后，才会推进到期时间戳。
    被跳过的运行不会将任务标记为已完成。

    文档： [Heartbeat](/zh-CN/gateway/heartbeat)、[自动化与任务](/zh-CN/automation)。

  </Accordion>

  <Accordion title="安装并设置 OpenClaw 的推荐方式">
    仓库推荐从源码运行，并使用新手引导：

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

    如果你还没有全局安装，可以通过 `pnpm openclaw onboard` 运行它。

  </Accordion>

  <Accordion title="完成新手引导后，如何打开仪表板？">
    向导会在新手引导完成后立即用你的浏览器打开一个干净的（不带令牌的）仪表板 URL，并且也会在摘要中打印该链接。请保持该标签页打开；如果它没有自动启动，请在同一台机器上复制/粘贴输出的 URL。
  </Accordion>

  <Accordion title="在 localhost 和远程环境中，我该如何为仪表板认证？">
    **Localhost（同一台机器）：**

    - 打开 `http://127.0.0.1:18789/`。
    - 如果它要求共享密钥认证，请将已配置的令牌或密码粘贴到 Control UI 设置中。
    - 令牌来源：`gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
    - 密码来源：`gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
    - 如果尚未配置共享密钥，请使用 `openclaw doctor --generate-gateway-token` 生成一个令牌。

    **不在 localhost：**

    - **Tailscale Serve**（推荐）：保持绑定到 loopback，运行 `openclaw gateway --tailscale serve`，打开 `https://<magicdns>/`。如果 `gateway.auth.allowTailscale` 为 `true`，身份标头即可满足 Control UI/WebSocket 认证要求（无需粘贴共享密钥，但假设 Gateway 网关主机可信）；除非你明确使用 private-ingress `none` 或 trusted-proxy HTTP 认证，否则 HTTP API 仍然需要共享密钥认证。
      来自同一客户端的错误并发 Serve 认证尝试会在失败认证限流器记录之前被串行化，因此第二次错误重试时就可能已经显示 `retry later`。
    - **Tailnet 绑定**：运行 `openclaw gateway --bind tailnet --token "<token>"`（或配置密码认证），打开 `http://<tailscale-ip>:18789/`，然后在仪表板设置中粘贴匹配的共享密钥。
    - **支持身份感知的反向代理**：将 Gateway 网关保留在非 loopback 的受信任代理后面，配置 `gateway.auth.mode: "trusted-proxy"`，然后打开代理 URL。
    - **SSH 隧道**：`ssh -N -L 18789:127.0.0.1:18789 user@host`，然后打开 `http://127.0.0.1:18789/`。通过隧道时共享密钥认证仍然适用；如果出现提示，请粘贴已配置的令牌或密码。

    有关绑定模式和认证详情，请参阅 [仪表板](/web/dashboard) 和 [Web 界面](/web)。

  </Accordion>

  <Accordion title="为什么聊天审批有两个 exec approval 配置？">
    它们控制的是不同层级：

    - `approvals.exec`：将审批提示转发到聊天目标
    - `channels.<channel>.execApprovals`：让该渠道作为 exec 审批的原生审批客户端

    主机的 exec 策略仍然是真正的审批关卡。聊天配置只控制审批
    提示出现在哪里，以及人们如何作答。

    在大多数设置中，你**不**需要同时使用这两者：

    - 如果聊天本身已经支持命令和回复，那么在同一聊天中使用 `/approve` 就会通过共享路径生效。
    - 如果受支持的原生渠道能够安全推断审批人，那么当 `channels.<channel>.execApprovals.enabled` 未设置或为 `"auto"` 时，OpenClaw 现在会自动启用私信优先的原生审批。
    - 当原生审批卡片/按钮可用时，该原生 UI 是主要路径；只有当工具结果表明聊天审批不可用，或者手动审批是唯一可用路径时，智能体才应附带手动 `/approve` 命令。
    - 仅当提示还需要转发到其他聊天或明确的运维房间时，才使用 `approvals.exec`。
    - 仅当你明确希望将审批提示发回原始房间/主题时，才使用 `channels.<channel>.execApprovals.target: "channel"` 或 `"both"`。
    - 插件审批则是另外一套：它们默认使用同一聊天中的 `/approve`、可选的 `approvals.plugin` 转发，而且只有某些原生渠道会在此基础上继续保留原生插件审批处理。

    简短来说：转发用于路由，原生客户端配置用于提供更丰富的渠道专属 UX。
    请参阅 [Exec 审批](/zh-CN/tools/exec-approvals)。

  </Accordion>

  <Accordion title="我需要什么运行时？">
    需要 Node **>= 22**。推荐使用 `pnpm`。Gateway 网关**不推荐**使用 Bun。
  </Accordion>

  <Accordion title="它能在 Raspberry Pi 上运行吗？">
    可以。Gateway 网关很轻量——文档中写明，个人使用场景下，**512MB-1GB 内存**、**1 个核心**和大约 **500MB**
    磁盘空间就足够，并且还特别说明 **Raspberry Pi 4 可以运行它**。

    如果你想要更多余量（日志、媒体、其他服务），推荐使用 **2GB**，
    但这不是硬性最低要求。

    提示：一个小型 Pi/VPS 就可以托管 Gateway 网关，而你可以在笔记本电脑/手机上配对**节点**，
    以提供本地屏幕/摄像头/canvas 或命令执行。请参阅 [节点](/zh-CN/nodes)。

  </Accordion>

  <Accordion title="Raspberry Pi 安装有什么建议吗？">
    简短来说：可以运行，但要预期会有一些边缘问题。

    - 使用 **64 位**操作系统，并保持 Node >= 22。
    - 优先使用**可修改的（git）安装**，这样你可以查看日志并快速更新。
    - 先不要启用渠道/Skills，然后逐个添加。
    - 如果你遇到奇怪的二进制问题，通常都是 **ARM 兼容性**问题。

    文档： [Linux](/zh-CN/platforms/linux)、[安装](/zh-CN/install)。

  </Accordion>

  <Accordion title="卡在 wake up my friend / 新手引导无法 hatch。现在该怎么办？">
    该界面依赖于 Gateway 网关可访问且已通过认证。TUI 在首次 hatch 时也会自动发送
    “Wake up, my friend!”。如果你看到这一行却**没有回复**，
    并且令牌仍然为 0，说明智能体根本没有运行。

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

    3. 如果仍然卡住，请运行：

    ```bash
    openclaw doctor
    ```

    如果 Gateway 网关是远程的，请确认隧道/Tailscale 连接正常，并且 UI
    指向了正确的 Gateway 网关。请参阅 [远程访问](/zh-CN/gateway/remote)。

  </Accordion>

  <Accordion title="我可以把设置迁移到新机器（Mac mini）上，而不重新做新手引导吗？">
    可以。复制**状态目录**和**工作区**，然后运行一次 Doctor。这样
    你的机器人就能保持“完全一样”（记忆、会话历史、认证和渠道
    状态），前提是你复制了**这两个**位置：

    1. 在新机器上安装 OpenClaw。
    2. 从旧机器复制 `$OPENCLAW_STATE_DIR`（默认：`~/.openclaw`）。
    3. 复制你的工作区（默认：`~/.openclaw/workspace`）。
    4. 运行 `openclaw doctor` 并重启 Gateway 网关服务。

    这会保留配置、认证配置文件、WhatsApp 凭证、会话和记忆。如果你处于
    远程模式，请记住会话存储和工作区归 Gateway 网关主机所有。

    **重要：**如果你只是把工作区提交/推送到 GitHub，你备份的是
    **记忆 + 引导文件**，但**不包括**会话历史或认证信息。这些内容位于
    `~/.openclaw/` 下（例如 `~/.openclaw/agents/<agentId>/sessions/`）。

    相关内容： [迁移](/zh-CN/install/migrating)、[磁盘上的文件位置](#where-things-live-on-disk)、
    [智能体工作区](/zh-CN/concepts/agent-workspace)、[Doctor](/zh-CN/gateway/doctor)、
    [远程模式](/zh-CN/gateway/remote)。

  </Accordion>

  <Accordion title="我在哪里可以看到最新版本有哪些新内容？">
    查看 GitHub 更新日志：
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    最新条目位于顶部。如果顶部部分标记为 **Unreleased**，则下一个带日期的
    部分就是最近发布的版本。条目按 **Highlights**、**Changes** 和
    **Fixes** 分组（如有需要，也会包含文档/其他部分）。

  </Accordion>

  <Accordion title="无法访问 docs.openclaw.ai（SSL 错误）">
    某些 Comcast/Xfinity 连接会被 Xfinity
    Advanced Security 错误地拦截 `docs.openclaw.ai`。请禁用它或将 `docs.openclaw.ai` 加入允许列表，然后重试。
    也请通过这里帮助我们解除拦截： [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status)。

    如果你仍然无法访问该站点，文档在 GitHub 上也有镜像：
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="稳定版和 beta 版的区别">
    **Stable** 和 **beta** 是 **npm dist-tag**，不是独立的代码线：

    - `latest` = 稳定版
    - `beta` = 用于测试的早期构建

    通常，稳定版本会先发布到 **beta**，然后再通过一个明确的
    提升步骤将同一版本移动到 `latest`。维护者也可以在需要时
    直接发布到 `latest`。这就是为什么在提升之后，beta 和稳定版可能会
    指向**同一个版本**。

    查看变更内容：
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    有关安装单行命令以及 beta 和 dev 的区别，请参阅下面的折叠项。

  </Accordion>

  <Accordion title="如何安装 beta 版本？beta 和 dev 有什么区别？">
    **Beta** 是 npm dist-tag `beta`（在提升后可能与 `latest` 相同）。
    **Dev** 是 `main` 的持续更新头部版本（git）；发布时使用 npm dist-tag `dev`。

    单行命令（macOS/Linux）：

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Windows 安装程序（PowerShell）：
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    更多细节： [开发渠道](/zh-CN/install/development-channels) 和 [安装器标志](/zh-CN/install/installer)。

  </Accordion>

  <Accordion title="如何试用最新内容？">
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

    这样你会得到一个可本地编辑的仓库，然后可通过 git 更新。

    如果你更喜欢手动进行干净克隆，请使用：

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    文档： [更新](/cli/update)、[开发渠道](/zh-CN/install/development-channels)、
    [安装](/zh-CN/install)。

  </Accordion>

  <Accordion title="安装和新手引导通常需要多长时间？">
    粗略参考：

    - **安装：**2-5 分钟
    - **新手引导：**5-15 分钟，取决于你配置了多少渠道/模型

    如果卡住了，请参阅 [安装器卡住了](#quick-start-and-first-run-setup)
    以及 [我卡住了](#quick-start-and-first-run-setup) 中的快速调试循环。

  </Accordion>

  <Accordion title="安装器卡住了？如何获得更多反馈？">
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

    Windows（PowerShell）等价方式：

    ```powershell
    # install.ps1 目前还没有专用的 -Verbose 标志。
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    更多选项： [安装器标志](/zh-CN/install/installer)。

  </Accordion>

  <Accordion title="Windows 安装提示 git not found 或 openclaw not recognized">
    两个常见的 Windows 问题：

    **1) npm 错误 spawn git / git not found**

    - 安装 **Git for Windows**，并确保 `git` 在你的 PATH 中。
    - 关闭并重新打开 PowerShell，然后重新运行安装器。

    **2) 安装后 openclaw is not recognized**

    - 你的 npm 全局 bin 目录不在 PATH 中。
    - 检查路径：

      ```powershell
      npm config get prefix
      ```

    - 将该目录添加到你的用户 PATH 中（Windows 上不需要 `\bin` 后缀；在大多数系统上它是 `%AppData%\npm`）。
    - 更新 PATH 后，关闭并重新打开 PowerShell。

    如果你想获得最顺畅的 Windows 设置体验，请使用 **WSL2** 而不是原生 Windows。
    文档： [Windows](/zh-CN/platforms/windows)。

  </Accordion>

  <Accordion title="Windows exec 输出显示乱码中文——我该怎么办？">
    这通常是原生 Windows shell 中控制台代码页不匹配造成的。

    症状：

    - `system.run`/`exec` 输出中的中文显示为乱码
    - 同一条命令在另一个终端配置中显示正常

    PowerShell 中的快速解决方法：

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

    如果你在最新版本 OpenClaw 上仍然能复现此问题，请在这里跟踪/报告：

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="文档没有回答我的问题——我该如何获得更好的答案？">
    使用**可修改的（git）安装**，这样你就可以在本地获得完整源码和文档，然后
    在_该目录中_向你的机器人（或 Claude/Codex）提问，这样它就能读取仓库并给出准确答案。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    更多细节： [安装](/zh-CN/install) 和 [安装器标志](/zh-CN/install/installer)。

  </Accordion>

  <Accordion title="如何在 Linux 上安装 OpenClaw？">
    简短回答：按照 Linux 指南操作，然后运行新手引导。

    - Linux 快速路径 + 服务安装： [Linux](/zh-CN/platforms/linux)。
    - 完整演练： [入门指南](/zh-CN/start/getting-started)。
    - 安装器 + 更新： [安装与更新](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="如何在 VPS 上安装 OpenClaw？">
    任何 Linux VPS 都可以。先在服务器上安装，然后通过 SSH/Tailscale 访问 Gateway 网关。

    指南： [exe.dev](/zh-CN/install/exe-dev)、[Hetzner](/zh-CN/install/hetzner)、[Fly.io](/zh-CN/install/fly)。
    远程访问： [Gateway 网关远程访问](/zh-CN/gateway/remote)。

  </Accordion>

  <Accordion title="云端/VPS 安装指南在哪里？">
    我们维护了一个**托管中心**，包含常见提供商。选择一个并按照对应指南操作：

    - [VPS 托管](/zh-CN/vps)（所有提供商集中在一处）
    - [Fly.io](/zh-CN/install/fly)
    - [Hetzner](/zh-CN/install/hetzner)
    - [exe.dev](/zh-CN/install/exe-dev)

    云端的工作方式是：**Gateway 网关运行在服务器上**，而你通过 Control UI（或 Tailscale/SSH）
    从笔记本电脑/手机访问它。你的状态 + 工作区
    保存在服务器上，因此应将主机视为事实来源并做好备份。

    你可以将**节点**（Mac/iOS/Android/无头）配对到该云端 Gateway 网关，以访问
    本地屏幕/摄像头/canvas，或在保留
    Gateway 网关于云端的同时，在你的笔记本电脑上运行命令。

    中心： [平台](/zh-CN/platforms)。远程访问： [Gateway 网关远程访问](/zh-CN/gateway/remote)。
    节点： [节点](/zh-CN/nodes)、[Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="我可以让 OpenClaw 自己更新自己吗？">
    简短回答：**可以，但不推荐**。更新流程可能会重启
    Gateway 网关（这会中断当前会话），可能需要干净的 git 检出，
    还可能要求确认。更安全的方式：由操作员在 shell 中运行更新。

    使用 CLI：

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    如果你必须从智能体自动化执行：

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    文档： [更新](/cli/update)、[更新中](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="新手引导实际上会做什么？">
    `openclaw onboard` 是推荐的设置路径。在**本地模式**下，它会引导你完成：

    - **模型/认证设置**（提供商 OAuth、API 密钥、Anthropic setup-token，以及 LM Studio 等本地模型选项）
    - **工作区**位置 + 引导文件
    - **Gateway 网关设置**（绑定/端口/认证/tailscale）
    - **渠道**（WhatsApp、Telegram、Discord、Mattermost、Signal、iMessage，以及像 QQ Bot 这样的内置渠道插件）
    - **守护进程安装**（macOS 上为 LaunchAgent；Linux/WSL2 上为 systemd 用户单元）
    - **健康检查**和 **Skills** 选择

    如果你配置的模型未知或缺少认证，它还会发出警告。

  </Accordion>

  <Accordion title="运行这个需要 Claude 或 OpenAI 订阅吗？">
    不需要。你可以通过 **API 密钥**（Anthropic/OpenAI/其他）运行 OpenClaw，或者使用
    **纯本地模型**，这样你的数据就会保留在你的设备上。订阅（Claude
    Pro/Max 或 OpenAI Codex）只是这些提供商的可选认证方式。

    对于 OpenClaw 中的 Anthropic，实际上的区分是：

    - **Anthropic API key**：常规 Anthropic API 计费
    - **OpenClaw 中的 Claude CLI / Claude 订阅认证**：Anthropic 员工
      告诉我们这种用法再次被允许，OpenClaw 目前将 `claude -p`
      的使用视为此集成的受支持方式，除非 Anthropic 发布新的
      政策

    对于长期运行的 Gateway 网关主机来说，Anthropic API 密钥仍然是更
    可预测的设置方式。OpenAI Codex OAuth 已明确支持
    OpenClaw 这类外部工具。

    OpenClaw 还支持其他托管式订阅选项，包括
    **Qwen Cloud Coding Plan**、**MiniMax Coding Plan** 和
    **Z.AI / GLM Coding Plan**。

    文档： [Anthropic](/zh-CN/providers/anthropic)、[OpenAI](/zh-CN/providers/openai)、
    [Qwen Cloud](/zh-CN/providers/qwen)、
    [MiniMax](/zh-CN/providers/minimax)、[GLM Models](/zh-CN/providers/glm)、
    [本地模型](/zh-CN/gateway/local-models)、[模型](/zh-CN/concepts/models)。

  </Accordion>

  <Accordion title="我可以在没有 API 密钥的情况下使用 Claude Max 订阅吗？">
    可以。

    Anthropic 员工告诉我们，OpenClaw 风格的 Claude CLI 用法再次被允许，因此
    除非 Anthropic 发布新的政策，否则 OpenClaw 会将 Claude 订阅认证和 `claude -p` 的使用视为此集成中受支持的方式。如果你想要
    最可预测的服务器端设置，建议改用 Anthropic API 密钥。

  </Accordion>

  <Accordion title="你们支持 Claude 订阅认证（Claude Pro 或 Max）吗？">
    支持。

    Anthropic 员工告诉我们，这种用法再次被允许，因此除非 Anthropic 发布新的政策，否则 OpenClaw 会将
    Claude CLI 复用和 `claude -p` 的使用视为此集成中受支持的方式。

    Anthropic setup-token 仍然是 OpenClaw 支持的令牌路径，但在可用时，OpenClaw 现在更倾向于优先使用 Claude CLI 复用和 `claude -p`。
    对于生产环境或多用户工作负载，Anthropic API 密钥认证仍然是
    更安全、更可预测的选择。如果你想在 OpenClaw 中使用其他托管式订阅
    选项，请参阅 [OpenAI](/zh-CN/providers/openai)、[Qwen / Model
    Cloud](/zh-CN/providers/qwen)、[MiniMax](/zh-CN/providers/minimax) 和 [GLM
    Models](/zh-CN/providers/glm)。

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="为什么我会看到来自 Anthropic 的 HTTP 429 rate_limit_error？">
这意味着你当前时间窗口内的 **Anthropic 配额/速率限制** 已耗尽。如果你
使用 **Claude CLI**，请等待窗口重置或升级你的套餐。如果你
使用 **Anthropic API 密钥**，请检查 Anthropic Console
中的用量/计费情况，并根据需要提高限额。

    如果消息具体是：
    `Extra usage is required for long context requests`，则表示该请求正试图使用
    Anthropic 的 1M 上下文 beta（`context1m: true`）。这只有在你的
    凭证符合长上下文计费条件时才可用（API 密钥计费，或启用了 Extra Usage 的
    OpenClaw Claude 登录路径）。

    提示：设置一个**回退模型**，这样 OpenClaw 就能在某个提供商受到速率限制时继续回复。
    请参阅 [模型](/cli/models)、[OAuth](/zh-CN/concepts/oauth) 和
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/zh-CN/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context)。

  </Accordion>

  <Accordion title="支持 AWS Bedrock 吗？">
    支持。OpenClaw 内置了 **Amazon Bedrock（Converse）** 提供商。当存在 AWS 环境标记时，OpenClaw 可以自动发现支持流式传输/文本的 Bedrock 目录，并将其作为隐式 `amazon-bedrock` 提供商合并；否则你也可以显式启用 `plugins.entries.amazon-bedrock.config.discovery.enabled`，或手动添加提供商条目。请参阅 [Amazon Bedrock](/zh-CN/providers/bedrock) 和 [模型提供商](/zh-CN/providers/models)。如果你更偏好托管式密钥流程，在 Bedrock 前面使用 OpenAI 兼容代理仍然是可行的选择。
  </Accordion>

  <Accordion title="Codex 认证是如何工作的？">
    OpenClaw 通过 OAuth（ChatGPT 登录）支持 **OpenAI Code（Codex）**。新手引导可以运行 OAuth 流程，并会在合适时将默认模型设置为 `openai-codex/gpt-5.4`。请参阅 [模型提供商](/zh-CN/concepts/model-providers) 和 [设置向导（CLI）](/zh-CN/start/wizard)。
  </Accordion>

  <Accordion title="为什么 ChatGPT GPT-5.4 不会在 OpenClaw 中解锁 openai/gpt-5.4？">
    OpenClaw 将这两条路径分开处理：

    - `openai-codex/gpt-5.4` = ChatGPT/Codex OAuth
    - `openai/gpt-5.4` = 直接 OpenAI Platform API

    在 OpenClaw 中，ChatGPT/Codex 登录绑定到 `openai-codex/*` 路径，
    而不是直接的 `openai/*` 路径。如果你想在 OpenClaw 中使用直接 API 路径，
    请设置 `OPENAI_API_KEY`（或等效的 OpenAI 提供商配置）。
    如果你想在 OpenClaw 中使用 ChatGPT/Codex 登录，请使用 `openai-codex/*`。

  </Accordion>

  <Accordion title="为什么 Codex OAuth 限额可能与 ChatGPT 网页版不同？">
    `openai-codex/*` 使用 Codex OAuth 路径，而它的可用配额窗口由
    OpenAI 管理，并取决于套餐。实际上，即使两者都绑定到同一个账户，
    这些限制也可能与 ChatGPT 网站/应用中的体验不同。

    OpenClaw 可以在
    `openclaw models status` 中显示当前可见的提供商用量/配额窗口，但不会自行推断或规范化 ChatGPT 网页版
    权益为直接 API 访问。如果你想要直接的 OpenAI Platform
    计费/限额路径，请配合 API 密钥使用 `openai/*`。

  </Accordion>

  <Accordion title="你们支持 OpenAI 订阅认证（Codex OAuth）吗？">
    支持。OpenClaw 完全支持 **OpenAI Code（Codex）订阅 OAuth**。
    OpenAI 明确允许在 OpenClaw 这样的外部工具/工作流中
    使用订阅 OAuth。新手引导可以为你运行 OAuth 流程。

    请参阅 [OAuth](/zh-CN/concepts/oauth)、[模型提供商](/zh-CN/concepts/model-providers) 和 [设置向导（CLI）](/zh-CN/start/wizard)。

  </Accordion>

  <Accordion title="如何设置 Gemini CLI OAuth？">
    Gemini CLI 使用的是**插件认证流程**，而不是在 `openclaw.json` 中配置 client id 或 secret。

    步骤：

    1. 在本地安装 Gemini CLI，确保 `gemini` 已加入 `PATH`
       - Homebrew：`brew install gemini-cli`
       - npm：`npm install -g @google/gemini-cli`
    2. 启用插件：`openclaw plugins enable google`
    3. 登录：`openclaw models auth login --provider google-gemini-cli --set-default`
    4. 登录后的默认模型：`google-gemini-cli/gemini-3-flash-preview`
    5. 如果请求失败，请在 Gateway 网关主机上设置 `GOOGLE_CLOUD_PROJECT` 或 `GOOGLE_CLOUD_PROJECT_ID`

    这会将 OAuth 令牌存储到 Gateway 网关主机上的认证配置文件中。详情请参阅： [模型提供商](/zh-CN/concepts/model-providers)。

  </Accordion>

  <Accordion title="本地模型适合日常闲聊吗？">
    通常不适合。OpenClaw 需要大上下文 + 强安全性；小模型会截断并泄漏。如果你确实需要，请在本地运行你能承载的**最大**模型构建（LM Studio），并参阅 [/gateway/local-models](/zh-CN/gateway/local-models)。更小/量化后的模型会增加提示注入风险——请参阅 [安全性](/zh-CN/gateway/security)。
  </Accordion>

  <Accordion title="如何让托管模型流量固定在特定区域？">
    选择固定区域的端点。OpenRouter 为 MiniMax、Kimi 和 GLM 提供美国托管选项；选择美国托管变体即可让数据保留在该区域内。你仍然可以通过使用 `models.mode: "merge"` 将 Anthropic/OpenAI 一起列出，这样在遵守你所选区域提供商限制的同时，回退模型也仍然可用。
  </Accordion>

  <Accordion title="安装这个必须买一台 Mac mini 吗？">
    不需要。OpenClaw 可运行在 macOS 或 Linux 上（Windows 通过 WSL2）。Mac mini 是可选的——有些人
    会买一台作为常开主机，但小型 VPS、家用服务器或 Raspberry Pi 级别的设备也可以。

    只有在你需要**仅限 macOS 的工具**时才必须使用 Mac。对于 iMessage，请使用 [BlueBubbles](/zh-CN/channels/bluebubbles)（推荐）——BlueBubbles 服务器可以运行在任意 Mac 上，而 Gateway 网关可以运行在 Linux 或其他环境中。如果你需要其他仅限 macOS 的工具，请在 Mac 上运行 Gateway 网关，或配对一个 macOS 节点。

    文档： [BlueBubbles](/zh-CN/channels/bluebubbles)、[节点](/zh-CN/nodes)、[Mac 远程模式](/zh-CN/platforms/mac/remote)。

  </Accordion>

  <Accordion title="要支持 iMessage，我需要 Mac mini 吗？">
    你需要**某种已登录 Messages 的 macOS 设备**。它**不一定**必须是 Mac mini——
    任何 Mac 都可以。对于 iMessage，**请使用 [BlueBubbles](/zh-CN/channels/bluebubbles)**（推荐）——BlueBubbles 服务器运行在 macOS 上，而 Gateway 网关可以运行在 Linux 或其他地方。

    常见设置：

    - 在 Linux/VPS 上运行 Gateway 网关，并在任意一台已登录 Messages 的 Mac 上运行 BlueBubbles 服务器。
    - 如果你想要最简单的单机设置，也可以把所有内容都运行在那台 Mac 上。

    文档： [BlueBubbles](/zh-CN/channels/bluebubbles)、[节点](/zh-CN/nodes)、
    [Mac 远程模式](/zh-CN/platforms/mac/remote)。

  </Accordion>

  <Accordion title="如果我买一台 Mac mini 来运行 OpenClaw，我可以把它连接到我的 MacBook Pro 吗？">
    可以。**Mac mini 可以运行 Gateway 网关**，而你的 MacBook Pro 可以作为
    **节点**（配套设备）连接。节点不运行 Gateway 网关——它们提供额外
    能力，比如该设备上的屏幕/摄像头/canvas 和 `system.run`。

    常见模式：

    - Gateway 网关运行在 Mac mini 上（常开）。
    - MacBook Pro 运行 macOS 应用或节点主机，并与 Gateway 网关配对。
    - 使用 `openclaw nodes status` / `openclaw nodes list` 查看它。

    文档： [节点](/zh-CN/nodes)、[Nodes CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="我可以使用 Bun 吗？">
    **不推荐**使用 Bun。我们观察到运行时 bug，尤其是在 WhatsApp 和 Telegram 上。
    想要稳定的 Gateway 网关，请使用 **Node**。

    如果你仍然想尝试 Bun，请在非生产 Gateway 网关上进行，
    并且不要接入 WhatsApp/Telegram。

  </Accordion>

  <Accordion title="Telegram：allowFrom 里应该填什么？">
    `channels.telegram.allowFrom` 应填写**真人发送者的 Telegram 用户 ID**（数字），不是机器人用户名。

    新手引导接受 `@username` 输入并将其解析为数字 ID，但 OpenClaw 授权只使用数字 ID。

    更安全的方式（无需第三方 bot）：

    - 给你的 bot 发私信，然后运行 `openclaw logs --follow` 并读取 `from.id`。

    官方 Bot API：

    - 给你的 bot 发私信，然后调用 `https://api.telegram.org/bot<bot_token>/getUpdates` 并读取 `message.from.id`。

    第三方方式（隐私性较差）：

    - 给 `@userinfobot` 或 `@getidsbot` 发私信。

    请参阅 [/channels/telegram](/zh-CN/channels/telegram#access-control-and-activation)。

  </Accordion>

  <Accordion title="多个人可以用同一个 WhatsApp 号码连接不同的 OpenClaw 实例吗？">
    可以，通过**多智能体路由**实现。将每个发送者的 WhatsApp **私信**（peer `kind: "direct"`，发送者 E.164 如 `+15551234567`）绑定到不同的 `agentId`，这样每个人都会有自己的工作区和会话存储。回复仍然来自**同一个 WhatsApp 账号**，而私信访问控制（`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`）对于该 WhatsApp 账号是全局的。请参阅 [多智能体路由](/zh-CN/concepts/multi-agent) 和 [WhatsApp](/zh-CN/channels/whatsapp)。
  </Accordion>

  <Accordion title='我可以同时运行一个“快速聊天”智能体和一个“用于编码的 Opus”智能体吗？'>
    可以。使用多智能体路由：为每个智能体设置各自的默认模型，然后将入站路由（提供商账号或特定 peer）绑定到各个智能体。示例配置见 [多智能体路由](/zh-CN/concepts/multi-agent)。另请参阅 [模型](/zh-CN/concepts/models) 和 [配置](/zh-CN/gateway/configuration)。
  </Accordion>

  <Accordion title="Homebrew 能在 Linux 上运行吗？">
    可以。Homebrew 支持 Linux（Linuxbrew）。快速设置：

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    如果你通过 systemd 运行 OpenClaw，请确保服务的 PATH 包含 `/home/linuxbrew/.linuxbrew/bin`（或你的 brew 前缀），这样 `brew` 安装的工具才能在非登录 shell 中被正确解析。
    最近的构建也会在 Linux systemd 服务上预置常见用户 bin 目录（例如 `~/.local/bin`、`~/.npm-global/bin`、`~/.local/share/pnpm`、`~/.bun/bin`），并在已设置时识别 `PNPM_HOME`、`NPM_CONFIG_PREFIX`、`BUN_INSTALL`、`VOLTA_HOME`、`ASDF_DATA_DIR`、`NVM_DIR` 和 `FNM_DIR`。

  </Accordion>

  <Accordion title="可修改的 git 安装和 npm install 有什么区别？">
    - **可修改的（git）安装：**完整源码检出，可编辑，最适合贡献者。
      你会在本地运行构建，也可以修改代码/文档。
    - **npm install：**全局 CLI 安装，不包含仓库，最适合“只想跑起来”。
      更新来自 npm dist-tag。

    文档： [入门指南](/zh-CN/start/getting-started)、[更新中](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="我之后可以在 npm 安装和 git 安装之间切换吗？">
    可以。安装另一种形式后，再运行 Doctor，让 Gateway 网关服务指向新的入口点。
    这**不会删除你的数据**——它只会更改 OpenClaw 的代码安装方式。你的状态
    （`~/.openclaw`）和工作区（`~/.openclaw/workspace`）都会保持不变。

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

    Doctor 会检测 Gateway 网关服务入口点不匹配的问题，并提供将服务配置重写为与当前安装匹配的选项（在自动化中使用 `--repair`）。

    备份建议：请参阅 [备份策略](#where-things-live-on-disk)。

  </Accordion>

  <Accordion title="我应该把 Gateway 网关运行在笔记本电脑上还是 VPS 上？">
    简短回答：**如果你想要 24/7 的可靠性，请使用 VPS**。如果你希望
    摩擦最小，并且可以接受休眠/重启，那就在本地运行。

    **笔记本电脑（本地 Gateway 网关）**

    - **优点：**无服务器成本，可直接访问本地文件，有可见的浏览器窗口。
    - **缺点：**休眠/网络中断 = 断连，操作系统更新/重启会中断，必须保持唤醒。

    **VPS / 云端**

    - **优点：**始终在线，网络稳定，没有笔记本休眠问题，更容易长期保持运行。
    - **缺点：**通常以无头模式运行（使用截图），只能远程访问文件，更新时必须通过 SSH。

    **OpenClaw 特别说明：**WhatsApp/Telegram/Slack/Mattermost/Discord 在 VPS 上都能正常运行。真正的取舍只有**无头浏览器**与可见窗口之间的差别。请参阅 [浏览器](/zh-CN/tools/browser)。

    **推荐默认选择：**如果你之前遇到过 Gateway 网关断连，建议使用 VPS。本地运行非常适合你正在积极使用 Mac，并且想要本地文件访问或带可见浏览器的 UI 自动化时。

  </Accordion>

  <Accordion title="在专用机器上运行 OpenClaw 有多重要？">
    不是必须，但**为了可靠性和隔离性，推荐这样做**。

    - **专用主机（VPS/Mac mini/Pi）：**始终在线，休眠/重启中断更少，权限更干净，更容易持续运行。
    - **共享笔记本/台式机：**用于测试和主动使用完全没问题，但机器休眠或更新时预计会出现暂停。

    如果你想兼顾两者优势，可以将 Gateway 网关放在专用主机上，再把笔记本电脑作为**节点**配对，用于本地屏幕/摄像头/exec 工具。请参阅 [节点](/zh-CN/nodes)。
    有关安全指南，请阅读 [安全性](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="最低 VPS 要求和推荐操作系统是什么？">
    OpenClaw 很轻量。对于基础 Gateway 网关 + 一个聊天渠道：

    - **绝对最低配置：**1 vCPU、1GB RAM、约 500MB 磁盘。
    - **推荐配置：**1-2 vCPU、2GB RAM 或更多余量（日志、媒体、多个渠道）。Node 工具和浏览器自动化可能比较耗费资源。

    操作系统：使用 **Ubuntu LTS**（或任何现代 Debian/Ubuntu）。Linux 安装路径在这些系统上测试最充分。

    文档： [Linux](/zh-CN/platforms/linux)、[VPS 托管](/zh-CN/vps)。

  </Accordion>

  <Accordion title="我可以在虚拟机中运行 OpenClaw 吗？需要什么配置？">
    可以。把虚拟机当作 VPS 看待即可：它需要始终在线、可访问，并且有足够的
    RAM 来运行 Gateway 网关以及你启用的各个渠道。

    基础建议：

    - **绝对最低配置：**1 vCPU、1GB RAM。
    - **推荐配置：**如果你运行多个渠道、浏览器自动化或媒体工具，建议使用 2GB RAM 或更多。
    - **操作系统：**Ubuntu LTS 或其他现代 Debian/Ubuntu。

    如果你使用的是 Windows，**WSL2 是最容易上手的虚拟机式配置**，并且具有最好的工具
    兼容性。请参阅 [Windows](/zh-CN/platforms/windows)、[VPS 托管](/zh-CN/vps)。
    如果你在虚拟机中运行 macOS，请参阅 [macOS VM](/zh-CN/install/macos-vm)。

  </Accordion>
</AccordionGroup>

## OpenClaw 是什么？

<AccordionGroup>
  <Accordion title="用一段话介绍 OpenClaw 是什么？">
    OpenClaw 是一个运行在你自己设备上的个人 AI 助手。它会在你已经使用的消息界面上回复（WhatsApp、Telegram、Slack、Mattermost、Discord、Google Chat、Signal、iMessage、WebChat，以及 QQ Bot 等内置渠道插件），并且在受支持的平台上还可以提供语音 + 实时 Canvas。**Gateway 网关**是始终在线的控制平面；而这个助手本身才是产品。
  </Accordion>

  <Accordion title="价值主张">
    OpenClaw 不是“又一个 Claude 包装器”。它是一个**本地优先的控制平面**，让你能够在**自己的硬件**上运行一个
    功能强大的助手，并通过你已经在使用的聊天应用访问它，同时拥有
    有状态的会话、记忆和工具——而不需要把你的工作流控制权交给托管式
    SaaS。

    亮点：

    - **你的设备，你的数据：**你可以在任意位置运行 Gateway 网关（Mac、Linux、VPS），并保持
      工作区 + 会话历史保存在本地。
    - **真实渠道，而不是 Web 沙箱：**WhatsApp/Telegram/Slack/Discord/Signal/iMessage 等，
      以及在受支持平台上的移动语音和 Canvas。
    - **模型无关：**使用 Anthropic、OpenAI、MiniMax、OpenRouter 等，并支持按智能体进行路由
      和故障切换。
    - **纯本地选项：**运行本地模型，这样如果你愿意，**所有数据都可以保留在你的设备上**。
    - **多智能体路由：**按渠道、账号或任务划分独立智能体，每个都有自己的
      工作区和默认设置。
    - **开源且可修改：**可以检查、扩展和自行托管，不受供应商锁定。

    文档： [Gateway 网关](/zh-CN/gateway)、[渠道](/zh-CN/channels)、[多智能体](/zh-CN/concepts/multi-agent)、
    [记忆](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="我刚刚完成设置——接下来先做什么？">
    很好的首批项目包括：

    - 构建一个网站（WordPress、Shopify，或简单的静态站点）。
    - 制作一个移动应用原型（大纲、界面、API 计划）。
    - 整理文件和文件夹（清理、命名、打标签）。
    - 连接 Gmail 并自动生成摘要或后续跟进。

    它可以处理大型任务，但当你把任务拆分为多个阶段，并
    使用子智能体并行工作时，效果最好。

  </Accordion>

  <Accordion title="OpenClaw 最常见的五个日常使用场景是什么？">
    日常收益通常体现在：

    - **个人简报：**汇总你的收件箱、日历和你关心的新闻。
    - **研究与起草：**快速研究、摘要，以及邮件或文档的初稿。
    - **提醒与跟进：**由 cron 或 Heartbeat 驱动的提醒和检查清单。
    - **浏览器自动化：**填写表单、收集数据，以及重复性的 Web 任务。
    - **跨设备协作：**从手机发送任务，让 Gateway 网关在服务器上运行，再把结果返回到聊天中。

  </Accordion>

  <Accordion title="OpenClaw 能帮我做 SaaS 的获客、外联、广告和博客吗？">
    对于**研究、资格筛选和起草**，可以。它可以扫描网站、建立候选名单、
    汇总潜在客户信息，并撰写外联或广告文案草稿。

    对于**外联或广告投放**，请保持人工参与。避免垃圾信息，遵守当地法律和
    平台政策，并在发送前审核所有内容。最安全的模式是让
    OpenClaw 先起草，再由你审批。

    文档： [安全性](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="与 Claude Code 相比，它在 Web 开发方面有什么优势？">
    OpenClaw 是一个**个人助手**和协调层，而不是 IDE 替代品。要在仓库内获得最快的直接编码循环，
    请使用 Claude Code 或 Codex。需要持久记忆、跨设备访问和工具编排时，请使用 OpenClaw。

    优势：

    - **跨会话的持久记忆 + 工作区**
    - **多平台访问**（WhatsApp、Telegram、TUI、WebChat）
    - **工具编排**（浏览器、文件、调度、hooks）
    - **始终在线的 Gateway 网关**（运行在 VPS 上，可随时随地交互）
    - 用于本地浏览器/屏幕/摄像头/exec 的**节点**

    展示： [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills 和自动化

<AccordionGroup>
  <Accordion title="如何自定义 Skills，同时不让仓库变脏？">
    使用托管覆盖，而不是直接编辑仓库副本。将你的修改放到 `~/.openclaw/skills/<name>/SKILL.md` 中（或者通过 `~/.openclaw/openclaw.json` 里的 `skills.load.extraDirs` 添加一个文件夹）。优先级顺序是 `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → 内置 → `skills.load.extraDirs`，因此托管覆盖仍然会优先于内置 Skills，而无需改动 git。如果你需要让某个 Skill 全局安装但只对某些智能体可见，请把共享副本放在 `~/.openclaw/skills` 中，再通过 `agents.defaults.skills` 和 `agents.list[].skills` 控制可见性。只有值得上游合并的修改才应放在仓库里并通过 PR 提交。
  </Accordion>

  <Accordion title="我可以从自定义文件夹加载 Skills 吗？">
    可以。通过 `~/.openclaw/openclaw.json` 中的 `skills.load.extraDirs` 添加额外目录（最低优先级）。默认优先级顺序是 `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → 内置 → `skills.load.extraDirs`。`clawhub` 默认安装到 `./skills`，OpenClaw 会在下一次会话中将其视为 `<workspace>/skills`。如果某个 Skill 只应对特定智能体可见，请结合 `agents.defaults.skills` 或 `agents.list[].skills` 使用。
  </Accordion>

  <Accordion title="如何为不同任务使用不同模型？">
    目前支持的模式有：

    - **Cron 作业**：隔离作业可以为每个作业设置 `model` 覆盖。
    - **子智能体**：将任务路由到具有不同默认模型的独立智能体。
    - **按需切换**：随时使用 `/model` 切换当前会话模型。

    请参阅 [Cron 作业](/zh-CN/automation/cron-jobs)、[多智能体路由](/zh-CN/concepts/multi-agent) 和 [斜杠命令](/zh-CN/tools/slash-commands)。

  </Accordion>

  <Accordion title="机器人在执行重任务时会卡住。如何把这类任务卸载出去？">
    对于长时间运行或并行任务，请使用**子智能体**。子智能体会在自己的会话中运行，
    返回摘要，并保持你的主聊天界面依然响应。

    你可以让机器人“为这个任务启动一个子智能体”，或者使用 `/subagents`。
    使用聊天中的 `/status` 可以查看 Gateway 网关当前正在做什么（以及它是否繁忙）。

    令牌提示：长任务和子智能体都会消耗令牌。如果你在意成本，可以通过 `agents.defaults.subagents.model` 为子智能体设置
    更便宜的模型。

    文档： [子智能体](/zh-CN/tools/subagents)、[后台任务](/zh-CN/automation/tasks)。

  </Accordion>

  <Accordion title="Discord 上绑定线程的子智能体会话是如何工作的？">
    使用线程绑定。你可以把 Discord 线程绑定到子智能体或会话目标，这样该线程中的后续消息就会始终发送到绑定的那个会话。

    基本流程：

    - 使用 `sessions_spawn` 并设置 `thread: true` 启动（也可选择 `mode: "session"` 以实现持久跟进）。
    - 或者手动用 `/focus <target>` 进行绑定。
    - 使用 `/agents` 查看绑定状态。
    - 使用 `/session idle <duration|off>` 和 `/session max-age <duration|off>` 控制自动取消聚焦。
    - 使用 `/unfocus` 解除线程绑定。

    所需配置：

    - 全局默认值：`session.threadBindings.enabled`、`session.threadBindings.idleHours`、`session.threadBindings.maxAgeHours`。
    - Discord 覆盖：`channels.discord.threadBindings.enabled`、`channels.discord.threadBindings.idleHours`、`channels.discord.threadBindings.maxAgeHours`。
    - 在启动时自动绑定：设置 `channels.discord.threadBindings.spawnSubagentSessions: true`。

    文档： [子智能体](/zh-CN/tools/subagents)、[Discord](/zh-CN/channels/discord)、[配置参考](/zh-CN/gateway/configuration-reference)、[斜杠命令](/zh-CN/tools/slash-commands)。

  </Accordion>

  <Accordion title="子智能体已完成，但完成更新发到了错误的位置，或者根本没有发送。我该检查什么？">
    先检查已解析的请求者路由：

    - 当存在已绑定的线程或对话路由时，完成模式的子智能体投递会优先使用它们。
    - 如果完成来源只携带渠道，OpenClaw 会回退到请求者会话中存储的路由（`lastChannel` / `lastTo` / `lastAccountId`），这样直接投递仍可能成功。
    - 如果既没有绑定路由，也没有可用的已存储路由，直接投递可能失败，结果会回退为排队的会话投递，而不是立即发送到聊天中。
    - 无效或过期的目标仍可能导致回退到队列投递，或最终投递失败。
    - 如果子任务最后一个可见的助手回复正好是静默令牌 `NO_REPLY` / `no_reply`，或者正好是 `ANNOUNCE_SKIP`，OpenClaw 会有意抑制公告，而不是发送之前已过期的进度信息。
    - 如果子任务在仅执行了工具调用后超时，公告可能会将其折叠为简短的部分进度摘要，而不是重放原始工具输出。

    调试：

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    文档： [子智能体](/zh-CN/tools/subagents)、[后台任务](/zh-CN/automation/tasks)、[会话工具](/zh-CN/concepts/session-tool)。

  </Accordion>

  <Accordion title="Cron 或提醒没有触发。我该检查什么？">
    Cron 在 Gateway 网关进程内部运行。如果 Gateway 网关没有持续运行，
    计划任务就不会执行。

    检查清单：

    - 确认已启用 cron（`cron.enabled`），并且未设置 `OPENCLAW_SKIP_CRON`。
    - 检查 Gateway 网关是否在 24/7 持续运行（没有休眠/重启）。
    - 验证作业的时区设置（`--tz` 与主机时区）。

    调试：

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    文档： [Cron 作业](/zh-CN/automation/cron-jobs)、[自动化与任务](/zh-CN/automation)。

  </Accordion>

  <Accordion title="Cron 触发了，但没有任何内容发送到渠道。为什么？">
    先检查投递模式：

    - `--no-deliver` / `delivery.mode: "none"` 表示不会有外部消息发送。
    - 缺少或无效的公告目标（`channel` / `to`）表示运行器跳过了对外投递。
    - 渠道认证失败（`unauthorized`、`Forbidden`）表示运行器尝试过投递，但凭证阻止了它。
    - 静默的隔离结果（仅有 `NO_REPLY` / `no_reply`）会被视为有意不可投递，因此运行器也会抑制排队回退投递。

    对于隔离的 cron 作业，最终投递由运行器负责。系统预期
    智能体返回纯文本摘要，由运行器负责发送。`--no-deliver` 会将
    该结果保留在内部；它并不会让智能体改为直接使用
    message 工具发送。

    调试：

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    文档： [Cron 作业](/zh-CN/automation/cron-jobs)、[后台任务](/zh-CN/automation/tasks)。

  </Accordion>

  <Accordion title="为什么隔离的 cron 运行会切换模型或重试一次？">
    这通常是实时模型切换路径，而不是重复调度。

    隔离的 cron 可以在活动运行抛出 `LiveSessionModelSwitchError` 时，
    持久化运行时模型切换并重试。重试会保留已切换的
    提供商/模型；如果切换还携带了新的认证配置文件覆盖，cron
    也会在重试前将其持久化。

    相关选择规则：

    - 若适用，Gmail hook 模型覆盖优先生效。
    - 然后是每个作业的 `model`。
    - 然后是任何已存储的 cron 会话模型覆盖。
    - 最后才是正常的智能体/默认模型选择。

    重试循环是有上限的。在初次尝试加上 2 次切换重试之后，
    cron 会中止，而不是无限循环。

    调试：

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    文档： [Cron 作业](/zh-CN/automation/cron-jobs)、[cron CLI](/cli/cron)。

  </Accordion>

  <Accordion title="如何在 Linux 上安装 Skills？">
    使用原生 `openclaw skills` 命令，或直接将 Skills 放入你的工作区。macOS 的 Skills UI 在 Linux 上不可用。
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
    目录。只有在你想发布或
    同步自己的 Skills 时，才需要单独安装 `clawhub` CLI。若要在多个智能体之间共享安装，请将 Skill 放到
    `~/.openclaw/skills` 下；如果你想限制只有某些智能体可见，请使用 `agents.defaults.skills` 或
    `agents.list[].skills`。

  </Accordion>

  <Accordion title="OpenClaw 可以按计划运行任务，或持续在后台运行吗？">
    可以。使用 Gateway 网关调度器：

    - **Cron 作业**：用于计划任务或周期性任务（重启后仍会保留）。
    - **Heartbeat**：用于“主会话”的周期性检查。
    - **隔离作业**：用于可自主运行、会发布摘要或投递到聊天中的智能体。

    文档： [Cron 作业](/zh-CN/automation/cron-jobs)、[自动化与任务](/zh-CN/automation)、
    [Heartbeat](/zh-CN/gateway/heartbeat)。

  </Accordion>

  <Accordion title="我可以从 Linux 运行 Apple 的 macOS 专属 Skills 吗？">
    不能直接运行。macOS Skills 受 `metadata.openclaw.os` 和所需二进制文件约束，且只有在 **Gateway 网关主机** 上符合条件时，这些 Skills 才会出现在系统提示中。在 Linux 上，`darwin` 专属 Skills（例如 `apple-notes`、`apple-reminders`、`things-mac`）不会加载，除非你覆盖此门控。

    你有三种受支持的模式：

    **选项 A - 在 Mac 上运行 Gateway 网关（最简单）。**
    在存在 macOS 二进制文件的地方运行 Gateway 网关，然后通过 [远程模式](#gateway-ports-already-running-and-remote-mode) 或 Tailscale 从 Linux 连接。因为 Gateway 网关主机是 macOS，所以这些 Skills 会正常加载。

    **选项 B - 使用 macOS 节点（无需 SSH）。**
    在 Linux 上运行 Gateway 网关，配对一个 macOS 节点（菜单栏应用），并在 Mac 上将 **Node Run Commands** 设置为 “Always Ask” 或 “Always Allow”。当节点上存在所需二进制文件时，OpenClaw 可以将 macOS 专属 Skills 视为符合条件。智能体会通过 `nodes` 工具运行这些 Skills。如果你选择 “Always Ask”，在提示中批准 “Always Allow” 会将该命令加入允许列表。

    **选项 C - 通过 SSH 代理 macOS 二进制文件（高级）。**
    将 Gateway 网关保留在 Linux 上，但让所需的 CLI 二进制文件解析为在 Mac 上运行的 SSH 包装器。然后覆盖 Skill，使其允许 Linux，从而保持符合条件。

    1. 为该二进制文件创建一个 SSH 包装器（示例：Apple Notes 的 `memo`）：

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. 将该包装器放到 Linux 主机的 `PATH` 中（例如 `~/bin/memo`）。
    3. 覆盖 Skill 元数据（工作区或 `~/.openclaw/skills`），以允许 Linux：

       ```markdown
       ---
       name: apple-notes
       description: 通过 macOS 上的 memo CLI 管理 Apple Notes。
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. 启动新会话，以刷新 Skills 快照。

  </Accordion>

  <Accordion title="你们有 Notion 或 HeyGen 集成吗？">
    目前没有内置。

    可选方案：

    - **自定义 Skill / 插件：**最适合可靠的 API 访问（Notion/HeyGen 都有 API）。
    - **浏览器自动化：**无需写代码，但更慢，也更脆弱。

    如果你想为每个客户保留上下文（代理机构工作流），一种简单模式是：

    - 每个客户一个 Notion 页面（上下文 + 偏好 + 当前工作）。
    - 让智能体在会话开始时先获取该页面。

    如果你想要原生集成，可以提交功能请求，或构建一个
    面向这些 API 的 Skill。

    安装 Skills：

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    原生安装会落到当前工作区的 `skills/` 目录中。若要在多个智能体之间共享 Skills，请将它们放在 `~/.openclaw/skills/<name>/SKILL.md`。如果只有部分智能体应看到共享安装，请配置 `agents.defaults.skills` 或 `agents.list[].skills`。某些 Skills 依赖通过 Homebrew 安装的二进制文件；在 Linux 上，这意味着 Linuxbrew（见上面的 Homebrew Linux 常见问题条目）。请参阅 [Skills](/zh-CN/tools/skills)、[Skills 配置](/zh-CN/tools/skills-config) 和 [ClawHub](/zh-CN/tools/clawhub)。

  </Accordion>

  <Accordion title="如何让 OpenClaw 使用我当前已登录的 Chrome？">
    使用内置的 `user` 浏览器配置文件，它通过 Chrome DevTools MCP 进行连接：

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    如果你想使用自定义名称，请创建一个显式 MCP 配置文件：

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    这条路径是主机本地的。如果 Gateway 网关运行在别处，请在浏览器所在机器上运行一个节点主机，或者改用远程 CDP。

    `existing-session` / `user` 当前限制：

    - 操作是基于 ref 驱动，而不是基于 CSS 选择器
    - 上传需要 `ref` / `inputRef`，并且当前一次只支持一个文件
    - `responsebody`、PDF 导出、下载拦截和批量操作仍然需要受管浏览器或原始 CDP 配置文件

  </Accordion>
</AccordionGroup>

## 沙箱隔离和记忆

<AccordionGroup>
  <Accordion title="有专门的沙箱隔离文档吗？">
    有。请参阅 [沙箱隔离](/zh-CN/gateway/sandboxing)。有关 Docker 专属设置（完整 Gateway 网关运行在 Docker 中，或沙箱镜像），请参阅 [Docker](/zh-CN/install/docker)。
  </Accordion>

  <Accordion title="Docker 感觉功能受限——如何启用完整功能？">
    默认镜像以安全优先为原则，并以 `node` 用户身份运行，因此它不
    包含系统软件包、Homebrew 或内置浏览器。若要获得更完整的设置：

    - 持久化 `/home/node`，并使用 `OPENCLAW_HOME_VOLUME`，这样缓存就能保留下来。
    - 使用 `OPENCLAW_DOCKER_APT_PACKAGES` 将系统依赖烘焙进镜像。
    - 通过内置 CLI 安装 Playwright 浏览器：
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - 设置 `PLAYWRIGHT_BROWSERS_PATH` 并确保该路径已持久化。

    文档： [Docker](/zh-CN/install/docker)、[浏览器](/zh-CN/tools/browser)。

  </Accordion>

  <Accordion title="我可以用一个智能体让私信保持私密，同时让群组公开/沙箱隔离吗？">
    可以——前提是你的私密流量是**私信**，公开流量是**群组**。

    使用 `agents.defaults.sandbox.mode: "non-main"`，这样群组/渠道会话（非主键）会在 Docker 中运行，而主私信会话仍在主机上运行。然后通过 `tools.sandbox.tools` 限制沙箱隔离会话中可用的工具。

    设置演练 + 示例配置： [群组：个人私信 + 公开群组](/zh-CN/channels/groups#pattern-personal-dms-public-groups-single-agent)

    关键配置参考： [Gateway 网关配置](/zh-CN/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="如何把主机文件夹绑定到沙箱中？">
    将 `agents.defaults.sandbox.docker.binds` 设置为 `["host:path:mode"]`（例如 `"/home/user/src:/src:ro"`）。全局绑定和按智能体绑定会合并；当 `scope: "shared"` 时，按智能体绑定会被忽略。对任何敏感内容都使用 `:ro`，并记住绑定会绕过沙箱文件系统隔离墙。

    OpenClaw 会同时根据规范化路径，以及通过最深层已存在祖先解析得到的规范路径，来验证绑定源。这意味着即使最后一个路径段尚不存在，经由符号链接父目录逃逸的情况仍会以默认拒绝方式关闭；并且在符号链接解析之后，允许根目录检查仍然会生效。

    有关示例和安全说明，请参阅 [沙箱隔离](/zh-CN/gateway/sandboxing#custom-bind-mounts) 和 [沙箱 vs 工具策略 vs 提权](/zh-CN/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check)。

  </Accordion>

  <Accordion title="记忆是如何工作的？">
    OpenClaw 的记忆就是智能体工作区中的 Markdown 文件：

    - `memory/YYYY-MM-DD.md` 中的每日笔记
    - `MEMORY.md` 中整理好的长期笔记（仅主/私密会话）

    OpenClaw 还会运行一个**静默的预压缩记忆刷新**，提醒模型
    在自动压缩前写入持久笔记。它只会在工作区
    可写时运行（只读沙箱会跳过）。请参阅 [记忆](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="记忆总是在忘东西。如何让它记住？">
    让机器人**把这个事实写入记忆**。长期笔记应写入 `MEMORY.md`，
    短期上下文则写入 `memory/YYYY-MM-DD.md`。

    这是我们仍在持续改进的领域。提醒模型存储记忆会有帮助；
    它会知道该怎么做。如果它仍然总是忘记，请确认 Gateway 网关每次运行时使用的是同一个
    工作区。

    文档： [记忆](/zh-CN/concepts/memory)、[智能体工作区](/zh-CN/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="记忆会永久保留吗？有什么限制？">
    记忆文件存储在磁盘上，并会一直保留，直到你删除它们。限制来自你的
    存储空间，而不是模型。**会话上下文**仍然受限于模型的
    上下文窗口，因此长对话可能会被压缩或截断。这就是为什么
    需要记忆搜索——它只会把相关部分重新拉回上下文。

    文档： [记忆](/zh-CN/concepts/memory)、[上下文](/zh-CN/concepts/context)。

  </Accordion>

  <Accordion title="语义记忆搜索需要 OpenAI API 密钥吗？">
    只有在你使用 **OpenAI embeddings** 时才需要。Codex OAuth 只覆盖聊天/补全，
    **不**提供 embeddings 访问，因此**使用 Codex 登录（OAuth 或
    Codex CLI 登录）**并不能帮助启用语义记忆搜索。OpenAI embeddings
    仍然需要真实的 API 密钥（`OPENAI_API_KEY` 或 `models.providers.openai.apiKey`）。

    如果你没有显式设置提供商，只要能解析到 API 密钥，OpenClaw 就会自动选择提供商
    （认证配置文件、`models.providers.*.apiKey` 或环境变量）。
    如果能解析到 OpenAI 密钥，它会优先选择 OpenAI；否则如果能解析到 Gemini 密钥，
    就选择 Gemini；再然后是 Voyage，最后是 Mistral。如果没有可用的远程密钥，记忆
    搜索会保持禁用，直到你完成配置。如果你配置了本地模型路径
    且该路径存在，OpenClaw
    会优先选择 `local`。当你显式设置
    `memorySearch.provider = "ollama"` 时，也支持 Ollama。

    如果你更希望保持本地化，请设置 `memorySearch.provider = "local"`（并可选设置
    `memorySearch.fallback = "none"`）。如果你想使用 Gemini embeddings，请设置
    `memorySearch.provider = "gemini"`，并提供 `GEMINI_API_KEY`（或
    `memorySearch.remote.apiKey`）。我们支持 **OpenAI、Gemini、Voyage、Mistral、Ollama 或 local** 的 embedding
    模型——具体设置详情请参阅 [记忆](/zh-CN/concepts/memory)。

  </Accordion>
</AccordionGroup>

## 磁盘上的文件位置

<AccordionGroup>
  <Accordion title="OpenClaw 使用的所有数据都会保存在本地吗？">
    不会——**OpenClaw 的状态保存在本地**，但**外部服务仍然会看到你发给它们的内容**。

    - **默认保存在本地：**会话、记忆文件、配置和工作区都保存在 Gateway 网关主机上
      （`~/.openclaw` + 你的工作区目录）。
    - **必须远程发送：**你发给模型提供商（Anthropic/OpenAI 等）的消息会发送到
      它们的 API，而聊天平台（WhatsApp/Telegram/Slack 等）会在它们的
      服务器上存储消息数据。
    - **足迹由你控制：**使用本地模型可以让提示保留在你的机器上，但渠道
      流量仍然会经过该渠道的服务器。

    相关内容： [智能体工作区](/zh-CN/concepts/agent-workspace)、[记忆](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="OpenClaw 把数据存在哪里？">
    所有内容都位于 `$OPENCLAW_STATE_DIR` 下（默认：`~/.openclaw`）：

    | 路径                                                            | 用途                                                               |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | 主配置（JSON5）                                                    |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | 旧版 OAuth 导入（首次使用时复制到认证配置文件中）                  |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | 认证配置文件（OAuth、API 密钥，以及可选的 `keyRef`/`tokenRef`）    |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef 提供商的可选文件后端密钥负载                      |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | 旧版兼容文件（静态 `api_key` 条目已清理）                          |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | 提供商状态（例如 `whatsapp/<accountId>/creds.json`）               |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | 按智能体划分的状态（agentDir + 会话）                              |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | 对话历史和状态（按智能体）                                         |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | 会话元数据（按智能体）                                             |

    旧版单智能体路径：`~/.openclaw/agent/*`（由 `openclaw doctor` 迁移）。

    你的**工作区**（AGENTS.md、记忆文件、Skills 等）是分开的，并通过 `agents.defaults.workspace` 配置（默认：`~/.openclaw/workspace`）。

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md 应该放在哪里？">
    这些文件位于**智能体工作区**中，而不是 `~/.openclaw`。

    - **工作区（按智能体）：**`AGENTS.md`、`SOUL.md`、`IDENTITY.md`、`USER.md`、
      `MEMORY.md`（当 `MEMORY.md` 不存在时，使用旧版回退 `memory.md`）、
      `memory/YYYY-MM-DD.md`、可选的 `HEARTBEAT.md`。
    - **状态目录（`~/.openclaw`）：**配置、渠道/提供商状态、认证配置文件、会话、日志，
      以及共享 Skills（`~/.openclaw/skills`）。

    默认工作区为 `~/.openclaw/workspace`，可通过以下方式配置：

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    如果机器人在重启后“忘记”了内容，请确认 Gateway 网关在每次启动时都使用相同的
    工作区（并且要记住：远程模式使用的是**Gateway 网关主机的**
    工作区，而不是你本地笔记本电脑上的工作区）。

    提示：如果你希望某种行为或偏好能长期保留，最好让机器人**把它写入
    AGENTS.md 或 MEMORY.md**，而不是仅依赖聊天历史。

    请参阅 [智能体工作区](/zh-CN/concepts/agent-workspace) 和 [记忆](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="推荐的备份策略">
    将你的**智能体工作区**放进一个**私有** git 仓库，并把它备份到某个
    私密位置（例如 GitHub 私有仓库）。这样可以保存记忆 + AGENTS/SOUL/USER
    文件，并让你日后能够恢复这个助手的“心智”。

    **不要**提交 `~/.openclaw` 下的任何内容（凭证、会话、令牌或加密的密钥负载）。
    如果你需要完整恢复，请分别备份工作区和状态目录
    （见上面的迁移问题）。

    文档： [智能体工作区](/zh-CN/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="如何彻底卸载 OpenClaw？">
    请参阅专门指南： [卸载](/zh-CN/install/uninstall)。
  </Accordion>

  <Accordion title="智能体可以在工作区之外工作吗？">
    可以。工作区是**默认 cwd** 和记忆锚点，而不是硬性沙箱。
    相对路径会在工作区内解析，但绝对路径可以访问其他
    主机位置，除非启用了沙箱隔离。如果你需要隔离，请使用
    [`agents.defaults.sandbox`](/zh-CN/gateway/sandboxing) 或按智能体设置的沙箱配置。如果你
    希望某个仓库成为默认工作目录，请将该智能体的
    `workspace` 指向仓库根目录。OpenClaw 仓库本身只是源代码；除非你明确希望智能体在其中工作，否则请将
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
    会话状态归**Gateway 网关主机**所有。如果你处于远程模式，你关心的会话存储位于远程机器上，而不是你本地的笔记本电脑。请参阅 [会话管理](/zh-CN/concepts/session)。
  </Accordion>
</AccordionGroup>

## 配置基础

<AccordionGroup>
  <Accordion title="配置是什么格式？它在哪里？">
    OpenClaw 会从 `$OPENCLAW_CONFIG_PATH` 读取一个可选的 **JSON5** 配置（默认：`~/.openclaw/openclaw.json`）：

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    如果该文件不存在，它会使用较为安全的默认值（包括默认工作区 `~/.openclaw/workspace`）。

  </Accordion>

  <Accordion title='我设置了 gateway.bind: "lan"（或 "tailnet"），现在没有任何监听 / UI 显示 unauthorized'>
    非 loopback 绑定**需要有效的 Gateway 网关认证路径**。实际来说，这意味着：

    - 共享密钥认证：令牌或密码
    - 在配置正确的非 loopback 身份感知反向代理之后使用 `gateway.auth.mode: "trusted-proxy"`

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

    说明：

    - `gateway.remote.token` / `.password` 本身**不会**启用本地 Gateway 网关认证。
    - 只有当 `gateway.auth.*` 未设置时，本地调用路径才能将 `gateway.remote.*` 用作回退。
    - 对于密码认证，请改为设置 `gateway.auth.mode: "password"`，并同时设置 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
    - 如果 `gateway.auth.token` / `gateway.auth.password` 通过 SecretRef 显式配置但无法解析，解析会以默认拒绝方式关闭（不会由远程回退掩盖）。
    - 共享密钥的 Control UI 设置通过 `connect.params.auth.token` 或 `connect.params.auth.password` 进行认证（存储在应用/UI 设置中）。像 Tailscale Serve 或 `trusted-proxy` 这样的带身份模式则改用请求标头。避免把共享密钥放进 URL。
    - 当使用 `gateway.auth.mode: "trusted-proxy"` 时，同一主机上的 loopback 反向代理**仍然不能**满足 trusted-proxy 认证要求。受信任代理必须是已配置的非 loopback 来源。

  </Accordion>

  <Accordion title="为什么现在在 localhost 上也需要令牌？">
    OpenClaw 默认强制要求 Gateway 网关认证，包括 loopback。在正常默认路径下，这意味着使用令牌认证：如果没有显式配置认证路径，Gateway 网关启动时会解析为令牌模式，并自动生成一个令牌，保存到 `gateway.auth.token` 中，因此**本地 WS 客户端必须进行认证**。这样可以阻止其他本地进程调用 Gateway 网关。

    如果你更偏好其他认证路径，可以显式选择密码模式（或者，对于非 loopback 的身份感知反向代理，选择 `trusted-proxy`）。如果你**确实**想开放 loopback，请在配置中显式设置 `gateway.auth.mode: "none"`。Doctor 随时都可以帮你生成令牌：`openclaw doctor --generate-gateway-token`。

  </Accordion>

  <Accordion title="改完配置后一定要重启吗？">
    Gateway 网关会监视配置并支持热重载：

    - `gateway.reload.mode: "hybrid"`（默认）：安全变更热应用，关键变更则重启
    - 也支持 `hot`、`restart`、`off`

  </Accordion>

  <Accordion title="如何关闭 CLI 里那些搞笑标语？">
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

    - `off`：隐藏标语文本，但保留横幅标题/版本行。
    - `default`：始终使用 `All your chats, one OpenClaw.`。
    - `random`：轮换搞笑/季节性标语（默认行为）。
    - 如果你想完全不显示横幅，请设置环境变量 `OPENCLAW_HIDE_BANNER=1`。

  </Accordion>

  <Accordion title="如何启用 Web 搜索（以及 Web 抓取）？">
    `web_fetch` 无需 API 密钥即可使用。`web_search` 取决于你选择的
    提供商：

    - Brave、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Perplexity 和 Tavily 等基于 API 的提供商，需要按其常规方式配置 API 密钥。
    - Ollama Web 搜索不需要密钥，但它会使用你配置的 Ollama 主机，并要求执行 `ollama signin`。
    - DuckDuckGo 不需要密钥，但它是非官方的基于 HTML 的集成。
    - SearXNG 不需要密钥/可自行托管；配置 `SEARXNG_BASE_URL` 或 `plugins.entries.searxng.config.webSearch.baseUrl`。

    **推荐：**运行 `openclaw configure --section web` 并选择一个提供商。
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

    提供商专属的 Web 搜索配置现在位于 `plugins.entries.<plugin>.config.webSearch.*` 下。
    出于兼容性考虑，旧版 `tools.web.search.*` 提供商路径暂时仍可加载，但不应再用于新配置。
    Firecrawl 的 Web 抓取回退配置位于 `plugins.entries.firecrawl.config.webFetch.*` 下。

    说明：

    - 如果你使用允许列表，请加入 `web_search`/`web_fetch`/`x_search` 或 `group:web`。
    - `web_fetch` 默认启用（除非显式禁用）。
    - 如果省略 `tools.web.fetch.provider`，OpenClaw 会从可用凭证中自动检测第一个可用的抓取回退提供商。目前内置提供商是 Firecrawl。
    - 守护进程会从 `~/.openclaw/.env`（或服务环境）读取环境变量。

    文档： [Web 工具](/zh-CN/tools/web)。

  </Accordion>

  <Accordion title="config.apply 把我的配置清空了。我该如何恢复并避免再次发生？">
    `config.apply` 会替换**整个配置**。如果你发送的是部分对象，其他所有内容
    都会被移除。

    恢复方法：

    - 从备份恢复（git 或复制的 `~/.openclaw/openclaw.json`）。
    - 如果你没有备份，请重新运行 `openclaw doctor`，然后重新配置渠道/模型。
    - 如果这不是你预期的行为，请提交一个 bug，并附上你最后已知的配置或任何备份。
    - 本地编码智能体通常可以根据日志或历史记录重建一个可用配置。

    避免方法：

    - 小改动请使用 `openclaw config set`。
    - 交互式编辑请使用 `openclaw configure`。
    - 当你不确定准确路径或字段结构时，先使用 `config.schema.lookup`；它会返回一个浅层 schema 节点及其直接子项摘要，便于逐层深入。
    - 对于部分 RPC 编辑，请使用 `config.patch`；仅在需要完整替换配置时才使用 `config.apply`。
    - 如果你在智能体运行中使用仅限所有者的 `gateway` 工具，它仍会拒绝对 `tools.exec.ask` / `tools.exec.security` 的写入（包括会归一化为同一受保护 exec 路径的旧版 `tools.bash.*` 别名）。

    文档： [配置](/cli/config)、[配置向导](/cli/configure)、[Doctor](/zh-CN/gateway/doctor)。

  </Accordion>

  <Accordion title="如何运行一个中心化的 Gateway 网关，并让不同设备承担专门的工作？">
    常见模式是**一个 Gateway 网关**（例如 Raspberry Pi）加上**节点**和**智能体**：

    - **Gateway 网关（中心）：**负责渠道（Signal/WhatsApp）、路由和会话。
    - **节点（设备）：**Mac/iOS/Android 作为外围设备连接，并暴露本地工具（`system.run`、`canvas`、`camera`）。
    - **智能体（工作者）：**为专门角色提供独立的大脑/工作区（例如“Hetzner 运维”“个人数据”）。
    - **子智能体：**当你想并行处理时，从主智能体派生后台工作。
    - **TUI：**连接到 Gateway 网关并切换智能体/会话。

    文档： [节点](/zh-CN/nodes)、[远程访问](/zh-CN/gateway/remote)、[多智能体路由](/zh-CN/concepts/multi-agent)、[子智能体](/zh-CN/tools/subagents)、[TUI](/web/tui)。

  </Accordion>

  <Accordion title="OpenClaw 浏览器可以无头运行吗？">
    可以。这是一个配置选项：

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

    默认值是 `false`（有头模式）。无头模式在某些网站上更容易触发反机器人检查。请参阅 [浏览器](/zh-CN/tools/browser)。

    无头模式使用**相同的 Chromium 引擎**，适用于大多数自动化任务（表单、点击、抓取、登录）。主要区别在于：

    - 没有可见的浏览器窗口（如果你需要可视化，请使用截图）。
    - 有些网站在无头模式下对自动化更严格（CAPTCHA、反机器人）。
      例如，X/Twitter 经常会拦截无头会话。

  </Accordion>

  <Accordion title="如何使用 Brave 进行浏览器控制？">
    将 `browser.executablePath` 设置为你的 Brave 二进制文件（或任何基于 Chromium 的浏览器），然后重启 Gateway 网关。
    完整配置示例请参阅 [浏览器](/zh-CN/tools/browser#use-brave-or-another-chromium-based-browser)。
  </Accordion>
</AccordionGroup>

## 远程 Gateway 网关和节点

<AccordionGroup>
  <Accordion title="Telegram、Gateway 网关和节点之间，命令是如何传播的？">
    Telegram 消息由 **Gateway 网关**处理。Gateway 网关运行智能体，
    只有在需要节点工具时，才会通过 **Gateway WebSocket**
    调用节点：

    Telegram → Gateway 网关 → 智能体 → `node.*` → 节点 → Gateway 网关 → Telegram

    节点看不到入站提供商流量；它们只接收节点 RPC 调用。

  </Accordion>

  <Accordion title="如果 Gateway 网关托管在远程环境中，我的智能体如何访问我的电脑？">
    简短回答：**把你的电脑配对为节点**。Gateway 网关运行在别处，但它可以
    通过 Gateway WebSocket 在你的本地机器上调用 `node.*` 工具（屏幕、摄像头、系统）。

    典型设置：

    1. 在始终在线的主机（VPS/家用服务器）上运行 Gateway 网关。
    2. 将 Gateway 网关主机和你的电脑放到同一个 tailnet 中。
    3. 确保 Gateway WS 可达（tailnet 绑定或 SSH 隧道）。
    4. 在本地打开 macOS 应用，并以**通过 SSH 远程连接**模式（或直接 tailnet）
       连接，以便它注册为一个节点。
    5. 在 Gateway 网关上批准该节点：

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    不需要单独的 TCP bridge；节点通过 Gateway WebSocket 连接。

    安全提醒：配对一个 macOS 节点意味着允许在该机器上执行 `system.run`。只
    配对你信任的设备，并查看 [安全性](/zh-CN/gateway/security)。

    文档： [节点](/zh-CN/nodes)、[Gateway 网关协议](/zh-CN/gateway/protocol)、[macOS 远程模式](/zh-CN/platforms/mac/remote)、[安全性](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="Tailscale 已连接，但我收不到回复。现在怎么办？">
    先检查基础项：

    - Gateway 网关正在运行：`openclaw gateway status`
    - Gateway 网关健康状态：`openclaw status`
    - 渠道健康状态：`openclaw channels status`

    然后验证认证和路由：

    - 如果你使用 Tailscale Serve，请确认 `gateway.auth.allowTailscale` 设置正确。
    - 如果你通过 SSH 隧道连接，请确认本地隧道已建立并指向正确端口。
    - 确认你的允许列表（私信或群组）包含你的账号。

    文档： [Tailscale](/zh-CN/gateway/tailscale)、[远程访问](/zh-CN/gateway/remote)、[渠道](/zh-CN/channels)。

  </Accordion>

  <Accordion title="两个 OpenClaw 实例之间可以互相通信吗（本地 + VPS）？">
    可以。虽然没有内置的“机器人对机器人”桥接，但你可以通过几种
    可靠方式来实现：

    **最简单：**使用两个机器人都能访问的普通聊天渠道（Telegram/Slack/WhatsApp）。
    让机器人 A 向机器人 B 发送消息，然后由机器人 B 正常回复。

    **CLI bridge（通用）：**运行一个脚本，通过
    `openclaw agent --message ... --deliver` 调用另一个 Gateway 网关，并将目标指向另一个机器人
    监听的聊天。如果其中一个机器人部署在远程 VPS 上，请让你的 CLI 通过 SSH/Tailscale 指向那个远程 Gateway 网关
    （参见 [远程访问](/zh-CN/gateway/remote)）。

    示例模式（在能访问目标 Gateway 网关的机器上运行）：

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    提示：添加一个保护措施，防止两个机器人无限循环（仅提及时回复、渠道
    允许列表，或“不要回复机器人消息”的规则）。

    文档： [远程访问](/zh-CN/gateway/remote)、[智能体 CLI](/cli/agent)、[智能体发送](/zh-CN/tools/agent-send)。

  </Accordion>

  <Accordion title="多个智能体需要分别使用不同的 VPS 吗？">
    不需要。一个 Gateway 网关就可以托管多个智能体，每个智能体都有自己的工作区、默认模型
    和路由。这是常见配置，比起为每个智能体分别运行
    一个 VPS，更便宜也更简单。

    只有当你需要硬隔离（安全边界）或非常
    不同、且不想共享的配置时，才需要分别使用不同 VPS。否则，保留一个 Gateway 网关，
    并使用多个智能体或子智能体即可。

  </Accordion>

  <Accordion title="与从 VPS 通过 SSH 访问相比，在我的个人笔记本电脑上使用节点有什么好处吗？">
    有——节点是从远程 Gateway 网关访问你笔记本电脑的一等方式，并且
    提供的不只是 shell 访问。Gateway 网关可以运行在 macOS/Linux 上（Windows 通过 WSL2），并且
    很轻量（小型 VPS 或 Raspberry Pi 级设备即可；4 GB RAM 已经很充足），因此一种常见
    配置是使用一个始终在线的主机，再把你的笔记本电脑作为节点。

    - **无需入站 SSH。**节点主动连接到 Gateway WebSocket，并使用设备配对。
    - **更安全的执行控制。**`system.run` 在那台笔记本电脑上受节点允许列表/审批控制。
    - **更多设备工具。**除了 `system.run`，节点还暴露 `canvas`、`camera` 和 `screen`。
    - **本地浏览器自动化。**把 Gateway 网关放在 VPS 上，但通过笔记本电脑上的节点主机在本地运行 Chrome，或通过 Chrome MCP 连接到主机上的本地 Chrome。

    SSH 适合临时 shell 访问，但对于持续性的智能体工作流和
    设备自动化，节点更简单。

    文档： [节点](/zh-CN/nodes)、[Nodes CLI](/cli/nodes)、[浏览器](/zh-CN/tools/browser)。

  </Accordion>

  <Accordion title="节点会运行一个 Gateway 网关服务吗？">
    不会。除非你有意运行隔离配置文件（参见 [多个 Gateway 网关](/zh-CN/gateway/multiple-gateways)），否则每台主机上只应运行**一个 Gateway 网关**。节点是连接到
    Gateway 网关的外围设备（iOS/Android 节点，或菜单栏应用中的 macOS“节点模式”）。有关无头节点
    主机和 CLI 控制，请参阅 [节点主机 CLI](/cli/node)。

    对 `gateway`、`discovery` 和 `canvasHost` 的更改需要完整重启。

  </Accordion>

  <Accordion title="有没有通过 API / RPC 应用配置的方法？">
    有。

    - `config.schema.lookup`：在写入前检查某个配置子树，返回其浅层 schema 节点、匹配的 UI 提示和直接子项摘要
    - `config.get`：获取当前快照 + 哈希
    - `config.patch`：安全的部分更新（大多数 RPC 编辑的首选）；可热重载时热重载，必须重启时自动重启
    - `config.apply`：验证 + 替换完整配置；可热重载时热重载，必须重启时自动重启
    - 仅限所有者的 `gateway` 运行时工具仍然拒绝重写 `tools.exec.ask` / `tools.exec.security`；旧版 `tools.bash.*` 别名会归一化到同一受保护的 exec 路径

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

  <Accordion title="如何在 VPS 上设置 Tailscale，并从我的 Mac 连接？">
    最小步骤：

    1. **在 VPS 上安装并登录**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **在你的 Mac 上安装并登录**
       - 使用 Tailscale 应用并登录到同一个 tailnet。
    3. **启用 MagicDNS（推荐）**
       - 在 Tailscale 管理控制台中启用 MagicDNS，这样 VPS 就会有一个稳定名称。
    4. **使用 tailnet 主机名**
       - SSH：`ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS：`ws://your-vps.tailnet-xxxx.ts.net:18789`

    如果你想在不使用 SSH 的情况下访问 Control UI，请在 VPS 上使用 Tailscale Serve：

    ```bash
    openclaw gateway --tailscale serve
    ```

    这样会让 Gateway 网关继续绑定到 loopback，并通过 Tailscale 暴露 HTTPS。请参阅 [Tailscale](/zh-CN/gateway/tailscale)。

  </Accordion>

  <Accordion title="如何把 Mac 节点连接到远程 Gateway 网关（Tailscale Serve）？">
    Serve 会暴露**Gateway 网关 Control UI + WS**。节点通过相同的 Gateway WS 端点连接。

    推荐设置：

    1. **确保 VPS 和 Mac 位于同一个 tailnet 中**。
    2. **在远程模式下使用 macOS 应用**（SSH 目标可以是 tailnet 主机名）。
       应用会隧道化 Gateway 端口，并以节点身份连接。
    3. **在 Gateway 网关上批准该节点**：

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    文档： [Gateway 网关协议](/zh-CN/gateway/protocol)、[设备发现](/zh-CN/gateway/discovery)、[macOS 远程模式](/zh-CN/platforms/mac/remote)。

  </Accordion>

  <Accordion title="我应该在第二台笔记本电脑上安装，还是只添加一个节点？">
    如果你只需要第二台笔记本电脑上的**本地工具**（屏幕/摄像头/exec），就把它添加为
    **节点**。这样可以保留一个单一 Gateway 网关，并避免重复配置。本地节点工具
    目前仅支持 macOS，但我们计划扩展到其他操作系统。

    只有在你需要**硬隔离**或两个完全独立的机器人时，才需要安装第二个 Gateway 网关。

    文档： [节点](/zh-CN/nodes)、[Nodes CLI](/cli/nodes)、[多个 Gateway 网关](/zh-CN/gateway/multiple-gateways)。

  </Accordion>
</AccordionGroup>

## 环境变量和 .env 加载

<AccordionGroup>
  <Accordion title="OpenClaw 如何加载环境变量？">
    OpenClaw 会读取父进程中的环境变量（shell、launchd/systemd、CI 等），并额外加载：

    - 当前工作目录中的 `.env`
    - `~/.openclaw/.env` 中的全局回退 `.env`（也就是 `$OPENCLAW_STATE_DIR/.env`）

    这两个 `.env` 文件都不会覆盖现有环境变量。

    你也可以在配置中定义内联环境变量（仅在进程环境中缺失时应用）：

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    完整的优先级和来源请参阅 [/environment](/zh-CN/help/environment)。

  </Accordion>

  <Accordion title="我通过服务启动了 Gateway 网关，结果环境变量都丢了。现在怎么办？">
    两种常见修复方式：

    1. 将缺失的键放入 `~/.openclaw/.env`，这样即使服务没有继承你的 shell 环境，也能读取到。
    2. 启用 shell 导入（可选的便捷功能）：

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

    这会运行你的登录 shell，并且只导入缺失的预期键名（绝不覆盖）。对应环境变量：
    `OPENCLAW_LOAD_SHELL_ENV=1`、`OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`。

  </Accordion>

  <Accordion title='我设置了 COPILOT_GITHUB_TOKEN，但 models status 显示 “Shell env: off.”。为什么？'>
    `openclaw models status` 报告的是**是否启用了 shell 环境导入**。“Shell env: off”
    **不**表示你的环境变量缺失——它只是表示 OpenClaw 不会
    自动加载你的登录 shell。

    如果 Gateway 网关作为服务运行（launchd/systemd），它不会继承你的 shell
    环境。可通过以下方式之一修复：

    1. 将令牌放入 `~/.openclaw/.env`：

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. 或启用 shell 导入（`env.shellEnv.enabled: true`）。
    3. 或将其加入配置中的 `env` 块（仅在缺失时应用）。

    然后重启 Gateway 网关并重新检查：

    ```bash
    openclaw models status
    ```

    Copilot 令牌会从 `COPILOT_GITHUB_TOKEN` 读取（也支持 `GH_TOKEN` / `GITHUB_TOKEN`）。
    请参阅 [/concepts/model-providers](/zh-CN/concepts/model-providers) 和 [/environment](/zh-CN/help/environment)。

  </Accordion>
</AccordionGroup>

## 会话和多个聊天

<AccordionGroup>
  <Accordion title="如何开始一个新的对话？">
    发送 `/new` 或 `/reset` 作为独立消息。请参阅 [会话管理](/zh-CN/concepts/session)。
  </Accordion>

  <Accordion title="如果我从不发送 /new，会话会自动重置吗？">
    会话可以在 `session.idleMinutes` 后过期，但这项功能**默认禁用**（默认值为 **0**）。
    将其设置为正值即可启用空闲过期。启用后，空闲期过后的**下一条**
    消息会为该聊天键开启一个新的会话 ID。
    这不会删除转录记录——它只是开始一个新会话。

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="有没有办法组建一个 OpenClaw 实例团队（一个 CEO 和多个智能体）？">
    有，可以通过**多智能体路由**和**子智能体**实现。你可以创建一个协调者
    智能体，以及多个拥有各自工作区和模型的工作智能体。

    不过，这更适合作为一个**有趣的实验**。它会消耗大量令牌，而且通常
    不如使用一个机器人配合不同会话高效。我们通常设想的模型是：
    你只和一个机器人交互，但为并行工作使用不同会话。这个
    机器人也可以在需要时启动子智能体。

    文档： [多智能体路由](/zh-CN/concepts/multi-agent)、[子智能体](/zh-CN/tools/subagents)、[智能体 CLI](/cli/agents)。

  </Accordion>

  <Accordion title="为什么上下文会在任务进行中被截断？我该如何防止？">
    会话上下文受限于模型窗口。长聊天、大量工具输出或许多
    文件都可能触发压缩或截断。

    有帮助的做法：

    - 让机器人总结当前状态并写入文件。
    - 在长任务前使用 `/compact`，切换话题时使用 `/new`。
    - 将重要上下文保存在工作区中，并让机器人重新读取。
    - 对长任务或并行工作使用子智能体，以保持主聊天更小。
    - 如果这种情况经常发生，请选择上下文窗口更大的模型。

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

    说明：

    - 如果新手引导检测到现有配置，也会提供**重置**选项。请参阅 [设置向导（CLI）](/zh-CN/start/wizard)。
    - 如果你使用了配置文件（`--profile` / `OPENCLAW_PROFILE`），请分别重置每个状态目录（默认是 `~/.openclaw-<profile>`）。
    - 开发重置：`openclaw gateway --dev --reset`（仅限开发；会清除开发配置 + 凭证 + 会话 + 工作区）。

  </Accordion>

  <Accordion title='我遇到了 “context too large” 错误——该如何重置或压缩？'>
    使用以下任一方式：

    - **压缩**（保留对话，但总结较早的轮次）：

      ```
      /compact
      ```

      或使用 `/compact <instructions>` 来指导摘要内容。

    - **重置**（为同一聊天键创建全新的会话 ID）：

      ```
      /new
      /reset
      ```

    如果这种情况反复发生：

    - 启用或调整**会话修剪**（`agents.defaults.contextPruning`）以裁剪旧的工具输出。
    - 使用上下文窗口更大的模型。

    文档： [压缩](/zh-CN/concepts/compaction)、[会话修剪](/zh-CN/concepts/session-pruning)、[会话管理](/zh-CN/concepts/session)。

  </Accordion>

  <Accordion title='为什么我会看到 “LLM request rejected: messages.content.tool_use.input field required”？'>
    这是提供商验证错误：模型发出了一个缺少必需
    `input` 的 `tool_use` 块。通常意味着会话历史陈旧或已损坏（常见于长线程
    或工具/schema 变更之后）。

    修复方法：使用 `/new`（独立消息）开始一个新会话。

  </Accordion>

  <Accordion title="为什么我每 30 分钟就会收到一次 heartbeat 消息？">
    Heartbeat 默认每 **30 分钟**运行一次（使用 OAuth 认证时为 **1 小时**）。你可以调整或禁用它们：

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // 或设为 "0m" 以禁用
          },
        },
      },
    }
    ```

    如果 `HEARTBEAT.md` 存在但实际上为空（只有空行和 Markdown
    标题，例如 `# Heading`），OpenClaw 会跳过 heartbeat 运行以节省 API 调用。
    如果文件不存在，heartbeat 仍会运行，并由模型决定该做什么。

    按智能体覆盖使用 `agents.list[].heartbeat`。文档： [Heartbeat](/zh-CN/gateway/heartbeat)。

  </Accordion>

  <Accordion title='我需要把一个“机器人账号”加入 WhatsApp 群组吗？'>
    不需要。OpenClaw 运行在**你自己的账号**上，所以只要你在群里，OpenClaw 就能看到它。
    默认情况下，群组回复会被阻止，直到你允许发送者（`groupPolicy: "allowlist"`）。

    如果你希望只有**你自己**能够触发群组回复：

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
    方式 1（最快）：查看日志，并在群里发送一条测试消息：

    ```bash
    openclaw logs --follow --json
    ```

    查找以 `@g.us` 结尾的 `chatId`（或 `from`），例如：
    `1234567890-1234567890@g.us`。

    方式 2（如果已配置/加入允许列表）：从配置中列出群组：

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    文档： [WhatsApp](/zh-CN/channels/whatsapp)、[目录](/cli/directory)、[日志](/cli/logs)。

  </Accordion>

  <Accordion title="为什么 OpenClaw 在群组中不回复？">
    两个常见原因：

    - 提及门控处于开启状态（默认）。你必须 @ 提及机器人（或匹配 `mentionPatterns`）。
    - 你配置了 `channels.whatsapp.groups`，但没有包含 `"*"`，并且该群组不在允许列表中。

    请参阅 [群组](/zh-CN/channels/groups) 和 [群组消息](/zh-CN/channels/group-messages)。

  </Accordion>

  <Accordion title="群组/线程会和私信共享上下文吗？">
    直接聊天默认会折叠到主会话。群组/渠道有各自独立的会话键，而 Telegram 话题 / Discord 线程也都是独立会话。请参阅 [群组](/zh-CN/channels/groups) 和 [群组消息](/zh-CN/channels/group-messages)。
  </Accordion>

  <Accordion title="我可以创建多少个工作区和智能体？">
    没有硬性限制。几十个（甚至上百个）都没问题，但要注意：

    - **磁盘增长：**会话 + 转录记录位于 `~/.openclaw/agents/<agentId>/sessions/` 下。
    - **令牌成本：**智能体越多，并发模型使用也越多。
    - **运维开销：**按智能体划分的认证配置文件、工作区和渠道路由。

    提示：

    - 每个智能体保持一个**活跃**工作区（`agents.defaults.workspace`）。
    - 如果磁盘增长明显，请修剪旧会话（删除 JSONL 或存储条目）。
    - 使用 `openclaw doctor` 检查零散工作区和配置文件不匹配问题。

  </Accordion>

  <Accordion title="我可以同时运行多个机器人或聊天（Slack）吗？应该如何设置？">
    可以。使用**多智能体路由**来运行多个相互隔离的智能体，并按
    渠道/账号/peer 路由入站消息。Slack 作为渠道受支持，也可以绑定到特定智能体。

    浏览器访问能力很强，但并不是“人类能做的都能做”——反机器人机制、CAPTCHA 和 MFA
    仍然可能阻止自动化。若要获得最可靠的浏览器控制，请在主机上使用本地 Chrome MCP，
    或在实际运行浏览器的机器上使用 CDP。

    最佳实践设置：

    - 始终在线的 Gateway 网关主机（VPS/Mac mini）。
    - 每个角色对应一个智能体（绑定）。
    - 将 Slack 渠道绑定到这些智能体。
    - 在需要时通过 Chrome MCP 或节点使用本地浏览器。

    文档： [多智能体路由](/zh-CN/concepts/multi-agent)、[Slack](/zh-CN/channels/slack)、
    [浏览器](/zh-CN/tools/browser)、[节点](/zh-CN/nodes)。

  </Accordion>
</AccordionGroup>

## 模型：默认值、选择、别名、切换

<AccordionGroup>
  <Accordion title='什么是“默认模型”？'>
    OpenClaw 的默认模型就是你设置在：

    ```
    agents.defaults.model.primary
    ```

    中的那个模型。

    模型以 `provider/model` 的形式引用（例如：`openai/gpt-5.4`）。如果你省略提供商，OpenClaw 会先尝试别名，然后尝试与该确切模型 id 唯一匹配的已配置提供商，只有最后才会回退到已配置默认提供商这一已弃用的兼容路径。如果该提供商已经不再暴露已配置的默认模型，OpenClaw 会回退到第一个已配置的提供商/模型，而不是暴露一个已移除提供商的陈旧默认值。你仍然应该**显式**设置 `provider/model`。

  </Accordion>

  <Accordion title="你们推荐什么模型？">
    **推荐默认值：**使用你的提供商栈中可用的最强最新一代模型。
    **对于启用了工具或接收不可信输入的智能体：**优先考虑模型能力，而不是成本。
    **对于日常/低风险聊天：**使用更便宜的回退模型，并按智能体角色进行路由。

    MiniMax 有自己的文档： [MiniMax](/zh-CN/providers/minimax) 和
    [本地模型](/zh-CN/gateway/local-models)。

    经验法则：对于高风险工作，使用你**能负担得起的最佳模型**；对于日常聊天或摘要，
    使用更便宜的模型。你可以按智能体路由模型，并使用子智能体来
    并行处理长任务（每个子智能体都会消耗令牌）。请参阅 [模型](/zh-CN/concepts/models) 和
    [子智能体](/zh-CN/tools/subagents)。

    强烈警告：较弱/过度量化的模型更容易受到提示
    注入和不安全行为的影响。请参阅 [安全性](/zh-CN/gateway/security)。

    更多背景： [模型](/zh-CN/concepts/models)。

  </Accordion>

  <Accordion title="如何在不清空配置的情况下切换模型？">
    使用**模型命令**，或只编辑**模型**字段。避免整体替换配置。

    安全选项：

    - 在聊天中使用 `/model`（快速、按会话）
    - `openclaw models set ...`（只更新模型配置）
    - `openclaw configure --section model`（交互式）
    - 编辑 `~/.openclaw/openclaw.json` 中的 `agents.defaults.model`

    除非你确实打算替换整个配置，否则不要对部分对象使用 `config.apply`。
    对于 RPC 编辑，先用 `config.schema.lookup` 检查，并优先使用 `config.patch`。lookup 返回的数据会提供规范化路径、浅层 schema 文档/约束，以及直接子项摘要，
    以便进行部分更新。
    如果你确实覆盖了配置，请从备份恢复，或重新运行 `openclaw doctor` 进行修复。

    文档： [模型](/zh-CN/concepts/models)、[配置向导](/cli/configure)、[配置](/cli/config)、[Doctor](/zh-CN/gateway/doctor)。

  </Accordion>

  <Accordion title="我可以使用自托管模型吗（llama.cpp、vLLM、Ollama）？">
    可以。Ollama 是使用本地模型最简单的路径。

    最快设置方法：

    1. 从 `https://ollama.com/download` 安装 Ollama
    2. 拉取一个本地模型，例如 `ollama pull gemma4`
    3. 如果你也想使用云模型，请运行 `ollama signin`
    4. 运行 `openclaw onboard` 并选择 `Ollama`
    5. 选择 `Local` 或 `Cloud + Local`

    说明：

    - `Cloud + Local` 会同时提供云模型和你的本地 Ollama 模型
    - 像 `kimi-k2.5:cloud` 这样的云模型不需要本地拉取
    - 如需手动切换，请使用 `openclaw models list` 和 `openclaw models set ollama/<model>`

    安全说明：更小或高度量化的模型更容易受到提示
    注入影响。对于任何可以使用工具的机器人，我们强烈建议使用**大模型**。
    如果你仍然想使用小模型，请启用沙箱隔离和严格的工具允许列表。

    文档： [Ollama](/zh-CN/providers/ollama)、[本地模型](/zh-CN/gateway/local-models)、
    [模型提供商](/zh-CN/concepts/model-providers)、[安全性](/zh-CN/gateway/security)、
    [沙箱隔离](/zh-CN/gateway/sandboxing)。

  </Accordion>

  <Accordion title="OpenClaw、Flawd 和 Krill 使用什么模型？">
    - 这些部署可能不同，而且会随时间变化；没有固定的提供商推荐。
    - 请在各自 Gateway 网关上通过 `openclaw models status` 检查当前运行时设置。
    - 对于安全敏感/启用了工具的智能体，请使用可用的最强最新一代模型。
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

    这些是内置别名。自定义别名可以通过 `agents.defaults.models` 添加。

    你可以使用 `/model`、`/model list` 或 `/model status` 查看可用模型。

    `/model`（以及 `/model list`）会显示一个紧凑的编号选择器。按编号选择：

    ```
    /model 3
    ```

    你还可以为提供商强制指定某个认证配置文件（按会话）：

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    提示：`/model status` 会显示当前活跃的是哪个智能体、正在使用哪个 `auth-profiles.json` 文件，以及接下来将尝试哪个认证配置文件。
    它还会在可用时显示已配置的提供商端点（`baseUrl`）和 API 模式（`api`）。

    **如何取消我通过 @profile 设置的固定配置文件？**

    重新运行 `/model`，**不要**带 `@profile` 后缀：

    ```
    /model anthropic/claude-opus-4-6
    ```

    如果你想回到默认值，就从 `/model` 中重新选择（或发送 `/model <默认 provider/model>`）。
    使用 `/model status` 确认当前激活的是哪个认证配置文件。

  </Accordion>

  <Accordion title="我可以用 GPT 5.2 处理日常任务、用 Codex 5.3 做编码吗？">
    可以。将其中一个设为默认值，并按需切换：

    - **快速切换（按会话）：**日常任务使用 `/model gpt-5.4`，需要通过 Codex OAuth 编码时使用 `/model openai-codex/gpt-5.4`。
    - **默认值 + 切换：**将 `agents.defaults.model.primary` 设为 `openai/gpt-5.4`，编码时再切换到 `openai-codex/gpt-5.4`（或反过来）。
    - **子智能体：**将编码任务路由到使用不同默认模型的子智能体。

    请参阅 [模型](/zh-CN/concepts/models) 和 [斜杠命令](/zh-CN/tools/slash-commands)。

  </Accordion>

  <Accordion title="如何为 GPT 5.4 配置 fast mode？">
    可以使用会话切换或配置默认值：

    - **按会话：**当当前会话使用 `openai/gpt-5.4` 或 `openai-codex/gpt-5.4` 时，发送 `/fast on`。
    - **按模型默认值：**将 `agents.defaults.models["openai/gpt-5.4"].params.fastMode` 设置为 `true`。
    - **Codex OAuth 也一样：**如果你也使用 `openai-codex/gpt-5.4`，请在那里设置相同标志。

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

    对于 OpenAI，fast mode 会在支持的原生 Responses 请求上映射为 `service_tier = "priority"`。会话中的 `/fast` 覆盖优先于配置默认值。

    请参阅 [思考与 fast mode](/zh-CN/tools/thinking) 和 [OpenAI fast mode](/zh-CN/providers/openai#openai-fast-mode)。

  </Accordion>

  <Accordion title='为什么我会看到 “Model ... is not allowed”，然后就没有回复了？'>
    如果设置了 `agents.defaults.models`，它就会成为 `/model` 和任何
    会话覆盖的**允许列表**。选择一个不在该列表中的模型会返回：

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    这个错误会**替代**正常回复返回。修复方法：把该模型加入
    `agents.defaults.models`，移除允许列表，或从 `/model list` 中选择一个模型。

  </Accordion>

  <Accordion title='为什么我会看到 “Unknown model: minimax/MiniMax-M2.7”？'>
    这意味着**提供商未配置**（找不到 MiniMax 提供商配置或认证
    配置文件），所以该模型无法解析。

    修复检查清单：

    1. 升级到当前 OpenClaw 版本（或从源码运行 `main`），然后重启 Gateway 网关。
    2. 确保已配置 MiniMax（通过向导或 JSON），或者确保环境变量/认证配置文件中存在 MiniMax 认证，
       这样相应提供商才能被注入
       （`minimax` 使用 `MINIMAX_API_KEY`，`minimax-portal` 使用 `MINIMAX_OAUTH_TOKEN` 或已存储的 MiniMax
       OAuth）。
    3. 使用与你的认证路径完全匹配的模型 id（区分大小写）：
       API 密钥配置使用 `minimax/MiniMax-M2.7` 或 `minimax/MiniMax-M2.7-highspeed`，
       OAuth 配置使用 `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed`。
    4. 运行：

       ```bash
       openclaw models list
       ```

       然后从列表中选择（或在聊天中使用 `/model list`）。

    请参阅 [MiniMax](/zh-CN/providers/minimax) 和 [模型](/zh-CN/concepts/models)。

  </Accordion>

  <Accordion title="我可以把 MiniMax 设为默认，把 OpenAI 用于复杂任务吗？">
    可以。将 **MiniMax 设为默认值**，并在需要时**按会话**切换模型。
    回退机制用于处理**错误**，而不是“更难的任务”，所以请使用 `/model` 或单独的智能体。

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

    **选项 B：使用不同智能体**

    - 智能体 A 默认：MiniMax
    - 智能体 B 默认：OpenAI
    - 通过智能体路由，或使用 `/agent` 进行切换

    文档： [模型](/zh-CN/concepts/models)、[多智能体路由](/zh-CN/concepts/multi-agent)、[MiniMax](/zh-CN/providers/minimax)、[OpenAI](/zh-CN/providers/openai)。

  </Accordion>

  <Accordion title="opus / sonnet / gpt 是内置快捷方式吗？">
    是。OpenClaw 自带一些默认简写（仅在模型存在于 `agents.defaults.models` 中时生效）：

    - `opus` → `anthropic/claude-opus-4-6`
    - `sonnet` → `anthropic/claude-sonnet-4-6`
    - `gpt` → `openai/gpt-5.4`
    - `gpt-mini` → `openai/gpt-5.4-mini`
    - `gpt-nano` → `openai/gpt-5.4-nano`
    - `gemini` → `google/gemini-3.1-pro-preview`
    - `gemini-flash` → `google/gemini-3-flash-preview`
    - `gemini-flash-lite` → `google/gemini-3.1-flash-lite-preview`

    如果你设置了同名的自定义别名，则以你的值为准。

  </Accordion>

  <Accordion title="如何定义/覆盖模型快捷方式（别名）？">
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

    然后 `/model sonnet`（或在支持时使用 `/<alias>`）就会解析到该模型 ID。

  </Accordion>

  <Accordion title="如何添加来自其他提供商的模型，比如 OpenRouter 或 Z.AI？">
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

    如果你引用了某个提供商/模型，但缺少所需的提供商密钥，你会收到运行时认证错误（例如 `No API key found for provider "zai"`）。

    **添加新智能体后提示 No API key found for provider**

    这通常意味着**新智能体**的认证存储为空。认证是按智能体区分的，
    并存储在：

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    修复方式：

    - 运行 `openclaw agents add <id>`，并在向导中配置认证。
    - 或者把主智能体 `agentDir` 中的 `auth-profiles.json` 复制到新智能体的 `agentDir` 中。

    **不要**在多个智能体之间复用 `agentDir`；这会导致认证/会话冲突。

  </Accordion>
</AccordionGroup>

## 模型故障切换和 “All models failed”

<AccordionGroup>
  <Accordion title="故障切换是如何工作的？">
    故障切换分为两个阶段：

    1. 同一提供商内的**认证配置文件轮换**。
    2. **模型回退**到 `agents.defaults.model.fallbacks` 中的下一个模型。

    对失败的配置文件会应用冷却时间（指数退避），因此即使某个提供商被限流或暂时失败，OpenClaw 仍能继续响应。

    速率限制桶不仅包含普通的 `429` 响应。OpenClaw
    还会将诸如 `Too many concurrent requests`、
    `ThrottlingException`、`concurrency limit reached`、
    `workers_ai ... quota limit exceeded`、`resource exhausted` 以及周期性
    用量窗口限制（`weekly/monthly limit reached`）等消息视为值得进行故障切换的
    速率限制。

    某些看似计费相关的响应并不是 `402`，而某些 HTTP `402`
    响应也仍然会留在那个临时故障桶中。如果提供商在 `401` 或 `403` 上返回
    明确的计费文本，OpenClaw 仍可将其保留在
    计费通道中，但提供商专属的文本匹配器仍然限定在
    拥有它们的提供商范围内（例如 OpenRouter 的 `Key limit exceeded`）。如果某个 `402`
    消息看起来像是可重试的用量窗口或
    组织/工作区支出限制（`daily limit reached, resets tomorrow`、
    `organization spending limit exceeded`），OpenClaw 会将其视为
    `rate_limit`，而不是长期计费禁用。

    上下文溢出错误则不同：像
    `request_too_large`、`input exceeds the maximum number of tokens`、
    `input token count exceeds the maximum number of input tokens`、
    `input is too long for the model` 或 `ollama error: context length
    exceeded` 这样的特征，会保留在压缩/重试路径上，而不是推进模型
    回退。

    通用服务器错误文本有意比“任何带 unknown/error 的内容”更窄。OpenClaw 确实会将提供商范围内的临时形态
    视为值得故障切换的超时/过载信号，例如 Anthropic 的裸 `An unknown error occurred`、OpenRouter 的裸
    `Provider returned error`、停止原因错误如 `Unhandled stop reason:
    error`、带有临时服务器文本的 JSON `api_error` 负载
    （`internal server error`、`unknown error, 520`、`upstream error`、`backend
    error`），以及诸如 `ModelNotReadyException` 之类的提供商繁忙错误——前提是提供商上下文
    匹配。
    而像 `LLM request failed with an unknown
    error.` 这样的通用内部回退文本则会保持保守，不会单独触发模型回退。

  </Accordion>

  <Accordion title='“No credentials found for profile anthropic:default” 是什么意思？'>
    这意味着系统尝试使用认证配置文件 ID `anthropic:default`，但在预期的认证存储中找不到对应凭证。

    **修复检查清单：**

    - **确认认证配置文件存放位置**（新路径与旧路径）
      - 当前：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
      - 旧版：`~/.openclaw/agent/*`（由 `openclaw doctor` 迁移）
    - **确认 Gateway 网关已加载你的环境变量**
      - 如果你在 shell 中设置了 `ANTHROPIC_API_KEY`，但通过 systemd/launchd 运行 Gateway 网关，它可能不会继承该变量。请将其放到 `~/.openclaw/.env` 中，或启用 `env.shellEnv`。
    - **确保你编辑的是正确的智能体**
      - 多智能体设置意味着可能存在多个 `auth-profiles.json` 文件。
    - **对模型/认证状态做基本检查**
      - 使用 `openclaw models status` 查看已配置模型，以及提供商是否已认证。

    **针对 “No credentials found for profile anthropic” 的修复检查清单**

    这意味着当前运行被固定到了一个 Anthropic 认证配置文件，但 Gateway 网关
    无法在其认证存储中找到它。

    - **使用 Claude CLI**
      - 在 Gateway 网关主机上运行 `openclaw models auth login --provider anthropic --method cli --set-default`。
    - **如果你想改用 API 密钥**
      - 将 `ANTHROPIC_API_KEY` 放入**Gateway 网关主机**上的 `~/.openclaw/.env`。
      - 清除任何强制使用缺失配置文件的固定顺序：

        ```bash
        openclaw models auth order clear --provider anthropic
        ```

    - **确认你是在 Gateway 网关主机上运行命令**
      - 在远程模式下，认证配置文件位于 Gateway 网关机器上，而不是你的笔记本电脑上。

  </Accordion>

  <Accordion title="为什么它还会尝试 Google Gemini 并失败？">
    如果你的模型配置将 Google Gemini 设为回退项（或你切换到了 Gemini 简写），OpenClaw 就会在模型回退时尝试它。如果你没有配置 Google 凭证，就会看到 `No API key found for provider "google"`。

    修复方法：要么提供 Google 认证，要么从 `agents.defaults.model.fallbacks` / 别名中移除或避免使用 Google 模型，这样回退就不会路由到那里。

    **LLM request rejected: thinking signature required（Google Antigravity）**

    原因：会话历史中包含**没有签名的 thinking 块**（通常来自
    中止/部分流式传输）。Google Antigravity 要求 thinking 块带有签名。

    修复方法：OpenClaw 现在会为 Google Antigravity Claude 移除未签名的 thinking 块。如果问题仍然出现，请开始一个**新会话**，或为该智能体设置 `/thinking off`。

  </Accordion>
</AccordionGroup>

## 认证配置文件：它是什么，以及如何管理

相关内容：[/concepts/oauth](/zh-CN/concepts/oauth)（OAuth 流程、令牌存储、多账号模式）

<AccordionGroup>
  <Accordion title="什么是认证配置文件？">
    认证配置文件是与某个提供商绑定的命名凭证记录（OAuth 或 API 密钥）。配置文件存放在：

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

  </Accordion>

  <Accordion title="常见的配置文件 ID 是什么样的？">
    OpenClaw 使用带提供商前缀的 ID，例如：

    - `anthropic:default`（当没有邮箱身份时很常见）
    - `anthropic:<email>` 用于 OAuth 身份
    - 你自定义的 ID（例如 `anthropic:work`）

  </Accordion>

  <Accordion title="我可以控制优先尝试哪个认证配置文件吗？">
    可以。配置支持配置文件的可选元数据以及按提供商划分的顺序（`auth.order.<provider>`）。这**不会**存储密钥；它只是把 ID 映射到提供商/模式，并设置轮换顺序。

    如果某个配置文件处于短暂**冷却**状态（速率限制/超时/认证失败）或较长的**禁用**状态（计费/额度不足），OpenClaw 可能会临时跳过它。要检查这一点，请运行 `openclaw models status --json` 并查看 `auth.unusableProfiles`。调优项：`auth.cooldowns.billingBackoffHours*`。

    速率限制冷却可以限定到模型范围。一个配置文件如果只对某个模型处于冷却中，
    对同一提供商下的兄弟模型仍可能可用，
    但计费/禁用窗口仍会阻止整个配置文件。

    你还可以通过 CLI 设置**按智能体**的顺序覆盖（存储在该智能体的 `auth-state.json` 中）：

    ```bash
    # 默认为已配置的默认智能体（省略 --agent）
    openclaw models auth order get --provider anthropic

    # 将轮换锁定为单个配置文件（只尝试这个）
    openclaw models auth order set --provider anthropic anthropic:default

    # 或设置一个显式顺序（提供商内部回退）
    openclaw models auth order set --provider anthropic anthropic:work anthropic:default

    # 清除覆盖（回退到配置中的 auth.order / 轮询）
    openclaw models auth order clear --provider anthropic
    ```

    目标指定到某个智能体：

    ```bash
    openclaw models auth order set --provider anthropic --agent main anthropic:default
    ```

    若要验证实际会尝试什么，请使用：

    ```bash
    openclaw models status --probe
    ```

    如果某个已存储的配置文件未包含在显式顺序中，probe 会对该配置文件报告
    `excluded_by_auth_order`，而不是静默尝试它。

  </Accordion>

  <Accordion title="OAuth 和 API 密钥有什么区别？">
    OpenClaw 两者都支持：

    - **OAuth** 通常会利用订阅访问权限（在适用时）。
    - **API 密钥** 使用按 token 计费。

    向导明确支持 Anthropic Claude CLI、OpenAI Codex OAuth 和 API 密钥。

  </Accordion>
</AccordionGroup>

## Gateway 网关：端口、“already running”和远程模式

<AccordionGroup>
  <Accordion title="Gateway 网关使用哪个端口？">
    `gateway.port` 控制单一复用端口，供 WebSocket + HTTP（Control UI、hooks 等）使用。

    优先级：

    ```
    --port > OPENCLAW_GATEWAY_PORT > gateway.port > 默认 18789
    ```

  </Accordion>

  <Accordion title='为什么 openclaw gateway status 显示 “Runtime: running”，但 “RPC probe: failed”？'>
    因为 “running” 是**监督器**的视角（launchd/systemd/schtasks）。而 RPC probe 是 CLI 实际连接到 Gateway 网关 WebSocket 并调用 `status`。

    使用 `openclaw gateway status`，并重点看这些行：

    - `Probe target:`（探测实际使用的 URL）
    - `Listening:`（端口上实际绑定的内容）
    - `Last gateway error:`（当进程存活但端口未监听时的常见根因）

  </Accordion>

  <Accordion title='为什么 openclaw gateway status 显示 “Config (cli)” 和 “Config (service)” 不同？'>
    你编辑的是一个配置文件，而服务实际运行的是另一个配置文件（通常是 `--profile` / `OPENCLAW_STATE_DIR` 不匹配）。

    修复方法：

    ```bash
    openclaw gateway install --force
    ```

    请在你希望服务使用的同一个 `--profile` / 环境下运行该命令。

  </Accordion>

  <Accordion title='“another gateway instance is already listening” 是什么意思？'>
    OpenClaw 会在启动时立即绑定 WebSocket 监听器（默认 `ws://127.0.0.1:18789`），以强制实现运行时锁。如果绑定因 `EADDRINUSE` 失败，就会抛出 `GatewayLockError`，表示已有另一个实例正在监听。

    修复方法：停止另一个实例，释放端口，或使用 `openclaw gateway --port <port>` 运行。

  </Accordion>

  <Accordion title="如何在远程模式下运行 OpenClaw（客户端连接到其他地方的 Gateway 网关）？">
    设置 `gateway.mode: "remote"`，并指向远程 WebSocket URL；你也可以选择性地附带共享密钥远程凭证：

    ```json5
    {
      gateway: {
        mode: "remote",
        remote: {
          url: "ws://gateway.tailnet:18789",
          token: "your-token",
          password: "your-password",
        },
      },
    }
    ```

    说明：

    - 只有当 `gateway.mode` 为 `local` 时，`openclaw gateway` 才会启动（或者你显式传入覆盖标志）。
    - macOS 应用会监视配置文件，并在这些值变更时实时切换模式。
    - `gateway.remote.token` / `.password` 只是客户端侧的远程凭证；它们本身不会启用本地 Gateway 网关认证。

  </Accordion>

  <Accordion title='Control UI 显示 “unauthorized”（或者不断重连）。现在怎么办？'>
    你的 Gateway 网关认证路径与 UI 的认证方式不匹配。

    事实（来自代码）：

    - Control UI 会将令牌保存在当前浏览器标签页会话和所选 Gateway 网关 URL 对应的 `sessionStorage` 中，因此同一标签页刷新后仍可正常工作，而无需恢复长期的 `localStorage` 令牌持久化。
    - 在出现 `AUTH_TOKEN_MISMATCH` 时，受信任客户端可以在 Gateway 网关返回重试提示（`canRetryWithDeviceToken=true`、`recommendedNextStep=retry_with_device_token`）后，使用缓存的设备令牌进行一次有界重试。
    - 该缓存令牌重试现在会复用与设备令牌一起存储的已批准作用域。显式的 `deviceToken` / 显式 `scopes` 调用方仍会保留它们请求的作用域集合，而不是继承缓存作用域。
    - 在该重试路径之外，连接认证优先级依次为：显式共享令牌/密码、显式 `deviceToken`、已存储设备令牌、bootstrap 令牌。
    - Bootstrap 令牌的作用域检查带有角色前缀。内置 bootstrap operator 允许列表只满足 operator 请求；节点或其他非 operator 角色仍需要各自角色前缀下的作用域。

    修复方法：

    - 最快方式：`openclaw dashboard`（会打印并复制仪表板 URL，尝试打开；若为无头环境会显示 SSH 提示）。
    - 如果你还没有令牌：`openclaw doctor --generate-gateway-token`。
    - 如果是远程环境，先建立隧道：`ssh -N -L 18789:127.0.0.1:18789 user@host`，然后打开 `http://127.0.0.1:18789/`。
    - 共享密钥模式：设置 `gateway.auth.token` / `OPENCLAW_GATEWAY_TOKEN`，或 `gateway.auth.password` / `OPENCLAW_GATEWAY_PASSWORD`，然后在 Control UI 设置中粘贴匹配的密钥。
    - Tailscale Serve 模式：确保已启用 `gateway.auth.allowTailscale`，并且你打开的是 Serve URL，而不是会绕过 Tailscale 身份标头的原始 loopback/tailnet URL。
    - trusted-proxy 模式：确保你是通过已配置的非 loopback 身份感知代理访问，而不是通过同主机 loopback 代理或原始 Gateway 网关 URL。
    - 如果在那一次重试后仍然不匹配，请轮换/重新批准已配对的设备令牌：
      - `openclaw devices list`
      - `openclaw devices rotate --device <id> --role operator`
    - 如果该 rotate 调用提示被拒绝，请检查两点：
      - 已配对设备会话只能轮换**自己的**设备，除非它们还具备 `operator.admin`
      - 显式 `--scope` 值不能超过调用方当前的 operator 作用域
    - 如果还是卡住？运行 `openclaw status --all`，并按照 [故障排除](/zh-CN/gateway/troubleshooting) 继续处理。认证详情请参阅 [仪表板](/web/dashboard)。

  </Accordion>

  <Accordion title="我设置了 gateway.bind tailnet，但它无法绑定，且没有任何监听">
    `tailnet` 绑定会从你的网络接口中选择一个 Tailscale IP（100.64.0.0/10）。如果该机器未加入 Tailscale（或接口已断开），就没有可绑定的地址。

    修复方法：

    - 在该主机上启动 Tailscale（使其获得一个 100.x 地址），或者
    - 切换到 `gateway.bind: "loopback"` / `"lan"`。

    说明：`tailnet` 是显式的。`auto` 会优先选择 loopback；当你希望只绑定到 tailnet 时，请使用 `gateway.bind: "tailnet"`。

  </Accordion>

  <Accordion title="我可以在同一台主机上运行多个 Gateway 网关吗？">
    通常不需要——一个 Gateway 网关就可以运行多个消息渠道和智能体。只有在你需要冗余（例如救援机器人）或硬隔离时，才使用多个 Gateway 网关。

    可以，但你必须隔离以下内容：

    - `OPENCLAW_CONFIG_PATH`（每个实例各自配置）
    - `OPENCLAW_STATE_DIR`（每个实例各自状态）
    - `agents.defaults.workspace`（工作区隔离）
    - `gateway.port`（唯一端口）

    快速设置（推荐）：

    - 每个实例使用 `openclaw --profile <name> ...`（会自动创建 `~/.openclaw-<name>`）。
    - 在每个配置文件中设置唯一的 `gateway.port`（或手动运行时传入 `--port`）。
    - 安装按 profile 区分的服务：`openclaw --profile <name> gateway install`。

    配置文件还会给服务名添加后缀（`ai.openclaw.<profile>`；旧版为 `com.openclaw.*`、`openclaw-gateway-<profile>.service`、`OpenClaw Gateway (<profile>)`）。
    完整指南： [多个 Gateway 网关](/zh-CN/gateway/multiple-gateways)。

  </Accordion>

  <Accordion title='“invalid handshake” / code 1008 是什么意思？'>
    Gateway 网关是一个**WebSocket 服务器**，它要求收到的第一条消息
    必须是 `connect` 帧。如果收到其他任何内容，它就会关闭连接，
    并返回 **code 1008**（策略违规）。

    常见原因：

    - 你在浏览器中打开了 **HTTP** URL（`http://...`），而不是使用 WS 客户端。
    - 你用了错误的端口或路径。
    - 代理或隧道剥离了认证标头，或发送了非 Gateway 网关请求。

    快速修复：

    1. 使用 WS URL：`ws://<host>:18789`（如果是 HTTPS，则使用 `wss://...`）。
    2. 不要在普通浏览器标签页中打开 WS 端口。
    3. 如果启用了认证，请在 `connect` 帧中包含令牌/密码。

    如果你使用 CLI 或 TUI，URL 应该如下所示：

    ```
    openclaw tui --url ws://<host>:18789 --token <token>
    ```

    协议详情： [Gateway 网关协议](/zh-CN/gateway/protocol)。

  </Accordion>
</AccordionGroup>

## 日志与调试

<AccordionGroup>
  <Accordion title="日志在哪里？">
    文件日志（结构化）：

    ```
    /tmp/openclaw/openclaw-YYYY-MM-DD.log
    ```

    你可以通过 `logging.file` 设置固定路径。文件日志级别由 `logging.level` 控制。控制台详细程度由 `--verbose` 和 `logging.consoleLevel` 控制。

    查看日志的最快方式：

    ```bash
    openclaw logs --follow
    ```

    服务/监督器日志（当 Gateway 网关通过 launchd/systemd 运行时）：

    - macOS：`$OPENCLAW_STATE_DIR/logs/gateway.log` 和 `gateway.err.log`（默认：`~/.openclaw/logs/...`；profile 使用 `~/.openclaw-<profile>/logs/...`）
    - Linux：`journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
    - Windows：`schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

    更多信息请参阅 [故障排除](/zh-CN/gateway/troubleshooting)。

  </Accordion>

  <Accordion title="如何启动/停止/重启 Gateway 网关服务？">
    使用 Gateway 网关辅助命令：

    ```bash
    openclaw gateway status
    openclaw gateway restart
    ```

    如果你是手动运行 Gateway 网关，`openclaw gateway --force` 可以夺回端口。请参阅 [Gateway 网关](/zh-CN/gateway)。

  </Accordion>

  <Accordion title="我在 Windows 上关闭了终端——如何重启 OpenClaw？">
    Windows 有**两种安装模式**：

    **1）WSL2（推荐）：**Gateway 网关运行在 Linux 内部。

    打开 PowerShell，进入 WSL，然后重启：

    ```powershell
    wsl
    openclaw gateway status
    openclaw gateway restart
    ```

    如果你从未安装服务，请以前台方式启动它：

    ```bash
    openclaw gateway run
    ```

    **2）原生 Windows（不推荐）：**Gateway 网关直接运行在 Windows 中。

    打开 PowerShell 并运行：

    ```powershell
    openclaw gateway status
    openclaw gateway restart
    ```

    如果你是手动运行它（没有服务），请使用：

    ```powershell
    openclaw gateway run
    ```

    文档： [Windows（WSL2）](/zh-CN/platforms/windows)、[Gateway 网关服务运行手册](/zh-CN/gateway)。

  </Accordion>

  <Accordion title="Gateway 网关已经启动，但回复始终收不到。我该检查什么？">
    先做一次快速健康检查：

    ```bash
    openclaw status
    openclaw models status
    openclaw channels status
    openclaw logs --follow
    ```

    常见原因：

    - Gateway 网关主机上的模型认证未加载（检查 `models status`）。
    - 渠道配对/允许列表阻止了回复（检查渠道配置 + 日志）。
    - WebChat/仪表板已打开，但没有使用正确令牌。

    如果你是远程环境，请确认隧道/Tailscale 连接正常，并且
    Gateway 网关 WebSocket 可达。

    文档： [渠道](/zh-CN/channels)、[故障排除](/zh-CN/gateway/troubleshooting)、[远程访问](/zh-CN/gateway/remote)。

  </Accordion>

  <Accordion title='"Disconnected from gateway: no reason"——现在怎么办？'>
    这通常意味着 UI 丢失了 WebSocket 连接。请检查：

    1. Gateway 网关正在运行吗？`openclaw gateway status`
    2. Gateway 网关健康吗？`openclaw status`
    3. UI 是否使用了正确令牌？`openclaw dashboard`
    4. 如果是远程环境，隧道/Tailscale 链路是否正常？

    然后查看日志：

    ```bash
    openclaw logs --follow
    ```

    文档： [仪表板](/web/dashboard)、[远程访问](/zh-CN/gateway/remote)、[故障排除](/zh-CN/gateway/troubleshooting)。

  </Accordion>

  <Accordion title="Telegram setMyCommands 失败了。我该检查什么？">
    先从日志和渠道状态开始：

    ```bash
    openclaw channels status
    openclaw channels logs --channel telegram
    ```

    然后对照错误：

    - `BOT_COMMANDS_TOO_MUCH`：Telegram 菜单项太多。OpenClaw 已经会裁剪到 Telegram 限制并用更少命令重试，但某些菜单项仍需删除。请减少插件/Skill/自定义命令，或在你不需要菜单时禁用 `channels.telegram.commands.native`。
    - `TypeError: fetch failed`、`Network request for 'setMyCommands' failed!` 或类似网络错误：如果你在 VPS 上或通过代理运行，请确认允许对 `api.telegram.org` 的出站 HTTPS 访问，并且 DNS 正常工作。

    如果 Gateway 网关是远程的，请确保你查看的是 Gateway 网关主机上的日志。

    文档： [Telegram](/zh-CN/channels/telegram)、[渠道故障排除](/zh-CN/channels/troubleshooting)。

  </Accordion>

  <Accordion title="TUI 没有输出。我该检查什么？">
    先确认 Gateway 网关可达，并且智能体可以运行：

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    在 TUI 中，使用 `/status` 查看当前状态。如果你期望回复发送到某个聊天
    渠道，请确保已启用投递（`/deliver on`）。

    文档： [TUI](/web/tui)、[斜杠命令](/zh-CN/tools/slash-commands)。

  </Accordion>

  <Accordion title="如何彻底停止然后重新启动 Gateway 网关？">
    如果你已安装服务：

    ```bash
    openclaw gateway stop
    openclaw gateway start
    ```

    这会停止/启动**受监督服务**（macOS 上是 launchd，Linux 上是 systemd）。
    当 Gateway 网关作为后台守护进程运行时，请使用这种方式。

    如果你是在前台运行，请用 Ctrl-C 停止，然后执行：

    ```bash
    openclaw gateway run
    ```

    文档： [Gateway 网关服务运行手册](/zh-CN/gateway)。

  </Accordion>

  <Accordion title="用最简单的话解释：openclaw gateway restart 和 openclaw gateway 有什么区别？">
    - `openclaw gateway restart`：重启**后台服务**（launchd/systemd）。
    - `openclaw gateway`：在当前终端会话中**前台**运行 Gateway 网关。

    如果你安装了服务，请使用 gateway 命令。只有在
    你想进行一次性的前台运行时，才使用 `openclaw gateway`。

  </Accordion>

  <Accordion title="出错时，最快获取更多细节的方法是什么？">
    用 `--verbose` 启动 Gateway 网关，以获得更多控制台细节。然后检查日志文件，查看渠道认证、模型路由和 RPC 错误。
  </Accordion>
</AccordionGroup>

## 媒体和附件

<AccordionGroup>
  <Accordion title="我的 Skill 生成了图片/PDF，但没有发送任何内容">
    来自智能体的出站附件必须包含一行 `MEDIA:<path-or-url>`（单独占一行）。请参阅 [OpenClaw 助手设置](/zh-CN/start/openclaw) 和 [智能体发送](/zh-CN/tools/agent-send)。

    CLI 发送方式：

    ```bash
    openclaw message send --target +15555550123 --message "Here you go" --media /path/to/file.png
    ```

    还要检查：

    - 目标渠道支持出站媒体，并且未被允许列表阻止。
    - 文件未超过提供商的大小限制（图片会被缩放到最大 2048px）。
    - `tools.fs.workspaceOnly=true` 会将本地路径发送限制在工作区、temp/media-store 和经沙箱验证的文件内。
    - `tools.fs.workspaceOnly=false` 允许 `MEDIA:` 发送智能体已经可以读取的主机本地文件，但仅限媒体和安全文档类型（图片、音频、视频、PDF 和 Office 文档）。纯文本和类似密钥的文件仍会被阻止。

    请参阅 [图片](/zh-CN/nodes/images)。

  </Accordion>
</AccordionGroup>

## 安全性和访问控制

<AccordionGroup>
  <Accordion title="将 OpenClaw 暴露给入站私信安全吗？">
    请将入站私信视为不可信输入。默认行为的设计目标就是降低风险：

    - 支持私信的渠道默认行为是**配对**：
      - 未知发送者会收到一个配对码；机器人不会处理他们的消息。
      - 使用以下命令批准：`openclaw pairing approve --channel <channel> [--account <id>] <code>`
      - 每个渠道的待处理请求上限为 **3 个**；如果没有收到配对码，请检查 `openclaw pairing list --channel <channel> [--account <id>]`。
    - 公开开放私信需要显式选择加入（`dmPolicy: "open"` 且允许列表为 `"*"`）。

    运行 `openclaw doctor` 可以发现存在风险的私信策略。

  </Accordion>

  <Accordion title="提示注入只对公开机器人构成风险吗？">
    不是。提示注入关乎的是**不可信内容**，而不只是“谁可以给机器人发私信”。
    如果你的助手会读取外部内容（Web 搜索/抓取、浏览器页面、电子邮件、
    文档、附件、粘贴的日志），这些内容就可能包含试图
    劫持模型的指令。即使**你是唯一发送者**，这种情况也会发生。

    最大的风险来自启用了工具时：模型可能被诱导去
    泄露上下文，或代表你调用工具。降低影响范围的方法包括：

    - 使用只读或禁用工具的“阅读器”智能体来总结不可信内容
    - 对启用了工具的智能体关闭 `web_search` / `web_fetch` / `browser`
    - 将解码后的文件/文档文本也视为不可信：OpenResponses
      `input_file` 和媒体附件提取都会将提取文本包装在
      明确的外部内容边界标记中，而不是直接传递原始文件文本
    - 使用沙箱隔离和严格的工具允许列表

    详情： [安全性](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="我的机器人是否应该使用自己的邮箱、GitHub 账号或电话号码？">
    对于大多数设置来说，是的。通过独立的账号和电话号码隔离机器人，
    可以在出问题时降低影响范围。这也会让你更容易轮换
    凭证或撤销访问，而不会影响你的个人账号。

    从小范围开始。只授予真正需要的工具和账号访问权限，
    如果后续有需要再逐步扩展。

    文档： [安全性](/zh-CN/gateway/security)、[配对](/zh-CN/channels/pairing)。

  </Accordion>

  <Accordion title="我可以让它自主处理我的短信吗？这样安全吗？">
    我们**不建议**让它对你的个人消息拥有完全自主权。最安全的模式是：

    - 让私信保持在**配对模式**或严格允许列表模式下。
    - 如果你希望它代表你发消息，请使用**单独的号码或账号**。
    - 让它先起草，然后**在发送前审批**。

    如果你想尝试，请在专用账号上进行，并保持隔离。请参阅
    [安全性](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="我可以为个人助理任务使用更便宜的模型吗？">
    可以，**前提是**该智能体仅用于聊天，且输入是可信的。更小档位的模型
    更容易受到指令劫持影响，因此对于启用了工具的智能体
    或需要读取不可信内容的场景，不建议使用。如果你必须使用更小的模型，请锁定
    工具，并在沙箱中运行。请参阅 [安全性](/zh-CN/gateway/security)。
  </Accordion>

  <Accordion title="我在 Telegram 里运行了 /start，但没有收到配对码">
    只有当未知发送者给机器人发消息，并且
    启用了 `dmPolicy: "pairing"` 时，才会发送配对码。单独执行 `/start` 不会生成配对码。

    检查待处理请求：

    ```bash
    openclaw pairing list telegram
    ```

    如果你想立即获得访问权限，请将你的发送者 id 加入允许列表，或为该账号设置 `dmPolicy: "open"`。

  </Accordion>

  <Accordion title="WhatsApp：它会给我的联系人发消息吗？配对是如何工作的？">
    不会。WhatsApp 默认私信策略是**配对**。未知发送者只会收到一个配对码，而且他们的消息**不会被处理**。OpenClaw 只会回复它收到的聊天，或你显式触发的发送。

    使用以下命令批准配对：

    ```bash
    openclaw pairing approve whatsapp <code>
    ```

    列出待处理请求：

    ```bash
    openclaw pairing list whatsapp
    ```

    向导中的电话号码提示：它用于设置你的**允许列表/所有者**，从而允许你自己的私信。它不会用于自动发送。如果你使用的是自己的个人 WhatsApp 号码，请使用该号码，并启用 `channels.whatsapp.selfChatMode`。

  </Accordion>
</AccordionGroup>

## 聊天命令、终止任务，以及“它就是不停下来”

<AccordionGroup>
  <Accordion title="如何阻止内部系统消息显示在聊天中？">
    大多数内部消息或工具消息只会在该会话启用了 **verbose**、**trace** 或 **reasoning** 时显示。

    在出现问题的聊天中这样修复：

    ```
    /verbose off
    /trace off
    /reasoning off
    ```

    如果仍然很吵，请检查 Control UI 中的会话设置，并将 verbose
    设为 **inherit**。同时确认你没有使用配置中将 `verboseDefault` 设为
    `on` 的机器人配置文件。

    文档： [思考与 verbose](/zh-CN/tools/thinking)、[安全性](/zh-CN/gateway/security#reasoning-verbose-output-in-groups)。

  </Accordion>

  <Accordion title="如何停止/取消一个正在运行的任务？">
    将以下任一内容**作为独立消息发送**（不带斜杠）：

    ```
    stop
    stop action
    stop current action
    stop run
    stop current run
    stop agent
    stop the agent
    stop openclaw
    openclaw stop
    stop don't do anything
    stop do not do anything
    stop doing anything
    please stop
    stop please
    abort
    esc
    wait
    exit
    interrupt
    ```

    这些是中止触发词（不是斜杠命令）。

    对于后台进程（来自 exec 工具），你可以让智能体运行：

    ```
    process action:kill sessionId:XXX
    ```

    斜杠命令概览：请参阅 [斜杠命令](/zh-CN/tools/slash-commands)。

    大多数命令都必须作为**以 `/` 开头的独立消息**发送，但少数快捷方式（如 `/status`）对于在允许列表中的发送者也支持内联使用。

  </Accordion>

  <Accordion title='如何从 Telegram 发送 Discord 消息？（“Cross-context messaging denied”）'>
    OpenClaw 默认会阻止**跨提供商**消息发送。如果某次工具调用绑定到了
    Telegram，除非你显式允许，否则它不会发送到 Discord。

    为该智能体启用跨提供商消息发送：

    ```json5
    {
      tools: {
        message: {
          crossContext: {
            allowAcrossProviders: true,
            marker: { enabled: true, prefix: "[from {channel}] " },
          },
        },
      },
    }
    ```

    编辑配置后重启 Gateway 网关。

  </Accordion>

  <Accordion title='为什么感觉机器人会“忽略”连续快速发送的消息？'>
    队列模式决定了新消息如何与正在运行中的任务交互。使用 `/queue` 切换模式：

    - `steer` - 新消息会重定向当前任务
    - `followup` - 消息按顺序一个个执行
    - `collect` - 批量收集消息后统一回复（默认）
    - `steer-backlog` - 先重定向当前任务，再处理积压消息
    - `interrupt` - 中止当前运行并重新开始

    你还可以添加选项，例如 `debounce:2s cap:25 drop:summarize`，用于 followup 模式。

  </Accordion>
</AccordionGroup>

## 杂项

<AccordionGroup>
  <Accordion title='Anthropic 搭配 API 密钥时的默认模型是什么？'>
    在 OpenClaw 中，凭证和模型选择是分开的。设置 `ANTHROPIC_API_KEY`（或在认证配置文件中存储 Anthropic API 密钥）会启用认证，但实际默认模型取决于你在 `agents.defaults.model.primary` 中的配置（例如 `anthropic/claude-sonnet-4-6` 或 `anthropic/claude-opus-4-6`）。如果你看到 `No credentials found for profile "anthropic:default"`，这意味着 Gateway 网关无法在当前运行智能体所对应的 `auth-profiles.json` 中找到 Anthropic 凭证。
  </Accordion>
</AccordionGroup>

---

还是卡住了？请到 [Discord](https://discord.com/invite/clawd) 提问，或发起一个 [GitHub discussion](https://github.com/openclaw/openclaw/discussions)。
