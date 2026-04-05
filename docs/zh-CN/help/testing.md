---
read_when:
    - 在本地或 CI 中运行测试时
    - 为模型 / 提供商问题添加回归测试时
    - 调试 Gateway 网关 + 智能体行为时
summary: 测试套件：单元 / e2e / 实时测试套件、Docker 运行器，以及各项测试的覆盖范围
title: 测试
x-i18n:
    generated_at: "2026-04-05T12:35:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 854a39ae261d8749b8d8d82097b97a7c52cf2216d1fe622e302d830a888866ab
    source_path: help/testing.md
    workflow: 15
---

# 测试

OpenClaw 有三个 Vitest 测试套件（单元 / 集成、e2e、实时）以及一小组 Docker 运行器。

本文档是一份“我们如何测试”的指南：

- 每个测试套件覆盖什么（以及它刻意 _不_ 覆盖什么）
- 常见工作流（本地、推送前、调试）应运行哪些命令
- 实时测试如何发现凭证并选择模型 / 提供商
- 如何为真实世界中的模型 / 提供商问题添加回归测试

## 快速开始

大多数时候：

- 完整门禁（推送前的预期要求）：`pnpm build && pnpm check && pnpm test`
- 在资源充足的机器上更快地运行本地完整测试套件：`pnpm test:max`
- 直接进入 Vitest 监听循环（现代 projects 配置）：`pnpm test:watch`
- 直接按文件定位现在也会路由扩展 / 渠道路径：`pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`

当你修改了测试，或者想要更高信心时：

- 覆盖率门禁：`pnpm test:coverage`
- E2E 测试套件：`pnpm test:e2e`

当你在调试真实提供商 / 模型时（需要真实凭证）：

- 实时测试套件（模型 + Gateway 网关工具 / 图像探针）：`pnpm test:live`
- 安静地只运行一个实时测试文件：`pnpm test:live -- src/agents/models.profiles.live.test.ts`

提示：当你只需要一个失败用例时，优先使用下面介绍的 allowlist 环境变量来缩小实时测试范围。

## 测试套件（各自运行位置）

可以把这些测试套件理解为“真实性逐步增加”（同时不稳定性 / 成本也逐步增加）：

### 单元 / 集成（默认）

- 命令：`pnpm test`
- 配置：通过 `vitest.config.ts` 使用原生 Vitest `projects`
- 文件：`src/**/*.test.ts`、`packages/**/*.test.ts`、`test/**/*.test.ts` 下的核心 / 单元测试清单，以及由 `vitest.unit.config.ts` 覆盖的白名单 `ui` Node 测试
- 范围：
  - 纯单元测试
  - 进程内集成测试（Gateway 网关认证、路由、工具、解析、配置）
  - 已知问题的确定性回归测试
- 预期：
  - 在 CI 中运行
  - 不需要真实密钥
  - 应该快速且稳定
- Projects 说明：
  - `pnpm test`、`pnpm test:watch` 和 `pnpm test:changed` 现在都使用同一个原生 Vitest 根级 `projects` 配置。
  - 直接文件过滤会通过根项目图原生路由，因此 `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` 无需自定义包装器即可工作。
