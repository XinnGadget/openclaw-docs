---
read_when:
    - Slackの設定時、またはSlackのsocket/HTTPモードをデバッグするとき
summary: Slackのセットアップとランタイム動作（Socket Mode + HTTP Request URLs）
title: Slack
x-i18n:
    generated_at: "2026-04-07T04:42:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2b8fd2cc6c638ee82069f0af2c2b6f6f49c87da709b941433a0343724a9907ea
    source_path: channels/slack.md
    workflow: 15
---

# Slack

ステータス: Slackアプリ連携によるDMとチャンネルに対応した本番運用対応。デフォルトモードはSocket Modeで、HTTP Request URLsもサポートされています。

<CardGroup cols={3}>
  <Card title="ペアリング" icon="link" href="/ja-JP/channels/pairing">
    Slack DMはデフォルトでペアリングモードです。
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
  <Tab title="Socket Mode (default)">
    <Steps>
      <Step title="新しいSlackアプリを作成する">
        Slackアプリ設定で **[Create New App](https://api.slack.com/apps/new)** ボタンを押します。

        - **from a manifest** を選び、アプリ用のワークスペースを選択します
        - 下の[サンプルmanifest](#manifest-and-scope-checklist)を貼り付け、そのまま作成を続行します
        - `connections:write` を付与した **App-Level Token** (`xapp-...`) を生成します
        - アプリをインストールし、表示される **Bot Token** (`xoxb-...`) をコピーします
      </Step>

      <Step title="OpenClawを設定する">

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

      <Step title="Gatewayを起動する">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP Request URLs">
    <Steps>
      <Step title="新しいSlackアプリを作成する">
        Slackアプリ設定で **[Create New App](https://api.slack.com/apps/new)** ボタンを押します。

        - **from a manifest** を選び、アプリ用のワークスペースを選択します
        - [サンプルmanifest](#manifest-and-scope-checklist)を貼り付け、作成前にURLを更新します
        - リクエスト検証用に **Signing Secret** を保存します
        - アプリをインストールし、表示される **Bot Token** (`xoxb-...`) をコピーします

      </Step>

      <Step title="OpenClawを設定する">

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

        <Note>
        マルチアカウントHTTPでは一意のwebhookパスを使用してください

        各アカウントに異なる `webhookPath`（デフォルトは `/slack/events`）を設定して、登録が衝突しないようにしてください。
        </Note>

      </Step>

      <Step title="Gatewayを起動する">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>
</Tabs>

## Manifestとスコープのチェックリスト

<Tabs>
  <Tab title="Socket Mode (default)">

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

  </Tab>

  <Tab title="HTTP Request URLs">

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
        "should_escape": false,
        "url": "https://gateway-host.example.com/slack/events"
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
    "event_subscriptions": {
      "request_url": "https://gateway-host.example.com/slack/events",
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
    },
    "interactivity": {
      "is_enabled": true,
      "request_url": "https://gateway-host.example.com/slack/events",
      "message_menu_options_url": "https://gateway-host.example.com/slack/events"
    }
  }
}
```

  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="任意のauthorshipスコープ（書き込み操作）">
    送信メッセージでデフォルトのSlackアプリIDではなく、アクティブなエージェントID（カスタムのユーザー名とアイコン）を使いたい場合は、`chat:write.customize` botスコープを追加してください。

    絵文字アイコンを使う場合、Slackは `:emoji_name:` 構文を想定します。

  </Accordion>
  <Accordion title="任意のuser tokenスコープ（読み取り操作）">
    `channels.slack.userToken` を設定する場合、一般的な読み取りスコープは次のとおりです:

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read`（Slack検索の読み取りに依存する場合）

  </Accordion>
</AccordionGroup>

## トークンモデル

- Socket Modeでは `botToken` + `appToken` が必要です。
- HTTPモードでは `botToken` + `signingSecret` が必要です。
- `botToken`、`appToken`、`signingSecret`、`userToken` はプレーンテキスト文字列またはSecretRefオブジェクトを受け付けます。
- 設定内のトークンは環境変数フォールバックより優先されます。
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` の環境変数フォールバックはデフォルトアカウントにのみ適用されます。
- `userToken` (`xoxp-...`) は設定でのみ指定可能です（環境変数フォールバックなし）。デフォルトでは読み取り専用動作（`userTokenReadOnly: true`）になります。

ステータススナップショットの動作:

- Slackアカウントの検査では、認証情報ごとの `*Source` と `*Status` フィールド（`botToken`、`appToken`、`signingSecret`、`userToken`）を追跡します。
- ステータスは `available`、`configured_unavailable`、`missing` のいずれかです。
- `configured_unavailable` は、そのアカウントがSecretRefまたは別の非インラインなシークレットソース経由で設定されているものの、現在のコマンド/ランタイム経路では実際の値を解決できなかったことを意味します。
- HTTPモードでは `signingSecretStatus` が含まれます。Socket Modeでは、必要な組み合わせは `botTokenStatus` + `appTokenStatus` です。

<Tip>
アクションやディレクトリ読み取りでは、設定されていればuser tokenが優先されることがあります。書き込みでは引き続きbot tokenが優先されます。user tokenでの書き込みは、`userTokenReadOnly: false` かつbot tokenが利用できない場合にのみ許可されます。
</Tip>

## Actionsとゲート

Slack actionsは `channels.slack.actions.*` で制御します。

現在のSlackツールで利用可能なactionグループ:

| Group      | Default |
| ---------- | ------- |
| messages   | enabled |
| reactions  | enabled |
| pins       | enabled |
| memberInfo | enabled |
| emojiList  | enabled |

現在のSlackメッセージactionには、`send`、`upload-file`、`download-file`、`read`、`edit`、`delete`、`pin`、`unpin`、`list-pins`、`member-info`、`emoji-list` が含まれます。

## アクセス制御とルーティング

<Tabs>
  <Tab title="DM policy">
    `channels.slack.dmPolicy` はDMアクセスを制御します（旧式: `channels.slack.dm.policy`）:

    - `pairing`（デフォルト）
    - `allowlist`
    - `open`（`channels.slack.allowFrom` に `"*"` を含める必要があります。旧式: `channels.slack.dm.allowFrom`）
    - `disabled`

    DMフラグ:

    - `dm.enabled`（デフォルトはtrue）
    - `channels.slack.allowFrom`（推奨）
    - `dm.allowFrom`（旧式）
    - `dm.groupEnabled`（グループDMのデフォルトはfalse）
    - `dm.groupChannels`（任意のMPIM許可リスト）

    マルチアカウントの優先順位:

    - `channels.slack.accounts.default.allowFrom` は `default` アカウントにのみ適用されます。
    - 名前付きアカウントは、自身の `allowFrom` が未設定の場合に `channels.slack.allowFrom` を継承します。
    - 名前付きアカウントは `channels.slack.accounts.default.allowFrom` を継承しません。

    DMでのペアリングには `openclaw pairing approve slack <code>` を使用します。

  </Tab>

  <Tab title="Channel policy">
    `channels.slack.groupPolicy` はチャンネル処理を制御します:

    - `open`
    - `allowlist`
    - `disabled`

    チャンネル許可リストは `channels.slack.channels` 配下にあり、安定したチャンネルIDを使う必要があります。

    ランタイム上の注意: `channels.slack` が完全に存在しない場合（環境変数のみのセットアップ）、ランタイムは `groupPolicy="allowlist"` にフォールバックし、警告を記録します（`channels.defaults.groupPolicy` が設定されていても同様です）。

    名前/ID解決:

    - チャンネル許可リスト項目とDM許可リスト項目は、トークンアクセスが可能であれば起動時に解決されます
    - 解決できないチャンネル名エントリは設定どおり保持されますが、デフォルトではルーティングでは無視されます
    - 受信時の認可とチャンネルルーティングは、デフォルトでID優先です。ユーザー名/slugの直接一致には `channels.slack.dangerouslyAllowNameMatching: true` が必要です

  </Tab>

  <Tab title="Mentions and channel users">
    チャンネルメッセージはデフォルトでメンションによるゲート制御が有効です。

    メンションソース:

    - 明示的なアプリメンション（`<@botId>`）
    - メンション正規表現パターン（`agents.list[].groupChat.mentionPatterns`、フォールバックは `messages.groupChat.mentionPatterns`）
    - 暗黙のbot返信スレッド動作（`thread.requireExplicitMention` が `true` の場合は無効）

    チャンネルごとの制御（`channels.slack.channels.<id>`; 名前は起動時解決または `dangerouslyAllowNameMatching` 経由のみ）:

    - `requireMention`
    - `users`（許可リスト）
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - `toolsBySender` のキー形式: `id:`、`e164:`、`username:`、`name:`、または `"*"` ワイルドカード
      （旧式のプレフィックスなしキーも引き続き `id:` のみに対応付けられます）

  </Tab>
</Tabs>

## スレッド、セッション、返信タグ

- DMは `direct` としてルーティングされ、チャンネルは `channel`、MPIMは `group` としてルーティングされます。
- デフォルトの `session.dmScope=main` では、Slack DMはエージェントのメインセッションに集約されます。
- チャンネルセッション: `agent:<agentId>:slack:channel:<channelId>`。
- スレッド返信では、必要に応じてスレッドセッション接尾辞（`:thread:<threadTs>`）が作成されます。
- `channels.slack.thread.historyScope` のデフォルトは `thread`、`thread.inheritParent` のデフォルトは `false` です。
- `channels.slack.thread.initialHistoryLimit` は、新しいスレッドセッション開始時に取得する既存スレッドメッセージ数を制御します（デフォルトは `20`、無効化するには `0` を設定）。
- `channels.slack.thread.requireExplicitMention`（デフォルト `false`）: `true` の場合、暗黙のスレッドメンションを抑制し、botがすでにそのスレッドに参加していても、スレッド内の明示的な `@bot` メンションにのみ応答します。これがない場合、botが参加しているスレッド内の返信は `requireMention` のゲートをバイパスします。

返信スレッド制御:

- `channels.slack.replyToMode`: `off|first|all|batched`（デフォルト `off`）
- `channels.slack.replyToModeByChatType`: `direct|group|channel` ごと
- direct chat用の旧式フォールバック: `channels.slack.dm.replyToMode`

手動の返信タグをサポートしています:

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

注意: `replyToMode="off"` は、明示的な `[[reply_to_*]]` タグを含め、Slackでの**すべて**の返信スレッドを無効化します。これはTelegramと異なり、Telegramでは `"off"` モードでも明示的なタグは引き続き有効です。この違いはプラットフォームごとのスレッドモデルを反映しています。Slackのスレッドはメッセージをチャンネルから隠しますが、Telegramの返信はメインチャットの流れの中で引き続き表示されます。

## 確認リアクション

`ackReaction` は、OpenClawが受信メッセージを処理している間、確認用の絵文字を送信します。

解決順序:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- エージェントIDの絵文字フォールバック（`agents.list[].identity.emoji`、なければ `"👀"`）

注意:

- Slackはショートコード（たとえば `"eyes"`）を想定します。
- Slackアカウント単位または全体でリアクションを無効にするには `""` を使用します。

## テキストストリーミング

`channels.slack.streaming` はライブプレビュー動作を制御します:

- `off`: ライブプレビューのストリーミングを無効にします。
- `partial`（デフォルト）: プレビューテキストを最新の部分出力に置き換えます。
- `block`: チャンク化されたプレビュー更新を追記します。
- `progress`: 生成中は進捗ステータステキストを表示し、その後に最終テキストを送信します。

`channels.slack.nativeStreaming` は、`streaming` が `partial` のときにSlackネイティブのテキストストリーミングを制御します（デフォルト: `true`）。

- ネイティブのテキストストリーミングを表示するには返信スレッドが必要です。スレッド選択は引き続き `replyToMode` に従います。これがない場合、通常の下書きプレビューが使われます。
- メディアや非テキストのペイロードは通常配信にフォールバックします。
- 返信の途中でストリーミングに失敗した場合、OpenClawは残りのペイロードを通常配信にフォールバックします。

Slackネイティブのテキストストリーミングの代わりに下書きプレビューを使うには:

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

`typingReaction` は、OpenClawが返信を処理している間、受信したSlackメッセージに一時的なリアクションを追加し、実行終了時に削除します。これは、デフォルトの「入力中...」ステータスインジケーターを使うスレッド返信の外で特に有用です。

解決順序:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

注意:

- Slackはショートコード（たとえば `"hourglass_flowing_sand"`）を想定します。
- このリアクションはベストエフォートであり、返信または失敗経路の完了後に自動クリーンアップが試行されます。

## メディア、チャンク化、配信

<AccordionGroup>
  <Accordion title="受信添付ファイル">
    Slackのファイル添付は、SlackがホストするプライベートURLからダウンロードされ（トークン認証付きリクエストフロー）、取得に成功しサイズ制限内であればメディアストアに書き込まれます。

    ランタイムの受信サイズ上限は、`channels.slack.mediaMaxMb` で上書きしない限りデフォルトで `20MB` です。

  </Accordion>

  <Accordion title="送信テキストとファイル">
    - テキストチャンクには `channels.slack.textChunkLimit`（デフォルト 4000）を使用します
    - `channels.slack.chunkMode="newline"` は段落優先の分割を有効にします
    - ファイル送信にはSlackアップロードAPIを使用し、スレッド返信（`thread_ts`）を含められます
    - 送信メディア上限は、設定されていれば `channels.slack.mediaMaxMb` に従います。未設定の場合、チャンネル送信ではメディアパイプラインのMIME種別デフォルトを使用します
  </Accordion>

  <Accordion title="配信先">
    推奨される明示的な宛先:

    - DMには `user:<id>`
    - チャンネルには `channel:<id>`

    Slack DMは、ユーザー宛先に送信する際にSlackのconversation API経由で開かれます。

  </Accordion>
</AccordionGroup>

## コマンドとスラッシュ動作

- Slackではネイティブコマンド自動モードは**off**です（`commands.native: "auto"` ではSlackネイティブコマンドは有効になりません）。
- ネイティブSlackコマンドハンドラーを有効にするには `channels.slack.commands.native: true`（またはグローバルの `commands.native: true`）を設定します。
- ネイティブコマンドが有効な場合、Slackに対応するスラッシュコマンド（`/<command>` 名）を登録してください。ただし1つ例外があります:
  - ステータスコマンドには `/agentstatus` を登録します（Slackは `/status` を予約しています）
- ネイティブコマンドが有効でない場合は、`channels.slack.slashCommand` 経由で1つの設定済みスラッシュコマンドを実行できます。
- ネイティブ引数メニューはレンダリング戦略を動的に切り替えるようになりました:
  - 最大5個のオプション: ボタンブロック
  - 6〜100個のオプション: static select menu
  - 100個を超えるオプション: interactivity options handlerが利用可能な場合、非同期オプションフィルタリング付きのexternal select
  - エンコード済みオプション値がSlackの制限を超える場合、フローはボタンにフォールバックします
- 長いオプションペイロードでは、Slash command引数メニューは選択値をディスパッチする前に確認ダイアログを使用します。

デフォルトのスラッシュコマンド設定:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

スラッシュセッションは分離されたキーを使用します:

- `agent:<agentId>:slack:slash:<userId>`

また、コマンド実行は引き続き対象のconversation session（`CommandTargetSessionKey`）に対してルーティングされます。

## インタラクティブ返信

Slackはエージェント作成のインタラクティブ返信コントロールをレンダリングできますが、この機能はデフォルトで無効です。

全体で有効にするには:

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

または、1つのSlackアカウントだけで有効にするには:

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

有効にすると、エージェントはSlack専用の返信ディレクティブを出力できます:

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

これらのディレクティブはSlack Block Kitにコンパイルされ、クリックまたは選択が既存のSlack interaction eventパスを通じて戻されます。

注意:

- これはSlack固有のUIです。他のチャンネルではSlack Block Kitディレクティブをそれぞれのボタンシステムに変換しません。
- インタラクティブコールバック値は、エージェントが生で作成した値ではなく、OpenClawが生成するopaque tokenです。
- 生成されたインタラクティブブロックがSlack Block Kitの制限を超える場合、OpenClawは無効なblocksペイロードを送る代わりに元のテキスト返信へフォールバックします。

## Slackでのexec承認

Slackは、Web UIやターミナルにフォールバックする代わりに、インタラクティブボタンとinteractionを備えたネイティブ承認クライアントとして動作できます。

- ネイティブDM/チャンネルルーティングには `channels.slack.execApprovals.*` を使用します。
- リクエストがすでにSlackに届いていて承認ID種別が `plugin:` の場合、plugin承認も同じSlackネイティブのボタンUI経由で解決できます。
- 承認者の認可は引き続き強制されます。Slack経由でリクエストを承認または拒否できるのは、承認者として識別されたユーザーのみです。

これは他チャンネルと同じ共有承認ボタンUIを使用します。Slackアプリ設定で `interactivity` が有効な場合、承認プロンプトは会話内に直接Block Kitボタンとして表示されます。
これらのボタンが存在する場合、それらが主要な承認UXになります。OpenClawは、ツール結果がチャット承認を利用不可と示す場合、または手動承認が唯一の経路である場合にのみ、手動の `/approve` コマンドを含めるべきです。

設定パス:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers`（任意。可能であれば `commands.ownerAllowFrom` にフォールバック）
- `channels.slack.execApprovals.target`（`dm` | `channel` | `both`、デフォルト: `dm`）
- `agentFilter`, `sessionFilter`

Slackは、`enabled` が未設定または `"auto"` で、少なくとも1人の承認者が解決されると、ネイティブexec承認を自動的に有効にします。Slackをネイティブ承認クライアントとして明示的に無効にするには `enabled: false` を設定します。
承認者が解決されるときにネイティブ承認を強制的に有効にするには `enabled: true` を設定します。

明示的なSlack exec承認設定がない場合のデフォルト動作:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

明示的なSlackネイティブ設定が必要なのは、承認者を上書きしたい場合、フィルターを追加したい場合、またはorigin-chat配信を有効にしたい場合のみです:

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

共有 `approvals.exec` 転送は別です。exec承認プロンプトを他のチャットや明示的な帯域外宛先にもルーティングする必要がある場合にのみ使用してください。共有 `approvals.plugin` 転送も別です。Slackネイティブボタンは、それらのリクエストがすでにSlackに届いている場合でもplugin承認を解決できます。

同一チャット内の `/approve` も、すでにコマンドをサポートしているSlackチャンネルとDMで動作します。完全な承認転送モデルについては、[Exec approvals](/ja-JP/tools/exec-approvals) を参照してください。

## イベントと運用動作

- メッセージ編集/削除/スレッドブロードキャストはsystem eventにマッピングされます。
- リアクション追加/削除イベントはsystem eventにマッピングされます。
- メンバー参加/退出、チャンネル作成/名前変更、ピン追加/削除イベントはsystem eventにマッピングされます。
- `channel_id_changed` は、`configWrites` が有効な場合にチャンネル設定キーを移行できます。
- チャンネルトピック/目的メタデータは信頼できないコンテキストとして扱われ、ルーティングコンテキストに注入されることがあります。
- スレッド開始者と初期スレッド履歴コンテキストのシーディングは、該当する場合、設定された送信者許可リストでフィルタリングされます。
- ブロックアクションとモーダルinteractionは、豊富なペイロードフィールドを持つ構造化された `Slack interaction: ...` system event を出力します:
  - ブロックアクション: 選択値、ラベル、picker値、`workflow_*` メタデータ
  - モーダル `view_submission` と `view_closed` イベント: ルーティングされたチャンネルメタデータとフォーム入力付き

## 設定リファレンスへのポインタ

主要リファレンス:

- [Configuration reference - Slack](/ja-JP/gateway/configuration-reference#slack)

  重要なSlackフィールド:
  - mode/auth: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DMアクセス: `dm.enabled`, `dmPolicy`, `allowFrom`（旧式: `dm.policy`, `dm.allowFrom`）、`dm.groupEnabled`, `dm.groupChannels`
  - 互換性トグル: `dangerouslyAllowNameMatching`（緊急時用。必要になるまで無効のままにしてください）
  - チャンネルアクセス: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - スレッド/履歴: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - 配信: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - 運用/機能: `configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## トラブルシューティング

<AccordionGroup>
  <Accordion title="チャンネルで返信がない">
    次の順で確認してください:

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

  <Accordion title="DMメッセージが無視される">
    次を確認してください:

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy`（または旧式の `channels.slack.dm.policy`）
    - ペアリング承認 / 許可リスト項目

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Socket modeが接続しない">
    bot tokenとapp token、およびSlackアプリ設定でのSocket Mode有効化を確認してください。

    `openclaw channels status --probe --json` で `botTokenStatus` または
    `appTokenStatus: "configured_unavailable"` が表示される場合、そのSlackアカウントは
    設定済みですが、現在のランタイムではSecretRefを使った値を
    解決できていません。

  </Accordion>

  <Accordion title="HTTP modeでイベントを受信しない">
    次を確認してください:

    - signing secret
    - webhookパス
    - Slack Request URLs（Events + Interactivity + Slash Commands）
    - HTTPアカウントごとの一意な `webhookPath`

    アカウントスナップショットに `signingSecretStatus: "configured_unavailable"` が
    表示される場合、そのHTTPアカウントは設定済みですが、現在のランタイムでは
    SecretRefを使ったsigning secretを解決できていません。

  </Accordion>

  <Accordion title="ネイティブ/スラッシュコマンドが発火しない">
    意図していた構成が次のどちらかを確認してください:

    - ネイティブコマンドモード（`channels.slack.commands.native: true`）で、対応するスラッシュコマンドがSlackに登録されている
    - または単一スラッシュコマンドモード（`channels.slack.slashCommand.enabled: true`）

    あわせて `commands.useAccessGroups` とチャンネル/ユーザー許可リストも確認してください。

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
