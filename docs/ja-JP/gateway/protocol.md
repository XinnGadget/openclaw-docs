---
read_when:
    - Gateway WSクライアントを実装または更新する場合
    - プロトコルの不一致や接続失敗をデバッグする場合
    - プロトコルスキーマ/モデルを再生成する場合
summary: 'Gateway WebSocketプロトコル: ハンドシェイク、フレーム、バージョニング'
title: Gatewayプロトコル
x-i18n:
    generated_at: "2026-04-08T02:16:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8635e3ac1dd311dbd3a770b088868aa1495a8d53b3ebc1eae0dfda3b2bf4694a
    source_path: gateway/protocol.md
    workflow: 15
---

# Gatewayプロトコル（WebSocket）

Gateway WSプロトコルは、OpenClawの**単一のコントロールプレーン + ノード転送**です。
すべてのクライアント（CLI、web UI、macOSアプリ、iOS/Androidノード、ヘッドレス
ノード）は、WebSocket経由で接続し、ハンドシェイク時に自分の**role**と**scope**を
宣言します。

## 転送

- WebSocket、JSONペイロードを含むテキストフレーム。
- 最初のフレームは**必ず** `connect` リクエストでなければなりません。

## ハンドシェイク（connect）

Gateway → Client（接続前チャレンジ）:

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

Client → Gateway:

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

Gateway → Client:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": { "type": "hello-ok", "protocol": 3, "policy": { "tickIntervalMs": 15000 } }
}
```

デバイストークンが発行される場合、`hello-ok` には次も含まれます:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

信頼されたブートストラップ引き継ぎの間、`hello-ok.auth` には
`deviceTokens` に追加の制限付きroleエントリが含まれる場合もあります:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "node",
    "scopes": [],
    "deviceTokens": [
      {
        "deviceToken": "…",
        "role": "operator",
        "scopes": ["operator.approvals", "operator.read", "operator.talk.secrets", "operator.write"]
      }
    ]
  }
}
```

組み込みのnode/operatorブートストラップフローでは、主nodeトークンは
`scopes: []` のままで、引き渡されたoperatorトークンはブートストラップ
operator許可リスト（`operator.approvals`, `operator.read`,
`operator.talk.secrets`, `operator.write`）に制限されたままです。
ブートストラップのscopeチェックは引き続きroleプレフィックス付きです:
operatorエントリはoperatorリクエストのみを満たし、non-operator
roleは引き続き自身のroleプレフィックス配下のscopeを必要とします。

### Nodeの例

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## フレーミング

- **リクエスト**: `{type:"req", id, method, params}`
- **レスポンス**: `{type:"res", id, ok, payload|error}`
- **イベント**: `{type:"event", event, payload, seq?, stateVersion?}`

副作用のあるメソッドには**冪等性キー**が必要です（スキーマを参照）。

## role + scope

### role

- `operator` = コントロールプレーンクライアント（CLI/UI/自動化）。
- `node` = 機能ホスト（camera/screen/canvas/system.run）。

### scope（operator）

一般的なscope:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

`includeSecrets: true` を伴う `talk.config` には `operator.talk.secrets`
（または `operator.admin`）が必要です。

プラグイン登録されたGateway RPCメソッドは独自のoperator scopeを要求する場合がありますが、
予約済みのコアadminプレフィックス（`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`）は常に `operator.admin` に解決されます。

メソッドscopeは最初のゲートにすぎません。`chat.send` を通じて到達する
一部のスラッシュコマンドには、さらに厳しいコマンドレベルのチェックが適用されます。
たとえば、永続的な `/config set` と `/config unset` の書き込みには
`operator.admin` が必要です。

`node.pair.approve` には、ベースメソッドscopeに加えて承認時の追加scopeチェックもあります:

- コマンドなしのリクエスト: `operator.pairing`
- non-exec nodeコマンドを伴うリクエスト: `operator.pairing` + `operator.write`
- `system.run`, `system.run.prepare`, `system.which` を含むリクエスト:
  `operator.pairing` + `operator.admin`

