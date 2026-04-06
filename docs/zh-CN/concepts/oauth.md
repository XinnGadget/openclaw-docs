---
read_when:
    - 你想端到端了解 OpenClaw OAuth
    - 你遇到了令牌失效 / 登出问题
    - 你想了解 Claude CLI 或 OAuth 认证流程
    - 你想使用多个账号或配置文件路由
summary: OpenClaw 中的 OAuth：令牌交换、存储与多账号模式
title: OAuth
x-i18n:
    generated_at: "2026-04-06T15:27:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4117fee70e3e64fd3a762403454ac2b78de695d2b85a7146750c6de615921e02
    source_path: concepts/oauth.md
    workflow: 15
---

# OAuth

OpenClaw 支持通过 OAuth 实现“订阅认证”，适用于提供该能力的提供商
（尤其是 **OpenAI Codex（ChatGPT OAuth）**）。对于 Anthropic，目前实际上的区分
是：

- **Anthropic API key**：常规 Anthropic API 计费
- **Anthropic Claude CLI / OpenClaw 内的订阅认证**：Anthropic 员工
  告诉我们这种用法再次被允许

OpenAI Codex OAuth 已明确支持在 OpenClaw 这类外部工具中使用。本页说明：

对于生产环境中的 Anthropic，API key 认证仍是更安全、也更推荐的路径。

- OAuth **令牌交换** 的工作方式（PKCE）
- 令牌**存储** 在哪里（以及原因）
- 如何处理**多个账号**（配置文件 + 每会话覆盖）

OpenClaw 还支持自带 OAuth 或 API‑key
流程的**提供商插件**。可通过以下命令运行：

```bash
openclaw models auth login --provider <id>
```

## 令牌汇集点（为什么存在）

OAuth 提供商通常会在登录 / 刷新流程中签发**新的刷新令牌**。某些提供商（或 OAuth 客户端）会在为同一用户 / 应用签发新令牌时，使旧的刷新令牌失效。

实际症状：

- 你同时通过 OpenClaw _和_ Claude Code / Codex CLI 登录 → 之后其中一个会随机出现“已登出”

为减少这种情况，OpenClaw 将 `auth-profiles.json` 视为**令牌汇集点**：

- 运行时从**一个位置**读取凭证
- 我们可以保留多个配置文件，并以确定性的方式进行路由
- 当凭证复用自 Codex CLI 这类外部 CLI 时，OpenClaw
  会带着来源信息镜像这些凭证，并重新读取该外部来源，而不是
  自己轮换刷新令牌

## 存储（令牌存放位置）

密钥按**每个智能体**存储：

- 认证配置文件（OAuth + API keys + 可选的值级引用）：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- 旧版兼容文件：`~/.openclaw/agents/<agentId>/agent/auth.json`
  （发现静态 `api_key` 条目时会被清理）

仅用于旧版导入的文件（仍受支持，但不是主要存储）：

- `~/.openclaw/credentials/oauth.json`（首次使用时导入到 `auth-profiles.json`）

