---
read_when:
    - ACP를 통해 코딩 harness를 실행할 때
    - 메시징 채널에서 conversation에 바인딩된 ACP 세션을 설정할 때
    - 메시지 채널 conversation을 지속적인 ACP 세션에 바인딩할 때
    - ACP 백엔드 및 플러그인 연결을 문제 해결할 때
    - 채팅에서 `/acp` command를 운영할 때
summary: Codex, Claude Code, Cursor, Gemini CLI, OpenClaw ACP 및 기타 harness agent에 ACP 런타임 세션 사용
title: ACP agent
x-i18n:
    generated_at: "2026-04-05T12:57:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 47063abc8170129cd22808d9a4b23160d0f340f6dc789907589d349f68c12e3e
    source_path: tools/acp-agents.md
    workflow: 15
---

# ACP agent

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/) 세션을 사용하면 OpenClaw가 ACP 백엔드 플러그인을 통해 외부 코딩 harness(예: Pi, Claude Code, Codex, Cursor, Copilot, OpenClaw ACP, OpenCode, Gemini CLI 및 기타 지원되는 ACPX harness)를 실행할 수 있습니다.

OpenClaw에 자연어로 "이걸 Codex에서 실행해" 또는 "스레드에서 Claude Code를 시작해"라고 요청하면, OpenClaw는 해당 요청을 네이티브 sub-agent 런타임이 아니라 ACP 런타임으로 라우팅해야 합니다. 각 ACP 세션 spawn은 [백그라운드 작업](/ko/automation/tasks)으로 추적됩니다.

Codex 또는 Claude Code를 기존 OpenClaw 채널 conversation에 외부 MCP client로 직접 연결하려면
ACP 대신 [`openclaw mcp serve`](/cli/mcp)를 사용하세요.

## 어떤 페이지를 봐야 하나요?

가까운 위치에 있지만 혼동하기 쉬운 surface가 세 가지 있습니다.

| 원하는 작업                                                                     | 사용 대상                              | 참고                                                                                                              |
| -------------------------------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| OpenClaw를 _통해_ Codex, Claude Code, Gemini CLI 또는 다른 외부 harness 실행     | 이 페이지: ACP agent                  | 채팅 바인딩 세션, `/acp spawn`, `sessions_spawn({ runtime: "acp" })`, 백그라운드 작업, 런타임 제어              |
| OpenClaw Gateway 세션을 ACP 서버로 editor나 client에 _노출_                      | [`openclaw acp`](/cli/acp)            | 브리지 모드. IDE/client가 stdio/WebSocket을 통해 ACP로 OpenClaw와 통신                                            |
| 로컬 AI CLI를 텍스트 전용 fallback 모델로 재사용                                 | [CLI 백엔드](/ko/gateway/cli-backends)   | ACP 아님. OpenClaw tool 없음, ACP 제어 없음, harness 런타임 없음                                                  |

## 별도 설정 없이 바로 동작하나요?

대체로 그렇습니다.

- 새 설치에는 이제 번들 `acpx` 런타임 플러그인이 기본으로 활성화되어 포함됩니다.
- 번들 `acpx` 플러그인은 플러그인 로컬에 고정된 `acpx` 바이너리를 우선 사용합니다.
- 시작 시 OpenClaw는 해당 바이너리를 점검하고 필요하면 자체 복구합니다.
- 빠른 준비 상태 점검이 필요하면 `/acp doctor`부터 시작하세요.

처음 사용할 때 여전히 발생할 수 있는 일:

- 대상 harness adapter는 해당 harness를 처음 사용할 때 `npx`로 필요 시 가져올 수 있습니다.
- 해당 harness에 대한 vendor auth는 여전히 호스트에 존재해야 합니다.
- 호스트에 npm/네트워크 접근이 없으면 캐시를 미리 준비하거나 다른 방식으로 adapter를 설치하기 전까지 첫 실행 adapter 가져오기가 실패할 수 있습니다.

예시:

- `/acp spawn codex`: OpenClaw는 `acpx`를 부트스트랩할 준비가 되어 있어야 하지만, Codex ACP adapter는 여전히 첫 실행 시 가져오기가 필요할 수 있습니다.
- `/acp spawn claude`: Claude ACP adapter도 동일하며, 추가로 해당 호스트에 Claude 측 auth가 필요합니다.

## 빠른 운영자 흐름

실용적인 `/acp` 실행 절차가 필요하다면 이것을 사용하세요.

1. 세션 spawn:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. 바인딩된 conversation 또는 thread에서 작업합니다(또는 해당 session key를 명시적으로 지정).
3. 런타임 상태 확인:
   - `/acp status`
4. 필요에 따라 런타임 옵션 조정:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. 컨텍스트를 교체하지 않고 활성 세션을 조정:
   - `/acp steer tighten logging and continue`
6. 작업 중지:
   - `/acp cancel` (현재 turn 중지), 또는
   - `/acp close` (세션 종료 + 바인딩 제거)

## 사람을 위한 빠른 시작

자연스러운 요청 예시:

- "이 Discord 채널을 Codex에 바인딩해."
- "여기 스레드에서 지속적인 Codex 세션을 시작하고 집중 상태를 유지해."
- "이 작업을 일회성 Claude Code ACP 세션으로 실행하고 결과를 요약해."
- "이 iMessage 채팅을 Codex에 바인딩하고 후속 작업도 같은 workspace에서 계속해."
- "이 작업에 Gemini CLI를 스레드에서 사용하고, 후속 작업도 같은 스레드에서 계속해."

OpenClaw가 해야 할 일:

1. `runtime: "acp"`를 선택합니다.
2. 요청된 harness 대상(`agentId`, 예: `codex`)을 resolve합니다.
3. 현재 conversation 바인딩이 요청되었고 활성 채널이 이를 지원하면, ACP 세션을 해당 conversation에 바인딩합니다.
4. 그렇지 않고 thread 바인딩이 요청되었으며 현재 채널이 이를 지원하면, ACP 세션을 해당 thread에 바인딩합니다.
5. 초점 해제/종료/만료될 때까지 바인딩된 후속 메시지를 같은 ACP 세션으로 라우팅합니다.

## ACP와 sub-agent의 차이

외부 harness 런타임이 필요하면 ACP를 사용하세요. OpenClaw 네이티브 위임 실행이 필요하면 sub-agent를 사용하세요.

| 영역          | ACP 세션                              | Sub-agent 실행                    |
| ------------- | ------------------------------------- | --------------------------------- |
| 런타임        | ACP 백엔드 플러그인(예: acpx)         | OpenClaw 네이티브 sub-agent 런타임 |
| Session key   | `agent:<agentId>:acp:<uuid>`          | `agent:<agentId>:subagent:<uuid>` |
| 주요 command  | `/acp ...`                            | `/subagents ...`                  |
| Spawn tool    | `sessions_spawn` with `runtime:"acp"` | `sessions_spawn` (기본 런타임)     |

참고: [Sub-agents](/tools/subagents)

## ACP가 Claude Code를 실행하는 방식

ACP를 통한 Claude Code의 경우 스택은 다음과 같습니다.

1. OpenClaw ACP 세션 control plane
2. 번들 `acpx` 런타임 플러그인
3. Claude ACP adapter
4. Claude 측 런타임/세션 메커니즘

중요한 구분:

- ACP Claude는 직접 `claude-cli/...` fallback 런타임과 같은 것이 아닙니다.
- ACP Claude는 ACP 제어, 세션 재개, 백그라운드 작업 추적, 선택적인 conversation/thread 바인딩을 갖춘 harness 세션입니다.
- `claude-cli/...`는 텍스트 전용 로컬 CLI 백엔드입니다. [CLI 백엔드](/ko/gateway/cli-backends)를 참고하세요.

운영자를 위한 실용적인 규칙:

- `/acp spawn`, 바인딩 가능한 세션, 런타임 제어, 또는 지속적인 harness 작업이 필요하면 ACP를 사용
- 원시 CLI를 통한 단순 로컬 텍스트 fallback이 필요하면 CLI 백엔드를 사용

## 바인딩된 세션

### 현재 conversation 바인딩

현재 conversation을 자식 thread를 만들지 않는 지속적인 ACP workspace로 만들고 싶다면 `/acp spawn <harness> --bind here`를 사용하세요.

동작:

- OpenClaw는 채널 transport, auth, 안전성, 전달을 계속 소유합니다.
- 현재 conversation은 spawn된 ACP session key에 고정됩니다.
- 해당 conversation의 후속 메시지는 같은 ACP 세션으로 라우팅됩니다.
- `/new`와 `/reset`은 같은 바인딩된 ACP 세션을 제자리에서 재설정합니다.
- `/acp close`는 세션을 닫고 현재 conversation 바인딩을 제거합니다.

실제로 의미하는 것:

- `--bind here`는 같은 채팅 surface를 유지합니다. Discord에서는 현재 채널이 그대로 현재 채널로 유지됩니다.
- `--bind here`는 새 작업을 spawn하는 경우 여전히 새 ACP 세션을 만들 수 있습니다. 바인딩은 그 세션을 현재 conversation에 연결합니다.
- `--bind here`는 자체적으로 자식 Discord thread나 Telegram topic을 만들지 않습니다.
- ACP 런타임은 여전히 자체 작업 디렉터리(`cwd`) 또는 백엔드 관리 workspace를 디스크에 가질 수 있습니다. 이 런타임 workspace는 채팅 surface와 별개이며 새 메시징 thread를 의미하지 않습니다.
- 다른 ACP agent로 spawn하고 `--cwd`를 전달하지 않으면 OpenClaw는 기본적으로 요청자의 workspace가 아니라 **대상 agent의** workspace를 상속합니다.
- 상속된 workspace 경로가 없으면(`ENOENT`/`ENOTDIR`), OpenClaw는 잘못된 트리를 조용히 재사용하는 대신 백엔드 기본 cwd로 fallback합니다.
- 상속된 workspace는 존재하지만 접근할 수 없으면(예: `EACCES`), spawn은 `cwd`를 버리지 않고 실제 접근 오류를 반환합니다.

정신 모델:

- 채팅 surface: 사람들이 계속 대화하는 곳 (`Discord channel`, `Telegram topic`, `iMessage chat`)
- ACP 세션: OpenClaw가 라우팅하는 지속적인 Codex/Claude/Gemini 런타임 상태
- 자식 thread/topic: `--thread ...`로만 생성되는 선택적 추가 메시징 surface
- 런타임 workspace: harness가 실행되는 파일 시스템 위치 (`cwd`, repo checkout, 백엔드 workspace)

예시:

- `/acp spawn codex --bind here`: 이 채팅을 유지하고 Codex ACP 세션을 spawn 또는 연결한 뒤 이후 메시지를 여기서 해당 세션으로 라우팅
- `/acp spawn codex --thread auto`: OpenClaw가 자식 thread/topic을 만들고 그곳에 ACP 세션을 바인딩할 수 있음
- `/acp spawn codex --bind here --cwd /workspace/repo`: 위와 같은 채팅 바인딩이지만 Codex는 `/workspace/repo`에서 실행됨

현재 conversation 바인딩 지원:

- 현재 conversation 바인딩 지원을 광고하는 채팅/메시지 채널은 공유 conversation-binding 경로를 통해 `--bind here`를 사용할 수 있습니다.
- 커스텀 thread/topic 의미론이 있는 채널도 동일한 공유 인터페이스 뒤에서 채널별 정규화를 제공할 수 있습니다.
- `--bind here`는 항상 "현재 conversation을 제자리에서 바인딩"함을 의미합니다.
- 일반적인 현재 conversation 바인딩은 공유 OpenClaw 바인딩 저장소를 사용하며 일반적인 gateway 재시작 후에도 유지됩니다.

참고:

- `/acp spawn`에서는 `--bind here`와 `--thread ...`를 함께 사용할 수 없습니다.
- Discord에서 `--bind here`는 현재 채널 또는 thread를 제자리에서 바인딩합니다. OpenClaw가 `--thread auto|here`를 위해 자식 thread를 만들어야 할 때만 `spawnAcpSessions`가 필요합니다.
- 활성 채널이 현재 conversation ACP 바인딩을 노출하지 않으면 OpenClaw는 명확한 미지원 메시지를 반환합니다.
- `resume` 및 "new session" 질문은 채널 질문이 아니라 ACP 세션 질문입니다. 현재 채팅 surface를 바꾸지 않고도 런타임 상태를 재사용하거나 교체할 수 있습니다.

### thread 바인딩 세션

채널 adapter에서 thread 바인딩이 활성화되어 있으면 ACP 세션을 thread에 바인딩할 수 있습니다.

- OpenClaw는 thread를 대상 ACP 세션에 바인딩합니다.
- 해당 thread의 후속 메시지는 바인딩된 ACP 세션으로 라우팅됩니다.
- ACP 출력은 같은 thread로 다시 전달됩니다.
- 초점 해제/종료/보관/유휴 시간 초과 또는 최대 기간 만료 시 바인딩이 제거됩니다.

thread 바인딩 지원은 adapter별입니다. 활성 채널 adapter가 thread 바인딩을 지원하지 않으면 OpenClaw는 명확한 unsupported/unavailable 메시지를 반환합니다.

thread 바인딩 ACP에 필요한 feature flag:

- `acp.enabled=true`
- `acp.dispatch.enabled`는 기본적으로 켜져 있음 (`false`로 설정하면 ACP dispatch를 일시 중지)
- 채널 adapter ACP thread-spawn 플래그 활성화(adapter별)
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### thread를 지원하는 채널

- session/thread 바인딩 capability를 노출하는 모든 채널 adapter
- 현재 내장 지원:
  - Discord thread/channel
  - Telegram topic(그룹/슈퍼그룹의 forum topic 및 DM topic)
- 플러그인 채널도 동일한 바인딩 인터페이스를 통해 지원을 추가할 수 있습니다.

## 채널별 설정

비일시적 워크플로에는 최상위 `bindings[]` entry에 지속적인 ACP 바인딩을 구성하세요.

### 바인딩 모델

- `bindings[].type="acp"`는 지속적인 ACP conversation 바인딩을 표시합니다.
- `bindings[].match`는 대상 conversation을 식별합니다.
  - Discord 채널 또는 thread: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Telegram forum topic: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
  - BlueBubbles DM/그룹 채팅: `match.channel="bluebubbles"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`  
    안정적인 그룹 바인딩에는 `chat_id:*` 또는 `chat_identifier:*`를 우선하세요.
  - iMessage DM/그룹 채팅: `match.channel="imessage"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`  
    안정적인 그룹 바인딩에는 `chat_id:*`를 우선하세요.
- `bindings[].agentId`는 소유 OpenClaw agent id입니다.
- 선택적 ACP override는 `bindings[].acp` 아래에 둡니다.
  - `mode` (`persistent` 또는 `oneshot`)
  - `label`
  - `cwd`
  - `backend`

### agent별 런타임 기본값

agent별로 ACP 기본값을 한 번만 정의하려면 `agents.list[].runtime`을 사용하세요.

- `agents.list[].runtime.type="acp"`
- `agents.list[].runtime.acp.agent` (harness id, 예: `codex` 또는 `claude`)
- `agents.list[].runtime.acp.backend`
- `agents.list[].runtime.acp.mode`
- `agents.list[].runtime.acp.cwd`

ACP 바인딩 세션의 override 우선순위:

1. `bindings[].acp.*`
2. `agents.list[].runtime.acp.*`
3. 전역 ACP 기본값(예: `acp.backend`)

예시:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
      {
        id: "claude",
        runtime: {
          type: "acp",
          acp: { agent: "claude", backend: "acpx", mode: "persistent" },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
    {
      type: "acp",
      agentId: "claude",
      match: {
        channel: "telegram",
        accountId: "default",
        peer: { kind: "group", id: "-1001234567890:topic:42" },
      },
      acp: { cwd: "/workspace/repo-b" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "discord", accountId: "default" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "telegram", accountId: "default" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": { requireMention: false },
          },
        },
      },
    },
    telegram: {
      groups: {
        "-1001234567890": {
          topics: { "42": { requireMention: false } },
        },
      },
    },
  },
}
```

동작:

- OpenClaw는 사용 전에 설정된 ACP 세션이 존재하도록 보장합니다.
- 해당 채널 또는 topic의 메시지는 설정된 ACP 세션으로 라우팅됩니다.
- 바인딩된 conversation에서 `/new`와 `/reset`은 같은 ACP session key를 제자리에서 재설정합니다.
- 일시적 런타임 바인딩(예: thread-focus 흐름으로 생성된 바인딩)은 존재할 경우 계속 적용됩니다.
- 명시적 `cwd` 없이 cross-agent ACP spawn을 할 경우 OpenClaw는 agent config에서 대상 agent workspace를 상속합니다.
- 상속된 workspace 경로가 없으면 백엔드 기본 cwd로 fallback하고, 실제 접근 실패는 spawn 오류로 표시됩니다.

## ACP 세션 시작(인터페이스)

### `sessions_spawn`에서

agent turn 또는 tool 호출에서 ACP 세션을 시작하려면 `runtime: "acp"`를 사용하세요.

```json
{
  "task": "Open the repo and summarize failing tests",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

참고:

- `runtime`의 기본값은 `subagent`이므로 ACP 세션에는 `runtime: "acp"`를 명시적으로 설정하세요.
- `agentId`를 생략하면 설정된 경우 OpenClaw는 `acp.defaultAgent`를 사용합니다.
- 지속적인 바인딩 conversation을 유지하려면 `mode: "session"`에 `thread: true`가 필요합니다.

인터페이스 세부사항:

- `task` (필수): ACP 세션에 전송되는 초기 프롬프트
- `runtime` (ACP에 필수): 반드시 `"acp"`여야 함
- `agentId` (선택 사항): ACP 대상 harness id. 설정된 경우 `acp.defaultAgent`로 fallback
- `thread` (선택 사항, 기본값 `false`): 지원되는 경우 thread 바인딩 흐름 요청
- `mode` (선택 사항): `run` (일회성) 또는 `session` (지속형)
  - 기본값은 `run`
  - `thread: true`이고 mode를 생략하면 런타임 경로에 따라 OpenClaw가 지속형 동작을 기본값으로 사용할 수 있음
  - `mode: "session"`에는 `thread: true`가 필요함
- `cwd` (선택 사항): 요청된 런타임 작업 디렉터리(백엔드/런타임 정책에 따라 검증됨). 생략하면 ACP spawn은 설정된 경우 대상 agent workspace를 상속합니다. 상속된 경로가 없으면 백엔드 기본값으로 fallback하고, 실제 접근 오류는 그대로 반환됩니다.
- `label` (선택 사항): session/banner 텍스트에 사용되는 운영자 대상 label
- `resumeSessionId` (선택 사항): 새 세션을 만드는 대신 기존 ACP 세션 재개. agent는 `session/load`를 통해 conversation history를 재생합니다. `runtime: "acp"` 필요.
- `streamTo` (선택 사항): `"parent"`는 초기 ACP 실행 진행 요약을 system event로 요청자 세션에 다시 스트리밍함
  - 가능할 때 허용되는 응답에는 전체 relay history를 tail할 수 있는 session 범위 JSONL 로그(`<sessionId>.acp-stream.jsonl`)를 가리키는 `streamLogPath`가 포함됨

### 기존 세션 재개

새로 시작하는 대신 이전 ACP 세션을 계속하려면 `resumeSessionId`를 사용하세요. agent는 `session/load`를 통해 conversation history를 재생하므로 이전 맥락을 온전히 이어받습니다.

```json
{
  "task": "Continue where we left off — fix the remaining test failures",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

일반적인 사용 사례:

- 노트북에서 휴대폰으로 Codex 세션을 넘기기 — agent에게 중단한 지점부터 이어서 하라고 지시
- CLI에서 대화형으로 시작한 코딩 세션을 이제 agent를 통해 headless로 계속하기
- gateway 재시작 또는 유휴 시간 초과로 중단된 작업 이어가기

참고:

- `resumeSessionId`는 `runtime: "acp"`가 필요합니다 — sub-agent 런타임과 함께 사용하면 오류가 반환됩니다.
- `resumeSessionId`는 업스트림 ACP conversation history를 복원합니다. `thread`와 `mode`는 여전히 새로 만드는 OpenClaw 세션에 정상적으로 적용되므로, `mode: "session"`에는 여전히 `thread: true`가 필요합니다.
- 대상 agent는 `session/load`를 지원해야 합니다(Codex와 Claude Code는 지원).
- 세션 ID를 찾지 못하면 spawn은 명확한 오류와 함께 실패합니다 — 새 세션으로 조용히 fallback하지 않습니다.

### 운영자 smoke test

gateway 배포 후 ACP spawn이 단순히 unit test를 통과하는 수준이 아니라
실제로 엔드투엔드로 동작하는지 빠르게 라이브 점검하려면 이것을 사용하세요.

권장 게이트:

1. 대상 호스트에서 배포된 gateway 버전/커밋을 확인합니다.
2. 배포된 소스에
   `src/gateway/sessions-patch.ts`의 ACP lineage 허용(`subagent:* or acp:* sessions`)이 포함되어 있는지 확인합니다.
3. 라이브 agent에 임시 ACPX 브리지 세션을 엽니다(예:
   `jpclawhq`의 `razor(main)`).
4. 해당 agent에 다음으로 `sessions_spawn`을 호출하게 합니다.
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - task: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. agent가 다음을 보고하는지 확인합니다.
   - `accepted=yes`
   - 실제 `childSessionKey`
   - validator 오류 없음
6. 임시 ACPX 브리지 세션을 정리합니다.

라이브 agent에 보낼 예시 프롬프트:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

참고:

- thread에 바인딩된 지속형 ACP 세션을 의도적으로 테스트하는 경우가 아니라면
  이 smoke test는 `mode: "run"`으로 유지하세요.
- 기본 게이트에 `streamTo: "parent"`를 요구하지 마세요. 이 경로는
  요청자/세션 capability에 의존하며 별도의 통합 점검입니다.
- thread 바인딩 `mode: "session"` 테스트는 실제 Discord thread 또는 Telegram topic에서의
  두 번째, 더 풍부한 통합 단계로 취급하세요.

## 샌드박스 호환성

현재 ACP 세션은 OpenClaw 샌드박스 내부가 아니라 호스트 런타임에서 실행됩니다.

현재 제한 사항:

- 요청자 세션이 샌드박스 상태면 ACP spawn은 `sessions_spawn({ runtime: "acp" })`와 `/acp spawn` 모두에서 차단됩니다.
  - 오류: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `runtime: "acp"`가 있는 `sessions_spawn`은 `sandbox: "require"`를 지원하지 않습니다.
  - 오류: `sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

샌드박스 강제 실행이 필요하면 `runtime: "subagent"`를 사용하세요.

### `/acp` command에서

채팅에서 명시적인 운영자 제어가 필요하면 `/acp spawn`을 사용하세요.

```text
/acp spawn codex --mode persistent --thread auto
/acp spawn codex --mode oneshot --thread off
/acp spawn codex --bind here
/acp spawn codex --thread here
```

주요 플래그:

- `--mode persistent|oneshot`
- `--bind here|off`
- `--thread auto|here|off`
- `--cwd <absolute-path>`
- `--label <name>`

[Slash Commands](/tools/slash-commands)를 참고하세요.

## 세션 대상 resolve

대부분의 `/acp` 동작은 선택적인 세션 대상(`session-key`, `session-id`, 또는 `session-label`)을 받습니다.

resolve 순서:

1. 명시적 대상 인수(또는 `/acp steer`의 `--session`)
   - 먼저 key 시도
   - 다음으로 UUID 형태 session id 시도
   - 다음으로 label 시도
2. 현재 thread 바인딩(이 conversation/thread가 ACP 세션에 바인딩된 경우)
3. 현재 요청자 세션 fallback

현재 conversation 바인딩과 thread 바인딩은 모두 2단계에 참여합니다.

대상이 resolve되지 않으면 OpenClaw는 명확한 오류를 반환합니다(`Unable to resolve session target: ...`).

## Spawn 바인딩 모드

`/acp spawn`은 `--bind here|off`를 지원합니다.

| Mode   | 동작                                                              |
| ------ | ----------------------------------------------------------------- |
| `here` | 현재 활성 conversation을 제자리에서 바인딩하며, 활성 상태가 없으면 실패합니다. |
| `off`  | 현재 conversation 바인딩을 만들지 않습니다.                       |

참고:

- `--bind here`는 "이 채널 또는 채팅을 Codex 기반으로 만들기"에 가장 단순한 운영자 경로입니다.
- `--bind here`는 자식 thread를 만들지 않습니다.
- `--bind here`는 현재 conversation 바인딩 지원을 노출하는 채널에서만 사용할 수 있습니다.
- `--bind`와 `--thread`는 같은 `/acp spawn` 호출에서 함께 사용할 수 없습니다.

## Spawn thread 모드

`/acp spawn`은 `--thread auto|here|off`를 지원합니다.

| Mode   | 동작                                                                                              |
| ------ | ------------------------------------------------------------------------------------------------- |
| `auto` | 활성 thread 안에서는 해당 thread를 바인딩합니다. thread 밖에서는 지원되는 경우 자식 thread를 만들고 바인딩합니다. |
| `here` | 현재 활성 thread를 요구하며, thread 안이 아니면 실패합니다.                                      |
| `off`  | 바인딩 없음. 세션은 바인딩되지 않은 상태로 시작됩니다.                                            |

참고:

- thread 바인딩이 아닌 surface에서는 기본 동작이 사실상 `off`입니다.
- thread 바인딩 spawn에는 채널 정책 지원이 필요합니다.
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- 자식 thread를 만들지 않고 현재 conversation을 고정하려면 `--bind here`를 사용하세요.

## ACP 제어

사용 가능한 command 계열:

- `/acp spawn`
- `/acp cancel`
- `/acp steer`
- `/acp close`
- `/acp status`
- `/acp set-mode`
- `/acp set`
- `/acp cwd`
- `/acp permissions`
- `/acp timeout`
- `/acp model`
- `/acp reset-options`
- `/acp sessions`
- `/acp doctor`
- `/acp install`

`/acp status`는 적용된 런타임 옵션과, 가능할 경우 런타임 수준 및 백엔드 수준 세션 식별자를 모두 표시합니다.

일부 제어는 백엔드 capability에 따라 달라집니다. 백엔드가 제어를 지원하지 않으면 OpenClaw는 명확한 unsupported-control 오류를 반환합니다.

## ACP command cookbook

| Command              | 수행 내용                                                  | 예시                                                          |
| -------------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| `/acp spawn`         | ACP 세션 생성; 선택적으로 현재 바인딩 또는 thread 바인딩.  | `/acp spawn codex --bind here --cwd /repo`                    |
| `/acp cancel`        | 대상 세션의 진행 중 turn 취소.                             | `/acp cancel agent:codex:acp:<uuid>`                          |
| `/acp steer`         | 실행 중 세션에 steer 지시 전송.                            | `/acp steer --session support inbox prioritize failing tests` |
| `/acp close`         | 세션 종료 및 thread 대상 바인딩 해제.                      | `/acp close`                                                  |
| `/acp status`        | 백엔드, 모드, 상태, 런타임 옵션, capability 표시.          | `/acp status`                                                 |
| `/acp set-mode`      | 대상 세션의 런타임 모드 설정.                              | `/acp set-mode plan`                                          |
| `/acp set`           | 일반 런타임 config 옵션 쓰기.                              | `/acp set model openai/gpt-5.4`                               |
| `/acp cwd`           | 런타임 작업 디렉터리 override 설정.                        | `/acp cwd /Users/user/Projects/repo`                          |
| `/acp permissions`   | 승인 정책 profile 설정.                                    | `/acp permissions strict`                                     |
| `/acp timeout`       | 런타임 시간 초과 설정(초).                                 | `/acp timeout 120`                                            |
| `/acp model`         | 런타임 모델 override 설정.                                 | `/acp model anthropic/claude-opus-4-6`                        |
| `/acp reset-options` | 세션 런타임 옵션 override 제거.                            | `/acp reset-options`                                          |
| `/acp sessions`      | 저장소에서 최근 ACP 세션 나열.                             | `/acp sessions`                                               |
| `/acp doctor`        | 백엔드 상태, capability, 실행 가능한 수정 방안.            | `/acp doctor`                                                 |
| `/acp install`       | 결정적인 install 및 활성화 단계 출력.                      | `/acp install`                                                |

`/acp sessions`는 현재 바인딩되었거나 요청자 세션의 저장소를 읽습니다. `session-key`, `session-id`, `session-label` 토큰을 받는 command는 커스텀 agent별 `session.store` 루트를 포함해 gateway 세션 discovery를 통해 대상을 resolve합니다.

## 런타임 옵션 매핑

`/acp`에는 편의 command와 일반 setter가 있습니다.

동등한 작업:

- `/acp model <id>`는 런타임 config key `model`에 매핑됩니다.
- `/acp permissions <profile>`은 런타임 config key `approval_policy`에 매핑됩니다.
- `/acp timeout <seconds>`는 런타임 config key `timeout`에 매핑됩니다.
- `/acp cwd <path>`는 런타임 cwd override를 직접 업데이트합니다.
- `/acp set <key> <value>`는 일반 경로입니다.
  - 특별 처리: `key=cwd`는 cwd override 경로를 사용합니다.
- `/acp reset-options`는 대상 세션의 모든 런타임 override를 지웁니다.

## acpx harness 지원(현재)

현재 acpx 내장 harness 별칭:

- `claude`
- `codex`
- `copilot`
- `cursor` (Cursor CLI: `cursor-agent acp`)
- `droid`
- `gemini`
- `iflow`
- `kilocode`
- `kimi`
- `kiro`
- `openclaw`
- `opencode`
- `pi`
- `qwen`

OpenClaw가 acpx 백엔드를 사용할 때는, 로컬 acpx config에 커스텀 agent 별칭이 정의되어 있지 않다면 `agentId`에 이 값을 우선 사용하세요.
로컬 Cursor 설치가 여전히 ACP를 `agent acp`로 노출한다면, 내장 기본값을 변경하는 대신 acpx config에서 `cursor` agent command를 override하세요.

직접 acpx CLI 사용은 `--agent <command>`를 통해 임의의 adapter도 대상으로 지정할 수 있지만, 이 원시 탈출구는 acpx CLI 기능일 뿐이며 일반적인 OpenClaw `agentId` 경로는 아닙니다.

## 필수 config

core ACP 기준선:

```json5
{
  acp: {
    enabled: true,
    // 선택 사항. 기본값은 true이며, /acp 제어는 유지한 채 ACP dispatch를 일시 중지하려면 false로 설정합니다.
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: [
      "claude",
      "codex",
      "copilot",
      "cursor",
      "droid",
      "gemini",
      "iflow",
      "kilocode",
      "kimi",
      "kiro",
      "openclaw",
      "opencode",
      "pi",
      "qwen",
    ],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

thread 바인딩 config는 채널 adapter별입니다. Discord 예시:

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        spawnAcpSessions: true,
      },
    },
  },
}
```

thread에 바인딩된 ACP spawn이 동작하지 않는다면 먼저 adapter feature flag를 확인하세요.

- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

현재 conversation 바인딩은 자식 thread 생성을 필요로 하지 않습니다. 활성 conversation 컨텍스트와 ACP conversation 바인딩을 노출하는 채널 adapter가 필요합니다.

[Configuration Reference](/ko/gateway/configuration-reference)를 참고하세요.

## acpx 백엔드를 위한 플러그인 설정

새 설치에는 번들 `acpx` 런타임 플러그인이 기본으로 활성화되어 포함되므로,
대체로 수동 플러그인 install 단계 없이 ACP가 동작합니다.

다음부터 시작하세요.

```text
/acp doctor
```

`acpx`를 비활성화했거나, `plugins.allow` / `plugins.deny`로 거부했거나,
로컬 개발 checkout으로 전환하려면 명시적 플러그인 경로를 사용하세요.

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

개발 중 로컬 workspace install:

```bash
openclaw plugins install ./path/to/local/acpx-plugin
```

그런 다음 백엔드 상태를 확인하세요.

```text
/acp doctor
```

### acpx command 및 버전 config

기본적으로 번들 acpx 백엔드 플러그인(`acpx`)은 플러그인 로컬에 고정된 바이너리를 사용합니다.

1. command는 ACPX 플러그인 패키지 내부의 플러그인 로컬 `node_modules/.bin/acpx`를 기본값으로 사용합니다.
2. 예상 버전은 extension pin을 기본값으로 사용합니다.
3. 시작 시 ACP 백엔드를 즉시 not-ready 상태로 등록합니다.
4. 백그라운드 ensure 작업이 `acpx --version`을 검증합니다.
5. 플러그인 로컬 바이너리가 없거나 버전이 맞지 않으면 다음을 실행합니다.
   `npm install --omit=dev --no-save acpx@<pinned>` 후 다시 검증합니다.

플러그인 config에서 command/version을 override할 수 있습니다.

```json
{
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "command": "../acpx/dist/cli.js",
          "expectedVersion": "any"
        }
      }
    }
  }
}
```

참고:

- `command`는 절대 경로, 상대 경로, 또는 command 이름(`acpx`)을 받을 수 있습니다.
- 상대 경로는 OpenClaw workspace 디렉터리 기준으로 resolve됩니다.
- `expectedVersion: "any"`는 엄격한 버전 일치를 비활성화합니다.
- `command`가 커스텀 바이너리/경로를 가리키면 플러그인 로컬 자동 install은 비활성화됩니다.
- 백엔드 상태 확인이 실행되는 동안에도 OpenClaw 시작은 non-blocking 상태를 유지합니다.

[플러그인](/tools/plugin)을 참고하세요.

### 자동 의존성 install

`npm install -g openclaw`로 OpenClaw를 전역 설치하면, acpx
런타임 의존성(플랫폼별 바이너리)은 postinstall hook을 통해 자동으로 설치됩니다.
자동 install이 실패해도 gateway는 정상적으로 시작되며,
누락된 의존성은 `openclaw acp doctor`를 통해 보고됩니다.

### 플러그인 tool MCP 브리지

기본적으로 ACPX 세션은 OpenClaw 플러그인 등록 tool을 ACP harness에 **노출하지 않습니다**.

Codex 또는 Claude Code 같은 ACP agent가 memory recall/store 같은
설치된 OpenClaw 플러그인 tool을 호출하게 하려면, 전용 브리지를 활성화하세요.

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

이 설정이 하는 일:

- ACPX 세션 bootstrap에 `openclaw-plugin-tools`라는 내장 MCP 서버를 주입합니다.
- 설치되고 활성화된 OpenClaw 플러그인이 이미 등록한 플러그인 tool을 노출합니다.
- 이 기능을 명시적이고 기본 비활성 상태로 유지합니다.

보안 및 신뢰 참고 사항:

- 이 설정은 ACP harness tool surface를 확장합니다.
- ACP agent는 gateway에서 이미 활성화된 플러그인 tool에만 접근할 수 있습니다.
- 이를 해당 플러그인이 OpenClaw 자체에서 실행되도록 허용하는 것과 같은 신뢰 경계로 취급하세요.
- 활성화하기 전에 설치된 플러그인을 검토하세요.

커스텀 `mcpServers`는 이전처럼 계속 동작합니다. 내장 plugin-tools 브리지는
일반 MCP 서버 config를 대체하는 것이 아니라, 추가적인 선택적 편의 기능입니다.

## 권한 config

ACP 세션은 비대화형으로 실행됩니다 — 파일 쓰기 및 shell 실행 권한 프롬프트를 승인하거나 거부할 TTY가 없습니다. acpx 플러그인은 권한 처리 방식을 제어하는 두 개의 config key를 제공합니다.

이 ACPX harness 권한은 OpenClaw exec 승인과 별개이며, Claude CLI `--permission-mode bypassPermissions` 같은 CLI 백엔드 vendor 우회 플래그와도 별개입니다. ACPX `approve-all`은 ACP 세션용 harness 수준의 브레이크글라스 스위치입니다.

### `permissionMode`

harness agent가 프롬프트 없이 수행할 수 있는 작업을 제어합니다.

| Value           | 동작                                                          |
| --------------- | ------------------------------------------------------------- |
| `approve-all`   | 모든 파일 쓰기와 shell command를 자동 승인합니다.             |
| `approve-reads` | 읽기만 자동 승인하고, 쓰기와 exec는 프롬프트가 필요합니다.    |
| `deny-all`      | 모든 권한 프롬프트를 거부합니다.                              |

### `nonInteractivePermissions`

권한 프롬프트가 표시되어야 하지만 대화형 TTY를 사용할 수 없을 때(ACP 세션에서는 항상 해당) 어떻게 동작할지 제어합니다.

| Value  | 동작                                                             |
| ------ | ---------------------------------------------------------------- |
| `fail` | `AcpRuntimeError`와 함께 세션을 중단합니다. **(기본값)**         |
| `deny` | 권한을 조용히 거부하고 계속 진행합니다(점진적 기능 저하).         |

### Configuration

플러그인 config로 설정:

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

이 값을 변경한 뒤 gateway를 재시작하세요.

> **중요:** OpenClaw는 현재 기본값으로 `permissionMode=approve-reads`와 `nonInteractivePermissions=fail`을 사용합니다. 비대화형 ACP 세션에서는 권한 프롬프트를 발생시키는 모든 쓰기 또는 exec가 `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`와 함께 실패할 수 있습니다.
>
> 권한을 제한해야 한다면, 세션이 크래시하지 않고 점진적으로 기능이 저하되도록 `nonInteractivePermissions`를 `deny`로 설정하세요.

## 문제 해결

| 증상                                                                        | 가능한 원인                                                                    | 해결 방법                                                                                                                                                          |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ACP runtime backend is not configured`                                     | 백엔드 플러그인이 없거나 비활성화됨.                                           | 백엔드 플러그인을 설치하고 활성화한 다음 `/acp doctor`를 실행하세요.                                                                                              |
| `ACP is disabled by policy (acp.enabled=false)`                             | ACP가 전역적으로 비활성화됨.                                                   | `acp.enabled=true`로 설정하세요.                                                                                                                                   |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)`           | 일반 thread 메시지에서의 dispatch가 비활성화됨.                               | `acp.dispatch.enabled=true`로 설정하세요.                                                                                                                          |
| `ACP agent "<id>" is not allowed by policy`                                 | agent가 allowlist에 없음.                                                      | 허용된 `agentId`를 사용하거나 `acp.allowedAgents`를 업데이트하세요.                                                                                                |
| `Unable to resolve session target: ...`                                     | 잘못된 key/id/label 토큰.                                                      | `/acp sessions`를 실행하고 정확한 key/label을 복사한 뒤 다시 시도하세요.                                                                                           |
| `--bind here requires running /acp spawn inside an active ... conversation` | `--bind here`가 활성화된 바인딩 가능 conversation 없이 사용됨.                 | 대상 chat/channel로 이동해 다시 시도하거나 바인딩 없이 spawn을 사용하세요.                                                                                         |
| `Conversation bindings are unavailable for <channel>.`                      | adapter에 현재 conversation ACP 바인딩 capability가 없음.                      | 지원되는 경우 `/acp spawn ... --thread ...`를 사용하거나, 최상위 `bindings[]`를 구성하거나, 지원되는 채널로 이동하세요.                                           |
| `--thread here requires running /acp spawn inside an active ... thread`     | `--thread here`가 thread 컨텍스트 밖에서 사용됨.                               | 대상 thread로 이동하거나 `--thread auto`/`off`를 사용하세요.                                                                                                       |
| `Only <user-id> can rebind this channel/conversation/thread.`               | 다른 사용자가 활성 바인딩 대상을 소유함.                                       | 소유자로 다시 바인딩하거나 다른 conversation 또는 thread를 사용하세요.                                                                                             |
| `Thread bindings are unavailable for <channel>.`                            | adapter에 thread 바인딩 capability가 없음.                                     | `--thread off`를 사용하거나 지원되는 adapter/channel로 이동하세요.                                                                                                 |
| `Sandboxed sessions cannot spawn ACP sessions ...`                          | ACP 런타임은 호스트 측에서 실행되며 요청자 세션은 샌드박스 상태임.             | 샌드박스 세션에서는 `runtime="subagent"`를 사용하거나, 샌드박스가 아닌 세션에서 ACP spawn을 실행하세요.                                                           |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...`     | ACP 런타임에 `sandbox="require"`가 요청됨.                                     | 필수 샌드박싱이 필요하면 `runtime="subagent"`를 사용하거나, 샌드박스가 아닌 세션에서 `sandbox="inherit"`와 함께 ACP를 사용하세요.                                 |
| 바인딩된 세션에 ACP 메타데이터가 없음                                       | 오래되었거나 삭제된 ACP 세션 메타데이터.                                       | `/acp spawn`으로 다시 생성한 다음 thread를 다시 바인딩/포커스하세요.                                                                                               |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`    | `permissionMode`가 비대화형 ACP 세션에서 쓰기/exec를 차단함.                   | `plugins.entries.acpx.config.permissionMode`를 `approve-all`로 설정하고 gateway를 재시작하세요. [권한 config](#permission-configuration)를 참고하세요.            |
| 출력이 거의 없이 ACP 세션이 초기에 실패함                                   | 권한 프롬프트가 `permissionMode`/`nonInteractivePermissions`에 의해 차단됨.    | gateway 로그에서 `AcpRuntimeError`를 확인하세요. 전체 권한이 필요하면 `permissionMode=approve-all`, 점진적 기능 저하가 필요하면 `nonInteractivePermissions=deny`로 설정하세요. |
| 작업 완료 후 ACP 세션이 무기한 멈춘 상태로 남음                             | harness 프로세스는 끝났지만 ACP 세션이 완료를 보고하지 않음.                   | `ps aux \| grep acpx`로 모니터링하고, 오래된 프로세스를 수동으로 종료하세요.                                                                                       |
