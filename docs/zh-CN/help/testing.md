---
read_when:
    - 在本地或 CI 中运行测试
    - 为模型 / 提供商缺陷添加回归测试
    - 调试 Gateway 网关 + 智能体行为
summary: 测试工具包：单元 / e2e / 实时测试套件、Docker 运行器，以及每类测试覆盖的内容
title: 测试
x-i18n:
    generated_at: "2026-04-12T18:04:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: a66ea672c386094ab4a8035a082c8a85d508a14301ad44b628d2a10d9cec3a52
    source_path: help/testing.md
    workflow: 15
---

# 测试

OpenClaw 有三套 Vitest 测试套件（单元 / 集成、e2e、实时）以及一小组 Docker 运行器。

本文档是一份“我们如何测试”的指南：

- 每个测试套件覆盖什么（以及它有意 _不_ 覆盖什么）
- 常见工作流应运行哪些命令（本地、推送前、调试）
- 实时测试如何发现凭证并选择模型 / 提供商
- 如何为真实世界中的模型 / 提供商问题添加回归测试

## 快速开始

大多数时候：

- 完整门禁（预期在推送前执行）：`pnpm build && pnpm check && pnpm test`
- 在配置充足的机器上更快地运行本地完整测试套件：`pnpm test:max`
- 直接进入 Vitest 监视循环：`pnpm test:watch`
- 现在也支持将扩展 / 渠道路径直接定向到文件：`pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- 当你在迭代单个失败问题时，优先使用定向运行。
- 基于 Docker 的 QA 站点：`pnpm qa:lab:up`
- 基于 Linux VM 的 QA 测试通道：`pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

当你修改了测试或希望获得更多信心时：

- 覆盖率门禁：`pnpm test:coverage`
- E2E 测试套件：`pnpm test:e2e`

当你在调试真实的提供商 / 模型时（需要真实凭证）：

- 实时测试套件（模型 + Gateway 网关工具 / 图像探测）：`pnpm test:live`
- 安静地只运行一个实时测试文件：`pnpm test:live -- src/agents/models.profiles.live.test.ts`

提示：当你只需要一个失败用例时，优先使用下面说明的允许列表环境变量来缩小实时测试范围。

## QA 专用运行器

当你需要更接近 QA-lab 的真实环境时，这些命令与主测试套件并列使用：

- `pnpm openclaw qa suite`
  - 直接在主机上运行由仓库支持的 QA 场景。
  - 默认并行运行多个选定场景，并为每个场景使用隔离的 Gateway 网关工作进程，最多 64 个工作进程或等于所选场景数量。使用 `--concurrency <count>` 调整工作进程数量，或使用 `--concurrency 1` 启用旧的串行通道。
- `pnpm openclaw qa suite --runner multipass`
  - 在一次性 Multipass Linux VM 中运行相同的 QA 测试套件。
  - 与主机上的 `qa suite` 保持相同的场景选择行为。
  - 复用与 `qa suite` 相同的提供商 / 模型选择标志。
  - 实时运行会转发对客户机实用的受支持 QA 鉴权输入：基于环境变量的提供商密钥、QA 实时提供商配置路径，以及存在时的 `CODEX_HOME`。
  - 输出目录必须保持在仓库根目录下，这样客户机才能通过挂载的工作区回写内容。
  - 将常规 QA 报告 + 摘要以及 Multipass 日志写入 `.artifacts/qa-e2e/...`。
- `pnpm qa:lab:up`
  - 启动基于 Docker 的 QA 站点，用于运维式 QA 工作。
- `pnpm openclaw qa matrix`
  - 针对一次性、基于 Docker 的 Tuwunel homeserver 运行 Matrix 实时 QA 通道。
  - 预配三个临时 Matrix 用户（`driver`、`sut`、`observer`）和一个私有房间，然后启动一个 QA Gateway 网关子进程，使用真实的 Matrix 插件作为 SUT 传输层。
  - 默认使用固定稳定版 Tuwunel 镜像 `ghcr.io/matrix-construct/tuwunel:v1.5.1`。当你需要测试其他镜像时，可用 `OPENCLAW_QA_MATRIX_TUWUNEL_IMAGE` 覆盖。
  - 将 Matrix QA 报告、摘要和 observed-events 工件写入 `.artifacts/qa-e2e/...`。
- `pnpm openclaw qa telegram`
  - 使用来自环境变量的 `driver` 和 SUT 机器人令牌，针对真实私有群组运行 Telegram 实时 QA 通道。
  - 需要 `OPENCLAW_QA_TELEGRAM_GROUP_ID`、`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` 和 `OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`。群组 id 必须是 Telegram 聊天的数字 id。
  - 需要两个位于同一私有群组中的不同机器人，并且 SUT 机器人需要暴露 Telegram 用户名。
  - 为了实现稳定的 bot-to-bot 观测，请在 `@BotFather` 中为两个机器人启用 Bot-to-Bot Communication Mode，并确保 `driver` 机器人可以观测群组中的机器人流量。
  - 将 Telegram QA 报告、摘要和 observed-messages 工件写入 `.artifacts/qa-e2e/...`。

实时传输通道共享一份标准契约，以避免新传输层发生漂移：

`qa-channel` 仍然是覆盖面较广的合成 QA 测试套件，不属于实时传输覆盖矩阵的一部分。

| 通道 | Canary | 提及门控 | 允许列表拦截 | 顶层回复 | 重启恢复 | 线程跟进 | 线程隔离 | 反应观测 | help 命令 |
| ---- | ------ | -------- | ------------ | -------- | -------- | -------- | -------- | -------- | --------- |
| Matrix | x | x | x | x | x | x | x | x |  |
| Telegram | x |  |  |  |  |  |  |  | x |

### 向 QA 添加一个渠道

向 Markdown QA 系统中添加一个渠道，严格来说只需要两样东西：

1. 该渠道的传输适配器。
2. 一个用于验证渠道契约的场景包。

当共享的 `qa-lab` 运行器可以承载该流程时，不要添加渠道专用 QA 运行器。

`qa-lab` 负责共享机制：

- 测试套件启动与清理
- 工作进程并发
- 工件写入
- 报告生成
- 场景执行
- 对旧版 `qa-channel` 场景的兼容别名

渠道适配器负责传输契约：

- 如何为该传输层配置 Gateway 网关
- 如何检查就绪状态
- 如何注入入站事件
- 如何观测出站消息
- 如何暴露转录内容和规范化后的传输状态
- 如何执行基于传输层的操作
- 如何处理传输专属的重置或清理

新渠道的最低接入门槛是：

1. 在共享的 `qa-lab` 接缝上实现传输适配器。
2. 在传输注册表中注册该适配器。
3. 将传输专属机制保留在适配器或渠道测试 harness 内部。
4. 在 `qa/scenarios/` 下编写或适配 Markdown 场景。
5. 对新场景使用通用场景辅助函数。
6. 保持现有兼容别名继续可用，除非仓库正在进行有意的迁移。

