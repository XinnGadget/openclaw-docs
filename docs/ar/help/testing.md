---
read_when:
    - تشغيل الاختبارات محليًا أو في CI
    - إضافة اختبارات انحدار لأخطاء النموذج/الموفّر
    - تصحيح سلوك gateway + العامل
summary: 'مجموعة الاختبار: أجنحة unit/e2e/live، ومشغلات Docker، وما الذي يغطيه كل اختبار'
title: الاختبار
x-i18n:
    generated_at: "2026-04-07T07:21:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9bd5fbc91435d7acd94758fa4a00af5a80363ddebc715b8731bb508b9e5d6d28
    source_path: help/testing.md
    workflow: 15
---

# الاختبار

يحتوي OpenClaw على ثلاثة أجنحة Vitest (unit/integration وe2e وlive) ومجموعة صغيرة من مشغلات Docker.

هذا المستند هو دليل "كيف نختبر":

- ما الذي يغطيه كل جناح (وما الذي _لا_ يغطيه عمدًا)
- ما الأوامر التي يجب تشغيلها لسير العمل الشائع (محلي، قبل الدفع، التصحيح)
- كيف تكتشف الاختبارات الحية بيانات الاعتماد وتحدد النماذج/الموفّرين
- كيفية إضافة اختبارات انحدار للمشكلات الواقعية المتعلقة بالنموذج/الموفّر

## بداية سريعة

في معظم الأيام:

- البوابة الكاملة (المتوقعة قبل الدفع): `pnpm build && pnpm check && pnpm test`
- تشغيل أسرع محليًا للجناح الكامل على جهاز ذي موارد جيدة: `pnpm test:max`
- حلقة مراقبة Vitest مباشرة: `pnpm test:watch`
- الاستهداف المباشر للملفات يوجّه الآن أيضًا مسارات extensions/channel: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- موقع QA المدعوم بـ Docker: `pnpm qa:lab:up`

عندما تلمس الاختبارات أو تريد ثقة إضافية:

- بوابة التغطية: `pnpm test:coverage`
- جناح E2E: `pnpm test:e2e`

عند تصحيح موفّرين/نماذج حقيقية (يتطلب بيانات اعتماد حقيقية):

- الجناح الحي (النماذج + فحوص أدوات/صور gateway): `pnpm test:live`
- استهدف ملف live واحد بهدوء: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

نصيحة: عندما تحتاج حالة فاشلة واحدة فقط، فالأفضل تضييق اختبارات live باستخدام متغيرات بيئة allowlist الموضحة أدناه.

## أجنحة الاختبار (ما الذي يعمل وأين)

فكّر في الأجنحة على أنها "واقعية متزايدة" (ومعها تزايد عدم الاستقرار/التكلفة):

### Unit / integration (الافتراضي)

- الأمر: `pnpm test`
- الإعداد: عشر تشغيلات shards متسلسلة (`vitest.full-*.config.ts`) عبر مشاريع Vitest المحددة الموجودة
- الملفات: قوائم unit/core تحت `src/**/*.test.ts` و`packages/**/*.test.ts` و`test/**/*.test.ts` واختبارات `ui` الخاصة بـ node المدرجة في allowlist والمغطاة بواسطة `vitest.unit.config.ts`
- النطاق:
  - اختبارات unit خالصة
  - اختبارات integration داخل العملية (مصادقة gateway، والتوجيه، والأدوات، والتحليل، والإعدادات)
  - اختبارات انحدار حتمية للأخطاء المعروفة
- التوقعات:
  - تعمل في CI
  - لا حاجة إلى مفاتيح حقيقية
  - يجب أن تكون سريعة ومستقرة
- ملاحظة المشاريع:
  - أصبح `pnpm test` غير الموجّه يشغّل الآن عشرة إعدادات shards أصغر (`core-unit-src` و`core-unit-security` و`core-unit-ui` و`core-unit-support` و`core-contracts` و`core-bundled` و`core-runtime` و`agentic` و`auto-reply` و`extensions`) بدلًا من عملية root-project أصلية واحدة ضخمة. هذا يقلل ذروة RSS على الأجهزة المزدحمة ويتجنب أن تؤدي أعمال auto-reply/extension إلى تجويع الأجنحة غير ذات الصلة.
  - يظل `pnpm test --watch` يستخدم مخطط مشاريع `vitest.config.ts` الأصلي للجذر، لأن حلقة مراقبة متعددة shards ليست عملية.
  - `pnpm test` و`pnpm test:watch` و`pnpm test:perf:imports` توجّه أهداف الملفات/الأدلة الصريحة عبر مسارات محددة أولًا، لذلك فإن `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` يتجنب تكلفة بدء root project الكامل.
  - يقوم `pnpm test:changed` بتوسيع مسارات git المتغيرة إلى هذه المسارات المحددة نفسها عندما يلمس الفرق ملفات مصدر/اختبار قابلة للتوجيه فقط؛ أما تعديلات config/setup فتعود إلى إعادة تشغيل root-project الواسعة.
  - بعض اختبارات `plugin-sdk` و`commands` المختارة تمر أيضًا عبر مسارات خفيفة مخصصة تتخطى `test/setup-openclaw-runtime.ts`؛ بينما تبقى الملفات ذات الحالة/الثقيلة من ناحية بيئة التشغيل على المسارات الحالية.
  - تُطابَق أيضًا بعض ملفات المصدر المساعدة المحددة لـ `plugin-sdk` و`commands` في وضع changed مع اختبارات شقيقة صريحة ضمن تلك المسارات الخفيفة، بحيث تتجنب تعديلات المساعدين إعادة تشغيل الجناح الثقيل الكامل لذلك الدليل.
  - يحتوي `auto-reply` الآن على ثلاث مجموعات مخصصة: مساعدات core ذات المستوى الأعلى، واختبارات integration من المستوى الأعلى لـ `reply.*`، والشجرة الفرعية `src/auto-reply/reply/**`. وهذا يبقي أكثر أعمال harness الخاصة بالردود ثقلًا بعيدًا عن اختبارات الحالة/الأجزاء/الرموز الرخيصة.
- ملاحظة المشغل المضمّن:
  - عندما تغيّر مدخلات اكتشاف أدوات الرسائل أو سياق وقت تشغيل compaction،
    حافظ على مستويي التغطية معًا.
  - أضف اختبارات انحدار مركزة للمساعدين لحدود التوجيه/التسوية الخالصة.
  - وحافظ أيضًا على سلامة أجنحة integration الخاصة بالمشغل المضمّن:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`،
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`، و
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - تتحقق هذه الأجنحة من أن المعرّفات المحددة وسلوك compaction لا يزالان يتدفقان
    عبر المسارات الحقيقية لـ `run.ts` / `compact.ts`؛ واختبارات المساعدين وحدها
    ليست بديلًا كافيًا لهذه المسارات التكاملية.
