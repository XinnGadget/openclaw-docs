---
read_when:
    - 원격 gateway 설정을 실행하거나 문제를 해결하는 경우
summary: SSH 터널(Gateway WS)과 tailnet을 사용한 원격 액세스
title: 원격 액세스
x-i18n:
    generated_at: "2026-04-05T12:43:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8596fa2a7fd44117dfe92b70c9d8f28c0e16d7987adf0d0769a9eff71d5bc081
    source_path: gateway/remote.md
    workflow: 15
---

# 원격 액세스 (SSH, 터널, tailnet)

이 리포지토리는 전용 호스트(데스크톱/서버)에서 단일 Gateway(마스터)를 실행하고 클라이언트를 여기에 연결하는 방식으로 “SSH를 통한 원격”을 지원합니다.

- **운영자(사용자 / macOS 앱)**의 경우: SSH 터널링이 범용 fallback입니다.
- **node(iOS/Android 및 향후 디바이스)**의 경우: 필요에 따라 **WebSocket** Gateway(LAN/tailnet 또는 SSH 터널)를 통해 연결합니다.

## 핵심 개념

- Gateway WebSocket은 구성된 포트(기본값 18789)에서 **loopback**에 바인딩됩니다.
- 원격 사용 시에는 이 loopback 포트를 SSH로 포워딩합니다(또는 tailnet/VPN을 사용해 터널 의존도를 줄일 수 있습니다).

## 일반적인 VPN/tailnet 설정(agent가 있는 위치)

**Gateway 호스트**를 “agent가 있는 곳”이라고 생각하세요. 이 호스트가 세션, auth profile, 채널, 상태를 소유합니다.
노트북/데스크톱(및 node)은 이 호스트에 연결합니다.

### 1) tailnet 내 항상 켜져 있는 Gateway(VPS 또는 홈 서버)

지속적으로 실행되는 호스트에서 Gateway를 실행하고 **Tailscale** 또는 SSH를 통해 접근합니다.

- **최상의 UX:** `gateway.bind: "loopback"`을 유지하고 Control UI에는 **Tailscale Serve**를 사용합니다.
- **Fallback:** loopback을 유지하고 액세스가 필요한 모든 머신에서 SSH 터널을 사용합니다.
- **예시:** [exe.dev](/install/exe-dev) (쉬운 VM) 또는 [Hetzner](/install/hetzner) (프로덕션 VPS).

노트북이 자주 절전 상태에 들어가더라도 agent를 항상 켜두고 싶다면 이상적인 방식입니다.

### 2) 집의 데스크톱에서 Gateway를 실행하고, 노트북은 원격 제어만 수행

노트북은 agent를 실행하지 **않습니다**. 원격으로 연결만 합니다.

- macOS 앱의 **Remote over SSH** 모드를 사용하세요(Settings → General → “OpenClaw runs”).
- 앱이 터널을 열고 관리하므로 WebChat + 상태 점검이 “그냥 작동”합니다.

실행 가이드: [macOS 원격 액세스](/platforms/mac/remote).

### 3) 노트북에서 Gateway를 실행하고, 다른 머신에서 원격 액세스

Gateway는 로컬에 유지하면서 안전하게 노출합니다.

- 다른 머신에서 노트북으로 SSH 터널을 열거나
- Tailscale Serve로 Control UI를 노출하고 Gateway는 loopback 전용으로 유지합니다.

가이드: [Tailscale](/gateway/tailscale) 및 [Web 개요](/web).

## 명령 흐름(무엇이 어디에서 실행되는지)

하나의 gateway 서비스가 상태 + 채널을 소유합니다. node는 주변 장치입니다.

흐름 예시(Telegram → node):

- Telegram 메시지가 **Gateway**에 도착합니다.
- Gateway가 **agent**를 실행하고 node 도구를 호출할지 결정합니다.
- Gateway가 Gateway WebSocket(`node.*` RPC)을 통해 **node**를 호출합니다.
- Node가 결과를 반환하고, Gateway가 Telegram으로 다시 응답합니다.

참고:

- **Node는 gateway 서비스를 실행하지 않습니다.** 의도적으로 격리된 profile을 실행하는 경우가 아니라면 호스트당 gateway는 하나만 실행해야 합니다([Multiple gateways](/gateway/multiple-gateways) 참조).
- macOS 앱의 “node mode”는 Gateway WebSocket을 통한 node 클라이언트일 뿐입니다.

## SSH 터널(CLI + 도구)

원격 Gateway WS로 로컬 터널을 생성합니다.

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

터널이 올라오면:

- `openclaw health`와 `openclaw status --deep`가 이제 `ws://127.0.0.1:18789`를 통해 원격 gateway에 도달합니다.
- `openclaw gateway status`, `openclaw gateway health`, `openclaw gateway probe`, `openclaw gateway call`도 필요할 때 `--url`로 포워딩된 URL을 대상으로 사용할 수 있습니다.

참고: `18789`는 구성된 `gateway.port`(또는 `--port`/`OPENCLAW_GATEWAY_PORT`)로 바꾸세요.
참고: `--url`을 전달하면 CLI는 config 또는 환경 자격 증명으로 fallback하지 않습니다.
`--token` 또는 `--password`를 명시적으로 포함하세요. 명시적 자격 증명이 없으면 오류입니다.

## CLI 원격 기본값

CLI 명령이 기본적으로 사용하도록 원격 대상을 저장할 수 있습니다.

```json5
{
  gateway: {
    mode: "remote",
    remote: {
      url: "ws://127.0.0.1:18789",
      token: "your-token",
    },
  },
}
```

gateway가 loopback 전용인 경우 URL은 `ws://127.0.0.1:18789`로 유지하고 먼저 SSH 터널을 여세요.

## 자격 증명 우선순위

Gateway 자격 증명 해상은 call/probe/status 경로와 Discord exec-approval 모니터링 전반에 걸쳐 하나의 공통 계약을 따릅니다. Node-host는 같은 기본 계약을 사용하되 로컬 모드 예외 하나가 있습니다(`gateway.remote.*`를 의도적으로 무시함).

- 명시적 자격 증명(`--token`, `--password`, 또는 도구 `gatewayToken`)은 명시적 auth를 허용하는 call 경로에서 항상 우선합니다.
- URL 재정의 안전 규칙:
  - CLI URL 재정의(`--url`)는 암묵적인 config/env 자격 증명을 절대 재사용하지 않습니다.
  - Env URL 재정의(`OPENCLAW_GATEWAY_URL`)는 env 자격 증명만 사용할 수 있습니다(`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`).
- 로컬 모드 기본값:
  - token: `OPENCLAW_GATEWAY_TOKEN` -> `gateway.auth.token` -> `gateway.remote.token` (원격 fallback은 로컬 auth token 입력이 설정되지 않은 경우에만 적용)
  - password: `OPENCLAW_GATEWAY_PASSWORD` -> `gateway.auth.password` -> `gateway.remote.password` (원격 fallback은 로컬 auth password 입력이 설정되지 않은 경우에만 적용)
- 원격 모드 기본값:
  - token: `gateway.remote.token` -> `OPENCLAW_GATEWAY_TOKEN` -> `gateway.auth.token`
  - password: `OPENCLAW_GATEWAY_PASSWORD` -> `gateway.remote.password` -> `gateway.auth.password`
- Node-host 로컬 모드 예외: `gateway.remote.token` / `gateway.remote.password`는 무시됩니다.
- 원격 probe/status 토큰 검사는 기본적으로 엄격합니다. 원격 모드를 대상으로 할 때는 `gateway.remote.token`만 사용합니다(로컬 토큰 fallback 없음).
- Gateway env 재정의는 `OPENCLAW_GATEWAY_*`만 사용합니다.

## SSH를 통한 채팅 UI

WebChat은 더 이상 별도의 HTTP 포트를 사용하지 않습니다. SwiftUI 채팅 UI는 직접 Gateway WebSocket에 연결됩니다.

- SSH로 `18789`를 포워딩한 다음(위 참조), 클라이언트를 `ws://127.0.0.1:18789`에 연결하세요.
- macOS에서는 앱의 “Remote over SSH” 모드를 사용하는 것이 좋습니다. 이 모드는 터널을 자동으로 관리합니다.

## macOS 앱 "Remote over SSH"

macOS 메뉴 바 앱은 동일한 설정을 엔드투엔드로 처리할 수 있습니다(원격 상태 점검, WebChat, Voice Wake 포워딩).

실행 가이드: [macOS 원격 액세스](/platforms/mac/remote).

## 보안 규칙(원격/VPN)

짧게 말하면: **반드시 필요하다고 확신하지 않는 한 Gateway는 loopback 전용으로 유지**하세요.

- **Loopback + SSH/Tailscale Serve**가 가장 안전한 기본값입니다(공개 노출 없음).
- 평문 `ws://`는 기본적으로 loopback 전용입니다. 신뢰할 수 있는 사설 네트워크에서는
  비상 우회용으로 클라이언트 프로세스에 `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`을 설정하세요.
