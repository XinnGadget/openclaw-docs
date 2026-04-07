---
read_when:
    - Necesitas depurar IDs de sesión, JSONL de transcripciones o campos de sessions.json
    - Estás cambiando el comportamiento de la compactación automática o añadiendo tareas previas a la compactación
    - Quieres implementar vaciados de memoria o turnos silenciosos del sistema
summary: 'Análisis detallado: almacén de sesiones + transcripciones, ciclo de vida e internals de la compactación (automática)'
title: Análisis detallado de la gestión de sesiones
x-i18n:
    generated_at: "2026-04-07T05:06:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: e379d624dd7808d3af25ed011079268ce6a9da64bb3f301598884ad4c46ab091
    source_path: reference/session-management-compaction.md
    workflow: 15
---

# Gestión de sesiones y compactación (análisis detallado)

Este documento explica cómo OpenClaw gestiona las sesiones de extremo a extremo:

- **Enrutamiento de sesiones** (cómo los mensajes entrantes se asignan a una `sessionKey`)
- **Almacén de sesiones** (`sessions.json`) y qué rastrea
- **Persistencia de transcripciones** (`*.jsonl`) y su estructura
- **Higiene de transcripciones** (ajustes específicos del proveedor antes de las ejecuciones)
- **Límites de contexto** (ventana de contexto frente a tokens rastreados)
- **Compactación** (compactación manual + automática) y dónde conectar trabajo previo a la compactación
- **Tareas silenciosas de mantenimiento** (por ejemplo, escrituras de memoria que no deberían producir salida visible para el usuario)

Si primero quieres una visión general de más alto nivel, empieza con:

- [/concepts/session](/es/concepts/session)
- [/concepts/compaction](/es/concepts/compaction)
- [/concepts/memory](/es/concepts/memory)
- [/concepts/memory-search](/es/concepts/memory-search)
- [/concepts/session-pruning](/es/concepts/session-pruning)
- [/reference/transcript-hygiene](/es/reference/transcript-hygiene)

---

## Fuente de verdad: el Gateway

OpenClaw está diseñado en torno a un único **proceso Gateway** que es el propietario del estado de sesión.

- Las interfaces de usuario (app de macOS, web Control UI, TUI) deben consultar al Gateway para obtener listas de sesiones y recuentos de tokens.
- En modo remoto, los archivos de sesión están en el host remoto; “comprobar tus archivos locales del Mac” no reflejará lo que está usando el Gateway.

---

## Dos capas de persistencia

OpenClaw conserva las sesiones en dos capas:

1. **Almacén de sesiones (`sessions.json`)**
   - Mapa clave/valor: `sessionKey -> SessionEntry`
   - Pequeño, mutable y seguro de editar (o eliminar entradas)
   - Rastrea metadatos de sesión (ID de sesión actual, última actividad, toggles, contadores de tokens, etc.)

2. **Transcripción (`<sessionId>.jsonl`)**
   - Transcripción append-only con estructura de árbol (las entradas tienen `id` + `parentId`)
   - Almacena la conversación real + llamadas a herramientas + resúmenes de compactación
   - Se usa para reconstruir el contexto del modelo para turnos futuros

---

## Ubicaciones en disco

Por agente, en el host del Gateway:

- Almacén: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- Transcripciones: `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Sesiones de temas de Telegram: `.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw resuelve esto mediante `src/config/sessions.ts`.

---

## Mantenimiento del almacén y controles de disco

La persistencia de sesiones tiene controles automáticos de mantenimiento (`session.maintenance`) para `sessions.json` y los artefactos de transcripción:

- `mode`: `warn` (predeterminado) o `enforce`
- `pruneAfter`: límite de antigüedad para entradas obsoletas (predeterminado `30d`)
- `maxEntries`: límite de entradas en `sessions.json` (predeterminado `500`)
- `rotateBytes`: rota `sessions.json` cuando es demasiado grande (predeterminado `10mb`)
- `resetArchiveRetention`: retención para archivos de archivo de transcripción `*.reset.<timestamp>` (predeterminado: igual que `pruneAfter`; `false` desactiva la limpieza)
- `maxDiskBytes`: presupuesto opcional para el directorio de sesiones
- `highWaterBytes`: objetivo opcional después de la limpieza (predeterminado `80%` de `maxDiskBytes`)

