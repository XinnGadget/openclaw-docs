---
read_when:
    - Slack をセットアップする場合、または Slack の socket/HTTP モードをデバッグする場合
summary: Slack のセットアップと実行時の動作（Socket Mode + HTTP Events API）
title: Slack
x-i18n:
    generated_at: "2026-04-06T03:07:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7e4ff2ce7d92276d62f4f3d3693ddb56ca163d5fdc2f1082ff7ba3421fada69c
    source_path: channels/slack.md
    workflow: 15
---

# Slack

ステータス: Slack アプリ連携による DM + チャンネル向けに本番運用対応済み。デフォルトモードは Socket Mode で、HTTP Events API モードにも対応しています。

<CardGroup cols={3}>
  <Card title="ペアリング" icon="link" href="/ja-JP/channels/pairing">
    Slack DM はデフォルトでペアリングモードです。
  </Card>
  <Card title="スラッシュコマンド" icon="terminal" href="/ja-JP/tools/slash-commands">
    ネイティブコマンドの動作とコマンドカタログ。
  </Card>
  <Card title="チャンネルのトラブルシューティング" icon="wrench" href="/ja-JP/channels/troubleshooting">
    チャンネル横断の診断と修復プレイブック。
  </Card>
</CardGroup>

## クイックセットアップ

<Tabs>
  <Tab title="Socket Mode（デフォルト）">
    <Steps>
      <Step title="Slack アプリとトークンを作成する">
        Slack アプリの設定で次を行います:

        - **Socket Mode** を有効にする
        - `connections:write` を持つ **App Token**（`xapp-...`）を作成する
        - アプリをインストールし、**Bot Token**（`xoxb-...`）をコピーする
      </Step>

      <Step title="OpenClaw を設定する">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "socket",
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

        環境変数でのフォールバック（デフォルトアカウントのみ）:

```bash
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
```

      </Step>

      <Step title="アプリイベントを購読する">
        次の bot イベントを購読します:

        - `app_mention`
        - `message.channels`, `message.groups`, `message.im`, `message.mpim`
        - `reaction_added`, `reaction_removed`
        - `member_joined_channel`, `member_left_channel`
        - `channel_rename`
        - `pin_added`, `pin_removed`

        さらに、DM 用に App Home の **Messages Tab** を有効にします。
      </Step>

      <Step title="Gateway を起動する">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP Events API モード">
    <Steps>
      <Step title="HTTP 用に Slack アプリを設定する">

        - モードを HTTP に設定する（`channels.slack.mode="http"`）
        - Slack の **Signing Secret** をコピーする
        - Event Subscriptions、Interactivity、スラッシュコマンドの Request URL をすべて同じ webhook パス（デフォルトは `/slack/events`）に設定する

      </Step>

      <Step title="OpenClaw の HTTP モードを設定する">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "your-signing-secret",
      webhookPath: "/slack/events",
    },
  },
}
```

      </Step>

      <Step title="複数アカウントの HTTP では一意の webhook パスを使う">
        アカウントごとの HTTP モードに対応しています。

        登録が衝突しないように、各アカウントに異なる `webhookPath` を設定してください。
      </Step>
    </Steps>

  </Tab>
</Tabs>

## マニフェストとスコープのチェックリスト

<AccordionGroup>
  <Accordion title="Slack アプリのマニフェスト例" defaultOpen>

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    }
  }
}
```

  </Accordion>

  <Accordion title="任意の user-token スコープ（読み取り操作）">
    `channels.slack.userToken` を設定する場合、一般的な読み取りスコープは次のとおりです:

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read`（Slack 検索の読み取りに依存する場合）

  </Accordion>
</AccordionGroup>

## トークンモデル

- Socket Mode には `botToken` + `appToken` が必要です。
- HTTP モードには `botToken` + `signingSecret` が必要です。
- `botToken`、`appToken`、`signingSecret`、`userToken` は平文の文字列または SecretRef オブジェクトを受け付けます。
- 設定内のトークンは環境変数フォールバックより優先されます。
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` の環境変数フォールバックはデフォルトアカウントにのみ適用されます。
- `userToken`（`xoxp-...`）は設定専用です（環境変数フォールバックなし）。デフォルトでは読み取り専用動作（`userTokenReadOnly: true`）になります。
- 任意: 送信メッセージにアクティブなエージェントの識別情報（カスタム `username` とアイコン）を使いたい場合は、`chat:write.customize` を追加してください。`icon_emoji` は `:emoji_name:` 構文を使います。

