---
read_when:
    - CLI 설치는 유지한 채 로컬 상태를 지우고 싶을 때
    - 무엇이 제거될지 dry-run으로 확인하고 싶을 때
summary: '`openclaw reset`용 CLI 참조(로컬 상태/구성 재설정)'
title: reset
x-i18n:
    generated_at: "2026-04-05T12:38:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad464700f948bebe741ec309f25150714f0b280834084d4f531327418a42c79b
    source_path: cli/reset.md
    workflow: 15
---

# `openclaw reset`

로컬 구성/상태를 재설정합니다(CLI 설치는 유지됨).

옵션:

- `--scope <scope>`: `config`, `config+creds+sessions`, 또는 `full`
- `--yes`: 확인 프롬프트 건너뛰기
- `--non-interactive`: 프롬프트 비활성화, `--scope`와 `--yes` 필요
- `--dry-run`: 파일을 제거하지 않고 수행할 작업 출력

예시:

```bash
openclaw backup create
openclaw reset
openclaw reset --dry-run
openclaw reset --scope config --yes --non-interactive
openclaw reset --scope config+creds+sessions --yes --non-interactive
openclaw reset --scope full --yes --non-interactive
```

참고:

- 로컬 상태를 제거하기 전에 복원 가능한 스냅샷이 필요하다면 먼저 `openclaw backup create`를 실행하세요.
- `--scope`를 생략하면, `openclaw reset`은 무엇을 제거할지 선택하는 대화형 프롬프트를 사용합니다.
- `--non-interactive`는 `--scope`와 `--yes`가 모두 설정된 경우에만 유효합니다.
