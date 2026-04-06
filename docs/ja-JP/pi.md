---
read_when:
    - OpenClawにおけるPi SDK統合設計を理解するとき
    - Piのエージェントセッションライフサイクル、tooling、またはprovider配線を変更するとき
summary: OpenClawの埋め込みPiエージェント統合のアーキテクチャとセッションライフサイクル
title: Pi統合アーキテクチャ
x-i18n:
    generated_at: "2026-04-06T03:09:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 28594290b018b7cc2963d33dbb7cec6a0bd817ac486dafad59dd2ccabd482582
    source_path: pi.md
    workflow: 15
---

# Pi統合アーキテクチャ

このドキュメントでは、OpenClawが [pi-coding-agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) とその兄弟パッケージ（`pi-ai`、`pi-agent-core`、`pi-tui`）をどのように統合し、AIエージェント機能を実現しているかを説明します。

## 概要

OpenClawはpi SDKを使用して、AIコーディングエージェントをそのメッセージングGatewayアーキテクチャに埋め込んでいます。piをサブプロセスとして起動したりRPCモードを使用したりする代わりに、OpenClawは `createAgentSession()` を通じてpiの `AgentSession` を直接importしてインスタンス化します。この埋め込み方式により、次の利点が得られます。

- セッションライフサイクルとイベント処理を完全に制御できる
- カスタムツール注入（メッセージング、sandbox、チャンネル固有アクション）
- チャンネル/コンテキストごとのシステムプロンプトカスタマイズ
- 分岐/コンパクション対応のセッション永続化
- フェイルオーバー付きマルチアカウント認証プロファイルローテーション
- providerに依存しないモデル切り替え

## パッケージ依存関係

```json
{
  "@mariozechner/pi-agent-core": "0.64.0",
  "@mariozechner/pi-ai": "0.64.0",
  "@mariozechner/pi-coding-agent": "0.64.0",
  "@mariozechner/pi-tui": "0.64.0"
}
```

| Package           | 目的 |
| ----------------- | ---- |
| `pi-ai`           | コアLLM抽象化: `Model`、`streamSimple`、メッセージ型、provider API |
| `pi-agent-core`   | エージェントループ、tool実行、`AgentMessage` 型 |
| `pi-coding-agent` | 高レベルSDK: `createAgentSession`、`SessionManager`、`AuthStorage`、`ModelRegistry`、組み込みツール |
| `pi-tui`          | ターミナルUIコンポーネント（OpenClawのローカルTUIモードで使用） |

## ファイル構成

