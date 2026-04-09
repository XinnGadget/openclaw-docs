---
title: "Arcee AI"
summary: "Настройка Arcee AI (аутентификация + выбор модели)"
read_when:
  - Вы хотите использовать Arcee AI с OpenClaw
  - Вам нужна переменная окружения с API-ключом или выбор аутентификации через CLI
---

# Arcee AI

[Arcee AI](https://arcee.ai) предоставляет доступ к семейству моделей mixture-of-experts (смесь экспертов) Trinity через API, совместимый с OpenAI. Все модели Trinity распространяются под лицензией Apache 2.0.

Доступ к моделям Arcee AI можно получить напрямую через платформу Arcee или через [OpenRouter](/providers/openrouter).

- Поставщик: `arcee`
- Аутентификация: `ARCEEAI_API_KEY` (напрямую) или `OPENROUTER_API_KEY` (через OpenRouter)
- API: совместим с OpenAI
- Базовый URL: `https://api.arcee.ai/api/v1` (напрямую) или `https://openrouter.ai/api/v1` (OpenRouter)

## Быстрый старт

1. Получите API-ключ на [Arcee AI](https://chat.arcee.ai/) или [OpenRouter](https://openrouter.ai/keys).

2. Задайте API-ключ (рекомендуется сохранить его для Gateway):

```bash
# Напрямую (платформа Arcee)
openclaw onboard --auth-choice arceeai-api-key

# Через OpenRouter
openclaw onboard --auth-choice arceeai-openrouter
```

3. Задайте модель по умолчанию:

```json5
{
  agents: {
    defaults: {
      model: { primary: "arcee/trinity-large-thinking" },
    },
  },
}
```

## Пример без интерактивного взаимодействия

```bash
# Напрямую (платформа Arcee)
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-api-key \
  --arceeai-api-key "$ARCEEAI_API_KEY"

# Через OpenRouter
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-openrouter \
  --openrouter-api-key "$OPENROUTER_API_KEY"
```

## Примечание об окружении

Если Gateway работает как демон (launchd/systemd), убедитесь, что переменная `ARCEEAI_API_KEY` (или `OPENROUTER_API_KEY`) доступна для этого процесса (например, в `~/.openclaw/.env` или через `env.shellEnv`).

## Встроенный каталог

В настоящее время OpenClaw поставляется со следующим встроенным каталогом Arcee:

| Ссылка на модель | Название | Ввод | Контекст | Стоимость (вход/выход за 1 млн) | Примечания |
| --- | --- | --- | --- | --- | --- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | текст | 256 К | 0,25 $ / 0,90 $ | Модель по умолчанию; включено рассуждение |
| `arcee/trinity-large-preview` | Trinity Large Preview | текст | 128 К | 0,25 $ / 1,00 $ | Универсального назначения; 400 млрд параметров, 13 млрд активных |
| `arcee/trinity-mini` | Trinity Mini 26B | текст | 128 К | 0,045 $ / 0,15 $ | Быстрая и экономичная; поддержка вызова функций |

Те же ссылки на модели работают как для прямого подключения, так и для настройки через OpenRouter (например, `arcee/trinity-large-thinking`).

Предустановка при подключении задаёт `arcee/trinity-large-thinking` в качестве модели по умолчанию.

## Поддерживаемые функции

- Потоковая передача (streaming)
- Использование инструментов / вызов функций (tool use / function calling)
- Структурированный вывод (режим JSON и схема JSON)
- Расширенное рассуждение (extended thinking, Trinity Large Thinking)