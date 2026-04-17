---
read_when:
    - Quieres automatización basada en eventos para /new, /reset, /stop y eventos del ciclo de vida del agente
    - Quieres crear, instalar o depurar hooks
summary: 'Hooks: automatización basada en eventos para comandos y eventos del ciclo de vida'
title: Hooks
x-i18n:
    generated_at: "2026-04-11T02:44:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 14296398e4042d442ebdf071a07c6be99d4afda7cbf3c2b934e76dc5539742c7
    source_path: automation/hooks.md
    workflow: 15
---

# Hooks

Los hooks son scripts pequeños que se ejecutan cuando sucede algo dentro del Gateway. Se descubren automáticamente desde directorios y se pueden inspeccionar con `openclaw hooks`.

Hay dos tipos de hooks en OpenClaw:

- **Hooks internos** (esta página): se ejecutan dentro del Gateway cuando se activan eventos del agente, como `/new`, `/reset`, `/stop` o eventos del ciclo de vida.
- **Webhooks**: endpoints HTTP externos que permiten que otros sistemas activen trabajo en OpenClaw. Consulta [Webhooks](/es/automation/cron-jobs#webhooks).

Los hooks también pueden incluirse dentro de plugins. `openclaw hooks list` muestra tanto hooks independientes como hooks administrados por plugins.

## Inicio rápido

```bash
# Listar hooks disponibles
openclaw hooks list

# Habilitar un hook
openclaw hooks enable session-memory

# Verificar el estado del hook
openclaw hooks check

# Obtener información detallada
openclaw hooks info session-memory
```

## Tipos de eventos

| Evento                   | Cuándo se activa                                |
| ------------------------ | ----------------------------------------------- |
| `command:new`            | Se emite el comando `/new`                      |
| `command:reset`          | Se emite el comando `/reset`                    |
| `command:stop`           | Se emite el comando `/stop`                     |
| `command`                | Cualquier evento de comando (listener general)  |
| `session:compact:before` | Antes de que la compactación resuma el historial |
| `session:compact:after`  | Después de que se completa la compactación      |
| `session:patch`          | Cuando se modifican las propiedades de la sesión |
| `agent:bootstrap`        | Antes de inyectar los archivos bootstrap del workspace |
| `gateway:startup`        | Después de iniciar los canales y cargar los hooks |
| `message:received`       | Mensaje entrante desde cualquier canal          |
| `message:transcribed`    | Después de completar la transcripción de audio  |
| `message:preprocessed`   | Después de completar todo el procesamiento de medios y enlaces |
| `message:sent`           | Mensaje saliente entregado                      |

## Escribir hooks

### Estructura de un hook

Cada hook es un directorio que contiene dos archivos:

```
my-hook/
├── HOOK.md          # Metadatos + documentación
└── handler.ts       # Implementación del handler
```

### Formato de HOOK.md

```markdown
---
name: my-hook
description: "Breve descripción de lo que hace este hook"
metadata:
  { "openclaw": { "emoji": "🔗", "events": ["command:new"], "requires": { "bins": ["node"] } } }
---

# My Hook

La documentación detallada va aquí.
```

**Campos de metadatos** (`metadata.openclaw`):

| Campo      | Descripción                                          |
| ---------- | ---------------------------------------------------- |
| `emoji`    | Emoji mostrado para la CLI                           |
| `events`   | Array de eventos que se escucharán                   |
| `export`   | Export nombrado que se usará (por defecto `"default"`) |
| `os`       | Plataformas requeridas (p. ej., `["darwin", "linux"]`) |
| `requires` | Rutas requeridas de `bins`, `anyBins`, `env` o `config` |
| `always`   | Omite las comprobaciones de elegibilidad (boolean)   |
| `install`  | Métodos de instalación                               |

### Implementación del handler

```typescript
const handler = async (event) => {
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  console.log(`[my-hook] New command triggered`);
  // Your logic here

  // Optionally send message to user
  event.messages.push("Hook executed!");
};

export default handler;
```

Cada evento incluye: `type`, `action`, `sessionKey`, `timestamp`, `messages` (haz `push` para enviarlos al usuario) y `context` (datos específicos del evento).

### Aspectos destacados del contexto de eventos

**Eventos de comando** (`command:new`, `command:reset`): `context.sessionEntry`, `context.previousSessionEntry`, `context.commandSource`, `context.workspaceDir`, `context.cfg`.

**Eventos de mensaje** (`message:received`): `context.from`, `context.content`, `context.channelId`, `context.metadata` (datos específicos del proveedor, incluidos `senderId`, `senderName`, `guildId`).

**Eventos de mensaje** (`message:sent`): `context.to`, `context.content`, `context.success`, `context.channelId`.

**Eventos de mensaje** (`message:transcribed`): `context.transcript`, `context.from`, `context.channelId`, `context.mediaPath`.

**Eventos de mensaje** (`message:preprocessed`): `context.bodyForAgent` (cuerpo final enriquecido), `context.from`, `context.channelId`.

**Eventos bootstrap** (`agent:bootstrap`): `context.bootstrapFiles` (array mutable), `context.agentId`.

**Eventos de parche de sesión** (`session:patch`): `context.sessionEntry`, `context.patch` (solo campos modificados), `context.cfg`. Solo los clientes privilegiados pueden activar eventos de parche.

**Eventos de compactación**: `session:compact:before` incluye `messageCount`, `tokenCount`. `session:compact:after` agrega `compactedCount`, `summaryLength`, `tokensBefore`, `tokensAfter`.

## Descubrimiento de hooks

Los hooks se descubren desde estos directorios, en orden de precedencia creciente de sobrescritura:

1. **Hooks incluidos**: enviados con OpenClaw
2. **Hooks de plugins**: hooks incluidos dentro de plugins instalados
3. **Hooks administrados**: `~/.openclaw/hooks/` (instalados por el usuario, compartidos entre workspaces). Los directorios adicionales de `hooks.internal.load.extraDirs` comparten esta precedencia.
4. **Hooks del workspace**: `<workspace>/hooks/` (por agente, deshabilitados por defecto hasta que se habilitan explícitamente)

Los hooks del workspace pueden agregar nombres de hooks nuevos, pero no pueden sobrescribir hooks incluidos, administrados o proporcionados por plugins con el mismo nombre.

### Paquetes de hooks

Los paquetes de hooks son paquetes npm que exportan hooks mediante `openclaw.hooks` en `package.json`. Instálalos con:

```bash
openclaw plugins install <path-or-spec>
```

Las especificaciones npm son solo de registro (nombre del paquete + versión exacta opcional o dist-tag). Se rechazan las especificaciones Git/URL/file y los rangos semver.

## Hooks incluidos

| Hook                  | Eventos                        | Qué hace                                              |
| --------------------- | ------------------------------ | ----------------------------------------------------- |
| session-memory        | `command:new`, `command:reset` | Guarda el contexto de la sesión en `<workspace>/memory/` |
| bootstrap-extra-files | `agent:bootstrap`              | Inyecta archivos bootstrap adicionales a partir de patrones glob |
| command-logger        | `command`                      | Registra todos los comandos en `~/.openclaw/logs/commands.log` |
| boot-md               | `gateway:startup`              | Ejecuta `BOOT.md` cuando se inicia el gateway         |

Habilita cualquier hook incluido:

```bash
openclaw hooks enable <hook-name>
```

<a id="session-memory"></a>

### Detalles de session-memory

Extrae los últimos 15 mensajes de usuario/asistente, genera un slug descriptivo de nombre de archivo mediante un LLM y lo guarda en `<workspace>/memory/YYYY-MM-DD-slug.md`. Requiere que `workspace.dir` esté configurado.

<a id="bootstrap-extra-files"></a>

### Configuración de bootstrap-extra-files

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "bootstrap-extra-files": {
          "enabled": true,
          "paths": ["packages/*/AGENTS.md", "packages/*/TOOLS.md"]
        }
      }
    }
  }
}
```

Las rutas se resuelven en relación con el workspace. Solo se cargan nombres base bootstrap reconocidos (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`, `MEMORY.md`).

