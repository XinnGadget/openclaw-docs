---
read_when:
    - Slack のセットアップ、または Slack のソケット/HTTP モードのデバッグ
summary: Slack のセットアップと実行時の挙動（Socket Mode + HTTP リクエスト URL）
title: Slack
x-i18n:
    generated_at: "2026-04-12T23:28:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4b80c1a612b8815c46c675b688639c207a481f367075996dde3858a83637313b
    source_path: channels/slack.md
    workflow: 15
---

# Slack

ステータス: Slack アプリ統合による DM とチャンネルに対応した本番運用対応。デフォルト モードは Socket Mode で、HTTP リクエスト URL にも対応しています。

<CardGroup cols={3}>
  <Card title="ペアリング" icon="link" href="/ja-JP/channels/pairing">
    Slack DM はデフォルトでペアリング モードです。
  </Card>
  <Card title="スラッシュコマンド" icon="terminal" href="/ja-JP/tools/slash-commands">
    ネイティブ コマンドの挙動とコマンド カタログ。
  </Card>
  <Card title="チャンネルのトラブルシューティング" icon="wrench" href="/ja-JP/channels/troubleshooting">
    チャンネル横断の診断と修復プレイブック。
  </Card>
</CardGroup>

## クイックセットアップ

<Tabs>
  <Tab title="Socket Mode（デフォルト）">
    <Steps>
      <Step title="新しい Slack アプリを作成する">
        Slack アプリ設定で **[Create New App](https://api.slack.com/apps/new)** ボタンを押します:

        - **from a manifest** を選択し、アプリ用のワークスペースを選びます
        - 以下の [マニフェスト例](#manifest-and-scope-checklist) を貼り付け、そのまま作成を続行します
        - `connections:write` を付けた **App-Level Token** (`xapp-...`) を生成します
        - アプリをインストールし、表示される **Bot Token** (`xoxb-...`) をコピーします
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

        環境変数フォールバック（デフォルト アカウントのみ）:

```bash
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
```

      </Step>

      <Step title="Gateway を起動する">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP リクエスト URL">
    <Steps>
      <Step title="新しい Slack アプリを作成する">
        Slack アプリ設定で **[Create New App](https://api.slack.com/apps/new)** ボタンを押します:

        - **from a manifest** を選択し、アプリ用のワークスペースを選びます
        - [マニフェスト例](#manifest-and-scope-checklist) を貼り付け、作成前に URL を更新します
        - リクエスト検証用に **Signing Secret** を保存します
        - アプリをインストールし、表示される **Bot Token** (`xoxb-...`) をコピーします

      </Step>

      <Step title="OpenClaw を設定する">

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
        マルチアカウント HTTP では一意の webhook パスを使用します

        登録が衝突しないよう、各アカウントに別々の `webhookPath`（デフォルトは `/slack/events`）を指定してください。
        </Note>

      </Step>

      <Step title="Gateway を起動する">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>
</Tabs>

## マニフェストとスコープのチェックリスト

<Tabs>
  <Tab title="Socket Mode（デフォルト）">

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

  <Tab title="HTTP リクエスト URL">

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

### 追加のマニフェスト設定

上記のデフォルトを拡張するさまざまな機能を表に出します。

<AccordionGroup>
  <Accordion title="オプションのネイティブ スラッシュコマンド">

    1 つの設定済みコマンドの代わりに、ニュアンスを伴って複数の [ネイティブ スラッシュコマンド](#commands-and-slash-behavior) を使用できます:

    - `/status` コマンドは予約済みのため、`/status` ではなく `/agentstatus` を使用します。
    - 一度に利用可能にできるスラッシュコマンドは 25 個までです。

    既存の `features.slash_commands` セクションを、[利用可能なコマンド](/ja-JP/tools/slash-commands#command-list) のサブセットで置き換えます:

    <Tabs>
      <Tab title="Socket Mode（デフォルト）">

```json
    "slash_commands": [
      {
        "command": "/new",
        "description": "Start a new session",
        "usage_hint": "[model]"
      },
      {
        "command": "/reset",
        "description": "Reset the current session"
      },
      {
        "command": "/compact",
        "description": "Compact the session context",
        "usage_hint": "[instructions]"
      },
      {
        "command": "/stop",
        "description": "Stop the current run"
      },
      {
        "command": "/session",
        "description": "Manage thread-binding expiry",
        "usage_hint": "idle <duration|off> or max-age <duration|off>"
      },
      {
        "command": "/think",
        "description": "Set the thinking level",
        "usage_hint": "<off|minimal|low|medium|high|xhigh>"
      },
      {
        "command": "/verbose",
        "description": "Toggle verbose output",
        "usage_hint": "on|off|full"
      },
      {
        "command": "/fast",
        "description": "Show or set fast mode",
        "usage_hint": "[status|on|off]"
      },
      {
        "command": "/reasoning",
        "description": "Toggle reasoning visibility",
        "usage_hint": "[on|off|stream]"
      },
      {
        "command": "/elevated",
        "description": "Toggle elevated mode",
        "usage_hint": "[on|off|ask|full]"
      },
      {
        "command": "/exec",
        "description": "Show or set exec defaults",
        "usage_hint": "host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>"
      },
      {
        "command": "/model",
        "description": "Show or set the model",
        "usage_hint": "[name|#|status]"
      },
      {
        "command": "/models",
        "description": "List providers or models for a provider",
        "usage_hint": "[provider] [page] [limit=<n>|size=<n>|all]"
      },
      {
        "command": "/help",
        "description": "Show the short help summary"
      },
      {
        "command": "/commands",
        "description": "Show the generated command catalog"
      },
      {
        "command": "/tools",
        "description": "Show what the current agent can use right now",
        "usage_hint": "[compact|verbose]"
      },
      {
        "command": "/agentstatus",
        "description": "Show runtime status, including provider usage/quota when available"
      },
      {
        "command": "/tasks",
        "description": "List active/recent background tasks for the current session"
      },
      {
        "command": "/context",
        "description": "Explain how context is assembled",
        "usage_hint": "[list|detail|json]"
      },
      {
        "command": "/whoami",
        "description": "Show your sender identity"
      },
      {
        "command": "/skill",
        "description": "Run a skill by name",
        "usage_hint": "<name> [input]"
      },
      {
        "command": "/btw",
        "description": "Ask a side question without changing session context",
        "usage_hint": "<question>"
      },
      {
        "command": "/usage",
        "description": "Control the usage footer or show cost summary",
        "usage_hint": "off|tokens|full|cost"
      }
    ]
```

      </Tab>
      <Tab title="HTTP リクエスト URL">

```json
    "slash_commands": [
      {
        "command": "/new",
        "description": "新しいセッションを開始する",
        "usage_hint": "[model]",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/reset",
        "description": "現在のセッションをリセットする",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/compact",
        "description": "セッション コンテキストを Compaction する",
        "usage_hint": "[instructions]",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/stop",
        "description": "現在の実行を停止する",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/session",
        "description": "スレッド バインディングの有効期限を管理する",
        "usage_hint": "idle <duration|off> または max-age <duration|off>",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/think",
        "description": "思考レベルを設定する",
        "usage_hint": "<off|minimal|low|medium|high|xhigh>",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/verbose",
        "description": "詳細出力を切り替える",
        "usage_hint": "on|off|full",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/fast",
        "description": "高速モードを表示または設定する",
        "usage_hint": "[status|on|off]",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/reasoning",
        "description": "reasoning の表示を切り替える",
        "usage_hint": "[on|off|stream]",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/elevated",
        "description": "昇格モードを切り替える",
        "usage_hint": "[on|off|ask|full]",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/exec",
        "description": "exec のデフォルトを表示または設定する",
        "usage_hint": "host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/model",
        "description": "モデルを表示または設定する",
        "usage_hint": "[name|#|status]",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/models",
        "description": "プロバイダーを一覧表示する、またはプロバイダーのモデルを一覧表示する",
        "usage_hint": "[provider] [page] [limit=<n>|size=<n>|all]",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/help",
        "description": "短いヘルプ要約を表示する",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/commands",
        "description": "生成されたコマンド カタログを表示する",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/tools",
        "description": "現在のエージェントが今使えるものを表示する",
        "usage_hint": "[compact|verbose]",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/agentstatus",
        "description": "利用可能な場合はプロバイダーの使用量/クォータを含む実行時ステータスを表示する",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/tasks",
        "description": "現在のセッションのアクティブな/最近のバックグラウンド タスクを一覧表示する",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/context",
        "description": "コンテキストがどのように組み立てられるかを説明する",
        "usage_hint": "[list|detail|json]",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/whoami",
        "description": "送信者 ID を表示する",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/skill",
        "description": "名前で Skills を実行する",
        "usage_hint": "<name> [input]",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/btw",
        "description": "セッション コンテキストを変更せずに補足の質問をする",
        "usage_hint": "<question>",
        "url": "https://gateway-host.example.com/slack/events"
      },
      {
        "command": "/usage",
        "description": "使用量フッターを制御する、またはコスト概要を表示する",
        "usage_hint": "off|tokens|full|cost",
        "url": "https://gateway-host.example.com/slack/events"
      }
    ]
```

      </Tab>
    </Tabs>

  </Accordion>
  <Accordion title="オプションの作成者スコープ（書き込み操作）">
    送信メッセージでデフォルトの Slack アプリ ID ではなく、アクティブなエージェント ID（カスタム ユーザー名とアイコン）を使いたい場合は、`chat:write.customize` bot スコープを追加します。

    絵文字アイコンを使う場合、Slack では `:emoji_name:` 構文が必要です。

  </Accordion>
  <Accordion title="オプションのユーザー トークン スコープ（読み取り操作）">
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

## トークン モデル

- Socket Mode には `botToken` + `appToken` が必要です。
- HTTP モードには `botToken` + `signingSecret` が必要です。
- `botToken`、`appToken`、`signingSecret`、`userToken` はプレーンテキストの
  文字列または SecretRef オブジェクトを受け付けます。
- config のトークンは env フォールバックより優先されます。
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` の env フォールバックはデフォルト アカウントにのみ適用されます。
- `userToken` (`xoxp-...`) は config 専用です（env フォールバックなし）。デフォルトでは読み取り専用動作（`userTokenReadOnly: true`）になります。

ステータス スナップショットの挙動:

- Slack アカウントの検査では、認証情報ごとの `*Source` と `*Status`
  フィールド（`botToken`、`appToken`、`signingSecret`、`userToken`）を追跡します。
- ステータスは `available`、`configured_unavailable`、または `missing` です。
- `configured_unavailable` は、そのアカウントが SecretRef
  または別の非インラインなシークレット ソースで設定されているが、現在のコマンド/実行時パス
  では実際の値を解決できなかったことを意味します。
- HTTP モードでは `signingSecretStatus` が含まれます。Socket Mode では、
  必要な組み合わせは `botTokenStatus` + `appTokenStatus` です。

<Tip>
アクション/ディレクトリ読み取りでは、設定されていれば user token を優先できます。書き込みでは bot token が引き続き優先されます。user-token による書き込みは `userTokenReadOnly: false` で、かつ bot token が利用できない場合にのみ許可されます。
</Tip>

## アクションとゲート

Slack アクションは `channels.slack.actions.*` で制御されます。

現在の Slack ツールで利用可能なアクション グループ:

| Group      | Default |
| ---------- | ------- |
| messages   | enabled |
| reactions  | enabled |
| pins       | enabled |
| memberInfo | enabled |
| emojiList  | enabled |

現在の Slack メッセージ アクションには `send`、`upload-file`、`download-file`、`read`、`edit`、`delete`、`pin`、`unpin`、`list-pins`、`member-info`、`emoji-list` が含まれます。

## アクセス制御とルーティング

<Tabs>
  <Tab title="DM ポリシー">
    `channels.slack.dmPolicy` は DM アクセスを制御します（レガシー: `channels.slack.dm.policy`）:

    - `pairing`（デフォルト）
    - `allowlist`
    - `open`（`channels.slack.allowFrom` に `"*"` を含める必要があります。レガシー: `channels.slack.dm.allowFrom`）
    - `disabled`

    DM フラグ:

    - `dm.enabled`（デフォルト true）
    - `channels.slack.allowFrom`（推奨）
    - `dm.allowFrom`（レガシー）
    - `dm.groupEnabled`（グループ DM はデフォルト false）
    - `dm.groupChannels`（オプションの MPIM 許可リスト）

    マルチアカウントの優先順位:

    - `channels.slack.accounts.default.allowFrom` は `default` アカウントにのみ適用されます。
    - 名前付きアカウントは、自身の `allowFrom` が未設定の場合に `channels.slack.allowFrom` を継承します。
    - 名前付きアカウントは `channels.slack.accounts.default.allowFrom` を継承しません。

    DM でのペアリングでは `openclaw pairing approve slack <code>` を使用します。

  </Tab>

  <Tab title="チャンネル ポリシー">
    `channels.slack.groupPolicy` はチャンネル処理を制御します:

    - `open`
    - `allowlist`
    - `disabled`

    チャンネル許可リストは `channels.slack.channels` の下にあり、安定したチャンネル ID を使う必要があります。

    実行時の注意: `channels.slack` が完全に存在しない場合（env のみのセットアップ）、実行時は `groupPolicy="allowlist"` にフォールバックし、警告をログに出します（`channels.defaults.groupPolicy` が設定されていても同様です）。

    名前/ID 解決:

    - チャンネル許可リストのエントリと DM 許可リストのエントリは、トークン アクセスが許可されていれば起動時に解決されます
    - 未解決のチャンネル名エントリは設定どおり保持されますが、デフォルトではルーティングで無視されます
    - 受信認可とチャンネル ルーティングはデフォルトで ID 優先です。ユーザー名/スラッグの直接一致には `channels.slack.dangerouslyAllowNameMatching: true` が必要です

  </Tab>

  <Tab title="メンションとチャンネル ユーザー">
    チャンネル メッセージはデフォルトでメンション ゲート付きです。

    メンション ソース:

    - 明示的なアプリ メンション（`<@botId>`）
    - メンション正規表現パターン（`agents.list[].groupChat.mentionPatterns`、フォールバックは `messages.groupChat.mentionPatterns`）
    - 暗黙の bot 返信スレッド挙動（`thread.requireExplicitMention` が `true` の場合は無効）

    チャンネルごとの制御（`channels.slack.channels.<id>`。名前は起動時解決または `dangerouslyAllowNameMatching` 経由のみ）:

    - `requireMention`
    - `users`（許可リスト）
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - `toolsBySender` のキー形式: `id:`、`e164:`、`username:`、`name:`、または `"*"` ワイルドカード
      （レガシーの接頭辞なしキーも引き続き `id:` のみにマップされます）

  </Tab>
</Tabs>

## スレッド、セッション、返信タグ

- DM は `direct` としてルーティングされ、チャンネルは `channel`、MPIM は `group` としてルーティングされます。
- デフォルトの `session.dmScope=main` では、Slack DM はエージェントのメイン セッションに集約されます。
- チャンネル セッション: `agent:<agentId>:slack:channel:<channelId>`。
- スレッド返信では、該当する場合にスレッド セッション接尾辞（`:thread:<threadTs>`）が作成されることがあります。
- `channels.slack.thread.historyScope` のデフォルトは `thread`、`thread.inheritParent` のデフォルトは `false` です。
- `channels.slack.thread.initialHistoryLimit` は、新しいスレッド セッション開始時に取得する既存スレッド メッセージ数を制御します（デフォルトは `20`、無効化するには `0` に設定）。
- `channels.slack.thread.requireExplicitMention`（デフォルト `false`）: `true` の場合、暗黙のスレッド メンションを抑制し、bot がすでにそのスレッドに参加していても、スレッド内の明示的な `@bot` メンションにのみ応答します。これがない場合、bot が参加したスレッド内の返信は `requireMention` ゲートをバイパスします。

返信スレッド制御:

- `channels.slack.replyToMode`: `off|first|all|batched`（デフォルト `off`）
- `channels.slack.replyToModeByChatType`: `direct|group|channel` ごと
- ダイレクト チャット向けのレガシー フォールバック: `channels.slack.dm.replyToMode`

手動返信タグに対応しています:

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

注意: `replyToMode="off"` は、明示的な `[[reply_to_*]]` タグを含め、Slack の**すべて**の返信スレッドを無効にします。これは Telegram と異なり、Telegram では `"off"` モードでも明示的タグが引き続き尊重されます。この違いはプラットフォームのスレッド モデルを反映しています。Slack のスレッドはチャンネルからメッセージを隠しますが、Telegram の返信はメインのチャット フロー内で表示されたままです。

## Ack reaction

`ackReaction` は、OpenClaw が受信メッセージを処理している間、確認用の絵文字を送信します。

解決順序:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- エージェント ID の絵文字フォールバック（`agents.list[].identity.emoji`、なければ `"👀"`）

注意:

- Slack では shortcode（たとえば `"eyes"`）が必要です。
- Slack アカウント単位またはグローバルでリアクションを無効化するには `""` を使用します。

## テキスト ストリーミング

`channels.slack.streaming` はライブ プレビューの挙動を制御します:

- `off`: ライブ プレビュー ストリーミングを無効にします。
- `partial`（デフォルト）: プレビュー テキストを最新の部分出力で置き換えます。
- `block`: チャンク化されたプレビュー更新を追記します。
- `progress`: 生成中は進捗ステータス テキストを表示し、その後に最終テキストを送信します。

`channels.slack.streaming.nativeTransport` は、`channels.slack.streaming.mode` が `partial` のときの Slack ネイティブ テキスト ストリーミングを制御します（デフォルト: `true`）。

- Slack ネイティブ テキスト ストリーミングと Slack assistant のスレッド ステータスを表示するには、返信スレッドが利用可能である必要があります。スレッド選択は引き続き `replyToMode` に従います。
- チャンネルおよびグループ チャットのルートでは、ネイティブ ストリーミングが利用できない場合でも通常のドラフト プレビューを使用できます。
- トップレベルの Slack DM はデフォルトでスレッド外のままなので、スレッド スタイルのプレビューは表示されません。そこで進捗を見せたい場合は、スレッド返信または `typingReaction` を使用してください。
- メディアおよび非テキスト ペイロードは通常配信にフォールバックします。
- 返信の途中でストリーミングに失敗した場合、OpenClaw は残りのペイロードについて通常配信にフォールバックします。

Slack ネイティブ テキスト ストリーミングの代わりにドラフト プレビューを使用するには:

```json5
{
  channels: {
    slack: {
      streaming: {
        mode: "partial",
        nativeTransport: false,
      },
    },
  },
}
```

レガシー キー:

- `channels.slack.streamMode`（`replace | status_final | append`）は自動的に `channels.slack.streaming.mode` に移行されます。
- 真偽値の `channels.slack.streaming` は自動的に `channels.slack.streaming.mode` と `channels.slack.streaming.nativeTransport` に移行されます。
- レガシーの `channels.slack.nativeStreaming` は自動的に `channels.slack.streaming.nativeTransport` に移行されます。

## Typing reaction フォールバック

`typingReaction` は、OpenClaw が返信を処理している間、受信した Slack メッセージに一時的なリアクションを追加し、実行完了時にそれを削除します。これは、デフォルトの「入力中...」ステータス インジケーターを使うスレッド返信の外で特に有用です。

解決順序:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

注意:

- Slack では shortcode（たとえば `"hourglass_flowing_sand"`）が必要です。
- このリアクションはベストエフォートであり、返信または失敗パスの完了後に自動クリーンアップが試行されます。

## メディア、チャンク化、配信

<AccordionGroup>
  <Accordion title="受信添付ファイル">
    Slack のファイル添付は、Slack がホストするプライベート URL からダウンロードされ（トークン認証付きリクエスト フロー）、取得に成功し、サイズ制限内であればメディア ストアに書き込まれます。

    実行時の受信サイズ上限は、`channels.slack.mediaMaxMb` で上書きしない限り、デフォルトで `20MB` です。

  </Accordion>

  <Accordion title="送信テキストとファイル">
    - テキスト チャンクには `channels.slack.textChunkLimit`（デフォルト 4000）を使用します
    - `channels.slack.chunkMode="newline"` で段落優先の分割が有効になります
    - ファイル送信では Slack のアップロード API を使用し、スレッド返信（`thread_ts`）を含めることができます
    - 送信メディアの上限は、設定されていれば `channels.slack.mediaMaxMb` に従います。未設定の場合、チャンネル送信ではメディア パイプラインの MIME 種別デフォルトを使用します
  </Accordion>

  <Accordion title="配信先">
    推奨される明示的な送信先:

    - DM には `user:<id>`
    - チャンネルには `channel:<id>`

    Slack DM は、ユーザー宛てに送信する際に Slack の conversation API を通じて開かれます。

  </Accordion>
</AccordionGroup>

## コマンドとスラッシュの挙動

スラッシュコマンドは、Slack では 1 つの設定済みコマンド、または複数のネイティブ コマンドとして表示されます。コマンド デフォルトを変更するには `channels.slack.slashCommand` を設定します:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

```txt
/openclaw /help
```

ネイティブ コマンドには、Slack アプリでの [追加のマニフェスト設定](#additional-manifest-settings) が必要で、代わりに `channels.slack.commands.native: true` またはグローバル設定の `commands.native: true` で有効化します。

- Slack ではネイティブ コマンドの自動モードは**オフ**のため、`commands.native: "auto"` では Slack ネイティブ コマンドは有効になりません。

```txt
/help
```

ネイティブ引数メニューは、選択したオプション値をディスパッチする前に確認モーダルを表示する適応型レンダリング戦略を使用します:

- 最大 5 個のオプション: ボタン ブロック
- 6〜100 個のオプション: static select メニュー
- 100 個を超える場合: interactivity のオプション ハンドラーが利用可能なら、非同期オプション フィルタリング付き external select
- Slack の制限を超えた場合: エンコードされたオプション値はボタンにフォールバックします

```txt
/think
```

スラッシュ セッションは `agent:<agentId>:slack:slash:<userId>` のような分離キーを使用しつつ、コマンド実行自体は `CommandTargetSessionKey` を使って対象の会話セッションへルーティングします。

## インタラクティブ返信

Slack はエージェント作成のインタラクティブ返信コントロールをレンダリングできますが、この機能はデフォルトで無効です。

グローバルに有効化するには:

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

または、1 つの Slack アカウントに対してのみ有効化するには:

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

これらのディレクティブは Slack Block Kit にコンパイルされ、クリックまたは選択は既存の Slack interaction イベント パスを通じて返送されます。

注意:

- これは Slack 固有の UI です。他のチャンネルでは Slack Block Kit ディレクティブを独自のボタン システムに変換しません。
- インタラクティブ コールバック値は OpenClaw が生成する不透明トークンであり、エージェントが生の値を書いたものではありません。
- 生成されたインタラクティブ ブロックが Slack Block Kit の制限を超える場合、OpenClaw は無効な blocks ペイロードを送信する代わりに元のテキスト返信へフォールバックします。

## Slack での Exec 承認

Slack は、Web UI やターミナルにフォールバックする代わりに、インタラクティブ ボタンと interaction を備えたネイティブ承認クライアントとして動作できます。

- Exec 承認では、ネイティブ DM/チャンネル ルーティングに `channels.slack.execApprovals.*` を使用します。
- Plugin 承認も、リクエストがすでに Slack に届いており、承認 ID 種別が `plugin:` の場合は、同じ Slack ネイティブ ボタン画面で解決できます。
- 承認者の認可は引き続き適用されます。Slack 経由でリクエストを承認または拒否できるのは、承認者として識別されたユーザーのみです。

これは他チャンネルと同じ共有承認ボタン画面を使用します。Slack アプリ設定で `interactivity` が有効な場合、承認プロンプトは会話内に Block Kit ボタンとして直接レンダリングされます。
それらのボタンが存在する場合、それが主要な承認 UX です。OpenClaw は、
ツール結果がチャット承認を利用不可と示す場合、または手動承認が唯一の経路である場合にのみ、手動の `/approve` コマンドを含めるべきです。

設定パス:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers`（オプション。可能なら `commands.ownerAllowFrom` にフォールバック）
- `channels.slack.execApprovals.target`（`dm` | `channel` | `both`、デフォルト: `dm`）
- `agentFilter`, `sessionFilter`

少なくとも 1 人の
承認者が解決される場合、Slack は `enabled` が未設定または `"auto"` のときにネイティブ exec 承認を自動有効化します。Slack をネイティブ承認クライアントとして明示的に無効化するには `enabled: false` を設定します。
承認者が解決される場合にネイティブ承認を強制的に有効化するには `enabled: true` を設定します。

明示的な Slack exec 承認設定がない場合のデフォルト動作:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

承認者を上書きしたい、フィルターを追加したい、または
送信元チャット配信にオプトインしたい場合にのみ、明示的な Slack ネイティブ設定が必要です:

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

共有の `approvals.exec` 転送は別物です。exec 承認プロンプトも
他のチャットや明示的な帯域外送信先へルーティングする必要がある場合にのみ使用してください。共有の `approvals.plugin` 転送も
別物です。Slack ネイティブ ボタンは、それらのリクエストがすでに Slack に届いている場合でも Plugin 承認を解決できます。

同一チャット内の `/approve` も、すでにコマンドに対応している Slack チャンネルと DM で動作します。完全な承認転送モデルについては [Exec approvals](/ja-JP/tools/exec-approvals) を参照してください。

## イベントと運用時の挙動

- メッセージの編集/削除/スレッド ブロードキャストは system event にマッピングされます。
- リアクションの追加/削除イベントは system event にマッピングされます。
- メンバーの参加/退出、チャンネルの作成/名前変更、ピンの追加/削除イベントは system event にマッピングされます。
- `channel_id_changed` は、`configWrites` が有効な場合にチャンネル設定キーを移行できます。
- チャンネル topic/purpose メタデータは信頼されていないコンテキストとして扱われ、ルーティング コンテキストに注入されることがあります。
- スレッド開始メッセージと初期スレッド履歴コンテキスト シーディングは、該当する場合、設定済み送信者許可リストでフィルタリングされます。
- Block action と modal interaction は、リッチなペイロード フィールドを持つ構造化された `Slack interaction: ...` system event を出力します:
  - block action: 選択値、ラベル、picker 値、`workflow_*` メタデータ
  - modal の `view_submission` および `view_closed` イベント。ルーティングされたチャンネル メタデータとフォーム入力を含みます

## 設定リファレンスへのポインター

主要リファレンス:

- [設定リファレンス - Slack](/ja-JP/gateway/configuration-reference#slack)

  シグナルの高い Slack フィールド:
  - モード/認証: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DM アクセス: `dm.enabled`, `dmPolicy`, `allowFrom`（レガシー: `dm.policy`, `dm.allowFrom`）, `dm.groupEnabled`, `dm.groupChannels`
  - 互換性トグル: `dangerouslyAllowNameMatching`（緊急用。必要になるまでオフのままにしてください）
  - チャンネル アクセス: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - スレッド/履歴: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - 配信: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `streaming.nativeTransport`
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
    次を確認してください:

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy`（またはレガシーの `channels.slack.dm.policy`）
    - ペアリング承認 / 許可リスト エントリ

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Socket mode が接続しない">
    bot トークン + app トークン、および Slack アプリ設定での Socket Mode 有効化を確認してください。

    `openclaw channels status --probe --json` に `botTokenStatus` または
    `appTokenStatus: "configured_unavailable"` が表示される場合、その Slack アカウントは
    設定済みですが、現在の実行時が SecretRef に支えられた
    値を解決できていません。

  </Accordion>

  <Accordion title="HTTP mode でイベントを受信しない">
    次を確認してください:

    - signing secret
    - webhook path
    - Slack Request URLs（Events + Interactivity + Slash Commands）
    - HTTP アカウントごとに一意の `webhookPath`

    アカウント
    スナップショットに `signingSecretStatus: "configured_unavailable"` が表示される場合、その HTTP アカウントは設定済みですが、現在の実行時が
    SecretRef に支えられた signing secret を解決できていません。

  </Accordion>

  <Accordion title="ネイティブ/スラッシュコマンドが発火しない">
    意図したものが次のどちらかを確認してください:

    - ネイティブ コマンド モード（`channels.slack.commands.native: true`）で、Slack に一致するスラッシュコマンドが登録されている
    - または単一スラッシュコマンド モード（`channels.slack.slashCommand.enabled: true`）

    あわせて `commands.useAccessGroups` とチャンネル/ユーザー許可リストも確認してください。

  </Accordion>
</AccordionGroup>

## 関連項目

- [ペアリング](/ja-JP/channels/pairing)
- [グループ](/ja-JP/channels/groups)
- [セキュリティ](/ja-JP/gateway/security)
- [チャンネル ルーティング](/ja-JP/channels/channel-routing)
- [トラブルシューティング](/ja-JP/channels/troubleshooting)
- [設定](/ja-JP/gateway/configuration)
- [スラッシュコマンド](/ja-JP/tools/slash-commands)