- ملاحظة pool:
  - أصبح إعداد Vitest الأساسي يستخدم `threads` افتراضيًا الآن.
  - كما يثبت إعداد Vitest المشترك `isolate: false` ويستخدم المشغل غير المعزول عبر مشاريع الجذر وتهيئات e2e وlive.
  - يحتفظ مسار UI الجذري بإعداد `jsdom` والمحسّن الخاص به، لكنه يعمل الآن أيضًا على المشغل المشترك غير المعزول.
  - يرث كل shard ضمن `pnpm test` الافتراضيات نفسها `threads` + `isolate: false` من إعداد Vitest المشترك.
  - يضيف المشغل المشترك `scripts/run-vitest.mjs` الآن أيضًا `--no-maglev` لعمليات Node الفرعية الخاصة بـ Vitest افتراضيًا لتقليل تقلبات الترجمة في V8 أثناء التشغيلات المحلية الكبيرة. اضبط `OPENCLAW_VITEST_ENABLE_MAGLEV=1` إذا كنت بحاجة إلى المقارنة مع سلوك V8 الافتراضي.
- ملاحظة التكرار المحلي السريع:
  - يوجّه `pnpm test:changed` عبر مسارات محددة عندما ترتبط المسارات المتغيرة بوضوح بجناح أصغر.
  - يحتفظ `pnpm test:max` و`pnpm test:changed:max` بسلوك التوجيه نفسه، ولكن مع حد أعلى أكبر للعمال.
  - أصبح التحجيم التلقائي لعدد العمال محليًا محافظًا عمدًا الآن ويتراجع أيضًا عندما يكون متوسط حمل المضيف مرتفعًا بالفعل، بحيث تُحدث تشغيلات Vitest المتزامنة المتعددة ضررًا أقل افتراضيًا.
  - يضع إعداد Vitest الأساسي ملفات projects/config كـ `forceRerunTriggers` بحيث تظل إعادة التشغيل في وضع changed صحيحة عندما تتغير أسلاك الاختبار.
  - يبقي الإعداد `OPENCLAW_VITEST_FS_MODULE_CACHE` مفعّلًا على المضيفين المدعومين؛ اضبط `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` إذا كنت تريد موقع cache صريحًا واحدًا من أجل profiling مباشر.
- ملاحظة تصحيح الأداء:
  - يفعّل `pnpm test:perf:imports` تقارير مدة الاستيراد في Vitest بالإضافة إلى مخرجات تفصيل الاستيراد.
  - يقيّد `pnpm test:perf:imports:changed` عرض profiling نفسه على الملفات التي تغيّرت منذ `origin/main`.
- يقارن `pnpm test:perf:changed:bench -- --ref <git-ref>` بين `test:changed` الموجّه ومسار root-project الأصلي لذلك الفرق الملتزم، ويطبع زمن الجدار بالإضافة إلى أقصى RSS على macOS.
- يختبر `pnpm test:perf:changed:bench -- --worktree` الشجرة المتسخة الحالية عبر توجيه قائمة الملفات المتغيرة إلى `scripts/test-projects.mjs` وإعداد Vitest الجذري.
  - يكتب `pnpm test:perf:profile:main` ملف profile للمعالج الرئيسي لـ CPU من أجل تكلفة بدء Vitest/Vite والتحويل.
  - يكتب `pnpm test:perf:profile:runner` ملفات profile لـ CPU+heap للمشغّل من أجل جناح unit مع تعطيل التوازي على مستوى الملفات.

### E2E (فحص gateway الدخاني)

- الأمر: `pnpm test:e2e`
- الإعداد: `vitest.e2e.config.ts`
- الملفات: `src/**/*.e2e.test.ts` و`test/**/*.e2e.test.ts`
- افتراضيات وقت التشغيل:
  - يستخدم Vitest `threads` مع `isolate: false`، بما يتطابق مع بقية المستودع.
  - يستخدم عمالًا تكيفيين (CI: حتى 2، محليًا: 1 افتراضيًا).
  - يعمل في الوضع الصامت افتراضيًا لتقليل تكلفة I/O في الطرفية.
- تجاوزات مفيدة:
  - `OPENCLAW_E2E_WORKERS=<n>` لفرض عدد العمال (بحد أقصى 16).
  - `OPENCLAW_E2E_VERBOSE=1` لإعادة تمكين المخرجات التفصيلية في الطرفية.
- النطاق:
  - سلوك gateway من الطرف إلى الطرف عبر عدة نُسخ
  - واجهات WebSocket/HTTP، واقتران العقد، والشبكات الأثقل
- التوقعات:
  - يعمل في CI (عند تمكينه في خط الأنابيب)
  - لا حاجة إلى مفاتيح حقيقية
  - يحتوي على أجزاء متحركة أكثر من اختبارات unit (وقد يكون أبطأ)

### E2E: فحص OpenShell الخلفي الدخاني

- الأمر: `pnpm test:e2e:openshell`
- الملف: `test/openshell-sandbox.e2e.test.ts`
- النطاق:
  - يبدأ gateway OpenShell معزولًا على المضيف عبر Docker
  - ينشئ sandbox من Dockerfile محلي مؤقت
  - يختبر الواجهة الخلفية OpenShell الخاصة بـ OpenClaw عبر `sandbox ssh-config` + تنفيذ SSH حقيقي
  - يتحقق من سلوك نظام الملفات canonical البعيد عبر جسر fs الخاص بـ sandbox
- التوقعات:
  - اشتراك اختياري فقط؛ ليس جزءًا من تشغيل `pnpm test:e2e` الافتراضي
  - يتطلب CLI محليًا لـ `openshell` بالإضافة إلى daemon Docker يعمل
  - يستخدم `HOME` / `XDG_CONFIG_HOME` معزولين، ثم يدمّر gateway الاختباري وsandbox
