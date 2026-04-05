---
read_when:
    - 시스템 프롬프트 텍스트, 도구 목록 또는 시간/heartbeat 섹션을 편집하는 경우
    - workspace bootstrap 또는 Skills 주입 동작을 변경하는 경우
summary: OpenClaw 시스템 프롬프트에 무엇이 포함되며 어떻게 조립되는지
title: 시스템 프롬프트
x-i18n:
    generated_at: "2026-04-05T12:41:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: f86b2fa496b183b64e86e6ddc493e4653ff8c9727d813fe33c8f8320184d022f
    source_path: concepts/system-prompt.md
    workflow: 15
---

# 시스템 프롬프트

OpenClaw는 모든 에이전트 실행마다 사용자 지정 시스템 프롬프트를 구성합니다. 이 프롬프트는 **OpenClaw 소유**이며 pi-coding-agent 기본 프롬프트를 사용하지 않습니다.

프롬프트는 OpenClaw가 조립하여 각 에이전트 실행에 주입합니다.

## 구조

프롬프트는 의도적으로 간결하게 유지되며 고정된 섹션을 사용합니다.

- **Tooling**: 현재 도구 목록 + 짧은 설명
- **Safety**: 권력 추구 행동이나 감독 우회를 피하도록 하는 짧은 가드레일 알림
- **Skills** (사용 가능한 경우): 필요할 때 Skills 지침을 로드하는 방법을 모델에 알려줌
- **OpenClaw Self-Update**: `config.schema.lookup`으로 config를 안전하게 검사하고, `config.patch`로 config를 패치하고, `config.apply`로 전체 config를 교체하며, 사용자의 명시적 요청이 있을 때만 `update.run`을 실행하는 방법. 소유자 전용 `gateway` 도구는 보호된 exec 경로로 정규화되는 레거시 `tools.bash.*` 별칭을 포함해 `tools.exec.ask` / `tools.exec.security` 재작성도 거부합니다.
- **Workspace**: 작업 디렉터리(`agents.defaults.workspace`)
- **Documentation**: OpenClaw 문서의 로컬 경로(리포지토리 또는 npm 패키지) 및 언제 읽어야 하는지
- **Workspace Files (injected)**: bootstrap 파일이 아래에 포함되어 있음을 나타냄
- **Sandbox** (활성화된 경우): sandbox 런타임, sandbox 경로, 상승된 exec 사용 가능 여부를 나타냄
- **Current Date & Time**: 사용자 로컬 시간, 시간대, 시간 형식
- **Reply Tags**: 지원되는 provider용 선택적 응답 태그 문법
- **Heartbeats**: heartbeat 프롬프트 및 ack 동작
- **Runtime**: 호스트, OS, node, 모델, 리포지토리 루트(감지된 경우), thinking level(한 줄)
- **Reasoning**: 현재 가시성 수준 + /reasoning 토글 힌트

Tooling 섹션에는 장기 실행 작업을 위한 런타임 가이드도 포함됩니다.

- 미래 후속 작업(`나중에 다시 확인`, 알림, 반복 작업)에는 `exec` sleep 루프, `yieldMs` 지연 트릭 또는 반복적인 `process` 폴링 대신 cron 사용
- 지금 시작해서 백그라운드에서 계속 실행되는 명령에만 `exec` / `process` 사용
- 자동 완료 wake가 활성화된 경우, 명령은 한 번만 시작하고 출력 또는 실패 시 푸시 기반 wake 경로에 의존
- 실행 중인 명령을 검사해야 할 때는 로그, 상태, 입력 또는 개입을 위해 `process` 사용
- 작업이 더 크다면 `sessions_spawn`을 우선 사용. 서브에이전트 완료는 푸시 기반이며 요청자에게 자동으로 알림
- 완료를 기다리기 위해 `subagents list` / `sessions_list`를 루프로 폴링하지 말 것

시스템 프롬프트의 Safety 가드레일은 권고 사항입니다. 이는 모델 동작을 안내하지만 정책을 강제하지는 않습니다. 강제 적용에는 도구 정책, exec 승인, sandboxing, 채널 허용 목록을 사용하세요. 운영자는 설계상 이를 비활성화할 수 있습니다.

네이티브 승인 카드/버튼을 지원하는 채널에서는 이제 런타임 프롬프트가 에이전트에게 먼저 해당 네이티브 승인 UI를 사용하도록 지시합니다. 도구 결과에서 채팅 승인을 사용할 수 없거나 수동 승인이 유일한 경로라고 할 때만 수동 `/approve` 명령을 포함해야 합니다.

## 프롬프트 모드

OpenClaw는 서브에이전트를 위해 더 작은 시스템 프롬프트를 렌더링할 수 있습니다. 런타임은 각 실행에 대해 `promptMode`를 설정합니다(사용자 대상 config는 아님).

- `full` (기본값): 위의 모든 섹션 포함
- `minimal`: 서브에이전트에 사용되며 **Skills**, **Memory Recall**, **OpenClaw Self-Update**, **Model Aliases**, **User Identity**, **Reply Tags**, **Messaging**, **Silent Replies**, **Heartbeats**를 생략합니다. Tooling, **Safety**, Workspace, Sandbox, Current Date & Time(알려진 경우), Runtime, 주입된 컨텍스트는 그대로 유지됩니다.
- `none`: 기본 정체성 한 줄만 반환

