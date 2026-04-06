---
read_when:
    - Bir model sağlayıcısı seçmek istiyorsunuz
    - Desteklenen LLM arka uçlarına dair hızlı bir genel bakışa ihtiyacınız var
summary: OpenClaw tarafından desteklenen model sağlayıcıları (LLM'ler)
title: Sağlayıcı Dizini
x-i18n:
    generated_at: "2026-04-06T03:11:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7271157a6ab5418672baff62bfd299572fd010f75aad529267095c6e55903882
    source_path: providers/index.md
    workflow: 15
---

# Model Sağlayıcıları

OpenClaw birçok LLM sağlayıcısını kullanabilir. Bir sağlayıcı seçin, kimlik doğrulaması yapın, ardından
varsayılan modeli `provider/model` olarak ayarlayın.

Sohbet kanalı belgelerini mi arıyorsunuz (WhatsApp/Telegram/Discord/Slack/Mattermost (plugin)/vb.)? Bkz. [Kanallar](/tr/channels).

## Hızlı başlangıç

1. Sağlayıcı ile kimlik doğrulaması yapın (genellikle `openclaw onboard` aracılığıyla).
2. Varsayılan modeli ayarlayın:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Sağlayıcı belgeleri

- [Alibaba Model Studio](/providers/alibaba)
- [Amazon Bedrock](/tr/providers/bedrock)
- [Anthropic (API + Claude CLI)](/tr/providers/anthropic)
- [BytePlus (Uluslararası)](/tr/concepts/model-providers#byteplus-international)
- [Chutes](/tr/providers/chutes)
- [ComfyUI](/providers/comfy)
- [Cloudflare AI Gateway](/tr/providers/cloudflare-ai-gateway)
- [DeepSeek](/tr/providers/deepseek)
- [fal](/providers/fal)
- [Fireworks](/tr/providers/fireworks)
- [GitHub Copilot](/tr/providers/github-copilot)
- [GLM modelleri](/tr/providers/glm)
- [Google (Gemini)](/tr/providers/google)
- [Groq (LPU çıkarımı)](/tr/providers/groq)
- [Hugging Face (Çıkarım)](/tr/providers/huggingface)
- [Kilocode](/tr/providers/kilocode)
- [LiteLLM (birleşik gateway)](/tr/providers/litellm)
- [MiniMax](/tr/providers/minimax)
- [Mistral](/tr/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/tr/providers/moonshot)
- [NVIDIA](/tr/providers/nvidia)
- [Ollama (bulut + yerel modeller)](/tr/providers/ollama)
- [OpenAI (API + Codex)](/tr/providers/openai)
- [OpenCode](/tr/providers/opencode)
- [OpenCode Go](/tr/providers/opencode-go)
- [OpenRouter](/tr/providers/openrouter)
- [Perplexity (web araması)](/tr/providers/perplexity-provider)
- [Qianfan](/tr/providers/qianfan)
- [Qwen Cloud](/tr/providers/qwen)
- [Runway](/providers/runway)
- [SGLang (yerel modeller)](/tr/providers/sglang)
- [StepFun](/tr/providers/stepfun)
- [Synthetic](/tr/providers/synthetic)
- [Together AI](/tr/providers/together)
- [Venice (Venice AI, gizlilik odaklı)](/tr/providers/venice)
- [Vercel AI Gateway](/tr/providers/vercel-ai-gateway)
- [Vydra](/providers/vydra)
- [vLLM (yerel modeller)](/tr/providers/vllm)
- [Volcengine (Doubao)](/tr/providers/volcengine)
- [xAI](/tr/providers/xai)
- [Xiaomi](/tr/providers/xiaomi)
- [Z.AI](/tr/providers/zai)

## Paylaşılan genel bakış sayfaları

- [Ek paketli varyantlar](/tr/providers/models#additional-bundled-provider-variants) - Anthropic Vertex, Copilot Proxy ve Gemini CLI OAuth
- [Görsel Üretimi](/tr/tools/image-generation) - Paylaşılan `image_generate` aracı, sağlayıcı seçimi ve failover
- [Müzik Üretimi](/tools/music-generation) - Paylaşılan `music_generate` aracı, sağlayıcı seçimi ve failover
- [Video Üretimi](/tools/video-generation) - Paylaşılan `video_generate` aracı, sağlayıcı seçimi ve failover

## Transkripsiyon sağlayıcıları

- [Deepgram (ses transkripsiyonu)](/tr/providers/deepgram)

## Topluluk araçları

- [Claude Max API Proxy](/tr/providers/claude-max-api-proxy) - Claude abonelik kimlik bilgileri için topluluk proxy'si (kullanmadan önce Anthropic ilkesini/şartlarını doğrulayın)

xAI, Groq, Mistral vb. dahil tam sağlayıcı kataloğu ve gelişmiş yapılandırma için
bkz. [Model sağlayıcıları](/tr/concepts/model-providers).
