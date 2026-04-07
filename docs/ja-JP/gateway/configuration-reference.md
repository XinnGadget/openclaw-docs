---
read_when:
    - 正確なフィールド単位の設定セマンティクスやデフォルト値が必要な場合
    - チャネル、モデル、Gateway、またはツールの設定ブロックを検証している場合
summary: すべての OpenClaw 設定キー、デフォルト値、チャネル設定の完全なリファレンス
title: 設定リファレンス
x-i18n:
    generated_at: "2026-04-07T04:47:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7768cb77e1d3fc483c66f655ea891d2c32f21b247e3c1a56a919b28a37f9b128
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# 設定リファレンス

`~/.openclaw/openclaw.json` で利用できるすべてのフィールドです。タスク指向の概要については、[Configuration](/ja-JP/gateway/configuration) を参照してください。

設定形式は **JSON5** です（コメントと末尾カンマを使用可能）。すべてのフィールドは任意で、省略時は OpenClaw が安全なデフォルト値を使用します。

---

## チャネル

各チャネルは、その設定セクションが存在すると自動的に起動します（`enabled: false` の場合を除く）。

### DM とグループのアクセス

すべてのチャネルは DM ポリシーとグループポリシーをサポートします。

| DM policy | 動作 |
| ------------------- | --------------------------------------------------------------- |
| `pairing`（デフォルト） | 未知の送信者には 1 回限りのペアリングコードが送られ、owner が承認する必要があります |
| `allowlist` | `allowFrom` 内の送信者のみ（またはペアリング済み allow ストア） |
| `open` | すべての受信 DM を許可します（`allowFrom: ["*"]` が必要） |
| `disabled` | すべての受信 DM を無視します |

| Group policy | 動作 |
| --------------------- | ------------------------------------------------------ |
| `allowlist`（デフォルト） | 設定された allowlist に一致するグループのみ |
| `open` | グループ allowlist をバイパスします（メンションゲーティングは引き続き適用） |
| `disabled` | すべてのグループ/room メッセージをブロックします |

<Note>
`channels.defaults.groupPolicy` は、プロバイダーの `groupPolicy` が未設定の場合のデフォルトを設定します。
ペアリングコードの有効期限は 1 時間です。保留中の DM ペアリング要求は **各チャネル 3 件まで** に制限されます。
プロバイダーブロック自体が完全に欠落している場合（`channels.<provider>` が存在しない場合）、実行時のグループポリシーは起動時警告とともに `allowlist`（フェイルクローズド）にフォールバックします。
</Note>

### チャネルごとのモデル上書き

`channels.modelByChannel` を使うと、特定のチャネル ID を特定のモデルに固定できます。値には `provider/model` または設定済みモデルエイリアスを指定できます。このチャネルマッピングは、セッションにすでにモデル上書きがない場合（たとえば `/model` で設定された場合）に適用されます。

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

### チャネルのデフォルトとハートビート

`channels.defaults` を使うと、プロバイダー間で共有するグループポリシーとハートビート動作を設定できます。

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

- `channels.defaults.groupPolicy`: プロバイダーレベルの `groupPolicy` が未設定のときのフォールバック用グループポリシーです。
- `channels.defaults.contextVisibility`: すべてのチャネルに対する補足コンテキスト可視性モードのデフォルトです。値: `all`（デフォルト、引用/スレッド/履歴コンテキストをすべて含める）、`allowlist`（allowlist に登録された送信者のコンテキストのみ含める）、`allowlist_quote`（allowlist と同じだが明示的な quote/reply コンテキストは保持）。チャネルごとの上書き: `channels.<channel>.contextVisibility`。
- `channels.defaults.heartbeat.showOk`: 正常なチャネル状態をハートビート出力に含めます。
- `channels.defaults.heartbeat.showAlerts`: 劣化/エラー状態をハートビート出力に含めます。
- `channels.defaults.heartbeat.useIndicator`: コンパクトなインジケータ形式のハートビート出力を描画します。

### WhatsApp

WhatsApp は Gateway の web チャネル（Baileys Web）経由で動作します。リンク済みセッションが存在すると自動的に起動します。

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

- 送信コマンドは、`default` アカウントが存在する場合はそのアカウントを、そうでなければ最初に設定されたアカウント ID（ソート順）をデフォルトで使用します。
- オプションの `channels.whatsapp.defaultAccount` は、設定済みアカウント ID と一致する場合、このフォールバックのデフォルトアカウント選択を上書きします。
- 従来の単一アカウント Baileys auth dir は、`openclaw doctor` により `whatsapp/default` に移行されます。
- アカウントごとの上書き: `channels.whatsapp.accounts.<id>.sendReadReceipts`, `channels.whatsapp.accounts.<id>.dmPolicy`, `channels.whatsapp.accounts.<id>.allowFrom`。

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

- Bot トークン: `channels.telegram.botToken` または `channels.telegram.tokenFile`（通常ファイルのみ。シンボリックリンクは拒否）で指定し、デフォルトアカウントには `TELEGRAM_BOT_TOKEN` をフォールバックとして使用できます。
- オプションの `channels.telegram.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。
- マルチアカウント構成（2 個以上のアカウント ID）では、フォールバックルーティングを避けるために明示的なデフォルト（`channels.telegram.defaultAccount` または `channels.telegram.accounts.default`）を設定してください。これがない、または無効な場合、`openclaw doctor` が警告します。
- `configWrites: false` は Telegram 起点の設定書き込み（supergroup ID 移行、`/config set|unset`）をブロックします。
- 最上位の `bindings[]` エントリで `type: "acp"` を使うと、フォーラムトピック向けの永続 ACP バインディングを設定できます（`match.peer.id` には正規の `chatId:topic:topicId` を使用）。フィールドの意味は [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings) と共通です。
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

- トークン: `channels.discord.token`。デフォルトアカウントのフォールバックとして `DISCORD_BOT_TOKEN` も使用できます。
- 明示的な Discord `token` を渡す直接送信 API 呼び出しでは、そのトークンがその呼び出しに使用されます。ただし、アカウントの retry/policy 設定はアクティブなランタイムスナップショットで選択されたアカウントから取得されます。
- オプションの `channels.discord.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。
- 配信ターゲットには `user:<id>`（DM）または `channel:<id>`（guild channel）を使用してください。プレーンな数値 ID は拒否されます。
- Guild slug は小文字で、空白は `-` に置き換えられます。channel キーには slug 化された名前（`#` なし）が使われます。guild ID の使用を推奨します。
- Bot が作成したメッセージはデフォルトで無視されます。`allowBots: true` で有効化されます。ボットへのメンションを含む bot メッセージのみ受け付けたい場合は `allowBots: "mentions"` を使用してください（自身のメッセージは引き続き除外されます）。
- `channels.discord.guilds.<id>.ignoreOtherMentions`（および channel 上書き）は、bot ではなく別のユーザーや role をメンションしたメッセージを破棄します（@everyone/@here は除外）。
- `maxLinesPerMessage`（デフォルト 17）は、2000 文字未満でも縦に長いメッセージを分割します。
- `channels.discord.threadBindings` は Discord の thread-bound ルーティングを制御します。
  - `enabled`: thread-bound session 機能の Discord 上書き（`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`, および bound delivery/routing）
  - `idleHours`: 非アクティブ時の自動 unfocus の Discord 上書き（時間単位、`0` で無効）
  - `maxAgeHours`: ハード最大保持時間の Discord 上書き（時間単位、`0` で無効）
  - `spawnSubagentSessions`: `sessions_spawn({ thread: true })` の自動 thread 作成/バインドを有効にする opt-in スイッチ
- 最上位の `bindings[]` エントリで `type: "acp"` を使うと、channel や thread 向けの永続 ACP バインディングを設定できます（`match.peer.id` に channel/thread id を使用）。フィールドの意味は [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings) と共通です。
- `channels.discord.ui.components.accentColor` は Discord components v2 コンテナのアクセントカラーを設定します。
- `channels.discord.voice` は Discord ボイスチャネル会話と、オプションの自動参加 + TTS 上書きを有効にします。
- `channels.discord.voice.daveEncryption` と `channels.discord.voice.decryptionFailureTolerance` は `@discordjs/voice` の DAVE オプションにそのまま渡されます（デフォルトは `true` と `24`）。
- OpenClaw は、復号失敗が繰り返された場合にボイスセッションを離脱・再参加することで、音声受信の回復も試みます。
- `channels.discord.streaming` は正規のストリームモードキーです。従来の `streamMode` と boolean の `streaming` 値は自動移行されます。
- `channels.discord.autoPresence` はランタイムの可用性を bot presence にマッピングします（healthy => online、degraded => idle、exhausted => dnd）し、オプションでステータステキストの上書きも可能です。
- `channels.discord.dangerouslyAllowNameMatching` は、可変な name/tag マッチングを再有効化します（非常用互換モード）。
- `channels.discord.execApprovals`: Discord ネイティブの exec 承認配信と承認者認可。
  - `enabled`: `true`、`false`、または `"auto"`（デフォルト）。auto モードでは、`approvers` または `commands.ownerAllowFrom` から承認者を解決できる場合に exec 承認が有効になります。
  - `approvers`: exec リクエストを承認できる Discord ユーザー ID。省略時は `commands.ownerAllowFrom` にフォールバックします。
  - `agentFilter`: オプションの agent ID allowlist。省略するとすべての agent の承認を転送します。
  - `sessionFilter`: オプションの session key パターン（部分文字列または regex）。
  - `target`: 承認プロンプトの送信先。`"dm"`（デフォルト）は承認者の DM に送信、`"channel"` は発信元 channel に送信、`"both"` は両方に送信します。target に `"channel"` が含まれる場合、ボタンを使用できるのは解決された承認者のみです。
  - `cleanupAfterResolve`: `true` の場合、承認・拒否・タイムアウト後に承認 DM を削除します。

