---
read_when:
    - Quieres activar o controlar TaskFlows desde un sistema externo
    - Estás configurando el plugin Webhooks incluido
summary: 'Plugin Webhooks: ingreso autenticado de TaskFlow para automatización externa de confianza'
title: Plugin Webhooks
x-i18n:
    generated_at: "2026-04-07T05:05:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5da12a887752ec6ee853cfdb912db0ae28512a0ffed06fe3828ef2eee15bc9d
    source_path: plugins/webhooks.md
    workflow: 15
---

# Webhooks (plugin)

El plugin Webhooks añade rutas HTTP autenticadas que vinculan la
automatización externa con los TaskFlows de OpenClaw.

Úsalo cuando quieras que un sistema de confianza, como Zapier, n8n, un trabajo de CI o un
servicio interno, cree y controle TaskFlows gestionados sin tener que escribir primero un
plugin personalizado.

## Dónde se ejecuta

El plugin Webhooks se ejecuta dentro del proceso Gateway.

Si tu Gateway se ejecuta en otra máquina, instala y configura el plugin en
ese host del Gateway y luego reinicia el Gateway.

## Configurar rutas

Establece la configuración en `plugins.entries.webhooks.config`:

```json5
{
  plugins: {
    entries: {
      webhooks: {
        enabled: true,
        config: {
          routes: {
            zapier: {
              path: "/plugins/webhooks/zapier",
              sessionKey: "agent:main:main",
              secret: {
                source: "env",
                provider: "default",
                id: "OPENCLAW_WEBHOOK_SECRET",
              },
              controllerId: "webhooks/zapier",
              description: "Puente TaskFlow de Zapier",
            },
          },
        },
      },
    },
  },
}
```

Campos de la ruta:

- `enabled`: opcional, el valor predeterminado es `true`
- `path`: opcional, el valor predeterminado es `/plugins/webhooks/<routeId>`
- `sessionKey`: sesión obligatoria que posee los TaskFlows vinculados
- `secret`: secreto compartido obligatorio o SecretRef
- `controllerId`: ID opcional del controlador para los flujos gestionados creados
- `description`: nota opcional para el operador

Entradas `secret` compatibles:

- Cadena simple
- SecretRef con `source: "env" | "file" | "exec"`

Si una ruta respaldada por secreto no puede resolver su secreto al iniciar, el plugin omite
esa ruta y registra una advertencia en lugar de exponer un endpoint roto.

## Modelo de seguridad

Cada ruta se considera de confianza para actuar con la autoridad de TaskFlow de su
`sessionKey` configurada.

Esto significa que la ruta puede inspeccionar y mutar TaskFlows propiedad de esa sesión, por lo
que deberías:

- Usar un secreto único y fuerte por ruta
- Preferir referencias de secretos frente a secretos de texto sin formato insertados directamente
- Vincular las rutas a la sesión más específica que se ajuste al flujo de trabajo
- Exponer solo la ruta webhook específica que necesites

El plugin aplica:

- Autenticación con secreto compartido
- Límites de tamaño del cuerpo de la solicitud y protecciones de tiempo de espera
- Limitación de tasa con ventana fija
- Límite de solicitudes en curso
- Acceso a TaskFlow vinculado al propietario mediante `api.runtime.taskFlow.bindSession(...)`

## Formato de la solicitud

Envía solicitudes `POST` con:

- `Content-Type: application/json`
- `Authorization: Bearer <secret>` o `x-openclaw-webhook-secret: <secret>`

Ejemplo:

```bash
curl -X POST https://gateway.example.com/plugins/webhooks/zapier \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_SHARED_SECRET' \
  -d '{"action":"create_flow","goal":"Review inbound queue"}'
```

## Acciones compatibles

Actualmente, el plugin acepta estos valores JSON de `action`:

- `create_flow`
- `get_flow`
- `list_flows`
- `find_latest_flow`
- `resolve_flow`
- `get_task_summary`
- `set_waiting`
- `resume_flow`
- `finish_flow`
- `fail_flow`
- `request_cancel`
- `cancel_flow`
- `run_task`

### `create_flow`

Crea un TaskFlow gestionado para la sesión vinculada de la ruta.

Ejemplo:

```json
{
  "action": "create_flow",
  "goal": "Review inbound queue",
  "status": "queued",
  "notifyPolicy": "done_only"
}
```

### `run_task`

Crea una tarea hija gestionada dentro de un TaskFlow gestionado existente.

Los tiempos de ejecución permitidos son:

- `subagent`
- `acp`

Ejemplo:

```json
{
  "action": "run_task",
  "flowId": "flow_123",
  "runtime": "acp",
  "childSessionKey": "agent:main:acp:worker",
  "task": "Inspect the next message batch"
}
```

## Forma de la respuesta

Las respuestas correctas devuelven:

```json
{
  "ok": true,
  "routeId": "zapier",
  "result": {}
}
```

Las solicitudes rechazadas devuelven:

```json
{
  "ok": false,
  "routeId": "zapier",
  "code": "not_found",
  "error": "TaskFlow not found.",
  "result": {}
}
```

El plugin elimina intencionadamente los metadatos de propietario/sesión de las respuestas del webhook.

## Documentación relacionada

- [SDK de tiempo de ejecución del plugin](/es/plugins/sdk-runtime)
- [Resumen de hooks y webhooks](/es/automation/hooks)
- [CLI webhooks](/cli/webhooks)
