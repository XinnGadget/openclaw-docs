---
read_when:
    - 수신 메시지가 어떻게 응답이 되는지 설명할 때
    - 세션, 큐잉 모드 또는 스트리밍 동작을 명확히 할 때
    - reasoning 가시성과 사용량 영향에 대해 문서화할 때
summary: 메시지 흐름, 세션, 큐잉, 그리고 reasoning 가시성
title: 메시지
x-i18n:
    generated_at: "2026-04-05T12:40:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 475f892bd534fdb10a2ee5d3c57a3d4a7fb8e1ab68d695189ba186004713f6f3
    source_path: concepts/messages.md
    workflow: 15
---

# 메시지

이 페이지는 OpenClaw가 수신 메시지, 세션, 큐잉,
스트리밍, reasoning 가시성을 어떻게 처리하는지 하나로 연결해 설명합니다.

## 메시지 흐름(상위 수준)

```
Inbound message
  -> routing/bindings -> session key
  -> queue (if a run is active)
  -> agent run (streaming + tools)
  -> outbound replies (channel limits + chunking)
```

핵심 조정 항목은 configuration에 있습니다:

- 접두사, 큐잉, 그룹 동작은 `messages.*`
- 블록 스트리밍과 청킹 기본값은 `agents.defaults.*`
- 상한 및 스트리밍 토글은 채널별 재정의(`channels.whatsapp.*`, `channels.telegram.*` 등)

전체 스키마는 [Configuration](/gateway/configuration)을 참조하세요.

## 수신 중복 제거

채널은 재연결 후 동일한 메시지를 다시 전달할 수 있습니다. OpenClaw는
채널/계정/피어/세션/메시지 id를 키로 하는 수명이 짧은 캐시를 유지하므로 중복 전달이 또 다른 에이전트 실행을 트리거하지 않습니다.

## 수신 디바운싱

**같은 발신자**의 빠르게 연속된 메시지는 `messages.inbound`를 통해 하나의
에이전트 턴으로 묶을 수 있습니다. 디바운싱은 채널 + 대화별로 적용되며
응답 스레딩/ID에는 가장 최근 메시지를 사용합니다.

config(전역 기본값 + 채널별 재정의):

```json5
{
  messages: {
    inbound: {
      debounceMs: 2000,
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
        discord: 1500,
      },
    },
  },
}
```

참고:

- 디바운스는 **텍스트 전용** 메시지에 적용되며, 미디어/첨부 파일은 즉시 플러시됩니다.
- 제어 명령은 디바운싱을 우회하므로 독립 실행 상태를 유지합니다.

## 세션과 디바이스

세션은 클라이언트가 아니라 게이트웨이가 소유합니다.

- 다이렉트 채팅은 에이전트 메인 세션 키로 합쳐집니다.
- 그룹/채널은 자체 세션 키를 가집니다.
- 세션 저장소와 transcript는 게이트웨이 호스트에 있습니다.

여러 디바이스/채널이 같은 세션에 매핑될 수 있지만, 기록이 모든
클라이언트에 완전히 다시 동기화되지는 않습니다. 권장 사항: 컨텍스트 분기를 피하려면 긴
대화에는 하나의 기본 디바이스를 사용하세요. Control UI와 TUI는 항상
게이트웨이 기반 세션 transcript를 보여 주므로 이것이 신뢰할 수 있는 원본입니다.

자세한 내용: [세션 관리](/concepts/session).

## 수신 본문과 기록 컨텍스트

OpenClaw는 **프롬프트 본문**과 **명령 본문**을 구분합니다:

- `Body`: 에이전트에 전송되는 프롬프트 텍스트. 여기에는 채널 엔벌로프와
  선택적 기록 래퍼가 포함될 수 있습니다.
- `CommandBody`: 지시문/명령 파싱을 위한 원시 사용자 텍스트.
- `RawBody`: `CommandBody`의 레거시 별칭(호환성을 위해 유지됨).

채널이 기록을 제공할 때는 공통 래퍼를 사용합니다:

- `[Chat messages since your last reply - for context]`
- `[Current message - respond to this]`

