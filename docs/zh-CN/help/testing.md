---
read_when:
    - 在本地或 CI 中运行测试时
    - 为模型 / 提供商缺陷添加回归测试时
    - 调试 Gateway 网关 + 智能体行为时
summary: 测试工具包：单元 / e2e / 实时测试套件、Docker 运行器，以及各类测试覆盖的内容
title: 测试
x-i18n:
    generated_at: "2026-04-06T01:02:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfa174e565df5fdf957234b7909beaf1304aa026e731cc2c433ca7d931681b56
    source_path: help/testing.md
    workflow: 15
---

# 测试

OpenClaw 有三个 Vitest 测试套件（单元 / 集成、e2e、实时）以及一小组 Docker 运行器。

本文档是一份“我们如何测试”的指南：

- 每个测试套件覆盖什么内容（以及它刻意 _不_ 覆盖什么）
- 常见工作流应运行哪些命令（本地、推送前、调试）
- 实时测试如何发现凭证并选择模型 / 提供商
- 如何为真实世界中的模型 / 提供商问题添加回归测试

## 快速开始

大多数时候：

- 完整 gate（推送前预期应运行）：`pnpm build && pnpm check && pnpm test`
- 在资源充足的机器上更快地运行本地完整测试套件：`pnpm test:max`
- 直接使用 Vitest 观察模式循环（现代 projects 配置）：`pnpm test:watch`
- 现在也支持直接按文件路径定位扩展 / 渠道测试：`pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`

当你修改了测试，或希望获得更高把握时：

- 覆盖率 gate：`pnpm test:coverage`
- E2E 测试套件：`pnpm test:e2e`

调试真实提供商 / 模型时（需要真实凭证）：

- 实时测试套件（模型 + Gateway 网关工具 / 图像探测）：`pnpm test:live`
- 安静地只运行一个实时测试文件：`pnpm test:live -- src/agents/models.profiles.live.test.ts`

提示：如果你只需要定位一个失败用例，优先使用下文介绍的 allowlist 环境变量来缩小实时测试范围。

## 测试套件（各自运行在哪里）

可以把这些测试套件理解为“真实程度逐步增加”（同时不稳定性 / 成本也逐步增加）：

### 单元 / 集成（默认）

- 命令：`pnpm test`
- 配置：通过 `vitest.config.ts` 使用原生 Vitest `projects`
- 文件：位于 `src/**/*.test.ts`、`packages/**/*.test.ts`、`test/**/*.test.ts` 的核心 / 单元测试清单，以及 `vitest.unit.config.ts` 覆盖的白名单 `ui` Node 测试
- 范围：
  - 纯单元测试
  - 进程内集成测试（Gateway 网关认证、路由、工具、解析、配置）
  - 针对已知缺陷的确定性回归测试
- 预期：
  - 在 CI 中运行
  - 不需要真实密钥
  - 应该快速且稳定
- Projects 说明：
  - `pnpm test`、`pnpm test:watch` 和 `pnpm test:changed` 现在都使用同一个原生 Vitest 根级 `projects` 配置。
  - 直接文件过滤现在会通过根项目图原生路由，因此 `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` 无需自定义包装器即可工作。
