---
read_when:
    - تريد توليد الوسائط عبر Vydra في OpenClaw
    - تحتاج إلى إرشادات إعداد مفتاح API لـ Vydra
summary: استخدم الصور والفيديو والكلام من Vydra في OpenClaw
title: Vydra
x-i18n:
    generated_at: "2026-04-12T23:33:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab623d14b656ce0b68d648a6393fcee3bb880077d6583e0d5c1012e91757f20e
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

يضيف Plugin المدمج Vydra ما يلي:

- توليد الصور عبر `vydra/grok-imagine`
- توليد الفيديو عبر `vydra/veo3` و`vydra/kling`
- توليد الكلام عبر مسار TTS في Vydra المعتمد على ElevenLabs

يستخدم OpenClaw المفتاح نفسه `VYDRA_API_KEY` للقدرات الثلاث جميعًا.

<Warning>
استخدم `https://www.vydra.ai/api/v1` كعنوان URL أساسي.

يقوم المضيف الأساسي لـ Vydra ‏(`https://vydra.ai/api/v1`) حاليًا بإعادة التوجيه إلى `www`. بعض عملاء HTTP يسقطون `Authorization` عند إعادة التوجيه عبر هذا التغيير في المضيف، ما يحوّل مفتاح API صالحًا إلى فشل مصادقة مضلل. يستخدم Plugin المدمج عنوان URL الأساسي `www` مباشرةً لتجنب ذلك.
</Warning>

## الإعداد

<Steps>
  <Step title="تشغيل التهيئة الأولية التفاعلية">
    ```bash
    openclaw onboard --auth-choice vydra-api-key
    ```

    أو اضبط متغير البيئة مباشرةً:

    ```bash
    export VYDRA_API_KEY="vydra_live_..."
    ```

  </Step>
  <Step title="اختيار قدرة افتراضية">
    اختر قدرة واحدة أو أكثر من القدرات أدناه (الصورة أو الفيديو أو الكلام) وطبّق الإعداد المطابق.
  </Step>
</Steps>

## القدرات

<AccordionGroup>
  <Accordion title="توليد الصور">
    نموذج الصور الافتراضي:

    - `vydra/grok-imagine`

    اضبطه كمزوّد الصور الافتراضي:

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

    يقتصر الدعم المدمج الحالي على تحويل النص إلى صورة فقط. تتوقع مسارات التحرير المستضافة في Vydra عناوين URL لصور بعيدة، ولا يضيف OpenClaw بعد جسر رفع خاصًا بـ Vydra في Plugin المدمج.

    <Note>
    راجع [توليد الصور](/ar/tools/image-generation) للاطلاع على معلمات الأداة المشتركة، واختيار Provider، وسلوك التحويل الاحتياطي.
    </Note>

  </Accordion>

  <Accordion title="توليد الفيديو">
    نماذج الفيديو المسجّلة:

    - `vydra/veo3` لتحويل النص إلى فيديو
    - `vydra/kling` لتحويل الصورة إلى فيديو

    اضبط Vydra كمزوّد الفيديو الافتراضي:

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

    - `vydra/veo3` مدمج لتحويل النص إلى فيديو فقط.
    - يتطلب `vydra/kling` حاليًا مرجع عنوان URL لصورة بعيدة. ويتم رفض رفع الملفات المحلية مسبقًا.
    - كان مسار HTTP الحالي لـ `kling` في Vydra غير متسق بشأن ما إذا كان يتطلب `image_url` أو `video_url`؛ ويقوم المزوّد المدمج بربط عنوان URL البعيد نفسه للصورة في كلا الحقلين.
    - يظل Plugin المدمج محافظًا ولا يمرّر عناصر تحكم بالأسلوب غير موثقة مثل نسبة الأبعاد أو الدقة أو العلامة المائية أو الصوت المُولَّد.

    <Note>
    راجع [توليد الفيديو](/ar/tools/video-generation) للاطلاع على معلمات الأداة المشتركة، واختيار Provider، وسلوك التحويل الاحتياطي.
    </Note>

  </Accordion>

  <Accordion title="اختبارات الفيديو الحية">
    التغطية الحية الخاصة بالمزوّد:

    ```bash
    OPENCLAW_LIVE_TEST=1 \
    OPENCLAW_LIVE_VYDRA_VIDEO=1 \
    pnpm test:live -- extensions/vydra/vydra.live.test.ts
    ```

    يغطي ملف Vydra الحي المدمج الآن ما يلي:

    - `vydra/veo3` لتحويل النص إلى فيديو
    - `vydra/kling` لتحويل الصورة إلى فيديو باستخدام عنوان URL لصورة بعيدة

    تجاوز مُثبّت الصورة البعيدة عند الحاجة:

    ```bash
    export OPENCLAW_LIVE_VYDRA_KLING_IMAGE_URL="https://example.com/reference.png"
    ```

  </Accordion>

  <Accordion title="توليد الكلام">
    اضبط Vydra كمزوّد للكلام:

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

    يوفّر Plugin المدمج حاليًا صوتًا افتراضيًا واحدًا معروف الجودة ويعيد ملفات صوتية بتنسيق MP3.

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="دليل المزوّدين" href="/ar/providers/index" icon="list">
    تصفّح جميع المزوّدين المتاحين.
  </Card>
  <Card title="توليد الصور" href="/ar/tools/image-generation" icon="image">
    معلمات أداة الصور المشتركة واختيار Provider.
  </Card>
  <Card title="توليد الفيديو" href="/ar/tools/video-generation" icon="video">
    معلمات أداة الفيديو المشتركة واختيار Provider.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference#agent-defaults" icon="gear">
    الإعدادات الافتراضية للوكيل وإعدادات النموذج.
  </Card>
</CardGroup>