决策规则是严格的：

- 如果某种行为可以在 `qa-lab` 中统一表达一次，就把它放在 `qa-lab` 中。
- 如果某种行为依赖某一个渠道传输层，就把它保留在该适配器或插件 harness 中。
- 如果某个场景需要一种可供多个渠道使用的新能力，请添加通用辅助函数，而不是在 `suite.ts` 中添加渠道专属分支。
- 如果某种行为只对一个传输层有意义，就让该场景保持传输层专属，并在场景契约中明确说明。

新场景推荐使用的通用辅助函数名称是：

- `waitForTransportReady`
- `waitForChannelReady`
- `injectInboundMessage`
- `injectOutboundMessage`
- `waitForTransportOutboundMessage`
- `waitForChannelOutboundMessage`
- `waitForNoTransportOutbound`
- `getTransportSnapshot`
- `readTransportMessage`
- `readTransportTranscript`
- `formatTransportTranscript`
- `resetTransport`

现有场景仍可使用兼容别名，包括：

- `waitForQaChannelReady`
- `waitForOutboundMessage`
- `waitForNoOutbound`
- `formatConversationTranscript`
- `resetBus`

新的渠道工作应使用这些通用辅助函数名称。
兼容别名存在的目的是避免一次性迁移日，而不是作为新场景编写的范式。

## 测试套件（各自在哪里运行）

可以把这些测试套件理解为“真实度逐步提升”（同时也会带来更高的不稳定性 / 成本）：

### 单元 / 集成（默认）

- 命令：`pnpm test`
- 配置：对现有按范围划分的 Vitest 项目执行十次顺序分片运行（`vitest.full-*.config.ts`）
- 文件：`src/**/*.test.ts`、`packages/**/*.test.ts`、`test/**/*.test.ts` 下的 core / unit 清单，以及由 `vitest.unit.config.ts` 覆盖并列入白名单的 `ui` Node 测试
- 范围：
  - 纯单元测试
  - 进程内集成测试（Gateway 网关鉴权、路由、工具、解析、配置）
  - 针对已知缺陷的确定性回归测试
- 预期：
  - 在 CI 中运行
  - 不需要真实密钥
  - 应该快速且稳定
- 项目说明：
  - 无定向目标的 `pnpm test` 现在运行 11 个更小的分片配置（`core-unit-src`、`core-unit-security`、`core-unit-ui`、`core-unit-support`、`core-support-boundary`、`core-contracts`、`core-bundled`、`core-runtime`、`agentic`、`auto-reply`、`extensions`），而不是一个庞大的原生根项目进程。这样可以降低高负载机器上的 RSS 峰值，并避免 auto-reply / 扩展相关工作拖累无关测试套件。
  - `pnpm test --watch` 仍然使用原生根 `vitest.config.ts` 项目图，因为多分片 watch 循环并不现实。
  - `pnpm test`、`pnpm test:watch` 和 `pnpm test:perf:imports` 现在会优先将显式文件 / 目录目标路由到按范围划分的通道，因此 `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` 不必承担完整根项目启动成本。
  - 当 diff 只涉及可路由的源码 / 测试文件时，`pnpm test:changed` 会将变更的 git 路径展开到相同的按范围划分通道中；配置 / setup 修改仍会回退到更广泛的根项目重新运行。
  - 来自 agents、commands、plugins、auto-reply 辅助函数、`plugin-sdk` 及类似纯工具区域的轻导入单元测试，会通过 `unit-fast` 通道运行，该通道会跳过 `test/setup-openclaw-runtime.ts`；有状态 / 运行时较重的文件仍保留在现有通道上。
  - 选定的 `plugin-sdk` 和 `commands` 辅助源码文件，在 changed 模式运行时也会映射到这些轻量通道中的显式同级测试，因此对辅助函数的修改无需为该目录重新运行完整的重型测试套件。
  - `auto-reply` 现在有三个专用分桶：顶层 core 辅助函数、顶层 `reply.*` 集成测试，以及 `src/auto-reply/reply/**` 子树。这样可以让最重的 reply harness 工作不影响轻量级状态 / 分块 / token 测试。
- 嵌入式运行器说明：
  - 当你修改消息工具发现输入或压缩运行时上下文时，
    需要同时保留两个层级的覆盖。
  - 为纯路由 / 规范化边界添加聚焦的辅助函数回归测试。
  - 同时也要确保嵌入式运行器集成测试套件保持健康：
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`、
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts` 和
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`。
  - 这些测试套件验证带作用域的 id 和压缩行为仍然通过真实的 `run.ts` / `compact.ts` 路径流转；仅有辅助函数测试并不能充分替代这些集成路径。
- 进程池说明：
  - 基础 Vitest 配置现在默认使用 `threads`。
  - 共享的 Vitest 配置还固定了 `isolate: false`，并在根项目、e2e 和实时配置中使用非隔离运行器。
  - 根 UI 通道保留了其 `jsdom` setup 和优化器，但现在也运行在共享的非隔离运行器上。
  - 每个 `pnpm test` 分片都会从共享 Vitest 配置继承相同的 `threads` + `isolate: false` 默认值。
  - 共享的 `scripts/run-vitest.mjs` 启动器现在默认也会为 Vitest 子 Node 进程添加 `--no-maglev`，以减少大型本地运行期间的 V8 编译抖动。如果你需要与默认 V8 行为进行对比，请设置 `OPENCLAW_VITEST_ENABLE_MAGLEV=1`。
- 快速本地迭代说明：
  - 当变更路径可以清晰映射到更小的测试套件时，`pnpm test:changed` 会通过按范围划分的通道进行路由。
  - `pnpm test:max` 和 `pnpm test:changed:max` 保持相同的路由行为，只是使用更高的工作进程上限。
  - 本地工作进程自动缩放现在有意更保守，并且当主机负载平均值已经较高时也会回退，因此默认情况下多个并发 Vitest 运行对系统的影响更小。
  - 基础 Vitest 配置将这些项目 / 配置文件标记为 `forceRerunTriggers`，以便在测试接线发生变化时，changed 模式重跑仍然正确。
  - 配置会在受支持主机上保持启用 `OPENCLAW_VITEST_FS_MODULE_CACHE`；如果你希望为直接性能分析指定一个明确缓存位置，请设置 `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path`。
- 性能调试说明：
  - `pnpm test:perf:imports` 会启用 Vitest 导入耗时报告以及导入明细输出。
  - `pnpm test:perf:imports:changed` 会将相同的性能分析视图限定到自 `origin/main` 以来发生变更的文件。
- `pnpm test:perf:changed:bench -- --ref <git-ref>` 会将已路由的 `test:changed` 与该提交 diff 的原生根项目路径进行比较，并打印总耗时以及 macOS 最大 RSS。
- `pnpm test:perf:changed:bench -- --worktree` 会通过将变更文件列表路由到 `scripts/test-projects.mjs` 和根 Vitest 配置，对当前未提交工作树进行基准测试。
  - `pnpm test:perf:profile:main` 会为 Vitest / Vite 启动和 transform 开销写入主线程 CPU profile。
  - `pnpm test:perf:profile:runner` 会在禁用文件并行的情况下，为单元测试套件写入运行器 CPU + 堆 profile。

### E2E（Gateway 网关冒烟）

- 命令：`pnpm test:e2e`
- 配置：`vitest.e2e.config.ts`
- 文件：`src/**/*.e2e.test.ts`、`test/**/*.e2e.test.ts`
- 运行时默认值：
  - 使用 Vitest `threads` 且 `isolate: false`，与仓库其余部分保持一致。
  - 使用自适应工作进程（CI：最多 2 个，本地：默认 1 个）。
  - 默认以静默模式运行，以减少控制台 I/O 开销。
- 常用覆盖方式：
  - `OPENCLAW_E2E_WORKERS=<n>`：强制指定工作进程数量（上限 16）。
  - `OPENCLAW_E2E_VERBOSE=1`：重新启用详细控制台输出。
- 范围：
  - 多实例 Gateway 网关端到端行为
  - WebSocket / HTTP 接口、节点配对以及更重的网络交互
- 预期：
  - 在 CI 中运行（当流水线启用时）
  - 不需要真实密钥
  - 比单元测试有更多可变部件（可能更慢）

### E2E：OpenShell 后端冒烟

- 命令：`pnpm test:e2e:openshell`
- 文件：`test/openshell-sandbox.e2e.test.ts`
- 范围：
  - 通过 Docker 在主机上启动一个隔离的 OpenShell Gateway 网关
  - 从一个临时本地 Dockerfile 创建一个沙箱
  - 通过真实的 `sandbox ssh-config` + SSH 执行来验证 OpenClaw 的 OpenShell 后端
  - 通过沙箱 fs bridge 验证远端规范文件系统行为
- 预期：
  - 仅按需启用；不属于默认的 `pnpm test:e2e` 运行
  - 需要本地 `openshell` CLI 和可用的 Docker daemon
  - 使用隔离的 `HOME` / `XDG_CONFIG_HOME`，然后销毁测试 Gateway 网关和沙箱
- 常用覆盖方式：
  - `OPENCLAW_E2E_OPENSHELL=1`：在手动运行更广泛的 e2e 测试套件时启用该测试
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`：指向非默认的 CLI 二进制文件或包装脚本