<a id="command-logger"></a>

### Detalles de command-logger

Registra cada comando con barra en `~/.openclaw/logs/commands.log`.

<a id="boot-md"></a>

### Detalles de boot-md

Ejecuta `BOOT.md` desde el workspace activo cuando se inicia el gateway.

## Hooks de plugins

Los plugins pueden registrar hooks mediante el Plugin SDK para una integración más profunda: interceptar llamadas a herramientas, modificar prompts, controlar el flujo de mensajes y más. El Plugin SDK expone 28 hooks que cubren la resolución de modelos, el ciclo de vida del agente, el flujo de mensajes, la ejecución de herramientas, la coordinación de subagentes y el ciclo de vida del gateway.

Para la referencia completa de hooks de plugins, incluidos `before_tool_call`, `before_agent_reply`, `before_install` y todos los demás hooks de plugins, consulta [Plugin Architecture](/es/plugins/architecture#provider-runtime-hooks).

## Configuración

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "session-memory": { "enabled": true },
        "command-logger": { "enabled": false }
      }
    }
  }
}
```

Variables de entorno por hook:

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "my-hook": {
          "enabled": true,
          "env": { "MY_CUSTOM_VAR": "value" }
        }
      }
    }
  }
}
```

Directorios de hooks adicionales:

```json
{
  "hooks": {
    "internal": {
      "load": {
        "extraDirs": ["/path/to/more/hooks"]
      }
    }
  }
}
```

