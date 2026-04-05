---
read_when:
    - 외부 CLI 통합을 추가하거나 변경하는 경우
    - RPC 어댑터(signal-cli, imsg)를 디버깅하는 경우
summary: 외부 CLI(signal-cli, 레거시 imsg)용 RPC 어댑터와 게이트웨이 패턴
title: RPC 어댑터
x-i18n:
    generated_at: "2026-04-05T12:53:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 06dc6b97184cc704ba4ec4a9af90502f4316bcf717c3f4925676806d8b184c57
    source_path: reference/rpc.md
    workflow: 15
---

# RPC 어댑터

OpenClaw는 JSON-RPC를 통해 외부 CLI를 통합합니다. 현재는 두 가지 패턴을 사용합니다.

## 패턴 A: HTTP 데몬(signal-cli)

- `signal-cli`는 HTTP를 통한 JSON-RPC를 사용하는 데몬으로 실행됩니다.
- 이벤트 스트림은 SSE(``/api/v1/events``)입니다.
- 상태 확인 프로브: `/api/v1/check`.
- `channels.signal.autoStart=true`일 때 OpenClaw가 수명 주기를 관리합니다.

설정 및 엔드포인트는 [Signal](/channels/signal)을 참고하세요.

## 패턴 B: stdio 자식 프로세스(레거시: imsg)

> **참고:** 새로운 iMessage 설정에는 대신 [BlueBubbles](/channels/bluebubbles)를 사용하세요.

- OpenClaw는 `imsg rpc`를 자식 프로세스로 실행합니다(레거시 iMessage 통합).
- JSON-RPC는 stdin/stdout을 통해 줄 단위로 구분됩니다(한 줄당 하나의 JSON 객체).
- TCP 포트가 없고 데몬도 필요하지 않습니다.

사용되는 코어 메서드:

- `watch.subscribe` → 알림(`method: "message"`)
- `watch.unsubscribe`
- `send`
- `chats.list` (프로브/진단)

레거시 설정 및 주소 지정(`chat_id` 권장)은 [iMessage](/channels/imessage)를 참고하세요.

## 어댑터 가이드라인

- 게이트웨이가 프로세스를 소유합니다(시작/중지는 프로바이더 수명 주기에 연결됨).
- RPC 클라이언트는 복원력을 갖추어야 합니다: 타임아웃, 종료 시 재시작.
- 표시 문자열보다 안정적인 ID(예: `chat_id`)를 우선 사용하세요.
