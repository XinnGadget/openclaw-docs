---
read_when:
    - Generar videos mediante el agente
    - Configurar proveedores y modelos de generación de video
    - Comprender los parámetros de la herramienta `video_generate`
summary: Genera videos a partir de texto, imágenes o videos existentes usando 12 backends de proveedor
title: Generación de video
x-i18n:
    generated_at: "2026-04-11T02:48:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6848d03ef578181902517d068e8d9fe2f845e572a90481bbdf7bd9f1c591f245
    source_path: tools/video-generation.md
    workflow: 15
---

# Generación de video

Los agentes de OpenClaw pueden generar videos a partir de prompts de texto, imágenes de referencia o videos existentes. Se admiten doce backends de proveedor, cada uno con distintas opciones de modelo, modos de entrada y conjuntos de funciones. El agente elige automáticamente el proveedor correcto según tu configuración y las claves de API disponibles.

<Note>
La herramienta `video_generate` solo aparece cuando hay al menos un proveedor de generación de video disponible. Si no la ves en las herramientas de tu agente, configura una clave de API del proveedor o `agents.defaults.videoGenerationModel`.
</Note>

OpenClaw trata la generación de video como tres modos de runtime:

- `generate` para solicitudes de texto a video sin medios de referencia
- `imageToVideo` cuando la solicitud incluye una o más imágenes de referencia
- `videoToVideo` cuando la solicitud incluye uno o más videos de referencia

Los proveedores pueden admitir cualquier subconjunto de esos modos. La herramienta valida el
modo activo antes del envío e informa los modos admitidos en `action=list`.

## Inicio rápido

1. Configura una clave de API para cualquier proveedor compatible:

```bash
export GEMINI_API_KEY="your-key"
```

2. Opcionalmente fija un modelo predeterminado:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. Pídele al agente:

> Genera un video cinematográfico de 5 segundos de una langosta amistosa surfeando al atardecer.

El agente llama automáticamente a `video_generate`. No se necesita allowlist de herramientas.

## Qué ocurre cuando generas un video

La generación de video es asíncrona. Cuando el agente llama a `video_generate` en una sesión:

1. OpenClaw envía la solicitud al proveedor y devuelve inmediatamente un ID de tarea.
2. El proveedor procesa el trabajo en segundo plano (normalmente entre 30 segundos y 5 minutos, según el proveedor y la resolución).
3. Cuando el video está listo, OpenClaw activa la misma sesión con un evento interno de finalización.
4. El agente publica el video terminado de vuelta en la conversación original.

Mientras haya un trabajo en curso, las llamadas duplicadas a `video_generate` en la misma sesión devuelven el estado actual de la tarea en lugar de iniciar otra generación. Usa `openclaw tasks list` o `openclaw tasks show <taskId>` para comprobar el progreso desde la CLI.

Fuera de las ejecuciones del agente respaldadas por sesión (por ejemplo, invocaciones directas de herramientas), la herramienta recurre a la generación en línea y devuelve la ruta final del medio en el mismo turno.

### Ciclo de vida de la tarea

Cada solicitud `video_generate` pasa por cuatro estados:

1. **queued** -- tarea creada, esperando a que el proveedor la acepte.
2. **running** -- el proveedor está procesando (normalmente entre 30 segundos y 5 minutos, según el proveedor y la resolución).
3. **succeeded** -- video listo; el agente se activa y lo publica en la conversación.
4. **failed** -- error o timeout del proveedor; el agente se activa con detalles del error.

Comprueba el estado desde la CLI:

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

Prevención de duplicados: si ya hay una tarea de video `queued` o `running` para la sesión actual, `video_generate` devuelve el estado de la tarea existente en lugar de iniciar una nueva. Usa `action: "status"` para comprobarlo explícitamente sin activar una nueva generación.

## Proveedores compatibles

