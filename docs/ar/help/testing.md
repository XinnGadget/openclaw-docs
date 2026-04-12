---
read_when:
    - تشغيل الاختبارات محليًا أو في CI
    - إضافة اختبارات تراجعية لأخطاء النماذج/المزوّدين
    - تصحيح سلوك Gateway + الوكيل
summary: 'حزمة الاختبار: أجنحة unit/e2e/live، ومشغلات Docker، وما الذي يغطيه كل اختبار'
title: الاختبار
x-i18n:
    generated_at: "2026-04-12T23:28:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: a66ea672c386094ab4a8035a082c8a85d508a14301ad44b628d2a10d9cec3a52
    source_path: help/testing.md
    workflow: 15
---

# الاختبار

يحتوي OpenClaw على ثلاث مجموعات Vitest (unit/integration وe2e وlive) بالإضافة إلى مجموعة صغيرة من مشغلات Docker.

هذا المستند هو دليل «كيف نختبر»:

- ما الذي تغطيه كل مجموعة (وما الذي لا تغطيه عمدًا)
- الأوامر التي يجب تشغيلها لسيناريوهات العمل الشائعة (محليًا، قبل الدفع، التصحيح)
- كيف تكتشف اختبارات live بيانات الاعتماد وتختار النماذج/المزوّدين
- كيفية إضافة اختبارات تراجعية لمشكلات النماذج/المزوّدين في العالم الحقيقي

## البدء السريع

في معظم الأيام:

