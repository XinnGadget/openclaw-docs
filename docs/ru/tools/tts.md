 ---
summary: "Преобразование текста в речь (TTS) для исходящих ответов"
read_when:
  - Включение преобразования текста в речь для ответов
  - Настройка провайдеров TTS или ограничений
  - Использование команд `/tts`
title: "Преобразование текста в речь"
---

# Преобразование текста в речь (TTS)

OpenClaw может преобразовывать исходящие ответы в аудио с помощью ElevenLabs, Microsoft, MiniMax или OpenAI.
Это работает везде, где OpenClaw может отправлять аудио.

## Поддерживаемые сервисы

- **ElevenLabs** (основной или резервный провайдер)
- **Microsoft** (основной или резервный провайдер; текущая встроенная реализация использует `node-edge-tts`)
- **MiniMax** (основной или резервный провайдер; использует API T2A v2)
- **OpenAI** (основной или резервный провайдер; также используется для сводок)

### Примечания к сервису речи Microsoft

Встроенный провайдер речи Microsoft в настоящее время использует онлайн-сервис нейронного преобразования текста в речь Microsoft Edge через библиотеку `node-edge-tts`. Это размещённый сервис (не локальный), использующий конечные точки Microsoft, и он не требует API-ключа.

`node-edge-tts` предоставляет параметры конфигурации речи и форматы вывода, но не все параметры поддерживаются сервисом. Устаревшая конфигурация и директивы ввода с использованием `edge` по-прежнему работают и нормализуются до `microsoft`.

Поскольку этот сервис представляет собой общедоступный веб-сервис без опубликованного SLA или квоты, относитесь к нему как к сервису с наилучшим усилием. Если вам нужны гарантированные лимиты и поддержка, используйте OpenAI или ElevenLabs.

## Необязательные ключи

Если вы хотите использовать OpenAI, ElevenLabs или MiniMax:

- `ELEVENLABS_API_KEY` (или `XI_API_KEY`)
- `MINIMAX_API_KEY`
- `OPENAI_API_KEY`

Для сервиса речи Microsoft API-ключ **не требуется**.

Если настроено несколько провайдеров, сначала используется выбранный провайдер, а остальные выступают в качестве резервных вариантов. Для автоматического создания сводки используется настроенный `summaryModel` (или `agents.defaults.model.primary`), поэтому этот провайдер также должен быть аутентифицирован, если вы включаете создание сводок.

## Ссылки на сервисы

- [Руководство по преобразованию текста в речь OpenAI](https://platform.openai.com/docs/guides/text-to-speech)
- [Справочник API аудио OpenAI](https://platform.openai.com/docs/api-reference/audio)
- [Преобразование текста в речь ElevenLabs](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [Аутентификация ElevenLabs](https://elevenlabs.io/docs/api-reference/authentication)
- [MiniMax T2A v2 API](https://platform.minimaxi.com/document/T2A%20V2)
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)
- [Форматы вывода речи Microsoft](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## Включено ли по умолчанию?

Нет. Авто-TTS по умолчанию **выключен**. Включите его в конфигурации с помощью `messages.tts.auto` или локально с помощью `/tts on`.

Если `messages.tts.provider` не задан, OpenClaw выбирает первого настроенного провайдера речи в порядке автоматического выбора реестра.

## Конфигурация

Конфигурация TTS находится в разделе `messages.tts` в файле `openclaw.json`. Полная схема представлена в разделе [Конфигурация шлюза](/gateway/configuration).

### Минимальная конфигурация (включение + провайдер)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "elevenlabs",
    },
  },
}
```

### OpenAI как основной провайдер с резервным ElevenLabs

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "openai",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: {
        enabled: true,
      },
      providers: {
        openai: {
          apiKey: "openai_api_key",
          baseUrl: "https://api.openai.com/v1",
          model: "gpt-4o-mini-tts",
          voice: "alloy",
        },
        elevenlabs: {
          apiKey: "elevenlabs_api_key",
          baseUrl: "https://api.elevenlabs.io",
          voiceId: "voice_id",
          modelId: "eleven_multilingual_v2",
          seed: 42,
          applyTextNormalization: "auto",
          languageCode: "en",
          voiceSettings: {
            stability: 0.5,
            similarityBoost: 0.75,
            style: 0.0,
            useSpeakerBoost: true,
            speed: 1.0,
          },
        },
      },
    },
  },
}
```

### Microsoft как основной провайдер (без API-ключа)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "microsoft",
      providers: {
        microsoft: {
          enabled: true,
          voice: "en-US-MichelleNeural",
          lang: "en-US",
          outputFormat: "audio-24khz-48kbitrate-mono-mp3",
          rate: "+10%",
          pitch: "-5%",
        },
      },
    },
  },
}
```

### MiniMax как основной провайдер

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "minimax",
      providers: {
        minimax: {
          apiKey: "minimax_api_key",
          baseUrl: "https://api.minimax.io",
          model: "speech-2.8-hd",
          voiceId: "English_expressive_narrator",
          speed: 1.0,
          vol: 1.0,
          pitch: 0,
        },
      },
    },
  },
}
```

