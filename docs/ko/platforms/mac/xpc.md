---
read_when:
    - IPC 계약 또는 메뉴 바 앱 IPC를 수정하는 경우
summary: OpenClaw 앱, gateway node 전송, PeekabooBridge를 위한 macOS IPC 아키텍처
title: macOS IPC
x-i18n:
    generated_at: "2026-04-05T12:49:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: d0211c334a4a59b71afb29dd7b024778172e529fa618985632d3d11d795ced92
    source_path: platforms/mac/xpc.md
    workflow: 15
---

# OpenClaw macOS IPC 아키텍처

**현재 모델:** 로컬 Unix 소켓이 **node host service**를 **macOS 앱**에 연결하여 exec 승인과 `system.run`을 처리합니다. `openclaw-mac` 디버그 CLI는 discovery/connect 점검용으로 존재하며, agent 작업은 계속 Gateway WebSocket과 `node.invoke`를 통해 흐릅니다. UI 자동화는 PeekabooBridge를 사용합니다.

## 목표

- 모든 TCC 관련 작업(알림, 화면 녹화, 마이크, 음성, AppleScript)을 소유하는 단일 GUI 앱 인스턴스.
- 자동화를 위한 작은 표면: Gateway + node 명령, 그리고 UI 자동화를 위한 PeekabooBridge.
- 예측 가능한 권한: 항상 동일한 서명된 번들 ID를 사용하고 launchd로 실행되어 TCC 권한 부여가 유지되도록 함.

## 작동 방식

### Gateway + node 전송

- 앱이 Gateway를 실행하고(로컬 모드), 노드로서 여기에 연결합니다.
- Agent 작업은 `node.invoke`를 통해 수행됩니다(예: `system.run`, `system.notify`, `canvas.*`).

### Node service + 앱 IPC

- 헤드리스 node host service가 Gateway WebSocket에 연결합니다.
- `system.run` 요청은 로컬 Unix 소켓을 통해 macOS 앱으로 전달됩니다.
- 앱이 UI 컨텍스트에서 exec를 수행하고, 필요 시 프롬프트를 표시한 뒤 출력을 반환합니다.

다이어그램(SCI):

```
Agent -> Gateway -> Node Service (WS)
                      |  IPC (UDS + token + HMAC + TTL)
                      v
                  Mac App (UI + TCC + system.run)
```

### PeekabooBridge (UI 자동화)

- UI 자동화는 `bridge.sock`라는 별도의 UNIX 소켓과 PeekabooBridge JSON 프로토콜을 사용합니다.
- 호스트 선호 순서(클라이언트 측): Peekaboo.app → Claude.app → OpenClaw.app → 로컬 실행.
- 보안: 브리지 호스트는 허용된 TeamID가 필요하며, DEBUG 전용 동일 UID 예외 경로는 `PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`로 보호됩니다(Peekaboo 규약).
- 자세한 내용은 [PeekabooBridge usage](/platforms/mac/peekaboo)를 참조하세요.

## 운영 흐름

- 재시작/재빌드: `SIGN_IDENTITY="Apple Development: <Developer Name> (<TEAMID>)" scripts/restart-mac.sh`
  - 기존 인스턴스 종료
  - Swift 빌드 + 패키징
  - LaunchAgent 기록/부트스트랩/킥스타트
- 단일 인스턴스: 동일한 번들 ID로 실행 중인 다른 인스턴스가 있으면 앱은 조기에 종료됩니다.

## 보안 강화 참고

- 모든 권한 있는 표면에 대해 TeamID 일치를 요구하는 것을 권장합니다.
- PeekabooBridge: `PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`(DEBUG 전용)은 로컬 개발을 위해 동일 UID 호출자를 허용할 수 있습니다.
- 모든 통신은 로컬 전용으로 유지되며 네트워크 소켓은 노출되지 않습니다.
- TCC 프롬프트는 GUI 앱 번들에서만 발생합니다. 재빌드 간 서명된 번들 ID를 안정적으로 유지하세요.
- IPC 보안 강화: 소켓 모드 `0600`, token, peer-UID 점검, HMAC 챌린지/응답, 짧은 TTL.
