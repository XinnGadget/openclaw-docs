---
title: "Google (Gemini)"
summary: "Настройка Google Gemini (ключ API + OAuth, генерация изображений, понимание медиаконтента, веб-поиск)"
read_when:
  - Вы хотите использовать модели Google Gemini с OpenClaw
  - Вам нужен ключ API или поток аутентификации OAuth
---

# Google (Gemini)

Плагин Google предоставляет доступ к моделям Gemini через Google AI Studio, а также к функциям генерации изображений, понимания медиаконтента (изображения/аудио/видео) и веб-поиска через Gemini Grounding.

- Поставщик: `google`
- Аутентификация: `GEMINI_API_KEY` или `GOOGLE_API_KEY`
- API: Google Gemini API
- Альтернативный поставщик: `google-gemini-cli` (OAuth)

## Быстрый старт

1. Задайте ключ API:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. Задайте модель по умолчанию:

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## Пример в неинтерактивном режиме

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## OAuth (Gemini CLI)

Альтернативный поставщик `google-gemini-cli` использует PKCE OAuth вместо ключа API. Это неофициальная интеграция; некоторые пользователи сообщают об ограничениях для учётных записей. Используйте на свой риск.

- Модель по умолчанию: `google-gemini-cli/gemini-3-flash-preview`
- Псевдоним: `gemini-cli`
- Предварительное требование: локальный Gemini CLI должен быть доступен как `gemini`
  - Homebrew: `brew install gemini-cli`
  - npm: `npm install -g @google/gemini-cli`
- Вход в систему:

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

Переменные окружения:

- `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
- `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

(Или варианты `GEMINI_CLI_*`.)

Если запросы OAuth через Gemini CLI завершаются ошибкой после входа в систему, задайте `GOOGLE_CLOUD_PROJECT` или `GOOGLE_CLOUD_PROJECT_ID` на хосте шлюза и повторите попытку.

Если вход в систему завершается ошибкой до начала потока в браузере, убедитесь, что локальная команда `gemini` установлена и находится в `PATH`. OpenClaw поддерживает установки через Homebrew и глобальные установки через npm, включая распространённые конфигурации для Windows/npm.

Примечания по использованию JSON в Gemini CLI:

- Текст ответа поступает из поля `response` в JSON CLI.
- Использование возвращается к `stats`, если CLI оставляет поле `usage` пустым.
- `stats.cached` преобразуется в `cacheRead` в OpenClaw.
- Если `stats.input` отсутствует, OpenClaw вычисляет входные токены на основе `stats.input_tokens - stats.cached`.

## Возможности

| Возможность | Поддерживается |
| --- | --- |
| Чат-дополнения | Да |
| Генерация изображений | Да |
| Генерация музыки | Да |
| Понимание изображений | Да |
| Транскрипция аудио | Да |
| Понимание видео | Да |
| Веб-поиск (Grounding) | Да |
| Мышление/рассуждения | Да (Gemini 3.1+) |
| Модели Gemma 4 | Да |

Модели Gemma 4 (например, `gemma-4-26b-a4b-it`) поддерживают режим мышления. OpenClaw преобразует `thinkingBudget` в поддерживаемый Google `thinkingLevel` для Gemma 4. Установка значения `thinking` в `off` сохраняет отключённое мышление вместо сопоставления с `MINIMAL`.

## Повторное использование кэша Gemini напрямую

Для прямых вызовов API Gemini (`api: "google-generative-ai"`) OpenClaw теперь передаёт настроенный дескриптор `cachedContent` в запросы к Gemini.

- Настройте параметры для конкретной модели или глобальные параметры с помощью `cachedContent` или устаревшего `cached_content`
- Если присутствуют оба параметра, приоритет имеет `cachedContent`
- Пример значения: `cachedContents/prebuilt-context`
- Использование кэша Gemini (cache-hit) преобразуется в `cacheRead` в OpenClaw из `cachedContentTokenCount` на стороне поставщика

Пример:

```json5
{
  agents: {
    defaults: {
      models: {
        "google/gemini-2.5-pro": {
          params: {
            cachedContent: "cachedContents/prebuilt-context",
          },
        },
      },
    },
  },
}
```

## Генерация изображений

Встроенный поставщик генерации изображений `google` по умолчанию использует `google/gemini-3.1-flash-image-preview`.

- Также поддерживает `google/gemini-3-pro-image-preview`
- Генерация: до 4 изображений за запрос
- Режим редактирования: включён, до 5 входных изображений
- Управление геометрией: `size`, `aspectRatio` и `resolution`

Поставщик `google-gemini-cli`, доступный только через OAuth, представляет собой отдельный интерфейс для текстового вывода. Генерация изображений, понимание медиаконтента и Gemini Grounding остаются на поставщике с идентификатором `google`.

Чтобы использовать Google в качестве поставщика изображений по умолчанию:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "google/gemini-3.1-flash-image-preview",
      },
    },
  },
}
```

См. [Генерация изображений](/tools/image-generation) для общих параметров инструмента, выбора поставщика и поведения при отказоустойчивости.

## Генерация видео

Встроенный плагин `google` также регистрирует генерацию видео через общий инструмент `video_generate`.

- Модель видео по умолчанию: `google/veo-3.1-fast-generate-preview`
- Режимы: текст-в-видео, изображение-в-видео и потоки с одним эталонным видео
- Поддерживает `aspectRatio`, `resolution` и `audio`
- Текущее ограничение по длительности: **от 4 до 8 секунд**

Чтобы использовать Google в качестве поставщика видео по умолчанию:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
      },
    },
  },
}
```

См. [Генерация видео](/tools/video-generation) для общих параметров инструмента, выбора поставщика и поведения при отказоустойчивости.

## Генерация музыки

Встроенный плагин `google` также регистрирует генерацию музыки через общий инструмент `music_generate`.

- Модель музыки по умолчанию: `google/lyria-3-clip-preview`
- Также поддерживает `google/lyria-3-pro-preview`
- Управление подсказками: `lyrics` и `instrumental`
- Формат вывода: `mp3` по умолчанию, а также `wav` в `google/lyria-3-pro-preview`
- Эталонные входные данные: до 10 изображений
- Запуски с поддержкой сеансов отделяются через общий поток задач/статусов, включая `action: "status"`

Чтобы использовать Google в качестве поставщика музыки по умолчанию:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
      },
    },
  },
}
```

См. [Генерация музыки](/tools/music-generation) для общих параметров инструмента, выбора поставщика и поведения при отказоустойчивости.

## Примечание об окружении

Если шлюз работает как демон (launchd/systemd), убедитесь, что `GEMINI_API_KEY` доступен для этого процесса (например, в `~/.openclaw/.env` или через `env.shellEnv`).