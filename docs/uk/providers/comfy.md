---
read_when:
    - Ви хочете використовувати локальні робочі процеси ComfyUI з OpenClaw
    - Ви хочете використовувати Comfy Cloud із робочими процесами для зображень, відео або музики
    - Вам потрібні ключі конфігурації bundled Plugin comfy
summary: Налаштування робочого процесу ComfyUI для генерації зображень, відео та музики в OpenClaw
title: ComfyUI
x-i18n:
    generated_at: "2026-04-12T10:12:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 85db395b171f37f80b34b22f3e7707bffc1fd9138e7d10687eef13eaaa55cf24
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

OpenClaw постачається з вбудованим Plugin `comfy` для запусків ComfyUI на основі робочих процесів. Plugin повністю керується робочими процесами, тому OpenClaw не намагається зіставляти загальні параметри `size`, `aspectRatio`, `resolution`, `durationSeconds` або елементи керування в стилі TTS з вашим графом.

| Властивість      | Деталі                                                                           |
| ---------------- | -------------------------------------------------------------------------------- |
| Провайдер        | `comfy`                                                                          |
| Моделі           | `comfy/workflow`                                                                 |
| Спільні поверхні | `image_generate`, `video_generate`, `music_generate`                             |
| Автентифікація   | Немає для локального ComfyUI; `COMFY_API_KEY` або `COMFY_CLOUD_API_KEY` для Comfy Cloud |
| API              | ComfyUI `/prompt` / `/history` / `/view` і Comfy Cloud `/api/*`                  |

## Що підтримується

- Генерація зображень із JSON робочого процесу
- Редагування зображень з 1 завантаженим еталонним зображенням
- Генерація відео з JSON робочого процесу
- Генерація відео з 1 завантаженим еталонним зображенням
- Генерація музики або аудіо через спільний інструмент `music_generate`
- Завантаження результатів із налаштованого вузла або з усіх відповідних вузлів виводу

## Початок роботи

Оберіть між запуском ComfyUI на власному комп’ютері або використанням Comfy Cloud.

