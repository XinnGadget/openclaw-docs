---
read_when:
    - تريد تشغيل OpenClaw مقابل خادم inferrs محلي
    - أنت تقدّم Gemma أو نموذجًا آخر عبر inferrs
    - تحتاج إلى أعلام التوافق الدقيقة في OpenClaw لـ inferrs
summary: شغّل OpenClaw عبر inferrs ‏(خادم محلي متوافق مع OpenAI)
title: inferrs
x-i18n:
    generated_at: "2026-04-12T23:30:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 847dcc131fe51dfe163dcd60075dbfaa664662ea2a5c3986ccb08ddd37e8c31f
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

يمكن لـ [inferrs](https://github.com/ericcurtin/inferrs) تقديم النماذج المحلية عبر
واجهة `/v1` متوافقة مع OpenAI. يعمل OpenClaw مع `inferrs` من خلال المسار العام
`openai-completions`.

من الأفضل حاليًا التعامل مع `inferrs` كواجهة خلفية OpenAI-compatible ذاتية الاستضافة
مخصصة، وليس كـ Plugin مزوّد مخصص في OpenClaw.

## البدء

<Steps>
  <Step title="بدء inferrs مع نموذج">
    ```bash
    inferrs serve google/gemma-4-E2B-it \
      --host 127.0.0.1 \
      --port 8080 \
      --device metal
    ```
  </Step>
  <Step title="التحقق من إمكانية الوصول إلى الخادم">
    ```bash
    curl http://127.0.0.1:8080/health
    curl http://127.0.0.1:8080/v1/models
    ```
  </Step>
  <Step title="إضافة إدخال مزوّد في OpenClaw">
    أضف إدخال مزوّد صريحًا ووجّه إليه نموذجك الافتراضي. راجع مثال الإعداد الكامل أدناه.
  </Step>
</Steps>

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

## متقدم

<AccordionGroup>
  <Accordion title="سبب أهمية requiresStringContent">
    تقبل بعض مسارات Chat Completions في `inferrs` فقط
    السلاسل النصية في `messages[].content`، وليس مصفوفات أجزاء المحتوى المنظمة.

    <Warning>
    إذا فشلت عمليات OpenClaw برسالة خطأ مثل:

    ```text
    messages[1].content: invalid type: sequence, expected a string
    ```

    فاضبط `compat.requiresStringContent: true` في إدخال النموذج.
    </Warning>

    ```json5
    compat: {
      requiresStringContent: true
    }
    ```

    سيقوم OpenClaw بتسطيح أجزاء المحتوى النصية الخالصة إلى سلاسل نصية عادية قبل إرسال
    الطلب.

  </Accordion>

  <Accordion title="ملاحظة حول Gemma ومخطط الأدوات">
    بعض التركيبات الحالية من `inferrs` + Gemma تقبل الطلبات الصغيرة المباشرة
    إلى `/v1/chat/completions` ولكنها ما تزال تفشل في أدوار وقت تشغيل وكيل OpenClaw
    الكاملة.

    إذا حدث ذلك، فجرّب هذا أولًا:

    ```json5
    compat: {
      requiresStringContent: true,
      supportsTools: false
    }
    ```

    يؤدي ذلك إلى تعطيل سطح مخطط أدوات OpenClaw لهذا النموذج، ويمكن أن يقلل ضغط الموجّه
    على الواجهات الخلفية المحلية الأكثر تشددًا.

    إذا استمرت الطلبات المباشرة الصغيرة في العمل ولكن أدوار وكيل OpenClaw العادية واصلت
    التعطل داخل `inferrs`، فعادةً ما تكون المشكلة المتبقية ناتجة عن سلوك النموذج/الخادم
    في المنبع وليس عن طبقة النقل في OpenClaw.

  </Accordion>

  <Accordion title="اختبار Smoke يدوي">
    بعد الإعداد، اختبر الطبقتين كلتيهما:

    ```bash
    curl http://127.0.0.1:8080/v1/chat/completions \
      -H 'content-type: application/json' \
      -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'
    ```

    ```bash
    openclaw infer model run \
      --model inferrs/google/gemma-4-E2B-it \
      --prompt "What is 2 + 2? Reply with one short sentence." \
      --json
    ```

    إذا نجح الأمر الأول لكن الثاني فشل، فراجع قسم استكشاف الأخطاء وإصلاحها أدناه.

  </Accordion>

  <Accordion title="سلوك نمط الوكيل">
    يتم التعامل مع `inferrs` كواجهة خلفية `/v1` متوافقة مع OpenAI بنمط الوكيل، وليس
    كنقطة نهاية OpenAI أصلية.

    - لا ينطبق هنا تشكيل الطلبات الخاص بـ OpenAI الأصلي فقط
    - لا يوجد `service_tier`، ولا `store` الخاص بـ Responses، ولا تلميحات cache للموجّه، ولا
      تشكيل حمولة reasoning-compat الخاص بـ OpenAI
    - لا يتم حقن ترويسات الإسناد المخفية في OpenClaw (`originator` و`version` و`User-Agent`)
      على عناوين `inferrs` الأساسية المخصصة

  </Accordion>
</AccordionGroup>

## استكشاف الأخطاء وإصلاحها

<AccordionGroup>
  <Accordion title="فشل curl /v1/models">
    `inferrs` غير مشغّل، أو لا يمكن الوصول إليه، أو غير مرتبط
    بالمضيف/المنفذ المتوقعين. تأكد من بدء تشغيل الخادم واستماعه على العنوان الذي
    ضبطته.
  </Accordion>

  <Accordion title="messages[].content كان متوقعًا أن تكون سلسلة نصية">
    اضبط `compat.requiresStringContent: true` في إدخال النموذج. راجع
    قسم `requiresStringContent` أعلاه لمزيد من التفاصيل.
  </Accordion>

  <Accordion title="نجحت استدعاءات /v1/chat/completions المباشرة لكن openclaw infer model run فشل">
    جرّب ضبط `compat.supportsTools: false` لتعطيل سطح مخطط الأدوات.
    راجع الملاحظة أعلاه حول مخطط أدوات Gemma.
  </Accordion>

  <Accordion title="ما يزال inferrs يتعطل في أدوار الوكيل الأكبر">
    إذا لم يعد OpenClaw يتلقى أخطاء schema لكن `inferrs` ما يزال يتعطل في أدوار
    الوكيل الأكبر، فتعامل مع ذلك باعتباره قيدًا في `inferrs` أو النموذج في المنبع. قلّل
    ضغط الموجّه أو انتقل إلى واجهة خلفية أو نموذج محلي مختلف.
  </Accordion>
</AccordionGroup>

<Tip>
للمساعدة العامة، راجع [استكشاف الأخطاء وإصلاحها](/ar/help/troubleshooting) و[الأسئلة الشائعة](/ar/help/faq).
</Tip>

## راجع أيضًا

<CardGroup cols={2}>
  <Card title="النماذج المحلية" href="/ar/gateway/local-models" icon="server">
    تشغيل OpenClaw مع خوادم النماذج المحلية.
  </Card>
  <Card title="استكشاف أخطاء Gateway وإصلاحها" href="/ar/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail" icon="wrench">
    تصحيح أخطاء الواجهات الخلفية المحلية المتوافقة مع OpenAI التي تنجح في probes المباشرة لكنها تفشل في تشغيلات الوكيل.
  </Card>
  <Card title="مزوّدو النماذج" href="/ar/concepts/model-providers" icon="layers">
    نظرة عامة على جميع المزوّدين، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
</CardGroup>