- 嵌入式运行器说明：
  - 当你修改消息工具发现输入或压缩运行时上下文时，
    要同时保持两个层级的覆盖。
  - 为纯路由 / 归一化边界添加聚焦的辅助函数回归测试。
  - 同时也要保持嵌入式运行器集成测试套件健康：
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`、
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts` 和
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`。
  - 这些套件会验证作用域 id 和压缩行为是否仍然通过真实的
    `run.ts` / `compact.ts` 路径流转；仅有辅助函数级测试
    不能充分替代这些集成路径。
- Pool 说明：
  - 基础 Vitest 配置现在默认使用 `threads`。
  - 共享 Vitest 配置还固定了 `isolate: false`，并在根 projects、e2e 和实时配置中使用非隔离运行器。
  - 根 UI 通道仍保留其 `jsdom` 设置和优化器，但现在也运行在共享的非隔离运行器上。
  - `pnpm test` 现在从根 `vitest.config.ts` 的 projects 配置继承相同的 `threads` + `isolate: false` 默认值。
  - 共享的 `scripts/run-vitest.mjs` 启动器现在默认还会为 Vitest 子 Node 进程添加 `--no-maglev`，以减少大型本地运行期间的 V8 编译抖动。如果你需要与原生 V8 行为进行对比，设置 `OPENCLAW_VITEST_ENABLE_MAGLEV=1`。
- 本地快速迭代说明：
  - `pnpm test:changed` 现在使用原生 projects 配置并带上 `--changed origin/main`。
  - `pnpm test:max` 和 `pnpm test:changed:max` 保持相同的原生 projects 配置，只是提高了 worker 上限。
  - 本地 worker 自动缩放现在有意更保守，并且在主机负载平均值已经较高时也会回退，因此多个并发 Vitest 运行默认造成的影响更小。
  - 基础 Vitest 配置将 projects / config 文件标记为 `forceRerunTriggers`，因此 changed 模式在测试接线发生变化时仍能正确重跑。
  - 配置在支持的主机上保持启用 `OPENCLAW_VITEST_FS_MODULE_CACHE`；如果你希望为直接性能分析指定一个显式缓存位置，可设置 `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path`。
- 性能调试说明：
  - `pnpm test:perf:imports` 会启用 Vitest 导入耗时报告以及导入明细输出。
  - `pnpm test:perf:imports:changed` 会将相同的性能分析视图限定到自 `origin/main` 以来发生变化的文件。
  - `pnpm test:perf:profile:main` 会为 Vitest / Vite 启动和转换开销写出主线程 CPU profile。
  - `pnpm test:perf:profile:runner` 会在禁用文件并行的情况下，为单元测试套件写出运行器 CPU + heap profile。

### E2E（Gateway 网关烟雾测试）

- 命令：`pnpm test:e2e`
- 配置：`vitest.e2e.config.ts`
- 文件：`src/**/*.e2e.test.ts`、`test/**/*.e2e.test.ts`
- 运行时默认值：
  - 使用 Vitest `threads` 与 `isolate: false`，与仓库其余部分保持一致。
  - 使用自适应 workers（CI：最多 2 个，本地：默认 1 个）。
  - 默认以静默模式运行，以减少控制台 I/O 开销。
- 常用覆盖项：
  - `OPENCLAW_E2E_WORKERS=<n>`：强制指定 worker 数量（上限为 16）。
  - `OPENCLAW_E2E_VERBOSE=1`：重新启用详细控制台输出。
- 范围：
  - 多实例 Gateway 网关端到端行为
  - WebSocket / HTTP 接口、节点配对以及更重的网络交互
- 预期：
  - 在 CI 中运行（当流水线中启用时）
  - 不需要真实密钥
  - 比单元测试涉及更多活动部件（可能更慢）

### E2E：OpenShell 后端烟雾测试

- 命令：`pnpm test:e2e:openshell`
- 文件：`test/openshell-sandbox.e2e.test.ts`
- 范围：
  - 通过 Docker 在主机上启动一个隔离的 OpenShell Gateway 网关
  - 基于临时本地 Dockerfile 创建一个沙箱
  - 通过真实的 `sandbox ssh-config` + SSH exec 运行 OpenClaw 的 OpenShell 后端
  - 通过沙箱 fs bridge 验证远端规范化文件系统行为
- 预期：
  - 仅在选择加入时运行；不属于默认 `pnpm test:e2e` 运行的一部分
  - 需要本地 `openshell` CLI 和一个可用的 Docker daemon
  - 使用隔离的 `HOME` / `XDG_CONFIG_HOME`，然后销毁测试 Gateway 网关和沙箱
- 常用覆盖项：
  - `OPENCLAW_E2E_OPENSHELL=1`：在手动运行更广泛的 e2e 套件时启用此测试
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`：指向非默认 CLI 二进制文件或包装脚本

### 实时（真实提供商 + 真实模型）

- 命令：`pnpm test:live`
- 配置：`vitest.live.config.ts`
- 文件：`src/**/*.live.test.ts`
- 默认：由 `pnpm test:live` **启用**（会设置 `OPENCLAW_LIVE_TEST=1`）
- 范围：
  - “这个提供商 / 模型今天在真实凭证下是否真的可用？”
  - 捕获提供商格式变更、工具调用怪癖、认证问题以及限流行为
- 预期：
  - 按设计不追求 CI 稳定性（真实网络、真实提供商策略、配额、故障）
  - 会花钱 / 消耗限流额度
  - 优先运行缩小范围的子集，而不是“全部”
