---
read_when:
    - Quieres generación multimedia de Vydra en OpenClaw
    - Necesitas orientación para configurar la clave API de Vydra
summary: Usa imagen, video y voz de Vydra en OpenClaw
title: Vydra
x-i18n:
    generated_at: "2026-04-07T05:05:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 24006a687ed6f9792e7b2b10927cc7ad71c735462a92ce03d5fa7c2b2ee2fcc2
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

El plugin Vydra incluido añade:

- generación de imágenes mediante `vydra/grok-imagine`
- generación de video mediante `vydra/veo3` y `vydra/kling`
- síntesis de voz mediante la ruta TTS de Vydra respaldada por ElevenLabs

OpenClaw usa la misma `VYDRA_API_KEY` para las tres capacidades.

## URL base importante

Usa `https://www.vydra.ai/api/v1`.

El host raíz de Vydra (`https://vydra.ai/api/v1`) actualmente redirige a `www`. Algunos clientes HTTP descartan `Authorization` en esa redirección entre hosts, lo que convierte una clave API válida en un fallo de autenticación engañoso. El plugin incluido usa directamente la URL base `www` para evitarlo.

## Configuración

Incorporación interactiva:

```bash
openclaw onboard --auth-choice vydra-api-key
```

O establece directamente la variable de entorno:

```bash
export VYDRA_API_KEY="vydra_live_..."
```

## Generación de imágenes

Modelo de imagen predeterminado:

- `vydra/grok-imagine`

Establécelo como proveedor de imágenes predeterminado:

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

La compatibilidad incluida actual es solo de texto a imagen. Las rutas de edición alojadas por Vydra esperan URLs remotas de imagen, y OpenClaw todavía no añade un puente de subida específico de Vydra en el plugin incluido.

Consulta [Generación de imágenes](/es/tools/image-generation) para ver el comportamiento compartido de la herramienta.

## Generación de video

Modelos de video registrados:

- `vydra/veo3` para texto a video
- `vydra/kling` para imagen a video

Establece Vydra como proveedor de video predeterminado:

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

Notas:

- `vydra/veo3` se incluye solo como texto a video.
- `vydra/kling` actualmente requiere una referencia a una URL remota de imagen. Las subidas de archivos locales se rechazan de inmediato.
- La ruta HTTP actual `kling` de Vydra ha sido inconsistente respecto a si requiere `image_url` o `video_url`; el proveedor incluido asigna la misma URL remota de imagen a ambos campos.
- El plugin incluido se mantiene conservador y no reenvía controles de estilo no documentados, como relación de aspecto, resolución, marca de agua o audio generado.

Cobertura live específica del proveedor:

```bash
OPENCLAW_LIVE_TEST=1 \
OPENCLAW_LIVE_VYDRA_VIDEO=1 \
pnpm test:live -- extensions/vydra/vydra.live.test.ts
```

El archivo live incluido de Vydra ahora cubre:

- `vydra/veo3` texto a video
- `vydra/kling` imagen a video usando una URL remota de imagen

Anula el fixture remoto de imagen cuando sea necesario:

```bash
export OPENCLAW_LIVE_VYDRA_KLING_IMAGE_URL="https://example.com/reference.png"
```

Consulta [Generación de video](/es/tools/video-generation) para ver el comportamiento compartido de la herramienta.

## Síntesis de voz

Establece Vydra como proveedor de voz:

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

Valores predeterminados:

- modelo: `elevenlabs/tts`
- ID de voz: `21m00Tcm4TlvDq8ikWAM`

El plugin incluido actualmente expone una voz predeterminada conocida por funcionar y devuelve archivos de audio MP3.

## Relacionado

- [Directorio de proveedores](/es/providers/index)
- [Generación de imágenes](/es/tools/image-generation)
- [Generación de video](/es/tools/video-generation)