| Proveedor | Modelo predeterminado           | Texto | Ref. de imagen     | Ref. de video    | Clave de API                               |
| --------- | ------------------------------- | ----- | ------------------ | ---------------- | ------------------------------------------ |
| Alibaba   | `wan2.6-t2v`                    | Sí    | Sí (URL remota)    | Sí (URL remota)  | `MODELSTUDIO_API_KEY`                      |
| BytePlus  | `seedance-1-0-lite-t2v-250428`  | Sí    | 1 imagen           | No               | `BYTEPLUS_API_KEY`                         |
| ComfyUI   | `workflow`                      | Sí    | 1 imagen           | No               | `COMFY_API_KEY` o `COMFY_CLOUD_API_KEY`    |
| fal       | `fal-ai/minimax/video-01-live`  | Sí    | 1 imagen           | No               | `FAL_KEY`                                  |
| Google    | `veo-3.1-fast-generate-preview` | Sí    | 1 imagen           | 1 video          | `GEMINI_API_KEY`                           |
| MiniMax   | `MiniMax-Hailuo-2.3`            | Sí    | 1 imagen           | No               | `MINIMAX_API_KEY`                          |
| OpenAI    | `sora-2`                        | Sí    | 1 imagen           | 1 video          | `OPENAI_API_KEY`                           |
| Qwen      | `wan2.6-t2v`                    | Sí    | Sí (URL remota)    | Sí (URL remota)  | `QWEN_API_KEY`                             |
| Runway    | `gen4.5`                        | Sí    | 1 imagen           | 1 video          | `RUNWAYML_API_SECRET`                      |
| Together  | `Wan-AI/Wan2.2-T2V-A14B`        | Sí    | 1 imagen           | No               | `TOGETHER_API_KEY`                         |
| Vydra     | `veo3`                          | Sí    | 1 imagen (`kling`) | No               | `VYDRA_API_KEY`                            |
| xAI       | `grok-imagine-video`            | Sí    | 1 imagen           | 1 video          | `XAI_API_KEY`                              |

