---
permalink: /security/formal-verification/
read_when:
    - 정형 보안 모델의 보장 사항 또는 한계를 검토하는 경우
    - TLA+/TLC 보안 모델 검사를 재현하거나 업데이트하는 경우
summary: OpenClaw의 가장 고위험 경로를 위한 기계 검증 보안 모델입니다.
title: 정형 검증(보안 모델)
x-i18n:
    generated_at: "2026-04-05T12:55:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0f7cd2461dcc00d320a5210e50279d76a7fa84e0830c440398323d75e262a38a
    source_path: security/formal-verification.md
    workflow: 15
---

# 정형 검증(보안 모델)

이 페이지는 OpenClaw의 **정형 보안 모델**(현재는 TLA+/TLC, 필요에 따라 추가)을 추적합니다.

> 참고: 일부 오래된 링크는 이전 프로젝트 이름을 가리킬 수 있습니다.

**목표(지향점):** OpenClaw가 명시적인 가정하에 의도한 보안 정책(권한 부여, 세션 격리, 도구 게이팅, 오구성 안전성)을 강제한다는 기계 검증 가능한 근거를 제공합니다.

**현재 이것이 의미하는 것:** 실행 가능한, 공격자 관점의 **보안 회귀 테스트 모음**입니다.

- 각 주장에는 유한한 상태 공간에 대해 실행 가능한 모델 검사가 있습니다.
- 많은 주장에는 현실적인 버그 클래스에 대한 반례 추적을 생성하는 짝이 되는 **부정 모델**이 있습니다.

**아직 이것이 아닌 것:** “OpenClaw가 모든 측면에서 안전하다”거나 전체 TypeScript 구현이 올바르다는 증명은 아닙니다.

## 모델 위치

