---
read_when:
    - Pluginからコアヘルパー（TTS、STT、画像生成、ウェブ検索、subagent）を呼び出す必要があります
    - '`api.runtime` が何を公開しているのかを理解したい'
    - Pluginコードから設定、agent、またはメディアヘルパーにアクセスしています
sidebarTitle: Runtime Helpers
summary: api.runtime -- Pluginで利用できる注入済みランタイムヘルパー
title: Pluginランタイムヘルパー
x-i18n:
    generated_at: "2026-04-15T19:41:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: c77a6e9cd48c84affa17dce684bbd0e072c8b63485e4a5d569f3793a4ea4f9c8
    source_path: plugins/sdk-runtime.md
    workflow: 15
---

# Pluginランタイムヘルパー

登録時にすべてのPluginへ注入される `api.runtime` オブジェクトのリファレンスです。
ホスト内部を直接 import する代わりに、これらのヘルパーを使用してください。

<Tip>
  **手順の説明を探していますか？** これらのヘルパーが実際の文脈でどのように使われるかを段階的に示したガイドは、[Channel Plugins](/ja-JP/plugins/sdk-channel-plugins)
  または [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) を参照してください。
</Tip>

```typescript
register(api) {
  const runtime = api.runtime;
}
```

## ランタイム名前空間

### `api.runtime.agent`

agentの識別情報、ディレクトリ、およびセッション管理。

```typescript
// agentの作業ディレクトリを解決
const agentDir = api.runtime.agent.resolveAgentDir(cfg);

// agentワークスペースを解決
const workspaceDir = api.runtime.agent.resolveAgentWorkspaceDir(cfg);

// agentの識別情報を取得
const identity = api.runtime.agent.resolveAgentIdentity(cfg);

// デフォルトの思考レベルを取得
const thinking = api.runtime.agent.resolveThinkingDefault(cfg, provider, model);

// agentのタイムアウトを取得
const timeoutMs = api.runtime.agent.resolveAgentTimeoutMs(cfg);

// ワークスペースが存在することを保証
await api.runtime.agent.ensureAgentWorkspace(cfg);

// 埋め込みagentターンを実行
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

`runEmbeddedAgent(...)` は、Pluginコードから通常のOpenClaw agentターンを開始するための中立的なヘルパーです。
これは、チャネルによってトリガーされる返信と同じプロバイダー/モデル解決およびagentハーネス選択を使用します。

`runEmbeddedPiAgent(...)` は、互換性のためのエイリアスとして残されています。

**セッションストアヘルパー** は `api.runtime.agent.session` 配下にあります。

```typescript
const storePath = api.runtime.agent.session.resolveStorePath(cfg);
const store = api.runtime.agent.session.loadSessionStore(cfg);
await api.runtime.agent.session.saveSessionStore(cfg, store);
const filePath = api.runtime.agent.session.resolveSessionFilePath(cfg, sessionId);
```

### `api.runtime.agent.defaults`

デフォルトのモデルおよびプロバイダー定数:

```typescript
const model = api.runtime.agent.defaults.model; // 例: "anthropic/claude-sonnet-4-6"
const provider = api.runtime.agent.defaults.provider; // 例: "anthropic"
```

### `api.runtime.subagent`

バックグラウンドsubagent実行を起動および管理します。

```typescript
// subagent実行を開始
const { runId } = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai", // オプションの上書き
  model: "gpt-4.1-mini", // オプションの上書き
  deliver: false,
});

// 完了を待機
const result = await api.runtime.subagent.waitForRun({ runId, timeoutMs: 30000 });

// セッションメッセージを読み取る
const { messages } = await api.runtime.subagent.getSessionMessages({
  sessionKey: "agent:main:subagent:search-helper",
  limit: 10,
});

// セッションを削除
await api.runtime.subagent.deleteSession({
  sessionKey: "agent:main:subagent:search-helper",
});
```

<Warning>
  モデル上書き（`provider`/`model`）には、設定の
  `plugins.entries.<id>.subagent.allowModelOverride: true` によるオペレーターのオプトインが必要です。
  信頼されていないPluginでもsubagentは実行できますが、上書きリクエストは拒否されます。
</Warning>

### `api.runtime.taskFlow`

TaskFlowランタイムを既存のOpenClawセッションキーまたは信頼されたツールコンテキストにバインドし、呼び出しごとに所有者を渡さずにTaskFlowを作成および管理します。

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

独自のバインディングレイヤーから取得した信頼済みのOpenClawセッションキーがすでにある場合は、`bindSession({ sessionKey, requesterOrigin })` を使用してください。生のユーザー入力からバインドしないでください。

### `api.runtime.tts`

テキスト読み上げ合成。

```typescript
// 標準TTS
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

// 電話向けに最適化されたTTS
const telephonyClip = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

// 利用可能な音声を一覧表示
const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

コアの `messages.tts` 設定とプロバイダー選択を使用します。PCM音声バッファーとサンプルレートを返します。

### `api.runtime.mediaUnderstanding`

画像、音声、および動画の解析。

```typescript
// 画像を説明
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

// 音声を文字起こし
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  mime: "audio/ogg", // MIMEを推定できない場合はオプション
});

// 動画を説明
const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});

// 汎用ファイル解析
const result = await api.runtime.mediaUnderstanding.runFile({
  filePath: "/tmp/inbound-file.pdf",
  cfg: api.config,
});
```

出力が生成されない場合（例: 入力がスキップされた場合）は、`{ text: undefined }` を返します。

<Info>
  `api.runtime.stt.transcribeAudioFile(...)` は、
  `api.runtime.mediaUnderstanding.transcribeAudioFile(...)` の互換性エイリアスとして残されています。
