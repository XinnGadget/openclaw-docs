---
read_when:
    - グループチャットの動作やメンションゲーティングを変更する場合
summary: 各サーフェス（Discord/iMessage/Matrix/Microsoft Teams/Signal/Slack/Telegram/WhatsApp/Zalo）にまたがるグループチャットの動作
title: グループ
x-i18n:
    generated_at: "2026-04-07T04:41:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 83d20f2958ed6ad3354f0078553b3c6a38643ea8ef38573c40e89ebef2fa8421
    source_path: channels/groups.md
    workflow: 15
---

# グループ

OpenClaw は、Discord、iMessage、Matrix、Microsoft Teams、Signal、Slack、Telegram、WhatsApp、Zalo などの各サーフェスで、グループチャットを一貫して扱います。

## 初心者向けイントロ（2分）

OpenClaw はあなた自身のメッセージングアカウント上で「動作」します。別個の WhatsApp ボットユーザーは存在しません。
**あなた** がグループに参加していれば、OpenClaw はそのグループを確認でき、そこで応答できます。

デフォルトの動作:

- グループは制限されています（`groupPolicy: "allowlist"`）。
- 明示的にメンションゲーティングを無効にしない限り、応答にはメンションが必要です。

つまり、allowlist に登録された送信者は、OpenClaw にメンションすることでトリガーできます。

> 要点
>
> - **DM access** は `*.allowFrom` で制御されます。
> - **Group access** は `*.groupPolicy` + allowlist（`*.groups`, `*.groupAllowFrom`）で制御されます。
> - **Reply triggering** はメンションゲーティング（`requireMention`, `/activation`）で制御されます。

クイックフロー（グループメッセージで何が起こるか）:

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

## コンテキストの可視性と allowlist

グループの安全性には、2 つの異なる制御が関係します。

- **トリガー認可**: 誰がエージェントをトリガーできるか（`groupPolicy`, `groups`, `groupAllowFrom`, チャネル固有の allowlist）。
- **コンテキストの可視性**: どの補足コンテキストがモデルに注入されるか（返信テキスト、引用、スレッド履歴、転送メタデータ）。

デフォルトでは、OpenClaw は通常のチャット動作を優先し、コンテキストはほとんど受信したまま保持します。つまり、allowlist は主に誰がアクションをトリガーできるかを決めるものであり、引用や履歴スニペットすべてに対する普遍的なマスキング境界ではありません。

現在の動作はチャネルごとに異なります。

- すでに一部のチャネルでは、特定の経路で補足コンテキストに送信者ベースのフィルタリングを適用しています（たとえば Slack のスレッドシード、Matrix の返信/スレッド参照）。
- 他のチャネルでは、引用/返信/転送コンテキストが受信したまま渡されます。

ハードニングの方向性（予定）:

- `contextVisibility: "all"`（デフォルト）は現在の受信時そのままの動作を維持します。
- `contextVisibility: "allowlist"` は補足コンテキストを allowlist に登録された送信者に限定します。
- `contextVisibility: "allowlist_quote"` は `allowlist` に 1 つの明示的な引用/返信例外を加えたものです。

このハードニングモデルがすべてのチャネルで一貫して実装されるまでは、サーフェスごとの差異があることを前提にしてください。

![グループメッセージフロー](/images/groups-flow.svg)

次のようにしたい場合...

| 目的 | 設定するもの |
| -------------------------------------------- | ---------------------------------------------------------- |
| すべてのグループを許可しつつ、@mentions のときだけ応答する | `groups: { "*": { requireMention: true } }` |
| すべてのグループ応答を無効にする | `groupPolicy: "disabled"` |
| 特定のグループのみ | `groups: { "<group-id>": { ... } }`（`"*"` キーなし） |
| グループ内でトリガーできるのは自分だけ | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## セッションキー

- グループセッションは `agent:<agentId>:<channel>:group:<id>` のセッションキーを使用します（room/channel は `agent:<agentId>:<channel>:channel:<id>` を使用します）。
- Telegram のフォーラムトピックでは、各トピックが独自のセッションを持つように、グループ ID に `:topic:<threadId>` が追加されます。
- ダイレクトチャットはメインセッションを使用します（設定されていれば送信者ごと）。
- ハートビートはグループセッションではスキップされます。

