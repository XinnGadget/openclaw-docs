---
read_when:
    - Ви хочете орієнтований на конфіденційність інференс у OpenClaw
    - Вам потрібні вказівки щодо налаштування Venice AI
summary: Використовуйте моделі Venice AI, орієнтовані на конфіденційність, в OpenClaw
title: Venice AI
x-i18n:
    generated_at: "2026-04-12T10:03:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6f8005edb1d7781316ce8b5432bf4f9375c16113594a2a588912dce82234a9e5
    source_path: providers/venice.md
    workflow: 15
---

# Venice AI

Venice AI надає **орієнтований на конфіденційність AI-інференс** із підтримкою нецензурованих моделей і доступом до основних пропрієтарних моделей через їхній анонімізований проксі. Увесь інференс є приватним за замовчуванням — без навчання на ваших даних і без журналювання.

## Чому Venice в OpenClaw

- **Приватний інференс** для моделей з відкритим кодом (без журналювання).
- **Нецензуровані моделі**, коли вони вам потрібні.
- **Анонімізований доступ** до пропрієтарних моделей (Opus/GPT/Gemini), коли важлива якість.
- OpenAI-сумісні кінцеві точки `/v1`.

## Режими конфіденційності

Venice пропонує два рівні конфіденційності — розуміння цього є ключовим для вибору вашої моделі:

| Режим          | Опис                                                                                                                             | Моделі                                                        |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Private**    | Повністю приватний. Підказки/відповіді **ніколи не зберігаються і не журналюються**. Ефемерний.                                  | Llama, Qwen, DeepSeek, Kimi, MiniMax, Venice Uncensored тощо. |
| **Anonymized** | Проксіюється через Venice з видаленням метаданих. Базовий провайдер (OpenAI, Anthropic, Google, xAI) бачить анонімізовані запити. | Claude, GPT, Gemini, Grok                                     |

<Warning>
Анонімізовані моделі **не** є повністю приватними. Venice видаляє метадані перед пересиланням, але базовий провайдер (OpenAI, Anthropic, Google, xAI) усе одно обробляє запит. Обирайте моделі **Private**, коли потрібна повна конфіденційність.
</Warning>

## Можливості

- **Орієнтованість на конфіденційність**: вибір між режимами "private" (повністю приватний) і "anonymized" (через проксі)
- **Нецензуровані моделі**: доступ до моделей без обмежень контенту
- **Доступ до основних моделей**: використовуйте Claude, GPT, Gemini та Grok через анонімізований проксі Venice
- **OpenAI-сумісний API**: стандартні кінцеві точки `/v1` для простої інтеграції
- **Потокова передача**: підтримується всіма моделями
- **Виклик функцій**: підтримується окремими моделями (перевіряйте можливості моделі)
- **Vision**: підтримується моделями з можливістю обробки зображень
- **Без жорстких лімітів швидкості**: за надмірного використання може застосовуватися обмеження за принципом чесного використання

## Початок роботи

