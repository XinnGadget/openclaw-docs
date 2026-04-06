---
read_when:
    - Ви хочете використовувати моделі MiniMax в OpenClaw
    - Вам потрібні вказівки з налаштування MiniMax
summary: Використання моделей MiniMax в OpenClaw
title: MiniMax
x-i18n:
    generated_at: "2026-04-06T00:52:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9ca35c43cdde53f6f09d9e12d48ce09e4c099cf8cbe1407ac6dbb45b1422507e
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

Провайдер MiniMax в OpenClaw за замовчуванням використовує **MiniMax M2.7**.

MiniMax також надає:

- вбудований синтез мовлення через T2A v2
- вбудоване розуміння зображень через `MiniMax-VL-01`
- вбудовану генерацію музики через `music-2.5+`
- вбудований `web_search` через API пошуку MiniMax Coding Plan

Розподіл провайдерів:

- `minimax`: текстовий провайдер з автентифікацією ключем API, а також вбудовані генерація зображень, розуміння зображень, мовлення та вебпошук
- `minimax-portal`: текстовий провайдер з OAuth, а також вбудовані генерація зображень і розуміння зображень

## Лінійка моделей

- `MiniMax-M2.7`: розміщена модель міркування за замовчуванням.
- `MiniMax-M2.7-highspeed`: швидший рівень міркування M2.7.
- `image-01`: модель генерації зображень (генерація та редагування image-to-image).

## Генерація зображень

Плагін MiniMax реєструє модель `image-01` для інструмента `image_generate`. Вона підтримує:

- **Генерацію text-to-image** з керуванням співвідношенням сторін.
- **Редагування image-to-image** (референс об’єкта) з керуванням співвідношенням сторін.
- До **9 вихідних зображень** на запит.
- До **1 референсного зображення** на запит редагування.
- Підтримувані співвідношення сторін: `1:1`, `16:9`, `4:3`, `3:2`, `2:3`, `3:4`, `9:16`, `21:9`.

Щоб використовувати MiniMax для генерації зображень, установіть його як провайдера генерації зображень:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "minimax/image-01" },
    },
  },
}
```

Плагін використовує той самий `MINIMAX_API_KEY` або OAuth-автентифікацію, що й текстові моделі. Якщо MiniMax уже налаштовано, додаткова конфігурація не потрібна.

І `minimax`, і `minimax-portal` реєструють `image_generate` з тією самою
моделлю `image-01`. Конфігурації з ключем API використовують `MINIMAX_API_KEY`; конфігурації OAuth можуть натомість використовувати
вбудований шлях автентифікації `minimax-portal`.

Коли онбординг або налаштування з ключем API записують явні записи
`models.providers.minimax`, OpenClaw матеріалізує `MiniMax-M2.7` і
`MiniMax-M2.7-highspeed` з `input: ["text", "image"]`.

Сам вбудований каталог текстових моделей MiniMax залишається метаданими
лише для тексту, доки не з’явиться явна конфігурація цього провайдера.
Розуміння зображень окремо надається через медіапровайдера `MiniMax-VL-01`, що належить плагіну.

Див. [Генерація зображень](/uk/tools/image-generation), щоб ознайомитися зі спільними
параметрами інструмента, вибором провайдера та поведінкою аварійного перемикання.

## Генерація музики

Вбудований плагін `minimax` також реєструє генерацію музики через спільний
інструмент `music_generate`.

- Модель музики за замовчуванням: `minimax/music-2.5+`
- Також підтримує `minimax/music-2.5` і `minimax/music-2.0`
- Керування запитом: `lyrics`, `instrumental`, `durationSeconds`
- Формат виводу: `mp3`
- Запуски на основі сесій відокремлюються через спільний потік завдань/стану, включно з `action: "status"`

Щоб використовувати MiniMax як музичного провайдера за замовчуванням:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "minimax/music-2.5+",
      },
    },
  },
}
```

Див. [Генерація музики](/uk/tools/music-generation), щоб ознайомитися зі спільними
параметрами інструмента, вибором провайдера та поведінкою аварійного перемикання.

## Генерація відео

Вбудований плагін `minimax` також реєструє генерацію відео через спільний
інструмент `video_generate`.

- Модель відео за замовчуванням: `minimax/MiniMax-Hailuo-2.3`
- Режими: text-to-video і потоки з одним референсним зображенням
- Підтримує `aspectRatio` і `resolution`