```
src/agents/
├── pi-embedded-runner.ts          # pi-embedded-runner/ から再エクスポート
├── pi-embedded-runner/
│   ├── run.ts                     # メインエントリ: runEmbeddedPiAgent()
│   ├── run/
│   │   ├── attempt.ts             # セッションセットアップを含む単一試行ロジック
│   │   ├── params.ts              # RunEmbeddedPiAgentParams 型
│   │   ├── payloads.ts            # 実行結果から応答ペイロードを構築
│   │   ├── images.ts              # Vision model 画像注入
│   │   └── types.ts               # EmbeddedRunAttemptResult
│   ├── abort.ts                   # 中断エラー検出
│   ├── cache-ttl.ts               # コンテキスト剪定のためのキャッシュTTL追跡
│   ├── compact.ts                 # 手動/自動コンパクションロジック
│   ├── extensions.ts              # 埋め込み実行用のpi拡張を読み込む
│   ├── extra-params.ts            # provider固有のstreamパラメータ
│   ├── google.ts                  # Google/Geminiのターン順序修正
│   ├── history.ts                 # 履歴制限（DM対グループ）
│   ├── lanes.ts                   # セッション/グローバルコマンドレーン
│   ├── logger.ts                  # サブシステムロガー
│   ├── model.ts                   # ModelRegistry経由のモデル解決
│   ├── runs.ts                    # アクティブ実行追跡、中断、キュー
│   ├── sandbox-info.ts            # システムプロンプト用のsandbox情報
│   ├── session-manager-cache.ts   # SessionManagerインスタンスキャッシュ
│   ├── session-manager-init.ts    # セッションファイル初期化
│   ├── system-prompt.ts           # システムプロンプトビルダー
│   ├── tool-split.ts              # ツールを builtIn と custom に分割
│   ├── types.ts                   # EmbeddedPiAgentMeta, EmbeddedPiRunResult
│   └── utils.ts                   # ThinkLevelマッピング、エラー説明
├── pi-embedded-subscribe.ts       # セッションイベント購読/配送
├── pi-embedded-subscribe.types.ts # SubscribeEmbeddedPiSessionParams
├── pi-embedded-subscribe.handlers.ts # イベントハンドラーファクトリー
├── pi-embedded-subscribe.handlers.lifecycle.ts
├── pi-embedded-subscribe.handlers.types.ts
├── pi-embedded-block-chunker.ts   # ストリーミングブロック返信チャンク化
├── pi-embedded-messaging.ts       # メッセージングツール送信追跡
├── pi-embedded-helpers.ts         # エラー分類、ターン検証
├── pi-embedded-helpers/           # ヘルパーモジュール
├── pi-embedded-utils.ts           # 整形ユーティリティ
├── pi-tools.ts                    # createOpenClawCodingTools()
├── pi-tools.abort.ts              # tool用AbortSignalラッピング
├── pi-tools.policy.ts             # ツール許可/拒否リストポリシー
├── pi-tools.read.ts               # 読み取りツールのカスタマイズ
├── pi-tools.schema.ts             # ツールスキーマ正規化
├── pi-tools.types.ts              # AnyAgentTool 型エイリアス
├── pi-tool-definition-adapter.ts  # AgentTool -> ToolDefinition アダプター
├── pi-settings.ts                 # 設定上書き
├── pi-hooks/                      # カスタムpiフック
│   ├── compaction-safeguard.ts    # セーフガード拡張
│   ├── compaction-safeguard-runtime.ts
│   ├── context-pruning.ts         # キャッシュTTLベースのコンテキスト剪定拡張
│   └── context-pruning/
├── model-auth.ts                  # 認証プロファイル解決
├── auth-profiles.ts               # プロファイルストア、クールダウン、フェイルオーバー
├── model-selection.ts             # デフォルトモデル解決
├── models-config.ts               # models.json 生成
├── model-catalog.ts               # モデルカタログキャッシュ
├── context-window-guard.ts        # コンテキストウィンドウ検証
├── failover-error.ts              # FailoverError クラス
├── defaults.ts                    # DEFAULT_PROVIDER, DEFAULT_MODEL
├── system-prompt.ts               # buildAgentSystemPrompt()
├── system-prompt-params.ts        # システムプロンプトパラメータ解決
├── system-prompt-report.ts        # デバッグレポート生成
├── tool-summaries.ts              # ツール説明サマリー
├── tool-policy.ts                 # ツールポリシー解決
├── transcript-policy.ts           # Transcript検証ポリシー
├── skills.ts                      # Skillsスナップショット/プロンプト構築
├── skills/                        # Skillsサブシステム
├── sandbox.ts                     # Sandboxコンテキスト解決
├── sandbox/                       # Sandboxサブシステム
├── channel-tools.ts               # チャンネル固有ツール注入
├── openclaw-tools.ts              # OpenClaw固有ツール
├── bash-tools.ts                  # exec/process ツール
├── apply-patch.ts                 # apply_patch ツール（OpenAI）
├── tools/                         # 個別ツール実装
│   ├── browser-tool.ts
│   ├── canvas-tool.ts
│   ├── cron-tool.ts
│   ├── gateway-tool.ts
│   ├── image-tool.ts
│   ├── message-tool.ts
│   ├── nodes-tool.ts
│   ├── session*.ts
│   ├── web-*.ts
│   └── ...
└── ...
```

