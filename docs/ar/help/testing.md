---
read_when:
    - تشغيل الاختبارات محليًا أو في CI
    - إضافة اختبارات تراجع لأخطاء النموذج/الموفر
    - تصحيح سلوك البوابة + الوكيل
summary: 'عدة الاختبار: أجنحة unit/e2e/live، ومشغلات Docker، وما الذي يغطيه كل اختبار'
title: الاختبار
x-i18n:
    generated_at: "2026-04-09T01:30:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 01117f41d8b171a4f1da11ed78486ee700e70ae70af54eb6060c57baf64ab21b
    source_path: help/testing.md
    workflow: 15
---

# الاختبار

يحتوي OpenClaw على ثلاثة أجنحة Vitest (unit/integration، وe2e، وlive) ومجموعة صغيرة من مشغلات Docker.

هذه الوثيقة هي دليل "كيف نختبر":

- ما الذي يغطيه كل جناح (وما الذي لا يغطيه عمدًا)
- ما الأوامر التي يجب تشغيلها في مسارات العمل الشائعة (محليًا، قبل الدفع، التصحيح)
- كيف تكتشف الاختبارات الحية بيانات الاعتماد وتختار النماذج/الموفرين
- كيف تضيف اختبارات تراجع لمشكلات النماذج/الموفرين في العالم الحقيقي

## البدء السريع

في معظم الأيام:

- البوابة الكاملة (متوقعة قبل الدفع): `pnpm build && pnpm check && pnpm test`
- تشغيل أسرع محليًا للجناح الكامل على جهاز واسع الموارد: `pnpm test:max`
- حلقة مراقبة Vitest مباشرة: `pnpm test:watch`
- استهداف الملفات مباشرة يوجّه الآن مسارات extensions/channel أيضًا: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- موقع QA مدعوم بـ Docker: `pnpm qa:lab:up`

عندما تلمس الاختبارات أو تريد ثقة إضافية:

- بوابة التغطية: `pnpm test:coverage`
- جناح E2E: `pnpm test:e2e`

عند تصحيح موفرين/نماذج حقيقية (يتطلب بيانات اعتماد حقيقية):

- الجناح الحي (مجسات النماذج + أدوات/صور البوابة): `pnpm test:live`
- استهدف ملفًا حيًا واحدًا بهدوء: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

نصيحة: عندما تحتاج فقط إلى حالة فاشلة واحدة، فالأفضل تضييق الاختبارات الحية باستخدام متغيرات البيئة allowlist الموضحة أدناه.

## أجنحة الاختبار (ما الذي يعمل وأين)

فكّر في الأجنحة على أنها "واقعية متزايدة" (ومعها قابلية فشل/تكلفة متزايدة):

### Unit / integration (الافتراضي)

- الأمر: `pnpm test`
- الإعداد: عشر تشغيلات shards متسلسلة (`vitest.full-*.config.ts`) فوق مشاريع Vitest المقيّدة الحالية
- الملفات: مخزونات core/unit تحت `src/**/*.test.ts` و`packages/**/*.test.ts` و`test/**/*.test.ts` واختبارات `ui` المعتمدة على node والمسموح بها والمغطاة بواسطة `vitest.unit.config.ts`
- النطاق:
  - اختبارات unit خالصة
  - اختبارات integration داخل العملية (مصادقة البوابة، والتوجيه، والأدوات، والتحليل، والإعداد)
  - اختبارات تراجع حتمية للأخطاء المعروفة
- التوقعات:
  - تعمل في CI
  - لا تتطلب مفاتيح حقيقية
  - يجب أن تكون سريعة ومستقرة
- ملاحظة المشاريع:
  - أصبح `pnpm test` غير المستهدف الآن يشغّل أحد عشر إعداد shard أصغر (`core-unit-src` و`core-unit-security` و`core-unit-ui` و`core-unit-support` و`core-support-boundary` و`core-contracts` و`core-bundled` و`core-runtime` و`agentic` و`auto-reply` و`extensions`) بدلًا من عملية root-project أصلية واحدة ضخمة. يقلل هذا من ذروة RSS على الأجهزة المزدحمة ويتجنب أن تستنزف أعمال auto-reply/extension الأجنحة غير المرتبطة.
  - يظل `pnpm test --watch` يستخدم مخطط المشروع الأصلي في الجذر `vitest.config.ts`، لأن حلقة مراقبة متعددة الـ shards غير عملية.
  - تقوم `pnpm test` و`pnpm test:watch` و`pnpm test:perf:imports` بتوجيه أهداف الملفات/الأدلة الصريحة عبر المسارات المقيّدة أولًا، لذلك فإن `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` يتجنب كلفة بدء تشغيل مشروع الجذر الكامل.
  - يوسّع `pnpm test:changed` مسارات git المتغيرة إلى المسارات المقيّدة نفسها عندما يلمس diff فقط ملفات المصدر/الاختبار القابلة للتوجيه؛ أما تعديلات config/setup فتعيد المسار إلى إعادة تشغيل مشروع الجذر الواسعة.
  - يتم أيضًا توجيه اختبارات `plugin-sdk` و`commands` المحددة عبر مسارات خفيفة مخصصة تتجاوز `test/setup-openclaw-runtime.ts`؛ وتبقى الملفات الثقيلة من حيث الحالة/وقت التشغيل على المسارات الحالية.
  - كما تُطابق ملفات المصدر المساعدة المحددة في `plugin-sdk` و`commands` تشغيلات وضع changed مع اختبارات شقيقة صريحة في تلك المسارات الخفيفة، بحيث تتجنب تعديلات المساعدين إعادة تشغيل الجناح الثقيل الكامل لذلك الدليل.
  - يحتوي `auto-reply` الآن على ثلاثة أقسام مخصصة: مساعدات core من المستوى الأعلى، واختبارات integration من المستوى الأعلى `reply.*`، والشجرة الفرعية `src/auto-reply/reply/**`. يحافظ هذا على أعمال harness الأثقل للرد بعيدًا عن اختبارات الحالة/القطع/token الأرخص.
