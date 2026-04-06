---
read_when:
    - 回答常见的设置、安装、新手引导或运行时支持问题
    - 在深入调试前对用户报告的问题进行初步分流
summary: 关于 OpenClaw 设置、配置和使用的常见问题解答
title: 常见问题
x-i18n:
    generated_at: "2026-04-06T15:34:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: bddcde55cf4bcec4913aadab4c665b235538104010e445e4c99915a1672b1148
    source_path: help/faq.md
    workflow: 15
---

# 常见问题

提供快速解答，以及适用于真实环境的更深入故障排除（本地开发、VPS、多智能体、OAuth / API 密钥、模型故障切换）。有关运行时诊断，请参见 [故障排除](/zh-CN/gateway/troubleshooting)。有关完整配置参考，请参见 [配置](/zh-CN/gateway/configuration)。

## 如果出了问题，最初的六十秒

1. **快速状态（第一项检查）**

   ```bash
   openclaw status
   ```

   快速本地摘要：操作系统 + 更新、Gateway 网关 / 服务可达性、智能体 / 会话、提供商配置 + 运行时问题（当 Gateway 网关可达时）。

2. **可粘贴的报告（可安全分享）**

   ```bash
   openclaw status --all
   ```

   只读诊断，附带日志尾部（令牌已打码）。

3. **守护进程 + 端口状态**

   ```bash
   openclaw gateway status
   ```

   显示监督器运行时与 RPC 可达性、探测目标 URL，以及服务可能使用了哪个配置。

4. **深度探测**

   ```bash
   openclaw status --deep
   ```

   运行实时 Gateway 网关健康探测，包括支持时的渠道探测
   （需要可访问的 Gateway 网关）。参见 [健康状态](/zh-CN/gateway/health)。

5. **查看最新日志**

   ```bash
   openclaw logs --follow
   ```

   如果 RPC 不可用，则退回到：

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   文件日志与服务日志是分开的；参见 [日志记录](/zh-CN/logging) 和 [故障排除](/zh-CN/gateway/troubleshooting)。

6. **运行 Doctor（修复）**

   ```bash
   openclaw doctor
   ```

   修复 / 迁移配置 / 状态并运行健康检查。参见 [Doctor](/zh-CN/gateway/doctor)。

7. **Gateway 网关快照**

   ```bash
   openclaw health --json
   openclaw health --verbose   # 出错时显示目标 URL + 配置路径
   ```

   向正在运行的 Gateway 网关请求完整快照（仅 WS）。参见 [健康状态](/zh-CN/gateway/health)。

## 快速开始与首次运行设置

