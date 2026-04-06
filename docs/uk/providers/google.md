---
read_when:
    - Ви хочете використовувати моделі Google Gemini з OpenClaw
    - Вам потрібен потік автентифікації за ключем API
summary: Налаштування Google Gemini (ключ API, генерація зображень, розуміння медіа, вебпошук)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-06T00:51:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 358d33a68275b01ebd916a3621dd651619cb9a1d062e2fb6196a7f3c501c015a
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Плагін Google надає доступ до моделей Gemini через Google AI Studio, а також до
генерації зображень, розуміння медіа (зображення/аудіо/відео) і вебпошуку через
Gemini Grounding.

- Провайдер: `google`
- Автентифікація: `GEMINI_API_KEY` або `GOOGLE_API_KEY`
- API: Google Gemini API

## Швидкий старт

1. Установіть ключ API:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. Установіть модель за замовчуванням:

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## Неінтерактивний приклад

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## Можливості

| Можливість             | Підтримується     |
| ---------------------- | ----------------- |
| Завершення чату        | Так               |
| Генерація зображень    | Так               |
| Генерація музики       | Так               |
| Розуміння зображень    | Так               |
| Транскрибування аудіо  | Так               |
| Розуміння відео        | Так               |
| Вебпошук (Grounding)   | Так               |
| Мислення/міркування    | Так (Gemini 3.1+) |

## Пряме повторне використання кешу Gemini

Для прямих запусків Gemini API (`api: "google-generative-ai"`) OpenClaw тепер
передає налаштований дескриптор `cachedContent` у запити до Gemini.

- Налаштовуйте параметри для окремої моделі або глобально за допомогою
  `cachedContent` або застарілого `cached_content`
- Якщо присутні обидва, пріоритет має `cachedContent`
- Приклад значення: `cachedContents/prebuilt-context`
- Використання Gemini cache-hit нормалізується в OpenClaw як `cacheRead` з
  вхідного `cachedContentTokenCount`

Приклад:

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

## Генерація зображень

Вбудований провайдер генерації зображень `google` за замовчуванням використовує
`google/gemini-3.1-flash-image-preview`.

- Також підтримує `google/gemini-3-pro-image-preview`
- Генерація: до 4 зображень на запит
- Режим редагування: увімкнено, до 5 вхідних зображень
- Керування геометрією: `size`, `aspectRatio` і `resolution`

Генерація зображень, розуміння медіа та Gemini Grounding усе ще використовують
ідентифікатор провайдера `google`.

Щоб використовувати Google як провайдера зображень за замовчуванням:

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

Див. [Генерація зображень](/uk/tools/image-generation), щоб дізнатися про спільні
параметри інструмента, вибір провайдера та поведінку аварійного перемикання.

## Генерація відео

Вбудований плагін `google` також реєструє генерацію відео через спільний
інструмент `video_generate`.

- Модель відео за замовчуванням: `google/veo-3.1-fast-generate-preview`
- Режими: text-to-video, image-to-video і потоки з одним еталонним відео
- Підтримує `aspectRatio`, `resolution` і `audio`
- Поточне обмеження тривалості: **від 4 до 8 секунд**

Щоб використовувати Google як провайдера відео за замовчуванням:

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

Див. [Генерація відео](/uk/tools/video-generation), щоб дізнатися про спільні
параметри інструмента, вибір провайдера та поведінку аварійного перемикання.

## Генерація музики

Вбудований плагін `google` також реєструє генерацію музики через спільний
інструмент `music_generate`.

- Модель музики за замовчуванням: `google/lyria-3-clip-preview`
- Також підтримує `google/lyria-3-pro-preview`
- Керування запитом: `lyrics` і `instrumental`
- Формат виводу: `mp3` за замовчуванням, а також `wav` для `google/lyria-3-pro-preview`
- Еталонні вхідні дані: до 10 зображень
- Запуски на основі сесій відокремлюються через спільний потік завдань/стану, включно з `action: "status"`

Щоб використовувати Google як музичного провайдера за замовчуванням:

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

Див. [Генерація музики](/uk/tools/music-generation), щоб дізнатися про спільні
параметри інструмента, вибір провайдера та поведінку аварійного перемикання.

## Примітка щодо середовища

Якщо Gateway працює як демон (launchd/systemd), переконайтеся, що `GEMINI_API_KEY`
доступний цьому процесу (наприклад, у `~/.openclaw/.env` або через
`env.shellEnv`).