- البوابة الكاملة (متوقعة قبل الدفع): `pnpm build && pnpm check && pnpm test`
- تشغيل أسرع للمجموعة الكاملة محليًا على جهاز بموارد جيدة: `pnpm test:max`
- حلقة مراقبة Vitest مباشرة: `pnpm test:watch`
- الاستهداف المباشر للملفات يوجّه الآن أيضًا مسارات الامتدادات/القنوات: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- فضّل التشغيلات الموجّهة أولًا عندما تعمل على تكرار إصلاح فشل واحد.
- موقع QA مدعوم بـ Docker: `pnpm qa:lab:up`
- مسار QA مدعوم بآلة Linux افتراضية: `pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

عندما تلمس الاختبارات أو تريد ثقة إضافية:

- بوابة التغطية: `pnpm test:coverage`
- مجموعة E2E: `pnpm test:e2e`

عند تصحيح مزوّدين/نماذج حقيقية (يتطلب بيانات اعتماد حقيقية):

- مجموعة Live (النماذج + فحوصات أدوات/صور Gateway): `pnpm test:live`
- استهدف ملف live واحدًا بهدوء: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

نصيحة: عندما تحتاج فقط إلى حالة فشل واحدة، فالأفضل تضييق اختبارات live باستخدام متغيرات بيئة allowlist الموضحة أدناه.

## المشغلات الخاصة بـ QA

توجد هذه الأوامر إلى جانب مجموعات الاختبار الرئيسية عندما تحتاج إلى واقعية qa-lab:

- `pnpm openclaw qa suite`
  - يشغّل سيناريوهات QA المدعومة من المستودع مباشرة على المضيف.
  - يشغّل عدة سيناريوهات محددة بالتوازي افتراضيًا مع عمّال Gateway معزولين، حتى 64 عاملًا أو بعدد السيناريوهات المحدد. استخدم `--concurrency <count>` لضبط عدد العمّال، أو `--concurrency 1` لمسار التسلسل الأقدم.
- `pnpm openclaw qa suite --runner multipass`
  - يشغّل مجموعة QA نفسها داخل آلة Linux افتراضية مؤقتة من Multipass.
  - يحافظ على سلوك اختيار السيناريو نفسه الخاص بـ `qa suite` على المضيف.
  - يعيد استخدام علامات اختيار المزوّد/النموذج نفسها الخاصة بـ `qa suite`.
  - تمرّر تشغيلات live مدخلات مصادقة QA المدعومة التي تكون عملية للضيف:
    مفاتيح المزوّد المعتمدة على env، ومسار إعداد مزوّد QA live، و`CODEX_HOME` عند وجوده.
  - يجب أن تبقى أدلة الإخراج تحت جذر المستودع حتى يتمكن الضيف من الكتابة مجددًا عبر مساحة العمل المركّبة.
  - يكتب تقرير QA المعتاد + الملخص بالإضافة إلى سجلات Multipass تحت
    `.artifacts/qa-e2e/...`.
- `pnpm qa:lab:up`
  - يبدأ موقع QA المدعوم بـ Docker لأعمال QA بأسلوب المشغّل.
- `pnpm openclaw qa matrix`
  - يشغّل مسار Matrix live QA على خادم Tuwunel مؤقت مدعوم بـ Docker.
  - يجهّز ثلاثة مستخدمين مؤقتين لـ Matrix (`driver` و`sut` و`observer`) بالإضافة إلى غرفة خاصة واحدة، ثم يبدأ عملية Gateway فرعية لـ QA باستخدام Plugin Matrix الحقيقي كنقل SUT.
  - يستخدم صورة Tuwunel المستقرة المثبتة `ghcr.io/matrix-construct/tuwunel:v1.5.1` افتراضيًا. استبدلها عبر `OPENCLAW_QA_MATRIX_TUWUNEL_IMAGE` عندما تحتاج إلى اختبار صورة مختلفة.
  - يكتب تقرير Matrix QA وملخصًا وartifact للأحداث المُلاحظة تحت `.artifacts/qa-e2e/...`.
- `pnpm openclaw qa telegram`
  - يشغّل مسار Telegram live QA على مجموعة خاصة حقيقية باستخدام رمزي bot الخاصين بـ driver وSUT من env.
  - يتطلب `OPENCLAW_QA_TELEGRAM_GROUP_ID` و`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` و`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`. يجب أن يكون معرّف المجموعة هو معرّف دردشة Telegram الرقمي.
  - يتطلب روبوتين مختلفين داخل المجموعة الخاصة نفسها، مع كون روبوت SUT يوفّر اسم مستخدم Telegram.
  - من أجل ملاحظة مستقرة بين bots، فعّل Bot-to-Bot Communication Mode في `@BotFather` لكلا الروبوتين وتأكد من أن روبوت driver يمكنه ملاحظة حركة bots داخل المجموعة.
  - يكتب تقرير Telegram QA وملخصًا وartifact للرسائل المُلاحظة تحت `.artifacts/qa-e2e/...`.

تتشارك مسارات النقل الحية عقدًا قياسيًا واحدًا حتى لا تنجرف وسائل النقل الجديدة:

يبقى `qa-channel` مجموعة QA الاصطناعية الواسعة وليس جزءًا من مصفوفة تغطية النقل الحي.

| المسار | Canary | بوابة الإشارة | حظر allowlist | رد على المستوى الأعلى | استئناف بعد إعادة التشغيل | متابعة الخيط | عزل الخيط | ملاحظة التفاعلات | أمر المساعدة |
| ------ | ------ | -------------- | ------------- | ---------------------- | -------------------------- | ------------ | ---------- | ---------------- | ------------ |
| Matrix   | x      | x              | x             | x                      | x                          | x            | x          | x                |              |
| Telegram | x      |                |               |                        |                            |              |            |                  | x            |

### إضافة قناة إلى QA

تتطلب إضافة قناة إلى نظام QA المعتمد على Markdown أمرين فقط بالضبط:

1. محول نقل للقناة.
2. حزمة سيناريوهات تختبر عقد القناة.

لا تضف مشغّل QA خاصًا بقناة عندما يكون بإمكان المشغّل المشترك `qa-lab` تولي التدفق.

يتولى `qa-lab` الآليات المشتركة:

- بدء المجموعة وإنهاؤها
- توازي العمّال
- كتابة artifacts
- توليد التقارير
- تنفيذ السيناريوهات
- الأسماء المستعارة التوافقية لسيناريوهات `qa-channel` الأقدم

ويتولى محول القناة عقد النقل:

- كيفية إعداد Gateway لذلك النقل
- كيفية التحقق من الجاهزية
- كيفية حقن الأحداث الواردة
- كيفية ملاحظة الرسائل الصادرة
- كيفية كشف النصوص وحالة النقل المعيارية
- كيفية تنفيذ الإجراءات المدعومة بالنقل
- كيفية التعامل مع إعادة الضبط أو التنظيف الخاص بالنقل

الحد الأدنى لاعتماد قناة جديدة هو:

1. تنفيذ محول النقل على واجهة `qa-lab` المشتركة.
2. تسجيل المحول في سجل النقل.
3. إبقاء الآليات الخاصة بالنقل داخل المحول أو إطار القناة.
4. تأليف أو تكييف سيناريوهات Markdown تحت `qa/scenarios/`.
5. استخدام مساعدات السيناريو العامة للسيناريوهات الجديدة.
6. الحفاظ على عمل الأسماء المستعارة التوافقية الحالية ما لم يكن المستودع ينفذ ترحيلًا مقصودًا.

قاعدة القرار صارمة:

- إذا أمكن التعبير عن السلوك مرة واحدة في `qa-lab`، فضعه في `qa-lab`.
- إذا كان السلوك يعتمد على نقل قناة واحدة، فأبقِه في ذلك المحول أو إطار Plugin.
- إذا احتاج سيناريو إلى قدرة جديدة يمكن لأكثر من قناة استخدامها، فأضف مساعدًا عامًا بدلًا من فرع خاص بقناة في `suite.ts`.
- إذا كان السلوك ذا معنى لنقل واحد فقط، فأبقِ السيناريو خاصًا بذلك النقل وصرّح بذلك بوضوح في عقد السيناريو.

أسماء المساعدات العامة المفضلة للسيناريوهات الجديدة هي:

- `waitForTransportReady`
- `waitForChannelReady`
- `injectInboundMessage`
- `injectOutboundMessage`
- `waitForTransportOutboundMessage`
- `waitForChannelOutboundMessage`
- `waitForNoTransportOutbound`
- `getTransportSnapshot`
- `readTransportMessage`
- `readTransportTranscript`
- `formatTransportTranscript`
- `resetTransport`

ولا تزال الأسماء المستعارة التوافقية متاحة للسيناريوهات الحالية، بما في ذلك:

- `waitForQaChannelReady`
- `waitForOutboundMessage`
- `waitForNoOutbound`
- `formatConversationTranscript`
- `resetBus`

يجب أن تستخدم الأعمال الجديدة الخاصة بالقنوات أسماء المساعدات العامة.
توجد الأسماء المستعارة التوافقية لتجنب ترحيل شامل دفعة واحدة، وليس كنموذج
لتأليف سيناريوهات جديدة.

## مجموعات الاختبار (ما الذي يعمل وأين)

فكّر في المجموعات على أنها «تزداد واقعية» (وتزداد هشاشة/كلفة):

### Unit / integration (الافتراضي)

- الأمر: `pnpm test`
- الإعداد: عشر تشغيلات shards متسلسلة (`vitest.full-*.config.ts`) عبر مشاريع Vitest المحددة الحالية
- الملفات: جرد core/unit تحت `src/**/*.test.ts` و`packages/**/*.test.ts` و`test/**/*.test.ts` واختبارات `ui` الخاصة بـ node والمسموح بها والتي يغطيها `vitest.unit.config.ts`
- النطاق:
  - اختبارات unit خالصة
  - اختبارات تكامل داخل العملية (مصادقة gateway، والتوجيه، والأدوات، والتحليل، والإعداد)
  - اختبارات تراجعية حتمية للأخطاء المعروفة
- التوقعات:
  - تُشغَّل في CI
  - لا تتطلب مفاتيح حقيقية
  - يجب أن تكون سريعة ومستقرة
- ملاحظة المشاريع:
  - أصبح `pnpm test` غير الموجَّه يشغّل الآن أحد عشر إعداد shard أصغر (`core-unit-src` و`core-unit-security` و`core-unit-ui` و`core-unit-support` و`core-support-boundary` و`core-contracts` و`core-bundled` و`core-runtime` و`agentic` و`auto-reply` و`extensions`) بدلًا من عملية root-project أصلية عملاقة واحدة. وهذا يقلّل ذروة RSS على الأجهزة المحمّلة ويمنع أعمال auto-reply/extension من تجويع المجموعات غير المرتبطة.
  - لا يزال `pnpm test --watch` يستخدم مخطط المشاريع الأصلي في الجذر من `vitest.config.ts`، لأن حلقة watch متعددة الـ shards غير عملية.
  - يوجّه `pnpm test` و`pnpm test:watch` و`pnpm test:perf:imports` أهداف الملفات/الأدلة الصريحة عبر المسارات المحددة أولًا، لذا فإن `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` يتجنب كلفة بدء root project الكامل.
  - يوسّع `pnpm test:changed` مسارات git المتغيرة إلى المسارات المحددة نفسها عندما يقتصر الفرق على ملفات source/test القابلة للتوجيه؛ بينما تعود تعديلات config/setup إلى إعادة تشغيل root-project الواسعة.
  - تُوجَّه اختبارات unit الخفيفة من حيث الاستيراد الخاصة بـ agents وcommands وplugins ومساعدات auto-reply و`plugin-sdk` ومناطق الأدوات الخالصة المشابهة عبر مسار `unit-fast` الذي يتجاوز `test/setup-openclaw-runtime.ts`؛ بينما تبقى الملفات ذات الحالة أو الثقيلة وقت التشغيل على المسارات الحالية.
  - تُعيَّن أيضًا بعض ملفات source المساعدة المحددة في `plugin-sdk` و`commands` في التشغيلات ذات النمط changed إلى اختبارات شقيقة صريحة في تلك المسارات الخفيفة، بحيث تتجنب تعديلات المساعدات إعادة تشغيل المجموعة الثقيلة الكاملة لذلك الدليل.
  - أصبح لدى `auto-reply` الآن ثلاث مجموعات مخصصة: مساعدات core العليا، واختبارات التكامل العليا `reply.*`، والشجرة الفرعية `src/auto-reply/reply/**`. وهذا يُبقي أعمال reply harness الأثقل بعيدًا عن اختبارات الحالة/المقاطع/الرموز الرخيصة.
- ملاحظة المشغّل المضمّن:
  - عندما تغيّر مدخلات اكتشاف أدوات الرسائل أو سياق وقت تشغيل Compaction،
    حافظ على مستويي التغطية معًا.
  - أضف اختبارات تراجعية مركزة للمساعدات عند حدود التوجيه/التطبيع الخالصة.
  - وحافظ أيضًا على سلامة مجموعات تكامل المشغّل المضمّن:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`،
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`، و
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - تتحقق هذه المجموعات من أن المعرّفات المحددة وسلوك Compaction لا يزالان يمران عبر المسارات الفعلية `run.ts` / `compact.ts`؛ واختبارات المساعدات وحدها ليست بديلًا كافيًا لهذه المسارات التكاملية.
- ملاحظة الـ pool:
  - أصبح إعداد Vitest الأساسي يستخدم `threads` افتراضيًا.
  - كما يثبّت إعداد Vitest المشترك `isolate: false` ويستخدم المشغّل غير المعزول عبر مشاريع الجذر وتهيئات e2e وlive.
  - يحتفظ مسار UI في الجذر بإعداد `jsdom` والمُحسِّن الخاص به، لكنه يعمل الآن أيضًا على المشغّل المشترك غير المعزول.
  - يرث كل shard في `pnpm test` إعدادات `threads` + `isolate: false` نفسها من إعداد Vitest المشترك.
  - يضيف مشغّل `scripts/run-vitest.mjs` المشترك الآن أيضًا `--no-maglev` افتراضيًا لعمليات Node الفرعية الخاصة بـ Vitest لتقليل تذبذب ترجمة V8 أثناء التشغيلات المحلية الكبيرة. اضبط `OPENCLAW_VITEST_ENABLE_MAGLEV=1` إذا كنت بحاجة إلى المقارنة مع سلوك V8 القياسي.
- ملاحظة التكرار المحلي السريع:
  - يوجّه `pnpm test:changed` عبر المسارات المحددة عندما تطابق المسارات المتغيرة مجموعة أصغر بشكل واضح.
  - يحافظ `pnpm test:max` و`pnpm test:changed:max` على سلوك التوجيه نفسه، ولكن مع حد أعلى أكبر للعمّال.
  - أصبح التوسّع التلقائي المحلي للعمّال محافظًا عمدًا الآن، ويتراجع أيضًا عندما يكون متوسط حمل المضيف مرتفعًا أصلًا، بحيث تتسبب تشغيلات Vitest المتزامنة المتعددة في ضرر أقل افتراضيًا.
  - يعلّم إعداد Vitest الأساسي المشاريع/ملفات الإعداد كـ `forceRerunTriggers` حتى تبقى إعادة التشغيل في وضع changed صحيحة عند تغيّر توصيل الاختبارات.
  - يحافظ الإعداد على تفعيل `OPENCLAW_VITEST_FS_MODULE_CACHE` على المضيفين المدعومين؛ اضبط `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` إذا أردت موقع cache صريحًا واحدًا لأغراض التحليل المباشر.
- ملاحظة تصحيح الأداء:
  - يفعّل `pnpm test:perf:imports` تقارير مدة الاستيراد في Vitest بالإضافة إلى مخرجات تفصيل الاستيراد.
  - يقيّد `pnpm test:perf:imports:changed` العرض التحليلي نفسه إلى الملفات التي تغيّرت منذ `origin/main`.
- يقارن `pnpm test:perf:changed:bench -- --ref <git-ref>` بين `test:changed` الموجَّه والمسار الأصلي لـ root-project لذلك الفرق الملتزم ويطبع زمن التنفيذ بالإضافة إلى أقصى RSS على macOS.
- يختبر `pnpm test:perf:changed:bench -- --worktree` الشجرة الحالية غير النظيفة عبر توجيه قائمة الملفات المتغيرة خلال `scripts/test-projects.mjs` وإعداد Vitest في الجذر.
  - يكتب `pnpm test:perf:profile:main` ملف تعريف CPU للخيط الرئيسي لزمن بدء Vitest/Vite وكلفة التحويل.
  - ويكتب `pnpm test:perf:profile:runner` ملفات تعريف CPU+heap الخاصة بالمشغّل لمجموعة unit مع تعطيل التوازي على مستوى الملفات.

### E2E (اختبار smoke لـ gateway)

- الأمر: `pnpm test:e2e`
- الإعداد: `vitest.e2e.config.ts`
- الملفات: `src/**/*.e2e.test.ts` و`test/**/*.e2e.test.ts`
- الإعدادات الافتراضية لوقت التشغيل:
  - يستخدم `threads` في Vitest مع `isolate: false`، بما يتطابق مع بقية المستودع.
  - يستخدم عمّالًا تكيفيين (في CI: حتى 2، ومحليًا: 1 افتراضيًا).
  - يعمل في الوضع الصامت افتراضيًا لتقليل كلفة إدخال/إخراج وحدة التحكم.
- تجاوزات مفيدة:
  - `OPENCLAW_E2E_WORKERS=<n>` لفرض عدد العمّال (بحد أقصى 16).
  - `OPENCLAW_E2E_VERBOSE=1` لإعادة تفعيل إخراج وحدة التحكم المفصل.
- النطاق:
  - سلوك end-to-end متعدد نُسخ gateway
  - أسطح WebSocket/HTTP، وإقران node، والشبكات الأثقل
- التوقعات:
  - يُشغَّل في CI (عند تفعيله في المسار)
  - لا يتطلب مفاتيح حقيقية
  - يحتوي على أجزاء متحركة أكثر من اختبارات unit (وقد يكون أبطأ)

### E2E: اختبار smoke للواجهة الخلفية OpenShell

- الأمر: `pnpm test:e2e:openshell`
- الملف: `test/openshell-sandbox.e2e.test.ts`
- النطاق:
  - يبدأ Gateway معزولًا لـ OpenShell على المضيف عبر Docker
  - ينشئ sandbox من Dockerfile محلي مؤقت
  - يختبر الواجهة الخلفية OpenShell في OpenClaw عبر `sandbox ssh-config` الحقيقي وتنفيذ SSH
  - يتحقق من سلوك نظام الملفات canonical عن بُعد عبر جسر sandbox fs
- التوقعات:
  - اختياري فقط؛ وليس جزءًا من تشغيل `pnpm test:e2e` الافتراضي
  - يتطلب CLI محليًا لـ `openshell` بالإضافة إلى Docker daemon عامل
  - يستخدم `HOME` / `XDG_CONFIG_HOME` معزولين، ثم يدمّر Gateway الاختباري وsandbox
- تجاوزات مفيدة:
  - `OPENCLAW_E2E_OPENSHELL=1` لتفعيل الاختبار عند تشغيل مجموعة e2e الأوسع يدويًا
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell` للإشارة إلى ملف CLI ثنائي غير افتراضي أو script wrapper

