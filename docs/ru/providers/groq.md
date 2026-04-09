---
title: "Groq"
summary: "Настройка Groq (аутентификация + выбор модели)"
read_when:
  - Вы хотите использовать Groq с OpenClaw
  - Вам нужна переменная окружения с API-ключом или выбор аутентификации через CLI
---

# Groq

[Groq](https://groq.com) обеспечивает сверхбыстрый вывод (inference) на моделях с открытым исходным кодом (Llama, Gemma, Mistral и др.) с использованием специализированного оборудования LPU. OpenClaw подключается к Groq через API, совместимый с OpenAI.

- Поставщик: `groq`
- Аутентификация: `GROQ_API_KEY`
- API: совместимый с OpenAI

## Быстрый старт

1. Получите API-ключ на [console.groq.com/keys](https://console.groq.com/keys).

2. Установите API-ключ:

```bash
export GROQ_API_KEY="gsk_..."
```

3. Задайте модель по умолчанию:

```json5
{
  agents: {
    defaults: {
      model: { primary: "groq/llama-3.3-70b-versatile" },
    },
  },
}
```

## Пример конфигурационного файла

```json5
{
  env: { GROQ_API_KEY: "gsk_..." },
  agents: {
    defaults: {
      model: { primary: "groq/llama-3.3-70b-versatile" },
    },
  },
}
```

## Транскрипция аудио

Groq также предоставляет быструю транскрипцию аудио на основе Whisper. При настройке в качестве поставщика для понимания медиаконтента OpenClaw использует модель Groq `whisper-large-v3-turbo` для транскрипции голосовых сообщений через общий интерфейс `tools.media.audio`.

```json5
{
  tools: {
    media: {
      audio: {
        models: [{ provider: "groq" }],
      },
    },
  },
}
```

## Примечание об окружении

Если Gateway запускается как демон (launchd/systemd), убедитесь, что переменная `GROQ_API_KEY` доступна для этого процесса (например, в `~/.openclaw/.env` или через `env.shellEnv`).

## Примечания по работе с аудио

- Общий путь к конфигурации: `tools.media.audio`
- Базовый URL для аудио в Groq по умолчанию: `https://api.groq.com/openai/v1`
- Модель для аудио в Groq по умолчанию: `whisper-large-v3-turbo`
- Для транскрипции аудио Groq использует совместимый с OpenAI путь `/audio/transcriptions`

## Доступные модели

Каталог моделей Groq часто обновляется. Чтобы увидеть доступные на данный момент модели, выполните команду `openclaw models list | grep groq` или проверьте страницу [console.groq.com/docs/models](https://console.groq.com/docs/models).

Популярные варианты:

- **Llama 3.3 70B Versatile** — общего назначения, большой контекст
- **Llama 3.1 8B Instant** — быстрая, лёгкая
- **Gemma 2 9B** — компактная, эффективная
- **Mixtral 8x7B** — архитектура MoE, сильные возможности рассуждения

## Ссылки

- [Консоль Groq](https://console.groq.com)
- [Документация по API](https://console.groq.com/docs)
- [Список моделей](https://console.groq.com/docs/models)
- [Цены](https://groq.com/pricing)