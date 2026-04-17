---
read_when:
    - Ви хочете використовувати моделі Anthropic в OpenClaw
summary: Використовуйте Anthropic Claude через API-ключі або Claude CLI в OpenClaw
title: Anthropic
x-i18n:
    generated_at: "2026-04-12T11:08:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5e3dda5f98ade9d4c3841888103bfb43d59e075d358a701ed0ae3ffb8d5694a7
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

Anthropic створює сімейство моделей **Claude**. OpenClaw підтримує два шляхи автентифікації:

- **API key** — прямий доступ до API Anthropic з тарифікацією за використання (`anthropic/*` моделі)
- **Claude CLI** — повторне використання наявного входу Claude CLI на тому самому хості

<Warning>
Співробітники Anthropic повідомили нам, що використання Claude CLI у стилі OpenClaw знову дозволене, тож
OpenClaw вважає повторне використання Claude CLI та використання `claude -p` санкціонованими, якщо
Anthropic не опублікує нову політику.

Для довготривалих хостів Gateway API-ключі Anthropic усе ще є найзрозумілішим і
найпередбачуванішим шляхом для production.

Поточна публічна документація Anthropic:

- [Довідка з Claude Code CLI](https://code.claude.com/docs/en/cli-reference)
- [Огляд Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Використання Claude Code з вашим планом Pro або Max](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Використання Claude Code з вашим планом Team або Enterprise](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)
  </Warning>

## Початок роботи

<Tabs>
  <Tab title="API key">
    **Найкраще підходить для:** стандартного доступу до API і тарифікації за використання.

    <Steps>
      <Step title="Отримайте свій API key">
        Створіть API key у [Anthropic Console](https://console.anthropic.com/).
      </Step>
      <Step title="Запустіть онбординг">
        ```bash
        openclaw onboard
        # choose: Anthropic API key
        ```

        Або передайте ключ напряму:

        ```bash
        openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
        ```
      </Step>
      <Step title="Переконайтеся, що модель доступна">
        ```bash
        openclaw models list --provider anthropic
        ```
      </Step>
    </Steps>

    ### Приклад конфігурації

    ```json5
    {
      env: { ANTHROPIC_API_KEY: "sk-ant-..." },
      agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
    }
    ```

  </Tab>

  <Tab title="Claude CLI">
    **Найкраще підходить для:** повторного використання наявного входу Claude CLI без окремого API key.

    <Steps>
      <Step title="Переконайтеся, що Claude CLI встановлено і в ньому виконано вхід">
        Перевірте командою:

        ```bash
        claude --version
        ```
      </Step>
      <Step title="Запустіть онбординг">
        ```bash
        openclaw onboard
        # choose: Claude CLI
        ```

        OpenClaw виявляє та повторно використовує наявні облікові дані Claude CLI.
      </Step>
      <Step title="Переконайтеся, що модель доступна">
        ```bash
        openclaw models list --provider anthropic
        ```
      </Step>
    </Steps>

    <Note>
    Подробиці налаштування та виконання для бекенда Claude CLI наведено в [CLI Backends](/uk/gateway/cli-backends).
    </Note>

    <Tip>
    Якщо вам потрібен найпрозоріший шлях тарифікації, натомість використовуйте API key Anthropic. OpenClaw також підтримує варіанти на основі підписки від [OpenAI Codex](/uk/providers/openai), [Qwen Cloud](/uk/providers/qwen), [MiniMax](/uk/providers/minimax) і [Z.AI / GLM](/uk/providers/glm).
    </Tip>

  </Tab>
</Tabs>

## Значення thinking за замовчуванням (Claude 4.6)

Для моделей Claude 4.6 в OpenClaw значення thinking за замовчуванням — `adaptive`, якщо явний рівень thinking не встановлено.

Перевизначте для окремого повідомлення через `/think:<level>` або в параметрах моделі:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { thinking: "adaptive" },
        },
      },
    },
  },
}
```

<Note>
Пов’язана документація Anthropic:
- [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
- [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
</Note>

## Кешування prompt

OpenClaw підтримує функцію кешування prompt від Anthropic для автентифікації через API key.

| Значення            | Тривалість кешу | Опис                                     |
| ------------------- | --------------- | ---------------------------------------- |
| `"short"` (типово)  | 5 хвилин        | Застосовується автоматично для автентифікації через API key |
| `"long"`            | 1 година        | Розширений кеш                           |
| `"none"`            | Без кешування   | Вимкнути кешування prompt                |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Перевизначення кешу для окремих агентів">
    Використовуйте параметри на рівні моделі як базу, а потім перевизначайте для конкретних агентів через `agents.list[].params`:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": {
              params: { cacheRetention: "long" },
            },
          },
        },
        list: [
          { id: "research", default: true },
          { id: "alerts", params: { cacheRetention: "none" } },
        ],
      },
    }
    ```

    Порядок об’єднання конфігурації:

    1. `agents.defaults.models["provider/model"].params`
    2. `agents.list[].params` (відповідний `id`, перевизначає за ключем)

    Це дає змогу одному агенту зберігати довготривалий кеш, тоді як інший агент на тій самій моделі вимикає кешування для імпульсного трафіку або трафіку з низьким повторним використанням.

  </Accordion>

  <Accordion title="Примітки щодо Bedrock Claude">
    - Моделі Anthropic Claude у Bedrock (`amazon-bedrock/*anthropic.claude*`) приймають наскрізну передачу `cacheRetention`, якщо її налаштовано.
    - Для моделей Bedrock, що не належать Anthropic, під час виконання примусово встановлюється `cacheRetention: "none"`.
    - Розумні типові значення для API key також ініціалізують `cacheRetention: "short"` для посилань Claude-on-Bedrock, якщо явне значення не задано.
  </Accordion>