- 嵌入式运行器说明：
  - 当你修改消息工具发现输入或压缩运行时上下文时，
    要同时保持两个层级的覆盖。
  - 为纯路由 / 归一化边界添加聚焦的辅助回归测试。
  - 同时也要保持嵌入式运行器集成测试套件健康：
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`、
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`，以及
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`。
  - 这些测试套件会验证作用域 id 和压缩行为是否仍然通过真实的 `run.ts` / `compact.ts` 路径流动；仅有辅助函数测试
    不能充分替代这些集成路径。
- 线程池说明：
  - 基础 Vitest 配置现在默认使用 `threads`。
  - 共享 Vitest 配置还固定了 `isolate: false`，并在根项目、e2e 和实时配置中使用非隔离运行器。
  - 根级 UI 通道仍保留其 `jsdom` 设置和优化器，但现在也运行在共享的非隔离运行器上。
  - `pnpm test` 会从根级 `vitest.config.ts` projects 配置继承相同的 `threads` + `isolate: false` 默认值。
  - 共享的 `scripts/run-vitest.mjs` 启动器现在默认还会为 Vitest 子 Node 进程添加 `--no-maglev`，以减少大型本地运行期间的 V8 编译抖动。如果你需要与原始 V8 行为比较，可设置 `OPENCLAW_VITEST_ENABLE_MAGLEV=1`。
- 快速本地迭代说明：
  - `pnpm test:changed` 使用原生 projects 配置并带上 `--changed origin/main`。
  - `pnpm test:max` 和 `pnpm test:changed:max` 保持相同的原生 projects 配置，只是提高了 worker 上限。
  - 本地 worker 自动扩缩容现在有意更保守，并且当主机负载平均值已经较高时也会回退，因此默认情况下多个并发 Vitest 运行造成的影响会更小。
  - 基础 Vitest 配置将项目 / 配置文件标记为 `forceRerunTriggers`，从而在测试接线发生变化时，changed 模式的重跑仍然正确。
  - 配置会在受支持的主机上保持启用 `OPENCLAW_VITEST_FS_MODULE_CACHE`；如果你想为直接分析指定一个显式缓存位置，可设置 `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path`。
- 性能调试说明：
  - `pnpm test:perf:imports` 会启用 Vitest 导入耗时报告以及导入拆分输出。
  - `pnpm test:perf:imports:changed` 会将同样的分析视图限制为自 `origin/main` 以来变更的文件。
  - `pnpm test:perf:profile:main` 会为 Vitest / Vite 启动和转换开销写入主线程 CPU profile。
  - `pnpm test:perf:profile:runner` 会在关闭文件并行的情况下，为单元测试套件写入运行器 CPU + 堆 profile。

### E2E（Gateway 网关冒烟）

- 命令：`pnpm test:e2e`
- 配置：`vitest.e2e.config.ts`
- 文件：`src/**/*.e2e.test.ts`、`test/**/*.e2e.test.ts`
- 运行时默认值：
  - 使用带 `isolate: false` 的 Vitest `threads`，与仓库其余部分保持一致。
  - 使用自适应 worker（CI：最多 2 个，本地：默认 1 个）。
  - 默认以静默模式运行，以减少控制台 I/O 开销。
- 有用的覆盖项：
  - `OPENCLAW_E2E_WORKERS=<n>` 强制指定 worker 数量（上限 16）。
  - `OPENCLAW_E2E_VERBOSE=1` 重新启用详细控制台输出。
- 范围：
  - 多实例 Gateway 网关端到端行为
  - WebSocket / HTTP 接口、节点配对和更重的网络路径
- 预期：
  - 在 CI 中运行（当流水线中启用时）
  - 不需要真实密钥
  - 比单元测试涉及更多活动部件（可能更慢）

### E2E：OpenShell 后端冒烟

- 命令：`pnpm test:e2e:openshell`
- 文件：`test/openshell-sandbox.e2e.test.ts`
- 范围：
  - 通过 Docker 在宿主机上启动一个隔离的 OpenShell Gateway 网关
  - 从一个临时本地 Dockerfile 创建沙箱
  - 通过真实的 `sandbox ssh-config` + SSH exec 演练 OpenClaw 的 OpenShell 后端
  - 通过沙箱 fs bridge 验证远程规范文件系统行为
- 预期：
  - 仅按需启用；不属于默认 `pnpm test:e2e` 运行的一部分
  - 需要本地 `openshell` CLI 和可用的 Docker daemon
  - 使用隔离的 `HOME` / `XDG_CONFIG_HOME`，然后销毁测试 Gateway 网关和沙箱
- 有用的覆盖项：
  - `OPENCLAW_E2E_OPENSHELL=1` 在手动运行更广泛的 e2e 测试套件时启用此测试
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell` 指向非默认 CLI 二进制文件或包装脚本

### 实时（真实提供商 + 真实模型）

- 命令：`pnpm test:live`
- 配置：`vitest.live.config.ts`
- 文件：`src/**/*.live.test.ts`
- 默认：由 `pnpm test:live` **启用**（设置 `OPENCLAW_LIVE_TEST=1`）
- 范围：
  - “这个提供商 / 模型在 _今天_ 搭配真实凭证是否真的可用？”
  - 捕捉提供商格式变化、工具调用怪癖、认证问题和速率限制行为
- 预期：
  - 按设计不适合在 CI 中保持稳定（真实网络、真实提供商策略、配额、故障）
  - 会花钱 / 消耗速率限制
  - 优先运行缩小范围的子集，而不是“全部”
- 实时运行会加载 `~/.profile` 以获取缺失的 API 密钥。
- 默认情况下，实时运行仍然会隔离 `HOME`，并将配置 / 认证材料复制到临时测试 home 中，这样单元测试 fixture 就不会修改你真实的 `~/.openclaw`。
- 仅当你确实有意让实时测试使用真实 home 目录时，才设置 `OPENCLAW_LIVE_USE_REAL_HOME=1`。
- `pnpm test:live` 现在默认更安静：它会保留 `[live] ...` 进度输出，但会隐藏额外的 `~/.profile` 提示，并静默 Gateway 网关启动日志 / Bonjour 杂讯。如果你想恢复完整启动日志，请设置 `OPENCLAW_LIVE_TEST_QUIET=0`。
- API 密钥轮换（提供商特定）：设置 `*_API_KEYS`，使用逗号 / 分号格式，或设置 `*_API_KEY_1`、`*_API_KEY_2`（例如 `OPENAI_API_KEYS`、`ANTHROPIC_API_KEYS`、`GEMINI_API_KEYS`），也可以通过 `OPENCLAW_LIVE_*_KEY` 为特定实时测试覆盖；测试在遇到速率限制响应时会重试。
- 进度 / 心跳输出：
  - 实时测试套件现在会向 stderr 输出进度行，因此即使 Vitest 控制台捕获较安静，长时间的提供商调用也能看出仍在活动。
  - `vitest.live.config.ts` 禁用了 Vitest 控制台拦截，因此提供商 / Gateway 网关进度行会在实时运行期间立即流式输出。
  - 使用 `OPENCLAW_LIVE_HEARTBEAT_MS` 调整直接模型心跳。
  - 使用 `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS` 调整 Gateway 网关 / 探针心跳。

