---
read_when:
    - Generar videos mediante el agente
    - Configurar proveedores y modelos de generación de video
    - Comprender los parámetros de la herramienta `video_generate`
summary: Genera videos a partir de texto, imágenes o videos existentes mediante 12 backends de proveedores
title: Generación de video
x-i18n:
    generated_at: "2026-04-06T05:12:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 90d8a392b35adbd899232b02c55c10895b9d7ffc9858d6ca448f2e4e4a57f12f
    source_path: tools/video-generation.md
    workflow: 15
---

# Generación de video

Los agentes de OpenClaw pueden generar videos a partir de indicaciones de texto, imágenes de referencia o videos existentes. Se admiten doce backends de proveedores, cada uno con distintas opciones de modelo, modos de entrada y conjuntos de funciones. El agente elige automáticamente el proveedor adecuado según tu configuración y las claves de API disponibles.

<Note>
La herramienta `video_generate` solo aparece cuando hay al menos un proveedor de generación de video disponible. Si no la ves en las herramientas de tu agente, configura una clave de API del proveedor o establece `agents.defaults.videoGenerationModel`.
</Note>

## Inicio rápido

1. Configura una clave de API para cualquier proveedor compatible:

```bash
export GEMINI_API_KEY="your-key"
```

2. Opcionalmente, fija un modelo predeterminado:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. Pídeselo al agente:

> Genera un video cinematográfico de 5 segundos de una langosta amistosa surfeando al atardecer.

El agente llama a `video_generate` automáticamente. No se necesita ninguna lista de herramientas permitidas.

## Qué sucede cuando generas un video

La generación de video es asíncrona. Cuando el agente llama a `video_generate` en una sesión:

1. OpenClaw envía la solicitud al proveedor y devuelve de inmediato un ID de tarea.
2. El proveedor procesa el trabajo en segundo plano (normalmente entre 30 segundos y 5 minutos, según el proveedor y la resolución).
3. Cuando el video está listo, OpenClaw reactiva la misma sesión con un evento interno de finalización.
4. El agente publica el video terminado de vuelta en la conversación original.

Mientras una tarea está en curso, las llamadas duplicadas a `video_generate` en la misma sesión devuelven el estado actual de la tarea en lugar de iniciar otra generación. Usa `openclaw tasks list` o `openclaw tasks show <taskId>` para comprobar el progreso desde la CLI.

Fuera de las ejecuciones del agente respaldadas por sesión (por ejemplo, invocaciones directas de herramientas), la herramienta recurre a la generación en línea y devuelve la ruta del medio final en el mismo turno.

## Proveedores compatibles

| Proveedor | Modelo predeterminado           | Texto | Imagen de ref.    | Video de ref.    | Clave de API                              |
| --------- | ------------------------------- | ----- | ----------------- | ---------------- | ----------------------------------------- |
| Alibaba   | `wan2.6-t2v`                    | Sí    | Sí (URL remota)   | Sí (URL remota)  | `MODELSTUDIO_API_KEY`                     |
| BytePlus  | `seedance-1-0-lite-t2v-250428`  | Sí    | 1 imagen          | No               | `BYTEPLUS_API_KEY`                        |
| ComfyUI   | `workflow`                      | Sí    | 1 imagen          | No               | `COMFY_API_KEY` o `COMFY_CLOUD_API_KEY`   |
| fal       | `fal-ai/minimax/video-01-live`  | Sí    | 1 imagen          | No               | `FAL_KEY`                                 |
| Google    | `veo-3.1-fast-generate-preview` | Sí    | 1 imagen          | 1 video          | `GEMINI_API_KEY`                          |
| MiniMax   | `MiniMax-Hailuo-2.3`            | Sí    | 1 imagen          | No               | `MINIMAX_API_KEY`                         |
| OpenAI    | `sora-2`                        | Sí    | 1 imagen          | 1 video          | `OPENAI_API_KEY`                          |
| Qwen      | `wan2.6-t2v`                    | Sí    | Sí (URL remota)   | Sí (URL remota)  | `QWEN_API_KEY`                            |
| Runway    | `gen4.5`                        | Sí    | 1 imagen          | 1 video          | `RUNWAYML_API_SECRET`                     |
| Together  | `Wan-AI/Wan2.2-T2V-A14B`        | Sí    | 1 imagen          | No               | `TOGETHER_API_KEY`                        |
| Vydra     | `veo3`                          | Sí    | 1 imagen (`kling`) | No              | `VYDRA_API_KEY`                           |
| xAI       | `grok-imagine-video`            | Sí    | 1 imagen          | 1 video          | `XAI_API_KEY`                             |

