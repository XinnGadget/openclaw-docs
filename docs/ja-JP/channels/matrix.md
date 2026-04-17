---
read_when:
    - OpenClawでのMatrixのセットアップ
    - MatrixのE2EEと検証の設定
summary: Matrixのサポート状況、セットアップ、および設定例
title: Matrix
x-i18n:
    generated_at: "2026-04-15T19:41:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: bd730bb9d0c8a548ee48b20931b3222e9aa1e6e95f1390b0c236645e03f3576d
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

MatrixはOpenClaw用のバンドルされたchannel Pluginです。
公式の`matrix-js-sdk`を使用し、DM、ルーム、スレッド、メディア、リアクション、投票、位置情報、E2EEをサポートします。

## バンドルされたPlugin

Matrixは現在のOpenClawリリースではバンドルされたPluginとして同梱されているため、通常の
パッケージ済みビルドでは別途インストールは不要です。

古いビルド、またはMatrixを除外したカスタムインストールを使用している場合は、手動で
インストールしてください。

npmからインストール:

```bash
openclaw plugins install @openclaw/matrix
```

ローカルチェックアウトからインストール:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

Pluginの動作とインストールルールについては、[Plugins](/ja-JP/tools/plugin)を参照してください。

## セットアップ

1. Matrix Pluginが利用可能であることを確認します。
   - 現在のパッケージ済みOpenClawリリースには、すでに同梱されています。
   - 古い/カスタムインストールでは、上記のコマンドで手動追加できます。
2. ご利用のhomeserverでMatrixアカウントを作成します。
3. `channels.matrix`を次のいずれかで設定します。
   - `homeserver` + `accessToken`、または
   - `homeserver` + `userId` + `password`。
4. Gatewayを再起動します。
5. ボットとDMを開始するか、ルームに招待します。
   - 新しいMatrix招待は、`channels.matrix.autoJoin`で許可されている場合にのみ機能します。

対話型セットアップのパス:

```bash
openclaw channels add
openclaw configure --section channels
```

Matrixウィザードでは、次の項目を尋ねます。

- homeserver URL
- 認証方法: アクセストークンまたはパスワード
- ユーザーID（パスワード認証のみ）
- オプションのデバイス名
- E2EEを有効にするかどうか
- ルームアクセスと招待自動参加を設定するかどうか

主なウィザードの動作:

- Matrix認証の環境変数がすでに存在し、そのアカウントの認証がまだconfigに保存されていない場合、ウィザードは認証を環境変数に保持するためのenvショートカットを提示します。
- アカウント名はアカウントIDに正規化されます。たとえば、`Ops Bot`は`ops-bot`になります。
- DM allowlistエントリは`@user:server`をそのまま受け付けます。表示名が機能するのは、ライブディレクトリ検索で1件の完全一致が見つかった場合のみです。
- ルーム allowlistエントリはルームIDとエイリアスをそのまま受け付けます。`!room:server`または`#alias:server`を推奨します。未解決の名前は、allowlist解決時にランタイムで無視されます。
- 招待自動参加のallowlistモードでは、安定した招待ターゲットのみを使用してください: `!roomId:server`、`#alias:server`、または`*`。プレーンなルーム名は拒否されます。
- 保存前にルーム名を解決するには、`openclaw channels resolve --channel matrix "Project Room"`を使用します。

<Warning>
`channels.matrix.autoJoin`のデフォルトは`off`です。

これを未設定のままにすると、ボットは招待されたルームや新しいDM形式の招待に参加しないため、先に手動で参加しない限り、新しいグループや招待されたDMには表示されません。

受け付ける招待を制限したい場合は、`autoJoinAllowlist`と一緒に`autoJoin: "allowlist"`を設定し、すべての招待に参加させたい場合は`autoJoin: "always"`を設定してください。

`allowlist`モードでは、`autoJoinAllowlist`は`!roomId:server`、`#alias:server`、または`*`のみ受け付けます。
</Warning>

allowlistの例:

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
デフォルトアカウントでは`credentials.json`を使用し、名前付きアカウントでは`credentials-<account>.json`を使用します。
そこにキャッシュされた認証情報が存在する場合、現在の認証がconfigに直接設定されていなくても、OpenClawはセットアップ、doctor、channel-status検出のためにMatrixが設定済みであると見なします。

環境変数の対応版（configキーが設定されていない場合に使用されます）:

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

デフォルト以外のアカウントでは、アカウントスコープ付きの環境変数を使用します。

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

アカウント`ops`の例:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

正規化されたアカウントID `ops-bot`では、次を使用します。

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

MatrixはアカウントID内の句読点をエスケープし、スコープ付き環境変数の衝突を防ぎます。
たとえば、`-`は`_X2D_`になるため、`ops-prod`は`MATRIX_OPS_X2D_PROD_*`に対応します。

対話型ウィザードがenv-varショートカットを提示するのは、それらの認証環境変数がすでに存在し、選択したアカウントにMatrix認証がまだconfigへ保存されていない場合のみです。

## 設定例

これは、DMペアリング、ルームallowlist、E2EE有効化を含む実用的なベースライン設定です。

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

`autoJoin`は、DM形式の招待を含むすべてのMatrix招待に適用されます。OpenClawは招待時点で
招待されたルームがDMかグループかを確実に分類できないため、すべての招待はまず`autoJoin`
を通ります。`dm.policy`は、ボットが参加してルームがDMとして分類された後に適用されます。

## ストリーミングプレビュー

Matrixの返信ストリーミングはオプトインです。

