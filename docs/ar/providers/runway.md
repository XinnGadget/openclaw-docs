---
read_when:
    - تريد استخدام توليد الفيديو عبر Runway في OpenClaw
    - تحتاج إلى إعداد مفتاح API / متغيرات البيئة لـ Runway
    - تريد جعل Runway مزوّد الفيديو الافتراضي
summary: إعداد توليد الفيديو عبر Runway في OpenClaw
title: Runway
x-i18n:
    generated_at: "2026-04-12T23:32:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb9a2d26687920544222b0769f314743af245629fd45b7f456c0161a47476176
    source_path: providers/runway.md
    workflow: 15
---

# Runway

يوفّر OpenClaw مزوّد `runway` مدمجًا لتوليد الفيديو المستضاف.

| الخاصية      | القيمة                                                            |
| ------------ | ----------------------------------------------------------------- |
| معرّف المزوّد | `runway`                                                          |
| المصادقة     | `RUNWAYML_API_SECRET` ‏(الأساسي) أو `RUNWAY_API_KEY`              |
| API          | توليد فيديو Runway المعتمد على المهام (`GET /v1/tasks/{id}` polling) |

## البدء

<Steps>
  <Step title="تعيين مفتاح API">
    ```bash
    openclaw onboard --auth-choice runway-api-key
    ```
  </Step>
  <Step title="تعيين Runway كمزوّد الفيديو الافتراضي">
    ```bash
    openclaw config set agents.defaults.videoGenerationModel.primary "runway/gen4.5"
    ```
  </Step>
  <Step title="توليد فيديو">
    اطلب من الوكيل توليد فيديو. وسيتم استخدام Runway تلقائيًا.
  </Step>
</Steps>

## الأوضاع المدعومة

| الوضع          | النموذج            | الإدخال المرجعي              |
| -------------- | ------------------ | ---------------------------- |
| نص إلى فيديو   | `gen4.5` ‏(افتراضي) | لا يوجد                      |
| صورة إلى فيديو | `gen4.5`           | صورة محلية أو بعيدة واحدة    |
| فيديو إلى فيديو | `gen4_aleph`      | فيديو محلي أو بعيد واحد      |

<Note>
تُدعَم مراجع الصور والفيديو المحلية عبر data URI. وتوفّر عمليات التشغيل النصية فقط
حاليًا نسب الأبعاد `16:9` و`9:16`.
</Note>

<Warning>
يتطلب وضع فيديو إلى فيديو حاليًا `runway/gen4_aleph` تحديدًا.
</Warning>

## الإعدادات

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "runway/gen4.5",
      },
    },
  },
}
```

## ملاحظات متقدمة

<AccordionGroup>
  <Accordion title="الأسماء البديلة لمتغيرات البيئة">
    يتعرّف OpenClaw على كل من `RUNWAYML_API_SECRET` ‏(الأساسي) و`RUNWAY_API_KEY`.
    وسيؤدي أي من المتغيرين إلى مصادقة مزوّد Runway.
  </Accordion>

  <Accordion title="استطلاع المهام">
    يستخدم Runway واجهة API قائمة على المهام. بعد إرسال طلب توليد، يقوم OpenClaw
    باستطلاع `GET /v1/tasks/{id}` حتى يصبح الفيديو جاهزًا. ولا يلزم أي
    إعداد إضافي لسلوك الاستطلاع هذا.
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="توليد الفيديو" href="/ar/tools/video-generation" icon="video">
    معلمات الأداة المشتركة، واختيار Provider، والسلوك غير المتزامن.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference#agent-defaults" icon="gear">
    إعدادات الوكيل الافتراضية بما في ذلك نموذج توليد الفيديو.
  </Card>
</CardGroup>
