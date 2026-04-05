---
read_when:
    - Heartbeat 주기나 메시징을 조정할 때
    - 예약된 작업에 heartbeat와 cron 중 무엇을 사용할지 결정할 때
summary: Heartbeat 폴링 메시지 및 알림 규칙
title: Heartbeat
x-i18n:
    generated_at: "2026-04-05T12:42:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: f417b0d4453bed9022144d364521a59dec919d44cca8f00f0def005cd38b146f
    source_path: gateway/heartbeat.md
    workflow: 15
---

# Heartbeat (Gateway)

> **Heartbeat vs Cron?** 각각을 언제 사용해야 하는지에 대한 안내는 [Automation & Tasks](/automation)를 참조하세요.

Heartbeat는 **주기적인 에이전트 턴**을 메인 세션에서 실행하여 모델이
주의가 필요한 내용을 과도한 알림 없이 표시할 수 있게 합니다.

Heartbeat는 예약된 메인 세션 턴입니다 — [background task](/automation/tasks) 기록을 생성하지 않습니다.
작업 기록은 분리된 작업(ACP 실행, 하위 에이전트, 격리된 cron 작업)을 위한 것입니다.

문제 해결: [Scheduled Tasks](/automation/cron-jobs#troubleshooting)

## 빠른 시작(초보자)

1. Heartbeat를 활성화된 상태로 둡니다(기본값은 `30m`, Anthropic OAuth/token 인증일 때는 `1h`, Claude CLI 재사용 포함) 또는 원하는 주기를 설정합니다.
2. 에이전트 워크스페이스에 작은 `HEARTBEAT.md` 체크리스트 또는 `tasks:` 블록을 만듭니다(선택 사항이지만 권장).
3. Heartbeat 메시지를 어디로 보낼지 결정합니다(기본값은 `target: "none"`이며, 마지막 연락처로 라우팅하려면 `target: "last"`를 설정).
4. 선택 사항: 투명성을 위해 heartbeat reasoning 전달을 활성화합니다.
5. 선택 사항: heartbeat 실행에 `HEARTBEAT.md`만 필요하다면 경량 부트스트랩 컨텍스트를 사용합니다.
6. 선택 사항: 각 heartbeat마다 전체 대화 기록을 보내지 않도록 격리된 세션을 활성화합니다.
7. 선택 사항: heartbeat를 활성 시간대(현지 시간)로 제한합니다.

예시 구성:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // explicit delivery to last contact (default is "none")
        directPolicy: "allow", // default: allow direct/DM targets; set "block" to suppress
        lightContext: true, // optional: only inject HEARTBEAT.md from bootstrap files
        isolatedSession: true, // optional: fresh session each run (no conversation history)
        // activeHours: { start: "08:00", end: "24:00" },
        // includeReasoning: true, // optional: send separate `Reasoning:` message too
      },
    },
  },
}
```

## 기본값

- 간격: `30m`(또는 Anthropic OAuth/token 인증이 감지된 인증 모드일 때는 `1h`, Claude CLI 재사용 포함). `agents.defaults.heartbeat.every` 또는 에이전트별 `agents.list[].heartbeat.every`를 설정하세요. 비활성화하려면 `0m`을 사용합니다.
- 프롬프트 본문(`agents.defaults.heartbeat.prompt`로 구성 가능):
  `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`
- Heartbeat 프롬프트는 사용자 메시지로 **있는 그대로** 전송됩니다. 시스템
  프롬프트에는 “Heartbeat” 섹션이 포함되며, 실행은 내부적으로 플래그 처리됩니다.
- 활성 시간(`heartbeat.activeHours`)은 구성된 시간대에서 확인됩니다.
  창 바깥에서는 다음 창 내부 틱까지 heartbeat가 건너뛰어집니다.

## heartbeat 프롬프트의 목적

기본 프롬프트는 의도적으로 넓은 범위를 가집니다.

- **background task**: “Consider outstanding tasks”는 에이전트가
  후속 작업(받은편지함, 캘린더, 알림, 대기 중인 작업)을 검토하고 긴급한 내용을 표시하도록 유도합니다.
- **사람 확인**: “Checkup sometimes on your human during day time”는
  가벼운 “필요한 것 있나요?” 메시지를 가끔 보내도록 유도하지만, 구성된 현지 시간대를 사용하여 야간 스팸은 피합니다([/concepts/timezone](/concepts/timezone) 참조).

Heartbeat는 완료된 [background tasks](/automation/tasks)에 반응할 수 있지만, heartbeat 실행 자체는 작업 기록을 생성하지 않습니다.

heartbeat가 매우 구체적인 작업(예: “Gmail PubSub
상태 확인” 또는 “gateway 상태 확인”)을 하도록 하려면 `agents.defaults.heartbeat.prompt`(또는
`agents.list[].heartbeat.prompt`)를 사용자 지정 본문으로 설정하세요(있는 그대로 전송됨).

## 응답 계약

- 주의가 필요한 것이 없다면 **`HEARTBEAT_OK`**로 응답합니다.
- Heartbeat 실행 중 OpenClaw는 `HEARTBEAT_OK`가 응답의 **시작 또는 끝**에 나타나면 이를 ack로 처리합니다. 이 토큰은 제거되며, 남은 내용이 **≤ `ackMaxChars`**(기본값: 300)인 경우 응답은 버려집니다.
- `HEARTBEAT_OK`가 응답의 **중간**에 나타나면 특별하게 취급되지 않습니다.
- 경고의 경우 **`HEARTBEAT_OK`를 포함하지 말고** 경고 텍스트만 반환합니다.

Heartbeat 외부에서는 메시지 시작/끝의 의도치 않은 `HEARTBEAT_OK`가 제거되고 로그에 기록됩니다. 메시지가 `HEARTBEAT_OK`뿐이면 버려집니다.

## 구성

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // default: 30m (0m disables)
        model: "anthropic/claude-opus-4-6",
        includeReasoning: false, // default: false (deliver separate Reasoning: message when available)
        lightContext: false, // default: false; true keeps only HEARTBEAT.md from workspace bootstrap files
        isolatedSession: false, // default: false; true runs each heartbeat in a fresh session (no conversation history)
        target: "last", // default: none | options: last | none | <channel id> (core or plugin, e.g. "bluebubbles")
        to: "+15551234567", // optional channel-specific override
        accountId: "ops-bot", // optional multi-account channel id
        prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        ackMaxChars: 300, // max chars allowed after HEARTBEAT_OK
      },
    },
  },
}
```

