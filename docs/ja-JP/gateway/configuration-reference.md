---
read_when:
    - 正確なフィールド単位の設定の意味やデフォルト値が必要
    - チャンネル、モデル、Gateway、またはツールの設定ブロックを検証している
summary: すべてのOpenClaw設定キー、デフォルト値、チャンネル設定の完全なリファレンス
title: 設定リファレンス
x-i18n:
    generated_at: "2026-04-08T02:19:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2c7991b948cbbb7954a3e26280089ab00088e7f4878ec0b0540c3c9acf222ebb
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# 設定リファレンス

`~/.openclaw/openclaw.json` で利用できるすべてのフィールド。タスク指向の概要については、[Configuration](/ja-JP/gateway/configuration) を参照してください。

設定形式は **JSON5** です（コメントと末尾カンマを許可）。すべてのフィールドは省略可能で、省略した場合はOpenClawが安全なデフォルト値を使用します。

---

## チャンネル

各チャンネルは、その設定セクションが存在すると自動的に開始されます（`enabled: false` の場合を除く）。

### DM とグループのアクセス

すべてのチャンネルはDMポリシーとグループポリシーをサポートします。

| DM policy           | 動作                                                             |
| ------------------- | ---------------------------------------------------------------- |
| `pairing` (default) | 未知の送信者には一度だけのペアリングコードが送られ、所有者の承認が必要 |
| `allowlist`         | `allowFrom` 内の送信者のみ許可（またはペア済みの許可ストア）      |
| `open`              | すべての受信DMを許可（`allowFrom: ["*"]` が必要）                 |
| `disabled`          | すべての受信DMを無視                                             |

| Group policy          | 動作                                                       |
| --------------------- | ---------------------------------------------------------- |
| `allowlist` (default) | 設定された許可リストに一致するグループのみ                 |
| `open`                | グループ許可リストをバイパス（メンションゲートは引き続き適用） |
| `disabled`            | すべてのグループ/ルームメッセージをブロック                |

<Note>
`channels.defaults.groupPolicy` は、プロバイダーの `groupPolicy` が未設定のときのデフォルトを設定します。
ペアリングコードの有効期限は1時間です。保留中のDMペアリングリクエストは**チャンネルごとに3件**までです。
プロバイダーブロックが完全に存在しない場合（`channels.<provider>` がない場合）、実行時のグループポリシーは起動時警告付きで `allowlist`（フェイルクローズ）にフォールバックします。
</Note>

### チャンネルごとのモデル上書き

`channels.modelByChannel` を使うと、特定のチャンネルIDを特定のモデルに固定できます。値には `provider/model` または設定済みのモデルエイリアスを指定できます。このチャンネルマッピングは、セッションにすでにモデル上書きが存在しない場合（たとえば `/model` で設定された場合）に適用されます。

```json5
{
  channels: {
    modelByChannel: {
      discord: {
        "123456789012345678": "anthropic/claude-opus-4-6",
      },
      slack: {
        C1234567890: "openai/gpt-4.1",
      },
      telegram: {
        "-1001234567890": "openai/gpt-4.1-mini",
        "-1001234567890:topic:99": "anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

### チャンネルのデフォルトとハートビート

プロバイダー間で共有するグループポリシーとハートビート動作には `channels.defaults` を使用します。

```json5
{
  channels: {
    defaults: {
      groupPolicy: "allowlist", // open | allowlist | disabled
      contextVisibility: "all", // all | allowlist | allowlist_quote
      heartbeat: {
        showOk: false,
        showAlerts: true,
        useIndicator: true,
      },
    },
  },
}
```

- `channels.defaults.groupPolicy`: プロバイダーレベルの `groupPolicy` が未設定のときのフォールバックグループポリシー。
- `channels.defaults.contextVisibility`: すべてのチャンネルの補足コンテキスト表示モードのデフォルト。値: `all`（デフォルト、引用/スレッド/履歴のすべてのコンテキストを含む）、`allowlist`（許可リストにある送信者のコンテキストのみ含む）、`allowlist_quote`（allowlist と同じだが明示的な引用/返信コンテキストは保持）。チャンネルごとの上書き: `channels.<channel>.contextVisibility`。
- `channels.defaults.heartbeat.showOk`: ハートビート出力に正常なチャンネル状態を含めます。
- `channels.defaults.heartbeat.showAlerts`: ハートビート出力に劣化/エラー状態を含めます。
- `channels.defaults.heartbeat.useIndicator`: コンパクトなインジケータ形式のハートビート出力を表示します。

### WhatsApp

WhatsApp は Gateway の web チャンネル（Baileys Web）を通じて動作します。リンク済みセッションが存在すると自動的に開始されます。

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // blue ticks (false in self-chat mode)
      groups: {
        "*": { requireMention: true },
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
  web: {
    enabled: true,
    heartbeatSeconds: 60,
    reconnect: {
      initialMs: 2000,
      maxMs: 120000,
      factor: 1.4,
      jitter: 0.2,
      maxAttempts: 0,
    },
  },
}
```

<Accordion title="マルチアカウント WhatsApp">

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: {},
        personal: {},
        biz: {
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

- 送信コマンドは、`default` アカウントが存在する場合はそれを、そうでなければ最初に設定されたアカウントID（ソート済み）をデフォルトにします。
- オプションの `channels.whatsapp.defaultAccount` は、設定済みアカウントIDに一致する場合、このフォールバックのデフォルトアカウント選択を上書きします。
- 従来の単一アカウント Baileys 認証ディレクトリは、`openclaw doctor` によって `whatsapp/default` に移行されます。
- アカウントごとの上書き: `channels.whatsapp.accounts.<id>.sendReadReceipts`、`channels.whatsapp.accounts.<id>.dmPolicy`、`channels.whatsapp.accounts.<id>.allowFrom`。

</Accordion>

### Telegram

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groups: {
        "*": { requireMention: true },
        "-1001234567890": {
          allowFrom: ["@admin"],
          systemPrompt: "Keep answers brief.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Stay on topic.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" },
      ],
      historyLimit: 50,
      replyToMode: "first", // off | first | all | batched
      linkPreview: true,
      streaming: "partial", // off | partial | block | progress (default: off; opt in explicitly to avoid preview-edit rate limits)
      actions: { reactions: true, sendMessage: true },
      reactionNotifications: "own", // off | own | all
      mediaMaxMb: 100,
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: {
        autoSelectFamily: true,
        dnsResultOrder: "ipv4first",
      },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

- Botトークン: `channels.telegram.botToken` または `channels.telegram.tokenFile`（通常ファイルのみ。シンボリックリンクは拒否）で、デフォルトアカウントのフォールバックとして `TELEGRAM_BOT_TOKEN` も使用できます。
- オプションの `channels.telegram.defaultAccount` は、設定済みアカウントIDに一致する場合、デフォルトアカウント選択を上書きします。
- マルチアカウント構成（2つ以上のアカウントID）では、フォールバックルーティングを避けるため明示的なデフォルト（`channels.telegram.defaultAccount` または `channels.telegram.accounts.default`）を設定してください。これが存在しないか無効な場合、`openclaw doctor` が警告します。
- `configWrites: false` は Telegram 起点の設定書き込み（supergroup ID 移行、`/config set|unset`）をブロックします。
- `type: "acp"` を持つトップレベルの `bindings[]` エントリは、フォーラムトピック用の永続的な ACP バインディングを設定します（`match.peer.id` には正規の `chatId:topic:topicId` を使用）。フィールドの意味は [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings) と共有されます。
- Telegram のストリームプレビューは `sendMessage` + `editMessageText` を使用します（ダイレクトチャットとグループチャットの両方で動作）。
- リトライポリシー: [Retry policy](/ja-JP/concepts/retry) を参照してください。

### Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 100,
      allowBots: false,
      actions: {
        reactions: true,
        stickers: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        roles: false,
        channelInfo: true,
        voiceStatus: true,
        events: true,
        moderation: false,
      },
      replyToMode: "off", // off | first | all | batched
      dmPolicy: "pairing",
      allowFrom: ["1234567890", "123456789012345678"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["openclaw-dm"] },
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
          ignoreOtherMentions: true,
          reactionNotifications: "own",
          users: ["987654321098765432"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["docs"],
              systemPrompt: "Short answers only.",
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length", // length | newline
      streaming: "off", // off | partial | block | progress (progress maps to partial on Discord)
      maxLinesPerMessage: 17,
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // opt-in for sessions_spawn({ thread: true })
      },
      voice: {
        enabled: true,
        autoJoin: [
          {
            guildId: "123456789012345678",
            channelId: "234567890123456789",
          },
        ],
        daveEncryption: true,
        decryptionFailureTolerance: 24,
        tts: {
          provider: "openai",
          openai: { voice: "alloy" },
        },
      },
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["987654321098765432"],
        agentFilter: ["default"],
        sessionFilter: ["discord:"],
        target: "dm", // dm | channel | both
        cleanupAfterResolve: false,
      },
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

- トークン: `channels.discord.token`。デフォルトアカウントのフォールバックとして `DISCORD_BOT_TOKEN` を使用します。
- 明示的な Discord `token` を指定する直接送信呼び出しでは、そのトークンが呼び出しに使われます。アカウントのリトライ/ポリシー設定は、アクティブな実行時スナップショット内の選択されたアカウントから引き続き取得されます。
- オプションの `channels.discord.defaultAccount` は、設定済みアカウントIDに一致する場合、デフォルトアカウント選択を上書きします。
- 配信ターゲットには `user:<id>`（DM）または `channel:<id>`（guild channel）を使用します。数値IDのみの指定は拒否されます。
- Guild slug は小文字で、スペースは `-` に置き換えられます。チャンネルキーは slug 化された名前（`#` なし）を使います。guild ID の使用を推奨します。
- bot 自身が投稿したメッセージはデフォルトで無視されます。`allowBots: true` で有効になります。`allowBots: "mentions"` を使うと、bot をメンションした bot メッセージのみ受け付けます（自分自身のメッセージは引き続き除外）。
- `channels.discord.guilds.<id>.ignoreOtherMentions`（およびチャンネル上書き）は、bot ではなく別のユーザーまたはロールに言及しているメッセージを破棄します（@everyone/@here は除く）。
- `maxLinesPerMessage`（デフォルト 17）は、2000文字未満でも縦長のメッセージを分割します。
- `channels.discord.threadBindings` は Discord のスレッドバインド型ルーティングを制御します。
  - `enabled`: スレッドバインドセッション機能の Discord 上書き（`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`、およびバインドされた配信/ルーティング）
  - `idleHours`: 非アクティブ時の自動 unfocus を時間単位で指定する Discord 上書き（`0` で無効）
  - `maxAgeHours`: ハード最大経過時間の Discord 上書き（時間単位、`0` で無効）
  - `spawnSubagentSessions`: `sessions_spawn({ thread: true })` の自動スレッド作成/バインドへのオプトインスイッチ