以上所有路径同样遵循 `$OPENCLAW_STATE_DIR`（状态目录覆盖）。完整参考：[/gateway/configuration](/zh-CN/gateway/configuration-reference#auth-storage)

关于静态密钥引用和运行时快照激活行为，请参见 [Secrets Management](/zh-CN/gateway/secrets)。

## Anthropic 旧版令牌兼容性

<Warning>
Anthropic 的公开 Claude Code 文档说明，直接使用 Claude Code 仍受
Claude 订阅限制约束，而 Anthropic 员工告诉我们，OpenClaw 风格的 Claude
CLI 用法再次被允许。因此，OpenClaw 目前将 Claude CLI 复用和
`claude -p` 用法视为该集成的许可方式，除非 Anthropic
发布新的政策。

关于 Anthropic 当前直接使用 Claude Code 的套餐文档，请参见 [Using Claude Code
with your Pro or Max
plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
和 [Using Claude Code with your Team or Enterprise
plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/).

如果你想在 OpenClaw 中使用其他订阅式选项，请参见 [OpenAI
Codex](/zh-CN/providers/openai)、[Qwen Cloud Coding
Plan](/zh-CN/providers/qwen)、[MiniMax Coding Plan](/zh-CN/providers/minimax)
以及 [Z.AI / GLM Coding Plan](/zh-CN/providers/glm)。
</Warning>

OpenClaw 也将 Anthropic setup-token 作为受支持的基于令牌的认证路径提供，但现在在可用时更优先使用 Claude CLI 复用和 `claude -p`。

## Anthropic Claude CLI 迁移

OpenClaw 再次支持复用 Anthropic Claude CLI。如果你在主机上已经有本地
Claude 登录，新手引导 / 配置过程可以直接复用它。

## OAuth 交换（登录如何工作）

OpenClaw 的交互式登录流程由 `@mariozechner/pi-ai` 实现，并接入到向导 / 命令中。

### Anthropic setup-token

流程形式：

1. 从 OpenClaw 启动 Anthropic setup-token 或 paste-token
2. OpenClaw 将生成的 Anthropic 凭证存储到认证配置文件中
3. 模型选择保持为 `anthropic/...`
4. 现有 Anthropic 认证配置文件仍然可用于回滚 / 顺序控制

### OpenAI Codex（ChatGPT OAuth）

OpenAI Codex OAuth 已明确支持在 Codex CLI 之外使用，包括 OpenClaw 工作流。

流程形式（PKCE）：

1. 生成 PKCE verifier/challenge + 随机 `state`
2. 打开 `https://auth.openai.com/oauth/authorize?...`
3. 尝试在 `http://127.0.0.1:1455/auth/callback` 捕获回调
4. 如果无法绑定回调（或你处于远程 / 无头环境），粘贴重定向 URL / 代码
5. 在 `https://auth.openai.com/oauth/token` 进行交换
6. 从访问令牌中提取 `accountId`，并存储 `{ access, refresh, expires, accountId }`

向导路径为 `openclaw onboard` → 认证选项 `openai-codex`。

## 刷新 + 过期

配置文件会存储一个 `expires` 时间戳。

在运行时：

- 如果 `expires` 还在未来 → 使用已存储的访问令牌
- 如果已过期 → 刷新（在文件锁下进行）并覆盖已存储的凭证
- 例外：复用的外部 CLI 凭证仍由外部管理；OpenClaw
  会重新读取 CLI 认证存储，绝不会自己使用复制来的刷新令牌

刷新流程是自动的；通常你不需要手动管理令牌。

## 多个账号（配置文件）+ 路由

有两种模式：

### 1）首选：分离的智能体

如果你希望“个人”和“工作”永不互相影响，请使用隔离的智能体（独立的会话 + 凭证 + 工作区）：

```bash
openclaw agents add work
openclaw agents add personal
```

然后按智能体分别配置认证（通过向导），并将聊天路由到正确的智能体。

### 2）高级：一个智能体内的多个配置文件

`auth-profiles.json` 支持同一提供商下的多个配置文件 ID。

选择使用哪个配置文件：

- 通过配置排序全局指定（`auth.order`）
- 通过 `/model ...@<profileId>` 按会话指定

示例（会话覆盖）：

- `/model Opus@anthropic:work`

如何查看有哪些配置文件 ID：

- `openclaw channels list --json`（显示 `auth[]`）

相关文档：

- [/concepts/model-failover](/zh-CN/concepts/model-failover)（轮换 + 冷却规则）
- [/tools/slash-commands](/zh-CN/tools/slash-commands)（命令界面）

## 相关内容

- [Authentication](/zh-CN/gateway/authentication) — 模型提供商认证概览
- [Secrets](/zh-CN/gateway/secrets) — 凭证存储与 SecretRef
- [Configuration Reference](/zh-CN/gateway/configuration-reference#auth-storage) — 认证配置键名
