---
read_when:
    - OpenClaw で Matrix をセットアップする場合
    - Matrix の E2EE と検証を設定する場合
summary: Matrix のサポート状況、セットアップ、および設定例
title: Matrix
x-i18n:
    generated_at: "2026-04-08T02:17:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: ec926df79a41fa296d63f0ec7219d0f32e075628d76df9ea490e93e4c5030f83
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix は OpenClaw 用の Matrix バンドルチャネル plugin です。
公式の `matrix-js-sdk` を使用し、DM、ルーム、スレッド、メディア、リアクション、投票、位置情報、E2EE をサポートします。

## バンドル plugin

Matrix は現在の OpenClaw リリースにバンドル plugin として同梱されているため、通常の
パッケージ済みビルドでは別途インストールは不要です。

古いビルドまたは Matrix を含まないカスタムインストールを使用している場合は、
手動でインストールしてください。

npm からインストール:

```bash
openclaw plugins install @openclaw/matrix
```

ローカルチェックアウトからインストール:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

plugin の動作とインストールルールについては、[Plugins](/ja-JP/tools/plugin) を参照してください。

## セットアップ

1. Matrix plugin が利用可能であることを確認します。
   - 現在のパッケージ版 OpenClaw リリースには、すでに同梱されています。
   - 古いインストールやカスタムインストールでは、上記のコマンドで手動追加できます。
2. homeserver 上に Matrix アカウントを作成します。
3. `channels.matrix` を次のいずれかで設定します。
   - `homeserver` + `accessToken`、または
   - `homeserver` + `userId` + `password`。
4. Gateway を再起動します。
5. bot との DM を開始するか、ルームに招待します。
   - 新しい Matrix 招待は、`channels.matrix.autoJoin` で許可されている場合にのみ機能します。

対話式セットアップのパス:

```bash
openclaw channels add
openclaw configure --section channels
```

Matrix ウィザードが実際に尋ねる内容:

- homeserver URL
- 認証方式: アクセストークンまたはパスワード
- パスワード認証を選んだ場合のみ user ID
- 任意のデバイス名
- E2EE を有効にするかどうか
- Matrix ルームアクセスを今すぐ設定するかどうか
- Matrix の招待自動参加を今すぐ設定するかどうか
- 招待自動参加を有効にした場合、それを `allowlist`、`always`、`off` のどれにするか

重要なウィザードの動作:

- 選択したアカウントに対する Matrix 認証 env var がすでに存在し、そのアカウントの認証がまだ config に保存されていない場合、ウィザードは env ショートカットを提示するため、secret を config にコピーせず env var に保持したままセットアップできます。
- 別の Matrix アカウントを対話的に追加すると、入力したアカウント名は config と env var で使われるアカウント ID に正規化されます。たとえば、`Ops Bot` は `ops-bot` になります。
- DM allowlist のプロンプトでは、完全な `@user:server` の値をそのまま受け付けます。表示名が使えるのは、ライブディレクトリ検索でちょうど 1 件の一致が見つかった場合のみです。それ以外の場合、ウィザードは完全な Matrix ID で再試行するよう求めます。
- ルーム allowlist のプロンプトでは、ルーム ID とエイリアスを直接受け付けます。参加済みルーム名のライブ解決もできますが、解決できなかった名前はセットアップ中に入力されたまま保持されるだけで、後のランタイム allowlist 解決では無視されます。`!room:server` または `#alias:server` の使用を推奨します。
- ウィザードは招待自動参加のステップの前に明示的な警告を表示します。これは `channels.matrix.autoJoin` のデフォルトが `off` だからです。設定しない限り、agent は招待されたルームや新しい DM 形式の招待に参加しません。
- 招待自動参加の allowlist モードでは、安定した招待ターゲットのみを使用してください: `!roomId:server`、`#alias:server`、または `*`。単なるルーム名は拒否されます。
- ランタイムのルーム/セッション識別子は安定した Matrix ルーム ID を使います。ルームで宣言されたエイリアスは検索入力としてのみ使われ、長期的なセッションキーや安定したグループ識別子としては使われません。
- 保存前にルーム名を解決するには、`openclaw channels resolve --channel matrix "Project Room"` を使用します。

<Warning>
`channels.matrix.autoJoin` のデフォルトは `off` です。

これを未設定のままにすると、bot は招待されたルームや新しい DM 形式の招待に参加しないため、手動で先に参加しない限り、新しいグループや招待 DM に現れません。

受け入れる招待を制限したい場合は、`autoJoin: "allowlist"` を `autoJoinAllowlist` と組み合わせて設定するか、すべての招待に参加させたい場合は `autoJoin: "always"` を設定してください。

`allowlist` モードでは、`autoJoinAllowlist` は `!roomId:server`、`#alias:server`、または `*` だけを受け付けます。
</Warning>

allowlist の例:

```json5
{
  channels: {
    matrix: {
      autoJoin: "allowlist",
      autoJoinAllowlist: ["!ops:example.org", "#support:example.org"],
      groups: {
        "!ops:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

すべての招待に参加:

```json5
{
  channels: {
    matrix: {
      autoJoin: "always",
    },
  },
}
```

最小限のトークンベース設定:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      dm: { policy: "pairing" },
    },
  },
}
```

パスワードベースのセットアップ（ログイン後にトークンがキャッシュされます）:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: allowlist secret
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

Matrix はキャッシュされた認証情報を `~/.openclaw/credentials/matrix/` に保存します。
デフォルトアカウントは `credentials.json` を使用し、名前付きアカウントは `credentials-<account>.json` を使用します。
そこにキャッシュ済み認証情報が存在する場合、現在の認証が config に直接設定されていなくても、OpenClaw は Matrix をセットアップ、doctor、チャネルステータス検出の対象として設定済みとみなします。

環境変数の対応項目（config キーが設定されていない場合に使用されます）:

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

デフォルト以外のアカウントでは、アカウントスコープ付き env var を使用します:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

アカウント `ops` の例:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

正規化されたアカウント ID `ops-bot` では次を使用します:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix はアカウント ID 内の句読点をエスケープし、スコープ付き env var の衝突を防ぎます。
たとえば `-` は `_X2D_` になるため、`ops-prod` は `MATRIX_OPS_X2D_PROD_*` に対応します。

対話式ウィザードが env-var ショートカットを提示するのは、それらの認証 env var がすでに存在し、かつ選択したアカウントに Matrix 認証がまだ config に保存されていない場合だけです。

## 設定例

