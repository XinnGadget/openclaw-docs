---
read_when:
    - Ви хочете розгортати моделі зі свого власного GPU-сервера
    - Ви налаштовуєте LM Studio або OpenAI-сумісний проксі-сервер
    - Вам потрібні найбезпечніші рекомендації щодо локальних моделей
summary: Запустіть OpenClaw на локальних LLM (LM Studio, vLLM, LiteLLM, власні OpenAI endpoint-и)
title: Локальні моделі
x-i18n:
    generated_at: "2026-04-15T10:48:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7a506ff83e4c2870d3878339f646c906584454a156ecd618c360f592cf3b0011
    source_path: gateway/local-models.md
    workflow: 15
---

# Локальні моделі

Локальний запуск можливий, але OpenClaw очікує великий контекст + сильний захист від prompt injection. Малі карти обрізають контекст і послаблюють безпеку. Орієнтуйтеся на високий рівень: **≥2 повністю укомплектовані Mac Studio або еквівалентна GPU-установка (~$30k+)**. Одна GPU на **24 GB** підходить лише для легших запитів із вищою затримкою. Використовуйте **найбільший / повнорозмірний варіант моделі, який можете запустити**; агресивно квантизовані або “small” чекпойнти підвищують ризик prompt injection (див. [Безпека](/uk/gateway/security)).

Якщо вам потрібне локальне налаштування з найменшим тертям, почніть із [LM Studio](/uk/providers/lmstudio) або [Ollama](/uk/providers/ollama) та `openclaw onboard`. Ця сторінка — практичний посібник для продуктивніших локальних стеків і власних локальних OpenAI-сумісних серверів.

## Рекомендовано: LM Studio + велика локальна модель (Responses API)

Найкращий актуальний локальний стек. Завантажте велику модель у LM Studio (наприклад, повнорозмірну збірку Qwen, DeepSeek або Llama), увімкніть локальний сервер (типово `http://127.0.0.1:1234`), і використовуйте Responses API, щоб тримати міркування окремо від фінального тексту.

```json5
{
  agents: {
    defaults: {
      model: { primary: “lmstudio/my-local-model” },
      models: {
        “anthropic/claude-opus-4-6”: { alias: “Opus” },
        “lmstudio/my-local-model”: { alias: “Local” },
      },
    },
  },
  models: {
    mode: “merge”,
    providers: {
      lmstudio: {
        baseUrl: “http://127.0.0.1:1234/v1”,
        apiKey: “lmstudio”,
        api: “openai-responses”,
        models: [
          {
            id: “my-local-model”,
            name: “Local Model”,
            reasoning: false,
            input: [“text”],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**Контрольний список налаштування**

- Установіть LM Studio: [https://lmstudio.ai](https://lmstudio.ai)
- У LM Studio завантажте **найбільшу доступну збірку моделі** (уникайте варіантів “small” / сильно квантизованих), запустіть сервер, переконайтеся, що `http://127.0.0.1:1234/v1/models` її показує.
- Замініть `my-local-model` на фактичний ID моделі, показаний у LM Studio.
- Тримайте модель завантаженою; холодне завантаження додає затримку запуску.
- Відкоригуйте `contextWindow` / `maxTokens`, якщо ваша збірка LM Studio відрізняється.
- Для WhatsApp використовуйте Responses API, щоб надсилався лише фінальний текст.

Тримайте хостовані моделі налаштованими навіть під час локального запуску; використовуйте `models.mode: "merge"`, щоб fallback-моделі залишалися доступними.

### Гібридна конфігурація: хостована основна модель, локальний fallback

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["lmstudio/my-local-model", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "lmstudio/my-local-model": { alias: "Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### Локальний пріоритет із хостованою страховкою

Поміняйте порядок основної моделі та fallback-моделей місцями; залиште той самий блок providers і `models.mode: "merge"`, щоб можна було перейти на Sonnet або Opus, коли локальний сервер недоступний.

### Регіональний хостинг / маршрутизація даних

- Хостовані варіанти MiniMax/Kimi/GLM також доступні в OpenRouter з endpoint-ами, прив’язаними до регіону (наприклад, хостинг у США). Виберіть там регіональний варіант, щоб трафік залишався у вибраній юрисдикції, і водночас використовуйте `models.mode: "merge"` для fallback-моделей Anthropic/OpenAI.
- Лише локальний запуск залишається найкращим шляхом для приватності; регіональна хостована маршрутизація — це компромісний варіант, коли вам потрібні можливості провайдера, але ви хочете контролювати потік даних.

## Інші OpenAI-сумісні локальні проксі

vLLM, LiteLLM, OAI-proxy або власні Gateway працюють, якщо вони надають OpenAI-подібний endpoint `/v1`. Замініть блок provider вище своїм endpoint-ом і ID моделі:

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Зберігайте `models.mode: "merge"`, щоб хостовані моделі залишалися доступними як fallback.

Примітка про поведінку для локальних / проксійованих `/v1` бекендів:

- OpenClaw трактує їх як проксі-подібні OpenAI-сумісні маршрути, а не як нативні endpoint-и OpenAI
- тут не застосовується формування запитів, доступне лише для нативного OpenAI: без
  `service_tier`, без `store` у Responses, без формування payload для сумісності з reasoning OpenAI
  і без підказок для кешу prompt-ів
- приховані службові заголовки OpenClaw (`originator`, `version`, `User-Agent`)
  не додаються до цих власних проксі-URL

Примітки щодо сумісності для суворіших OpenAI-сумісних бекендів:

- Деякі сервери приймають у Chat Completions лише рядковий `messages[].content`, а не
  структуровані масиви content-part. Для
  таких endpoint-ів задайте `models.providers.<provider>.models[].compat.requiresStringContent: true`.
- Деякі менші або суворіші локальні бекенди нестабільно працюють із повною формою prompt-ів
  runtime агента OpenClaw, особливо коли включені схеми інструментів. Якщо
  бекенд працює для крихітних прямих викликів `/v1/chat/completions`, але не працює на звичайних
  ходах агента OpenClaw, спершу спробуйте
  `agents.defaults.experimental.localModelLean: true`, щоб прибрати важкі
  стандартні інструменти, як-от `browser`, `cron` і `message`; це експериментальний
  прапорець, а не стабільне налаштування типового режиму. Див.
  [Експериментальні можливості](/uk/concepts/experimental-features). Якщо це не допомогло, спробуйте
  `models.providers.<provider>.models[].compat.supportsTools: false`.
- Якщо бекенд і далі падає лише на більших запусках OpenClaw, то зазвичай проблема,
  що залишилася, — це обмеження моделі/сервера на upstream або баг бекенда, а не транспортного шару OpenClaw.

## Усунення проблем

- Gateway може дістатися до проксі? `curl http://127.0.0.1:1234/v1/models`.
- Модель LM Studio вивантажена? Завантажте її знову; холодний старт — поширена причина “зависання”.
- OpenClaw попереджає, коли виявлене вікно контексту менше за **32k**, і блокує роботу нижче за **16k**. Якщо ви натрапили на цю попередню перевірку, збільште ліміт контексту сервера/моделі або виберіть більшу модель.
- Помилки контексту? Зменште `contextWindow` або підвищте ліміт вашого сервера.
- OpenAI-сумісний сервер повертає `messages[].content ... expected a string`?
  Додайте `compat.requiresStringContent: true` до цього запису моделі.
- Прямі маленькі виклики `/v1/chat/completions` працюють, але `openclaw infer model run`
  не працює на Gemma або іншій локальній моделі? Спочатку вимкніть схеми інструментів через
  `compat.supportsTools: false`, а потім перевірте ще раз. Якщо сервер і далі падає лише
  на більших prompt-ах OpenClaw, вважайте це обмеженням upstream-сервера/моделі.
- Безпека: локальні моделі пропускають фільтри на боці провайдера; тримайте агентів вузько налаштованими та залишайте Compaction увімкненим, щоб обмежити радіус ураження від prompt injection.