</AccordionGroup>

## Розширена конфігурація

<AccordionGroup>
  <Accordion title="Швидкий режим">
    Спільний перемикач `/fast` в OpenClaw підтримує прямий трафік Anthropic (API key і OAuth до `api.anthropic.com`).

    | Команда | Відображається на |
    |---------|-------------------|
    | `/fast on` | `service_tier: "auto"` |
    | `/fast off` | `service_tier: "standard_only"` |

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "anthropic/claude-sonnet-4-6": {
              params: { fastMode: true },
            },
          },
        },
      },
    }
    ```

    <Note>
    - Вставляється лише для прямих запитів до `api.anthropic.com`. Маршрути через проксі залишають `service_tier` без змін.
    - Явні параметри `serviceTier` або `service_tier` мають пріоритет над `/fast`, якщо встановлено обидва.
    - Для облікових записів без місткості Priority Tier значення `service_tier: "auto"` може визначитися як `standard`.
    </Note>

  </Accordion>

  <Accordion title="Розуміння медіа (зображення та PDF)">
    Вбудований Plugin Anthropic реєструє розуміння зображень і PDF. OpenClaw
    автоматично визначає медіа-можливості з налаштованої автентифікації Anthropic —
    додаткова конфігурація не потрібна.

    | Property       | Value                |
    | -------------- | -------------------- |
    | Default model  | `claude-opus-4-6`    |
    | Supported input | Images, PDF documents |

    Коли зображення або PDF додається до розмови, OpenClaw автоматично
    маршрутизує його через провайдера розуміння медіа Anthropic.

  </Accordion>

  <Accordion title="Вікно контексту 1M (бета)">
    Вікно контексту 1M від Anthropic доступне лише в межах beta. Увімкніть його для окремої моделі:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "anthropic/claude-opus-4-6": {
              params: { context1m: true },
            },
          },
        },
      },
    }
    ```

    OpenClaw відображає це в `anthropic-beta: context-1m-2025-08-07` у запитах.

    <Warning>
    Потрібен доступ до довгого контексту для ваших облікових даних Anthropic. Застаріла автентифікація токеном (`sk-ant-oat-*`) відхиляється для запитів із контекстом 1M — OpenClaw записує попередження в журнал і повертається до стандартного вікна контексту.
    </Warning>

  </Accordion>
</AccordionGroup>

## Усунення несправностей

<AccordionGroup>
  <Accordion title="Помилки 401 / токен раптово став недійсним">
    Автентифікація токеном Anthropic може завершитися або бути відкликана. Для нових налаштувань перейдіть на API key Anthropic.
  </Accordion>

  <Accordion title='API key не знайдено для провайдера "anthropic"'>
    Автентифікація є **для кожного агента окремо**. Нові агенти не успадковують ключі головного агента. Повторно запустіть онбординг для цього агента або налаштуйте API key на хості Gateway, а потім перевірте через `openclaw models status`.
  </Accordion>

  <Accordion title='Облікові дані для профілю "anthropic:default" не знайдено'>
    Запустіть `openclaw models status`, щоб побачити, який профіль автентифікації активний. Повторно запустіть онбординг або налаштуйте API key для шляху цього профілю.
  </Accordion>

  <Accordion title="Немає доступного профілю автентифікації (усі в cooldown)">
    Перевірте `openclaw models status --json` для `auth.unusableProfiles`. Cooldown через обмеження швидкості Anthropic може бути прив’язаний до моделі, тому споріднена модель Anthropic все ще може бути придатною до використання. Додайте інший профіль Anthropic або дочекайтеся завершення cooldown.
  </Accordion>
</AccordionGroup>

<Note>
Більше довідки: [Усунення несправностей](/uk/help/troubleshooting) і [FAQ](/uk/help/faq).
</Note>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір провайдерів, посилань на моделі та поведінки failover.
  </Card>
  <Card title="CLI backends" href="/uk/gateway/cli-backends" icon="terminal">
    Налаштування бекенда Claude CLI та подробиці виконання.
  </Card>
  <Card title="Кешування prompt" href="/uk/reference/prompt-caching" icon="database">
    Як працює кешування prompt у різних провайдерів.
  </Card>
  <Card title="OAuth та автентифікація" href="/uk/gateway/authentication" icon="key">
    Подробиці автентифікації та правила повторного використання облікових даних.
  </Card>
</CardGroup>
