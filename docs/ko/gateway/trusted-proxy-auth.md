---
read_when:
    - ID 인식 프록시 뒤에서 OpenClaw를 실행할 때
    - OpenClaw 앞단에 Pomerium, Caddy 또는 nginx + OAuth를 설정할 때
    - reverse proxy 설정에서 WebSocket 1008 unauthorized 오류를 해결할 때
    - HSTS 및 기타 HTTP 보안 강화 헤더를 어디에 설정할지 결정할 때
summary: 신뢰된 reverse proxy(Pomerium, Caddy, nginx + OAuth)에 게이트웨이 인증 위임
title: 신뢰된 프록시 인증
x-i18n:
    generated_at: "2026-04-05T12:44:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: ccd39736b43e8744de31566d5597b3fbf40ecb6ba9c8ba9d2343e1ab9bb8cd45
    source_path: gateway/trusted-proxy-auth.md
    workflow: 15
---

# 신뢰된 프록시 인증

> ⚠️ **보안에 민감한 기능입니다.** 이 모드는 인증을 전적으로 reverse proxy에 위임합니다. 잘못 구성하면 권한 없는 접근에 게이트웨이가 노출될 수 있습니다. 활성화하기 전에 이 페이지를 주의 깊게 읽으세요.

## 사용해야 하는 경우

다음 경우 `trusted-proxy` 인증 모드를 사용하세요:

- OpenClaw를 **ID 인식 프록시**(Pomerium, Caddy + OAuth, nginx + oauth2-proxy, Traefik + forward auth) 뒤에서 실행하는 경우
- 프록시가 모든 인증을 처리하고 사용자 ID를 헤더를 통해 전달하는 경우
- 프록시가 게이트웨이로 가는 유일한 경로인 Kubernetes 또는 컨테이너 환경인 경우
- 브라우저가 WS 페이로드에 토큰을 전달할 수 없어 WebSocket `1008 unauthorized` 오류가 발생하는 경우

## 사용하면 안 되는 경우

- 프록시가 사용자를 인증하지 않는 경우(단순 TLS 종료기 또는 로드 밸런서)
- 프록시를 우회하여 게이트웨이에 도달할 수 있는 경로가 하나라도 있는 경우(방화벽 구멍, 내부 네트워크 접근)
- 프록시가 전달 헤더를 올바르게 제거/덮어쓰는지 확신할 수 없는 경우
- 개인 단일 사용자 접근만 필요한 경우(더 단순한 설정을 위해 Tailscale Serve + loopback을 고려하세요)

## 동작 방식

1. reverse proxy가 사용자 인증을 수행합니다(OAuth, OIDC, SAML 등)
2. 프록시가 인증된 사용자 ID를 담은 헤더를 추가합니다(예: `x-forwarded-user: nick@example.com`)
3. OpenClaw는 요청이 **신뢰된 프록시 IP**(`gateway.trustedProxies`에 구성됨)에서 왔는지 확인합니다
4. OpenClaw는 구성된 헤더에서 사용자 ID를 추출합니다
5. 모든 것이 확인되면 요청이 인증됩니다

## 제어 UI 페어링 동작

`gateway.auth.mode = "trusted-proxy"`가 활성화되어 있고 요청이
신뢰된 프록시 검사를 통과하면, 제어 UI WebSocket 세션은 디바이스
페어링 ID 없이 연결할 수 있습니다.

의미:

- 이 모드에서는 페어링이 더 이상 제어 UI 접근의 기본 게이트가 아닙니다.
- reverse proxy 인증 정책과 `allowUsers`가 실질적인 접근 제어가 됩니다.
- 게이트웨이 ingress는 신뢰된 프록시 IP만 허용하도록 잠가 두세요(`gateway.trustedProxies` + 방화벽).

## 구성

```json5
{
  gateway: {
    // trusted-proxy 인증은 non-loopback 신뢰 프록시 소스에서 온 요청을 기대합니다
    bind: "lan",

    // 중요: 여기에 프록시의 IP만 추가하세요
    trustedProxies: ["10.0.0.1", "172.17.0.1"],

    auth: {
      mode: "trusted-proxy",
      trustedProxy: {
        // 인증된 사용자 ID를 담는 헤더(필수)
        userHeader: "x-forwarded-user",

        // 선택 사항: 반드시 존재해야 하는 헤더(프록시 검증)
        requiredHeaders: ["x-forwarded-proto", "x-forwarded-host"],

        // 선택 사항: 특정 사용자로 제한(비어 있으면 모두 허용)
        allowUsers: ["nick@example.com", "admin@company.org"],
      },
    },
  },
}
```