**リアクション通知モード:** `off`（なし）、`own`（ボットのメッセージ、デフォルト）、`all`（すべてのメッセージ）、`allowlist`（`guilds.<id>.users` 由来の全メッセージ）。

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

- サービスアカウント JSON はインライン（`serviceAccount`）またはファイルベース（`serviceAccountFile`）で指定できます。
- サービスアカウントの SecretRef（`serviceAccountRef`）もサポートしています。
- 環境変数フォールバック: `GOOGLE_CHAT_SERVICE_ACCOUNT` または `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`。
- 配信ターゲットには `spaces/<spaceId>` または `users/<userId>` を使用してください。
- `channels.googlechat.dangerouslyAllowNameMatching` は、可変な email principal マッチングを再有効化します（非常用互換モード）。

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
- `botToken`、`appToken`、`signingSecret`、`userToken` はプレーンテキスト文字列または SecretRef オブジェクトを受け付けます。
- Slack アカウントのスナップショットには、`botTokenSource`、`botTokenStatus`、`appTokenStatus`、HTTP mode では `signingSecretStatus` など、認証情報ごとの source/status フィールドが含まれます。`configured_unavailable` は、そのアカウントが SecretRef で設定されているが、現在のコマンド/ランタイム経路では secret 値を解決できなかったことを意味します。
- `configWrites: false` は Slack 起点の設定書き込みをブロックします。
- オプションの `channels.slack.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。
- `channels.slack.streaming` は正規のストリームモードキーです。従来の `streamMode` と boolean の `streaming` 値は自動移行されます。
- 配信ターゲットには `user:<id>`（DM）または `channel:<id>` を使用してください。

**リアクション通知モード:** `off`、`own`（デフォルト）、`all`、`allowlist`（`reactionAllowlist` 由来）。

**スレッドセッション分離:** `thread.historyScope` はスレッド単位（デフォルト）またはチャネル共有です。`thread.inheritParent` は親チャネルの transcript を新しいスレッドにコピーします。

- `typingReaction` は返信処理中、受信した Slack メッセージに一時リアクションを追加し、完了時に削除します。`"hourglass_flowing_sand"` のような Slack の emoji shortcode を使用してください。
- `channels.slack.execApprovals`: Slack ネイティブの exec 承認配信と承認者認可。Discord と同じスキーマです: `enabled`（`true`/`false`/`"auto"`）、`approvers`（Slack ユーザー ID）、`agentFilter`、`sessionFilter`、`target`（`"dm"`、`"channel"`、または `"both"`）。

| アクショングループ | デフォルト | 注 |
| ------------ | ------- | ---------------------- |
| reactions | 有効 | React + リアクション一覧 |
| messages | 有効 | 読み取り/送信/編集/削除 |
| pins | 有効 | ピン留め/解除/一覧 |
| memberInfo | 有効 | メンバー情報 |
| emojiList | 有効 | カスタム絵文字一覧 |

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

チャットモード: `oncall`（@-mention で応答、デフォルト）、`onmessage`（すべてのメッセージ）、`onchar`（トリガープレフィックスで始まるメッセージ）。

Mattermost ネイティブコマンドが有効な場合:

- `commands.callbackPath` には完全 URL ではなくパス（例: `/api/channels/mattermost/command`）を指定する必要があります。
- `commands.callbackUrl` は OpenClaw Gateway エンドポイントを解決し、Mattermost サーバーから到達可能でなければなりません。
- ネイティブ slash callback は、slash command 登録時に Mattermost から返されるコマンドごとのトークンで認証されます。登録に失敗した場合、またはコマンドが有効化されていない場合、OpenClaw は `Unauthorized: invalid command token.` で callback を拒否します。
- 非公開/tailnet/internal の callback ホストでは、Mattermost が `ServiceSettings.AllowedUntrustedInternalConnections` に callback host/domain を含めることを要求する場合があります。完全 URL ではなく host/domain 値を使用してください。
- `channels.mattermost.configWrites`: Mattermost 起点の設定書き込みを許可または拒否します。
- `channels.mattermost.requireMention`: channel 内で返信する前に `@mention` を要求します。
- `channels.mattermost.groups.<channelId>.requireMention`: チャネルごとの mention-gating 上書き（デフォルトには `"*"` を使用）。
- オプションの `channels.mattermost.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。

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

**リアクション通知モード:** `off`、`own`（デフォルト）、`all`、`allowlist`（`reactionAllowlist` 由来）。

- `channels.signal.account`: チャネル起動を特定の Signal アカウント identity に固定します。
- `channels.signal.configWrites`: Signal 起点の設定書き込みを許可または拒否します。
- オプションの `channels.signal.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。

### BlueBubbles

BlueBubbles は推奨される iMessage 経路です（プラグインベース、`channels.bluebubbles` 配下で設定）。

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

- ここで扱う主要キーパス: `channels.bluebubbles`, `channels.bluebubbles.dmPolicy`。
- オプションの `channels.bluebubbles.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。
- 最上位の `bindings[]` エントリで `type: "acp"` を使うと、BlueBubbles 会話を永続 ACP セッションにバインドできます。`match.peer.id` には BlueBubbles の handle または target 文字列（`chat_id:*`, `chat_guid:*`, `chat_identifier:*`）を使用してください。共通のフィールド定義: [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings)。
- 完全な BlueBubbles チャネル設定は [BlueBubbles](/ja-JP/channels/bluebubbles) に記載されています。

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

