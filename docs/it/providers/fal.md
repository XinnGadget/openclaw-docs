---
read_when:
    - Vuoi usare la generazione di immagini fal in OpenClaw
    - Hai bisogno del flusso di autenticazione `FAL_KEY`
    - Vuoi i valori predefiniti fal per `image_generate` o `video_generate`
summary: Configurazione di fal per la generazione di immagini e video in OpenClaw
title: fal
x-i18n:
    generated_at: "2026-04-11T02:47:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9bfe4f69124e922a79a516a1bd78f0c00f7a45f3c6f68b6d39e0d196fa01beb3
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw include un provider `fal` integrato per la generazione ospitata di immagini e video.

- Provider: `fal`
- Auth: `FAL_KEY` (canonico; anche `FAL_API_KEY` funziona come fallback)
- API: endpoint dei modelli fal

## Avvio rapido

1. Imposta la chiave API:

```bash
openclaw onboard --auth-choice fal-api-key
```

2. Imposta un modello immagine predefinito:

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

## Generazione di immagini

Il provider di generazione immagini `fal` integrato usa come predefinito
`fal/fal-ai/flux/dev`.

- Generazione: fino a 4 immagini per richiesta
- Modalità modifica: abilitata, 1 immagine di riferimento
- Supporta `size`, `aspectRatio` e `resolution`
- Limitazione attuale della modifica: l'endpoint di modifica immagini fal **non** supporta
  override di `aspectRatio`

Per usare fal come provider immagine predefinito:

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

## Generazione di video

Il provider di generazione video `fal` integrato usa come predefinito
`fal/fal-ai/minimax/video-01-live`.

- Modalità: flussi text-to-video e con singola immagine di riferimento
- Runtime: flusso submit/status/result basato su coda per job di lunga durata
- Riferimento modello HeyGen video-agent:
  - `fal/fal-ai/heygen/v2/video-agent`
- Riferimenti modello Seedance 2.0:
  - `fal/bytedance/seedance-2.0/fast/text-to-video`
  - `fal/bytedance/seedance-2.0/fast/image-to-video`
  - `fal/bytedance/seedance-2.0/text-to-video`
  - `fal/bytedance/seedance-2.0/image-to-video`

Per usare Seedance 2.0 come modello video predefinito:

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

Per usare HeyGen video-agent come modello video predefinito:

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

## Correlati

- [Image Generation](/it/tools/image-generation)
- [Video Generation](/it/tools/video-generation)
- [Configuration Reference](/it/gateway/configuration-reference#agent-defaults)