### Live (مزوّدون حقيقيون + نماذج حقيقية)

- الأمر: `pnpm test:live`
- الإعداد: `vitest.live.config.ts`
- الملفات: `src/**/*.live.test.ts`
- الافتراضي: **مفعّل** بواسطة `pnpm test:live` (يضبط `OPENCLAW_LIVE_TEST=1`)
- النطاق:
  - «هل يعمل هذا المزوّد/النموذج فعلًا _اليوم_ باستخدام بيانات اعتماد حقيقية؟»
  - التقاط تغيّرات تنسيق المزوّد، وخصائص استدعاء الأدوات، ومشكلات المصادقة، وسلوك حدود المعدل
- التوقعات:
  - غير مستقر في CI بطبيعته (شبكات حقيقية، وسياسات مزوّدين حقيقية، وحصص، وانقطاعات)
  - يكلّف مالًا / يستهلك حدود المعدل
  - يُفضّل تشغيل مجموعات فرعية مضيقة بدلًا من تشغيل «كل شيء»
- تستورد تشغيلات live الملف `~/.profile` لالتقاط مفاتيح API الناقصة.
- افتراضيًا، تعزل تشغيلات live أيضًا `HOME` وتنسخ مواد config/auth إلى home اختباري مؤقت حتى لا تتمكن تجهيزات unit من تعديل `~/.openclaw` الحقيقي.
- اضبط `OPENCLAW_LIVE_USE_REAL_HOME=1` فقط عندما تحتاج عمدًا إلى أن تستخدم اختبارات live دليل home الحقيقي.
- أصبح `pnpm test:live` يستخدم الآن وضعًا أهدأ افتراضيًا: فهو يحتفظ بمخرجات التقدم `[live] ...`، لكنه يخفي إشعار `~/.profile` الإضافي ويكتم سجلات تمهيد gateway وضجيج Bonjour. اضبط `OPENCLAW_LIVE_TEST_QUIET=0` إذا أردت سجلات البدء الكاملة مجددًا.
- تدوير مفاتيح API (خاص بكل مزوّد): اضبط `*_API_KEYS` بتنسيق الفاصلة/الفاصلة المنقوطة أو `*_API_KEY_1` و`*_API_KEY_2` (مثل `OPENAI_API_KEYS` و`ANTHROPIC_API_KEYS` و`GEMINI_API_KEYS`) أو تجاوزًا لكل live عبر `OPENCLAW_LIVE_*_KEY`؛ وتعيد الاختبارات المحاولة عند استجابات حدود المعدل.
- مخرجات التقدم/Heartbeat:
  - تصدر مجموعات live الآن أسطر التقدم إلى stderr بحيث تكون استدعاءات المزوّد الطويلة مرئية على أنها نشطة حتى عندما يكون التقاط وحدة التحكم في Vitest هادئًا.
  - يعطّل `vitest.live.config.ts` اعتراض وحدة التحكم في Vitest بحيث تتدفق أسطر تقدم المزوّد/gateway فورًا أثناء تشغيلات live.
  - اضبط Heartbeat للنموذج المباشر عبر `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - واضبط Heartbeat الخاص بـ gateway/probe عبر `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## أي مجموعة يجب أن أشغّل؟

استخدم جدول القرار هذا:

- عند تعديل المنطق/الاختبارات: شغّل `pnpm test` (و`pnpm test:coverage` إذا غيّرت الكثير)
- عند لمس شبكات gateway / بروتوكول WS / الإقران: أضف `pnpm test:e2e`
- عند تصحيح «البوت الخاص بي متوقف» / حالات الفشل الخاصة بالمزوّد / استدعاء الأدوات: شغّل `pnpm test:live` على مجموعة فرعية مضيقة

## Live: مسح قدرات Android node

- الاختبار: `src/gateway/android-node.capabilities.live.test.ts`
- السكربت: `pnpm android:test:integration`
- الهدف: استدعاء **كل أمر مُعلَن عنه حاليًا** بواسطة Android node متصل والتحقق من سلوك عقد الأمر.
- النطاق:
  - إعداد مسبق/يدوي (لا تقوم المجموعة بتثبيت التطبيق أو تشغيله أو إقرانه).
  - تحقق `node.invoke` في gateway أمرًا بأمر لـ Android node المحدد.
- الإعداد المسبق المطلوب:
  - أن يكون تطبيق Android متصلًا ومقترنًا بـ gateway مسبقًا.
  - إبقاء التطبيق في الواجهة الأمامية.
  - منح الأذونات/موافقة الالتقاط للقدرات التي تتوقع نجاحها.
