---
read_when:
    - Generar música o audio mediante el agente
    - Configurar proveedores y modelos de generación de música
    - Entender los parámetros de la herramienta music_generate
summary: Genera música con proveedores compartidos, incluidos plugins basados en flujos de trabajo
title: Generación de música
x-i18n:
    generated_at: "2026-04-07T05:07:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: ce8da8dfc188efe8593ca5cbec0927dd1d18d2861a1a828df89c8541ccf1cb25
    source_path: tools/music-generation.md
    workflow: 15
---

# Generación de música

La herramienta `music_generate` permite al agente crear música o audio mediante la
capacidad compartida de generación de música con proveedores configurados como Google,
MiniMax y ComfyUI configurado mediante flujos de trabajo.

Para sesiones de agente respaldadas por proveedores compartidos, OpenClaw inicia la generación de música como una
tarea en segundo plano, la rastrea en el registro de tareas y luego vuelve a activar al agente cuando la pista está lista para que el agente pueda publicar el audio terminado de nuevo en el
canal original.

<Note>
La herramienta compartida integrada solo aparece cuando hay al menos un proveedor de generación de música disponible. Si no ves `music_generate` en las herramientas de tu agente, configura `agents.defaults.musicGenerationModel` o establece una clave de API del proveedor.
</Note>

## Inicio rápido

### Generación respaldada por proveedores compartidos

1. Establece una clave de API para al menos un proveedor, por ejemplo `GEMINI_API_KEY` o
   `MINIMAX_API_KEY`.
2. Opcionalmente establece tu modelo preferido:

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

3. Pídele al agente: _"Genera una pista synthpop animada sobre un viaje nocturno
   por una ciudad de neón."_

El agente llama a `music_generate` automáticamente. No hace falta lista de permitidos de herramientas.

Para contextos síncronos directos sin una ejecución de agente respaldada por sesión, la
herramienta integrada sigue recurriendo a la generación en línea y devuelve la ruta final del contenido multimedia en
el resultado de la herramienta.

Prompts de ejemplo:

```text
Genera una pista cinematográfica de piano con cuerdas suaves y sin voces.
```

```text
Genera un loop chiptune enérgico sobre el lanzamiento de un cohete al amanecer.
```

### Generación con Comfy basada en flujos de trabajo

El plugin integrado `comfy` se conecta a la herramienta compartida `music_generate` a través del
registro de proveedores de generación de música.

1. Configura `models.providers.comfy.music` con un JSON de flujo de trabajo y
   nodos de prompt/salida.
2. Si usas Comfy Cloud, establece `COMFY_API_KEY` o `COMFY_CLOUD_API_KEY`.
3. Pide al agente música o llama a la herramienta directamente.

Ejemplo:

```text
/tool music_generate prompt="Loop synth ambiental cálido con suave textura de cinta"
```

## Compatibilidad compartida de proveedores integrados

| Provider | Default model          | Reference inputs | Supported controls                                        | API key                                |
| -------- | ---------------------- | ---------------- | --------------------------------------------------------- | -------------------------------------- |
| ComfyUI  | `workflow`             | Hasta 1 imagen   | Música o audio definidos por el flujo de trabajo          | `COMFY_API_KEY`, `COMFY_CLOUD_API_KEY` |
| Google   | `lyria-3-clip-preview` | Hasta 10 imágenes | `lyrics`, `instrumental`, `format`                        | `GEMINI_API_KEY`, `GOOGLE_API_KEY`     |
| MiniMax  | `music-2.5+`           | Ninguno          | `lyrics`, `instrumental`, `durationSeconds`, `format=mp3` | `MINIMAX_API_KEY`                      |

### Matriz de capacidades declaradas

Este es el contrato de modos explícito que usan `music_generate`, las pruebas de contratos
y la pasada live compartida.

| Provider | `generate` | `edit` | Límite de edición | Lanes live compartidos                                                     |
| -------- | ---------- | ------ | ----------------- | -------------------------------------------------------------------------- |
| ComfyUI  | Sí         | Sí     | 1 imagen          | No está en la pasada compartida; cubierto por `extensions/comfy/comfy.live.test.ts` |
| Google   | Sí         | Sí     | 10 imágenes       | `generate`, `edit`                                                         |
| MiniMax  | Sí         | No     | Ninguno           | `generate`                                                                 |

Usa `action: "list"` para inspeccionar los proveedores y modelos compartidos disponibles en
tiempo de ejecución:

```text
/tool music_generate action=list
```

Usa `action: "status"` para inspeccionar la tarea de música activa respaldada por sesión:

```text
/tool music_generate action=status
```

Ejemplo de generación directa:

```text
/tool music_generate prompt="Lo-fi hip hop onírico con textura de vinilo y lluvia suave" instrumental=true
```

## Parámetros de la herramienta integrada

| Parameter         | Type     | Description                                                                                       |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------- |
| `prompt`          | string   | Prompt de generación de música (obligatorio para `action: "generate"`)                           |
| `action`          | string   | `"generate"` (predeterminado), `"status"` para la tarea actual de la sesión o `"list"` para inspeccionar proveedores |
| `model`           | string   | Anulación de proveedor/modelo, por ejemplo `google/lyria-3-pro-preview` o `comfy/workflow`       |
| `lyrics`          | string   | Letra opcional cuando el proveedor admite entrada explícita de letras                            |
| `instrumental`    | boolean  | Solicita salida solo instrumental cuando el proveedor lo admite                                  |
| `image`           | string   | Ruta o URL de una sola imagen de referencia                                                      |
| `images`          | string[] | Varias imágenes de referencia (hasta 10)                                                         |
| `durationSeconds` | number   | Duración objetivo en segundos cuando el proveedor admite sugerencias de duración                 |
| `format`          | string   | Sugerencia de formato de salida (`mp3` o `wav`) cuando el proveedor lo admite                    |
| `filename`        | string   | Sugerencia de nombre de archivo                                                                  |

No todos los proveedores admiten todos los parámetros. OpenClaw sigue validando límites estrictos
como los recuentos de entradas antes del envío. Cuando un proveedor admite duración pero
usa un máximo más corto que el valor solicitado, OpenClaw ajusta automáticamente
al valor compatible más cercano. Las sugerencias opcionales realmente no compatibles se ignoran
con una advertencia cuando el proveedor o modelo seleccionado no puede respetarlas.

Los resultados de la herramienta informan de los ajustes aplicados. Cuando OpenClaw ajusta la duración durante el cambio automático de proveedor, el `durationSeconds` devuelto refleja el valor enviado y `details.normalization.durationSeconds` muestra la correspondencia entre el valor solicitado y el aplicado.

## Comportamiento asíncrono para la ruta respaldada por proveedores compartidos

- Ejecuciones de agente respaldadas por sesión: `music_generate` crea una tarea en segundo plano, devuelve inmediatamente una respuesta de inicio/tarea y publica la pista terminada más tarde en un mensaje de seguimiento del agente.
- Prevención de duplicados: mientras esa tarea en segundo plano siga en estado `queued` o `running`, las llamadas posteriores a `music_generate` en la misma sesión devuelven el estado de la tarea en lugar de iniciar otra generación.
- Consulta de estado: usa `action: "status"` para inspeccionar la tarea de música activa respaldada por sesión sin iniciar una nueva.
- Seguimiento de tareas: usa `openclaw tasks list` o `openclaw tasks show <taskId>` para inspeccionar el estado en cola, en ejecución y final de la generación.
- Activación al completarse: OpenClaw inyecta un evento interno de finalización en la misma sesión para que el modelo pueda escribir por sí mismo el mensaje de seguimiento orientado al usuario.
- Pista para el prompt: los turnos posteriores del usuario/manuales en la misma sesión reciben una pequeña pista en tiempo de ejecución cuando ya hay una tarea musical en curso para que el modelo no llame ciegamente a `music_generate` de nuevo.
- Respaldo sin sesión: los contextos directos/locales sin una sesión real del agente siguen ejecutándose en línea y devuelven el resultado final del audio en el mismo turno.

### Ciclo de vida de la tarea

Cada solicitud `music_generate` pasa por cuatro estados:

1. **queued** -- tarea creada, esperando a que el proveedor la acepte.
2. **running** -- el proveedor está procesando (normalmente de 30 segundos a 3 minutos según el proveedor y la duración).
3. **succeeded** -- pista lista; el agente se activa y la publica en la conversación.
4. **failed** -- error o timeout del proveedor; el agente se activa con detalles del error.

Comprueba el estado desde la CLI:

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

Prevención de duplicados: si ya hay una tarea musical en estado `queued` o `running` para la sesión actual, `music_generate` devuelve el estado de la tarea existente en lugar de iniciar una nueva. Usa `action: "status"` para comprobarlo explícitamente sin activar una nueva generación.

