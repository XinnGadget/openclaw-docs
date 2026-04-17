---
read_when:
    - Вам потрібно викликати допоміжні функції ядра з Plugin-а (TTS, STT, генерація зображень, вебпошук, subagent)
    - Ви хочете зрозуміти, що надає `api.runtime`
    - Ви отримуєте доступ до допоміжних функцій конфігурації, агента або медіа з коду Plugin-а
sidebarTitle: Runtime Helpers
summary: api.runtime — впроваджені допоміжні функції середовища виконання, доступні для Plugin-ів
title: Допоміжні функції середовища виконання Plugin-ів
x-i18n:
    generated_at: "2026-04-15T16:36:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: c77a6e9cd48c84affa17dce684bbd0e072c8b63485e4a5d569f3793a4ea4f9c8
    source_path: plugins/sdk-runtime.md
    workflow: 15
---

# Допоміжні функції середовища виконання Plugin-ів

Довідник для об’єкта `api.runtime`, який впроваджується в кожен Plugin під час
реєстрації. Використовуйте ці допоміжні функції замість прямого імпорту внутрішніх компонентів хоста.

<Tip>
  **Шукаєте покроковий огляд?** Див. [Channel Plugins](/uk/plugins/sdk-channel-plugins)
  або [Provider Plugins](/uk/plugins/sdk-provider-plugins), щоб переглянути покрокові інструкції,
  які показують ці допоміжні функції в контексті.
</Tip>

```typescript
register(api) {
  const runtime = api.runtime;
}
```

## Простори імен середовища виконання

### `api.runtime.agent`

Ідентичність агента, каталоги та керування сесіями.

```typescript
// Resolve the agent's working directory
const agentDir = api.runtime.agent.resolveAgentDir(cfg);

// Resolve agent workspace
const workspaceDir = api.runtime.agent.resolveAgentWorkspaceDir(cfg);

// Get agent identity
const identity = api.runtime.agent.resolveAgentIdentity(cfg);

// Get default thinking level
const thinking = api.runtime.agent.resolveThinkingDefault(cfg, provider, model);

// Get agent timeout
const timeoutMs = api.runtime.agent.resolveAgentTimeoutMs(cfg);

// Ensure workspace exists
await api.runtime.agent.ensureAgentWorkspace(cfg);

// Run an embedded agent turn
const agentDir = api.runtime.agent.resolveAgentDir(cfg);
const result = await api.runtime.agent.runEmbeddedAgent({
  sessionId: "my-plugin:task-1",
  runId: crypto.randomUUID(),
  sessionFile: path.join(agentDir, "sessions", "my-plugin-task-1.jsonl"),
  workspaceDir: api.runtime.agent.resolveAgentWorkspaceDir(cfg),
  prompt: "Summarize the latest changes",
  timeoutMs: api.runtime.agent.resolveAgentTimeoutMs(cfg),
});
```

`runEmbeddedAgent(...)` — це нейтральна допоміжна функція для запуску звичайного ходу
агента OpenClaw з коду Plugin-а. Вона використовує те саме визначення provider/model і
вибір agent-harness, що й відповіді, ініційовані каналом.

`runEmbeddedPiAgent(...)` залишається сумісним псевдонімом.

**Допоміжні функції сховища сесій** розміщені в `api.runtime.agent.session`:

```typescript
const storePath = api.runtime.agent.session.resolveStorePath(cfg);
const store = api.runtime.agent.session.loadSessionStore(cfg);
await api.runtime.agent.session.saveSessionStore(cfg, store);
const filePath = api.runtime.agent.session.resolveSessionFilePath(cfg, sessionId);
```

### `api.runtime.agent.defaults`

Константи моделі та provider за замовчуванням:

```typescript
const model = api.runtime.agent.defaults.model; // e.g. "anthropic/claude-sonnet-4-6"
const provider = api.runtime.agent.defaults.provider; // e.g. "anthropic"
```

### `api.runtime.subagent`

Запуск і керування фоновими запусками subagent.

