---
summary: "Поставщики моделей (LLM), поддерживаемые OpenClaw"
read_when:
  - Вы хотите выбрать поставщика модели
  - Вам нужен краткий обзор поддерживаемых бэкендов LLM
title: "Каталог поставщиков"
---

# Поставщики моделей

OpenClaw может использовать множество поставщиков LLM. Выберите поставщика, пройдите аутентификацию, затем задайте модель по умолчанию в формате `provider/model`.

Ищете документацию по каналам чата (WhatsApp/Telegram/Discord/Slack/Mattermost (плагин) и т. д.)? Смотрите [Каналы](/channels).

## Быстрый старт

1. Пройдите аутентификацию у поставщика (обычно с помощью команды `openclaw onboard`.
2. Задайте модель по умолчанию:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Документация по поставщикам

- [Alibaba Model Studio](/providers/alibaba)
- [Amazon Bedrock](/providers/bedrock)
- [Anthropic (API + Claude CLI)](/providers/anthropic)
- [Arcee AI (модели Trinity)](/providers/arcee)
- [BytePlus (международная версия)](/concepts/model-providers#byteplus-international)
- [Chutes](/providers/chutes)
- [ComfyUI](/providers/comfy)
- [Cloudflare AI Gateway](/providers/cloudflare-ai-gateway)
- [DeepSeek](/providers/deepseek)
- [fal](/providers/fal)
- [Fireworks](/providers/fireworks)
- [GitHub Copilot](/providers/github-copilot)
- [Модели GLM](/providers/glm)
- [Google (Gemini)](/providers/google)
- [Groq (вывод на LPU)](/providers/groq)
- [Hugging Face (вывод)](/providers/huggingface)
- [inferrs (локальные модели)](/providers/inferrs)
- [Kilocode](/providers/kilocode)
- [LiteLLM (унифицированный шлюз)](/providers/litellm)
- [MiniMax](/providers/minimax)
- [Mistral](/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/providers/moonshot)
- [NVIDIA](/providers/nvidia)
- [Ollama (облачные и локальные модели)](/providers/ollama)
- [OpenAI (API + Codex)](/providers/openai)
- [OpenCode](/providers/opencode)
- [OpenCode Go](/providers/opencode-go)
- [OpenRouter](/providers/openrouter)
- [Perplexity (поиск в интернете)](/providers/perplexity-provider)
- [Qianfan](/providers/qianfan)
- [Qwen Cloud](/providers/qwen)
- [Runway](/providers/runway)
- [SGLang (локальные модели)](/providers/sglang)
- [StepFun](/providers/stepfun)
- [Synthetic](/providers/synthetic)
- [Together AI](/providers/together)
- [Venice (Venice AI, ориентирован на конфиденциальность)](/providers/venice)
- [Vercel AI Gateway](/providers/vercel-ai-gateway)
- [Vydra](/providers/vydra)
- [vLLM (локальные модели)](/providers/vllm)
- [Volcengine (Doubao)](/providers/volcengine)
- [xAI](/providers/xai)
- [Xiaomi](/providers/xiaomi)
- [Z.AI](/providers/zai)

## Общие обзорные страницы

- [Дополнительные встроенные варианты](/providers/models#additional-bundled-provider-variants) — Anthropic Vertex, Copilot Proxy и Gemini CLI OAuth
- [Генерация изображений](/tools/image-generation) — общий инструмент `image_generate`, выбор поставщика и отказоустойчивость
- [Генерация музыки](/tools/music-generation) — общий инструмент `music_generate`, выбор поставщика и отказоустойчивость
- [Генерация видео](/tools/video-generation) — общий инструмент `video_generate`, выбор поставщика и отказоустойчивость

## Поставщики услуг транскрипции

- [Deepgram (транскрипция аудио)](/providers/deepgram)

## Инструменты сообщества

- [Claude Max API Proxy](/providers/claude-max-api-proxy) — прокси сообщества для учётных данных подписки Claude (перед использованием проверьте политику/условия Anthropic)

Полный каталог поставщиков (xAI, Groq, Mistral и т. д.) и расширенная конфигурация доступны в разделе [Поставщики моделей](/concepts/model-providers).