중요한 런타임 규칙:

- 신뢰된 프록시 인증은 loopback 소스 요청(`127.0.0.1`, `::1`, loopback CIDR)을 거부합니다.
- 동일 호스트의 loopback reverse proxy는 trusted-proxy 인증 조건을 충족하지 않습니다.
- 동일 호스트 loopback 프록시 설정에서는 대신 token/password 인증을 사용하거나, OpenClaw가 검증할 수 있는 non-loopback 신뢰 프록시 주소를 통해 라우팅하세요.
- non-loopback 제어 UI 배포에서는 여전히 명시적인 `gateway.controlUi.allowedOrigins`가 필요합니다.

### 구성 참조

| 필드 | 필수 여부 | 설명 |
| ------------------------------------------- | -------- | --------------------------------------------------------------------------- |
| `gateway.trustedProxies`                    | 예 | 신뢰할 프록시 IP 주소 배열. 다른 IP에서 온 요청은 거부됩니다. |
| `gateway.auth.mode`                         | 예 | 반드시 `"trusted-proxy"`여야 함 |
| `gateway.auth.trustedProxy.userHeader`      | 예 | 인증된 사용자 ID를 담는 헤더 이름 |
| `gateway.auth.trustedProxy.requiredHeaders` | 아니요 | 요청이 신뢰되기 위해 추가로 반드시 존재해야 하는 헤더 |
| `gateway.auth.trustedProxy.allowUsers`      | 아니요 | 사용자 ID 허용 목록. 비어 있으면 인증된 모든 사용자를 허용합니다. |

## TLS 종료와 HSTS

TLS 종료 지점은 하나만 사용하고 그 위치에 HSTS를 적용하세요.

### 권장 패턴: 프록시 TLS 종료

reverse proxy가 `https://control.example.com`에 대한 HTTPS를 처리하는 경우,
해당 도메인에 대해 프록시에서 `Strict-Transport-Security`를 설정하세요.

- 인터넷에 노출된 배포에 적합합니다.
- 인증서 + HTTP 보안 강화 정책을 한곳에 둘 수 있습니다.
- OpenClaw는 프록시 뒤에서 loopback HTTP로 유지할 수 있습니다.

헤더 값 예시:

```text
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 게이트웨이 TLS 종료

OpenClaw 자체가 HTTPS를 직접 제공하는 경우(TLS 종료 프록시 없음), 다음과 같이 설정하세요:

```json5
{
  gateway: {
    tls: { enabled: true },
    http: {
      securityHeaders: {
        strictTransportSecurity: "max-age=31536000; includeSubDomains",
      },
    },
  },
}
```

`strictTransportSecurity`는 문자열 헤더 값 또는 명시적 비활성화를 위한 `false`를 받습니다.

### 롤아웃 가이드

- 트래픽을 검증하는 동안 먼저 짧은 max age(예: `max-age=300`)로 시작하세요.
- 충분한 확신이 생긴 뒤에만 장기 값(예: `max-age=31536000`)으로 늘리세요.
- 모든 하위 도메인이 HTTPS 준비가 되어 있을 때만 `includeSubDomains`를 추가하세요.
- 전체 도메인 집합이 preload 요구사항을 충족하도록 의도한 경우에만 preload를 사용하세요.
- loopback 전용 로컬 개발에는 HSTS의 이점이 없습니다.

## 프록시 설정 예시

### Pomerium

Pomerium은 `x-pomerium-claim-email`(또는 다른 claim 헤더)과 `x-pomerium-jwt-assertion`의 JWT로 ID를 전달합니다.

```json5
{
  gateway: {
    bind: "lan",
    trustedProxies: ["10.0.0.1"], // Pomerium의 IP
    auth: {
      mode: "trusted-proxy",
      trustedProxy: {
        userHeader: "x-pomerium-claim-email",
        requiredHeaders: ["x-pomerium-jwt-assertion"],
      },
    },
  },
}
```

Pomerium config 스니펫:

```yaml
routes:
  - from: https://openclaw.example.com
    to: http://openclaw-gateway:18789
    policy:
      - allow:
          or:
            - email:
                is: nick@example.com
    pass_identity_headers: true
