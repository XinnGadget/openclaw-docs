---
read_when:
    - mac WebChat 뷰 또는 loopback 포트를 디버깅할 때
summary: mac 앱이 gateway WebChat을 임베드하는 방식과 디버깅 방법
title: WebChat (macOS)
x-i18n:
    generated_at: "2026-04-05T12:48:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4f2c45fa5512cc9c5d3b3aa188d94e2e5a90e4bcce607d959d40bea8b17c90c5
    source_path: platforms/mac/webchat.md
    workflow: 15
---

# WebChat (macOS 앱)

macOS 메뉴 막대 앱은 WebChat UI를 네이티브 SwiftUI 뷰로 임베드합니다. 이 UI는
Gateway에 연결되며, 선택된 에이전트의 **main session**을 기본값으로 사용합니다
(다른 세션을 위한 세션 전환기 포함).

- **로컬 모드**: 로컬 Gateway WebSocket에 직접 연결합니다.
- **원격 모드**: SSH를 통해 Gateway 제어 포트를 포워딩하고 해당
  터널을 데이터 평면으로 사용합니다.

## 실행 및 디버깅

- 수동: Lobster 메뉴 → “Open Chat”.
- 테스트용 자동 열기:

  ```bash
  dist/OpenClaw.app/Contents/MacOS/OpenClaw --webchat
  ```

- 로그: `./scripts/clawlog.sh` (subsystem `ai.openclaw`, category `WebChatSwiftUI`).

## 연결 방식

- 데이터 평면: Gateway WS 메서드 `chat.history`, `chat.send`, `chat.abort`,
  `chat.inject` 및 이벤트 `chat`, `agent`, `presence`, `tick`, `health`.
- `chat.history`는 표시용으로 정규화된 transcript 행을 반환합니다. 인라인 directive
  태그는 표시 텍스트에서 제거되고, 일반 텍스트 tool-call XML 페이로드
  (`<tool_call>...</tool_call>`,
  `<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`,
  `<function_calls>...</function_calls>`, 그리고 잘린 tool-call 블록 포함)와
  유출된 ASCII/전각 모델 제어 토큰은 제거되며, 정확히 `NO_REPLY` / `no_reply`인
  순수 silent-token assistant 행은 생략되고,
  지나치게 큰 행은 플레이스홀더로 대체될 수 있습니다.
- 세션: 기본값은 기본 세션(`main`, 또는 범위가 global이면 `global`)입니다.
  UI에서 세션을 전환할 수 있습니다.
- 온보딩은 첫 실행 설정을 분리하기 위해 전용 세션을 사용합니다.

## 보안 표면

- 원격 모드는 SSH를 통해 Gateway WebSocket 제어 포트만 포워딩합니다.

## 알려진 제한 사항

- UI는 전체 브라우저 sandbox가 아니라 채팅 세션에 최적화되어 있습니다.
