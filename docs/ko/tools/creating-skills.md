---
read_when:
    - workspace에서 새 사용자 지정 skill을 만드는 경우
    - SKILL.md 기반 Skills를 위한 빠른 시작 워크플로가 필요한 경우
summary: SKILL.md로 사용자 지정 workspace Skills 빌드 및 테스트하기
title: Skills 만들기
x-i18n:
    generated_at: "2026-04-05T12:56:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 747cebc5191b96311d1d6760bede1785a099acd7633a0b88de6b7882b57e1db6
    source_path: tools/creating-skills.md
    workflow: 15
---

# Skills 만들기

Skills는 agent에게 도구를 언제 어떻게 사용할지 가르칩니다. 각 skill은 YAML frontmatter와 마크다운 지침이 포함된 `SKILL.md` 파일을 담고 있는 디렉터리입니다.

Skills가 어떻게 로드되고 우선순위가 정해지는지는 [Skills](/tools/skills)를 참조하세요.

## 첫 번째 skill 만들기

<Steps>
  <Step title="skill 디렉터리 만들기">
    Skills는 workspace에 있습니다. 새 폴더를 만드세요:

    ```bash
    mkdir -p ~/.openclaw/workspace/skills/hello-world
    ```

  </Step>

  <Step title="SKILL.md 작성하기">
    해당 디렉터리 안에 `SKILL.md`를 만드세요. frontmatter는 메타데이터를 정의하고,
    마크다운 본문에는 agent에 대한 지침이 들어갑니다.

    ```markdown
    ---
    name: hello_world
    description: 간단히 인사하는 skill입니다.
    ---

    # Hello World Skill

    사용자가 인사를 요청하면 `echo` 도구를 사용해
    "Hello from your custom skill!"라고 말하세요.
    ```

  </Step>

  <Step title="도구 추가하기(선택 사항)">
    frontmatter에서 사용자 지정 도구 스키마를 정의하거나, agent에게
    기존 system 도구(`exec`나 `browser` 등)를 사용하도록 지시할 수 있습니다. Skills는
    설명하는 도구와 함께 plugin 내부에 포함될 수도 있습니다.

  </Step>

  <Step title="skill 로드하기">
    OpenClaw가 skill을 인식하도록 새 세션을 시작하세요:

    ```bash
    # 채팅에서
    /new

    # 또는 gateway 재시작
    openclaw gateway restart
    ```

    skill이 로드되었는지 확인하세요:

    ```bash
    openclaw skills list
    ```

  </Step>

  <Step title="테스트하기">
    skill이 트리거되어야 하는 메시지를 보내세요:

    ```bash
    openclaw agent --message "인사해 줘"
    ```

    또는 그냥 agent와 대화하면서 인사를 요청해도 됩니다.

  </Step>
</Steps>

## skill 메타데이터 참조

YAML frontmatter는 다음 필드를 지원합니다:

| 필드 | 필수 | 설명 |
| ----------------------------------- | -------- | ------------------------------------------- |
| `name`                              | 예      | 고유 식별자(`snake_case`)              |
| `description`                       | 예      | agent에 표시되는 한 줄 설명     |
| `metadata.openclaw.os`              | 아니요       | OS 필터(`["darwin"]`, `["linux"]` 등) |
| `metadata.openclaw.requires.bins`   | 아니요       | PATH에 필요한 바이너리                   |
| `metadata.openclaw.requires.config` | 아니요       | 필요한 구성 키                        |

## 모범 사례

- **간결하게 작성하세요** — 모델에게 AI처럼 행동하는 법이 아니라 _무엇을_ 해야 하는지 지시하세요
- **안전이 우선입니다** — skill이 `exec`를 사용하는 경우, 신뢰할 수 없는 입력으로부터 임의 명령 주입이 가능하지 않도록 프롬프트를 설계하세요
- **로컬에서 테스트하세요** — 공유하기 전에 `openclaw agent --message "..."`로 테스트하세요
- **ClawHub를 사용하세요** — [ClawHub](https://clawhub.ai)에서 Skills를 탐색하고 기여하세요

## Skills가 위치하는 곳

| 위치 | 우선순위 | 범위 |
| ------------------------------- | ---------- | --------------------- |
| `\<workspace\>/skills/`         | 가장 높음    | agent별             |
| `\<workspace\>/.agents/skills/` | 높음       | workspace별 agent   |
| `~/.agents/skills/`             | 중간     | 공유 agent 프로필  |
| `~/.openclaw/skills/`           | 중간     | 공유(모든 agents)   |
| 번들됨(OpenClaw와 함께 제공) | 낮음        | 전역                |
| `skills.load.extraDirs`         | 가장 낮음     | 사용자 지정 공유 폴더 |

## 관련 문서

- [Skills 참조](/tools/skills) — 로드, 우선순위 및 게이팅 규칙
- [Skills 구성](/tools/skills-config) — `skills.*` 구성 스키마
- [ClawHub](/tools/clawhub) — 공개 skill 레지스트리
- [plugin 빌드하기](/ko/plugins/building-plugins) — plugin은 Skills를 포함할 수 있습니다
