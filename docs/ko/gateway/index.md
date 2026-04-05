---
read_when:
    - 게이트웨이 프로세스를 실행하거나 디버깅할 때
summary: 게이트웨이 서비스, 수명 주기 및 운영을 위한 운영 문서
title: 게이트웨이 운영 문서
x-i18n:
    generated_at: "2026-04-05T12:42:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0ec17674370de4e171779389c83580317308a4f07ebf335ad236a47238af18e1
    source_path: gateway/index.md
    workflow: 15
---

# 게이트웨이 운영 문서

이 페이지는 게이트웨이 서비스의 Day 1 시작 및 Day 2 운영에 사용하세요.

<CardGroup cols={2}>
  <Card title="심층 문제 해결" icon="siren" href="/gateway/troubleshooting">
    정확한 명령 순서와 로그 시그니처를 포함한 증상 중심 진단.
  </Card>
  <Card title="구성" icon="sliders" href="/gateway/configuration">
    작업 중심 설정 가이드 + 전체 구성 참조.
  </Card>
  <Card title="Secrets 관리" icon="key-round" href="/gateway/secrets">
    SecretRef 계약, 런타임 스냅샷 동작, 마이그레이션/리로드 작업.
  </Card>
  <Card title="Secrets 계획 계약" icon="shield-check" href="/gateway/secrets-plan-contract">
    정확한 `secrets apply` 대상/경로 규칙과 ref 전용 인증 프로필 동작.
  </Card>
</CardGroup>

## 5분 로컬 시작

<Steps>
  <Step title="게이트웨이 시작">

```bash
openclaw gateway --port 18789
# debug/trace가 stdio로 미러링됨
openclaw gateway --port 18789 --verbose
# 선택한 포트의 리스너를 강제 종료한 뒤 시작
openclaw gateway --force
```

  </Step>

  <Step title="서비스 상태 확인">

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
```

정상 기준: `Runtime: running` 및 `RPC probe: ok`.

  </Step>

  <Step title="채널 준비 상태 검증">

```bash
openclaw channels status --probe
```

도달 가능한 게이트웨이가 있으면 이 명령은 지원되는 경우 계정별 실시간 채널 프로브와 선택적 감사를 실행합니다.
게이트웨이에 도달할 수 없으면 CLI는 실시간 프로브 출력 대신 config 전용 채널 요약으로 대체합니다.

  </Step>
</Steps>

<Note>
게이트웨이 config 리로드는 활성 config 파일 경로를 감시합니다(프로필/상태 기본값에서 해석되거나, 설정된 경우 `OPENCLAW_CONFIG_PATH`).
기본 모드는 `gateway.reload.mode="hybrid"`입니다.
첫 번째 성공적인 로드 후, 실행 중인 프로세스는 활성 메모리 내 config 스냅샷을 제공하며, 성공적인 리로드는 해당 스냅샷을 원자적으로 교체합니다.
</Note>

## 런타임 모델

- 라우팅, 제어 평면, 채널 연결을 위한 하나의 상시 실행 프로세스
- 다음을 위한 단일 다중화 포트:
  - WebSocket 제어/RPC
  - HTTP API, OpenAI 호환 (`/v1/models`, `/v1/embeddings`, `/v1/chat/completions`, `/v1/responses`, `/tools/invoke`)
  - 제어 UI 및 hooks
- 기본 바인드 모드: `loopback`
- 기본적으로 인증이 필요합니다. 공유 비밀 설정은
  `gateway.auth.token` / `gateway.auth.password`(또는
  `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`)를 사용하며, non-loopback
  reverse-proxy 설정은 `gateway.auth.mode: "trusted-proxy"`를 사용할 수 있습니다.

## OpenAI 호환 엔드포인트

OpenClaw의 가장 활용도 높은 호환성 표면은 현재 다음과 같습니다:

- `GET /v1/models`
- `GET /v1/models/{id}`
- `POST /v1/embeddings`
- `POST /v1/chat/completions`
- `POST /v1/responses`

이 세트가 중요한 이유:

- 대부분의 Open WebUI, LobeChat, LibreChat 통합은 먼저 `/v1/models`를 확인합니다.
- 많은 RAG 및 메모리 파이프라인은 `/v1/embeddings`를 기대합니다.
- 에이전트 중심 클라이언트는 점점 더 `/v1/responses`를 선호합니다.

계획 참고:

- `/v1/models`는 agent 우선입니다. `openclaw`, `openclaw/default`, `openclaw/<agentId>`를 반환합니다.
- `openclaw/default`는 항상 구성된 기본 agent에 매핑되는 안정적인 별칭입니다.
- 백엔드 provider/모델 재정의가 필요하면 `x-openclaw-model`을 사용하세요. 그렇지 않으면 선택된 agent의 일반 모델 및 임베딩 설정이 계속 제어권을 가집니다.

이 모든 항목은 메인 게이트웨이 포트에서 실행되며, 나머지 게이트웨이 HTTP API와 동일한 신뢰된 운영자 인증 경계를 사용합니다.

### 포트 및 바인드 우선순위

| 설정 | 해석 순서 |
| ------------ | ------------------------------------------------------------- |
| 게이트웨이 포트 | `--port` → `OPENCLAW_GATEWAY_PORT` → `gateway.port` → `18789` |
| 바인드 모드 | CLI/override → `gateway.bind` → `loopback` |

### 핫 리로드 모드

| `gateway.reload.mode` | 동작 |
| --------------------- | ------------------------------------------ |
| `off`                 | config 리로드 없음 |
| `hot`                 | 핫 세이프 변경만 적용 |
| `restart`             | 리로드가 필요한 변경 시 재시작 |
| `hybrid` (기본값)    | 안전하면 핫 적용, 필요하면 재시작 |

## 운영자 명령 세트

```bash
openclaw gateway status
openclaw gateway status --deep   # 시스템 수준 서비스 스캔 추가
openclaw gateway status --json
openclaw gateway install
openclaw gateway restart
openclaw gateway stop
openclaw secrets reload
openclaw logs --follow
openclaw doctor
```

`gateway status --deep`는 추가 서비스 검색용입니다(LaunchDaemons/systemd system
units/schtasks). 더 깊은 RPC 상태 프로브가 아닙니다.

## 다중 게이트웨이(동일 호스트)

대부분의 설치는 머신당 하나의 게이트웨이를 실행해야 합니다. 단일 게이트웨이로 여러
agents와 channels를 호스팅할 수 있습니다.

다중 게이트웨이는 의도적으로 격리 또는 구조용 봇이 필요할 때만 필요합니다.

유용한 점검:

```bash
openclaw gateway status --deep
openclaw gateway probe
```

예상되는 동작:

- `gateway status --deep`는 `Other gateway-like services detected (best effort)`를 보고하고
  오래된 launchd/systemd/schtasks 설치가 남아 있을 때 정리 힌트를 출력할 수 있습니다.
- `gateway probe`는 둘 이상의 대상이 응답하면 `multiple reachable gateways`를 경고할 수 있습니다.
- 이것이 의도된 경우 게이트웨이별로 포트, config/상태, 워크스페이스 루트를 분리하세요.

자세한 설정: [/gateway/multiple-gateways](/gateway/multiple-gateways).

## 원격 접근

권장: Tailscale/VPN.
대체: SSH 터널.

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

그런 다음 클라이언트를 로컬의 `ws://127.0.0.1:18789`에 연결합니다.

