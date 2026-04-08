---
read_when:
    - グループチャットの動作やメンションゲーティングを変更する場合
summary: 各サーフェス（Discord/iMessage/Matrix/Microsoft Teams/Signal/Slack/Telegram/WhatsApp/Zalo）にわたるグループチャットの動作
title: グループ
x-i18n:
    generated_at: "2026-04-08T02:14:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: f5045badbba30587c8f1bf27f6b940c7c471a95c57093c9adb142374413ac81e
    source_path: channels/groups.md
    workflow: 15
---

# グループ

OpenClaw は、Discord、iMessage、Matrix、Microsoft Teams、Signal、Slack、Telegram、WhatsApp、Zalo の各サーフェスでグループチャットを一貫して扱います。

## 初心者向けイントロ（2分）

OpenClaw はあなた自身のメッセージングアカウント上で「動作」します。別個の WhatsApp ボットユーザーは存在しません。
**あなた** がグループに参加していれば、OpenClaw はそのグループを確認でき、そこで応答できます。

デフォルトの動作:

- グループは制限されています（`groupPolicy: "allowlist"`）。
- 明示的にメンションゲーティングを無効にしない限り、返信にはメンションが必要です。

つまり、allowlist に登録された送信者は、OpenClaw にメンションすることでトリガーできます。

> 要点
>
> - **DM アクセス** は `*.allowFrom` で制御されます。
> - **グループアクセス** は `*.groupPolicy` と allowlist（`*.groups`、`*.groupAllowFrom`）で制御されます。
> - **返信のトリガー** はメンションゲーティング（`requireMention`、`/activation`）で制御されます。

クイックフロー（グループメッセージで何が起こるか）:

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

## コンテキストの可視性と allowlist

グループの安全性には、2 つの異なる制御が関係します。

- **トリガー認可**: 誰がエージェントをトリガーできるか（`groupPolicy`、`groups`、`groupAllowFrom`、チャネル固有の allowlist）。
- **コンテキストの可視性**: どの補足コンテキストがモデルに注入されるか（返信テキスト、引用、スレッド履歴、転送メタデータ）。

デフォルトでは、OpenClaw は通常のチャット動作を優先し、コンテキストはほぼ受信したまま保持します。これは、allowlist が主に誰がアクションをトリガーできるかを決定するものであり、あらゆる引用や履歴断片に対する普遍的なマスキング境界ではないことを意味します。

現在の動作はチャネルごとに異なります。

- 一部のチャネルでは、特定の経路で補足コンテキストに対して送信者ベースのフィルタリングがすでに適用されています（たとえば Slack のスレッドシード、Matrix の返信/スレッド参照）。
- 他のチャネルでは、引用/返信/転送コンテキストが受信したまま渡されます。

ハードニングの方向性（予定）:

- `contextVisibility: "all"`（デフォルト）は、現在の受信したままの動作を維持します。
- `contextVisibility: "allowlist"` は、補足コンテキストを allowlist に登録された送信者に絞り込みます。
- `contextVisibility: "allowlist_quote"` は、`allowlist` に 1 つの明示的な引用/返信例外を加えたものです。

このハードニングモデルが各チャネルで一貫して実装されるまでは、サーフェスごとの差異があると考えてください。

![グループメッセージフロー](/images/groups-flow.svg)

もし次のようにしたい場合…

| 目的 | 設定内容 |
| -------------------------------------------- | ---------------------------------------------------------- |
| すべてのグループを許可しつつ、`@mentions` のときだけ返信する | `groups: { "*": { requireMention: true } }`                |
| すべてのグループ返信を無効にする | `groupPolicy: "disabled"`                                  |
| 特定のグループのみ | `groups: { "<group-id>": { ... } }` (`"*"` キーなし)         |
| グループ内でトリガーできるのは自分だけ | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## セッションキー

- グループセッションは `agent:<agentId>:<channel>:group:<id>` セッションキーを使用します（ルーム/チャネルは `agent:<agentId>:<channel>:channel:<id>` を使用します）。
- Telegram のフォーラムトピックでは、各トピックが独自のセッションを持つように、グループ ID に `:topic:<threadId>` が追加されます。
- ダイレクトチャットはメインセッション（または、設定されている場合は送信者ごとのセッション）を使用します。
- ハートビートはグループセッションではスキップされます。

<a id="pattern-personal-dms-public-groups-single-agent"></a>

## パターン: 個人 DM + 公開グループ（単一エージェント）

はい。あなたの「個人」トラフィックが **DM** で、「公開」トラフィックが **グループ** なら、これはうまく機能します。

