---
read_when:
    - Quieres un respaldo confiable cuando fallen los proveedores de API
    - Estás ejecutando Codex CLI u otras CLI de IA locales y quieres reutilizarlas
    - Quieres entender el puente loopback de MCP para el acceso a herramientas del backend de CLI
summary: 'Backends de CLI: respaldo de CLI de IA local con puente opcional de herramientas MCP'
title: Backends de CLI
x-i18n:
    generated_at: "2026-04-07T05:02:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: f061357f420455ad6ffaabe7fe28f1fb1b1769d73a4eb2e6f45c6eb3c2e36667
    source_path: gateway/cli-backends.md
    workflow: 15
---

# Backends de CLI (runtime de respaldo)

OpenClaw puede ejecutar **CLI de IA locales** como un **respaldo solo de texto** cuando los proveedores de API no están disponibles,
tienen limitación de tasa o se comportan mal temporalmente. Esto es intencionalmente conservador:

- **Las herramientas de OpenClaw no se inyectan directamente**, pero los backends con `bundleMcp: true`
  pueden recibir herramientas del gateway mediante un puente MCP loopback.
- **Streaming JSONL** para las CLI que lo admiten.
- **Las sesiones son compatibles** (para que los turnos de seguimiento sigan siendo coherentes).
- **Las imágenes pueden pasarse** si la CLI acepta rutas de imágenes.

Esto está diseñado como una **red de seguridad** en lugar de una ruta principal. Úsalo cuando
quieras respuestas de texto que “siempre funcionen” sin depender de APIs externas.

Si quieres un runtime con arnés completo con controles de sesión ACP, tareas en segundo plano,
vinculación de hilos/conversaciones y sesiones externas persistentes de codificación, usa
[ACP Agents](/es/tools/acp-agents) en su lugar. Los backends de CLI no son ACP.

## Inicio rápido para principiantes

Puedes usar Codex CLI **sin ninguna configuración** (el plugin incluido de OpenAI
registra un backend predeterminado):

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

Si tu gateway se ejecuta bajo launchd/systemd y PATH es mínimo, añade solo la
ruta del comando:

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
      },
    },
  },
}
```

Eso es todo. No se necesitan claves ni configuración de autenticación adicional aparte de la propia CLI.

Si usas un backend de CLI incluido como **proveedor principal de mensajes** en un
host de gateway, OpenClaw ahora carga automáticamente el plugin incluido propietario cuando tu configuración
hace referencia explícita a ese backend en una referencia de modelo o en
`agents.defaults.cliBackends`.

## Uso como respaldo

Añade un backend de CLI a tu lista de respaldos para que solo se ejecute cuando fallen los modelos principales:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["codex-cli/gpt-5.4"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "codex-cli/gpt-5.4": {},
      },
    },
  },
}
```

Notas:

- Si usas `agents.defaults.models` (lista de permitidos), también debes incluir allí los modelos de tu backend de CLI.
- Si falla el proveedor principal (autenticación, límites de tasa, tiempos de espera), OpenClaw
  probará el backend de CLI a continuación.

## Resumen de configuración

Todos los backends de CLI viven en:

```
agents.defaults.cliBackends
```

Cada entrada se indexa por un **id de proveedor** (por ejemplo, `codex-cli`, `my-cli`).
El id del proveedor pasa a ser el lado izquierdo de tu referencia de modelo:

```
<provider>/<model>
```

### Ejemplo de configuración

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-6": "opus",
            "claude-sonnet-4-6": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## Cómo funciona

1. **Selecciona un backend** según el prefijo del proveedor (`codex-cli/...`).
2. **Construye un prompt del sistema** usando el mismo prompt + contexto de espacio de trabajo de OpenClaw.
3. **Ejecuta la CLI** con un id de sesión (si se admite) para que el historial se mantenga consistente.
4. **Analiza la salida** (JSON o texto sin formato) y devuelve el texto final.
5. **Persiste ids de sesión** por backend, para que los seguimientos reutilicen la misma sesión de CLI.

<Note>
El backend incluido `claude-cli` de Anthropic vuelve a ser compatible. El personal de Anthropic
nos dijo que el uso de Claude CLI al estilo OpenClaw vuelve a estar permitido, por lo que OpenClaw trata
el uso de `claude -p` como autorizado para esta integración, a menos que Anthropic publique
una nueva política.
</Note>

## Sesiones

- Si la CLI admite sesiones, configura `sessionArg` (por ejemplo, `--session-id`) o
  `sessionArgs` (marcador `{sessionId}`) cuando el ID deba insertarse
  en varios flags.
- Si la CLI usa un **subcomando de reanudación** con flags diferentes, configura
  `resumeArgs` (reemplaza `args` al reanudar) y opcionalmente `resumeOutput`
  (para reanudaciones no JSON).
- `sessionMode`:
  - `always`: siempre envía un id de sesión (UUID nuevo si no hay ninguno almacenado).
  - `existing`: solo envía un id de sesión si ya se había almacenado antes.
  - `none`: nunca envía un id de sesión.

Notas sobre serialización:

- `serialize: true` mantiene ordenadas las ejecuciones de la misma vía.
- La mayoría de las CLI serializan en una vía de proveedor.
- OpenClaw descarta la reutilización de sesiones de CLI almacenadas cuando cambia el estado de autenticación del backend, incluido volver a iniciar sesión, la rotación de tokens o un cambio en la credencial del perfil de autenticación.

