---
read_when:
    - تريد تشغيل OpenClaw مقابل خادم inferrs محلي
    - أنت تقدّم Gemma أو نموذجًا آخر عبر inferrs
    - تحتاج إلى علامات التوافق الدقيقة في OpenClaw الخاصة بـ inferrs
summary: تشغيل OpenClaw عبر inferrs (خادم محلي متوافق مع OpenAI)
title: inferrs
x-i18n:
    generated_at: "2026-04-09T01:29:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 03b9d5a9935c75fd369068bacb7807a5308cd0bd74303b664227fb664c3a2098
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

يمكن لـ [inferrs](https://github.com/ericcurtin/inferrs) تقديم النماذج المحلية خلف
واجهة `/v1` API متوافقة مع OpenAI. يعمل OpenClaw مع `inferrs` عبر المسار العام
`openai-completions`.

من الأفضل حاليًا التعامل مع `inferrs` كخلفية مخصصة مستضافة ذاتيًا ومتوافقة مع OpenAI،
وليس كإضافة موفر مخصصة في OpenClaw.

## بدء سريع

1. ابدأ `inferrs` مع نموذج.

مثال:

```bash
inferrs serve google/gemma-4-E2B-it \
  --host 127.0.0.1 \
  --port 8080 \
  --device metal
```

2. تحقق من إمكانية الوصول إلى الخادم.

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

3. أضف إدخال موفر صريحًا في OpenClaw ووجّه نموذجك الافتراضي إليه.

## مثال إعداد كامل

يستخدم هذا المثال Gemma 4 على خادم `inferrs` محلي.

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/google/gemma-4-E2B-it" },
      models: {
        "inferrs/google/gemma-4-E2B-it": {
          alias: "Gemma 4 (inferrs)",
        },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      inferrs: {
        baseUrl: "http://127.0.0.1:8080/v1",
        apiKey: "inferrs-local",
        api: "openai-completions",
        models: [
          {
            id: "google/gemma-4-E2B-it",
            name: "Gemma 4 E2B (inferrs)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 131072,
            maxTokens: 4096,
            compat: {
              requiresStringContent: true,
            },
          },
        ],
      },
    },
  },
}
```

## لماذا تهم `requiresStringContent`

تقبل بعض مسارات Chat Completions في `inferrs` فقط
`messages[].content` النصية، وليس مصفوفات أجزاء المحتوى المنظمة.

إذا فشلت عمليات OpenClaw مع خطأ مثل:

```text
messages[1].content: invalid type: sequence, expected a string
```

فاضبط:

```json5
compat: {
  requiresStringContent: true
}
```

سيقوم OpenClaw بتسطيح أجزاء المحتوى النصية البحتة إلى سلاسل نصية عادية قبل إرسال
الطلب.

## ملاحظة Gemma ومخطط الأدوات

بعض التركيبات الحالية من `inferrs` + Gemma تقبل الطلبات المباشرة الصغيرة إلى
`/v1/chat/completions` لكنها لا تزال تفشل في أدوار وقت تشغيل وكيل OpenClaw
الكاملة.

إذا حدث ذلك، فجرّب هذا أولًا:

```json5
compat: {
  requiresStringContent: true,
  supportsTools: false
}
```

هذا يعطّل سطح مخطط الأدوات في OpenClaw لهذا النموذج ويمكن أن يقلل ضغط
الموجّه على الخلفيات المحلية الأكثر تشددًا.

إذا كانت الطلبات المباشرة الصغيرة لا تزال تعمل لكن أدوار وكيل OpenClaw العادية تستمر في
الانهيار داخل `inferrs`، فعادةً ما تكون المشكلة المتبقية سلوكًا صاعدًا في النموذج/الخادم
وليس في طبقة النقل الخاصة بـ OpenClaw.

## اختبار دخان يدوي

بعد الإعداد، اختبر الطبقتين كلتيهما:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'

openclaw infer model run \
  --model inferrs/google/gemma-4-E2B-it \
  --prompt "What is 2 + 2? Reply with one short sentence." \
  --json
```

إذا نجح الأمر الأول لكن الثاني فشل، فاستخدم ملاحظات استكشاف الأخطاء وإصلاحها
أدناه.

## استكشاف الأخطاء وإصلاحها

- فشل `curl /v1/models`: إما أن `inferrs` غير مشغّل، أو غير قابل للوصول، أو
  غير مربوط بالمضيف/المنفذ المتوقع.
- `messages[].content ... expected a string`: اضبط
  `compat.requiresStringContent: true`.
- تنجح الاستدعاءات المباشرة الصغيرة إلى `/v1/chat/completions`، لكن `openclaw infer model run`
  يفشل: جرّب `compat.supportsTools: false`.
- لم يعد OpenClaw يتلقى أخطاء مخطط، لكن `inferrs` لا يزال يتعطل في الأدوار الأكبر
  للوكلاء: تعامل مع ذلك على أنه قيد صاعد في `inferrs` أو النموذج وقلل
  ضغط الموجّه أو بدّل الخلفية/النموذج المحلي.

## سلوك نمط الوكيل

يُعامل `inferrs` على أنه خلفية `/v1` متوافقة مع OpenAI بنمط الوكيل، وليس
كنقطة نهاية OpenAI أصلية.

- لا ينطبق هنا تشكيل الطلبات الأصلي الخاص بـ OpenAI فقط
- لا `service_tier`، ولا `store` في Responses، ولا تلميحات لذاكرة الموجهات المؤقتة، ولا
  تشكيل لحمولات التوافق مع استدلال OpenAI
- لا يتم حقن رؤوس الإسناد المخفية الخاصة بـ OpenClaw (`originator` و`version` و`User-Agent`)
  على عناوين URL الأساسية المخصصة لـ `inferrs`

## راجع أيضًا

- [النماذج المحلية](/ar/gateway/local-models)
- [استكشاف أخطاء البوابة وإصلاحها](/ar/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)
- [موفرو النماذج](/ar/concepts/model-providers)
