---
read_when:
    - تحتاج إلى مرجع لإعداد النماذج مزوّدًا بمزوّد
    - تريد إعدادات نموذجية أو أوامر تهيئة عبر CLI لمزوّدي النماذج
summary: نظرة عامة على مزوّدي النماذج مع إعدادات نموذجية + تدفقات CLI
title: مزوّدو النماذج
x-i18n:
    generated_at: "2026-04-07T07:18:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: a9c1f7f8cf09b6047a64189f7440811aafc93d01335f76969afd387cc54c7ab5
    source_path: concepts/model-providers.md
    workflow: 15
---

# مزوّدو النماذج

تغطي هذه الصفحة **مزوّدي LLM/النماذج** (وليس قنوات الدردشة مثل WhatsApp/Telegram).
للاطلاع على قواعد اختيار النموذج، راجع [/concepts/models](/ar/concepts/models).

## قواعد سريعة

- تستخدم مراجع النماذج الصيغة `provider/model` (مثال: `opencode/claude-opus-4-6`).
- إذا قمت بتعيين `agents.defaults.models`، فسيصبح قائمة السماح.
- أدوات CLI المساعدة: `openclaw onboard` و `openclaw models list` و `openclaw models set <provider/model>`.
- قواعد وقت التشغيل الاحتياطية، وفحوصات التهدئة، واستمرارية تجاوزات الجلسة موثقة
  في [/concepts/model-failover](/ar/concepts/model-failover).
- `models.providers.*.models[].contextWindow` هي بيانات تعريف أصلية للنموذج؛
  أما `models.providers.*.models[].contextTokens` فهو الحد الفعّال في وقت التشغيل.
- يمكن لإضافات المزوّدين حقن فهارس النماذج عبر `registerProvider({ catalog })`;
  ويقوم OpenClaw بدمج هذا الخرج في `models.providers` قبل كتابة
  `models.json`.
- يمكن لبيانات تعريف المزوّدين التصريحية الإعلان عن `providerAuthEnvVars` بحيث لا تحتاج
  فحوصات المصادقة العامة المعتمدة على متغيرات البيئة إلى تحميل وقت تشغيل الإضافة. أصبحت
  خريطة متغيرات البيئة الأساسية المتبقية الآن فقط للمزوّدين غير المعتمدين على الإضافات/الأساسيين
  وبعض حالات أسبقية عامة، مثل تهيئة Anthropic التي تبدأ بمفتاح API.