- ملاحظة المشغل المضمّن:
  - عندما تغيّر مدخلات اكتشاف message-tool أو سياق وقت تشغيل compaction،
    حافظ على مستويي التغطية معًا.
  - أضف اختبارات تراجع مركزة للمساعدات لحدود التوجيه/التطبيع الخالصة.
  - وحافظ أيضًا على صحة أجنحة integration للمشغل المضمّن:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`،
    و`src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`، و
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - تتحقق هذه الأجنحة من أن المعرّفات المقيّدة وسلوك compaction ما زالا يمران
    عبر المسارات الحقيقية `run.ts` / `compact.ts`؛ ولا تُعد اختبارات المساعدات فقط
    بديلًا كافيًا عن مسارات integration هذه.
- ملاحظة الـ pool:
  - أصبح إعداد Vitest الأساسي يفترض `threads`.
  - كما يثبت إعداد Vitest المشترك `isolate: false` ويستخدم المشغّل غير المعزول عبر مشاريع الجذر وإعدادات e2e وlive.
  - يحتفظ مسار UI في الجذر بإعداد `jsdom` والمُحسِّن الخاص به، لكنه يعمل الآن أيضًا على المشغّل المشترك غير المعزول.
  - يرث كل shard في `pnpm test` القيم الافتراضية نفسها `threads` + `isolate: false` من إعداد Vitest المشترك.
  - يضيف مشغّل `scripts/run-vitest.mjs` المشترك الآن أيضًا `--no-maglev` افتراضيًا إلى عمليات Node الفرعية الخاصة بـ Vitest لتقليل تقلبات ترجمة V8 أثناء التشغيلات المحلية الكبيرة. عيّن `OPENCLAW_VITEST_ENABLE_MAGLEV=1` إذا كنت تحتاج إلى المقارنة مع سلوك V8 القياسي.
- ملاحظة التكرار المحلي السريع:
  - يوجّه `pnpm test:changed` عبر المسارات المقيّدة عندما تُطابق المسارات المتغيرة جناحًا أصغر بشكل واضح.
  - يحتفظ `pnpm test:max` و`pnpm test:changed:max` بسلوك التوجيه نفسه، ولكن مع حد أعلى أكبر للعمّال.
  - أصبح توسيع العمّال المحلي التلقائي محافظًا عمدًا الآن كما أنه يتراجع عندما يكون متوسط حمل المضيف مرتفعًا بالفعل، بحيث تُحدث تشغيلات Vitest المتزامنة المتعددة ضررًا أقل افتراضيًا.
  - يعلّم إعداد Vitest الأساسي ملفات projects/config على أنها `forceRerunTriggers` حتى تظل إعادة التشغيل في وضع changed صحيحة عندما يتغير توصيل الاختبارات.
  - يحافظ الإعداد على تفعيل `OPENCLAW_VITEST_FS_MODULE_CACHE` على المضيفين المدعومين؛ عيّن `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` إذا كنت تريد موقع cache صريحًا واحدًا لأغراض التحليل المباشر.
- ملاحظة تصحيح الأداء:
  - يفعّل `pnpm test:perf:imports` تقارير مدة الاستيراد في Vitest بالإضافة إلى مخرجات تفصيل الاستيراد.
  - يقيّد `pnpm test:perf:imports:changed` طريقة العرض التحليلية نفسها بالملفات المتغيرة منذ `origin/main`.
- يقارن `pnpm test:perf:changed:bench -- --ref <git-ref>` بين `test:changed` الموجّه والمسار الأصلي لمشروع الجذر لذلك diff الملتزم ويطبع زمن التنفيذ بالإضافة إلى أقصى RSS على macOS.
- يضع `pnpm test:perf:changed:bench -- --worktree` معيارًا للشجرة المتسخة الحالية عبر توجيه قائمة الملفات المتغيرة من خلال `scripts/test-projects.mjs` وإعداد Vitest الجذري.
  - يكتب `pnpm test:perf:profile:main` ملف تعريف CPU للخيط الرئيسي لتكاليف بدء تشغيل Vitest/Vite والتحويل.
  - يكتب `pnpm test:perf:profile:runner` ملفات تعريف CPU+heap للمشغّل لجناح unit مع تعطيل التوازي على مستوى الملفات.

### E2E (اختبار دخان البوابة)

- الأمر: `pnpm test:e2e`
- الإعداد: `vitest.e2e.config.ts`
- الملفات: `src/**/*.e2e.test.ts` و`test/**/*.e2e.test.ts`
- افتراضيات وقت التشغيل:
  - يستخدم Vitest `threads` مع `isolate: false` بما يطابق بقية المستودع.
  - يستخدم عمّالًا تكيّفيين (CI: حتى 2، محليًا: 1 افتراضيًا).
  - يعمل في الوضع الصامت افتراضيًا لتقليل كلفة I/O في وحدة التحكم.
- تجاوزات مفيدة:
  - `OPENCLAW_E2E_WORKERS=<n>` لفرض عدد العمّال (بحد أقصى 16).
  - `OPENCLAW_E2E_VERBOSE=1` لإعادة تفعيل مخرجات وحدة التحكم المفصلة.
- النطاق:
  - سلوك البوابة متعددة المثيلات من طرف إلى طرف
  - أسطح WebSocket/HTTP، واقتران العقد، والشبكات الأثقل
- التوقعات:
  - تعمل في CI (عند تفعيلها في المسار)
  - لا تتطلب مفاتيح حقيقية
  - تحتوي على أجزاء متحركة أكثر من اختبارات unit (وقد تكون أبطأ)

### E2E: اختبار دخان الواجهة الخلفية OpenShell

- الأمر: `pnpm test:e2e:openshell`
- الملف: `test/openshell-sandbox.e2e.test.ts`
- النطاق:
  - يبدأ بوابة OpenShell معزولة على المضيف عبر Docker
  - ينشئ sandbox من Dockerfile محلي مؤقت
  - يختبر الواجهة الخلفية OpenShell الخاصة بـ OpenClaw عبر `sandbox ssh-config` + تنفيذ SSH الحقيقي
  - يتحقق من سلوك نظام الملفات canonical عن بُعد عبر جسر fs الخاص بـ sandbox
- التوقعات:
  - يعمل فقط عند الاشتراك؛ وليس جزءًا من تشغيل `pnpm test:e2e` الافتراضي
  - يتطلب CLI محليًا باسم `openshell` بالإضافة إلى daemon Docker يعمل
  - يستخدم `HOME` / `XDG_CONFIG_HOME` معزولين، ثم يدمر بوابة الاختبار وsandbox
- تجاوزات مفيدة:
  - `OPENCLAW_E2E_OPENSHELL=1` لتفعيل الاختبار عند تشغيل جناح e2e الأوسع يدويًا
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell` للإشارة إلى binary CLI غير افتراضي أو wrapper script

### Live (موفرون حقيقيون + نماذج حقيقية)

- الأمر: `pnpm test:live`
- الإعداد: `vitest.live.config.ts`
- الملفات: `src/**/*.live.test.ts`
- الافتراضي: **مفعّل** بواسطة `pnpm test:live` (يضبط `OPENCLAW_LIVE_TEST=1`)
- النطاق:
  - "هل يعمل هذا الموفر/النموذج بالفعل _اليوم_ باستخدام بيانات اعتماد حقيقية؟"
  - التقاط تغيّرات تنسيق الموفر، ومراوغات استدعاء الأدوات، ومشكلات المصادقة، وسلوك حدود المعدل
- التوقعات:
  - غير مستقرة بطبيعتها في CI (شبكات حقيقية، وسياسات موفرين حقيقية، وحصص، وانقطاعات)
  - تكلّف مالًا / تستهلك حدود المعدل
  - يُفضَّل تشغيل مجموعات فرعية مضيقة بدلًا من "كل شيء"
