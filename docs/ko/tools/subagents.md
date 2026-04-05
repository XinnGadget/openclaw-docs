---
read_when:
    - agent를 통해 백그라운드/병렬 작업을 원할 때
    - sessions_spawn 또는 sub-agent tool 정책을 변경할 때
    - thread에 바인딩된 subagent 세션을 구현하거나 문제 해결할 때
summary: 요청자 채팅으로 결과를 다시 알리는 격리된 agent 실행을 spawn하는 Sub-agent
title: Sub-agent
x-i18n:
    generated_at: "2026-04-05T12:58:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9df7cc35a3069ce4eb9c92a95df3ce5365a00a3fae92ff73def75461b58fec3f
    source_path: tools/subagents.md
    workflow: 15
---

# Sub-agent

Sub-agent는 기존 agent 실행에서 spawn되는 백그라운드 agent 실행입니다. 이들은 자체 세션(`agent:<agentId>:subagent:<uuid>`)에서 실행되며, 완료되면 결과를 요청자 채팅 채널에 다시 **알립니다**. 각 sub-agent 실행은 [백그라운드 작업](/ko/automation/tasks)으로 추적됩니다.

## Slash command

**현재 세션**의 sub-agent 실행을 확인하거나 제어하려면 `/subagents`를 사용하세요.

- `/subagents list`
- `/subagents kill <id|#|all>`
- `/subagents log <id|#> [limit] [tools]`
- `/subagents info <id|#>`
- `/subagents send <id|#> <message>`
- `/subagents steer <id|#> <message>`
- `/subagents spawn <agentId> <task> [--model <model>] [--thinking <level>]`

thread 바인딩 제어:

이 command는 지속적인 thread 바인딩을 지원하는 채널에서 동작합니다. 아래 **thread를 지원하는 채널**을 참고하세요.

- `/focus <subagent-label|session-key|session-id|session-label>`
- `/unfocus`
- `/agents`
- `/session idle <duration|off>`
- `/session max-age <duration|off>`

`/subagents info`는 실행 메타데이터(상태, 타임스탬프, session id, transcript 경로, cleanup)를 표시합니다.
범위가 제한되고 안전 필터링된 회상 뷰에는 `sessions_history`를 사용하고,
원시 전체 transcript가 필요할 때는 디스크의 transcript 경로를 확인하세요.

### Spawn 동작

`/subagents spawn`은 백그라운드 sub-agent를 내부 relay가 아닌 사용자 command로 시작하며, 실행이 끝나면 요청자 채팅으로 최종 완료 업데이트 하나를 전송합니다.

- spawn command는 non-blocking입니다. 즉시 run id를 반환합니다.
- 완료 시 sub-agent는 요청자 채팅 채널에 요약/결과 메시지를 알립니다.
- 완료는 push 기반입니다. 한 번 spawn한 뒤에는 완료를 기다리기 위해
  `/subagents list`, `sessions_list`, `sessions_history`를 반복 호출하거나
  루프를 돌리지 마세요. 상태 확인은 디버깅이나 개입이 필요할 때만 수행하세요.
- 완료 시 OpenClaw는 최선의 노력으로 해당 sub-agent 세션이 연 추적된 브라우저 탭/프로세스를 닫은 뒤 announce cleanup 흐름을 계속합니다.
- 수동 spawn의 경우 전달은 복원력이 있습니다.
  - OpenClaw는 먼저 안정적인 멱등성 키를 사용해 직접 `agent` 전달을 시도합니다.
  - 직접 전달이 실패하면 queue 라우팅으로 fallback합니다.
  - queue 라우팅도 불가능하면 최종 포기 전 짧은 지수 백오프로 announce를 재시도합니다.
- 완료 전달은 resolve된 요청자 경로를 유지합니다.
  - 가능하면 thread 바인딩 또는 conversation 바인딩 완료 경로가 우선합니다
  - 완료 origin이 채널만 제공하는 경우, OpenClaw는 요청자 세션의 resolve된 경로(`lastChannel` / `lastTo` / `lastAccountId`)에서 누락된 target/account를 채워 직접 전달이 계속 동작하도록 합니다
