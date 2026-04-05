---
read_when:
    - 어떤 Skills를 사용할 수 있고 실행 준비가 되었는지 확인하려고 할 때
    - ClawHub에서 Skills를 검색, 설치 또는 업데이트하려고 할 때
    - Skills에 필요한 바이너리/env/config 누락을 디버깅하려고 할 때
summary: '`openclaw skills`용 CLI 참조(search/install/update/list/info/check)'
title: Skills
x-i18n:
    generated_at: "2026-04-05T12:39:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 11af59b1b6bff19cc043acd8d67bdd4303201d3f75f23c948b83bf14882c7bb1
    source_path: cli/skills.md
    workflow: 15
---

# `openclaw skills`

로컬 Skills를 검사하고 ClawHub에서 Skills를 설치/업데이트합니다.

관련 항목:

- Skills 시스템: [Skills](/tools/skills)
- Skills 구성: [Skills config](/tools/skills-config)
- ClawHub 설치: [ClawHub](/tools/clawhub)

## 명령

```bash
openclaw skills search "calendar"
openclaw skills search --limit 20 --json
openclaw skills install <slug>
openclaw skills install <slug> --version <version>
openclaw skills install <slug> --force
openclaw skills update <slug>
openclaw skills update --all
openclaw skills list
openclaw skills list --eligible
openclaw skills list --json
openclaw skills list --verbose
openclaw skills info <name>
openclaw skills info <name> --json
openclaw skills check
openclaw skills check --json
```

`search`/`install`/`update`는 ClawHub를 직접 사용하며 활성
워크스페이스의 `skills/` 디렉터리에 설치됩니다. `list`/`info`/`check`는 여전히 현재
워크스페이스와 구성에서 볼 수 있는 로컬 Skills를 검사합니다.

이 CLI `install` 명령은 ClawHub에서 Skill 폴더를 다운로드합니다. 온보딩 또는 Skills 설정에서
트리거되는 Gateway 기반 Skill 의존성 설치는 대신 별도의
`skills.install` 요청 경로를 사용합니다.

참고:

- `search [query...]`는 선택적 쿼리를 받습니다. 이를 생략하면 기본
  ClawHub 검색 피드를 탐색합니다.
- `search --limit <n>`은 반환되는 결과 수를 제한합니다.
- `install --force`는 동일한
  slug에 대해 기존 워크스페이스 Skill 폴더를 덮어씁니다.
- `update --all`은 활성 워크스페이스에서 추적되는 ClawHub 설치만 업데이트합니다.
- 하위 명령이 제공되지 않으면 `list`가 기본 동작입니다.
- `list`, `info`, `check`는 렌더링된 출력을 stdout에 씁니다.
  `--json`과 함께 사용하면 기계가 읽을 수 있는 페이로드가 파이프와 스크립트를 위해 stdout에 유지됩니다.
