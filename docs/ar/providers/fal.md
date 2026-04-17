---
read_when:
    - تريد استخدام توليد الصور عبر fal في OpenClaw
    - تحتاج إلى تدفق المصادقة FAL_KEY
    - تريد إعدادات fal الافتراضية لـ `image_generate` أو `video_generate`
summary: إعداد توليد الصور والفيديو عبر fal في OpenClaw
title: fal
x-i18n:
    generated_at: "2026-04-12T23:30:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: ff275233179b4808d625383efe04189ad9e92af09944ba39f1e953e77378e347
    source_path: providers/fal.md
    workflow: 15
---

# fal

يوفّر OpenClaw مزود `fal` مدمجًا لتوليد الصور والفيديو المستضاف.

| الخاصية | القيمة                                                        |
| ------- | ------------------------------------------------------------- |
| Provider | `fal`                                                         |
| المصادقة | `FAL_KEY` (الأساسي؛ كما يعمل `FAL_API_KEY` كخيار احتياطي)    |
| API     | نقاط نهاية نماذج fal                                          |

## البدء

<Steps>
  <Step title="تعيين مفتاح API">
    ```bash
    openclaw onboard --auth-choice fal-api-key
    ```
  </Step>
  <Step title="تعيين نموذج صور افتراضي">
    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "fal/fal-ai/flux/dev",
          },
        },
      },
    }
    ```
  </Step>
</Steps>

## توليد الصور

القيمة الافتراضية لمزود توليد الصور `fal` المدمج هي
`fal/fal-ai/flux/dev`.

| الإمكانية      | القيمة                    |
| -------------- | ------------------------- |
| الحد الأقصى للصور | 4 لكل طلب                |
| وضع التحرير     | مفعّل، صورة مرجعية واحدة  |
| تجاوزات الحجم   | مدعومة                    |
| نسبة الأبعاد    | مدعومة                    |
| الدقة           | مدعومة                    |

<Warning>
نقطة نهاية تحرير الصور في fal **لا** تدعم تجاوزات `aspectRatio`.
</Warning>

لاستخدام fal كمزود الصور الافتراضي:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## توليد الفيديو

القيمة الافتراضية لمزود توليد الفيديو `fal` المدمج هي
`fal/fal-ai/minimax/video-01-live`.

| الإمكانية | القيمة                                                        |
| ---------- | ------------------------------------------------------------ |
| الأوضاع    | نص إلى فيديو، ومرجع بصورة واحدة                              |
| وقت التشغيل | مسار إرسال/حالة/نتيجة مدعوم بالطابور للمهام طويلة التشغيل   |

<AccordionGroup>
  <Accordion title="نماذج الفيديو المتاحة">
    **وكيل فيديو HeyGen:**

    - `fal/fal-ai/heygen/v2/video-agent`

    **Seedance 2.0:**

    - `fal/bytedance/seedance-2.0/fast/text-to-video`
    - `fal/bytedance/seedance-2.0/fast/image-to-video`
    - `fal/bytedance/seedance-2.0/text-to-video`
    - `fal/bytedance/seedance-2.0/image-to-video`

  </Accordion>

  <Accordion title="مثال إعداد Seedance 2.0">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "fal/bytedance/seedance-2.0/fast/text-to-video",
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="مثال إعداد وكيل فيديو HeyGen">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "fal/fal-ai/heygen/v2/video-agent",
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

<Tip>
استخدم `openclaw models list --provider fal` لعرض القائمة الكاملة لنماذج fal
المتاحة، بما في ذلك أي إدخالات أضيفت مؤخرًا.
</Tip>

## ذو صلة

<CardGroup cols={2}>
  <Card title="توليد الصور" href="/ar/tools/image-generation" icon="image">
    معلمات أداة الصور المشتركة واختيار Provider.
  </Card>
  <Card title="توليد الفيديو" href="/ar/tools/video-generation" icon="video">
    معلمات أداة الفيديو المشتركة واختيار Provider.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference#agent-defaults" icon="gear">
    الإعدادات الافتراضية للوكيل، بما في ذلك اختيار نموذج الصور والفيديو.
  </Card>
</CardGroup>
