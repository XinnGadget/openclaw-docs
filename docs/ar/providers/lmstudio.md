---
read_when:
    - تريد تشغيل OpenClaw باستخدام نماذج مفتوحة المصدر عبر LM Studio
    - تريد إعداد LM Studio وتكوينه
summary: شغّل OpenClaw باستخدام LM Studio
title: LM Studio
x-i18n:
    generated_at: "2026-04-13T07:28:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 11264584e8277260d4215feb7c751329ce04f59e9228da1c58e147c21cd9ac2c
    source_path: providers/lmstudio.md
    workflow: 15
---

# LM Studio

يُعد LM Studio تطبيقًا سهل الاستخدام لكنه قوي لتشغيل النماذج مفتوحة الأوزان على أجهزتك الخاصة. يتيح لك تشغيل نماذج llama.cpp ‏(GGUF) أو MLX ‏(Apple Silicon). يتوفر كحزمة بواجهة رسومية أو كخادم دون واجهة (`llmster`). للاطلاع على وثائق المنتج والإعداد، راجع [lmstudio.ai](https://lmstudio.ai/).

## البدء السريع

1. ثبّت LM Studio (سطح المكتب) أو `llmster` (دون واجهة)، ثم ابدأ الخادم المحلي:

```bash
curl -fsSL https://lmstudio.ai/install.sh | bash
```

2. ابدأ الخادم

تأكد من أنك إما تشغّل تطبيق سطح المكتب أو تشغّل الخادم باستخدام الأمر التالي:

```bash
lms daemon up
```

```bash
lms server start --port 1234
```

إذا كنت تستخدم التطبيق، فتأكد من تمكين JIT للحصول على تجربة سلسة. تعرّف على المزيد في [دليل JIT وTTL في LM Studio](https://lmstudio.ai/docs/developer/core/ttl-and-auto-evict).

3. يتطلب OpenClaw قيمة رمز مميز لـ LM Studio. اضبط `LM_API_TOKEN`:

```bash
export LM_API_TOKEN="your-lm-studio-api-token"
```

إذا كانت المصادقة معطّلة في LM Studio، فاستخدم أي قيمة رمز مميز غير فارغة:

```bash
export LM_API_TOKEN="placeholder-key"
```

للحصول على تفاصيل إعداد المصادقة في LM Studio، راجع [مصادقة LM Studio](https://lmstudio.ai/docs/developer/core/authentication).

4. شغّل الإعداد الأولي واختر `LM Studio`:

```bash
openclaw onboard
```

5. أثناء الإعداد الأولي، استخدم موجّه `Default model` لاختيار نموذج LM Studio الخاص بك.

يمكنك أيضًا تعيينه أو تغييره لاحقًا:

```bash
openclaw models set lmstudio/qwen/qwen3.5-9b
```

تتبع مفاتيح نماذج LM Studio تنسيق `author/model-name` (مثل `qwen/qwen3.5-9b`). وتضيف مراجع نماذج OpenClaw اسم المزوّد في البداية: `lmstudio/qwen/qwen3.5-9b`. يمكنك العثور على المفتاح الدقيق لأي نموذج عبر تشغيل `curl http://localhost:1234/api/v1/models` والنظر إلى الحقل `key`.

## الإعداد الأولي غير التفاعلي

استخدم الإعداد الأولي غير التفاعلي عندما تريد إعدادًا قابلًا للبرمجة النصية (CI، التهيئة، الإقلاع الأولي عن بُعد):

```bash
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --auth-choice lmstudio
```

أو حدّد عنوان URL الأساسي أو النموذج مع مفتاح API:

```bash
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --auth-choice lmstudio \
  --custom-base-url http://localhost:1234/v1 \
  --lmstudio-api-key "$LM_API_TOKEN" \
  --custom-model-id qwen/qwen3.5-9b
```

يأخذ `--custom-model-id` مفتاح النموذج كما يعيده LM Studio (مثل `qwen/qwen3.5-9b`)، من دون بادئة المزوّد `lmstudio/`.

يتطلب الإعداد الأولي غير التفاعلي `--lmstudio-api-key` (أو `LM_API_TOKEN` في البيئة).
وبالنسبة إلى خوادم LM Studio غير التي تتطلب المصادقة، تعمل أي قيمة رمز مميز غير فارغة.

يبقى `--custom-api-key` مدعومًا للتوافق، لكن يُفضّل `--lmstudio-api-key` مع LM Studio.

يكتب هذا `models.providers.lmstudio`، ويضبط النموذج الافتراضي إلى
`lmstudio/<custom-model-id>`، ويكتب ملف تعريف المصادقة `lmstudio:default`.

يمكن للإعداد التفاعلي أن يطلب طول سياق تحميل مفضّل اختياريًا ويطبّقه على نماذج LM Studio المكتشفة التي يحفظها في الإعدادات.

## الإعدادات

### إعدادات صريحة

```json5
{
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "${LM_API_TOKEN}",
        api: "openai-completions",
        models: [
          {
            id: "qwen/qwen3-coder-next",
            name: "Qwen 3 Coder Next",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## استكشاف الأخطاء وإصلاحها

### لم يتم اكتشاف LM Studio

تأكد من أن LM Studio قيد التشغيل وأنك قمت بتعيين `LM_API_TOKEN` (وبالنسبة إلى الخوادم غير التي تتطلب المصادقة، تعمل أي قيمة رمز مميز غير فارغة):

```bash
# Start via desktop app, or headless:
lms server start --port 1234
```

تحقق من إمكانية الوصول إلى API:

```bash
curl http://localhost:1234/api/v1/models
```

### أخطاء المصادقة (HTTP 401)

إذا أبلغ الإعداد عن HTTP 401، فتحقق من مفتاح API الخاص بك:

- تأكد من أن `LM_API_TOKEN` يطابق المفتاح المهيأ في LM Studio.
- للحصول على تفاصيل إعداد المصادقة في LM Studio، راجع [مصادقة LM Studio](https://lmstudio.ai/docs/developer/core/authentication).
- إذا كان الخادم لا يتطلب المصادقة، فاستخدم أي قيمة رمز مميز غير فارغة لـ `LM_API_TOKEN`.

### تحميل النموذج عند الطلب

يدعم LM Studio تحميل النماذج عند الطلب (JIT)، حيث تُحمَّل النماذج عند أول طلب. تأكد من تمكين هذا لتجنب أخطاء "Model not loaded".
