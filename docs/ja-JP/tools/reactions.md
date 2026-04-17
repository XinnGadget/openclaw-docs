---
read_when:
    - 任意の channel でリアクション機能を扱うこと
    - 絵文字リアクションがプラットフォームごとにどう異なるかを理解すること
summary: サポートされているすべての channels における reaction tool のセマンティクス
title: リアクション
x-i18n:
    generated_at: "2026-04-11T02:48:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfac31b7f0effc89cc696e3cf34cd89503ccdbb28996723945025e4b6e159986
    source_path: tools/reactions.md
    workflow: 15
---

# リアクション

agent は `message`
tool の `react` アクションを使って、メッセージに絵文字リアクションを追加および削除できます。リアクションの動作は channel によって異なります。

## 仕組み

```json
{
  "action": "react",
  "messageId": "msg-123",
  "emoji": "thumbsup"
}
```

- リアクションを追加する場合、`emoji` は必須です。
- bot のリアクションを削除するには、`emoji` を空文字列（`""`）に設定します。
- 特定の絵文字を削除するには、`remove: true` を設定します（空でない `emoji` が必要です）。

## Channel ごとの動作

<AccordionGroup>
  <Accordion title="Discord と Slack">
    - 空の `emoji` は、そのメッセージ上の bot のリアクションをすべて削除します。
    - `remove: true` は、指定された絵文字だけを削除します。
  </Accordion>

  <Accordion title="Google Chat">
    - 空の `emoji` は、そのメッセージ上の app のリアクションを削除します。
    - `remove: true` は、指定された絵文字だけを削除します。
  </Accordion>

  <Accordion title="Telegram">
    - 空の `emoji` は、bot のリアクションを削除します。
    - `remove: true` でもリアクションは削除されますが、tool の検証上は引き続き空でない `emoji` が必要です。
  </Accordion>

  <Accordion title="WhatsApp">
    - 空の `emoji` は、bot のリアクションを削除します。
    - `remove: true` は内部的に空の絵文字へマップされます（それでも tool 呼び出しでは `emoji` が必要です）。
  </Accordion>

  <Accordion title="Zalo Personal (zalouser)">
    - 空でない `emoji` が必要です。
    - `remove: true` は、その特定の絵文字リアクションを削除します。
  </Accordion>

  <Accordion title="Feishu/Lark">
    - `add`、`remove`、`list` アクションを持つ `feishu_reaction` tool を使用します。
    - 追加/削除には `emoji_type` が必要で、削除では `reaction_id` も必要です。
  </Accordion>

  <Accordion title="Signal">
    - 受信リアクション通知は `channels.signal.reactionNotifications` によって制御されます。`"off"` は無効化、`"own"`（デフォルト）はユーザーが bot メッセージにリアクションしたときにイベントを発行し、`"all"` はすべてのリアクションに対してイベントを発行します。
  </Accordion>
</AccordionGroup>

## リアクションレベル

channel ごとの `reactionLevel` 設定は、agent がどの程度広くリアクションを使うかを制御します。値は通常 `off`、`ack`、`minimal`、または `extensive` です。

- [Telegram reactionLevel](/ja-JP/channels/telegram#reaction-notifications) — `channels.telegram.reactionLevel`
- [WhatsApp reactionLevel](/ja-JP/channels/whatsapp#reaction-level) — `channels.whatsapp.reactionLevel`

個別の channel に `reactionLevel` を設定して、各プラットフォームで agent がどの程度積極的にメッセージへリアクションするかを調整してください。

## 関連

- [Agent Send](/ja-JP/tools/agent-send) — `react` を含む `message` tool
- [Channels](/ja-JP/channels) — channel 固有の設定
