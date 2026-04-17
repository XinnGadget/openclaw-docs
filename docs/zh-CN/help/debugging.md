---
read_when:
    - 你需要检查原始模型输出，以排查推理泄漏
    - 你想在迭代时以监视模式运行 Gateway 网关
    - 你需要一个可重复的调试工作流
summary: 调试工具：监视模式、原始模型流，以及推理泄漏追踪
title: 调试
x-i18n:
    generated_at: "2026-04-12T18:22:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: bc31ce9b41e92a14c4309f32df569b7050b18024f83280930e53714d3bfcd5cc
    source_path: help/debugging.md
    workflow: 15
---

# 调试

本页介绍用于流式输出的调试辅助工具，尤其适用于提供商将推理内容混入普通文本时的情况。

## 运行时调试覆盖

在聊天中使用 `/debug` 来设置**仅运行时**的配置覆盖（存储在内存中，而不是磁盘）。
`/debug` 默认禁用；可通过 `commands.debug: true` 启用。
当你需要切换一些较少使用的设置，而不想编辑 `openclaw.json` 时，这会很方便。

示例：

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset` 会清除所有覆盖，并恢复为磁盘上的配置。

## 会话追踪输出

当你想在单个会话中查看插件拥有的追踪/调试行，而不启用完整详细模式时，请使用 `/trace`。

示例：

```text
/trace
/trace on
/trace off
```

将 `/trace` 用于插件诊断，例如 Active Memory 调试摘要。
对于常规的详细状态/工具输出，继续使用 `/verbose`；对于仅运行时的配置覆盖，继续使用 `/debug`。

## Gateway 网关监视模式

为了快速迭代，请在文件监视器下运行 Gateway 网关：

```bash
pnpm gateway:watch
```

这对应于：

```bash
node scripts/watch-node.mjs gateway --force
```

监视器会在 `src/` 下与构建相关的文件、扩展源码文件、扩展的 `package.json` 和 `openclaw.plugin.json` 元数据、`tsconfig.json`、`package.json` 以及 `tsdown.config.ts` 发生变更时重启。
扩展元数据变更会在不强制执行 `tsdown` 重建的情况下重启 Gateway 网关；源码和配置变更仍会先重建 `dist`。

在 `gateway:watch` 后添加任何 Gateway 网关 CLI 标志，它们都会在每次重启时透传。
现在，对于同一仓库/标志组合重复运行相同的监视命令时，会替换旧的监视器，而不是留下重复的监视器父进程。

## 开发配置文件 + 开发 Gateway 网关（`--dev`）

使用开发配置文件来隔离状态，并为调试启动一个安全、可丢弃的环境。这里有**两个** `--dev` 标志：

- **全局 `--dev`（配置文件）：** 将状态隔离到 `~/.openclaw-dev` 下，并将 Gateway 网关端口默认为 `19001`（派生端口也会随之变化）。
- **`gateway --dev`：** 告诉 Gateway 网关在缺失时自动创建默认配置 + 工作区（并跳过 `BOOTSTRAP.md`）。

推荐流程（开发配置文件 + 开发引导）：

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

如果你还没有全局安装，请通过 `pnpm openclaw ...` 运行 CLI。

具体作用如下：

1. **配置文件隔离**（全局 `--dev`）
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001`（browser/canvas 端口也会相应变化）

2. **开发引导**（`gateway --dev`）
   - 如果缺失，则写入最小配置（`gateway.mode=local`，绑定到 loopback）。
   - 将 `agent.workspace` 设置为开发工作区。
   - 设置 `agent.skipBootstrap=true`（不使用 `BOOTSTRAP.md`）。
   - 如果缺失，则为工作区填充这些文件：
     `AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`。
   - 默认身份：**C3‑PO**（协议机器人）。
   - 在开发模式下跳过渠道提供商（`OPENCLAW_SKIP_CHANNELS=1`）。

重置流程（全新开始）：

```bash
pnpm gateway:dev:reset
```

注意：`--dev` 是一个**全局**配置文件标志，某些运行器会吞掉它。
如果你需要明确写出来，请使用环境变量形式：

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset` 会清除配置、凭证、会话和开发工作区（使用 `trash`，而不是 `rm`），然后重新创建默认的开发环境。

提示：如果一个非开发 Gateway 网关已经在运行（launchd/systemd），请先停止它：

```bash
openclaw gateway stop
```

## 原始流日志（OpenClaw）

OpenClaw 可以在任何过滤/格式化之前记录**原始 assistant 流**。
这是查看推理内容是否作为纯文本增量到达（或作为单独的 thinking 块到达）的最佳方式。

通过 CLI 启用：

```bash
pnpm gateway:watch --raw-stream
```

可选路径覆盖：

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

等效环境变量：

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

默认文件：

`~/.openclaw/logs/raw-stream.jsonl`

## 原始分块日志（pi-mono）

要在解析为块之前捕获**原始 OpenAI-compat 分块**，pi-mono 提供了一个单独的日志记录器：

```bash
PI_RAW_STREAM=1
```

可选路径：

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

默认文件：

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> 注意：这仅由使用 pi-mono 的
> `openai-completions` 提供商的进程输出。

## 安全注意事项

- 原始流日志可能包含完整提示词、工具输出和用户数据。
- 请将日志保留在本地，并在调试后删除。
- 如果你要共享日志，请先清理其中的密钥和个人身份信息。
