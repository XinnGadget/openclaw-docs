---
read_when:
    - gateway 서비스 및/또는 로컬 상태를 제거하려고 함
    - 먼저 dry-run을 하려고 함
summary: '`openclaw uninstall`용 CLI 참조(gateway 서비스 + 로컬 데이터 제거)'
title: uninstall
x-i18n:
    generated_at: "2026-04-05T12:39:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2123a4f9c7a070ef7e13c60dafc189053ef61ce189fa4f29449dd50987c1894c
    source_path: cli/uninstall.md
    workflow: 15
---

# `openclaw uninstall`

gateway 서비스 + 로컬 데이터를 제거합니다(CLI는 유지됨).

옵션:

- `--service`: gateway 서비스 제거
- `--state`: 상태 및 config 제거
- `--workspace`: workspace 디렉터리 제거
- `--app`: macOS 앱 제거
- `--all`: 서비스, 상태, workspace, 앱 제거
- `--yes`: 확인 프롬프트 건너뛰기
- `--non-interactive`: 프롬프트 비활성화, `--yes` 필요
- `--dry-run`: 파일을 제거하지 않고 수행 작업 출력

예시:

```bash
openclaw backup create
openclaw uninstall
openclaw uninstall --service --yes --non-interactive
openclaw uninstall --state --workspace --yes --non-interactive
openclaw uninstall --all --yes
openclaw uninstall --dry-run
```

참고:

- 상태 또는 workspaces를 제거하기 전에 복원 가능한 스냅샷을 원한다면 먼저 `openclaw backup create`를 실행하세요.
- `--all`은 서비스, 상태, workspace, 앱을 함께 제거하는 축약형입니다.
- `--non-interactive`에는 `--yes`가 필요합니다.