### Отключение речи Microsoft

```json5
{
  messages: {
    tts: {
      providers: {
        microsoft: {
          enabled: false,
        },
      },
    },
  },
}
```

### Пользовательские лимиты + путь к настройкам

```json5
{
  messages: {
    tts: {
      auto: "always",
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
    },
  },
}
```

### Отправка ответа только в аудиоформате после входящего голосового сообщения

```json5
{
  messages: {
    tts: {
      auto: "inbound",
    },
  },
}
```

### Отключение автоматического создания сводки для длинных ответов

```json5
{
  messages: {
    tts: {
      auto: "always",
    },
  },
}
```

Затем выполните:

```
/tts summary off
```

### Примечания к полям

- `auto`: режим авто-TTS (`off`, `always`, `inbound`, `tagged`).
  - `inbound` отправляет аудио только после входящего голосового сообщения.
  - `tagged` отправляет аудио только тогда, когда ответ содержит теги `[[tts]]`.
- `enabled`: устаревший переключатель (система переносит его в `auto`).
- `mode`: `"final"` (по умолчанию) или `"all"` (включает ответы инструментов/блоков).
- `provider`: идентификатор провайдера речи, например `"elevenlabs"`, `"microsoft"`, `"minimax"` или `"openai"` (резервный вариант выбирается автоматически).
- Если `provider` **не задан**, OpenClaw использует первого настроенного провайдера речи в порядке автоматического выбора реестра.
- Устаревший `provider: "edge"` по-прежнему работает и нормализуется до `microsoft`.
- `summaryModel`: необязательная дешёвая модель для автоматического создания сводки; по умолчанию используется `agents.defaults.model.primary`.
  - Принимает `provider/model` или настроенный псевдоним модели.
- `modelOverrides`: позволяет модели выдавать директивы TTS (включено по умолчанию).
  - `allowProvider` по умолчанию имеет значение `false` (переключение провайдеров требует явного разрешения).
- `providers.<id>`: настройки, принадлежащие провайдеру, с ключом по идентификатору провайдера речи.
- Устаревшие блоки прямого провайдера (`messages.tts.openai`, `messages.tts.elevenlabs`, `messages.tts.microsoft`, `messages.tts.edge`) автоматически переносятся в `messages.tts.providers.<id>` при загрузке.
- `maxTextLength`: жёсткое ограничение для ввода TTS (символы). Команда `/tts audio` завершится ошибкой, если ограничение превышено.
- `timeoutMs`: тайм-аут запроса (мс).
- `prefsPath`: переопределение пути к локальному JSON-файлу настроек (провайдер/лимиты/сводка).
- Значения `apiKey` возвращаются к переменным окружения (`ELEVENLABS_API_KEY`/`XI_API_KEY`, `MINIMAX_API_KEY`, `OPENAI_API_KEY`).
- `providers.elevenlabs.baseUrl`: переопределение базового URL API ElevenLabs.
- `providers.openai.baseUrl`: переопределение конечной точки TTS OpenAI.
  - Порядок разрешения: `messages.tts.providers.openai.baseUrl` -> `OPENAI_TTS_BASE_URL` -> `https://api.openai.com/v1`
  - Значения, отличные от стандартных, рассматриваются как совместимые с OpenAI конечные точки TTS, поэтому принимаются пользовательские имена моделей и голосов.
- `providers.elevenlabs.voiceSettings`:
  - `stability`, `similarityBoost`, `style`: `0..1`
  - `useSpeakerBoost`: `true|false`
  - `speed`: `0.5..2.0` (1.0 = нормально)