- يمكن لإضافات المزوّدين أيضًا امتلاك سلوك وقت تشغيل المزوّد عبر
  `normalizeModelId`, `normalizeTransport`, `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`,
  `normalizeResolvedModel`, `contributeResolvedModelCompat`,
  `capabilities`, `normalizeToolSchemas`,
  `inspectToolSchemas`, `resolveReasoningOutputMode`,
  `prepareExtraParams`, `createStreamFn`, `wrapStreamFn`,
  `resolveTransportTurnState`, `resolveWebSocketSessionPolicy`,
  `createEmbeddingProvider`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`,
  `matchesContextOverflowError`, `classifyFailoverReason`,
  `isCacheTtlEligible`, `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot`, and
  `onModelSelected`.
- ملاحظة: `capabilities` الخاصة بوقت تشغيل المزوّد هي بيانات تعريف مشتركة للمشغّل (عائلة المزوّد،
  وخصائص النصوص/الأدوات، وتلميحات النقل/التخزين المؤقت). وهي ليست
  نفسها [لنموذج القدرات العامة](/ar/plugins/architecture#public-capability-model)
  الذي يصف ما الذي تسجله الإضافة (استدلال نصي، كلام، إلخ).

## سلوك المزوّد المملوك للإضافة

يمكن لإضافات المزوّدين الآن امتلاك معظم المنطق الخاص بكل مزوّد، بينما يحافظ OpenClaw
على حلقة الاستدلال العامة.

التقسيم المعتاد:

- `auth[].run` / `auth[].runNonInteractive`: يمتلك المزوّد تدفقات التهيئة/تسجيل الدخول
  الخاصة بـ `openclaw onboard` و `openclaw models auth` والإعداد غير التفاعلي
- `wizard.setup` / `wizard.modelPicker`: يمتلك المزوّد تسميات خيارات المصادقة،
  والأسماء المستعارة القديمة، وتلميحات قائمة السماح أثناء التهيئة، وإدخالات
  الإعداد في منتقيات التهيئة/النموذج
- `catalog`: يظهر المزوّد في `models.providers`
- `normalizeModelId`: يقوم المزوّد بتطبيع معرّفات النماذج القديمة/المعاينة قبل
  البحث أو جعلها معيارية
- `normalizeTransport`: يقوم المزوّد بتطبيع `api` / `baseUrl` الخاصة بعائلة النقل
  قبل التجميع العام للنموذج؛ يتحقق OpenClaw أولًا من المزوّد المطابق،
  ثم من إضافات المزوّد الأخرى القادرة على الخطافات حتى تغيّر إحداها
  النقل فعليًا
- `normalizeConfig`: يقوم المزوّد بتطبيع إعدادات `models.providers.<id>` قبل
  أن يستخدمها وقت التشغيل؛ يتحقق OpenClaw أولًا من المزوّد المطابق، ثم من إضافات المزوّد
  الأخرى القادرة على الخطافات حتى تغيّر إحداها الإعدادات فعليًا. إذا لم
  تعد كتابة الإعدادات أي خطافات مزوّد، فإن مساعدات Google-family المضمّنة
  ستظل تطبّع إدخالات مزوّدي Google المدعومة.
- `applyNativeStreamingUsageCompat`: يطبّق المزوّد إعادة كتابة توافق استخدام البث الأصلي المعتمدة على نقطة النهاية لمزوّدي الإعدادات
- `resolveConfigApiKey`: يحل المزوّد مصادقة علامات البيئة لمزوّدي الإعدادات
  من دون فرض تحميل مصادقة وقت التشغيل الكاملة. يمتلك `amazon-bedrock` أيضًا
  محلّلًا مضمّنًا لعلامات بيئة AWS هنا، رغم أن مصادقة وقت تشغيل Bedrock تستخدم
  سلسلة AWS SDK الافتراضية.
- `resolveSyntheticAuth`: يمكن للمزوّد عرض توفّر المصادقة المحلية/المستضافة ذاتيًا أو
  المصادقة الأخرى المعتمدة على الإعدادات دون تخزين أسرار نصية صريحة
- `shouldDeferSyntheticProfileAuth`: يمكن للمزوّد تعليم عناصر نائبة محفوظة لملفات تعريف تركيبية
  على أنها أقل أسبقية من المصادقة المعتمدة على البيئة/الإعدادات
- `resolveDynamicModel`: يقبل المزوّد معرّفات نماذج غير موجودة بعد في
  الفهرس الثابت المحلي
- `prepareDynamicModel`: يحتاج المزوّد إلى تحديث البيانات التعريفية قبل إعادة محاولة
  الحل الديناميكي
- `normalizeResolvedModel`: يحتاج المزوّد إلى إعادة كتابة النقل أو عنوان URL الأساسي
- `contributeResolvedModelCompat`: يساهم المزوّد بعلامات توافق لنماذجه
  التابعة للمورّد حتى عندما تصل عبر نقل متوافق آخر
- `capabilities`: ينشر المزوّد خصائص النصوص/الأدوات/عائلة المزوّد
- `normalizeToolSchemas`: ينظف المزوّد مخططات الأدوات قبل أن يراها
  المشغّل المضمّن
- `inspectToolSchemas`: يعرض المزوّد تحذيرات مخطط خاصة بالنقل
  بعد التطبيع
- `resolveReasoningOutputMode`: يختار المزوّد عقود مخرجات التفكير الأصلية أو الموسومة
- `prepareExtraParams`: يضع المزوّد قيمًا افتراضية أو يطبّع معلمات الطلب لكل نموذج
- `createStreamFn`: يستبدل المزوّد مسار البث المعتاد بنقل مخصص بالكامل
- `wrapStreamFn`: يطبّق المزوّد أغلفة توافق لروؤس/جسم/نموذج الطلب
- `resolveTransportTurnState`: يوفّر المزوّد روؤسًا أو بيانات تعريفية
  أصلية للنقل لكل دور
- `resolveWebSocketSessionPolicy`: يوفّر المزوّد روؤس جلسة WebSocket أصلية
  أو سياسة تهدئة الجلسة
- `createEmbeddingProvider`: يمتلك المزوّد سلوك تضمين الذاكرة عندما
  يكون من الأنسب أن يكون داخل إضافة المزوّد بدلًا من لوحة تحويل التضمين الأساسية
- `formatApiKey`: ينسّق المزوّد ملفات تعريف المصادقة المخزنة إلى
  سلسلة `apiKey` الخاصة بوقت التشغيل التي يتوقعها النقل
- `refreshOAuth`: يمتلك المزوّد تحديث OAuth عندما لا تكون أدوات التحديث
  المشتركة `pi-ai` كافية
- `buildAuthDoctorHint`: يضيف المزوّد إرشادات إصلاح عندما يفشل تحديث OAuth
- `matchesContextOverflowError`: يتعرّف المزوّد على
  أخطاء تجاوز نافذة السياق الخاصة بالمزوّد التي قد تفوتها الإرشادات العامة
- `classifyFailoverReason`: يربط المزوّد أخطاء النقل/API الخام الخاصة بالمزوّد
  بأسباب التحويل الاحتياطي مثل حد المعدل أو زيادة الحمل
- `isCacheTtlEligible`: يحدد المزوّد معرّفات النماذج upstream التي تدعم مدة صلاحية التخزين المؤقت للمطالبات
- `buildMissingAuthMessage`: يستبدل المزوّد خطأ مخزن المصادقة العام
  بتلميح استرداد خاص بالمزوّد
- `suppressBuiltInModel`: يخفي المزوّد الصفوف upstream القديمة ويمكنه إرجاع
  خطأ مملوكًا للمورّد عند فشل الحل المباشر
- `augmentModelCatalog`: يضيف المزوّد صفوفًا تركيبية/نهائية إلى الفهرس بعد
  الاكتشاف ودمج الإعدادات
- `isBinaryThinking`: يمتلك المزوّد تجربة استخدام التفكير الثنائي تشغيل/إيقاف
- `supportsXHighThinking`: يضمّن المزوّد نماذج محددة ضمن `xhigh`
- `resolveDefaultThinkingLevel`: يمتلك المزوّد سياسة `/think` الافتراضية
  لعائلة نماذج
- `applyConfigDefaults`: يطبّق المزوّد قيمًا افتراضية عامة خاصة بالمزوّد
  أثناء إنشاء الإعدادات استنادًا إلى وضع المصادقة أو البيئة أو عائلة النموذج
- `isModernModelRef`: يمتلك المزوّد مطابقة النموذج المفضّل في الوضعين المباشر/الاختباري
- `prepareRuntimeAuth`: يحوّل المزوّد بيانات الاعتماد المهيأة إلى رمز وقت تشغيل
  قصير العمر
- `resolveUsageAuth`: يحل المزوّد بيانات اعتماد الاستخدام/الحصص الخاصة بـ `/usage`
  والأسطح ذات الصلة للحالة/التقارير
- `fetchUsageSnapshot`: يمتلك المزوّد جلب/تحليل نقطة نهاية الاستخدام بينما
  يظل الأساس مسؤولًا عن غلاف الملخص والتنسيق
- `onModelSelected`: ينفّذ المزوّد آثارًا جانبية بعد الاختيار مثل
  القياس عن بُعد أو مسك دفاتر الجلسات المملوك للمزوّد

الأمثلة المضمّنة الحالية:

- `anthropic`: توافق احتياطي مستقبلي لـ Claude 4.6، وتلميحات إصلاح المصادقة، وجلب
  نقطة نهاية الاستخدام، وبيانات تعريف مدة صلاحية التخزين المؤقت/عائلة المزوّد، وقيم افتراضية عامة
  للإعدادات مدركة للمصادقة
- `amazon-bedrock`: مطابقة تجاوز السياق وتصنيف أسباب
  التحويل الاحتياطي الخاصتين بـ Bedrock للأخطاء الخاصة بالاختناق/عدم الجاهزية، بالإضافة إلى
  عائلة إعادة التشغيل المشتركة `anthropic-by-model` لحراس سياسة إعادة التشغيل الخاصة بـ Claude فقط
  على حركة Anthropic
- `anthropic-vertex`: حراس سياسة إعادة التشغيل الخاصة بـ Claude فقط على حركة
  رسائل Anthropic
- `openrouter`: معرّفات نماذج تمريرية، وأغلفة طلبات، وتلميحات قدرات المزوّد،
  وتنظيف توقيعات أفكار Gemini على حركة Gemini الوكيلة، وحقن التفكير الوكيلي
  عبر عائلة البث `openrouter-thinking`، وتمرير بيانات التوجيه
  التعريفية، وسياسة مدة صلاحية التخزين المؤقت
- `github-copilot`: التهيئة/تسجيل الدخول بالجهاز، والتوافق الاحتياطي المستقبلي للنموذج،
  وتلميحات نصوص تفكير Claude، وتبادل رمز وقت التشغيل، وجلب نقطة نهاية
  الاستخدام
- `openai`: توافق احتياطي مستقبلي لـ GPT-5.4، وتطبيع
  نقل OpenAI المباشر، وتلميحات فقدان المصادقة المدركة لـ Codex، وقمع Spark،
  وصفوف فهرس OpenAI/Codex التركيبية، وسياسة التفكير/النموذج المباشر، وتطبيع
  الأسماء المستعارة لرموز الاستخدام (`input` / `output` وعائلتي `prompt` / `completion`)، و
  عائلة البث المشتركة `openai-responses-defaults` لأغلفة OpenAI/Codex الأصلية،
  وبيانات تعريف عائلة المزوّد، وتسجيل مزوّد
  توليد الصور المضمّن لـ `gpt-image-1`، وتسجيل مزوّد
  توليد الفيديو المضمّن لـ `sora-2`
- `google` و `google-gemini-cli`: توافق احتياطي مستقبلي لـ Gemini 3.1،
  والتحقق الأصلي من إعادة تشغيل Gemini، وتنظيف إعادة التشغيل عند التمهيد، ووضع
  مخرجات التفكير الموسومة، ومطابقة النماذج الحديثة، وتسجيل مزوّد
  توليد الصور المضمّن لنماذج معاينة الصور Gemini، وتسجيل
  مزوّد توليد الفيديو المضمّن لنماذج Veo؛ كما تمتلك Gemini CLI OAuth أيضًا
  تنسيق رموز ملفات تعريف المصادقة، وتحليل رموز الاستخدام، وجلب
  نقطة نهاية الحصة لأسطح الاستخدام
- `moonshot`: نقل مشترك، وتطبيع حمولة التفكير مملوك للإضافة
- `kilocode`: نقل مشترك، وروؤس طلبات مملوكة للإضافة، وتطبيع حمولة التفكير،
  وتنظيف توقيع أفكار Gemini الوكيل، وسياسة مدة صلاحية التخزين المؤقت
- `zai`: توافق احتياطي مستقبلي لـ GLM-5، وقيم افتراضية لـ `tool_stream`، وسياسة مدة صلاحية التخزين المؤقت،
  وسياسة التفكير الثنائي/النموذج المباشر، ومصادقة الاستخدام + جلب الحصة؛
  وتُنشأ معرّفات `glm-5*` غير المعروفة تركيبيًا من القالب المضمّن `glm-4.7`
- `xai`: تطبيع نقل Responses الأصلي، وإعادة كتابة الأسماء المستعارة `/fast` لنسخ
  Grok السريعة، و`tool_stream` الافتراضي، وتنظيف مخطط الأدوات /
  حمولة التفكير الخاصة بـ xAI، وتسجيل مزوّد توليد الفيديو
  المضمّن لـ `grok-imagine-video`
- `mistral`: بيانات تعريف قدرات مملوكة للإضافة
- `opencode` و `opencode-go`: بيانات تعريف قدرات مملوكة للإضافة بالإضافة إلى
  تنظيف توقيع أفكار Gemini الوكيل
- `alibaba`: فهرس توليد فيديو مملوك للإضافة لمراجع نماذج Wan المباشرة
  مثل `alibaba/wan2.6-t2v`
- `byteplus`: فهارس مملوكة للإضافة بالإضافة إلى تسجيل مزوّد
  توليد الفيديو المضمّن لنماذج Seedance لتحويل النص إلى فيديو/الصورة إلى فيديو
- `fal`: تسجيل مزوّد توليد الفيديو المضمّن لنماذج طرف ثالث مستضافة
  وتسجيل مزوّد توليد الصور لنماذج صور FLUX بالإضافة إلى تسجيل مزوّد
  توليد الفيديو المضمّن لنماذج فيديو طرف ثالث مستضافة
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway`, و `volcengine`:
  فهارس مملوكة للإضافة فقط