これは、DM pairing、ルーム allowlist、有効化された E2EE を含む実用的なベースライン設定です。

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,

      dm: {
        policy: "pairing",
        sessionScope: "per-room",
        threadReplies: "off",
      },

      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },

      autoJoin: "allowlist",
      autoJoinAllowlist: ["!roomid:example.org"],
      threadReplies: "inbound",
      replyToMode: "off",
      streaming: "partial",
    },
  },
}
```

`autoJoin` は Matrix の招待全般に適用され、ルーム/グループ招待だけには限定されません。
これには新しい DM 形式の招待も含まれます。招待時点では、OpenClaw はその
招待されたルームが最終的に DM として扱われるのかグループとして扱われるのかを確実には判断できないため、すべての招待は最初に同じ
`autoJoin` 判定を通ります。`dm.policy` は bot が参加した後、そのルームが
DM と分類されてから適用されるため、`autoJoin` は参加動作を制御し、`dm.policy` は返信/アクセス
動作を制御します。

## ストリーミングプレビュー

Matrix の返信ストリーミングはオプトインです。

OpenClaw に単一のライブプレビュー
返信を送信させ、モデルがテキストを生成している間にそのプレビューをその場で編集し、
返信完了時に確定したい場合は、`channels.matrix.streaming` を `"partial"` に設定します:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` がデフォルトです。OpenClaw は最終返信を待って一度だけ送信します。
- `streaming: "partial"` は、現在の assistant ブロック用に編集可能な 1 つのプレビューメッセージを通常の Matrix テキストメッセージとして作成します。これにより Matrix の従来の「まずプレビュー」通知動作が保たれるため、標準クライアントでは完成したブロックではなく最初のストリーミングプレビューテキストで通知される場合があります。
- `streaming: "quiet"` は、現在の assistant ブロック用に編集可能な静かなプレビュー notice を 1 つ作成します。これは、最終化されたプレビュー編集に対する受信者の push rule も設定する場合にのみ使ってください。
- `blockStreaming: true` は別個の Matrix 進捗メッセージを有効にします。プレビューストリーミングが有効な場合、Matrix は現在のブロックのライブ下書きを保持し、完了したブロックは別メッセージとして保持します。
- プレビューストリーミングが有効で `blockStreaming` が off の場合、Matrix はライブ下書きをその場で編集し、ブロックまたはターン完了時に同じイベントを確定します。
- プレビューが 1 つの Matrix イベントに収まらなくなった場合、OpenClaw はプレビューストリーミングを停止し、通常の最終配信にフォールバックします。
- メディア返信は引き続き通常どおり添付ファイルを送信します。古いプレビューを安全に再利用できなくなった場合、OpenClaw は最終メディア返信を送る前にそれを redact します。
- プレビュー編集は Matrix API 呼び出しを余分に消費します。最も保守的なレート制限動作を望む場合は、ストリーミングを無効のままにしてください。

`blockStreaming` 自体では下書きプレビューは有効になりません。
プレビュー編集には `streaming: "partial"` または `streaming: "quiet"` を使用し、そのうえで完了した assistant ブロックも別個の進捗メッセージとして表示したい場合にだけ `blockStreaming: true` を追加してください。

カスタム push rule を使わずに標準的な Matrix 通知が必要な場合は、プレビュー先行動作には `streaming: "partial"` を使うか、最終結果のみ配信するために `streaming` を無効のままにしてください。`streaming: "off"` の場合:

- `blockStreaming: true` は、完了した各ブロックを通常の通知付き Matrix メッセージとして送信します。
- `blockStreaming: false` は、最終的に完成した返信のみを通常の通知付き Matrix メッセージとして送信します。

### セルフホスト環境での静かな最終化プレビュー用 push rule

独自の Matrix インフラを運用していて、静かなプレビューでブロックまたは
最終返信が完了したときだけ通知したい場合は、`streaming: "quiet"` を設定し、最終化されたプレビュー編集向けのユーザーごとの push rule を追加してください。

これは通常、homeserver 全体の設定変更ではなく、受信ユーザー側の設定です。

始める前の簡単な対応表:

- recipient user = 通知を受け取る人
- bot user = 返信を送る OpenClaw Matrix アカウント
- 以下の API 呼び出しでは受信ユーザーのアクセストークンを使います
- push rule の `sender` は bot user の完全な MXID と一致させます

1. OpenClaw で静かなプレビューを使うよう設定します:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. 受信側アカウントがすでに通常の Matrix push 通知を受け取れていることを確認します。静かなプレビュー
   ルールが機能するのは、そのユーザーですでに pusher/device が動作している場合だけです。

3. 受信ユーザーのアクセストークンを取得します。
   - bot のトークンではなく、受信側ユーザーのトークンを使用します。
   - 既存のクライアントセッショントークンを再利用するのが通常は最も簡単です。
   - 新しいトークンを発行する必要がある場合は、標準の Matrix Client-Server API でログインできます:

```bash
curl -sS -X POST \
  "https://matrix.example.org/_matrix/client/v3/login" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "m.login.password",
    "identifier": {
      "type": "m.id.user",
      "user": "@alice:example.org"
    },
    "password": "REDACTED"
  }'
```

4. 受信側アカウントにすでに pusher があることを確認します:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

これでアクティブな pusher/device が返らない場合は、下記の
OpenClaw ルールを追加する前に、まず通常の Matrix 通知を修正してください。

OpenClaw は最終化されたテキストのみのプレビュー編集に次の印を付けます:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. これらの通知を受け取る各受信側アカウントに対して、override push rule を作成します:

```bash
curl -sS -X PUT \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname" \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "conditions": [
      { "kind": "event_match", "key": "type", "pattern": "m.room.message" },
      {
        "kind": "event_property_is",
        "key": "content.m\\.relates_to.rel_type",
        "value": "m.replace"
      },
      {
        "kind": "event_property_is",
        "key": "content.com\\.openclaw\\.finalized_preview",
        "value": true
      },
      { "kind": "event_match", "key": "sender", "pattern": "@bot:example.org" }
    ],
    "actions": [
      "notify",
      { "set_tweak": "sound", "value": "default" },
      { "set_tweak": "highlight", "value": false }
    ]
  }'
```

コマンド実行前に次の値を置き換えてください:

- `https://matrix.example.org`: あなたの homeserver のベース URL
- `$USER_ACCESS_TOKEN`: 受信側ユーザーのアクセストークン
- `openclaw-finalized-preview-botname`: この受信側ユーザーに対するこの bot 用の一意な rule ID
- `@bot:example.org`: 受信側ユーザーの MXID ではなく、あなたの OpenClaw Matrix bot MXID

複数 bot 構成で重要な点:

- Push rule は `ruleId` をキーにします。同じ rule ID に対して `PUT` を再実行すると、その 1 つのルールが更新されます。
- 1 人の受信ユーザーが複数の OpenClaw Matrix bot アカウントから通知を受ける必要がある場合は、各 sender 一致ごとに一意な rule ID を持つルールを bot ごとに 1 つ作成してください。
- シンプルなパターンは `openclaw-finalized-preview-<botname>` です。たとえば `openclaw-finalized-preview-ops` や `openclaw-finalized-preview-support` です。

このルールはイベント送信者に対して評価されます:

- 受信側ユーザーのトークンで認証する
- `sender` を OpenClaw bot MXID と一致させる

6. ルールが存在することを確認します:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. ストリーミング返信をテストします。quiet モードでは、ルームには静かな下書きプレビューが表示され、
   ブロックまたはターンが完了すると最終のその場編集で 1 回通知されるはずです。

後でルールを削除する必要がある場合は、受信側ユーザーのトークンで同じ rule ID を削除してください:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

注意:

- ルールの作成には bot のトークンではなく、受信側ユーザーのアクセストークンを使用してください。
- 新しいユーザー定義 `override` ルールはデフォルトの抑制ルールより前に挿入されるため、追加の並び順パラメーターは不要です。
- これは、OpenClaw が安全にその場で最終化できるテキストのみのプレビュー編集にのみ影響します。メディアフォールバックや古いプレビューフォールバックでは、引き続き通常の Matrix 配信を使います。
- `GET /_matrix/client/v3/pushers` で pusher が表示されない場合、そのユーザーはそのアカウント/device でまだ動作する Matrix push 配信を持っていません。

#### Synapse

Synapse では、通常は上記のセットアップだけで十分です:

- 最終化された OpenClaw プレビュー通知のために特別な `homeserver.yaml` 変更は不要です。
- Synapse デプロイメントですでに通常の Matrix push 通知が送られている場合、ユーザートークン + 上記の `pushrules` 呼び出しが主なセットアップ手順です。
- Synapse をリバースプロキシや worker の背後で実行している場合は、`/_matrix/client/.../pushrules/` が正しく Synapse に到達することを確認してください。
- Synapse worker を使用している場合は、pusher が健全であることを確認してください。push 配信はメインプロセスまたは `synapse.app.pusher` / 設定された pusher worker によって処理されます。

#### Tuwunel

Tuwunel では、上記と同じセットアップフローと push-rule API 呼び出しを使用してください:

- 最終化プレビューマーカー自体に対する Tuwunel 固有の設定は不要です。
- そのユーザーで通常の Matrix 通知がすでに動作している場合、ユーザートークン + 上記の `pushrules` 呼び出しが主なセットアップ手順です。
- ユーザーが別の device でアクティブな間に通知が消えるように見える場合は、`suppress_push_when_active` が有効か確認してください。Tuwunel は 2025 年 9 月 12 日の Tuwunel 1.4.2 でこのオプションを追加しており、1 つの device がアクティブな間は他の device への push を意図的に抑制できます。

## 暗号化と検証

暗号化された（E2EE）ルームでは、送信画像イベントに `thumbnail_file` を使うため、画像プレビューは完全な添付ファイルと一緒に暗号化されます。暗号化されていないルームでは、引き続き通常の `thumbnail_url` を使います。設定は不要です。plugin が E2EE 状態を自動検出します。

### Bot 間ルーム

デフォルトでは、他の設定済み OpenClaw Matrix アカウントからの Matrix メッセージは無視されます。

agent 間の Matrix トラフィックを意図的に許可したい場合は、`allowBots` を使用します:

```json5
{
  channels: {
    matrix: {
      allowBots: "mentions", // true | "mentions"
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

- `allowBots: true` は、許可されたルームと DM において、他の設定済み Matrix bot アカウントからのメッセージを受け入れます。
- `allowBots: "mentions"` は、ルーム内でこの bot への明示的な mention がある場合に限り、そのようなメッセージを受け入れます。DM は引き続き許可されます。
- `groups.<room>.allowBots` は、1 つのルームに対してアカウントレベル設定を上書きします。
- OpenClaw は自己返信ループを避けるため、同じ Matrix user ID からのメッセージは引き続き無視します。
- Matrix にはここでネイティブな bot フラグはありません。OpenClaw は「bot authored」を「この OpenClaw Gateway 上の別の設定済み Matrix アカウントによって送信されたもの」として扱います。

共有ルームで bot 間トラフィックを有効にする場合は、厳格なルーム allowlist と mention 要件を使用してください。

暗号化を有効にする:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

検証状態を確認する:

```bash
openclaw matrix verify status
```

詳細ステータス（完全な診断情報）:

```bash
openclaw matrix verify status --verbose
```

保存された recovery key を機械可読出力に含める:

```bash
openclaw matrix verify status --include-recovery-key --json
```

クロス署名と検証状態をブートストラップする:

```bash
openclaw matrix verify bootstrap
```

マルチアカウント対応: `channels.matrix.accounts` にアカウントごとの認証情報と任意の `name` を指定して使用します。共有パターンについては [Configuration reference](/ja-JP/gateway/configuration-reference#multi-account-all-channels) を参照してください。

詳細なブートストラップ診断:

```bash
openclaw matrix verify bootstrap --verbose
```

ブートストラップ前にクロス署名 ID を強制的に新規リセットする:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

recovery key でこの device を検証する:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

device 検証の詳細:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

ルームキー backup の健全性を確認する:

```bash
openclaw matrix verify backup status
```

backup 健全性の詳細診断:

```bash
openclaw matrix verify backup status --verbose
```

サーバー backup からルームキーを復元する:

```bash
openclaw matrix verify backup restore
```

復元の詳細診断:

```bash
openclaw matrix verify backup restore --verbose
```

現在のサーバー backup を削除し、新しい backup ベースラインを作成します。保存済みの
backup key を正常に読み込めない場合、このリセットでは secret storage も再作成されることがあり、
将来のコールドスタートで新しい backup key を読み込めるようになります:

```bash
openclaw matrix verify backup reset --yes
```

すべての `verify` コマンドはデフォルトで簡潔な出力です（内部 SDK の quiet ログも含む）で、詳細な診断情報は `--verbose` を付けた場合にのみ表示されます。
スクリプトで使う場合は、完全な機械可読出力として `--json` を使用してください。

マルチアカウント構成では、`--account <id>` を渡さない限り、Matrix CLI コマンドは暗黙の Matrix デフォルトアカウントを使用します。
複数の名前付きアカウントを設定している場合は、先に `channels.matrix.defaultAccount` を設定してください。そうしないと、それらの暗黙的な CLI 操作は停止して明示的なアカウント選択を求めます。
検証や device 操作の対象を明示的に名前付きアカウントにしたい場合は、常に `--account` を使用してください:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

暗号化が無効な場合、または名前付きアカウントで利用できない場合、Matrix の警告と検証エラーはそのアカウントの config キーを指します。たとえば `channels.matrix.accounts.assistant.encryption` です。

### 「verified」の意味

OpenClaw は、この Matrix device が自分自身のクロス署名 ID によって検証されている場合にのみ verified として扱います。
実際には、`openclaw matrix verify status --verbose` は 3 つの信頼シグナルを表示します:

- `Locally trusted`: この device は現在のクライアントでのみ信頼されています
- `Cross-signing verified`: SDK が、この device はクロス署名によって検証済みだと報告しています
- `Signed by owner`: この device は自分自身の self-signing key によって署名されています

`Verified by owner` が `yes` になるのは、クロス署名検証または owner 署名が存在する場合だけです。
ローカル信頼だけでは、OpenClaw はその device を完全に検証済みとは扱いません。

### bootstrap が行うこと

`openclaw matrix verify bootstrap` は、暗号化された Matrix アカウント向けの修復およびセットアップコマンドです。
次のすべてを順に実行します:

- secret storage を bootstrap し、可能であれば既存の recovery key を再利用する
- クロス署名を bootstrap し、欠けている公開クロス署名キーをアップロードする
- 現在の device に印を付けてクロス署名することを試みる
- サーバー側のルームキー backup がまだ存在しない場合は新規作成する

homeserver がクロス署名キーのアップロードに対話式認証を要求する場合、OpenClaw はまず認証なしでアップロードを試し、次に `m.login.dummy`、そして `channels.matrix.password` が設定されている場合は `m.login.password` を試します。

`--force-reset-cross-signing` は、現在のクロス署名 ID を破棄して新しいものを作成したい場合にのみ使用してください。

現在のルームキー backup を意図的に破棄し、将来のメッセージ向けの新しい
backup ベースラインを開始したい場合は、`openclaw matrix verify backup reset --yes` を使用してください。
これは、復元不能な古い暗号化履歴が引き続き利用できないままであること、および現在の backup
secret を安全に読み込めない場合に OpenClaw が secret storage を再作成する可能性があることを受け入れる場合にのみ実行してください。

### 新しい backup ベースライン

将来の暗号化メッセージを引き続き機能させつつ、復元不能な古い履歴を失うことを受け入れる場合は、次のコマンドを順に実行してください:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

名前付き Matrix アカウントを明示的に対象にしたい場合は、各コマンドに `--account <id>` を追加してください。

### 起動時の動作

`encryption: true` の場合、Matrix はデフォルトで `startupVerification` を `"if-unverified"` に設定します。
起動時にこの device がまだ未検証であれば、Matrix は別の Matrix クライアントでの自己検証を要求し、
すでに保留中の要求がある場合は重複要求をスキップし、再起動後に再試行する前にローカルのクールダウンを適用します。
要求作成に成功した場合よりも、失敗した要求試行のほうがデフォルトでは早く再試行されます。
自動起動時要求を無効にするには `startupVerification: "off"` を設定するか、再試行間隔を短くまたは長くしたい場合は `startupVerificationCooldownHours`
を調整してください。

起動時には保守的な crypto bootstrap パスも自動的に実行されます。
このパスはまず現在の secret storage とクロス署名 ID の再利用を試み、明示的な bootstrap 修復フローを実行しない限りクロス署名をリセットしません。

起動時に壊れた bootstrap 状態が見つかり、`channels.matrix.password` が設定されている場合、OpenClaw はより厳密な修復パスを試みることがあります。
現在の device がすでに owner-signed である場合、OpenClaw はその ID を自動リセットする代わりに保持します。

以前の公開 Matrix plugin からのアップグレード:

- OpenClaw は可能であれば同じ Matrix アカウント、アクセストークン、device ID を自動的に再利用します。
- 実行可能な Matrix 移行変更が動く前に、OpenClaw は `~/Backups/openclaw-migrations/` の下に recovery snapshot を作成するか再利用します。
- 複数の Matrix アカウントを使う場合、古いフラットストアレイアウトからアップグレードする前に `channels.matrix.defaultAccount` を設定してください。これにより OpenClaw は、その共有されたレガシー状態をどのアカウントに受け渡すべきかを把握できます。
- 以前の plugin が Matrix ルームキー backup の復号キーをローカルに保存していた場合、起動時または `openclaw doctor --fix` がそれを新しい recovery-key フローに自動的にインポートします。
- Matrix アクセストークンが移行準備後に変更されていた場合、起動時は自動 backup 復元をあきらめる前に、保留中のレガシー復元状態を持つ兄弟トークンハッシュ storage root をスキャンします。
- 同じアカウント、homeserver、ユーザーに対して後で Matrix アクセストークンが変更された場合、OpenClaw は空の Matrix 状態ディレクトリから始める代わりに、最も完全な既存のトークンハッシュ storage root を再利用するようになりました。
- 次回の Gateway 起動時に、backup 済みルームキーは新しい crypto store に自動復元されます。
- 古い plugin にローカルのみのルームキーがあり、それが一度も backup されていなかった場合、OpenClaw は明確に警告します。それらのキーは以前の rust crypto store から自動エクスポートできないため、一部の古い暗号化履歴は手動復旧されるまで利用できないままになる可能性があります。
- 完全なアップグレードフロー、制限、復旧コマンド、一般的な移行メッセージについては、[Matrix migration](/ja-JP/install/migrating-matrix) を参照してください。

暗号化ランタイム状態は、アカウントごと・ユーザーごと・トークンハッシュごとの root 配下、
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/` に整理されます。
このディレクトリには sync store（`bot-storage.json`）、crypto store（`crypto/`）、
recovery key ファイル（`recovery-key.json`）、IndexedDB snapshot（`crypto-idb-snapshot.json`）、
thread bindings（`thread-bindings.json`）、および startup verification state（`startup-verification.json`）
が、これらの機能が使われている場合に含まれます。
トークンが変わってもアカウント ID が同じであれば、OpenClaw はそのアカウント/homeserver/user タプルに対する最良の既存
root を再利用するため、以前の sync state、crypto state、thread bindings、
startup verification state が引き続き見える状態に保たれます。

### Node crypto store モデル

この plugin の Matrix E2EE は、Node 上で公式の `matrix-js-sdk` Rust crypto パスを使用します。
このパスでは、再起動後も crypto state を保持したい場合に IndexedDB ベースの永続化が必要です。

OpenClaw は現在、Node でこれを次の方法で提供しています:

- SDK が期待する IndexedDB API shim として `fake-indexeddb` を使う
- `initRustCrypto` の前に `crypto-idb-snapshot.json` から Rust crypto IndexedDB の内容を復元する
- 初期化後およびランタイム中に、更新された IndexedDB の内容を `crypto-idb-snapshot.json` に永続化する
- `crypto-idb-snapshot.json` に対する snapshot の復元と永続化を advisory file lock で直列化し、Gateway ランタイムの永続化と CLI メンテナンスが同じ snapshot ファイルで競合しないようにする

これは互換性/保存のための仕組みであり、独自の crypto 実装ではありません。
snapshot ファイルは機密性の高いランタイム状態であり、厳格なファイル権限で保存されます。
OpenClaw のセキュリティモデルでは、Gateway ホストとローカル OpenClaw 状態ディレクトリはすでに信頼されたオペレーター境界内にあるため、これは主に別のリモート信頼境界というより運用上の耐久性の懸念です。

計画されている改善:

- 永続的な Matrix キーマテリアルに SecretRef サポートを追加し、recovery key や関連する store 暗号化 secret をローカルファイルだけでなく OpenClaw secrets provider から取得できるようにする

## プロファイル管理

選択したアカウントの Matrix セルフプロファイルを更新するには、次を使用します:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

名前付き Matrix アカウントを明示的に対象にしたい場合は、`--account <id>` を追加してください。

Matrix は `mxc://` の avatar URL を直接受け付けます。`http://` または `https://` の avatar URL を渡した場合、OpenClaw はまずそれを Matrix にアップロードし、解決された `mxc://` URL を `channels.matrix.avatarUrl`（または選択したアカウントの override）に保存し直します。

## 自動検証通知

Matrix は現在、検証ライフサイクル通知を strict DM 検証ルームへ `m.notice` メッセージとして直接投稿します。
これには以下が含まれます:

- 検証要求通知
- 検証準備完了通知（明示的な「Verify by emoji」案内付き）
- 検証開始と完了の通知
- 利用可能な場合の SAS 詳細（絵文字と数値）

別の Matrix クライアントからの受信検証要求は追跡され、OpenClaw が自動承認します。
自己検証フローでは、絵文字検証が利用可能になると OpenClaw は SAS フローも自動開始し、自分側を確認します。
別の Matrix ユーザー/device からの検証要求については、OpenClaw は要求を自動承認し、その後 SAS フローが通常どおり進行するのを待ちます。
検証を完了するには、引き続き Matrix クライアント上で絵文字または数値の SAS を比較し、「They match」を確認する必要があります。

OpenClaw は自己開始の重複フローを無条件には自動承認しません。起動時には、自己検証要求がすでに保留中であれば新しい要求を作成しません。

検証プロトコル/システム通知は agent chat pipeline には転送されないため、`NO_REPLY` は生成されません。

### Device hygiene

古い OpenClaw 管理下の Matrix device がアカウント上に蓄積し、暗号化ルームの信頼状態がわかりにくくなることがあります。
一覧表示するには:

```bash
openclaw matrix devices list
```

古い OpenClaw 管理下 device を削除するには:

```bash
openclaw matrix devices prune-stale
```

### Direct Room Repair

ダイレクトメッセージ状態の同期が崩れると、OpenClaw はライブ DM ではなく古いソロルームを指す古い `m.direct` マッピングを持ってしまうことがあります。ある相手の現在のマッピングを確認するには次を使用します:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

修復するには:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

修復では Matrix 固有のロジックを plugin 内に保ちます:

- まず、`m.direct` にすでにマップされている strict 1:1 DM を優先します
- それ以外では、そのユーザーとの現在参加中の strict 1:1 DM にフォールバックします
- 健全な DM が存在しない場合は、新しいダイレクトルームを作成し、それを指すように `m.direct` を書き換えます

修復フローは古いルームを自動削除しません。健全な DM を選択してマッピングを更新するだけなので、新しい Matrix 送信、検証通知、その他のダイレクトメッセージフローが再び正しいルームを対象にするようになります。

## スレッド

Matrix は、自動返信と message-tool send の両方でネイティブ Matrix スレッドをサポートします。

- `dm.sessionScope: "per-user"`（デフォルト）は Matrix DM ルーティングを送信者スコープに保つため、同じ相手に解決される複数の DM ルームで 1 つのセッションを共有できます。
- `dm.sessionScope: "per-room"` は、通常の DM 認証と allowlist チェックを使いながら、各 Matrix DM ルームを独自のセッションキーに分離します。
- 明示的な Matrix conversation binding は引き続き `dm.sessionScope` より優先されるため、バインドされたルームとスレッドは選択された対象セッションを維持します。
- `threadReplies: "off"` は返信をトップレベルに保ち、受信したスレッド付きメッセージも親セッション上に保ちます。
- `threadReplies: "inbound"` は、受信メッセージがすでにそのスレッド内にあった場合にのみ、そのスレッド内で返信します。
- `threadReplies: "always"` は、トリガーとなったメッセージをルートとするスレッド内にルーム返信を保持し、最初のトリガーメッセージから対応するスレッドスコープのセッションを通じてその会話をルーティングします。
- `dm.threadReplies` は DM のみについてトップレベル設定を上書きします。たとえば、ルームスレッドは分離したまま、DM はフラットに保てます。
- 受信したスレッド付きメッセージには、追加の agent コンテキストとしてスレッドルートメッセージが含まれます。
- message-tool send は、同じルーム、または同じ DM ユーザーターゲットが対象である場合、明示的な `threadId` が指定されない限り、現在の Matrix スレッドを自動継承するようになりました。
- 同一セッションでの DM ユーザーターゲット再利用が有効になるのは、現在のセッションメタデータから同じ Matrix アカウント上の同じ DM 相手であることが証明できる場合だけです。それ以外では OpenClaw は通常のユーザースコープルーティングにフォールバックします。
- OpenClaw が、同じ共有 Matrix DM セッション上で別の DM ルームと衝突する Matrix DM ルームを検出すると、thread bindings が有効で `dm.sessionScope` ヒントがある場合、そのルームに `/focus` エスケープハッチを示す 1 回限りの `m.notice` を投稿します。
- ランタイム thread binding は Matrix でサポートされます。`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`、および thread-bound の `/acp spawn` は Matrix ルームと DM で動作します。
- トップレベルの Matrix ルーム/DM での `/focus` は、`threadBindings.spawnSubagentSessions=true` の場合、新しい Matrix スレッドを作成し、それをターゲットセッションにバインドします。
- 既存の Matrix スレッド内で `/focus` または `/acp spawn --thread here` を実行すると、代わりにその現在のスレッドがバインドされます。

## ACP conversation binding

Matrix ルーム、DM、既存の Matrix スレッドは、chat surface を変えずに永続的な ACP workspace に変換できます。

