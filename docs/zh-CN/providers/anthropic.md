---
read_when:
    - 你想在 OpenClaw 中使用 Anthropic 模型
summary: 在 OpenClaw 中通过 API key 使用 Anthropic Claude
title: Anthropic
x-i18n:
    generated_at: "2026-04-05T18:14:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: bbc6c4938674aedf20ff944bc04e742c9a7e77a5ff10ae4f95b5718504c57c2d
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic（Claude）

Anthropic 构建了 **Claude** 模型家族，并通过 API 提供访问。
在 OpenClaw 中，新的 Anthropic 设置应使用 API key。现有的旧版
Anthropic token 配置文件如果已经配置，运行时仍会继续支持。

<Warning>
在 OpenClaw 中使用 Anthropic 时，计费方式分为：

- **Anthropic API key**：标准 Anthropic API 计费。
- **OpenClaw 内的 Claude 订阅认证**：Anthropic 于
  **2026 年 4 月 4 日太平洋时间中午 12:00 / 英国夏令时间晚上 8:00**
  告知 OpenClaw 用户，这属于第三方 harness 使用，因此需要 **Extra Usage**（按量付费，
  与订阅分开计费）。

我们的本地复现结果也符合这一划分：

- 直接使用 `claude -p` 可能仍然可用
- `claude -p --append-system-prompt ...` 在提示词表明 OpenClaw
  身份时，可能会触发 Extra Usage 限制
- 相同的类 OpenClaw 系统提示词，在 Anthropic SDK + `ANTHROPIC_API_KEY`
  路径上**不会**复现该拦截

所以实际规则是：**Anthropic API key，或启用了
Extra Usage 的 Claude 订阅**。如果你想采用最明确的生产环境方案，请使用 Anthropic API
key。

Anthropic 当前的公开文档：

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)