- `qwen`: فهارس مملوكة للإضافة للنماذج النصية بالإضافة إلى تسجيلات مزوّدي
  فهم الوسائط وتوليد الفيديو المشتركة لأسطحه متعددة الوسائط؛ يستخدم
  توليد الفيديو في Qwen نقاط نهاية فيديو DashScope القياسية مع نماذج Wan
  مضمّنة مثل `wan2.6-t2v` و `wan2.7-r2v`
- `runway`: تسجيل مزوّد توليد فيديو مملوك للإضافة للنماذج الأصلية المعتمدة على المهام في Runway
  مثل `gen4.5`
- `minimax`: فهارس مملوكة للإضافة، وتسجيل مزوّد
  توليد الفيديو المضمّن لنماذج فيديو Hailuo، وتسجيل مزوّد توليد الصور
  المضمّن لـ `image-01`، واختيار سياسة إعادة تشغيل هجينة Anthropic/OpenAI،
  ومنطق مصادقة/لقطة الاستخدام
- `together`: فهارس مملوكة للإضافة بالإضافة إلى تسجيل مزوّد توليد الفيديو
  المضمّن لنماذج فيديو Wan
- `xiaomi`: فهارس مملوكة للإضافة بالإضافة إلى منطق مصادقة/لقطة الاستخدام