- تجاوزات الهدف الاختيارية:
  - `OPENCLAW_ANDROID_NODE_ID` أو `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- تفاصيل إعداد Android الكاملة: [تطبيق Android](/ar/platforms/android)

## Live: اختبار smoke للنماذج (مفاتيح profile)

تنقسم اختبارات live إلى طبقتين حتى نتمكن من عزل حالات الفشل:

- يخبرنا «النموذج المباشر» ما إذا كان المزوّد/النموذج قادرًا على الرد أصلًا باستخدام المفتاح المحدد.
- يخبرنا «اختبار smoke لـ gateway» ما إذا كان خط أنابيب gateway+agent الكامل يعمل لهذا النموذج (الجلسات، والسجل، والأدوات، وسياسة sandbox، وما إلى ذلك).

### الطبقة 1: إكمال مباشر للنموذج (من دون gateway)

- الاختبار: `src/agents/models.profiles.live.test.ts`
- الهدف:
  - تعداد النماذج المكتشفة
  - استخدام `getApiKeyForModel` لتحديد النماذج التي لديك بيانات اعتماد لها
  - تشغيل إكمال صغير لكل نموذج (واختبارات تراجعية موجّهة عند الحاجة)
- كيفية التفعيل:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` عند استدعاء Vitest مباشرة)
- اضبط `OPENCLAW_LIVE_MODELS=modern` (أو `all`، وهو اسم مستعار لـ modern) لتشغيل هذه المجموعة فعليًا؛ وإلا فسيتم تخطيها للحفاظ على تركيز `pnpm test:live` على اختبار smoke الخاص بـ gateway
- كيفية اختيار النماذج:
  - `OPENCLAW_LIVE_MODELS=modern` لتشغيل allowlist الحديثة (`Opus/Sonnet 4.6+` و`GPT-5.x + Codex` و`Gemini 3` و`GLM 4.7` و`MiniMax M2.7` و`Grok 4`)
  - `OPENCLAW_LIVE_MODELS=all` هو اسم مستعار لـ allowlist الحديثة
  - أو `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (allowlist مفصولة بفواصل)
  - تستخدم عمليات المسح الحديثة/الكلية حدًا منسقًا عالي الإشارة افتراضيًا؛ اضبط `OPENCLAW_LIVE_MAX_MODELS=0` لإجراء مسح حديث شامل أو رقمًا موجبًا لحد أصغر.
- كيفية اختيار المزوّدين:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (allowlist مفصولة بفواصل)
- من أين تأتي المفاتيح:
  - افتراضيًا: من مخزن profile وبدائل env
  - اضبط `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض **مخزن profile** فقط
- سبب وجود هذا:
  - يفصل بين «واجهة API الخاصة بالمزوّد معطلة / المفتاح غير صالح» و«خط أنابيب gateway agent معطل»
  - يحتوي على اختبارات تراجعية صغيرة ومعزولة (مثال: إعادة تشغيل reasoning flows واستدعاء الأدوات في OpenAI Responses/Codex Responses)

### الطبقة 2: اختبار smoke لـ Gateway + وكيل التطوير (ما الذي يفعله "@openclaw" فعليًا)

- الاختبار: `src/gateway/gateway-models.profiles.live.test.ts`
- الهدف:
  - تشغيل Gateway داخل العملية
  - إنشاء/تعديل جلسة `agent:dev:*` (مع تجاوز النموذج لكل تشغيل)
  - التكرار عبر النماذج التي لها مفاتيح والتحقق من:
    - استجابة «ذات معنى» (من دون أدوات)
    - نجاح استدعاء أداة حقيقي (فحص `read`)
    - فحوصات أدوات إضافية اختيارية (فحص `exec+read`)
    - استمرار عمل مسارات OpenAI التراجعية (استدعاء أداة فقط ← متابعة)
- تفاصيل الفحوصات (حتى تتمكن من شرح الإخفاقات بسرعة):
  - فحص `read`: يكتب الاختبار ملف nonce في مساحة العمل ويطلب من الوكيل `read` قراءته ثم إعادة nonce.
  - فحص `exec+read`: يطلب الاختبار من الوكيل استخدام `exec` لكتابة nonce في ملف مؤقت، ثم `read` لقراءته مجددًا.
  - فحص الصورة: يرفق الاختبار صورة PNG مُولَّدة (قطة + رمز عشوائي) ويتوقع من النموذج أن يعيد `cat <CODE>`.
  - مرجع التنفيذ: `src/gateway/gateway-models.profiles.live.test.ts` و`src/gateway/live-image-probe.ts`.
- كيفية التفعيل:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` عند استدعاء Vitest مباشرة)
- كيفية اختيار النماذج:
  - الافتراضي: allowlist حديثة (`Opus/Sonnet 4.6+` و`GPT-5.x + Codex` و`Gemini 3` و`GLM 4.7` و`MiniMax M2.7` و`Grok 4`)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` هو اسم مستعار للـ allowlist الحديثة
  - أو اضبط `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (أو قائمة مفصولة بفواصل) للتضييق
  - تستخدم عمليات المسح الحديثة/الكلية الخاصة بـ gateway حدًا منسقًا عالي الإشارة افتراضيًا؛ اضبط `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0` لإجراء مسح حديث شامل أو رقمًا موجبًا لحد أصغر.
- كيفية اختيار المزوّدين (لتجنب «كل شيء في OpenRouter»):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (allowlist مفصولة بفواصل)
- تكون فحوصات الأدوات + الصور مفعّلة دائمًا في هذا الاختبار live:
  - فحص `read` + فحص `exec+read` (ضغط على الأدوات)
  - يعمل فحص الصورة عندما يعلن النموذج دعمه لإدخال الصور
  - التدفق (على مستوى عالٍ):
    - يولّد الاختبار صورة PNG صغيرة تحتوي على `CAT` + رمز عشوائي (`src/gateway/live-image-probe.ts`)
    - يرسلها عبر `agent` باستخدام `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - يحلل Gateway المرفقات إلى `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - يمرر الوكيل المضمّن رسالة مستخدم متعددة الوسائط إلى النموذج
    - التحقق: تحتوي الاستجابة على `cat` + الرمز (مع سماح OCR بأخطاء طفيفة)

نصيحة: لمعرفة ما يمكنك اختباره على جهازك (ومعرّفات `provider/model` الدقيقة)، شغّل:

```bash
openclaw models list
openclaw models list --json
```

## Live: اختبار smoke للواجهة الخلفية CLI (Claude أو Codex أو Gemini أو CLI محلي آخر)

- الاختبار: `src/gateway/gateway-cli-backend.live.test.ts`
- الهدف: التحقق من خط أنابيب Gateway + الوكيل باستخدام واجهة خلفية CLI محلية، من دون لمس الإعداد الافتراضي الخاص بك.
- توجد إعدادات smoke الافتراضية الخاصة بكل واجهة خلفية في تعريف `cli-backend.ts` التابع للامتداد المالك.
- التفعيل:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` عند استدعاء Vitest مباشرة)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- الإعدادات الافتراضية:
  - المزوّد/النموذج الافتراضي: `claude-cli/claude-sonnet-4-6`
  - يأتي سلوك الأمر/المعاملات/الصورة من بيانات Plugin الوصفية الخاصة بواجهة CLI الخلفية المالكة.
- التجاوزات (اختيارية):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` لإرسال مرفق صورة حقيقي (تُحقن المسارات داخل الموجه).
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` لتمرير مسارات ملفات الصور كمعاملات CLI بدلًا من حقنها في الموجه.
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (أو `"list"`) للتحكم في كيفية تمرير معاملات الصور عند ضبط `IMAGE_ARG`.
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` لإرسال دور ثانٍ والتحقق من تدفق الاستئناف.
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0` لتعطيل فحص الاستمرارية الافتراضي داخل الجلسة نفسها من Claude Sonnet إلى Opus (اضبطه إلى `1` لفرض تفعيله عندما يدعم النموذج المحدد هدف تبديل).

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

وصفات Docker لمزوّد واحد:

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:claude-subscription
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

ملاحظات:

- يوجد مشغّل Docker في `scripts/test-live-cli-backend-docker.sh`.
- يشغّل اختبار smoke لواجهة CLI الخلفية الحية داخل صورة Docker الخاصة بالمستودع كمستخدم `node` غير الجذر.
- يحلّل بيانات smoke الوصفية الخاصة بـ CLI من الامتداد المالك، ثم يثبّت حزمة CLI الموافقة لنظام Linux (`@anthropic-ai/claude-code` أو `@openai/codex` أو `@google/gemini-cli`) في prefix قابل للكتابة ومخزن مؤقتًا عند `OPENCLAW_DOCKER_CLI_TOOLS_DIR` (الافتراضي: `~/.cache/openclaw/docker-cli-tools`).
- يتطلب `pnpm test:docker:live-cli-backend:claude-subscription` مصادقة OAuth المحمولة لاشتراك Claude Code عبر `~/.claude/.credentials.json` مع `claudeAiOauth.subscriptionType` أو `CLAUDE_CODE_OAUTH_TOKEN` من `claude setup-token`. وهو يثبت أولًا نجاح `claude -p` المباشر داخل Docker، ثم يشغّل دورين من واجهة Gateway CLI الخلفية من دون الاحتفاظ بمتغيرات env الخاصة بمفاتيح Anthropic API. ويعطّل مسار الاشتراك هذا فحوصات Claude MCP/tool والصورة افتراضيًا لأن Claude يوجّه حاليًا استخدام التطبيقات الخارجية عبر فوترة استخدام إضافي بدلًا من حدود خطة الاشتراك العادية.
- يختبر smoke الحي لواجهة CLI الخلفية الآن التدفق الكامل نفسه من طرف إلى طرف لـ Claude وCodex وGemini: دور نصي، ثم دور تصنيف صورة، ثم استدعاء أداة MCP `cron` يتم التحقق منه عبر Gateway CLI.
- يقوم اختبار smoke الافتراضي الخاص بـ Claude أيضًا بتعديل الجلسة من Sonnet إلى Opus ويتحقق من أن الجلسة المستأنفة لا تزال تتذكر ملاحظة سابقة.

