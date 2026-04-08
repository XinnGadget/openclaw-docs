---
read_when:
    - フィールド単位の正確な設定セマンティクスやデフォルト値が必要な場合
    - チャンネル、モデル、Gateway、またはツールの設定ブロックを検証している場合
summary: すべてのOpenClaw設定キー、デフォルト値、チャンネル設定の完全リファレンス
title: 設定リファレンス
x-i18n:
    generated_at: "2026-04-08T04:47:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: a22899b8f43a7819a2e27fae1bddbe67b29b314bce5a9844fc276482bda9156c
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# 設定リファレンス

`~/.openclaw/openclaw.json` で利用できるすべてのフィールド。タスク指向の概要については、[Configuration](/ja-JP/gateway/configuration) を参照してください。

設定形式は **JSON5** です（コメントと末尾カンマを許可）。すべてのフィールドは任意です。省略された場合、OpenClaw は安全なデフォルト値を使用します。

---

## チャンネル

各チャンネルは、その設定セクションが存在する場合に自動的に開始されます（`enabled: false` の場合を除く）。

### DM とグループアクセス

すべてのチャンネルは DM ポリシーとグループポリシーをサポートします。

| DM ポリシー        | 動作                                                           |
| ------------------ | -------------------------------------------------------------- |
| `pairing` (デフォルト) | 未知の送信者には 1 回限りのペアリングコードが送られ、所有者の承認が必要 |
| `allowlist`        | `allowFrom` 内の送信者のみ（またはペア済み許可ストア）             |
| `open`             | すべての受信 DM を許可（`allowFrom: ["*"]` が必要）               |
| `disabled`         | すべての受信 DM を無視                                          |

| グループポリシー      | 動作                                                   |
| --------------------- | ------------------------------------------------------ |
| `allowlist` (デフォルト) | 設定された許可リストに一致するグループのみ               |
| `open`                | グループ許可リストをバイパス（メンションゲートは引き続き適用） |
| `disabled`            | すべてのグループ/ルームメッセージをブロック               |

<Note>
`channels.defaults.groupPolicy` は、プロバイダーの `groupPolicy` が未設定の場合のデフォルトを設定します。
ペアリングコードの有効期限は 1 時間です。保留中の DM ペアリングリクエストは **チャンネルごとに 3 件まで** に制限されます。
プロバイダーブロック自体が完全に欠けている場合（`channels.<provider>` が存在しない場合）、ランタイムのグループポリシーは起動時警告付きで `allowlist`（fail-closed）にフォールバックします。
</Note>

### チャンネルごとのモデル上書き

特定のチャンネル ID をモデルに固定するには `channels.modelByChannel` を使用します。値には `provider/model` または設定済みモデルエイリアスを指定できます。チャンネルマッピングは、セッションにすでにモデル上書きがない場合（たとえば `/model` で設定された場合）に適用されます。

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

### チャンネルのデフォルト値とハートビート

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

- `channels.defaults.groupPolicy`: プロバイダーレベルの `groupPolicy` が未設定の場合のフォールバックグループポリシー。
- `channels.defaults.contextVisibility`: すべてのチャンネルのデフォルト補助コンテキスト可視性モード。値: `all`（デフォルト、引用/スレッド/履歴コンテキストをすべて含む）、`allowlist`（許可リストにある送信者のコンテキストのみ含む）、`allowlist_quote`（allowlist と同じだが明示的な引用/返信コンテキストは保持）。チャンネルごとの上書き: `channels.<channel>.contextVisibility`。
- `channels.defaults.heartbeat.showOk`: 正常なチャンネル状態をハートビート出力に含めます。
- `channels.defaults.heartbeat.showAlerts`: 劣化/エラー状態をハートビート出力に含めます。
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

<Accordion title="複数アカウントの WhatsApp">

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

- 送信コマンドは、`default` アカウントが存在する場合は既定でそれを使用し、存在しない場合は最初に設定されたアカウント ID（ソート順）を使用します。
- 任意の `channels.whatsapp.defaultAccount` は、設定済みアカウント ID に一致する場合、このフォールバックのデフォルトアカウント選択を上書きします。
- 旧来の単一アカウント Baileys 認証ディレクトリは、`openclaw doctor` により `whatsapp/default` へ移行されます。
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

- Bot トークン: `channels.telegram.botToken` または `channels.telegram.tokenFile`（通常ファイルのみ。シンボリックリンクは拒否）で指定し、デフォルトアカウントのフォールバックとして `TELEGRAM_BOT_TOKEN` も使用できます。
- 任意の `channels.telegram.defaultAccount` は、設定済みアカウント ID に一致する場合、デフォルトアカウント選択を上書きします。
- 複数アカウント構成（2 つ以上のアカウント ID）では、フォールバックルーティングを避けるために明示的なデフォルト（`channels.telegram.defaultAccount` または `channels.telegram.accounts.default`）を設定してください。これが欠けているか無効な場合、`openclaw doctor` が警告します。
- `configWrites: false` は Telegram 起点の設定書き込み（supergroup ID 移行、`/config set|unset`）をブロックします。
- `type: "acp"` を持つトップレベルの `bindings[]` エントリーは、フォーラムトピック向けの永続 ACP バインディングを設定します（`match.peer.id` には正規の `chatId:topic:topicId` を使用）。フィールドの意味は [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings) で共通です。
- Telegram のストリームプレビューは `sendMessage` + `editMessageText` を使用します（ダイレクトチャットとグループチャットの両方で動作）。
- 再試行ポリシー: [Retry policy](/ja-JP/concepts/retry) を参照してください。

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
- 明示的な Discord `token` を指定した直接送信呼び出しは、そのトークンをその呼び出しに使用します。アカウントの再試行/ポリシー設定は、アクティブなランタイムスナップショット内で選択されたアカウントから引き続き取得されます。
- 任意の `channels.discord.defaultAccount` は、設定済みアカウント ID に一致する場合、デフォルトアカウント選択を上書きします。
- 配信ターゲットには `user:<id>`（DM）または `channel:<id>`（guild channel）を使用します。数字だけの ID は拒否されます。
- Guild slug は小文字で空白を `-` に置き換えたものです。channel キーには slug 化された名前（`#` なし）を使います。guild ID を推奨します。
- Bot 自身が投稿したメッセージは既定で無視されます。`allowBots: true` で有効化できます。`allowBots: "mentions"` を使うと、Bot へのメンションを含む bot メッセージのみ受け付けます（自分自身のメッセージは引き続き除外）。
- `channels.discord.guilds.<id>.ignoreOtherMentions`（およびチャンネル上書き）は、bot ではなく別のユーザーやロールに言及しているメッセージを破棄します（@everyone/@here は除外）。
- `maxLinesPerMessage`（デフォルト 17）は、2000 文字未満でも行数の多いメッセージを分割します。
- `channels.discord.threadBindings` は Discord のスレッド束縛ルーティングを制御します。
  - `enabled`: スレッド束縛セッション機能（`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`、および束縛配信/ルーティング）の Discord 上書き
  - `idleHours`: 非アクティブ時の自動 unfocus を時間単位で指定する Discord 上書き（`0` で無効）
  - `maxAgeHours`: ハード最大寿命を時間単位で指定する Discord 上書き（`0` で無効）
  - `spawnSubagentSessions`: `sessions_spawn({ thread: true })` の自動スレッド作成/束縛を有効にするオプトインスイッチ
