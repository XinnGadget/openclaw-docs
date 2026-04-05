---
read_when:
    - 새 사용자에게 ClawHub를 소개하는 경우
    - skill 또는 plugin을 설치, 검색, 게시하는 경우
    - ClawHub CLI 플래그와 동기화 동작을 설명하는 경우
summary: 'ClawHub 가이드: 공개 레지스트리, 기본 OpenClaw 설치 흐름, ClawHub CLI 워크플로'
title: ClawHub
x-i18n:
    generated_at: "2026-04-05T12:56:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: e65b3fd770ca96a5dd828dce2dee4ef127268f4884180a912f43d7744bc5706f
    source_path: tools/clawhub.md
    workflow: 15
---

# ClawHub

ClawHub는 **OpenClaw skills 및 plugins**를 위한 공개 레지스트리입니다.

- 기본 `openclaw` 명령을 사용해 skills를 검색/설치/업데이트하고
  ClawHub에서 plugins를 설치하세요.
- 레지스트리 인증, 게시, 삭제,
  삭제 취소 또는 동기화 워크플로가 필요할 때는 별도의 `clawhub` CLI를 사용하세요.

사이트: [clawhub.ai](https://clawhub.ai)

## 기본 OpenClaw 흐름

Skills:

```bash
openclaw skills search "calendar"
openclaw skills install <skill-slug>
openclaw skills update --all
```

Plugins:

```bash
openclaw plugins install clawhub:<package>
openclaw plugins update --all
```

패키지 이름만 있는 npm-safe plugin spec도 npm보다 먼저 ClawHub에서 시도됩니다:

```bash
openclaw plugins install openclaw-codex-app-server
```

기본 `openclaw` 명령은 활성 워크스페이스에 설치하고 소스
메타데이터를 저장하므로 이후 `update` 호출이 ClawHub를 계속 사용할 수 있습니다.

Plugin 설치는 아카이브 설치가 실행되기 전에 광고된 `pluginApi` 및 `minGatewayVersion`
호환성을 검증하므로, 호환되지 않는 호스트는 패키지가 부분 설치되는 대신
초기에 안전하게 실패합니다.

`openclaw plugins install clawhub:...`는 설치 가능한 plugin 계열만 허용합니다.
ClawHub 패키지가 실제로는 skill인 경우 OpenClaw는 중단하고 대신
`openclaw skills install <slug>`를 안내합니다.

## ClawHub란 무엇인가

- OpenClaw skills 및 plugins를 위한 공개 레지스트리입니다.
- skill 번들과 메타데이터를 버전별로 저장하는 저장소입니다.
- 검색, 태그, 사용 신호를 위한 탐색 표면입니다.

## 작동 방식

1. 사용자가 skill 번들(파일 + 메타데이터)을 게시합니다.
2. ClawHub가 번들을 저장하고, 메타데이터를 파싱하고, 버전을 할당합니다.
3. 레지스트리가 검색과 탐색을 위해 skill을 색인화합니다.
4. 사용자가 OpenClaw에서 skills를 탐색, 다운로드, 설치합니다.

## 할 수 있는 일

- 새 skills와 기존 skills의 새 버전을 게시합니다.
- 이름, 태그 또는 검색으로 skills를 찾습니다.
- skill 번들을 다운로드하고 파일을 검사합니다.
- 악성 또는 안전하지 않은 skills를 신고합니다.
- 운영자인 경우 숨기기, 숨김 해제, 삭제 또는 차단할 수 있습니다.

## 대상 사용자(초보자 친화적)

OpenClaw 에이전트에 새 기능을 추가하고 싶다면 ClawHub가 skills를 찾고 설치하는 가장 쉬운 방법입니다. 백엔드가 어떻게 동작하는지 알 필요는 없습니다. 다음을 할 수 있습니다:

- 자연어로 skills를 검색합니다.
- 워크스페이스에 skill을 설치합니다.
- 나중에 한 명령으로 skills를 업데이트합니다.
- 자신이 만든 skills를 게시하여 백업합니다.

## 빠른 시작(비기술적)

1. 필요한 것을 검색합니다:
   - `openclaw skills search "calendar"`
2. skill을 설치합니다:
   - `openclaw skills install <skill-slug>`
3. 새 skill이 반영되도록 새 OpenClaw 세션을 시작합니다.
4. 게시하거나 레지스트리 인증을 관리하려면 별도의
   `clawhub` CLI도 설치하세요.

## ClawHub CLI 설치

게시/동기화 같은 레지스트리 인증 워크플로에만 필요합니다:

```bash
npm i -g clawhub
```

```bash
pnpm add -g clawhub
```

## OpenClaw에 어떻게 맞물리는가

기본 `openclaw skills install`은 활성 워크스페이스의 `skills/`
디렉터리에 설치합니다. `openclaw plugins install clawhub:...`는 일반 관리형
plugin 설치와 업데이트용 ClawHub 소스 메타데이터를 함께 기록합니다.

익명 ClawHub plugin 설치도 비공개 패키지에 대해서는 안전하게 실패합니다.
커뮤니티 또는 기타 비공식 채널은 여전히 설치할 수 있지만, OpenClaw는
활성화 전에 운영자가 소스와 검증을 검토할 수 있도록 경고를 표시합니다.

별도의 `clawhub` CLI도 현재 작업 디렉터리 아래 `./skills`에 skills를 설치합니다.
OpenClaw 워크스페이스가 설정되어 있으면 `clawhub`는
`--workdir`(또는 `CLAWHUB_WORKDIR`)로 재정의하지 않는 한 해당 워크스페이스로 폴백합니다.
OpenClaw는 `<workspace>/skills`에서 워크스페이스 skills를 로드하며
**다음** 세션에서 이를 반영합니다. 이미
`~/.openclaw/skills` 또는 번들 skills를 사용 중이면 워크스페이스 skills가 우선합니다.

skills가 어떻게 로드, 공유, 게이트되는지에 대한 자세한 내용은
[Skills](/tools/skills)를 참고하세요.

## Skill 시스템 개요

skill은 OpenClaw에 특정 작업 수행 방법을 가르치는 버전 관리된 파일 번들입니다.
게시할 때마다 새 버전이 생성되며, 레지스트리는 버전 기록을 유지하므로
사용자가 변경 사항을 감사할 수 있습니다.

일반적인 skill에는 다음이 포함됩니다:

- 기본 설명과 사용법이 담긴 `SKILL.md` 파일.
- skill이 사용하는 선택적 설정, 스크립트 또는 지원 파일.
- 태그, 요약, 설치 요구 사항 같은 메타데이터.

ClawHub는 메타데이터를 사용해 탐색 기능을 제공하고 skill 기능을 안전하게 노출합니다.
또한 레지스트리는 순위와 가시성을 높이기 위해 사용 신호(예: 별점, 다운로드)도 추적합니다.

## 서비스가 제공하는 것(기능)

- skills와 해당 `SKILL.md` 콘텐츠의 **공개 탐색**
- 키워드뿐 아니라 임베딩(벡터 검색) 기반의 **검색**
- semver, changelog, 태그(`latest` 포함)를 사용하는 **버전 관리**
- 버전별 zip 형태의 **다운로드**
- 커뮤니티 피드백을 위한 **별점과 댓글**
- 승인 및 감사를 위한 **운영 훅**
- 자동화와 스크립팅을 위한 **CLI 친화적 API**

## 보안 및 운영

ClawHub는 기본적으로 열려 있습니다. 누구나 skills를 업로드할 수 있지만, 게시하려면
GitHub 계정이 최소 1주일 이상 되어야 합니다. 이는 정당한 기여자를 막지 않으면서
악용을 늦추는 데 도움이 됩니다.

신고 및 운영:

- 로그인한 모든 사용자는 skill을 신고할 수 있습니다.
- 신고 사유는 필수이며 기록됩니다.
- 각 사용자는 동시에 최대 20개의 활성 신고를 가질 수 있습니다.
- 3명 이상의 고유 사용자에게 신고된 skill은 기본적으로 자동 숨김 처리됩니다.
- 운영자는 숨겨진 skills를 보고, 숨김 해제하고, 삭제하거나, 사용자를 차단할 수 있습니다.
- 신고 기능을 남용하면 계정 차단될 수 있습니다.

운영자가 되고 싶으신가요? OpenClaw Discord에서 문의하고 운영자 또는
유지관리자에게 연락하세요.

## CLI 명령과 매개변수

전역 옵션(모든 명령에 적용):

- `--workdir <dir>`: 작업 디렉터리(기본값: 현재 디렉터리, OpenClaw 워크스페이스로 폴백).
- `--dir <dir>`: workdir 기준 skills 디렉터리(기본값: `skills`).
- `--site <url>`: 사이트 기본 URL(브라우저 로그인).
- `--registry <url>`: 레지스트리 API 기본 URL.
- `--no-input`: 프롬프트 비활성화(비대화형).
- `-V, --cli-version`: CLI 버전 출력.

인증:

- `clawhub login`(브라우저 흐름) 또는 `clawhub login --token <token>`
- `clawhub logout`
- `clawhub whoami`

옵션:

- `--token <token>`: API 토큰 붙여넣기.
- `--label <label>`: 브라우저 로그인 토큰에 저장할 레이블(기본값: `CLI token`).
- `--no-browser`: 브라우저를 열지 않음(`--token` 필요).

검색:

- `clawhub search "query"`
- `--limit <n>`: 최대 결과 수.

설치:

- `clawhub install <slug>`
- `--version <version>`: 특정 버전 설치.
- `--force`: 폴더가 이미 존재하면 덮어쓰기.

업데이트:

- `clawhub update <slug>`
- `clawhub update --all`
- `--version <version>`: 특정 버전으로 업데이트(단일 slug에만 적용).
- `--force`: 로컬 파일이 게시된 어떤 버전과도 일치하지 않을 때 덮어쓰기.

목록:

- `clawhub list`(`.clawhub/lock.json` 읽음)

skills 게시:

- `clawhub skill publish <path>`
- `--slug <slug>`: skill slug.
- `--name <name>`: 표시 이름.
- `--version <version>`: semver 버전.
- `--changelog <text>`: changelog 텍스트(비어 있어도 됨).
- `--tags <tags>`: 쉼표로 구분된 태그(기본값: `latest`).

plugins 게시:

- `clawhub package publish <source>`
- `<source>`는 로컬 폴더, `owner/repo`, `owner/repo@ref`, 또는 GitHub URL이 될 수 있습니다.
- `--dry-run`: 아무것도 업로드하지 않고 정확한 게시 계획만 빌드합니다.
- `--json`: CI용 기계 판독 가능 출력 생성.
- `--source-repo`, `--source-commit`, `--source-ref`: 자동 감지가 충분하지 않을 때 사용하는 선택적 재정의.

삭제/삭제 취소(소유자/관리자 전용):

- `clawhub delete <slug> --yes`
- `clawhub undelete <slug> --yes`

동기화(로컬 skills 스캔 + 신규/업데이트 게시):

- `clawhub sync`
- `--root <dir...>`: 추가 스캔 루트.
- `--all`: 프롬프트 없이 모두 업로드.
- `--dry-run`: 업로드될 내용을 표시.
- `--bump <type>`: 업데이트용 `patch|minor|major`(기본값: `patch`).
- `--changelog <text>`: 비대화형 업데이트용 changelog.
- `--tags <tags>`: 쉼표로 구분된 태그(기본값: `latest`).
- `--concurrency <n>`: 레지스트리 검사 수(기본값: 4).

## 에이전트를 위한 일반 워크플로

### skills 검색

```bash
clawhub search "postgres backups"
```

### 새 skills 다운로드

```bash
clawhub install my-skill-pack
```

### 설치된 skills 업데이트

```bash
clawhub update --all
```

### skills 백업(게시 또는 동기화)

단일 skill 폴더의 경우:

```bash
clawhub skill publish ./my-skill --slug my-skill --name "My Skill" --version 1.0.0 --tags latest
```

여러 skills를 한 번에 스캔하고 백업하려면:

```bash
clawhub sync --all
```

### GitHub에서 plugin 게시

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
clawhub package publish your-org/your-plugin@v1.0.0
clawhub package publish https://github.com/your-org/your-plugin
```

코드 plugins에는 `package.json`에 필요한 OpenClaw 메타데이터가 포함되어야 합니다:

```json
{
  "name": "@myorg/openclaw-my-plugin",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
    "compat": {
      "pluginApi": ">=2026.3.24-beta.2",
      "minGatewayVersion": "2026.3.24-beta.2"
    },
    "build": {
      "openclawVersion": "2026.3.24-beta.2",
      "pluginSdkVersion": "2026.3.24-beta.2"
    }
  }
}
```

## 고급 세부 사항(기술)

### 버전 관리와 태그

- 게시할 때마다 새로운 **semver** `SkillVersion`이 생성됩니다.
- `latest` 같은 태그는 특정 버전을 가리키며, 태그를 이동해 롤백할 수 있습니다.
- changelog는 버전별로 연결되며 동기화 또는 업데이트 게시 시 비워둘 수 있습니다.

### 로컬 변경 사항과 레지스트리 버전

업데이트는 콘텐츠 해시를 사용해 로컬 skill 내용과 레지스트리 버전을 비교합니다. 로컬 파일이
게시된 어떤 버전과도 일치하지 않으면 CLI는 덮어쓰기 전에 확인을 요청합니다(또는 비대화형 실행에서는 `--force` 필요).

### 동기화 스캔과 폴백 루트

`clawhub sync`는 먼저 현재 workdir를 스캔합니다. skills를 찾지 못하면
알려진 레거시 위치(예: `~/openclaw/skills`, `~/.openclaw/skills`)로 폴백합니다.
이는 추가 플래그 없이 오래된 skill 설치를 찾기 위한 설계입니다.

### 저장소와 lockfile

- 설치된 skills는 workdir 아래 `.clawhub/lock.json`에 기록됩니다.
- 인증 토큰은 ClawHub CLI 설정 파일에 저장됩니다(`CLAWHUB_CONFIG_PATH`로 재정의 가능).

### 텔레메트리(설치 수)

로그인한 상태에서 `clawhub sync`를 실행하면 CLI는 설치 수 계산을 위해 최소한의 스냅샷을 전송합니다. 이를 완전히 비활성화할 수 있습니다:

```bash
export CLAWHUB_DISABLE_TELEMETRY=1
```

## 환경 변수

- `CLAWHUB_SITE`: 사이트 URL 재정의.
- `CLAWHUB_REGISTRY`: 레지스트리 API URL 재정의.
- `CLAWHUB_CONFIG_PATH`: CLI가 토큰/설정을 저장하는 위치 재정의.
- `CLAWHUB_WORKDIR`: 기본 workdir 재정의.
- `CLAWHUB_DISABLE_TELEMETRY=1`: `sync` 시 텔레메트리 비활성화.