- 实时运行会 source `~/.profile` 以补齐缺失的 API 密钥。
- 默认情况下，实时运行仍会隔离 `HOME`，并将配置 / 认证材料复制到临时测试 home 中，这样单元测试夹具就不会修改你真实的 `~/.openclaw`。
- 只有当你明确需要实时测试使用真实 home 目录时，才设置 `OPENCLAW_LIVE_USE_REAL_HOME=1`。
- `pnpm test:live` 现在默认使用更安静的模式：会保留 `[live] ...` 进度输出，但会抑制额外的 `~/.profile` 提示，并静默 Gateway 网关引导日志 / Bonjour 噪音。如果你希望恢复完整启动日志，可设置 `OPENCLAW_LIVE_TEST_QUIET=0`。
- API 密钥轮换（提供商特定）：设置 `*_API_KEYS`，使用逗号 / 分号格式，或设置 `*_API_KEY_1`、`*_API_KEY_2`（例如 `OPENAI_API_KEYS`、`ANTHROPIC_API_KEYS`、`GEMINI_API_KEYS`），也可通过 `OPENCLAW_LIVE_*_KEY` 为单次实时运行覆盖；测试会在遇到限流响应时重试。
- 进度 / 心跳输出：
  - 实时测试套件现在会将进度行输出到 stderr，因此即使 Vitest 控制台捕获较安静，长时间的提供商调用也能显示其仍在活动。
  - `vitest.live.config.ts` 会禁用 Vitest 控制台拦截，因此提供商 / Gateway 网关进度行会在实时运行期间立即流式输出。
  - 使用 `OPENCLAW_LIVE_HEARTBEAT_MS` 调整 direct-model 心跳。
  - 使用 `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS` 调整 Gateway 网关 / 探测心跳。

## 我应该运行哪个测试套件？

使用下面这个决策表：

- 编辑逻辑 / 测试：运行 `pnpm test`（如果改动较多，再加上 `pnpm test:coverage`）
- 触及 Gateway 网关网络 / WS 协议 / 配对：再加跑 `pnpm test:e2e`
- 调试“我的 bot 挂了” / 提供商特定故障 / 工具调用：运行一个缩小范围的 `pnpm test:live`

## 实时：Android 节点能力扫描

- 测试：`src/gateway/android-node.capabilities.live.test.ts`
- 脚本：`pnpm android:test:integration`
- 目标：调用已连接 Android 节点当前**声明的每一个命令**，并断言命令契约行为。
- 范围：
  - 需要预设 / 手动设置（该套件不会安装 / 运行 / 配对应用）。
  - 针对所选 Android 节点逐命令验证 Gateway 网关 `node.invoke`。
- 必需的预设步骤：
  - Android 应用已连接并与 Gateway 网关配对。
  - 应用保持前台运行。
  - 已为你期望通过的能力授予权限 / 捕获同意。
- 可选目标覆盖项：
  - `OPENCLAW_ANDROID_NODE_ID` 或 `OPENCLAW_ANDROID_NODE_NAME`。
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`。
- 完整 Android 设置详情：[Android App](/zh-CN/platforms/android)

## 实时：模型烟雾测试（profile keys）

实时测试拆分为两层，以便隔离故障：

- “Direct model” 用于告诉我们：给定的 key 下，该提供商 / 模型是否至少能响应。
- “Gateway smoke” 用于告诉我们：该模型的完整 Gateway 网关 + 智能体管线是否工作正常（会话、历史、工具、沙箱策略等）。

### 第 1 层：Direct model completion（无 Gateway 网关）

- 测试：`src/agents/models.profiles.live.test.ts`
- 目标：
  - 枚举发现到的模型
  - 使用 `getApiKeyForModel` 选择你有凭证的模型
  - 为每个模型运行一次小型 completion（并在需要时运行定向回归）
- 启用方式：
  - `pnpm test:live`（或直接调用 Vitest 时设置 `OPENCLAW_LIVE_TEST=1`）
- 设置 `OPENCLAW_LIVE_MODELS=modern`（或 `all`，即 modern 的别名）后才会实际运行此套件；否则它会跳过，以便让 `pnpm test:live` 聚焦于 Gateway 网关烟雾测试
- 如何选择模型：
  - `OPENCLAW_LIVE_MODELS=modern`：运行 modern allowlist（Opus / Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_MODELS=all` 是 modern allowlist 的别名
  - 或 `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."`（逗号分隔的 allowlist）
