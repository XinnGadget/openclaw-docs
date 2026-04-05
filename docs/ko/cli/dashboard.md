---
read_when:
    - 현재 토큰으로 Control UI를 열려는 경우
    - 브라우저를 실행하지 않고 URL을 출력하려는 경우
summary: '`openclaw dashboard`용 CLI 참조(Control UI 열기)'
title: dashboard
x-i18n:
    generated_at: "2026-04-05T12:37:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: a34cd109a3803e2910fcb4d32f2588aa205a4933819829ef5598f0780f586c94
    source_path: cli/dashboard.md
    workflow: 15
---

# `openclaw dashboard`

현재 인증을 사용해 Control UI를 엽니다.

```bash
openclaw dashboard
openclaw dashboard --no-open
```

참고:

- `dashboard`는 가능할 경우 구성된 `gateway.auth.token` SecretRef를 해석합니다.
- SecretRef로 관리되는 토큰(해석되었거나 해석되지 않았거나)의 경우, `dashboard`는 외부 시크릿이 터미널 출력, 클립보드 기록 또는 브라우저 실행 인수에 노출되지 않도록 토큰이 포함되지 않은 URL을 출력/복사/엽니다.
- `gateway.auth.token`이 SecretRef로 관리되지만 이 명령 경로에서 해석되지 않은 경우, 이 명령은 잘못된 토큰 플레이스홀더를 포함하는 대신 토큰이 없는 URL과 명시적인 해결 지침을 출력합니다.
