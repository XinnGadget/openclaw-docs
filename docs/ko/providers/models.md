---
read_when:
    - 모델 제공자를 선택하려는 경우
    - LLM 인증 + 모델 선택을 위한 빠른 설정 예시가 필요한 경우
summary: OpenClaw에서 지원하는 모델 제공자(LLM)
title: 모델 제공자 빠른 시작
x-i18n:
    generated_at: "2026-04-05T12:52:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: 83e372193b476c7cee6eb9f5c443b03563d863043f47c633ac0096bca642cc6f
    source_path: providers/models.md
    workflow: 15
---

# 모델 제공자

OpenClaw는 많은 LLM 제공자를 사용할 수 있습니다. 하나를 선택하고 인증한 다음 기본
모델을 `provider/model`로 설정하세요.

## 빠른 시작(두 단계)

1. 제공자에 인증합니다(보통 `openclaw onboard`를 통해).
2. 기본 모델을 설정합니다:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## 지원되는 제공자(시작용 목록)

- [Anthropic (API + Claude CLI)](/providers/anthropic)
- [Amazon Bedrock](/providers/bedrock)
- [BytePlus (International)](/ko/concepts/model-providers#byteplus-international)
- [Chutes](/ko/providers/chutes)
- [Cloudflare AI Gateway](/ko/providers/cloudflare-ai-gateway)
- [Fireworks](/providers/fireworks)
- [GLM 모델](/providers/glm)
- [MiniMax](/providers/minimax)
- [Mistral](/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/providers/moonshot)
- [OpenAI (API + Codex)](/providers/openai)
- [OpenCode (Zen + Go)](/providers/opencode)
- [OpenRouter](/providers/openrouter)
- [Qianfan](/providers/qianfan)
- [Qwen](/providers/qwen)
- [StepFun](/providers/stepfun)
- [Synthetic](/providers/synthetic)
- [Vercel AI Gateway](/providers/vercel-ai-gateway)
- [Venice (Venice AI)](/providers/venice)
- [xAI](/providers/xai)
- [Z.AI](/providers/zai)

## 추가 번들 제공자 변형

- `anthropic-vertex` - Vertex 자격 증명을 사용할 수 있을 때 암시적으로 지원되는 Google Vertex의 Anthropic입니다. 별도의 온보딩 인증 선택은 없습니다
- `copilot-proxy` - 로컬 VS Code Copilot Proxy 브리지입니다. `openclaw onboard --auth-choice copilot-proxy`를 사용하세요
- `google-gemini-cli` - 비공식 Gemini CLI OAuth 흐름입니다. 로컬 `gemini` 설치가 필요합니다(`brew install gemini-cli` 또는 `npm install -g @google/gemini-cli`). 기본 모델은 `google-gemini-cli/gemini-3.1-pro-preview`이며, `openclaw onboard --auth-choice google-gemini-cli` 또는 `openclaw models auth login --provider google-gemini-cli --set-default`를 사용하세요

전체 제공자 카탈로그(xAI, Groq, Mistral 등)와 고급 설정은
[모델 제공자](/ko/concepts/model-providers)를 참고하세요.
