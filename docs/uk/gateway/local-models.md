---
read_when:
    - Ви хочете обслуговувати моделі зі свого власного GPU-сервера.
    - Ви налаштовуєте LM Studio або сумісний з OpenAI проксі.
    - Вам потрібні найбезпечніші рекомендації щодо локальних моделей.
summary: Запустіть OpenClaw на локальних LLM (LM Studio, vLLM, LiteLLM, користувацькі OpenAI-ендпойнти)
title: Локальні моделі
x-i18n:
    generated_at: "2026-04-14T13:47:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8778cc1c623a356ff3cf306c494c046887f9417a70ec71e659e4a8aae912a780
    source_path: gateway/local-models.md
    workflow: 15
---

# Локальні моделі

Локально — це можливо, але OpenClaw очікує великий контекст і надійний захист від інʼєкції в підказки. Малі карти обрізають контекст і послаблюють безпеку. Орієнтуйтеся на високий рівень: **≥2 повністю укомплектовані Mac Studio або еквівалентна GPU-система (~$30k+)**. Один GPU на **24 GB** підходить лише для легших підказок із вищою затримкою. Використовуйте **найбільший / повнорозмірний варіант моделі, який можете запустити**; агресивно квантизовані або “small” чекпойнти підвищують ризик інʼєкції в підказки (див. [Безпека](/uk/gateway/security)).

Якщо вам потрібне локальне налаштування з найменшими труднощами, почніть з [LM Studio](/uk/providers/lmstudio) або [Ollama](/uk/providers/ollama) і `openclaw onboard`. Ця сторінка — це рекомендаційний посібник для потужніших локальних стеків і користувацьких локальних серверів, сумісних з OpenAI.

## Рекомендовано: LM Studio + велика локальна модель (Responses API)

Найкращий локальний стек на сьогодні. Завантажте велику модель у LM Studio (наприклад, повнорозмірну збірку Qwen, DeepSeek або Llama), увімкніть локальний сервер (типово `http://127.0.0.1:1234`) і використовуйте Responses API, щоб відокремити міркування від фінального тексту.

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

- Встановіть LM Studio: [https://lmstudio.ai](https://lmstudio.ai)
- У LM Studio завантажте **найбільшу доступну збірку моделі** (уникайте варіантів “small” / сильно квантизованих), запустіть сервер, переконайтеся, що `http://127.0.0.1:1234/v1/models` показує її в списку.
- Замініть `my-local-model` на фактичний ID моделі, показаний у LM Studio.
- Тримайте модель завантаженою; холодне завантаження додає затримку запуску.
- За потреби скоригуйте `contextWindow` / `maxTokens`, якщо ваша збірка LM Studio відрізняється.
- Для WhatsApp використовуйте лише Responses API, щоб надсилався тільки фінальний текст.

Залишайте хостингові моделі налаштованими навіть під час локальної роботи; використовуйте `models.mode: "merge"`, щоб резервні варіанти лишалися доступними.

### Гібридна конфігурація: основна хостингова модель, локальна резервна

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

### Спочатку локальна модель із хостинговою страховкою

Поміняйте місцями порядок `primary` і `fallback`; залиште той самий блок `providers` і `models.mode: "merge"`, щоб мати змогу переключитися на Sonnet або Opus, коли локальний сервер недоступний.

### Регіональний хостинг / маршрутизація даних

- Хостингові варіанти MiniMax/Kimi/GLM також доступні на OpenRouter з ендпойнтами, привʼязаними до регіону (наприклад, розміщеними у США). Оберіть там регіональний варіант, щоб трафік залишався у вибраній вами юрисдикції, і водночас використовуйте `models.mode: "merge"` для резервних варіантів Anthropic/OpenAI.
- Лише локальний запуск лишається найкращим шляхом для приватності; регіональна маршрутизація через хостинг — це компромісний варіант, якщо вам потрібні можливості провайдера, але ви хочете контролювати потік даних.

## Інші локальні проксі, сумісні з OpenAI

vLLM, LiteLLM, OAI-proxy або користувацькі Gateway працюють, якщо вони надають OpenAI-подібний ендпойнт `/v1`. Замініть блок провайдера вище на свій ендпойнт і ID моделі:

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

Зберігайте `models.mode: "merge"`, щоб хостингові моделі лишалися доступними як резервні.

Примітка щодо поведінки для локальних / проксійованих бекендів `/v1`:

- OpenClaw розглядає їх як проксі-маршрути, сумісні з OpenAI, а не як нативні ендпойнти OpenAI
- тут не застосовується формування запитів, характерне лише для нативного OpenAI: без `service_tier`, без `store` у Responses, без сумісного з reasoning формування payload для OpenAI і без підказок для кешу підказок
- приховані службові заголовки атрибуції OpenClaw (`originator`, `version`, `User-Agent`) не додаються до цих користувацьких проксі-URL

Примітки щодо сумісності для суворіших бекендів, сумісних з OpenAI:

- Деякі сервери приймають у Chat Completions лише рядковий `messages[].content`, а не структуровані масиви частин вмісту. Для таких ендпойнтів встановіть `models.providers.<provider>.models[].compat.requiresStringContent: true`.
- Деякі менші або суворіші локальні бекенди нестабільно працюють із повною формою підказок середовища агента OpenClaw, особливо коли включені схеми інструментів. Якщо бекенд працює для маленьких прямих викликів `/v1/chat/completions`, але не працює для звичайних ходів агента OpenClaw, спочатку спробуйте `agents.defaults.localModelMode: "lean"`, щоб прибрати важкі типові інструменти на кшталт `browser`, `cron` і `message`; якщо це не допоможе, спробуйте `models.providers.<provider>.models[].compat.supportsTools: false`.
- Якщо бекенд і далі падає лише на більших запусках OpenClaw, то причина зазвичай у можливостях моделі / сервера або у багу бекенда, а не в транспортному шарі OpenClaw.

## Усунення несправностей

- Gateway може дістатися до проксі? `curl http://127.0.0.1:1234/v1/models`.
- Модель у LM Studio вивантажена? Завантажте її знову; холодний старт — поширена причина “зависання”.
- OpenClaw попереджає, коли виявлене вікно контексту менше за **32k**, і блокує роботу нижче за **16k**. Якщо ви натрапили на цю попередню перевірку, збільште ліміт контексту сервера / моделі або виберіть більшу модель.
- Помилки контексту? Зменште `contextWindow` або підвищте ліміт вашого сервера.
- Сервер, сумісний з OpenAI, повертає `messages[].content ... expected a string`?
  Додайте `compat.requiresStringContent: true` до запису цієї моделі.
- Маленькі прямі виклики `/v1/chat/completions` працюють, але `openclaw infer model run`
  не працює з Gemma або іншою локальною моделлю? Спочатку вимкніть схеми інструментів через
  `compat.supportsTools: false`, а потім перевірте ще раз. Якщо сервер і далі падає лише
  на більших підказках OpenClaw, вважайте це обмеженням моделі / сервера на стороні джерела.
- Безпека: локальні моделі оминають фільтри на боці провайдера; робіть агентів вузькоспрямованими й тримайте Compaction увімкненим, щоб обмежити радіус ураження від інʼєкції в підказки.
