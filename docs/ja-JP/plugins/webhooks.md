---
read_when:
    - 外部システムからTaskFlowをトリガーまたは操作したいとき
    - バンドルされたwebhooks pluginを設定しているとき
summary: 'Webhooks plugin: 信頼された外部自動化のための認証付きTaskFlow ingress'
title: Webhooks Plugin
x-i18n:
    generated_at: "2026-04-07T04:45:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5da12a887752ec6ee853cfdb912db0ae28512a0ffed06fe3828ef2eee15bc9d
    source_path: plugins/webhooks.md
    workflow: 15
---

# Webhooks (plugin)

Webhooks pluginは、外部自動化をOpenClaw TaskFlowsに結び付ける認証付きHTTPルートを追加します。

Zapier、n8n、CIジョブ、または内部サービスのような信頼されたシステムから、まずcustom pluginを書かずにmanaged TaskFlowsを作成して操作したい場合に使用します。

## 実行場所

Webhooks pluginはGatewayプロセス内で実行されます。

Gatewayが別のマシンで動作している場合は、そのGateway hostにpluginをインストールして設定し、その後Gatewayを再起動してください。

## ルートを設定する

`plugins.entries.webhooks.config` 配下に設定します:

```json5
{
  plugins: {
    entries: {
      webhooks: {
        enabled: true,
        config: {
          routes: {
            zapier: {
              path: "/plugins/webhooks/zapier",
              sessionKey: "agent:main:main",
              secret: {
                source: "env",
                provider: "default",
                id: "OPENCLAW_WEBHOOK_SECRET",
              },
              controllerId: "webhooks/zapier",
              description: "Zapier TaskFlow bridge",
            },
          },
        },
      },
    },
  },
}
```

ルートフィールド:

- `enabled`: 任意。デフォルトは `true`
- `path`: 任意。デフォルトは `/plugins/webhooks/<routeId>`
- `sessionKey`: バインドされたTaskFlowsを所有する必須のsession
- `secret`: 必須の共有シークレットまたはSecretRef
- `controllerId`: 作成されるmanaged flow用の任意のcontroller id
- `description`: 任意の運用メモ

サポートされる `secret` 入力:

- プレーン文字列
- `source: "env" | "file" | "exec"` のSecretRef

シークレットを参照するルートが起動時にそのシークレットを解決できない場合、pluginは壊れたendpointを公開する代わりに、そのルートをスキップして警告を記録します。

## セキュリティモデル

各ルートは、設定された `sessionKey` のTaskFlow権限で動作することを信頼されます。

これは、そのルートがそのsessionに属するTaskFlowsを検査および変更できることを意味するため、次のようにしてください:

- ルートごとに強力で一意なシークレットを使用する
- インラインのプレーンテキストシークレットよりもシークレット参照を優先する
- ワークフローに合う最も狭いsessionにルートをバインドする
- 必要な特定のwebhook pathのみを公開する

pluginが適用するもの:

- 共有シークレット認証
- リクエストボディサイズとタイムアウトのガード
- fixed-window rate limiting
- 処理中リクエスト数の制限
- `api.runtime.taskFlow.bindSession(...)` を通じたowner-bound TaskFlowアクセス

## リクエスト形式

次の形式で `POST` リクエストを送信します:

- `Content-Type: application/json`
- `Authorization: Bearer <secret>` または `x-openclaw-webhook-secret: <secret>`

例:

```bash
curl -X POST https://gateway.example.com/plugins/webhooks/zapier \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_SHARED_SECRET' \
  -d '{"action":"create_flow","goal":"Review inbound queue"}'
```

## サポートされるactions

pluginは現在、次のJSON `action` 値を受け付けます:

- `create_flow`
- `get_flow`
- `list_flows`
- `find_latest_flow`
- `resolve_flow`
- `get_task_summary`
- `set_waiting`
- `resume_flow`
- `finish_flow`
- `fail_flow`
- `request_cancel`
- `cancel_flow`
- `run_task`

### `create_flow`

ルートにバインドされたsession用のmanaged TaskFlowを作成します。

例:

```json
{
  "action": "create_flow",
  "goal": "Review inbound queue",
  "status": "queued",
  "notifyPolicy": "done_only"
}
```

### `run_task`

既存のmanaged TaskFlow内にmanaged child taskを作成します。

許可されるruntimeは次のとおりです:

- `subagent`
- `acp`

例:

```json
{
  "action": "run_task",
  "flowId": "flow_123",
  "runtime": "acp",
  "childSessionKey": "agent:main:acp:worker",
  "task": "Inspect the next message batch"
}
```

## レスポンス形式

成功レスポンスは次を返します:

```json
{
  "ok": true,
  "routeId": "zapier",
  "result": {}
}
```

拒否されたリクエストは次を返します:

```json
{
  "ok": false,
  "routeId": "zapier",
  "code": "not_found",
  "error": "TaskFlow not found.",
  "result": {}
}
```

pluginは意図的に、webhookレスポンスからowner/session metadataを除去します。

## 関連ドキュメント

- [Plugin runtime SDK](/ja-JP/plugins/sdk-runtime)
- [Hooks and webhooks overview](/ja-JP/automation/hooks)
- [CLI webhooks](/cli/webhooks)