- تستورد التشغيلات الحية `~/.profile` لالتقاط مفاتيح API الناقصة.
- افتراضيًا، تظل التشغيلات الحية تعزل `HOME` وتنسخ مواد config/auth إلى home اختباري مؤقت حتى لا تتمكن fixtures الخاصة بـ unit من تعديل `~/.openclaw` الحقيقي لديك.
- اضبط `OPENCLAW_LIVE_USE_REAL_HOME=1` فقط عندما تحتاج عمدًا إلى أن تستخدم الاختبارات الحية دليل home الحقيقي لديك.
- أصبح `pnpm test:live` افتراضيًا الآن في وضع أكثر هدوءًا: فهو يبقي مخرجات التقدم `[live] ...`، لكنه يخفي إشعار `~/.profile` الإضافي ويكتم سجلات إقلاع البوابة/ضوضاء Bonjour. اضبط `OPENCLAW_LIVE_TEST_QUIET=0` إذا أردت عودة سجلات البدء الكاملة.
- تدوير مفاتيح API (حسب الموفر): اضبط `*_API_KEYS` بصيغة فاصلة/فاصلة منقوطة أو `*_API_KEY_1` و`*_API_KEY_2` (مثل `OPENAI_API_KEYS` و`ANTHROPIC_API_KEYS` و`GEMINI_API_KEYS`) أو تجاوزًا لكل live عبر `OPENCLAW_LIVE_*_KEY`؛ وتُعاد محاولة الاختبارات عند ردود rate limit.
- مخرجات التقدم/النبض:
  - تصدر الأجنحة الحية الآن أسطر التقدم إلى stderr بحيث تظهر الاستدعاءات الطويلة للموفر كأنها نشطة حتى عندما يكون التقاط وحدة التحكم في Vitest هادئًا.
  - يعطل `vitest.live.config.ts` اعتراض Vitest لوحدة التحكم بحيث تتدفق أسطر تقدم الموفر/البوابة مباشرة أثناء التشغيلات الحية.
  - اضبط نبضات direct-model باستخدام `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - اضبط نبضات gateway/probe باستخدام `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## أي جناح يجب أن أشغّل؟

استخدم جدول القرار هذا:

- تعديل المنطق/الاختبارات: شغّل `pnpm test` (و`pnpm test:coverage` إذا غيّرت الكثير)
- لمس شبكات البوابة / بروتوكول WS / الاقتران: أضف `pnpm test:e2e`
- تصحيح "البوت الخاص بي متوقف" / أعطال خاصة بالموفر / استدعاء الأدوات: شغّل `pnpm test:live` مضيّقًا

## Live: مسح قدرات عقدة Android

- الاختبار: `src/gateway/android-node.capabilities.live.test.ts`
- السكربت: `pnpm android:test:integration`
- الهدف: استدعاء **كل أمر معلن عنه حاليًا** من عقدة Android متصلة والتحقق من سلوك عقد الأوامر.
- النطاق:
  - إعداد مسبق/يدوي (الجناح لا يثبت التطبيق ولا يشغّله ولا يقرنه).
  - تحقق `node.invoke` في البوابة أمرًا بأمر لعقدة Android المحددة.
- الإعداد المسبق المطلوب:
  - تطبيق Android متصل ومقترن بالبوابة بالفعل.
  - إبقاء التطبيق في الواجهة الأمامية.
  - منح الأذونات/الموافقة على الالتقاط للقدرات التي تتوقع نجاحها.
- تجاوزات الهدف الاختيارية:
  - `OPENCLAW_ANDROID_NODE_ID` أو `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- تفاصيل إعداد Android الكاملة: [Android App](/ar/platforms/android)

## Live: اختبار دخان النماذج (مفاتيح profiles)

تنقسم الاختبارات الحية إلى طبقتين حتى نتمكن من عزل الأعطال:

- يوضح "النموذج المباشر" أن الموفر/النموذج قادر على الاستجابة أصلًا بالمفتاح المعطى.
- يوضح "اختبار دخان البوابة" أن مسار البوابة+الوكيل الكامل يعمل لذلك النموذج (الجلسات، السجل، الأدوات، سياسة sandbox، إلخ).

### الطبقة 1: إكمال النموذج المباشر (بدون بوابة)

- الاختبار: `src/agents/models.profiles.live.test.ts`
- الهدف:
  - تعداد النماذج المكتشفة
  - استخدام `getApiKeyForModel` لاختيار النماذج التي لديك بيانات اعتماد لها
  - تشغيل إكمال صغير لكل نموذج (واختبارات تراجع مستهدفة عند الحاجة)
- كيفية التفعيل:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` إذا كنت تستدعي Vitest مباشرة)
- اضبط `OPENCLAW_LIVE_MODELS=modern` (أو `all`، وهو اسم بديل لـ modern) لتشغيل هذا الجناح فعليًا؛ وإلا فسيتخطاه للحفاظ على تركيز `pnpm test:live` على اختبار دخان البوابة
- كيفية اختيار النماذج:
  - `OPENCLAW_LIVE_MODELS=modern` لتشغيل allowlist الحديثة (Opus/Sonnet 4.6+، وGPT-5.x + Codex، وGemini 3، وGLM 4.7، وMiniMax M2.7، وGrok 4)
  - `OPENCLAW_LIVE_MODELS=all` هو اسم بديل لـ allowlist الحديثة
  - أو `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (allowlist مفصولة بفواصل)
  - تفترض مسوح modern/all حدًا عالي الإشارة مُنتقى؛ اضبط `OPENCLAW_LIVE_MAX_MODELS=0` لمسح modern شامل أو رقمًا موجبًا لحد أصغر.
- كيفية اختيار الموفّرين:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (allowlist مفصولة بفواصل)
- من أين تأتي المفاتيح:
  - افتراضيًا: من مخزن profiles وبدائل env
  - اضبط `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض **مخزن profiles** فقط
- سبب وجود هذا:
  - يفصل بين "واجهة API الخاصة بالموفر معطلة / المفتاح غير صالح" و"مسار وكيل البوابة معطل"
  - يحتوي اختبارات تراجع صغيرة ومعزولة (مثال: مسارات reasoning replay + tool-call الخاصة بـ OpenAI Responses/Codex Responses)

### الطبقة 2: اختبار دخان البوابة + وكيل dev (ما الذي يفعله "@openclaw" فعليًا)

- الاختبار: `src/gateway/gateway-models.profiles.live.test.ts`
- الهدف:
  - تشغيل بوابة داخل العملية
  - إنشاء/ترقيع جلسة `agent:dev:*` (مع تجاوز النموذج لكل تشغيل)
  - التكرار عبر النماذج ذات المفاتيح والتحقق من:
    - استجابة "ذات معنى" (من دون أدوات)
    - نجاح استدعاء أداة حقيقي (مجس read)
    - مجسات أدوات إضافية اختيارية (مجس exec+read)
    - استمرار عمل مسارات تراجع OpenAI (tool-call-only → follow-up)
- تفاصيل المجسات (حتى تتمكن من شرح الأعطال بسرعة):
  - مجس `read`: يكتب الاختبار ملف nonce في مساحة العمل ويطلب من الوكيل `read` له وإرجاع nonce.
  - مجس `exec+read`: يطلب الاختبار من الوكيل كتابة nonce إلى ملف مؤقت عبر `exec` ثم `read` له مرة أخرى.
  - مجس الصورة: يرفق الاختبار PNG مولّدًا (قط + رمز عشوائي) ويتوقع من النموذج أن يعيد `cat <CODE>`.
  - مرجع التنفيذ: `src/gateway/gateway-models.profiles.live.test.ts` و`src/gateway/live-image-probe.ts`.