## 我应该运行哪个测试套件？

使用这个决策表：

- 编辑逻辑 / 测试：运行 `pnpm test`（如果你改动较多，再加上 `pnpm test:coverage`）
- 修改 Gateway 网关网络 / WS 协议 / 配对：额外运行 `pnpm test:e2e`
- 调试“我的 bot 挂了” / 提供商特定故障 / 工具调用：运行一个缩小范围的 `pnpm test:live`

## 实时：Android 节点能力扫描

- 测试：`src/gateway/android-node.capabilities.live.test.ts`
- 脚本：`pnpm android:test:integration`
- 目标：调用已连接 Android 节点当前**公布的每一个命令**，并断言命令契约行为。
- 范围：
  - 预设条件 / 手动设置（该测试套件不会安装 / 运行 / 配对应用）。
  - 针对所选 Android 节点逐命令验证 Gateway 网关 `node.invoke`。
- 必需的预设设置：
  - Android 应用已连接并与 Gateway 网关配对。
  - 应用保持在前台。
  - 为你期望通过的能力授予权限 / 捕获同意。
- 可选目标覆盖项：
  - `OPENCLAW_ANDROID_NODE_ID` 或 `OPENCLAW_ANDROID_NODE_NAME`。
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`。
- 完整 Android 设置详情： [Android App](/zh-CN/platforms/android)

## 实时：模型冒烟（配置档密钥）

实时测试分为两层，这样我们可以隔离故障：

- “直接模型”告诉我们，在给定密钥下，提供商 / 模型是否至少能够响应。
- “Gateway 网关冒烟”告诉我们，针对该模型，完整的 Gateway 网关 + 智能体流水线是否可用（会话、历史、工具、沙箱策略等）。

### 第 1 层：直接模型补全（无 Gateway 网关）

- 测试：`src/agents/models.profiles.live.test.ts`
- 目标：
  - 枚举发现到的模型
  - 使用 `getApiKeyForModel` 选择你有凭证的模型
  - 对每个模型运行一个小型补全（并在需要时运行定向回归）
- 如何启用：
  - `pnpm test:live`（或者如果你直接调用 Vitest，则设置 `OPENCLAW_LIVE_TEST=1`）
- 设置 `OPENCLAW_LIVE_MODELS=modern`（或 `all`，即 modern 的别名）后，此测试套件才会真正运行；否则它会跳过，以便让 `pnpm test:live` 聚焦于 Gateway 网关冒烟
- 如何选择模型：
  - `OPENCLAW_LIVE_MODELS=modern` 运行现代 allowlist（Opus / Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_MODELS=all` 是现代 allowlist 的别名
  - 或 `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."`（逗号分隔 allowlist）
- 如何选择提供商：
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"`（逗号分隔 allowlist）
- 密钥来源：
  - 默认：配置档存储和环境变量回退
  - 设置 `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 可强制**仅**使用配置档存储
- 存在原因：
  - 将“提供商 API 坏了 / 密钥无效”与“Gateway 网关智能体流水线坏了”分离开来
  - 容纳小而独立的回归测试（例如：OpenAI Responses / Codex Responses 的推理回放 + 工具调用流程）

### 第 2 层：Gateway 网关 + 开发智能体冒烟（也就是 “@openclaw” 实际做的事）

- 测试：`src/gateway/gateway-models.profiles.live.test.ts`
- 目标：
  - 启动一个进程内 Gateway 网关
  - 创建 / 修补一个 `agent:dev:*` 会话（每次运行按模型覆盖）
  - 遍历带密钥的模型并断言：
    - “有意义的”响应（无工具）
    - 真实工具调用可用（read 探针）
    - 可选附加工具探针可用（exec+read 探针）
    - OpenAI 回归路径（仅工具调用 → 后续跟进）继续可用
- 探针细节（这样你可以快速解释故障）：
  - `read` 探针：测试会在工作区写入一个 nonce 文件，然后要求智能体 `read` 它并回显该 nonce。
  - `exec+read` 探针：测试会要求智能体通过 `exec` 将 nonce 写入一个临时文件，然后再 `read` 回来。
  - 图像探针：测试会附加一个生成的 PNG（猫 + 随机代码），并期望模型返回 `cat <CODE>`。
  - 实现参考：`src/gateway/gateway-models.profiles.live.test.ts` 和 `src/gateway/live-image-probe.ts`。
- 如何启用：
  - `pnpm test:live`（或者如果你直接调用 Vitest，则设置 `OPENCLAW_LIVE_TEST=1`）
- 如何选择模型：
  - 默认：现代 allowlist（Opus / Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` 是现代 allowlist 的别名
  - 或设置 `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`（或逗号列表）来缩小范围
