 ---
summary: "Поиск в интернете через Kimi с использованием Moonshot web search"
read_when:
  - Вы хотите использовать Kimi для web_search
  - Вам нужен KIMI_API_KEY или MOONSHOT_API_KEY
title: "Поиск через Kimi"
---

# Поиск через Kimi

OpenClaw поддерживает Kimi в качестве провайдера `web_search`, используя Moonshot web search для формирования синтезированных ИИ-ответов с цитатами.

## Получение API-ключа

<Steps>
  <Step title="Создание ключа">
    Получите API-ключ на [Moonshot AI](https://platform.moonshot.cn/).
  </Step>
  <Step title="Сохранение ключа">
    Установите `KIMI_API_KEY` или `MOONSHOT_API_KEY` в окружении Gateway либо настройте через:

    ```bash
    openclaw configure --section web
    ```

  </Step>
</Steps>

Когда вы выбираете **Kimi** во время выполнения `openclaw onboard` или `openclaw configure --section web`, OpenClaw также может запросить:

- регион API Moonshot:
  - `https://api.moonshot.ai/v1`
  - `https://api.moonshot.cn/v1`
- модель веб-поиска Kimi по умолчанию (по умолчанию — `kimi-k2.5`)

## Настройка

```json5
{
  plugins: {
    entries: {
      moonshot: {
        config: {
          webSearch: {
            apiKey: "sk-...", // необязательно, если задан KIMI_API_KEY или MOONSHOT_API_KEY
            baseUrl: "https://api.moonshot.ai/v1",
            model: "kimi-k2.5",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "kimi",
      },
    },
  },
}
```

Если вы используете китайский хост API для чата (`models.providers.moonshot.baseUrl`: `https://api.moonshot.cn/v1`), OpenClaw повторно использует этот же хост для Kimi `web_search`, когда `tools.web.search.kimi.baseUrl` не указан. Это позволяет избежать ошибочного обращения ключей с [platform.moonshot.cn](https://platform.moonshot.cn/) к международному эндпоинту (который часто возвращает HTTP 401). Переопределите значение через `tools.web.search.kimi.baseUrl`, если вам нужен другой базовый URL для поиска.

**Альтернатива через окружение:** установите `KIMI_API_KEY` или `MOONSHOT_API_KEY` в окружении Gateway. Для установки шлюза поместите значение в `~/.openclaw/.env`.

Если вы не укажете `baseUrl`, OpenClaw по умолчанию использует `https://api.moonshot.ai/v1`.
Если вы не укажете `model`, OpenClaw по умолчанию использует `kimi-k2.5`.

## Принцип работы

Kimi использует Moonshot web search для синтеза ответов с встроенными цитатами — аналогично подходу с обоснованными ответами (grounded response) у Gemini и Grok.

## Поддерживаемые параметры

Поиск через Kimi поддерживает параметр `query`.

Параметр `count` принимается для обеспечения совместимости с общим интерфейсом `web_search`, но Kimi по-прежнему возвращает один синтезированный ответ с цитатами, а не список из N результатов.

Специфичные для провайдера фильтры в настоящее время не поддерживаются.

## Связанные материалы

- [Обзор веб-поиска](/tools/web) — все провайдеры и автоматическое определение
- [Moonshot AI](/providers/moonshot) — документация по модели Moonshot и провайдеру Kimi Coding
- [Поиск через Gemini](/tools/gemini-search) — синтезированные ИИ-ответы с опорой на данные Google
- [Поиск через Grok](/tools/grok-search) — синтезированные ИИ-ответы с опорой на данные xAI