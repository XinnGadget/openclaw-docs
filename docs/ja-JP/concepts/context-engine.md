---
read_when:
    - OpenClaw がどのようにモデルコンテキストを組み立てるかを理解したい
    - レガシーエンジンとプラグインエンジンを切り替えている
    - コンテキストエンジンプラグインを構築している
summary: 'コンテキストエンジン: プラグ可能なコンテキスト組み立て、圧縮、サブエージェントのライフサイクル'
title: コンテキストエンジン
x-i18n:
    generated_at: "2026-04-08T02:14:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: e8290ac73272eee275bce8e481ac7959b65386752caa68044d0c6f3e450acfb1
    source_path: concepts/context-engine.md
    workflow: 15
---

# コンテキストエンジン

**コンテキストエンジン** は、OpenClaw が各実行でどのようにモデルコンテキストを構築するかを制御します。
どのメッセージを含めるか、古い履歴をどのように要約するか、そして
サブエージェント境界をまたいでコンテキストをどのように管理するかを決定します。

OpenClaw には組み込みの `legacy` エンジンが付属しています。プラグインは、
アクティブなコンテキストエンジンのライフサイクルを置き換える代替エンジンを登録できます。

## クイックスタート

どのエンジンがアクティブかを確認します。

```bash
openclaw doctor
# or inspect config directly:
cat ~/.openclaw/openclaw.json | jq '.plugins.slots.contextEngine'
```

### コンテキストエンジンプラグインのインストール

コンテキストエンジンプラグインは、他の OpenClaw プラグインと同じようにインストールします。まずインストールしてから、
スロットでエンジンを選択します。

```bash
# Install from npm
openclaw plugins install @martian-engineering/lossless-claw

# Or install from a local path (for development)
openclaw plugins install -l ./my-context-engine
```

その後、プラグインを有効にして、設定でそれをアクティブなエンジンとして選択します。

```json5
// openclaw.json
{
  plugins: {
    slots: {
      contextEngine: "lossless-claw", // must match the plugin's registered engine id
    },
    entries: {
      "lossless-claw": {
        enabled: true,
        // Plugin-specific config goes here (see the plugin's docs)
      },
    },
  },
}
```

インストールと設定の後で Gateway を再起動します。

組み込みエンジンに戻すには、`contextEngine` を `"legacy"` に設定します（または
キーを完全に削除します — `"legacy"` がデフォルトです）。

## 仕組み

OpenClaw がモデルプロンプトを実行するたびに、コンテキストエンジンは
4 つのライフサイクルポイントに関与します。

1. **Ingest** — 新しいメッセージがセッションに追加されたときに呼び出されます。エンジンは
   自身のデータストアにメッセージを保存またはインデックス化できます。
2. **Assemble** — 各モデル実行の前に呼び出されます。エンジンは、
   トークン予算内に収まる順序付きのメッセージセット（およびオプションの `systemPromptAddition`）を返します。
3. **Compact** — コンテキストウィンドウがいっぱいになったとき、またはユーザーが
   `/compact` を実行したときに呼び出されます。エンジンは古い履歴を要約して空きを作ります。
4. **After turn** — 実行完了後に呼び出されます。エンジンは状態を永続化したり、
   バックグラウンド圧縮をトリガーしたり、インデックスを更新したりできます。

### サブエージェントのライフサイクル（任意）

OpenClaw は現在、1 つのサブエージェントライフサイクルフックを呼び出します。

- **onSubagentEnded** — サブエージェントセッションが完了したとき、または掃除されたときにクリーンアップします。

`prepareSubagentSpawn` フックは将来の用途のためにインターフェースの一部ですが、
ランタイムはまだそれを呼び出しません。

### システムプロンプト追加

`assemble` メソッドは `systemPromptAddition` 文字列を返すことができます。OpenClaw は
これを実行時のシステムプロンプトの先頭に追加します。これによりエンジンは、
静的なワークスペースファイルを必要とせずに、動的な想起ガイダンス、
検索指示、またはコンテキスト対応のヒントを注入できます。

## レガシーエンジン

組み込みの `legacy` エンジンは、OpenClaw の元の動作を維持します。

