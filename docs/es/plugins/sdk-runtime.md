---
read_when:
    - Necesitas llamar a ayudantes del núcleo desde un plugin (TTS, STT, generación de imágenes, búsqueda web, subagente)
    - Quieres entender qué expone `api.runtime`
    - Estás accediendo a ayudantes de configuración, agente o multimedia desde código de plugin
sidebarTitle: Runtime Helpers
summary: api.runtime -- los ayudantes de runtime inyectados disponibles para los plugins
title: Ayudantes de runtime de plugins
x-i18n:
    generated_at: "2026-04-11T02:46:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: fbf8a6ecd970300f784b8aca20eed40ba12c83107abd27385bfdc3347d2544be
    source_path: plugins/sdk-runtime.md
    workflow: 15
---

# Ayudantes de runtime de plugins

Referencia del objeto `api.runtime` inyectado en cada plugin durante el
registro. Usa estos ayudantes en lugar de importar directamente los componentes internos del host.

<Tip>
  **¿Buscas una guía práctica?** Consulta [Channel Plugins](/es/plugins/sdk-channel-plugins)
  o [Provider Plugins](/es/plugins/sdk-provider-plugins) para ver guías paso a paso
  que muestran estos ayudantes en contexto.
</Tip>

```typescript
register(api) {
  const runtime = api.runtime;
}
```

## Espacios de nombres de runtime

### `api.runtime.agent`

Identidad del agente, directorios y gestión de sesiones.

```typescript
// Resolver el directorio de trabajo del agente
const agentDir = api.runtime.agent.resolveAgentDir(cfg);

// Resolver el espacio de trabajo del agente
const workspaceDir = api.runtime.agent.resolveAgentWorkspaceDir(cfg);

// Obtener la identidad del agente
const identity = api.runtime.agent.resolveAgentIdentity(cfg);

// Obtener el nivel de pensamiento predeterminado
const thinking = api.runtime.agent.resolveThinkingDefault(cfg, provider, model);

// Obtener el tiempo de espera del agente
const timeoutMs = api.runtime.agent.resolveAgentTimeoutMs(cfg);

// Asegurarse de que el espacio de trabajo exista
await api.runtime.agent.ensureAgentWorkspace(cfg);

// Ejecutar un turno de agente integrado
const agentDir = api.runtime.agent.resolveAgentDir(cfg);
const result = await api.runtime.agent.runEmbeddedAgent({
  sessionId: "my-plugin:task-1",
  runId: crypto.randomUUID(),
  sessionFile: path.join(agentDir, "sessions", "my-plugin-task-1.jsonl"),
  workspaceDir: api.runtime.agent.resolveAgentWorkspaceDir(cfg),
  prompt: "Resume los cambios más recientes",
  timeoutMs: api.runtime.agent.resolveAgentTimeoutMs(cfg),
});
```

`runEmbeddedAgent(...)` es el ayudante neutral para iniciar un turno normal de
agente de OpenClaw desde código de plugin. Usa la misma resolución de proveedor/modelo y
la misma selección de arnés de agente que las respuestas activadas por canal.

`runEmbeddedPiAgent(...)` sigue existiendo como alias de compatibilidad.

**Los ayudantes de almacén de sesiones** están en `api.runtime.agent.session`:

```typescript
const storePath = api.runtime.agent.session.resolveStorePath(cfg);
const store = api.runtime.agent.session.loadSessionStore(cfg);
await api.runtime.agent.session.saveSessionStore(cfg, store);
const filePath = api.runtime.agent.session.resolveSessionFilePath(cfg, sessionId);
```

### `api.runtime.agent.defaults`

Constantes predeterminadas de modelo y proveedor:

```typescript
const model = api.runtime.agent.defaults.model; // p. ej. "anthropic/claude-sonnet-4-6"
const provider = api.runtime.agent.defaults.provider; // p. ej. "anthropic"
```

### `api.runtime.subagent`

Inicia y gestiona ejecuciones de subagentes en segundo plano.

```typescript
// Iniciar una ejecución de subagente
const { runId } = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Amplía esta consulta en búsquedas de seguimiento más específicas.",
  provider: "openai", // anulación opcional
  model: "gpt-4.1-mini", // anulación opcional
  deliver: false,
});

// Esperar a que termine
const result = await api.runtime.subagent.waitForRun({ runId, timeoutMs: 30000 });

// Leer mensajes de la sesión
const { messages } = await api.runtime.subagent.getSessionMessages({
  sessionKey: "agent:main:subagent:search-helper",
  limit: 10,
});

// Eliminar una sesión
await api.runtime.subagent.deleteSession({
  sessionKey: "agent:main:subagent:search-helper",
});
```