<Warning>
SSH 터널은 게이트웨이 인증을 우회하지 않습니다. 공유 비밀 인증의 경우 클라이언트는
터널을 통해서도 여전히 `token`/`password`를 보내야 합니다. ID 기반 모드의 경우에도
요청은 여전히 해당 인증 경로를 충족해야 합니다.
</Warning>

참조: [원격 게이트웨이](/gateway/remote), [인증](/gateway/authentication), [Tailscale](/gateway/tailscale).

## 감독 및 서비스 수명 주기

프로덕션 수준의 신뢰성을 위해 감독된 실행을 사용하세요.

<Tabs>
  <Tab title="macOS (launchd)">

```bash
openclaw gateway install
openclaw gateway status
openclaw gateway restart
openclaw gateway stop
```

LaunchAgent 레이블은 `ai.openclaw.gateway`(기본) 또는 `ai.openclaw.<profile>`(이름 있는 프로필)입니다. `openclaw doctor`는 서비스 config 드리프트를 감사하고 복구합니다.

  </Tab>

  <Tab title="Linux (systemd user)">

```bash
openclaw gateway install
systemctl --user enable --now openclaw-gateway[-<profile>].service
openclaw gateway status
```

로그아웃 후에도 유지하려면 lingering을 활성화하세요:

```bash
sudo loginctl enable-linger <user>
```

사용자 지정 설치 경로가 필요할 때의 수동 user-unit 예시:

```ini
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group

[Install]
WantedBy=default.target
```

  </Tab>

  <Tab title="Windows (native)">

```powershell
openclaw gateway install
openclaw gateway status --json
openclaw gateway restart
openclaw gateway stop
```

기본 Windows 관리형 시작은 `OpenClaw Gateway`
(또는 이름 있는 프로필의 경우 `OpenClaw Gateway (<profile>)`)라는 이름의 Scheduled Task를 사용합니다. Scheduled Task
생성이 거부되면 OpenClaw는 상태 디렉터리의 `gateway.cmd`를 가리키는 사용자별 Startup 폴더 실행기로 대체합니다.

  </Tab>

  <Tab title="Linux (system service)">

