---
summary: "Поиск, скрапинг и резервный механизм web_fetch в Firecrawl"
read_when:
  - Вам нужен веб‑экстракшн с использованием Firecrawl
  - Вам необходим API‑ключ Firecrawl
  - Вы хотите использовать Firecrawl в качестве провайдера web_search
  - Вам нужна экстракция с обходом ботов для web_fetch
title: "Firecrawl"
---

# Firecrawl

OpenClaw может использовать **Firecrawl** тремя способами:

- в качестве провайдера `web_search`;
- в качестве явных инструментов плагина: `firecrawl_search` и `firecrawl_scrape`;
- в качестве резервного экстрактора для `web_fetch`.

Это размещённый сервис извлечения/поиска, который поддерживает обход ботов и кэширование. Он помогает работать с сайтами, насыщенными JavaScript, или страницами, которые блокируют обычные HTTP‑запросы.

## Получение API‑ключа

1. Создайте учётную запись Firecrawl и сгенерируйте API‑ключ.
2. Сохраните его в конфигурации или задайте переменную `FIRECRAWL_API_KEY` в среде шлюза.

## Настройка поиска Firecrawl

```json5
{
  tools: {
    web: {
      search: {
        provider: "firecrawl",
      },
    },
  },
  plugins: {
    entries: {
      firecrawl: {
        enabled: true,
        config: {
          webSearch: {
            apiKey: "FIRECRAWL_API_KEY_HERE",
            baseUrl: "https://api.firecrawl.dev",
          },
        },
      },
    },
  },
}
```

Примечания:

- Выбор Firecrawl при первичной настройке или выполнение команды `openclaw configure --section web` автоматически включает встроенный плагин Firecrawl.
- `web_search` с Firecrawl поддерживает параметры `query` и `count`.
- Для управления специфичными для Firecrawl параметрами (например, `sources`, `categories` или скрапинг результатов) используйте `firecrawl_search`.
- Переопределения `baseUrl` должны оставаться на `https://api.firecrawl.dev`.
- `FIRECRAWL_BASE_URL` — общая переменная окружения для резервных URL поиска и скрапинга Firecrawl.

## Настройка скрапинга Firecrawl и резервного механизма web_fetch

```json5
{
  plugins: {
    entries: {
      firecrawl: {
        enabled: true,
        config: {
          webFetch: {
            apiKey: "FIRECRAWL_API_KEY_HERE",
            baseUrl: "https://api.firecrawl.dev",
            onlyMainContent: true,
            maxAgeMs: 172800000,
            timeoutSeconds: 60,
          },
        },
      },
    },
  },
}
```

Примечания:

- Попытки использования резервного механизма Firecrawl выполняются только при наличии API‑ключа (`plugins.entries.firecrawl.config.webFetch.apiKey` или `FIRECRAWL_API_KEY`).
- `maxAgeMs` задаёт максимально допустимый возраст кэшированных результатов (в миллисекундах). По умолчанию — 2 дня.
- Устаревшая конфигурация `tools.web.fetch.firecrawl.*` автоматически мигрируется с помощью `openclaw doctor --fix`.
- Переопределения URL скрапинга/базового URL Firecrawl ограничены `https://api.firecrawl.dev`.

`firecrawl_scrape` использует те же настройки и переменные окружения, что и `plugins.entries.firecrawl.config.webFetch.*`.

## Инструменты плагина Firecrawl

### `firecrawl_search`

Используйте этот инструмент, если вам нужны специфичные для Firecrawl параметры поиска, а не общий `web_search`.

Основные параметры:

- `query`;
- `count`;
- `sources`;
- `categories`;
- `scrapeResults`;
- `timeoutSeconds`.

### `firecrawl_scrape`

Используйте этот инструмент для страниц, насыщенных JavaScript, или защищённых от ботов, где обычный `web_fetch` неэффективен.

Основные параметры:

- `url`;
- `extractMode`;
- `maxChars`;
- `onlyMainContent`;
- `maxAgeMs`;
- `proxy`;
- `storeInCache`;
- `timeoutSeconds`.

## Обход ботов (stealth)

Firecrawl предоставляет параметр **режима прокси** для обхода ботов (`basic`, `stealth` или `auto`).
OpenClaw всегда использует `proxy: "auto"` плюс `storeInCache: true` для запросов к Firecrawl.
Если параметр прокси не указан, Firecrawl по умолчанию использует `auto`. Режим `auto` повторяет попытку с использованием скрытных прокси, если базовая попытка не удаётся, что может потребовать больше кредитов, чем скрапинг только в базовом режиме.

## Как `web_fetch` использует Firecrawl

Порядок экстракции в `web_fetch`:

1. Readability (локально).
2. Firecrawl (если выбран или автоматически определён как активный резервный механизм web‑fetch).
3. Базовая очистка HTML (последний резервный механизм).

Параметр выбора — `tools.web.fetch.provider`. Если вы его не укажете, OpenClaw автоматически определит первый доступный провайдер web‑fetch на основе имеющихся учётных данных.
На данный момент встроенным провайдером является Firecrawl.

## Связанные материалы

- [Обзор веб‑поиска](/tools/web) — все провайдеры и автоматическое определение;
- [Web Fetch](/tools/web-fetch) — инструмент web_fetch с резервным механизмом Firecrawl;
- [Tavily](/tools/tavily) — инструменты поиска и экстракции.