<Warning>
  Las anulaciones de modelo (`provider`/`model`) requieren aceptación explícita del operador mediante
  `plugins.entries.<id>.subagent.allowModelOverride: true` en la configuración.
  Los plugins no confiables pueden seguir ejecutando subagentes, pero las solicitudes de anulación se rechazan.
</Warning>

### `api.runtime.taskFlow`

Vincula un runtime de Task Flow a una clave de sesión existente de OpenClaw o a un
contexto de herramienta confiable, y luego crea y gestiona Task Flows sin pasar un propietario en cada llamada.

```typescript
const taskFlow = api.runtime.taskFlow.fromToolContext(ctx);

const created = taskFlow.createManaged({
  controllerId: "my-plugin/review-batch",
  goal: "Revisar nuevas pull requests",
});

const child = taskFlow.runTask({
  flowId: created.flowId,
  runtime: "acp",
  childSessionKey: "agent:main:subagent:reviewer",
  task: "Revisar PR #123",
  status: "running",
  startedAt: Date.now(),
});

const waiting = taskFlow.setWaiting({
  flowId: created.flowId,
  expectedRevision: created.revision,
  currentStep: "await-human-reply",
  waitJson: { kind: "reply", channel: "telegram" },
});
```

Usa `bindSession({ sessionKey, requesterOrigin })` cuando ya tengas una
clave de sesión de OpenClaw confiable desde tu propia capa de vinculación. No hagas vinculaciones a partir de entrada bruta del usuario.

### `api.runtime.tts`

Síntesis de texto a voz.

```typescript
// TTS estándar
const clip = await api.runtime.tts.textToSpeech({
  text: "Hola desde OpenClaw",
  cfg: api.config,
});

// TTS optimizado para telefonía
const telephonyClip = await api.runtime.tts.textToSpeechTelephony({
  text: "Hola desde OpenClaw",
  cfg: api.config,
});

// Listar voces disponibles
const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Usa la configuración central `messages.tts` y la selección de proveedor. Devuelve un
búfer de audio PCM + frecuencia de muestreo.

### `api.runtime.mediaUnderstanding`

Análisis de imágenes, audio y video.

```typescript
// Describir una imagen
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

// Transcribir audio
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  mime: "audio/ogg", // opcional, para cuando no se puede inferir el tipo MIME
});

// Describir un video
const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});

// Análisis genérico de archivos
const result = await api.runtime.mediaUnderstanding.runFile({
  filePath: "/tmp/inbound-file.pdf",
  cfg: api.config,
});
```

Devuelve `{ text: undefined }` cuando no se produce salida (por ejemplo, entrada omitida).

<Info>
  `api.runtime.stt.transcribeAudioFile(...)` sigue existiendo como alias de compatibilidad
  para `api.runtime.mediaUnderstanding.transcribeAudioFile(...)`.
</Info>

### `api.runtime.imageGeneration`

Generación de imágenes.

```typescript
const result = await api.runtime.imageGeneration.generate({
  prompt: "Un robot pintando un atardecer",
  cfg: api.config,
});

