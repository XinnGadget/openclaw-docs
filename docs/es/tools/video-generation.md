---
read_when:
    - Generando videos mediante el agente
    - Configurando proveedores y modelos de generación de video
    - Entendiendo los parámetros de la herramienta video_generate
summary: Genera videos a partir de texto, imágenes o videos existentes usando 12 backends de proveedores
title: Generación de video
x-i18n:
    generated_at: "2026-04-07T05:07:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: bf1224c59a5f1217f56cf2001870aca710a09268677dcd12aad2efbe476e47b7
    source_path: tools/video-generation.md
    workflow: 15
---

# Generación de video

Los agentes de OpenClaw pueden generar videos a partir de prompts de texto, imágenes de referencia o videos existentes. Se admiten doce backends de proveedores, cada uno con distintas opciones de modelo, modos de entrada y conjuntos de funciones. El agente elige automáticamente el proveedor adecuado según tu configuración y las API keys disponibles.

<Note>
La herramienta `video_generate` solo aparece cuando hay al menos un proveedor de generación de video disponible. Si no la ves en las herramientas de tu agente, configura una API key de proveedor o establece `agents.defaults.videoGenerationModel`.
</Note>

OpenClaw trata la generación de video como tres modos de tiempo de ejecución:

- `generate` para solicitudes de texto a video sin multimedia de referencia
- `imageToVideo` cuando la solicitud incluye una o más imágenes de referencia
- `videoToVideo` cuando la solicitud incluye uno o más videos de referencia

Los proveedores pueden admitir cualquier subconjunto de esos modos. La herramienta valida el
modo activo antes del envío e informa los modos admitidos en `action=list`.

## Inicio rápido

1. Configura una API key para cualquier proveedor compatible:

```bash
export GEMINI_API_KEY="your-key"
```

2. Opcionalmente fija un modelo predeterminado:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. Pídele al agente:

> Genera un video cinematográfico de 5 segundos de una langosta amigable surfeando al atardecer.

El agente llama automáticamente a `video_generate`. No se necesita lista de permitidos de herramientas.

## Qué ocurre cuando generas un video

La generación de video es asíncrona. Cuando el agente llama a `video_generate` en una sesión:

1. OpenClaw envía la solicitud al proveedor y devuelve inmediatamente un ID de tarea.
2. El proveedor procesa el trabajo en segundo plano (normalmente de 30 segundos a 5 minutos según el proveedor y la resolución).
3. Cuando el video está listo, OpenClaw reactiva la misma sesión con un evento interno de finalización.
4. El agente publica el video terminado de vuelta en la conversación original.

Mientras un trabajo está en curso, las llamadas duplicadas a `video_generate` en la misma sesión devuelven el estado actual de la tarea en lugar de iniciar otra generación. Usa `openclaw tasks list` o `openclaw tasks show <taskId>` para comprobar el progreso desde la CLI.

Fuera de las ejecuciones del agente respaldadas por sesión (por ejemplo, invocaciones directas de herramientas), la herramienta recurre a la generación en línea y devuelve la ruta final del multimedia en el mismo turno.

### Ciclo de vida de la tarea

Cada solicitud `video_generate` pasa por cuatro estados:

1. **queued** -- tarea creada, esperando a que el proveedor la acepte.
2. **running** -- el proveedor está procesando (normalmente de 30 segundos a 5 minutos según el proveedor y la resolución).
3. **succeeded** -- video listo; el agente se reactiva y lo publica en la conversación.
4. **failed** -- error del proveedor o timeout; el agente se reactiva con detalles del error.

Comprueba el estado desde la CLI:

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

Prevención de duplicados: si ya hay una tarea de video `queued` o `running` para la sesión actual, `video_generate` devuelve el estado de la tarea existente en lugar de iniciar una nueva. Usa `action: "status"` para comprobarlo explícitamente sin activar una nueva generación.

## Proveedores compatibles

