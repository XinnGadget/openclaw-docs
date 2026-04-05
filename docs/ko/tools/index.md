---
read_when:
    - OpenClaw가 어떤 도구를 제공하는지 이해하려는 경우
    - 도구를 구성, 허용 또는 거부해야 하는 경우
    - 내장 도구, Skills, plugin 중 무엇을 사용할지 결정하는 경우
summary: 'OpenClaw 도구 및 plugin 개요: 에이전트가 할 수 있는 일과 이를 확장하는 방법'
title: 도구 및 plugin
x-i18n:
    generated_at: "2026-04-05T12:57:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 17768048b23f980de5e502cc30fbddbadc2e26ae62f0f03c5ab5bbcdeea67e50
    source_path: tools/index.md
    workflow: 15
---

# 도구 및 plugin

에이전트가 텍스트 생성 외에 수행하는 모든 작업은 **도구**를 통해 이루어집니다.
도구는 에이전트가 파일을 읽고, 명령을 실행하고, 웹을 탐색하고, 메시지를 보내고, 디바이스와 상호작용하는 방식입니다.

## 도구, Skills, plugin

OpenClaw에는 함께 작동하는 세 개의 계층이 있습니다:

<Steps>
  <Step title="도구는 에이전트가 호출하는 것입니다">
    도구는 에이전트가 호출할 수 있는 타입이 지정된 함수입니다(예: `exec`, `browser`,
    `web_search`, `message`). OpenClaw는 **내장 도구** 집합을 제공하며,
    plugin은 추가 도구를 등록할 수 있습니다.

    에이전트는 도구를 모델 API로 전송되는 구조화된 함수 정의로 인식합니다.

  </Step>

  <Step title="Skills는 언제, 어떻게 사용할지 에이전트에게 가르칩니다">
    Skill은 system 프롬프트에 주입되는 마크다운 파일(`SKILL.md`)입니다.
    Skills는 에이전트가 도구를 효과적으로 사용할 수 있도록 컨텍스트, 제약 조건,
    단계별 안내를 제공합니다. Skills는 워크스페이스, 공유 폴더에 있거나,
    plugin 내부에 포함되어 제공될 수 있습니다.

    [Skills 참조](/tools/skills) | [Skills 만들기](/tools/creating-skills)

  </Step>

  <Step title="plugin은 모든 것을 함께 패키징합니다">
    plugin은 다음 기능 조합 중 무엇이든 등록할 수 있는 패키지입니다:
    채널, 모델 공급자, 도구, Skills, 음성, 실시간 전사,
    실시간 음성, 미디어 이해, 이미지 생성, 비디오 생성,
    web fetch, web search 등. 일부 plugin은 **코어**(OpenClaw와 함께
    제공됨)이고, 다른 plugin은 **외부**(커뮤니티가 npm에 게시)입니다.

    [plugin 설치 및 구성](/tools/plugin) | [직접 만들기](/ko/plugins/building-plugins)

  </Step>
</Steps>

## 내장 도구

이 도구들은 OpenClaw와 함께 제공되며 plugin을 설치하지 않아도 사용할 수 있습니다:

| 도구 | 기능 | 페이지 |
| ------------------------------------------ | --------------------------------------------------------------------- | --------------------------------------- |
| `exec` / `process`                         | 셸 명령 실행, 백그라운드 프로세스 관리 | [Exec](/tools/exec) |
| `code_execution`                           | 샌드박스된 원격 Python 분석 실행 | [Code Execution](/tools/code-execution) |
| `browser`                                  | Chromium 브라우저 제어(탐색, 클릭, 스크린샷) | [Browser](/tools/browser) |
| `web_search` / `x_search` / `web_fetch`    | 웹 검색, X 게시물 검색, 페이지 콘텐츠 가져오기 | [Web](/tools/web) |
| `read` / `write` / `edit`                  | 워크스페이스의 파일 I/O |                                         |
| `apply_patch`                              | 여러 청크에 걸친 파일 패치 | [Apply Patch](/tools/apply-patch) |
| `message`                                  | 모든 채널로 메시지 전송 | [Agent Send](/tools/agent-send) |
| `canvas`                                   | 노드 Canvas 제어(present, eval, snapshot) |                                         |
| `nodes`                                    | 페어링된 디바이스 탐색 및 대상으로 지정 |                                         |
| `cron` / `gateway`                         | 예약 작업 관리, gateway 검사, 패치, 재시작, 업데이트 |                                         |
| `image` / `image_generate`                 | 이미지 분석 또는 생성 |                                         |
| `tts`                                      | 일회성 텍스트 음성 변환 | [TTS](/tools/tts) |
| `sessions_*` / `subagents` / `agents_list` | 세션 관리, 상태 확인, 하위 에이전트 오케스트레이션 | [Sub-agents](/tools/subagents) |
| `session_status`                           | 경량 `/status` 스타일 읽기 및 세션 모델 재정의 | [Session Tools](/ko/concepts/session-tool) |

