---
read_when:
    - تبحث عن تعريفات قنوات الإصدار العامة
    - تبحث عن تسمية الإصدارات والوتيرة
summary: قنوات الإصدار العامة، وتسمية الإصدارات، والوتيرة
title: سياسة الإصدار
x-i18n:
    generated_at: "2026-04-12T23:33:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: dffc1ee5fdbb20bd1bf4b3f817d497fc0d87f70ed6c669d324fea66dc01d0b0b
    source_path: reference/RELEASING.md
    workflow: 15
---

# سياسة الإصدار

لدى OpenClaw ثلاثة مسارات إصدار عامة:

- stable: إصدارات موسومة تُنشر إلى npm `beta` افتراضيًا، أو إلى npm `latest` عند الطلب صراحةً
- beta: وسوم إصدارات تمهيدية تُنشر إلى npm `beta`
- dev: الرأس المتحرك للفرع `main`

## تسمية الإصدارات

- إصدار النسخة المستقرة: `YYYY.M.D`
  - وسم Git: `vYYYY.M.D`
- إصدار تصحيح النسخة المستقرة: `YYYY.M.D-N`
  - وسم Git: `vYYYY.M.D-N`
- إصدار beta التمهيدي: `YYYY.M.D-beta.N`
  - وسم Git: `vYYYY.M.D-beta.N`
- لا تُضف أصفارًا بادئة للشهر أو اليوم
- `latest` يعني إصدار npm المستقر المروَّج الحالي
- `beta` يعني هدف تثبيت beta الحالي
- تُنشر الإصدارات المستقرة وإصدارات التصحيح المستقرة إلى npm `beta` افتراضيًا؛ ويمكن لمشغّلي الإصدار الاستهداف إلى `latest` صراحةً، أو ترقية إصدار beta مُراجَع لاحقًا
- يشحن كل إصدار من OpenClaw حزمة npm وتطبيق macOS معًا

## وتيرة الإصدار

- تبدأ الإصدارات عبر beta أولًا
- لا يتبع stable إلا بعد التحقق من أحدث beta
- إن إجراء الإصدار المفصل، والموافقات، وبيانات الاعتماد، وملاحظات الاسترداد
  مخصصة للمشرفين فقط

## الفحص التمهيدي للإصدار

- شغّل `pnpm build && pnpm ui:build` قبل `pnpm release:check` حتى تتوفر
  عناصر الإصدار المتوقعة `dist/*` وحزمة Control UI لخطوة
  التحقق من الحزمة
- شغّل `pnpm release:check` قبل كل إصدار موسوم
- تُشغَّل فحوصات الإصدار الآن في workflow يدوي منفصل:
  `OpenClaw Release Checks`
- هذا الفصل مقصود: أبقِ مسار إصدار npm الفعلي قصيرًا
  وحتميًا ومركّزًا على العناصر الناتجة، بينما تبقى الفحوصات الحية الأبطأ في
  مسارها الخاص حتى لا تُبطئ النشر أو تمنعه
- يجب إرسال فحوصات الإصدار من مرجع workflow للفرع `main` حتى تبقى
  منطقية workflow والأسرار مرجعية
- تقبل تلك workflow إما وسم إصدار موجود أو قيمة SHA كاملة من 40 حرفًا
  لالتزام `main` الحالي
- في وضع SHA الخاص بالالتزام، لا تقبل إلا قيمة HEAD الحالية لـ `origin/main`؛ استخدم
  وسم إصدار للالتزامات الأقدم الخاصة بالإصدار
- كما يقبل الفحص التمهيدي للتحقق فقط لـ `OpenClaw NPM Release`
  قيمة SHA الكاملة الحالية من 40 حرفًا لالتزام `main` من دون اشتراط وسم مدفوع
- مسار SHA هذا مخصص للتحقق فقط ولا يمكن ترقيته إلى نشر فعلي
- في وضع SHA، تُولِّد workflow القيمة `v<package.json version>` فقط من أجل
  فحص بيانات تعريف الحزمة؛ أما النشر الفعلي فلا يزال يتطلب وسم إصدار فعلي