### caps/commands/permissions（node）

ノードは接続時に機能クレームを宣言します:

- `caps`: 高レベルな機能カテゴリ。
- `commands`: invoke用のコマンド許可リスト。
- `permissions`: 詳細なトグル（例: `screen.record`, `camera.capture`）。

Gatewayはこれらを**クレーム**として扱い、サーバー側の許可リストを適用します。

## プレゼンス

- `system-presence` はデバイスアイデンティティをキーとしたエントリを返します。
- プレゼンスエントリには `deviceId`, `roles`, `scopes` が含まれるため、UIは
  同一デバイスが **operator** と **node** の両方として接続していても
  1行で表示できます。

## よく使われるRPCメソッドファミリー

このページは生成された完全なダンプではありませんが、公開WSサーフェスは
上記のハンドシェイク/認証の例よりも広範です。これらは現在Gatewayが公開している
主なメソッドファミリーです。

`hello-ok.features.methods` は、
`src/gateway/server-methods-list.ts` と、読み込まれたプラグイン/チャネルの
メソッドエクスポートから構築された保守的な検出リストです。
これを機能検出として扱ってください。`src/gateway/server-methods/*.ts` に実装された
呼び出し可能なすべてのヘルパーの生成ダンプではありません。

### systemとidentity

- `health` は、キャッシュされた、または新たにプローブされたGatewayヘルススナップショットを返します。
- `status` は `/status` スタイルのGatewayサマリーを返します。機密フィールドは
  admin scopeを持つoperatorクライアントにのみ含まれます。
- `gateway.identity.get` は、relayおよびpairingフローで使われるGatewayデバイスIDを返します。
- `system-presence` は、接続中のoperator/nodeデバイスの現在のプレゼンススナップショットを返します。
- `system-event` はsystemイベントを追加し、プレゼンスコンテキストを更新/ブロードキャストできます。
- `last-heartbeat` は、最後に永続化されたheartbeatイベントを返します。
- `set-heartbeats` は、Gatewayでのheartbeat処理を切り替えます。

### modelとusage

- `models.list` は、ランタイムで許可されたモデルカタログを返します。
- `usage.status` は、プロバイダー使用量ウィンドウ/残りクォータのサマリーを返します。
- `usage.cost` は、日付範囲の集計済みコスト使用量サマリーを返します。
- `doctor.memory.status` は、アクティブなデフォルトagentワークスペース向けの
  ベクターメモリ / embedding準備状態を返します。
- `sessions.usage` は、セッションごとの使用量サマリーを返します。
- `sessions.usage.timeseries` は、1つのセッションの時系列使用量を返します。
- `sessions.usage.logs` は、1つのセッションの使用量ログエントリを返します。

### チャネルとログインヘルパー

- `channels.status` は、組み込み + バンドルされたチャネル/プラグインのステータスサマリーを返します。
- `channels.logout` は、ログアウト対応のチャネルで特定のチャネル/アカウントをログアウトします。
- `web.login.start` は、現在のQR対応webチャネルプロバイダー向けのQR/webログインフローを開始します。
- `web.login.wait` は、そのQR/webログインフローの完了を待ち、成功時にチャネルを開始します。
- `push.test` は、登録済みiOSノードにテストAPNsプッシュを送信します。
- `voicewake.get` は、保存されたウェイクワードトリガーを返します。
- `voicewake.set` は、ウェイクワードトリガーを更新し、その変更をブロードキャストします。

### メッセージングとログ

- `send` は、chat runner外でのチャネル/アカウント/threadターゲット送信向けの
  直接のアウトバウンド配信RPCです。
- `logs.tail` は、カーソル/上限および最大バイト制御付きで、
  設定されたGatewayファイルログの末尾を返します。

### TalkとTTS

- `talk.config` は、有効なTalk設定ペイロードを返します。`includeSecrets`
  には `operator.talk.secrets`（または `operator.admin`）が必要です。