## Imágenes (paso directo)

Si tu CLI acepta rutas de imágenes, configura `imageArg`:

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw escribirá las imágenes base64 en archivos temporales. Si `imageArg` está configurado, esas
rutas se pasan como argumentos de CLI. Si falta `imageArg`, OpenClaw añade las
rutas de archivos al prompt (inyección de ruta), lo que es suficiente para las CLI que cargan
automáticamente archivos locales a partir de rutas simples.

## Entradas / salidas

- `output: "json"` (predeterminado) intenta analizar JSON y extraer texto + id de sesión.
- Para la salida JSON de Gemini CLI, OpenClaw lee el texto de respuesta desde `response` y
  el uso desde `stats` cuando `usage` falta o está vacío.
- `output: "jsonl"` analiza streams JSONL (por ejemplo, Codex CLI `--json`) y extrae el mensaje final del agente más
  identificadores de sesión cuando están presentes.
- `output: "text"` trata stdout como la respuesta final.

Modos de entrada:

- `input: "arg"` (predeterminado) pasa el prompt como el último argumento de la CLI.
- `input: "stdin"` envía el prompt por stdin.
- Si el prompt es muy largo y `maxPromptArgChars` está configurado, se usa stdin.

## Valores predeterminados (propiedad del plugin)

El plugin incluido de OpenAI también registra un valor predeterminado para `codex-cli`:

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

El plugin incluido de Google también registra un valor predeterminado para `google-gemini-cli`:

- `command: "gemini"`
- `args: ["--prompt", "--output-format", "json"]`
- `resumeArgs: ["--resume", "{sessionId}", "--prompt", "--output-format", "json"]`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

Requisito previo: la Gemini CLI local debe estar instalada y disponible como
`gemini` en `PATH` (`brew install gemini-cli` o
`npm install -g @google/gemini-cli`).

Notas sobre JSON de Gemini CLI:

- El texto de respuesta se lee del campo JSON `response`.
- El uso recurre a `stats` cuando `usage` está ausente o vacío.
- `stats.cached` se normaliza como `cacheRead` de OpenClaw.
- Si falta `stats.input`, OpenClaw deriva los tokens de entrada a partir de
  `stats.input_tokens - stats.cached`.

Reemplázalo solo si es necesario (lo habitual: ruta absoluta de `command`).

## Valores predeterminados propiedad del plugin

Los valores predeterminados del backend de CLI ahora forman parte de la superficie del plugin:

- Los plugins los registran con `api.registerCliBackend(...)`.
- El `id` del backend pasa a ser el prefijo del proveedor en las referencias de modelo.
- La configuración del usuario en `agents.defaults.cliBackends.<id>` sigue reemplazando el valor predeterminado del plugin.
- La limpieza de configuración específica del backend sigue siendo propiedad del plugin mediante el hook opcional
  `normalizeConfig`.

## Superposiciones MCP del bundle

Los backends de CLI **no** reciben directamente llamadas a herramientas de OpenClaw, pero un backend puede
optar por una superposición de configuración MCP generada con `bundleMcp: true`.

Comportamiento incluido actual:

- `codex-cli`: sin superposición MCP del bundle
- `google-gemini-cli`: sin superposición MCP del bundle

Cuando bundle MCP está habilitado, OpenClaw:

- genera un servidor MCP HTTP loopback que expone herramientas del gateway al proceso de la CLI
- autentica el puente con un token por sesión (`OPENCLAW_MCP_TOKEN`)
- limita el acceso a las herramientas a la sesión, cuenta y contexto de canal actuales
- carga los servidores bundle-MCP habilitados para el espacio de trabajo actual
- los fusiona con cualquier `--mcp-config` del backend existente
- reescribe los argumentos de la CLI para pasar `--strict-mcp-config --mcp-config <generated-file>`

Si no hay servidores MCP habilitados, OpenClaw sigue inyectando una configuración estricta cuando un
backend opta por bundle MCP para que las ejecuciones en segundo plano permanezcan aisladas.

## Limitaciones

- **Sin llamadas directas a herramientas de OpenClaw.** OpenClaw no inyecta llamadas a herramientas en
  el protocolo del backend de CLI. Los backends solo ven herramientas del gateway cuando optan por
  `bundleMcp: true`.
- **El streaming es específico de cada backend.** Algunos backends transmiten JSONL; otros almacenan en búfer
  hasta salir.
- **Las salidas estructuradas** dependen del formato JSON de la CLI.
- **Las sesiones de Codex CLI** se reanudan mediante salida de texto (sin JSONL), lo que es menos
  estructurado que la ejecución inicial con `--json`. Las sesiones de OpenClaw siguen funcionando
  normalmente.

## Solución de problemas

- **CLI no encontrada**: configura `command` con una ruta completa.
- **Nombre de modelo incorrecto**: usa `modelAliases` para mapear `provider/model` → modelo de CLI.
- **Sin continuidad de sesión**: asegúrate de que `sessionArg` esté configurado y que `sessionMode` no sea
  `none` (Codex CLI actualmente no puede reanudar con salida JSON).
- **Imágenes ignoradas**: configura `imageArg` (y verifica que la CLI admita rutas de archivo).