- 요청자 세션으로의 완료 handoff는 런타임이 생성한 내부 컨텍스트이며(사용자 작성 텍스트 아님), 다음을 포함합니다.
  - `Result` (가장 최신의 보이는 `assistant` 답변 텍스트, 없으면 정리된 최신 tool/toolResult 텍스트)
  - `Status` (`completed successfully` / `failed` / `timed out` / `unknown`)
  - 간결한 런타임/토큰 통계
  - 원시 내부 메타데이터를 그대로 전달하지 말고 일반 assistant 음성으로 다시 작성하라는 전달 지시
- `--model`과 `--thinking`은 해당 실행에 대해서만 기본값을 override합니다.
- 완료 후 세부 정보와 출력을 확인하려면 `info`/`log`를 사용하세요.
- `/subagents spawn`은 일회성 모드(`mode: "run"`)입니다. 지속적인 thread 바인딩 세션에는 `thread: true` 및 `mode: "session"`으로 `sessions_spawn`을 사용하세요.
- ACP harness 세션(Codex, Claude Code, Gemini CLI)에는 `runtime: "acp"`로 `sessions_spawn`을 사용하고 [ACP agent](/tools/acp-agents)를 참고하세요.

주요 목표:

- 메인 실행을 막지 않고 "조사 / 장기 작업 / 느린 tool" 작업을 병렬화합니다.
- 기본적으로 sub-agent를 격리 상태로 유지합니다(세션 분리 + 선택적 샌드박싱).
- tool surface를 오용하기 어렵게 유지합니다: sub-agent는 기본적으로 session tool을 받지 않습니다.
- orchestrator 패턴을 위한 설정 가능한 중첩 깊이를 지원합니다.

비용 참고: 각 sub-agent는 **자체적인** 컨텍스트와 토큰 사용량을 가집니다. 무겁거나 반복적인
작업의 경우 sub-agent에는 더 저렴한 모델을 설정하고 메인 agent는 더 고품질 모델로 유지하세요.
이는 `agents.defaults.subagents.model` 또는 agent별 override로 설정할 수 있습니다.

## Tool

`sessions_spawn` 사용:

- sub-agent 실행 시작 (`deliver: false`, 전역 lane: `subagent`)
- 그런 다음 announce 단계를 실행하고 announce 답변을 요청자 채팅 채널에 게시
- 기본 모델: `agents.defaults.subagents.model`(또는 agent별 `agents.list[].subagents.model`)을 설정하지 않으면 호출자를 상속합니다. 명시적인 `sessions_spawn.model`은 여전히 우선합니다.
- 기본 thinking: `agents.defaults.subagents.thinking`(또는 agent별 `agents.list[].subagents.thinking`)을 설정하지 않으면 호출자를 상속합니다. 명시적인 `sessions_spawn.thinking`은 여전히 우선합니다.
- 기본 실행 timeout: `sessions_spawn.runTimeoutSeconds`가 생략되면, 설정된 경우 OpenClaw는 `agents.defaults.subagents.runTimeoutSeconds`를 사용하고, 그렇지 않으면 `0`(timeout 없음)으로 fallback합니다.

tool 파라미터:

- `task` (필수)
- `label?` (선택 사항)
- `agentId?` (선택 사항; 허용되는 경우 다른 agent id 아래에서 spawn)
- `model?` (선택 사항; sub-agent 모델 override; 잘못된 값은 건너뛰고 tool 결과에 경고를 남긴 채 기본 모델로 sub-agent가 실행됨)
- `thinking?` (선택 사항; sub-agent 실행의 thinking 레벨 override)
- `runTimeoutSeconds?` (설정된 경우 기본값은 `agents.defaults.subagents.runTimeoutSeconds`, 그렇지 않으면 `0`; 설정 시 sub-agent 실행은 N초 후 중단됨)
- `thread?` (기본값 `false`; `true`이면 이 sub-agent 세션에 대한 채널 thread 바인딩 요청)
- `mode?` (`run|session`)
  - 기본값은 `run`
  - `thread: true`이고 `mode`가 생략되면 기본값은 `session`
  - `mode: "session"`에는 `thread: true`가 필요함
