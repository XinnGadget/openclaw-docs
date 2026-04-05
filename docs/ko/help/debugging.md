---
read_when:
    - reasoning 누출 여부를 위해 원시 모델 출력을 검사해야 할 때
    - 반복 작업 중 Gateway를 watch mode로 실행하고 싶을 때
    - 반복 가능한 디버깅 워크플로가 필요할 때
summary: '도구 디버깅: watch mode, 원시 모델 스트림, reasoning 누출 추적'
title: 디버깅
x-i18n:
    generated_at: "2026-04-05T12:44:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: f90d944ecc2e846ca0b26a162126ceefb3a3c6cf065c99b731359ec79d4289e3
    source_path: help/debugging.md
    workflow: 15
---

# 디버깅

이 페이지는 특히
provider가 reasoning을 일반 텍스트에 섞어 보내는 경우의 스트리밍 출력용 디버깅 도우미를 다룹니다.

## 런타임 디버그 재정의

채팅에서 `/debug`를 사용해 **런타임 전용** config 재정의를 설정하세요(디스크가 아닌 메모리).
`/debug`는 기본적으로 비활성화되어 있으며, `commands.debug: true`로 활성화합니다.
`openclaw.json`을 편집하지 않고 드문 설정을 전환해야 할 때 유용합니다.

예시:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset`은 모든 재정의를 지우고 온디스크 config로 되돌립니다.

## Gateway watch mode

빠른 반복 작업을 위해 파일 watcher 아래에서 gateway를 실행하세요:

```bash
pnpm gateway:watch
```

이는 다음에 매핑됩니다:

```bash
node scripts/watch-node.mjs gateway --force
```

watcher는 `src/` 아래의 빌드 관련 파일, extension 소스 파일,
extension `package.json` 및 `openclaw.plugin.json` 메타데이터, `tsconfig.json`,
`package.json`, `tsdown.config.ts` 변경 시 재시작합니다. Extension 메타데이터 변경은
`tsdown` 재빌드를 강제하지 않고 gateway를 재시작하며, 소스 및 config 변경은 여전히
먼저 `dist`를 다시 빌드합니다.

`gateway:watch` 뒤에 gateway CLI 플래그를 추가하면
매 재시작 때마다 그대로 전달됩니다.

## 개발 프로필 + 개발 gateway (`--dev`)

개발 프로필을 사용해 상태를 격리하고
디버깅용으로 안전하고 일회성인 설정을 띄우세요. `--dev` 플래그는 **두 가지**가 있습니다:

- **전역 `--dev` (프로필):** 상태를 `~/.openclaw-dev` 아래로 격리하고
  gateway 포트를 기본적으로 `19001`로 설정합니다(파생 포트도 함께 이동).
- **`gateway --dev`:** Gateway에 기본 config + workspace를 누락 시 자동 생성하도록 지시합니다
  (그리고 `BOOTSTRAP.md`는 건너뜀).

권장 흐름(개발 프로필 + 개발 부트스트랩):

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

아직 전역 설치가 없다면 `pnpm openclaw ...`로 CLI를 실행하세요.

이 동작이 하는 일:

1. **프로필 격리** (전역 `--dev`)
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001` (browser/canvas도 이에 맞춰 이동)

2. **개발 부트스트랩** (`gateway --dev`)
   - 누락 시 최소 config를 작성합니다 (`gateway.mode=local`, bind loopback).
   - `agent.workspace`를 개발 workspace로 설정합니다.
   - `agent.skipBootstrap=true`를 설정합니다 (`BOOTSTRAP.md` 없음).
   - 누락 시 다음 workspace 파일을 시드합니다:
     `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`.
   - 기본 IDENTITY: **C3‑PO** (protocol droid).
   - 개발 모드에서는 채널 provider를 건너뜁니다 (`OPENCLAW_SKIP_CHANNELS=1`).

재설정 흐름(새로 시작):

```bash
pnpm gateway:dev:reset
```

참고: `--dev`는 **전역** 프로필 플래그이므로 일부 runner가 이를 소비합니다.
명시적으로 써야 한다면 env var 형식을 사용하세요:

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset`은 config, 자격 증명, 세션, 개발 workspace를
`rm`이 아닌 `trash`로 삭제한 뒤, 기본 개발 설정을 다시 만듭니다.

팁: 비개발 gateway가 이미 실행 중이라면(launchd/systemd) 먼저 중지하세요:

```bash
openclaw gateway stop
```

## 원시 스트림 로깅(OpenClaw)

OpenClaw는 필터링/포맷팅 전에 **원시 어시스턴트 스트림**을 로그할 수 있습니다.
이것은 reasoning이 일반 텍스트 delta로 들어오는지
(또는 별도의 thinking 블록으로 들어오는지) 확인하는 가장 좋은 방법입니다.

CLI에서 활성화:

```bash
pnpm gateway:watch --raw-stream
```

선택적 경로 재정의:

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

동등한 env var:

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

기본 파일:

`~/.openclaw/logs/raw-stream.jsonl`

## 원시 청크 로깅(pi-mono)

블록으로 파싱되기 전에 **원시 OpenAI 호환 청크**를 캡처하려면
pi-mono가 별도의 로거를 노출합니다:

```bash
PI_RAW_STREAM=1
```

선택적 경로:

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

기본 파일:

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> 참고: 이는 pi-mono의
> `openai-completions` provider를 사용하는 프로세스에서만 출력됩니다.

## 보안 참고 사항

- 원시 스트림 로그에는 전체 프롬프트, 도구 출력, 사용자 데이터가 포함될 수 있습니다.
- 로그는 로컬에만 보관하고 디버깅 후 삭제하세요.
- 로그를 공유할 경우 먼저 비밀 정보와 PII를 제거하세요.