- 如何选择提供商：
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity"`（逗号分隔的 allowlist）
- 密钥来源：
  - 默认：profile 存储和环境变量回退
  - 设置 `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 可强制**仅使用 profile 存储**
- 存在原因：
  - 将“提供商 API 坏了 / key 无效”和“Gateway 网关智能体管线坏了”分离开来
  - 容纳小而隔离的回归场景（例如：OpenAI Responses / Codex Responses 的 reasoning replay + tool-call 流程）

### 第 2 层：Gateway 网关 + dev 智能体烟雾测试（也就是 “@openclaw” 实际做的事）

- 测试：`src/gateway/gateway-models.profiles.live.test.ts`
- 目标：
  - 启动一个进程内 Gateway 网关
  - 创建 / 修补一个 `agent:dev:*` 会话（每次运行按模型覆盖）
  - 遍历有密钥的模型并断言：
    - “有意义的”响应（无工具）
    - 一次真实工具调用可正常工作（read probe）
    - 可选的额外工具探测可正常工作（exec+read probe）
    - OpenAI 回归路径（仅 tool-call → 后续跟进）持续可用
- 探测细节（这样你就能快速解释故障）：
  - `read` probe：测试会在工作区写入一个 nonce 文件，并要求智能体 `read` 它并把 nonce 回显回来。
  - `exec+read` probe：测试会要求智能体通过 `exec` 将一个 nonce 写入临时文件，然后再 `read` 回来。
  - image probe：测试会附加一个生成的 PNG（猫 + 随机代码），并期望模型返回 `cat <CODE>`。
  - 实现参考：`src/gateway/gateway-models.profiles.live.test.ts` 和 `src/gateway/live-image-probe.ts`。
- 启用方式：
  - `pnpm test:live`（或直接调用 Vitest 时设置 `OPENCLAW_LIVE_TEST=1`）
- 如何选择模型：
  - 默认：modern allowlist（Opus / Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` 是 modern allowlist 的别名
  - 或设置 `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`（或逗号列表）来缩小范围
- 如何选择提供商（避免“OpenRouter 全家桶”）：
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,openai,anthropic,zai,minimax"`（逗号分隔的 allowlist）
- 工具 + 图像探测在此实时测试中始终开启：
  - `read` probe + `exec+read` probe（工具压力测试）
  - 当模型声明支持图像输入时，会运行 image probe
  - 流程（高层说明）：
    - 测试生成一个包含 “CAT” + 随机代码的小型 PNG（`src/gateway/live-image-probe.ts`）
    - 通过 `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]` 发送
    - Gateway 网关会将附件解析到 `images[]` 中（`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`）
    - 嵌入式智能体将多模态用户消息转发给模型
    - 断言：回复包含 `cat` + 该代码（OCR 允许轻微误差）

提示：如果你想查看自己的机器上能测试哪些内容（以及准确的 `provider/model` id），请运行：

```bash
openclaw models list
openclaw models list --json
```

## 实时：ACP bind 烟雾测试（`/acp spawn ... --bind here`）

- 测试：`src/gateway/gateway-acp-bind.live.test.ts`
- 目标：使用实时 ACP 智能体验证真实 ACP conversation-bind 流程：
  - 发送 `/acp spawn <agent> --bind here`
  - 原地绑定一个合成的消息渠道会话
  - 在同一个会话上发送一个普通跟进消息
  - 验证该跟进消息确实落入已绑定的 ACP 会话转录中
- 启用：
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- 默认值：
  - ACP 智能体：`claude`
  - 合成渠道：Slack 私信风格的会话上下文
  - ACP 后端：`acpx`
- 覆盖项：
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- 说明：
  - 该测试通道使用 Gateway 网关 `chat.send` 接口，并带有仅管理员可用的合成 originating-route 字段，因此测试可以附加消息渠道上下文，而不必假装对外投递。
  - 当 `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` 未设置时，测试会使用内置 `acpx` 插件中的智能体注册表来选择 ACP harness 智能体。

示例：

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

Docker 配方：

```bash
pnpm test:docker:live-acp-bind
```

Docker 说明：

- Docker 运行器位于 `scripts/test-live-acp-bind-docker.sh`。
- 它会 source `~/.profile`，将匹配的 CLI 认证材料暂存到容器中，把 `acpx` 安装到可写 npm prefix，然后在缺失时安装所请求的实时 CLI（`@anthropic-ai/claude-code` 或 `@openai/codex`）。
- 在 Docker 内，运行器会设置 `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx`，这样 acpx 就能让来自已 source profile 的提供商环境变量继续对其子 harness CLI 可用。

### 推荐的实时测试配方

范围窄、显式的 allowlist 最快，也最不容易出问题：

- 单模型，direct（无 Gateway 网关）：
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- 单模型，Gateway 网关烟雾测试：
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 跨多个提供商测试工具调用：
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Google 聚焦（Gemini API key + Antigravity）：
  - Gemini（API key）：`OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity（OAuth）：`OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

说明：

- `google/...` 使用 Gemini API（API key）。
- `google-antigravity/...` 使用 Antigravity OAuth bridge（Cloud Code Assist 风格的智能体端点）。

## 实时：模型矩阵（我们覆盖什么）

没有固定的“CI 模型列表”（实时测试是可选启用的），但下面这些是在拥有密钥的开发机上建议定期覆盖的**推荐**模型。

### 现代烟雾测试集合（工具调用 + 图像）

这是我们期望持续可用的“常见模型”运行集：