<Tabs>
  <Tab title="Local">
    **Найкраще підходить для:** запуску власного екземпляра ComfyUI на вашому комп’ютері або в LAN.

    <Steps>
      <Step title="Запустіть ComfyUI локально">
        Переконайтеся, що ваш локальний екземпляр ComfyUI запущений (типово `http://127.0.0.1:8188`).
      </Step>
      <Step title="Підготуйте JSON вашого робочого процесу">
        Експортуйте або створіть JSON-файл робочого процесу ComfyUI. Зверніть увагу на ID вузлів для вузла введення запиту та вузла виводу, з якого OpenClaw має читати дані.
      </Step>
      <Step title="Налаштуйте провайдера">
        Установіть `mode: "local"` і вкажіть файл вашого робочого процесу. Ось мінімальний приклад для зображень:

        ```json5
        {
          models: {
            providers: {
              comfy: {
                mode: "local",
                baseUrl: "http://127.0.0.1:8188",
                image: {
                  workflowPath: "./workflows/flux-api.json",
                  promptNodeId: "6",
                  outputNodeId: "9",
                },
              },
            },
          },
        }
        ```
      </Step>
      <Step title="Установіть модель за замовчуванням">
        Спрямуйте OpenClaw на модель `comfy/workflow` для можливості, яку ви налаштували:

        ```json5
        {
          agents: {
            defaults: {
              imageGenerationModel: {
                primary: "comfy/workflow",
              },
            },
          },
        }
        ```
      </Step>
      <Step title="Перевірте">
        ```bash
        openclaw models list --provider comfy
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Comfy Cloud">
    **Найкраще підходить для:** запуску робочих процесів у Comfy Cloud без керування локальними ресурсами GPU.

    <Steps>
      <Step title="Отримайте API-ключ">
        Зареєструйтеся на [comfy.org](https://comfy.org) і згенеруйте API-ключ на інформаційній панелі свого облікового запису.
      </Step>
      <Step title="Установіть API-ключ">
        Надайте ключ одним із цих способів:

        ```bash
        # Змінна середовища (рекомендовано)
        export COMFY_API_KEY="your-key"

        # Альтернативна змінна середовища
        export COMFY_CLOUD_API_KEY="your-key"

        # Або безпосередньо в конфігурації
        openclaw config set models.providers.comfy.apiKey "your-key"
        ```
      </Step>
      <Step title="Підготуйте JSON вашого робочого процесу">
        Експортуйте або створіть JSON-файл робочого процесу ComfyUI. Зверніть увагу на ID вузлів для вузла введення запиту та вузла виводу.
      </Step>
      <Step title="Налаштуйте провайдера">
        Установіть `mode: "cloud"` і вкажіть файл вашого робочого процесу:

        ```json5
        {
          models: {
            providers: {
              comfy: {
                mode: "cloud",
                image: {
                  workflowPath: "./workflows/flux-api.json",
                  promptNodeId: "6",
                  outputNodeId: "9",
                },
              },
            },
          },
        }
        ```

        <Tip>
        У режимі cloud для `baseUrl` типово використовується `https://cloud.comfy.org`. Вам потрібно вказати `baseUrl`, лише якщо ви використовуєте власну cloud-адресу.
        </Tip>
      </Step>
      <Step title="Установіть модель за замовчуванням">
        ```json5
        {
          agents: {
            defaults: {
              imageGenerationModel: {
                primary: "comfy/workflow",
              },
            },
          },
        }
        ```
      </Step>
      <Step title="Перевірте">
        ```bash
        openclaw models list --provider comfy
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Конфігурація

Comfy підтримує спільні налаштування з’єднання верхнього рівня, а також розділи робочих процесів для окремих можливостей (`image`, `video`, `music`):

```json5
{
  models: {
    providers: {
      comfy: {
        mode: "local",
        baseUrl: "http://127.0.0.1:8188",
        image: {
          workflowPath: "./workflows/flux-api.json",
          promptNodeId: "6",
          outputNodeId: "9",
        },
        video: {
          workflowPath: "./workflows/video-api.json",
          promptNodeId: "12",
          outputNodeId: "21",
        },
        music: {
          workflowPath: "./workflows/music-api.json",
          promptNodeId: "3",
          outputNodeId: "18",
        },
      },
    },
  },
}
```

### Спільні ключі

| Ключ                  | Тип                    | Опис                                                                                 |
| --------------------- | ---------------------- | ------------------------------------------------------------------------------------ |
| `mode`                | `"local"` or `"cloud"` | Режим з’єднання.                                                                     |
| `baseUrl`             | string                 | Типово `http://127.0.0.1:8188` для local або `https://cloud.comfy.org` для cloud.   |
| `apiKey`              | string                 | Необов’язковий ключ у конфігурації, альтернатива змінним середовища `COMFY_API_KEY` / `COMFY_CLOUD_API_KEY`. |
| `allowPrivateNetwork` | boolean                | Дозволяє приватний/LAN `baseUrl` у режимі cloud.                                     |

### Ключі для окремих можливостей

Ці ключі застосовуються всередині розділів `image`, `video` або `music`:

| Ключ                         | Обов’язково | Типово   | Опис                                                                        |
| ---------------------------- | ----------- | -------- | --------------------------------------------------------------------------- |
| `workflow` or `workflowPath` | Так         | --       | Шлях до JSON-файлу робочого процесу ComfyUI.                                |
| `promptNodeId`               | Так         | --       | ID вузла, який отримує текстовий запит.                                     |
| `promptInputName`            | Ні          | `"text"` | Назва входу у вузлі запиту.                                                 |
| `outputNodeId`               | Ні          | --       | ID вузла, з якого читати результат. Якщо не вказано, використовуються всі відповідні вузли виводу. |
| `pollIntervalMs`             | Ні          | --       | Інтервал опитування в мілісекундах для завершення завдання.                 |
| `timeoutMs`                  | Ні          | --       | Тайм-аут у мілісекундах для виконання робочого процесу.                     |

