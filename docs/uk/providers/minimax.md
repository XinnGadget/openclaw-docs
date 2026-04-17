---
read_when:
    - Ви хочете моделі MiniMax в OpenClaw
    - Вам потрібні вказівки з налаштування MiniMax
summary: Використовуйте моделі MiniMax в OpenClaw
title: MiniMax
x-i18n:
    generated_at: "2026-04-12T10:03:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: ee9c89faf57384feb66cda30934000e5746996f24b59122db309318f42c22389
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

Постачальник MiniMax в OpenClaw типово використовує **MiniMax M2.7**.

MiniMax також надає:

- Вбудований синтез мовлення через T2A v2
- Вбудоване розуміння зображень через `MiniMax-VL-01`
- Вбудовану генерацію музики через `music-2.5+`
- Вбудований `web_search` через API пошуку MiniMax Coding Plan

Розподіл постачальників:

| ID постачальника | Автентифікація | Можливості                                                      |
| ---------------- | -------------- | --------------------------------------------------------------- |
| `minimax`        | API key        | Текст, генерація зображень, розуміння зображень, мовлення, вебпошук |
| `minimax-portal` | OAuth          | Текст, генерація зображень, розуміння зображень                 |

## Лінійка моделей

| Модель                   | Тип              | Опис                                     |
| ------------------------ | ---------------- | ---------------------------------------- |
| `MiniMax-M2.7`           | Чат (міркування) | Типова розміщена модель для міркування   |
| `MiniMax-M2.7-highspeed` | Чат (міркування) | Швидший рівень міркування M2.7           |
| `MiniMax-VL-01`          | Бачення          | Модель розуміння зображень               |
| `image-01`               | Генерація зображень | Перетворення тексту на зображення та редагування зображення за зображенням |
| `music-2.5+`             | Генерація музики | Типова музична модель                    |
| `music-2.5`              | Генерація музики | Попередній рівень генерації музики       |
| `music-2.0`              | Генерація музики | Застарілий рівень генерації музики       |
| `MiniMax-Hailuo-2.3`     | Генерація відео  | Потоки перетворення тексту на відео та з опорним зображенням |

## Початок роботи

Виберіть бажаний метод автентифікації та виконайте кроки налаштування.

