---
read_when:
    - 타이핑 표시 동작이나 기본값을 변경하는 경우
summary: OpenClaw가 타이핑 표시를 보여주는 시점과 이를 조정하는 방법
title: 타이핑 표시
x-i18n:
    generated_at: "2026-04-05T12:41:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 28c8c395a135fc0745181aab66a93582177e6acd0b3496debcbb98159a4f11dc
    source_path: concepts/typing-indicators.md
    workflow: 15
---

# 타이핑 표시

실행이 활성 상태인 동안 타이핑 표시는 채팅 채널로 전송됩니다. 타이핑이 **언제** 시작되는지는
`agents.defaults.typingMode`로 제어하고, **얼마나 자주** 새로 고쳐지는지는 `typingIntervalSeconds`로 제어합니다.

## 기본값

`agents.defaults.typingMode`가 **설정되지 않은 경우**, OpenClaw는 레거시 동작을 유지합니다.

- **다이렉트 채팅**: 모델 루프가 시작되면 즉시 타이핑이 시작됩니다.
- **멘션이 있는 그룹 채팅**: 즉시 타이핑이 시작됩니다.
- **멘션이 없는 그룹 채팅**: 메시지 텍스트 스트리밍이 시작될 때만 타이핑이 시작됩니다.
- **Heartbeat 실행**: 타이핑이 비활성화됩니다.

## 모드

`agents.defaults.typingMode`를 다음 중 하나로 설정하세요.

- `never` — 어떤 경우에도 타이핑 표시를 보내지 않습니다.
- `instant` — 실행이 나중에 무음 응답 토큰만 반환하더라도, **모델 루프가 시작되자마자** 타이핑을 시작합니다.
- `thinking` — **첫 reasoning delta**에서 타이핑을 시작합니다(실행에 `reasoningLevel: "stream"` 필요).
- `message` — **첫 번째 무음이 아닌 텍스트 delta**에서 타이핑을 시작합니다(`NO_REPLY` 무음 토큰은 무시함).

“얼마나 일찍 시작되는지”의 순서는 다음과 같습니다:
`never` → `message` → `thinking` → `instant`

## 구성

```json5
{
  agent: {
    typingMode: "thinking",
    typingIntervalSeconds: 6,
  },
}
```

세션별로 모드 또는 주기를 재정의할 수 있습니다.

```json5
{
  session: {
    typingMode: "message",
    typingIntervalSeconds: 4,
  },
}
```

## 참고

- `message` 모드는 전체 페이로드가 정확히 무음 토큰일 때(예: `NO_REPLY` / `no_reply`, 대소문자 무시 일치) 무음 전용 응답에 대해 타이핑을 표시하지 않습니다.
- `thinking`은 실행이 reasoning을 스트리밍할 때만 동작합니다(`reasoningLevel: "stream"`).
  모델이 reasoning delta를 내보내지 않으면 타이핑은 시작되지 않습니다.
- Heartbeat는 모드와 관계없이 타이핑을 표시하지 않습니다.
- `typingIntervalSeconds`는 시작 시간이 아니라 **새로 고침 주기**를 제어합니다.
  기본값은 6초입니다.