- تجاوزات مفيدة:
  - `OPENCLAW_E2E_OPENSHELL=1` لتمكين الاختبار عند تشغيل جناح e2e الأوسع يدويًا
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell` للإشارة إلى binary CLI غير افتراضي أو script wrapper

### Live (موفّرون حقيقيون + نماذج حقيقية)

- الأمر: `pnpm test:live`
- الإعداد: `vitest.live.config.ts`
- الملفات: `src/**/*.live.test.ts`
- الافتراضي: **مفعّل** بواسطة `pnpm test:live` (يضبط `OPENCLAW_LIVE_TEST=1`)
- النطاق:
  - "هل يعمل هذا الموفّر/النموذج فعلًا _اليوم_ باستخدام بيانات اعتماد حقيقية؟"
  - كشف تغييرات تنسيق الموفّر، وخصائص استدعاء الأدوات، ومشكلات المصادقة، وسلوك حدود المعدل
- التوقعات:
  - غير مستقر في CI بطبيعته (شبكات حقيقية، وسياسات موفّرين حقيقية، وحصص، وأعطال)
  - يكلّف أموالًا / يستهلك حدود المعدل
  - يُفضَّل تشغيل مجموعات فرعية ضيقة بدلًا من "كل شيء"
- تستورد تشغيلات live الملف `~/.profile` لالتقاط مفاتيح API الناقصة.
- افتراضيًا، تظل تشغيلات live تعزل `HOME` وتنسخ مواد config/auth إلى home اختباري مؤقت حتى لا تتمكن fixtures الخاصة بـ unit من تعديل `~/.openclaw` الحقيقي لديك.
- اضبط `OPENCLAW_LIVE_USE_REAL_HOME=1` فقط عندما تحتاج عمدًا إلى أن تستخدم اختبارات live دليل home الحقيقي لديك.
- أصبح `pnpm test:live` يستخدم وضعًا أكثر هدوءًا افتراضيًا: فهو يبقي مخرجات التقدم `[live] ...`، لكنه يخفي الإشعار الإضافي الخاص بـ `~/.profile` ويكتم سجلات تمهيد gateway وضجيج Bonjour. اضبط `OPENCLAW_LIVE_TEST_QUIET=0` إذا أردت سجلات البدء الكاملة مجددًا.
- تدوير مفاتيح API (خاص بكل موفّر): اضبط `*_API_KEYS` بتنسيق الفاصلة/الفاصلة المنقوطة أو `*_API_KEY_1` و`*_API_KEY_2` (مثل `OPENAI_API_KEYS` و`ANTHROPIC_API_KEYS` و`GEMINI_API_KEYS`) أو تجاوزًا خاصًا بـ live عبر `OPENCLAW_LIVE_*_KEY`؛ تعيد الاختبارات المحاولة عند استجابات حدود المعدل.
- مخرجات التقدم/النبض:
  - تصدر أجنحة live الآن أسطر التقدم إلى stderr بحيث تبدو استدعاءات الموفّر الطويلة نشطة بوضوح حتى عندما يكون التقاط طرفية Vitest هادئًا.
  - يعطّل `vitest.live.config.ts` اعتراض طرفية Vitest بحيث تُبث أسطر تقدم الموفّر/gateway فورًا أثناء تشغيلات live.
  - اضبط نبضات النماذج المباشرة بواسطة `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - اضبط نبضات gateway/probe بواسطة `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## أي جناح يجب أن أشغّل؟

استخدم جدول القرار هذا:

- تعديل المنطق/الاختبارات: شغّل `pnpm test` (و`pnpm test:coverage` إذا غيّرت الكثير)
- لمس شبكات gateway / بروتوكول WS / الاقتران: أضف `pnpm test:e2e`
- تصحيح "الروبوت الخاص بي متوقف" / الأعطال الخاصة بالموفّر / استدعاء الأدوات: شغّل `pnpm test:live` مضيقًا

## Live: مسح قدرات عقدة Android

- الاختبار: `src/gateway/android-node.capabilities.live.test.ts`
- السكربت: `pnpm android:test:integration`
- الهدف: استدعاء **كل أمر مُعلن عنه حاليًا** بواسطة عقدة Android متصلة والتحقق من سلوك عقد الأوامر.
- النطاق:
  - إعداد مسبق/يدوي (لا يقوم الجناح بتثبيت التطبيق أو تشغيله أو إقرانه).
  - تحقق `node.invoke` في gateway أمرًا بأمر لعقدة Android المحددة.
- الإعداد المسبق المطلوب:
  - أن يكون تطبيق Android متصلًا ومقترنًا بالفعل مع gateway.
  - إبقاء التطبيق في الواجهة الأمامية.
  - منح الأذونات/موافقة الالتقاط للقدرات التي تتوقع نجاحها.
- تجاوزات الهدف الاختيارية:
  - `OPENCLAW_ANDROID_NODE_ID` أو `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- تفاصيل إعداد Android الكاملة: [تطبيق Android](/ar/platforms/android)

## Live: فحص النموذج الدخاني (مفاتيح الملفات الشخصية)

تنقسم اختبارات live إلى طبقتين حتى نتمكن من عزل الأعطال:

- يخبرنا "النموذج المباشر" ما إذا كان الموفّر/النموذج قادرًا على الرد أصلًا بالمفتاح المعطى.
- يخبرنا "فحص gateway الدخاني" ما إذا كان مسار gateway+agent الكامل يعمل لهذا النموذج (الجلسات، والسجل، والأدوات، وسياسة sandbox، وغير ذلك).

### الطبقة 1: إكمال النموذج المباشر (من دون gateway)

- الاختبار: `src/agents/models.profiles.live.test.ts`
- الهدف:
  - تعداد النماذج المكتشفة
  - استخدام `getApiKeyForModel` لاختيار النماذج التي لديك بيانات اعتماد لها
  - تشغيل إكمال صغير لكل نموذج (واختبارات انحدار مستهدفة عند الحاجة)
- كيفية التمكين:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` إذا كنت تستدعي Vitest مباشرة)
- اضبط `OPENCLAW_LIVE_MODELS=modern` (أو `all`، وهو اسم مستعار لـ modern) لتشغيل هذا الجناح فعلًا؛ وإلا فسيتم تخطيه لإبقاء `pnpm test:live` مركزًا على فحص gateway الدخاني
- كيفية اختيار النماذج:
  - `OPENCLAW_LIVE_MODELS=modern` لتشغيل allowlist الحديثة (Opus/Sonnet 4.6+، وGPT-5.x + Codex، وGemini 3، وGLM 4.7، وMiniMax M2.7، وGrok 4)
  - `OPENCLAW_LIVE_MODELS=all` هو اسم مستعار لـ allowlist الحديثة
  - أو `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (allowlist مفصولة بفواصل)
