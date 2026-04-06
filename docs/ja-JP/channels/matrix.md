---
read_when:
    - OpenClawでMatrixをセットアップする
    - MatrixのE2EEと検証を設定する
summary: Matrixのサポート状況、セットアップ、設定例
title: Matrix
x-i18n:
    generated_at: "2026-04-06T03:08:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3e2d84c08d7d5b96db14b914e54f08d25334401cdd92eb890bc8dfb37b0ca2dc
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrixは、OpenClaw用のMatrixバンドルチャネルプラグインです。
公式の`matrix-js-sdk`を使用し、DM、ルーム、スレッド、メディア、リアクション、投票、位置情報、E2EEをサポートします。

## バンドルプラグイン

Matrixは現在のOpenClawリリースにバンドルプラグインとして含まれているため、通常の
パッケージビルドでは別途インストールは不要です。

古いビルドまたはMatrixを含まないカスタムインストールを使用している場合は、
手動でインストールしてください。

npmからインストール:

```bash
openclaw plugins install @openclaw/matrix
```

ローカルチェックアウトからインストール:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

プラグインの動作とインストールルールについては、[プラグイン](/ja-JP/tools/plugin)を参照してください。

## セットアップ

1. Matrixプラグインが利用可能であることを確認します。
   - 現在のパッケージ版OpenClawリリースにはすでに含まれています。
   - 古い/カスタムインストールでは、上記コマンドで手動追加できます。
2. ご自身のhomeserverでMatrixアカウントを作成します。
3. `channels.matrix`を次のいずれかで設定します。
   - `homeserver` + `accessToken`、または
   - `homeserver` + `userId` + `password`。
4. Gatewayを再起動します。
5. ボットとDMを開始するか、ルームに招待します。

対話型セットアップの経路:

```bash
openclaw channels add
openclaw configure --section channels
```

Matrixウィザードで実際に尋ねられる内容:

- homeserver URL
- 認証方法: アクセストークンまたはパスワード
- パスワード認証を選択した場合のみユーザーID
- 任意のデバイス名
- E2EEを有効にするかどうか
- Matrixルームアクセスを今すぐ設定するかどうか

重要なウィザードの動作:

- 選択したアカウントに対するMatrix認証env varsがすでに存在し、そのアカウントの認証がまだconfigに保存されていない場合、ウィザードはenvショートカットを提示し、そのアカウントには`enabled: true`のみを書き込みます。
- Matrixアカウントを対話的に追加すると、入力したアカウント名はconfigとenv varsで使われるアカウントIDに正規化されます。たとえば、`Ops Bot`は`ops-bot`になります。
- DM許可リストのプロンプトでは、完全な`@user:server`値をすぐに受け付けます。表示名は、ライブディレクトリ検索で厳密に1件一致した場合のみ機能します。それ以外の場合、ウィザードは完全なMatrix IDで再試行するよう求めます。
- ルーム許可リストのプロンプトでは、ルームIDとエイリアスを直接受け付けます。参加済みルーム名をライブで解決することもできますが、解決できなかった名前はセットアップ時に入力されたまま保持されるだけで、実行時の許可リスト解決では無視されます。`!room:server`または`#alias:server`を推奨します。
- 実行時のルーム/セッション識別には、安定したMatrixルームIDが使われます。ルームで宣言されたエイリアスは、長期的なセッションキーや安定したグループIDではなく、検索入力としてのみ使われます。
- 保存前にルーム名を解決するには、`openclaw channels resolve --channel matrix "Project Room"`を使います。

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

パスワードベース設定（ログイン後にトークンをキャッシュ）:

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
デフォルトアカウントは`credentials.json`を使用し、名前付きアカウントは`credentials-<account>.json`を使用します。
そこにキャッシュ済み認証情報が存在する場合、現在の認証がconfigに直接設定されていなくても、OpenClawはセットアップ、doctor、チャネルステータス検出においてMatrixが設定済みであると見なします。

環境変数の同等項目（configキーが未設定のときに使用）:

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

デフォルト以外のアカウントでは、アカウントスコープ付きenv varsを使用します:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

アカウント`ops`の例:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

正規化されたアカウントID`ops-bot`では、次を使用します:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrixは、アカウントID内の句読点をエスケープして、スコープ付きenv varsの衝突を防ぎます。
たとえば、`-`は`_X2D_`になるため、`ops-prod`は`MATRIX_OPS_X2D_PROD_*`に対応します。

対話型ウィザードがenv-varショートカットを提示するのは、それらの認証env varsがすでに存在し、かつ選択したアカウントにMatrix認証がまだconfigに保存されていない場合だけです。

## 設定例

これは、DMペアリング、ルーム許可リスト、有効化されたE2EEを備えた実用的なベースライン設定です:

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

## ストリーミングプレビュー

Matrixの返信ストリーミングはオプトインです。

OpenClawに単一のライブプレビュー
返信を送信させ、モデルがテキストを生成している間そのプレビューをその場で編集し、返信完了時に最終化したい場合は、
`channels.matrix.streaming`を`"partial"`に設定してください:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"`がデフォルトです。OpenClawは最終返信を待って一度だけ送信します。
- `streaming: "partial"`は、現在のassistantブロック用に通常のMatrixテキストメッセージを使った編集可能なプレビューメッセージを1つ作成します。これにより、Matrixの従来の「プレビュー優先」通知動作が維持されるため、標準クライアントでは完成済みブロックではなく、最初にストリーミングされたプレビューテキストで通知されることがあります。
- `streaming: "quiet"`は、現在のassistantブロック用に編集可能な静かなプレビュー通知を1つ作成します。これは、最終化されたプレビュー編集用の受信者プッシュルールも設定する場合にのみ使用してください。
- `blockStreaming: true`は、個別のMatrix進捗メッセージを有効にします。プレビューのストリーミングが有効な場合、Matrixは現在のブロックのライブドラフトを維持し、完了済みブロックを別メッセージとして保持します。
- プレビューが有効で`blockStreaming`がoffの場合、Matrixはライブドラフトをその場で編集し、ブロックまたはターン終了時にその同じイベントを最終化します。
- プレビューが1つのMatrixイベントに収まらなくなった場合、OpenClawはプレビューのストリーミングを停止し、通常の最終配信にフォールバックします。
- メディア返信は引き続き通常どおり添付ファイルを送信します。古いプレビューを安全に再利用できなくなった場合、OpenClawは最終メディア返信を送る前にそれを削除します。
- プレビュー編集には追加のMatrix API呼び出しがかかります。最も保守的なレート制限挙動を望む場合は、ストリーミングをoffのままにしてください。

