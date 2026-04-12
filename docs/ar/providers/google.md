---
read_when:
    - تريد استخدام نماذج Google Gemini مع OpenClaw
    - تحتاج إلى مسار مصادقة مفتاح API أو OAuth
summary: إعداد Google Gemini ‏(مفتاح API + OAuth، وتوليد الصور، وفهم الوسائط، والبحث على الويب)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-12T23:30:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 64b848add89061b208a5d6b19d206c433cace5216a0ca4b63d56496aecbde452
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

يوفّر Plugin Google الوصول إلى نماذج Gemini عبر Google AI Studio، بالإضافة إلى
توليد الصور، وفهم الوسائط (الصور/الصوت/الفيديو)، والبحث على الويب عبر
Gemini Grounding.

- المزوّد: `google`
- المصادقة: `GEMINI_API_KEY` أو `GOOGLE_API_KEY`
- API: Google Gemini API
- مزوّد بديل: `google-gemini-cli` ‏(OAuth)

## البدء

اختر طريقة المصادقة المفضلة لديك واتبع خطوات الإعداد.

<Tabs>
  <Tab title="مفتاح API">
    **الأفضل لـ:** الوصول القياسي إلى Gemini API عبر Google AI Studio.

    <Steps>
      <Step title="شغّل الإعداد">
        ```bash
        openclaw onboard --auth-choice gemini-api-key
        ```

        أو مرّر المفتاح مباشرة:

        ```bash
        openclaw onboard --non-interactive \
          --mode local \
          --auth-choice gemini-api-key \
          --gemini-api-key "$GEMINI_API_KEY"
        ```
      </Step>
      <Step title="عيّن نموذجًا افتراضيًا">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "google/gemini-3.1-pro-preview" },
            },
          },
        }
        ```
      </Step>
      <Step title="تحقق من أن النموذج متاح">
        ```bash
        openclaw models list --provider google
        ```
      </Step>
    </Steps>

    <Tip>
    يُقبل كل من متغيري البيئة `GEMINI_API_KEY` و`GOOGLE_API_KEY`. استخدم أيًّا منهما لديك مضبوطًا بالفعل.
    </Tip>

  </Tab>

  <Tab title="Gemini CLI (OAuth)">
    **الأفضل لـ:** إعادة استخدام تسجيل دخول Gemini CLI موجود عبر PKCE OAuth بدلًا من مفتاح API منفصل.

    <Warning>
    إن المزوّد `google-gemini-cli` تكامل غير رسمي. أفاد بعض المستخدمين
    بوجود قيود على الحساب عند استخدام OAuth بهذه الطريقة. استخدمه على مسؤوليتك الخاصة.
    </Warning>

    <Steps>
      <Step title="ثبّت Gemini CLI">
        يجب أن يكون الأمر المحلي `gemini` متاحًا على `PATH`.

        ```bash
        # Homebrew
        brew install gemini-cli

        # أو npm
        npm install -g @google/gemini-cli
        ```

        يدعم OpenClaw كلاً من تثبيتات Homebrew والتثبيتات العامة عبر npm، بما في ذلك
        التخطيطات الشائعة على Windows/npm.
      </Step>
      <Step title="سجّل الدخول عبر OAuth">
        ```bash
        openclaw models auth login --provider google-gemini-cli --set-default
        ```
      </Step>
      <Step title="تحقق من أن النموذج متاح">
        ```bash
        openclaw models list --provider google-gemini-cli
        ```
      </Step>
    </Steps>

    - النموذج الافتراضي: `google-gemini-cli/gemini-3-flash-preview`
    - الاسم المستعار: `gemini-cli`

    **متغيرات البيئة:**

    - `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
    - `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

    (أو صيغ `GEMINI_CLI_*`.)

    <Note>
    إذا فشلت طلبات Gemini CLI OAuth بعد تسجيل الدخول، فعيّن `GOOGLE_CLOUD_PROJECT` أو
    `GOOGLE_CLOUD_PROJECT_ID` على مضيف Gateway ثم أعد المحاولة.
    </Note>

    <Note>
    إذا فشل تسجيل الدخول قبل بدء تدفق المتصفح، فتأكد من أن الأمر المحلي `gemini`
    مثبّت وموجود على `PATH`.
    </Note>

    إن المزوّد `google-gemini-cli` المعتمد على OAuth فقط هو
    سطح منفصل للاستدلال النصي. ويبقى توليد الصور، وفهم الوسائط، وGemini Grounding على
    معرّف المزوّد `google`.

  </Tab>
</Tabs>

## الإمكانات

| الإمكانية             | مدعومة         |
| ---------------------- | ----------------- |
| إكمالات الدردشة       | نعم               |
| توليد الصور       | نعم               |
| توليد الموسيقى       | نعم               |
| فهم الصور    | نعم               |
| نسخ الصوت إلى نص    | نعم               |
| فهم الفيديو    | نعم               |
| البحث على الويب (Grounding) | نعم               |
| التفكير/الاستدلال     | نعم (Gemini 3.1+) |
| نماذج Gemma 4         | نعم               |

<Tip>
تدعم نماذج Gemma 4 (على سبيل المثال `gemma-4-26b-a4b-it`) وضع التفكير. يقوم OpenClaw
بإعادة كتابة `thinkingBudget` إلى `thinkingLevel` مدعوم من Google في نماذج Gemma 4.
ويؤدي ضبط التفكير إلى `off` إلى إبقاء التفكير معطّلًا بدلًا من ربطه بـ
`MINIMAL`.
</Tip>

## توليد الصور

يستخدم مزوّد توليد الصور المضمّن `google` افتراضيًا
`google/gemini-3.1-flash-image-preview`.

- يدعم أيضًا `google/gemini-3-pro-image-preview`
- التوليد: حتى 4 صور لكل طلب
- وضع التحرير: مفعّل، حتى 5 صور إدخال
- عناصر التحكم الهندسية: `size` و`aspectRatio` و`resolution`

لاستخدام Google كمزوّد الصور الافتراضي:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "google/gemini-3.1-flash-image-preview",
      },
    },
  },
}
```

