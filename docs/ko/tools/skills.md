---
read_when:
    - Skills를 추가하거나 수정하고 있습니다
    - Skill 게이팅 또는 로드 규칙을 변경하고 있습니다
summary: 'Skills: 관리형 vs 워크스페이스, 게이팅 규칙, config/env 연결'
title: Skills
x-i18n:
    generated_at: "2026-04-05T12:58:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6bb0e2e7c2ff50cf19c759ea1da1fd1886dc11f94adc77cbfd816009f75d93ee
    source_path: tools/skills.md
    workflow: 15
---

# Skills (OpenClaw)

OpenClaw는 에이전트에게 도구 사용법을 가르치기 위해 **[AgentSkills](https://agentskills.io) 호환** skill 폴더를 사용합니다. 각 skill은 YAML frontmatter와 지침이 들어 있는 `SKILL.md`를 포함한 디렉터리입니다. OpenClaw는 **번들 skills**와 선택적인 로컬 재정의를 함께 로드하고, 환경, config, 바이너리 존재 여부를 기준으로 로드 시점에 이를 필터링합니다.

## 위치와 우선순위

OpenClaw는 다음 소스에서 skills를 로드합니다:

1. **추가 skill 폴더**: `skills.load.extraDirs`로 구성
2. **번들 skills**: 설치물(npm 패키지 또는 OpenClaw.app)에 포함
3. **관리형/로컬 skills**: `~/.openclaw/skills`
4. **개인 에이전트 skills**: `~/.agents/skills`
5. **프로젝트 에이전트 skills**: `<workspace>/.agents/skills`
6. **워크스페이스 skills**: `<workspace>/skills`

skill 이름이 충돌하면 우선순위는 다음과 같습니다:

`<workspace>/skills`(가장 높음) → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → 번들 skills → `skills.load.extraDirs`(가장 낮음)

## 에이전트별 skills vs 공유 skills

**멀티 에이전트** 설정에서는 각 에이전트가 자체 워크스페이스를 가집니다. 이는 다음을 의미합니다:

- **에이전트별 skills**는 해당 에이전트 전용 `<workspace>/skills`에 있습니다.
- **프로젝트 에이전트 skills**는 `<workspace>/.agents/skills`에 있으며,
  일반 워크스페이스 `skills/` 폴더보다 먼저 해당 워크스페이스에 적용됩니다.
- **개인 에이전트 skills**는 `~/.agents/skills`에 있으며, 해당 머신의
  여러 워크스페이스에 걸쳐 적용됩니다.
- **공유 skills**는 `~/.openclaw/skills`(관리형/로컬)에 있으며, 동일한
  머신의 **모든 에이전트**에서 볼 수 있습니다.
- **공유 폴더**는 여러 에이전트가 사용하는 공통 skills 팩이 필요할 경우
  `skills.load.extraDirs`를 통해 추가할 수도 있습니다(가장 낮은 우선순위).

같은 skill 이름이 여러 위치에 존재하면 일반적인 우선순위가 적용됩니다:
workspace가 우선하고, 그다음 프로젝트 에이전트 skills, 개인 에이전트 skills,
관리형/로컬, 번들, extra dirs 순입니다.

## 에이전트 skill 허용 목록

skill **위치**와 skill **가시성**은 서로 다른 제어입니다.

- 위치/우선순위는 같은 이름의 skill 중 어떤 복사본이 우선하는지 결정합니다.
- 에이전트 허용 목록은 보이는 skill 중 에이전트가 실제로 사용할 수 있는 것을 결정합니다.

공유 기본값에는 `agents.defaults.skills`를 사용하고, 에이전트별 재정의에는
`agents.list[].skills`를 사용하세요:

```json5
{
  agents: {
    defaults: {
      skills: ["github", "weather"],
    },
    list: [
      { id: "writer" }, // github, weather 상속
      { id: "docs", skills: ["docs-search"] }, // 기본값 대체
      { id: "locked-down", skills: [] }, // skill 없음
    ],
  },
}
```

규칙:

- 기본적으로 제한 없는 skills를 원하면 `agents.defaults.skills`를 생략하세요.
- `agents.defaults.skills`를 상속하려면 `agents.list[].skills`를 생략하세요.
- skill이 전혀 없게 하려면 `agents.list[].skills: []`로 설정하세요.
- 비어 있지 않은 `agents.list[].skills` 목록은 해당 에이전트의 최종 집합이며,
  기본값과 병합되지 않습니다.

OpenClaw는 프롬프트 구성, skill 슬래시 명령 검색, 샌드박스 동기화, skill 스냅샷 전반에 걸쳐 유효한 에이전트 skill 집합을 적용합니다.

## 플러그인 + skills

플러그인은 `openclaw.plugin.json`에 `skills` 디렉터리(플러그인 루트 기준 상대 경로)를 나열하여 자체 skills를 포함할 수 있습니다. 플러그인 skills는 플러그인이 활성화되면 로드됩니다. 현재 이 디렉터리들은 `skills.load.extraDirs`와 같은 저우선순위 경로에 병합되므로, 같은 이름의 번들, 관리형, 에이전트, 워크스페이스 skill이 이를 재정의합니다.
플러그인의 config 항목에서 `metadata.openclaw.requires.config`로 이를 게이트할 수
있습니다. 검색/config는 [플러그인](/tools/plugin), 해당 skills가 가르치는 도구 표면은 [도구](/tools)를 참고하세요.

## ClawHub(설치 + 동기화)

ClawHub는 OpenClaw용 공개 skills 레지스트리입니다.
[https://clawhub.ai](https://clawhub.ai)에서 둘러볼 수 있습니다. 검색/설치/업데이트에는 네이티브 `openclaw skills`
명령을 사용하고, 게시/동기화 워크플로가 필요하면 별도의 `clawhub` CLI를 사용하세요.
전체 가이드는 [ClawHub](/tools/clawhub)를 참고하세요.

일반적인 흐름:

- 워크스페이스에 skill 설치:
  - `openclaw skills install <skill-slug>`
- 설치된 모든 skills 업데이트:
  - `openclaw skills update --all`
- 동기화(스캔 + 업데이트 게시):
  - `clawhub sync --all`

네이티브 `openclaw skills install`은 활성 워크스페이스의 `skills/`
디렉터리에 설치합니다. 별도의 `clawhub` CLI 역시 현재 작업 디렉터리 아래의 `./skills`에 설치하며
(또는 구성된 OpenClaw 워크스페이스로 폴백), OpenClaw는 다음 세션에서 이를 `<workspace>/skills`로 인식합니다.

## 보안 참고

- 서드파티 skills는 **신뢰할 수 없는 코드**로 취급하세요. 활성화 전에 읽어보세요.
- 신뢰할 수 없는 입력과 위험한 도구에는 샌드박스 실행을 우선하세요. [샌드박싱](/ko/gateway/sandboxing)을 참고하세요.
- 워크스페이스 및 extra-dir skill 검색은 해석된 realpath가 구성된 루트 안에 머무는 skill 루트와 `SKILL.md` 파일만 허용합니다.
- Gateway 기반 skill 의존성 설치(`skills.install`, 온보딩, Skills 설정 UI)는 설치자 메타데이터를 실행하기 전에 내장 위험 코드 스캐너를 실행합니다. `critical` 결과는 호출자가 명시적으로 위험 재정의를 설정하지 않는 한 기본적으로 차단되며, 의심스러운 결과는 여전히 경고만 합니다.
- `openclaw skills install <slug>`는 다릅니다. 이것은 ClawHub skill 폴더를 워크스페이스로 다운로드하며 위의 설치자 메타데이터 경로를 사용하지 않습니다.
- `skills.entries.*.env`와 `skills.entries.*.apiKey`는 해당 에이전트 턴 동안 **호스트** 프로세스에 시크릿을 주입합니다
  (샌드박스가 아님). 프롬프트와 로그에는 시크릿을 남기지 마세요.
- 더 넓은 위협 모델과 체크리스트는 [보안](/ko/gateway/security)을 참고하세요.

## 형식(AgentSkills + Pi 호환)

`SKILL.md`에는 최소한 다음이 포함되어야 합니다:

```markdown
---
name: image-lab
description: Generate or edit images via a provider-backed image workflow
---
```

참고:

- 레이아웃/의도는 AgentSkills 사양을 따릅니다.
- 임베디드 에이전트가 사용하는 파서는 **단일 줄** frontmatter 키만 지원합니다.
- `metadata`는 **단일 줄 JSON 객체**여야 합니다.
- skill 폴더 경로를 참조하려면 지침에서 `{baseDir}`를 사용하세요.
- 선택적 frontmatter 키:
  - `homepage` — macOS Skills UI에서 “Website”로 표시되는 URL(`metadata.openclaw.homepage`로도 지원).
  - `user-invocable` — `true|false`(기본값: `true`). `true`이면 skill이 사용자 슬래시 명령으로 노출됩니다.
  - `disable-model-invocation` — `true|false`(기본값: `false`). `true`이면 skill은 모델 프롬프트에서 제외되지만 사용자 호출은 가능합니다.
  - `command-dispatch` — `tool`(선택 사항). `tool`로 설정하면 슬래시 명령이 모델을 우회하고 직접 tool로 디스패치됩니다.
  - `command-tool` — `command-dispatch: tool`이 설정되었을 때 호출할 tool 이름.
  - `command-arg-mode` — `raw`(기본값). tool 디스패치의 경우 원시 args 문자열을 tool에 전달합니다(코어 파싱 없음).

    tool은 다음 params로 호출됩니다:
    `{ command: "<raw args>", commandName: "<slash command>", skillName: "<skill name>" }`.

## 게이팅(로드 시 필터)

OpenClaw는 `metadata`(단일 줄 JSON)를 사용해 **로드 시점에 skills를 필터링**합니다:

```markdown
---
name: image-lab
description: Generate or edit images via a provider-backed image workflow
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"], "config": ["browser.enabled"] },
        "primaryEnv": "GEMINI_API_KEY",
      },
  }
---
```

`metadata.openclaw` 아래 필드:

- `always: true` — 항상 skill을 포함합니다(다른 게이트 건너뜀).
- `emoji` — macOS Skills UI에서 사용하는 선택적 이모지.
- `homepage` — macOS Skills UI에 “Website”로 표시되는 선택적 URL.
- `os` — 선택적 플랫폼 목록(`darwin`, `linux`, `win32`). 설정된 경우 해당 OS에서만 skill이 유효합니다.
- `requires.bins` — 목록; 각각 `PATH`에 존재해야 합니다.
- `requires.anyBins` — 목록; 최소 하나는 `PATH`에 존재해야 합니다.
- `requires.env` — 목록; env var가 존재해야 하거나 config에서 제공되어야 합니다.
- `requires.config` — 참값이어야 하는 `openclaw.json` 경로 목록.
- `primaryEnv` — `skills.entries.<name>.apiKey`와 연결된 env var 이름.
- `install` — macOS Skills UI에서 사용하는 선택적 설치자 명세 배열(brew/node/go/uv/download).

샌드박싱 관련 참고:

- `requires.bins`는 skill 로드 시점에 **호스트**에서 검사됩니다.
- 에이전트가 샌드박스된 경우, 바이너리는 **컨테이너 내부에도**
  존재해야 합니다.
  `agents.defaults.sandbox.docker.setupCommand`(또는 커스텀 이미지)로 이를 설치하세요.
  `setupCommand`는 컨테이너 생성 후 한 번 실행됩니다.
  패키지 설치에는 네트워크 egress, 쓰기 가능한 루트 FS, 샌드박스 내 루트 사용자도 필요합니다.
  예: `summarize` skill(`skills/summarize/SKILL.md`)은
  այնտեղ서 실행되려면 샌드박스 컨테이너 안에 `summarize` CLI가 있어야 합니다.

설치자 예시:

```markdown
---
name: gemini
description: Use Gemini CLI for coding assistance and Google search lookups.
metadata:
  {
    "openclaw":
      {
        "emoji": "♊️",
        "requires": { "bins": ["gemini"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "gemini-cli",
              "bins": ["gemini"],
              "label": "Install Gemini CLI (brew)",
            },
          ],
      },
  }
---
```

참고:

- 여러 설치자가 나열되면 gateway는 **하나의** 선호 옵션을 선택합니다(brew를 사용할 수 있으면 brew, 그렇지 않으면 node).
- 모든 설치자가 `download`이면 OpenClaw는 사용 가능한 아티팩트를 볼 수 있도록 각 항목을 나열합니다.
- 설치자 명세에는 플랫폼별 옵션 필터링을 위한 `os: ["darwin"|"linux"|"win32"]`를 포함할 수 있습니다.
- Node 설치는 `openclaw.json`의 `skills.install.nodeManager`를 따릅니다(기본값: npm, 옵션: npm/pnpm/yarn/bun).
  이것은 **skill 설치**에만 영향을 줍니다. Gateway 런타임은 여전히 Node를 사용해야 하며
  (WhatsApp/Telegram에는 Bun을 권장하지 않음).
- Gateway 기반 설치자 선택은 node 전용이 아니라 선호도 기반입니다.
  설치 명세에 여러 종류가 섞여 있을 때 OpenClaw는
  `skills.install.preferBrew`가 활성화되어 있고 `brew`가 존재하면 Homebrew를 우선하고,
  그다음 `uv`, 구성된 node manager, 이후 `go`나 `download` 같은 다른 폴백을 선택합니다.
- 모든 설치 명세가 `download`이면 OpenClaw는 하나의 선호 설치자로 축소하지 않고
  모든 다운로드 옵션을 노출합니다.
- Go 설치: `go`가 없고 `brew`를 사용할 수 있으면 gateway는 먼저 Homebrew로 Go를 설치하고, 가능하면 `GOBIN`을 Homebrew의 `bin`으로 설정합니다.
- 다운로드 설치: `url`(필수), `archive` (`tar.gz` | `tar.bz2` | `zip`), `extract` (기본값: 아카이브 감지 시 자동), `stripComponents`, `targetDir` (기본값: `~/.openclaw/tools/<skillKey>`).

`metadata.openclaw`가 없으면 skill은 항상 유효합니다(config에서 비활성화되었거나 번들 skill에 대해 `skills.allowBundled`에 막힌 경우 제외).

## config 재정의(`~/.openclaw/openclaw.json`)

번들/관리형 skills는 토글하고 env 값을 제공할 수 있습니다:

```json5
{
  skills: {
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // 또는 일반 문자열
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
        config: {
          endpoint: "https://example.invalid",
          model: "nano-pro",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

참고: skill 이름에 하이픈이 있으면 키를 따옴표로 감싸세요(JSON5는 따옴표가 있는 키를 허용함).

OpenClaw 자체 안에서 기본 이미지 생성/편집을 원한다면, 번들 skill 대신 코어
`image_generate` tool과 `agents.defaults.imageGenerationModel`을 사용하세요. 여기의 skill 예시는 커스텀 또는 서드파티 워크플로용입니다.

네이티브 이미지 분석에는 `agents.defaults.imageModel`과 함께 `image` tool을 사용하세요.
네이티브 이미지 생성/편집에는
`agents.defaults.imageGenerationModel`과 함께 `image_generate`를 사용하세요. `openai/*`, `google/*`,
`fal/*` 또는 다른 제공자별 이미지 모델을 선택한다면, 해당 제공자의 인증/API
키도 추가하세요.

config 키는 기본적으로 **skill 이름**과 일치합니다. skill이
`metadata.openclaw.skillKey`를 정의하면 `skills.entries` 아래에서 해당 키를 사용하세요.

규칙:

- `enabled: false`는 번들/설치되어 있더라도 skill을 비활성화합니다.
- `env`: 프로세스에 해당 변수가 아직 설정되지 않은 경우에만 주입됩니다.
- `apiKey`: `metadata.openclaw.primaryEnv`를 선언한 skills를 위한 편의 기능입니다.
  일반 문자열 또는 SecretRef 객체(`{ source, provider, id }`)를 지원합니다.
- `config`: 커스텀 skill별 필드를 위한 선택적 bag이며, 커스텀 키는 여기에 있어야 합니다.
- `allowBundled`: **번들** skills 전용 선택적 허용 목록입니다. 설정하면
  목록에 있는 번들 skills만 유효합니다(관리형/워크스페이스 skills는 영향 없음).

## 환경 주입(에이전트 실행별)

에이전트 실행이 시작되면 OpenClaw는 다음을 수행합니다:

1. skill 메타데이터를 읽습니다.
2. `skills.entries.<key>.env` 또는 `skills.entries.<key>.apiKey`를
   `process.env`에 적용합니다.
3. **유효한** skills로 시스템 프롬프트를 구성합니다.
4. 실행이 끝나면 원래 환경을 복원합니다.

이것은 전역 셸 환경이 아니라 **에이전트 실행 범위로 제한**됩니다.

## 세션 스냅샷(성능)

OpenClaw는 **세션 시작 시점에** 유효한 skills를 스냅샷으로 저장하고 같은 세션의 이후 턴에서 그 목록을 재사용합니다. skills나 config 변경은 다음 새 세션부터 적용됩니다.

skills watcher가 활성화되어 있거나 중간에 새로 유효한 원격 노드가 나타나는 경우, 세션 중간에도 skills를 새로고칠 수 있습니다(아래 참고). 이를 **핫 리로드**로 생각하면 됩니다. 새로고침된 목록은 다음 에이전트 턴에서 반영됩니다.

해당 세션의 유효한 에이전트 skill 허용 목록이 바뀌면 OpenClaw는
스냅샷을 새로고쳐 보이는 skills가 현재 에이전트와 계속 일치하도록 합니다.

## 원격 macOS 노드(Linux gateway)

Gateway가 Linux에서 실행 중이지만 **`system.run`이 허용된** **macOS 노드**가 연결되어 있으면(Exec approvals 보안이 `deny`가 아님), OpenClaw는 필요한 바이너리가 해당 노드에 있을 때 macOS 전용 skills를 유효한 것으로 취급할 수 있습니다. 에이전트는 `host=node`와 함께 `exec` tool을 사용해 تلك skills를 실행해야 합니다.

이것은 노드가 보고하는 명령 지원과 `system.run`을 통한 바이너리 프로브에 의존합니다. 나중에 macOS 노드가 오프라인이 되더라도 skills는 계속 표시되며, 노드가 다시 연결될 때까지 호출이 실패할 수 있습니다.

## Skills watcher(자동 새로고침)

기본적으로 OpenClaw는 skill 폴더를 감시하고 `SKILL.md` 파일이 바뀌면 skills 스냅샷을 갱신합니다. 이는 `skills.load` 아래에서 구성합니다:

```json5
{
  skills: {
    load: {
      watch: true,
      watchDebounceMs: 250,
    },
  },
}
```

## 토큰 영향(skills 목록)

skills가 유효하면 OpenClaw는 사용 가능한 skills의 압축된 XML 목록을 시스템 프롬프트에 주입합니다(`pi-coding-agent`의 `formatSkillsForPrompt` 사용). 비용은 결정론적입니다:

- **기본 오버헤드(1개 이상의 skill이 있을 때만):** 195자
- **skill당:** 97자 + XML 이스케이프된 `<name>`, `<description>`, `<location>` 값의 길이

공식(문자 수):

```
total = 195 + Σ (97 + len(name_escaped) + len(description_escaped) + len(location_escaped))
```

참고:

- XML 이스케이프는 `& < > " '`를 엔터티(`&amp;`, `&lt;` 등)로 확장하므로 길이가 늘어납니다.
- 토큰 수는 모델 토크나이저에 따라 달라집니다. 대략적인 OpenAI 스타일 추정으로는 ~4자/토큰이므로 **97자 ≈ 24토큰**에 실제 필드 길이가 더해집니다.

## 관리형 skills 수명주기

OpenClaw는 설치물의 일부로 **번들 skills**의 기준 세트를 제공합니다(npm 패키지 또는 OpenClaw.app). `~/.openclaw/skills`는 로컬 재정의용으로 존재합니다(예: 번들 복사본을 바꾸지 않고 skill을 고정/패치). 워크스페이스 skills는 사용자 소유이며, 이름이 충돌하면 둘 다 재정의합니다.

## config 참고

전체 구성 스키마는 [Skills config](/tools/skills-config)를 참고하세요.

## 더 많은 skills를 찾고 있나요?

[https://clawhub.ai](https://clawhub.ai)에서 찾아보세요.

---

## 관련 문서

- [Skills 만들기](/tools/creating-skills) — 커스텀 skills 빌드하기
- [Skills Config](/tools/skills-config) — skill 구성 참고
- [슬래시 명령](/tools/slash-commands) — 사용 가능한 모든 슬래시 명령
- [플러그인](/tools/plugin) — 플러그인 시스템 개요
