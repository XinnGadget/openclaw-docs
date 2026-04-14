---
read_when:
    - أبحث عن تعريفات قنوات الإصدار العامة
    - أبحث عن تسمية الإصدارات والوتيرة
summary: قنوات الإصدار العامة، وتسمية الإصدارات، والوتيرة
title: سياسة الإصدار
x-i18n:
    generated_at: "2026-04-14T07:17:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3eaf9f1786b8c9fd4f5a9c657b623cb69d1a485958e1a9b8f108511839b63587
    source_path: reference/RELEASING.md
    workflow: 15
---

# سياسة الإصدار

لدى OpenClaw ثلاث مسارات إصدار عامة:

- stable: إصدارات موسومة تُنشر إلى npm `beta` افتراضيًا، أو إلى npm `latest` عند الطلب الصريح
- beta: وسوم إصدارات تمهيدية تُنشر إلى npm `beta`
- dev: الرأس المتحرك لفرع `main`

## تسمية الإصدارات

- إصدار الإصدار المستقر: `YYYY.M.D`
  - وسم Git: `vYYYY.M.D`
- إصدار تصحيح الإصدار المستقر: `YYYY.M.D-N`
  - وسم Git: `vYYYY.M.D-N`
- إصدار بيتا التمهيدي: `YYYY.M.D-beta.N`
  - وسم Git: `vYYYY.M.D-beta.N`
- لا تُضِف أصفارًا بادئة إلى الشهر أو اليوم
- `latest` يعني إصدار npm المستقر المُرقّى الحالي
- `beta` يعني هدف تثبيت بيتا الحالي
- تُنشر الإصدارات المستقرة وإصدارات التصحيح المستقرة إلى npm `beta` افتراضيًا؛ ويمكن لمشغّلي الإصدار استهداف `latest` صراحةً، أو ترقية بنية بيتا مُتحقَّق منها لاحقًا
- يشحن كل إصدار من OpenClaw حزمة npm وتطبيق macOS معًا

## وتيرة الإصدار

- تبدأ الإصدارات من beta أولًا
- لا يأتي stable إلا بعد التحقق من أحدث beta
- إجراء الإصدار التفصيلي، والموافقات، وبيانات الاعتماد، وملاحظات الاسترداد
  مخصّصة للمشرفين فقط

## التحقق المسبق للإصدار

- شغّل `pnpm build && pnpm ui:build` قبل `pnpm release:check` حتى تكون
  عناصر إصدار `dist/*` المتوقعة وحزمة Control UI موجودة من أجل
  خطوة التحقق من الحزمة
- شغّل `pnpm release:check` قبل كل إصدار موسوم
- تعمل الآن فحوصات الإصدار ضمن سير عمل يدوي منفصل:
  `OpenClaw Release Checks`
- هذا الفصل مقصود: إبقاء مسار إصدار npm الحقيقي قصيرًا،
  وحتميًا، ومركّزًا على العناصر، بينما تبقى الفحوصات الحية الأبطأ في
  مسارها الخاص حتى لا تؤخر النشر أو تمنعه
- يجب تشغيل فحوصات الإصدار من مرجع سير العمل `main` حتى تبقى
  منطقية سير العمل والأسرار معتمدة وموحدة
- يقبل سير العمل هذا إما وسم إصدار موجودًا أو SHA الكامل الحالي
  المكوّن من 40 حرفًا لالتزام `main`
- في وضع commit-SHA، لا يقبل إلا HEAD الحالي لـ `origin/main`؛ استخدم
  وسم إصدار للالتزامات الأقدم الخاصة بالإصدار
- يقبل التحقق المسبق للتحقق فقط في `OpenClaw NPM Release` أيضًا
  SHA الكامل الحالي المكوّن من 40 حرفًا لالتزام `main` من دون الحاجة إلى وسم مدفوع
- هذا المسار المعتمد على SHA مخصص للتحقق فقط ولا يمكن ترقيته إلى نشر حقيقي
- في وضع SHA، ينشئ سير العمل `v<package.json version>` فقط
  من أجل فحص بيانات تعريف الحزمة؛ ولا يزال النشر الحقيقي يتطلب وسم إصدار حقيقي
- يُبقي كلا سيرَي العمل مسار النشر والترقية الحقيقيين على مشغّلات GitHub المستضافة،
  بينما يمكن لمسار التحقق غير المُعدِّل استخدام مشغّلات
  Blacksmith Linux الأكبر
