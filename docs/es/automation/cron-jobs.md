---
read_when:
    - Programación de tareas en segundo plano o activaciones
    - Conexión de desencadenadores externos (webhooks, Gmail) a OpenClaw
    - Decidir entre heartbeat y cron para las tareas programadas
summary: Trabajos programados, webhooks y desencadenadores de PubSub de Gmail para el programador del Gateway
title: Tareas programadas
x-i18n:
    generated_at: "2026-04-11T02:44:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 04d94baa152de17d78515f7d545f099fe4810363ab67e06b465e489737f54665
    source_path: automation/cron-jobs.md
    workflow: 15
---

# Tareas programadas (Cron)

Cron es el programador integrado del Gateway. Conserva los trabajos, activa al agente en el momento adecuado y puede devolver la salida a un canal de chat o a un endpoint de webhook.

## Inicio rápido

```bash
# Add a one-shot reminder
openclaw cron add \
  --name "Reminder" \
  --at "2026-02-01T16:00:00Z" \
  --session main \
  --system-event "Reminder: check the cron docs draft" \
  --wake now \
  --delete-after-run

# Check your jobs
openclaw cron list

# See run history
openclaw cron runs --id <job-id>
```

## Cómo funciona cron

- Cron se ejecuta **dentro del proceso Gateway** (no dentro del modelo).
- Los trabajos se conservan en `~/.openclaw/cron/jobs.json`, por lo que los reinicios no hacen perder la programación.
- Todas las ejecuciones de cron crean registros de [tarea en segundo plano](/es/automation/tasks).
- Los trabajos de una sola ejecución (`--at`) se eliminan automáticamente después de completarse con éxito de forma predeterminada.
- Las ejecuciones aisladas de cron intentan cerrar, en la medida de lo posible, las pestañas/procesos del navegador rastreados para su sesión `cron:<jobId>` cuando la ejecución termina, para que la automatización desacoplada del navegador no deje procesos huérfanos.
- Las ejecuciones aisladas de cron también protegen contra respuestas de confirmación obsoletas. Si el primer resultado es solo una actualización de estado provisional (`on it`, `pulling everything together` y pistas similares) y ninguna ejecución descendiente de subagente sigue siendo responsable de la respuesta final, OpenClaw vuelve a hacer un prompt una vez para obtener el resultado real antes de entregarlo.

<a id="maintenance"></a>

La reconciliación de tareas para cron es propiedad del runtime: una tarea de cron activa sigue viva mientras el runtime de cron siga rastreando ese trabajo como en ejecución, incluso si todavía existe una fila antigua de sesión hija.
Una vez que el runtime deja de ser propietario del trabajo y expira el período de gracia de 5 minutos, el mantenimiento puede marcar la tarea como `lost`.

## Tipos de programación

| Tipo    | Indicador CLI | Descripción                                                   |
| ------- | ------------- | ------------------------------------------------------------- |
| `at`    | `--at`        | Marca de tiempo de una sola ejecución (ISO 8601 o relativa como `20m`) |
| `every` | `--every`     | Intervalo fijo                                                |
| `cron`  | `--cron`      | Expresión cron de 5 o 6 campos con `--tz` opcional            |

Las marcas de tiempo sin zona horaria se tratan como UTC. Agrega `--tz America/New_York` para programación según la hora local.

Las expresiones recurrentes al inicio de cada hora se escalonan automáticamente hasta 5 minutos para reducir picos de carga. Usa `--exact` para forzar una sincronización precisa o `--stagger 30s` para una ventana explícita.

## Estilos de ejecución

| Estilo          | valor de `--session` | Se ejecuta en            | Ideal para                     |
| --------------- | -------------------- | ------------------------ | ------------------------------ |
| Sesión principal | `main`              | Siguiente turno de heartbeat | Recordatorios, eventos del sistema |
| Aislado         | `isolated`           | `cron:<jobId>` dedicado  | Informes, tareas en segundo plano |
| Sesión actual   | `current`            | Vinculado en el momento de la creación | Trabajo recurrente con contexto |
| Sesión personalizada | `session:custom-id` | Sesión nombrada persistente | Flujos de trabajo que se basan en el historial |

