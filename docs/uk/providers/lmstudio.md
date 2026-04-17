---
read_when:
    - Ви хочете запустити OpenClaw з моделями з відкритим кодом через LM Studio
    - Ви хочете налаштувати й сконфігурувати LM Studio
summary: Запустіть OpenClaw з LM Studio
title: LM Studio
x-i18n:
    generated_at: "2026-04-13T07:24:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 11264584e8277260d4215feb7c751329ce04f59e9228da1c58e147c21cd9ac2c
    source_path: providers/lmstudio.md
    workflow: 15
---

# LM Studio

LM Studio — це зручна, але водночас потужна програма для запуску моделей з відкритими вагами на власному обладнанні. Вона дає змогу запускати моделі llama.cpp (GGUF) або MLX (Apple Silicon). Доступна як GUI-пакет або headless-демон (`llmster`). Документацію про продукт і налаштування дивіться на [lmstudio.ai](https://lmstudio.ai/).

## Швидкий старт

1. Встановіть LM Studio (desktop) або `llmster` (headless), а потім запустіть локальний сервер:

```bash
curl -fsSL https://lmstudio.ai/install.sh | bash
```

2. Запустіть сервер

Переконайтеся, що ви або запустили desktop-застосунок, або запустили демон за допомогою такої команди:

```bash
lms daemon up
```

```bash
lms server start --port 1234
```

Якщо ви використовуєте застосунок, переконайтеся, що у вас увімкнено JIT для плавної роботи. Докладніше дивіться в [посібнику LM Studio про JIT і TTL](https://lmstudio.ai/docs/developer/core/ttl-and-auto-evict).

3. OpenClaw потребує значення токена LM Studio. Задайте `LM_API_TOKEN`:

```bash
export LM_API_TOKEN="your-lm-studio-api-token"
```

Якщо в LM Studio автентифікацію вимкнено, використайте будь-яке непорожнє значення токена:

```bash
export LM_API_TOKEN="placeholder-key"
```

Докладніше про налаштування автентифікації LM Studio дивіться в [LM Studio Authentication](https://lmstudio.ai/docs/developer/core/authentication).

4. Запустіть онбординг і виберіть `LM Studio`:

```bash
openclaw onboard
```

5. Під час онбордингу використайте запит `Default model`, щоб вибрати свою модель LM Studio.

Ви також можете встановити або змінити її пізніше:

```bash
openclaw models set lmstudio/qwen/qwen3.5-9b
```

Ключі моделей LM Studio мають формат `author/model-name` (наприклад, `qwen/qwen3.5-9b`). У посиланнях на моделі OpenClaw додається префікс імені провайдера: `lmstudio/qwen/qwen3.5-9b`. Точний ключ моделі можна знайти, виконавши `curl http://localhost:1234/api/v1/models` і переглянувши поле `key`.

## Неінтерактивний онбординг

Використовуйте неінтерактивний онбординг, якщо хочете автоматизувати налаштування (CI, provisioning, віддалений bootstrap):

```bash
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --auth-choice lmstudio
```

Або вкажіть base URL чи модель разом з API-ключем:

```bash
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --auth-choice lmstudio \
  --custom-base-url http://localhost:1234/v1 \
  --lmstudio-api-key "$LM_API_TOKEN" \
  --custom-model-id qwen/qwen3.5-9b
```

`--custom-model-id` приймає ключ моделі, який повертає LM Studio (наприклад, `qwen/qwen3.5-9b`), без префікса провайдера `lmstudio/`.

Неінтерактивний онбординг потребує `--lmstudio-api-key` (або `LM_API_TOKEN` у змінних середовища).
Для серверів LM Studio без автентифікації підійде будь-яке непорожнє значення токена.

`--custom-api-key` і далі підтримується для сумісності, але для LM Studio рекомендовано `--lmstudio-api-key`.

Це записує `models.providers.lmstudio`, встановлює модель за замовчуванням у значення
`lmstudio/<custom-model-id>` і записує профіль автентифікації `lmstudio:default`.

Інтерактивне налаштування може запропонувати вказати необов’язкову бажану довжину контексту завантаження та застосовує її до виявлених моделей LM Studio, які зберігає в конфігурації.

## Конфігурація

### Явна конфігурація

```json5
{
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "${LM_API_TOKEN}",
        api: "openai-completions",
        models: [
          {
            id: "qwen/qwen3-coder-next",
            name: "Qwen 3 Coder Next",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## Усунення неполадок

### LM Studio не виявлено

Переконайтеся, що LM Studio запущено і що ви задали `LM_API_TOKEN` (для серверів без автентифікації підійде будь-яке непорожнє значення токена):

```bash
# Запустіть через desktop-застосунок або в headless-режимі:
lms server start --port 1234
```

Перевірте, що API доступний:

```bash
curl http://localhost:1234/api/v1/models
```

### Помилки автентифікації (HTTP 401)

Якщо під час налаштування з’являється HTTP 401, перевірте свій API-ключ:

- Переконайтеся, що `LM_API_TOKEN` збігається з ключем, налаштованим у LM Studio.
- Докладніше про налаштування автентифікації LM Studio дивіться в [LM Studio Authentication](https://lmstudio.ai/docs/developer/core/authentication).
- Якщо ваш сервер не вимагає автентифікації, використайте будь-яке непорожнє значення токена для `LM_API_TOKEN`.

### Завантаження моделей just-in-time

LM Studio підтримує завантаження моделей just-in-time (JIT), коли моделі завантажуються під час першого запиту. Переконайтеся, що це ввімкнено, щоб уникнути помилок на кшталт 'Model not loaded'.