- `cleanup?` (`delete|keep`, 기본값 `keep`)
- `sandbox?` (`inherit|require`, 기본값 `inherit`; `require`는 대상 자식 런타임이 샌드박스 상태가 아니면 spawn을 거부)
- `sessions_spawn`은 채널 전달 파라미터(`target`, `channel`, `to`, `threadId`, `replyTo`, `transport`)를 받지 않습니다. 전달은 spawn된 실행에서 `message`/`sessions_send`를 사용하세요.

## thread에 바인딩된 세션

채널에서 thread 바인딩이 활성화되어 있으면, sub-agent는 thread에 바인딩된 상태로 유지될 수 있어 해당 thread의 후속 사용자 메시지가 같은 sub-agent 세션으로 계속 라우팅됩니다.

### thread를 지원하는 채널

- Discord(현재 유일한 지원 채널): 지속적인 thread 바인딩 subagent 세션(`thread: true`인 `sessions_spawn`), 수동 thread 제어(`/_focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`), 그리고 adapter key `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`, `channels.discord.threadBindings.spawnSubagentSessions`를 지원합니다.

빠른 흐름:

1. `thread: true`(및 선택적으로 `mode: "session"`)로 `sessions_spawn`을 사용해 spawn합니다.
2. OpenClaw가 활성 채널에서 thread를 만들거나 그 세션 대상에 바인딩합니다.
3. 해당 thread의 답변과 후속 메시지는 바인딩된 세션으로 라우팅됩니다.
4. `/session idle`을 사용해 비활성 자동 unfocus를 확인/업데이트하고, `/session max-age`로 하드 제한을 제어합니다.
5. 수동으로 분리하려면 `/unfocus`를 사용합니다.

수동 제어:

- `/focus <target>`은 현재 thread를 sub-agent/session 대상에 바인딩합니다(또는 thread를 생성).
- `/unfocus`는 현재 바인딩된 thread의 바인딩을 제거합니다.
- `/agents`는 활성 실행과 바인딩 상태(`thread:<id>` 또는 `unbound`)를 나열합니다.
- `/session idle`과 `/session max-age`는 포커스된 바인딩 thread에서만 동작합니다.

config 스위치:

- 전역 기본값: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`
- 채널 override 및 spawn 자동 바인딩 key는 adapter별입니다. 위의 **thread를 지원하는 채널**을 참고하세요.

현재 adapter 세부사항은 [Configuration Reference](/ko/gateway/configuration-reference) 및 [Slash commands](/tools/slash-commands)를 참고하세요.

allowlist:

- `agents.list[].subagents.allowAgents`: `agentId`를 통해 대상으로 지정할 수 있는 agent id 목록(`["*"]`는 모든 agent 허용). 기본값: 요청자 agent만.
- `agents.defaults.subagents.allowAgents`: 요청자 agent가 자체 `subagents.allowAgents`를 설정하지 않았을 때 사용하는 기본 대상-agent allowlist.
- 샌드박스 상속 가드: 요청자 세션이 샌드박스 상태면 `sessions_spawn`은 샌드박스 없이 실행될 대상을 거부합니다.
- `agents.defaults.subagents.requireAgentId` / `agents.list[].subagents.requireAgentId`: true일 때 `agentId`를 생략한 `sessions_spawn` 호출을 차단합니다(명시적 profile 선택 강제). 기본값: false.

discovery:

- 현재 `sessions_spawn`에 허용된 agent id를 보려면 `agents_list`를 사용하세요.

자동 보관:

- sub-agent 세션은 `agents.defaults.subagents.archiveAfterMinutes` 후 자동 보관됩니다(기본값: 60).
- 보관은 `sessions.delete`를 사용하고 transcript를 `*.deleted.<timestamp>`로 이름 변경합니다(같은 폴더).
- `cleanup: "delete"`는 announce 직후 즉시 보관합니다(여전히 transcript는 이름 변경을 통해 유지).
- 자동 보관은 최선의 노력이며, gateway가 재시작되면 보류 중인 타이머는 사라집니다.
- `runTimeoutSeconds`는 자동 보관하지 않습니다. 실행만 중지합니다. 세션은 자동 보관까지 유지됩니다.
- 자동 보관은 depth-1과 depth-2 세션에 동일하게 적용됩니다.
- 브라우저 cleanup은 보관 cleanup과 별개입니다. transcript/session 레코드가 유지되더라도, 실행이 끝나면 추적된 브라우저 탭/프로세스를 최선의 노력으로 닫습니다.

## 중첩 Sub-agent

기본적으로 sub-agent는 자신의 sub-agent를 spawn할 수 없습니다(`maxSpawnDepth: 1`). `maxSpawnDepth: 2`를 설정하면 한 단계의 중첩을 활성화할 수 있으며, 이는 **orchestrator 패턴**을 허용합니다: main → orchestrator sub-agent → worker sub-sub-agent.

### 활성화 방법

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxSpawnDepth: 2, // sub-agent가 자식을 spawn할 수 있게 허용 (기본값: 1)
        maxChildrenPerAgent: 5, // agent 세션당 최대 활성 자식 수 (기본값: 5)
        maxConcurrent: 8, // 전역 동시성 lane 상한 (기본값: 8)
        runTimeoutSeconds: 900, // sessions_spawn 생략 시 기본 timeout (0 = timeout 없음)
      },
    },
  },
}
```

