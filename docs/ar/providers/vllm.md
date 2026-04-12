---
read_when:
    - تريد تشغيل OpenClaw مقابل خادم vLLM محلي
    - تريد استخدام نقاط النهاية المتوافقة مع OpenAI ‏`/v1` مع نماذجك الخاصة
summary: شغّل OpenClaw مع vLLM ‏(خادم محلي متوافق مع OpenAI)
title: vLLM
x-i18n:
    generated_at: "2026-04-12T23:33:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: a43be9ae879158fcd69d50fb3a47616fd560e3c6fe4ecb3a109bdda6a63a6a80
    source_path: providers/vllm.md
    workflow: 15
---

# vLLM

يمكن لـ vLLM تقديم نماذج مفتوحة المصدر (وبعض النماذج المخصصة) عبر HTTP API **متوافق مع OpenAI**. يتصل OpenClaw بـ vLLM باستخدام API ‏`openai-completions`.

يمكن لـ OpenClaw أيضًا **اكتشاف النماذج المتاحة تلقائيًا** من vLLM عندما تشترك صراحةً باستخدام `VLLM_API_KEY` (أي قيمة تعمل إذا كان خادمك لا يفرض المصادقة) ولا تعرّف إدخال `models.providers.vllm` صريحًا.

| الخاصية         | القيمة                                   |
| ---------------- | ---------------------------------------- |
| معرّف المزود     | `vllm`                                   |
| API              | `openai-completions` (متوافق مع OpenAI) |
| المصادقة         | متغير البيئة `VLLM_API_KEY`              |
| عنوان URL الأساسي الافتراضي | `http://127.0.0.1:8000/v1`      |

## البدء

<Steps>
  <Step title="شغّل vLLM مع خادم متوافق مع OpenAI">
    يجب أن يكشف عنوان URL الأساسي لديك عن نقاط نهاية `/v1` (مثل `/v1/models` و`/v1/chat/completions`). يعمل vLLM عادة على:

    ```
    http://127.0.0.1:8000/v1
    ```

  </Step>
  <Step title="عيّن متغير البيئة لمفتاح API">
    تعمل أي قيمة إذا كان خادمك لا يفرض المصادقة:

    ```bash
    export VLLM_API_KEY="vllm-local"
    ```

  </Step>
  <Step title="اختر نموذجًا">
    استبدل ذلك بأحد معرّفات نماذج vLLM لديك:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "vllm/your-model-id" },
        },
      },
    }
    ```

  </Step>
  <Step title="تحقق من توفر النموذج">
    ```bash
    openclaw models list --provider vllm
    ```
  </Step>
</Steps>

## اكتشاف النماذج (المزود الضمني)

عند تعيين `VLLM_API_KEY` (أو وجود ملف تعريف مصادقة) و**عدم** تعريف `models.providers.vllm`، يستعلم OpenClaw عن:

```
GET http://127.0.0.1:8000/v1/models
```

ويحوّل المعرّفات المُعادة إلى إدخالات نماذج.

<Note>
إذا عيّنت `models.providers.vllm` صراحةً، فسيتم تخطي الاكتشاف التلقائي ويجب عليك تعريف النماذج يدويًا.
</Note>

## الإعداد الصريح (نماذج يدوية)

استخدم الإعداد الصريح عندما:

- يعمل vLLM على مضيف أو منفذ مختلف
- تريد تثبيت قيم `contextWindow` أو `maxTokens`
- يتطلب خادمك مفتاح API حقيقيًا (أو تريد التحكم في الرؤوس)

```json5
{
  models: {
    providers: {
      vllm: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "${VLLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "Local vLLM Model",
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

## ملاحظات متقدمة

<AccordionGroup>
  <Accordion title="سلوك بنمط proxy">
    يُعامَل vLLM كواجهة خلفية متوافقة مع OpenAI `/v1` بنمط proxy، وليس
    كنقطة نهاية OpenAI أصلية. وهذا يعني:

    | السلوك | هل يُطبَّق؟ |
    |--------|-------------|
    | تشكيل طلب OpenAI الأصلي | لا |
    | `service_tier` | لا يتم إرساله |
    | `store` في الاستجابات | لا يتم إرساله |
    | تلميحات Prompt-cache | لا يتم إرسالها |
    | تشكيل حمولة التوافق مع التفكير في OpenAI | لا يُطبَّق |
    | رؤوس الإسناد المخفية الخاصة بـ OpenClaw | لا يتم حقنها على عناوين URL الأساسية المخصصة |

  </Accordion>

  <Accordion title="عنوان URL أساسي مخصص">
    إذا كان خادم vLLM لديك يعمل على مضيف أو منفذ غير افتراضي، فعيّن `baseUrl` في إعدادات المزود الصريحة:

    ```json5
    {
      models: {
        providers: {
          vllm: {
            baseUrl: "http://192.168.1.50:9000/v1",
            apiKey: "${VLLM_API_KEY}",
            api: "openai-completions",
            models: [
              {
                id: "my-custom-model",
                name: "Remote vLLM Model",
                reasoning: false,
                input: ["text"],
                contextWindow: 64000,
                maxTokens: 4096,
              },
            ],
          },
        },
      },
    }
    ```

  </Accordion>
</AccordionGroup>

## استكشاف الأخطاء وإصلاحها

<AccordionGroup>
  <Accordion title="الخادم غير قابل للوصول">
    تحقق من أن خادم vLLM يعمل ويمكن الوصول إليه:

    ```bash
    curl http://127.0.0.1:8000/v1/models
    ```

    إذا ظهرت لك رسالة خطأ في الاتصال، فتحقق من المضيف، والمنفذ، ومن أن vLLM بدأ في وضع الخادم المتوافق مع OpenAI.

  </Accordion>

  <Accordion title="أخطاء المصادقة في الطلبات">
    إذا فشلت الطلبات بأخطاء مصادقة، فعيّن `VLLM_API_KEY` حقيقيًا يطابق إعدادات خادمك، أو قم بإعداد المزود صراحةً ضمن `models.providers.vllm`.

    <Tip>
    إذا كان خادم vLLM لديك لا يفرض المصادقة، فإن أي قيمة غير فارغة لـ `VLLM_API_KEY` تعمل كإشارة اشتراك صريحة لـ OpenClaw.
    </Tip>

  </Accordion>

  <Accordion title="لم يتم اكتشاف أي نماذج">
    يتطلب الاكتشاف التلقائي تعيين `VLLM_API_KEY` **وألا** يوجد إدخال إعدادات صريح لـ `models.providers.vllm`. إذا كنت قد عرّفت المزود يدويًا، فسيتخطى OpenClaw الاكتشاف ويستخدم النماذج التي أعلنت عنها فقط.
  </Accordion>
</AccordionGroup>

<Warning>
للمزيد من المساعدة: [استكشاف الأخطاء وإصلاحها](/ar/help/troubleshooting) و[الأسئلة الشائعة](/ar/help/faq).
</Warning>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزودات، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="OpenAI" href="/ar/providers/openai" icon="bolt">
    مزود OpenAI الأصلي وسلوك المسار المتوافق مع OpenAI.
  </Card>
  <Card title="OAuth والمصادقة" href="/ar/gateway/authentication" icon="key">
    تفاصيل المصادقة وقواعد إعادة استخدام بيانات الاعتماد.
  </Card>
  <Card title="استكشاف الأخطاء وإصلاحها" href="/ar/help/troubleshooting" icon="wrench">
    المشكلات الشائعة وكيفية حلها.
  </Card>
</CardGroup>