ステータススナップショットの動作:

- Slack アカウントの検査では、認証情報ごとの `*Source` と `*Status` フィールド（`botToken`、`appToken`、`signingSecret`、`userToken`）を追跡します。
- ステータスは `available`、`configured_unavailable`、`missing` のいずれかです。
- `configured_unavailable` は、そのアカウントが SecretRef または別のインラインではないシークレットソース経由で設定されているものの、現在のコマンド/実行時パスでは実際の値を解決できなかったことを意味します。
- HTTP モードでは `signingSecretStatus` が含まれます。Socket Mode では必要な組み合わせは `botTokenStatus` + `appTokenStatus` です。

<Tip>
アクション/ディレクトリ読み取りでは、設定されていれば user token を優先できます。書き込みでは bot token が引き続き優先されます。user-token による書き込みは、`userTokenReadOnly: false` かつ bot token が利用できない場合にのみ許可されます。
</Tip>

## アクションとゲート

Slack のアクションは `channels.slack.actions.*` で制御されます。

現在の Slack ツールで利用可能なアクショングループ:

| Group      | Default |
| ---------- | ------- |
| messages   | enabled |
| reactions  | enabled |
| pins       | enabled |
| memberInfo | enabled |
| emojiList  | enabled |

現在の Slack メッセージアクションには、`send`、`upload-file`、`download-file`、`read`、`edit`、`delete`、`pin`、`unpin`、`list-pins`、`member-info`、`emoji-list` が含まれます。

## アクセス制御とルーティング

<Tabs>
  <Tab title="DM ポリシー">
    `channels.slack.dmPolicy` は DM アクセスを制御します（旧式: `channels.slack.dm.policy`）:

    - `pairing`（デフォルト）
    - `allowlist`
    - `open`（`channels.slack.allowFrom` に `"*"` を含める必要があります。旧式: `channels.slack.dm.allowFrom`）
    - `disabled`

    DM フラグ:

    - `dm.enabled`（デフォルト true）
    - `channels.slack.allowFrom`（推奨）
    - `dm.allowFrom`（旧式）
    - `dm.groupEnabled`（グループ DM のデフォルトは false）
    - `dm.groupChannels`（任意の MPIM 許可リスト）

    複数アカウント時の優先順位:

    - `channels.slack.accounts.default.allowFrom` は `default` アカウントにのみ適用されます。
    - 名前付きアカウントは、自身の `allowFrom` が未設定の場合に `channels.slack.allowFrom` を継承します。
    - 名前付きアカウントは `channels.slack.accounts.default.allowFrom` を継承しません。

    DM でのペアリングには `openclaw pairing approve slack <code>` を使います。

  </Tab>

  <Tab title="チャンネルポリシー">
    `channels.slack.groupPolicy` はチャンネルの扱いを制御します:

    - `open`
    - `allowlist`
    - `disabled`

    チャンネル許可リストは `channels.slack.channels` 配下にあり、安定したチャンネル ID を使うべきです。

    実行時メモ: `channels.slack` が完全に欠けている場合（環境変数のみのセットアップ）、実行時は `groupPolicy="allowlist"` にフォールバックし、警告を記録します（`channels.defaults.groupPolicy` が設定されていても同様です）。

    名前/ID 解決:

    - チャンネル許可リスト項目と DM 許可リスト項目は、トークンアクセスが可能なら起動時に解決されます
    - 未解決のチャンネル名エントリは設定どおり保持されますが、デフォルトではルーティングで無視されます
    - 受信認可とチャンネルルーティングはデフォルトで ID 優先です。直接のユーザー名/スラッグ一致には `channels.slack.dangerouslyAllowNameMatching: true` が必要です

  </Tab>

  <Tab title="メンションとチャンネルユーザー">
    チャンネルメッセージはデフォルトでメンションゲートされます。

    メンションソース:

    - 明示的なアプリメンション（`<@botId>`）
    - メンション正規表現パターン（`agents.list[].groupChat.mentionPatterns`、フォールバックは `messages.groupChat.mentionPatterns`）
    - bot への返信スレッドの暗黙的動作

    チャンネルごとの制御（`channels.slack.channels.<id>`; 名前は起動時解決または `dangerouslyAllowNameMatching` 経由のみ）:

    - `requireMention`
    - `users`（許可リスト）
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - `toolsBySender` のキー形式: `id:`、`e164:`、`username:`、`name:`、または `"*"` ワイルドカード
      （旧式の接頭辞なしキーも引き続き `id:` のみにマップされます）

  </Tab>