素早いオペレーター向けフロー:

- 継続して使いたい Matrix DM、ルーム、または既存スレッドの中で `/acp spawn codex --bind here` を実行します。
- トップレベルの Matrix DM またはルームでは、現在の DM/ルームが chat surface のまま維持され、以後のメッセージは生成された ACP セッションへルーティングされます。
- 既存の Matrix スレッド内では、`--bind here` はその現在のスレッドをその場でバインドします。
- `/new` と `/reset` は同じバインド済み ACP セッションをその場でリセットします。
- `/acp close` は ACP セッションを閉じ、binding を削除します。

注意:

- `--bind here` は子 Matrix スレッドを作成しません。
- `threadBindings.spawnAcpSessions` が必要なのは `/acp spawn --thread auto|here` の場合だけで、そのとき OpenClaw は子 Matrix スレッドを作成またはバインドする必要があります。

### Thread Binding Config

Matrix は `session.threadBindings` からグローバルデフォルトを継承し、チャネルごとの override もサポートします:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrix の thread-bound spawn フラグはオプトインです:

- `threadBindings.spawnSubagentSessions: true` を設定すると、トップレベルの `/focus` が新しい Matrix スレッドを作成してバインドできるようになります。
- `threadBindings.spawnAcpSessions: true` を設定すると、`/acp spawn --thread auto|here` が ACP セッションを Matrix スレッドにバインドできるようになります。

## リアクション

Matrix は、送信リアクションアクション、受信リアクション通知、受信 ack リアクションをサポートします。

- 送信リアクション機能は `channels["matrix"].actions.reactions` で制御されます。
- `react` は特定の Matrix イベントにリアクションを追加します。
- `reactions` は特定の Matrix イベントに対する現在のリアクション概要を一覧表示します。
- `emoji=""` は、そのイベントに対する bot アカウント自身のリアクションを削除します。
- `remove: true` は、bot アカウントの指定された絵文字リアクションだけを削除します。

ack リアクションは標準の OpenClaw 解決順序を使用します:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- agent identity の絵文字フォールバック

ack リアクションスコープは次の順序で解決されます:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

リアクション通知モードは次の順序で解決されます:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- デフォルト: `own`

現在の動作:

- `reactionNotifications: "own"` は、bot が作成した Matrix メッセージを対象とする追加 `m.reaction` イベントを転送します。
- `reactionNotifications: "off"` はリアクションシステムイベントを無効にします。
- Matrix ではリアクション削除が独立した `m.reaction` 削除ではなく redaction として表現されるため、リアクション削除はまだシステムイベントとして合成されません。

## 履歴コンテキスト

- `channels.matrix.historyLimit` は、Matrix ルームメッセージが agent をトリガーしたときに `InboundHistory` として含める最近のルームメッセージ数を制御します。
- これは `messages.groupChat.historyLimit` にフォールバックします。両方が未設定の場合、有効なデフォルトは `0` なので、mention 制御されたルームメッセージはバッファされません。無効にするには `0` を設定してください。
- Matrix ルーム履歴はルーム専用です。DM は通常のセッション履歴を使い続けます。
- Matrix ルーム履歴は pending-only です。OpenClaw はまだ返信をトリガーしていないルームメッセージをバッファし、その mention やその他のトリガーが来た時点でそのウィンドウを snapshot します。
- 現在のトリガーメッセージは `InboundHistory` には含まれません。そのターンのメイン受信本文に残ります。
- 同じ Matrix イベントの再試行では、より新しいルームメッセージへずれていくのではなく、元の履歴 snapshot を再利用します。

## コンテキスト可視性

Matrix は、取得した返信テキスト、スレッドルート、保留中履歴などの補足ルームコンテキストに対する共有 `contextVisibility` 制御をサポートします。

- `contextVisibility: "all"` がデフォルトです。補足コンテキストは受信したまま保持されます。
- `contextVisibility: "allowlist"` は、アクティブなルーム/ユーザー allowlist チェックで許可された送信者に補足コンテキストを絞り込みます。
- `contextVisibility: "allowlist_quote"` は `allowlist` と同様に動作しますが、1 つの明示的な引用返信は保持します。

この設定は補足コンテキストの可視性に影響し、受信メッセージ自体が返信をトリガーできるかどうかには影響しません。
トリガー認可は引き続き `groupPolicy`、`groups`、`groupAllowFrom`、および DM policy 設定によって決まります。

## DM とルーム policy の例

```json5
{
  channels: {
    matrix: {
      dm: {
        policy: "allowlist",
        allowFrom: ["@admin:example.org"],
        threadReplies: "off",
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

mention 制御と allowlist の動作については、[Groups](/ja-JP/channels/groups) を参照してください。

Matrix DM の pairing 例:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

未承認の Matrix ユーザーが承認前にメッセージを送り続けた場合、OpenClaw は同じ保留中の pairing code を再利用し、新しい code を発行する代わりに短いクールダウン後に再度 reminder reply を送ることがあります。

共有 DM pairing フローと storage layout については、[Pairing](/ja-JP/channels/pairing) を参照してください。

## Exec approvals

Matrix は Matrix アカウント用のネイティブ approval client として動作できます。ネイティブの
DM/チャネルルーティング設定は、引き続き exec approval config 配下にあります:

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers`（任意。`channels.matrix.dm.allowFrom` にフォールバック）
- `channels.matrix.execApprovals.target`（`dm` | `channel` | `both`、デフォルト: `dm`）
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

approver は `@owner:example.org` のような Matrix user ID である必要があります。Matrix は `enabled` が未設定または `"auto"` で、かつ少なくとも 1 人の approver を解決できる場合にネイティブ approval を自動有効化します。Exec approval ではまず `execApprovals.approvers` を使い、`channels.matrix.dm.allowFrom` にフォールバックできます。plugin approval は `channels.matrix.dm.allowFrom` を通じて認可します。Matrix をネイティブ approval client として明示的に無効化するには `enabled: false` を設定してください。それ以外の場合、approval request は他の設定済み approval ルートまたは approval fallback policy にフォールバックします。

Matrix のネイティブルーティングは現在、両方の approval 種別をサポートしています:

- `channels.matrix.execApprovals.*` は Matrix approval prompt のネイティブ DM/チャネル配信モードを制御します。
- Exec approval は `execApprovals.approvers` または `channels.matrix.dm.allowFrom` から exec approver 集合を使用します。
- plugin approval は Matrix DM allowlist の `channels.matrix.dm.allowFrom` を使用します。
- Matrix のリアクションショートカットとメッセージ更新は、exec approval と plugin approval の両方に適用されます。

配信ルール:

- `target: "dm"` は approval prompt を approver の DM に送信します
- `target: "channel"` は prompt を元の Matrix ルームまたは DM に送り返します
- `target: "both"` は approver の DM と元の Matrix ルームまたは DM の両方に送信します

Matrix approval prompt は、主要な approval メッセージ上にリアクションショートカットを設定します:

- `✅` = 一度だけ許可
- `❌` = 拒否
- `♾️` = 有効な exec policy でその判断が許可されている場合は常に許可

approver はそのメッセージにリアクションするか、フォールバックの slash command `/approve <id> allow-once`、`/approve <id> allow-always`、または `/approve <id> deny` を使用できます。

承認または拒否できるのは解決済み approver のみです。exec approval では、チャネル配信にはコマンドテキストが含まれるため、`channel` または `both` は信頼されたルームでのみ有効にしてください。

Matrix approval prompt は共有 core approval planner を再利用します。Matrix 固有のネイティブ surface は、exec approval と plugin approval の両方について、ルーム/DM ルーティング、リアクション、メッセージの送信/更新/削除動作を処理します。

アカウントごとの override:

- `channels.matrix.accounts.<account>.execApprovals`

関連ドキュメント: [Exec approvals](/ja-JP/tools/exec-approvals)

## マルチアカウントの例

```json5
{
  channels: {
    matrix: {
      enabled: true,
      defaultAccount: "assistant",
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_xxx",
          encryption: true,
        },
        alerts: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_xxx",
          dm: {
            policy: "allowlist",
            allowFrom: ["@ops:example.org"],
            threadReplies: "off",
          },
        },
      },
    },
  },
}
```

トップレベルの `channels.matrix` 値は、アカウント側で override されない限り、名前付きアカウントのデフォルトとして機能します。
継承されたルームエントリを 1 つの Matrix アカウントにスコープするには `groups.<room>.account`（またはレガシーの `rooms.<room>.account`）を使用できます。
`account` のないエントリはすべての Matrix アカウントで共有され、`account: "default"` のエントリは、デフォルトアカウントがトップレベルの `channels.matrix.*` に直接設定されている場合でも引き続き機能します。
共有認証デフォルトが部分的にあるだけでは、それ自体で別個の暗黙的デフォルトアカウントは作成されません。OpenClaw は、そのデフォルトに新しい認証（`homeserver` + `accessToken`、または `homeserver` + `userId` と `password`）がある場合にのみ、トップレベルの `default` アカウントを合成します。名前付きアカウントは、後からキャッシュ済み認証情報が認証を満たす場合、`homeserver` + `userId` だけでも引き続き発見可能です。
Matrix にすでにちょうど 1 つの名前付きアカウントがある場合、または `defaultAccount` が既存の名前付きアカウントキーを指している場合、単一アカウントからマルチアカウントへの修復/セットアップ昇格では、新しい `accounts.default` エントリを作成せず、そのアカウントが保持されます。昇格されたアカウントに移るのは Matrix 認証/bootstrap キーだけで、共有配信 policy キーはトップレベルに残ります。
暗黙的ルーティング、プローブ、CLI 操作で 1 つの名前付き Matrix アカウントを優先したい場合は、`defaultAccount` を設定してください。
複数の名前付きアカウントを設定する場合は、暗黙的なアカウント選択に依存する CLI コマンドのために `defaultAccount` を設定するか、`--account <id>` を渡してください。
1 つのコマンドだけでその暗黙的選択を上書きしたい場合は、`openclaw matrix verify ...` と `openclaw matrix devices ...` に `--account <id>` を渡してください。

## プライベート/LAN homeserver

デフォルトでは、OpenClaw は SSRF 保護のため、プライベート/内部 Matrix homeserver をブロックします。
アカウントごとに明示的にオプトインしない限り接続できません。

homeserver が localhost、LAN/Tailscale IP、または内部ホスト名で動作している場合は、
その Matrix アカウントで `network.dangerouslyAllowPrivateNetwork` を有効にしてください:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      network: {
        dangerouslyAllowPrivateNetwork: true,
      },
      accessToken: "syt_internal_xxx",
    },
  },
}
```

CLI セットアップ例:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

このオプトインは、信頼されたプライベート/内部ターゲットのみを許可します。たとえば
`http://matrix.example.org:8008` のような公開クリアテキスト homeserver は引き続きブロックされます。可能な限り `https://` を推奨します。

## Matrix トラフィックのプロキシ

Matrix デプロイメントで明示的な送信 HTTP(S) プロキシが必要な場合は、`channels.matrix.proxy` を設定してください:

```json5
{
  channels: {
    matrix: {
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
    },
  },
}
```

名前付きアカウントは `channels.matrix.accounts.<id>.proxy` でトップレベルのデフォルトを override できます。
OpenClaw はランタイム Matrix トラフィックとアカウントステータスプローブの両方で同じプロキシ設定を使用します。

## ターゲット解決

Matrix は、OpenClaw がルームまたはユーザーのターゲットを要求する場所ならどこでも、次のターゲット形式を受け付けます:

- ユーザー: `@user:server`、`user:@user:server`、または `matrix:user:@user:server`
- ルーム: `!room:server`、`room:!room:server`、または `matrix:room:!room:server`
- エイリアス: `#alias:server`、`channel:#alias:server`、または `matrix:channel:#alias:server`

ライブディレクトリ検索は、ログイン中の Matrix アカウントを使います:

- ユーザー検索は、その homeserver 上の Matrix ユーザーディレクトリに問い合わせます。
- ルーム検索は明示的なルーム ID とエイリアスを直接受け付け、その後、そのアカウントで参加済みのルーム名検索にフォールバックします。
- 参加済みルーム名検索はベストエフォートです。ルーム名を ID またはエイリアスに解決できない場合、ランタイム allowlist 解決では無視されます。

## 設定リファレンス

