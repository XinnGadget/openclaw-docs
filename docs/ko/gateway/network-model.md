---
read_when:
    - Gateway 네트워킹 모델을 간결하게 보고 싶은 경우
summary: Gateway, 노드, canvas 호스트가 어떻게 연결되는지
title: 네트워크 모델
x-i18n:
    generated_at: "2026-04-05T12:42:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7d02d87f38ee5a9fae228f5028892b192c50b473ab4441bbe0b40ee85a1dd402
    source_path: gateway/network-model.md
    workflow: 15
---

# 네트워크 모델

> 이 내용은 [네트워크](/network#core-model)로 통합되었습니다. 현재 가이드는 해당 페이지를 참조하세요.

대부분의 작업은 채널 연결과 WebSocket 제어 평면을 소유하는 단일 장기 실행 프로세스인 Gateway(`openclaw gateway`)를 통해 흐릅니다.

## 핵심 규칙

- 호스트당 하나의 Gateway를 권장합니다. WhatsApp Web 세션을 소유할 수 있는 유일한 프로세스입니다. 복구 bot 또는 엄격한 격리가 필요한 경우 격리된 프로필과 포트로 여러 gateway를 실행하세요. [다중 gateway](/gateway/multiple-gateways)를 참조하세요.
- loopback 우선: Gateway WS의 기본값은 `ws://127.0.0.1:18789`입니다. wizard는 기본적으로 shared-secret 인증을 생성하며, 대개 loopback에서도 토큰을 생성합니다. loopback이 아닌 액세스에는 유효한 gateway 인증 경로를 사용하세요: shared-secret token/password 인증, 또는 올바르게 구성된 non-loopback `trusted-proxy` 배포. tailnet/모바일 구성은 일반적으로 원시 tailnet `ws://` 대신 Tailscale Serve 또는 다른 `wss://` 엔드포인트를 통해 가장 잘 동작합니다.
- 노드는 필요에 따라 LAN, tailnet 또는 SSH를 통해 Gateway WS에 연결합니다. 레거시 TCP 브리지는 제거되었습니다.
- canvas 호스트는 Gateway와 **같은 포트**(기본값 `18789`)에서 Gateway HTTP 서버에 의해 제공됩니다:
  - `/__openclaw__/canvas/`
  - `/__openclaw__/a2ui/`
    `gateway.auth`가 구성되어 있고 Gateway가 loopback을 넘어 바인딩되는 경우, 이 경로들은 Gateway 인증으로 보호됩니다. 노드 클라이언트는 활성 WS 세션에 연결된 노드 범위 capability URL을 사용합니다. [Gateway 구성](/gateway/configuration) (`canvasHost`, `gateway`)을 참조하세요.
- 원격 사용은 일반적으로 SSH 터널 또는 tailnet VPN을 사용합니다. [원격 액세스](/gateway/remote) 및 [검색](/gateway/discovery)을 참조하세요.