OpenClawに単一のライブプレビュー返信を送信させ、モデルがテキストを生成している間はその
プレビューをその場で編集し、返信が完了したら確定させたい場合は、`channels.matrix.streaming`
を`"partial"`に設定します。

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"`がデフォルトです。OpenClawは最終返信を待ってから1回送信します。
- `streaming: "partial"`は、現在のassistantブロック用に通常のMatrixテキストメッセージを使った編集可能なプレビューを1つ作成します。これにより、Matrixの従来の「プレビュー先行」通知動作が維持されるため、標準クライアントでは完成したブロックではなく、最初のストリーミングプレビューテキストで通知される場合があります。
- `streaming: "quiet"`は、現在のassistantブロック用に編集可能な静かなプレビュー通知を1つ作成します。これを使用するのは、確定したプレビュー編集に対する受信者のプッシュルールも設定する場合だけにしてください。
- `blockStreaming: true`は、個別のMatrix進行状況メッセージを有効にします。プレビューストリーミングが有効な場合、Matrixは現在のブロックのライブ下書きを保持し、完了したブロックを別メッセージとして保持します。
- プレビューストリーミングがオンで`blockStreaming`がオフの場合、Matrixはライブ下書きをその場で編集し、ブロックまたはターンの完了時にその同じイベントを確定します。
- プレビューが1つのMatrixイベントに収まらなくなった場合、OpenClawはプレビューストリーミングを停止し、通常の最終配信にフォールバックします。
- メディア返信は引き続き通常どおり添付ファイルを送信します。古いプレビューを安全に再利用できなくなった場合、OpenClawは最終的なメディア返信を送る前にそのプレビューをリダクトします。
- プレビュー編集には追加のMatrix API呼び出しコストがかかります。最も保守的なレート制限動作を求める場合は、ストリーミングをオフのままにしてください。

`blockStreaming`だけでは下書きプレビューは有効になりません。
プレビュー編集には`streaming: "partial"`または`streaming: "quiet"`を使用し、完了したassistantブロックも個別の進行状況メッセージとして表示したい場合にのみ、さらに`blockStreaming: true`を追加してください。

カスタムプッシュルールなしで標準のMatrix通知が必要な場合は、プレビュー先行動作のために`streaming: "partial"`を使用するか、最終配信のみのために`streaming`をオフのままにしてください。`streaming: "off"`の場合:

- `blockStreaming: true`は、各完了ブロックを通常の通知付きMatrixメッセージとして送信します。
- `blockStreaming: false`は、最終的に完成した返信のみを通常の通知付きMatrixメッセージとして送信します。

### セルフホスト環境で、確定した静かなプレビュー用のプッシュルールを設定する

独自のMatrixインフラを運用していて、ブロックまたは最終返信が完了したときにのみ静かなプレビューで通知したい場合は、`streaming: "quiet"`を設定し、確定したプレビュー編集用のユーザーごとのプッシュルールを追加します。

これは通常、homeserver全体の設定変更ではなく、受信ユーザー側の設定です。

開始前の簡単な対応関係:

- recipient user = 通知を受け取る人
- bot user = 返信を送信するOpenClaw Matrixアカウント
- 以下のAPI呼び出しではrecipient userのアクセストークンを使用します
- プッシュルール内の`sender`はbot userの完全なMXIDに一致させます

1. OpenClawが静かなプレビューを使うように設定します。

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. recipientアカウントがすでに通常のMatrixプッシュ通知を受け取っていることを確認します。静かなプレビュー
   ルールが機能するのは、そのユーザーに有効なpusher/デバイスがすでにある場合のみです。

3. recipient userのアクセストークンを取得します。
   - botのトークンではなく、受信側ユーザーのトークンを使用してください。
   - 既存のクライアントセッショントークンを再利用するのが通常は最も簡単です。
   - 新しいトークンを発行する必要がある場合は、標準のMatrix Client-Server APIからログインできます。

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

4. recipientアカウントにすでにpusherがあることを確認します。

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

これで有効なpusher/デバイスが返らない場合は、以下の
OpenClawルールを追加する前に、まず通常のMatrix通知を修正してください。

OpenClawは、確定したテキストのみのプレビュー編集を次のようにマークします。

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. これらの通知を受け取る必要がある各recipientアカウントに対して、overrideプッシュルールを作成します。

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

コマンド実行前に次の値を置き換えてください。

- `https://matrix.example.org`: ご利用のhomeserverのベースURL
- `$USER_ACCESS_TOKEN`: 受信側ユーザーのアクセストークン
- `openclaw-finalized-preview-botname`: この受信側ユーザーに対するこのbot固有のルールID
- `@bot:example.org`: 受信側ユーザーのMXIDではなく、OpenClaw Matrix botのMXID

複数bot構成で重要な点:

- プッシュルールは`ruleId`をキーにしています。同じルールIDに対して`PUT`を再実行すると、その1つのルールが更新されます。
- 1人の受信ユーザーが複数のOpenClaw Matrix botアカウントに対して通知を受け取る必要がある場合は、各送信者一致ごとに一意のルールIDを使って、botごとに1つのルールを作成してください。
- 単純なパターンは`openclaw-finalized-preview-<botname>`です。たとえば、`openclaw-finalized-preview-ops`や`openclaw-finalized-preview-support`です。

このルールはイベント送信者に対して評価されます。

- 受信ユーザーのトークンで認証する
- `sender`をOpenClaw botのMXIDに一致させる

6. ルールが存在することを確認します。

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. ストリーミング返信をテストします。quietモードでは、ルームに静かな下書きプレビューが表示され、
   ブロックまたはターンが完了すると、最終的なインプレース編集で1回通知されるはずです。

後でルールを削除する必要がある場合は、受信ユーザーのトークンを使って同じルールIDを削除してください。

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

注意:

- ルールはbotのトークンではなく、受信ユーザーのアクセストークンで作成してください。
- 新しいユーザー定義の`override`ルールは、デフォルトの抑制ルールより前に挿入されるため、追加の順序パラメーターは不要です。
- これは、OpenClawが安全にその場で確定できるテキストのみのプレビュー編集にのみ影響します。メディアへのフォールバックや古いプレビューへのフォールバックでは、通常のMatrix配信が引き続き使われます。
- `GET /_matrix/client/v3/pushers`でpusherが表示されない場合、そのユーザーはまだこのアカウント/デバイスで有効なMatrixプッシュ配信を利用できていません。