チャンネル固有のメッセージアクションランタイムは、現在 `src/agents/tools` 配下ではなく、プラグイン所有の拡張ディレクトリにあります。たとえば次のものです。

- Discordプラグインのアクションランタイムファイル
- Slackプラグインのアクションランタイムファイル
- Telegramプラグインのアクションランタイムファイル
- WhatsAppプラグインのアクションランタイムファイル

## コア統合フロー

### 1. 埋め込みエージェントの実行

メインエントリポイントは `pi-embedded-runner/run.ts` の `runEmbeddedPiAgent()` です。

```typescript
import { runEmbeddedPiAgent } from "./agents/pi-embedded-runner.js";

const result = await runEmbeddedPiAgent({
  sessionId: "user-123",
  sessionKey: "main:whatsapp:+1234567890",
  sessionFile: "/path/to/session.jsonl",
  workspaceDir: "/path/to/workspace",
  config: openclawConfig,
  prompt: "Hello, how are you?",
  provider: "anthropic",
  model: "claude-sonnet-4-6",
  timeoutMs: 120_000,
  runId: "run-abc",
  onBlockReply: async (payload) => {
    await sendToChannel(payload.text, payload.mediaUrls);
  },
});
```

### 2. セッション作成

`runEmbeddedAttempt()`（`runEmbeddedPiAgent()` から呼び出される）内部では、pi SDKが使用されます。

```typescript
import {
  createAgentSession,
  DefaultResourceLoader,
  SessionManager,
  SettingsManager,
} from "@mariozechner/pi-coding-agent";

const resourceLoader = new DefaultResourceLoader({
  cwd: resolvedWorkspace,
  agentDir,
  settingsManager,
  additionalExtensionPaths,
});
await resourceLoader.reload();

const { session } = await createAgentSession({
  cwd: resolvedWorkspace,
  agentDir,
  authStorage: params.authStorage,
  modelRegistry: params.modelRegistry,
  model: params.model,
  thinkingLevel: mapThinkingLevel(params.thinkLevel),
  tools: builtInTools,
  customTools: allCustomTools,
  sessionManager,
  settingsManager,
  resourceLoader,
});

applySystemPromptOverrideToSession(session, systemPromptOverride);
```

### 3. イベント購読

`subscribeEmbeddedPiSession()` はpiの `AgentSession` イベントを購読します。

```typescript
const subscription = subscribeEmbeddedPiSession({
  session: activeSession,
  runId: params.runId,
  verboseLevel: params.verboseLevel,
  reasoningMode: params.reasoningLevel,
  toolResultFormat: params.toolResultFormat,
  onToolResult: params.onToolResult,
  onReasoningStream: params.onReasoningStream,
  onBlockReply: params.onBlockReply,
  onPartialReply: params.onPartialReply,
  onAgentEvent: params.onAgentEvent,
});
```

処理されるイベントには次のものがあります。

- `message_start` / `message_end` / `message_update`（ストリーミングテキスト/思考）
- `tool_execution_start` / `tool_execution_update` / `tool_execution_end`
- `turn_start` / `turn_end`
- `agent_start` / `agent_end`
- `auto_compaction_start` / `auto_compaction_end`

### 4. プロンプト送信

セットアップ後、セッションにプロンプトを送ります。

```typescript
await session.prompt(effectivePrompt, { images: imageResult.images });
```

SDKは、LLMへの送信、tool callの実行、応答ストリーミングを含むエージェントループ全体を処理します。

画像注入はプロンプトローカルです。OpenClawは現在のプロンプトから画像参照を読み込み、そのターンに対してのみ `images` 経由で渡します。古い履歴ターンを再走査して画像ペイロードを再注入することはありません。

## ツールアーキテクチャ

### ツールパイプライン

