---
read_when:
    - 전체 CLI 온보딩 없이 첫 실행 설정을 진행할 때
    - 기본 워크스페이스 경로를 설정하려고 할 때
summary: '`openclaw setup`용 CLI 참조(config + 워크스페이스 초기화)'
title: setup
x-i18n:
    generated_at: "2026-04-05T12:38:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: f538aac341c749043ad959e35f2ed99c844ab8c3500ff59aa159d940bd301792
    source_path: cli/setup.md
    workflow: 15
---

# `openclaw setup`

`~/.openclaw/openclaw.json`과 에이전트 워크스페이스를 초기화합니다.

관련 문서:

- 시작하기: [시작하기](/ko/start/getting-started)
- CLI 온보딩: [온보딩(CLI)](/ko/start/wizard)

## 예시

```bash
openclaw setup
openclaw setup --workspace ~/.openclaw/workspace
openclaw setup --wizard
openclaw setup --non-interactive --mode remote --remote-url wss://gateway-host:18789 --remote-token <token>
```

## 옵션

- `--workspace <dir>`: 에이전트 워크스페이스 디렉터리(`agents.defaults.workspace`로 저장)
- `--wizard`: 온보딩 실행
- `--non-interactive`: 프롬프트 없이 온보딩 실행
- `--mode <local|remote>`: 온보딩 모드
- `--remote-url <url>`: 원격 게이트웨이 WebSocket URL
- `--remote-token <token>`: 원격 게이트웨이 토큰

setup을 통해 온보딩 실행:

```bash
openclaw setup --wizard
```

참고:

- 일반 `openclaw setup`은 전체 온보딩 흐름 없이 config + 워크스페이스를 초기화합니다.
- 온보딩 플래그가 하나라도 있으면(`--wizard`, `--non-interactive`, `--mode`, `--remote-url`, `--remote-token`) 온보딩이 자동 실행됩니다.