تمتلك الإضافة المضمّنة `openai` الآن معرّفي المزوّدين كليهما: `openai` و
`openai-codex`.

يغطي ذلك المزوّدين الذين ما زالوا يلائمون وسائل النقل العادية في OpenClaw. أمّا المزوّد
الذي يحتاج إلى منفّذ طلبات مخصص بالكامل فهو سطح إضافة منفصل وأعمق.

## تدوير مفاتيح API

- يدعم تدويرًا عامًا للمزوّد لمزوّدين محددين.
- قم بتهيئة مفاتيح متعددة عبر:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (تجاوز مباشر واحد، أعلى أولوية)
  - `<PROVIDER>_API_KEYS` (قائمة مفصولة بفواصل أو فاصلة منقوطة)
  - `<PROVIDER>_API_KEY` (المفتاح الأساسي)
  - `<PROVIDER>_API_KEY_*` (قائمة مرقمة، مثل `<PROVIDER>_API_KEY_1`)
- بالنسبة إلى مزوّدي Google، يتم أيضًا تضمين `GOOGLE_API_KEY` كخيار احتياطي.
- يحافظ ترتيب اختيار المفاتيح على الأولوية ويزيل القيم المكررة.
- لا تُعاد محاولة الطلبات بالمفتاح التالي إلا عند استجابات حد المعدل (على
  سبيل المثال `429` أو `rate_limit` أو `quota` أو `resource exhausted` أو `Too many
concurrent requests` أو `ThrottlingException` أو `concurrency limit reached`،
  أو `workers_ai ... quota limit exceeded`، أو رسائل حدود الاستخدام الدورية).
- تفشل الإخفاقات غير المرتبطة بحد المعدل فورًا؛ لا تتم محاولة تدوير المفاتيح.
- عند فشل كل المفاتيح المرشحة، يُعاد الخطأ النهائي من آخر محاولة.

## المزوّدون المضمّنون (فهرس pi-ai)

يأتي OpenClaw مع فهرس pi‑ai. لا تتطلب هذه المزوّدات **أي**
إعدادات `models.providers`; يكفي فقط تعيين المصادقة + اختيار نموذج.

### OpenAI

- المزوّد: `openai`
- المصادقة: `OPENAI_API_KEY`
- التدوير الاختياري: `OPENAI_API_KEYS` و `OPENAI_API_KEY_1` و `OPENAI_API_KEY_2`، بالإضافة إلى `OPENCLAW_LIVE_OPENAI_KEY` (تجاوز واحد)
- أمثلة للنماذج: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- النقل الافتراضي هو `auto` (WebSocket أولًا، ثم SSE كخيار احتياطي)
- يمكنك التجاوز لكل نموذج عبر `agents.defaults.models["openai/<model>"].params.transport` (`"sse"` أو `"websocket"` أو `"auto"`)
- يتم تفعيل الإحماء المسبق لـ OpenAI Responses WebSocket افتراضيًا عبر `params.openaiWsWarmup` (`true`/`false`)
- يمكن تفعيل المعالجة ذات الأولوية في OpenAI عبر `agents.defaults.models["openai/<model>"].params.serviceTier`
- يقوم `/fast` و `params.fastMode` بربط طلبات Responses المباشرة `openai/*` إلى `service_tier=priority` على `api.openai.com`
- استخدم `params.serviceTier` عندما تريد مستوى صريحًا بدلًا من زر التبديل المشترك `/fast`
- تُطبَّق روؤس الإسناد المخفية الخاصة بـ OpenClaw (`originator`, `version`,
  `User-Agent`) فقط على حركة OpenAI الأصلية إلى `api.openai.com`، وليس على
  الوكلاء العموميين المتوافقين مع OpenAI
- تحتفظ مسارات OpenAI الأصلية أيضًا بقيم Responses `store` وتلميحات التخزين المؤقت للمطالبات
  وتشكيل الحمولة المتوافق مع تفكير OpenAI؛ أما المسارات الوكيلة فلا
- تم حجب `openai/gpt-5.3-codex-spark` عمدًا في OpenClaw لأن OpenAI API المباشر يرفضه؛ ويُعامل Spark على أنه مخصص لـ Codex فقط

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- المزوّد: `anthropic`
- المصادقة: `ANTHROPIC_API_KEY`
- التدوير الاختياري: `ANTHROPIC_API_KEYS` و `ANTHROPIC_API_KEY_1` و `ANTHROPIC_API_KEY_2`، بالإضافة إلى `OPENCLAW_LIVE_ANTHROPIC_KEY` (تجاوز واحد)
- مثال للنموذج: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- تدعم طلبات Anthropic العامة المباشرة زر التبديل المشترك `/fast` و `params.fastMode`، بما في ذلك الحركة الموثقة بمفتاح API وOAuth المرسلة إلى `api.anthropic.com`; ويربط OpenClaw ذلك بـ Anthropic `service_tier` (`auto` مقابل `standard_only`)
- ملاحظة Anthropic: أخبرنا موظفو Anthropic أن استخدام Claude CLI بأسلوب OpenClaw مسموح به مرة أخرى، لذلك يتعامل OpenClaw مع إعادة استخدام Claude CLI واستخدام `claude -p` على أنهما مصرح بهما لهذا التكامل ما لم تنشر Anthropic سياسة جديدة.
- ما يزال رمز إعداد Anthropic متاحًا كمسار رمز مدعوم في OpenClaw، لكن OpenClaw يفضّل الآن إعادة استخدام Claude CLI و `claude -p` عند توفرهما.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- المزوّد: `openai-codex`
- المصادقة: OAuth (ChatGPT)
- مثال للنموذج: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` أو `openclaw models auth login --provider openai-codex`
- النقل الافتراضي هو `auto` (WebSocket أولًا، ثم SSE كخيار احتياطي)
- يمكنك التجاوز لكل نموذج عبر `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"` أو `"websocket"` أو `"auto"`)
- يتم أيضًا تمرير `params.serviceTier` على طلبات Codex Responses الأصلية (`chatgpt.com/backend-api`)
- لا تُرفق روؤس الإسناد المخفية الخاصة بـ OpenClaw (`originator`, `version`,
  `User-Agent`) إلا على حركة Codex الأصلية إلى
  `chatgpt.com/backend-api`، وليس على الوكلاء العموميين المتوافقين مع OpenAI