1. **ベースツール**: piの `codingTools`（read, bash, edit, write）
2. **カスタム置き換え**: OpenClawはbashを `exec`/`process` に置き換え、sandbox向けにread/edit/writeをカスタマイズ
3. **OpenClawツール**: messaging、browser、canvas、sessions、cron、gateway など
4. **チャンネルツール**: Discord/Telegram/Slack/WhatsApp 固有アクションツール
5. **ポリシーフィルタリング**: ツールをprofile、provider、agent、group、sandbox ポリシーでフィルタリング
6. **スキーマ正規化**: Gemini/OpenAIの癖に合わせてスキーマをクリーンアップ
7. **AbortSignalラッピング**: toolがabort signalを尊重するようラップ

### ツール定義アダプター

pi-agent-core の `AgentTool` は、pi-coding-agent の `ToolDefinition` と異なる `execute` シグネチャを持ちます。`pi-tool-definition-adapter.ts` のアダプターがこれを橋渡しします。

```typescript
export function toToolDefinitions(tools: AnyAgentTool[]): ToolDefinition[] {
  return tools.map((tool) => ({
    name: tool.name,
    label: tool.label ?? name,
    description: tool.description ?? "",
    parameters: tool.parameters,
    execute: async (toolCallId, params, onUpdate, _ctx, signal) => {
      // pi-coding-agent のシグネチャは pi-agent-core と異なる
      return await tool.execute(toolCallId, params, signal, onUpdate);
    },
  }));
}
```

### ツール分割戦略

`splitSdkTools()` はすべてのツールを `customTools` 経由で渡します。

```typescript
export function splitSdkTools(options: { tools: AnyAgentTool[]; sandboxEnabled: boolean }) {
  return {
    builtInTools: [], // 空。すべて上書きする
    customTools: toToolDefinitions(options.tools),
  };
}
```

これにより、OpenClawのポリシーフィルタリング、sandbox統合、拡張ツールセットがprovider間で一貫したまま保たれます。

## システムプロンプト構築

システムプロンプトは `buildAgentSystemPrompt()`（`system-prompt.ts`）で構築されます。Tooling、Tool Call Style、安全ガードレール、OpenClaw CLIリファレンス、Skills、Docs、Workspace、Sandbox、Messaging、Reply Tags、Voice、Silent Replies、Heartbeats、Runtime metadata、さらに有効時には Memory と Reactions、および任意のコンテキストファイルと追加システムプロンプト内容を含む完全なプロンプトを組み立てます。サブエージェントで使われる最小プロンプトモード用にはセクションが削減されます。

プロンプトは、セッション作成後に `applySystemPromptOverrideToSession()` を通じて適用されます。

```typescript
const systemPromptOverride = createSystemPromptOverride(appendPrompt);
applySystemPromptOverrideToSession(session, systemPromptOverride);
```

## セッション管理

### セッションファイル

セッションはツリー構造（id/parentIdリンク）を持つJSONLファイルです。piの `SessionManager` が永続化を処理します。

```typescript
const sessionManager = SessionManager.open(params.sessionFile);
```

OpenClawはこれを `guardSessionManager()` でラップし、tool結果の安全性を高めています。

### セッションキャッシュ

`session-manager-cache.ts` は、繰り返しのファイル解析を避けるために SessionManager インスタンスをキャッシュします。

```typescript
await prewarmSessionFile(params.sessionFile);
sessionManager = SessionManager.open(params.sessionFile);
trackSessionManagerAccess(params.sessionFile);
```

### 履歴制限

`limitHistoryTurns()` は、チャンネル種別（DM対グループ）に基づいて会話履歴をトリミングします。

### コンパクション

自動コンパクションはコンテキストあふれ時に起動します。一般的なオーバーフローのシグネチャには、
`request_too_large`、`context length exceeded`、`input exceeds the
maximum number of tokens`、`input token count exceeds the maximum number of
input tokens`、`input is too long for the model`、`ollama error: context
length exceeded` が含まれます。`compactEmbeddedPiSessionDirect()` は手動コンパクションを処理します。

