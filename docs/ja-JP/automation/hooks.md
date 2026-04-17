---
read_when:
    - /new、/reset、/stop、およびエージェントのライフサイクルイベントに対するイベント駆動型自動化が必要な場合
    - フックを構築、インストール、またはデバッグしたい場合
summary: 'フック: コマンドとライフサイクルイベントのためのイベント駆動型自動化'
title: フック
x-i18n:
    generated_at: "2026-04-11T02:44:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 14296398e4042d442ebdf071a07c6be99d4afda7cbf3c2b934e76dc5539742c7
    source_path: automation/hooks.md
    workflow: 15
---

# フック

フックは、Gateway内部で何かが起きたときに実行される小さなスクリプトです。ディレクトリから自動的に検出され、`openclaw hooks`で確認できます。

OpenClawには2種類のフックがあります。

- **内部フック**（このページ）: `/new`、`/reset`、`/stop`、またはライフサイクルイベントのようなエージェントイベントが発火したときにGateway内で実行されます。
- **Webhook**: 外部HTTPエンドポイントで、他のシステムがOpenClaw内の処理をトリガーできるようにします。[Webhook](/ja-JP/automation/cron-jobs#webhooks)を参照してください。

フックはプラグイン内に同梱することもできます。`openclaw hooks list`には、スタンドアロンのフックとプラグイン管理のフックの両方が表示されます。

## クイックスタート

```bash
# 利用可能なフックを一覧表示
openclaw hooks list

# フックを有効化
openclaw hooks enable session-memory

# フックの状態を確認
openclaw hooks check

# 詳細情報を取得
openclaw hooks info session-memory
```

## イベントタイプ

| イベント                 | 発火するタイミング                               |
| ------------------------ | ------------------------------------------------ |
| `command:new`            | `/new`コマンドが実行されたとき                   |
| `command:reset`          | `/reset`コマンドが実行されたとき                 |
| `command:stop`           | `/stop`コマンドが実行されたとき                  |
| `command`                | 任意のコマンドイベント（汎用リスナー）           |
| `session:compact:before` | compactが履歴を要約する前                        |
| `session:compact:after`  | compactの完了後                                  |
| `session:patch`          | セッションプロパティが変更されたとき             |
| `agent:bootstrap`        | ワークスペースのbootstrapファイルが注入される前  |
| `gateway:startup`        | チャンネル開始後、かつフックが読み込まれた後     |
| `message:received`       | 任意のチャンネルから受信メッセージが届いたとき   |
| `message:transcribed`    | 音声文字起こしが完了した後                       |
| `message:preprocessed`   | すべてのメディアとリンクの理解が完了した後       |
| `message:sent`           | 送信メッセージが配信されたとき                   |

## フックの作成

### フックの構成

各フックは2つのファイルを含むディレクトリです。

```
my-hook/
├── HOOK.md          # メタデータ + ドキュメント
└── handler.ts       # ハンドラー実装
```

### HOOK.md形式

```markdown
---
name: my-hook
description: "このフックが行うことの短い説明"
metadata:
  { "openclaw": { "emoji": "🔗", "events": ["command:new"], "requires": { "bins": ["node"] } } }
---

# My Hook

詳細なドキュメントをここに記述します。
```

**メタデータフィールド**（`metadata.openclaw`）:

| フィールド | 説明                                                 |
| ---------- | ---------------------------------------------------- |
| `emoji`    | CLIに表示する絵文字                                  |
| `events`   | 監視するイベントの配列                               |
| `export`   | 使用する名前付きエクスポート（デフォルトは`"default"`） |
| `os`       | 必要なプラットフォーム（例: `["darwin", "linux"]`）  |
| `requires` | 必要な`bins`、`anyBins`、`env`、または`config`パス   |
| `always`   | 適格性チェックをバイパスするかどうか（boolean）      |
| `install`  | インストール方法                                     |

### ハンドラー実装

```typescript
const handler = async (event) => {
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  console.log(`[my-hook] New command triggered`);
  // ここにロジックを記述

  // 必要に応じてユーザーにメッセージを送信
  event.messages.push("Hook executed!");
};

export default handler;
```

各イベントには`type`、`action`、`sessionKey`、`timestamp`、`messages`（ユーザー送信用にpush）、および`context`（イベント固有のデータ）が含まれます。

### イベントコンテキストの要点

**コマンドイベント**（`command:new`、`command:reset`）: `context.sessionEntry`、`context.previousSessionEntry`、`context.commandSource`、`context.workspaceDir`、`context.cfg`。

**メッセージイベント**（`message:received`）: `context.from`、`context.content`、`context.channelId`、`context.metadata`（`senderId`、`senderName`、`guildId`を含むプロバイダー固有データ）。

**メッセージイベント**（`message:sent`）: `context.to`、`context.content`、`context.success`、`context.channelId`。

**メッセージイベント**（`message:transcribed`）: `context.transcript`、`context.from`、`context.channelId`、`context.mediaPath`。

**メッセージイベント**（`message:preprocessed`）: `context.bodyForAgent`（最終的に拡張された本文）、`context.from`、`context.channelId`。

**Bootstrapイベント**（`agent:bootstrap`）: `context.bootstrapFiles`（変更可能な配列）、`context.agentId`。

**セッションパッチイベント**（`session:patch`）: `context.sessionEntry`、`context.patch`（変更されたフィールドのみ）、`context.cfg`。パッチイベントをトリガーできるのは特権クライアントのみです。

**Compactイベント**: `session:compact:before`には`messageCount`、`tokenCount`が含まれます。`session:compact:after`には`compactedCount`、`summaryLength`、`tokensBefore`、`tokensAfter`が追加されます。

## フックの検出

フックは、優先順位の低い順から高い順に、次のディレクトリから検出されます。

1. **同梱フック**: OpenClawに同梱されているもの
2. **プラグインフック**: インストール済みプラグインに同梱されているフック
3. **管理フック**: `~/.openclaw/hooks/`（ユーザーがインストールした、ワークスペース間で共有されるもの）。`hooks.internal.load.extraDirs`の追加ディレクトリもこの優先順位を共有します。
4. **ワークスペースフック**: `<workspace>/hooks/`（エージェント単位、明示的に有効化されるまでデフォルトで無効）

ワークスペースフックは新しいフック名を追加できますが、同じ名前の同梱、管理、またはプラグイン提供フックを上書きすることはできません。

### フックパック

フックパックは、`package.json`の`openclaw.hooks`を通じてフックをエクスポートするnpmパッケージです。次のコマンドでインストールします。

```bash
openclaw plugins install <path-or-spec>
```

npm specとして使えるのはレジストリのみです（パッケージ名 + 任意の厳密なバージョンまたはdist-tag）。Git/URL/file specやsemver rangeは拒否されます。

## 同梱フック

| フック                | イベント                       | 動作内容                                              |
| --------------------- | ------------------------------ | ----------------------------------------------------- |
| session-memory        | `command:new`, `command:reset` | セッションコンテキストを`<workspace>/memory/`に保存   |
| bootstrap-extra-files | `agent:bootstrap`              | globパターンから追加のbootstrapファイルを注入         |
| command-logger        | `command`                      | すべてのコマンドを`~/.openclaw/logs/commands.log`に記録 |
| boot-md               | `gateway:startup`              | Gateway起動時に`BOOT.md`を実行                        |

任意の同梱フックを有効化するには:

```bash
openclaw hooks enable <hook-name>
```

<a id="session-memory"></a>

### session-memoryの詳細

直近15件のuser/assistantメッセージを抽出し、LLMで説明的なファイル名slugを生成して、`<workspace>/memory/YYYY-MM-DD-slug.md`に保存します。`workspace.dir`の設定が必要です。

<a id="bootstrap-extra-files"></a>

### bootstrap-extra-filesの設定

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

パスはワークスペース基準で解決されます。読み込まれるのは認識されたbootstrap basenameのみです（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、`BOOTSTRAP.md`、`MEMORY.md`）。

<a id="command-logger"></a>

### command-loggerの詳細

すべてのスラッシュコマンドを`~/.openclaw/logs/commands.log`に記録します。

<a id="boot-md"></a>

### boot-mdの詳細

Gateway起動時にアクティブなワークスペースの`BOOT.md`を実行します。

## プラグインフック

プラグインは、より深い統合のためにPlugin SDKを通じてフックを登録できます。たとえば、ツール呼び出しのインターセプト、プロンプトの変更、メッセージフローの制御などです。Plugin SDKは、モデル解決、エージェントライフサイクル、メッセージフロー、ツール実行、サブエージェント連携、Gatewayライフサイクルをカバーする28個のフックを公開しています。

`before_tool_call`、`before_agent_reply`、`before_install`、およびその他すべてのプラグインフックを含む完全なプラグインフックリファレンスについては、[プラグインアーキテクチャ](/ja-JP/plugins/architecture#provider-runtime-hooks)を参照してください。

## 設定

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

フックごとの環境変数:

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

追加のフックディレクトリ:

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
従来の`hooks.internal.handlers`配列設定形式も後方互換性のため引き続きサポートされていますが、新しいフックでは検出ベースのシステムを使用してください。
</Note>

## CLIリファレンス

```bash
# すべてのフックを一覧表示（--eligible、--verbose、または--jsonを追加可能）
openclaw hooks list

# フックの詳細情報を表示
openclaw hooks info <hook-name>

# 適格性の概要を表示
openclaw hooks check

# 有効化/無効化
openclaw hooks enable <hook-name>
openclaw hooks disable <hook-name>
```

## ベストプラクティス

- **ハンドラーは高速に保つ。** フックはコマンド処理中に実行されます。重い処理は`void processInBackground(event)`でfire-and-forgetにしてください。
- **エラーは適切に処理する。** 危険な操作はtry/catchで囲み、他のハンドラーが実行できるようにthrowしないでください。
- **早い段階でイベントを絞り込む。** イベントのtype/actionが関係ない場合はすぐにreturnしてください。
- **具体的なイベントキーを使う。** オーバーヘッド削減のため、`"events": ["command"]`より`"events": ["command:new"]`を優先してください。

## トラブルシューティング

### フックが検出されない

```bash
# ディレクトリ構成を確認
ls -la ~/.openclaw/hooks/my-hook/
# 表示されるべき内容: HOOK.md, handler.ts

# 検出されたフックをすべて一覧表示
openclaw hooks list
```

### フックが適格でない

```bash
openclaw hooks info my-hook
```

不足しているバイナリ（PATH）、環境変数、設定値、またはOS互換性を確認してください。

### フックが実行されない

1. フックが有効になっていることを確認してください: `openclaw hooks list`
2. フックを再読み込みするためにGatewayプロセスを再起動してください。
3. Gatewayログを確認してください: `./scripts/clawlog.sh | grep hook`

## 関連

- [CLIリファレンス: hooks](/cli/hooks)
- [Webhook](/ja-JP/automation/cron-jobs#webhooks)
- [プラグインアーキテクチャ](/ja-JP/plugins/architecture#provider-runtime-hooks) — 完全なプラグインフックリファレンス
- [設定](/ja-JP/gateway/configuration-reference#hooks)
