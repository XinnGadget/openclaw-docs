---
read_when:
    - Ви хочете використовувати генерацію зображень fal в OpenClaw
    - Вам потрібен потік автентифікації `FAL_KEY`
    - Ви хочете типові налаштування fal для `image_generate` або `video_generate`
summary: Налаштування генерації зображень і відео fal в OpenClaw
title: fal
x-i18n:
    generated_at: "2026-04-11T01:59:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9bfe4f69124e922a79a516a1bd78f0c00f7a45f3c6f68b6d39e0d196fa01beb3
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw постачається зі вбудованим провайдером `fal` для хостингової генерації зображень і відео.

- Провайдер: `fal`
- Автентифікація: `FAL_KEY` (канонічний варіант; `FAL_API_KEY` також працює як резервний)
- API: кінцеві точки моделей fal

## Швидкий початок

1. Встановіть API-ключ:

```bash
openclaw onboard --auth-choice fal-api-key
```

2. Встановіть типову модель зображень:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## Генерація зображень

Вбудований провайдер генерації зображень `fal` типово використовує
`fal/fal-ai/flux/dev`.

- Генерація: до 4 зображень на запит
- Режим редагування: увімкнено, 1 еталонне зображення
- Підтримує `size`, `aspectRatio` і `resolution`
- Поточне обмеження редагування: кінцева точка редагування зображень fal **не** підтримує
  перевизначення `aspectRatio`

Щоб використовувати fal як типовий провайдер зображень:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## Генерація відео

Вбудований провайдер генерації відео `fal` типово використовує
`fal/fal-ai/minimax/video-01-live`.

- Режими: text-to-video і потоки з одним еталонним зображенням
- Середовище виконання: потік submit/status/result на основі черги для довготривалих завдань
- Посилання на модель відеоагента HeyGen:
  - `fal/fal-ai/heygen/v2/video-agent`
- Посилання на моделі Seedance 2.0:
  - `fal/bytedance/seedance-2.0/fast/text-to-video`
  - `fal/bytedance/seedance-2.0/fast/image-to-video`
  - `fal/bytedance/seedance-2.0/text-to-video`
  - `fal/bytedance/seedance-2.0/image-to-video`

Щоб використовувати Seedance 2.0 як типову модель відео:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "fal/bytedance/seedance-2.0/fast/text-to-video",
      },
    },
  },
}
```

Щоб використовувати HeyGen video-agent як типову модель відео:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "fal/fal-ai/heygen/v2/video-agent",
      },
    },
  },
}
```

## Пов’язане

- [Генерація зображень](/uk/tools/image-generation)
- [Генерація відео](/uk/tools/video-generation)
- [Довідник із конфігурації](/uk/gateway/configuration-reference#agent-defaults)
