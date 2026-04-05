---
read_when:
    - '`openclaw clawbot ...`를 사용하는 기존 스크립트를 유지 관리하는 경우'
    - 현재 명령으로의 마이그레이션 가이드가 필요한 경우
summary: '`openclaw clawbot`용 CLI 참조(레거시 별칭 네임스페이스)'
title: clawbot
x-i18n:
    generated_at: "2026-04-05T12:37:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1db82065ecb0107d1ab1a2c6ddaee9df1dd02b983ca1f759974c9d73f0ee3bde
    source_path: cli/clawbot.md
    workflow: 15
---

# `openclaw clawbot`

하위 호환성을 위해 유지되는 레거시 별칭 네임스페이스입니다.

현재 지원되는 별칭:

- `openclaw clawbot qr` (`openclaw qr`와 동일한 동작, [`openclaw qr`](/cli/qr) 참조)

## 마이그레이션

최신 최상위 명령을 직접 사용하는 것을 권장합니다.

- `openclaw clawbot qr` -> `openclaw qr`