### 깊이 수준

| Depth | Session key 형태                            | 역할                                          | spawn 가능 여부               |
| ----- | ------------------------------------------- | --------------------------------------------- | ----------------------------- |
| 0     | `agent:<id>:main`                           | 메인 agent                                    | 항상 가능                     |
| 1     | `agent:<id>:subagent:<uuid>`                | Sub-agent (`depth 2` 허용 시 orchestrator)    | `maxSpawnDepth >= 2`일 때만   |
| 2     | `agent:<id>:subagent:<uuid>:subagent:<uuid>` | Sub-sub-agent(leaf worker)                    | 불가                          |

### 알림 체인

결과는 체인을 따라 상위로 전달됩니다.

1. depth-2 worker 완료 → 부모(depth-1 orchestrator)에게 알림
2. depth-1 orchestrator가 알림을 수신하고 결과를 종합한 뒤 완료 → main에 알림
3. main agent가 알림을 수신하고 사용자에게 전달

각 수준은 직접적인 자식의 알림만 봅니다.

운영 지침:

- 자식 작업은 한 번 시작하고, `sessions_list`, `sessions_history`, `/subagents list`,
  또는 `exec` sleep command를 중심으로 poll 루프를 만들지 말고 완료 이벤트를 기다리세요.
- 자식 완료 이벤트가 최종 답변을 이미 보낸 뒤 도착했다면,
  올바른 후속 동작은 정확히 `NO_REPLY` / `no_reply`라는 무음 토큰입니다.

### 깊이별 tool 정책

- 역할과 제어 범위는 spawn 시점에 세션 메타데이터에 기록됩니다. 이렇게 하면 평면화되었거나 복원된 session key가 의도치 않게 orchestrator 권한을 되찾는 일을 막을 수 있습니다.
- **Depth 1 (`maxSpawnDepth >= 2`일 때 orchestrator)**: 자식을 관리할 수 있도록 `sessions_spawn`, `subagents`, `sessions_list`, `sessions_history`를 받습니다. 다른 session/system tool은 계속 거부됩니다.
- **Depth 1 (`maxSpawnDepth == 1`일 때 leaf)**: session tool 없음(현재 기본 동작).
- **Depth 2 (leaf worker)**: session tool 없음 — depth 2에서는 `sessions_spawn`이 항상 거부됩니다. 더 깊은 자식을 spawn할 수 없습니다.

### agent별 spawn 제한

각 agent 세션(어떤 depth이든)은 동시에 최대 `maxChildrenPerAgent`(기본값: 5)개의 활성 자식을 가질 수 있습니다. 이는 단일 orchestrator로부터의 과도한 fan-out을 방지합니다.