- يشغّل سير العمل هذا
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  باستخدام سريَي سير العمل `OPENAI_API_KEY` و`ANTHROPIC_API_KEY`
- لم يعد التحقق المسبق لإصدار npm ينتظر مسار فحوصات الإصدار المنفصل
- شغّل `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (أو وسم beta/التصحيح المطابق) قبل الموافقة
- بعد نشر npm، شغّل
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (أو إصدار beta/التصحيح المطابق) للتحقق من
  مسار التثبيت من السجل المنشور في بادئة temp جديدة
- تستخدم الآن أتمتة الإصدار الخاصة بالمشرفين أسلوب التحقق المسبق ثم الترقية:
  - يجب أن يمر نشر npm الحقيقي عبر `preflight_run_id` ناجح لـ npm
  - تُوجَّه إصدارات npm المستقرة إلى `beta` افتراضيًا
  - يمكن أن يستهدف نشر npm المستقر `latest` صراحةً عبر إدخال سير العمل
  - ما تزال ترقية npm المستقرة من `beta` إلى `latest` متاحة كوضع يدوي صريح ضمن سير العمل الموثوق `OpenClaw NPM Release`
  - يمكن أيضًا لعمليات النشر المستقرة المباشرة تشغيل وضع مزامنة `dist-tag` صريح
    يشير فيه كل من `latest` و`beta` إلى الإصدار المستقر المنشور بالفعل
  - ما تزال أوضاع `dist-tag` هذه تحتاج إلى `NPM_TOKEN` صالح في بيئة `npm-release` لأن إدارة npm `dist-tag` منفصلة عن النشر الموثوق
  - إصدار `macOS Release` العام مخصص للتحقق فقط
  - يجب أن يمر نشر mac الخاص الحقيقي والخاص عبر
    `preflight_run_id` و`validate_run_id` ناجحين لـ mac الخاص
  - تروّج مسارات النشر الحقيقية للعناصر المُحضّرة بدلًا من إعادة بنائها
    مرة أخرى
- بالنسبة إلى إصدارات التصحيح المستقرة مثل `YYYY.M.D-N`، يتحقق مُراجِع ما بعد النشر
  أيضًا من مسار الترقية نفسه في بادئة temp من `YYYY.M.D` إلى `YYYY.M.D-N`
  حتى لا تترك تصحيحات الإصدار بصمت عمليات التثبيت العالمية الأقدم على
  الحمولة الأساسية للإصدار المستقر
- يفشل التحقق المسبق لإصدار npm بشكل مغلق ما لم تتضمن الحزمة المضغوطة كلاً من
  `dist/control-ui/index.html` وحمولة غير فارغة ضمن `dist/control-ui/assets/`
  حتى لا نشحن مجددًا لوحة متصفح فارغة
- يفرض `pnpm test:install:smoke` أيضًا ميزانية `unpackedSize` الخاصة بحزمة npm
  على الحزمة المرشحة للتحديث، بحيث تلتقط اختبارات e2e الخاصة بالمثبّت تضخم الحزمة غير المقصود
  قبل مسار نشر الإصدار
- إذا كانت أعمال الإصدار قد مست تخطيط CI أو بيانات توقيت الإضافات أو
  مصفوفات اختبارات الإضافات، فأعِد توليد وراجِع
  مخرجات مصفوفة سير العمل `checks-node-extensions` المملوكة للمخطِّط من `.github/workflows/ci.yml`
  قبل الموافقة حتى لا تصف ملاحظات الإصدار تخطيط CI قديمًا
- تتضمن جاهزية إصدار macOS المستقر أيضًا أسطح أداة التحديث:
  - يجب أن ينتهي إصدار GitHub محتويًا على `.zip` و`.dmg` و`.dSYM.zip` المُعبأة
  - يجب أن يشير `appcast.xml` على `main` إلى ملف zip المستقر الجديد بعد النشر
  - يجب أن يحافظ التطبيق المُعبأ على معرّف حزمة غير تصحيحي، وURL غير فارغ
    لخلاصة Sparkle، و`CFBundleVersion` يساوي أو يفوق حد Sparkle الأدنى القياسي
    لإصدار ذلك الإصدار

## مُدخلات سير عمل NPM

يقبل `OpenClaw NPM Release` مُدخلات يتحكم بها المشغّل كما يلي:

- `tag`: وسم الإصدار المطلوب مثل `v2026.4.2` أو `v2026.4.2-1` أو
  `v2026.4.2-beta.1`؛ وعند `preflight_only=true`، يمكن أن يكون أيضًا
  SHA الكامل الحالي المكوّن من 40 حرفًا لالتزام `main` من أجل تحقق مسبق للتحقق فقط
- `preflight_only`: القيمة `true` للتحقق/البناء/الحزمة فقط، و`false` لمسار
  النشر الحقيقي
- `preflight_run_id`: مطلوب في مسار النشر الحقيقي حتى يعيد سير العمل استخدام
  الحزمة المضغوطة المُحضّرة من تشغيل التحقق المسبق الناجح
- `npm_dist_tag`: وسم npm الهدف لمسار النشر؛ والقيمة الافتراضية هي `beta`
- `promote_beta_to_latest`: القيمة `true` لتخطي النشر ونقل
  بنية `beta` مستقرة منشورة بالفعل إلى `latest`
- `sync_stable_dist_tags`: القيمة `true` لتخطي النشر وتوجيه كل من `latest` و
  `beta` إلى إصدار مستقر منشور بالفعل

يقبل `OpenClaw Release Checks` مُدخلات يتحكم بها المشغّل كما يلي:

- `ref`: وسم إصدار موجود أو SHA الكامل الحالي المكوّن من 40 حرفًا لالتزام `main`
  للتحقق

القواعد:

- يمكن لوسوم stable ووسوم التصحيح النشر إلى `beta` أو `latest`
- يمكن لوسوم beta التمهيدية النشر إلى `beta` فقط
- يُسمح بإدخال SHA الكامل للالتزام فقط عندما يكون `preflight_only=true`
- يتطلب وضع commit-SHA في فحوصات الإصدار أيضًا HEAD الحالي لـ `origin/main`
- يجب أن يستخدم مسار النشر الحقيقي القيمة نفسها لـ `npm_dist_tag` المستخدمة أثناء التحقق المسبق؛
  ويتحقق سير العمل من تلك البيانات التعريفية قبل متابعة النشر
- يجب أن يستخدم وضع الترقية وسم stable أو وسم تصحيح، و`preflight_only=false`،
  و`preflight_run_id` فارغًا، و`npm_dist_tag=beta`
- يجب أن يستخدم وضع مزامنة `dist-tag` وسم stable أو وسم تصحيح،
  و`preflight_only=false`، و`preflight_run_id` فارغًا، و`npm_dist_tag=latest`،
  و`promote_beta_to_latest=false`
- تتطلب أوضاع الترقية ومزامنة `dist-tag` أيضًا `NPM_TOKEN` صالحًا لأن
  `npm dist-tag add` ما يزال يحتاج إلى مصادقة npm العادية؛ أما النشر الموثوق
  فيغطي مسار نشر الحزمة فقط

## تسلسل إصدار npm المستقر

عند إصدار نسخة npm مستقرة:

1. شغّل `OpenClaw NPM Release` مع `preflight_only=true`
   - قبل وجود وسم، يمكنك استخدام SHA الكامل الحالي لالتزام `main` من أجل
     تشغيل جاف للتحقق فقط من سير عمل التحقق المسبق
2. اختر `npm_dist_tag=beta` للتدفق العادي الذي يبدأ بـ beta، أو `latest` فقط
   عندما تريد عمدًا نشر إصدار مستقر مباشر
3. شغّل `OpenClaw Release Checks` بشكل منفصل باستخدام الوسم نفسه أو
   SHA الكامل الحالي لـ `main` عندما تريد تغطية حية لذاكرة التخزين المؤقت للمطالبات
   - هذا فصل مقصود حتى تبقى التغطية الحية متاحة من دون
     إعادة ربط الفحوصات الطويلة أو غير المستقرة بسير عمل النشر
4. احفظ `preflight_run_id` الناجح
5. شغّل `OpenClaw NPM Release` مرة أخرى مع `preflight_only=false`، و`tag`
   نفسه، و`npm_dist_tag` نفسه، و`preflight_run_id` المحفوظ
6. إذا وصل الإصدار إلى `beta`، فشغّل `OpenClaw NPM Release` لاحقًا باستخدام
   وسم stable نفسه، و`promote_beta_to_latest=true`، و`preflight_only=false`،
   و`preflight_run_id` فارغًا، و`npm_dist_tag=beta` عندما تريد نقل ذلك
   الإصدار المنشور إلى `latest`
7. إذا نُشر الإصدار عمدًا مباشرةً إلى `latest` وكان يجب أن يتبع `beta`
   البنية المستقرة نفسها، فشغّل `OpenClaw NPM Release` باستخدام
   وسم stable نفسه، و`sync_stable_dist_tags=true`، و`promote_beta_to_latest=false`،
   و`preflight_only=false`، و`preflight_run_id` فارغًا، و`npm_dist_tag=latest`

ما تزال أوضاع الترقية ومزامنة `dist-tag` تتطلب موافقة بيئة `npm-release`
و`NPM_TOKEN` صالحًا يمكن لسير العمل هذا الوصول إليه.

هذا يُبقي كلاً من مسار النشر المباشر ومسار الترقية الذي يبدأ بـ beta
موثقين ومرئيين للمشغّل.

## مراجع عامة

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

يستخدم المشرفون مستندات الإصدار الخاصة في
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
كدليل التشغيل الفعلي.
