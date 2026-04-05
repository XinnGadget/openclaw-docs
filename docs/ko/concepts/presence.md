---
read_when:
    - Instances 탭을 디버깅할 때
    - 중복되거나 오래된 인스턴스 행을 조사할 때
    - gateway WS 연결 또는 system-event 비콘을 변경할 때
summary: OpenClaw presence 항목이 생성, 병합, 표시되는 방식
title: Presence
x-i18n:
    generated_at: "2026-04-05T12:40:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: a004a1f87be08699c1b2cba97cad8678ce5e27baa425f59eaa18006fdcff26e7
    source_path: concepts/presence.md
    workflow: 15
---

# Presence

OpenClaw의 “presence”는 다음에 대한 가볍고 최선형의 보기입니다:

- **Gateway** 자체
- **Gateway에 연결된 클라이언트**(mac app, WebChat, CLI 등)

Presence는 주로 macOS app의 **Instances** 탭을 렌더링하고
운영자에게 빠른 가시성을 제공하는 데 사용됩니다.

## Presence 필드(표시되는 항목)

Presence 항목은 다음과 같은 필드를 가진 구조화된 객체입니다:

- `instanceId`(선택 사항이지만 강력 권장): 안정적인 클라이언트 ID(보통 `connect.client.instanceId`)
- `host`: 사람이 읽기 쉬운 호스트 이름
- `ip`: 최선형 IP 주소
- `version`: 클라이언트 버전 문자열
- `deviceFamily` / `modelIdentifier`: 하드웨어 힌트
- `mode`: `ui`, `webchat`, `cli`, `backend`, `probe`, `test`, `node`, ...
- `lastInputSeconds`: “마지막 사용자 입력 이후 지난 초 수”(알려진 경우)
- `reason`: `self`, `connect`, `node-connected`, `periodic`, ...
- `ts`: 마지막 업데이트 타임스탬프(epoch 이후 ms)

## 생산자(presence의 출처)

Presence 항목은 여러 소스에서 생성되며 **병합**됩니다.

### 1) Gateway 자체 항목

Gateway는 시작 시 항상 “self” 항목을 시드하므로, 어떤 클라이언트도 연결되기 전에
UI에서 gateway 호스트를 표시할 수 있습니다.

### 2) WebSocket 연결

모든 WS 클라이언트는 `connect` 요청으로 시작합니다. 핸드셰이크가 성공하면
Gateway는 해당 연결에 대한 presence 항목을 upsert합니다.

#### 일회성 CLI 명령이 표시되지 않는 이유

CLI는 짧은 일회성 명령을 위해 연결되는 경우가 많습니다. Instances 목록이
과도하게 채워지는 것을 막기 위해 `client.mode === "cli"`는 **presence 항목으로 변환되지 않습니다**.

### 3) `system-event` 비콘

클라이언트는 `system-event` 메서드를 통해 더 풍부한 주기적 비콘을 보낼 수 있습니다. mac
app은 이를 사용해 호스트 이름, IP, `lastInputSeconds`를 보고합니다.

### 4) 노드 연결(role: node)

노드가 `role: node`로 Gateway WebSocket에 연결되면, Gateway는
해당 노드에 대한 presence 항목을 upsert합니다(다른 WS 클라이언트와 동일한 흐름).

## 병합 + 중복 제거 규칙(`instanceId`가 중요한 이유)

Presence 항목은 단일 메모리 내 맵에 저장됩니다:

- 항목은 **presence key**로 키가 지정됩니다.
- 가장 좋은 키는 재시작 후에도 유지되는 안정적인 `instanceId`(`connect.client.instanceId`)입니다.
- 키는 대소문자를 구분하지 않습니다.

클라이언트가 안정적인 `instanceId` 없이 다시 연결되면
**중복** 행으로 표시될 수 있습니다.

## TTL 및 제한된 크기

Presence는 의도적으로 일시적입니다:

- **TTL:** 5분보다 오래된 항목은 정리됩니다
- **최대 항목 수:** 200개(가장 오래된 항목부터 제거)

이렇게 하면 목록을 최신 상태로 유지하고 메모리가 무제한으로 증가하는 것을 방지할 수 있습니다.

## 원격/터널 관련 주의 사항(loopback IP)

클라이언트가 SSH 터널 / 로컬 포트 포워딩을 통해 연결되면 Gateway는
원격 주소를 `127.0.0.1`로 볼 수 있습니다. 양호한 클라이언트 보고 IP를 덮어쓰지 않도록
loopback 원격 주소는 무시됩니다.

## 소비자

### macOS Instances 탭

macOS app은 `system-presence`의 출력을 렌더링하고 마지막 업데이트 경과 시간에 따라
작은 상태 표시기(Active/Idle/Stale)를 적용합니다.

## 디버깅 팁

- 원시 목록을 보려면 Gateway에 대해 `system-presence`를 호출하세요.
- 중복이 보이면:
  - 클라이언트가 핸드셰이크에서 안정적인 `client.instanceId`를 보내는지 확인하세요
  - 주기적 비콘이 같은 `instanceId`를 사용하는지 확인하세요
  - 연결에서 파생된 항목에 `instanceId`가 누락되었는지 확인하세요(이 경우 중복은 예상된 동작입니다)
