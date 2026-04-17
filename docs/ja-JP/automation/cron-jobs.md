---
read_when:
    - バックグラウンドジョブやウェイクアップのスケジュール設定
    - 外部トリガー（Webhook、Gmail）をOpenClawに接続すること
    - スケジュール済みタスクに heartbeat と cron のどちらを使うかを決めること
summary: Gatewayスケジューラ用のスケジュール済みジョブ、Webhook、Gmail PubSubトリガー
title: スケジュール済みタスク
x-i18n:
    generated_at: "2026-04-12T04:43:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: f42bcaeedd0595d025728d7f236a724a0ebc67b6813c57233f4d739b3088317f
    source_path: automation/cron-jobs.md
    workflow: 15
---

# スケジュール済みタスク（Cron）

Cron は Gateway に組み込まれたスケジューラです。ジョブを永続化し、適切なタイミングでエージェントを起動し、出力をチャットチャンネルまたは Webhook エンドポイントに返すことができます。

## クイックスタート

```bash
# 1 回限りのリマインダーを追加する
openclaw cron add \
  --name "Reminder" \
  --at "2026-02-01T16:00:00Z" \
  --session main \
  --system-event "Reminder: check the cron docs draft" \
  --wake now \
  --delete-after-run

# ジョブを確認する
openclaw cron list

# 実行履歴を確認する
openclaw cron runs --id <job-id>
```

## cron の仕組み

- Cron は **Gateway プロセス内** で実行されます（モデル内ではありません）。
- ジョブは `~/.openclaw/cron/jobs.json` に永続化されるため、再起動してもスケジュールは失われません。
- すべての cron 実行で [バックグラウンドタスク](/ja-JP/automation/tasks) レコードが作成されます。
- 1 回限りのジョブ（`--at`）は、デフォルトで成功後に自動削除されます。
- 分離された cron 実行では、実行完了時にその `cron:<jobId>` セッション向けに追跡されているブラウザータブやプロセスをベストエフォートで閉じるため、切り離されたブラウザー自動化によって孤立プロセスが残りません。
- 分離された cron 実行では、古い確認応答返信も防止されます。最初の結果が単なる中間ステータス更新（`on it`、`pulling everything together`、およびそれに類するヒント）であり、最終回答を担当する子孫サブエージェント実行が残っていない場合、OpenClaw は配信前に実際の結果を得るために 1 回だけ再プロンプトします。

<a id="maintenance"></a>

cron のタスク整合性管理はランタイム側で行われます。古い子セッション行が残っていても、cron ランタイムがそのジョブを実行中として追跡している間は、アクティブな cron タスクは存続します。ランタイムがそのジョブの所有をやめ、5 分の猶予期間が過ぎると、メンテナンスによってタスクが `lost` とマークされることがあります。

## スケジュールの種類

| 種類    | CLI フラグ | 説明                                                  |
| ------- | ---------- | ----------------------------------------------------- |
| `at`    | `--at`     | 1 回限りのタイムスタンプ（ISO 8601 または `20m` のような相対指定） |
| `every` | `--every`  | 固定間隔                                              |
| `cron`  | `--cron`   | 任意指定の `--tz` を伴う 5 フィールドまたは 6 フィールドの cron 式 |

タイムゾーンを含まないタイムスタンプは UTC として扱われます。ローカルの壁時計時刻でスケジュールするには `--tz America/New_York` を追加してください。

毎時ちょうどに繰り返す式は、負荷スパイクを減らすために最大 5 分まで自動的に分散されます。正確な時刻で実行するには `--exact` を使うか、明示的なウィンドウとして `--stagger 30s` を指定してください。

### 日付指定と曜日指定は OR ロジックを使います

