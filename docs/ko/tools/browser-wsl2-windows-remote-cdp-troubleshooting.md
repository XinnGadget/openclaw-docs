---
read_when:
    - Chrome는 Windows에 있고 OpenClaw Gateway는 WSL2에서 실행하는 경우
    - WSL2와 Windows 전반에서 브라우저/control-ui 오류가 겹쳐 나타나는 경우
    - 분리된 호스트 설정에서 host-local Chrome MCP와 원시 원격 CDP 중 무엇을 쓸지 결정하는 경우
summary: WSL2 Gateway + Windows Chrome 원격 CDP를 계층별로 문제 해결하기
title: WSL2 + Windows + 원격 Chrome CDP 문제 해결
x-i18n:
    generated_at: "2026-04-05T12:56:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 99df2988d3c6cf36a8c2124d5b724228d095a60b2d2b552f3810709b5086127d
    source_path: tools/browser-wsl2-windows-remote-cdp-troubleshooting.md
    workflow: 15
---

# WSL2 + Windows + 원격 Chrome CDP 문제 해결

이 가이드는 다음과 같은 일반적인 분리 호스트 설정을 다룹니다:

- OpenClaw Gateway는 WSL2 내부에서 실행됨
- Chrome은 Windows에서 실행됨
- 브라우저 제어는 WSL2/Windows 경계를 넘어야 함

또한 [issue #39369](https://github.com/openclaw/openclaw/issues/39369)의 계층형 실패 패턴도 다룹니다. 여러 개의 독립적인 문제가 동시에 나타날 수 있어 잘못된 계층이 먼저 망가진 것처럼 보일 수 있습니다.

## 먼저 올바른 브라우저 모드를 선택하세요

유효한 패턴은 두 가지입니다:

### 옵션 1: WSL2에서 Windows로의 원시 원격 CDP

WSL2에서 Windows Chrome CDP 엔드포인트를 가리키는 원격 브라우저 프로필을 사용합니다.

다음 경우에 선택하세요:

- Gateway가 WSL2 내부에 유지되는 경우
- Chrome이 Windows에서 실행되는 경우
- 브라우저 제어가 WSL2/Windows 경계를 넘어야 하는 경우

### 옵션 2: Host-local Chrome MCP

Gateway 자체가 Chrome과 동일한 호스트에서 실행될 때만 `existing-session` / `user`를 사용하세요.

다음 경우에 선택하세요:

- OpenClaw와 Chrome이 같은 컴퓨터에서 실행되는 경우
- 로컬에서 로그인된 브라우저 상태를 사용하려는 경우
- 호스트 간 브라우저 전송이 필요하지 않은 경우
- `responsebody`, PDF 내보내기, 다운로드 가로채기, 배치 작업과 같은 고급 managed/raw-CDP 전용 경로가 필요하지 않은 경우

WSL2 Gateway + Windows Chrome 조합에서는 원시 원격 CDP를 권장합니다. Chrome MCP는 host-local이며 WSL2에서 Windows로 연결하는 브리지가 아닙니다.

## 동작하는 아키텍처

참조 형태:

- WSL2는 `127.0.0.1:18789`에서 Gateway를 실행함
- Windows는 일반 브라우저에서 `http://127.0.0.1:18789/`로 Control UI를 엶
- Windows Chrome은 포트 `9222`에서 CDP 엔드포인트를 노출함
- WSL2는 해당 Windows CDP 엔드포인트에 도달할 수 있음
- OpenClaw는 WSL2에서 도달 가능한 주소를 가리키는 브라우저 프로필을 사용함

## 왜 이 설정이 혼란스러운가

여러 실패가 겹칠 수 있습니다:

- WSL2가 Windows CDP 엔드포인트에 도달할 수 없음
- Control UI가 안전하지 않은 origin에서 열림
- `gateway.controlUi.allowedOrigins`가 페이지 origin과 일치하지 않음
- 토큰 또는 페어링이 누락됨
- 브라우저 프로필이 잘못된 주소를 가리킴

이 때문에 한 계층을 고쳐도 다른 오류가 계속 보일 수 있습니다.

## Control UI의 중요 규칙

UI를 Windows에서 여는 경우, 의도적으로 HTTPS를 구성하지 않았다면 Windows localhost를 사용하세요.

사용할 주소:

`http://127.0.0.1:18789/`

Control UI에 기본적으로 LAN IP를 사용하지 마세요. LAN 또는 tailnet 주소에서의 일반 HTTP는 CDP 자체와는 무관한 insecure-origin/device-auth 동작을 유발할 수 있습니다. [Control UI](/web/control-ui)를 참조하세요.

## 계층별로 검증하기

위에서 아래로 작업하세요. 건너뛰지 마세요.

### 계층 1: Chrome이 Windows에서 CDP를 제공하는지 확인

원격 디버깅을 활성화한 상태로 Windows에서 Chrome을 시작합니다:

```powershell
chrome.exe --remote-debugging-port=9222
```

Windows에서 먼저 Chrome 자체를 확인합니다:

```powershell
curl http://127.0.0.1:9222/json/version
curl http://127.0.0.1:9222/json/list
```

여기서 Windows에서 실패하면, 아직 OpenClaw 문제가 아닙니다.

### 계층 2: WSL2가 해당 Windows 엔드포인트에 도달할 수 있는지 확인

WSL2에서 `cdpUrl`에 사용할 정확한 주소를 테스트합니다:

```bash
curl http://WINDOWS_HOST_OR_IP:9222/json/version
curl http://WINDOWS_HOST_OR_IP:9222/json/list
```

정상 결과:

- `/json/version`은 Browser / Protocol-Version 메타데이터가 있는 JSON을 반환함
- `/json/list`는 JSON을 반환함(열린 페이지가 없으면 빈 배열이어도 괜찮음)

여기서 실패하면:

- Windows가 아직 WSL2에 포트를 노출하지 않은 상태임
- WSL2 쪽에서 사용할 주소가 잘못됨
- 방화벽 / 포트 포워딩 / 로컬 프록시가 아직 누락됨

OpenClaw 구성을 건드리기 전에 먼저 이것을 해결하세요.

### 계층 3: 올바른 브라우저 프로필 구성

원시 원격 CDP의 경우, WSL2에서 도달 가능한 주소를 OpenClaw에 지정하세요:

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "remote",
    profiles: {
      remote: {
        cdpUrl: "http://WINDOWS_HOST_OR_IP:9222",
        attachOnly: true,
        color: "#00AA00",
      },
    },
  },
}
```

참고:

- Windows에서만 동작하는 주소가 아니라 WSL2에서 도달 가능한 주소를 사용하세요
- 외부에서 관리되는 브라우저에는 `attachOnly: true`를 유지하세요
- `cdpUrl`은 `http://`, `https://`, `ws://`, `wss://`를 사용할 수 있습니다
- OpenClaw가 `/json/version`을 찾게 하려면 HTTP(S)를 사용하세요
- 브라우저 공급자가 직접 DevTools 소켓 URL을 제공하는 경우에만 WS(S)를 사용하세요
- OpenClaw가 성공할 것으로 기대하기 전에 동일한 URL을 `curl`로 테스트하세요

