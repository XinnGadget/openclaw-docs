---
read_when:
    - Musisz wywołać pomocnicze funkcje rdzenia z Pluginu (TTS, STT, generowanie obrazów, wyszukiwanie w sieci, subagent)
    - Chcesz zrozumieć, co udostępnia `api.runtime`
    - Uzyskujesz dostęp do pomocniczych funkcji konfiguracji, agenta lub multimediów z kodu Pluginu
sidebarTitle: Runtime Helpers
summary: api.runtime — wstrzyknięte pomocnicze funkcje środowiska uruchomieniowego dostępne dla Pluginów
title: Pomocnicze funkcje środowiska uruchomieniowego Pluginu
x-i18n:
    generated_at: "2026-04-15T19:41:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: c77a6e9cd48c84affa17dce684bbd0e072c8b63485e4a5d569f3793a4ea4f9c8
    source_path: plugins/sdk-runtime.md
    workflow: 15
---

# Pomocnicze funkcje środowiska uruchomieniowego Pluginu

Dokumentacja referencyjna obiektu `api.runtime` wstrzykiwanego do każdego Pluginu podczas
rejestracji. Używaj tych funkcji pomocniczych zamiast bezpośrednio importować elementy wewnętrzne hosta.

<Tip>
  **Szukasz omówienia?** Zobacz [Pluginy kanałów](/pl/plugins/sdk-channel-plugins)
  lub [Pluginy dostawców](/pl/plugins/sdk-provider-plugins), aby zapoznać się z przewodnikami krok po kroku,
  które pokazują te funkcje pomocnicze w kontekście.
</Tip>

```typescript
register(api) {
  const runtime = api.runtime;
}
```

## Przestrzenie nazw środowiska uruchomieniowego

### `api.runtime.agent`

Tożsamość agenta, katalogi i zarządzanie sesjami.

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

`runEmbeddedAgent(...)` to neutralna funkcja pomocnicza do uruchamiania zwykłego przebiegu
agenta OpenClaw z kodu Pluginu. Używa tego samego rozpoznawania dostawcy/modelu i
wyboru uprzęży agenta co odpowiedzi wywoływane przez kanał.

`runEmbeddedPiAgent(...)` pozostaje aliasem zgodności.

**Funkcje pomocnicze magazynu sesji** znajdują się w `api.runtime.agent.session`:

```typescript
const storePath = api.runtime.agent.session.resolveStorePath(cfg);
const store = api.runtime.agent.session.loadSessionStore(cfg);
await api.runtime.agent.session.saveSessionStore(cfg, store);
const filePath = api.runtime.agent.session.resolveSessionFilePath(cfg, sessionId);
```

### `api.runtime.agent.defaults`

Stałe domyślnego modelu i dostawcy:

```typescript
const model = api.runtime.agent.defaults.model; // np. "anthropic/claude-sonnet-4-6"
const provider = api.runtime.agent.defaults.provider; // np. "anthropic"
```

### `api.runtime.subagent`

Uruchamianie i zarządzanie przebiegami subagentów w tle.

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
  Nadpisania modelu (`provider`/`model`) wymagają zgody operatora poprzez
  `plugins.entries.<id>.subagent.allowModelOverride: true` w konfiguracji.
  Niezaufane Pluginy nadal mogą uruchamiać subagentów, ale żądania nadpisania są odrzucane.
</Warning>

### `api.runtime.taskFlow`

Powiąż środowisko uruchomieniowe TaskFlow z istniejącym kluczem sesji OpenClaw lub zaufanym
kontekstem narzędzia, a następnie twórz i zarządzaj TaskFlow bez przekazywania właściciela przy każdym wywołaniu.

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

Użyj `bindSession({ sessionKey, requesterOrigin })`, gdy masz już zaufany klucz sesji OpenClaw
z własnej warstwy powiązania. Nie twórz powiązania na podstawie surowych danych wejściowych użytkownika.

### `api.runtime.tts`

Synteza mowy z tekstu.

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

Używa podstawowej konfiguracji `messages.tts` i wyboru dostawcy. Zwraca bufor
dźwięku PCM + częstotliwość próbkowania.

### `api.runtime.mediaUnderstanding`

Analiza obrazów, dźwięku i wideo.

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

Zwraca `{ text: undefined }`, gdy nie zostanie wygenerowany żaden wynik (np. pominięte dane wejściowe).

<Info>
  `api.runtime.stt.transcribeAudioFile(...)` pozostaje aliasem zgodności
  dla `api.runtime.mediaUnderstanding.transcribeAudioFile(...)`.
</Info>

### `api.runtime.imageGeneration`

Generowanie obrazów.

```typescript
const result = await api.runtime.imageGeneration.generate({
  prompt: "A robot painting a sunset",
  cfg: api.config,
});

const providers = api.runtime.imageGeneration.listProviders({ cfg: api.config });
```

### `api.runtime.webSearch`

Wyszukiwanie w sieci.

```typescript
const providers = api.runtime.webSearch.listProviders({ config: api.config });

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: { query: "OpenClaw plugin SDK", count: 5 },
});
```

