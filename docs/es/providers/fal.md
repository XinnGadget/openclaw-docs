---
read_when:
    - Quieres usar la generación de imágenes de fal en OpenClaw
    - Necesitas el flujo de autenticación `FAL_KEY`
    - Quieres valores predeterminados de fal para `image_generate` o `video_generate`
summary: Configuración de generación de imágenes y video de fal en OpenClaw
title: fal
x-i18n:
    generated_at: "2026-04-11T02:47:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9bfe4f69124e922a79a516a1bd78f0c00f7a45f3c6f68b6d39e0d196fa01beb3
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw incluye un proveedor integrado `fal` para la generación alojada de imágenes y video.

- Proveedor: `fal`
- Autenticación: `FAL_KEY` (canónica; `FAL_API_KEY` también funciona como respaldo)
- API: endpoints de modelos de fal

## Inicio rápido

1. Establece la clave de API:

```bash
openclaw onboard --auth-choice fal-api-key
```

2. Establece un modelo de imagen predeterminado:

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

## Generación de imágenes

El proveedor integrado de generación de imágenes `fal` usa de forma predeterminada
`fal/fal-ai/flux/dev`.

- Generación: hasta 4 imágenes por solicitud
- Modo de edición: habilitado, 1 imagen de referencia
- Admite `size`, `aspectRatio` y `resolution`
- Advertencia actual de edición: el endpoint de edición de imágenes de fal **no** admite
  anulaciones de `aspectRatio`

Para usar fal como proveedor de imágenes predeterminado:

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

## Generación de video

El proveedor integrado de generación de video `fal` usa de forma predeterminada
`fal/fal-ai/minimax/video-01-live`.

- Modos: flujos de texto a video y de referencia de una sola imagen
- Entorno de ejecución: flujo respaldado por cola de envío/estado/resultado para trabajos de larga duración
- Referencia de modelo de agente de video de HeyGen:
  - `fal/fal-ai/heygen/v2/video-agent`
- Referencias de modelo de Seedance 2.0:
  - `fal/bytedance/seedance-2.0/fast/text-to-video`
  - `fal/bytedance/seedance-2.0/fast/image-to-video`
  - `fal/bytedance/seedance-2.0/text-to-video`
  - `fal/bytedance/seedance-2.0/image-to-video`

Para usar Seedance 2.0 como modelo de video predeterminado:

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

Para usar el agente de video de HeyGen como modelo de video predeterminado:

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

## Relacionado

- [Generación de imágenes](/es/tools/image-generation)
- [Generación de video](/es/tools/video-generation)
- [Referencia de configuración](/es/gateway/configuration-reference#agent-defaults)