- **비-loopback 바인딩**(`lan`/`tailnet`/`custom`, 또는 loopback을 사용할 수 없을 때의 `auto`)은 gateway auth를 사용해야 합니다: token, password 또는 `gateway.auth.mode: "trusted-proxy"`를 사용하는 identity-aware 리버스 프록시.
- `gateway.remote.token` / `.password`는 클라이언트 자격 증명 소스입니다. 이것만으로 서버 auth를 구성하지는 않습니다.
- 로컬 call 경로는 `gateway.auth.*`가 설정되지 않은 경우에만 `gateway.remote.*`를 fallback으로 사용할 수 있습니다.
- `gateway.auth.token` / `gateway.auth.password`가 SecretRef로 명시적으로 구성되어 있는데 확인되지 않으면, 해상은 안전하게 실패합니다(원격 fallback이 이를 가리지 않음).
- `gateway.remote.tlsFingerprint`는 `wss://` 사용 시 원격 TLS 인증서를 pinning합니다.
- **Tailscale Serve**는 `gateway.auth.allowTailscale: true`일 때 identity
  헤더를 통해 Control UI/WebSocket 트래픽을 인증할 수 있습니다. HTTP API 엔드포인트는
  이 Tailscale 헤더 auth를 사용하지 않으며 대신 gateway의 일반 HTTP
  auth 모드를 따릅니다. 이 토큰 없는 흐름은 gateway 호스트가 신뢰된다는 것을 전제로 합니다. 어디서나 공유 시크릿 auth를 원한다면 이를
  `false`로 설정하세요.
- **Trusted-proxy** auth는 비-loopback identity-aware 프록시 설정 전용입니다.
  동일 호스트의 loopback 리버스 프록시는 `gateway.auth.mode: "trusted-proxy"` 조건을 충족하지 않습니다.
- browser 제어는 운영자 액세스처럼 취급하세요: tailnet 전용 + 의도적인 node 페어링.

자세한 내용: [Security](/gateway/security).

### macOS: LaunchAgent를 통한 영구 SSH 터널

원격 gateway에 연결하는 macOS 클라이언트의 경우, 가장 쉬운 영구 설정은 SSH `LocalForward` config 항목과 LaunchAgent를 사용해 재부팅과 충돌 후에도 터널을 유지하는 것입니다.

#### 1단계: SSH config 추가

`~/.ssh/config`를 편집하세요.

```ssh
Host remote-gateway
    HostName <REMOTE_IP>
    User <REMOTE_USER>
    LocalForward 18789 127.0.0.1:18789
    IdentityFile ~/.ssh/id_rsa
```

`<REMOTE_IP>`와 `<REMOTE_USER>`를 실제 값으로 바꾸세요.

#### 2단계: SSH 키 복사(1회)

```bash
ssh-copy-id -i ~/.ssh/id_rsa <REMOTE_USER>@<REMOTE_IP>
```

#### 3단계: gateway 토큰 구성

재시작 후에도 유지되도록 config에 토큰을 저장하세요.

```bash
openclaw config set gateway.remote.token "<your-token>"
```

#### 4단계: LaunchAgent 생성

다음을 `~/Library/LaunchAgents/ai.openclaw.ssh-tunnel.plist`로 저장하세요.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.ssh-tunnel</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/ssh</string>
        <string>-N</string>
        <string>remote-gateway</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

#### 5단계: LaunchAgent 로드

```bash
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/ai.openclaw.ssh-tunnel.plist
```

터널은 로그인 시 자동으로 시작되고, 충돌 시 재시작되며, 포워딩된 포트를 계속 활성 상태로 유지합니다.

참고: 이전 설정에서 남아 있는 `com.openclaw.ssh-tunnel` LaunchAgent가 있다면, 언로드하고 삭제하세요.

#### 문제 해결

터널이 실행 중인지 확인:

```bash
ps aux | grep "ssh -N remote-gateway" | grep -v grep
lsof -i :18789
```

터널 재시작:

```bash
launchctl kickstart -k gui/$UID/ai.openclaw.ssh-tunnel
```

터널 중지:

```bash
launchctl bootout gui/$UID/ai.openclaw.ssh-tunnel
```

| Config 항목                           | 동작                                                         |
| ------------------------------------- | ------------------------------------------------------------ |
| `LocalForward 18789 127.0.0.1:18789`  | 로컬 포트 18789를 원격 포트 18789로 포워딩                  |
| `ssh -N`                              | 원격 명령을 실행하지 않는 SSH(포트 포워딩 전용)             |
| `KeepAlive`                           | 터널이 충돌하면 자동으로 재시작                              |
| `RunAtLoad`                           | 로그인 시 LaunchAgent가 로드되면 터널 시작                   |