### `api.runtime.media`

Niskopoziomowe narzędzia multimedialne.

```typescript
const webMedia = await api.runtime.media.loadWebMedia(url);
const mime = await api.runtime.media.detectMime(buffer);
const kind = api.runtime.media.mediaKindFromMime("image/jpeg"); // "image"
const isVoice = api.runtime.media.isVoiceCompatibleAudio(filePath);
const metadata = await api.runtime.media.getImageMetadata(filePath);
const resized = await api.runtime.media.resizeToJpeg(buffer, { maxWidth: 800 });
```

### `api.runtime.config`

Wczytywanie i zapisywanie konfiguracji.

```typescript
const cfg = await api.runtime.config.loadConfig();
await api.runtime.config.writeConfigFile(cfg);
```

### `api.runtime.system`

Narzędzia na poziomie systemu.

```typescript
await api.runtime.system.enqueueSystemEvent(event);
api.runtime.system.requestHeartbeatNow();
const output = await api.runtime.system.runCommandWithTimeout(cmd, args, opts);
const hint = api.runtime.system.formatNativeDependencyHint(pkg);
```

### `api.runtime.events`

Subskrypcje zdarzeń.

```typescript
api.runtime.events.onAgentEvent((event) => {
  /* ... */
});
api.runtime.events.onSessionTranscriptUpdate((update) => {
  /* ... */
});
```

### `api.runtime.logging`

Logowanie.

```typescript
const verbose = api.runtime.logging.shouldLogVerbose();
const childLogger = api.runtime.logging.getChildLogger({ plugin: "my-plugin" }, { level: "debug" });
```

### `api.runtime.modelAuth`

Rozpoznawanie uwierzytelniania modelu i dostawcy.

```typescript
const auth = await api.runtime.modelAuth.getApiKeyForModel({ model, cfg });
const providerAuth = await api.runtime.modelAuth.resolveApiKeyForProvider({
  provider: "openai",
  cfg,
});
```

### `api.runtime.state`

Rozpoznawanie katalogu stanu.

```typescript
const stateDir = api.runtime.state.resolveStateDir();
```

### `api.runtime.tools`

Fabryki narzędzi pamięci i CLI.

```typescript
const getTool = api.runtime.tools.createMemoryGetTool(/* ... */);
const searchTool = api.runtime.tools.createMemorySearchTool(/* ... */);
api.runtime.tools.registerMemoryCli(/* ... */);
```

### `api.runtime.channel`

Funkcje pomocnicze środowiska uruchomieniowego specyficzne dla kanału (dostępne, gdy załadowany jest Plugin kanału).

`api.runtime.channel.mentions` to współdzielona powierzchnia zasad wzmianek przychodzących dla
dołączonych Pluginów kanałów, które korzystają z wstrzykiwania środowiska uruchomieniowego:

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

Dostępne funkcje pomocnicze wzmianek:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

`api.runtime.channel.mentions` celowo nie udostępnia starszych
pomocniczych funkcji zgodności `resolveMentionGating*`. Preferuj znormalizowaną
ścieżkę `{ facts, policy }`.

## Przechowywanie odwołań do środowiska uruchomieniowego

Użyj `createPluginRuntimeStore`, aby przechować odwołanie do środowiska uruchomieniowego do użycia poza
wywołaniem zwrotnym `register`:

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

Preferuj `pluginId` jako tożsamość runtime-store. Niższopoziomowa forma `key` jest
przeznaczona do rzadkich przypadków, gdy jeden Plugin celowo potrzebuje więcej niż jednego gniazda środowiska uruchomieniowego.

## Inne pola najwyższego poziomu `api`

Poza `api.runtime` obiekt API udostępnia również:

| Pole                     | Typ                       | Opis                                                                                         |
| ------------------------ | ------------------------- | -------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | Identyfikator Pluginu                                                                        |
| `api.name`               | `string`                  | Wyświetlana nazwa Pluginu                                                                    |
| `api.config`             | `OpenClawConfig`          | Bieżąca migawka konfiguracji (aktywna migawka środowiska uruchomieniowego w pamięci, jeśli dostępna) |
| `api.pluginConfig`       | `Record<string, unknown>` | Konfiguracja specyficzna dla Pluginu z `plugins.entries.<id>.config`                         |
| `api.logger`             | `PluginLogger`            | Logger o ograniczonym zakresie (`debug`, `info`, `warn`, `error`)                            |
| `api.registrationMode`   | `PluginRegistrationMode`  | Bieżący tryb wczytywania; `"setup-runtime"` to lekkie okno uruchamiania/konfiguracji przed pełnym uruchomieniem wpisu |
| `api.resolvePath(input)` | `(string) => string`      | Rozpoznaje ścieżkę względem katalogu głównego Pluginu                                        |

## Powiązane

- [Omówienie SDK](/pl/plugins/sdk-overview) -- dokumentacja podścieżek
- [Punkty wejścia SDK](/pl/plugins/sdk-entrypoints) -- opcje `definePluginEntry`
- [Elementy wewnętrzne Pluginu](/pl/plugins/architecture) -- model możliwości i rejestr
