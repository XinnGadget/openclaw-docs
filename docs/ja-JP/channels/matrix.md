---
read_when:
    - OpenClawでMatrixをセットアップする場合
    - MatrixのE2EEと検証を設定する場合
summary: Matrixのサポート状況、セットアップ、および設定例
title: Matrix
x-i18n:
    generated_at: "2026-04-07T04:43:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: d53baa2ea5916cd00a99cae0ded3be41ffa13c9a69e8ea8461eb7baa6a99e13c
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrixは、OpenClaw向けのMatrixバンドル済みチャネルプラグインです。
公式の`matrix-js-sdk`を使用し、DM、ルーム、スレッド、メディア、リアクション、投票、位置情報、E2EEをサポートします。

## バンドル済みプラグイン

Matrixは現在のOpenClawリリースではバンドル済みプラグインとして同梱されているため、通常の
パッケージ版ビルドでは別途インストールは不要です。

古いビルドまたはMatrixが除外されたカスタムインストールを使用している場合は、
手動でインストールしてください。

npmからインストールする場合:

```bash
openclaw plugins install @openclaw/matrix
```

ローカルのチェックアウトからインストールする場合:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

プラグインの動作とインストールルールについては、[Plugins](/ja-JP/tools/plugin)を参照してください。

## セットアップ

1. Matrixプラグインが利用可能であることを確認します。
   - 現在のパッケージ版OpenClawリリースには、すでに同梱されています。
   - 古い/カスタムインストールでは、上記のコマンドで手動追加できます。
2. お使いのhomeserverでMatrixアカウントを作成します。
3. `channels.matrix`を次のいずれかで設定します。
   - `homeserver` + `accessToken`、または
   - `homeserver` + `userId` + `password`。
4. Gatewayを再起動します。
5. ボットとのDMを開始するか、ルームに招待します。
   - 新しいMatrix招待は、`channels.matrix.autoJoin`で許可されている場合にのみ機能します。

対話型セットアップのパス:

```bash
openclaw channels add
openclaw configure --section channels
```

Matrixウィザードが実際に尋ねる内容:

- homeserver URL
- 認証方法: アクセストークンまたはパスワード
- パスワード認証を選択した場合のみユーザーID
- 任意のデバイス名
- E2EEを有効にするかどうか
- Matrixルームアクセスを今すぐ設定するかどうか
- Matrix招待の自動参加を今すぐ設定するかどうか
- 招待の自動参加を有効にする場合、それを`allowlist`、`always`、`off`のどれにするか

重要なウィザードの動作:

- 選択したアカウントに対してMatrix認証の環境変数がすでに存在し、そのアカウントにまだconfig内の認証が保存されていない場合、ウィザードはenvショートカットを提示します。これにより、認証情報をconfigにコピーせず、env varsに保持したままセットアップできます。
- 対話的に別のMatrixアカウントを追加すると、入力したアカウント名はconfigとenv varsで使われるアカウントIDに正規化されます。たとえば、`Ops Bot`は`ops-bot`になります。
- DM allowlistのプロンプトは、完全な`@user:server`値をすぐに受け付けます。表示名は、ライブディレクトリ検索で完全一致が1件見つかった場合にのみ機能します。それ以外の場合、ウィザードは完全なMatrix IDで再試行するよう求めます。
- ルーム allowlist のプロンプトは、ルームIDとエイリアスを直接受け付けます。また、参加済みルーム名をライブ解決することもできますが、解決できなかった名前はセットアップ中に入力されたまま保持されるだけで、実行時のallowlist解決では無視されます。`!room:server`または`#alias:server`を推奨します。
- `channels.matrix.autoJoin`のデフォルトが`off`であるため、ウィザードは招待の自動参加ステップの前に明示的な警告を表示するようになりました。これを設定しない限り、エージェントは招待されたルームや新しいDM形式の招待には参加しません。
- 招待の自動参加がallowlistモードの場合は、安定した招待ターゲットのみを使用してください: `!roomId:server`、`#alias:server`、または`*`。単純なルーム名は拒否されます。
- 実行時のルーム/セッション識別には、安定したMatrix room IDが使用されます。ルームで宣言されたエイリアスは、長期的なセッションキーや安定したグループ識別子ではなく、検索入力としてのみ使用されます。
- 保存前にルーム名を解決するには、`openclaw channels resolve --channel matrix "Project Room"`を使用してください。

<Warning>
`channels.matrix.autoJoin`のデフォルトは`off`です。

未設定のままにすると、ボットは招待されたルームや新しいDM形式の招待に参加しないため、手動で先に参加しない限り、新しいグループや招待されたDMには表示されません。

受け入れる招待を制限したい場合は、`autoJoin: "allowlist"`を`autoJoinAllowlist`と一緒に設定するか、すべての招待に参加させたい場合は`autoJoin: "always"`を設定してください。

`allowlist`モードでは、`autoJoinAllowlist`は`!roomId:server`、`#alias:server`、または`*`のみ受け付けます。
</Warning>

Allowlistの例:

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

すべての招待に参加する場合:

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

パスワードベースの設定（ログイン後にトークンがキャッシュされます）:

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

Matrixはキャッシュされた認証情報を`~/.openclaw/credentials/matrix/`に保存します。
デフォルトアカウントでは`credentials.json`、名前付きアカウントでは`credentials-<account>.json`を使用します。
そこにキャッシュ済み認証情報が存在する場合、現在の認証がconfigに直接設定されていなくても、OpenClawはセットアップ、doctor、チャネル状態の検出においてMatrixを設定済みとして扱います。

環境変数の同等項目（config keyが設定されていない場合に使用されます）:

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

デフォルト以外のアカウントでは、アカウントスコープ付きの環境変数を使用します:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

アカウント`ops`の例:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

正規化されたアカウントID `ops-bot` では、次を使用します:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrixは、アカウントID内の句読点をエスケープして、スコープ付き環境変数が衝突しないようにします。
たとえば、`-`は`_X2D_`になるため、`ops-prod`は`MATRIX_OPS_X2D_PROD_*`に対応します。

対話型ウィザードがenv-varショートカットを提示するのは、それらの認証環境変数がすでに存在し、かつ選択したアカウントにMatrix認証がまだconfigへ保存されていない場合のみです。

## 設定例

これは、DMペアリング、ルーム allowlist、E2EE有効化を含む実用的なベースライン設定です:

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

