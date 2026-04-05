---
read_when:
    - Gateway 프로세스를 실행하거나 디버깅할 때
    - 단일 인스턴스 강제를 조사할 때
summary: WebSocket 리스너 바인드를 사용하는 Gateway 싱글턴 가드
title: Gateway 잠금
x-i18n:
    generated_at: "2026-04-05T12:41:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 726c687ab53f2dd1e46afed8fc791b55310a5c1e62f79a0e38a7dc4ca7576093
    source_path: gateway/gateway-lock.md
    workflow: 15
---

# Gateway 잠금

## 이유

- 동일한 호스트에서 기본 포트당 하나의 gateway 인스턴스만 실행되도록 보장합니다. 추가 gateway는 격리된 profile과 고유한 포트를 사용해야 합니다.
- 오래된 잠금 파일을 남기지 않고 충돌/SIGKILL을 견딥니다.
- 제어 포트가 이미 사용 중일 때 명확한 오류와 함께 빠르게 실패합니다.

## 메커니즘

- Gateway는 시작 직후 독점 TCP 리스너를 사용하여 WebSocket 리스너(기본값 `ws://127.0.0.1:18789`)를 즉시 바인드합니다.
- 바인드가 `EADDRINUSE`로 실패하면, 시작 시 `GatewayLockError("another gateway instance is already listening on ws://127.0.0.1:<port>")`를 발생시킵니다.
- OS는 충돌 및 SIGKILL을 포함한 모든 프로세스 종료 시 리스너를 자동으로 해제하므로, 별도의 잠금 파일이나 정리 단계가 필요하지 않습니다.
- 종료 시 Gateway는 포트를 즉시 해제하기 위해 WebSocket 서버와 기본 HTTP 서버를 닫습니다.

## 오류 표면

- 다른 프로세스가 포트를 점유하고 있으면, 시작 시 `GatewayLockError("another gateway instance is already listening on ws://127.0.0.1:<port>")`를 발생시킵니다.
- 다른 바인드 실패는 `GatewayLockError("failed to bind gateway socket on ws://127.0.0.1:<port>: …")`로 표시됩니다.

## 운영 참고 사항

- 포트를 _다른_ 프로세스가 점유하고 있는 경우에도 오류는 동일합니다. 포트를 해제하거나 `openclaw gateway --port <port>`로 다른 포트를 선택하세요.
- macOS 앱은 여전히 gateway를 생성하기 전에 자체적인 경량 PID 가드를 유지하지만, 런타임 잠금은 WebSocket 바인드로 강제됩니다.

## 관련 항목

- [Multiple Gateways](/gateway/multiple-gateways) — 고유한 포트로 여러 인스턴스 실행
- [Troubleshooting](/gateway/troubleshooting) — `EADDRINUSE` 및 포트 충돌 진단
