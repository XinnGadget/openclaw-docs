---
read_when:
    - Gateway 플러그인 또는 호환 번들을 설치하거나 관리하려는 경우
    - 플러그인 로드 실패를 디버그하려는 경우
summary: '`openclaw plugins`용 CLI 참조(list, install, marketplace, uninstall, enable/disable, doctor)'
title: plugins
x-i18n:
    generated_at: "2026-04-05T12:39:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8c35ccf68cd7be1af5fee175bd1ce7de88b81c625a05a23887e5780e790df925
    source_path: cli/plugins.md
    workflow: 15
---

# `openclaw plugins`

Gateway 플러그인/확장, hook pack, 호환 번들을 관리합니다.

관련 항목:

- 플러그인 시스템: [Plugins](/tools/plugin)
- 번들 호환성: [Plugin bundles](/plugins/bundles)
- 플러그인 manifest + schema: [Plugin manifest](/plugins/manifest)
- 보안 강화: [Security](/gateway/security)

## 명령

```bash
openclaw plugins list
openclaw plugins list --enabled
openclaw plugins list --verbose
openclaw plugins list --json
openclaw plugins install <path-or-spec>
openclaw plugins inspect <id>
openclaw plugins inspect <id> --json
openclaw plugins inspect --all
openclaw plugins info <id>
openclaw plugins enable <id>
openclaw plugins disable <id>
openclaw plugins uninstall <id>
openclaw plugins doctor
openclaw plugins update <id>
openclaw plugins update --all
openclaw plugins marketplace list <marketplace>
openclaw plugins marketplace list <marketplace> --json
```

번들 플러그인은 OpenClaw와 함께 제공됩니다. 일부는 기본적으로 활성화되어 있으며(예:
번들 모델 provider, 번들 음성 provider, 번들 browser
plugin), 다른 것들은 `plugins enable`이 필요합니다.

네이티브 OpenClaw 플러그인은 인라인 JSON
Schema(`configSchema`, 비어 있어도 포함)와 함께 `openclaw.plugin.json`을 제공해야 합니다. 호환 번들은 대신 자체 번들
manifest를 사용합니다.

`plugins list`는 `Format: openclaw` 또는 `Format: bundle`을 표시합니다. 자세한 list/info
출력에는 번들 하위 유형(`codex`, `claude`, 또는 `cursor`)과 감지된 번들
기능도 표시됩니다.

### 설치

```bash
openclaw plugins install <package>                      # 먼저 ClawHub, 그다음 npm
openclaw plugins install clawhub:<package>              # ClawHub만
openclaw plugins install <package> --force              # 기존 설치 덮어쓰기
openclaw plugins install <package> --pin                # 버전 고정
openclaw plugins install <package> --dangerously-force-unsafe-install
openclaw plugins install <path>                         # 로컬 경로
openclaw plugins install <plugin>@<marketplace>         # marketplace
openclaw plugins install <plugin> --marketplace <name>  # marketplace (명시적)
openclaw plugins install <plugin> --marketplace https://github.com/<owner>/<repo>
```

접두사 없는 패키지 이름은 먼저 ClawHub에서 확인한 다음 npm을 확인합니다. 보안 참고:
플러그인 설치는 코드 실행처럼 취급하세요. 고정된 버전을 권장합니다.

config가 유효하지 않으면 `plugins install`은 일반적으로 실패 시 닫힘 방식으로 동작하며 먼저
`openclaw doctor --fix`를 실행하라고 안내합니다. 문서화된 유일한 예외는
명시적으로
`openclaw.install.allowInvalidConfigRecovery`를 opt-in한 플러그인을 위한 제한적인 번들 플러그인 복구 경로입니다.

`--force`는 기존 설치 대상을 재사용하고 이미 설치된
플러그인 또는 hook pack을 제자리에서 덮어씁니다. 새 로컬 경로, archive, ClawHub 패키지 또는 npm artifact에서
동일한 ID를 의도적으로 다시 설치할 때 사용하세요.

`--pin`은 npm 설치에만 적용됩니다. `--marketplace`와는 함께 사용할 수 없습니다.
marketplace 설치는 npm spec 대신 marketplace 소스 메타데이터를 유지하기 때문입니다.

`--dangerously-force-unsafe-install`은 내장된 dangerous-code scanner의 오탐을 위한 비상용 옵션입니다.
내장 scanner가 `critical` 결과를 보고해도 설치를 계속 진행할 수 있게 하지만,
플러그인 `before_install` hook 정책 차단은 **우회하지 않으며**,
scan 실패도 우회하지 않습니다.

이 CLI 플래그는 플러그인 설치/업데이트 흐름에 적용됩니다. Gateway 기반 Skills
종속성 설치는 대응되는 `dangerouslyForceUnsafeInstall` 요청
재정의를 사용하며, `openclaw skills install`은 별도의 ClawHub Skills
다운로드/설치 흐름으로 유지됩니다.

`plugins install`은 `package.json`에
`openclaw.hooks`를 노출하는 hook pack의 설치 표면이기도 합니다. 필터링된 hook
가시성과 hook별 활성화에는 패키지 설치가 아니라 `openclaw hooks`를 사용하세요.