`autoJoin`は、ルーム/グループ招待だけでなく、一般的なMatrix招待に適用されます。
これには新しいDM形式の招待も含まれます。招待時点では、OpenClawはその招待された
ルームが最終的にDMとして扱われるかグループとして扱われるかを確実には判断できないため、
すべての招待は最初に同じ`autoJoin`判定を通ります。ボットが参加し、ルームが
DMとして分類された後は引き続き`dm.policy`が適用されるため、`autoJoin`は参加動作を制御し、
`dm.policy`は返信/アクセス動作を制御します。

## ストリーミングプレビュー

Matrixの返信ストリーミングはオプトインです。

OpenClawに単一のライブプレビュー返信を送信させ、
モデルがテキストを生成している間そのプレビューをその場で編集し、
返信完了時にそれを確定したい場合は、`channels.matrix.streaming`を`"partial"`に設定します:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"`がデフォルトです。OpenClawは最終返信を待って1回だけ送信します。
- `streaming: "partial"`は、通常のMatrixテキストメッセージを使用して、現在のアシスタントブロック用に編集可能なプレビューメッセージを1つ作成します。これにより、Matrixの従来の「プレビュー優先」通知動作が維持されるため、標準クライアントでは完成したブロックではなく最初のストリーミングプレビューテキストで通知されることがあります。
- `streaming: "quiet"`は、現在のアシスタントブロック用に編集可能な静かなプレビュー通知を1つ作成します。これは、確定済みプレビュー編集用の受信者プッシュルールも設定する場合にのみ使用してください。
- `blockStreaming: true`は、個別のMatrix進行状況メッセージを有効にします。プレビューのストリーミングが有効な場合、Matrixは現在のブロックのライブドラフトを保持し、完了済みブロックを別メッセージとして保持します。
- プレビューのストリーミングが有効で`blockStreaming`が無効な場合、Matrixはライブドラフトをその場で編集し、ブロックまたはターンが終了した時点で同じイベントを確定します。
- プレビューが1つのMatrixイベントに収まらなくなった場合、OpenClawはプレビューのストリーミングを停止し、通常の最終配信にフォールバックします。
- メディア返信は引き続き通常どおり添付ファイルを送信します。古いプレビューを安全に再利用できなくなった場合、OpenClawは最終メディア返信を送る前にそのプレビューをredactします。
- プレビュー編集には追加のMatrix API呼び出しコストがかかります。最も保守的なレート制限動作を望む場合は、ストリーミングをオフのままにしてください。

`blockStreaming`自体ではドラフトプレビューは有効になりません。
プレビュー編集には`streaming: "partial"`または`streaming: "quiet"`を使用し、そのうえで完了したアシスタントブロックも個別の進行状況メッセージとして表示したい場合にのみ`blockStreaming: true`を追加してください。

カスタムプッシュルールなしで標準のMatrix通知が必要な場合は、プレビュー優先動作のために`streaming: "partial"`を使うか、最終結果のみを配信するために`streaming`をオフのままにしてください。`streaming: "off"`の場合:

- `blockStreaming: true`は、完了した各ブロックを通常の通知付きMatrixメッセージとして送信します。
- `blockStreaming: false`は、最終的に完了した返信のみを通常の通知付きMatrixメッセージとして送信します。

### quietな確定済みプレビュー用のセルフホスト型プッシュルール

独自のMatrixインフラを運用していて、quietプレビューがブロックまたは
最終返信の完了時にのみ通知するようにしたい場合は、`streaming: "quiet"`を設定し、
確定済みプレビュー編集用のユーザー単位プッシュルールを追加してください。

これは通常、homeserver全体の設定変更ではなく、受信側ユーザーの設定です:

始める前の簡単な対応表:

- recipient user = 通知を受け取る人
- bot user = 返信を送信するOpenClaw Matrixアカウント
- 以下のAPI呼び出しには受信側ユーザーのアクセストークンを使用する
- プッシュルール内の`sender`はbot userの完全なMXIDに一致させる

1. quietプレビューを使うようOpenClawを設定します:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. 受信側アカウントがすでに通常のMatrixプッシュ通知を受け取れていることを確認します。quietプレビュー
   ルールは、そのユーザーにすでに動作するpusher/デバイスがある場合にのみ機能します。

3. 受信側ユーザーのアクセストークンを取得します。
   - ボットのトークンではなく、受信側ユーザーのトークンを使用してください。
   - 通常は、既存のクライアントセッショントークンを再利用するのが最も簡単です。
   - 新しいトークンを発行する必要がある場合は、標準のMatrix Client-Server API経由でログインできます:

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

4. 受信側アカウントにすでにpusherが存在することを確認します:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

これでアクティブなpusher/デバイスが返ってこない場合は、以下の
OpenClawルールを追加する前に、まず通常のMatrix通知を修正してください。

OpenClawは、確定済みのテキストのみプレビュー編集に次のマークを付けます:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. これらの通知を受け取りたい各受信側アカウントに対して、overrideプッシュルールを作成します:

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

- `https://matrix.example.org`: あなたのhomeserverのベースURL
- `$USER_ACCESS_TOKEN`: 受信側ユーザーのアクセストークン
- `openclaw-finalized-preview-botname`: この受信側ユーザーに対してこのボット固有となるrule ID
- `@bot:example.org`: 受信側ユーザーのMXIDではなく、あなたのOpenClaw Matrix bot MXID

複数ボット構成で重要な点:

- プッシュルールは`ruleId`で識別されます。同じrule IDに対して`PUT`を再実行すると、その1つのルールが更新されます。
- 1人の受信側ユーザーが複数のOpenClaw Matrix botアカウントから通知を受ける必要がある場合は、各sender一致ごとに一意なrule IDで、ボットごとに1ルール作成してください。
- 単純なパターンとしては`openclaw-finalized-preview-<botname>`が使えます。たとえば`openclaw-finalized-preview-ops`や`openclaw-finalized-preview-support`です。

このルールはイベント送信者に対して評価されます:

- 受信側ユーザーのトークンで認証する
- `sender`をOpenClaw botのMXIDに一致させる

6. ルールが存在することを確認します:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. ストリーミング返信をテストします。quietモードでは、ルームにquietなドラフトプレビューが表示され、
   最終的なその場編集によって、ブロックまたはターン完了時に1回通知されるはずです。

後でこのルールを削除する必要がある場合は、受信側ユーザーのトークンで同じrule IDを削除します:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

注意:

