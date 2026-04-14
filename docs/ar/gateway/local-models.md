---
read_when:
    - تريد تقديم النماذج من جهاز GPU الخاص بك
    - أنت تُعدّ LM Studio أو وكيلاً متوافقًا مع OpenAI
    - تحتاج إلى أكثر إرشادات النماذج المحلية أمانًا
summary: شغّل OpenClaw على نماذج اللغة الكبيرة المحلية (LM Studio وvLLM وLiteLLM ونقاط نهاية OpenAI المخصّصة)
title: النماذج المحلية
x-i18n:
    generated_at: "2026-04-14T07:17:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1544c522357ba4b18dfa6d05ea8d60c7c6262281b53863d9aee7002464703ca7
    source_path: gateway/local-models.md
    workflow: 15
---

# النماذج المحلية

التشغيل المحلي ممكن، لكن OpenClaw يتوقع سياقًا كبيرًا + دفاعات قوية ضد حقن التلقين. البطاقات الصغيرة تقتطع السياق وتُضعف الأمان. استهدف مستوى عالٍ: **استوديوهَا Mac Studio مضبوطتان للحد الأقصى على الأقل أو منصة GPU مكافئة (~أكثر من 30 ألف دولار)**. تعمل وحدة GPU واحدة بسعة **24 GB** فقط مع التلقينات الأخف وبزمن استجابة أعلى. استخدم **أكبر / البديل الكامل الحجم من النموذج الذي يمكنك تشغيله**؛ إذ إن نقاط التحقق المضغوطة بقوة أو “الصغيرة” ترفع مخاطر حقن التلقين (راجع [الأمان](/ar/gateway/security)).

إذا كنت تريد إعدادًا محليًا بأقل قدر من التعقيد، فابدأ بـ [LM Studio](/ar/providers/lmstudio) أو [Ollama](/ar/providers/ollama) و`openclaw onboard`. هذه الصفحة هي الدليل العملي الموجَّه للحِزم المحلية الأعلى مستوى وخوادم OpenAI-compatible المحلية المخصّصة.

## الموصى به: LM Studio + نموذج محلي كبير (Responses API)

أفضل حزمة محلية حاليًا. حمّل نموذجًا كبيرًا في LM Studio (على سبيل المثال، إصدارًا كامل الحجم من Qwen أو DeepSeek أو Llama)، ثم فعّل الخادم المحلي (الافتراضي `http://127.0.0.1:1234`) واستخدم Responses API لإبقاء الاستدلال منفصلًا عن النص النهائي.

```json5
{
  agents: {
    defaults: {
      model: { primary: “lmstudio/my-local-model” },
      models: {
        “anthropic/claude-opus-4-6”: { alias: “Opus” },
        “lmstudio/my-local-model”: { alias: “Local” },
      },
    },
  },
  models: {
    mode: “merge”,
    providers: {
      lmstudio: {
        baseUrl: “http://127.0.0.1:1234/v1”,
        apiKey: “lmstudio”,
        api: “openai-responses”,
        models: [
          {
            id: “my-local-model”,
            name: “Local Model”,
            reasoning: false,
            input: [“text”],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**قائمة الإعداد**

- ثبّت LM Studio: [https://lmstudio.ai](https://lmstudio.ai)
- في LM Studio، نزّل **أكبر إصدار نموذج متاح** (تجنّب البدائل “الصغيرة” أو المضغوطة بشدة)، وابدأ الخادم، وتأكد من أن `http://127.0.0.1:1234/v1/models` يعرضه.
- استبدل `my-local-model` بمعرّف النموذج الفعلي الظاهر في LM Studio.
- أبقِ النموذج محمّلًا؛ فالتحميل البارد يضيف زمن بدء تشغيل.
- اضبط `contextWindow`/`maxTokens` إذا كان إصدار LM Studio لديك مختلفًا.
- بالنسبة إلى WhatsApp، التزم بـ Responses API حتى لا يُرسل إلا النص النهائي.

أبقِ النماذج المستضافة مُعدّة حتى عند التشغيل المحلي؛ استخدم `models.mode: "merge"` حتى تظل خيارات الرجوع الاحتياطي متاحة.

