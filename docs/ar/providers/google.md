---
read_when:
    - تريد استخدام نماذج Google Gemini مع OpenClaw
    - تحتاج إلى مفتاح API أو تدفق مصادقة OAuth
summary: إعداد Google Gemini (مفتاح API + OAuth، إنشاء الصور، فهم الوسائط، TTS، البحث على الويب)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-16T07:17:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: ec2d62855f5e80efda758aad71bcaa95c38b1e41761fa1100d47a06c62881419
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

يوفر Plugin Google إمكانية الوصول إلى نماذج Gemini عبر Google AI Studio، بالإضافة إلى
إنشاء الصور، وفهم الوسائط (الصور/الصوت/الفيديو)، وتحويل النص إلى كلام، والبحث على الويب عبر
Gemini Grounding.

- المزوّد: `google`
- المصادقة: `GEMINI_API_KEY` أو `GOOGLE_API_KEY`
- API: Google Gemini API
- مزوّد بديل: `google-gemini-cli` (OAuth)

## البدء

اختر طريقة المصادقة المفضلة لديك واتبع خطوات الإعداد.

<Tabs>
  <Tab title="مفتاح API">
    **الأفضل لـ:** الوصول القياسي إلى Gemini API عبر Google AI Studio.

    <Steps>
      <Step title="تشغيل الإعداد الأولي">
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
      <Step title="تعيين نموذج افتراضي">
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
      <Step title="التحقق من أن النموذج متاح">
        ```bash
        openclaw models list --provider google
        ```
      </Step>
    </Steps>

    <Tip>
    يُقبل متغيرا البيئة `GEMINI_API_KEY` و`GOOGLE_API_KEY` كلاهما. استخدم أيًّا منهما لديك مُعدًّا بالفعل.
    </Tip>

  </Tab>

  <Tab title="Gemini CLI (OAuth)">
    **الأفضل لـ:** إعادة استخدام تسجيل دخول Gemini CLI موجود عبر PKCE OAuth بدلًا من مفتاح API منفصل.

    <Warning>
    يُعد المزوّد `google-gemini-cli` تكاملًا غير رسمي. يفيد بعض المستخدمين
    بوجود قيود على الحساب عند استخدام OAuth بهذه الطريقة. استخدمه على مسؤوليتك الخاصة.
    </Warning>

    <Steps>
      <Step title="تثبيت Gemini CLI">
        يجب أن يكون الأمر المحلي `gemini` متاحًا على `PATH`.

        ```bash
        # Homebrew
        brew install gemini-cli

        # أو npm
        npm install -g @google/gemini-cli
        ```

        يدعم OpenClaw كلاً من تثبيتات Homebrew وتثبيتات npm العامة، بما في ذلك
        تخطيطات Windows/npm الشائعة.
      </Step>
      <Step title="تسجيل الدخول عبر OAuth">
        ```bash
        openclaw models auth login --provider google-gemini-cli --set-default
        ```
      </Step>
      <Step title="التحقق من أن النموذج متاح">
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
    إذا فشلت طلبات Gemini CLI OAuth بعد تسجيل الدخول، فاضبط `GOOGLE_CLOUD_PROJECT` أو
    `GOOGLE_CLOUD_PROJECT_ID` على مضيف Gateway ثم أعد المحاولة.
    </Note>

    <Note>
    إذا فشل تسجيل الدخول قبل بدء تدفق المتصفح، فتأكد من أن الأمر المحلي `gemini`
    مُثبّت وموجود على `PATH`.
    </Note>

    يمثّل المزوّد `google-gemini-cli` المعتمد على OAuth فقط سطحًا منفصلًا
    للاستدلال النصي. بينما يبقى إنشاء الصور، وفهم الوسائط، وGemini Grounding على
    معرّف المزوّد `google`.

  </Tab>
</Tabs>

## الإمكانات

| الإمكانية             | مدعومة            |
| --------------------- | ----------------- |
| إكمالات الدردشة       | نعم               |
| إنشاء الصور           | نعم               |
| إنشاء الموسيقى        | نعم               |
| تحويل النص إلى كلام   | نعم               |
| فهم الصور             | نعم               |
| نسخ الصوت إلى نص      | نعم               |
| فهم الفيديو           | نعم               |
| البحث على الويب (Grounding) | نعم         |
| التفكير/الاستدلال     | نعم (Gemini 3.1+) |
| نماذج Gemma 4         | نعم               |

<Tip>
تدعم نماذج Gemma 4 (مثل `gemma-4-26b-a4b-it`) وضع التفكير. يعيد OpenClaw
كتابة `thinkingBudget` إلى قيمة Google `thinkingLevel` مدعومة لـ Gemma 4.
ويؤدي ضبط التفكير على `off` إلى إبقاء التفكير معطّلًا بدلًا من تعيينه إلى
`MINIMAL`.
</Tip>

## إنشاء الصور

يستخدم مزوّد إنشاء الصور المضمّن `google` افتراضيًا
`google/gemini-3.1-flash-image-preview`.

- يدعم أيضًا `google/gemini-3-pro-image-preview`
- الإنشاء: حتى 4 صور لكل طلب
- وضع التحرير: مفعّل، مع ما يصل إلى 5 صور إدخال
- عناصر التحكّم في الأبعاد: `size` و`aspectRatio` و`resolution`

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
راجع [إنشاء الصور](/ar/tools/image-generation) للاطلاع على معاملات الأداة المشتركة، واختيار المزوّد، وسلوك تجاوز الفشل.
</Note>

