---
read_when:
    - 正確なフィールドレベルの設定セマンティクスまたはデフォルト値が必要です
    - channel、model、gateway、または tool の設定ブロックを検証しています
summary: コア OpenClaw のキー、デフォルト値、および各サブシステム専用リファレンスへのリンクのための Gateway 設定リファレンス
title: 設定リファレンス
x-i18n:
    generated_at: "2026-04-15T19:41:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2bdb0f3e56e4a4d767fb4d6150526ae9b3926ef5b213b458001f41d02762436d
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# 設定リファレンス

`~/.openclaw/openclaw.json` のコア設定リファレンスです。タスク指向の概要については、[Configuration](/ja-JP/gateway/configuration) を参照してください。

このページでは、主要な OpenClaw の設定サーフェスを扱い、サブシステムごとにより詳細な専用リファレンスがある場合はそちらへリンクします。このページでは、すべての channel/plugin 所有のコマンドカタログや、メモリ/QMD の詳細なノブを 1 ページにすべてインライン展開することは**意図していません**。

コード上の真実:

- `openclaw config schema` は、検証と Control UI に使われるライブ JSON Schema を出力し、利用可能な場合は bundled/plugin/channel のメタデータもマージされます
- `config.schema.lookup` は、ドリルダウン用ツールのために、1 つのパスにスコープされたスキーマノードを返します
- `pnpm config:docs:check` / `pnpm config:docs:gen` は、設定ドキュメントのベースラインハッシュを現在のスキーマサーフェスに対して検証します

専用の詳細リファレンス:

- `agents.defaults.memorySearch.*`、`memory.qmd.*`、`memory.citations`、および `plugins.entries.memory-core.config.dreaming` 配下の dreaming 設定については [メモリ設定リファレンス](/ja-JP/reference/memory-config)
- 現在の組み込み + bundled コマンドカタログについては [スラッシュコマンド](/ja-JP/tools/slash-commands)
- channel 固有のコマンドサーフェスについては各 channel/plugin ページ

設定形式は **JSON5** です（コメントと末尾カンマを許可）。すべてのフィールドは省略可能です。省略された場合、OpenClaw は安全なデフォルト値を使用します。

---

## Channels

各 channel は、その設定セクションが存在すると自動的に起動します（`enabled: false` の場合を除く）。

### DM とグループアクセス

すべての channel は DM ポリシーとグループポリシーをサポートします:

| DM ポリシー          | 動作                                                            |
| -------------------- | --------------------------------------------------------------- |
| `pairing` (デフォルト) | 未知の送信者には 1 回限りのペアリングコードが送られ、owner の承認が必要 |
| `allowlist`          | `allowFrom` 内の送信者のみ（またはペア済みの許可ストア）             |
| `open`               | すべての受信 DM を許可（`allowFrom: ["*"]` が必要）                  |
| `disabled`           | すべての受信 DM を無視                                          |

| グループポリシー         | 動作                                                   |
| ------------------------ | ------------------------------------------------------ |
| `allowlist` (デフォルト) | 設定された許可リストに一致するグループのみ               |
| `open`                   | グループ許可リストをバイパス（mention-gating は引き続き適用） |
| `disabled`               | すべてのグループ/ルームメッセージをブロック              |

<Note>
`channels.defaults.groupPolicy` は、provider の `groupPolicy` が未設定のときのデフォルト値を設定します。
ペアリングコードは 1 時間後に期限切れになります。保留中の DM ペアリングリクエストは **channel ごとに 3 件**までです。
provider ブロック自体が完全に欠けている場合（`channels.<provider>` がない場合）、ランタイムのグループポリシーは起動時警告とともに `allowlist`（フェイルクローズ）へフォールバックします。
</Note>

### Channel モデルのオーバーライド

特定の channel ID をモデルに固定するには `channels.modelByChannel` を使います。値には `provider/model` または設定済みのモデルエイリアスを指定できます。channel マッピングは、セッションにすでにモデルオーバーライドが存在しない場合に適用されます（たとえば `/model` で設定された場合など）。

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

### Channel のデフォルト設定と Heartbeat

provider 間で共有するグループポリシーと Heartbeat の動作には `channels.defaults` を使います:

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

- `channels.defaults.groupPolicy`: provider レベルの `groupPolicy` が未設定のときのフォールバックグループポリシー。
- `channels.defaults.contextVisibility`: すべての channel に対する補足コンテキスト可視性モードのデフォルト値。値: `all`（デフォルト。引用/スレッド/履歴のすべてのコンテキストを含める）、`allowlist`（許可リストにある送信者からのコンテキストのみ含める）、`allowlist_quote`（`allowlist` と同じだが、明示的な引用/返信コンテキストは保持する）。channel ごとのオーバーライド: `channels.<channel>.contextVisibility`。
- `channels.defaults.heartbeat.showOk`: 正常な channel ステータスを Heartbeat 出力に含めます。
- `channels.defaults.heartbeat.showAlerts`: 劣化/エラー状態のステータスを Heartbeat 出力に含めます。
- `channels.defaults.heartbeat.useIndicator`: コンパクトなインジケータ形式の Heartbeat 出力を描画します。

### WhatsApp

WhatsApp は Gateway の web channel（Baileys Web）経由で動作します。リンク済みセッションが存在すると自動的に起動します。

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

- 送信コマンドは、`default` アカウントが存在する場合はそれを、存在しない場合は最初に設定されたアカウント ID（ソート順）をデフォルトにします。
- 任意の `channels.whatsapp.defaultAccount` は、設定済みアカウント ID と一致する場合に、このフォールバックのデフォルトアカウント選択を上書きします。
- 従来の単一アカウント Baileys auth dir は、`openclaw doctor` によって `whatsapp/default` へ移行されます。
- アカウントごとのオーバーライド: `channels.whatsapp.accounts.<id>.sendReadReceipts`、`channels.whatsapp.accounts.<id>.dmPolicy`、`channels.whatsapp.accounts.<id>.allowFrom`。

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

- Bot トークン: `channels.telegram.botToken` または `channels.telegram.tokenFile`（通常ファイルのみ。symlink は拒否されます）。デフォルトアカウントには `TELEGRAM_BOT_TOKEN` もフォールバックとして使えます。
- 任意の `channels.telegram.defaultAccount` は、設定済みアカウント ID と一致する場合にデフォルトアカウント選択を上書きします。
- マルチアカウント構成（2 個以上のアカウント ID）では、フォールバックルーティングを避けるために明示的なデフォルト（`channels.telegram.defaultAccount` または `channels.telegram.accounts.default`）を設定してください。これがない、または無効な場合、`openclaw doctor` が警告します。
- `configWrites: false` は、Telegram 起点の設定書き込み（supergroup ID の移行、`/config set|unset`）をブロックします。
- `type: "acp"` を持つトップレベルの `bindings[]` エントリは、フォーラムトピック用の永続 ACP バインディングを設定します（`match.peer.id` には正規の `chatId:topic:topicId` を使用）。フィールドのセマンティクスは [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings) と共通です。
- Telegram のストリームプレビューは `sendMessage` + `editMessageText` を使います（ダイレクトチャットとグループチャットの両方で動作）。
- retry ポリシー: [Retry policy](/ja-JP/concepts/retry) を参照してください。

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

- トークン: `channels.discord.token`。デフォルトアカウントでは `DISCORD_BOT_TOKEN` もフォールバックとして使えます。
- 明示的な Discord `token` を指定する直接の送信呼び出しでは、その呼び出しにそのトークンが使われます。アカウントの retry/ポリシー設定は、引き続きアクティブなランタイムスナップショット内で選択されたアカウントから取得されます。
- 任意の `channels.discord.defaultAccount` は、設定済みアカウント ID と一致する場合にデフォルトアカウント選択を上書きします。
- 配信ターゲットには `user:<id>`（DM）または `channel:<id>`（guild channel）を使用します。数値 ID 単体は拒否されます。
- Guild slug は小文字で、スペースは `-` に置き換えられます。channel キーには slug 化された名前（`#` なし）を使います。guild ID の使用を推奨します。
- bot 自身が作成したメッセージはデフォルトで無視されます。`allowBots: true` で有効になります。bot をメンションした bot メッセージだけを受け付けるには `allowBots: "mentions"` を使ってください（自分自身のメッセージは引き続きフィルタされます）。
- `channels.discord.guilds.<id>.ignoreOtherMentions`（および channel オーバーライド）は、別のユーザーまたはロールにはメンションしているが bot にはメンションしていないメッセージを破棄します（@everyone/@here は除く）。
- `maxLinesPerMessage`（デフォルト 17）は、2000 文字未満でも行数の多いメッセージを分割します。
- `channels.discord.threadBindings` は Discord のスレッドバインド型ルーティングを制御します:
  - `enabled`: スレッドバインドセッション機能（`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`、およびバインド配信/ルーティング）に対する Discord オーバーライド
  - `idleHours`: 非アクティブ時の自動 unfocus を時間単位で指定する Discord オーバーライド（`0` で無効）
  - `maxAgeHours`: ハード最大経過時間を時間単位で指定する Discord オーバーライド（`0` で無効）
  - `spawnSubagentSessions`: `sessions_spawn({ thread: true })` の自動スレッド作成/バインドを有効にするオプトインスイッチ
- `type: "acp"` を持つトップレベルの `bindings[]` エントリは、channel とスレッド用の永続 ACP バインディングを設定します（`match.peer.id` には channel/thread id を使用）。フィールドのセマンティクスは [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings) と共通です。
- `channels.discord.ui.components.accentColor` は、Discord components v2 コンテナのアクセントカラーを設定します。
- `channels.discord.voice` は、Discord 音声 channel での会話と、任意の自動参加 + TTS オーバーライドを有効にします。
- `channels.discord.voice.daveEncryption` と `channels.discord.voice.decryptionFailureTolerance` は、`@discordjs/voice` の DAVE オプションにそのまま渡されます（デフォルトは `true` と `24`）。
- さらに OpenClaw は、復号失敗が繰り返された後に音声セッションを離脱/再参加することで、音声受信の回復も試みます。
- `channels.discord.streaming` は正規のストリームモードキーです。従来の `streamMode` と boolean の `streaming` 値は自動移行されます。
- `channels.discord.autoPresence` は、ランタイム可用性を bot の presence にマッピングします（healthy => online、degraded => idle、exhausted => dnd）。任意のステータステキスト上書きも可能です。
- `channels.discord.dangerouslyAllowNameMatching` は、変更可能な name/tag マッチングを再有効化します（非常時用の互換モード）。
- `channels.discord.execApprovals`: Discord ネイティブの exec 承認配信と承認者認可。
  - `enabled`: `true`、`false`、または `"auto"`（デフォルト）。auto モードでは、`approvers` または `commands.ownerAllowFrom` から承認者を解決できる場合に exec 承認が有効化されます。
  - `approvers`: exec リクエストを承認できる Discord ユーザー ID。省略時は `commands.ownerAllowFrom` にフォールバックします。
  - `agentFilter`: 任意の agent ID 許可リスト。省略するとすべての agent の承認を転送します。
  - `sessionFilter`: 任意のセッションキーパターン（部分文字列または regex）。
  - `target`: 承認プロンプトの送信先。`"dm"`（デフォルト）は承認者 DM に送信し、`"channel"` は元の channel に送信し、`"both"` は両方に送信します。target に `"channel"` が含まれる場合、ボタンを使用できるのは解決済み承認者のみです。
  - `cleanupAfterResolve`: `true` の場合、承認、拒否、またはタイムアウト後に承認 DM を削除します。

**リアクション通知モード:** `off`（なし）、`own`（bot のメッセージ、デフォルト）、`all`（すべてのメッセージ）、`allowlist`（すべてのメッセージに対して `guilds.<id>.users` から）。

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
- `channels.googlechat.dangerouslyAllowNameMatching` は、変更可能なメール principal マッチングを再有効化します（非常時用の互換モード）。

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
      streaming: {
        mode: "partial", // off | partial | block | progress
        nativeTransport: true, // use Slack native streaming API when mode=partial
      },
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
- Slack アカウントスナップショットは、`botTokenSource`、`botTokenStatus`、`appTokenStatus`、HTTP mode では `signingSecretStatus` など、認証情報ごとの source/status フィールドを公開します。`configured_unavailable` は、そのアカウントが SecretRef 経由で設定されているが、現在のコマンド/ランタイム経路では secret 値を解決できなかったことを意味します。
- `configWrites: false` は、Slack 起点の設定書き込みをブロックします。
- 任意の `channels.slack.defaultAccount` は、設定済みアカウント ID と一致する場合にデフォルトアカウント選択を上書きします。
- `channels.slack.streaming.mode` は正規の Slack ストリームモードキーです。`channels.slack.streaming.nativeTransport` は Slack のネイティブストリーミング転送を制御します。従来の `streamMode`、boolean の `streaming`、`nativeStreaming` の値は自動移行されます。
- 配信ターゲットには `user:<id>`（DM）または `channel:<id>` を使用します。

**リアクション通知モード:** `off`、`own`（デフォルト）、`all`、`allowlist`（`reactionAllowlist` から）。

**スレッドセッション分離:** `thread.historyScope` はスレッド単位（デフォルト）または channel 共有です。`thread.inheritParent` は親 channel のトランスクリプトを新しいスレッドにコピーします。

- Slack ネイティブストリーミングと、Slack の assistant スタイル「is typing...」スレッドステータスには、返信スレッドターゲットが必要です。トップレベル DM はデフォルトでスレッド外のままなので、スレッドスタイルのプレビューではなく `typingReaction` または通常配信を使います。
- `typingReaction` は、返信の実行中に受信した Slack メッセージへ一時的なリアクションを追加し、完了時に削除します。`"hourglass_flowing_sand"` のような Slack 絵文字 shortcode を使用してください。
- `channels.slack.execApprovals`: Slack ネイティブの exec 承認配信と承認者認可。スキーマは Discord と同じです: `enabled`（`true`/`false`/`"auto"`）、`approvers`（Slack ユーザー ID）、`agentFilter`、`sessionFilter`、`target`（`"dm"`、`"channel"`、または `"both"`）。

| アクショングループ | デフォルト | 備考                     |
| ------------------ | ---------- | ------------------------ |
| reactions          | enabled    | リアクト + リアクション一覧 |
| messages           | enabled    | 読み取り/送信/編集/削除     |
| pins               | enabled    | ピン留め/解除/一覧         |
| memberInfo         | enabled    | メンバー情報               |
| emojiList          | enabled    | カスタム絵文字一覧         |

### Mattermost

Mattermost は Plugin として提供されます: `openclaw plugins install @openclaw/mattermost`。

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

チャットモード: `oncall`（@-mention 時に応答、デフォルト）、`onmessage`（すべてのメッセージ）、`onchar`（トリガープレフィックスで始まるメッセージ）。

Mattermost ネイティブコマンドが有効な場合:

- `commands.callbackPath` はフル URL ではなくパスである必要があります（例: `/api/channels/mattermost/command`）。
- `commands.callbackUrl` は OpenClaw Gateway エンドポイントを指し、Mattermost サーバーから到達可能である必要があります。
- ネイティブスラッシュコールバックは、スラッシュコマンド登録時に Mattermost が返すコマンド単位のトークンで認証されます。登録に失敗した場合、または有効化されたコマンドがない場合、OpenClaw はコールバックを `Unauthorized: invalid command token.` で拒否します。
- 非公開/tailnet/internal のコールバックホストでは、Mattermost 側で `ServiceSettings.AllowedUntrustedInternalConnections` にコールバックホスト/ドメインを含める必要がある場合があります。フル URL ではなく、ホスト/ドメイン値を使用してください。
- `channels.mattermost.configWrites`: Mattermost 起点の設定書き込みを許可または拒否します。
- `channels.mattermost.requireMention`: channel で返信する前に `@mention` を必須にします。
- `channels.mattermost.groups.<channelId>.requireMention`: channel ごとの mention-gating オーバーライド（デフォルトは `"*"`）。
- 任意の `channels.mattermost.defaultAccount` は、設定済みアカウント ID と一致する場合にデフォルトアカウント選択を上書きします。

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

- `channels.signal.account`: channel の起動先を特定の Signal アカウント ID に固定します。
- `channels.signal.configWrites`: Signal 起点の設定書き込みを許可または拒否します。
- 任意の `channels.signal.defaultAccount` は、設定済みアカウント ID と一致する場合にデフォルトアカウント選択を上書きします。

### BlueBubbles

BlueBubbles は推奨される iMessage 経路です（Plugin バック、`channels.bluebubbles` 配下で設定）。

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

