---
read_when:
    - Chcesz wybrać dostawcę modeli
    - Chcesz zobaczyć szybkie przykłady konfiguracji uwierzytelniania LLM i wyboru modelu
summary: Dostawcy modeli (LLM) obsługiwani przez OpenClaw
title: Szybki start z dostawcami modeli
x-i18n:
    generated_at: "2026-04-06T03:11:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: c0314fb1c754171e5fc252d30f7ba9bb6acdbb978d97e9249264d90351bac2e7
    source_path: providers/models.md
    workflow: 15
---

# Dostawcy modeli

OpenClaw może używać wielu dostawców LLM. Wybierz jednego, uwierzytelnij się, a następnie ustaw domyślny
model jako `provider/model`.

## Szybki start (dwa kroki)

1. Uwierzytelnij się u dostawcy (zwykle przez `openclaw onboard`).
2. Ustaw model domyślny:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Obsługiwani dostawcy (zestaw startowy)

- [Alibaba Model Studio](/providers/alibaba)
- [Anthropic (API + Claude CLI)](/pl/providers/anthropic)
- [Amazon Bedrock](/pl/providers/bedrock)
- [BytePlus (międzynarodowy)](/pl/concepts/model-providers#byteplus-international)
- [Chutes](/pl/providers/chutes)
- [ComfyUI](/providers/comfy)
- [Cloudflare AI Gateway](/pl/providers/cloudflare-ai-gateway)
- [fal](/providers/fal)
- [Fireworks](/pl/providers/fireworks)
- [Modele GLM](/pl/providers/glm)
- [MiniMax](/pl/providers/minimax)
- [Mistral](/pl/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/pl/providers/moonshot)
- [OpenAI (API + Codex)](/pl/providers/openai)
- [OpenCode (Zen + Go)](/pl/providers/opencode)
- [OpenRouter](/pl/providers/openrouter)
- [Qianfan](/pl/providers/qianfan)
- [Qwen](/pl/providers/qwen)
- [Runway](/providers/runway)
- [StepFun](/pl/providers/stepfun)
- [Synthetic](/pl/providers/synthetic)
- [Vercel AI Gateway](/pl/providers/vercel-ai-gateway)
- [Venice (Venice AI)](/pl/providers/venice)
- [xAI](/pl/providers/xai)
- [Z.AI](/pl/providers/zai)

## Dodatkowe warianty wbudowanych dostawców

- `anthropic-vertex` - niejawna obsługa Anthropic w Google Vertex, gdy dostępne są poświadczenia Vertex; brak osobnej opcji uwierzytelniania w onboardingu
- `copilot-proxy` - lokalny most VS Code Copilot Proxy; użyj `openclaw onboard --auth-choice copilot-proxy`

Pełny katalog dostawców (xAI, Groq, Mistral itd.) oraz konfigurację zaawansowaną znajdziesz w [Dostawcy modeli](/pl/concepts/model-providers).
