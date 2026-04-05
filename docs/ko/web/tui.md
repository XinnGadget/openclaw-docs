---
read_when:
    - TUI에 대한 초보자 친화적인 안내가 필요한 경우
    - TUI 기능, 명령, 단축키의 전체 목록이 필요한 경우
summary: '터미널 UI(TUI): 어느 머신에서나 Gateway에 연결'
title: TUI
x-i18n:
    generated_at: "2026-04-05T12:59:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: a73f70d65ecc7bff663e8df28c07d70d2920d4732fbb8288c137d65b8653ac52
    source_path: web/tui.md
    workflow: 15
---

# TUI (터미널 UI)

## 빠른 시작

1. Gateway를 시작합니다.

```bash
openclaw gateway
```

2. TUI를 엽니다.

```bash
openclaw tui
```

3. 메시지를 입력하고 Enter를 누릅니다.

원격 Gateway:

```bash
openclaw tui --url ws://<host>:<port> --token <gateway-token>
```

Gateway가 비밀번호 인증을 사용하는 경우 `--password`를 사용하세요.

## 화면 구성

- 헤더: 연결 URL, 현재 에이전트, 현재 세션
- 채팅 로그: 사용자 메시지, 어시스턴트 응답, 시스템 알림, 도구 카드
- 상태 줄: 연결/실행 상태(connecting, running, streaming, idle, error)
- 푸터: 연결 상태 + 에이전트 + 세션 + 모델 + think/fast/verbose/reasoning + 토큰 수 + deliver
- 입력: 자동 완성이 있는 텍스트 편집기

## 개념 이해: 에이전트 + 세션

- 에이전트는 고유한 슬러그입니다(예: `main`, `research`). Gateway가 목록을 노출합니다.
- 세션은 현재 에이전트에 속합니다.
- 세션 키는 `agent:<agentId>:<sessionKey>` 형식으로 저장됩니다.
  - `/session main`을 입력하면 TUI는 이를 `agent:<currentAgent>:main`으로 확장합니다.
  - `/session agent:other:main`을 입력하면 해당 에이전트 세션으로 명시적으로 전환합니다.
- 세션 범위:
  - `per-sender`(기본값): 각 에이전트는 여러 세션을 가집니다.
  - `global`: TUI는 항상 `global` 세션을 사용합니다(선택기가 비어 있을 수 있음).
- 현재 에이전트 + 세션은 항상 푸터에 표시됩니다.

## 전송 + 전달

- 메시지는 Gateway로 전송되며, 공급자로의 전달은 기본적으로 꺼져 있습니다.
- 전달을 켜려면:
  - `/deliver on`
  - 또는 Settings 패널
  - 또는 `openclaw tui --deliver`로 시작

## 선택기 + 오버레이

- 모델 선택기: 사용 가능한 모델을 나열하고 세션 재정의를 설정합니다.
- 에이전트 선택기: 다른 에이전트를 선택합니다.
- 세션 선택기: 현재 에이전트의 세션만 표시합니다.
- 설정: deliver, 도구 출력 확장, thinking 표시를 전환합니다.

## 키보드 단축키

- Enter: 메시지 전송
- Esc: 활성 실행 중단
- Ctrl+C: 입력 지우기(두 번 누르면 종료)
- Ctrl+D: 종료
- Ctrl+L: 모델 선택기
- Ctrl+G: 에이전트 선택기
- Ctrl+P: 세션 선택기
- Ctrl+O: 도구 출력 확장 전환
- Ctrl+T: thinking 표시 전환(히스토리 다시 로드)

## 슬래시 명령

핵심:

- `/help`
- `/status`
- `/agent <id>` (또는 `/agents`)
- `/session <key>` (또는 `/sessions`)
- `/model <provider/model>` (또는 `/models`)

세션 제어:

- `/think <off|minimal|low|medium|high>`
- `/fast <status|on|off>`
- `/verbose <on|full|off>`
- `/reasoning <on|off|stream>`
- `/usage <off|tokens|full>`
- `/elevated <on|off|ask|full>` (별칭: `/elev`)
- `/activation <mention|always>`
- `/deliver <on|off>`

세션 수명 주기:

- `/new` 또는 `/reset` (세션 초기화)
- `/abort` (활성 실행 중단)
- `/settings`
- `/exit`

