---
read_when:
    - Chcesz używać generowania multimediów Vydra w OpenClaw
    - Potrzebujesz wskazówek dotyczących konfiguracji klucza API Vydra
summary: Używaj generowania obrazów, wideo i mowy Vydra w OpenClaw
title: Vydra
x-i18n:
    generated_at: "2026-04-06T03:12:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0fe999e8a5414b8a31a6d7d127bc6bcfc3b4492b8f438ab17dfa9680c5b079b7
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

Dołączony plugin Vydra dodaje:

- generowanie obrazów przez `vydra/grok-imagine`
- generowanie wideo przez `vydra/veo3` i `vydra/kling`
- syntezę mowy przez trasę TTS Vydra opartą na ElevenLabs

OpenClaw używa tego samego `VYDRA_API_KEY` dla wszystkich trzech capabilities.

## Ważny base URL

Użyj `https://www.vydra.ai/api/v1`.

Główny host Vydra (`https://vydra.ai/api/v1`) obecnie przekierowuje do `www`. Niektóre klienty HTTP gubią `Authorization` przy takim przekierowaniu między hostami, co zmienia prawidłowy klucz API w mylący błąd uwierzytelniania. Dołączony plugin używa bezpośrednio base URL z `www`, aby tego uniknąć.

## Konfiguracja

Interaktywny onboarding:

```bash
openclaw onboard --auth-choice vydra-api-key
```

Lub ustaw bezpośrednio zmienną env:

```bash
export VYDRA_API_KEY="vydra_live_..."
```

## Generowanie obrazów

Domyślny model obrazu:

- `vydra/grok-imagine`

Ustaw go jako domyślnego dostawcę obrazów:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "vydra/grok-imagine",
      },
    },
  },
}
```

Obecna obsługa w dołączonym pluginie obejmuje tylko text-to-image. Hostowane trasy edycji Vydra oczekują zdalnych URL-i obrazów, a OpenClaw nie dodaje jeszcze pomostu przesyłania specyficznego dla Vydra w dołączonym pluginie.

Zobacz [Generowanie obrazów](/pl/tools/image-generation), aby poznać współdzielone zachowanie narzędzia.

## Generowanie wideo

Zarejestrowane modele wideo:

- `vydra/veo3` dla text-to-video
- `vydra/kling` dla image-to-video

Ustaw Vydra jako domyślnego dostawcę wideo:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "vydra/veo3",
      },
    },
  },
}
```

Uwagi:

- `vydra/veo3` jest dołączony wyłącznie jako text-to-video.
- `vydra/kling` obecnie wymaga referencji do zdalnego URL obrazu. Przesyłanie plików lokalnych jest odrzucane od razu.
- Dołączony plugin pozostaje zachowawczy i nie przekazuje nieudokumentowanych ustawień stylu, takich jak proporcje, rozdzielczość, znak wodny czy wygenerowane audio.

Zobacz [Generowanie wideo](/tools/video-generation), aby poznać współdzielone zachowanie narzędzia.

## Synteza mowy

Ustaw Vydra jako dostawcę mowy:

```json5
{
  messages: {
    tts: {
      provider: "vydra",
      providers: {
        vydra: {
          apiKey: "${VYDRA_API_KEY}",
          voiceId: "21m00Tcm4TlvDq8ikWAM",
        },
      },
    },
  },
}
```

Domyślne wartości:

- model: `elevenlabs/tts`
- voice id: `21m00Tcm4TlvDq8ikWAM`

Dołączony plugin obecnie udostępnia jeden sprawdzony domyślny głos i zwraca pliki audio MP3.

## Powiązane

- [Katalog dostawców](/pl/providers/index)
- [Generowanie obrazów](/pl/tools/image-generation)
- [Generowanie wideo](/tools/video-generation)
