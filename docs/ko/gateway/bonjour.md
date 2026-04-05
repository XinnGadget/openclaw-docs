---
read_when:
    - macOS/iOS에서 Bonjour 검색 문제를 디버깅할 때
    - mDNS 서비스 유형, TXT 레코드 또는 검색 UX를 변경할 때
summary: Bonjour/mDNS 검색 + 디버깅(게이트웨이 비컨, 클라이언트, 일반적인 실패 모드)
title: Bonjour 검색
x-i18n:
    generated_at: "2026-04-05T12:41:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7f5a7f3211c74d4d10fdc570fc102b3c949c0ded9409c54995ab8820e5787f02
    source_path: gateway/bonjour.md
    workflow: 15
---

# Bonjour / mDNS 검색

OpenClaw는 활성 게이트웨이(WebSocket 엔드포인트)를 검색하기 위해 Bonjour(mDNS / DNS‑SD)를 사용합니다.
멀티캐스트 `local.` 탐색은 **LAN 전용 편의 기능**입니다. 네트워크 간 검색을 위해
동일한 비컨을 구성된 광역 DNS-SD 도메인을 통해 게시할 수도 있습니다. 검색은
여전히 최선형 동작이며 SSH 또는 Tailnet 기반 연결을 **대체하지 않습니다**.

## Tailscale을 통한 광역 Bonjour(Unicast DNS-SD)

노드와 게이트웨이가 서로 다른 네트워크에 있으면 멀티캐스트 mDNS는
그 경계를 넘지 못합니다. 이 경우 Tailscale을 통해 **유니캐스트 DNS‑SD**
("광역 Bonjour")로 전환하여 동일한 검색 UX를 유지할 수 있습니다.

상위 수준 단계:

1. 게이트웨이 호스트에서 DNS 서버를 실행합니다(Tailnet을 통해 도달 가능해야 함).
2. 전용 zone 아래에 `_openclaw-gw._tcp`용 DNS‑SD 레코드를 게시합니다
   (예: `openclaw.internal.`).
3. 클라이언트(iOS 포함)가 해당 DNS 서버를 통해 선택한 도메인을 해석하도록
   Tailscale **split DNS**를 구성합니다.

OpenClaw는 어떤 검색 도메인도 지원합니다. `openclaw.internal.`은 단지 예시일 뿐입니다.
iOS/Android 노드는 `local.`과 구성된 광역 도메인을 모두 탐색합니다.

### 게이트웨이 config(권장)

```json5
{
  gateway: { bind: "tailnet" }, // tailnet 전용(권장)
  discovery: { wideArea: { enabled: true } }, // 광역 DNS-SD 게시 활성화
}
```

### 1회성 DNS 서버 설정(게이트웨이 호스트)

```bash
openclaw dns setup --apply
```

이 명령은 CoreDNS를 설치하고 다음과 같이 구성합니다:

- 게이트웨이의 Tailscale 인터페이스에서만 포트 53 수신
- `~/.openclaw/dns/<domain>.db`에서 선택한 도메인(예: `openclaw.internal.`) 제공

tailnet에 연결된 머신에서 검증:

```bash
dns-sd -B _openclaw-gw._tcp openclaw.internal.
dig @<TAILNET_IPV4> -p 53 _openclaw-gw._tcp.openclaw.internal PTR +short
```

### Tailscale DNS 설정

Tailscale 관리자 콘솔에서:

- 게이트웨이의 tailnet IP(UDP/TCP 53)를 가리키는 nameserver를 추가합니다.
- 검색 도메인이 해당 nameserver를 사용하도록 split DNS를 추가합니다.

클라이언트가 tailnet DNS를 수락하면 iOS 노드와 CLI 검색은
멀티캐스트 없이도 검색 도메인에서 `_openclaw-gw._tcp`를 탐색할 수 있습니다.

### 게이트웨이 리스너 보안(권장)

게이트웨이 WS 포트(기본값 `18789`)는 기본적으로 loopback에 바인딩됩니다. LAN/tailnet
접근을 위해서는 명시적으로 바인딩하고 인증을 활성화된 상태로 유지하세요.

tailnet 전용 설정의 경우:

- `~/.openclaw/openclaw.json`에서 `gateway.bind: "tailnet"`을 설정합니다.
- 게이트웨이를 재시작합니다(또는 macOS menubar 앱을 재시작합니다).

## 무엇이 광고되는가

오직 게이트웨이만 `_openclaw-gw._tcp`를 광고합니다.

## 서비스 유형

- `_openclaw-gw._tcp` — 게이트웨이 전송 비컨(macOS/iOS/Android 노드에서 사용).

## TXT 키(비밀이 아닌 힌트)

게이트웨이는 UI 흐름을 편리하게 만들기 위해 작은 비밀이 아닌 힌트를 광고합니다:

- `role=gateway`
- `displayName=<friendly name>`
- `lanHost=<hostname>.local`
- `gatewayPort=<port>` (게이트웨이 WS + HTTP)
- `gatewayTls=1` (TLS가 활성화된 경우에만)
- `gatewayTlsSha256=<sha256>` (TLS가 활성화되고 fingerprint를 사용할 수 있는 경우에만)
- `canvasPort=<port>` (canvas 호스트가 활성화된 경우에만, 현재는 `gatewayPort`와 동일)
- `transport=gateway`
- `tailnetDns=<magicdns>` (Tailnet을 사용할 수 있을 때의 선택적 힌트)
- `sshPort=<port>` (mDNS 전체 모드에서만, 광역 DNS-SD에서는 생략될 수 있음)
- `cliPath=<path>` (mDNS 전체 모드에서만, 광역 DNS-SD에서도 원격 설치 힌트로 계속 기록됨)

보안 참고:

- Bonjour/mDNS TXT 레코드는 **인증되지 않습니다**. 클라이언트는 TXT를 권한 있는 라우팅 정보로 취급해서는 안 됩니다.
- 클라이언트는 해석된 서비스 엔드포인트(SRV + A/AAAA)를 사용해 라우팅해야 합니다. `lanHost`, `tailnetDns`, `gatewayPort`, `gatewayTlsSha256`는 힌트로만 취급하세요.
- SSH 자동 대상 지정도 마찬가지로 TXT 전용 힌트가 아니라 해석된 서비스 호스트를 사용해야 합니다.
- TLS pinning에서는 광고된 `gatewayTlsSha256`이 이전에 저장된 pin을 절대 덮어쓰게 해서는 안 됩니다.
- iOS/Android 노드는 검색 기반 직접 연결을 **TLS 전용**으로 취급해야 하며, 처음 보는 fingerprint를 신뢰하기 전에 명시적인 사용자 확인을 요구해야 합니다.

## macOS에서 디버깅

유용한 내장 도구:

- 인스턴스 탐색:

  ```bash
  dns-sd -B _openclaw-gw._tcp local.
  ```

- 인스턴스 하나 해석( `<instance>` 대체):

  ```bash
  dns-sd -L "<instance>" _openclaw-gw._tcp local.
  ```

탐색은 되는데 해석이 실패한다면, 보통 LAN 정책 또는
mDNS 해석기 문제입니다.

## 게이트웨이 로그에서 디버깅

게이트웨이는 롤링 로그 파일을 기록합니다(시작 시
`gateway log file: ...`로 출력됨). 특히 다음과 같은 `bonjour:` 줄을 확인하세요:

- `bonjour: advertise failed ...`
- `bonjour: ... name conflict resolved` / `hostname conflict resolved`
- `bonjour: watchdog detected non-announced service ...`

## iOS 노드에서 디버깅

iOS 노드는 `NWBrowser`를 사용해 `_openclaw-gw._tcp`를 검색합니다.

로그를 수집하려면:

- Settings → Gateway → Advanced → **Discovery Debug Logs**
- Settings → Gateway → Advanced → **Discovery Logs** → 재현 → **Copy**

로그에는 브라우저 상태 전환과 결과 집합 변경이 포함됩니다.

## 일반적인 실패 모드

- **Bonjour는 네트워크를 넘지 못함**: Tailnet 또는 SSH를 사용하세요.
- **멀티캐스트 차단됨**: 일부 Wi‑Fi 네트워크는 mDNS를 비활성화합니다.
- **절전 / 인터페이스 변동**: macOS가 일시적으로 mDNS 결과를 놓칠 수 있습니다. 다시 시도하세요.
- **탐색은 되지만 해석은 실패함**: 머신 이름을 단순하게 유지하세요(이모지나
  구두점 피하기). 그다음 게이트웨이를 재시작하세요. 서비스 인스턴스 이름은
  호스트 이름에서 파생되므로, 지나치게 복잡한 이름은 일부 해석기를 혼란스럽게 할 수 있습니다.

## 이스케이프된 인스턴스 이름(`\032`)

Bonjour/DNS‑SD는 서비스 인스턴스 이름의 바이트를 종종 10진수 `\DDD`
시퀀스로 이스케이프합니다(예: 공백은 `\032`가 됨).

- 이는 프로토콜 수준에서 정상입니다.
- UI는 표시용으로 디코드해야 합니다(iOS는 `BonjourEscapes.decode` 사용).

## 비활성화 / 구성

- `OPENCLAW_DISABLE_BONJOUR=1`은 광고를 비활성화합니다(레거시: `OPENCLAW_DISABLE_BONJOUR`).
- `~/.openclaw/openclaw.json`의 `gateway.bind`는 게이트웨이 바인드 모드를 제어합니다.
- `OPENCLAW_SSH_PORT`는 `sshPort`가 광고될 때 SSH 포트를 재정의합니다(레거시: `OPENCLAW_SSH_PORT`).
- `OPENCLAW_TAILNET_DNS`는 TXT에 MagicDNS 힌트를 게시합니다(레거시: `OPENCLAW_TAILNET_DNS`).
- `OPENCLAW_CLI_PATH`는 광고되는 CLI 경로를 재정의합니다(레거시: `OPENCLAW_CLI_PATH`).

## 관련 문서

- 검색 정책 및 전송 선택: [검색](/gateway/discovery)
- 노드 페어링 + 승인: [게이트웨이 페어링](/gateway/pairing)