### 연쇄 중지

depth-1 orchestrator를 중지하면 모든 depth-2 자식도 자동으로 중지됩니다.

- 메인 채팅에서 `/stop`을 실행하면 모든 depth-1 agent가 중지되고 해당 depth-2 자식에도 연쇄 적용됩니다.
- `/subagents kill <id>`는 특정 sub-agent를 중지하고 그 자식에게도 연쇄 적용됩니다.
- `/subagents kill all`은 요청자의 모든 sub-agent를 중지하고 연쇄 적용됩니다.

## 인증

sub-agent 인증은 세션 타입이 아니라 **agent id**를 기준으로 resolve됩니다.

- sub-agent session key는 `agent:<agentId>:subagent:<uuid>`입니다.
- auth 저장소는 해당 agent의 `agentDir`에서 로드됩니다.
- 메인 agent의 auth profile은 **fallback**으로 병합되며, 충돌 시 agent profile이 main profile을 override합니다.

참고: 이 병합은 additive이므로 main profile은 항상 fallback으로 사용 가능합니다. agent별 완전한 격리 인증은 아직 지원되지 않습니다.

## announce

sub-agent는 announce 단계를 통해 결과를 보고합니다.

- announce 단계는 요청자 세션이 아니라 sub-agent 세션 내부에서 실행됩니다.
- sub-agent가 정확히 `ANNOUNCE_SKIP`로 답하면 아무것도 게시되지 않습니다.
- 최신 assistant 텍스트가 정확히 `NO_REPLY` / `no_reply`라는 무음 토큰이면,
  이전에 보이는 진행 상황이 있었더라도 announce 출력은 억제됩니다.
- 그 외에는 요청자 depth에 따라 전달이 달라집니다.
  - 최상위 요청자 세션은 외부 전달(`deliver=true`)이 있는 후속 `agent` 호출을 사용합니다
  - 중첩된 요청자 subagent 세션은 orchestrator가 세션 내에서 자식 결과를 종합할 수 있도록 내부 후속 주입(`deliver=false`)을 받습니다
  - 중첩된 요청자 subagent 세션이 사라졌다면, 가능하면 OpenClaw는 해당 세션의 요청자로 fallback합니다
- 최상위 요청자 세션의 경우, completion 모드 직접 전달은 먼저 바인딩된 conversation/thread 경로와 hook override를 resolve한 뒤, 요청자 세션에 저장된 경로에서 누락된 채널 대상 필드를 채웁니다. 이렇게 하면 완료 origin이 채널만 식별하더라도 올바른 chat/topic에서 완료 전달이 유지됩니다.
- 중첩된 완료 결과를 구성할 때 자식 완료 집계는 현재 요청자 실행 범위로 제한되므로, 이전 실행의 오래된 자식 출력이 현재 announce에 섞이지 않습니다.
- 채널 adapter에서 가능할 경우 announce 답변은 thread/topic 라우팅을 유지합니다.
- announce 컨텍스트는 안정적인 내부 이벤트 블록으로 정규화됩니다.
  - source (`subagent` 또는 `cron`)
  - 자식 session key/id
  - announce 타입 + task label
  - 런타임 결과(`success`, `error`, `timeout`, `unknown`)에서 파생된 status 라인
  - 가장 최신의 보이는 assistant 텍스트에서 선택한 결과 콘텐츠, 없으면 정리된 최신 tool/toolResult 텍스트
  - 언제 답해야 하고 언제 조용히 있어야 하는지 설명하는 후속 지시
- `Status`는 모델 출력에서 추론되지 않습니다. 런타임 결과 신호에서 가져옵니다.
- timeout 시 자식이 tool 호출까지만 진행했다면, announce는 원시 tool 출력을 재생하는 대신 그 히스토리를 짧은 부분 진행 요약으로 축약할 수 있습니다.

announce payload는 끝에 통계 라인을 포함합니다(래핑된 경우에도 동일).

