---
summary: "Поставщики моделей (LLM), поддерживаемые OpenClaw"
read_when:
  - Вы хотите выбрать поставщика модели
  - Вам нужны примеры быстрой настройки аутентификации LLM + выбора модели
title: "Быстрое начало работы с поставщиками моделей"
---

# Поставщики моделей

OpenClaw может использовать множество поставщиков LLM. Выберите одного, пройдите аутентификацию, затем задайте модель по умолчанию в формате `provider/model`.

## Быстрое начало (два шага)

1. Пройдите аутентификацию у поставщика (обычно через `openclaw onboard`).
2. Задайте модель по умолчанию:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Поддерживаемые поставщики (начальный набор)

- [Alibaba Model Studio](/providers/alibaba)
- [Anthropic (API + Claude CLI)](/providers/anthropic)
- [Amazon Bedrock](/providers/bedrock)
- [BytePlus (International)](/concepts/model-providers#byteplus-international)
- [Chutes](/providers/chutes)
- [ComfyUI](/providers/comfy)
- [Cloudflare AI Gateway](/providers/cloudflare-ai-gateway)
- [fal](/providers/fal)
- [Fireworks](/providers/fireworks)
- [GLM models](/providers/glm)
- [MiniMax](/providers/minimax)
- [Mistral](/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/providers/moonshot)
- [OpenAI (API + Codex)](/providers/openai)
- [OpenCode (Zen + Go)](/providers/opencode)
- [OpenRouter](/providers/openrouter)
- [Qianfan](/providers/qianfan)
- [Qwen](/providers/qwen)
- [Runway](/providers/runway)
- [StepFun](/providers/stepfun)
- [Synthetic](/providers/synthetic)
- [Vercel AI Gateway](/providers/vercel-ai-gateway)
- [Venice (Venice AI)](/providers/venice)
- [xAI](/providers/xai)
- [Z.AI](/providers/zai)

## Дополнительные варианты поставщиков, включённые в комплект

- `anthropic-vertex` — неявная поддержка Anthropic на Google Vertex, когда доступны учётные данные Vertex; отдельный выбор аутентификации при подключении не требуется.
- `copilot-proxy` — локальный мост VS Code Copilot Proxy; используйте `openclaw onboard --auth-choice copilot-proxy`.
- `google-gemini-cli` — неофициальный поток OAuth для Gemini CLI; требуется локальная установка `gemini` (`brew install gemini-cli` или `npm install -g @google/gemini-cli`); модель по умолчанию — `google-gemini-cli/gemini-3-flash-preview`; используйте `openclaw onboard --auth-choice google-gemini-cli` или `openclaw models auth login --provider google-gemini-cli --set-default`.

Полный каталог поставщиков (xAI, Groq, Mistral и др.) и расширенная конфигурация доступны в разделе [Поставщики моделей](/concepts/model-providers).