<Note>
El formato heredado de configuración de array `hooks.internal.handlers` todavía es compatible por compatibilidad con versiones anteriores, pero los hooks nuevos deben usar el sistema basado en descubrimiento.
</Note>

## Referencia de la CLI

```bash
# Listar todos los hooks (agrega --eligible, --verbose o --json)
openclaw hooks list

# Mostrar información detallada sobre un hook
openclaw hooks info <hook-name>

# Mostrar resumen de elegibilidad
openclaw hooks check

# Habilitar/deshabilitar
openclaw hooks enable <hook-name>
openclaw hooks disable <hook-name>
```

## Buenas prácticas

- **Mantén los handlers rápidos.** Los hooks se ejecutan durante el procesamiento de comandos. Ejecuta en segundo plano el trabajo pesado con `void processInBackground(event)`.
- **Maneja los errores con cuidado.** Envuelve las operaciones riesgosas en try/catch; no lances errores para que otros handlers puedan ejecutarse.
- **Filtra eventos pronto.** Haz `return` inmediatamente si el tipo/acción del evento no es relevante.
- **Usa claves de evento específicas.** Prefiere `"events": ["command:new"]` en lugar de `"events": ["command"]` para reducir la sobrecarga.

## Solución de problemas

### Hook no descubierto

```bash
# Verificar la estructura del directorio
ls -la ~/.openclaw/hooks/my-hook/
# Debe mostrar: HOOK.md, handler.ts

# Listar todos los hooks descubiertos
openclaw hooks list
```

### Hook no elegible

```bash
openclaw hooks info my-hook
```

Comprueba si faltan binarios (PATH), variables de entorno, valores de configuración o compatibilidad del SO.

### Hook no se ejecuta

1. Verifica que el hook esté habilitado: `openclaw hooks list`
2. Reinicia tu proceso gateway para que los hooks se recarguen.
3. Revisa los logs del gateway: `./scripts/clawlog.sh | grep hook`

## Relacionado

- [CLI Reference: hooks](/cli/hooks)
- [Webhooks](/es/automation/cron-jobs#webhooks)
- [Plugin Architecture](/es/plugins/architecture#provider-runtime-hooks) — referencia completa de hooks de plugins
- [Configuration](/es/gateway/configuration-reference#hooks)