- ルールの作成には、ボットのアクセストークンではなく受信側ユーザーのアクセストークンを使用してください。
- 新しいユーザー定義`override`ルールは、デフォルトの抑制ルールより前に挿入されるため、追加の順序パラメータは不要です。
- これは、OpenClawが安全にその場で確定できるテキストのみのプレビュー編集にのみ影響します。メディアへのフォールバックや古いプレビューへのフォールバックでは、引き続き通常のMatrix配信を使います。
- `GET /_matrix/client/v3/pushers`でpusherが表示されない場合、そのユーザーはまだこのアカウント/デバイスで動作するMatrixプッシュ配信を持っていません。

#### Synapse

Synapseでは、通常、上記のセットアップだけで十分です:

- 確定済みOpenClawプレビュー通知のために特別な`homeserver.yaml`変更は不要です。
- Synapseデプロイがすでに通常のMatrixプッシュ通知を送信している場合、主なセットアップ手順は上記のユーザートークン + `pushrules`呼び出しです。
- リバースプロキシまたはworkersの背後でSynapseを動かしている場合は、`/_matrix/client/.../pushrules/`が正しくSynapseに到達することを確認してください。
- Synapse workersを使用している場合は、pusherが正常であることを確認してください。プッシュ配信はメインプロセスまたは`synapse.app.pusher` / 設定済みpusher workersで処理されます。

#### Tuwunel

Tuwunelでは、上記と同じセットアップフローおよびpush-rule API呼び出しを使用してください:

- 確定済みプレビューマーカー自体に対して、Tuwunel固有の設定は不要です。
- そのユーザーに対して通常のMatrix通知がすでに機能している場合、主なセットアップ手順は上記のユーザートークン + `pushrules`呼び出しです。
- ユーザーが別デバイスでアクティブな間に通知が消えるように見える場合は、`suppress_push_when_active`が有効か確認してください。Tuwunelは2025年9月12日のTuwunel 1.4.2でこのオプションを追加しており、1つのデバイスがアクティブな間は他デバイスへのプッシュを意図的に抑制することがあります。

## 暗号化と検証

暗号化された（E2EE）ルームでは、送信画像イベントは`thumbnail_file`を使用するため、画像プレビューもフル添付ファイルと一緒に暗号化されます。暗号化されていないルームでは引き続き通常の`thumbnail_url`を使用します。設定は不要で、プラグインがE2EE状態を自動検出します。

### ボット間ルーム

デフォルトでは、他の設定済みOpenClaw MatrixアカウントからのMatrixメッセージは無視されます。

エージェント間のMatrixトラフィックを意図的に許可したい場合は、`allowBots`を使用します:

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

- `allowBots: true`は、許可されたルームおよびDMで、他の設定済みMatrix botアカウントからのメッセージを受け付けます。
- `allowBots: "mentions"`は、ルーム内でそれらのメッセージがこのボットに明示的にメンションしている場合にのみ受け付けます。DMは引き続き許可されます。
- `groups.<room>.allowBots`は、1つのルームに対してアカウントレベル設定を上書きします。
- OpenClawは、自己返信ループを避けるため、同じMatrix user IDからのメッセージは引き続き無視します。
- Matrixはここでネイティブなbotフラグを公開していません。OpenClawは「botが作成した」を「このOpenClaw Gateway上の別の設定済みMatrixアカウントによって送信された」として扱います。

共有ルームでボット間トラフィックを有効にする場合は、厳格なルーム allowlist とメンション要件を使用してください。

暗号化を有効にする場合:

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

検証状態を確認する場合:

```bash
openclaw matrix verify status
```

詳細な状態（完全な診断）:

```bash
openclaw matrix verify status --verbose
```

保存されたrecovery keyを機械可読出力に含める場合:

```bash
openclaw matrix verify status --include-recovery-key --json
```

cross-signingと検証状態をbootstrapする場合:

```bash
openclaw matrix verify bootstrap
```

