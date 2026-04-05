---
read_when:
    - BOOT.md 체크리스트를 추가하고 있습니다
summary: BOOT.md용 워크스페이스 템플릿
title: BOOT.md 템플릿
x-i18n:
    generated_at: "2026-04-05T12:54:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 694e836d2c4010bf723d0e64f40e98800d3c135ca4c4124d42f96f5e050936f8
    source_path: reference/templates/BOOT.md
    workflow: 15
---

# BOOT.md

시작 시 OpenClaw가 수행해야 할 작업에 대해 짧고 명확한 지침을 추가하세요(`hooks.internal.enabled` 활성화).
작업이 메시지를 보내는 경우 message tool을 사용한 다음, 정확한
무응답 토큰 `NO_REPLY` / `no_reply`로 응답하세요.