기타 Gateway 슬래시 명령(예: `/context`)은 Gateway로 전달되고 시스템 출력으로 표시됩니다. [슬래시 명령](/tools/slash-commands)을 참조하세요.

## 로컬 셸 명령

- 줄 앞에 `!`를 붙이면 TUI 호스트에서 로컬 셸 명령을 실행합니다.
- TUI는 세션마다 한 번 로컬 실행 허용 여부를 묻고, 거부하면 해당 세션에서 `!`가 비활성화된 상태로 유지됩니다.
- 명령은 TUI 작업 디렉터리에서 새 비대화형 셸로 실행됩니다(`cd`/env는 유지되지 않음).
- 로컬 셸 명령은 환경 변수로 `OPENCLAW_SHELL=tui-local`을 받습니다.
- 단독 `!`는 일반 메시지로 전송되며, 앞에 공백이 있으면 로컬 exec가 트리거되지 않습니다.

## 도구 출력

- 도구 호출은 인자 + 결과가 포함된 카드로 표시됩니다.
- Ctrl+O는 축소/확장 보기를 전환합니다.
- 도구가 실행되는 동안 부분 업데이트가 같은 카드로 스트리밍됩니다.

## 터미널 색상

- TUI는 어시스턴트 본문 텍스트를 터미널의 기본 전경색으로 유지하므로 어두운 터미널과 밝은 터미널 모두에서 읽기 쉽습니다.
- 터미널이 밝은 배경을 사용하고 자동 감지가 잘못되면 `openclaw tui`를 실행하기 전에 `OPENCLAW_THEME=light`를 설정하세요.
- 대신 원래의 어두운 팔레트를 강제하려면 `OPENCLAW_THEME=dark`를 설정하세요.

## 히스토리 + 스트리밍

- 연결 시 TUI는 최신 히스토리(기본값 200개 메시지)를 불러옵니다.
- 스트리밍 응답은 완료될 때까지 제자리에서 갱신됩니다.
- TUI는 더 풍부한 도구 카드를 위해 에이전트 도구 이벤트도 수신합니다.

## 연결 세부 정보

- TUI는 `mode: "tui"`로 Gateway에 등록됩니다.
- 재연결은 시스템 메시지로 표시되며, 이벤트 누락은 로그에 표시됩니다.

## 옵션

- `--url <url>`: Gateway WebSocket URL(기본값은 구성 또는 `ws://127.0.0.1:<port>`)
- `--token <token>`: Gateway 토큰(필요한 경우)
- `--password <password>`: Gateway 비밀번호(필요한 경우)
- `--session <key>`: 세션 키(기본값: `main`, 또는 범위가 global이면 `global`)
- `--deliver`: 어시스턴트 응답을 공급자로 전달(기본값 꺼짐)
- `--thinking <level>`: 전송 시 thinking 수준 재정의
- `--message <text>`: 연결 후 초기 메시지 전송
- `--timeout-ms <ms>`: 에이전트 타임아웃(ms)(기본값은 `agents.defaults.timeoutSeconds`)
- `--history-limit <n>`: 불러올 히스토리 항목 수(기본값 `200`)

참고: `--url`을 설정하면 TUI는 구성 또는 환경 자격 증명으로 폴백하지 않습니다.
`--token` 또는 `--password`를 명시적으로 전달하세요. 명시적 자격 증명이 없으면 오류가 발생합니다.

## 문제 해결

메시지를 보낸 후 출력이 없는 경우:

- TUI에서 `/status`를 실행해 Gateway가 연결되어 있고 idle/busy 상태인지 확인하세요.
- Gateway 로그를 확인하세요: `openclaw logs --follow`
- 에이전트가 실행 가능한지 확인하세요: `openclaw status` 및 `openclaw models status`
- 채팅 채널에 메시지가 표시되기를 기대한다면 전달을 활성화하세요(`/deliver on` 또는 `--deliver`).

## 연결 문제 해결

- `disconnected`: Gateway가 실행 중인지, `--url/--token/--password`가 올바른지 확인하세요.
- 선택기에 에이전트가 없음: `openclaw agents list`와 라우팅 구성을 확인하세요.
- 세션 선택기가 비어 있음: global 범위에 있거나 아직 세션이 없을 수 있습니다.

## 관련 문서

- [Control UI](/web/control-ui) — 웹 기반 제어 인터페이스
- [CLI 참조](/cli) — 전체 CLI 명령 참조