`promptMode=minimal`일 때 추가로 주입되는 프롬프트는 **Group Chat Context** 대신 **Subagent Context**로 표시됩니다.

## Workspace bootstrap 주입

bootstrap 파일은 모델이 명시적으로 읽지 않아도 정체성과 프로필 컨텍스트를 볼 수 있도록 **Project Context** 아래에 다듬어져 추가됩니다.

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (완전히 새로운 workspace에서만)
- `MEMORY.md`가 있으면 사용, 없으면 소문자 폴백으로 `memory.md`

이 모든 파일은 매 턴마다 **컨텍스트 창에 주입**되므로 토큰을 소비합니다. 간결하게 유지하세요. 특히 `MEMORY.md`는 시간이 지나며 커질 수 있고, 예상보다 높은 컨텍스트 사용량과 더 잦은 압축으로 이어질 수 있습니다.

> **참고:** `memory/*.md` 일일 파일은 자동으로 주입되지 않습니다. 이 파일들은 필요 시 `memory_search` 및 `memory_get` 도구를 통해 접근되므로, 모델이 명시적으로 읽지 않는 한 컨텍스트 창을 차지하지 않습니다.

큰 파일은 마커와 함께 잘립니다. 파일별 최대 크기는 `agents.defaults.bootstrapMaxChars`(기본값: 20000)로 제어됩니다. 파일 전체에 걸친 총 주입 bootstrap 콘텐츠는 `agents.defaults.bootstrapTotalMaxChars`(기본값: 150000)로 제한됩니다. 누락된 파일은 짧은 missing-file 마커를 주입합니다. 잘림이 발생하면 OpenClaw는 Project Context에 경고 블록을 주입할 수 있습니다. 이는 `agents.defaults.bootstrapPromptTruncationWarning` (`off`, `once`, `always`; 기본값: `once`)으로 제어합니다.

서브에이전트 세션은 `AGENTS.md`와 `TOOLS.md`만 주입합니다(다른 bootstrap 파일은 서브에이전트 컨텍스트를 작게 유지하기 위해 필터링됨).

내부 hooks는 `agent:bootstrap`을 통해 이 단계에 개입하여 주입되는 bootstrap 파일을 변경하거나 교체할 수 있습니다(예: `SOUL.md`를 대체 persona로 교체).

에이전트가 덜 일반적으로 들리게 하려면 [SOUL.md Personality Guide](/concepts/soul)부터 시작하세요.

주입된 각 파일이 얼마나 기여하는지(raw 대비 injected, 잘림, 도구 스키마 오버헤드 포함) 확인하려면 `/context list` 또는 `/context detail`을 사용하세요. 자세한 내용은 [컨텍스트](/concepts/context)를 참조하세요.

## 시간 처리

사용자 시간대를 알고 있는 경우 시스템 프롬프트에는 전용 **Current Date & Time** 섹션이 포함됩니다. 프롬프트 캐시를 안정적으로 유지하기 위해 이제 **시간대만** 포함하며(동적인 시계나 시간 형식은 포함하지 않음).

에이전트가 현재 시간이 필요할 때는 `session_status`를 사용하세요. 상태 카드에는 타임스탬프 줄이 포함됩니다. 같은 도구는 선택적으로 세션별 모델 재정의도 설정할 수 있습니다(`model=default`는 이를 지움).

구성 항목:

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

전체 동작 세부 정보는 [날짜 및 시간](/date-time)을 참조하세요.

## Skills

사용 가능한 Skills가 있으면 OpenClaw는 각 Skill의 **파일 경로**를 포함하는 간결한 **사용 가능한 skills 목록**(`formatSkillsForPrompt`)을 주입합니다. 프롬프트는 모델에게 나열된 위치(workspace, managed 또는 bundled)에 있는 SKILL.md를 `read`로 로드하라고 지시합니다. 사용 가능한 Skills가 없으면 Skills 섹션은 생략됩니다.

적격성에는 Skill 메타데이터 게이트, 런타임 환경/config 검사, 그리고 `agents.defaults.skills` 또는 `agents.list[].skills`가 구성된 경우의 유효 에이전트 Skill 허용 목록이 포함됩니다.

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

이는 기본 프롬프트를 작게 유지하면서도 대상 Skill 사용은 가능하게 합니다.

## Documentation

사용 가능한 경우 시스템 프롬프트에는 로컬 OpenClaw 문서 디렉터리(리포지토리 workspace의 `docs/` 또는 번들 npm 패키지 문서)를 가리키는 **Documentation** 섹션이 포함되며, public 미러, 소스 리포지토리, 커뮤니티 Discord, 그리고 Skill 검색을 위한 ClawHub([https://clawhub.ai](https://clawhub.ai))도 함께 안내합니다. 프롬프트는 OpenClaw 동작, 명령, 구성 또는 아키텍처에 대해서는 먼저 로컬 문서를 참조하고, 가능하면 `openclaw status`를 스스로 실행하며(접근 권한이 없을 때만 사용자에게 묻도록) 지시합니다.
