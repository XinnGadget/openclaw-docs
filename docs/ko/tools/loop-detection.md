---
read_when:
    - 사용자가 에이전트가 반복적인 tool call에 갇힌다고 보고하는 경우
    - 반복 호출 방지를 조정해야 하는 경우
    - 에이전트 도구/런타임 정책을 수정하는 경우
summary: 반복적인 tool-call 루프를 감지하는 guardrail을 활성화하고 조정하는 방법
title: Tool-loop 감지
x-i18n:
    generated_at: "2026-04-05T12:57:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: dc3c92579b24cfbedd02a286b735d99a259b720f6d9719a9b93902c9fc66137d
    source_path: tools/loop-detection.md
    workflow: 15
---

# Tool-loop 감지

OpenClaw는 에이전트가 반복되는 tool-call 패턴에 갇히지 않도록 할 수 있습니다.
이 guard는 **기본적으로 비활성화**되어 있습니다.

엄격한 설정에서는 정상적인 반복 호출도 차단할 수 있으므로, 필요한 경우에만 활성화하세요.

## 이것이 존재하는 이유

- 진행이 없는 반복 시퀀스를 감지합니다.
- 높은 빈도의 무결과 루프(같은 도구, 같은 입력, 반복되는 오류)를 감지합니다.
- 알려진 polling 도구에 대한 특정 반복 호출 패턴을 감지합니다.

## 구성 블록

전역 기본값:

```json5
{
  tools: {
    loopDetection: {
      enabled: false,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

에이전트별 재정의(선택 사항):

```json5
{
  agents: {
    list: [
      {
        id: "safe-runner",
        tools: {
          loopDetection: {
            enabled: true,
            warningThreshold: 8,
            criticalThreshold: 16,
          },
        },
      },
    ],
  },
}
```

### 필드 동작

- `enabled`: 마스터 스위치입니다. `false`이면 loop 감지를 수행하지 않습니다.
- `historySize`: 분석을 위해 유지하는 최근 tool call 수입니다.
- `warningThreshold`: 패턴을 경고 전용으로 분류하기 전의 임곗값입니다.
- `criticalThreshold`: 반복 루프 패턴을 차단하는 임곗값입니다.
- `globalCircuitBreakerThreshold`: 전역 무진행 차단기 임곗값입니다.
- `detectors.genericRepeat`: 같은 도구 + 같은 매개변수 패턴의 반복을 감지합니다.
- `detectors.knownPollNoProgress`: 상태 변화가 없는 알려진 polling 유사 패턴을 감지합니다.
- `detectors.pingPong`: 번갈아 나타나는 ping-pong 패턴을 감지합니다.

## 권장 설정

- `enabled: true`로 시작하고 나머지 기본값은 그대로 유지하세요.
- 임곗값 순서는 `warningThreshold < criticalThreshold < globalCircuitBreakerThreshold`를 유지하세요.
- 오탐이 발생하면:
  - `warningThreshold` 및/또는 `criticalThreshold`를 높입니다
  - (선택적으로) `globalCircuitBreakerThreshold`를 높입니다
  - 문제를 일으키는 detector만 비활성화합니다
  - 과거 컨텍스트를 덜 엄격하게 하려면 `historySize`를 줄입니다

## 로그 및 예상 동작

루프가 감지되면 OpenClaw는 loop 이벤트를 보고하고, 심각도에 따라 다음 tool-cycle을 차단하거나 완화합니다.
이렇게 하면 정상적인 도구 접근은 유지하면서도 폭주하는 토큰 비용과 잠김 상태로부터 사용자를 보호할 수 있습니다.

- 먼저 경고와 일시적 억제를 우선하세요.
- 반복된 증거가 누적될 때만 상향 조정하세요.

## 참고 사항

- `tools.loopDetection`은 에이전트 수준 재정의와 병합됩니다.
- 에이전트별 구성은 전역 값을 완전히 재정의하거나 확장합니다.
- 구성이 없으면 guardrail은 비활성 상태로 유지됩니다.
