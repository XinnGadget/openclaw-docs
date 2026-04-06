---
read_when:
    - Ви хочете вибрати постачальника моделей
    - Вам потрібен швидкий огляд підтримуваних бекендів LLM
summary: Постачальники моделей (LLM), які підтримує OpenClaw
title: Каталог постачальників
x-i18n:
    generated_at: "2026-04-06T18:54:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 39d9ace35fd9452a4fb510fd980d251b6e51480e4647f051020bee2f1f2222e1
    source_path: providers/index.md
    workflow: 15
---

# Постачальники моделей

OpenClaw може використовувати багато постачальників LLM. Виберіть постачальника, пройдіть автентифікацію, а потім задайте
модель за замовчуванням як `provider/model`.

Шукаєте документацію про канали чату (WhatsApp/Telegram/Discord/Slack/Mattermost (plugin)/etc.)? Див. [Канали](/uk/channels).

## Швидкий старт

1. Пройдіть автентифікацію у постачальника (зазвичай через `openclaw onboard`).
2. Задайте модель за замовчуванням:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Документація постачальників

- [Alibaba Model Studio](/uk/providers/alibaba)
- [Amazon Bedrock](/uk/providers/bedrock)
- [Anthropic (API + Claude CLI)](/uk/providers/anthropic)
- [Arcee AI (моделі Trinity)](/uk/providers/arcee)
- [BytePlus (міжнародний)](/uk/concepts/model-providers#byteplus-international)
- [Chutes](/uk/providers/chutes)
- [ComfyUI](/uk/providers/comfy)
- [Cloudflare AI Gateway](/uk/providers/cloudflare-ai-gateway)
- [DeepSeek](/uk/providers/deepseek)
- [fal](/uk/providers/fal)
- [Fireworks](/uk/providers/fireworks)
- [GitHub Copilot](/uk/providers/github-copilot)
- [Моделі GLM](/uk/providers/glm)
- [Google (Gemini)](/uk/providers/google)
- [Groq (LPU-інференс)](/uk/providers/groq)
- [Hugging Face (інференс)](/uk/providers/huggingface)
- [Kilocode](/uk/providers/kilocode)
- [LiteLLM (уніфікований шлюз)](/uk/providers/litellm)
- [MiniMax](/uk/providers/minimax)
- [Mistral](/uk/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/uk/providers/moonshot)
- [NVIDIA](/uk/providers/nvidia)
- [Ollama (хмарні + локальні моделі)](/uk/providers/ollama)
- [OpenAI (API + Codex)](/uk/providers/openai)
- [OpenCode](/uk/providers/opencode)
- [OpenCode Go](/uk/providers/opencode-go)
- [OpenRouter](/uk/providers/openrouter)
- [Perplexity (вебпошук)](/uk/providers/perplexity-provider)
- [Qianfan](/uk/providers/qianfan)
- [Qwen Cloud](/uk/providers/qwen)
- [Runway](/uk/providers/runway)
- [SGLang (локальні моделі)](/uk/providers/sglang)
- [StepFun](/uk/providers/stepfun)
- [Synthetic](/uk/providers/synthetic)
- [Together AI](/uk/providers/together)
- [Venice (Venice AI, орієнтований на конфіденційність)](/uk/providers/venice)
- [Vercel AI Gateway](/uk/providers/vercel-ai-gateway)
- [Vydra](/uk/providers/vydra)
- [vLLM (локальні моделі)](/uk/providers/vllm)
- [Volcengine (Doubao)](/uk/providers/volcengine)
- [xAI](/uk/providers/xai)
- [Xiaomi](/uk/providers/xiaomi)
- [Z.AI](/uk/providers/zai)

## Спільні оглядові сторінки

- [Додаткові вбудовані варіанти](/uk/providers/models#additional-bundled-provider-variants) - Anthropic Vertex, Copilot Proxy і Gemini CLI OAuth
- [Генерація зображень](/uk/tools/image-generation) - Спільний інструмент `image_generate`, вибір постачальника та failover
- [Генерація музики](/uk/tools/music-generation) - Спільний інструмент `music_generate`, вибір постачальника та failover
- [Генерація відео](/uk/tools/video-generation) - Спільний інструмент `video_generate`, вибір постачальника та failover

## Постачальники транскрибування

- [Deepgram (транскрибування аудіо)](/uk/providers/deepgram)

## Інструменти спільноти

- [Claude Max API Proxy](/uk/providers/claude-max-api-proxy) - Проксі від спільноти для облікових даних підписки Claude (перед використанням перевірте політику/умови Anthropic)

Повний каталог постачальників (xAI, Groq, Mistral тощо) і розширену конфігурацію
див. у розділі [Постачальники моделей](/uk/concepts/model-providers).
