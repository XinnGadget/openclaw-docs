---
read_when:
    - 你需要了解为什么某个 CI 作业会运行或不会运行
    - 你正在调试失败的 GitHub Actions 检查
summary: CI 作业图、作用域门禁，以及本地命令等效项
title: CI 流水线
x-i18n:
    generated_at: "2026-04-10T23:44:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: ca7e355b7f73bfe8ea8c6971e78164b8b2e68cbb27966964955e267fed89fce6
    source_path: ci.md
    workflow: 15
---

# CI 流水线

CI 会在每次推送到 `main` 以及每个拉取请求时运行。它使用智能作用域划分，在仅有不相关区域发生变更时跳过开销较大的作业。

## 作业概览

| 作业                      | 目的                                                                                 | 运行时机                            |
| ------------------------ | ------------------------------------------------------------------------------------ | ----------------------------------- |
| `preflight`              | 检测仅文档变更、变更作用域、变更的扩展，并构建 CI 清单                               | 在所有非草稿推送和 PR 上始终运行    |
| `security-fast`          | 私钥检测、通过 `zizmor` 进行工作流审计、生产依赖审计                                 | 在所有非草稿推送和 PR 上始终运行    |
| `build-artifacts`        | 构建 `dist/` 和 Control UI 一次，并上传可供下游作业复用的制品                        | 与 Node 相关的变更                  |
| `checks-fast-core`       | 快速 Linux 正确性通道，例如 bundled/plugin-contract/protocol 检查                    | 与 Node 相关的变更                  |
| `checks-node-extensions` | 跨整个扩展套件的完整 bundled-plugin 测试分片                                         | 与 Node 相关的变更                  |
| `checks-node-core-test`  | 核心 Node 测试分片，不包括渠道、bundled、contract 和扩展通道                         | 与 Node 相关的变更                  |
| `extension-fast`         | 仅针对已变更 bundled 插件的聚焦测试                                                  | 检测到扩展变更时                    |
| `check`                  | CI 中的主要本地门禁：`pnpm check` 加 `pnpm build:strict-smoke`                       | 与 Node 相关的变更                  |
| `check-additional`       | 架构、边界、导入循环防护，以及 Gateway 网关 watch 回归测试 harness                   | 与 Node 相关的变更                  |
| `build-smoke`            | 已构建 CLI 的冒烟测试和启动内存冒烟测试                                              | 与 Node 相关的变更                  |
| `checks`                 | 剩余的 Linux Node 通道：渠道测试以及仅在推送时运行的 Node 22 兼容性检查              | 与 Node 相关的变更                  |
| `check-docs`             | 文档格式、lint 和损坏链接检查                                                        | 文档发生变更时                      |
| `skills-python`          | 面向 Python 支持的 Skills 的 Ruff + pytest                                           | 与 Python Skills 相关的变更         |
| `checks-windows`         | Windows 特定测试通道                                                                 | 与 Windows 相关的变更               |
| `macos-node`             | 使用共享构建制品的 macOS TypeScript 测试通道                                         | 与 macOS 相关的变更                 |
| `macos-swift`            | macOS 应用的 Swift lint、构建和测试                                                  | 与 macOS 相关的变更                 |
| `android`                | Android 构建和测试矩阵                                                               | 与 Android 相关的变更               |

## 快速失败顺序

作业的排列顺序经过设计，以便让廉价检查先失败，避免昂贵作业过早运行：

1. `preflight` 决定哪些通道实际存在。`docs-scope` 和 `changed-scope` 逻辑是这个作业内部的步骤，不是独立作业。
2. `security-fast`、`check`、`check-additional`、`check-docs` 和 `skills-python` 会快速失败，而不会等待更重的制品和平台矩阵作业。
3. `build-artifacts` 会与快速 Linux 通道并行运行，这样下游使用方一旦共享构建准备好就可以立即开始。
4. 更重的平台和运行时通道会在此之后展开：`checks-fast-core`、`checks-node-extensions`、`checks-node-core-test`、`extension-fast`、`checks`、`checks-windows`、`macos-node`、`macos-swift` 和 `android`。

作用域逻辑位于 `scripts/ci-changed-scope.mjs`，并由 `src/scripts/ci-changed-scope.test.ts` 中的单元测试覆盖。
单独的 `install-smoke` 工作流会通过它自己的 `preflight` 作业复用同一个作用域脚本。它会基于更窄的 changed-smoke 信号计算 `run_install_smoke`，因此 Docker/安装冒烟测试只会在与安装、打包和容器相关的变更时运行。

在推送时，`checks` 矩阵会增加仅推送时运行的 `compat-node22` 通道。在拉取请求中，该通道会被跳过，矩阵会继续聚焦于常规测试/渠道通道。

## 运行器

| 运行器                           | 作业                                                                                                 |
| -------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `blacksmith-16vcpu-ubuntu-2404`  | `preflight`、`security-fast`、`build-artifacts`、Linux 检查、文档检查、Python Skills、`android`     |
| `blacksmith-32vcpu-windows-2025` | `checks-windows`                                                                                     |
| `macos-latest`                   | `macos-node`、`macos-swift`                                                                          |

## 本地等效项

```bash
pnpm check          # 类型检查 + lint + 格式检查
pnpm build:strict-smoke
pnpm check:import-cycles
pnpm test:gateway:watch-regression
pnpm test           # vitest 测试
pnpm test:channels
pnpm check:docs     # 文档格式 + lint + 损坏链接检查
pnpm build          # 当 CI 的 artifact/build-smoke 通道相关时，构建 dist
```