- `type: "acp"` を持つトップレベルの `bindings[]` エントリーは、チャンネルとスレッド向けの永続 ACP バインディングを設定します（`match.peer.id` には channel/thread id を使用）。フィールドの意味は [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings) で共通です。
- `channels.discord.ui.components.accentColor` は Discord components v2 コンテナのアクセントカラーを設定します。
- `channels.discord.voice` は Discord 音声チャンネル会話と、任意の自動参加 + TTS 上書きを有効にします。
- `channels.discord.voice.daveEncryption` と `channels.discord.voice.decryptionFailureTolerance` は `@discordjs/voice` の DAVE オプションにそのまま渡されます（デフォルトは `true` と `24`）。
- OpenClaw はさらに、復号失敗が繰り返された後に音声セッションから退出して再参加することで、音声受信の復旧も試みます。
- `channels.discord.streaming` は正規のストリームモードキーです。旧来の `streamMode` と真偽値の `streaming` は自動移行されます。
- `channels.discord.autoPresence` はランタイムの可用性を bot presence にマッピングし（healthy => online、degraded => idle、exhausted => dnd）、任意のステータステキスト上書きも可能にします。
- `channels.discord.dangerouslyAllowNameMatching` は可変な name/tag マッチングを再度有効にします（非常用の互換モード）。
- `channels.discord.execApprovals`: Discord ネイティブの exec 承認配信と承認者認可。
  - `enabled`: `true`、`false`、または `"auto"`（デフォルト）。auto モードでは、承認者を `approvers` または `commands.ownerAllowFrom` から解決できる場合に exec 承認が有効化されます。
  - `approvers`: exec リクエストを承認できる Discord ユーザー ID。省略時は `commands.ownerAllowFrom` にフォールバックします。
  - `agentFilter`: 任意の agent ID 許可リスト。省略するとすべての agent の承認を転送します。
  - `sessionFilter`: 任意のセッションキーパターン（部分一致または正規表現）。
  - `target`: 承認プロンプトの送信先。`"dm"`（デフォルト）は承認者の DM に送信し、`"channel"` は発信元チャンネルに送信し、`"both"` は両方に送信します。target に `"channel"` が含まれる場合、ボタンは解決済み承認者のみが使用できます。
  - `cleanupAfterResolve`: `true` の場合、承認、拒否、またはタイムアウト後に承認 DM を削除します。

**リアクション通知モード:** `off`（なし）、`own`（bot のメッセージ、デフォルト）、`all`（すべてのメッセージ）、`allowlist`（`guilds.<id>.users` にあるユーザーのすべてのメッセージ）。

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
- サービスアカウントの SecretRef（`serviceAccountRef`）もサポートされます。
- 環境変数フォールバック: `GOOGLE_CHAT_SERVICE_ACCOUNT` または `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`。
- 配信ターゲットには `spaces/<spaceId>` または `users/<userId>` を使用します。
- `channels.googlechat.dangerouslyAllowNameMatching` は可変な email principal マッチングを再度有効にします（非常用の互換モード）。

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
- **HTTP mode** には `botToken` に加えて `signingSecret` が必要です（ルートまたはアカウントごと）。
- `botToken`、`appToken`、`signingSecret`、`userToken` は平文文字列または SecretRef オブジェクトを受け付けます。
- Slack アカウントスナップショットは、`botTokenSource`、`botTokenStatus`、`appTokenStatus`、HTTP mode では `signingSecretStatus` などの資格情報ごとの source/status フィールドを公開します。`configured_unavailable` は、アカウントが SecretRef で設定されているが、現在のコマンド/ランタイム経路では secret 値を解決できなかったことを意味します。
- `configWrites: false` は Slack 起点の設定書き込みをブロックします。
- 任意の `channels.slack.defaultAccount` は、設定済みアカウント ID に一致する場合、デフォルトアカウント選択を上書きします。
- `channels.slack.streaming` は正規のストリームモードキーです。旧来の `streamMode` と真偽値の `streaming` は自動移行されます。
- 配信ターゲットには `user:<id>`（DM）または `channel:<id>` を使用します。

**リアクション通知モード:** `off`、`own`（デフォルト）、`all`、`allowlist`（`reactionAllowlist` から）。

**スレッドセッション分離:** `thread.historyScope` はスレッド単位（デフォルト）またはチャンネル共有です。`thread.inheritParent` は親チャンネルトランスクリプトを新しいスレッドにコピーします。

- `typingReaction` は、返信実行中に受信 Slack メッセージへ一時的なリアクションを追加し、完了時に削除します。`"hourglass_flowing_sand"` のような Slack 絵文字ショートコードを使用します。
- `channels.slack.execApprovals`: Slack ネイティブの exec 承認配信と承認者認可。スキーマは Discord と同じです: `enabled`（`true`/`false`/`"auto"`）、`approvers`（Slack ユーザー ID）、`agentFilter`、`sessionFilter`、`target`（`"dm"`、`"channel"`、または `"both"`）。

| アクショングループ | デフォルト | 注記                     |
| ------------------ | ---------- | ------------------------ |
| reactions          | enabled    | リアクション + 一覧表示 |
| messages           | enabled    | 読み取り/送信/編集/削除 |
| pins               | enabled    | ピン留め/解除/一覧      |
| memberInfo         | enabled    | メンバー情報            |
| emojiList          | enabled    | カスタム絵文字一覧      |

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

Mattermost のネイティブコマンドが有効な場合:

- `commands.callbackPath` はパスである必要があります（例: `/api/channels/mattermost/command`）。完全な URL ではありません。
- `commands.callbackUrl` は OpenClaw Gateway エンドポイントを指し、Mattermost サーバーから到達可能である必要があります。
- ネイティブスラッシュコールバックは、スラッシュコマンド登録時に Mattermost が返すコマンドごとのトークンで認証されます。登録に失敗した場合、または有効化されたコマンドがない場合、OpenClaw は `Unauthorized: invalid command token.` でコールバックを拒否します。
- 非公開/tailnet/internal の callback host では、Mattermost で `ServiceSettings.AllowedUntrustedInternalConnections` に callback host/domain を含める必要がある場合があります。完全な URL ではなく host/domain 値を使用してください。
- `channels.mattermost.configWrites`: Mattermost 起点の設定書き込みを許可または拒否します。
- `channels.mattermost.requireMention`: チャンネルで返信する前に `@mention` を必須にします。
- `channels.mattermost.groups.<channelId>.requireMention`: チャンネルごとのメンションゲート上書き（デフォルトは `"*"`）。
- 任意の `channels.mattermost.defaultAccount` は、設定済みアカウント ID に一致する場合、デフォルトアカウント選択を上書きします。

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

- `channels.signal.account`: チャンネル起動を特定の Signal アカウント ID に固定します。
- `channels.signal.configWrites`: Signal 起点の設定書き込みを許可または拒否します。
- 任意の `channels.signal.defaultAccount` は、設定済みアカウント ID に一致する場合、デフォルトアカウント選択を上書きします。

### BlueBubbles

BlueBubbles は推奨される iMessage 経路です（プラグインベースで、`channels.bluebubbles` の下に設定します）。

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
- 任意の `channels.bluebubbles.defaultAccount` は、設定済みアカウント ID に一致する場合、デフォルトアカウント選択を上書きします。
- `type: "acp"` を持つトップレベルの `bindings[]` エントリーは、BlueBubbles 会話を永続 ACP セッションに束縛できます。`match.peer.id` には BlueBubbles handle または target string（`chat_id:*`、`chat_guid:*`、`chat_identifier:*`）を使用してください。共通フィールド意味: [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings)。
- 完全な BlueBubbles チャンネル設定は [BlueBubbles](/ja-JP/channels/bluebubbles) に記載されています。

### iMessage

OpenClaw は `imsg rpc`（stdio 上の JSON-RPC）を起動します。デーモンやポートは不要です。

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

- 任意の `channels.imessage.defaultAccount` は、設定済みアカウント ID に一致する場合、デフォルトアカウント選択を上書きします。

- Messages DB への Full Disk Access が必要です。
- `chat_id:<id>` ターゲットを推奨します。チャット一覧には `imsg chats --limit 20` を使用してください。
- `cliPath` は SSH ラッパーを指すことができ、SCP 添付取得用に `remoteHost`（`host` または `user@host`）を設定できます。
- `attachmentRoots` と `remoteAttachmentRoots` は受信添付パスを制限します（デフォルト: `/Users/*/Library/Messages/Attachments`）。
- SCP は strict host-key checking を使用するため、リレーホストキーがすでに `~/.ssh/known_hosts` に存在していることを確認してください。
- `channels.imessage.configWrites`: iMessage 起点の設定書き込みを許可または拒否します。
- `type: "acp"` を持つトップレベルの `bindings[]` エントリーは、iMessage 会話を永続 ACP セッションに束縛できます。`match.peer.id` には正規化された handle、または明示的チャットターゲット（`chat_id:*`、`chat_guid:*`、`chat_identifier:*`）を使用してください。共通フィールド意味: [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings)。

