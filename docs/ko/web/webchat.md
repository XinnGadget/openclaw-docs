---
read_when:
    - WebChat 접근을 디버깅하거나 설정할 때
summary: 채팅 UI를 위한 loopback WebChat 정적 호스트 및 Gateway WS 사용
title: WebChat
x-i18n:
    generated_at: "2026-04-05T12:59:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2588be04e9ae38149bdf284bf4d75b6784d63899026d2351c4e0e7efdf05ff39
    source_path: web/webchat.md
    workflow: 15
---

# WebChat (Gateway WebSocket UI)

상태: macOS/iOS SwiftUI 채팅 UI는 Gateway WebSocket에 직접 연결됩니다.

## 개요

- gateway용 네이티브 채팅 UI입니다(임베디드 브라우저 및 로컬 정적 서버 없음).
- 다른 채널과 동일한 session 및 라우팅 규칙을 사용합니다.
- 결정적 라우팅: 답장은 항상 WebChat으로 다시 돌아갑니다.

## 빠른 시작

1. gateway를 시작합니다.
2. WebChat UI(macOS/iOS 앱) 또는 Control UI 채팅 탭을 엽니다.
3. 유효한 gateway auth 경로가 설정되어 있는지 확인합니다(기본적으로 shared-secret,
   loopback에서도 동일).

## 작동 방식(동작)

- UI는 Gateway WebSocket에 연결하고 `chat.history`, `chat.send`, `chat.inject`를 사용합니다.
- `chat.history`는 안정성을 위해 범위가 제한됩니다. Gateway는 긴 텍스트 필드를 잘라내고, 무거운 메타데이터를 생략하며, 너무 큰 entry는 `[chat.history omitted: message too large]`로 대체할 수 있습니다.
- `chat.history`는 표시용으로도 정규화됩니다. 인라인 전달 directive tag
  (`[[reply_to_*]]`, `[[audio_as_voice]]` 등), 일반 텍스트 tool-call XML
  payload(` <tool_call>...</tool_call>`,
  `<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`,
  `<function_calls>...</function_calls>`, 잘린 tool-call 블록 포함), 그리고
  누출된 ASCII/전각 모델 제어 토큰은 보이는 텍스트에서 제거되며,
  전체 보이는 텍스트가 정확히 무음 토큰 `NO_REPLY` / `no_reply`뿐인 assistant entry는 생략됩니다.
- `chat.inject`는 assistant note를 transcript에 직접 추가하고 UI에 브로드캐스트합니다(agent 실행 없음).
- 중단된 실행은 UI에 부분 assistant 출력을 계속 표시할 수 있습니다.
- Gateway는 버퍼링된 출력이 있으면 중단된 부분 assistant 텍스트를 transcript 기록에 유지하고, 해당 entry에 중단 메타데이터를 표시합니다.
- 기록은 항상 gateway에서 가져옵니다(로컬 파일 감시 없음).
- gateway에 연결할 수 없으면 WebChat은 읽기 전용입니다.

## Control UI agent tool 패널

- Control UI `/agents` Tools 패널에는 서로 분리된 두 개의 뷰가 있습니다.
  - **Available Right Now**는 `tools.effective(sessionKey=...)`를 사용하며,
    core, plugin, 채널 소유 tool을 포함해 현재
    session이 런타임에서 실제로 사용할 수 있는 항목을 보여줍니다.
  - **Tool Configuration**은 `tools.catalog`를 사용하며 profile, override,
    catalog 의미론에 집중합니다.
- 런타임 가용성은 session 범위입니다. 같은 agent에서 session을 바꾸면
  **Available Right Now** 목록이 달라질 수 있습니다.
- config editor는 런타임 가용성을 의미하지 않습니다. 실제 접근 권한은 여전히 정책
  우선순위(`allow`/`deny`, agent별 및 provider/channel override)를 따릅니다.

## 원격 사용

- 원격 모드는 SSH/Tailscale을 통해 gateway WebSocket을 터널링합니다.
- 별도의 WebChat 서버를 실행할 필요가 없습니다.

## config 참조(WebChat)

전체 config: [Configuration](/ko/gateway/configuration)

WebChat 옵션:

- `gateway.webchat.chatHistoryMaxChars`: `chat.history` 응답에서 텍스트 필드의 최대 문자 수입니다. transcript entry가 이 제한을 초과하면 Gateway는 긴 텍스트 필드를 잘라내고 너무 큰 메시지를 placeholder로 대체할 수 있습니다. 클라이언트는 단일 `chat.history` 호출에 대해서만 이 기본값을 override하기 위해 요청별 `maxChars`를 함께 보낼 수도 있습니다.

관련 전역 옵션:

- `gateway.port`, `gateway.bind`: WebSocket 호스트/포트
- `gateway.auth.mode`, `gateway.auth.token`, `gateway.auth.password`:
  shared-secret WebSocket auth
- `gateway.auth.allowTailscale`: 브라우저 Control UI 채팅 탭은 활성화된 경우 Tailscale
  Serve identity header를 사용할 수 있습니다.
- `gateway.auth.mode: "trusted-proxy"`: identity-aware **non-loopback** 프록시 소스 뒤의 브라우저 client를 위한 reverse-proxy auth([Trusted Proxy Auth](/ko/gateway/trusted-proxy-auth) 참고)
- `gateway.remote.url`, `gateway.remote.token`, `gateway.remote.password`: 원격 gateway 대상
- `session.*`: session 저장소 및 main key 기본값