### 实时（真实提供商 + 真实模型）

- 命令：`pnpm test:live`
- 配置：`vitest.live.config.ts`
- 文件：`src/**/*.live.test.ts`
- 默认：由 `pnpm test:live` **启用**（设置 `OPENCLAW_LIVE_TEST=1`）
- 范围：
  - “这个提供商 / 模型在 _今天_ 使用真实凭证时是否真的可用？”
  - 捕获提供商格式变化、工具调用怪癖、鉴权问题以及速率限制行为
- 预期：
  - 从设计上就不适合作为稳定 CI（真实网络、真实提供商策略、配额、故障）
  - 会花钱 / 消耗速率限制
  - 优先运行缩小范围的子集，而不是“全部”
- 实时运行会加载 `~/.profile` 以补齐缺失的 API 密钥。
- 默认情况下，实时运行仍会隔离 `HOME`，并将配置 / 鉴权材料复制到临时测试 home 中，以免单元测试夹具修改你的真实 `~/.openclaw`。
- 仅当你明确需要实时测试使用真实 home 目录时，才设置 `OPENCLAW_LIVE_USE_REAL_HOME=1`。
- `pnpm test:live` 现在默认使用更安静的模式：会保留 `[live] ...` 进度输出，但会隐藏额外的 `~/.profile` 提示，并静音 Gateway 网关引导日志 / Bonjour 杂音。如果你希望恢复完整启动日志，请设置 `OPENCLAW_LIVE_TEST_QUIET=0`。
- API 密钥轮换（提供商专属）：设置逗号 / 分号格式的 `*_API_KEYS`，或设置 `*_API_KEY_1`、`*_API_KEY_2`（例如 `OPENAI_API_KEYS`、`ANTHROPIC_API_KEYS`、`GEMINI_API_KEYS`），也可以通过 `OPENCLAW_LIVE_*_KEY` 为实时测试单独覆盖；测试在收到速率限制响应时会重试。
- 进度 / 心跳输出：
  - 实时测试套件现在会向 stderr 输出进度行，因此即使 Vitest 控制台捕获较安静，较长时间的提供商调用也能明显看出仍在运行。
  - `vitest.live.config.ts` 会禁用 Vitest 的控制台拦截，因此提供商 / Gateway 网关进度行会在实时运行期间立即流式输出。
  - 使用 `OPENCLAW_LIVE_HEARTBEAT_MS` 调整直接模型心跳。
  - 使用 `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS` 调整 Gateway 网关 / 探测心跳。

## 我应该运行哪个测试套件？

使用下面的决策表：

- 修改逻辑 / 测试：运行 `pnpm test`（如果改动很多，再运行 `pnpm test:coverage`）
- 涉及 Gateway 网关网络 / WS 协议 / 配对：额外运行 `pnpm test:e2e`
- 调试“我的机器人挂了” / 提供商专属故障 / 工具调用：运行缩小范围的 `pnpm test:live`

## 实时：Android 节点能力扫描

- 测试：`src/gateway/android-node.capabilities.live.test.ts`
- 脚本：`pnpm android:test:integration`
- 目标：调用已连接 Android 节点当前**公布的每一条命令**，并断言命令契约行为。
- 范围：
  - 依赖预先手动 setup（该测试套件不会安装 / 运行 / 配对应用）。
  - 针对所选 Android 节点逐命令验证 Gateway 网关 `node.invoke`。
- 必需的预先 setup：
  - Android 应用已连接并与 Gateway 网关完成配对。
  - 应用保持在前台。
  - 已为你期望通过的能力授予权限 / 捕获同意。