- `talk.mode` は、WebChat/Control UIクライアント向けの現在のTalkモード状態を設定/ブロードキャストします。
- `talk.speak` は、アクティブなTalk speechプロバイダーを通じて音声を合成します。
- `tts.status` は、TTS有効状態、アクティブプロバイダー、フォールバックプロバイダー、
  およびプロバイダー設定状態を返します。
- `tts.providers` は、表示可能なTTSプロバイダーのインベントリを返します。
- `tts.enable` と `tts.disable` は、TTS設定状態を切り替えます。
- `tts.setProvider` は、優先TTSプロバイダーを更新します。
- `tts.convert` は、単発のtext-to-speech変換を実行します。

### シークレット、設定、更新、およびウィザード

- `secrets.reload` は、アクティブなSecretRefを再解決し、完全成功時にのみランタイムのシークレット状態を切り替えます。
- `secrets.resolve` は、特定のコマンド/ターゲットセット向けにコマンド対象のシークレット割り当てを解決します。
- `config.get` は、現在の設定スナップショットとハッシュを返します。
- `config.set` は、検証済みの設定ペイロードを書き込みます。
- `config.patch` は、部分的な設定更新をマージします。
- `config.apply` は、完全な設定ペイロードを検証して置き換えます。
- `config.schema` は、Control UIおよびCLIツールで使われるライブ設定スキーマペイロード
  を返します: スキーマ、`uiHints`、バージョン、生成メタデータ。これには、ランタイムで
  読み込める場合のプラグイン + チャネルスキーマメタデータも含まれます。
  スキーマには、UIで使われるものと同じラベルおよびヘルプテキストから導出された
  フィールド `title` / `description` メタデータが含まれます。これには、ネストしたobject、
  wildcard、array-item、および対応するフィールドドキュメントが存在する場合の
  `anyOf` / `oneOf` / `allOf` 合成分岐も含まれます。
- `config.schema.lookup` は、1つの設定パス向けのパススコープ付きlookupペイロードを返します:
  正規化されたパス、浅いスキーマノード、一致したhint + `hintPath`、および
  UI/CLIドリルダウン向けの直接の子サマリーです。
  - Lookupスキーマノードは、ユーザー向けドキュメントおよび一般的な検証フィールドを保持します:
    `title`, `description`, `type`, `enum`, `const`, `format`, `pattern`,
    数値/文字列/配列/objectの境界、および
    `additionalProperties`, `deprecated`, `readOnly`, `writeOnly` のような真偽値フラグ。
  - 子サマリーは `key`、正規化された `path`、`type`、`required`、
    `hasChildren`、および一致した `hint` / `hintPath` を公開します。
- `update.run` は、Gateway更新フローを実行し、更新自体が成功した場合にのみ再起動をスケジュールします。
- `wizard.start`、`wizard.next`、`wizard.status`、`wizard.cancel` は、
  オンボーディングウィザードをWS RPC経由で公開します。

### 既存の主要ファミリー

#### agentとworkspaceヘルパー

- `agents.list` は、設定済みagentエントリを返します。
- `agents.create`、`agents.update`、`agents.delete` は、agentレコードと
  workspace配線を管理します。
- `agents.files.list`、`agents.files.get`、`agents.files.set` は、
  agent向けに公開されたブートストラップworkspaceファイルを管理します。
- `agent.identity.get` は、agentまたはセッションの有効なassistant identityを返します。
- `agent.wait` は、実行完了を待ち、利用可能な場合は終端スナップショットを返します。

#### セッション制御

- `sessions.list` は、現在のセッションインデックスを返します。
- `sessions.subscribe` と `sessions.unsubscribe` は、現在のWSクライアントの
  セッション変更イベント購読を切り替えます。
- `sessions.messages.subscribe` と `sessions.messages.unsubscribe` は、
  1つのセッションのトランスクリプト/メッセージイベント購読を切り替えます。
