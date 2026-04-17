---
read_when:
    - تريد استخدام توليد الفيديو Wan من Alibaba في OpenClaw
    - تحتاج إلى إعداد مفتاح API لـ Model Studio أو DashScope لتوليد الفيديو
summary: توليد فيديو Wan في Alibaba Model Studio داخل OpenClaw
title: Alibaba Model Studio
x-i18n:
    generated_at: "2026-04-12T23:28:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: a6e97d929952cdba7740f5ab3f6d85c18286b05596a4137bf80bbc8b54f32662
    source_path: providers/alibaba.md
    workflow: 15
---

# Alibaba Model Studio

يوفّر OpenClaw مزوّد توليد فيديو مضمّنًا باسم `alibaba` لنماذج Wan على
Alibaba Model Studio / DashScope.

- المزوّد: `alibaba`
- المصادقة المفضلة: `MODELSTUDIO_API_KEY`
- المقبول أيضًا: `DASHSCOPE_API_KEY`، `QWEN_API_KEY`
- API: توليد فيديو غير متزامن عبر DashScope / Model Studio

## البدء

<Steps>
  <Step title="تعيين مفتاح API">
    ```bash
    openclaw onboard --auth-choice qwen-standard-api-key
    ```
  </Step>
  <Step title="تعيين نموذج الفيديو الافتراضي">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "alibaba/wan2.6-t2v",
          },
        },
      },
    }
    ```
  </Step>
  <Step title="التحقق من توفر المزوّد">
    ```bash
    openclaw models list --provider alibaba
    ```
  </Step>
</Steps>

<Note>
سيعمل أي مفتاح من مفاتيح المصادقة المقبولة (`MODELSTUDIO_API_KEY` و`DASHSCOPE_API_KEY` و`QWEN_API_KEY`). يضبط خيار الإعداد `qwen-standard-api-key` بيانات اعتماد DashScope المشتركة.
</Note>

## نماذج Wan المضمّنة

يسجّل المزوّد المضمّن `alibaba` حاليًا ما يلي:

| مرجع النموذج | الوضع |
| -------------------------- | ------------------------- |
| `alibaba/wan2.6-t2v`       | نص إلى فيديو |
| `alibaba/wan2.6-i2v`       | صورة إلى فيديو |
| `alibaba/wan2.6-r2v`       | مرجع إلى فيديو |
| `alibaba/wan2.6-r2v-flash` | مرجع إلى فيديو (سريع) |
| `alibaba/wan2.7-r2v`       | مرجع إلى فيديو |

## الحدود الحالية

| المعلمة | الحد |
| --------------------- | --------------------------------------------------------- |
| فيديوهات الإخراج | حتى **1** لكل طلب |
| صور الإدخال | حتى **1** |
| فيديوهات الإدخال | حتى **4** |
| المدة | حتى **10 ثوانٍ** |
| عناصر التحكم المدعومة | `size` و`aspectRatio` و`resolution` و`audio` و`watermark` |
| صورة/فيديو مرجعي | عناوين URL بعيدة `http(s)` فقط |

<Warning>
يتطلب وضع الصورة/الفيديو المرجعي حاليًا **عناوين URL بعيدة من نوع http(s)**. لا يتم دعم مسارات الملفات المحلية لمدخلات المرجع.
</Warning>

## الإعداد المتقدم

<AccordionGroup>
  <Accordion title="العلاقة مع Qwen">
    يستخدم المزوّد المضمّن `qwen` أيضًا نقاط نهاية DashScope المستضافة من Alibaba من أجل
    توليد فيديو Wan. استخدم:

    - `qwen/...` عندما تريد سطح مزوّد Qwen القياسي
    - `alibaba/...` عندما تريد سطح Wan المباشر المملوك للمورّد

    راجع [مستندات مزوّد Qwen](/ar/providers/qwen) لمزيد من التفاصيل.

  </Accordion>

  <Accordion title="أولوية مفتاح المصادقة">
    يتحقق OpenClaw من مفاتيح المصادقة بهذا الترتيب:

    1. `MODELSTUDIO_API_KEY` (مفضّل)
    2. `DASHSCOPE_API_KEY`
    3. `QWEN_API_KEY`

    أيّ من هذه المفاتيح سيصادق مزوّد `alibaba`.

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="توليد الفيديو" href="/ar/tools/video-generation" icon="video">
    معلمات أداة الفيديو المشتركة واختيار المزوّد.
  </Card>
  <Card title="Qwen" href="/ar/providers/qwen" icon="microchip">
    إعداد مزوّد Qwen وتكامل DashScope.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference#agent-defaults" icon="gear">
    الإعدادات الافتراضية للوكيل وضبط النموذج.
  </Card>
</CardGroup>
