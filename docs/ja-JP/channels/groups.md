---
read_when:
    - グループチャットの動作やメンションゲーティングを変更する場合
summary: 各サーフェス（Discord/iMessage/Matrix/Microsoft Teams/Signal/Slack/Telegram/WhatsApp/Zalo）におけるグループチャットの動作
title: グループ
x-i18n:
    generated_at: "2026-04-06T03:06:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8620de6f7f0b866bf43a307fdbec3399790f09f22a87703704b0522caba80b18
    source_path: channels/groups.md
    workflow: 15
---

# グループ

OpenClaw は、Discord、iMessage、Matrix、Microsoft Teams、Signal、Slack、Telegram、WhatsApp、Zalo の各サーフェスで、グループチャットを一貫して扱います。

## 初心者向けイントロ（2分）

OpenClaw は、あなた自身のメッセージングアカウント上で「動作」します。別個の WhatsApp ボットユーザーは存在しません。
**あなた** がグループに参加していれば、OpenClaw はそのグループを確認して、そこで応答できます。

デフォルトの動作:

- グループは制限されます（`groupPolicy: "allowlist"`）。
- 明示的にメンションゲーティングを無効にしない限り、返信にはメンションが必要です。

つまり、許可リストに登録された送信者は、OpenClaw にメンションすることでトリガーできます。

> 要点
>
> - **DM アクセス** は `*.allowFrom` によって制御されます。
> - **グループアクセス** は `*.groupPolicy` + 許可リスト（`*.groups`、`*.groupAllowFrom`）によって制御されます。
> - **返信のトリガー** はメンションゲーティング（`requireMention`、`/activation`）によって制御されます。

クイックフロー（グループメッセージで何が起こるか）:

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

## コンテキストの可視性と許可リスト

グループの安全性には、2 つの異なる制御が関わります。

- **トリガー認可**: 誰がエージェントをトリガーできるか（`groupPolicy`、`groups`、`groupAllowFrom`、チャネル固有の許可リスト）
- **コンテキストの可視性**: どの補足コンテキストがモデルに注入されるか（返信テキスト、引用、スレッド履歴、転送メタデータ）

デフォルトでは、OpenClaw は通常のチャット動作を優先し、コンテキストは主に受信したまま保持します。つまり、許可リストは主として誰がアクションをトリガーできるかを決定するものであり、あらゆる引用や履歴スニペットに対する普遍的なマスキング境界ではありません。

現在の動作はチャネルごとに異なります。

- 一部のチャネルでは、特定の経路で補足コンテキストに対する送信者ベースのフィルタリングがすでに適用されています（たとえば Slack のスレッドシーディング、Matrix の返信/スレッド参照）。
- 他のチャネルでは、引用/返信/転送コンテキストが受信したまま渡されます。

ハードニングの方向性（予定）:

- `contextVisibility: "all"`（デフォルト）は、現在の「受信したまま」の動作を維持します。
- `contextVisibility: "allowlist"` は、補足コンテキストを許可リスト登録済み送信者に絞り込みます。
- `contextVisibility: "allowlist_quote"` は、`allowlist` に加えて 1 つの明示的な引用/返信例外を含みます。

このハードニングモデルが各チャネルで一貫して実装されるまでは、サーフェスごとの差異があることを想定してください。

![グループメッセージフロー](/images/groups-flow.svg)

もし次のようにしたい場合...

| 目的                                         | 設定内容                                                   |
| -------------------------------------------- | ---------------------------------------------------------- |
| すべてのグループを許可しつつ、`@mention` 時のみ返信する | `groups: { "*": { requireMention: true } }`                |
| すべてのグループ返信を無効にする             | `groupPolicy: "disabled"`                                  |
| 特定のグループのみ許可する                   | `groups: { "<group-id>": { ... } }`（`"*"` キーなし）      |
| グループ内でトリガーできるのを自分だけにする | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## セッションキー

- グループセッションは `agent:<agentId>:<channel>:group:<id>` のセッションキーを使用します（ルーム/チャネルは `agent:<agentId>:<channel>:channel:<id>` を使用）。
- Telegram のフォーラムトピックでは、各トピックが独自セッションを持つように、グループ ID に `:topic:<threadId>` が追加されます。
- ダイレクトチャットはメインセッションを使用します（設定されていれば送信者ごと）。
- ハートビートはグループセッションではスキップされます。

<a id="pattern-personal-dms-public-groups-single-agent"></a>

## パターン: 個人 DM + 公開グループ（単一エージェント）

はい、これは「個人的」なトラフィックが **DM** で、「公開」トラフィックが **グループ** の場合にうまく機能します。