Розділи `image` і `video` також підтримують:

| Ключ                  | Обов’язково                           | Типово    | Опис                                                |
| --------------------- | ------------------------------------- | --------- | --------------------------------------------------- |
| `inputImageNodeId`    | Так (коли передається еталонне зображення) | --        | ID вузла, який отримує завантажене еталонне зображення. |
| `inputImageInputName` | Ні                                    | `"image"` | Назва входу у вузлі зображення.                     |

## Деталі робочих процесів

<AccordionGroup>
  <Accordion title="Image workflows">
    Установіть модель зображень за замовчуванням на `comfy/workflow`:

    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "comfy/workflow",
          },
        },
      },
    }
    ```

    **Приклад редагування з використанням еталонного зображення:**

    Щоб увімкнути редагування зображень із завантаженим еталонним зображенням, додайте `inputImageNodeId` до конфігурації `image`:

    ```json5
    {
      models: {
        providers: {
          comfy: {
            image: {
              workflowPath: "./workflows/edit-api.json",
              promptNodeId: "6",
              inputImageNodeId: "7",
              inputImageInputName: "image",
              outputNodeId: "9",
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Video workflows">
    Установіть модель відео за замовчуванням на `comfy/workflow`:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "comfy/workflow",
          },
        },
      },
    }
    ```

    Робочі процеси Comfy для відео підтримують текст-у-відео та зображення-у-відео через налаштований граф.

    <Note>
    OpenClaw не передає вхідні відео в робочі процеси Comfy. Як вхідні дані підтримуються лише текстові запити та окремі еталонні зображення.
    </Note>

  </Accordion>

  <Accordion title="Music workflows">
    Вбудований Plugin реєструє провайдера генерації музики для визначених робочим процесом аудіо- або музичних результатів, доступного через спільний інструмент `music_generate`:

    ```text
    /tool music_generate prompt="Warm ambient synth loop with soft tape texture"
    ```

    Використовуйте розділ конфігурації `music`, щоб вказати JSON вашого аудіоробочого процесу та вузол виводу.

  </Accordion>

  <Accordion title="Backward compatibility">
    Наявна конфігурація зображень верхнього рівня (без вкладеного розділу `image`) як і раніше працює:

    ```json5
    {
      models: {
        providers: {
          comfy: {
            workflowPath: "./workflows/flux-api.json",
            promptNodeId: "6",
            outputNodeId: "9",
          },
        },
      },
    }
    ```

    OpenClaw розглядає цю застарілу форму як конфігурацію робочого процесу для зображень. Вам не потрібно негайно виконувати міграцію, але для нових налаштувань рекомендуються вкладені розділи `image` / `video` / `music`.

    <Tip>
    Якщо ви використовуєте лише генерацію зображень, застаріла пласка конфігурація та новий вкладений розділ `image` функціонально еквівалентні.
    </Tip>

  </Accordion>

  <Accordion title="Live tests">
    Для вбудованого Plugin існує live-покриття за явним увімкненням:

    ```bash
    OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
    ```

    Live-тест пропускає окремі сценарії для зображень, відео або музики, якщо не налаштовано відповідний розділ робочого процесу Comfy.

  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Image Generation" href="/uk/tools/image-generation" icon="image">
    Налаштування та використання інструмента генерації зображень.
  </Card>
  <Card title="Video Generation" href="/uk/tools/video-generation" icon="video">
    Налаштування та використання інструмента генерації відео.
  </Card>
  <Card title="Music Generation" href="/uk/tools/music-generation" icon="music">
    Налаштування генерації музики та аудіо.
  </Card>
  <Card title="Provider Directory" href="/uk/providers/index" icon="layers">
    Огляд усіх провайдерів і посилань на моделі.
  </Card>
  <Card title="Configuration Reference" href="/uk/gateway/configuration-reference#agent-defaults" icon="gear">
    Повний довідник із конфігурації, включно з типовими значеннями агентів.
  </Card>
</CardGroup>
