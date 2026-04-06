---
read_when:
    - 你想在 OpenClaw 中使用 Anthropic 模型
summary: 在 OpenClaw 中通过 API 密钥或 Claude CLI 使用 Anthropic Claude
title: Anthropic
x-i18n:
    generated_at: "2026-04-06T15:31:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 423928fd36c66729985208d4d3f53aff1f94f63b908df85072988bdc41d5cf46
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic（Claude）

Anthropic 构建了 **Claude** 模型家族，并通过 API 和
Claude CLI 提供访问。在 OpenClaw 中，Anthropic API 密钥和 Claude CLI 复用都受支持。如果现有的旧版 Anthropic 令牌配置文件已经配置好，运行时仍会继续使用它们。

<Warning>
Anthropic 员工告诉我们，OpenClaw 风格的 Claude CLI 用法再次被允许，因此只要 Anthropic 没有发布新的政策，OpenClaw 就会将 Claude CLI 复用和 `claude -p` 用法视为此集成下被认可的方式。

对于长期运行的 Gateway 网关主机，Anthropic API 密钥仍然是最清晰、最可预测的生产路径。如果你已经在主机上使用 Claude CLI，OpenClaw 可以直接复用该登录状态。

Anthropic 当前公开文档：

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)

- [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Using Claude Code with your Team or Enterprise plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

如果你想要最清晰的计费路径，请改用 Anthropic API 密钥。
OpenClaw 也支持其他订阅式选项，包括 [OpenAI
Codex](/zh-CN/providers/openai)、[Qwen Cloud Coding Plan](/zh-CN/providers/qwen)、
[MiniMax Coding Plan](/zh-CN/providers/minimax) 和 [Z.AI / GLM Coding
Plan](/zh-CN/providers/glm)。
</Warning>

## 选项 A：Anthropic API 密钥

**最适合：** 标准 API 访问和按使用量计费。
请在 Anthropic Console 中创建你的 API 密钥。

### CLI 设置

```bash
openclaw onboard
# choose: Anthropic API key

# or non-interactive
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### Anthropic 配置片段

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Thinking 默认值（Claude 4.6）

- 当未设置显式 thinking 级别时，Anthropic Claude 4.6 模型在 OpenClaw 中默认使用 `adaptive` thinking。
- 你可以按消息覆盖（`/think:<level>`），或在模型参数中设置：
  `agents.defaults.models["anthropic/<model>"].params.thinking`。
- 相关 Anthropic 文档：
  - [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## 快速模式（Anthropic API）

OpenClaw 的共享 `/fast` 开关也支持直接公共 Anthropic 流量，包括发送到 `api.anthropic.com` 的 API 密钥和 OAuth 认证请求。

- `/fast on` 映射为 `service_tier: "auto"`
- `/fast off` 映射为 `service_tier: "standard_only"`
- 配置默认值：

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-sonnet-4-6": {
          params: { fastMode: true },
        },
      },
    },
  },
}
```

重要限制：

- OpenClaw 仅对直接发往 `api.anthropic.com` 的请求注入 Anthropic service tier。如果你通过代理或 Gateway 网关路由 `anthropic/*`，`/fast` 不会改动 `service_tier`。
- 如果同时设置了显式 Anthropic `serviceTier` 或 `service_tier` 模型参数，则它们会覆盖 `/fast` 默认值。
- Anthropic 会在响应中的 `usage.service_tier` 下报告实际生效的层级。对于没有 Priority Tier 容量的账户，`service_tier: "auto"` 仍可能解析为 `standard`。

## 提示缓存（Anthropic API）

OpenClaw 支持 Anthropic 的提示缓存功能。这是**仅限 API**的；旧版 Anthropic 令牌凭证不会遵循缓存设置。

### 配置

在模型配置中使用 `cacheRetention` 参数：

| 值 | 缓存时长 | 说明 |
| ------- | -------------- | ------------------------ |
| `none`  | 不缓存 | 禁用提示缓存 |
| `short` | 5 分钟 | API 密钥凭证的默认值 |
| `long`  | 1 小时 | 扩展缓存 |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

### 默认值

当使用 Anthropic API 密钥凭证时，OpenClaw 会自动对所有 Anthropic 模型应用 `cacheRetention: "short"`（5 分钟缓存）。你可以通过在配置中显式设置 `cacheRetention` 来覆盖此值。

### 按智能体覆盖 cacheRetention

将模型级参数作为基线，然后通过 `agents.list[].params` 覆盖特定智能体。

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // 大多数智能体的基线
        },
      },
    },
    list: [
      { id: "research", default: true },
      { id: "alerts", params: { cacheRetention: "none" } }, // 仅覆盖此智能体
    ],
  },
}
```

与缓存相关的参数配置合并顺序：

1. `agents.defaults.models["provider/model"].params`
2. `agents.list[].params`（匹配 `id`，按键覆盖）

这样，同一模型上的一个智能体可以保留长期缓存，而另一个智能体则可以关闭缓存，以避免在突发/低复用流量下产生写入成本。

### Bedrock Claude 说明

- Bedrock 上的 Anthropic Claude 模型（`amazon-bedrock/*anthropic.claude*`）在配置后接受 `cacheRetention` 透传。
- 非 Anthropic 的 Bedrock 模型在运行时会被强制设置为 `cacheRetention: "none"`。
- 当未设置显式值时，Anthropic API 密钥的智能默认值也会为 Claude-on-Bedrock 模型引用注入 `cacheRetention: "short"`。

## 100 万上下文窗口（Anthropic beta）

Anthropic 的 100 万上下文窗口受 beta 限制。在 OpenClaw 中，可通过
`params.context1m: true` 为受支持的 Opus/Sonnet 模型按模型启用。

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { context1m: true },
        },
      },
    },
  },
}
```

OpenClaw 会将其映射为 Anthropic 请求中的
`anthropic-beta: context-1m-2025-08-07`。

只有当该模型的 `params.context1m` 被显式设置为 `true` 时，才会启用此功能。

要求：Anthropic 必须允许该凭证使用长上下文。

注意：Anthropic 目前在使用旧版 Anthropic 令牌凭证（`sk-ant-oat-*`）时会拒绝 `context-1m-*` beta 请求。如果你在该旧版凭证模式下配置
`context1m: true`，OpenClaw 会记录警告，并通过跳过 context1m beta
请求头、同时保留必需的 OAuth beta，请求回退到标准上下文窗口。

## Claude CLI 后端

内置的 Anthropic `claude-cli` 后端在 OpenClaw 中受支持。

- Anthropic 员工告诉我们这种用法再次被允许。
- 因此，只要 Anthropic 没有发布新的政策，OpenClaw 就会将 Claude CLI 复用和 `claude -p` 用法视为此集成下被认可的方式。
- 对于始终在线的 Gateway 网关主机，Anthropic API 密钥仍然是最清晰的生产路径，也更便于进行显式服务端计费控制。
- 设置和运行时详情请参见 [/gateway/cli-backends](/zh-CN/gateway/cli-backends)。

## 说明

- Anthropic 的公开 Claude Code 文档仍然记录了类似
  `claude -p` 的直接 CLI 用法，而 Anthropic 员工也告诉我们 OpenClaw 风格的 Claude CLI 用法再次被允许。除非 Anthropic 发布新的政策变更，否则我们将这一指导视为已确定。
- Anthropic setup-token 仍在 OpenClaw 中作为受支持的令牌凭证路径保留，但 OpenClaw 现在在可用时优先使用 Claude CLI 复用和 `claude -p`。
- 凭证详情和复用规则请参见 [/concepts/oauth](/zh-CN/concepts/oauth)。

## 故障排除

**401 错误 / 令牌突然失效**

- Anthropic 令牌凭证可能会过期或被撤销。
- 对于新的设置，请迁移到 Anthropic API 密钥。

**未找到提供商 “anthropic” 的 API 密钥**

- 凭证是**按智能体**管理的。新智能体不会继承主智能体的密钥。
- 请为该智能体重新运行新手引导，或者在 Gateway 网关主机上配置 API 密钥，然后使用 `openclaw models status` 验证。

**未找到配置文件 `anthropic:default` 的凭证**

- 运行 `openclaw models status` 查看当前启用的是哪个凭证配置文件。
- 重新运行新手引导，或者为该配置文件路径配置一个 API 密钥。

**没有可用的凭证配置文件（全部处于冷却中/不可用）**

- 检查 `openclaw models status --json` 中的 `auth.unusableProfiles`。
- Anthropic 速率限制冷却可能是按模型划分的，因此即使当前模型处于冷却中，兄弟 Anthropic 模型仍可能可用。
- 添加另一个 Anthropic 配置文件，或等待冷却结束。

更多内容：[/gateway/troubleshooting](/zh-CN/gateway/troubleshooting) 和 [/help/faq](/zh-CN/help/faq)。
