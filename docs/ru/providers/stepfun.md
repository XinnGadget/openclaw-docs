---
summary: "Использовать модели StepFun в OpenClaw"
read_when:
  - Вам нужны модели StepFun в OpenClaw
  - Вам требуется руководство по настройке StepFun
title: "StepFun"
---

# StepFun

OpenClaw включает встроенный плагин провайдера StepFun с двумя идентификаторами провайдера:

- `stepfun` — для стандартного эндпоинта;
- `stepfun-plan` — для эндпоинта Step Plan.

Встроенные каталоги в настоящее время различаются по интерфейсу:

- Стандартный: `step-3.5-flash`;
- Step Plan: `step-3.5-flash`, `step-3.5-flash-2603`.

## Обзор регионов и эндпоинтов

- Стандартный эндпоинт для Китая: `https://api.stepfun.com/v1`;
- Стандартный глобальный эндпоинт: `https://api.stepfun.ai/v1`;
- Эндпоинт Step Plan для Китая: `https://api.stepfun.com/step_plan/v1`;
- Глобальный эндпоинт Step Plan: `https://api.stepfun.ai/step_plan/v1`;
- Переменная окружения для аутентификации: `STEPFUN_API_KEY`.

Используйте ключ для Китая с эндпоинтами `.com`, а глобальный ключ — с эндпоинтами `.ai`.

## Настройка через CLI

Интерактивная настройка:

```bash
openclaw onboard
```

Выберите один из следующих вариантов аутентификации:

- `stepfun-standard-api-key-cn`;
- `stepfun-standard-api-key-intl`;
- `stepfun-plan-api-key-cn`;
- `stepfun-plan-api-key-intl`.

Примеры неинтерактивной настройки:

```bash
openclaw onboard --auth-choice stepfun-standard-api-key-intl --stepfun-api-key "$STEPFUN_API_KEY"
openclaw onboard --auth-choice stepfun-plan-api-key-intl --stepfun-api-key "$STEPFUN_API_KEY"
```

## Ссылки на модели

- Стандартная модель по умолчанию: `stepfun/step-3.5-flash`;
- Модель Step Plan по умолчанию: `stepfun-plan/step-3.5-flash`;
- Альтернативная модель Step Plan: `stepfun-plan/step-3.5-flash-2603`.

## Встроенные каталоги

Стандартный (`stepfun`):

| Ссылка на модель | Контекст | Максимальный объём вывода | Примечания |
| --- | --- | --- | --- |
| `stepfun/step-3.5-flash` | 262 144 | 65 536 | Стандартная модель по умолчанию |

Step Plan (`stepfun-plan`):

| Ссылка на модель | Контекст | Максимальный объём вывода | Примечания |
| --- | --- | --- | --- |
| `stepfun-plan/step-3.5-flash` | 262 144 | 65 536 | Модель Step Plan по умолчанию |
| `stepfun-plan/step-3.5-flash-2603` | 262 144 | 65 536 | Дополнительная модель Step Plan |

## Фрагменты конфигурации

Провайдер стандартного типа:

```json5
{
  env: { STEPFUN_API_KEY: "your-key" },
  agents: { defaults: { model: { primary: "stepfun/step-3.5-flash" } } },
  models: {
    mode: "merge",
    providers: {
      stepfun: {
        baseUrl: "https://api.stepfun.ai/v1",
        api: "openai-completions",
        apiKey: "${STEPFUN_API_KEY}",
        models: [
          {
            id: "step-3.5-flash",
            name: "Step 3.5 Flash",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

Провайдер Step Plan:

```json5
{
  env: { STEPFUN_API_KEY: "your-key" },
  agents: { defaults: { model: { primary: "stepfun-plan/step-3.5-flash" } } },
  models: {
    mode: "merge",
    providers: {
      "stepfun-plan": {
        baseUrl: "https://api.stepfun.ai/step_plan/v1",
        api: "openai-completions",
        apiKey: "${STEPFUN_API_KEY}",
        models: [
          {
            id: "step-3.5-flash",
            name: "Step 3.5 Flash",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 65536,
          },
          {
            id: "step-3.5-flash-2603",
            name: "Step 3.5 Flash 2603",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

## Примечания

- Провайдер включён в состав OpenClaw, поэтому отдельный этап установки плагина не требуется.
- Модель `step-3.5-flash-2603` в настоящее время доступна только в `stepfun-plan`.
- Единый процесс аутентификации создаёт профили, соответствующие региону, как для `stepfun`, так и для `stepfun-plan`, поэтому оба интерфейса можно обнаружить одновременно.
- Используйте команды `openclaw models list` и `openclaw models set <provider/model>`, чтобы просмотреть или переключиться на другие модели.
- Для общего обзора провайдеров см. [Провайдеры моделей](/concepts/model-providers).