- ここで扱うコアのキーパス: `channels.bluebubbles`、`channels.bluebubbles.dmPolicy`。
- 任意の `channels.bluebubbles.defaultAccount` は、設定済みアカウント ID と一致する場合にデフォルトアカウント選択を上書きします。
- `type: "acp"` を持つトップレベルの `bindings[]` エントリは、BlueBubbles の会話を永続 ACP セッションにバインドできます。`match.peer.id` には BlueBubbles の handle またはターゲット文字列（`chat_id:*`、`chat_guid:*`、`chat_identifier:*`）を使用します。共通フィールドセマンティクス: [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings)。
- 完全な BlueBubbles channel 設定は [BlueBubbles](/ja-JP/channels/bluebubbles) に記載されています。

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

- 任意の `channels.imessage.defaultAccount` は、設定済みアカウント ID と一致する場合にデフォルトアカウント選択を上書きします。

- Messages DB へのフルディスクアクセスが必要です。
- `chat_id:<id>` ターゲットの使用を推奨します。チャット一覧は `imsg chats --limit 20` で取得できます。
- `cliPath` は SSH ラッパーを指すこともできます。SCP で添付ファイルを取得するには `remoteHost`（`host` または `user@host`）を設定してください。
- `attachmentRoots` と `remoteAttachmentRoots` は受信添付ファイルのパスを制限します（デフォルト: `/Users/*/Library/Messages/Attachments`）。
- SCP は厳格なホストキー検証を使うため、リレーホストのキーがすでに `~/.ssh/known_hosts` に存在している必要があります。
- `channels.imessage.configWrites`: iMessage 起点の設定書き込みを許可または拒否します。
- `type: "acp"` を持つトップレベルの `bindings[]` エントリは、iMessage の会話を永続 ACP セッションにバインドできます。`match.peer.id` には正規化済み handle または明示的な chat ターゲット（`chat_id:*`、`chat_guid:*`、`chat_identifier:*`）を使用します。共通フィールドセマンティクス: [ACP Agents](/ja-JP/tools/acp-agents#channel-specific-settings)。

<Accordion title="iMessage SSH ラッパーの例">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix は extension バックで、`channels.matrix` 配下で設定します。

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
- `channels.matrix.proxy` は Matrix HTTP トラフィックを明示的な HTTP(S) proxy 経由にします。名前付きアカウントは `channels.matrix.accounts.<id>.proxy` で上書きできます。
- `channels.matrix.network.dangerouslyAllowPrivateNetwork` は private/internal な homeserver を許可します。`proxy` とこのネットワーク opt-in は独立した制御です。
- `channels.matrix.defaultAccount` は、マルチアカウント構成で優先アカウントを選択します。
- `channels.matrix.autoJoin` のデフォルトは `off` なので、招待された room や新しい DM スタイルの招待は、`autoJoin: "allowlist"` と `autoJoinAllowlist` を設定するか、`autoJoin: "always"` を設定するまで無視されます。
- `channels.matrix.execApprovals`: Matrix ネイティブの exec 承認配信と承認者認可。
  - `enabled`: `true`、`false`、または `"auto"`（デフォルト）。auto モードでは、`approvers` または `commands.ownerAllowFrom` から承認者を解決できる場合に exec 承認が有効化されます。
  - `approvers`: exec リクエストを承認できる Matrix ユーザー ID（例: `@owner:example.org`）。
  - `agentFilter`: 任意の agent ID 許可リスト。省略するとすべての agent の承認を転送します。
  - `sessionFilter`: 任意のセッションキーパターン（部分文字列または regex）。
  - `target`: 承認プロンプトの送信先。`"dm"`（デフォルト）、`"channel"`（発信元 room）、または `"both"`。
  - アカウントごとのオーバーライド: `channels.matrix.accounts.<id>.execApprovals`。
- `channels.matrix.dm.sessionScope` は、Matrix DM をどのようにセッションへグループ化するかを制御します: `per-user`（デフォルト）はルーティングされた peer 単位で共有し、`per-room` は各 DM room を分離します。
- Matrix のステータス probe とライブディレクトリ参照は、ランタイムトラフィックと同じ proxy ポリシーを使います。
- 完全な Matrix 設定、ターゲティングルール、セットアップ例は [Matrix](/ja-JP/channels/matrix) に記載されています。

### Microsoft Teams

Microsoft Teams は extension バックで、`channels.msteams` 配下で設定します。

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

- ここで扱うコアのキーパス: `channels.msteams`、`channels.msteams.configWrites`。
- 完全な Teams 設定（資格情報、webhook、DM/グループポリシー、team/channel ごとのオーバーライド）は [Microsoft Teams](/ja-JP/channels/msteams) に記載されています。

### IRC

IRC は extension バックで、`channels.irc` 配下で設定します。

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

- ここで扱うコアのキーパス: `channels.irc`、`channels.irc.dmPolicy`、`channels.irc.configWrites`、`channels.irc.nickserv.*`。
- 任意の `channels.irc.defaultAccount` は、設定済みアカウント ID と一致する場合にデフォルトアカウント選択を上書きします。
- 完全な IRC channel 設定（host/port/TLS/channels/allowlists/mention gating）は [IRC](/ja-JP/channels/irc) に記載されています。

### マルチアカウント（すべての channels）

channel ごとに複数のアカウントを実行できます（各アカウントは独自の `accountId` を持ちます）:

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

- `accountId` を省略した場合は `default` が使われます（CLI + ルーティング）。
- 環境変数トークンは **default** アカウントにのみ適用されます。
- ベース channel 設定は、アカウントごとに上書きしない限りすべてのアカウントに適用されます。
- `bindings[].match.accountId` を使うと、各アカウントを異なる agent にルーティングできます。
- 単一アカウントのトップレベル channel 設定のまま `openclaw channels add`（または channel オンボーディング）で非デフォルトアカウントを追加すると、OpenClaw はまずアカウントスコープのトップレベル単一アカウント値を channel のアカウントマップへ昇格させるため、元のアカウントはそのまま動作し続けます。ほとんどの channels ではそれらは `channels.<channel>.accounts.default` に移動されますが、Matrix では既存の一致する named/default ターゲットを代わりに保持できます。
- 既存の channel のみのバインディング（`accountId` なし）は引き続きデフォルトアカウントに一致します。アカウントスコープ付きバインディングは引き続き任意です。
- `openclaw doctor --fix` も、アカウントスコープのトップレベル単一アカウント値をその channel 用に選ばれた昇格先アカウントへ移動することで、混在した形状を修復します。ほとんどの channels では `accounts.default` が使われますが、Matrix では既存の一致する named/default ターゲットを代わりに保持できます。

### その他の extension channels

多くの extension channels は `channels.<id>` として設定され、専用の channel ページに記載されています（たとえば Feishu、Matrix、LINE、Nostr、Zalo、Nextcloud Talk、Synology Chat、Twitch）。
完全な channel 一覧は [Channels](/ja-JP/channels) を参照してください。

### グループチャットの mention gating

グループメッセージでは、デフォルトで **メンション必須** です（メタデータメンションまたは安全な regex パターン）。WhatsApp、Telegram、Discord、Google Chat、iMessage のグループチャットに適用されます。

**メンションの種類:**

- **メタデータメンション**: ネイティブプラットフォームの @-mention。WhatsApp の self-chat mode では無視されます。
- **テキストパターン**: `agents.list[].groupChat.mentionPatterns` 内の安全な regex パターン。無効なパターンや安全でないネストされた繰り返しは無視されます。
- mention gating は、検出可能な場合にのみ適用されます（ネイティブメンションまたは少なくとも 1 つのパターンがある場合）。

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

`messages.groupChat.historyLimit` はグローバルデフォルトを設定します。channels は `channels.<channel>.historyLimit`（またはアカウントごと）で上書きできます。無効にするには `0` を設定します。

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

解決順序: DM ごとのオーバーライド → provider デフォルト → 制限なし（すべて保持）。

サポート対象: `telegram`、`whatsapp`、`discord`、`slack`、`signal`、`imessage`、`msteams`。

#### self-chat mode

自分の電話番号を `allowFrom` に含めると self-chat mode が有効になります（ネイティブ @-mention は無視し、テキストパターンのみに応答します）:

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
    native: "auto", // supported の場合はネイティブコマンドを登録
    nativeSkills: "auto", // supported の場合はネイティブ skill コマンドを登録
    text: true, // チャットメッセージ内の /commands を解析
    bash: false, // ! を許可（alias: /bash）
    bashForegroundMs: 2000,
    config: false, // /config を許可
    mcp: false, // /mcp を許可
    plugins: false, // /plugins を許可
    debug: false, // /debug を許可
    restart: true, // /restart + Gateway restart tool を許可
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw", // raw | hash
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="コマンド詳細">

- このブロックはコマンドサーフェスを設定します。現在の組み込み + bundled コマンドカタログについては [スラッシュコマンド](/ja-JP/tools/slash-commands) を参照してください。
- このページは**設定キーリファレンス**であり、完全なコマンドカタログではありません。QQ Bot の `/bot-ping` `/bot-help` `/bot-logs`、LINE の `/card`、device-pair の `/pair`、memory の `/dreaming`、phone-control の `/phone`、Talk の `/voice` などの channel/plugin 所有コマンドは、それぞれの channel/plugin ページと [スラッシュコマンド](/ja-JP/tools/slash-commands) に記載されています。
- テキストコマンドは、先頭が `/` の**単独メッセージ**である必要があります。
- `native: "auto"` は Discord/Telegram でネイティブコマンドを有効にし、Slack では無効のままにします。
- `nativeSkills: "auto"` は Discord/Telegram でネイティブ Skills コマンドを有効にし、Slack では無効のままにします。
- channel ごとのオーバーライド: `channels.discord.commands.native`（bool または `"auto"`）。`false` を指定すると、以前登録されたコマンドをクリアします。
- ネイティブ skill 登録は `channels.<provider>.commands.nativeSkills` で provider ごとにオーバーライドできます。
- `channels.telegram.customCommands` は追加の Telegram bot メニュー項目を追加します。
- `bash: true` はホスト shell 用の `! <cmd>` を有効にします。`tools.elevated.enabled` と、送信者が `tools.elevated.allowFrom.<channel>` に含まれていることが必要です。
- `config: true` は `/config`（`openclaw.json` の読み書き）を有効にします。Gateway の `chat.send` クライアントでは、永続的な `/config set|unset` 書き込みには `operator.admin` も必要です。読み取り専用の `/config show` は通常の書き込みスコープを持つ operator クライアントでも引き続き使用できます。
- `mcp: true` は、`mcp.servers` 配下の OpenClaw 管理 MCP サーバー設定用の `/mcp` を有効にします。
- `plugins: true` は、Plugin の検出、インストール、有効化/無効化制御用の `/plugins` を有効にします。
- `channels.<provider>.configWrites` は channel ごとの設定変更を制御します（デフォルト: true）。
- マルチアカウント channel では、`channels.<provider>.accounts.<id>.configWrites` も、そのアカウントを対象とする書き込みを制御します（たとえば `/allowlist --config --account <id>` や `/config set channels.<provider>.accounts.<id>...`）。
- `restart: false` は `/restart` と Gateway restart tool アクションを無効にします。デフォルト: `true`。
- `ownerAllowFrom` は、owner 専用コマンド/ツール用の明示的な owner 許可リストです。`allowFrom` とは別です。
- `ownerDisplay: "hash"` は、system prompt 内の owner ID をハッシュ化します。ハッシュ化を制御するには `ownerDisplaySecret` を設定してください。
- `allowFrom` は provider ごとです。設定されている場合、これが**唯一の**認可ソースになります（channel の allowlist/pairing と `useAccessGroups` は無視されます）。
- `useAccessGroups: false` は、`allowFrom` が設定されていない場合に、コマンドが access-group ポリシーをバイパスできるようにします。
- コマンドドキュメントの対応表:
  - 組み込み + bundled カタログ: [スラッシュコマンド](/ja-JP/tools/slash-commands)
  - channel 固有のコマンドサーフェス: [Channels](/ja-JP/channels)
  - QQ Bot コマンド: [QQ Bot](/ja-JP/channels/qqbot)
  - pairing コマンド: [Pairing](/ja-JP/channels/pairing)
  - LINE card コマンド: [LINE](/ja-JP/channels/line)
  - memory dreaming: [Dreaming](/ja-JP/concepts/dreaming)

</Accordion>

---

## Agent のデフォルト設定

### `agents.defaults.workspace`

デフォルト: `~/.openclaw/workspace`。

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

system prompt の Runtime 行に表示される任意のリポジトリルートです。未設定の場合、OpenClaw は workspace から上方向にたどって自動検出します。

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

`agents.list[].skills` を設定していない agent 用の、任意のデフォルト Skills 許可リストです。

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // github, weather を継承
      { id: "docs", skills: ["docs-search"] }, // デフォルトを置き換え
      { id: "locked-down", skills: [] }, // Skills なし
    ],
  },
}
```

- デフォルトで Skills を無制限にするには `agents.defaults.skills` を省略します。
- デフォルトを継承するには `agents.list[].skills` を省略します。
- Skills なしにするには `agents.list[].skills: []` を設定します。
- 空でない `agents.list[].skills` リストは、その agent の最終セットです。デフォルトとはマージされません。

### `agents.defaults.skipBootstrap`

workspace bootstrap ファイル（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、`BOOTSTRAP.md`）の自動作成を無効にします。

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

workspace bootstrap ファイルを 언제 system prompt に注入するかを制御します。デフォルト: `"always"`。

- `"continuation-skip"`: 安全な継続ターン（assistant の応答完了後）では workspace bootstrap の再注入をスキップし、プロンプトサイズを削減します。Heartbeat 実行と Compaction 後の再試行では引き続きコンテキストが再構築されます。

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

切り詰め前の、workspace bootstrap ファイルごとの最大文字数です。デフォルト: `20000`。

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

すべての workspace bootstrap ファイルにまたがって注入される最大総文字数です。デフォルト: `150000`。

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

bootstrap コンテキストが切り詰められたときに agent に見える警告テキストを制御します。
デフォルト: `"once"`。

- `"off"`: system prompt に警告テキストを一切注入しません。
- `"once"`: 一意の切り詰めシグネチャごとに 1 回だけ警告を注入します（推奨）。
- `"always"`: 切り詰めが存在する場合、毎回の実行で警告を注入します。

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### コンテキスト予算の所有マップ

OpenClaw には大容量の prompt/context 予算が複数あり、それらは 1 つの汎用ノブにまとめず、サブシステムごとに意図的に分割されています。

- `agents.defaults.bootstrapMaxChars` /
  `agents.defaults.bootstrapTotalMaxChars`:
  通常の workspace bootstrap 注入。
- `agents.defaults.startupContext.*`:
  1 回限りの `/new` と `/reset` の起動前奏コンテキスト。最近の
  `memory/*.md` ファイルを含みます。
- `skills.limits.*`:
  system prompt に注入されるコンパクトな Skills 一覧。
- `agents.defaults.contextLimits.*`:
  制限付きランタイム抜粋と、注入されるランタイム所有ブロック。
- `memory.qmd.limits.*`:
  インデックス化された memory search スニペットと注入サイズ。

特定の agent にのみ別の予算が必要な場合に限り、対応する agent ごとのオーバーライドを使用してください:

- `agents.list[].skillsLimits.maxSkillsPromptChars`
- `agents.list[].contextLimits.*`

#### `agents.defaults.startupContext`

素の `/new` と `/reset` 実行時に注入される、最初のターンの起動前奏コンテキストを制御します。

```json5
{
  agents: {
    defaults: {
      startupContext: {
        enabled: true,
        applyOn: ["new", "reset"],
        dailyMemoryDays: 2,
        maxFileBytes: 16384,
        maxFileChars: 1200,
        maxTotalChars: 2800,
      },
    },
  },
}
```

#### `agents.defaults.contextLimits`

制限付きランタイムコンテキストサーフェスの共有デフォルトです。

```json5
{
  agents: {
    defaults: {
      contextLimits: {
        memoryGetMaxChars: 12000,
        memoryGetDefaultLines: 120,
        toolResultMaxChars: 16000,
        postCompactionMaxChars: 1800,
      },
    },
  },
}
```

- `memoryGetMaxChars`: 切り詰めメタデータと継続通知が追加される前の、デフォルトの `memory_get` 抜粋上限。
- `memoryGetDefaultLines`: `lines` を省略した場合の、デフォルトの `memory_get` 行ウィンドウ。
- `toolResultMaxChars`: 永続化される結果とオーバーフロー回復に使われる、ライブ tool result 上限。
- `postCompactionMaxChars`: Compaction 後の再注入時に使われる AGENTS.md 抜粋上限。

#### `agents.list[].contextLimits`

共有 `contextLimits` ノブの agent ごとのオーバーライドです。省略されたフィールドは `agents.defaults.contextLimits` から継承されます。

```json5
{
  agents: {
    defaults: {
      contextLimits: {
        memoryGetMaxChars: 12000,
        toolResultMaxChars: 16000,
      },
    },
    list: [
      {
        id: "tiny-local",
        contextLimits: {
          memoryGetMaxChars: 6000,
          toolResultMaxChars: 8000,
        },
      },
    ],
  },
}
```

#### `skills.limits.maxSkillsPromptChars`

system prompt に注入されるコンパクトな Skills 一覧のグローバル上限です。
これは必要に応じて `SKILL.md` ファイルを読むことには影響しません。

```json5
{
  skills: {
    limits: {
      maxSkillsPromptChars: 18000,
    },
  },
}
```

#### `agents.list[].skillsLimits.maxSkillsPromptChars`

Skills prompt 予算の agent ごとのオーバーライドです。

```json5
{
  agents: {
    list: [
      {
        id: "tiny-local",
        skillsLimits: {
          maxSkillsPromptChars: 6000,
        },
      },
    ],
  },
}
```

### `agents.defaults.imageMaxDimensionPx`

provider 呼び出し前に、transcript/tool の画像ブロックで最長辺に適用される最大ピクセルサイズです。
デフォルト: `1200`。

通常、値を小さくするとスクリーンショットの多い実行で vision token 使用量とリクエスト payload サイズが減ります。
値を大きくすると、より多くの視覚的詳細が保持されます。

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

system prompt コンテキスト用のタイムゾーンです（メッセージタイムスタンプ用ではありません）。未設定の場合はホストのタイムゾーンにフォールバックします。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

system prompt 内の時刻形式です。デフォルト: `auto`（OS の設定）。

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
      params: { cacheRetention: "long" }, // グローバルなデフォルト provider params
      embeddedHarness: {
        runtime: "auto", // auto | pi | registered harness id, e.g. codex
        fallback: "pi", // pi | none
      },
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
  - 文字列形式はプライマリモデルのみを設定します。
  - オブジェクト形式は、プライマリに加えて順序付きのフェイルオーバーモデルを設定します。
- `imageModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - `image` tool パスで、その vision-model 設定として使われます。
  - 選択された/デフォルトの model が画像入力を受け付けられない場合のフォールバックルーティングにも使われます。
- `imageGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共有の画像生成機能と、今後追加される画像生成用の tool/plugin サーフェスで使われます。
  - 代表的な値: Gemini ネイティブ画像生成用の `google/gemini-3.1-flash-image-preview`、fal 用の `fal/fal-ai/flux/dev`、または OpenAI Images 用の `openai/gpt-image-1`。
  - provider/model を直接選択する場合は、対応する provider の auth/API キーも設定してください（例: `google/*` には `GEMINI_API_KEY` または `GOOGLE_API_KEY`、`openai/*` には `OPENAI_API_KEY`、`fal/*` には `FAL_KEY`）。
  - 省略しても、`image_generate` は auth に裏付けられた provider デフォルトを推論できます。まず現在のデフォルト provider を試し、その後、残りの登録済み画像生成 provider を provider-id 順で試します。
- `musicGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共有の音楽生成機能と、組み込みの `music_generate` tool で使われます。
  - 代表的な値: `google/lyria-3-clip-preview`、`google/lyria-3-pro-preview`、または `minimax/music-2.5+`。
  - 省略しても、`music_generate` は auth に裏付けられた provider デフォルトを推論できます。まず現在のデフォルト provider を試し、その後、残りの登録済み音楽生成 provider を provider-id 順で試します。
  - provider/model を直接選択する場合は、対応する provider の auth/API キーも設定してください。
- `videoGenerationModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - 共有の動画生成機能と、組み込みの `video_generate` tool で使われます。
  - 代表的な値: `qwen/wan2.6-t2v`、`qwen/wan2.6-i2v`、`qwen/wan2.6-r2v`、`qwen/wan2.6-r2v-flash`、または `qwen/wan2.7-r2v`。
  - 省略しても、`video_generate` は auth に裏付けられた provider デフォルトを推論できます。まず現在のデフォルト provider を試し、その後、残りの登録済み動画生成 provider を provider-id 順で試します。
  - provider/model を直接選択する場合は、対応する provider の auth/API キーも設定してください。
  - bundled の Qwen 動画生成 provider は、最大 1 本の出力動画、1 枚の入力画像、4 本の入力動画、10 秒の長さ、および provider レベルの `size`、`aspectRatio`、`resolution`、`audio`、`watermark` オプションをサポートします。
- `pdfModel`: 文字列（`"provider/model"`）またはオブジェクト（`{ primary, fallbacks }`）を受け付けます。
  - `pdf` tool で model ルーティングに使われます。
  - 省略した場合、PDF tool は `imageModel` にフォールバックし、その後、解決済みのセッション/デフォルト model にフォールバックします。
- `pdfMaxBytesMb`: 呼び出し時に `maxBytesMb` が渡されない場合の、`pdf` tool のデフォルト PDF サイズ上限。
- `pdfMaxPages`: `pdf` tool の抽出フォールバックモードで考慮されるページ数のデフォルト上限。
- `verboseDefault`: agent のデフォルト verbose レベル。値: `"off"`、`"on"`、`"full"`。デフォルト: `"off"`。
- `elevatedDefault`: agent のデフォルト elevated-output レベル。値: `"off"`、`"on"`、`"ask"`、`"full"`。デフォルト: `"on"`。
- `model.primary`: 形式は `provider/model`（例: `openai/gpt-5.4`）。provider を省略すると、OpenClaw はまず alias を試し、次にその正確な model id に一致する一意の configured-provider を試し、それでもだめなら設定済みのデフォルト provider にフォールバックします（非推奨の互換挙動なので、明示的な `provider/model` を推奨します）。その provider が設定済みデフォルト model をもはや公開していない場合、OpenClaw は古くなった削除済み provider のデフォルトを出す代わりに、最初の設定済み provider/model にフォールバックします。
- `models`: `/model` 用の設定済み model カタログ兼許可リスト。各エントリには `alias`（短縮名）と `params`（provider 固有。例: `temperature`、`maxTokens`、`cacheRetention`、`context1m`）を含められます。
- `params`: すべての models に適用されるグローバルなデフォルト provider パラメータ。`agents.defaults.params` に設定します（例: `{ cacheRetention: "long" }`）。
- `params` のマージ優先順位（設定）: `agents.defaults.params`（グローバルベース）が `agents.defaults.models["provider/model"].params`（model ごと）で上書きされ、その後 `agents.list[].params`（一致する agent id）がキーごとに上書きします。詳細は [Prompt Caching](/ja-JP/reference/prompt-caching) を参照してください。
- `embeddedHarness`: デフォルトの低レベル埋め込み agent ランタイムポリシー。`runtime: "auto"` を使うと、登録済み plugin harness がサポート対象 model を引き受けられるようになり、`runtime: "pi"` で組み込み PI harness を強制し、`runtime: "codex"` のような登録済み harness id も指定できます。自動 PI フォールバックを無効にするには `fallback: "none"` を設定します。
- これらのフィールドを変更する設定ライター（たとえば `/models set`、`/models set-image`、fallback の追加/削除コマンド）は、正規のオブジェクト形式で保存し、可能な限り既存の fallback リストを保持します。
- `maxConcurrent`: セッションをまたいで並列実行できる agent run の最大数です（各セッション自体は引き続き直列化されます）。デフォルト: 4。

### `agents.defaults.embeddedHarness`

`embeddedHarness` は、埋め込み agent ターンをどの低レベル executor で実行するかを制御します。
ほとんどの環境では、デフォルトの `{ runtime: "auto", fallback: "pi" }` のままで構いません。
bundled の Codex app-server harness のように、信頼できる plugin がネイティブ harness を提供する場合に使ってください。

```json5
{
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

- `runtime`: `"auto"`、`"pi"`、または登録済み plugin harness id。bundled の Codex Plugin は `codex` を登録します。
- `fallback`: `"pi"` または `"none"`。`"pi"` は互換性用フォールバックとして組み込み PI harness を維持します。`"none"` は、plugin harness の選択が存在しない、または未対応の場合に、黙って PI を使わず失敗させます。
- 環境変数による上書き: `OPENCLAW_AGENT_RUNTIME=<id|auto|pi>` は `runtime` を上書きし、`OPENCLAW_AGENT_HARNESS_FALLBACK=none` はそのプロセスの PI フォールバックを無効にします。
- Codex 専用環境では、`model: "codex/gpt-5.4"`、`embeddedHarness.runtime: "codex"`、`embeddedHarness.fallback: "none"` を設定してください。
- これは埋め込み chat harness のみを制御します。media generation、vision、PDF、music、video、TTS は引き続きそれぞれの provider/model 設定を使います。

**組み込み alias 短縮名**（model が `agents.defaults.models` にある場合のみ適用）:

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

設定済みの alias は常にデフォルトより優先されます。

Z.AI の GLM-4.x models は、`--thinking off` を設定するか、`agents.defaults.models["zai/<model>"].params.thinking` を自分で定義しない限り、自動的に thinking mode を有効にします。
Z.AI models は、tool call ストリーミングのためにデフォルトで `tool_stream` を有効にします。無効にするには `agents.defaults.models["zai/<model>"].params.tool_stream` を `false` に設定してください。
Anthropic Claude 4.6 models は、明示的な thinking レベルが設定されていない場合、デフォルトで `adaptive` thinking を使用します。

### `agents.defaults.cliBackends`

テキスト専用のフォールバック実行用の任意の CLI バックエンドです（tool call なし）。API provider が失敗したときのバックアップとして役立ちます。

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

- CLI バックエンドはテキスト優先です。tools は常に無効です。
- `sessionArg` が設定されている場合はセッションをサポートします。
- `imageArg` がファイルパスを受け付ける場合は画像パススルーをサポートします。

### `agents.defaults.systemPromptOverride`

OpenClaw が組み立てた system prompt 全体を固定文字列で置き換えます。デフォルトレベル（`agents.defaults.systemPromptOverride`）または agent ごと（`agents.list[].systemPromptOverride`）で設定します。agent ごとの値が優先されます。空または空白のみの値は無視されます。制御された prompt 実験に役立ちます。

```json5
{
  agents: {
    defaults: {
      systemPromptOverride: "You are a helpful assistant.",
    },
  },
}
```

### `agents.defaults.heartbeat`

定期的な Heartbeat 実行です。

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m disables
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        includeSystemPromptSection: true, // default: true; false omits the Heartbeat section from the system prompt
        lightContext: false, // default: false; true keeps only HEARTBEAT.md from workspace bootstrap files
        isolatedSession: false, // default: false; true runs each heartbeat in a fresh session (no conversation history)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (default) | block
        target: "none", // default: none | options: last | whatsapp | telegram | discord | ...
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
        timeoutSeconds: 45,
      },
    },
  },
}
```

- `every`: 期間文字列（ms/s/m/h）。デフォルト: `30m`（API-key auth）または `1h`（OAuth auth）。無効にするには `0m` を設定します。
- `includeSystemPromptSection`: false の場合、system prompt から Heartbeat セクションを省略し、bootstrap コンテキストへの `HEARTBEAT.md` 注入もスキップします。デフォルト: `true`。
- `suppressToolErrorWarnings`: true の場合、Heartbeat 実行中の tool error 警告 payload を抑制します。
- `timeoutSeconds`: 中断されるまでに Heartbeat agent ターンに許可される最大秒数。未設定の場合は `agents.defaults.timeoutSeconds` を使います。
- `directPolicy`: direct/DM 配信ポリシー。`allow`（デフォルト）は direct-target 配信を許可します。`block` は direct-target 配信を抑制し、`reason=dm-blocked` を出力します。
- `lightContext`: true の場合、Heartbeat 実行は軽量 bootstrap コンテキストを使い、workspace bootstrap ファイルから `HEARTBEAT.md` のみを保持します。
- `isolatedSession`: true の場合、各 Heartbeat は以前の会話履歴がない新しいセッションで実行されます。Cron の `sessionTarget: "isolated"` と同じ分離パターンです。Heartbeat あたりの token コストを約 100K から約 2〜5K token に削減します。
- agent ごと: `agents.list[].heartbeat` を設定します。いずれかの agent が `heartbeat` を定義している場合、Heartbeat を実行するのは**その agent だけ**です。
- Heartbeat は完全な agent ターンを実行するため、間隔を短くするとより多くの token を消費します。

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        provider: "my-provider", // 登録済み Compaction provider Plugin の id（任意）
        timeoutSeconds: 900,
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "デプロイ ID、チケット ID、host:port の組み合わせを正確に保持してください。", // identifierPolicy=custom のときに使用
        postCompactionSections: ["Session Startup", "Red Lines"], // [] で再注入を無効化
        model: "openrouter/anthropic/claude-sonnet-4-6", // Compaction 専用の model オーバーライド（任意）
        notifyUser: true, // Compaction 開始時に簡単な通知を送信（デフォルト: false）
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "セッションはまもなく Compaction に入ります。永続的な記憶を今すぐ保存してください。",
          prompt: "持続的に残すべきメモがあれば memory/YYYY-MM-DD.md に書き込んでください。保存するものがなければ、正確なサイレントトークン NO_REPLY で応答してください。",
        },
      },
    },
  },
}
```

- `mode`: `default` または `safeguard`（長い履歴向けのチャンク化された要約）。[Compaction](/ja-JP/concepts/compaction) を参照してください。
- `provider`: 登録済みの Compaction provider Plugin の id。設定すると、組み込み LLM 要約の代わりに、その provider の `summarize()` が呼び出されます。失敗時は組み込み方式にフォールバックします。provider を設定すると `mode: "safeguard"` が強制されます。[Compaction](/ja-JP/concepts/compaction) を参照してください。
- `timeoutSeconds`: OpenClaw が中断するまでに、1 回の Compaction 操作に許可される最大秒数。デフォルト: `900`。
- `identifierPolicy`: `strict`（デフォルト）、`off`、または `custom`。`strict` は、Compaction 要約中に組み込みの不透明識別子保持ガイダンスを先頭に追加します。
- `identifierInstructions`: `identifierPolicy=custom` のときに使われる、任意のカスタム識別子保持テキスト。
- `postCompactionSections`: Compaction 後に再注入する任意の AGENTS.md の H2/H3 セクション名。デフォルトは `["Session Startup", "Red Lines"]` です。`[]` を設定すると再注入を無効にします。未設定、または明示的にそのデフォルトの組み合わせを設定した場合、従来互換のフォールバックとして古い `Every Session`/`Safety` 見出しも受け付けます。
- `model`: Compaction 要約専用の任意の `provider/model-id` オーバーライド。メインセッションは 1 つの model を維持しつつ、Compaction 要約は別の model で実行したい場合に使います。未設定の場合、Compaction はセッションのプライマリ model を使います。
- `notifyUser`: `true` の場合、Compaction 開始時にユーザーへ短い通知を送ります（例: 「コンテキストを Compaction 中...」）。デフォルトでは、Compaction をサイレントに保つため無効です。
- `memoryFlush`: 自動 Compaction 前に永続メモリを保存するサイレントな agent ターンです。workspace が読み取り専用の場合はスキップされます。

### `agents.defaults.contextPruning`

LLM に送信する前に、メモリ内コンテキストから**古い tool result** を削減します。ディスク上のセッション履歴は**変更しません**。

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
        hardClear: { enabled: true, placeholder: "[古い tool result の内容は削除されました]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="cache-ttl モードの動作">

- `mode: "cache-ttl"` は pruning パスを有効にします。
- `ttl` は、最後のキャッシュ更新後に pruning を再実行できる頻度を制御します。
- pruning は、まず大きすぎる tool result をソフトトリムし、その後必要に応じて古い tool result を完全クリアします。

**soft-trim** は先頭と末尾を保持し、中間に `...` を挿入します。

**hard-clear** は tool result 全体をプレースホルダーに置き換えます。

注意:

- 画像ブロックは切り詰め/クリアされません。
- 比率は文字数ベース（概算）であり、正確な token 数ではありません。
- assistant メッセージが `keepLastAssistants` 未満の場合、pruning はスキップされます。

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

- Telegram 以外の channel では、ブロック返信を有効にするには明示的な `*.blockStreaming: true` が必要です。
- channel ごとのオーバーライド: `channels.<channel>.blockStreamingCoalesce`（およびアカウントごとのバリアント）。Signal/Slack/Discord/Google Chat のデフォルトは `minChars: 1500` です。
- `humanDelay`: ブロック返信間のランダムな待機時間。`natural` = 800〜2500ms。agent ごとのオーバーライド: `agents.list[].humanDelay`。

動作とチャンク化の詳細は [Streaming](/ja-JP/concepts/streaming) を参照してください。

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

- デフォルト: ダイレクトチャット/メンションでは `instant`、メンションされていないグループチャットでは `message`。
- セッションごとのオーバーライド: `session.typingMode`、`session.typingIntervalSeconds`。

[Typing Indicators](/ja-JP/concepts/typing-indicators) を参照してください。

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

埋め込み agent 用の任意の sandbox 化です。完全なガイドは [Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。

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
          // SecretRef / インライン内容もサポート:
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

<Accordion title="sandbox の詳細">

**バックエンド:**

- `docker`: ローカル Docker ランタイム（デフォルト）
- `ssh`: 汎用 SSH バックのリモートランタイム
- `openshell`: OpenShell ランタイム

`backend: "openshell"` を選択した場合、ランタイム固有の設定は
`plugins.entries.openshell.config` に移ります。

**SSH バックエンド設定:**

- `target`: `user@host[:port]` 形式の SSH ターゲット
- `command`: SSH クライアントコマンド（デフォルト: `ssh`）
- `workspaceRoot`: スコープごとの workspace に使う絶対リモートルート
- `identityFile` / `certificateFile` / `knownHostsFile`: OpenSSH に渡される既存のローカルファイル
- `identityData` / `certificateData` / `knownHostsData`: OpenClaw がランタイム時に一時ファイルへ実体化するインライン内容または SecretRef
- `strictHostKeyChecking` / `updateHostKeys`: OpenSSH のホストキー方針ノブ

**SSH 認証の優先順位:**

- `identityData` は `identityFile` より優先
- `certificateData` は `certificateFile` より優先
- `knownHostsData` は `knownHostsFile` より優先
- SecretRef バックの `*Data` 値は、sandbox セッション開始前にアクティブな secrets ランタイムスナップショットから解決されます

**SSH バックエンドの動作:**

- 作成または再作成後に、リモート workspace を 1 回だけシードします
- その後はリモート SSH workspace を正規の状態として維持します
- `exec`、ファイル tools、media パスを SSH 経由でルーティングします
- リモート変更は自動ではホストへ同期されません
- sandbox browser コンテナはサポートしません

**workspace アクセス:**

- `none`: `~/.openclaw/sandboxes` 配下のスコープごとの sandbox workspace
- `ro`: `/workspace` に sandbox workspace、`/agent` に agent workspace を読み取り専用でマウント
- `rw`: agent workspace を `/workspace` に読み書き可能でマウント

**スコープ:**

- `session`: セッションごとのコンテナ + workspace
- `agent`: agent ごとに 1 つのコンテナ + workspace（デフォルト）
- `shared`: 共有コンテナと共有 workspace（セッション間分離なし）

**OpenShell Plugin 設定:**

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

- `mirror`: 実行前にローカルからリモートへシードし、実行後に同期し戻します。ローカル workspace が正規状態のまま維持されます
- `remote`: sandbox 作成時に 1 回だけリモートをシードし、その後はリモート workspace を正規状態として維持します

`remote` モードでは、シード後に OpenClaw 外で行われたホストローカル編集は、自動では sandbox に同期されません。
転送は OpenShell sandbox への SSH ですが、sandbox のライフサイクルと任意の mirror 同期は Plugin が管理します。

**`setupCommand`** はコンテナ作成後に 1 回だけ実行されます（`sh -lc` 経由）。ネットワーク外向き通信、書き込み可能なルート、root ユーザーが必要です。

**コンテナのデフォルトは `network: "none"`** です。agent に外向きアクセスが必要な場合は `"bridge"`（またはカスタム bridge network）に設定してください。
`"host"` はブロックされます。`"container:<id>"` は、明示的に
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` を設定しない限り（非常時用）デフォルトでブロックされます。

**受信添付ファイル** は、アクティブな workspace の `media/inbound/*` にステージされます。

**`docker.binds`** は追加のホストディレクトリをマウントします。グローバルと agent ごとの binds はマージされます。

**sandbox 化された browser**（`sandbox.browser.enabled`）: コンテナ内の Chromium + CDP。noVNC URL は system prompt に注入されます。`openclaw.json` で `browser.enabled` は不要です。
noVNC の閲覧専用アクセスはデフォルトで VNC 認証を使用し、OpenClaw は共有 URL にパスワードを露出させる代わりに短命トークン URL を発行します。

- `allowHostControl: false`（デフォルト）は、sandbox 化されたセッションがホスト browser を対象にすることをブロックします。
- `network` のデフォルトは `openclaw-sandbox-browser`（専用 bridge network）です。グローバル bridge 接続性が明示的に必要な場合のみ `bridge` に設定してください。
- `cdpSourceRange` は、必要に応じて CDP の受信接続をコンテナ境界で CIDR 範囲（例: `172.21.0.1/32`）に制限します。
- `sandbox.browser.binds` は、追加のホストディレクトリを sandbox browser コンテナにのみマウントします。設定されると（`[]` を含む）、browser コンテナでは `docker.binds` の代わりにこれが使われます。
- 起動時のデフォルトは `scripts/sandbox-browser-entrypoint.sh` で定義され、コンテナホスト向けに調整されています:
  - `--remote-debugging-address=127.0.0.1`
  - `--remote-debugging-port=<OPENCLAW_BROWSER_CDP_PORT から導出>`
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
    デフォルトで有効であり、WebGL/3D の使用で必要な場合は
    `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` で無効化できます。
  - ワークフローで extensions が必要な場合は
    `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` で再有効化できます。
  - `--renderer-process-limit=2` は
    `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` で変更できます。Chromium の
    デフォルトプロセス上限を使うには `0` を設定してください。
  - さらに、`noSandbox` が有効な場合は `--no-sandbox` と `--disable-setuid-sandbox`。
  - これらのデフォルトはコンテナイメージのベースラインです。コンテナのデフォルトを変更するには、カスタム entrypoint を持つカスタム browser イメージを使用してください。

</Accordion>

browser sandbox 化と `sandbox.docker.binds` は Docker 専用です。

イメージをビルド:

```bash
scripts/sandbox-setup.sh           # メイン sandbox イメージ
scripts/sandbox-browser-setup.sh   # 任意の browser イメージ
```

### `agents.list`（agent ごとのオーバーライド）

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
        model: "anthropic/claude-opus-4-6", // または { primary, fallbacks }
        thinkingDefault: "high", // agent ごとの thinking レベル上書き
        reasoningDefault: "on", // agent ごとの reasoning 可視性上書き
        fastModeDefault: false, // agent ごとの fast mode 上書き
        embeddedHarness: { runtime: "auto", fallback: "pi" },
        params: { cacheRetention: "none" }, // 一致する defaults.models params をキーごとに上書き
        skills: ["docs-search"], // 設定時は agents.defaults.skills を置き換え
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
- `default`: 複数設定されている場合は最初のものが優先されます（警告を記録）。どれも設定されていない場合は、リストの最初のエントリがデフォルトです。
- `model`: 文字列形式は `primary` のみを上書きし、オブジェクト形式 `{ primary, fallbacks }` は両方を上書きします（`[]` はグローバル fallbacks を無効化）。`primary` のみを上書きする Cron ジョブは、`fallbacks: []` を設定しない限りデフォルトの fallbacks を引き続き継承します。
- `params`: `agents.defaults.models` の選択された model エントリにマージされる agent ごとの stream params。model カタログ全体を複製せずに、`cacheRetention`、`temperature`、`maxTokens` などの agent 固有オーバーライドに使います。
- `skills`: 任意の agent ごとの Skills 許可リスト。省略した場合、その agent は `agents.defaults.skills` が設定されていればそれを継承します。明示的なリストはデフォルトとマージせず置き換え、`[]` は Skills なしを意味します。
- `thinkingDefault`: 任意の agent ごとのデフォルト thinking レベル（`off | minimal | low | medium | high | xhigh | adaptive`）。メッセージごとまたはセッションごとの上書きがない場合、この agent では `agents.defaults.thinkingDefault` を上書きします。
- `reasoningDefault`: 任意の agent ごとのデフォルト reasoning 可視性（`on | off | stream`）。メッセージごとまたはセッションごとの reasoning 上書きがない場合に適用されます。
- `fastModeDefault`: 任意の agent ごとの fast mode デフォルト（`true | false`）。メッセージごとまたはセッションごとの fast-mode 上書きがない場合に適用されます。
- `embeddedHarness`: 任意の agent ごとの低レベル harness ポリシー上書き。ある 1 つの agent だけを Codex 専用にし、他の agents はデフォルトの PI フォールバックを維持するには `{ runtime: "codex", fallback: "none" }` を使います。
- `runtime`: 任意の agent ごとのランタイム記述子。agent をデフォルトで ACP harness セッションにしたい場合は、`type: "acp"` と `runtime.acp` のデフォルト（`agent`、`backend`、`mode`、`cwd`）を使います。
- `identity.avatar`: workspace 相対パス、`http(s)` URL、または `data:` URI。
- `identity` はデフォルト値を導出します: `emoji` から `ackReaction`、`name`/`emoji` から `mentionPatterns`。
- `subagents.allowAgents`: `sessions_spawn` 用の agent id 許可リスト（`["*"]` = 任意、デフォルト: 同じ agent のみ）。
- sandbox 継承ガード: 要求元セッションが sandbox 化されている場合、`sessions_spawn` は sandbox なしで実行されるターゲットを拒否します。
- `subagents.requireAgentId`: true の場合、`agentId` を省略した `sessions_spawn` 呼び出しをブロックします（明示的なプロファイル選択を強制。デフォルト: false）。

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

### バインディング一致フィールド

- `type`（任意）: 通常のルーティングには `route`（type 省略時も route）、永続 ACP 会話バインディングには `acp`
- `match.channel`（必須）
- `match.accountId`（任意。`*` = 任意のアカウント、省略 = デフォルトアカウント）
- `match.peer`（任意。`{ kind: direct|group|channel, id }`）
- `match.guildId` / `match.teamId`（任意。channel 固有）
- `acp`（任意。`type: "acp"` のみ）: `{ mode, label, cwd, backend }`

**決定的な一致順序:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId`（完全一致、peer/guild/team なし）
5. `match.accountId: "*"`（channel 全体）
6. デフォルト agent

各 tier 内では、最初に一致した `bindings` エントリが優先されます。

`type: "acp"` エントリについては、OpenClaw は正確な会話 ID（`match.channel` + account + `match.peer.id`）で解決し、上記の route バインディング tier 順序は使用しません。

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
    parentForkMaxTokens: 100000, // この token 数を超える親スレッド fork はスキップ（0 で無効）
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // duration または false
      maxDiskBytes: "500mb", // 任意のハード予算
      highWaterBytes: "400mb", // 任意のクリーンアップ目標
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // 非アクティブ時の自動 unfocus のデフォルト時間（`0` で無効）
      maxAgeHours: 0, // ハード最大経過時間のデフォルト時間（`0` で無効）
    },
    mainKey: "main", // legacy（ランタイムは常に "main" を使用）
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="Session フィールド詳細">

- **`scope`**: グループチャット文脈における基本の session グループ化戦略。
  - `per-sender`（デフォルト）: channel 文脈内で、各送信者ごとに分離された session を使います。
  - `global`: channel 文脈内のすべての参加者が 1 つの session を共有します（共有コンテキストを意図する場合にのみ使用してください）。
- **`dmScope`**: DM のグループ化方法。
  - `main`: すべての DM がメイン session を共有します。
  - `per-peer`: channels をまたいで送信者 id ごとに分離します。
  - `per-channel-peer`: channel + 送信者ごとに分離します（マルチユーザー受信箱に推奨）。
  - `per-account-channel-peer`: account + channel + 送信者ごとに分離します（マルチアカウントに推奨）。
- **`identityLinks`**: channel 間で session を共有するため、正規 id を provider 接頭辞付き peer にマッピングします。
- **`reset`**: 基本のリセットポリシー。`daily` はローカル時刻の `atHour` にリセットし、`idle` は `idleMinutes` 後にリセットします。両方が設定されている場合、先に期限を迎えた方が優先されます。
- **`resetByType`**: タイプごとのオーバーライド（`direct`、`group`、`thread`）。従来の `dm` も `direct` の alias として受け付けます。
- **`parentForkMaxTokens`**: fork されたスレッド session を作成するときに許可される親 session の `totalTokens` 上限（デフォルト `100000`）。
  - 親の `totalTokens` がこの値を超える場合、OpenClaw は親 transcript 履歴を継承せず、新しいスレッド session を開始します。
  - このガードを無効にして常に親 fork を許可するには `0` を設定します。
- **`mainKey`**: legacy フィールドです。ランタイムはメインのダイレクトチャットバケットに常に `"main"` を使います。
- **`agentToAgent.maxPingPongTurns`**: agent 間のやり取り中に許可される agent 間の返信往復ターン数の上限（整数、範囲: `0`–`5`）。`0` は ping-pong 連鎖を無効にします。
- **`sendPolicy`**: `channel`、`chatType`（`direct|group|channel`、従来の `dm` alias あり）、`keyPrefix`、または `rawKeyPrefix` で一致させます。最初の deny が優先されます。
- **`maintenance`**: session ストアのクリーンアップ + 保持制御。
  - `mode`: `warn` は警告のみ出し、`enforce` はクリーンアップを適用します。
  - `pruneAfter`: 古いエントリの期限切れまでの期間（デフォルト `30d`）。
  - `maxEntries`: `sessions.json` 内の最大エントリ数（デフォルト `500`）。
  - `rotateBytes`: `sessions.json` がこのサイズを超えたらローテーションします（デフォルト `10mb`）。
  - `resetArchiveRetention`: `*.reset.<timestamp>` transcript アーカイブの保持期間。デフォルトでは `pruneAfter` を使います。無効にするには `false` を設定します。
  - `maxDiskBytes`: 任意の sessions ディレクトリのディスク予算。`warn` モードでは警告を記録し、`enforce` モードでは最も古い成果物/session から削除します。
  - `highWaterBytes`: 予算クリーンアップ後の任意の目標値。デフォルトは `maxDiskBytes` の `80%` です。
- **`threadBindings`**: スレッドバインド session 機能のグローバルデフォルト。
  - `enabled`: マスターのデフォルトスイッチ（provider ごとに上書き可能。Discord は `channels.discord.threadBindings.enabled` を使用）
  - `idleHours`: 非アクティブ時の自動 unfocus のデフォルト時間数（`0` で無効。provider ごとに上書き可能）
  - `maxAgeHours`: ハード最大経過時間のデフォルト時間数（`0` で無効。provider ごとに上書き可能）

</Accordion>

---

## Messages

```json5
{
  messages: {
    responsePrefix: "🦞", // または "auto"
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
      debounceMs: 2000, // 0 で無効
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### 応答プレフィックス

channel/account ごとのオーバーライド: `channels.<channel>.responsePrefix`、`channels.<channel>.accounts.<id>.responsePrefix`。

解決順序（最も具体的なものが優先）: account → channel → global。`""` は無効化し、カスケードも停止します。`"auto"` は `[{identity.name}]` を導出します。

**テンプレート変数:**

| 変数              | 説明                 | 例                          |
| ----------------- | -------------------- | --------------------------- |
| `{model}`         | 短い model 名        | `claude-opus-4-6`           |
| `{modelFull}`     | 完全な model 識別子  | `anthropic/claude-opus-4-6` |
| `{provider}`      | provider 名          | `anthropic`                 |
| `{thinkingLevel}` | 現在の thinking レベル | `high`, `low`, `off`        |
| `{identity.name}` | agent identity 名    | （`"auto"` と同じ）         |

変数は大文字小文字を区別しません。`{think}` は `{thinkingLevel}` の alias です。

### 確認リアクション

- デフォルトはアクティブな agent の `identity.emoji`、それ以外は `"👀"` です。無効にするには `""` を設定します。
- channel ごとのオーバーライド: `channels.<channel>.ackReaction`、`channels.<channel>.accounts.<id>.ackReaction`。
- 解決順序: account → channel → `messages.ackReaction` → identity フォールバック。
- スコープ: `group-mentions`（デフォルト）、`group-all`、`direct`、`all`。
- `removeAckAfterReply`: Slack、Discord、Telegram で返信後に ack を削除します。
- `messages.statusReactions.enabled`: Slack、Discord、Telegram でライフサイクル status リアクションを有効にします。
  Slack と Discord では、未設定の場合、ack リアクションが有効なら status リアクションも有効のままになります。
  Telegram では、ライフサイクル status リアクションを有効にするには明示的に `true` を設定してください。

### 受信 debounce

同じ送信者からの連続するテキストのみのメッセージを 1 回の agent ターンにまとめます。media/添付ファイルは即時フラッシュされます。制御コマンドは debouncing をバイパスします。

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

- `auto` はデフォルトの自動 TTS モードを制御します: `off`、`always`、`inbound`、または `tagged`。`/tts on|off` でローカル設定を上書きでき、`/tts status` で実効状態を確認できます。
- `summaryModel` は、自動要約に対して `agents.defaults.model.primary` を上書きします。
- `modelOverrides` はデフォルトで有効です。`modelOverrides.allowProvider` のデフォルトは `false`（オプトイン）です。
- API キーは `ELEVENLABS_API_KEY`/`XI_API_KEY` および `OPENAI_API_KEY` にフォールバックします。
- `openai.baseUrl` は OpenAI TTS エンドポイントを上書きします。解決順序は、設定、次に `OPENAI_TTS_BASE_URL`、最後に `https://api.openai.com/v1` です。
- `openai.baseUrl` が OpenAI 以外のエンドポイントを指している場合、OpenClaw はそれを OpenAI 互換 TTS サーバーとして扱い、model/voice 検証を緩和します。

---

## Talk

Talk mode（macOS/iOS/Android）のデフォルト設定です。

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

- `talk.provider` は、複数の Talk provider が設定されている場合、`talk.providers` 内のキーと一致している必要があります。
- 従来のフラットな Talk キー（`talk.voiceId`、`talk.voiceAliases`、`talk.modelId`、`talk.outputFormat`、`talk.apiKey`）は互換性専用であり、`talk.providers.<provider>` に自動移行されます。
- Voice ID は `ELEVENLABS_VOICE_ID` または `SAG_VOICE_ID` にフォールバックします。
- `providers.*.apiKey` はプレーンテキスト文字列または SecretRef オブジェクトを受け付けます。
- `ELEVENLABS_API_KEY` へのフォールバックは、Talk API キーが設定されていない場合にのみ適用されます。
- `providers.*.voiceAliases` を使うと、Talk ディレクティブで親しみやすい名前を使えます。
- `silenceTimeoutMs` は、Talk mode がユーザーの無音後に transcript を送信するまで待機する時間を制御します。未設定の場合はプラットフォームのデフォルト待機時間が使われます（`macOS と Android では 700 ms、iOS では 900 ms`）。

---

## Tools

### Tool プロファイル

`tools.profile` は、`tools.allow`/`tools.deny` の前に基本 allowlist を設定します。

ローカルのオンボーディングでは、新しいローカル設定で未設定の場合、デフォルトで `tools.profile: "coding"` を設定します（既存の明示的なプロファイルは保持されます）。

| プロファイル | 含まれるもの                                                                                                                |
| ------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `minimal`    | `session_status` のみ                                                                                                       |
| `coding`     | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging`  | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                   |
| `full`       | 制限なし（未設定と同じ）                                                                                                     |

### Tool グループ

| グループ           | Tools                                                                                                                   |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec`, `process`, `code_execution`（`bash` は `exec` の alias として受け付けられます）                                  |
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
| `group:openclaw`   | すべての組み込み tools（provider Plugin は除く）                                                                        |

### `tools.allow` / `tools.deny`

グローバルな tool の許可/拒否ポリシーです（deny が優先）。大文字小文字を区別せず、`*` ワイルドカードをサポートします。Docker sandbox がオフでも適用されます。

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

特定の provider または model に対して tools をさらに制限します。順序: ベースプロファイル → provider プロファイル → allow/deny。

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

sandbox の外での elevated exec アクセスを制御します:

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

- agent ごとのオーバーライド（`agents.list[].tools.elevated`）は、さらに制限することしかできません。
- `/elevated on|off|ask|full` は状態を session ごとに保存します。インラインディレクティブは 1 件のメッセージにのみ適用されます。
- Elevated `exec` は sandbox 化をバイパスし、設定された escape path を使います（デフォルトは `gateway`、exec ターゲットが `node` の場合は `node`）。

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

tool ループの安全チェックは**デフォルトで無効**です。有効化するには `enabled: true` を設定してください。
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

- `historySize`: ループ分析のために保持する tool 呼び出し履歴の最大数。
- `warningThreshold`: 警告を出す、進捗なしの繰り返しパターンのしきい値。
- `criticalThreshold`: 重大なループをブロックするための、より高い繰り返ししきい値。
- `globalCircuitBreakerThreshold`: あらゆる進捗なし実行に対するハード停止しきい値。
- `detectors.genericRepeat`: 同じ tool/同じ引数の繰り返し呼び出しに警告します。
- `detectors.knownPollNoProgress`: 既知の poll tools（`process.poll`、`command_status` など）に対して警告/ブロックします。
- `detectors.pingPong`: 交互に続く進捗なしのペアパターンに警告/ブロックします。
- `warningThreshold >= criticalThreshold` または `criticalThreshold >= globalCircuitBreakerThreshold` の場合、検証は失敗します。

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // または BRAVE_API_KEY env
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // 任意。自動検出する場合は省略
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

受信 media 理解（画像/音声/動画）を設定します:

```json5
{
  tools: {
    media: {
      concurrency: 2,
      asyncCompletion: {
        directSend: false, // opt-in: 完了した非同期 music/video を channel に直接送信
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

**Provider エントリ**（`type: "provider"` または省略）:

- `provider`: API provider id（`openai`、`anthropic`、`google`/`gemini`、`groq` など）
- `model`: model id オーバーライド
- `profile` / `preferredProfile`: `auth-profiles.json` のプロファイル選択

**CLI エントリ**（`type: "cli"`）:

- `command`: 実行する実行ファイル
- `args`: テンプレート化された引数（`{{MediaPath}}`、`{{Prompt}}`、`{{MaxChars}}` などをサポート）

**共通フィールド:**

- `capabilities`: 任意のリスト（`image`、`audio`、`video`）。デフォルト: `openai`/`anthropic`/`minimax` → image、`google` → image+audio+video、`groq` → audio。
- `prompt`、`maxChars`、`maxBytes`、`timeoutSeconds`、`language`: エントリごとのオーバーライド。
- 失敗した場合は次のエントリにフォールバックします。

provider の auth は標準順序に従います: `auth-profiles.json` → env vars → `models.providers.*.apiKey`。

**非同期完了フィールド:**

- `asyncCompletion.directSend`: `true` の場合、完了した非同期 `music_generate`
  および `video_generate` タスクは、まず direct channel 配信を試みます。デフォルト: `false`
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

session tools（`sessions_list`、`sessions_history`、`sessions_send`）でどの session を対象にできるかを制御します。

デフォルト: `tree`（現在の session + そこから spawn された session。たとえば subagents）。

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

注意:

- `self`: 現在の session key のみ。
- `tree`: 現在の session + 現在の session から spawn された session（subagents）。
- `agent`: 現在の agent id に属する任意の session（同じ agent id の下で送信者ごとの session を実行している場合、他のユーザーを含むことがあります）。
- `all`: 任意の session。agent 間ターゲティングには引き続き `tools.agentToAgent` が必要です。
- sandbox クランプ: 現在の session が sandbox 化されており、`agents.defaults.sandbox.sessionToolsVisibility="spawned"` の場合、`tools.sessions.visibility="all"` でも可視性は `tree` に強制されます。

### `tools.sessions_spawn`

`sessions_spawn` のインライン添付サポートを制御します。

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // opt-in: true にするとインラインファイル添付を許可
        maxTotalBytes: 5242880, // すべてのファイル合計で 5 MB
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 ファイルあたり 1 MB
        retainOnSessionKeep: false, // cleanup="keep" のときに添付を保持
      },
    },
  },
}
```

注意:

- 添付は `runtime: "subagent"` でのみサポートされます。ACP ランタイムはこれを拒否します。
- ファイルは子 workspace の `.openclaw/attachments/<uuid>/` に `.manifest.json` とともに実体化されます。
- 添付内容は transcript 永続化から自動的に秘匿化されます。
- Base64 入力は、厳格なアルファベット/パディング検査とデコード前サイズガードで検証されます。
- ファイル権限は、ディレクトリが `0700`、ファイルが `0600` です。
- クリーンアップは `cleanup` ポリシーに従います: `delete` は常に添付を削除し、`keep` は `retainOnSessionKeep: true` の場合にのみ保持します。

### `tools.experimental`

実験的な組み込み tool フラグです。strict-agentic GPT-5 の自動有効化ルールが適用される場合を除き、デフォルトはオフです。

```json5
{
  tools: {
    experimental: {
      planTool: true, // 実験的な update_plan を有効化
    },
  },
}
```

注意:

- `planTool`: 自明でない複数ステップ作業の追跡用に、構造化された `update_plan` tool を有効にします。
- デフォルト: `agents.defaults.embeddedPi.executionContract`（または agent ごとのオーバーライド）が OpenAI または OpenAI Codex の GPT-5 系実行に対して `"strict-agentic"` に設定されている場合を除き `false`。その範囲外でも強制的に有効にするには `true` を、strict-agentic GPT-5 実行でも無効に保つには `false` を設定してください。
- 有効な場合、system prompt にも使用ガイダンスが追加され、model はそれを実質的な作業にのみ使い、`in_progress` のステップを最大 1 つまでに保ちます。

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

- `model`: spawn された sub-agent のデフォルト model。省略した場合、sub-agent は呼び出し元の model を継承します。
- `allowAgents`: 要求元 agent が独自の `subagents.allowAgents` を設定していない場合に、`sessions_spawn` で対象にできる agent id のデフォルト allowlist（`["*"]` = 任意、デフォルト: 同じ agent のみ）。
- `runTimeoutSeconds`: tool 呼び出しで `runTimeoutSeconds` を省略した場合の、`sessions_spawn` のデフォルトタイムアウト（秒）。`0` はタイムアウトなしを意味します。
- sub-agent ごとの tool ポリシー: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`。

---

## カスタム provider と base URL

OpenClaw は組み込み model カタログを使用します。カスタム provider は設定の `models.providers` または `~/.openclaw/agents/<agentId>/agent/models.json` で追加できます。

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

- カスタム auth が必要な場合は `authHeader: true` + `headers` を使用します。
- agent 設定ルートは `OPENCLAW_AGENT_DIR`（または legacy な環境変数 alias の `PI_CODING_AGENT_DIR`）で上書きできます。
- 一致する provider ID に対するマージ優先順位:
  - 空でない agent の `models.json` `baseUrl` 値が優先されます。
  - 空でない agent の `apiKey` 値は、その provider が現在の config/auth-profile コンテキストで SecretRef 管理されていない場合にのみ優先されます。
  - SecretRef 管理された provider の `apiKey` 値は、解決済み secret を永続化する代わりに、ソースマーカー（env ref には `ENV_VAR_NAME`、file/exec ref には `secretref-managed`）から再更新されます。
  - SecretRef 管理された provider ヘッダー値も、ソースマーカー（env ref には `secretref-env:ENV_VAR_NAME`、file/exec ref には `secretref-managed`）から再更新されます。
  - agent の `apiKey`/`baseUrl` が空または欠落している場合は、設定の `models.providers` にフォールバックします。
  - 一致する model の `contextWindow`/`maxTokens` には、明示的な設定値と暗黙のカタログ値のうち高い方が使われます。
  - 一致する model の `contextTokens` は、明示的なランタイム上限が存在する場合それを保持します。ネイティブ model メタデータを変更せずに有効コンテキストを制限したい場合に使ってください。
  - 設定で `models.json` を完全に上書きしたい場合は `models.mode: "replace"` を使います。
  - マーカーの永続化はソース優先です。マーカーは、解決済みランタイム secret 値からではなく、アクティブなソース設定スナップショット（解決前）から書き込まれます。

### Provider フィールド詳細

- `models.mode`: provider カタログの動作（`merge` または `replace`）。
- `models.providers`: provider id をキーにしたカスタム provider マップ。
- `models.providers.*.api`: リクエストアダプター（`openai-completions`、`openai-responses`、`anthropic-messages`、`google-generative-ai` など）。
- `models.providers.*.apiKey`: provider の認証情報（SecretRef/env 置換の利用を推奨）。
- `models.providers.*.auth`: 認証戦略（`api-key`、`token`、`oauth`、`aws-sdk`）。
- `models.providers.*.injectNumCtxForOpenAICompat`: Ollama + `openai-completions` 用。リクエストに `options.num_ctx` を注入します（デフォルト: `true`）。
- `models.providers.*.authHeader`: 必要な場合に、認証情報を `Authorization` ヘッダーで送るよう強制します。
- `models.providers.*.baseUrl`: 上流 API の base URL。
- `models.providers.*.headers`: proxy/tenant ルーティング用の追加の静的ヘッダー。
- `models.providers.*.request`: model-provider HTTP リクエストの転送オーバーライド。
  - `request.headers`: 追加ヘッダー（provider デフォルトとマージ）。値には SecretRef を使えます。
  - `request.auth`: 認証戦略オーバーライド。モード: `"provider-default"`（provider 組み込み auth を使う）、`"authorization-bearer"`（`token` とともに使用）、`"header"`（`headerName`、`value`、任意の `prefix` とともに使用）。
  - `request.proxy`: HTTP proxy オーバーライド。モード: `"env-proxy"`（`HTTP_PROXY`/`HTTPS_PROXY` env vars を使用）、`"explicit-proxy"`（`url` とともに使用）。どちらのモードも任意の `tls` サブオブジェクトを受け付けます。
  - `request.tls`: 直接接続用の TLS オーバーライド。フィールド: `ca`、`cert`、`key`、`passphrase`（すべて SecretRef を受け付けます）、`serverName`、`insecureSkipVerify`。
  - `request.allowPrivateNetwork`: `true` の場合、provider HTTP fetch ガード経由で、DNS が private、CGNAT、または類似レンジへ解決される `baseUrl` への HTTPS を許可します（信頼済みセルフホスト OpenAI 互換 endpoint 用の operator opt-in）。WebSocket はヘッダー/TLS には同じ `request` を使いますが、その fetch SSRF ガードは使いません。デフォルトは `false`。
- `models.providers.*.models`: 明示的な provider model カタログエントリ。
- `models.providers.*.models.*.contextWindow`: model ネイティブのコンテキストウィンドウメタデータ。
- `models.providers.*.models.*.contextTokens`: 任意のランタイムコンテキスト上限。model 本来の `contextWindow` より小さい実効コンテキスト予算にしたい場合に使います。
- `models.providers.*.models.*.compat.supportsDeveloperRole`: 任意の互換性ヒント。`api: "openai-completions"` かつ空でない非ネイティブ `baseUrl`（host が `api.openai.com` ではない）の場合、OpenClaw はランタイム時にこれを `false` に強制します。`baseUrl` が空または省略されている場合は、OpenAI のデフォルト動作を維持します。
- `models.providers.*.models.*.compat.requiresStringContent`: 文字列のみを受け付ける OpenAI 互換 chat endpoint 用の任意の互換性ヒント。`true` の場合、OpenClaw はリクエスト送信前に、純粋なテキストの `messages[].content` 配列をプレーン文字列へ平坦化します。
- `plugins.entries.amazon-bedrock.config.discovery`: Bedrock 自動検出設定のルート。
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: 暗黙的な検出をオン/オフします。
- `plugins.entries.amazon-bedrock.config.discovery.region`: 検出に使う AWS リージョン。
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: 対象を絞った検出用の任意の provider-id フィルター。
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: 検出更新のポーリング間隔。
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: 検出された models 用のフォールバック context window。
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: 検出された models 用のフォールバック最大出力 token 数。

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

Cerebras には `cerebras/zai-glm-4.7` を使用し、Z.AI へ直接接続する場合は `zai/glm-4.7` を使います。

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

`OPENCODE_API_KEY`（または `OPENCODE_ZEN_API_KEY`）を設定してください。Zen カタログには `opencode/...` 参照を、Go カタログには `opencode-go/...` 参照を使います。ショートカット: `openclaw onboard --auth-choice opencode-zen` または `openclaw onboard --auth-choice opencode-go`。

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
- コーディング endpoint（デフォルト）: `https://api.z.ai/api/coding/paas/v4`
- 一般 endpoint を使う場合は、base URL オーバーライド付きのカスタム provider を定義してください。

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

China endpoint 用: `baseUrl: "https://api.moonshot.cn/v1"` または `openclaw onboard --auth-choice moonshot-api-key-cn`。

ネイティブ Moonshot endpoint は、共有の
`openai-completions` 転送上でストリーミング使用互換性を公開しており、OpenClaw は組み込み provider id だけでなく、その endpoint の機能に基づいてそれを判断します。

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

base URL には `/v1` を含めないでください（Anthropic クライアントが付加します）。ショートカット: `openclaw onboard --auth-choice synthetic-api-key`。

</Accordion>

<Accordion title="MiniMax M2.7（直接接続）">

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
model カタログのデフォルトは M2.7 のみです。
Anthropic 互換ストリーミングパスでは、OpenClaw は `thinking` を明示的に設定しない限り、
デフォルトで MiniMax の thinking を無効にします。`/fast on` または
`params.fastMode: true` は `MiniMax-M2.7` を
`MiniMax-M2.7-highspeed` に書き換えます。

</Accordion>

<Accordion title="ローカル models（LM Studio）">

[Local Models](/ja-JP/gateway/local-models) を参照してください。要点: 十分な性能のハードウェア上で LM Studio Responses API を使って大きなローカル model を実行し、フォールバック用にホスト型 models もマージしたままにしておきます。

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
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // またはプレーンテキスト文字列
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: bundled Skills のみを対象にした任意の allowlist です（managed/workspace Skills には影響しません）。
- `load.extraDirs`: 追加の共有 skill ルート（最も低い優先順位）。
- `install.preferBrew`: `true` の場合、`brew` が利用可能なら他の installer 種別へフォールバックする前に Homebrew installer を優先します。
- `install.nodeManager`: `metadata.openclaw.install`
  指定用の node installer 優先設定（`npm` | `pnpm` | `yarn` | `bun`）。
- `entries.<skillKey>.enabled: false` は、その skill が bundled/installed であっても無効にします。
- `entries.<skillKey>.apiKey`: 主要 env var を宣言する Skills 向けの簡易設定です（プレーンテキスト文字列または SecretRef オブジェクト）。

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
- 検出では、ネイティブ OpenClaw Plugins に加えて、互換性のある Codex bundle と Claude bundle も受け付けます。manifest のない Claude のデフォルトレイアウト bundle も含まれます。
- **設定変更には Gateway の再起動が必要です。**
- `allow`: 任意の allowlist（一覧にある Plugins のみ読み込まれます）。`deny` が優先されます。
- `plugins.entries.<id>.apiKey`: Plugin レベルの API キー用簡易フィールド（Plugin がサポートしている場合）。
- `plugins.entries.<id>.env`: Plugin スコープの env var マップ。
- `plugins.entries.<id>.hooks.allowPromptInjection`: `false` の場合、core は `before_prompt_build` をブロックし、従来の `before_agent_start` からの prompt 変更フィールドを無視します。一方で、従来の `modelOverride` と `providerOverride` は保持します。ネイティブ Plugin hooks と、サポートされる bundle 提供の hook ディレクトリに適用されます。
- `plugins.entries.<id>.subagent.allowModelOverride`: この Plugin が、バックグラウンド subagent 実行ごとに `provider` と `model` のオーバーライドを要求することを明示的に信頼します。
- `plugins.entries.<id>.subagent.allowedModels`: 信頼済み subagent オーバーライド用の、正規 `provider/model` ターゲットの任意の allowlist。任意の model を許可したい意図がある場合にのみ `"*"` を使ってください。
- `plugins.entries.<id>.config`: Plugin 定義の設定オブジェクト（利用可能な場合はネイティブ OpenClaw Plugin schema で検証されます）。
- `plugins.entries.firecrawl.config.webFetch`: Firecrawl の web fetch provider 設定。
  - `apiKey`: Firecrawl API キー（SecretRef を受け付けます）。`plugins.entries.firecrawl.config.webSearch.apiKey`、従来の `tools.web.fetch.firecrawl.apiKey`、または `FIRECRAWL_API_KEY` env var にフォールバックします。
  - `baseUrl`: Firecrawl API の base URL（デフォルト: `https://api.firecrawl.dev`）。
  - `onlyMainContent`: ページから主要コンテンツのみを抽出します（デフォルト: `true`）。
  - `maxAgeMs`: キャッシュの最大有効期間（ミリ秒）（デフォルト: `172800000` / 2 日）。
  - `timeoutSeconds`: スクレイプリクエストのタイムアウト秒数（デフォルト: `60`）。
- `plugins.entries.xai.config.xSearch`: xAI X Search（Grok web search）設定。
  - `enabled`: X Search provider を有効にします。
  - `model`: 検索に使う Grok model（例: `"grok-4-1-fast"`）。
- `plugins.entries.memory-core.config.dreaming`: memory の Dreaming 設定。フェーズとしきい値については [Dreaming](/ja-JP/concepts/dreaming) を参照してください。
  - `enabled`: Dreaming のマスタースイッチ（デフォルト `false`）。
  - `frequency`: 各フル Dreaming スイープの Cron 間隔（デフォルトは `"0 3 * * *"`）。
  - フェーズポリシーとしきい値は実装詳細であり、ユーザー向け設定キーではありません。
- 完全な memory 設定は [メモリ設定リファレンス](/ja-JP/reference/memory-config) にあります:
  - `agents.defaults.memorySearch.*`
  - `memory.backend`
  - `memory.citations`
  - `memory.qmd.*`
  - `plugins.entries.memory-core.config.dreaming`
- 有効な Claude bundle Plugins は、`settings.json` から埋め込み Pi デフォルトも提供できます。OpenClaw はそれらを生の OpenClaw 設定パッチではなく、サニタイズ済み agent 設定として適用します。
- `plugins.slots.memory`: アクティブな memory Plugin id を選択するか、memory Plugins を無効にするには `"none"` を指定します。
- `plugins.slots.contextEngine`: アクティブな context engine Plugin id を選択します。別の engine をインストールして選択しない限り、デフォルトは `"legacy"` です。
- `plugins.installs`: `openclaw plugins update` が使用する CLI 管理のインストールメタデータ。
  - `source`、`spec`、`sourcePath`、`installPath`、`version`、`resolvedName`、`resolvedVersion`、`resolvedSpec`、`integrity`、`shasum`、`resolvedAt`、`installedAt` を含みます。
  - `plugins.installs.*` は管理状態として扱い、手動編集より CLI コマンドを優先してください。

[Plugins](/ja-JP/tools/plugin) を参照してください。

---

## Browser

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    defaultProfile: "user",
    ssrfPolicy: {
      // dangerouslyAllowPrivateNetwork: true, // 信頼できる private-network アクセスに対してのみ opt in
      // allowPrivateNetwork: true, // legacy alias
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: { driver: "existing-session", attachOnly: true, color: "#00AA00" },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    color: "#FF4500",
    // headless: false,
    // noSandbox: false,
    // extraArgs: [],
    // executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    // attachOnly: false,
  },
}
```

- `evaluateEnabled: false` は `act:evaluate` と `wait --fn` を無効にします。
- `ssrfPolicy.dangerouslyAllowPrivateNetwork` は未設定時には無効なので、browser ナビゲーションはデフォルトで strict のままです。
- `ssrfPolicy.dangerouslyAllowPrivateNetwork: true` は、private-network browser ナビゲーションを意図的に信頼する場合にのみ設定してください。
- strict モードでは、リモート CDP profile endpoint（`profiles.*.cdpUrl`）にも、到達性/検出チェック時に同じ private-network ブロックが適用されます。
- `ssrfPolicy.allowPrivateNetwork` は従来の alias として引き続きサポートされます。
- strict モードでは、明示的な例外には `ssrfPolicy.hostnameAllowlist` と `ssrfPolicy.allowedHostnames` を使います。
- リモート profiles は attach-only です（start/stop/reset は無効）。
- `profiles.*.cdpUrl` は `http://`、`https://`、`ws://`、`wss://` を受け付けます。
  `/json/version` を OpenClaw に検出させたい場合は HTTP(S) を使い、
  provider が直接の DevTools WebSocket URL を提供する場合は WS(S)
  を使ってください。
- `existing-session` profiles は host 専用で、CDP の代わりに Chrome MCP を使います。
- `existing-session` profiles では、特定の
  Chromium ベース browser profile（Brave や Edge など）を対象にするために `userDataDir` を設定できます。
- `existing-session` profiles は、現在の Chrome MCP ルート制限を維持します:
  CSS セレクター指定ではなく snapshot/ref ベースのアクション、単一ファイルのアップロード
  hooks、dialog タイムアウト上書きなし、`wait --load networkidle` なし、
  さらに `responsebody`、PDF エクスポート、ダウンロード傍受、バッチアクションもありません。
- ローカル管理の `openclaw` profiles は `cdpPort` と `cdpUrl` を自動割り当てします。明示的に
  `cdpUrl` を設定するのはリモート CDP の場合のみです。
- 自動検出順序: デフォルト browser が Chromium ベースならそれを優先 → Chrome → Brave → Edge → Chromium → Chrome Canary。
- 制御サービス: loopback のみ（port は `gateway.port` から導出。デフォルト `18791`）。
- `extraArgs` は、ローカル Chromium 起動に追加の起動フラグを付加します（たとえば
  `--disable-gpu`、ウィンドウサイズ設定、デバッグフラグなど）。

---

## UI

```json5
{
  ui: {
    seamColor: "#FF4500",
    assistant: {
      name: "OpenClaw",
      avatar: "CB", // emoji, short text, image URL, or data URI
    },
  },
}
```

- `seamColor`: ネイティブ app UI chrome 用のアクセントカラーです（Talk Mode のバブル色合いなど）。
- `assistant`: Control UI の identity オーバーライド。アクティブな agent identity にフォールバックします。

---

## Gateway

```json5
{
  gateway: {
    mode: "local", // local | remote
    port: 18789,
    bind: "loopback",
    auth: {
      mode: "token", // none | token | password | trusted-proxy
      token: "your-token",
      // password: "your-password", // or OPENCLAW_GATEWAY_PASSWORD
      // trustedProxy: { userHeader: "x-forwarded-user" }, // mode=trusted-proxy 用。/gateway/trusted-proxy-auth を参照
      allowTailscale: true,
      rateLimit: {
        maxAttempts: 10,
        windowMs: 60000,
        lockoutMs: 300000,
        exemptLoopback: true,
      },
    },
    tailscale: {
      mode: "off", // off | serve | funnel
      resetOnExit: false,
    },
    controlUi: {
      enabled: true,
      basePath: "/openclaw",
      // root: "dist/control-ui",
      // embedSandbox: "scripts", // strict | scripts | trusted
      // allowExternalEmbedUrls: false, // 危険: 絶対外部 http(s) 埋め込み URL を許可
      // allowedOrigins: ["https://control.example.com"], // 非 loopback の Control UI に必須
      // dangerouslyAllowHostHeaderOriginFallback: false, // 危険な Host ヘッダー origin フォールバックモード
      // allowInsecureAuth: false,
      // dangerouslyDisableDeviceAuth: false,
    },
    remote: {
      url: "ws://gateway.tailnet:18789",
      transport: "ssh", // ssh | direct
      token: "your-token",
      // password: "your-password",
    },
    trustedProxies: ["10.0.0.1"],
    // 任意。デフォルトは false。
    allowRealIpFallback: false,
    tools: {
      // /tools/invoke HTTP に対する追加 deny
      deny: ["browser"],
      // デフォルトの HTTP deny リストから tools を除外
      allow: ["gateway"],
    },
    push: {
      apns: {
        relay: {
          baseUrl: "https://relay.example.com",
          timeoutMs: 10000,
        },
      },
    },
  },
}
```

<Accordion title="Gateway フィールド詳細">

- `mode`: `local`（Gateway を実行）または `remote`（リモート Gateway に接続）。`local` でない限り Gateway は起動を拒否します。
- `port`: WS + HTTP 用の単一多重化ポート。優先順位: `--port` > `OPENCLAW_GATEWAY_PORT` > `gateway.port` > `18789`。
- `bind`: `auto`、`loopback`（デフォルト）、`lan`（`0.0.0.0`）、`tailnet`（Tailscale IP のみ）、または `custom`。
- **従来の bind alias**: `gateway.bind` にはホスト alias（`0.0.0.0`、`127.0.0.1`、`localhost`、`::`、`::1`）ではなく、bind mode 値（`auto`、`loopback`、`lan`、`tailnet`、`custom`）を使ってください。
- **Docker 注意事項**: デフォルトの `loopback` bind は、コンテナ内では `127.0.0.1` で待ち受けます。Docker bridge ネットワーク（`-p 18789:18789`）では、トラフィックは `eth0` に到着するため、Gateway に到達できません。`--network host` を使うか、すべてのインターフェースで待ち受けるために `bind: "lan"`（または `bind: "custom"` と `customBindHost: "0.0.0.0"`）を設定してください。
- **Auth**: デフォルトで必須です。loopback 以外の bind には Gateway auth が必要です。実運用では、共有 token/password または `gateway.auth.mode: "trusted-proxy"` を使う ID 認識型 reverse proxy を意味します。オンボーディングウィザードはデフォルトで token を生成します。
- `gateway.auth.token` と `gateway.auth.password` の両方が設定されている場合（SecretRef を含む）、`gateway.auth.mode` を `token` または `password` に明示設定してください。両方が設定されていて mode が未設定の場合、起動と service のインストール/修復フローは失敗します。
- `gateway.auth.mode: "none"`: 明示的な no-auth mode。信頼できる local loopback 構成でのみ使用してください。これは意図的にオンボーディングプロンプトでは提供されません。
- `gateway.auth.mode: "trusted-proxy"`: auth を ID 認識型 reverse proxy に委譲し、`gateway.trustedProxies` からの ID ヘッダーを信頼します（[Trusted Proxy Auth](/ja-JP/gateway/trusted-proxy-auth) を参照）。この mode は**非 loopback** の proxy ソースを前提とします。同一ホストの loopback reverse proxy は trusted-proxy auth の要件を満たしません。
- `gateway.auth.allowTailscale`: `true` の場合、Tailscale Serve の identity ヘッダーで Control UI/WebSocket auth を満たせます（`tailscale whois` で検証）。HTTP API endpoint はこの Tailscale ヘッダー auth を**使わず**、通常の Gateway HTTP auth mode に従います。この token なしフローは Gateway ホストが信頼されている前提です。`tailscale.mode = "serve"` の場合、デフォルトは `true` です。
- `gateway.auth.rateLimit`: 任意の認証失敗レート制限です。クライアント IP ごと、および auth スコープごとに適用されます（共有 secret と device token は独立して追跡されます）。ブロックされた試行には `429` + `Retry-After` が返されます。
  - 非同期の Tailscale Serve Control UI パスでは、同じ `{scope, clientIp}` に対する失敗試行は、失敗書き込み前に直列化されます。そのため、同じクライアントからの並行する不正試行は、両方が単なる不一致として競合通過するのではなく、2 回目のリクエストで制限に達する場合があります。
  - `gateway.auth.rateLimit.exemptLoopback` のデフォルトは `true` です。localhost トラフィックも意図的にレート制限したい場合（テスト構成や厳格な proxy 配置など）は `false` に設定してください。
- browser 由来の WS auth 試行は、loopback 免除を無効にした状態で常にスロットルされます（browser ベースの localhost ブルートフォースに対する多層防御）。
- loopback 上では、それらの browser 由来ロックアウトは正規化された `Origin`
  値ごとに分離されるため、ある localhost origin からの繰り返し失敗が、
  自動的に別の origin をロックアウトすることはありません。
- `tailscale.mode`: `serve`（tailnet のみ、loopback bind）または `funnel`（公開、auth 必須）。
- `controlUi.allowedOrigins`: Gateway WebSocket 接続用の明示的な browser origin allowlist。非 loopback origin から browser クライアントが接続する想定なら必須です。
- `controlUi.dangerouslyAllowHostHeaderOriginFallback`: Host ヘッダー origin ポリシーに意図的に依存するデプロイ向けの、危険な Host ヘッダー origin フォールバックモードを有効にします。
- `remote.transport`: `ssh`（デフォルト）または `direct`（ws/wss）。`direct` の場合、`remote.url` は `ws://` または `wss://` でなければなりません。
- `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`: クライアント側の非常時用オーバーライドで、信頼できる private-network IP への平文 `ws://` を許可します。デフォルトでは、平文は引き続き loopback のみです。
- `gateway.remote.token` / `.password` はリモートクライアント用の認証情報フィールドです。これら自体は Gateway auth を設定しません。
- `gateway.push.apns.relay.baseUrl`: 公式/TestFlight iOS ビルドが relay バック登録を Gateway に公開した後に使用される、外部 APNs relay の base HTTPS URL。この URL は iOS ビルドにコンパイルされた relay URL と一致している必要があります。
- `gateway.push.apns.relay.timeoutMs`: Gateway から relay への送信タイムアウト（ミリ秒）。デフォルトは `10000`。
- relay バック登録は特定の Gateway identity に委譲されます。ペア済み iOS app は `gateway.identity.get` を取得し、その identity を relay 登録に含め、登録スコープの送信権限を Gateway へ転送します。別の Gateway はその保存済み登録を再利用できません。
- `OPENCLAW_APNS_RELAY_BASE_URL` / `OPENCLAW_APNS_RELAY_TIMEOUT_MS`: 上記 relay 設定の一時的な env オーバーライド。
- `OPENCLAW_APNS_RELAY_ALLOW_HTTP=true`: loopback HTTP relay URL 用の開発専用 escape hatch。本番 relay URL は HTTPS のままにしてください。
- `gateway.channelHealthCheckMinutes`: channel ヘルスモニター間隔（分）。ヘルスモニター再起動をグローバルに無効にするには `0` を設定します。デフォルト: `5`。
- `gateway.channelStaleEventThresholdMinutes`: 古い socket と見なすしきい値（分）。これは `gateway.channelHealthCheckMinutes` 以上に保ってください。デフォルト: `30`。
- `gateway.channelMaxRestartsPerHour`: ローリング 1 時間あたりの、channel/account ごとのヘルスモニター再起動回数上限。デフォルト: `10`。
- `channels.<provider>.healthMonitor.enabled`: グローバルモニターを有効のまま、channel ごとにヘルスモニター再起動を opt out します。
- `channels.<provider>.accounts.<accountId>.healthMonitor.enabled`: マルチアカウント channel 用のアカウントごとのオーバーライド。設定されている場合、channel レベルのオーバーライドより優先されます。
- ローカル Gateway 呼び出しパスでは、`gateway.auth.*` が未設定の場合にのみ `gateway.remote.*` をフォールバックとして使えます。
- `gateway.auth.token` / `gateway.auth.password` が SecretRef 経由で明示設定されていて未解決の場合、解決はフェイルクローズします（リモートフォールバックで隠蔽されません）。
- `trustedProxies`: TLS を終端する、または転送クライアントヘッダーを注入する reverse proxy の IP。自分が管理する proxy のみを列挙してください。loopback エントリは、同一ホスト proxy/ローカル検出構成（たとえば Tailscale Serve やローカル reverse proxy）では依然有効ですが、loopback リクエストが `gateway.auth.mode: "trusted-proxy"` の対象になるわけでは**ありません**。
- `allowRealIpFallback`: `true` の場合、`X-Forwarded-For` がないときに `X-Real-IP` を受け入れます。デフォルトは、フェイルクローズ動作のため `false` です。
- `gateway.tools.deny`: HTTP `POST /tools/invoke` に対して追加でブロックする tool 名（デフォルト deny リストを拡張）。
- `gateway.tools.allow`: デフォルトの HTTP deny リストから tool 名を除外します。

</Accordion>

### OpenAI 互換 endpoint

- Chat Completions: デフォルトでは無効です。`gateway.http.endpoints.chatCompletions.enabled: true` で有効にします。
- Responses API: `gateway.http.endpoints.responses.enabled`。
- Responses の URL 入力 hardening:
  - `gateway.http.endpoints.responses.maxUrlParts`
  - `gateway.http.endpoints.responses.files.urlAllowlist`
  - `gateway.http.endpoints.responses.images.urlAllowlist`
    空の allowlist は未設定として扱われます。URL 取得を無効にするには
    `gateway.http.endpoints.responses.files.allowUrl=false`
    および/または `gateway.http.endpoints.responses.images.allowUrl=false` を使ってください。
- 任意のレスポンス hardening ヘッダー:
  - `gateway.http.securityHeaders.strictTransportSecurity`（自分が制御する HTTPS origin に対してのみ設定。 [Trusted Proxy Auth](/ja-JP/gateway/trusted-proxy-auth#tls-termination-and-hsts) を参照）

### マルチインスタンス分離

1 台のホストで複数の Gateway を、固有のポートと状態ディレクトリで実行します:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json \
OPENCLAW_STATE_DIR=~/.openclaw-a \
openclaw gateway --port 19001
```

便利なフラグ: `--dev`（`~/.openclaw-dev` + ポート `19001` を使用）、`--profile <name>`（`~/.openclaw-<name>` を使用）。

[Multiple Gateways](/ja-JP/gateway/multiple-gateways) を参照してください。

### `gateway.tls`

```json5
{
  gateway: {
    tls: {
      enabled: false,
      autoGenerate: false,
      certPath: "/etc/openclaw/tls/server.crt",
      keyPath: "/etc/openclaw/tls/server.key",
      caPath: "/etc/openclaw/tls/ca-bundle.crt",
    },
  },
}
```

- `enabled`: Gateway リスナーで TLS 終端（HTTPS/WSS）を有効にします（デフォルト: `false`）。
- `autoGenerate`: 明示的なファイルが設定されていない場合に、ローカルの自己署名 cert/key ペアを自動生成します。ローカル/開発用途専用です。
- `certPath`: TLS 証明書ファイルへのファイルシステムパス。
- `keyPath`: TLS 秘密鍵ファイルへのファイルシステムパス。権限制限を維持してください。
- `caPath`: クライアント検証またはカスタム信頼チェーン用の任意の CA バンドルパス。

### `gateway.reload`

```json5
{
  gateway: {
    reload: {
      mode: "hybrid", // off | restart | hot | hybrid
      debounceMs: 500,
      deferralTimeoutMs: 300000,
    },
  },
}
```

- `mode`: 設定編集をランタイムでどのように適用するかを制御します。
  - `"off"`: ライブ編集を無視します。変更には明示的な再起動が必要です。
  - `"restart"`: 設定変更時に常に Gateway プロセスを再起動します。
  - `"hot"`: 再起動せずにプロセス内で変更を適用します。
  - `"hybrid"`（デフォルト）: まず hot reload を試し、必要であれば restart にフォールバックします。
- `debounceMs`: 設定変更を適用する前の debounce ウィンドウ（ms）（非負整数）。
- `deferralTimeoutMs`: 進行中の操作を待ってから再起動を強制するまでの最大時間（ms）（デフォルト: `300000` = 5 分）。

---

## Hooks

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
    maxBodyBytes: 262144,
    defaultSessionKey: "hook:ingress",
    allowRequestSessionKey: false,
    allowedSessionKeyPrefixes: ["hook:"],
    allowedAgentIds: ["hooks", "main"],
    presets: ["gmail"],
    transformsDir: "~/.openclaw/hooks/transforms",
    mappings: [
      {
        match: { path: "gmail" },
        action: "agent",
        agentId: "hooks",
        wakeMode: "now",
        name: "Gmail",
        sessionKey: "hook:gmail:{{messages[0].id}}",
        messageTemplate: "From: {{messages[0].from}}\nSubject: {{messages[0].subject}}\n{{messages[0].snippet}}",
        deliver: true,
        channel: "last",
        model: "openai/gpt-5.4-mini",
      },
    ],
  },
}
```

Auth: `Authorization: Bearer <token>` または `x-openclaw-token: <token>`。
クエリ文字列の hook token は拒否されます。

検証と安全性に関する注意:

- `hooks.enabled=true` には、空でない `hooks.token` が必要です。
- `hooks.token` は `gateway.auth.token` と**異なっている必要があります**。Gateway token の再利用は拒否されます。
- `hooks.path` は `/` にできません。`/hooks` のような専用サブパスを使ってください。
- `hooks.allowRequestSessionKey=true` の場合は、`hooks.allowedSessionKeyPrefixes` を制限してください（例: `["hook:"]`）。

**Endpoints:**

- `POST /hooks/wake` → `{ text, mode?: "now"|"next-heartbeat" }`
- `POST /hooks/agent` → `{ message, name?, agentId?, sessionKey?, wakeMode?, deliver?, channel?, to?, model?, thinking?, timeoutSeconds? }`
  - リクエスト payload の `sessionKey` は、`hooks.allowRequestSessionKey=true` の場合にのみ受け付けられます（デフォルト: `false`）。
- `POST /hooks/<name>` → `hooks.mappings` 経由で解決されます

<Accordion title="マッピング詳細">

- `match.path` は `/hooks` の後のサブパスに一致します（例: `/hooks/gmail` → `gmail`）。
- `match.source` は汎用パス用の payload フィールドに一致します。
- `{{messages[0].subject}}` のようなテンプレートは payload から読み取ります。
- `transform` は、hook アクションを返す JS/TS module を指せます。
  - `transform.module` は相対パスである必要があり、`hooks.transformsDir` 内にとどまります（絶対パスと path traversal は拒否されます）。
- `agentId` は特定の agent にルーティングします。不明な ID はデフォルトへフォールバックします。
- `allowedAgentIds`: 明示的なルーティングを制限します（`*` または省略 = すべて許可、`[]` = すべて拒否）。
- `defaultSessionKey`: 明示的な `sessionKey` がない hook agent 実行用の任意の固定 session key。
- `allowRequestSessionKey`: `/hooks/agent` 呼び出し元が `sessionKey` を設定できるようにします（デフォルト: `false`）。
- `allowedSessionKeyPrefixes`: 明示的な `sessionKey` 値（リクエスト + マッピング）用の任意の接頭辞 allowlist。例: `["hook:"]`。
- `deliver: true` は最終返信を channel に送信します。`channel` のデフォルトは `last` です。
- `model` はこの hook 実行用の LLM を上書きします（model カタログが設定されている場合、許可されている必要があります）。

</Accordion>

### Gmail 統合

```json5
{
  hooks: {
    gmail: {
      account: "openclaw@gmail.com",
      topic: "projects/<project-id>/topics/gog-gmail-watch",
      subscription: "gog-gmail-watch-push",
      pushToken: "shared-push-token",
      hookUrl: "http://127.0.0.1:18789/hooks/gmail",
      includeBody: true,
      maxBytes: 20000,
      renewEveryMinutes: 720,
      serve: { bind: "127.0.0.1", port: 8788, path: "/" },
      tailscale: { mode: "funnel", path: "/gmail-pubsub" },
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

- 設定されている場合、Gateway は起動時に `gog gmail watch serve` を自動起動します。無効にするには `OPENCLAW_SKIP_GMAIL_WATCHER=1` を設定してください。
- Gateway と並行して別の `gog gmail watch serve` を実行しないでください。

---

## Canvas host

```json5
{
  canvasHost: {
    root: "~/.openclaw/workspace/canvas",
    liveReload: true,
    // enabled: false, // または OPENCLAW_SKIP_CANVAS_HOST=1
  },
}
```

- agent が編集可能な HTML/CSS/JS と A2UI を、Gateway ポート配下の HTTP で配信します:
  - `http://<gateway-host>:<gateway.port>/__openclaw__/canvas/`
  - `http://<gateway-host>:<gateway.port>/__openclaw__/a2ui/`
- ローカル専用: `gateway.bind: "loopback"`（デフォルト）のままにしてください。
- loopback 以外の bind では、canvas ルートにも他の Gateway HTTP サーフェスと同様に Gateway auth（token/password/trusted-proxy）が必要です。
- Node WebViews は通常 auth ヘッダーを送信しません。node がペアリングされ接続されると、Gateway は canvas/A2UI アクセス用の node スコープ capability URL を通知します。
- capability URL はアクティブな node WS セッションにバインドされ、すぐに期限切れになります。IP ベースのフォールバックは使われません。
- 配信される HTML に live-reload クライアントを注入します。
- 空の場合はスターター `index.html` を自動作成します。
- A2UI も `/__openclaw__/a2ui/` で配信します。
- 変更には Gateway の再起動が必要です。
- 大きなディレクトリや `EMFILE` エラーの場合は live reload を無効にしてください。

---

## Discovery

### mDNS（Bonjour）

```json5
{
  discovery: {
    mdns: {
      mode: "minimal", // minimal | full | off
    },
  },
}
```

- `minimal`（デフォルト）: TXT レコードから `cliPath` + `sshPort` を省略します。
- `full`: `cliPath` + `sshPort` を含めます。
- hostname のデフォルトは `openclaw`。上書きするには `OPENCLAW_MDNS_HOSTNAME` を使います。

### 広域（DNS-SD）

```json5
{
  discovery: {
    wideArea: { enabled: true },
  },
}
```

`~/.openclaw/dns/` 配下にユニキャスト DNS-SD zone を書き込みます。ネットワーク間 discovery には、DNS サーバー（推奨: CoreDNS）+ Tailscale split DNS と組み合わせてください。

セットアップ: `openclaw dns setup --apply`。

---

## Environment

### `env`（インライン env vars）

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: {
      GROQ_API_KEY: "gsk-...",
    },
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

- インライン env vars は、プロセス env にそのキーが存在しない場合にのみ適用されます。
- `.env` ファイル: カレントディレクトリの `.env` + `~/.openclaw/.env`（どちらも既存の変数は上書きしません）。
- `shellEnv`: ログイン shell プロファイルから、足りない想定キーを取り込みます。
- 完全な優先順位は [Environment](/ja-JP/help/environment) を参照してください。

### Env var 置換

任意の設定文字列で `${VAR_NAME}` を使って env vars を参照できます:

```json5
{
  gateway: {
    auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" },
  },
}
```

- 一致するのは大文字名のみです: `[A-Z_][A-Z0-9_]*`。
- 変数が欠落している、または空の場合、設定読み込み時にエラーになります。
- リテラルの `${VAR}` にするには `$${VAR}` でエスケープしてください。
- `$include` でも動作します。

---

## Secrets

Secret refs は加算的です。プレーンテキスト値も引き続き使えます。

### `SecretRef`

次の 1 つのオブジェクト形を使います:

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

検証:

- `provider` パターン: `^[a-z][a-z0-9_-]{0,63}$`
- `source: "env"` の id パターン: `^[A-Z][A-Z0-9_]{0,127}$`
- `source: "file"` の id: 絶対 JSON pointer（例: `"/providers/openai/apiKey"`）
- `source: "exec"` の id パターン: `^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$`
- `source: "exec"` の id には、`.` または `..` のスラッシュ区切りパスセグメントを含めてはいけません（例: `a/../b` は拒否されます）

### サポートされる認証情報サーフェス

- 正規の一覧: [SecretRef Credential Surface](/ja-JP/reference/secretref-credential-surface)
- `secrets apply` は、サポートされる `openclaw.json` の認証情報パスを対象にします。
- `auth-profiles.json` の refs もランタイム解決と監査対象に含まれます。

### Secret provider 設定

```json5
{
  secrets: {
    providers: {
      default: { source: "env" }, // 任意の明示的 env provider
      filemain: {
        source: "file",
        path: "~/.openclaw/secrets.json",
        mode: "json",
        timeoutMs: 5000,
      },
      vault: {
        source: "exec",
        command: "/usr/local/bin/openclaw-vault-resolver",
        passEnv: ["PATH", "VAULT_ADDR"],
      },
    },
    defaults: {
      env: "default",
      file: "filemain",
      exec: "vault",
    },
  },
}
```

注意:

- `file` provider は `mode: "json"` と `mode: "singleValue"` をサポートします（singleValue mode では `id` は `"value"` でなければなりません）。
- `exec` provider には絶対 `command` パスが必要で、stdin/stdout 上のプロトコル payload を使用します。
- デフォルトでは symlink の command パスは拒否されます。解決後のターゲットパスを検証しつつ symlink パスを許可するには `allowSymlinkCommand: true` を設定してください。
- `trustedDirs` が設定されている場合、trusted-dir チェックは解決後のターゲットパスに適用されます。
- `exec` 子プロセス環境はデフォルトで最小限です。必要な変数は `passEnv` で明示的に渡してください。
- Secret refs は有効化時にメモリ内スナップショットへ解決され、その後のリクエストパスはそのスナップショットだけを読みます。
- アクティブサーフェスフィルタリングは有効化中に適用されます。有効なサーフェス上の未解決 refs は起動/リロードを失敗させ、非アクティブなサーフェスは診断付きでスキップされます。

---

## Auth ストレージ

```json5
{
  auth: {
    profiles: {
      "anthropic:default": { provider: "anthropic", mode: "api_key" },
      "anthropic:work": { provider: "anthropic", mode: "api_key" },
      "openai-codex:personal": { provider: "openai-codex", mode: "oauth" },
    },
    order: {
      anthropic: ["anthropic:default", "anthropic:work"],
      "openai-codex": ["openai-codex:personal"],
    },
  },
}
```

- agent ごとの profiles は `<agentDir>/auth-profiles.json` に保存されます。
- `auth-profiles.json` は、静的認証モード用の値レベル refs（`api_key` には `keyRef`、`token` には `tokenRef`）をサポートします。
- OAuth モード profile（`auth.profiles.<id>.mode = "oauth"`）は、SecretRef バックの auth-profile 認証情報をサポートしません。
- 静的ランタイム認証情報はメモリ内の解決済みスナップショットから取得され、従来の静的 `auth.json` エントリは見つかると除去されます。
- 従来の OAuth インポート元は `~/.openclaw/credentials/oauth.json` です。
- [OAuth](/ja-JP/concepts/oauth) を参照してください。
- Secrets ランタイム動作と `audit/configure/apply` ツール群: [Secrets Management](/ja-JP/gateway/secrets)。

### `auth.cooldowns`

```json5
{
  auth: {
    cooldowns: {
      billingBackoffHours: 5,
      billingBackoffHoursByProvider: { anthropic: 3, openai: 8 },
      billingMaxHours: 24,
      authPermanentBackoffMinutes: 10,
      authPermanentMaxMinutes: 60,
      failureWindowHours: 24,
      overloadedProfileRotations: 1,
      overloadedBackoffMs: 0,
      rateLimitedProfileRotations: 1,
    },
  },
}
```

- `billingBackoffHours`: 真の
  billing/insufficient-credit エラーで profile が失敗したときの基本バックオフ時間（時）（デフォルト: `5`）。明示的な billing テキストは
  `401`/`403` 応答でもここに入ることがありますが、provider 固有のテキスト
  マッチャーはその provider に属するものだけに限定されます（例: OpenRouter の
  `Key limit exceeded`）。再試行可能な HTTP `402` の使用量ウィンドウや
  organization/workspace 支出上限メッセージは、代わりに `rate_limit` パス
  に残ります。
- `billingBackoffHoursByProvider`: billing バックオフ時間の任意の provider ごとの上書き。
- `billingMaxHours`: billing バックオフ指数増加の上限時間（時）（デフォルト: `24`）。
- `authPermanentBackoffMinutes`: 高信頼の `auth_permanent` 失敗に対する基本バックオフ時間（分）（デフォルト: `10`）。
- `authPermanentMaxMinutes`: `auth_permanent` バックオフ増加の上限時間（分）（デフォルト: `60`）。
- `failureWindowHours`: バックオフカウンターに使うローリングウィンドウ時間（時）（デフォルト: `24`）。
- `overloadedProfileRotations`: overloaded エラーで model フォールバックに切り替える前に行う、同一 provider 内 auth-profile ローテーションの最大回数（デフォルト: `1`）。`ModelNotReadyException` のような provider busy 形状はここに入ります。
- `overloadedBackoffMs`: overloaded な provider/profile ローテーションを再試行する前の固定遅延（デフォルト: `0`）。
- `rateLimitedProfileRotations`: rate-limit エラーで model フォールバックに切り替える前に行う、同一 provider 内 auth-profile ローテーションの最大回数（デフォルト: `1`）。その rate-limit バケットには、`Too many concurrent requests`、`ThrottlingException`、`concurrency limit reached`、`workers_ai ... quota limit exceeded`、`resource exhausted` のような provider 由来テキストも含まれます。

---

## Logging

```json5
{
  logging: {
    level: "info",
    file: "/tmp/openclaw/openclaw.log",
    consoleLevel: "info",
    consoleStyle: "pretty", // pretty | compact | json
    redactSensitive: "tools", // off | tools
    redactPatterns: ["\\bTOKEN\\b\\s*[=:]\\s*([\"']?)([^\\s\"']+)\\1"],
  },
}
```

- デフォルトのログファイル: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`。
- 安定したパスにするには `logging.file` を設定してください。
- `consoleLevel` は `--verbose` で `debug` に上がります。
- `maxFileBytes`: 書き込みを抑止する前の最大ログファイルサイズ（バイト）（正の整数。デフォルト: `524288000` = 500 MB）。本番デプロイでは外部ログローテーションを使ってください。

---

## Diagnostics

```json5
{
  diagnostics: {
    enabled: true,
    flags: ["telegram.*"],
    stuckSessionWarnMs: 30000,

    otel: {
      enabled: false,
      endpoint: "https://otel-collector.example.com:4318",
      protocol: "http/protobuf", // http/protobuf | grpc
      headers: { "x-tenant-id": "my-org" },
      serviceName: "openclaw-gateway",
      traces: true,
      metrics: true,
      logs: false,
      sampleRate: 1.0,
      flushIntervalMs: 5000,
    },

    cacheTrace: {
      enabled: false,
      filePath: "~/.openclaw/logs/cache-trace.jsonl",
      includeMessages: true,
      includePrompt: true,
      includeSystem: true,
    },
  },
}
```

- `enabled`: 計装出力のマスタートグルです（デフォルト: `true`）。
- `flags`: 対象を絞ったログ出力を有効にするフラグ文字列の配列です（`"telegram.*"` や `"*"` のようなワイルドカードをサポートします）。
- `stuckSessionWarnMs`: session が処理中状態のままの間に stuck-session 警告を出すための経過時間しきい値（ms）。
- `otel.enabled`: OpenTelemetry エクスポートパイプラインを有効にします（デフォルト: `false`）。
- `otel.endpoint`: OTel エクスポート用の collector URL。
- `otel.protocol`: `"http/protobuf"`（デフォルト）または `"grpc"`。
- `otel.headers`: OTel エクスポートリクエストとともに送信される追加の HTTP/gRPC メタデータヘッダー。
- `otel.serviceName`: リソース属性用のサービス名。
- `otel.traces` / `otel.metrics` / `otel.logs`: trace、metrics、または log エクスポートを有効にします。
- `otel.sampleRate`: trace サンプリング率 `0`–`1`。
- `otel.flushIntervalMs`: 定期テレメトリ flush 間隔（ms）。
- `cacheTrace.enabled`: 埋め込み実行の cache trace スナップショットを記録します（デフォルト: `false`）。
- `cacheTrace.filePath`: cache trace JSONL の出力パス（デフォルト: `$OPENCLAW_STATE_DIR/logs/cache-trace.jsonl`）。
- `cacheTrace.includeMessages` / `includePrompt` / `includeSystem`: cache trace 出力に何を含めるかを制御します（すべてデフォルトは `true`）。

---

## Update

```json5
{
  update: {
    channel: "stable", // stable | beta | dev
    checkOnStart: true,

    auto: {
      enabled: false,
      stableDelayHours: 6,
      stableJitterHours: 12,
      betaCheckIntervalHours: 1,
    },
  },
}
```

- `channel`: npm/git インストール用のリリース channel — `"stable"`、`"beta"`、または `"dev"`。
- `checkOnStart`: Gateway 起動時に npm アップデートを確認します（デフォルト: `true`）。
- `auto.enabled`: package インストール用のバックグラウンド自動アップデートを有効にします（デフォルト: `false`）。
- `auto.stableDelayHours`: stable channel の自動適用までの最小遅延時間（時）（デフォルト: `6`、最大: `168`）。
- `auto.stableJitterHours`: stable channel ロールアウトの追加分散ウィンドウ時間（時）（デフォルト: `12`、最大: `168`）。
- `auto.betaCheckIntervalHours`: beta channel の確認を実行する間隔（時）（デフォルト: `1`、最大: `24`）。

---

## ACP

```json5
{
  acp: {
    enabled: false,
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "main",
    allowedAgents: ["main", "ops"],
    maxConcurrentSessions: 10,

    stream: {
      coalesceIdleMs: 50,
      maxChunkChars: 1000,
      repeatSuppression: true,
      deliveryMode: "live", // live | final_only
      hiddenBoundarySeparator: "paragraph", // none | space | newline | paragraph
      maxOutputChars: 50000,
      maxSessionUpdateChars: 500,
    },

    runtime: {
      ttlMinutes: 30,
    },
  },
}
```

- `enabled`: グローバル ACP 機能ゲート（デフォルト: `false`）。
- `dispatch.enabled`: ACP session ターンディスパッチ用の独立したゲート（デフォルト: `true`）。ACP コマンドは利用可能なまま実行だけをブロックしたい場合は `false` に設定します。
- `backend`: デフォルト ACP ランタイムバックエンド id（登録済み ACP ランタイム Plugin と一致している必要があります）。
- `defaultAgent`: spawn 時に明示的なターゲットが指定されない場合のフォールバック ACP ターゲット agent id。
- `allowedAgents`: ACP ランタイム session に許可される agent id の allowlist。空の場合は追加制限なしを意味します。
- `maxConcurrentSessions`: 同時にアクティブになれる ACP session の最大数。
- `stream.coalesceIdleMs`: ストリーミング text 用のアイドル flush ウィンドウ（ms）。
- `stream.maxChunkChars`: ストリーミングされたブロック投影を分割する前の最大チャンクサイズ。
- `stream.repeatSuppression`: ターンごとの繰り返し status/tool 行を抑制します（デフォルト: `true`）。
- `stream.deliveryMode`: `"live"` は段階的にストリーミングし、`"final_only"` はターン終端イベントまでバッファリングします。
- `stream.hiddenBoundarySeparator`: 非表示 tool イベントの後、可視 text の前に入れる区切り（デフォルト: `"paragraph"`）。
- `stream.maxOutputChars`: ACP ターンごとに投影される assistant 出力文字数の上限。
- `stream.maxSessionUpdateChars`: 投影される ACP status/update 行の最大文字数。
- `stream.tagVisibility`: ストリーミングイベント用のタグ名から boolean 可視性オーバーライドへの記録。
- `runtime.ttlMinutes`: クリーンアップ対象になるまでの ACP session worker のアイドル TTL（分）。
- `runtime.installCommand`: ACP ランタイム環境をブートストラップするときに実行する任意の install コマンド。

---

## CLI

```json5
{
  cli: {
    banner: {
      taglineMode: "off", // random | default | off
    },
  },
}
```

- `cli.banner.taglineMode` はバナーのタグラインスタイルを制御します:
  - `"random"`（デフォルト）: ローテーションする面白い/季節限定タグライン。
  - `"default"`: 固定の中立タグライン（`All your chats, one OpenClaw.`）。
  - `"off"`: タグラインテキストなし（バナーのタイトル/バージョンは引き続き表示）。
- バナー全体を隠すには（タグラインだけでなく）、env `OPENCLAW_HIDE_BANNER=1` を設定してください。

---

## Wizard

CLI のガイド付きセットアップフロー（`onboard`、`configure`、`doctor`）によって書き込まれるメタデータ:

```json5
{
  wizard: {
    lastRunAt: "2026-01-01T00:00:00.000Z",
    lastRunVersion: "2026.1.4",
    lastRunCommit: "abc1234",
    lastRunCommand: "configure",
    lastRunMode: "local",
  },
}
```

---

## Identity

[Agent のデフォルト設定](#agent-defaults) の `agents.list` identity フィールドを参照してください。

---

## Bridge（legacy、削除済み）

現在のビルドには TCP bridge は含まれていません。Nodes は Gateway WebSocket 経由で接続します。`bridge.*` キーはもはや設定 schema の一部ではありません（削除するまで検証は失敗します。`openclaw doctor --fix` で不明キーを除去できます）。

<Accordion title="従来の bridge 設定（履歴リファレンス）">

```json
{
  "bridge": {
    "enabled": true,
    "port": 18790,
    "bind": "tailnet",
    "tls": {
      "enabled": true,
      "autoGenerate": true
    }
  }
}
```

</Accordion>

---

## Cron

```json5
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 2,
    webhook: "https://example.invalid/legacy", // 非推奨: 保存済み notify:true ジョブ用のフォールバック
    webhookToken: "replace-with-dedicated-token", // 任意: outbound webhook auth 用 bearer token
    sessionRetention: "24h", // duration 文字列または false
    runLog: {
      maxBytes: "2mb", // デフォルト 2_000_000 bytes
      keepLines: 2000, // デフォルト 2000
    },
  },
}
```

- `sessionRetention`: 完了済みの isolated cron 実行 session を `sessions.json` から pruning するまで保持する期間です。アーカイブされた削除済み cron transcript のクリーンアップも制御します。デフォルト: `24h`。無効にするには `false` を設定します。
- `runLog.maxBytes`: pruning 前の実行ログファイルごとの最大サイズ（`cron/runs/<jobId>.jsonl`）。デフォルト: `2_000_000` bytes。
- `runLog.keepLines`: 実行ログの pruning が発動したときに保持される最新行数。デフォルト: `2000`。
- `webhookToken`: cron webhook POST 配信（`delivery.mode = "webhook"`）に使う bearer token。省略した場合、auth ヘッダーは送信されません。
- `webhook`: 非推奨の従来フォールバック webhook URL（http/https）。まだ `notify: true` を持つ保存済みジョブにのみ使われます。

### `cron.retry`

```json5
{
  cron: {
    retry: {
      maxAttempts: 3,
      backoffMs: [30000, 60000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "timeout", "server_error"],
    },
  },
}
```

- `maxAttempts`: 一過性エラー時の one-shot ジョブに対する最大 retry 回数（デフォルト: `3`、範囲: `0`–`10`）。
- `backoffMs`: 各 retry 試行に対する backoff 遅延（ms）の配列（デフォルト: `[30000, 60000, 300000]`、1〜10 エントリ）。
- `retryOn`: retry を引き起こすエラー種別 — `"rate_limit"`、`"overloaded"`、`"network"`、`"timeout"`、`"server_error"`。省略した場合、すべての一過性エラー種別を retry します。

これは one-shot cron ジョブにのみ適用されます。定期ジョブでは別の失敗処理が使われます。

### `cron.failureAlert`

```json5
{
  cron: {
    failureAlert: {
      enabled: false,
      after: 3,
      cooldownMs: 3600000,
      mode: "announce",
      accountId: "main",
    },
  },
}
```

- `enabled`: cron ジョブの失敗アラートを有効にします（デフォルト: `false`）。
- `after`: アラート発火までの連続失敗回数（正の整数、最小: `1`）。
- `cooldownMs`: 同じジョブに対して繰り返しアラートを出すまでの最小間隔（ミリ秒）（非負整数）。
- `mode`: 配信モード — `"announce"` は channel メッセージで送信し、`"webhook"` は設定済み webhook に POST します。
- `accountId`: アラート配信のスコープを絞る任意の account または channel id。

### `cron.failureDestination`

```json5
{
  cron: {
    failureDestination: {
      mode: "announce",
      channel: "last",
      to: "channel:C1234567890",
      accountId: "main",
    },
  },
}
```

- すべてのジョブに共通する、cron 失敗通知のデフォルト送信先です。
- `mode`: `"announce"` または `"webhook"`。十分なターゲットデータが存在する場合、デフォルトは `"announce"` です。
- `channel`: announce 配信用の channel オーバーライド。`"last"` は最後に使われた配信 channel を再利用します。
- `to`: 明示的な announce ターゲットまたは webhook URL。webhook mode では必須です。
- `accountId`: 配信用の任意の account オーバーライド。
- ジョブごとの `delivery.failureDestination` はこのグローバルデフォルトを上書きします。
- グローバルにもジョブごとにも失敗送信先が設定されていない場合、すでに `announce` で配信するジョブは、失敗時にそのプライマリ announce ターゲットへフォールバックします。
- `delivery.failureDestination` は、ジョブのプライマリ `delivery.mode` が `"webhook"` の場合を除き、`sessionTarget="isolated"` ジョブでのみサポートされます。

[Cron Jobs](/ja-JP/automation/cron-jobs) を参照してください。isolated cron 実行は [background tasks](/ja-JP/automation/tasks) として追跡されます。

---

## Media model テンプレート変数

`tools.media.models[].args` で展開されるテンプレートプレースホルダー:

| 変数               | 説明                                      |
| ------------------ | ----------------------------------------- |
| `{{Body}}`         | 受信メッセージ本文全体                    |
| `{{RawBody}}`      | 生の本文（履歴/送信者ラッパーなし）       |
| `{{BodyStripped}}` | グループメンションを除去した本文          |
| `{{From}}`         | 送信者識別子                              |
| `{{To}}`           | 宛先識別子                                |
| `{{MessageSid}}`   | channel メッセージ id                     |
| `{{SessionId}}`    | 現在の session UUID                       |
| `{{IsNewSession}}` | 新しい session が作成された場合 `"true"`  |
| `{{MediaUrl}}`     | 受信 media の擬似 URL                     |
| `{{MediaPath}}`    | ローカル media パス                       |
| `{{MediaType}}`    | media タイプ（image/audio/document/…）    |
| `{{Transcript}}`   | 音声 transcript                           |
| `{{Prompt}}`       | CLI エントリ用に解決された media prompt   |
| `{{MaxChars}}`     | CLI エントリ用に解決された最大出力文字数  |
| `{{ChatType}}`     | `"direct"` または `"group"`               |
| `{{GroupSubject}}` | グループ件名（ベストエフォート）          |
| `{{GroupMembers}}` | グループメンバーのプレビュー（ベストエフォート） |
| `{{SenderName}}`   | 送信者表示名（ベストエフォート）          |
| `{{SenderE164}}`   | 送信者電話番号（ベストエフォート）        |
| `{{Provider}}`     | provider ヒント（whatsapp、telegram、discord など） |

---

## Config include（`$include`）

設定を複数ファイルに分割できます:

```json5
// ~/.openclaw/openclaw.json
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
  broadcast: {
    $include: ["./clients/mueller.json5", "./clients/schmidt.json5"],
  },
}
```

**マージ動作:**

- 単一ファイル: そのオブジェクト全体を置き換えます。
- ファイル配列: 順番に deep merge されます（後ろのものが前を上書き）。
- 同階層キー: include の後にマージされます（include された値を上書き）。
- ネストした include: 最大 10 レベル。
- パス: include 元ファイルからの相対で解決されますが、トップレベル設定ディレクトリ（`openclaw.json` の `dirname`）内に収まっている必要があります。絶対パスや `../` 形式も、最終的にその境界内に解決される場合にのみ許可されます。
- エラー: 欠落ファイル、解析エラー、循環 include に対して明確なメッセージが出ます。

---

_関連: [Configuration](/ja-JP/gateway/configuration) · [Configuration Examples](/ja-JP/gateway/configuration-examples) · [Doctor](/ja-JP/gateway/doctor)_
