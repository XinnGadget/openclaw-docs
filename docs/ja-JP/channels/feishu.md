---
read_when:
    - Feishu/Larkボットを接続したい場合
    - Feishuチャンネルを設定しています
summary: Feishuボットの概要、機能、および設定
title: Feishu
x-i18n:
    generated_at: "2026-04-13T12:36:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 77fcf95a3fab534ed898bc157d76bf8bdfa8bf8a918d6af84c0db19890916c1a
    source_path: channels/feishu.md
    workflow: 15
---

# Feishu / Lark

Feishu/Larkは、チームがチャット、ドキュメント共有、カレンダー管理を行い、共同で作業を進められるオールインワンのコラボレーションプラットフォームです。

**ステータス:** ボットのDMとグループチャット向けに本番利用可能です。デフォルトのモードはWebSocketで、webhookモードは任意です。

---

## クイックスタート

> **OpenClaw 2026.4.10 以降が必要です。** 確認するには `openclaw --version` を実行してください。アップグレードするには `openclaw update` を実行します。

<Steps>
  <Step title="チャンネル設定ウィザードを実行する">
  ```bash
  openclaw channels login --channel feishu
  ```
  Feishu/LarkモバイルアプリでQRコードをスキャンすると、Feishu/Larkボットが自動的に作成されます。
  </Step>
  
  <Step title="設定完了後、変更を適用するためにGatewayを再起動する">
  ```bash
  openclaw gateway restart
  ```
  </Step>
</Steps>

---

## アクセス制御

### ダイレクトメッセージ

ボットにDMを送信できるユーザーを制御するには、`dmPolicy` を設定します。

- `"pairing"` — 不明なユーザーにはペアリングコードが送られます。CLI経由で承認してください
- `"allowlist"` — `allowFrom` に記載されたユーザーのみがチャットできます（デフォルト: ボット所有者のみ）
- `"open"` — すべてのユーザーを許可します
- `"disabled"` — すべてのDMを無効にします

**ペアリングリクエストを承認するには:**

```bash
openclaw pairing list feishu
openclaw pairing approve feishu <CODE>
```

### グループチャット

**グループポリシー** (`channels.feishu.groupPolicy`):

| 値 | 動作 |
| ------------- | ------------------------------------------ |
| `"open"` | グループ内のすべてのメッセージに応答します |
| `"allowlist"` | `groupAllowFrom` 内のグループにのみ応答します |
| `"disabled"` | すべてのグループメッセージを無効にします |

デフォルト: `allowlist`

**メンション必須** (`channels.feishu.requireMention`):

- `true` — @メンションを必須にします（デフォルト）
- `false` — @メンションなしで応答します
- グループごとの上書き: `channels.feishu.groups.<chat_id>.requireMention`

---

## グループ設定の例

### すべてのグループを許可し、@メンションを不要にする

```json5
{
  channels: {
    feishu: {
      groupPolicy: "open",
    },
  },
}
```

### すべてのグループを許可し、@メンションは引き続き必須にする

```json5
{
  channels: {
    feishu: {
      groupPolicy: "open",
      requireMention: true,
    },
  },
}
```

### 特定のグループのみ許可する

```json5
{
  channels: {
    feishu: {
      groupPolicy: "allowlist",
      // グループIDの形式: oc_xxx
      groupAllowFrom: ["oc_xxx", "oc_yyy"],
    },
  },
}
```

### グループ内の送信者を制限する

```json5
{
  channels: {
    feishu: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["oc_xxx"],
      groups: {
        oc_xxx: {
          // ユーザーのopen_idの形式: ou_xxx
          allowFrom: ["ou_user1", "ou_user2"],
        },
      },
    },
  },
}
```

---

## グループID/ユーザーIDを取得する

### グループID (`chat_id`, 形式: `oc_xxx`)

Feishu/Larkでグループを開き、右上のメニューアイコンをクリックして **Settings** に進みます。設定ページにグループID (`chat_id`) が表示されます。

![Get Group ID](/images/feishu-get-group-id.png)

### ユーザーID (`open_id`, 形式: `ou_xxx`)

Gatewayを起動し、ボットにDMを送信してから、ログを確認します。

```bash
openclaw logs --follow
```

ログ出力内の `open_id` を探してください。保留中のペアリングリクエストを確認することもできます。

```bash
openclaw pairing list feishu
```

---

## よく使うコマンド

