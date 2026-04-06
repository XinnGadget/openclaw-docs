---
read_when:
    - Ви хочете використовувати локальні робочі процеси ComfyUI з OpenClaw
    - Ви хочете використовувати Comfy Cloud із робочими процесами зображень, відео або музики
    - Вам потрібні ключі конфігурації вбудованого плагіна comfy
summary: Налаштування генерації зображень, відео та музики через робочі процеси ComfyUI в OpenClaw
title: ComfyUI
x-i18n:
    generated_at: "2026-04-06T01:05:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: e645f32efdffdf4cd498684f1924bb953a014d3656b48f4b503d64e38c61ba9c
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

OpenClaw постачається з вбудованим плагіном `comfy` для запусків ComfyUI на основі робочих процесів.

- Провайдер: `comfy`
- Моделі: `comfy/workflow`
- Спільні поверхні: `image_generate`, `video_generate`, `music_generate`
- Автентифікація: не потрібна для локального ComfyUI; `COMFY_API_KEY` або `COMFY_CLOUD_API_KEY` для Comfy Cloud
- API: ComfyUI `/prompt` / `/history` / `/view` і Comfy Cloud `/api/*`

## Що підтримується

- Генерація зображень із JSON робочого процесу
- Редагування зображень з 1 завантаженим еталонним зображенням
- Генерація відео з JSON робочого процесу
- Генерація відео з 1 завантаженим еталонним зображенням
- Генерація музики або аудіо через спільний інструмент `music_generate`
- Завантаження результатів із налаштованого вузла або з усіх відповідних вузлів виводу

Вбудований плагін керується робочими процесами, тому OpenClaw не намагається зіставляти загальні
`size`, `aspectRatio`, `resolution`, `durationSeconds` або елементи керування у стилі TTS
з вашим графом.

## Структура конфігурації

Comfy підтримує спільні налаштування з'єднання верхнього рівня, а також розділи
робочих процесів для кожної можливості:

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

Спільні ключі:

- `mode`: `local` або `cloud`
- `baseUrl`: типово `http://127.0.0.1:8188` для локального режиму або `https://cloud.comfy.org` для хмарного
- `apiKey`: необов'язкова вбудована альтернатива ключу через змінні середовища
- `allowPrivateNetwork`: дозволяє приватний/LAN `baseUrl` у хмарному режимі

Ключі для кожної можливості в `image`, `video` або `music`:

- `workflow` або `workflowPath`: обов'язково
- `promptNodeId`: обов'язково
- `promptInputName`: типово `text`
- `outputNodeId`: необов'язково
- `pollIntervalMs`: необов'язково
- `timeoutMs`: необов'язково

Розділи зображень і відео також підтримують:

- `inputImageNodeId`: обов'язково, коли ви передаєте еталонне зображення
- `inputImageInputName`: типово `image`

## Зворотна сумісність

Наявна конфігурація зображень верхнього рівня все ще працює:

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

OpenClaw розглядає цю застарілу форму як конфігурацію робочого процесу зображень.

## Робочі процеси зображень

Установіть типову модель зображень:

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

Приклад редагування з еталонним зображенням:

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

## Робочі процеси відео

Установіть типову модель відео:

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

Робочі процеси відео Comfy наразі підтримують перетворення тексту на відео та
зображення на відео через налаштований граф. OpenClaw не передає вхідні відео
до робочих процесів Comfy.

## Робочі процеси музики

Вбудований плагін реєструє провайдера генерації музики для визначених робочим процесом
аудіо- або музичних результатів, доступних через спільний інструмент `music_generate`:

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

Використовуйте розділ конфігурації `music`, щоб указати JSON вашого аудіоробочого процесу та
вузол виводу.

## Comfy Cloud

Використовуйте `mode: "cloud"` плюс один із варіантів:

- `COMFY_API_KEY`
- `COMFY_CLOUD_API_KEY`
- `models.providers.comfy.apiKey`

Хмарний режим, як і раніше, використовує ті самі розділи робочих процесів `image`, `video` і `music`.

## Live тести

Для вбудованого плагіна є покриття Live тестами за явним увімкненням:

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

Live тест пропускає окремі сценарії для зображень, відео або музики, якщо відповідний
розділ робочого процесу Comfy не налаштовано.

## Пов'язане

- [Генерація зображень](/uk/tools/image-generation)
- [Генерація відео](/uk/tools/video-generation)
- [Генерація музики](/uk/tools/music-generation)
- [Каталог провайдерів](/uk/providers/index)
- [Довідник із конфігурації](/uk/gateway/configuration-reference#agent-defaults)