Los trabajos de **sesión principal** ponen en cola un evento del sistema y, opcionalmente, activan el heartbeat (`--wake now` o `--wake next-heartbeat`). Los trabajos **aislados** ejecutan un turno de agente dedicado con una sesión nueva. Las **sesiones personalizadas** (`session:xxx`) conservan el contexto entre ejecuciones, lo que permite flujos de trabajo como reuniones diarias que se basan en resúmenes anteriores.

Para los trabajos aislados, el desmontaje del runtime ahora incluye una limpieza del navegador para esa sesión de cron en la medida de lo posible. Los fallos de limpieza se ignoran para que el resultado real de cron siga teniendo prioridad.

Cuando las ejecuciones aisladas de cron orquestan subagentes, la entrega también prioriza la salida final descendiente sobre el texto provisional obsoleto del padre. Si los descendientes todavía se están ejecutando, OpenClaw suprime esa actualización parcial del padre en lugar de anunciarla.

### Opciones de payload para trabajos aislados

- `--message`: texto del prompt (obligatorio para aislado)
- `--model` / `--thinking`: anulaciones del modelo y del nivel de razonamiento
- `--light-context`: omite la inyección de archivos de arranque del espacio de trabajo
- `--tools exec,read`: restringe qué herramientas puede usar el trabajo

`--model` usa el modelo permitido seleccionado para ese trabajo. Si el modelo solicitado no está permitido, cron registra una advertencia y vuelve a la selección de modelo predeterminada o del agente del trabajo. Las cadenas de fallback configuradas siguen aplicándose, pero una simple anulación de modelo sin una lista explícita de fallback por trabajo ya no agrega el primario del agente como un objetivo extra de reintento oculto.

La precedencia de selección de modelo para trabajos aislados es:

1. Anulación de modelo del hook de Gmail (cuando la ejecución vino de Gmail y esa anulación está permitida)
2. `model` del payload por trabajo
3. Anulación de modelo conservada en la sesión de cron
4. Selección de modelo predeterminada o del agente

El modo rápido también sigue la selección activa resuelta. Si la configuración del modelo seleccionado tiene `params.fastMode`, el cron aislado lo usa de forma predeterminada. Una anulación almacenada de `fastMode` en la sesión sigue teniendo prioridad sobre la configuración en cualquier dirección.

Si una ejecución aislada encuentra una transferencia activa de cambio de modelo, cron vuelve a intentar con el proveedor/modelo cambiado y conserva esa selección activa antes de reintentar. Cuando el cambio también incluye un nuevo perfil de autenticación, cron también conserva esa anulación del perfil de autenticación. Los reintentos están limitados: después del intento inicial más 2 reintentos por cambio, cron aborta en lugar de entrar en un bucle infinito.

## Entrega y salida

| Modo      | Qué sucede                                                  |
| --------- | ----------------------------------------------------------- |
| `announce` | Entrega un resumen al canal de destino (predeterminado para aislado) |
| `webhook`  | Envía por POST el payload del evento finalizado a una URL   |
| `none`     | Solo interno, sin entrega                                   |

Usa `--announce --channel telegram --to "-1001234567890"` para entrega al canal. Para temas de foros de Telegram, usa `-1001234567890:topic:123`. Los destinos de Slack/Discord/Mattermost deben usar prefijos explícitos (`channel:<id>`, `user:<id>`).

Para trabajos aislados propiedad de cron, el ejecutor es propietario de la ruta de entrega final. Al agente se le pide que devuelva un resumen en texto plano, y luego ese resumen se envía mediante `announce`, `webhook` o se conserva internamente para `none`. `--no-deliver` no devuelve la entrega al agente; mantiene la ejecución como interna.

Si la tarea original indica explícitamente que se debe enviar un mensaje a algún destinatario externo, el agente debe indicar quién/dónde debe recibir ese mensaje en su salida en lugar de intentar enviarlo directamente.

Las notificaciones de fallo siguen una ruta de destino separada:

- `cron.failureDestination` establece un valor predeterminado global para las notificaciones de fallo.
- `job.delivery.failureDestination` lo anula por trabajo.
- Si ninguno está configurado y el trabajo ya entrega mediante `announce`, las notificaciones de fallo ahora recurren a ese destino principal de anuncio.
- `delivery.failureDestination` solo es compatible con trabajos `sessionTarget="isolated"` a menos que el modo principal de entrega sea `webhook`.

## Ejemplos de CLI

