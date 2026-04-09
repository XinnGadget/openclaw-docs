---
title: "Perplexity (провайдер)"
summary: "Настройка провайдера веб-поиска Perplexity (API-ключ, режимы поиска, фильтрация)"
read_when:
  - Вы хотите настроить Perplexity в качестве провайдера веб-поиска
  - Вам нужен API-ключ Perplexity или настройка прокси OpenRouter
---

# Perplexity (провайдер веб-поиска)

Плагин Perplexity предоставляет возможности веб-поиска через Perplexity Search API или Perplexity Sonar через OpenRouter.

<Note>
На этой странице описана настройка **провайдера** Perplexity. Чтобы узнать о **инструменте** Perplexity (о том, как его использует агент), см. [инструмент Perplexity](/tools/perplexity-search).
</Note>

- Тип: провайдер веб-поиска (не провайдер моделей)
- Аутентификация: `PERPLEXITY_API_KEY` (напрямую) или `OPENROUTER_API_KEY` (через OpenRouter)
- Путь к конфигурации: `plugins.entries.perplexity.config.webSearch.apiKey`

## Быстрый старт

1. Задайте API-ключ:

```bash
openclaw configure --section web
```

Или задайте его напрямую:

```bash
openclaw config set plugins.entries.perplexity.config.webSearch.apiKey "pplx-xxxxxxxxxxxx"
```

2. После настройки агент будет автоматически использовать Perplexity для веб-поиска.

## Режимы поиска

Плагин автоматически выбирает транспорт на основе префикса API-ключа:

| Префикс ключа | Транспорт | Возможности |
| --- | --- | --- |
| `pplx-` | Native Perplexity Search API | Структурированные результаты, фильтры по домену/языку/дате |
| `sk-or-` | OpenRouter (Sonar) | Ответы, синтезированные ИИ, со ссылками на источники |

## Фильтрация в Native API

При использовании Native Perplexity API (ключ `pplx-`) поиск поддерживает:

- **Страна**: двухбуквенный код страны
- **Язык**: код языка по стандарту ISO 639-1
- **Диапазон дат**: день, неделя, месяц, год
- **Фильтры доменов**: белый/чёрный список (максимум 20 доменов)
- **Бюджет контента**: `max_tokens`, `max_tokens_per_page`

## Примечание об окружении

Если шлюз запущен как демон (launchd/systemd), убедитесь, что `PERPLEXITY_API_KEY` доступен для этого процесса (например, в `~/.openclaw/.env` или через `env.shellEnv`).