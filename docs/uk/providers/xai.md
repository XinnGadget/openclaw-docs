---
read_when:
    - Ви хочете використовувати моделі Grok в OpenClaw
    - Ви налаштовуєте автентифікацію xAI або ідентифікатори моделей
summary: Використовуйте моделі xAI Grok в OpenClaw
title: xAI
x-i18n:
    generated_at: "2026-04-12T11:08:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: 820fef290c67d9815e41a96909d567216f67ca0f01df1d325008fd04666ad255
    source_path: providers/xai.md
    workflow: 15
---

# xAI

OpenClaw постачається з вбудованим плагіном провайдера `xai` для моделей Grok.

## Початок роботи

<Steps>
  <Step title="Створіть API-ключ">
    Створіть API-ключ у [консолі xAI](https://console.x.ai/).
  </Step>
  <Step title="Установіть свій API-ключ">
    Установіть `XAI_API_KEY` або виконайте:

    ```bash
    openclaw onboard --auth-choice xai-api-key
    ```

  </Step>
  <Step title="Виберіть модель">
    ```json5
    {
      agents: { defaults: { model: { primary: "xai/grok-4" } } },
    }
    ```
  </Step>
</Steps>

<Note>
OpenClaw використовує xAI Responses API як вбудований транспорт xAI. Той самий
`XAI_API_KEY` також може забезпечувати роботу Grok-backed `web_search`, повноцінного `x_search`
і віддаленого `code_execution`.
Якщо ви зберігаєте ключ xAI у `plugins.entries.xai.config.webSearch.apiKey`,
вбудований провайдер моделей xAI також повторно використовує цей ключ як резервний варіант.
Налаштування `code_execution` розміщені в `plugins.entries.xai.config.codeExecution`.
</Note>

## Каталог вбудованих моделей

OpenClaw містить такі сімейства моделей xAI з коробки:

| Сімейство      | Ідентифікатори моделей                                                  |
| -------------- | ----------------------------------------------------------------------- |
| Grok 3         | `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`              |
| Grok 4         | `grok-4`, `grok-4-0709`                                                 |
| Grok 4 Fast    | `grok-4-fast`, `grok-4-fast-non-reasoning`                              |
| Grok 4.1 Fast  | `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`                          |
| Grok 4.20 Beta | `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning` |
| Grok Code      | `grok-code-fast-1`                                                      |

Плагін також напряму зіставляє новіші ідентифікатори `grok-4*` і `grok-code-fast*`, коли
вони відповідають тій самій формі API.

<Tip>
`grok-4-fast`, `grok-4-1-fast` і варіанти `grok-4.20-beta-*` —
це поточні посилання Grok із підтримкою зображень у вбудованому каталозі.
</Tip>

### Зіставлення швидкого режиму

`/fast on` або `agents.defaults.models["xai/<model>"].params.fastMode: true`
перезаписує нативні запити xAI так:

| Вихідна модель | Ціль швидкого режиму |
| -------------- | -------------------- |
| `grok-3`       | `grok-3-fast`        |
| `grok-3-mini`  | `grok-3-mini-fast`   |
| `grok-4`       | `grok-4-fast`        |
| `grok-4-0709`  | `grok-4-fast`        |

### Застарілі псевдоніми сумісності

Застарілі псевдоніми все ще нормалізуються до канонічних вбудованих ідентифікаторів:

| Застарілий псевдонім       | Канонічний ідентифікатор           |
| -------------------------- | ---------------------------------- |
| `grok-4-fast-reasoning`    | `grok-4-fast`                      |
| `grok-4-1-fast-reasoning`  | `grok-4-1-fast`                    |
| `grok-4.20-reasoning`      | `grok-4.20-beta-latest-reasoning`  |
| `grok-4.20-non-reasoning`  | `grok-4.20-beta-latest-non-reasoning` |

## Можливості

<AccordionGroup>
  <Accordion title="Вебпошук">
    Вбудований провайдер вебпошуку `grok` також використовує `XAI_API_KEY`:

    ```bash
    openclaw config set tools.web.search.provider grok
    ```

  </Accordion>

  <Accordion title="Генерація відео">
    Вбудований плагін `xai` реєструє генерацію відео через спільний
    інструмент `video_generate`.

    - Модель відео за замовчуванням: `xai/grok-imagine-video`
    - Режими: text-to-video, image-to-video, а також віддалені потоки редагування/розширення відео
    - Підтримує `aspectRatio` і `resolution`

    <Warning>
    Локальні відеобуфери не приймаються. Для
    вхідних даних video-reference і edit використовуйте віддалені URL-адреси `http(s)`.
    </Warning>

    Щоб використовувати xAI як провайдера відео за замовчуванням:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "xai/grok-imagine-video",
          },
        },
      },
    }
    ```

    <Note>
    Див. [Генерація відео](/uk/tools/video-generation), щоб дізнатися про спільні параметри інструмента,
    вибір провайдера та поведінку резервного перемикання.
    </Note>

  </Accordion>

  <Accordion title="Конфігурація x_search">
    Вбудований плагін xAI надає `x_search` як інструмент OpenClaw для пошуку
    контенту X (раніше Twitter) через Grok.

    Шлях конфігурації: `plugins.entries.xai.config.xSearch`

    | Ключ               | Тип     | За замовчуванням    | Опис                                 |
    | ------------------ | ------- | ------------------- | ------------------------------------ |
    | `enabled`          | boolean | —                   | Увімкнути або вимкнути x_search      |
    | `model`            | string  | `grok-4-1-fast`     | Модель для запитів x_search          |
    | `inlineCitations`  | boolean | —                   | Додавати вбудовані цитати в результати |
    | `maxTurns`         | number  | —                   | Максимальна кількість ходів розмови  |
    | `timeoutSeconds`   | number  | —                   | Тайм-аут запиту в секундах           |
    | `cacheTtlMinutes`  | number  | —                   | Час життя кешу в хвилинах            |

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              xSearch: {
                enabled: true,
                model: "grok-4-1-fast",
                inlineCitations: true,
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Конфігурація виконання коду">
    Вбудований плагін xAI надає `code_execution` як інструмент OpenClaw для
    віддаленого виконання коду в середовищі sandbox xAI.

    Шлях конфігурації: `plugins.entries.xai.config.codeExecution`

    | Ключ              | Тип     | За замовчуванням          | Опис                                     |
    | ----------------- | ------- | ------------------------- | ---------------------------------------- |
    | `enabled`         | boolean | `true` (якщо ключ доступний) | Увімкнути або вимкнути виконання коду |
    | `model`           | string  | `grok-4-1-fast`           | Модель для запитів виконання коду        |
    | `maxTurns`        | number  | —                         | Максимальна кількість ходів розмови      |
    | `timeoutSeconds`  | number  | —                         | Тайм-аут запиту в секундах               |

    <Note>
    Це віддалене виконання в sandbox xAI, а не локальний [`exec`](/uk/tools/exec).
    </Note>

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              codeExecution: {
                enabled: true,
                model: "grok-4-1-fast",
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Відомі обмеження">
    - Наразі автентифікація підтримується лише через API-ключ. В OpenClaw поки що немає потоку xAI OAuth або device-code.
    - `grok-4.20-multi-agent-experimental-beta-0304` не підтримується в
      звичайному шляху провайдера xAI, оскільки він потребує іншої поверхні
      upstream API, ніж стандартний транспорт xAI в OpenClaw.
  </Accordion>

  <Accordion title="Додаткові примітки">
    - OpenClaw автоматично застосовує виправлення сумісності схем інструментів і викликів інструментів, специфічні для xAI,
      у спільному шляху виконання.
    - Нативні запити xAI за замовчуванням використовують `tool_stream: true`. Установіть
      `agents.defaults.models["xai/<model>"].params.tool_stream` у `false`, щоб
      вимкнути це.
    - Вбудована обгортка xAI видаляє непідтримувані прапорці суворої схеми інструментів і
      ключі payload reasoning перед надсиланням нативних запитів xAI.
    - `web_search`, `x_search` і `code_execution` доступні як інструменти OpenClaw.
      OpenClaw вмикає конкретний вбудований інструмент xAI, який потрібен у кожному запиті інструмента,
      замість того щоб додавати всі нативні інструменти до кожного ходу чату.
    - `x_search` і `code_execution` належать вбудованому плагіну xAI, а не
      жорстко закодовані в базове середовище виконання моделі.
    - `code_execution` — це віддалене виконання в sandbox xAI, а не локальний
      [`exec`](/uk/tools/exec).
  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір провайдерів, посилань на моделі та поведінки резервного перемикання.
  </Card>
  <Card title="Генерація відео" href="/uk/tools/video-generation" icon="video">
    Спільні параметри відеоінструмента та вибір провайдера.
  </Card>
  <Card title="Усі провайдери" href="/uk/providers/index" icon="grid-2">
    Ширший огляд провайдерів.
  </Card>
  <Card title="Усунення проблем" href="/uk/help/troubleshooting" icon="wrench">
    Поширені проблеми та способи їх вирішення.
  </Card>
</CardGroup>
