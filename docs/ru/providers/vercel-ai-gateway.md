---
title: "Шлюз Vercel AI"
summary: "Настройка шлюза Vercel AI (аутентификация + выбор модели)"
read_when:
  - Вы хотите использовать шлюз Vercel AI с OpenClaw
  - Вам нужна переменная окружения с API-ключом или выбор аутентификации через CLI
---

# Шлюз Vercel AI

[Шлюз Vercel AI](https://vercel.com/ai-gateway) предоставляет унифицированный API для доступа к сотням моделей через единую конечную точку.

- Поставщик: `vercel-ai-gateway`
- Аутентификация: `AI_GATEWAY_API_KEY`
- API: совместим с Anthropic Messages
- OpenClaw автоматически обнаруживает каталог шлюза `/v1/models`, поэтому команда `/models vercel-ai-gateway` включает актуальные ссылки на модели, такие как `vercel-ai-gateway/openai/gpt-5.4`.

## Быстрый старт

1. Задайте API-ключ (рекомендуется сохранить его для шлюза):

```bash
openclaw onboard --auth-choice ai-gateway-api-key
```

2. Задайте модель по умолчанию:

```json5
{
  agents: {
    defaults: {
      model: { primary: "vercel-ai-gateway/anthropic/claude-opus-4.6" },
    },
  },
}
```

## Пример в неинтерактивном режиме

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice ai-gateway-api-key \
  --ai-gateway-api-key "$AI_GATEWAY_API_KEY"
```

## Примечание об окружении

Если шлюз работает как демон (launchd/systemd), убедитесь, что переменная `AI_GATEWAY_API_KEY` доступна для этого процесса (например, в `~/.openclaw/.env` или через `env.shellEnv`).

## Сокращённые идентификаторы моделей

OpenClaw принимает сокращённые ссылки на модели Vercel Claude и нормализует их во время выполнения:

- `vercel-ai-gateway/claude-opus-4.6` → `vercel-ai-gateway/anthropic/claude-opus-4.6`
- `vercel-ai-gateway/opus-4.6` → `vercel-ai-gateway/anthropic/claude-opus-4-6`