#### Synapse

Synapseでは、通常は上記のセットアップだけで十分です。

- 確定したOpenClawプレビュー通知のために、特別な`homeserver.yaml`変更は不要です。
- Synapseのデプロイですでに通常のMatrixプッシュ通知が送信されている場合、主なセットアップ手順は上記のユーザートークン + `pushrules`呼び出しです。
- Synapseをリバースプロキシまたはworkerの背後で実行している場合は、`/_matrix/client/.../pushrules/`が正しくSynapseに到達することを確認してください。
- Synapse workersを使用している場合は、pusherが正常であることを確認してください。プッシュ配信はメインプロセスまたは`synapse.app.pusher` / 設定済みのpusher workerによって処理されます。

#### Tuwunel

Tuwunelでは、上記と同じセットアップフローとpush-rule API呼び出しを使用してください。

- 確定したプレビューマーカー自体に対して、Tuwunel固有の設定は不要です。
- そのユーザーに対して通常のMatrix通知がすでに機能している場合、主なセットアップ手順は上記のユーザートークン + `pushrules`呼び出しです。
- ユーザーが別のデバイスでアクティブな間に通知が消えるように見える場合は、`suppress_push_when_active`が有効になっているか確認してください。Tuwunelでは2025年9月12日のTuwunel 1.4.2でこのオプションが追加されており、1つのデバイスがアクティブな間、他のデバイスへのプッシュを意図的に抑制することがあります。

## bot同士のルーム

デフォルトでは、他の設定済みOpenClaw MatrixアカウントからのMatrixメッセージは無視されます。

意図的にagent間のMatrixトラフィックを許可したい場合は、`allowBots`を使用します。

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

- `allowBots: true`は、許可されたルームとDMにおいて、他の設定済みMatrix botアカウントからのメッセージを受け付けます。
- `allowBots: "mentions"`は、ルーム内でそのメッセージがこのbotに明示的にメンションしている場合にのみ受け付けます。DMは引き続き許可されます。
- `groups.<room>.allowBots`は、1つのルームに対してアカウントレベル設定を上書きします。
- OpenClawは自己返信ループを避けるため、同じMatrix user IDからのメッセージは引き続き無視します。
- Matrixはここでネイティブのbotフラグを公開していません。OpenClawは「botが作成した」を「このOpenClaw gateway上の別の設定済みMatrixアカウントが送信した」と見なします。

共有ルームでbot同士のトラフィックを有効にする場合は、厳格なルームallowlistとメンション必須設定を使用してください。

## 暗号化と検証

暗号化された（E2EE）ルームでは、送信画像イベントは`thumbnail_file`を使用するため、画像プレビューは完全な添付ファイルとともに暗号化されます。暗号化されていないルームでは、引き続きプレーンな`thumbnail_url`を使用します。設定は不要で、PluginがE2EE状態を自動検出します。

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

詳細な状態（完全な診断情報）:

```bash
openclaw matrix verify status --verbose
```

保存されているリカバリーキーを機械可読出力に含める:

```bash
openclaw matrix verify status --include-recovery-key --json
```

クロス署名と検証状態をブートストラップする:

```bash
openclaw matrix verify bootstrap
```

詳細なブートストラップ診断情報:

```bash
openclaw matrix verify bootstrap --verbose
```

ブートストラップ前に新しいクロス署名IDリセットを強制する:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

リカバリーキーでこのデバイスを検証する:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

詳細なデバイス検証情報:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

ルームキーのバックアップ状態を確認する:

```bash
openclaw matrix verify backup status
```

詳細なバックアップ状態診断情報:

```bash
openclaw matrix verify backup status --verbose
```

サーバーバックアップからルームキーを復元する:

```bash
openclaw matrix verify backup restore
```

詳細な復元診断情報:

```bash
openclaw matrix verify backup restore --verbose
```

現在のサーバーバックアップを削除し、新しいバックアップベースラインを作成します。保存されている
バックアップキーを正常に読み込めない場合、このリセットによって秘密ストレージも再作成され、
今後のコールドスタートで新しいバックアップキーを読み込めるようになることがあります。

```bash
openclaw matrix verify backup reset --yes
```

すべての`verify`コマンドはデフォルトで簡潔です（内部SDKログもquietを含む）で、詳細な診断情報は`--verbose`を付けた場合にのみ表示されます。
スクリプトで使用する場合は、完全な機械可読出力のために`--json`を使用してください。

複数アカウント構成では、Matrix CLIコマンドは`--account <id>`を渡さない限り暗黙のMatrixデフォルトアカウントを使用します。
複数の名前付きアカウントを設定している場合は、まず`channels.matrix.defaultAccount`を設定してください。そうしないと、これらの暗黙のCLI操作は停止して、明示的にアカウント選択を求めます。
検証またはデバイス操作を明示的に名前付きアカウントに向けたい場合は、常に`--account`を使用してください。

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

暗号化が無効、または名前付きアカウントで利用できない場合、Matrixの警告と検証エラーはそのアカウントのconfigキーを指します。たとえば`channels.matrix.accounts.assistant.encryption`です。

### 「verified」の意味

OpenClawは、このMatrixデバイスがあなた自身のクロス署名IDによって検証されている場合にのみ、検証済みと見なします。
実際には、`openclaw matrix verify status --verbose`は次の3つの信頼シグナルを表示します。

- `Locally trusted`: このデバイスは現在のクライアントでのみ信頼されています
- `Cross-signing verified`: SDKが、このデバイスがクロス署名によって検証済みであると報告しています
- `Signed by owner`: このデバイスは、あなた自身のself-signingキーによって署名されています

`Verified by owner`が`yes`になるのは、クロス署名検証またはowner署名が存在する場合のみです。
ローカル信頼だけでは、OpenClawはこのデバイスを完全に検証済みとは見なしません。

