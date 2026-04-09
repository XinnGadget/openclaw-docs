---
summary: "Запустить OpenClaw через inferrs (локальный сервер, совместимый с OpenAI)"
read_when:
  - Вы хотите запустить OpenClaw с локальным сервером inferrs
  - Вы предоставляете модель Gemma или другую модель через inferrs
  - Вам нужны точные флаги совместимости OpenClaw для inferrs
title: "inferrs"
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) может предоставлять локальные модели через API, совместимый с OpenAI (`/v1`). OpenClaw работает с `inferrs` через общий путь `openai-completions`.

В настоящее время `inferrs` лучше рассматривать как пользовательский саморазмещённый бэкенд, совместимый с OpenAI, а не как специализированный плагин-провайдер для OpenClaw.

## Быстрый старт

1. Запустите `inferrs` с моделью.

Пример:

```bash
inferrs serve google/gemma-4-E2B-it \
  --host 127.0.0.1 \
  --port 8080 \
  --device metal
```

2. Проверьте доступность сервера.

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

3. Добавьте явную запись провайдера OpenClaw и укажите на неё модель по умолчанию.

## Полный пример конфигурации

В этом примере используется Gemma 4 на локальном сервере `inferrs`.

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/google/gemma-4-E2B-it" },
      models: {
        "inferrs/google/gemma-4-E2B-it": {
          alias: "Gemma 4 (inferrs)",
        },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      inferrs: {
        baseUrl: "http://127.0.0.1:8080/v1",
        apiKey: "inferrs-local",
        api: "openai-completions",
        models: [
          {
            id: "google/gemma-4-E2B-it",
            name: "Gemma 4 E2B (inferrs)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 131072,
            maxTokens: 4096,
            compat: {
              requiresStringContent: true,
            },
          },
        ],
      },
    },
  },
}
```

## Почему важен `requiresStringContent`

Некоторые маршруты Chat Completions в `inferrs` принимают только строку `messages[].content`, а не структурированные массивы частей контента.

Если выполнение OpenClaw завершается с ошибкой вида:

```text
messages[1].content: invalid type: sequence, expected a string
```

установите:

```json5
compat: {
  requiresStringContent: true
}
```

OpenClaw преобразует чистые текстовые части контента в простые строки перед отправкой запроса.

## Предупреждение о Gemma и схеме инструментов

Некоторые текущие комбинации `inferrs` + Gemma принимают небольшие прямые запросы `/v1/chat/completions`, но всё равно завершаются ошибкой при полных поворотах агента OpenClaw.

Если это происходит, сначала попробуйте следующее:

```json5
compat: {
  requiresStringContent: true,
  supportsTools: false
}
```

Это отключит поверхность схемы инструментов OpenClaw для модели и может снизить нагрузку на более строгие локальные бэкенды.

Если небольшие прямые запросы по-прежнему работают, но обычные повороты агента OpenClaw продолжают завершаться сбоем внутри `inferrs`, оставшаяся проблема, как правило, связана с поведением модели/сервера на вышестоящем уровне, а не с транспортным слоем OpenClaw.

## Ручной дымовый тест

После настройки проверьте оба уровня:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'

openclaw infer model run \
  --model inferrs/google/gemma-4-E2B-it \
  --prompt "What is 2 + 2? Reply with one short sentence." \
  --json
```

Если первая команда выполняется успешно, а вторая — нет, воспользуйтесь примечаниями по устранению неполадок ниже.

## Устранение неполадок

- `curl /v1/models` завершается ошибкой: `inferrs` не запущен, недоступен или не привязан к ожидаемому хосту/порту.
- `messages[].content ... expected a string`: установите `compat.requiresStringContent: true`.
- Прямые небольшие вызовы `/v1/chat/completions` проходят, но `openclaw infer model run` завершается ошибкой: попробуйте `compat.supportsTools: false`.
- OpenClaw больше не получает ошибок схемы, но `inferrs` по-прежнему завершается сбоем при более крупных поворотах агента: рассмотрите это как ограничение `inferrs` или модели на вышестоящем уровне и снизьте нагрузку на промпт или смените локальный бэкенд/модель.

## Поведение в стиле прокси

`inferrs` рассматривается как бэкенд в стиле прокси, совместимый с OpenAI `/v1`, а не как нативный эндпоинт OpenAI.

- формирование запросов, специфичное только для OpenAI, здесь не применяется;
- нет `service_tier`, нет Responses `store`, нет подсказок кэширования промпта и нет формирования полезной нагрузки, совместимой с рассуждениями OpenAI;
- скрытые заголовки атрибуции OpenClaw (`originator`, `version`, `User-Agent`) не добавляются в пользовательские базовые URL `inferrs`.

## См. также

- [Локальные модели](/gateway/local-models)
- [Устранение неполадок шлюза](/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)
- [Провайдеры моделей](/concepts/model-providers)