- `providers.elevenlabs.applyTextNormalization`: `auto|on|off`
- `providers.elevenlabs.languageCode`: двухбуквенный код ISO 639-1 (например, `en`, `de`)
- `providers.elevenlabs.seed`: целое число `0..4294967295` (максимально возможное детерминированное поведение)
- `providers.minimax.baseUrl`: переопределение базового URL API MiniMax (по умолчанию `https://api.minimax.io`, переменная окружения: `MINIMAX_API_HOST`).
- `providers.minimax.model`: модель TTS (по умолчанию `speech-2.8-hd`, переменная окружения: `MINIMAX_TTS_MODEL`).
- `providers.minimax.voiceId`: идентификатор голоса (по умолчанию `English_expressive_narrator`, переменная окружения: `MINIMAX_TTS_VOICE_ID`).
- `providers.minimax.speed`: скорость воспроизведения `0.5..2.0` (по умолчанию 1.0).
- `providers.minimax.vol`: громкость `(0, 10]` (по умолчанию 1.0; должна быть больше 0).
- `providers.minimax.pitch`: сдвиг высоты тона `-12..12` (по умолчанию 0).
- `providers.microsoft.enabled`: разрешение использования речи Microsoft (по умолчанию `true`; API-ключ не требуется).
- `providers.microsoft.voice`: имя нейронного голоса Microsoft (например, `en-US-MichelleNeural`).
- `providers.microsoft.lang`: код языка (например, `en-US`).
- `providers.microsoft.outputFormat`: формат вывода Microsoft (например, `audio-24khz-48kbitrate-mono-mp3`).
  - Смотрите форматы вывода речи Microsoft для допустимых значений; не все форматы поддерживаются встроенным транспортом на базе Edge.
- `providers.microsoft.rate` / `providers.microsoft.pitch` / `providers.microsoft.volume`: строки в процентах (например, `+10%`, `-5%`).
- `providers.microsoft.saveSubtitles`: запись JSON-субтитров вместе с аудиофайлом.
- `providers.microsoft.proxy`: URL прокси для запросов речи Microsoft.
- `providers.microsoft.timeoutMs`: переопределение тайм-аута запроса (мс).
- `edge.*`: устаревший псевдоним для тех же настроек Microsoft.

## Переопределения на основе модели (включено по умолчанию)

По умолчанию модель **может** выдавать директивы TTS для одного ответа. Когда `messages.tts.auto` имеет значение `tagged`, эти директивы необходимы для запуска аудио.

При включении модель может выдавать директивы `[[tts:...]]` для переопределения голоса для одного ответа, а также необязательный блок `[[tts:text]]...[[/tts:text]]` для предоставления выразительных тегов (смех, подсказки для пения и т. д.), которые должны отображаться только в аудио.

Директивы `provider=...` игнорируются, если не задано `modelOverrides.allowProvider: true`.

Пример полезной нагрузки ответа:

```
Вот, пожалуйста.

[[tts:voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](смеётся) Прочитай песню ещё раз.[[/tts:text]]
```

Доступные ключи директив (при включении):

- `provider` (зарегистрированный идентификатор провайдера речи, например `openai`, `elevenlabs`, `minimax` или `microsoft`; требует `allowProvider: true`)
- `voice` (голос OpenAI) или `voiceId` (ElevenLabs / MiniMax)
- `model` (модель TTS OpenAI, идентификатор модели ElevenLabs или модель MiniMax)
- `stability`, `similarityBoost`, `style`, `speed`, `useSpeakerBoost`
- `vol` / `volume` (громкость MiniMax, 0–10)
- `pitch` (высота тона MiniMax, от −12 до 12)
- `applyTextNormalization` (`auto|on|off`)
- `languageCode` (ISO 639-1)
- `seed`

Отключение всех переопределений модели:

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: false,
      },
    },
  },
}
```

Необязательный белый список (включение переключения провайдеров при сохранении возможности настройки других параметров):

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: true,
        allowProvider: true,
        allowSeed: false,
      },
    },
  },
}
```

## Предпочтения для отдельных пользователей

Команды с косой чертой записывают локальные переопределения в `prefsPath` (по умолчанию: `~/.openclaw/settings/tts.json`, переопределение с помощью `OPENCLAW_TTS_PREFS` или `messages.tts.prefsPath`).

Сохраняемые поля:

- `enabled`
- `provider`
- `maxLength` (порог сводки; по умолчанию 1500 символов)
- `summarize` (по умолчанию `true`)

Они переопределяют `messages.tts.*` для этого хоста.

## Форматы вывода (фиксированные)

