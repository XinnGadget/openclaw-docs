---
read_when:
    - تريد اختيار مزوّد نموذج
    - تريد أمثلة إعداد سريعة لمصادقة LLM + اختيار النموذج
summary: مزوّدو النماذج (LLMs) الذين يدعمهم OpenClaw
title: البدء السريع لمزوّد النماذج
x-i18n:
    generated_at: "2026-04-07T07:21:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 500191bfe853241096f97928ced2327a13b6f7f62003cb7452b24886c272e6ba
    source_path: providers/models.md
    workflow: 15
---

# مزودو النماذج

يمكن لـ OpenClaw استخدام العديد من مزوّدي LLM. اختر واحدًا، ثم صادق، ثم اضبط
النموذج الافتراضي بصيغة `provider/model`.

## البدء السريع (خطوتان)

1. صادق مع المزوّد (عادةً عبر `openclaw onboard`).
2. اضبط النموذج الافتراضي:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## المزوّدون المدعومون (المجموعة الابتدائية)

- [Alibaba Model Studio](/ar/providers/alibaba)
- [Anthropic (API + Claude CLI)](/ar/providers/anthropic)
- [Amazon Bedrock](/ar/providers/bedrock)
- [BytePlus (دولي)](/ar/concepts/model-providers#byteplus-international)
- [Chutes](/ar/providers/chutes)
- [ComfyUI](/ar/providers/comfy)
- [Cloudflare AI Gateway](/ar/providers/cloudflare-ai-gateway)
- [fal](/ar/providers/fal)
- [Fireworks](/ar/providers/fireworks)
- [نماذج GLM](/ar/providers/glm)
- [MiniMax](/ar/providers/minimax)
- [Mistral](/ar/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/ar/providers/moonshot)
- [OpenAI (API + Codex)](/ar/providers/openai)
- [OpenCode (Zen + Go)](/ar/providers/opencode)
- [OpenRouter](/ar/providers/openrouter)
- [Qianfan](/ar/providers/qianfan)
- [Qwen](/ar/providers/qwen)
- [Runway](/ar/providers/runway)
- [StepFun](/ar/providers/stepfun)
- [Synthetic](/ar/providers/synthetic)
- [Vercel AI Gateway](/ar/providers/vercel-ai-gateway)
- [Venice (Venice AI)](/ar/providers/venice)
- [xAI](/ar/providers/xai)
- [Z.AI](/ar/providers/zai)

## متغيرات المزوّدات المضمّنة الإضافية

- `anthropic-vertex` - دعم Anthropic ضمن Google Vertex بشكل ضمني عندما تكون بيانات اعتماد Vertex متاحة؛ لا يوجد خيار مصادقة onboarding منفصل
- `copilot-proxy` - جسر Copilot Proxy محلي لـ VS Code؛ استخدم `openclaw onboard --auth-choice copilot-proxy`
- `google-gemini-cli` - تدفق OAuth غير رسمي لـ Gemini CLI؛ يتطلب تثبيت `gemini` محليًا (`brew install gemini-cli` أو `npm install -g @google/gemini-cli`)؛ النموذج الافتراضي هو `google-gemini-cli/gemini-3.1-pro-preview`؛ استخدم `openclaw onboard --auth-choice google-gemini-cli` أو `openclaw models auth login --provider google-gemini-cli --set-default`

للاطلاع على كتالوج المزوّدين الكامل (xAI وGroq وMistral وما إلى ذلك) والإعدادات المتقدمة،
راجع [مزوّدو النماذج](/ar/concepts/model-providers).