- يشترك في زر التبديل `/fast` نفسه وإعداد `params.fastMode` نفسه مثل `openai/*` المباشر؛ ويربط OpenClaw ذلك بـ `service_tier=priority`
- يظل `openai-codex/gpt-5.3-codex-spark` متاحًا عندما يكشف فهرس Codex OAuth عنه؛ وذلك يعتمد على الاستحقاق
- يحتفظ `openai-codex/gpt-5.4` بالقيمة الأصلية `contextWindow = 1050000` وحد وقت تشغيل افتراضي `contextTokens = 272000`؛ يمكنك تجاوز حد وقت التشغيل عبر `models.providers.openai-codex.models[].contextTokens`
- ملاحظة سياسة: يدعم OpenAI Codex OAuth صراحةً الأدوات/سير العمل الخارجية مثل OpenClaw.

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [{ id: "gpt-5.4", contextTokens: 160000 }],
      },
    },
  },
}
```

### خيارات أخرى مستضافة بنمط الاشتراك

- [Qwen Cloud](/ar/providers/qwen): سطح مزوّد Qwen Cloud بالإضافة إلى ربط نقاط نهاية Alibaba DashScope وCoding Plan
- [MiniMax](/ar/providers/minimax): وصول MiniMax Coding Plan عبر OAuth أو مفتاح API
- [GLM Models](/ar/providers/glm): نقاط نهاية Z.AI Coding Plan أو API العامة

### OpenCode

- المصادقة: `OPENCODE_API_KEY` (أو `OPENCODE_ZEN_API_KEY`)
- مزوّد وقت تشغيل Zen: `opencode`
- مزوّد وقت تشغيل Go: `opencode-go`
- أمثلة للنماذج: `opencode/claude-opus-4-6`, `opencode-go/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice opencode-zen` أو `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini (مفتاح API)

- المزوّد: `google`
- المصادقة: `GEMINI_API_KEY`
- التدوير الاختياري: `GEMINI_API_KEYS` و `GEMINI_API_KEY_1` و `GEMINI_API_KEY_2`، وخيار `GOOGLE_API_KEY` الاحتياطي، و `OPENCLAW_LIVE_GEMINI_KEY` (تجاوز واحد)
- أمثلة للنماذج: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- التوافق: يتم تطبيع إعداد OpenClaw القديم الذي يستخدم `google/gemini-3.1-flash-preview` إلى `google/gemini-3-flash-preview`
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- تقبل تشغيلات Gemini المباشرة أيضًا `agents.defaults.models["google/<model>"].params.cachedContent`
  (أو الاسم القديم `cached_content`) لتمرير معرّف أصلي من المزوّد
  `cachedContents/...`; وتظهر إصابات التخزين المؤقت في Gemini على شكل OpenClaw `cacheRead`

### Google Vertex و Gemini CLI

- المزوّدان: `google-vertex`, `google-gemini-cli`
- المصادقة: يستخدم Vertex gcloud ADC؛ ويستخدم Gemini CLI تدفق OAuth الخاص به
- تحذير: تكامل Gemini CLI OAuth في OpenClaw غير رسمي. أبلغ بعض المستخدمين عن قيود على حسابات Google بعد استخدام عملاء من أطراف ثالثة. راجع شروط Google واستخدم حسابًا غير حرج إذا اخترت المتابعة.
- يتم شحن Gemini CLI OAuth كجزء من الإضافة المضمّنة `google`.
  - ثبّت Gemini CLI أولًا:
    - `brew install gemini-cli`
    - أو `npm install -g @google/gemini-cli`
  - التمكين: `openclaw plugins enable google`
  - تسجيل الدخول: `openclaw models auth login --provider google-gemini-cli --set-default`
  - النموذج الافتراضي: `google-gemini-cli/gemini-3.1-pro-preview`
  - ملاحظة: **لا** تقوم بلصق معرّف عميل أو سر في `openclaw.json`. يقوم تدفق تسجيل الدخول في CLI بتخزين
    الرموز في ملفات تعريف المصادقة على مضيف البوابة.
  - إذا فشلت الطلبات بعد تسجيل الدخول، فعيّن `GOOGLE_CLOUD_PROJECT` أو `GOOGLE_CLOUD_PROJECT_ID` على مضيف البوابة.
  - يتم تحليل ردود Gemini CLI بصيغة JSON من `response`؛ ويعود الاستخدام إلى
    `stats`، مع تطبيع `stats.cached` إلى OpenClaw `cacheRead`.

### Z.AI (GLM)

- المزوّد: `zai`
- المصادقة: `ZAI_API_KEY`
- مثال للنموذج: `zai/glm-5`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - الأسماء المستعارة: يتم تطبيع `z.ai/*` و `z-ai/*` إلى `zai/*`
  - يكتشف `zai-api-key` نقطة نهاية Z.AI المطابقة تلقائيًا؛ بينما تفرض `zai-coding-global` و `zai-coding-cn` و `zai-global` و `zai-cn` سطحًا محددًا

