---
read_when:
    - تريد استخدام Deepgram لتحويل الكلام إلى نص للمرفقات الصوتية
    - تحتاج إلى مثال إعداد سريع لـ Deepgram
summary: نسخ Deepgram للملاحظات الصوتية الواردة
title: Deepgram
x-i18n:
    generated_at: "2026-04-12T23:30:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 091523d6669e3d258f07c035ec756bd587299b6c7025520659232b1b2c1e21a5
    source_path: providers/deepgram.md
    workflow: 15
---

# Deepgram (نسخ الصوت)

Deepgram هي API لتحويل الكلام إلى نص. وفي OpenClaw تُستخدم من أجل **نسخ
الصوت/الملاحظات الصوتية الواردة** عبر `tools.media.audio`.

عند تمكينها، يقوم OpenClaw برفع الملف الصوتي إلى Deepgram وحقن النص المنسوخ
في مسار الرد (`{{Transcript}}` + كتلة `[Audio]`). هذا **ليس بثًا مباشرًا**؛
بل يستخدم نقطة نهاية النسخ للتسجيلات المسبقة.

| التفاصيل      | القيمة                                                     |
| ------------- | ---------------------------------------------------------- |
| الموقع        | [deepgram.com](https://deepgram.com)                       |
| المستندات     | [developers.deepgram.com](https://developers.deepgram.com) |
| المصادقة      | `DEEPGRAM_API_KEY`                                         |
| النموذج الافتراضي | `nova-3`                                                |

## البدء

<Steps>
  <Step title="تعيين مفتاح API الخاص بك">
    أضف مفتاح API الخاص بـ Deepgram إلى البيئة:

    ```
    DEEPGRAM_API_KEY=dg_...
    ```

  </Step>
  <Step title="تمكين مزود الصوت">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            models: [{ provider: "deepgram", model: "nova-3" }],
          },
        },
      },
    }
    ```
  </Step>
  <Step title="إرسال ملاحظة صوتية">
    أرسل رسالة صوتية عبر أي قناة متصلة. سيقوم OpenClaw بنسخها
    عبر Deepgram وحقن النص المنسوخ في مسار الرد.
  </Step>
</Steps>

## خيارات الإعداد

| الخيار            | المسار                                                       | الوصف                                  |
| ----------------- | ------------------------------------------------------------ | -------------------------------------- |
| `model`           | `tools.media.audio.models[].model`                           | معرّف نموذج Deepgram (الافتراضي: `nova-3`) |
| `language`        | `tools.media.audio.models[].language`                        | تلميح اللغة (اختياري)                  |
| `detect_language` | `tools.media.audio.providerOptions.deepgram.detect_language` | تمكين اكتشاف اللغة (اختياري)           |
| `punctuate`       | `tools.media.audio.providerOptions.deepgram.punctuate`       | تمكين علامات الترقيم (اختياري)         |
| `smart_format`    | `tools.media.audio.providerOptions.deepgram.smart_format`    | تمكين التنسيق الذكي (اختياري)          |

<Tabs>
  <Tab title="مع تلميح لغة">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            models: [{ provider: "deepgram", model: "nova-3", language: "en" }],
          },
        },
      },
    }
    ```
  </Tab>
  <Tab title="مع خيارات Deepgram">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            providerOptions: {
              deepgram: {
                detect_language: true,
                punctuate: true,
                smart_format: true,
              },
            },
            models: [{ provider: "deepgram", model: "nova-3" }],
          },
        },
      },
    }
    ```
  </Tab>
</Tabs>

## ملاحظات

<AccordionGroup>
  <Accordion title="المصادقة">
    تتبع المصادقة ترتيب مصادقة المزود القياسي. ويُعد `DEEPGRAM_API_KEY`
    أبسط مسار.
  </Accordion>
  <Accordion title="الوكيل ونقاط النهاية المخصصة">
    يمكنك تجاوز نقاط النهاية أو الرؤوس باستخدام `tools.media.audio.baseUrl` و
    `tools.media.audio.headers` عند استخدام proxy.
  </Accordion>
  <Accordion title="سلوك الإخراج">
    يتبع الإخراج قواعد الصوت نفسها كما في المزودات الأخرى (حدود الحجم، والمهلات،
    وحقن النص المنسوخ).
  </Accordion>
</AccordionGroup>

<Note>
نسخ Deepgram مخصص **للتسجيلات المسبقة فقط** (وليس للبث المباشر في الوقت الحقيقي). يقوم OpenClaw
برفع الملف الصوتي الكامل وينتظر النص المنسوخ الكامل قبل حقنه
في المحادثة.
</Note>

## ذو صلة

<CardGroup cols={2}>
  <Card title="أدوات الوسائط" href="/tools/media" icon="photo-film">
    نظرة عامة على مسار معالجة الصوت والصور والفيديو.
  </Card>
  <Card title="الإعدادات" href="/ar/gateway/configuration" icon="gear">
    المرجع الكامل للإعدادات بما في ذلك إعدادات أدوات الوسائط.
  </Card>
  <Card title="استكشاف الأخطاء وإصلاحها" href="/ar/help/troubleshooting" icon="wrench">
    المشكلات الشائعة وخطوات التصحيح.
  </Card>
  <Card title="الأسئلة الشائعة" href="/ar/help/faq" icon="circle-question">
    الأسئلة الشائعة حول إعداد OpenClaw.
  </Card>
</CardGroup>
