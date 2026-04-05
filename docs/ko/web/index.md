---
read_when:
    - Tailscale을 통해 Gateway에 접근하려고 합니다
    - 브라우저 Control UI와 config 편집을 사용하려고 합니다
summary: 'Gateway 웹 표면: Control UI, 바인드 모드, 보안'
title: Web
x-i18n:
    generated_at: "2026-04-05T12:58:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 15f5643283f7d37235d3d8104897f38db27ac5a9fdef6165156fb542d0e7048c
    source_path: web/index.md
    workflow: 15
---

# Web (Gateway)

Gateway는 Gateway WebSocket과 동일한 포트에서 작은 **브라우저 Control UI**(Vite + Lit)를 제공합니다:

- 기본값: `http://<host>:18789/`
- 선택적 접두사: `gateway.controlUi.basePath` 설정(예: `/openclaw`)

기능은 [Control UI](/web/control-ui)에 있습니다.
이 페이지는 바인드 모드, 보안, 웹 표면에 중점을 둡니다.

## Webhooks

`hooks.enabled=true`이면 Gateway는 동일한 HTTP 서버에서 작은 webhook 엔드포인트도 노출합니다.
인증 + payload는 [Gateway configuration](/ko/gateway/configuration)의 `hooks`를 참고하세요.

## config(기본 활성화)

Control UI는 자산(`dist/control-ui`)이 있으면 **기본적으로 활성화**됩니다.
다음 config로 제어할 수 있습니다:

```json5
{
  gateway: {
    controlUi: { enabled: true, basePath: "/openclaw" }, // basePath는 선택 사항
  },
}
```

## Tailscale 접근

### 통합 Serve(권장)

Gateway를 loopback에 유지하고 Tailscale Serve가 이를 프록시하게 하세요:

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "serve" },
  },
}
```

그런 다음 gateway를 시작합니다:

```bash
openclaw gateway
```

열기:

- `https://<magicdns>/` (또는 구성한 `gateway.controlUi.basePath`)

### Tailnet 바인드 + 토큰

```json5
{
  gateway: {
    bind: "tailnet",
    controlUi: { enabled: true },
    auth: { mode: "token", token: "your-token" },
  },
}
```

그런 다음 gateway를 시작합니다(이 non-loopback 예시는 공유 시크릿 토큰
인증을 사용합니다):

```bash
openclaw gateway
```

열기:

- `http://<tailscale-ip>:18789/` (또는 구성한 `gateway.controlUi.basePath`)

### 공용 인터넷(Funnel)

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "funnel" },
    auth: { mode: "password" }, // 또는 OPENCLAW_GATEWAY_PASSWORD
  },
}
```

## 보안 참고

- Gateway 인증은 기본적으로 필요합니다(token, password, trusted-proxy 또는 활성화된 경우 Tailscale Serve identity headers).
- non-loopback 바인드도 여전히 **gateway 인증이 필요**합니다. 실제로는 token/password 인증 또는 `gateway.auth.mode: "trusted-proxy"`를 사용하는 identity-aware reverse proxy를 의미합니다.
- 마법사는 기본적으로 공유 시크릿 인증을 생성하며 보통
  gateway 토큰도 생성합니다(loopback에서도).
- 공유 시크릿 모드에서 UI는 `connect.params.auth.token` 또는
  `connect.params.auth.password`를 전송합니다.
- Tailscale Serve 또는 `trusted-proxy` 같은 identity-bearing 모드에서는
  WebSocket 인증 검사가 대신 요청 헤더에서 충족됩니다.
- non-loopback Control UI 배포에서는 `gateway.controlUi.allowedOrigins`를
  명시적으로 설정하세요(전체 origin). 이것이 없으면 기본적으로 gateway 시작이 거부됩니다.
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true`는
  Host-header origin 폴백 모드를 활성화하지만, 이는 위험한 보안 저하입니다.
- Serve를 사용할 때 `gateway.auth.allowTailscale`이 `true`이면
  Tailscale identity headers가 Control UI/WebSocket 인증을 충족할 수 있습니다
  (token/password 불필요).
  HTTP API 엔드포인트는 이러한 Tailscale identity headers를 사용하지 않으며,
  대신 gateway의 일반 HTTP 인증 모드를 따릅니다. 명시적 자격 증명을 요구하려면
  `gateway.auth.allowTailscale: false`를 설정하세요.
  [Tailscale](/ko/gateway/tailscale)과 [보안](/ko/gateway/security)을 참고하세요. 이
  토큰 없는 흐름은 gateway 호스트가 신뢰된다고 가정합니다.
- `gateway.tailscale.mode: "funnel"`에는 `gateway.auth.mode: "password"`(공유 비밀번호)가 필요합니다.

## UI 빌드

Gateway는 `dist/control-ui`에서 정적 파일을 제공합니다. 다음으로 빌드하세요:

```bash
pnpm ui:build # 첫 실행 시 UI deps를 자동 설치
```