Щоб використовувати MiniMax як провайдера відео за замовчуванням:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "minimax/MiniMax-Hailuo-2.3",
      },
    },
  },
}
```

Див. [Генерація відео](/uk/tools/video-generation), щоб ознайомитися зі спільними
параметрами інструмента, вибором провайдера та поведінкою аварійного перемикання.

## Розуміння зображень

Плагін MiniMax реєструє розуміння зображень окремо від текстового
каталогу:

- `minimax`: модель зображень за замовчуванням `MiniMax-VL-01`
- `minimax-portal`: модель зображень за замовчуванням `MiniMax-VL-01`

Саме тому автоматична маршрутизація медіа може використовувати MiniMax для розуміння зображень, навіть
коли вбудований каталог текстових провайдерів і далі показує чат-посилання M2.7 як метадані лише для тексту.

## Вебпошук

Плагін MiniMax також реєструє `web_search` через API пошуку MiniMax Coding Plan.

- Ідентифікатор провайдера: `minimax`
- Структуровані результати: заголовки, URL, фрагменти, пов’язані запити
- Бажана змінна середовища: `MINIMAX_CODE_PLAN_KEY`
- Підтримуваний псевдонім env: `MINIMAX_CODING_API_KEY`
- Запасний варіант сумісності: `MINIMAX_API_KEY`, якщо він уже вказує на токен coding-plan
- Повторне використання регіону: `plugins.entries.minimax.config.webSearch.region`, потім `MINIMAX_API_HOST`, потім базові URL провайдера MiniMax
- Пошук залишається на ідентифікаторі провайдера `minimax`; конфігурація OAuth CN/global і далі може опосередковано керувати регіоном через `models.providers.minimax-portal.baseUrl`

Конфігурація зберігається в `plugins.entries.minimax.config.webSearch.*`.
Див. [Пошук MiniMax](/uk/tools/minimax-search).

## Виберіть спосіб налаштування

### MiniMax OAuth (Coding Plan) - рекомендовано

**Найкраще для:** швидкого налаштування MiniMax Coding Plan через OAuth, без ключа API.

Пройдіть автентифікацію за допомогою явного регіонального варіанта OAuth:

```bash
openclaw onboard --auth-choice minimax-global-oauth
# або
openclaw onboard --auth-choice minimax-cn-oauth
```

Відповідність варіантів:

- `minimax-global-oauth`: міжнародні користувачі (`api.minimax.io`)
- `minimax-cn-oauth`: користувачі в Китаї (`api.minimaxi.com`)

Докладніше див. у README пакета плагіна MiniMax в репозиторії OpenClaw.

### MiniMax M2.7 (ключ API)

**Найкраще для:** розміщеного MiniMax із API, сумісним з Anthropic.

Налаштування через CLI:

- Інтерактивний онбординг:

```bash
openclaw onboard --auth-choice minimax-global-api
# або
openclaw onboard --auth-choice minimax-cn-api
```

- `minimax-global-api`: міжнародні користувачі (`api.minimax.io`)
- `minimax-cn-api`: користувачі в Китаї (`api.minimaxi.com`)

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "minimax/MiniMax-M2.7" } } },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
          {
            id: "MiniMax-M2.7-highspeed",
            name: "MiniMax M2.7 Highspeed",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.6, output: 2.4, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

У потоці streaming, сумісному з Anthropic, OpenClaw тепер вимикає thinking для MiniMax
за замовчуванням, якщо тільки ви явно не встановили `thinking` самостійно. Streaming endpoint MiniMax
повертає `reasoning_content` у дельта-фрагментах у стилі OpenAI
замість нативних блоків thinking Anthropic, що може призвести до витоку внутрішніх міркувань
у видимий вивід, якщо неявно залишити це увімкненим.

### MiniMax M2.7 як запасний варіант (приклад)

**Найкраще для:** зберегти вашу найсильнішу модель останнього покоління як основну, а за потреби перемикатися на MiniMax M2.7.
У прикладі нижче використовується Opus як конкретна основна модель; замініть її на бажану основну модель останнього покоління.

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "primary" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
    },
  },
}
```

## Налаштування через `openclaw configure`

Використовуйте інтерактивний майстер конфігурації, щоб налаштувати MiniMax без редагування JSON:

1. Запустіть `openclaw configure`.
2. Виберіть **Модель/автентифікація**.
3. Виберіть варіант автентифікації **MiniMax**.
4. Виберіть модель за замовчуванням, коли буде запропоновано.

Поточні варіанти автентифікації MiniMax у майстрі/CLI:

- `minimax-global-oauth`
- `minimax-cn-oauth`
- `minimax-global-api`
- `minimax-cn-api`

## Параметри конфігурації