<a id="pattern-personal-dms-public-groups-single-agent"></a>

## パターン: 個人 DM + 公開グループ（単一エージェント）

はい。あなたの「個人」トラフィックが **DM** で、「公開」トラフィックが **グループ** であるなら、これはうまく機能します。

理由: 単一エージェントモードでは、DM は通常 **メイン** セッションキー（`agent:main:main`）に入り、一方でグループは常に **非メイン** セッションキー（`agent:main:<channel>:group:<id>`）を使用します。`mode: "non-main"` でサンドボックスを有効にすると、それらのグループセッションは Docker 上で実行され、メインの DM セッションはホスト上に残ります。

これにより、1 つのエージェント「頭脳」（共有ワークスペース + メモリ）を維持しつつ、2 つの実行姿勢を持てます。

- **DMs**: フルツール（ホスト）
- **Groups**: サンドボックス + 制限付きツール（Docker）

> 本当に別々のワークスペース/人格（「個人」と「公開」を絶対に混在させたくない）が必要な場合は、2 つ目のエージェント + バインディングを使ってください。[Multi-Agent Routing](/ja-JP/concepts/multi-agent) を参照してください。

例（DM はホスト、グループはサンドボックス化 + メッセージング専用ツール）:

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // groups/channels are non-main -> sandboxed
        scope: "session", // strongest isolation (one container per group/channel)
        workspaceAccess: "none",
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        // If allow is non-empty, everything else is blocked (deny still wins).
        allow: ["group:messaging", "group:sessions"],
        deny: ["group:runtime", "group:fs", "group:ui", "nodes", "cron", "gateway"],
      },
    },
  },
}
```

「ホストアクセスなし」ではなく「グループはフォルダー X のみ見られる」にしたい場合は、`workspaceAccess: "none"` を維持しつつ、allowlist に登録したパスだけをサンドボックスにマウントします。

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
        docker: {
          binds: [
            // hostPath:containerPath:mode
            "/home/user/FriendsShared:/data:ro",
          ],
        },
      },
    },
  },
}
```

関連:

