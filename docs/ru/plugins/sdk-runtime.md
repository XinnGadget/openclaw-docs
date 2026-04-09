---
title: "Вспомогательные средства выполнения плагинов"
sidebarTitle: "Вспомогательные средства выполнения"
summary: "api.runtime — внедряемые вспомогательные средства выполнения, доступные плагинам"
read_when:
  - Вам нужно вызвать основные вспомогательные средства из плагина (TTS, STT, генерация изображений, веб-поиск, субагент)
  - Вы хотите понять, что предоставляет api.runtime
  - Вы обращаетесь к вспомогательным средствам конфигурации, агента или мультимедиа из кода плагина
---

# Вспомогательные средства выполнения плагинов

Справочник по объекту `api.runtime`, внедряемому в каждый плагин во время регистрации. Используйте эти вспомогательные средства вместо прямого импорта внутренних компонентов хоста.

<Tip>
  **Ищете пошаговое руководство?** Ознакомьтесь с разделами [Плагины каналов](/plugins/sdk-channel-plugins) или [Плагины провайдеров](/plugins/sdk-provider-plugins) — там есть пошаговые инструкции, демонстрирующие использование этих вспомогательных средств в контексте.
</Tip>

```typescript
register(api) {
  const runtime = api.runtime;
}
```

## Пространства имён выполнения

### `api.runtime.agent`

Идентификация агента, каталоги и управление сессиями.

```typescript
// Определить рабочий каталог агента
const agentDir = api.runtime.agent.resolveAgentDir(cfg);

// Определить рабочее пространство агента
const workspaceDir = api.runtime.agent.resolveAgentWorkspaceDir(cfg);

// Получить идентификацию агента
const identity = api.runtime.agent.resolveAgentIdentity(cfg);

// Получить уровень мышления по умолчанию
const thinking = api.runtime.agent.resolveThinkingDefault(cfg, provider, model);

// Получить тайм-аут агента
const timeoutMs = api.runtime.agent.resolveAgentTimeoutMs(cfg);

// Убедиться, что рабочее пространство существует
await api.runtime.agent.ensureAgentWorkspace(cfg);

// Запустить встроенный агент Pi
const agentDir = api.runtime.agent.resolveAgentDir(cfg);
const result = await api.runtime.agent.runEmbeddedPiAgent({
  sessionId: "my-plugin:task-1",
  runId: crypto.randomUUID(),
  sessionFile: path.join(agentDir, "sessions", "my-plugin-task-1.jsonl"),
  workspaceDir: api.runtime.agent.resolveAgentWorkspaceDir(cfg),
  prompt: "Summarize the latest changes",
  timeoutMs: api.runtime.agent.resolveAgentTimeoutMs(cfg),
});
```

**Вспомогательные средства хранилища сессий** находятся в `api.runtime.agent.session`:

```typescript
const storePath = api.runtime.agent.session.resolveStorePath(cfg);
const store = api.runtime.agent.session.loadSessionStore(cfg);
await api.runtime.agent.session.saveSessionStore(cfg, store);
const filePath = api.runtime.agent.session.resolveSessionFilePath(cfg, sessionId);
```

### `api.runtime.agent.defaults`

Константы модели и провайдера по умолчанию:

```typescript
const model = api.runtime.agent.defaults.model; // например, "anthropic/claude-sonnet-4-6"
const provider = api.runtime.agent.defaults.provider; // например, "anthropic"
```

### `api.runtime.subagent`

Запуск и управление фоновыми запусками субагентов.

```typescript
// Запустить выполнение субагента
const { runId } = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai", // необязательная переопределяющая настройка
  model: "gpt-4.1-mini", // необязательная переопределяющая настройка
  deliver: false,
});

// Дождаться завершения
const result = await api.runtime.subagent.waitForRun({ runId, timeoutMs: 30000 });

// Прочитать сообщения сессии
const { messages } = await api.runtime.subagent.getSessionMessages({
  sessionKey: "agent:main:subagent:search-helper",
  limit: 10,
});

// Удалить сессию
await api.runtime.subagent.deleteSession({
  sessionKey: "agent:main:subagent:search-helper",
});
```

<Warning>
  Для переопределения модели (`provider`/`model`) требуется согласие оператора через параметр `plugins.entries.<id>.subagent.allowModelOverride: true` в конфигурации.
  Ненадёжные плагины могут запускать субагенты, но запросы на переопределение будут отклонены.
</Warning>

### `api.runtime.taskFlow`

Привязать среду выполнения Task Flow к существующему ключу сессии OpenClaw или доверенному контексту инструмента, затем создавать и управлять Task Flow без передачи владельца при каждом вызове.

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

Используйте `bindSession({ sessionKey, requesterOrigin })` , если у вас уже есть доверенный ключ сессии OpenClaw из вашего собственного слоя привязки. Не выполняйте привязку на основе необработанных пользовательских данных.

### `api.runtime.tts`

Синтез речи из текста.

```typescript
// Стандартный TTS
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

// TTS, оптимизированный для телефонии
const telephonyClip = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

// Получить список доступных голосов
const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Использует основную конфигурацию `messages.tts` и выбор провайдера. Возвращает буфер аудио PCM и частоту дискретизации.

### `api.runtime.mediaUnderstanding`

Анализ изображений, аудио и видео.

```typescript
// Описать изображение
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

// Транскрибировать аудио
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  mime: "audio/ogg", // необязательно, если MIME нельзя определить
});

// Описать видео
const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});

// Общий анализ файла
const result = await api.runtime.mediaUnderstanding.runFile({
  filePath: "/tmp/inbound-file.pdf",
  cfg: api.config,
});
```

Возвращает `{ text: undefined }`, если вывод не сформирован (например, входные данные пропущены).

<Info>
  `api.runtime.stt.transcribeAudioFile(...)` остаётся как псевдоним совместимости для `api.runtime.mediaUnderstanding.transcribeAudioFile(...)`.
</Info>

### `api.runtime.imageGeneration`

Генерация изображений.

```typescript
const result = await api.runtime.imageGeneration.generate({
  prompt: "A robot painting a sunset",
  cfg: api.config,
});

const providers = api.runtime.imageGeneration.listProviders({ cfg: api.config });
```

### `api.runtime.webSearch`

Веб-поиск.

```typescript
const providers = api.runtime.webSearch.listProviders({ config: api.config });

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: { query: "OpenClaw plugin SDK", count: 5 },
});
```

### `api.runtime.media`

Низкоуровневые утилиты для