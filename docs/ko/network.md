---
read_when:
    - 네트워크 아키텍처 + 보안 개요가 필요할 때
    - 로컬과 tailnet 접근 또는 페어링을 디버깅하는 경우
    - 네트워킹 문서의 정식 목록이 필요할 때
summary: '네트워크 허브: 게이트웨이 표면, 페어링, 검색 및 보안'
title: 네트워크
x-i18n:
    generated_at: "2026-04-05T12:47:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4a5f39d4f40ad19646d372000c85b663770eae412af91e1c175eb27b22208118
    source_path: network.md
    workflow: 15
---

# 네트워크 허브

이 허브는 OpenClaw가 localhost, LAN, tailnet 전반에서 디바이스를 어떻게 연결하고, 페어링하고, 보호하는지에 대한 핵심 문서를 연결합니다.

## 핵심 모델

대부분의 작업은 게이트웨이(`openclaw gateway`)를 통해 흐릅니다. 게이트웨이는 채널 연결과 WebSocket 제어 평면을 소유하는 단일 장기 실행 프로세스입니다.

- **Loopback 우선**: 게이트웨이 WS의 기본값은 `ws://127.0.0.1:18789`입니다.
  non-loopback 바인드에는 유효한 게이트웨이 인증 경로가 필요합니다: 공유 비밀
  token/password 인증 또는 올바르게 구성된 non-loopback
  `trusted-proxy` 배포.
- **호스트당 하나의 게이트웨이**를 권장합니다. 격리가 필요하면 분리된 프로필과 포트로 여러 게이트웨이를 실행하세요([다중 게이트웨이](/gateway/multiple-gateways)).
- **Canvas host**는 게이트웨이와 동일한 포트(` /__openclaw__/canvas/`, `/__openclaw__/a2ui/`)에서 제공되며, loopback을 넘어 바인드될 때는 게이트웨이 인증으로 보호됩니다.
- **원격 접근**은 일반적으로 SSH 터널 또는 Tailscale VPN입니다([원격 접근](/gateway/remote)).

핵심 참조:

- [게이트웨이 아키텍처](/concepts/architecture)
- [게이트웨이 프로토콜](/gateway/protocol)
- [게이트웨이 운영 문서](/gateway)
- [Web 표면 + 바인드 모드](/web)

## 페어링 + ID

- [페어링 개요(DM + 노드)](/channels/pairing)
- [게이트웨이 소유 노드 페어링](/gateway/pairing)
- [Devices CLI(페어링 + 토큰 순환)](/cli/devices)
- [페어링 CLI(DM 승인)](/cli/pairing)

로컬 신뢰:

- 동일 호스트 UX를 원활하게 유지하기 위해 직접 local loopback 연결은 페어링에 대해 자동 승인될 수 있습니다.
- OpenClaw에는 신뢰된 공유 비밀 helper 흐름을 위한 좁은 범위의 backend/container-local self-connect 경로도 있습니다.
- 동일 호스트 tailnet 바인드를 포함한 tailnet 및 LAN 클라이언트는 여전히 명시적인 페어링 승인이 필요합니다.

## 검색 + 전송

- [검색 및 전송](/gateway/discovery)
- [Bonjour / mDNS](/gateway/bonjour)
- [원격 접근(SSH)](/gateway/remote)
- [Tailscale](/gateway/tailscale)

## 노드 + 전송

- [노드 개요](/nodes)
- [브리지 프로토콜(레거시 노드, 역사적)](/gateway/bridge-protocol)
- [노드 운영 문서: iOS](/platforms/ios)
- [노드 운영 문서: Android](/platforms/android)

## 보안

- [보안 개요](/gateway/security)
- [게이트웨이 config 참조](/gateway/configuration)
- [문제 해결](/gateway/troubleshooting)
- [Doctor](/gateway/doctor)