```typescript
// Start a subagent run
const { runId } = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai", // optional override
  model: "gpt-4.1-mini", // optional override
  deliver: false,
});

// Wait for completion
const result = await api.runtime.subagent.waitForRun({ runId, timeoutMs: 30000 });

// Read session messages
const { messages } = await api.runtime.subagent.getSessionMessages({
  sessionKey: "agent:main:subagent:search-helper",
  limit: 10,
});

// Delete a session
await api.runtime.subagent.deleteSession({
  sessionKey: "agent:main:subagent:search-helper",
});
```

<Warning>
  Перевизначення моделі (`provider`/`model`) потребує згоди оператора через
  `plugins.entries.<id>.subagent.allowModelOverride: true` у конфігурації.
  Ненадійні plugins усе ще можуть запускати subagents, але запити на перевизначення відхиляються.
</Warning>

### `api.runtime.taskFlow`

Прив’язка середовища виконання TaskFlow до наявного ключа сесії OpenClaw або довіреного
контексту інструмента, а потім створення й керування TaskFlow без передавання власника під час кожного виклику.

```typescript
const taskFlow = api.runtime.taskFlow.fromToolContext(ctx);

const created = taskFlow.createManaged({
  controllerId: "my-plugin/review-batch",
  goal: "Review new pull requests",
});

const child = taskFlow.runTask({
  flowId: created.flowId,
  runtime: "acp",
  childSessionKey: "agent:main:subagent:reviewer",
  task: "Review PR #123",
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

Використовуйте `bindSession({ sessionKey, requesterOrigin })`, коли у вас уже є
довірений ключ сесії OpenClaw з вашого власного шару прив’язки. Не виконуйте прив’язку з необробленого
користувацького вводу.

### `api.runtime.tts`

Синтез мовлення з тексту.

```typescript
// Standard TTS
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

// Telephony-optimized TTS
const telephonyClip = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

// List available voices
const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Використовує основну конфігурацію `messages.tts` і вибір provider. Повертає PCM-аудіобуфер
і частоту дискретизації.

### `api.runtime.mediaUnderstanding`

Аналіз зображень, аудіо та відео.

```typescript
// Describe an image
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

// Transcribe audio
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  mime: "audio/ogg", // optional, for when MIME cannot be inferred
});

// Describe a video
const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});

// Generic file analysis
const result = await api.runtime.mediaUnderstanding.runFile({
  filePath: "/tmp/inbound-file.pdf",
  cfg: api.config,
});
```

Повертає `{ text: undefined }`, коли вихідні дані не створено (наприклад, якщо ввід пропущено).

<Info>
  `api.runtime.stt.transcribeAudioFile(...)` залишається сумісним псевдонімом
  для `api.runtime.mediaUnderstanding.transcribeAudioFile(...)`.
</Info>

### `api.runtime.imageGeneration`

Генерація зображень.

```typescript
const result = await api.runtime.imageGeneration.generate({
  prompt: "A robot painting a sunset",
  cfg: api.config,
});

const providers = api.runtime.imageGeneration.listProviders({ cfg: api.config });
```

### `api.runtime.webSearch`

Вебпошук.

```typescript
const providers = api.runtime.webSearch.listProviders({ config: api.config });

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: { query: "OpenClaw plugin SDK", count: 5 },
});
```

### `api.runtime.media`

Низькорівневі медіаутиліти.

```typescript
const webMedia = await api.runtime.media.loadWebMedia(url);
const mime = await api.runtime.media.detectMime(buffer);
const kind = api.runtime.media.mediaKindFromMime("image/jpeg"); // "image"
const isVoice = api.runtime.media.isVoiceCompatibleAudio(filePath);
const metadata = await api.runtime.media.getImageMetadata(filePath);
const resized = await api.runtime.media.resizeToJpeg(buffer, { maxWidth: 800 });
```

### `api.runtime.config`

Завантаження та запис конфігурації.

```typescript
const cfg = await api.runtime.config.loadConfig();
await api.runtime.config.writeConfigFile(cfg);
```

### `api.runtime.system`

Системні утиліти.

```typescript
await api.runtime.system.enqueueSystemEvent(event);
api.runtime.system.requestHeartbeatNow();
const output = await api.runtime.system.runCommandWithTimeout(cmd, args, opts);
const hint = api.runtime.system.formatNativeDependencyHint(pkg);
```

