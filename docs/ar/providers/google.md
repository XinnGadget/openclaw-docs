---
read_when:
    - تريد استخدام نماذج Google Gemini مع OpenClaw
    - تحتاج إلى تدفق المصادقة عبر مفتاح API أو OAuth
summary: إعداد Google Gemini ‏(مفتاح API + OAuth، وتوليد الصور، وفهم الوسائط، والبحث على الويب)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-07T07:21:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: 36cc7c7d8d19f6d4a3fb223af36c8402364fc309d14ffe922bd004203ceb1754
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

يوفر Google plugin الوصول إلى نماذج Gemini عبر Google AI Studio، بالإضافة إلى
توليد الصور، وفهم الوسائط (الصور/الصوت/الفيديو)، والبحث على الويب عبر
Gemini Grounding.

- المزود: `google`
- المصادقة: `GEMINI_API_KEY` أو `GOOGLE_API_KEY`
- API: ‏Google Gemini API
- مزود بديل: `google-gemini-cli` ‏(OAuth)

## البدء السريع

1. اضبط مفتاح API:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. اضبط نموذجًا افتراضيًا:

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## مثال غير تفاعلي

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## OAuth ‏(Gemini CLI)

يستخدم مزود بديل باسم `google-gemini-cli` مصادقة PKCE OAuth بدلًا من مفتاح
API. وهذا تكامل غير رسمي؛ وقد أفاد بعض المستخدمين بوجود قيود
على الحسابات. استخدمه على مسؤوليتك الخاصة.

- النموذج الافتراضي: `google-gemini-cli/gemini-3.1-pro-preview`
- الاسم البديل: `gemini-cli`
- متطلب التثبيت: توفر Gemini CLI محليًا باسم `gemini`
  - Homebrew: ‏`brew install gemini-cli`
  - npm: ‏`npm install -g @google/gemini-cli`
- تسجيل الدخول:

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

متغيرات البيئة:

- `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
- `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

(أو متغيرات `GEMINI_CLI_*` البديلة.)

إذا فشلت طلبات Gemini CLI OAuth بعد تسجيل الدخول، فاضبط
`GOOGLE_CLOUD_PROJECT` أو `GOOGLE_CLOUD_PROJECT_ID` على مضيف gateway ثم
أعد المحاولة.

إذا فشل تسجيل الدخول قبل بدء تدفق المتصفح، فتأكد من أن الأمر المحلي `gemini`
مثبّت وموجود على `PATH`. يدعم OpenClaw كلًا من تثبيتات Homebrew
وتثبيتات npm العامة، بما في ذلك تخطيطات Windows/npm الشائعة.

ملاحظات استخدام JSON في Gemini CLI:

- يأتي نص الرد من الحقل `response` في JSON الخاص بـ CLI.
- تعود معلومات الاستخدام إلى `stats` عندما يترك CLI الحقل `usage` فارغًا.
- يتم تطبيع `stats.cached` إلى `cacheRead` في OpenClaw.
- إذا كان `stats.input` مفقودًا، فإن OpenClaw يستنتج رموز الإدخال من
  `stats.input_tokens - stats.cached`.

## القدرات

| القدرة | مدعومة |
| ---------------------- | ----------------- |
| إكمالات الدردشة | نعم |
| توليد الصور | نعم |
| توليد الموسيقى | نعم |
| فهم الصور | نعم |
| نسخ الصوت | نعم |
| فهم الفيديو | نعم |
| البحث على الويب (Grounding) | نعم |
| التفكير/الاستدلال | نعم (Gemini 3.1+) |

## إعادة استخدام ذاكرة Gemini المؤقتة مباشرة

بالنسبة إلى تشغيلات Gemini API المباشرة (`api: "google-generative-ai"`)، يقوم OpenClaw الآن
بتمرير معرّف `cachedContent` المضبوط إلى طلبات Gemini.

- اضبط المعلمات لكل نموذج أو بشكل عام باستخدام
  `cachedContent` أو `cached_content` القديم
- إذا وُجد الاثنان، تكون الأولوية لـ `cachedContent`
- مثال على القيمة: `cachedContents/prebuilt-context`
- يتم تطبيع استخدام إصابة ذاكرة Gemini المؤقتة إلى `cacheRead` في OpenClaw من
  `cachedContentTokenCount` الصادر من المصدر

مثال:

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

## توليد الصور

يضبط مزود توليد الصور المضمّن `google` افتراضيًا على
`google/gemini-3.1-flash-image-preview`.

- يدعم أيضًا `google/gemini-3-pro-image-preview`
- التوليد: حتى 4 صور لكل طلب
- وضع التحرير: مفعّل، حتى 5 صور إدخال
- عناصر التحكم بالهندسة: `size` و`aspectRatio` و`resolution`

المزود `google-gemini-cli` المعتمد على OAuth فقط هو سطح منفصل
للاستدلال النصي. أما توليد الصور، وفهم الوسائط، وGemini Grounding فتبقى على
معرّف المزود `google`.

لاستخدام Google بوصفه مزود الصور الافتراضي:

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

راجع [توليد الصور](/ar/tools/image-generation) لمعلمات
الأداة المشتركة، واختيار المزود، وسلوك failover.

## توليد الفيديو

يسجل Google plugin المضمّن أيضًا توليد الفيديو عبر الأداة المشتركة
`video_generate`.

- نموذج الفيديو الافتراضي: `google/veo-3.1-fast-generate-preview`
- الأوضاع: من نص إلى فيديو، ومن صورة إلى فيديو، وتدفقات مرجعية لفيديو واحد
- يدعم `aspectRatio` و`resolution` و`audio`
- حد المدة الحالي: **من 4 إلى 8 ثوانٍ**

لاستخدام Google بوصفه مزود الفيديو الافتراضي:

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

راجع [توليد الفيديو](/ar/tools/video-generation) لمعلمات
الأداة المشتركة، واختيار المزود، وسلوك failover.

## توليد الموسيقى

يسجل Google plugin المضمّن أيضًا توليد الموسيقى عبر الأداة المشتركة
`music_generate`.

- نموذج الموسيقى الافتراضي: `google/lyria-3-clip-preview`
- يدعم أيضًا `google/lyria-3-pro-preview`
- عناصر التحكم في prompt: ‏`lyrics` و`instrumental`
- تنسيق الإخراج: `mp3` افتراضيًا، بالإضافة إلى `wav` على `google/lyria-3-pro-preview`
- مدخلات مرجعية: حتى 10 صور
- يتم فصل التشغيلات المدعومة بالجلسات عبر تدفق المهمة/الحالة المشترك، بما في ذلك `action: "status"`

لاستخدام Google بوصفه مزود الموسيقى الافتراضي:

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

راجع [توليد الموسيقى](/ar/tools/music-generation) لمعلمات
الأداة المشتركة، واختيار المزود، وسلوك failover.

## ملاحظة حول البيئة

إذا كان Gateway يعمل كخدمة daemon ‏(launchd/systemd)، فتأكد من أن `GEMINI_API_KEY`
متاح لتلك العملية (على سبيل المثال، في `~/.openclaw/.env` أو عبر
`env.shellEnv`).
