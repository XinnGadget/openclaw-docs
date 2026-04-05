---
read_when:
    - 로깅 출력 또는 형식을 변경할 때
    - CLI 또는 gateway 출력을 디버깅할 때
summary: 로깅 표면, 파일 로그, WS 로그 스타일, 콘솔 서식
title: Gateway 로깅
x-i18n:
    generated_at: "2026-04-05T12:42:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: 465fe66ae6a3bc844e75d3898aed15b3371481c4fe89ede40e5a9377e19bb74c
    source_path: gateway/logging.md
    workflow: 15
---

# 로깅

사용자 대상 개요(CLI + Control UI + config)는 [/logging](/logging)을 참조하세요.

OpenClaw에는 두 가지 로그 “표면”이 있습니다:

- **콘솔 출력**(터미널 / Debug UI에서 보이는 것)
- gateway 로거가 기록하는 **파일 로그**(JSON lines)

## 파일 기반 로거

- 기본 롤링 로그 파일은 `/tmp/openclaw/` 아래에 있습니다(하루에 파일 하나): `openclaw-YYYY-MM-DD.log`
  - 날짜는 gateway 호스트의 로컬 시간대를 사용합니다.
- 로그 파일 경로와 레벨은 `~/.openclaw/openclaw.json`에서 구성할 수 있습니다:
  - `logging.file`
  - `logging.level`

파일 형식은 한 줄당 하나의 JSON 객체입니다.

Control UI Logs 탭은 gateway를 통해 이 파일을 tail합니다(`logs.tail`).
CLI도 동일하게 할 수 있습니다:

```bash
openclaw logs --follow
```

**Verbose와 로그 레벨**

- **파일 로그**는 오직 `logging.level`로만 제어됩니다.
- `--verbose`는 **콘솔 상세도**(및 WS 로그 스타일)에만 영향을 주며, 파일 로그 레벨은 높이지 않습니다.
- verbose 전용 세부 정보를 파일 로그에 캡처하려면 `logging.level`을 `debug` 또는 `trace`로 설정하세요.

## 콘솔 캡처

CLI는 `console.log/info/warn/error/debug/trace`를 캡처해 파일 로그에 기록하면서,
동시에 stdout/stderr에도 출력합니다.

콘솔 상세도는 다음을 통해 별도로 조정할 수 있습니다:

- `logging.consoleLevel` (기본값 `info`)
- `logging.consoleStyle` (`pretty` | `compact` | `json`)

## 도구 요약 마스킹

상세 도구 요약(예: `🛠️ Exec: ...`)은 콘솔 스트림에 도달하기 전에 민감한 토큰을 마스킹할 수 있습니다. 이는 **도구 전용**이며 파일 로그는 변경하지 않습니다.

- `logging.redactSensitive`: `off` | `tools` (기본값: `tools`)
- `logging.redactPatterns`: 정규식 문자열 배열(기본값 재정의)
  - 원시 정규식 문자열(자동 `gi`)을 사용하거나, 사용자 지정 플래그가 필요하면 `/pattern/flags`를 사용하세요.
  - 일치 항목은 앞 6자 + 뒤 4자(길이 >= 18)를 유지하고 마스킹되며, 그보다 짧으면 `***`로 처리됩니다.
  - 기본값은 일반적인 키 할당, CLI 플래그, JSON 필드, bearer 헤더, PEM 블록, 널리 쓰이는 토큰 접두사를 포함합니다.

## Gateway WebSocket 로그

gateway는 두 가지 모드로 WebSocket 프로토콜 로그를 출력합니다:

- **일반 모드**(`--verbose` 없음): “흥미로운” RPC 결과만 출력합니다:
  - 오류(`ok=false`)
  - 느린 호출(기본 임계값: `>= 50ms`)
  - 파싱 오류
- **Verbose 모드**(`--verbose`): 모든 WS 요청/응답 트래픽을 출력합니다.

### WS 로그 스타일

`openclaw gateway`는 gateway별 스타일 전환을 지원합니다:

- `--ws-log auto` (기본값): 일반 모드는 최적화되고, verbose 모드는 compact 출력을 사용합니다
- `--ws-log compact`: verbose일 때 compact 출력(쌍으로 묶인 요청/응답)
- `--ws-log full`: verbose일 때 전체 프레임별 출력
- `--compact`: `--ws-log compact`의 별칭

예시:

```bash
# 최적화됨(오류/느린 호출만)
openclaw gateway

# 모든 WS 트래픽 표시(쌍으로 표시)
openclaw gateway --verbose --ws-log compact

# 모든 WS 트래픽 표시(전체 메타데이터)
openclaw gateway --verbose --ws-log full
```

## 콘솔 서식(서브시스템 로깅)

콘솔 포매터는 **TTY 인식형**이며 일관된 접두사가 붙은 줄을 출력합니다.
서브시스템 로거는 출력이 그룹화되고 훑어보기 쉽도록 유지합니다.

동작:

- 모든 줄에 **서브시스템 접두사**(예: `[gateway]`, `[canvas]`, `[tailscale]`)
- **서브시스템 색상**(서브시스템별로 고정) + 레벨 색상
- **출력이 TTY이거나 환경이 리치 터미널처럼 보일 때 색상 사용** (`TERM`/`COLORTERM`/`TERM_PROGRAM`), `NO_COLOR` 존중
- **축약된 서브시스템 접두사**: 앞의 `gateway/` + `channels/`는 제거하고 마지막 2개 세그먼트만 유지(예: `whatsapp/outbound`)
- **서브시스템별 하위 로거**(자동 접두사 + 구조화된 필드 `{ subsystem }`)
- QR/UX 출력을 위한 **`logRaw()`**(접두사 없음, 서식 없음)
- **콘솔 스타일**(예: `pretty | compact | json`)
- 파일 로그 레벨과 분리된 **콘솔 로그 레벨**(파일은 `logging.level`이 `debug`/`trace`로 설정되면 전체 세부 정보를 유지)
- **WhatsApp 메시지 본문**은 `debug`로 기록됨(보려면 `--verbose` 사용)

이렇게 하면 기존 파일 로그는 안정적으로 유지하면서 상호작용 출력은 훑어보기 쉽게 만듭니다.