<Tabs>
  <Tab title="OAuth (Coding Plan)">
    **Найкраще для:** швидкого налаштування MiniMax Coding Plan через OAuth, API key не потрібен.

    <Tabs>
      <Tab title="International">
        <Steps>
          <Step title="Run onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-global-oauth
            ```

            Це автентифікує через `api.minimax.io`.
          </Step>
          <Step title="Verify the model is available">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="China">
        <Steps>
          <Step title="Run onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-cn-oauth
            ```

            Це автентифікує через `api.minimaxi.com`.
          </Step>
          <Step title="Verify the model is available">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    <Note>
    Налаштування OAuth використовують ID постачальника `minimax-portal`. Посилання на моделі мають формат `minimax-portal/MiniMax-M2.7`.
    </Note>

    <Tip>
    Реферальне посилання для MiniMax Coding Plan (знижка 10%): [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
    </Tip>

  </Tab>

  <Tab title="API key">
    **Найкраще для:** розміщеного MiniMax із API, сумісним з Anthropic.

    <Tabs>
      <Tab title="International">
        <Steps>
          <Step title="Run onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-global-api
            ```

            Це налаштовує `api.minimax.io` як базову URL-адресу.
          </Step>
          <Step title="Verify the model is available">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="China">
        <Steps>
          <Step title="Run onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-cn-api
            ```

            Це налаштовує `api.minimaxi.com` як базову URL-адресу.
          </Step>
          <Step title="Verify the model is available">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    ### Приклад конфігурації

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

    <Warning>
    У сумісному з Anthropic потоці потокової передачі OpenClaw типово вимикає thinking для MiniMax, якщо ви явно не встановите `thinking` самостійно. Потокова кінцева точка MiniMax видає `reasoning_content` у дельта-фрагментах у стилі OpenAI замість власних блоків thinking Anthropic, через що внутрішні міркування можуть потрапити у видимий вивід, якщо залишити це неявно увімкненим.
    </Warning>

    <Note>
    Налаштування з API key використовують ID постачальника `minimax`. Посилання на моделі мають формат `minimax/MiniMax-M2.7`.
    </Note>

  </Tab>
</Tabs>

## Налаштування через `openclaw configure`

Використовуйте інтерактивний майстер конфігурації, щоб налаштувати MiniMax без редагування JSON:

<Steps>
  <Step title="Launch the wizard">
    ```bash
    openclaw configure
    ```
  </Step>
  <Step title="Select Model/auth">
    Виберіть **Model/auth** у меню.
  </Step>
  <Step title="Choose a MiniMax auth option">
    Виберіть один із доступних варіантів автентифікації MiniMax:

    | Варіант автентифікації | Опис |
    | --- | --- |
    | `minimax-global-oauth` | International OAuth (Coding Plan) |
    | `minimax-cn-oauth` | China OAuth (Coding Plan) |
    | `minimax-global-api` | International API key |
    | `minimax-cn-api` | China API key |

  </Step>
  <Step title="Pick your default model">
    Виберіть типову модель, коли з’явиться запит.
  </Step>
</Steps>

## Можливості

### Генерація зображень

Plugin MiniMax реєструє модель `image-01` для інструмента `image_generate`. Вона підтримує:

- **Генерація зображень із тексту** з керуванням співвідношенням сторін
- **Редагування зображення за зображенням** (опорне зображення об’єкта) з керуванням співвідношенням сторін
- До **9 вихідних зображень** на запит
- До **1 опорного зображення** на запит редагування
- Підтримувані співвідношення сторін: `1:1`, `16:9`, `4:3`, `3:2`, `2:3`, `3:4`, `9:16`, `21:9`

Щоб використовувати MiniMax для генерації зображень, установіть його як постачальника генерації зображень:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "minimax/image-01" },
    },
  },
}
```

Plugin використовує той самий `MINIMAX_API_KEY` або OAuth-автентифікацію, що й текстові моделі. Додаткова конфігурація не потрібна, якщо MiniMax уже налаштовано.

І `minimax`, і `minimax-portal` реєструють `image_generate` з тією самою
моделлю `image-01`. Налаштування з API key використовують `MINIMAX_API_KEY`; налаштування OAuth можуть натомість використовувати
вбудований шлях автентифікації `minimax-portal`.

Коли під час початкового налаштування або налаштування API key записуються явні записи
`models.providers.minimax`, OpenClaw матеріалізує `MiniMax-M2.7` і
`MiniMax-M2.7-highspeed` з `input: ["text", "image"]`.

Сам вбудований каталог текстових моделей MiniMax залишається метаданими лише для тексту,
доки не з’явиться ця явна конфігурація постачальника. Розуміння зображень надається окремо
через власний медіапостачальник Plugin `MiniMax-VL-01`.

<Note>
Перегляньте [Генерація зображень](/uk/tools/image-generation), щоб дізнатися про спільні параметри інструмента, вибір постачальника та поведінку резервного перемикання.
</Note>

### Генерація музики

Вбудований plugin `minimax` також реєструє генерацію музики через спільний
інструмент `music_generate`.

- Типова музична модель: `minimax/music-2.5+`
- Також підтримує `minimax/music-2.5` і `minimax/music-2.0`
- Керування запитом: `lyrics`, `instrumental`, `durationSeconds`
- Формат виводу: `mp3`
- Запуски з підтримкою сесій відокремлюються через спільний потік завдань/стану, включно з `action: "status"`

Щоб використовувати MiniMax як типовий музичний постачальник:

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

<Note>
Перегляньте [Генерація музики](/uk/tools/music-generation), щоб дізнатися про спільні параметри інструмента, вибір постачальника та поведінку резервного перемикання.
</Note>

### Генерація відео

Вбудований plugin `minimax` також реєструє генерацію відео через спільний
інструмент `video_generate`.

- Типова відеомодель: `minimax/MiniMax-Hailuo-2.3`
- Режими: текст у відео та потоки з одним опорним зображенням
- Підтримує `aspectRatio` і `resolution`

Щоб використовувати MiniMax як типовий відеопостачальник:

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

<Note>
Перегляньте [Генерація відео](/uk/tools/video-generation), щоб дізнатися про спільні параметри інструмента, вибір постачальника та поведінку резервного перемикання.
</Note>

### Розуміння зображень

Plugin MiniMax реєструє розуміння зображень окремо від текстового
каталогу:

| ID постачальника | Типова модель зображень |
| ---------------- | ----------------------- |
| `minimax`        | `MiniMax-VL-01`         |
| `minimax-portal` | `MiniMax-VL-01`         |

Саме тому автоматична маршрутизація медіа може використовувати розуміння зображень MiniMax, навіть
коли вбудований каталог постачальника тексту все ще показує лише текстові посилання на чат M2.7.

### Вебпошук

Plugin MiniMax також реєструє `web_search` через API пошуку MiniMax Coding Plan.

- ID постачальника: `minimax`
- Структуровані результати: заголовки, URL, фрагменти, пов’язані запити
- Бажана змінна середовища: `MINIMAX_CODE_PLAN_KEY`
- Підтримуваний псевдонім змінної середовища: `MINIMAX_CODING_API_KEY`
- Сумісний резервний варіант: `MINIMAX_API_KEY`, якщо він уже вказує на токен coding-plan
- Повторне використання регіону: `plugins.entries.minimax.config.webSearch.region`, потім `MINIMAX_API_HOST`, потім базові URL постачальника MiniMax
- Пошук залишається на ID постачальника `minimax`; налаштування OAuth CN/global усе ще можуть опосередковано спрямовувати регіон через `models.providers.minimax-portal.baseUrl`

Конфігурація розміщується в `plugins.entries.minimax.config.webSearch.*`.

<Note>
Перегляньте [Пошук MiniMax](/uk/tools/minimax-search), щоб дізнатися про повну конфігурацію та використання вебпошуку.
</Note>

## Розширена конфігурація

<AccordionGroup>
  <Accordion title="Параметри конфігурації">
    | Параметр | Опис |
    | --- | --- |
    | `models.providers.minimax.baseUrl` | Надавайте перевагу `https://api.minimax.io/anthropic` (сумісний з Anthropic); `https://api.minimax.io/v1` є необов’язковим для корисних навантажень, сумісних з OpenAI |
    | `models.providers.minimax.api` | Надавайте перевагу `anthropic-messages`; `openai-completions` є необов’язковим для корисних навантажень, сумісних з OpenAI |
    | `models.providers.minimax.apiKey` | API key MiniMax (`MINIMAX_API_KEY`) |
    | `models.providers.minimax.models` | Визначте `id`, `name`, `reasoning`, `contextWindow`, `maxTokens`, `cost` |
    | `agents.defaults.models` | Псевдоніми моделей, які ви хочете додати до allowlist |
    | `models.mode` | Залиште `merge`, якщо хочете додати MiniMax поруч із вбудованими моделями |
  </Accordion>

  <Accordion title="Типові значення thinking">
    Для `api: "anthropic-messages"` OpenClaw додає `thinking: { type: "disabled" }`, якщо thinking ще не встановлено явно в параметрах/конфігурації.

    Це запобігає тому, щоб потокова кінцева точка MiniMax видавала `reasoning_content` у дельта-фрагментах у стилі OpenAI, що призвело б до витоку внутрішніх міркувань у видимий вивід.

  </Accordion>

  <Accordion title="Швидкий режим">
    `/fast on` або `params.fastMode: true` переписує `MiniMax-M2.7` на `MiniMax-M2.7-highspeed` на шляху потокової передачі, сумісному з Anthropic.
  </Accordion>

  <Accordion title="Приклад резервного перемикання">
    **Найкраще для:** залишити вашу найсильнішу найновішу модель покоління як основну та перемикатися на MiniMax M2.7 у разі збою. У прикладі нижче Opus використовується як конкретна основна модель; замініть її на бажану найновішу основну модель покоління.

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

  </Accordion>

  <Accordion title="Докладно про використання Coding Plan">
    - API використання Coding Plan: `https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains` (потребує ключа coding plan).
    - OpenClaw нормалізує використання coding plan MiniMax до того самого відображення `% left`, що й в інших постачальників. Сирі поля `usage_percent` / `usagePercent` у MiniMax означають залишкову квоту, а не використану, тому OpenClaw інвертує їх. Поля на основі лічильників мають пріоритет, якщо вони присутні.
    - Коли API повертає `model_remains`, OpenClaw надає перевагу запису chat model, за потреби виводить мітку вікна з `start_time` / `end_time` і включає вибрану назву моделі в мітку плану, щоб вікна coding plan було легше розрізняти.
    - Знімки використання розглядають `minimax`, `minimax-cn` і `minimax-portal` як ту саму поверхню квоти MiniMax та надають перевагу збереженій MiniMax OAuth перед резервним використанням змінних середовища з ключем Coding Plan.
  </Accordion>
