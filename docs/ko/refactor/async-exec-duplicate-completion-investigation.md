---
x-i18n:
    generated_at: "2026-04-16T06:00:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 95e56c5411204363676f002059c942201503e2359515d1a4b409882cc2e04920
    source_path: refactor/async-exec-duplicate-completion-investigation.md
    workflow: 15
---

# 비동기 Exec 중복 완료 조사

## 범위

- 세션: `agent:main:telegram:group:-1003774691294:topic:1`
- 증상: 동일한 비동기 exec 완료가 세션/실행 `keen-nexus`에 대해 LCM에 사용자 턴으로 두 번 기록되었습니다.
- 목표: 이것이 중복 세션 주입인지, 아니면 단순한 아웃바운드 전달 재시도인지 식별합니다.

## 결론

가장 가능성이 높은 것은 순수한 아웃바운드 전달 재시도가 아니라 **중복 세션 주입**입니다.

게이트웨이 측에서 가장 강한 결함 지점은 **node exec 완료 경로**입니다:

1. node 측 exec 종료가 전체 `runId`와 함께 `exec.finished`를 내보냅니다.
2. Gateway의 `server-node-events`가 이를 시스템 이벤트로 변환하고 Heartbeat를 요청합니다.
3. Heartbeat 실행이 비워진 시스템 이벤트 블록을 에이전트 프롬프트에 주입합니다.
4. 임베디드 러너가 그 프롬프트를 세션 transcript의 새 사용자 턴으로 영속화합니다.

어떤 이유로든 동일한 `runId`에 대해 같은 `exec.finished`가 Gateway에 두 번 도달하면(재생, 재연결 중복, 업스트림 재전송, 중복된 producer), OpenClaw는 현재 이 경로에서 `runId`/`contextKey`를 키로 하는 **멱등성 검사**가 없습니다. 두 번째 복사본은 같은 내용의 두 번째 사용자 메시지가 됩니다.

## 정확한 코드 경로

### 1. Producer: node exec 완료 이벤트

- `src/node-host/invoke.ts:340-360`
  - `sendExecFinishedEvent(...)`가 이벤트 `exec.finished`와 함께 `node.event`를 내보냅니다.
  - payload에는 `sessionKey`와 전체 `runId`가 포함됩니다.

### 2. Gateway 이벤트 수집

- `src/gateway/server-node-events.ts:574-640`
  - `exec.finished`를 처리합니다.
  - 다음 텍스트를 구성합니다:
    - `Exec finished (node=..., id=<runId>, code ...)`
  - 이를 다음으로 큐에 넣습니다:
    - `enqueueSystemEvent(text, { sessionKey, contextKey: runId ? \`exec:${runId}\` : "exec", trusted: false })`
  - 그리고 즉시 wake를 요청합니다:
    - `requestHeartbeatNow(scopedHeartbeatWakeOptions(sessionKey, { reason: "exec-event" }))`

### 3. 시스템 이벤트 중복 제거 취약점

- `src/infra/system-events.ts:90-115`
  - `enqueueSystemEvent(...)`는 **연속된 동일 텍스트**만 억제합니다:
    - `if (entry.lastText === cleaned) return false`
  - `contextKey`를 저장하지만, 멱등성을 위해 `contextKey`를 사용하지는 않습니다.
  - drain 이후에는 중복 억제가 초기화됩니다.

즉, 동일한 `runId`를 가진 재생된 `exec.finished`는 나중에 다시 허용될 수 있으며, 코드에는 이미 안정적인 멱등성 후보(`exec:<runId>`)가 있었음에도 그렇습니다.

### 4. Wake 처리가 주된 중복 원인은 아님

- `src/infra/heartbeat-wake.ts:79-117`
  - wake는 `(agentId, sessionKey)` 기준으로 병합됩니다.
  - 동일한 대상에 대한 중복 wake 요청은 하나의 대기 중 wake 항목으로 합쳐집니다.

따라서 **중복 wake 처리만으로는** 중복 이벤트 수집보다 설명력이 약합니다.

### 5. Heartbeat가 이벤트를 소비해 프롬프트 입력으로 변환

- `src/infra/heartbeat-runner.ts:535-574`
  - preflight가 대기 중인 시스템 이벤트를 미리 보고 exec-event 실행을 분류합니다.
- `src/auto-reply/reply/session-system-events.ts:86-90`
  - `drainFormattedSystemEvents(...)`가 세션의 큐를 비웁니다.
- `src/auto-reply/reply/get-reply-run.ts:400-427`
  - 비워진 시스템 이벤트 블록이 에이전트 프롬프트 본문 앞에 prepend됩니다.

### 6. Transcript 주입 지점

- `src/agents/pi-embedded-runner/run/attempt.ts:2000-2017`
  - `activeSession.prompt(effectivePrompt)`가 전체 프롬프트를 임베디드 PI 세션에 제출합니다.
  - 완료 기반 프롬프트가 영속화된 사용자 턴이 되는 지점이 바로 여기입니다.

따라서 동일한 시스템 이벤트가 두 번 다시 프롬프트로 구성되면, LCM에서 중복 사용자 메시지가 생기는 것은 예상된 결과입니다.

## 단순 아웃바운드 전달 재시도 가능성이 더 낮은 이유

Heartbeat runner에는 실제 아웃바운드 실패 경로가 있습니다:

- `src/infra/heartbeat-runner.ts:1194-1242`
  - 먼저 응답이 생성됩니다.
  - 그 뒤에 `deliverOutboundPayloads(...)`를 통해 아웃바운드 전달이 수행됩니다.
  - 여기서 실패하면 `{ status: "failed" }`를 반환합니다.

하지만 동일한 시스템 이벤트 큐 항목에 대해 이것만으로는 **중복 사용자 턴**을 설명하기에 충분하지 않습니다:

- `src/auto-reply/reply/session-system-events.ts:86-90`
  - 시스템 이벤트 큐는 아웃바운드 전달 전에 이미 비워집니다.

따라서 채널 전송 재시도만으로는 동일한 큐 이벤트가 다시 생성되지 않습니다. 외부 전달 누락/실패는 설명할 수 있지만, 동일한 세션 사용자 메시지가 두 번째로 생기는 현상 자체를 단독으로 설명하지는 못합니다.

## 2차적이며 신뢰도는 더 낮은 가능성

에이전트 runner에는 전체 실행 재시도 루프가 있습니다:

- `src/auto-reply/reply/agent-runner-execution.ts:741-1473`
  - 특정 일시적 실패는 전체 실행을 재시도하고 같은 `commandBody`를 다시 제출할 수 있습니다.

이 경우 재시도 조건이 트리거되기 전에 프롬프트가 이미 append되었다면, **동일한 응답 실행 내에서** 영속화된 사용자 프롬프트가 중복될 수 있습니다.

제가 이것을 중복 `exec.finished` 수집보다 낮게 평가하는 이유는 다음과 같습니다:

- 관측된 간격이 약 51초였는데, 이는 프로세스 내부 재시도보다는 두 번째 wake/turn에 더 가까워 보입니다.
- 보고서에는 반복된 메시지 전송 실패도 언급되어 있는데, 이는 즉각적인 모델/런타임 재시도보다는 분리된 나중 턴을 더 시사합니다.

## 근본 원인 가설

가장 신뢰도가 높은 가설:

- `keen-nexus` 완료는 **node exec 이벤트 경로**를 통해 들어왔습니다.
- 동일한 `exec.finished`가 `server-node-events`에 두 번 전달되었습니다.
- Gateway는 `enqueueSystemEvent(...)`가 `contextKey` / `runId` 기준으로 중복 제거를 하지 않기 때문에 둘 다 수용했습니다.
- 수용된 각 이벤트가 Heartbeat를 트리거했고, PI transcript에 사용자 턴으로 주입되었습니다.

## 제안하는 작고 정밀한 수정

수정이 필요하다면, 가장 작으면서 효과가 큰 변경은 다음과 같습니다:

- 적어도 정확히 동일한 `(sessionKey, contextKey, text)` 반복에 대해서는 짧은 기간 동안 exec/시스템 이벤트 멱등성이 `contextKey`를 존중하도록 합니다.
- 또는 `(sessionKey, runId, event kind)`를 키로 하는 `exec.finished` 전용 중복 제거를 `server-node-events`에 추가합니다.

이렇게 하면 재생된 `exec.finished` 중복이 세션 턴이 되기 전에 직접 차단됩니다.
