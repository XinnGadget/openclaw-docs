---
read_when:
    - CLI에서 Gateway를 실행할 때(개발 또는 서버)
    - Gateway 인증, 바인드 모드, 연결성을 디버깅할 때
    - Bonjour를 통해 Gateway를 발견할 때(local + wide-area DNS-SD)
summary: OpenClaw Gateway CLI(`openclaw gateway`) — Gateway 실행, 조회, 발견
title: gateway
x-i18n:
    generated_at: "2026-04-05T12:38:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: e311ded0dbad84b8212f0968f3563998d49c5e0eb292a0dc4b3bd3c22d4fa7f2
    source_path: cli/gateway.md
    workflow: 15
---

# Gateway CLI

Gateway는 OpenClaw의 WebSocket 서버입니다(채널, 노드, 세션, 훅).

이 페이지의 하위 명령은 `openclaw gateway …` 아래에 있습니다.

관련 문서:

- [/gateway/bonjour](/gateway/bonjour)
- [/gateway/discovery](/gateway/discovery)
- [/gateway/configuration](/gateway/configuration)

## Gateway 실행

로컬 Gateway 프로세스를 실행합니다:

```bash
openclaw gateway
```

포그라운드 별칭:

```bash
openclaw gateway run
```

참고:

- 기본적으로 Gateway는 `~/.openclaw/openclaw.json`에 `gateway.mode=local`이 설정되어 있지 않으면 시작을 거부합니다. 임시/개발 실행에는 `--allow-unconfigured`를 사용하세요.
- `openclaw onboard --mode local`과 `openclaw setup`은 `gateway.mode=local`을 기록해야 합니다. 파일은 존재하지만 `gateway.mode`가 없으면 이를 암묵적으로 local 모드로 가정하지 말고, 손상되었거나 덮어써진 구성으로 보고 복구해야 합니다.
- 파일이 존재하고 `gateway.mode`가 없으면, Gateway는 이를 의심스러운 구성 손상으로 간주하고 사용자를 위해 “local로 추측”하지 않습니다.
- 인증 없이 loopback을 넘어 바인딩하는 것은 차단됩니다(안전 가드레일).
- `SIGUSR1`은 권한이 있으면 프로세스 내부 재시작을 트리거합니다(`commands.restart`는 기본적으로 활성화되어 있으며, 수동 재시작을 막으려면 `commands.restart: false`로 설정하세요. 단, gateway tool/config apply/update는 계속 허용됩니다).
- `SIGINT`/`SIGTERM` 핸들러는 gateway 프로세스를 중지하지만, 사용자 지정 터미널 상태를 복원하지는 않습니다. CLI를 TUI 또는 raw-mode 입력으로 감싸는 경우 종료 전에 터미널을 복원하세요.

### 옵션

- `--port <port>`: WebSocket 포트(기본값은 config/env에서 오며, 일반적으로 `18789`)
- `--bind <loopback|lan|tailnet|auto|custom>`: 리스너 바인드 모드
- `--auth <token|password>`: 인증 모드 재정의
- `--token <token>`: 토큰 재정의(프로세스에 대해 `OPENCLAW_GATEWAY_TOKEN`도 설정)
- `--password <password>`: 비밀번호 재정의. 경고: 인라인 비밀번호는 로컬 프로세스 목록에 노출될 수 있습니다.
- `--password-file <path>`: 파일에서 gateway 비밀번호 읽기
- `--tailscale <off|serve|funnel>`: Tailscale을 통해 Gateway 노출
- `--tailscale-reset-on-exit`: 종료 시 Tailscale serve/funnel 구성 재설정
- `--allow-unconfigured`: config에 `gateway.mode=local`이 없어도 gateway 시작 허용. 이는 임시/개발 부트스트랩용 시작 가드를 우회할 뿐이며, config 파일을 기록하거나 복구하지는 않습니다.
- `--dev`: 없으면 개발용 config + workspace 생성(`BOOTSTRAP.md` 건너뜀)
- `--reset`: 개발용 config + 자격 증명 + 세션 + workspace 재설정(`--dev` 필요)
- `--force`: 시작 전에 선택한 포트의 기존 리스너 강제 종료
- `--verbose`: 자세한 로그
- `--cli-backend-logs`: 콘솔에 CLI 백엔드 로그만 표시(stdout/stderr도 활성화)
- `--claude-cli-logs`: `--cli-backend-logs`의 deprecated 별칭
- `--ws-log <auto|full|compact>`: websocket 로그 스타일(기본값 `auto`)
- `--compact`: `--ws-log compact`의 별칭
- `--raw-stream`: 원시 모델 스트림 이벤트를 jsonl로 기록
- `--raw-stream-path <path>`: 원시 스트림 jsonl 경로

