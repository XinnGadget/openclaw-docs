---
read_when:
    - Buscas una descripción general de las capacidades de medios
    - Decides qué proveedor de medios configurar
    - Quieres entender cómo funciona la generación asíncrona de medios
summary: Página de inicio unificada para capacidades de generación, comprensión y voz de medios
title: Descripción general de medios
x-i18n:
    generated_at: "2026-04-07T05:07:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfee08eb91ec3e827724c8fa99bff7465356f6f1ac1b146562f35651798e3fd6
    source_path: tools/media-overview.md
    workflow: 15
---

# Generación y comprensión de medios

OpenClaw genera imágenes, videos y música, comprende medios entrantes (imágenes, audio, video) y reproduce respuestas en voz alta con conversión de texto a voz. Todas las capacidades de medios están controladas por herramientas: el agente decide cuándo usarlas según la conversación, y cada herramienta solo aparece cuando hay al menos un proveedor de respaldo configurado.

## Capacidades de un vistazo

| Capacidad                 | Herramienta       | Proveedores                                                                                  | Qué hace                                                   |
| ------------------------- | ----------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Generación de imágenes    | `image_generate`  | ComfyUI, fal, Google, MiniMax, OpenAI, Vydra                                                | Crea o edita imágenes a partir de prompts de texto o referencias |
| Generación de video       | `video_generate`  | Alibaba, BytePlus, ComfyUI, fal, Google, MiniMax, OpenAI, Qwen, Runway, Together, Vydra, xAI | Crea videos a partir de texto, imágenes o videos existentes |
| Generación de música      | `music_generate`  | ComfyUI, Google, MiniMax                                                                     | Crea música o pistas de audio a partir de prompts de texto |
| Conversión de texto a voz (TTS) | `tts`      | ElevenLabs, Microsoft, MiniMax, OpenAI                                                       | Convierte respuestas salientes en audio hablado            |
| Comprensión de medios     | (automática)      | Cualquier proveedor de modelos con capacidad de visión/audio, además de respaldos de CLI     | Resume imágenes, audio y video entrantes                   |

## Matriz de capacidades por proveedor

Esta tabla muestra qué proveedores admiten qué capacidades de medios en toda la plataforma.

| Proveedor  | Imagen | Video | Música | TTS | STT / transcripción | Comprensión de medios |
| ---------- | ------ | ----- | ------ | --- | ------------------- | --------------------- |
| Alibaba    |        | Sí    |        |     |                     |                       |
| BytePlus   |        | Sí    |        |     |                     |                       |
| ComfyUI    | Sí     | Sí    | Sí     |     |                     |                       |
| Deepgram   |        |       |        |     | Sí                  |                       |
| ElevenLabs |        |       |        | Sí  |                     |                       |
| fal        | Sí     | Sí    |        |     |                     |                       |
| Google     | Sí     | Sí    | Sí     |     |                     | Sí                    |
| Microsoft  |        |       |        | Sí  |                     |                       |
| MiniMax    | Sí     | Sí    | Sí     | Sí  |                     |                       |
| OpenAI     | Sí     | Sí    |        | Sí  | Sí                  | Sí                    |
| Qwen       |        | Sí    |        |     |                     |                       |
| Runway     |        | Sí    |        |     |                     |                       |
| Together   |        | Sí    |        |     |                     |                       |
| Vydra      | Sí     | Sí    |        |     |                     |                       |
| xAI        |        | Sí    |        |     |                     |                       |

<Note>
La comprensión de medios usa cualquier modelo con capacidad de visión o audio registrado en la configuración de tu proveedor. La tabla anterior destaca proveedores con soporte dedicado para comprensión de medios; la mayoría de los proveedores de LLM con modelos multimodales (Anthropic, Google, OpenAI, etc.) también pueden comprender medios entrantes cuando están configurados como el modelo de respuesta activo.
</Note>

## Cómo funciona la generación asíncrona

La generación de video y música se ejecuta como tareas en segundo plano porque el procesamiento del proveedor suele tardar entre 30 segundos y varios minutos. Cuando el agente llama a `video_generate` o `music_generate`, OpenClaw envía la solicitud al proveedor, devuelve de inmediato un id de tarea y hace seguimiento del trabajo en el registro de tareas. El agente sigue respondiendo a otros mensajes mientras el trabajo se ejecuta. Cuando el proveedor termina, OpenClaw reactiva al agente para que pueda publicar el medio terminado en el canal original. La generación de imágenes y TTS son síncronas y se completan en línea con la respuesta.

## Enlaces rápidos

- [Generación de imágenes](/es/tools/image-generation) -- generar y editar imágenes
- [Generación de video](/es/tools/video-generation) -- texto a video, imagen a video y video a video
- [Generación de música](/es/tools/music-generation) -- crear música y pistas de audio
- [Conversión de texto a voz](/es/tools/tts) -- convertir respuestas en audio hablado
- [Comprensión de medios](/es/nodes/media-understanding) -- comprender imágenes, audio y video entrantes
