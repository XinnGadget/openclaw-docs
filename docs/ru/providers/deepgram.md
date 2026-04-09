---
summary: "Транскрипция входящих голосовых заметок с помощью Deepgram"
read_when:
  - Вам нужна функция преобразования речи в текст (speech-to-text) от Deepgram для аудиовложений
  - Вам нужен пример быстрой настройки Deepgram
title: "Deepgram"
---

# Deepgram (транскрипция аудио)

Deepgram — это API для преобразования речи в текст (speech-to-text). В OpenClaw он используется для **транскрипции входящих аудио/голосовых заметок** через `tools.media.audio`.

При активации OpenClaw загружает аудиофайл в Deepgram и встраивает транскрипцию в конвейер ответов (`{{Transcript}}` + блок `[Audio]`). Это **не потоковая передача**; используется endpoint для транскрипции предварительно записанных файлов.

Сайт: [https://deepgram.com](https://deepgram.com)  
Документация: [https://developers.deepgram.com](https://developers.deepgram.com)

## Быстрый старт

1. Задайте свой API-ключ:

```
DEEPGRAM_API_KEY=dg_...
```

2. Включите провайдера:

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "deepgram", model: "nova-3" }],
      },
    },
  },
}
```

## Параметры

- `model`: идентификатор модели Deepgram (по умолчанию: `nova-3`)
- `language`: подсказка о языке (необязательно)
- `tools.media.audio.providerOptions.deepgram.detect_language`: включение определения языка (необязательно)
- `tools.media.audio.providerOptions.deepgram.punctuate`: включение пунктуации (необязательно)
- `tools.media.audio.providerOptions.deepgram.smart_format`: включение умного форматирования (необязательно)

Пример с указанием языка:

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "deepgram", model: "nova-3", language: "en" }],
      },
    },
  },
}
```

Пример с параметрами Deepgram:

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        providerOptions: {
          deepgram: {
            detect_language: true,
            punctuate: true,
            smart_format: true,
          },
        },
        models: [{ provider: "deepgram", model: "nova-3" }],
      },
    },
  },
}
```

## Примечания

- Аутентификация следует стандартному порядку аутентификации провайдера; самый простой способ — использовать `DEEPGRAM_API_KEY`.
- Переопределите endpoints или заголовки с помощью `tools.media.audio.baseUrl` и `tools.media.audio.headers` при использовании прокси.
- Вывод подчиняется тем же правилам для аудио, что и у других провайдеров (ограничения по размеру, тайм-ауты, встраивание транскрипции).