- OpenAI（非 Codex）：`openai/gpt-5.4`（可选：`openai/gpt-5.4-mini`）
- OpenAI Codex：`openai-codex/gpt-5.4`
- Anthropic：`anthropic/claude-opus-4-6`（或 `anthropic/claude-sonnet-4-6`）
- Google（Gemini API）：`google/gemini-3.1-pro-preview` 和 `google/gemini-3-flash-preview`（避免较旧的 Gemini 2.x 模型）
- Google（Antigravity）：`google-antigravity/claude-opus-4-6-thinking` 和 `google-antigravity/gemini-3-flash`
- Z.AI（GLM）：`zai/glm-4.7`
- MiniMax：`minimax/MiniMax-M2.7`

运行带工具 + 图像的 Gateway 网关烟雾测试：
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### 基线：工具调用（Read + 可选 Exec）

每个提供商家族至少选一个：

- OpenAI：`openai/gpt-5.4`（或 `openai/gpt-5.4-mini`）
- Anthropic：`anthropic/claude-opus-4-6`（或 `anthropic/claude-sonnet-4-6`）
- Google：`google/gemini-3-flash-preview`（或 `google/gemini-3.1-pro-preview`）
- Z.AI（GLM）：`zai/glm-4.7`
- MiniMax：`minimax/MiniMax-M2.7`

可选附加覆盖（锦上添花）：

- xAI：`xai/grok-4`（或当前可用的最新版本）
- Mistral：`mistral/`…（选一个你已启用、支持工具的模型）
- Cerebras：`cerebras/`…（如果你有访问权限）
- LM Studio：`lmstudio/`…（本地；工具调用取决于 API 模式）

### Vision：图像发送（附件 → 多模态消息）

在 `OPENCLAW_LIVE_GATEWAY_MODELS` 中至少包含一个支持图像的模型（Claude / Gemini / OpenAI 的支持视觉变体等），以触发 image probe。

### 聚合器 / 替代 Gateway 网关

如果你启用了相应密钥，也支持通过以下方式测试：

- OpenRouter：`openrouter/...`（数百个模型；使用 `openclaw models scan` 查找支持工具 + 图像的候选模型）
- OpenCode：`opencode/...` 用于 Zen，`opencode-go/...` 用于 Go（通过 `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY` 认证）

你还可以将更多提供商纳入实时矩阵（如果你有凭证 / 配置）：

- 内置：`openai`、`openai-codex`、`anthropic`、`google`、`google-vertex`、`google-antigravity`、`zai`、`openrouter`、`opencode`、`opencode-go`、`xai`、`groq`、`cerebras`、`mistral`、`github-copilot`
- 通过 `models.providers`（自定义端点）：`minimax`（云端 / API），以及任何兼容 OpenAI / Anthropic 的代理（LM Studio、vLLM、LiteLLM 等）

提示：不要试图在文档中硬编码“所有模型”。权威列表应以你机器上的 `discoverModels(...)` 返回结果以及可用密钥为准。

## 凭证（绝不要提交）

实时测试发现凭证的方式与 CLI 完全相同。实际含义如下：

- 如果 CLI 可用，实时测试也应能找到相同的密钥。
- 如果实时测试提示“无凭证”，请像调试 `openclaw models list` / 模型选择那样进行调试。

- 每个智能体的认证 profile：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（这就是实时测试里 “profile keys” 的含义）
- 配置：`~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）
- 旧版状态目录：`~/.openclaw/credentials/`（存在时会复制进暂存的实时 home，但它不是主 profile-key 存储）
- 本地实时运行默认会将当前配置、每个智能体的 `auth-profiles.json` 文件、旧版 `credentials/` 以及受支持的外部 CLI 认证目录复制到临时测试 home 中；在该暂存配置中会去掉 `agents.*.workspace` / `agentDir` 路径覆盖，这样探测就不会落到你真实主机的工作区。

如果你想依赖环境变量密钥（例如导出在你的 `~/.profile` 中），请在 `source ~/.profile` 后运行本地测试，或使用下方的 Docker 运行器（它们可以将 `~/.profile` 挂载到容器中）。

## Deepgram 实时测试（音频转录）

- 测试：`src/media-understanding/providers/deepgram/audio.live.test.ts`
- 启用：`DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus（国际版） 编码计划实时测试

- 测试：`src/agents/byteplus.live.test.ts`
- 启用：`BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- 可选模型覆盖：`BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow 媒体实时测试