</AccordionGroup>

## Примітки

- Посилання на моделі відповідають шляху автентифікації:
  - Налаштування API key: `minimax/<model>`
  - Налаштування OAuth: `minimax-portal/<model>`
- Типова чат-модель: `MiniMax-M2.7`
- Альтернативна чат-модель: `MiniMax-M2.7-highspeed`
- Початкове налаштування та пряме налаштування API key записують явні визначення моделей з `input: ["text", "image"]` для обох варіантів M2.7
- Вбудований каталог постачальника наразі показує посилання чату як метадані лише для тексту, доки не з’явиться явна конфігурація постачальника MiniMax
- Оновіть значення цін у `models.json`, якщо вам потрібне точне відстеження вартості
- Використовуйте `openclaw models list`, щоб підтвердити поточний ID постачальника, а потім перемкніться за допомогою `openclaw models set minimax/MiniMax-M2.7` або `openclaw models set minimax-portal/MiniMax-M2.7`

<Tip>
Реферальне посилання для MiniMax Coding Plan (знижка 10%): [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
</Tip>

<Note>
Перегляньте [Постачальники моделей](/uk/concepts/model-providers), щоб дізнатися про правила для постачальників.
</Note>

## Усунення несправностей

<AccordionGroup>
  <Accordion title='"Невідома модель: minimax/MiniMax-M2.7"'>
    Зазвичай це означає, що **постачальника MiniMax не налаштовано** (немає відповідного запису постачальника й не знайдено автентифікаційного профілю/ключа середовища MiniMax). Виправлення для цього виявлення є у **2026.1.12**. Щоб виправити:

    - Оновіться до **2026.1.12** (або запустіть із вихідного коду `main`), а потім перезапустіть Gateway.
    - Запустіть `openclaw configure` і виберіть параметр автентифікації **MiniMax**, або
    - Додайте відповідний блок `models.providers.minimax` або `models.providers.minimax-portal` вручну, або
    - Установіть `MINIMAX_API_KEY`, `MINIMAX_OAUTH_TOKEN` або профіль автентифікації MiniMax, щоб можна було додати відповідний постачальник.

    Переконайтеся, що ID моделі **чутливий до регістру**:

    - Шлях API key: `minimax/MiniMax-M2.7` або `minimax/MiniMax-M2.7-highspeed`
    - Шлях OAuth: `minimax-portal/MiniMax-M2.7` або `minimax-portal/MiniMax-M2.7-highspeed`

    Потім перевірте ще раз за допомогою:

    ```bash
    openclaw models list
    ```

  </Accordion>
</AccordionGroup>

<Note>
Додаткова допомога: [Усунення несправностей](/uk/help/troubleshooting) і [FAQ](/uk/help/faq).
</Note>

## Пов’язані матеріали

<CardGroup cols={2}>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір постачальників, посилань на моделі та поведінки резервного перемикання.
  </Card>
  <Card title="Генерація зображень" href="/uk/tools/image-generation" icon="image">
    Спільні параметри інструмента зображень і вибір постачальника.
  </Card>
  <Card title="Генерація музики" href="/uk/tools/music-generation" icon="music">
    Спільні параметри музичного інструмента і вибір постачальника.
  </Card>
  <Card title="Генерація відео" href="/uk/tools/video-generation" icon="video">
    Спільні параметри інструмента відео і вибір постачальника.
  </Card>
  <Card title="Пошук MiniMax" href="/uk/tools/minimax-search" icon="magnifying-glass">
    Конфігурація вебпошуку через MiniMax Coding Plan.
  </Card>
  <Card title="Усунення несправностей" href="/uk/help/troubleshooting" icon="wrench">
    Загальне усунення несправностей і FAQ.
  </Card>
</CardGroup>