## 실행 중인 Gateway 조회

모든 조회 명령은 WebSocket RPC를 사용합니다.

출력 모드:

- 기본값: 사람이 읽기 쉬운 형식(TTY에서는 색상 포함)
- `--json`: 기계가 읽기 쉬운 JSON(스타일/스피너 없음)
- `--no-color`(또는 `NO_COLOR=1`): 사람용 레이아웃은 유지하면서 ANSI 비활성화

공통 옵션(지원되는 경우):

- `--url <url>`: Gateway WebSocket URL
- `--token <token>`: Gateway 토큰
- `--password <password>`: Gateway 비밀번호
- `--timeout <ms>`: 타임아웃/예산(명령마다 다름)
- `--expect-final`: “final” 응답을 기다림(에이전트 호출)

참고: `--url`을 설정하면 CLI는 config 또는 환경 자격 증명으로 대체하지 않습니다.
`--token` 또는 `--password`를 명시적으로 전달하세요. 명시적 자격 증명이 없으면 오류입니다.

### `gateway health`

```bash
openclaw gateway health --url ws://127.0.0.1:18789
```

### `gateway usage-cost`

세션 로그에서 usage-cost 요약을 가져옵니다.

```bash
openclaw gateway usage-cost
openclaw gateway usage-cost --days 7
openclaw gateway usage-cost --json
```

옵션:

- `--days <days>`: 포함할 일 수(기본값 `30`)

### `gateway status`

`gateway status`는 Gateway 서비스(launchd/systemd/schtasks)와 선택적 RPC 프로브를 표시합니다.

```bash
openclaw gateway status
openclaw gateway status --json
openclaw gateway status --require-rpc
```

옵션:

- `--url <url>`: 명시적 프로브 대상을 추가합니다. 구성된 원격 + localhost도 계속 프로브됩니다.
- `--token <token>`: 프로브용 토큰 인증
- `--password <password>`: 프로브용 비밀번호 인증
- `--timeout <ms>`: 프로브 타임아웃(기본값 `10000`)
- `--no-probe`: RPC 프로브 건너뜀(서비스 전용 보기)
- `--deep`: 시스템 수준 서비스도 스캔
- `--require-rpc`: RPC 프로브가 실패하면 0이 아닌 값으로 종료. `--no-probe`와 함께 사용할 수 없습니다.

참고:

- `gateway status`는 로컬 CLI config가 없거나 잘못되어도 진단용으로 계속 사용할 수 있습니다.
- `gateway status`는 가능할 때 프로브 인증을 위해 구성된 인증 SecretRef를 해석합니다.
- 필요한 인증 SecretRef가 이 명령 경로에서 해석되지 않으면, `gateway status --json`은 프로브 연결/인증이 실패할 때 `rpc.authWarning`을 보고합니다. `--token`/`--password`를 명시적으로 전달하거나 먼저 비밀 소스를 해석하세요.
- 프로브가 성공하면 unresolved auth-ref 경고는 거짓 양성을 피하기 위해 억제됩니다.
- 단순히 리스닝 서비스만으로는 충분하지 않고 Gateway RPC 자체가 정상이어야 하는 스크립트 및 자동화에서는 `--require-rpc`를 사용하세요.
- `--deep`는 추가 launchd/systemd/schtasks 설치를 best-effort로 스캔합니다. 여러 gateway 유사 서비스가 감지되면, 사람용 출력은 정리 힌트를 출력하고 대부분의 설정에서는 머신당 하나의 gateway만 실행해야 한다고 경고합니다.
- 사람용 출력에는 해석된 파일 로그 경로와 CLI 대 서비스 config 경로/유효성 스냅샷이 포함되어 profile 또는 state-dir 드리프트 진단에 도움이 됩니다.
- Linux systemd 설치에서 서비스 인증 드리프트 검사는 유닛의 `Environment=`와 `EnvironmentFile=` 값을 모두 읽습니다(`%h`, 인용된 경로, 여러 파일, 선택적 `-` 파일 포함).
- 드리프트 검사는 병합된 런타임 env를 사용해 `gateway.auth.token` SecretRef를 해석합니다(우선 서비스 명령 env, 그다음 프로세스 env 대체).
- 토큰 인증이 실질적으로 활성 상태가 아니면(명시적 `gateway.auth.mode`가 `password`/`none`/`trusted-proxy`이거나, mode가 설정되지 않아 비밀번호가 우선될 수 있고 어떤 토큰 후보도 우선될 수 없는 경우), 토큰 드리프트 검사는 config 토큰 해석을 건너뜁니다.