<Note>
راجع [Image Generation](/ar/tools/image-generation) لمعلمات الأداة المشتركة، واختيار المزوّد، وسلوك التبديل الاحتياطي.
</Note>

## توليد الفيديو

يسجّل Plugin ‏`google` المضمّن أيضًا توليد الفيديو عبر الأداة المشتركة
`video_generate`.

- نموذج الفيديو الافتراضي: `google/veo-3.1-fast-generate-preview`
- الأوضاع: نص إلى فيديو، وصورة إلى فيديو، وتدفقات مرجعية لفيديو واحد
- يدعم `aspectRatio` و`resolution` و`audio`
- الحد الحالي للمدة: **من 4 إلى 8 ثوانٍ**

لاستخدام Google كمزوّد الفيديو الافتراضي:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
      },
    },
  },
}
```

<Note>
راجع [Video Generation](/ar/tools/video-generation) لمعلمات الأداة المشتركة، واختيار المزوّد، وسلوك التبديل الاحتياطي.
</Note>

## توليد الموسيقى

يسجّل Plugin ‏`google` المضمّن أيضًا توليد الموسيقى عبر الأداة المشتركة
`music_generate`.

- نموذج الموسيقى الافتراضي: `google/lyria-3-clip-preview`
- يدعم أيضًا `google/lyria-3-pro-preview`
- عناصر تحكم الموجّه: `lyrics` و`instrumental`
- تنسيق الإخراج: `mp3` افتراضيًا، بالإضافة إلى `wav` على `google/lyria-3-pro-preview`
- المدخلات المرجعية: حتى 10 صور
- تفصل التشغيلات المدعومة بالجلسات عبر تدفق المهام/الحالة المشترك، بما في ذلك `action: "status"`

لاستخدام Google كمزوّد الموسيقى الافتراضي:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
      },
    },
  },
}
```

<Note>
راجع [Music Generation](/ar/tools/music-generation) لمعلمات الأداة المشتركة، واختيار المزوّد، وسلوك التبديل الاحتياطي.
</Note>

## الإعداد المتقدم

<AccordionGroup>
  <Accordion title="إعادة استخدام التخزين المؤقت المباشر لـ Gemini">
    في تشغيلات Gemini API المباشرة (`api: "google-generative-ai"`)، يمرّر OpenClaw
    معرّف `cachedContent` مضبوطًا إلى طلبات Gemini.

    - اضبط معلمات على مستوى النموذج أو بشكل عام باستخدام
      `cachedContent` أو الشكل القديم `cached_content`
    - إذا وُجد الاثنان، تكون الأولوية لـ `cachedContent`
    - مثال على القيمة: `cachedContents/prebuilt-context`
    - يتم تطبيع استخدام إصابة التخزين المؤقت في Gemini إلى `cacheRead` في OpenClaw انطلاقًا من
      القيمة العليا `cachedContentTokenCount`

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "google/gemini-2.5-pro": {
              params: {
                cachedContent: "cachedContents/prebuilt-context",
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="ملاحظات استخدام JSON في Gemini CLI">
    عند استخدام مزوّد OAuth ‏`google-gemini-cli`، يقوم OpenClaw بتطبيع
    خرج JSON من CLI على النحو التالي:

    - يأتي نص الرد من الحقل `response` في JSON الخاص بـ CLI.
    - تعود معلومات الاستخدام إلى `stats` عندما يترك CLI الحقل `usage` فارغًا.
    - يتم تطبيع `stats.cached` إلى `cacheRead` في OpenClaw.
    - إذا كان `stats.input` مفقودًا، يستنتج OpenClaw رموز الإدخال من
      `stats.input_tokens - stats.cached`.

  </Accordion>

  <Accordion title="إعداد البيئة والخدمة daemon">
    إذا كان Gateway يعمل كخدمة daemon (`launchd`/`systemd`)، فتأكد من أن `GEMINI_API_KEY`
    متاح لتلك العملية (على سبيل المثال، في `~/.openclaw/.env` أو عبر
    `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدين، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="توليد الصور" href="/ar/tools/image-generation" icon="image">
    معلمات أداة الصور المشتركة واختيار المزوّد.
  </Card>
  <Card title="توليد الفيديو" href="/ar/tools/video-generation" icon="video">
    معلمات أداة الفيديو المشتركة واختيار المزوّد.
  </Card>
  <Card title="توليد الموسيقى" href="/ar/tools/music-generation" icon="music">
    معلمات أداة الموسيقى المشتركة واختيار المزوّد.
  </Card>
</CardGroup>