```typescript
const compactResult = await compactEmbeddedPiSessionDirect({
  sessionId, sessionFile, provider, model, ...
});
```

## 認証とモデル解決

### 認証プロファイル

OpenClawはproviderごとに複数APIキーを持つ認証プロファイルストアを維持します。

```typescript
const authStore = ensureAuthProfileStore(agentDir, { allowKeychainPrompt: false });
const profileOrder = resolveAuthProfileOrder({ cfg, store: authStore, provider, preferredProfile });
```

プロファイルは、クールダウントラッキング付きで失敗時にローテーションされます。

```typescript
await markAuthProfileFailure({ store, profileId, reason, cfg, agentDir });
const rotated = await advanceAuthProfile();
```

### モデル解決

```typescript
import { resolveModel } from "./pi-embedded-runner/model.js";

const { model, error, authStorage, modelRegistry } = resolveModel(
  provider,
  modelId,
  agentDir,
  config,
);

// piの ModelRegistry と AuthStorage を使用
authStorage.setRuntimeApiKey(model.provider, apiKeyInfo.apiKey);
```

### フェイルオーバー

`FailoverError` は、設定されている場合にモデルフォールバックを起動します。

```typescript
if (fallbackConfigured && isFailoverErrorMessage(errorText)) {
  throw new FailoverError(errorText, {
    reason: promptFailoverReason ?? "unknown",
    provider,
    model: modelId,
    profileId,
    status: resolveFailoverStatus(promptFailoverReason),
  });
}
```

## Pi拡張

OpenClawは特殊な動作のためにカスタムpi拡張を読み込みます。

### コンパクションセーフガード

`src/agents/pi-hooks/compaction-safeguard.ts` は、適応的トークン予算編成に加え、tool失敗とファイル操作サマリーを含むコンパクションガードレールを追加します。

```typescript
if (resolveCompactionMode(params.cfg) === "safeguard") {
  setCompactionSafeguardRuntime(params.sessionManager, { maxHistoryShare });
  paths.push(resolvePiExtensionPath("compaction-safeguard"));
}
```

### コンテキスト剪定

`src/agents/pi-hooks/context-pruning.ts` は、キャッシュTTLベースのコンテキスト剪定を実装します。

```typescript
if (cfg?.agents?.defaults?.contextPruning?.mode === "cache-ttl") {
  setContextPruningRuntime(params.sessionManager, {
    settings,
    contextWindowTokens,
    isToolPrunable,
    lastCacheTouchAt,
  });
  paths.push(resolvePiExtensionPath("context-pruning"));
}
```

## ストリーミングとブロック返信

### ブロックチャンク化

`EmbeddedBlockChunker` は、ストリーミングテキストを個別の返信ブロックに分割して管理します。

```typescript
const blockChunker = blockChunking ? new EmbeddedBlockChunker(blockChunking) : null;
```

### 思考/最終タグの除去

ストリーミング出力は、`<think>`/`<thinking>` ブロックを除去し、`<final>` 内容を抽出するよう処理されます。

```typescript
const stripBlockTags = (text: string, state: { thinking: boolean; final: boolean }) => {
  // <think>...</think> の内容を除去
  // enforceFinalTag の場合、<final>...</final> の内容だけを返す
};
```

### 返信ディレクティブ

`[[media:url]]`、`[[voice]]`、`[[reply:id]]` のような返信ディレクティブは解析され、抽出されます。

```typescript
const { text: cleanedText, mediaUrls, audioAsVoice, replyToId } = consumeReplyDirectives(chunk);
```

## エラー処理

### エラー分類

`pi-embedded-helpers.ts` は、適切に処理できるようエラーを分類します。

```typescript
isContextOverflowError(errorText)     // コンテキストが大きすぎる
isCompactionFailureError(errorText)   // コンパクション失敗
isAuthAssistantError(lastAssistant)   // 認証失敗
isRateLimitAssistantError(...)        // レート制限
isFailoverAssistantError(...)         // フェイルオーバーすべき
classifyFailoverReason(errorText)     // "auth" | "rate_limit" | "quota" | "timeout" | ...
```