- كيفية التفعيل:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` إذا كنت تستدعي Vitest مباشرة)
- كيفية اختيار النماذج:
  - الافتراضي: allowlist الحديثة (Opus/Sonnet 4.6+، وGPT-5.x + Codex، وGemini 3، وGLM 4.7، وMiniMax M2.7، وGrok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` هو اسم بديل لـ allowlist الحديثة
  - أو اضبط `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (أو قائمة مفصولة بفواصل) للتضييق
  - تفترض مسوح gateway الحديثة/الكلية حدًا عالي الإشارة مُنتقى؛ اضبط `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0` لمسح حديث شامل أو رقمًا موجبًا لحد أصغر.
- كيفية اختيار الموفّرين (تجنب "كل ما في OpenRouter"):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (allowlist مفصولة بفواصل)
- تكون مجسات الأدوات + الصور مفعّلة دائمًا في هذا الاختبار الحي:
  - مجس `read` + مجس `exec+read` (ضغط الأدوات)
  - يعمل مجس الصورة عندما يعلن النموذج دعم إدخال الصور
  - التدفق (على مستوى عالٍ):
    - يولّد الاختبار PNG صغيرًا مع "CAT" + رمز عشوائي (`src/gateway/live-image-probe.ts`)
    - يرسله عبر `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - تحلل البوابة المرفقات إلى `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - يمرر الوكيل المضمّن رسالة مستخدم متعددة الوسائط إلى النموذج
    - التحقق: تحتوي الاستجابة على `cat` + الرمز (مع سماحية OCR: أخطاء طفيفة مسموح بها)

نصيحة: لمعرفة ما يمكنك اختباره على جهازك (ومعرفات `provider/model` الدقيقة)، شغّل:

```bash
openclaw models list
openclaw models list --json
```

## Live: اختبار دخان الواجهة الخلفية CLI (Claude أو Codex أو Gemini أو CLIs محلية أخرى)

- الاختبار: `src/gateway/gateway-cli-backend.live.test.ts`
- الهدف: التحقق من مسار Gateway + agent باستخدام واجهة خلفية CLI محلية، من دون لمس config الافتراضي لديك.
- تعيش افتراضيات اختبار الدخان الخاصة بكل واجهة خلفية داخل تعريف `cli-backend.ts` للإضافة المالكة.
- التفعيل:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` إذا كنت تستدعي Vitest مباشرة)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- الافتراضيات:
  - الموفر/النموذج الافتراضي: `claude-cli/claude-sonnet-4-6`
  - يأتي سلوك command/args/image من metadata الخاصة بالإضافة المالكة للواجهة الخلفية CLI.
- التجاوزات (اختيارية):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` لإرسال مرفق صورة حقيقي (يتم حقن المسارات في prompt).
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` لتمرير مسارات ملفات الصور كوسائط CLI بدلًا من حقنها في prompt.
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (أو `"list"`) للتحكم في كيفية تمرير وسائط الصور عندما يكون `IMAGE_ARG` مضبوطًا.
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` لإرسال دورة ثانية والتحقق من تدفق الاستئناف.
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0` لتعطيل مجس الاستمرارية الافتراضي في الجلسة نفسها Claude Sonnet -> Opus (اضبطه على `1` لفرض تشغيله عندما يدعم النموذج المحدد هدف تبديل).

مثال:

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

وصفة Docker:

```bash
pnpm test:docker:live-cli-backend
```

وصفات Docker لموفر واحد:

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

ملاحظات:

- يوجد مشغّل Docker في `scripts/test-live-cli-backend-docker.sh`.
- يشغّل اختبار دخان الواجهة الخلفية CLI الحي داخل صورة Docker الخاصة بالمستودع بصفته المستخدم غير الجذر `node`.
- يحل metadata الخاصة باختبار دخان CLI من الإضافة المالكة، ثم يثبت حزمة Linux CLI المطابقة (`@anthropic-ai/claude-code` أو `@openai/codex` أو `@google/gemini-cli`) في prefix قابل للكتابة ومخزّن مؤقتًا عند `OPENCLAW_DOCKER_CLI_TOOLS_DIR` (الافتراضي: `~/.cache/openclaw/docker-cli-tools`).
- يختبر اختبار دخان الواجهة الخلفية CLI الحي الآن التدفق الكامل نفسه من طرف إلى طرف لكل من Claude وCodex وGemini: دورة نصية، ثم دورة تصنيف صورة، ثم استدعاء أداة MCP `cron` يتم التحقق منه عبر CLI البوابة.
- يقوم اختبار الدخان الافتراضي لـ Claude أيضًا بترقيع الجلسة من Sonnet إلى Opus ويتحقق من أن الجلسة المستأنفة ما زالت تتذكر ملاحظة سابقة.

## Live: اختبار دخان ربط ACP (`/acp spawn ... --bind here`)

- الاختبار: `src/gateway/gateway-acp-bind.live.test.ts`
- الهدف: التحقق من تدفق ربط المحادثة ACP الحقيقي مع وكيل ACP حي:
  - إرسال `/acp spawn <agent> --bind here`
  - ربط محادثة قناة رسائل تركيبية في مكانها
  - إرسال متابعة عادية على تلك المحادثة نفسها
  - التحقق من أن المتابعة تصل إلى transcript الجلسة ACP المرتبطة
- التفعيل:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- الافتراضيات:
  - وكلاء ACP في Docker: `claude,codex,gemini`
  - وكيل ACP للتشغيل المباشر `pnpm test:live ...`: `claude`
  - القناة التركيبية: سياق محادثة بنمط Slack DM
  - الواجهة الخلفية ACP: `acpx`
- التجاوزات:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- ملاحظات:
  - يستخدم هذا المسار سطح البوابة `chat.send` مع حقول originating-route تركيبية خاصة بالمشرف فقط حتى تتمكن الاختبارات من إرفاق سياق قناة الرسائل من دون التظاهر بالتسليم الخارجي.
  - عندما لا يكون `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` مضبوطًا، يستخدم الاختبار سجل الوكلاء المضمّن في إضافة `acpx` لاختيار وكيل harness ACP المحدد.

مثال:

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

وصفة Docker:

```bash
pnpm test:docker:live-acp-bind
```

وصفات Docker لوكيل واحد:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

ملاحظات Docker:

- يوجد مشغّل Docker في `scripts/test-live-acp-bind-docker.sh`.
- يشغّل افتراضيًا اختبار دخان ربط ACP ضد جميع وكلاء CLI الحية المدعومة بالتسلسل: `claude` ثم `codex` ثم `gemini`.
- استخدم `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude` أو `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` أو `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` لتضييق المصفوفة.
- يستورد `~/.profile`، ويجهز مواد مصادقة CLI المطابقة داخل الحاوية، ويثبت `acpx` في prefix npm قابل للكتابة، ثم يثبت CLI الحي المطلوب (`@anthropic-ai/claude-code` أو `@openai/codex` أو `@google/gemini-cli`) إذا كان مفقودًا.
- داخل Docker، يضبط المشغّل `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` حتى يحتفظ acpx بمتغيرات بيئة الموفر من profile المستوردة والمتاحة لـ CLI harness الابن.