Recordatorio de una sola ejecución (sesión principal):

```bash
openclaw cron add \
  --name "Calendar check" \
  --at "20m" \
  --session main \
  --system-event "Next heartbeat: check calendar." \
  --wake now
```

Trabajo recurrente aislado con entrega:

```bash
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize overnight updates." \
  --announce \
  --channel slack \
  --to "channel:C1234567890"
```

Trabajo aislado con anulación de modelo y razonamiento:

```bash
openclaw cron add \
  --name "Deep analysis" \
  --cron "0 6 * * 1" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Weekly deep analysis of project progress." \
  --model "opus" \
  --thinking high \
  --announce
```

## Webhooks

Gateway puede exponer endpoints HTTP de webhook para desencadenadores externos. Habilítalos en la configuración:

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
  },
}
```

### Autenticación

Cada solicitud debe incluir el token del hook mediante un encabezado:

- `Authorization: Bearer <token>` (recomendado)
- `x-openclaw-token: <token>`

Los tokens en la cadena de consulta se rechazan.

### POST /hooks/wake

Pone en cola un evento del sistema para la sesión principal:

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"text":"New email received","mode":"now"}'
```

- `text` (obligatorio): descripción del evento
- `mode` (opcional): `now` (predeterminado) o `next-heartbeat`

### POST /hooks/agent

Ejecuta un turno de agente aislado:

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","model":"openai/gpt-5.4-mini"}'
```

Campos: `message` (obligatorio), `name`, `agentId`, `wakeMode`, `deliver`, `channel`, `to`, `model`, `thinking`, `timeoutSeconds`.

### Hooks mapeados (POST /hooks/\<name\>)

Los nombres de hook personalizados se resuelven mediante `hooks.mappings` en la configuración. Los mapeos pueden transformar payloads arbitrarios en acciones `wake` o `agent` con plantillas o transformaciones de código.

### Seguridad

- Mantén los endpoints de hook detrás de loopback, tailnet o un proxy inverso de confianza.
- Usa un token de hook dedicado; no reutilices tokens de autenticación del gateway.
- Mantén `hooks.path` en una subruta dedicada; `/` se rechaza.
- Configura `hooks.allowedAgentIds` para limitar el enrutamiento explícito de `agentId`.
- Mantén `hooks.allowRequestSessionKey=false` a menos que necesites sesiones seleccionadas por quien llama.
- Si habilitas `hooks.allowRequestSessionKey`, también configura `hooks.allowedSessionKeyPrefixes` para restringir las formas permitidas de la clave de sesión.
- Los payloads del hook se encapsulan con límites de seguridad de forma predeterminada.

## Integración de Gmail PubSub

Conecta los desencadenadores del buzón de Gmail a OpenClaw mediante Google PubSub.

**Requisitos previos**: CLI de `gcloud`, `gog` (gogcli), hooks de OpenClaw habilitados, Tailscale para el endpoint HTTPS público.

### Configuración con asistente (recomendada)

```bash
openclaw webhooks gmail setup --account openclaw@gmail.com
```

Esto escribe la configuración `hooks.gmail`, habilita el ajuste preestablecido de Gmail y usa Tailscale Funnel para el endpoint push.

### Inicio automático del Gateway

Cuando `hooks.enabled=true` y `hooks.gmail.account` está configurado, el Gateway inicia `gog gmail watch serve` al arrancar y renueva automáticamente la suscripción de watch. Configura `OPENCLAW_SKIP_GMAIL_WATCHER=1` para excluirte.

### Configuración manual de una sola vez

1. Selecciona el proyecto de GCP que es propietario del cliente OAuth usado por `gog`:

```bash
gcloud auth login
gcloud config set project <project-id>
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

2. Crea el tema y otorga a Gmail acceso de push:

```bash
gcloud pubsub topics create gog-gmail-watch
gcloud pubsub topics add-iam-policy-binding gog-gmail-watch \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
```

3. Inicia la suscripción de watch:

```bash
gog gmail watch start \
  --account openclaw@gmail.com \
  --label INBOX \
  --topic projects/<project-id>/topics/gog-gmail-watch
```

### Anulación de modelo de Gmail

```json5
{
  hooks: {
    gmail: {
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

## Gestión de trabajos

```bash
# List all jobs
openclaw cron list

