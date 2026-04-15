---
read_when:
    - 공개 릴리스 채널 정의를 찾고 있습니다
    - 버전 명명과 출시 주기를 찾고 있습니다
summary: 공개 릴리스 채널, 버전 명명, 및 출시 주기
title: 릴리스 정책
x-i18n:
    generated_at: "2026-04-15T06:00:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 88724307269ab783a9fbf8a0540fea198d8a3add68457f4e64d5707114fa518c
    source_path: reference/RELEASING.md
    workflow: 15
---

# 릴리스 정책

OpenClaw에는 세 가지 공개 릴리스 레인이 있습니다:

- stable: 기본적으로 npm `beta`에 게시되는 태그 릴리스이며, 명시적으로 요청된 경우 npm `latest`에 게시됩니다
- beta: npm `beta`에 게시되는 프리릴리스 태그입니다
- dev: `main`의 이동 중인 최신 헤드입니다

## 버전 명명

- Stable 릴리스 버전: `YYYY.M.D`
  - Git 태그: `vYYYY.M.D`
- Stable 수정 릴리스 버전: `YYYY.M.D-N`
  - Git 태그: `vYYYY.M.D-N`
- Beta 프리릴리스 버전: `YYYY.M.D-beta.N`
  - Git 태그: `vYYYY.M.D-beta.N`
- 월 또는 일에 0을 붙여 자릿수를 맞추지 마세요
- `latest`는 현재 승격된 stable npm 릴리스를 의미합니다
- `beta`는 현재 beta 설치 대상을 의미합니다
- Stable 및 stable 수정 릴리스는 기본적으로 npm `beta`에 게시됩니다. 릴리스 운영자는 명시적으로 `latest`를 대상으로 지정하거나, 검증된 beta 빌드를 나중에 승격할 수 있습니다
- 모든 OpenClaw 릴리스는 npm 패키지와 macOS 앱을 함께 제공합니다

## 릴리스 주기

- 릴리스는 beta 우선으로 진행됩니다
- Stable은 최신 beta가 검증된 후에만 이어집니다
- 자세한 릴리스 절차, 승인, 자격 증명, 복구 참고 사항은
  maintainer 전용입니다

## 릴리스 사전 점검

- pack 검증 단계에 필요한
  `dist/*` 릴리스 아티팩트와 Control UI 번들이 존재하도록,
  `pnpm release:check` 전에 `pnpm build && pnpm ui:build`를 실행하세요
- 모든 태그 릴리스 전에 `pnpm release:check`를 실행하세요
- 릴리스 검사는 이제 별도의 수동 워크플로에서 실행됩니다:
  `OpenClaw Release Checks`
- 교차 OS 설치 및 업그레이드 런타임 검증은
  비공개 호출자 워크플로
  `openclaw/releases-private/.github/workflows/openclaw-cross-os-release-checks.yml`에서
  디스패치되며, 이 워크플로는 재사용 가능한 공개 워크플로
  `.github/workflows/openclaw-cross-os-release-checks-reusable.yml`를 호출합니다
- 이 분리는 의도된 것입니다. 실제 npm 릴리스 경로는 짧고,
  결정론적이며, 아티팩트 중심으로 유지하고, 더 느린 라이브 검사는 별도 레인에 두어
  게시를 지연시키거나 차단하지 않도록 합니다
- 릴리스 검사는 워크플로 로직과 시크릿이 정식 기준으로 유지되도록
  `main` 워크플로 ref에서 디스패치되어야 합니다
- 해당 워크플로는 기존 릴리스 태그 또는 현재 전체
  40자 `main` 커밋 SHA를 받을 수 있습니다
- 커밋 SHA 모드에서는 현재 `origin/main` HEAD만 허용합니다.
  이전 릴리스 커밋에는 릴리스 태그를 사용하세요
- `OpenClaw NPM Release` 검증 전용 사전 점검도
  푸시된 태그 없이 현재 전체 40자 `main` 커밋 SHA를 받을 수 있습니다
- 해당 SHA 경로는 검증 전용이며 실제 게시로 승격할 수 없습니다
- SHA 모드에서 워크플로는 패키지 메타데이터 확인을 위해서만
  `v<package.json version>`을 합성합니다. 실제 게시에는 여전히 실제 릴리스 태그가 필요합니다