| Proveedor | Modelo predeterminado           | Texto | Referencia de imagen | Referencia de video | API key                                  |
| --------- | ------------------------------- | ----- | -------------------- | ------------------- | ---------------------------------------- |
| Alibaba   | `wan2.6-t2v`                    | Sí    | Sí (URL remota)      | Sí (URL remota)     | `MODELSTUDIO_API_KEY`                    |
| BytePlus  | `seedance-1-0-lite-t2v-250428`  | Sí    | 1 imagen             | No                  | `BYTEPLUS_API_KEY`                       |
| ComfyUI   | `workflow`                      | Sí    | 1 imagen             | No                  | `COMFY_API_KEY` o `COMFY_CLOUD_API_KEY` |
| fal       | `fal-ai/minimax/video-01-live`  | Sí    | 1 imagen             | No                  | `FAL_KEY`                                |
| Google    | `veo-3.1-fast-generate-preview` | Sí    | 1 imagen             | 1 video             | `GEMINI_API_KEY`                         |
| MiniMax   | `MiniMax-Hailuo-2.3`            | Sí    | 1 imagen             | No                  | `MINIMAX_API_KEY`                        |
| OpenAI    | `sora-2`                        | Sí    | 1 imagen             | 1 video             | `OPENAI_API_KEY`                         |
| Qwen      | `wan2.6-t2v`                    | Sí    | Sí (URL remota)      | Sí (URL remota)     | `QWEN_API_KEY`                           |
| Runway    | `gen4.5`                        | Sí    | 1 imagen             | 1 video             | `RUNWAYML_API_SECRET`                    |
| Together  | `Wan-AI/Wan2.2-T2V-A14B`        | Sí    | 1 imagen             | No                  | `TOGETHER_API_KEY`                       |
| Vydra     | `veo3`                          | Sí    | 1 imagen (`kling`)   | No                  | `VYDRA_API_KEY`                          |
| xAI       | `grok-imagine-video`            | Sí    | 1 imagen             | 1 video             | `XAI_API_KEY`                            |

