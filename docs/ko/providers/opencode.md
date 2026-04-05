---
read_when:
    - OpenCode 호스팅 모델 액세스를 사용하려는 경우
    - Zen 및 Go 카탈로그 중에서 선택하려는 경우
summary: OpenClaw에서 OpenCode Zen 및 Go 카탈로그를 사용합니다
title: OpenCode
x-i18n:
    generated_at: "2026-04-05T12:52:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: c23bc99208d9275afcb1731c28eee250c9f4b7d0578681ace31416135c330865
    source_path: providers/opencode.md
    workflow: 15
---

# OpenCode

OpenCode는 OpenClaw에서 두 개의 호스팅 카탈로그를 제공합니다:

- **Zen** 카탈로그용 `opencode/...`
- **Go** 카탈로그용 `opencode-go/...`

두 카탈로그 모두 동일한 OpenCode API 키를 사용합니다. OpenClaw는 업스트림 모델별
라우팅이 올바르게 유지되도록 런타임 provider id를 분리해 두지만, onboarding 및 문서에서는
이를 하나의 OpenCode 설정으로 취급합니다.

## CLI 설정

### Zen 카탈로그

```bash
openclaw onboard --auth-choice opencode-zen
openclaw onboard --opencode-zen-api-key "$OPENCODE_API_KEY"
```

### Go 카탈로그

```bash
openclaw onboard --auth-choice opencode-go
openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
```

## 구성 스니펫

```json5
{
  env: { OPENCODE_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

## 카탈로그

### Zen

- 런타임 provider: `opencode`
- 예시 모델: `opencode/claude-opus-4-6`, `opencode/gpt-5.4`, `opencode/gemini-3-pro`
- 엄선된 OpenCode 멀티모델 프록시를 원하는 경우에 가장 적합합니다

### Go

- 런타임 provider: `opencode-go`
- 예시 모델: `opencode-go/kimi-k2.5`, `opencode-go/glm-5`, `opencode-go/minimax-m2.5`
- OpenCode 호스팅 Kimi/GLM/MiniMax 라인업을 원하는 경우에 가장 적합합니다

## 참고

- `OPENCODE_ZEN_API_KEY`도 지원됩니다.
- 설정 중 하나의 OpenCode 키를 입력하면 두 런타임 provider 모두에 대한 자격 증명이 저장됩니다.
- OpenCode에 로그인하고, 결제 정보를 추가한 다음, API 키를 복사하면 됩니다.
- 과금 및 카탈로그 제공 여부는 OpenCode 대시보드에서 관리됩니다.
- Gemini 기반 OpenCode 참조는 프록시-Gemini 경로에 그대로 유지되므로, OpenClaw는
  네이티브 Gemini 재생 검증이나 bootstrap 재작성은 활성화하지 않으면서 그 경로에서
  Gemini thought-signature 정리를 유지합니다.
- Gemini가 아닌 OpenCode 참조는 최소한의 OpenAI 호환 재생 정책을 유지합니다.
