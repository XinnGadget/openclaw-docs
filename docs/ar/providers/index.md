---
read_when:
    - تريد اختيار موفّر نماذج
    - تحتاج إلى نظرة عامة سريعة على الواجهات الخلفية المدعومة لـ LLM
summary: موفرو النماذج (LLMs) المدعومون بواسطة OpenClaw
title: دليل المزوّدين
x-i18n:
    generated_at: "2026-04-13T07:28:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3bc682d008119719826f71f74959ab32bedf14214459f5e6ac9cb70371d3c540
    source_path: providers/index.md
    workflow: 15
---

# موفرو النماذج

يمكن لـ OpenClaw استخدام العديد من موفري LLM. اختر موفّرًا، وأكمل المصادقة، ثم عيّن
النموذج الافتراضي بصيغة `provider/model`.

هل تبحث عن وثائق قنوات الدردشة (WhatsApp/Telegram/Discord/Slack/Mattermost (Plugin)/إلخ)؟ راجع [القنوات](/ar/channels).

## البدء السريع

1. أكمل المصادقة مع المزوّد (عادةً عبر `openclaw onboard`).
2. عيّن النموذج الافتراضي:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## وثائق المزوّدين

- [Alibaba Model Studio](/ar/providers/alibaba)
- [Amazon Bedrock](/ar/providers/bedrock)
- [Anthropic (API + Claude CLI)](/ar/providers/anthropic)
- [Arcee AI (نماذج Trinity)](/ar/providers/arcee)
- [BytePlus (دولي)](/ar/concepts/model-providers#byteplus-international)
- [Chutes](/ar/providers/chutes)
- [ComfyUI](/ar/providers/comfy)
- [Cloudflare AI Gateway](/ar/providers/cloudflare-ai-gateway)
- [DeepSeek](/ar/providers/deepseek)
- [fal](/ar/providers/fal)
- [Fireworks](/ar/providers/fireworks)
- [GitHub Copilot](/ar/providers/github-copilot)
- [نماذج GLM](/ar/providers/glm)
- [Google (Gemini)](/ar/providers/google)
- [Groq (استدلال LPU)](/ar/providers/groq)
- [Hugging Face (الاستدلال)](/ar/providers/huggingface)
- [inferrs (نماذج محلية)](/ar/providers/inferrs)
- [Kilocode](/ar/providers/kilocode)
- [LiteLLM (بوابة موحّدة)](/ar/providers/litellm)
- [LM Studio (نماذج محلية)](/ar/providers/lmstudio)
- [MiniMax](/ar/providers/minimax)
- [Mistral](/ar/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/ar/providers/moonshot)
- [NVIDIA](/ar/providers/nvidia)
- [Ollama (نماذج سحابية + محلية)](/ar/providers/ollama)
- [OpenAI (API + Codex)](/ar/providers/openai)
- [OpenCode](/ar/providers/opencode)
- [OpenCode Go](/ar/providers/opencode-go)
- [OpenRouter](/ar/providers/openrouter)
- [Perplexity (البحث على الويب)](/ar/providers/perplexity-provider)
- [Qianfan](/ar/providers/qianfan)
- [Qwen Cloud](/ar/providers/qwen)
- [Runway](/ar/providers/runway)
- [SGLang (نماذج محلية)](/ar/providers/sglang)
- [StepFun](/ar/providers/stepfun)
- [Synthetic](/ar/providers/synthetic)
- [Together AI](/ar/providers/together)
- [Venice (Venice AI، مع تركيز على الخصوصية)](/ar/providers/venice)
- [Vercel AI Gateway](/ar/providers/vercel-ai-gateway)
- [Vydra](/ar/providers/vydra)
- [vLLM (نماذج محلية)](/ar/providers/vllm)
- [Volcengine (Doubao)](/ar/providers/volcengine)
- [xAI](/ar/providers/xai)
- [Xiaomi](/ar/providers/xiaomi)
- [Z.AI](/ar/providers/zai)

## صفحات النظرة العامة المشتركة

- [متغيرات إضافية مضمّنة](/ar/providers/models#additional-bundled-provider-variants) - Anthropic Vertex وCopilot Proxy وGemini CLI OAuth
- [توليد الصور](/ar/tools/image-generation) - أداة `image_generate` المشتركة، واختيار المزوّد، والتبديل التلقائي عند الفشل
- [توليد الموسيقى](/ar/tools/music-generation) - أداة `music_generate` المشتركة، واختيار المزوّد، والتبديل التلقائي عند الفشل
- [توليد الفيديو](/ar/tools/video-generation) - أداة `video_generate` المشتركة، واختيار المزوّد، والتبديل التلقائي عند الفشل

## مزودو التفريغ النصي

- [Deepgram (تفريغ نصي للصوت)](/ar/providers/deepgram)

## أدوات المجتمع

- [Claude Max API Proxy](/ar/providers/claude-max-api-proxy) - وكيل مجتمع لبيانات اعتماد اشتراك Claude (تحقق من سياسة Anthropic/الشروط قبل الاستخدام)

للحصول على فهرس المزوّدين الكامل (xAI وGroq وMistral وما إلى ذلك) والإعدادات المتقدمة،
راجع [موفرو النماذج](/ar/concepts/model-providers).