## Live: اختبار smoke لربط ACP (`/acp spawn ... --bind here`)

- الاختبار: `src/gateway/gateway-acp-bind.live.test.ts`
- الهدف: التحقق من تدفق ربط المحادثة الحقيقي في ACP باستخدام وكيل ACP حي:
  - إرسال `/acp spawn <agent> --bind here`
  - ربط محادثة قناة رسائل اصطناعية في مكانها
  - إرسال متابعة عادية على هذه المحادثة نفسها
  - التحقق من أن المتابعة تصل إلى نص جلسة ACP المرتبطة
- التفعيل:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- الإعدادات الافتراضية:
  - وكلاء ACP في Docker: `claude,codex,gemini`
  - وكيل ACP للاستدعاء المباشر عبر `pnpm test:live ...`: `claude`
  - القناة الاصطناعية: سياق محادثة على نمط Slack DM
  - الواجهة الخلفية لـ ACP: `acpx`
- التجاوزات:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- ملاحظات:
  - يستخدم هذا المسار سطح `chat.send` في gateway مع حقول originating-route اصطناعية مخصصة للمشرف فقط حتى تتمكن الاختبارات من إرفاق سياق قناة الرسائل من دون التظاهر بالتسليم الخارجي.
  - عندما لا يكون `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` مضبوطًا، يستخدم الاختبار سجل الوكلاء المضمّن داخل Plugin `acpx` لاختيار وكيل ACP الخاص بإطار الاختبار.

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
- افتراضيًا، يشغّل اختبار smoke لربط ACP على جميع وكلاء CLI الحية المدعومة بالتسلسل: `claude` ثم `codex` ثم `gemini`.
- استخدم `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude` أو `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` أو `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` لتضييق المصفوفة.
- يستورد `~/.profile`، ويجهّز مواد المصادقة الخاصة بـ CLI المطابق داخل الحاوية، ويثبّت `acpx` في npm prefix قابل للكتابة، ثم يثبّت CLI الحي المطلوب (`@anthropic-ai/claude-code` أو `@openai/codex` أو `@google/gemini-cli`) إذا لم يكن موجودًا.
- داخل Docker، يضبط المشغّل `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` حتى يحافظ acpx على متغيرات env الخاصة بالمزوّد من profile المستورد متاحة لـ CLI الفرعي الخاص بإطار الاختبار.

## Live: اختبار smoke لإطار Codex app-server

- الهدف: التحقق من إطار Codex المملوك للـ Plugin عبر
  طريقة `agent` العادية في gateway:
  - تحميل Plugin `codex` المضمّن
  - اختيار `OPENCLAW_AGENT_RUNTIME=codex`
  - إرسال أول دور لوكيل gateway إلى `codex/gpt-5.4`
  - إرسال دور ثانٍ إلى جلسة OpenClaw نفسها والتحقق من أن
    خيط app-server يمكنه الاستئناف
  - تشغيل `/codex status` و`/codex models` عبر مسار
    أوامر gateway نفسه
- الاختبار: `src/gateway/gateway-codex-harness.live.test.ts`
- التفعيل: `OPENCLAW_LIVE_CODEX_HARNESS=1`
- النموذج الافتراضي: `codex/gpt-5.4`
- فحص الصورة الاختياري: `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1`
- فحص MCP/tool الاختياري: `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1`
- يضبط اختبار smoke القيمة `OPENCLAW_AGENT_HARNESS_FALLBACK=none` حتى لا يمر
  إطار Codex المعطّل بصمت عبر الرجوع الاحتياطي إلى PI.
- المصادقة: `OPENAI_API_KEY` من shell/profile، بالإضافة إلى نسخ اختيارية من
  `~/.codex/auth.json` و`~/.codex/config.toml`

وصفة محلية:

```bash
source ~/.profile
OPENCLAW_LIVE_CODEX_HARNESS=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MODEL=codex/gpt-5.4 \
  pnpm test:live -- src/gateway/gateway-codex-harness.live.test.ts
```

وصفة Docker:

```bash
source ~/.profile
pnpm test:docker:live-codex-harness
```

ملاحظات Docker:

- يوجد مشغّل Docker في `scripts/test-live-codex-harness-docker.sh`.
- يستورد `~/.profile` المركّب، ويمرر `OPENAI_API_KEY`، وينسخ ملفات
  مصادقة Codex CLI عند وجودها، ويثبّت `@openai/codex` في npm prefix
  قابل للكتابة ومركّب، ويجهّز شجرة المصدر، ثم يشغّل فقط اختبار Codex-harness الحي.
- يفعّل Docker فحوصات الصورة وMCP/tool افتراضيًا. اضبط
  `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=0` أو
  `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=0` عندما تحتاج إلى تشغيل تصحيح أضيق.
- يصدّر Docker أيضًا `OPENCLAW_AGENT_HARNESS_FALLBACK=none`، بما يطابق إعداد
  الاختبار الحي حتى لا يتمكن الرجوع الاحتياطي إلى `openai-codex/*` أو PI من إخفاء
  تراجع في إطار Codex.

### وصفات live الموصى بها

تُعد allowlists الضيقة والصريحة الأسرع والأقل عرضة للهشاشة:

- نموذج واحد، مباشر (من دون gateway):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- نموذج واحد، اختبار smoke لـ gateway:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- استدعاء الأدوات عبر عدة مزوّدين:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- تركيز Google (مفتاح Gemini API + Antigravity):
  - Gemini (مفتاح API): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

ملاحظات:

- يستخدم `google/...` واجهة Gemini API (مفتاح API).
- يستخدم `google-antigravity/...` جسر Antigravity OAuth (نقطة نهاية وكيل على نمط Cloud Code Assist).
- يستخدم `google-gemini-cli/...` واجهة Gemini CLI المحلية على جهازك (مع مصادقة منفصلة وخصائص أدوات مختلفة).
- Gemini API مقابل Gemini CLI:
  - API: يستدعي OpenClaw واجهة Gemini API المستضافة من Google عبر HTTP (بمصادقة مفتاح API / profile)؛ وهذا ما يقصده معظم المستخدمين بكلمة «Gemini».
  - CLI: ينفّذ OpenClaw ملف `gemini` الثنائي المحلي؛ وله مصادقته الخاصة وقد يتصرف بشكل مختلف (الدفق/دعم الأدوات/اختلاف الإصدارات).

## Live: مصفوفة النماذج (ما الذي نغطيه)

لا توجد «قائمة نماذج CI» ثابتة (لأن live اختيارية)، لكن هذه هي النماذج **الموصى بها** للتغطية بانتظام على جهاز تطوير مزود بالمفاتيح.

### مجموعة smoke الحديثة (استدعاء الأدوات + الصور)

هذا هو تشغيل «النماذج الشائعة» الذي نتوقع أن يبقى عاملًا:

