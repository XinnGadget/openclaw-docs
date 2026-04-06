---
read_when:
    - 你想选择一个模型提供商
    - 你想查看用于 LLM 身份验证和模型选择的快速设置示例
summary: OpenClaw 支持的模型提供商（LLM）
title: 模型提供商快速开始
x-i18n:
    generated_at: "2026-04-06T00:19:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4836c7baa0a5af6b01c1369ebe2fdc6032d50d306dd10e2dbb778c6fce1384c4
    source_path: providers/models.md
    workflow: 15
---

# 模型提供商

OpenClaw 可以使用许多 LLM 提供商。选择一个，完成身份验证，然后将默认模型设置为 `provider/model`。

## 快速开始（两步）

1. 使用提供商完成身份验证（通常通过 `openclaw onboard`）。
2. 设置默认模型：

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## 支持的提供商（入门集合）

- [Alibaba Model Studio](/zh-CN/providers/alibaba)
- [Anthropic（API + Claude CLI）](/zh-CN/providers/anthropic)
- [Amazon Bedrock](/zh-CN/providers/bedrock)
- [BytePlus（国际版）](/zh-CN/concepts/model-providers#byteplus-international)
- [Chutes](/zh-CN/providers/chutes)
- [Cloudflare AI Gateway](/zh-CN/providers/cloudflare-ai-gateway)
- [fal](/zh-CN/providers/fal)
- [Fireworks](/zh-CN/providers/fireworks)
- [GLM 模型](/zh-CN/providers/glm)
- [MiniMax](/zh-CN/providers/minimax)
- [Mistral](/zh-CN/providers/mistral)
- [Moonshot AI（Kimi + Kimi Coding）](/zh-CN/providers/moonshot)
- [OpenAI（API + Codex）](/zh-CN/providers/openai)
- [OpenCode（Zen + Go）](/zh-CN/providers/opencode)
- [OpenRouter](/zh-CN/providers/openrouter)
- [Qianfan](/zh-CN/providers/qianfan)
- [Qwen](/zh-CN/providers/qwen)
- [Runway](/zh-CN/providers/runway)
- [StepFun](/zh-CN/providers/stepfun)
- [Synthetic](/zh-CN/providers/synthetic)
- [Vercel AI Gateway](/zh-CN/providers/vercel-ai-gateway)
- [Venice（Venice AI）](/zh-CN/providers/venice)
- [xAI](/zh-CN/providers/xai)
- [Z.AI](/zh-CN/providers/zai)

## 其他内置提供商变体

- `anthropic-vertex` - 当 Vertex 凭证可用时，隐式支持 Google Vertex 上的 Anthropic；无需单独的新手引导身份验证选项
- `copilot-proxy` - 本地 VS Code Copilot Proxy 桥接；使用 `openclaw onboard --auth-choice copilot-proxy`

要查看完整的提供商目录（xAI、Groq、Mistral 等）和高级配置，请参阅 [模型提供商](/zh-CN/concepts/model-providers)。
