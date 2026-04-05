---
read_when:
    - 자동 compaction 및 /compact를 이해하려는 경우
    - 컨텍스트 한도에 도달하는 긴 세션을 디버깅하는 경우
summary: OpenClaw가 모델 한도 내에 머물기 위해 긴 대화를 요약하는 방법
title: Compaction
x-i18n:
    generated_at: "2026-04-05T12:39:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4c6dbd6ebdcd5f918805aafdc153925efef3e130faa3fab3c630832e938219fc
    source_path: concepts/compaction.md
    workflow: 15
---

# Compaction

모든 모델에는 컨텍스트 창이 있습니다. 즉, 모델이 처리할 수 있는 최대 토큰 수입니다.
대화가 그 한도에 가까워지면 OpenClaw는 채팅을 계속할 수 있도록 오래된 메시지를 요약으로 **compacts**합니다.

## 작동 방식

1. 이전 대화 턴은 compact 항목으로 요약됩니다.
2. 요약은 세션 transcript에 저장됩니다.
3. 최근 메시지는 그대로 유지됩니다.

OpenClaw가 기록을 compaction 청크로 분할할 때는 assistant 도구 호출이 해당 `toolResult` 항목과 짝을 이루도록 유지합니다. 분할 지점이 도구 블록 내부에 걸리면 OpenClaw는 경계를 이동하여 해당 쌍이 함께 유지되고 현재 요약되지 않은 tail이 보존되도록 합니다.

전체 대화 기록은 디스크에 유지됩니다. Compaction은 다음 턴에서 모델이 무엇을 보게 되는지만 변경합니다.

## 자동 compaction

자동 compaction은 기본적으로 활성화되어 있습니다. 세션이 컨텍스트 한도에 가까워질 때 실행되거나, 모델이 컨텍스트 오버플로 오류를 반환할 때 실행됩니다(이 경우 OpenClaw는 compaction을 수행한 뒤 재시도함). 일반적인 오버플로 시그니처에는 `request_too_large`, `context length exceeded`, `input exceeds the maximum number of tokens`, `input token count exceeds the maximum number of input tokens`, `input is too long for the model`, `ollama error: context length exceeded`가 포함됩니다.

<Info>
Compaction을 수행하기 전에 OpenClaw는 중요한 메모를 [memory](/concepts/memory) 파일에 저장하라고 agent에 자동으로 알려줍니다. 이렇게 하면 컨텍스트 손실을 방지할 수 있습니다.
</Info>

## 수동 compaction

임의의 채팅에서 `/compact`를 입력하여 compaction을 강제로 실행할 수 있습니다. 요약 방향을 안내하려면 지침을 추가하세요:

```
/compact Focus on the API design decisions
```

## 다른 모델 사용

기본적으로 compaction은 agent의 기본 모델을 사용합니다. 더 나은 요약을 위해 더 강력한 모델을 사용할 수 있습니다:

```json5
{
  agents: {
    defaults: {
      compaction: {
        model: "openrouter/anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

## Compaction 시작 알림

기본적으로 compaction은 조용히 실행됩니다. compaction이 시작될 때 짧은 알림을 표시하려면 `notifyUser`를 활성화하세요:

```json5
{
  agents: {
    defaults: {
      compaction: {
        notifyUser: true,
      },
    },
  },
}
```

활성화하면 사용자는 각 compaction 실행 시작 시 짧은 메시지(예: "Compacting
context...")를 보게 됩니다.

## Compaction과 pruning 비교

|                  | Compaction                    | Pruning                          |
| ---------------- | ----------------------------- | -------------------------------- |
| **수행 내용** | 오래된 대화를 요약 | 오래된 도구 결과를 잘라냄 |
| **저장 여부**       | 예(세션 transcript에 저장)   | 아니요(메모리 내 전용, 요청별) |
| **범위**        | 전체 대화           | 도구 결과만                |

[Session pruning](/concepts/session-pruning)은 요약 없이 도구 출력을 잘라내는 더 가벼운 보완 기능입니다.

## 문제 해결

**Compaction이 너무 자주 발생하나요?** 모델의 컨텍스트 창이 작거나 도구 출력이 클 수 있습니다. [session pruning](/concepts/session-pruning)을 활성화해 보세요.

**Compaction 후 컨텍스트가 오래된 것처럼 느껴지나요?** `/compact Focus on <topic>`을 사용해 요약을 안내하거나, 메모가 유지되도록 [memory flush](/concepts/memory)를 활성화하세요.

**완전히 새로 시작해야 하나요?** `/new`는 compaction 없이 새 세션을 시작합니다.

고급 구성(예약 토큰, 식별자 보존, 사용자 지정 컨텍스트 엔진, OpenAI 서버 측 compaction)에 대해서는 [Session Management Deep Dive](/reference/session-management-compaction)를 참조하세요.

## 관련 문서

- [Session](/concepts/session) — 세션 관리 및 수명 주기
- [Session Pruning](/concepts/session-pruning) — 도구 결과 잘라내기
- [Context](/concepts/context) — agent 턴을 위한 컨텍스트가 구성되는 방식
- [Hooks](/automation/hooks) — compaction 수명 주기 훅(`before_compaction`, `after_compaction`)
