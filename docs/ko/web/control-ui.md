---
read_when:
    - 브라우저에서 Gateway를 운영하려는 경우
    - SSH 터널 없이 Tailnet 액세스를 원할 경우
summary: Gateway용 브라우저 기반 Control UI(채팅, 노드, 구성)
title: Control UI
x-i18n:
    generated_at: "2026-04-05T12:59:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1568680a07907343352dbb3a2e6a1b896826404a7d8baba62512f03eac28e3d7
    source_path: web/control-ui.md
    workflow: 15
---

# Control UI (브라우저)

Control UI는 Gateway가 제공하는 작은 **Vite + Lit** 단일 페이지 앱입니다:

- 기본값: `http://<host>:18789/`
- 선택적 접두사: `gateway.controlUi.basePath` 설정(예: `/openclaw`)

이 UI는 같은 포트에서 **Gateway WebSocket에 직접 연결**합니다.

## 빠르게 열기(local)

Gateway가 같은 컴퓨터에서 실행 중이라면 다음을 여세요:

- [http://127.0.0.1:18789/](http://127.0.0.1:18789/) (또는 [http://localhost:18789/](http://localhost:18789/))

페이지가 로드되지 않으면 먼저 Gateway를 시작하세요: `openclaw gateway`.

인증은 WebSocket 핸드셰이크 중 다음을 통해 제공됩니다:

- `connect.params.auth.token`
- `connect.params.auth.password`
- `gateway.auth.allowTailscale: true`일 때의 Tailscale Serve ID 헤더
- `gateway.auth.mode: "trusted-proxy"`일 때의 trusted-proxy ID 헤더

대시보드 설정 패널은 현재 브라우저 탭 세션과 선택한 gateway URL에 대한 토큰을 유지하며,
비밀번호는 저장하지 않습니다. 온보딩은 일반적으로 첫 연결 시
공유 비밀 인증을 위한 gateway 토큰을 생성하지만, `gateway.auth.mode`가 `"password"`일 때는
비밀번호 인증도 동작합니다.

## 디바이스 페어링(첫 연결)

새 브라우저나 새 디바이스에서 Control UI에 연결하면 Gateway는
**1회성 페어링 승인**을 요구합니다. `gateway.auth.allowTailscale: true`로
같은 Tailnet에 있더라도 마찬가지입니다. 이는 무단 액세스를 방지하기 위한 보안 조치입니다.

**표시되는 내용:** `"disconnected (1008): pairing required"`

**디바이스 승인 방법:**

```bash
# 대기 중인 요청 목록
openclaw devices list

# 요청 ID로 승인
openclaw devices approve <requestId>
```

브라우저가 변경된 인증 정보(role/scopes/public
key)로 페어링을 다시 시도하면 이전 대기 요청은 대체되고 새로운 `requestId`가
생성됩니다. 승인 전에 `openclaw devices list`를 다시 실행하세요.

한 번 승인되면 해당 디바이스는 기억되며,
`openclaw devices revoke --device <id> --role <role>`로 취소하지 않는 한 다시 승인할 필요가 없습니다. 토큰 회전과 취소는
[Devices CLI](/cli/devices)를 참조하세요.

**참고:**

- 직접 local loopback 브라우저 연결(`127.0.0.1` / `localhost`)은
  자동 승인됩니다.
- Tailnet 및 LAN 브라우저 연결은 같은 머신에서 시작되더라도 여전히
  명시적 승인이 필요합니다.
- 각 브라우저 프로필은 고유한 디바이스 ID를 생성하므로, 브라우저를 바꾸거나
  브라우저 데이터를 지우면 다시 페어링해야 합니다.

## 언어 지원

Control UI는 첫 로드 시 브라우저 로캘을 기준으로 자체적으로 현지화할 수 있으며, 이후에는 Access 카드의 언어 선택기에서 이를 재정의할 수 있습니다.

- 지원 로캘: `en`, `zh-CN`, `zh-TW`, `pt-BR`, `de`, `es`
- 영어가 아닌 번역은 브라우저에서 지연 로드됩니다.
- 선택한 로캘은 브라우저 저장소에 저장되어 이후 방문 시 재사용됩니다.
- 누락된 번역 키는 영어로 대체됩니다.

## 현재 가능한 작업

- Gateway WS를 통한 모델 채팅 (`chat.history`, `chat.send`, `chat.abort`, `chat.inject`)
- Chat에서 도구 호출 스트리밍 + 실시간 도구 출력 카드(agent 이벤트)
- 채널: 내장 + 번들/외부 plugin 채널 상태, QR 로그인, 채널별 구성 (`channels.status`, `web.login.*`, `config.patch`)
- 인스턴스: presence 목록 + 새로고침 (`system-presence`)
- 세션: 목록 + 세션별 model/thinking/fast/verbose/reasoning 재정의 (`sessions.list`, `sessions.patch`)
- Cron 작업: 목록/추가/편집/실행/활성화/비활성화 + 실행 기록 (`cron.*`)
- Skills: 상태, 활성화/비활성화, 설치, API 키 업데이트 (`skills.*`)
- 노드: 목록 + caps (`node.list`)
- Exec 승인: `exec host=gateway/node`용 gateway 또는 node allowlist + ask 정책 편집 (`exec.approvals.*`)
- 구성: `~/.openclaw/openclaw.json` 보기/편집 (`config.get`, `config.set`)
- 구성: 검증과 함께 적용 + 재시작 (`config.apply`) 및 마지막 활성 세션 깨우기
- 구성 쓰기에는 동시 편집 덮어쓰기를 방지하는 base-hash 가드가 포함됨
- 구성 쓰기(`config.set`/`config.apply`/`config.patch`)는 제출된 구성 페이로드 안의 ref에 대해 활성 SecretRef 확인도 사전 수행하며, 확인할 수 없는 활성 제출 ref는 쓰기 전에 거부됨
- 구성 스키마 + 폼 렌더링 (`config.schema` / `config.schema.lookup`,
  필드 `title` / `description`, 일치하는 UI 힌트, 즉시 하위 항목
  요약, 중첩 object/wildcard/array/composition 노드의 문서 메타데이터,
  사용 가능한 경우 plugin + channel 스키마 포함). Raw JSON 편집기는
  스냅샷이 안전한 raw 왕복을 지원할 때만 사용 가능
- 스냅샷이 raw 텍스트로 안전하게 왕복할 수 없으면 Control UI는 Form 모드를 강제하고 해당 스냅샷에 대해 Raw 모드를 비활성화함
- 구조화된 SecretRef 객체 값은 실수로 객체가 문자열로 손상되는 일을 막기 위해 폼 텍스트 입력에서 읽기 전용으로 렌더링됨
- 디버그: 상태/헬스/모델 스냅샷 + 이벤트 로그 + 수동 RPC 호출 (`status`, `health`, `models.list`)
- 로그: 필터/내보내기가 가능한 gateway 파일 로그 실시간 tail (`logs.tail`)
- 업데이트: 패키지/git 업데이트 + 재시작 실행 (`update.run`) 및 재시작 보고서

Cron 작업 패널 참고:

- 격리된 작업의 경우 전달 기본값은 요약 알림입니다. 내부 전용 실행을 원하면 none으로 전환할 수 있습니다.
- announce가 선택되면 channel/target 필드가 표시됩니다.
- Webhook 모드는 `delivery.mode = "webhook"`을 사용하며 `delivery.to`를 유효한 HTTP(S) webhook URL로 설정합니다.
- main-session 작업에서는 webhook 및 none 전달 모드를 사용할 수 있습니다.
- 고급 편집 컨트롤에는 실행 후 삭제, agent 재정의 지우기, cron exact/stagger 옵션,
  agent model/thinking 재정의, best-effort 전달 토글이 포함됩니다.
- 폼 검증은 필드 수준 오류와 함께 인라인으로 수행되며, 잘못된 값이 있으면 수정될 때까지 저장 버튼이 비활성화됩니다.
- 전용 bearer 토큰을 보내려면 `cron.webhookToken`을 설정하세요. 생략하면 webhook은 인증 헤더 없이 전송됩니다.
- deprecated fallback: `notify: true`가 저장된 레거시 작업은 마이그레이션 전까지 여전히 `cron.webhook`을 사용할 수 있습니다.

## 채팅 동작

- `chat.send`는 **non-blocking**입니다. 즉시 `{ runId, status: "started" }`로 응답하고, 답변은 `chat` 이벤트를 통해 스트리밍됩니다.
- 같은 `idempotencyKey`로 다시 보내면 실행 중에는 `{ status: "in_flight" }`, 완료 후에는 `{ status: "ok" }`를 반환합니다.
- `chat.history` 응답은 UI 안전을 위해 크기 제한이 있습니다. transcript 항목이 너무 크면 Gateway는 긴 텍스트 필드를 자르거나, 무거운 메타데이터 블록을 생략하거나, 너무 큰 메시지를 플레이스홀더(`"[chat.history omitted: message too large]"`)로 대체할 수 있습니다.
- `chat.history`는 표시 전용 인라인 directive 태그(예: `[[reply_to_*]]`, `[[audio_as_voice]]`), 일반 텍스트 도구 호출 XML 페이로드(`\<tool_call>...\</tool_call>`, `\<function_call>...\</function_call>`, `\<tool_calls>...\</tool_calls>`, `\<function_calls>...\</function_calls>`, 잘린 도구 호출 블록 포함), 유출된 ASCII/전각 모델 제어 토큰도 제거하며, 전체 표시 텍스트가 정확히 무음 토큰 `NO_REPLY` / `no_reply`뿐인 assistant 항목은 생략합니다.
- `chat.inject`는 세션 transcript에 assistant 메모를 추가하고 UI 전용 업데이트를 위해 `chat` 이벤트를 브로드캐스트합니다(agent 실행 없음, 채널 전달 없음).
- 채팅 헤더의 model 및 thinking 선택기는 `sessions.patch`를 통해 즉시 활성 세션을 패치합니다. 이것은 1회성 전송 옵션이 아니라 영구적인 세션 재정의입니다.
- 중지:
  - **Stop** 클릭(`chat.abort` 호출)
  - `/stop` 입력(또는 `stop`, `stop action`, `stop run`, `stop openclaw`, `please stop` 같은 독립 중단 문구)으로 out-of-band 중단
  - `chat.abort`는 `{ sessionKey }`(`runId` 없음)를 지원하며 해당 세션의 모든 활성 실행을 중단함
- 중단된 부분 출력 유지:
  - 실행이 중단되면 UI에는 부분 assistant 텍스트가 계속 표시될 수 있음
  - Gateway는 버퍼링된 출력이 있을 경우 중단된 부분 assistant 텍스트를 transcript 기록에 저장함
  - 저장된 항목에는 중단 메타데이터가 포함되어 transcript 소비자가 중단 부분 출력을 정상 완료 출력과 구분할 수 있음

## Tailnet 액세스(권장)

### 통합 Tailscale Serve(권장)

Gateway는 local loopback에 유지하고 Tailscale Serve가 HTTPS로 프록시하도록 하세요:

```bash
openclaw gateway --tailscale serve
```

열기:

- `https://<magicdns>/` (또는 구성된 `gateway.controlUi.basePath`)

기본적으로 Control UI/WebSocket Serve 요청은
`gateway.auth.allowTailscale`이 `true`일 때 Tailscale ID 헤더
(`tailscale-user-login`)를 통해 인증할 수 있습니다. OpenClaw는
`x-forwarded-for` 주소를 `tailscale whois`로 확인하고 이를 헤더와 일치시키며,
요청이 Tailscale의 `x-forwarded-*` 헤더와 함께 local loopback에 도달했을 때만 이를 허용합니다.
Serve 트래픽에도 명시적인 공유 비밀
자격 증명을 요구하려면 `gateway.auth.allowTailscale: false`로 설정하세요. 그런 다음
`gateway.auth.mode: "token"` 또는
`"password"`를 사용하세요.
이 비동기 Serve ID 경로에서는 동일한 클라이언트 IP와 인증 범위에 대한 실패한 인증 시도가
속도 제한 쓰기 전에 직렬화됩니다. 따라서 같은 브라우저에서 동시에 잘못 재시도하면
단순한 두 개의 불일치가 병렬로 경쟁하는 대신 두 번째 요청에서 `retry later`가 표시될 수 있습니다.
토큰 없는 Serve 인증은 gateway host를 신뢰한다고 가정합니다. 해당 호스트에서 신뢰할 수 없는 로컬 코드가 실행될 수 있다면 토큰/비밀번호 인증을 요구하세요.

### tailnet에 bind + 토큰

```bash
openclaw gateway --bind tailnet --token "$(openssl rand -hex 32)"
```

그런 다음 여세요:

- `http://<tailscale-ip>:18789/` (또는 구성된 `gateway.controlUi.basePath`)

일치하는 공유 비밀을 UI 설정에 붙여 넣으세요(`connect.params.auth.token` 또는 `connect.params.auth.password`로 전송됨).

## 안전하지 않은 HTTP

일반 HTTP(`http://<lan-ip>` 또는 `http://<tailscale-ip>`)로 대시보드를 열면,
브라우저는 **비보안 컨텍스트**에서 실행되며 WebCrypto를 차단합니다. 기본적으로
OpenClaw는 디바이스 ID가 없는 Control UI 연결을 **차단**합니다.

문서화된 예외:

- `gateway.controlUi.allowInsecureAuth=true`를 사용하는 localhost 전용 안전하지 않은 HTTP 호환성
- `gateway.auth.mode: "trusted-proxy"`를 통한 성공적인 운영자 Control UI 인증
- 비상용 `gateway.controlUi.dangerouslyDisableDeviceAuth=true`

**권장 해결책:** HTTPS(Tailscale Serve)를 사용하거나 UI를 로컬에서 여세요:

- `https://<magicdns>/` (Serve)
- `http://127.0.0.1:18789/` (gateway host에서)

**안전하지 않은 인증 토글 동작:**

```json5
{
  gateway: {
    controlUi: { allowInsecureAuth: true },
    bind: "tailnet",
    auth: { mode: "token", token: "replace-me" },
  },
}
```

`allowInsecureAuth`는 로컬 호환성 토글일 뿐입니다:

- 비보안 HTTP 컨텍스트의 localhost Control UI 세션이 디바이스 ID 없이 진행되도록 허용합니다.
- pairing 검사를 우회하지 않습니다.
- 원격(non-localhost) 디바이스 ID 요구 사항을 완화하지 않습니다.

**비상용 전용:**

```json5
{
  gateway: {
    controlUi: { dangerouslyDisableDeviceAuth: true },
    bind: "tailnet",
    auth: { mode: "token", token: "replace-me" },
  },
}
```

`dangerouslyDisableDeviceAuth`는 Control UI 디바이스 ID 검사를 비활성화하며,
심각한 보안 저하를 초래합니다. 긴급 사용 후에는 빠르게 되돌리세요.

Trusted-proxy 참고:

- 성공적인 trusted-proxy 인증은 디바이스 ID 없이도 **운영자** Control UI 세션을 허용할 수 있음
- 이는 node-role Control UI 세션에는 **적용되지 않음**
- 같은 호스트의 loopback 리버스 프록시는 여전히 trusted-proxy 인증을 충족하지 않음. 자세한 내용은
  [Trusted Proxy Auth](/ko/gateway/trusted-proxy-auth) 참조

HTTPS 설정 가이드는 [Tailscale](/ko/gateway/tailscale)를 참조하세요.

## UI 빌드하기

Gateway는 `dist/control-ui`의 정적 파일을 제공합니다. 다음으로 빌드하세요:

```bash
pnpm ui:build # 첫 실행 시 UI 종속성을 자동 설치
```

선택적 절대 base(고정 에셋 URL을 원할 때):

```bash
OPENCLAW_CONTROL_UI_BASE_PATH=/openclaw/ pnpm ui:build
```

로컬 개발(별도 dev 서버)의 경우:

```bash
pnpm ui:dev # 첫 실행 시 UI 종속성을 자동 설치
```

그런 다음 UI가 Gateway WS URL(예: `ws://127.0.0.1:18789`)을 가리키도록 하세요.

## 디버깅/테스트: dev 서버 + 원격 Gateway

Control UI는 정적 파일이며 WebSocket 대상은 구성 가능하고
HTTP origin과 달라도 됩니다. 이는 Vite dev 서버는 로컬에서 실행하고
Gateway는 다른 곳에서 실행할 때 유용합니다.

1. UI dev 서버 시작: `pnpm ui:dev`
2. 다음과 같은 URL 열기:

```text
http://localhost:5173/?gatewayUrl=ws://<gateway-host>:18789
```

선택적 1회성 인증(필요한 경우):

```text
http://localhost:5173/?gatewayUrl=wss://<gateway-host>:18789#token=<gateway-token>
```

참고:

- `gatewayUrl`은 로드 후 localStorage에 저장되고 URL에서는 제거됩니다.
- `token`은 가능하면 URL 프래그먼트(`#token=...`)를 통해 전달해야 합니다. 프래그먼트는 서버로 전송되지 않으므로 요청 로그 및 Referer 유출을 피할 수 있습니다. 레거시 `?token=` 쿼리 파라미터는 호환성을 위해 여전히 한 번 가져오지만, fallback으로만 사용되며 bootstrap 직후 즉시 제거됩니다.
- `password`는 메모리에만 유지됩니다.
- `gatewayUrl`이 설정되면 UI는 config 또는 환경 자격 증명으로 fallback하지 않습니다.
  `token`(또는 `password`)을 명시적으로 제공하세요. 명시적 자격 증명이 없으면 오류입니다.
- Gateway가 TLS(Tailscale Serve, HTTPS 프록시 등) 뒤에 있으면 `wss://`를 사용하세요.
- `gatewayUrl`은 클릭재킹을 방지하기 위해 최상위 창에서만 허용됩니다(임베드 불가).
- non-loopback Control UI 배포는 `gateway.controlUi.allowedOrigins`를 명시적으로 설정해야 합니다
  (전체 origin). 여기에는 원격 dev 설정도 포함됩니다.
- 강하게 제어된 로컬 테스트가 아닌 한 `gateway.controlUi.allowedOrigins: ["*"]`를 사용하지 마세요.
  이는 “지금 사용하는 호스트에 맞추기”가 아니라 임의의 브라우저 origin을 모두 허용한다는 뜻입니다.
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true`는
  Host-header origin fallback 모드를 활성화하지만, 이는 위험한 보안 모드입니다.

예시:

```json5
{
  gateway: {
    controlUi: {
      allowedOrigins: ["http://localhost:5173"],
    },
  },
}
```

원격 액세스 설정 세부 정보: [원격 액세스](/ko/gateway/remote).

## 관련

- [Dashboard](/web/dashboard) — gateway 대시보드
- [WebChat](/web/webchat) — 브라우저 기반 채팅 인터페이스
- [TUI](/web/tui) — 터미널 사용자 인터페이스
- [Health Checks](/ko/gateway/health) — gateway 상태 모니터링
