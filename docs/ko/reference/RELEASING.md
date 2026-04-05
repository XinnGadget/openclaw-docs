---
read_when:
    - 공개 릴리스 채널 정의를 찾고 있습니다
    - 버전 명명과 배포 주기를 찾고 있습니다
summary: 공개 릴리스 채널, 버전 명명, 배포 주기
title: 릴리스 정책
x-i18n:
    generated_at: "2026-04-05T12:53:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: bb52a13264c802395aa55404c6baeec5c7b2a6820562e7a684057e70cc85668f
    source_path: reference/RELEASING.md
    workflow: 15
---

# 릴리스 정책

OpenClaw에는 세 가지 공개 릴리스 레인이 있습니다:

- stable: 태그된 릴리스로, 기본적으로 npm `beta`에 게시되며 명시적으로 요청된 경우 npm `latest`에 게시됩니다
- beta: npm `beta`에 게시되는 프리릴리스 태그
- dev: `main`의 이동하는 헤드

## 버전 명명

- Stable 릴리스 버전: `YYYY.M.D`
  - Git 태그: `vYYYY.M.D`
- Stable 수정 릴리스 버전: `YYYY.M.D-N`
  - Git 태그: `vYYYY.M.D-N`
- Beta 프리릴리스 버전: `YYYY.M.D-beta.N`
  - Git 태그: `vYYYY.M.D-beta.N`
- 월 또는 일은 앞에 0을 붙이지 마세요
- `latest`는 현재 승격된 stable npm 릴리스를 의미합니다
- `beta`는 현재 beta 설치 대상을 의미합니다
- Stable 및 stable 수정 릴리스는 기본적으로 npm `beta`에 게시됩니다. 릴리스 운영자는 명시적으로 `latest`를 대상으로 지정하거나, 나중에 검증된 beta 빌드를 승격할 수 있습니다
- 모든 OpenClaw 릴리스는 npm 패키지와 macOS 앱을 함께 배포합니다

## 릴리스 주기

- 릴리스는 beta 우선으로 진행됩니다
- Stable은 최신 beta가 검증된 후에만 이어집니다
- 자세한 릴리스 절차, 승인, 자격 증명, 복구 참고 사항은
  maintainer 전용입니다

## 릴리스 사전 점검

- pack 검증 단계에 필요한 `dist/*` 릴리스 아티팩트와 Control UI 번들이
  존재하도록, `pnpm release:check` 전에 `pnpm build && pnpm ui:build`를
  실행하세요
- 태그된 모든 릴리스 전에 `pnpm release:check`를 실행하세요
- `main` 브랜치 npm 사전 점검은 tarball 패키징 전에
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`도
  실행하며, `OPENAI_API_KEY`와 `ANTHROPIC_API_KEY` 워크플로 시크릿을
  모두 사용합니다
- 승인 전에
  `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (또는 해당 beta/수정 태그)를 실행하세요
- npm 게시 후에는 새 임시 prefix에서 게시된 레지스트리 설치 경로를
  검증하기 위해
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (또는 해당 beta/수정 버전)를 실행하세요
- Maintainer 릴리스 자동화는 이제 preflight 후 승격 방식을 사용합니다:
  - 실제 npm 게시에는 성공한 npm `preflight_run_id`가 필요합니다
  - stable npm 릴리스는 기본적으로 `beta`를 대상으로 합니다
  - stable npm 게시에서 워크플로 입력을 통해 명시적으로 `latest`를 지정할 수 있습니다
  - `beta`에서 `latest`로 stable npm 승격하는 기능은 신뢰된 `OpenClaw NPM Release` 워크플로에서 여전히 명시적 수동 모드로 제공됩니다
  - 해당 승격 모드에는 npm `dist-tag` 관리가 trusted publishing과 별개이므로 `npm-release` 환경에 유효한 `NPM_TOKEN`이 여전히 필요합니다
  - 공개 `macOS Release`는 검증 전용입니다
  - 실제 비공개 mac 게시에는 성공한 비공개 mac
    `preflight_run_id`와 `validate_run_id`가 필요합니다
  - 실제 게시 경로는 준비된 아티팩트를 다시 빌드하는 대신 승격합니다
- `YYYY.M.D-N` 같은 stable 수정 릴리스의 경우, 게시 후 검증기는
  `YYYY.M.D`에서 `YYYY.M.D-N`으로의 동일한 임시 prefix 업그레이드 경로도
  검사하므로, 릴리스 수정으로 인해 이전 전역 설치가 기본 stable payload에
  조용히 남는 일이 없게 합니다