- 可选目标覆盖：
  - `OPENCLAW_ANDROID_NODE_ID` 或 `OPENCLAW_ANDROID_NODE_NAME`。
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`。
- 完整 Android 设置详情：[Android App](/zh-CN/platforms/android)

## 实时：模型冒烟（profile 密钥）

实时测试分为两层，以便隔离故障：

- “直接模型”告诉我们，该提供商 / 模型在给定密钥下是否至少能返回结果。
- “Gateway 网关冒烟”告诉我们，完整的 gateway + 智能体流水线是否对该模型正常工作（会话、历史、工具、沙箱策略等）。

### 第 1 层：直接模型补全（无 gateway）

- 测试：`src/agents/models.profiles.live.test.ts`
- 目标：
  - 枚举发现到的模型
  - 使用 `getApiKeyForModel` 选择你拥有凭证的模型
  - 为每个模型运行一个小型补全（并在需要时运行定向回归）
- 启用方式：
  - `pnpm test:live`（或在直接调用 Vitest 时设置 `OPENCLAW_LIVE_TEST=1`）
- 设置 `OPENCLAW_LIVE_MODELS=modern`（或 `all`，即 modern 的别名）后才会真正运行此测试套件；否则它会跳过，以便让 `pnpm test:live` 继续聚焦 Gateway 网关冒烟
- 选择模型的方法：
  - `OPENCLAW_LIVE_MODELS=modern`：运行现代允许列表（Opus / Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_MODELS=all`：是现代允许列表的别名
  - 或 `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."`（逗号分隔的允许列表）
  - modern / all 扫描默认带有精心筛选的高信号上限；设置 `OPENCLAW_LIVE_MAX_MODELS=0` 可执行完整的现代扫描，或设置一个正数来指定更小的上限。
- 选择提供商的方法：
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"`（逗号分隔的允许列表）
- 密钥来源：
  - 默认：profile 存储和环境变量回退
  - 设置 `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 可强制仅使用 **profile 存储**
- 为什么要有这一层：
  - 将“提供商 API 损坏 / 密钥无效”与“gateway 智能体流水线损坏”区分开
  - 容纳小而隔离的回归测试（例如：OpenAI Responses / Codex Responses 推理重放 + 工具调用流程）

### 第 2 层：Gateway 网关 + dev 智能体冒烟（也就是 “@openclaw” 实际在做的事）

- 测试：`src/gateway/gateway-models.profiles.live.test.ts`
- 目标：
  - 启动一个进程内 Gateway 网关
  - 创建 / 修补一个 `agent:dev:*` 会话（每次运行都可覆盖模型）
  - 遍历带密钥的模型并断言：
    - 有“有意义”的回复（不使用工具）
    - 一次真实的工具调用可用（read 探测）
    - 可选的额外工具探测（exec+read 探测）
    - OpenAI 回归路径（仅工具调用 → 后续跟进）保持正常
- 探测详情（便于你快速解释失败原因）：
  - `read` 探测：测试会在工作区写入一个 nonce 文件，并要求智能体 `read` 该文件并回显 nonce。
  - `exec+read` 探测：测试会要求智能体通过 `exec` 将 nonce 写入一个临时文件，然后再 `read` 读回。
  - 图像探测：测试会附加一个生成的 PNG（猫 + 随机代码），并期望模型返回 `cat <CODE>`。
  - 实现参考：`src/gateway/gateway-models.profiles.live.test.ts` 和 `src/gateway/live-image-probe.ts`。
- 启用方式：
  - `pnpm test:live`（或在直接调用 Vitest 时设置 `OPENCLAW_LIVE_TEST=1`）
- 选择模型的方法：
  - 默认：现代允许列表（Opus / Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` 是现代允许列表的别名
  - 或设置 `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`（或逗号列表）来缩小范围
  - modern / all Gateway 网关扫描默认带有精心筛选的高信号上限；设置 `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0` 可执行完整的现代扫描，或设置一个正数来指定更小的上限。
- 选择提供商的方法（避免“OpenRouter 全家桶”）：
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"`（逗号分隔的允许列表）
- 工具 + 图像探测在此实时测试中始终开启：
  - `read` 探测 + `exec+read` 探测（工具压力测试）
  - 当模型宣告支持图像输入时，会运行图像探测
  - 流程（高层概述）：
    - 测试会生成一个带有 “CAT” + 随机代码的小型 PNG（`src/gateway/live-image-probe.ts`）
    - 通过 `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]` 发送
    - Gateway 网关会将附件解析到 `images[]` 中（`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`）
    - 嵌入式智能体向模型转发一条多模态用户消息
    - 断言：回复中包含 `cat` + 该代码（允许轻微 OCR 错误）

提示：如果你想查看你的机器上可以测试什么（以及精确的 `provider/model` id），请运行：

```bash
openclaw models list
openclaw models list --json
```

## 实时：CLI 后端冒烟（Claude、Codex、Gemini 或其他本地 CLI）

- 测试：`src/gateway/gateway-cli-backend.live.test.ts`
- 目标：在不触碰默认配置的前提下，使用本地 CLI 后端验证 Gateway 网关 + 智能体流水线。
- 后端专属的默认冒烟配置位于所属扩展的 `cli-backend.ts` 定义中。
- 启用：
  - `pnpm test:live`（或在直接调用 Vitest 时设置 `OPENCLAW_LIVE_TEST=1`）
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- 默认值：
  - 默认提供商 / 模型：`claude-cli/claude-sonnet-4-6`
  - 命令 / 参数 / 图像行为来自所属 CLI 后端插件元数据。
- 覆盖方式（可选）：
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` 发送真实图像附件（路径会注入到提示词中）。
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` 通过 CLI 参数传递图像文件路径，而不是注入到提示词中。
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"`（或 `"list"`）用于控制在设置 `IMAGE_ARG` 时如何传递图像参数。
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` 发送第二轮并验证恢复流程。
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0` 禁用默认的 Claude Sonnet -> Opus 同会话连续性探测（当所选模型支持切换目标时，设置为 `1` 可强制开启）。

示例：

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

Docker 配方：

```bash
pnpm test:docker:live-cli-backend
```

单提供商 Docker 配方：

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:claude-subscription
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

说明：

- Docker 运行器位于 `scripts/test-live-cli-backend-docker.sh`。
- 它会在仓库 Docker 镜像内以非 root 的 `node` 用户运行实时 CLI 后端冒烟。
- 它会从所属扩展解析 CLI 冒烟元数据，然后将匹配的 Linux CLI 包（`@anthropic-ai/claude-code`、`@openai/codex` 或 `@google/gemini-cli`）安装到可缓存的可写前缀 `OPENCLAW_DOCKER_CLI_TOOLS_DIR` 中（默认：`~/.cache/openclaw/docker-cli-tools`）。
- `pnpm test:docker:live-cli-backend:claude-subscription` 需要可移植的 Claude Code 订阅 OAuth，可通过 `~/.claude/.credentials.json` 中的 `claudeAiOauth.subscriptionType` 或来自 `claude setup-token` 的 `CLAUDE_CODE_OAUTH_TOKEN` 提供。它会先在 Docker 中验证直接 `claude -p` 可用，然后在不保留 Anthropic API 密钥环境变量的情况下运行两轮 Gateway 网关 CLI 后端测试。这个订阅通道默认禁用 Claude MCP / 工具和图像探测，因为 Claude 当前会将第三方应用用量计入额外用量计费，而不是普通订阅方案额度。
- 实时 CLI 后端冒烟现在会对 Claude、Codex 和 Gemini 执行相同的端到端流程：文本轮次、图像分类轮次，然后通过 gateway CLI 验证 MCP `cron` 工具调用。
- Claude 的默认冒烟还会将会话从 Sonnet 修补到 Opus，并验证恢复后的会话仍记得之前的备注。