</Tabs>

## スレッド、セッション、返信タグ

- DM は `direct`、チャンネルは `channel`、MPIM は `group` としてルーティングされます。
- デフォルトの `session.dmScope=main` では、Slack DM はエージェントのメインセッションに集約されます。
- チャンネルセッション: `agent:<agentId>:slack:channel:<channelId>`。
- スレッド返信では、必要に応じてスレッドセッション接尾辞（`:thread:<threadTs>`）が作成されることがあります。
- `channels.slack.thread.historyScope` のデフォルトは `thread`、`thread.inheritParent` のデフォルトは `false` です。
- `channels.slack.thread.initialHistoryLimit` は、新しいスレッドセッション開始時に取得する既存スレッドメッセージ数を制御します（デフォルトは `20`、無効化するには `0` を設定します）。

返信スレッド制御:

- `channels.slack.replyToMode`: `off|first|all|batched`（デフォルトは `off`）
- `channels.slack.replyToModeByChatType`: `direct|group|channel` ごと
- 直接チャット向けの旧式フォールバック: `channels.slack.dm.replyToMode`

手動返信タグに対応しています:

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

注意: `replyToMode="off"` は、Slack における **すべて** の返信スレッド機能を無効にします。これには明示的な `[[reply_to_*]]` タグも含まれます。これは Telegram と異なり、Telegram では `"off"` モードでも明示タグは引き続き尊重されます。この違いはプラットフォームのスレッドモデルを反映しています。Slack スレッドはメッセージをチャンネルから隠しますが、Telegram の返信はメインチャットの流れに表示されたままです。

## 確認リアクション

`ackReaction` は、OpenClaw が受信メッセージを処理中であることを示す確認絵文字を送信します。

解決順序:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- エージェント識別絵文字のフォールバック（`agents.list[].identity.emoji`、なければ `"👀"`）

注意:

- Slack はショートコードを想定しています（例: `"eyes"`）。
- Slack アカウント単位またはグローバルでリアクションを無効にするには `""` を使います。

## テキストストリーミング

`channels.slack.streaming` はライブプレビュー動作を制御します:

- `off`: ライブプレビューのストリーミングを無効にします。
- `partial`（デフォルト）: プレビューテキストを最新の部分出力で置き換えます。
- `block`: チャンク化されたプレビュー更新を追記します。
- `progress`: 生成中は進捗ステータステキストを表示し、その後最終テキストを送信します。

`channels.slack.nativeStreaming` は、`streaming` が `partial` のときに Slack ネイティブのテキストストリーミングを制御します（デフォルト: `true`）。

- Slack ネイティブのテキストストリーミングを表示するには返信スレッドが利用可能である必要があります。スレッドの選択は引き続き `replyToMode` に従います。スレッドがなければ通常の下書きプレビューが使われます。
- メディアと非テキストペイロードは通常配信にフォールバックします。
- 返信の途中でストリーミングに失敗した場合、OpenClaw は残りのペイロードについて通常配信にフォールバックします。

