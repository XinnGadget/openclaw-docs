---
read_when:
    - 어떤 채널에서든 리액션 작업을 할 때
    - 플랫폼별로 emoji 리액션이 어떻게 다른지 이해할 때
summary: 지원되는 모든 채널에서의 reaction tool 의미론
title: 리액션
x-i18n:
    generated_at: "2026-04-05T12:57:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9af2951eee32e73adb982dbdf39b32e4065993454e9cce2ad23b27565cab4f84
    source_path: tools/reactions.md
    workflow: 15
---

# 리액션

agent는 `message`
tool의 `react` action을 사용해 메시지에 emoji 리액션을 추가하거나 제거할 수 있습니다. 리액션 동작은 채널마다 다릅니다.

## 작동 방식

```json
{
  "action": "react",
  "messageId": "msg-123",
  "emoji": "thumbsup"
}
```

- 리액션을 추가할 때는 `emoji`가 필수입니다.
- 봇의 리액션을 제거하려면 `emoji`를 빈 문자열(`""`)로 설정하세요.
- 특정 emoji를 제거하려면 `remove: true`를 설정하세요(비어 있지 않은 `emoji` 필요).

## 채널별 동작

<AccordionGroup>
  <Accordion title="Discord and Slack">
    - 빈 `emoji`는 해당 메시지에서 봇의 모든 리액션을 제거합니다.
    - `remove: true`는 지정한 emoji만 제거합니다.
  </Accordion>

  <Accordion title="Google Chat">
    - 빈 `emoji`는 해당 메시지에서 앱의 리액션을 제거합니다.
    - `remove: true`는 지정한 emoji만 제거합니다.
  </Accordion>

  <Accordion title="Telegram">
    - 빈 `emoji`는 봇의 리액션을 제거합니다.
    - `remove: true`도 리액션을 제거하지만, tool 검증을 위해 여전히 비어 있지 않은 `emoji`가 필요합니다.
  </Accordion>

  <Accordion title="WhatsApp">
    - 빈 `emoji`는 봇 리액션을 제거합니다.
    - `remove: true`는 내부적으로 빈 emoji로 매핑됩니다(여전히 tool 호출에는 `emoji`가 필요함).
  </Accordion>

  <Accordion title="Zalo Personal (zalouser)">
    - 비어 있지 않은 `emoji`가 필요합니다.
    - `remove: true`는 해당 특정 emoji 리액션을 제거합니다.
  </Accordion>

  <Accordion title="Feishu/Lark">
    - `add`, `remove`, `list` action이 있는 `feishu_reaction` tool을 사용하세요.
    - 추가/제거에는 `emoji_type`이 필요하고, 제거에는 `reaction_id`도 필요합니다.
  </Accordion>

  <Accordion title="Signal">
    - 인바운드 리액션 알림은 `channels.signal.reactionNotifications`로 제어됩니다. `"off"`는 이를 비활성화하고, `"own"`(기본값)은 사용자가 봇 메시지에 리액션했을 때 이벤트를 발생시키며, `"all"`은 모든 리액션에 대해 이벤트를 발생시킵니다.
  </Accordion>
</AccordionGroup>

## 리액션 수준

채널별 `reactionLevel` config는 agent가 얼마나 폭넓게 리액션을 사용하는지 제어합니다. 값은 일반적으로 `off`, `ack`, `minimal`, `extensive`입니다.

- [Telegram reactionLevel](/ko/channels/telegram#reaction-notifications) — `channels.telegram.reactionLevel`
- [WhatsApp reactionLevel](/ko/channels/whatsapp#reactions) — `channels.whatsapp.reactionLevel`

각 플랫폼에서 agent가 메시지에 얼마나 적극적으로 리액션할지 조정하려면 개별 채널에 `reactionLevel`을 설정하세요.

## 관련 항목

- [Agent Send](/tools/agent-send) — `react`를 포함하는 `message` tool
- [채널](/ko/channels) — 채널별 config