| コマンド | 説明 |
| --------- | --------------------------- |
| `/status` | ボットのステータスを表示します |
| `/reset` | 現在のセッションをリセットします |
| `/model` | AIモデルを表示または切り替えます |

> Feishu/Larkはネイティブのスラッシュコマンドメニューをサポートしていないため、これらは通常のテキストメッセージとして送信してください。

---

## トラブルシューティング

### グループチャットでボットが応答しない

1. ボットがグループに追加されていることを確認します
2. ボットを@メンションしていることを確認します（デフォルトで必須です）
3. `groupPolicy` が `"disabled"` ではないことを確認します
4. ログを確認します: `openclaw logs --follow`

### ボットがメッセージを受信しない

1. ボットがFeishu Open Platform / Lark Developerで公開および承認されていることを確認します
2. イベント購読に `im.message.receive_v1` が含まれていることを確認します
3. **persistent connection**（WebSocket）が選択されていることを確認します
4. 必要な権限スコープがすべて付与されていることを確認します
5. Gatewayが実行中であることを確認します: `openclaw gateway status`
6. ログを確認します: `openclaw logs --follow`

### App Secretが漏洩した

1. Feishu Open Platform / Lark DeveloperでApp Secretをリセットします
2. 設定内の値を更新します
3. Gatewayを再起動します: `openclaw gateway restart`

---

## 高度な設定

### 複数アカウント

```json5
{
  channels: {
    feishu: {
      defaultAccount: "main",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
          name: "Primary bot",
        },
        backup: {
          appId: "cli_yyy",
          appSecret: "yyy",
          name: "Backup bot",
          enabled: false,
        },
      },
    },
  },
}
```

`defaultAccount` は、送信APIで `accountId` が指定されていない場合にどのアカウントを使用するかを制御します。

### メッセージ制限

- `textChunkLimit` — 送信テキストのチャンクサイズ（デフォルト: `2000` 文字）
- `mediaMaxMb` — メディアのアップロード/ダウンロード制限（デフォルト: `30` MB）

### ストリーミング

Feishu/Larkはインタラクティブカードによるストリーミング返信をサポートしています。有効にすると、ボットはテキスト生成中にカードをリアルタイムで更新します。

```json5
{
  channels: {
    feishu: {
      streaming: true, // ストリーミングカード出力を有効にする（デフォルト: true）
      blockStreaming: true, // ブロック単位のストリーミングを有効にする（デフォルト: true）
    },
  },
}
```

`streaming: false` を設定すると、返信全体を1つのメッセージとして送信します。

### クォータ最適化

2つの任意フラグを使ってFeishu/Lark API呼び出し回数を減らせます。

- `typingIndicator`（デフォルト `true`）: `false` に設定すると入力中リアクションの呼び出しをスキップします
- `resolveSenderNames`（デフォルト `true`）: `false` に設定すると送信者プロフィールの参照をスキップします

```json5
{
  channels: {
    feishu: {
      typingIndicator: false,
      resolveSenderNames: false,
    },
  },
}
```

### ACPセッション

Feishu/LarkはDMとグループスレッドメッセージでACPをサポートしています。Feishu/Lark ACPはテキストコマンド駆動で、ネイティブのスラッシュコマンドメニューはないため、会話内で `/acp ...` メッセージを直接使用してください。