- `models.providers.minimax.baseUrl`: бажано `https://api.minimax.io/anthropic` (сумісний з Anthropic); `https://api.minimax.io/v1` необов’язково для payload, сумісних з OpenAI.
- `models.providers.minimax.api`: бажано `anthropic-messages`; `openai-completions` необов’язково для payload, сумісних з OpenAI.
- `models.providers.minimax.apiKey`: ключ API MiniMax (`MINIMAX_API_KEY`).
- `models.providers.minimax.models`: визначте `id`, `name`, `reasoning`, `contextWindow`, `maxTokens`, `cost`.
- `agents.defaults.models`: створіть псевдоніми для моделей, які хочете додати до allowlist.
- `models.mode`: залишайте `merge`, якщо хочете додати MiniMax поряд із вбудованими провайдерами.

## Примітки

- Посилання на моделі залежать від шляху автентифікації:
  - Налаштування з ключем API: `minimax/<model>`
  - Налаштування з OAuth: `minimax-portal/<model>`
- Модель чату за замовчуванням: `MiniMax-M2.7`
- Альтернативна модель чату: `MiniMax-M2.7-highspeed`
- Для `api: "anthropic-messages"` OpenClaw додає
  `thinking: { type: "disabled" }`, якщо thinking ще не задано явно в
  params/config.
- `/fast on` або `params.fastMode: true` переписує `MiniMax-M2.7` на
  `MiniMax-M2.7-highspeed` у потоці streaming, сумісному з Anthropic.
- Онбординг і пряме налаштування з ключем API записують явні визначення моделей з
  `input: ["text", "image"]` для обох варіантів M2.7
- Вбудований каталог провайдера наразі показує посилання на чат як метадані
  лише для тексту, доки не з’явиться явна конфігурація провайдера MiniMax
- API використання Coding Plan: `https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains` (потрібен ключ coding plan).
- OpenClaw нормалізує використання MiniMax coding-plan до того самого відображення `% left`, яке
  використовується для інших провайдерів. Сирі поля `usage_percent` / `usagePercent` у MiniMax
  означають залишок квоти, а не спожиту квоту, тому OpenClaw інвертує їх.
  Поля з підрахунком мають пріоритет, якщо вони наявні. Коли API повертає `model_remains`,
  OpenClaw надає перевагу запису моделі чату, за потреби виводить мітку вікна з
  `start_time` / `end_time` і включає назву вибраної моделі
  до мітки плану, щоб вікна coding-plan було легше розрізняти.
- Знімки використання трактують `minimax`, `minimax-cn` і `minimax-portal` як
  одну й ту саму поверхню квоти MiniMax і надають перевагу збереженому MiniMax OAuth, перш ніж
  переходити до змінних середовища з ключем Coding Plan.
- Оновіть значення цін у `models.json`, якщо вам потрібне точне відстеження вартості.
- Реферальне посилання для MiniMax Coding Plan (знижка 10%): [https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
- Правила для провайдерів див. у [/concepts/model-providers](/uk/concepts/model-providers).
- Використовуйте `openclaw models list`, щоб підтвердити поточний ідентифікатор провайдера, а потім перемкніть його за допомогою
  `openclaw models set minimax/MiniMax-M2.7` або
  `openclaw models set minimax-portal/MiniMax-M2.7`.

## Усунення несправностей

### "Unknown model: minimax/MiniMax-M2.7"

Зазвичай це означає, що **провайдер MiniMax не налаштовано** (немає відповідного
запису провайдера й не знайдено профіль автентифікації/env-ключ MiniMax). Виправлення для цього
виявлення є у **2026.1.12**. Способи виправлення:

- Оновіть до **2026.1.12** (або запустіть із вихідного коду `main`), а потім перезапустіть gateway.
- Запустіть `openclaw configure` і виберіть варіант автентифікації **MiniMax**, або
- Додайте відповідний блок `models.providers.minimax` або
  `models.providers.minimax-portal` вручну, або
- Установіть `MINIMAX_API_KEY`, `MINIMAX_OAUTH_TOKEN` або профіль автентифікації MiniMax,
  щоб можна було впровадити відповідний провайдер.

Переконайтеся, що ідентифікатор моделі **чутливий до регістру**:

- Шлях з ключем API: `minimax/MiniMax-M2.7` або `minimax/MiniMax-M2.7-highspeed`
- Шлях OAuth: `minimax-portal/MiniMax-M2.7` або
  `minimax-portal/MiniMax-M2.7-highspeed`

Потім перевірте ще раз за допомогою:

```bash
openclaw models list
```