マルチアカウント対応: アカウントごとの認証情報と任意の`name`には`channels.matrix.accounts`を使用します。共有パターンについては、[Configuration reference](/ja-JP/gateway/configuration-reference#multi-account-all-channels)を参照してください。

詳細なbootstrap診断:

```bash
openclaw matrix verify bootstrap --verbose
```

bootstrapの前に新しいcross-signing identityのリセットを強制する場合:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

recovery keyでこのデバイスを検証する場合:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

詳細なデバイス検証情報:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

room-key backupの健全性を確認する場合:

```bash
openclaw matrix verify backup status
```

詳細なbackup健全性診断:

```bash
openclaw matrix verify backup status --verbose
```

サーバーバックアップからroom keysを復元する場合:

```bash
openclaw matrix verify backup restore
```

詳細な復元診断:

```bash
openclaw matrix verify backup restore --verbose
```

現在のサーバーバックアップを削除し、新しいbackup baselineを作成します。保存済み
backup keyを正常に読み込めない場合、このリセットによってsecret storageも再作成されるため、
今後のcold startで新しいbackup keyを読み込めるようになります:

```bash
openclaw matrix verify backup reset --yes
```

すべての`verify`コマンドはデフォルトで簡潔です（内部SDKログもquietを含む）で、詳細な診断を表示するのは`--verbose`を付けた場合のみです。
スクリプトで使用する場合は、完全な機械可読出力に`--json`を使用してください。

マルチアカウント構成では、`--account <id>`を渡さない限り、Matrix CLIコマンドは暗黙のMatrixデフォルトアカウントを使用します。
複数の名前付きアカウントを設定している場合は、最初に`channels.matrix.defaultAccount`を設定してください。そうしないと、それらの暗黙的なCLI操作は停止してアカウントを明示的に選ぶよう求めます。
検証またはデバイス操作を明示的に名前付きアカウントに向けたい場合は、`--account`を使用してください:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

名前付きアカウントで暗号化が無効または利用できない場合、Matrixの警告と検証エラーは、そのアカウントのconfig keyを指します。たとえば`channels.matrix.accounts.assistant.encryption`です。

### 「verified」の意味

OpenClawは、このMatrixデバイスが自分自身のcross-signing identityによって検証された場合にのみ、verifiedとして扱います。
実際には、`openclaw matrix verify status --verbose`は次の3つの信頼シグナルを公開します:

- `Locally trusted`: このデバイスは現在のクライアントでのみ信頼されている
- `Cross-signing verified`: SDKが、このデバイスをcross-signing経由で検証済みとして報告している
- `Signed by owner`: このデバイスが自分自身のself-signing keyによって署名されている

`Verified by owner`が`yes`になるのは、cross-signing verificationまたはowner-signingが存在する場合のみです。
ローカルの信頼だけでは、OpenClawはこのデバイスを完全に検証済みとは扱いません。

### bootstrapの動作

`openclaw matrix verify bootstrap`は、暗号化されたMatrixアカウント向けの修復およびセットアップコマンドです。
これは次のすべてを順に行います:

- secret storageをbootstrapし、可能であれば既存のrecovery keyを再利用する
- cross-signingをbootstrapし、不足している公開cross-signing keysをアップロードする
- 現在のデバイスをマークしてcross-signすることを試みる
- まだ存在しない場合は、新しいサーバー側room-key backupを作成する

homeserverがcross-signing keysのアップロードに対して対話型認証を要求する場合、OpenClawは最初に認証なしでアップロードを試み、その後`m.login.dummy`、さらに`channels.matrix.password`が設定されていれば`m.login.password`を試みます。

現在のcross-signing identityを破棄して新しいものを作成したい場合にのみ、`--force-reset-cross-signing`を使用してください。

現在のroom-key backupを意図的に破棄し、
将来のメッセージ向けに新しいbackup baselineを開始したい場合は、`openclaw matrix verify backup reset --yes`を使用してください。
これは、回復不能な古い暗号化履歴が引き続き利用できないままになること、
および現在のbackup secretを安全に読み込めない場合にOpenClawがsecret storageを再作成する可能性を受け入れる場合にのみ実行してください。

### 新しいbackup baseline

将来の暗号化メッセージを引き続き利用可能にしつつ、回復不能な古い履歴を失っても構わない場合は、次のコマンドを順に実行します:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

名前付きMatrixアカウントを明示的に対象にしたい場合は、各コマンドに`--account <id>`を追加してください。

### 起動時の動作

`encryption: true`の場合、Matrixは`startupVerification`のデフォルトを`"if-unverified"`にします。
起動時にこのデバイスがまだ未検証であれば、Matrixは別のMatrixクライアントでの自己検証を要求し、
すでに1つ保留中である間は重複リクエストをスキップし、再起動後に再試行する前にローカルのクールダウンを適用します。
デフォルトでは、失敗したリクエスト試行は、成功したリクエスト作成よりも早く再試行されます。
自動起動リクエストを無効にするには`startupVerification: "off"`を設定するか、再試行ウィンドウを短くまたは長くしたい場合は`startupVerificationCooldownHours`
を調整してください。

起動時には、自動で保守的なcrypto bootstrapパスも実行されます。
このパスはまず現在のsecret storageとcross-signing identityの再利用を試み、明示的なbootstrap修復フローを実行しない限りcross-signingのリセットを避けます。

起動時に破損したbootstrap状態が見つかり、`channels.matrix.password`が設定されている場合、OpenClawはより厳格な修復パスを試行できます。
現在のデバイスがすでにowner-signedである場合、OpenClawはそれを自動リセットせず、そのidentityを保持します。

以前の公開Matrixプラグインからアップグレードする場合:

- OpenClawは可能であれば同じMatrixアカウント、アクセストークン、デバイスidentityを自動再利用します。
- 実行可能なMatrix移行変更を行う前に、OpenClawは`~/Backups/openclaw-migrations/`配下にrecovery snapshotを作成または再利用します。
- 複数のMatrixアカウントを使用している場合、古いflat-storeレイアウトからアップグレードする前に`channels.matrix.defaultAccount`を設定してください。そうすることで、その共有レガシー状態をどのアカウントが受け取るべきかOpenClawが判断できます。
- 以前のプラグインがMatrix room-key backup復号キーをローカルに保存していた場合、起動時または`openclaw doctor --fix`がそれを新しいrecovery-keyフローに自動インポートします。
- 移行の準備後にMatrixアクセストークンが変更された場合、起動時は自動backup復元を諦める前に、保留中のレガシー復元状態を持つ兄弟token-hashストレージrootをスキャンするようになりました。
- 同じアカウント、homeserver、ユーザーに対して後でMatrixアクセストークンが変更された場合、OpenClawは空のMatrix stateディレクトリから開始するのではなく、最も完全な既存のtoken-hashストレージrootを再利用することを優先するようになりました。
- 次回のGateway起動時に、バックアップ済みroom keysは新しいcrypto storeへ自動復元されます。
- 古いプラグインにローカルのみに存在するroom keysがあり、それらが一度もバックアップされていなかった場合、OpenClawは明確に警告します。それらのキーは以前のrust crypto storeから自動エクスポートできないため、手動で回復するまで一部の古い暗号化履歴は利用できない可能性があります。
- 完全なアップグレードフロー、制限、回復コマンド、一般的な移行メッセージについては、[Matrix migration](/ja-JP/install/migrating-matrix)を参照してください。

暗号化された実行時状態は、アカウントごと、ユーザーごとのtoken-hash rootの下で
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`に整理されます。
そのディレクトリには、sync store（`bot-storage.json`）、crypto store（`crypto/`）、
recovery keyファイル（`recovery-key.json`）、IndexedDB snapshot（`crypto-idb-snapshot.json`）、
thread bindings（`thread-bindings.json`）、およびstartup verification state（`startup-verification.json`）
が、それらの機能が使用されている場合に含まれます。
トークンが変わってもアカウントidentityが同じであれば、OpenClawはそのアカウント/homeserver/user組に対して最適な既存
rootを再利用するため、以前のsync state、crypto state、thread bindings、
startup verification stateが引き続き見える状態で維持されます。

### Node crypto storeモデル

このプラグインのMatrix E2EEは、Node内で公式の`matrix-js-sdk` Rust crypto pathを使用します。
このパスでは、crypto stateを再起動後も保持したい場合、IndexedDBベースの永続化が必要です。

OpenClawは現在、Nodeでこれを次の方法で提供しています:

- SDKが期待するIndexedDB API shimとして`fake-indexeddb`を使用する
- `initRustCrypto`の前に`crypto-idb-snapshot.json`からRust crypto IndexedDB内容を復元する
- init後および実行中に、更新されたIndexedDB内容を`crypto-idb-snapshot.json`へ永続化する
- advisory file lockを用いて、`crypto-idb-snapshot.json`に対するsnapshot復元と永続化を直列化し、Gateway実行時の永続化とCLIメンテナンスが同じsnapshotファイルで競合しないようにする

これは互換性/ストレージの配線であり、カスタムcrypto実装ではありません。
snapshotファイルは機密性の高い実行時状態であり、制限されたファイル権限で保存されます。
OpenClawのセキュリティモデルでは、GatewayホストとローカルのOpenClaw stateディレクトリはすでに信頼できるオペレーター境界内にあるため、これは主に、別個のリモート信頼境界というより運用上の耐久性の問題です。

計画中の改善:

- 永続的なMatrix key materialに対するSecretRefサポートを追加し、recovery keysや関連するstore-encryption secretsをローカルファイルだけでなくOpenClawのsecrets providersから取得できるようにする

## プロファイル管理

選択したアカウントのMatrix self-profileを更新するには、次を使用します:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

名前付きMatrixアカウントを明示的に対象にしたい場合は、`--account <id>`を追加してください。

Matrixは`mxc://` avatar URLを直接受け付けます。`http://`または`https://`のavatar URLを渡した場合、OpenClawはまずそれをMatrixにアップロードし、解決された`mxc://` URLを`channels.matrix.avatarUrl`（または選択したアカウントの上書き先）へ保存します。

## 自動検証通知

Matrixは、strict DM verification roomに直接`m.notice`メッセージとして検証ライフサイクル通知を投稿するようになりました。
これには以下が含まれます:

- 検証リクエスト通知
- 検証準備完了通知（明示的な「Verify by emoji」案内付き）
- 検証開始および完了通知
- 利用可能な場合のSAS詳細（絵文字および10進数）

別のMatrixクライアントからの受信検証リクエストは、OpenClawによって追跡され自動受諾されます。
自己検証フローでは、絵文字検証が利用可能になると、OpenClawは自動でSASフローも開始し、自分側を確認します。
別のMatrixユーザー/デバイスからの検証リクエストでは、OpenClawはリクエストを自動受諾した後、SASフローが通常どおり進むのを待ちます。
検証を完了するには、引き続きMatrixクライアントで絵文字または10進数のSASを比較し、そこで「一致する」を確認する必要があります。

OpenClawは、自分で開始した重複フローを無条件に自動受諾しません。自己検証リクエストがすでに保留中である場合、起動時は新しいリクエストを作成しません。

検証プロトコル/システム通知はエージェントのチャットパイプラインには転送されないため、`NO_REPLY`は生成されません。

### デバイス衛生

古いOpenClaw管理のMatrixデバイスがアカウント上に蓄積すると、暗号化ルームの信頼性が把握しにくくなることがあります。
一覧表示するには次を使用します:

```bash
openclaw matrix devices list
```

古いOpenClaw管理デバイスを削除するには次を使用します:

```bash
openclaw matrix devices prune-stale
```

### Direct Room Repair

ダイレクトメッセージの状態が同期ずれを起こすと、OpenClawは、現在使われているDMではなく古い単独ルームを指す古い`m.direct`マッピングを保持してしまうことがあります。相手ユーザーに対する現在のマッピングを調べるには次を使用します:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

修復するには次を使用します:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

修復処理では、Matrix固有のロジックはプラグイン内に維持されます:

- まず、`m.direct`にすでにマッピングされている厳密な1対1のDMを優先します
- それ以外の場合、そのユーザーとの現在参加中の厳密な1対1 DMにフォールバックします
- 正常なDMが存在しない場合は、新しいダイレクトルームを作成し、`m.direct`をそれに向けて書き換えます

この修復フローは古いルームを自動削除しません。正常なDMを選択してマッピングを更新するだけなので、新しいMatrix送信、検証通知、その他のダイレクトメッセージフローが再び正しいルームを対象にするようになります。

## スレッド

Matrixは、自動返信とmessage-tool送信の両方でネイティブなMatrixスレッドをサポートします。

- `dm.sessionScope: "per-user"`（デフォルト）は、Matrix DMルーティングを送信者スコープに保つため、同じ相手として解決される複数のDMルームで1つのセッションを共有できます。
- `dm.sessionScope: "per-room"`は、通常のDM認証とallowlistチェックを維持しつつ、各Matrix DMルームを独自のセッションキーへ分離します。
- 明示的なMatrix会話バインディングは、引き続き`dm.sessionScope`より優先されるため、バインド済みルームとスレッドは選択された対象セッションを維持します。
- `threadReplies: "off"`は、返信をトップレベルに保ち、受信したスレッド付きメッセージも親セッション上に維持します。
- `threadReplies: "inbound"`は、受信メッセージがすでにそのスレッド内にあった場合にのみスレッド内で返信します。
- `threadReplies: "always"`は、ルーム返信をトリガーとなったメッセージをルートとするスレッド内に保ち、その会話を最初のトリガーメッセージから対応するスレッドスコープのセッション経由でルーティングします。
- `dm.threadReplies`は、DMに対してのみトップレベル設定を上書きします。たとえば、DMをフラットに保ったままルームスレッドだけを分離できます。
- 受信したスレッド付きメッセージには、追加のエージェントコンテキストとしてスレッドルートメッセージが含まれます。
- message-tool送信は、明示的な`threadId`が指定されていない限り、ターゲットが同じルームまたは同じDMユーザーターゲットであれば、現在のMatrixスレッドを自動継承するようになりました。
- 同一セッションのDMユーザーターゲット再利用は、現在のセッションメタデータが同じMatrixアカウント上の同じDM相手であることを証明できる場合にのみ有効になります。それ以外では、OpenClawは通常のユーザースコープルーティングにフォールバックします。
- OpenClawが、同じ共有Matrix DMセッション上で別のDMルームと衝突するMatrix DMルームを検出すると、thread bindingsが有効で`dm.sessionScope`ヒントがある場合、そのルームに`/focus`エスケープハッチを含む1回限りの`m.notice`を投稿します。
- 実行時thread bindingsはMatrixでサポートされています。`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`、およびスレッドにバインドされた`/acp spawn`が、MatrixルームとDMで動作するようになりました。
- トップレベルのMatrix room/DMでの`/focus`は、`threadBindings.spawnSubagentSessions=true`の場合、新しいMatrixスレッドを作成し、それを対象セッションにバインドします。
- 既存のMatrixスレッド内で`/focus`または`/acp spawn --thread here`を実行すると、その現在のスレッドに代わりにバインドされます。

## ACP会話バインディング

Matrixルーム、DM、既存のMatrixスレッドは、チャット画面を変えずに永続的なACPワークスペースへ変換できます。

高速なオペレーターフロー:

- 使い続けたいMatrix DM、ルーム、または既存スレッド内で`/acp spawn codex --bind here`を実行します。
- トップレベルのMatrix DMまたはルームでは、現在のDM/ルームがチャット画面のまま維持され、今後のメッセージは生成されたACPセッションへルーティングされます。
- 既存のMatrixスレッド内では、`--bind here`がその現在のスレッドをその場でバインドします。
- `/new`と`/reset`は、同じバインド済みACPセッションをその場でリセットします。
- `/acp close`はACPセッションを閉じてバインディングを削除します。

注意:

- `--bind here`は子Matrixスレッドを作成しません。
- `threadBindings.spawnAcpSessions`が必要なのは、OpenClawが子Matrixスレッドを作成またはバインドする必要がある`/acp spawn --thread auto|here`の場合のみです。

### Thread Binding Config

Matrixは`session.threadBindings`からグローバルデフォルトを継承し、チャネルごとの上書きもサポートします:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrixのthread-bound spawnフラグはオプトインです:

- トップレベルの`/focus`で新しいMatrixスレッドの作成とバインドを許可するには、`threadBindings.spawnSubagentSessions: true`を設定します。
- `/acp spawn --thread auto|here`でACPセッションをMatrixスレッドへバインドできるようにするには、`threadBindings.spawnAcpSessions: true`を設定します。

## リアクション

Matrixは、送信リアクション操作、受信リアクション通知、および受信ackリアクションをサポートします。

- 送信リアクションtoolingは`channels["matrix"].actions.reactions`で制御されます。
- `react`は特定のMatrixイベントにリアクションを追加します。
- `reactions`は特定のMatrixイベントに対する現在のリアクション要約を一覧表示します。
- `emoji=""`は、そのイベント上のボットアカウント自身のリアクションを削除します。
- `remove: true`は、ボットアカウントの指定された絵文字リアクションのみを削除します。

ack reactionは、標準のOpenClaw解決順序を使用します:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- エージェントidentity絵文字へのフォールバック

ack reaction scopeは次の順で解決されます:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

reaction notification modeは次の順で解決されます:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- デフォルト: `own`

現在の動作:

- `reactionNotifications: "own"`は、botが作成したMatrixメッセージを対象とする追加済み`m.reaction`イベントを転送します。
- `reactionNotifications: "off"`は、reactionシステムイベントを無効にします。
- リアクション削除は、Matrixではそれらが独立した`m.reaction`削除ではなくredactionとして表現されるため、依然としてシステムイベントには合成されません。

## 履歴コンテキスト

- `channels.matrix.historyLimit`は、Matrixルームメッセージがエージェントをトリガーしたときに`InboundHistory`として含める最近のルームメッセージ数を制御します。
- これは`messages.groupChat.historyLimit`にフォールバックします。両方とも未設定の場合、有効デフォルトは`0`なので、メンション制御されたルームメッセージはバッファされません。無効にするには`0`を設定してください。
- Matrixルーム履歴はルーム専用です。DMは引き続き通常のセッション履歴を使用します。
- Matrixルーム履歴はpending-onlyです。OpenClawはまだ返信をトリガーしていないルームメッセージをバッファし、メンションや他のトリガーが到着したときにそのウィンドウをスナップショットします。
- 現在のトリガーメッセージは`InboundHistory`には含まれません。そのターンのメイン受信本文に残ります。
- 同じMatrixイベントの再試行では、より新しいルームメッセージへ進んでしまうことなく、元の履歴スナップショットが再利用されます。

## コンテキスト可視性

Matrixは、取得した返信テキスト、スレッドルート、保留中履歴などの補足ルームコンテキストに対して共有の`contextVisibility`制御をサポートします。

- `contextVisibility: "all"`がデフォルトです。補足コンテキストは受信したまま保持されます。
- `contextVisibility: "allowlist"`は、補足コンテキストを、アクティブなルーム/ユーザーallowlistチェックで許可された送信者に絞り込みます。
- `contextVisibility: "allowlist_quote"`は`allowlist`と同様に動作しますが、明示的な引用返信を1つだけ保持します。

この設定は、補足コンテキストの可視性に影響するものであり、受信メッセージ自体が返信をトリガーできるかどうかには影響しません。
トリガーの認可は引き続き`groupPolicy`、`groups`、`groupAllowFrom`、およびDM policy設定から決まります。

## DMとルームポリシーの例

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

メンション制御とallowlistの動作については、[Groups](/ja-JP/channels/groups)を参照してください。

Matrix DMのペアリング例:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

未承認のMatrixユーザーが承認前にメッセージを送り続けた場合、OpenClawは同じ保留中のペアリングコードを再利用し、新しいコードを発行する代わりに、短いクールダウン後に再度リマインダー返信を送ることがあります。

共有のDMペアリングフローとストレージレイアウトについては、[Pairing](/ja-JP/channels/pairing)を参照してください。

## Exec approvals

Matrixは、Matrixアカウントのexec approvalクライアントとして機能できます。

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers`（任意。`channels.matrix.dm.allowFrom`にフォールバック）
- `channels.matrix.execApprovals.target`（`dm` | `channel` | `both`、デフォルト: `dm`）
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

approversは`@owner:example.org`のようなMatrix user IDである必要があります。`enabled`が未設定または`"auto"`で、`execApprovals.approvers`または`channels.matrix.dm.allowFrom`から少なくとも1人のapproverを解決できる場合、Matrixはネイティブexec approvalsを自動有効化します。Matrixをネイティブapprovalクライアントとして明示的に無効にするには、`enabled: false`を設定してください。それ以外の場合、approvalリクエストは他の設定済みapprovalルートまたはexec approvalフォールバックポリシーにフォールバックします。

現在、ネイティブMatrixルーティングはexec専用です:

- `channels.matrix.execApprovals.*`は、exec approvals専用のネイティブDM/チャネルルーティングを制御します。
- Plugin approvalsは、引き続き共有のsame-chat `/approve`と、設定されている場合は`approvals.plugin`転送を使用します。
- Matrixは、安全にapproversを推定できる場合、plugin-approval認可のために`channels.matrix.dm.allowFrom`を再利用できますが、ネイティブなplugin-approval DM/チャネルファンアウト経路は個別には公開しません。

配信ルール:

- `target: "dm"`は、approver DMにapprovalプロンプトを送信します
- `target: "channel"`は、発信元のMatrixルームまたはDMにプロンプトを送り返します
- `target: "both"`は、approver DMと発信元のMatrixルームまたはDMの両方に送信します

Matrix approvalプロンプトは、主要なapprovalメッセージにreactionショートカットを付与します:

- `✅` = 1回だけ許可
- `❌` = 拒否
- `♾️` = 有効なexec policyでその判断が許可されている場合は常に許可

approversはそのメッセージにリアクションするか、フォールバックのスラッシュコマンドを使用できます: `/approve <id> allow-once`、`/approve <id> allow-always`、または`/approve <id> deny`。

承認または拒否できるのは、解決済みapproversのみです。チャネル配信にはコマンドテキストが含まれるため、`channel`または`both`は信頼できるルームでのみ有効にしてください。

Matrix approvalプロンプトは共有のコアapproval plannerを再利用します。Matrix固有のネイティブ画面は、exec approvals用のtransportのみです: ルーム/DMルーティング、およびメッセージの送信/更新/削除動作。

アカウントごとの上書き:

- `channels.matrix.accounts.<account>.execApprovals`

関連ドキュメント: [Exec approvals](/ja-JP/tools/exec-approvals)

## マルチアカウント例

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

トップレベルの`channels.matrix`値は、アカウント側で上書きされない限り、名前付きアカウントのデフォルトとして機能します。
継承されたルームエントリを1つのMatrixアカウントに限定するには、`groups.<room>.account`（または旧来の`rooms.<room>.account`）を使用できます。
`account`を持たないエントリはすべてのMatrixアカウントで共有され、`account: "default"`を持つエントリはデフォルトアカウントがトップレベルの`channels.matrix.*`に直接設定されている場合でも引き続き機能します。
共有認証デフォルトの一部だけでは、それ自体で別個の暗黙的デフォルトアカウントは作成されません。OpenClawがトップレベルの`default`アカウントを合成するのは、そのデフォルトに新しい認証情報（`homeserver` + `accessToken`、または`homeserver` + `userId` + `password`）がある場合のみです。名前付きアカウントは、その後でキャッシュ済み認証情報が認証要件を満たすなら、`homeserver` + `userId`だけでも引き続き検出可能な状態を維持できます。
Matrixにすでにちょうど1つの名前付きアカウントがある場合、または`defaultAccount`が既存の名前付きアカウントキーを指している場合、単一アカウントからマルチアカウントへの修復/セットアップ昇格では、新しい`accounts.default`エントリを作成せず、そのアカウントが保持されます。昇格されたアカウントへ移動するのはMatrix auth/bootstrap keysのみで、共有配信ポリシーキーはトップレベルに残ります。
暗黙ルーティング、プローブ、CLI操作において1つの名前付きMatrixアカウントを優先したい場合は、`defaultAccount`を設定してください。
複数の名前付きアカウントを設定する場合は、暗黙のアカウント選択に依存するCLIコマンドのために`defaultAccount`を設定するか、`--account <id>`を渡してください。
1つのコマンドだけでその暗黙選択を上書きしたい場合は、`openclaw matrix verify ...`と`openclaw matrix devices ...`に`--account <id>`を渡してください。

## プライベート/LAN homeserver

デフォルトでは、OpenClawはSSRF保護のため、プライベート/内部のMatrix homeserverをブロックします。
アカウントごとに明示的にオプトインした場合のみ許可されます。

お使いのhomeserverがlocalhost、LAN/Tailscale IP、または内部ホスト名で動作している場合は、
そのMatrixアカウントで`network.dangerouslyAllowPrivateNetwork`を有効にしてください:

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

CLIセットアップ例:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

このオプトインは、信頼できるプライベート/内部ターゲットのみを許可します。`http://matrix.example.org:8008`のような
公開の平文homeserverは引き続きブロックされます。可能な限り`https://`を推奨します。

## Matrixトラフィックのプロキシ

Matrixデプロイで明示的な送信HTTP(S)プロキシが必要な場合は、`channels.matrix.proxy`を設定します:

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

名前付きアカウントは`channels.matrix.accounts.<id>.proxy`でトップレベルのデフォルトを上書きできます。
OpenClawは、実行時のMatrixトラフィックとアカウント状態プローブの両方に同じプロキシ設定を使用します。

## ターゲット解決

OpenClawがルームまたはユーザーターゲットを求める箇所では、Matrixは以下のターゲット形式を受け付けます:

- ユーザー: `@user:server`、`user:@user:server`、または`matrix:user:@user:server`
- ルーム: `!room:server`、`room:!room:server`、または`matrix:room:!room:server`
- エイリアス: `#alias:server`、`channel:#alias:server`、または`matrix:channel:#alias:server`

ライブディレクトリ検索は、ログイン済みのMatrixアカウントを使用します:

- ユーザー検索は、そのhomeserverのMatrix user directoryに問い合わせます。
- ルーム検索は、明示的なルームIDとエイリアスを直接受け付け、その後そのアカウントの参加済みルーム名の検索にフォールバックします。
- 参加済みルーム名の検索はベストエフォートです。ルーム名をIDまたはエイリアスに解決できない場合、実行時のallowlist解決では無視されます。

## 設定リファレンス

- `enabled`: チャネルを有効または無効にします。
- `name`: アカウントの任意ラベルです。
- `defaultAccount`: 複数のMatrixアカウントが設定されている場合に優先されるアカウントIDです。
- `homeserver`: homeserver URLです。たとえば`https://matrix.example.org`。
- `network.dangerouslyAllowPrivateNetwork`: このMatrixアカウントがプライベート/内部homeserverへ接続できるようにします。homeserverが`localhost`、LAN/Tailscale IP、または`matrix-synapse`のような内部ホストへ解決される場合に有効化してください。
- `proxy`: Matrixトラフィック用の任意のHTTP(S)プロキシURLです。名前付きアカウントは独自の`proxy`でトップレベルデフォルトを上書きできます。
- `userId`: 完全なMatrix user IDです。たとえば`@bot:example.org`。
- `accessToken`: トークンベース認証用のアクセストークンです。平文値とSecretRef値は、env/file/exec providers全体で`channels.matrix.accessToken`および`channels.matrix.accounts.<id>.accessToken`でサポートされます。[Secrets Management](/ja-JP/gateway/secrets)を参照してください。
- `password`: パスワードベースログイン用のパスワードです。平文値とSecretRef値がサポートされます。
- `deviceId`: 明示的なMatrix device IDです。
- `deviceName`: パスワードログイン用のデバイス表示名です。
- `avatarUrl`: プロファイル同期と`set-profile`更新のために保存されるself-avatar URLです。
- `initialSyncLimit`: 起動時syncイベント制限です。
- `encryption`: E2EEを有効にします。
- `allowlistOnly`: DMとルームでallowlist専用動作を強制します。
- `allowBots`: 他の設定済みOpenClaw Matrixアカウントからのメッセージを許可します（`true`または`"mentions"`）。
- `groupPolicy`: `open`、`allowlist`、または`disabled`。
- `contextVisibility`: 補足ルームコンテキストの可視性モード（`all`、`allowlist`、`allowlist_quote`）。
- `groupAllowFrom`: ルームトラフィック用のuser ID allowlistです。
- `groupAllowFrom`のエントリは完全なMatrix user IDにする必要があります。解決できない名前は実行時に無視されます。
- `historyLimit`: グループ履歴コンテキストとして含めるルームメッセージの最大数です。`messages.groupChat.historyLimit`にフォールバックし、両方とも未設定の場合の有効デフォルトは`0`です。無効にするには`0`を設定してください。
- `replyToMode`: `off`、`first`、`all`、または`batched`。
- `markdown`: 送信Matrixテキスト用の任意のMarkdownレンダリング設定です。
- `streaming`: `off`（デフォルト）、`partial`、`quiet`、`true`、または`false`。`partial`と`true`は、通常のMatrixテキストメッセージによるプレビュー優先のドラフト更新を有効にします。`quiet`は、セルフホスト型push-rule構成向けに通知しないプレビュー通知を使用します。
- `blockStreaming`: `true`は、ドラフトプレビューストリーミングが有効な間、完了したアシスタントブロックごとの個別進行状況メッセージを有効にします。
- `threadReplies`: `off`、`inbound`、または`always`。
- `threadBindings`: スレッドにバインドされたセッションルーティングとライフサイクルのチャネルごとの上書きです。
- `startupVerification`: 起動時の自動自己検証リクエストモード（`if-unverified`、`off`）。
- `startupVerificationCooldownHours`: 自動起動検証リクエストを再試行するまでのクールダウンです。
- `textChunkLimit`: 送信メッセージのチャンクサイズです。
- `chunkMode`: `length`または`newline`。
- `responsePrefix`: 送信返信用の任意のメッセージプレフィックスです。
- `ackReaction`: このチャネル/アカウント向けの任意のack reaction上書きです。
- `ackReactionScope`: 任意のack reaction scope上書きです（`group-mentions`、`group-all`、`direct`、`all`、`none`、`off`）。
- `reactionNotifications`: 受信reaction通知モードです（`own`、`off`）。
- `mediaMaxMb`: Matrixメディア処理用のメディアサイズ上限（MB）です。送信と受信メディア処理の両方に適用されます。
- `autoJoin`: 招待の自動参加ポリシー（`always`、`allowlist`、`off`）。デフォルト: `off`。これはルーム/グループ招待だけでなく、DM形式の招待を含む一般的なMatrix招待に適用されます。OpenClawは、参加したルームをDMかグループか確実に分類できる前の招待時点でこの判断を行います。
- `autoJoinAllowlist`: `autoJoin`が`allowlist`のときに許可されるルーム/エイリアスです。エイリアスエントリは招待処理中にルームIDへ解決されます。OpenClawは、招待されたルームが主張するエイリアス状態を信頼しません。
- `dm`: DMポリシーブロック（`enabled`、`policy`、`allowFrom`、`sessionScope`、`threadReplies`）。
- `dm.policy`: OpenClawがルームに参加し、それをDMとして分類した後のDMアクセスを制御します。招待が自動参加されるかどうかは変更しません。
- `dm.allowFrom`のエントリは、ライブディレクトリ検索ですでに解決済みでない限り、完全なMatrix user IDにする必要があります。
- `dm.sessionScope`: `per-user`（デフォルト）または`per-room`。相手が同じでも各Matrix DMルームに別々のコンテキストを持たせたい場合は`per-room`を使用します。
- `dm.threadReplies`: DM専用のスレッドポリシー上書き（`off`、`inbound`、`always`）。DMにおける返信配置とセッション分離の両方で、トップレベルの`threadReplies`設定を上書きします。
- `execApprovals`: Matrixネイティブのexec approval配信（`enabled`、`approvers`、`target`、`agentFilter`、`sessionFilter`）。
- `execApprovals.approvers`: execリクエストを承認できるMatrix user IDです。`dm.allowFrom`ですでにapproversを識別できる場合は任意です。
- `execApprovals.target`: `dm | channel | both`（デフォルト: `dm`）。
- `accounts`: 名前付きアカウントごとの上書きです。トップレベルの`channels.matrix`値は、これらのエントリのデフォルトとして機能します。
- `groups`: ルームごとのポリシーマップです。ルームIDまたはエイリアスを推奨します。解決できないルーム名は実行時に無視されます。セッション/グループ識別には解決後の安定したroom IDが使われ、人間が読みやすいラベルは引き続きルーム名から取得されます。
- `groups.<room>.account`: マルチアカウント構成で、継承された1つのルームエントリを特定のMatrixアカウントに限定します。
- `groups.<room>.allowBots`: 設定済みbot送信者に対するルームレベルの上書きです（`true`または`"mentions"`）。
- `groups.<room>.users`: ルームごとの送信者allowlistです。
- `groups.<room>.tools`: ルームごとのtool許可/拒否上書きです。
- `groups.<room>.autoReply`: ルームレベルのメンション制御上書きです。`true`はそのルームのメンション要件を無効にし、`false`は再度有効にします。
- `groups.<room>.skills`: 任意のルームレベルskillフィルターです。
- `groups.<room>.systemPrompt`: 任意のルームレベルsystem promptスニペットです。
- `rooms`: `groups`の旧エイリアスです。
- `actions`: アクションごとのtool制御（`messages`、`reactions`、`pins`、`profile`、`memberInfo`、`channelInfo`、`verification`）。

## 関連

- [Channels Overview](/ja-JP/channels) — すべての対応チャネル
- [Pairing](/ja-JP/channels/pairing) — DM認証とペアリングフロー
- [Groups](/ja-JP/channels/groups) — グループチャットの動作とメンション制御
- [Channel Routing](/ja-JP/channels/channel-routing) — メッセージのセッションルーティング
- [Security](/ja-JP/gateway/security) — アクセスモデルとハードニング