### ブートストラップが行うこと

`openclaw matrix verify bootstrap`は、暗号化されたMatrixアカウントの修復とセットアップのためのコマンドです。
これにより、次のすべてが順番に実行されます。

- 可能であれば既存のリカバリーキーを再利用して、秘密ストレージをブートストラップする
- クロス署名をブートストラップし、不足している公開クロス署名キーをアップロードする
- 現在のデバイスにマークを付けてクロス署名することを試みる
- サーバー側の新しいルームキーバックアップを、まだ存在しない場合に作成する

homeserverがクロス署名キーのアップロードに対話的認証を要求する場合、OpenClawはまず認証なしでアップロードを試し、その後`m.login.dummy`、さらに`channels.matrix.password`が設定されている場合は`m.login.password`を試します。

`--force-reset-cross-signing`は、現在のクロス署名IDを破棄して新しいものを作成したい場合にのみ使用してください。

現在のルームキーバックアップを意図的に破棄し、将来のメッセージ用に新しい
バックアップベースラインを開始したい場合は、`openclaw matrix verify backup reset --yes`を使用してください。
これは、復元不可能な古い暗号化履歴が引き続き利用不能のままであること、および現在のバックアップ
シークレットを安全に読み込めない場合にOpenClawが秘密ストレージを再作成する可能性があることを受け入れる場合にのみ実行してください。

### 新しいバックアップベースライン

将来の暗号化メッセージを引き続き利用可能にしつつ、復元不可能な古い履歴を失うことを受け入れる場合は、次のコマンドを順に実行してください。

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

名前付きMatrixアカウントを明示的に対象にしたい場合は、各コマンドに`--account <id>`を追加してください。

### 起動時の動作

`encryption: true`の場合、Matrixは`startupVerification`のデフォルトを`"if-unverified"`にします。
起動時にこのデバイスがまだ未検証である場合、Matrixは別のMatrixクライアントで自己検証を要求し、
すでに保留中の要求がある間は重複要求をスキップし、再起動後の再試行前にローカルのクールダウンを適用します。
失敗した要求試行は、成功した要求作成よりもデフォルトで早く再試行されます。
自動起動時要求を無効にするには`startupVerification: "off"`を設定し、再試行間隔を短くまたは長くしたい場合は`startupVerificationCooldownHours`
を調整してください。

起動時には、保守的なcryptoブートストラップ処理も自動的に実行されます。
この処理はまず現在の秘密ストレージとクロス署名IDの再利用を試み、明示的なブートストラップ修復フローを実行しない限り、クロス署名のリセットを避けます。

それでも起動時に壊れたブートストラップ状態が見つかった場合、OpenClawは`channels.matrix.password`が設定されていなくても、保護付き修復パスを試みることがあります。
その修復でhomeserverがパスワードベースのUIAを要求する場合、OpenClawは警告をログに出し、botを中止するのではなく起動を非致命のまま維持します。
現在のデバイスがすでにowner署名済みである場合、OpenClawはそれを自動的にリセットせず、そのIDを保持します。

完全なアップグレードフロー、制限、復旧コマンド、一般的な移行メッセージについては、[Matrix migration](/ja-JP/install/migrating-matrix)を参照してください。

### 検証通知

Matrixは、厳格なDM検証ルームに検証ライフサイクル通知を`m.notice`メッセージとして直接投稿します。
これには次が含まれます。

- 検証要求通知
- 検証準備完了通知（明示的な「絵文字で検証」ガイダンス付き）
- 検証開始および完了通知
- 利用可能な場合のSAS詳細（絵文字と10進数）

別のMatrixクライアントからの受信検証要求は、OpenClawが追跡して自動受諾します。
自己検証フローでは、絵文字検証が利用可能になると、OpenClawはSASフローも自動的に開始し、自身の側を確認します。
別のMatrixユーザー/デバイスからの検証要求については、OpenClawは要求を自動受諾し、その後SASフローが通常どおり進行するのを待ちます。
検証を完了するには、引き続きMatrixクライアントで絵文字または10進SASを比較し、そこで「一致する」を確認する必要があります。

OpenClawは、自己開始された重複フローを無条件に自動受諾しません。自己検証要求がすでに保留中の場合、起動時には新しい要求の作成をスキップします。

検証プロトコル/システム通知はagentチャットパイプラインには転送されないため、`NO_REPLY`は発生しません。

### デバイス管理

古いOpenClaw管理のMatrixデバイスがアカウント上に蓄積し、暗号化ルームの信頼性を把握しづらくなることがあります。
次のコマンドで一覧表示します。

```bash
openclaw matrix devices list
```

古いOpenClaw管理デバイスを削除するには:

```bash
openclaw matrix devices prune-stale
```

### Cryptoストア

MatrixのE2EEは、Node上で公式の`matrix-js-sdk` Rust cryptoパスを使用し、IndexedDBのshimとして`fake-indexeddb`を使用します。Crypto状態はスナップショットファイル（`crypto-idb-snapshot.json`）に永続化され、起動時に復元されます。スナップショットファイルは機密性の高いランタイム状態であり、制限されたファイル権限で保存されます。

暗号化されたランタイム状態は、アカウントごと・ユーザートークンハッシュごとのルート配下で
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`に保存されます。
このディレクトリには、syncストア（`bot-storage.json`）、cryptoストア（`crypto/`）、
リカバリーキーファイル（`recovery-key.json`）、IndexedDBスナップショット（`crypto-idb-snapshot.json`）、
スレッドバインディング（`thread-bindings.json`）、起動時検証状態（`startup-verification.json`）が含まれます。
トークンが変更されてもアカウントIDが同じままであれば、OpenClawはそのアカウント/homeserver/userタプルに対して最適な既存ルートを再利用するため、以前のsync状態、crypto状態、スレッドバインディング、
起動時検証状態は引き続き利用できます。

## プロファイル管理

選択したアカウントのMatrixセルフプロファイルを更新するには、次を使用します。

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

名前付きMatrixアカウントを明示的に対象にしたい場合は、`--account <id>`を追加してください。

Matrixは`mxc://`アバターURLをそのまま受け付けます。`http://`または`https://`のアバターURLを渡した場合、OpenClawはまずそれをMatrixにアップロードし、解決後の`mxc://` URLを`channels.matrix.avatarUrl`（または選択したアカウントの上書き先）へ保存します。

