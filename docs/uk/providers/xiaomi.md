---
read_when:
    - Ви хочете моделі Xiaomi MiMo в OpenClaw
    - Вам потрібно налаштувати `XIAOMI_API_KEY`
summary: Використовуйте моделі Xiaomi MiMo з OpenClaw
title: Xiaomi MiMo
x-i18n:
    generated_at: "2026-04-12T10:29:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: cd5a526764c796da7e1fff61301bc2ec618e1cf3857894ba2ef4b6dd9c4dc339
    source_path: providers/xiaomi.md
    workflow: 15
---

# Xiaomi MiMo

Xiaomi MiMo — це API-платформа для моделей **MiMo**. OpenClaw використовує Xiaomi
OpenAI-сумісну кінцеву точку з автентифікацією за API-ключем.

| Властивість | Значення                       |
| ----------- | ------------------------------ |
| Постачальник | `xiaomi`                       |
| Автентифікація | `XIAOMI_API_KEY`             |
| API         | OpenAI-сумісний                |
| Базовий URL | `https://api.xiaomimimo.com/v1` |

## Початок роботи

<Steps>
  <Step title="Отримайте API-ключ">
    Створіть API-ключ у [консолі Xiaomi MiMo](https://platform.xiaomimimo.com/#/console/api-keys).
  </Step>
  <Step title="Запустіть онбординг">
    ```bash
    openclaw onboard --auth-choice xiaomi-api-key
    ```

    Або передайте ключ безпосередньо:

    ```bash
    openclaw onboard --auth-choice xiaomi-api-key --xiaomi-api-key "$XIAOMI_API_KEY"
    ```

  </Step>
  <Step title="Перевірте, що модель доступна">
    ```bash
    openclaw models list --provider xiaomi
    ```
  </Step>
</Steps>

## Доступні моделі

| Посилання на модель     | Вхідні дані | Контекст  | Макс. вивід | Міркування | Примітки      |
| ----------------------- | ----------- | --------- | ----------- | ---------- | ------------- |
| `xiaomi/mimo-v2-flash` | text        | 262,144   | 8,192       | Ні         | Модель за замовчуванням |
| `xiaomi/mimo-v2-pro`   | text        | 1,048,576 | 32,000      | Так        | Великий контекст |
| `xiaomi/mimo-v2-omni`  | text, image | 262,144   | 32,000      | Так        | Мультимодальна |

<Tip>
Посилання на модель за замовчуванням — `xiaomi/mimo-v2-flash`. Постачальник додається автоматично, коли встановлено `XIAOMI_API_KEY` або існує профіль автентифікації.
</Tip>

## Приклад конфігурації

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

<AccordionGroup>
  <Accordion title="Поведінка автоматичного додавання">
    Постачальник `xiaomi` додається автоматично, коли у вашому середовищі встановлено `XIAOMI_API_KEY` або існує профіль автентифікації. Вам не потрібно вручну налаштовувати постачальника, якщо тільки ви не хочете перевизначити метадані моделі або базовий URL.
  </Accordion>

  <Accordion title="Відомості про моделі">
    - **mimo-v2-flash** — легка й швидка модель, ідеальна для текстових завдань загального призначення. Підтримка міркувань відсутня.
    - **mimo-v2-pro** — підтримує міркування з контекстним вікном на 1M токенів для навантажень із довгими документами.
    - **mimo-v2-omni** — мультимодальна модель із підтримкою міркувань, що приймає як текстові, так і графічні вхідні дані.

    <Note>
    Усі моделі використовують префікс `xiaomi/` (наприклад, `xiaomi/mimo-v2-pro`).
    </Note>

  </Accordion>

  <Accordion title="Усунення несправностей">
    - Якщо моделі не з’являються, переконайтеся, що `XIAOMI_API_KEY` встановлено і він дійсний.
    - Коли Gateway працює як демон, переконайтеся, що ключ доступний цьому процесу (наприклад, у `~/.openclaw/.env` або через `env.shellEnv`).

    <Warning>
    Ключі, встановлені лише у вашій інтерактивній оболонці, не видимі для процесів Gateway, якими керує демон. Для постійної доступності використовуйте `~/.openclaw/.env` або конфігурацію `env.shellEnv`.
    </Warning>

  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір постачальників, посилань на моделі та поведінки резервного перемикання.
  </Card>
  <Card title="Довідник з конфігурації" href="/uk/gateway/configuration" icon="gear">
    Повний довідник із конфігурації OpenClaw.
  </Card>
  <Card title="Консоль Xiaomi MiMo" href="https://platform.xiaomimimo.com" icon="arrow-up-right-from-square">
    Панель Xiaomi MiMo та керування API-ключами.
  </Card>
</CardGroup>
