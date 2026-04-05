---
read_when:
    - Skills 구성을 추가하거나 수정하는 경우
    - 번들 allowlist 또는 설치 동작을 조정하는 경우
summary: Skills 구성 스키마 및 예시
title: Skills 구성
x-i18n:
    generated_at: "2026-04-05T12:58:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7839f39f68c1442dcf4740b09886e0ef55762ce0d4b9f7b4f493a8c130c84579
    source_path: tools/skills-config.md
    workflow: 15
---

# Skills 구성

대부분의 skills 로더/설치 구성은
`~/.openclaw/openclaw.json`의 `skills` 아래에 있습니다. 에이전트별 skill 표시 여부는
`agents.defaults.skills` 및 `agents.list[].skills` 아래에 있습니다.

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills", "~/Projects/oss/some-skill-pack/skills"],
      watch: true,
      watchDebounceMs: 250,
    },
    install: {
      preferBrew: true,
      nodeManager: "npm", // npm | pnpm | yarn | bun (Gateway runtime still Node; bun not recommended)
    },
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // or plaintext string
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

내장 이미지 생성/편집에는 `agents.defaults.imageGenerationModel`과
코어 `image_generate` 도구를 우선 사용하세요. `skills.entries.*`는 사용자 지정 또는
서드파티 skill 워크플로에만 해당합니다.

특정 이미지 provider/모델을 선택하는 경우 해당 provider의
인증/API 키도 함께 구성하세요. 일반적인 예: `google/*`용
`GEMINI_API_KEY` 또는 `GOOGLE_API_KEY`, `openai/*`용 `OPENAI_API_KEY`,
`fal/*`용 `FAL_KEY`.

예시:

- 네이티브 Nano Banana 스타일 설정: `agents.defaults.imageGenerationModel.primary: "google/gemini-3.1-flash-image-preview"`
- 네이티브 fal 설정: `agents.defaults.imageGenerationModel.primary: "fal/fal-ai/flux/dev"`

## 에이전트 skill allowlist

같은 머신/워크스페이스 skill 루트를 사용하면서도 에이전트마다
보이는 skill 집합을 다르게 하고 싶다면 에이전트 구성을 사용하세요.

```json5
{
  agents: {
    defaults: {
      skills: ["github", "weather"],
    },
    list: [
      { id: "writer" }, // inherits defaults -> github, weather
      { id: "docs", skills: ["docs-search"] }, // replaces defaults
      { id: "locked-down", skills: [] }, // no skills
    ],
  },
}
```

규칙:

- `agents.defaults.skills`: `agents.list[].skills`를 생략한 에이전트가
  상속받는 공통 기준 allowlist입니다.
- 기본적으로 skills를 제한하지 않으려면 `agents.defaults.skills`를 생략하세요.
- `agents.list[].skills`: 해당 에이전트의 명시적인 최종 skill 집합입니다. 기본값과
  병합되지 않습니다.
- `agents.list[].skills: []`: 해당 에이전트에는 skill을 전혀 노출하지 않습니다.

## 필드

- 내장 skill 루트에는 항상 `~/.openclaw/skills`, `~/.agents/skills`,
  `<workspace>/.agents/skills`, `<workspace>/skills`가 포함됩니다.
- `allowBundled`: **번들된** skills 전용 선택적 allowlist입니다. 설정되면
  목록에 있는 번들 skills만 대상이 됩니다(관리형, agent, workspace skills는 영향 없음).
- `load.extraDirs`: 추가로 스캔할 skill 디렉터리(가장 낮은 우선순위).
- `load.watch`: skill 폴더를 감시하고 skills 스냅샷을 새로 고칩니다(기본값: true).
- `load.watchDebounceMs`: skill watcher 이벤트에 대한 디바운스 시간(밀리초, 기본값: 250).
- `install.preferBrew`: 가능하면 brew 설치를 우선합니다(기본값: true).
- `install.nodeManager`: node 설치 관리자 선호도(`npm` | `pnpm` | `yarn` | `bun`, 기본값: npm).
  이는 **skill 설치**에만 영향을 줍니다. Gateway runtime은 여전히 Node를 사용해야 하며
  (WhatsApp/Telegram에는 Bun 비권장).
  - `openclaw setup --node-manager`는 더 좁은 옵션이며 현재 `npm`,
    `pnpm`, `bun`만 허용합니다. Yarn 기반 skill 설치를 원한다면
    `skills.install.nodeManager: "yarn"`을 수동으로 설정하세요.
- `entries.<skillKey>`: skill별 재정의입니다.
- `agents.defaults.skills`: `agents.list[].skills`를 생략한 에이전트가
  상속받는 선택적 기본 skill allowlist입니다.
- `agents.list[].skills`: 선택적 에이전트별 최종 skill allowlist입니다. 명시적
  목록은 상속된 기본값을 병합하지 않고 대체합니다.

skill별 필드:

- `enabled`: skill이 번들되었거나 설치되어 있어도 `false`로 설정하면 비활성화합니다.
- `env`: 에이전트 실행에 주입되는 환경 변수입니다(이미 설정되어 있지 않은 경우에만).
- `apiKey`: 기본 env var를 선언하는 skills를 위한 선택적 편의 항목입니다.
  평문 문자열 또는 SecretRef 객체(`{ source, provider, id }`)를 지원합니다.

## 참고 사항

- `entries` 아래의 키는 기본적으로 skill 이름에 매핑됩니다. skill이
  `metadata.openclaw.skillKey`를 정의한다면 대신 그 키를 사용하세요.
- 로드 우선순위는 `<workspace>/skills` → `<workspace>/.agents/skills` →
  `~/.agents/skills` → `~/.openclaw/skills` → 번들 skills →
  `skills.load.extraDirs`입니다.
- watcher가 활성화되어 있으면 skill 변경 사항은 다음 에이전트 턴에서 반영됩니다.

### 샌드박스된 skills + env vars

세션이 **샌드박스**되어 있으면 skill 프로세스는 Docker 내부에서 실행됩니다. 샌드박스는
호스트의 `process.env`를 상속하지 않습니다.

다음 중 하나를 사용하세요.

- `agents.defaults.sandbox.docker.env`(또는 에이전트별 `agents.list[].sandbox.docker.env`)
- 사용자 지정 샌드박스 이미지에 env를 포함

전역 `env`와 `skills.entries.<skill>.env/apiKey`는 **호스트** 실행에만 적용됩니다.