- `sessions.preview` は、特定のセッションキー向けに制限付きトランスクリプトプレビューを返します。
- `sessions.resolve` は、セッションターゲットを解決または正規化します。
- `sessions.create` は、新しいセッションエントリを作成します。
- `sessions.send` は、既存のセッションにメッセージを送信します。
- `sessions.steer` は、アクティブなセッション向けの中断して誘導するバリアントです。
- `sessions.abort` は、セッションのアクティブな作業を中止します。
- `sessions.patch` は、セッションメタデータ/上書きを更新します。
- `sessions.reset`、`sessions.delete`、`sessions.compact` は、セッション保守を実行します。
- `sessions.get` は、保存済みの完全なセッション行を返します。
- chat実行では引き続き `chat.history`、`chat.send`、`chat.abort`、`chat.inject` を使用します。
- `chat.history` は、UIクライアント向けに表示正規化されています: インラインディレクティブタグは
  表示テキストから削除され、プレーンテキストのツール呼び出しXMLペイロード
  （`<tool_call>...</tool_call>`、`<function_call>...</function_call>`、
  `<tool_calls>...</tool_calls>`、`<function_calls>...</function_calls>`、
  および切り詰められたツール呼び出しブロックを含む）と、
  漏れ出したASCII/全角のモデル制御トークンは削除され、正確に `NO_REPLY` /
  `no_reply` である純粋なsilent-token assistant行は省略され、
  過大な行はプレースホルダーに置き換えられる場合があります。

#### デバイスpairingとデバイストークン

- `device.pair.list` は、保留中および承認済みのpair済みデバイスを返します。
- `device.pair.approve`、`device.pair.reject`、`device.pair.remove` は、
  デバイスpairingレコードを管理します。
- `device.token.rotate` は、pairing済みデバイストークンを承認済みroleおよび
  scopeの範囲内でローテーションします。
- `device.token.revoke` は、pairing済みデバイストークンを失効させます。

#### node pairing、invoke、および保留中作業

- `node.pair.request`、`node.pair.list`、`node.pair.approve`、
  `node.pair.reject`、`node.pair.verify` は、node pairingとブートストラップ
  検証を扱います。
- `node.list` と `node.describe` は、既知/接続中のノード状態を返します。
- `node.rename` は、pairing済みノードラベルを更新します。
- `node.invoke` は、接続中ノードにコマンドを転送します。
- `node.invoke.result` は、invokeリクエストの結果を返します。
- `node.event` は、ノード起点イベントをGatewayへ戻します。
- `node.canvas.capability.refresh` は、スコープ付きcanvas-capabilityトークンを更新します。
- `node.pending.pull` と `node.pending.ack` は、接続中ノードのキューAPIです。
- `node.pending.enqueue` と `node.pending.drain` は、
  オフライン/切断中ノード向けの永続保留作業を管理します。

#### 承認ファミリー

- `exec.approval.request`、`exec.approval.get`、`exec.approval.list`、
  `exec.approval.resolve` は、単発のexec承認リクエストと、
  保留中承認の検索/再生を扱います。
- `exec.approval.waitDecision` は、1件の保留中exec承認を待機し、
  最終判断を返します（タイムアウト時は `null`）。
- `exec.approvals.get` と `exec.approvals.set` は、Gateway exec承認
  ポリシースナップショットを管理します。
- `exec.approvals.node.get` と `exec.approvals.node.set` は、
  ノードリレーコマンド経由でnodeローカルのexec承認ポリシーを管理します。
- `plugin.approval.request`、`plugin.approval.list`、
  `plugin.approval.waitDecision`、`plugin.approval.resolve` は、
  プラグイン定義の承認フローを扱います。

#### その他の主要ファミリー

- automation:
  - `wake` は、即時または次のheartbeatでのwakeテキスト注入をスケジュールします
  - `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`,
    `cron.run`, `cron.runs`
- Skills/ツール: `skills.*`, `tools.catalog`, `tools.effective`

### 一般的なイベントファミリー

- `chat`: `chat.inject` などの、UI chat更新やその他のトランスクリプト専用chatイベント。
- `session.message` と `session.tool`: 購読されたセッション向けの
  トランスクリプト/イベントストリーム更新。
