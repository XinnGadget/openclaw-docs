---
read_when:
    - フィールド単位で正確な設定の意味やデフォルト値が必要な場合
    - チャネル、モデル、Gateway、またはツールの設定ブロックを検証している場合
summary: すべての OpenClaw 設定キー、デフォルト値、チャネル設定の完全リファレンス
title: 設定リファレンス
x-i18n:
    generated_at: "2026-04-06T03:12:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6aa6b24b593f6f07118817afabea4cc7842aca6b7c5602b45f479b40c1685230
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# 設定リファレンス

`~/.openclaw/openclaw.json` で使用可能なすべてのフィールドです。タスク指向の概要については、[Configuration](/ja-JP/gateway/configuration) を参照してください。

設定形式は **JSON5** です（コメントと末尾カンマを使用可能）。すべてのフィールドは任意で、省略した場合 OpenClaw は安全なデフォルト値を使用します。

---

## チャネル

各チャネルは、その設定セクションが存在する場合に自動的に開始されます（`enabled: false` を除く）。

### DM とグループアクセス

すべてのチャネルは DM ポリシーとグループポリシーをサポートします。

| DM ポリシー         | 動作                                                            |
| ------------------- | --------------------------------------------------------------- |
| `pairing`（デフォルト） | 未知の送信者には 1 回限りのペアリングコードが発行され、オーナーの承認が必要 |
| `allowlist`         | `allowFrom` 内の送信者のみ（またはペアリング済み許可ストア）     |
| `open`              | すべての受信 DM を許可（`allowFrom: ["*"]` が必要）             |
| `disabled`          | すべての受信 DM を無視                                          |

| グループポリシー      | 動作                                                   |
| --------------------- | ------------------------------------------------------ |
| `allowlist`（デフォルト） | 設定された許可リストに一致するグループのみ             |
| `open`                | グループ許可リストをバイパス（メンションゲーティングは引き続き適用） |
| `disabled`            | すべてのグループ/ルームメッセージをブロック            |

<Note>
`channels.defaults.groupPolicy` は、プロバイダーの `groupPolicy` が未設定の場合のデフォルト値を設定します。
ペアリングコードは 1 時間で期限切れになります。保留中の DM ペアリング要求は **チャネルごとに 3 件** に制限されます。
プロバイダーブロックが完全に欠落している場合（`channels.<provider>` が存在しない場合）、ランタイムのグループポリシーは起動時警告とともに `allowlist`（フェイルクローズド）にフォールバックします。
</Note>

### チャネルごとのモデル上書き

`channels.modelByChannel` を使用して、特定のチャネル ID をモデルに固定します。値には `provider/model` または設定済みモデルエイリアスを指定できます。このチャネルマッピングは、セッションにすでにモデル上書きが存在しない場合（たとえば `/model` で設定された場合）に適用されます。

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

### チャネルのデフォルト値と heartbeat

`channels.defaults` を使用して、プロバイダー間で共通のグループポリシーと heartbeat の動作を設定します。

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
- `channels.defaults.contextVisibility`: 全チャネル向けの補足コンテキスト可視性モードのデフォルト。値: `all`（デフォルト、すべての引用/スレッド/履歴コンテキストを含む）、`allowlist`（許可リスト済み送信者からのコンテキストのみ含む）、`allowlist_quote`（allowlist と同じだが明示的な引用/返信コンテキストは保持）。チャネルごとの上書き: `channels.<channel>.contextVisibility`。
- `channels.defaults.heartbeat.showOk`: heartbeat 出力に正常なチャネル状態を含める。
- `channels.defaults.heartbeat.showAlerts`: heartbeat 出力に劣化/エラー状態を含める。
- `channels.defaults.heartbeat.useIndicator`: コンパクトなインジケーター形式の heartbeat 出力を表示する。

### WhatsApp

WhatsApp は Gateway の web チャネル（Baileys Web）を通じて実行されます。リンク済みセッションが存在する場合、自動的に開始されます。

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

- 送信コマンドは、`default` アカウントが存在する場合はそれを、存在しない場合は最初に設定されたアカウント ID（ソート順）をデフォルトに使用します。
- オプションの `channels.whatsapp.defaultAccount` は、設定済みアカウント ID と一致する場合、このフォールバック既定アカウント選択を上書きします。
- 旧単一アカウントの Baileys auth dir は、`openclaw doctor` によって `whatsapp/default` へ移行されます。
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

- Bot token: `channels.telegram.botToken` または `channels.telegram.tokenFile`（通常ファイルのみ。シンボリックリンクは拒否）、デフォルトアカウントのフォールバックとして `TELEGRAM_BOT_TOKEN` を使用可能。
- オプションの `channels.telegram.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。
- 複数アカウント構成（2 つ以上のアカウント ID）では、フォールバックルーティングを避けるために、明示的なデフォルト（`channels.telegram.defaultAccount` または `channels.telegram.accounts.default`）を設定してください。これが欠落または無効な場合、`openclaw doctor` が警告します。
- `configWrites: false` は Telegram 起点の設定書き込み（supergroup ID の移行、`/config set|unset`）をブロックします。
- `type: "acp"` を持つトップレベルの `bindings[]` エントリーは、フォーラムトピック向けの永続 ACP バインディングを設定します（`match.peer.id` には正規形の `chatId:topic:topicId` を使用）。フィールドの意味は [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings) と共通です。
- Telegram のストリームプレビューは `sendMessage` + `editMessageText` を使用します（ダイレクトチャットとグループチャットの両方で動作）。
- リトライポリシー: [Retry policy](/ja-JP/concepts/retry) を参照。

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

- Token: `channels.discord.token`。デフォルトアカウントのフォールバックとして `DISCORD_BOT_TOKEN` を使用可能。
- 明示的な Discord `token` を指定した直接送信呼び出しは、その呼び出しに対してその token を使用します。アカウントの retry/policy 設定は、アクティブなランタイムスナップショットで選択されたアカウントから引き続き取得されます。
- オプションの `channels.discord.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。
- 配信先には `user:<id>`（DM）または `channel:<id>`（guild channel）を使用してください。プレフィックスなしの数値 ID は拒否されます。
- ギルド slug は小文字で、スペースは `-` に置換されます。チャネルキーには slug 化された名前（`#` なし）を使用します。ギルド ID を推奨します。
- bot が作成したメッセージはデフォルトで無視されます。`allowBots: true` で有効化されます。bot へのメンションを含む bot メッセージのみ受け入れるには `allowBots: "mentions"` を使用してください（自身のメッセージは引き続き除外）。
- `channels.discord.guilds.<id>.ignoreOtherMentions`（およびチャネル上書き）は、bot ではなく別のユーザーまたはロールにメンションしているメッセージを破棄します（@everyone/@here を除く）。
- `maxLinesPerMessage`（デフォルト 17）は、2000 文字未満でも縦長メッセージを分割します。
- `channels.discord.threadBindings` は Discord のスレッド境界ルーティングを制御します:
  - `enabled`: スレッド境界セッション機能（`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`、およびバインドされた配信/ルーティング）向けの Discord 上書き
  - `idleHours`: 非アクティブ時の自動 unfocus の時間単位上書き（`0` で無効）
  - `maxAgeHours`: 最大有効期間の時間単位上書き（`0` で無効）
  - `spawnSubagentSessions`: `sessions_spawn({ thread: true })` の自動スレッド作成/バインドのオプトインスイッチ