## 实时：ACP 绑定冒烟（`/acp spawn ... --bind here`）

- 测试：`src/gateway/gateway-acp-bind.live.test.ts`
- 目标：使用实时 ACP 智能体验证真实的 ACP 会话绑定流程：
  - 发送 `/acp spawn <agent> --bind here`
  - 原地绑定一个合成消息渠道会话
  - 在同一个会话上发送普通后续消息
  - 验证该后续消息落入已绑定 ACP 会话的转录中
- 启用：
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- 默认值：
  - Docker 中的 ACP 智能体：`claude,codex,gemini`
  - 直接 `pnpm test:live ...` 的 ACP 智能体：`claude`
  - 合成渠道：类似 Slack 私信的会话上下文
  - ACP 后端：`acpx`
- 覆盖方式：
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- 说明：
  - 此通道使用 gateway `chat.send` 接口，并配合仅管理员可用的合成 originating-route 字段，以便测试能附加消息渠道上下文，而无需假装真的向外部投递。
  - 当未设置 `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` 时，测试会对选定的 ACP harness 智能体使用内置 `acpx` 插件自带的智能体注册表。

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

单智能体 Docker 配方：

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

Docker 说明：

- Docker 运行器位于 `scripts/test-live-acp-bind-docker.sh`。
- 默认情况下，它会按顺序对所有受支持的实时 CLI 智能体运行 ACP 绑定冒烟：`claude`、`codex`，然后是 `gemini`。
- 使用 `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`、`OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` 或 `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` 可缩小矩阵范围。
- 它会加载 `~/.profile`，将匹配的 CLI 鉴权材料暂存到容器中，把 `acpx` 安装到可写 npm 前缀，然后在缺失时安装所请求的实时 CLI（`@anthropic-ai/claude-code`、`@openai/codex` 或 `@google/gemini-cli`）。
- 在 Docker 内部，运行器会设置 `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx`，从而让 `acpx` 将来自已加载 profile 的提供商环境变量传递给子 harness CLI。

## 实时：Codex app-server harness 冒烟

- 目标：通过常规 gateway
  `agent` 方法验证插件自有的 Codex harness：
  - 加载内置的 `codex` 插件
  - 选择 `OPENCLAW_AGENT_RUNTIME=codex`
  - 向 `codex/gpt-5.4` 发送第一条 gateway 智能体消息
  - 向同一个 OpenClaw 会话发送第二条消息，并验证 app-server
    线程可以恢复
  - 通过相同的 gateway 命令
    路径运行 `/codex status` 和 `/codex models`
- 测试：`src/gateway/gateway-codex-harness.live.test.ts`
- 启用：`OPENCLAW_LIVE_CODEX_HARNESS=1`
- 默认模型：`codex/gpt-5.4`
- 可选图像探测：`OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1`
- 可选 MCP / 工具探测：`OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1`
- 此冒烟测试会设置 `OPENCLAW_AGENT_HARNESS_FALLBACK=none`，这样损坏的 Codex
  harness 就不会因为悄悄回退到 PI 而误判通过。
- 鉴权：来自 shell / profile 的 `OPENAI_API_KEY`，以及可选复制的
  `~/.codex/auth.json` 和 `~/.codex/config.toml`

本地配方：

```bash
source ~/.profile
OPENCLAW_LIVE_CODEX_HARNESS=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MODEL=codex/gpt-5.4 \
  pnpm test:live -- src/gateway/gateway-codex-harness.live.test.ts
```

Docker 配方：

```bash
source ~/.profile
pnpm test:docker:live-codex-harness
```

Docker 说明：

- Docker 运行器位于 `scripts/test-live-codex-harness-docker.sh`。
- 它会加载挂载的 `~/.profile`，传递 `OPENAI_API_KEY`，在存在时复制 Codex CLI
  鉴权文件，将 `@openai/codex` 安装到可写挂载 npm 前缀中，暂存源码树，然后只运行 Codex-harness 实时测试。
- Docker 默认启用图像和 MCP / 工具探测。当你需要更窄的调试运行时，可设置
  `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=0` 或
  `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=0`。
- Docker 还会导出 `OPENCLAW_AGENT_HARNESS_FALLBACK=none`，与实时
  测试配置保持一致，因此 `openai-codex/*` 或 PI 回退都无法掩盖 Codex harness
  回归。

### 推荐的实时测试配方

范围窄、显式的允许列表速度最快，也最不容易波动：

- 单模型，直接模式（无 gateway）：
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- 单模型，Gateway 网关冒烟：
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 多个提供商上的工具调用：
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 聚焦 Google（Gemini API 密钥 + Antigravity）：
  - Gemini（API 密钥）：`OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity（OAuth）：`OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

说明：

- `google/...` 使用 Gemini API（API 密钥）。
- `google-antigravity/...` 使用 Antigravity OAuth bridge（Cloud Code Assist 风格的智能体端点）。
- `google-gemini-cli/...` 使用你机器上的本地 Gemini CLI（单独的鉴权方式 + 工具行为差异）。
- Gemini API 与 Gemini CLI：
  - API：OpenClaw 通过 HTTP 调用 Google 托管的 Gemini API（API 密钥 / profile 鉴权）；这通常就是大多数用户所说的 “Gemini”。
  - CLI：OpenClaw 会调用本地 `gemini` 二进制；它有自己的鉴权方式，并且在流式传输 / 工具支持 / 版本偏差方面可能表现不同。

## 实时：模型矩阵（我们覆盖什么）

并不存在固定的“CI 模型列表”（实时测试是按需启用的），但以下是**推荐**在具备相关密钥的开发机器上定期覆盖的模型。

### 现代冒烟集（工具调用 + 图像）

这是我们期望持续保持可用的“常用模型”运行集：

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

每个提供商家族至少选一个：

- OpenAI：`openai/gpt-5.4`（或 `openai/gpt-5.4-mini`）
- Anthropic：`anthropic/claude-opus-4-6`（或 `anthropic/claude-sonnet-4-6`）
- Google：`google/gemini-3-flash-preview`（或 `google/gemini-3.1-pro-preview`）
- Z.AI（GLM）：`zai/glm-4.7`
- MiniMax：`minimax/MiniMax-M2.7`

可选的额外覆盖（有更好，没有也可以）：

- xAI：`xai/grok-4`（或当前最新可用版本）
- Mistral：`mistral/`…（选择一个已启用且支持工具的模型）
- Cerebras：`cerebras/`…（如果你有权限）
- LM Studio：`lmstudio/`…（本地；工具调用取决于 API 模式）

### 视觉：图像发送（附件 → 多模态消息）

在 `OPENCLAW_LIVE_GATEWAY_MODELS` 中至少包含一个支持图像的模型（Claude / Gemini / OpenAI 的视觉变体等），以便覆盖图像探测。