- 测试：`extensions/comfy/comfy.live.test.ts`
- 启用：`OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- 范围：
  - 运行内置 comfy 图像、视频和 `music_generate` 路径
  - 除非已配置 `models.providers.comfy.<capability>`，否则会跳过各项能力
  - 在修改 comfy workflow 提交、轮询、下载或插件注册后很有用

## 图像生成实时测试

- 测试：`src/image-generation/runtime.live.test.ts`
- 命令：`pnpm test:live src/image-generation/runtime.live.test.ts`
- 范围：
  - 枚举每一个已注册的图像生成提供商插件
  - 在探测前从你的登录 shell（`~/.profile`）加载缺失的提供商环境变量
  - 默认优先使用实时 / 环境变量 API 密钥，而不是已存储的认证 profile，这样 `auth-profiles.json` 中过期的测试密钥不会掩盖真实的 shell 凭证
  - 跳过没有可用认证 / profile / 模型的提供商
  - 通过共享运行时能力运行标准图像生成变体：
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- 当前覆盖的内置提供商：
  - `openai`
  - `google`
- 可选缩小范围方式：
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- 可选认证行为：
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`：强制使用 profile 存储认证并忽略仅来自环境变量的覆盖

## 音乐生成实时测试

- 测试：`extensions/music-generation-providers.live.test.ts`
- 启用：`OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- 范围：
  - 运行共享的内置音乐生成提供商路径
  - 当前覆盖 Google 和 MiniMax
  - 在探测前从你的登录 shell（`~/.profile`）加载提供商环境变量
  - 跳过没有可用认证 / profile / 模型的提供商
- 可选缩小范围方式：
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`

## Docker 运行器（可选的“在 Linux 中可运行”检查）

这些 Docker 运行器分为两类：