### 범위 및 우선순위

- `agents.defaults.heartbeat`는 전역 heartbeat 동작을 설정합니다.
- `agents.list[].heartbeat`는 그 위에 병합됩니다. 어떤 에이전트라도 `heartbeat` 블록을 가지면 **그 에이전트들만** heartbeat를 실행합니다.
- `channels.defaults.heartbeat`는 모든 채널에 대한 가시성 기본값을 설정합니다.
- `channels.<channel>.heartbeat`는 채널 기본값을 재정의합니다.
- `channels.<channel>.accounts.<id>.heartbeat`(멀티 계정 채널)는 채널별 설정을 재정의합니다.

### 에이전트별 heartbeat

어떤 `agents.list[]` 항목에라도 `heartbeat` 블록이 포함되면 **그 에이전트들만**
heartbeat를 실행합니다. 에이전트별 블록은 `agents.defaults.heartbeat`
위에 병합됩니다(즉, 공통 기본값을 한 번 설정하고 에이전트별로 재정의할 수 있습니다).

예시: 두 개의 에이전트 중 두 번째 에이전트만 heartbeat를 실행합니다.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // explicit delivery to last contact (default is "none")
      },
    },
    list: [
      { id: "main", default: true },
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "whatsapp",
          to: "+15551234567",
          prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        },
      },
    ],
  },
}
```

### 활성 시간 예시

특정 시간대의 업무 시간으로 heartbeat를 제한합니다:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // explicit delivery to last contact (default is "none")
        activeHours: {
          start: "09:00",
          end: "22:00",
          timezone: "America/New_York", // optional; uses your userTimezone if set, otherwise host tz
        },
      },
    },
  },
}
```

