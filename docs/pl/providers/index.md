---
read_when:
    - Chcesz wybrać providera modeli
    - Potrzebujesz szybkiego przeglądu obsługiwanych backendów LLM
summary: Providery modeli (LLM) obsługiwane przez OpenClaw
title: Katalog providerów
x-i18n:
    generated_at: "2026-04-06T03:11:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7271157a6ab5418672baff62bfd299572fd010f75aad529267095c6e55903882
    source_path: providers/index.md
    workflow: 15
---

# Providery modeli

OpenClaw może używać wielu providerów LLM. Wybierz providera, uwierzytelnij się, a następnie ustaw
domyślny model jako `provider/model`.

Szukasz dokumentacji kanałów czatu (WhatsApp/Telegram/Discord/Slack/Mattermost (plugin)/itd.)? Zobacz [Kanały](/pl/channels).

## Szybki start

1. Uwierzytelnij się u providera (zwykle przez `openclaw onboard`).
2. Ustaw domyślny model:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Dokumentacja providerów

- [Alibaba Model Studio](/providers/alibaba)
- [Amazon Bedrock](/pl/providers/bedrock)
- [Anthropic (API + Claude CLI)](/pl/providers/anthropic)
- [BytePlus (International)](/pl/concepts/model-providers#byteplus-international)
- [Chutes](/pl/providers/chutes)
- [ComfyUI](/providers/comfy)
- [Cloudflare AI Gateway](/pl/providers/cloudflare-ai-gateway)
- [DeepSeek](/pl/providers/deepseek)
- [fal](/providers/fal)
- [Fireworks](/pl/providers/fireworks)
- [GitHub Copilot](/pl/providers/github-copilot)
- [GLM models](/pl/providers/glm)
- [Google (Gemini)](/pl/providers/google)
- [Groq (inferencja LPU)](/pl/providers/groq)
- [Hugging Face (Inference)](/pl/providers/huggingface)
- [Kilocode](/pl/providers/kilocode)
- [LiteLLM (ujednolicony gateway)](/pl/providers/litellm)
- [MiniMax](/pl/providers/minimax)
- [Mistral](/pl/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/pl/providers/moonshot)
- [NVIDIA](/pl/providers/nvidia)
- [Ollama (modele chmurowe + lokalne)](/pl/providers/ollama)
- [OpenAI (API + Codex)](/pl/providers/openai)
- [OpenCode](/pl/providers/opencode)
- [OpenCode Go](/pl/providers/opencode-go)
- [OpenRouter](/pl/providers/openrouter)
- [Perplexity (wyszukiwanie w sieci)](/pl/providers/perplexity-provider)
- [Qianfan](/pl/providers/qianfan)
- [Qwen Cloud](/pl/providers/qwen)
- [Runway](/providers/runway)
- [SGLang (modele lokalne)](/pl/providers/sglang)
- [StepFun](/pl/providers/stepfun)
- [Synthetic](/pl/providers/synthetic)
- [Together AI](/pl/providers/together)
- [Venice (Venice AI, skoncentrowane na prywatności)](/pl/providers/venice)
- [Vercel AI Gateway](/pl/providers/vercel-ai-gateway)
- [Vydra](/providers/vydra)
- [vLLM (modele lokalne)](/pl/providers/vllm)
- [Volcengine (Doubao)](/pl/providers/volcengine)
- [xAI](/pl/providers/xai)
- [Xiaomi](/pl/providers/xiaomi)
- [Z.AI](/pl/providers/zai)

## Wspólne strony przeglądowe

- [Dodatkowe wbudowane warianty](/pl/providers/models#additional-bundled-provider-variants) - Anthropic Vertex, Copilot Proxy i Gemini CLI OAuth
- [Generowanie obrazów](/pl/tools/image-generation) - Wspólne narzędzie `image_generate`, wybór providera i failover
- [Generowanie muzyki](/tools/music-generation) - Wspólne narzędzie `music_generate`, wybór providera i failover
- [Generowanie wideo](/tools/video-generation) - Wspólne narzędzie `video_generate`, wybór providera i failover

## Providery transkrypcji

- [Deepgram (transkrypcja audio)](/pl/providers/deepgram)

## Narzędzia społeczności

- [Claude Max API Proxy](/pl/providers/claude-max-api-proxy) - Społecznościowe proxy dla poświadczeń subskrypcji Claude (przed użyciem sprawdź zasady/warunki Anthropic)

Pełny katalog providerów (xAI, Groq, Mistral itd.) i konfigurację zaawansowaną znajdziesz w [Providerach modeli](/pl/concepts/model-providers).
