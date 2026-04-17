---
read_when:
    - تريد استخدام نماذج Mistral في OpenClaw
    - تحتاج إلى إعداد مفتاح API لـ Mistral عبر onboarding ومراجع النماذج
summary: استخدم نماذج Mistral ونسخ Voxtral مع OpenClaw
title: Mistral
x-i18n:
    generated_at: "2026-04-12T23:31:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0474f55587909ce9bbdd47b881262edbeb1b07eb3ed52de1090a8ec4d260c97b
    source_path: providers/mistral.md
    workflow: 15
---

# Mistral

يدعم OpenClaw Mistral لكلٍّ من توجيه نماذج النص/الصور (`mistral/...`) ونسخ
الصوت عبر Voxtral ضمن media understanding.
كما يمكن استخدام Mistral لتضمينات الذاكرة (`memorySearch.provider = "mistral"`).

- الموفّر: `mistral`
- المصادقة: `MISTRAL_API_KEY`
- API: ‏Mistral Chat Completions (`https://api.mistral.ai/v1`)

## البدء

<Steps>
  <Step title="Get your API key">
    أنشئ مفتاح API في [Mistral Console](https://console.mistral.ai/).
  </Step>
  <Step title="Run onboarding">
    ```bash
    openclaw onboard --auth-choice mistral-api-key
    ```

    أو مرّر المفتاح مباشرةً:

    ```bash
    openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
    ```

  </Step>
  <Step title="Set a default model">
    ```json5
    {
      env: { MISTRAL_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
    }
    ```
  </Step>
  <Step title="Verify the model is available">
    ```bash
    openclaw models list --provider mistral
    ```
  </Step>
</Steps>

## فهرس LLM المضمّن

يشحن OpenClaw حاليًا فهرس Mistral المضمّن التالي:

| مرجع النموذج                     | الإدخال     | السياق   | الحد الأقصى للإخراج | ملاحظات                                                            |
| -------------------------------- | ----------- | -------- | ------------------- | ------------------------------------------------------------------ |
| `mistral/mistral-large-latest`   | نص، صورة    | 262,144  | 16,384              | النموذج الافتراضي                                                  |
| `mistral/mistral-medium-2508`    | نص، صورة    | 262,144  | 8,192               | Mistral Medium 3.1                                                 |
| `mistral/mistral-small-latest`   | نص، صورة    | 128,000  | 16,384              | Mistral Small 4؛ استدلال قابل للضبط عبر API `reasoning_effort`    |
| `mistral/pixtral-large-latest`   | نص، صورة    | 128,000  | 32,768              | Pixtral                                                            |
| `mistral/codestral-latest`       | نص          | 256,000  | 4,096               | للبرمجة                                                            |
| `mistral/devstral-medium-latest` | نص          | 262,144  | 32,768              | Devstral 2                                                         |
| `mistral/magistral-small`        | نص          | 128,000  | 40,000              | مع تمكين الاستدلال                                                 |

## نسخ الصوت إلى نص (Voxtral)

استخدم Voxtral لنسخ الصوت إلى نص عبر مسار media understanding.

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

<Tip>
يستخدم مسار نسخ الوسائط نقطة النهاية `/v1/audio/transcriptions`. والنموذج الصوتي الافتراضي لـ Mistral هو `voxtral-mini-latest`.
</Tip>

## إعداد متقدم

<AccordionGroup>
  <Accordion title="Adjustable reasoning (mistral-small-latest)">
    يشير `mistral/mistral-small-latest` إلى Mistral Small 4 ويدعم [الاستدلال القابل للضبط](https://docs.mistral.ai/capabilities/reasoning/adjustable) على Chat Completions API عبر `reasoning_effort` (`none` يقلل التفكير الإضافي في المخرجات إلى الحد الأدنى؛ و`high` يُظهر آثار التفكير الكاملة قبل الإجابة النهائية).

    يربط OpenClaw مستوى **thinking** في الجلسة بواجهة API الخاصة بـ Mistral:

    | مستوى thinking في OpenClaw                         | `reasoning_effort` في Mistral |
    | -------------------------------------------------- | ----------------------------- |
    | **off** / **minimal**                              | `none`                        |
    | **low** / **medium** / **high** / **xhigh** / **adaptive** | `high`            |

    <Note>
    لا تستخدم نماذج فهرس Mistral المضمّنة الأخرى هذا المعامل. استمر في استخدام نماذج `magistral-*` عندما تريد سلوك Mistral الأصلي القائم على الاستدلال أولًا.
    </Note>

  </Accordion>

  <Accordion title="Memory embeddings">
    يمكن لـ Mistral تقديم تضمينات الذاكرة عبر `/v1/embeddings` (النموذج الافتراضي: `mistral-embed`).

    ```json5
    {
      memorySearch: { provider: "mistral" },
    }
    ```

  </Accordion>

  <Accordion title="Auth and base URL">
    - تستخدم مصادقة Mistral المتغير `MISTRAL_API_KEY`.
    - تكون قيمة Base URL الافتراضية للموفّر هي `https://api.mistral.ai/v1`.
    - النموذج الافتراضي في onboarding هو `mistral/mistral-large-latest`.
    - تستخدم Z.AI مصادقة Bearer مع مفتاح API الخاص بك.
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="Model selection" href="/ar/concepts/model-providers" icon="layers">
    اختيار الموفّرات، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="Media understanding" href="/tools/media-understanding" icon="microphone">
    إعداد نسخ الصوت إلى نص واختيار الموفّر.
  </Card>
</CardGroup>
