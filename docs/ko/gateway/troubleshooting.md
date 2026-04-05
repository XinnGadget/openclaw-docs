---
read_when:
    - 더 깊은 진단을 위해 문제 해결 허브가 이 페이지로 안내한 경우
    - 정확한 명령이 포함된 안정적인 증상 기반 실행 가이드 섹션이 필요한 경우
summary: gateway, 채널, 자동화, node, browser를 위한 심화 문제 해결 실행 가이드
title: 문제 해결
x-i18n:
    generated_at: "2026-04-05T12:44:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 028226726e6adc45ca61d41510a953c4e21a3e85f3082af9e8085745c6ac3ec1
    source_path: gateway/troubleshooting.md
    workflow: 15
---

# Gateway 문제 해결

이 페이지는 심화 실행 가이드입니다.
먼저 빠른 분류 흐름이 필요하다면 [/help/troubleshooting](/help/troubleshooting)에서 시작하세요.

## 명령 순서

먼저 다음 명령을 이 순서대로 실행하세요.

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

예상되는 정상 신호:

- `openclaw gateway status`에 `Runtime: running`과 `RPC probe: ok`가 표시됩니다.
- `openclaw doctor`가 차단하는 config/서비스 문제를 보고하지 않습니다.
- `openclaw channels status --probe`가 계정별 라이브 전송 상태와,
  지원되는 경우 `works` 또는 `audit ok` 같은 프로브/감사 결과를 표시합니다.

## 긴 컨텍스트에 Anthropic 429 extra usage required

로그/오류에 다음이 포함될 때 이 섹션을 사용하세요:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

확인할 사항:

- 선택된 Anthropic Opus/Sonnet 모델에 `params.context1m: true`가 설정되어 있습니다.
- 현재 Anthropic 자격 증명은 긴 컨텍스트 사용에 적합하지 않습니다.
- 요청이 1M 베타 경로가 필요한 긴 세션/모델 실행에서만 실패합니다.

해결 방법:

1. 해당 모델에서 `context1m`을 비활성화해 일반 컨텍스트 창으로 fallback합니다.
2. 청구가 가능한 Anthropic API 키를 사용하거나, Anthropic OAuth/구독 계정에서 Anthropic Extra Usage를 활성화합니다.
3. Anthropic 긴 컨텍스트 요청이 거부될 때도 실행이 계속되도록 fallback 모델을 구성합니다.

관련 항목:

- [/providers/anthropic](/providers/anthropic)
- [/reference/token-use](/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## 응답이 없음

채널은 올라와 있지만 아무 응답이 없다면, 무엇이든 다시 연결하기 전에 먼저 라우팅과 정책을 점검하세요.

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

확인할 사항:

- DM 발신자에 대한 페어링 대기 중 상태.
- 그룹 멘션 게이팅(`requireMention`, `mentionPatterns`).
- 채널/그룹 허용 목록 불일치.

일반적인 징후:

- `drop guild message (mention required` → 멘션이 있을 때까지 그룹 메시지가 무시됨.
- `pairing request` → 발신자 승인이 필요함.
- `blocked` / `allowlist` → 발신자/채널이 정책에 의해 필터링됨.

관련 항목:

- [/channels/troubleshooting](/channels/troubleshooting)
- [/channels/pairing](/channels/pairing)
- [/channels/groups](/channels/groups)

## Dashboard control ui 연결

dashboard/control UI가 연결되지 않으면 URL, auth 모드, 보안 컨텍스트 가정을 검증하세요.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

확인할 사항:

- 올바른 프로브 URL 및 dashboard URL.
- 클라이언트와 gateway 간 auth 모드/토큰 불일치.
- 디바이스 신원이 필요한 상황에서의 HTTP 사용.

일반적인 징후:

- `device identity required` → 비보안 컨텍스트이거나 디바이스 auth가 누락됨.
- `origin not allowed` → browser `Origin`이 `gateway.controlUi.allowedOrigins`에 없거나
  (또는 명시적 허용 목록 없이 비-loopback browser origin에서 연결 중임).
- `device nonce required` / `device nonce mismatch` → 클라이언트가
  챌린지 기반 디바이스 auth 흐름(`connect.challenge` + `device.nonce`)을 완료하지 못함.
- `device signature invalid` / `device signature expired` → 클라이언트가 현재 핸드셰이크에 대해 잘못된
  페이로드(또는 오래된 타임스탬프)에 서명함.
- `AUTH_TOKEN_MISMATCH`와 `canRetryWithDeviceToken=true` → 클라이언트는 캐시된 디바이스 토큰으로 한 번 신뢰 재시도를 수행할 수 있음.
- 해당 캐시 토큰 재시도는 페어링된
  디바이스 토큰과 함께 저장된 캐시 범위 집합을 재사용합니다. 명시적 `deviceToken` / 명시적 `scopes` 호출자는 요청한 범위 집합을 유지합니다.
- 그 재시도 경로 밖에서는 연결 auth 우선순위가 명시적 공유
  토큰/비밀번호 우선, 그다음 명시적 `deviceToken`, 그다음 저장된 디바이스 토큰,
  그다음 bootstrap 토큰입니다.
- 비동기 Tailscale Serve Control UI 경로에서는 동일한
  `{scope, ip}`에 대한 실패 시도가 limiter가 실패를 기록하기 전에 직렬화됩니다. 따라서 같은 클라이언트의 잘못된 동시 재시도 두 개에서는 두 번의 일반 불일치 대신 두 번째 시도에 `retry later`가 나타날 수 있습니다.
- browser-origin loopback 클라이언트에서 `too many failed authentication attempts (retry later)` →
  동일한 정규화된 `Origin`에서 반복된 실패가 일시적으로 잠깁니다. 다른 localhost origin은 별도 버킷을 사용합니다.
- 그 재시도 후에도 반복되는 `unauthorized` → 공유 토큰/디바이스 토큰 드리프트; 필요하면 토큰 config를 새로 고치고 디바이스 토큰을 다시 승인/회전하세요.
- `gateway connect failed:` → 잘못된 host/port/url 대상.

### Auth 세부 코드 빠른 매핑

실패한 `connect` 응답의 `error.details.code`를 사용해 다음 조치를 선택하세요.

| 세부 코드                    | 의미                                                     | 권장 조치                                                                                                                                                                                                                                                                         |
| ---------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AUTH_TOKEN_MISSING`         | 클라이언트가 필요한 공유 토큰을 보내지 않았습니다.       | 클라이언트에 토큰을 붙여넣거나 설정한 뒤 다시 시도하세요. dashboard 경로의 경우: `openclaw config get gateway.auth.token` 후 Control UI 설정에 붙여넣으세요.                                                                                                                     |
| `AUTH_TOKEN_MISMATCH`        | 공유 토큰이 gateway auth 토큰과 일치하지 않습니다.       | `canRetryWithDeviceToken=true`이면 한 번의 신뢰 재시도를 허용하세요. 캐시 토큰 재시도는 저장된 승인 범위를 재사용하며, 명시적 `deviceToken` / `scopes` 호출자는 요청한 범위를 유지합니다. 여전히 실패하면 [토큰 드리프트 복구 체크리스트](/cli/devices#token-drift-recovery-checklist)를 실행하세요. |
| `AUTH_DEVICE_TOKEN_MISMATCH` | 캐시된 디바이스별 토큰이 오래되었거나 취소되었습니다.    | [devices CLI](/cli/devices)를 사용해 디바이스 토큰을 회전/재승인한 뒤 다시 연결하세요.                                                                                                                                                                                             |
| `PAIRING_REQUIRED`           | 디바이스 신원은 알려져 있지만 이 역할에 대해 승인되지 않았습니다. | 대기 중 요청을 승인하세요: `openclaw devices list` 후 `openclaw devices approve <requestId>`.                                                                                                                                                                                      |

디바이스 auth v2 마이그레이션 점검:

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

로그에 nonce/signature 오류가 보이면 연결하는 클라이언트를 업데이트하고 다음을 확인하세요.

1. `connect.challenge`를 기다림
2. 챌린지에 바인딩된 페이로드에 서명함
3. 같은 챌린지 nonce와 함께 `connect.params.device.nonce`를 보냄

`openclaw devices rotate` / `revoke` / `remove`가 예상치 못하게 거부된다면:

- 페어링된 디바이스 토큰 세션은
  호출자에게 `operator.admin`도 없는 한 **자기 자신의** 디바이스만 관리할 수 있습니다
- `openclaw devices rotate --scope ...`는
  호출자 세션이 이미 보유한 operator 범위만 요청할 수 있습니다

관련 항목:

- [/web/control-ui](/web/control-ui)
- [/gateway/configuration](/gateway/configuration) (gateway auth 모드)
- [/gateway/trusted-proxy-auth](/gateway/trusted-proxy-auth)
- [/gateway/remote](/gateway/remote)
- [/cli/devices](/cli/devices)

## Gateway 서비스가 실행되지 않음

서비스는 설치되어 있지만 프로세스가 계속 살아 있지 않을 때 이 섹션을 사용하세요.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep   # 시스템 수준 서비스도 스캔
```

확인할 사항:

- 종료 힌트와 함께 `Runtime: stopped`.
- 서비스 config 불일치(`Config (cli)` 대 `Config (service)`).
- 포트/리스너 충돌.
- `--deep` 사용 시 추가 launchd/systemd/schtasks 설치.
- `Other gateway-like services detected (best effort)` 정리 힌트.

일반적인 징후:

- `Gateway start blocked: set gateway.mode=local` 또는 `existing config is missing gateway.mode` → 로컬 gateway 모드가 활성화되지 않았거나 config 파일이 덮어써져 `gateway.mode`를 잃었습니다. 해결: config에서 `gateway.mode="local"`을 설정하거나 `openclaw onboard --mode local` / `openclaw setup`을 다시 실행해 예상되는 로컬 모드 config를 다시 기록하세요. Podman을 통해 OpenClaw를 실행 중이라면 기본 config 경로는 `~/.openclaw/openclaw.json`입니다.
- `refusing to bind gateway ... without auth` → 유효한 gateway auth 경로(token/password, 또는 구성된 trusted-proxy) 없이 비-loopback 바인딩.
- `another gateway instance is already listening` / `EADDRINUSE` → 포트 충돌.
- `Other gateway-like services detected (best effort)` → 오래되었거나 병렬인 launchd/systemd/schtasks 유닛이 존재합니다. 대부분의 설정에서는 머신당 gateway 하나를 유지해야 합니다. 둘 이상이 필요하다면 포트 + config/상태/워크스페이스를 분리하세요. [/gateway#multiple-gateways-same-host](/gateway#multiple-gateways-same-host)를 참조하세요.

관련 항목:

- [/gateway/background-process](/gateway/background-process)
- [/gateway/configuration](/gateway/configuration)
- [/gateway/doctor](/gateway/doctor)

## Gateway 프로브 경고

`openclaw gateway probe`가 무언가에 도달했지만 여전히 경고 블록을 출력할 때 이 섹션을 사용하세요.

```bash
openclaw gateway probe
openclaw gateway probe --json
openclaw gateway probe --ssh user@gateway-host
```

확인할 사항:

- JSON 출력의 `warnings[].code` 및 `primaryTargetId`.
- 경고가 SSH fallback, 여러 gateway, 누락된 범위, 확인되지 않은 auth ref와 관련되어 있는지 여부.

일반적인 징후:

- `SSH tunnel failed to start; falling back to direct probes.` → SSH 설정이 실패했지만, 명령은 여전히 직접 구성된/loopback 대상을 시도했습니다.
- `multiple reachable gateways detected` → 둘 이상의 대상이 응답했습니다. 일반적으로 의도된 멀티 gateway 설정이거나 오래되었거나 중복된 리스너를 의미합니다.
- `Probe diagnostics are limited by gateway scopes (missing operator.read)` → 연결은 되었지만 세부 RPC가 범위 제한을 받습니다. 디바이스 신원을 페어링하거나 `operator.read`가 있는 자격 증명을 사용하세요.
- 확인되지 않은 `gateway.auth.*` / `gateway.remote.*` SecretRef 경고 텍스트 → 실패한 대상에 대해 이 명령 경로에서 auth 자료를 사용할 수 없었습니다.

관련 항목:

- [/cli/gateway](/cli/gateway)
- [/gateway#multiple-gateways-same-host](/gateway#multiple-gateways-same-host)
- [/gateway/remote](/gateway/remote)

## 채널은 연결되었지만 메시지가 흐르지 않음

채널 상태는 연결됨인데 메시지 흐름이 멈췄다면 정책, 권한, 채널별 전달 규칙에 집중하세요.

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

확인할 사항:

- DM 정책(`pairing`, `allowlist`, `open`, `disabled`).
- 그룹 허용 목록 및 멘션 요구 사항.
- 누락된 채널 API 권한/범위.

일반적인 징후:

- `mention required` → 그룹 멘션 정책에 의해 메시지가 무시됨.
- `pairing` / 대기 중 승인 흔적 → 발신자가 승인되지 않음.
- `missing_scope`, `not_in_channel`, `Forbidden`, `401/403` → 채널 auth/권한 문제.

관련 항목:

- [/channels/troubleshooting](/channels/troubleshooting)
- [/channels/whatsapp](/channels/whatsapp)
- [/channels/telegram](/channels/telegram)
- [/channels/discord](/channels/discord)

## Cron 및 heartbeat 전달

cron 또는 heartbeat가 실행되지 않았거나 전달되지 않았다면, 먼저 스케줄러 상태를 확인한 다음 전달 대상을 확인하세요.

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

확인할 사항:

- cron이 활성화되어 있고 다음 깨우기가 존재하는지.
- 작업 실행 기록 상태(`ok`, `skipped`, `error`).
- heartbeat 건너뜀 이유(`quiet-hours`, `requests-in-flight`, `alerts-disabled`, `empty-heartbeat-file`, `no-tasks-due`).

일반적인 징후:

- `cron: scheduler disabled; jobs will not run automatically` → cron 비활성화.
- `cron: timer tick failed` → 스케줄러 tick 실패; 파일/로그/런타임 오류를 확인하세요.
- `heartbeat skipped`와 `reason=quiet-hours` → 활성 시간 창 밖입니다.
- `heartbeat skipped`와 `reason=empty-heartbeat-file` → `HEARTBEAT.md`가 존재하지만 빈 줄/markdown 헤더만 포함하므로 OpenClaw가 모델 호출을 건너뜁니다.
- `heartbeat skipped`와 `reason=no-tasks-due` → `HEARTBEAT.md`에 `tasks:` 블록이 있지만, 이번 tick에서 기한이 된 작업이 없습니다.
- `heartbeat: unknown accountId` → heartbeat 전달 대상에 잘못된 계정 id.
- `heartbeat skipped`와 `reason=dm-blocked` → heartbeat 대상이 DM 스타일 대상으로 해석되었지만 `agents.defaults.heartbeat.directPolicy`(또는 agent별 재정의)가 `block`으로 설정되어 있습니다.

관련 항목:

- [/automation/cron-jobs#troubleshooting](/automation/cron-jobs#troubleshooting)
- [/automation/cron-jobs](/automation/cron-jobs)
- [/gateway/heartbeat](/gateway/heartbeat)

## node가 페어링되었지만 도구가 실패함

node는 페어링되었지만 도구가 실패하면 foreground, 권한, 승인 상태를 분리해서 점검하세요.

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

확인할 사항:

- 예상된 capability와 함께 node가 온라인 상태인지.
- 카메라/마이크/위치/화면에 대한 OS 권한 부여.
- exec 승인 및 허용 목록 상태.

일반적인 징후:

- `NODE_BACKGROUND_UNAVAILABLE` → node 앱이 foreground에 있어야 합니다.
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → OS 권한 누락.
- `SYSTEM_RUN_DENIED: approval required` → exec 승인 대기 중.
- `SYSTEM_RUN_DENIED: allowlist miss` → 허용 목록에 의해 명령 차단됨.

관련 항목:

- [/nodes/troubleshooting](/nodes/troubleshooting)
- [/nodes/index](/nodes/index)
- [/tools/exec-approvals](/tools/exec-approvals)

## Browser 도구가 실패함

gateway 자체는 정상인데 browser 도구 작업이 실패할 때 이 섹션을 사용하세요.

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

확인할 사항:

- `plugins.allow`가 설정되어 있고 `browser`를 포함하는지.
- 유효한 browser 실행 파일 경로.
- CDP profile 도달 가능성.
- `existing-session` / `user` profile용 로컬 Chrome 사용 가능 여부.

일반적인 징후:

- `unknown command "browser"` 또는 `unknown command 'browser'` → 번들 browser plugin이 `plugins.allow`에 의해 제외됨.
- `browser.enabled=true`인데 browser 도구가 없거나 사용할 수 없음 → `plugins.allow`가 `browser`를 제외하여 plugin이 로드되지 않음.
- `Failed to start Chrome CDP on port` → browser 프로세스 시작 실패.
- `browser.executablePath not found` → 구성된 경로가 잘못됨.
- `browser.cdpUrl must be http(s) or ws(s)` → 구성된 CDP URL이 `file:` 또는 `ftp:` 같은 지원되지 않는 스킴을 사용함.
- `browser.cdpUrl has invalid port` → 구성된 CDP URL에 잘못되었거나 범위를 벗어난 포트가 있음.
- `No Chrome tabs found for profile="user"` → Chrome MCP 연결 profile에 열려 있는 로컬 Chrome 탭이 없음.
- `Remote CDP for profile "<name>" is not reachable` → 구성된 원격 CDP 엔드포인트에 gateway 호스트에서 도달할 수 없음.
- `Browser attachOnly is enabled ... not reachable` 또는 `Browser attachOnly is enabled and CDP websocket ... is not reachable` → attach-only profile에 도달 가능한 대상이 없거나, HTTP 엔드포인트는 응답했지만 CDP WebSocket은 여전히 열 수 없음.
- `Playwright is not available in this gateway build; '<feature>' is unsupported.` → 현재 gateway 설치에 전체 Playwright 패키지가 없습니다. ARIA 스냅샷과 기본 페이지 스크린샷은 여전히 작동할 수 있지만, 탐색, AI 스냅샷, CSS 선택자 기반 요소 스크린샷, PDF 내보내기는 계속 사용할 수 없습니다.
- `fullPage is not supported for element screenshots` → 스크린샷 요청에서 `--full-page`와 `--ref` 또는 `--element`를 함께 사용함.
- `element screenshots are not supported for existing-session profiles; use ref from snapshot.` → Chrome MCP / `existing-session` 스크린샷 호출은 CSS `--element`가 아니라 페이지 캡처 또는 스냅샷 `--ref`를 사용해야 합니다.
- `existing-session file uploads do not support element selectors; use ref/inputRef.` → Chrome MCP 업로드 hook은 CSS 선택자가 아니라 스냅샷 ref가 필요합니다.
- `existing-session file uploads currently support one file at a time.` → Chrome MCP profile에서는 호출당 업로드 하나만 보내세요.
- `existing-session dialog handling does not support timeoutMs.` → Chrome MCP profile의 dialog hook은 timeout 재정의를 지원하지 않습니다.
- `response body is not supported for existing-session profiles yet.` → `responsebody`는 여전히 관리형 browser 또는 원시 CDP profile이 필요합니다.
- attach-only 또는 remote CDP profile에서 오래된 viewport / dark-mode / locale / offline 재정의 → `openclaw browser stop --browser-profile <name>`을 실행해 전체 gateway를 재시작하지 않고도 활성 제어 세션을 닫고 Playwright/CDP 에뮬레이션 상태를 해제하세요.

관련 항목:

- [/tools/browser-linux-troubleshooting](/tools/browser-linux-troubleshooting)
- [/tools/browser](/tools/browser)

## 업그레이드 후 갑자기 문제가 생긴 경우

업그레이드 후 대부분의 문제는 config 드리프트이거나 이제 더 엄격한 기본값이 적용되기 때문입니다.

### 1) Auth 및 URL 재정의 동작이 변경됨

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

확인할 사항:

- `gateway.mode=remote`이면 로컬 서비스는 정상인데 CLI 호출이 원격을 대상으로 할 수 있습니다.
- 명시적 `--url` 호출은 저장된 자격 증명으로 fallback하지 않습니다.

일반적인 징후:

- `gateway connect failed:` → 잘못된 URL 대상.
- `unauthorized` → 엔드포인트에는 도달했지만 auth가 잘못됨.

### 2) 바인딩 및 auth 가드레일이 더 엄격해짐

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

확인할 사항:

- 비-loopback 바인딩(`lan`, `tailnet`, `custom`)은 유효한 gateway auth 경로가 필요합니다: 공유 token/password auth 또는 올바르게 구성된 비-loopback `trusted-proxy` 배포.
- `gateway.token` 같은 이전 키는 `gateway.auth.token`을 대체하지 않습니다.

일반적인 징후:

- `refusing to bind gateway ... without auth` → 유효한 gateway auth 경로 없이 비-loopback 바인딩.
- 런타임은 실행 중인데 `RPC probe: failed` → gateway는 살아 있지만 현재 auth/url로는 접근할 수 없음.

### 3) 페어링 및 디바이스 신원 상태가 변경됨

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

확인할 사항:

- dashboard/node에 대한 대기 중 디바이스 승인.
- 정책 또는 신원 변경 후 대기 중인 DM 페어링 승인.

일반적인 징후:

- `device identity required` → 디바이스 auth 조건이 충족되지 않음.
- `pairing required` → 발신자/디바이스를 승인해야 함.

검사 후에도 서비스 config와 런타임이 계속 다르면, 같은 profile/상태 디렉터리에서 서비스 메타데이터를 다시 설치하세요.

```bash
openclaw gateway install --force
openclaw gateway restart
```

관련 항목:

- [/gateway/pairing](/gateway/pairing)
- [/gateway/authentication](/gateway/authentication)
- [/gateway/background-process](/gateway/background-process)
