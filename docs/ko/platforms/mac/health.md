---
read_when:
    - mac app 상태 표시기를 디버깅하는 경우
summary: macOS 앱이 gateway/Baileys 상태를 보고하는 방식
title: 상태 확인 (macOS)
x-i18n:
    generated_at: "2026-04-05T12:48:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: f9223b2bbe272b32526f79cf878510ac5104e788402d94a1b1627e72c5fbebf5
    source_path: platforms/mac/health.md
    workflow: 15
---

# macOS의 상태 확인

메뉴 막대 앱에서 연결된 채널이 정상인지 확인하는 방법입니다.

## 메뉴 막대

- 상태 점은 이제 Baileys 상태를 반영합니다.
  - 녹색: 연결됨 + 최근에 소켓이 열림
  - 주황색: 연결 중/재시도 중
  - 빨간색: 로그아웃됨 또는 프로브 실패
- 보조 줄에는 "linked · auth 12m"가 표시되거나 실패 이유가 표시됩니다.
- "Run Health Check" 메뉴 항목은 온디맨드 프로브를 트리거합니다.

## 설정

- General 탭에는 linked auth age, session-store 경로/개수, 마지막 확인 시간, 마지막 오류/상태 코드, Run Health Check / Reveal Logs 버튼을 보여주는 Health 카드가 추가됩니다.
- 캐시된 스냅샷을 사용하므로 UI는 즉시 로드되며 오프라인일 때도 정상적으로 폴백합니다.
- **Channels 탭**은 WhatsApp/Telegram의 채널 상태 + 제어(로그인 QR, 로그아웃, 프로브, 마지막 연결 해제/오류)를 표시합니다.

## 프로브 작동 방식

- 앱은 `ShellExecutor`를 통해 약 60초마다 그리고 온디맨드로 `openclaw health --json`을 실행합니다. 이 프로브는 메시지를 보내지 않고 자격 증명을 로드하고 상태를 보고합니다.
- 깜빡임을 방지하기 위해 마지막 정상 스냅샷과 마지막 오류를 별도로 캐시하고, 각각의 타임스탬프를 표시합니다.

## 확실하지 않을 때

- [Gateway health](/gateway/health)의 CLI 흐름(`openclaw status`, `openclaw status --deep`, `openclaw health --json`)을 계속 사용할 수 있으며, `web-heartbeat` / `web-reconnect`를 위해 `/tmp/openclaw/openclaw-*.log`를 tail할 수 있습니다.
