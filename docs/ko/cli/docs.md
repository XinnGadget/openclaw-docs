---
read_when:
    - 터미널에서 실시간 OpenClaw 문서를 검색하려는 경우
summary: '`openclaw docs`용 CLI 참조(실시간 문서 인덱스 검색)'
title: docs
x-i18n:
    generated_at: "2026-04-05T12:37:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfcceed872d7509b9843af3fae733a136bc5e26ded55c2ac47a16489a1636989
    source_path: cli/docs.md
    workflow: 15
---

# `openclaw docs`

실시간 문서 인덱스를 검색합니다.

인수:

- `[query...]`: 실시간 문서 인덱스로 보낼 검색어

예시:

```bash
openclaw docs
openclaw docs browser existing-session
openclaw docs sandbox allowHostControl
openclaw docs gateway token secretref
```

참고:

- 쿼리가 없으면 `openclaw docs`는 실시간 문서 검색 진입점을 엽니다.
- 여러 단어 쿼리는 하나의 검색 요청으로 그대로 전달됩니다.