cron 式は [croner](https://github.com/Hexagon/croner) によって解析されます。日付指定フィールドと曜日指定フィールドの両方がワイルドカードでない場合、croner は **両方ではなく、どちらか一方** が一致したときにマッチします。これは標準的な Vixie cron の動作です。

```
# 意図: 「15 日の午前 9 時、ただし月曜日の場合のみ」
# 実際: 「毎月 15 日の午前 9 時、かつ毎週月曜日の午前 9 時」
0 9 15 * 1
```

これは月に 0〜1 回ではなく、月に約 5〜6 回発火します。OpenClaw はここで Croner のデフォルト OR 動作を使います。両方の条件を必須にするには、Croner の `+` 曜日修飾子（`0 9 15 * +1`）を使うか、片方のフィールドだけでスケジュールし、もう片方はジョブのプロンプトまたはコマンド内でガードしてください。

## 実行スタイル

| スタイル        | `--session` の値    | 実行場所                 | 最適な用途                      |
| --------------- | ------------------- | ------------------------ | ------------------------------- |
| メインセッション | `main`              | 次の heartbeat ターン     | リマインダー、システムイベント |
| 分離            | `isolated`          | 専用の `cron:<jobId>`     | レポート、バックグラウンド作業 |
| 現在のセッション | `current`           | 作成時にバインド          | コンテキスト依存の定期作業     |
| カスタムセッション | `session:custom-id` | 永続的な名前付きセッション | 履歴を積み上げるワークフロー   |

**メインセッション** ジョブはシステムイベントをキューに入れ、必要に応じて heartbeat を起動します（`--wake now` または `--wake next-heartbeat`）。**分離** ジョブは、新しいセッションで専用のエージェントターンを実行します。**カスタムセッション**（`session:xxx`）は実行をまたいでコンテキストを保持するため、以前の要約を積み上げる日次スタンドアップのようなワークフローを実現できます。

分離ジョブでは、ランタイムの後片付けにその cron セッション向けのブラウザーのベストエフォートなクリーンアップも含まれます。クリーンアップの失敗は無視されるため、実際の cron 結果が優先されます。

分離された cron 実行がサブエージェントをオーケストレーションする場合、配信では古い親の中間テキストよりも最終的な子孫出力が優先されます。子孫がまだ実行中であれば、OpenClaw はその部分的な親更新を通知する代わりに抑制します。

### 分離ジョブのペイロードオプション

- `--message`: プロンプトテキスト（分離では必須）
- `--model` / `--thinking`: モデルおよび thinking レベルのオーバーライド
- `--light-context`: ワークスペースのブートストラップファイル注入をスキップ
- `--tools exec,read`: ジョブが使えるツールを制限

`--model` は、そのジョブで選択された許可済みモデルを使います。要求されたモデルが許可されていない場合、cron は警告を記録し、代わりにそのジョブのエージェントまたはデフォルトのモデル選択にフォールバックします。設定済みのフォールバックチェーンは引き続き適用されますが、明示的なジョブ単位のフォールバックリストなしの単純なモデルオーバーライドでは、エージェントのプライマリが隠れた追加リトライ先として付加されなくなりました。

分離ジョブのモデル選択の優先順位は次のとおりです。

1. Gmail フックのモデルオーバーライド（その実行が Gmail 由来で、そのオーバーライドが許可されている場合）
2. ジョブ単位ペイロードの `model`
3. 保存済み cron セッションのモデルオーバーライド
4. エージェントまたはデフォルトのモデル選択

Fast mode も解決後のライブ選択に従います。選択されたモデル設定に `params.fastMode` がある場合、分離 cron はデフォルトでそれを使用します。保存済みセッションの `fastMode` オーバーライドは、どちらの方向でも設定より優先されます。

分離実行でライブのモデル切り替えハンドオフが発生した場合、cron は切り替え後のプロバイダー/モデルで再試行し、そのライブ選択を再試行前に保存します。切り替えに新しい認証プロファイルも含まれている場合、cron はその認証プロファイルのオーバーライドも保存します。再試行回数には上限があり、初回試行に加えて 2 回の切り替え再試行の後は、無限ループせず中止します。

## 配信と出力

| モード     | 動作                                                    |
| ---------- | ------------------------------------------------------- |
| `announce` | 要約を対象チャンネルに配信する（分離のデフォルト）      |
| `webhook`  | 完了イベントのペイロードを URL に POST する             |
| `none`     | 内部のみで、配信しない                                  |

チャンネル配信には `--announce --channel telegram --to "-1001234567890"` を使用します。Telegram フォーラムトピックでは `-1001234567890:topic:123` を使います。Slack/Discord/Mattermost の対象には明示的な接頭辞（`channel:<id>`、`user:<id>`）を使ってください。

cron が所有する分離ジョブでは、実行ランナーが最終配信経路を管理します。エージェントにはプレーンテキストの要約を返すよう促され、その要約が `announce`、`webhook` を通じて送信されるか、`none` の場合は内部に保持されます。`--no-deliver` は配信をエージェントに戻しません。その実行を内部専用に保ちます。

元のタスクで何らかの外部受信者にメッセージを送ることが明示されている場合、エージェントは直接送信しようとするのではなく、そのメッセージを誰に/どこへ送るべきかを出力内に記載する必要があります。

失敗通知は別の宛先経路に従います。

- `cron.failureDestination` は失敗通知のグローバルデフォルトを設定します。
- `job.delivery.failureDestination` はジョブ単位でそれを上書きします。
- どちらも設定されておらず、ジョブがすでに `announce` で配信している場合、失敗通知はそのプライマリな通知先にフォールバックします。
- `delivery.failureDestination` は、プライマリ配信モードが `webhook` である場合を除き、`sessionTarget="isolated"` のジョブでのみサポートされます。

## CLI の例

1 回限りのリマインダー（メインセッション）:

```bash
openclaw cron add \
  --name "Calendar check" \
  --at "20m" \
  --session main \
  --system-event "Next heartbeat: check calendar." \
  --wake now
```

配信付きの定期的な分離ジョブ:

```bash
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize overnight updates." \
  --announce \
  --channel slack \
  --to "channel:C1234567890"
```

モデルと thinking のオーバーライドを持つ分離ジョブ:

```bash
openclaw cron add \
  --name "Deep analysis" \
  --cron "0 6 * * 1" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Weekly deep analysis of project progress." \
  --model "opus" \
  --thinking high \
  --announce
```

## Webhook

Gateway は外部トリガー用に HTTP Webhook エンドポイントを公開できます。設定で有効化します。

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
  },
}
```

### 認証

すべてのリクエストは、ヘッダーを介してフックトークンを含める必要があります。

- `Authorization: Bearer <token>`（推奨）
- `x-openclaw-token: <token>`

クエリ文字列のトークンは拒否されます。

### POST /hooks/wake

メインセッション用のシステムイベントをキューに入れます。

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"text":"New email received","mode":"now"}'
```

