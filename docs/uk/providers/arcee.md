---
read_when:
    - Ви хочете використовувати Arcee AI з OpenClaw
    - Вам потрібна змінна середовища ключа API або варіант автентифікації в CLI
summary: Налаштування Arcee AI (автентифікація + вибір моделі)
title: Arcee AI
x-i18n:
    generated_at: "2026-04-06T18:54:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb04909a708fec08dd2c8c863501b178f098bc4818eaebad38aea264157969d8
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

[Arcee AI](https://arcee.ai) надає доступ до сімейства моделей Trinity типу mixture-of-experts через OpenAI-сумісний API. Усі моделі Trinity ліцензовано за Apache 2.0.

До моделей Arcee AI можна отримати доступ безпосередньо через платформу Arcee або через [OpenRouter](/uk/providers/openrouter).

- Провайдер: `arcee`
- Автентифікація: `ARCEEAI_API_KEY` (безпосередньо) або `OPENROUTER_API_KEY` (через OpenRouter)
- API: OpenAI-сумісний
- Базовий URL: `https://api.arcee.ai/api/v1` (безпосередньо) або `https://openrouter.ai/api/v1` (OpenRouter)

## Швидкий старт

1. Отримайте ключ API від [Arcee AI](https://chat.arcee.ai/) або [OpenRouter](https://openrouter.ai/keys).

2. Установіть ключ API (рекомендовано: збережіть його для Gateway):

```bash
# Direct (Arcee platform)
openclaw onboard --auth-choice arceeai-api-key

# Via OpenRouter
openclaw onboard --auth-choice arceeai-openrouter
```

3. Установіть модель за замовчуванням:

```json5
{
  agents: {
    defaults: {
      model: { primary: "arcee/trinity-large-thinking" },
    },
  },
}
```

## Неінтерактивний приклад

```bash
# Direct (Arcee platform)
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-api-key \
  --arceeai-api-key "$ARCEEAI_API_KEY"

# Via OpenRouter
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-openrouter \
  --openrouter-api-key "$OPENROUTER_API_KEY"
```

## Примітка щодо середовища

Якщо Gateway працює як демон (launchd/systemd), переконайтеся, що `ARCEEAI_API_KEY`
(або `OPENROUTER_API_KEY`) доступний для цього процесу (наприклад, у
`~/.openclaw/.env` або через `env.shellEnv`).

## Вбудований каталог

Наразі OpenClaw постачається з таким вбудованим каталогом Arcee:

| Посилання на модель            | Назва                  | Вхід  | Контекст | Вартість (вхід/вихід за 1 млн) | Примітки                                  |
| ------------------------------ | ---------------------- | ----- | -------- | ------------------------------ | ----------------------------------------- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text  | 256K     | $0.25 / $0.90                  | Модель за замовчуванням; reasoning увімкнено |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text  | 128K     | $0.25 / $1.00                  | Загального призначення; 400B параметрів, 13B active |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text  | 128K     | $0.045 / $0.15                 | Швидка та економна; виклик функцій        |

Ті самі посилання на моделі працюють як для прямого налаштування, так і для налаштування через OpenRouter (наприклад, `arcee/trinity-large-thinking`).

Початкове налаштування встановлює `arcee/trinity-large-thinking` як модель за замовчуванням.

## Підтримувані можливості

- Потокова передача
- Використання інструментів / виклик функцій
- Структурований вивід (режим JSON і схема JSON)
- Розширене thinking (Trinity Large Thinking)