- [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Using Claude Code with your Team or Enterprise plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

如果你希望采用最明确的计费路径，请改用 Anthropic API key。
OpenClaw 也支持其他订阅式选项，包括 [OpenAI
Codex](/zh-CN/providers/openai)、[Qwen Cloud Coding Plan](/zh-CN/providers/qwen)、
[MiniMax Coding Plan](/zh-CN/providers/minimax) 和 [Z.AI / GLM Coding
Plan](/zh-CN/providers/glm)。
</Warning>

## 选项 A：Anthropic API key

**最适合：** 标准 API 访问和按量计费。
请在 Anthropic Console 中创建你的 API key。

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
- 你可以按消息覆盖（`/think:<level>`），或在模型参数中覆盖：
  `agents.defaults.models["anthropic/<model>"].params.thinking`。
- 相关 Anthropic 文档：
  - [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## 快速模式（Anthropic API）

OpenClaw 的共享 `/fast` 开关也支持直接面向公开 Anthropic 的流量，包括发送到 `api.anthropic.com` 的 API key 和 OAuth 认证请求。

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

- OpenClaw 仅会为直接发往 `api.anthropic.com` 的请求注入 Anthropic service tier。如果你通过代理或 Gateway 网关路由 `anthropic/*`，`/fast` 不会修改 `service_tier`。
- 如果同时设置了显式 Anthropic `serviceTier` 或 `service_tier` 模型参数，则它们会覆盖 `/fast` 的默认值。
- Anthropic 会在响应中的 `usage.service_tier` 报告实际生效的 tier。对于没有 Priority Tier 容量的账户，`service_tier: "auto"` 仍可能解析为 `standard`。

## 提示词缓存（Anthropic API）

OpenClaw 支持 Anthropic 的提示词缓存功能。这**仅适用于 API**；旧版 Anthropic token 认证不会遵循缓存设置。

### 配置

在你的模型配置中使用 `cacheRetention` 参数：

| 值      | 缓存时长 | 说明                 |
| ------- | -------- | -------------------- |
| `none`  | 不缓存   | 禁用提示词缓存       |
| `short` | 5 分钟   | API key 认证的默认值 |
| `long`  | 1 小时   | 扩展缓存             |

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

使用 Anthropic API Key 认证时，OpenClaw 会自动对所有 Anthropic 模型应用 `cacheRetention: "short"`（5 分钟缓存）。你可以通过在配置中显式设置 `cacheRetention` 来覆盖它。

### 按智能体覆盖 `cacheRetention`

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

与缓存相关的配置合并顺序：

1. `agents.defaults.models["provider/model"].params`
2. `agents.list[].params`（匹配 `id`，按键覆盖）

这样就可以让一个智能体保留长期缓存，而另一个使用同一模型的智能体禁用缓存，以避免突发性/低复用流量带来的写入成本。

### Bedrock Claude 说明

- Bedrock 上的 Anthropic Claude 模型（`amazon-bedrock/*anthropic.claude*`）在配置后可透传 `cacheRetention`。
- 非 Anthropic 的 Bedrock 模型会在运行时被强制设为 `cacheRetention: "none"`。
- 当未设置显式值时，Anthropic API key 的智能默认值也会为 Claude-on-Bedrock 模型引用填入 `cacheRetention: "short"`。

## 100 万上下文窗口（Anthropic beta）

Anthropic 的 100 万上下文窗口受 beta 权限控制。在 OpenClaw 中，
对受支持的 Opus/Sonnet 模型，可通过为每个模型设置
`params.context1m: true` 启用。

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

只有当该模型的 `params.context1m` 被显式设置为 `true` 时，
此功能才会启用。

要求：Anthropic 必须允许该凭证使用长上下文
（通常是 API key 计费，或 OpenClaw 的 Claude 登录路径 / 启用了
Extra Usage 的旧版 token 认证）。否则 Anthropic 会返回：
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`。

注意：Anthropic 当前在使用
旧版 Anthropic token 认证（`sk-ant-oat-*`）时，会拒绝 `context-1m-*`
beta 请求。如果你在这种旧版认证模式下配置了
`context1m: true`，OpenClaw 会记录一条警告，并通过跳过 context1m beta
header 回退到标准上下文窗口，同时保留所需的 OAuth beta。

## 已移除：Claude CLI 后端

内置的 Anthropic `claude-cli` 后端已被移除。

- Anthropic 在 2026 年 4 月 4 日的通知中表示，由 OpenClaw 驱动的 Claude 登录流量属于
  第三方 harness 使用，因此需要 **Extra Usage**。
- 我们的本地复现也显示，直接使用
  `claude -p --append-system-prompt ...` 在附加提示词表明 OpenClaw
  身份时，也可能触发同样的限制。
- 相同的类 OpenClaw 系统提示词，在
  Anthropic SDK + `ANTHROPIC_API_KEY` 路径上不会触发该限制。
- 在 OpenClaw 中处理 Anthropic 流量时，请使用 Anthropic API key。

## 说明

- Anthropic 的公开 Claude Code 文档仍然记录了直接 CLI 用法，例如
  `claude -p`，但 Anthropic 面向 OpenClaw 用户的单独通知指出，
  **OpenClaw** 的 Claude 登录路径属于第三方 harness 使用，因此需要
  **Extra Usage**（按量付费，与订阅分开计费）。
  我们的本地复现也显示，直接使用
  `claude -p --append-system-prompt ...` 在附加提示词表明 OpenClaw
  身份时可能触发同样的限制，而相同形式的提示词在
  Anthropic SDK + `ANTHROPIC_API_KEY` 路径上不会复现该问题。对于生产环境，我们
  建议改用 Anthropic API key。
- Anthropic setup-token 已重新在 OpenClaw 中作为旧版/手动路径提供。Anthropic 针对 OpenClaw 的专用计费通知仍然适用，因此使用此路径时，应预期 Anthropic 会要求 **Extra Usage**。
- 认证细节和复用规则见 [/concepts/oauth](/zh-CN/concepts/oauth)。

## 故障排除

**401 错误 / token 突然失效**

- 旧版 Anthropic token 认证可能过期或被撤销。
- 对于新的设置，请迁移到 Anthropic API key。

**未找到 provider "anthropic" 的 API key**

- 认证是**按智能体**区分的。新智能体不会继承主智能体的 key。
- 重新为该智能体运行新手引导，或在 Gateway 网关
  主机上配置 API key，然后使用 `openclaw models status` 验证。

**未找到配置文件 `anthropic:default` 的凭证**

- 运行 `openclaw models status` 查看当前激活的是哪个认证配置文件。
- 重新运行新手引导，或为该配置文件路径配置 API key。

**没有可用的认证配置文件（全部处于冷却中/不可用）**

- 检查 `openclaw models status --json` 中的 `auth.unusableProfiles`。
- Anthropic 的速率限制冷却可能是按模型区分的，因此即使当前模型处于冷却中，
  同级的另一个 Anthropic 模型仍可能可用。
- 添加另一个 Anthropic 配置文件，或等待冷却结束。

更多内容：[/gateway/troubleshooting](/zh-CN/gateway/troubleshooting) 和 [/help/faq](/zh-CN/help/faq)。