- 두 워크플로 모두 실제 게시 및 승격 경로는 GitHub 호스팅
  러너에서 유지하고, 변경 없는 검증 경로는 더 큰
  Blacksmith Linux 러너를 사용할 수 있습니다
- 해당 워크플로는
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  를 `OPENAI_API_KEY` 및 `ANTHROPIC_API_KEY` 워크플로 시크릿 모두를 사용하여 실행합니다
- npm 릴리스 사전 점검은 더 이상 별도의 릴리스 검사 레인을 기다리지 않습니다
- 승인 전에
  `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (또는 해당하는 beta/수정 태그)를 실행하세요
- npm 게시 후에는 게시된 레지스트리
  설치 경로를 새 임시 prefix에서 검증하기 위해
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (또는 해당하는 beta/수정 버전)를 실행하세요
- Maintainer 릴리스 자동화는 이제 사전 점검 후 승격 방식을 사용합니다:
  - 실제 npm 게시에는 성공한 npm `preflight_run_id`가 필요합니다
  - stable npm 릴리스는 기본적으로 `beta`를 대상으로 합니다
  - stable npm 게시는 워크플로 입력을 통해 명시적으로 `latest`를 대상으로 지정할 수 있습니다
  - 토큰 기반 npm dist-tag 변경은 이제 보안을 위해
    `openclaw/releases-private/.github/workflows/openclaw-npm-dist-tags.yml`
    에 있습니다. 이는 `npm dist-tag add`에 여전히 `NPM_TOKEN`이 필요하지만,
    공개 저장소는 OIDC 전용 게시를 유지하기 때문입니다
  - 공개 `macOS Release`는 검증 전용입니다
  - 실제 비공개 mac 게시에는 성공한 비공개 mac
    `preflight_run_id` 및 `validate_run_id`가 필요합니다
  - 실제 게시 경로는 준비된 아티팩트를 다시 빌드하는 대신
    이를 승격합니다
- `YYYY.M.D-N`과 같은 stable 수정 릴리스의 경우, 게시 후 검증기는
  동일한 임시 prefix 업그레이드 경로를 `YYYY.M.D`에서 `YYYY.M.D-N`으로도 확인하므로
  릴리스 수정으로 인해 기존 글로벌 설치가 기본 stable payload에
  조용히 남아 있는 일이 없도록 합니다
- npm 릴리스 사전 점검은 tarball에
  `dist/control-ui/index.html`과 비어 있지 않은 `dist/control-ui/assets/` payload가
  모두 포함되지 않으면 실패 종료되므로, 빈 브라우저 대시보드를 다시
  배포하지 않도록 합니다
- `pnpm test:install:smoke`는 후보 업데이트 tarball의 npm pack `unpackedSize` 예산도 강제하므로,
  설치 프로그램 e2e가 릴리스 게시 경로 이전에 우발적인 pack 크기 증가를 포착합니다
- 릴리스 작업이 CI 계획, 확장 timing manifest,
  또는 확장 테스트 매트릭스에 영향을 주었다면, 승인 전에
  `.github/workflows/ci.yml`의 planner 소유
  `checks-node-extensions` 워크플로 매트릭스 출력을 재생성하고 검토하여
  릴리스 노트가 오래된 CI 레이아웃을 설명하지 않도록 하세요
- Stable macOS 릴리스 준비 상태에는 업데이터 표면도 포함됩니다:
  - GitHub 릴리스에는 패키징된 `.zip`, `.dmg`, `.dSYM.zip`이 포함되어야 합니다
  - `main`의 `appcast.xml`은 게시 후 새 stable zip을 가리켜야 합니다
  - 패키징된 앱은 디버그가 아닌 번들 id, 비어 있지 않은 Sparkle 피드
    URL, 그리고 해당 릴리스 버전에 대한 정식 Sparkle 빌드 하한 이상인
    `CFBundleVersion`을 유지해야 합니다

## NPM 워크플로 입력

`OpenClaw NPM Release`는 다음과 같은 운영자 제어 입력을 받습니다:

- `tag`: 필수 릴리스 태그로, 예를 들어 `v2026.4.2`, `v2026.4.2-1`, 또는
  `v2026.4.2-beta.1`입니다. `preflight_only=true`일 때는 검증 전용
  사전 점검을 위해 현재 전체 40자 `main` 커밋 SHA도 사용할 수 있습니다
- `preflight_only`: 검증/빌드/패키지 전용이면 `true`, 실제 게시 경로이면 `false`
- `preflight_run_id`: 워크플로가 성공한 사전 점검 실행에서 준비된 tarball을
  재사용하도록 실제 게시 경로에서 필수입니다
- `npm_dist_tag`: 게시 경로의 npm 대상 태그이며, 기본값은 `beta`입니다

`OpenClaw Release Checks`는 다음과 같은 운영자 제어 입력을 받습니다:

- `ref`: 검증할 기존 릴리스 태그 또는 현재 전체 40자 `main` 커밋
  SHA입니다

규칙:

- Stable 및 수정 태그는 `beta` 또는 `latest` 중 어느 쪽으로도 게시할 수 있습니다
- Beta 프리릴리스 태그는 `beta`에만 게시할 수 있습니다
- 전체 커밋 SHA 입력은 `preflight_only=true`일 때만 허용됩니다
- 릴리스 검사 커밋 SHA 모드에서도 현재 `origin/main` HEAD가 필요합니다
- 실제 게시 경로는 사전 점검 중 사용한 것과 동일한 `npm_dist_tag`를 사용해야 하며,
  워크플로는 게시를 계속하기 전에 해당 메타데이터를 검증합니다

## Stable npm 릴리스 순서

Stable npm 릴리스를 진행할 때:

1. `preflight_only=true`로 `OpenClaw NPM Release`를 실행합니다
   - 태그가 아직 없으면 사전 점검 워크플로의 검증 전용 드라이 런을 위해
     현재 전체 `main` 커밋 SHA를 사용할 수 있습니다
2. 일반적인 beta 우선 흐름에는 `npm_dist_tag=beta`를 선택하고, 직접 stable 게시를
   의도하는 경우에만 `latest`를 선택합니다
3. 라이브 프롬프트 캐시 적용 범위를 원한다면
   동일한 태그 또는 현재 전체 `main` 커밋 SHA로
   `OpenClaw Release Checks`를 별도로 실행합니다
   - 이는 라이브 적용 범위를 유지하면서도 장시간 실행되거나 불안정할 수 있는 검사를
     게시 워크플로에 다시 결합하지 않기 위한 의도적인 분리입니다
4. 성공한 `preflight_run_id`를 저장합니다
5. `preflight_only=false`, 동일한 `tag`,
   동일한 `npm_dist_tag`, 저장한 `preflight_run_id`로
   `OpenClaw NPM Release`를 다시 실행합니다
6. 릴리스가 `beta`에 게시되었다면, 비공개
   `openclaw/releases-private/.github/workflows/openclaw-npm-dist-tags.yml`
   워크플로를 사용해 해당 stable 버전을 `beta`에서 `latest`로 승격합니다
7. 릴리스가 의도적으로 `latest`에 직접 게시되었고 `beta`도 즉시 같은 stable 빌드를
   따라가야 한다면, 동일한 비공개 워크플로를 사용해 두 dist-tag 모두를
   stable 버전으로 지정하거나, 예약된 self-healing sync가 나중에 `beta`를 이동하도록 둘 수 있습니다

dist-tag 변경은 보안을 위해 비공개 저장소에 있습니다. 이는 여전히
`NPM_TOKEN`이 필요하지만, 공개 저장소는 OIDC 전용 게시를 유지하기 때문입니다.

이렇게 하면 직접 게시 경로와 beta 우선 승격 경로가 모두 문서화되고
운영자에게 가시적으로 유지됩니다.

## 공개 참조

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`.github/workflows/openclaw-cross-os-release-checks-reusable.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-cross-os-release-checks-reusable.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Maintainer는 실제 실행 절차를 위해
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
의 비공개 릴리스 문서를 사용합니다.