- `type: "acp"` を持つトップレベル `bindings[]` エントリは、チャンネルとスレッド用の永続 ACP バインディングを設定します（`match.peer.id` には channel/thread id を使用）。フィールドの意味は [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings) と共有されます。
- `channels.discord.ui.components.accentColor` は Discord components v2 コンテナのアクセントカラーを設定します。
- `channels.discord.voice` は Discord ボイスチャンネル会話と、任意の自動参加 + TTS 上書きを有効にします。
- `channels.discord.voice.daveEncryption` と `channels.discord.voice.decryptionFailureTolerance` は `@discordjs/voice` の DAVE オプションにそのまま渡されます（デフォルトは `true` と `24`）。
- さらに OpenClaw は、復号失敗が繰り返された後にボイスセッションを退出/再参加することで、音声受信の復旧も試みます。
- `channels.discord.streaming` は正規のストリームモードキーです。従来の `streamMode` とブール値 `streaming` は自動移行されます。
- `channels.discord.autoPresence` は実行時の可用性を bot presence にマッピングします（healthy => online、degraded => idle、exhausted => dnd）。任意のステータステキスト上書きも可能です。
- `channels.discord.dangerouslyAllowNameMatching` は、変更可能な name/tag マッチングを再有効化します（緊急回避用の互換モード）。
- `channels.discord.execApprovals`: Discord ネイティブの exec 承認配信と承認者認可。
  - `enabled`: `true`、`false`、または `"auto"`（デフォルト）。auto モードでは、`approvers` または `commands.ownerAllowFrom` から承認者を解決できるときに exec 承認が有効になります。
  - `approvers`: exec リクエストを承認できる Discord ユーザーID。省略時は `commands.ownerAllowFrom` にフォールバックします。
  - `agentFilter`: オプションの agent ID 許可リスト。省略するとすべてのエージェントの承認を転送します。
  - `sessionFilter`: オプションのセッションキーパターン（部分文字列または正規表現）。
  - `target`: 承認プロンプトの送信先。`"dm"`（デフォルト）は承認者のDMに送信し、`"channel"` は元のチャンネルに送信し、`"both"` は両方に送信します。target に `"channel"` を含む場合、ボタンは解決済み承認者のみ利用できます。
  - `cleanupAfterResolve`: `true` の場合、承認、拒否、タイムアウト後に承認DMを削除します。

**リアクション通知モード:** `off`（なし）、`own`（bot のメッセージ、デフォルト）、`all`（すべてのメッセージ）、`allowlist`（`guilds.<id>.users` から、すべてのメッセージ）。

### Google Chat

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url", // app-url | project-number
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890",
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["users/1234567890"],
      },
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": { allow: true, requireMention: true },
      },
      actions: { reactions: true },
      typingIndicator: "message",
      mediaMaxMb: 20,
    },
  },
}
```

- サービスアカウント JSON: インライン（`serviceAccount`）またはファイルベース（`serviceAccountFile`）。
- サービスアカウント SecretRef（`serviceAccountRef`）もサポートされています。
- 環境変数フォールバック: `GOOGLE_CHAT_SERVICE_ACCOUNT` または `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`。
- 配信ターゲットには `spaces/<spaceId>` または `users/<userId>` を使用します。
- `channels.googlechat.dangerouslyAllowNameMatching` は、変更可能なメール principal マッチングを再有効化します（緊急回避用の互換モード）。

### Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",
      dmPolicy: "pairing",
      allowFrom: ["U123", "U456", "*"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["G123"] },
      channels: {
        C123: { allow: true, requireMention: true, allowBots: false },
        "#general": {
          allow: true,
          requireMention: true,
          allowBots: false,
          users: ["U123"],
          skills: ["docs"],
          systemPrompt: "Short answers only.",
        },
      },
      historyLimit: 50,
      allowBots: false,
      reactionNotifications: "own",
      reactionAllowlist: ["U123"],
      replyToMode: "off", // off | first | all | batched
      thread: {
        historyScope: "thread", // thread | channel
        inheritParent: false,
      },
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true,
      },
      slashCommand: {
        enabled: true,
        name: "openclaw",
        sessionPrefix: "slack:slash",
        ephemeral: true,
      },
      typingReaction: "hourglass_flowing_sand",
      textChunkLimit: 4000,
      chunkMode: "length",
      streaming: "partial", // off | partial | block | progress (preview mode)
      nativeStreaming: true, // use Slack native streaming API when streaming=partial
      mediaMaxMb: 20,
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["U123"],
        agentFilter: ["default"],
        sessionFilter: ["slack:"],
        target: "dm", // dm | channel | both
      },
    },
  },
}
```

- **Socket mode** には `botToken` と `appToken` の両方が必要です（デフォルトアカウントの環境変数フォールバックは `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN`）。
- **HTTP mode** には `botToken` と `signingSecret`（ルートまたはアカウントごと）が必要です。
- `botToken`、`appToken`、`signingSecret`、`userToken` は、プレーンテキスト文字列または SecretRef オブジェクトを受け付けます。
- Slack のアカウントスナップショットは、`botTokenSource`、`botTokenStatus`、`appTokenStatus`、HTTP mode では `signingSecretStatus` のような資格情報ごとの source/status フィールドを公開します。`configured_unavailable` は、そのアカウントが SecretRef 経由で設定されているが、現在のコマンド/実行時パスでは秘密値を解決できなかったことを意味します。
- `configWrites: false` は Slack 起点の設定書き込みをブロックします。
- オプションの `channels.slack.defaultAccount` は、設定済みアカウントIDに一致する場合、デフォルトアカウント選択を上書きします。
- `channels.slack.streaming` は正規のストリームモードキーです。従来の `streamMode` とブール値 `streaming` は自動移行されます。
- 配信ターゲットには `user:<id>`（DM）または `channel:<id>` を使用します。

**リアクション通知モード:** `off`、`own`（デフォルト）、`all`、`allowlist`（`reactionAllowlist` から）。

**スレッドセッション分離:** `thread.historyScope` はスレッドごと（デフォルト）またはチャンネル共有です。`thread.inheritParent` は親チャンネルの transcript を新しいスレッドにコピーします。

- `typingReaction` は返信実行中、受信した Slack メッセージに一時的なリアクションを追加し、完了時に削除します。`"hourglass_flowing_sand"` のような Slack 絵文字 shortcode を使用してください。
- `channels.slack.execApprovals`: Slack ネイティブの exec 承認配信と承認者認可。スキーマは Discord と同じです: `enabled`（`true`/`false`/`"auto"`）、`approvers`（Slack ユーザーID）、`agentFilter`、`sessionFilter`、`target`（`"dm"`、`"channel"`、または `"both"`）。

| Action group | デフォルト | 注記                   |
| ------------ | ---------- | ---------------------- |
| reactions    | enabled    | リアクション + 一覧表示 |
| messages     | enabled    | 読み取り/送信/編集/削除 |
| pins         | enabled    | ピン留め/解除/一覧     |
| memberInfo   | enabled    | メンバー情報           |
| emojiList    | enabled    | カスタム絵文字一覧     |

### Mattermost

Mattermost はプラグインとして提供されます: `openclaw plugins install @openclaw/mattermost`。

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
      chatmode: "oncall", // oncall | onmessage | onchar
      oncharPrefixes: [">", "!"],
      groups: {
        "*": { requireMention: true },
        "team-channel-id": { requireMention: false },
      },
      commands: {
        native: true, // opt-in
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // Optional explicit URL for reverse-proxy/public deployments
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

チャットモード: `oncall`（@メンション時に応答、デフォルト）、`onmessage`（すべてのメッセージ）、`onchar`（トリガープレフィックスで始まるメッセージ）。

Mattermost ネイティブコマンドが有効な場合:

- `commands.callbackPath` はパスである必要があります（例 `/api/channels/mattermost/command`）。完全なURLは不可です。
- `commands.callbackUrl` は OpenClaw Gateway エンドポイントを指し、Mattermost サーバーから到達可能である必要があります。
- ネイティブ slash callback は、slash command 登録時に Mattermost から返されるコマンドごとのトークンで認証されます。登録に失敗した場合、または有効化されたコマンドがない場合、OpenClaw は callback を `Unauthorized: invalid command token.` で拒否します。
- プライベート/tailnet/internal な callback host では、Mattermost が `ServiceSettings.AllowedUntrustedInternalConnections` に callback host/domain を含めることを求める場合があります。完全なURLではなく host/domain の値を使ってください。
- `channels.mattermost.configWrites`: Mattermost 起点の設定書き込みを許可または拒否します。
- `channels.mattermost.requireMention`: チャンネルで返信する前に `@mention` を要求します。
- `channels.mattermost.groups.<channelId>.requireMention`: チャンネルごとのメンションゲート上書き（デフォルトには `"*"`）。
- オプションの `channels.mattermost.defaultAccount` は、設定済みアカウントIDに一致する場合、デフォルトアカウント選択を上書きします。

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // optional account binding
      dmPolicy: "pairing",
      allowFrom: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      configWrites: true,
      reactionNotifications: "own", // off | own | all | allowlist
      reactionAllowlist: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      historyLimit: 50,
    },
  },
}
```

**リアクション通知モード:** `off`、`own`（デフォルト）、`all`、`allowlist`（`reactionAllowlist` から）。

- `channels.signal.account`: チャンネル起動を特定の Signal アカウント identity に固定します。
- `channels.signal.configWrites`: Signal 起点の設定書き込みを許可または拒否します。
- オプションの `channels.signal.defaultAccount` は、設定済みアカウントIDに一致する場合、デフォルトアカウント選択を上書きします。

### BlueBubbles

BlueBubbles は推奨される iMessage パスです（プラグインバックドで、`channels.bluebubbles` の下で設定します）。

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl, password, webhookPath, group controls, and advanced actions:
      // see /channels/bluebubbles
    },
  },
}
```

- ここで扱うコアキーパス: `channels.bluebubbles`、`channels.bluebubbles.dmPolicy`。
- オプションの `channels.bluebubbles.defaultAccount` は、設定済みアカウントIDに一致する場合、デフォルトアカウント選択を上書きします。
- `type: "acp"` を持つトップレベル `bindings[]` エントリは、BlueBubbles 会話を永続 ACP セッションにバインドできます。`match.peer.id` には BlueBubbles の handle または target string（`chat_id:*`、`chat_guid:*`、`chat_identifier:*`）を使用します。共有フィールドの意味: [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings)。
- 完全な BlueBubbles チャンネル設定は [BlueBubbles](/ja-JP/channels/bluebubbles) に記載されています。

### iMessage

