---
read_when:
    - Ви хочете використовувати моделі Google Gemini з OpenClaw
    - Вам потрібен ключ API або потік автентифікації OAuth
summary: Налаштування Google Gemini (ключ API + OAuth, генерація зображень, розуміння медіа, TTS, вебпошук)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-16T06:26:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: ec2d62855f5e80efda758aad71bcaa95c38b1e41761fa1100d47a06c62881419
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Плагін Google надає доступ до моделей Gemini через Google AI Studio, а також до
генерації зображень, розуміння медіа (зображення/аудіо/відео), перетворення тексту на мовлення та вебпошуку через
Gemini Grounding.

- Провайдер: `google`
- Автентифікація: `GEMINI_API_KEY` або `GOOGLE_API_KEY`
- API: Google Gemini API
- Альтернативний провайдер: `google-gemini-cli` (OAuth)

## Початок роботи

Оберіть бажаний спосіб автентифікації та виконайте кроки налаштування.

<Tabs>
  <Tab title="API key">
    **Найкраще для:** стандартного доступу до Gemini API через Google AI Studio.

    <Steps>
      <Step title="Run onboarding">
        ```bash
        openclaw onboard --auth-choice gemini-api-key
        ```

        Або передайте ключ безпосередньо:

        ```bash
        openclaw onboard --non-interactive \
          --mode local \
          --auth-choice gemini-api-key \
          --gemini-api-key "$GEMINI_API_KEY"
        ```
      </Step>
      <Step title="Set a default model">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "google/gemini-3.1-pro-preview" },
            },
          },
        }
        ```
      </Step>
      <Step title="Verify the model is available">
        ```bash
        openclaw models list --provider google
        ```
      </Step>
    </Steps>

    <Tip>
    Змінні середовища `GEMINI_API_KEY` і `GOOGLE_API_KEY` обидві підтримуються. Використовуйте ту, яку вже налаштовано у вас.
    </Tip>

  </Tab>

  <Tab title="Gemini CLI (OAuth)">
    **Найкраще для:** повторного використання наявного входу Gemini CLI через PKCE OAuth замість окремого ключа API.

    <Warning>
    Провайдер `google-gemini-cli` є неофіційною інтеграцією. Деякі користувачі
    повідомляють про обмеження облікового запису під час використання OAuth у такий спосіб. Використовуйте на власний ризик.
    </Warning>

    <Steps>
      <Step title="Install the Gemini CLI">
        Локальна команда `gemini` має бути доступною в `PATH`.

        ```bash
        # Homebrew
        brew install gemini-cli

        # or npm
        npm install -g @google/gemini-cli
        ```

        OpenClaw підтримує як встановлення через Homebrew, так і глобальні встановлення npm, зокрема
        поширені схеми Windows/npm.
      </Step>
      <Step title="Log in via OAuth">
        ```bash
        openclaw models auth login --provider google-gemini-cli --set-default
        ```
      </Step>
      <Step title="Verify the model is available">
        ```bash
        openclaw models list --provider google-gemini-cli
        ```
      </Step>
    </Steps>

    - Модель за замовчуванням: `google-gemini-cli/gemini-3-flash-preview`
    - Псевдонім: `gemini-cli`

    **Змінні середовища:**

    - `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
    - `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

    (Або варіанти `GEMINI_CLI_*`.)

    <Note>
    Якщо запити Gemini CLI OAuth не вдаються після входу, задайте `GOOGLE_CLOUD_PROJECT` або
    `GOOGLE_CLOUD_PROJECT_ID` на хості Gateway і повторіть спробу.
    </Note>

    <Note>
    Якщо вхід не вдається до початку потоку в браузері, переконайтеся, що локальну команду `gemini`
    встановлено та додано до `PATH`.
    </Note>

    Провайдер `google-gemini-cli`, який підтримує лише OAuth, є окремою
    поверхнею текстового інференсу. Генерація зображень, розуміння медіа та Gemini Grounding залишаються на
    ідентифікаторі провайдера `google`.

  </Tab>
</Tabs>

## Можливості

| Можливість             | Підтримка          |
| ---------------------- | ------------------ |
| Завершення чату        | Так                |
| Генерація зображень    | Так                |
| Генерація музики       | Так                |
| Перетворення тексту на мовлення | Так        |
| Розуміння зображень    | Так                |
| Транскрипція аудіо     | Так                |
| Розуміння відео        | Так                |
| Вебпошук (Grounding)   | Так                |
| Мислення/міркування    | Так (Gemini 3.1+)  |
| Моделі Gemma 4         | Так                |

<Tip>
Моделі Gemma 4 (наприклад, `gemma-4-26b-a4b-it`) підтримують режим мислення. OpenClaw
перезаписує `thinkingBudget` у підтримуваний Google `thinkingLevel` для Gemma 4.
Встановлення мислення в `off` зберігає вимкнений стан мислення замість зіставлення з
`MINIMAL`.
</Tip>

## Генерація зображень

Вбудований провайдер генерації зображень `google` за замовчуванням використовує
`google/gemini-3.1-flash-image-preview`.

- Також підтримує `google/gemini-3-pro-image-preview`
- Генерація: до 4 зображень на запит
- Режим редагування: увімкнено, до 5 вхідних зображень
- Керування геометрією: `size`, `aspectRatio` і `resolution`

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

<Note>
Див. [Генерація зображень](/uk/tools/image-generation), щоб дізнатися про спільні параметри інструмента, вибір провайдера та поведінку перемикання при збоях.
</Note>

## Генерація відео

Вбудований плагін `google` також реєструє генерацію відео через спільний
інструмент `video_generate`.

- Модель відео за замовчуванням: `google/veo-3.1-fast-generate-preview`
- Режими: text-to-video, image-to-video та потоки з одним опорним відео
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

<Note>
Див. [Генерація відео](/uk/tools/video-generation), щоб дізнатися про спільні параметри інструмента, вибір провайдера та поведінку перемикання при збоях.
</Note>

## Генерація музики

Вбудований плагін `google` також реєструє генерацію музики через спільний
інструмент `music_generate`.

- Модель музики за замовчуванням: `google/lyria-3-clip-preview`
- Також підтримує `google/lyria-3-pro-preview`
- Керування запитом: `lyrics` і `instrumental`
- Формат виводу: `mp3` за замовчуванням, а також `wav` у `google/lyria-3-pro-preview`
- Опорні вхідні дані: до 10 зображень
- Запуски з підтримкою сесій відокремлюються через спільний потік задачі/статусу, зокрема `action: "status"`

Щоб використовувати Google як провайдера музики за замовчуванням:

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

<Note>
Див. [Генерація музики](/uk/tools/music-generation), щоб дізнатися про спільні параметри інструмента, вибір провайдера та поведінку перемикання при збоях.
</Note>

## Перетворення тексту на мовлення

Вбудований мовленнєвий провайдер `google` використовує шлях Gemini API TTS з
`gemini-3.1-flash-tts-preview`.

- Голос за замовчуванням: `Kore`
- Автентифікація: `messages.tts.providers.google.apiKey`, `models.providers.google.apiKey`, `GEMINI_API_KEY` або `GOOGLE_API_KEY`
- Вивід: WAV для звичайних TTS-вкладень, PCM для Talk/телефонії
- Нативний вивід голосових нотаток: не підтримується в цьому шляху Gemini API, оскільки API повертає PCM, а не Opus

Щоб використовувати Google як TTS-провайдера за замовчуванням:

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "google",
      providers: {
        google: {
          model: "gemini-3.1-flash-tts-preview",
          voiceName: "Kore",
        },
      },
    },
  },
}
```

