---
read_when:
    - 연결/인증 문제가 있어 안내형 수정이 필요할 때
    - 업데이트 후 정상 여부를 점검하려고 할 때
summary: '`openclaw doctor`용 CLI 참조(상태 점검 + 안내형 복구)'
title: doctor
x-i18n:
    generated_at: "2026-04-05T12:37:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: d257a9e2797b4b0b50c1020165c8a1cd6a2342381bf9c351645ca37494c881e1
    source_path: cli/doctor.md
    workflow: 15
---

# `openclaw doctor`

게이트웨이와 채널을 위한 상태 점검 + 빠른 수정 도구입니다.

관련 문서:

- 문제 해결: [문제 해결](/gateway/troubleshooting)
- 보안 감사: [보안](/gateway/security)

## 예시

```bash
openclaw doctor
openclaw doctor --repair
openclaw doctor --deep
openclaw doctor --repair --non-interactive
openclaw doctor --generate-gateway-token
```

## 옵션

- `--no-workspace-suggestions`: 워크스페이스 메모리/검색 제안을 비활성화
- `--yes`: 프롬프트 없이 기본값 수락
- `--repair`: 프롬프트 없이 권장 복구 적용
- `--fix`: `--repair`의 별칭
- `--force`: 필요 시 사용자 지정 서비스 구성을 덮어쓰는 것을 포함한 적극적인 복구 적용
- `--non-interactive`: 프롬프트 없이 실행, 안전한 마이그레이션만 수행
- `--generate-gateway-token`: 게이트웨이 토큰 생성 및 구성
- `--deep`: 추가 게이트웨이 설치를 찾기 위해 시스템 서비스를 스캔

참고:

- 대화형 프롬프트(키체인/OAuth 수정 등)는 stdin이 TTY이고 `--non-interactive`가 **설정되지 않은 경우에만** 실행됩니다. 헤드리스 실행(cron, Telegram, 터미널 없음)에서는 프롬프트를 건너뜁니다.
- `--fix`(`--repair`의 별칭)는 백업을 `~/.openclaw/openclaw.json.bak`에 기록하고 알 수 없는 config 키를 제거하며, 제거된 각 항목을 나열합니다.
- 이제 상태 무결성 검사는 세션 디렉터리의 고아 transcript 파일을 감지하며, 공간을 안전하게 회수하기 위해 이를 `.deleted.<timestamp>`로 보관할 수 있습니다.
- Doctor는 또한 `~/.openclaw/cron/jobs.json`(또는 `cron.store`)에서 레거시 cron 작업 형식을 스캔하며, 스케줄러가 런타임에 자동 정규화하기 전에 이를 제자리에서 다시 쓸 수 있습니다.
- Doctor는 레거시 평면 Talk config(`talk.voiceId`, `talk.modelId` 등)를 `talk.provider` + `talk.providers.<provider>`로 자동 마이그레이션합니다.
- 이제 `doctor --fix`를 반복 실행해도 차이가 객체 키 순서뿐인 경우 Talk 정규화를 보고하거나 적용하지 않습니다.
- Doctor에는 메모리 검색 준비 상태 점검이 포함되어 있으며, 임베딩 자격 증명이 없을 경우 `openclaw configure --section model`을 권장할 수 있습니다.
- sandbox 모드가 활성화되어 있지만 Docker를 사용할 수 없는 경우, doctor는 해결 방법(`install Docker` 또는 `openclaw config set agents.defaults.sandbox.mode off`)과 함께 신호가 강한 경고를 보고합니다.
- `gateway.auth.token`/`gateway.auth.password`가 SecretRef로 관리되고 현재 명령 경로에서 사용할 수 없는 경우, doctor는 읽기 전용 경고를 보고하며 일반 텍스트 대체 자격 증명을 쓰지 않습니다.
- 수정 경로에서 채널 SecretRef 검사가 실패하더라도, doctor는 조기 종료하지 않고 계속 진행하며 경고를 보고합니다.
- Telegram `allowFrom` 사용자 이름 자동 해석(`doctor --fix`)에는 현재 명령 경로에서 해석 가능한 Telegram 토큰이 필요합니다. 토큰 검사를 사용할 수 없으면 doctor는 경고를 보고하고 해당 실행에서는 자동 해석을 건너뜁니다.

## macOS: `launchctl` env 재정의

이전에 `launchctl setenv OPENCLAW_GATEWAY_TOKEN ...`(또는 `...PASSWORD`)를 실행한 적이 있다면, 그 값이 config 파일을 재정의하여 지속적인 “unauthorized” 오류를 일으킬 수 있습니다.

```bash
launchctl getenv OPENCLAW_GATEWAY_TOKEN
launchctl getenv OPENCLAW_GATEWAY_PASSWORD

launchctl unsetenv OPENCLAW_GATEWAY_TOKEN
launchctl unsetenv OPENCLAW_GATEWAY_PASSWORD
```