### `api.runtime.events`

Підписки на події.

```typescript
api.runtime.events.onAgentEvent((event) => {
  /* ... */
});
api.runtime.events.onSessionTranscriptUpdate((update) => {
  /* ... */
});
```

### `api.runtime.logging`

Логування.

```typescript
const verbose = api.runtime.logging.shouldLogVerbose();
const childLogger = api.runtime.logging.getChildLogger({ plugin: "my-plugin" }, { level: "debug" });
```

### `api.runtime.modelAuth`

Визначення автентифікації моделі та provider.

```typescript
const auth = await api.runtime.modelAuth.getApiKeyForModel({ model, cfg });
const providerAuth = await api.runtime.modelAuth.resolveApiKeyForProvider({
  provider: "openai",
  cfg,
});
```

### `api.runtime.state`

Визначення каталогу стану.

```typescript
const stateDir = api.runtime.state.resolveStateDir();
```

### `api.runtime.tools`

Фабрики інструментів пам’яті та CLI.

```typescript
const getTool = api.runtime.tools.createMemoryGetTool(/* ... */);
const searchTool = api.runtime.tools.createMemorySearchTool(/* ... */);
api.runtime.tools.registerMemoryCli(/* ... */);
```

### `api.runtime.channel`

Допоміжні функції середовища виконання для конкретного каналу (доступні, коли завантажено channel Plugin).

`api.runtime.channel.mentions` — це спільна поверхня політики згадок для вхідних повідомлень
для вбудованих channel Plugin-ів, які використовують впровадження середовища виконання:

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

Доступні допоміжні функції згадок:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

`api.runtime.channel.mentions` навмисно не надає старі
сумісні допоміжні функції `resolveMentionGating*`. Надавайте перевагу нормалізованому
шляху `{ facts, policy }`.

## Зберігання посилань на середовище виконання

Використовуйте `createPluginRuntimeStore`, щоб зберегти посилання на середовище виконання для використання поза межами
зворотного виклику `register`:

```typescript
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
import type { PluginRuntime } from "openclaw/plugin-sdk/runtime-store";

const store = createPluginRuntimeStore<PluginRuntime>({
  pluginId: "my-plugin",
  errorMessage: "my-plugin runtime not initialized",
});

// In your entry point
export default defineChannelPluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Example",
  plugin: myPlugin,
  setRuntime: store.setRuntime,
});

// In other files
export function getRuntime() {
  return store.getRuntime(); // throws if not initialized
}

export function tryGetRuntime() {
  return store.tryGetRuntime(); // returns null if not initialized
}
```

Для ідентичності runtime-store надавайте перевагу `pluginId`. Нижчорівнева форма `key`
призначена для нечастих випадків, коли одному Plugin-у навмисно потрібно більше одного слота середовища виконання.

## Інші поля верхнього рівня `api`

Окрім `api.runtime`, об’єкт API також надає:

| Поле                     | Тип                       | Опис                                                                                        |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | Ідентифікатор Plugin-а                                                                      |
| `api.name`               | `string`                  | Відображувана назва Plugin-а                                                                |
| `api.config`             | `OpenClawConfig`          | Поточний знімок конфігурації (активний знімок середовища виконання в пам’яті, коли доступний) |
| `api.pluginConfig`       | `Record<string, unknown>` | Конфігурація Plugin-а з `plugins.entries.<id>.config`                                      |
| `api.logger`             | `PluginLogger`            | Logger з областю видимості (`debug`, `info`, `warn`, `error`)                              |
| `api.registrationMode`   | `PluginRegistrationMode`  | Поточний режим завантаження; `"setup-runtime"` — це полегшене вікно запуску/налаштування перед повним запуском entry point |
| `api.resolvePath(input)` | `(string) => string`      | Визначає шлях відносно кореня Plugin-а                                                      |

## Пов’язане

- [Огляд SDK](/uk/plugins/sdk-overview) -- довідник щодо subpath
- [Точки входу SDK](/uk/plugins/sdk-entrypoints) -- параметри `definePluginEntry`
- [Внутрішні компоненти Plugin-ів](/uk/plugins/architecture) -- модель можливостей і реєстр