### 聚合器 / 备用 Gateway 网关

如果你已启用相应密钥，也支持通过以下方式测试：

- OpenRouter：`openrouter/...`（数百个模型；使用 `openclaw models scan` 查找支持工具 + 图像的候选模型）
- OpenCode：Zen 使用 `opencode/...`，Go 使用 `opencode-go/...`（通过 `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY` 鉴权）

你也可以将更多提供商纳入实时矩阵（前提是你具备相应凭证 / 配置）：

- 内置：`openai`、`openai-codex`、`anthropic`、`google`、`google-vertex`、`google-antigravity`、`google-gemini-cli`、`zai`、`openrouter`、`opencode`、`opencode-go`、`xai`、`groq`、`cerebras`、`mistral`、`github-copilot`
- 通过 `models.providers`（自定义端点）：`minimax`（云端 / API），以及任何兼容 OpenAI / Anthropic 的代理（LM Studio、vLLM、LiteLLM 等）

提示：不要试图在文档中硬编码“所有模型”。权威列表应以你机器上 `discoverModels(...)` 的返回结果，以及当前可用密钥为准。

## 凭证（绝不要提交）

实时测试以与 CLI 相同的方式发现凭证。实际含义如下：

- 如果 CLI 可用，实时测试通常也应能找到相同的密钥。
- 如果某个实时测试提示“没有凭证”，就按你调试 `openclaw models list` / 模型选择问题的方式来调试。

- 按智能体划分的鉴权 profile：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（这就是实时测试中 “profile 密钥” 的含义）
- 配置：`~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）
- 旧版状态目录：`~/.openclaw/credentials/`（存在时会复制到暂存的实时测试 home 中，但它不是主 profile 密钥存储）
- 本地实时运行默认会将当前活动配置、按智能体划分的 `auth-profiles.json` 文件、旧版 `credentials/` 以及受支持的外部 CLI 鉴权目录复制到临时测试 home 中；暂存的实时 home 会跳过 `workspace/` 和 `sandboxes/`，并移除 `agents.*.workspace` / `agentDir` 路径覆盖，以确保探测不会落到你的真实主机工作区中。

如果你想依赖环境变量密钥（例如在 `~/.profile` 中导出的密钥），请在本地测试前运行 `source ~/.profile`，或者使用下面的 Docker 运行器（它们可以将 `~/.profile` 挂载进容器）。

## Deepgram 实时测试（音频转录）

- 测试：`src/media-understanding/providers/deepgram/audio.live.test.ts`
- 启用：`DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus 编码计划实时测试

- 测试：`src/agents/byteplus.live.test.ts`
- 启用：`BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- 可选模型覆盖：`BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI 工作流媒体实时测试

- 测试：`extensions/comfy/comfy.live.test.ts`
- 启用：`OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- 范围：
  - 验证内置 comfy 图像、视频和 `music_generate` 路径
  - 除非配置了 `models.providers.comfy.<capability>`，否则会跳过对应能力
  - 适用于你修改 comfy 工作流提交、轮询、下载或插件注册之后

## 图像生成实时测试

- 测试：`src/image-generation/runtime.live.test.ts`
- 命令：`pnpm test:live src/image-generation/runtime.live.test.ts`
- Harness：`pnpm test:live:media image`
- 范围：
  - 枚举每个已注册的图像生成提供商插件
  - 在探测前从你的登录 shell（`~/.profile`）加载缺失的提供商环境变量
  - 默认优先使用实时 / 环境变量 API 密钥，而不是已存储的鉴权 profile，因此 `auth-profiles.json` 中过期的测试密钥不会掩盖 shell 中真实可用的凭证
  - 跳过没有可用鉴权 / profile / 模型的提供商
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
- 可选鉴权行为：
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 强制使用 profile 存储鉴权，并忽略仅来自环境变量的覆盖

## 音乐生成实时测试

- 测试：`extensions/music-generation-providers.live.test.ts`
- 启用：`OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Harness：`pnpm test:live:media music`
- 范围：
  - 验证共享的内置音乐生成提供商路径
  - 当前覆盖 Google 和 MiniMax
  - 在探测前从你的登录 shell（`~/.profile`）加载提供商环境变量
  - 默认优先使用实时 / 环境变量 API 密钥，而不是已存储的鉴权 profile，因此 `auth-profiles.json` 中过期的测试密钥不会掩盖 shell 中真实可用的凭证
  - 跳过没有可用鉴权 / profile / 模型的提供商
  - 在可用时同时运行两种已声明的运行时模式：
    - `generate`：仅使用提示词输入
    - `edit`：当提供商声明了 `capabilities.edit.enabled` 时
  - 当前共享通道覆盖：
    - `google`：`generate`、`edit`
    - `minimax`：`generate`
    - `comfy`：单独的 Comfy 实时测试文件，不属于这次共享扫描
- 可选缩小范围：
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- 可选鉴权行为：
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 强制使用 profile 存储鉴权，并忽略仅来自环境变量的覆盖

## 视频生成实时测试

- 测试：`extensions/video-generation-providers.live.test.ts`
- 启用：`OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Harness：`pnpm test:live:media video`
- 范围：
  - 验证共享的内置视频生成提供商路径
  - 在探测前从你的登录 shell（`~/.profile`）加载提供商环境变量
  - 默认优先使用实时 / 环境变量 API 密钥，而不是已存储的鉴权 profile，因此 `auth-profiles.json` 中过期的测试密钥不会掩盖 shell 中真实可用的凭证
  - 跳过没有可用鉴权 / profile / 模型的提供商
  - 在可用时同时运行两种已声明的运行时模式：
    - `generate`：仅使用提示词输入
    - `imageToVideo`：当提供商声明了 `capabilities.imageToVideo.enabled`，且所选提供商 / 模型在共享扫描中接受基于 buffer 的本地图像输入时
    - `videoToVideo`：当提供商声明了 `capabilities.videoToVideo.enabled`，且所选提供商 / 模型在共享扫描中接受基于 buffer 的本地视频输入时
  - 当前在共享扫描中已声明但被跳过的 `imageToVideo` 提供商：
    - `vydra`，因为内置 `veo3` 仅支持文本，而内置 `kling` 需要远程图像 URL
  - Vydra 提供商专属覆盖：
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - 该文件会运行 `veo3` text-to-video，以及默认使用远程图像 URL 固定夹具的 `kling` 通道
  - 当前 `videoToVideo` 实时覆盖：
    - 仅 `runway`，且所选模型为 `runway/gen4_aleph` 时
  - 当前在共享扫描中已声明但被跳过的 `videoToVideo` 提供商：
    - `alibaba`、`qwen`、`xai`，因为这些路径目前需要远程 `http(s)` / MP4 参考 URL
    - `google`，因为当前共享 Gemini / Veo 通道使用本地 buffer 输入，而共享扫描不接受该路径
    - `openai`，因为当前共享通道无法保证组织专属的视频 inpaint / remix 访问权限
- 可选缩小范围：
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- 可选鉴权行为：
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 强制使用 profile 存储鉴权，并忽略仅来自环境变量的覆盖

## 媒体实时测试 harness

- 命令：`pnpm test:live:media`
- 目的：
  - 通过一个仓库原生入口运行共享的图像、音乐和视频实时测试套件
  - 自动从 `~/.profile` 加载缺失的提供商环境变量
  - 默认自动将每个测试套件缩小到当前具备可用鉴权的提供商
  - 复用 `scripts/test-live.mjs`，以保持心跳和静默模式行为一致
- 示例：
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Docker 运行器（可选的“在 Linux 中可用”检查）

这些 Docker 运行器分为两类：

- 实时模型运行器：`test:docker:live-models` 和 `test:docker:live-gateway` 只会在仓库 Docker 镜像内运行各自匹配的 profile 密钥实时测试文件（`src/agents/models.profiles.live.test.ts` 和 `src/gateway/gateway-models.profiles.live.test.ts`），挂载你的本地配置目录和工作区（如果挂载了 `~/.profile`，也会加载它）。对应的本地入口是 `test:live:models-profiles` 和 `test:live:gateway-profiles`。
- Docker 实时运行器默认使用更小的冒烟上限，以便完整的 Docker 扫描仍然可行：
  `test:docker:live-models` 默认设置 `OPENCLAW_LIVE_MAX_MODELS=12`，并且
  `test:docker:live-gateway` 默认设置 `OPENCLAW_LIVE_GATEWAY_SMOKE=1`、
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`、
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000` 和
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`。当你
  明确想要执行更大范围的完整扫描时，可覆盖这些环境变量。