- كيفية اختيار الموفّرين:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (allowlist مفصولة بفواصل)
- من أين تأتي المفاتيح:
  - افتراضيًا: من مخزن الملفات الشخصية وبدائل env
  - اضبط `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض **مخزن الملفات الشخصية** فقط
- سبب وجود هذا:
  - يفصل بين "API الموفّر معطّل / المفتاح غير صالح" و"خط أنابيب gateway agent معطّل"
  - يحتوي على اختبارات انحدار صغيرة ومعزولة (مثال: تشغيلات OpenAI Responses/Codex Responses الخاصة بإعادة reasoning + تدفقات استدعاء الأدوات)

### الطبقة 2: فحص gateway + dev agent الدخاني (ما الذي يفعله "@openclaw" فعليًا)

- الاختبار: `src/gateway/gateway-models.profiles.live.test.ts`
- الهدف:
  - تشغيل gateway داخل العملية
  - إنشاء/ترقيع جلسة `agent:dev:*` (مع تجاوز النموذج لكل تشغيل)
  - التكرار على النماذج التي لها مفاتيح والتحقق من:
    - استجابة "ذات معنى" (من دون أدوات)
    - عمل استدعاء أداة حقيقي (فحص read)
    - فحوص أدوات إضافية اختيارية (فحص exec+read)
    - استمرار عمل مسارات الانحدار الخاصة بـ OpenAI (استدعاء أدوات فقط → متابعة)
- تفاصيل الفحص (حتى تتمكن من شرح الأعطال بسرعة):
  - فحص `read`: يكتب الاختبار ملف nonce في مساحة العمل ويطلب من العامل أن يستخدم `read` له ويعيد nonce.
  - فحص `exec+read`: يطلب الاختبار من العامل أن يكتب nonce باستخدام `exec` في ملف مؤقت، ثم يستخدم `read` له.
  - فحص الصورة: يرفق الاختبار PNG مُنشأً (قطة + رمز عشوائي) ويتوقع من النموذج أن يعيد `cat <CODE>`.
  - مرجع التنفيذ: `src/gateway/gateway-models.profiles.live.test.ts` و`src/gateway/live-image-probe.ts`.
- كيفية التمكين:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` إذا كنت تستدعي Vitest مباشرة)
- كيفية اختيار النماذج:
  - الافتراضي: allowlist الحديثة (Opus/Sonnet 4.6+، وGPT-5.x + Codex، وGemini 3، وGLM 4.7، وMiniMax M2.7، وGrok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` هو اسم مستعار لـ allowlist الحديثة
  - أو اضبط `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (أو قائمة مفصولة بفواصل) للتضييق
- كيفية اختيار الموفّرين (لتجنب "كل شيء في OpenRouter"):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (allowlist مفصولة بفواصل)
- تكون فحوص الأدوات + الصور مفعلة دائمًا في هذا الاختبار الحي:
  - فحص `read` + فحص `exec+read` (ضغط على الأدوات)
  - يعمل فحص الصورة عندما يعلن النموذج دعم إدخال الصور
  - التدفق (بمستوى عالٍ):
    - ينشئ الاختبار PNG صغيرًا يحتوي على "CAT" + رمز عشوائي (`src/gateway/live-image-probe.ts`)
    - يرسله عبر `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - تحلل gateway المرفقات إلى `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - يمرّر العامل المضمّن رسالة مستخدم متعددة الوسائط إلى النموذج
    - التحقق: يحتوي الرد على `cat` + الرمز (سماحية OCR: يُسمح بأخطاء طفيفة)

نصيحة: لرؤية ما يمكنك اختباره على جهازك (ومعرّفات `provider/model` الدقيقة)، شغّل:

```bash
openclaw models list
openclaw models list --json
```

## Live: فحص الواجهة الخلفية CLI الدخاني (Codex CLI أو واجهات CLI محلية أخرى)

- الاختبار: `src/gateway/gateway-cli-backend.live.test.ts`
- الهدف: التحقق من خط أنابيب Gateway + agent باستخدام واجهة خلفية CLI محلية، من دون لمس إعداداتك الافتراضية.
- التمكين:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` إذا كنت تستدعي Vitest مباشرة)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- الافتراضيات:
  - النموذج: `codex-cli/gpt-5.4`
  - الأمر: `codex`
  - الوسائط: `["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]`
- التجاوزات (اختيارية):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` لإرسال مرفق صورة حقيقي (تُحقن المسارات في التوجيه).
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` لتمرير مسارات ملفات الصور كوسائط CLI بدلًا من حقنها في التوجيه.
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (أو `"list"`) للتحكم في كيفية تمرير وسائط الصور عندما يكون `IMAGE_ARG` مضبوطًا.
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` لإرسال منعطف ثانٍ والتحقق من تدفق الاستئناف.

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

ملاحظات:

- يوجد مشغل Docker في `scripts/test-live-cli-backend-docker.sh`.
- يشغّل فحص الواجهة الخلفية CLI الحي داخل صورة Docker الخاصة بالمستودع كمستخدم `node` غير الجذر.
- بالنسبة إلى `codex-cli`، فإنه يثبت حزمة Linux الخاصة بـ `@openai/codex` في بادئة قابلة للكتابة ومخزنة مؤقتًا عند `OPENCLAW_DOCKER_CLI_TOOLS_DIR` (الافتراضي: `~/.cache/openclaw/docker-cli-tools`).

## Live: فحص ACP bind الدخاني (`/acp spawn ... --bind here`)

- الاختبار: `src/gateway/gateway-acp-bind.live.test.ts`
- الهدف: التحقق من تدفق ربط المحادثة ACP الحقيقي مع عامل ACP حي:
  - إرسال `/acp spawn <agent> --bind here`
  - ربط محادثة قناة رسائل اصطناعية في مكانها
  - إرسال متابعة عادية على نفس المحادثة
  - التحقق من وصول المتابعة إلى نص جلسة ACP المرتبطة
- التمكين:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- الافتراضيات:
  - عوامل ACP في Docker: `claude,codex,gemini`
  - عامل ACP للاستخدام المباشر مع `pnpm test:live ...`: `claude`
  - قناة اصطناعية: سياق محادثة على نمط Slack DM
  - الواجهة الخلفية ACP: `acpx`
- التجاوزات:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- ملاحظات:
  - يستخدم هذا المسار واجهة `chat.send` في gateway مع حقول synthetic originating-route الخاصة بالمشرف فقط حتى تتمكن الاختبارات من إرفاق سياق قناة الرسائل من دون الادعاء بتسليم خارجي.
  - عندما لا يكون `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` مضبوطًا، يستخدم الاختبار سجل العوامل المضمّن في plugin `acpx` المحدد لعامل ACP harness المختار.

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

وصفات Docker لعامل واحد:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

ملاحظات Docker:

- يوجد مشغل Docker في `scripts/test-live-acp-bind-docker.sh`.
- افتراضيًا، يشغّل فحص ACP bind الدخاني مقابل جميع عوامل CLI الحية المدعومة بالتسلسل: `claude` ثم `codex` ثم `gemini`.
- استخدم `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude` أو `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` أو `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` لتضييق المصفوفة.
- يستورد `~/.profile`، ويجهّز مواد مصادقة CLI المطابقة داخل الحاوية، ويثبت `acpx` في بادئة npm قابلة للكتابة، ثم يثبت CLI الحي المطلوب (`@anthropic-ai/claude-code` أو `@openai/codex` أو `@google/gemini-cli`) إذا كان مفقودًا.
- داخل Docker، يضبط المشغل `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` حتى يحتفظ acpx بمتغيرات env الخاصة بالموفّر من الملف profile المستورد متاحة لواجهة harness CLI الفرعية.

### وصفات live الموصى بها

تكون allowlist الضيقة والصريحة أسرع وأقل عرضة للتقلب:

- نموذج واحد، مباشر (من دون gateway):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- نموذج واحد، فحص gateway دخاني:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- استدعاء الأدوات عبر عدة موفّرين:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- تركيز Google (مفتاح Gemini API + Antigravity):
  - Gemini (مفتاح API): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

ملاحظات:

- يستخدم `google/...` Gemini API (مفتاح API).
- يستخدم `google-antigravity/...` جسر Antigravity OAuth (نقطة نهاية عامل على نمط Cloud Code Assist).
- يستخدم `google-gemini-cli/...` Gemini CLI المحلية على جهازك (مصادقة منفصلة وخصائص أدوات مختلفة).
- Gemini API مقابل Gemini CLI:
  - API: يستدعي OpenClaw Gemini API المستضافة من Google عبر HTTP (مصادقة مفتاح API / profile)؛ وهذا هو ما يقصده معظم المستخدمين بـ "Gemini".
  - CLI: يقوم OpenClaw باستدعاء binary محلي باسم `gemini`؛ ولديه مصادقة خاصة به وقد يتصرف بشكل مختلف (البث/دعم الأدوات/اختلاف الإصدارات).

## Live: مصفوفة النماذج (ما الذي نغطيه)

لا توجد "قائمة نماذج CI" ثابتة (لأن live اختياري)، ولكن هذه هي النماذج **الموصى بها** للتغطية بانتظام على جهاز تطوير يحتوي على مفاتيح.

### مجموعة الفحص الحديثة (استدعاء الأدوات + الصور)

هذا هو تشغيل "النماذج الشائعة" الذي نتوقع أن يبقى عاملًا:

- OpenAI (غير Codex): `openai/gpt-5.4` (اختياري: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (أو `anthropic/claude-sonnet-4-6`)
- Google (Gemini API): `google/gemini-3.1-pro-preview` و`google/gemini-3-flash-preview` (تجنب نماذج Gemini 2.x الأقدم)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` و`google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

شغّل فحص gateway الدخاني مع الأدوات + الصور:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### الأساس: استدعاء الأدوات (Read + Exec اختياري)

اختر واحدًا على الأقل من كل عائلة موفّرين:

- OpenAI: `openai/gpt-5.4` (أو `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (أو `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (أو `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

تغطية إضافية اختيارية (من الجيد توفرها):

- xAI: `xai/grok-4` (أو أحدث إصدار متاح)
- Mistral: `mistral/`… (اختر نموذجًا واحدًا قادرًا على "tools" ومفعّلًا لديك)
- Cerebras: `cerebras/`… (إذا كان لديك وصول)
- LM Studio: `lmstudio/`… (محلي؛ يعتمد استدعاء الأدوات على وضع API)

### الرؤية: إرسال صورة (مرفق ← رسالة متعددة الوسائط)

ضمّن نموذجًا واحدًا على الأقل قادرًا على التعامل مع الصور في `OPENCLAW_LIVE_GATEWAY_MODELS` (أحد إصدارات Claude/Gemini/OpenAI القادرة على الرؤية، إلخ) لتشغيل فحص الصورة.

### المجمعات / البوابات البديلة

إذا كانت لديك مفاتيح مفعّلة، فنحن ندعم أيضًا الاختبار عبر:

- OpenRouter: `openrouter/...` (مئات النماذج؛ استخدم `openclaw models scan` للعثور على مرشحين قادرين على الأدوات+الصور)
- OpenCode: `opencode/...` لـ Zen و`opencode-go/...` لـ Go (المصادقة عبر `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

موفّرون إضافيون يمكنك تضمينهم في مصفوفة live (إذا كانت لديك بيانات الاعتماد/الإعدادات):

- المضمنة: `openai` و`openai-codex` و`anthropic` و`google` و`google-vertex` و`google-antigravity` و`google-gemini-cli` و`zai` و`openrouter` و`opencode` و`opencode-go` و`xai` و`groq` و`cerebras` و`mistral` و`github-copilot`
- عبر `models.providers` (نقاط نهاية مخصصة): `minimax` (سحابي/API)، بالإضافة إلى أي proxy متوافق مع OpenAI/Anthropic (مثل LM Studio وvLLM وLiteLLM وغيرها)

نصيحة: لا تحاول تثبيت "كل النماذج" بشكل صارم في الوثائق. القائمة الموثوقة هي أي شيء تُعيده `discoverModels(...)` على جهازك + أي مفاتيح متاحة.

## بيانات الاعتماد (لا تلتزم بها أبدًا)

تكتشف اختبارات live بيانات الاعتماد بالطريقة نفسها التي يفعلها CLI. الآثار العملية:

- إذا كانت CLI تعمل، فيجب أن تعثر اختبارات live على المفاتيح نفسها.
- إذا قال اختبار live "لا توجد بيانات اعتماد"، فقم بالتصحيح بالطريقة نفسها التي ستصحح بها `openclaw models list` / اختيار النموذج.

- ملفات مصادقة التعريفات الخاصة بكل عامل: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (وهذا ما تعنيه "مفاتيح الملف الشخصي" في اختبارات live)
- الإعدادات: `~/.openclaw/openclaw.json` (أو `OPENCLAW_CONFIG_PATH`)
- دليل الحالة القديم: `~/.openclaw/credentials/` (يُنسخ إلى home الحي المرحلي عند وجوده، لكنه ليس مخزن مفاتيح الملف الشخصي الرئيسي)
- تقوم تشغيلات live المحلية بنسخ الإعدادات النشطة، وملفات `auth-profiles.json` الخاصة بكل عامل، و`credentials/` القديمة، وأدلة مصادقة CLI الخارجية المدعومة إلى home اختباري مؤقت افتراضيًا؛ وتُزال تجاوزات المسار `agents.*.workspace` / `agentDir` في هذا config المرحلي بحيث تبقى الفحوص بعيدًا عن مساحة العمل الحقيقية على المضيف.

إذا أردت الاعتماد على مفاتيح env (مثلًا تلك المصدّرة في `~/.profile`)، فشغّل الاختبارات المحلية بعد `source ~/.profile`، أو استخدم مشغلات Docker أدناه (يمكنها تحميل `~/.profile` داخل الحاوية).

## Deepgram live (نسخ الصوت)

- الاختبار: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- التمكين: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- الاختبار: `src/agents/byteplus.live.test.ts`
- التمكين: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- تجاوز النموذج الاختياري: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow media live

- الاختبار: `extensions/comfy/comfy.live.test.ts`
- التمكين: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- النطاق:
  - يختبر مسارات الصور والفيديو و`music_generate` المضمنة في comfy
  - يتخطى كل قدرة ما لم يتم ضبط `models.providers.comfy.<capability>`
  - مفيد بعد تغيير إرسال workflow الخاص بـ comfy، أو polling، أو التنزيلات، أو تسجيل plugin

## Image generation live

- الاختبار: `src/image-generation/runtime.live.test.ts`
- الأمر: `pnpm test:live src/image-generation/runtime.live.test.ts`
- الـ Harness: `pnpm test:live:media image`
- النطاق:
  - يعدّد كل plugin موفّر لتوليد الصور مسجّل
  - يحمّل متغيرات env الخاصة بالموفّر الناقصة من shell تسجيل الدخول لديك (`~/.profile`) قبل الفحص
  - يستخدم مفاتيح API الحية/من env قبل ملفات المصادقة المخزنة افتراضيًا، بحيث لا تحجب مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات اعتماد shell الحقيقية
  - يتخطى الموفّرين الذين لا يملكون مصادقة/ملفًا شخصيًا/نموذجًا صالحًا
  - يشغّل متغيرات توليد الصور القياسية عبر قدرة وقت التشغيل المشتركة:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- الموفّرون المضمنون المغطّون حاليًا:
  - `openai`
  - `google`
- تضييق اختياري:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- سلوك مصادقة اختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن الملف الشخصي وتجاهل تجاوزات env فقط

## Music generation live

- الاختبار: `extensions/music-generation-providers.live.test.ts`
- التمكين: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- الـ Harness: `pnpm test:live:media music`
- النطاق:
  - يختبر مسار موفّر توليد الموسيقى المضمن المشترك
  - يغطي حاليًا Google وMiniMax
  - يحمّل متغيرات env الخاصة بالموفّر من shell تسجيل الدخول لديك (`~/.profile`) قبل الفحص
  - يستخدم مفاتيح API الحية/من env قبل ملفات المصادقة المخزنة افتراضيًا، بحيث لا تحجب مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات اعتماد shell الحقيقية
  - يتخطى الموفّرين الذين لا يملكون مصادقة/ملفًا شخصيًا/نموذجًا صالحًا
  - يشغّل وضعي وقت التشغيل المعلنين عند توفرهما:
    - `generate` بإدخال قائم على prompt فقط
    - `edit` عندما يعلن الموفّر `capabilities.edit.enabled`
  - التغطية الحالية للمسار المشترك:
    - `google`: `generate` و`edit`
    - `minimax`: `generate`
    - `comfy`: ملف Comfy live منفصل، وليس هذا المسح المشترك
- تضييق اختياري:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- سلوك مصادقة اختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن الملف الشخصي وتجاهل تجاوزات env فقط

## Video generation live

- الاختبار: `extensions/video-generation-providers.live.test.ts`
- التمكين: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- الـ Harness: `pnpm test:live:media video`
- النطاق:
  - يختبر مسار موفّر توليد الفيديو المضمن المشترك
  - يحمّل متغيرات env الخاصة بالموفّر من shell تسجيل الدخول لديك (`~/.profile`) قبل الفحص
  - يستخدم مفاتيح API الحية/من env قبل ملفات المصادقة المخزنة افتراضيًا، بحيث لا تحجب مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات اعتماد shell الحقيقية
  - يتخطى الموفّرين الذين لا يملكون مصادقة/ملفًا شخصيًا/نموذجًا صالحًا
  - يشغّل وضعي وقت التشغيل المعلنين عند توفرهما:
    - `generate` بإدخال قائم على prompt فقط
    - `imageToVideo` عندما يعلن الموفّر `capabilities.imageToVideo.enabled` ويقبل الموفّر/النموذج المحدد إدخال صور محلية مدعومًا بمخزن مؤقت في المسح المشترك
    - `videoToVideo` عندما يعلن الموفّر `capabilities.videoToVideo.enabled` ويقبل الموفّر/النموذج المحدد إدخال فيديو محلي مدعومًا بمخزن مؤقت في المسح المشترك
  - موفّرو `imageToVideo` المعلنون حاليًا لكن المتخطون في المسح المشترك:
    - `vydra` لأن `veo3` المضمن نصي فقط و`kling` المضمن يتطلب URL صورة بعيدًا
  - تغطية Vydra الخاصة بالموفّر:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - يشغّل ذلك الملف `veo3` لتحويل النص إلى فيديو بالإضافة إلى مسار `kling` يستخدم fixture لعنوان URL صورة بعيد افتراضيًا
  - تغطية `videoToVideo` الحالية في live:
    - `runway` فقط عندما يكون النموذج المحدد هو `runway/gen4_aleph`
  - موفّرو `videoToVideo` المعلنون حاليًا لكن المتخطون في المسح المشترك:
    - `alibaba` و`qwen` و`xai` لأن هذه المسارات تتطلب حاليًا عناوين URL مرجعية بعيدة من نوع `http(s)` / MP4
    - `google` لأن مسار Gemini/Veo المشترك الحالي يستخدم إدخالًا محليًا مدعومًا بمخزن مؤقت، وهذا المسار غير مقبول في المسح المشترك
    - `openai` لأن المسار المشترك الحالي يفتقر إلى ضمانات الوصول الخاصة بالمؤسسة الخاصة بـ video inpaint/remix
- تضييق اختياري:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- سلوك مصادقة اختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن الملف الشخصي وتجاهل تجاوزات env فقط

## Media live harness

- الأمر: `pnpm test:live:media`
- الغرض:
  - يشغّل أجنحة live المشتركة للصور والموسيقى والفيديو عبر نقطة دخول أصلية واحدة في المستودع
  - يحمّل تلقائيًا متغيرات env الخاصة بالموفّر الناقصة من `~/.profile`
  - يضيّق كل جناح تلقائيًا إلى الموفّرين الذين يملكون حاليًا مصادقة قابلة للاستخدام افتراضيًا
  - يعيد استخدام `scripts/test-live.mjs`، بحيث يظل سلوك النبض والوضع الهادئ متسقًا
- أمثلة:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## مشغلات Docker (فحوص "يعمل على Linux" الاختيارية)

تنقسم مشغلات Docker هذه إلى فئتين:

- مشغلات النماذج الحية: `test:docker:live-models` و`test:docker:live-gateway` يشغّلان فقط ملف live المطابق لمفاتيح الملفات الشخصية داخل صورة Docker الخاصة بالمستودع (`src/agents/models.profiles.live.test.ts` و`src/gateway/gateway-models.profiles.live.test.ts`)، مع تحميل دليل config المحلي ومساحة العمل (واستيراد `~/.profile` إن تم تحميله). نقاط الدخول المحلية المطابقة هي `test:live:models-profiles` و`test:live:gateway-profiles`.
- تستخدم مشغلات Docker الحية حدًا أصغر للفحص الدخاني افتراضيًا حتى يبقى المسح الكامل داخل Docker عمليًا:
  يضبط `test:docker:live-models` افتراضيًا `OPENCLAW_LIVE_MAX_MODELS=12`، كما يضبط
  `test:docker:live-gateway` افتراضيًا `OPENCLAW_LIVE_GATEWAY_SMOKE=1`،
  و`OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`،
  و`OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`، و
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. تجاوز متغيرات env هذه عندما
  تريد صراحةً المسح الأكبر والأشمل.
- يقوم `test:docker:all` ببناء صورة Docker الحية مرة واحدة عبر `test:docker:live-build`، ثم يعيد استخدامها لمساري Docker الحيين.
- مشغلات فحص الحاويات الدخاني: `test:docker:openwebui` و`test:docker:onboard` و`test:docker:gateway-network` و`test:docker:mcp-channels` و`test:docker:plugins` تشغّل حاوية واحدة أو أكثر حقيقية وتتحقق من مسارات integration أعلى مستوى.

تقوم مشغلات Docker الخاصة بالنماذج الحية أيضًا بربط وتحميل منازل مصادقة CLI المطلوبة فقط (أو جميع المنازل المدعومة عندما لا يكون التشغيل مضيقًا)، ثم تنسخها إلى home الحاوية قبل التشغيل حتى تتمكن OAuth الخاصة بـ CLI الخارجي من تحديث الرموز من دون تعديل مخزن المصادقة على المضيف:

- النماذج المباشرة: `pnpm test:docker:live-models` (السكربت: `scripts/test-live-models-docker.sh`)
- فحص ACP bind الدخاني: `pnpm test:docker:live-acp-bind` (السكربت: `scripts/test-live-acp-bind-docker.sh`)
- فحص الواجهة الخلفية CLI الدخاني: `pnpm test:docker:live-cli-backend` (السكربت: `scripts/test-live-cli-backend-docker.sh`)
- Gateway + dev agent: `pnpm test:docker:live-gateway` (السكربت: `scripts/test-live-gateway-models-docker.sh`)
- فحص Open WebUI الحي الدخاني: `pnpm test:docker:openwebui` (السكربت: `scripts/e2e/openwebui-docker.sh`)
- معالج onboarding (TTY، تهيئة كاملة): `pnpm test:docker:onboard` (السكربت: `scripts/e2e/onboard-docker.sh`)
- شبكات Gateway (حاويتان، مصادقة WS + health): `pnpm test:docker:gateway-network` (السكربت: `scripts/e2e/gateway-network-docker.sh`)
- جسر قناة MCP (Gateway مزروع + جسر stdio + فحص إطار إشعارات Claude الخام): `pnpm test:docker:mcp-channels` (السكربت: `scripts/e2e/mcp-channels-docker.sh`)
- Plugins (فحص التثبيت الدخاني + الاسم المستعار `/plugin` + دلالات إعادة تشغيل Claude-bundle): `pnpm test:docker:plugins` (السكربت: `scripts/e2e/plugins-docker.sh`)

تقوم مشغلات Docker الخاصة بالنماذج الحية أيضًا بربط checkout الحالي بوضع القراءة فقط
وتجهيزه في workdir مؤقت داخل الحاوية. وهذا يبقي صورة وقت التشغيل
خفيفة مع الاستمرار في تشغيل Vitest على مصدر/config المحليين لديك كما هما.
تتخطى خطوة التجهيز الذاكرات المؤقتة المحلية الكبيرة ومخرجات بناء التطبيقات مثل
`.pnpm-store` و`.worktrees` و`__openclaw_vitest__` وأدلة `.build` المحلية للتطبيقات أو مخرجات Gradle
حتى لا تقضي تشغيلات Docker live دقائق في نسخ آثار خاصة بالجهاز.
كما أنها تضبط `OPENCLAW_SKIP_CHANNELS=1` حتى لا تبدأ فحوص gateway الحية
عمّال القنوات الحقيقية مثل Telegram/Discord وغيرهما داخل الحاوية.
لا يزال `test:docker:live-models` يشغّل `pnpm test:live`، لذا مرّر
`OPENCLAW_LIVE_GATEWAY_*` أيضًا عندما تحتاج إلى تضييق أو استبعاد تغطية gateway
الحية من مسار Docker هذا.
يُعد `test:docker:openwebui` فحص توافق دخاني على مستوى أعلى: فهو يبدأ
حاوية gateway لـ OpenClaw مع تمكين نقاط نهاية HTTP المتوافقة مع OpenAI،
ثم يبدأ حاوية Open WebUI مثبتة الإصدار مقابل تلك gateway، ويسجّل الدخول عبر
Open WebUI، ويتحقق من أن `/api/models` يعرض `openclaw/default`، ثم يرسل
طلب chat حقيقيًا عبر proxy `Open WebUI` الخاص بـ `/api/chat/completions`.
قد يكون التشغيل الأول أبطأ بشكل ملحوظ لأن Docker قد يحتاج إلى سحب
صورة Open WebUI وقد يحتاج Open WebUI إلى إكمال إعداد البدء البارد الخاص به.
يتوقع هذا المسار مفتاح نموذج حيًا صالحًا، ويُعد `OPENCLAW_PROFILE_FILE`
(`~/.profile` افتراضيًا) هو الطريقة الأساسية لتوفيره في التشغيلات عبر Docker.
تطبع التشغيلات الناجحة حمولة JSON صغيرة مثل `{ "ok": true, "model":
"openclaw/default", ... }`.
أما `test:docker:mcp-channels` فهو حتمي عمدًا ولا يحتاج إلى
حساب Telegram أو Discord أو iMessage حقيقي. فهو يشغّل حاوية Gateway مزروعة،
ويبدأ حاوية ثانية تشغّل `openclaw mcp serve`، ثم
يتحقق من اكتشاف المحادثات الموجّهة، وقراءات النصوص، وبيانات تعريف المرفقات،
وسلوك طابور الأحداث الحية، وتوجيه الإرسال الصادر، وإشعارات القنوات +
الأذونات على نمط Claude عبر جسر stdio MCP الحقيقي. ويفحص فحص الإشعارات
إطارات stdio MCP الخام مباشرة بحيث يتحقق الفحص الدخاني مما يصدره الجسر
فعليًا، وليس فقط مما تعرِضه حزمة SDK معينة من عميل ما.

فحص يدوي بلغة عادية لخيط ACP (ليس في CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- احتفظ بهذا السكربت من أجل سير عمل الانحدار/التصحيح. قد تكون هناك حاجة إليه مرة أخرى للتحقق من توجيه خيوط ACP، لذا لا تحذفه.

متغيرات env مفيدة:

- `OPENCLAW_CONFIG_DIR=...` (الافتراضي: `~/.openclaw`) يُحمَّل إلى `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` (الافتراضي: `~/.openclaw/workspace`) يُحمَّل إلى `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` (الافتراضي: `~/.profile`) يُحمَّل إلى `/home/node/.profile` ويُستورد قبل تشغيل الاختبارات
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (الافتراضي: `~/.cache/openclaw/docker-cli-tools`) يُحمَّل إلى `/home/node/.npm-global` لتخزين تثبيتات CLI مؤقتًا داخل Docker
- تُحمَّل أدلة/ملفات مصادقة CLI الخارجية تحت `$HOME` بوضع القراءة فقط تحت `/host-auth...`، ثم تُنسخ إلى `/home/node/...` قبل بدء الاختبارات
  - الأدلة الافتراضية: `.minimax`
  - الملفات الافتراضية: `~/.codex/auth.json` و`~/.codex/config.toml` و`.claude.json` و`~/.claude/.credentials.json` و`~/.claude/settings.json` و`~/.claude/settings.local.json`
  - تركّب التشغيلات المضيقة للمزوّدين الأدلة/الملفات المطلوبة فقط والمستنتجة من `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - تجاوز ذلك يدويًا عبر `OPENCLAW_DOCKER_AUTH_DIRS=all` أو `OPENCLAW_DOCKER_AUTH_DIRS=none` أو قائمة مفصولة بفواصل مثل `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` لتضييق التشغيل
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...` لتصفية الموفّرين داخل الحاوية
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لضمان أن تأتي بيانات الاعتماد من مخزن الملف الشخصي (وليس env)
- `OPENCLAW_OPENWEBUI_MODEL=...` لاختيار النموذج الذي تعرِضه gateway لفحص Open WebUI الدخاني
- `OPENCLAW_OPENWEBUI_PROMPT=...` لتجاوز prompt فحص nonce المستخدم بواسطة فحص Open WebUI الدخاني
- `OPENWEBUI_IMAGE=...` لتجاوز وسم صورة Open WebUI المثبتة

## سلامة الوثائق

شغّل فحوص الوثائق بعد تعديلها: `pnpm check:docs`.
وشغّل تحقق الروابط والمراسي الكامل في Mintlify عندما تحتاج أيضًا إلى فحوص عناوين الصفحة الداخلية: `pnpm docs:check-links:anchors`.

## اختبارات الانحدار دون اتصال (آمنة لـ CI)

هذه اختبارات انحدار "لخط أنابيب حقيقي" من دون موفّرين حقيقيين:

- استدعاء أدوات gateway (OpenAI وهمي، gateway + agent loop حقيقيتان): `src/gateway/gateway.test.ts` (الحالة: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- معالج gateway (WS `wizard.start`/`wizard.next`، مع فرض كتابة config + auth): `src/gateway/gateway.test.ts` (الحالة: "runs wizard over ws and writes auth token config")

## تقييمات موثوقية العامل (Skills)

لدينا بالفعل بعض الاختبارات الآمنة لـ CI التي تتصرف مثل "تقييمات موثوقية العامل":

- استدعاء أدوات وهمي عبر gateway + agent loop الحقيقيتين (`src/gateway/gateway.test.ts`).
- تدفقات wizard من الطرف إلى الطرف التي تتحقق من أسلاك الجلسة وتأثيرات الإعدادات (`src/gateway/gateway.test.ts`).

ما لا يزال مفقودًا بالنسبة إلى Skills (راجع [Skills](/ar/tools/skills)):

- **اتخاذ القرار:** عندما تُدرج Skills في التوجيه، هل يختار العامل Skill الصحيحة (أو يتجنب غير ذات الصلة)؟
- **الامتثال:** هل يقرأ العامل `SKILL.md` قبل الاستخدام ويتبع الخطوات/الوسائط المطلوبة؟
- **عقود سير العمل:** سيناريوهات متعددة المنعطفات تؤكد ترتيب الأدوات، واستمرار سجل الجلسة، وحدود sandbox.

يجب أن تظل التقييمات المستقبلية حتمية أولًا:

- مشغل سيناريوهات يستخدم موفّرين وهميين لتأكيد استدعاءات الأدوات + ترتيبها، وقراءات ملفات Skills، وأسلاك الجلسة.
- مجموعة صغيرة من السيناريوهات المركزة على Skills (استخدام مقابل تجنّب، والبوابات، وحقن التوجيه).
- تقييمات live اختيارية (محكومة بالبيئة ومشتركة بالاشتراك) فقط بعد اكتمال الجناح الآمن لـ CI.

## اختبارات العقود (شكل plugin وchannel)

تتحقق اختبارات العقود من أن كل plugin وchannel مسجلين يتوافقان مع
عقد الواجهة الخاص بهما. وهي تتكرر على كل plugins المكتشفة وتشغّل مجموعة من
التحققات الخاصة بالشكل والسلوك. يتخطى مسار unit الافتراضي في `pnpm test`
هذه الملفات المشتركة الخاصة بالحدود والفحوص الدخانية عمدًا؛ شغّل أوامر العقود
صراحةً عندما تلمس أسطح channel أو provider المشتركة.

### الأوامر

- جميع العقود: `pnpm test:contracts`
- عقود القنوات فقط: `pnpm test:contracts:channels`
- عقود الموفّرين فقط: `pnpm test:contracts:plugins`

### عقود القنوات

تقع في `src/channels/plugins/contracts/*.contract.test.ts`:

- **plugin** - الشكل الأساسي لـ plugin (id، والاسم، والقدرات)
- **setup** - عقد معالج الإعداد
- **session-binding** - سلوك ربط الجلسة
- **outbound-payload** - بنية حمولة الرسالة
- **inbound** - معالجة الرسائل الواردة
- **actions** - معالجات إجراءات القناة
- **threading** - التعامل مع معرّف الخيط
- **directory** - واجهة API الخاصة بالدليل/القائمة
- **group-policy** - فرض سياسة المجموعات

### عقود حالة الموفّر

تقع في `src/plugins/contracts/*.contract.test.ts`.

- **status** - فحوص حالة القنوات
- **registry** - شكل سجل plugin

### عقود الموفّر

تقع في `src/plugins/contracts/*.contract.test.ts`:

- **auth** - عقد تدفق المصادقة
- **auth-choice** - اختيار/تحديد المصادقة
- **catalog** - واجهة API لفهرس النماذج
- **discovery** - اكتشاف plugin
- **loader** - تحميل plugin
- **runtime** - وقت تشغيل الموفّر
- **shape** - شكل/واجهة plugin
- **wizard** - معالج الإعداد

### متى تُشغَّل

- بعد تغيير تصديرات `plugin-sdk` أو المسارات الفرعية الخاصة به
- بعد إضافة plugin قناة أو موفّر أو تعديلها
- بعد إعادة هيكلة تسجيل plugin أو اكتشافها

تعمل اختبارات العقود في CI ولا تتطلب مفاتيح API حقيقية.

## إضافة اختبارات انحدار (إرشادات)

عندما تصلح مشكلة موفّر/نموذج تم اكتشافها في live:

- أضف اختبار انحدار آمنًا لـ CI إن أمكن (موفّر وهمي/مزيف، أو التقاط تحويل شكل الطلب الدقيق)
- إذا كانت المشكلة حية بطبيعتها فقط (حدود المعدل، وسياسات المصادقة)، فاجعل اختبار live ضيقًا واختياريًا عبر متغيرات env
- فضّل استهداف أصغر طبقة تلتقط الخطأ:
  - خطأ في تحويل/إعادة تشغيل طلب الموفّر → اختبار النماذج المباشرة
  - خطأ في خط أنابيب جلسة/sجل/أداة gateway → فحص gateway live دخاني أو اختبار gateway وهمي وآمن لـ CI
- حاجز اجتياز SecretRef:
  - يشتق `src/secrets/exec-secret-ref-id-parity.test.ts` هدفًا نموذجيًا واحدًا لكل فئة SecretRef من بيانات تعريف السجل (`listSecretTargetRegistryEntries()`)، ثم يتحقق من رفض معرّفات exec الخاصة بمقاطع الاجتياز.
  - إذا أضفت عائلة هدف SecretRef جديدة من نوع `includeInPlan` في `src/secrets/target-registry-data.ts`، فحدّث `classifyTargetClass` في ذلك الاختبار. يفشل الاختبار عمدًا عند وجود معرّفات أهداف غير مصنفة حتى لا يمكن تخطي الفئات الجديدة بصمت.
