---
read_when:
    - تريد مفتاح API واحدًا للعديد من نماذج LLM
    - تريد تشغيل النماذج عبر OpenRouter في OpenClaw
summary: استخدم واجهة OpenRouter API الموحدة للوصول إلى العديد من النماذج في OpenClaw
title: OpenRouter
x-i18n:
    generated_at: "2026-04-12T23:32:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9083c30b9e9846a9d4ef071c350576d4c3083475f4108871eabbef0b9bb9a368
    source_path: providers/openrouter.md
    workflow: 15
---

# OpenRouter

يوفّر OpenRouter **واجهة API موحّدة** توجّه الطلبات إلى العديد من النماذج عبر
نقطة نهاية واحدة ومفتاح API واحد. وهو متوافق مع OpenAI، لذلك تعمل معظم حِزم SDK الخاصة بـ OpenAI
بمجرد تبديل عنوان URL الأساسي.

## البدء

<Steps>
  <Step title="احصل على مفتاح API الخاص بك">
    أنشئ مفتاح API على [openrouter.ai/keys](https://openrouter.ai/keys).
  </Step>
  <Step title="شغّل الإعداد الأولي">
    ```bash
    openclaw onboard --auth-choice openrouter-api-key
    ```
  </Step>
  <Step title="(اختياري) بدّل إلى نموذج محدد">
    يضبط الإعداد الأولي افتراضيًا `openrouter/auto`. ويمكنك اختيار نموذج محدد لاحقًا:

    ```bash
    openclaw models set openrouter/<provider>/<model>
    ```

  </Step>
</Steps>

## مثال على الإعداد

```json5
{
  env: { OPENROUTER_API_KEY: "sk-or-..." },
  agents: {
    defaults: {
      model: { primary: "openrouter/auto" },
    },
  },
}
```

## مراجع النماذج

<Note>
تتبع مراجع النماذج النمط `openrouter/<provider>/<model>`. وللاطلاع على القائمة الكاملة
للمزوّدين والنماذج المتاحة، راجع [/concepts/model-providers](/ar/concepts/model-providers).
</Note>

## المصادقة والرؤوس

يستخدم OpenRouter رمز Bearer مع مفتاح API الخاص بك داخليًا.

في طلبات OpenRouter الفعلية (`https://openrouter.ai/api/v1`)، يضيف OpenClaw أيضًا
رؤوس إسناد التطبيق الموثقة في OpenRouter:

| الرأس                     | القيمة                |
| ------------------------- | --------------------- |
| `HTTP-Referer`            | `https://openclaw.ai` |
| `X-OpenRouter-Title`      | `OpenClaw`            |
| `X-OpenRouter-Categories` | `cli-agent`           |

<Warning>
إذا أعدت توجيه مزوّد OpenRouter إلى proxy آخر أو عنوان URL أساسي مختلف، فلن يقوم OpenClaw
**بحقن** رؤوس OpenRouter الخاصة تلك أو علامات Anthropic الخاصة بالتخزين المؤقت.
</Warning>

## ملاحظات متقدمة

<AccordionGroup>
  <Accordion title="علامات التخزين المؤقت الخاصة بـ Anthropic">
    في مسارات OpenRouter التي تم التحقق منها، تحتفظ مراجع نماذج Anthropic
    بعلامات `cache_control` الخاصة بـ Anthropic ضمن OpenRouter التي يستخدمها OpenClaw
    لتحسين إعادة استخدام التخزين المؤقت للموجه في كتل موجهات النظام/المطوّر.
  </Accordion>

  <Accordion title="حقن التفكير / الاستدلال">
    في المسارات المدعومة غير `auto`، يربط OpenClaw مستوى التفكير المحدد
    بحمولات الاستدلال الخاصة بـ proxy في OpenRouter. ويتم تجاوز
    تلميحات النماذج غير المدعومة و`openrouter/auto` في حقن هذا الاستدلال.
  </Accordion>

  <Accordion title="تشكيل الطلبات الخاص بـ OpenAI فقط">
    لا يزال OpenRouter يعمل عبر المسار المتوافق مع OpenAI على نمط proxy، لذلك
    لا يتم تمرير تشكيل الطلبات الأصلي الخاص بـ OpenAI فقط مثل `serviceTier`، و`store` في Responses،
    وحمولات التوافق مع استدلال OpenAI، وتلميحات التخزين المؤقت للموجه.
  </Accordion>

  <Accordion title="المسارات المدعومة من Gemini">
    تبقى مراجع OpenRouter المعتمدة على Gemini ضمن مسار proxy-Gemini: يحتفظ OpenClaw
    هناك بتنقية Gemini thought-signature، لكنه لا يفعّل التحقق الأصلي من إعادة تشغيل Gemini
    أو عمليات إعادة الكتابة التمهيدية.
  </Accordion>

  <Accordion title="بيانات تعريف توجيه المزوّد">
    إذا مررت توجيه مزوّد OpenRouter ضمن معلمات النموذج، فسيقوم OpenClaw بتمريره
    كبيانات تعريف توجيه OpenRouter قبل تشغيل أغلفة البث المشتركة.
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدين، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="مرجع الإعداد" href="/ar/gateway/configuration-reference" icon="gear">
    المرجع الكامل لإعدادات الوكلاء، والنماذج، والمزوّدين.
  </Card>
</CardGroup>