- 如何选择提供商（避免“OpenRouter 全部都跑”）：
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"`（逗号分隔 allowlist）
- 工具 + 图像探针在这个实时测试中始终开启：
  - `read` 探针 + `exec+read` 探针（工具压力测试）
  - 当模型声明支持图像输入时，会运行图像探针
  - 流程（高层）：
    - 测试生成一个带有 “CAT” + 随机代码的微型 PNG（`src/gateway/live-image-probe.ts`）
    - 通过 `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]` 发送
    - Gateway 网关将附件解析进 `images[]`（`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`）
    - 嵌入式智能体将多模态用户消息转发给模型
    - 断言：回复包含 `cat` + 该代码（OCR 容错：允许轻微错误）

提示：如果你想查看你的机器上能测试什么（以及准确的 `provider/model` id），请运行：

```bash
openclaw models list
openclaw models list --json
```

## 实时：CLI 后端冒烟（Claude CLI 或其他本地 CLI）

- 测试：`src/gateway/gateway-cli-backend.live.test.ts`
- 目标：使用本地 CLI 后端验证 Gateway 网关 + 智能体流水线，而不触碰你的默认配置。
- 启用：
  - `pnpm test:live`（或者如果你直接调用 Vitest，则设置 `OPENCLAW_LIVE_TEST=1`）
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- 默认值：
  - 模型：`claude-cli/claude-sonnet-4-6`
  - 命令：`claude`
  - 参数：`["-p","--output-format","stream-json","--include-partial-messages","--verbose","--permission-mode","bypassPermissions"]`
