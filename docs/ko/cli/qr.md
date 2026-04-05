---
read_when:
    - 모바일 노드 앱을 gateway와 빠르게 페어링하려고 함
    - 원격/수동 공유를 위한 설정 코드 출력이 필요함
summary: '`openclaw qr`용 CLI 참조(모바일 페어링 QR + 설정 코드 생성)'
title: qr
x-i18n:
    generated_at: "2026-04-05T12:38:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: ee6469334ad09037318f938c7ac609b7d5e3385c0988562501bb02a1bfa411ff
    source_path: cli/qr.md
    workflow: 15
---

# `openclaw qr`

현재 Gateway 구성에서 모바일 페어링 QR과 설정 코드를 생성합니다.

## 사용법

```bash
openclaw qr
openclaw qr --setup-code-only
openclaw qr --json
openclaw qr --remote
openclaw qr --url wss://gateway.example/ws
```

## 옵션

- `--remote`: `gateway.remote.url`을 우선 사용합니다. 이 값이 설정되지 않은 경우에도 `gateway.tailscale.mode=serve|funnel`이 원격 공개 URL을 제공할 수 있습니다
- `--url <url>`: 페이로드에 사용되는 gateway URL 재정의
- `--public-url <url>`: 페이로드에 사용되는 공개 URL 재정의
- `--token <token>`: bootstrap 흐름이 인증에 사용할 gateway 토큰 재정의
- `--password <password>`: bootstrap 흐름이 인증에 사용할 gateway 비밀번호 재정의
- `--setup-code-only`: 설정 코드만 출력
- `--no-ascii`: ASCII QR 렌더링 건너뛰기
- `--json`: JSON 출력(`setupCode`, `gatewayUrl`, `auth`, `urlSource`)

## 참고

- `--token`과 `--password`는 함께 사용할 수 없습니다.
- 이제 설정 코드 자체에는 공유 gateway 토큰/비밀번호가 아니라 불투명한 단기 `bootstrapToken`이 포함됩니다.
- 내장된 node/operator bootstrap 흐름에서 기본 노드 토큰은 여전히 `scopes: []`로 설정됩니다.
- bootstrap 핸드오프가 operator 토큰도 발급하는 경우, 그것은 bootstrap allowlist인 `operator.approvals`, `operator.read`, `operator.talk.secrets`, `operator.write` 범위 내로 제한됩니다.
- Bootstrap scope 검사는 역할 접두사 기반입니다. 해당 operator allowlist는 operator 요청에만 적용되며, operator가 아닌 역할은 여전히 자기 역할 접두사 아래의 scopes가 필요합니다.
- Tailscale/공개 `ws://` gateway URL에서는 모바일 페어링이 fail closed 처리됩니다. 비공개 LAN `ws://`는 계속 지원되지만, Tailscale/공개 모바일 경로에는 Tailscale Serve/Funnel 또는 `wss://` gateway URL을 사용해야 합니다.
- `--remote`를 사용할 때 OpenClaw는 `gateway.remote.url` 또는
  `gateway.tailscale.mode=serve|funnel` 중 하나를 요구합니다.
- `--remote`를 사용할 때, 실질적으로 활성화된 원격 자격 증명이 SecretRef로 구성되어 있고 `--token` 또는 `--password`를 전달하지 않으면, 명령은 활성 gateway 스냅샷에서 해당 값을 확인합니다. gateway를 사용할 수 없으면 명령은 즉시 실패합니다.
- `--remote` 없이 실행할 때는 CLI 인증 재정의를 전달하지 않은 경우 로컬 gateway 인증 SecretRef가 확인됩니다.
  - 토큰 인증이 우선될 수 있을 때 `gateway.auth.token`이 확인됩니다(명시적 `gateway.auth.mode="token"` 또는 비밀번호 소스가 우선하지 않는 추론 모드).
  - 비밀번호 인증이 우선될 수 있을 때 `gateway.auth.password`가 확인됩니다(명시적 `gateway.auth.mode="password"` 또는 auth/env에서 우선 토큰이 없는 추론 모드).
- `gateway.auth.token`과 `gateway.auth.password`가 모두 구성되어 있고(SecretRef 포함) `gateway.auth.mode`가 설정되지 않은 경우, 명시적으로 모드를 설정할 때까지 설정 코드 확인은 실패합니다.
- Gateway 버전 불일치 참고: 이 명령 경로에는 `secrets.resolve`를 지원하는 gateway가 필요합니다. 오래된 gateway는 unknown-method 오류를 반환합니다.
- 스캔 후에는 다음 명령으로 기기 페어링을 승인하세요.
  - `openclaw devices list`
  - `openclaw devices approve <requestId>`
