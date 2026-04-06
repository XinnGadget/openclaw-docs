---
read_when:
    - Chcesz używać generowania wideo Runway w OpenClaw
    - Potrzebujesz konfiguracji klucza API / env dla Runway
    - Chcesz ustawić Runway jako domyślnego dostawcę wideo
summary: Konfiguracja generowania wideo Runway w OpenClaw
title: Runway
x-i18n:
    generated_at: "2026-04-06T03:11:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: bc615d1a26f7a4b890d29461e756690c858ecb05024cf3c4d508218022da6e76
    source_path: providers/runway.md
    workflow: 15
---

# Runway

OpenClaw zawiera dołączonego dostawcę `runway` do hostowanego generowania wideo.

- Identyfikator dostawcy: `runway`
- Uwierzytelnianie: `RUNWAYML_API_SECRET` (kanoniczne) lub `RUNWAY_API_KEY`
- API: generowanie wideo oparte na zadaniach Runway (odpytywanie `GET /v1/tasks/{id}`)

## Szybki start

1. Ustaw klucz API:

```bash
openclaw onboard --auth-choice runway-api-key
```

2. Ustaw Runway jako domyślnego dostawcę wideo:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "runway/gen4.5"
```

3. Poproś agenta o wygenerowanie wideo. Runway zostanie użyty automatycznie.

## Obsługiwane tryby

| Tryb           | Model              | Wejście referencyjne        |
| -------------- | ------------------ | --------------------------- |
| Text-to-video  | `gen4.5` (domyślny) | Brak                       |
| Image-to-video | `gen4.5`           | 1 obraz lokalny lub zdalny |
| Video-to-video | `gen4_aleph`       | 1 wideo lokalne lub zdalne |

- Lokalne obrazy i wideo referencyjne są obsługiwane przez URI danych.
- Video-to-video obecnie wymaga konkretnie `runway/gen4_aleph`.
- Uruchomienia tylko tekstowe obecnie udostępniają proporcje `16:9` i `9:16`.

## Konfiguracja

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "runway/gen4.5",
      },
    },
  },
}
```

## Powiązane

- [Generowanie wideo](/tools/video-generation) -- współdzielone parametry narzędzia, wybór dostawcy i zachowanie asynchroniczne
- [Dokumentacja konfiguracji](/pl/gateway/configuration-reference#agent-defaults)