## スレッド

Matrixは、自動返信とmessage-tool送信の両方でネイティブのMatrixスレッドをサポートします。

- `dm.sessionScope: "per-user"`（デフォルト）は、Matrix DMルーティングを送信者単位で維持するため、複数のDMルームが同じ相手に解決される場合は1つのセッションを共有できます。
- `dm.sessionScope: "per-room"`は、通常のDM認証とallowlistチェックを維持しながら、各Matrix DMルームを独自のセッションキーに分離します。
- 明示的なMatrix会話バインディングは引き続き`dm.sessionScope`より優先されるため、バインドされたルームとスレッドは選択された対象セッションを維持します。
- `threadReplies: "off"`は返信をトップレベルに保ち、受信したスレッド付きメッセージを親セッション上で維持します。
- `threadReplies: "inbound"`は、受信メッセージがすでにそのスレッド内にある場合にのみ、そのスレッド内で返信します。
- `threadReplies: "always"`は、ルーム返信をトリガー元メッセージをルートとするスレッド内に維持し、その会話を最初のトリガー元メッセージに一致するスレッドスコープのセッションへルーティングします。
- `dm.threadReplies`は、DMに対してのみトップレベル設定を上書きします。たとえば、ルームスレッドは分離したまま、DMはフラットに保てます。
- 受信したスレッド付きメッセージには、追加のagentコンテキストとしてスレッドのルートメッセージが含まれます。
- Message-tool送信は、明示的な`threadId`が指定されていない限り、対象が同じルーム、または同じDMユーザー対象であれば、現在のMatrixスレッドを自動的に継承します。
- 同一セッションのDMユーザー対象の再利用は、現在のセッションメタデータが同じMatrixアカウント上の同一DM相手であることを証明している場合にのみ有効になります。それ以外の場合、OpenClawは通常のユーザースコープルーティングにフォールバックします。
- OpenClawが、あるMatrix DMルームが同じ共有Matrix DMセッション上の別のDMルームと衝突していることを検出すると、スレッドバインディングが有効で`dm.sessionScope`ヒントがある場合、そのルームに`/focus`エスケープハッチ付きの1回限りの`m.notice`を投稿します。
- Matrixはランタイムスレッドバインディングをサポートします。`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`、およびスレッドにバインドされた`/acp spawn`は、MatrixルームとDMで機能します。
- トップレベルのMatrixルーム/DMでの`/focus`は、`threadBindings.spawnSubagentSessions=true`のとき、新しいMatrixスレッドを作成して対象セッションにバインドします。
- 既存のMatrixスレッド内で`/focus`または`/acp spawn --thread here`を実行すると、代わりにその現在のスレッドがバインドされます。

## ACP会話バインディング

Matrixルーム、DM、既存のMatrixスレッドは、チャット画面を変えることなく永続的なACPワークスペースにできます。

高速なオペレーターフロー:

- 使い続けたいMatrix DM、ルーム、または既存スレッドの中で`/acp spawn codex --bind here`を実行します。
- トップレベルのMatrix DMまたはルームでは、現在のDM/ルームがチャット画面のまま維持され、以後のメッセージは生成されたACPセッションにルーティングされます。
- 既存のMatrixスレッド内では、`--bind here`がその現在のスレッドをその場でバインドします。
- `/new`と`/reset`は、同じバインド済みACPセッションをその場でリセットします。
- `/acp close`はACPセッションを閉じて、バインディングを削除します。

注意:

- `--bind here`は子のMatrixスレッドを作成しません。
- `threadBindings.spawnAcpSessions`が必要になるのは、OpenClawが子のMatrixスレッドを作成またはバインドする必要がある`/acp spawn --thread auto|here`の場合のみです。

### スレッドバインディング設定

Matrixは`session.threadBindings`からグローバルデフォルトを継承し、channelごとの上書きもサポートします。

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrixのスレッドバインドspawnフラグはオプトインです。

- トップレベルの`/focus`で新しいMatrixスレッドを作成してバインドできるようにするには、`threadBindings.spawnSubagentSessions: true`を設定します。
- `/acp spawn --thread auto|here`でACPセッションをMatrixスレッドにバインドできるようにするには、`threadBindings.spawnAcpSessions: true`を設定します。

## リアクション

Matrixは、送信リアクション操作、受信リアクション通知、受信ackリアクションをサポートします。

- 送信リアクションtoolingは`channels["matrix"].actions.reactions`で制御されます。
- `react`は特定のMatrixイベントにリアクションを追加します。
- `reactions`は特定のMatrixイベントの現在のリアクション要約を一覧表示します。
- `emoji=""`は、そのイベントに対するbotアカウント自身のリアクションを削除します。
- `remove: true`は、botアカウントから指定された絵文字リアクションのみを削除します。

ackリアクションは、標準のOpenClaw解決順序を使用します。

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- agent identityの絵文字フォールバック

ackリアクションスコープは次の順で解決されます。

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

リアクション通知モードは次の順で解決されます。

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- デフォルト: `own`

動作:

- `reactionNotifications: "own"`は、botが作成したMatrixメッセージを対象とする追加済み`m.reaction`イベントを転送します。
- `reactionNotifications: "off"`は、リアクションシステムイベントを無効にします。
- リアクション削除は、Matrixではそれらが独立した`m.reaction`削除ではなくredactionとして表現されるため、システムイベントには合成されません。