- `enabled`: チャネルを有効または無効にします。
- `name`: アカウントの任意ラベル。
- `defaultAccount`: 複数の Matrix アカウントが設定されている場合に優先されるアカウント ID。
- `homeserver`: homeserver URL。例: `https://matrix.example.org`。
- `network.dangerouslyAllowPrivateNetwork`: この Matrix アカウントがプライベート/内部 homeserver に接続できるようにします。homeserver が `localhost`、LAN/Tailscale IP、または `matrix-synapse` のような内部ホストに解決される場合に有効にしてください。
- `proxy`: Matrix トラフィック用の任意の HTTP(S) プロキシ URL。名前付きアカウントは独自の `proxy` でトップレベルのデフォルトを override できます。
- `userId`: 完全な Matrix user ID。例: `@bot:example.org`。
- `accessToken`: トークンベース認証用のアクセストークン。平文値と SecretRef 値の両方が、env/file/exec provider 全体で `channels.matrix.accessToken` および `channels.matrix.accounts.<id>.accessToken` に対応しています。詳しくは [Secrets Management](/ja-JP/gateway/secrets) を参照してください。
- `password`: パスワードベースログイン用のパスワード。平文値と SecretRef 値の両方に対応しています。
- `deviceId`: 明示的な Matrix device ID。
- `deviceName`: パスワードログイン用の device 表示名。
- `avatarUrl`: プロファイル同期および `set-profile` 更新用に保存される self-avatar URL。
- `initialSyncLimit`: 起動時 sync イベント上限。
- `encryption`: E2EE を有効にします。
- `allowlistOnly`: DM とルームに対して allowlist 専用動作を強制します。
- `allowBots`: 他の設定済み OpenClaw Matrix アカウントからのメッセージを許可します（`true` または `"mentions"`）。
- `groupPolicy`: `open`、`allowlist`、または `disabled`。
- `contextVisibility`: 補足ルームコンテキストの可視性モード（`all`、`allowlist`、`allowlist_quote`）。
- `groupAllowFrom`: ルームトラフィック用の user ID allowlist。
- `groupAllowFrom` エントリは完全な Matrix user ID にしてください。解決できない名前はランタイムで無視されます。
- `historyLimit`: グループ履歴コンテキストとして含めるルームメッセージの最大数。`messages.groupChat.historyLimit` にフォールバックします。両方が未設定の場合、有効なデフォルトは `0` です。無効にするには `0` を設定してください。
- `replyToMode`: `off`、`first`、`all`、または `batched`。
- `markdown`: 送信 Matrix テキスト用の任意の Markdown レンダリング設定。
- `streaming`: `off`（デフォルト）、`partial`、`quiet`、`true`、または `false`。`partial` と `true` は通常の Matrix テキストメッセージによるプレビュー先行の下書き更新を有効にします。`quiet` はセルフホスト push-rule 構成向けに通知しないプレビュー notice を使用します。
- `blockStreaming`: `true` は、下書きプレビューストリーミングが有効なとき、完了した assistant ブロック用の別個の進捗メッセージを有効にします。
- `threadReplies`: `off`、`inbound`、または `always`。
- `threadBindings`: thread-bound セッションルーティングとライフサイクルのチャネルごとの override。
- `startupVerification`: 起動時の自動自己検証要求モード（`if-unverified`、`off`）。
- `startupVerificationCooldownHours`: 自動起動時検証要求を再試行するまでのクールダウン。
- `textChunkLimit`: 送信メッセージのチャンクサイズ。
- `chunkMode`: `length` または `newline`。
- `responsePrefix`: 送信返信用の任意のメッセージ接頭辞。
- `ackReaction`: このチャネル/アカウント用の任意の ack リアクション override。
- `ackReactionScope`: 任意の ack リアクションスコープ override（`group-mentions`、`group-all`、`direct`、`all`、`none`、`off`）。
- `reactionNotifications`: 受信リアクション通知モード（`own`、`off`）。
- `mediaMaxMb`: Matrix メディア処理用のメディアサイズ上限（MB）。送信と受信メディア処理の両方に適用されます。
- `autoJoin`: 招待自動参加 policy（`always`、`allowlist`、`off`）。デフォルト: `off`。これは Matrix 招待全般に適用され、DM 形式の招待も含まれます。OpenClaw は、参加ルームを DM かグループか確実に分類できる前の招待時点でこの判定を行います。
- `autoJoinAllowlist`: `autoJoin` が `allowlist` のときに許可されるルーム/エイリアス。エイリアスエントリは招待処理中にルーム ID に解決されます。OpenClaw は招待されたルームが主張するエイリアス状態を信頼しません。
- `dm`: DM policy ブロック（`enabled`、`policy`、`allowFrom`、`sessionScope`、`threadReplies`）。
- `dm.policy`: OpenClaw がルームに参加し、それを DM と分類した後の DM アクセスを制御します。招待が自動参加されるかどうかは変えません。
- `dm.allowFrom` エントリは、ライブディレクトリ検索ですでに解決済みでない限り、完全な Matrix user ID にしてください。
- `dm.sessionScope`: `per-user`（デフォルト）または `per-room`。相手が同じでも各 Matrix DM ルームを別コンテキストに保ちたい場合は `per-room` を使用します。
- `dm.threadReplies`: DM 専用のスレッド policy override（`off`、`inbound`、`always`）。DM での返信配置とセッション分離の両方に対して、トップレベルの `threadReplies` 設定を上書きします。
- `execApprovals`: Matrix ネイティブの exec approval 配信（`enabled`、`approvers`、`target`、`agentFilter`、`sessionFilter`）。
- `execApprovals.approvers`: exec request を承認できる Matrix user ID。`dm.allowFrom` がすでに approver を識別している場合は任意です。
- `execApprovals.target`: `dm | channel | both`（デフォルト: `dm`）。
- `accounts`: 名前付きアカウントごとの override。トップレベルの `channels.matrix` 値はこれらのエントリのデフォルトとして機能します。
- `groups`: ルームごとの policy マップ。ルーム ID またはエイリアスを推奨します。解決できないルーム名はランタイムで無視されます。セッション/グループ ID は解決後に安定したルーム ID を使い、人が読めるラベルは引き続きルーム名から取得されます。
- `groups.<room>.account`: マルチアカウント構成で 1 つの継承ルームエントリを特定の Matrix アカウントに制限します。
- `groups.<room>.allowBots`: 設定済み bot sender に対するルームレベル override（`true` または `"mentions"`）。
- `groups.<room>.users`: ルームごとの sender allowlist。
- `groups.<room>.tools`: ルームごとの tool allow/deny override。
- `groups.<room>.autoReply`: ルームレベルの mention 制御 override。`true` はそのルームの mention 要件を無効にし、`false` はそれらを再度強制します。
- `groups.<room>.skills`: 任意のルームレベル skill フィルター。
- `groups.<room>.systemPrompt`: 任意のルームレベル system prompt スニペット。
- `rooms`: `groups` のレガシー alias。
- `actions`: アクションごとの tool 制御（`messages`、`reactions`、`pins`、`profile`、`memberInfo`、`channelInfo`、`verification`）。

## 関連

- [Channels Overview](/ja-JP/channels) — サポートされているすべてのチャネル
- [Pairing](/ja-JP/channels/pairing) — DM 認証と pairing フロー
- [Groups](/ja-JP/channels/groups) — グループチャットの動作と mention 制御
- [Channel Routing](/ja-JP/channels/channel-routing) — メッセージのセッションルーティング
- [Security](/ja-JP/gateway/security) — アクセスモデルとハードニング
