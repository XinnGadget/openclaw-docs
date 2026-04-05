---
read_when:
    - 你想使用 OpenCode 托管的模型访问
    - 你想在 Zen 和 Go 目录之间进行选择
summary: 在 OpenClaw 中使用 OpenCode Zen 和 Go 目录
title: OpenCode
x-i18n:
    generated_at: "2026-04-05T08:42:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: c23bc99208d9275afcb1731c28eee250c9f4b7d0578681ace31416135c330865
    source_path: providers/opencode.md
    workflow: 15
---

# OpenCode

OpenCode 在 OpenClaw 中提供两个托管目录：

- `opencode/...` 用于 **Zen** 目录
- `opencode-go/...` 用于 **Go** 目录

这两个目录使用相同的 OpenCode API 密钥。OpenClaw 将运行时提供商 id 保持分离，
以确保上游的逐模型路由保持正确，但新手引导和文档将它们视为一次统一的
OpenCode 设置。

## CLI 设置

### Zen 目录

```bash
openclaw onboard --auth-choice opencode-zen
openclaw onboard --opencode-zen-api-key "$OPENCODE_API_KEY"
```

### Go 目录

```bash
openclaw onboard --auth-choice opencode-go
openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
```

## 配置片段

```json5
{
  env: { OPENCODE_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

## 目录

### Zen

- 运行时提供商：`opencode`
- 示例模型：`opencode/claude-opus-4-6`、`opencode/gpt-5.4`、`opencode/gemini-3-pro`
- 最适合你想使用经过精选的 OpenCode 多模型代理时

### Go

- 运行时提供商：`opencode-go`
- 示例模型：`opencode-go/kimi-k2.5`、`opencode-go/glm-5`、`opencode-go/minimax-m2.5`
- 最适合你想使用 OpenCode 托管的 Kimi/GLM/MiniMax 阵容时

## 说明

- 也支持 `OPENCODE_ZEN_API_KEY`。
- 在设置期间输入一个 OpenCode 密钥会为两个运行时提供商存储凭证。
- 你需要登录 OpenCode，添加账单信息，然后复制你的 API 密钥。
- 计费和目录可用性由 OpenCode 控制台管理。
- 由 Gemini 支持的 OpenCode 引用会保留在 proxy-Gemini 路径上，因此 OpenClaw 会在那里保留
  Gemini thought-signature 清理，而不会启用原生 Gemini
  重放验证或 bootstrap 重写。
- 非 Gemini 的 OpenCode 引用会保留最小化的 OpenAI 兼容重放策略。