- 覆盖项（可选）：
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="claude-cli/claude-opus-4-6"`
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/claude"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["-p","--output-format","stream-json","--include-partial-messages","--verbose","--permission-mode","bypassPermissions"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_CLEAR_ENV='["ANTHROPIC_API_KEY","ANTHROPIC_API_KEY_OLD"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` 发送真实图像附件（路径会注入到提示中）。
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` 将图像文件路径作为 CLI 参数传递，而不是注入提示。
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"`（或 `"list"`）控制在设置 `IMAGE_ARG` 时如何传递图像参数。
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` 发送第二轮并验证恢复流程。
- `OPENCLAW_LIVE_CLI_BACKEND_DISABLE_MCP_CONFIG=0` 可保持 Claude CLI MCP 配置启用（默认会注入一个临时的严格空 `--mcp-config`，这样环境 / 全局 MCP 服务器在冒烟期间保持禁用）。

示例：

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="claude-cli/claude-sonnet-4-6" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

Docker 配方：

```bash
pnpm test:docker:live-cli-backend
```

说明：

- Docker 运行器位于 `scripts/test-live-cli-backend-docker.sh`。
- 它会在仓库 Docker 镜像内以非 root 的 `node` 用户身份运行实时 CLI 后端冒烟，因为 Claude CLI 在以 root 身份调用时会拒绝 `bypassPermissions`。
- 对于 `claude-cli`，它会将 Linux `@anthropic-ai/claude-code` 包安装到可缓存、可写的前缀 `OPENCLAW_DOCKER_CLI_TOOLS_DIR` 中（默认：`~/.cache/openclaw/docker-cli-tools`）。
- 对于 `claude-cli`，实时冒烟默认会注入严格的空 MCP 配置，除非你设置 `OPENCLAW_LIVE_CLI_BACKEND_DISABLE_MCP_CONFIG=0`。
- 如果存在，它会把 `~/.claude` 复制到容器中；但在那些通过 `ANTHROPIC_API_KEY` 支持 Claude 认证的机器上，它还会通过 `OPENCLAW_LIVE_CLI_BACKEND_PRESERVE_ENV` 为子 Claude CLI 保留 `ANTHROPIC_API_KEY` / `ANTHROPIC_API_KEY_OLD`。

## 实时：ACP 绑定冒烟（`/acp spawn ... --bind here`）

- 测试：`src/gateway/gateway-acp-bind.live.test.ts`
- 目标：使用实时 ACP 智能体验证真实的 ACP 会话绑定流程：
  - 发送 `/acp spawn <agent> --bind here`
  - 原地绑定一个合成的消息渠道会话
  - 在同一会话上发送普通后续消息
  - 验证后续消息落在绑定的 ACP 会话转录中
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
  - `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=/full/path/to/acpx`
- 说明：
  - 该通道使用 Gateway 网关 `chat.send` 接口，并带有仅管理员可用的合成 originating-route 字段，因此测试可以附加消息渠道上下文，而无需假装进行外部投递。
  - 当 `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND` 未设置时，测试会使用已配置 / 内置的 acpx 命令。如果你的测试环境认证依赖 `~/.profile` 中的环境变量，优先选择一个能保留提供商环境变量的自定义 `acpx` 命令。

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
- 它会加载 `~/.profile`，把匹配的 CLI 认证 home（`~/.claude` 或 `~/.codex`）复制到容器中，把 `acpx` 安装到可写 npm 前缀，然后在缺失时安装所请求的实时 CLI（`@anthropic-ai/claude-code` 或 `@openai/codex`）。
- 在 Docker 内，运行器会设置 `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx`，这样 acpx 就能让来自已加载 profile 的提供商环境变量继续对其子 harness CLI 可用。

### 推荐的实时测试配方

范围窄、显式的 allowlist 最快，也最不容易不稳定：

- 单个模型，直接运行（无 Gateway 网关）：
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- 单个模型，Gateway 网关冒烟：
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 跨多个提供商的工具调用：
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Google 聚焦（Gemini API 密钥 + Antigravity）：
  - Gemini（API 密钥）：`OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity（OAuth）：`OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

说明：

- `google/...` 使用 Gemini API（API 密钥）。
- `google-antigravity/...` 使用 Antigravity OAuth bridge（Cloud Code Assist 风格的智能体端点）。
- `google-gemini-cli/...` 使用你机器上的本地 Gemini CLI（单独的认证 + 工具链怪癖）。
- Gemini API 与 Gemini CLI：
  - API：OpenClaw 通过 HTTP 调用 Google 托管的 Gemini API（API 密钥 / 配置档认证）；这通常就是大多数用户所说的 “Gemini”。
  - CLI：OpenClaw 会 shell out 到本地 `gemini` 二进制文件；它有自己的认证方式，行为也可能不同（流式传输 / 工具支持 / 版本偏差）。

## 实时：模型矩阵（我们覆盖什么）

没有固定的“CI 模型列表”（实时测试是按需启用的），但这些是在拥有密钥的开发机器上建议定期覆盖的**推荐**模型。

### 现代冒烟集合（工具调用 + 图像）

这是我们期望始终保持可用的“常见模型”运行集：

- OpenAI（非 Codex）：`openai/gpt-5.4`（可选：`openai/gpt-5.4-mini`）
- OpenAI Codex：`openai-codex/gpt-5.4`
- Anthropic：`anthropic/claude-opus-4-6`（或 `anthropic/claude-sonnet-4-6`）
- Google（Gemini API）：`google/gemini-3.1-pro-preview` 和 `google/gemini-3-flash-preview`（避免较旧的 Gemini 2.x 模型）
- Google（Antigravity）：`google-antigravity/claude-opus-4-6-thinking` 和 `google-antigravity/gemini-3-flash`
- Z.AI（GLM）：`zai/glm-4.7`
- MiniMax：`minimax/MiniMax-M2.7`

运行带工具 + 图像的 Gateway 网关冒烟：
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### 基线：工具调用（Read + 可选 Exec）

每个提供商家族至少选择一个：

- OpenAI：`openai/gpt-5.4`（或 `openai/gpt-5.4-mini`）
- Anthropic：`anthropic/claude-opus-4-6`（或 `anthropic/claude-sonnet-4-6`）
- Google：`google/gemini-3-flash-preview`（或 `google/gemini-3.1-pro-preview`）
- Z.AI（GLM）：`zai/glm-4.7`
- MiniMax：`minimax/MiniMax-M2.7`

可选附加覆盖（有的话更好）：

- xAI：`xai/grok-4`（或最新可用版本）
- Mistral：`mistral/`…（选择一个你已启用、支持工具的模型）
- Cerebras：`cerebras/`…（如果你有访问权限）
- LM Studio：`lmstudio/`…（本地；工具调用取决于 API 模式）

### Vision：图像发送（附件 → 多模态消息）

在 `OPENCLAW_LIVE_GATEWAY_MODELS` 中至少包含一个支持图像的模型（Claude / Gemini / OpenAI 支持视觉的变体等），以演练图像探针。

### 聚合器 / 替代 Gateway 网关

如果你启用了相关密钥，我们也支持通过以下方式测试：

- OpenRouter：`openrouter/...`（数百个模型；使用 `openclaw models scan` 查找支持工具 + 图像的候选模型）
- OpenCode：`opencode/...` 用于 Zen，`opencode-go/...` 用于 Go（通过 `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY` 认证）

如果你有凭证 / 配置，还可以把更多提供商纳入实时矩阵：

- 内置：`openai`、`openai-codex`、`anthropic`、`google`、`google-vertex`、`google-antigravity`、`google-gemini-cli`、`zai`、`openrouter`、`opencode`、`opencode-go`、`xai`、`groq`、`cerebras`、`mistral`、`github-copilot`
- 通过 `models.providers`（自定义端点）：`minimax`（云 / API），以及任何兼容 OpenAI / Anthropic 的代理（LM Studio、vLLM、LiteLLM 等）

提示：不要尝试在文档里硬编码“所有模型”。权威列表始终是你机器上 `discoverModels(...)` 返回的结果，加上当前可用的密钥。

## 凭证（绝不要提交）

实时测试发现凭证的方式与 CLI 相同。实际含义是：

- 如果 CLI 可用，实时测试应该能找到同样的密钥。
- 如果实时测试提示“没有凭证”，那就用和调试 `openclaw models list` / 模型选择相同的方式来排查。

- 按智能体划分的认证配置档：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（这就是实时测试里“配置档密钥”的含义）
- 配置：`~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）
- 旧版状态目录：`~/.openclaw/credentials/`（如果存在，会复制到暂存的实时 home 中，但它不是主配置档密钥存储）
- 本地实时运行默认会把当前配置、按智能体划分的 `auth-profiles.json` 文件、旧版 `credentials/` 以及受支持的外部 CLI 认证目录复制到临时测试 home；在该暂存配置中，`agents.*.workspace` / `agentDir` 路径覆盖会被剥离，这样探针就不会落到你真实宿主机的工作区上。

