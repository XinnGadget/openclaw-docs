---
read_when:
    - Chcesz używać lokalnych workflow ComfyUI z OpenClaw
    - Chcesz używać Comfy Cloud z workflow obrazów, wideo lub muzyki
    - Potrzebujesz kluczy konfiguracji dla wbudowanego pluginu comfy
summary: Konfiguracja generowania obrazów, wideo i muzyki z workflow ComfyUI w OpenClaw
title: ComfyUI
x-i18n:
    generated_at: "2026-04-06T03:11:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: e645f32efdffdf4cd498684f1924bb953a014d3656b48f4b503d64e38c61ba9c
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

OpenClaw dostarcza wbudowany plugin `comfy` do uruchamiania ComfyUI sterowanego workflow.

- Dostawca: `comfy`
- Modele: `comfy/workflow`
- Współdzielone powierzchnie: `image_generate`, `video_generate`, `music_generate`
- Uwierzytelnianie: brak dla lokalnego ComfyUI; `COMFY_API_KEY` lub `COMFY_CLOUD_API_KEY` dla Comfy Cloud
- API: ComfyUI `/prompt` / `/history` / `/view` oraz Comfy Cloud `/api/*`

## Co jest obsługiwane

- Generowanie obrazów z pliku JSON workflow
- Edycja obrazów z 1 przesłanym obrazem referencyjnym
- Generowanie wideo z pliku JSON workflow
- Generowanie wideo z 1 przesłanym obrazem referencyjnym
- Generowanie muzyki lub audio przez współdzielone narzędzie `music_generate`
- Pobieranie wyników z skonfigurowanego node albo ze wszystkich pasujących node wyjściowych

Wbudowany plugin jest sterowany workflow, więc OpenClaw nie próbuje mapować ogólnych parametrów
`size`, `aspectRatio`, `resolution`, `durationSeconds` ani ustawień w stylu TTS
na Twój graf.

## Układ konfiguracji

Comfy obsługuje współdzielone ustawienia połączenia na najwyższym poziomie oraz sekcje workflow
dla poszczególnych zdolności:

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

Współdzielone klucze:

- `mode`: `local` lub `cloud`
- `baseUrl`: domyślnie `http://127.0.0.1:8188` dla trybu local lub `https://cloud.comfy.org` dla trybu cloud
- `apiKey`: opcjonalna alternatywa dla klucza w zmiennych env
- `allowPrivateNetwork`: zezwala na prywatny/LAN `baseUrl` w trybie cloud

Klucze dla poszczególnych zdolności w `image`, `video` lub `music`:

- `workflow` lub `workflowPath`: wymagane
- `promptNodeId`: wymagane
- `promptInputName`: domyślnie `text`
- `outputNodeId`: opcjonalne
- `pollIntervalMs`: opcjonalne
- `timeoutMs`: opcjonalne

Sekcje obrazów i wideo obsługują także:

- `inputImageNodeId`: wymagane, gdy przekazujesz obraz referencyjny
- `inputImageInputName`: domyślnie `image`

## Zgodność wsteczna

Istniejąca konfiguracja obrazu na najwyższym poziomie nadal działa:

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

OpenClaw traktuje ten starszy kształt jako konfigurację workflow obrazu.

## Workflow obrazów

Ustaw domyślny model obrazu:

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

Przykład edycji z obrazem referencyjnym:

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

## Workflow wideo

Ustaw domyślny model wideo:

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

Workflow wideo Comfy obecnie obsługują text-to-video i image-to-video przez
skonfigurowany graf. OpenClaw nie przekazuje wejściowych plików wideo do workflow Comfy.

## Workflow muzyki

Wbudowany plugin rejestruje dostawcę generowania muzyki dla wyjść audio lub muzycznych
zdefiniowanych przez workflow, udostępnianego przez współdzielone narzędzie `music_generate`:

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

Użyj sekcji konfiguracji `music`, aby wskazać plik JSON workflow audio i
node wyjściowy.

## Comfy Cloud

Użyj `mode: "cloud"` oraz jednego z poniższych:

- `COMFY_API_KEY`
- `COMFY_CLOUD_API_KEY`
- `models.providers.comfy.apiKey`

Tryb cloud nadal używa tych samych sekcji workflow `image`, `video` i `music`.

## Testy live

Dla wbudowanego pluginu istnieje opcjonalne pokrycie live:

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

Test live pomija poszczególne przypadki obrazów, wideo lub muzyki, jeśli odpowiadająca im
sekcja workflow Comfy nie jest skonfigurowana.

## Powiązane

- [Generowanie obrazów](/pl/tools/image-generation)
- [Generowanie wideo](/tools/video-generation)
- [Generowanie muzyki](/tools/music-generation)
- [Katalog dostawców](/pl/providers/index)
- [Dokumentacja konfiguracji](/pl/gateway/configuration-reference#agent-defaults)