모델은 별도의 저장소에서 관리됩니다: [vignesh07/openclaw-formal-models](https://github.com/vignesh07/openclaw-formal-models).

## 중요한 주의 사항

- 이는 전체 TypeScript 구현이 아니라 **모델**입니다. 모델과 코드 사이에 드리프트가 발생할 수 있습니다.
- 결과는 TLC가 탐색한 상태 공간 범위에 의해 제한되며, “green”이라고 해서 모델링된 가정과 범위를 넘어 안전함을 의미하지는 않습니다.
- 일부 주장은 명시적인 환경 가정(예: 올바른 배포, 올바른 config 입력)에 의존합니다.

## 결과 재현

현재는 모델 저장소를 로컬로 클론하고 TLC를 실행하여 결과를 재현합니다(아래 참고). 향후에는 다음을 제공할 수 있습니다.

- 공개 아티팩트(반례 추적, 실행 로그)가 포함된 CI 실행 모델
- 작은 범위 제한 검사를 위한 호스팅된 “이 모델 실행” 워크플로

시작하기:

```bash
git clone https://github.com/vignesh07/openclaw-formal-models
cd openclaw-formal-models

# Java 11+ 필요(TLC는 JVM에서 실행됨).
# 이 저장소는 고정된 `tla2tools.jar`(TLA+ 도구)를 벤더링하며 `bin/tlc` + Make 타깃을 제공합니다.

make <target>
```

### Gateway 노출 및 open gateway 오구성

**주장:** 인증 없이 loopback을 넘어서 바인딩하면 원격 침해가 가능해지거나 노출이 증가할 수 있으며, 토큰/비밀번호는 무단 공격자를 차단합니다(모델 가정 기준).

- Green 실행:
  - `make gateway-exposure-v2`
  - `make gateway-exposure-v2-protected`
- Red(예상됨):
  - `make gateway-exposure-v2-negative`

추가 참고: 모델 저장소의 `docs/gateway-exposure-matrix.md`.

### Node exec 파이프라인(최고위험 기능)

**주장:** `exec host=node`에는 (a) 노드 명령 allowlist와 선언된 명령, 그리고 (b) 구성된 경우 라이브 승인이 필요합니다. 승인은 재사용 공격을 방지하기 위해 토큰화됩니다(모델 기준).

- Green 실행:
  - `make nodes-pipeline`
  - `make approvals-token`
- Red(예상됨):
  - `make nodes-pipeline-negative`
  - `make approvals-token-negative`

### Pairing 저장소(DM 게이팅)

**주장:** pairing 요청은 TTL 및 pending-request 상한을 준수합니다.

- Green 실행:
  - `make pairing`
  - `make pairing-cap`
- Red(예상됨):
  - `make pairing-negative`
  - `make pairing-cap-negative`

### 인그레스 게이팅(멘션 + 제어 명령 우회)

**주장:** 멘션이 필요한 그룹 컨텍스트에서는 권한 없는 “제어 명령”이 멘션 게이팅을 우회할 수 없습니다.

- Green:
  - `make ingress-gating`
- Red(예상됨):
  - `make ingress-gating-negative`

### 라우팅/session-key 격리

**주장:** 서로 다른 피어의 DM은 명시적으로 연결/구성되지 않는 한 동일한 세션으로 합쳐지지 않습니다.

- Green:
  - `make routing-isolation`
- Red(예상됨):
  - `make routing-isolation-negative`

## v1++: 추가 범위 제한 모델(동시성, 재시도, 추적 정확성)

이는 실제 장애 모드(비원자적 업데이트, 재시도, 메시지 fan-out)에 대한 충실도를 높이는 후속 모델입니다.

### Pairing 저장소 동시성 / 멱등성

**주장:** pairing 저장소는 인터리빙 상황에서도 `MaxPending`과 멱등성을 강제해야 합니다(즉, “check-then-write”는 원자적이거나 잠금되어야 하며, refresh는 중복을 생성해서는 안 됨).

의미:

- 동시 요청 상황에서 채널별 `MaxPending`을 초과할 수 없습니다.
- 동일한 `(channel, sender)`에 대한 반복 요청/refresh는 중복된 활성 pending 행을 생성해서는 안 됩니다.

- Green 실행:
  - `make pairing-race` (원자적/잠금된 상한 검사)
  - `make pairing-idempotency`
  - `make pairing-refresh`
  - `make pairing-refresh-race`
- Red(예상됨):
  - `make pairing-race-negative` (비원자적 begin/commit 상한 경쟁)
  - `make pairing-idempotency-negative`
  - `make pairing-refresh-negative`
  - `make pairing-refresh-race-negative`

### 인그레스 추적 상관관계 / 멱등성

**주장:** 수집은 fan-out 전반에 걸쳐 추적 상관관계를 보존해야 하며, 프로바이더 재시도 하에서도 멱등적이어야 합니다.

의미:

- 하나의 외부 이벤트가 여러 내부 메시지가 될 때, 모든 부분이 동일한 trace/event identity를 유지합니다.
- 재시도로 인해 이중 처리되지 않습니다.
- 프로바이더 이벤트 ID가 없으면, dedupe는 서로 다른 이벤트가 제거되지 않도록 안전한 키(예: trace ID)로 폴백합니다.

- Green:
  - `make ingress-trace`
  - `make ingress-trace2`
  - `make ingress-idempotency`
  - `make ingress-dedupe-fallback`
- Red(예상됨):
  - `make ingress-trace-negative`
  - `make ingress-trace2-negative`
  - `make ingress-idempotency-negative`
  - `make ingress-dedupe-fallback-negative`

### 라우팅 dmScope 우선순위 + identityLinks

**주장:** 라우팅은 기본적으로 DM 세션을 격리된 상태로 유지해야 하며, 명시적으로 구성된 경우에만 세션을 합쳐야 합니다(채널 우선순위 + identity links).

의미:

- 채널별 dmScope 재정의는 전역 기본값보다 우선해야 합니다.
- identityLinks는 명시적으로 연결된 그룹 내에서만 세션을 합쳐야 하며, 관련 없는 피어 간에는 합치면 안 됩니다.

- Green:
  - `make routing-precedence`
  - `make routing-identitylinks`
- Red(예상됨):
  - `make routing-precedence-negative`
  - `make routing-identitylinks-negative`