### Vercel AI Gateway

- المزوّد: `vercel-ai-gateway`
- المصادقة: `AI_GATEWAY_API_KEY`
- مثال للنموذج: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- المزوّد: `kilocode`
- المصادقة: `KILOCODE_API_KEY`
- مثال للنموذج: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- عنوان URL الأساسي: `https://api.kilo.ai/api/gateway/`
- يشحن الفهرس الاحتياطي الثابت `kilocode/kilo/auto`; ويمكن لاكتشاف
  `https://api.kilo.ai/api/gateway/models` المباشر توسيع فهرس وقت التشغيل أكثر.
- يمتلك Kilo Gateway التوجيه upstream الدقيق خلف `kilocode/kilo/auto`،
  وليس مشفّرًا بشكل ثابت في OpenClaw.

راجع [/providers/kilocode](/ar/providers/kilocode) للاطلاع على تفاصيل الإعداد.

### إضافات مزوّدين مضمّنة أخرى

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- مثال للنموذج: `openrouter/auto`
- يطبّق OpenClaw روؤس إسناد التطبيق الموثقة في OpenRouter فقط عندما
  يستهدف الطلب فعليًا `openrouter.ai`
- كما تُقيّد علامات `cache_control` الخاصة بـ Anthropic في OpenRouter
  على مسارات OpenRouter المتحقق منها، وليس على عناوين URL الوكيلة العشوائية
- يظل OpenRouter على المسار الوكيلي المتوافق مع OpenAI، لذا لا يتم
  تمرير تشكيل الطلبات الأصلي الخاص بـ OpenAI فقط (`serviceTier`, Responses `store`,
  تلميحات التخزين المؤقت للمطالبات، حمولات التوافق مع التفكير في OpenAI)
- تحتفظ مراجع OpenRouter المدعومة بـ Gemini فقط بمسار تنظيف توقيع أفكار Gemini الوكيل؛ أما التحقق الأصلي من إعادة تشغيل Gemini وإعادة كتابة التمهيد فيظلان معطلين
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- مثال للنموذج: `kilocode/kilo/auto`
- تحتفظ مراجع Kilo المدعومة بـ Gemini بمسار تنظيف توقيع أفكار Gemini الوكيل نفسه؛ وتتخطى تلميحات `kilocode/kilo/auto` وغيرها من التلميحات الوكيلة غير الداعمة للتفكير الوكيلي حقن التفكير الوكيلي
- MiniMax: ‏`minimax` (مفتاح API) و `minimax-portal` (OAuth)
- المصادقة: `MINIMAX_API_KEY` لـ `minimax`؛ و`MINIMAX_OAUTH_TOKEN` أو `MINIMAX_API_KEY` لـ `minimax-portal`
- مثال للنموذج: `minimax/MiniMax-M2.7` أو `minimax-portal/MiniMax-M2.7`
- تكتب تهيئة MiniMax/إعداد مفتاح API تعريفات صريحة لنموذج M2.7 مع
  `input: ["text", "image"]`; بينما يبقي فهرس المزوّد المضمّن مراجع الدردشة
  نصية فقط إلى أن تتم تهيئة إعدادات ذلك المزوّد
- Moonshot: ‏`moonshot` (`MOONSHOT_API_KEY`)
- مثال للنموذج: `moonshot/kimi-k2.5`
- Kimi Coding: ‏`kimi` (`KIMI_API_KEY` أو `KIMICODE_API_KEY`)
- مثال للنموذج: `kimi/kimi-code`
- Qianfan: ‏`qianfan` (`QIANFAN_API_KEY`)
- مثال للنموذج: `qianfan/deepseek-v3.2`
- Qwen Cloud: ‏`qwen` (`QWEN_API_KEY`, `MODELSTUDIO_API_KEY`, أو `DASHSCOPE_API_KEY`)
- مثال للنموذج: `qwen/qwen3.5-plus`
- NVIDIA: ‏`nvidia` (`NVIDIA_API_KEY`)
- مثال للنموذج: `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun: ‏`stepfun` / `stepfun-plan` (`STEPFUN_API_KEY`)
- أمثلة للنماذج: `stepfun/step-3.5-flash`, `stepfun-plan/step-3.5-flash-2603`
- Together: ‏`together` (`TOGETHER_API_KEY`)
- مثال للنموذج: `together/moonshotai/Kimi-K2.5`
- Venice: ‏`venice` (`VENICE_API_KEY`)
- Xiaomi: ‏`xiaomi` (`XIAOMI_API_KEY`)
- مثال للنموذج: `xiaomi/mimo-v2-flash`
- Vercel AI Gateway: ‏`vercel-ai-gateway` (`AI_GATEWAY_API_KEY`)
- Hugging Face Inference: ‏`huggingface` (`HUGGINGFACE_HUB_TOKEN` أو `HF_TOKEN`)
- Cloudflare AI Gateway: ‏`cloudflare-ai-gateway` (`CLOUDFLARE_AI_GATEWAY_API_KEY`)
- Volcengine: ‏`volcengine` (`VOLCANO_ENGINE_API_KEY`)
- مثال للنموذج: `volcengine-plan/ark-code-latest`
- BytePlus: ‏`byteplus` (`BYTEPLUS_API_KEY`)
- مثال للنموذج: `byteplus-plan/ark-code-latest`
- xAI: ‏`xai` (`XAI_API_KEY`)
  - تستخدم طلبات xAI الأصلية المضمّنة مسار xAI Responses
  - يقوم `/fast` أو `params.fastMode: true` بإعادة كتابة `grok-3` و `grok-3-mini`،
    و `grok-4`، و `grok-4-0709` إلى النسخ `*-fast` الخاصة بها
  - يكون `tool_stream` مفعّلًا افتراضيًا؛ عيّن
    `agents.defaults.models["xai/<model>"].params.tool_stream` إلى `false`
    لتعطيله
- Mistral: ‏`mistral` (`MISTRAL_API_KEY`)
- مثال للنموذج: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: ‏`groq` (`GROQ_API_KEY`)
- Cerebras: ‏`cerebras` (`CEREBRAS_API_KEY`)
  - تستخدم نماذج GLM على Cerebras المعرّفات `zai-glm-4.7` و `zai-glm-4.6`.
  - عنوان URL الأساسي المتوافق مع OpenAI: `https://api.cerebras.ai/v1`.