- `sessions.changed`: セッションインデックスまたはメタデータが変更された。
- `presence`: systemプレゼンススナップショット更新。
- `tick`: 定期的なkeepalive / 生存確認イベント。
- `health`: Gatewayヘルススナップショット更新。
- `heartbeat`: heartbeatイベントストリーム更新。
- `cron`: cron実行/ジョブ変更イベント。
- `shutdown`: Gatewayシャットダウン通知。
- `node.pair.requested` / `node.pair.resolved`: node pairingライフサイクル。
- `node.invoke.request`: node invokeリクエストのブロードキャスト。
- `device.pair.requested` / `device.pair.resolved`: pair済みデバイスライフサイクル。
- `voicewake.changed`: ウェイクワードトリガー設定が変更された。
- `exec.approval.requested` / `exec.approval.resolved`: exec承認
  ライフサイクル。
- `plugin.approval.requested` / `plugin.approval.resolved`: プラグイン承認
  ライフサイクル。

### nodeヘルパーメソッド

- ノードは、自動許可チェック向けの現在のskill実行ファイル一覧を取得するために
  `skills.bins` を呼び出せます。

### operatorヘルパーメソッド

- operatorは、agent向けのランタイムツールカタログを取得するために
  `tools.catalog`（`operator.read`）を呼び出せます。レスポンスには、グループ化された
  ツールと由来メタデータが含まれます:
  - `source`: `core` または `plugin`
  - `pluginId`: `source="plugin"` のときのプラグイン所有者
  - `optional`: プラグインツールがオプションかどうか
- operatorは、セッションのランタイム有効ツール
  インベントリを取得するために `tools.effective`（`operator.read`）を呼び出せます。
  - `sessionKey` は必須です。
  - Gatewayは、呼び出し元が指定した認証や配信コンテキストを受け取る代わりに、
    信頼できるランタイムコンテキストをサーバー側でセッションから導出します。
  - レスポンスはセッションスコープであり、core、plugin、channelツールを含む、
    現在アクティブな会話で今すぐ使えるものを反映します。
- operatorは、agent向けの表示可能なskillインベントリを取得するために
  `skills.status`（`operator.read`）を呼び出せます。
  - `agentId` は任意です。省略するとデフォルトagent workspaceを読み取ります。
  - レスポンスには、rawシークレット値を公開することなく、
    適格性、不足している要件、設定チェック、およびサニタイズ済みinstall optionsが含まれます。
- operatorは、ClawHub検出メタデータ向けに `skills.search` と `skills.detail`
  （`operator.read`）を呼び出せます。
