---
title: "Cloudflare AI Gateway"
summary: "Настройка Cloudflare AI Gateway (аутентификация + выбор модели)"
read_when:
  - Вы хотите использовать Cloudflare AI Gateway с OpenClaw
  - Вам нужен ID аккаунта, ID шлюза или переменная окружения с API-ключом
---

# Cloudflare AI Gateway

Cloudflare AI Gateway располагается перед API провайдеров и позволяет добавлять аналитику, кэширование и средства управления. Для Anthropic OpenClaw использует API Anthropic Messages через вашу конечную точку шлюза.

- Провайдер: `cloudflare-ai-gateway`
- Базовый URL: `https://gateway.ai.cloudflare.com/v1/<account_id>/<gateway_id>/anthropic`
- Модель по умолчанию: `cloudflare-ai-gateway/claude-sonnet-4-5`
- API-ключ: `CLOUDFLARE_AI_GATEWAY_API_KEY` (ваш API-ключ провайдера для запросов через шлюз)

Для моделей Anthropic используйте ваш API-ключ Anthropic.

## Быстрый старт

1. Задайте API-ключ провайдера и параметры шлюза:

```bash
openclaw onboard --auth-choice cloudflare-ai-gateway-api-key
```

2. Задайте модель по умолчанию:

```json5
{
  agents: {
    defaults: {
      model: { primary: "cloudflare-ai-gateway/claude-sonnet-4-5" },
    },
  },
}
```

## Пример без интерактивного режима

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice cloudflare-ai-gateway-api-key \
  --cloudflare-ai-gateway-account-id "your-account-id" \
  --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
  --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY"
```

## Аутентифицированные шлюзы

Если вы включили аутентификацию шлюза в Cloudflare, добавьте заголовок `cf-aig-authorization` (это дополнительно к вашему API-ключу провайдера).

```json5
{
  models: {
    providers: {
      "cloudflare-ai-gateway": {
        headers: {
          "cf-aig-authorization": "Bearer <cloudflare-ai-gateway-token>",
        },
      },
    },
  },
}
```

## Примечание об окружении

Если шлюз работает как демон (launchd/systemd), убедитесь, что `CLOUDFLARE_AI_GATEWAY_API_KEY` доступен для этого процесса (например, в `~/.openclaw/.env` или через `env.shellEnv`).