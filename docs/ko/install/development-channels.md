---
read_when:
    - stable/beta/dev 사이를 전환하려는 경우
    - 특정 버전, 태그 또는 SHA를 고정하려는 경우
    - 프리릴리스를 태깅하거나 게시하는 경우
sidebarTitle: Release Channels
summary: 'stable, beta, dev 채널: 의미, 전환, 고정, 태깅'
title: 릴리스 채널
x-i18n:
    generated_at: "2026-04-05T12:45:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3f33a77bf356f989cd4de5f8bb57f330c276e7571b955bea6994a4527e40258d
    source_path: install/development-channels.md
    workflow: 15
---

# 개발 채널

OpenClaw는 세 가지 업데이트 채널을 제공합니다:

- **stable**: npm dist-tag `latest`. 대부분의 사용자에게 권장됩니다.
- **beta**: 현재 유효한 경우 npm dist-tag `beta`; beta가 없거나
  최신 stable 릴리스보다 오래된 경우 업데이트 흐름은 `latest`로 대체됩니다.
- **dev**: `main`의 이동하는 헤드(git). npm dist-tag: `dev`(게시된 경우).
  `main` 브랜치는 실험과 활발한 개발을 위한 곳입니다. 미완성 기능이나
  호환성이 깨지는 변경이 포함될 수 있습니다. 프로덕션 게이트웨이에는 사용하지 마세요.

일반적으로 stable 빌드는 먼저 **beta**에 배포하고, 그곳에서 테스트한 뒤,
버전 번호를 변경하지 않고 검증된 빌드를 `latest`로 이동하는 명시적
승격 단계를 실행합니다. 유지관리자는 필요에 따라 stable 릴리스를
직접 `latest`에 게시할 수도 있습니다. npm 설치에서는 dist-tag가
소스 오브 트루스입니다.

## 채널 전환

```bash
openclaw update --channel stable
openclaw update --channel beta
openclaw update --channel dev
```

`--channel`은 선택을 config(`update.channel`)에 유지하고 설치 방법도
이에 맞게 정렬합니다:

- **`stable`** (패키지 설치): npm dist-tag `latest`를 통해 업데이트합니다.
- **`beta`** (패키지 설치): npm dist-tag `beta`를 우선 사용하지만,
  `beta`가 없거나 현재 stable 태그보다 오래된 경우 `latest`로 대체합니다.
- **`stable`** (git 설치): 최신 stable git 태그를 체크아웃합니다.
- **`beta`** (git 설치): 최신 beta git 태그를 우선 사용하지만, beta가 없거나 더 오래된 경우
  최신 stable git 태그로 대체합니다.
- **`dev`**: git 체크아웃을 보장하고(기본값 `~/openclaw`, `OPENCLAW_GIT_DIR`로 재정의 가능),
  `main`으로 전환한 뒤 upstream에 리베이스하고, 빌드한 다음
  해당 체크아웃에서 전역 CLI를 설치합니다.

팁: stable과 dev를 병렬로 사용하려면 클론을 두 개 유지하고
게이트웨이는 stable 쪽을 가리키게 하세요.

## 일회성 버전 또는 태그 대상 지정

유지된 채널을 변경하지 않고 한 번의
업데이트에 대해 특정 dist-tag, 버전 또는 패키지 spec을 대상으로 하려면 `--tag`를 사용하세요:

```bash
# 특정 버전 설치
openclaw update --tag 2026.4.1-beta.1

# beta dist-tag에서 설치(일회성, 유지되지 않음)
openclaw update --tag beta

# GitHub main 브랜치에서 설치(npm tarball)
openclaw update --tag main

# 특정 npm package spec 설치
openclaw update --tag openclaw@2026.4.1-beta.1
```

참고:

- `--tag`는 **패키지(npm) 설치에만** 적용됩니다. git 설치는 이를 무시합니다.
- 태그는 유지되지 않습니다. 다음 `openclaw update`는 평소처럼
  구성된 채널을 사용합니다.
- 다운그레이드 보호: 대상 버전이 현재 버전보다 오래된 경우,
  OpenClaw는 확인을 요청합니다(`--yes`로 건너뛸 수 있음).
- `--channel beta`는 `--tag beta`와 다릅니다. 채널 흐름은 beta가 없거나 오래된 경우
  stable/latest로 대체될 수 있지만, `--tag beta`는
  그 한 번의 실행에 대해 원시 `beta` dist-tag를 대상으로 합니다.

## 드라이 런

변경 없이 `openclaw update`가 무엇을 할지 미리 봅니다:

```bash
openclaw update --dry-run
openclaw update --channel beta --dry-run
openclaw update --tag 2026.4.1-beta.1 --dry-run
openclaw update --dry-run --json
```

드라이 런은 실제 채널, 대상 버전, 계획된 작업, 그리고
다운그레이드 확인이 필요한지를 보여줍니다.

## Plugins 및 채널

`openclaw update`로 채널을 전환하면 OpenClaw는 plugin
소스도 동기화합니다:

- `dev`는 git 체크아웃의 번들 plugins를 우선 사용합니다.
- `stable`과 `beta`는 npm으로 설치된 plugin 패키지를 복원합니다.
- npm으로 설치된 plugins는 코어 업데이트가 완료된 후 업데이트됩니다.

## 현재 상태 확인

```bash
openclaw update status
```

활성 채널, 설치 종류(git 또는 package), 현재 버전, 그리고
소스(config, git tag, git branch 또는 기본값)를 표시합니다.

## 태깅 모범 사례

- git 체크아웃이 도달해야 하는 릴리스에는 태그를 붙이세요(`vYYYY.M.D`는 stable,
  `vYYYY.M.D-beta.N`은 beta).
- `vYYYY.M.D.beta.N`도 호환성을 위해 인식되지만, `-beta.N`을 권장합니다.
- 레거시 `vYYYY.M.D-<patch>` 태그도 여전히 stable(non-beta)로 인식됩니다.
- 태그는 변경 불가능하게 유지하세요. 태그를 이동하거나 재사용하지 마세요.
- npm 설치에서는 npm dist-tag가 계속 소스 오브 트루스입니다:
  - `latest` -> stable
  - `beta` -> 후보 빌드 또는 beta 우선 stable 빌드
  - `dev` -> main 스냅샷(선택 사항)

## macOS 앱 제공 여부

beta 및 dev 빌드에는 **macOS 앱 릴리스가 포함되지 않을 수 있습니다**. 이는 괜찮습니다:

- git 태그와 npm dist-tag는 여전히 게시될 수 있습니다.
- 릴리스 노트 또는 changelog에 "이 beta에는 macOS 빌드가 없음"을 명시하세요.
