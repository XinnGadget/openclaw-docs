---
summary: "Использовать модели Xiaomi MiMo с OpenClaw"
read_when:
  - Вам нужны модели Xiaomi MiMo в OpenClaw
  - Вам необходимо настроить XIAOMI_API_KEY
title: "Xiaomi MiMo"
---

# Xiaomi MiMo

Xiaomi MiMo — это API-платформа для моделей **MiMo**. OpenClaw использует совместимую с OpenAI конечную точку Xiaomi с аутентификацией по API-ключу. Создайте свой API-ключ в [консоли Xiaomi MiMo](https://platform.xiaomimimo.com/#/console/api-keys), затем настройте встроенный провайдер `xiaomi` с этим ключом.

## Встроенный каталог

- Базовый URL: `https://api.xiaomimimo.com/v1`
- API: `openai-completions`
- Авторизация: `Bearer $XIAOMI_API_KEY`

| Ссылка на модель | Входные данные | Контекст | Максимальный объём вывода | Примечания |
| --- | --- | --- | --- | --- |
| `xiaomi/mimo-v2-flash` | текст | 262 144 | 8 192 | Модель по умолчанию |
| `xiaomi/mimo-v2-pro` | текст | 1 048 576 | 32 000 | С поддержкой рассуждений |
| `xiaomi/mimo-v2-omni` | текст, изображение | 262 144 | 32 000 | Мультимодальная модель с поддержкой рассуждений |

## Настройка через CLI

```bash
openclaw onboard --auth-choice xiaomi-api-key
# или в неинтерактивном режиме
openclaw onboard --auth-choice xiaomi-api-key --xiaomi-api-key "$XIAOMI_API_KEY"
```

## Фрагмент конфигурации

```json5
{
  env: { XIAOMI_API_KEY: "your-key" },
  agents: { defaults: { model: { primary: "xiaomi/mimo-v2-flash" } } },
  models: {
    mode: "merge",
    providers: {
      xiaomi: {
        baseUrl: "https://api.xiaomimimo.com/v1",
        api: "openai-completions",
        apiKey: "XIAOMI_API_KEY",
        models: [
          {
            id: "mimo-v2-flash",
            name: "Xiaomi MiMo V2 Flash",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 8192,
          },
          {
            id: "mimo-v2-pro",
            name: "Xiaomi MiMo V2 Pro",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 1048576,
            maxTokens: 32000,
          },
          {
            id: "mimo-v2-omni",
            name: "Xiaomi MiMo V2 Omni",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

## Примечания

- Ссылка на модель по умолчанию: `xiaomi/mimo-v2-flash`.
- Дополнительные встроенные модели: `xiaomi/mimo-v2-pro`, `xiaomi/mimo-v2-omni`.
- Провайдер внедряется автоматически, когда задан `XIAOMI_API_KEY` (или существует профиль аутентификации).
- См. [/concepts/model-providers](/concepts/model-providers) для ознакомления с правилами работы провайдеров.