## 履歴コンテキスト

- `channels.matrix.historyLimit`は、Matrixルームメッセージがagentをトリガーしたときに`InboundHistory`として含める最近のルームメッセージ数を制御します。`messages.groupChat.historyLimit`にフォールバックし、両方とも未設定なら実効デフォルトは`0`です。無効にするには`0`を設定します。
- Matrixルーム履歴はルームのみです。DMは通常のセッション履歴を引き続き使用します。
- Matrixルーム履歴はpending-onlyです。OpenClawは、まだ返信をトリガーしていないルームメッセージをバッファし、メンションやその他のトリガーが到着した時点でそのウィンドウをスナップショットします。
- 現在のトリガーメッセージは`InboundHistory`には含まれず、そのターンのメインの受信本文に残ります。
- 同じMatrixイベントの再試行では、新しいルームメッセージへずれていくのではなく、元の履歴スナップショットを再利用します。

## コンテキスト可視性

Matrixは、取得した返信テキスト、スレッドルート、pending履歴などの補足ルームコンテキストに対して、共有の`contextVisibility`制御をサポートします。

- `contextVisibility: "all"`がデフォルトです。補足コンテキストは受信したまま保持されます。
- `contextVisibility: "allowlist"`は、補足コンテキストを、アクティブなルーム/ユーザーallowlistチェックで許可された送信者に絞り込みます。
- `contextVisibility: "allowlist_quote"`は`allowlist`と同様に動作しますが、明示的に引用された1件の返信は保持します。

この設定は補足コンテキストの可視性に影響するものであり、受信メッセージ自体が返信をトリガーできるかどうかには影響しません。
トリガーの認可は引き続き`groupPolicy`、`groups`、`groupAllowFrom`、およびDMポリシー設定から行われます。

## DMとルームのポリシー

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

Matrix DMのpairing例:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

未承認のMatrixユーザーが承認前にメッセージを送り続けた場合、OpenClawは同じ保留中のpairingコードを再利用し、新しいコードを発行する代わりに、短いクールダウン後に再度リマインダー返信を送ることがあります。

共有のDM pairingフローと保存レイアウトについては、[Pairing](/ja-JP/channels/pairing)を参照してください。

## 直接ルーム修復

ダイレクトメッセージ状態の同期が崩れると、OpenClawはライブのDMではなく古い1対1ルームを指す古い`m.direct`マッピングを持つことがあります。相手に対する現在のマッピングを確認するには、次を使用します。

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

修復するには:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

修復フロー:

- すでに`m.direct`にマッピングされている厳密な1:1 DMを優先します
- それがなければ、そのユーザーとの現在参加中の厳密な1:1 DMにフォールバックします
- 正常なDMが存在しない場合は、新しいダイレクトルームを作成して`m.direct`を書き換えます

修復フローは古いルームを自動削除しません。正常なDMを選択してマッピングを更新するだけで、新しいMatrix送信、検証通知、その他のダイレクトメッセージフローが再び正しいルームを対象にするようになります。

## Exec承認

Matrixは、Matrixアカウント用のネイティブ承認クライアントとして動作できます。ネイティブの
DM/channelルーティング設定は、引き続きexec承認設定の下にあります。

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers`（オプション。`channels.matrix.dm.allowFrom`にフォールバック）
- `channels.matrix.execApprovals.target`（`dm` | `channel` | `both`、デフォルト: `dm`）
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

承認者は`@owner:example.org`のようなMatrix user IDである必要があります。Matrixは、`enabled`が未設定または`"auto"`で、少なくとも1人の承認者を解決できる場合、自動的にネイティブ承認を有効にします。Exec承認はまず`execApprovals.approvers`を使用し、`channels.matrix.dm.allowFrom`にフォールバックできます。Plugin承認は`channels.matrix.dm.allowFrom`を通じて認可されます。Matrixをネイティブ承認クライアントとして明示的に無効にするには、`enabled: false`を設定してください。それ以外の場合、承認要求は他の設定済み承認ルートまたは承認フォールバックポリシーにフォールバックします。

Matrixネイティブルーティングは両方の承認種別をサポートします。

- `channels.matrix.execApprovals.*`は、Matrix承認プロンプトのネイティブDM/channelファンアウトモードを制御します。
- Exec承認は`execApprovals.approvers`または`channels.matrix.dm.allowFrom`からexec承認者セットを使用します。
- Plugin承認は`channels.matrix.dm.allowFrom`からMatrix DM allowlistを使用します。
- Matrixリアクションショートカットとメッセージ更新は、exec承認とPlugin承認の両方に適用されます。

配信ルール:

- `target: "dm"`は承認プロンプトを承認者DMへ送信します
- `target: "channel"`はプロンプトを元のMatrixルームまたはDMへ送り返します
- `target: "both"`は承認者DMと元のMatrixルームまたはDMの両方へ送信します

Matrix承認プロンプトは、主要な承認メッセージにリアクションショートカットを設定します。

- `✅` = 1回だけ許可
- `❌` = 拒否
- `♾️` = 実効execポリシーでその判断が許可されている場合、常に許可

承認者はそのメッセージにリアクションするか、フォールバックのスラッシュコマンド `/approve <id> allow-once`、`/approve <id> allow-always`、または`/approve <id> deny`を使用できます。

解決済みの承認者のみが承認または拒否できます。Exec承認では、channel配信にコマンドテキストが含まれるため、`channel`または`both`は信頼できるルームでのみ有効にしてください。

アカウントごとの上書き:

- `channels.matrix.accounts.<account>.execApprovals`

関連ドキュメント: [Exec approvals](/ja-JP/tools/exec-approvals)

## 複数アカウント

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
継承されたルームエントリを1つのMatrixアカウントに限定するには、`groups.<room>.account`を使用できます。
`account`なしのエントリはすべてのMatrixアカウントで共有されたままとなり、`account: "default"`が付いたエントリは、デフォルトアカウントがトップレベルの`channels.matrix.*`に直接設定されている場合でも引き続き機能します。
共有認証デフォルトが部分的に存在するだけでは、それ自体で別個の暗黙のデフォルトアカウントは作成されません。OpenClawがトップレベルの`default`アカウントを合成するのは、そのデフォルトに新しい認証情報（`homeserver` + `accessToken`、または`homeserver` + `userId` + `password`）がある場合のみです。名前付きアカウントは、後からキャッシュされた認証情報が認証要件を満たす場合、`homeserver` + `userId`の段階でも引き続き検出可能なままです。
Matrixにすでにちょうど1つの名前付きアカウントがある場合、または`defaultAccount`が既存の名前付きアカウントキーを指している場合、単一アカウントから複数アカウントへの修復/セットアップ昇格では、新しい`accounts.default`エントリを作成せず、そのアカウントが保持されます。その昇格済みアカウントに移動するのはMatrix認証/ブートストラップキーのみであり、共有の配信ポリシーキーはトップレベルに残ります。
暗黙のルーティング、プローブ、CLI操作で1つの名前付きMatrixアカウントを優先させたい場合は、`defaultAccount`を設定してください。
複数のMatrixアカウントが設定されていて、そのうちの1つのアカウントIDが`default`である場合、`defaultAccount`が未設定でもOpenClawはそのアカウントを暗黙的に使用します。
複数の名前付きアカウントを設定する場合は、暗黙のアカウント選択に依存するCLIコマンドのために`defaultAccount`を設定するか、`--account <id>`を渡してください。
1つのコマンドだけでその暗黙選択を上書きしたい場合は、`openclaw matrix verify ...`と`openclaw matrix devices ...`に`--account <id>`を渡してください。

共有の複数アカウントパターンについては、[Configuration reference](/ja-JP/gateway/configuration-reference#multi-account-all-channels)を参照してください。

## プライベート/LAN homeserver

デフォルトでは、OpenClawはSSRF保護のため、プライベート/内部のMatrix homeserverをブロックします。アカウントごとに
明示的にオプトインしない限り接続できません。

homeserverがlocalhost、LAN/Tailscale IP、または内部ホスト名で動作している場合は、そのMatrixアカウントに対して
`network.dangerouslyAllowPrivateNetwork`を有効にしてください。

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

このオプトインは、信頼されたプライベート/内部ターゲットのみを許可します。たとえば
`http://matrix.example.org:8008`のような公開クリアテキストhomeserverは引き続きブロックされます。可能な限り`https://`を使用してください。