### `gateway probe`

`gateway probe`는 “모든 것을 디버깅”하는 명령입니다. 항상 다음을 프로브합니다:

- 구성된 원격 gateway(설정된 경우)
- local loopback(원격이 구성되어 있어도)

`--url`을 전달하면 해당 명시적 대상이 둘보다 앞에 추가됩니다. 사람용 출력에서는
대상을 다음과 같이 라벨링합니다:

- `URL (explicit)`
- `Remote (configured)` 또는 `Remote (configured, inactive)`
- `Local loopback`

여러 Gateway에 연결할 수 있으면 모두 출력합니다. 격리된 profile/port(예: 구조 봇)를 사용할 때는 여러 Gateway를 지원하지만, 대부분의 설치는 여전히 단일 gateway를 실행합니다.

```bash
openclaw gateway probe
openclaw gateway probe --json
```

해석:

- `Reachable: yes`는 최소 하나의 대상이 WebSocket 연결을 수락했음을 의미합니다.
- `RPC: ok`는 상세 RPC 호출(`health`/`status`/`system-presence`/`config.get`)도 성공했음을 의미합니다.
- `RPC: limited - missing scope: operator.read`는 연결은 성공했지만 상세 RPC가 범위 제한을 받았음을 의미합니다. 이는 완전한 실패가 아니라 **성능 저하된** 연결 가능성으로 보고됩니다.
- 종료 코드는 프로브한 대상 중 어느 것도 연결할 수 없을 때만 0이 아닙니다.

JSON 참고(`--json`):

- 최상위:
  - `ok`: 최소 하나의 대상에 연결 가능
  - `degraded`: 최소 하나의 대상에서 상세 RPC가 범위 제한을 받음
  - `primaryTargetId`: 다음 순서로 활성 승자로 취급할 최적 대상: 명시적 URL, SSH 터널, 구성된 원격, 그다음 local loopback
  - `warnings[]`: `code`, `message`, 선택적 `targetIds`가 포함된 best-effort 경고 기록
  - `network`: 현재 config와 호스트 네트워킹에서 파생된 local loopback/tailnet URL 힌트
  - `discovery.timeoutMs`와 `discovery.count`: 이 프로브 패스에 실제로 사용된 발견 예산/결과 수
- 대상별(`targets[].connect`):
  - `ok`: 연결 + degraded 분류 이후의 연결 가능성
  - `rpcOk`: 전체 상세 RPC 성공
  - `scopeLimited`: `operator.read` 범위가 없어 상세 RPC 실패

일반적인 경고 코드:

- `ssh_tunnel_failed`: SSH 터널 설정 실패, 명령이 직접 프로브로 대체됨
- `multiple_gateways`: 둘 이상의 대상에 연결할 수 있었음. 구조 봇 같은 격리 profile을 의도적으로 실행하지 않는 한 흔치 않습니다.
- `auth_secretref_unresolved`: 실패한 대상에 대해 구성된 인증 SecretRef를 해석할 수 없었음
- `probe_scope_limited`: WebSocket 연결은 성공했지만 상세 RPC가 `operator.read` 누락으로 제한됨

#### SSH를 통한 원격(Mac 앱 동등 기능)

macOS 앱의 “Remote over SSH” 모드는 로컬 포트 포워딩을 사용하므로, 원격 gateway(오직 loopback에만 바인딩되어 있을 수 있음)가 `ws://127.0.0.1:<port>`에서 연결 가능해집니다.

CLI 동등 명령:

```bash
openclaw gateway probe --ssh user@gateway-host
```

옵션:

- `--ssh <target>`: `user@host` 또는 `user@host:port`(포트 기본값 `22`)
- `--ssh-identity <path>`: identity 파일
- `--ssh-auto`: 해석된 discovery 엔드포인트(`local.`와 설정된 wide-area 도메인, 있는 경우)에서 발견된 첫 번째 gateway 호스트를 SSH 대상으로 선택. TXT 전용 힌트는 무시됩니다.

Config(선택 사항, 기본값으로 사용됨):

- `gateway.remote.sshTarget`
- `gateway.remote.sshIdentity`

### `gateway call <method>`

저수준 RPC 도우미입니다.

```bash
openclaw gateway call status
openclaw gateway call logs.tail --params '{"sinceMs": 60000}'
```

옵션:

- `--params <json>`: params용 JSON 객체 문자열(기본값 `{}`)
- `--url <url>`
- `--token <token>`
- `--password <password>`
- `--timeout <ms>`
- `--expect-final`
- `--json`

참고:

- `--params`는 유효한 JSON이어야 합니다.
- `--expect-final`은 중간 이벤트를 스트리밍한 뒤 최종 페이로드를 보내는 에이전트 스타일 RPC에 주로 사용됩니다.

## Gateway 서비스 관리

```bash
openclaw gateway install
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
openclaw gateway uninstall
```

명령 옵션:

- `gateway status`: `--url`, `--token`, `--password`, `--timeout`, `--no-probe`, `--require-rpc`, `--deep`, `--json`
- `gateway install`: `--port`, `--runtime <node|bun>`, `--token`, `--force`, `--json`
- `gateway uninstall|start|stop|restart`: `--json`

참고:

- `gateway install`은 `--port`, `--runtime`, `--token`, `--force`, `--json`을 지원합니다.
- 토큰 인증에 토큰이 필요하고 `gateway.auth.token`이 SecretRef로 관리되면, `gateway install`은 SecretRef를 해석 가능한지 검증하지만 해석된 토큰을 서비스 환경 메타데이터에 저장하지는 않습니다.
- 토큰 인증에 토큰이 필요하고 구성된 토큰 SecretRef가 해석되지 않으면, 설치는 대체 일반 텍스트를 저장하는 대신 fail closed합니다.
- `gateway run`에서 비밀번호 인증을 사용할 때는 인라인 `--password`보다 `OPENCLAW_GATEWAY_PASSWORD`, `--password-file`, 또는 SecretRef 기반 `gateway.auth.password`를 권장합니다.
- inferred auth 모드에서는 셸 전용 `OPENCLAW_GATEWAY_PASSWORD`가 install 토큰 요구 사항을 완화하지 않습니다. 관리형 서비스를 설치할 때는 내구성 있는 config(`gateway.auth.password` 또는 config `env`)를 사용하세요.
- `gateway.auth.token`과 `gateway.auth.password`가 모두 구성되어 있고 `gateway.auth.mode`가 설정되지 않으면, mode가 명시적으로 설정될 때까지 install이 차단됩니다.
- 수명 주기 명령은 스크립팅용으로 `--json`을 허용합니다.

## Gateway 발견(Bonjour)

`gateway discover`는 Gateway 비콘(`_openclaw-gw._tcp`)을 스캔합니다.

- 멀티캐스트 DNS-SD: `local.`
- 유니캐스트 DNS-SD(Wide-Area Bonjour): 도메인 선택(예: `openclaw.internal.`) 후 split DNS + DNS 서버 설정, 자세한 내용은 [/gateway/bonjour](/gateway/bonjour)

Bonjour discovery가 활성화된 Gateway만(기본값) 비콘을 광고합니다.

Wide-Area discovery 레코드에는 다음이 포함됩니다(TXT):

- `role`(gateway 역할 힌트)
- `transport`(전송 힌트, 예: `gateway`)
- `gatewayPort`(WebSocket 포트, 일반적으로 `18789`)
- `sshPort`(선택 사항; 없으면 클라이언트는 SSH 대상 포트를 기본값 `22`로 사용)
- `tailnetDns`(사용 가능한 경우 MagicDNS 호스트명)
- `gatewayTls` / `gatewayTlsSha256`(TLS 활성화 + 인증서 지문)
- `cliPath`(wide-area 영역에 기록되는 원격 설치 힌트)

### `gateway discover`

```bash
openclaw gateway discover
```

옵션:

- `--timeout <ms>`: 명령별 타임아웃(browse/resolve), 기본값 `2000`
- `--json`: 기계가 읽기 쉬운 출력(스타일/스피너도 비활성화)

예시:

```bash
openclaw gateway discover --timeout 4000
openclaw gateway discover --json | jq '.beacons[].wsUrl'
```

참고:

- CLI는 `local.`과 활성화된 경우 구성된 wide-area 도메인을 함께 스캔합니다.
- JSON 출력의 `wsUrl`은 `lanHost`나 `tailnetDns` 같은 TXT 전용 힌트가 아니라 해석된 서비스 엔드포인트에서 파생됩니다.
- `local.` mDNS에서는 `discovery.mdns.mode`가 `full`일 때만 `sshPort`와 `cliPath`가 브로드캐스트됩니다. Wide-area DNS-SD는 여전히 `cliPath`를 기록하며, `sshPort`도 সেখানে 선택 사항으로 유지됩니다.