**비다이렉트 채팅**(그룹/채널/룸)의 경우 **현재 메시지 본문** 앞에는
발신자 레이블이 붙습니다(기록 항목에 사용하는 것과 같은 스타일). 이렇게 하면 실시간 메시지와 대기열/기록
메시지가 에이전트 프롬프트에서 일관성을 유지합니다.

기록 버퍼는 **보류 중인 메시지만** 포함합니다. 즉, 실행을 트리거하지 않은 그룹 메시지(예: 멘션 게이트가 적용된 메시지)는 포함하고,
이미 세션 transcript에 있는 메시지는 **제외**합니다.

지시문 제거는 **현재 메시지** 섹션에만 적용되므로 기록은 그대로 유지됩니다.
기록을 래핑하는 채널은 `CommandBody`(또는
`RawBody`)를 원래 메시지 텍스트로 설정하고, `Body`는 결합된 프롬프트로 유지해야 합니다.
기록 버퍼는 `messages.groupChat.historyLimit`(전역
기본값)과 `channels.slack.historyLimit` 또는
`channels.telegram.accounts.<id>.historyLimit` 같은 채널별 재정의를 통해 구성할 수 있습니다(`0`으로 설정하면 비활성화).

## 큐잉과 후속 처리

이미 실행이 활성화되어 있으면 수신 메시지는 대기열에 들어가거나, 현재
실행으로 유도되거나, 후속 턴용으로 수집될 수 있습니다.

- `messages.queue`(및 `messages.queue.byChannel`)를 통해 구성합니다.
- 모드: `interrupt`, `steer`, `followup`, `collect` 및 backlog 변형.

자세한 내용: [큐잉](/concepts/queue).

## 스트리밍, 청킹, 배치 처리

블록 스트리밍은 모델이 텍스트 블록을 생성하는 동안 부분 응답을 전송합니다.
청킹은 채널 텍스트 제한을 준수하며 fenced code가 분리되지 않도록 합니다.

핵심 설정:

- `agents.defaults.blockStreamingDefault` (`on|off`, 기본값 off)
- `agents.defaults.blockStreamingBreak` (`text_end|message_end`)
- `agents.defaults.blockStreamingChunk` (`minChars|maxChars|breakPreference`)
- `agents.defaults.blockStreamingCoalesce` (유휴 시간 기반 배치)
- `agents.defaults.humanDelay` (블록 응답 사이의 사람 같은 지연)
- 채널별 재정의: `*.blockStreaming` 및 `*.blockStreamingCoalesce` (Telegram이 아닌 채널은 명시적인 `*.blockStreaming: true` 필요)

자세한 내용: [스트리밍 + 청킹](/concepts/streaming).

## reasoning 가시성과 토큰

OpenClaw는 모델 reasoning을 노출하거나 숨길 수 있습니다:

- `/reasoning on|off|stream`이 가시성을 제어합니다.
- 모델이 생성한 reasoning 콘텐츠는 여전히 토큰 사용량에 포함됩니다.
- Telegram은 초안 버블에 reasoning 스트림을 지원합니다.

자세한 내용: [thinking + reasoning directives](/tools/thinking) 및 [토큰 사용량](/reference/token-use).

## 접두사, 스레딩, 응답

발신 메시지 서식은 `messages`에서 중앙 관리됩니다:

- `messages.responsePrefix`, `channels.<channel>.responsePrefix`, `channels.<channel>.accounts.<id>.responsePrefix`(발신 접두사 단계적 적용), 그리고 `channels.whatsapp.messagePrefix`(WhatsApp 수신 접두사)
- `replyToMode` 및 채널별 기본값을 통한 응답 스레딩

자세한 내용: [Configuration](/gateway/configuration-reference#messages) 및 채널 문서를 참조하세요.

## 관련 항목

- [스트리밍](/concepts/streaming) — 실시간 메시지 전달
- [재시도](/concepts/retry) — 메시지 전달 재시도 동작
- [큐](/concepts/queue) — 메시지 처리 대기열
- [채널](/channels) — 메시징 플랫폼 통합