`blockStreaming`だけではドラフトプレビューは有効になりません。
プレビュー編集には`streaming: "partial"`または`streaming: "quiet"`を使用し、完了済みassistantブロックも個別の進捗メッセージとして表示したい場合にのみ`blockStreaming: true`を追加してください。

カスタムプッシュルールなしで標準のMatrix通知が必要な場合は、プレビュー優先動作には`streaming: "partial"`を使用するか、最終版のみ配信するために`streaming`をoffのままにしてください。`streaming: "off"`では:

- `blockStreaming: true`は、完了した各ブロックを通常の通知付きMatrixメッセージとして送信します。
- `blockStreaming: false`は、最終的に完成した返信のみを通常の通知付きMatrixメッセージとして送信します。

### 静かな最終化プレビュー向けのセルフホスト型プッシュルール

独自のMatrix基盤を運用していて、静かなプレビューをブロックまたは
最終返信の完了時にのみ通知させたい場合は、`streaming: "quiet"`を設定し、最終化されたプレビュー編集用にユーザー単位のプッシュルールを追加してください。

これは通常、homeserver全体の設定変更ではなく、受信側ユーザーの設定です:

始める前の簡単な対応表:

- recipient user = 通知を受け取るべき人
- bot user = 返信を送信するOpenClaw Matrixアカウント
- 以下のAPI呼び出しではrecipient userのアクセストークンを使う
- プッシュルールの`sender`はbot userの完全なMXIDに一致させる

1. OpenClawを静かなプレビューを使うよう設定します:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. 受信側アカウントがすでに通常のMatrixプッシュ通知を受け取っていることを確認します。静かなプレビュー
   ルールが機能するのは、そのユーザーに既存の有効なpusher/devicesがある場合だけです。

3. 受信側ユーザーのアクセストークンを取得します。
   - ボットのトークンではなく、受信側ユーザーのトークンを使用してください。
   - 既存のクライアントセッショントークンを再利用するのが通常は最も簡単です。
   - 新しいトークンを発行する必要がある場合は、標準のMatrix Client-Server APIからログインできます:

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

4. 受信側アカウントにすでにpushersがあることを確認します:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

これが有効なpushers/devicesを返さない場合は、以下の
OpenClawルールを追加する前に、まず通常のMatrix通知を修正してください。

OpenClawは、最終化されたテキストのみのプレビュー編集に次のマーカーを付けます:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. これらの通知を受け取るべき各受信側アカウントに対して、overrideプッシュルールを作成します:

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

コマンド実行前に、以下の値を置き換えてください:

- `https://matrix.example.org`: あなたのhomeserverのベースURL
- `$USER_ACCESS_TOKEN`: 受信側ユーザーのアクセストークン
- `openclaw-finalized-preview-botname`: この受信側ユーザーに対するこのボット用の一意なrule ID
- `@bot:example.org`: 受信側ユーザーのMXIDではなく、あなたのOpenClaw MatrixボットMXID

複数ボット構成で重要な点:

- プッシュルールは`ruleId`で識別されます。同じrule IDに対して`PUT`を再実行すると、その1つのルールが更新されます。
- 1人の受信側ユーザーが複数のOpenClaw Matrixボットアカウントから通知を受ける必要がある場合は、各sender一致に対して一意なrule IDを持つルールをボットごとに1つ作成してください。
- 単純なパターンとしては`openclaw-finalized-preview-<botname>`があり、たとえば`openclaw-finalized-preview-ops`や`openclaw-finalized-preview-support`です。

このルールはイベント送信者に対して評価されます:

- 受信側ユーザーのトークンで認証する
- `sender`をOpenClawボットのMXIDに一致させる

6. ルールが存在することを確認します:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. ストリーミング返信をテストします。quietモードでは、ルームには静かなドラフトプレビューが表示され、
   ブロックまたはターンが完了すると、その場での最終編集で1回通知されるはずです。

後でルールを削除する必要がある場合は、受信側ユーザーのトークンで同じrule IDを削除してください:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

注意:

- ルールの作成には、ボットのトークンではなく受信側ユーザーのアクセストークンを使用してください。
- 新しいユーザー定義の`override`ルールは、デフォルトの抑制ルールより前に挿入されるため、追加の順序パラメーターは不要です。
- これは、OpenClawが安全にその場で最終化できるテキストのみのプレビュー編集にのみ影響します。メディアフォールバックや古いプレビューフォールバックでは、引き続き通常のMatrix配信を使用します。
- `GET /_matrix/client/v3/pushers`がpushersを示さない場合、そのユーザーはそのアカウント/デバイスでまだ有効なMatrixプッシュ配信を持っていません。

#### Synapse

Synapseでは、通常、上記の設定だけで十分です:

- 最終化されたOpenClawプレビュー通知のために特別な`homeserver.yaml`変更は不要です。
- Synapseデプロイですでに通常のMatrixプッシュ通知が送信されている場合、主な設定手順は上記のユーザートークン + `pushrules`呼び出しです。
- Synapseをリバースプロキシやworkersの背後で実行している場合は、`/_matrix/client/.../pushrules/`が正しくSynapseに届くことを確認してください。
- Synapse workersを実行している場合は、pushersが正常であることを確認してください。プッシュ配信はメインプロセスまたは`synapse.app.pusher` / 設定済みpusher workersによって処理されます。

#### Tuwunel

Tuwunelでは、上記と同じセットアップフローとpush-rule API呼び出しを使用します:

- 最終化プレビューマーカー自体のためのTuwunel固有設定は不要です。
- そのユーザーに対して通常のMatrix通知がすでに機能している場合、主な設定手順は上記のユーザートークン + `pushrules`呼び出しです。
- ユーザーが別のデバイスでアクティブな間に通知が消えるように見える場合は、`suppress_push_when_active`が有効になっていないか確認してください。Tuwunelは2025年9月12日のTuwunel 1.4.2でこのオプションを追加しており、1つのデバイスがアクティブな間、他のデバイスへのプッシュを意図的に抑制することがあります。

## 暗号化と検証

暗号化された（E2EE）ルームでは、送信画像イベントは`thumbnail_file`を使用するため、画像プレビューは完全な添付ファイルと一緒に暗号化されます。暗号化されていないルームでは引き続き通常の`thumbnail_url`を使用します。設定は不要です — プラグインがE2EE状態を自動検出します。

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

- `allowBots: true`は、許可されたルームとDMで他の設定済みMatrixボットアカウントからのメッセージを受け入れます。
- `allowBots: "mentions"`は、ルーム内でそれらのメッセージがこのボットに明示的にメンションしている場合にのみ受け入れます。DMは引き続き許可されます。
- `groups.<room>.allowBots`は、1つのルームに対してアカウントレベル設定を上書きします。
- OpenClawは自己返信ループを避けるため、同じMatrix user IDからのメッセージは引き続き無視します。
- Matrixはここでネイティブのbotフラグを公開しないため、OpenClawは「bot-authored」を「このOpenClaw Gateway上の別の設定済みMatrixアカウントによって送信されたもの」として扱います。

共有ルームでボット間トラフィックを有効にする場合は、厳格なルーム許可リストとメンション要件を使用してください。

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

検証ステータスを確認する:

```bash
openclaw matrix verify status
```

詳細ステータス（完全な診断）:

```bash
openclaw matrix verify status --verbose
```

保存済みのリカバリーキーを機械可読出力に含める:

```bash
openclaw matrix verify status --include-recovery-key --json
```

クロスサイニングと検証状態をブートストラップする:

```bash
openclaw matrix verify bootstrap
```