npm spec은 **registry 전용**입니다(패키지 이름 + 선택적 **정확한 버전** 또는
**dist-tag**). Git/URL/file spec과 semver 범위는 거부됩니다. 종속성 설치는 안전을 위해
`--ignore-scripts`와 함께 실행됩니다.

접두사 없는 spec과 `@latest`는 stable 트랙을 유지합니다. npm이 이 둘 중 하나를 prerelease로 해석하면
OpenClaw는 중단하고
`@beta`/`@rc` 같은 prerelease 태그나 `@1.2.3-beta.4` 같은 정확한 prerelease 버전으로
명시적으로 opt-in하라고 요청합니다.

접두사 없는 설치 spec이 번들 플러그인 ID(예: `diffs`)와 일치하면 OpenClaw는
번들 플러그인을 직접 설치합니다. 같은 이름의 npm 패키지를 설치하려면 명시적인 scoped spec을
사용하세요(예: `@scope/diffs`).

지원되는 archive: `.zip`, `.tgz`, `.tar.gz`, `.tar`.

Claude marketplace 설치도 지원됩니다.

ClawHub 설치는 명시적인 `clawhub:<package>` locator를 사용합니다.

```bash
openclaw plugins install clawhub:openclaw-codex-app-server
openclaw plugins install clawhub:openclaw-codex-app-server@1.2.3
```

이제 OpenClaw는 접두사 없는 npm-safe 플러그인 spec에 대해서도 ClawHub를 우선 사용합니다. 해당 패키지나 버전이
ClawHub에 없을 때만 npm으로 대체합니다.

```bash
openclaw plugins install openclaw-codex-app-server
```

OpenClaw는 ClawHub에서 패키지 archive를 다운로드하고, 광고된
플러그인 API / 최소 gateway 호환성을 확인한 뒤, 일반 archive 경로를 통해 설치합니다. 기록된 설치는 나중 업데이트를 위해
ClawHub 소스 메타데이터를 유지합니다.

marketplace 이름이 Claude의 로컬 레지스트리 캐시 `~/.claude/plugins/known_marketplaces.json`에 있을 때는
`plugin@marketplace` 축약형을 사용하세요.

```bash
openclaw plugins marketplace list <marketplace-name>
openclaw plugins install <plugin-name>@<marketplace-name>
```

marketplace 소스를 명시적으로 전달하려면 `--marketplace`를 사용하세요.

```bash
openclaw plugins install <plugin-name> --marketplace <marketplace-name>
openclaw plugins install <plugin-name> --marketplace <owner/repo>
openclaw plugins install <plugin-name> --marketplace https://github.com/<owner>/<repo>
openclaw plugins install <plugin-name> --marketplace ./my-marketplace
```

Marketplace 소스는 다음 중 하나일 수 있습니다.

- `~/.claude/plugins/known_marketplaces.json`의 Claude known-marketplace 이름
- 로컬 marketplace 루트 또는 `marketplace.json` 경로
- `owner/repo` 같은 GitHub repo 축약형
- `https://github.com/owner/repo` 같은 GitHub repo URL
- git URL

GitHub 또는 git에서 로드한 원격 marketplace의 경우 플러그인 항목은
복제된 marketplace repo 내부에 남아 있어야 합니다. OpenClaw는 해당
repo의 상대 경로 소스를 허용하고, 원격 manifest의 HTTP(S), 절대 경로, git, GitHub 및 기타 비경로
플러그인 소스는 거부합니다.

로컬 경로와 archive의 경우 OpenClaw는 다음을 자동 감지합니다.

- 네이티브 OpenClaw 플러그인 (`openclaw.plugin.json`)
- Codex 호환 번들 (`.codex-plugin/plugin.json`)
- Claude 호환 번들 (`.claude-plugin/plugin.json` 또는 기본 Claude
  component 레이아웃)
- Cursor 호환 번들 (`.cursor-plugin/plugin.json`)

호환 번들은 일반 extensions 루트에 설치되고 동일한 list/info/enable/disable 흐름에 참여합니다. 현재는 번들 Skills, Claude
command-skills, Claude `settings.json` 기본값, Claude `.lsp.json` /
manifest에 선언된 `lspServers` 기본값, Cursor command-skills, 호환
Codex hook 디렉터리가 지원됩니다. 다른 감지된 번들 기능은 diagnostics/info에는 표시되지만 아직 런타임 실행에 연결되지는 않았습니다.

### 목록

```bash
openclaw plugins list
openclaw plugins list --enabled
openclaw plugins list --verbose
openclaw plugins list --json
```

로드된 플러그인만 보려면 `--enabled`를 사용하세요. 테이블 보기에서 플러그인별 세부 줄 보기로 전환하려면
`--verbose`를 사용하세요. 소스/출처/버전/활성화
메타데이터가 표시됩니다. 기계 판독 가능한 인벤토리와 레지스트리
diagnostics에는 `--json`을 사용하세요.

로컬 디렉터리를 복사하지 않으려면 `--link`를 사용하세요(`plugins.load.paths`에 추가됨).