- 設定キーとデフォルト: [Gateway configuration](/ja-JP/gateway/configuration-reference#agentsdefaultssandbox)
- なぜツールがブロックされているかをデバッグする: [Sandbox vs Tool Policy vs Elevated](/ja-JP/gateway/sandbox-vs-tool-policy-vs-elevated)
- バインドマウントの詳細: [Sandboxing](/ja-JP/gateway/sandboxing#custom-bind-mounts)

## 表示ラベル

- UI ラベルは、利用可能な場合 `displayName` を使い、`<channel>:<token>` の形式で表示されます。
- `#room` は room/channel 用に予約されています。グループチャットは `g-<slug>` を使用します（小文字、スペースは `-` に変換し、`#@+._-` は維持します）。

## グループポリシー

チャネルごとに、グループ/room メッセージをどのように扱うかを制御します。

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "disabled", // "open" | "disabled" | "allowlist"
      groupAllowFrom: ["+15551234567"],
    },
    telegram: {
      groupPolicy: "disabled",
      groupAllowFrom: ["123456789"], // numeric Telegram user id (wizard can resolve @username)
    },
    signal: {
      groupPolicy: "disabled",
      groupAllowFrom: ["+15551234567"],
    },
    imessage: {
      groupPolicy: "disabled",
      groupAllowFrom: ["chat_id:123"],
    },
    msteams: {
      groupPolicy: "disabled",
      groupAllowFrom: ["user@org.com"],
    },
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        GUILD_ID: { channels: { help: { allow: true } } },
      },
    },
    slack: {
      groupPolicy: "allowlist",
      channels: { "#general": { allow: true } },
    },
    matrix: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["@owner:example.org"],
      groups: {
        "!roomId:example.org": { enabled: true },
        "#alias:example.org": { enabled: true },
      },
    },
  },
}
```

| ポリシー | 動作 |
| ------------- | ------------------------------------------------------------ |
| `"open"` | グループは allowlist をバイパスします。メンションゲーティングは引き続き適用されます。 |
| `"disabled"` | すべてのグループメッセージを完全にブロックします。 |
| `"allowlist"` | 設定された allowlist に一致するグループ/room のみ許可します。 |

注:

- `groupPolicy` はメンションゲーティング（@mentions を要求するもの）とは別です。
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams/Zalo: `groupAllowFrom` を使用します（フォールバック: 明示的な `allowFrom`）。
- DM ペアリング承認（`*-allowFrom` ストアエントリ）は DM access にのみ適用されます。グループ送信者認可は、引き続きグループ allowlist に明示的に指定する必要があります。
- Discord: allowlist は `channels.discord.guilds.<id>.channels` を使用します。
- Slack: allowlist は `channels.slack.channels` を使用します。
- Matrix: allowlist は `channels.matrix.groups` を使用します。room ID または alias を優先してください。参加済み room 名の参照はベストエフォートで、解決できない名前は実行時に無視されます。送信者を制限するには `channels.matrix.groupAllowFrom` を使用します。room ごとの `users` allowlist もサポートされています。
- グループ DM は別個に制御されます（`channels.discord.dm.*`, `channels.slack.dm.*`）。
- Telegram の allowlist はユーザー ID（`"123456789"`, `"telegram:123456789"`, `"tg:123456789"`）またはユーザー名（`"@alice"` または `"alice"`）に一致できます。プレフィックスは大文字小文字を区別しません。
- デフォルトは `groupPolicy: "allowlist"` です。グループ allowlist が空の場合、グループメッセージはブロックされます。
- ランタイム安全性: プロバイダーのブロックが完全に欠けている場合（`channels.<provider>` が存在しない場合）、グループポリシーは `channels.defaults.groupPolicy` を継承せず、フェイルクローズドモード（通常は `allowlist`）にフォールバックします。

クイックな考え方（グループメッセージの評価順序）:

1. `groupPolicy`（open/disabled/allowlist）
2. グループ allowlist（`*.groups`, `*.groupAllowFrom`, チャネル固有の allowlist）
3. メンションゲーティング（`requireMention`, `/activation`）

## メンションゲーティング（デフォルト）

グループメッセージは、グループごとに上書きされない限り、メンションが必要です。デフォルトはサブシステムごとに `*.groups."*"` の下にあります。

ボットメッセージへの返信は、暗黙のメンションとして扱われます（チャネルが返信メタデータをサポートしている場合）。これは Telegram、WhatsApp、Slack、Discord、Microsoft Teams に適用されます。

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
        "123@g.us": { requireMention: false },
      },
    },
    telegram: {
      groups: {
        "*": { requireMention: true },
        "123456789": { requireMention: false },
      },
    },
    imessage: {
      groups: {
        "*": { requireMention: true },
        "123": { requireMention: false },
      },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          mentionPatterns: ["@openclaw", "openclaw", "\\+15555550123"],
          historyLimit: 50,
        },
      },
    ],
  },
}
```

注:

- `mentionPatterns` は大文字小文字を区別しない安全な正規表現パターンです。無効なパターンや安全でないネストした繰り返し形式は無視されます。
- 明示的なメンションを提供するサーフェスでは、それが引き続き通ります。パターンはフォールバックです。
- エージェントごとの上書き: `agents.list[].groupChat.mentionPatterns`（複数のエージェントが 1 つのグループを共有する場合に有用です）。
- メンション検出が可能な場合（ネイティブメンションがある、または `mentionPatterns` が設定されている場合）にのみ、メンションゲーティングが適用されます。
- Discord のデフォルトは `channels.discord.guilds."*"` にあります（guild/channel ごとに上書き可能）。
- グループ履歴コンテキストはチャネル間で統一された形でラップされ、**保留中のみ**（メンションゲーティングによりスキップされたメッセージ）です。グローバルデフォルトには `messages.groupChat.historyLimit`、上書きには `channels.<channel>.historyLimit`（または `channels.<channel>.accounts.*.historyLimit`）を使用します。無効にするには `0` を設定します。

## グループ/channel のツール制限（任意）

一部のチャネル設定では、**特定の group/room/channel 内で** 利用可能なツールを制限できます。

