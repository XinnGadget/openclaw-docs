---
read_when:
    - .prose 워크플로를 실행하거나 작성하려고 할 때
    - OpenProse plugin을 활성화하려고 할 때
    - 상태 저장 방식을 이해해야 할 때
summary: 'OpenProse: OpenClaw에서의 .prose 워크플로, 슬래시 명령, 상태'
title: OpenProse
x-i18n:
    generated_at: "2026-04-05T12:50:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 95f86ed3029c5599b6a6bed1f75b2e10c8808cf7ffa5e33dbfb1801a7f65f405
    source_path: prose.md
    workflow: 15
---

# OpenProse

OpenProse는 AI 세션을 오케스트레이션하기 위한 이식 가능한 markdown 우선 워크플로 형식입니다. OpenClaw에서는 OpenProse skill 팩과 `/prose` 슬래시 명령을 설치하는 plugin으로 제공됩니다. 프로그램은 `.prose` 파일에 존재하며, 명시적인 제어 흐름으로 여러 하위 에이전트를 생성할 수 있습니다.

공식 사이트: [https://www.prose.md](https://www.prose.md)

## 할 수 있는 일

- 명시적 병렬성을 가진 멀티 에이전트 조사 + 종합
- 반복 가능한 승인 안전 워크플로(코드 리뷰, 사고 분류, 콘텐츠 파이프라인)
- 지원되는 에이전트 런타임 전반에서 실행할 수 있는 재사용 가능한 `.prose` 프로그램

## 설치 + 활성화

번들 plugin은 기본적으로 비활성화되어 있습니다. OpenProse를 활성화하세요:

```bash
openclaw plugins enable open-prose
```

plugin을 활성화한 후 Gateway를 재시작하세요.

개발/로컬 체크아웃: `openclaw plugins install ./path/to/local/open-prose-plugin`

관련 문서: [Plugins](/tools/plugin), [Plugin manifest](/plugins/manifest), [Skills](/tools/skills).

## 슬래시 명령

OpenProse는 사용자 호출 가능 skill 명령으로 `/prose`를 등록합니다. 이 명령은 OpenProse VM 지침으로 라우팅되며 내부적으로 OpenClaw 도구를 사용합니다.

일반적인 명령:

```
/prose help
/prose run <file.prose>
/prose run <handle/slug>
/prose run <https://example.com/file.prose>
/prose compile <file.prose>
/prose examples
/prose update
```

## 예시: 간단한 `.prose` 파일

```prose
# Research + synthesis with two agents running in parallel.

input topic: "What should we research?"

agent researcher:
  model: sonnet
  prompt: "You research thoroughly and cite sources."

agent writer:
  model: opus
  prompt: "You write a concise summary."

parallel:
  findings = session: researcher
    prompt: "Research {topic}."
  draft = session: writer
    prompt: "Summarize {topic}."

session "Merge the findings + draft into a final answer."
context: { findings, draft }
```

## 파일 위치

OpenProse는 워크스페이스의 `.prose/` 아래에 상태를 유지합니다:

```
.prose/
├── .env
├── runs/
│   └── {YYYYMMDD}-{HHMMSS}-{random}/
│       ├── program.prose
│       ├── state.md
│       ├── bindings/
│       └── agents/
└── agents/
```

사용자 수준의 영구 에이전트는 다음 위치에 있습니다:

```
~/.prose/agents/
```

## 상태 모드

OpenProse는 여러 상태 백엔드를 지원합니다:

- **filesystem** (기본값): `.prose/runs/...`
- **in-context**: 작은 프로그램용 일시적 모드
- **sqlite** (실험적): `sqlite3` 바이너리 필요
- **postgres** (실험적): `psql`과 연결 문자열 필요

참고:

- sqlite/postgres는 opt-in이며 실험적입니다.
- postgres 자격 증명은 하위 에이전트 로그로 흐르므로, 전용 최소 권한 DB를 사용하세요.

## 원격 프로그램

`/prose run <handle/slug>`는 `https://p.prose.md/<handle>/<slug>`로 해석됩니다.
직접 URL은 있는 그대로 가져옵니다. 이는 `web_fetch` 도구(또는 POST의 경우 `exec`)를 사용합니다.

## OpenClaw 런타임 매핑

OpenProse 프로그램은 OpenClaw 기본 요소에 매핑됩니다:

| OpenProse 개념 | OpenClaw 도구 |
| ------------------------- | ---------------- |
| 세션 생성 / 작업 도구 | `sessions_spawn` |
| 파일 읽기/쓰기 | `read` / `write` |
| 웹 가져오기 | `web_fetch` |

도구 allowlist가 이러한 도구를 차단하면 OpenProse 프로그램은 실패합니다. [Skills config](/tools/skills-config)를 참조하세요.

## 보안 + 승인

`.prose` 파일은 코드처럼 취급하세요. 실행 전에 검토하세요. OpenClaw 도구 allowlist와 승인 게이트를 사용해 부작용을 제어하세요.

결정적이고 승인 게이트가 있는 워크플로는 [Lobster](/tools/lobster)와 비교해 보세요.