Slack ネイティブのテキストストリーミングの代わりに下書きプレビューを使う:

```json5
{
  channels: {
    slack: {
      streaming: "partial",
      nativeStreaming: false,
    },
  },
}
```

旧式キー:

- `channels.slack.streamMode`（`replace | status_final | append`）は自動的に `channels.slack.streaming` に移行されます。
- 真偽値の `channels.slack.streaming` は自動的に `channels.slack.nativeStreaming` に移行されます。

## 入力中リアクションのフォールバック

`typingReaction` は、OpenClaw が返信を処理している間、受信した Slack メッセージに一時的なリアクションを追加し、実行完了時に削除します。これは、デフォルトの「入力中...」ステータスインジケーターを使うスレッド返信の外で特に有用です。

解決順序:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

注意:

- Slack はショートコードを想定しています（例: `"hourglass_flowing_sand"`）。
- このリアクションはベストエフォートで、返信または失敗パスの完了後に自動クリーンアップが試行されます。

## メディア、チャンク化、配信

<AccordionGroup>
  <Accordion title="受信添付ファイル">
    Slack のファイル添付は、Slack がホストするプライベート URL からダウンロードされます（トークン認証付きリクエストフロー）。取得に成功し、サイズ制限内であればメディアストアに書き込まれます。

    実行時の受信サイズ上限は、`channels.slack.mediaMaxMb` で上書きしない限りデフォルトで `20MB` です。

  </Accordion>

  <Accordion title="送信テキストとファイル">
    - テキストチャンクには `channels.slack.textChunkLimit` を使います（デフォルト 4000）
    - `channels.slack.chunkMode="newline"` で段落優先の分割を有効にします
    - ファイル送信には Slack のアップロード API を使い、スレッド返信（`thread_ts`）を含めることができます
    - 送信メディア上限は、`channels.slack.mediaMaxMb` が設定されていればそれに従い、そうでなければチャンネル送信はメディアパイプラインの MIME 種別デフォルトに従います
  </Accordion>

  <Accordion title="配信先">
    推奨される明示的な送信先:

    - DM には `user:<id>`
    - チャンネルには `channel:<id>`

    ユーザー宛て送信時、Slack DM は Slack conversation API を通じて開かれます。

  </Accordion>
</AccordionGroup>

## コマンドとスラッシュ動作

- Slack ではネイティブコマンドの自動モードは **off** です（`commands.native: "auto"` では Slack ネイティブコマンドは有効になりません）。
- `channels.slack.commands.native: true`（またはグローバルな `commands.native: true`）でネイティブ Slack コマンドハンドラーを有効にします。
- ネイティブコマンドが有効な場合、対応するスラッシュコマンドを Slack に登録してください（`/<command>` 名）。ただし例外が 1 つあります:
  - ステータスコマンドには `/agentstatus` を登録してください（Slack は `/status` を予約しています）
- ネイティブコマンドが有効でない場合は、`channels.slack.slashCommand` によって設定された単一のスラッシュコマンドを実行できます。
- ネイティブ引数メニューはレンダリング戦略を自動調整するようになりました:
  - 最大 5 個のオプション: ボタンブロック
  - 6〜100 個のオプション: static select メニュー
  - 100 個を超えるオプション: interactivity options handler が利用可能な場合、非同期オプションフィルタリング付きの external select
  - エンコードされたオプション値が Slack の制限を超える場合、フローはボタンにフォールバックします
- 長いオプションペイロードでは、スラッシュコマンド引数メニューは選択値のディスパッチ前に確認ダイアログを使います。

デフォルトのスラッシュコマンド設定:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

スラッシュセッションは分離されたキーを使います:

- `agent:<agentId>:slack:slash:<userId>`

また、コマンド実行は引き続き対象会話セッション（`CommandTargetSessionKey`）に対してルーティングされます。

## インタラクティブ返信

Slack ではエージェント作成のインタラクティブ返信コントロールをレンダリングできますが、この機能はデフォルトで無効です。