- オプションの `channels.imessage.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。

- Messages DB への Full Disk Access が必要です。
- `chat_id:<id>` ターゲットを推奨します。チャット一覧表示には `imsg chats --limit 20` を使用してください。
- `cliPath` は SSH ラッパーを指すことができます。SCP による添付ファイル取得には `remoteHost`（`host` または `user@host`）を設定してください。
- `attachmentRoots` と `remoteAttachmentRoots` は受信添付ファイルパスを制限します（デフォルト: `/Users/*/Library/Messages/Attachments`）。
- SCP は strict host-key checking を使うため、relay host key がすでに `~/.ssh/known_hosts` に存在していることを確認してください。
- `channels.imessage.configWrites`: iMessage 起点の設定書き込みを許可または拒否します。
- 最上位の `bindings[]` エントリで `type: "acp"` を使うと、iMessage 会話を永続 ACP セッションにバインドできます。`match.peer.id` には正規化された handle または明示的な chat target（`chat_id:*`, `chat_guid:*`, `chat_identifier:*`）を使用してください。共通のフィールド定義: [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings)。

<Accordion title="iMessage SSH ラッパーの例">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix は拡張機能ベースで、`channels.matrix` 配下で設定します。

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

- トークン認証は `accessToken` を使用し、パスワード認証は `userId` + `password` を使用します。
- `channels.matrix.proxy` は Matrix の HTTP トラフィックを明示的な HTTP(S) プロキシ経由でルーティングします。名前付きアカウントでは `channels.matrix.accounts.<id>.proxy` で上書きできます。
- `channels.matrix.network.dangerouslyAllowPrivateNetwork` は private/internal homeserver を許可します。`proxy` とこの network opt-in は独立した制御です。
- `channels.matrix.defaultAccount` はマルチアカウント構成で優先アカウントを選択します。
- `channels.matrix.autoJoin` のデフォルトは `off` であり、`autoJoin: "allowlist"` と `autoJoinAllowlist`、または `autoJoin: "always"` を設定するまで、招待された room や新しい DM 風招待は無視されます。
- `channels.matrix.execApprovals`: Matrix ネイティブの exec 承認配信と承認者認可。
  - `enabled`: `true`、`false`、または `"auto"`（デフォルト）。auto モードでは、`approvers` または `commands.ownerAllowFrom` から承認者を解決できる場合に exec 承認が有効になります。
  - `approvers`: exec リクエストを承認できる Matrix ユーザー ID（例: `@owner:example.org`）。
  - `agentFilter`: オプションの agent ID allowlist。省略するとすべての agent の承認を転送します。
  - `sessionFilter`: オプションの session key パターン（部分文字列または regex）。
  - `target`: 承認プロンプトの送信先。`"dm"`（デフォルト）、`"channel"`（発信元 room）、または `"both"`。
  - アカウントごとの上書き: `channels.matrix.accounts.<id>.execApprovals`。
- `channels.matrix.dm.sessionScope` は Matrix DM をどのようにセッション化するかを制御します: `per-user`（デフォルト）はルーティング先 peer 単位で共有し、`per-room` は各 DM room を分離します。
- Matrix の status probe と live directory lookup は、ランタイムトラフィックと同じ proxy policy を使用します。
- 完全な Matrix 設定、ターゲティングルール、セットアップ例は [Matrix](/ja-JP/channels/matrix) に記載されています。

### Microsoft Teams

Microsoft Teams は拡張機能ベースで、`channels.msteams` 配下で設定します。

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

- ここで扱う主要キーパス: `channels.msteams`, `channels.msteams.configWrites`。
- 完全な Teams 設定（認証情報、webhook、DM/group policy、team/channel ごとの上書き）は [Microsoft Teams](/ja-JP/channels/msteams) に記載されています。

### IRC

IRC は拡張機能ベースで、`channels.irc` 配下で設定します。

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

- ここで扱う主要キーパス: `channels.irc`, `channels.irc.dmPolicy`, `channels.irc.configWrites`, `channels.irc.nickserv.*`。
- オプションの `channels.irc.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。
- 完全な IRC チャネル設定（host/port/TLS/channels/allowlists/mention gating）は [IRC](/ja-JP/channels/irc) に記載されています。

### マルチアカウント（すべてのチャネル）

チャネルごとに複数アカウントを実行できます（それぞれ独自の `accountId` を持ちます）。

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

- `accountId` が省略された場合、`default` が使用されます（CLI + routing）。
- 環境変数トークンは **default** アカウントにのみ適用されます。
- ベースのチャネル設定は、アカウントごとに上書きされない限りすべてのアカウントに適用されます。
- `bindings[].match.accountId` を使用すると、各アカウントを異なる agent にルーティングできます。
- 単一アカウントの最上位チャネル設定のまま、`openclaw channels add`（またはチャネルのオンボーディング）で non-default アカウントを追加すると、OpenClaw はまずアカウントスコープの最上位単一アカウント値をチャネルの account map に昇格させ、元のアカウントがそのまま動作するようにします。ほとんどのチャネルでは `channels.<channel>.accounts.default` に移動し、Matrix は既存の一致する named/default ターゲットを維持できる場合があります。
- 既存のチャネル専用 binding（`accountId` なし）はデフォルトアカウントに引き続き一致し、アカウントスコープ binding は任意のままです。
- `openclaw doctor --fix` も混在した形状を修復し、そのチャネルで選ばれた昇格先アカウントにアカウントスコープの最上位単一アカウント値を移動します。ほとんどのチャネルでは `accounts.default` を使用し、Matrix は既存の一致する named/default ターゲットを維持できる場合があります。

### その他の拡張チャネル

多くの拡張チャネルは `channels.<id>` として設定され、それぞれの専用チャネルページに記載されています（たとえば Feishu、Matrix、LINE、Nostr、Zalo、Nextcloud Talk、Synology Chat、Twitch など）。
完全なチャネル一覧は [Channels](/ja-JP/channels) を参照してください。

### グループチャットのメンションゲーティング

グループメッセージはデフォルトで **メンション必須** です（メタデータのメンションまたは安全な regex パターン）。WhatsApp、Telegram、Discord、Google Chat、iMessage のグループチャットに適用されます。

**メンション種別:**

- **メタデータメンション**: ネイティブのプラットフォーム @-mentions。WhatsApp の self-chat mode では無視されます。
- **テキストパターン**: `agents.list[].groupChat.mentionPatterns` にある安全な regex パターン。無効なパターンや安全でないネストした繰り返しは無視されます。
- メンションゲーティングは、検出が可能な場合（ネイティブメンションまたは少なくとも 1 つのパターンがある場合）にのみ適用されます。

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

`messages.groupChat.historyLimit` はグローバルデフォルトを設定します。チャネルは `channels.<channel>.historyLimit`（またはアカウントごと）で上書きできます。無効にするには `0` を設定してください。

#### DM 履歴上限

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

解決順序: DM ごとの上書き → プロバイダーデフォルト → 上限なし（すべて保持）。

対応チャネル: `telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`。

#### Self-chat mode

自分の電話番号を `allowFrom` に含めると self-chat mode が有効になり、ネイティブ @-mentions を無視してテキストパターンにのみ応答します。

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

<Accordion title="コマンド詳細">

- テキストコマンドは、先頭に `/` が付いた**単独メッセージ**である必要があります。
- `native: "auto"` は Discord/Telegram でネイティブコマンドを有効にし、Slack は無効のままにします。
- チャネルごとの上書き: `channels.discord.commands.native`（bool または `"auto"`）。`false` は以前登録済みのコマンドを解除します。
- `channels.telegram.customCommands` は Telegram ボットメニューに追加エントリを加えます。
- `bash: true` はホスト shell 用の `! <cmd>` を有効にします。`tools.elevated.enabled` と、送信者が `tools.elevated.allowFrom.<channel>` に含まれていることが必要です。
- `config: true` は `/config` を有効にします（`openclaw.json` の読み書き）。Gateway `chat.send` クライアントでは、永続的な `/config set|unset` 書き込みには `operator.admin` も必要です。読み取り専用の `/config show` は通常の書き込み権限を持つ operator クライアントでも引き続き利用できます。
- `channels.<provider>.configWrites` は、チャネルごとの設定変更を制御します（デフォルト: true）。
- マルチアカウントチャネルでは、`channels.<provider>.accounts.<id>.configWrites` も、そのアカウントを対象とする書き込み（たとえば `/allowlist --config --account <id>` や `/config set channels.<provider>.accounts.<id>...`）を制御します。
- `allowFrom` はプロバイダーごとです。設定されると、それが**唯一の**認可ソースになります（チャネル allowlist/ペアリング と `useAccessGroups` は無視されます）。
- `useAccessGroups: false` は、`allowFrom` が設定されていない場合、コマンドが access-group ポリシーをバイパスできるようにします。

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

システムプロンプトの Runtime 行に表示される、オプションの repository root です。未設定の場合、OpenClaw は workspace から上方向にたどって自動検出します。

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

`agents.list[].skills` を設定していない agent に適用される、オプションのデフォルト skill allowlist です。

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // inherits github, weather
      { id: "docs", skills: ["docs-search"] }, // replaces defaults
      { id: "locked-down", skills: [] }, // no skills
    ],
  },
}
```

- デフォルトで Skills を無制限にしたい場合は、`agents.defaults.skills` を省略してください。
- デフォルトを継承させたい場合は、`agents.list[].skills` を省略してください。
- Skills をなしにするには `agents.list[].skills: []` を設定します。
- `agents.list[].skills` が空でないリストの場合、それがその agent の最終セットになり、デフォルトとはマージされません。

### `agents.defaults.skipBootstrap`

workspace の bootstrap ファイル（`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`）の自動作成を無効にします。

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

workspace の bootstrap ファイルをシステムプロンプトに注入するタイミングを制御します。デフォルトは `"always"` です。

- `"continuation-skip"`: 安全な継続ターン（assistant の応答完了後）では、workspace bootstrap の再注入をスキップし、プロンプトサイズを削減します。heartbeat 実行と compact 後の再試行では引き続きコンテキストを再構築します。

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

workspace bootstrap ファイル 1 件あたりの文字数上限です。これを超えると切り詰められます。デフォルト: `20000`。

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

すべての workspace bootstrap ファイルにまたがって注入される文字数合計の上限です。デフォルト: `150000`。

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

bootstrap コンテキストが切り詰められたときに agent に見える警告文を制御します。
デフォルト: `"once"`。

- `"off"`: システムプロンプトに警告文を注入しません。
- `"once"`: 一意の切り詰めシグネチャごとに 1 回だけ警告を注入します（推奨）。
- `"always"`: 切り詰めがある場合、毎回警告を注入します。

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

provider 呼び出し前に、transcript/tool の image block における長辺の最大ピクセルサイズです。
デフォルト: `1200`。

通常、低い値ほど vision token 使用量とリクエスト payload サイズを減らせます。高い値ほど視覚的な細部をより保持します。

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

システムプロンプト用コンテキストのタイムゾーンです（メッセージ timestamp ではありません）。ホストのタイムゾーンにフォールバックします。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

システムプロンプト内の時刻形式です。デフォルト: `auto`（OS の設定に従う）。

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
  - オブジェクト形式は primary と順序付き failover model を設定します。
- `imageModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - `image` ツール経路で vision-model 設定として使用されます。
  - 選択済み/デフォルトの model が image input を受け付けられない場合のフォールバックルーティングにも使われます。
- `imageGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共有 image-generation capability と、今後の画像生成を行う tool/plugin surface で使用されます。
  - 代表的な値: ネイティブ Gemini 画像生成向け `google/gemini-3.1-flash-image-preview`、fal 向け `fal/fal-ai/flux/dev`、OpenAI Images 向け `openai/gpt-image-1`。
  - provider/model を直接選択する場合は、対応する provider auth/API key も設定してください（例: `google/*` には `GEMINI_API_KEY` または `GOOGLE_API_KEY`、`openai/*` には `OPENAI_API_KEY`、`fal/*` には `FAL_KEY`）。
  - 省略しても、`image_generate` は auth がある provider default を推測できます。まず現在の default provider を試し、その後 provider-id 順で残りの登録済み image-generation provider を試します。
- `musicGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共有 music-generation capability と組み込み `music_generate` ツールで使用されます。
  - 代表的な値: `google/lyria-3-clip-preview`、`google/lyria-3-pro-preview`、`minimax/music-2.5+`。
  - 省略しても、`music_generate` は auth がある provider default を推測できます。まず現在の default provider を試し、その後 provider-id 順で残りの登録済み music-generation provider を試します。
  - provider/model を直接選択する場合は、対応する provider auth/API key も設定してください。
- `videoGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共有 video-generation capability と組み込み `video_generate` ツールで使用されます。
  - 代表的な値: `qwen/wan2.6-t2v`、`qwen/wan2.6-i2v`、`qwen/wan2.6-r2v`、`qwen/wan2.6-r2v-flash`、`qwen/wan2.7-r2v`。
  - 省略しても、`video_generate` は auth がある provider default を推測できます。まず現在の default provider を試し、その後 provider-id 順で残りの登録済み video-generation provider を試します。
  - provider/model を直接選択する場合は、対応する provider auth/API key も設定してください。
  - バンドルされている Qwen video-generation provider は現在、最大 1 本の出力 video、1 枚の入力 image、4 本の入力 video、10 秒の長さ、および provider レベルの `size`、`aspectRatio`、`resolution`、`audio`、`watermark` オプションをサポートしています。
- `pdfModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - `pdf` ツールの model routing に使用されます。
  - 省略した場合、PDF ツールは `imageModel`、その後解決済みの session/default model にフォールバックします。
- `pdfMaxBytesMb`: `pdf` ツール呼び出し時に `maxBytesMb` が渡されなかった場合のデフォルト PDF サイズ上限です。
- `pdfMaxPages`: `pdf` ツールの extraction fallback mode で考慮されるデフォルト最大ページ数です。
- `verboseDefault`: agent のデフォルト verbose level。値: `"off"`, `"on"`, `"full"`。デフォルト: `"off"`。
- `elevatedDefault`: agent のデフォルト elevated-output level。値: `"off"`, `"on"`, `"ask"`, `"full"`。デフォルト: `"on"`。
- `model.primary`: 形式は `provider/model`（例: `openai/gpt-5.4`）。provider を省略すると、OpenClaw はまず alias を試し、次にその正確な model id に一致する一意の configured-provider を試し、最後に configured default provider にフォールバックします（非推奨の互換動作のため、明示的な `provider/model` を推奨）。その provider が設定済みの default model を提供しなくなっている場合、OpenClaw は古い削除済み provider default を表面化させる代わりに、最初の configured provider/model にフォールバックします。
- `models`: 設定済みの model catalog と `/model` 用 allowlist。各エントリには `alias`（ショートカット）と `params`（`temperature`、`maxTokens`、`cacheRetention`、`context1m` などの provider-specific パラメータ）を含められます。
- `params`: すべての model に適用される global default provider parameters。`agents.defaults.params` に設定します（例: `{ cacheRetention: "long" }`）。
- `params` のマージ優先順位（config）: `agents.defaults.params`（global base）が `agents.defaults.models["provider/model"].params`（per-model）で上書きされ、その後 `agents.list[].params`（一致する agent id）がキーごとに上書きします。詳細は [Prompt Caching](/ja-JP/reference/prompt-caching) を参照してください。
- これらのフィールドを変更する config writer（例: `/models set`, `/models set-image`, および fallback の追加/削除コマンド）は、正規の object form を保存し、可能な限り既存の fallback list を保持します。
- `maxConcurrent`: セッション間での agent 実行の最大並列数です（各 session 自体は引き続き直列化されます）。デフォルト: 4。

**組み込み alias shorthand**（model が `agents.defaults.models` にある場合のみ適用）:

| Alias | Model |
| ------------------- | -------------------------------------- |
| `opus` | `anthropic/claude-opus-4-6` |
| `sonnet` | `anthropic/claude-sonnet-4-6` |
| `gpt` | `openai/gpt-5.4` |
| `gpt-mini` | `openai/gpt-5.4-mini` |
| `gpt-nano` | `openai/gpt-5.4-nano` |
| `gemini` | `google/gemini-3.1-pro-preview` |
| `gemini-flash` | `google/gemini-3-flash-preview` |
| `gemini-flash-lite` | `google/gemini-3.1-flash-lite-preview` |

設定した alias は常にデフォルトより優先されます。

Z.AI の GLM-4.x model は、`--thinking off` を設定するか、`agents.defaults.models["zai/<model>"].params.thinking` を自分で定義しない限り、自動的に thinking mode を有効にします。
Z.AI model は、tool call streaming のために `tool_stream` をデフォルトで有効にします。無効にするには `agents.defaults.models["zai/<model>"].params.tool_stream` を `false` に設定してください。
Anthropic Claude 4.6 model は、明示的な thinking level が設定されていない場合、デフォルトで `adaptive` thinking を使用します。

### `agents.defaults.cliBackends`

テキスト専用のフォールバック実行用 CLI backend を任意で設定できます（tool call なし）。API provider が失敗したときのバックアップとして役立ちます。

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

- CLI backend は text-first で、tool は常に無効です。
- `sessionArg` が設定されている場合、session をサポートします。
- `imageArg` が file path を受け付ける場合、image pass-through をサポートします。

### `agents.defaults.heartbeat`

定期的な heartbeat 実行です。

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

- `every`: duration 文字列（ms/s/m/h）。デフォルト: `30m`（API-key auth）または `1h`（OAuth auth）。無効化するには `0m` に設定します。
- `suppressToolErrorWarnings`: `true` の場合、heartbeat 実行中の tool error warning payload を抑制します。
- `directPolicy`: direct/DM 配信ポリシー。`allow`（デフォルト）は direct-target 配信を許可します。`block` は direct-target 配信を抑制し、`reason=dm-blocked` を出力します。
- `lightContext`: `true` の場合、heartbeat 実行は軽量 bootstrap context を使用し、workspace bootstrap ファイルのうち `HEARTBEAT.md` のみを保持します。
- `isolatedSession`: `true` の場合、各 heartbeat 実行は prior conversation history のない新しい session で実行されます。cron の `sessionTarget: "isolated"` と同じ分離パターンです。heartbeat あたりの token コストを約 100K から約 2〜5K token に削減します。
- agent ごと: `agents.list[].heartbeat` を設定します。いずれかの agent が `heartbeat` を定義すると、heartbeat を実行するのは**その agent だけ**になります。
- Heartbeat は完全な agent turn を実行するため、短い間隔ほど token を多く消費します。

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
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

- `mode`: `default` または `safeguard`（長い履歴用の chunked summarization）。[Compaction](/ja-JP/concepts/compaction) を参照してください。
- `timeoutSeconds`: OpenClaw が中止するまでに 1 回の compaction 操作に許可される最大秒数です。デフォルト: `900`。
- `identifierPolicy`: `strict`（デフォルト）、`off`、または `custom`。`strict` は compaction summarization 中に組み込みの opaque identifier 保持ガイダンスを前置します。
- `identifierInstructions`: `identifierPolicy=custom` のときに使われる、オプションのカスタム identifier 保持テキストです。
- `postCompactionSections`: compaction 後に再注入する AGENTS.md の H2/H3 セクション名です。デフォルトは `["Session Startup", "Red Lines"]` で、再注入を無効化するには `[]` を設定します。未設定、または明示的にこのデフォルトの組み合わせに設定されている場合、従来の `Every Session` / `Safety` 見出しもレガシーフォールバックとして受け入れます。
- `model`: compaction summarization 専用のオプション `provider/model-id` 上書きです。メイン session は 1 つの model を維持しつつ、compaction summary は別の model で実行したい場合に使います。未設定の場合、compaction は session の primary model を使用します。
- `notifyUser`: `true` の場合、compaction 開始時にユーザーへ短い通知（例: 「Compacting context...」）を送ります。デフォルトでは compaction を無言で行うため無効です。
- `memoryFlush`: 自動 compaction 前の silent agentic turn で、永続 memory を保存します。workspace が read-only の場合はスキップされます。

### `agents.defaults.contextPruning`

LLM に送信する前に、メモリ内コンテキストから**古い tool result**を刈り込みます。ディスク上の session history は変更しません。

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

- `mode: "cache-ttl"` は pruning pass を有効にします。
- `ttl` は pruning を再実行できる頻度を制御します（最後の cache touch 後）。
- pruning はまず oversized な tool result を soft-trim し、その後必要に応じて古い tool result を hard-clear します。

**Soft-trim** は先頭と末尾を保持し、中間に `...` を挿入します。

**Hard-clear** は tool result 全体を placeholder に置き換えます。

注:

- image block は切り詰め/削除されません。
- 比率は文字数ベース（概算）であり、正確な token 数ではありません。
- `keepLastAssistants` より少ない assistant message しか存在しない場合、pruning はスキップされます。

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

- Telegram 以外のチャネルでは、block reply を有効にするには明示的な `*.blockStreaming: true` が必要です。
- チャネルごとの上書き: `channels.<channel>.blockStreamingCoalesce`（およびアカウントごとのバリアント）。Signal/Slack/Discord/Google Chat のデフォルトは `minChars: 1500`。
- `humanDelay`: block reply 間のランダムな待機。`natural` = 800〜2500ms。agent ごとの上書き: `agents.list[].humanDelay`。

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

- デフォルト: direct chat/mention では `instant`、メンションなしの group chat では `message`。
- session ごとの上書き: `session.typingMode`, `session.typingIntervalSeconds`。

詳細は [Typing Indicators](/ja-JP/concepts/typing-indicators) を参照してください。

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

埋め込み agent 向けのオプション sandboxing です。完全なガイドは [Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。

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

<Accordion title="Sandbox 詳細">

**Backend:**

- `docker`: ローカル Docker runtime（デフォルト）
- `ssh`: 汎用 SSH ベースの remote runtime
- `openshell`: OpenShell runtime

`backend: "openshell"` を選択すると、runtime 固有の設定は
`plugins.entries.openshell.config` に移動します。

**SSH backend 設定:**

- `target`: `user@host[:port]` 形式の SSH target
- `command`: SSH client command（デフォルト: `ssh`）
- `workspaceRoot`: scope ごとの workspace に使う絶対 remote root
- `identityFile` / `certificateFile` / `knownHostsFile`: OpenSSH に渡される既存のローカルファイル
- `identityData` / `certificateData` / `knownHostsData`: OpenClaw が実行時に temp file として実体化する inline 内容または SecretRef
- `strictHostKeyChecking` / `updateHostKeys`: OpenSSH の host-key policy 設定

**SSH auth の優先順位:**

- `identityData` は `identityFile` より優先
- `certificateData` は `certificateFile` より優先
- `knownHostsData` は `knownHostsFile` より優先
- SecretRef ベースの `*Data` 値は、sandbox session 開始前にアクティブな secrets runtime snapshot から解決されます

**SSH backend の動作:**

- create または recreate 後に remote workspace を一度だけ seed します
- その後は remote SSH workspace を canonical として維持します
- `exec`、file tool、media path を SSH 経由でルーティングします
- remote の変更をホストへ自動同期しません
- sandbox browser container はサポートしません

**Workspace access:**

- `none`: `~/.openclaw/sandboxes` 配下の scope ごとの sandbox workspace
- `ro`: `/workspace` に sandbox workspace、agent workspace は `/agent` に read-only マウント
- `rw`: agent workspace を `/workspace` に read/write マウント

**Scope:**

- `session`: session ごとの container + workspace
- `agent`: agent ごとに 1 つの container + workspace（デフォルト）
- `shared`: 共有 container と workspace（session 間分離なし）

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

**OpenShell モード:**

- `mirror`: exec 前に local から remote を seed し、exec 後に同期を戻す。local workspace が canonical のまま
- `remote`: sandbox 作成時に remote を 1 回 seed し、その後は remote workspace を canonical として維持

`remote` モードでは、OpenClaw 外で行われたホストローカル編集は、seed ステップ後に sandbox に自動同期されません。
転送は SSH 経由で OpenShell sandbox に入りますが、sandbox lifecycle とオプションの mirror sync は plugin が管理します。

**`setupCommand`** は container 作成後に 1 回だけ（`sh -lc` 経由で）実行されます。network egress、書き込み可能な root、root user が必要です。

**Container のデフォルトは `network: "none"`** です。agent が outbound access を必要とする場合は `"bridge"`（またはカスタム bridge network）に設定してください。
`"host"` はブロックされます。`"container:<id>"` もデフォルトではブロックされ、明示的に
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` を設定した場合のみ許可されます（非常用）。

**受信添付ファイル** は、アクティブ workspace の `media/inbound/*` に staged されます。

**`docker.binds`** は追加の host directory をマウントします。global と agent ごとの bind はマージされます。

**Sandboxed browser**（`sandbox.browser.enabled`）: container 内の Chromium + CDP。システムプロンプトに noVNC URL が注入されます。`openclaw.json` の `browser.enabled` は不要です。
noVNC の observer access はデフォルトで VNC auth を使い、OpenClaw は共有 URL に password を露出せず、短命 token URL を発行します。

- `allowHostControl: false`（デフォルト）は、sandboxed session が host browser をターゲットにすることを防ぎます。
- `network` のデフォルトは `openclaw-sandbox-browser`（専用 bridge network）です。グローバル bridge 接続を明示的に望む場合のみ `bridge` に設定してください。
- `cdpSourceRange` は、container edge での CDP ingress を CIDR 範囲（例: `172.21.0.1/32`）に制限できます。
- `sandbox.browser.binds` は追加の host directory を browser container のみにマウントします。設定されると（`[]` を含む）、browser container では `docker.binds` の代わりにこれが使われます。
- 起動デフォルトは `scripts/sandbox-browser-entrypoint.sh` に定義され、container host 向けに調整されています:
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
  - `--disable-3d-apis`, `--disable-software-rasterizer`, `--disable-gpu` はデフォルトで有効で、WebGL/3D 利用で必要な場合は `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` で無効化できます。
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` で、workflow が依存している場合に extensions を再有効化できます。
  - `--renderer-process-limit=2` は `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` で変更可能です。Chromium のデフォルト process limit を使うには `0` を設定してください。
  - `noSandbox` が有効な場合は、これに加えて `--no-sandbox` と `--disable-setuid-sandbox`。
  - これらのデフォルトは container image のベースラインです。container デフォルトを変更したい場合は、カスタム browser image とカスタム entrypoint を使ってください。

</Accordion>

Browser sandboxing と `sandbox.docker.binds` は現在 Docker 専用です。

イメージをビルドするには:

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
- `default`: 複数設定された場合は最初が勝ちます（警告を出力）。どれも設定されていない場合、list の先頭エントリがデフォルトです。
- `model`: 文字列形式は `primary` のみを上書きし、オブジェクト形式 `{ primary, fallbacks }` は両方を上書きします（`[]` で global fallback を無効化）。`primary` のみを上書きする cron job は、`fallbacks: []` を設定しない限り、デフォルト fallback を引き続き継承します。
- `params`: `agents.defaults.models` にある選択済み model エントリの上にマージされる、agent ごとの stream params です。`cacheRetention`、`temperature`、`maxTokens` などの agent 固有上書きに使えます。model catalog 全体を複製する必要はありません。
- `skills`: オプションの agent ごとの skill allowlist。省略時、その agent は `agents.defaults.skills` が設定されていればそれを継承します。明示的な list はデフォルトとマージせず置き換え、`[]` は Skills なしを意味します。
- `thinkingDefault`: オプションの agent ごとのデフォルト thinking level（`off | minimal | low | medium | high | xhigh | adaptive`）。メッセージごとまたは session ごとの上書きがない場合、この agent では `agents.defaults.thinkingDefault` を上書きします。
- `reasoningDefault`: オプションの agent ごとのデフォルト reasoning visibility（`on | off | stream`）。メッセージごとまたは session ごとの reasoning 上書きがない場合に適用されます。
- `fastModeDefault`: オプションの agent ごとの fast mode デフォルト（`true | false`）。メッセージごとまたは session ごとの fast-mode 上書きがない場合に適用されます。
- `runtime`: オプションの agent ごとの runtime descriptor。agent に既定で ACP harness session を使わせたい場合は、`type: "acp"` と `runtime.acp` のデフォルト（`agent`, `backend`, `mode`, `cwd`）を使います。
- `identity.avatar`: workspace 相対パス、`http(s)` URL、または `data:` URI。
- `identity` はデフォルトを導出します: `ackReaction` は `emoji` から、`mentionPatterns` は `name`/`emoji` から導出されます。
- `subagents.allowAgents`: `sessions_spawn` 用の agent id allowlist（`["*"]` = 任意、デフォルト: 同じ agent のみ）。
- Sandbox 継承ガード: リクエスター session が sandboxed の場合、`sessions_spawn` は unsandboxed に実行されるターゲットを拒否します。
- `subagents.requireAgentId`: `true` の場合、`agentId` を省略した `sessions_spawn` 呼び出しをブロックします（明示的な profile 選択を強制。デフォルト: false）。

---

## マルチエージェントルーティング

1 つの Gateway 内で複数の分離された agent を実行します。[Multi-Agent](/ja-JP/concepts/multi-agent) を参照してください。

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

### Binding のマッチフィールド

- `type`（任意）: 通常ルーティング用の `route`（type 未指定は route）、永続 ACP 会話 binding 用の `acp`
- `match.channel`（必須）
- `match.accountId`（任意。`*` = 任意のアカウント、未指定 = デフォルトアカウント）
- `match.peer`（任意。`{ kind: direct|group|channel, id }`）
- `match.guildId` / `match.teamId`（任意。チャネル固有）
- `acp`（任意。`type: "acp"` のみ）: `{ mode, label, cwd, backend }`

**決定的なマッチ順序:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId`（exact、peer/guild/team なし）
5. `match.accountId: "*"`（channel-wide）
6. デフォルト agent

各 tier 内では、最初に一致した `bindings` エントリが勝ちます。

`type: "acp"` のエントリでは、OpenClaw は正確な会話 identity（`match.channel` + account + `match.peer.id`）で解決し、上記の route binding tier 順序は使用しません。

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

<Accordion title="読み取り専用ツール + workspace">

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

<Accordion title="セッションフィールド詳細">

- **`scope`**: group-chat context 用の基本 session grouping 戦略です。
  - `per-sender`（デフォルト）: チャネル context 内で送信者ごとに分離された session。
  - `global`: チャネル context 内のすべての参加者が 1 つの session を共有します（共有 context が意図される場合のみ使用）。
- **`dmScope`**: DM をどのようにグループ化するか。
  - `main`: すべての DM が main session を共有。
  - `per-peer`: チャネルをまたいで送信者 id ごとに分離。
  - `per-channel-peer`: チャネル + 送信者ごとに分離（複数ユーザーの inbox に推奨）。
  - `per-account-channel-peer`: account + channel + sender ごとに分離（マルチアカウントに推奨）。
- **`identityLinks`**: チャネル間 session 共有用の、canonical id から provider-prefixed peer へのマップ。
- **`reset`**: 主要 reset policy。`daily` はローカル時刻の `atHour` に reset、`idle` は `idleMinutes` 後に reset。両方設定されている場合、先に期限切れになった方が適用されます。
- **`resetByType`**: type ごとの上書き（`direct`, `group`, `thread`）。従来の `dm` は `direct` のエイリアスとして受け付けます。
- **`parentForkMaxTokens`**: fork された thread session を作成する際に許可される親 session の `totalTokens` 上限（デフォルト `100000`）。
  - 親の `totalTokens` がこの値を超える場合、OpenClaw は親 transcript history を継承せず、新しい thread session を開始します。
  - このガードを無効にし、常に parent fork を許可するには `0` を設定します。
- **`mainKey`**: 従来フィールドです。runtime は現在、main direct-chat bucket に常に `"main"` を使用します。
- **`agentToAgent.maxPingPongTurns`**: agent 間やり取りでの reply-back turn の最大数（整数、範囲: `0`–`5`）。`0` は ping-pong chaining を無効化します。
- **`sendPolicy`**: `channel`、`chatType`（`direct|group|channel`。従来の `dm` エイリアスあり）、`keyPrefix`、`rawKeyPrefix` によるマッチ。最初の deny が勝ちます。
- **`maintenance`**: session-store のクリーンアップ + 保持制御。
  - `mode`: `warn` は警告のみ、`enforce` はクリーンアップを適用。
  - `pruneAfter`: 古いエントリの年齢しきい値（デフォルト `30d`）。
  - `maxEntries`: `sessions.json` 内の最大エントリ数（デフォルト `500`）。
  - `rotateBytes`: `sessions.json` がこのサイズを超えたらローテート（デフォルト `10mb`）。
  - `resetArchiveRetention`: `*.reset.<timestamp>` transcript archive の保持期間。デフォルトは `pruneAfter`。無効にするには `false` を設定。
  - `maxDiskBytes`: オプションの sessions directory のディスク予算。`warn` モードでは警告し、`enforce` モードでは最も古い artifact/session から削除します。
  - `highWaterBytes`: 予算クリーンアップ後の目標値。デフォルトは `maxDiskBytes` の `80%`。
- **`threadBindings`**: thread-bound session 機能のグローバルデフォルト。
  - `enabled`: マスターのデフォルトスイッチ（プロバイダーごとに上書き可能。Discord は `channels.discord.threadBindings.enabled` を使用）
  - `idleHours`: 非アクティブ時の自動 unfocus のデフォルト時間（`0` で無効。プロバイダーごとに上書き可能）
  - `maxAgeHours`: ハード最大保持時間のデフォルト（`0` で無効。プロバイダーごとに上書き可能）

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

### 応答プレフィックス

チャネル/アカウントごとの上書き: `channels.<channel>.responsePrefix`, `channels.<channel>.accounts.<id>.responsePrefix`。

解決順序（より具体的なものが優先）: account → channel → global。`""` は無効化して cascade を止めます。`"auto"` は `[{identity.name}]` を導出します。

**テンプレート変数:**

| Variable | 説明 | 例 |
| ----------------- | ---------------------- | --------------------------- |
| `{model}` | 短い model 名 | `claude-opus-4-6` |
| `{modelFull}` | 完全な model identifier | `anthropic/claude-opus-4-6` |
| `{provider}` | provider 名 | `anthropic` |
| `{thinkingLevel}` | 現在の thinking level | `high`, `low`, `off` |
| `{identity.name}` | agent identity 名 | （`"auto"` と同じ） |

変数は大文字小文字を区別しません。`{think}` は `{thinkingLevel}` のエイリアスです。

### Ack reaction

- デフォルトはアクティブ agent の `identity.emoji`、なければ `"👀"` です。無効にするには `""` を設定します。
- チャネルごとの上書き: `channels.<channel>.ackReaction`, `channels.<channel>.accounts.<id>.ackReaction`。
- 解決順序: account → channel → `messages.ackReaction` → identity fallback。
- Scope: `group-mentions`（デフォルト）、`group-all`、`direct`、`all`。
- `removeAckAfterReply`: Slack、Discord、Telegram で reply 後に ack を削除します。
- `messages.statusReactions.enabled`: Slack、Discord、Telegram で lifecycle status reaction を有効にします。
  Slack と Discord では、未設定の場合 ack reaction が有効なとき status reaction も有効のままです。
  Telegram では、lifecycle status reaction を有効にするには明示的に `true` を設定してください。

### 受信 debounce

同じ送信者からの連続するテキストメッセージを 1 つの agent turn にまとめます。media/attachment は即時 flush されます。control command は debouncing をバイパスします。

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
- `modelOverrides` はデフォルトで有効です。`modelOverrides.allowProvider` のデフォルトは `false`（opt-in）です。
- API key は `ELEVENLABS_API_KEY`/`XI_API_KEY` および `OPENAI_API_KEY` にフォールバックします。
- `openai.baseUrl` は OpenAI TTS endpoint を上書きします。解決順序は config、次に `OPENAI_TTS_BASE_URL`、最後に `https://api.openai.com/v1` です。
- `openai.baseUrl` が非 OpenAI endpoint を指す場合、OpenClaw はそれを OpenAI 互換 TTS server として扱い、model/voice validation を緩和します。

---

## Talk

Talk mode（macOS/iOS/Android）のデフォルトです。

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

- 複数の Talk provider が設定されている場合、`talk.provider` は `talk.providers` のキーと一致している必要があります。
- 従来のフラットな Talk キー（`talk.voiceId`, `talk.voiceAliases`, `talk.modelId`, `talk.outputFormat`, `talk.apiKey`）は互換性維持専用であり、自動的に `talk.providers.<provider>` に移行されます。
- Voice ID は `ELEVENLABS_VOICE_ID` または `SAG_VOICE_ID` にフォールバックします。
- `providers.*.apiKey` はプレーンテキスト文字列または SecretRef オブジェクトを受け付けます。
- `ELEVENLABS_API_KEY` のフォールバックは、Talk API key が設定されていない場合にのみ適用されます。
- `providers.*.voiceAliases` を使うと、Talk directive でフレンドリーな名前を使えます。
- `silenceTimeoutMs` は、Talk mode がユーザーの無音後に transcript を送信するまでの待機時間を制御します。未設定の場合、プラットフォームのデフォルト待機時間（macOS と Android は `700 ms`、iOS は `900 ms`）を使います。

---

## ツール

### Tool profile

`tools.profile` は `tools.allow`/`tools.deny` より前にベース allowlist を設定します。

ローカルオンボーディングでは、未設定の新しいローカル構成に `tools.profile: "coding"` をデフォルト設定します（既存の明示的 profile は保持されます）。

| Profile | 含まれるもの |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `minimal` | `session_status` のみ |
| `coding` | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status` |
| `full` | 制限なし（未設定と同じ） |

### Tool group

| Group | Tools |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `group:runtime` | `exec`, `process`, `code_execution`（`bash` は `exec` のエイリアスとして受け付けます） |
| `group:fs` | `read`, `write`, `edit`, `apply_patch` |
| `group:sessions` | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory` | `memory_search`, `memory_get` |
| `group:web` | `web_search`, `x_search`, `web_fetch` |
| `group:ui` | `browser`, `canvas` |
| `group:automation` | `cron`, `gateway` |
| `group:messaging` | `message` |
| `group:nodes` | `nodes` |
| `group:agents` | `agents_list` |
| `group:media` | `image`, `image_generate`, `video_generate`, `tts` |
| `group:openclaw` | すべての組み込み tool（provider plugin は除外） |

### `tools.allow` / `tools.deny`

グローバルな tool 許可/拒否ポリシーです（deny が優先）。大文字小文字を区別せず、`*` ワイルドカードをサポートします。Docker sandbox が off でも適用されます。

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

特定の provider または model に対して tool をさらに制限します。順序: base profile → provider profile → allow/deny。

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

sandbox 外での elevated exec access を制御します。

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

- agent ごとの上書き（`agents.list[].tools.elevated`）では、さらに制限することしかできません。
- `/elevated on|off|ask|full` は状態を session ごとに保存し、inline directive は単一メッセージに適用されます。
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

tool-loop の安全性チェックは**デフォルトで無効**です。有効にするには `enabled: true` を設定してください。
設定はグローバルな `tools.loopDetection` で定義でき、agent ごとの `agents.list[].tools.loopDetection` で上書きできます。

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

- `historySize`: loop 分析用に保持する tool-call history の最大数。
- `warningThreshold`: 警告を出す繰り返し no-progress パターンのしきい値。
- `criticalThreshold`: 重大な loop をブロックするための、より高い繰り返ししきい値。
- `globalCircuitBreakerThreshold`: あらゆる no-progress 実行を強制停止するハードしきい値。
- `detectors.genericRepeat`: 同じ tool/同じ args の繰り返し呼び出しで警告。
- `detectors.knownPollNoProgress`: 既知の poll tool（`process.poll`, `command_status` など）で警告/ブロック。
- `detectors.pingPong`: 交互に現れる no-progress のペアパターンで警告/ブロック。
- `warningThreshold >= criticalThreshold` または `criticalThreshold >= globalCircuitBreakerThreshold` の場合、validation は失敗します。

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

<Accordion title="Media model エントリフィールド">

**Provider エントリ**（`type: "provider"` または省略時）:

- `provider`: API provider id（`openai`、`anthropic`、`google`/`gemini`、`groq` など）
- `model`: model id 上書き
- `profile` / `preferredProfile`: `auth-profiles.json` の profile 選択

**CLI エントリ**（`type: "cli"`）:

- `command`: 実行する executable
- `args`: テンプレート化された args（`{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}` などをサポート）

**共通フィールド:**

- `capabilities`: オプションのリスト（`image`, `audio`, `video`）。デフォルト: `openai`/`anthropic`/`minimax` → image、`google` → image+audio+video、`groq` → audio。
- `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`: エントリごとの上書き。
- 失敗時は次のエントリへフォールバックします。

Provider auth は標準順序に従います: `auth-profiles.json` → 環境変数 → `models.providers.*.apiKey`。

**Async completion フィールド:**

- `asyncCompletion.directSend`: `true` の場合、完了した非同期 `music_generate` と `video_generate` タスクは、まず直接チャネル配信を試みます。デフォルト: `false`（従来の requester-session wake/model-delivery 経路）。

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

session tool（`sessions_list`, `sessions_history`, `sessions_send`）で対象にできる session を制御します。

デフォルト: `tree`（現在の session + そこから spawn された session。subagent など）。

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

注:

- `self`: 現在の session key のみ。
- `tree`: 現在の session + 現在の session から spawn された session（subagent）。
- `agent`: 現在の agent id に属する任意の session（同じ agent id の下で per-sender session を運用している場合、他のユーザーも含まれる可能性があります）。
- `all`: 任意の session。cross-agent targeting には引き続き `tools.agentToAgent` が必要です。
- Sandbox clamp: 現在の session が sandboxed で、`agents.defaults.sandbox.sessionToolsVisibility="spawned"` の場合、`tools.sessions.visibility="all"` でも visibility は `tree` に強制されます。

### `tools.sessions_spawn`

`sessions_spawn` の inline attachment support を制御します。

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

注:

- Attachment は `runtime: "subagent"` でのみサポートされます。ACP runtime はこれを拒否します。
- ファイルは child workspace の `.openclaw/attachments/<uuid>/` に `.manifest.json` とともに実体化されます。
- Attachment 内容は transcript persistence から自動的に redact されます。
- Base64 input は厳格な alphabet/padding チェックと decode 前サイズガードで検証されます。
- ファイル権限は directory が `0700`、file が `0600` です。
- クリーンアップは `cleanup` policy に従います: `delete` は常に attachment を削除し、`keep` は `retainOnSessionKeep: true` の場合のみ保持します。

### `tools.experimental`

実験的な組み込み tool フラグです。runtime 固有の auto-enable ルールが適用される場合を除き、デフォルトは off です。

```json5
{
  tools: {
    experimental: {
      planTool: true, // enable experimental update_plan
    },
  },
}
```

注:

- `planTool`: 構造化された `update_plan` ツールを有効にし、複雑な複数ステップ作業の追跡に使います。
- デフォルト: 非 OpenAI provider では `false`。OpenAI と OpenAI Codex 実行では自動有効化されます。
- 有効な場合、システムプロンプトにも使用ガイダンスが追加され、モデルは substantial work にのみ使用し、`in_progress` のステップを最大 1 つまでに保ちます。

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

- `model`: spawn される sub-agent のデフォルト model。省略時、sub-agent は caller の model を継承します。
- `allowAgents`: リクエスター agent が独自の `subagents.allowAgents` を設定していない場合の、`sessions_spawn` 対象 agent id のデフォルト allowlist（`["*"]` = 任意、デフォルト: 同じ agent のみ）。
- `runTimeoutSeconds`: tool call で `runTimeoutSeconds` が省略された場合の `sessions_spawn` のデフォルト timeout（秒）。`0` は無制限。
- subagent ごとの tool policy: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`。

---

## カスタム provider と base URL

OpenClaw は組み込み model catalog を使用します。カスタム provider は config の `models.providers` または `~/.openclaw/agents/<agentId>/agent/models.json` で追加できます。

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

- カスタム auth が必要な場合は `authHeader: true` + `headers` を使用してください。
- agent config root は `OPENCLAW_AGENT_DIR`（または従来の環境変数エイリアス `PI_CODING_AGENT_DIR`）で上書きできます。
- 一致する provider ID に対するマージ優先順位:
  - 空でない agent `models.json` の `baseUrl` が優先されます。
  - 空でない agent の `apiKey` は、その provider が現在の config/auth-profile context で SecretRef 管理されていない場合にのみ優先されます。
  - SecretRef 管理の provider `apiKey` は、解決済み secret を保持する代わりに source marker（env ref なら `ENV_VAR_NAME`、file/exec ref なら `secretref-managed`）から更新されます。
  - SecretRef 管理の provider header 値は、source marker（env ref なら `secretref-env:ENV_VAR_NAME`、file/exec ref なら `secretref-managed`）から更新されます。
  - agent の `apiKey`/`baseUrl` が空または欠落している場合は、config の `models.providers` にフォールバックします。
  - 一致する model の `contextWindow`/`maxTokens` には、明示的な config 値と暗黙 catalog 値の高い方が使われます。
  - 一致する model の `contextTokens` は、明示的な runtime cap が存在する場合それを保持します。モデル本来の metadata を変えずに有効 context を制限したい場合に使用してください。
  - config で `models.json` を完全に書き換えたい場合は `models.mode: "replace"` を使ってください。
  - Marker persistence は source-authoritative です。marker は解決済み runtime secret 値からではなく、アクティブな source config snapshot（解決前）から書き込まれます。

### Provider フィールド詳細

- `models.mode`: provider catalog の動作（`merge` または `replace`）。
- `models.providers`: provider id をキーにしたカスタム provider map。
- `models.providers.*.api`: リクエスト adapter（`openai-completions`、`openai-responses`、`anthropic-messages`、`google-generative-ai` など）。
- `models.providers.*.apiKey`: provider credential（SecretRef/env substitution 推奨）。
- `models.providers.*.auth`: auth strategy（`api-key`、`token`、`oauth`、`aws-sdk`）。
- `models.providers.*.injectNumCtxForOpenAICompat`: Ollama + `openai-completions` の場合、リクエストに `options.num_ctx` を注入します（デフォルト: `true`）。
- `models.providers.*.authHeader`: 必要な場合に credential を `Authorization` header で送るよう強制します。
- `models.providers.*.baseUrl`: upstream API の base URL。
- `models.providers.*.headers`: proxy/tenant routing 用の追加 static header。
- `models.providers.*.request`: model-provider HTTP request 用の transport override。
  - `request.headers`: 追加 header（provider default とマージ）。値は SecretRef を受け付けます。
  - `request.auth`: auth strategy override。モード: `"provider-default"`（provider 組み込み auth を使用）、`"authorization-bearer"`（`token` を使用）、`"header"`（`headerName`, `value`, 任意の `prefix` を使用）。
  - `request.proxy`: HTTP proxy override。モード: `"env-proxy"`（`HTTP_PROXY`/`HTTPS_PROXY` 環境変数を使用）、`"explicit-proxy"`（`url` を使用）。どちらのモードも任意の `tls` サブオブジェクトを受け付けます。
  - `request.tls`: 直接接続時の TLS override。フィールド: `ca`, `cert`, `key`, `passphrase`（すべて SecretRef 可）、`serverName`, `insecureSkipVerify`。
- `models.providers.*.models`: 明示的な provider model catalog エントリ。
- `models.providers.*.models.*.contextWindow`: model 本来の context window metadata。
- `models.providers.*.models.*.contextTokens`: オプションの runtime context cap。model 本来の `contextWindow` より小さい有効 context budget にしたい場合に使用します。
- `models.providers.*.models.*.compat.supportsDeveloperRole`: オプションの互換性ヒント。`api: "openai-completions"` かつ空でない非ネイティブの `baseUrl`（host が `api.openai.com` でない）の場合、OpenClaw は実行時にこれを `false` に強制します。`baseUrl` が空または省略されている場合は、OpenAI のデフォルト動作を維持します。
- `plugins.entries.amazon-bedrock.config.discovery`: Bedrock auto-discovery 設定のルート。
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: 暗黙 discovery のオン/オフ。
- `plugins.entries.amazon-bedrock.config.discovery.region`: discovery 用 AWS region。
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: 対象を絞るための任意の provider-id filter。
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: discovery refresh の polling interval。
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: 発見された model 用の fallback context window。
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: 発見された model 用の fallback max output tokens。

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

Cerebras には `cerebras/zai-glm-4.7` を、Z.AI 直結には `zai/glm-4.7` を使ってください。

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

`OPENCODE_API_KEY`（または `OPENCODE_ZEN_API_KEY`）を設定してください。Zen catalog には `opencode/...` 参照、Go catalog には `opencode-go/...` 参照を使用します。ショートカット: `openclaw onboard --auth-choice opencode-zen` または `openclaw onboard --auth-choice opencode-go`。

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

`ZAI_API_KEY` を設定してください。`z.ai/*` と `z-ai/*` は受け付けられるエイリアスです。ショートカット: `openclaw onboard --auth-choice zai-api-key`。

- 一般エンドポイント: `https://api.z.ai/api/paas/v4`
- Coding エンドポイント（デフォルト）: `https://api.z.ai/api/coding/paas/v4`
- 一般エンドポイントを使う場合は、base URL override を持つカスタム provider を定義してください。

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

中国向けエンドポイントでは `baseUrl: "https://api.moonshot.cn/v1"` または `openclaw onboard --auth-choice moonshot-api-key-cn` を使用してください。

ネイティブ Moonshot endpoint は共有 `openai-completions` transport 上での streaming usage 互換性を提示し、OpenClaw はそれを組み込み provider id 単独ではなく endpoint capability に基づいて判定するようになりました。

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

<Accordion title="Synthetic（Anthropic 互換）">

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

Base URL には `/v1` を含めないでください（Anthropic client が追加します）。ショートカット: `openclaw onboard --auth-choice synthetic-api-key`。

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
Anthropic 互換 streaming path では、明示的に `thinking` を設定しない限り、OpenClaw はデフォルトで MiniMax thinking を無効にします。`/fast on` または `params.fastMode: true` は `MiniMax-M2.7` を `MiniMax-M2.7-highspeed` に書き換えます。

</Accordion>

<Accordion title="ローカルモデル（LM Studio）">

[Local Models](/ja-JP/gateway/local-models) を参照してください。要点: 本格的なハードウェアでは LM Studio Responses API 経由で大きなローカル model を実行し、フォールバック用に hosted model は merged のままにしておきます。

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

- `allowBundled`: bundled skill のみを対象とするオプション allowlist です（managed/workspace skill には影響しません）。
- `load.extraDirs`: 追加の共有 skill root（最も低い優先順位）。
- `install.preferBrew`: `brew` が利用可能な場合、他の installer 種別にフォールバックする前に Homebrew installer を優先します。
- `install.nodeManager`: `metadata.openclaw.install` spec 用の node installer 優先設定（`npm` | `pnpm` | `yarn` | `bun`）。
- `entries.<skillKey>.enabled: false` は、その skill が bundled/installed であっても無効化します。
- `entries.<skillKey>.apiKey`: その skill が主要な env var を宣言している場合の簡易 API key フィールド（プレーンテキスト文字列または SecretRef オブジェクト）。

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

- `~/.openclaw/extensions`、`<workspace>/.openclaw/extensions`、および `plugins.load.paths` から読み込まれます。
- Discovery はネイティブ OpenClaw plugin に加え、互換性のある Codex bundle、Claude bundle、manifest を持たない Claude default-layout bundle も受け付けます。
- **設定変更には Gateway の再起動が必要です。**
- `allow`: オプションの allowlist（一覧にある plugin のみロード）。`deny` が優先されます。
- `plugins.entries.<id>.apiKey`: plugin がサポートしている場合の plugin レベル API key 簡易フィールド。
- `plugins.entries.<id>.env`: plugin スコープの env var map。
- `plugins.entries.<id>.hooks.allowPromptInjection`: `false` の場合、core は `before_prompt_build` をブロックし、legacy `before_agent_start` 由来の prompt を変更するフィールドを無視します。ただし legacy の `modelOverride` と `providerOverride` は保持します。ネイティブ plugin hook と、サポートされる bundle 提供 hook directory に適用されます。
- `plugins.entries.<id>.subagent.allowModelOverride`: この plugin が background subagent 実行時に `provider` と `model` の上書きを要求できることを明示的に信頼します。
- `plugins.entries.<id>.subagent.allowedModels`: trusted な subagent override に対する、正規の `provider/model` ターゲットのオプション allowlist。任意の model を許可したい意図がある場合のみ `"*"` を使ってください。
- `plugins.entries.<id>.config`: plugin 定義の config object（利用可能な場合はネイティブ OpenClaw plugin schema で検証されます）。
- `plugins.entries.firecrawl.config.webFetch`: Firecrawl web-fetch provider 設定。
  - `apiKey`: Firecrawl API key（SecretRef 可）。`plugins.entries.firecrawl.config.webSearch.apiKey`、従来の `tools.web.fetch.firecrawl.apiKey`、または `FIRECRAWL_API_KEY` 環境変数にフォールバックします。
  - `baseUrl`: Firecrawl API base URL（デフォルト: `https://api.firecrawl.dev`）。
  - `onlyMainContent`: ページから主要コンテンツのみを抽出します（デフォルト: `true`）。
  - `maxAgeMs`: キャッシュの最大有効期間（ミリ秒、デフォルト: `172800000` / 2 日）。
  - `timeoutSeconds`: scrape request timeout（秒、デフォルト: `60`）。
- `plugins.entries.xai.config.xSearch`: xAI X Search（Grok web search）設定。
  - `enabled`: X Search provider を有効化します。
  - `model`: search に使用する Grok model（例: `"grok-4-1-fast"`）。
- `plugins.entries.memory-core.config.dreaming`: memory dreaming（実験的）設定。phase と threshold については [Dreaming](/concepts