---
read_when:
    - Увімкнення перетворення тексту на мовлення для відповідей
    - Налаштування провайдерів TTS або обмежень
    - Використання команд `/tts`
summary: Перетворення тексту на мовлення (TTS) для вихідних відповідей
title: Text-to-Speech
x-i18n:
    generated_at: "2026-04-16T06:26:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: de7c1dc8831c1ba307596afd48cb4d36f844724887a13b17e35f41ef5174a86f
    source_path: tools/tts.md
    workflow: 15
---

# Перетворення тексту на мовлення (TTS)

OpenClaw може перетворювати вихідні відповіді на аудіо за допомогою ElevenLabs, Google Gemini, Microsoft, MiniMax або OpenAI.
Це працює всюди, де OpenClaw може надсилати аудіо.

## Підтримувані сервіси

- **ElevenLabs** (основний або резервний провайдер)
- **Google Gemini** (основний або резервний провайдер; використовує Gemini API TTS)
- **Microsoft** (основний або резервний провайдер; поточна вбудована реалізація використовує `node-edge-tts`)
- **MiniMax** (основний або резервний провайдер; використовує API T2A v2)
- **OpenAI** (основний або резервний провайдер; також використовується для підсумків)

### Примітки щодо мовлення Microsoft

Вбудований провайдер мовлення Microsoft наразі використовує онлайн-сервіс
нейронного TTS Microsoft Edge через бібліотеку `node-edge-tts`. Це хостований сервіс (не
локальний), він використовує кінцеві точки Microsoft і не потребує API-ключа.
`node-edge-tts` надає параметри конфігурації мовлення та вихідні формати, але
не всі параметри підтримуються сервісом. Застаріла конфігурація та введення директив
із використанням `edge` усе ще працюють і нормалізуються до `microsoft`.

Оскільки цей шлях використовує публічний вебсервіс без опублікованих SLA або квот,
вважайте його рішенням із найкращими можливими зусиллями. Якщо вам потрібні гарантовані ліміти та підтримка, використовуйте OpenAI
або ElevenLabs.

## Необов’язкові ключі

Якщо ви хочете використовувати OpenAI, ElevenLabs, Google Gemini або MiniMax:

- `ELEVENLABS_API_KEY` (або `XI_API_KEY`)
- `GEMINI_API_KEY` (або `GOOGLE_API_KEY`)
- `MINIMAX_API_KEY`
- `OPENAI_API_KEY`

Мовлення Microsoft **не** потребує API-ключа.

Якщо налаштовано кілька провайдерів, спочатку використовується вибраний провайдер, а інші стають резервними варіантами.
Автоматичне створення підсумків використовує налаштований `summaryModel` (або `agents.defaults.model.primary`),
тому якщо ви вмикаєте підсумки, цей провайдер також має бути автентифікований.

## Посилання на сервіси