グローバルに有効化する:

```json5
{
  channels: {
    slack: {
      capabilities: {
        interactiveReplies: true,
      },
    },
  },
}
```

または、1 つの Slack アカウントでのみ有効化する:

```json5
{
  channels: {
    slack: {
      accounts: {
        ops: {
          capabilities: {
            interactiveReplies: true,
          },
        },
      },
    },
  },
}
```

有効化すると、エージェントは Slack 専用の返信ディレクティブを出力できます:

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

これらのディレクティブは Slack Block Kit にコンパイルされ、クリックや選択を既存の Slack interaction event パス経由で戻します。

注意:

- これは Slack 固有の UI です。他のチャンネルでは Slack Block Kit ディレクティブを独自のボタンシステムに変換しません。
- インタラクティブコールバック値は OpenClaw 生成の不透明トークンであり、生のエージェント作成値ではありません。
- 生成されたインタラクティブブロックが Slack Block Kit の制限を超える場合、OpenClaw は無効な blocks ペイロードを送る代わりに元のテキスト返信へフォールバックします。

## Slack での exec 承認

Slack は、Web UI やターミナルにフォールバックする代わりに、インタラクティブボタンと interaction を備えたネイティブ承認クライアントとして機能できます。

- Exec 承認では、ネイティブ DM/チャンネルルーティングに `channels.slack.execApprovals.*` を使います。
- リクエストがすでに Slack に届いており、承認 id の種別が `plugin:` である場合、plugin 承認も同じ Slack ネイティブボタン UI で解決できます。
- 承認者認可は引き続き適用されます。Slack を通じてリクエストを承認または拒否できるのは、承認者として識別されたユーザーだけです。

これは他のチャンネルと同じ共有承認ボタン UI を使います。Slack アプリ設定で `interactivity` が有効な場合、承認プロンプトは会話内に Block Kit ボタンとして直接レンダリングされます。
これらのボタンが存在する場合、それらが主要な承認 UX です。OpenClaw は、ツール結果がチャット承認を利用不可と示す場合、または手動承認が唯一の経路である場合にのみ、手動の `/approve` コマンドを含めるべきです。

設定パス:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers`（任意。可能であれば `commands.ownerAllowFrom` にフォールバックします）
- `channels.slack.execApprovals.target`（`dm` | `channel` | `both`、デフォルト: `dm`）
- `agentFilter`, `sessionFilter`

Slack は、`enabled` が未設定または `"auto"` で、少なくとも 1 人の
承認者が解決される場合、自動的にネイティブ exec 承認を有効にします。Slack をネイティブ承認クライアントとして明示的に無効にするには `enabled: false` を設定します。
承認者が解決されるときにネイティブ承認を強制的に有効化するには `enabled: true` を設定します。

明示的な Slack exec 承認設定がない場合のデフォルト動作:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

承認者を上書きしたり、フィルターを追加したり、送信元チャット配信を有効にしたい場合にのみ、明示的な Slack ネイティブ設定が必要です:

```json5
{
  channels: {
    slack: {
      execApprovals: {
        enabled: true,
        approvers: ["U12345678"],
        target: "both",
      },
    },
  },
}
```

共有の `approvals.exec` 転送は別機能です。exec 承認プロンプトを他のチャットや明示的な帯域外ターゲットにもルーティングする必要がある場合にのみ使ってください。共有の `approvals.plugin` 転送も別機能です。Slack ネイティブボタンは、それらのリクエストがすでに Slack に届いている場合、引き続き plugin 承認を解決できます。

同一チャットの `/approve` は、すでにコマンド対応している Slack チャンネルと DM でも機能します。完全な承認転送モデルについては [Exec approvals](/ja-JP/tools/exec-approvals) を参照してください。

## イベントと運用時の動作

- メッセージ編集/削除/スレッドブロードキャストはシステムイベントにマッピングされます。
- リアクション追加/削除イベントはシステムイベントにマッピングされます。
- メンバー参加/退出、チャンネル作成/名前変更、ピン追加/削除イベントはシステムイベントにマッピングされます。
- `channel_id_changed` は、`configWrites` が有効な場合にチャンネル設定キーを移行できます。
- チャンネルトピック/目的メタデータは信頼されないコンテキストとして扱われ、ルーティングコンテキストに注入されることがあります。
- スレッド開始メッセージと初期スレッド履歴コンテキストのシーディングは、適用可能な場合に設定済み送信者許可リストでフィルタリングされます。
- ブロックアクションとモーダル interaction は、構造化された `Slack interaction: ...` システムイベントとして、豊富なペイロードフィールド付きで出力されます:
  - ブロックアクション: 選択値、ラベル、picker 値、`workflow_*` メタデータ
  - モーダル `view_submission` と `view_closed` イベント: ルーティング済みチャンネルメタデータとフォーム入力を含む

## 設定リファレンスへのポインタ

主要なリファレンス:

- [設定リファレンス - Slack](/ja-JP/gateway/configuration-reference#slack)

  重要な Slack フィールド:
  - モード/認証: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DM アクセス: `dm.enabled`, `dmPolicy`, `allowFrom`（旧式: `dm.policy`, `dm.allowFrom`）、`dm.groupEnabled`, `dm.groupChannels`
  - 互換性トグル: `dangerouslyAllowNameMatching`（緊急用。必要な場合を除いて無効のままにしてください）
  - チャンネルアクセス: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - スレッド/履歴: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - 配信: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - 運用/機能: `configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## トラブルシューティング