<AccordionGroup>
  <Accordion title="我卡住了，最快如何解决问题">
    使用能够**看到你的机器**的本地 AI 智能体。这比在 Discord 里提问要有效得多，
    因为大多数“我卡住了”的情况都是**本地配置或环境问题**，
    远程帮助者无法直接检查。

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    这些工具可以读取仓库、运行命令、检查日志，并帮助修复你机器级别的
    设置问题（PATH、服务、权限、凭证文件）。请通过可修改的
    hackable（git）安装方式，把**完整源码检出**提供给它们：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    这会从 **git 检出**安装 OpenClaw，因此智能体可以读取代码 + 文档，
    并基于你正在运行的确切版本进行推理。你之后始终可以通过重新运行安装器、
    并去掉 `--install-method git` 切回稳定版。

    提示：让智能体先**规划并监督**修复过程（逐步进行），然后只执行必要的
    命令。这样能让变更保持较小，也更容易审计。

    如果你发现了真实的 bug 或修复，请提交 GitHub issue 或发送 PR：
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    先从这些命令开始（寻求帮助时请附上输出）：

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    它们的作用：

    - `openclaw status`：快速查看 Gateway 网关 / 智能体健康状态 + 基本配置。
    - `openclaw models status`：检查提供商凭证 + 模型可用性。
    - `openclaw doctor`：验证并修复常见配置 / 状态问题。

    其他有用的 CLI 检查：`openclaw status --all`、`openclaw logs --follow`、
    `openclaw gateway status`、`openclaw health --verbose`。

    快速调试循环：[如果出了问题，最初的六十秒](#first-60-seconds-if-something-is-broken)。
    安装文档：[安装](/zh-CN/install)、[安装器标志](/zh-CN/install/installer)、[更新](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="Heartbeat 一直跳过。跳过原因分别是什么意思？">
    常见的 Heartbeat 跳过原因：

    - `quiet-hours`：不在配置的活跃时间窗口内
    - `empty-heartbeat-file`：`HEARTBEAT.md` 存在，但仅包含空白 / 只有标题的脚手架内容
    - `no-tasks-due`：`HEARTBEAT.md` 任务模式已启用，但尚无任何任务间隔到期
    - `alerts-disabled`：所有 heartbeat 可见性均已禁用（`showOk`、`showAlerts` 和 `useIndicator` 全部关闭）

    在任务模式下，只有在一次真实 heartbeat 运行完成后，任务的到期时间戳才会推进。
    被跳过的运行不会将任务标记为已完成。

    文档：[Heartbeat](/zh-CN/gateway/heartbeat)、[自动化与任务](/zh-CN/automation)。

  </Accordion>

  <Accordion title="安装并设置 OpenClaw 的推荐方式">
    仓库推荐从源码运行，并使用新手引导：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    向导也可以自动构建 UI 资源。完成新手引导后，你通常会在 **18789** 端口运行 Gateway 网关。

    从源码开始（贡献者 / 开发者）：

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # 首次运行时自动安装 UI 依赖
    openclaw onboard
    ```

    如果你还没有全局安装，可以通过 `pnpm openclaw onboard` 运行它。

  </Accordion>

  <Accordion title="新手引导后如何打开仪表盘？">
    向导会在新手引导完成后立即使用一个干净的（非 token 化）仪表盘 URL 打开你的浏览器，并在摘要中打印该链接。请保持该标签页打开；如果它没有自动启动，请在同一台机器上复制 / 粘贴打印出的 URL。
  </Accordion>

  <Accordion title="如何在 localhost 与远程环境中为仪表盘进行身份验证？">
    **localhost（同一台机器）：**

    - 打开 `http://127.0.0.1:18789/`。
    - 如果它要求共享密钥身份验证，请将已配置的 token 或密码粘贴到 Control UI 设置中。
    - Token 来源：`gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
    - 密码来源：`gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
    - 如果尚未配置共享密钥，可使用 `openclaw doctor --generate-gateway-token` 生成 token。

    **不在 localhost 上：**

    - **Tailscale Serve**（推荐）：保持绑定 loopback，运行 `openclaw gateway --tailscale serve`，打开 `https://<magicdns>/`。如果 `gateway.auth.allowTailscale` 为 `true`，身份标头将满足 Control UI / WebSocket 身份验证要求（无需粘贴共享密钥，默认信任 Gateway 网关主机）；HTTP API 仍然需要共享密钥身份验证，除非你明确使用私有入口 `none` 或受信任代理 HTTP 身份验证。
      来自同一客户端的并发 Serve 错误身份验证尝试，会在失败身份验证限速器记录之前被串行化，因此第二次错误重试可能已经显示 `retry later`。
    - **Tailnet 绑定**：运行 `openclaw gateway --bind tailnet --token "<token>"`（或配置密码身份验证），打开 `http://<tailscale-ip>:18789/`，然后在仪表盘设置中粘贴对应的共享密钥。
    - **具身份感知的反向代理**：将 Gateway 网关放在非 loopback 的受信任代理之后，配置 `gateway.auth.mode: "trusted-proxy"`，然后打开代理 URL。
    - **SSH 隧道**：`ssh -N -L 18789:127.0.0.1:18789 user@host`，然后打开 `http://127.0.0.1:18789/`。通过隧道时仍适用共享密钥身份验证；如果出现提示，请粘贴已配置的 token 或密码。

    参见 [仪表盘](/web/dashboard) 和 [Web 界面](/web) 了解绑定模式与身份验证细节。

  </Accordion>

  <Accordion title="为什么聊天审批会有两个 exec approval 配置？">
    它们控制的是不同层级：

    - `approvals.exec`：将审批提示转发到聊天目的地
    - `channels.<channel>.execApprovals`：使该渠道充当 exec 审批的原生审批客户端

    主机 exec 策略仍然是真正的审批门槛。聊天配置只控制审批提示
    出现在什么地方，以及人们如何回复它们。

    在大多数设置中，你**不需要**同时使用两者：

    - 如果聊天本身已经支持命令和回复，那么同一聊天内的 `/approve` 会通过共享路径工作。
    - 如果某个受支持的原生渠道可以安全推断审批人，而 `channels.<channel>.execApprovals.enabled` 未设置或为 `"auto"`，OpenClaw 现在会自动启用“优先私信”的原生审批。
    - 当存在原生审批卡片 / 按钮时，该原生 UI 是主路径；只有在工具结果表明聊天审批不可用或手动审批是唯一方式时，智能体才应包含手动 `/approve` 命令。
    - 仅当提示还必须转发到其他聊天或明确的运维房间时，才使用 `approvals.exec`。
    - 仅当你明确希望将审批提示回发到原始房间 / 主题时，才使用 `channels.<channel>.execApprovals.target: "channel"` 或 `"both"`。
    - 插件审批则再次独立：它们默认使用同一聊天内的 `/approve`，可选 `approvals.plugin` 转发，并且只有部分原生渠道会在此之上保留原生插件审批处理。

    简而言之：转发用于路由，原生客户端配置用于提供更丰富的渠道特定 UX。
    参见 [Exec 审批](/zh-CN/tools/exec-approvals)。

  </Accordion>

  <Accordion title="我需要什么运行时？">
    需要 Node **>= 22**。推荐使用 `pnpm`。Gateway 网关**不推荐**使用 Bun。
  </Accordion>

  <Accordion title="它能在 Raspberry Pi 上运行吗？">
    可以。Gateway 网关很轻量——文档中写明个人使用场景下 **512 MB - 1 GB 内存**、**1 核**、约 **500 MB**
    磁盘就足够，并注明 **Raspberry Pi 4 可以运行它**。

    如果你想要更多余量（日志、媒体、其他服务），推荐 **2 GB**，但
    这并不是硬性最低要求。

    提示：小型 Pi / VPS 可以托管 Gateway 网关，而你可以在笔记本 / 手机上配对 **节点**，用于
    本地屏幕 / 摄像头 / Canvas 或命令执行。参见 [节点](/zh-CN/nodes)。

  </Accordion>

  <Accordion title="安装 Raspberry Pi 版有什么建议吗？">
    简短回答：能用，但要预期会有一些粗糙边缘。

    - 使用 **64 位**操作系统，并保持 Node >= 22。
    - 优先使用 **hackable（git）安装**，这样你可以查看日志并快速更新。
    - 先在没有渠道 / Skills 的情况下启动，然后逐个添加。
    - 如果遇到奇怪的二进制问题，通常是 **ARM 兼容性**问题。

    文档：[Linux](/zh-CN/platforms/linux)、[安装](/zh-CN/install)。

  </Accordion>

  <Accordion title="它卡在 wake up my friend / onboarding will not hatch 了。现在怎么办？">
    该界面依赖 Gateway 网关可达并且已通过身份验证。TUI 也会在首次 hatch 时自动发送
    “Wake up, my friend!”。如果你看到这行字却**没有回复**，
    且 token 始终为 0，说明智能体根本没有运行。

    1. 重启 Gateway 网关：

    ```bash
    openclaw gateway restart
    ```

    2. 检查状态 + 凭证：

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. 如果仍然卡住，运行：

    ```bash
    openclaw doctor
    ```

    如果 Gateway 网关在远程环境中，请确保隧道 / Tailscale 连接已建立，并且 UI
    指向了正确的 Gateway 网关。参见 [远程访问](/zh-CN/gateway/remote)。

  </Accordion>

  <Accordion title="我可以把当前设置迁移到新机器（Mac mini）而不重新做新手引导吗？">
    可以。复制**状态目录**和**工作区**，然后运行一次 Doctor。这样会
    保持你的机器人“完全不变”（记忆、会话历史、凭证和渠道
    状态），前提是你复制了**这两个位置**：

    1. 在新机器上安装 OpenClaw。
    2. 从旧机器复制 `$OPENCLAW_STATE_DIR`（默认：`~/.openclaw`）。
    3. 复制你的工作区（默认：`~/.openclaw/workspace`）。
    4. 运行 `openclaw doctor` 并重启 Gateway 网关服务。

    这样会保留配置、凭证配置文件、WhatsApp 凭证、会话和记忆。如果你处于
    远程模式，请记住会话存储和工作区归 Gateway 网关主机所有。

    **重要：**如果你只是把工作区 commit / push 到 GitHub，你备份的是
    **记忆 + 引导文件**，但**不包括**会话历史或凭证。这些内容存储在
    `~/.openclaw/` 下（例如 `~/.openclaw/agents/<agentId>/sessions/`）。

    相关内容：[迁移](/zh-CN/install/migrating)、[磁盘上的文件位置](#where-things-live-on-disk)、
    [智能体工作区](/zh-CN/concepts/agent-workspace)、[Doctor](/zh-CN/gateway/doctor)、
    [远程模式](/zh-CN/gateway/remote)。

  </Accordion>

  <Accordion title="在哪里可以看到最新版本的新内容？">
    查看 GitHub 更新日志：
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    最新条目在最上方。如果最顶部部分标记为 **Unreleased**，则下一个带日期的
    部分就是最新已发布版本。条目按 **Highlights**、**Changes** 和
    **Fixes** 分组（需要时还会有 docs / other 部分）。

  </Accordion>

  <Accordion title="无法访问 docs.openclaw.ai（SSL 错误）">
    某些 Comcast / Xfinity 连接会错误地通过 Xfinity
    Advanced Security 屏蔽 `docs.openclaw.ai`。请禁用它或将 `docs.openclaw.ai` 加入白名单，然后重试。
    也请通过这里帮助我们解除屏蔽：[https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status)。

    如果你仍然无法访问该站点，文档在 GitHub 上也有镜像：
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="稳定版与 beta 的区别">
    **Stable** 和 **beta** 是 **npm dist-tag**，不是独立的代码线：

    - `latest` = 稳定版
    - `beta` = 用于测试的早期构建

    通常，一个稳定版会先发布到 **beta**，然后通过一次明确的
    提升步骤将同一版本移动到 `latest`。维护者也可以在必要时
    直接发布到 `latest`。这就是为什么 beta 与 stable 在提升后可能指向**同一个版本**。

    查看变更内容：
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    有关安装单行命令以及 beta 与 dev 的区别，请参见下方的折叠项。

  </Accordion>

  <Accordion title="如何安装 beta 版本？beta 与 dev 有什么区别？">
    **Beta** 是 npm dist-tag `beta`（提升后可能与 `latest` 一致）。
    **Dev** 是 `main` 的移动头部（git）；发布后使用 npm dist-tag `dev`。

    单行命令（macOS / Linux）：

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Windows 安装器（PowerShell）：
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    更多细节：[开发渠道](/zh-CN/install/development-channels) 和 [安装器标志](/zh-CN/install/installer)。

  </Accordion>

  <Accordion title="如何试用最新功能？">
    有两种方式：

    1. **Dev 渠道（git 检出）：**

    ```bash
    openclaw update --channel dev
    ```

    这会切换到 `main` 分支并从源码更新。

    2. **Hackable 安装（来自安装站点）：**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    这样你会得到一个可本地编辑的仓库，然后可以通过 git 更新。

    如果你更喜欢手动做一个干净克隆，请使用：

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    文档：[更新](/cli/update)、[开发渠道](/zh-CN/install/development-channels)、
    [安装](/zh-CN/install)。

  </Accordion>

  <Accordion title="安装和新手引导通常需要多久？">
    粗略参考：

    - **安装：**2 - 5 分钟
    - **新手引导：**5 - 15 分钟，取决于你配置了多少渠道 / 模型

    如果卡住，请参考 [安装器卡住了](#quick-start-and-first-run-setup)
    和 [我卡住了](#quick-start-and-first-run-setup) 中的快速调试循环。

  </Accordion>

  <Accordion title="安装器卡住了？如何获得更多反馈？">
    使用**详细输出**重新运行安装器：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    安装 beta 并启用详细输出：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    对于 hackable（git）安装：

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Windows（PowerShell）等效方法：

    ```powershell
    # install.ps1 目前还没有专用的 -Verbose 标志。
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    更多选项：[安装器标志](/zh-CN/install/installer)。

  </Accordion>

  <Accordion title="Windows 安装时提示 git not found 或 openclaw not recognized">
    Windows 上有两个常见问题：

    **1）npm 错误 spawn git / git not found**

    - 安装 **Git for Windows**，并确保 `git` 在你的 PATH 中。
    - 关闭并重新打开 PowerShell，然后重新运行安装器。

    **2）安装后 openclaw is not recognized**

    - 你的 npm 全局 bin 目录不在 PATH 中。
    - 检查路径：

      ```powershell
      npm config get prefix
      ```

    - 将该目录添加到你的用户 PATH 中（Windows 上无需 `\bin` 后缀；大多数系统上它是 `%AppData%\npm`）。
    - 更新 PATH 后关闭并重新打开 PowerShell。

    如果你想获得最顺畅的 Windows 设置体验，请使用 **WSL2**，而不是原生 Windows。
    文档：[Windows](/zh-CN/platforms/windows)。

  </Accordion>

  <Accordion title="Windows exec 输出显示乱码中文，我该怎么办？">
    这通常是原生 Windows shell 中控制台代码页不匹配导致的。

    症状：

    - `system.run` / `exec` 输出中的中文显示为乱码
    - 同一命令在其他终端配置文件中显示正常

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

    如果你在最新版 OpenClaw 中仍能复现该问题，请在这里跟踪 / 报告：

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="文档没有回答我的问题，如何获得更好的答案？">
    使用 **hackable（git）安装**，这样你就能在本地拥有完整源码和文档，然后
    从该文件夹中向你的机器人（或 Claude / Codex）提问，
    它就能读取仓库并给出精确答案。

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    更多细节：[安装](/zh-CN/install) 和 [安装器标志](/zh-CN/install/installer)。

  </Accordion>

  <Accordion title="如何在 Linux 上安装 OpenClaw？">
    简短回答：按照 Linux 指南操作，然后运行新手引导。

    - Linux 快速路径 + 服务安装：[Linux](/zh-CN/platforms/linux)。
    - 完整演练：[入门指南](/zh-CN/start/getting-started)。
    - 安装器 + 更新：[安装与更新](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="如何在 VPS 上安装 OpenClaw？">
    任何 Linux VPS 都可以。安装到服务器上，然后通过 SSH / Tailscale 访问 Gateway 网关。

    指南：[exe.dev](/zh-CN/install/exe-dev)、[Hetzner](/zh-CN/install/hetzner)、[Fly.io](/zh-CN/install/fly)。
    远程访问：[Gateway 网关远程访问](/zh-CN/gateway/remote)。

  </Accordion>

  <Accordion title="云 / VPS 安装指南在哪里？">
    我们维护了一个**托管中心**，收录常见提供商。选择其中一个并按照指南操作：

    - [VPS 托管](/zh-CN/vps)（所有提供商集中在一处）
    - [Fly.io](/zh-CN/install/fly)
    - [Hetzner](/zh-CN/install/hetzner)
    - [exe.dev](/zh-CN/install/exe-dev)

    云中工作方式如下：**Gateway 网关运行在服务器上**，你通过 Control UI
    （或 Tailscale / SSH）从笔记本 / 手机上访问它。你的状态 + 工作区
    存储在服务器上，因此请将主机视为事实来源并做好备份。

    你可以将 **节点**（Mac / iOS / Android / 无头设备）配对到该云端 Gateway 网关，以访问
    本地屏幕 / 摄像头 / Canvas，或在笔记本上运行命令，同时将
    Gateway 网关保留在云中。

    中心：[平台](/zh-CN/platforms)。远程访问：[Gateway 网关远程访问](/zh-CN/gateway/remote)。
    节点：[节点](/zh-CN/nodes)、[节点 CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="我可以让 OpenClaw 自己更新自己吗？">
    简短回答：**可以，但不推荐**。更新流程可能会重启
    Gateway 网关（这会中断当前会话），可能需要一个干净的 git 检出，并且
    可能会要求确认。更安全的方式：由操作员在 shell 中运行更新。

    使用 CLI：

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    如果你必须从智能体中自动化执行：

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    文档：[更新](/cli/update)、[更新说明](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="新手引导实际上会做什么？">
    `openclaw onboard` 是推荐的设置路径。在**本地模式**下，它会引导你完成：

    - **模型 / 凭证设置**（提供商 OAuth、API 密钥、Anthropic setup-token，以及 LM Studio 等本地模型选项）
    - **工作区**位置 + 引导文件
    - **Gateway 网关设置**（bind / port / auth / tailscale）
    - **渠道**（WhatsApp、Telegram、Discord、Mattermost、Signal、iMessage，以及像 QQ Bot 这样的内置渠道插件）
    - **守护进程安装**（macOS 上为 LaunchAgent；Linux / WSL2 上为 systemd user unit）
    - **健康检查** 和 **Skills** 选择

    如果你配置的模型未知或缺少凭证，它也会发出警告。

  </Accordion>

  <Accordion title="运行这个需要 Claude 或 OpenAI 订阅吗？">
    不需要。你可以通过 **API 密钥**（Anthropic / OpenAI / 其他）运行 OpenClaw，也可以使用
    **仅本地模型**，这样你的数据就能保留在自己的设备上。订阅（Claude
    Pro / Max 或 OpenAI Codex）只是这些提供商的可选身份验证方式。

    对于 OpenClaw 中的 Anthropic，实际可分为：

    - **Anthropic API 密钥**：正常的 Anthropic API 计费
    - **OpenClaw 中的 Claude CLI / Claude 订阅凭证**：Anthropic 工作人员
      告诉我们，这种用法再次被允许，因此除非 Anthropic 发布新政策，
      否则 OpenClaw 会将 `claude -p`
      用法视为该集成的许可用法

    对于长期运行的 Gateway 网关主机，Anthropic API 密钥仍然是
    更可预测的设置方式。OpenAI Codex OAuth 明确支持用于 OpenClaw 这类外部
    工具。

    OpenClaw 还支持其他托管式订阅方案，包括
    **Qwen Cloud Coding Plan**、**MiniMax Coding Plan** 和
    **Z.AI / GLM Coding Plan**。

    文档：[Anthropic](/zh-CN/providers/anthropic)、[OpenAI](/zh-CN/providers/openai)、
    [Qwen Cloud](/zh-CN/providers/qwen)、
    [MiniMax](/zh-CN/providers/minimax)、[GLM Models](/zh-CN/providers/glm)、
    [本地模型](/zh-CN/gateway/local-models)、[模型](/zh-CN/concepts/models)。

  </Accordion>

  <Accordion title="我可以在没有 API 密钥的情况下使用 Claude Max 订阅吗？">
    可以。

    Anthropic 工作人员告诉我们，OpenClaw 风格的 Claude CLI 用法再次被允许，因此
    除非 Anthropic 发布新政策，否则
    OpenClaw 会将 Claude 订阅凭证和 `claude -p` 用法视为该集成的许可用法。如果你想要
    最可预测的服务器端设置，请改用 Anthropic API 密钥。

  </Accordion>

  <Accordion title="支持 Claude 订阅凭证（Claude Pro 或 Max）吗？">
    支持。

    Anthropic 工作人员告诉我们，这种用法再次被允许，因此除非 Anthropic 发布新政策，
    否则 OpenClaw 会将
    Claude CLI 复用和 `claude -p` 用法视为该集成的许可用法。

    Anthropic setup-token 仍然作为受支持的 OpenClaw token 路径提供，但在可用时，OpenClaw 现在更偏好 Claude CLI 复用和 `claude -p`。
    对于生产环境或多用户工作负载，Anthropic API 密钥凭证仍然是
    更安全、更可预测的选择。如果你想在 OpenClaw 中使用其他托管式订阅选项，
    参见 [OpenAI](/zh-CN/providers/openai)、[Qwen / Model
    Cloud](/zh-CN/providers/qwen)、[MiniMax](/zh-CN/providers/minimax) 和 [GLM
    Models](/zh-CN/providers/glm)。

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="为什么我会看到来自 Anthropic 的 HTTP 429 rate_limit_error？">
这意味着你当前窗口的 **Anthropic 配额 / 速率限制** 已耗尽。如果你
使用 **Claude CLI**，请等待窗口重置或升级你的套餐。如果你
使用 **Anthropic API 密钥**，请检查 Anthropic Console
中的使用量 / 计费，并根据需要提高限制。

    如果消息明确是：
    `Extra usage is required for long context requests`，说明请求正尝试使用
    Anthropic 的 1M 上下文 beta（`context1m: true`）。这仅在你的
    凭证具备长上下文计费资格时可用（API 密钥计费，或
    启用了 Extra Usage 的 OpenClaw Claude 登录路径）。

    提示：设置一个**回退模型**，这样当某个提供商受到速率限制时，OpenClaw 仍可继续回复。
    参见 [模型](/cli/models)、[OAuth](/zh-CN/concepts/oauth) 和
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/zh-CN/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context)。

  </Accordion>

  <Accordion title="支持 AWS Bedrock 吗？">
    支持。OpenClaw 内置了 **Amazon Bedrock（Converse）** 提供商。当 AWS 环境标记存在时，OpenClaw 可以自动发现支持流式 / 文本的 Bedrock 目录，并将其合并为隐式的 `amazon-bedrock` 提供商；否则，你也可以显式启用 `plugins.entries.amazon-bedrock.config.discovery.enabled` 或添加手动提供商条目。参见 [Amazon Bedrock](/zh-CN/providers/bedrock) 和 [模型提供商](/zh-CN/providers/models)。如果你更喜欢托管式密钥流程，在 Bedrock 前面使用 OpenAI 兼容代理仍然是可行的选择。
  </Accordion>

  <Accordion title="Codex 凭证是如何工作的？">
    OpenClaw 通过 OAuth（ChatGPT 登录）支持 **OpenAI Code（Codex）**。新手引导可以运行 OAuth 流程，并在适用时将默认模型设置为 `openai-codex/gpt-5.4`。参见 [模型提供商](/zh-CN/concepts/model-providers) 和 [设置向导（CLI）](/zh-CN/start/wizard)。
  </Accordion>

  <Accordion title="为什么 ChatGPT GPT-5.4 不会在 OpenClaw 中解锁 openai/gpt-5.4？">
    OpenClaw 将这两条路径分开处理：

    - `openai-codex/gpt-5.4` = ChatGPT / Codex OAuth
    - `openai/gpt-5.4` = 直接 OpenAI Platform API

    在 OpenClaw 中，ChatGPT / Codex 登录连接到 `openai-codex/*` 路径，
    而不是直接的 `openai/*` 路径。如果你想要 OpenClaw 中的直接 API 路径，
    请设置 `OPENAI_API_KEY`（或等效的 OpenAI 提供商配置）。
    如果你想在 OpenClaw 中使用 ChatGPT / Codex 登录，请使用 `openai-codex/*`。

  </Accordion>

  <Accordion title="为什么 Codex OAuth 限额会与 ChatGPT Web 不同？">
    `openai-codex/*` 使用 Codex OAuth 路径，其可用配额窗口由
    OpenAI 管理，并且取决于你的套餐。在实践中，这些限制可能与
    ChatGPT 网站 / 应用的体验不同，即使两者绑定到同一个账户也是如此。

    OpenClaw 可以在
    `openclaw models status` 中显示当前可见的提供商使用量 / 配额窗口，但它不会凭空发明或将 ChatGPT Web
    权益标准化为直接 API 访问。如果你想使用直接的 OpenAI Platform
    计费 / 限额路径，请通过 API 密钥使用 `openai/*`。

  </Accordion>

  <Accordion title="支持 OpenAI 订阅凭证（Codex OAuth）吗？">
    支持。OpenClaw 完整支持 **OpenAI Code（Codex）订阅 OAuth**。
    OpenAI 明确允许在 OpenClaw 这类外部工具 / 工作流中
    使用订阅 OAuth。新手引导可以为你运行 OAuth 流程。

    参见 [OAuth](/zh-CN/concepts/oauth)、[模型提供商](/zh-CN/concepts/model-providers) 和 [设置向导（CLI）](/zh-CN/start/wizard)。

  </Accordion>

  <Accordion title="如何设置 Gemini CLI OAuth？">
    Gemini CLI 使用的是**插件凭证流程**，而不是 `openclaw.json` 中的 client id 或 secret。

    步骤如下：

    1. 在本地安装 Gemini CLI，使 `gemini` 可在 `PATH` 中找到
       - Homebrew：`brew install gemini-cli`
       - npm：`npm install -g @google/gemini-cli`
    2. 启用插件：`openclaw plugins enable google`
    3. 登录：`openclaw models auth login --provider google-gemini-cli --set-default`
    4. 登录后的默认模型：`google-gemini-cli/gemini-3.1-pro-preview`
    5. 如果请求失败，请在 Gateway 网关主机上设置 `GOOGLE_CLOUD_PROJECT` 或 `GOOGLE_CLOUD_PROJECT_ID`

    这会把 OAuth token 存储到 Gateway 网关主机上的凭证配置文件中。详情： [模型提供商](/zh-CN/concepts/model-providers)。

  </Accordion>

  <Accordion title="本地模型适合日常聊天吗？">
    通常不适合。OpenClaw 需要大上下文 + 强安全性；小显存模型会截断并泄露。如果你一定要用，请在本地（LM Studio）运行你能承载的**最大**模型构建，并参见 [/gateway/local-models](/zh-CN/gateway/local-models)。更小 / 更量化的模型会增加 prompt injection 风险——参见 [安全](/zh-CN/gateway/security)。
  </Accordion>

  <Accordion title="如何让托管模型流量保持在特定区域内？">
    选择区域固定的端点。OpenRouter 为 MiniMax、Kimi 和 GLM 提供美国托管选项；选择美国托管变体即可让数据保留在该区域内。你仍然可以通过 `models.mode: "merge"` 同时列出 Anthropic / OpenAI，使回退保持可用，同时遵守你选择的区域化提供商。
  </Accordion>

  <Accordion title="安装这个必须买 Mac Mini 吗？">
    不需要。OpenClaw 可运行于 macOS 或 Linux（Windows 可通过 WSL2）。Mac mini 是可选的——有些人
    会买一台作为常开主机，但小型 VPS、家用服务器或 Raspberry Pi 级别设备也可以。

    只有在使用 **仅限 macOS 的工具** 时，你才需要 Mac。对于 iMessage，请使用 [BlueBubbles](/zh-CN/channels/bluebubbles)（推荐）——BlueBubbles 服务器运行在任意 Mac 上，而 Gateway 网关可以运行在 Linux 或其他地方。如果你想使用其他仅限 macOS 的工具，请在 Mac 上运行 Gateway 网关，或配对一个 macOS 节点。

    文档：[BlueBubbles](/zh-CN/channels/bluebubbles)、[节点](/zh-CN/nodes)、[Mac 远程模式](/zh-CN/platforms/mac/remote)。

  </Accordion>

  <Accordion title="支持 iMessage 一定需要 Mac mini 吗？">
    你需要某个**已登录 Messages 的 macOS 设备**。它**不一定**是 Mac mini——
    任何 Mac 都可以。对于 iMessage，请**使用 [BlueBubbles](/zh-CN/channels/bluebubbles)**（推荐）——BlueBubbles 服务器运行在 macOS 上，而 Gateway 网关可以运行在 Linux 或其他地方。

    常见设置：

    - 在 Linux / VPS 上运行 Gateway 网关，在任意已登录 Messages 的 Mac 上运行 BlueBubbles 服务器。
    - 如果你想要最简单的单机设置，也可以把所有内容都运行在 Mac 上。

    文档：[BlueBubbles](/zh-CN/channels/bluebubbles)、[节点](/zh-CN/nodes)、
    [Mac 远程模式](/zh-CN/platforms/mac/remote)。

  </Accordion>

  <Accordion title="如果我买一台 Mac mini 来运行 OpenClaw，可以把它连接到我的 MacBook Pro 吗？">
    可以。**Mac mini 可以运行 Gateway 网关**，而你的 MacBook Pro 可以作为
    **节点**（配套设备）连接。节点不会运行 Gateway 网关——它们会提供额外
    功能，例如该设备上的屏幕 / 摄像头 / Canvas 和 `system.run`。

    常见模式：

    - Gateway 网关运行在 Mac mini 上（常开）。
    - MacBook Pro 运行 macOS 应用或节点主机，并与 Gateway 网关配对。
    - 使用 `openclaw nodes status` / `openclaw nodes list` 查看它。

    文档：[节点](/zh-CN/nodes)、[节点 CLI](/cli/nodes)。

  </Accordion>

  <Accordion title="可以使用 Bun 吗？">
    **不推荐**使用 Bun。我们观察到运行时 bug，尤其是在 WhatsApp 和 Telegram 上。
    稳定运行的 Gateway 网关请使用 **Node**。

    如果你仍然想尝试 Bun，请在非生产 Gateway 网关上
    进行，并且不要启用 WhatsApp / Telegram。

  </Accordion>

  <Accordion title="Telegram：allowFrom 中应填写什么？">
    `channels.telegram.allowFrom` 是**真人发送者的 Telegram 用户 ID**（数字）。
    它不是机器人用户名。

    新手引导接受 `@username` 输入并将其解析为数字 ID，但 OpenClaw 的授权只使用数字 ID。

    更安全的做法（无需第三方机器人）：

    - 给你的机器人发私信，然后运行 `openclaw logs --follow` 并读取 `from.id`。

    官方 Bot API：

    - 给你的机器人发私信，然后调用 `https://api.telegram.org/bot<bot_token>/getUpdates` 并读取 `message.from.id`。

    第三方方式（隐私性较差）：

    - 向 `@userinfobot` 或 `@getidsbot` 发送私信。

    参见 [/channels/telegram](/zh-CN/channels/telegram#access-control-and-activation)。

  </Accordion>

  <Accordion title="多个用户可以用同一个 WhatsApp 号码连接不同的 OpenClaw 实例吗？">
    可以，通过**多智能体路由**实现。将每个发送者的 WhatsApp **私信**
    （peer `kind: "direct"`，发送者 E.164 格式如 `+15551234567`）绑定到不同的 `agentId`，这样每个人都有自己的工作区和会话存储。回复仍然会来自**同一个 WhatsApp 账户**，而私信访问控制（`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`）则在该 WhatsApp 账户级别全局生效。参见 [多智能体路由](/zh-CN/concepts/multi-agent) 和 [WhatsApp](/zh-CN/channels/whatsapp)。
  </Accordion>

  <Accordion title='我可以同时运行一个“快速聊天”智能体和一个“用于编程的 Opus”智能体吗？'>
    可以。使用多智能体路由：为每个智能体设置各自的默认模型，然后将入站路由（提供商账户或特定 peer）绑定到各自智能体。示例配置位于 [多智能体路由](/zh-CN/concepts/multi-agent)。另请参见 [模型](/zh-CN/concepts/models) 和 [配置](/zh-CN/gateway/configuration)。
  </Accordion>

  <Accordion title="Homebrew 能在 Linux 上工作吗？">
    可以。Homebrew 支持 Linux（Linuxbrew）。快速设置如下：

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    如果你通过 systemd 运行 OpenClaw，请确保服务 PATH 包含 `/home/linuxbrew/.linuxbrew/bin`（或你的 brew 前缀），这样 `brew` 安装的工具就能在非登录 shell 中被解析。
    最近的构建还会在 Linux systemd 服务中预置常见用户 bin 目录（例如 `~/.local/bin`、`~/.npm-global/bin`、`~/.local/share/pnpm`、`~/.bun/bin`），并在设置时遵循 `PNPM_HOME`、`NPM_CONFIG_PREFIX`、`BUN_INSTALL`、`VOLTA_HOME`、`ASDF_DATA_DIR`、`NVM_DIR` 和 `FNM_DIR`。

  </Accordion>

  <Accordion title="hackable git 安装与 npm install 的区别">
    - **Hackable（git）安装：**完整源码检出，可编辑，最适合贡献者。
      你需要在本地运行构建，并可以修改代码 / 文档。
    - **npm install：**全局 CLI 安装，没有仓库，最适合“直接运行”。
      更新来自 npm dist-tag。

    文档：[入门指南](/zh-CN/start/getting-started)、[更新](/zh-CN/install/updating)。

  </Accordion>

  <Accordion title="之后还能在 npm 安装和 git 安装之间切换吗？">
    可以。安装另一种方式后，运行 Doctor，让 Gateway 网关服务指向新的入口点。
    这**不会删除你的数据**——它只会更改 OpenClaw 代码安装方式。你的状态
    （`~/.openclaw`）和工作区（`~/.openclaw/workspace`）会保持不变。

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

    Doctor 会检测 Gateway 网关服务入口点不匹配，并提供将服务配置重写为匹配当前安装的选项（在自动化中使用 `--repair`）。

    备份建议：参见 [备份策略](#where-things-live-on-disk)。

  </Accordion>

  <Accordion title="我应该把 Gateway 网关运行在笔记本上还是 VPS 上？">
    简短回答：**如果你想要 24 / 7 可靠性，就用 VPS**。如果你更在意
    最低摩擦，并且能接受休眠 / 重启，那就在本地运行。

    **笔记本（本地 Gateway 网关）**

    - **优点：**无需服务器成本，直接访问本地文件，可见的浏览器窗口。
    - **缺点：**休眠 / 网络中断 = 连接断开，操作系统更新 / 重启会中断，必须保持唤醒。

    **VPS / 云**

    - **优点：**常开、网络稳定、没有笔记本休眠问题、更容易持续运行。
    - **缺点：**通常是无头运行（需使用截图），只能远程访问文件，你必须通过 SSH 更新。

    **OpenClaw 特定说明：**WhatsApp / Telegram / Slack / Mattermost / Discord 都能在 VPS 上正常工作。唯一真正的权衡是**无头浏览器**与可见窗口之间的差异。参见 [浏览器](/zh-CN/tools/browser)。

    **推荐默认方案：**如果你之前遇到过 Gateway 网关断连，请使用 VPS。本地运行非常适合你在积极使用 Mac，并希望访问本地文件或使用可见浏览器进行 UI 自动化的情况。

  </Accordion>

  <Accordion title="将 OpenClaw 运行在专用机器上有多重要？">
    不是必需的，但**出于可靠性和隔离考虑，推荐这样做**。

    - **专用主机（VPS / Mac mini / Pi）：**常开，较少受到休眠 / 重启影响，权限更干净，更容易持续运行。
    - **共享笔记本 / 台式机：**完全适合测试和日常主动使用，但当机器休眠或更新时，预计会有暂停。

    如果你想两全其美，可以将 Gateway 网关放在专用主机上，并把你的笔记本配对为**节点**，用于本地屏幕 / 摄像头 / exec 工具。参见 [节点](/zh-CN/nodes)。
    有关安全指导，请阅读 [安全](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="最低 VPS 配置要求和推荐操作系统是什么？">
    OpenClaw 很轻量。对于基础 Gateway 网关 + 单个聊天渠道：

    - **绝对最低：**1 vCPU、1 GB 内存、约 500 MB 磁盘。
    - **推荐：**1 - 2 vCPU、2 GB 内存或更多余量（用于日志、媒体、多渠道）。Node 工具和浏览器自动化可能比较吃资源。

    操作系统：请使用 **Ubuntu LTS**（或任何现代 Debian / Ubuntu）。Linux 安装路径在这些系统上测试最充分。

    文档：[Linux](/zh-CN/platforms/linux)、[VPS 托管](/zh-CN/vps)。

  </Accordion>

  <Accordion title="可以在 VM 中运行 OpenClaw 吗？需要什么配置？">
    可以。将 VM 视为 VPS：它需要始终在线、可访问，并且有足够的
    内存供 Gateway 网关和你启用的任何渠道使用。

    基线建议：

    - **绝对最低：**1 vCPU、1 GB 内存。
    - **推荐：**如果运行多个渠道、浏览器自动化或媒体工具，建议 2 GB 内存或更多。
    - **操作系统：**Ubuntu LTS 或其他现代 Debian / Ubuntu。

    如果你使用 Windows，**WSL2 是最简单的 VM 风格设置**，并且工具兼容性最好。
    参见 [Windows](/zh-CN/platforms/windows)、[VPS 托管](/zh-CN/vps)。
    如果你在 VM 中运行 macOS，请参见 [macOS VM](/zh-CN/install/macos-vm)。

  </Accordion>
</AccordionGroup>

## OpenClaw 是什么？

<AccordionGroup>
  <Accordion title="用一段话解释什么是 OpenClaw">
    OpenClaw 是一个运行在你自己设备上的个人 AI 助手。它会在你已经使用的消息界面上回复你（WhatsApp、Telegram、Slack、Mattermost、Discord、Google Chat、Signal、iMessage、WebChat，以及像 QQ Bot 这样的内置渠道插件），并且在受支持的平台上还可以提供语音 + 实时 Canvas。**Gateway 网关**是始终在线的控制平面；这个助手本身才是产品。
  </Accordion>

  <Accordion title="价值主张">
    OpenClaw 不只是“Claude 包装器”。它是一个**本地优先的控制平面**，让你可以在**自己的硬件**上运行一个强大的助手，通过你已经在使用的聊天应用访问，并且具备有状态的会话、记忆和工具——而无需把你的工作流控制权交给托管式
    SaaS。

    亮点：

    - **你的设备，你的数据：**可以在任何你想要的地方运行 Gateway 网关（Mac、Linux、VPS），并将
      工作区 + 会话历史保留在本地。
    - **真实渠道，而非 Web 沙箱：**WhatsApp / Telegram / Slack / Discord / Signal / iMessage 等，
      以及在受支持平台上的移动语音和 Canvas。
    - **模型无关：**使用 Anthropic、OpenAI、MiniMax、OpenRouter 等，并支持按智能体路由
      和故障切换。
    - **仅本地选项：**运行本地模型，这样**所有数据都可以保留在你的设备上**。
    - **多智能体路由：**按渠道、账户或任务拆分智能体，每个智能体拥有自己的
      工作区和默认值。
    - **开源且可修改：**可检查、扩展并自托管，无厂商锁定。

    文档：[Gateway 网关](/zh-CN/gateway)、[渠道](/zh-CN/channels)、[多智能体](/zh-CN/concepts/multi-agent)、
    [记忆](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="我刚设置好它——第一步应该做什么？">
    适合作为起步的项目：

    - 搭建一个网站（WordPress、Shopify 或简单静态站点）。
    - 原型设计一个移动应用（大纲、界面、API 计划）。
    - 整理文件和文件夹（清理、命名、打标签）。
    - 连接 Gmail 并自动生成摘要或后续跟进。

    它可以处理大型任务，但当你把任务拆分成多个阶段，并
    使用子智能体并行工作时，效果最好。

  </Accordion>

  <Accordion title="OpenClaw 最常见的五个日常使用场景是什么？">
    日常高价值场景通常包括：

    - **个人简报：**汇总你关心的收件箱、日历和新闻。
    - **研究与起草：**快速研究、总结，以及邮件或文档的初稿。
    - **提醒与跟进：**由 cron 或 heartbeat 驱动的提醒和清单。
    - **浏览器自动化：**填写表单、收集数据、重复执行 Web 任务。
    - **跨设备协作：**在手机上发出任务，让 Gateway 网关在服务器上执行，然后把结果发回聊天。

  </Accordion>

  <Accordion title="OpenClaw 能帮助 SaaS 做获客、外联、广告和博客吗？">
    可以用于**研究、筛选和起草**。它可以扫描网站、建立候选清单、
    总结潜在客户，并撰写外联或广告文案草稿。

    但对于**外联或广告投放**，请务必让人工参与。避免垃圾信息，遵守当地法律和
    平台政策，并在发送前审查所有内容。最安全的模式是让
    OpenClaw 起草，由你审批。

    文档：[安全](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="与 Claude Code 相比，在 Web 开发方面有什么优势？">
    OpenClaw 是一个**个人助手**和协作层，而不是 IDE 替代品。在仓库内进行最快的直接编码循环时，
    请使用 Claude Code 或 Codex。当你
    需要持久记忆、跨设备访问和工具编排时，请使用 OpenClaw。

    优势：

    - **跨会话的持久记忆 + 工作区**
    - **多平台访问**（WhatsApp、Telegram、TUI、WebChat）
    - **工具编排**（浏览器、文件、调度、hooks）
    - **始终在线的 Gateway 网关**（可运行在 VPS 上，随处交互）
    - 用于本地浏览器 / 屏幕 / 摄像头 / exec 的**节点**

    展示页：[https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills 与自动化

<AccordionGroup>
  <Accordion title="如何自定义 skills 而不让仓库变脏？">
    使用托管覆盖，而不是编辑仓库副本。将你的更改放到 `~/.openclaw/skills/<name>/SKILL.md` 中（或通过 `~/.openclaw/openclaw.json` 中的 `skills.load.extraDirs` 添加文件夹）。优先级为 `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → 内置 → `skills.load.extraDirs`，因此托管覆盖仍会在不修改 git 的情况下覆盖内置 skills。如果你需要全局安装某个 skill，但只希望部分智能体可见，请将共享副本放在 `~/.openclaw/skills` 中，并通过 `agents.defaults.skills` 和 `agents.list[].skills` 控制可见性。只有值得上游合并的更改才应该保留在仓库里并以 PR 形式提交。
  </Accordion>

  <Accordion title="可以从自定义文件夹加载 skills 吗？">
    可以。通过 `~/.openclaw/openclaw.json` 中的 `skills.load.extraDirs` 添加额外目录（最低优先级）。默认优先级为 `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → 内置 → `skills.load.extraDirs`。`clawhub` 默认安装到 `./skills`，OpenClaw 会在下一次会话中将其视为 `<workspace>/skills`。如果该 skill 只应对特定智能体可见，请同时搭配 `agents.defaults.skills` 或 `agents.list[].skills`。
  </Accordion>

  <Accordion title="如何为不同任务使用不同模型？">
    当前支持的模式有：

    - **Cron 任务**：隔离任务可为每个任务设置 `model` 覆盖。
    - **子智能体**：将任务路由到拥有不同默认模型的独立智能体。
    - **按需切换**：随时使用 `/model` 切换当前会话模型。

    参见 [Cron 任务](/zh-CN/automation/cron-jobs)、[多智能体路由](/zh-CN/concepts/multi-agent) 和 [斜杠命令](/zh-CN/tools/slash-commands)。

  </Accordion>

  <Accordion title="机器人在执行重任务时卡住了。如何把工作卸载出去？">
    对于耗时较长或可并行的任务，请使用**子智能体**。子智能体运行在自己的会话中，
    返回摘要，并保持主聊天响应流畅。

    你可以要求机器人“为这个任务启动一个子智能体”，或者使用 `/subagents`。
    使用聊天中的 `/status` 查看 Gateway 网关当前正在做什么（以及它是否繁忙）。

    Token 提示：长任务和子智能体都会消耗 token。如果你关心成本，请通过 `agents.defaults.subagents.model` 为子智能体设置更便宜的模型。

    文档：[子智能体](/zh-CN/tools/subagents)、[后台任务](/zh-CN/automation/tasks)。

  </Accordion>

  <Accordion title="Discord 上与线程绑定的 subagent 会话是如何工作的？">
    使用线程绑定。你可以将 Discord 线程绑定到子智能体或会话目标，这样该线程中的后续消息会持续停留在该绑定会话中。

    基本流程：

    - 使用 `sessions_spawn` 启动并设置 `thread: true`（以及可选的 `mode: "session"`，用于持久后续跟进）。
    - 或通过 `/focus <target>` 手动绑定。
    - 使用 `/agents` 检查绑定状态。
    - 使用 `/session idle <duration|off>` 和 `/session max-age <duration|off>` 控制自动取消聚焦。
    - 使用 `/unfocus` 解除线程绑定。

    必需配置：

    - 全局默认值：`session.threadBindings.enabled`、`session.threadBindings.idleHours`、`session.threadBindings.maxAgeHours`。
    - Discord 覆盖：`channels.discord.threadBindings.enabled`、`channels.discord.threadBindings.idleHours`、`channels.discord.threadBindings.maxAgeHours`。
    - 在 spawn 时自动绑定：设置 `channels.discord.threadBindings.spawnSubagentSessions: true`。

    文档：[子智能体](/zh-CN/tools/subagents)、[Discord](/zh-CN/channels/discord)、[配置参考](/zh-CN/gateway/configuration-reference)、[斜杠命令](/zh-CN/tools/slash-commands)。

  </Accordion>

  <Accordion title="子智能体已完成，但完成更新发送到了错误位置，或者根本没有发出。我该检查什么？">
    先检查解析后的请求方路由：

    - 完成模式下的子智能体投递会优先使用任何已绑定的线程或对话路由。
    - 如果完成来源仅携带渠道，OpenClaw 会退回到请求方会话存储的路由（`lastChannel` / `lastTo` / `lastAccountId`），这样直接投递仍可能成功。
    - 如果既不存在绑定路由，也没有可用的存储路由，直接投递可能失败，结果会退回到排队的会话投递，而不是立即发送到聊天。
    - 无效或过时的目标仍可能导致退回到队列，或最终投递失败。
    - 如果子会话中最后一条可见的 assistant 回复是完全静默 token `NO_REPLY` / `no_reply`，或恰好为 `ANNOUNCE_SKIP`，OpenClaw 会有意抑制公告，而不是发布更早的过时进度。
    - 如果子任务只进行了工具调用后就超时，公告可能会将其折叠为简短的部分进度摘要，而不是回放原始工具输出。

    调试：

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    文档：[子智能体](/zh-CN/tools/subagents)、[后台任务](/zh-CN/automation/tasks)、[会话工具](/zh-CN/concepts/session-tool)。

  </Accordion>

  <Accordion title="Cron 或提醒没有触发。我该检查什么？">
    Cron 在 Gateway 网关进程内部运行。如果 Gateway 网关没有持续运行，
    已计划的任务就不会执行。

    检查清单：

    - 确认 cron 已启用（`cron.enabled`），并且未设置 `OPENCLAW_SKIP_CRON`。
    - 检查 Gateway 网关是否 24 / 7 运行（无休眠 / 重启）。
    - 验证任务时区设置（`--tz` 与主机时区）。

    调试：

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    文档：[Cron 任务](/zh-CN/automation/cron-jobs)、[自动化与任务](/zh-CN/automation)。

  </Accordion>

  <Accordion title="Cron 触发了，但没有向渠道发送任何内容。为什么？">
    先检查投递模式：

    - `--no-deliver` / `delivery.mode: "none"` 表示不期望有任何外部消息。
    - 缺失或无效的公告目标（`channel` / `to`）表示运行器跳过了出站投递。
    - 渠道凭证失败（`unauthorized`、`Forbidden`）表示运行器尝试了投递，但凭证阻止了它。
    - 静默的隔离结果（只有 `NO_REPLY` / `no_reply`）会被视为有意不可投递，因此运行器也会抑制排队的回退投递。

    对于隔离的 cron 任务，运行器负责最终投递。智能体应当
    返回纯文本摘要，供运行器发送。`--no-deliver` 会让
    该结果保持内部状态；它并不会让智能体改为通过
    message 工具直接发送。

    调试：

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    文档：[Cron 任务](/zh-CN/automation/cron-jobs)、[后台任务](/zh-CN/automation/tasks)。

  </Accordion>

  <Accordion title="为什么一次隔离的 cron 运行会切换模型或重试一次？">
    这通常是实时模型切换路径，而不是重复调度。

    隔离的 cron 可以在活动运行抛出 `LiveSessionModelSwitchError` 时，
    持久化一个运行时模型切换并进行重试。该重试会保留切换后的
    提供商 / 模型，如果这次切换携带了新的凭证配置文件覆盖，cron
    也会在重试前将其持久化。

    相关选择规则：

    - 适用时，Gmail hook 模型覆盖优先级最高。
    - 其次是每个任务的 `model`。
    - 再其次是任何存储的 cron 会话模型覆盖。
    - 最后是正常的智能体 / 默认模型选择。

    重试循环是有界的。初次尝试加上 2 次切换重试之后，
    cron 会中止，而不是无限循环。

    调试：

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    文档：[Cron 任务](/zh-CN/automation/cron-jobs)、[cron CLI](/cli/cron)。

  </Accordion>

  <Accordion title="如何在 Linux 上安装 Skills？">
    使用原生 `openclaw skills` 命令，或将 skills 放入你的工作区。macOS Skills UI 在 Linux 上不可用。
    可在 [https://clawhub.ai](https://clawhub.ai) 浏览 skills。

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
    目录。只有当你想发布或同步自己的 skills 时，才需要安装单独的 `clawhub` CLI。对于跨智能体共享安装，请将 skill 放在
    `~/.openclaw/skills` 下，并使用 `agents.defaults.skills` 或
    `agents.list[].skills` 来缩小哪些智能体可见它。

  </Accordion>

  <Accordion title="OpenClaw 可以按计划运行任务，或持续在后台运行吗？">
    可以。使用 Gateway 网关调度器：

    - **Cron 任务**：用于计划任务或周期性任务（重启后仍会保留）。
    - **Heartbeat**：用于“主会话”的周期性检查。
    - **隔离任务**：用于自主智能体，可发布摘要或投递到聊天。

    文档：[Cron 任务](/zh-CN/automation/cron-jobs)、[自动化与任务](/zh-CN/automation)、
    [Heartbeat](/zh-CN/gateway/heartbeat)。

  </Accordion>

  <Accordion title="可以从 Linux 运行 Apple macOS 专属 skills 吗？">
    不能直接运行。macOS skills 受 `metadata.openclaw.os` 以及所需二进制文件控制，只有在 **Gateway 网关主机** 上符合条件时，这些 skills 才会出现在 system prompt 中。在 Linux 上，`darwin` 专属 skills（如 `apple-notes`、`apple-reminders`、`things-mac`）不会加载，除非你覆盖这些限制。

    你有三种受支持的模式：

    **方案 A：在 Mac 上运行 Gateway 网关（最简单）。**
    在具备 macOS 二进制文件的机器上运行 Gateway 网关，然后通过 [远程模式](#gateway-ports-already-running-and-remote-mode) 或 Tailscale 从 Linux 连接。由于 Gateway 网关主机是 macOS，这些 skills 会正常加载。

    **方案 B：使用 macOS 节点（无需 SSH）。**
    在 Linux 上运行 Gateway 网关，配对一个 macOS 节点（菜单栏应用），并在 Mac 上将 **Node Run Commands** 设置为 “Always Ask” 或 “Always Allow”。当所需二进制文件存在于该节点上时，OpenClaw 可以将这些仅限 macOS 的 skills 视为可用。智能体会通过 `nodes` 工具运行这些 skills。如果你选择 “Always Ask”，在提示中批准 “Always Allow” 会将该命令加入允许列表。

    **方案 C：通过 SSH 代理 macOS 二进制文件（高级）。**
    将 Gateway 网关保留在 Linux 上，但让所需的 CLI 二进制文件解析为在 Mac 上运行的 SSH 包装器。然后覆盖该 skill，使其允许 Linux，从而保持可用。

    1. 为该二进制文件创建 SSH 包装器（示例：Apple Notes 的 `memo`）：

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. 将该包装器放到 Linux 主机的 `PATH` 中（例如 `~/bin/memo`）。
    3. 覆盖 skill 元数据（工作区或 `~/.openclaw/skills`），以允许 Linux：

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. 启动一个新会话，使 skills 快照刷新。

  </Accordion>

  <Accordion title="有 Notion 或 HeyGen 集成吗？">
    目前没有内置。

    可选方式：

    - **自定义 skill / 插件：**最适合可靠的 API 访问（Notion / HeyGen 都有 API）。
    - **浏览器自动化：**无需代码，但速度较慢，也更脆弱。

    如果你想为每个客户保留上下文（例如代理机构工作流），一个简单的模式是：

    - 每个客户一个 Notion 页面（上下文 + 偏好 + 当前工作）。
    - 让智能体在会话开始时拉取该页面。

    如果你想要原生集成，请提交功能请求，或构建一个
    面向这些 API 的 skill。

    安装 skills：

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    原生安装会进入当前工作区的 `skills/` 目录。对于跨智能体共享的 skills，请将它们放在 `~/.openclaw/skills/<name>/SKILL.md` 中。如果共享安装只应对部分智能体可见，请配置 `agents.defaults.skills` 或 `agents.list[].skills`。有些 skills 依赖通过 Homebrew 安装的二进制文件；在 Linux 上这意味着 Linuxbrew（见上面的 Homebrew Linux 常见问题）。参见 [Skills](/zh-CN/tools/skills)、[Skills 配置](/zh-CN/tools/skills-config) 和 [ClawHub](/zh-CN/tools/clawhub)。

  </Accordion>

  <Accordion title="如何让 OpenClaw 使用我已经登录的 Chrome？">
    使用内置的 `user` 浏览器配置文件，它会通过 Chrome DevTools MCP 连接：

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    如果你想要自定义名称，请创建显式 MCP 配置文件：

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    这条路径是主机本地的。如果 Gateway 网关运行在其他地方，请在浏览器所在机器上运行一个节点主机，或改用远程 CDP。

    `existing-session` / `user` 当前的限制：

    - 操作基于 ref，而不是基于 CSS 选择器
    - 上传需要 `ref` / `inputRef`，并且当前一次只支持一个文件
    - `responsebody`、PDF 导出、下载拦截和批量操作仍需要托管浏览器或原始 CDP 配置文件

  </Accordion>
</AccordionGroup>

## 沙箱隔离与记忆

<AccordionGroup>
  <Accordion title="有专门的沙箱隔离文档吗？">
    有。参见 [沙箱隔离](/zh-CN/gateway/sandboxing)。对于 Docker 专用设置（Docker 中的完整 gateway 或沙箱镜像），参见 [Docker](/zh-CN/install/docker)。
  </Accordion>

  <Accordion title="Docker 感觉功能受限——如何启用完整功能？">
    默认镜像以安全为先，并以 `node` 用户运行，因此它
    不包含系统包、Homebrew 或内置浏览器。若要获得更完整的设置：

    - 使用 `OPENCLAW_HOME_VOLUME` 持久化 `/home/node`，以便缓存得以保留。
    - 通过 `OPENCLAW_DOCKER_APT_PACKAGES` 将系统依赖烘焙进镜像。
    - 使用内置 CLI 安装 Playwright 浏览器：
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - 设置 `PLAYWRIGHT_BROWSERS_PATH` 并确保该路径被持久化。

    文档：[Docker](/zh-CN/install/docker)、[浏览器](/zh-CN/tools/browser)。

  </Accordion>

  <Accordion title="我可以让私信保持私人，但让群组公开 / 沙箱隔离，同时只用一个智能体吗？">
    可以——前提是你的私人流量是**私信**，而公开流量是**群组**。

    使用 `agents.defaults.sandbox.mode: "non-main"`，这样群组 / 渠道会话（非主键）会在 Docker 中运行，而主私信会话仍在主机上运行。然后通过 `tools.sandbox.tools` 限制沙箱会话中可用的工具。

    设置演练 + 示例配置：[群组：私人私信 + 公开群组](/zh-CN/channels/groups#pattern-personal-dms-public-groups-single-agent)

    关键配置参考：[Gateway 网关配置](/zh-CN/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="如何将主机文件夹绑定到沙箱中？">
    将 `agents.defaults.sandbox.docker.binds` 设置为 `["host:path:mode"]`（例如 `"/home/user/src:/src:ro"`）。全局绑定与按智能体绑定会合并；当 `scope: "shared"` 时，会忽略按智能体绑定。对于任何敏感内容，请使用 `:ro`，并记住绑定会绕过沙箱文件系统边界。

    OpenClaw 会根据规范化路径以及通过最深层现有祖先解析得到的规范路径，双重验证绑定源。这意味着即使最后一个路径段尚不存在，通过符号链接父目录逃逸也会被默认拒绝，并且在符号链接解析后仍会应用允许根路径检查。

    示例与安全说明请参见 [沙箱隔离](/zh-CN/gateway/sandboxing#custom-bind-mounts) 和 [沙箱 vs 工具策略 vs 提权](/zh-CN/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check)。

  </Accordion>

  <Accordion title="记忆是如何工作的？">
    OpenClaw 的记忆就是智能体工作区中的 Markdown 文件：

    - `memory/YYYY-MM-DD.md` 中的每日笔记
    - `MEMORY.md` 中整理过的长期笔记（仅主 / 私有会话）

    OpenClaw 还会运行一个**静默的压缩前记忆刷新**，提醒模型
    在自动压缩前写入持久笔记。它只会在工作区
    可写时运行（只读沙箱会跳过）。参见 [记忆](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="记忆总是忘事。如何让它记住？">
    请让机器人**把事实写入记忆**。长期笔记应写入 `MEMORY.md`，
    短期上下文则写入 `memory/YYYY-MM-DD.md`。

    这仍然是我们正在改进的领域。提醒模型存储记忆会有帮助；
    它会知道该怎么做。如果它仍然经常遗忘，请确认 Gateway 网关每次运行时都在使用同一个
    工作区。

    文档：[记忆](/zh-CN/concepts/memory)、[智能体工作区](/zh-CN/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="记忆会永久保存吗？有什么限制？">
    记忆文件存储在磁盘上，并会一直保留，直到你删除它们。限制来自你的
    存储空间，而不是模型。**会话上下文**仍然受模型
    上下文窗口限制，因此长对话可能会被压缩或截断。这也是为什么会有
    记忆搜索——它只会把相关部分重新拉回上下文。

    文档：[记忆](/zh-CN/concepts/memory)、[上下文](/zh-CN/concepts/context)。

  </Accordion>

  <Accordion title="语义记忆搜索需要 OpenAI API 密钥吗？">
    只有当你使用 **OpenAI embeddings** 时才需要。Codex OAuth 只覆盖聊天 / completions，
    **不**授予 embeddings 访问权限，因此**使用 Codex 登录（OAuth 或
    Codex CLI 登录）**并不能帮助启用语义记忆搜索。OpenAI embeddings
    仍然需要真实的 API 密钥（`OPENAI_API_KEY` 或 `models.providers.openai.apiKey`）。

    如果你没有显式设置提供商，只要 OpenClaw
    能解析出 API 密钥（凭证配置文件、`models.providers.*.apiKey` 或环境变量），它就会自动选择提供商。
    如果能解析出 OpenAI 密钥，它会优先选择 OpenAI；否则如果能解析出 Gemini 密钥，则使用 Gemini；
    再之后是 Voyage，然后是 Mistral。如果没有可用的远程密钥，记忆
    搜索会保持禁用，直到你进行配置。如果你已经配置了本地模型路径
    并且该路径存在，OpenClaw
    会优先选择 `local`。当你显式设置
    `memorySearch.provider = "ollama"` 时，也支持 Ollama。

    如果你更想保持本地化，请设置 `memorySearch.provider = "local"`（并可选设置
    `memorySearch.fallback = "none"`）。如果你想使用 Gemini embeddings，请设置
    `memorySearch.provider = "gemini"` 并提供 `GEMINI_API_KEY`（或
    `memorySearch.remote.apiKey`）。我们支持 **OpenAI、Gemini、Voyage、Mistral、Ollama 或 local**
    embedding 模型——设置详情请参见 [记忆](/zh-CN/concepts/memory)。

  </Accordion>
</AccordionGroup>

## 磁盘上的文件位置

<AccordionGroup>
  <Accordion title="OpenClaw 使用的所有数据都保存在本地吗？">
    不是——**OpenClaw 的状态保存在本地**，但**外部服务仍然会看到你发送给它们的内容**。

    - **默认本地：**会话、记忆文件、配置和工作区位于 Gateway 网关主机上
      （`~/.openclaw` + 你的工作区目录）。
    - **因需要而远程：**你发送给模型提供商（Anthropic / OpenAI / 等）的消息会发送到
      它们的 API，聊天平台（WhatsApp / Telegram / Slack / 等）也会在
      它们的服务器上存储消息数据。
    - **足迹由你控制：**使用本地模型可将 prompts 保留在你的机器上，但渠道
      流量仍会经过相应渠道的服务器。

    相关内容：[智能体工作区](/zh-CN/concepts/agent-workspace)、[记忆](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="OpenClaw 把数据存在哪里？">
    所有内容都位于 `$OPENCLAW_STATE_DIR` 下（默认：`~/.openclaw`）：

    | Path                                                            | Purpose                                                            |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | 主配置（JSON5）                                                    |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | 旧版 OAuth 导入（首次使用时复制到凭证配置文件）                   |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | 凭证配置文件（OAuth、API 密钥，以及可选的 `keyRef` / `tokenRef`） |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef 提供商的可选文件后备密钥载荷                     |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | 旧版兼容文件（静态 `api_key` 条目已清除）                         |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | 提供商状态（例如 `whatsapp/<accountId>/creds.json`）              |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | 每个智能体的状态（agentDir + sessions）                           |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | 对话历史与状态（每个智能体）                                      |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | 会话元数据（每个智能体）                                          |

    旧版单智能体路径：`~/.openclaw/agent/*`（由 `openclaw doctor` 迁移）。

    你的**工作区**（AGENTS.md、记忆文件、skills 等）是独立的，并通过 `agents.defaults.workspace` 配置（默认：`~/.openclaw/workspace`）。

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md 应该放在哪里？">
    这些文件位于**智能体工作区**中，而不是 `~/.openclaw`。

    - **工作区（按智能体）**：`AGENTS.md`、`SOUL.md`、`IDENTITY.md`、`USER.md`、
      `MEMORY.md`（若无 `MEMORY.md` 则回退到旧版 `memory.md`）、
      `memory/YYYY-MM-DD.md`、可选的 `HEARTBEAT.md`。
    - **状态目录（`~/.openclaw`）**：配置、渠道 / 提供商状态、凭证配置文件、会话、日志，
      以及共享 skills（`~/.openclaw/skills`）。

    默认工作区是 `~/.openclaw/workspace`，可通过以下方式配置：

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    如果机器人在重启后“忘记”了内容，请确认 Gateway 网关在每次启动时都在使用同一个
    工作区（并记住：远程模式使用的是**Gateway 网关主机上的**
    工作区，而不是你的本地笔记本）。

    提示：如果你想保留某个持久行为或偏好，请让机器人**将其写入
    AGENTS.md 或 MEMORY.md**，而不是依赖聊天历史。

    参见 [智能体工作区](/zh-CN/concepts/agent-workspace) 和 [记忆](/zh-CN/concepts/memory)。

  </Accordion>

  <Accordion title="推荐的备份策略">
    将你的**智能体工作区**放入一个**私有** git 仓库，并备份到某个
    私有位置（例如 GitHub 私有仓库）。这样可以保留记忆 + AGENTS / SOUL / USER
    文件，并让你以后恢复助手的“心智”。

    **不要**提交 `~/.openclaw` 下的任何内容（凭证、会话、token 或加密后的 secrets 载荷）。
    如果你需要完整恢复，请分别备份工作区和状态目录
    （参见上面的迁移问题）。

    文档：[智能体工作区](/zh-CN/concepts/agent-workspace)。

  </Accordion>

  <Accordion title="如何彻底卸载 OpenClaw？">
    请参见专门指南：[卸载](/zh-CN/install/uninstall)。
  </Accordion>

  <Accordion title="智能体可以在工作区之外工作吗？">
    可以。工作区是**默认 cwd** 和记忆锚点，而不是硬沙箱。
    相对路径会在工作区内解析，但绝对路径仍可访问其他
    主机位置，除非启用了沙箱隔离。如果你需要隔离，请使用
    [`agents.defaults.sandbox`](/zh-CN/gateway/sandboxing) 或按智能体的沙箱设置。如果你
    想把某个仓库作为默认工作目录，请将该智能体的
    `workspace` 指向仓库根目录。OpenClaw 仓库只是源代码；除非你有意让智能体在其中工作，否则请将
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
    会话状态归**Gateway 网关主机**所有。如果你处于远程模式，那么你关心的会话存储位于远程机器上，而不是本地笔记本。参见 [会话管理](/zh-CN/concepts/session)。
  </Accordion>
</AccordionGroup>

## 配置基础

<AccordionGroup>
  <Accordion title="配置是什么格式？在哪里？">
    OpenClaw 从 `$OPENCLAW_CONFIG_PATH` 读取可选的 **JSON5** 配置（默认：`~/.openclaw/openclaw.json`）：

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    如果该文件不存在，它会使用相对安全的默认值（包括默认工作区 `~/.openclaw/workspace`）。

  </Accordion>

  <Accordion title='我设置了 gateway.bind: "lan"（或 "tailnet"），现在没有任何监听 / UI 显示 unauthorized'>
    非 loopback 绑定**要求有效的 gateway auth 路径**。实际上这意味着：

    - 共享密钥身份验证：token 或密码
    - 配置正确的非 loopback、具身份感知的反向代理后，使用 `gateway.auth.mode: "trusted-proxy"`

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

    - `gateway.remote.token` / `.password` **不会**自行启用本地 gateway 身份验证。
    - 只有在 `gateway.auth.*` 未设置时，本地调用路径才能使用 `gateway.remote.*` 作为回退。
    - 对于密码身份验证，请设置 `gateway.auth.mode: "password"` 加上 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
    - 如果通过 SecretRef 显式配置了 `gateway.auth.token` / `gateway.auth.password` 但无法解析，则会默认拒绝解析（不会用远程回退掩盖）。
    - 共享密钥 Control UI 设置通过 `connect.params.auth.token` 或 `connect.params.auth.password` 进行身份验证（存储在应用 / UI 设置中）。像 Tailscale Serve 或 `trusted-proxy` 这样的带身份模式则改用请求头。避免把共享密钥放在 URL 中。
    - 使用 `gateway.auth.mode: "trusted-proxy"` 时，同主机上的 loopback 反向代理**仍然不会**满足 trusted-proxy 身份验证要求。受信任代理必须是配置好的非 loopback 来源。

  </Accordion>

  <Accordion title="为什么现在在 localhost 上也需要 token？">
    OpenClaw 默认强制启用 gateway 身份验证，包括 loopback。在正常默认路径中，这意味着 token 身份验证：如果没有显式配置身份验证路径，gateway 启动会解析为 token 模式并自动生成一个 token，将其保存到 `gateway.auth.token`，因此**本地 WS 客户端也必须进行身份验证**。这样可以阻止其他本地进程调用 Gateway 网关。

    如果你更喜欢其他身份验证路径，可以显式选择密码模式（或者，对于非 loopback 的具身份感知反向代理，使用 `trusted-proxy`）。如果你**确实**想开放 loopback，请在配置中显式设置 `gateway.auth.mode: "none"`。Doctor 可随时为你生成 token：`openclaw doctor --generate-gateway-token`。

  </Accordion>

  <Accordion title="更改配置后需要重启吗？">
    Gateway 网关会监视配置并支持热重载：

    - `gateway.reload.mode: "hybrid"`（默认）：安全更改热应用，关键更改则重启
    - 也支持 `hot`、`restart`、`off`

  </Accordion>

  <Accordion title="如何关闭有趣的 CLI 标语？">
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

    - `off`：隐藏标语文本，但保留横幅标题 / 版本行。
    - `default`：始终使用 `All your chats, one OpenClaw.`。
    - `random`：轮换有趣 / 季节性标语（默认行为）。
    - 如果你完全不想要横幅，请设置环境变量 `OPENCLAW_HIDE_BANNER=1`。

  </Accordion>

  <Accordion title="如何启用 Web 搜索（以及 Web 抓取）？">
    `web_fetch` 无需 API 密钥即可工作。`web_search` 则取决于你选择的
    提供商：

    - 基于 API 的提供商，如 Brave、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Perplexity 和 Tavily，需要按正常方式配置 API 密钥。
    - Ollama Web 搜索 不需要密钥，但它使用你配置的 Ollama 主机，并要求 `ollama signin`。
    - DuckDuckGo 不需要密钥，但这是一个非官方的基于 HTML 的集成。
    - SearXNG 是免密钥 / 自托管的；请配置 `SEARXNG_BASE_URL` 或 `plugins.entries.searxng.config.webSearch.baseUrl`。

    **推荐方式：**运行 `openclaw configure --section web` 并选择一个提供商。
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

    提供商特定的 Web 搜索配置现在位于 `plugins.entries.<plugin>.config.webSearch.*` 下。
    出于兼容性考虑，旧版 `tools.web.search.*` 提供商路径目前仍可加载，但不应再用于新配置。
    Firecrawl 的 Web 抓取回退配置位于 `plugins.entries.firecrawl.config.webFetch.*` 下。

    说明：

    - 如果你使用允许列表，请添加 `web_search` / `web_fetch` / `x_search` 或 `group:web`。
    - `web_fetch` 默认启用（除非显式禁用）。
    - 如果省略 `tools.web.fetch.provider`，OpenClaw 会从可用凭证中自动检测第一个已就绪的抓取回退提供商。目前内置提供商是 Firecrawl。
    - 守护进程会从 `~/.openclaw/.env`（或服务环境）读取环境变量。

    文档：[Web 工具](/zh-CN/tools/web)。

  </Accordion>

  <Accordion title="config.apply 把我的配置清空了。如何恢复并避免这种情况？">
    `config.apply` 会替换**整个配置**。如果你传入的是部分对象，其余内容
    都会被删除。

    恢复方法：

    - 从备份恢复（git 或复制的 `~/.openclaw/openclaw.json`）。
    - 如果没有备份，请重新运行 `openclaw doctor` 并重新配置渠道 / 模型。
    - 如果这不是预期行为，请提交 bug，并附上你最后已知的配置或任何备份。
    - 本地编码智能体通常可以根据日志或历史记录重建一个可工作的配置。

    避免方法：

    - 小改动请使用 `openclaw config set`。
    - 交互式编辑请使用 `openclaw configure`。
    - 当你不确定确切路径或字段结构时，先使用 `config.schema.lookup`；它会返回一个浅层 schema 节点和直接子项摘要，便于逐层钻取。
    - 对于部分 RPC 编辑，请使用 `config.patch`；仅在确实需要完整替换配置时才使用 `config.apply`。
    - 如果你在智能体运行中使用仅限所有者的 `gateway` 工具，它仍会拒绝写入 `tools.exec.ask` / `tools.exec.security`（包括会规范化到相同受保护 exec 路径的旧版 `tools.bash.*` 别名）。

    文档：[配置](/cli/config)、[配置向导](/cli/configure)、[Doctor](/zh-CN/gateway/doctor)。

  </Accordion>

  <Accordion title="如何在多设备上运行一个中央 Gateway 网关，并配合专用 worker？">
    常见模式是**一个 Gateway 网关**（例如 Raspberry Pi）配合**节点**和**智能体**：

    - **Gateway 网关（中心）：**负责渠道（Signal / WhatsApp）、路由和会话。
    - **节点（设备）：**Mac / iOS / Android 作为外设连接，暴露本地工具（`system.run`、`canvas`、`camera`）。
    - **智能体（workers）：**拥有各自工作区 / 角色的独立“大脑”（例如“Hetzner 运维”“个人数据”）。
    - **子智能体：**当你想并行处理时，从主智能体中启动后台任务。
    - **TUI：**连接到 Gateway 网关并切换智能体 / 会话。

    文档：[节点](/zh-CN/nodes)、[远程访问](/zh-CN/gateway/remote)、[多智能体路由](/zh-CN/concepts/multi-agent)、[子智能体](/zh-CN/tools/subagents)、[TUI](/web/tui)。

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

    默认是 `false`（有头模式）。无头模式更容易在某些站点触发反机器人检查。参见 [浏览器](/zh-CN/tools/browser)。

    无头模式使用**相同的 Chromium 引擎**，适用于大多数自动化场景（表单、点击、抓取、登录）。主要区别在于：

    - 没有可见浏览器窗口（如果你需要视觉信息，请使用截图）。
    - 某些站点对无头模式下的自动化更严格（CAPTCHA、反机器人）。
      例如，X / Twitter 常常会阻止无头会话。

  </Accordion>

  <Accordion title="如何使用 Brave 进行浏览器控制？">
    将 `browser.executablePath` 设置为你的 Brave 二进制文件（或任意基于 Chromium 的浏览器），然后重启 Gateway 网关。
    完整配置示例请参见 [浏览器](/zh-CN/tools/browser#use-brave-or-another-chromium-based-browser)。
  </Accordion>
</AccordionGroup>

## 远程 Gateway 网关与节点

<AccordionGroup>
  <Accordion title="命令如何在 Telegram、gateway 和节点之间传播？">
    Telegram 消息由 **gateway** 处理。gateway 运行智能体，
    只有在需要节点工具时，才会通过 **Gateway WebSocket** 调用节点：

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    节点看不到入站提供商流量；它们只接收节点 RPC 调用。

  </Accordion>

  <Accordion title="如果 Gateway 网关托管在远程环境中，我的智能体如何访问我的电脑？">
    简短回答：**将你的电脑配对为节点**。Gateway 网关运行在其他地方，但它可以
    通过 Gateway WebSocket 在你的本地机器上调用 `node.*` 工具（屏幕、摄像头、system）。

    典型设置：

    1. 在常开主机（VPS / 家庭服务器）上运行 Gateway 网关。
    2. 将 Gateway 网关主机和你的电脑放到同一个 tailnet 中。
    3. 确保 Gateway 网关 WS 可访问（tailnet 绑定或 SSH 隧道）。
    4. 在本地打开 macOS 应用，并以**通过 SSH 远程连接**模式（或直接 tailnet）
       连接，以便它注册为节点。
    5. 在 Gateway 网关上批准该节点：

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    不需要单独的 TCP bridge；节点通过 Gateway WebSocket 连接。

    安全提醒：配对 macOS 节点意味着允许在该机器上运行 `system.run`。
    只配对你信任的设备，并查看 [安全](/zh-CN/gateway/security)。

    文档：[节点](/zh-CN/nodes)、[Gateway 网关协议](/zh-CN/gateway/protocol)、[macOS 远程模式](/zh-CN/platforms/mac/remote)、[安全](/zh-CN/gateway/security)。

  </Accordion>

  <Accordion title="Tailscale 已连接，但我收不到回复。现在怎么办？">
    先检查基础项：

    - Gateway 网关正在运行：`openclaw gateway status`
    - Gateway 网关健康状态：`openclaw status`
    - 渠道健康状态：`openclaw channels status`

    然后验证身份验证和路由：

    - 如果你使用 Tailscale Serve，请确认 `gateway.auth.allowTailscale` 设置正确。
    - 如果你通过 SSH 隧道连接，请确认本地隧道已建立，并指向正确端口。
    - 确认你的允许列表（私信或群组）包含你的账户。

    文档：[Tailscale](/zh-CN/gateway/tailscale)、[远程访问](/zh-CN/gateway/remote)、[渠道](/zh-CN/channels)。

  </Accordion>

  <Accordion title="两个 OpenClaw 实例可以互相通信吗（本地 + VPS）？">
    可以。没有内置的“机器人对机器人”桥接，但你可以通过几种
    可靠方式将其接起来：

    **最简单方式：**使用两个机器人都能访问的普通聊天渠道（Telegram / Slack / WhatsApp）。
    让机器人 A 给机器人 B 发消息，然后让机器人 B 像平常一样回复。

    **CLI 桥接（通用）：**运行一个脚本，通过
    `openclaw agent --message ... --deliver` 调用另一个 Gateway 网关，目标设为另一个机器人
    正在监听的聊天。如果某个机器人位于远程 VPS 上，请通过 SSH / Tailscale
    将你的 CLI 指向该远程 Gateway 网关（参见 [远程访问](/zh-CN/gateway/remote)）。

    示例模式（在一台能访问目标 Gateway 网关的机器上运行）：

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    提示：增加一个防护措施，避免两个机器人无限循环回复（仅回应提及、
    渠道允许列表，或“不要回复机器人消息”的规则）。

    文档：[远程访问](/zh-CN/gateway/remote)、[智能体 CLI](/cli/agent)、[智能体发送](/zh-CN/tools/agent-send)。

  </Accordion>

  <Accordion title="多个智能体需要分别使用不同的 VPS 吗？">
    不需要。一个 Gateway 网关可以托管多个智能体，每个智能体都有自己的工作区、默认模型
    和路由。这是正常设置，比每个智能体运行一个 VPS
    更便宜也更简单。

    只有在你需要硬隔离（安全边界）或
    不想共享的截然不同配置时，才需要单独的 VPS。否则，保留一个 Gateway 网关，
    并使用多个智能体或子智能体即可。

  </Accordion>

  <Accordion title="相比从 VPS 通过 SSH 访问，在个人笔记本上使用节点有什么好处？">
    有——节点是从远程 Gateway 网关访问你笔记本的首选方式，而且
    它们提供的不仅仅是 shell 访问。Gateway 网关运行于 macOS / Linux（Windows 通过 WSL2），并且
    十分轻量（小型 VPS 或 Raspberry Pi 级设备就足够；4 GB 内存完全够用），因此一种常见
    设置是常开主机 + 你的笔记本作为节点。

    - **无需入站 SSH。**节点主动连接到 Gateway WebSocket，并使用设备配对。
    - **更安全的执行控制。**`system.run` 在该笔记本上受节点允许列表 / 审批控制。
    - **更多设备工具。**节点除了 `system.run` 外，还暴露 `canvas`、`camera` 和 `screen`。
    - **本地浏览器自动化。**将 Gateway 网关放在 VPS 上，但通过笔记本上的节点主机在本地运行 Chrome，或通过 Chrome MCP 连接主机上的本地 Chrome。

    SSH 适合临时 shell 访问，但对于持续的智能体工作流和
    设备自动化，节点更简单。

    文档：[节点](/zh-CN/nodes)、[节点 CLI](/cli/nodes)、[浏览器](/zh-CN/tools/browser)。

  </Accordion>

  <Accordion title="节点会运行 gateway 服务吗？">
    不会。除非你有意运行隔离配置文件（参见 [多个 Gateway 网关](/zh-CN/gateway/multiple-gateways)），否则每台主机上只应运行**一个 gateway**。节点是连接到
    gateway 的外设（iOS / Android 节点，或菜单栏应用中的 macOS “node mode”）。有关无头节点
    主机和 CLI 控制，请参见 [节点主机 CLI](/cli/node)。

    对 `gateway`、`discovery` 和 `canvasHost` 的更改需要完整重启。

  </Accordion>

  <Accordion title="有没有 API / RPC 方式来应用配置？">
    有。

    - `config.schema.lookup`：在写入前检查一个配置子树，包括其浅层 schema 节点、匹配的 UI 提示和直接子项摘要
    - `config.get`：获取当前快照 + hash
    - `config.patch`：安全的部分更新（大多数 RPC 编辑推荐）
    - `config.apply`：验证并替换完整配置，然后重启
    - 仅限所有者的 `gateway` 运行时工具仍然拒绝重写 `tools.exec.ask` / `tools.exec.security`；旧版 `tools.bash.*` 别名会被规范化到同样受保护的 exec 路径

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

  <Accordion title="如何在 VPS 上设置 Tailscale 并从 Mac 连接？">
    最简步骤如下：

    1. **在 VPS 上安装并登录**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **在你的 Mac 上安装并登录**
       - 使用 Tailscale 应用并登录到同一个 tailnet。
    3. **启用 MagicDNS（推荐）**
       - 在 Tailscale 管理控制台中启用 MagicDNS，让 VPS 拥有稳定名称。
    4. **使用 tailnet 主机名**
       - SSH：`ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway 网关 WS：`ws://your-vps.tailnet-xxxx.ts.net:18789`

    如果你想在不使用 SSH 的情况下访问 Control UI，请在 VPS 上使用 Tailscale Serve：

    ```bash
    openclaw gateway --tailscale serve
    ```

    这样会让 gateway 保持绑定到 loopback，并通过 Tailscale 暴露 HTTPS。参见 [Tailscale](/zh-CN/gateway/tailscale)。

  </Accordion>

  <Accordion title="如何将 Mac 节点连接到远程 Gateway 网关（Tailscale Serve）？">
    Serve 会暴露 **Gateway 网关 Control UI + WS**。节点通过同一个 Gateway WS 端点连接。

    推荐设置：

    1. **确保 VPS 和 Mac 在同一个 tailnet 中**。
    2. **在 Remote 模式下使用 macOS 应用**（SSH 目标可以是 tailnet 主机名）。
       应用会隧道化 Gateway 端口，并作为节点连接。
    3. **在 gateway 上批准该节点**：

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    文档：[Gateway 网关协议](/zh-CN/gateway/protocol)、[设备发现](/zh-CN/gateway/discovery)、[macOS 远程模式](/zh-CN/platforms/mac/remote)。

  </Accordion>

  <Accordion title="我应该在第二台笔记本上安装，还是只添加一个节点？">
    如果你只需要第二台笔记本上的**本地工具**（屏幕 / 摄像头 / exec），请把它添加为
    **节点**。这样可以保持单一 Gateway 网关，并避免重复配置。目前本地节点工具
    仅支持 macOS，但我们计划扩展到其他操作系统。

    只有在你需要**硬隔离**或两个完全独立的机器人时，才安装第二个 Gateway 网关。

    文档：[节点](/zh-CN/nodes)、[节点 CLI](/cli/nodes)、[多个 Gateway 网关](/zh-CN/gateway/multiple-gateways)。

  </Accordion>
</AccordionGroup>

## 环境变量和 .env 加载

<AccordionGroup>
  <Accordion title="OpenClaw 如何加载环境变量？">
    OpenClaw 会从父进程（shell、launchd / systemd、CI 等）读取环境变量，并另外加载：

    - 当前工作目录中的 `.env`
    - 来自 `~/.openclaw/.env` 的全局回退 `.env`（即 `$OPENCLAW_STATE_DIR/.env`）

    这两个 `.env` 文件都不会覆盖现有环境变量。

    你也可以在配置中定义内联环境变量（仅当进程环境中缺失时应用）：

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    完整优先级和来源请参见 [/environment](/zh-CN/help/environment)。

  </Accordion>

  <Accordion title="我通过服务启动 Gateway 网关后，环境变量消失了。怎么办？">
    两种常见修复方式：

    1. 将缺失的键放入 `~/.openclaw/.env`，这样即使服务没有继承你的 shell 环境，也能读取到。
    2. 启用 shell 导入（自选便利功能）：

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

  <Accordion title='我设置了 COPILOT_GITHUB_TOKEN，但 models status 显示 "Shell env: off."。为什么？'>
    `openclaw models status` 报告的是**是否启用了 shell 环境导入**。“Shell env: off”
    **并不**意味着你的环境变量缺失——它只是表示 OpenClaw 不会自动加载
    你的登录 shell。

    如果 Gateway 网关作为服务运行（launchd / systemd），它不会继承你的 shell
    环境。可通过以下任一方式修复：

    1. 将 token 放入 `~/.openclaw/.env`：

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. 或启用 shell 导入（`env.shellEnv.enabled: true`）。
    3. 或把它加入配置中的 `env` 块（仅在缺失时应用）。

    然后重启 gateway 并重新检查：

    ```bash
    openclaw models status
    ```

    Copilot token 读取自 `COPILOT_GITHUB_TOKEN`（也支持 `GH_TOKEN` / `GITHUB_TOKEN`）。
    参见 [/concepts/model-providers](/zh-CN/concepts/model-providers) 和 [/environment](/zh-CN/help/environment)。

  </Accordion>
</AccordionGroup>

## 会话与多个聊天

<AccordionGroup>
  <Accordion title="如何开始一个新的对话？">
    发送 `/new` 或 `/reset` 作为独立消息。参见 [会话管理](/zh-CN/concepts/session)。
  </Accordion>

  <Accordion title="如果我从不发送 /new，会话会自动重置吗？">
    会话会在 `session.idleMinutes` 到期后过期，但该功能**默认关闭**（默认值 **0**）。
    将其设置为正值即可启用空闲过期。启用后，空闲期之后的**下一条**
    消息会为该聊天键启动一个新的会话 ID。
    这不会删除转录——只是开始一个新会话。

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="有没有办法搭建一组 OpenClaw 实例（一个 CEO，多个智能体）？">
    有，通过**多智能体路由**和**子智能体**。你可以创建一个协调者
    智能体，以及若干拥有各自工作区和模型的工作智能体。

    不过，这更适合作为一个**有趣的实验**。它会消耗大量 token，而且通常
    不如使用一个机器人配合多个独立会话高效。我们通常设想的模式
    是：你与一个机器人交流，用不同会话并行处理工作。该
    机器人也可以在需要时启动子智能体。

    文档：[多智能体路由](/zh-CN/concepts/multi-agent)、[子智能体](/zh-CN/tools/subagents)、[智能体 CLI](/cli/agents)。

  </Accordion>

  <Accordion title="为什么上下文会在任务中途被截断？如何防止？">
    会话上下文受模型窗口限制。长聊天、大量工具输出或许多
    文件都可能触发压缩或截断。

    有帮助的做法：

    - 让机器人总结当前状态并写入文件。
    - 在长任务前使用 `/compact`，切换主题时使用 `/new`。
    - 将重要上下文保留在工作区中，并让机器人重新读取它。
    - 对于长任务或并行工作，使用子智能体，这样主聊天会更小。
    - 如果这种情况经常发生，请选择上下文窗口更大的模型。

  </Accordion>

  <Accordion title="如何彻底重置 OpenClaw 但保留安装？">
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

    - 如果检测到现有配置，新手引导也会提供 **Reset**。参见 [设置向导（CLI）](/zh-CN/start/wizard)。
    - 如果你使用了配置文件（`--profile` / `OPENCLAW_PROFILE`），请重置每个状态目录（默认是 `~/.openclaw-<profile>`）。
    - 开发重置：`openclaw gateway --dev --reset`（仅开发用途；会清除开发配置 + 凭证 + 会话 + 工作区）。

  </Accordion>

  <Accordion title='我遇到 "context too large" 错误——如何重置或压缩？'>
    请使用以下方法之一：

    - **压缩**（保留对话，但总结较旧轮次）：

      ```
      /compact
      ```

      或使用 `/compact <instructions>` 来指导摘要内容。

    - **重置**（为同一聊天键创建新的会话 ID）：

      ```
      /new
      /reset
      ```

    如果这种情况持续发生：

    - 启用或调整**会话裁剪**（`agents.defaults.contextPruning`）以修剪旧工具输出。
    - 使用上下文窗口更大的模型。

    文档：[压缩](/zh-CN/concepts/compaction)、[会话裁剪](/zh-CN/concepts/session-pruning)、[会话管理](/zh-CN/concepts/session)。

  </Accordion>

  <Accordion title='为什么我会看到 "LLM request rejected: messages.content.tool_use.input field required"？'>
    这是一个提供商校验错误：模型发出了一个 `tool_use` 块，但缺少必需的
    `input`。这通常意味着会话历史已过时或损坏（常见于长线程
    或工具 / schema 变更之后）。

    修复方法：通过 `/new`（独立消息）开启一个新会话。

  </Accordion>

  <Accordion title="为什么我每 30 分钟会收到 heartbeat 消息？">
    Heartbeat 默认每 **30m** 运行一次（使用 OAuth 凭证时为 **1h**）。可以调整或禁用它们：

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // 或 "0m" 以禁用
          },
        },
      },
    }
    ```

    如果 `HEARTBEAT.md` 存在但实际上为空（仅包含空行和 Markdown
    标题如 `# Heading`），OpenClaw 会跳过 heartbeat 运行以节省 API 调用。
    如果文件不存在，heartbeat 仍会运行，并由模型决定要做什么。

    按智能体覆盖请使用 `agents.list[].heartbeat`。文档：[Heartbeat](/zh-CN/gateway/heartbeat)。

  </Accordion>

  <Accordion title='我需要把一个“机器人账号”加入 WhatsApp 群组吗？'>
    不需要。OpenClaw 运行在**你自己的账号**上，所以只要你在群组里，OpenClaw 就能看到它。
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

    找到以 `@g.us` 结尾的 `chatId`（或 `from`），例如：
    `1234567890-1234567890@g.us`。

    方式 2（如果已配置 / 已加入允许列表）：从配置中列出群组：

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    文档：[WhatsApp](/zh-CN/channels/whatsapp)、[目录](/cli/directory)、[日志](/cli/logs)。

  </Accordion>

  <Accordion title="为什么 OpenClaw 在群组中不回复？">
    两个常见原因：

    - 提及门控已启用（默认）。你必须 @ 提及机器人（或匹配 `mentionPatterns`）。
    - 你配置了 `channels.whatsapp.groups`，但没有包含 `"*"`，而且该群组不在允许列表中。

    参见 [群组](/zh-CN/channels/groups) 和 [群组消息](/zh-CN/channels/group-messages)。

  </Accordion>

  <Accordion title="群组 / 线程会与私信共享上下文吗？">
    直接聊天默认会折叠到主会话。群组 / 渠道拥有各自的会话键，Telegram 主题 / Discord 线程也都是独立会话。参见 [群组](/zh-CN/channels/groups) 和 [群组消息](/zh-CN/channels/group-messages)。
  </Accordion>

  <Accordion title="我可以创建多少个工作区和智能体？">
    没有硬性限制。几十个（甚至上百个）都可以，但请注意：

    - **磁盘增长：**会话 + 转录文件存储在 `~/.openclaw/agents/<agentId>/sessions/` 下。
    - **Token 成本：**更多智能体意味着更多并发模型使用。
    - **运维开销：**按智能体划分的凭证配置文件、工作区和渠道路由。

    提示：

    - 每个智能体保留一个**活跃**工作区（`agents.defaults.workspace`）。
    - 如果磁盘增长，裁剪旧会话（删除 JSONL 或存储条目）。
    - 使用 `openclaw doctor` 发现游离工作区和配置文件不匹配问题。

  </Accordion>

  <Accordion title="我可以同时运行多个机器人或聊天（Slack）吗？应该如何设置？">
    可以。使用**多智能体路由**来运行多个隔离的智能体，并按
    渠道 / 账户 / peer 路由入站消息。Slack 支持作为一个渠道，并且可以绑定到特定智能体。

    浏览器访问能力很强，但并不等于“人能做的都能做”——反机器人机制、CAPTCHA 和 MFA
    仍然会阻止自动化。若要获得最可靠的浏览器控制，请在主机上使用本地 Chrome MCP，
    或在实际运行浏览器的机器上使用 CDP。

    最佳实践设置：

    - 常开 Gateway 网关主机（VPS / Mac mini）。
    - 每个角色一个智能体（bindings）。
    - 将 Slack 渠道绑定到这些智能体。
    - 在需要时通过 Chrome MCP 或节点使用本地浏览器。

    文档：[多智能体路由](/zh-CN/concepts/multi-agent)、[Slack](/zh-CN/channels/slack)、
    [浏览器](/zh-CN/tools/browser)、[节点](/zh-CN/nodes)。

  </Accordion>
</AccordionGroup>

## 模型：默认值、选择、别名与切换

<AccordionGroup>
  <Accordion title='什么是“默认模型”？'>
    OpenClaw 的默认模型就是你设置为：

    ```
    agents.defaults.model.primary
    ```

    模型以 `provider/model` 的形式引用（例如：`openai/gpt-5.4`）。如果你省略提供商，OpenClaw 会先尝试别名，然后尝试对该精确模型 ID 进行唯一的已配置提供商匹配，最后才退回到已配置的默认提供商这一已废弃的兼容路径。如果该提供商不再暴露已配置的默认模型，OpenClaw 会退回到第一个已配置的提供商 / 模型，而不是继续暴露一个过时、已移除提供商的默认值。你仍然应该**显式**设置 `provider/model`。

  </Accordion>

  <Accordion title="你推荐什么模型？">
    **推荐默认值：**使用你提供商栈中最新一代、能力最强的模型。
    **对于启用工具或面对不可信输入的智能体：**优先考虑模型能力，而不是成本。
    **对于日常 / 低风险聊天：**使用更便宜的回退模型，并按智能体角色进行路由。

    MiniMax 有单独的文档：[MiniMax](/zh-CN/providers/minimax) 和
    [本地模型](/zh-CN/gateway/local-models)。

    经验法则：对高风险工作使用**你负担得起的最佳模型**，而对日常
    聊天或摘要使用更便宜的模型。你可以按智能体路由模型，并使用子智能体并行化
    长任务（每个子智能体都会消耗 token）。参见 [模型](/zh-CN/concepts/models) 和
    [子智能体](/zh-CN/tools/subagents)。

    强烈警告：较弱 / 过度量化的模型更容易受到 prompt
    injection 和不安全行为的影响。参见 [安全](/zh-CN/gateway/security)。

    更多背景：[模型](/zh-CN/concepts/models)。

  </Accordion>

  <Accordion title="如何在不清空配置的情况下切换模型？">
    使用**模型命令**或仅编辑**模型**字段。避免完整替换配置。

    安全选项：

    - 在聊天中使用 `/model`（快速，按会话）
    - `openclaw models set ...`（仅更新模型配置）
    - `openclaw configure --section model`（交互式）
    - 编辑 `~/.openclaw/openclaw.json` 中的 `agents.defaults.model`

    除非你确实打算替换整个配置，否则避免对部分对象使用 `config.apply`。
    对于 RPC 编辑，请先用 `config.schema.lookup` 检查，并优先使用 `config.patch`。lookup 载荷会给出规范化路径、浅层 schema 文档 / 约束以及直接子项摘要。
    用于部分更新。
    如果你确实覆盖了配置，请从备份恢复，或重新运行 `openclaw doctor` 进行修复。

    文档：[模型](/zh-CN/concepts/models)、[配置向导](/cli/configure)、[配置](/cli/config)、[Doctor](/zh-CN/gateway/doctor)。

  </Accordion>

  <Accordion title="可以使用自托管模型（llama.cpp、vLLM、Ollama）吗？">
    可以。Ollama 是本地模型最简单的路径。

    最快设置方式：

    1. 从 `https://ollama.com/download` 安装 Ollama
    2. 拉取一个本地模型，例如 `ollama pull glm-4.7-flash`
    3. 如果你还想使用云模型，请运行 `ollama signin`
    4. 运行 `openclaw onboard` 并选择 `Ollama`
    5. 选择 `Local` 或 `Cloud + Local`

    说明：

    - `Cloud + Local` 会同时提供云模型和你的本地 Ollama 模型
    - 像 `kimi-k2.5:cloud` 这样的云模型不需要本地 pull
    - 如需手动切换，可使用 `openclaw models list` 和 `openclaw models set ollama/<model>`

    安全说明：较小或高度量化的模型更容易受到 prompt
    injection 的影响。对于任何能够使用工具的机器人，我们强烈推荐**大模型**。
    如果你仍想使用小模型，请启用沙箱隔离和严格的工具允许列表。

    文档：[Ollama](/zh-CN/providers/ollama)、[本地模型](/zh-CN/gateway/local-models)、
    [模型提供商](/zh-CN/concepts/model-providers)、[安全](/zh-CN/gateway/security)、
    [沙箱隔离](/zh-CN/gateway/sandboxing)。

  </Accordion>

  <Accordion title="OpenClaw、Flawd 和 Krill 使用什么模型？">
    - 这些部署可能不同，并且会随时间变化；没有固定的提供商推荐。
    - 在每个 gateway 上使用 `openclaw models status` 检查当前运行时设置。
    - 对于安全敏感 / 启用工具的智能体，请使用当前可用的最新一代最强模型。
  </Accordion>

  <Accordion title="如何动态切换模型（无需重启）？">
    使用 `/model` 命令作为独立消息：

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    这些是内置别名。自定义别名可通过 `agents.defaults.models` 添加。

    你可以使用 `/model`、`/model list` 或 `/model status` 列出可用模型。

    `/model`（以及 `/model list`）会显示一个紧凑的编号选择器。通过数字选择：

    ```
    /model 3
    ```

    你还可以为该提供商强制指定特定凭证配置文件（按会话）：

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    提示：`/model status` 会显示当前活跃的是哪个智能体、正在使用哪个 `auth-profiles.json` 文件，以及下一个将尝试哪个凭证配置文件。
    如果可用，它还会显示已配置的提供商端点（`baseUrl`）和 API 模式（`api`）。

    **如何取消固定我通过 @profile 设置的配置文件？**

    重新运行 `/model`，但**不要**带上 `@profile` 后缀：

    ```
    /model anthropic/claude-opus-4-6
    ```

    如果你想回到默认值，请从 `/model` 中选择它（或发送 `/model <default provider/model>`）。
    使用 `/model status` 确认当前活动的凭证配置文件。

  </Accordion>

  <Accordion title="我可以用 GPT 5.2 处理日常任务，用 Codex 5.3 进行编码吗？">
    可以。把一个设为默认值，并在需要时切换：

    - **快速切换（按会话）：**日常任务使用 `/model gpt-5.4`，编码使用 `/model openai-codex/gpt-5.4` 搭配 Codex OAuth。
    - **默认值 + 切换：**将 `agents.defaults.model.primary` 设为 `openai/gpt-5.4`，然后在编码时切换到 `openai-codex/gpt-5.4`（或反过来）。
    - **子智能体：**将编码任务路由到具有不同默认模型的子智能体。

    参见 [模型](/zh-CN/concepts/models) 和 [斜杠命令](/zh-CN/tools/slash-commands)。

  </Accordion>

  <Accordion title="如何为 GPT 5.4 配置快速模式？">
    你可以使用会话级开关，或配置默认值：

    - **按会话：**当会话正在使用 `openai/gpt-5.4` 或 `openai-codex/gpt-5.4` 时，发送 `/fast on`。
    - **按模型默认值：**设置 `agents.defaults.models["openai/gpt-5.4"].params.fastMode` 为 `true`。
    - **Codex OAuth 也适用：**如果你也使用 `openai-codex/gpt-5.4`，请在其上设置相同标志。

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

    对于 OpenAI，快速模式会在支持的原生 Responses 请求上映射为 `service_tier = "priority"`。会话级 `/fast` 覆盖优先于配置默认值。

    参见 [Thinking 与快速模式](/zh-CN/tools/thinking) 和 [OpenAI 快速模式](/zh-CN/providers/openai#openai-fast-mode)。

  </Accordion>

  <Accordion title='为什么我会看到 "Model ... is not allowed"，然后就没有回复了？'>
    如果设置了 `agents.defaults.models`，它就会成为 `/model` 和任何
    会话覆盖的**允许列表**。选择不在该列表中的模型会返回：

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    该错误会**替代**正常回复返回。修复方法：将该模型添加到
    `agents.defaults.models`，移除允许列表，或从 `/model list` 中选择一个模型。

  </Accordion>

  <Accordion title='为什么我会看到 "Unknown model: minimax/MiniMax-M2.7"？'>
    这意味着**提供商未配置**（未找到 MiniMax 提供商配置或凭证
    配置文件），因此无法解析该模型。

    修复检查清单：

    1. 升级到当前 OpenClaw 版本（或直接从源码 `main` 运行），然后重启 gateway。
    2. 确保 MiniMax 已配置（向导或 JSON），或者环境变量 / 凭证配置文件中存在
       MiniMax 凭证，以便注入匹配的提供商
       （`MINIMAX_API_KEY` 对应 `minimax`，`MINIMAX_OAUTH_TOKEN` 或已存储的 MiniMax
       OAuth 对应 `minimax-portal`）。
    3. 为你的凭证路径使用精确模型 ID（区分大小写）：
       API 密钥设置使用 `minimax/MiniMax-M2.7` 或 `minimax/MiniMax-M2.7-highspeed`，
       OAuth 设置使用 `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed`。
    4. 运行：

       ```bash
       openclaw models list
       ```

       并从列表中选择（或在聊天中使用 `/model list`）。

    参见 [MiniMax](/zh-CN/providers/minimax) 和 [模型](/zh-CN/concepts/models)。

  </Accordion>

  <Accordion title="我可以把 MiniMax 设为默认模型，把 OpenAI 用于复杂任务吗？">
    可以。将 **MiniMax 作为默认值**，并在需要时**按会话**
    切换模型。回退是为**错误**准备的，不是为“困难任务”准备的，因此请使用 `/model` 或单独的智能体。

    **方案 A：按会话切换**

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

    **方案 B：分离智能体**

    - 智能体 A 默认：MiniMax
    - 智能体 B 默认：OpenAI
    - 按智能体路由，或使用 `/agent` 切换

    文档：[模型](/zh-CN/concepts/models)、[多智能体路由](/zh-CN/concepts/multi-agent)、[MiniMax](/zh-CN/providers/minimax)、[OpenAI](/zh-CN/providers/openai)。

  </Accordion>

  <Accordion title="opus / sonnet / gpt 是内置快捷方式吗？">
    是的。OpenClaw 附带一些默认简写（仅当模型存在于 `agents.defaults.models` 中时适用）：

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

  <Accordion title="如何定义 / 覆盖模型快捷方式（别名）？">
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

  <Accordion title="如何添加 OpenRouter 或 Z.AI 等其他提供商的模型？">
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

    如果你引用了某个 provider / model，但缺少所需的 provider 密钥，你会得到运行时凭证错误（例如 `No API key found for provider "zai"`）。

    **添加新智能体后出现 No API key found for provider**

    这通常意味着**新智能体**的凭证存储为空。凭证是按智能体存储的，
    路径为：

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    修复选项：

    - 运行 `openclaw agents add <id>` 并在向导中配置凭证。
    - 或者将主智能体 `agentDir` 中的 `auth-profiles.json` 复制到新智能体的 `agentDir`。

    **不要**在多个智能体之间复用 `agentDir`；这会导致凭证 / 会话冲突。

  </Accordion>
</AccordionGroup>

## 模型故障切换与 “All models failed”

<AccordionGroup>
  <Accordion title="故障切换是如何工作的？">
    故障切换分两个阶段发生：

    1. 同一提供商内的**凭证配置文件轮换**。
    2. 回退到 `agents.defaults.model.fallbacks` 中的下一个模型，即**模型回退**。

    冷却时间会应用到失败的配置文件上（指数退避），因此即使某个提供商受到速率限制或暂时故障，OpenClaw 仍可继续响应。

    速率限制分类不仅包含普通 `429` 响应。OpenClaw
    还会将 `Too many concurrent requests`、
    `ThrottlingException`、`concurrency limit reached`、
    `workers_ai ... quota limit exceeded`、`resource exhausted` 以及周期性
    使用窗口限制（`weekly/monthly limit reached`）视为值得故障切换的
    速率限制。

    某些看起来像计费问题的响应并不是 `402`，而某些 HTTP `402`
    响应也仍然属于瞬态分类。如果某个提供商在 `401` 或 `403` 上返回了
    明确的计费文本，OpenClaw 仍可将其保留在
    计费分类中，但提供商特定的文本匹配器仍仅限于对应提供商
    （例如 OpenRouter 的 `Key limit exceeded`）。如果某条 `402`
    消息看起来像是可重试的使用窗口或
    组织 / 工作区支出限制（`daily limit reached, resets tomorrow`、
    `organization spending limit exceeded`），OpenClaw 会将其视为
    `rate_limit`，而不是长期计费禁用。

    上下文溢出错误则不同：像
    `request_too_large`、`input exceeds the maximum number of tokens`、
    `input token count exceeds the maximum number of input tokens`、
    `input is too long for the model` 或 `ollama error: context length
    exceeded` 这样的特征会停留在压缩 / 重试路径中，而不会推进模型
    回退。

    通用服务器错误文本的处理故意比“任何包含
    unknown / error 的内容”更窄。OpenClaw 确实会将提供商范围的瞬态形式
    视为值得故障切换的超时 / 过载信号，例如 Anthropic 裸文本 `An unknown error occurred`、OpenRouter 裸文本
    `Provider returned error`、停止原因错误如 `Unhandled stop reason:
    error`、带有瞬态服务器文本的 JSON `api_error` 载荷
    （`internal server error`、`unknown error, 520`、`upstream error`、`backend
    error`），以及 `ModelNotReadyException` 之类的提供商繁忙错误，
    但前提是提供商上下文
    确实匹配。
    像 `LLM request failed with an unknown
    error.` 这样的通用内部回退文本则保持保守，不会单独触发模型回退。

  </Accordion>

  <Accordion title='“No credentials found for profile anthropic:default” 是什么意思？'>
    这表示系统尝试使用凭证配置文件 ID `anthropic:default`，但在预期的凭证存储中找不到与之对应的凭证。

    **修复检查清单：**

    - **确认凭证配置文件所在位置**（新路径与旧路径）
      - 当前：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
      - 旧版：`~/.openclaw/agent/*`（由 `openclaw doctor` 迁移）
    - **确认 Gateway 网关已加载你的环境变量**
      - 如果你在 shell 中设置了 `ANTHROPIC_API_KEY`，但通过 systemd / launchd 运行 Gateway 网关，它可能不会继承该变量。请将其放入 `~/.openclaw/.env`，或