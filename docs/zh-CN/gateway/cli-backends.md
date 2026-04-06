---
read_when:
    - 当 API 提供商失败时，你想要一个可靠的回退方案
    - 你正在运行 Codex CLI 或其他本地 AI CLI，并且想要复用它们
    - 你想了解用于 CLI 后端工具访问的 MCP loopback 桥接
summary: CLI 后端：带可选 MCP 工具桥接的本地 AI CLI 回退
title: CLI 后端
x-i18n:
    generated_at: "2026-04-06T15:27:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: f061357f420455ad6ffaabe7fe28f1fb1b1769d73a4eb2e6f45c6eb3c2e36667
    source_path: gateway/cli-backends.md
    workflow: 15
---

# CLI 后端（回退运行时）

当 API 提供商不可用、受到速率限制或暂时行为异常时，OpenClaw 可以运行**本地 AI CLI** 作为**纯文本回退**。这是有意采取的保守设计：

- **不会直接注入 OpenClaw 工具**，但设置了 `bundleMcp: true` 的后端可以通过 loopback MCP 桥接接收 Gateway 网关工具。
- 支持 **JSONL 流式传输**，适用于支持它的 CLI。
- 支持**会话**（因此后续轮次可以保持连贯）。
- 如果 CLI 接受图片路径，**图片可以透传**。

它的设计目标是作为**安全兜底方案**，而不是主要路径。当你希望在不依赖外部 API 的情况下获得“始终可用”的文本响应时，可以使用它。

如果你想要一个具备 ACP 会话控制、后台任务、线程/对话绑定以及持久化外部编码会话的完整 harness 运行时，请改用 [ACP Agents](/zh-CN/tools/acp-agents)。CLI 后端不是 ACP。

## 面向初学者的快速开始

你可以在**无需任何配置**的情况下使用 Codex CLI（内置 OpenAI 插件会注册一个默认后端）：

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

如果你的 Gateway 网关运行在 launchd/systemd 下，且 PATH 非常精简，只需添加命令路径：

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
      },
    },
  },
}
```

就是这样。除了 CLI 本身之外，不需要密钥，也不需要额外的身份验证配置。

如果你在 Gateway 网关主机上将内置 CLI 后端用作**主要消息提供商**，现在只要你的配置在模型引用中或在 `agents.defaults.cliBackends` 下显式引用了该后端，OpenClaw 就会自动加载对应的内置插件。

## 将其用作回退

把一个 CLI 后端添加到你的回退列表中，这样它只会在主要模型失败时运行：

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["codex-cli/gpt-5.4"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "codex-cli/gpt-5.4": {},
      },
    },
  },
}
```

说明：

- 如果你使用 `agents.defaults.models`（允许列表），你也必须把 CLI 后端模型包含进去。
- 如果主要提供商失败（身份验证、速率限制、超时），OpenClaw 会接着尝试 CLI 后端。

## 配置概览

所有 CLI 后端都位于：

```
agents.defaults.cliBackends
```

每个条目都以一个**提供商 id** 为键（例如 `codex-cli`、`my-cli`）。
该提供商 id 会成为你的模型引用左侧部分：

```
<provider>/<model>
```

### 配置示例

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-6": "opus",
            "claude-sonnet-4-6": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## 工作原理

1. 根据提供商前缀（`codex-cli/...`）**选择一个后端**。
2. 使用相同的 OpenClaw 提示词和工作区上下文**构建系统提示词**。
3. 如果支持，则带着会话 id **执行 CLI**，以便保持历史一致。
4. **解析输出**（JSON 或纯文本）并返回最终文本。
5. 按后端**持久化会话 id**，这样后续轮次就会复用同一个 CLI 会话。

<Note>
内置 Anthropic `claude-cli` 后端现已再次受支持。Anthropic 工作人员告诉我们，OpenClaw 风格的 Claude CLI 用法现在再次被允许，因此除非 Anthropic 发布新政策，否则 OpenClaw 会将 `claude -p` 用法视为此集成的许可方式。
</Note>

## 会话

- 如果 CLI 支持会话，请设置 `sessionArg`（例如 `--session-id`）或
  `sessionArgs`（占位符 `{sessionId}`），用于在需要将该 ID 插入多个标志时使用。
- 如果 CLI 使用带有不同标志的**恢复子命令**，请设置
  `resumeArgs`（恢复时替换 `args`），并可选设置 `resumeOutput`
  （用于非 JSON 恢复）。
- `sessionMode`：
  - `always`：始终发送会话 id（如果没有已存储值，则生成新的 UUID）。
  - `existing`：仅在之前存储过会话 id 时发送。
  - `none`：从不发送会话 id。

序列化说明：

- `serialize: true` 会保持同一通道运行按顺序执行。
- 大多数 CLI 会在单个提供商通道上串行化。
- 当后端身份验证状态发生变化时，包括重新登录、令牌轮换或身份验证配置文件凭据变更，OpenClaw 会丢弃已存储的 CLI 会话复用。