- npm 릴리스 사전 점검은 tarball에
  `dist/control-ui/index.html`과 비어 있지 않은
  `dist/control-ui/assets/` payload가 모두 포함되지 않으면
  실패하도록 닫혀 있으므로, 비어 있는 브라우저 대시보드를 다시 배포하지 않게
  합니다
- 릴리스 작업이 CI 계획, extension 타이밍 매니페스트, 또는 빠른 테스트
  매트릭스에 영향을 주었다면, 승인 전에 `.github/workflows/ci.yml`의
  planner 소유 `checks-fast-extensions` 워크플로 매트릭스 출력을 재생성하고
  검토하여 릴리스 노트가 오래된 CI 레이아웃을 설명하지 않도록 하세요
- Stable macOS 릴리스 준비 상태에는 updater 표면도 포함됩니다:
  - GitHub 릴리스에는 패키징된 `.zip`, `.dmg`, `.dSYM.zip`이 포함되어야 합니다
  - `main`의 `appcast.xml`은 게시 후 새 stable zip을 가리켜야 합니다
  - 패키징된 앱은 비디버그 번들 ID, 비어 있지 않은 Sparkle 피드 URL,
    그리고 해당 릴리스 버전에 대한 표준 Sparkle 빌드 하한 이상인
    `CFBundleVersion`을 유지해야 합니다

## NPM 워크플로 입력

`OpenClaw NPM Release`는 운영자가 제어하는 다음 입력을 받습니다:

- `tag`: `v2026.4.2`, `v2026.4.2-1`,
  `v2026.4.2-beta.1` 같은 필수 릴리스 태그
- `preflight_only`: 검증/빌드/패키지 전용이면 `true`, 실제 게시 경로면 `false`
- `preflight_run_id`: 실제 게시 경로에서 필수이며, 워크플로가 성공한 사전 점검 실행에서 준비된 tarball을 재사용할 수 있게 합니다
- `npm_dist_tag`: 게시 경로의 npm 대상 태그이며, 기본값은 `beta`입니다
- `promote_beta_to_latest`: 게시를 건너뛰고 이미 게시된 stable `beta` 빌드를 `latest`로 옮기려면 `true`

규칙:

- Stable 및 수정 태그는 `beta` 또는 `latest` 중 어느 쪽으로도 게시할 수 있습니다
- Beta 프리릴리스 태그는 `beta`에만 게시할 수 있습니다
- 실제 게시 경로는 사전 점검 중 사용한 것과 동일한 `npm_dist_tag`를 사용해야 하며, 워크플로는 게시를 계속하기 전에 해당 메타데이터를 검증합니다
- 승격 모드는 stable 또는 수정 태그, `preflight_only=false`,
  비어 있는 `preflight_run_id`, `npm_dist_tag=beta`를 사용해야 합니다
- 승격 모드에도 `npm dist-tag add`에는 여전히 일반 npm 인증이 필요하므로
  `npm-release` 환경에 유효한 `NPM_TOKEN`이 필요합니다

## Stable npm 릴리스 순서

stable npm 릴리스를 만들 때:

1. `preflight_only=true`로 `OpenClaw NPM Release`를 실행합니다
2. 일반적인 beta 우선 흐름에는 `npm_dist_tag=beta`를 선택하고, 직접 stable 게시를 의도한 경우에만 `latest`를 선택합니다
3. 성공한 `preflight_run_id`를 저장합니다
4. `preflight_only=false`, 동일한 `tag`, 동일한 `npm_dist_tag`, 저장한 `preflight_run_id`로 `OpenClaw NPM Release`를 다시 실행합니다
5. 릴리스가 `beta`에 배포되었다면, 게시된 빌드를 `latest`로 옮기고 싶을 때 나중에 동일한 stable `tag`, `promote_beta_to_latest=true`, `preflight_only=false`, 빈 `preflight_run_id`, `npm_dist_tag=beta`로 `OpenClaw NPM Release`를 실행합니다

승격 모드에도 여전히 `npm-release` 환경 승인과 그 환경 내의
유효한 `NPM_TOKEN`이 필요합니다.

이렇게 하면 직접 게시 경로와 beta 우선 승격 경로가 모두
문서화되고 운영자에게 명확히 보이게 됩니다.

## 공개 참고 자료

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

실제 운영 절차는 maintainer가 비공개 릴리스 문서
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)를
사용합니다.