#### 永続的なACPバインディング

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "feishu",
        accountId: "default",
        peer: { kind: "direct", id: "ou_1234567890" },
      },
    },
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "feishu",
        accountId: "default",
        peer: { kind: "group", id: "oc_group_chat:topic:om_topic_root" },
      },
      acp: { label: "codex-feishu-topic" },
    },
  ],
}
```

#### チャットからACPを起動する

Feishu/LarkのDMまたはスレッド内で:

```text
/acp spawn codex --thread here
```

`--thread here` はDMとFeishu/Larkのスレッドメッセージで機能します。以降、そのバインドされた会話内のメッセージはそのACPセッションに直接ルーティングされます。

### マルチエージェントルーティング

`bindings` を使用して、Feishu/LarkのDMまたはグループを異なるエージェントにルーティングします。

```json5
{
  agents: {
    list: [
      { id: "main" },
      { id: "agent-a", workspace: "/home/user/agent-a" },
      { id: "agent-b", workspace: "/home/user/agent-b" },
    ],
  },
  bindings: [
    {
      agentId: "agent-a",
      match: {
        channel: "feishu",
        peer: { kind: "direct", id: "ou_xxx" },
      },
    },
    {
      agentId: "agent-b",
      match: {
        channel: "feishu",
        peer: { kind: "group", id: "oc_zzz" },
      },
    },
  ],
}
```

ルーティング項目:

- `match.channel`: `"feishu"`
- `match.peer.kind`: `"direct"`（DM）または `"group"`（グループチャット）
- `match.peer.id`: ユーザーOpen ID（`ou_xxx`）またはグループID（`oc_xxx`）

取得方法のヒントは [グループID/ユーザーIDを取得する](#get-groupuser-ids) を参照してください。

---

## 設定リファレンス

完全な設定: [Gateway configuration](/ja-JP/gateway/configuration)

| 設定 | 説明 | デフォルト |
| ------------------------------------------------- | ------------------------------------------ | ---------------- |
| `channels.feishu.enabled` | チャンネルを有効/無効にします | `true` |
| `channels.feishu.domain` | APIドメイン（`feishu` または `lark`） | `feishu` |
| `channels.feishu.connectionMode` | イベント転送方式（`websocket` または `webhook`） | `websocket` |
| `channels.feishu.defaultAccount` | 送信ルーティング用のデフォルトアカウント | `default` |
| `channels.feishu.verificationToken` | webhookモードで必須 | — |
| `channels.feishu.encryptKey` | webhookモードで必須 | — |
| `channels.feishu.webhookPath` | Webhookルートパス | `/feishu/events` |
| `channels.feishu.webhookHost` | Webhookのバインドホスト | `127.0.0.1` |
| `channels.feishu.webhookPort` | Webhookのバインドポート | `3000` |
| `channels.feishu.accounts.<id>.appId` | App ID | — |
| `channels.feishu.accounts.<id>.appSecret` | App Secret | — |
| `channels.feishu.accounts.<id>.domain` | アカウントごとのドメイン上書き | `feishu` |
| `channels.feishu.dmPolicy` | DMポリシー | `allowlist` |
| `channels.feishu.allowFrom` | DM許可リスト（open_id一覧） | [BotOwnerId] |
| `channels.feishu.groupPolicy` | グループポリシー | `allowlist` |
| `channels.feishu.groupAllowFrom` | グループ許可リスト | — |
| `channels.feishu.requireMention` | グループで@メンションを必須にします | `true` |
| `channels.feishu.groups.<chat_id>.requireMention` | グループごとの@メンション上書き | 継承 |
| `channels.feishu.groups.<chat_id>.enabled` | 特定のグループを有効/無効にします | `true` |
| `channels.feishu.textChunkLimit` | メッセージチャンクサイズ | `2000` |
| `channels.feishu.mediaMaxMb` | メディアサイズ上限 | `30` |
| `channels.feishu.streaming` | ストリーミングカード出力 | `true` |
| `channels.feishu.blockStreaming` | ブロック単位のストリーミング | `true` |
| `channels.feishu.typingIndicator` | 入力中リアクションを送信します | `true` |
| `channels.feishu.resolveSenderNames` | 送信者の表示名を解決します | `true` |

---

## サポートされるメッセージタイプ

### 受信

- ✅ テキスト
- ✅ リッチテキスト（post）
- ✅ 画像
- ✅ ファイル
- ✅ 音声
- ✅ 動画/メディア
- ✅ スタンプ

### 送信

- ✅ テキスト
- ✅ 画像
- ✅ ファイル
- ✅ 音声
- ✅ 動画/メディア
- ✅ インタラクティブカード（ストリーミング更新を含む）
- ⚠️ リッチテキスト（post形式のフォーマット。Feishu/Larkの完全な作成機能には対応していません）

### スレッドと返信

- ✅ インライン返信
- ✅ スレッド返信
- ✅ スレッドメッセージへの返信時も、メディア返信はスレッド認識を維持します

---

## 関連

- [チャンネル概要](/ja-JP/channels) — サポートされているすべてのチャンネル
- [ペアリング](/ja-JP/channels/pairing) — DM認証とペアリングフロー
- [グループ](/ja-JP/channels/groups) — グループチャットの動作とメンションゲート
- [チャンネルルーティング](/ja-JP/channels/channel-routing) — メッセージのセッションルーティング
- [セキュリティ](/ja-JP/gateway/security) — アクセスモデルとハードニング