## Matrixトラフィックのプロキシ

Matrixデプロイで明示的な送信HTTP(S)プロキシが必要な場合は、`channels.matrix.proxy`を設定します。

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

名前付きアカウントは、トップレベルのデフォルトを`channels.matrix.accounts.<id>.proxy`で上書きできます。
OpenClawは、ランタイムのMatrixトラフィックとアカウント状態プローブの両方で同じプロキシ設定を使用します。

## ターゲット解決

Matrixは、OpenClawがルームまたはユーザーターゲットを求めるあらゆる箇所で、次のターゲット形式を受け付けます。

- ユーザー: `@user:server`、`user:@user:server`、または`matrix:user:@user:server`
- ルーム: `!room:server`、`room:!room:server`、または`matrix:room:!room:server`
- エイリアス: `#alias:server`、`channel:#alias:server`、または`matrix:channel:#alias:server`

ライブディレクトリ検索は、ログイン済みのMatrixアカウントを使用します。

- ユーザー検索は、そのhomeserver上のMatrixユーザーディレクトリを問い合わせます。
- ルーム検索は、明示的なルームIDとエイリアスをそのまま受け付け、その後そのアカウントで参加済みのルーム名検索にフォールバックします。
- 参加済みルーム名検索はベストエフォートです。ルーム名をIDまたはエイリアスに解決できない場合、ランタイムallowlist解決では無視されます。

## 設定リファレンス