Gemini API TTS приймає виразні квадратні аудіотеги в тексті, наприклад
`[whispers]` або `[laughs]`. Щоб приховати теги з видимої відповіді в чаті, але
надсилати їх до TTS, помістіть їх у блок `[[tts:text]]...[[/tts:text]]`:

```text
Ось чистий текст відповіді.

[[tts:text]][whispers] Ось озвучена версія.[[/tts:text]]
```

<Note>
Ключ API Google Cloud Console, обмежений Gemini API, є дійсним для цього
провайдера. Це не окремий шлях Cloud Text-to-Speech API.
</Note>

## Розширене налаштування

<AccordionGroup>
  <Accordion title="Direct Gemini cache reuse">
    Для прямих запусків Gemini API (`api: "google-generative-ai"`) OpenClaw
    передає налаштований дескриптор `cachedContent` у запити Gemini.

    - Налаштовуйте параметри для окремої моделі або глобально за допомогою
      `cachedContent` або застарілого `cached_content`
    - Якщо присутні обидва, `cachedContent` має пріоритет
    - Приклад значення: `cachedContents/prebuilt-context`
    - Використання влучення кешу Gemini нормалізується в OpenClaw `cacheRead` з
      вихідного `cachedContentTokenCount`

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

  </Accordion>

  <Accordion title="Gemini CLI JSON usage notes">
    Під час використання OAuth-провайдера `google-gemini-cli` OpenClaw нормалізує
    JSON-вивід CLI таким чином:

    - Текст відповіді береться з поля CLI JSON `response`.
    - Використання повертається до `stats`, якщо CLI залишає `usage` порожнім.
    - `stats.cached` нормалізується в OpenClaw `cacheRead`.
    - Якщо `stats.input` відсутній, OpenClaw виводить кількість вхідних токенів із
      `stats.input_tokens - stats.cached`.

  </Accordion>

  <Accordion title="Environment and daemon setup">
    Якщо Gateway працює як демон (launchd/systemd), переконайтеся, що `GEMINI_API_KEY`
    доступний цьому процесу (наприклад, у `~/.openclaw/.env` або через
    `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Model selection" href="/uk/concepts/model-providers" icon="layers">
    Вибір провайдерів, посилань на моделі та поведінки перемикання при збоях.
  </Card>
  <Card title="Image generation" href="/uk/tools/image-generation" icon="image">
    Спільні параметри інструмента зображень і вибір провайдера.
  </Card>
  <Card title="Video generation" href="/uk/tools/video-generation" icon="video">
    Спільні параметри інструмента відео і вибір провайдера.
  </Card>
  <Card title="Music generation" href="/uk/tools/music-generation" icon="music">
    Спільні параметри інструмента музики і вибір провайдера.
  </Card>
</CardGroup>
