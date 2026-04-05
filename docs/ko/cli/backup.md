---
read_when:
    - 로컬 OpenClaw 상태를 위한 일급 백업 아카이브가 필요할 때
    - 재설정 또는 제거 전에 어떤 경로가 포함될지 미리 보고 싶을 때
summary: '`openclaw backup`용 CLI 참조(로컬 백업 아카이브 생성)'
title: backup
x-i18n:
    generated_at: "2026-04-05T12:37:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 700eda8f9eac1cc93a854fa579f128e5e97d4e6dfc0da75b437c0fb2a898a37d
    source_path: cli/backup.md
    workflow: 15
---

# `openclaw backup`

OpenClaw 상태, config, 인증 프로필, 채널/제공자 자격 증명, 세션, 그리고 선택적으로 워크스페이스에 대한 로컬 백업 아카이브를 생성합니다.

```bash
openclaw backup create
openclaw backup create --output ~/Backups
openclaw backup create --dry-run --json
openclaw backup create --verify
openclaw backup create --no-include-workspace
openclaw backup create --only-config
openclaw backup verify ./2026-03-09T00-00-00.000Z-openclaw-backup.tar.gz
```

## 참고

- 아카이브에는 확인된 소스 경로와 아카이브 레이아웃이 포함된 `manifest.json` 파일이 포함됩니다.
- 기본 출력은 현재 작업 디렉터리에 타임스탬프가 포함된 `.tar.gz` 아카이브입니다.
- 현재 작업 디렉터리가 백업 대상 소스 트리 내부에 있으면, OpenClaw는 기본 아카이브 위치로 홈 디렉터리를 대신 사용합니다.
- 기존 아카이브 파일은 절대 덮어쓰지 않습니다.
- 소스 상태/워크스페이스 트리 내부의 출력 경로는 자체 포함을 방지하기 위해 거부됩니다.
- `openclaw backup verify <archive>`는 아카이브에 루트 manifest가 정확히 하나 포함되어 있는지 검증하고, traversal 스타일 아카이브 경로를 거부하며, manifest에 선언된 모든 페이로드가 tarball에 존재하는지 확인합니다.
- `openclaw backup create --verify`는 아카이브를 쓴 직후 해당 검증을 즉시 실행합니다.
- `openclaw backup create --only-config`는 활성 JSON config 파일만 백업합니다.

## 백업되는 항목

`openclaw backup create`는 로컬 OpenClaw 설치에서 백업 소스를 계획합니다:

- OpenClaw의 로컬 상태 확인자가 반환하는 상태 디렉터리(보통 `~/.openclaw`)
- 활성 config 파일 경로
- 상태 디렉터리 밖에 존재하는 경우 확인된 `credentials/` 디렉터리
- `--no-include-workspace`를 전달하지 않는 한 현재 config에서 발견된 워크스페이스 디렉터리

모델 인증 프로필은 이미 상태 디렉터리 아래
`agents/<agentId>/agent/auth-profiles.json`에 포함되어 있으므로, 일반적으로
상태 백업 항목으로 포함됩니다.

`--only-config`를 사용하면 OpenClaw는 상태, 자격 증명 디렉터리, 워크스페이스 검색을 건너뛰고 활성 config 파일 경로만 아카이브합니다.

OpenClaw는 아카이브를 만들기 전에 경로를 정규화합니다. config, 자격 증명 디렉터리 또는 워크스페이스가 이미 상태 디렉터리 내부에 있으면, 별도의 최상위 백업 소스로 중복되지 않습니다. 누락된 경로는 건너뜁니다.

아카이브 페이로드는 해당 소스 트리의 파일 내용을 저장하며, 포함된 `manifest.json`은 확인된 절대 소스 경로와 각 자산에 사용된 아카이브 레이아웃을 기록합니다.

## 잘못된 config 동작

`openclaw backup`은 복구 중에도 도움을 줄 수 있도록 의도적으로 일반 config 사전 점검을 우회합니다. 하지만 워크스페이스 검색은 유효한 config에 의존하므로, 이제 `openclaw backup create`는 config 파일이 존재하지만 잘못되었고 워크스페이스 백업이 여전히 활성화되어 있으면 즉시 실패합니다.

그런 상황에서도 부분 백업을 원한다면 다음과 같이 다시 실행하세요:

```bash
openclaw backup create --no-include-workspace
```

이렇게 하면 상태, config, 외부 자격 증명 디렉터리는 범위에 유지하면서
워크스페이스 검색은 완전히 건너뜁니다.

config 파일 자체의 복사본만 필요하다면, `--only-config`도 config가 잘못된 경우에 작동합니다. 워크스페이스 검색을 위해 config 파싱에 의존하지 않기 때문입니다.

## 크기 및 성능

OpenClaw는 기본 제공 최대 백업 크기 또는 파일별 크기 제한을 강제하지 않습니다.

실질적인 제한은 로컬 머신과 대상 파일 시스템에서 결정됩니다:

- 임시 아카이브 쓰기와 최종 아카이브를 위한 사용 가능한 공간
- 큰 워크스페이스 트리를 순회하고 `.tar.gz`로 압축하는 데 걸리는 시간
- `openclaw backup create --verify`를 사용하거나 `openclaw backup verify`를 실행할 때 아카이브를 다시 검사하는 시간
- 대상 경로에서의 파일 시스템 동작. OpenClaw는 덮어쓰지 않는 하드 링크 게시 단계를 우선 사용하고, 하드 링크를 지원하지 않으면 배타적 복사로 대체합니다

큰 워크스페이스는 보통 아카이브 크기의 주요 원인입니다. 더 작거나 더 빠른 백업을 원하면 `--no-include-workspace`를 사용하세요.

가장 작은 아카이브가 필요하면 `--only-config`를 사용하세요.