- `type: "acp"` を持つトップレベル `bindings[]` エントリーは、チャネルおよびスレッド向けの永続 ACP バインディングを設定します（`match.peer.id` には channel/thread id を使用）。フィールドの意味は [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings) と共通です。
- `channels.discord.ui.components.accentColor` は、Discord components v2 コンテナのアクセントカラーを設定します。
- `channels.discord.voice` は、Discord 音声チャネル会話と、オプションの自動参加 + TTS 上書きを有効にします。
- `channels.discord.voice.daveEncryption` と `channels.discord.voice.decryptionFailureTolerance` は、`@discordjs/voice` の DAVE オプションにそのまま渡されます（デフォルトは `true` と `24`）。
- OpenClaw はさらに、復号失敗が繰り返された場合に、音声セッションから離脱して再参加することで音声受信の回復も試みます。
- `channels.discord.streaming` は正規の stream mode キーです。旧 `streamMode` と真偽値 `streaming` は自動移行されます。
- `channels.discord.autoPresence` は、ランタイムの可用性を bot presence にマッピングします（healthy => online、degraded => idle、exhausted => dnd）。オプションの status text 上書きも可能です。
- `channels.discord.dangerouslyAllowNameMatching` は、可変な name/tag マッチングを再有効化します（非常時専用の互換モード）。
- `channels.discord.execApprovals`: Discord ネイティブの exec 承認配信と承認者認可。
  - `enabled`: `true`、`false`、または `"auto"`（デフォルト）。auto モードでは、`approvers` または `commands.ownerAllowFrom` から承認者を解決できる場合に exec 承認が有効になります。
  - `approvers`: exec 要求を承認できる Discord user ID。省略時は `commands.ownerAllowFrom` にフォールバックします。
  - `agentFilter`: オプションの agent ID 許可リスト。省略するとすべての agent の承認を転送します。
  - `sessionFilter`: オプションの session key パターン（部分一致または regex）。
  - `target`: 承認プロンプトの送信先。`"dm"`（デフォルト）は承認者の DM に送信、`"channel"` は元のチャネルに送信、`"both"` は両方に送信します。target に `"channel"` を含む場合、ボタンは解決済み承認者のみが使用できます。
  - `cleanupAfterResolve`: `true` の場合、承認、拒否、またはタイムアウト後に承認 DM を削除します。

**リアクション通知モード:** `off`（なし）、`own`（bot 自身のメッセージ、デフォルト）、`all`（すべてのメッセージ）、`allowlist`（`guilds.<id>.users` からの全メッセージ）。

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

- Service account JSON: インライン（`serviceAccount`）またはファイルベース（`serviceAccountFile`）。
- Service account SecretRef もサポートされています（`serviceAccountRef`）。
- 環境変数フォールバック: `GOOGLE_CHAT_SERVICE_ACCOUNT` または `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`。
- 配信先には `spaces/<spaceId>` または `users/<userId>` を使用してください。
- `channels.googlechat.dangerouslyAllowNameMatching` は、可変なメール principal マッチングを再有効化します（非常時専用の互換モード）。

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

- **Socket mode** では `botToken` と `appToken` の両方が必要です（デフォルトアカウントの環境変数フォールバックは `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN`）。
- **HTTP mode** では `botToken` と `signingSecret`（ルートまたはアカウントごと）が必要です。
- `botToken`、`appToken`、`signingSecret`、`userToken` はプレーンテキスト文字列または SecretRef オブジェクトを受け付けます。
- Slack アカウントスナップショットは、`botTokenSource`、`botTokenStatus`、`appTokenStatus`、HTTP mode では `signingSecretStatus` などの認証情報ごとの source/status フィールドを公開します。`configured_unavailable` は、そのアカウントが SecretRef で設定されているが、現在のコマンド/ランタイム経路でシークレット値を解決できなかったことを意味します。
- `configWrites: false` は Slack 起点の設定書き込みをブロックします。
- オプションの `channels.slack.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。
- `channels.slack.streaming` は正規の stream mode キーです。旧 `streamMode` と真偽値 `streaming` は自動移行されます。
- 配信先には `user:<id>`（DM）または `channel:<id>` を使用してください。

**リアクション通知モード:** `off`、`own`（デフォルト）、`all`、`allowlist`（`reactionAllowlist` から）。

**スレッドセッション分離:** `thread.historyScope` はスレッド単位（デフォルト）またはチャネル全体で共有。`thread.inheritParent` は親チャネルの transcript を新規スレッドへコピーします。

- `typingReaction` は、返信処理中に受信した Slack メッセージへ一時的なリアクションを追加し、完了時に削除します。`"hourglass_flowing_sand"` のような Slack emoji shortcode を使用してください。
- `channels.slack.execApprovals`: Slack ネイティブの exec 承認配信と承認者認可。スキーマは Discord と同じです: `enabled`（`true`/`false`/`"auto"`）、`approvers`（Slack user IDs）、`agentFilter`、`sessionFilter`、`target`（`"dm"`、`"channel"`、または `"both"`）。

| アクショングループ | デフォルト | 注記                     |
| ------------------ | ---------- | ------------------------ |
| reactions          | enabled    | リアクション + 一覧      |
| messages           | enabled    | 読み取り/送信/編集/削除  |
| pins               | enabled    | 固定/解除/一覧           |
| memberInfo         | enabled    | メンバー情報             |
| emojiList          | enabled    | カスタム絵文字一覧       |

### Mattermost

Mattermost は plugin として提供されます: `openclaw plugins install @openclaw/mattermost`。

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

Chat modes: `oncall`（@-mention で応答、デフォルト）、`onmessage`（すべてのメッセージ）、`onchar`（トリガープレフィックスで始まるメッセージ）。

Mattermost ネイティブコマンドが有効な場合:

- `commands.callbackPath` はフル URL ではなくパスである必要があります（例: `/api/channels/mattermost/command`）。
- `commands.callbackUrl` は OpenClaw Gateway のエンドポイントを解決し、Mattermost サーバーから到達可能である必要があります。
- ネイティブ slash callback は、slash command 登録時に Mattermost から返されるコマンドごとの token で認証されます。登録に失敗した場合、または有効なコマンドがない場合、OpenClaw は callback を `Unauthorized: invalid command token.` で拒否します。
- プライベート/tailnet/internal な callback host では、Mattermost が `ServiceSettings.AllowedUntrustedInternalConnections` に callback host/domain を含めることを要求する場合があります。フル URL ではなく host/domain 値を使用してください。
- `channels.mattermost.configWrites`: Mattermost 起点の設定書き込みを許可または拒否します。
- `channels.mattermost.requireMention`: チャネルで返信する前に `@mention` を要求します。
- `channels.mattermost.groups.<channelId>.requireMention`: チャネルごとのメンションゲーティング上書き（デフォルトは `"*"`）。
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

**リアクション通知モード:** `off`、`own`（デフォルト）、`all`、`allowlist`（`reactionAllowlist` から）。

- `channels.signal.account`: 特定の Signal アカウント ID にチャネル起動を固定します。
- `channels.signal.configWrites`: Signal 起点の設定書き込みを許可または拒否します。
- オプションの `channels.signal.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。

### BlueBubbles

BlueBubbles は推奨される iMessage 経路です（plugin ベースで、`channels.bluebubbles` の下に設定します）。

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