- `enabled`: channelを有効または無効にします。
- `name`: アカウントのオプションラベル。
- `defaultAccount`: 複数のMatrixアカウントが設定されているときの優先アカウントID。
- `homeserver`: homeserver URL。例: `https://matrix.example.org`。
- `network.dangerouslyAllowPrivateNetwork`: このMatrixアカウントがプライベート/内部homeserverへ接続できるようにします。homeserverが`localhost`、LAN/Tailscale IP、または`matrix-synapse`のような内部ホストに解決される場合に有効化してください。
- `proxy`: Matrixトラフィック用のオプションHTTP(S)プロキシURL。名前付きアカウントは独自の`proxy`でトップレベルデフォルトを上書きできます。
- `userId`: 完全なMatrix user ID。例: `@bot:example.org`。
- `accessToken`: トークンベース認証用のアクセストークン。プレーンテキスト値とSecretRef値は、env/file/execプロバイダー全体で`channels.matrix.accessToken`および`channels.matrix.accounts.<id>.accessToken`に対応しています。[Secrets Management](/ja-JP/gateway/secrets)を参照してください。
- `password`: パスワードベースログイン用のパスワード。プレーンテキスト値とSecretRef値に対応しています。
- `deviceId`: 明示的なMatrix device ID。
- `deviceName`: パスワードログイン用のデバイス表示名。
- `avatarUrl`: プロファイル同期および`profile set`更新用に保存されるセルフアバターURL。
- `initialSyncLimit`: 起動時sync中に取得するイベントの最大数。
- `encryption`: E2EEを有効にします。
- `allowlistOnly`: `true`の場合、`open`ルームポリシーを`allowlist`に引き上げ、`disabled`以外のすべてのアクティブなDMポリシー（`pairing`と`open`を含む）を`allowlist`に強制します。`disabled`ポリシーには影響しません。
- `allowBots`: 他の設定済みOpenClaw Matrixアカウントからのメッセージを許可します（`true`または`"mentions"`）。
- `groupPolicy`: `open`、`allowlist`、または`disabled`。
- `contextVisibility`: 補足ルームコンテキストの可視性モード（`all`、`allowlist`、`allowlist_quote`）。
- `groupAllowFrom`: ルームトラフィック用のuser ID allowlist。エントリは完全なMatrix user IDにしてください。未解決の名前はランタイムで無視されます。
- `historyLimit`: グループ履歴コンテキストとして含めるルームメッセージの最大数。`messages.groupChat.historyLimit`にフォールバックし、両方とも未設定なら実効デフォルトは`0`です。無効にするには`0`を設定します。
- `replyToMode`: `off`、`first`、`all`、または`batched`。
- `markdown`: 送信Matrixテキスト用のオプションMarkdownレンダリング設定。
- `streaming`: `off`（デフォルト）、`"partial"`、`"quiet"`、`true`、または`false`。`"partial"`と`true`は、通常のMatrixテキストメッセージによるプレビュー先行の下書き更新を有効にします。`"quiet"`は、セルフホストのプッシュルール構成向けに通知しないプレビューnoticeを使用します。`false`は`"off"`と同等です。
- `blockStreaming`: `true`は、下書きプレビューストリーミングが有効なとき、完了したassistantブロック用の個別進行状況メッセージを有効にします。
- `threadReplies`: `off`、`inbound`、または`always`。
- `threadBindings`: スレッドにバインドされたセッションルーティングとライフサイクル用のchannelごとの上書き。
- `startupVerification`: 起動時の自動自己検証要求モード（`if-unverified`、`off`）。
- `startupVerificationCooldownHours`: 起動時自動検証要求を再試行するまでのクールダウン。
- `textChunkLimit`: 送信メッセージの文字数チャンクサイズ（`chunkMode`が`length`のときに適用）。
- `chunkMode`: `length`は文字数でメッセージを分割し、`newline`は改行境界で分割します。
- `responsePrefix`: このchannelのすべての送信返信の先頭に付加されるオプション文字列。
- `ackReaction`: このchannel/アカウント用のオプションackリアクション上書き。
- `ackReactionScope`: オプションackリアクションスコープ上書き（`group-mentions`、`group-all`、`direct`、`all`、`none`、`off`）。
- `reactionNotifications`: 受信リアクション通知モード（`own`、`off`）。
- `mediaMaxMb`: 送信送信および受信メディア処理用のメディアサイズ上限（MB）。
- `autoJoin`: 招待自動参加ポリシー（`always`、`allowlist`、`off`）。デフォルト: `off`。DM形式の招待を含むすべてのMatrix招待に適用されます。
- `autoJoinAllowlist`: `autoJoin`が`allowlist`のときに許可されるルーム/エイリアス。エイリアスエントリは招待処理中にルームIDへ解決されます。OpenClawは、招待されたルームが主張するエイリアス状態を信頼しません。
- `dm`: DMポリシーブロック（`enabled`、`policy`、`allowFrom`、`sessionScope`、`threadReplies`）。
- `dm.policy`: OpenClawがルームに参加し、それをDMと分類した後のDMアクセスを制御します。招待が自動参加されるかどうかは変更しません。
- `dm.allowFrom`: すでにライブディレクトリ検索で解決済みでない限り、エントリは完全なMatrix user IDにしてください。
- `dm.sessionScope`: `per-user`（デフォルト）または`per-room`。相手が同じでも各Matrix DMルームで別々のコンテキストを維持したい場合は`per-room`を使用します。
- `dm.threadReplies`: DM専用のスレッドポリシー上書き（`off`、`inbound`、`always`）。DMにおける返信配置とセッション分離の両方で、トップレベルの`threadReplies`設定を上書きします。
- `execApprovals`: Matrixネイティブexec承認配信（`enabled`、`approvers`、`target`、`agentFilter`、`sessionFilter`）。
- `execApprovals.approvers`: execリクエストを承認できるMatrix user ID。`dm.allowFrom`ですでに承認者が識別されている場合は省略可能です。
- `execApprovals.target`: `dm | channel | both`（デフォルト: `dm`）。
- `accounts`: 名前付きのアカウントごとの上書き。トップレベルの`channels.matrix`値はこれらのエントリのデフォルトとして機能します。
- `groups`: ルームごとのポリシーマップ。ルームIDまたはエイリアスを推奨します。未解決のルーム名はランタイムで無視されます。解決後のセッション/グループIDには安定したルームIDが使用されます。
- `groups.<room>.account`: 複数アカウント構成で、1つの継承ルームエントリを特定のMatrixアカウントに限定します。
- `groups.<room>.allowBots`: 設定済みbot送信者に対するルームレベル上書き（`true`または`"mentions"`）。
- `groups.<room>.users`: ルームごとの送信者allowlist。
- `groups.<room>.tools`: ルームごとのtool許可/拒否上書き。
- `groups.<room>.autoReply`: ルームレベルのメンション制御上書き。`true`はそのルームのメンション必須を無効化し、`false`は再び有効化します。
- `groups.<room>.skills`: オプションのルームレベルSkillsフィルター。
- `groups.<room>.systemPrompt`: オプションのルームレベルsystem promptスニペット。
- `rooms`: `groups`のレガシーエイリアス。
- `actions`: アクションごとのtool制御（`messages`、`reactions`、`pins`、`profile`、`memberInfo`、`channelInfo`、`verification`）。

## 関連

- [Channels Overview](/ja-JP/channels) — サポートされているすべてのchannel
- [Pairing](/ja-JP/channels/pairing) — DM認証とpairingフロー
- [Groups](/ja-JP/channels/groups) — グループチャットの動作とメンション制御
- [Channel Routing](/ja-JP/channels/channel-routing) — メッセージのセッションルーティング
- [Security](/ja-JP/gateway/security) — アクセスモデルとハードニング