### وصفات live الموصى بها

تكون allowlists الضيقة والصريحة الأسرع والأقل تعرّضًا للفشل:

- نموذج واحد، مباشر (بدون بوابة):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- نموذج واحد، اختبار دخان البوابة:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- استدعاء الأدوات عبر عدة موفرين:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- تركيز Google (مفتاح Gemini API + Antigravity):
  - Gemini (مفتاح API): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

ملاحظات:

- يستخدم `google/...` واجهة Gemini API (مفتاح API).
- يستخدم `google-antigravity/...` جسر Antigravity OAuth (نقطة نهاية وكيل بنمط Cloud Code Assist).
- يستخدم `google-gemini-cli/...` Gemini CLI المحلي على جهازك (مصادقة منفصلة ومراوغات أدوات منفصلة).
- Gemini API مقابل Gemini CLI:
  - API: يستدعي OpenClaw Gemini API المستضافة من Google عبر HTTP (مفتاح API / مصادقة profile)؛ وهذا ما يعنيه معظم المستخدمين عندما يقولون "Gemini".
  - CLI: يقوم OpenClaw بتنفيذ binary محلي باسم `gemini`؛ وله مصادقة خاصة به وقد يتصرف بشكل مختلف (streaming/دعم الأدوات/اختلاف الإصدار).

## Live: مصفوفة النماذج (ما الذي نغطيه)

لا توجد "قائمة نماذج CI" ثابتة (live اختيارية)، لكن هذه هي النماذج **الموصى بها** للتغطية بانتظام على جهاز تطوير مع مفاتيح.

### مجموعة الدخان الحديثة (استدعاء الأدوات + الصور)

هذا هو تشغيل "النماذج الشائعة" الذي نتوقع أن يظل يعمل:

- OpenAI (غير Codex): `openai/gpt-5.4` (اختياري: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (أو `anthropic/claude-sonnet-4-6`)
- Google (Gemini API): `google/gemini-3.1-pro-preview` و`google/gemini-3-flash-preview` (تجنب نماذج Gemini 2.x الأقدم)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` و`google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

شغّل اختبار دخان البوابة مع الأدوات + الصور:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### الأساس: استدعاء الأدوات (Read + Exec اختياري)

اختر على الأقل واحدًا من كل عائلة موفرين:

- OpenAI: `openai/gpt-5.4` (أو `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (أو `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (أو `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

تغطية إضافية اختيارية (من الجيد وجودها):

- xAI: `xai/grok-4` (أو أحدث ما هو متاح)
- Mistral: `mistral/`… (اختر نموذجًا واحدًا يدعم "tools" لديك مفعّل)
- Cerebras: `cerebras/`… (إذا كان لديك وصول)
- LM Studio: `lmstudio/`… (محلي؛ يعتمد استدعاء الأدوات على وضع API)

### الرؤية: إرسال الصور (مرفق → رسالة متعددة الوسائط)

ضمّن نموذجًا واحدًا على الأقل يدعم الصور في `OPENCLAW_LIVE_GATEWAY_MODELS` (إصدارات Claude/Gemini/OpenAI القادرة على الرؤية، إلخ) لتفعيل مجس الصورة.

### المجمعات / البوابات البديلة

إذا كانت لديك مفاتيح مفعلة، فنحن ندعم أيضًا الاختبار عبر:

- OpenRouter: `openrouter/...` (مئات النماذج؛ استخدم `openclaw models scan` للعثور على مرشحين يدعمون tools+image)
- OpenCode: `opencode/...` لـ Zen و`opencode-go/...` لـ Go (المصادقة عبر `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

موفرون إضافيون يمكنك تضمينهم في مصفوفة live (إذا كانت لديك بيانات اعتماد/config):

- مدمجة: `openai` و`openai-codex` و`anthropic` و`google` و`google-vertex` و`google-antigravity` و`google-gemini-cli` و`zai` و`openrouter` و`opencode` و`opencode-go` و`xai` و`groq` و`cerebras` و`mistral` و`github-copilot`
- عبر `models.providers` (نقاط نهاية مخصصة): `minimax` (سحابي/API)، بالإضافة إلى أي proxy متوافق مع OpenAI/Anthropic (LM Studio أو vLLM أو LiteLLM، إلخ)

نصيحة: لا تحاول ترميز "كل النماذج" بشكل ثابت في الوثائق. القائمة الموثوقة هي ما تُرجعه `discoverModels(...)` على جهازك + أي مفاتيح متاحة.

## بيانات الاعتماد (لا تُلتزم أبدًا)

تكتشف الاختبارات الحية بيانات الاعتماد بالطريقة نفسها التي يفعلها CLI. وتترتب على ذلك آثار عملية:

- إذا كان CLI يعمل، فيجب أن تجد الاختبارات الحية المفاتيح نفسها.
- إذا قال اختبار حي "لا توجد بيانات اعتماد"، فقم بالتصحيح بالطريقة نفسها التي ستصحح بها `openclaw models list` / اختيار النموذج.

- ملفات auth profile لكل وكيل: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (وهذا هو المقصود بـ "profile keys" في الاختبارات الحية)
- الإعداد: `~/.openclaw/openclaw.json` (أو `OPENCLAW_CONFIG_PATH`)
- دليل الحالة القديم: `~/.openclaw/credentials/` (يُنسخ إلى home الحي المرحلي عندما يكون موجودًا، لكنه ليس مخزن مفاتيح profile الرئيسي)
- تنسخ التشغيلات الحية المحلية افتراضيًا الإعداد النشط وملفات `auth-profiles.json` لكل وكيل و`credentials/` القديمة وأدلة مصادقة CLI الخارجية المدعومة إلى home اختباري مؤقت؛ وتتخطى homes الحية المرحلية `workspace/` و`sandboxes/`، وتُزال تجاوزات المسار `agents.*.workspace` / `agentDir` حتى تبقى المجسات بعيدة عن مساحة العمل الحقيقية على مضيفك.

إذا كنت تريد الاعتماد على مفاتيح env (مثلًا المصدّرة في `~/.profile`)، فشغّل الاختبارات المحلية بعد `source ~/.profile`، أو استخدم مشغلات Docker أدناه (يمكنها ربط `~/.profile` بالحاوية).

## Deepgram live (نسخ صوتي)

- الاختبار: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- التفعيل: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- الاختبار: `src/agents/byteplus.live.test.ts`
- التفعيل: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- تجاوز اختياري للنموذج: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow media live

- الاختبار: `extensions/comfy/comfy.live.test.ts`
- التفعيل: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- النطاق:
  - يختبر مسارات الصورة والفيديو و`music_generate` المدمجة الخاصة بـ comfy
  - يتخطى كل قدرة ما لم تكن `models.providers.comfy.<capability>` مضبوطة
  - مفيد بعد تغيير إرسال workflow الخاص بـ comfy أو polling أو التنزيلات أو تسجيل الإضافة

## Image generation live

- الاختبار: `src/image-generation/runtime.live.test.ts`
- الأمر: `pnpm test:live src/image-generation/runtime.live.test.ts`
- الـ harness: `pnpm test:live:media image`
- النطاق:
  - يعدد كل إضافة موفر لتوليد الصور مسجلة
  - يحمّل متغيرات env الناقصة للموفر من shell تسجيل الدخول لديك (`~/.profile`) قبل المجسات
  - يستخدم مفاتيح API الحية/من env قبل profiles المخزنة للمصادقة افتراضيًا، حتى لا تُخفي مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات اعتماد shell الحقيقية
  - يتخطى الموفّرين الذين لا يملكون مصادقة/ profile / نموذجًا صالحًا
  - يشغّل متغيرات توليد الصور الافتراضية عبر قدرة runtime المشتركة:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- الموفّرون المدمجون الحاليون المغطّون:
  - `openai`
  - `google`
- تضييق اختياري:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- سلوك مصادقة اختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن profiles وتجاهل تجاوزات env-only

## Music generation live

- الاختبار: `extensions/music-generation-providers.live.test.ts`
- التفعيل: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- الـ harness: `pnpm test:live:media music`
- النطاق:
  - يختبر مسار موفر توليد الموسيقى المشترك المدمج
  - يغطي حاليًا Google وMiniMax
  - يحمّل متغيرات env الخاصة بالموفر من shell تسجيل الدخول لديك (`~/.profile`) قبل المجسات
  - يستخدم مفاتيح API الحية/من env قبل profiles المخزنة للمصادقة افتراضيًا، حتى لا تُخفي مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات اعتماد shell الحقيقية
  - يتخطى الموفّرين الذين لا يملكون مصادقة/ profile / نموذجًا صالحًا
  - يشغّل وضعي runtime المعلنين كليهما عندما يكونان متاحين:
    - `generate` مع إدخال يعتمد فقط على prompt
    - `edit` عندما يعلن الموفّر `capabilities.edit.enabled`
  - التغطية الحالية للمسار المشترك:
    - `google`: `generate` و`edit`
    - `minimax`: `generate`
    - `comfy`: ملف Comfy حي منفصل، وليس هذا المسح المشترك
- تضييق اختياري:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- سلوك مصادقة اختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن profiles وتجاهل تجاوزات env-only

## Video generation live

- الاختبار: `extensions/video-generation-providers.live.test.ts`
- التفعيل: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- الـ harness: `pnpm test:live:media video`
- النطاق:
  - يختبر مسار موفر توليد الفيديو المشترك المدمج
  - يحمّل متغيرات env الخاصة بالموفر من shell تسجيل الدخول لديك (`~/.profile`) قبل المجسات
  - يستخدم مفاتيح API الحية/من env قبل profiles المخزنة للمصادقة افتراضيًا، حتى لا تُخفي مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات اعتماد shell الحقيقية
  - يتخطى الموفّرين الذين لا يملكون مصادقة/ profile / نموذجًا صالحًا
  - يشغّل وضعي runtime المعلنين كليهما عندما يكونان متاحين:
    - `generate` مع إدخال يعتمد فقط على prompt
    - `imageToVideo` عندما يعلن الموفّر `capabilities.imageToVideo.enabled` ويقبل الموفّر/النموذج المحدد إدخال الصور المحلية المعتمد على buffer في المسح المشترك
    - `videoToVideo` عندما يعلن الموفّر `capabilities.videoToVideo.enabled` ويقبل الموفّر/النموذج المحدد إدخال الفيديو المحلي المعتمد على buffer في المسح المشترك
  - الموفّرون المعلنون حاليًا لكن المتخطَّون في المسح المشترك لـ `imageToVideo`:
    - `vydra` لأن `veo3` المدمج نصي فقط و`kling` المدمج يتطلب URL صورة عن بُعد
  - تغطية Vydra الخاصة بالموفر:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - يشغّل هذا الملف `veo3` لتحويل النص إلى فيديو بالإضافة إلى مسار `kling` يستخدم fixture افتراضيًا لصورة عبر URL عن بُعد
  - التغطية الحية الحالية لـ `videoToVideo`:
    - `runway` فقط عندما يكون النموذج المحدد هو `runway/gen4_aleph`
  - الموفّرون المعلنون حاليًا لكن المتخطَّون في المسح المشترك لـ `videoToVideo`:
    - `alibaba` و`qwen` و`xai` لأن هذه المسارات تتطلب حاليًا URLs مرجعية عن بُعد من نوع `http(s)` / MP4
    - `google` لأن مسار Gemini/Veo المشترك الحالي يستخدم إدخالًا محليًا معتمدًا على buffer وهذا المسار غير مقبول في المسح المشترك
    - `openai` لأن المسار المشترك الحالي يفتقر إلى ضمانات وصول خاصة بالمؤسسة إلى inpaint/remix للفيديو
- تضييق اختياري:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- سلوك مصادقة اختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن profiles وتجاهل تجاوزات env-only

## Media live harness

- الأمر: `pnpm test:live:media`
- الغرض:
  - يشغّل أجنحة image وmusic وvideo الحية المشتركة عبر نقطة دخول أصلية واحدة للمستودع
  - يحمّل تلقائيًا متغيرات env الناقصة للموفر من `~/.profile`
  - يضيّق تلقائيًا كل جناح إلى الموفّرين الذين لديهم حاليًا مصادقة صالحة افتراضيًا
  - يعيد استخدام `scripts/test-live.mjs`، بحيث يبقى سلوك النبض والوضع الهادئ متسقًا
- أمثلة:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## مشغلات Docker (اختبارات اختيارية من نوع "يعمل على Linux")

تنقسم مشغلات Docker هذه إلى فئتين:

- مشغلات النماذج الحية: يقوم `test:docker:live-models` و`test:docker:live-gateway` بتشغيل ملف live المطابق الخاص بمفاتيح profiles فقط داخل صورة Docker للمستودع (`src/agents/models.profiles.live.test.ts` و`src/gateway/gateway-models.profiles.live.test.ts`)، مع ربط دليل config المحلي ومساحة العمل لديك (واستيراد `~/.profile` إذا تم ربطه). نقاط الدخول المحلية المطابقة هي `test:live:models-profiles` و`test:live:gateway-profiles`.
- تفترض مشغلات Docker الحية افتراضيًا حدًا أصغر لاختبار الدخان حتى يبقى المسح الكامل عبر Docker عمليًا:
  يضبط `test:docker:live-models` افتراضيًا `OPENCLAW_LIVE_MAX_MODELS=12`، ويضبط
  `test:docker:live-gateway` افتراضيًا `OPENCLAW_LIVE_GATEWAY_SMOKE=1`،
  و`OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`،
  و`OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`، و
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. تجاوز متغيرات البيئة تلك عندما
  تريد عمدًا المسح الشامل الأكبر.
- يبني `test:docker:all` صورة Docker الحية مرة واحدة عبر `test:docker:live-build`، ثم يعيد استخدامها لمساري Docker الحيين.
- مشغلات دخان الحاويات: تقوم `test:docker:openwebui` و`test:docker:onboard` و`test:docker:gateway-network` و`test:docker:mcp-channels` و`test:docker:plugins` بتشغيل حاوية أو أكثر حقيقية وتتحقق من مسارات integration ذات مستوى أعلى.

تقوم مشغلات Docker الخاصة بالنماذج الحية أيضًا بربط أدلة مصادقة CLI المطلوبة فقط (أو جميع الأدلة المدعومة عندما لا يكون التشغيل مضيّقًا)، ثم تنسخها إلى home الحاوية قبل التشغيل حتى تتمكن OAuth الخاصة بـ CLI الخارجي من تحديث الرموز من دون تعديل مخزن المصادقة على المضيف:

- النماذج المباشرة: `pnpm test:docker:live-models` (السكربت: `scripts/test-live-models-docker.sh`)
- اختبار دخان ربط ACP: `pnpm test:docker:live-acp-bind` (السكربت: `scripts/test-live-acp-bind-docker.sh`)
- اختبار دخان الواجهة الخلفية CLI: `pnpm test:docker:live-cli-backend` (السكربت: `scripts/test-live-cli-backend-docker.sh`)
- البوابة + وكيل dev: `pnpm test:docker:live-gateway` (السكربت: `scripts/test-live-gateway-models-docker.sh`)
- اختبار دخان Open WebUI الحي: `pnpm test:docker:openwebui` (السكربت: `scripts/e2e/openwebui-docker.sh`)
- معالج onboarding (TTY، سقالة كاملة): `pnpm test:docker:onboard` (السكربت: `scripts/e2e/onboard-docker.sh`)
- شبكات البوابة (حاويتان، مصادقة WS + health): `pnpm test:docker:gateway-network` (السكربت: `scripts/e2e/gateway-network-docker.sh`)
- جسر قناة MCP (بوابة seed + جسر stdio + اختبار دخان raw Claude notification-frame): `pnpm test:docker:mcp-channels` (السكربت: `scripts/e2e/mcp-channels-docker.sh`)
- الإضافات (اختبار دخان التثبيت + الاسم البديل `/plugin` + دلالات إعادة تشغيل Claude-bundle): `pnpm test:docker:plugins` (السكربت: `scripts/e2e/plugins-docker.sh`)

تقوم مشغلات Docker الخاصة بالنماذج الحية أيضًا بربط النسخة الحالية من checkout
لديك بوضع القراءة فقط وتهيئتها في workdir مؤقت داخل الحاوية. يحافظ هذا على نحافة
صورة وقت التشغيل مع الاستمرار في تشغيل Vitest على المصدر/config المحليين لديك بدقة.
تتخطى خطوة التهيئة caches المحلية الكبيرة فقط ومخرجات بناء التطبيقات مثل
`.pnpm-store` و`.worktrees` و`__openclaw_vitest__` وأدلة `.build` المحلية للتطبيق أو
مخرجات Gradle حتى لا تقضي تشغيلات Docker الحية دقائق في نسخ
القطع الأثرية الخاصة بالجهاز.
كما تضبط `OPENCLAW_SKIP_CHANNELS=1` حتى لا تبدأ مجسات البوابة الحية
عمّال القنوات الحقيقية مثل Telegram/Discord وغيرها داخل الحاوية.
لا يزال `test:docker:live-models` يشغّل `pnpm test:live`، لذا مرّر أيضًا
`OPENCLAW_LIVE_GATEWAY_*` عندما تحتاج إلى تضييق أو استبعاد تغطية
البوابة الحية من مسار Docker ذلك.
يُعد `test:docker:openwebui` اختبار دخان توافق أعلى مستوى: فهو يبدأ
حاوية بوابة OpenClaw مع تمكين نقاط النهاية HTTP المتوافقة مع OpenAI،
ويبدأ حاوية Open WebUI مثبتة على ذلك gateway، ويسجل الدخول عبر
Open WebUI، ويتحقق من أن `/api/models` يعرض `openclaw/default`، ثم يرسل
طلب محادثة حقيقيًا عبر وكيل `/api/chat/completions` في Open WebUI.
قد يكون التشغيل الأول أبطأ بشكل ملحوظ لأن Docker قد يحتاج إلى سحب
صورة Open WebUI وقد يحتاج Open WebUI إلى إكمال إعداد البدء البارد الخاص به.
يتوقع هذا المسار مفتاح نموذج حي صالحًا، ويُعد `OPENCLAW_PROFILE_FILE`
(`~/.profile` افتراضيًا) الطريقة الأساسية لتوفيره في التشغيلات عبر Docker.
تطبع التشغيلات الناجحة payload JSON صغيرة مثل `{ "ok": true, "model":
"openclaw/default", ... }`.
تم تصميم `test:docker:mcp-channels` ليكون حتميًا عمدًا ولا يحتاج إلى
حساب Telegram أو Discord أو iMessage حقيقي. فهو يشغّل حاوية Gateway
ببيانات seed، ويبدأ حاوية ثانية تشغّل `openclaw mcp serve`، ثم
يتحقق من اكتشاف المحادثات الموجّهة، وقراءات transcript، وmetadata الخاصة بالمرفقات،
وسلوك قائمة الأحداث الحية، وتوجيه الإرسال الصادر، وإشعارات القناة +
الصلاحيات بنمط Claude عبر جسر stdio MCP الحقيقي. ويفحص تحقق الإشعارات
إطارات stdio MCP الخام مباشرة بحيث يثبت اختبار الدخان ما الذي يصدره
الجسر فعلًا، وليس فقط ما قد تُظهره SDK عميل معين.

اختبار thread ACP باللغة الطبيعية يدويًا (ليس في CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- احتفظ بهذا السكربت لمسارات اختبارات التراجع/التصحيح. قد تكون هناك حاجة إليه مرة أخرى للتحقق من توجيه thread في ACP، لذا لا تحذفه.

متغيرات بيئة مفيدة:

- `OPENCLAW_CONFIG_DIR=...` (الافتراضي: `~/.openclaw`) يُربط إلى `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` (الافتراضي: `~/.openclaw/workspace`) يُربط إلى `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` (الافتراضي: `~/.profile`) يُربط إلى `/home/node/.profile` ويُستورد قبل تشغيل الاختبارات
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (الافتراضي: `~/.cache/openclaw/docker-cli-tools`) يُربط إلى `/home/node/.npm-global` لتثبيتات CLI المخزنة مؤقتًا داخل Docker
- تُربط أدلة/ملفات مصادقة CLI الخارجية تحت `$HOME` بوضع القراءة فقط تحت `/host-auth...`، ثم تُنسخ إلى `/home/node/...` قبل بدء الاختبارات
  - الأدلة الافتراضية: `.minimax`
  - الملفات الافتراضية: `~/.codex/auth.json` و`~/.codex/config.toml` و`.claude.json` و`~/.claude/.credentials.json` و`~/.claude/settings.json` و`~/.claude/settings.local.json`
  - تقوم تشغيلات الموفّر المضيق بربط الأدلة/الملفات المطلوبة فقط والمستنتجة من `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - تجاوز يدويًا عبر `OPENCLAW_DOCKER_AUTH_DIRS=all` أو `OPENCLAW_DOCKER_AUTH_DIRS=none` أو قائمة مفصولة بفواصل مثل `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` لتضييق التشغيل
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...` لتصفية الموفّرين داخل الحاوية
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لضمان أن تأتي بيانات الاعتماد من مخزن profiles (وليس env)
- `OPENCLAW_OPENWEBUI_MODEL=...` لاختيار النموذج الذي تعرضه البوابة لاختبار دخان Open WebUI
- `OPENCLAW_OPENWEBUI_PROMPT=...` لتجاوز prompt فحص nonce المستخدم في اختبار دخان Open WebUI
- `OPENWEBUI_IMAGE=...` لتجاوز وسم صورة Open WebUI المثبتة

## سلامة الوثائق

شغّل فحوصات الوثائق بعد تعديل الوثائق: `pnpm check:docs`.
شغّل تحقق Mintlify الكامل للروابط والمرابط عندما تحتاج أيضًا إلى فحوصات العناوين داخل الصفحة: `pnpm docs:check-links:anchors`.

## اختبار تراجع دون اتصال (آمن لـ CI)

هذه اختبارات تراجع "للمسار الحقيقي" من دون موفرين حقيقيين:

- استدعاء أدوات البوابة (OpenAI وهمي، بوابة حقيقية + حلقة وكيل): `src/gateway/gateway.test.ts` (الحالة: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- معالج البوابة (WS `wizard.start`/`wizard.next`، يكتب config + يفرض auth): `src/gateway/gateway.test.ts` (الحالة: "runs wizard over ws and writes auth token config")

## تقييمات موثوقية الوكيل (Skills)

لدينا بالفعل بعض الاختبارات الآمنة لـ CI التي تتصرف مثل "تقييمات موثوقية الوكيل":

- استدعاء أدوات وهمية عبر البوابة الحقيقية + حلقة الوكيل (`src/gateway/gateway.test.ts`).
- تدفقات wizard من طرف إلى طرف تتحقق من توصيل الجلسة وآثار config (`src/gateway/gateway.test.ts`).

ما يزال مفقودًا للـ Skills (راجع [Skills](/ar/tools/skills)):

- **اتخاذ القرار:** عندما تُدرج Skills في prompt، هل يختار الوكيل المهارة الصحيحة (أو يتجنب غير المرتبط منها)؟
- **الامتثال:** هل يقرأ الوكيل `SKILL.md` قبل الاستخدام ويتبع الخطوات/الوسائط المطلوبة؟
- **عقود سير العمل:** سيناريوهات متعددة الأدوار تتحقق من ترتيب الأدوات، واستمرار سجل الجلسة، وحدود sandbox.

يجب أن تبقى التقييمات المستقبلية حتمية أولًا:

- مشغّل سيناريوهات يستخدم موفرين وهميين للتحقق من استدعاءات الأدوات + ترتيبها، وقراءات ملفات المهارات، وتوصيل الجلسة.
- جناح صغير من السيناريوهات المركزة على المهارات (استخدم مقابل تجنب، البوابات، حقن prompt).
- تقييمات حية اختيارية (opt-in، ومحكومة بـ env) فقط بعد وجود الجناح الآمن لـ CI.

## اختبارات العقود (شكل الإضافة والقناة)

تتحقق اختبارات العقود من أن كل إضافة وقناة مسجلة تطابق
عقد الواجهة الخاص بها. فهي تتكرر عبر جميع الإضافات المكتشفة وتشغّل مجموعة من
التحققات الخاصة بالشكل والسلوك. يتخطى مسار unit الافتراضي `pnpm test`
عمدًا ملفات هذا السطح المشترك واختباراته الدخانية؛ شغّل أوامر العقود صراحةً
عندما تلمس أسطح القنوات أو الموفّرين المشتركة.

### الأوامر

- كل العقود: `pnpm test:contracts`
- عقود القنوات فقط: `pnpm test:contracts:channels`
- عقود الموفّرين فقط: `pnpm test:contracts:plugins`

### عقود القنوات

توجد في `src/channels/plugins/contracts/*.contract.test.ts`:

- **plugin** - الشكل الأساسي للإضافة (id، name، capabilities)
- **setup** - عقد معالج الإعداد
- **session-binding** - سلوك ربط الجلسة
- **outbound-payload** - بنية payload الرسالة
- **inbound** - معالجة الرسائل الواردة
- **actions** - معالجات إجراءات القناة
- **threading** - التعامل مع معرّف thread
- **directory** - API الدليل/القائمة
- **group-policy** - فرض سياسة المجموعة

### عقود حالة الموفّر

توجد في `src/plugins/contracts/*.contract.test.ts`.

- **status** - مجسات حالة القناة
- **registry** - شكل سجل الإضافة

### عقود الموفّر

توجد في `src/plugins/contracts/*.contract.test.ts`:

- **auth** - عقد تدفق المصادقة
- **auth-choice** - اختيار/تحديد المصادقة
- **catalog** - API كتالوج النماذج
- **discovery** - اكتشاف الإضافة
- **loader** - تحميل الإضافة
- **runtime** - وقت تشغيل الموفّر
- **shape** - شكل/واجهة الإضافة
- **wizard** - معالج الإعداد

### متى تُشغّل

- بعد تغيير صادرات `plugin-sdk` أو subpaths الخاصة به
- بعد إضافة أو تعديل إضافة قناة أو موفّر
- بعد إعادة هيكلة تسجيل الإضافة أو اكتشافها

تعمل اختبارات العقود في CI ولا تتطلب مفاتيح API حقيقية.

## إضافة اختبارات تراجع (إرشادات)

عندما تصلح مشكلة موفر/نموذج اكتُشفت في live:

- أضف اختبار تراجع آمنًا لـ CI إن أمكن (موفر وهمي/بديل، أو التقاط التحويل الدقيق لشكل الطلب)
- إذا كانت بطبيعتها مقتصرة على live فقط (حدود المعدل، سياسات المصادقة)، فأبقِ الاختبار الحي ضيقًا ومفعّلًا اختياريًا عبر متغيرات env
- افضّل استهداف أصغر طبقة تلتقط الخطأ:
  - خطأ في تحويل/إعادة تشغيل طلب الموفّر → اختبار direct models
  - خطأ في مسار جلسة/سجل/أدوات البوابة → اختبار دخان live للبوابة أو اختبار وهمي آمن لـ CI للبوابة
- حاجز حماية اجتياز SecretRef:
  - يستخلص `src/secrets/exec-secret-ref-id-parity.test.ts` هدفًا نموذجيًا واحدًا لكل فئة SecretRef من metadata الخاصة بالسجل (`listSecretTargetRegistryEntries()`)، ثم يتحقق من رفض معرّفات exec الخاصة بمقاطع الاجتياز.
  - إذا أضفت عائلة أهداف SecretRef جديدة من نوع `includeInPlan` في `src/secrets/target-registry-data.ts`، فحدّث `classifyTargetClass` في ذلك الاختبار. يفشل الاختبار عمدًا مع معرّفات الأهداف غير المصنفة حتى لا يمكن تخطي الفئات الجديدة بصمت.