<Accordion title="iMessage SSH ラッパーの例">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix は拡張機能ベースで、`channels.matrix` の下に設定します。

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
- `channels.matrix.proxy` は Matrix HTTP 通信を明示的な HTTP(S) プロキシ経由にします。名前付きアカウントでは `channels.matrix.accounts.<id>.proxy` で上書きできます。
- `channels.matrix.network.dangerouslyAllowPrivateNetwork` は private/internal homeserver を許可します。`proxy` とこのネットワークオプトインは独立した制御です。
- `channels.matrix.defaultAccount` は複数アカウント構成で優先アカウントを選択します。
- `channels.matrix.autoJoin` のデフォルトは `off` です。そのため、招待されたルームや新しい DM 形式の招待は、`autoJoin: "allowlist"` と `autoJoinAllowlist` または `autoJoin: "always"` を設定するまで無視されます。
- `channels.matrix.execApprovals`: Matrix ネイティブの exec 承認配信と承認者認可。
  - `enabled`: `true`、`false`、または `"auto"`（デフォルト）。auto モードでは、承認者を `approvers` または `commands.ownerAllowFrom` から解決できる場合に exec 承認が有効化されます。
  - `approvers`: exec リクエストを承認できる Matrix user ID（例: `@owner:example.org`）。
  - `agentFilter`: 任意の agent ID 許可リスト。省略するとすべての agent の承認を転送します。
  - `sessionFilter`: 任意のセッションキーパターン（部分一致または正規表現）。
  - `target`: 承認プロンプトの送信先。`"dm"`（デフォルト）、`"channel"`（発信元ルーム）、または `"both"`。
  - アカウントごとの上書き: `channels.matrix.accounts.<id>.execApprovals`。
- `channels.matrix.dm.sessionScope` は Matrix DM をどのようにセッションへまとめるかを制御します。`per-user`（デフォルト）はルーティングされた peer ごとに共有し、`per-room` は各 DM ルームを分離します。
- Matrix の状態プローブとライブディレクトリルックアップは、ランタイム通信と同じプロキシポリシーを使用します。
- 完全な Matrix 設定、ターゲティングルール、セットアップ例は [Matrix](/ja-JP/channels/matrix) に記載されています。

### Microsoft Teams

Microsoft Teams は拡張機能ベースで、`channels.msteams` の下に設定します。

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
- 完全な Teams 設定（資格情報、webhook、DM/グループポリシー、チームごと/チャンネルごとの上書き）は [Microsoft Teams](/ja-JP/channels/msteams) に記載されています。

### IRC

IRC は拡張機能ベースで、`channels.irc` の下に設定します。

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
- 任意の `channels.irc.defaultAccount` は、設定済みアカウント ID に一致する場合、デフォルトアカウント選択を上書きします。
- 完全な IRC チャンネル設定（host/port/TLS/channels/allowlists/mention gating）は [IRC](/ja-JP/channels/irc) に記載されています。

### 複数アカウント（すべてのチャンネル）

チャンネルごとに複数アカウントを実行できます（各アカウントは独自の `accountId` を持ちます）。

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

- `accountId` を省略した場合、`default` が使用されます（CLI + ルーティング）。
- 環境変数トークンは **default** アカウントにのみ適用されます。
- ベースチャンネル設定は、アカウントごとに上書きされない限り、すべてのアカウントに適用されます。
- 各アカウントを別の agent にルーティングするには `bindings[].match.accountId` を使用します。
- `openclaw channels add`（またはチャンネルのオンボーディング）で、まだ単一アカウントのトップレベルチャンネル設定形状のまま non-default アカウントを追加すると、OpenClaw は元のアカウントが引き続き動作するよう、まずアカウント範囲のトップレベル単一アカウント値をチャンネルアカウントマップへ昇格させます。ほとんどのチャンネルでは `channels.<channel>.accounts.default` に移されますが、Matrix は既存の一致する named/default ターゲットを保持できます。
- 既存のチャンネル専用バインディング（`accountId` なし）は、引き続き default アカウントに一致します。アカウント範囲バインディングは任意のままです。
- `openclaw doctor --fix` も混在形状を修復し、そのチャンネル向けに選ばれた昇格アカウントへアカウント範囲トップレベル単一アカウント値を移動します。ほとんどのチャンネルでは `accounts.default` を使い、Matrix は既存の一致する named/default ターゲットを保持できます。

### その他の拡張チャンネル

多くの拡張チャンネルは `channels.<id>` として設定され、それぞれ専用のチャンネルページに記載されています（例: Feishu、Matrix、LINE、Nostr、Zalo、Nextcloud Talk、Synology Chat、Twitch）。
完全なチャンネル一覧は [Channels](/ja-JP/channels) を参照してください。

### グループチャットのメンションゲート

グループメッセージは、デフォルトで **メンション必須** です（メタデータメンションまたは安全な正規表現パターン）。WhatsApp、Telegram、Discord、Google Chat、iMessage のグループチャットに適用されます。

**メンション種別:**

- **メタデータメンション**: ネイティブのプラットフォーム @-mention。WhatsApp の self-chat mode では無視されます。
- **テキストパターン**: `agents.list[].groupChat.mentionPatterns` の安全な正規表現パターン。無効なパターンや安全でない入れ子反復は無視されます。
- メンションゲートは、検出が可能な場合（ネイティブメンションまたは少なくとも 1 つのパターンがある場合）にのみ強制されます。

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

`messages.groupChat.historyLimit` はグローバルデフォルトを設定します。チャンネルは `channels.<channel>.historyLimit`（またはアカウントごと）で上書きできます。無効化するには `0` を設定します。

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

対応対象: `telegram`、`whatsapp`、`discord`、`slack`、`signal`、`imessage`、`msteams`。

#### Self-chat mode

自分の番号を `allowFrom` に含めると self-chat mode が有効になります（ネイティブ @-mentions を無視し、テキストパターンのみに応答）。

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

### Commands（チャットコマンド処理）

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

- テキストコマンドは、先頭が `/` の**単独メッセージ**である必要があります。
- `native: "auto"` は Discord/Telegram のネイティブコマンドを有効化し、Slack は無効のままにします。
- チャンネルごとの上書き: `channels.discord.commands.native`（bool または `"auto"`）。`false` は以前登録されたコマンドをクリアします。
- `channels.telegram.customCommands` は Telegram bot メニューエントリーを追加します。
- `bash: true` はホストシェル向けに `! <cmd>` を有効化します。`tools.elevated.enabled` が必要で、送信者が `tools.elevated.allowFrom.<channel>` に含まれている必要があります。
- `config: true` は `/config`（`openclaw.json` の読み書き）を有効にします。Gateway の `chat.send` クライアントでは、永続的な `/config set|unset` 書き込みに `operator.admin` も必要です。読み取り専用の `/config show` は通常の書き込みスコープを持つ operator クライアントでも利用できます。
- `channels.<provider>.configWrites` はチャンネルごとの設定変更を制御します（デフォルト: true）。
- 複数アカウントチャンネルでは、`channels.<provider>.accounts.<id>.configWrites` も、そのアカウントを対象にした書き込み（例: `/allowlist --config --account <id>` や `/config set channels.<provider>.accounts.<id>...`）を制御します。
- `allowFrom` はプロバイダーごとです。設定されている場合、それが**唯一の**認可ソースになります（チャンネル allowlists/pairing と `useAccessGroups` は無視されます）。
- `useAccessGroups: false` は、`allowFrom` が設定されていない場合に、コマンドが access-group ポリシーをバイパスできるようにします。

</Accordion>

---

## Agent のデフォルト値

### `agents.defaults.workspace`

デフォルト: `~/.openclaw/workspace`。

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

システムプロンプトの Runtime 行に表示される任意のリポジトリルート。未設定の場合、OpenClaw は workspace から上方向にたどって自動検出します。

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

`agents.list[].skills` を設定していない agent 向けの任意のデフォルト Skills 許可リスト。

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

- デフォルトで Skills を無制限にするには `agents.defaults.skills` を省略します。
- デフォルトを継承するには `agents.list[].skills` を省略します。
- Skills なしにするには `agents.list[].skills: []` を設定します。
- 空でない `agents.list[].skills` のリストは、その agent の最終セットです。デフォルトとはマージされません。

### `agents.defaults.skipBootstrap`

workspace bootstrap ファイル（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、`BOOTSTRAP.md`）の自動作成を無効にします。

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

workspace bootstrap ファイルをシステムプロンプトに注入するタイミングを制御します。デフォルト: `"always"`。

- `"continuation-skip"`: 完了した assistant 応答の後の安全な継続ターンでは、workspace bootstrap の再注入をスキップし、プロンプトサイズを削減します。heartbeat 実行と compact 後の再試行では引き続きコンテキストを再構築します。

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

切り詰め前の workspace bootstrap ファイル 1 つあたりの最大文字数。デフォルト: `20000`。

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

すべての workspace bootstrap ファイルから注入される合計最大文字数。デフォルト: `150000`。

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