理由: 単一エージェントモードでは、DM は通常 **main** セッションキー（`agent:main:main`）に届き、グループは常に **非 main** セッションキー（`agent:main:<channel>:group:<id>`）を使用します。`mode: "non-main"` でサンドボックス化を有効にすると、それらのグループセッションは Docker 上で実行される一方、メインの DM セッションはホスト上に残ります。

これにより、1 つのエージェント「頭脳」（共有ワークスペース + メモリ）を維持しつつ、2 つの実行姿勢を持てます。

- **DM**: フルツール（ホスト）
- **グループ**: サンドボックス + 制限付きツール（Docker）

> ワークスペースやペルソナを本当に分離する必要がある場合（「個人」と「公開」を決して混在させたくない場合）は、2 つ目のエージェント + バインディングを使ってください。[Multi-Agent Routing](/ja-JP/concepts/multi-agent) を参照してください。

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

「ホストアクセスなし」ではなく「グループはフォルダー X のみ参照できる」にしたい場合は、`workspaceAccess: "none"` を維持したまま、許可リスト済みパスだけをサンドボックスにマウントします。

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

- 設定キーとデフォルト値: [Gateway configuration](/ja-JP/gateway/configuration-reference#agentsdefaultssandbox)
- ツールがブロックされる理由のデバッグ: [Sandbox vs Tool Policy vs Elevated](/ja-JP/gateway/sandbox-vs-tool-policy-vs-elevated)
- バインドマウントの詳細: [Sandboxing](/ja-JP/gateway/sandboxing#custom-bind-mounts)

## 表示ラベル

- UI ラベルは、利用可能な場合は `displayName` を使用し、`<channel>:<token>` 形式で表示されます。
- `#room` はルーム/チャネル専用です。グループチャットは `g-<slug>` を使用します（小文字、スペースは `-` に変換、`#@+._-` は保持）。

## グループポリシー

チャネルごとにグループ/ルームメッセージをどのように扱うかを制御します。

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
        "!roomId:example.org": { allow: true },
        "#alias:example.org": { allow: true },
      },
    },
  },
}
```

| ポリシー      | 動作                                                         |
| ------------- | ------------------------------------------------------------ |
| `"open"`      | グループは許可リストをバイパスします。メンションゲーティングは引き続き適用されます。 |
| `"disabled"`  | すべてのグループメッセージを完全にブロックします。           |
| `"allowlist"` | 設定済みの許可リストに一致するグループ/ルームのみ許可します。 |

注記:

- `groupPolicy` はメンションゲーティング（@mention を必須にするもの）とは別です。
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams/Zalo: `groupAllowFrom` を使用します（フォールバック: 明示的な `allowFrom`）。
- DM ペアリング承認（`*-allowFrom` ストアのエントリー）は DM アクセスのみに適用されます。グループ送信者の認可は、グループ許可リストに対して明示的なままです。
- Discord: 許可リストは `channels.discord.guilds.<id>.channels` を使用します。
- Slack: 許可リストは `channels.slack.channels` を使用します。
- Matrix: 許可リストは `channels.matrix.groups` を使用します。ルーム ID またはエイリアスを推奨します。参加済みルーム名の参照はベストエフォートであり、解決できない名前は実行時に無視されます。送信者を制限するには `channels.matrix.groupAllowFrom` を使用してください。ルームごとの `users` 許可リストもサポートされています。
- グループ DM は別途制御されます（`channels.discord.dm.*`、`channels.slack.dm.*`）。
- Telegram の許可リストは、ユーザー ID（`"123456789"`、`"telegram:123456789"`、`"tg:123456789"`）またはユーザー名（`"@alice"` または `"alice"`）に一致できます。プレフィックスは大文字小文字を区別しません。
- デフォルトは `groupPolicy: "allowlist"` です。グループ許可リストが空の場合、グループメッセージはブロックされます。
- ランタイム安全性: プロバイダーブロックが完全に欠落している場合（`channels.<provider>` が存在しない場合）、グループポリシーは `channels.defaults.groupPolicy` を継承するのではなく、フェイルクローズドモード（通常は `allowlist`）にフォールバックします。

クイックメンタルモデル（グループメッセージの評価順）:

1. `groupPolicy`（open/disabled/allowlist）
2. グループ許可リスト（`*.groups`、`*.groupAllowFrom`、チャネル固有の許可リスト）
3. メンションゲーティング（`requireMention`、`/activation`）

## メンションゲーティング（デフォルト）

グループメッセージは、グループごとに上書きされない限り、メンションを必要とします。デフォルト値は各サブシステムの `*.groups."*"` にあります。

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

注記:

- `mentionPatterns` は大文字小文字を区別しない安全な regex パターンです。無効なパターンや、安全でないネスト反復形式は無視されます。
- 明示的なメンションを提供するサーフェスは引き続き通過します。パターンはフォールバックです。
- エージェントごとの上書き: `agents.list[].groupChat.mentionPatterns`（複数のエージェントが同じグループを共有する場合に有用）。
- メンションゲーティングは、メンション検出が可能な場合にのみ強制されます（ネイティブメンション、または `mentionPatterns` が設定されている場合）。
- Discord のデフォルト値は `channels.discord.guilds."*"` にあります（ギルド/チャネルごとに上書き可能）。
- グループ履歴コンテキストはチャネル間で統一的にラップされ、**保留中のみ** です（メンションゲーティングによりスキップされたメッセージ）。グローバルデフォルトには `messages.groupChat.historyLimit` を使用し、上書きには `channels.<channel>.historyLimit`（または `channels.<channel>.accounts.*.historyLimit`）を使用します。無効にするには `0` を設定します。

## グループ/チャネルのツール制限（オプション）

一部のチャネル設定では、**特定のグループ/ルーム/チャネル内** で利用可能なツールを制限できます。

- `tools`: グループ全体に対してツールを許可/拒否します。
- `toolsBySender`: グループ内の送信者ごとの上書きです。
  明示的なキープレフィックスを使用してください:
  `id:<senderId>`、`e164:<phone>`、`username:<handle>`、`name:<displayName>`、および `"*"` ワイルドカード。
  従来のプレフィックスなしキーも引き続き受け付けられ、`id:` のみとして照合されます。

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

注記:

- グループ/チャネルのツール制限は、グローバル/エージェントのツールポリシーに加えて適用されます（deny が引き続き優先されます）。
- 一部のチャネルでは、ルーム/チャネルに異なるネスト構造を使用します（例: Discord `guilds.*.channels.*`、Slack `channels.*`、Microsoft Teams `teams.*.channels.*`）。

## グループ許可リスト

`channels.whatsapp.groups`、`channels.telegram.groups`、または `channels.imessage.groups` が設定されている場合、それらのキーはグループ許可リストとして機能します。すべてのグループを許可しつつ、デフォルトのメンション動作を設定したい場合は `"*"` を使用してください。

よくある混乱: DM のペアリング承認は、グループ認可と同じではありません。
DM ペアリングをサポートするチャネルでは、ペアリングストアは DM のみを解放します。グループコマンドには依然として、`groupAllowFrom` などの設定許可リスト、またはそのチャネルで文書化された設定フォールバックによる、明示的なグループ送信者認可が必要です。

よくある意図（コピー&ペースト）:

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

3. すべてのグループを許可しつつ、メンションを必須にする（明示的）

```json5
{
  channels: {
    whatsapp: {
      groups: { "*": { requireMention: true } },
    },
  },
}
```

4. グループ内でトリガーできるのをオーナーだけにする（WhatsApp）

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

グループオーナーは、グループごとの activation を切り替えできます。

- `/activation mention`
- `/activation always`

オーナーは `channels.whatsapp.allowFrom` によって判定されます（未設定時はボット自身の E.164）。コマンドは単独メッセージとして送信してください。他のサーフェスは現在 `/activation` を無視します。

## コンテキストフィールド

グループ受信ペイロードでは次が設定されます。

- `ChatType=group`
- `GroupSubject`（既知の場合）
- `GroupMembers`（既知の場合）
- `WasMentioned`（メンションゲーティング結果）
- Telegram のフォーラムトピックには、`MessageThreadId` と `IsForum` も含まれます。

チャネル固有の注記:

- BlueBubbles は、`GroupMembers` を設定する前に、名前のない macOS グループ参加者をローカル Contacts データベースから補完することを任意で行えます。これはデフォルトで無効であり、通常のグループゲーティングを通過した後にのみ実行されます。

エージェントのシステムプロンプトには、新しいグループセッションの最初のターンでグループ向けイントロが含まれます。これは、モデルに対して人間らしく応答すること、Markdown テーブルを避けること、空行を最小限にすること、通常のチャット間隔に従うこと、そして文字どおりの `\n` シーケンスを入力しないことを促します。

## iMessage 固有事項

- ルーティングや許可リストでは `chat_id:<id>` を優先してください。
- チャット一覧: `imsg chats --limit 20`
- グループ返信は常に同じ `chat_id` に返されます。

## WhatsApp 固有事項

WhatsApp 専用の動作（履歴注入、メンション処理の詳細）については、[Group messages](/ja-JP/channels/group-messages) を参照してください。