```bash
openclaw plugins install -l ./my-plugin
```

링크 설치는 관리되는 설치 대상을 복사해 덮어쓰는 대신 소스 경로를 재사용하므로,
`--force`는 `--link`와 함께 지원되지 않습니다.

npm 설치에서 확인된 정확한 spec(`name@version`)을
`plugins.installs`에 저장하려면 `--pin`을 사용하세요. 기본 동작은 고정되지 않은 상태로 유지됩니다.

### 제거

```bash
openclaw plugins uninstall <id>
openclaw plugins uninstall <id> --dry-run
openclaw plugins uninstall <id> --keep-files
```

`uninstall`은 `plugins.entries`, `plugins.installs`,
플러그인 허용 목록, 그리고 해당되는 경우 링크된 `plugins.load.paths` 항목에서 플러그인 기록을 제거합니다.
활성 메모리 플러그인의 경우 메모리 슬롯은 `memory-core`로 재설정됩니다.

기본적으로 제거는 활성
state-dir plugin 루트 아래의 플러그인 설치 디렉터리도 삭제합니다. 디스크의 파일을 유지하려면
`--keep-files`를 사용하세요.

`--keep-config`는 `--keep-files`의 deprecated 별칭으로 지원됩니다.

### 업데이트

```bash
openclaw plugins update <id-or-npm-spec>
openclaw plugins update --all
openclaw plugins update <id-or-npm-spec> --dry-run
openclaw plugins update @openclaw/voice-call@beta
openclaw plugins update openclaw-codex-app-server --dangerously-force-unsafe-install
```

업데이트는 `plugins.installs`의 추적된 설치와 `hooks.internal.installs`의 추적된 hook-pack
설치에 적용됩니다.

플러그인 ID를 전달하면 OpenClaw는 해당
플러그인에 대해 기록된 설치 spec을 재사용합니다. 즉, 이전에 저장된 `@beta` 같은 dist-tag와 정확히 고정된 버전이 이후 `update <id>` 실행에서도 계속 사용됩니다.

npm 설치의 경우 dist-tag
또는 정확한 버전이 포함된 명시적 npm 패키지 spec도 전달할 수 있습니다. OpenClaw는 해당 패키지 이름을 추적된 플러그인
기록에 다시 매핑하고, 설치된 플러그인을 업데이트한 뒤, 이후
ID 기반 업데이트를 위해 새 npm spec을 기록합니다.

저장된 integrity hash가 존재하고 가져온 artifact hash가 변경되면,
OpenClaw는 경고를 출력하고 진행 전에 확인을 요청합니다. CI/비대화형 실행에서 프롬프트를 우회하려면
전역 `--yes`를 사용하세요.

`--dangerously-force-unsafe-install`은 `plugins update`에서도
플러그인 업데이트 중 내장 dangerous-code scan 오탐을 위한 비상 재정의로 사용할 수 있습니다.
여전히 플러그인 `before_install` 정책 차단이나
scan-failure 차단은 우회하지 않으며, hook-pack 업데이트가 아니라 플러그인 업데이트에만 적용됩니다.

### 검사

```bash
openclaw plugins inspect <id>
openclaw plugins inspect <id> --json
```

단일 플러그인에 대한 심층 검사입니다. 식별, 로드 상태, 소스,
등록된 기능, hook, 도구, 명령, 서비스, gateway 메서드,
HTTP 경로, 정책 플래그, diagnostics, 설치 메타데이터, 번들 기능,
그리고 감지된 MCP 또는 LSP 서버 지원을 표시합니다.

각 플러그인은 런타임에 실제로 등록한 항목에 따라 분류됩니다.

- **plain-capability** — 하나의 기능 유형(예: provider 전용 플러그인)
- **hybrid-capability** — 여러 기능 유형(예: 텍스트 + 음성 + 이미지)
- **hook-only** — 기능이나 표면 없이 hook만 존재
- **non-capability** — 기능은 없지만 도구/명령/서비스가 있음

기능 모델에 대한 자세한 내용은 [Plugin shapes](/plugins/architecture#plugin-shapes)를 참조하세요.

`--json` 플래그는 스크립팅과
감사에 적합한 기계 판독 가능한 보고서를 출력합니다.

`inspect --all`은 shape, capability 종류,
호환성 공지, 번들 기능, hook 요약 열이 포함된 전체 플릿 테이블을 렌더링합니다.

`info`는 `inspect`의 별칭입니다.

### Doctor

```bash
openclaw plugins doctor
```

`doctor`는 플러그인 로드 오류, manifest/discovery diagnostics, 그리고
호환성 공지를 보고합니다. 모든 것이 정상이면 `No plugin issues
detected.`를 출력합니다.

### Marketplace

```bash
openclaw plugins marketplace list <source>
openclaw plugins marketplace list <source> --json
```

Marketplace 목록은 로컬 marketplace 경로, `marketplace.json` 경로,
`owner/repo` 같은 GitHub 축약형, GitHub repo URL, 또는 git URL을 받을 수 있습니다. `--json`은
확인된 소스 레이블과 파싱된 marketplace manifest 및
플러그인 항목을 출력합니다.
