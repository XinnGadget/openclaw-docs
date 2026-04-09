---
read_when:
    - تريد استخدام Qwen مع OpenClaw
    - كنت تستخدم Qwen OAuth سابقًا
summary: استخدام Qwen Cloud عبر موفر qwen المضمّن في OpenClaw
title: Qwen
x-i18n:
    generated_at: "2026-04-09T01:30:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4786df2cb6ec1ab29d191d012c61dcb0e5468bf0f8561fbbb50eed741efad325
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**تمت إزالة Qwen OAuth.** لم يعد تكامل OAuth الخاص بالطبقة المجانية
(`qwen-portal`) الذي كان يستخدم نقاط نهاية `portal.qwen.ai` متاحًا.
راجع [Issue #49557](https://github.com/openclaw/openclaw/issues/49557) للاطلاع
على الخلفية.

</Warning>

## الموصى به: Qwen Cloud

يتعامل OpenClaw الآن مع Qwen بوصفه موفرًا مضمّنًا أساسيًا بالمعرّف القياسي
`qwen`. يستهدف الموفّر المضمّن نقاط نهاية Qwen Cloud / Alibaba DashScope و
Coding Plan ويحافظ على عمل معرّفات `modelstudio` القديمة بوصفها
أسماء مستعارة للتوافق.

- الموفّر: `qwen`
- متغير env المفضّل: `QWEN_API_KEY`
- المقبول أيضًا للتوافق: `MODELSTUDIO_API_KEY`، `DASHSCOPE_API_KEY`
- نمط API: متوافق مع OpenAI

إذا كنت تريد `qwen3.6-plus`، ففضّل نقطة النهاية **Standard (الدفع حسب الاستخدام)**.
قد يتأخر دعم Coding Plan عن الفهرس العام.

```bash
# نقطة نهاية Coding Plan العامة
openclaw onboard --auth-choice qwen-api-key

# نقطة نهاية Coding Plan في الصين
openclaw onboard --auth-choice qwen-api-key-cn

# نقطة نهاية Standard (الدفع حسب الاستخدام) العامة
openclaw onboard --auth-choice qwen-standard-api-key

# نقطة نهاية Standard (الدفع حسب الاستخدام) في الصين
openclaw onboard --auth-choice qwen-standard-api-key-cn
```

لا تزال معرّفات `auth-choice` القديمة `modelstudio-*` ومراجع النماذج `modelstudio/...`
تعمل بوصفها أسماء مستعارة للتوافق، لكن يجب أن تفضّل تدفقات الإعداد الجديدة
معرّفات `auth-choice` القياسية `qwen-*` ومراجع النماذج `qwen/...`.

بعد التهيئة، عيّن نموذجًا افتراضيًا:

```json5
{
  agents: {
    defaults: {
      model: { primary: "qwen/qwen3.5-plus" },
    },
  },
}
```

## أنواع الخطط ونقاط النهاية

| الخطة                      | المنطقة | خيار المصادقة             | نقطة النهاية                                     |
| -------------------------- | ------- | ------------------------- | ------------------------------------------------ |
| Standard (الدفع حسب الاستخدام) | الصين   | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1`      |
| Standard (الدفع حسب الاستخدام) | عامة    | `qwen-standard-api-key`    | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (اشتراك)       | الصين   | `qwen-api-key-cn`          | `coding.dashscope.aliyuncs.com/v1`               |
| Coding Plan (اشتراك)       | عامة    | `qwen-api-key`             | `coding-intl.dashscope.aliyuncs.com/v1`          |

يختار الموفّر نقطة النهاية تلقائيًا بناءً على خيار المصادقة لديك. تستخدم الخيارات
القياسية عائلة `qwen-*`؛ أما `modelstudio-*` فتبقى للتوافق فقط.
يمكنك التبديل باستخدام `baseUrl` مخصص في الإعداد.

تعلن نقاط نهاية Model Studio الأصلية عن توافق استخدام البث على
وسيلة النقل المشتركة `openai-completions`. يربط OpenClaw ذلك الآن بإمكانات
نقطة النهاية، لذا فإن معرّفات الموفّرين المخصصة المتوافقة مع DashScope والتي تستهدف
المضيفين الأصليين أنفسهم ترث سلوك استخدام البث نفسه بدلًا من
اشتراط معرّف الموفّر المضمّن `qwen` على وجه التحديد.

## احصل على مفتاح API الخاص بك

- **إدارة المفاتيح**: [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys)
- **الوثائق**: [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)

## الفهرس المضمّن

يشحن OpenClaw حاليًا فهرس Qwen المضمّن هذا. يكون الفهرس المضبوط
مدركًا لنقطة النهاية: إذ تحذف إعدادات Coding Plan النماذج التي لا يُعرف أنها تعمل إلا على
نقطة النهاية Standard.

| مرجع النموذج               | الإدخال      | السياق    | ملاحظات                                            |
| -------------------------- | ------------ | --------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus`         | نص، صورة     | 1,000,000 | النموذج الافتراضي                                  |
| `qwen/qwen3.6-plus`         | نص، صورة     | 1,000,000 | فضّل نقاط النهاية Standard عندما تحتاج هذا النموذج |
| `qwen/qwen3-max-2026-01-23` | نص           | 262,144   | سطر Qwen Max                                       |
| `qwen/qwen3-coder-next`     | نص           | 262,144   | برمجة                                              |
| `qwen/qwen3-coder-plus`     | نص           | 1,000,000 | برمجة                                              |
| `qwen/MiniMax-M2.5`         | نص           | 1,000,000 | التفكير مفعّل                                      |
| `qwen/glm-5`                | نص           | 202,752   | GLM                                                |
| `qwen/glm-4.7`              | نص           | 202,752   | GLM                                                |
| `qwen/kimi-k2.5`            | نص، صورة     | 262,144   | Moonshot AI عبر Alibaba                            |

قد يختلف التوفر أيضًا حسب نقطة النهاية وخطة الفوترة حتى عندما يكون النموذج
موجودًا في الفهرس المضمّن.

ينطبق توافق استخدام البث الأصلي على كل من مضيفي Coding Plan
ومضيفي Standard المتوافقين مع DashScope:

- `https://coding.dashscope.aliyuncs.com/v1`
- `https://coding-intl.dashscope.aliyuncs.com/v1`
- `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

## توفر Qwen 3.6 Plus

يتوفر `qwen3.6-plus` على نقاط نهاية Model Studio من نوع Standard (الدفع حسب الاستخدام):

- الصين: `dashscope.aliyuncs.com/compatible-mode/v1`
- عالمي: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

إذا أعادت نقاط نهاية Coding Plan خطأ "unsupported model" لـ
`qwen3.6-plus`، فانتقل إلى Standard (الدفع حسب الاستخدام) بدلًا من
زوج نقطة النهاية/المفتاح الخاص بـ Coding Plan.

## خطة القدرات

يتم حاليًا وضع امتداد `qwen` بوصفه موطن المورّد لسطح Qwen
Cloud الكامل، وليس فقط نماذج البرمجة/النص.

- نماذج النص/الدردشة: مضمّنة الآن
- استدعاء الأدوات، والمخرجات المنظمة، والتفكير: موروثة من وسيلة النقل المتوافقة مع OpenAI
- إنشاء الصور: مخطّط له على طبقة إضافة الموفّر
- فهم الصور/الفيديو: مضمّن الآن على نقطة النهاية Standard
- الكلام/الصوت: مخطّط له على طبقة إضافة الموفّر
- تضمينات الذاكرة/إعادة الترتيب: مخطّط لها عبر سطح محول التضمين
- إنشاء الفيديو: مضمّن الآن عبر قدرة إنشاء الفيديو المشتركة

## الإضافات متعددة الوسائط

يكشف امتداد `qwen` الآن أيضًا عن:

- فهم الفيديو عبر `qwen-vl-max-latest`
- إنشاء فيديو Wan عبر:
  - `wan2.6-t2v` (الافتراضي)
  - `wan2.6-i2v`
  - `wan2.6-r2v`
  - `wan2.6-r2v-flash`
  - `wan2.7-r2v`

تستخدم هذه الأسطح متعددة الوسائط نقاط نهاية DashScope من نوع **Standard**،
وليس نقاط نهاية Coding Plan.

- عنوان URL الأساسي لـ Standard العالمي/الدولي: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- عنوان URL الأساسي لـ Standard في الصين: `https://dashscope.aliyuncs.com/compatible-mode/v1`

في إنشاء الفيديو، يربط OpenClaw منطقة Qwen المضبوطة بمضيف DashScope AIGC
المطابق قبل إرسال المهمة:

- عالمي/دولي: `https://dashscope-intl.aliyuncs.com`
- الصين: `https://dashscope.aliyuncs.com`

وهذا يعني أن `models.providers.qwen.baseUrl` العادي الذي يشير إلى
مضيفي Qwen من نوع Coding Plan أو Standard سيُبقي إنشاء الفيديو على نقطة نهاية
فيديو DashScope الإقليمية الصحيحة.

لإنشاء الفيديو، عيّن نموذجًا افتراضيًا صراحةً:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

الحدود الحالية المضمّنة لإنشاء الفيديو في Qwen:

- حتى **1** فيديو خرج لكل طلب
- حتى **1** صورة إدخال
- حتى **4** مقاطع فيديو إدخال
- حتى **10 ثوانٍ** مدة
- يدعم `size` و`aspectRatio` و`resolution` و`audio` و`watermark`
- يتطلب وضع الصورة/الفيديو المرجعي حاليًا **عناوين URL بعيدة من نوع http(s)**. تُرفض
  مسارات الملفات المحلية مقدمًا لأن نقطة نهاية الفيديو في DashScope لا
  تقبل تحميل مخازن محلية لتلك المراجع.

راجع [Video Generation](/ar/tools/video-generation) للاطلاع على
معلمات الأداة المشتركة، واختيار الموفّر، وسلوك التحويل الاحتياطي.

## ملاحظة البيئة

إذا كانت البوابة تعمل كخدمة daemon ‏(launchd/systemd)، فتأكد من أن `QWEN_API_KEY`
متاح لتلك العملية (على سبيل المثال، في `~/.openclaw/.env` أو عبر
`env.shellEnv`).