이미지 작업에는 분석용 `image`, 생성 또는 편집용 `image_generate`를 사용하세요. `openai/*`, `google/*`, `fal/*` 또는 다른 기본이 아닌 이미지 공급자를 대상으로 하는 경우 먼저 해당 공급자의 인증/API 키를 구성하세요.

`session_status`는 sessions 그룹의 경량 상태/읽기 도구입니다.
이 도구는 현재 세션에 대한 `/status` 스타일 질문에 답변하고,
선택적으로 세션별 모델 재정의를 설정할 수 있으며, `model=default`는
해당 재정의를 지웁니다. `/status`와 마찬가지로 최신 전사 usage 항목에서
희소한 토큰/캐시 카운터와 활성 런타임 모델 레이블을 보완할 수 있습니다.

`gateway`는 gateway 작업을 위한 소유자 전용 런타임 도구입니다:

- 편집 전 하나의 경로 범위 구성 하위 트리를 조회하는 `config.schema.lookup`
- 현재 구성 스냅샷 + 해시를 가져오는 `config.get`
- 재시작과 함께 부분 구성 업데이트를 수행하는 `config.patch`
- 전체 구성을 교체할 때만 사용하는 `config.apply`
- 명시적 자체 업데이트 + 재시작을 수행하는 `update.run`

부분 변경의 경우 `config.schema.lookup` 다음에 `config.patch`를 우선 사용하세요.
의도적으로 전체 구성을 교체할 때만 `config.apply`를 사용하세요.
이 도구는 또한 `tools.exec.ask` 또는 `tools.exec.security` 변경을 거부합니다.
레거시 `tools.bash.*` 별칭은 동일한 보호된 exec 경로로 정규화됩니다.

### plugin이 제공하는 도구

plugin은 추가 도구를 등록할 수 있습니다. 몇 가지 예:

- [Lobster](/tools/lobster) — 재개 가능한 승인이 있는 타입 안전 워크플로 런타임
- [LLM Task](/tools/llm-task) — 구조화된 출력을 위한 JSON 전용 LLM 단계
- [Diffs](/tools/diffs) — diff 뷰어 및 렌더러
- [OpenProse](/ko/prose) — 마크다운 우선 워크플로 오케스트레이션

## 도구 구성

### 허용 및 거부 목록

구성의 `tools.allow` / `tools.deny`를 통해 에이전트가 호출할 수 있는 도구를 제어합니다.
거부는 항상 허용보다 우선합니다.

```json5
{
  tools: {
    allow: ["group:fs", "browser", "web_search"],
    deny: ["exec"],
  },
}
```

### 도구 프로필

`tools.profile`은 `allow`/`deny`가 적용되기 전에 기본 허용 목록을 설정합니다.
에이전트별 재정의: `agents.list[].tools.profile`.

| 프로필 | 포함 내용 |
| ----------- | ------------------------------------------------------------------------------------------------------------- |
| `full`      | 제한 없음(설정하지 않은 것과 동일) |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status` |
| `minimal`   | `session_status`만 |

### 도구 그룹

허용/거부 목록에서 `group:*` 축약형을 사용하세요:

| 그룹 | 도구 |
| ------------------ | --------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | exec, process, code_execution (`bash`는 `exec`의 별칭으로 허용됨) |
| `group:fs`         | read, write, edit, apply_patch |
| `group:sessions`   | sessions_list, sessions_history, sessions_send, sessions_spawn, sessions_yield, subagents, session_status |
| `group:memory`     | memory_search, memory_get |
| `group:web`        | web_search, x_search, web_fetch |
| `group:ui`         | browser, canvas |
| `group:automation` | cron, gateway |
| `group:messaging`  | message |
| `group:nodes`      | nodes |
| `group:agents`     | agents_list |
| `group:media`      | image, image_generate, tts |
| `group:openclaw`   | 모든 내장 OpenClaw 도구(plugin 도구 제외) |

`sessions_history`는 제한되고 안전 필터링된 회상 보기를 반환합니다.
이 도구는 thinking 태그, `<relevant-memories>` 스캐폴딩, 일반 텍스트 도구 호출 XML
페이로드( `<tool_call>...</tool_call>`,
`<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`,
`<function_calls>...</function_calls>`, 잘린 도구 호출 블록 포함),
축소된 도구 호출 스캐폴딩, 유출된 ASCII/전각 모델 제어
토큰, 어시스턴트 텍스트의 잘못된 MiniMax 도구 호출 XML을 제거한 다음,
원시 전사 덤프처럼 동작하는 대신 마스킹/잘라내기와
필요 시 과대 행 자리표시자를 적용합니다.

### 공급자별 제한

전역 기본값을 변경하지 않고 특정 공급자에 대한 도구를 제한하려면
`tools.byProvider`를 사용하세요:

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
  },
}
```