# Edit a job
openclaw cron edit <jobId> --message "Updated prompt" --model "opus"

# Force run a job now
openclaw cron run <jobId>

# Run only if due
openclaw cron run <jobId> --due

# View run history
openclaw cron runs --id <jobId> --limit 50

# Delete a job
openclaw cron remove <jobId>

# Agent selection (multi-agent setups)
openclaw cron add --name "Ops sweep" --cron "0 6 * * *" --session isolated --message "Check ops queue" --agent ops
openclaw cron edit <jobId> --clear-agent
```

Nota sobre la anulación de modelo:

- `openclaw cron add|edit --model ...` cambia el modelo seleccionado del trabajo.
- Si el modelo está permitido, ese proveedor/modelo exacto llega a la ejecución aislada del agente.
- Si no está permitido, cron muestra una advertencia y vuelve a la selección de modelo predeterminada o del agente del trabajo.
- Las cadenas de fallback configuradas siguen aplicándose, pero una simple anulación con `--model` sin una lista explícita de fallback por trabajo ya no recurre al primario del agente como un objetivo adicional de reintento silencioso.

## Configuración

```json5
{
  cron: {
    enabled: true,
    store: "~/.openclaw/cron/jobs.json",
    maxConcurrentRuns: 1,
    retry: {
      maxAttempts: 3,
      backoffMs: [60000, 120000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "server_error"],
    },
    webhookToken: "replace-with-dedicated-webhook-token",
    sessionRetention: "24h",
    runLog: { maxBytes: "2mb", keepLines: 2000 },
  },
}
```

Desactiva cron: `cron.enabled: false` o `OPENCLAW_SKIP_CRON=1`.

**Reintento de una sola ejecución**: los errores transitorios (límite de tasa, sobrecarga, red, error del servidor) se reintentan hasta 3 veces con backoff exponencial. Los errores permanentes se desactivan de inmediato.

**Reintento recurrente**: backoff exponencial (de 30s a 60m) entre reintentos. El backoff se restablece después de la siguiente ejecución correcta.

**Mantenimiento**: `cron.sessionRetention` (predeterminado `24h`) elimina las entradas de sesión de ejecuciones aisladas. `cron.runLog.maxBytes` / `cron.runLog.keepLines` eliminan automáticamente los archivos de registro de ejecución.

## Solución de problemas

### Escalera de comandos

```bash
openclaw status
openclaw gateway status
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
openclaw doctor
```

### Cron no se activa

- Comprueba `cron.enabled` y la variable de entorno `OPENCLAW_SKIP_CRON`.
- Confirma que el Gateway se esté ejecutando de forma continua.
- Para programaciones `cron`, verifica la zona horaria (`--tz`) frente a la zona horaria del host.
- `reason: not-due` en la salida de ejecución significa que la ejecución manual se comprobó con `openclaw cron run <jobId> --due` y que el trabajo aún no vencía.

### Cron se activó pero no hubo entrega

- El modo de entrega `none` significa que no se espera ningún mensaje externo.
- Un destino de entrega faltante o no válido (`channel`/`to`) significa que la salida se omitió.
- Los errores de autenticación del canal (`unauthorized`, `Forbidden`) significan que la entrega fue bloqueada por las credenciales.
- Si la ejecución aislada devuelve solo el token silencioso (`NO_REPLY` / `no_reply`), OpenClaw suprime la entrega directa saliente y también suprime la ruta de resumen en cola de fallback, por lo que no se publica nada de vuelta en el chat.
- Para los trabajos aislados propiedad de cron, no esperes que el agente use la herramienta de mensajes como fallback. El ejecutor es propietario de la entrega final; `--no-deliver` la mantiene interna en lugar de permitir un envío directo.

### Consideraciones sobre la zona horaria

- Cron sin `--tz` usa la zona horaria del host del gateway.
- Las programaciones `at` sin zona horaria se tratan como UTC.
- `activeHours` de heartbeat usa la resolución de zona horaria configurada.

## Relacionado

- [Automatización y tareas](/es/automation) — todos los mecanismos de automatización de un vistazo
- [Tareas en segundo plano](/es/automation/tasks) — registro de tareas para ejecuciones de cron
- [Heartbeat](/es/gateway/heartbeat) — turnos periódicos de la sesión principal
- [Zona horaria](/es/concepts/timezone) — configuración de la zona horaria