Orden de aplicación para la limpieza por presupuesto de disco (`mode: "enforce"`):

1. Elimina primero los artefactos de transcripción archivados u huérfanos más antiguos.
2. Si aún se supera el objetivo, expulsa las entradas de sesión más antiguas y sus archivos de transcripción.
3. Continúa hasta que el uso quede en `highWaterBytes` o por debajo.

En `mode: "warn"`, OpenClaw informa de posibles expulsiones, pero no modifica el almacén ni los archivos.

Ejecuta el mantenimiento bajo demanda:

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## Sesiones cron y registros de ejecución

Las ejecuciones cron aisladas también crean entradas de sesión/transcripciones, y tienen controles de retención dedicados:

- `cron.sessionRetention` (predeterminado `24h`) elimina sesiones antiguas de ejecuciones cron aisladas del almacén de sesiones (`false` lo desactiva).
- `cron.runLog.maxBytes` + `cron.runLog.keepLines` recortan archivos `~/.openclaw/cron/runs/<jobId>.jsonl` (predeterminados: `2_000_000` bytes y `2000` líneas).

---

## Claves de sesión (`sessionKey`)

Una `sessionKey` identifica _en qué contenedor de conversación_ estás (enrutamiento + aislamiento).

Patrones habituales:

- Chat principal/directo (por agente): `agent:<agentId>:<mainKey>` (predeterminado `main`)
- Grupo: `agent:<agentId>:<channel>:group:<id>`
- Sala/canal (Discord/Slack): `agent:<agentId>:<channel>:channel:<id>` o `...:room:<id>`
- Cron: `cron:<job.id>`
- Webhook: `hook:<uuid>` (salvo que se anule)

Las reglas canónicas están documentadas en [/concepts/session](/es/concepts/session).

---

## IDs de sesión (`sessionId`)

Cada `sessionKey` apunta a un `sessionId` actual (el archivo de transcripción que continúa la conversación).

Reglas generales:

- **Restablecer** (`/new`, `/reset`) crea un nuevo `sessionId` para esa `sessionKey`.
- **Restablecimiento diario** (predeterminado a las 4:00 AM hora local en el host del gateway) crea un nuevo `sessionId` en el siguiente mensaje después del límite de restablecimiento.
- **Caducidad por inactividad** (`session.reset.idleMinutes` o el heredado `session.idleMinutes`) crea un nuevo `sessionId` cuando llega un mensaje después de la ventana de inactividad. Cuando diario + inactividad están ambos configurados, gana el que caduque primero.
- **Protección contra bifurcación del padre del hilo** (`session.parentForkMaxTokens`, predeterminado `100000`) omite la bifurcación de la transcripción padre cuando la sesión padre ya es demasiado grande; el nuevo hilo empieza limpio. Establece `0` para desactivarlo.

Detalle de implementación: la decisión ocurre en `initSessionState()` en `src/auto-reply/reply/session.ts`.

---

## Esquema del almacén de sesiones (`sessions.json`)

El tipo de valor del almacén es `SessionEntry` en `src/config/sessions.ts`.

Campos clave (no exhaustivo):

- `sessionId`: ID actual de transcripción (el nombre de archivo se deriva de esto salvo que se configure `sessionFile`)
- `updatedAt`: marca de tiempo de la última actividad
- `sessionFile`: anulación opcional explícita de la ruta de transcripción
- `chatType`: `direct | group | room` (ayuda a las interfaces de usuario y a la política de envío)
- `provider`, `subject`, `room`, `space`, `displayName`: metadatos para etiquetado de grupo/canal
- Toggles:
  - `thinkingLevel`, `verboseLevel`, `reasoningLevel`, `elevatedLevel`
  - `sendPolicy` (anulación por sesión)
- Selección de modelo:
  - `providerOverride`, `modelOverride`, `authProfileOverride`
- Contadores de tokens (best-effort / dependientes del proveedor):
  - `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`
- `compactionCount`: cuántas veces se completó la compactación automática para esta clave de sesión
- `memoryFlushAt`: marca de tiempo del último vaciado de memoria previo a la compactación
- `memoryFlushCompactionCount`: recuento de compactación cuando se ejecutó el último vaciado

El almacén se puede editar con seguridad, pero el Gateway es la autoridad: puede reescribir o rehidratar entradas a medida que se ejecutan las sesiones.

---