<Steps>
  <Step title="Отримайте свій API-ключ">
    1. Зареєструйтеся на [venice.ai](https://venice.ai)
    2. Перейдіть до **Settings > API Keys > Create new key**
    3. Скопіюйте свій API-ключ (формат: `vapi_xxxxxxxxxxxx`)
  </Step>
  <Step title="Налаштуйте OpenClaw">
    Оберіть бажаний спосіб налаштування:

    <Tabs>
      <Tab title="Інтерактивно (рекомендовано)">
        ```bash
        openclaw onboard --auth-choice venice-api-key
        ```

        Це:
        1. Запросить ваш API-ключ (або використає наявний `VENICE_API_KEY`)
        2. Покажe всі доступні моделі Venice
        3. Дозволить вибрати модель за замовчуванням
        4. Автоматично налаштує провайдера
      </Tab>
      <Tab title="Змінна середовища">
        ```bash
        export VENICE_API_KEY="vapi_xxxxxxxxxxxx"
        ```
      </Tab>
      <Tab title="Неінтерактивно">
        ```bash
        openclaw onboard --non-interactive \
          --auth-choice venice-api-key \
          --venice-api-key "vapi_xxxxxxxxxxxx"
        ```
      </Tab>
    </Tabs>

  </Step>
  <Step title="Перевірте налаштування">
    ```bash
    openclaw agent --model venice/kimi-k2-5 --message "Hello, are you working?"
    ```
  </Step>
</Steps>

## Вибір моделі

Після налаштування OpenClaw показує всі доступні моделі Venice. Обирайте відповідно до своїх потреб:

- **Модель за замовчуванням**: `venice/kimi-k2-5` для потужного приватного міркування та Vision.
- **Варіант із високими можливостями**: `venice/claude-opus-4-6` для найпотужнішого анонімізованого шляху через Venice.
- **Конфіденційність**: обирайте моделі "private" для повністю приватного інференсу.
- **Можливості**: обирайте моделі "anonymized", щоб отримати доступ до Claude, GPT, Gemini через проксі Venice.

Змінити модель за замовчуванням можна будь-коли:

```bash
openclaw models set venice/kimi-k2-5
openclaw models set venice/claude-opus-4-6
```

Переглянути всі доступні моделі:

```bash
openclaw models list | grep venice
```

Ви також можете виконати `openclaw configure`, вибрати **Model/auth** і потім **Venice AI**.

<Tip>
Скористайтеся таблицею нижче, щоб вибрати правильну модель для свого сценарію використання.

| Сценарій використання      | Рекомендована модель             | Чому                                          |
| -------------------------- | -------------------------------- | --------------------------------------------- |
| **Загальний чат (типово)** | `kimi-k2-5`                      | Потужне приватне міркування та Vision         |
| **Найкраща загальна якість** | `claude-opus-4-6`              | Найпотужніший анонімізований варіант Venice   |
| **Конфіденційність + кодування** | `qwen3-coder-480b-a35b-instruct` | Приватна модель для кодування з великим контекстом |
| **Приватний Vision**       | `kimi-k2-5`                      | Підтримка Vision без виходу з приватного режиму |
| **Швидко + дешево**        | `qwen3-4b`                       | Легка модель для міркування                   |
| **Складні приватні завдання** | `deepseek-v3.2`               | Потужне міркування, але без підтримки інструментів Venice |
| **Нецензуровано**          | `venice-uncensored`              | Без обмежень контенту                         |

</Tip>

## Доступні моделі (усього 41)

<AccordionGroup>
  <Accordion title="Приватні моделі (26) — повністю приватні, без журналювання">
    | ID моделі                              | Назва                               | Контекст | Можливості                 |
    | -------------------------------------- | ----------------------------------- | -------- | -------------------------- |
    | `kimi-k2-5`                            | Kimi K2.5                           | 256k     | Типова, міркування, vision |
    | `kimi-k2-thinking`                     | Kimi K2 Thinking                    | 256k     | Міркування                 |
    | `llama-3.3-70b`                        | Llama 3.3 70B                       | 128k     | Загальні                   |
    | `llama-3.2-3b`                         | Llama 3.2 3B                        | 128k     | Загальні                   |
    | `hermes-3-llama-3.1-405b`              | Hermes 3 Llama 3.1 405B             | 128k     | Загальні, інструменти вимкнено |
    | `qwen3-235b-a22b-thinking-2507`        | Qwen3 235B Thinking                 | 128k     | Міркування                 |
    | `qwen3-235b-a22b-instruct-2507`        | Qwen3 235B Instruct                 | 128k     | Загальні                   |
    | `qwen3-coder-480b-a35b-instruct`       | Qwen3 Coder 480B                    | 256k     | Кодування                  |
    | `qwen3-coder-480b-a35b-instruct-turbo` | Qwen3 Coder 480B Turbo              | 256k     | Кодування                  |
    | `qwen3-5-35b-a3b`                      | Qwen3.5 35B A3B                     | 256k     | Міркування, vision         |
    | `qwen3-next-80b`                       | Qwen3 Next 80B                      | 256k     | Загальні                   |
    | `qwen3-vl-235b-a22b`                   | Qwen3 VL 235B (Vision)              | 256k     | Vision                     |
    | `qwen3-4b`                             | Venice Small (Qwen3 4B)             | 32k      | Швидка, міркування         |
    | `deepseek-v3.2`                        | DeepSeek V3.2                       | 160k     | Міркування, інструменти вимкнено |
    | `venice-uncensored`                    | Venice Uncensored (Dolphin-Mistral) | 32k      | Нецензурована, інструменти вимкнено |
    | `mistral-31-24b`                       | Venice Medium (Mistral)             | 128k     | Vision                     |
    | `google-gemma-3-27b-it`                | Google Gemma 3 27B Instruct         | 198k     | Vision                     |
    | `openai-gpt-oss-120b`                  | OpenAI GPT OSS 120B                 | 128k     | Загальні                   |
    | `nvidia-nemotron-3-nano-30b-a3b`       | NVIDIA Nemotron 3 Nano 30B          | 128k     | Загальні                   |
    | `olafangensan-glm-4.7-flash-heretic`   | GLM 4.7 Flash Heretic               | 128k     | Міркування                 |
    | `zai-org-glm-4.6`                      | GLM 4.6                             | 198k     | Загальні                   |
    | `zai-org-glm-4.7`                      | GLM 4.7                             | 198k     | Міркування                 |
    | `zai-org-glm-4.7-flash`                | GLM 4.7 Flash                       | 128k     | Міркування                 |
    | `zai-org-glm-5`                        | GLM 5                               | 198k     | Міркування                 |
    | `minimax-m21`                          | MiniMax M2.1                        | 198k     | Міркування                 |
    | `minimax-m25`                          | MiniMax M2.5                        | 198k     | Міркування                 |
  </Accordion>

  <Accordion title="Анонімізовані моделі (15) — через проксі Venice">
    | ID моделі                        | Назва                          | Контекст | Можливості                |
    | ------------------------------- | ------------------------------ | -------- | ------------------------- |
    | `claude-opus-4-6`               | Claude Opus 4.6 (через Venice) | 1M       | Міркування, vision        |
    | `claude-opus-4-5`               | Claude Opus 4.5 (через Venice) | 198k     | Міркування, vision        |
    | `claude-sonnet-4-6`             | Claude Sonnet 4.6 (через Venice) | 1M     | Міркування, vision        |
    | `claude-sonnet-4-5`             | Claude Sonnet 4.5 (через Venice) | 198k   | Міркування, vision        |
    | `openai-gpt-54`                 | GPT-5.4 (через Venice)         | 1M       | Міркування, vision        |
    | `openai-gpt-53-codex`           | GPT-5.3 Codex (через Venice)   | 400k     | Міркування, vision, кодування |
    | `openai-gpt-52`                 | GPT-5.2 (через Venice)         | 256k     | Міркування                |
    | `openai-gpt-52-codex`           | GPT-5.2 Codex (через Venice)   | 256k     | Міркування, vision, кодування |
    | `openai-gpt-4o-2024-11-20`      | GPT-4o (через Venice)          | 128k     | Vision                    |
    | `openai-gpt-4o-mini-2024-07-18` | GPT-4o Mini (через Venice)     | 128k     | Vision                    |
    | `gemini-3-1-pro-preview`        | Gemini 3.1 Pro (через Venice)  | 1M       | Міркування, vision        |
    | `gemini-3-pro-preview`          | Gemini 3 Pro (через Venice)    | 198k     | Міркування, vision        |
    | `gemini-3-flash-preview`        | Gemini 3 Flash (через Venice)  | 256k     | Міркування, vision        |
    | `grok-41-fast`                  | Grok 4.1 Fast (через Venice)   | 1M       | Міркування, vision        |
    | `grok-code-fast-1`              | Grok Code Fast 1 (через Venice) | 256k    | Міркування, кодування     |
  </Accordion>
</AccordionGroup>

## Виявлення моделей

OpenClaw автоматично виявляє моделі з API Venice, коли встановлено `VENICE_API_KEY`. Якщо API недоступний, система переходить до статичного каталогу.

Кінцева точка `/models` є публічною (автентифікація не потрібна для переліку), але для інференсу потрібен чинний API-ключ.

## Потокова передача та підтримка інструментів

| Можливість          | Підтримка                                            |
| ------------------- | ---------------------------------------------------- |
| **Потокова передача** | Усі моделі                                         |
| **Виклик функцій**  | Більшість моделей (перевіряйте `supportsFunctionCalling` в API) |
| **Vision/зображення** | Моделі, позначені можливістю "Vision"             |
| **Режим JSON**      | Підтримується через `response_format`               |

## Ціни

Venice використовує систему на основі кредитів. Перевіряйте актуальні тарифи на [venice.ai/pricing](https://venice.ai/pricing):

- **Приватні моделі**: зазвичай нижча вартість
- **Анонімізовані моделі**: схоже на пряме ціноутворення API + невелика комісія Venice

### Venice (анонімізовано) проти прямого API

| Аспект       | Venice (анонімізовано)         | Прямий API          |
| ------------ | ------------------------------ | ------------------- |
| **Конфіденційність** | Метадані видалено, анонімізовано | Прив’язано до вашого облікового запису |
| **Затримка** | +10–50 мс (проксі)             | Напряму             |
| **Можливості** | Підтримується більшість можливостей | Усі можливості      |
| **Білінг**   | Кредити Venice                 | Білінг провайдера   |

## Приклади використання

```bash
# Використати типову приватну модель
openclaw agent --model venice/kimi-k2-5 --message "Quick health check"

# Використати Claude Opus через Venice (анонімізовано)
openclaw agent --model venice/claude-opus-4-6 --message "Summarize this task"

# Використати нецензуровану модель
openclaw agent --model venice/venice-uncensored --message "Draft options"

# Використати модель Vision із зображенням
openclaw agent --model venice/qwen3-vl-235b-a22b --message "Review attached image"

# Використати модель для кодування
openclaw agent --model venice/qwen3-coder-480b-a35b-instruct --message "Refactor this function"
```

## Усунення несправностей

<AccordionGroup>
  <Accordion title="API-ключ не розпізнається">
    ```bash
    echo $VENICE_API_KEY
    openclaw models list | grep venice
    ```

    Переконайтеся, що ключ починається з `vapi_`.

  </Accordion>

  <Accordion title="Модель недоступна">
    Каталог моделей Venice оновлюється динамічно. Запустіть `openclaw models list`, щоб побачити моделі, доступні зараз. Деякі моделі можуть бути тимчасово офлайн.
  </Accordion>

  <Accordion title="Проблеми зі з’єднанням">
    API Venice доступний за адресою `https://api.venice.ai/api/v1`. Переконайтеся, що ваша мережа дозволяє HTTPS-з’єднання.
  </Accordion>
</AccordionGroup>

<Note>
Додаткова допомога: [Усунення несправностей](/uk/help/troubleshooting) і [FAQ](/uk/help/faq).
</Note>

## Розширене налаштування

<AccordionGroup>
  <Accordion title="Приклад файла конфігурації">
    ```json5
    {
      env: { VENICE_API_KEY: "vapi_..." },
      agents: { defaults: { model: { primary: "venice/kimi-k2-5" } } },
      models: {
        mode: "merge",
        providers: {
          venice: {
            baseUrl: "https://api.venice.ai/api/v1",
            apiKey: "${VENICE_API_KEY}",
            api: "openai-completions",
            models: [
              {
                id: "kimi-k2-5",
                name: "Kimi K2.5",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 256000,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір провайдерів, посилань на моделі та поведінки резервного перемикання.
  </Card>
  <Card title="Venice AI" href="https://venice.ai" icon="globe">
    Домашня сторінка Venice AI та реєстрація облікового запису.
  </Card>
  <Card title="Документація API" href="https://docs.venice.ai" icon="book">
    Довідник API Venice і документація для розробників.
  </Card>
  <Card title="Ціни" href="https://venice.ai/pricing" icon="credit-card">
    Актуальні тарифи Venice у кредитах і плани.
  </Card>
</CardGroup>