- **Ingest**: no-op（セッションマネージャーがメッセージ永続化を直接処理します）。
- **Assemble**: pass-through（ランタイム内の既存の sanitize → validate → limit パイプラインが
  コンテキスト組み立てを処理します）。
- **Compact**: 組み込みの要約圧縮に委譲されます。これは
  古いメッセージの単一の要約を作成し、最近のメッセージはそのまま保持します。
- **After turn**: no-op。

レガシーエンジンはツールを登録せず、`systemPromptAddition` も提供しません。

`plugins.slots.contextEngine` が設定されていない場合（または `"legacy"` に設定されている場合）は、
このエンジンが自動的に使われます。

## プラグインエンジン

プラグインは、プラグイン API を使ってコンテキストエンジンを登録できます。

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function register(api) {
  api.registerContextEngine("my-engine", () => ({
    info: {
      id: "my-engine",
      name: "My Context Engine",
      ownsCompaction: true,
    },

    async ingest({ sessionId, message, isHeartbeat }) {
      // Store the message in your data store
      return { ingested: true };
    },

    async assemble({ sessionId, messages, tokenBudget, availableTools, citationsMode }) {
      // Return messages that fit the budget
      return {
        messages: buildContext(messages, tokenBudget),
        estimatedTokens: countTokens(messages),
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },

    async compact({ sessionId, force }) {
      // Summarize older context
      return { ok: true, compacted: true };
    },
  }));
}
```

その後、設定で有効にします。

```json5
{
  plugins: {
    slots: {
      contextEngine: "my-engine",
    },
    entries: {
      "my-engine": {
        enabled: true,
      },
    },
  },
}
```

### ContextEngine インターフェース

必須メンバー:

| Member             | Kind     | Purpose                                                  |
| ------------------ | -------- | -------------------------------------------------------- |
| `info`             | Property | エンジン ID、名前、バージョン、および圧縮を所有するかどうか |
| `ingest(params)`   | Method   | 単一のメッセージを保存する                                   |
| `assemble(params)` | Method   | モデル実行用のコンテキストを構築する（`AssembleResult` を返す） |
| `compact(params)`  | Method   | コンテキストを要約・削減する                                 |

`assemble` は、次を含む `AssembleResult` を返します。

- `messages` — モデルに送信する順序付きメッセージ。
- `estimatedTokens`（必須、`number`）— 組み立てられたコンテキスト内の合計
  トークン数に対するエンジンの推定値。OpenClaw はこれを圧縮しきい値の
  判定と診断レポートに使用します。
- `systemPromptAddition`（任意、`string`）— システムプロンプトの先頭に追加されます。

任意メンバー:

| Member                         | Kind   | Purpose                                                                                                         |
| ------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------- |
| `bootstrap(params)`            | Method | セッション用のエンジン状態を初期化する。エンジンがセッションを初めて認識したときに 1 回呼び出されます（例: 履歴のインポート）。 |
| `ingestBatch(params)`          | Method | 完了したターンをバッチとして取り込む。実行完了後、そのターンのすべてのメッセージをまとめて呼び出されます。     |
| `afterTurn(params)`            | Method | 実行後のライフサイクル処理（状態の永続化、バックグラウンド圧縮のトリガー）。                                         |
| `prepareSubagentSpawn(params)` | Method | 子セッション用の共有状態をセットアップする。                                                                        |
| `onSubagentEnded(params)`      | Method | サブエージェント終了後にクリーンアップする。                                                                                 |
| `dispose()`                    | Method | リソースを解放する。Gateway のシャットダウン時またはプラグイン再読み込み時に呼び出され、セッションごとではありません。                           |

### ownsCompaction

`ownsCompaction` は、Pi の組み込みの試行中自動圧縮を実行時に
有効のままにするかどうかを制御します。

- `true` — エンジンが圧縮動作を所有します。OpenClaw はその実行について Pi の組み込み
  自動圧縮を無効にし、エンジンの `compact()` 実装が `/compact`、オーバーフロー回復圧縮、
  および `afterTurn()` で実行したい任意の積極的な
  圧縮を担当します。
- `false` または未設定 — Pi の組み込み自動圧縮は、プロンプト
  実行中に引き続き動作する可能性がありますが、アクティブなエンジンの `compact()` メソッドは
  `/compact` とオーバーフロー回復のために引き続き呼び出されます。

`ownsCompaction: false` は、OpenClaw が自動的に
レガシーエンジンの圧縮パスにフォールバックすることを意味する **わけではありません**。

つまり、有効なプラグインパターンは 2 つあります。

- **Owning mode** — 独自の圧縮アルゴリズムを実装し、
  `ownsCompaction: true` を設定します。
- **Delegating mode** — `ownsCompaction: false` を設定し、`compact()` で
  `openclaw/plugin-sdk/core` の `delegateCompactionToRuntime(...)` を呼び出して
  OpenClaw の組み込み圧縮動作を使用します。

アクティブな非所有エンジンで no-op の `compact()` を使うのは安全ではありません。これは
そのエンジンスロットに対する通常の `/compact` とオーバーフロー回復圧縮パスを
無効にしてしまうためです。

## 設定リファレンス

```json5
{
  plugins: {
    slots: {
      // Select the active context engine. Default: "legacy".
      // Set to a plugin id to use a plugin engine.
      contextEngine: "legacy",
    },
  },
}
```

このスロットは実行時に排他的です — 登録されたコンテキストエンジンは 1 つだけが
特定の実行または圧縮処理のために解決されます。他の有効な
`kind: "context-engine"` プラグインも引き続きロードされ、その登録
コードを実行できます。`plugins.slots.contextEngine` は、登録されたどのエンジン ID を
OpenClaw がコンテキストエンジンを必要とするときに解決するかを選択するだけです。

## 圧縮とメモリとの関係

- **圧縮** は、コンテキストエンジンの責務の 1 つです。レガシーエンジンは
  OpenClaw の組み込み要約に委譲します。プラグインエンジンは
  任意の圧縮戦略（DAG 要約、ベクトル検索など）を実装できます。
- **メモリプラグイン**（`plugins.slots.memory`）は、コンテキストエンジンとは別です。
  メモリプラグインは検索・取得を提供し、コンテキストエンジンは
  モデルが何を見るかを制御します。両者は連携できます — コンテキストエンジンは
  組み立て中にメモリプラグインのデータを使う場合があります。アクティブなメモリ
  プロンプトパスを使いたいプラグインエンジンは、`openclaw/plugin-sdk/core` の
  `buildMemorySystemPromptAddition(...)` を優先して使うべきです。これはアクティブなメモリプロンプトセクションを
  そのまま先頭追加できる `systemPromptAddition` に変換します。エンジンがより低レベルの
  制御を必要とする場合は、
  `openclaw/plugin-sdk/memory-host-core` の
  `buildActiveMemoryPromptSection(...)` を通じて生の行を取得することもできます。
- **セッションの剪定**（古いツール結果をメモリ内でトリミングすること）は、
  どのコンテキストエンジンがアクティブであっても引き続き実行されます。

## ヒント

- エンジンが正しくロードされていることを確認するには `openclaw doctor` を使います。
- エンジンを切り替えた場合でも、既存のセッションは現在の履歴を維持します。
  新しいエンジンは今後の実行に対して引き継ぎます。
- エンジンエラーはログに記録され、診断にも表示されます。プラグインエンジンが
  登録に失敗した場合、または選択されたエンジン ID を解決できない場合、OpenClaw
  は自動的にはフォールバックしません。プラグインを修正するか、
  `plugins.slots.contextEngine` を `"legacy"` に戻すまで実行は失敗します。
- 開発時には、`openclaw plugins install -l ./my-engine` を使って、
  ローカルプラグインディレクトリをコピーせずにリンクします。

関連項目: [圧縮](/ja-JP/concepts/compaction)、[コンテキスト](/ja-JP/concepts/context)、
[プラグイン](/ja-JP/tools/plugin)、[プラグインマニフェスト](/ja-JP/plugins/manifest)。

## 関連

- [コンテキスト](/ja-JP/concepts/context) — エージェントのターン向けにコンテキストがどのように構築されるか
- [プラグインアーキテクチャ](/ja-JP/plugins/architecture) — コンテキストエンジンプラグインの登録
- [圧縮](/ja-JP/concepts/compaction) — 長い会話の要約
