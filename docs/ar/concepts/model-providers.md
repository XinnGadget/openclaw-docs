---
read_when:
    - تحتاج إلى مرجع لإعداد النماذج لكل موفر على حدة
    - تريد أمثلة إعدادات أو أوامر تهيئة CLI لموفري النماذج
summary: نظرة عامة على موفري النماذج مع أمثلة إعدادات + تدفقات CLI
title: موفرو النماذج
x-i18n:
    generated_at: "2026-04-09T01:29:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 53e3141256781002bbe1d7e7b78724a18d061fcf36a203baae04a091b8c9ea1b
    source_path: concepts/model-providers.md
    workflow: 15
---

# موفرو النماذج

تغطي هذه الصفحة **موفري LLM/النماذج** (وليس قنوات الدردشة مثل WhatsApp/Telegram).
للاطلاع على قواعد اختيار النموذج، راجع [/concepts/models](/ar/concepts/models).

## قواعد سريعة

- تستخدم مراجع النماذج الصيغة `provider/model` (مثال: `opencode/claude-opus-4-6`).
- إذا قمت بتعيين `agents.defaults.models`، فسيصبح هو قائمة السماح.
- مساعدات CLI: `openclaw onboard` و`openclaw models list` و`openclaw models set <provider/model>`.
- قواعد وقت التشغيل الاحتياطية، وفحوصات التهدئة، واستمرارية تجاوزات الجلسة
  موثقة في [/concepts/model-failover](/ar/concepts/model-failover).
- `models.providers.*.models[].contextWindow` هي بيانات وصفية أصلية للنموذج؛
  أما `models.providers.*.models[].contextTokens` فهو الحد الفعلي في وقت التشغيل.
- يمكن لإضافات الموفر حقن فهارس النماذج عبر `registerProvider({ catalog })`؛
  ويقوم OpenClaw بدمج هذا الناتج في `models.providers` قبل كتابة
  `models.json`.
- يمكن لبيانات تعريف الموفر إعلان `providerAuthEnvVars` و
  `providerAuthAliases` حتى لا تحتاج فحوصات المصادقة العامة المعتمدة على env ومتغيرات الموفر
  إلى تحميل وقت تشغيل الإضافة. أصبحت خريطة متغيرات env الأساسية المتبقية الآن
  مخصصة فقط لموفري non-plugin/core وبعض حالات الأولوية العامة
  مثل تهيئة Anthropic مع تفضيل مفتاح API أولًا.
- يمكن لإضافات الموفر أيضًا امتلاك سلوك وقت تشغيل الموفر عبر
  `normalizeModelId` و`normalizeTransport` و`normalizeConfig` و
  `applyNativeStreamingUsageCompat` و`resolveConfigApiKey` و
  `resolveSyntheticAuth` و`shouldDeferSyntheticProfileAuth` و
  `resolveDynamicModel` و`prepareDynamicModel` و
  `normalizeResolvedModel` و`contributeResolvedModelCompat` و
  `capabilities` و`normalizeToolSchemas` و
  `inspectToolSchemas` و`resolveReasoningOutputMode` و
  `prepareExtraParams` و`createStreamFn` و`wrapStreamFn` و
  `resolveTransportTurnState` و`resolveWebSocketSessionPolicy` و
  `createEmbeddingProvider` و`formatApiKey` و`refreshOAuth` و
  `buildAuthDoctorHint` و
  `matchesContextOverflowError` و`classifyFailoverReason` و
  `isCacheTtlEligible` و`buildMissingAuthMessage` و`suppressBuiltInModel` و
  `augmentModelCatalog` و`isBinaryThinking` و`supportsXHighThinking` و
  `resolveDefaultThinkingLevel` و`applyConfigDefaults` و`isModernModelRef` و
  `prepareRuntimeAuth` و`resolveUsageAuth` و`fetchUsageSnapshot` و
  `onModelSelected`.