## Configuración

### Selección de modelo

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
        fallbacks: ["minimax/music-2.5+"],
      },
    },
  },
}
```

### Orden de selección de proveedor

Al generar música, OpenClaw prueba los proveedores en este orden:

1. El parámetro `model` de la llamada a la herramienta, si el agente especifica uno
2. `musicGenerationModel.primary` de la configuración
3. `musicGenerationModel.fallbacks` en orden
4. Detección automática usando solo valores predeterminados de proveedores respaldados por autenticación:
   - primero el proveedor predeterminado actual
   - los proveedores de generación de música registrados restantes en orden de ID de proveedor

Si un proveedor falla, se prueba automáticamente el siguiente candidato. Si todos fallan, el
error incluye detalles de cada intento.

Establece `agents.defaults.mediaGenerationAutoProviderFallback: false` si quieres que la
generación de música use solo las entradas explícitas `model`, `primary` y `fallbacks`.

## Notas sobre proveedores

- Google usa generación por lotes de Lyria 3. El flujo integrado actual admite
  prompt, texto opcional de letras e imágenes de referencia opcionales.
- MiniMax usa el endpoint por lotes `music_generation`. El flujo integrado actual
  admite prompt, letras opcionales, modo instrumental, ajuste de duración y
  salida mp3.
- La compatibilidad con ComfyUI está controlada por flujos de trabajo y depende del grafo configurado más
  la asignación de nodos para campos de prompt/salida.

## Modos de capacidad del proveedor

El contrato compartido de generación de música ahora admite declaraciones explícitas de modos:

- `generate` para generación solo con prompt
- `edit` cuando la solicitud incluye una o más imágenes de referencia

Las nuevas implementaciones de proveedores deberían preferir bloques de modo explícitos:

```typescript
capabilities: {
  generate: {
    maxTracks: 1,
    supportsLyrics: true,
    supportsFormat: true,
  },
  edit: {
    enabled: true,
    maxTracks: 1,
    maxInputImages: 1,
    supportsFormat: true,
  },
}
```

Los campos planos heredados como `maxInputImages`, `supportsLyrics` y
`supportsFormat` no bastan para anunciar compatibilidad con edición. Los proveedores deberían
declarar `generate` y `edit` explícitamente para que las pruebas live, las pruebas de contratos y
la herramienta compartida `music_generate` puedan validar la compatibilidad de modos de manera determinista.

## Elegir la ruta correcta

- Usa la ruta compartida respaldada por proveedores cuando quieras selección de modelo, cambio de proveedor por error y el flujo integrado de tarea/estado asíncrono.
- Usa una ruta de plugin como ComfyUI cuando necesites un grafo de flujo de trabajo personalizado o un proveedor que no forme parte de la capacidad musical compartida integrada.
- Si estás depurando un comportamiento específico de ComfyUI, consulta [ComfyUI](/es/providers/comfy). Si estás depurando un comportamiento compartido de proveedores, empieza por [Google (Gemini)](/es/providers/google) o [MiniMax](/es/providers/minimax).

## Pruebas live

Cobertura live opcional para los proveedores integrados compartidos:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts
```

Envoltorio del repositorio:

```bash
pnpm test:live:media music
```

Este archivo live carga las variables de entorno de proveedor que falten desde `~/.profile`, prioriza
por defecto las claves de API live/de entorno por delante de los perfiles de autenticación almacenados y ejecuta cobertura tanto de
`generate` como de `edit` declarado cuando el proveedor habilita el modo de edición.

Hoy eso significa:

- `google`: `generate` más `edit`
- `minimax`: solo `generate`
- `comfy`: cobertura live de Comfy separada, no en la pasada de proveedores compartidos

Cobertura live opcional para la ruta musical integrada de ComfyUI:

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

El archivo live de Comfy también cubre flujos de trabajo de imagen y video de comfy cuando esas
secciones están configuradas.

## Relacionado

- [Background Tasks](/es/automation/tasks) - seguimiento de tareas para ejecuciones desacopladas de `music_generate`
- [Configuration Reference](/es/gateway/configuration-reference#agent-defaults) - configuración de `musicGenerationModel`
- [ComfyUI](/es/providers/comfy)
- [Google (Gemini)](/es/providers/google)
- [MiniMax](/es/providers/minimax)
- [Models](/es/concepts/models) - configuración de modelos y cambio por error
- [Tools Overview](/es/tools)
