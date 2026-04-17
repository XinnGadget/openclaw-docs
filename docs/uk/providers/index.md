---
read_when:
    - Ви хочете вибрати постачальника моделей
    - Вам потрібен швидкий огляд підтримуваних бекендів LLM
summary: Постачальники моделей (LLM), які підтримуються OpenClaw
title: Каталог постачальників
x-i18n:
    generated_at: "2026-04-13T07:24:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3bc682d008119719826f71f74959ab32bedf14214459f5e6ac9cb70371d3c540
    source_path: providers/index.md
    workflow: 15
---

# Постачальники моделей

OpenClaw може використовувати багато постачальників LLM. Виберіть постачальника, пройдіть автентифікацію, а потім установіть
модель за замовчуванням як `provider/model`.

Шукаєте документацію щодо каналів чату (WhatsApp/Telegram/Discord/Slack/Mattermost (Plugin)/тощо)? Див. [Channels](/uk/channels).

## Швидкий старт

1. Пройдіть автентифікацію у постачальника (зазвичай через `openclaw onboard`).
2. Установіть модель за замовчуванням:

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
- [моделі GLM](/uk/providers/glm)
- [Google (Gemini)](/uk/providers/google)
- [Groq (LPU inference)](/uk/providers/groq)
- [Hugging Face (Inference)](/uk/providers/huggingface)
- [inferrs (локальні моделі)](/uk/providers/inferrs)
- [Kilocode](/uk/providers/kilocode)
- [LiteLLM (уніфікований Gateway)](/uk/providers/litellm)
- [LM Studio (локальні моделі)](/uk/providers/lmstudio)
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
- [Venice (Venice AI, з акцентом на конфіденційність)](/uk/providers/venice)
- [Vercel AI Gateway](/uk/providers/vercel-ai-gateway)
- [Vydra](/uk/providers/vydra)
- [vLLM (локальні моделі)](/uk/providers/vllm)
- [Volcengine (Doubao)](/uk/providers/volcengine)
- [xAI](/uk/providers/xai)
- [Xiaomi](/uk/providers/xiaomi)
- [Z.AI](/uk/providers/zai)

## Спільні сторінки огляду

- [Додаткові вбудовані варіанти](/uk/providers/models#additional-bundled-provider-variants) - Anthropic Vertex, Copilot Proxy і Gemini CLI OAuth
- [Генерація зображень](/uk/tools/image-generation) - спільний інструмент `image_generate`, вибір постачальника та перемикання при відмові
- [Генерація музики](/uk/tools/music-generation) - спільний інструмент `music_generate`, вибір постачальника та перемикання при відмові
- [Генерація відео](/uk/tools/video-generation) - спільний інструмент `video_generate`, вибір постачальника та перемикання при відмові

## Постачальники транскрибування

- [Deepgram (транскрибування аудіо)](/uk/providers/deepgram)

## Інструменти спільноти

- [Claude Max API Proxy](/uk/providers/claude-max-api-proxy) - Проксі спільноти для облікових даних підписки Claude (перед використанням перевірте політику/умови Anthropic)

Повний каталог постачальників (xAI, Groq, Mistral тощо) і розширену конфігурацію див. у розділі [Постачальники моделей](/uk/concepts/model-providers).
