---
read_when:
    - تريد توجيه OpenClaw عبر وكيل LiteLLM
    - تحتاج إلى تتبع التكاليف أو التسجيل أو توجيه النماذج عبر LiteLLM
summary: شغّل OpenClaw عبر LiteLLM Proxy للوصول الموحّد إلى النماذج وتتبع التكاليف
title: LiteLLM
x-i18n:
    generated_at: "2026-04-12T23:31:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 766692eb83a1be83811d8e09a970697530ffdd4f3392247cfb2927fd590364a0
    source_path: providers/litellm.md
    workflow: 15
---

# LiteLLM

‏[LiteLLM](https://litellm.ai) هو Gateway مفتوح المصدر لنماذج LLM يوفّر API موحّدًا لأكثر من 100 مزوّد نماذج. وجّه OpenClaw عبر LiteLLM للحصول على تتبّع مركزي للتكاليف، والتسجيل، ومرونة تبديل الواجهات الخلفية من دون تغيير إعداد OpenClaw الخاص بك.

<Tip>
**لماذا تستخدم LiteLLM مع OpenClaw؟**

- **تتبّع التكاليف** — اعرف بدقة ما ينفقه OpenClaw عبر جميع النماذج
- **توجيه النماذج** — بدّل بين Claude وGPT-4 وGemini وBedrock من دون تغييرات في الإعداد
- **المفاتيح الافتراضية** — أنشئ مفاتيح مع حدود إنفاق لـ OpenClaw
- **التسجيل** — سجلات كاملة للطلبات/الردود من أجل تصحيح الأخطاء
- **التحويل الاحتياطي** — تحويل تلقائي إذا كان المزوّد الأساسي متوقفًا
  </Tip>

## بدء سريع

<Tabs>
  <Tab title="الإعداد الأولي (موصى به)">
    **الأفضل لـ:** أسرع مسار إلى إعداد LiteLLM يعمل.

    <Steps>
      <Step title="شغّل الإعداد">
        ```bash
        openclaw onboard --auth-choice litellm-api-key
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="الإعداد اليدوي">
    **الأفضل لـ:** تحكم كامل في التثبيت والإعداد.

    <Steps>
      <Step title="شغّل LiteLLM Proxy">
        ```bash
        pip install 'litellm[proxy]'
        litellm --model claude-opus-4-6
        ```
      </Step>
      <Step title="وجّه OpenClaw إلى LiteLLM">
        ```bash
        export LITELLM_API_KEY="your-litellm-key"

        openclaw
        ```

        هذا كل شيء. يوجّه OpenClaw الآن عبر LiteLLM.
      </Step>
    </Steps>

  </Tab>
</Tabs>

## الإعداد

### متغيرات البيئة

```bash
export LITELLM_API_KEY="sk-litellm-key"
```

### ملف الإعداد

```json5
{
  models: {
    providers: {
      litellm: {
        baseUrl: "http://localhost:4000",
        apiKey: "${LITELLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "claude-opus-4-6",
            name: "Claude Opus 4.6",
            reasoning: true,
            input: ["text", "image"],
            contextWindow: 200000,
            maxTokens: 64000,
          },
          {
            id: "gpt-4o",
            name: "GPT-4o",
            reasoning: false,
            input: ["text", "image"],
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "litellm/claude-opus-4-6" },
    },
  },
}
```

## موضوعات متقدمة

<AccordionGroup>
  <Accordion title="المفاتيح الافتراضية">
    أنشئ مفتاحًا مخصصًا لـ OpenClaw مع حدود للإنفاق:

    ```bash
    curl -X POST "http://localhost:4000/key/generate" \
      -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "key_alias": "openclaw",
        "max_budget": 50.00,
        "budget_duration": "monthly"
      }'
    ```

    استخدم المفتاح المُنشأ كقيمة لـ `LITELLM_API_KEY`.

  </Accordion>

  <Accordion title="توجيه النماذج">
    يمكن لـ LiteLLM توجيه طلبات النماذج إلى واجهات خلفية مختلفة. اضبط ذلك في `config.yaml` الخاص بـ LiteLLM:

    ```yaml
    model_list:
      - model_name: claude-opus-4-6
        litellm_params:
          model: claude-opus-4-6
          api_key: os.environ/ANTHROPIC_API_KEY

      - model_name: gpt-4o
        litellm_params:
          model: gpt-4o
          api_key: os.environ/OPENAI_API_KEY
    ```

    يواصل OpenClaw طلب `claude-opus-4-6` — ويتولى LiteLLM التوجيه.

  </Accordion>

  <Accordion title="عرض الاستخدام">
    تحقّق من لوحة معلومات LiteLLM أو API الخاص به:

    ```bash
    # معلومات المفتاح
    curl "http://localhost:4000/key/info" \
      -H "Authorization: Bearer sk-litellm-key"

    # سجلات الإنفاق
    curl "http://localhost:4000/spend/logs" \
      -H "Authorization: Bearer $LITELLM_MASTER_KEY"
    ```

  </Accordion>

  <Accordion title="ملاحظات حول سلوك Proxy">
    - يعمل LiteLLM افتراضيًا على `http://localhost:4000`
    - يتصل OpenClaw عبر نقطة النهاية المتوافقة مع OpenAI ذات نمط Proxy الخاصة بـ LiteLLM عند `/v1`
    - لا ينطبق تشكيل الطلبات الأصلي الخاص بـ OpenAI فقط عبر LiteLLM:
      لا يوجد `service_tier`، ولا `store` الخاص بـ Responses، ولا تلميحات للتخزين المؤقت للموجّهات، ولا تشكيل حمولة متوافق مع الاستدلال في OpenAI
    - لا يتم حقن ترويسات الإسناد المخفية الخاصة بـ OpenClaw (`originator` و`version` و`User-Agent`) على عناوين LiteLLM الأساسية المخصصة
  </Accordion>
</AccordionGroup>

<Note>
لإعداد المزوّد العام وسلوك التبديل الاحتياطي، راجع [Model Providers](/ar/concepts/model-providers).
</Note>

## ذو صلة

<CardGroup cols={2}>
  <Card title="مستندات LiteLLM" href="https://docs.litellm.ai" icon="book">
    وثائق LiteLLM الرسمية ومرجع API.
  </Card>
  <Card title="مزوّدو النماذج" href="/ar/concepts/model-providers" icon="layers">
    نظرة عامة على جميع المزوّدين ومراجع النماذج وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="الإعداد" href="/ar/gateway/configuration" icon="gear">
    مرجع الإعداد الكامل.
  </Card>
  <Card title="اختيار النموذج" href="/ar/concepts/models" icon="brain">
    كيفية اختيار النماذج وضبطها.
  </Card>
</CardGroup>