## إنشاء الفيديو

يسجّل Plugin ‏`google` المضمّن أيضًا إنشاء الفيديو عبر الأداة المشتركة
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
راجع [إنشاء الفيديو](/ar/tools/video-generation) للاطلاع على معاملات الأداة المشتركة، واختيار المزوّد، وسلوك تجاوز الفشل.
</Note>

## إنشاء الموسيقى

يسجّل Plugin ‏`google` المضمّن أيضًا إنشاء الموسيقى عبر الأداة المشتركة
`music_generate`.

- نموذج الموسيقى الافتراضي: `google/lyria-3-clip-preview`
- يدعم أيضًا `google/lyria-3-pro-preview`
- عناصر التحكّم في الطلب: `lyrics` و`instrumental`
- تنسيق الإخراج: `mp3` افتراضيًا، بالإضافة إلى `wav` على `google/lyria-3-pro-preview`
- مدخلات مرجعية: حتى 10 صور
- يتم فصل التشغيلات المعتمدة على الجلسات عبر تدفق المهمة/الحالة المشترك، بما في ذلك `action: "status"`

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
راجع [إنشاء الموسيقى](/ar/tools/music-generation) للاطلاع على معاملات الأداة المشتركة، واختيار المزوّد، وسلوك تجاوز الفشل.
</Note>

## تحويل النص إلى كلام

يستخدم مزوّد الكلام المضمّن `google` مسار Gemini API لتحويل النص إلى كلام مع
`gemini-3.1-flash-tts-preview`.

- الصوت الافتراضي: `Kore`
- المصادقة: `messages.tts.providers.google.apiKey` أو `models.providers.google.apiKey` أو `GEMINI_API_KEY` أو `GOOGLE_API_KEY`
- الإخراج: WAV لمرفقات TTS العادية، وPCM لـ Talk/الهاتف
- إخراج الملاحظات الصوتية الأصلي: غير مدعوم على مسار Gemini API هذا لأن API يعيد PCM بدلًا من Opus

لاستخدام Google كمزوّد TTS الافتراضي:

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "google",
      providers: {
        google: {
          model: "gemini-3.1-flash-tts-preview",
          voiceName: "Kore",
        },
      },
    },
  },
}
```

يقبل Gemini API TTS وسومًا صوتية تعبيرية بين أقواس مربعة في النص، مثل
`[whispers]` أو `[laughs]`. ولإبقاء الوسوم خارج رد الدردشة المرئي مع
إرسالها إلى TTS، ضعها داخل كتلة `[[tts:text]]...[[/tts:text]]`:

```text
إليك نص الرد النظيف.

[[tts:text]][whispers] إليك النسخة المنطوقة.[[/tts:text]]
```

<Note>
يُعد مفتاح API من Google Cloud Console والمقيّد بـ Gemini API صالحًا لهذا
المزوّد. هذا ليس مسار Cloud Text-to-Speech API المنفصل.
</Note>

## الإعدادات المتقدمة

<AccordionGroup>
  <Accordion title="إعادة استخدام ذاكرة Gemini المؤقتة مباشرة">
    بالنسبة لتشغيلات Gemini API المباشرة (`api: "google-generative-ai"`)، يقوم OpenClaw
    بتمرير معرّف `cachedContent` مضبوط إلى طلبات Gemini.

    - اضبط معاملات لكل نموذج أو معاملات عامة باستخدام
      `cachedContent` أو الصيغة القديمة `cached_content`
    - إذا وُجد الاثنان، فستكون الأولوية لـ `cachedContent`
    - مثال على القيمة: `cachedContents/prebuilt-context`
    - يتم توحيد استخدام إصابة الذاكرة المؤقتة في Gemini إلى `cacheRead` في OpenClaw من
      قيمة `cachedContentTokenCount` القادمة من المصدر

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
    عند استخدام مزوّد OAuth ‏`google-gemini-cli`، يقوم OpenClaw بتوحيد
    مخرجات JSON من CLI كما يلي:

    - يأتي نص الرد من الحقل `response` في JSON الخاص بـ CLI.
    - يعود الاستخدام إلى `stats` عندما يترك CLI الحقل `usage` فارغًا.
    - يتم توحيد `stats.cached` إلى `cacheRead` في OpenClaw.
    - إذا كان `stats.input` مفقودًا، يستنتج OpenClaw رموز الإدخال من
      `stats.input_tokens - stats.cached`.

  </Accordion>

  <Accordion title="إعداد البيئة وdaemon">
    إذا كان Gateway يعمل كخدمة daemon ‏(launchd/systemd)، فتأكد من أن `GEMINI_API_KEY`
    متاح لتلك العملية (على سبيل المثال في `~/.openclaw/.env` أو عبر
    `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدين، ومراجع النماذج، وسلوك تجاوز الفشل.
  </Card>
  <Card title="إنشاء الصور" href="/ar/tools/image-generation" icon="image">
    معاملات أداة الصور المشتركة واختيار المزوّد.
  </Card>
  <Card title="إنشاء الفيديو" href="/ar/tools/video-generation" icon="video">
    معاملات أداة الفيديو المشتركة واختيار المزوّد.
  </Card>
  <Card title="إنشاء الموسيقى" href="/ar/tools/music-generation" icon="music">
    معاملات أداة الموسيقى المشتركة واختيار المزوّد.
  </Card>
</CardGroup>
