---
read_when:
    - 예약된 작업과 웨이크업이 필요할 때
    - cron 실행 및 로그를 디버깅할 때
summary: '`openclaw cron`용 CLI 참조(백그라운드 작업 예약 및 실행)'
title: cron
x-i18n:
    generated_at: "2026-04-05T12:37:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: f74ec8847835f24b3970f1b260feeb69c7ab6c6ec7e41615cbb73f37f14a8112
    source_path: cli/cron.md
    workflow: 15
---

# `openclaw cron`

게이트웨이 스케줄러의 cron 작업을 관리합니다.

관련 항목:

- Cron Jobs: [Cron Jobs](/automation/cron-jobs)

팁: 전체 명령 표면을 보려면 `openclaw cron --help`를 실행하세요.

참고: 격리된 `cron add` 작업은 기본적으로 `--announce` 전달을 사용합니다. 출력을 내부 전용으로 유지하려면 `--no-deliver`를 사용하세요. `--deliver`는 `--announce`의 더 이상 권장되지 않는 별칭으로 유지됩니다.

참고: cron이 소유하는 격리 실행은 일반 텍스트 요약을 기대하며, 최종 전송 경로는 실행기가 소유합니다. `--no-deliver`는 실행을 내부 전용으로 유지합니다. 이 옵션은 전달을 에이전트의 메시지 도구로 다시 넘기지 않습니다.

참고: 원샷(`--at`) 작업은 기본적으로 성공 후 삭제됩니다. 유지하려면 `--keep-after-run`을 사용하세요.

참고: `--session`은 `main`, `isolated`, `current`, `session:<id>`를 지원합니다. 생성 시 활성 세션에 바인딩하려면 `current`를 사용하고, 명시적인 영구 세션 키를 사용하려면 `session:<id>`를 사용하세요.

참고: 원샷 CLI 작업의 경우, 오프셋이 없는 `--at` 날짜/시간은 `--tz <iana>`를 함께 전달하지 않는 한 UTC로 처리됩니다. `--tz <iana>`를 함께 전달하면 해당 로컬 벽시계 시간을 지정한 시간대에서 해석합니다.

참고: 반복 작업은 이제 연속 오류 후 지수적 재시도 백오프(30초 → 1분 → 5분 → 15분 → 60분)를 사용하며, 다음 성공 실행 후 정상 일정으로 돌아갑니다.

참고: `openclaw cron run`은 이제 수동 실행이 실행 대기열에 들어가자마자 반환됩니다. 성공 응답에는 `{ ok: true, enqueued: true, runId }`가 포함됩니다. 최종 결과를 추적하려면 `openclaw cron runs --id <job-id>`를 사용하세요.

참고: `openclaw cron run <job-id>`는 기본적으로 강제 실행합니다. 이전의 "기한이 되었을 때만 실행" 동작을 유지하려면 `--due`를 사용하세요.

참고: 격리된 cron 턴은 오래된 확인 전용 응답을 억제합니다. 첫 번째 결과가 단지 중간 상태 업데이트일 뿐이고, 최종 답변을 담당하는 하위 에이전트 실행이 없다면 cron은 전달 전에 실제 결과를 위해 한 번 더 다시 프롬프트합니다.

참고: 격리된 cron 실행이 무음 토큰만 반환하는 경우(`NO_REPLY` / `no_reply`), cron은 직접 아웃바운드 전달과 대체 대기열 요약 경로도 함께 억제하므로 채팅에 아무것도 게시되지 않습니다.

참고: `cron add|edit --model ...`은 해당 작업에 그 선택된 허용 모델을 사용합니다. 모델이 허용되지 않으면 cron은 경고를 출력하고 대신 작업의 에이전트/기본 모델 선택으로 대체합니다. 구성된 대체 체인은 계속 적용되지만, 명시적인 작업별 대체 목록이 없는 일반 모델 재정의는 더 이상 에이전트 기본 모델을 숨겨진 추가 재시도 대상으로 붙이지 않습니다.

참고: 격리된 cron 모델 우선순위는 Gmail-hook 재정의가 먼저이고, 그다음 작업별 `--model`, 그다음 저장된 cron 세션 모델 재정의, 마지막으로 일반 에이전트/기본 선택입니다.

참고: 격리된 cron fast mode는 확인된 라이브 모델 선택을 따릅니다. 모델 config `params.fastMode`는 기본적으로 적용되지만, 저장된 세션 `fastMode` 재정의는 여전히 config보다 우선합니다.

참고: 격리된 실행에서 `LiveSessionModelSwitchError`가 발생하면 cron은 재시도 전에 전환된 provider/model(존재하는 경우 전환된 auth profile 재정의 포함)을 유지합니다. 바깥쪽 재시도 루프는 초기 시도 후 최대 2번의 전환 재시도로 제한되며, 이후에는 무한 루프 대신 중단합니다.

참고: 실패 알림은 먼저 `delivery.failureDestination`을 사용하고, 그다음 전역 `cron.failureDestination`, 마지막으로 명시적 실패 대상이 구성되지 않은 경우 작업의 기본 announce 대상으로 대체됩니다.

참고: 보존/정리는 config에서 제어됩니다:

- `cron.sessionRetention`(기본값 `24h`)은 완료된 격리 실행 세션을 정리합니다.
- `cron.runLog.maxBytes` + `cron.runLog.keepLines`는 `~/.openclaw/cron/runs/<jobId>.jsonl`을 정리합니다.

업그레이드 참고: 현재 전달/저장 형식 이전의 오래된 cron 작업이 있다면 `openclaw doctor --fix`를 실행하세요. 이제 doctor는 레거시 cron 필드(`jobId`, `schedule.cron`, 레거시 `threadId`를 포함한 최상위 전달 필드, payload `provider` 전달 별칭)를 정규화하고, `cron.webhook`이 구성된 경우 단순한 `notify: true` 웹훅 대체 작업을 명시적 웹훅 전달로 마이그레이션합니다.

## 일반적인 편집

메시지를 변경하지 않고 전달 설정만 업데이트:

```bash
openclaw cron edit <job-id> --announce --channel telegram --to "123456789"
```

격리된 작업의 전달 비활성화:

```bash
openclaw cron edit <job-id> --no-deliver
```

격리된 작업에 경량 부트스트랩 컨텍스트 활성화:

```bash
openclaw cron edit <job-id> --light-context
```

특정 채널로 announce:

```bash
openclaw cron edit <job-id> --announce --channel slack --to "channel:C1234567890"
```

경량 부트스트랩 컨텍스트로 격리된 작업 생성:

```bash
openclaw cron add \
  --name "경량 아침 브리프" \
  --cron "0 7 * * *" \
  --session isolated \
  --message "밤사이 업데이트를 요약하세요." \
  --light-context \
  --no-deliver
```

`--light-context`는 격리된 agent-turn 작업에만 적용됩니다. cron 실행에서는 경량 모드가 전체 워크스페이스 부트스트랩 세트를 주입하는 대신 부트스트랩 컨텍스트를 비워 둡니다.

전달 소유권 참고:

- cron이 소유하는 격리 작업은 항상 최종 사용자 표시 전달을 cron 실행기(`announce`, `webhook`, 또는 내부 전용 `none`)를 통해 라우팅합니다.
- 작업이 어떤 외부 수신자에게 메시지를 보내는 것을 언급하는 경우, 에이전트는 직접 보내려고 하지 말고 결과에 의도된 대상을 설명해야 합니다.

## 일반적인 관리자 명령

수동 실행:

```bash
openclaw cron run <job-id>
openclaw cron run <job-id> --due
openclaw cron runs --id <job-id> --limit 50
```

에이전트/세션 재지정:

```bash
openclaw cron edit <job-id> --agent ops
openclaw cron edit <job-id> --clear-agent
openclaw cron edit <job-id> --session current
openclaw cron edit <job-id> --session "session:daily-brief"
```

전달 조정:

```bash
openclaw cron edit <job-id> --announce --channel slack --to "channel:C1234567890"
openclaw cron edit <job-id> --best-effort-deliver
openclaw cron edit <job-id> --no-best-effort-deliver
openclaw cron edit <job-id> --no-deliver
```

실패 전달 참고:

- `delivery.failureDestination`은 격리된 작업에 지원됩니다.
- 메인 세션 작업은 기본 전달 모드가 `webhook`일 때만 `delivery.failureDestination`을 사용할 수 있습니다.
- 실패 대상을 별도로 설정하지 않았고 작업이 이미 채널에 announce하고 있다면, 실패 알림은 동일한 announce 대상을 재사용합니다.