```

### OAuth가 포함된 Caddy

`caddy-security` plugin이 포함된 Caddy는 사용자를 인증하고 ID 헤더를 전달할 수 있습니다.

```json5
{
  gateway: {
    bind: "lan",
    trustedProxies: ["10.0.0.1"], // Caddy/sidecar 프록시 IP
    auth: {
      mode: "trusted-proxy",
      trustedProxy: {
        userHeader: "x-forwarded-user",
      },
    },
  },
}
```

Caddyfile 스니펫:

```
openclaw.example.com {
    authenticate with oauth2_provider
    authorize with policy1

    reverse_proxy openclaw:18789 {
        header_up X-Forwarded-User {http.auth.user.email}
    }
}
```

### nginx + oauth2-proxy

oauth2-proxy는 사용자를 인증하고 `x-auth-request-email`에 ID를 전달합니다.

```json5
{
  gateway: {
    bind: "lan",
    trustedProxies: ["10.0.0.1"], // nginx/oauth2-proxy IP
    auth: {
      mode: "trusted-proxy",
      trustedProxy: {
        userHeader: "x-auth-request-email",
      },
    },
  },
}
```

nginx config 스니펫:

```nginx
location / {
    auth_request /oauth2/auth;
    auth_request_set $user $upstream_http_x_auth_request_email;

    proxy_pass http://openclaw:18789;
    proxy_set_header X-Auth-Request-Email $user;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Forward Auth가 포함된 Traefik

```json5
{
  gateway: {
    bind: "lan",
    trustedProxies: ["172.17.0.1"], // Traefik 컨테이너 IP
    auth: {
      mode: "trusted-proxy",
      trustedProxy: {
        userHeader: "x-forwarded-user",
      },
    },
  },
}
```

## 혼합 token 구성

OpenClaw는 `gateway.auth.token`(또는 `OPENCLAW_GATEWAY_TOKEN`)과 `trusted-proxy` 모드가 동시에 활성화된 모호한 구성을 거부합니다. 혼합 token 구성은 loopback 요청이 잘못된 인증 경로로 조용히 인증되도록 만들 수 있습니다.

시작 시 `mixed_trusted_proxy_token` 오류가 보이면:

- trusted-proxy 모드를 사용할 때 공유 token을 제거하거나
- token 기반 인증을 의도한 경우 `gateway.auth.mode`를 `"token"`으로 전환하세요.

loopback trusted-proxy 인증도 fail closed 방식으로 동작합니다. 동일 호스트 호출자는 조용히 인증되는 대신 신뢰된 프록시를 통해 구성된 ID 헤더를 제공해야 합니다.

## 운영자 범위 헤더

trusted-proxy 인증은 **ID를 포함하는** HTTP 모드이므로, 호출자는
선택적으로 `x-openclaw-scopes`로 운영자 범위를 선언할 수 있습니다.

예시:

- `x-openclaw-scopes: operator.read`
- `x-openclaw-scopes: operator.read,operator.write`
- `x-openclaw-scopes: operator.admin,operator.write`

동작:

- 헤더가 존재하면 OpenClaw는 선언된 범위 집합을 존중합니다.
- 헤더가 존재하지만 비어 있으면 요청은 **운영자 범위를 선언하지 않은 것**입니다.
- 헤더가 없으면 일반적인 ID 포함 HTTP API는 표준 운영자 기본 범위 집합으로 대체됩니다.
- 게이트웨이 인증 **plugin HTTP 라우트**는 기본적으로 더 좁습니다. `x-openclaw-scopes`가 없으면 런타임 범위는 `operator.write`로 대체됩니다.
- 브라우저 원본 HTTP 요청은 trusted-proxy 인증이 성공한 뒤에도 여전히 `gateway.controlUi.allowedOrigins`(또는 의도적인 Host 헤더 fallback 모드)를 통과해야 합니다.

실용적인 규칙:

- trusted-proxy 요청을 기본값보다 더 좁게 만들고 싶거나, gateway-auth plugin 라우트에 write 범위보다 강한 것이 필요할 때는 `x-openclaw-scopes`를 명시적으로 보내세요.

## 보안 체크리스트

trusted-proxy 인증을 활성화하기 전에 다음을 확인하세요:

- [ ] **프록시가 유일한 경로임**: 게이트웨이 포트는 프록시 외 모든 접근으로부터 방화벽으로 차단됨
- [ ] **trustedProxies가 최소 범위임**: 전체 서브넷이 아니라 실제 프록시 IP만 포함
- [ ] **loopback 프록시 소스 없음**: trusted-proxy 인증은 loopback 소스 요청에서 fail closed
- [ ] **프록시가 헤더를 제거함**: 프록시는 클라이언트의 `x-forwarded-*` 헤더를 추가가 아니라 덮어씀
- [ ] **TLS 종료**: 프록시가 TLS를 처리하며 사용자는 HTTPS로 연결함
- [ ] **allowedOrigins가 명시적임**: non-loopback 제어 UI는 명시적인 `gateway.controlUi.allowedOrigins` 사용
- [ ] **allowUsers가 설정됨**(권장): 인증된 누구나 허용하는 대신 알려진 사용자로 제한
- [ ] **혼합 token 구성 없음**: `gateway.auth.token`과 `gateway.auth.mode: "trusted-proxy"`를 동시에 설정하지 않음

## 보안 감사

`openclaw security audit`는 trusted-proxy 인증에 대해 **critical** 심각도의 결과를 표시합니다. 이는 의도된 동작으로, 보안이 프록시 설정에 위임된다는 점을 상기시키기 위한 것입니다.

감사에서는 다음을 점검합니다:

- 기본 `gateway.trusted_proxy_auth` 경고/critical 알림
- 누락된 `trustedProxies` 구성
- 누락된 `userHeader` 구성
- 비어 있는 `allowUsers`(인증된 모든 사용자 허용)
- 노출된 제어 UI 표면에서 와일드카드 또는 누락된 브라우저 원본 정책

## 문제 해결

### "trusted_proxy_untrusted_source"

요청이 `gateway.trustedProxies`의 IP에서 오지 않았습니다. 다음을 확인하세요:

- 프록시 IP가 올바른가요? (Docker 컨테이너 IP는 바뀔 수 있음)
- 프록시 앞에 로드 밸런서가 있나요?
- 실제 IP를 찾으려면 `docker inspect` 또는 `kubectl get pods -o wide`를 사용하세요

### "trusted_proxy_loopback_source"

OpenClaw가 loopback 소스 trusted-proxy 요청을 거부했습니다.

다음을 확인하세요:

- 프록시가 `127.0.0.1` / `::1`에서 연결하고 있나요?
- 동일 호스트 loopback reverse proxy에서 trusted-proxy 인증을 사용하려고 하나요?

해결 방법:

- 동일 호스트 loopback 프록시 설정에서는 token/password 인증을 사용하거나
- non-loopback 신뢰 프록시 주소를 통해 라우팅하고 해당 IP를 `gateway.trustedProxies`에 유지하세요.

### "trusted_proxy_user_missing"

사용자 헤더가 비어 있거나 누락되었습니다. 다음을 확인하세요:

- 프록시가 ID 헤더를 전달하도록 구성되어 있나요?
- 헤더 이름이 올바른가요? (대소문자는 구분하지 않지만 철자는 중요함)
- 사용자가 실제로 프록시에서 인증되었나요?

### "trusted*proxy_missing_header*\*"

필수 헤더가 존재하지 않았습니다. 다음을 확인하세요:

- 해당 특정 헤더에 대한 프록시 구성
- 체인 중간에서 헤더가 제거되고 있지 않은지 여부

### "trusted_proxy_user_not_allowed"

사용자는 인증되었지만 `allowUsers`에 없습니다. 해당 사용자를 추가하거나 허용 목록을 제거하세요.

### "trusted_proxy_origin_not_allowed"

trusted-proxy 인증은 성공했지만, 브라우저 `Origin` 헤더가 제어 UI 원본 검사를 통과하지 못했습니다.

다음을 확인하세요:

- `gateway.controlUi.allowedOrigins`에 정확한 브라우저 원본이 포함되어 있는지
- 의도적으로 모두 허용하려는 경우가 아니라면 와일드카드 원본에 의존하지 않는지
- 의도적으로 Host 헤더 fallback 모드를 사용하는 경우 `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true`가 명시적으로 설정되어 있는지

### WebSocket이 여전히 실패하는 경우

프록시가 다음 조건을 만족하는지 확인하세요:

- WebSocket 업그레이드를 지원함(`Upgrade: websocket`, `Connection: upgrade`)
- HTTP뿐 아니라 WebSocket 업그레이드 요청에서도 ID 헤더를 전달함
- WebSocket 연결에 별도의 인증 경로가 없음

## Token 인증에서 마이그레이션

token 인증에서 trusted-proxy로 이동하는 경우:

1. 프록시가 사용자를 인증하고 헤더를 전달하도록 구성합니다
2. 프록시 설정을 독립적으로 테스트합니다(헤더와 함께 curl)
3. OpenClaw config를 trusted-proxy 인증으로 업데이트합니다
4. 게이트웨이를 다시 시작합니다
5. 제어 UI에서 WebSocket 연결을 테스트합니다
6. `openclaw security audit`를 실행하고 결과를 검토합니다

## 관련

- [보안](/gateway/security) — 전체 보안 가이드
- [구성](/gateway/configuration) — config 참조
- [원격 접근](/gateway/remote) — 기타 원격 접근 패턴
- [Tailscale](/gateway/tailscale) — tailnet 전용 접근을 위한 더 단순한 대안