이 시간 창 밖에서는(동부 시간 기준 오전 9시 이전 또는 오후 10시 이후) heartbeat가 건너뛰어집니다. 창 안의 다음 예약 틱은 정상적으로 실행됩니다.

### 24/7 설정

Heartbeat를 하루 종일 실행하려면 다음 패턴 중 하나를 사용하세요:

- `activeHours`를 완전히 생략합니다(시간 창 제한 없음, 기본 동작).
- 하루 전체 창을 설정합니다: `activeHours: { start: "00:00", end: "24:00" }`.

같은 `start`와 `end` 시간을 설정하지 마세요(예: `08:00`에서 `08:00`).
이는 너비가 0인 창으로 처리되므로 heartbeat는 항상 건너뛰어집니다.

### 멀티 계정 예시

Telegram 같은 멀티 계정 채널에서 특정 계정을 대상으로 하려면 `accountId`를 사용하세요:

```json5
{
  agents: {
    list: [
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "telegram",
          to: "12345678:topic:42", // optional: route to a specific topic/thread
          accountId: "ops-bot",
        },
      },
    ],
  },
  channels: {
    telegram: {
      accounts: {
        "ops-bot": { botToken: "YOUR_TELEGRAM_BOT_TOKEN" },
      },
    },
  },
}
```

### 필드 참고

- `every`: heartbeat 간격(지속 시간 문자열, 기본 단위 = 분).
- `model`: heartbeat 실행용 선택적 모델 재정의(`provider/model`).
- `includeReasoning`: 활성화되면 가능한 경우 별도의 `Reasoning:` 메시지도 전달합니다(`/reasoning on`과 같은 형태).
- `lightContext`: true이면 heartbeat 실행은 경량 부트스트랩 컨텍스트를 사용하고 워크스페이스 부트스트랩 파일 중 `HEARTBEAT.md`만 유지합니다.
- `isolatedSession`: true이면 각 heartbeat는 이전 대화 기록이 없는 새 세션에서 실행됩니다. cron의 `sessionTarget: "isolated"`와 같은 격리 패턴을 사용합니다. heartbeat당 토큰 비용을 크게 줄입니다. 최대 절약을 위해 `lightContext: true`와 함께 사용하세요. 전달 라우팅은 여전히 메인 세션 컨텍스트를 사용합니다.
- `session`: heartbeat 실행용 선택적 세션 키.
  - `main`(기본값): 에이전트 메인 세션.
  - 명시적 세션 키(`openclaw sessions --json` 또는 [sessions CLI](/cli/sessions)에서 복사).
  - 세션 키 형식: [Sessions](/concepts/session) 및 [Groups](/channels/groups) 참조.
- `target`:
  - `last`: 마지막으로 사용한 외부 채널로 전달.
  - 명시적 채널: 구성된 모든 채널 또는 plugin id. 예: `discord`, `matrix`, `telegram`, `whatsapp`.
  - `none`(기본값): heartbeat는 실행하지만 외부로는 **전달하지 않음**.
- `directPolicy`: 직접/DM 전달 동작 제어:
  - `allow`(기본값): 직접/DM heartbeat 전달 허용.
  - `block`: 직접/DM 전달 억제(`reason=dm-blocked`).
- `to`: 선택적 수신자 재정의(채널별 ID. 예: WhatsApp의 E.164 또는 Telegram 채팅 ID). Telegram 토픽/스레드에는 `<chatId>:topic:<messageThreadId>`를 사용합니다.
- `accountId`: 멀티 계정 채널용 선택적 계정 ID. `target: "last"`일 때 계정 ID는 계정을 지원하는 경우 해석된 마지막 채널에 적용되고, 그렇지 않으면 무시됩니다. 계정 ID가 해석된 채널의 구성된 계정과 일치하지 않으면 전달은 건너뛰어집니다.
- `prompt`: 기본 프롬프트 본문 재정의(병합되지 않음).
- `ackMaxChars`: `HEARTBEAT_OK` 뒤에 허용되는 최대 문자 수.
- `suppressToolErrorWarnings`: true이면 heartbeat 실행 중 도구 오류 경고 페이로드를 억제합니다.
- `activeHours`: heartbeat 실행을 시간 창으로 제한합니다. `start`(HH:MM, 포함, 하루 시작은 `00:00`), `end`(HH:MM, 제외, 하루 끝에는 `24:00` 허용), 선택적 `timezone` 객체입니다.
  - 생략 또는 `"user"`: 설정되어 있으면 `agents.defaults.userTimezone`을 사용하고, 그렇지 않으면 호스트 시스템 시간대로 대체합니다.
  - `"local"`: 항상 호스트 시스템 시간대를 사용합니다.
  - 모든 IANA 식별자(예: `America/New_York`): 직접 사용하며, 잘못된 경우 위의 `"user"` 동작으로 대체합니다.
  - 활성 창을 위해 `start`와 `end`는 같아서는 안 됩니다. 같으면 너비 0(항상 창 밖)으로 처리됩니다.
  - 활성 창 밖에서는 다음 창 내부 틱까지 heartbeat가 건너뛰어집니다.

## 전달 동작

- Heartbeat는 기본적으로 에이전트의 메인 세션(`agent:<id>:<mainKey>`)에서 실행되며,
  `session.scope = "global"`이면 `global`에서 실행됩니다. 특정 채널 세션(Discord/WhatsApp 등)으로 재정의하려면 `session`을 설정하세요.
- `session`은 실행 컨텍스트에만 영향을 주며, 전달은 `target`과 `to`로 제어됩니다.
- 특정 채널/수신자에게 전달하려면 `target` + `to`를 설정합니다. `target: "last"`이면 해당 세션의 마지막 외부 채널을 사용합니다.
- Heartbeat 전달은 기본적으로 직접/DM 대상을 허용합니다. heartbeat 턴은 계속 실행하되 직접 대상 전송을 억제하려면 `directPolicy: "block"`을 설정하세요.
- 메인 큐가 바쁘면 heartbeat는 건너뛰고 나중에 다시 시도합니다.
- `target`이 외부 대상 없이 해석되더라도 실행은 이루어지지만
  아웃바운드 메시지는 전송되지 않습니다.
- `showOk`, `showAlerts`, `useIndicator`가 모두 비활성화되면 실행은 사전에 `reason=alerts-disabled`로 건너뛰어집니다.
- 경고 전달만 비활성화된 경우에도 OpenClaw는 heartbeat를 실행하고, due-task 타임스탬프를 업데이트하고, 세션 idle 타임스탬프를 복원하고, 외부 경고 페이로드는 억제할 수 있습니다.
- heartbeat 전용 응답은 세션을 활성 상태로 유지하지 않습니다. 마지막 `updatedAt`이
  복원되므로 idle 만료는 정상적으로 동작합니다.
- 분리된 [background tasks](/automation/tasks)는 메인 세션이 무언가를 빨리 알아야 할 때 시스템 이벤트를 큐에 넣고 heartbeat를 깨울 수 있습니다. 이 깨우기는 heartbeat 실행을 background task로 만들지는 않습니다.

## 가시성 제어

기본적으로 `HEARTBEAT_OK` ack는 억제되고 경고 내용은 전달됩니다.
이를 채널별 또는 계정별로 조정할 수 있습니다:

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false # Hide HEARTBEAT_OK (default)
      showAlerts: true # Show alert messages (default)
      useIndicator: true # Emit indicator events (default)
  telegram:
    heartbeat:
      showOk: true # Show OK acknowledgments on Telegram
  whatsapp:
    accounts:
      work:
        heartbeat:
          showAlerts: false # Suppress alert delivery for this account
```

우선순위: 계정별 → 채널별 → 채널 기본값 → 내장 기본값.

### 각 플래그의 기능

- `showOk`: 모델이 OK 전용 응답을 반환할 때 `HEARTBEAT_OK` ack를 전송합니다.
- `showAlerts`: 모델이 non-OK 응답을 반환할 때 경고 내용을 전송합니다.
- `useIndicator`: UI 상태 표면용 indicator 이벤트를 발생시킵니다.

**세 플래그가 모두** false이면 OpenClaw는 heartbeat 실행 전체를 건너뜁니다(모델 호출 없음).

### 채널별 vs 계정별 예시

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false
      showAlerts: true
      useIndicator: true
  slack:
    heartbeat:
      showOk: true # all Slack accounts
    accounts:
      ops:
        heartbeat:
          showAlerts: false # suppress alerts for the ops account only
  telegram:
    heartbeat:
      showOk: true
```

### 일반적인 패턴

| 목표 | 구성 |
| ---------------------------------------- | ---------------------------------------------------------------------------------------- |
| 기본 동작(조용한 OK, 경고는 켜짐) | _(구성 불필요)_ |
| 완전히 조용함(메시지 없음, indicator 없음) | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: false }` |
| indicator 전용(메시지 없음) | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: true }` |
| 한 채널에서만 OK 표시 | `channels.telegram.heartbeat: { showOk: true }` |

## HEARTBEAT.md(선택 사항)

워크스페이스에 `HEARTBEAT.md` 파일이 있으면 기본 프롬프트는 에이전트에게
이를 읽으라고 지시합니다. 이를 “heartbeat 체크리스트”로 생각하세요. 작고, 안정적이며,
30분마다 포함해도 안전해야 합니다.

`HEARTBEAT.md`가 존재하지만 사실상 비어 있으면(빈 줄과 `# Heading` 같은 markdown
헤더만 있는 경우), OpenClaw는 API 호출을 아끼기 위해 heartbeat 실행을 건너뜁니다.
이 건너뛰기는 `reason=empty-heartbeat-file`로 보고됩니다.
파일이 없으면 heartbeat는 계속 실행되고 모델이 무엇을 할지 결정합니다.

프롬프트가 커지지 않도록 작게 유지하세요(짧은 체크리스트 또는 알림).

예시 `HEARTBEAT.md`:

```md
# Heartbeat checklist

- Quick scan: anything urgent in inboxes?
- If it’s daytime, do a lightweight check-in if nothing else is pending.
- If a task is blocked, write down _what is missing_ and ask Peter next time.
```

### `tasks:` 블록

`HEARTBEAT.md`는 heartbeat 내부의 간격 기반
확인을 위해 작은 구조화된 `tasks:` 블록도 지원합니다.

예시:

```md
tasks:

- name: inbox-triage
  interval: 30m
  prompt: "Check for urgent unread emails and flag anything time sensitive."
- name: calendar-scan
  interval: 2h
  prompt: "Check for upcoming meetings that need prep or follow-up."

# Additional instructions

- Keep alerts short.
- If nothing needs attention after all due tasks, reply HEARTBEAT_OK.
```

동작:

- OpenClaw는 `tasks:` 블록을 파싱하고 각 작업을 자신의 `interval`에 따라 확인합니다.
- **기한이 된** 작업만 해당 틱의 heartbeat 프롬프트에 포함됩니다.
- 기한이 된 작업이 없으면 heartbeat는 낭비되는 모델 호출을 피하기 위해 전체가 건너뛰어집니다(`reason=no-tasks-due`).
- `HEARTBEAT.md`의 작업이 아닌 내용은 보존되며 기한이 된 작업 목록 뒤에 추가 컨텍스트로 덧붙여집니다.
- 작업 마지막 실행 타임스탬프는 세션 상태(`heartbeatTaskState`)에 저장되므로, 간격은 일반 재시작 후에도 유지됩니다.
- 작업 타임스탬프는 heartbeat 실행이 정상 응답 경로를 완료한 뒤에만 진행됩니다. 건너뛴 `empty-heartbeat-file` / `no-tasks-due` 실행은 작업을 완료로 표시하지 않습니다.

작업 모드는 하나의 heartbeat 파일 안에 여러 주기적 확인을 담고, 매 틱마다 그 모두에 대한 비용을 지불하지 않으려 할 때 유용합니다.

### 에이전트가 HEARTBEAT.md를 업데이트할 수 있나요?

네 — 그렇게 하라고 요청하면 됩니다.

`HEARTBEAT.md`는 에이전트 워크스페이스의 일반 파일일 뿐이므로, 일반 채팅에서
다음과 같이 에이전트에게 말할 수 있습니다:

- “`HEARTBEAT.md`를 업데이트해서 매일 캘린더 확인을 추가해줘.”
- “`HEARTBEAT.md`를 더 짧고 받은편지함 후속 조치에 집중되도록 다시 작성해줘.”

이 작업이 능동적으로 일어나게 하려면 heartbeat 프롬프트에
“체크리스트가 오래되면 더 나은 체크리스트로 HEARTBEAT.md를
업데이트하라” 같은 명시적인 줄을 추가할 수도 있습니다.

안전 참고: `HEARTBEAT.md`에 비밀 정보(API 키, 전화번호, 비공개 토큰)를 넣지 마세요 — 프롬프트 컨텍스트의 일부가 됩니다.

## 수동 깨우기(온디맨드)

시스템 이벤트를 큐에 넣고 즉시 heartbeat를 트리거하려면 다음을 사용하세요:

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
```

여러 에이전트에 `heartbeat`가 구성되어 있으면 수동 깨우기는 해당
에이전트 heartbeat를 모두 즉시 실행합니다.

다음 예약 틱까지 기다리려면 `--mode next-heartbeat`를 사용하세요.

## Reasoning 전달(선택 사항)

기본적으로 heartbeat는 최종 “응답” 페이로드만 전달합니다.

투명성이 필요하다면 다음을 활성화하세요:

- `agents.defaults.heartbeat.includeReasoning: true`

활성화되면 heartbeat는 `Reasoning:` 접두사가 붙은 별도 메시지도
전달합니다(`/reasoning on`과 같은 형태). 에이전트가 여러 세션/codex를 관리하고 있을 때
왜 사용자에게 핑을 보내기로 결정했는지 보고 싶다면 유용할 수 있지만,
원하지 않는 내부 세부 정보가 더 많이 노출될 수도 있습니다. 그룹 채팅에서는
끄는 편을 권장합니다.

## 비용 인식

Heartbeat는 전체 에이전트 턴을 실행합니다. 간격이 짧을수록 더 많은 토큰을 사용합니다. 비용을 줄이려면:

- `isolatedSession: true`를 사용해 전체 대화 기록 전송을 피합니다(실행당 약 100K 토큰에서 약 2-5K로 감소).
- `lightContext: true`를 사용해 부트스트랩 파일을 `HEARTBEAT.md`로만 제한합니다.
- 더 저렴한 `model`을 설정합니다(예: `ollama/llama3.2:1b`).
- `HEARTBEAT.md`를 작게 유지합니다.
- 내부 상태 업데이트만 원한다면 `target: "none"`을 사용합니다.

## 관련 항목

- [Automation & Tasks](/automation) — 모든 자동화 메커니즘 한눈에 보기
- [Background Tasks](/automation/tasks) — 분리된 작업이 추적되는 방식
- [Timezone](/concepts/timezone) — 시간대가 heartbeat 스케줄링에 미치는 영향
- [Troubleshooting](/automation/cron-jobs#troubleshooting) — 자동화 문제 디버깅
