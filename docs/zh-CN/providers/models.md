---
read_when:
    - 你想选择一个模型提供商
    - 你想要用于 LLM 认证和模型选择的快速设置示例
summary: OpenClaw 支持的模型提供商（LLM）
title: 模型提供商快速开始
x-i18n:
    generated_at: "2026-04-05T08:42:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 83e372193b476c7cee6eb9f5c443b03563d863043f47c633ac0096bca642cc6f
    source_path: providers/models.md
    workflow: 15
---

# 模型提供商

OpenClaw 可以使用许多 LLM 提供商。选择一个，完成认证，然后将默认模型设置为 `provider/model`。

## 快速开始（两步）

1. 使用提供商完成认证（通常通过 `openclaw onboard`）。
2. 设置默认模型：

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## 支持的提供商（入门集合）

- [Anthropic（API + Claude CLI）](/providers/anthropic)
- [Amazon Bedrock](/providers/bedrock)
- [BytePlus（国际版）](/concepts/model-providers#byteplus-international)
- [Chutes](/providers/chutes)
- [Cloudflare AI Gateway](/providers/cloudflare-ai-gateway)
- [Fireworks](/providers/fireworks)
- [GLM 模型](/providers/glm)
- [MiniMax](/providers/minimax)
- [Mistral](/providers/mistral)
- [Moonshot AI（Kimi + Kimi Coding）](/providers/moonshot)
- [OpenAI（API + Codex）](/providers/openai)
- [OpenCode（Zen + Go）](/providers/opencode)
- [OpenRouter](/providers/openrouter)
- [Qianfan](/providers/qianfan)
- [Qwen](/providers/qwen)
- [StepFun](/providers/stepfun)
- [Synthetic](/providers/synthetic)
- [Vercel AI Gateway](/providers/vercel-ai-gateway)
- [Venice（Venice AI）](/providers/venice)
- [xAI](/providers/xai)
- [Z.AI](/providers/zai)

## 其他内置变体

- `anthropic-vertex` - 当 Vertex 凭证可用时，隐式支持 Google Vertex 上的 Anthropic；无需单独的新手引导认证选项
- `copilot-proxy` - 本地 VS Code Copilot Proxy 桥接；使用 `openclaw onboard --auth-choice copilot-proxy`
- `google-gemini-cli` - 非官方 Gemini CLI OAuth 流程；需要本地安装 `gemini`（`brew install gemini-cli` 或 `npm install -g @google/gemini-cli`）；默认模型为 `google-gemini-cli/gemini-3.1-pro-preview`；使用 `openclaw onboard --auth-choice google-gemini-cli` 或 `openclaw models auth login --provider google-gemini-cli --set-default`

如需完整的提供商目录（xAI、Groq、Mistral 等）和高级配置，请参阅[模型提供商](/concepts/model-providers)。