- operatorは、2つのモードで `skills.install`（`operator.admin`）を呼び出せます:
  - ClawHubモード: `{ source: "clawhub", slug, version?, force? }` は、
    デフォルトagent workspaceの `skills/` ディレクトリにskillフォルダーをインストールします。
  - Gateway installerモード: `{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    は、Gatewayホスト上で宣言された `metadata.openclaw.install` アクションを実行します。
- operatorは、2つのモードで `skills.update`（`operator.admin`）を呼び出せます:
  - ClawHubモードでは、1つの追跡対象slugまたはデフォルトagent workspace内の
    すべての追跡対象ClawHubインストールを更新します。
  - Configモードでは、`enabled`、
    `apiKey`、`env` などの `skills.entries.<skillKey>` 値をパッチします。

## exec承認

- execリクエストに承認が必要な場合、Gatewayは `exec.approval.requested` をブロードキャストします。
- operatorクライアントは、`exec.approval.resolve` を呼び出して解決します
  （`operator.approvals` scopeが必要）。
- `host=node` の場合、`exec.approval.request` には `systemRunPlan`
  （正規の `argv`/`cwd`/`rawCommand`/sessionメタデータ）が含まれていなければなりません。
  `systemRunPlan` がないリクエストは拒否されます。
- 承認後、転送された `node.invoke system.run` 呼び出しは、その正規の
  `systemRunPlan` を権威あるコマンド/cwd/sessionコンテキストとして再利用します。
- 呼び出し元が prepare と最終的な承認済み `system.run` 転送の間で
  `command`、`rawCommand`、`cwd`、`agentId`、`sessionKey` を変更した場合、
  Gatewayは変更されたペイロードを信頼せず、実行を拒否します。

## agent配信フォールバック

- `agent` リクエストには、アウトバウンド配信を要求するための `deliver=true` を含めることができます。
- `bestEffortDeliver=false` は厳格な動作を維持します: 解決不能または内部専用の配信先は `INVALID_REQUEST` を返します。
- `bestEffortDeliver=true` は、外部配信可能ルートを解決できない場合
  （たとえば内部/webchatセッションや曖昧なマルチチャネル設定）に、
  セッション専用実行へのフォールバックを許可します。

## バージョニング

- `PROTOCOL_VERSION` は `src/gateway/protocol/schema.ts` にあります。
- クライアントは `minProtocol` + `maxProtocol` を送信し、サーバーは不一致を拒否します。
- スキーマ + モデルはTypeBox定義から生成されます:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

## 認証

- 共有シークレットGateway認証では、設定された認証モードに応じて
  `connect.params.auth.token` または
  `connect.params.auth.password` を使用します。
- Tailscale Serve のようなIDを伴うモード
  （`gateway.auth.allowTailscale: true`）や、non-loopback
  `gateway.auth.mode: "trusted-proxy"` では、
  `connect.params.auth.*` の代わりにリクエストヘッダーから接続認証チェックを満たします。
- private-ingress `gateway.auth.mode: "none"` は、共有シークレット接続認証を
  完全にスキップします。このモードを公開/信頼できないingressで公開しないでください。
- pairing後、Gatewayは接続のrole + scopeにスコープされた**デバイストークン**を発行します。
  これは `hello-ok.auth.deviceToken` で返され、クライアントは将来の接続のために
  これを永続化する必要があります。
- クライアントは、接続成功後に主要な `hello-ok.auth.deviceToken` を永続化する必要があります。
- その**保存済み**デバイストークンで再接続する場合は、そのトークンに対して以前承認された
  scopeセットも再利用する必要があります。これにより、すでに許可された
  read/probe/statusアクセスが保持され、再接続時により狭い暗黙的な
  admin専用scopeへ静かに縮小されるのを防げます。
- 通常の接続認証の優先順位は、明示的な共有token/passwordが最優先で、次に
  明示的な `deviceToken`、次に保存済みのデバイスごとのトークン、
  最後にブートストラップトークンです。
- 追加の `hello-ok.auth.deviceTokens` エントリは、ブートストラップ引き継ぎトークンです。
  それらは、`wss://` や loopback/local pairing のような信頼できる転送上で
  接続がブートストラップ認証を使った場合にのみ永続化してください。
- クライアントが**明示的な** `deviceToken` または明示的な `scopes` を指定した場合、
  その呼び出し元要求のscopeセットが権威を持ち続けます。キャッシュされたscopeが再利用されるのは、
  クライアントが保存済みのデバイスごとのトークンを再利用している場合だけです。
- デバイストークンは `device.token.rotate` と
  `device.token.revoke` でローテーション/失効できます
  （`operator.pairing` scopeが必要）。
- トークン発行/ローテーションは、そのデバイスのpairingエントリに記録された
  承認済みroleセットの範囲内に制限されます。トークンのローテーションで、
  pairing承認が一度も許可していないroleへデバイスを拡張することはできません。
- pair済みデバイストークンセッションでは、呼び出し元が `operator.admin` も
  持っていない限り、デバイス管理は自己スコープになります:
  non-admin呼び出し元は、自分**自身**のデバイスエントリのみを削除/失効/ローテーションできます。
- `device.token.rotate` は、要求されたoperator scopeセットも
  呼び出し元の現在のセッションscopeに対してチェックします。non-admin呼び出し元は、
  現在自分が保持しているものより広いoperator scopeセットへトークンをローテーションできません。