Algunos proveedores aceptan variables de entorno de API key adicionales o alternativas. Consulta las [páginas de proveedores](#related) individuales para obtener detalles.

Ejecuta `video_generate action=list` para inspeccionar en tiempo de ejecución los proveedores, modelos y
modos de tiempo de ejecución disponibles.

### Matriz declarada de capacidades

Este es el contrato explícito de modos usado por `video_generate`, las pruebas de contrato
y la barrida compartida en vivo.

| Proveedor | `generate` | `imageToVideo` | `videoToVideo` | Carriles compartidos en vivo hoy                                                                                                           |
| --------- | ---------- | -------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba   | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; `videoToVideo` se omite porque este proveedor necesita URLs de video remotas `http(s)`                         |
| BytePlus  | Sí         | Sí             | No             | `generate`, `imageToVideo`                                                                                                                  |
| ComfyUI   | Sí         | Sí             | No             | No está en la barrida compartida; la cobertura específica del workflow vive con las pruebas de Comfy                                       |
| fal       | Sí         | Sí             | No             | `generate`, `imageToVideo`                                                                                                                  |
| Google    | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; `videoToVideo` compartido se omite porque la barrida actual de Gemini/Veo respaldada por buffer no acepta esa entrada |
| MiniMax   | Sí         | Sí             | No             | `generate`, `imageToVideo`                                                                                                                  |
| OpenAI    | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; `videoToVideo` compartido se omite porque esta ruta de organización/entrada actualmente necesita acceso de inpaint/remix del lado del proveedor |
| Qwen      | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; `videoToVideo` se omite porque este proveedor necesita URLs de video remotas `http(s)`                         |
| Runway    | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; `videoToVideo` solo se ejecuta cuando el modelo seleccionado es `runway/gen4_aleph`                            |
| Together  | Sí         | Sí             | No             | `generate`, `imageToVideo`                                                                                                                  |
| Vydra     | Sí         | Sí             | No             | `generate`; `imageToVideo` compartido se omite porque `veo3` empaquetado es solo de texto y `kling` empaquetado requiere una URL de imagen remota |
| xAI       | Sí         | Sí             | Sí             | `generate`, `imageToVideo`; `videoToVideo` se omite porque este proveedor actualmente necesita una URL remota de MP4                       |

## Parámetros de la herramienta

### Obligatorios

| Parámetro | Tipo   | Descripción                                                                    |
| --------- | ------ | ------------------------------------------------------------------------------ |
| `prompt`  | string | Descripción de texto del video que se va a generar (obligatorio para `action: "generate"`) |

### Entradas de contenido

| Parámetro | Tipo     | Descripción                              |
| --------- | -------- | ---------------------------------------- |
| `image`   | string   | Una sola imagen de referencia (ruta o URL) |
| `images`  | string[] | Varias imágenes de referencia (hasta 5)  |
| `video`   | string   | Un solo video de referencia (ruta o URL) |
| `videos`  | string[] | Varios videos de referencia (hasta 4)    |

### Controles de estilo

| Parámetro         | Tipo    | Descripción                                                               |
| ----------------- | ------- | ------------------------------------------------------------------------- |
| `aspectRatio`     | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`  |
| `resolution`      | string  | `480P`, `720P`, `768P` o `1080P`                                          |
| `durationSeconds` | number  | Duración objetivo en segundos (redondeada al valor admitido más cercano por el proveedor) |
| `size`            | string  | Indicación de tamaño cuando el proveedor lo admite                        |
| `audio`           | boolean | Habilita audio generado cuando se admite                                  |
| `watermark`       | boolean | Activa o desactiva la marca de agua del proveedor cuando se admite        |

### Avanzado

| Parámetro | Tipo   | Descripción                                       |
| ---------- | ------ | ------------------------------------------------ |
| `action`   | string | `"generate"` (predeterminado), `"status"` o `"list"` |
| `model`    | string | Anulación de proveedor/modelo (por ejemplo `runway/gen4.5`) |
| `filename` | string | Sugerencia de nombre de archivo                  |

No todos los proveedores admiten todos los parámetros. OpenClaw ya normaliza la duración al valor admitido más cercano por el proveedor, y también reasigna indicaciones geométricas traducidas como tamaño a relación de aspecto cuando un proveedor alternativo expone una superficie de control diferente. Las anulaciones realmente no admitidas se ignoran según el mejor esfuerzo y se informan como advertencias en el resultado de la herramienta. Los límites estrictos de capacidad (como demasiadas entradas de referencia) fallan antes del envío.

Los resultados de la herramienta informan la configuración aplicada. Cuando OpenClaw reasigna duración o geometría durante el failover del proveedor, los valores devueltos `durationSeconds`, `size`, `aspectRatio` y `resolution` reflejan lo que se envió, y `details.normalization` captura la traducción de solicitado a aplicado.

Las entradas de referencia también seleccionan el modo de tiempo de ejecución:

- Sin multimedia de referencia: `generate`
- Cualquier imagen de referencia: `imageToVideo`
- Cualquier video de referencia: `videoToVideo`

Las referencias mixtas de imágenes y videos no son una superficie estable de capacidad compartida.
Se recomienda usar un solo tipo de referencia por solicitud.

## Acciones

- **generate** (predeterminado) -- crear un video a partir del prompt dado y entradas de referencia opcionales.
- **status** -- comprobar el estado de la tarea de video en curso para la sesión actual sin iniciar otra generación.
- **list** -- mostrar los proveedores, modelos y sus capacidades disponibles.

## Selección de modelo

Al generar un video, OpenClaw resuelve el modelo en este orden:

1. **Parámetro de herramienta `model`** -- si el agente especifica uno en la llamada.
2. **`videoGenerationModel.primary`** -- desde la configuración.
3. **`videoGenerationModel.fallbacks`** -- se prueban en orden.
4. **Detección automática** -- usa proveedores que tienen autenticación válida, empezando por el proveedor predeterminado actual y luego los proveedores restantes en orden alfabético.

Si un proveedor falla, se prueba automáticamente el siguiente candidato. Si todos los candidatos fallan, el error incluye detalles de cada intento.

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

## Notas de proveedores

| Proveedor | Notas                                                                                                                                                       |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba   | Usa el endpoint asíncrono de DashScope/Model Studio. Las imágenes y videos de referencia deben ser URLs remotas `http(s)`.                                |
| BytePlus  | Solo una imagen de referencia.                                                                                                                              |
| ComfyUI   | Ejecución local o en la nube controlada por workflow. Admite texto a video e imagen a video mediante el grafo configurado.                                |
| fal       | Usa un flujo respaldado por cola para trabajos de larga duración. Solo una imagen de referencia.                                                           |
| Google    | Usa Gemini/Veo. Admite una imagen o un video de referencia.                                                                                                |
| MiniMax   | Solo una imagen de referencia.                                                                                                                              |
| OpenAI    | Solo se reenvía la anulación `size`. Otras anulaciones de estilo (`aspectRatio`, `resolution`, `audio`, `watermark`) se ignoran con una advertencia.      |
| Qwen      | Mismo backend DashScope que Alibaba. Las entradas de referencia deben ser URLs remotas `http(s)`; los archivos locales se rechazan de inmediato.          |
| Runway    | Admite archivos locales mediante URI de datos. Video a video requiere `runway/gen4_aleph`. Las ejecuciones de solo texto exponen relaciones de aspecto `16:9` y `9:16`. |
| Together  | Solo una imagen de referencia.                                                                                                                              |
| Vydra     | Usa `https://www.vydra.ai/api/v1` directamente para evitar redirecciones que pierden autenticación. `veo3` se empaqueta solo como texto a video; `kling` requiere una URL de imagen remota. |
| xAI       | Admite texto a video, imagen a video y flujos remotos de edición/extensión de video.                                                                       |

## Modos de capacidad del proveedor

El contrato compartido de generación de video ahora permite que los proveedores declaren
capacidades específicas por modo en lugar de solo límites agregados planos. Las nuevas
implementaciones de proveedores deberían preferir bloques de modo explícitos:

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

Los campos agregados planos como `maxInputImages` y `maxInputVideos` no son
suficientes para anunciar compatibilidad con modos de transformación. Los proveedores deben declarar
`generate`, `imageToVideo` y `videoToVideo` explícitamente para que las pruebas en vivo,
las pruebas de contrato y la herramienta compartida `video_generate` puedan validar la compatibilidad de modos
de forma determinista.

## Pruebas en vivo

Cobertura en vivo opt-in para los proveedores empaquetados compartidos:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts
```

Wrapper del repositorio:

```bash
pnpm test:live:media video
```

Este archivo en vivo carga variables de entorno faltantes de proveedores desde `~/.profile`, prioriza
por defecto las API keys en vivo/de entorno por delante de los perfiles de autenticación almacenados y ejecuta los
modos declarados que puede probar de forma segura con multimedia local:

- `generate` para cada proveedor en la barrida
- `imageToVideo` cuando `capabilities.imageToVideo.enabled`
- `videoToVideo` cuando `capabilities.videoToVideo.enabled` y el proveedor/modelo
  acepta entrada de video local respaldada por buffer en la barrida compartida

Hoy el carril compartido en vivo de `videoToVideo` cubre:

- `runway` solo cuando seleccionas `runway/gen4_aleph`

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

- [Descripción general de herramientas](/es/tools)
- [Tareas en segundo plano](/es/automation/tasks) -- seguimiento de tareas para generación asíncrona de video
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