다중 사용자/상시 실행 호스트에는 system unit를 사용하세요.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-gateway[-<profile>].service
```

사용자 unit와 동일한 서비스 본문을 사용하되,
`/etc/systemd/system/openclaw-gateway[-<profile>].service` 아래에 설치하고
`openclaw` 바이너리가 다른 위치에 있다면 `ExecStart=`를 조정하세요.

  </Tab>
</Tabs>

## 한 호스트에서 여러 게이트웨이

대부분의 설정은 **하나의** 게이트웨이를 실행해야 합니다.
엄격한 격리/중복성(예: 구조용 프로필)을 위해서만 여러 개를 사용하세요.

인스턴스별 체크리스트:

- 고유한 `gateway.port`
- 고유한 `OPENCLAW_CONFIG_PATH`
- 고유한 `OPENCLAW_STATE_DIR`
- 고유한 `agents.defaults.workspace`

예시:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json OPENCLAW_STATE_DIR=~/.openclaw-a openclaw gateway --port 19001
OPENCLAW_CONFIG_PATH=~/.openclaw/b.json OPENCLAW_STATE_DIR=~/.openclaw-b openclaw gateway --port 19002
```

참조: [다중 게이트웨이](/gateway/multiple-gateways).

### 개발 프로필 빠른 경로

```bash
openclaw --dev setup
openclaw --dev gateway --allow-unconfigured
openclaw --dev status
```

기본값에는 격리된 상태/config와 기본 게이트웨이 포트 `19001`이 포함됩니다.

## 프로토콜 빠른 참조(운영자 관점)

- 첫 번째 클라이언트 프레임은 반드시 `connect`여야 합니다.
- 게이트웨이는 `hello-ok` 스냅샷(`presence`, `health`, `stateVersion`, `uptimeMs`, limits/policy)을 반환합니다.
- `hello-ok.features.methods` / `events`는
  호출 가능한 모든 헬퍼 경로를 생성 덤프로 나열한 것이 아니라 보수적인 검색 목록입니다.
- 요청: `req(method, params)` → `res(ok/payload|error)`.
- 일반적인 이벤트에는 `connect.challenge`, `agent`, `chat`,
  `session.message`, `session.tool`, `sessions.changed`, `presence`, `tick`,
  `health`, `heartbeat`, pairing/approval 수명 주기 이벤트, `shutdown`이 포함됩니다.

Agent 실행은 2단계입니다:

1. 즉시 수락 ack (`status:"accepted"`)
2. 최종 완료 응답 (`status:"ok"|"error"`), 그 사이에 스트리밍된 `agent` 이벤트

전체 프로토콜 문서: [게이트웨이 프로토콜](/gateway/protocol).

## 운영 점검

### 라이브니스

- WS를 열고 `connect`를 보냅니다.
- 스냅샷이 포함된 `hello-ok` 응답을 기대합니다.

### 레디니스

```bash
openclaw gateway status
openclaw channels status --probe
openclaw health
```

### 간극 복구

이벤트는 재생되지 않습니다. 시퀀스 간극이 있으면 계속하기 전에 상태를 새로 고치세요(`health`, `system-presence`).

## 일반적인 실패 시그니처

| 시그니처 | 가능성이 높은 문제 |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `refusing to bind gateway ... without auth`                    | 유효한 게이트웨이 인증 경로 없이 non-loopback 바인드 시도 |
| `another gateway instance is already listening` / `EADDRINUSE` | 포트 충돌 |
| `Gateway start blocked: set gateway.mode=local`                | config가 원격 모드로 설정되었거나 손상된 config에서 로컬 모드 표시가 누락됨 |
| `unauthorized` during connect                                  | 클라이언트와 게이트웨이 간 인증 불일치 |

전체 진단 순서는 [게이트웨이 문제 해결](/gateway/troubleshooting)을 사용하세요.

## 안전 보장

- 게이트웨이 프로토콜 클라이언트는 게이트웨이를 사용할 수 없을 때 즉시 실패합니다(암묵적인 직접 채널 대체 없음).
- 잘못된/non-connect 첫 프레임은 거부되고 연결이 닫힙니다.
- 정상 종료 시 소켓이 닫히기 전에 `shutdown` 이벤트를 보냅니다.

---

관련 문서:

- [문제 해결](/gateway/troubleshooting)
- [백그라운드 프로세스](/gateway/background-process)
- [구성](/gateway/configuration)
- [상태](/gateway/health)
- [Doctor](/gateway/doctor)
- [인증](/gateway/authentication)
