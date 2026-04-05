---
read_when:
    - Pi 통합 코드 또는 테스트 작업을 할 때
    - Pi 전용 lint, 타입 검사 및 실시간 테스트 흐름을 실행할 때
summary: 'Pi 통합을 위한 개발자 워크플로: 빌드, 테스트 및 실시간 검증'
title: Pi 개발 워크플로
x-i18n:
    generated_at: "2026-04-05T12:48:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: f61ebe29ea38ac953a03fe848fe5ac6b6de4bace5e6955b76ae9a7d093eb0cc5
    source_path: pi-dev.md
    workflow: 15
---

# Pi 개발 워크플로

이 가이드는 OpenClaw에서 pi 통합 작업을 위한 합리적인 워크플로를 요약합니다.

## 타입 검사 및 린팅

- 기본 로컬 게이트: `pnpm check`
- 변경이 빌드 출력, 패키징 또는 lazy-loading/module 경계에 영향을 줄 수 있는 경우의 빌드 게이트: `pnpm build`
- Pi 관련 변경의 전체 랜딩 게이트: `pnpm check && pnpm test`

## Pi 테스트 실행

Vitest로 Pi 중심 테스트 세트를 직접 실행합니다:

```bash
pnpm test \
  "src/agents/pi-*.test.ts" \
  "src/agents/pi-embedded-*.test.ts" \
  "src/agents/pi-tools*.test.ts" \
  "src/agents/pi-settings.test.ts" \
  "src/agents/pi-tool-definition-adapter*.test.ts" \
  "src/agents/pi-hooks/**/*.test.ts"
```

실시간 provider 검증까지 포함하려면:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test src/agents/pi-embedded-runner-extraparams.live.test.ts
```

이 명령은 주요 Pi 단위 테스트 모음을 다룹니다:

- `src/agents/pi-*.test.ts`
- `src/agents/pi-embedded-*.test.ts`
- `src/agents/pi-tools*.test.ts`
- `src/agents/pi-settings.test.ts`
- `src/agents/pi-tool-definition-adapter.test.ts`
- `src/agents/pi-hooks/*.test.ts`

## 수동 테스트

권장 흐름:

- 게이트웨이를 dev 모드로 실행:
  - `pnpm gateway:dev`
- 에이전트를 직접 트리거:
  - `pnpm openclaw agent --message "Hello" --thinking low`
- 대화형 디버깅에는 TUI 사용:
  - `pnpm tui`

도구 호출 동작을 보려면 `read` 또는 `exec` 작업을 유도하는 프롬프트를 사용하여 도구 스트리밍과 페이로드 처리를 확인하세요.

## 초기 상태로 재설정

상태는 OpenClaw 상태 디렉터리 아래에 저장됩니다. 기본값은 `~/.openclaw`입니다. `OPENCLAW_STATE_DIR`가 설정되어 있으면 해당 디렉터리를 대신 사용하세요.

모든 것을 재설정하려면:

- config용 `openclaw.json`
- 모델 인증 프로필(API 키 + OAuth)용 `agents/<agentId>/agent/auth-profiles.json`
- 인증 프로필 저장소 외부에 아직 남아 있는 provider/channel 상태용 `credentials/`
- 에이전트 세션 기록용 `agents/<agentId>/sessions/`
- 세션 인덱스용 `agents/<agentId>/sessions/sessions.json`
- 레거시 경로가 존재하는 경우 `sessions/`
- 빈 워크스페이스를 원할 경우 `workspace/`

세션만 재설정하려면 해당 에이전트의 `agents/<agentId>/sessions/`만 삭제하세요. 인증을 유지하려면 `agents/<agentId>/agent/auth-profiles.json`과 `credentials/` 아래의 provider 상태는 그대로 두세요.

## 참고 자료

- [Testing](/help/testing)
- [시작하기](/ko/start/getting-started)
