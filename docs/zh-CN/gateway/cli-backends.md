---
read_when:
    - 当 API 提供商失效时，你需要一个可靠的回退方案
    - 你正在运行 Codex CLI 或其他本地 AI CLI，并希望复用它们
    - 你想了解用于 CLI 后端工具访问的 MCP loopback 桥接机制
summary: CLI 后端：带可选 MCP 工具桥接的本地 AI CLI 回退机制
title: CLI 后端
x-i18n:
    generated_at: "2026-04-16T16:33:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 381273532a8622bc4628000a6fb999712b12af08faade2b5f2b7ac4cc7d23efe
    source_path: gateway/cli-backends.md
    workflow: 15
---

# CLI 后端（回退运行时）

当 API 提供商不可用、触发速率限制或暂时行为异常时，OpenClaw 可以运行**本地 AI CLI** 作为**纯文本回退**。这是一种有意保持保守的设计：

- **OpenClaw 工具不会被直接注入**，但设置了 `bundleMcp: true` 的后端可以通过 loopback MCP 桥接接收 Gateway 网关工具。
- 为支持的 CLI 提供 **JSONL 流式传输**。
- **支持会话**（因此后续轮次能够保持连贯）。
- 如果 CLI 接受图片路径，**图片可以被透传**。

它被设计为一个**安全兜底方案**，而不是主要路径。当你想要“不管怎样都能工作”的文本回复，而不依赖外部 API 时，可以使用它。

如果你想要具备 ACP 会话控制、后台任务、线程/会话绑定以及持久化外部编码会话的完整 harness 运行时，请改用
[ACP Agents](/zh-CN/tools/acp-agents)。CLI 后端不是 ACP。

## 面向初学者的快速开始

你可以**无需任何配置**使用 Codex CLI（内置的 OpenAI 插件会注册一个默认后端）：

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

如果你的 Gateway 网关运行在 launchd/systemd 下，且 PATH 很精简，只需添加命令路径：

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

就是这样。除了 CLI 本身之外，不需要额外的密钥或认证配置。

如果你在 Gateway 网关主机上将某个内置 CLI 后端用作**主消息提供商**，当你的配置在模型引用中或
`agents.defaults.cliBackends` 下显式引用该后端时，OpenClaw 现在会自动加载其所属的内置插件。

## 将它用作回退

将一个 CLI 后端添加到你的回退列表中，这样它只会在主模型失败时运行：

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

注意：

- 如果你使用 `agents.defaults.models`（允许列表），也必须把你的 CLI 后端模型包含进去。
- 如果主提供商失败（认证、速率限制、超时），OpenClaw 会接着尝试 CLI 后端。

## 配置概览

所有 CLI 后端都位于：

```
agents.defaults.cliBackends
```

每个条目都以**提供商 id** 作为键（例如 `codex-cli`、`my-cli`）。
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
          // 对于 Codex 风格的 CLI，也可以改为指向提示词文件：
          // systemPromptFileConfigArg: "-c",
          // systemPromptFileConfigKey: "model_instructions_file",
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
3. 使用会话 id 执行 CLI（如果支持），以便保持历史一致。
4. **解析输出**（JSON 或纯文本）并返回最终文本。
5. 按后端**持久化会话 id**，以便后续轮次复用相同的 CLI 会话。

<Note>
内置的 Anthropic `claude-cli` 后端现已再次受到支持。Anthropic 员工告诉我们，允许使用 OpenClaw 风格的 Claude CLI 方式，因此除非 Anthropic 发布新政策，否则 OpenClaw 会将这种 `claude -p` 用法视为该集成的被认可方式。
</Note>

内置的 OpenAI `codex-cli` 后端会通过 Codex 的 `model_instructions_file` 配置覆盖项（`-c
model_instructions_file="..."`）传递 OpenClaw 的系统提示词。Codex 不提供类似 Claude 的
`--append-system-prompt` 标志，因此 OpenClaw 会为每个新的 Codex CLI 会话将组装好的提示词写入一个临时文件。

内置的 Anthropic `claude-cli` 后端会通过两种方式接收 OpenClaw Skills 快照：追加到系统提示词中的紧凑型 OpenClaw Skills 目录，以及通过 `--plugin-dir` 传入的临时 Claude Code 插件。该插件只包含对该智能体/会话符合条件的 Skills，因此 Claude Code 的原生 Skill 解析器看到的就是与 OpenClaw 否则会在提示词中公布的同一组经过筛选的内容。Skill 环境变量/API 密钥覆盖仍然由 OpenClaw 应用于此次运行的子进程环境。

## 会话

- 如果 CLI 支持会话，请设置 `sessionArg`（例如 `--session-id`）或
  `sessionArgs`（占位符为 `{sessionId}`），用于当该 ID 需要插入多个标志时。
- 如果 CLI 使用带有不同标志的**恢复子命令**，请设置
  `resumeArgs`（恢复时替换 `args`），并可选设置 `resumeOutput`
  （用于非 JSON 恢复）。
- `sessionMode`：
  - `always`：始终发送会话 id（如果未存储则生成新的 UUID）。
  - `existing`：仅当之前已存储会话 id 时才发送。
  - `none`：从不发送会话 id。

序列化说明：

- `serialize: true` 会保持同一路径上的运行按顺序进行。
- 大多数 CLI 会在单个提供商路径上串行执行。
- 当后端认证状态发生变化时，包括重新登录、令牌轮换或认证配置文件凭证变化，OpenClaw 会丢弃已存储的 CLI 会话复用。

## 图片（透传）

如果你的 CLI 接受图片路径，请设置 `imageArg`：

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw 会将 base64 图片写入临时文件。如果设置了 `imageArg`，这些路径会作为 CLI 参数传递。如果缺少 `imageArg`，OpenClaw 会将文件路径附加到提示词中（路径注入），这对于那些能从普通路径自动加载本地文件的 CLI 来说已经足够。

