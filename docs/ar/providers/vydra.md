---
read_when:
    - تريد توليد وسائط Vydra في OpenClaw
    - تحتاج إلى إرشادات إعداد مفتاح API لـ Vydra
summary: استخدام الصور والفيديو والكلام من Vydra في OpenClaw
title: Vydra
x-i18n:
    generated_at: "2026-04-07T07:21:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 24006a687ed6f9792e7b2b10927cc7ad71c735462a92ce03d5fa7c2b2ee2fcc2
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

تضيف إضافة Vydra المضمّنة ما يلي:

- توليد الصور عبر `vydra/grok-imagine`
- توليد الفيديو عبر `vydra/veo3` و `vydra/kling`
- تحويل النص إلى كلام عبر مسار TTS الخاص بـ Vydra والمدعوم من ElevenLabs

يستخدم OpenClaw مفتاح `VYDRA_API_KEY` نفسه للقدرات الثلاث كلها.

## عنوان URL الأساسي المهم

استخدم `https://www.vydra.ai/api/v1`.

يقوم المضيف الجذري لـ Vydra (`https://vydra.ai/api/v1`) حاليًا بإعادة التوجيه إلى `www`. تُسقط بعض عملاء HTTP ترويسة `Authorization` عند إعادة التوجيه هذه بين المضيفين، مما يحوّل مفتاح API صالحًا إلى فشل مضلل في المصادقة. تستخدم الإضافة المضمّنة عنوان URL الأساسي `www` مباشرةً لتجنّب ذلك.

## الإعداد

التهيئة التفاعلية:

```bash
openclaw onboard --auth-choice vydra-api-key
```

أو عيّن متغير البيئة مباشرةً:

```bash
export VYDRA_API_KEY="vydra_live_..."
```

## توليد الصور

نموذج الصور الافتراضي:

- `vydra/grok-imagine`

عيّنه كمزوّد الصور الافتراضي:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "vydra/grok-imagine",
      },
    },
  },
}
```

الدعم المضمّن الحالي يقتصر على تحويل النص إلى صورة فقط. تتوقع مسارات التحرير المستضافة لدى Vydra عناوين URL لصور بعيدة، ولا يضيف OpenClaw بعد جسر رفع خاصًا بـ Vydra في الإضافة المضمّنة.

راجع [توليد الصور](/ar/tools/image-generation) للاطلاع على سلوك الأداة المشتركة.

## توليد الفيديو

نماذج الفيديو المسجلة:

- `vydra/veo3` لتحويل النص إلى فيديو
- `vydra/kling` لتحويل الصورة إلى فيديو

عيّن Vydra كمزوّد الفيديو الافتراضي:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "vydra/veo3",
      },
    },
  },
}
```

ملاحظات:

- `vydra/veo3` مضمّن كنموذج لتحويل النص إلى فيديو فقط.
- يتطلب `vydra/kling` حاليًا مرجع عنوان URL لصورة بعيدة. ويتم رفض رفع الملفات المحلية مسبقًا.
- كان مسار HTTP الحالي `kling` في Vydra غير متسق بشأن ما إذا كان يتطلب `image_url` أو `video_url`؛ ويقوم المزوّد المضمّن بربط عنوان URL للصورة البعيدة نفسه في كلا الحقلين.
- تظل الإضافة المضمّنة محافظة ولا تمرّر عناصر تحكم غير موثقة مثل نسبة العرض إلى الارتفاع أو الدقة أو العلامة المائية أو الصوت المُولَّد.

تغطية مباشرة خاصة بالمزوّد:

```bash
OPENCLAW_LIVE_TEST=1 \
OPENCLAW_LIVE_VYDRA_VIDEO=1 \
pnpm test:live -- extensions/vydra/vydra.live.test.ts
```

يغطي ملف Vydra المباشر المضمّن الآن ما يلي:

- `vydra/veo3` لتحويل النص إلى فيديو
- `vydra/kling` لتحويل الصورة إلى فيديو باستخدام عنوان URL لصورة بعيدة

يمكنك تجاوز العنصر المرجعي للصورة البعيدة عند الحاجة:

```bash
export OPENCLAW_LIVE_VYDRA_KLING_IMAGE_URL="https://example.com/reference.png"
```

راجع [توليد الفيديو](/ar/tools/video-generation) للاطلاع على سلوك الأداة المشتركة.

## تحويل النص إلى كلام

عيّن Vydra كمزوّد الكلام:

```json5
{
  messages: {
    tts: {
      provider: "vydra",
      providers: {
        vydra: {
          apiKey: "${VYDRA_API_KEY}",
          voiceId: "21m00Tcm4TlvDq8ikWAM",
        },
      },
    },
  },
}
```

القيم الافتراضية:

- النموذج: `elevenlabs/tts`
- معرّف الصوت: `21m00Tcm4TlvDq8ikWAM`

تعرض الإضافة المضمّنة حاليًا صوتًا افتراضيًا واحدًا معروف الموثوقية وتعيد ملفات صوت MP3.

## ذو صلة

- [دليل المزوّدين](/ar/providers/index)
- [توليد الصور](/ar/tools/image-generation)
- [توليد الفيديو](/ar/tools/video-generation)
