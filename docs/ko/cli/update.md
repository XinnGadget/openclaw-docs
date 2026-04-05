---
read_when:
    - 소스 체크아웃을 안전하게 업데이트하고 싶을 때
    - '`--update` 단축 동작을 이해해야 할 때'
summary: '`openclaw update`용 CLI 참조(비교적 안전한 소스 업데이트 + gateway 자동 재시작)'
title: update
x-i18n:
    generated_at: "2026-04-05T12:39:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: 12c8098654b644c3666981d379f6c018e84fde56a5420f295d78052f9001bdad
    source_path: cli/update.md
    workflow: 15
---

# `openclaw update`

OpenClaw를 안전하게 업데이트하고 stable/beta/dev 채널 간에 전환합니다.

**npm/pnpm/bun**으로 설치한 경우(전역 설치, git 메타데이터 없음),
업데이트는 [Updating](/install/updating)의 패키지 관리자 흐름을 통해 수행됩니다.

## 사용법

```bash
openclaw update
openclaw update status
openclaw update wizard
openclaw update --channel beta
openclaw update --channel dev
openclaw update --tag beta
openclaw update --tag main
openclaw update --dry-run
openclaw update --no-restart
openclaw update --yes
openclaw update --json
openclaw --update
```

## 옵션

- `--no-restart`: 업데이트가 성공한 후 Gateway 서비스를 재시작하지 않습니다.
- `--channel <stable|beta|dev>`: 업데이트 채널 설정(git + npm, config에 유지됨).
- `--tag <dist-tag|version|spec>`: 이번 업데이트에만 패키지 대상을 재정의합니다. 패키지 설치의 경우 `main`은 `github:openclaw/openclaw#main`에 매핑됩니다.
- `--dry-run`: config 쓰기, 설치, plugin 동기화, 재시작 없이 계획된 업데이트 작업(채널/태그/대상/재시작 흐름)을 미리 봅니다.
- `--json`: 기계가 읽을 수 있는 `UpdateRunResult` JSON을 출력합니다.
- `--timeout <seconds>`: 단계별 시간 초과(기본값 1200초).
- `--yes`: 확인 프롬프트를 건너뜁니다(예: 다운그레이드 확인)

참고: 이전 버전은 구성을 손상시킬 수 있으므로 다운그레이드에는 확인이 필요합니다.

## `update status`

활성 업데이트 채널 + git 태그/브랜치/SHA(소스 체크아웃의 경우)와 업데이트 가능 여부를 표시합니다.

```bash
openclaw update status
openclaw update status --json
openclaw update status --timeout 10
```

옵션:

- `--json`: 기계가 읽을 수 있는 상태 JSON을 출력합니다.
- `--timeout <seconds>`: 확인 시간 초과(기본값 3초).

## `update wizard`

업데이트 채널을 선택하고 업데이트 후 Gateway를 재시작할지 확인하는
대화형 흐름입니다(기본값은 재시작). git 체크아웃 없이 `dev`를 선택하면
체크아웃을 생성할지 제안합니다.

옵션:

- `--timeout <seconds>`: 각 업데이트 단계의 시간 초과(기본값 `1200`)

## 수행 작업

채널을 명시적으로 전환할 때(`--channel ...`), OpenClaw는
설치 방식도 함께 맞춥니다:

- `dev` → git 체크아웃을 보장합니다(기본값: `~/openclaw`, `OPENCLAW_GIT_DIR`로 재정의 가능),
  이를 업데이트하고 해당 체크아웃에서 전역 CLI를 설치합니다.
- `stable` → `latest`를 사용해 npm에서 설치합니다.
- `beta` → npm dist-tag `beta`를 우선 사용하지만, beta가 없거나 현재 stable 릴리스보다 오래된 경우 `latest`로 대체합니다.

Gateway 코어 자동 업데이터(config에서 활성화된 경우)는 동일한 업데이트 경로를 재사용합니다.

## Git 체크아웃 흐름

채널:

- `stable`: 최신 비-beta 태그를 체크아웃한 다음 build + doctor를 실행합니다.
- `beta`: 최신 `-beta` 태그를 우선 사용하지만, beta가 없거나 더 오래된 경우 최신 stable 태그로 대체합니다.
- `dev`: `main`을 체크아웃한 다음 fetch + rebase를 수행합니다.

상위 수준 흐름:

1. 깨끗한 worktree가 필요합니다(커밋되지 않은 변경 사항 없음).
2. 선택한 채널(태그 또는 브랜치)로 전환합니다.
3. 업스트림을 fetch합니다(dev 전용).
4. dev 전용: 임시 worktree에서 사전 점검 lint + TypeScript build를 실행합니다. 최신 팁이 실패하면 최대 10개 커밋까지 되돌아가며 가장 최신의 정상 빌드를 찾습니다.
5. 선택한 커밋으로 rebase합니다(dev 전용).
6. 의존성을 설치합니다(pnpm 우선, npm 대체, bun은 보조 호환성 대체 수단으로 유지).
7. build 및 Control UI build를 실행합니다.
8. 최종 “안전 업데이트” 확인으로 `openclaw doctor`를 실행합니다.
9. 활성 채널에 맞게 plugin을 동기화하고(dev는 번들 extension 사용, stable/beta는 npm 사용) npm으로 설치된 plugin을 업데이트합니다.

## `--update` 단축

`openclaw --update`는 `openclaw update`로 다시 작성됩니다(셸 및 런처 스크립트에 유용).

## 함께 보기

- `openclaw doctor` (git 체크아웃에서 먼저 update 실행을 제안함)
- [개발 채널](/install/development-channels)
- [업데이트](/install/updating)
- [CLI 참조](/cli)
