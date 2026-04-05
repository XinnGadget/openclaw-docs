---
read_when:
    - 일반적인 작업 예시를 위해 `openclaw browser`를 사용할 때
    - 노드 호스트를 통해 다른 머신에서 실행 중인 브라우저를 제어하려고 할 때
    - Chrome MCP를 통해 로컬의 로그인된 Chrome에 연결하려고 할 때
summary: '`openclaw browser`용 CLI 참조(수명 주기, 프로필, 탭, 작업, 상태, 디버깅)'
title: browser
x-i18n:
    generated_at: "2026-04-05T12:37:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: c89a7483dd733863dd8ebd47a14fbb411808ad07daaed515c1270978de9157e7
    source_path: cli/browser.md
    workflow: 15
---

# `openclaw browser`

OpenClaw의 브라우저 제어 표면을 관리하고 브라우저 작업(수명 주기, 프로필, 탭, 스냅샷, 스크린샷, 탐색, 입력, 상태 에뮬레이션, 디버깅)을 실행합니다.

관련 문서:

- 브라우저 도구 + API: [Browser tool](/tools/browser)

## 공통 플래그

- `--url <gatewayWsUrl>`: 게이트웨이 WebSocket URL(config 기본값 사용).
- `--token <token>`: 게이트웨이 토큰(필요한 경우).
- `--timeout <ms>`: 요청 타임아웃(ms).
- `--expect-final`: 최종 게이트웨이 응답을 기다립니다.
- `--browser-profile <name>`: 브라우저 프로필 선택(config의 기본값 사용).
- `--json`: 기계 판독 가능 출력(지원되는 경우).

## 빠른 시작(로컬)

