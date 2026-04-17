---
read_when:
    - Ви хочете використовувати GitHub Copilot як постачальника моделей
    - Вам потрібен потік `openclaw models auth login-github-copilot`
summary: Увійдіть у GitHub Copilot з OpenClaw за допомогою потоку пристрою
title: GitHub Copilot
x-i18n:
    generated_at: "2026-04-15T09:41:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: b8258fecff22fb73b057de878462941f6eb86d0c5f775c5eac4840e95ba5eccf
    source_path: providers/github-copilot.md
    workflow: 15
---

# GitHub Copilot

GitHub Copilot — це помічник для програмування з ШІ від GitHub. Він надає доступ до моделей Copilot для вашого облікового запису GitHub і тарифного плану. OpenClaw може використовувати Copilot як постачальника моделей двома різними способами.

## Два способи використання Copilot в OpenClaw

<Tabs>
  <Tab title="Вбудований постачальник (github-copilot)">
    Використовуйте нативний потік входу через пристрій, щоб отримати токен GitHub, а потім обміняти його на токени API Copilot під час роботи OpenClaw. Це **типовий** і найпростіший шлях, оскільки він не потребує VS Code.

    <Steps>
      <Step title="Запустіть команду входу">
        ```bash
        openclaw models auth login-github-copilot
        ```

        Вам буде запропоновано перейти за URL-адресою та ввести одноразовий код. Тримайте
        термінал відкритим, доки процес не завершиться.
      </Step>
      <Step title="Установіть типову модель">
        ```bash
        openclaw models set github-copilot/gpt-4o
        ```

        Або в config:

        ```json5
        {
          agents: { defaults: { model: { primary: "github-copilot/gpt-4o" } } },
        }
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Plugin Copilot Proxy (copilot-proxy)">
    Використовуйте розширення VS Code **Copilot Proxy** як локальний міст. OpenClaw звертається до
    endpoint `/v1` проксі та використовує список моделей, який ви там налаштуєте.

    <Note>
    Вибирайте цей варіант, якщо ви вже запускаєте Copilot Proxy у VS Code або вам потрібно маршрутизувати
    через нього. Ви маєте ввімкнути Plugin і підтримувати роботу розширення VS Code.
    </Note>

  </Tab>
</Tabs>

## Необов’язкові прапорці

| Flag            | Опис                                                |
| --------------- | --------------------------------------------------- |
| `--yes`         | Пропустити запит підтвердження                      |
| `--set-default` | Також застосувати рекомендовану типову модель постачальника |

```bash
# Пропустити підтвердження
openclaw models auth login-github-copilot --yes

# Увійти й установити типову модель за один крок
openclaw models auth login --provider github-copilot --method device --set-default
```

<AccordionGroup>
  <Accordion title="Потрібен інтерактивний TTY">
    Потік входу через пристрій потребує інтерактивного TTY. Запускайте його безпосередньо в
    терміналі, а не в неінтерактивному скрипті чи конвеєрі CI.
  </Accordion>

  <Accordion title="Доступність моделей залежить від вашого тарифного плану">
    Доступність моделей Copilot залежить від вашого тарифного плану GitHub. Якщо модель
    відхиляється, спробуйте інший ID (наприклад, `github-copilot/gpt-4.1`).
  </Accordion>

  <Accordion title="Вибір транспорту">
    Ідентифікатори моделей Claude автоматично використовують транспорт Anthropic Messages. Моделі GPT,
    o-series і Gemini зберігають транспорт OpenAI Responses. OpenClaw
    вибирає правильний транспорт на основі посилання на модель.
  </Accordion>

  <Accordion title="Порядок пріоритету змінних середовища">
    OpenClaw визначає автентифікацію Copilot зі змінних середовища в такому
    порядку пріоритету:

    | Priority | Variable              | Примітки                         |
    | -------- | --------------------- | -------------------------------- |
    | 1        | `COPILOT_GITHUB_TOKEN` | Найвищий пріоритет, спеціально для Copilot |
    | 2        | `GH_TOKEN`            | Токен GitHub CLI (резервний варіант) |
    | 3        | `GITHUB_TOKEN`        | Стандартний токен GitHub (найнижчий пріоритет) |

    Коли задано кілька змінних, OpenClaw використовує ту, що має найвищий пріоритет.
    Потік входу через пристрій (`openclaw models auth login-github-copilot`) зберігає
    свій токен у сховищі профілів автентифікації та має пріоритет над усіма змінними
    середовища.

  </Accordion>

  <Accordion title="Зберігання токенів">
    Під час входу токен GitHub зберігається у сховищі профілів автентифікації та обмінюється
    на токен API Copilot під час роботи OpenClaw. Вам не потрібно керувати
    токеном вручну.
  </Accordion>
</AccordionGroup>

<Warning>
Потрібен інтерактивний TTY. Запускайте команду входу безпосередньо в терміналі, а не
всередині безголового скрипту чи завдання CI.
</Warning>

## Ембедінги для пошуку в пам’яті

GitHub Copilot також може слугувати постачальником ембедінгів для
[пошуку в пам’яті](/uk/concepts/memory-search). Якщо у вас є підписка Copilot і
ви вже ввійшли, OpenClaw може використовувати його для ембедінгів без окремого API-ключа.

### Автовизначення

Коли `memorySearch.provider` має значення `"auto"` (типово), GitHub Copilot перевіряється
з пріоритетом 15 — після локальних ембедінгів, але перед OpenAI та іншими платними
постачальниками. Якщо токен GitHub доступний, OpenClaw визначає доступні
моделі ембедінгів через API Copilot і автоматично вибирає найкращу.

### Явна конфігурація

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "github-copilot",
        // Необов’язково: перевизначити автоматично виявлену модель
        model: "text-embedding-3-small",
      },
    },
  },
}
```

### Як це працює

1. OpenClaw визначає ваш токен GitHub (зі змінних середовища або профілю автентифікації).
2. Обмінює його на короткоживучий токен API Copilot.
3. Надсилає запит до endpoint Copilot `/models`, щоб визначити доступні моделі ембедінгів.
4. Вибирає найкращу модель (надає перевагу `text-embedding-3-small`).
5. Надсилає запити на ембедінги до endpoint Copilot `/embeddings`.

Доступність моделей залежить від вашого тарифного плану GitHub. Якщо моделі ембедінгів
недоступні, OpenClaw пропускає Copilot і переходить до наступного постачальника.

## Пов’язане

<CardGroup cols={2}>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір постачальників, посилань на моделі та поведінки резервного перемикання.
  </Card>
  <Card title="OAuth та автентифікація" href="/uk/gateway/authentication" icon="key">
    Відомості про автентифікацію та правила повторного використання облікових даних.
  </Card>
</CardGroup>
