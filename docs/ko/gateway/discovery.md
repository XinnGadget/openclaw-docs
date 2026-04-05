---
read_when:
    - Bonjour 검색/광고를 구현하거나 변경하는 경우
    - 원격 연결 모드(직접 연결 vs SSH)를 조정하는 경우
    - 원격 노드를 위한 노드 검색 + 페어링을 설계하는 경우
summary: gateway를 찾기 위한 노드 검색 및 전송(Bonjour, Tailscale, SSH)
title: 검색 및 전송
x-i18n:
    generated_at: "2026-04-05T12:42:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: e76cca9279ca77b55e30d6e746f6325e5644134ef06b9c58f2cf3d793d092685
    source_path: gateway/discovery.md
    workflow: 15
---

# 검색 및 전송

OpenClaw에는 겉보기에는 비슷하지만 실제로는 서로 다른 두 가지 문제가 있습니다.

1. **운영자 원격 제어**: 다른 곳에서 실행 중인 gateway를 macOS 메뉴 막대 앱이 제어하는 경우
2. **노드 페어링**: iOS/Android(및 향후 노드)가 gateway를 찾고 안전하게 페어링하는 경우

설계 목표는 모든 네트워크 검색/광고를 **Node Gateway** (`openclaw gateway`)에 유지하고, 클라이언트(mac app, iOS)는 이를 소비하는 쪽으로 두는 것입니다.

## 용어

- **Gateway**: 상태(세션, 페어링, 노드 레지스트리)를 소유하고 채널을 실행하는 단일 장기 실행 gateway 프로세스입니다. 대부분의 구성은 호스트당 하나를 사용하지만, 격리된 다중 gateway 구성도 가능합니다.
- **Gateway WS (제어 평면)**: 기본적으로 `127.0.0.1:18789`의 WebSocket 엔드포인트이며, `gateway.bind`를 통해 LAN/tailnet에 바인딩할 수 있습니다.
- **직접 WS 전송**: LAN/tailnet에 노출된 Gateway WS 엔드포인트(SSH 없음)
- **SSH 전송(폴백)**: SSH를 통해 `127.0.0.1:18789`를 포워딩하여 원격 제어
- **레거시 TCP 브리지(제거됨)**: 이전 노드 전송 방식입니다([브리지 프로토콜](/gateway/bridge-protocol) 참조). 더 이상 검색용으로 광고되지 않으며 현재 빌드의 일부도 아닙니다.

프로토콜 세부 정보:

- [Gateway protocol](/gateway/protocol)
- [Bridge protocol (legacy)](/gateway/bridge-protocol)

## 왜 "직접 연결"과 SSH를 둘 다 유지하는가

- **직접 WS**는 같은 네트워크 및 tailnet 내에서 최고의 UX를 제공합니다.
  - Bonjour를 통한 LAN 자동 검색
  - gateway가 소유하는 페어링 토큰 + ACL
  - 셸 액세스가 필요 없음. 프로토콜 표면을 엄격하고 감사 가능하게 유지 가능
- **SSH**는 여전히 범용 폴백입니다.
  - SSH 액세스만 있으면 어디서나 작동(서로 관련 없는 네트워크를 가로질러도 가능)
  - 멀티캐스트/mDNS 문제를 회피 가능
  - SSH 외에 새로운 인바운드 포트가 필요 없음

## 검색 입력(클라이언트가 gateway 위치를 아는 방법)

### 1) Bonjour / DNS-SD 검색

멀티캐스트 Bonjour는 best-effort이며 네트워크를 넘지 않습니다. OpenClaw는 구성된 광역 DNS-SD 도메인을 통해서도 동일한 gateway beacon을 탐색할 수 있으므로 검색 범위는 다음을 포함할 수 있습니다.

- 동일 LAN의 `local.`
- 네트워크 간 검색을 위한 구성된 유니캐스트 DNS-SD 도메인

대상 방향:

- **gateway**가 Bonjour를 통해 자신의 WS 엔드포인트를 광고합니다.
- 클라이언트는 이를 탐색하고 “gateway 선택” 목록을 표시한 뒤, 선택한 엔드포인트를 저장합니다.

문제 해결 및 beacon 세부 정보: [Bonjour](/gateway/bonjour).

#### 서비스 beacon 세부 정보

- 서비스 유형:
  - `_openclaw-gw._tcp` (gateway 전송 beacon)
- TXT 키(비밀 아님):
  - `role=gateway`
  - `transport=gateway`
  - `displayName=<friendly name>` (운영자가 구성한 표시 이름)
  - `lanHost=<hostname>.local`
  - `gatewayPort=18789` (Gateway WS + HTTP)
  - `gatewayTls=1` (TLS가 활성화된 경우에만)
  - `gatewayTlsSha256=<sha256>` (TLS가 활성화되어 있고 지문을 사용할 수 있는 경우에만)
  - `canvasPort=<port>` (canvas 호스트 포트. 현재 canvas 호스트가 활성화된 경우 `gatewayPort`와 동일)
  - `tailnetDns=<magicdns>` (선택적 힌트. Tailscale 사용 가능 시 자동 감지)
  - `sshPort=<port>` (mDNS 전체 모드에서만. 광역 DNS-SD에서는 생략될 수 있으며, 이 경우 SSH 기본값은 `22` 유지)
  - `cliPath=<path>` (mDNS 전체 모드에서만. 광역 DNS-SD에서도 원격 설치 힌트로 기록됨)