- **Feishu / Matrix / Telegram / WhatsApp**: голосовое сообщение Opus (`opus_48000_64` от ElevenLabs, `opus` от OpenAI).
  - 48 кГц / 64 кбит/с — хороший компромисс для голосовых сообщений.
- **Другие каналы**: MP3 (`mp3_44100_128` от ElevenLabs, `mp3` от OpenAI).
  - 44,1 кГц / 128 кбит/с — баланс по умолчанию для чёткости речи.
- **MiniMax**: MP3 (`speech-2.8-hd` модель, частота дискретизации 32 кГц). Формат голосовых заметок изначально не поддерживается; используйте OpenAI или ElevenLabs для гарантированных голосовых сообщений Opus.
- **Microsoft**: использует `microsoft.outputFormat` (по умолчанию `audio-24khz-48kbitrate-mono-mp3`).
  - Встроенный транспорт принимает `outputFormat`, но не все форматы доступны в сервисе.
  - Значения формата вывода соответствуют форматам вывода речи Microsoft (включая Ogg/WebM Opus).
  - Telegram `sendVoice` принимает OGG/MP3/M4A; используйте OpenAI/ElevenLabs, если вам нужны гарантированные голосовые сообщения Opus.
  - Если настроенный формат вывода Microsoft не работает, OpenClaw повторяет попытку с MP3.

Форматы вывода OpenAI/ElevenLabs фиксированы для каждого канала (см. выше).

## Поведение авто-TTS

При включении OpenClaw:

- пропускает TTS, если ответ уже содержит медиа или директиву `MEDIA:`.
- пропускает очень короткие ответы (< 10 символов).
- создаёт сводку для длинных ответов, если она включена, с использованием `agents.defaults.model.primary` (или `summaryModel`).
- прикрепляет сгенерированное аудио к ответу.

Если ответ превышает `maxLength`, а создание сводки отключено (или отсутствует API-ключ для модели сводки), аудио пропускается и отправляется обычный текстовый ответ.

## Диаграмма потока

```
Ответ -> Включён TTS?
  нет -> отправить текст
  да -> есть медиа / MEDIA: / короткий?
          да -> отправить текст
          нет -> длина > лимита?
                  нет -> TTS -> прикрепить аудио
                  да -> включено создание сводки?
                          нет -> отправить текст
                          да -> создать сводку (summaryModel или agents.defaults.model.primary)
                                    -> TTS -> прикрепить аудио
```

## Использование команд с косой чертой

Есть одна команда: `/tts`.
Подробности включения см. в разделе [Команды с косой чертой](/tools/slash-commands).

Примечание для Discord: `/tts` — встроенная команда Discord, поэтому OpenClaw регистрирует `/voice` в качестве собственной команды там. Текст `/tts ...` по-прежнему работает.

```
/tts off
/tts on
/tts status
/tts provider openai
/tts limit 2000
/tts summary off
/tts audio Hello from OpenClaw
```

Примечания:

- Команды требуют авторизованного отправителя (правила белого списка/владельца по-прежнему применяются).
- Должна быть включена регистрация `commands.text` или собственных команд.
- Конфигурация `messages.tts.auto` принимает значения `off|always|inbound|tagged`.
- `/tts on` записывает локальное предпочтение TTS как `always`; `/tts off` записывает его как `off`.
- Используйте конфигурацию, если хотите установить значения по умолчанию `inbound` или `tagged`.
- `limit` и `summary` сохраняются в локальных настройках, а не в основной конфигурации.
- `/tts audio` генерирует разовый аудиоответ (не включает TTS).
- `/tts status` включает видимость резервного варианта для последней попытки:
  - успешный резервный вариант: `Fallback: <primary> -> <used>` плюс `Attempts: ...`
  - ошибка: `Error: ...` плюс `Attempts: ...`
  - подробная диагностика: `Attempt details: provider:outcome(reasonCode) latency`
- Сбои API OpenAI и ElevenLabs теперь включают детализированную ошибку провайдера и идентификатор запроса (если возвращается провайдером), которые отображаются в ошибках/журналах TTS.

## Инструмент агента

Инструмент `tts` преобразует текст в речь и возвращает аудио-вложение для доставки ответа. Когда канал — Feishu, Matrix, Telegram или WhatsApp, аудио доставляется как голосовое сообщение, а не как вложение файла.

## RPC шлюза

Методы шлюза:

- `tts.status`
- `tts.enable`
- `tts.disable`
- `tts.convert`
- `tts.setProvider`
- `tts.providers`