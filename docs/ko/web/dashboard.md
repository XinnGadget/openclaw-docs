---
read_when:
    - 대시보드 인증 또는 노출 모드를 변경하는 경우
summary: Gateway 대시보드(Control UI) 액세스 및 인증
title: 대시보드
x-i18n:
    generated_at: "2026-04-05T12:58:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 316e082ae4759f710b457487351e30c53b34c7c2b4bf84ad7b091a50538af5cc
    source_path: web/dashboard.md
    workflow: 15
---

# 대시보드(Control UI)

Gateway 대시보드는 기본적으로 `/`에서 제공되는 브라우저 Control UI입니다
(`gateway.controlUi.basePath`로 재정의 가능).

빠른 열기(로컬 Gateway):

- [http://127.0.0.1:18789/](http://127.0.0.1:18789/) (또는 [http://localhost:18789/](http://localhost:18789/))

주요 참조:

- 사용법과 UI 기능은 [Control UI](/web/control-ui)
- Serve/Funnel 자동화는 [Tailscale](/ko/gateway/tailscale)
- 바인드 모드와 보안 참고 사항은 [웹 표면](/web)

인증은 구성된 gateway
인증 경로를 통해 WebSocket 핸드셰이크에서 강제됩니다:

- `connect.params.auth.token`
- `connect.params.auth.password`
- `gateway.auth.allowTailscale: true`일 때의 Tailscale Serve identity 헤더
- `gateway.auth.mode: "trusted-proxy"`일 때의 trusted-proxy identity 헤더

자세한 내용은 [Gateway 구성](/ko/gateway/configuration)의 `gateway.auth`를 참고하세요.

보안 참고: Control UI는 **관리자 표면**입니다(채팅, config, exec 승인).
공개적으로 노출하지 마세요. UI는 현재 브라우저 탭 세션과 선택한 gateway URL에 대해
대시보드 URL 토큰을 sessionStorage에 유지하며, 로드 후 URL에서 제거합니다.
localhost, Tailscale Serve 또는 SSH 터널 사용을 권장합니다.

## 빠른 경로(권장)

- 온보딩 후 CLI가 자동으로 대시보드를 열고 깔끔한(토큰 없는) 링크를 출력합니다.
- 언제든 다시 열기: `openclaw dashboard` (링크 복사, 가능하면 브라우저 열기, headless면 SSH 힌트 표시).
- UI가 공유 비밀 인증을 요청하면 구성된 토큰 또는
  비밀번호를 Control UI 설정에 붙여 넣으세요.

## 인증 기본 사항(로컬 vs 원격)

- **Localhost**: `http://127.0.0.1:18789/`를 여세요.
- **공유 비밀 토큰 소스**: `gateway.auth.token`(또는
  `OPENCLAW_GATEWAY_TOKEN`); `openclaw dashboard`는 일회성 부트스트랩을 위해 URL fragment를 통해 이를 전달할 수 있으며, Control UI는 이를
  localStorage 대신 현재 브라우저 탭 세션과 선택한 gateway URL에 대해 sessionStorage에 유지합니다.
- `gateway.auth.token`이 SecretRef로 관리되면 `openclaw dashboard`는
  의도적으로 토큰 없는 URL을 출력/복사/엽니다. 이는 외부에서 관리되는 토큰이 셸 로그, 클립보드 기록 또는 브라우저 실행 인자에 노출되는 것을 방지합니다.
- `gateway.auth.token`이 SecretRef로 구성되어 있고 현재 셸에서 확인되지 않더라도, `openclaw dashboard`는 여전히 토큰 없는 URL과
  실행 가능한 인증 설정 안내를 출력합니다.
- **공유 비밀 비밀번호**: 구성된 `gateway.auth.password`(또는
  `OPENCLAW_GATEWAY_PASSWORD`)를 사용하세요. 대시보드는
  새로고침 사이에 비밀번호를 유지하지 않습니다.
- **identity-bearing 모드**: `gateway.auth.allowTailscale: true`일 때 Tailscale Serve는 identity 헤더를 통해 Control UI/WebSocket
  인증을 충족할 수 있으며, loopback이 아닌 identity-aware reverse proxy는
  `gateway.auth.mode: "trusted-proxy"`를 충족할 수 있습니다. 이 모드에서는 대시보드가 WebSocket용 공유 비밀을 붙여 넣을 필요가 없습니다.
- **localhost가 아님**: Tailscale Serve, loopback이 아닌 공유 비밀 바인드,
  `gateway.auth.mode: "trusted-proxy"`가 있는 loopback이 아닌 identity-aware reverse proxy,
  또는 SSH 터널을 사용하세요. HTTP API는 의도적으로 private-ingress
  `gateway.auth.mode: "none"` 또는 trusted-proxy HTTP auth를 실행하지 않는 한 여전히 공유 비밀 인증을 사용합니다. 자세한 내용은
  [웹 표면](/web)을 참고하세요.

<a id="if-you-see-unauthorized-1008"></a>

## "unauthorized" / 1008이 표시되는 경우

- gateway에 접근 가능한지 확인하세요(로컬: `openclaw status`; 원격: SSH 터널 `ssh -N -L 18789:127.0.0.1:18789 user@host` 후 `http://127.0.0.1:18789/` 열기).
- `AUTH_TOKEN_MISMATCH`의 경우 gateway가 재시도 힌트를 반환하면 클라이언트는 캐시된 장치 토큰으로 한 번 신뢰된 재시도를 할 수 있습니다. 이 캐시 토큰 재시도는 토큰의 캐시된 승인 범위를 재사용합니다. 명시적 `deviceToken` / 명시적 `scopes` 호출자는 요청한 범위 집합을 유지합니다. 해당 재시도 후에도 인증이 실패하면 수동으로 토큰 불일치를 해결하세요.
- 해당 재시도 경로 밖에서는 연결 인증 우선순위가 명확합니다. 먼저 명시적 공유 토큰/비밀번호, 그다음 명시적 `deviceToken`, 그다음 저장된 장치 토큰, 마지막으로 부트스트랩 토큰입니다.
- 비동기 Tailscale Serve Control UI 경로에서는 같은
  `{scope, ip}`에 대한 실패 시도가 failed-auth limiter에 기록되기 전에 직렬화되므로, 두 번째 동시 잘못된 재시도에서는 이미 `retry later`가 표시될 수 있습니다.
- 토큰 불일치 복구 단계는 [토큰 불일치 복구 체크리스트](/cli/devices#token-drift-recovery-checklist)를 따르세요.
- gateway host에서 공유 비밀을 가져오거나 제공하세요:
  - 토큰: `openclaw config get gateway.auth.token`
  - 비밀번호: 구성된 `gateway.auth.password` 또는
    `OPENCLAW_GATEWAY_PASSWORD` 확인
  - SecretRef 관리 토큰: 외부 시크릿 제공자를 확인하거나
    이 셸에 `OPENCLAW_GATEWAY_TOKEN`을 내보낸 다음 `openclaw dashboard`를 다시 실행
  - 공유 비밀이 구성되지 않은 경우: `openclaw doctor --generate-gateway-token`
- 대시보드 설정에서 인증 필드에 토큰 또는 비밀번호를 붙여 넣은 다음,
  연결하세요.