- ملاحظة: إن `capabilities` في وقت تشغيل الموفر هي بيانات وصفية مشتركة للمنفذ
  (عائلة الموفر، وخصائص النصوص والأدوات، وتلميحات النقل/الذاكرة المؤقتة). وهي ليست
  نفسها [لنموذج القدرات العام](/ar/plugins/architecture#public-capability-model)
  الذي يصف ما الذي تسجله الإضافة (استدلال نصي، كلام، إلخ).

## السلوك المملوك لإضافة الموفر

يمكن لإضافات الموفر الآن امتلاك معظم المنطق الخاص بكل موفر بينما يحتفظ OpenClaw
بحلقة الاستدلال العامة.

تقسيم نموذجي:

- `auth[].run` / `auth[].runNonInteractive`: يمتلك الموفر تدفقات التهيئة/تسجيل الدخول
  الخاصة بـ `openclaw onboard` و`openclaw models auth` والإعداد بدون تفاعل
- `wizard.setup` / `wizard.modelPicker`: يمتلك الموفر تسميات خيارات المصادقة،
  والأسماء المستعارة القديمة، وتلميحات قائمة السماح الخاصة بالتهيئة، وإدخالات الإعداد في منتقيات التهيئة/النماذج
- `catalog`: يظهر الموفر في `models.providers`
- `normalizeModelId`: يطبّع الموفر معرّفات النماذج القديمة/المعاينة قبل
  البحث أو التحويل إلى الصيغة القياسية
- `normalizeTransport`: يطبّع الموفر `api` / `baseUrl` الخاصة بعائلة النقل
  قبل التجميع العام للنموذج؛ يتحقق OpenClaw من الموفر المطابق أولًا،
  ثم من إضافات الموفر الأخرى القادرة على التعامل مع الخطافات حتى تغيّر إحداها
  النقل فعلًا
- `normalizeConfig`: يطبّع الموفر إعداد `models.providers.<id>` قبل أن
  يستخدمه وقت التشغيل؛ يتحقق OpenClaw من الموفر المطابق أولًا، ثم من إضافات
  الموفر الأخرى القادرة على التعامل مع الخطافات حتى تغيّر إحداها الإعداد فعلًا. إذا لم
  تُعد كتابة الإعداد بواسطة أي خطاف موفر، فما زالت مساعدات Google-family
  المضمنة تطبّع إدخالات موفري Google المدعومة.
- `applyNativeStreamingUsageCompat`: يطبق الموفر إعادات كتابة توافق استخدام البث الأصلي المدفوعة بنقطة النهاية لموفري الإعدادات
- `resolveConfigApiKey`: يحل الموفر مصادقة env-marker لموفري الإعدادات
  من دون فرض تحميل كامل لمصادقة وقت التشغيل. لدى `amazon-bedrock` أيضًا
  محلل AWS env-marker مدمج هنا، رغم أن مصادقة وقت تشغيل Bedrock تستخدم
  سلسلة AWS SDK الافتراضية.
- `resolveSyntheticAuth`: يمكن للموفر كشف توفر المصادقة المحلية/المستضافة ذاتيًا أو
  المصادقة الأخرى المعتمدة على الإعداد من دون حفظ أسرار نصية صريحة
- `shouldDeferSyntheticProfileAuth`: يمكن للموفر تعليم العناصر النائبة لملفات التعريف الاصطناعية المخزنة
  على أنها أقل أولوية من المصادقة المعتمدة على env/config
- `resolveDynamicModel`: يقبل الموفر معرّفات نماذج غير موجودة بعد في الفهرس
  الثابت المحلي
- `prepareDynamicModel`: يحتاج الموفر إلى تحديث البيانات الوصفية قبل إعادة محاولة
  الحل الديناميكي
- `normalizeResolvedModel`: يحتاج الموفر إلى إعادات كتابة للنقل أو عنوان URL الأساسي
- `contributeResolvedModelCompat`: يساهم الموفر بعلامات التوافق لنماذجه
  الخاصة بالمورّد حتى عندما تصل عبر نقل متوافق آخر
- `capabilities`: ينشر الموفر خصائص النصوص/الأدوات/عائلة الموفر
- `normalizeToolSchemas`: ينظف الموفر مخططات الأدوات قبل أن
  يراها المنفذ المضمّن
- `inspectToolSchemas`: يعرض الموفر تحذيرات المخطط الخاصة بالنقل
  بعد التطبيع
- `resolveReasoningOutputMode`: يختار الموفر عقود مخرجات الاستدلال
  الأصلية مقابل المعلّمة
- `prepareExtraParams`: يضع الموفر قيمًا افتراضية أو يطبّع معلمات الطلب لكل نموذج
- `createStreamFn`: يستبدل الموفر مسار البث العادي بنقل
  مخصص بالكامل
- `wrapStreamFn`: يطبق الموفر أغلفة توافق للرؤوس/الجسم/النموذج في الطلب
- `resolveTransportTurnState`: يوفر الموفر
  رؤوسًا أو بيانات وصفية أصلية للنقل لكل دور
- `resolveWebSocketSessionPolicy`: يوفر الموفر
  رؤوس جلسة WebSocket أصلية أو سياسة تهدئة للجلسة
- `createEmbeddingProvider`: يمتلك الموفر سلوك تضمين الذاكرة عندما
  يكون من الأنسب وجوده مع إضافة الموفر بدلًا من مبدّل التضمين الأساسي
- `formatApiKey`: ينسّق الموفر ملفات تعريف المصادقة المخزنة إلى
  سلسلة `apiKey` الخاصة بوقت التشغيل والمتوقعة من النقل
- `refreshOAuth`: يمتلك الموفر عملية تحديث OAuth عندما لا تكفي
  محدِّثات `pi-ai` المشتركة
- `buildAuthDoctorHint`: يضيف الموفر إرشادات إصلاح عندما يفشل تحديث OAuth
- `matchesContextOverflowError`: يتعرف الموفر على
  أخطاء تجاوز نافذة السياق الخاصة به والتي قد تفوتها الاستدلالات العامة
- `classifyFailoverReason`: يطابق الموفر أخطاء النقل/API الخام الخاصة به
  مع أسباب التحويل الاحتياطي مثل تحديد المعدل أو التحميل الزائد
- `isCacheTtlEligible`: يحدد الموفر أي معرّفات النماذج الصاعدة تدعم TTL لذاكرة التخزين المؤقت للموجهات
- `buildMissingAuthMessage`: يستبدل الموفر خطأ مخزن المصادقة العام
  بتلميح استرداد خاص بالموفر
- `suppressBuiltInModel`: يخفي الموفر الصفوف الصاعدة القديمة ويمكنه إرجاع
  خطأ مملوك للمورّد عند فشل الحل المباشر
- `augmentModelCatalog`: يضيف الموفر صفوف فهرس اصطناعية/نهائية بعد
  الاكتشاف ودمج الإعداد
- `isBinaryThinking`: يمتلك الموفر تجربة استخدام التفكير الثنائية تشغيل/إيقاف
- `supportsXHighThinking`: يمكّن الموفر النماذج المختارة من `xhigh`
- `resolveDefaultThinkingLevel`: يمتلك الموفر سياسة `/think` الافتراضية
  لعائلة نماذج
- `applyConfigDefaults`: يطبق الموفر إعدادات عامة افتراضية خاصة به
  أثناء إنشاء الإعداد اعتمادًا على وضع المصادقة أو env أو عائلة النموذج
- `isModernModelRef`: يمتلك الموفر مطابقة النموذج المفضل في البث المباشر/الاختبارات السريعة
- `prepareRuntimeAuth`: يحول الموفر بيانات الاعتماد المضبوطة إلى
  رمز وقت تشغيل قصير العمر
- `resolveUsageAuth`: يحل الموفر بيانات اعتماد الاستخدام/الحصة لأجل `/usage`
  والأسطح الأخرى ذات الصلة بالحالة/التقارير
- `fetchUsageSnapshot`: يمتلك الموفر عملية جلب/تحليل نقطة نهاية الاستخدام بينما
  يظل القلب مسؤولًا عن الغلاف الملخص والتنسيق
- `onModelSelected`: يشغّل الموفر آثارًا جانبية بعد الاختيار مثل
  القياس عن بُعد أو حفظ الجلسة المملوك للموفر

الأمثلة المضمنة الحالية:

- `anthropic`: دعم احتياطي للتوافق الأمامي مع Claude 4.6، وتلميحات إصلاح المصادقة، وجلب
  نقطة نهاية الاستخدام، وبيانات cache-TTL/عائلة الموفر الوصفية، وإعدادات عامة افتراضية
  واعية بالمصادقة
- `amazon-bedrock`: مطابقة تجاوز السياق المملوكة للموفر وتصنيف
  أسباب التحويل الاحتياطي لأخطاء Bedrock الخاصة بالتقييد/عدم الجاهزية، إضافةً إلى
  عائلة الإعادة المشتركة `anthropic-by-model` لحمايات سياسة الإعادة الخاصة بـ Claude فقط
  على حركة Anthropic
- `anthropic-vertex`: حمايات سياسة إعادة تخص Claude فقط على
  حركة `anthropic-message`
- `openrouter`: معرّفات نماذج تمريرية، وأغلفة طلبات، وتلميحات لقدرات الموفر،
  وتنقية توقيع أفكار Gemini على حركة Gemini عبر الوكيل،
  وحقن الاستدلال عبر الوكيل من خلال عائلة البث `openrouter-thinking`،
  وتمرير بيانات التوجيه الوصفية، وسياسة cache-TTL
- `github-copilot`: التهيئة/تسجيل الدخول بالجهاز، ودعم احتياطي للتوافق الأمامي للنماذج،
  وتلميحات نصوص تفكير Claude، وتبادل رمز وقت التشغيل، وجلب نقطة نهاية
  الاستخدام
- `openai`: دعم احتياطي للتوافق الأمامي لـ GPT-5.4، وتطبيع
  نقل OpenAI المباشر، وتلميحات فقدان المصادقة الواعية بـ Codex، وإخفاء Spark،
  وصفوف فهرس اصطناعية لـ OpenAI/Codex، وسياسة التفكير/النماذج الحية،
  وتطبيع الأسماء المستعارة لرموز الاستخدام (`input` / `output` و`prompt` / `completion`)، وعائلة البث المشتركة
  `openai-responses-defaults` للأغلفة الأصلية لـ OpenAI/Codex،
  وبيانات عائلة الموفر الوصفية، وتسجيل موفر إنشاء الصور المضمن
  لـ `gpt-image-1`، وتسجيل موفر إنشاء الفيديو المضمن
  لـ `sora-2`
- `google` و`google-gemini-cli`: دعم احتياطي للتوافق الأمامي لـ Gemini 3.1،
  والتحقق الأصلي من إعادة Gemini، وتنقية الإعادة في التمهيد، ووضع
  مخرجات الاستدلال المعلّم، ومطابقة النماذج الحديثة، وتسجيل موفر إنشاء
  الصور المضمن لنماذج معاينة صور Gemini، وتسجيل موفر إنشاء
  الفيديو المضمن لنماذج Veo؛ كما أن Gemini CLI OAuth
  يمتلك أيضًا تنسيق رموز ملفات تعريف المصادقة، وتحليل رموز الاستخدام، وجلب
  نقطة نهاية الحصة لأسطح الاستخدام
- `moonshot`: نقل مشترك، وتطبيع مملوك للإضافة لحمولة التفكير
- `kilocode`: نقل مشترك، ورؤوس طلبات مملوكة للإضافة، وتطبيع حمولة الاستدلال،
  وتنقية توقيع أفكار Gemini عبر الوكيل، وسياسة cache-TTL
- `zai`: دعم احتياطي للتوافق الأمامي لـ GLM-5، وإعدادات `tool_stream`
  الافتراضية، وسياسة cache-TTL، وسياسة التفكير الثنائي/النماذج الحية،
  ومصادقة الاستخدام + جلب الحصة؛ وتُنشأ معرّفات `glm-5*` غير المعروفة
  اصطناعيًا من القالب المضمّن `glm-4.7`
- `xai`: تطبيع نقل Responses الأصلي، وإعادات كتابة الاسم المستعار `/fast` لـ
  متغيرات Grok السريعة، و`tool_stream` الافتراضي، وتنظيف
  مخطط الأداة / حمولة الاستدلال الخاص بـ xAI، وتسجيل موفر إنشاء الفيديو المضمن
  لـ `grok-imagine-video`
- `mistral`: بيانات وصفية للقدرات مملوكة للإضافة
- `opencode` و`opencode-go`: بيانات وصفية للقدرات مملوكة للإضافة مع
  تنقية توقيع أفكار Gemini عبر الوكيل
- `alibaba`: فهرس إنشاء فيديو مملوك للإضافة لمراجع نماذج Wan المباشرة
  مثل `alibaba/wan2.6-t2v`
- `byteplus`: فهارس مملوكة للإضافة مع تسجيل موفر إنشاء الفيديو المضمن
  لنماذج Seedance من نص إلى فيديو/من صورة إلى فيديو
- `fal`: تسجيل موفر إنشاء الفيديو المضمن لموفر مستضاف تابع لجهة خارجية
  وتسجيل موفر إنشاء الصور المضمن لنماذج صور FLUX مع تسجيل موفر إنشاء
  الفيديو المضمن لنماذج فيديو مستضافة تابعة لجهة خارجية
- `cloudflare-ai-gateway` و`huggingface` و`kimi` و`nvidia` و`qianfan` و
  `stepfun` و`synthetic` و`venice` و`vercel-ai-gateway` و`volcengine`:
  فهارس مملوكة للإضافة فقط
- `qwen`: فهارس مملوكة للإضافة للنماذج النصية مع تسجيلات موفر
  مشتركة لفهم الوسائط وإنشاء الفيديو لأسطحه متعددة الوسائط؛ يستخدم إنشاء فيديو Qwen
  نقاط نهاية فيديو DashScope القياسية مع نماذج Wan المضمنة مثل
  `wan2.6-t2v` و`wan2.7-r2v`
- `runway`: تسجيل موفر إنشاء الفيديو المملوك للإضافة لنماذج Runway
  الأصلية المعتمدة على المهام مثل `gen4.5`
- `minimax`: فهارس مملوكة للإضافة، وتسجيل موفر إنشاء الفيديو المضمن
  لنماذج فيديو Hailuo، وتسجيل موفر إنشاء الصور المضمن
  لـ `image-01`، واختيار هجين لسياسة الإعادة بين Anthropic/OpenAI،
  ومنطق مصادقة الاستخدام/اللقطة
- `together`: فهارس مملوكة للإضافة مع تسجيل موفر إنشاء الفيديو المضمن
  لنماذج فيديو Wan
- `xiaomi`: فهارس مملوكة للإضافة مع منطق مصادقة الاستخدام/اللقطة

تمتلك إضافة `openai` المضمنة الآن معرّفي الموفر كليهما: `openai` و
`openai-codex`.

يغطي ذلك الموفّرين الذين ما زالوا يناسبون وسائل النقل العادية في OpenClaw. أما الموفّر
الذي يحتاج إلى منفّذ طلبات مخصص بالكامل فهو سطح توسعة منفصل وأعمق.

## تدوير مفاتيح API

- يدعم التدوير العام للمفاتيح لموفّرين محددين.
- اضبط مفاتيح متعددة عبر:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (تجاوز بث مباشر مفرد، أعلى أولوية)
  - `<PROVIDER>_API_KEYS` (قائمة مفصولة بفواصل أو فاصلة منقوطة)
  - `<PROVIDER>_API_KEY` (المفتاح الأساسي)
  - `<PROVIDER>_API_KEY_*` (قائمة مرقمة، مثل `<PROVIDER>_API_KEY_1`)
- بالنسبة إلى موفري Google، يتم أيضًا تضمين `GOOGLE_API_KEY` كبديل احتياطي.
- يحافظ ترتيب اختيار المفاتيح على الأولوية ويزيل القيم المكررة.
- يُعاد تنفيذ الطلبات بالمفتاح التالي فقط عند استجابات تحديد المعدل (على
  سبيل المثال `429` أو `rate_limit` أو `quota` أو `resource exhausted` أو `Too many
concurrent requests` أو `ThrottlingException` أو `concurrency limit reached` أو
  `workers_ai ... quota limit exceeded` أو رسائل حدود الاستخدام الدورية).
- تفشل الأخطاء غير المرتبطة بتحديد المعدل مباشرة؛ ولا تتم محاولة تدوير المفاتيح.
- عند فشل كل المفاتيح المرشحة، يُعاد الخطأ النهائي من آخر محاولة.

## الموفّرون المضمنون (فهرس pi-ai)

يشحن OpenClaw مع فهرس pi‑ai. لا تتطلب هذه الموفّرات أي إعداد
`models.providers`؛ فقط اضبط المصادقة ثم اختر نموذجًا.

### OpenAI

- الموفّر: `openai`
- المصادقة: `OPENAI_API_KEY`
- تدوير اختياري: `OPENAI_API_KEYS` و`OPENAI_API_KEY_1` و`OPENAI_API_KEY_2` بالإضافة إلى `OPENCLAW_LIVE_OPENAI_KEY` (تجاوز مفرد)
- أمثلة النماذج: `openai/gpt-5.4` و`openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- النقل الافتراضي هو `auto` (WebSocket أولًا، ثم SSE احتياطيًا)
- تجاوز لكل نموذج عبر `agents.defaults.models["openai/<model>"].params.transport` (`"sse"` أو `"websocket"` أو `"auto"`)
- يتم تفعيل الإحماء المسبق لـ OpenAI Responses WebSocket افتراضيًا عبر `params.openaiWsWarmup` (`true`/`false`)
- يمكن تمكين المعالجة ذات الأولوية في OpenAI عبر `agents.defaults.models["openai/<model>"].params.serviceTier`
- يربط `/fast` و`params.fastMode` طلبات Responses المباشرة `openai/*` إلى `service_tier=priority` على `api.openai.com`
- استخدم `params.serviceTier` عندما تريد طبقة صريحة بدلًا من مفتاح التبديل المشترك `/fast`
- تنطبق رؤوس الإسناد المخفية الخاصة بـ OpenClaw (`originator` و`version` و
  `User-Agent`) فقط على حركة OpenAI الأصلية إلى `api.openai.com`، وليس على
  الوكلاء العامين المتوافقين مع OpenAI
- تحتفظ مسارات OpenAI الأصلية أيضًا بخاصية `store` في Responses، وتلميحات
  الذاكرة المؤقتة للموجهات، وتشكيل الحمولة المتوافق مع استدلال OpenAI؛ أما
  مسارات الوكيل فلا تفعل ذلك
- يتم إخفاء `openai/gpt-5.3-codex-spark` عمدًا في OpenClaw لأن OpenAI API الحي يرفضه؛ ويُعامل Spark على أنه خاص بـ Codex فقط

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- الموفّر: `anthropic`
- المصادقة: `ANTHROPIC_API_KEY`
- تدوير اختياري: `ANTHROPIC_API_KEYS` و`ANTHROPIC_API_KEY_1` و`ANTHROPIC_API_KEY_2` بالإضافة إلى `OPENCLAW_LIVE_ANTHROPIC_KEY` (تجاوز مفرد)
- مثال النموذج: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- تدعم طلبات Anthropic العامة المباشرة مفتاح التبديل المشترك `/fast` و`params.fastMode`، بما في ذلك الحركة الموثقة بمفتاح API وOAuth المرسلة إلى `api.anthropic.com`؛ ويطابق OpenClaw ذلك مع `service_tier` في Anthropic (`auto` مقابل `standard_only`)
- ملاحظة Anthropic: أخبرنا موظفو Anthropic أن استخدام Claude CLI على نمط OpenClaw مسموح به مجددًا، لذلك يتعامل OpenClaw مع إعادة استخدام Claude CLI واستخدام `claude -p` على أنهما معتمدان لهذا التكامل ما لم تنشر Anthropic سياسة جديدة.
- يظل رمز إعداد Anthropic متاحًا كمسار رمز مدعوم في OpenClaw، لكن OpenClaw يفضل الآن إعادة استخدام Claude CLI و`claude -p` عند توفرهما.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- الموفّر: `openai-codex`
- المصادقة: OAuth ‏(ChatGPT)
- مثال النموذج: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` أو `openclaw models auth login --provider openai-codex`
- النقل الافتراضي هو `auto` (WebSocket أولًا، ثم SSE احتياطيًا)
- تجاوز لكل نموذج عبر `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"` أو `"websocket"` أو `"auto"`)
- يتم أيضًا تمرير `params.serviceTier` على طلبات Codex Responses الأصلية (`chatgpt.com/backend-api`)
- رؤوس الإسناد المخفية الخاصة بـ OpenClaw (`originator` و`version` و
  `User-Agent`) تُرفق فقط على حركة Codex الأصلية إلى
  `chatgpt.com/backend-api`، وليس على الوكلاء العامين المتوافقين مع OpenAI
- يشارك نفس مفتاح التبديل `/fast` وإعداد `params.fastMode` مثل `openai/*` المباشر؛ ويطابق OpenClaw ذلك مع `service_tier=priority`
- يظل `openai-codex/gpt-5.3-codex-spark` متاحًا عندما يعرضه فهرس Codex OAuth؛ ويعتمد على الاستحقاق
- يحتفظ `openai-codex/gpt-5.4` بالقيمة الأصلية `contextWindow = 1050000` وبحد تشغيل افتراضي `contextTokens = 272000`؛ يمكنك تجاوز حد التشغيل عبر `models.providers.openai-codex.models[].contextTokens`
- ملاحظة السياسة: إن OpenAI Codex OAuth مدعوم صراحةً للأدوات/سير العمل الخارجية مثل OpenClaw.

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

### خيارات مستضافة أخرى بنمط الاشتراك

- [Qwen Cloud](/ar/providers/qwen): سطح موفر Qwen Cloud مع تعيين DashScope وCoding Plan
- [MiniMax](/ar/providers/minimax): وصول MiniMax Coding Plan عبر OAuth أو مفتاح API
- [GLM Models](/ar/providers/glm): نقاط نهاية Z.AI Coding Plan أو نقاط نهاية API العامة

### OpenCode

- المصادقة: `OPENCODE_API_KEY` (أو `OPENCODE_ZEN_API_KEY`)
- موفر وقت تشغيل Zen: `opencode`
- موفر وقت تشغيل Go: `opencode-go`
- أمثلة النماذج: `opencode/claude-opus-4-6` و`opencode-go/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice opencode-zen` أو `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini (مفتاح API)

- الموفّر: `google`
- المصادقة: `GEMINI_API_KEY`
- تدوير اختياري: `GEMINI_API_KEYS` و`GEMINI_API_KEY_1` و`GEMINI_API_KEY_2` والبديل الاحتياطي `GOOGLE_API_KEY` و`OPENCLAW_LIVE_GEMINI_KEY` (تجاوز مفرد)
- أمثلة النماذج: `google/gemini-3.1-pro-preview` و`google/gemini-3-flash-preview`
- التوافق: يتم تطبيع إعداد OpenClaw القديم الذي يستخدم `google/gemini-3.1-flash-preview` إلى `google/gemini-3-flash-preview`
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- تقبل تشغيلات Gemini المباشرة أيضًا `agents.defaults.models["google/<model>"].params.cachedContent`
  (أو `cached_content` القديم) لتمرير معرّف
  `cachedContents/...` أصلي خاص بالموفر؛ وتظهر إصابات ذاكرة Gemini المؤقتة في OpenClaw على أنها `cacheRead`

### Google Vertex وGemini CLI

- الموفّران: `google-vertex` و`google-gemini-cli`
- المصادقة: يستخدم Vertex ‏gcloud ADC؛ ويستخدم Gemini CLI تدفق OAuth الخاص به
- تحذير: تكامل Gemini CLI OAuth في OpenClaw غير رسمي. أبلغ بعض المستخدمين عن قيود على حسابات Google بعد استخدام عملاء من جهات خارجية. راجع شروط Google واستخدم حسابًا غير حرج إذا اخترت المتابعة.
- يتم شحن Gemini CLI OAuth كجزء من إضافة `google` المضمنة.
  - ثبّت Gemini CLI أولًا:
    - `brew install gemini-cli`
    - أو `npm install -g @google/gemini-cli`
  - التفعيل: `openclaw plugins enable google`
  - تسجيل الدخول: `openclaw models auth login --provider google-gemini-cli --set-default`
  - النموذج الافتراضي: `google-gemini-cli/gemini-3-flash-preview`
  - ملاحظة: **لا** تقوم بلصق معرّف عميل أو سر في `openclaw.json`. يقوم تدفق تسجيل الدخول في CLI بتخزين
    الرموز في ملفات تعريف المصادقة على مضيف البوابة.
  - إذا فشلت الطلبات بعد تسجيل الدخول، فاضبط `GOOGLE_CLOUD_PROJECT` أو `GOOGLE_CLOUD_PROJECT_ID` على مضيف البوابة.
  - يتم تحليل ردود Gemini CLI بصيغة JSON من `response`؛ بينما يرجع الاستخدام إلى
    `stats`، مع تطبيع `stats.cached` إلى `cacheRead` في OpenClaw.

### Z.AI ‏(GLM)

- الموفّر: `zai`
- المصادقة: `ZAI_API_KEY`
- مثال النموذج: `zai/glm-5.1`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - الأسماء المستعارة: يتم تطبيع `z.ai/*` و`z-ai/*` إلى `zai/*`
  - يكتشف `zai-api-key` تلقائيًا نقطة نهاية Z.AI المطابقة؛ بينما تفرض `zai-coding-global` و`zai-coding-cn` و`zai-global` و`zai-cn` سطحًا محددًا

### Vercel AI Gateway

- الموفّر: `vercel-ai-gateway`
- المصادقة: `AI_GATEWAY_API_KEY`
- مثال النموذج: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- الموفّر: `kilocode`
- المصادقة: `KILOCODE_API_KEY`
- مثال النموذج: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- عنوان URL الأساسي: `https://api.kilo.ai/api/gateway/`
- يشحن فهرس احتياطي ثابت بـ `kilocode/kilo/auto`؛ ويمكن لاكتشاف
  `https://api.kilo.ai/api/gateway/models` المباشر
  توسيع فهرس وقت التشغيل أكثر.
- إن التوجيه الصاعد الدقيق خلف `kilocode/kilo/auto` مملوك لـ Kilo Gateway،
  وليس مبرمجًا بشكل ثابت في OpenClaw.

راجع [/providers/kilocode](/ar/providers/kilocode) للحصول على تفاصيل الإعداد.

### إضافات موفرين مضمّنة أخرى

- OpenRouter: ‏`openrouter` ‏(`OPENROUTER_API_KEY`)
- مثال النموذج: `openrouter/auto`
- يطبق OpenClaw رؤوس إسناد التطبيق الموثقة في OpenRouter فقط عندما
  يستهدف الطلب فعلًا `openrouter.ai`
- كما أن علامات `cache_control` الخاصة بـ Anthropic في OpenRouter مقيّدة أيضًا
  بالمسارات المتحقق منها الخاصة بـ OpenRouter، وليس بأي عناوين URL وكيل عشوائية
- يظل OpenRouter على المسار الوكيل المتوافق مع OpenAI، لذا لا يتم
  تمرير تشكيل الطلبات الأصلي الخاص بـ OpenAI فقط (`serviceTier` و`store` في Responses،
  وتلميحات ذاكرة الموجهات المؤقتة، وحمولات التوافق مع استدلال OpenAI)
- تحتفظ مراجع OpenRouter المدعومة من Gemini فقط بمسار
  تنقية توقيع أفكار Gemini عبر الوكيل؛ بينما يظل التحقق الأصلي من إعادة Gemini وإعادات الكتابة عند التمهيد معطّلًا
- Kilo Gateway: ‏`kilocode` ‏(`KILOCODE_API_KEY`)
- مثال النموذج: `kilocode/kilo/auto`
- تحتفظ مراجع Kilo المدعومة من Gemini بنفس مسار
  تنقية توقيع أفكار Gemini عبر الوكيل؛ أما `kilocode/kilo/auto` وغيرها من التلميحات غير
  المدعومة للاستدلال عبر الوكيل فتتجاوز حقن الاستدلال عبر الوكيل
- MiniMax: ‏`minimax` (مفتاح API) و`minimax-portal` (OAuth)
- المصادقة: `MINIMAX_API_KEY` لـ `minimax`؛ و`MINIMAX_OAUTH_TOKEN` أو `MINIMAX_API_KEY` لـ `minimax-portal`
- مثال النموذج: `minimax/MiniMax-M2.7` أو `minimax-portal/MiniMax-M2.7`
- تكتب تهيئة MiniMax/إعداد مفتاح API تعريفات صريحة لنموذج M2.7 مع
  `input: ["text", "image"]`؛ بينما يبقي فهرس الموفر المضمّن مراجع الدردشة
  نصية فقط إلى أن يتم إنشاء إعداد ذلك الموفر
- Moonshot: ‏`moonshot` ‏(`MOONSHOT_API_KEY`)
- مثال النموذج: `moonshot/kimi-k2.5`
- Kimi Coding: ‏`kimi` ‏(`KIMI_API_KEY` أو `KIMICODE_API_KEY`)
- مثال النموذج: `kimi/kimi-code`
- Qianfan: ‏`qianfan` ‏(`QIANFAN_API_KEY`)
- مثال النموذج: `qianfan/deepseek-v3.2`
- Qwen Cloud: ‏`qwen` ‏(`QWEN_API_KEY` أو `MODELSTUDIO_API_KEY` أو `DASHSCOPE_API_KEY`)
- مثال النموذج: `qwen/qwen3.5-plus`
- NVIDIA: ‏`nvidia` ‏(`NVIDIA_API_KEY`)
- مثال النموذج: `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun: ‏`stepfun` / `stepfun-plan` ‏(`STEPFUN_API_KEY`)
- أمثلة النماذج: `stepfun/step-3.5-flash` و`stepfun-plan/step-3.5-flash-2603`
- Together: ‏`together` ‏(`TOGETHER_API_KEY`)
- مثال النموذج: `together/moonshotai/Kimi-K2.5`
- Venice: ‏`venice` ‏(`VENICE_API_KEY`)
- Xiaomi: ‏`xiaomi` ‏(`XIAOMI_API_KEY`)
- مثال النموذج: `xiaomi/mimo-v2-flash`
- Vercel AI Gateway: ‏`vercel-ai-gateway` ‏(`AI_GATEWAY_API_KEY`)
- Hugging Face Inference: ‏`huggingface` ‏(`HUGGINGFACE_HUB_TOKEN` أو `HF_TOKEN`)
- Cloudflare AI Gateway: ‏`cloudflare-ai-gateway` ‏(`CLOUDFLARE_AI_GATEWAY_API_KEY`)
- Volcengine: ‏`volcengine` ‏(`VOLCANO_ENGINE_API_KEY`)
- مثال النموذج: `volcengine-plan/ark-code-latest`
- BytePlus: ‏`byteplus` ‏(`BYTEPLUS_API_KEY`)
- مثال النموذج: `byteplus-plan/ark-code-latest`
- xAI: ‏`xai` ‏(`XAI_API_KEY`)
  - تستخدم طلبات xAI الأصلية المضمنة مسار xAI Responses
  - يعيد `/fast` أو `params.fastMode: true` كتابة `grok-3` و`grok-3-mini` و
    `grok-4` و`grok-4-0709` إلى متغيراتها `*-fast`
  - يكون `tool_stream` مفعّلًا افتراضيًا؛ اضبط
    `agents.defaults.models["xai/<model>"].params.tool_stream` إلى `false` من أجل
    تعطيله
- Mistral: ‏`mistral` ‏(`MISTRAL_API_KEY`)
- مثال النموذج: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: ‏`groq` ‏(`GROQ_API_KEY`)
- Cerebras: ‏`cerebras` ‏(`CEREBRAS_API_KEY`)
  - تستخدم نماذج GLM على Cerebras المعرّفات `zai-glm-4.7` و`zai-glm-4.6`.
  - عنوان URL الأساسي المتوافق مع OpenAI: ‏`https://api.cerebras.ai/v1`.
- GitHub Copilot: ‏`github-copilot` ‏(`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- مثال نموذج Hugging Face Inference: ‏`huggingface/deepseek-ai/DeepSeek-R1`؛ وCLI: ‏`openclaw onboard --auth-choice huggingface-api-key`. راجع [Hugging Face (Inference)](/ar/providers/huggingface).

## الموفّرون عبر `models.providers` ‏(مخصص/عنوان URL أساسي)

استخدم `models.providers` (أو `models.json`) لإضافة موفّرين **مخصصين** أو
وكلاء متوافقين مع OpenAI/Anthropic.

تنشر العديد من إضافات الموفر المضمنة أدناه بالفعل فهرسًا افتراضيًا.
استخدم إدخالات `models.providers.<id>` الصريحة فقط عندما تريد تجاوز
عنوان URL الأساسي أو الرؤوس أو قائمة النماذج الافتراضية.

### Moonshot AI ‏(Kimi)

يأتي Moonshot كإضافة موفر مضمّنة. استخدم الموفّر المدمج افتراضيًا،
وأضف إدخال `models.providers.moonshot` صريحًا فقط عندما
تحتاج إلى تجاوز عنوان URL الأساسي أو البيانات الوصفية للنموذج:

- الموفّر: `moonshot`
- المصادقة: `MOONSHOT_API_KEY`
- مثال النموذج: `moonshot/kimi-k2.5`
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

- الموفّر: `kimi`
- المصادقة: `KIMI_API_KEY`
- مثال النموذج: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

لا يزال `kimi/k2p5` القديم مقبولًا بوصفه معرّف نموذج للتوافق.

### Volcano Engine ‏(Doubao)

يوفّر Volcano Engine ‏(火山引擎) الوصول إلى Doubao ونماذج أخرى في الصين.

- الموفّر: `volcengine` ‏(البرمجة: `volcengine-plan`)
- المصادقة: `VOLCANO_ENGINE_API_KEY`
- مثال النموذج: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

تستخدم التهيئة سطح البرمجة افتراضيًا، ولكن يتم تسجيل فهرس
`volcengine/*` العام في الوقت نفسه.

في منتقيات التهيئة/تكوين النموذج، يفضّل خيار مصادقة Volcengine كلًا من
الصفوف `volcengine/*` و`volcengine-plan/*`. وإذا لم تكن هذه النماذج قد حُمّلت بعد،
فإن OpenClaw يعود إلى الفهرس غير المفلتر بدلًا من إظهار منتقٍ فارغ
محدّد النطاق حسب الموفّر.

النماذج المتاحة:

- `volcengine/doubao-seed-1-8-251228` ‏(Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` ‏(Kimi K2.5)
- `volcengine/glm-4-7-251222` ‏(GLM 4.7)
- `volcengine/deepseek-v3-2-251201` ‏(DeepSeek V3.2 128K)

نماذج البرمجة (`volcengine-plan`):

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus ‏(دولي)

يوفر BytePlus ARK الوصول إلى النماذج نفسها التي يوفّرها Volcano Engine للمستخدمين الدوليين.

- الموفّر: `byteplus` ‏(البرمجة: `byteplus-plan`)
- المصادقة: `BYTEPLUS_API_KEY`
- مثال النموذج: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

تستخدم التهيئة سطح البرمجة افتراضيًا، ولكن يتم تسجيل فهرس
`byteplus/*` العام في الوقت نفسه.

في منتقيات التهيئة/تكوين النموذج، يفضّل خيار مصادقة BytePlus كلًا من
الصفوف `byteplus/*` و`byteplus-plan/*`. وإذا لم تكن هذه النماذج قد حُمّلت بعد،
فإن OpenClaw يعود إلى الفهرس غير المفلتر بدلًا من إظهار منتقٍ فارغ
محدّد النطاق حسب الموفّر.

النماذج المتاحة:

- `byteplus/seed-1-8-251228` ‏(Seed 1.8)
- `byteplus/kimi-k2-5-260127` ‏(Kimi K2.5)
- `byteplus/glm-4-7-251222` ‏(GLM 4.7)

نماذج البرمجة (`byteplus-plan`):

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

توفّر Synthetic نماذج متوافقة مع Anthropic خلف الموفّر `synthetic`:

- الموفّر: `synthetic`
- المصادقة: `SYNTHETIC_API_KEY`
- مثال النموذج: `synthetic/hf:MiniMaxAI/MiniMax-M2.5`
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

- MiniMax OAuth ‏(عالمي): `--auth-choice minimax-global-oauth`
- MiniMax OAuth ‏(الصين): `--auth-choice minimax-cn-oauth`
- مفتاح API لـ MiniMax ‏(عالمي): `--auth-choice minimax-global-api`
- مفتاح API لـ MiniMax ‏(الصين): `--auth-choice minimax-cn-api`
- المصادقة: `MINIMAX_API_KEY` لـ `minimax`؛ و`MINIMAX_OAUTH_TOKEN` أو
  `MINIMAX_API_KEY` لـ `minimax-portal`

راجع [/providers/minimax](/ar/providers/minimax) للحصول على تفاصيل الإعداد وخيارات النماذج ومقتطفات الإعداد.

في مسار البث المتوافق مع Anthropic في MiniMax، يعطّل OpenClaw التفكير
افتراضيًا ما لم تقم بتعيينه صراحةً، ويعيد `/fast on` كتابة
`MiniMax-M2.7` إلى `MiniMax-M2.7-highspeed`.

تقسيم القدرات المملوك للإضافة:

- تظل الإعدادات الافتراضية للنص/الدردشة على `minimax/MiniMax-M2.7`
- يكون إنشاء الصور على `minimax/image-01` أو `minimax-portal/image-01`
- يكون فهم الصور على `MiniMax-VL-01` المملوك للإضافة على كلا مساري مصادقة MiniMax
- يظل البحث على الويب على معرّف الموفّر `minimax`

### Ollama

يأتي Ollama كإضافة موفر مضمّنة ويستخدم واجهة API الأصلية الخاصة بـ Ollama:

- الموفّر: `ollama`
- المصادقة: غير مطلوبة (خادم محلي)
- مثال النموذج: `ollama/llama3.3`
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

يُكتشف Ollama محليًا على `http://127.0.0.1:11434` عند الاشتراك
باستخدام `OLLAMA_API_KEY`، وتضيف إضافة الموفر المضمنة Ollama مباشرةً إلى
`openclaw onboard` ومنتقي النموذج. راجع [/providers/ollama](/ar/providers/ollama)
للحصول على معلومات التهيئة ووضع السحابة/الوضع المحلي والإعداد المخصص.

### vLLM

يأتي vLLM كإضافة موفر مضمّنة للخوادم المحلية/المستضافة ذاتيًا
المتوافقة مع OpenAI:

- الموفّر: `vllm`
- المصادقة: اختيارية (حسب خادمك)
- عنوان URL الأساسي الافتراضي: `http://127.0.0.1:8000/v1`

للاشتراك في الاكتشاف التلقائي محليًا (أي قيمة تعمل إذا كان خادمك لا يفرض المصادقة):

```bash
export VLLM_API_KEY="vllm-local"
```

ثم اضبط نموذجًا (استبدله بأحد المعرّفات التي يعرضها `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

راجع [/providers/vllm](/ar/providers/vllm) للتفاصيل.

### SGLang

يأتي SGLang كإضافة موفر مضمّنة لخوادم سريعة مستضافة ذاتيًا
ومتوافقة مع OpenAI:

- الموفّر: `sglang`
- المصادقة: اختيارية (حسب خادمك)
- عنوان URL الأساسي الافتراضي: `http://127.0.0.1:30000/v1`

للاشتراك في الاكتشاف التلقائي محليًا (أي قيمة تعمل إذا كان خادمك لا
يفرض المصادقة):

```bash
export SGLANG_API_KEY="sglang-local"
```

ثم اضبط نموذجًا (استبدله بأحد المعرّفات التي يعرضها `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

راجع [/providers/sglang](/ar/providers/sglang) للتفاصيل.

### الوكلاء المحليون ‏(LM Studio وvLLM وLiteLLM وما إلى ذلك)

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

- بالنسبة إلى الموفّرين المخصصين، تكون `reasoning` و`input` و`cost` و`contextWindow` و`maxTokens` اختيارية.
  وعند حذفها، يستخدم OpenClaw القيم الافتراضية التالية:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- يُنصح بتعيين قيم صريحة تطابق حدود الوكيل/النموذج لديك.
- بالنسبة إلى `api: "openai-completions"` على نقاط النهاية غير الأصلية (أي `baseUrl` غير فارغ يكون مضيفه ليس `api.openai.com`)، يفرض OpenClaw القيمة `compat.supportsDeveloperRole: false` لتجنب أخطاء 400 من الموفّر بشأن الأدوار `developer` غير المدعومة.
- تتجاوز مسارات الوكيل المتوافقة مع OpenAI أيضًا
  تشكيل الطلبات الأصلي الخاص بـ OpenAI فقط: لا `service_tier`، ولا `store` في Responses، ولا تلميحات لذاكرة الموجهات المؤقتة، ولا
  تشكيل لحمولات التوافق مع استدلال OpenAI، ولا رؤوس إسناد مخفية خاصة بـ OpenClaw.
- إذا كان `baseUrl` فارغًا/محذوفًا، يحتفظ OpenClaw بسلوك OpenAI الافتراضي (الذي يُحل إلى `api.openai.com`).
- لأغراض السلامة، يتم مع ذلك تجاوز أي `compat.supportsDeveloperRole: true` صريح على نقاط نهاية `openai-completions` غير الأصلية.

## أمثلة CLI

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

راجع أيضًا: [/gateway/configuration](/ar/gateway/configuration) للحصول على أمثلة إعداد كاملة.

## ذو صلة

- [Models](/ar/concepts/models) — إعداد النماذج والأسماء المستعارة
- [Model Failover](/ar/concepts/model-failover) — سلاسل التحويل الاحتياطي وسلوك إعادة المحاولة
- [Configuration Reference](/ar/gateway/configuration-reference#agent-defaults) — مفاتيح إعداد النموذج
- [Providers](/ar/providers) — أدلة إعداد كل موفر