- ここで扱うコアキーのパス: `channels.bluebubbles`、`channels.bluebubbles.dmPolicy`。
- オプションの `channels.bluebubbles.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。
- `type: "acp"` を持つトップレベル `bindings[]` エントリーは、BlueBubbles 会話を永続 ACP セッションにバインドできます。`match.peer.id` には BlueBubbles handle または target string（`chat_id:*`、`chat_guid:*`、`chat_identifier:*`）を使用します。共有されるフィールドの意味: [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings)。
- BlueBubbles チャネルの完全な設定は [BlueBubbles](/ja-JP/channels/bluebubbles) に記載されています。

### iMessage

OpenClaw は `imsg rpc`（stdio 上の JSON-RPC）を起動します。daemon やポートは不要です。

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

- Messages DB へのフルディスクアクセスが必要です。
- `chat_id:<id>` ターゲットを推奨します。チャット一覧には `imsg chats --limit 20` を使用してください。
- `cliPath` は SSH ラッパーを指すことができます。SCP で添付ファイルを取得するには `remoteHost`（`host` または `user@host`）を設定します。
- `attachmentRoots` と `remoteAttachmentRoots` は受信添付ファイルパスを制限します（デフォルト: `/Users/*/Library/Messages/Attachments`）。
- SCP は厳格な host-key checking を使用するため、relay host key がすでに `~/.ssh/known_hosts` に存在している必要があります。
- `channels.imessage.configWrites`: iMessage 起点の設定書き込みを許可または拒否します。
- `type: "acp"` を持つトップレベル `bindings[]` エントリーは、iMessage 会話を永続 ACP セッションにバインドできます。`match.peer.id` には正規化済み handle または明示的な chat target（`chat_id:*`、`chat_guid:*`、`chat_identifier:*`）を使用します。共有されるフィールドの意味: [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings)。

<Accordion title="iMessage SSH ラッパーの例">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix は拡張機能ベースで、`channels.matrix` の下に設定されます。

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

- token 認証は `accessToken`、password 認証は `userId` + `password` を使用します。
- `channels.matrix.proxy` は、Matrix HTTP トラフィックを明示的な HTTP(S) proxy 経由にします。名前付きアカウントでは `channels.matrix.accounts.<id>.proxy` で上書きできます。
- `channels.matrix.allowPrivateNetwork` は、プライベート/内部 homeserver を許可します。`proxy` と `allowPrivateNetwork` は独立した制御です。
- `channels.matrix.defaultAccount` は、複数アカウント構成で優先アカウントを選択します。
- `channels.matrix.execApprovals`: Matrix ネイティブの exec 承認配信と承認者認可。
  - `enabled`: `true`、`false`、または `"auto"`（デフォルト）。auto モードでは、`approvers` または `commands.ownerAllowFrom` から承認者を解決できる場合に exec 承認が有効になります。
  - `approvers`: exec 要求を承認できる Matrix user ID（例: `@owner:example.org`）。
  - `agentFilter`: オプションの agent ID 許可リスト。省略するとすべての agent の承認を転送します。
  - `sessionFilter`: オプションの session key パターン（部分一致または regex）。
  - `target`: 承認プロンプトの送信先。`"dm"`（デフォルト）、`"channel"`（元のルーム）、または `"both"`。
  - アカウントごとの上書き: `channels.matrix.accounts.<id>.execApprovals`。
- `channels.matrix.dm.sessionScope` は、Matrix DM をどのようにセッションへまとめるかを制御します。`per-user`（デフォルト）はルーティング先 peer ごとに共有し、`per-room` は各 DM ルームを分離します。
- Matrix の status probe と live directory lookup は、ランタイムトラフィックと同じ proxy ポリシーを使用します。
- Matrix の完全な設定、ターゲティング規則、設定例は [Matrix](/ja-JP/channels/matrix) に記載されています。

### Microsoft Teams

Microsoft Teams は拡張機能ベースで、`channels.msteams` の下に設定されます。

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

- ここで扱うコアキーのパス: `channels.msteams`、`channels.msteams.configWrites`。
- Teams の完全な設定（認証情報、webhook、DM/グループポリシー、チームごと/チャネルごとの上書き）は [Microsoft Teams](/ja-JP/channels/msteams) に記載されています。

### IRC

IRC は拡張機能ベースで、`channels.irc` の下に設定されます。

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

- ここで扱うコアキーのパス: `channels.irc`、`channels.irc.dmPolicy`、`channels.irc.configWrites`、`channels.irc.nickserv.*`。
- オプションの `channels.irc.defaultAccount` は、設定済みアカウント ID と一致する場合、デフォルトアカウント選択を上書きします。
- IRC チャネルの完全な設定（host/port/TLS/channels/allowlists/mention gating）は [IRC](/ja-JP/channels/irc) に記載されています。

### 複数アカウント（全チャネル）

チャネルごとに複数アカウントを実行します（それぞれ固有の `accountId` を持ちます）。

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
- 環境変数 token は **default** アカウントにのみ適用されます。
- ベースチャネル設定は、アカウントごとに上書きしない限り、すべてのアカウントに適用されます。
- `bindings[].match.accountId` を使用して、各アカウントを別々のエージェントへルーティングします。
- `openclaw channels add`（またはチャネル onboarding）で、単一アカウントのトップレベルチャネル設定のまま非デフォルトアカウントを追加すると、OpenClaw はまずアカウントスコープのトップレベル単一アカウント値をチャネルアカウントマップへ昇格させ、元のアカウントが引き続き動作するようにします。ほとんどのチャネルではそれらは `channels.<channel>.accounts.default` に移動されますが、Matrix は既存の一致する named/default target を保持することがあります。
- 既存のチャネル専用バインディング（`accountId` なし）はデフォルトアカウントに引き続き一致します。アカウントスコープのバインディングは引き続き任意です。
- `openclaw doctor --fix` も、アカウントスコープのトップレベル単一アカウント値を、そのチャネル向けに昇格したアカウントへ移動することで、混在形状を修復します。ほとんどのチャネルでは `accounts.default` を使用し、Matrix は既存の一致する named/default target を保持できる場合があります。

### その他の拡張チャネル

多くの拡張チャネルは `channels.<id>` として設定され、それぞれの専用チャネルページに記載されています（たとえば Feishu、Matrix、LINE、Nostr、Zalo、Nextcloud Talk、Synology Chat、Twitch）。
完全なチャネル一覧: [Channels](/ja-JP/channels)。

### グループチャットのメンションゲーティング

グループメッセージはデフォルトで **メンション必須** です（メタデータメンションまたは安全な regex パターン）。WhatsApp、Telegram、Discord、Google Chat、iMessage のグループチャットに適用されます。

**メンションの種類:**

- **メタデータメンション**: ネイティブなプラットフォームの @-mention。WhatsApp の self-chat mode では無視されます。
- **テキストパターン**: `agents.list[].groupChat.mentionPatterns` にある安全な regex パターン。無効なパターンや安全でないネスト反復は無視されます。
- メンションゲーティングは、検出が可能な場合（ネイティブメンションまたは少なくとも 1 つのパターンがある場合）にのみ強制されます。

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

`messages.groupChat.historyLimit` はグローバルデフォルトを設定します。チャネル側では `channels.<channel>.historyLimit`（またはアカウントごと）で上書きできます。無効にするには `0` を設定します。

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

サポート対象: `telegram`、`whatsapp`、`discord`、`slack`、`signal`、`imessage`、`msteams`。

#### Self-chat mode

自分の番号を `allowFrom` に含めると self-chat mode が有効になります（ネイティブな @-mention を無視し、テキストパターンにのみ応答します）。

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

<Accordion title="コマンドの詳細">

- テキストコマンドは、先頭に `/` が付いた**単独の**メッセージである必要があります。
- `native: "auto"` は Discord/Telegram でネイティブコマンドを有効にし、Slack では無効のままにします。
- チャネルごとの上書き: `channels.discord.commands.native`（bool または `"auto"`）。`false` は以前登録されたコマンドを解除します。
- `channels.telegram.customCommands` は、Telegram bot メニューに追加エントリーを加えます。
- `bash: true` は、ホスト shell 向けの `! <cmd>` を有効にします（別名: `/bash`）。`tools.elevated.enabled` と、送信者が `tools.elevated.allowFrom.<channel>` に含まれている必要があります。
- `config: true` は `/config` を有効にします（`openclaw.json` を読み書き）。Gateway `chat.send` クライアントでは、永続的な `/config set|unset` 書き込みには `operator.admin` も必要です。読み取り専用の `/config show` は通常の書き込みスコープの operator クライアントでも引き続き利用できます。
- `channels.<provider>.configWrites` は、チャネルごとの設定変更を制御します（デフォルト: true）。
- 複数アカウントチャネルでは、`channels.<provider>.accounts.<id>.configWrites` も、そのアカウントを対象とする書き込み（たとえば `/allowlist --config --account <id>` や `/config set channels.<provider>.accounts.<id>...`）を制御します。
- `allowFrom` はプロバイダーごとです。設定されている場合、これが**唯一の**認可ソースとなり（チャネル許可リスト/ペアリングおよび `useAccessGroups` は無視されます）。
- `useAccessGroups: false` は、`allowFrom` が設定されていない場合に、コマンドが access-group ポリシーをバイパスできるようにします。

</Accordion>

---

## エージェントのデフォルト値

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

`agents.list[].skills` を設定していないエージェント向けの、オプションのデフォルト skill 許可リスト。

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

- `agents.defaults.skills` を省略すると、デフォルトでは Skills は無制限です。
- `agents.list[].skills` を省略すると、デフォルト値を継承します。
- Skills をなしにするには `agents.list[].skills: []` を設定します。
- `agents.list[].skills` が空でない場合、そのリストがそのエージェントの最終セットになります。デフォルト値とはマージされません。

### `agents.defaults.skipBootstrap`

workspace bootstrap ファイル（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、`BOOTSTRAP.md`）の自動作成を無効にします。

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.bootstrapMaxChars`

切り詰め前の、workspace bootstrap ファイル 1 つあたりの最大文字数。デフォルト: `20000`。

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

すべての workspace bootstrap ファイルにまたがって注入される総文字数の上限。デフォルト: `150000`。

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

bootstrap コンテキストが切り詰められたときに、エージェントに見える警告文を制御します。
デフォルト: `"once"`。

- `"off"`: システムプロンプトに警告文を注入しません。
- `"once"`: 一意の切り詰めシグネチャごとに 1 回だけ警告を注入します（推奨）。
- `"always"`: 切り詰めがあるたびに毎回警告を注入します。

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

プロバイダー呼び出し前に transcript/tool の画像ブロックで許可される、最長辺の最大ピクセル数。
デフォルト: `1200`。

値を小さくすると通常は vision token 使用量とリクエストペイロードサイズが減ります。
値を大きくするとより多くの視覚的詳細が保持されます。

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

システムプロンプトのコンテキスト用 timezone（メッセージのタイムスタンプではありません）。ホストの timezone にフォールバックします。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

システムプロンプトでの時刻形式。デフォルト: `auto`（OS の設定）。

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
  - オブジェクト形式は primary に加えて、順序付き failover model を設定します。
- `imageModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - `image` ツール経路で vision-model 設定として使用されます。
  - 選択済み/デフォルト model が画像入力を受け付けられない場合のフォールバックルーティングにも使用されます。
- `imageGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共通の画像生成機能と、将来の画像生成ツール/plugin サーフェスで使用されます。
  - 一般的な値: Gemini ネイティブ画像生成の `google/gemini-3.1-flash-image-preview`、fal の `fal/fal-ai/flux/dev`、または OpenAI Images の `openai/gpt-image-1`。
  - プロバイダー/モデルを直接選択する場合は、対応するプロバイダー認証/API key も設定してください（例: `google/*` には `GEMINI_API_KEY` または `GOOGLE_API_KEY`、`openai/*` には `OPENAI_API_KEY`、`fal/*` には `FAL_KEY`）。
  - 省略した場合でも、`image_generate` は認証済みプロバイダーのデフォルトを推測できます。現在のデフォルトプロバイダーを先に試し、その後で残りの登録済み画像生成プロバイダーを provider-id 順に試します。
- `musicGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共通の音楽生成機能と、組み込み `music_generate` ツールで使用されます。
  - 一般的な値: `google/lyria-3-clip-preview`、`google/lyria-3-pro-preview`、または `minimax/music-2.5+`。
  - 省略した場合でも、`music_generate` は認証済みプロバイダーのデフォルトを推測できます。現在のデフォルトプロバイダーを先に試し、その後で残りの登録済み音楽生成プロバイダーを provider-id 順に試します。
  - プロバイダー/モデルを直接選択する場合は、対応するプロバイダー認証/API key も設定してください。
- `videoGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共通の動画生成機能と、組み込み `video_generate` ツールで使用されます。
  - 一般的な値: `qwen/wan2.6-t2v`、`qwen/wan2.6-i2v`、`qwen/wan2.6-r2v`、`qwen/wan2.6-r2v-flash`、または `qwen/wan2.7-r2v`。
  - 省略した場合でも、`video_generate` は認証済みプロバイダーのデフォルトを推測できます。現在のデフォルトプロバイダーを先に試し、その後で残りの登録済み動画生成プロバイダーを provider-id 順に試します。
  - プロバイダー/モデルを直接選択する場合は、対応するプロバイダー認証/API key も設定してください。
  - バンドルされた Qwen 動画生成プロバイダーは現在、最大 1 本の出力動画、1 枚の入力画像、4 本の入力動画、10 秒の長さ、およびプロバイダーレベルの `size`、`aspectRatio`、`resolution`、`audio`、`watermark` オプションをサポートしています。
- `pdfModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - `pdf` ツールのモデルルーティングに使用されます。
  - 省略した場合、PDF ツールは `imageModel`、次に解決済みの session/default model にフォールバックします。
- `pdfMaxBytesMb`: `pdf` ツール呼び出し時に `maxBytesMb` が渡されない場合の、デフォルト PDF サイズ上限。
- `pdfMaxPages`: `pdf` ツールで抽出フォールバックモードにより考慮されるデフォルト最大ページ数。
- `verboseDefault`: エージェント向けのデフォルト verbose レベル。値: `"off"`、`"on"`、`"full"`。デフォルト: `"off"`。
- `elevatedDefault`: エージェント向けのデフォルト elevated-output レベル。値: `"off"`、`"on"`、`"ask"`、`"full"`。デフォルト: `"on"`。
- `model.primary`: 形式は `provider/model`（例: `openai/gpt-5.4`）。provider を省略した場合、OpenClaw はまず alias を試し、次にその model id に一致する一意の configured-provider を探し、それでも見つからない場合にのみ configured default provider にフォールバックします（非推奨の互換動作なので、明示的な `provider/model` を推奨します）。その provider が設定済み default model をもはや提供していない場合、OpenClaw は古い削除済み provider の default を表面化する代わりに、最初の configured provider/model にフォールバックします。
- `models`: `/model` 用の設定済み model catalog と許可リスト。各エントリーには `alias`（ショートカット）と `params`（プロバイダー固有。例: `temperature`、`maxTokens`、`cacheRetention`、`context1m`）を含められます。
- `params`: すべての model に適用されるグローバルデフォルト provider parameters。`agents.defaults.params` で設定します（例: `{ cacheRetention: "long" }`）。
- `params` のマージ優先順位（config）: `agents.defaults.params`（グローバルベース）が `agents.defaults.models["provider/model"].params`（model ごと）で上書きされ、さらに `agents.list[].params`（一致する agent id）がキーごとに上書きします。詳細は [Prompt Caching](/ja-JP/reference/prompt-caching) を参照してください。
- これらのフィールドを変更する config writer（たとえば `/models set`、`/models set-image`、fallback の追加/削除コマンド）は、正規のオブジェクト形式で保存し、可能な限り既存の fallback リストを保持します。
- `maxConcurrent`: セッション間での最大並列 agent 実行数（各セッション内は引き続き直列）。デフォルト: 4。

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

設定した alias は常にデフォルトより優先されます。

Z.AI GLM-4.x model は、`--thinking off` を設定するか、`agents.defaults.models["zai/<model>"].params.thinking` を自分で定義しない限り、自動的に thinking mode を有効にします。
Z.AI model は、ツール呼び出しストリーミングのためにデフォルトで `tool_stream` を有効にします。無効にするには `agents.defaults.models["zai/<model>"].params.tool_stream` を `false` に設定してください。
Anthropic Claude 4.6 model は、明示的な thinking level が設定されていない場合、デフォルトで `adaptive` thinking を使用します。

- `sessionArg` が設定されている場合、sessions がサポートされます。
- `imageArg` がファイルパスを受け付ける場合、画像パススルーがサポートされます。

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

- `every`: duration string（ms/s/m/h）。デフォルト: `30m`（API-key auth）または `1h`（OAuth auth）。無効にするには `0m` を設定します。
- `suppressToolErrorWarnings`: true の場合、heartbeat 実行中の tool error warning payload を抑制します。
- `directPolicy`: direct/DM 配信ポリシー。`allow`（デフォルト）は direct-target 配信を許可します。`block` は direct-target 配信を抑制し、`reason=dm-blocked` を出力します。
- `lightContext`: true の場合、heartbeat 実行は軽量 bootstrap context を使用し、workspace bootstrap ファイルのうち `HEARTBEAT.md` のみを保持します。
- `isolatedSession`: true の場合、各 heartbeat 実行は prior conversation history なしの新規 session で実行されます。cron の `sessionTarget: "isolated"` と同じ分離パターンです。heartbeat ごとの token コストを約 100K から約 2-5K tokens に削減します。
- agent ごと: `agents.list[].heartbeat` を設定します。いずれかの agent が `heartbeat` を定義すると、**その agent のみ** が heartbeat を実行します。
- heartbeats は完全な agent turn を実行するため、間隔を短くすると token 消費が増えます。

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

- `mode`: `default` または `safeguard`（長い履歴向けのチャンク分割要約）。[Compaction](/ja-JP/concepts/compaction) を参照。
- `timeoutSeconds`: 1 回の compaction 操作に許可される最大秒数。これを超えると OpenClaw は中止します。デフォルト: `900`。
- `identifierPolicy`: `strict`（デフォルト）、`off`、または `custom`。`strict` は compaction 要約時に組み込みの opaque identifier 保持ガイダンスを先頭に付加します。
- `identifierInstructions`: `identifierPolicy=custom` のときに使われる、オプションの custom identifier-preservation テキスト。
- `postCompactionSections`: compaction 後に再注入する AGENTS.md の H2/H3 セクション名。デフォルトは `["Session Startup", "Red Lines"]`。無効にするには `[]` を設定します。未設定または明示的にこのデフォルトペアが設定されている場合、旧 `Every Session`/`Safety` 見出しも legacy fallback として受け入れられます。
- `model`: compaction 要約専用のオプション `provider/model-id` 上書き。メイン session は 1 つの model を維持しつつ、compaction 要約は別 model で実行したい場合に使用します。未設定なら compaction は session の primary model を使用します。
- `notifyUser`: `true` の場合、compaction 開始時にユーザーへ短い通知（例: 「Compacting context...」）を送信します。デフォルトでは無効で、compaction を静かに保ちます。
- `memoryFlush`: 自動 compaction 前に durable memory を保存するための silent agentic turn。workspace が read-only の場合はスキップされます。

### `agents.defaults.contextPruning`

LLM 送信前に、メモリ上のコンテキストから**古い tool result** を pruning します。ディスク上の session history は**変更しません**。

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

<Accordion title="cache-ttl mode の動作">

- `mode: "cache-ttl"` は pruning pass を有効にします。
- `ttl` は、最後の cache touch 後に pruning を再実行できるまでの間隔を制御します。
- pruning はまず oversized な tool result を soft-trim し、その後必要に応じて古い tool result を hard-clear します。

**Soft-trim** は先頭 + 末尾を残し、中間に `...` を挿入します。

**Hard-clear** は tool result 全体を placeholder に置き換えます。

注記:

- image block は決して trim/clear されません。
- ratio は文字数ベース（概算）であり、正確な token 数ではありません。
- `keepLastAssistants` 個未満の assistant message しか存在しない場合、pruning はスキップされます。

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

- Telegram 以外のチャネルでは、block reply を有効にするために明示的な `*.blockStreaming: true` が必要です。
- チャネルごとの上書き: `channels.<channel>.blockStreamingCoalesce`（およびアカウントごとの variant）。Signal/Slack/Discord/Google Chat のデフォルトは `minChars: 1500`。
- `humanDelay`: block reply 間のランダムな待機。`natural` = 800–2500ms。agent ごとの上書き: `agents.list[].humanDelay`。

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

- デフォルト: direct chats/mentions では `instant`、メンションされていない group chats では `message`。
- session ごとの上書き: `session.typingMode`、`session.typingIntervalSeconds`。

[Typing Indicators](/ja-JP/concepts/typing-indicators) を参照してください。

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

組み込みエージェント向けのオプションの sandboxing。完全ガイドは [Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。

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
- `ssh`: 汎用 SSH ベースの remote runtime
- `openshell`: OpenShell runtime

`backend: "openshell"` を選択した場合、runtime 固有の設定は
`plugins.entries.openshell.config` に移動します。

**SSH backend config:**

- `target`: `user@host[:port]` 形式の SSH target
- `command`: SSH クライアントコマンド（デフォルト: `ssh`）
- `workspaceRoot`: スコープごとの workspace に使用される絶対 remote root
- `identityFile` / `certificateFile` / `knownHostsFile`: OpenSSH に渡される既存のローカルファイル
- `identityData` / `certificateData` / `knownHostsData`: OpenClaw がランタイム時に一時ファイルへ materialize するインライン内容または SecretRef
- `strictHostKeyChecking` / `updateHostKeys`: OpenSSH の host-key policy ノブ

**SSH auth 優先順位:**

- `identityData` は `identityFile` より優先
- `certificateData` は `certificateFile` より優先
- `knownHostsData` は `knownHostsFile` より優先
- SecretRef ベースの `*Data` 値は、sandbox session 開始前にアクティブな secrets runtime snapshot から解決されます

**SSH backend の動作:**

- create または recreate の後に remote workspace を 1 回 seed します
- その後は remote SSH workspace を canonical として維持します
- `exec`、file tools、media path を SSH 経由にルーティングします
- remote 側の変更をホストへ自動で同期しません
- sandbox browser container はサポートしません

**Workspace access:**

- `none`: `~/.openclaw/sandboxes` 配下のスコープごとの sandbox workspace
- `ro`: `/workspace` に sandbox workspace、`/agent` に agent workspace を read-only でマウント
- `rw`: `/workspace` に agent workspace を read/write でマウント

**Scope:**

- `session`: セッションごとの container + workspace
- `agent`: エージェントごとに 1 つの container + workspace（デフォルト）
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

- `mirror`: exec 前に local から remote へ seed し、exec 後に同期し戻す。local workspace が canonical のまま維持されます
- `remote`: sandbox 作成時に 1 回だけ remote を seed し、その後は remote workspace を canonical として維持します

`remote` mode では、OpenClaw 外で行われたホスト側の local 編集は、seed step 後に sandbox に自動同期されません。
transport は OpenShell sandbox への SSH ですが、sandbox lifecycle とオプションの mirror sync は plugin が管理します。

**`setupCommand`** は container 作成後に 1 回だけ実行されます（`sh -lc` 経由）。network egress、書き込み可能な root、root user が必要です。

**Container はデフォルトで `network: "none"`** です — agent に outbound access が必要な場合は `"bridge"`（または custom bridge network）に設定してください。
`"host"` はブロックされます。`"container:<id>"` もデフォルトでブロックされますが、
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` を明示的に設定した場合のみ使用可能です（非常時専用）。

**受信添付ファイル** は、アクティブ workspace の `media/inbound/*` に stage されます。

**`docker.binds`** は追加のホストディレクトリをマウントします。グローバルおよび agent ごとの binds はマージされます。

**Sandboxed browser**（`sandbox.browser.enabled`）: container 内の Chromium + CDP。noVNC URL が system prompt に注入されます。`openclaw.json` の `browser.enabled` は不要です。
noVNC 観察アクセスはデフォルトで VNC auth を使用し、OpenClaw は共有 URL にパスワードを露出する代わりに短命 token URL を発行します。

- `allowHostControl: false`（デフォルト）は、sandboxed session がホスト browser を対象にすることをブロックします。
- `network` のデフォルトは `openclaw-sandbox-browser`（専用 bridge network）です。グローバル bridge 接続が明示的に必要な場合にのみ `bridge` に設定してください。
- `cdpSourceRange` は、container エッジでの CDP ingress を CIDR 範囲（例: `172.21.0.1/32`）に制限できます。
- `sandbox.browser.binds` は、sandbox browser container のみに追加のホストディレクトリをマウントします。設定された場合（`[]` を含む）、browser container では `docker.binds` を置き換えます。
- 起動時のデフォルトは `scripts/sandbox-browser-entrypoint.sh` に定義され、container host 向けに調整されています:
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
  - `--disable-3d-apis`、`--disable-software-rasterizer`、`--disable-gpu` はデフォルトで有効で、WebGL/3D の利用で必要な場合は `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` で無効化できます。
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` は、ワークフローが extensions に依存している場合に再有効化します。
  - `--renderer-process-limit=2` は `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` で変更できます。`0` にすると Chromium のデフォルトの process limit を使います。
  - さらに、`noSandbox` が有効な場合は `--no-sandbox` と `--disable-setuid-sandbox`。
  - デフォルト値は container image のベースラインです。container のデフォルト値を変更するには、custom browser image と custom entrypoint を使用してください。

</Accordion>

Browser sandboxing と `sandbox.docker.binds` は現在 Docker 専用です。

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
- `default`: 複数設定されている場合は最初のものが優先されます（警告を記録）。1 つもない場合は list の最初のエントリーがデフォルトです。
- `model`: 文字列形式は `primary` のみを上書きします。オブジェクト形式 `{ primary, fallbacks }` は両方を上書きします（`[]` はグローバル fallback を無効化）。`primary` だけを上書きする cron job は、`fallbacks: []` を設定しない限り、デフォルト fallback を継承します。
- `params`: 選択された `agents.defaults.models` エントリーに対してマージされる agent ごとの stream params。`cacheRetention`、`temperature`、`maxTokens` などの agent 固有上書きに使い、model catalog 全体の重複を避けます。
- `skills`: オプションの agent ごとの skill 許可リスト。省略した場合、その agent は設定されていれば `agents.defaults.skills` を継承します。明示的なリストはデフォルトをマージせずに置き換え、`[]` は Skills なしを意味します。
- `thinkingDefault`: オプションの agent ごとのデフォルト thinking level（`off | minimal | low | medium | high | xhigh | adaptive`）。メッセージごとまたは session 上書きが未設定のとき、この agent では `agents.defaults.thinkingDefault` を上書きします。
- `reasoningDefault`: オプションの agent ごとのデフォルト reasoning visibility（`on | off | stream`）。メッセージごとまたは session の reasoning 上書きが未設定のときに適用されます。
- `fastModeDefault`: オプションの agent ごとの fast mode デフォルト（`true | false`）。メッセージごとまたは session の fast-mode 上書きが未設定のときに適用されます。
- `runtime`: オプションの agent ごとの runtime descriptor。agent がデフォルトで ACP harness session を使うべき場合は `type: "acp"` と `runtime.acp` のデフォルト値（`agent`、`backend`、`mode`、`cwd`）を使用します。
- `identity.avatar`: workspace 相対パス、`http(s)` URL、または `data:` URI。
- `identity` はデフォルト値を導出します: `emoji` から `ackReaction`、`name`/`emoji` から `mentionPatterns`。
- `subagents.allowAgents`: `sessions_spawn` 用の agent id 許可リスト（`["*"]` = 任意。デフォルト: 同じ agent のみ）。
- Sandbox 継承ガード: 要求元 session が sandboxed の場合、`sessions_spawn` は unsandboxed で実行される target を拒否します。
- `subagents.requireAgentId`: true の場合、`agentId` を省略した `sessions_spawn` 呼び出しをブロックします（明示的な profile 選択を強制。デフォルト: false）。

---

## 複数エージェントのルーティング

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

### Binding match fields

- `type`（オプション）: 通常の routing には `route`（省略時も route）、永続 ACP conversation binding には `acp`。
- `match.channel`（必須）
- `match.accountId`（オプション。`*` = 任意のアカウント、省略 = デフォルトアカウント）
- `match.peer`（オプション。`{ kind: direct|group|channel, id }`）
- `match.guildId` / `match.teamId`（オプション。チャネル固有）
- `acp`（オプション。`type: "acp"` の場合のみ）: `{ mode, label, cwd, backend }`

**決定的なマッチ順序:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId`（peer/guild/team なしの厳密一致）
5. `match.accountId: "*"`（チャネル全体）
6. デフォルト agent

各 tier 内では、最初に一致した `bindings` エントリーが優先されます。

`type: "acp"` エントリーでは、OpenClaw は厳密な conversation identity（`match.channel` + account + `match.peer.id`）で解決し、上記の route binding tier 順序は使用しません。

### agent ごとの access profile

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

<Accordion title="Session フィールドの詳細">

- **`scope`**: group-chat context の基本 session grouping 戦略。
  - `per-sender`（デフォルト）: チャネル context 内で送信者ごとに分離された session。
  - `global`: チャネル context 内のすべての参加者で 1 つの session を共有（共有 context が意図されている場合にのみ使用）。
- **`dmScope`**: DM の grouping 方法。
  - `main`: すべての DM が main session を共有。
  - `per-peer`: チャネルをまたいで sender id ごとに分離。
  - `per-channel-peer`: チャネル + sender ごとに分離（複数ユーザー inbox に推奨）。
  - `per-account-channel-peer`: account + channel + sender ごとに分離（複数アカウントに推奨）。
- **`identityLinks`**: cross-channel session 共有のための、正規 ID から provider 接頭辞付き peer へのマップ。
- **`reset`**: 主 reset ポリシー。`daily` はローカル時間の `atHour` に reset、`idle` は `idleMinutes` 後に reset。両方が設定されている場合は、先に期限切れになる方が優先されます。
- **`resetByType`**: タイプごとの上書き（`direct`、`group`、`thread`）。旧 `dm` も `direct` の alias として受け付けます。
- **`parentForkMaxTokens`**: forked thread session 作成時に許可される parent session の `totalTokens` 最大値（デフォルト `100000`）。
  - parent の `totalTokens` がこの値を超える場合、OpenClaw は parent transcript history を引き継がず、新しい thread session を開始します。
  - このガードを無効にして常に parent fork を許可するには `0` を設定します。
- **`mainKey`**: 旧フィールド。ランタイムは現在常に `"main"` を main direct-chat bucket に使用します。
- **`agentToAgent.maxPingPongTurns`**: agent-to-agent exchange 中の返信往復ターンの最大数（整数、範囲: `0`–`5`）。`0` で ping-pong chaining を無効化。
- **`sendPolicy`**: `channel`、`chatType`（`direct|group|channel`、旧 `dm` alias あり）、`keyPrefix`、または `rawKeyPrefix` で一致。最初の deny が優先されます。
- **`maintenance`**: session-store の cleanup + retention 制御。
  - `mode`: `warn` は警告のみ、`enforce` は cleanup を適用。
  - `pruneAfter`: 古いエントリーの age cutoff（デフォルト `30d`）。
  - `maxEntries`: `sessions.json` 内の最大エントリー数（デフォルト `500`）。
  - `rotateBytes`: `sessions.json` がこのサイズを超えたら rotate（デフォルト `10mb`）。
  - `resetArchiveRetention`: `*.reset.<timestamp>` transcript archive の retention。デフォルトは `pruneAfter`。無効にするには `false`。
  - `maxDiskBytes`: オプションの sessions-directory disk budget。`warn` mode では警告を記録し、`enforce` mode では最も古い artifact/session から削除します。
  - `highWaterBytes`: budget cleanup 後のオプション目標値。デフォルトは `maxDiskBytes` の `80%`。
- **`threadBindings`**: thread-bound session 機能のグローバルデフォルト。
  - `enabled`: マスターデフォルトスイッチ（プロバイダーが上書き可能。Discord は `channels.discord.threadBindings.enabled` を使用）
  - `idleHours`: 非アクティブ時の自動 unfocus のデフォルト時間（`0` で無効。プロバイダーが上書き可能）
  - `maxAgeHours`: 最大有効期間のデフォルト時間（`0` で無効。プロバイダーが上書き可能）

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

チャネル/アカウントごとの上書き: `channels.<channel>.responsePrefix`、`channels.<channel>.accounts.<id>.responsePrefix`。

解決順序（最も具体的なものが優先）: account → channel → global。`""` は無効化し、上位への継承も止めます。`"auto"` は `[{identity.name}]` を導出します。

**テンプレート変数:**

| 変数              | 説明                   | 例                          |
| ----------------- | ---------------------- | --------------------------- |
| `{model}`         | 短い model 名          | `claude-opus-4-6`           |
| `{modelFull}`     | 完全な model 識別子    | `anthropic/claude-opus-4-6` |
| `{provider}`      | provider 名            | `anthropic`                 |
| `{thinkingLevel}` | 現在の thinking level  | `high`, `low`, `off`        |
| `{identity.name}` | agent identity 名      | （`"auto"` と同じ）         |

変数は大文字小文字を区別しません。`{think}` は `{thinkingLevel}` の alias です。

### Ack reaction

- デフォルトはアクティブ agent の `identity.emoji`、それ以外は `"👀"`。無効にするには `""` を設定します。
- チャネルごとの上書き: `channels.<channel>.ackReaction`、`channels.<channel>.accounts.<id>.ackReaction`。
- 解決順序: account → channel → `messages.ackReaction` → identity fallback。
- Scope: `group-mentions`（デフォルト）、`group-all`、`direct`、`all`。
- `removeAckAfterReply`: Slack、Discord、Telegram で reply 後に ack を削除します。
- `messages.statusReactions.enabled`: Slack、Discord、Telegram で lifecycle status reaction を有効にします。
  Slack と Discord では、未設定時は ack reaction がアクティブなら status reaction も有効のままです。
  Telegram では、lifecycle status reaction を有効にするには明示的に `true` を設定してください。

### Inbound debounce

同じ送信者からの高速なテキストのみのメッセージを、1 回の agent turn にまとめます。media/attachment は即時に flush されます。control command は debouncing をバイパスします。

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
- `summaryModel` は auto-summary に対して `agents.defaults.model.primary` を上書きします。
- `modelOverrides` はデフォルトで有効です。`modelOverrides.allowProvider` のデフォルトは `false`（オプトイン）。
- API key は `ELEVENLABS_API_KEY`/`XI_API_KEY` と `OPENAI_API_KEY` にフォールバックします。
- `openai.baseUrl` は OpenAI TTS endpoint を上書きします。解決順序は config、次に `OPENAI_TTS_BASE_URL`、最後に `https://api.openai.com/v1` です。
- `openai.baseUrl` が OpenAI 以外の endpoint を指している場合、OpenClaw はそれを OpenAI 互換 TTS server とみなし、model/voice 検証を緩和します。

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

- `talk.provider` は、複数の Talk provider が設定されている場合、`talk.providers` 内のキーと一致する必要があります。
- 旧フラット Talk キー（`talk.voiceId`、`talk.voiceAliases`、`talk.modelId`、`talk.outputFormat`、`talk.apiKey`）は互換専用で、自動的に `talk.providers.<provider>` へ移行されます。
- Voice ID は `ELEVENLABS_VOICE_ID` または `SAG_VOICE_ID` にフォールバックします。
- `providers.*.apiKey` はプレーンテキスト文字列または SecretRef オブジェクトを受け付けます。
- `ELEVENLABS_API_KEY` フォールバックは、Talk API key が設定されていない場合にのみ適用されます。
- `providers.*.voiceAliases` は、Talk directive が friendly name を使えるようにします。
- `silenceTimeoutMs` は、Talk mode がユーザーの無音後に transcript を送信するまで待つ時間を制御します。未設定の場合、プラットフォームデフォルトの pause window（`macOS と Android は 700 ms、iOS は 900 ms`）が維持されます。

---

## Tools

### Tool profile

`tools.profile` は、`tools.allow`/`tools.deny` より前にベース許可リストを設定します。

ローカル onboarding は、新規 local config で未設定の場合、デフォルトで `tools.profile: "coding"` を設定します（既存の明示的 profile は保持されます）。

| Profile     | 含まれる内容                                                                                                                |
| ----------- | --------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | `session_status` のみ                                                                                                       |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                  |
| `full`      | 制限なし（未設定と同じ）                                                                                                    |

### Tool group

| Group              | Tools                                                                                                                   |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec`, `process`, `code_execution`（`bash` は `exec` の alias として受理）                                            |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                                                  |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory`     | `memory_search`, `memory_get`                                                                                           |
| `group:web`        | `web_search`, `x_search`, `web_fetch`                                                                                   |
| `group:ui`         | `browser`, `canvas`                                                                                                     |
| `group:automation` | `cron`, `gateway`                                                                                                       |
| `group:messaging`  | `message`                                                                                                               |
| `group:nodes`      | `nodes`                                                                                                                 |
| `group:agents`     | `agents_list`                                                                                                           |
| `group:media`      | `image`, `image_generate`, `video_generate`, `tts`                                                                      |
| `group:openclaw`   | すべての組み込み tools（provider plugins を除く）                                                                       |

### `tools.allow` / `tools.deny`

グローバルな tool 許可/拒否ポリシー（deny が優先）。大文字小文字を区別せず、`*` ワイルドカードをサポートします。Docker sandbox がオフでも適用されます。

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

特定の provider または model 向けに、tool をさらに制限します。順序: base profile → provider profile → allow/deny。

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
- `/elevated on|off|ask|full` は状態を session ごとに保存します。インライン directive は単一メッセージにのみ適用されます。
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

tool-loop の安全チェックは**デフォルトで無効**です。有効化するには `enabled: true` を設定します。
設定はグローバルの `tools.loopDetection` で定義でき、agent ごとに `agents.list[].tools.loopDetection` で上書きできます。

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
- `warningThreshold`: 警告を出す no-progress 繰り返しパターンの閾値。
- `criticalThreshold`: 重大な loop をブロックする、より高い繰り返し閾値。
- `globalCircuitBreakerThreshold`: あらゆる no-progress 実行に対する強制停止閾値。
- `detectors.genericRepeat`: 同じ tool/同じ args の繰り返し呼び出しを警告。
- `detectors.knownPollNoProgress`: 既知の poll tools（`process.poll`、`command_status` など）の no-progress を警告/ブロック。
- `detectors.pingPong`: 交互に現れる no-progress ペアパターンを警告/ブロック。
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

<Accordion title="Media model エントリーのフィールド">

**Provider エントリー**（`type: "provider"` または省略時）:

- `provider`: API provider id（`openai`、`anthropic`、`google`/`gemini`、`groq` など）
- `model`: model id 上書き
- `profile` / `preferredProfile`: `auth-profiles.json` の profile 選択

**CLI エントリー**（`type: "cli"`）:

- `command`: 実行する executable
- `args`: テンプレート展開される args（`{{MediaPath}}`、`{{Prompt}}`、`{{MaxChars}}` などをサポート）

**共通フィールド:**

- `capabilities`: オプションのリスト（`image`、`audio`、`video`）。デフォルト: `openai`/`anthropic`/`minimax` → image、`google` → image+audio+video、`groq` → audio。
- `prompt`、`maxChars`、`maxBytes`、`timeoutSeconds`、`language`: エントリーごとの上書き。
- 失敗時は次のエントリーにフォールバックします。

Provider auth は標準順序に従います: `auth-profiles.json` → env vars → `models.providers.*.apiKey`。

**Async completion フィールド:**

- `asyncCompletion.directSend`: `true` の場合、完了した async `music_generate`
  および `video_generate` タスクは、まずチャネルへ直接配信を試みます。デフォルト: `false`
  （旧 requester-session wake/model-delivery path）。

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
- `tree`: 現在の session + 現在の session から spawn された session（subagents）。
- `agent`: 現在の agent id に属する任意の session（同じ agent id の下で per-sender session を実行している場合、他ユーザーを含むことがあります）。
- `all`: 任意の session。cross-agent targeting には依然として `tools.agentToAgent` が必要です。
- Sandbox clamp: 現在の session が sandboxed で、`agents.defaults.sandbox.sessionToolsVisibility="spawned"` の場合、`tools.sessions.visibility="all"` であっても visibility は `tree` に強制されます。

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

- 添付ファイルは `runtime: "subagent"` の場合のみサポートされます。ACP runtime は拒否します。
- ファイルは child workspace の `.openclaw/attachments/<uuid>/` に `.manifest.json` とともに materialize されます。
- 添付ファイル内容は transcript persistence から自動的に redaction されます。
- Base64 入力は、厳密な alphabet/padding チェックとデコード前サイズガードにより検証されます。
- ファイル権限はディレクトリが `0700`、ファイルが `0600` です。
- Cleanup は `cleanup` ポリシーに従います: `delete` は常に添付ファイルを削除し、`keep` は `retainOnSessionKeep: true` の場合にのみ保持します。

### `tools.experimental`

実験的な組み込み tool フラグ。runtime 固有の自動有効化ルールが適用されない限り、デフォルトはオフです。

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

- `planTool`: 構造化された `update_plan` ツールを有効にし、些細でない複数ステップ作業の追跡に使います。
- デフォルト: 非 OpenAI provider では `false`。OpenAI および OpenAI Codex 実行では自動的に有効になります。
- 有効な場合、system prompt にも使用ガイダンスが追加され、モデルは substantial work に対してのみこれを使用し、`in_progress` のステップを最大 1 つに保つようになります。

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

- `model`: spawn される sub-agent 向けのデフォルト model。省略時は、sub-agent は呼び出し元の model を継承します。
- `allowAgents`: 要求元 agent が独自の `subagents.allowAgents` を設定していない場合の、`sessions_spawn` 向けデフォルト target agent id 許可リスト（`["*"]` = 任意。デフォルト: 同じ agent のみ）。
- `runTimeoutSeconds`: `sessions_spawn` が `runTimeoutSeconds` を省略した場合のデフォルト timeout（秒）。`0` は timeout なし。
- subagent ごとの tool ポリシー: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`。

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

- カスタム認証が必要な場合は `authHeader: true` + `headers` を使用します。
- agent config root は `OPENCLAW_AGENT_DIR`（または旧環境変数 alias の `PI_CODING_AGENT_DIR`）で上書きできます。
- 一致する provider ID に対するマージ優先順位:
  - 空でない agent `models.json` の `baseUrl` が優先されます。
  - 空でない agent `apiKey` は、その provider が現在の config/auth-profile コンテキストで SecretRef 管理されていない場合にのみ優先されます。
  - SecretRef 管理された provider `apiKey` 値は、解決済みシークレットを永続化する代わりに source marker（env ref では `ENV_VAR_NAME`、file/exec ref では `secretref-managed`）から再更新されます。
  - SecretRef 管理された provider header 値は、source marker（env ref では `secretref-env:ENV_VAR_NAME`、file/exec ref では `secretref-managed`）から再更新されます。
  - 空または欠落した agent `apiKey`/`baseUrl` は、config の `models.providers` にフォールバックします。
  - 一致する model の `contextWindow`/`maxTokens` には、明示的 config と暗黙 catalog 値の高い方が使われます。
  - 一致する model の `contextTokens` は、存在する場合は明示的ランタイム cap を保持します。ネイティブ model metadata を変えずに実効 context を制限したい場合に使用してください。
  - config により `models.json` を完全に書き換えたい場合は `models.mode: "replace"` を使用します。
  - marker persistence は source-authoritative です: marker は解決済みランタイムシークレット値からではなく、アクティブな source config snapshot（解決前）から書き込まれます。

### Provider フィールドの詳細

- `models.mode`: provider catalog の動作（`merge` または `replace`）。
- `models.providers`: provider id をキーとするカスタム provider マップ。
- `models.providers.*.api`: リクエストアダプター（`openai-completions`、`openai-responses`、`anthropic-messages`、`google-generative-ai` など）。
- `models.providers.*.apiKey`: provider credential（SecretRef/env substitution を推奨）。
- `models.providers.*.auth`: auth 戦略（`api-key`、`token`、`oauth`、`aws-sdk`）。
- `models.providers.*.injectNumCtxForOpenAICompat`: Ollama + `openai-completions` 用に、リクエストへ `options.num_ctx` を注入します（デフォルト: `true`）。
- `models.providers.*.authHeader`: 必要な場合に `Authorization` header で credential を送るよう強制します。
- `models.providers.*.baseUrl`: 上流 API の base URL。
- `models.providers.*.headers`: proxy/tenant routing 用の追加 static header。
- `models.providers.*.request`: model-provider HTTP request の transport 上書き。
  - `request.headers`: 追加 header（provider デフォルトとマージ）。値は SecretRef を受け付けます。
  - `request.auth`: auth 戦略の上書き。モード: `"provider-default"`（provider 組み込み auth を使用）、`"authorization-bearer"`（`token` を使用）、`"header"`（`headerName`、`value`、オプションの `prefix` を使用）。
  - `request.proxy`: HTTP proxy の上書き。モード: `"env-proxy"`（`HTTP_PROXY`/`HTTPS_PROXY` 環境変数を使用）、`"explicit-proxy"`（`url` を使用）。両モードともオプションの `tls` サブオブジェクトを受け付けます。
  - `request.tls`: direct connection 向けの TLS 上書き。フィールド: `ca`、`cert`、`key`、`passphrase`（すべて SecretRef を受け付けます）、`serverName`、`insecureSkipVerify`。
- `models.providers.*.models`: 明示的な provider model catalog エントリー。
- `models.providers.*.models.*.contextWindow`: ネイティブ model の context window metadata。
- `models.providers.*.models.*.contextTokens`: オプションの runtime context cap。model 本来の `contextWindow` より小さい実効 context budget を使いたい場合に使用します。
- `models.providers.*.models.*.compat.supportsDeveloperRole`: オプションの互換性ヒント。`api: "openai-completions"` で空でない非ネイティブ `baseUrl`（host が `api.openai.com` ではない）を使用している場合、OpenClaw は実行時にこれを `false` へ強制します。`baseUrl` が空/省略なら OpenAI のデフォルト動作を維持します。
- `plugins.entries.amazon-bedrock.config.discovery`: Bedrock 自動 discovery 設定のルート。
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: 暗黙 discovery のオン/オフ。
- `plugins.entries.amazon-bedrock.config.discovery.region`: discovery 用の AWS region。
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: 対象を絞った discovery 向けのオプション provider-id filter。
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: discovery refresh の polling interval。
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: discovery された model 用のフォールバック context window。
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: discovery された model 用のフォールバック max output tokens。

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

Cerebras には `cerebras/zai-glm-4.7` を、Z.AI direct には `zai/glm-4.7` を使用します。

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

`ZAI_API_KEY` を設定してください。`z.ai/*` と `z-ai/*` は受け付けられる alias です。ショートカット: `openclaw onboard --auth-choice zai-api-key`。

- 一般 endpoint: `https://api.z.ai/api/paas/v4`
- Coding endpoint（デフォルト）: `https://api.z.ai/api/coding/paas/v4`
- 一般 endpoint には、base URL 上書き付きのカスタム provider を定義してください。

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

China endpoint には `baseUrl: "https://api.moonshot.cn/v1"` または `openclaw onboard --auth-choice moonshot-api-key-cn` を使用してください。

ネイティブ Moonshot endpoint は、共有の `openai-completions` transport で streaming usage compatibility を広告しており、OpenClaw は現在これを組み込み provider id のみに依存せず endpoint capability に基づいて判定します。

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

Anthropic 互換の組み込み provider。ショートカット: `openclaw onboard --auth-choice kimi-code-api-key`。

</Accordion>

<Accordion title="Synthetic（Anthropic-compatible）">

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
Anthropic 互換 streaming path では、thinking を明示設定しない限り OpenClaw は MiniMax thinking をデフォルトで無効化します。`/fast on` または `params.fastMode: true` は `MiniMax-M2.7` を `MiniMax-M2.7-highspeed` に書き換えます。

</Accordion>

<Accordion title="ローカル model（LM Studio）">

[Local Models](/ja-JP/gateway/local-models) を参照してください。要点: 本格的なハードウェア上の LM Studio Responses API で大きなローカル model を実行し、フォールバック用にはホスト型 model をマージしたままにしてください。

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

- `allowBundled`: bundled skills のみを対象とするオプション許可リスト（managed/workspace skills には影響しません）。
- `load.extraDirs`: 追加の共有 skill root（最も低い優先順位）。
- `install.preferBrew`: true の場合、`brew` が利用可能なら他の installer 種類にフォールバックする前に Homebrew installer を優先します。
- `install.nodeManager`: `metadata.openclaw.install` spec 向けの node installer 優先設定（`npm` | `pnpm` | `yarn` | `bun`）。
- `entries.<skillKey>.enabled: false` は、その skill が bundled/installed されていても無効化します。
- `entries.<skillKey>.apiKey`: primary env var を宣言する skill 向けの簡易 API key フィールド（skill がサポートしている場合）。

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
- discovery はネイティブ OpenClaw plugins と互換性のある Codex bundle および Claude bundle を受け付け、manifest なしの Claude default-layout bundle も含まれます。
- **設定変更には Gateway の再起動が必要です。**
- `allow`: オプションの許可リスト（列挙された plugin のみ読み込み）。`deny` が優先されます。
- `plugins.entries.<id>.apiKey`: plugin レベルの API key 簡易フィールド（plugin がサポートする場合）。
- `plugins.entries.<id>.env`: plugin スコープの env var マップ。
- `plugins.entries.<id>.hooks.allowPromptInjection`: `false` の場合、core は `before_prompt_build` をブロックし、旧 `before_agent_start` からの prompt 変更フィールドを無視します。ただし旧 `modelOverride` と `providerOverride` は保持します。ネイティブ plugin hook と、サポートされる bundle 提供 hook directory に適用されます。
- `plugins.entries.<id>.subagent.allowModelOverride`: この plugin が background subagent 実行に対して per-run の `provider` と `model` 上書きを要求することを明示的に信頼します。
- `plugins.entries.<id>.subagent.allowedModels`: 信頼済み subagent 上書き向けの、正規 `provider/model` target のオプション許可リスト。意図的に任意の model を許可したい場合にのみ `"*"` を使用してください。
- `plugins.entries.<id>.config`: plugin 定義の config object（利用可能な場合、ネイティブ OpenClaw plugin schema で検証）。
- `plugins.entries.firecrawl.config.webFetch`: Firecrawl web-fetch provider 設定。
  - `apiKey`: Firecrawl API key（SecretRef を受け付けます）。`plugins.entries.firecrawl.config.webSearch.apiKey`、旧 `tools.web.fetch.firecrawl.apiKey`、または `FIRECRAWL_API_KEY` env var にフォールバックします。
  - `baseUrl`: Firecrawl API base URL（デフォルト: `https://api.firecrawl.dev`）。
  - `onlyMainContent`: ページから主要コンテンツのみを抽出（デフォルト: `true`）。
  - `maxAgeMs`: キャッシュの最大経過時間（ミリ秒）（デフォルト: `172800000` / 2 日）。
  - `timeoutSeconds`: scrape request timeout（秒）（デフォルト: `60`）。
- `plugins.entries.xai.config.xSearch`: xAI X Search（Grok web search）設定。
  - `enabled`: X Search provider を有効化。
  - `model`: 検索に使用する Grok model（例: `"grok-4-1-fast"`）。
- `plugins.entries.memory-core.config.dreaming`: memory dreaming（experimental）設定。フェーズと閾値は [Dreaming](/concepts/dreaming) を参照してください。
  - `enabled`: dreaming のマスタースイッチ（デフォルト `false`）。
  - `frequency`: 各完全 dreaming sweep の cron cadence（デフォルト `"0 3 * * *"`）。
  - phase policy と threshold は実装詳細であり（ユーザー向け config key ではありません）。
- 有効な Claude bundle plugin は、`settings.json` から埋め込み Pi デフォルトも提供できます。OpenClaw はこれらを raw OpenClaw config patch ではなく、sanitize 済み agent setting として適用します。
-