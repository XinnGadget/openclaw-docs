---
read_when:
    - エージェントループまたはライフサイクルイベントの正確なウォークスルーが必要です
summary: エージェントループのライフサイクル、ストリーム、および待機のセマンティクス
title: エージェントループ
x-i18n:
    generated_at: "2026-04-12T23:27:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3c2986708b444055340e0c91b8fce7d32225fcccf3d197b797665fd36b1991a5
    source_path: concepts/agent-loop.md
    workflow: 15
---

# エージェントループ（OpenClaw）

エージェントループは、エージェントの完全な「実際の」実行全体です。取り込み → コンテキスト構築 → モデル推論 →
ツール実行 → ストリーミング返信 → 永続化、という流れになります。これは、セッション状態の整合性を保ちながら、
メッセージをアクションと最終返信へ変換する、信頼できる正規の経路です。

OpenClaw では、ループはセッションごとに直列化された単一の実行であり、モデルが思考し、ツールを呼び出し、出力をストリーミングする間に、
ライフサイクルイベントとストリームイベントを発行します。このドキュメントでは、その正規のループがエンドツーエンドでどのように配線されているかを説明します。

## エントリーポイント

- Gateway RPC: `agent` と `agent.wait`
- CLI: `agent` コマンド

## 仕組み（概要）

1. `agent` RPC はパラメータを検証し、セッション（sessionKey/sessionId）を解決し、セッションメタデータを永続化し、即座に `{ runId, acceptedAt }` を返します。
2. `agentCommand` がエージェントを実行します:
   - モデルと thinking/verbose/trace のデフォルト値を解決する
   - Skills スナップショットを読み込む
   - `runEmbeddedPiAgent`（pi-agent-core ランタイム）を呼び出す
   - 埋め込みループが発行しない場合は **ライフサイクル end/error** を発行する
3. `runEmbeddedPiAgent`:
   - セッションごと + グローバルキューを介して実行を直列化する
   - モデル + 認証プロファイルを解決し、Pi セッションを構築する
   - pi イベントを購読し、assistant/tool の差分をストリーミングする
   - タイムアウトを強制し、超過時は実行を中断する
   - ペイロード + 使用量メタデータを返す
4. `subscribeEmbeddedPiSession` は pi-agent-core のイベントを OpenClaw の `agent` ストリームに橋渡しします:
   - ツールイベント => `stream: "tool"`
   - assistant の差分 => `stream: "assistant"`
   - ライフサイクルイベント => `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` は `waitForAgentRun` を使用します:
   - `runId` に対する **ライフサイクル end/error** を待機する
   - `{ status: ok|error|timeout, startedAt, endedAt, error? }` を返す

## キューイング + 並行性

- 実行はセッションキーごと（セッションレーン）に直列化され、必要に応じてグローバルレーンも通ります。
- これにより、ツール/セッションの競合を防ぎ、セッション履歴の整合性を維持します。
- メッセージングチャネルは、このレーンシステムに流し込まれるキューモード（collect/steer/followup）を選択できます。
  詳しくは [Command Queue](/ja-JP/concepts/queue) を参照してください。

## セッション + ワークスペースの準備

- ワークスペースは解決されて作成されます。サンドボックス実行では、サンドボックスのワークスペースルートにリダイレクトされる場合があります。
- Skills は読み込まれ（またはスナップショットから再利用され）、環境変数とプロンプトに注入されます。
- ブートストラップ/コンテキストファイルが解決され、システムプロンプトレポートに注入されます。
- セッション書き込みロックが取得され、`SessionManager` がストリーミング前にオープンおよび準備されます。

## プロンプト構築 + システムプロンプト

- システムプロンプトは、OpenClaw のベースプロンプト、Skills プロンプト、ブートストラップコンテキスト、および実行ごとのオーバーライドから構築されます。
- モデル固有の制限と Compaction 用の予備トークンが強制されます。
- モデルが何を見るかについては、[System prompt](/ja-JP/concepts/system-prompt) を参照してください。

## フックポイント（介入できる場所）

OpenClaw には 2 つのフックシステムがあります。

- **内部フック**（Gateway hooks）: コマンドとライフサイクルイベント用のイベント駆動スクリプト。
- **Plugin フック**: エージェント/ツールのライフサイクルおよび Gateway パイプライン内の拡張ポイント。

### 内部フック（Gateway hooks）

- **`agent:bootstrap`**: システムプロンプトが確定する前に、ブートストラップファイルを構築している間に実行されます。
  これを使ってブートストラップコンテキストファイルを追加/削除します。
- **コマンドフック**: `/new`、`/reset`、`/stop`、およびその他のコマンドイベント（Hooks ドキュメントを参照）。

セットアップと例については、[Hooks](/ja-JP/automation/hooks) を参照してください。

### Plugin フック（エージェント + Gateway ライフサイクル）

これらはエージェントループ内または Gateway パイプライン内で実行されます。