- 認証失敗には `error.details.code` と復旧ヒントが含まれます:
  - `error.details.canRetryWithDeviceToken`（boolean）
  - `error.details.recommendedNextStep`（`retry_with_device_token`, `update_auth_configuration`, `update_auth_credentials`, `wait_then_retry`, `review_auth_configuration`）
- `AUTH_TOKEN_MISMATCH` に対するクライアント動作:
  - 信頼されたクライアントは、キャッシュされたデバイスごとのトークンで
    1回だけ制限付き再試行を試みてもかまいません。
  - その再試行も失敗した場合、クライアントは自動再接続ループを停止し、
    operator向けの対処ガイダンスを表示する必要があります。

## デバイスidentity + pairing

- ノードは、キーペアフィンガープリントから導出された安定したデバイスidentity（`device.id`）を含める必要があります。
- Gatewayは、デバイス + roleごとにトークンを発行します。
- ローカル自動承認が有効でない限り、新しいデバイスIDにはpairing承認が必要です。
- pairing自動承認は、直接のlocal loopback接続を中心にしています。
- OpenClawには、信頼された共有シークレットヘルパーフロー向けの
  狭いbackend/container-local self-connectパスもあります。
- 同一ホストのtailnetやLAN接続も、引き続きリモートとして扱われ、
  pairing承認が必要です。
- すべてのWSクライアントは、`connect` 中に `device` identity を含める必要があります
  （operator + node）。
  Control UIがこれを省略できるのは、次のモードだけです:
  - localhost専用の非安全HTTP互換性向け `gateway.controlUi.allowInsecureAuth=true`
  - `gateway.auth.mode: "trusted-proxy"` でのoperator Control UI認証成功時。
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true`（緊急避難用、重大なセキュリティ低下）。
- すべての接続は、サーバー提供の `connect.challenge` nonce に署名しなければなりません。

### デバイス認証移行診断

依然としてpre-challenge署名動作を使っているレガシークライアント向けに、
`connect` は現在、安定した `error.details.reason` の下で
`error.details.code` に `DEVICE_AUTH_*` 詳細コードを返します。

一般的な移行失敗:

| メッセージ                     | details.code                     | details.reason           | 意味                                                  |
| ------------------------------ | -------------------------------- | ------------------------ | ----------------------------------------------------- |
| `device nonce required`        | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | クライアントが `device.nonce` を省略した（または空を送信した）。 |
| `device nonce mismatch`        | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | クライアントが古い/誤ったnonceで署名した。            |
| `device signature invalid`     | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | 署名ペイロードがv2ペイロードと一致しない。            |
| `device signature expired`     | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | 署名済みタイムスタンプが許容スキュー範囲外である。    |
| `device identity mismatch`     | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id` が公開鍵フィンガープリントと一致しない。  |
| `device public key invalid`    | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | 公開鍵の形式/正規化に失敗した。                       |

移行ターゲット:

- 常に `connect.challenge` を待つ。
- サーバーnonceを含むv2ペイロードに署名する。
- 同じnonceを `connect.params.device.nonce` で送る。
- 推奨署名ペイロードは `v3` で、device/client/role/scopes/token/nonce
  フィールドに加えて `platform` と `deviceFamily` も結び付けます。
- レガシーな `v2` 署名も互換性のため引き続き受け入れられますが、
  pair済みデバイスのメタデータ固定が、再接続時のコマンドポリシーを引き続き制御します。

## TLS + ピン留め

- WS接続ではTLSがサポートされています。
- クライアントは、必要に応じてGateway証明書のフィンガープリントをピン留めできます
  （`gateway.tls` 設定、および `gateway.remote.tlsFingerprint` または
  CLI `--tls-fingerprint` を参照）。

## スコープ

このプロトコルは、**完全なGateway API**（status、channels、models、chat、
agent、sessions、nodes、approvalsなど）を公開します。正確なサーフェスは
`src/gateway/protocol/schema.ts` 内のTypeBoxスキーマで定義されます。
