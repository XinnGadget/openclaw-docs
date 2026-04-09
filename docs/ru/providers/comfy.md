---
title: "ComfyUI"
summary: "Настройка генерации изображений, видео и музыки с помощью рабочих процессов ComfyUI в OpenClaw"
read_when:
  - Вы хотите использовать локальные рабочие процессы ComfyUI с OpenClaw
  - Вы хотите использовать Comfy Cloud с рабочими процессами для изображений, видео или музыки
  - Вам нужны ключи конфигурации плагина comfy, входящие в комплект поставки
---

# ComfyUI

OpenClaw включает в себя встроенный плагин `comfy` для запуска ComfyUI на основе рабочих процессов.

- Поставщик: `comfy`
- Модели: `comfy/workflow`
- Общие интерфейсы: `image_generate`, `video_generate`, `music_generate`
- Аутентификация: не требуется для локального ComfyUI; `COMFY_API_KEY` или `COMFY_CLOUD_API_KEY` для Comfy Cloud
- API: ComfyUI `/prompt` / `/history` / `/view` и Comfy Cloud `/api/*`

## Что поддерживается

- Генерация изображений на основе JSON-описания рабочего процесса
- Редактирование изображений с использованием одного загруженного эталонного изображения
- Генерация видео на основе JSON-описания рабочего процесса
- Генерация видео с использованием одного загруженного эталонного изображения
- Генерация музыки или аудио с помощью общего инструмента `music_generate`
- Загрузка результатов из настроенного узла или из всех соответствующих выходных узлов

Встроенный плагин работает на основе рабочих процессов, поэтому OpenClaw не пытается сопоставить общие параметры `size`, `aspectRatio`, `resolution`, `durationSeconds` или элементы управления в стиле TTS с вашим графом.

## Структура конфигурации

Comfy поддерживает общие настройки подключения на верхнем уровне, а также разделы рабочих процессов для каждой возможности:

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

Общие ключи:

- `mode`: `local` или `cloud`
- `baseUrl`: по умолчанию `http://127.0.0.1:8188` для локального режима или `https://cloud.comfy.org` для облачного
- `apiKey`: необязательный встроенный ключ, альтернатива переменным окружения
- `allowPrivateNetwork`: разрешает использование `baseUrl` для частной сети/LAN в облачном режиме

Ключи для каждой возможности (в разделах `image`, `video` или `music`):

- `workflow` или `workflowPath`: обязательно
- `promptNodeId`: обязательно
- `promptInputName`: по умолчанию `text`
- `outputNodeId`: необязательно
- `pollIntervalMs`: необязательно
- `timeoutMs`: необязательно

Разделы для изображений и видео также поддерживают:

- `inputImageNodeId`: обязательно при передаче эталонного изображения
- `inputImageInputName`: по умолчанию `image`

## Обратная совместимость

Существующая конфигурация изображений на верхнем уровне по-прежнему работает:

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

OpenClaw обрабатывает такую устаревшую конфигурацию как настройки рабочего процесса для изображений.

## Рабочие процессы для изображений

Задайте модель изображений по умолчанию:

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

Пример редактирования с использованием эталонного изображения:

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

## Рабочие процессы для видео

Задайте модель видео по умолчанию:

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

Рабочие процессы Comfy для видео в настоящее время поддерживают преобразование текста в видео и изображения в видео через настроенный граф. OpenClaw не передаёт входные видео в рабочие процессы Comfy.

## Рабочие процессы для музыки

Встроенный плагин регистрирует поставщика генерации музыки для аудио- или музыкальных выходных данных, определённых в рабочем процессе, доступных через общий инструмент `music_generate`:

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

Используйте раздел конфигурации `music`, чтобы указать на ваш JSON-файл рабочего процесса для аудио и выходной узел.

## Comfy Cloud

Используйте `mode: "cloud"` вместе с одним из следующих параметров:

- `COMFY_API_KEY`
- `COMFY_CLOUD_API_KEY`
- `models.providers.comfy.apiKey`

В облачном режиме по-прежнему используются те же разделы рабочих процессов для `image`, `video` и `music`.

## Живые тесты

Для встроенного плагина доступна опция участия в живых тестах:

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

Живой тест пропускает отдельные случаи для изображений, видео или музыки, если соответствующий раздел рабочего процесса Comfy не настроен.

## Связанные материалы

- [Генерация изображений](/tools/image-generation)
- [Генерация видео](/tools/video-generation)
- [Генерация музыки](/tools/music-generation)
- [Каталог поставщиков](/providers/index)
- [Справочник по конфигурации](/gateway/configuration-reference#agent-defaults)