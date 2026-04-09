 ---
summary: "Поиск MiniMax через API поиска Coding Plan"
read_when:
  - Вы хотите использовать MiniMax для web_search
  - Вам нужен ключ MiniMax Coding Plan
  - Вам нужны указания по хостам поиска MiniMax CN/глобальный
title: "Поиск MiniMax"
---

# Поиск MiniMax

OpenClaw поддерживает MiniMax в качестве провайдера `web_search` через API поиска MiniMax Coding Plan. Он возвращает структурированные результаты поиска с заголовками, URL-адресами, фрагментами текста и связанными запросами.

## Получение ключа Coding Plan

<Steps>
  <Step title="Создание ключа">
    Создайте или скопируйте ключ MiniMax Coding Plan на [платформе MiniMax](https://platform.minimax.io/user-center/basic-information/interface-key).
  </Step>
  <Step title="Сохранение ключа">
    Установите переменную `MINIMAX_CODE_PLAN_KEY` в окружении Gateway либо настройте с помощью команды:

    ```bash
    openclaw configure --section web
    ```

  </Step>
</Steps>

OpenClaw также принимает `MINIMAX_CODING_API_KEY` в качестве псевдонима переменной окружения. `MINIMAX_API_KEY` по-прежнему считывается как запасной вариант совместимости, если она уже указывает на токен coding-plan.

## Настройка

```json5
{
  plugins: {
    entries: {
      minimax: {
        config: {
          webSearch: {
            apiKey: "sk-cp-...", // необязательно, если установлена MINIMAX_CODE_PLAN_KEY
            region: "global", // или "cn"
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "minimax",
      },
    },
  },
}
```

**Альтернатива через переменные окружения:** установите `MINIMAX_CODE_PLAN_KEY` в окружении Gateway. При установке шлюза поместите её в `~/.openclaw/.env`.

## Выбор региона

Для поиска MiniMax используются следующие эндпоинты:

- Глобальный: `https://api.minimax.io/v1/coding_plan/search`
- CN: `https://api.minimaxi.com/v1/coding_plan/search`

Если параметр `plugins.entries.minimax.config.webSearch.region` не задан, OpenClaw определяет регион в следующем порядке:

1. `tools.web.search.minimax.region` / `webSearch.region`, принадлежащий плагину
2. `MINIMAX_API_HOST`
3. `models.providers.minimax.baseUrl`
4. `models.providers.minimax-portal.baseUrl`

Это означает, что при подключении к CN или при установке `MINIMAX_API_HOST=https://api.minimaxi.com/...` поиск MiniMax также автоматически будет использовать хост CN.

Даже если вы выполнили аутентификацию MiniMax через путь OAuth `minimax-portal`, веб-поиск по-прежнему регистрируется как провайдер с ID `minimax`; базовый URL провайдера OAuth используется только как подсказка для выбора хоста (CN/глобальный).

## Поддерживаемые параметры

Поиск MiniMax поддерживает:

- `query`
- `count` (OpenClaw обрезает возвращаемый список результатов до указанного количества)

Специфичные для провайдера фильтры в настоящее время не поддерживаются.

## Связанные материалы

- [Обзор веб-поиска](/tools/web) — все провайдеры и автоматическое определение
- [MiniMax](/providers/minimax) — настройка модели, изображений, речи и аутентификации