---
read_when:
    - Chcesz używać modeli Google Gemini z OpenClaw
    - Potrzebujesz przepływu uwierzytelniania kluczem API
summary: Konfiguracja Google Gemini (klucz API, generowanie obrazów, rozumienie multimediów, wyszukiwanie w sieci)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-06T03:11:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 358d33a68275b01ebd916a3621dd651619cb9a1d062e2fb6196a7f3c501c015a
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Plugin Google zapewnia dostęp do modeli Gemini przez Google AI Studio, a także
generowanie obrazów, rozumienie multimediów (obraz/audio/wideo) oraz wyszukiwanie w sieci przez
Gemini Grounding.

- Dostawca: `google`
- Uwierzytelnianie: `GEMINI_API_KEY` lub `GOOGLE_API_KEY`
- API: Google Gemini API

## Szybki start

1. Ustaw klucz API:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. Ustaw model domyślny:

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## Przykład nieinteraktywny

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## Capabilities

| Capability             | Obsługiwane       |
| ---------------------- | ----------------- |
| Uzupełnianie czatu     | Tak               |
| Generowanie obrazów    | Tak               |
| Generowanie muzyki     | Tak               |
| Rozumienie obrazów     | Tak               |
| Transkrypcja audio     | Tak               |
| Rozumienie wideo       | Tak               |
| Wyszukiwanie w sieci (Grounding) | Tak      |
| Thinking/reasoning     | Tak (Gemini 3.1+) |

## Bezpośrednie ponowne użycie cache Gemini

Dla bezpośrednich uruchomień Gemini API (`api: "google-generative-ai"`) OpenClaw
przekazuje teraz skonfigurowany uchwyt `cachedContent` dalej do żądań Gemini.

- Skonfiguruj parametry dla modelu lub globalnie za pomocą
  `cachedContent` albo starszego `cached_content`
- Jeśli obecne są oba, pierwszeństwo ma `cachedContent`
- Przykładowa wartość: `cachedContents/prebuilt-context`
- Użycie trafienia cache Gemini jest normalizowane do OpenClaw `cacheRead` z
  upstream `cachedContentTokenCount`

Przykład:

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

## Generowanie obrazów

Dołączony dostawca generowania obrazów `google` domyślnie używa
`google/gemini-3.1-flash-image-preview`.

- Obsługuje też `google/gemini-3-pro-image-preview`
- Generowanie: do 4 obrazów na żądanie
- Tryb edycji: włączony, do 5 obrazów wejściowych
- Kontrola geometrii: `size`, `aspectRatio` i `resolution`

Generowanie obrazów, rozumienie multimediów i Gemini Grounding pozostają przy
identyfikatorze dostawcy `google`.

Aby używać Google jako domyślnego dostawcy obrazów:

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

Zobacz [Generowanie obrazów](/pl/tools/image-generation), aby poznać współdzielone
parametry narzędzia, wybór dostawcy i zachowanie failover.

## Generowanie wideo

Dołączony plugin `google` rejestruje też generowanie wideo przez współdzielone
narzędzie `video_generate`.

- Domyślny model wideo: `google/veo-3.1-fast-generate-preview`
- Tryby: text-to-video, image-to-video i przepływy z pojedynczym wideo referencyjnym
- Obsługuje `aspectRatio`, `resolution` i `audio`
- Obecny zakres ograniczenia czasu trwania: **od 4 do 8 sekund**

Aby używać Google jako domyślnego dostawcy wideo:

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

Zobacz [Generowanie wideo](/tools/video-generation), aby poznać współdzielone
parametry narzędzia, wybór dostawcy i zachowanie failover.

## Generowanie muzyki

Dołączony plugin `google` rejestruje też generowanie muzyki przez współdzielone
narzędzie `music_generate`.

- Domyślny model muzyczny: `google/lyria-3-clip-preview`
- Obsługuje też `google/lyria-3-pro-preview`
- Kontrole promptu: `lyrics` i `instrumental`
- Format wyjściowy: domyślnie `mp3`, a także `wav` w `google/lyria-3-pro-preview`
- Wejścia referencyjne: do 10 obrazów
- Uruchomienia oparte na sesji są odłączane przez współdzielony przepływ zadania/statusu, w tym `action: "status"`

Aby używać Google jako domyślnego dostawcy muzyki:

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

Zobacz [Generowanie muzyki](/tools/music-generation), aby poznać współdzielone
parametry narzędzia, wybór dostawcy i zachowanie failover.

## Uwaga dotycząca środowiska

Jeśli Gateway działa jako demon (launchd/systemd), upewnij się, że `GEMINI_API_KEY`
jest dostępny dla tego procesu (na przykład w `~/.openclaw/.env` lub przez
`env.shellEnv`).