Algunos proveedores aceptan variables de entorno adicionales o alternativas para la clave de API. Consulta las páginas individuales de [proveedores](#related) para más detalles.

Ejecuta `video_generate action=list` para inspeccionar los proveedores, modelos y
modos de runtime disponibles en tiempo de ejecución.

### Matriz de capacidades declarada

Este es el contrato explícito de modos usado por `video_generate`, las pruebas de contrato
y el barrido compartido en vivo.

| Proveedor | `generate` | `imageToVideo` | `videoToVideo` | Rutas compartidas en vivo hoy                                                                                                             |
| --------- | ---------- | -------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba   | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; `videoToVideo` se omite porque este proveedor necesita URLs de video remotas `http(s)`                      |
| BytePlus  | Sí         | Sí             | No             | `generate`, `imageToVideo`                                                                                                                |
| ComfyUI   | Sí         | Sí             | No             | No está en el barrido compartido; la cobertura específica de workflow vive con las pruebas de Comfy                                      |
| fal       | Sí         | Sí             | No             | `generate`, `imageToVideo`                                                                                                                |
| Google    | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; el `videoToVideo` compartido se omite porque el barrido actual de Gemini/Veo respaldado por buffer no acepta esa entrada |
| MiniMax   | Sí         | Sí             | No             | `generate`, `imageToVideo`                                                                                                                |
| OpenAI    | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; el `videoToVideo` compartido se omite porque esta ruta actual de organización/entrada requiere acceso del proveedor a inpaint/remix |
| Qwen      | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; `videoToVideo` se omite porque este proveedor necesita URLs de video remotas `http(s)`                      |
| Runway    | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; `videoToVideo` se ejecuta solo cuando el modelo seleccionado es `runway/gen4_aleph`                         |
| Together  | Sí         | Sí             | No             | `generate`, `imageToVideo`                                                                                                                |
| Vydra     | Sí         | Sí             | No             | `generate`; el `imageToVideo` compartido se omite porque el `veo3` incluido es solo de texto y el `kling` incluido requiere una URL remota de imagen |
| xAI       | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; `videoToVideo` se omite porque este proveedor actualmente necesita una URL remota de MP4                    |

## Parámetros de la herramienta

### Obligatorios

| Parámetro | Tipo   | Descripción                                                                  |
| --------- | ------ | ---------------------------------------------------------------------------- |
| `prompt`  | string | Descripción de texto del video que se va a generar (obligatorio para `action: "generate"`) |

### Entradas de contenido

| Parámetro | Tipo     | Descripción                            |
| --------- | -------- | -------------------------------------- |
| `image`   | string   | Imagen de referencia única (ruta o URL) |
| `images`  | string[] | Varias imágenes de referencia (hasta 5) |
| `video`   | string   | Video de referencia único (ruta o URL)  |
| `videos`  | string[] | Varios videos de referencia (hasta 4)   |

### Controles de estilo

| Parámetro        | Tipo    | Descripción                                                             |
| ---------------- | ------- | ----------------------------------------------------------------------- |
| `aspectRatio`    | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`     | string  | `480P`, `720P`, `768P` o `1080P`                                        |
| `durationSeconds`| number  | Duración objetivo en segundos (redondeada al valor compatible más cercano del proveedor) |
| `size`           | string  | Sugerencia de tamaño cuando el proveedor lo admite                      |
| `audio`          | boolean | Habilita audio generado cuando se admite                               |
| `watermark`      | boolean | Activa o desactiva la marca de agua del proveedor cuando se admite      |

### Avanzados

| Parámetro | Tipo   | Descripción                                      |
| --------- | ------ | ------------------------------------------------ |
| `action`  | string | `"generate"` (predeterminado), `"status"` o `"list"` |
| `model`   | string | Sobrescritura de proveedor/modelo (por ejemplo `runway/gen4.5`) |
| `filename`| string | Sugerencia de nombre de archivo                  |

No todos los proveedores admiten todos los parámetros. OpenClaw ya normaliza la duración al valor compatible más cercano del proveedor y también reasigna sugerencias de geometría traducidas, como tamaño a relación de aspecto, cuando un proveedor de fallback expone una superficie de control distinta. Las sobrescrituras realmente no compatibles se ignoran según el mejor esfuerzo y se informan como advertencias en el resultado de la herramienta. Los límites estrictos de capacidad (como demasiadas entradas de referencia) fallan antes del envío.

Los resultados de la herramienta informan la configuración aplicada. Cuando OpenClaw reasigna duración o geometría durante el fallback de proveedor, los valores devueltos de `durationSeconds`, `size`, `aspectRatio` y `resolution` reflejan lo que se envió, y `details.normalization` captura la traducción entre lo solicitado y lo aplicado.

Las entradas de referencia también seleccionan el modo de runtime:

- Sin medios de referencia: `generate`
- Cualquier referencia de imagen: `imageToVideo`
- Cualquier referencia de video: `videoToVideo`

Las referencias mixtas de imagen y video no son una superficie de capacidad compartida estable.
Prefiere un tipo de referencia por solicitud.

## Acciones

- **generate** (predeterminado) -- crea un video a partir del prompt dado y entradas de referencia opcionales.
- **status** -- comprueba el estado de la tarea de video en curso para la sesión actual sin iniciar otra generación.
- **list** -- muestra los proveedores, modelos y sus capacidades disponibles.

## Selección de modelo

Al generar un video, OpenClaw resuelve el modelo en este orden:

1. **Parámetro de herramienta `model`** -- si el agente especifica uno en la llamada.
2. **`videoGenerationModel.primary`** -- desde la configuración.
3. **`videoGenerationModel.fallbacks`** -- se prueban en orden.
4. **Detección automática** -- usa los proveedores que tienen autenticación válida, empezando por el proveedor predeterminado actual y luego los proveedores restantes en orden alfabético.

Si un proveedor falla, el siguiente candidato se prueba automáticamente. Si todos los candidatos fallan, el error incluye detalles de cada intento.

Establece `agents.defaults.mediaGenerationAutoProviderFallback: false` si quieres que
la generación de video use solo las entradas explícitas `model`, `primary` y `fallbacks`.

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

HeyGen video-agent en fal se puede fijar con:

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

Seedance 2.0 en fal se puede fijar con:

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

## Notas sobre proveedores

| Proveedor | Notas                                                                                                                                                               |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba   | Usa el endpoint asíncrono de DashScope/Model Studio. Las imágenes y videos de referencia deben ser URLs remotas `http(s)`.                                        |
| BytePlus  | Solo una imagen de referencia.                                                                                                                                      |
| ComfyUI   | Ejecución local o en la nube impulsada por workflows. Admite texto a video e imagen a video mediante el grafo configurado.                                        |
| fal       | Usa un flujo respaldado por cola para trabajos de larga duración. Solo una imagen de referencia. Incluye referencias de modelo de HeyGen video-agent y de Seedance 2.0 para texto a video e imagen a video. |
| Google    | Usa Gemini/Veo. Admite una imagen o un video de referencia.                                                                                                        |
| MiniMax   | Solo una imagen de referencia.                                                                                                                                      |
| OpenAI    | Solo se reenvía la sobrescritura `size`. Otras sobrescrituras de estilo (`aspectRatio`, `resolution`, `audio`, `watermark`) se ignoran con una advertencia.       |
| Qwen      | Mismo backend DashScope que Alibaba. Las entradas de referencia deben ser URLs remotas `http(s)`; los archivos locales se rechazan de entrada.                    |
| Runway    | Admite archivos locales mediante URI de datos. `videoToVideo` requiere `runway/gen4_aleph`. Las ejecuciones solo de texto exponen relaciones de aspecto `16:9` y `9:16`. |
| Together  | Solo una imagen de referencia.                                                                                                                                      |
| Vydra     | Usa `https://www.vydra.ai/api/v1` directamente para evitar redirecciones que descartan autenticación. `veo3` incluido es solo de texto a video; `kling` requiere una URL remota de imagen. |
| xAI       | Admite flujos de texto a video, imagen a video y edición/extensión de video remoto.                                                                                |

## Modos de capacidad del proveedor

El contrato compartido de generación de video ahora permite que los proveedores declaren
capacidades específicas por modo en lugar de solo límites agregados planos. Las nuevas implementaciones de proveedores
deben preferir bloques de modo explícitos:

```typescript
capabilities: {
  generate: {
    maxVideos: 1,
    maxDurationSeconds: 10,
    supportsResolution: true,
  },
  imageToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputImages: 1,
    maxDurationSeconds: 5,
  },
  videoToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputVideos: 1,
    maxDurationSeconds: 5,
  },
}
```

Los campos agregados planos como `maxInputImages` y `maxInputVideos` no
son suficientes para anunciar compatibilidad con modos de transformación. Los proveedores deben declarar
`generate`, `imageToVideo` y `videoToVideo` explícitamente para que las pruebas en vivo,
las pruebas de contrato y la herramienta compartida `video_generate` puedan validar la compatibilidad de modos
de forma determinista.

## Pruebas en vivo

Cobertura en vivo opcional para los proveedores compartidos incluidos:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts
```

Wrapper del repositorio:

```bash
pnpm test:live:media video
```

Este archivo en vivo carga variables de entorno faltantes de proveedores desde `~/.profile`, da prioridad a las
claves de API de env/vivo frente a los perfiles de autenticación almacenados de forma predeterminada, y ejecuta los
modos declarados que puede ejercitar de forma segura con medios locales:

- `generate` para cada proveedor del barrido
- `imageToVideo` cuando `capabilities.imageToVideo.enabled`
- `videoToVideo` cuando `capabilities.videoToVideo.enabled` y el proveedor/modelo
  acepta entrada de video local respaldada por buffer en el barrido compartido

Hoy la ruta compartida en vivo `videoToVideo` cubre:

- `runway` solo cuando seleccionas `runway/gen4_aleph`

## Configuración

Establece el modelo predeterminado de generación de video en la configuración de OpenClaw:

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

- [Descripción general de herramientas](/es/tools)
- [Tareas en segundo plano](/es/automation/tasks) -- seguimiento de tareas para generación de video asíncrona
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
- [Models](/es/concepts/models)