bootstrap コンテキストが切り詰められたときに、agent に見える警告文をどう扱うかを制御します。
デフォルト: `"once"`。

- `"off"`: 警告文をシステムプロンプトに一切注入しません。
- `"once"`: 一意の切り詰めシグネチャごとに 1 回だけ警告を注入します（推奨）。
- `"always"`: 切り詰めが存在するたび毎回警告を注入します。

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

プロバイダー呼び出し前に transcript/tool の image ブロックで許可される、画像の最長辺の最大ピクセルサイズ。
デフォルト: `1200`。

低い値は通常、スクリーンショットが多い実行で vision token 使用量とリクエスト payload サイズを減らします。
高い値は、より多くの視覚的詳細を保持します。

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

システムプロンプトコンテキスト用のタイムゾーンです（メッセージタイムスタンプではありません）。ホストのタイムゾーンにフォールバックします。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

システムプロンプトでの時刻形式。デフォルト: `auto`（OS 設定）。

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

- `model`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）のいずれかを受け付けます。
  - 文字列形式は primary model のみを設定します。
  - オブジェクト形式は primary に加えて順序付き failover model を設定します。
- `imageModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）のいずれかを受け付けます。
  - `image` tool 経路の vision-model 設定として使用されます。
  - 選択/デフォルト model が image 入力を受け取れない場合のフォールバックルーティングにも使用されます。
- `imageGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）のいずれかを受け付けます。
  - 共有の image-generation capability と、今後の image 生成を行う tool/plugin surface で使用されます。
  - 典型的な値: ネイティブ Gemini 画像生成には `google/gemini-3.1-flash-image-preview`、fal には `fal/fal-ai/flux/dev`、OpenAI Images には `openai/gpt-image-1`。
  - provider/model を直接選択する場合は、対応する provider auth/API key も設定してください（例: `google/*` には `GEMINI_API_KEY` または `GOOGLE_API_KEY`、`openai/*` には `OPENAI_API_KEY`、`fal/*` には `FAL_KEY`）。
  - 省略時でも `image_generate` は auth に支えられた provider デフォルトを推論できます。まず現在の default provider を試し、その後 provider-id 順で残りの登録済み image-generation provider を試します。
- `musicGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）のいずれかを受け付けます。
  - 共有の music-generation capability と組み込み `music_generate` tool で使用されます。
  - 典型的な値: `google/lyria-3-clip-preview`、`google/lyria-3-pro-preview`、または `minimax/music-2.5+`。
  - 省略時でも `music_generate` は auth に支えられた provider デフォルトを推論できます。まず現在の default provider を試し、その後 provider-id 順で残りの登録済み music-generation provider を試します。
  - provider/model を直接選択する場合は、対応する provider auth/API key も設定してください。
- `videoGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）のいずれかを受け付けます。
  - 共有の video-generation capability と組み込み `video_generate` tool で使用されます。
  - 典型的な値: `qwen/wan2.6-t2v`、`qwen/wan2.6-i2v`、`qwen/wan2.6-r2v`、`qwen/wan2.6-r2v-flash`、または `qwen/wan2.7-r2v`。
  - 省略時でも `video_generate` は auth に支えられた provider デフォルトを推論できます。まず現在の default provider を試し、その後 provider-id 順で残りの登録済み video-generation provider を試します。
  - provider/model を直接選択する場合は、対応する provider auth/API key も設定してください。
  - 同梱の Qwen video-generation provider は現在、最大 1 本の出力動画、1 枚の入力画像、4 本の入力動画、10 秒の長さ、および provider レベルの `size`、`aspectRatio`、`resolution`、`audio`、`watermark` オプションをサポートします。