- `tools`: グループ全体のツール許可/拒否。
- `toolsBySender`: グループ内の送信者ごとの上書き。
  明示的なキープレフィックスを使用してください:
  `id:<senderId>`, `e164:<phone>`, `username:<handle>`, `name:<displayName>`, および `"*"` ワイルドカード。
  従来のプレフィックスなしキーも引き続き受け付けられますが、`id:` のみとして一致します。

解決順序（より具体的なものが優先）:

1. group/channel の `toolsBySender` 一致
2. group/channel の `tools`
3. デフォルト（`"*"`）の `toolsBySender` 一致
4. デフォルト（`"*"`）の `tools`

例（Telegram）:

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { tools: { deny: ["exec"] } },
        "-1001234567890": {
          tools: { deny: ["exec", "read", "write"] },
          toolsBySender: {
            "id:123456789": { alsoAllow: ["exec"] },
          },
        },
      },
    },
  },
}
```

注:

- グループ/channel のツール制限は、グローバル/エージェントのツールポリシーに加えて適用されます（deny が引き続き優先されます）。
- 一部のチャネルでは、room/channel に異なるネストが使われます（例: Discord の `guilds.*.channels.*`、Slack の `channels.*`、Microsoft Teams の `teams.*.channels.*`）。

## グループ allowlist

`channels.whatsapp.groups`、`channels.telegram.groups`、または `channels.imessage.groups` が設定されている場合、それらのキーはグループ allowlist として機能します。すべてのグループを許可しつつ、デフォルトのメンション動作も設定するには `"*"` を使用します。

よくある混乱: DM ペアリング承認は、グループ認可と同じではありません。
DM ペアリングをサポートするチャネルでは、ペアリングストアは DM のみを解放します。グループコマンドには、`groupAllowFrom` やそのチャネルで文書化されている設定フォールバックなど、設定 allowlist からの明示的なグループ送信者認可が引き続き必要です。

よくある意図（コピー＆ペースト用）:

1. すべてのグループ応答を無効にする

```json5
{
  channels: { whatsapp: { groupPolicy: "disabled" } },
}
```

2. 特定のグループのみ許可する（WhatsApp）

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "123@g.us": { requireMention: true },
        "456@g.us": { requireMention: false },
      },
    },
  },
}
```

3. すべてのグループを許可するが、メンションを必須にする（明示的）

```json5
{
  channels: {
    whatsapp: {
      groups: { "*": { requireMention: true } },
    },
  },
}
```

4. グループ内でトリガーできるのは owner のみ（WhatsApp）

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
      groups: { "*": { requireMention: true } },
    },
  },
}
```

## Activation（owner のみ）

グループ owner は、グループごとの activation を切り替えられます。

- `/activation mention`
- `/activation always`

owner は `channels.whatsapp.allowFrom` によって決定されます（未設定の場合はボット自身の E.164）。このコマンドは単独のメッセージとして送信してください。現在、他のサーフェスは `/activation` を無視します。

## コンテキストフィールド

グループの受信ペイロードでは、次が設定されます。

- `ChatType=group`
- `GroupSubject`（判明している場合）
- `GroupMembers`（判明している場合）
- `WasMentioned`（メンションゲーティングの結果）
- Telegram のフォーラムトピックには `MessageThreadId` と `IsForum` も含まれます。

チャネル固有の注:

- BlueBubbles では、`GroupMembers` を設定する前に、名前のない macOS グループ参加者をローカル Contacts データベースから補完することを任意で行えます。これはデフォルトではオフで、通常のグループゲーティング通過後にのみ実行されます。

エージェントのシステムプロンプトには、新しいグループセッションの最初のターンでグループ向けイントロが含まれます。そこでは、人間らしく応答すること、Markdown テーブルを避けること、空行を最小限にすること、通常のチャットの間隔に従うこと、文字どおりの `\n` シーケンスを打たないことがモデルに注意喚起されます。

## iMessage の詳細

- ルーティングや allowlist では `chat_id:<id>` を優先してください。
- チャット一覧: `imsg chats --limit 20`
- グループ返信は常に同じ `chat_id` に戻ります。

## WhatsApp の詳細

WhatsApp 固有の動作（履歴注入、メンション処理の詳細）については、[Group messages](/ja-JP/channels/group-messages) を参照してください。