### 계층 4: Control UI 계층을 별도로 확인

Windows에서 UI를 엽니다:

`http://127.0.0.1:18789/`

그런 다음 다음을 확인합니다:

- 페이지 origin이 `gateway.controlUi.allowedOrigins`가 기대하는 값과 일치하는지
- 토큰 인증 또는 페어링이 올바르게 구성되었는지
- 브라우저 문제를 디버깅한다고 생각하면서 실제로는 Control UI 인증 문제를 디버깅하고 있지 않은지

도움이 되는 페이지:

- [Control UI](/web/control-ui)

### 계층 5: end-to-end 브라우저 제어 확인

WSL2에서:

```bash
openclaw browser open https://example.com --browser-profile remote
openclaw browser tabs --browser-profile remote
```

정상 결과:

- 탭이 Windows Chrome에서 열림
- `openclaw browser tabs`가 대상 탭을 반환함
- 이후 작업(`snapshot`, `screenshot`, `navigate`)이 같은 프로필에서 동작함

## 자주 오해되는 오류

각 메시지를 계층별 단서로 취급하세요:

- `control-ui-insecure-auth`
  - CDP 전송 문제가 아니라 UI origin / secure-context 문제
- `token_missing`
  - 인증 구성 문제
- `pairing required`
  - 디바이스 승인 문제
- `Remote CDP for profile "remote" is not reachable`
  - WSL2가 구성된 `cdpUrl`에 도달할 수 없음
- `Browser attachOnly is enabled and CDP websocket for profile "remote" is not reachable`
  - HTTP 엔드포인트는 응답했지만 DevTools WebSocket은 여전히 열 수 없음
- 원격 세션 이후 오래된 viewport / dark-mode / locale / offline 재정의가 남아 있음
  - `openclaw browser stop --browser-profile remote`를 실행하세요
  - 이렇게 하면 gateway나 외부 브라우저를 다시 시작하지 않고도 활성 제어 세션을 닫고 Playwright/CDP 에뮬레이션 상태를 해제합니다
- `gateway timeout after 1500ms`
  - 여전히 CDP 도달성 문제이거나 원격 엔드포인트가 느리거나 도달 불가한 경우가 많음
- `No Chrome tabs found for profile="user"`
  - host-local 탭이 없는 상황에서 로컬 Chrome MCP 프로필을 선택한 경우

## 빠른 분류 체크리스트

1. Windows: `curl http://127.0.0.1:9222/json/version`가 동작하나요?
2. WSL2: `curl http://WINDOWS_HOST_OR_IP:9222/json/version`가 동작하나요?
3. OpenClaw 구성: `browser.profiles.<name>.cdpUrl`이 정확히 그 WSL2 도달 가능 주소를 사용하나요?
4. Control UI: LAN IP 대신 `http://127.0.0.1:18789/`를 열고 있나요?
5. 원시 원격 CDP 대신 WSL2와 Windows 사이에서 `existing-session`을 사용하려고 하고 있나요?

## 실용적인 결론

이 설정은 대체로 실현 가능합니다. 어려운 점은 브라우저 전송, Control UI origin 보안, 토큰/페어링이 각각 독립적으로 실패할 수 있으면서 사용자 입장에서는 비슷하게 보일 수 있다는 것입니다.

확실하지 않다면:

- 먼저 Windows Chrome 엔드포인트를 로컬에서 검증하세요
- 그다음 WSL2에서 동일한 엔드포인트를 검증하세요
- 그 후에만 OpenClaw 구성이나 Control UI 인증을 디버깅하세요