<AccordionGroup>
  <Accordion title="チャンネルで返信がない">
    次の順に確認してください:

    - `groupPolicy`
    - チャンネル許可リスト（`channels.slack.channels`）
    - `requireMention`
    - チャンネルごとの `users` 許可リスト

    便利なコマンド:

```bash
openclaw channels status --probe
openclaw logs --follow
openclaw doctor
```

  </Accordion>

  <Accordion title="DM メッセージが無視される">
    確認事項:

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy`（または旧式の `channels.slack.dm.policy`）
    - ペアリング承認 / 許可リスト項目

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Socket mode が接続しない">
    Bot トークンと App トークン、および Slack アプリ設定での Socket Mode 有効化を検証してください。

    `openclaw channels status --probe --json` で `botTokenStatus` または
    `appTokenStatus: "configured_unavailable"` が表示される場合、その Slack アカウントは
    設定されていますが、現在の実行時では SecretRef バックの値を
    解決できませんでした。

  </Accordion>

  <Accordion title="HTTP モードでイベントを受信しない">
    次を検証してください:

    - signing secret
    - webhook パス
    - Slack Request URL（Events + Interactivity + Slash Commands）
    - HTTP アカウントごとに一意の `webhookPath`

    アカウントスナップショットに `signingSecretStatus: "configured_unavailable"` が
    表示される場合、その HTTP アカウントは設定されていますが、現在の実行時では
    SecretRef バックの signing secret を解決できませんでした。

  </Accordion>

  <Accordion title="ネイティブ/スラッシュコマンドが動作しない">
    意図していたのがどちらかを確認してください:

    - ネイティブコマンドモード（`channels.slack.commands.native: true`）で、対応するスラッシュコマンドが Slack に登録されている
    - または単一スラッシュコマンドモード（`channels.slack.slashCommand.enabled: true`）

    さらに `commands.useAccessGroups` とチャンネル/ユーザー許可リストも確認してください。

  </Accordion>
</AccordionGroup>

## 関連

- [ペアリング](/ja-JP/channels/pairing)
- [グループ](/ja-JP/channels/groups)
- [セキュリティ](/ja-JP/gateway/security)
- [チャンネルルーティング](/ja-JP/channels/channel-routing)
- [トラブルシューティング](/ja-JP/channels/troubleshooting)
- [設定](/ja-JP/gateway/configuration)
- [スラッシュコマンド](/ja-JP/tools/slash-commands)