如果你想依赖环境变量密钥（例如导出在 `~/.profile` 中），请在 `source ~/.profile` 之后运行本地测试，或者使用下面的 Docker 运行器（它们可以把 `~/.profile` 挂载进容器）。

## Deepgram 实时测试（音频转录）

- 测试：`src/media-understanding/providers/deepgram/audio.live.test.ts`
- 启用：`DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus（国际版） 编码方案实时测试

- 测试：`src/agents/byteplus.live.test.ts`
- 启用：`BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- 可选模型覆盖：`BYTEPLUS_CODING_MODEL=ark-code-latest`

## 图像生成实时测试

- 测试：`src/image-generation/runtime.live.test.ts`
- 命令：`pnpm test:live src/image-generation/runtime.live.test.ts`
- 范围：
  - 枚举每个已注册的图像生成提供商插件
  - 在探测前从你的登录 shell（`~/.profile`）中加载缺失的提供商环境变量
  - 默认优先使用实时 / 环境 API 密钥，而不是已存储的认证配置档，这样 `auth-profiles.json` 里的陈旧测试密钥就不会掩盖真实 shell 凭证
  - 跳过没有可用认证 / 配置档 / 模型的提供商
  - 通过共享运行时能力运行标准图像生成变体：
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- 当前覆盖的内置提供商：
  - `openai`
  - `google`
- 可选缩小范围：
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- 可选认证行为：
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 强制使用配置档存储认证，并忽略仅环境变量覆盖

## Docker 运行器（可选的“可在 Linux 中工作”检查）

这些 Docker 运行器分为两类：