## 输入 / 输出

- `output: "json"`（默认）会尝试解析 JSON 并提取文本 + 会话 id。
- 对于 Gemini CLI JSON 输出，当 `usage` 缺失或为空时，OpenClaw 会从 `response` 读取回复文本，并从
  `stats` 读取用量。
- `output: "jsonl"` 会解析 JSONL 流（例如 Codex CLI `--json`），并在存在时提取最终智能体消息以及会话标识符。
- `output: "text"` 会将 stdout 视为最终回复。

输入模式：

- `input: "arg"`（默认）会将提示词作为最后一个 CLI 参数传递。
- `input: "stdin"` 会通过 stdin 发送提示词。
- 如果提示词很长且设置了 `maxPromptArgChars`，则会使用 stdin。

## 默认值（插件拥有）

内置的 OpenAI 插件也为 `codex-cli` 注册了一个默认值：

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","-c","sandbox_mode=\"workspace-write\"","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

内置的 Google 插件也为 `google-gemini-cli` 注册了一个默认值：

- `command: "gemini"`
- `args: ["--output-format", "json", "--prompt", "{prompt}"]`
- `resumeArgs: ["--resume", "{sessionId}", "--output-format", "json", "--prompt", "{prompt}"]`
- `imageArg: "@"`
- `imagePathScope: "workspace"`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

前提条件：本地 Gemini CLI 必须已安装，并且可以在
`PATH` 中作为 `gemini` 使用（`brew install gemini-cli` 或
`npm install -g @google/gemini-cli`）。

Gemini CLI JSON 说明：

- 回复文本从 JSON 的 `response` 字段读取。
- 当 `usage` 不存在或为空时，用量会回退到 `stats`。
- `stats.cached` 会被标准化为 OpenClaw 的 `cacheRead`。
- 如果 `stats.input` 缺失，OpenClaw 会根据
  `stats.input_tokens - stats.cached` 推导输入 token 数。

仅在需要时覆盖（常见情况：使用绝对 `command` 路径）。

## 插件拥有的默认值

CLI 后端默认值现在是插件表面的一部分：

- 插件使用 `api.registerCliBackend(...)` 注册它们。
- 后端 `id` 会成为模型引用中的提供商前缀。
- `agents.defaults.cliBackends.<id>` 中的用户配置仍会覆盖插件默认值。
- 后端特定的配置清理由插件通过可选的
  `normalizeConfig` hook 继续负责。

需要微小提示词/消息兼容性 shim 的插件，可以声明双向文本转换，而无需替换提供商或 CLI 后端：

```typescript
api.registerTextTransforms({
  input: [
    { from: /red basket/g, to: "blue basket" },
    { from: /paper ticket/g, to: "digital ticket" },
    { from: /left shelf/g, to: "right shelf" },
  ],
  output: [
    { from: /blue basket/g, to: "red basket" },
    { from: /digital ticket/g, to: "paper ticket" },
    { from: /right shelf/g, to: "left shelf" },
  ],
});
```

`input` 会重写传递给 CLI 的系统提示词和用户提示词。`output`
会在 OpenClaw 处理其自身控制标记和渠道投递之前，重写流式传输的助手增量内容以及解析后的最终文本。

对于输出与 Claude Code stream-json 兼容的 JSONL 的 CLI，请在该后端配置中设置
`jsonlDialect: "claude-stream-json"`。

## Bundle MCP 覆盖层

CLI 后端**不会**直接接收 OpenClaw 工具调用，但后端可以通过设置
`bundleMcp: true` 选择接收一个生成的 MCP 配置覆盖层。

当前的内置行为：

- `claude-cli`：生成严格的 MCP 配置文件
- `codex-cli`：为 `mcp_servers` 提供内联配置覆盖
- `google-gemini-cli`：生成 Gemini 系统设置文件

启用 bundle MCP 后，OpenClaw 会：

- 启动一个 loopback HTTP MCP 服务器，向 CLI 进程暴露 Gateway 网关工具
- 使用每会话令牌（`OPENCLAW_MCP_TOKEN`）对桥接进行认证
- 将工具访问范围限定在当前会话、账户和渠道上下文中
- 为当前工作区加载已启用的 bundle-MCP 服务器
- 将它们与任何现有的后端 MCP 配置/设置结构合并
- 使用所属扩展中后端拥有的集成模式重写启动配置

如果没有启用任何 MCP 服务器，当后端选择启用 bundle MCP 时，OpenClaw 仍会注入严格配置，以便后台运行保持隔离。

## 限制

- **没有直接的 OpenClaw 工具调用。** OpenClaw 不会将工具调用直接注入到
  CLI 后端协议中。后端只有在选择启用
  `bundleMcp: true` 时才会看到 Gateway 网关工具。
- **流式传输依赖具体后端。** 某些后端会流式输出 JSONL；其他后端则会缓冲直到退出。
- **结构化输出** 取决于 CLI 的 JSON 格式。
- **Codex CLI 会话** 通过文本输出恢复（不是 JSONL），其结构化程度低于初始的 `--json` 运行。不过 OpenClaw 会话本身仍然可以正常工作。

## 故障排除

- **找不到 CLI**：将 `command` 设置为完整路径。
- **模型名称错误**：使用 `modelAliases` 将 `provider/model` 映射到 CLI 模型。
- **没有会话连续性**：确保已设置 `sessionArg`，并且 `sessionMode` 不是
  `none`（Codex CLI 当前无法使用 JSON 输出进行恢复）。
- **图片被忽略**：设置 `imageArg`（并确认 CLI 支持文件路径）。
