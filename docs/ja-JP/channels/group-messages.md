---
read_when:
    - グループメッセージのルールまたはメンションの変更
summary: WhatsAppグループメッセージ処理の動作と設定（`mentionPatterns` は各サーフェス間で共有されます）
title: グループメッセージ
x-i18n:
    generated_at: "2026-04-12T23:27:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5d9484dd1de74d42f8dce4c3ac80d60c24864df30a7802e64893ef55506230fe
    source_path: channels/group-messages.md
    workflow: 15
---

# グループメッセージ（WhatsApp web チャネル）

目標：Clawd を WhatsApp グループに参加させ、呼びかけられたときだけ起動し、そのスレッドを個人 DM セッションとは分けて維持できるようにします。

注: `agents.list[].groupChat.mentionPatterns` は現在 Telegram/Discord/Slack/iMessage でも使用されます。このドキュメントは WhatsApp 固有の動作に焦点を当てています。マルチエージェント構成では、エージェントごとに `agents.list[].groupChat.mentionPatterns` を設定してください（またはグローバルなフォールバックとして `messages.groupChat.mentionPatterns` を使用してください）。

## 現在の実装（2025-12-03）

- アクティベーションモード: `mention`（デフォルト）または `always`。`mention` では呼びかけが必要です（`mentionedJids` による実際の WhatsApp の @メンション、安全な正規表現パターン、またはテキスト内の任意の位置にあるボットの E.164）。`always` はすべてのメッセージでエージェントを起動しますが、意味のある価値を追加できる場合にのみ返信すべきです。そうでない場合は、正確にサイレントトークン `NO_REPLY` / `no_reply` を返します。デフォルトは設定の `channels.whatsapp.groups` で指定でき、グループごとに `/activation` で上書きできます。`channels.whatsapp.groups` が設定されている場合、グループ許可リストとしても機能します（すべてを許可するには `"*"` を含めます）。
- グループポリシー: `channels.whatsapp.groupPolicy` は、グループメッセージを受け入れるかどうかを制御します（`open|disabled|allowlist`）。`allowlist` は `channels.whatsapp.groupAllowFrom` を使用します（フォールバック: 明示的な `channels.whatsapp.allowFrom`）。デフォルトは `allowlist` です（送信者を追加するまでブロックされます）。
- グループごとのセッション: セッションキーは `agent:<agentId>:whatsapp:group:<jid>` のようになります。そのため、`/verbose on`、`/trace on`、`/think high` などのコマンド（単独メッセージとして送信）はそのグループにスコープされます。個人 DM の状態には影響しません。Heartbeat はグループスレッドではスキップされます。
- コンテキスト注入: 実行をトリガーしなかった**保留中のみ**のグループメッセージ（デフォルト 50 件）は、`[Chat messages since your last reply - for context]` の下にプレフィックスされ、トリガーとなった行は `[Current message - respond to this]` の下に置かれます。すでにセッション内にあるメッセージは再注入されません。
- 送信者の表示: 各グループバッチの末尾には `[from: Sender Name (+E164)]` が追加されるため、Pi は誰が話しているかを把握できます。
- 一時メッセージ / view-once: テキストやメンションを抽出する前にそれらをアンラップするため、その中の呼びかけでも引き続きトリガーされます。
- グループシステムプロンプト: グループセッションの最初のターン時（および `/activation` でモードが変更されるたび）に、`You are replying inside the WhatsApp group "<subject>". Group members: Alice (+44...), Bob (+43...), … Activation: trigger-only … Address the specific sender noted in the message context.` のような短い説明をシステムプロンプトに注入します。メタデータが利用できない場合でも、グループチャットであることはエージェントに伝えます。

## 設定例（WhatsApp）

表示名による呼びかけが、WhatsApp が本文テキスト内の視覚的な `@` を取り除いた場合でも機能するように、`~/.openclaw/openclaw.json` に `groupChat` ブロックを追加します。

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
      },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          historyLimit: 50,
          mentionPatterns: ["@?openclaw", "\\+?15555550123"],
        },
      },
    ],
  },
}
```

注:

- これらの正規表現は大文字小文字を区別せず、他の設定用正規表現サーフェスと同じ safe-regex ガードレールを使用します。無効なパターンや、安全でないネストされた繰り返しは無視されます。
- WhatsApp は、誰かが連絡先をタップしたときに `mentionedJids` 経由で正規のメンションも送信するため、番号フォールバックが必要になることはまれですが、有用な安全策です。

### アクティベーションコマンド（owner-only）

グループチャットコマンドを使用します。

- `/activation mention`
- `/activation always`

これを変更できるのは owner 番号のみです（`channels.whatsapp.allowFrom`、未設定時はボット自身の E.164）。現在のアクティベーションモードを確認するには、グループで `/status` を単独メッセージとして送信してください。

## 使用方法

1. WhatsApp アカウント（OpenClaw を実行しているもの）をグループに追加します。
2. `@openclaw …` と発言します（または番号を含めます）。`groupPolicy: "open"` を設定しない限り、許可リストにある送信者だけがトリガーできます。
3. エージェントプロンプトには最近のグループコンテキストと末尾の `[from: …]` マーカーが含まれるため、正しい相手に応答できます。
4. セッションレベルのディレクティブ（`/verbose on`、`/trace on`、`/think high`、`/new` または `/reset`、`/compact`）はそのグループのセッションにのみ適用されます。認識されるよう、単独メッセージとして送信してください。個人 DM セッションは独立したままです。

## テスト / 検証

- 手動スモークテスト:
  - グループで `@openclaw` の呼びかけを送信し、送信者名に言及した返信を確認します。
  - 2 回目の呼びかけを送信し、履歴ブロックが含まれ、その次のターンでクリアされることを確認します。
- Gateway ログ（`--verbose` 付きで実行）を確認し、`from: <groupJid>` を示す `inbound web message` エントリと `[from: …]` サフィックスを確認します。

## 既知の考慮事項

- グループではノイズの多いブロードキャストを避けるため、Heartbeat は意図的にスキップされます。
- エコー抑制は結合されたバッチ文字列を使用します。メンションなしで同一テキストを 2 回送信した場合、返信を受けるのは最初の 1 回だけです。
- セッションストアのエントリは、セッションストア（デフォルトでは `~/.openclaw/agents/<agentId>/sessions/sessions.json`）内で `agent:<agentId>:whatsapp:group:<jid>` として表示されます。エントリがない場合は、まだそのグループで実行がトリガーされていないことを意味するだけです。
- グループでの入力中インジケーターは `agents.defaults.typingMode` に従います（デフォルト: メンションされていない場合は `message`）。