- `pdfModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）のいずれかを受け付けます。
  - `pdf` tool の model routing に使用されます。
  - 省略時、PDF tool は `imageModel` にフォールバックし、さらに解決済み session/default model にフォールバックします。
- `pdfMaxBytesMb`: `pdf` tool で呼び出し時に `maxBytesMb` が渡されない場合のデフォルト PDF サイズ上限。
- `pdfMaxPages`: `pdf` tool の抽出フォールバックモードで考慮するデフォルト最大ページ数。
- `verboseDefault`: agent のデフォルト verbose レベル。値: `"off"`、`"on"`、`"full"`。デフォルト: `"off"`。
- `elevatedDefault`: agent のデフォルト elevated-output レベル。値: `"off"`、`"on"`、`"ask"`、`"full"`。デフォルト: `"on"`。
- `model.primary`: 形式は `provider/model`（例: `openai/gpt-5.4`）。provider を省略した場合、OpenClaw はまず alias を試し、次にその正確な model id に対する一意の configured-provider 一致を試し、それでもなければ configured default provider にフォールバックします（これは非推奨の互換動作なので、明示的な `provider/model` を推奨します）。その provider が設定済み default model をもはや公開していない場合、OpenClaw は古い削除済み provider default をそのまま使うのではなく、最初の configured provider/model にフォールバックします。
- `models`: 設定済み model catalog および `/model` 用の allowlist。各エントリーには `alias`（ショートカット）と `params`（provider 固有、例: `temperature`、`maxTokens`、`cacheRetention`、`context1m`）を含められます。
- `params`: すべての model に適用されるグローバルデフォルト provider parameter。`agents.defaults.params` に設定します（例: `{ cacheRetention: "long" }`）。
- `params` のマージ優先順位（config）: `agents.defaults.params`（グローバルベース）が `agents.defaults.models["provider/model"].params`（model ごと）で上書きされ、さらに `agents.list[].params`（一致する agent id）がキーごとに上書きします。詳細は [Prompt Caching](/ja-JP/reference/prompt-caching) を参照してください。
- これらのフィールドを変更する config writer（例: `/models set`、`/models set-image`、fallback add/remove コマンド）は、可能な限り既存の fallback リストを保持しつつ、正規のオブジェクト形式で保存します。
- `maxConcurrent`: セッション間での並列 agent 実行の最大数（各セッション自体は直列処理）。デフォルト: 4。

**組み込み alias ショートハンド**（model が `agents.defaults.models` にある場合のみ適用）:

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

Z.AI GLM-4.x model は、`--thinking off` を設定するか `agents.defaults.models["zai/<model>"].params.thinking` を自分で定義しない限り、自動的に thinking mode を有効にします。
Z.AI model は tool call streaming のためにデフォルトで `tool_stream` を有効にします。無効にするには `agents.defaults.models["zai/<model>"].params.tool_stream` を `false` に設定してください。
Anthropic Claude 4.6 model は、明示的な thinking level が設定されていない場合、デフォルトで `adaptive` thinking を使用します。

### `agents.defaults.cliBackends`

テキストのみのフォールバック実行向けの任意の CLI backend（tool call なし）。API provider が失敗したときのバックアップとして有用です。

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

- CLI backend は text-first であり、tools は常に無効です。
- `sessionArg` が設定されている場合は sessions をサポートします。
- `imageArg` が file path を受け取る場合は image pass-through をサポートします。

### `agents.defaults.heartbeat`

定期 heartbeat 実行。

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

- `every`: 期間文字列（ms/s/m/h）。デフォルト: `30m`（API-key auth）または `1h`（OAuth auth）。無効にするには `0m` を設定します。
- `suppressToolErrorWarnings`: true の場合、heartbeat 実行中に tool error warning payload を抑制します。
- `directPolicy`: 直接/DM 配信ポリシー。`allow`（デフォルト）は direct-target 配信を許可します。`block` は direct-target 配信を抑止し、`reason=dm-blocked` を出力します。
- `lightContext`: true の場合、heartbeat 実行は軽量 bootstrap context を使用し、workspace bootstrap ファイルのうち `HEARTBEAT.md` のみを保持します。
- `isolatedSession`: true の場合、各 heartbeat 実行は prior conversation history を持たない fresh session で行われます。cron の `sessionTarget: "isolated"` と同じ分離パターンです。heartbeat ごとの token コストを約 100K から約 2-5K token に削減します。
- agent ごと: `agents.list[].heartbeat` を設定します。いずれかの agent が `heartbeat` を定義している場合、heartbeat を実行するのは**それらの agent のみ**です。
- heartbeat は完全な agent turn を実行します。間隔が短いほど token を多く消費します。

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
- `provider`: 登録済み compaction provider plugin の id。設定すると、組み込み LLM 要約の代わりにその provider の `summarize()` が呼び出されます。失敗時は組み込みにフォールバックします。provider を設定すると `mode: "safeguard"` が強制されます。[Compaction](/ja-JP/concepts/compaction) を参照してください。
- `timeoutSeconds`: 単一の compaction 操作に OpenClaw が許容する最大秒数。デフォルト: `900`。
- `identifierPolicy`: `strict`（デフォルト）、`off`、または `custom`。`strict` は compaction 要約時に組み込みの opaque identifier 保持ガイダンスを前置します。
- `identifierInstructions`: `identifierPolicy=custom` のときに使用する、任意のカスタム identifier 保持文。
- `postCompactionSections`: compaction 後に再注入する任意の AGENTS.md H2/H3 セクション名。デフォルトは `["Session Startup", "Red Lines"]` です。無効にするには `[]` を設定します。未設定、またはそのデフォルトのペアに明示設定されている場合、古い `Every Session`/`Safety` 見出しも legacy fallback として受け入れられます。
- `model`: compaction 要約専用の任意の `provider/model-id` 上書き。メインセッションでは 1 つの model を使い続けつつ、compaction summary は別 model で実行したい場合に使用します。未設定時、compaction は session の primary model を使用します。
- `notifyUser`: `true` の場合、compaction 開始時にユーザーへ簡単な通知（例: 「Compacting context...」）を送ります。既定では compaction を静かに保つため無効です。
- `memoryFlush`: 自動 compaction 前に durable memory を保存するためのサイレント agentic turn。workspace が read-only の場合はスキップされます。

### `agents.defaults.contextPruning`

LLM へ送信する前に、メモリ内コンテキストから**古い tool result** を剪定します。ディスク上の session history は変更しません。

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

- `mode: "cache-ttl"` は剪定パスを有効にします。
- `ttl` は、最後の cache touch 後に再び剪定を実行できる頻度を制御します。
- 剪定はまず大きすぎる tool result を soft-trim し、その後必要に応じて古い tool result を hard-clear します。

**Soft-trim** は先頭と末尾を保持し、中間に `...` を挿入します。

**Hard-clear** は tool result 全体を placeholder に置き換えます。

注記:

- image block は切り詰めもクリアもされません。
- 比率は文字数ベース（概算）であり、正確な token 数ではありません。
- `keepLastAssistants` 未満の assistant message しか存在しない場合、剪定はスキップされます。

</Accordion>

動作の詳細は [Session Pruning](/ja-JP/concepts/session-pruning) を参照してください。

### Block streaming

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

- Telegram 以外のチャンネルでは、block reply を有効にするには明示的な `*.blockStreaming: true` が必要です。
- チャンネルごとの上書き: `channels.<channel>.blockStreamingCoalesce`（およびアカウントごとの variants）。Signal/Slack/Discord/Google Chat のデフォルトは `minChars: 1500` です。
- `humanDelay`: block reply 間のランダムな待機時間。`natural` = 800–2500ms。agent ごとの上書き: `agents.list[].humanDelay`。

動作と chunking の詳細は [Streaming](/ja-JP/concepts/streaming) を参照してください。

### Typing indicators

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

- デフォルト: direct chat/mention では `instant`、メンションなし group chat では `message`。
- セッションごとの上書き: `session.typingMode`、`session.typingIntervalSeconds`。

[Typing Indicators](/ja-JP/concepts/typing-indicators) を参照してください。

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

埋め込み agent 向けの任意 sandboxing。完全ガイドは [Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。

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

`backend: "openshell"` を選択した場合、runtime 固有設定は
`plugins.entries.openshell.config` に移動します。

**SSH backend config:**

- `target`: `user@host[:port]` 形式の SSH target
- `command`: SSH client command（デフォルト: `ssh`）
- `workspaceRoot`: スコープごとの workspace に使う絶対 remote root
- `identityFile` / `certificateFile` / `knownHostsFile`: OpenSSH に渡される既存のローカルファイル
- `identityData` / `certificateData` / `knownHostsData`: インライン内容または SecretRef。OpenClaw はランタイム時にこれらを temp file に materialize します
- `strictHostKeyChecking` / `updateHostKeys`: OpenSSH の host-key policy ノブ

**SSH auth の優先順位:**

- `identityData` は `identityFile` より優先
- `certificateData` は `certificateFile` より優先
- `knownHostsData` は `knownHostsFile` より優先
- SecretRef ベースの `*Data` 値は、sandbox session 開始前に active secrets runtime snapshot から解決されます

**SSH backend の動作:**

- create または recreate の後、remote workspace を 1 度 seed します
- その後は remote SSH workspace を canonical として維持します
- `exec`、file tools、media path を SSH 経由でルーティングします
- remote の変更は自動的にホストへ同期されません
- sandbox browser container はサポートしません

**Workspace access:**

- `none`: `~/.openclaw/sandboxes` 配下のスコープごとの sandbox workspace
- `ro`: `/workspace` に sandbox workspace、`/agent` に agent workspace を read-only マウント
- `rw`: `/workspace` に agent workspace を read/write マウント

**Scope:**

- `session`: セッションごとの container + workspace
- `agent`: agent ごとに 1 つの container + workspace（デフォルト）
- `shared`: 共有 container と workspace（セッション間分離なし）

**OpenShell plugin config:**

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

- `mirror`: 実行前に local から remote へ seed し、実行後に逆同期します。local workspace が canonical のままです
- `remote`: sandbox 作成時に 1 度だけ remote へ seed し、その後は remote workspace を canonical として維持します

`remote` mode では、seed ステップ後に OpenClaw の外で行われた host-local 編集は自動的には sandbox に同期されません。
transport は OpenShell sandbox への SSH ですが、sandbox lifecycle と任意の mirror sync は plugin が管理します。

**`setupCommand`** は container 作成後に 1 回（`sh -lc` 経由で）実行されます。network egress、writable root、root user が必要です。

**Container のデフォルトは `network: "none"`** です。agent が outbound access を必要とする場合は `"bridge"`（または custom bridge network）に設定してください。
`"host"` はブロックされます。`"container:<id>"` は、`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` を明示設定しない限り（非常用）、既定でブロックされます。

**Inbound attachment** は、active workspace の `media/inbound/*` に stage されます。

**`docker.binds`** は追加のホストディレクトリをマウントします。グローバル bind と agent ごとの bind はマージされます。

**Sandboxed browser**（`sandbox.browser.enabled`）: container 内の Chromium + CDP。noVNC URL は system prompt に注入されます。`openclaw.json` の `browser.enabled` は不要です。
noVNC observer access は既定で VNC auth を使用し、OpenClaw は共有 URL にパスワードを露出する代わりに短命トークン URL を発行します。

- `allowHostControl: false`（デフォルト）は、sandboxed session がホスト browser をターゲットにすることをブロックします。
- `network` のデフォルトは `openclaw-sandbox-browser`（専用 bridge network）です。グローバル bridge 接続を明示的に望む場合にのみ `bridge` に設定してください。
- `cdpSourceRange` は、container edge で CDP ingress を CIDR 範囲（例: `172.21.0.1/32`）に制限できます。
- `sandbox.browser.binds` は追加の host directory を sandbox browser container のみにマウントします。設定された場合（`[]` を含む）、browser container については `docker.binds` を置き換えます。
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
  - `--disable-3d-apis`、`--disable-software-rasterizer`、`--disable-gpu` はデフォルトで有効で、WebGL/3D 使用で必要な場合は `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` で無効にできます。
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` で、ワークフローが依存している場合に extensions を再有効化できます。
  - `--renderer-process-limit=2` は `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` で変更できます。Chromium のデフォルト process limit を使うには `0` を設定します。
  - さらに、`noSandbox` が有効な場合は `--no-sandbox` と `--disable-setuid-sandbox`。
  - これらのデフォルトは container image の baseline です。container のデフォルトを変更するには custom entrypoint を持つ custom browser image を使用してください。

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
- `default`: 複数設定されている場合は最初のものが優先されます（警告を記録）。どれも設定されていない場合、最初の list エントリーが default です。
- `model`: 文字列形式は `primary` のみを上書きし、オブジェクト形式 `{ primary, fallbacks }` は両方を上書きします（`[]` でグローバル fallback を無効化）。`primary` のみを上書きする cron job では、`fallbacks: []` を設定しない限り default fallback を継承します。
- `params`: 選択された `agents.defaults.models` 内の model entry に対してマージされる agent ごとの stream params。`cacheRetention`、`temperature`、`maxTokens` などの agent 固有上書きを、model catalog 全体を複製せずに行うために使います。
- `skills`: 任意の agent ごとの Skills 許可リスト。省略時、その agent は `agents.defaults.skills` が設定されていればそれを継承します。明示的リストはデフォルトをマージせず置き換え、`[]` は Skills なしを意味します。
- `thinkingDefault`: 任意の agent ごとのデフォルト thinking level（`off | minimal | low | medium | high | xhigh | adaptive`）。メッセージごとまたはセッション上書きが設定されていない場合、この agent に対して `agents.defaults.thinkingDefault` を上書きします。
- `reasoningDefault`: 任意の agent ごとのデフォルト reasoning visibility（`on | off | stream`）。メッセージごとまたはセッション上書きが設定されていない場合に適用されます。
- `fastModeDefault`: 任意の agent ごとのデフォルト fast mode（`true | false`）。メッセージごとまたはセッション上書きが設定されていない場合に適用されます。
- `runtime`: 任意の agent ごとの runtime descriptor。agent が ACP harness session をデフォルトにする必要がある場合は `type: "acp"` と `runtime.acp` デフォルト（`agent`、`backend`、`mode`、`cwd`）を使います。
- `identity.avatar`: workspace 相対パス、`http(s)` URL、または `data:` URI。
- `identity` はデフォルトを導出します: `emoji` から `ackReaction`、`name`/`emoji` から `mentionPatterns`。
- `subagents.allowAgents`: `sessions_spawn` 用の agent id 許可リスト（`["*"]` = 任意。デフォルト: 同じ agent のみ）。
- Sandbox 継承ガード: 要求元 session が sandboxed の場合、`sessions_spawn` は unsandboxed で実行される target を拒否します。
- `subagents.requireAgentId`: true の場合、`agentId` を省略した `sessions_spawn` 呼び出しをブロックします（明示的な profile 選択を強制。デフォルト: false）。

---

## マルチ agent ルーティング

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

### Binding の match フィールド

- `type`（任意）: 通常ルーティングは `route`（type 省略時も route）、永続 ACP 会話バインディングは `acp`
- `match.channel`（必須）
- `match.accountId`（任意。`*` = 任意のアカウント、省略 = default アカウント）
- `match.peer`（任意。`{ kind: direct|group|channel, id }`）
- `match.guildId` / `match.teamId`（任意。チャンネル固有）
- `acp`（任意。`type: "acp"` の場合のみ）: `{ mode, label, cwd, backend }`

**決定的な match 順序:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId`（正確一致、peer/guild/team なし）
5. `match.accountId: "*"`（チャンネル全体）
6. Default agent

各 tier 内では、最初に一致した `bindings` エントリーが優先されます。

`type: "acp"` のエントリーについては、OpenClaw は正確な会話 ID（`match.channel` + account + `match.peer.id`）で解決し、上記の route binding tier 順序は使用しません。

### Agent ごとのアクセスプロファイル

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

<Accordion title="読み取り専用 tools + workspace">

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

## Session

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

<Accordion title="Session フィールド詳細">

- **`scope`**: group-chat context 向けの基本 session grouping 戦略。
  - `per-sender`（デフォルト）: チャンネル context 内で送信者ごとに分離された session。
  - `global`: チャンネル context 内の全参加者が 1 つの session を共有します（共有 context が意図される場合にのみ使用）。
- **`dmScope`**: DM をどうまとめるか。
  - `main`: すべての DM が main session を共有。
  - `per-peer`: チャンネルをまたいで送信者 ID ごとに分離。
  - `per-channel-peer`: チャンネル + 送信者ごとに分離（複数ユーザー inbox 向け推奨）。
  - `per-account-channel-peer`: アカウント + チャンネル + 送信者ごとに分離（複数アカウント向け推奨）。
- **`identityLinks`**: cross-channel session 共有のため、正規 ID を provider 接頭辞付き peer にマップします。
- **`reset`**: 基本 reset ポリシー。`daily` はローカル時間の `atHour` に reset し、`idle` は `idleMinutes` 後に reset します。両方設定されている場合、先に期限切れになる方が優先されます。
- **`resetByType`**: タイプごとの上書き（`direct`、`group`、`thread`）。旧来の `dm` は `direct` のエイリアスとして受け付けられます。
- **`parentForkMaxTokens`**: forked thread session 作成時に許可される parent-session `totalTokens` の最大値（デフォルト `100000`）。
  - parent の `totalTokens` がこの値を超えている場合、OpenClaw は parent transcript history を継承する代わりに fresh thread session を開始します。
  - このガードを無効にして常に parent fork を許可するには `0` を設定します。
- **`mainKey`**: 旧来フィールド。ランタイムは現在、main direct-chat bucket に常に `"main"` を使用します。
- **`agentToAgent.maxPingPongTurns`**: agent-to-agent 交換中の agent 間 reply-back turn の最大数（整数、範囲: `0`–`5`）。`0` は ping-pong chaining を無効にします。
- **`sendPolicy`**: `channel`、`chatType`（`direct|group|channel`、旧来の `dm` エイリアスあり）、`keyPrefix`、または `rawKeyPrefix` でマッチします。最初の deny が優先されます。
- **`maintenance`**: session-store の cleanup + retention 制御。
  - `mode`: `warn` は警告のみを出力し、`enforce` は cleanup を適用します。
  - `pruneAfter`: 古い entry の age cutoff（デフォルト `30d`）。
  - `maxEntries`: `sessions.json` 内の最大 entry 数（デフォルト `500`）。
  - `rotateBytes`: `sessions.json` がこのサイズを超えると rotate します（デフォルト `10mb`）。
  - `resetArchiveRetention`: `*.reset.<timestamp>` transcript archive の retention。デフォルトは `pruneAfter`。無効にするには `false` を設定します。
  - `maxDiskBytes`: 任意の sessions-directory disk budget。`warn` mode では警告を記録し、`enforce` mode では最も古い artifact/session から順に削除します。
  - `highWaterBytes`: budget cleanup 後の任意の目標値。デフォルトは `maxDiskBytes` の `80%`。
- **`threadBindings`**: thread-bound session 機能のグローバルデフォルト。
  - `enabled`: マスター default switch（provider が上書き可能。Discord は `channels.discord.threadBindings.enabled` を使用）
  - `idleHours`: 非アクティブ時の auto-unfocus のデフォルト時間（`0` で無効。provider が上書き可能）
  - `maxAgeHours`: hard max age のデフォルト時間（`0` で無効。provider が上書き可能）

</Accordion>

---

## Messages

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

解決順序（最も具体的なものが優先）: account → channel → global。`""` は無効化し、cascade を停止します。`"auto"` は `[{identity.name}]` を導出します。

**テンプレート変数:**

| 変数              | 説明                     | 例                          |
| ----------------- | ------------------------ | --------------------------- |
| `{model}`         | 短い model 名            | `claude-opus-4-6`           |
| `{modelFull}`     | 完全な model identifier  | `anthropic/claude-opus-4-6` |
| `{provider}`      | Provider 名              | `anthropic`                 |
| `{thinkingLevel}` | 現在の thinking level    | `high`, `low`, `off`        |
| `{identity.name}` | Agent identity 名        | （`"auto"` と同じ）         |

変数は大文字小文字を区別しません。`{think}` は `{thinkingLevel}` のエイリアスです。

### Ack reaction

- デフォルトは active agent の `identity.emoji`、それ以外は `"👀"`。無効化するには `""` を設定します。
- チャンネルごとの上書き: `channels.<channel>.ackReaction`、`channels.<channel>.accounts.<id>.ackReaction`。
- 解決順序: account → channel → `messages.ackReaction` → identity fallback。
- スコープ: `group-mentions`（デフォルト）、`group-all`、`direct`、`all`。
- `removeAckAfterReply`: Slack、Discord、Telegram で reply 後に ack を削除します。
- `messages.statusReactions.enabled`: Slack、Discord、Telegram で lifecycle status reaction を有効にします。
  Slack と Discord では、未設定だと ack reaction が有効な場合に status reaction も有効のままになります。
  Telegram では、lifecycle status reaction を有効にするには明示的に `true` に設定してください。

### Inbound debounce

同じ送信者からの短時間の text-only message を 1 つの agent turn にまとめます。media/attachment は即時 flush されます。control command は debounce をバイパスします。

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

- `auto` は auto-TTS を制御します。`/tts off|always|inbound|tagged` はセッションごとに上書きします。
- `summaryModel` は auto-summary 用に `agents.defaults.model.primary` を上書きします。
- `modelOverrides` はデフォルトで有効です。`modelOverrides.allowProvider` のデフォルトは `false`（オプトイン）です。
- API key は `ELEVENLABS_API_KEY`/`XI_API_KEY` と `OPENAI_API_KEY` にフォールバックします。
- `openai.baseUrl` は OpenAI TTS endpoint を上書きします。解決順序は config、次に `OPENAI_TTS_BASE_URL`、最後に `https://api.openai.com/v1` です。
- `openai.baseUrl` が非 OpenAI endpoint を指す場合、OpenClaw はそれを OpenAI 互換 TTS server と見なし、model/voice validation を緩和します。

---

## Talk

Talk mode（macOS/iOS/Android）のデフォルト値。

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

- `talk.provider` は、複数の Talk provider を設定している場合、`talk.providers` 内のキーに一致している必要があります。
- 旧来のフラットな Talk キー（`talk.voiceId`、`talk.voiceAliases`、`talk.modelId`、`talk.outputFormat`、`talk.apiKey`）は互換専用であり、自動的に `talk.providers.<provider>` へ移行されます。
- Voice ID は `ELEVENLABS_VOICE_ID` または `SAG_VOICE_ID` にフォールバックします。
- `providers.*.apiKey` は平文文字列または SecretRef オブジェクトを受け付けます。
- `ELEVENLABS_API_KEY` のフォールバックは、Talk API key が未設定の場合にのみ適用されます。
- `providers.*.voiceAliases` により、Talk directive でフレンドリー名を使用できます。
- `silenceTimeoutMs` は、Talk mode がユーザーの無音後に transcript を送信するまで待機する時間を制御します。未設定の場合、プラットフォームデフォルトの pause window を維持します（macOS と Android では `700 ms`、iOS では `900 ms`）。

---

## Tools

### Tool profile

`tools.profile` は `tools.allow`/`tools.deny` の前にベース allowlist を設定します。

ローカルオンボーディングでは、未設定の新しい local config に既定で `tools.profile: "coding"` を設定します（既存の明示 profile は保持されます）。

| Profile     | 含まれるもの                                                                                                              |
| ----------- | ------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | `session_status` のみ                                                                                                     |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                               |
| `full`      | 制限なし（未設定と同じ）                                                                                                  |

### Tool group

| グループ           | Tools                                                                                                                  |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec`, `process`, `code_execution`（`bash` は `exec` のエイリアスとして受け付けられます）                              |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                                                 |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory`     | `memory_search`, `memory_get`                                                                                          |
| `group:web`        | `web_search`, `x_search`, `web_fetch`                                                                                  |
| `group:ui`         | `browser`, `canvas`                                                                                                    |
| `group:automation` | `cron`, `gateway`                                                                                                      |
| `group:messaging`  | `message`                                                                                                              |
| `group:nodes`      | `nodes`                                                                                                                |
| `group:agents`     | `agents_list`                                                                                                          |
| `group:media`      | `image`, `image_generate`, `video_generate`, `tts`                                                                     |
| `group:openclaw`   | すべての組み込み tools（provider plugin は除く）                                                                        |

### `tools.allow` / `tools.deny`

グローバルな tool の allow/deny ポリシー（deny 優先）。大文字小文字を区別せず、`*` ワイルドカードをサポートします。Docker sandbox が無効でも適用されます。

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

特定の provider または model 向けに、tools をさらに制限します。順序: base profile → provider profile → allow/deny。

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

- agent ごとの上書き（`agents.list[].tools.elevated`）は、さらに制限することしかできません。
- `/elevated on|off|ask|full` はセッションごとに状態を保存します。inline directive は 1 メッセージのみに適用されます。
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

Tool-loop 安全チェックは**デフォルトで無効**です。有効にするには `enabled: true` を設定します。
設定はグローバルに `tools.loopDetection` で定義でき、agent ごとに `agents.list[].tools.loopDetection` で上書きできます。

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

- `historySize`: loop 分析のために保持する tool-call history の最大数。
- `warningThreshold`: 繰り返しの no-progress パターンで警告を出す閾値。
- `criticalThreshold`: 深刻な loop をブロックするための、より高い繰り返し閾値。
- `globalCircuitBreakerThreshold`: あらゆる no-progress 実行に対するハード停止閾値。
- `detectors.genericRepeat`: 同一 tool/同一 args の繰り返し呼び出しで警告します。
- `detectors.knownPollNoProgress`: 既知の poll tool（`process.poll`、`command_status` など）で警告/ブロックします。
- `detectors.pingPong`: 交互に発生する no-progress ペアパターンで警告/ブロックします。
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

<Accordion title="Media model entry フィールド">

**Provider entry**（`type: "provider"` または省略時）:

- `provider`: API provider id（`openai`、`anthropic`、`google`/`gemini`、`groq` など）
- `model`: model id 上書き
- `profile` / `preferredProfile`: `auth-profiles.json` profile 選択

**CLI entry**（`type: "cli"`）:

- `command`: 実行する executable
- `args`: テンプレート化された args（`{{MediaPath}}`、`{{Prompt}}`、`{{MaxChars}}` などをサポート）

**共通フィールド:**

- `capabilities`: 任意のリスト（`image`、`audio`、`video`）。デフォルト: `openai`/`anthropic`/`minimax` → image、`google` → image+audio+video、`groq` → audio。
- `prompt`、`maxChars`、`maxBytes`、`timeoutSeconds`、`language`: エントリーごとの上書き。
- 失敗時は次のエントリーにフォールバックします。

Provider auth は標準順序に従います: `auth-profiles.json` → env vars → `models.providers.*.apiKey`。

**Async completion フィールド:**

- `asyncCompletion.directSend`: `true` の場合、完了した非同期 `music_generate`
  と `video_generate` タスクは、まず直接チャンネル配信を試みます。デフォルト: `false`
  （旧来の requester-session wake/model-delivery 経路）。

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

session tools（`sessions_list`、`sessions_history`、`sessions_send`）でどの session を対象にできるかを制御します。

デフォルト: `tree`（現在の session + そこから spawn された session、たとえば subagent）。

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
- `agent`: 現在の agent id に属する任意の session（同じ agent id 配下で per-sender session を運用している場合は他ユーザーの session も含まれることがあります）。
- `all`: 任意の session。cross-agent targeting には引き続き `tools.agentToAgent` が必要です。
- Sandbox clamp: 現在の session が sandboxed で、`agents.defaults.sandbox.sessionToolsVisibility="spawned"` の場合、`tools.sessions.visibility="all"` であっても visibility は `tree` に強制されます。

### `tools.sessions_spawn`

`sessions_spawn` の inline attachment サポートを制御します。

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

- Attachment は `runtime: "subagent"` でのみサポートされます。ACP runtime では拒否されます。
- ファイルは child workspace の `.openclaw/attachments/<uuid>/` に `.manifest.json` とともに materialize されます。
- Attachment 内容は transcript persistence から自動的に redact されます。
- Base64 入力は厳密な alphabet/padding チェックと decode 前サイズガードで検証されます。
- File permission は directory が `0700`、file が `0600` です。
- Cleanup は `cleanup` policy に従います。`delete` は常に attachment を削除し、`keep` は `retainOnSessionKeep: true` の場合にのみ保持します。

### `tools.experimental`

実験的な組み込み tool フラグ。runtime 固有の auto-enable ルールが適用される場合を除き、デフォルトでは無効です。

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

- `planTool`: 重要な複数ステップ作業の追跡に使う、構造化された `update_plan` tool を有効にします。
- デフォルト: 非 OpenAI provider では `false`。OpenAI と OpenAI Codex 実行では未設定時に自動有効化されます。これを無効にするには `false` を設定してください。
- 有効時、system prompt にも使用ガイダンスが追加され、model は実質的な作業にのみこれを使い、`in_progress` の step を最大 1 つだけ維持します。

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

- `model`: spawn される sub-agent のデフォルト model。省略時、sub-agent は呼び出し元の model を継承します。
- `allowAgents`: リクエスター agent が独自の `subagents.allowAgents` を設定していない場合に、`sessions_spawn` で使う target agent id のデフォルト許可リスト（`["*"]` = 任意。デフォルト: 同じ agent のみ）。
- `runTimeoutSeconds`: tool call で `runTimeoutSeconds` を省略した場合に `sessions_spawn` が使うデフォルト timeout（秒）。`0` は timeout なしを意味します。
- subagent ごとの tool policy: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`。

---

## カスタム provider と base URL

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

- カスタム auth には `authHeader: true` + `headers` を使用します。
- Agent config root を上書きするには `OPENCLAW_AGENT_DIR`（または旧来の環境変数エイリアス `PI_CODING_AGENT_DIR`）を使います。
- 一致する provider ID に対するマージ優先順位:
  - 空でない agent `models.json` の `baseUrl` 値が優先されます。
  - 空でない agent `apiKey` 値は、その provider が現在の config/auth-profile context で SecretRef 管理されていない場合にのみ優先されます。
  - SecretRef 管理の provider `apiKey` 値は、解決済み secret を永続化する代わりに source marker（env ref は `ENV_VAR_NAME`、file/exec ref は `secretref-managed`）から更新されます。
  - SecretRef 管理の provider header 値は、source marker（env ref は `secretref-env:ENV_VAR_NAME`、file/exec ref は `secretref-managed`）から更新されます。
  - 空または欠落している agent `apiKey`/`baseUrl` は config の `models.providers` にフォールバックします。
  - 一致する model の `contextWindow`/`maxTokens` は、明示設定値と暗黙 catalog 値のうち大きい方を使用します。
  - 一致する model の `contextTokens` は、明示的 runtime cap がある場合はそれを保持します。native model metadata を変更せずに有効コンテキストを制限したい場合に使用してください。
  - config で `models.json` を完全に書き換えたい場合は `models.mode: "replace"` を使用します。
  - Marker persistence は source-authoritative です。marker は解決済み runtime secret 値からではなく、active source config snapshot（解決前）から書き込まれます。

### Provider フィールド詳細

- `models.mode`: provider catalog の動作（`merge` または `replace`）。
- `models.providers`: provider id をキーにしたカスタム provider map。
- `models.providers.*.api`: request adapter（`openai-completions`、`openai-responses`、`anthropic-messages`、`google-generative-ai` など）。
- `models.providers.*.apiKey`: provider credential（SecretRef/env substitution 推奨）。
- `models.providers.*.auth`: auth strategy（`api-key`、`token`、`oauth`、`aws-sdk`）。
- `models.providers.*.injectNumCtxForOpenAICompat`: Ollama + `openai-completions` 向けに、request へ `options.num_ctx` を注入します（デフォルト: `true`）。
- `models.providers.*.authHeader`: 必要に応じて `Authorization` header で credential を送るよう強制します。
- `models.providers.*.baseUrl`: 上流 API base URL。
- `models.providers.*.headers`: proxy/tenant routing 用の追加 static header。
- `models.providers.*.request`: model-provider HTTP request 用の transport override。
  - `request.headers`: 追加 header（provider デフォルトとマージ）。値は SecretRef を受け付けます。
  - `request.auth`: auth strategy override。モード: `"provider-default"`（provider の組み込み auth を使用）、`"authorization-bearer"`（`token` 使用）、`"header"`（`headerName`、`value`、任意の `prefix` を使用）。
  - `request.proxy`: HTTP proxy override。モード: `"env-proxy"`（`HTTP_PROXY`/`HTTPS_PROXY` env vars を使用）、`"explicit-proxy"`（`url` 使用）。両モードとも任意の `tls` サブオブジェクトを受け付けます。
  - `request.tls`: 直接接続時の TLS override。フィールド: `ca`、`cert`、`key`、`passphrase`（すべて SecretRef を受け付けます）、`serverName`、`insecureSkipVerify`。
- `models.providers.*.models`: 明示的な provider model catalog entry。
- `models.providers.*.models.*.contextWindow`: native model context window metadata。
- `models.providers.*.models.*.contextTokens`: 任意の runtime context cap。model の native `contextWindow` より小さい有効 context budget を使いたい場合に利用します。
- `models.providers.*.models.*.compat.supportsDeveloperRole`: 任意の互換ヒント。`api: "openai-completions"` で空でない非 native `baseUrl`（host が `api.openai.com` ではない）の場合、OpenClaw はランタイムでこれを `false` に強制します。空または省略した `baseUrl` はデフォルト OpenAI 動作を維持します。
- `models.providers.*.models.*.compat.requiresStringContent`: string-only の OpenAI 互換 chat endpoint 向け任意の互換ヒント。`true` の場合、OpenClaw は pure text の `messages[].content` array を送信前に plain string に flatten します。
- `plugins.entries.amazon-bedrock.config.discovery`: Bedrock 自動 discovery 設定のルート。
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: 暗黙 discovery のオン/オフ。
- `plugins.entries.amazon-bedrock.config.discovery.region`: discovery 用 AWS region。
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: targeted discovery 用の任意の provider-id filter。
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: discovery refresh の polling 間隔。
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: discovered model 用の fallback context window。
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: discovered model 用の fallback max output tokens。

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

Cerebras には `cerebras/zai-glm-4.7` を使用し、Z.AI 直結には `zai/glm-4.7` を使用します。

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

`OPENCODE_API_KEY`（または `OPENCODE_ZEN_API_KEY`）を設定してください。Zen catalog には `opencode/...` 参照を使い、Go catalog には `opencode-go/...` 参照を使います。ショートカット: `openclaw onboard --auth-choice opencode-zen` または `openclaw onboard --auth-choice opencode-go`。

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

- General endpoint: `https://api.z.ai/api/paas/v4`
- Coding endpoint（デフォルト）: `https://api.z.ai/api/coding/paas/v4`
- General endpoint を使う場合は、base URL override 付きの custom provider を定義してください。

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

中国 endpoint には次を使用します: `baseUrl: "https://api.moonshot.cn/v1"` または `openclaw onboard --auth-choice moonshot-api-key-cn`。

ネイティブ Moonshot endpoint は共有 `openai-completions` transport 上で streaming usage 互換性を公開しており、OpenClaw は現在、これを組み込み provider id 単体ではなく endpoint capability に基づいて判定します。

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

Anthropic 互換、組み込み provider です。ショートカット: `openclaw onboard --auth-choice kimi-code-api-key`。

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

Base URL には `/v1` を含めないでください（Anthropic client が付加します）。ショートカット: `openclaw onboard --auth-choice synthetic-api-key`。

</Accordion>

<Accordion title="MiniMax M2.7（直接）">

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
Anthropic 互換 streaming path では、OpenClaw は明示的に `thinking` を設定しない限り、デフォルトで MiniMax thinking を無効にします。`/fast on` または `params.fastMode: true` は `MiniMax-M2.7` を `MiniMax-M2.7-highspeed` に書き換えます。

</Accordion>

<Accordion title="ローカルモデル（LM Studio）">

[Local Models](/ja-JP/gateway/local-models) を参照してください。要約すると、本格的なハードウェア上では LM Studio Responses API 経由で大規模ローカルモデルを実行し、フォールバック用にホスト型モデルを merged のまま維持します。

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

- `allowBundled`: bundled skill のみを対象とする任意の許可リスト（managed/workspace skill には影響しません）。
- `load.extraDirs`: 追加の共有 skill root（最も低い優先順位）。
- `install.preferBrew`: true の場合、`brew` が利用可能なら他の installer kind にフォールバックする前に Homebrew installer を優先します。
- `install.nodeManager`: `metadata.openclaw.install` spec 用の node installer 優先設定（`npm` | `pnpm` | `yarn` | `bun`）。
- `entries.<skillKey>.enabled: false` は、その skill が bundled/installed されていても無効にします。
- `entries.<skillKey>.apiKey`: primary env var を宣言する skill 向けの簡易 API key フィールド（平文文字列または SecretRef オブジェクト）。

---

## Plugins

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
- Discovery は、ネイティブ OpenClaw plugin に加え、manifestless Claude default-layout bundle を含む互換 Codex bundle と Claude bundle も受け付けます。
- **Config の変更には Gateway の再起動が必要です。**
- `allow`: 任意の許可リスト（列挙された plugin のみ読み込まれます）。`deny` が優先されます。
- `plugins.entries.<id>.apiKey`: plugin がサポートする場合の plugin レベル API key 簡易フィールド。
- `plugins.entries.<id>.env`: plugin スコープの env var map。
- `plugins.entries.<id>.hooks.allowPromptInjection`: `false` の場合、core は `before_prompt_build` をブロックし、legacy `before_agent_start` の prompt 変更フィールドを無視します。一方で legacy `modelOverride` と `providerOverride` は保持されます。ネイティブ plugin hook と、対応する bundle 提供 hook directory に適用されます。
- `plugins.entries.<id>.subagent.allowModelOverride`: この plugin が background subagent run に対して run ごとの `provider` および `model` 上書きを要求することを明示的