```bash
openclaw browser profiles
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

## 수명 주기

```bash
openclaw browser status
openclaw browser start
openclaw browser stop
openclaw browser --browser-profile openclaw reset-profile
```

참고:

- `attachOnly` 및 원격 CDP 프로필의 경우, `openclaw browser stop`은
  OpenClaw가 브라우저 프로세스를 직접 시작하지 않았더라도 활성 제어 세션을 닫고
  임시 에뮬레이션 재정의를 지웁니다.
- 로컬 관리형 프로필의 경우, `openclaw browser stop`은 생성된 브라우저
  프로세스를 중지합니다.

## 명령이 없는 경우

`openclaw browser`가 알 수 없는 명령이라면
`~/.openclaw/openclaw.json`의 `plugins.allow`를 확인하세요.

`plugins.allow`가 있으면 번들 브라우저 plugin이
명시적으로 나열되어 있어야 합니다:

```json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
```

plugin 허용 목록에서 `browser`가 제외되어 있으면
`browser.enabled=true`만으로는 CLI 하위 명령이 복구되지 않습니다.

관련 문서: [Browser tool](/tools/browser#missing-browser-command-or-tool)

## 프로필

프로필은 이름 있는 브라우저 라우팅 구성입니다. 실제로는 다음과 같습니다:

- `openclaw`: 전용 OpenClaw 관리 Chrome 인스턴스를 시작하거나 연결합니다(격리된 사용자 데이터 디렉터리).
- `user`: Chrome DevTools MCP를 통해 기존의 로그인된 Chrome 세션을 제어합니다.
- 사용자 지정 CDP 프로필: 로컬 또는 원격 CDP 엔드포인트를 가리킵니다.

```bash
openclaw browser profiles
openclaw browser create-profile --name work --color "#FF5A36"
openclaw browser create-profile --name chrome-live --driver existing-session
openclaw browser create-profile --name remote --cdp-url https://browser-host.example.com
openclaw browser delete-profile --name work
```

특정 프로필 사용:

```bash
openclaw browser --browser-profile work tabs
```

## 탭

```bash
openclaw browser tabs
openclaw browser tab new
openclaw browser tab select 2
openclaw browser tab close 2
openclaw browser open https://docs.openclaw.ai
openclaw browser focus <targetId>
openclaw browser close <targetId>
```

## 스냅샷 / 스크린샷 / 작업

스냅샷:

```bash
openclaw browser snapshot
```

스크린샷:

```bash
openclaw browser screenshot
openclaw browser screenshot --full-page
openclaw browser screenshot --ref e12
```

참고:

- `--full-page`는 페이지 캡처 전용이며 `--ref`
  또는 `--element`와 함께 사용할 수 없습니다.
- `existing-session` / `user` 프로필은 페이지 스크린샷과 스냅샷 출력의 `--ref`
  스크린샷은 지원하지만 CSS `--element` 스크린샷은 지원하지 않습니다.

탐색/클릭/입력(ref 기반 UI 자동화):

```bash
openclaw browser navigate https://example.com
openclaw browser click <ref>
openclaw browser type <ref> "hello"
openclaw browser press Enter
openclaw browser hover <ref>
openclaw browser scrollintoview <ref>
openclaw browser drag <startRef> <endRef>
openclaw browser select <ref> OptionA OptionB
openclaw browser fill --fields '[{"ref":"1","value":"Ada"}]'
openclaw browser wait --text "Done"
openclaw browser evaluate --fn '(el) => el.textContent' --ref <ref>
```

파일 + 대화상자 헬퍼:

```bash
openclaw browser upload /tmp/openclaw/uploads/file.pdf --ref <ref>
openclaw browser waitfordownload
openclaw browser download <ref> report.pdf
openclaw browser dialog --accept
```

## 상태 및 저장소

뷰포트 + 에뮬레이션:

```bash
openclaw browser resize 1280 720
openclaw browser set viewport 1280 720
openclaw browser set offline on
openclaw browser set media dark
openclaw browser set timezone Europe/London
openclaw browser set locale en-GB
openclaw browser set geo 51.5074 -0.1278 --accuracy 25
openclaw browser set device "iPhone 14"
openclaw browser set headers '{"x-test":"1"}'
openclaw browser set credentials myuser mypass
```

쿠키 + 저장소:

```bash
openclaw browser cookies
openclaw browser cookies set session abc123 --url https://example.com
openclaw browser cookies clear
openclaw browser storage local get
openclaw browser storage local set token abc123
openclaw browser storage session clear
```

## 디버깅

```bash
openclaw browser console --level error
openclaw browser pdf
openclaw browser responsebody "**/api"
openclaw browser highlight <ref>
openclaw browser errors --clear
openclaw browser requests --filter api
openclaw browser trace start
openclaw browser trace stop --out trace.zip
```

## MCP를 통한 기존 Chrome

기본 제공 `user` 프로필을 사용하거나, 직접 `existing-session` 프로필을 만드세요:

```bash
openclaw browser --browser-profile user tabs
openclaw browser create-profile --name chrome-live --driver existing-session
openclaw browser create-profile --name brave-live --driver existing-session --user-data-dir "~/Library/Application Support/BraveSoftware/Brave-Browser"
openclaw browser --browser-profile chrome-live tabs
```

이 경로는 호스트 전용입니다. Docker, 헤드리스 서버, Browserless 또는 기타 원격 설정에서는 대신 CDP 프로필을 사용하세요.

현재 existing-session 제한 사항:

- 스냅샷 기반 작업은 CSS 선택자가 아니라 ref를 사용합니다
- `click`은 왼쪽 클릭만 지원합니다
- `type`은 `slowly=true`를 지원하지 않습니다
- `press`는 `delayMs`를 지원하지 않습니다
- `hover`, `scrollintoview`, `drag`, `select`, `fill`, `evaluate`는
  호출별 타임아웃 재정의를 거부합니다
- `select`는 값 하나만 지원합니다
- `wait --load networkidle`은 지원되지 않습니다
- 파일 업로드는 `--ref` / `--input-ref`가 필요하며 CSS
  `--element`를 지원하지 않고, 현재 한 번에 파일 하나만 지원합니다
- 대화상자 훅은 `--timeout`을 지원하지 않습니다
- 스크린샷은 페이지 캡처와 `--ref`는 지원하지만 CSS `--element`는 지원하지 않습니다
- `responsebody`, 다운로드 가로채기, PDF 내보내기, 일괄 작업은 여전히
  관리형 브라우저 또는 원시 CDP 프로필이 필요합니다

## 원격 브라우저 제어(노드 호스트 프록시)

게이트웨이가 브라우저와 다른 머신에서 실행되는 경우, Chrome/Brave/Edge/Chromium이 있는 머신에서 **노드 호스트**를 실행하세요. 게이트웨이는 브라우저 작업을 해당 노드로 프록시합니다(별도의 브라우저 제어 서버는 필요하지 않음).

자동 라우팅은 `gateway.nodes.browser.mode`로 제어하고, 여러 노드가 연결되어 있을 경우 특정 노드를 고정하려면 `gateway.nodes.browser.node`를 사용하세요.

보안 + 원격 설정: [Browser tool](/tools/browser), [Remote access](/gateway/remote), [Tailscale](/gateway/tailscale), [Security](/gateway/security)
