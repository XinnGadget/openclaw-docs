---
read_when:
    - Chcesz używać generowania obrazów fal w OpenClaw
    - Potrzebujesz przepływu uwierzytelniania `FAL_KEY`
    - Chcesz używać domyślnych ustawień fal dla `image_generate` lub `video_generate`
summary: Konfiguracja generowania obrazów i wideo fal w OpenClaw
title: fal
x-i18n:
    generated_at: "2026-04-06T03:11:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1922907d2c8360c5877a56495323d54bd846d47c27a801155e3d11e3f5706fbd
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw dostarcza wbudowanego dostawcę `fal` do hostowanego generowania obrazów i wideo.

- Dostawca: `fal`
- Uwierzytelnianie: `FAL_KEY` (kanoniczne; `FAL_API_KEY` działa również jako awaryjne)
- API: endpointy modeli fal

## Szybki start

1. Ustaw klucz API:

```bash
openclaw onboard --auth-choice fal-api-key
```

2. Ustaw domyślny model obrazu:

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

## Generowanie obrazów

Wbudowany dostawca generowania obrazów `fal` domyślnie używa
`fal/fal-ai/flux/dev`.

- Generowanie: maksymalnie 4 obrazy na żądanie
- Tryb edycji: włączony, 1 obraz referencyjny
- Obsługuje `size`, `aspectRatio` i `resolution`
- Aktualne ograniczenie edycji: endpoint edycji obrazów fal **nie** obsługuje
  nadpisywania `aspectRatio`

Aby używać fal jako domyślnego dostawcy obrazów:

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

## Generowanie wideo

Wbudowany dostawca generowania wideo `fal` domyślnie używa
`fal/fal-ai/minimax/video-01-live`.

- Tryby: text-to-video oraz przepływy z pojedynczym obrazem referencyjnym
- Runtime: przepływ submit/status/result oparty na kolejce dla długotrwałych zadań

Aby używać fal jako domyślnego dostawcy wideo:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "fal/fal-ai/minimax/video-01-live",
      },
    },
  },
}
```

## Powiązane

- [Generowanie obrazów](/pl/tools/image-generation)
- [Generowanie wideo](/tools/video-generation)
- [Dokumentacja konfiguracji](/pl/gateway/configuration-reference#agent-defaults)