- تُبقي كلتا workflow مسار النشر والترقية الفعليين على GitHub-hosted
  runners، بينما يمكن لمسار التحقق غير المعدِّل استخدام
  Blacksmith Linux runners الأكبر
- تُشغّل تلك workflow الأمر
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  باستخدام سري workflow وهما `OPENAI_API_KEY` و`ANTHROPIC_API_KEY`
- لم يعد الفحص التمهيدي لإصدار npm ينتظر مسار فحوصات الإصدار المنفصل
- شغّل `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (أو وسم beta/التصحيح المطابق) قبل الموافقة
- بعد نشر npm، شغّل
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (أو إصدار beta/التصحيح المطابق) للتحقق من مسار تثبيت السجل المنشور
  في بادئة temp جديدة
- تستخدم أتمتة الإصدار لدى المشرفين الآن أسلوب الفحص التمهيدي ثم الترقية:
  - يجب أن يمر نشر npm الفعلي عبر `preflight_run_id` ناجح خاص بـ npm
  - تستخدم إصدارات npm المستقرة `beta` افتراضيًا
  - يمكن لإصدار npm المستقر الاستهداف إلى `latest` صراحةً عبر مدخل workflow
  - لا تزال ترقية npm المستقرة من `beta` إلى `latest` متاحة كوضع يدوي صريح على workflow الموثوقة `OpenClaw NPM Release`
  - لا يزال وضع الترقية هذا يحتاج إلى `NPM_TOKEN` صالح في بيئة `npm-release` لأن إدارة `dist-tag` في npm منفصلة عن النشر الموثوق
  - الإصدار العام لـ `macOS Release` مخصص للتحقق فقط
  - يجب أن يمر النشر الخاص الفعلي لـ mac عبر
    `preflight_run_id` و`validate_run_id` ناجحين للإصدار الخاص على mac
  - تقوم مسارات النشر الفعلية بترقية العناصر الناتجة المحضّرة بدلًا من إعادة بنائها مرة أخرى
- بالنسبة إلى إصدارات التصحيح المستقرة مثل `YYYY.M.D-N`، يتحقق برنامج ما بعد النشر أيضًا
  من مسار الترقية نفسه ضمن بادئة temp من `YYYY.M.D` إلى `YYYY.M.D-N`
  حتى لا تؤدي تصحيحات الإصدار بصمت إلى ترك التثبيتات العامة الأقدم على
  حمولة النسخة المستقرة الأساسية
- يفشل الفحص التمهيدي لإصدار npm بإغلاق كامل ما لم تتضمن tarball كلاً من
  `dist/control-ui/index.html` وحمولة غير فارغة ضمن `dist/control-ui/assets/`
  حتى لا نشحن مرة أخرى لوحة متصفح فارغة
- إذا كان عمل الإصدار قد لمس تخطيط CI أو manifests توقيتات الامتدادات أو
  مصفوفات اختبار الامتدادات، فأعد توليد ومراجعة
  مخرجات مصفوفة workflow `checks-node-extensions` المملوكة للمخطِّط من `.github/workflows/ci.yml`
  قبل الموافقة حتى لا تصف ملاحظات الإصدار تخطيط CI قديمًا
- يتضمن استعداد إصدار macOS المستقر أيضًا أسطح المُحدِّث:
  - يجب أن ينتهي إصدار GitHub مع الملفات المعبأة `.zip` و`.dmg` و`.dSYM.zip`
  - يجب أن يشير `appcast.xml` على `main` إلى ملف zip المستقر الجديد بعد النشر
  - يجب أن يحتفظ التطبيق المعبأ بمعرّف حزمة غير تصحيحي، وعنوان URL غير فارغ
    لتغذية Sparkle، وقيمة `CFBundleVersion` مساوية أو أعلى من حد Sparkle الأدنى
    المعتمد لذلك الإصدار

## مدخلات workflow الخاصة بـ NPM

تقبل `OpenClaw NPM Release` مدخلات يتحكم بها المشغّل:

- `tag`: وسم الإصدار المطلوب مثل `v2026.4.2` أو `v2026.4.2-1` أو
  `v2026.4.2-beta.1`؛ وعندما يكون `preflight_only=true` قد يكون أيضًا
  قيمة SHA الكاملة الحالية من 40 حرفًا لالتزام `main` من أجل فحص تمهيدي للتحقق فقط
- `preflight_only`: القيمة `true` للتحقق/البناء/الحزمة فقط، و`false` لمسار النشر الفعلي
- `preflight_run_id`: مطلوب في مسار النشر الفعلي حتى تعيد workflow استخدام tarball المحضّر من تشغيل الفحص التمهيدي الناجح
- `npm_dist_tag`: وسم npm الهدف لمسار النشر؛ والقيمة الافتراضية `beta`
- `promote_beta_to_latest`: القيمة `true` لتخطي النشر ونقل إصدار stable منشور مسبقًا من `beta` إلى `latest`

تقبل `OpenClaw Release Checks` هذه المدخلات التي يتحكم بها المشغّل:

- `ref`: وسم إصدار موجود أو قيمة SHA الكاملة الحالية من 40 حرفًا لالتزام `main`
  للتحقق

القواعد:

- يمكن لوسوم stable ووسوم التصحيح النشر إلى `beta` أو `latest`
- لا يمكن لوسوم beta التمهيدية النشر إلا إلى `beta`
- يُسمح بإدخال SHA الكامل للالتزام فقط عندما يكون `preflight_only=true`
- يتطلب وضع SHA الخاص بالالتزام في فحوصات الإصدار أيضًا HEAD الحالية لـ `origin/main`
- يجب أن يستخدم مسار النشر الفعلي نفس قيمة `npm_dist_tag` المستخدمة أثناء الفحص التمهيدي؛ وتتحقق workflow من تلك البيانات التعريفية قبل متابعة النشر
- يجب أن يستخدم وضع الترقية وسم stable أو تصحيح، و`preflight_only=false`،
  و`preflight_run_id` فارغًا، و`npm_dist_tag=beta`
- ويتطلب وضع الترقية أيضًا `NPM_TOKEN` صالحًا في بيئة `npm-release`
  لأن `npm dist-tag add` لا يزال يحتاج إلى مصادقة npm عادية

## تسلسل إصدار npm المستقر

عند قطع إصدار npm مستقر:

1. شغّل `OpenClaw NPM Release` مع `preflight_only=true`
   - قبل وجود وسم، يمكنك استخدام قيمة SHA الكاملة الحالية لالتزام `main` من أجل
     تشغيل تجريبي للتحقق فقط لمسار workflow الخاص بالفحص التمهيدي
2. اختر `npm_dist_tag=beta` لتدفق beta-first العادي، أو `latest` فقط
   عندما تريد عمدًا نشر stable مباشرًا
3. شغّل `OpenClaw Release Checks` بشكل منفصل باستخدام الوسم نفسه أو
   قيمة SHA الكاملة الحالية لـ `main` عندما تريد تغطية حيّة للتخزين المؤقت للموجّهات
   - وهذا منفصل عمدًا حتى تبقى التغطية الحية متاحة من دون
     إعادة ربط الفحوصات الطويلة أو غير المستقرة بـ workflow النشر
4. احفظ `preflight_run_id` الناجح
5. شغّل `OpenClaw NPM Release` مرة أخرى مع `preflight_only=false`، والقيمة نفسها
   لـ `tag`، والقيمة نفسها لـ `npm_dist_tag`، و`preflight_run_id` المحفوظ
6. إذا وصل الإصدار إلى `beta`، فشغّل `OpenClaw NPM Release` لاحقًا باستخدام
   وسم stable نفسه، و`promote_beta_to_latest=true`، و`preflight_only=false`،
   و`preflight_run_id` فارغًا، و`npm_dist_tag=beta` عندما تريد نقل ذلك
   الإصدار المنشور إلى `latest`

لا يزال وضع الترقية يتطلب موافقة بيئة `npm-release` ووجود
`NPM_TOKEN` صالح في تلك البيئة.

وهذا يُبقي كلاً من مسار النشر المباشر ومسار الترقية وفق beta-first
موثّقين ومرئيين للمشغّل.

## المراجع العامة

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

يستخدم المشرفون مستندات الإصدار الخاصة في
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
كدليل التشغيل الفعلي.