## Estructura de la transcripción (`*.jsonl`)

Las transcripciones son gestionadas por `@mariozechner/pi-coding-agent` mediante `SessionManager`.

El archivo es JSONL:

- Primera línea: cabecera de sesión (`type: "session"`, incluye `id`, `cwd`, `timestamp`, `parentSession` opcional)
- Después: entradas de sesión con `id` + `parentId` (árbol)

Tipos de entrada destacados:

- `message`: mensajes de usuario/asistente/toolResult
- `custom_message`: mensajes inyectados por extensiones que _sí_ entran en el contexto del modelo (pueden ocultarse de la UI)
- `custom`: estado de extensión que _no_ entra en el contexto del modelo
- `compaction`: resumen de compactación persistido con `firstKeptEntryId` y `tokensBefore`
- `branch_summary`: resumen persistido al navegar por una rama del árbol

OpenClaw intencionadamente **no** “corrige” transcripciones; el Gateway usa `SessionManager` para leerlas/escribirlas.

---

## Ventanas de contexto frente a tokens rastreados

Importan dos conceptos distintos:

1. **Ventana de contexto del modelo**: límite estricto por modelo (tokens visibles para el modelo)
2. **Contadores del almacén de sesiones**: estadísticas acumuladas escritas en `sessions.json` (usadas para /status y paneles)

Si estás ajustando límites:

- La ventana de contexto viene del catálogo de modelos (y puede anularse mediante configuración).
- `contextTokens` en el almacén es un valor de estimación/informe en tiempo de ejecución; no lo trates como una garantía estricta.

Para más información, consulta [/token-use](/es/reference/token-use).

---

## Compactación: qué es

La compactación resume la conversación antigua en una entrada `compaction` persistida en la transcripción y mantiene intactos los mensajes recientes.

Después de la compactación, los turnos futuros ven:

- El resumen de compactación
- Los mensajes posteriores a `firstKeptEntryId`

La compactación es **persistente** (a diferencia de la poda de sesiones). Consulta [/concepts/session-pruning](/es/concepts/session-pruning).

## Límites de bloques de compactación y emparejamiento de herramientas

Cuando OpenClaw divide una transcripción larga en bloques de compactación, mantiene
emparejadas las llamadas a herramientas del asistente con sus entradas `toolResult` correspondientes.

- Si la división por proporción de tokens cae entre una llamada a herramienta y su resultado, OpenClaw
  desplaza el límite al mensaje de llamada a herramienta del asistente en lugar de separar
  la pareja.
- Si un bloque final de resultado de herramienta hiciera que el bloque superara el objetivo,
  OpenClaw conserva ese bloque de herramienta pendiente y mantiene intacta la cola no resumida.
- Los bloques abortados/con error de llamada a herramienta no mantienen abierta una división pendiente.

---

## Cuándo ocurre la compactación automática (tiempo de ejecución de Pi)

En el agente Pi integrado, la compactación automática se activa en dos casos:

1. **Recuperación por desbordamiento**: el modelo devuelve un error de desbordamiento de contexto
   (`request_too_large`, `context length exceeded`, `input exceeds the maximum
number of tokens`, `input token count exceeds the maximum number of input
tokens`, `input is too long for the model`, `ollama error: context length
exceeded` y variantes similares con forma específica del proveedor) → compactar → reintentar.
2. **Mantenimiento por umbral**: después de un turno correcto, cuando:

`contextTokens > contextWindow - reserveTokens`

Donde:

- `contextWindow` es la ventana de contexto del modelo
- `reserveTokens` es el margen reservado para prompts + la siguiente salida del modelo

Estas son semánticas del tiempo de ejecución de Pi (OpenClaw consume los eventos, pero Pi decide cuándo compactar).

---

## Ajustes de compactación (`reserveTokens`, `keepRecentTokens`)

Los ajustes de compactación de Pi viven en la configuración de Pi:

```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,
    keepRecentTokens: 20000,
  },
}
```

OpenClaw también aplica un umbral mínimo de seguridad para ejecuciones integradas:

- Si `compaction.reserveTokens < reserveTokensFloor`, OpenClaw lo aumenta.
- El umbral mínimo predeterminado es `20000` tokens.
- Establece `agents.defaults.compaction.reserveTokensFloor: 0` para desactivar el umbral.
- Si ya es mayor, OpenClaw lo deja igual.