- 实时模型运行器：`test:docker:live-models` 和 `test:docker:live-gateway` 只会在仓库 Docker 镜像中运行与各自匹配的 profile-key 实时测试文件（`src/agents/models.profiles.live.test.ts` 和 `src/gateway/gateway-models.profiles.live.test.ts`），并挂载你的本地配置目录与工作区（若已挂载，还会 source `~/.profile`）。对应的本地入口点是 `test:live:models-profiles` 和 `test:live:gateway-profiles`。
- Docker 实时运行器默认使用更小的 smoke 上限，以便完整 Docker 扫描仍然切实可行：
  `test:docker:live-models` 默认设置 `OPENCLAW_LIVE_MAX_MODELS=12`，而
  `test:docker:live-gateway` 默认设置 `OPENCLAW_LIVE_GATEWAY_SMOKE=1`、
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`、
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000` 和
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`。当你
  明确想要更大的穷举扫描时，再覆盖这些环境变量。
- `test:docker:all` 会先通过 `test:docker:live-build` 构建一次实时 Docker 镜像，然后在两个实时 Docker 通道中复用它。
- 容器烟雾测试运行器：`test:docker:openwebui`、`test:docker:onboard`、`test:docker:gateway-network`、`test:docker:mcp-channels` 和 `test:docker:plugins` 会启动一个或多个真实容器，并验证更高层级的集成路径。

实时模型 Docker 运行器还会仅绑定挂载所需的 CLI 认证 home（若运行未缩小范围，则挂载所有受支持项），然后在运行前将它们复制到容器 home 中，这样外部 CLI OAuth 就可以刷新令牌，而不会修改主机认证存储：

- Direct models：`pnpm test:docker:live-models`（脚本：`scripts/test-live-models-docker.sh`）
- ACP bind 烟雾测试：`pnpm test:docker:live-acp-bind`（脚本：`scripts/test-live-acp-bind-docker.sh`）
- Gateway 网关 + dev 智能体：`pnpm test:docker:live-gateway`（脚本：`scripts/test-live-gateway-models-docker.sh`）
- Open WebUI 实时烟雾测试：`pnpm test:docker:openwebui`（脚本：`scripts/e2e/openwebui-docker.sh`）
- 新手引导向导（TTY，完整脚手架）：`pnpm test:docker:onboard`（脚本：`scripts/e2e/onboard-docker.sh`）
- Gateway 网关网络（两个容器，WS 认证 + 健康检查）：`pnpm test:docker:gateway-network`（脚本：`scripts/e2e/gateway-network-docker.sh`）
- MCP 渠道 bridge（带种子数据的 Gateway 网关 + stdio bridge + 原始 Claude notification-frame 烟雾测试）：`pnpm test:docker:mcp-channels`（脚本：`scripts/e2e/mcp-channels-docker.sh`）
- 插件（安装烟雾测试 + `/plugin` 别名 + Claude bundle 重启语义）：`pnpm test:docker:plugins`（脚本：`scripts/e2e/plugins-docker.sh`）

实时模型 Docker 运行器还会将当前 checkout 以只读方式绑定挂载，
并将其暂存到容器内的临时工作目录中。这样可以在保持运行时镜像
精简的同时，依然针对你当前本地源码 / 配置准确运行 Vitest。
暂存步骤会跳过大型本地专用缓存和应用构建输出，例如
`.pnpm-store`、`.worktrees`、`__openclaw_vitest__`，以及应用本地 `.build` 或
Gradle 输出目录，因此 Docker 实时运行不会花几分钟去复制
与机器相关的产物。
它们还会设置 `OPENCLAW_SKIP_CHANNELS=1`，因此 Gateway 网关实时探测不会在容器中启动
真实 Telegram / Discord / 等渠道 worker。
`test:docker:live-models` 仍然运行 `pnpm test:live`，因此在你需要缩小范围
或从该 Docker 通道中排除 Gateway 网关实时覆盖时，也请一并传入
`OPENCLAW_LIVE_GATEWAY_*`。
`test:docker:openwebui` 是一个更高层级的兼容性烟雾测试：它会启动一个
启用了 OpenAI 兼容 HTTP 端点的 OpenClaw Gateway 网关容器，
再针对该 Gateway 网关启动一个固定版本的 Open WebUI 容器，通过
Open WebUI 完成登录，验证 `/api/models` 暴露 `openclaw/default`，然后通过
Open WebUI 的 `/api/chat/completions` 代理发送一次真实聊天请求。
第一次运行可能会明显更慢，因为 Docker 可能需要拉取
Open WebUI 镜像，而 Open WebUI 也可能需要完成自身冷启动设置。
该通道需要一个可用的实时模型密钥，而 `OPENCLAW_PROFILE_FILE`
（默认 `~/.profile`）是在 Docker 化运行中提供该密钥的主要方式。
成功运行会打印一个小型 JSON 载荷，例如 `{ "ok": true, "model":
"openclaw/default", ... }`。
`test:docker:mcp-channels` 刻意保持确定性，不需要
真实的 Telegram、Discord 或 iMessage 账号。它会启动一个带种子数据的 Gateway 网关
容器，再启动第二个容器来运行 `openclaw mcp serve`，然后
验证路由后的会话发现、转录读取、附件元数据、
实时事件队列行为、出站发送路由，以及 Claude 风格的渠道 +
权限通知是否通过真实 stdio MCP bridge 正常工作。通知检查
会直接检查原始 stdio MCP 帧，因此这个烟雾测试验证的是
bridge 实际发出了什么，而不只是某个特定客户端 SDK 恰好暴露了什么。

手动 ACP 自然语言线程烟雾测试（非 CI）：

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- 保留此脚本用于回归 / 调试工作流。后续可能仍会需要它来验证 ACP 线程路由，因此不要删除它。

常用环境变量：

- `OPENCLAW_CONFIG_DIR=...`（默认：`~/.openclaw`）挂载到 `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...`（默认：`~/.openclaw/workspace`）挂载到 `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...`（默认：`~/.profile`）挂载到 `/home/node/.profile` 并在运行测试前 source
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...`（默认：`~/.cache/openclaw/docker-cli-tools`）挂载到 `/home/node/.npm-global`，用于 Docker 内缓存 CLI 安装
- `$HOME` 下的外部 CLI 认证目录 / 文件会以只读方式挂载到 `/host-auth...` 下，然后在测试开始前复制到 `/home/node/...`
  - 默认目录：`.minimax`
  - 默认文件：`~/.codex/auth.json`、`~/.codex/config.toml`、`.claude.json`、`~/.claude/.credentials.json`、`~/.claude/settings.json`、`~/.claude/settings.local.json`
  - 缩小提供商范围的运行仅会挂载由 `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS` 推断出的必要目录 / 文件
  - 可手动覆盖为 `OPENCLAW_DOCKER_AUTH_DIRS=all`、`OPENCLAW_DOCKER_AUTH_DIRS=none`，或逗号列表，例如 `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`：缩小运行范围
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`：在容器内过滤提供商
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`：确保凭证来自 profile 存储（而非环境变量）
- `OPENCLAW_OPENWEBUI_MODEL=...`：选择由 Gateway 网关暴露给 Open WebUI 烟雾测试的模型
- `OPENCLAW_OPENWEBUI_PROMPT=...`：覆盖 Open WebUI 烟雾测试使用的 nonce 检查提示词
- `OPENWEBUI_IMAGE=...`：覆盖固定的 Open WebUI 镜像标签

## 文档完整性检查

文档编辑后运行文档检查：`pnpm check:docs`。
当你还需要完整的 Mintlify anchor 校验（包括页内标题检查）时，运行：`pnpm docs:check-links:anchors`。

## 离线回归（CI 安全）

这些是在不依赖真实提供商的情况下，针对“真实管线”的回归测试：