- `text`（必須）: イベントの説明
- `mode`（任意）: `now`（デフォルト）または `next-heartbeat`

### POST /hooks/agent

分離されたエージェントターンを実行します。

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","model":"openai/gpt-5.4-mini"}'
```

フィールド: `message`（必須）、`name`、`agentId`、`wakeMode`、`deliver`、`channel`、`to`、`model`、`thinking`、`timeoutSeconds`。

### マップされたフック（POST /hooks/\<name\>）

カスタムフック名は、設定の `hooks.mappings` を通じて解決されます。マッピングは、テンプレートまたはコード変換を使って任意のペイロードを `wake` または `agent` アクションに変換できます。

### セキュリティ

- フックエンドポイントは loopback、tailnet、または信頼できるリバースプロキシの背後に置いてください。
- 専用のフックトークンを使ってください。Gateway の認証トークンを再利用しないでください。
- `hooks.path` は専用のサブパスにしてください。`/` は拒否されます。
- 明示的な `agentId` ルーティングを制限するには `hooks.allowedAgentIds` を設定してください。
- 呼び出し元がセッションを選べる必要がない限り、`hooks.allowRequestSessionKey=false` のままにしてください。
- `hooks.allowRequestSessionKey` を有効にする場合は、許可されるセッションキーの形を制約するために `hooks.allowedSessionKeyPrefixes` も設定してください。
- フックペイロードはデフォルトで安全境界によりラップされます。

## Gmail PubSub 連携

Google PubSub を通じて Gmail 受信トレイトリガーを OpenClaw に接続します。

**前提条件**: `gcloud` CLI、`gog`（gogcli）、OpenClaw のフックが有効、公開 HTTPS エンドポイント用の Tailscale。

### ウィザード設定（推奨）

```bash
openclaw webhooks gmail setup --account openclaw@gmail.com
```

これにより `hooks.gmail` 設定が書き込まれ、Gmail プリセットが有効化され、push エンドポイントに Tailscale Funnel が使われます。

### Gateway の自動起動

`hooks.enabled=true` かつ `hooks.gmail.account` が設定されている場合、Gateway は起動時に `gog gmail watch serve` を開始し、自動的に watch を更新します。無効にするには `OPENCLAW_SKIP_GMAIL_WATCHER=1` を設定してください。

### 手動の 1 回限りの設定

1. `gog` が使用する OAuth クライアントを所有する GCP プロジェクトを選択します。

```bash
gcloud auth login
gcloud config set project <project-id>
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

2. トピックを作成し、Gmail に push アクセス権を付与します。

```bash
gcloud pubsub topics create gog-gmail-watch
gcloud pubsub topics add-iam-policy-binding gog-gmail-watch \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
```

3. watch を開始します。

```bash
gog gmail watch start \
  --account openclaw@gmail.com \
  --label INBOX \
  --topic projects/<project-id>/topics/gog-gmail-watch
```

### Gmail のモデルオーバーライド