- Runtime (예: `runtime 5m12s`)
- 토큰 사용량(input/output/total)
- 모델 가격이 설정된 경우 예상 비용(`models.providers.*.models[].cost`)
- `sessionKey`, `sessionId`, transcript 경로(따라서 main agent가 `sessions_history`로 히스토리를 가져오거나 디스크 파일을 직접 확인할 수 있음)
- 내부 메타데이터는 오케스트레이션 전용입니다. 사용자 대상 답변은 일반 assistant 음성으로 다시 작성해야 합니다.

`sessions_history`는 더 안전한 오케스트레이션 경로입니다.

- assistant 회상은 먼저 정규화됩니다.
  - thinking tag는 제거됩니다
  - `<relevant-memories>` / `<relevant_memories>` scaffold 블록은 제거됩니다
  - `<tool_call>...</tool_call>`,
    `<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`,
    `<function_calls>...</function_calls>` 같은 일반 텍스트 tool-call XML payload 블록은 제거되며,
    정상적으로 닫히지 않은 잘린 payload도 포함됩니다
  - 강등된 tool-call/result scaffold 및 historical-context marker는 제거됩니다
  - `<|assistant|>` 같은 누출된 모델 제어 토큰, 기타 ASCII
    `<|...|>` 토큰, 전체 폭 `<｜...｜>` 변형은 제거됩니다
  - 잘못된 MiniMax tool-call XML은 제거됩니다
- credential/token 유사 텍스트는 redaction됩니다
- 긴 블록은 잘릴 수 있습니다
- 매우 큰 히스토리는 오래된 row를 제거하거나 큰 row 하나를
  `[sessions_history omitted: message too large]`로 대체할 수 있습니다
- 전체 바이트 단위 transcript가 필요하면 원시 디스크 transcript 확인이 fallback입니다

## Tool 정책(sub-agent tool)

기본적으로 sub-agent는 **session tool과** system tool을 제외한 **모든 tool**을 받습니다.

- `sessions_list`
- `sessions_history`
- `sessions_send`
- `sessions_spawn`

여기서도 `sessions_history`는 범위가 제한되고 정리된 회상 뷰이며,
원시 transcript 덤프가 아닙니다.

`maxSpawnDepth >= 2`일 때 depth-1 orchestrator sub-agent는 자식을 관리할 수 있도록 추가로 `sessions_spawn`, `subagents`, `sessions_list`, `sessions_history`를 받습니다.

config를 통한 override:

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxConcurrent: 1,
      },
    },
  },
  tools: {
    subagents: {
      tools: {
        // deny가 우선
        deny: ["gateway", "cron"],
        // allow가 설정되면 allow-only가 됨(deny가 여전히 우선)
        // allow: ["read", "exec", "process"]
      },
    },
  },
}
```

## 동시성

sub-agent는 전용 in-process queue lane을 사용합니다.

- Lane 이름: `subagent`
- 동시성: `agents.defaults.subagents.maxConcurrent` (기본값 `8`)

## 중지

- 요청자 채팅에 `/stop`을 보내면 요청자 세션이 중단되고, 여기서 spawn된 활성 sub-agent 실행도 중첩된 자식까지 연쇄적으로 중지됩니다.
- `/subagents kill <id>`는 특정 sub-agent를 중지하고 그 자식에게도 연쇄 적용됩니다.

## 제한 사항

- sub-agent announce는 **best-effort**입니다. gateway가 재시작되면 대기 중인 "결과 알림" 작업은 사라집니다.
- sub-agent는 여전히 동일한 gateway 프로세스 리소스를 공유하므로 `maxConcurrent`를 안전 밸브로 취급하세요.
- `sessions_spawn`은 항상 non-blocking입니다. 즉시 `{ status: "accepted", runId, childSessionKey }`를 반환합니다.
- sub-agent 컨텍스트는 `AGENTS.md` + `TOOLS.md`만 주입합니다(`SOUL.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`는 없음).
- 최대 중첩 깊이는 5입니다(`maxSpawnDepth` 범위: 1–5). 대부분의 사용 사례에는 depth 2를 권장합니다.
- `maxChildrenPerAgent`는 세션당 활성 자식 수를 제한합니다(기본값: 5, 범위: 1–20).
