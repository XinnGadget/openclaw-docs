---
read_when:
    - 백그라운드 작업 또는 깨우기 예약
    - 외부 트리거(웹훅, Gmail)를 OpenClaw에 연결
    - 예약 작업에 heartbeat와 cron 중 무엇을 사용할지 결정
summary: Gateway 스케줄러를 위한 예약 작업, 웹훅, Gmail PubSub 트리거
title: 예약 작업
x-i18n:
    generated_at: "2026-04-05T12:34:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 43b906914461aba9af327e7e8c22aa856f65802ec2da37ed0c4f872d229cfde6
    source_path: automation/cron-jobs.md
    workflow: 15
---

# 예약 작업 (Cron)

Cron은 Gateway에 내장된 스케줄러입니다. 작업을 영속적으로 저장하고, 적절한 시간에 에이전트를 깨우며, 출력 결과를 채팅 채널이나 웹훅 엔드포인트로 다시 전달할 수 있습니다.

## 빠른 시작

```bash
# 일회성 리마인더 추가
openclaw cron add \
  --name "Reminder" \
  --at "2026-02-01T16:00:00Z" \
  --session main \
  --system-event "Reminder: check the cron docs draft" \
  --wake now \
  --delete-after-run

# 작업 확인
openclaw cron list

# 실행 기록 보기
openclaw cron runs --id <job-id>
```

## cron 작동 방식

- Cron은 **Gateway 프로세스 내부에서** 실행됩니다(모델 내부가 아님).
- 작업은 `~/.openclaw/cron/jobs.json`에 영속 저장되므로 재시작해도 일정이 사라지지 않습니다.
- 모든 cron 실행은 [background task](/automation/tasks) 레코드를 생성합니다.
- 일회성 작업(`--at`)은 기본적으로 성공 후 자동 삭제됩니다.
- 격리된 cron 실행은 완료 시 해당 `cron:<jobId>` 세션에 대해 추적된 브라우저 탭/프로세스를 최선의 노력으로 종료하므로, 분리된 브라우저 자동화가 고아 프로세스를 남기지 않습니다.
- 격리된 cron 실행은 오래된 확인 응답도 방지합니다. 첫 번째 결과가 단지 중간 상태 업데이트(`on it`, `pulling everything together` 및 유사한 힌트)이고, 최종 답변에 여전히 책임이 있는 하위 subagent 실행이 없다면, OpenClaw는 전달 전에 실제 결과를 얻기 위해 한 번 더 다시 프롬프트합니다.

cron의 작업 조정은 런타임이 소유합니다. 오래된 하위 세션 행이 여전히 존재하더라도, 활성 cron 작업은 cron 런타임이 해당 작업을 실행 중으로 추적하는 동안 계속 활성 상태로 유지됩니다.
런타임이 더 이상 작업을 소유하지 않고 5분 유예 시간이 지나면, 유지보수에서 해당 작업을 `lost`로 표시할 수 있습니다.

## 일정 유형

| 종류    | CLI 플래그 | 설명                                                      |
| ------- | ---------- | --------------------------------------------------------- |
| `at`    | `--at`     | 일회성 타임스탬프(ISO 8601 또는 `20m` 같은 상대 시간)     |
| `every` | `--every`  | 고정 간격                                                  |
| `cron`  | `--cron`   | 선택적 `--tz`와 함께 사용하는 5필드 또는 6필드 cron 표현식 |

타임존이 없는 타임스탬프는 UTC로 처리됩니다. 로컬 벽시계 기준 예약에는 `--tz America/New_York`를 추가하세요.

정시 반복 표현식은 부하 급증을 줄이기 위해 최대 5분까지 자동으로 분산됩니다. 정확한 타이밍을 강제하려면 `--exact`를 사용하고, 명시적인 범위를 원하면 `--stagger 30s`를 사용하세요.

## 실행 스타일

| 스타일         | `--session` 값      | 실행 위치                 | 적합한 용도                     |
| -------------- | ------------------- | ------------------------- | ------------------------------- |
| 메인 세션      | `main`              | 다음 heartbeat 턴         | 리마인더, 시스템 이벤트         |
| 격리됨         | `isolated`          | 전용 `cron:<jobId>`       | 리포트, 백그라운드 작업         |
| 현재 세션      | `current`           | 생성 시점에 바인딩됨      | 컨텍스트 인지형 반복 작업       |
| 커스텀 세션    | `session:custom-id` | 영속적인 이름 있는 세션   | 기록을 기반으로 쌓이는 워크플로 |

**메인 세션** 작업은 시스템 이벤트를 큐에 넣고 선택적으로 heartbeat를 깨웁니다(`--wake now` 또는 `--wake next-heartbeat`). **격리됨** 작업은 새 세션으로 전용 에이전트 턴을 실행합니다. **커스텀 세션**(`session:xxx`)은 실행 간 컨텍스트를 유지하므로, 이전 요약을 바탕으로 쌓이는 일일 스탠드업 같은 워크플로를 가능하게 합니다.

격리된 작업의 경우, 런타임 종료 단계에는 이제 해당 cron 세션에 대한 최선의 노력 기반 브라우저 정리가 포함됩니다. 정리 실패는 실제 cron 결과가 우선되도록 무시됩니다.

격리된 cron 실행이 subagent를 조정할 때는, 전달 시에도 오래된 상위 중간 텍스트보다 최종 하위 결과를 우선합니다. 하위 실행이 아직 진행 중이면, OpenClaw는 그 부분적인 상위 업데이트를 알리는 대신 억제합니다.

### 격리된 작업의 페이로드 옵션

- `--message`: 프롬프트 텍스트(격리됨에서 필수)
- `--model` / `--thinking`: 모델 및 thinking 수준 재정의
- `--light-context`: 워크스페이스 부트스트랩 파일 주입 건너뛰기
- `--tools exec,read`: 작업이 사용할 수 있는 도구 제한

`--model`은 해당 작업에 대해 선택된 허용 모델을 사용합니다. 요청한 모델이 허용되지 않으면 cron은 경고를 기록하고, 대신 작업의 agent/default 모델 선택으로 대체합니다. 구성된 fallback 체인은 계속 적용되지만, 명시적 작업별 fallback 목록이 없는 단순 모델 재정의는 더 이상 숨겨진 추가 재시도 대상으로 agent primary를 덧붙이지 않습니다.

격리된 작업의 모델 선택 우선순위는 다음과 같습니다.

1. Gmail 훅 모델 재정의(실행이 Gmail에서 왔고 해당 재정의가 허용된 경우)
2. 작업별 페이로드 `model`
3. 저장된 cron 세션 모델 재정의
4. Agent/default 모델 선택

빠른 모드도 해결된 라이브 선택을 따릅니다. 선택된 모델 구성에 `params.fastMode`가 있으면, 격리된 cron은 기본적으로 이를 사용합니다. 저장된 세션 `fastMode` 재정의는 어느 방향에서든 여전히 구성보다 우선합니다.

격리된 실행이 라이브 모델 전환 handoff에 도달하면, cron은 전환된 provider/model로 재시도하고 재시도 전에 해당 라이브 선택을 영속 저장합니다. 전환에 새 auth profile도 포함되어 있으면, cron은 그 auth profile 재정의도 저장합니다. 재시도는 제한됩니다. 초기 시도에 더해 전환 재시도 2회를 넘기면, cron은 무한 반복하는 대신 중단합니다.

## 전달 및 출력

| 모드       | 동작                                                         |
| ---------- | ------------------------------------------------------------ |
| `announce` | 요약을 대상 채널로 전달(격리됨의 기본값)                     |
| `webhook`  | 완료된 이벤트 페이로드를 URL로 POST                          |
| `none`     | 내부 전용, 전달 없음                                         |

채널 전달에는 `--announce --channel telegram --to "-1001234567890"`를 사용하세요. Telegram 포럼 주제의 경우 `-1001234567890:topic:123`을 사용하세요. Slack/Discord/Mattermost 대상은 명시적 접두사(`channel:<id>`, `user:<id>`)를 사용해야 합니다.

cron이 소유한 격리된 작업의 경우, 실행기가 최종 전달 경로를 소유합니다. 에이전트는 일반 텍스트 요약을 반환하도록 프롬프트되며, 그 요약은 이후 `announce`, `webhook`으로 전송되거나 `none`일 경우 내부에만 유지됩니다. `--no-deliver`는 전달을 에이전트에 되돌리지 않으며, 실행을 내부 전용으로 유지합니다.

원래 작업이 어떤 외부 수신자에게 메시지를 보내라고 명시적으로 지시한 경우, 에이전트는 직접 전송을 시도하는 대신 그 메시지가 누구/어디로 가야 하는지를 출력에 적어야 합니다.

실패 알림은 별도의 대상 경로를 따릅니다.

- `cron.failureDestination`은 실패 알림의 전역 기본값을 설정합니다.
- `job.delivery.failureDestination`은 작업별로 이를 재정의합니다.
- 둘 다 설정되지 않았고 작업이 이미 `announce`를 통해 전달하는 경우, 실패 알림은 이제 기본 announce 대상으로 대체됩니다.
- `delivery.failureDestination`은 기본 전달 모드가 `webhook`인 경우를 제외하면 `sessionTarget="isolated"` 작업에서만 지원됩니다.

## CLI 예시

일회성 리마인더(메인 세션):

```bash
openclaw cron add \
  --name "Calendar check" \
  --at "20m" \
  --session main \
  --system-event "Next heartbeat: check calendar." \
  --wake now
```

전달이 포함된 반복 격리 작업:

```bash
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize overnight updates." \
  --announce \
  --channel slack \
  --to "channel:C1234567890"
```

모델 및 thinking 재정의가 포함된 격리 작업:

```bash
openclaw cron add \
  --name "Deep analysis" \
  --cron "0 6 * * 1" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Weekly deep analysis of project progress." \
  --model "opus" \
  --thinking high \
  --announce
```

## 웹훅

Gateway는 외부 트리거를 위해 HTTP 웹훅 엔드포인트를 노출할 수 있습니다. config에서 활성화하세요.

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
  },
}
```

### 인증

모든 요청에는 헤더를 통해 훅 토큰이 포함되어야 합니다.

- `Authorization: Bearer <token>`(권장)
- `x-openclaw-token: <token>`

쿼리 문자열 토큰은 거부됩니다.

### POST /hooks/wake

메인 세션에 시스템 이벤트를 큐에 넣습니다.

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"text":"New email received","mode":"now"}'
```

- `text`(필수): 이벤트 설명
- `mode`(선택 사항): `now`(기본값) 또는 `next-heartbeat`

### POST /hooks/agent

격리된 에이전트 턴을 실행합니다.

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","model":"openai/gpt-5.4-mini"}'
```

필드: `message`(필수), `name`, `agentId`, `wakeMode`, `deliver`, `channel`, `to`, `model`, `thinking`, `timeoutSeconds`.

### 매핑된 훅(POST /hooks/\<name\>)

커스텀 훅 이름은 config의 `hooks.mappings`를 통해 해석됩니다. 매핑은 템플릿이나 코드 변환을 사용해 임의의 페이로드를 `wake` 또는 `agent` 작업으로 변환할 수 있습니다.

### 보안

- 훅 엔드포인트는 loopback, tailnet 또는 신뢰할 수 있는 리버스 프록시 뒤에 두세요.
- 전용 훅 토큰을 사용하세요. gateway auth 토큰을 재사용하지 마세요.
- `hooks.path`는 전용 하위 경로로 유지하세요. `/`는 거부됩니다.
- 명시적 `agentId` 라우팅을 제한하려면 `hooks.allowedAgentIds`를 설정하세요.
- 호출자가 세션을 선택해야 하는 경우가 아니라면 `hooks.allowRequestSessionKey=false`를 유지하세요.
- `hooks.allowRequestSessionKey`를 활성화하는 경우, 허용된 세션 키 형태를 제한하기 위해 `hooks.allowedSessionKeyPrefixes`도 함께 설정하세요.
- 훅 페이로드는 기본적으로 안전 경계로 감싸집니다.

## Gmail PubSub 통합

Google PubSub를 통해 Gmail 받은편지함 트리거를 OpenClaw에 연결하세요.

**사전 요구 사항**: `gcloud` CLI, `gog`(gogcli), OpenClaw hooks 활성화, 공개 HTTPS 엔드포인트용 Tailscale.

### 마법사 설정(권장)

```bash
openclaw webhooks gmail setup --account openclaw@gmail.com
```

이 명령은 `hooks.gmail` config를 기록하고, Gmail 프리셋을 활성화하며, 푸시 엔드포인트에 Tailscale Funnel을 사용합니다.

### Gateway 자동 시작

`hooks.enabled=true`이고 `hooks.gmail.account`가 설정되어 있으면, Gateway는 부팅 시 `gog gmail watch serve`를 시작하고 watch를 자동 갱신합니다. 제외하려면 `OPENCLAW_SKIP_GMAIL_WATCHER=1`을 설정하세요.

### 수동 1회 설정

1. `gog`가 사용하는 OAuth 클라이언트를 소유한 GCP 프로젝트를 선택합니다.

```bash
gcloud auth login
gcloud config set project <project-id>
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

2. 토픽을 만들고 Gmail 푸시 액세스 권한을 부여합니다.

```bash
gcloud pubsub topics create gog-gmail-watch
gcloud pubsub topics add-iam-policy-binding gog-gmail-watch \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
```

3. watch를 시작합니다.

```bash
gog gmail watch start \
  --account openclaw@gmail.com \
  --label INBOX \
  --topic projects/<project-id>/topics/gog-gmail-watch
```

### Gmail 모델 재정의

```json5
{
  hooks: {
    gmail: {
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

## 작업 관리

```bash
# 모든 작업 나열
openclaw cron list

# 작업 편집
openclaw cron edit <jobId> --message "Updated prompt" --model "opus"

# 지금 작업 강제 실행
openclaw cron run <jobId>

# 기한이 지난 경우에만 실행
openclaw cron run <jobId> --due

# 실행 기록 보기
openclaw cron runs --id <jobId> --limit 50

# 작업 삭제
openclaw cron remove <jobId>

# Agent 선택(멀티 agent 설정)
openclaw cron add --name "Ops sweep" --cron "0 6 * * *" --session isolated --message "Check ops queue" --agent ops
openclaw cron edit <jobId> --clear-agent
```

모델 재정의 참고:

- `openclaw cron add|edit --model ...`은 작업의 선택된 모델을 변경합니다.
- 모델이 허용되면, 정확히 그 provider/model이 격리된 agent 실행에 전달됩니다.
- 허용되지 않으면, cron은 경고를 표시하고 작업의 agent/default 모델 선택으로 대체합니다.
- 구성된 fallback 체인은 계속 적용되지만, 명시적 작업별 fallback 목록이 없는 일반 `--model` 재정의는 더 이상 조용한 추가 재시도 대상으로 agent primary로 넘어가지 않습니다.

## 구성

```json5
{
  cron: {
    enabled: true,
    store: "~/.openclaw/cron/jobs.json",
    maxConcurrentRuns: 1,
    retry: {
      maxAttempts: 3,
      backoffMs: [60000, 120000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "server_error"],
    },
    webhookToken: "replace-with-dedicated-webhook-token",
    sessionRetention: "24h",
    runLog: { maxBytes: "2mb", keepLines: 2000 },
  },
}
```

cron 비활성화: `cron.enabled: false` 또는 `OPENCLAW_SKIP_CRON=1`.

**일회성 재시도**: 일시적 오류(rate limit, overload, network, server error)는 지수 백오프와 함께 최대 3회 재시도합니다. 영구 오류는 즉시 비활성화됩니다.

**반복 재시도**: 재시도 사이에 지수 백오프(30초~60분)를 사용합니다. 다음 성공 실행 후에는 백오프가 초기화됩니다.

**유지보수**: `cron.sessionRetention`(기본값 `24h`)은 격리된 실행 세션 항목을 정리합니다. `cron.runLog.maxBytes` / `cron.runLog.keepLines`는 실행 로그 파일을 자동 정리합니다.

## 문제 해결

### 명령 순서

```bash
openclaw status
openclaw gateway status
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
openclaw doctor
```

### Cron이 실행되지 않음

- `cron.enabled`와 `OPENCLAW_SKIP_CRON` 환경 변수를 확인하세요.
- Gateway가 계속 실행 중인지 확인하세요.
- `cron` 일정의 경우 타임존(`--tz`)과 호스트 타임존이 일치하는지 확인하세요.
- 실행 출력의 `reason: not-due`는 수동 실행이 `openclaw cron run <jobId> --due`로 확인되었고 작업 기한이 아직 되지 않았음을 의미합니다.

### Cron이 실행되었지만 전달이 없음

- 전달 모드가 `none`이면 외부 메시지는 예상되지 않습니다.
- 전달 대상이 없거나 잘못된 경우(`channel`/`to`) 아웃바운드가 건너뛰어집니다.
- 채널 인증 오류(`unauthorized`, `Forbidden`)는 자격 증명 때문에 전달이 차단되었음을 의미합니다.
- 격리된 실행이 무음 토큰(`NO_REPLY` / `no_reply`)만 반환하면, OpenClaw는 직접 아웃바운드 전달과 fallback 대기열 요약 경로도 모두 억제하므로 채팅으로 아무것도 게시되지 않습니다.
- cron이 소유한 격리된 작업의 경우, fallback으로 에이전트가 message 도구를 사용할 것이라 기대하지 마세요. 최종 전달은 실행기가 소유하며, `--no-deliver`는 직접 전송을 허용하는 대신 내부 전용으로 유지합니다.

### 타임존 관련 주의사항

- `--tz`가 없는 cron은 gateway 호스트 타임존을 사용합니다.
- 타임존이 없는 `at` 일정은 UTC로 처리됩니다.
- Heartbeat `activeHours`는 구성된 타임존 해석을 사용합니다.

## 관련 항목

- [Automation & Tasks](/automation) — 모든 자동화 메커니즘 한눈에 보기
- [Background Tasks](/automation/tasks) — cron 실행을 위한 작업 원장
- [Heartbeat](/gateway/heartbeat) — 주기적인 메인 세션 턴
- [Timezone](/concepts/timezone) — 타임존 구성
