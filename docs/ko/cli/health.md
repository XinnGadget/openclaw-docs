---
read_when:
    - 실행 중인 Gateway의 상태를 빠르게 확인하려는 경우
summary: '`openclaw health`용 CLI 참조(RPC를 통한 gateway 상태 스냅샷)'
title: health
x-i18n:
    generated_at: "2026-04-05T12:37:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4ed2b9ceefee6159cabaae9172d2d88174626456e7503d5d2bcd142634188ff0
    source_path: cli/health.md
    workflow: 15
---

# `openclaw health`

실행 중인 Gateway에서 상태 정보를 가져옵니다.

옵션:

- `--json`: 기계가 읽을 수 있는 출력
- `--timeout <ms>`: 밀리초 단위 연결 타임아웃(기본값 `10000`)
- `--verbose`: 자세한 로깅
- `--debug`: `--verbose`의 별칭

예시:

```bash
openclaw health
openclaw health --json
openclaw health --timeout 2500
openclaw health --verbose
openclaw health --debug
```

참고:

- 기본 `openclaw health`는 실행 중인 gateway에 상태 스냅샷을 요청합니다. gateway에 이미 최신 캐시 스냅샷이 있으면, 해당 캐시된 페이로드를 반환하고 백그라운드에서 새로 고칠 수 있습니다.
- `--verbose`는 라이브 프로브를 강제하고, gateway 연결 세부 정보를 출력하며, 사람이 읽을 수 있는 출력을 구성된 모든 계정과 agent에 걸쳐 확장합니다.
- 여러 agent가 구성된 경우 출력에는 agent별 세션 저장소가 포함됩니다.
