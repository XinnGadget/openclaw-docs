---
read_when:
    - 모델 공급자를 선택하려는 경우
    - 지원되는 LLM 백엔드의 빠른 개요가 필요한 경우
summary: OpenClaw에서 지원하는 모델 공급자(LLM)
title: 공급자 디렉터리
x-i18n:
    generated_at: "2026-04-05T12:52:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 690d17c14576d454ea3cd3dcbc704470da10a2a34adfe681dab7048438f2e193
    source_path: providers/index.md
    workflow: 15
---

# 모델 공급자

OpenClaw는 많은 LLM 공급자를 사용할 수 있습니다. 공급자를 선택하고 인증한 다음 기본 모델을 `provider/model`로 설정하세요.

채팅 채널 문서(WhatsApp/Telegram/Discord/Slack/Mattermost (plugin)/기타)를 찾고 있나요? [채널](/ko/channels)을 참조하세요.

## 빠른 시작

1. 공급자로 인증합니다(보통 `openclaw onboard`를 통해).
2. 기본 모델을 설정합니다:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## 공급자 문서

- [Amazon Bedrock](/providers/bedrock)
- [Anthropic (API + Claude CLI)](/providers/anthropic)
- [BytePlus (International)](/ko/concepts/model-providers#byteplus-international)
- [Chutes](/ko/providers/chutes)
- [Cloudflare AI Gateway](/ko/providers/cloudflare-ai-gateway)
- [DeepSeek](/providers/deepseek)
- [Fireworks](/providers/fireworks)
- [GitHub Copilot](/providers/github-copilot)
- [GLM 모델](/providers/glm)
- [Google (Gemini)](/providers/google)
- [Groq (LPU 추론)](/providers/groq)
- [Hugging Face (추론)](/providers/huggingface)
- [Kilocode](/providers/kilocode)
- [LiteLLM (통합 게이트웨이)](/providers/litellm)
- [MiniMax](/providers/minimax)
- [Mistral](/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/providers/moonshot)
- [NVIDIA](/providers/nvidia)
- [Ollama (클라우드 + 로컬 모델)](/providers/ollama)
- [OpenAI (API + Codex)](/providers/openai)
- [OpenCode](/providers/opencode)
- [OpenCode Go](/providers/opencode-go)
- [OpenRouter](/providers/openrouter)
- [Perplexity (웹 검색)](/providers/perplexity-provider)
- [Qianfan](/providers/qianfan)
- [Qwen Cloud](/providers/qwen)
- [Qwen / Model Studio (엔드포인트 세부 정보; `qwen-*`가 정식이며 `modelstudio-*`는 레거시)](/providers/qwen_modelstudio)
- [SGLang (로컬 모델)](/providers/sglang)
- [StepFun](/providers/stepfun)
- [Synthetic](/providers/synthetic)
- [Together AI](/providers/together)
- [Venice (Venice AI, 개인 정보 보호 중심)](/providers/venice)
- [Vercel AI Gateway](/providers/vercel-ai-gateway)
- [vLLM (로컬 모델)](/providers/vllm)
- [Volcengine (Doubao)](/providers/volcengine)
- [xAI](/providers/xai)
- [Xiaomi](/providers/xiaomi)
- [Z.AI](/providers/zai)

## 공유 개요 페이지

- [추가 번들 변형](/providers/models#additional-bundled-provider-variants) - Anthropic Vertex, Copilot Proxy 및 Gemini CLI OAuth

## 전사 공급자

- [Deepgram (오디오 전사)](/providers/deepgram)

## 커뮤니티 도구

- [Claude Max API Proxy](/providers/claude-max-api-proxy) - Claude 구독 자격 증명을 위한 커뮤니티 프록시(사용 전에 Anthropic 정책/약관을 확인하세요)

전체 공급자 카탈로그(xAI, Groq, Mistral 등)와 고급 구성은 [모델 공급자](/ko/concepts/model-providers)를 참조하세요.