### إعداد هجين: نموذج مستضاف أساسي، ونموذج محلي احتياطي

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["lmstudio/my-local-model", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "lmstudio/my-local-model": { alias: "Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### محلي أولًا مع شبكة أمان مستضافة

بدّل ترتيب الأساسي والاحتياطي؛ وأبقِ كتلة المزوّدين نفسها و`models.mode: "merge"` حتى تتمكن من الرجوع إلى Sonnet أو Opus عندما يتعطل الجهاز المحلي.

### الاستضافة الإقليمية / توجيه البيانات

- تتوفر أيضًا بدائل MiniMax/Kimi/GLM المستضافة على OpenRouter مع نقاط نهاية مثبّتة حسب المنطقة (مثلًا، مستضافة في الولايات المتحدة). اختر البديل الإقليمي هناك للإبقاء على حركة البيانات داخل النطاق القضائي الذي تختاره مع الاستمرار في استخدام `models.mode: "merge"` كخيارات احتياطية لـ Anthropic/OpenAI.
- يظل التشغيل المحلي فقط هو أقوى مسار للخصوصية؛ أما التوجيه الإقليمي المستضاف فهو الحل الوسط عندما تحتاج إلى مزايا المزوّد لكنك تريد التحكم في تدفق البيانات.

## وكلاء محليون آخرون متوافقون مع OpenAI

يعمل vLLM وLiteLLM وOAI-proxy أو البوابات المخصّصة إذا كانت توفّر نقطة نهاية `/v1` بأسلوب OpenAI. استبدل كتلة المزوّد أعلاه بنقطة النهاية ومعرّف النموذج لديك:

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

أبقِ `models.mode: "merge"` حتى تظل النماذج المستضافة متاحة كخيارات احتياطية.

ملاحظة سلوكية لخلفيات `/v1` المحلية/الوسيطة:

- يتعامل OpenClaw مع هذه المسارات على أنها مسارات وسيطة متوافقة مع OpenAI، وليست
  نقاط نهاية OpenAI أصلية
- لا ينطبق هنا تشكيل الطلبات الخاص بـ OpenAI الأصلية فقط: لا
  `service_tier`، ولا `store` في Responses، ولا تشكيل حمولة التوافق مع استدلال OpenAI،
  ولا تلميحات ذاكرة التخزين المؤقت للتلقين
- لا تُحقن ترويسات الإسناد المخفية الخاصة بـ OpenClaw (`originator` و`version` و`User-Agent`)
  في عناوين URL المخصّصة لهذه الوكلاء

ملاحظات التوافق للخلفيات الأكثر تشددًا والمتوافقة مع OpenAI:

- بعض الخوادم تقبل فقط `messages[].content` كسلسلة نصية في Chat Completions، وليس
  مصفوفات أجزاء المحتوى المهيكلة. اضبط
  `models.providers.<provider>.models[].compat.requiresStringContent: true` لنقاط
  النهاية تلك.
- بعض الخلفيات المحلية الأصغر أو الأكثر تشددًا تكون غير مستقرة مع شكل التلقين الكامل
  لبيئة تشغيل الوكلاء في OpenClaw، خاصةً عند تضمين مخططات الأدوات. إذا كانت
  الخلفية تعمل مع استدعاءات `/v1/chat/completions` المباشرة الصغيرة لكنها تفشل في
  أدوار الوكيل العادية في OpenClaw، فجرّب أولًا
  `models.providers.<provider>.models[].compat.supportsTools: false`.
- إذا استمرت الخلفية في الفشل فقط مع تشغيلات OpenClaw الأكبر، فعادةً ما تكون المشكلة
  في سعة النموذج/الخادم المصدر أو في خطأ في الخلفية، وليس في طبقة النقل الخاصة بـ OpenClaw.

## استكشاف الأخطاء وإصلاحها

- هل يستطيع Gateway الوصول إلى الوكيل؟ `curl http://127.0.0.1:1234/v1/models`.
- هل تم إلغاء تحميل نموذج LM Studio؟ أعد تحميله؛ فالبدء البارد سبب شائع لـ “التعليق”.
- يحذّر OpenClaw عندما تكون نافذة السياق المكتشفة أقل من **32k** ويمنع التشغيل عندما تكون أقل من **16k**. إذا واجهت هذا الفحص المسبق، فارفع حد السياق في الخادم/النموذج أو اختر نموذجًا أكبر.
- أخطاء في السياق؟ خفّض `contextWindow` أو ارفع حد الخادم لديك.
- هل يعيد الخادم المتوافق مع OpenAI الخطأ `messages[].content ... expected a string`؟
  أضف `compat.requiresStringContent: true` إلى إدخال ذلك النموذج.
- هل تعمل استدعاءات `/v1/chat/completions` الصغيرة المباشرة، لكن `openclaw infer model run`
  يفشل مع Gemma أو نموذج محلي آخر؟ عطّل مخططات الأدوات أولًا باستخدام
  `compat.supportsTools: false`، ثم اختبر مجددًا. إذا استمر الخادم في التعطل فقط
  مع تلقينات OpenClaw الأكبر، فاعتبر ذلك قيدًا في الخادم/النموذج المصدر.
- الأمان: تتجاوز النماذج المحلية عوامل التصفية الموجودة لدى المزوّد؛ لذا اجعل الوكلاء محدودي النطاق وأبقِ Compaction مفعّلًا لتقليل نطاق تأثير حقن التلقين.
