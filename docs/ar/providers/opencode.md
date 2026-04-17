---
read_when:
    - تريد الوصول إلى النماذج المستضافة على OpenCode
    - تريد الاختيار بين فهرسي Zen وGo
summary: استخدم فهارس OpenCode Zen وGo مع OpenClaw
title: OpenCode
x-i18n:
    generated_at: "2026-04-12T23:32:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: a68444d8c403c3caba4a18ea47f078c7a4c163f874560e1fad0e818afb6e0e60
    source_path: providers/opencode.md
    workflow: 15
---

# OpenCode

يوفّر OpenCode فهرسين مستضافين في OpenClaw:

| الفهرس | البادئة            | مزود التشغيل   |
| ------ | ------------------ | -------------- |
| **Zen** | `opencode/...`    | `opencode`     |
| **Go**  | `opencode-go/...` | `opencode-go`  |

يستخدم كلا الفهرسين مفتاح OpenCode API نفسه. ويُبقي OpenClaw معرّفات مزود التشغيل
منفصلة حتى يظل التوجيه لكل نموذج في المنبع صحيحًا، لكن الإعداد الأولي والوثائق
يتعاملان معهما باعتبارهما إعداد OpenCode واحدًا.

## البدء

<Tabs>
  <Tab title="فهرس Zen">
    **الأفضل لـ:** وكيل OpenCode المتعدد النماذج المُنسَّق (Claude وGPT وGemini).

    <Steps>
      <Step title="شغّل الإعداد الأولي">
        ```bash
        openclaw onboard --auth-choice opencode-zen
        ```

        أو مرّر المفتاح مباشرة:

        ```bash
        openclaw onboard --opencode-zen-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="عيّن نموذج Zen كنموذج افتراضي">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode/claude-opus-4-6"
        ```
      </Step>
      <Step title="تحقق من توفر النماذج">
        ```bash
        openclaw models list --provider opencode
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="فهرس Go">
    **الأفضل لـ:** مجموعة Kimi وGLM وMiniMax المستضافة على OpenCode.

    <Steps>
      <Step title="شغّل الإعداد الأولي">
        ```bash
        openclaw onboard --auth-choice opencode-go
        ```

        أو مرّر المفتاح مباشرة:

        ```bash
        openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="عيّن نموذج Go كنموذج افتراضي">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode-go/kimi-k2.5"
        ```
      </Step>
      <Step title="تحقق من توفر النماذج">
        ```bash
        openclaw models list --provider opencode-go
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## مثال على الإعداد

```json5
{
  env: { OPENCODE_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

## الفهارس

### Zen

| الخاصية        | القيمة                                                                  |
| -------------- | ----------------------------------------------------------------------- |
| مزود التشغيل   | `opencode`                                                              |
| أمثلة على النماذج | `opencode/claude-opus-4-6`, `opencode/gpt-5.4`, `opencode/gemini-3-pro` |

### Go

| الخاصية        | القيمة                                                                   |
| -------------- | ------------------------------------------------------------------------ |
| مزود التشغيل   | `opencode-go`                                                            |
| أمثلة على النماذج | `opencode-go/kimi-k2.5`, `opencode-go/glm-5`, `opencode-go/minimax-m2.5` |

## ملاحظات متقدمة

<AccordionGroup>
  <Accordion title="أسماء مفتاح API البديلة">
    `OPENCODE_ZEN_API_KEY` مدعوم أيضًا كاسم بديل لـ `OPENCODE_API_KEY`.
  </Accordion>

  <Accordion title="بيانات الاعتماد المشتركة">
    يؤدي إدخال مفتاح OpenCode واحد أثناء الإعداد إلى تخزين بيانات الاعتماد لكلا
    مزودي التشغيل. لا تحتاج إلى تشغيل الإعداد الأولي لكل فهرس على حدة.
  </Accordion>

  <Accordion title="الفوترة ولوحة التحكم">
    تقوم بتسجيل الدخول إلى OpenCode، وتضيف تفاصيل الفوترة، وتنسخ مفتاح API الخاص بك. تتم إدارة الفوترة
    ومدى توفر الفهرس من لوحة تحكم OpenCode.
  </Accordion>

  <Accordion title="سلوك إعادة تشغيل Gemini">
    تبقى مراجع OpenCode المدعومة بـ Gemini على مسار proxy-Gemini، لذلك يحتفظ OpenClaw
    هناك بتنقية توقيع التفكير في Gemini دون تمكين التحقق الأصلي من إعادة تشغيل Gemini
    أو عمليات إعادة كتابة التمهيد.
  </Accordion>

  <Accordion title="سلوك إعادة التشغيل لغير Gemini">
    تحتفظ مراجع OpenCode غير التابعة لـ Gemini بسياسة إعادة التشغيل الدنيا المتوافقة مع OpenAI.
  </Accordion>
</AccordionGroup>

<Tip>
يؤدي إدخال مفتاح OpenCode واحد أثناء الإعداد إلى تخزين بيانات الاعتماد لكلٍّ من مزودي التشغيل Zen و
Go، لذلك تحتاج إلى تشغيل الإعداد الأولي مرة واحدة فقط.
</Tip>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزودات، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference" icon="gear">
    المرجع الكامل لإعدادات الوكلاء والنماذج والمزودات.
  </Card>
</CardGroup>
