---
read_when:
    - zsh/bash/fish/PowerShell용 셸 자동 완성이 필요할 때
    - OpenClaw 상태 아래에 자동 완성 스크립트를 캐시해야 할 때
summary: '`openclaw completion`용 CLI 참조(셸 자동 완성 스크립트 생성/설치)'
title: completion
x-i18n:
    generated_at: "2026-04-05T12:37:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7bbf140a880bafdb7140149f85465d66d0d46e5a3da6a1e41fb78be2fd2bd4d0
    source_path: cli/completion.md
    workflow: 15
---

# `openclaw completion`

셸 자동 완성 스크립트를 생성하고, 선택적으로 셸 프로필에 설치합니다.

## 사용법

```bash
openclaw completion
openclaw completion --shell zsh
openclaw completion --install
openclaw completion --shell fish --install
openclaw completion --write-state
openclaw completion --shell bash --write-state
```

## 옵션

- `-s, --shell <shell>`: 셸 대상(`zsh`, `bash`, `powershell`, `fish`; 기본값: `zsh`)
- `-i, --install`: 셸 프로필에 source 줄을 추가하여 자동 완성 설치
- `--write-state`: 스크립트를 stdout에 출력하지 않고 `$OPENCLAW_STATE_DIR/completions`에 자동 완성 스크립트를 작성
- `-y, --yes`: 설치 확인 프롬프트 건너뛰기

## 참고

- `--install`은 셸 프로필에 작은 "OpenClaw Completion" 블록을 작성하고 이를 캐시된 스크립트에 연결합니다.
- `--install`이나 `--write-state`가 없으면 명령은 스크립트를 stdout에 출력합니다.
- 자동 완성 생성은 중첩된 하위 명령이 포함되도록 명령 트리를 eager 로드합니다.
