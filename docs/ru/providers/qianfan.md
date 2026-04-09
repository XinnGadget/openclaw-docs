---
summary: "Используйте унифицированный API Qianfan для доступа к множеству моделей в OpenClaw"
read_when:
  - Вам нужен один API-ключ для множества LLM
  - Вам требуется руководство по настройке Baidu Qianfan
title: "Qianfan"
---

# Руководство по провайдеру Qianfan

Qianfan — это платформа MaaS от Baidu, которая предоставляет **унифицированный API**, направляющий запросы к множеству моделей через единую конечную точку и API-ключ. Платформа совместима с OpenAI, поэтому большинство SDK OpenAI работают после смены базового URL.

## Предварительные требования

1. Учётная запись Baidu Cloud с доступом к API Qianfan.
2. API-ключ из консоли Qianfan.
3. Установленный на вашей системе OpenClaw.

## Получение API-ключа

1. Перейдите в [консоль Qianfan](https://console.bce.baidu.com/qianfan/ais/console/apiKey).
2. Создайте новое приложение или выберите существующее.
3. Сгенерируйте API-ключ (формат: `bce-v3/ALTAK-...`).
4. Скопируйте API-ключ для использования с OpenClaw.

## Настройка через CLI

```bash
openclaw onboard --auth-choice qianfan-api-key
```

## Фрагмент конфигурации

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

## Примечания

- Модель, включённая по умолчанию: `qianfan/deepseek-v3.2`.
- Базовый URL по умолчанию: `https://qianfan.baidubce.com/v2`.
- В текущий комплект каталога входят `deepseek-v3.2` и `ernie-5.0-thinking-preview`.
- Добавляйте или переопределяйте `models.providers.qianfan` только в случае необходимости задать пользовательский базовый URL или метаданные модели.
- Qianfan работает через транспортный путь, совместимый с OpenAI, а не через формирование запросов, специфичное для OpenAI.

## Сопутствующая документация

- [Конфигурация OpenClaw](/gateway/configuration)
- [Провайдеры моделей](/concepts/model-providers)
- [Настройка агента](/concepts/agent)
- [Документация по API Qianfan](https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb)