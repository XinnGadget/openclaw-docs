---
read_when:
    - 채널 연결성 또는 게이트웨이 상태를 진단할 때
    - 상태 점검 CLI 명령과 옵션을 이해하려고 할 때
summary: 상태 점검 명령과 게이트웨이 상태 모니터링
title: 상태 점검
x-i18n:
    generated_at: "2026-04-05T12:42:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: b8824bca34c4d1139f043481c75f0a65d83e54008898c34cf69c6f98fd04e819
    source_path: gateway/health.md
    workflow: 15
---

# 상태 점검(CLI)

추측하지 않고 채널 연결성을 확인하기 위한 짧은 가이드입니다.

## 빠른 점검

- `openclaw status` — 로컬 요약: 게이트웨이 도달 가능성/모드, 업데이트 힌트, 연결된 채널 인증 경과 시간, 세션 + 최근 활동.
- `openclaw status --all` — 전체 로컬 진단(읽기 전용, 색상 포함, 디버깅용으로 안전하게 붙여넣기 가능).
- `openclaw status --deep` — 실행 중인 게이트웨이에 실시간 상태 프로브(`probe:true`가 포함된 `health`)를 요청하며, 지원되는 경우 계정별 채널 프로브도 포함됩니다.
- `openclaw health` — 실행 중인 게이트웨이에 상태 스냅샷을 요청합니다(WS 전용, CLI에서 직접 채널 소켓에 연결하지 않음).
- `openclaw health --verbose` — 실시간 상태 프로브를 강제하고 게이트웨이 연결 세부 정보를 출력합니다.
- `openclaw health --json` — 기계 판독 가능한 상태 스냅샷 출력.
- WhatsApp/WebChat에서 `/status`를 독립 실행형 메시지로 보내면 에이전트를 호출하지 않고 상태 답장을 받을 수 있습니다.
- 로그: `/tmp/openclaw/openclaw-*.log`를 tail하고 `web-heartbeat`, `web-reconnect`, `web-auto-reply`, `web-inbound`로 필터링하세요.

## 심층 진단

- 디스크의 자격 증명: `ls -l ~/.openclaw/credentials/whatsapp/<accountId>/creds.json`(mtime이 최신이어야 함).
- 세션 저장소: `ls -l ~/.openclaw/agents/<agentId>/sessions/sessions.json`(경로는 config에서 재정의 가능). 개수와 최근 수신자는 `status`를 통해 표시됩니다.
- 재연결 흐름: 로그에 상태 코드 409–515 또는 `loggedOut`이 나타나면 `openclaw channels logout && openclaw channels login --verbose`. (참고: QR 로그인 흐름은 페어링 후 상태 515에 대해 한 번 자동 재시작됩니다.)

## 상태 모니터 config

- `gateway.channelHealthCheckMinutes`: 게이트웨이가 채널 상태를 확인하는 주기. 기본값: `5`. 상태 모니터 재시작을 전역적으로 비활성화하려면 `0`으로 설정하세요.
- `gateway.channelStaleEventThresholdMinutes`: 연결된 채널이 얼마나 오래 유휴 상태로 있을 수 있는지, 그 이후 상태 모니터가 이를 오래된 상태로 간주하고 재시작하는지 정의합니다. 기본값: `30`. 이 값은 `gateway.channelHealthCheckMinutes`보다 크거나 같아야 합니다.
- `gateway.channelMaxRestartsPerHour`: 채널/계정별 상태 모니터 재시작의 1시간 롤링 상한. 기본값: `10`.
- `channels.<provider>.healthMonitor.enabled`: 전역 모니터링을 유지한 채 특정 채널에 대한 상태 모니터 재시작만 비활성화합니다.
- `channels.<provider>.accounts.<accountId>.healthMonitor.enabled`: 채널 수준 설정보다 우선하는 다중 계정 재정의.
- 이러한 채널별 재정의는 현재 이를 노출하는 내장 채널 모니터에 적용됩니다: Discord, Google Chat, iMessage, Microsoft Teams, Signal, Slack, Telegram, WhatsApp.

## 문제가 발생했을 때

- `logged out` 또는 상태 409–515 → `openclaw channels logout` 후 `openclaw channels login`으로 다시 연결합니다.
- 게이트웨이에 도달할 수 없음 → 시작하세요: `openclaw gateway --port 18789`(포트가 사용 중이면 `--force` 사용).
- 수신 메시지가 없음 → 연결된 휴대폰이 온라인인지, 발신자가 허용되었는지(`channels.whatsapp.allowFrom`) 확인하세요. 그룹 채팅의 경우 허용 목록 + 멘션 규칙이 일치하는지 확인하세요(`channels.whatsapp.groups`, `agents.list[].groupChat.mentionPatterns`).

## 전용 "health" 명령

`openclaw health`는 실행 중인 게이트웨이에 상태 스냅샷을 요청합니다(CLI에서 직접 채널
소켓에 연결하지 않음). 기본적으로 이 명령은 새로고침된 캐시형 게이트웨이 스냅샷을 반환할 수 있으며, 게이트웨이는
그 이후 백그라운드에서 해당 캐시를 갱신합니다. `openclaw health --verbose`는 대신
실시간 프로브를 강제합니다. 이 명령은 사용 가능한 경우 연결된 자격 증명/인증 경과 시간,
채널별 프로브 요약, 세션 저장소 요약, 프로브 지속 시간을 보고합니다. 게이트웨이에
도달할 수 없거나 프로브가 실패/타임아웃되면 0이 아닌 종료 코드를 반환합니다.

옵션:

- `--json`: 기계 판독 가능한 JSON 출력
- `--timeout <ms>`: 기본 10초 프로브 타임아웃 재정의
- `--verbose`: 실시간 프로브를 강제하고 게이트웨이 연결 세부 정보 출력
- `--debug`: `--verbose`의 별칭

상태 스냅샷에는 다음이 포함됩니다: `ok`(불리언), `ts`(타임스탬프), `durationMs`(프로브 시간), 채널별 상태, 에이전트 가용성, 세션 저장소 요약.
