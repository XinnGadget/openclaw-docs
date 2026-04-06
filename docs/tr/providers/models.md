---
read_when:
    - Bir model provider seçmek istiyorsunuz
    - LLM auth + model seçimi için hızlı kurulum örnekleri istiyorsunuz
summary: OpenClaw tarafından desteklenen model provider’lar (LLM’ler)
title: Model Provider Hızlı Başlangıç
x-i18n:
    generated_at: "2026-04-06T03:11:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: c0314fb1c754171e5fc252d30f7ba9bb6acdbb978d97e9249264d90351bac2e7
    source_path: providers/models.md
    workflow: 15
---

# Model Provider’lar

OpenClaw birçok LLM provider’ı kullanabilir. Birini seçin, kimlik doğrulamasını yapın, sonra varsayılan
modeli `provider/model` olarak ayarlayın.

## Hızlı başlangıç (iki adım)

1. Provider ile kimlik doğrulaması yapın (genellikle `openclaw onboard` ile).
2. Varsayılan modeli ayarlayın:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Desteklenen provider’lar (başlangıç kümesi)

- [Alibaba Model Studio](/providers/alibaba)
- [Anthropic (API + Claude CLI)](/tr/providers/anthropic)
- [Amazon Bedrock](/tr/providers/bedrock)
- [BytePlus (International)](/tr/concepts/model-providers#byteplus-international)
- [Chutes](/tr/providers/chutes)
- [ComfyUI](/providers/comfy)
- [Cloudflare AI Gateway](/tr/providers/cloudflare-ai-gateway)
- [fal](/providers/fal)
- [Fireworks](/tr/providers/fireworks)
- [GLM models](/tr/providers/glm)
- [MiniMax](/tr/providers/minimax)
- [Mistral](/tr/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/tr/providers/moonshot)
- [OpenAI (API + Codex)](/tr/providers/openai)
- [OpenCode (Zen + Go)](/tr/providers/opencode)
- [OpenRouter](/tr/providers/openrouter)
- [Qianfan](/tr/providers/qianfan)
- [Qwen](/tr/providers/qwen)
- [Runway](/providers/runway)
- [StepFun](/tr/providers/stepfun)
- [Synthetic](/tr/providers/synthetic)
- [Vercel AI Gateway](/tr/providers/vercel-ai-gateway)
- [Venice (Venice AI)](/tr/providers/venice)
- [xAI](/tr/providers/xai)
- [Z.AI](/tr/providers/zai)

## Ek paketlenmiş provider varyantları

- `anthropic-vertex` - Vertex kimlik bilgileri mevcut olduğunda örtük Anthropic on Google Vertex desteği; ayrı bir onboarding auth seçeneği yok
- `copilot-proxy` - yerel VS Code Copilot Proxy köprüsü; `openclaw onboard --auth-choice copilot-proxy` kullanın

Tam provider kataloğu (xAI, Groq, Mistral vb.) ve gelişmiş yapılandırma için
bkz. [Model providers](/tr/concepts/model-providers).