- OpenAI (غير Codex): `openai/gpt-5.4` (اختياري: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (أو `anthropic/claude-sonnet-4-6`)
- Google (Gemini API): `google/gemini-3.1-pro-preview` و`google/gemini-3-flash-preview` (تجنب نماذج Gemini 2.x الأقدم)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` و`google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

شغّل اختبار smoke لـ gateway مع الأدوات + الصور:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### الأساس: استدعاء الأدوات (Read + Exec اختياري)

اختر واحدًا على الأقل لكل عائلة مزوّد:

- OpenAI: `openai/gpt-5.4` (أو `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (أو `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (أو `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

تغطية إضافية اختيارية (من الجيد توفرها):

- xAI: `xai/grok-4` (أو أحدث إصدار متاح)
- Mistral: `mistral/`… (اختر نموذجًا واحدًا قادرًا على `tools` لديك)
- Cerebras: `cerebras/`… (إذا كان لديك وصول)
- LM Studio: `lmstudio/`… (محلي؛ استدعاء الأدوات يعتمد على وضع API)

### الرؤية: إرسال صورة (مرفق ← رسالة متعددة الوسائط)

أدرج نموذجًا واحدًا على الأقل قادرًا على التعامل مع الصور في `OPENCLAW_LIVE_GATEWAY_MODELS` (مثل متغيرات Claude/Gemini/OpenAI القادرة على الرؤية، إلخ) لاختبار فحص الصورة.

### المجمّعات / البوابات البديلة

إذا كانت لديك مفاتيح مفعلة، فنحن ندعم أيضًا الاختبار عبر:

- OpenRouter: `openrouter/...` (مئات النماذج؛ استخدم `openclaw models scan` للعثور على مرشحين قادرين على tools+image)
- OpenCode: `opencode/...` لـ Zen و`opencode-go/...` لـ Go (المصادقة عبر `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

مزيد من المزوّدين الذين يمكنك تضمينهم في مصفوفة live (إذا كانت لديك بيانات الاعتماد/الإعداد):

- مدمجة: `openai` و`openai-codex` و`anthropic` و`google` و`google-vertex` و`google-antigravity` و`google-gemini-cli` و`zai` و`openrouter` و`opencode` و`opencode-go` و`xai` و`groq` و`cerebras` و`mistral` و`github-copilot`
- عبر `models.providers` (نقاط نهاية مخصصة): `minimax` (سحابي/API)، بالإضافة إلى أي proxy متوافق مع OpenAI/Anthropic (مثل LM Studio وvLLM وLiteLLM وغيرها)

نصيحة: لا تحاول ترميز «كل النماذج» بشكل ثابت في المستندات. القائمة المرجعية هي ما يعيده `discoverModels(...)` على جهازك + أي مفاتيح متاحة.

## بيانات الاعتماد (لا تلتزم بها أبدًا)

تكتشف اختبارات live بيانات الاعتماد بالطريقة نفسها التي يستخدمها CLI. والنتائج العملية لذلك:

- إذا كان CLI يعمل، فيجب أن تعثر اختبارات live على المفاتيح نفسها.
- إذا أخبرك اختبار live بأنه «لا توجد بيانات اعتماد»، فقم بالتصحيح بالطريقة نفسها التي ستصحح بها `openclaw models list` / اختيار النموذج.

- ملفات المصادقة لكل وكيل: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (وهذا هو المقصود بعبارة «مفاتيح profile» في اختبارات live)
- الإعداد: `~/.openclaw/openclaw.json` (أو `OPENCLAW_CONFIG_PATH`)
- دليل الحالة القديم: `~/.openclaw/credentials/` (يتم نسخه إلى home live المرحلي عند وجوده، لكنه ليس مخزن مفاتيح profile الرئيسي)
- تنسخ تشغيلات live المحلية الإعداد النشط وملفات `auth-profiles.json` لكل وكيل و`credentials/` القديمة وأدلة مصادقة CLI الخارجية المدعومة إلى home اختباري مؤقت افتراضيًا؛ وتتخطى homes الحية المرحلية `workspace/` و`sandboxes/`، كما تُزال تجاوزات المسار `agents.*.workspace` و`agentDir` حتى تبقى الفحوصات بعيدة عن مساحة العمل الحقيقية على المضيف.

إذا كنت تريد الاعتماد على مفاتيح env (مثل تلك التي تم تصديرها في `~/.profile`)، فشغّل الاختبارات المحلية بعد `source ~/.profile`، أو استخدم مشغلات Docker أدناه (يمكنها تركيب `~/.profile` داخل الحاوية).

## Live: Deepgram (نسخ صوتي)

- الاختبار: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- التفعيل: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## Live: خطة ترميز BytePlus

- الاختبار: `src/agents/byteplus.live.test.ts`
- التفعيل: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- تجاوز النموذج الاختياري: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## Live: وسائط workflow الخاصة بـ ComfyUI

- الاختبار: `extensions/comfy/comfy.live.test.ts`
- التفعيل: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- النطاق:
  - يختبر مسارات الصورة والفيديو و`music_generate` الخاصة بـ comfy المضمّن
  - يتجاوز كل قدرة ما لم يتم إعداد `models.providers.comfy.<capability>`
  - مفيد بعد تغيير إرسال workflow الخاص بـ comfy، أو polling، أو التنزيلات، أو تسجيل Plugin

## Live: إنشاء الصور

- الاختبار: `src/image-generation/runtime.live.test.ts`
- الأمر: `pnpm test:live src/image-generation/runtime.live.test.ts`
- إطار الاختبار: `pnpm test:live:media image`
- النطاق:
  - يعدّد كل Plugin مزوّد لإنشاء الصور مسجل
  - يحمّل متغيرات env الخاصة بالمزوّد الناقصة من shell تسجيل الدخول الخاص بك (`~/.profile`) قبل الفحص
  - يستخدم مفاتيح API الحية/من env قبل ملفات المصادقة المخزنة افتراضيًا، حتى لا تخفي مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات الاعتماد الحقيقية في shell
  - يتجاوز المزوّدين الذين لا يملكون مصادقة/ profile / نموذجًا صالحًا
  - يشغّل متغيرات إنشاء الصور القياسية عبر قدرة وقت التشغيل المشتركة:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- المزوّدون المضمّنون المغطَّون حاليًا:
  - `openai`
  - `google`
- التضييق الاختياري:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- سلوك المصادقة الاختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن profile وتجاهل التجاوزات المعتمدة على env فقط

## Live: إنشاء الموسيقى

- الاختبار: `extensions/music-generation-providers.live.test.ts`
- التفعيل: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- إطار الاختبار: `pnpm test:live:media music`
- النطاق:
  - يختبر مسار مزوّد إنشاء الموسيقى المضمّن المشترك
  - يغطي حاليًا Google وMiniMax
  - يحمّل متغيرات env الخاصة بالمزوّد من shell تسجيل الدخول الخاص بك (`~/.profile`) قبل الفحص
  - يستخدم مفاتيح API الحية/من env قبل ملفات المصادقة المخزنة افتراضيًا، حتى لا تخفي مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات الاعتماد الحقيقية في shell
  - يتجاوز المزوّدين الذين لا يملكون مصادقة/ profile / نموذجًا صالحًا
  - يشغّل وضعي وقت التشغيل المعلنين كليهما عند توفرهما:
    - `generate` مع إدخال يعتمد على الموجه فقط
    - `edit` عندما يعلن المزوّد `capabilities.edit.enabled`
  - التغطية الحالية في المسار المشترك:
    - `google`: `generate` و`edit`
    - `minimax`: `generate`
    - `comfy`: له ملف live منفصل لـ Comfy، وليس ضمن هذا المسح المشترك
- التضييق الاختياري:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- سلوك المصادقة الاختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن profile وتجاهل التجاوزات المعتمدة على env فقط

## Live: إنشاء الفيديو

- الاختبار: `extensions/video-generation-providers.live.test.ts`
- التفعيل: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- إطار الاختبار: `pnpm test:live:media video`
- النطاق:
  - يختبر مسار مزوّد إنشاء الفيديو المضمّن المشترك
  - يحمّل متغيرات env الخاصة بالمزوّد من shell تسجيل الدخول الخاص بك (`~/.profile`) قبل الفحص
  - يستخدم مفاتيح API الحية/من env قبل ملفات المصادقة المخزنة افتراضيًا، حتى لا تخفي مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات الاعتماد الحقيقية في shell
  - يتجاوز المزوّدين الذين لا يملكون مصادقة/ profile / نموذجًا صالحًا
  - يشغّل وضعي وقت التشغيل المعلنين كليهما عند توفرهما:
    - `generate` مع إدخال يعتمد على الموجه فقط
    - `imageToVideo` عندما يعلن المزوّد `capabilities.imageToVideo.enabled` ويقبل المزوّد/النموذج المحدد إدخال صور محلية مدعومًا بالذاكرة المؤقتة في المسح المشترك
    - `videoToVideo` عندما يعلن المزوّد `capabilities.videoToVideo.enabled` ويقبل المزوّد/النموذج المحدد إدخال فيديو محليًا مدعومًا بالذاكرة المؤقتة في المسح المشترك
  - المزوّدون الحاليون المعلَن عنهم لكن يتم تجاوزهم في مسح `imageToVideo` المشترك:
    - `vydra` لأن `veo3` المضمّن نصي فقط و`kling` المضمّن يتطلب URL صورة بعيدًا
  - تغطية Vydra الخاصة بالمزوّد:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - يشغّل هذا الملف مسار `veo3` لتحويل النص إلى فيديو بالإضافة إلى مسار `kling` يستخدم fixture لعنوان URL صورة بعيد افتراضيًا
  - التغطية الحالية لـ `videoToVideo` في live:
    - `runway` فقط عندما يكون النموذج المحدد هو `runway/gen4_aleph`
  - المزوّدون الحاليون المعلَن عنهم لكن يتم تجاوزهم في مسح `videoToVideo` المشترك:
    - `alibaba` و`qwen` و`xai` لأن هذه المسارات تتطلب حاليًا عناوين URL مرجعية بعيدة من نوع `http(s)` / MP4
    - `google` لأن مسار Gemini/Veo المشترك الحالي يستخدم إدخالًا محليًا مدعومًا بالذاكرة المؤقتة ولا يُقبل هذا المسار في المسح المشترك
    - `openai` لأن المسار المشترك الحالي يفتقر إلى ضمانات وصول الفيديو الخاصة بالمؤسسة لعمليات inpaint/remix
- التضييق الاختياري:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- سلوك المصادقة الاختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن profile وتجاهل التجاوزات المعتمدة على env فقط

## إطار اختبارات الوسائط الحي

- الأمر: `pnpm test:live:media`
- الغرض:
  - يشغّل مجموعات live المشتركة للصورة والموسيقى والفيديو عبر نقطة دخول أصلية واحدة للمستودع
  - يحمّل تلقائيًا متغيرات env الناقصة الخاصة بالمزوّد من `~/.profile`
  - يضيّق تلقائيًا كل مجموعة إلى المزوّدين الذين يملكون حاليًا مصادقة قابلة للاستخدام افتراضيًا
  - يعيد استخدام `scripts/test-live.mjs`، بحيث يبقى سلوك Heartbeat والوضع الهادئ متسقًا
- أمثلة:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## مشغلات Docker (فحوصات اختيارية من نوع "يعمل على Linux")

تنقسم مشغلات Docker هذه إلى فئتين:

- مشغلات النماذج الحية: يشغّل `test:docker:live-models` و`test:docker:live-gateway` فقط ملف الاختبار الحي المطابق لمفاتيح profile داخل صورة Docker الخاصة بالمستودع (`src/agents/models.profiles.live.test.ts` و`src/gateway/gateway-models.profiles.live.test.ts`)، مع تركيب دليل الإعداد المحلي ومساحة العمل الخاصة بك (واستيراد `~/.profile` إذا تم تركيبه). ونقاط الدخول المحلية المطابقة هي `test:live:models-profiles` و`test:live:gateway-profiles`.
- تستخدم مشغلات Docker الحية افتراضيًا حد smoke أصغر حتى يظل المسح الكامل داخل Docker عمليًا:
  يستخدم `test:docker:live-models` القيمة الافتراضية `OPENCLAW_LIVE_MAX_MODELS=12`، ويستخدم
  `test:docker:live-gateway` افتراضيًا `OPENCLAW_LIVE_GATEWAY_SMOKE=1`،
  و`OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`،
  و`OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`، و
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. تجاوز هذه المتغيرات البيئية عندما
  تريد صراحةً إجراء المسح الشامل الأكبر.
- يقوم `test:docker:all` ببناء صورة Docker الحية مرة واحدة عبر `test:docker:live-build`، ثم يعيد استخدامها لمساري Docker الحيين.
- مشغلات smoke الخاصة بالحاويات: `test:docker:openwebui` و`test:docker:onboard` و`test:docker:gateway-network` و`test:docker:mcp-channels` و`test:docker:plugins` تشغّل حاوية واحدة أو أكثر حقيقية وتتحقق من مسارات تكامل أعلى مستوى.

تقوم مشغلات Docker الخاصة بالنماذج الحية أيضًا بتركيب أدلة مصادقة CLI المطلوبة فقط (أو جميع الأدلة المدعومة عندما لا يكون التشغيل مضيقًا)، ثم تنسخها إلى home الخاص بالحاوية قبل التشغيل حتى تتمكن مصادقة OAuth الخاصة بواجهات CLI الخارجية من تحديث الرموز من دون تعديل مخزن المصادقة على المضيف:

- النماذج المباشرة: `pnpm test:docker:live-models` (السكربت: `scripts/test-live-models-docker.sh`)
- اختبار smoke لربط ACP: `pnpm test:docker:live-acp-bind` (السكربت: `scripts/test-live-acp-bind-docker.sh`)
- اختبار smoke للواجهة الخلفية CLI: `pnpm test:docker:live-cli-backend` (السكربت: `scripts/test-live-cli-backend-docker.sh`)
- اختبار smoke لإطار Codex app-server: `pnpm test:docker:live-codex-harness` (السكربت: `scripts/test-live-codex-harness-docker.sh`)
- Gateway + وكيل التطوير: `pnpm test:docker:live-gateway` (السكربت: `scripts/test-live-gateway-models-docker.sh`)
- اختبار smoke حي لـ Open WebUI: `pnpm test:docker:openwebui` (السكربت: `scripts/e2e/openwebui-docker.sh`)
- معالج onboarding (TTY، scaffold كامل): `pnpm test:docker:onboard` (السكربت: `scripts/e2e/onboard-docker.sh`)
- شبكات Gateway (حاويتان، مصادقة WS + health): `pnpm test:docker:gateway-network` (السكربت: `scripts/e2e/gateway-network-docker.sh`)
- جسر قناة MCP (Gateway مُهيّأ مسبقًا + جسر stdio + اختبار smoke خام لإطار إشعارات Claude): `pnpm test:docker:mcp-channels` (السكربت: `scripts/e2e/mcp-channels-docker.sh`)
- Plugins (اختبار smoke للتثبيت + الاسم المستعار `/plugin` + دلالات إعادة تشغيل حزمة Claude): `pnpm test:docker:plugins` (السكربت: `scripts/e2e/plugins-docker.sh`)

تقوم مشغلات Docker الخاصة بالنماذج الحية أيضًا بتركيب النسخة الحالية من المستودع
للقراءة فقط ثم تجهّزها في workdir مؤقت داخل الحاوية. وهذا يُبقي صورة وقت التشغيل
خفيفة مع الاستمرار في تشغيل Vitest على المصدر/الإعداد المحلي الدقيق لديك.
وتتجاوز خطوة التجهيز المخازن المؤقتة المحلية الكبيرة ومخرجات بناء التطبيقات مثل
`.pnpm-store` و`.worktrees` و`__openclaw_vitest__` وأدلة `.build` المحلية للتطبيق أو
مخرجات Gradle، حتى لا تقضي تشغيلات Docker الحية دقائق في نسخ artifacts
خاصة بالجهاز.
كما تضبط أيضًا `OPENCLAW_SKIP_CHANNELS=1` حتى لا تبدأ فحوصات gateway الحية
عمّال قنوات حقيقية مثل Telegram/Discord وغيرها داخل الحاوية.
لا يزال `test:docker:live-models` يشغّل `pnpm test:live`، لذا مرّر أيضًا
`OPENCLAW_LIVE_GATEWAY_*` عندما تحتاج إلى تضييق أو استبعاد تغطية gateway
الحية من مسار Docker هذا.
ويُعد `test:docker:openwebui` اختبار smoke توافقًا أعلى مستوى: فهو يبدأ
حاوية Gateway خاصة بـ OpenClaw مع تفعيل نقاط نهاية HTTP المتوافقة مع OpenAI،
ويبدأ حاوية Open WebUI مثبتة على ذلك الـ gateway، ويسجل الدخول عبر
Open WebUI، ويتحقق من أن `/api/models` يعرض `openclaw/default`، ثم يرسل
طلب دردشة حقيقيًا عبر وكيل `/api/chat/completions` في Open WebUI.
قد يكون التشغيل الأول أبطأ بشكل ملحوظ لأن Docker قد يحتاج إلى سحب صورة
Open WebUI وقد يحتاج Open WebUI نفسه إلى إنهاء إعداد البدء البارد الخاص به.
ويتوقع هذا المسار مفتاح نموذج حي صالحًا، ويُعد `OPENCLAW_PROFILE_FILE`
(`~/.profile` افتراضيًا) الطريقة الأساسية لتوفيره في التشغيلات داخل Docker.
وتطبع التشغيلات الناجحة حمولة JSON صغيرة مثل `{ "ok": true, "model":
"openclaw/default", ... }`.
أما `test:docker:mcp-channels` فهو حتمي عمدًا ولا يحتاج إلى حساب
Telegram أو Discord أو iMessage حقيقي. فهو يشغّل حاوية Gateway
مُهيّأة مسبقًا، ويبدأ حاوية ثانية تشغّل `openclaw mcp serve`، ثم
يتحقق من اكتشاف المحادثات الموجّهة، وقراءة النصوص، وبيانات تعريف المرفقات،
وسلوك طابور الأحداث الحية، وتوجيه الإرسال الصادر، وإشعارات القنوات +
الأذونات على نمط Claude عبر جسر MCP الحقيقي القائم على stdio. كما يفحص تحقق
الإشعارات إطارات MCP الخام الخاصة بـ stdio مباشرة حتى يثبت الاختبار ما الذي
يبثه الجسر فعليًا، لا مجرد ما قد تعرضه مجموعة SDK عميل معيّنة.

اختبار smoke يدوي لخيط ACP بلغة طبيعية (ليس في CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- احتفظ بهذا السكربت لتدفقات العمل الخاصة بالاختبارات التراجعية/التصحيح. فقد تكون هناك حاجة إليه مرة أخرى للتحقق من توجيه خيوط ACP، لذا لا تحذفه.

متغيرات env مفيدة:

- `OPENCLAW_CONFIG_DIR=...` (الافتراضي: `~/.openclaw`) يُركّب إلى `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` (الافتراضي: `~/.openclaw/workspace`) يُركّب إلى `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` (الافتراضي: `~/.profile`) يُركّب إلى `/home/node/.profile` ويُستورد قبل تشغيل الاختبارات
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (الافتراضي: `~/.cache/openclaw/docker-cli-tools`) يُركّب إلى `/home/node/.npm-global` لتخزين تثبيتات CLI مؤقتًا داخل Docker
- تُركّب أدلة/ملفات مصادقة CLI الخارجية تحت `$HOME` للقراءة فقط ضمن `/host-auth...`، ثم تُنسخ إلى `/home/node/...` قبل بدء الاختبارات
  - الأدلة الافتراضية: `.minimax`
  - الملفات الافتراضية: `~/.codex/auth.json` و`~/.codex/config.toml` و`.claude.json` و`~/.claude/.credentials.json` و`~/.claude/settings.json` و`~/.claude/settings.local.json`
  - تركّب التشغيلات المضيقة للمزوّد فقط الأدلة/الملفات المطلوبة التي يتم استنتاجها من `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - يمكن التجاوز يدويًا عبر `OPENCLAW_DOCKER_AUTH_DIRS=all` أو `OPENCLAW_DOCKER_AUTH_DIRS=none` أو قائمة مفصولة بفواصل مثل `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` لتضييق التشغيل
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...` لتصفية المزوّدين داخل الحاوية
- `OPENCLAW_SKIP_DOCKER_BUILD=1` لإعادة استخدام صورة `openclaw:local-live` موجودة لتكرارات التشغيل التي لا تحتاج إلى إعادة بناء
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لضمان أن تأتي بيانات الاعتماد من مخزن profile (وليس من env)
- `OPENCLAW_OPENWEBUI_MODEL=...` لاختيار النموذج الذي يعرضه gateway لاختبار smoke الخاص بـ Open WebUI
- `OPENCLAW_OPENWEBUI_PROMPT=...` لتجاوز موجه التحقق من nonce المستخدم في اختبار smoke لـ Open WebUI
- `OPENWEBUI_IMAGE=...` لتجاوز وسم صورة Open WebUI المثبتة

## سلامة المستندات

شغّل فحوصات المستندات بعد تعديلات المستندات: `pnpm check:docs`.
وشغّل التحقق الكامل من روابط Mintlify anchors عندما تحتاج أيضًا إلى فحوصات العناوين داخل الصفحة: `pnpm docs:check-links:anchors`.

## اختبار تراجعي دون اتصال (آمن لـ CI)

هذه اختبارات تراجعية لـ «خط أنابيب حقيقي» من دون مزوّدين حقيقيين:

- استدعاء أدوات Gateway (OpenAI وهمي، Gateway حقيقي + حلقة وكيل حقيقية): `src/gateway/gateway.test.ts` (الحالة: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- معالج Gateway (‏WS `wizard.start`/`wizard.next`، يكتب الإعداد + يفرض المصادقة): `src/gateway/gateway.test.ts` (الحالة: "runs wizard over ws and writes auth token config")

## تقييمات موثوقية الوكيل (Skills)

لدينا بالفعل بعض الاختبارات الآمنة لـ CI التي تتصرف مثل «تقييمات موثوقية الوكيل»:

- استدعاء الأدوات الوهمي عبر حلقة Gateway + الوكيل الحقيقية (`src/gateway/gateway.test.ts`).
- تدفقات المعالج الكاملة من طرف إلى طرف التي تتحقق من توصيل الجلسة وتأثيرات الإعداد (`src/gateway/gateway.test.ts`).

ما الذي لا يزال مفقودًا بالنسبة إلى Skills (راجع [Skills](/ar/tools/skills)):

- **اتخاذ القرار:** عندما تُدرج Skills في الموجه، هل يختار الوكيل Skill الصحيحة (أو يتجنب غير الملائمة)؟
- **الامتثال:** هل يقرأ الوكيل `SKILL.md` قبل الاستخدام ويتبع الخطوات/المعاملات المطلوبة؟
- **عقود سير العمل:** سيناريوهات متعددة الأدوار تتحقق من ترتيب الأدوات، واستمرار سجل الجلسة، وحدود sandbox.

يجب أن تبقى التقييمات المستقبلية حتمية أولًا:

- مشغّل سيناريوهات يستخدم مزوّدين وهميين للتحقق من استدعاءات الأدوات + ترتيبها، وقراءة ملفات skill، وتوصيل الجلسة.
- مجموعة صغيرة من السيناريوهات المركزة على Skills (استخدم مقابل تجنب، والبوابات، وحقن الموجه).
- تقييمات live اختيارية (مفعّلة عند الطلب وبوابات env) فقط بعد وجود المجموعة الآمنة لـ CI.

## اختبارات العقود (شكل Plugin والقناة)

تتحقق اختبارات العقود من أن كل Plugin وقناة مسجلين يلتزمان
بعقد الواجهة الخاص بهما. فهي تكرّر على جميع Plugins المكتشفة وتشغّل مجموعة من
التحققات الخاصة بالشكل والسلوك. ويتجاوز مسار unit الافتراضي في `pnpm test`
عمدًا هذه الملفات المشتركة الخاصة بالواجهات واختبارات smoke؛ شغّل أوامر العقود
صراحةً عندما تلمس الأسطح المشتركة الخاصة بالقنوات أو المزوّدين.

### الأوامر

- جميع العقود: `pnpm test:contracts`
- عقود القنوات فقط: `pnpm test:contracts:channels`
- عقود المزوّدين فقط: `pnpm test:contracts:plugins`

### عقود القنوات

تقع في `src/channels/plugins/contracts/*.contract.test.ts`:

- **plugin** - شكل Plugin الأساسي (المعرّف، والاسم، والقدرات)
- **setup** - عقد معالج الإعداد
- **session-binding** - سلوك ربط الجلسة
- **outbound-payload** - بنية حمولة الرسالة
- **inbound** - معالجة الرسائل الواردة
- **actions** - معالجات إجراءات القناة
- **threading** - التعامل مع معرّف الخيط
- **directory** - واجهة API الخاصة بالدليل/القائمة
- **group-policy** - فرض سياسة المجموعات

### عقود حالة المزوّد

تقع في `src/plugins/contracts/*.contract.test.ts`.

- **status** - فحوصات حالة القناة
- **registry** - شكل سجل Plugin

### عقود المزوّدين

تقع في `src/plugins/contracts/*.contract.test.ts`:

- **auth** - عقد تدفق المصادقة
- **auth-choice** - اختيار/تحديد المصادقة
- **catalog** - واجهة API لفهرس النماذج
- **discovery** - اكتشاف Plugin
- **loader** - تحميل Plugin
- **runtime** - وقت تشغيل المزوّد
- **shape** - شكل/واجهة Plugin
- **wizard** - معالج الإعداد

### متى تُشغَّل

- بعد تغيير صادرات `plugin-sdk` أو المسارات الفرعية
- بعد إضافة Plugin قناة أو مزوّد أو تعديله
- بعد إعادة هيكلة تسجيل Plugin أو اكتشافه

تعمل اختبارات العقود في CI ولا تتطلب مفاتيح API حقيقية.

## إضافة اختبارات تراجعية (إرشادات)

عندما تصلح مشكلة مزوّد/نموذج تم اكتشافها في live:

- أضف اختبارًا تراجعيًا آمنًا لـ CI إن أمكن (مزوّدًا وهميًا/Stub، أو التقط تحويل شكل الطلب الدقيق)
- إذا كانت المشكلة بطبيعتها live فقط (حدود المعدل، وسياسات المصادقة)، فأبقِ اختبار live ضيقًا ومفعّلًا عند الطلب عبر متغيرات env
- فضّل استهداف أصغر طبقة تلتقط الخطأ:
  - خطأ في تحويل/إعادة تشغيل طلب المزوّد → اختبار النماذج المباشرة
  - خطأ في خط أنابيب جلسة/سجل/أدوات gateway → اختبار smoke حي لـ gateway أو اختبار Gateway وهمي وآمن لـ CI
- حاجز الحماية لاجتياز SecretRef:
  - يستمد `src/secrets/exec-secret-ref-id-parity.test.ts` هدفًا نموذجيًا واحدًا لكل فئة SecretRef من بيانات سجل metadata (`listSecretTargetRegistryEntries()`)، ثم يتحقق من رفض معرّفات exec الخاصة بمقاطع الاجتياز.
  - إذا أضفت عائلة أهداف SecretRef جديدة من نوع `includeInPlan` في `src/secrets/target-registry-data.ts`، فحدّث `classifyTargetClass` في ذلك الاختبار. ويفشل الاختبار عمدًا عند وجود معرّفات أهداف غير مصنفة حتى لا يمكن تخطي الفئات الجديدة بصمت.
