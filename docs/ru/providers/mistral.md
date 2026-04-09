---
summary: "Использование моделей Mistral и транскрипции Voxtral с OpenClaw"
read_when:
  - Вы хотите использовать модели Mistral в OpenClaw
  - Вам нужна настройка API-ключа Mistral и ссылки на модели
title: "Mistral"
---

# Mistral

OpenClaw поддерживает Mistral как для маршрутизации моделей текста/изображений (`mistral/...`), так и для транскрипции аудио с помощью Voxtral в рамках понимания медиаконтента.
Mistral также можно использовать для встраивания памяти (`memorySearch.provider = "mistral"`).

## Настройка через CLI

```bash
openclaw onboard --auth-choice mistral-api-key
# или в неинтерактивном режиме
openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
```

## Фрагмент конфигурации (провайдер LLM)

```json5
{
  env: { MISTRAL_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
}
```

## Встроенный каталог LLM

В настоящее время OpenClaw поставляется со следующим встроенным каталогом Mistral:

| Ссылка на модель | Входные данные | Контекст | Максимальный объём вывода | Примечания |
| --- | --- | --- | --- | --- |
| `mistral/mistral-large-latest` | текст, изображение | 262 144 | 16 384 | Модель по умолчанию |
| `mistral/mistral-medium-2508` | текст, изображение | 262 144 | 8 192 | Mistral Medium 3.1 |
| `mistral/mistral-small-latest` | текст, изображение | 128 000 | 16 384 | Mistral Small 4; регулируемое рассуждение через API `reasoning_effort` |
| `mistral/pixtral-large-latest` | текст, изображение | 128 000 | 32 768 | Pixtral |
| `mistral/codestral-latest` | текст | 256 000 | 4 096 | Для кодирования |
| `mistral/devstral-medium-latest` | текст | 262 144 | 32 768 | Devstral 2 |
| `mistral/magistral-small` | текст | 128 000 | 40 000 | С поддержкой рассуждений |

## Фрагмент конфигурации (транскрипция аудио с Voxtral)

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

## Регулируемое рассуждение (`mistral-small-latest`)

`mistral/mistral-small-latest` соответствует Mistral Small 4 и поддерживает [регулируемое рассуждение](https://docs.mistral.ai/capabilities/reasoning/adjustable) в API Chat Completions через параметр `reasoning_effort` (`none` минимизирует дополнительные рассуждения в выводе; `high` отображает полные цепочки рассуждений перед окончательным ответом).

OpenClaw сопоставляет уровень **рассуждений** сессии с API Mistral:

- **off** / **minimal** → `none`
- **low** / **medium** / **high** / **xhigh** / **adaptive** → `high`

Другие модели из встроенного каталога Mistral не используют этот параметр; используйте модели `magistral-*`, если вам нужно поведение Mistral с приоритетом рассуждений.

## Примечания

- Для аутентификации Mistral используется `MISTRAL_API_KEY`.
- Базовый URL провайдера по умолчанию: `https://api.mistral.ai/v1`.
- Модель по умолчанию при настройке: `mistral/mistral-large-latest`.
- Модель аудио по умолчанию для понимания медиаконтента в Mistral: `voxtral-mini-latest`.
- Путь для транскрипции медиа использует `/v1/audio/transcriptions`.
- Путь для встраивания памяти использует `/v1/embeddings` (модель по умолчанию: `mistral-embed`).