- 实时模型运行器：`test:docker:live-models` 和 `test:docker:live-gateway` 仅在仓库 Docker 镜像内运行各自匹配的配置档密钥实时测试文件（`src/agents/models.profiles.live.test.ts` 和 `src/gateway/gateway-models.profiles.live.test.ts`），并挂载你的本地配置目录和工作区（如果已挂载，也会加载 `~/.profile`）。对应的本地入口点是 `test:live:models-profiles` 和 `test:live:gateway-profiles`。
- Docker 实时运行器默认使用更小的冒烟上限，以便完整 Docker 扫描保持可操作性：
  `test:docker:live-models` 默认设置 `OPENCLAW_LIVE_MAX_MODELS=12`，而
  `test:docker:live-gateway` 默认设置 `OPENCLAW_LIVE_GATEWAY_SMOKE=1`、
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`、
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`，以及
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`。如果你
  明确想要更大、更穷举的扫描，请覆盖这些环境变量。
- `test:docker:all` 会先通过 `test:docker:live-build` 构建一次实时 Docker 镜像，然后在两个实时 Docker 通道中复用它。
- 容器冒烟运行器：`test:docker:openwebui`、`test:docker:onboard`、`test:docker:gateway-network`、`test:docker:mcp-channels` 和 `test:docker:plugins` 会启动一个或多个真实容器，并验证更高层级的集成路径。

实时模型 Docker 运行器还会仅 bind-mount 所需的 CLI 认证 home（如果运行未缩小范围，则挂载所有受支持的目录），然后在运行前将它们复制到容器 home 中，这样外部 CLI OAuth 就可以刷新令牌，而不会修改宿主机认证存储：

- 直接模型：`pnpm test:docker:live-models`（脚本：`scripts/test-live-models-docker.sh`）
- ACP 绑定冒烟：`pnpm test:docker:live-acp-bind`（脚本：`scripts/test-live-acp-bind-docker.sh`）
- CLI 后端冒烟：`pnpm test:docker:live-cli-backend`（脚本：`scripts/test-live-cli-backend-docker.sh`）
- Gateway 网关 + 开发智能体：`pnpm test:docker:live-gateway`（脚本：`scripts/test-live-gateway-models-docker.sh`）
- Open WebUI 实时冒烟：`pnpm test:docker:openwebui`（脚本：`scripts/e2e/openwebui-docker.sh`）
- 新手引导向导（TTY，完整脚手架）：`pnpm test:docker:onboard`（脚本：`scripts/e2e/onboard-docker.sh`）
- Gateway 网关网络（两个容器，WS 认证 + 健康检查）：`pnpm test:docker:gateway-network`（脚本：`scripts/e2e/gateway-network-docker.sh`）
- MCP 渠道桥接（带种子的 Gateway 网关 + stdio bridge + 原始 Claude notification-frame 冒烟）：`pnpm test:docker:mcp-channels`（脚本：`scripts/e2e/mcp-channels-docker.sh`）
- 插件（安装冒烟 + `/plugin` 别名 + Claude bundle 重启语义）：`pnpm test:docker:plugins`（脚本：`scripts/e2e/plugins-docker.sh`）

实时模型 Docker 运行器还会以只读方式 bind-mount 当前 checkout，并将其暂存到容器内的临时 workdir 中。这样可以保持运行时镜像轻量，同时仍然让 Vitest 针对你本地精确的源代码 / 配置运行。
它们还会设置 `OPENCLAW_SKIP_CHANNELS=1`，这样 Gateway 网关实时探针就不会在容器内启动真实的 Telegram / Discord / 等渠道 worker。
`test:docker:live-models` 仍然会运行 `pnpm test:live`，因此当你需要缩小范围或从该 Docker 通道排除 Gateway 网关实时覆盖时，也请一并传入
`OPENCLAW_LIVE_GATEWAY_*`。
`test:docker:openwebui` 是一个更高层级的兼容性冒烟：它会启动一个启用了 OpenAI 兼容 HTTP 端点的
OpenClaw Gateway 网关容器，针对该 Gateway 网关启动一个固定版本的 Open WebUI 容器，通过
Open WebUI 登录，验证 `/api/models` 暴露了 `openclaw/default`，然后通过
Open WebUI 的 `/api/chat/completions` 代理发送一个真实聊天请求。
第一次运行可能会明显更慢，因为 Docker 可能需要拉取
Open WebUI 镜像，而且 Open WebUI 也可能需要完成自己的冷启动设置。
这个通道需要一个可用的实时模型密钥，而 `OPENCLAW_PROFILE_FILE`
（默认 `~/.profile`）是在 Docker 化运行中提供该密钥的主要方式。
成功运行会打印一个小型 JSON 负载，例如 `{ "ok": true, "model":
"openclaw/default", ... }`。
`test:docker:mcp-channels` 刻意保持确定性，不需要真实的
Telegram、Discord 或 iMessage 账号。它会启动一个带种子的 Gateway 网关
容器，再启动第二个容器来拉起 `openclaw mcp serve`，然后
验证路由后的会话发现、转录读取、附件元数据、
实时事件队列行为、出站发送路由，以及 Claude 风格的渠道 +
权限通知，这些都通过真实的 stdio MCP bridge 完成。通知检查
会直接检查原始 stdio MCP 帧，因此该冒烟验证的是
bridge 实际发出的内容，而不仅仅是某个特定客户端 SDK 恰好暴露出来的内容。

手动 ACP 自然语言线程冒烟（不在 CI 中）：

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- 保留此脚本用于回归 / 调试工作流。之后仍可能需要它来验证 ACP 线程路由，因此不要删除它。

有用的环境变量：

- `OPENCLAW_CONFIG_DIR=...`（默认：`~/.openclaw`）挂载到 `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...`（默认：`~/.openclaw/workspace`）挂载到 `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...`（默认：`~/.profile`）挂载到 `/home/node/.profile`，并在运行测试前加载
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...`（默认：`~/.cache/openclaw/docker-cli-tools`）挂载到 `/home/node/.npm-global`，用于缓存 Docker 内部的 CLI 安装
- `$HOME` 下的外部 CLI 认证目录会以只读方式挂载到 `/host-auth/...`，然后在测试开始前复制到 `/home/node/...`
  - 默认：挂载所有受支持目录（`.codex`、`.claude`、`.minimax`）
  - 缩小范围的提供商运行只挂载从 `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS` 推断出的所需目录
  - 手动覆盖：`OPENCLAW_DOCKER_AUTH_DIRS=all`、`OPENCLAW_DOCKER_AUTH_DIRS=none`，或逗号列表，例如 `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` 用于缩小运行范围
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...` 用于在容器内过滤提供商
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 确保凭证来自配置档存储（而不是环境变量）
- `OPENCLAW_OPENWEBUI_MODEL=...` 选择 Open WebUI 冒烟中由 Gateway 网关暴露的模型
- `OPENCLAW_OPENWEBUI_PROMPT=...` 覆盖 Open WebUI 冒烟所用的 nonce 检查提示
- `OPENWEBUI_IMAGE=...` 覆盖固定的 Open WebUI 镜像标签

## 文档完整性检查

编辑文档后运行文档检查：`pnpm check:docs`。
当你还需要页内标题检查时，运行完整的 Mintlify anchor 验证：`pnpm docs:check-links:anchors`。

## 离线回归（CI 安全）

这些是“不依赖真实提供商”的“真实流水线”回归：

- Gateway 网关工具调用（模拟 OpenAI，真实 Gateway 网关 + 智能体循环）：`src/gateway/gateway.test.ts`（用例：“runs a mock OpenAI tool call end-to-end via gateway agent loop”）
- Gateway 网关向导（WS `wizard.start` / `wizard.next`，强制写入配置 + 认证）：`src/gateway/gateway.test.ts`（用例：“runs wizard over ws and writes auth token config”）

## 智能体可靠性评估（Skills）

我们已经有一些 CI 安全的测试，它们的行为类似于“智能体可靠性评估”：

- 通过真实 Gateway 网关 + 智能体循环进行模拟工具调用（`src/gateway/gateway.test.ts`）。
- 验证会话接线与配置效果的端到端向导流程（`src/gateway/gateway.test.ts`）。

对于 Skills（见 [Skills](/zh-CN/tools/skills)）仍然缺少的内容：

- **决策能力：** 当提示中列出 Skills 时，智能体是否会选择正确的 Skill（或避免无关的 Skill）？
- **合规性：** 智能体是否会在使用前读取 `SKILL.md`，并遵循必需的步骤 / 参数？
- **工作流契约：** 断言工具顺序、会话历史延续和沙箱边界的多轮场景。

未来的评估应首先保持确定性：

- 一个使用模拟提供商的场景运行器，用来断言工具调用 + 顺序、Skill 文件读取和会话接线。
- 一小组聚焦 Skill 的场景（使用 vs 避免、门控、提示注入）。
- 只有在 CI 安全测试套件到位之后，才添加可选的实时评估（按需启用、受环境变量控制）。

## 契约测试（插件和渠道形状）

契约测试用于验证每个已注册的插件和渠道都符合其
接口契约。它们会遍历所有已发现的插件，并运行一组
形状和行为断言。默认的 `pnpm test` 单元通道有意
跳过这些共享接缝和冒烟文件；当你修改共享渠道或提供商接口时，
请显式运行契约命令。

### 命令

- 所有契约：`pnpm test:contracts`
- 仅渠道契约：`pnpm test:contracts:channels`
- 仅提供商契约：`pnpm test:contracts:plugins`

### 渠道契约

位于 `src/channels/plugins/contracts/*.contract.test.ts`：

- **plugin** - 基础插件形状（id、名称、能力）
- **setup** - 设置向导契约
- **session-binding** - 会话绑定行为
- **outbound-payload** - 消息负载结构
- **inbound** - 入站消息处理
- **actions** - 渠道操作处理器
- **threading** - 线程 ID 处理
- **directory** - 目录 / roster API
- **group-policy** - 群组策略执行

### 提供商状态契约

位于 `src/plugins/contracts/*.contract.test.ts`。

- **status** - 渠道状态探针
- **registry** - 插件注册表形状

### 提供商契约

位于 `src/plugins/contracts/*.contract.test.ts`：

- **auth** - 认证流程契约
- **auth-choice** - 认证选择 / 选择逻辑
- **catalog** - 模型目录 API
- **discovery** - 插件发现
- **loader** - 插件加载
- **runtime** - 提供商运行时
- **shape** - 插件形状 / 接口
- **wizard** - 设置向导

### 何时运行

- 修改 plugin-sdk 导出或子路径之后
- 添加或修改渠道或提供商插件之后
- 重构插件注册或发现逻辑之后

契约测试会在 CI 中运行，不需要真实 API 密钥。

## 添加回归测试（指南）

当你修复了一个在实时测试中发现的提供商 / 模型问题时：

- 如果可能，添加一个 CI 安全的回归测试（模拟 / stub 提供商，或捕获精确的请求形状转换）
- 如果它本质上只能做实时测试（速率限制、认证策略），那就让实时测试保持范围狭窄，并通过环境变量按需启用
- 优先锁定能捕捉该 bug 的最小层级：
  - 提供商请求转换 / 回放 bug → 直接模型测试
  - Gateway 网关会话 / 历史 / 工具流水线 bug → Gateway 网关实时冒烟或 CI 安全的 Gateway 网关模拟测试
- SecretRef 遍历防护栏：
  - `src/secrets/exec-secret-ref-id-parity.test.ts` 会从注册表元数据（`listSecretTargetRegistryEntries()`）中为每个 SecretRef 类派生一个采样目标，然后断言遍历段 exec id 会被拒绝。
  - 如果你在 `src/secrets/target-registry-data.ts` 中新增了一个 `includeInPlan` SecretRef 目标族，请更新该测试中的 `classifyTargetClass`。该测试会在遇到未分类目标 id 时故意失败，这样新类别就不能被悄悄跳过。