### 思考レベルのフォールバック

思考レベルがサポートされていない場合はフォールバックします。

```typescript
const fallbackThinking = pickFallbackThinkingLevel({
  message: errorText,
  attempted: attemptedThinking,
});
if (fallbackThinking) {
  thinkLevel = fallbackThinking;
  continue;
}
```

## Sandbox統合

sandboxモードが有効な場合、ツールとパスは制約されます。

```typescript
const sandbox = await resolveSandboxContext({
  config: params.config,
  sessionKey: sandboxSessionKey,
  workspaceDir: resolvedWorkspace,
});

if (sandboxRoot) {
  // sandbox化された read/edit/write ツールを使用
  // Exec はコンテナ内で実行
  // Browser はブリッジURLを使用
}
```

## Provider固有の処理

### Anthropic

- 拒否マジック文字列の除去
- 連続ロールに対するターン検証
- 厳格な上流Piツールパラメータ検証

### Google/Gemini

- プラグイン所有のツールスキーマサニタイズ

### OpenAI

- Codexモデル用の `apply_patch` ツール
- 思考レベルのダウングレード処理

## TUI統合

OpenClawには、pi-tuiコンポーネントを直接使用するローカルTUIモードもあります。

```typescript
// src/tui/tui.ts
import { ... } from "@mariozechner/pi-tui";
```

これにより、piネイティブモードに近い対話型ターミナル体験を提供します。

## Pi CLIとの主な違い

| Aspect          | Pi CLI | OpenClaw Embedded |
| --------------- | ------ | ----------------- |
| Invocation      | `pi` コマンド / RPC | `createAgentSession()` 経由のSDK |
| Tools           | デフォルトのコーディングツール | カスタムOpenClawツールスイート |
| System prompt   | AGENTS.md + prompts | チャンネル/コンテキストごとの動的生成 |
| Session storage | `~/.pi/agent/sessions/` | `~/.openclaw/agents/<agentId>/sessions/`（または `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`） |
| Auth            | 単一の資格情報 | ローテーション付きマルチプロファイル |
| Extensions      | ディスクから読み込み | プログラム的 + ディスクパス |
| Event handling  | TUIレンダリング | コールバックベース（onBlockReply など） |

## 今後の検討事項

再設計の可能性がある領域:

1. **ツールシグネチャの整合**: 現在は pi-agent-core と pi-coding-agent のシグネチャ間を適応している
2. **Session manager ラッピング**: `guardSessionManager` は安全性を追加するが複雑さも増す
3. **拡張の読み込み**: piの `ResourceLoader` をより直接使える可能性がある
4. **ストリーミングハンドラーの複雑さ**: `subscribeEmbeddedPiSession` が大きくなっている
5. **providerの癖**: pi側で処理できる可能性のあるprovider固有コードパスが多い

## テスト

Pi統合のカバレッジは次のスイートにまたがっています。

- `src/agents/pi-*.test.ts`
- `src/agents/pi-auth-json.test.ts`
- `src/agents/pi-embedded-*.test.ts`
- `src/agents/pi-embedded-helpers*.test.ts`
- `src/agents/pi-embedded-runner*.test.ts`
- `src/agents/pi-embedded-runner/**/*.test.ts`
- `src/agents/pi-embedded-subscribe*.test.ts`
- `src/agents/pi-tools*.test.ts`
- `src/agents/pi-tool-definition-adapter*.test.ts`
- `src/agents/pi-settings.test.ts`
- `src/agents/pi-hooks/**/*.test.ts`

ライブ/オプトイン:

- `src/agents/pi-embedded-runner-extraparams.live.test.ts`（`OPENCLAW_LIVE_TEST=1` を有効化）

現在の実行コマンドについては、[Pi Development Workflow](/ja-JP/pi-dev) を参照してください。