理由: 単一エージェントモードでは、DM は通常 **メイン** セッションキー（`agent:main:main`）に入り、グループは常に **非メイン** セッションキー（`agent:main:<channel>:group:<id>`）を使用します。`mode: "non-main"` でサンドボックス化を有効にすると、それらのグループセッションは Docker 内で実行され、メインの DM セッションはホスト上に残ります。

これにより、1 つのエージェント「頭脳」（共有ワークスペース + メモリ）を維持しつつ、2 つの実行姿勢を持てます。

- **DM**: フルツール（ホスト）
- **グループ**: サンドボックス + 制限付きツール（Docker）

> 本当に分離されたワークスペース/ペルソナ（「個人」と「公開」を決して混在させてはいけない）が必要な場合は、2 つ目のエージェント + バインディングを使用してください。[Multi-Agent Routing](/ja-JP/concepts/multi-agent) を参照してください。

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

「ホストアクセスなし」ではなく「グループはフォルダー X だけ見られる」にしたい場合は、`workspaceAccess: "none"` を維持しつつ、allowlist に登録されたパスだけをサンドボックスにマウントしてください。

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
- ツールがブロックされる理由のデバッグ: [Sandbox vs Tool Policy vs Elevated](/ja-JP/gateway/sandbox-vs-tool-policy-vs-elevated)
- バインドマウントの詳細: [Sandboxing](/ja-JP/gateway/sandboxing#custom-bind-mounts)

## 表示ラベル

- UI ラベルは、利用可能な場合 `displayName` を使用し、`<channel>:<token>` 形式で表示されます。
- `#room` はルーム/チャネル用に予約されています。グループチャットは `g-<slug>` を使用します（小文字、スペースは `-` に変換し、`#@+._-` は維持します）。

## グループポリシー

チャネルごとに、グループ/ルームメッセージをどのように扱うかを制御します。

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
| `"open"`      | グループは allowlist をバイパスします。メンションゲーティングは引き続き適用されます。      |
| `"disabled"`  | すべてのグループメッセージを完全にブロックします。                           |
| `"allowlist"` | 設定された allowlist に一致するグループ/ルームのみを許可します。 |

注意:

- `groupPolicy` はメンションゲーティング（@mentions を要求するもの）とは別です。
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams/Zalo: `groupAllowFrom` を使用します（フォールバック: 明示的な `allowFrom`）。
- DM ペアリング承認（`*-allowFrom` ストアエントリ）は DM アクセスにのみ適用されます。グループ送信者の認可は、グループ allowlist に対して明示的なままです。
- Discord: allowlist は `channels.discord.guilds.<id>.channels` を使用します。
- Slack: allowlist は `channels.slack.channels` を使用します。
- Matrix: allowlist は `channels.matrix.groups` を使用します。ルーム ID またはエイリアスを優先してください。参加済みルーム名の参照はベストエフォートで、解決できない名前は実行時に無視されます。送信者を制限するには `channels.matrix.groupAllowFrom` を使用します。ルーム単位の `users` allowlist もサポートされています。
- グループ DM は別途制御されます（`channels.discord.dm.*`、`channels.slack.dm.*`）。
- Telegram の allowlist はユーザー ID（`"123456789"`、`"telegram:123456789"`、`"tg:123456789"`）またはユーザー名（`"@alice"` または `"alice"`）に一致できます。プレフィックスは大文字/小文字を区別しません。
- デフォルトは `groupPolicy: "allowlist"` です。グループ allowlist が空の場合、グループメッセージはブロックされます。
- ランタイム安全性: プロバイダーブロック全体が完全に欠落している場合（`channels.<provider>` が存在しない場合）、グループポリシーは `channels.defaults.groupPolicy` を継承せず、フェイルクローズドモード（通常は `allowlist`）にフォールバックします。

クイックメンタルモデル（グループメッセージの評価順序）:

1. `groupPolicy`（open/disabled/allowlist）
2. グループ allowlist（`*.groups`、`*.groupAllowFrom`、チャネル固有の allowlist）
3. メンションゲーティング（`requireMention`、`/activation`）

## メンションゲーティング（デフォルト）

グループメッセージは、グループごとに上書きしない限り、メンションを必要とします。デフォルトは各サブシステムの `*.groups."*"` 配下にあります。

チャネルが返信メタデータをサポートしている場合、ボットメッセージへの返信は暗黙のメンションとして扱われます。
引用メタデータを公開するチャネルでは、ボットメッセージの引用も暗黙の
メンションとして扱われることがあります。現在の組み込みケースには
Telegram、WhatsApp、Slack、Discord、Microsoft Teams、ZaloUser が含まれます。

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

注意:

- `mentionPatterns` は大文字/小文字を区別しない安全な正規表現パターンです。無効なパターンや、安全でないネストされた反復形式は無視されます。
- 明示的なメンションを提供するサーフェスは、そのまま通過します。パターンはフォールバックです。
- エージェント単位の上書き: `agents.list[].groupChat.mentionPatterns`（複数のエージェントが同じグループを共有する場合に便利です）。
- メンションゲーティングは、メンション検出が可能な場合にのみ適用されます（ネイティブメンション、または `mentionPatterns` が設定されている場合）。
- Discord のデフォルトは `channels.discord.guilds."*"` 配下にあります（guild/channel ごとに上書き可能）。
- グループ履歴コンテキストは、チャネル間で一貫した形でラップされ、**保留中のみ** です（メンションゲーティングのためにスキップされたメッセージ）。グローバルデフォルトには `messages.groupChat.historyLimit` を使用し、上書きには `channels.<channel>.historyLimit`（または `channels.<channel>.accounts.*.historyLimit`）を使用します。無効にするには `0` を設定します。

## グループ/チャネルのツール制限（任意）

一部のチャネル設定では、**特定のグループ/ルーム/チャネル内** で利用できるツールを制限できます。

- `tools`: グループ全体に対するツールの許可/拒否。
- `toolsBySender`: グループ内の送信者ごとの上書き。
  明示的なキープレフィックスを使用します:
  `id:<senderId>`、`e164:<phone>`、`username:<handle>`、`name:<displayName>`、および `"*"` ワイルドカード。
  従来のプレフィックスなしキーも引き続き受け付けられ、`id:` のみとして一致します。

解決順序（最も具体的なものが優先）:

1. グループ/チャネルの `toolsBySender` 一致
2. グループ/チャネルの `tools`
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

注意:

- グループ/チャネルのツール制限は、グローバル/エージェントのツールポリシーに加えて適用されます（deny が引き続き優先されます）。
- チャネルによって、ルーム/チャネルに異なるネストを使用するものがあります（例: Discord `guilds.*.channels.*`、Slack `channels.*`、Microsoft Teams `teams.*.channels.*`）。

## グループ allowlist

`channels.whatsapp.groups`、`channels.telegram.groups`、または `channels.imessage.groups` が設定されている場合、それらのキーはグループ allowlist として機能します。すべてのグループを許可しつつデフォルトのメンション動作を設定したい場合は、`"*"` を使用してください。

よくある混乱: DM のペアリング承認は、グループ認可と同じではありません。
DM ペアリングをサポートするチャネルでは、ペアリングストアは DM のみを解放します。グループコマンドには、`groupAllowFrom` やそのチャネルで文書化されている設定フォールバックなど、設定 allowlist からの明示的なグループ送信者認可が引き続き必要です。

よくある意図（コピー/貼り付け用）:

1. すべてのグループ返信を無効にする

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

4. グループ内でトリガーできるのはオーナーだけ（WhatsApp）

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

## Activation（owner-only）

グループオーナーは、グループごとの activation を切り替えられます。

- `/activation mention`
- `/activation always`

オーナーは `channels.whatsapp.allowFrom`（未設定時はボット自身の E.164）によって判定されます。コマンドは単独のメッセージとして送信してください。現在、他のサーフェスでは `/activation` は無視されます。

## コンテキストフィールド

グループの受信ペイロードでは、次が設定されます。

- `ChatType=group`
- `GroupSubject`（わかっている場合）
- `GroupMembers`（わかっている場合）
- `WasMentioned`（メンションゲーティングの結果）
- Telegram のフォーラムトピックでは、`MessageThreadId` と `IsForum` も含まれます。

チャネル固有の注意:

- BlueBubbles は、`GroupMembers` を設定する前に、名前のない macOS グループ参加者をローカル Contacts データベースから任意で補完できます。これはデフォルトでオフであり、通常のグループゲーティングを通過した後にのみ実行されます。

エージェントのシステムプロンプトには、新しいグループセッションの最初のターンでグループ向けイントロが含まれます。これは、モデルに対して人間のように応答すること、Markdown テーブルを避けること、空行を最小限にすること、通常のチャット間隔に従うこと、そして文字どおりの `\n` シーケンスを入力しないことを促します。

## iMessage 固有事項

- ルーティングや allowlist には `chat_id:<id>` を優先してください。
- チャット一覧: `imsg chats --limit 20`
- グループ返信は常に同じ `chat_id` に返されます。

## WhatsApp 固有事項

WhatsApp 専用の動作（履歴注入、メンション処理の詳細）については、[Group messages](/ja-JP/channels/group-messages) を参照してください。