</Info>

### `api.runtime.imageGeneration`

画像生成。

```typescript
const result = await api.runtime.imageGeneration.generate({
  prompt: "A robot painting a sunset",
  cfg: api.config,
});

const providers = api.runtime.imageGeneration.listProviders({ cfg: api.config });
```

### `api.runtime.webSearch`

ウェブ検索。

```typescript
const providers = api.runtime.webSearch.listProviders({ config: api.config });

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: { query: "OpenClaw plugin SDK", count: 5 },
});
```

### `api.runtime.media`

低レベルのメディアユーティリティ。

```typescript
const webMedia = await api.runtime.media.loadWebMedia(url);
const mime = await api.runtime.media.detectMime(buffer);
const kind = api.runtime.media.mediaKindFromMime("image/jpeg"); // "image"
const isVoice = api.runtime.media.isVoiceCompatibleAudio(filePath);
const metadata = await api.runtime.media.getImageMetadata(filePath);
const resized = await api.runtime.media.resizeToJpeg(buffer, { maxWidth: 800 });
```

### `api.runtime.config`

設定の読み込みと書き込み。

```typescript
const cfg = await api.runtime.config.loadConfig();
await api.runtime.config.writeConfigFile(cfg);
```

### `api.runtime.system`

システムレベルのユーティリティ。

```typescript
await api.runtime.system.enqueueSystemEvent(event);
api.runtime.system.requestHeartbeatNow();
const output = await api.runtime.system.runCommandWithTimeout(cmd, args, opts);
const hint = api.runtime.system.formatNativeDependencyHint(pkg);
```

### `api.runtime.events`

イベント購読。

```typescript
api.runtime.events.onAgentEvent((event) => {
  /* ... */
});
api.runtime.events.onSessionTranscriptUpdate((update) => {
  /* ... */
});
```

### `api.runtime.logging`

ロギング。

```typescript
const verbose = api.runtime.logging.shouldLogVerbose();
const childLogger = api.runtime.logging.getChildLogger({ plugin: "my-plugin" }, { level: "debug" });
```

### `api.runtime.modelAuth`

モデルおよびプロバイダーの認証解決。

```typescript
const auth = await api.runtime.modelAuth.getApiKeyForModel({ model, cfg });
const providerAuth = await api.runtime.modelAuth.resolveApiKeyForProvider({
  provider: "openai",
  cfg,
});
```

### `api.runtime.state`

stateディレクトリの解決。

```typescript
const stateDir = api.runtime.state.resolveStateDir();
```

### `api.runtime.tools`

メモリツールファクトリーおよびCLI。

```typescript
const getTool = api.runtime.tools.createMemoryGetTool(/* ... */);
const searchTool = api.runtime.tools.createMemorySearchTool(/* ... */);
api.runtime.tools.registerMemoryCli(/* ... */);
```

### `api.runtime.channel`

チャネル固有のランタイムヘルパー（チャネルPluginが読み込まれている場合に利用可能）。

`api.runtime.channel.mentions` は、ランタイム注入を使用するバンドル済みチャネルPlugin向けの共有受信メンションポリシーサーフェスです。

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

利用可能なメンションヘルパー:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

`api.runtime.channel.mentions` は、意図的に古い
`resolveMentionGating*` 互換ヘルパーを公開していません。正規化された
`{ facts, policy }` パスを使用してください。

## ランタイム参照の保存

`register` コールバックの外で使用するためにランタイム参照を保存するには、`createPluginRuntimeStore` を使用します。

```typescript
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
import type { PluginRuntime } from "openclaw/plugin-sdk/runtime-store";

const store = createPluginRuntimeStore<PluginRuntime>({
  pluginId: "my-plugin",
  errorMessage: "my-plugin runtime not initialized",
});

// エントリーポイント内
export default defineChannelPluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Example",
  plugin: myPlugin,
  setRuntime: store.setRuntime,
});

// 他のファイル内
export function getRuntime() {
  return store.getRuntime(); // 初期化されていない場合は例外を投げる
}

export function tryGetRuntime() {
  return store.tryGetRuntime(); // 初期化されていない場合は null を返す
}
```

ランタイムストアの識別には `pluginId` を優先してください。より低レベルの `key` 形式は、1つのPluginが意図的に複数のランタイムスロットを必要とするまれなケース向けです。

## その他のトップレベル `api` フィールド

`api.runtime` に加えて、APIオブジェクトは次も提供します:

| フィールド | 型 | 説明 |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id` | `string` | Plugin id |
| `api.name` | `string` | Plugin表示名 |
| `api.config` | `OpenClawConfig` | 現在の設定スナップショット（利用可能な場合は、アクティブなインメモリランタイムスナップショット） |
| `api.pluginConfig` | `Record<string, unknown>` | `plugins.entries.<id>.config` から取得したPlugin固有の設定 |
| `api.logger` | `PluginLogger` | スコープ付きロガー（`debug`、`info`、`warn`、`error`） |
| `api.registrationMode` | `PluginRegistrationMode` | 現在のロードモード。`"setup-runtime"` は、完全なエントリー前の軽量な起動/セットアップ用ウィンドウです |
| `api.resolvePath(input)` | `(string) => string` | Pluginルートを基準に相対パスを解決 |

## 関連

- [SDK Overview](/ja-JP/plugins/sdk-overview) -- サブパスリファレンス
- [SDK Entry Points](/ja-JP/plugins/sdk-entrypoints) -- `definePluginEntry` オプション
- [Plugin Internals](/ja-JP/plugins/architecture) -- 機能モデルとレジストリ