- GitHub Copilot: ‏`github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- مثال نموذج Hugging Face Inference: ‏`huggingface/deepseek-ai/DeepSeek-R1`; ‏CLI: `openclaw onboard --auth-choice huggingface-api-key`. راجع [Hugging Face (Inference)](/ar/providers/huggingface).

## المزوّدون عبر `models.providers` ‏(مخصص/عنوان URL أساسي)

استخدم `models.providers` (أو `models.json`) لإضافة **مزوّدين مخصصين** أو
وكلاء متوافقين مع OpenAI/Anthropic.

تنشر كثير من إضافات المزوّدين المضمّنة أدناه بالفعل فهرسًا افتراضيًا.
استخدم إدخالات `models.providers.<id>` الصريحة فقط عندما تريد تجاوز
عنوان URL الأساسي أو الروؤس أو قائمة النماذج الافتراضية.

### Moonshot AI (Kimi)

يأتي Moonshot كإضافة مزوّد مضمّنة. استخدم المزوّد المضمّن افتراضيًا،
وأضف إدخال `models.providers.moonshot` صريحًا فقط عندما
تحتاج إلى تجاوز عنوان URL الأساسي أو بيانات تعريف النموذج:

- المزوّد: `moonshot`
- المصادقة: `MOONSHOT_API_KEY`
- مثال للنموذج: `moonshot/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice moonshot-api-key` أو `openclaw onboard --auth-choice moonshot-api-key-cn`

معرّفات نموذج Kimi K2:

[//]: # "moonshot-kimi-k2-model-refs:start"

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
- `moonshot/kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-model-refs:end"

```json5
{
  agents: {
    defaults: { model: { primary: "moonshot/kimi-k2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5" }],
      },
    },
  },
}
```

### Kimi Coding

يستخدم Kimi Coding نقطة النهاية المتوافقة مع Anthropic الخاصة بـ Moonshot AI:

- المزوّد: `kimi`
- المصادقة: `KIMI_API_KEY`
- مثال للنموذج: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

ما يزال `kimi/k2p5` القديم مقبولًا كمعرّف نموذج للتوافق.

### Volcano Engine (Doubao)

يوفر Volcano Engine (火山引擎) الوصول إلى Doubao ونماذج أخرى في الصين.

- المزوّد: `volcengine` (الترميز: `volcengine-plan`)
- المصادقة: `VOLCANO_ENGINE_API_KEY`
- مثال للنموذج: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

تستخدم التهيئة سطح الترميز افتراضيًا، لكن يتم تسجيل فهرس `volcengine/*`
العام في الوقت نفسه.

في منتقيات النماذج الخاصة بالتهيئة/الإعداد، يفضّل خيار مصادقة Volcengine كلا
الصفّين `volcengine/*` و `volcengine-plan/*`. وإذا لم تكن هذه النماذج محملة بعد،
فإن OpenClaw يعود إلى الفهرس غير المصفّى بدلًا من إظهار منتقٍ فارغ
محصور بالمزوّد.

النماذج المتاحة:

- `volcengine/doubao-seed-1-8-251228` ‏(Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` ‏(Kimi K2.5)
- `volcengine/glm-4-7-251222` ‏(GLM 4.7)
- `volcengine/deepseek-v3-2-251201` ‏(DeepSeek V3.2 128K)

نماذج الترميز (`volcengine-plan`):

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus (دولي)

يوفر BytePlus ARK الوصول إلى النماذج نفسها التي يوفرها Volcano Engine للمستخدمين الدوليين.

- المزوّد: `byteplus` (الترميز: `byteplus-plan`)
- المصادقة: `BYTEPLUS_API_KEY`
- مثال للنموذج: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

تستخدم التهيئة سطح الترميز افتراضيًا، لكن يتم تسجيل فهرس `byteplus/*`
العام في الوقت نفسه.

في منتقيات النماذج الخاصة بالتهيئة/الإعداد، يفضّل خيار مصادقة BytePlus كلا
الصفّين `byteplus/*` و `byteplus-plan/*`. وإذا لم تكن هذه النماذج محملة بعد،
فإن OpenClaw يعود إلى الفهرس غير المصفّى بدلًا من إظهار منتقٍ فارغ
محصور بالمزوّد.

النماذج المتاحة:

- `byteplus/seed-1-8-251228` ‏(Seed 1.8)
- `byteplus/kimi-k2-5-260127` ‏(Kimi K2.5)
- `byteplus/glm-4-7-251222` ‏(GLM 4.7)

نماذج الترميز (`byteplus-plan`):

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

يوفر Synthetic نماذج متوافقة مع Anthropic خلف المزوّد `synthetic`:

- المزوّد: `synthetic`
- المصادقة: `SYNTHETIC_API_KEY`
- مثال للنموذج: `synthetic/hf:MiniMaxAI/MiniMax-M2.5`
- CLI: `openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.5", name: "MiniMax M2.5" }],
      },
    },
  },
}
```

### MiniMax

يتم إعداد MiniMax عبر `models.providers` لأنه يستخدم نقاط نهاية مخصصة:

- MiniMax OAuth (عالمي): `--auth-choice minimax-global-oauth`
- MiniMax OAuth (الصين): `--auth-choice minimax-cn-oauth`
- مفتاح API لـ MiniMax (عالمي): `--auth-choice minimax-global-api`
- مفتاح API لـ MiniMax (الصين): `--auth-choice minimax-cn-api`
- المصادقة: `MINIMAX_API_KEY` لـ `minimax`; و`MINIMAX_OAUTH_TOKEN` أو
  `MINIMAX_API_KEY` لـ `minimax-portal`

راجع [/providers/minimax](/ar/providers/minimax) للحصول على تفاصيل الإعداد وخيارات النماذج ومقاطع الإعداد.

على مسار البث المتوافق مع Anthropic في MiniMax، يقوم OpenClaw بتعطيل التفكير
افتراضيًا ما لم تقم بتعيينه صراحةً، ويقوم `/fast on` بإعادة كتابة
`MiniMax-M2.7` إلى `MiniMax-M2.7-highspeed`.

تقسيم القدرات المملوك للإضافة:

- تظل إعدادات النص/الدردشة الافتراضية على `minimax/MiniMax-M2.7`
- يكون توليد الصور هو `minimax/image-01` أو `minimax-portal/image-01`
- يكون فهم الصور هو `MiniMax-VL-01` المملوك للإضافة على مساري مصادقة MiniMax كليهما
- يظل البحث على الويب على معرّف المزوّد `minimax`

### Ollama

يأتي Ollama كإضافة مزوّد مضمّنة ويستخدم API الأصلي الخاص بـ Ollama:

- المزوّد: `ollama`
- المصادقة: لا شيء مطلوب (خادم محلي)
- مثال للنموذج: `ollama/llama3.3`
- التثبيت: [https://ollama.com/download](https://ollama.com/download)

```bash
# ثبّت Ollama، ثم اسحب نموذجًا:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

يتم اكتشاف Ollama محليًا على `http://127.0.0.1:11434` عندما تختار الاشتراك
باستخدام `OLLAMA_API_KEY`، وتضيف إضافة المزوّد المضمّنة Ollama مباشرةً إلى
`openclaw onboard` ومنتقي النموذج. راجع [/providers/ollama](/ar/providers/ollama)
للاطلاع على التهيئة ووضع السحابة/الوضع المحلي والإعداد المخصص.

### vLLM

يأتي vLLM كإضافة مزوّد مضمّنة للخوادم المحلية/المستضافة ذاتيًا المتوافقة مع OpenAI:

- المزوّد: `vllm`
- المصادقة: اختيارية (بحسب خادمك)
- عنوان URL الأساسي الافتراضي: `http://127.0.0.1:8000/v1`

للاشتراك في الاكتشاف التلقائي محليًا (أي قيمة تكفي إذا كان خادمك لا يفرض المصادقة):

```bash
export VLLM_API_KEY="vllm-local"
```

ثم عيّن نموذجًا (استبدله بأحد المعرّفات التي يعيدها `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

راجع [/providers/vllm](/ar/providers/vllm) للتفاصيل.

### SGLang

يأتي SGLang كإضافة مزوّد مضمّنة للخوادم السريعة المتوافقة مع OpenAI والمستضافة ذاتيًا:

- المزوّد: `sglang`
- المصادقة: اختيارية (بحسب خادمك)
- عنوان URL الأساسي الافتراضي: `http://127.0.0.1:30000/v1`

للاشتراك في الاكتشاف التلقائي محليًا (أي قيمة تكفي إذا كان خادمك لا
يفرض المصادقة):

```bash
export SGLANG_API_KEY="sglang-local"
```

ثم عيّن نموذجًا (استبدله بأحد المعرّفات التي يعيدها `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

راجع [/providers/sglang](/ar/providers/sglang) للتفاصيل.

### الوكلاء المحليون (LM Studio و vLLM و LiteLLM وما إلى ذلك)

مثال (متوافق مع OpenAI):

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "Local" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "LMSTUDIO_KEY",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

ملاحظات:

- بالنسبة إلى المزوّدين المخصصين، تكون `reasoning` و `input` و `cost` و `contextWindow` و `maxTokens` اختيارية.
  وعند حذفها، يستخدم OpenClaw افتراضيًا:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- الموصى به: عيّن قيمًا صريحة تطابق حدود الوكيل/النموذج لديك.
- بالنسبة إلى `api: "openai-completions"` على نقاط النهاية غير الأصلية (أي `baseUrl` غير فارغ يكون مضيفه غير `api.openai.com`)، يفرض OpenClaw القيمة `compat.supportsDeveloperRole: false` لتجنب أخطاء 400 من المزوّد بسبب أدوار `developer` غير المدعومة.
- تتخطى أيضًا المسارات الوكيلة المتوافقة مع OpenAI تشكيل الطلبات الأصلي الخاص بـ OpenAI فقط:
  لا `service_tier`، ولا Responses `store`، ولا تلميحات التخزين المؤقت للمطالبات، ولا
  تشكيل الحمولة المتوافق مع تفكير OpenAI، ولا روؤس الإسناد المخفية الخاصة بـ OpenClaw.
- إذا كان `baseUrl` فارغًا/محذوفًا، فسيحتفظ OpenClaw بسلوك OpenAI الافتراضي (الذي يُحل إلى `api.openai.com`).
- لأسباب تتعلق بالأمان، ما تزال قيمة `compat.supportsDeveloperRole: true` الصريحة تُتجاوز على نقاط النهاية غير الأصلية `openai-completions`.

## أمثلة CLI

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

راجع أيضًا: [/gateway/configuration](/ar/gateway/configuration) للاطلاع على أمثلة الإعداد الكاملة.

## ذو صلة

- [النماذج](/ar/concepts/models) — إعداد النموذج والأسماء المستعارة
- [التحويل الاحتياطي للنموذج](/ar/concepts/model-failover) — سلاسل الاحتياط وسلوك إعادة المحاولة
- [مرجع الإعدادات](/ar/gateway/configuration-reference#agent-defaults) — مفاتيح إعداد النموذج
- [المزوّدون](/ar/providers) — أدلة الإعداد لكل مزوّد