OpenClaw は `imsg rpc`（stdio 上の JSON-RPC）を起動します。daemon や port は不要です。

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host",
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123"],
      historyLimit: 50,
      includeAttachments: false,
      attachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      remoteAttachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      mediaMaxMb: 16,
      service: "auto",
      region: "US",
    },
  },
}
```

- オプションの `channels.imessage.defaultAccount` は、設定済みアカウントIDに一致する場合、デフォルトアカウント選択を上書きします。

- Messages DB への Full Disk Access が必要です。
- `chat_id:<id>` ターゲットの使用を推奨します。チャット一覧は `imsg chats --limit 20` で取得できます。
- `cliPath` は SSH ラッパーを指すこともできます。SCP で添付ファイルを取得するには `remoteHost`（`host` または `user@host`）を設定してください。
- `attachmentRoots` と `remoteAttachmentRoots` は受信添付ファイルのパスを制限します（デフォルト: `/Users/*/Library/Messages/Attachments`）。
- SCP は strict host-key checking を使うため、中継ホストキーがすでに `~/.ssh/known_hosts` に存在している必要があります。
- `channels.imessage.configWrites`: iMessage 起点の設定書き込みを許可または拒否します。
- `type: "acp"` を持つトップレベル `bindings[]` エントリは、iMessage 会話を永続 ACP セッションにバインドできます。`match.peer.id` には正規化された handle または明示的な chat target（`chat_id:*`、`chat_guid:*`、`chat_identifier:*`）を使用します。共有フィールドの意味: [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings)。

<Accordion title="iMessage SSH ラッパーの例">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix は extension バックドで、`channels.matrix` の下で設定します。

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
      encryption: true,
      initialSyncLimit: 20,
      defaultAccount: "ops",
      accounts: {
        ops: {
          name: "Ops",
          userId: "@ops:example.org",
          accessToken: "syt_ops_xxx",
        },
        alerts: {
          userId: "@alerts:example.org",
          password: "secret",
          proxy: "http://127.0.0.1:7891",
        },
      },
    },
  },
}
```

- トークン認証には `accessToken`、パスワード認証には `userId` + `password` を使用します。
- `channels.matrix.proxy` は Matrix HTTP トラフィックを明示的な HTTP(S) proxy 経由にします。名前付きアカウントは `channels.matrix.accounts.<id>.proxy` で上書きできます。
- `channels.matrix.network.dangerouslyAllowPrivateNetwork` はプライベート/内部 homeserver を許可します。`proxy` とこのネットワークオプトインは独立した制御です。
- `channels.matrix.defaultAccount` はマルチアカウント構成で優先アカウントを選択します。
- `channels.matrix.autoJoin` のデフォルトは `off` なので、招待された room や新しい DM 形式の招待は、`autoJoin: "allowlist"` と `autoJoinAllowlist` を設定するか、`autoJoin: "always"` を設定するまで無視されます。
- `channels.matrix.execApprovals`: Matrix ネイティブの exec 承認配信と承認者認可。
  - `enabled`: `true`、`false`、または `"auto"`（デフォルト）。auto モードでは、`approvers` または `commands.ownerAllowFrom` から承認者を解決できるときに exec 承認が有効になります。
  - `approvers`: exec リクエストを承認できる Matrix ユーザーID（例 `@owner:example.org`）。
  - `agentFilter`: オプションの agent ID 許可リスト。省略するとすべてのエージェントの承認を転送します。
  - `sessionFilter`: オプションのセッションキーパターン（部分文字列または正規表現）。
  - `target`: 承認プロンプトの送信先。`"dm"`（デフォルト）、`"channel"`（元の room）、または `"both"`。
  - アカウントごとの上書き: `channels.matrix.accounts.<id>.execApprovals`。
- `channels.matrix.dm.sessionScope` は Matrix DM をどのようにセッションにまとめるかを制御します: `per-user`（デフォルト）はルーティングされた peer ごとに共有し、`per-room` は各 DM room を分離します。
- Matrix のステータス probe と live directory lookup は、実行時トラフィックと同じ proxy ポリシーを使用します。
- 完全な Matrix 設定、ターゲティング規則、セットアップ例は [Matrix](/ja-JP/channels/matrix) に記載されています。

### Microsoft Teams

Microsoft Teams は extension バックドで、`channels.msteams` の下で設定します。

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId, appPassword, tenantId, webhook, team/channel policies:
      // see /channels/msteams
    },
  },
}
```

- ここで扱うコアキーパス: `channels.msteams`、`channels.msteams.configWrites`。
- 完全な Teams 設定（資格情報、webhook、DM/グループポリシー、チーム/チャンネルごとの上書き）は [Microsoft Teams](/ja-JP/channels/msteams) に記載されています。

### IRC

IRC は extension バックドで、`channels.irc` の下で設定します。

```json5
{
  channels: {
    irc: {
      enabled: true,
      dmPolicy: "pairing",
      configWrites: true,
      nickserv: {
        enabled: true,
        service: "NickServ",
        password: "${IRC_NICKSERV_PASSWORD}",
        register: false,
        registerEmail: "bot@example.com",
      },
    },
  },
}
```

- ここで扱うコアキーパス: `channels.irc`、`channels.irc.dmPolicy`、`channels.irc.configWrites`、`channels.irc.nickserv.*`。
- オプションの `channels.irc.defaultAccount` は、設定済みアカウントIDに一致する場合、デフォルトアカウント選択を上書きします。
- 完全な IRC チャンネル設定（host/port/TLS/channels/allowlists/mention gating）は [IRC](/ja-JP/channels/irc) に記載されています。

### マルチアカウント（全チャンネル）

チャンネルごとに複数アカウントを実行します（それぞれ独自の `accountId` を持ちます）。

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "Primary bot",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "Alerts bot",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- `default` は `accountId` が省略されたときに使用されます（CLI + ルーティング）。
- 環境変数トークンは **default** アカウントにのみ適用されます。
- ベースチャンネル設定は、アカウントごとに上書きされない限り、すべてのアカウントに適用されます。
- `bindings[].match.accountId` を使うと、各アカウントを別のエージェントにルーティングできます。
- 単一アカウントのトップレベルチャンネル設定のまま、`openclaw channels add`（またはチャンネルのオンボーディング）で非 default アカウントを追加すると、OpenClaw はまずアカウントスコープのトップレベル単一アカウント値をチャンネルのアカウントマップへ昇格させ、元のアカウントが引き続き動作するようにします。ほとんどのチャンネルではそれらを `channels.<channel>.accounts.default` に移動しますが、Matrix では既存の一致する named/default ターゲットを保持できます。
- 既存のチャンネル単独のバインディング（`accountId` なし）は default アカウントに引き続き一致します。アカウントスコープのバインディングは任意のままです。
- `openclaw doctor --fix` も混在した形を修復し、そのチャンネル用に選ばれた昇格先アカウントへアカウントスコープのトップレベル単一アカウント値を移動します。ほとんどのチャンネルでは `accounts.default` を使いますが、Matrix では既存の一致する named/default ターゲットを保持できます。

### その他の extension チャンネル

多くの extension チャンネルは `channels.<id>` として設定され、それぞれの専用チャンネルページに記載されています（たとえば Feishu、Matrix、LINE、Nostr、Zalo、Nextcloud Talk、Synology Chat、Twitch）。
完全なチャンネル一覧は [Channels](/ja-JP/channels) を参照してください。

### グループチャットのメンションゲート

グループメッセージはデフォルトで **メンション必須** です（メタデータのメンションまたは安全な正規表現パターン）。WhatsApp、Telegram、Discord、Google Chat、iMessage のグループチャットに適用されます。

**メンションの種類:**

- **メタデータメンション**: ネイティブプラットフォームの @-mention。WhatsApp の self-chat mode では無視されます。
- **テキストパターン**: `agents.list[].groupChat.mentionPatterns` 内の安全な正規表現パターン。無効なパターンや安全でない入れ子の繰り返しは無視されます。
- メンションゲートは、検出が可能な場合（ネイティブメンションまたは少なくとも1つのパターンがある場合）にのみ適用されます。

```json5
{
  messages: {
    groupChat: { historyLimit: 50 },
  },
  agents: {
    list: [{ id: "main", groupChat: { mentionPatterns: ["@openclaw", "openclaw"] } }],
  },
}
```

`messages.groupChat.historyLimit` はグローバルデフォルトを設定します。チャンネルは `channels.<channel>.historyLimit`（またはアカウントごと）で上書きできます。`0` に設定すると無効になります。

#### DM 履歴制限

```json5
{
  channels: {
    telegram: {
      dmHistoryLimit: 30,
      dms: {
        "123456789": { historyLimit: 50 },
      },
    },
  },
}
```

解決順: DM ごとの上書き → プロバイダーデフォルト → 制限なし（すべて保持）。

対応: `telegram`、`whatsapp`、`discord`、`slack`、`signal`、`imessage`、`msteams`。

#### Self-chat mode

自分の番号を `allowFrom` に含めると self-chat mode が有効になります（ネイティブ @-mention を無視し、テキストパターンにのみ応答します）。

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: { mentionPatterns: ["reisponde", "@openclaw"] },
      },
    ],
  },
}
```

### コマンド（チャットコマンド処理）

```json5
{
  commands: {
    native: "auto", // register native commands when supported
    text: true, // parse /commands in chat messages
    bash: false, // allow ! (alias: /bash)
    bashForegroundMs: 2000,
    config: false, // allow /config
    debug: false, // allow /debug
    restart: false, // allow /restart + gateway restart tool
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="コマンドの詳細">

- テキストコマンドは先頭に `/` がある**単独の**メッセージである必要があります。
- `native: "auto"` は Discord/Telegram ではネイティブコマンドを有効にし、Slack では無効のままにします。
- チャンネルごとの上書き: `channels.discord.commands.native`（bool または `"auto"`）。`false` は以前に登録されたコマンドをクリアします。
- `channels.telegram.customCommands` は追加の Telegram bot メニュー項目を加えます。
- `bash: true` はホストシェルへの `! <cmd>` を有効にします（エイリアス: `/bash`）。`tools.elevated.enabled` と、送信者が `tools.elevated.allowFrom.<channel>` に含まれていることが必要です。
- `config: true` は `/config`（`openclaw.json` の読み書き）を有効にします。Gateway の `chat.send` クライアントでは、永続的な `/config set|unset` 書き込みには `operator.admin` も必要です。読み取り専用の `/config show` は通常の書き込みスコープを持つ operator クライアントでも利用できます。
- `channels.<provider>.configWrites` はチャンネルごとの設定変更を制御します（デフォルト: true）。
- マルチアカウントチャンネルでは、`channels.<provider>.accounts.<id>.configWrites` も、そのアカウントを対象とする書き込み（たとえば `/allowlist --config --account <id>` や `/config set channels.<provider>.accounts.<id>...`）を制御します。
- `allowFrom` はプロバイダーごとです。設定されている場合、それが**唯一の**認可ソースになります（チャンネル許可リスト/ペアリングおよび `useAccessGroups` は無視されます）。
- `useAccessGroups: false` は、`allowFrom` が設定されていない場合にコマンドが access-group ポリシーをバイパスできるようにします。

</Accordion>

---

## エージェントのデフォルト

### `agents.defaults.workspace`

デフォルト: `~/.openclaw/workspace`。

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

システムプロンプトの Runtime 行に表示されるオプションのリポジトリルート。未設定の場合、OpenClaw は workspace から上方向にたどって自動検出します。

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

`agents.list[].skills` を設定していないエージェント向けの、オプションのデフォルト Skills 許可リスト。

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // github, weather を継承
      { id: "docs", skills: ["docs-search"] }, // デフォルトを置き換える
      { id: "locked-down", skills: [] }, // Skills なし
    ],
  },
}
```

- デフォルトで Skills を無制限にするには `agents.defaults.skills` を省略します。
- デフォルトを継承するには `agents.list[].skills` を省略します。
- Skills を使わない場合は `agents.list[].skills: []` を設定します。
- 空でない `agents.list[].skills` リストは、そのエージェントの最終セットになります。デフォルトとはマージされません。

### `agents.defaults.skipBootstrap`

workspace bootstrap ファイル（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、`BOOTSTRAP.md`）の自動作成を無効にします。

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

workspace bootstrap ファイルをいつシステムプロンプトに注入するかを制御します。デフォルト: `"always"`。

- `"continuation-skip"`: 安全な継続ターン（assistant の応答完了後）では workspace bootstrap の再注入をスキップし、プロンプトサイズを削減します。heartbeat 実行とコンパクション後の再試行では引き続きコンテキストが再構築されます。

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

切り詰め前の workspace bootstrap ファイルごとの最大文字数。デフォルト: `20000`。

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

すべての workspace bootstrap ファイルにわたって注入される合計最大文字数。デフォルト: `150000`。

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

bootstrap コンテキストが切り詰められたときにエージェントへ見える警告文を制御します。
デフォルト: `"once"`。

- `"off"`: システムプロンプトに警告文を注入しません。
- `"once"`: 一意の切り詰めシグネチャごとに1回だけ警告を注入します（推奨）。
- `"always"`: 切り詰めが存在するたびに毎回警告を注入します。

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

provider 呼び出し前に transcript/tool の画像ブロックで使われる、画像の長辺の最大ピクセルサイズ。
デフォルト: `1200`。

値を低くすると通常は vision token 使用量とリクエストペイロードサイズが減ります。
値を高くすると、より多くの視覚的詳細が保持されます。

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

システムプロンプトのコンテキスト用タイムゾーンです（メッセージタイムスタンプではありません）。ホストのタイムゾーンにフォールバックします。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

システムプロンプト内の時刻形式。デフォルト: `auto`（OS設定）。

```json5
{
  agents: { defaults: { timeFormat: "auto" } }, // auto | 12 | 24
}
```

### `agents.defaults.model`

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview"],
      },
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-i2v"],
      },
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.4-mini"],
      },
      params: { cacheRetention: "long" }, // global default provider params
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
      thinkingDefault: "low",
      verboseDefault: "off",
      elevatedDefault: "on",
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      contextTokens: 200000,
      maxConcurrent: 3,
    },
  },
}
```

- `model`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 文字列形式は primary model のみを設定します。
  - オブジェクト形式は primary に加えて順序付き failover model も設定します。
- `imageModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - `image` ツールパスが vision-model 設定として使用します。
  - 選択/デフォルトのモデルが画像入力を受け付けない場合の fallback ルーティングにも使用されます。
- `imageGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共通の画像生成 capability と、将来の画像生成ツール/プラグイン surface で使用されます。
  - 一般的な値: ネイティブ Gemini 画像生成なら `google/gemini-3.1-flash-image-preview`、fal なら `fal/fal-ai/flux/dev`、OpenAI Images なら `openai/gpt-image-1`。
  - provider/model を直接選ぶ場合は、対応する provider auth/API key も設定してください（例: `google/*` には `GEMINI_API_KEY` または `GOOGLE_API_KEY`、`openai/*` には `OPENAI_API_KEY`、`fal/*` には `FAL_KEY`）。
  - 省略しても、`image_generate` は auth がある provider のデフォルトを推論できます。最初に現在の default provider を試し、その後、残りの登録済み画像生成 provider を provider-id 順で試します。
- `musicGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共通の音楽生成 capability と組み込み `music_generate` ツールで使用されます。
  - 一般的な値: `google/lyria-3-clip-preview`、`google/lyria-3-pro-preview`、`minimax/music-2.5+`。
  - 省略しても、`music_generate` は auth がある provider のデフォルトを推論できます。最初に現在の default provider を試し、その後、残りの登録済み音楽生成 provider を provider-id 順で試します。
  - provider/model を直接選ぶ場合は、対応する provider auth/API key も設定してください。
- `videoGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共通の動画生成 capability と組み込み `video_generate` ツールで使用されます。
  - 一般的な値: `qwen/wan2.6-t2v`、`qwen/wan2.6-i2v`、`qwen/wan2.6-r2v`、`qwen/wan2.6-r2v-flash`、`qwen/wan2.7-r2v`。
  - 省略しても、`video_generate` は auth がある provider のデフォルトを推論できます。最初に現在の default provider を試し、その後、残りの登録済み動画生成 provider を provider-id 順で試します。
  - provider/model を直接選ぶ場合は、対応する provider auth/API key も設定してください。
  - 同梱の Qwen 動画生成 provider は現在、最大で出力動画1件、入力画像1件、入力動画4件、長さ10秒、および provider レベルの `size`、`aspectRatio`、`resolution`、`audio`、`watermark` オプションをサポートします。
- `pdfModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - `pdf` ツールがモデルルーティングに使用します。
  - 省略した場合、PDF ツールは `imageModel`、その次に解決された session/default model にフォールバックします。
- `pdfMaxBytesMb`: `pdf` ツールで呼び出し時に `maxBytesMb` が渡されない場合のデフォルト PDF サイズ制限。
- `pdfMaxPages`: `pdf` ツールの抽出 fallback mode で考慮するデフォルトの最大ページ数。
- `verboseDefault`: エージェントのデフォルト verbose レベル。値: `"off"`、`"on"`、`"full"`。デフォルト: `"off"`。
- `elevatedDefault`: エージェントのデフォルト elevated-output レベル。値: `"off"`、`"on"`、`"ask"`、`"full"`。デフォルト: `"on"`。
- `model.primary`: 形式は `provider/model`（例 `openai/gpt-5.4`）。provider を省略すると、OpenClaw は最初に alias を試し、その後、その正確な model id に一致する一意の configured-provider を試し、最後に configured default provider にフォールバックします（非推奨の互換動作なので、明示的な `provider/model` を推奨）。その provider が設定済み default model をもう公開していない場合、OpenClaw は古い削除済み provider デフォルトを表示する代わりに、最初の configured provider/model にフォールバックします。
- `models`: `/model` 用の configured model catalog と allowlist。各エントリには `alias`（短縮名）と `params`（provider 固有、例 `temperature`、`maxTokens`、`cacheRetention`、`context1m`）を含められます。
- `params`: すべての model に適用されるグローバルな default provider parameters。`agents.defaults.params` に設定します（例 `{ cacheRetention: "long" }`）。
- `params` のマージ優先順位（config）: `agents.defaults.params`（グローバルベース）は `agents.defaults.models["provider/model"].params`（model ごと）で上書きされ、その後 `agents.list[].params`（一致する agent id）がキーごとに上書きします。詳細は [Prompt Caching](/ja-JP/reference/prompt-caching) を参照してください。
- これらのフィールドを書き換える config writer（例 `/models set`、`/models set-image`、fallback の追加/削除コマンド）は、正規のオブジェクト形式で保存し、可能な限り既存の fallback リストを保持します。
- `maxConcurrent`: セッションをまたいだ並列 agent 実行の最大数（各セッション自体は引き続き直列化されます）。デフォルト: 4。

**組み込みの alias 短縮名**（model が `agents.defaults.models` にある場合のみ適用）:

| Alias               | Model                                  |
| ------------------- | -------------------------------------- |
| `opus`              | `anthropic/claude-opus-4-6`            |
| `sonnet`            | `anthropic/claude-sonnet-4-6`          |
| `gpt`               | `openai/gpt-5.4`                       |
| `gpt-mini`          | `openai/gpt-5.4-mini`                  |
| `gpt-nano`          | `openai/gpt-5.4-nano`                  |
| `gemini`            | `google/gemini-3.1-pro-preview`        |
| `gemini-flash`      | `google/gemini-3-flash-preview`        |
| `gemini-flash-lite` | `google/gemini-3.1-flash-lite-preview` |

設定済み alias は常にデフォルトより優先されます。

Z.AI GLM-4.x model は、`--thinking off` を設定するか、`agents.defaults.models["zai/<model>"].params.thinking` を自分で定義しない限り、自動的に thinking mode を有効にします。
Z.AI model は、tool call streaming 用にデフォルトで `tool_stream` を有効にします。無効にするには `agents.defaults.models["zai/<model>"].params.tool_stream` を `false` に設定してください。
Anthropic Claude 4.6 model は、明示的な thinking level が設定されていない場合、デフォルトで `adaptive` thinking を使用します。

### `agents.defaults.cliBackends`

テキスト専用の fallback 実行（tool call なし）用のオプションの CLI backend。API provider が失敗したときのバックアップとして便利です。

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          modelArg: "--model",
          sessionArg: "--session",
          sessionMode: "existing",
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
        },
      },
    },
  },
}
```

- CLI backend はテキスト優先で、tool は常に無効です。
- `sessionArg` が設定されている場合は session をサポートします。
- `imageArg` がファイルパスを受け付ける場合は画像のパススルーをサポートします。

### `agents.defaults.heartbeat`

定期的な heartbeat 実行。

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m disables
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        lightContext: false, // default: false; true keeps only HEARTBEAT.md from workspace bootstrap files
        isolatedSession: false, // default: false; true runs each heartbeat in a fresh session (no conversation history)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (default) | block
        target: "none", // default: none | options: last | whatsapp | telegram | discord | ...
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
      },
    },
  },
}
```

- `every`: 期間文字列（ms/s/m/h）。デフォルトは `30m`（API-key auth）または `1h`（OAuth auth）。無効にするには `0m` を設定します。
- `suppressToolErrorWarnings`: `true` の場合、heartbeat 実行中の tool error warning payload を抑制します。
- `directPolicy`: direct/DM 配信ポリシー。`allow`（デフォルト）は direct ターゲット配信を許可します。`block` は direct ターゲット配信を抑制し、`reason=dm-blocked` を出力します。
- `lightContext`: `true` の場合、heartbeat 実行は軽量 bootstrap context を使用し、workspace bootstrap ファイルのうち `HEARTBEAT.md` のみを保持します。
- `isolatedSession`: `true` の場合、各 heartbeat 実行は prior conversation history を持たない新しい session で実行されます。cron の `sessionTarget: "isolated"` と同じ分離パターンです。heartbeat ごとの token コストを約 100K から約 2-5K token に削減します。
- agent ごと: `agents.list[].heartbeat` を設定します。いずれかの agent が `heartbeat` を定義すると、heartbeat を実行するのは**それらの agent のみ**になります。
- heartbeat は完全な agent turn を実行するため、間隔を短くすると token 消費が増えます。

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        provider: "my-provider", // id of a registered compaction provider plugin (optional)
        timeoutSeconds: 900,
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "Preserve deployment IDs, ticket IDs, and host:port pairs exactly.", // used when identifierPolicy=custom
        postCompactionSections: ["Session Startup", "Red Lines"], // [] disables reinjection
        model: "openrouter/anthropic/claude-sonnet-4-6", // optional compaction-only model override
        notifyUser: true, // send a brief notice when compaction starts (default: false)
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with the exact silent token NO_REPLY if nothing to store.",
        },
      },
    },
  },
}
```

- `mode`: `default` または `safeguard`（長い履歴向けのチャンク化要約）。[Compaction](/ja-JP/concepts/compaction) を参照してください。
- `provider`: 登録済み compaction provider plugin の id。設定すると、組み込み LLM 要約の代わりに provider の `summarize()` が呼び出されます。失敗時は組み込みにフォールバックします。provider を設定すると `mode: "safeguard"` が強制されます。[Compaction](/ja-JP/concepts/compaction) を参照してください。
- `timeoutSeconds`: OpenClaw が中断するまでに単一の compaction 操作へ許可する最大秒数。デフォルト: `900`。
- `identifierPolicy`: `strict`（デフォルト）、`off`、または `custom`。`strict` は compaction 要約中に組み込みの opaque identifier 保持ガイダンスを先頭に追加します。
- `identifierInstructions`: `identifierPolicy=custom` のときに使われるオプションのカスタム identifier 保持テキスト。
- `postCompactionSections`: compaction 後に再注入する AGENTS.md の H2/H3 セクション名のオプション指定。デフォルトは `["Session Startup", "Red Lines"]` で、`[]` にすると再注入を無効化します。未設定またはそのデフォルトのペアが明示設定されている場合は、古い `Every Session`/`Safety` 見出しも従来互換の fallback として受け入れられます。
- `model`: compaction 要約専用のオプション `provider/model-id` 上書き。メイン session は同じ model を維持しつつ、compaction 要約のみ別 model で実行したい場合に使用します。未設定の場合、compaction は session の primary model を使用します。
- `notifyUser`: `true` の場合、compaction 開始時にユーザーへ短い通知（例 `"Compacting context..."`）を送ります。デフォルトでは無効で、compaction を静かに保ちます。
- `memoryFlush`: auto-compaction 前に durable memory を保存する silent agentic turn。workspace が read-only の場合はスキップされます。

### `agents.defaults.contextPruning`

LLM に送信する前に、インメモリコンテキストから**古い tool result** を剪定します。ディスク上の session history は変更しません。

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // duration (ms/s/m/h), default unit: minutes
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Old tool result content cleared]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="cache-ttl モードの動作">

- `mode: "cache-ttl"` で pruning pass が有効になります。
- `ttl` は、前回の cache touch 後に pruning を再度実行できる頻度を制御します。
- pruning はまず oversized な tool result を soft-trim し、その後必要に応じて古い tool result を hard-clear します。

**Soft-trim** は先頭と末尾を保持し、中間に `...` を挿入します。

**Hard-clear** は tool result 全体を placeholder に置き換えます。

注記:

- image block は決して trim/clear されません。
- ratio は token 数ではなく文字数ベースの概算です。
- `keepLastAssistants` 未満の assistant message しか存在しない場合、pruning はスキップされます。

</Accordion>

動作の詳細は [Session Pruning](/ja-JP/concepts/session-pruning) を参照してください。

### ブロックストリーミング

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (use minMs/maxMs)
    },
  },
}
```

- Telegram 以外のチャンネルでは、ブロック返信を有効にするには明示的な `*.blockStreaming: true` が必要です。
- チャンネルごとの上書き: `channels.<channel>.blockStreamingCoalesce`（およびアカウントごとの変種）。Signal/Slack/Discord/Google Chat のデフォルトは `minChars: 1500` です。
- `humanDelay`: ブロック返信間のランダムな待機時間。`natural` = 800–2500ms。agent ごとの上書き: `agents.list[].humanDelay`。

動作と chunking の詳細は [Streaming](/ja-JP/concepts/streaming) を参照してください。

### タイピングインジケーター

```json5
{
  agents: {
    defaults: {
      typingMode: "instant", // never | instant | thinking | message
      typingIntervalSeconds: 6,
    },
  },
}
```

- デフォルト: direct chat/mention では `instant`、メンションされていない group chat では `message`。
- session ごとの上書き: `session.typingMode`、`session.typingIntervalSeconds`。

[Typing Indicators](/ja-JP/concepts/typing-indicators) を参照してください。

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

埋め込み agent 向けのオプションの sandbox 化。完全なガイドは [Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        backend: "docker", // docker | ssh | openshell
        scope: "agent", // session | agent | shared
        workspaceAccess: "none", // none | ro | rw
        workspaceRoot: "~/.openclaw/sandboxes",
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          containerPrefix: "openclaw-sbx-",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: {
            nofile: { soft: 1024, hard: 2048 },
            nproc: 256,
          },
          seccompProfile: "/path/to/seccomp.json",
          apparmorProfile: "openclaw-sandbox",
          dns: ["1.1.1.1", "8.8.8.8"],
          extraHosts: ["internal.service:10.0.0.5"],
          binds: ["/home/user/source:/source:rw"],
        },
        ssh: {
          target: "user@gateway-host:22",
          command: "ssh",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // SecretRefs / inline contents also supported:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
        browser: {
          enabled: false,
          image: "openclaw-sandbox-browser:bookworm-slim",
          network: "openclaw-sandbox-browser",
          cdpPort: 9222,
          cdpSourceRange: "172.21.0.1/32",
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          allowHostControl: false,
          autoStart: true,
          autoStartTimeoutMs: 12000,
        },
        prune: {
          idleHours: 24,
          maxAgeDays: 7,
        },
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        allow: [
          "exec",
          "process",
          "read",
          "write",
          "edit",
          "apply_patch",
          "sessions_list",
          "sessions_history",
          "sessions_send",
          "sessions_spawn",
          "session_status",
        ],
        deny: ["browser", "canvas", "nodes", "cron", "discord", "gateway"],
      },
    },
  },
}
```

<Accordion title="Sandbox の詳細">

**Backend:**

- `docker`: ローカル Docker runtime（デフォルト）
- `ssh`: 汎用 SSH バックド remote runtime
- `openshell`: OpenShell runtime

`backend: "openshell"` を選択した場合、runtime 固有の設定は
`plugins.entries.openshell.config` に移ります。

**SSH backend 設定:**

- `target`: `user@host[:port]` 形式の SSH ターゲット
- `command`: SSH client command（デフォルト: `ssh`）
- `workspaceRoot`: scope ごとの workspace に使う絶対 remote root
- `identityFile` / `certificateFile` / `knownHostsFile`: OpenSSH に渡される既存のローカルファイル
- `identityData` / `certificateData` / `knownHostsData`: OpenClaw が runtime で temp file に materialize する inline content または SecretRef
- `strictHostKeyChecking` / `updateHostKeys`: OpenSSH の host-key policy ノブ

**SSH auth の優先順位:**

- `identityData` は `identityFile` より優先
- `certificateData` は `certificateFile` より優先
- `knownHostsData` は `knownHostsFile` より優先
- SecretRef バックドの `*Data` 値は、sandbox session 開始前にアクティブな secrets runtime snapshot から解決されます

**SSH backend の動作:**

- create または recreate の後に remote workspace を一度 seed する
- その後は remote SSH workspace を正規のものとして維持する
- `exec`、file tool、media path を SSH 経由にルーティングする
- remote での変更を host に自動同期しない
- sandbox browser container はサポートしない

**Workspace access:**

- `none`: `~/.openclaw/sandboxes` 配下の scope ごとの sandbox workspace
- `ro`: `/workspace` に sandbox workspace、`/agent` に agent workspace を読み取り専用で mount
- `rw`: agent workspace を `/workspace` に読み書き可能で mount

**Scope:**

- `session`: session ごとの container + workspace
- `agent`: agent ごとに1つの container + workspace（デフォルト）
- `shared`: 共有 container と workspace（セッション間分離なし）

**OpenShell plugin 設定:**

```json5
{
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          mode: "mirror", // mirror | remote
          from: "openclaw",
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
          gateway: "lab", // optional
          gatewayEndpoint: "https://lab.example", // optional
          policy: "strict", // optional OpenShell policy id
          providers: ["openai"], // optional
          autoProviders: true,
          timeoutSeconds: 120,
        },
      },
    },
  },
}
```

**OpenShell mode:**

- `mirror`: exec 前に local から remote へ seed し、exec 後に同期し戻す。local workspace が正規のまま維持される
- `remote`: sandbox 作成時に一度 remote へ seed し、その後は remote workspace を正規のものとして維持する

`remote` mode では、OpenClaw の外で行われた host-local の編集は、seed ステップ後に sandbox へ自動同期されません。
transport は OpenShell sandbox への SSH ですが、plugin が sandbox lifecycle と任意の mirror sync を所有します。

**`setupCommand`** は container 作成後に1回だけ実行されます（`sh -lc` 経由）。network egress、書き込み可能な root、root user が必要です。

**Container のデフォルトは `network: "none"`** です。agent が外向きアクセスを必要とする場合は `"bridge"`（またはカスタム bridge network）に設定してください。
`"host"` はブロックされます。`"container:<id>"` もデフォルトではブロックされますが、
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` を明示設定した場合にのみ許可されます（緊急回避用）。

**受信添付ファイル** はアクティブな workspace の `media/inbound/*` に staged されます。

**`docker.binds`** は追加の host ディレクトリを mount します。グローバルと agent ごとの bind はマージされます。

**Sandboxed browser**（`sandbox.browser.enabled`）: container 内の Chromium + CDP。noVNC URL がシステムプロンプトへ注入されます。`openclaw.json` で `browser.enabled` は不要です。
noVNC の observer access ではデフォルトで VNC auth が使われ、OpenClaw は共有URLにパスワードを露出させる代わりに短命の token URL を出力します。

- `allowHostControl: false`（デフォルト）は、sandbox 化された session が host browser をターゲットにすることを防ぎます。
- `network` のデフォルトは `openclaw-sandbox-browser`（専用 bridge network）です。明示的にグローバル bridge 接続を望む場合のみ `bridge` に設定してください。
- `cdpSourceRange` は、container エッジで CDP ingress を CIDR 範囲（例 `172.21.0.1/32`）に制限できます。
- `sandbox.browser.binds` は追加の host ディレクトリを browser container のみに mount します。設定された場合（`[]` を含む）、browser container では `docker.binds` の代わりに使われます。
- 起動デフォルトは `scripts/sandbox-browser-entrypoint.sh` に定義されており、container host 向けに調整されています:
  - `--remote-debugging-address=127.0.0.1`
  - `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
  - `--user-data-dir=${HOME}/.chrome`
  - `--no-first-run`
  - `--no-default-browser-check`
  - `--disable-3d-apis`
  - `--disable-gpu`
  - `--disable-software-rasterizer`
  - `--disable-dev-shm-usage`
  - `--disable-background-networking`
  - `--disable-features=TranslateUI`
  - `--disable-breakpad`
  - `--disable-crash-reporter`
  - `--renderer-process-limit=2`
  - `--no-zygote`
  - `--metrics-recording-only`
  - `--disable-extensions`（デフォルトで有効）
  - `--disable-3d-apis`、`--disable-software-rasterizer`、`--disable-gpu` は
    デフォルトで有効で、WebGL/3D 利用で必要な場合は
    `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` で無効にできます。
  - ワークフローが extension に依存する場合は
    `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` で再有効化できます。
  - `--renderer-process-limit=2` は
    `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` で変更できます。`0` にすると Chromium の
    デフォルト process limit を使います。
  - 加えて、`noSandbox` が有効なときは `--no-sandbox` と `--disable-setuid-sandbox`。
  - デフォルトは container image のベースラインです。container デフォルトを変更するには、
    custom browser image と custom entrypoint を使用してください。

</Accordion>

browser sandboxing と `sandbox.docker.binds` は現在 Docker 専用です。

イメージをビルド:

```bash
scripts/sandbox-setup.sh           # main sandbox image
scripts/sandbox-browser-setup.sh   # optional browser image
```

### `agents.list`（agent ごとの上書き）

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6", // or { primary, fallbacks }
        thinkingDefault: "high", // per-agent thinking level override
        reasoningDefault: "on", // per-agent reasoning visibility override
        fastModeDefault: false, // per-agent fast mode override
        params: { cacheRetention: "none" }, // overrides matching defaults.models params by key
        skills: ["docs-search"], // replaces agents.defaults.skills when set
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
        subagents: { allowAgents: ["*"] },
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
          elevated: { enabled: true },
        },
      },
    ],
  },
}
```

- `id`: 安定した agent id（必須）。
- `default`: 複数設定されている場合は最初のものが勝ちます（警告が記録されます）。何も設定されていない場合は list の最初のエントリが default になります。
- `model`: 文字列形式は `primary` のみを上書きし、オブジェクト形式 `{ primary, fallbacks }` は両方を上書きします（`[]` でグローバル fallback を無効化）。`primary` のみを上書きする cron job は、`fallbacks: []` を設定しない限りデフォルト fallback を引き継ぎます。
- `params`: 選択された model エントリに対して `agents.defaults.models` からマージされる agent ごとの stream params。`cacheRetention`、`temperature`、`maxTokens` のような agent 固有の上書きに使います。model catalog 全体を複製する必要はありません。
- `skills`: オプションの agent ごとの Skills 許可リスト。省略時は、設定されていれば agent は `agents.defaults.skills` を継承します。明示的なリストはデフォルトをマージせず置き換え、`[]` は Skills なしを意味します。
- `thinkingDefault`: オプションの agent ごとのデフォルト thinking level（`off | minimal | low | medium | high | xhigh | adaptive`）。メッセージごとまたは session ごとの上書きがない場合、この agent の `agents.defaults.thinkingDefault` を上書きします。
- `reasoningDefault`: オプションの agent ごとのデフォルト reasoning visibility（`on | off | stream`）。メッセージごとまたは session ごとの reasoning 上書きがない場合に適用されます。
- `fastModeDefault`: オプションの agent ごとの fast mode デフォルト（`true | false`）。メッセージごとまたは session ごとの fast-mode 上書きがない場合に適用されます。
- `runtime`: オプションの agent ごとの runtime descriptor。agent がデフォルトで ACP harness session を使うべき場合は、`type: "acp"` と `runtime.acp` のデフォルト（`agent`、`backend`、`mode`、`cwd`）を使用します。
- `identity.avatar`: workspace 相対パス、`http(s)` URL、または `data:` URI。
- `identity` はデフォルトを導出します: `emoji` から `ackReaction`、`name`/`emoji` から `mentionPatterns`。
- `subagents.allowAgents`: `sessions_spawn` 用の agent id 許可リスト（`["*"]` = 任意、デフォルト: 同じ agent のみ）。
- Sandbox 継承ガード: リクエスター session が sandbox 化されている場合、`sessions_spawn` は sandbox 化されないターゲットを拒否します。
- `subagents.requireAgentId`: `true` の場合、`agentId` を省略した `sessions_spawn` 呼び出しをブロックします（明示的な profile 選択を強制。デフォルト: false）。

---

## マルチエージェントルーティング

1つの Gateway 内で複数の分離された agent を実行します。[Multi-Agent](/ja-JP/concepts/multi-agent) を参照してください。

```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

### バインディングの一致フィールド

- `type`（オプション）: 通常ルーティング用の `route`（type がない場合は route がデフォルト）、永続 ACP 会話バインディング用の `acp`
- `match.channel`（必須）
- `match.accountId`（オプション。`*` = 任意のアカウント、省略 = default アカウント）
- `match.peer`（オプション。`{ kind: direct|group|channel, id }`）
- `match.guildId` / `match.teamId`（オプション。チャンネル固有）
- `acp`（オプション。`type: "acp"` のときのみ）: `{ mode, label, cwd, backend }`

**決定的な一致順序:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId`（完全一致。peer/guild/team なし）
5. `match.accountId: "*"`（チャンネル全体）
6. デフォルト agent

各 tier 内では、最初に一致した `bindings` エントリが勝ちます。

`type: "acp"` エントリでは、OpenClaw は正確な会話 identity（`match.channel` + account + `match.peer.id`）で解決し、上記の route binding tier 順序は使用しません。

### agent ごとのアクセスプロファイル

<Accordion title="フルアクセス（sandbox なし）">

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="読み取り専用のツール + workspace">

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "ro" },
        tools: {
          allow: [
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="ファイルシステムアクセスなし（メッセージングのみ）">

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "none" },
        tools: {
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
            "gateway",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

</Accordion>

優先順位の詳細は [Multi-Agent Sandbox & Tools](/ja-JP/tools/multi-agent-sandbox-tools) を参照してください。

---

## セッション

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main", // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily", // daily | idle
      atHour: 4,
      idleMinutes: 60,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    parentForkMaxTokens: 100000, // skip parent-thread fork above this token count (0 disables)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // duration or false
      maxDiskBytes: "500mb", // optional hard budget
      highWaterBytes: "400mb", // optional cleanup target
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // default inactivity auto-unfocus in hours (`0` disables)
      maxAgeHours: 0, // default hard max age in hours (`0` disables)
    },
    mainKey: "main", // legacy (runtime always uses "main")
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="セッションフィールドの詳細">

- **`scope`**: group-chat context 向けのベース session grouping strategy。
  - `per-sender`（デフォルト）: チャンネルコンテキスト内で送信者ごとに分離された session。
  - `global`: チャンネルコンテキスト内の全参加者で1つの session を共有します（共有コンテキストを意図する場合のみ使用してください）。
- **`dmScope`**: DM のグループ化方法。
  - `main`: すべての DM が main session を共有します。
  - `per-peer`: チャンネルをまたいで送信者 id ごとに分離します。
  - `per-channel-peer`: チャンネル + 送信者ごとに分離します（マルチユーザー inbox に推奨）。
  - `per-account-channel-peer`: アカウント + チャンネル + 送信者ごとに分離します（マルチアカウントに推奨）。
- **`identityLinks`**: channel 間の session 共有用に、canonical id を provider 接頭辞付き peer へマップします。
- **`reset`**: プライマリ reset policy。`daily` はローカル時刻の `atHour` に reset し、`idle` は `idleMinutes` 後に reset します。両方が設定されている場合、先に期限切れになる方が適用されます。
- **`resetByType`**: type ごとの上書き（`direct`、`group`、`thread`）。従来の `dm` も `direct` の別名として受け付けます。
- **`parentForkMaxTokens`**: fork された thread session を作成するときに許可される親 session の `totalTokens` 最大値（デフォルト `100000`）。
  - 親の `totalTokens` がこの値を超えている場合、OpenClaw は親 transcript history を継承せず、新しい thread session を開始します。
  - `0` に設定するとこのガードを無効にし、常に親 fork を許可します。
- **`mainKey`**: 従来フィールド。runtime は現在常に direct-chat bucket の main に `"main"` を使用します。
- **`agentToAgent.maxPingPongTurns`**: agent-to-agent exchange 中に agent 間で許可される返信往復 turn の最大数（整数、範囲: `0`–`5`）。`0` で ping-pong chaining を無効化します。
- **`sendPolicy`**: `channel`、`chatType`（`direct|group|channel`。従来の `dm` 別名あり）、`keyPrefix`、または `rawKeyPrefix` で一致します。最初の deny が勝ちます。
- **`maintenance`**: session-store の cleanup + retention 制御。
  - `mode`: `warn` は警告のみ出し、`enforce` は cleanup を適用します。
  - `pruneAfter`: stale entry の age cutoff（デフォルト `30d`）。
  - `maxEntries`: `sessions.json` 内の最大 entry 数（デフォルト `500`）。
  - `rotateBytes`: `sessions.json` がこのサイズを超えたら rotate します（デフォルト `10mb`）。
  - `resetArchiveRetention`: `*.reset.<timestamp>` transcript archive の retention。デフォルトは `pruneAfter`。無効化するには `false` を設定します。
  - `maxDiskBytes`: オプションの sessions ディレクトリ disk budget。`warn` mode では警告を出し、`enforce` mode では最も古い artifact/session から削除します。
  - `highWaterBytes`: budget cleanup 後のオプション目標。デフォルトは `maxDiskBytes` の `80%`。
- **`threadBindings`**: thread-bound session 機能のグローバルデフォルト。
  - `enabled`: マスターデフォルトスイッチ（provider が上書き可能。Discord は `channels.discord.threadBindings.enabled` を使います）
  - `idleHours`: 非アクティブ時の自動 unfocus のデフォルト時間数（`0` で無効。provider が上書き可能）
  - `maxAgeHours`: ハード最大経過時間のデフォルト時間数（`0` で無効。provider が上書き可能）

</Accordion>

---

## メッセージ

```json5
{
  messages: {
    responsePrefix: "🦞", // or "auto"
    ackReaction: "👀",
    ackReactionScope: "group-mentions", // group-mentions | group-all | direct | all
    removeAckAfterReply: false,
    queue: {
      mode: "collect", // steer | followup | collect | steer-backlog | steer+backlog | queue | interrupt
      debounceMs: 1000,
      cap: 20,
      drop: "summarize", // old | new | summarize
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
      },
    },
    inbound: {
      debounceMs: 2000, // 0 disables
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### Response prefix

チャンネル/アカウントごとの上書き: `channels.<channel>.responsePrefix`、`channels.<channel>.accounts.<id>.responsePrefix`。

解決順（最も具体的なものが優先）: account → channel → global。`""` は無効化して cascade を止めます。`"auto"` は `[{identity.name}]` を導出します。

**テンプレート変数:**

| Variable          | 説明                       | 例                          |
| ----------------- | -------------------------- | --------------------------- |
| `{model}`         | 短いモデル名               | `claude-opus-4-6`           |
| `{modelFull}`     | 完全なモデル識別子         | `anthropic/claude-opus-4-6` |
| `{provider}`      | プロバイダー名             | `anthropic`                 |
| `{thinkingLevel}` | 現在の thinking level      | `high`, `low`, `off`        |
| `{identity.name}` | エージェント identity 名   | （`"auto"` と同じ）         |

変数は大文字小文字を区別しません。`{think}` は `{thinkingLevel}` の別名です。

### Ack reaction

- デフォルトはアクティブ agent の `identity.emoji`、なければ `"👀"`。無効にするには `""` を設定します。
- チャンネルごとの上書き: `channels.<channel>.ackReaction`、`channels.<channel>.accounts.<id>.ackReaction`。
- 解決順: account → channel → `messages.ackReaction` → identity fallback。
- Scope: `group-mentions`（デフォルト）、`group-all`、`direct`、`all`。
- `removeAckAfterReply`: Slack、Discord、Telegram で返信後に ack を削除します。
- `messages.statusReactions.enabled`: Slack、Discord、Telegram で lifecycle status reaction を有効にします。
  Slack と Discord では、未設定だと ack reaction が有効な場合に status reaction も有効のままになります。
  Telegram では、lifecycle status reaction を有効にするには明示的に `true` を設定してください。

### Inbound debounce

同じ送信者からの連続するテキストのみのメッセージを1つの agent turn にまとめます。media/attachment は即時 flush されます。control command は debouncing をバイパスします。

### TTS（text-to-speech）

```json5
{
  messages: {
    tts: {
      auto: "always", // off | always | inbound | tagged
      mode: "final", // final | all
      provider: "elevenlabs",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: { enabled: true },
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
      elevenlabs: {
        apiKey: "elevenlabs_api_key",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 42,
        applyTextNormalization: "auto",
        languageCode: "en",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          style: 0.0,
          useSpeakerBoost: true,
          speed: 1.0,
        },
      },
      openai: {
        apiKey: "openai_api_key",
        baseUrl: "https://api.openai.com/v1",
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
    },
  },
}
```

- `auto` は auto-TTS を制御します。`/tts off|always|inbound|tagged` は session ごとに上書きします。
- `summaryModel` は auto-summary 用に `agents.defaults.model.primary` を上書きします。
- `modelOverrides` はデフォルトで有効です。`modelOverrides.allowProvider` のデフォルトは `false`（明示的な opt-in）。
- API key は `ELEVENLABS_API_KEY`/`XI_API_KEY` および `OPENAI_API_KEY` にフォールバックします。
- `openai.baseUrl` は OpenAI TTS endpoint を上書きします。解決順は config、次に `OPENAI_TTS_BASE_URL`、次に `https://api.openai.com/v1` です。
- `openai.baseUrl` が非 OpenAI endpoint を指す場合、OpenClaw はそれを OpenAI 互換 TTS server として扱い、model/voice の検証を緩和します。

---

## Talk

Talk mode（macOS/iOS/Android）のデフォルト。

```json5
{
  talk: {
    provider: "elevenlabs",
    providers: {
      elevenlabs: {
        voiceId: "elevenlabs_voice_id",
        voiceAliases: {
          Clawd: "EXAVITQu4vr4xnSDxMaL",
          Roger: "CwhRBWXzGAHq8TQ4Fs17",
        },
        modelId: "eleven_v3",
        outputFormat: "mp3_44100_128",
        apiKey: "elevenlabs_api_key",
      },
    },
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
  },
}
```

- `talk.provider` は、複数の Talk provider が設定されている場合、`talk.providers` のキーと一致する必要があります。
- 従来のフラットな Talk キー（`talk.voiceId`、`talk.voiceAliases`、`talk.modelId`、`talk.outputFormat`、`talk.apiKey`）は互換用のみで、`talk.providers.<provider>` に自動移行されます。
- Voice ID は `ELEVENLABS_VOICE_ID` または `SAG_VOICE_ID` にフォールバックします。
- `providers.*.apiKey` はプレーンテキスト文字列または SecretRef オブジェクトを受け付けます。
- `ELEVENLABS_API_KEY` のフォールバックは、Talk API key が設定されていない場合にのみ適用されます。
- `providers.*.voiceAliases` により、Talk の directive で親しみやすい名前を使用できます。
- `silenceTimeoutMs` は、Talk mode がユーザーの無音後に transcript を送信するまで待機する時間を制御します。未設定の場合、プラットフォームのデフォルト pause window を使用します（`macOS と Android では 700 ms、iOS では 900 ms`）。

---

## ツール

### ツールプロファイル

`tools.profile` は `tools.allow`/`tools.deny` の前にベース許可リストを設定します。

ローカルオンボーディングでは、未設定の新しいローカル設定に対して `tools.profile: "coding"` をデフォルトで設定します（既存の明示的な profile は保持されます）。

| Profile     | 含まれるもの                                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `minimal`   | `session_status` のみ                                                                                                          |
| `coding`    | `group:fs`、`group:runtime`、`group:web`、`group:sessions`、`group:memory`、`cron`、`image`、`image_generate`、`video_generate` |
| `messaging` | `group:messaging`、`sessions_list`、`sessions_history`、`sessions_send`、`session_status`                                      |
| `full`      | 制限なし（未設定と同じ）                                                                                                       |

### ツールグループ

| Group              | ツール                                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `group:runtime`    | `exec`、`process`、`code_execution`（`bash` は `exec` の別名として受け付けられます）                                      |
| `group:fs`         | `read`、`write`、`edit`、`apply_patch`                                                                                   |
| `group:sessions`   | `sessions_list`、`sessions_history`、`sessions_send`、`sessions_spawn`、`sessions_yield`、`subagents`、`session_status` |
| `group:memory`     | `memory_search`、`memory_get`                                                                                            |
| `group:web`        | `web_search`、`x_search`、`web_fetch`                                                                                    |
| `group:ui`         | `browser`、`canvas`                                                                                                      |
| `group:automation` | `cron`、`gateway`                                                                                                        |
| `group:messaging`  | `message`                                                                                                                |
| `group:nodes`      | `nodes`                                                                                                                  |
| `group:agents`     | `agents_list`                                                                                                            |
| `group:media`      | `image`、`image_generate`、`video_generate`、`tts`                                                                       |
| `group:openclaw`   | すべての組み込みツール（provider plugin を除く）                                                                          |

### `tools.allow` / `tools.deny`

グローバルな tool allow/deny policy（deny が優先）。大文字小文字を区別せず、`*` ワイルドカードをサポートします。Docker sandbox がオフでも適用されます。

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

特定の provider または model 向けにツールをさらに制限します。順序: base profile → provider profile → allow/deny。

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.4": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

### `tools.elevated`

sandbox 外での elevated exec アクセスを制御します。

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["1234567890123", "987654321098765432"],
      },
    },
  },
}
```

- agent ごとの上書き（`agents.list[].tools.elevated`）は、さらに制限することしかできません。
- `/elevated on|off|ask|full` は状態を session ごとに保存します。インライン directive は単一メッセージに適用されます。
- Elevated `exec` は sandboxing をバイパスし、設定された escape path（デフォルトは `gateway`、exec target が `node` の場合は `node`）を使用します。

### `tools.exec`

```json5
{
  tools: {
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
      notifyOnExitEmptySuccess: false,
      applyPatch: {
        enabled: false,
        allowModels: ["gpt-5.4"],
      },
    },
  },
}
```

### `tools.loopDetection`

tool-loop の安全チェックは**デフォルトで無効**です。有効化するには `enabled: true` を設定してください。
設定はグローバルに `tools.loopDetection` で定義し、agent ごとに `agents.list[].tools.loopDetection` で上書きできます。

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

- `historySize`: loop analysis 用に保持する tool-call history の最大数。
- `warningThreshold`: 警告を出す繰り返し no-progress pattern のしきい値。
- `criticalThreshold`: 深刻な loop をブロックするための、より高い繰り返ししきい値。
- `globalCircuitBreakerThreshold`: あらゆる no-progress run に対する hard stop しきい値。
- `detectors.genericRepeat`: 同じ tool/同じ args 呼び出しの繰り返しで警告します。
- `detectors.knownPollNoProgress`: 既知の poll tool（`process.poll`、`command_status` など）で no-progress を警告/ブロックします。
- `detectors.pingPong`: no-progress の交互ペアパターンを警告/ブロックします。
- `warningThreshold >= criticalThreshold` または `criticalThreshold >= globalCircuitBreakerThreshold` の場合、検証は失敗します。

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // or BRAVE_API_KEY env
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // optional; omit for auto-detect
        maxChars: 50000,
        maxCharsCap: 50000,
        maxResponseBytes: 2000000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        maxRedirects: 3,
        readability: true,
        userAgent: "custom-ua",
      },
    },
  },
}
```

### `tools.media`

受信 media 理解（image/audio/video）を設定します。

```json5
{
  tools: {
    media: {
      concurrency: 2,
      asyncCompletion: {
        directSend: false, // opt-in: send finished async music/video directly to the channel
      },
      audio: {
        enabled: true,
        maxBytes: 20971520,
        scope: {
          default: "deny",
          rules: [{ action: "allow", match: { chatType: "direct" } }],
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { type: "cli", command: "whisper", args: ["--model", "base", "{{MediaPath}}"] },
        ],
      },
      video: {
        enabled: true,
        maxBytes: 52428800,
        models: [{ provider: "google", model: "gemini-3-flash-preview" }],
      },
    },
  },
}
```

<Accordion title="Media model エントリのフィールド">

**Provider エントリ**（`type: "provider"` または省略時）:

- `provider`: API provider id（`openai`、`anthropic`、`google`/`gemini`、`groq` など）
- `model`: model id 上書き
- `profile` / `preferredProfile`: `auth-profiles.json` の profile 選択

**CLI エントリ**（`type: "cli"`）:

- `command`: 実行する executable
- `args`: テンプレート化された args（`{{MediaPath}}`、`{{Prompt}}`、`{{MaxChars}}` などをサポート）

**共通フィールド:**

- `capabilities`: オプションのリスト（`image`、`audio`、`video`）。デフォルト: `openai`/`anthropic`/`minimax` → image、`google` → image+audio+video、`groq` → audio。
- `prompt`、`maxChars`、`maxBytes`、`timeoutSeconds`、`language`: エントリごとの上書き。
- 失敗した場合は次のエントリにフォールバックします。

Provider auth は標準の順序に従います: `auth-profiles.json` → 環境変数 → `models.providers.*.apiKey`。

**Async completion フィールド:**

- `asyncCompletion.directSend`: `true` の場合、完了した async `music_generate`
  と `video_generate` タスクはまず直接チャンネル配信を試みます。デフォルト: `false`
  （従来の requester-session wake/model-delivery パス）。

</Accordion>

### `tools.agentToAgent`

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },
}
```

### `tools.sessions`

session tool（`sessions_list`、`sessions_history`、`sessions_send`）でターゲットにできる session を制御します。

デフォルト: `tree`（現在の session と、そこから spawn された session。subagent など）。

```json5
{
  tools: {
    sessions: {
      // "self" | "tree" | "agent" | "all"
      visibility: "tree",
    },
  },
}
```

注記:

- `self`: 現在の session key のみ。
- `tree`: 現在の session + 現在の session から spawn された session（subagent）。
- `agent`: 現在の agent id に属するすべての session（同じ agent id の下で per-sender session を実行している場合は他のユーザーも含まれる可能性があります）。
- `all`: すべての session。cross-agent ターゲティングには引き続き `tools.agentToAgent` が必要です。
- Sandbox clamp: 現在の session が sandbox 化されていて、`agents.defaults.sandbox.sessionToolsVisibility="spawned"` の場合、`tools.sessions.visibility="all"` であっても visibility は `tree` に強制されます。

### `tools.sessions_spawn`

`sessions_spawn` のインライン添付ファイルサポートを制御します。

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // opt-in: set true to allow inline file attachments
        maxTotalBytes: 5242880, // 5 MB total across all files
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 MB per file
        retainOnSessionKeep: false, // keep attachments when cleanup="keep"
      },
    },
  },
}
```

注記:

- 添付ファイルは `runtime: "subagent"` でのみサポートされます。ACP runtime では拒否されます。
- ファイルは child workspace の `.openclaw/attachments/<uuid>/` に `.manifest.json` とともに materialize されます。
- 添付ファイルの内容は transcript persistence から自動的に redaction されます。
- Base64 入力は厳密な alphabet/padding チェックと decode 前サイズガードで検証されます。
- ファイル権限はディレクトリが `0700`、ファイルが `0600` です。
- cleanup は `cleanup` policy に従います。`delete` は常に添付ファイルを削除し、`keep` は `retainOnSessionKeep: true` の場合のみ保持します。

### `tools.experimental`

実験的な組み込み tool フラグ。runtime 固有の自動有効化ルールが適用されない限り、デフォルトは off。

```json5
{
  tools: {
    experimental: {
      planTool: true, // enable experimental update_plan
    },
  },
}
```

注記:

- `planTool`: 非自明な複数ステップ作業の追跡用に、構造化された `update_plan` tool を有効にします。
- デフォルト: 非 OpenAI provider では `false`。OpenAI と OpenAI Codex 実行では自動有効化されます。
- 有効な場合、システムプロンプトにも使用ガイダンスが追加され、実質的な作業にのみ使い、`in_progress` なステップを最大1つに保つようになります。

### `agents.defaults.subagents`

```json5
{
  agents: {
    defaults: {
      subagents: {
        allowAgents: ["research"],
        model: "minimax/MiniMax-M2.7",
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

- `model`: spawn された sub-agent のデフォルト model。省略すると、sub-agent は呼び出し元の model を継承します。
- `allowAgents`: リクエスター agent が自身の `subagents.allowAgents` を設定していない場合の、`sessions_spawn` 用ターゲット agent id のデフォルト許可リスト（`["*"]` = 任意。デフォルト: 同じ agent のみ）。
- `runTimeoutSeconds`: tool call が `runTimeoutSeconds` を省略した場合の `sessions_spawn` 用デフォルト timeout（秒）。`0` は timeout なしを意味します。
- sub-agent ごとの tool policy: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`。

---

## カスタムプロバイダーと base URL

OpenClaw は組み込み model catalog を使用します。カスタム provider は config の `models.providers` または `~/.openclaw/agents/<agentId>/agent/models.json` で追加します。

```json5
{
  models: {
    mode: "merge", // merge (default) | replace
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions", // openai-completions | openai-responses | anthropic-messages | google-generative-ai
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            contextTokens: 96000,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

- カスタム認証が必要な場合は `authHeader: true` + `headers` を使用してください。
- agent config root は `OPENCLAW_AGENT_DIR`（または従来の環境変数別名 `PI_CODING_AGENT_DIR`）で上書きできます。
- 一致する provider ID に対するマージ優先順位:
  - 空でない agent `models.json` の `baseUrl` 値が優先されます。
  - 空でない agent `apiKey` 値は、その provider が現在の config/auth-profile context で SecretRef 管理されていない場合にのみ優先されます。
  - SecretRef 管理の provider `apiKey` 値は、解決済み secret を永続化する代わりに source marker（env ref なら `ENV_VAR_NAME`、file/exec ref なら `secretref-managed`）から更新されます。
  - SecretRef 管理の provider header 値は source marker（env ref なら `secretref-env:ENV_VAR_NAME`、file/exec ref なら `secretref-managed`）から更新されます。
  - 空または欠落している agent `apiKey`/`baseUrl` は config の `models.providers` にフォールバックします。
  - 一致する model の `contextWindow`/`maxTokens` には、明示的 config と暗黙の catalog 値のうち高い方を使用します。
  - 一致する model の `contextTokens` は、明示的な runtime cap が存在する場合それを保持します。ネイティブな model metadata を変えずに、有効な context budget を制限したい場合に使用してください。
  - config で `models.json` を完全に書き換えたい場合は `models.mode: "replace"` を使用してください。
  - marker の永続化は source authoritative です。marker は、解決済み runtime secret 値からではなく、アクティブな source config snapshot（解決前）から書き込まれます。

### Provider フィールドの詳細

- `models.mode`: provider catalog の動作（`merge` または `replace`）。
- `models.providers`: provider id をキーとするカスタム provider map。
- `models.providers.*.api`: request adapter（`openai-completions`、`openai-responses`、`anthropic-messages`、`google-generative-ai` など）。
- `models.providers.*.apiKey`: provider credential（SecretRef/env substitution の利用を推奨）。
- `models.providers.*.auth`: auth strategy（`api-key`、`token`、`oauth`、`aws-sdk`）。
- `models.providers.*.injectNumCtxForOpenAICompat`: Ollama + `openai-completions` 用に、request へ `options.num_ctx` を注入します（デフォルト: `true`）。
- `models.providers.*.authHeader`: 必要な場合に credential を `Authorization` header で送ることを強制します。
- `models.providers.*.baseUrl`: 上流 API の base URL。
- `models.providers.*.headers`: proxy/tenant routing 用の追加の static header。
- `models.providers.*.request`: model-provider HTTP request 用の transport 上書き。
  - `request.headers`: 追加の header（provider デフォルトとマージ）。値は SecretRef を受け付けます。
  - `request.auth`: auth strategy 上書き。mode: `"provider-default"`（provider 組み込み auth を使用）、`"authorization-bearer"`（`token` を使用）、`"header"`（`headerName`、`value`、オプションの `prefix` を使用）。
  - `request.proxy`: HTTP proxy 上書き。mode: `"env-proxy"`（`HTTP_PROXY`/`HTTPS_PROXY` 環境変数を使用）、`"explicit-proxy"`（`url` を使用）。両 mode ともオプションの `tls` サブオブジェクトを受け付けます。
  - `request.tls`: direct connection 用の TLS 上書き。フィールド: `ca`、`cert`、`key`、`passphrase`（すべて SecretRef を受け付けます）、`serverName`、`insecureSkipVerify`。
- `models.providers.*.models`: 明示的な provider model catalog エントリ。
- `models.providers.*.models.*.contextWindow`: ネイティブ model context window metadata。
- `models.providers.*.models.*.contextTokens`: オプションの runtime context cap。model のネイティブ `contextWindow` より小さい有効 context budget にしたい場合に使います。
- `models.providers.*.models.*.compat.supportsDeveloperRole`: オプションの互換性ヒント。`api: "openai-completions"` で `baseUrl` が空でない non-native URL（host が `api.openai.com` ではない）の場合、OpenClaw は runtime でこれを `false` に強制します。空または省略された `baseUrl` では OpenAI のデフォルト動作を維持します。
- `models.providers.*.models.*.compat.requiresStringContent`: string-only の OpenAI 互換 chat endpoint 用のオプション互換性ヒント。`true` の場合、OpenClaw は request を送る前に、純粋なテキスト `messages[].content` 配列をプレーン文字列へ flatten します。
- `plugins.entries.amazon-bedrock.config.discovery`: Bedrock auto-discovery 設定ルート。
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: 暗黙の discovery を有効/無効にします。
- `plugins.entries.amazon-bedrock.config.discovery.region`: discovery 用 AWS region。
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: 対象を絞った discovery 用のオプション provider-id filter。
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: discovery refresh の polling interval。
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: discovery された model 用の fallback context window。
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: discovery された model 用の fallback max output tokens。

### Provider の例

<Accordion title="Cerebras（GLM 4.6 / 4.7）">

```json5
{
  env: { CEREBRAS_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: {
        primary: "cerebras/zai-glm-4.7",
        fallbacks: ["cerebras/zai-glm-4.6"],
      },
      models: {
        "cerebras/zai-glm-4.7": { alias: "GLM 4.7 (Cerebras)" },
        "cerebras/zai-glm-4.6": { alias: "GLM 4.6 (Cerebras)" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      cerebras: {
        baseUrl: "https://api.cerebras.ai/v1",
        apiKey: "${CEREBRAS_API_KEY}",
        api: "openai-completions",
        models: [
          { id: "zai-glm-4.7", name: "GLM 4.7 (Cerebras)" },
          { id: "zai-glm-4.6", name: "GLM 4.6 (Cerebras)" },
        ],
      },
    },
  },
}
```

Cerebras には `cerebras/zai-glm-4.7` を、Z.AI direct には `zai/glm-4.7` を使用してください。

</Accordion>

<Accordion title="OpenCode">

```json5
{
  agents: {
    defaults: {
      model: { primary: "opencode/claude-opus-4-6" },
      models: { "opencode/claude-opus-4-6": { alias: "Opus" } },
    },
  },
}
```

`OPENCODE_API_KEY`（または `OPENCODE_ZEN_API_KEY`）を設定してください。Zen catalog には `opencode/...` 参照を、Go catalog には `opencode-go/...` 参照を使用します。ショートカット: `openclaw onboard --auth-choice opencode-zen` または `openclaw onboard --auth-choice opencode-go`。

</Accordion>

<Accordion title="Z.AI（GLM-4.7）">

```json5
{
  agents: {
    defaults: {
      model: { primary: "zai/glm-4.7" },
      models: { "zai/glm-4.7": {} },
    },
  },
}
```

`ZAI_API_KEY` を設定してください。`z.ai/*` と `z-ai/*` は受け付けられる別名です。ショートカット: `openclaw onboard --auth-choice zai-api-key`。

- 汎用 endpoint: `https://api.z.ai/api/paas/v4`
- コーディング endpoint（デフォルト）: `https://api.z.ai/api/coding/paas/v4`
- 汎用 endpoint を使う場合は、base URL 上書き付きのカスタム provider を定義してください。

</Accordion>

<Accordion title="Moonshot AI（Kimi）">

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: { "moonshot/kimi-k2.5": { alias: "Kimi K2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
        ],
      },
    },
  },
}
```

中国向け endpoint では `baseUrl: "https://api.moonshot.cn/v1"` または `openclaw onboard --auth-choice moonshot-api-key-cn` を使用してください。

ネイティブ Moonshot endpoint は共有 `openai-completions` transport での streaming 使用互換性を公開しており、OpenClaw は現在それを組み込み provider id 単独ではなく endpoint capability に基づいて判定します。

</Accordion>

<Accordion title="Kimi Coding">

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi/kimi-code" },
      models: { "kimi/kimi-code": { alias: "Kimi Code" } },
    },
  },
}
```

Anthropic 互換の組み込み provider です。ショートカット: `openclaw onboard --auth-choice kimi-code-api-key`。

</Accordion>

<Accordion title="Synthetic（Anthropic互換）">

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

base URL には `/v1` を含めないでください（Anthropic client が付加します）。ショートカット: `openclaw onboard --auth-choice synthetic-api-key`。

</Accordion>

<Accordion title="MiniMax M2.7（direct）">

```json5
{
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.7" },
      models: {
        "minimax/MiniMax-M2.7": { alias: "Minimax" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

`MINIMAX_API_KEY` を設定してください。ショートカット:
`openclaw onboard --auth-choice minimax-global-api` または
`openclaw onboard --auth-choice minimax-cn-api`。
model catalog は現在 M2.7 のみをデフォルトにしています。
Anthropic 互換 streaming path では、OpenClaw は MiniMax の thinking を
自分で明示設定しない限りデフォルトで無効にします。`/fast on` または
`params.fastMode: true` は `MiniMax-M2.7` を
`MiniMax-M2.7-highspeed` に書き換えます。

</Accordion>

<Accordion title="ローカルモデル（LM Studio）">

[Local Models](/ja-JP/gateway/local-models) を参照してください。要点: 十分なハードウェア上で LM Studio Responses API 経由の大きなローカル model を実行し、fallback 用にホスト型 model を merge したままにしておいてください。

</Accordion>

---

## Skills

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm", // npm | pnpm | yarn | bun
    },
    entries: {
      "image-lab": {
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // or plaintext string
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: bundled Skills のみを対象にするオプション許可リストです（managed/workspace Skills には影響しません）。
- `load.extraDirs`: 追加の共有 skill ルート（最も低い優先順位）。
- `install.preferBrew`: `true` の場合、`brew` が利用可能なら、他の installer 種別へフォールバックする前に Homebrew installer を優先します。
- `install.nodeManager`: `metadata.openclaw.install` 仕様向けの node installer 優先設定（`npm` | `pnpm` | `yarn` | `bun`）。
- `entries.<skillKey>.enabled: false` は、その skill が bundled/installed されていても無効化します。
- `entries.<skillKey>.apiKey`: primary env var を宣言する skill のための簡易 API key フィールド（プレーンテキスト文字列または SecretRef オブジェクト）。

---

## プラグイン

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: [],
    load: {
      paths: ["~/Projects/oss/voice-call-extension"],
    },
    entries: {
      "voice-call": {
        enabled: true,
        hooks: {
          allowPromptInjection: false,
        },
        config: { provider: "twilio" },
      },
    },
  },
}
```

- `~/.openclaw/extensions`、`<workspace>/.openclaw/extensions`、および `plugins.load.paths` からロードされます。
- discovery は、ネイティブ OpenClaw plugin に加え、互換性のある Codex bundle と Claude bundle、manifest を持たない Claude デフォルトレイアウト bundle も受け付けます。
- **設定変更には Gateway の再起動が必要です。**
- `allow`: オプションの許可リスト（列挙された plugin のみロード）。`deny` が優先されます。
- `