- **`before_model_resolve`**: モデル解決の前に、provider/model を決定論的に上書きするために、セッション前（`messages` なし）で実行されます。
- **`before_prompt_build`**: セッション読み込み後（`messages` あり）に実行され、プロンプト送信前に `prependContext`、`systemPrompt`、`prependSystemContext`、または `appendSystemContext` を注入します。ターンごとの動的テキストには `prependContext` を使用し、システムプロンプト空間に配置すべき安定したガイダンスには system-context フィールドを使用してください。
- **`before_agent_start`**: 後方互換性のためのレガシーフックで、どちらのフェーズでも実行される場合があります。明示的な上記フックを優先してください。
- **`before_agent_reply`**: インラインアクションの後、LLM 呼び出しの前に実行され、Plugin がそのターンを引き受けて合成返信を返したり、ターン全体を無音にしたりできます。
- **`agent_end`**: 完了後に最終メッセージリストと実行メタデータを検査します。
- **`before_compaction` / `after_compaction`**: Compaction サイクルを監視または注釈付けします。
- **`before_tool_call` / `after_tool_call`**: ツールのパラメータ/結果に介入します。
- **`before_install`**: 組み込みスキャンの検出結果を検査し、必要に応じて skill または Plugin のインストールをブロックします。
- **`tool_result_persist`**: ツール結果がセッショントランスクリプトに書き込まれる前に、同期的に変換します。
- **`message_received` / `message_sending` / `message_sent`**: 受信 + 送信メッセージフック。
- **`session_start` / `session_end`**: セッションライフサイクルの境界。
- **`gateway_start` / `gateway_stop`**: Gateway ライフサイクルイベント。

送信/ツールガードのフック判定ルール:

- `before_tool_call`: `{ block: true }` は終端的であり、優先度の低いハンドラを停止します。
- `before_tool_call`: `{ block: false }` は no-op であり、以前の block を解除しません。
- `before_install`: `{ block: true }` は終端的であり、優先度の低いハンドラを停止します。
- `before_install`: `{ block: false }` は no-op であり、以前の block を解除しません。
- `message_sending`: `{ cancel: true }` は終端的であり、優先度の低いハンドラを停止します。
- `message_sending`: `{ cancel: false }` は no-op であり、以前の cancel を解除しません。

フック API と登録の詳細については、[Plugin hooks](/ja-JP/plugins/architecture#provider-runtime-hooks) を参照してください。

## ストリーミング + 部分返信

- assistant の差分は pi-agent-core からストリーミングされ、`assistant` イベントとして発行されます。
- ブロックストリーミングは、`text_end` または `message_end` のいずれかで部分返信を発行できます。
- reasoning ストリーミングは、別のストリームとして、またはブロック返信として発行できます。
- チャンク分割とブロック返信の挙動については、[Streaming](/ja-JP/concepts/streaming) を参照してください。

## ツール実行 + メッセージングツール

- ツールの start/update/end イベントは `tool` ストリーム上で発行されます。
- ツール結果は、ログ記録/発行の前に、サイズと画像ペイロードについてサニタイズされます。
- メッセージングツールによる送信は追跡され、assistant による重複確認を抑止します。

## 返信の整形 + 抑止

- 最終ペイロードは次から組み立てられます:
  - assistant テキスト（および任意の reasoning）
  - インラインツール要約（verbose かつ許可されている場合）
  - モデルでエラーが発生した場合の assistant エラーテキスト
- 正確なサイレントトークン `NO_REPLY` / `no_reply` は送信ペイロードから
  フィルタリングされます。
- メッセージングツールの重複は最終ペイロードリストから削除されます。
- レンダリング可能なペイロードが何も残らず、かつツールがエラーになった場合は、フォールバックのツールエラー返信が発行されます
  （メッセージングツールがすでにユーザー向けの返信を送信している場合を除く）。

## Compaction + リトライ

- 自動 Compaction は `compaction` ストリームイベントを発行し、リトライを引き起こす場合があります。
- リトライ時には、重複出力を避けるために、インメモリバッファとツール要約がリセットされます。
- Compaction パイプラインについては、[Compaction](/ja-JP/concepts/compaction) を参照してください。

## イベントストリーム（現時点）

- `lifecycle`: `subscribeEmbeddedPiSession` によって発行される（およびフォールバックとして `agentCommand` からも発行される）
- `assistant`: pi-agent-core からストリーミングされる差分
- `tool`: pi-agent-core からストリーミングされるツールイベント

## チャットチャネルの処理

- assistant の差分はチャット `delta` メッセージにバッファリングされます。
- チャット `final` は **ライフサイクル end/error** 時に発行されます。

## タイムアウト

- `agent.wait` のデフォルト: 30 秒（待機のみ）。`timeoutMs` パラメータで上書きします。
- エージェントランタイム: `agents.defaults.timeoutSeconds` のデフォルトは 172800 秒（48 時間）で、`runEmbeddedPiAgent` の中断タイマーで強制されます。
- LLM アイドルタイムアウト: `agents.defaults.llm.idleTimeoutSeconds` は、アイドル時間の枠内で応答チャンクが届かない場合にモデルリクエストを中断します。遅いローカルモデルや reasoning/ツールコール provider では、これを明示的に設定してください。無効にするには 0 に設定します。未設定の場合、OpenClaw は `agents.defaults.timeoutSeconds` が設定されていればそれを使用し、そうでなければ 120 秒を使用します。明示的な LLM またはエージェントタイムアウトがない Cron トリガー実行では、アイドルウォッチドッグは無効化され、Cron 外側のタイムアウトに依存します。

## 途中で終了する可能性がある場所

- エージェントタイムアウト（中断）
- AbortSignal（キャンセル）
- Gateway 切断または RPC タイムアウト
- `agent.wait` タイムアウト（待機のみであり、エージェント自体は停止しない）

## 関連

- [Tools](/ja-JP/tools) — 利用可能なエージェントツール
- [Hooks](/ja-JP/automation/hooks) — エージェントライフサイクルイベントによってトリガーされるイベント駆動スクリプト
- [Compaction](/ja-JP/concepts/compaction) — 長い会話がどのように要約されるか
- [Exec Approvals](/ja-JP/tools/exec-approvals) — シェルコマンドの承認ゲート
- [Thinking](/ja-JP/tools/thinking) — thinking/reasoning レベル設定