マルチアカウント対応: アカウントごとの認証情報と任意の`name`を含む`channels.matrix.accounts`を使用します。共有パターンについては、[設定リファレンス](/ja-JP/gateway/configuration-reference#multi-account-all-channels)を参照してください。

詳細なブートストラップ診断:

```bash
openclaw matrix verify bootstrap --verbose
```

ブートストラップ前に新しいクロスサイニングIDリセットを強制する:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

リカバリーキーでこのデバイスを検証する:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

詳細なデバイス検証の詳細:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

ルームキーバックアップの健全性を確認する:

```bash
openclaw matrix verify backup status
```

詳細なバックアップ健全性診断:

```bash
openclaw matrix verify backup status --verbose
```

サーバーバックアップからルームキーを復元する:

```bash
openclaw matrix verify backup restore
```

詳細な復元診断:

```bash
openclaw matrix verify backup restore --verbose
```

現在のサーバーバックアップを削除し、新しいバックアップベースラインを作成します。保存済みの
バックアップキーを正常に読み込めない場合、このリセットではシークレットストレージも再作成できるため、
今後のコールドスタートで新しいバックアップキーを読み込めるようになります:

```bash
openclaw matrix verify backup reset --yes
```

すべての`verify`コマンドはデフォルトで簡潔です（静かな内部SDKログを含む）。詳細な診断は`--verbose`が付いた場合にのみ表示されます。
スクリプトで使用する場合は、完全な機械可読出力のために`--json`を使用してください。

マルチアカウント構成では、`--account <id>`を渡さない限り、Matrix CLIコマンドは暗黙のMatrixデフォルトアカウントを使います。
複数の名前付きアカウントを設定している場合は、まず`channels.matrix.defaultAccount`を設定してください。設定しないと、それらの暗黙的なCLI操作は停止し、アカウントを明示的に選ぶよう求めます。
検証やデバイス操作を明示的に名前付きアカウントに向けたい場合は、`--account`を使用してください:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

暗号化が無効または名前付きアカウントで利用できない場合、Matrixの警告や検証エラーは、そのアカウントのconfigキーを指します。たとえば`channels.matrix.accounts.assistant.encryption`です。

### 「verified」の意味

OpenClawは、このMatrixデバイスがあなた自身のクロスサイニングIDによって検証されている場合にのみ、このMatrixデバイスをverifiedとして扱います。
実際には、`openclaw matrix verify status --verbose`は3つの信頼シグナルを公開します:

- `Locally trusted`: このデバイスは現在のクライアントによってのみ信頼されている
- `Cross-signing verified`: SDKがこのデバイスをクロスサイニング経由で検証済みと報告している
- `Signed by owner`: このデバイスがあなた自身のself-signingキーで署名されている

`Verified by owner`が`yes`になるのは、クロスサイニング検証またはowner-signingが存在する場合だけです。
ローカル信頼だけでは、OpenClawはそのデバイスを完全に検証済みとは見なしません。

### bootstrapが行うこと

`openclaw matrix verify bootstrap`は、暗号化されたMatrixアカウントの修復およびセットアップコマンドです。
次のすべてを順番に実行します:

- 可能であれば既存のリカバリーキーを再利用しつつ、シークレットストレージをブートストラップする
- クロスサイニングをブートストラップし、不足している公開クロスサイニングキーをアップロードする
- 現在のデバイスをマークし、クロスサインしようと試みる
- まだ存在しない場合は、新しいサーバー側ルームキーバックアップを作成する

homeserverがクロスサイニングキーのアップロードに対話型認証を要求する場合、OpenClawはまず認証なしでアップロードを試み、次に`m.login.dummy`、さらに`channels.matrix.password`が設定されている場合は`m.login.password`で試みます。

`--force-reset-cross-signing`は、現在のクロスサイニングIDを意図的に破棄して新しいものを作成したい場合にのみ使用してください。

現在のルームキーバックアップを意図的に破棄し、将来のメッセージ用に新しい
バックアップベースラインを開始したい場合は、`openclaw matrix verify backup reset --yes`を使用してください。
これは、復元不能な古い暗号化履歴が引き続き利用不可のままになること、
および現在のバックアップシークレットを安全に読み込めない場合にOpenClawがシークレットストレージを再作成する可能性を
受け入れる場合にのみ行ってください。

### 新しいバックアップベースライン

今後の暗号化メッセージを引き続き機能させ、復元不能な古い履歴を失うことを受け入れる場合は、次のコマンドを順に実行してください:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

名前付きMatrixアカウントを明示的に対象にしたい場合は、各コマンドに`--account <id>`を追加してください。

### 起動時の動作

`encryption: true`の場合、Matrixは`startupVerification`をデフォルトで`"if-unverified"`にします。
起動時にこのデバイスがまだ未検証の場合、Matrixは別のMatrixクライアントで自己検証を要求し、
すでに1つ保留中の場合は重複要求をスキップし、再起動後の再試行前にローカルクールダウンを適用します。
デフォルトでは、失敗した要求試行は成功した要求作成よりも早く再試行されます。
自動起動要求を無効にするには`startupVerification: "off"`を設定するか、
再試行ウィンドウを短くまたは長くしたい場合は`startupVerificationCooldownHours`を調整してください。

起動時には、保守的なcrypto bootstrapパスも自動的に実行されます。
このパスはまず現在のシークレットストレージとクロスサイニングIDの再利用を試み、明示的なbootstrap修復フローを実行しない限り、クロスサイニングのリセットを避けます。

起動時に壊れたbootstrap状態が見つかり、`channels.matrix.password`が設定されている場合、OpenClawはより厳格な修復パスを試みることができます。
現在のデバイスがすでにowner-signedである場合、OpenClawはそのIDを自動的にリセットせず保持します。

以前の公開Matrixプラグインからのアップグレード:

- OpenClawは、可能な限り同じMatrixアカウント、アクセストークン、デバイスIDを自動的に再利用します。
- 実行可能なMatrix移行変更が実行される前に、OpenClawは`~/Backups/openclaw-migrations/`の下にリカバリースナップショットを作成または再利用します。
- 複数のMatrixアカウントを使用している場合、古いフラットストアレイアウトからアップグレードする前に`channels.matrix.defaultAccount`を設定して、どのアカウントがその共有レガシー状態を受け取るべきかをOpenClawが把握できるようにしてください。
- 以前のプラグインがMatrixルームキーバックアップ復号キーをローカルに保存していた場合、起動時または`openclaw doctor --fix`がそれを新しいリカバリーキーフローに自動的にインポートします。
- 移行の準備後にMatrixアクセストークンが変更された場合、起動時には自動バックアップ復元をあきらめる前に、保留中のレガシー復元状態を持つ兄弟トークンハッシュストレージルートをスキャンします。
- 同じアカウント、homeserver、userに対して後からMatrixアクセストークンが変更された場合、OpenClawは空のMatrix状態ディレクトリから開始するのではなく、最も完全な既存のトークンハッシュストレージルートの再利用を優先するようになりました。
- 次回Gateway起動時に、バックアップされたルームキーが新しいcrypto storeへ自動的に復元されます。
- 古いプラグインにバックアップされていないローカル専用ルームキーがあった場合、OpenClawは明確に警告します。それらのキーは以前のrust crypto storeから自動エクスポートできないため、手動で回復されるまでは一部の古い暗号化履歴が引き続き利用できない可能性があります。
- 完全なアップグレードフロー、制限、回復コマンド、一般的な移行メッセージについては、[Matrix migration](/ja-JP/install/migrating-matrix)を参照してください。

暗号化されたランタイム状態は、アカウントごと、ユーザーごとのトークンハッシュルート配下の
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`に整理されます。
このディレクトリには、同期ストア（`bot-storage.json`）、crypto store（`crypto/`）、
リカバリーキーファイル（`recovery-key.json`）、IndexedDBスナップショット（`crypto-idb-snapshot.json`）、
スレッドバインディング（`thread-bindings.json`）、起動時検証状態（`startup-verification.json`）
が、それらの機能使用時に含まれます。
トークンが変わってもアカウントIDが同じである場合、OpenClawはそのアカウント/homeserver/user組に対して最適な既存
ルートを再利用するため、以前の同期状態、crypto状態、スレッドバインディング、
起動時検証状態が引き続き見えるままになります。

### Node crypto storeモデル

このプラグインのMatrix E2EEは、Nodeにおける公式`matrix-js-sdk`のRust cryptoパスを使用します。
そのパスでは、crypto stateを再起動後も保持したい場合、IndexedDBベースの永続化が必要です。

OpenClawは現在、Nodeでこれを次の方法で提供しています:

- SDKが期待するIndexedDB API shimとして`fake-indexeddb`を使用する
- `initRustCrypto`の前に`crypto-idb-snapshot.json`からRust crypto IndexedDB内容を復元する
- 初期化後および実行中に、更新されたIndexedDB内容を`crypto-idb-snapshot.json`へ永続化する
- Gateway実行時の永続化とCLI保守が同じスナップショットファイルで競合しないように、助言的ファイルロックで`crypto-idb-snapshot.json`に対するスナップショット復元と永続化を直列化する

これは互換性/ストレージの配管であり、独自の暗号実装ではありません。
スナップショットファイルは機密ランタイム状態であり、厳しいファイル権限で保存されます。
OpenClawのセキュリティモデルでは、GatewayホストとローカルOpenClaw状態ディレクトリはすでに信頼された運用者境界内にあるため、これは主として別個のリモート信頼境界ではなく、運用上の耐久性に関する問題です。

計画中の改善:

- 永続的なMatrix鍵素材に対するSecretRefサポートを追加し、リカバリーキーや関連するストア暗号化シークレットを、ローカルファイルだけでなくOpenClaw secrets providersから取得できるようにする

## プロフィール管理

選択したアカウントのMatrix self-profileを更新するには、次を使用します:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

名前付きMatrixアカウントを明示的に対象にしたい場合は、`--account <id>`を追加してください。

Matrixは`mxc://`アバターURLを直接受け付けます。`http://`または`https://`のアバターURLを渡した場合、OpenClawはまずそれをMatrixにアップロードし、解決された`mxc://` URLを`channels.matrix.avatarUrl`（または選択したアカウントのoverride）に保存し直します。

## 自動検証通知

Matrixは、検証ライフサイクル通知を厳格なDM検証ルームに`m.notice`メッセージとして直接投稿するようになりました。
これには次が含まれます:

- 検証要求通知
- 検証準備完了通知（明示的な「Verify by emoji」ガイダンス付き）
- 検証開始および完了通知
- 利用可能な場合のSAS詳細（絵文字と10進数）

別のMatrixクライアントからの受信検証要求は、OpenClawによって追跡され自動承認されます。
自己検証フローでは、絵文字検証が利用可能になるとOpenClawはSASフローも自動開始し、自分側を確認します。
別のMatrixユーザー/デバイスからの検証要求では、OpenClawは要求を自動承認し、その後SASフローが通常どおり進行するのを待ちます。
検証を完了するには、引き続きご利用のMatrixクライアントで絵文字または10進数SASを比較し、「They match」を確認する必要があります。

OpenClawは、自己開始の重複フローを無条件に自動承認することはありません。自己検証要求がすでに保留中の場合、起動時に新しい要求は作成されません。

検証プロトコル/システム通知はエージェントチャットパイプラインへ転送されないため、`NO_REPLY`は発生しません。

### デバイス衛生

古いOpenClaw管理のMatrixデバイスがアカウント上に蓄積し、暗号化ルームの信頼を把握しにくくすることがあります。
一覧表示するには次を使います:

```bash
openclaw matrix devices list
```

古いOpenClaw管理デバイスを削除するには次を使います:

```bash
openclaw matrix devices prune-stale
```

### Direct Room Repair

ダイレクトメッセージ状態が同期ずれを起こすと、OpenClawはライブDMではなく古い1人用ルームを指す古い`m.direct`マッピングを持つことがあります。ピアに対する現在のマッピングを調べるには次を使います:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

修復するには次を使います:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

修復では、Matrix固有ロジックをプラグイン内に保ちます:

- すでに`m.direct`にマップされている厳格な1:1 DMを優先する
- それ以外では、そのユーザーとの現在参加中の厳格な1:1 DMにフォールバックする
- 健全なDMが存在しない場合は、新しいダイレクトルームを作成し、`m.direct`をそれに向けて書き換える

修復フローは古いルームを自動削除しません。健全なDMを選び、マッピングを更新するだけで、新しいMatrix送信、検証通知、その他のダイレクトメッセージフローが再び正しいルームを対象にするようになります。

## スレッド

Matrixは、自動返信とmessage-tool送信の両方でネイティブMatrixスレッドをサポートします。

- `dm.sessionScope: "per-user"`（デフォルト）は、Matrix DMルーティングを送信者スコープで維持するため、同じ相手に解決される複数のDMルームが1つのセッションを共有できます。
- `dm.sessionScope: "per-room"`は、通常のDM認証と許可リストチェックを使いながら、各Matrix DMルームを独自のセッションキーに分離します。
- 明示的なMatrix会話バインディングは引き続き`dm.sessionScope`より優先されるため、バインド済みルームやスレッドは選択された対象セッションを維持します。
- `threadReplies: "off"`は、返信をトップレベルのままにし、受信スレッドメッセージを親セッション上に保ちます。
- `threadReplies: "inbound"`は、受信メッセージがすでにそのスレッド内にあった場合にのみスレッド内で返信します。
- `threadReplies: "always"`は、ルーム返信をトリガーメッセージをルートとするスレッド内に保ち、その会話を最初のトリガーメッセージから対応するスレッドスコープのセッションを通じてルーティングします。
- `dm.threadReplies`は、DMに対してのみトップレベル設定を上書きします。たとえば、ルームスレッドを分離したまま、DMはフラットに保てます。
- 受信スレッドメッセージには、追加のagent contextとしてスレッドルートメッセージが含まれます。
- message-tool送信は、対象が同じルーム、または同じDMユーザー対象である場合、明示的な`threadId`が指定されない限り、現在のMatrixスレッドを自動継承するようになりました。
- 同一セッションのDMユーザー対象再利用が有効になるのは、現在のセッションメタデータによって同じMatrixアカウント上の同じDM相手であることが証明される場合だけです。それ以外では、OpenClawは通常のユーザースコープルーティングにフォールバックします。
- OpenClawが、同じ共有Matrix DMセッション上であるMatrix DMルームが別のDMルームと衝突していることを検出した場合、スレッドバインディングが有効で`dm.sessionScope`ヒントがあると、そのルームに`/focus`エスケープハッチ付きの一度限りの`m.notice`を投稿します。
- Matrixはランタイムスレッドバインディングをサポートしています。`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`、およびスレッドバインドされた`/acp spawn`は、MatrixルームとDMで動作するようになりました。
- トップレベルのMatrixルーム/DMでの`/focus`は、`threadBindings.spawnSubagentSessions=true`のとき、新しいMatrixスレッドを作成し、それを対象セッションにバインドします。
- 既存のMatrixスレッド内で`/focus`または`/acp spawn --thread here`を実行すると、代わりにその現在のスレッドをバインドします。

## ACP会話バインディング

Matrixルーム、DM、既存のMatrixスレッドは、チャット面を変更せずに永続的なACPワークスペースへ変換できます。

高速な運用フロー:

- 使用し続けたいMatrix DM、ルーム、または既存スレッド内で`/acp spawn codex --bind here`を実行します。
- トップレベルのMatrix DMまたはルームでは、現在のDM/ルームがチャット面のまま維持され、今後のメッセージは生成されたACPセッションへルーティングされます。
- 既存のMatrixスレッド内では、`--bind here`がその現在のスレッドをその場でバインドします。
- `/new`と`/reset`は、同じバインド済みACPセッションをその場でリセットします。
- `/acp close`はACPセッションを閉じ、バインディングを削除します。

注意:

- `--bind here`は子Matrixスレッドを作成しません。
- `threadBindings.spawnAcpSessions`が必要になるのは、OpenClawが子Matrixスレッドを作成またはバインドする必要がある`/acp spawn --thread auto|here`の場合だけです。

### Thread Binding Config

Matrixは`session.threadBindings`からグローバルデフォルトを継承し、チャネルごとのoverrideもサポートします:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrixのスレッドバインドspawnフラグはオプトインです:

- トップレベルの`/focus`で新しいMatrixスレッドの作成とバインドを許可するには、`threadBindings.spawnSubagentSessions: true`を設定します。
- `/acp spawn --thread auto|here`でACPセッションをMatrixスレッドへバインドできるようにするには、`threadBindings.spawnAcpSessions: true`を設定します。

## リアクション

Matrixは、送信リアクションアクション、受信リアクション通知、受信ackリアクションをサポートします。

- 送信リアクションtoolingは`channels["matrix"].actions.reactions`で制御されます。
- `react`は、特定のMatrixイベントにリアクションを追加します。
- `reactions`は、特定のMatrixイベントに対する現在のリアクション要約を一覧表示します。
- `emoji=""`は、そのイベントに対するボットアカウント自身のリアクションを削除します。
- `remove: true`は、ボットアカウントから指定された絵文字リアクションだけを削除します。

ackリアクションは、標準のOpenClaw解決順序を使用します:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- agent identity emoji fallback

ackリアクションスコープは次の順序で解決されます:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

リアクション通知モードは次の順序で解決されます:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- デフォルト: `own`

現在の挙動:

- `reactionNotifications: "own"`は、ボット作成のMatrixメッセージを対象にした追加済み`m.reaction`イベントを転送します。
- `reactionNotifications: "off"`は、リアクションシステムイベントを無効にします。
- Matrixではリアクション削除が単独の`m.reaction`削除ではなくredactionsとして現れるため、リアクション削除はまだシステムイベントに合成されません。

## 履歴コンテキスト

- `channels.matrix.historyLimit`は、Matrixルームメッセージがagentをトリガーしたときに`InboundHistory`として含める最近のルームメッセージ数を制御します。
- これは`messages.groupChat.historyLimit`にフォールバックします。無効にするには`0`を設定してください。
- Matrixルーム履歴はルーム専用です。DMは引き続き通常のセッション履歴を使用します。
- Matrixルーム履歴はpending-onlyです。OpenClawはまだ返信をトリガーしていないルームメッセージをバッファし、メンションや他のトリガーが到着したときにそのウィンドウをスナップショットします。
- 現在のトリガーメッセージは`InboundHistory`には含まれません。そのターンのメイン受信本文に残ります。
- 同じMatrixイベントの再試行では、新しいルームメッセージへ前進してずれるのではなく、元の履歴スナップショットが再利用されます。

## コンテキスト可視性

Matrixは、取得された返信テキスト、スレッドルート、保留履歴などの補足ルームコンテキストに対する共有の`contextVisibility`制御をサポートします。

- `contextVisibility: "all"`がデフォルトです。補足コンテキストは受信したまま保持されます。
- `contextVisibility: "allowlist"`は、アクティブなルーム/ユーザー許可リストチェックで許可された送信者に補足コンテキストを絞り込みます。
- `contextVisibility: "allowlist_quote"`は`allowlist`と同様に動作しますが、明示的な引用返信を1つだけ保持します。

この設定は補足コンテキストの可視性に影響するものであり、受信メッセージ自体が返信をトリガーできるかどうかには影響しません。
トリガー認可は引き続き`groupPolicy`、`groups`、`groupAllowFrom`、およびDMポリシー設定から行われます。

## DMとルームのポリシー例

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

メンションゲーティングと許可リストの挙動については、[グループ](/ja-JP/channels/groups)を参照してください。

Matrix DMのペアリング例:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

未承認のMatrixユーザーが承認前に繰り返しメッセージを送ってきた場合、OpenClawは同じ保留中のペアリングコードを再利用し、新しいコードを発行する代わりに、短いクールダウン後に再度リマインダー返信を送ることがあります。

共有のDMペアリングフローと保存レイアウトについては、[ペアリング](/ja-JP/channels/pairing)を参照してください。

## Exec承認

Matrixは、Matrixアカウントのexec承認クライアントとして機能できます。

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers`（任意。`channels.matrix.dm.allowFrom`にフォールバック）
- `channels.matrix.execApprovals.target`（`dm` | `channel` | `both`、デフォルト: `dm`）
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

承認者は`@owner:example.org`のようなMatrix user IDである必要があります。`enabled`が未設定または`"auto"`で、`execApprovals.approvers`または`channels.matrix.dm.allowFrom`のいずれかから少なくとも1人の承認者を解決できる場合、Matrixはネイティブexec承認を自動有効化します。Matrixをネイティブ承認クライアントとして明示的に無効化するには、`enabled: false`を設定してください。そうしない場合、承認要求は他の設定済み承認経路またはexec承認フォールバックポリシーへフォールバックします。

現在、ネイティブMatrixルーティングはexec専用です:

- `channels.matrix.execApprovals.*`は、exec承認専用のネイティブDM/チャネルルーティングを制御します。
- プラグイン承認は、引き続き共有の同一チャット`/approve`と設定済みの`approvals.plugin`転送を使用します。
- Matrixは、承認者を安全に推論できる場合、プラグイン承認の認可のために`channels.matrix.dm.allowFrom`を再利用できますが、ネイティブなプラグイン承認DM/チャネルfanout経路は別途公開しません。

配信ルール:

- `target: "dm"`は、承認プロンプトを承認者DMへ送信します
- `target: "channel"`は、プロンプトを発生元のMatrixルームまたはDMへ送り返します
- `target: "both"`は、承認者DMと発生元のMatrixルームまたはDMの両方へ送信します

Matrix承認プロンプトは、主要な承認メッセージ上にリアクションショートカットを設定します:

- `✅` = 一度だけ許可
- `❌` = 拒否
- `♾️` = 有効なexecポリシーでその判断が許可されている場合に常に許可

承認者はそのメッセージにリアクションするか、フォールバックのスラッシュコマンド `/approve <id> allow-once`、`/approve <id> allow-always`、または`/approve <id> deny`を使えます。

承認または拒否できるのは解決済み承認者だけです。チャネル配信ではコマンドテキストが含まれるため、`channel`または`both`は信頼できるルームでのみ有効にしてください。

Matrix承認プロンプトは共有のコア承認プランナーを再利用します。Matrix固有のネイティブ面は、exec承認のためのトランスポートのみです: ルーム/DMルーティング、およびメッセージ送信/更新/削除の挙動です。

アカウントごとのoverride:

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

トップレベルの`channels.matrix`値は、アカウントがoverrideしない限り、名前付きアカウントのデフォルトとして機能します。
継承されたルームエントリは、`groups.<room>.account`（またはレガシーの`rooms.<room>.account`）で1つのMatrixアカウントにスコープできます。
`account`のないエントリはすべてのMatrixアカウントで共有されたままとなり、`account: "default"`付きのエントリは、デフォルトアカウントがトップレベルの`channels.matrix.*`に直接設定されている場合にも引き続き機能します。
共有認証デフォルトが部分的にあるだけでは、それ自体で別の暗黙のデフォルトアカウントは作成されません。OpenClawがトップレベルの`default`アカウントを合成するのは、そのデフォルトに新しい認証（`homeserver` + `accessToken`、または`homeserver` + `userId` + `password`）がある場合だけです。名前付きアカウントは、後でキャッシュ済み認証情報が認証要件を満たす場合、`homeserver` + `userId`からでも引き続き検出可能にできます。
Matrixにすでに名前付きアカウントがちょうど1つある場合、または`defaultAccount`が既存の名前付きアカウントキーを指している場合、単一アカウントからマルチアカウントへの修復/セットアップ昇格では、新しい`accounts.default`エントリを作成せず、そのアカウントが保持されます。その昇格したアカウントに移されるのはMatrix認証/bootstrapキーだけであり、共有配信ポリシーキーはトップレベルに残ります。
暗黙的なルーティング、プローブ、CLI操作で1つの名前付きMatrixアカウントを優先させたい場合は、`defaultAccount`を設定してください。
複数の名前付きアカウントを設定する場合は、暗黙的なアカウント選択に依存するCLIコマンドに対して`defaultAccount`を設定するか、`--account <id>`を渡してください。
1つのコマンドだけでその暗黙の選択を上書きしたい場合は、`openclaw matrix verify ...`と`openclaw matrix devices ...`に`--account <id>`を渡してください。

## プライベート/LAN homeserver

デフォルトでは、OpenClawはSSRF保護のため、プライベート/内部のMatrix homeserverをブロックします。
明示的にアカウント単位でオプトインしない限り、接続できません。

homeserverがlocalhost、LAN/Tailscale IP、または内部ホスト名で動作している場合は、
そのMatrixアカウントで`allowPrivateNetwork`を有効にしてください:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      allowPrivateNetwork: true,
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

このオプトインは、信頼されたプライベート/内部ターゲットのみを許可します。
`http://matrix.example.org:8008`のような公開クリアテキストhomeserverは引き続きブロックされます。可能な限り`https://`を推奨します。

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

名前付きアカウントは、`channels.matrix.accounts.<id>.proxy`でトップレベルのデフォルトをoverrideできます。
OpenClawは、実行時のMatrixトラフィックとアカウントステータスプローブの両方に同じプロキシ設定を使用します。

## ターゲット解決

OpenClawがルームまたはユーザーターゲットを求める場面では、Matrixは次のターゲット形式を受け付けます:

- ユーザー: `@user:server`, `user:@user:server`, または `matrix:user:@user:server`
- ルーム: `!room:server`, `room:!room:server`, または `matrix:room:!room:server`
- エイリアス: `#alias:server`, `channel:#alias:server`, または `matrix:channel:#alias:server`

ライブディレクトリ検索は、ログイン済みのMatrixアカウントを使用します:

- ユーザー検索は、そのhomeserver上のMatrix user directoryを照会します。
- ルーム検索では、明示的なルームIDとエイリアスを直接受け付け、その後そのアカウントの参加済みルーム名検索へフォールバックします。
- 参加済みルーム名検索はベストエフォートです。ルーム名をIDまたはエイリアスに解決できない場合、実行時の許可リスト解決では無視されます。

## 設定リファレンス

- `enabled`: チャネルを有効または無効にします。
- `name`: アカウントの任意ラベル。
- `defaultAccount`: 複数のMatrixアカウントが設定されているときの優先アカウントID。
- `homeserver`: homeserver URL。例: `https://matrix.example.org`。
- `allowPrivateNetwork`: このMatrixアカウントがプライベート/内部homeserverへ接続することを許可します。homeserverが`localhost`、LAN/Tailscale IP、または`matrix-synapse`のような内部ホストに解決される場合に有効化してください。
- `proxy`: Matrixトラフィック用の任意のHTTP(S)プロキシURL。名前付きアカウントは独自の`proxy`でトップレベルデフォルトをoverrideできます。
- `userId`: 完全なMatrix user ID。例: `@bot:example.org`。
- `accessToken`: トークンベース認証用アクセストークン。`channels.matrix.accessToken`および`channels.matrix.accounts.<id>.accessToken`では、env/file/exec providers全体でプレーンテキスト値とSecretRef値がサポートされます。[Secrets Management](/ja-JP/gateway/secrets)を参照してください。
- `password`: パスワードベースログイン用パスワード。プレーンテキスト値とSecretRef値がサポートされます。
- `deviceId`: 明示的なMatrix device ID。
- `deviceName`: パスワードログイン用デバイス表示名。
- `avatarUrl`: プロフィール同期と`set-profile`更新用に保存されるself-avatar URL。
- `initialSyncLimit`: 起動時同期イベント上限。
- `encryption`: E2EEを有効化します。
- `allowlistOnly`: DMとルームに対して許可リスト専用動作を強制します。
- `allowBots`: 他の設定済みOpenClaw Matrixアカウントからのメッセージを許可します（`true`または`"mentions"`）。
- `groupPolicy`: `open`、`allowlist`、または`disabled`。
- `contextVisibility`: 補足ルームコンテキストの可視性モード（`all`、`allowlist`、`allowlist_quote`）。
- `groupAllowFrom`: ルームトラフィック用のuser ID許可リスト。
- `groupAllowFrom`エントリは完全なMatrix user IDである必要があります。解決されない名前は実行時に無視されます。
- `historyLimit`: グループ履歴コンテキストに含めるルームメッセージ最大数。`messages.groupChat.historyLimit`にフォールバックします。無効にするには`0`を設定してください。
- `replyToMode`: `off`、`first`、または`all`。
- `markdown`: 送信Matrixテキスト用の任意のMarkdownレンダリング設定。
- `streaming`: `off`（デフォルト）、`partial`、`quiet`、`true`、または`false`。`partial`と`true`は通常のMatrixテキストメッセージでプレビュー優先ドラフト更新を有効にします。`quiet`はセルフホストのプッシュルール構成向けに通知しないプレビュー通知を使用します。
- `blockStreaming`: `true`は、ドラフトプレビューのストリーミングが有効な間、完了済みassistantブロックの個別進捗メッセージを有効にします。
- `threadReplies`: `off`、`inbound`、または`always`。
- `threadBindings`: スレッドバインドセッションルーティングとライフサイクルのチャネルごとのoverride。
- `startupVerification`: 起動時の自動自己検証要求モード（`if-unverified`、`off`）。
- `startupVerificationCooldownHours`: 起動時自動検証要求を再試行する前のクールダウン。
- `textChunkLimit`: 送信メッセージチャンクサイズ。
- `chunkMode`: `length`または`newline`。
- `responsePrefix`: 送信返信用の任意メッセージ接頭辞。
- `ackReaction`: このチャネル/アカウント用の任意のackリアクションoverride。
- `ackReactionScope`: 任意のackリアクションスコープoverride（`group-mentions`、`group-all`、`direct`、`all`、`none`、`off`）。
- `reactionNotifications`: 受信リアクション通知モード（`own`、`off`）。
- `mediaMaxMb`: Matrixメディア処理用のMB単位メディアサイズ上限。送信と受信メディア処理の両方に適用されます。
- `autoJoin`: 招待の自動参加ポリシー（`always`、`allowlist`、`off`）。デフォルト: `off`。
- `autoJoinAllowlist`: `autoJoin`が`allowlist`のときに許可されるルーム/エイリアス。エイリアスエントリは招待処理中にルームIDへ解決されます。OpenClawは招待されたルームが主張するエイリアス状態を信頼しません。
- `dm`: DMポリシーブロック（`enabled`、`policy`、`allowFrom`、`sessionScope`、`threadReplies`）。
- `dm.allowFrom`エントリは、ライブディレクトリ検索で解決済みでない限り、完全なMatrix user IDである必要があります。
- `dm.sessionScope`: `per-user`（デフォルト）または`per-room`。相手が同じでも各Matrix DMルームで別個のコンテキストを維持したい場合は`per-room`を使用してください。
- `dm.threadReplies`: DM専用スレッドポリシーoverride（`off`、`inbound`、`always`）。DMにおける返信配置とセッション分離の両方について、トップレベルの`threadReplies`設定を上書きします。
- `execApprovals`: Matrixネイティブexec承認配信（`enabled`、`approvers`、`target`、`agentFilter`、`sessionFilter`）。
- `execApprovals.approvers`: exec要求を承認できるMatrix user ID。`dm.allowFrom`がすでに承認者を識別している場合は任意です。
- `execApprovals.target`: `dm | channel | both`（デフォルト: `dm`）。
- `accounts`: 名前付きアカウントごとのoverride。トップレベルの`channels.matrix`値がこれらのエントリのデフォルトとして機能します。
- `groups`: ルームごとのポリシーマップ。ルームIDまたはエイリアスを推奨します。解決されないルーム名は実行時に無視されます。解決後のセッション/グループIDには安定したルームIDが使用され、人間向けラベルは引き続きルーム名から取得されます。
- `groups.<room>.account`: マルチアカウント構成で、継承された1つのルームエントリを特定のMatrixアカウントに限定します。
- `groups.<room>.allowBots`: 設定済みボット送信者に対するルームレベルoverride（`true`または`"mentions"`）。
- `groups.<room>.users`: ルームごとの送信者許可リスト。
- `groups.<room>.tools`: ルームごとのtool許可/拒否override。
- `groups.<room>.autoReply`: ルームレベルのメンションゲーティングoverride。`true`はそのルームのメンション要件を無効にし、`false`は再び有効にします。
- `groups.<room>.skills`: 任意のルームレベルskill filter。
- `groups.<room>.systemPrompt`: 任意のルームレベルsystem prompt snippet。
- `rooms`: `groups`のレガシーエイリアス。
- `actions`: アクションごとのtool gating（`messages`、`reactions`、`pins`、`profile`、`memberInfo`、`channelInfo`、`verification`）。

## 関連

- [チャネル概要](/ja-JP/channels) — サポートされているすべてのチャネル
- [ペアリング](/ja-JP/channels/pairing) — DM認証とペアリングフロー
- [グループ](/ja-JP/channels/groups) — グループチャット動作とメンションゲーティング
- [チャネルルーティング](/ja-JP/channels/channel-routing) — メッセージのセッションルーティング
- [セキュリティ](/ja-JP/gateway/security) — アクセスモデルとハードニング
