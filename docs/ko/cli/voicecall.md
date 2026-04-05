---
read_when:
    - voice-call plugin을 사용하며 CLI 진입점을 알고 싶을 때
    - '`voicecall call|continue|status|tail|expose`의 빠른 예시가 필요할 때'
summary: '`openclaw voicecall`용 CLI 참조(voice-call plugin 명령 표면)'
title: voicecall
x-i18n:
    generated_at: "2026-04-05T12:39:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2c99e7a3d256e1c74a0f07faba9675cc5a88b1eb2fc6e22993caf3874d4f340a
    source_path: cli/voicecall.md
    workflow: 15
---

# `openclaw voicecall`

`voicecall`은 plugin이 제공하는 명령입니다. voice-call plugin이 설치되고 활성화된 경우에만 표시됩니다.

기본 문서:

- voice-call plugin: [Voice Call](/plugins/voice-call)

## 일반적인 명령

```bash
openclaw voicecall status --call-id <id>
openclaw voicecall call --to "+15555550123" --message "Hello" --mode notify
openclaw voicecall continue --call-id <id> --message "Any questions?"
openclaw voicecall end --call-id <id>
```

## 웹훅 노출(Tailscale)

```bash
openclaw voicecall expose --mode serve
openclaw voicecall expose --mode funnel
openclaw voicecall expose --mode off
```

보안 참고: 웹훅 엔드포인트는 신뢰하는 네트워크에만 노출하세요. 가능하면 Funnel보다 Tailscale Serve를 우선하세요.
