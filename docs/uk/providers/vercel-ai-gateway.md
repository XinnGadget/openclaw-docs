---
read_when:
    - Ви хочете використовувати Vercel AI Gateway з OpenClaw
    - Вам потрібна змінна середовища ключа API або варіант автентифікації в CLI
summary: Налаштування Vercel AI Gateway (автентифікація + вибір моделі)
title: Vercel AI Gateway
x-i18n:
    generated_at: "2026-04-12T10:36:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 48c206a645d7a62e201a35ae94232323c8570fdae63129231c38d363ea78a60b
    source_path: providers/vercel-ai-gateway.md
    workflow: 15
---

# Vercel AI Gateway

[Vercel AI Gateway](https://vercel.com/ai-gateway) надає уніфікований API для доступу
до сотень моделей через єдину кінцеву точку.

| Властивість   | Значення                        |
| ------------- | ------------------------------- |
| Провайдер     | `vercel-ai-gateway`             |
| Автентифікація | `AI_GATEWAY_API_KEY`            |
| API           | сумісний з Anthropic Messages   |
| Каталог моделей | автоматично виявляється через `/v1/models` |

<Tip>
OpenClaw автоматично виявляє каталог Gateway `/v1/models`, тому
`/models vercel-ai-gateway` містить актуальні посилання на моделі, як-от
`vercel-ai-gateway/openai/gpt-5.4`.
</Tip>

## Початок роботи

<Steps>
  <Step title="Встановіть ключ API">
    Запустіть онбординг і виберіть варіант автентифікації AI Gateway:

    ```bash
    openclaw onboard --auth-choice ai-gateway-api-key
    ```

  </Step>
  <Step title="Встановіть модель за замовчуванням">
    Додайте модель до вашої конфігурації OpenClaw:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "vercel-ai-gateway/anthropic/claude-opus-4.6" },
        },
      },
    }
    ```

  </Step>
  <Step title="Перевірте, що модель доступна">
    ```bash
    openclaw models list --provider vercel-ai-gateway
    ```
  </Step>
</Steps>

## Неінтерактивний приклад

Для налаштувань через скрипти або в CI передайте всі значення в командному рядку:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice ai-gateway-api-key \
  --ai-gateway-api-key "$AI_GATEWAY_API_KEY"
```

## Скорочений запис ID моделі

OpenClaw приймає скорочені посилання на моделі Vercel Claude і нормалізує їх
під час виконання:

| Скорочений ввід                    | Нормалізоване посилання на модель             |
| ---------------------------------- | --------------------------------------------- |
| `vercel-ai-gateway/claude-opus-4.6` | `vercel-ai-gateway/anthropic/claude-opus-4.6` |
| `vercel-ai-gateway/opus-4.6`        | `vercel-ai-gateway/anthropic/claude-opus-4-6` |

<Tip>
У вашій конфігурації можна використовувати як скорочений запис, так і повне
посилання на модель. OpenClaw автоматично визначає канонічну форму.
</Tip>

## Додаткові примітки

<AccordionGroup>
  <Accordion title="Змінна середовища для процесів-демонів">
    Якщо Gateway OpenClaw працює як демон (launchd/systemd), переконайтеся, що
    `AI_GATEWAY_API_KEY` доступна для цього процесу.

    <Warning>
    Ключ, заданий лише в `~/.profile`, не буде видимий демону launchd/systemd,
    якщо це середовище не імпортовано явно. Задайте ключ у
    `~/.openclaw/.env` або через `env.shellEnv`, щоб процес gateway міг
    його прочитати.
    </Warning>

  </Accordion>

  <Accordion title="Маршрутизація провайдера">
    Vercel AI Gateway маршрутизує запити до висхідного провайдера на основі
    префікса посилання на модель. Наприклад, `vercel-ai-gateway/anthropic/claude-opus-4.6` маршрутизується
    через Anthropic, а `vercel-ai-gateway/openai/gpt-5.4` — через
    OpenAI. Ваш єдиний `AI_GATEWAY_API_KEY` забезпечує автентифікацію для всіх
    висхідних провайдерів.
  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір провайдерів, посилань на моделі та поведінки резервного перемикання.
  </Card>
  <Card title="Усунення несправностей" href="/uk/help/troubleshooting" icon="wrench">
    Загальне усунення несправностей і поширені запитання.
  </Card>
</CardGroup>