- [Посібник OpenAI Text-to-Speech](https://platform.openai.com/docs/guides/text-to-speech)
- [Довідка API Audio OpenAI](https://platform.openai.com/docs/api-reference/audio)
- [ElevenLabs Text to Speech](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [Автентифікація ElevenLabs](https://elevenlabs.io/docs/api-reference/authentication)
- [MiniMax T2A v2 API](https://platform.minimaxi.com/document/T2A%20V2)
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)
- [Вихідні формати Microsoft Speech](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## Чи ввімкнено це за замовчуванням?

Ні. Автоматичний TTS **вимкнено** за замовчуванням. Увімкніть його в конфігурації через
`messages.tts.auto` або локально за допомогою `/tts on`.

Коли `messages.tts.provider` не задано, OpenClaw вибирає першого
налаштованого провайдера мовлення в порядку автоматичного вибору реєстру.

## Конфігурація

Конфігурація TTS розміщується в `messages.tts` у `openclaw.json`.
Повна схема наведена в [Конфігурація Gateway](/uk/gateway/configuration).

### Мінімальна конфігурація (увімкнення + провайдер)

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

### OpenAI як основний, ElevenLabs як резервний

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

### Microsoft як основний (без API-ключа)

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

### MiniMax як основний

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

### Google Gemini як основний

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "google",
      providers: {
        google: {
          apiKey: "gemini_api_key",
          model: "gemini-3.1-flash-tts-preview",
          voiceName: "Kore",
        },
      },
    },
  },
}
```

Google Gemini TTS використовує шлях API-ключа Gemini. API-ключ Google Cloud Console,
обмежений Gemini API, тут є дійсним, і це той самий тип ключа, який використовується
вбудованим провайдером генерації зображень Google. Порядок визначення:
`messages.tts.providers.google.apiKey` -> `models.providers.google.apiKey` ->
`GEMINI_API_KEY` -> `GOOGLE_API_KEY`.

### Вимкнення мовлення Microsoft

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

### Власні ліміти + шлях до prefs

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

### Відповідати лише аудіо після вхідного голосового повідомлення

```json5
{
  messages: {
    tts: {
      auto: "inbound",
    },
  },
}
```

### Вимкнення автоматичного підсумку для довгих відповідей

```json5
{
  messages: {
    tts: {
      auto: "always",
    },
  },
}
```

Потім виконайте:

```
/tts summary off
```

### Примітки щодо полів

- `auto`: режим автоматичного TTS (`off`, `always`, `inbound`, `tagged`).
  - `inbound` надсилає аудіо лише після вхідного голосового повідомлення.
  - `tagged` надсилає аудіо лише тоді, коли відповідь містить директиви `[[tts:key=value]]` або блок `[[tts:text]]...[[/tts:text]]`.
- `enabled`: застарілий перемикач (doctor мігрує його до `auto`).
- `mode`: `"final"` (типово) або `"all"` (включає відповіді інструментів/блоків).
- `provider`: ідентифікатор провайдера мовлення, наприклад `"elevenlabs"`, `"google"`, `"microsoft"`, `"minimax"` або `"openai"` (резервне перемикання відбувається автоматично).
- Якщо `provider` **не задано**, OpenClaw використовує першого налаштованого провайдера мовлення в порядку автоматичного вибору реєстру.
- Застарілий `provider: "edge"` усе ще працює та нормалізується до `microsoft`.
- `summaryModel`: необов’язкова недорога модель для автоматичного підсумку; типово використовується `agents.defaults.model.primary`.
  - Приймає `provider/model` або налаштований псевдонім моделі.
- `modelOverrides`: дозволяє моделі видавати директиви TTS (типово ввімкнено).
  - `allowProvider` типово має значення `false` (перемикання провайдера вмикається явно).
- `providers.<id>`: налаштування, що належать провайдеру, із ключем за ідентифікатором провайдера мовлення.
- Застарілі прямі блоки провайдерів (`messages.tts.openai`, `messages.tts.elevenlabs`, `messages.tts.microsoft`, `messages.tts.edge`) автоматично мігруються до `messages.tts.providers.<id>` під час завантаження.
- `maxTextLength`: жорстке обмеження для вхідного тексту TTS (символи). `/tts audio` завершується помилкою, якщо його перевищено.
- `timeoutMs`: тайм-аут запиту (мс).
- `prefsPath`: перевизначає локальний шлях до JSON-файлу prefs (провайдер/ліміт/підсумок).
- Значення `apiKey` резервно беруться зі змінних середовища (`ELEVENLABS_API_KEY`/`XI_API_KEY`, `GEMINI_API_KEY`/`GOOGLE_API_KEY`, `MINIMAX_API_KEY`, `OPENAI_API_KEY`).
- `providers.elevenlabs.baseUrl`: перевизначає базову URL-адресу API ElevenLabs.
- `providers.openai.baseUrl`: перевизначає кінцеву точку OpenAI TTS.
  - Порядок визначення: `messages.tts.providers.openai.baseUrl` -> `OPENAI_TTS_BASE_URL` -> `https://api.openai.com/v1`
  - Нетипові значення вважаються OpenAI-сумісними кінцевими точками TTS, тому приймаються власні назви моделей і голосів.
- `providers.elevenlabs.voiceSettings`:
  - `stability`, `similarityBoost`, `style`: `0..1`
  - `useSpeakerBoost`: `true|false`
  - `speed`: `0.5..2.0` (1.0 = звичайна швидкість)
- `providers.elevenlabs.applyTextNormalization`: `auto|on|off`
- `providers.elevenlabs.languageCode`: 2-літерний ISO 639-1 (наприклад, `en`, `de`)
- `providers.elevenlabs.seed`: ціле число `0..4294967295` (детермінованість у межах найкращих можливих зусиль)
- `providers.minimax.baseUrl`: перевизначає базову URL-адресу API MiniMax (типово `https://api.minimax.io`, env: `MINIMAX_API_HOST`).
- `providers.minimax.model`: модель TTS (типово `speech-2.8-hd`, env: `MINIMAX_TTS_MODEL`).
- `providers.minimax.voiceId`: ідентифікатор голосу (типово `English_expressive_narrator`, env: `MINIMAX_TTS_VOICE_ID`).
- `providers.minimax.speed`: швидкість відтворення `0.5..2.0` (типово 1.0).
- `providers.minimax.vol`: гучність `(0, 10]` (типово 1.0; має бути більшою за 0).
- `providers.minimax.pitch`: зміщення тону `-12..12` (типово 0).
- `providers.google.model`: модель Gemini TTS (типово `gemini-3.1-flash-tts-preview`).
- `providers.google.voiceName`: назва вбудованого голосу Gemini (типово `Kore`; також приймається `voice`).
- `providers.google.baseUrl`: перевизначає базову URL-адресу Gemini API. Приймається лише `https://generativelanguage.googleapis.com`.
  - Якщо `messages.tts.providers.google.apiKey` пропущено, TTS може повторно використати `models.providers.google.apiKey` перед резервним переходом до env.
- `providers.microsoft.enabled`: дозволяє використання мовлення Microsoft (типово `true`; без API-ключа).
- `providers.microsoft.voice`: назва нейронного голосу Microsoft (наприклад, `en-US-MichelleNeural`).
- `providers.microsoft.lang`: код мови (наприклад, `en-US`).
- `providers.microsoft.outputFormat`: вихідний формат Microsoft (наприклад, `audio-24khz-48kbitrate-mono-mp3`).
  - Дивіться вихідні формати Microsoft Speech для допустимих значень; не всі формати підтримуються вбудованим транспортом на основі Edge.
- `providers.microsoft.rate` / `providers.microsoft.pitch` / `providers.microsoft.volume`: рядки у відсотках (наприклад, `+10%`, `-5%`).
- `providers.microsoft.saveSubtitles`: записує JSON-субтитри поруч з аудіофайлом.
- `providers.microsoft.proxy`: URL-адреса проксі для запитів мовлення Microsoft.
- `providers.microsoft.timeoutMs`: перевизначення тайм-ауту запиту (мс).
- `edge.*`: застарілий псевдонім для тих самих налаштувань Microsoft.

## Перевизначення, керовані моделлю (типово ввімкнено)

Типово модель **може** видавати директиви TTS для однієї відповіді.
Коли `messages.tts.auto` має значення `tagged`, ці директиви потрібні для запуску аудіо.

Коли це ввімкнено, модель може видавати директиви `[[tts:...]]` для перевизначення голосу
для однієї відповіді, а також необов’язковий блок `[[tts:text]]...[[/tts:text]]` для
додавання виразних тегів (сміх, підказки для співу тощо), які мають з’являтися
лише в аудіо.

Директиви `provider=...` ігноруються, якщо не встановлено `modelOverrides.allowProvider: true`.

Приклад корисного навантаження відповіді:

```
Here you go.

[[tts:voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](laughs) Read the song once more.[[/tts:text]]
```

Доступні ключі директив (коли ввімкнено):

- `provider` (ідентифікатор зареєстрованого провайдера мовлення, наприклад `openai`, `elevenlabs`, `google`, `minimax` або `microsoft`; потребує `allowProvider: true`)
- `voice` (голос OpenAI), `voiceName` / `voice_name` / `google_voice` (голос Google) або `voiceId` (ElevenLabs / MiniMax)
- `model` (модель OpenAI TTS, ідентифікатор моделі ElevenLabs або модель MiniMax) або `google_model` (модель Google TTS)
- `stability`, `similarityBoost`, `style`, `speed`, `useSpeakerBoost`
- `vol` / `volume` (гучність MiniMax, 0-10)
- `pitch` (тон MiniMax, від -12 до 12)
- `applyTextNormalization` (`auto|on|off`)
- `languageCode` (ISO 639-1)
- `seed`

Вимкнення всіх перевизначень моделі:

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

Необов’язковий allowlist (увімкнення перемикання провайдера зі збереженням можливості налаштовувати інші параметри):

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

## Налаштування для окремих користувачів

Команди зі слешем записують локальні перевизначення в `prefsPath` (типово:
`~/.openclaw/settings/tts.json`, перевизначається через `OPENCLAW_TTS_PREFS` або
`messages.tts.prefsPath`).

Збережені поля:

- `enabled`
- `provider`
- `maxLength` (поріг підсумку; типово 1500 символів)
- `summarize` (типово `true`)

Вони перевизначають `messages.tts.*` для цього хоста.

## Вихідні формати (фіксовані)

- **Feishu / Matrix / Telegram / WhatsApp**: голосове повідомлення Opus (`opus_48000_64` від ElevenLabs, `opus` від OpenAI).
  - 48 кГц / 64 кбіт/с — це хороший компроміс для голосових повідомлень.
- **Інші канали**: MP3 (`mp3_44100_128` від ElevenLabs, `mp3` від OpenAI).
  - 44,1 кГц / 128 кбіт/с — типовий баланс для чіткості мовлення.
- **MiniMax**: MP3 (модель `speech-2.8-hd`, частота дискретизації 32 кГц). Формат голосових нотаток нативно не підтримується; використовуйте OpenAI або ElevenLabs, якщо вам потрібні гарантовані голосові повідомлення Opus.
- **Google Gemini**: Gemini API TTS повертає необроблений PCM 24 кГц. OpenClaw обгортає його у WAV для аудіовкладень і повертає PCM напряму для Talk/телефонії. Нативний формат голосових нотаток Opus у цьому шляху не підтримується.
- **Microsoft**: використовує `microsoft.outputFormat` (типово `audio-24khz-48kbitrate-mono-mp3`).
  - Вбудований транспорт приймає `outputFormat`, але не всі формати доступні в сервісі.
  - Значення вихідного формату відповідають вихідним форматам Microsoft Speech (включно з Ogg/WebM Opus).
  - Telegram `sendVoice` приймає OGG/MP3/M4A; використовуйте OpenAI/ElevenLabs, якщо вам потрібні
    гарантовані голосові повідомлення Opus.
  - Якщо налаштований вихідний формат Microsoft не спрацьовує, OpenClaw повторює спробу з MP3.

Вихідні формати OpenAI/ElevenLabs фіксовані для кожного каналу (див. вище).

## Поведінка автоматичного TTS

Коли ввімкнено, OpenClaw:

- пропускає TTS, якщо відповідь уже містить медіа або директиву `MEDIA:`.
- пропускає дуже короткі відповіді (< 10 символів).
- створює підсумок довгих відповідей, якщо це ввімкнено, за допомогою `agents.defaults.model.primary` (або `summaryModel`).
- додає згенероване аудіо до відповіді.

Якщо відповідь перевищує `maxLength`, а підсумок вимкнено (або немає API-ключа для
моделі підсумку), аудіо
пропускається, і надсилається звичайна текстова відповідь.

## Діаграма потоку

```
Reply -> TTS enabled?
  no  -> send text
  yes -> has media / MEDIA: / short?
          yes -> send text
          no  -> length > limit?
                   no  -> TTS -> attach audio
                   yes -> summary enabled?
                            no  -> send text
                            yes -> summarize (summaryModel or agents.defaults.model.primary)
                                      -> TTS -> attach audio
```

## Використання команд зі слешем

Є одна команда: `/tts`.
Докладніше про ввімкнення див. у [Команди зі слешем](/uk/tools/slash-commands).

Примітка для Discord: `/tts` — це вбудована команда Discord, тому OpenClaw реєструє
`/voice` як нативну команду там. Текстова команда `/tts ...` усе ще працює.

```
/tts off
/tts on
/tts status
/tts provider openai
/tts limit 2000
/tts summary off
/tts audio Hello from OpenClaw
```

Примітки:

- Команди потребують авторизованого відправника (правила allowlist/owner усе ще застосовуються).
- Має бути ввімкнено `commands.text` або реєстрацію нативних команд.
- Конфігурація `messages.tts.auto` приймає `off|always|inbound|tagged`.
- `/tts on` записує локальне налаштування TTS як `always`; `/tts off` записує його як `off`.
- Використовуйте конфігурацію, якщо вам потрібні типові значення `inbound` або `tagged`.
- `limit` і `summary` зберігаються в локальних prefs, а не в основній конфігурації.
- `/tts audio` генерує одноразову аудіовідповідь (не вмикає TTS).
- `/tts status` містить видимість резервного перемикання для останньої спроби:
  - успішне резервне перемикання: `Fallback: <primary> -> <used>` плюс `Attempts: ...`
  - помилка: `Error: ...` плюс `Attempts: ...`
  - докладна діагностика: `Attempt details: provider:outcome(reasonCode) latency`
- Збої API OpenAI та ElevenLabs тепер містять розібрані відомості про помилку провайдера та ідентифікатор запиту (коли його повертає провайдер), що відображається в помилках/журналах TTS.

## Інструмент агента

Інструмент `tts` перетворює текст на мовлення та повертає аудіовкладення для
доставки у відповіді. Коли каналом є Feishu, Matrix, Telegram або WhatsApp,
аудіо доставляється як голосове повідомлення, а не як файлове вкладення.

## Gateway RPC

Методи Gateway:

- `tts.status`
- `tts.enable`
- `tts.disable`
- `tts.convert`
- `tts.setProvider`
- `tts.providers`
