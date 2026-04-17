---
read_when:
    - Вам потрібен один API-ключ для багатьох LLM-ів
    - Вам потрібні вказівки з налаштування Baidu Qianfan
summary: Використовуйте уніфікований API Qianfan для доступу до багатьох моделей в OpenClaw
title: Qianfan
x-i18n:
    generated_at: "2026-04-12T10:30:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1d0eeee9ec24b335c2fb8ac5e985a9edc35cfc5b2641c545cb295dd2de619f50
    source_path: providers/qianfan.md
    workflow: 15
---

# Qianfan

Qianfan — це платформа MaaS від Baidu, яка надає **уніфікований API**, що маршрутизує запити до багатьох моделей через єдину
кінцеву точку та API-ключ. Вона сумісна з OpenAI, тому більшість OpenAI SDK працюють, якщо змінити base URL.

| Властивість | Значення                          |
| ----------- | --------------------------------- |
| Провайдер   | `qianfan`                         |
| Автентифікація | `QIANFAN_API_KEY`              |
| API         | Сумісний з OpenAI                |
| Base URL    | `https://qianfan.baidubce.com/v2` |

## Початок роботи

<Steps>
  <Step title="Створіть обліковий запис Baidu Cloud">
    Зареєструйтеся або увійдіть у [Qianfan Console](https://console.bce.baidu.com/qianfan/ais/console/apiKey) і переконайтеся, що для вас увімкнено доступ до API Qianfan.
  </Step>
  <Step title="Згенеруйте API-ключ">
    Створіть новий застосунок або виберіть наявний, а потім згенеруйте API-ключ. Формат ключа: `bce-v3/ALTAK-...`.
  </Step>
  <Step title="Запустіть онбординг">
    ```bash
    openclaw onboard --auth-choice qianfan-api-key
    ```
  </Step>
  <Step title="Перевірте, що модель доступна">
    ```bash
    openclaw models list --provider qianfan
    ```
  </Step>
</Steps>

## Доступні моделі

| Посилання на модель                  | Вхідні дані | Контекст | Макс. вивід | Міркування | Примітки      |
| ------------------------------------ | ----------- | -------- | ----------- | ---------- | ------------- |
| `qianfan/deepseek-v3.2`              | текст       | 98,304   | 32,768      | Так        | Модель за замовчуванням |
| `qianfan/ernie-5.0-thinking-preview` | текст, зображення | 119,000 | 64,000 | Так        | Мультимодальна |

<Tip>
Базове посилання на вбудовану модель — `qianfan/deepseek-v3.2`. Вам потрібно перевизначати `models.providers.qianfan` лише тоді, коли потрібен власний base URL або метадані моделі.
</Tip>

## Приклад конфігурації

```json5
{
  env: { QIANFAN_API_KEY: "bce-v3/ALTAK-..." },
  agents: {
    defaults: {
      model: { primary: "qianfan/deepseek-v3.2" },
      models: {
        "qianfan/deepseek-v3.2": { alias: "QIANFAN" },
      },
    },
  },
  models: {
    providers: {
      qianfan: {
        baseUrl: "https://qianfan.baidubce.com/v2",
        api: "openai-completions",
        models: [
          {
            id: "deepseek-v3.2",
            name: "DEEPSEEK V3.2",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 98304,
            maxTokens: 32768,
          },
          {
            id: "ernie-5.0-thinking-preview",
            name: "ERNIE-5.0-Thinking-Preview",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 119000,
            maxTokens: 64000,
          },
        ],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Транспорт і сумісність">
    Qianfan працює через транспортний шлях, сумісний з OpenAI, а не через нативне формування запитів OpenAI. Це означає, що стандартні можливості OpenAI SDK працюють, але специфічні для провайдера параметри можуть не передаватися.
  </Accordion>

  <Accordion title="Каталог і перевизначення">
    Вбудований каталог наразі містить `deepseek-v3.2` і `ernie-5.0-thinking-preview`. Додавайте або перевизначайте `models.providers.qianfan` лише тоді, коли вам потрібен власний base URL або метадані моделі.

    <Note>
    Посилання на моделі використовують префікс `qianfan/` (наприклад, `qianfan/deepseek-v3.2`).
    </Note>

  </Accordion>

  <Accordion title="Усунення проблем">
    - Переконайтеся, що ваш API-ключ починається з `bce-v3/ALTAK-` і що в консолі Baidu Cloud для нього увімкнено доступ до API Qianfan.
    - Якщо моделі не відображаються у списку, підтвердьте, що для вашого облікового запису активовано сервіс Qianfan.
    - Base URL за замовчуванням: `https://qianfan.baidubce.com/v2`. Змінюйте його лише у випадку використання власної кінцевої точки або проксі.
  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір провайдерів, посилань на моделі та поведінки перемикання при відмові.
  </Card>
  <Card title="Довідник із конфігурації" href="/uk/gateway/configuration" icon="gear">
    Повний довідник з конфігурації OpenClaw.
  </Card>
  <Card title="Налаштування агента" href="/uk/concepts/agent" icon="robot">
    Налаштування типових параметрів агента та призначення моделей.
  </Card>
  <Card title="Документація API Qianfan" href="https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb" icon="arrow-up-right-from-square">
    Офіційна документація API Qianfan.
  </Card>
</CardGroup>
