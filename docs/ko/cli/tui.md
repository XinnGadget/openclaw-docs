---
read_when:
    - Gateway용 터미널 UI가 필요할 때(원격 친화적)
    - 스크립트에서 url/token/session을 전달하고 싶을 때
summary: Gateway에 연결된 `openclaw tui`용 CLI 참조(터미널 UI)
title: tui
x-i18n:
    generated_at: "2026-04-05T12:39:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 60e35062c0551f85ce0da604a915b3e1ca2514d00d840afe3b94c529304c2c1a
    source_path: cli/tui.md
    workflow: 15
---

# `openclaw tui`

Gateway에 연결된 터미널 UI를 엽니다.

관련 항목:

- TUI 가이드: [TUI](/web/tui)

참고:

- `tui`는 가능할 때 token/password 인증을 위해 구성된 gateway auth SecretRef를 확인합니다(`env`/`file`/`exec` 제공자).
- 구성된 에이전트 워크스페이스 디렉터리 내부에서 실행되면, TUI는 세션 키 기본값으로 해당 에이전트를 자동 선택합니다(`--session`이 명시적으로 `agent:<id>:...`인 경우 제외).

## 예시

```bash
openclaw tui
openclaw tui --url ws://127.0.0.1:18789 --token <token>
openclaw tui --session main --deliver
# 에이전트 워크스페이스 내부에서 실행하면 해당 에이전트를 자동으로 추론
openclaw tui --session bugfix
```