- `test:docker:all` 会先通过 `test:docker:live-build` 构建一次实时 Docker 镜像，然后在两个实时 Docker 通道中复用它。
- 容器冒烟运行器：`test:docker:openwebui`、`test:docker:onboard`、`test:docker:gateway-network`、`test:docker:mcp-channels` 和 `test:docker:plugins` 会启动一个或多个真实容器，并验证更高层级的集成路径。

实时模型 Docker 运行器还会只绑定挂载所需的 CLI 鉴权 home（如果运行未缩小范围，则挂载全部受支持的鉴权 home），然后在运行前将它们复制到容器 home 中，以便外部 CLI OAuth 可以刷新令牌，而不会修改主机上的鉴权存储：

- 直接模型：`pnpm test:docker:live-models`（脚本：`scripts/test-live-models-docker.sh`）
- ACP 绑定冒烟：`pnpm test:docker:live-acp-bind`（脚本：`scripts/test-live-acp-bind-docker.sh`）
- CLI 后端冒烟：`pnpm test:docker:live-cli-backend`（脚本：`scripts/test-live-cli-backend-docker.sh`）
- Codex app-server harness 冒烟：`pnpm test:docker:live-codex-harness`（脚本：`scripts/test-live-codex-harness-docker.sh`）
- Gateway 网关 + dev 智能体：`pnpm test:docker:live-gateway`（脚本：`scripts/test-live-gateway-models-docker.sh`）
- Open WebUI 实时冒烟：`pnpm test:docker:openwebui`（脚本：`scripts/e2e/openwebui-docker.sh`）
- 新手引导向导（TTY，完整脚手架）：`pnpm test:docker:onboard`（脚本：`scripts/e2e/onboard-docker.sh`）
- Gateway 网关网络（两个容器，WS 鉴权 + 健康检查）：`pnpm test:docker:gateway-network`（脚本：`scripts/e2e/gateway-network-docker.sh`）
- MCP 渠道桥接（带种子数据的 Gateway 网关 + stdio bridge + 原始 Claude 通知帧冒烟）：`pnpm test:docker:mcp-channels`（脚本：`scripts/e2e/mcp-channels-docker.sh`）
- 插件（安装冒烟 + `/plugin` 别名 + Claude 内置包重启语义）：`pnpm test:docker:plugins`（脚本：`scripts/e2e/plugins-docker.sh`）

实时模型 Docker 运行器还会以只读方式绑定挂载当前 checkout，并将其暂存到容器内的临时工作目录中。这样可以让运行时镜像保持精简，同时仍能针对你当前本地的准确源码 / 配置运行 Vitest。暂存步骤会跳过大型本地专用缓存和应用构建输出，例如 `.pnpm-store`、`.worktrees`、`__openclaw_vitest__`，以及应用本地的 `.build` 或 Gradle 输出目录，因此 Docker 实时运行不会花费数分钟复制机器专属工件。
它们还会设置 `OPENCLAW_SKIP_CHANNELS=1`，以便 Gateway 网关实时探测不会在容器内启动真实的 Telegram / Discord / 等渠道工作进程。
`test:docker:live-models` 仍然运行 `pnpm test:live`，因此当你需要缩小或排除该 Docker 通道中的 Gateway 网关实时覆盖时，也请一并传入 `OPENCLAW_LIVE_GATEWAY_*`。
`test:docker:openwebui` 是更高层级的兼容性冒烟：它会启动一个启用了 OpenAI 兼容 HTTP 端点的 OpenClaw Gateway 网关容器，再针对该 Gateway 网关启动一个固定版本的 Open WebUI 容器，通过 Open WebUI 登录，验证 `/api/models` 暴露出 `openclaw/default`，然后通过 Open WebUI 的 `/api/chat/completions` 代理发送一次真实聊天请求。
首次运行可能会明显更慢，因为 Docker 可能需要拉取 Open WebUI 镜像，而 Open WebUI 也可能需要完成它自己的冷启动 setup。
这个通道需要可用的实时模型密钥，而 `OPENCLAW_PROFILE_FILE`
（默认是 `~/.profile`）是在 Docker 化运行中提供该密钥的主要方式。
成功运行会打印一个小型 JSON 载荷，例如 `{ "ok": true, "model":
"openclaw/default", ... }`。
`test:docker:mcp-channels` 是有意保持确定性的，不需要真实的 Telegram、Discord 或 iMessage 账号。它会启动一个带种子数据的 Gateway 网关容器，再启动第二个容器来运行 `openclaw mcp serve`，然后通过真实的 stdio MCP bridge 验证路由后的会话发现、转录读取、附件元数据、实时事件队列行为、出站发送路由，以及 Claude 风格的渠道 + 权限通知。通知检查会直接检查原始 stdio MCP 帧，因此该冒烟测试验证的是 bridge 实际发出的内容，而不只是某个特定客户端 SDK 恰好暴露出的内容。

手动 ACP 自然语言线程冒烟（非 CI）：

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- 请为回归 / 调试工作流保留这个脚本。它未来可能还会再次用于 ACP 线程路由验证，因此不要删除它。

常用环境变量：