```json5
{
  hooks: {
    gmail: {
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

## ジョブの管理

```bash
# すべてのジョブを一覧表示する
openclaw cron list

# ジョブを編集する
openclaw cron edit <jobId> --message "Updated prompt" --model "opus"

# ジョブを今すぐ強制実行する
openclaw cron run <jobId>

# 期限到来時のみ実行する
openclaw cron run <jobId> --due

# 実行履歴を表示する
openclaw cron runs --id <jobId> --limit 50

# ジョブを削除する
openclaw cron remove <jobId>

# エージェント選択（マルチエージェント構成）
openclaw cron add --name "Ops sweep" --cron "0 6 * * *" --session isolated --message "Check ops queue" --agent ops
openclaw cron edit <jobId> --clear-agent
```

モデルオーバーライドに関する注意:

- `openclaw cron add|edit --model ...` はジョブの選択モデルを変更します。
- モデルが許可されている場合、その正確なプロバイダー/モデルが分離エージェント実行に渡されます。
- 許可されていない場合、cron は警告を出し、ジョブのエージェントまたはデフォルトのモデル選択にフォールバックします。
- 設定済みのフォールバックチェーンは引き続き適用されますが、明示的なジョブ単位のフォールバックリストがない単純な `--model` オーバーライドは、隠れた追加リトライ先としてエージェントのプライマリへ自動的にフォールスルーしなくなりました。

## 設定

```json5
{
  cron: {
    enabled: true,
    store: "~/.openclaw/cron/jobs.json",
    maxConcurrentRuns: 1,
    retry: {
      maxAttempts: 3,
      backoffMs: [60000, 120000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "server_error"],
    },
    webhookToken: "replace-with-dedicated-webhook-token",
    sessionRetention: "24h",
    runLog: { maxBytes: "2mb", keepLines: 2000 },
  },
}
```

cron を無効にする: `cron.enabled: false` または `OPENCLAW_SKIP_CRON=1`。

**1 回限りジョブの再試行**: 一時的なエラー（rate limit、overload、network、server error）は指数バックオフで最大 3 回まで再試行されます。恒久的なエラーは即座に無効化されます。

**定期ジョブの再試行**: 再試行の間隔には指数バックオフ（30 秒〜60 分）が使われます。バックオフは次回の成功実行後にリセットされます。

**メンテナンス**: `cron.sessionRetention`（デフォルト `24h`）は分離実行セッションのエントリを削除します。`cron.runLog.maxBytes` / `cron.runLog.keepLines` は実行ログファイルを自動的に削除します。

## トラブルシューティング

### コマンドの手順

```bash
openclaw status
openclaw gateway status
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
openclaw doctor
```

### cron が発火しない

- `cron.enabled` と `OPENCLAW_SKIP_CRON` 環境変数を確認してください。
- Gateway が継続的に実行されていることを確認してください。
- `cron` スケジュールでは、タイムゾーン（`--tz`）とホストのタイムゾーンが一致しているか確認してください。
- 実行出力の `reason: not-due` は、手動実行が `openclaw cron run <jobId> --due` で確認され、そのジョブがまだ期限前だったことを意味します。

### cron は発火したが配信されない

- 配信モードが `none` の場合、外部メッセージは送信されません。
- 配信先が欠落しているか無効（`channel` / `to`）の場合、送信はスキップされます。
- チャンネル認証エラー（`unauthorized`、`Forbidden`）は、認証情報によって配信がブロックされたことを意味します。
- 分離実行がサイレントトークン（`NO_REPLY` / `no_reply`）のみを返した場合、OpenClaw は直接の外部配信を抑制し、フォールバックのキュー済み要約経路も抑制するため、チャットには何も投稿されません。
- cron が所有する分離ジョブでは、フォールバックとしてエージェントが message ツールを使うことを期待しないでください。最終配信はランナーが担当します。`--no-deliver` は直接送信を許可する代わりに、その実行を内部専用に保ちます。

### タイムゾーンの落とし穴

- `--tz` なしの cron は Gateway ホストのタイムゾーンを使います。
- タイムゾーンなしの `at` スケジュールは UTC として扱われます。
- Heartbeat の `activeHours` は設定されたタイムゾーン解決を使います。

## 関連

- [自動化とタスク](/ja-JP/automation) — すべての自動化メカニズムの概要
- [バックグラウンドタスク](/ja-JP/automation/tasks) — cron 実行のタスク台帳
- [Heartbeat](/ja-JP/gateway/heartbeat) — 定期的なメインセッションターン
- [タイムゾーン](/ja-JP/concepts/timezone) — タイムゾーン設定
