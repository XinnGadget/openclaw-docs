---
read_when:
    - Bir model sağlayıcısı seçmek istiyorsunuz
    - LLM kimlik doğrulaması + model seçimi için hızlı kurulum örnekleri istiyorsunuz
summary: OpenClaw tarafından desteklenen model sağlayıcıları (LLM'ler)
title: Model Sağlayıcısı Hızlı Başlangıç
x-i18n:
    generated_at: "2026-04-07T08:48:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 500191bfe853241096f97928ced2327a13b6f7f62003cb7452b24886c272e6ba
    source_path: providers/models.md
    workflow: 15
---

# Model Sağlayıcıları

OpenClaw birçok LLM sağlayıcısını kullanabilir. Birini seçin, kimlik doğrulamasını yapın, ardından
varsayılan modeli `provider/model` olarak ayarlayın.

## Hızlı başlangıç (iki adım)

1. Sağlayıcı ile kimlik doğrulaması yapın (genellikle `openclaw onboard` üzerinden).
2. Varsayılan modeli ayarlayın:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Desteklenen sağlayıcılar (başlangıç kümesi)

- [Alibaba Model Studio](/tr/providers/alibaba)
- [Anthropic (API + Claude CLI)](/tr/providers/anthropic)
- [Amazon Bedrock](/tr/providers/bedrock)
- [BytePlus (Uluslararası)](/tr/concepts/model-providers#byteplus-international)
- [Chutes](/tr/providers/chutes)
- [ComfyUI](/tr/providers/comfy)
- [Cloudflare AI Gateway](/tr/providers/cloudflare-ai-gateway)
- [fal](/tr/providers/fal)
- [Fireworks](/tr/providers/fireworks)
- [GLM modelleri](/tr/providers/glm)
- [MiniMax](/tr/providers/minimax)
- [Mistral](/tr/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/tr/providers/moonshot)
- [OpenAI (API + Codex)](/tr/providers/openai)
- [OpenCode (Zen + Go)](/tr/providers/opencode)
- [OpenRouter](/tr/providers/openrouter)
- [Qianfan](/tr/providers/qianfan)
- [Qwen](/tr/providers/qwen)
- [Runway](/tr/providers/runway)
- [StepFun](/tr/providers/stepfun)
- [Synthetic](/tr/providers/synthetic)
- [Vercel AI Gateway](/tr/providers/vercel-ai-gateway)
- [Venice (Venice AI)](/tr/providers/venice)
- [xAI](/tr/providers/xai)
- [Z.AI](/tr/providers/zai)

## Ek paketlenmiş sağlayıcı varyantları

- `anthropic-vertex` - Vertex kimlik bilgileri kullanılabilir olduğunda örtük Anthropic on Google Vertex desteği; ayrı bir onboarding auth seçimi yok
- `copilot-proxy` - yerel VS Code Copilot Proxy köprüsü; `openclaw onboard --auth-choice copilot-proxy` kullanın
- `google-gemini-cli` - resmî olmayan Gemini CLI OAuth akışı; yerel bir `gemini` kurulumu gerekir (`brew install gemini-cli` veya `npm install -g @google/gemini-cli`); varsayılan model `google-gemini-cli/gemini-3.1-pro-preview`; `openclaw onboard --auth-choice google-gemini-cli` veya `openclaw models auth login --provider google-gemini-cli --set-default` kullanın

Tam sağlayıcı kataloğu (xAI, Groq, Mistral vb.) ve gelişmiş yapılandırma için
bkz. [Model sağlayıcıları](/tr/concepts/model-providers).
