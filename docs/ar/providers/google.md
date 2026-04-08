---
read_when:
    - تريد استخدام نماذج Google Gemini مع OpenClaw
    - تحتاج إلى تدفق المصادقة بمفتاح API أو OAuth
summary: إعداد Google Gemini ‏(مفتاح API + OAuth، توليد الصور، فهم الوسائط، البحث على الويب)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-08T07:16:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: fad2ff68987301bd86145fa6e10de8c7b38d5bd5dbcd13db9c883f7f5b9a4e01
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

يوفر مكون Google الإضافي الوصول إلى نماذج Gemini من خلال Google AI Studio، بالإضافة إلى
توليد الصور، وفهم الوسائط (الصور/الصوت/الفيديو)، والبحث على الويب عبر
Gemini Grounding.

- المزوّد: `google`
- المصادقة: `GEMINI_API_KEY` أو `GOOGLE_API_KEY`
- API: ‏Google Gemini API
- المزوّد البديل: `google-gemini-cli` ‏(OAuth)

## البدء السريع

1. عيّن مفتاح API:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. عيّن نموذجًا افتراضيًا:

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

يستخدم المزوّد البديل `google-gemini-cli` مصادقة PKCE OAuth بدلًا من مفتاح
API. هذا تكامل غير رسمي؛ وقد أبلغ بعض المستخدمين عن
قيود على الحساب. استخدمه على مسؤوليتك الخاصة.

- النموذج الافتراضي: `google-gemini-cli/gemini-3-flash-preview`
- الاسم المستعار: `gemini-cli`
- متطلب التثبيت المسبق: توفر Gemini CLI محليًا باسم `gemini`
  - Homebrew: `brew install gemini-cli`
  - npm: `npm install -g @google/gemini-cli`
- تسجيل الدخول:

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

متغيرات البيئة:

- `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
- `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

(أو متغيرات `GEMINI_CLI_*`.)

إذا فشلت طلبات Gemini CLI OAuth بعد تسجيل الدخول، فعيّن
`GOOGLE_CLOUD_PROJECT` أو `GOOGLE_CLOUD_PROJECT_ID` على مضيف البوابة ثم
أعد المحاولة.

إذا فشل تسجيل الدخول قبل بدء تدفق المتصفح، فتأكد من أن الأمر المحلي `gemini`
مثبّت وموجود في `PATH`. يدعم OpenClaw كلًا من تثبيتات Homebrew
وتثبيتات npm العامة، بما في ذلك تخطيطات Windows/npm الشائعة.

ملاحظات استخدام JSON في Gemini CLI:

- يأتي نص الرد من الحقل `response` في JSON الخاص بـ CLI.
- يعود الاستخدام إلى `stats` عندما يترك CLI الحقل `usage` فارغًا.
- تتم تسوية `stats.cached` إلى `cacheRead` في OpenClaw.
- إذا كان `stats.input` مفقودًا، يشتق OpenClaw رموز الإدخال من
  `stats.input_tokens - stats.cached`.

## الإمكانات

| الإمكانية             | مدعومة            |
| ---------------------- | ----------------- |
| إكمالات الدردشة       | نعم               |
| توليد الصور           | نعم               |
| توليد الموسيقى        | نعم               |
| فهم الصور             | نعم               |
| نسخ الصوت             | نعم               |
| فهم الفيديو           | نعم               |
| البحث على الويب (Grounding) | نعم         |
| التفكير/الاستدلال     | نعم (Gemini 3.1+) |
| نماذج Gemma 4         | نعم               |

تدعم نماذج Gemma 4 ‏(على سبيل المثال `gemma-4-26b-a4b-it`) وضع التفكير. يعيد OpenClaw كتابة `thinkingBudget` إلى `thinkingLevel` مدعوم من Google لنماذج Gemma 4. يؤدي ضبط التفكير على `off` إلى إبقاء التفكير معطّلًا بدلًا من تعيينه إلى `MINIMAL`.

## إعادة استخدام ذاكرة التخزين المؤقت المباشرة لـ Gemini

في عمليات تشغيل Gemini API المباشرة (`api: "google-generative-ai"`)، يقوم OpenClaw الآن
بتمرير معرّف `cachedContent` مُعدّ مسبقًا إلى طلبات Gemini.

- اضبط المعلمات لكل نموذج أو على مستوى عام باستخدام
  `cachedContent` أو `cached_content` القديم
- إذا كان كلاهما موجودًا، تكون الأولوية لـ `cachedContent`
- مثال على القيمة: `cachedContents/prebuilt-context`
- تتم تسوية استخدام إصابة ذاكرة التخزين المؤقت في Gemini إلى `cacheRead` في OpenClaw من
  `cachedContentTokenCount` في المصدر

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

يستخدم مزوّد توليد الصور `google` المضمّن افتراضيًا
`google/gemini-3.1-flash-image-preview`.

- يدعم أيضًا `google/gemini-3-pro-image-preview`
- التوليد: حتى 4 صور لكل طلب
- وضع التحرير: مفعّل، حتى 5 صور إدخال
- عناصر التحكم في الأبعاد: `size` و`aspectRatio` و`resolution`

يُعدّ المزوّد `google-gemini-cli` المعتمد على OAuth فقط سطحًا منفصلًا
لاستدلال النص. يظل توليد الصور، وفهم الوسائط، وGemini Grounding على
معرّف المزوّد `google`.

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

راجع [توليد الصور](/ar/tools/image-generation) لمعلمات
الأداة المشتركة، واختيار المزوّد، وسلوك التبديل الاحتياطي.

## توليد الفيديو

يسجل مكون `google` الإضافي المضمّن أيضًا توليد الفيديو من خلال أداة
`video_generate` المشتركة.

- نموذج الفيديو الافتراضي: `google/veo-3.1-fast-generate-preview`
- الأوضاع: نص إلى فيديو، وصورة إلى فيديو، وتدفقات مرجعية لفيديو واحد
- يدعم `aspectRatio` و`resolution` و`audio`
- التقييد الحالي للمدة: **من 4 إلى 8 ثوانٍ**

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

راجع [توليد الفيديو](/ar/tools/video-generation) لمعلمات
الأداة المشتركة، واختيار المزوّد، وسلوك التبديل الاحتياطي.

## توليد الموسيقى

يسجل مكون `google` الإضافي المضمّن أيضًا توليد الموسيقى من خلال أداة
`music_generate` المشتركة.

- نموذج الموسيقى الافتراضي: `google/lyria-3-clip-preview`
- يدعم أيضًا `google/lyria-3-pro-preview`
- عناصر التحكم في المطالبة: `lyrics` و`instrumental`
- تنسيق الإخراج: `mp3` افتراضيًا، بالإضافة إلى `wav` على `google/lyria-3-pro-preview`
- المدخلات المرجعية: حتى 10 صور
- تُفصل عمليات التشغيل المدعومة بالجلسات عبر تدفق المهام/الحالة المشترك، بما في ذلك `action: "status"`

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

راجع [توليد الموسيقى](/ar/tools/music-generation) لمعلمات
الأداة المشتركة، واختيار المزوّد، وسلوك التبديل الاحتياطي.

## ملاحظة حول البيئة

إذا كانت البوابة تعمل كخدمة daemon ‏(`launchd/systemd`)، فتأكد من أن `GEMINI_API_KEY`
متاح لتلك العملية (على سبيل المثال، في `~/.openclaw/.env` أو عبر
`env.shellEnv`).