- Gateway 网关工具调用（mock OpenAI，真实 Gateway 网关 + 智能体循环）：`src/gateway/gateway.test.ts`（用例：“runs a mock OpenAI tool call end-to-end via gateway agent loop”）
- Gateway 网关向导（WS `wizard.start` / `wizard.next`，强制写入 config + auth）：`src/gateway/gateway.test.ts`（用例：“runs wizard over ws and writes auth token config”）

## 智能体可靠性评估（Skills）

我们已经有一些 CI 安全的测试，其行为类似“智能体可靠性评估”：

- 通过真实 Gateway 网关 + 智能体循环进行 mock 工具调用（`src/gateway/gateway.test.ts`）。
- 端到端向导流程，用于验证会话接线和配置效果（`src/gateway/gateway.test.ts`）。

针对 Skills 目前仍缺少的内容（参见 [Skills](/zh-CN/tools/skills)）：

- **决策能力：** 当 prompt 中列出了 skills 时，智能体是否会选择正确的 skill（或避开无关 skill）？
- **合规性：** 智能体是否会在使用前读取 `SKILL.md`，并遵循要求的步骤 / 参数？
- **工作流契约：** 断言工具顺序、会话历史延续和沙箱边界的多轮场景。

未来的评估应优先保持确定性：

- 一个使用 mock 提供商的场景运行器，用于断言工具调用 + 顺序、skill 文件读取以及会话接线。
- 一小组面向 skill 的场景（使用 vs 避免、gate、prompt 注入）。
- 只有在 CI 安全套件就位后，才添加可选实时评估（显式启用、受环境变量控制）。

## 契约测试（插件和渠道形状）

契约测试用于验证每个已注册的插件和渠道都符合其
接口契约。它们会遍历所有已发现的插件，并运行一组
针对形状与行为的断言。默认的 `pnpm test` 单元通道会有意
跳过这些共享接缝与烟雾测试文件；当你修改共享渠道或提供商表面时，
请显式运行契约测试命令。

### 命令

- 所有契约测试：`pnpm test:contracts`
- 仅渠道契约测试：`pnpm test:contracts:channels`
- 仅提供商契约测试：`pnpm test:contracts:plugins`

### 渠道契约测试

位于 `src/channels/plugins/contracts/*.contract.test.ts`：

- **plugin** - 基本插件形状（id、名称、能力）
- **setup** - 设置向导契约
- **session-binding** - 会话绑定行为
- **outbound-payload** - 消息载荷结构
- **inbound** - 入站消息处理
- **actions** - 渠道动作处理器
- **threading** - 线程 ID 处理
- **directory** - 目录 / roster API
- **group-policy** - 群组策略执行

### 提供商状态契约测试

位于 `src/plugins/contracts/*.contract.test.ts`。

- **status** - 渠道状态探测
- **registry** - 插件注册表形状

### 提供商契约测试

位于 `src/plugins/contracts/*.contract.test.ts`：

- **auth** - 认证流程契约
- **auth-choice** - 认证方式 / 选择
- **catalog** - 模型目录 API
- **discovery** - 插件发现
- **loader** - 插件加载
- **runtime** - 提供商运行时
- **shape** - 插件形状 / 接口
- **wizard** - 设置向导

### 何时运行

- 修改 plugin-sdk 导出或子路径之后
- 添加或修改某个渠道或提供商插件之后
- 重构插件注册或发现逻辑之后

契约测试会在 CI 中运行，不需要真实 API 密钥。

## 添加回归测试（指导）

当你修复了一个在实时测试中发现的提供商 / 模型问题时：

- 如果可能，添加一个 CI 安全的回归测试（mock / stub 提供商，或捕获精确的请求形状转换）
- 如果它天然只能通过实时测试捕获（限流、认证策略），就保持实时测试范围窄，并通过环境变量显式启用
- 优先定位到能捕获此缺陷的最小层级：
  - 提供商请求转换 / 回放缺陷 → direct models 测试
  - Gateway 网关会话 / 历史 / 工具管线缺陷 → Gateway 网关实时烟雾测试或 CI 安全的 Gateway 网关 mock 测试
- SecretRef 遍历护栏：
  - `src/secrets/exec-secret-ref-id-parity.test.ts` 会从注册表元数据（`listSecretTargetRegistryEntries()`）中为每个 SecretRef 类推导一个采样目标，然后断言遍历分段 exec id 会被拒绝。
  - 如果你在 `src/secrets/target-registry-data.ts` 中添加了新的 `includeInPlan` SecretRef 目标家族，请更新该测试中的 `classifyTargetClass`。该测试会故意在未分类目标 id 出现时失败，这样新类别就不会被悄悄跳过。
