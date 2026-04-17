---
read_when:
    - Ви хочете використовувати Arcee AI з OpenClaw
    - Вам потрібна змінна середовища з API-ключем або варіант автентифікації в CLI
summary: Налаштування Arcee AI (автентифікація + вибір моделі)
title: Arcee AI
x-i18n:
    generated_at: "2026-04-12T10:29:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 68c5fddbe272c69611257ceff319c4de7ad21134aaf64582d60720a6f3b853cc
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

[Arcee AI](https://arcee.ai) надає доступ до сімейства моделей Trinity типу mixture-of-experts через API, сумісний з OpenAI. Усі моделі Trinity ліцензовані за Apache 2.0.

До моделей Arcee AI можна отримати доступ безпосередньо через платформу Arcee або через [OpenRouter](/uk/providers/openrouter).

| Властивість | Значення                                                                             |
| ----------- | ------------------------------------------------------------------------------------ |
| Провайдер   | `arcee`                                                                              |
| Автентифікація | `ARCEEAI_API_KEY` (напряму) або `OPENROUTER_API_KEY` (через OpenRouter)           |
| API         | сумісний з OpenAI                                                                    |
| Базовий URL | `https://api.arcee.ai/api/v1` (напряму) або `https://openrouter.ai/api/v1` (OpenRouter) |

## Початок роботи

<Tabs>
  <Tab title="Напряму (платформа Arcee)">
    <Steps>
      <Step title="Отримайте API-ключ">
        Створіть API-ключ у [Arcee AI](https://chat.arcee.ai/).
      </Step>
      <Step title="Запустіть онбординг">
        ```bash
        openclaw onboard --auth-choice arceeai-api-key
        ```
      </Step>
      <Step title="Установіть модель за замовчуванням">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```
      </Step>
    </Steps>
  </Tab>

  <Tab title="Через OpenRouter">
    <Steps>
      <Step title="Отримайте API-ключ">
        Створіть API-ключ у [OpenRouter](https://openrouter.ai/keys).
      </Step>
      <Step title="Запустіть онбординг">
        ```bash
        openclaw onboard --auth-choice arceeai-openrouter
        ```
      </Step>
      <Step title="Установіть модель за замовчуванням">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```

        Ті самі посилання на моделі працюють як для прямого налаштування, так і для налаштування через OpenRouter (наприклад, `arcee/trinity-large-thinking`).
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Неінтерактивне налаштування

<Tabs>
  <Tab title="Напряму (платформа Arcee)">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-api-key \
      --arceeai-api-key "$ARCEEAI_API_KEY"
    ```
  </Tab>

  <Tab title="Через OpenRouter">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-openrouter \
      --openrouter-api-key "$OPENROUTER_API_KEY"
    ```
  </Tab>
</Tabs>

## Вбудований каталог

Наразі OpenClaw постачається з таким вбудованим каталогом Arcee:

| Model ref                      | Назва                  | Вхід | Контекст | Вартість (вхід/вихід за 1M) | Примітки                                  |
| ------------------------------ | ---------------------- | ---- | -------- | --------------------------- | ----------------------------------------- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text | 256K     | $0.25 / $0.90               | Модель за замовчуванням; reasoning увімкнено |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text | 128K     | $0.25 / $1.00               | Загального призначення; 400B параметрів, 13B активних |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text | 128K     | $0.045 / $0.15              | Швидка та економна; виклик функцій |

<Tip>
Початкове налаштування онбордингу встановлює `arcee/trinity-large-thinking` як модель за замовчуванням.
</Tip>

## Підтримувані можливості

| Можливість                                  | Підтримується                |
| ------------------------------------------- | ---------------------------- |
| Потокова передача                           | Так                          |
| Використання інструментів / виклик функцій  | Так                          |
| Структурований вивід (режим JSON і схема JSON) | Так                       |
| Розширене thinking                          | Так (Trinity Large Thinking) |

<AccordionGroup>
  <Accordion title="Примітка щодо середовища">
    Якщо Gateway працює як демон (launchd/systemd), переконайтеся, що `ARCEEAI_API_KEY`
    (або `OPENROUTER_API_KEY`) доступний для цього процесу (наприклад, у
    `~/.openclaw/.env` або через `env.shellEnv`).
  </Accordion>

  <Accordion title="Маршрутизація OpenRouter">
    Під час використання моделей Arcee через OpenRouter застосовуються ті самі посилання на моделі `arcee/*`.
    OpenClaw прозоро обробляє маршрутизацію залежно від вашого вибору автентифікації. Докладніше про конфігурацію,
    специфічну для OpenRouter, див. у
    [документації провайдера OpenRouter](/uk/providers/openrouter).
  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="OpenRouter" href="/uk/providers/openrouter" icon="shuffle">
    Отримуйте доступ до моделей Arcee та багатьох інших за допомогою одного API-ключа.
  </Card>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір провайдерів, посилань на моделі та поведінки резервного перемикання.
  </Card>
</CardGroup>