const providers = api.runtime.imageGeneration.listProviders({ cfg: api.config });
```

### `api.runtime.webSearch`

Búsqueda web.

```typescript
const providers = api.runtime.webSearch.listProviders({ config: api.config });

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: { query: "OpenClaw plugin SDK", count: 5 },
});
```

### `api.runtime.media`

Utilidades multimedia de bajo nivel.

```typescript
const webMedia = await api.runtime.media.loadWebMedia(url);
const mime = await api.runtime.media.detectMime(buffer);
const kind = api.runtime.media.mediaKindFromMime("image/jpeg"); // "image"
const isVoice = api.runtime.media.isVoiceCompatibleAudio(filePath);
const metadata = await api.runtime.media.getImageMetadata(filePath);
const resized = await api.runtime.media.resizeToJpeg(buffer, { maxWidth: 800 });
```

### `api.runtime.config`

Carga y escritura de configuración.

```typescript
const cfg = await api.runtime.config.loadConfig();
await api.runtime.config.writeConfigFile(cfg);
```

### `api.runtime.system`

Utilidades de nivel de sistema.

```typescript
await api.runtime.system.enqueueSystemEvent(event);
api.runtime.system.requestHeartbeatNow();
const output = await api.runtime.system.runCommandWithTimeout(cmd, args, opts);
const hint = api.runtime.system.formatNativeDependencyHint(pkg);
```

### `api.runtime.events`

Suscripciones a eventos.

```typescript
api.runtime.events.onAgentEvent((event) => {
  /* ... */
});
api.runtime.events.onSessionTranscriptUpdate((update) => {
  /* ... */
});
```

### `api.runtime.logging`

Registro.

```typescript
const verbose = api.runtime.logging.shouldLogVerbose();
const childLogger = api.runtime.logging.getChildLogger({ plugin: "my-plugin" }, { level: "debug" });
```

### `api.runtime.modelAuth`

Resolución de autenticación de modelos y proveedores.

```typescript
const auth = await api.runtime.modelAuth.getApiKeyForModel({ model, cfg });
const providerAuth = await api.runtime.modelAuth.resolveApiKeyForProvider({
  provider: "openai",
  cfg,
});
```

### `api.runtime.state`

Resolución del directorio de estado.

```typescript
const stateDir = api.runtime.state.resolveStateDir();
```

### `api.runtime.tools`

Fábricas de herramientas de memoria y CLI.

```typescript
const getTool = api.runtime.tools.createMemoryGetTool(/* ... */);
const searchTool = api.runtime.tools.createMemorySearchTool(/* ... */);
api.runtime.tools.registerMemoryCli(/* ... */);
```

### `api.runtime.channel`

Ayudantes de runtime específicos del canal (disponibles cuando se carga un plugin de canal).

`api.runtime.channel.mentions` es la superficie compartida de política de menciones entrantes para
plugins de canal integrados que usan inyección de runtime:

```typescript
const mentionMatch = api.runtime.channel.mentions.matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const decision = api.runtime.channel.mentions.resolveInboundMentionDecision({
  facts: {
    canDetectMention: true,
    wasMentioned: mentionMatch.matched,
    implicitMentionKinds: api.runtime.channel.mentions.implicitMentionKindWhen(
      "reply_to_bot",
      isReplyToBot,
    ),
  },
  policy: {
    isGroup,
    requireMention,
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});
```

Ayudantes de mención disponibles:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

`api.runtime.channel.mentions` intencionalmente no expone los ayudantes heredados de compatibilidad
`resolveMentionGating*`. Prefiere la ruta normalizada
`{ facts, policy }`.

## Almacenar referencias de runtime

Usa `createPluginRuntimeStore` para almacenar la referencia de runtime y usarla fuera
del callback `register`:

```typescript
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
import type { PluginRuntime } from "openclaw/plugin-sdk/runtime-store";

const store = createPluginRuntimeStore<PluginRuntime>("runtime de my-plugin no inicializado");

// En tu punto de entrada
export default defineChannelPluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Example",
  plugin: myPlugin,
  setRuntime: store.setRuntime,
});

// En otros archivos
export function getRuntime() {
  return store.getRuntime(); // lanza una excepción si no está inicializado
}

export function tryGetRuntime() {
  return store.tryGetRuntime(); // devuelve null si no está inicializado
}
```

## Otros campos de nivel superior de `api`

Además de `api.runtime`, el objeto API también proporciona:

| Campo                    | Tipo                      | Descripción                                                                                 |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | ID del plugin                                                                               |
| `api.name`               | `string`                  | Nombre para mostrar del plugin                                                              |
| `api.config`             | `OpenClawConfig`          | Instantánea de configuración actual (instantánea activa en memoria del runtime cuando está disponible) |
| `api.pluginConfig`       | `Record<string, unknown>` | Configuración específica del plugin desde `plugins.entries.<id>.config`                     |
| `api.logger`             | `PluginLogger`            | Registrador con alcance (`debug`, `info`, `warn`, `error`)                                 |
| `api.registrationMode`   | `PluginRegistrationMode`  | Modo de carga actual; `"setup-runtime"` es la ventana ligera de inicio/configuración antes de la entrada completa |
| `api.resolvePath(input)` | `(string) => string`      | Resuelve una ruta relativa a la raíz del plugin                                             |

## Relacionado

- [SDK Overview](/es/plugins/sdk-overview) -- referencia de subrutas
- [SDK Entry Points](/es/plugins/sdk-entrypoints) -- opciones de `definePluginEntry`
- [Plugin Internals](/es/plugins/architecture) -- modelo de capacidades y registro