Por qué: dejar suficiente margen para “tareas de mantenimiento” de varios turnos (como escrituras de memoria) antes de que la compactación sea inevitable.

Implementación: `ensurePiCompactionReserveTokens()` en `src/agents/pi-settings.ts`
(llamado desde `src/agents/pi-embedded-runner.ts`).

---

## Superficies visibles para el usuario

Puedes observar la compactación y el estado de la sesión mediante:

- `/status` (en cualquier sesión de chat)
- `openclaw status` (CLI)
- `openclaw sessions` / `sessions --json`
- Modo detallado: `🧹 Auto-compaction complete` + recuento de compactación

---

## Tareas silenciosas de mantenimiento (`NO_REPLY`)

OpenClaw admite turnos “silenciosos” para tareas en segundo plano donde el usuario no debería ver salida intermedia.

Convención:

- El asistente empieza su salida con el token silencioso exacto `NO_REPLY` /
  `no_reply` para indicar “no entregar una respuesta al usuario”.
- OpenClaw elimina/suprime esto en la capa de entrega.
- La supresión del token silencioso exacto no distingue entre mayúsculas y minúsculas, por lo que `NO_REPLY` y
  `no_reply` cuentan cuando toda la carga útil es solo el token silencioso.
- Esto es solo para turnos realmente en segundo plano/sin entrega; no es un atajo para
  solicitudes normales del usuario que requieran acción.

A partir de `2026.1.10`, OpenClaw también suprime el **streaming de borrador/escritura** cuando un
fragmento parcial comienza con `NO_REPLY`, para que las operaciones silenciosas no filtren salida parcial a mitad del turno.

---

## “Vaciado de memoria” previo a la compactación (implementado)

Objetivo: antes de que ocurra la compactación automática, ejecutar un turno agentico silencioso que escriba
estado duradero en disco (por ejemplo, `memory/YYYY-MM-DD.md` en el espacio de trabajo del agente) para que la compactación no pueda
borrar contexto crítico.

OpenClaw usa el enfoque de **vaciado previo al umbral**:

1. Supervisar el uso del contexto de la sesión.
2. Cuando cruza un “umbral suave” (por debajo del umbral de compactación de Pi), ejecutar una directiva silenciosa
   de “escribe memoria ahora” para el agente.
3. Usar el token silencioso exacto `NO_REPLY` / `no_reply` para que el usuario no vea
   nada.

Configuración (`agents.defaults.compaction.memoryFlush`):

- `enabled` (predeterminado: `true`)
- `softThresholdTokens` (predeterminado: `4000`)
- `prompt` (mensaje del usuario para el turno de vaciado)
- `systemPrompt` (prompt del sistema adicional añadido para el turno de vaciado)

Notas:

- El prompt/prompt del sistema predeterminados incluyen una pista `NO_REPLY` para suprimir
  la entrega.
- El vaciado se ejecuta una vez por ciclo de compactación (rastreado en `sessions.json`).
- El vaciado solo se ejecuta para sesiones Pi integradas (los backends CLI lo omiten).
- El vaciado se omite cuando el espacio de trabajo de la sesión es de solo lectura (`workspaceAccess: "ro"` o `"none"`).
- Consulta [Memoria](/es/concepts/memory) para ver el diseño de archivos del espacio de trabajo y los patrones de escritura.

Pi también expone un hook `session_before_compact` en la API de extensiones, pero la lógica de
vaciado de OpenClaw vive actualmente del lado del Gateway.

---

## Lista de comprobación para solución de problemas

- ¿La clave de sesión es incorrecta? Empieza por [/concepts/session](/es/concepts/session) y confirma la `sessionKey` en `/status`.
- ¿No coincide el almacén con la transcripción? Confirma el host del Gateway y la ruta del almacén desde `openclaw status`.
- ¿Compactación excesiva? Comprueba:
  - la ventana de contexto del modelo (demasiado pequeña)
  - los ajustes de compactación (`reserveTokens` demasiado alto para la ventana del modelo puede provocar una compactación más temprana)
  - el crecimiento por `toolResult`: habilita/ajusta la poda de sesiones
- ¿Se filtran turnos silenciosos? Confirma que la respuesta empieza con `NO_REPLY` (token exacto sin distinguir mayúsculas/minúsculas) y que estás en una compilación que incluye la corrección de supresión de streaming.