## 图片（透传）

如果你的 CLI 接受图片路径，请设置 `imageArg`：

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw 会将 base64 图片写入临时文件。如果设置了 `imageArg`，这些路径会作为 CLI 参数传入。如果缺少 `imageArg`，OpenClaw 会把文件路径附加到提示词中（路径注入），这对于会从普通路径自动加载本地文件的 CLI 已经足够。

## 输入 / 输出

- `output: "json"`（默认）会尝试解析 JSON 并提取文本 + 会话 id。
- 对于 Gemini CLI JSON 输出，当 `usage` 缺失或为空时，OpenClaw 会从 `response` 读取回复文本，并从 `stats` 读取用量。
- `output: "jsonl"` 会解析 JSONL 流（例如 Codex CLI `--json`），并提取最终智能体消息以及存在时的会话标识符。
- `output: "text"` 会将 stdout 视为最终响应。

输入模式：

- `input: "arg"`（默认）会将提示词作为最后一个 CLI 参数传递。
- `input: "stdin"` 会通过 stdin 发送提示词。
- 如果提示词非常长且设置了 `maxPromptArgChars`，则会改用 stdin。

## 默认值（插件拥有）

内置 OpenAI 插件还为 `codex-cli` 注册了一个默认值：

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

内置 Google 插件也为 `google-gemini-cli` 注册了一个默认值：

- `command: "gemini"`
- `args: ["--prompt", "--output-format", "json"]`
- `resumeArgs: ["--resume", "{sessionId}", "--prompt", "--output-format", "json"]`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

前提条件：本地 Gemini CLI 必须已安装，并且能通过 `PATH` 中的
`gemini` 使用（`brew install gemini-cli` 或
`npm install -g @google/gemini-cli`）。

Gemini CLI JSON 说明：

- 回复文本从 JSON 的 `response` 字段读取。
- 当 `usage` 不存在或为空时，用量会回退到 `stats`。
- `stats.cached` 会被标准化为 OpenClaw `cacheRead`。
- 如果 `stats.input` 缺失，OpenClaw 会根据
  `stats.input_tokens - stats.cached` 推导输入 token 数。

仅在需要时覆盖（常见情况：使用绝对 `command` 路径）。

## 插件拥有的默认值

CLI 后端默认值现在属于插件表面的一部分：

- 插件通过 `api.registerCliBackend(...)` 注册它们。
- 后端的 `id` 会成为模型引用中的提供商前缀。
- `agents.defaults.cliBackends.<id>` 中的用户配置仍然会覆盖插件默认值。
- 后端特定的配置清理由插件通过可选的
  `normalizeConfig` hook 继续拥有。

## Bundle MCP 覆盖层

CLI 后端**不会**直接接收 OpenClaw 工具调用，但后端可以通过设置
`bundleMcp: true` 选择加入自动生成的 MCP 配置覆盖层。

当前内置行为：

- `codex-cli`：无 bundle MCP 覆盖层
- `google-gemini-cli`：无 bundle MCP 覆盖层

启用 bundle MCP 后，OpenClaw 会：

- 启动一个 loopback HTTP MCP 服务器，将 Gateway 网关工具暴露给 CLI 进程
- 使用每会话令牌（`OPENCLAW_MCP_TOKEN`）对桥接进行身份验证
- 将工具访问范围限定到当前会话、账户和渠道上下文
- 为当前工作区加载已启用的 bundle-MCP 服务器
- 将它们与任何现有后端 `--mcp-config` 合并
- 重写 CLI 参数以传递 `--strict-mcp-config --mcp-config <generated-file>`

如果没有启用任何 MCP 服务器，那么当后端选择加入 bundle MCP 时，OpenClaw 仍会注入严格配置，以便后台运行保持隔离。

## 限制

- **没有直接的 OpenClaw 工具调用。** OpenClaw 不会把工具调用注入到
  CLI 后端协议中。只有当后端选择加入 `bundleMcp: true` 时，它们才能看到 Gateway 网关工具。
- **流式传输取决于后端。** 有些后端会流式输出 JSONL；其他后端则会一直缓冲到退出。
- **结构化输出** 取决于 CLI 的 JSON 格式。
- **Codex CLI 会话** 通过文本输出恢复（没有 JSONL），其结构性弱于初始的 `--json` 运行。不过 OpenClaw 会话仍然可以正常工作。

## 故障排除

- **找不到 CLI**：将 `command` 设置为完整路径。
- **模型名称错误**：使用 `modelAliases` 将 `provider/model` 映射为 CLI 模型。
- **没有会话连续性**：确保已设置 `sessionArg`，并且 `sessionMode` 不是
  `none`（Codex CLI 目前无法使用 JSON 输出恢复）。
- **图片被忽略**：设置 `imageArg`（并确认 CLI 支持文件路径）。