Algunos proveedores aceptan variables de entorno de clave de API adicionales o alternativas. Consulta las [páginas de proveedores](#related) individuales para obtener más detalles.

Ejecuta `video_generate action=list` para inspeccionar los proveedores y modelos disponibles en tiempo de ejecución.

## Parámetros de la herramienta

### Obligatorios

| Parámetro | Tipo   | Descripción                                                                  |
| --------- | ------ | ---------------------------------------------------------------------------- |
| `prompt`  | string | Descripción de texto del video que se va a generar (obligatoria para `action: "generate"`) |

### Entradas de contenido

| Parámetro | Tipo     | Descripción                              |
| --------- | -------- | ---------------------------------------- |
| `image`   | string   | Una sola imagen de referencia (ruta o URL) |
| `images`  | string[] | Varias imágenes de referencia (hasta 5)  |
| `video`   | string   | Un solo video de referencia (ruta o URL) |
| `videos`  | string[] | Varios videos de referencia (hasta 4)    |

### Controles de estilo

| Parámetro        | Tipo    | Descripción                                                             |
| ---------------- | ------- | ----------------------------------------------------------------------- |
| `aspectRatio`    | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`     | string  | `480P`, `720P` o `1080P`                                                |
| `durationSeconds` | number | Duración objetivo en segundos (redondeada al valor compatible más cercano del proveedor) |
| `size`           | string  | Indicación de tamaño cuando el proveedor lo admite                      |
| `audio`          | boolean | Habilita el audio generado cuando se admite                             |
| `watermark`      | boolean | Activa o desactiva la marca de agua del proveedor cuando se admite      |

### Avanzados

| Parámetro | Tipo   | Descripción                                    |
| --------- | ------ | ---------------------------------------------- |
| `action`  | string | `"generate"` (predeterminado), `"status"` o `"list"` |
| `model`   | string | Anulación de proveedor/modelo (por ejemplo, `runway/gen4.5`) |
| `filename` | string | Sugerencia de nombre de archivo de salida     |

No todos los proveedores admiten todos los parámetros. Las anulaciones no compatibles se ignoran según el mejor esfuerzo y se informan como advertencias en el resultado de la herramienta. Los límites estrictos de capacidad (como demasiadas entradas de referencia) fallan antes del envío.

## Acciones

- **generate** (predeterminada) -- crea un video a partir de la indicación dada y entradas de referencia opcionales.
- **status** -- comprueba el estado de la tarea de video en curso para la sesión actual sin iniciar otra generación.
- **list** -- muestra los proveedores, modelos y sus capacidades disponibles.

## Selección de modelo

Al generar un video, OpenClaw resuelve el modelo en este orden:

1. **Parámetro de herramienta `model`** -- si el agente especifica uno en la llamada.
2. **`videoGenerationModel.primary`** -- desde la configuración.
3. **`videoGenerationModel.fallbacks`** -- se prueban en orden.
4. **Detección automática** -- usa los proveedores que tienen autenticación válida, comenzando por el proveedor predeterminado actual y luego los proveedores restantes en orden alfabético.

Si un proveedor falla, se prueba automáticamente el siguiente candidato. Si todos los candidatos fallan, el error incluye detalles de cada intento.

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: ["runway/gen4.5", "qwen/wan2.6-t2v"],
      },
    },
  },
}
```

## Notas sobre proveedores

| Proveedor | Notas                                                                                                                                                        |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Alibaba   | Usa el endpoint asíncrono de DashScope/Model Studio. Las imágenes y videos de referencia deben ser URL `http(s)` remotas.                                  |
| BytePlus  | Solo admite una imagen de referencia.                                                                                                                        |
| ComfyUI   | Ejecución local o en la nube basada en flujos de trabajo. Admite texto a video e imagen a video mediante el grafo configurado.                             |
| fal       | Usa un flujo respaldado por cola para trabajos de larga duración. Solo admite una imagen de referencia.                                                     |
| Google    | Usa Gemini/Veo. Admite una imagen o un video de referencia.                                                                                                  |
| MiniMax   | Solo admite una imagen de referencia.                                                                                                                        |
| OpenAI    | Solo se reenvía la anulación `size`. Las demás anulaciones de estilo (`aspectRatio`, `resolution`, `audio`, `watermark`) se ignoran con una advertencia.   |
| Qwen      | El mismo backend de DashScope que Alibaba. Las entradas de referencia deben ser URL `http(s)` remotas; los archivos locales se rechazan por adelantado.    |
| Runway    | Admite archivos locales mediante URI de datos. Video a video requiere `runway/gen4_aleph`. Las ejecuciones solo con texto exponen las relaciones de aspecto `16:9` y `9:16`. |
| Together  | Solo admite una imagen de referencia.                                                                                                                        |
| Vydra     | Usa `https://www.vydra.ai/api/v1` directamente para evitar redirecciones que eliminan la autenticación. `veo3` se incluye solo como texto a video; `kling` requiere una URL de imagen remota. |
| xAI       | Admite flujos de texto a video, imagen a video y edición/extensión de video remoto.                                                                         |

## Configuración

Establece el modelo predeterminado de generación de video en tu configuración de OpenClaw:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-r2v-flash"],
      },
    },
  },
}
```

O mediante la CLI:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "qwen/wan2.6-t2v"
```

## Relacionado

- [Resumen de herramientas](/es/tools)
- [Tareas en segundo plano](/es/automation/tasks) -- seguimiento de tareas para la generación asíncrona de video
- [Alibaba Model Studio](/es/providers/alibaba)
- [BytePlus](/es/concepts/model-providers#byteplus-international)
- [ComfyUI](/es/providers/comfy)
- [fal](/es/providers/fal)
- [Google (Gemini)](/es/providers/google)
- [MiniMax](/es/providers/minimax)
- [OpenAI](/es/providers/openai)
- [Qwen](/es/providers/qwen)
- [Runway](/es/providers/runway)
- [Together AI](/es/providers/together)
- [Vydra](/es/providers/vydra)
- [xAI](/es/providers/xai)
- [Referencia de configuración](/es/gateway/configuration-reference#agent-defaults)
- [Modelos](/es/concepts/models)