보안 참고:

- Bonjour/mDNS TXT 레코드는 **인증되지 않습니다**. 클라이언트는 TXT 값을 UX 힌트로만 취급해야 합니다.
- 라우팅(host/port)은 TXT에서 제공된 `lanHost`, `tailnetDns`, `gatewayPort`보다 **해석된 서비스 엔드포인트**(SRV + A/AAAA)를 우선해야 합니다.
- TLS pinning에서는 광고된 `gatewayTlsSha256`가 기존에 저장된 pin을 절대로 덮어쓰지 못하게 해야 합니다.
- iOS/Android 노드는 선택한 경로가 secure/TLS 기반일 때 처음 저장하는 pin에 대해 명시적인 “이 지문을 신뢰” 확인(대역 외 검증)을 요구해야 합니다.

비활성화/재정의:

- `OPENCLAW_DISABLE_BONJOUR=1`은 광고를 비활성화합니다.
- `~/.openclaw/openclaw.json`의 `gateway.bind`는 Gateway 바인드 모드를 제어합니다.
- `OPENCLAW_SSH_PORT`는 `sshPort`가 출력될 때 광고되는 SSH 포트를 재정의합니다.
- `OPENCLAW_TAILNET_DNS`는 `tailnetDns` 힌트(MagicDNS)를 게시합니다.
- `OPENCLAW_CLI_PATH`는 광고되는 CLI 경로를 재정의합니다.

### 2) Tailnet(네트워크 간)

런던/비엔나 스타일 구성에서는 Bonjour가 도움이 되지 않습니다. 권장되는 “직접 연결” 대상은 다음과 같습니다.

- Tailscale MagicDNS 이름(권장) 또는 안정적인 tailnet IP

gateway가 Tailscale 환경에서 실행 중임을 감지할 수 있으면, 클라이언트를 위한 선택적 힌트로 `tailnetDns`를 게시합니다(광역 beacon 포함).

이제 macOS 앱은 gateway 검색 시 원시 Tailscale IP보다 MagicDNS 이름을 우선합니다. 이렇게 하면 tailnet IP가 변경될 때(예: 노드 재시작 또는 CGNAT 재할당 이후) MagicDNS 이름이 현재 IP로 자동 해석되므로 신뢰성이 향상됩니다.

모바일 노드 페어링의 경우, 검색 힌트는 tailnet/public 경로에서 전송 보안을 완화하지 않습니다.

- iOS/Android는 여전히 처음 tailnet/public 경로로 연결할 때 secure 경로(`wss://` 또는 Tailscale Serve/Funnel)를 요구합니다.
- 검색된 원시 tailnet IP는 라우팅 힌트일 뿐이며, 평문 원격 `ws://`를 사용할 권한을 의미하지 않습니다.
- private LAN 직접 연결 `ws://`는 계속 지원됩니다.
- 모바일 노드에 가장 단순한 Tailscale 경로를 원한다면, 검색과 설정 코드가 동일한 secure MagicDNS 엔드포인트로 해석되도록 Tailscale Serve를 사용하세요.

### 3) 수동 / SSH 대상

직접 경로가 없거나(또는 직접 연결이 비활성화된 경우) 클라이언트는 언제나 루프백 gateway 포트를 포워딩하여 SSH를 통해 연결할 수 있습니다.

[원격 액세스](/gateway/remote)를 참조하세요.

## 전송 선택(클라이언트 정책)

권장되는 클라이언트 동작:

1. 페어링된 직접 엔드포인트가 구성되어 있고 도달 가능하면 이를 사용
2. 그렇지 않고 `local.` 또는 구성된 광역 도메인에서 검색으로 gateway를 찾으면, 한 번 탭해서 “이 gateway 사용” 선택지를 제공하고 이를 직접 엔드포인트로 저장
3. 그렇지 않고 tailnet DNS/IP가 구성되어 있으면 직접 연결 시도  
   tailnet/public 경로의 모바일 노드에서 직접 연결은 평문 원격 `ws://`가 아니라 secure 엔드포인트를 의미
4. 그렇지 않으면 SSH로 폴백

## 페어링 + 인증(직접 전송)

gateway는 노드/클라이언트 승인(admission)의 기준 정보원입니다.

- 페어링 요청은 gateway에서 생성/승인/거부됩니다([Gateway pairing](/gateway/pairing) 참조).
- gateway는 다음을 강제합니다.
  - 인증(token / keypair)
  - 범위/ACL(gateway는 모든 메서드에 대한 원시 프록시가 아님)
  - 속도 제한

## 구성 요소별 책임

- **Gateway**: 검색 beacon을 광고하고, 페어링 결정을 소유하며, WS 엔드포인트를 호스팅합니다.
- **macOS 앱**: gateway 선택을 돕고, 페어링 프롬프트를 표시하며, SSH는 폴백으로만 사용합니다.
- **iOS/Android 노드**: 편의상 Bonjour를 탐색하고, 페어링된 Gateway WS에 연결합니다.