- `OPENCLAW_CONFIG_DIR=...`（默认：`~/.openclaw`）挂载到 `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...`（默认：`~/.openclaw/workspace`）挂载到 `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...`（默认：`~/.profile`）挂载到 `/home/node/.profile` 并在运行测试前加载
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...`（默认：`~/.cache/openclaw/docker-cli-tools`）挂载到 `/home/node/.npm-global`，用于缓存 Docker 内部的 CLI 安装
- `$HOME` 下的外部 CLI 鉴权目录 / 文件会以只读方式挂载到 `/host-auth...` 下，然后在测试开始前复制到 `/home/node/...`
  - 默认目录：`.minimax`
  - 默认文件：`~/.codex/auth.json`、`~/.codex/config.toml`、`.claude.json`、`~/.claude/.credentials.json`、`~/.claude/settings.json`、`~/.claude/settings.local.json`
  - 缩小范围后的提供商运行只会挂载根据 `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS` 推断出的所需目录 / 文件
  - 可手动覆盖：`OPENCLAW_DOCKER_AUTH_DIRS=all`、`OPENCLAW_DOCKER_AUTH_DIRS=none`，或像 `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex` 这样的逗号列表
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` 用于缩小运行范围
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...` 用于在容器内过滤提供商
- `OPENCLAW_SKIP_DOCKER_BUILD=1` 用于复用已有的 `openclaw:local-live` 镜像，以便在无需重建时重新运行
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 用于确保凭证来自 profile 存储（而不是环境变量）
- `OPENCLAW_OPENWEBUI_MODEL=...` 用于选择 Gateway 网关为 Open WebUI 冒烟暴露的模型
- `OPENCLAW_OPENWEBUI_PROMPT=...` 用于覆盖 Open WebUI 冒烟使用的 nonce 检查提示词
- `OPENWEBUI_IMAGE=...` 用于覆盖固定的 Open WebUI 镜像标签

## 文档完整性检查

编辑文档后运行文档检查：`pnpm check:docs`。
当你还需要页内标题检查时，运行完整的 Mintlify 锚点验证：`pnpm docs:check-links:anchors`。

## 离线回归测试（CI 安全）

这些是在没有真实提供商的情况下进行的“真实流水线”回归测试：

- Gateway 网关工具调用（模拟 OpenAI，真实 Gateway 网关 + 智能体循环）：`src/gateway/gateway.test.ts`（用例：“runs a mock OpenAI tool call end-to-end via gateway agent loop”）
- Gateway 网关向导（WS `wizard.start` / `wizard.next`，强制写入配置 + 鉴权）：`src/gateway/gateway.test.ts`（用例：“runs wizard over ws and writes auth token config”）

## 智能体可靠性评估（Skills）

我们已经有一些 CI 安全的测试，它们表现得像“智能体可靠性评估”：

- 通过真实 Gateway 网关 + 智能体循环进行模拟工具调用（`src/gateway/gateway.test.ts`）。
- 验证会话接线和配置效果的端到端向导流程（`src/gateway/gateway.test.ts`）。

对于 Skills（见 [Skills](/zh-CN/tools/skills)）目前仍缺少的部分：

- **决策能力：** 当 Skills 被列在提示词中时，智能体是否会选择正确的 Skills（或避免选择无关 Skills）？
- **合规性：** 智能体是否会在使用前读取 `SKILL.md`，并遵循要求的步骤 / 参数？
- **工作流契约：** 多轮场景，用于断言工具顺序、会话历史延续，以及沙箱边界。

未来的评估应优先保持确定性：

- 一个使用模拟提供商的场景运行器，用于断言工具调用 + 顺序、Skills 文件读取以及会话接线。
- 一小套面向 Skills 的场景（使用 vs 避免、门控、提示词注入）。
- 仅在 CI 安全测试套件到位之后，才添加可选的实时评估（按需启用、环境变量门控）。

## 契约测试（插件和渠道形状）

契约测试用于验证每个已注册插件和渠道都符合其
接口契约。它们会遍历所有已发现的插件，并运行一组
关于结构和行为的断言。默认的 `pnpm test` 单元测试通道会有意
跳过这些共享接缝和冒烟文件；当你修改共享渠道或提供商表面时，
请显式运行契约测试命令。

### 命令

- 所有契约测试：`pnpm test:contracts`
- 仅渠道契约测试：`pnpm test:contracts:channels`
- 仅提供商契约测试：`pnpm test:contracts:plugins`

### 渠道契约测试

位于 `src/channels/plugins/contracts/*.contract.test.ts`：

- **plugin** - 基本插件结构（id、name、capabilities）
- **setup** - 设置向导契约
- **session-binding** - 会话绑定行为
- **outbound-payload** - 消息载荷结构
- **inbound** - 入站消息处理
- **actions** - 渠道动作处理器
- **threading** - 线程 ID 处理
- **directory** - 目录 / roster API
- **group-policy** - 群组策略强制执行

### 提供商状态契约测试

位于 `src/plugins/contracts/*.contract.test.ts`。

- **status** - 渠道状态探测
- **registry** - 插件注册表结构

### 提供商契约测试

位于 `src/plugins/contracts/*.contract.test.ts`：

- **auth** - 鉴权流程契约
- **auth-choice** - 鉴权选择 / 选取
- **catalog** - 模型目录 API
- **discovery** - 插件发现
- **loader** - 插件加载
- **runtime** - 提供商运行时
- **shape** - 插件结构 / 接口
- **wizard** - 设置向导

### 何时运行

- 修改 `plugin-sdk` 导出或子路径之后
- 添加或修改渠道插件或提供商插件之后
- 重构插件注册或发现逻辑之后

契约测试会在 CI 中运行，并且不需要真实 API 密钥。

## 添加回归测试（指南）

当你修复了在实时测试中发现的提供商 / 模型问题时：

- 如果可能，添加一个 CI 安全的回归测试（模拟 / stub 提供商，或捕获精确的请求结构转换）
- 如果它天然只能做实时测试（速率限制、鉴权策略），就让实时测试保持范围窄，并通过环境变量按需启用
- 优先定位到能够捕获该缺陷的最小层级：
  - 提供商请求转换 / 重放缺陷 → 直接模型测试
  - Gateway 网关会话 / 历史 / 工具流水线缺陷 → Gateway 网关实时冒烟或 CI 安全的 Gateway 网关模拟测试
- SecretRef 遍历护栏：
  - `src/secrets/exec-secret-ref-id-parity.test.ts` 会从注册表元数据（`listSecretTargetRegistryEntries()`）中为每个 SecretRef 类派生一个采样目标，然后断言遍历段 exec id 会被拒绝。
  - 如果你在 `src/secrets/target-registry-data.ts` 中添加了新的 `includeInPlan` SecretRef 目标家族，请更新该测试中的 `classifyTargetClass`。该测试会在遇到未分类的目标 id 时有意失败，以确保新类别不会被悄悄跳过。
