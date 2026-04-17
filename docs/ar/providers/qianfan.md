---
read_when:
    - تريد مفتاح API واحدًا للعديد من نماذج LLM
    - تحتاج إلى إرشادات إعداد Baidu Qianfan
summary: استخدم API الموحّد من Qianfan للوصول إلى العديد من النماذج في OpenClaw
title: Qianfan
x-i18n:
    generated_at: "2026-04-12T23:32:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1d0eeee9ec24b335c2fb8ac5e985a9edc35cfc5b2641c545cb295dd2de619f50
    source_path: providers/qianfan.md
    workflow: 15
---

# Qianfan

Qianfan هي منصة MaaS من Baidu، وتوفّر **API موحّدًا** يوجّه الطلبات إلى العديد من النماذج خلف
نقطة نهاية واحدة ومفتاح API واحد. وهي متوافقة مع OpenAI، لذا تعمل معظم حِزم OpenAI SDK بمجرد تغيير عنوان URL الأساسي.

| الخاصية | القيمة                            |
| -------- | -------------------------------- |
| المزود | `qianfan`                        |
| المصادقة | `QIANFAN_API_KEY`                |
| API      | متوافق مع OpenAI                |
| عنوان URL الأساسي | `https://qianfan.baidubce.com/v2` |

## البدء

<Steps>
  <Step title="أنشئ حساب Baidu Cloud">
    سجّل أو سجّل الدخول في [Qianfan Console](https://console.bce.baidu.com/qianfan/ais/console/apiKey) وتأكد من تمكين وصول API الخاص بـ Qianfan.
  </Step>
  <Step title="أنشئ مفتاح API">
    أنشئ تطبيقًا جديدًا أو اختر تطبيقًا موجودًا، ثم أنشئ مفتاح API. يكون تنسيق المفتاح `bce-v3/ALTAK-...`.
  </Step>
  <Step title="شغّل الإعداد الأولي">
    ```bash
    openclaw onboard --auth-choice qianfan-api-key
    ```
  </Step>
  <Step title="تحقق من توفر النموذج">
    ```bash
    openclaw models list --provider qianfan
    ```
  </Step>
</Steps>

## النماذج المتاحة

| مرجع النموذج                       | الإدخال      | السياق | الحد الأقصى للإخراج | التفكير | ملاحظات           |
| --------------------------------- | ------------ | ------ | ------------------- | ------- | ----------------- |
| `qianfan/deepseek-v3.2`           | text         | 98,304 | 32,768              | نعم     | النموذج الافتراضي |
| `qianfan/ernie-5.0-thinking-preview` | text, image | 119,000 | 64,000            | نعم     | متعدد الوسائط     |

<Tip>
مرجع النموذج المدمج الافتراضي هو `qianfan/deepseek-v3.2`. لا تحتاج إلى تجاوز `models.providers.qianfan` إلا عندما تحتاج إلى عنوان URL أساسي مخصص أو بيانات وصفية مخصصة للنموذج.
</Tip>

## مثال على الإعداد

```json5
{
  env: { QIANFAN_API_KEY: "bce-v3/ALTAK-..." },
  agents: {
    defaults: {
      model: { primary: "qianfan/deepseek-v3.2" },
      models: {
        "qianfan/deepseek-v3.2": { alias: "QIANFAN" },
      },
    },
  },
  models: {
    providers: {
      qianfan: {
        baseUrl: "https://qianfan.baidubce.com/v2",
        api: "openai-completions",
        models: [
          {
            id: "deepseek-v3.2",
            name: "DEEPSEEK V3.2",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 98304,
            maxTokens: 32768,
          },
          {
            id: "ernie-5.0-thinking-preview",
            name: "ERNIE-5.0-Thinking-Preview",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 119000,
            maxTokens: 64000,
          },
        ],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="النقل والتوافق">
    يعمل Qianfan عبر مسار النقل المتوافق مع OpenAI، وليس عبر تشكيل الطلبات الأصلي الخاص بـ OpenAI. وهذا يعني أن ميزات OpenAI SDK القياسية تعمل، لكن المعلمات الخاصة بالمزود قد لا يتم تمريرها.
  </Accordion>

  <Accordion title="الفهرس والتجاوزات">
    يتضمن الفهرس المدمج حاليًا `deepseek-v3.2` و`ernie-5.0-thinking-preview`. أضف أو تجاوز `models.providers.qianfan` فقط عندما تحتاج إلى عنوان URL أساسي مخصص أو بيانات وصفية للنموذج.

    <Note>
    تستخدم مراجع النماذج البادئة `qianfan/` (على سبيل المثال `qianfan/deepseek-v3.2`).
    </Note>

  </Accordion>

  <Accordion title="استكشاف الأخطاء وإصلاحها">
    - تأكد من أن مفتاح API الخاص بك يبدأ بـ `bce-v3/ALTAK-` وأن وصول API الخاص بـ Qianfan مفعّل في وحدة تحكم Baidu Cloud.
    - إذا لم تكن النماذج مدرجة، فتأكد من أن خدمة Qianfan مفعّلة في حسابك.
    - عنوان URL الأساسي الافتراضي هو `https://qianfan.baidubce.com/v2`. لا تغيّره إلا إذا كنت تستخدم نقطة نهاية أو proxy مخصصًا.
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزودات، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration" icon="gear">
    المرجع الكامل لإعدادات OpenClaw.
  </Card>
  <Card title="إعداد الوكيل" href="/ar/concepts/agent" icon="robot">
    إعداد الإعدادات الافتراضية للوكيل وتعيينات النماذج.
  </Card>
  <Card title="مستندات Qianfan API" href="https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb" icon="arrow-up-right-from-square">
    الوثائق الرسمية لـ Qianfan API.
  </Card>
</CardGroup>
