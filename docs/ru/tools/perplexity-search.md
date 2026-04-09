 ---
summary: "API поиска Perplexity и совместимость с Sonar/OpenRouter для web_search"
read_when:
  - Вы хотите использовать Perplexity Search для веб-поиска
  - Вам нужно настроить PERPLEXITY_API_KEY или OPENROUTER_API_KEY
title: "Perplexity Search"
---

# API поиска Perplexity

OpenClaw поддерживает API поиска Perplexity в качестве провайдера `web_search`.
Он возвращает структурированные результаты с полями `title`, `url` и `snippet`.

Для обеспечения совместимости OpenClaw также поддерживает устаревшие настройки Perplexity Sonar/OpenRouter.
Если вы используете `OPENROUTER_API_KEY`, ключ вида `sk-or-...` в `plugins.entries.perplexity.config.webSearch.apiKey` либо задаёте `plugins.entries.perplexity.config.webSearch.baseUrl` / `model`, провайдер переключается на путь chat-completions и возвращает синтезированные ИИ-ответы с цитатами вместо структурированных результатов API поиска.

## Получение API-ключа Perplexity

1. Создайте учётную запись Perplexity на [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api).
2. Сгенерируйте API-ключ в панели управления.
3. Сохраните ключ в конфигурации либо задайте `PERPLEXITY_API_KEY` в окружении Gateway.

## Совместимость с OpenRouter

Если вы уже использовали OpenRouter для Perplexity Sonar, оставьте `provider: "perplexity"` и задайте `OPENROUTER_API_KEY` в окружении Gateway либо сохраните ключ вида `sk-or-...` в `plugins.entries.perplexity.config.webSearch.apiKey`.

Дополнительные параметры управления совместимостью:

- `plugins.entries.perplexity.config.webSearch.baseUrl`
- `plugins.entries.perplexity.config.webSearch.model`

## Примеры конфигурации

### Нативный API поиска Perplexity

```json5
{
  plugins: {
    entries: {
      perplexity: {
        config: {
          webSearch: {
            apiKey: "pplx-...",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "perplexity",
      },
    },
  },
}
```

### Совместимость с OpenRouter / Sonar

```json5
{
  plugins: {
    entries: {
      perplexity: {
        config: {
          webSearch: {
            apiKey: "<openrouter-api-key>",
            baseUrl: "https://openrouter.ai/api/v1",
            model: "perplexity/sonar-pro",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "perplexity",
      },
    },
  },
}
```

## Где задать ключ

**Через конфигурацию:** выполните `openclaw configure --section web`. Ключ будет сохранён в `~/.openclaw/openclaw.json` в поле `plugins.entries.perplexity.config.webSearch.apiKey`.
Это поле также поддерживает объекты SecretRef.

**Через окружение:** задайте `PERPLEXITY_API_KEY` или `OPENROUTER_API_KEY` в окружении процесса Gateway. Для установки шлюза поместите его в `~/.openclaw/.env` (или в окружение вашей службы). См. [Env vars](/help/faq#env-vars-and-env-loading).

Если настроен `provider: "perplexity"`, а SecretRef ключа Perplexity не разрешён и нет запасного варианта в окружении, запуск/перезагрузка завершится с ошибкой.

## Параметры инструмента

Эти параметры применяются к нативному пути API поиска Perplexity.

| Параметр | Описание |
| --- | --- |
| `query` | Поисковый запрос (обязательный) |
| `count` | Количество возвращаемых результатов (1–10, по умолчанию: 5) |
| `country` | Двухбуквенный код страны по ISO (например, "US", "DE") |
| `language` | Код языка по ISO 639-1 (например, "en", "de", "fr") |
| `freshness` | Фильтр по времени: `day` (24 ч), `week`, `month` или `year` |
| `date_after` | Только результаты, опубликованные после указанной даты (ГГГГ-ММ-ДД) |
| `date_before` | Только результаты, опубликованные до указанной даты (ГГГГ-ММ-ДД) |
| `domain_filter` | Массив разрешённых/запрещённых доменов (максимум 20) |
| `max_tokens` | Общий бюджет контента (по умолчанию: 25 000, максимум: 1 000 000) |
| `max_tokens_per_page` | Лимит токенов на страницу (по умолчанию: 2048) |

Для устаревшего пути совместимости с Sonar/OpenRouter:

- Принимаются параметры `query`, `count` и `freshness`.
- `count` там используется только для совместимости; в ответе по-прежнему будет один синтезированный ответ с цитатами, а не список из N результатов.
- Фильтры, доступные только в API поиска (`country`, `language`, `date_after`, `date_before`, `domain_filter`, `max_tokens` и `max_tokens_per_page`), возвращают явные ошибки.

**Примеры:**

```javascript
// Поиск с учётом страны и языка
await web_search({
  query: "renewable energy",
  country: "DE",
  language: "de",
});

// Недавние результаты (за последнюю неделю)
await web_search({
  query: "AI news",
  freshness: "week",
});

// Поиск по диапазону дат
await web_search({
  query: "AI developments",
  date_after: "2024-01-01",
  date_before: "2024-06-30",
});

// Фильтрация по доменам (разрешённый список)
await web_search({
  query: "climate research",
  domain_filter: ["nature.com", "science.org", ".edu"],
});

// Фильтрация по доменам (запрещённый список — добавьте префикс -)
await web_search({
  query: "product reviews",
  domain_filter: ["-reddit.com", "-pinterest.com"],
});

// Извлечение большего объёма контента
await web_search({
  query: "detailed AI research",
  max_tokens: 50000,
  max_tokens_per_page: 4096,
});
```

### Правила фильтрации по доменам

- Максимум 20 доменов на фильтр.
- Нельзя смешивать разрешённый и запрещённый списки в одном запросе.
- Для записей запрещённого списка используйте префикс `-` (например, `["-reddit.com"]`).

## Примечания

- API поиска Perplexity возвращает структурированные результаты веб-поиска (`title`, `url`, `snippet`).
- OpenRouter или явное указание `plugins.entries.perplexity.config.webSearch.baseUrl` / `model` переключает Perplexity обратно на чат-дополнения Sonar для обеспечения совместимости.
- В режиме совместимости с Sonar/OpenRouter возвращается один синтезированный ответ с цитатами, а не структурированные строки результатов.
- По умолчанию результаты кэшируются на 15 минут (можно настроить через `cacheTtlMinutes`).

## Связанные материалы

- [Обзор веб-поиска](/tools/web) — все провайдеры и автоматическое определение.
- [Документация API поиска Perplexity](https://docs.perplexity.ai/docs/search/quickstart) — официальная документация Perplexity.
- [Brave Search](/tools/brave-search) — структурированные результаты с фильтрами по стране и языку.
- [Exa Search](/tools/exa-search) — нейронный поиск с извлечением контента.