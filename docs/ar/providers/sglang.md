---
read_when:
    - تريد تشغيل OpenClaw على خادم SGLang محلي
    - تريد نقاط نهاية `/v1` متوافقة مع OpenAI مع نماذجك الخاصة
summary: شغّل OpenClaw مع SGLang (خادم مستضاف ذاتيًا ومتوافق مع OpenAI)
title: SGLang
x-i18n:
    generated_at: "2026-04-12T23:32:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0a2e50a499c3d25dcdc3af425fb023c6e3f19ed88f533ecf0eb8a2cb7ec8b0d
    source_path: providers/sglang.md
    workflow: 15
---

# SGLang

يمكن لـ SGLang تقديم نماذج مفتوحة المصدر عبر HTTP API **متوافق مع OpenAI**.
ويمكن لـ OpenClaw الاتصال بـ SGLang باستخدام API ‏`openai-completions`.

كما يمكن لـ OpenClaw أيضًا **اكتشاف** النماذج المتاحة تلقائيًا من SGLang عندما
تفعّل ذلك عبر `SGLANG_API_KEY` (أي قيمة تعمل إذا كان خادمك لا يفرض المصادقة)
ولا تعرّف إدخالًا صريحًا `models.providers.sglang`.

## البدء

<Steps>
  <Step title="Start SGLang">
    شغّل SGLang بخادم متوافق مع OpenAI. يجب أن يعرّض Base URL لديك نقاط نهاية
    `/v1` (مثل `/v1/models` و`/v1/chat/completions`). يعمل SGLang غالبًا على:

    - `http://127.0.0.1:30000/v1`

  </Step>
  <Step title="Set an API key">
    تعمل أي قيمة إذا لم تُضبط مصادقة على خادمك:

    ```bash
    export SGLANG_API_KEY="sglang-local"
    ```

  </Step>
  <Step title="Run onboarding or set a model directly">
    ```bash
    openclaw onboard
    ```

    أو اضبط النموذج يدويًا:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "sglang/your-model-id" },
        },
      },
    }
    ```

  </Step>
</Steps>

## اكتشاف النموذج (الموفّر الضمني)

عند تعيين `SGLANG_API_KEY` (أو وجود ملف مصادقة) و**عدم** تعريف
`models.providers.sglang`، سيستعلم OpenClaw عن:

- `GET http://127.0.0.1:30000/v1/models`

ثم يحوّل المعرّفات المُعادة إلى إدخالات نماذج.

<Note>
إذا عيّنت `models.providers.sglang` بشكل صريح، فسيتم تخطي الاكتشاف التلقائي
ويجب عليك تعريف النماذج يدويًا.
</Note>

## الإعداد الصريح (النماذج اليدوية)

استخدم الإعداد الصريح عندما:

- يعمل SGLang على مضيف/منفذ مختلف.
- تريد تثبيت قيم `contextWindow`/`maxTokens`.
- يتطلب خادمك مفتاح API حقيقيًا (أو تريد التحكم في الترويسات).

```json5
{
  models: {
    providers: {
      sglang: {
        baseUrl: "http://127.0.0.1:30000/v1",
        apiKey: "${SGLANG_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "نموذج SGLang محلي",
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

## إعداد متقدم

<AccordionGroup>
  <Accordion title="Proxy-style behavior">
    يُعامل SGLang على أنه واجهة خلفية `/v1` متوافقة مع OpenAI بأسلوب الوكيل،
    وليس نقطة نهاية OpenAI أصلية.

    | السلوك | SGLang |
    |--------|--------|
    | تشكيل الطلبات الخاص بـ OpenAI فقط | لا يُطبّق |
    | `service_tier` و`store` الخاص بـ Responses وتلميحات ذاكرة التخزين المؤقت للمطالبات | لا تُرسل |
    | تشكيل الحمولة المتوافق مع الاستدلال | لا يُطبّق |
    | ترويسات الإسناد المخفية (`originator` و`version` و`User-Agent`) | لا تُحقن على عناوين Base URL المخصصة لـ SGLang |

  </Accordion>

  <Accordion title="Troubleshooting">
    **الخادم غير قابل للوصول**

    تحقّق من أن الخادم قيد التشغيل ويستجيب:

    ```bash
    curl http://127.0.0.1:30000/v1/models
    ```

    **أخطاء المصادقة**

    إذا فشلت الطلبات بسبب أخطاء مصادقة، فعيّن `SGLANG_API_KEY` حقيقيًا يطابق
    إعداد خادمك، أو اضبط الموفّر صراحةً تحت `models.providers.sglang`.

    <Tip>
    إذا كنت تشغّل SGLang من دون مصادقة، فتكفي أي قيمة غير فارغة لـ
    `SGLANG_API_KEY` لتفعيل اكتشاف النماذج.
    </Tip>

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="Model selection" href="/ar/concepts/model-providers" icon="layers">
    اختيار الموفّرات، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="Configuration reference" href="/ar/gateway/configuration-reference" icon="gear">
    مخطط الإعداد الكامل، بما في ذلك إدخالات الموفّرين.
  </Card>
</CardGroup>
