---
read_when:
    - تحتاج إلى مرجع لإعداد النماذج لكل موفّر على حدة
    - تريد أمثلة على الإعدادات أو أوامر الإعداد عبر CLI لموفّري النماذج
summary: نظرة عامة على موفّر النموذج مع أمثلة على الإعدادات وتدفّقات CLI
title: موفّرو النماذج
x-i18n:
    generated_at: "2026-04-13T07:28:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66ba688c4b4366eec07667571e835d4cfeee684896e2ffae11d601b5fa0a4b98
    source_path: concepts/model-providers.md
    workflow: 15
---

# موفّرو النماذج

تغطي هذه الصفحة **موفّري LLM/النماذج** (وليس قنوات الدردشة مثل WhatsApp/Telegram).
للاطلاع على قواعد اختيار النماذج، راجع [/concepts/models](/ar/concepts/models).

## القواعد السريعة

- تستخدم مراجع النماذج الصيغة `provider/model` (مثال: `opencode/claude-opus-4-6`).
- إذا قمت بتعيين `agents.defaults.models`، فستصبح قائمة السماح.
- مساعدات CLI: `openclaw onboard` و `openclaw models list` و `openclaw models set <provider/model>`.
- قواعد التشغيل الاحتياطي في وقت التشغيل، وفحوصات فترة التهدئة، واستمرارية تجاوزات الجلسات
  موثقة في [/concepts/model-failover](/ar/concepts/model-failover).
- يمثّل `models.providers.*.models[].contextWindow` بيانات تعريف النموذج الأصلية؛
  بينما يمثّل `models.providers.*.models[].contextTokens` الحد الفعّال في وقت التشغيل.
- يمكن لإضافات الموفّر حقن فهارس النماذج عبر `registerProvider({ catalog })`؛
  ويقوم OpenClaw بدمج هذا الناتج في `models.providers` قبل كتابة
  `models.json`.
- يمكن لبيانات تعريف الموفّر التصريحية الإعلان عن `providerAuthEnvVars` و
  `providerAuthAliases` بحيث لا تحتاج فحوصات المصادقة العامة المعتمدة على المتغيرات البيئية ومتغيرات الموفّر
  إلى تحميل وقت تشغيل الإضافة. أصبحت خريطة متغيرات البيئة الأساسية المتبقية الآن
  مخصّصة فقط للموفّرين غير المعتمدين على الإضافات/الأساسيين وبعض حالات الأسبقية العامة
  مثل إعداد Anthropic الذي يعطي أولوية لمفتاح API.
- يمكن لإضافات الموفّر أيضًا امتلاك سلوك وقت تشغيل الموفّر عبر
  `normalizeModelId` و `normalizeTransport` و `normalizeConfig`،
  و `applyNativeStreamingUsageCompat` و `resolveConfigApiKey`،
  و `resolveSyntheticAuth` و `shouldDeferSyntheticProfileAuth`،
  و `resolveDynamicModel` و `prepareDynamicModel`،
  و `normalizeResolvedModel` و `contributeResolvedModelCompat`،
  و `capabilities` و `normalizeToolSchemas`،
  و `inspectToolSchemas` و `resolveReasoningOutputMode`،
  و `prepareExtraParams` و `createStreamFn` و `wrapStreamFn`،
  و `resolveTransportTurnState` و `resolveWebSocketSessionPolicy`،
  و `createEmbeddingProvider` و `formatApiKey` و `refreshOAuth`،
  و `buildAuthDoctorHint`،
  و `matchesContextOverflowError` و `classifyFailoverReason`،
  و `isCacheTtlEligible` و `buildMissingAuthMessage` و `suppressBuiltInModel`،
  و `augmentModelCatalog` و `isBinaryThinking` و `supportsXHighThinking`،
  و `resolveDefaultThinkingLevel` و `applyConfigDefaults` و `isModernModelRef`،
  و `prepareRuntimeAuth` و `resolveUsageAuth` و `fetchUsageSnapshot`، و
  `onModelSelected`.
- ملاحظة: إن `capabilities` الخاصة بوقت تشغيل الموفّر هي بيانات تعريف مشتركة للمشغّل (عائلة الموفّر، وخصائص النصوص وسلوك الأدوات، وتلميحات النقل/التخزين المؤقت). وهي ليست
  نفسها [نموذج الإمكانات العام](/ar/plugins/architecture#public-capability-model)
  الذي يصف ما تسجّله الإضافة (الاستدلال النصي، والكلام، وما إلى ذلك).
- يتم إقران موفّر `codex` المضمّن مع حزمة وكيل Codex المضمّنة.
  استخدم `codex/gpt-*` عندما تريد تسجيل دخول مملوكًا لـ Codex، واكتشافًا للنماذج، واستئنافًا أصليًا
  للسلاسل، وتنفيذًا على خادم التطبيق. تستمر مراجع `openai/gpt-*` العادية
  في استخدام موفّر OpenAI ووسيط نقل الموفّر العادي في OpenClaw.
  يمكن لعمليات النشر الخاصة بـ Codex فقط تعطيل الرجوع التلقائي إلى PI عبر
  `agents.defaults.embeddedHarness.fallback: "none"`؛ راجع
  [Codex Harness](/ar/plugins/codex-harness).

## سلوك الموفّر المملوك للإضافة

يمكن لإضافات الموفّر الآن امتلاك معظم المنطق الخاص بكل موفّر بينما يحافظ OpenClaw
على حلقة الاستدلال العامة.

التقسيم المعتاد:

- `auth[].run` / `auth[].runNonInteractive`: يملك الموفّر تدفقات
  الإعداد/تسجيل الدخول لـ `openclaw onboard` و `openclaw models auth` والإعداد
  غير التفاعلي
- `wizard.setup` / `wizard.modelPicker`: يملك الموفّر تسميات خيارات المصادقة،
  والأسماء المستعارة القديمة، وتلميحات قائمة السماح الخاصة بالإعداد، وإدخالات الإعداد في منتقيات الإعداد/النموذج
- `catalog`: يظهر الموفّر في `models.providers`
- `normalizeModelId`: يطبّع الموفّر معرّفات النماذج القديمة/التجريبية قبل
  البحث أو التحويل إلى صيغة معيارية
- `normalizeTransport`: يطبّع الموفّر `api` / `baseUrl` لعائلة النقل
  قبل التجميع العام للنموذج؛ يتحقق OpenClaw من الموفّر المطابق أولًا،
  ثم من إضافات الموفّر الأخرى القادرة على الخطافات إلى أن يقوم أحدها فعلًا
  بتغيير النقل
- `normalizeConfig`: يطبّع الموفّر إعداد `models.providers.<id>` قبل
  أن يستخدمه وقت التشغيل؛ يتحقق OpenClaw من الموفّر المطابق أولًا، ثم من إضافات الموفّر
  الأخرى القادرة على الخطافات إلى أن يقوم أحدها فعلًا بتغيير الإعداد. إذا لم
  تعِد أي خطافة موفّر كتابة الإعداد، فستستمر مساعدات عائلة Google المضمّنة
  في تطبيع إدخالات موفّر Google المدعومة.
- `applyNativeStreamingUsageCompat`: يطبّق الموفّر عمليات إعادة كتابة توافق استخدام البث الأصلي المعتمدة على نقطة النهاية لموفّري الإعدادات
- `resolveConfigApiKey`: يحلّ الموفّر مصادقة علامات متغيرات البيئة لموفّري الإعدادات
  دون فرض تحميل كامل لمصادقة وقت التشغيل. ويحتوي `amazon-bedrock` أيضًا على
  محلّل علامات بيئة AWS مضمّن هنا، رغم أن مصادقة وقت تشغيل Bedrock تستخدم
  سلسلة AWS SDK الافتراضية.
- `resolveSyntheticAuth`: يمكن للموفّر إتاحة توفر المصادقة المحلية/المستضافة ذاتيًا أو غيرها من المصادقات
  المعتمدة على الإعدادات دون حفظ أسرار نصية صريحة
- `shouldDeferSyntheticProfileAuth`: يمكن للموفّر تمييز عناصر النائب الاصطناعية المخزنة في الملف الشخصي
  على أنها أقل أولوية من المصادقة المعتمدة على البيئة/الإعدادات
- `resolveDynamicModel`: يقبل الموفّر معرّفات النماذج غير الموجودة بعد في
  الفهرس المحلي الثابت
- `prepareDynamicModel`: يحتاج الموفّر إلى تحديث بيانات التعريف قبل إعادة محاولة
  التحليل الديناميكي
- `normalizeResolvedModel`: يحتاج الموفّر إلى عمليات إعادة كتابة للنقل أو عنوان URL الأساسي
- `contributeResolvedModelCompat`: يساهم الموفّر بعلامات التوافق الخاصة
  بنماذج المورّد التابعة له حتى عندما تصل عبر نقل متوافق آخر
- `capabilities`: ينشر الموفّر خصائص النصوص/الأدوات/عائلة الموفّر
- `normalizeToolSchemas`: ينظّف الموفّر مخططات الأدوات قبل أن يراها
  المشغّل المضمّن
- `inspectToolSchemas`: يعرض الموفّر تحذيرات المخططات الخاصة بالنقل
  بعد التطبيع
- `resolveReasoningOutputMode`: يختار الموفّر بين
  عقود مخرجات الاستدلال الأصلية أو الموسومة
- `prepareExtraParams`: يضبط الموفّر افتراضيات أو يطبّع معلمات الطلب لكل نموذج
- `createStreamFn`: يستبدل الموفّر مسار البث العادي بنقل
  مخصّص بالكامل
- `wrapStreamFn`: يطبّق الموفّر أغلفة توافق للرؤوس/نص الطلب/النموذج
- `resolveTransportTurnState`: يوفّر الموفّر رؤوسًا أو بيانات تعريف
  أصلية للنقل لكل دور
- `resolveWebSocketSessionPolicy`: يوفّر الموفّر رؤوس جلسة WebSocket أصلية
  أو سياسة تهدئة الجلسة
- `createEmbeddingProvider`: يملك الموفّر سلوك التضمين للذاكرة عندما
  يكون من الأنسب أن ينتمي إلى إضافة الموفّر بدلًا من لوحة تحويل التضمين الأساسية
- `formatApiKey`: ينسّق الموفّر ملفات تعريف المصادقة المخزنة إلى
  سلسلة `apiKey` الخاصة بوقت التشغيل والمتوقعة من النقل
- `refreshOAuth`: يملك الموفّر تحديث OAuth عندما لا تكون
  أدوات التحديث المشتركة `pi-ai` كافية
- `buildAuthDoctorHint`: يضيف الموفّر إرشادات إصلاح عندما يفشل
  تحديث OAuth
- `matchesContextOverflowError`: يتعرف الموفّر على
  أخطاء تجاوز نافذة السياق الخاصة بالموفّر والتي قد تفوتها الاستدلالات العامة
- `classifyFailoverReason`: يربط الموفّر أخطاء النقل/API الخام الخاصة بالموفّر
  بأسباب الفشل الاحتياطي مثل تجاوز الحد أو الحمل الزائد
- `isCacheTtlEligible`: يحدد الموفّر أي معرّفات النماذج الصادرة من الجهة العليا تدعم مدة صلاحية التخزين المؤقت للموجّه
- `buildMissingAuthMessage`: يستبدل الموفّر خطأ مخزن المصادقة العام
  بتلميح استرداد خاص بالموفّر
- `suppressBuiltInModel`: يُخفي الموفّر الصفوف العليا القديمة ويمكنه إرجاع
  خطأ مملوك للمورّد عند فشل التحليل المباشر
- `augmentModelCatalog`: يُلحق الموفّر صفوف فهرس اصطناعية/نهائية بعد
  الاكتشاف ودمج الإعدادات
- `isBinaryThinking`: يملك الموفّر تجربة استخدام التفكير الثنائي تشغيل/إيقاف
- `supportsXHighThinking`: يضمّن الموفّر نماذج محددة ضمن `xhigh`
- `resolveDefaultThinkingLevel`: يملك الموفّر سياسة `/think` الافتراضية لعائلة
  نماذج معيّنة
- `applyConfigDefaults`: يطبّق الموفّر افتراضيات عامة خاصة به
  أثناء تجسيد الإعدادات استنادًا إلى وضع المصادقة أو البيئة أو عائلة النموذج
- `isModernModelRef`: يملك الموفّر مطابقة النموذج المفضّل للاختبارات الحية/اختبارات الدخان
- `prepareRuntimeAuth`: يحوّل الموفّر بيانات اعتماد مُعدّة مسبقًا إلى
  رمز وقت تشغيل قصير العمر
- `resolveUsageAuth`: يحلّ الموفّر بيانات اعتماد الاستخدام/الحصة لـ `/usage`
  والأسطح الأخرى ذات الصلة بالحالة/التقارير
- `fetchUsageSnapshot`: يملك الموفّر جلب/تحليل نقطة نهاية الاستخدام بينما
  يظل اللبّ مسؤولًا عن هيكل الملخص والتنسيق
- `onModelSelected`: يشغّل الموفّر تأثيرات جانبية بعد الاختيار مثل
  القياس عن بُعد أو مسك الدفاتر الخاص بالجلسة والمملوك للموفّر

الأمثلة المضمّنة الحالية:

- `anthropic`: توافق احتياطي مستقبلي لـ Claude 4.6، وتلميحات إصلاح المصادقة، وجلب
  نقطة نهاية الاستخدام، وبيانات تعريف TTL لذاكرة التخزين المؤقت/عائلة الموفّر، وافتراضيات الإعدادات
  العامة الواعية بالمصادقة
- `amazon-bedrock`: مطابقة تجاوز نافذة السياق المملوكة للموفّر وتصنيف
  أسباب الفشل الاحتياطي لأخطاء Bedrock الخاصة بتقييد المعدّل/عدم الجاهزية، بالإضافة إلى
  عائلة إعادة التشغيل المشتركة `anthropic-by-model` لحواجز سياسة إعادة التشغيل الخاصة بـ Claude فقط
  على حركة مرور Anthropic
- `anthropic-vertex`: حواجز سياسة إعادة التشغيل الخاصة بـ Claude فقط على
  حركة مرور رسائل Anthropic
- `openrouter`: معرّفات نماذج تمرير مباشر، وأغلفة الطلبات، وتلميحات قدرات الموفّر،
  وتنقية توقيع أفكار Gemini على حركة مرور Gemini عبر الوكيل، وحقن
  الاستدلال عبر الوكيل من خلال عائلة البث `openrouter-thinking`،
  وتمرير بيانات تعريف التوجيه، وسياسة TTL لذاكرة التخزين المؤقت
- `github-copilot`: الإعداد/تسجيل الدخول عبر الجهاز، والتوافق الاحتياطي المستقبلي للنموذج،
  وتلميحات نصوص Claude الخاصة بالتفكير، وتبادل رموز وقت التشغيل، وجلب نقطة
  نهاية الاستخدام
- `openai`: توافق احتياطي مستقبلي لـ GPT-5.4، وتطبيع مباشر لنقل OpenAI،
  وتلميحات فقدان المصادقة الواعية بـ Codex، وإخفاء Spark، وصفوف فهرس
  اصطناعية لـ OpenAI/Codex، وسياسة التفكير/النموذج الحي، وتطبيع الأسماء المستعارة
  لرموز الاستخدام (`input` / `output` وعائلتا `prompt` / `completion`)، وعائلة
  البث المشتركة `openai-responses-defaults` للأغلفة الأصلية لـ OpenAI/Codex،
  وبيانات تعريف عائلة الموفّر، وتسجيل موفّر توليد الصور المضمّن
  لـ `gpt-image-1`، وتسجيل موفّر توليد الفيديو المضمّن
  لـ `sora-2`
- `google` و `google-gemini-cli`: توافق احتياطي مستقبلي لـ Gemini 3.1،
  والتحقق الأصلي من إعادة تشغيل Gemini، وتنقية إعادة تشغيل التمهيد، ووضع
  مخرجات الاستدلال الموسومة، ومطابقة النماذج الحديثة، وتسجيل موفّر
  توليد الصور المضمّن لنماذج Gemini image-preview، وتسجيل موفّر
  توليد الفيديو المضمّن لنماذج Veo؛ كما أن OAuth الخاص بـ Gemini CLI
  يملك أيضًا تنسيق رموز ملفات تعريف المصادقة، وتحليل رموز الاستخدام،
  وجلب نقطة نهاية الحصة لأسطح الاستخدام
- `moonshot`: نقل مشترك، وتطبيع حمولة التفكير مملوك للإضافة
- `kilocode`: نقل مشترك، ورؤوس طلبات مملوكة للإضافة، وتطبيع
  حمولة الاستدلال، وتنقية توقيع أفكار Gemini عبر الوكيل،
  وسياسة TTL لذاكرة التخزين المؤقت
- `zai`: توافق احتياطي مستقبلي لـ GLM-5، وافتراضيات `tool_stream`، وسياسة TTL لذاكرة التخزين المؤقت،
  وسياسة التفكير الثنائي/النموذج الحي، ومصادقة الاستخدام + جلب الحصة؛
  وتُنشأ معرّفات `glm-5*` غير المعروفة اصطناعيًا من القالب المضمّن `glm-4.7`
- `xai`: تطبيع نقل Responses الأصلي، وإعادات كتابة الأسماء المستعارة `/fast` لـ
  متغيرات Grok السريعة، و`tool_stream` الافتراضي، وتنظيف
  مخطط الأدوات / حمولة الاستدلال الخاص بـ xAI، وتسجيل موفّر توليد الفيديو
  المضمّن لـ `grok-imagine-video`
- `mistral`: بيانات تعريف القدرات المملوكة للإضافة
- `opencode` و `opencode-go`: بيانات تعريف القدرات المملوكة للإضافة بالإضافة إلى
  تنقية توقيع أفكار Gemini عبر الوكيل
- `alibaba`: فهرس توليد الفيديو المملوك للإضافة لمراجع نماذج Wan المباشرة
  مثل `alibaba/wan2.6-t2v`
- `byteplus`: فهارس مملوكة للإضافة بالإضافة إلى تسجيل موفّر توليد الفيديو المضمّن
  لنماذج Seedance لتحويل النص إلى فيديو/الصورة إلى فيديو
- `fal`: تسجيل موفّر توليد الفيديو المضمّن لنماذج الأطراف الثالثة المستضافة
  وتسجيل موفّر توليد الصور المضمّن لنماذج صور FLUX بالإضافة إلى تسجيل
  موفّر توليد الفيديو المضمّن لنماذج الفيديو المستضافة من أطراف ثالثة
- `cloudflare-ai-gateway` و `huggingface` و `kimi` و `nvidia` و `qianfan`،
  و `stepfun` و `synthetic` و `venice` و `vercel-ai-gateway` و `volcengine`:
  فهارس مملوكة للإضافة فقط
- `qwen`: فهارس مملوكة للإضافة للنماذج النصية بالإضافة إلى تسجيلات
  مشتركة لموفّر فهم الوسائط وتوليد الفيديو لأسطحه متعددة الوسائط؛ يستخدم توليد الفيديو في Qwen
  نقاط نهاية الفيديو القياسية DashScope مع نماذج Wan المضمّنة
  مثل `wan2.6-t2v` و `wan2.7-r2v`
- `runway`: تسجيل موفّر توليد الفيديو المملوك للإضافة لنماذج
  Runway الأصلية المعتمدة على المهام مثل `gen4.5`
- `minimax`: فهارس مملوكة للإضافة، وتسجيل موفّر توليد الفيديو المضمّن
  لنماذج فيديو Hailuo، وتسجيل موفّر توليد الصور المضمّن
  لـ `image-01`، واختيار هجين لسياسة إعادة التشغيل بين Anthropic/OpenAI،
  ومنطق مصادقة/لقطة الاستخدام
- `together`: فهارس مملوكة للإضافة بالإضافة إلى تسجيل موفّر توليد الفيديو المضمّن
  لنماذج فيديو Wan
- `xiaomi`: فهارس مملوكة للإضافة بالإضافة إلى منطق مصادقة/لقطة الاستخدام

أصبحت الإضافة المضمّنة `openai` الآن تملك كلا معرّفي الموفّر:
`openai` و `openai-codex`.

وهذا يغطي الموفّرين الذين ما زالوا يناسبون وسائل النقل العادية في OpenClaw. أما الموفّر
الذي يحتاج إلى منفّذ طلبات مخصّص بالكامل فهو سطح توسعة منفصل وأعمق.

## تدوير مفاتيح API

- يدعم تدويرًا عامًا لمفاتيح الموفّر لموفّرين محددين.
- قم بتهيئة عدة مفاتيح عبر:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (تجاوز حي واحد، أعلى أولوية)
  - `<PROVIDER>_API_KEYS` (قائمة مفصولة بفواصل أو فاصلة منقوطة)
  - `<PROVIDER>_API_KEY` (المفتاح الأساسي)
  - `<PROVIDER>_API_KEY_*` (قائمة مرقمة، مثل `<PROVIDER>_API_KEY_1`)
- بالنسبة إلى موفّري Google، يتم تضمين `GOOGLE_API_KEY` أيضًا كبديل احتياطي.
- يحافظ ترتيب اختيار المفاتيح على الأولوية ويزيل القيم المكررة.
- تُعاد محاولة الطلبات باستخدام المفتاح التالي فقط عند استجابات تجاوز المعدّل (على
  سبيل المثال `429` أو `rate_limit` أو `quota` أو `resource exhausted` أو `Too many
concurrent requests` أو `ThrottlingException` أو `concurrency limit reached`،
  أو `workers_ai ... quota limit exceeded`، أو رسائل حد الاستخدام الدورية).
- تفشل الأخطاء غير المرتبطة بتجاوز المعدّل فورًا؛ ولا تتم محاولة تدوير المفاتيح.
- عندما تفشل جميع المفاتيح المرشحة، يُعاد الخطأ النهائي من آخر محاولة.

## الموفّرون المضمّنون (فهرس pi-ai)

يشحن OpenClaw مع فهرس pi-ai. لا تتطلب هذه الموفّرات أي
إعداد `models.providers`؛ فقط عيّن المصادقة + اختر نموذجًا.

### OpenAI

- الموفّر: `openai`
- المصادقة: `OPENAI_API_KEY`
- التدوير الاختياري: `OPENAI_API_KEYS` و `OPENAI_API_KEY_1` و `OPENAI_API_KEY_2`، بالإضافة إلى `OPENCLAW_LIVE_OPENAI_KEY` (تجاوز واحد)
- أمثلة على النماذج: `openai/gpt-5.4` و `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- النقل الافتراضي هو `auto` (WebSocket أولًا، ثم SSE احتياطيًا)
- يمكنك التجاوز لكل نموذج عبر `agents.defaults.models["openai/<model>"].params.transport` (`"sse"` أو `"websocket"` أو `"auto"`)
- يتم تفعيل الإحماء المسبق لـ OpenAI Responses WebSocket افتراضيًا عبر `params.openaiWsWarmup` (`true`/`false`)
- يمكن تمكين المعالجة ذات الأولوية في OpenAI عبر `agents.defaults.models["openai/<model>"].params.serviceTier`
- تقوم `/fast` و `params.fastMode` بربط طلبات Responses المباشرة `openai/*` بـ `service_tier=priority` على `api.openai.com`
- استخدم `params.serviceTier` عندما تريد مستوى خدمة صريحًا بدلًا من مفتاح التبديل المشترك `/fast`
- تنطبق رؤوس الإسناد المخفية الخاصة بـ OpenClaw (`originator` و `version` و
  `User-Agent`) فقط على حركة مرور OpenAI الأصلية إلى `api.openai.com`، وليس على
  وكلاء OpenAI-compatible العامّين
- تحتفظ مسارات OpenAI الأصلية أيضًا بخاصية Responses `store`، وتلميحات ذاكرة التخزين المؤقت للموجّه، و
  تشكيل حمولة توافق الاستدلال الخاصة بـ OpenAI؛ أما مسارات الوكيل فلا تحتفظ بذلك
- يتم إخفاء `openai/gpt-5.3-codex-spark` عمدًا في OpenClaw لأن واجهة OpenAI API الحية ترفضه؛ ويُعامل Spark على أنه خاص بـ Codex فقط

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- الموفّر: `anthropic`
- المصادقة: `ANTHROPIC_API_KEY`
- التدوير الاختياري: `ANTHROPIC_API_KEYS` و `ANTHROPIC_API_KEY_1` و `ANTHROPIC_API_KEY_2`، بالإضافة إلى `OPENCLAW_LIVE_ANTHROPIC_KEY` (تجاوز واحد)
- مثال على النموذج: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- تدعم طلبات Anthropic العامة المباشرة أيضًا مفتاح التبديل المشترك `/fast` و `params.fastMode`، بما في ذلك حركة المرور المرسلة إلى `api.anthropic.com` والمصادق عليها بمفتاح API وOAuth؛ ويقوم OpenClaw بربط ذلك بـ `service_tier` الخاص بـ Anthropic (`auto` مقابل `standard_only`)
- ملاحظة Anthropic: أخبرنا موظفو Anthropic أن استخدام Claude CLI بأسلوب OpenClaw مسموح مرة أخرى، لذا يتعامل OpenClaw مع إعادة استخدام Claude CLI واستخدام `claude -p` على أنهما معتمدان لهذا التكامل ما لم تنشر Anthropic سياسة جديدة.
- لا يزال رمز إعداد Anthropic متاحًا كمسار رمز مدعوم في OpenClaw، لكن OpenClaw يفضّل الآن إعادة استخدام Claude CLI و `claude -p` عند توفرهما.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- الموفّر: `openai-codex`
- المصادقة: OAuth (ChatGPT)
- مثال على النموذج: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` أو `openclaw models auth login --provider openai-codex`
- النقل الافتراضي هو `auto` (WebSocket أولًا، ثم SSE احتياطيًا)
- يمكنك التجاوز لكل نموذج عبر `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"` أو `"websocket"` أو `"auto"`)
- يتم أيضًا تمرير `params.serviceTier` في طلبات Codex Responses الأصلية (`chatgpt.com/backend-api`)
- لا تُرفق رؤوس الإسناد المخفية الخاصة بـ OpenClaw (`originator` و `version` و
  `User-Agent`) إلا على حركة مرور Codex الأصلية إلى
  `chatgpt.com/backend-api`، وليس على وكلاء OpenAI-compatible العامّين
- يشارك نفس مفتاح التبديل `/fast` وإعداد `params.fastMode` مثل `openai/*` المباشر؛ ويقوم OpenClaw بربط ذلك بـ `service_tier=priority`
- يبقى `openai-codex/gpt-5.3-codex-spark` متاحًا عندما يكشف فهرس Codex OAuth عنه؛ وذلك يعتمد على الاستحقاق
- يحتفظ `openai-codex/gpt-5.4` بقيمته الأصلية `contextWindow = 1050000` وقيمة وقت تشغيل افتراضية `contextTokens = 272000`؛ ويمكنك تجاوز حد وقت التشغيل عبر `models.providers.openai-codex.models[].contextTokens`
- ملاحظة حول السياسة: مصادقة OpenAI Codex عبر OAuth مدعومة صراحةً للأدوات/سير العمل الخارجية مثل OpenClaw.

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

- [Qwen Cloud](/ar/providers/qwen): سطح موفّر Qwen Cloud بالإضافة إلى ربط نقاط نهاية Alibaba DashScope وCoding Plan
- [MiniMax](/ar/providers/minimax): وصول MiniMax Coding Plan عبر OAuth أو مفتاح API
- [GLM Models](/ar/providers/glm): Z.AI Coding Plan أو نقاط نهاية API العامة

### OpenCode

- المصادقة: `OPENCODE_API_KEY` (أو `OPENCODE_ZEN_API_KEY`)
- موفّر وقت تشغيل Zen: `opencode`
- موفّر وقت تشغيل Go: `opencode-go`
- أمثلة على النماذج: `opencode/claude-opus-4-6` و `opencode-go/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice opencode-zen` أو `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini (مفتاح API)

- الموفّر: `google`
- المصادقة: `GEMINI_API_KEY`
- التدوير الاختياري: `GEMINI_API_KEYS` و `GEMINI_API_KEY_1` و `GEMINI_API_KEY_2`، والبديل الاحتياطي `GOOGLE_API_KEY`، و `OPENCLAW_LIVE_GEMINI_KEY` (تجاوز واحد)
- أمثلة على النماذج: `google/gemini-3.1-pro-preview` و `google/gemini-3-flash-preview`
- التوافق: يتم تطبيع إعداد OpenClaw القديم الذي يستخدم `google/gemini-3.1-flash-preview` إلى `google/gemini-3-flash-preview`
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- تقبل عمليات Gemini المباشرة أيضًا `agents.defaults.models["google/<model>"].params.cachedContent`
  (أو `cached_content` القديم) لتمرير معرّف
  `cachedContents/...` أصلي خاص بالموفّر؛ وتظهر إصابات ذاكرة Gemini المؤقتة في OpenClaw على شكل `cacheRead`

### Google Vertex وGemini CLI

- الموفّرون: `google-vertex`، `google-gemini-cli`
- المصادقة: يستخدم Vertex بيانات اعتماد ADC من gcloud؛ ويستخدم Gemini CLI تدفق OAuth الخاص به
- تحذير: إن OAuth الخاص بـ Gemini CLI في OpenClaw تكامل غير رسمي. أبلغ بعض المستخدمين عن قيود على حسابات Google بعد استخدام عملاء من جهات خارجية. راجع شروط Google واستخدم حسابًا غير حرج إذا اخترت المتابعة.
- يتم شحن OAuth الخاص بـ Gemini CLI كجزء من الإضافة المضمّنة `google`.
  - ثبّت Gemini CLI أولًا:
    - `brew install gemini-cli`
    - أو `npm install -g @google/gemini-cli`
  - التمكين: `openclaw plugins enable google`
  - تسجيل الدخول: `openclaw models auth login --provider google-gemini-cli --set-default`
  - النموذج الافتراضي: `google-gemini-cli/gemini-3-flash-preview`
  - ملاحظة: لا تقوم **بلصق** معرّف العميل أو السر في `openclaw.json`. يخزن تدفق تسجيل الدخول في CLI
    الرموز في ملفات تعريف المصادقة على مضيف Gateway.
  - إذا فشلت الطلبات بعد تسجيل الدخول، فعيّن `GOOGLE_CLOUD_PROJECT` أو `GOOGLE_CLOUD_PROJECT_ID` على مضيف Gateway.
  - يتم تحليل ردود JSON الخاصة بـ Gemini CLI من `response`؛ بينما يعود الاستخدام احتياطيًا إلى
    `stats`، مع تطبيع `stats.cached` إلى `cacheRead` في OpenClaw.

### Z.AI (GLM)

- الموفّر: `zai`
- المصادقة: `ZAI_API_KEY`
- مثال على النموذج: `zai/glm-5.1`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - الأسماء المستعارة: يتم تطبيع `z.ai/*` و `z-ai/*` إلى `zai/*`
  - يكتشف `zai-api-key` نقطة نهاية Z.AI المطابقة تلقائيًا؛ بينما يفرض `zai-coding-global` و `zai-coding-cn` و `zai-global` و `zai-cn` سطحًا محددًا

### Vercel AI Gateway

- الموفّر: `vercel-ai-gateway`
- المصادقة: `AI_GATEWAY_API_KEY`
- مثال على النموذج: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- الموفّر: `kilocode`
- المصادقة: `KILOCODE_API_KEY`
- مثال على النموذج: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- عنوان URL الأساسي: `https://api.kilo.ai/api/gateway/`
- يشحن فهرس احتياطي ثابت مع `kilocode/kilo/auto`؛ ويمكن لاكتشاف
  `https://api.kilo.ai/api/gateway/models` الحي توسيع فهرس
  وقت التشغيل بشكل أكبر.
- إن التوجيه الفعلي من المصدر وراء `kilocode/kilo/auto` مملوك لـ Kilo Gateway،
  وليس مضمّنًا بشكل ثابت في OpenClaw.

راجع [/providers/kilocode](/ar/providers/kilocode) للحصول على تفاصيل الإعداد.

### إضافات الموفّرين المضمّنة الأخرى

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- مثال على النموذج: `openrouter/auto`
- يطبّق OpenClaw رؤوس إسناد التطبيق الموثقة في OpenRouter فقط عندما
  يستهدف الطلب فعليًا `openrouter.ai`
- كما تُقيَّد علامات `cache_control` الخاصة بـ Anthropic والمخصصة لـ OpenRouter
  على مسارات OpenRouter المتحقق منها، وليس على عناوين URL الوكيلة العشوائية
- يظل OpenRouter على مسار OpenAI-compatible بنمط الوكيل، لذلك لا يتم
  تمرير تشكيل الطلبات الأصلي الخاص بـ OpenAI فقط (`serviceTier`، و `store` الخاص بـ Responses،
  وتلميحات ذاكرة التخزين المؤقت للموجّه، وحمولات توافق الاستدلال الخاصة بـ OpenAI)
- تحتفظ مراجع OpenRouter المدعومة بـ Gemini فقط بمسار تنقية توقيع أفكار Gemini عبر الوكيل؛
  بينما يظل التحقق الأصلي من إعادة تشغيل Gemini وإعادات كتابة التمهيد معطّلين
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- مثال على النموذج: `kilocode/kilo/auto`
- تحتفظ مراجع Kilo المدعومة بـ Gemini بنفس
  مسار تنقية توقيع أفكار Gemini عبر الوكيل؛ بينما يتجاوز `kilocode/kilo/auto` والتلميحات الأخرى التي لا تدعم استدلال الوكيل
  حقن الاستدلال عبر الوكيل
- MiniMax: `minimax` (مفتاح API) و `minimax-portal` (OAuth)
- المصادقة: `MINIMAX_API_KEY` لـ `minimax`؛ و `MINIMAX_OAUTH_TOKEN` أو `MINIMAX_API_KEY` لـ `minimax-portal`
- مثال على النموذج: `minimax/MiniMax-M2.7` أو `minimax-portal/MiniMax-M2.7`
- يكتب إعداد MiniMax/إعداد مفتاح API تعريفات صريحة لنموذج M2.7 مع
  `input: ["text", "image"]`؛ بينما يبقي فهرس الموفّر المضمّن مراجع الدردشة
  نصية فقط إلى أن يتم تجسيد إعداد ذلك الموفّر
- Moonshot: `moonshot` (`MOONSHOT_API_KEY`)
- مثال على النموذج: `moonshot/kimi-k2.5`
- Kimi Coding: `kimi` (`KIMI_API_KEY` أو `KIMICODE_API_KEY`)
- مثال على النموذج: `kimi/kimi-code`
- Qianfan: `qianfan` (`QIANFAN_API_KEY`)
- مثال على النموذج: `qianfan/deepseek-v3.2`
- Qwen Cloud: `qwen` (`QWEN_API_KEY` أو `MODELSTUDIO_API_KEY` أو `DASHSCOPE_API_KEY`)
- مثال على النموذج: `qwen/qwen3.5-plus`
- NVIDIA: `nvidia` (`NVIDIA_API_KEY`)
- مثال على النموذج: `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun: `stepfun` / `stepfun-plan` (`STEPFUN_API_KEY`)
- أمثلة على النماذج: `stepfun/step-3.5-flash`، `stepfun-plan/step-3.5-flash-2603`
- Together: `together` (`TOGETHER_API_KEY`)
- مثال على النموذج: `together/moonshotai/Kimi-K2.5`
- Venice: `venice` (`VENICE_API_KEY`)
- Xiaomi: `xiaomi` (`XIAOMI_API_KEY`)
- مثال على النموذج: `xiaomi/mimo-v2-flash`
- Vercel AI Gateway: `vercel-ai-gateway` (`AI_GATEWAY_API_KEY`)
- Hugging Face Inference: `huggingface` (`HUGGINGFACE_HUB_TOKEN` أو `HF_TOKEN`)
- Cloudflare AI Gateway: `cloudflare-ai-gateway` (`CLOUDFLARE_AI_GATEWAY_API_KEY`)
- Volcengine: `volcengine` (`VOLCANO_ENGINE_API_KEY`)
- مثال على النموذج: `volcengine-plan/ark-code-latest`
- BytePlus: `byteplus` (`BYTEPLUS_API_KEY`)
- مثال على النموذج: `byteplus-plan/ark-code-latest`
- xAI: `xai` (`XAI_API_KEY`)
  - تستخدم طلبات xAI الأصلية المضمّنة مسار xAI Responses
  - تعيد `/fast` أو `params.fastMode: true` كتابة `grok-3` و `grok-3-mini`،
    و `grok-4` و `grok-4-0709` إلى متغيراتها `*-fast`
  - يكون `tool_stream` مفعّلًا افتراضيًا؛ عيّن
    `agents.defaults.models["xai/<model>"].params.tool_stream` إلى `false` من أجل
    تعطيله
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- مثال على النموذج: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - تستخدم نماذج GLM على Cerebras المعرّفات `zai-glm-4.7` و `zai-glm-4.6`.
  - عنوان URL الأساسي المتوافق مع OpenAI: `https://api.cerebras.ai/v1`.
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- مثال على نموذج Hugging Face Inference: `huggingface/deepseek-ai/DeepSeek-R1`؛ CLI: `openclaw onboard --auth-choice huggingface-api-key`. راجع [Hugging Face (Inference)](/ar/providers/huggingface).

## الموفّرون عبر `models.providers` (عنوان URL مخصّص/أساسي)

استخدم `models.providers` (أو `models.json`) لإضافة موفّرين **مخصّصين** أو
وكلاء متوافقين مع OpenAI/Anthropic.

تنشر العديد من إضافات الموفّرين المضمّنة أدناه بالفعل فهرسًا افتراضيًا.
استخدم إدخالات `models.providers.<id>` الصريحة فقط عندما تريد تجاوز
عنوان URL الأساسي أو الرؤوس أو قائمة النماذج الافتراضية.

### Moonshot AI (Kimi)

يُشحن Moonshot كإضافة موفّر مضمّنة. استخدم الموفّر المضمّن
افتراضيًا، وأضف إدخال `models.providers.moonshot` صريحًا فقط عندما
تحتاج إلى تجاوز عنوان URL الأساسي أو بيانات تعريف النموذج:

- الموفّر: `moonshot`
- المصادقة: `MOONSHOT_API_KEY`
- مثال على النموذج: `moonshot/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice moonshot-api-key` أو `openclaw onboard --auth-choice moonshot-api-key-cn`

معرّفات نماذج Kimi K2:

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
- مثال على النموذج: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

يبقى `kimi/k2p5` القديم مقبولًا بوصفه معرّف نموذج للتوافق.

### Volcano Engine (Doubao)

يوفّر Volcano Engine (火山引擎) إمكانية الوصول إلى Doubao ونماذج أخرى في الصين.

- الموفّر: `volcengine` (الترميز: `volcengine-plan`)
- المصادقة: `VOLCANO_ENGINE_API_KEY`
- مثال على النموذج: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

يكون الإعداد الافتراضي موجّهًا إلى سطح البرمجة، لكن فهرس
`volcengine/*` العام يُسجَّل في الوقت نفسه.

في منتقيات الإعداد/تكوين النموذج، يفضّل خيار مصادقة Volcengine صفوف
`volcengine/*` و `volcengine-plan/*` معًا. إذا لم تكن هذه النماذج محمّلة بعد،
فإن OpenClaw يعود إلى الفهرس غير المفلتر بدلًا من عرض منتقٍ فارغ
مقيّد بنطاق الموفّر.

النماذج المتاحة:

- `volcengine/doubao-seed-1-8-251228` (Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` (Kimi K2.5)
- `volcengine/glm-4-7-251222` (GLM 4.7)
- `volcengine/deepseek-v3-2-251201` (DeepSeek V3.2 128K)

نماذج البرمجة (`volcengine-plan`):

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus (الدولي)

يوفّر BytePlus ARK الوصول إلى النماذج نفسها التي يوفّرها Volcano Engine للمستخدمين الدوليين.

- الموفّر: `byteplus` (البرمجة: `byteplus-plan`)
- المصادقة: `BYTEPLUS_API_KEY`
- مثال على النموذج: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

يكون الإعداد الافتراضي موجّهًا إلى سطح البرمجة، لكن فهرس
`byteplus/*` العام يُسجَّل في الوقت نفسه.

في منتقيات الإعداد/تكوين النموذج، يفضّل خيار مصادقة BytePlus صفوف
`byteplus/*` و `byteplus-plan/*` معًا. إذا لم تكن هذه النماذج محمّلة بعد،
فإن OpenClaw يعود إلى الفهرس غير المفلتر بدلًا من عرض منتقٍ فارغ
مقيّد بنطاق الموفّر.

النماذج المتاحة:

- `byteplus/seed-1-8-251228` (Seed 1.8)
- `byteplus/kimi-k2-5-260127` (Kimi K2.5)
- `byteplus/glm-4-7-251222` (GLM 4.7)

نماذج البرمجة (`byteplus-plan`):

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

يوفّر Synthetic نماذج متوافقة مع Anthropic خلف الموفّر `synthetic`:

- الموفّر: `synthetic`
- المصادقة: `SYNTHETIC_API_KEY`
- مثال على النموذج: `synthetic/hf:MiniMaxAI/MiniMax-M2.5`
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

يتم تكوين MiniMax عبر `models.providers` لأنه يستخدم نقاط نهاية مخصّصة:

- MiniMax OAuth (عالمي): `--auth-choice minimax-global-oauth`
- MiniMax OAuth (الصين): `--auth-choice minimax-cn-oauth`
- مفتاح API لـ MiniMax (عالمي): `--auth-choice minimax-global-api`
- مفتاح API لـ MiniMax (الصين): `--auth-choice minimax-cn-api`
- المصادقة: `MINIMAX_API_KEY` لـ `minimax`؛ و `MINIMAX_OAUTH_TOKEN` أو
  `MINIMAX_API_KEY` لـ `minimax-portal`

راجع [/providers/minimax](/ar/providers/minimax) للحصول على تفاصيل الإعداد وخيارات النماذج ومقتطفات الإعداد.

في مسار البث المتوافق مع Anthropic الخاص بـ MiniMax، يعطّل OpenClaw التفكير
افتراضيًا ما لم تقم بتعيينه صراحةً، كما أن `/fast on` يعيد كتابة
`MiniMax-M2.7` إلى `MiniMax-M2.7-highspeed`.

تقسيم القدرات المملوك للإضافة:

- تظل افتراضيات النص/الدردشة على `minimax/MiniMax-M2.7`
- يكون توليد الصور على `minimax/image-01` أو `minimax-portal/image-01`
- يكون فهم الصور على `MiniMax-VL-01` المملوك للإضافة على مساري مصادقة MiniMax كليهما
- يظل البحث على الويب على معرّف الموفّر `minimax`

### LM Studio

يُشحن LM Studio كإضافة موفّر مضمّنة تستخدم API الأصلية:

- الموفّر: `lmstudio`
- المصادقة: `LM_API_TOKEN`
- عنوان URL الأساسي الافتراضي للاستدلال: `http://localhost:1234/v1`

ثم عيّن نموذجًا (استبدله بأحد المعرّفات التي يعيدها `http://localhost:1234/api/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "lmstudio/openai/gpt-oss-20b" } },
  },
}
```

يستخدم OpenClaw نقطتي النهاية الأصليتين في LM Studio وهما `/api/v1/models` و `/api/v1/models/load`
للاكتشاف + التحميل التلقائي، ويستخدم `/v1/chat/completions` للاستدلال افتراضيًا.
راجع [/providers/lmstudio](/ar/providers/lmstudio) للحصول على الإعداد واستكشاف الأخطاء وإصلاحها.

### Ollama

يُشحن Ollama كإضافة موفّر مضمّنة ويستخدم API الأصلية الخاصة بـ Ollama:

- الموفّر: `ollama`
- المصادقة: لا شيء مطلوب (خادم محلي)
- مثال على النموذج: `ollama/llama3.3`
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

يتم اكتشاف Ollama محليًا على `http://127.0.0.1:11434` عندما تشترك
باستخدام `OLLAMA_API_KEY`، وتضيف إضافة الموفّر المضمّنة Ollama مباشرةً إلى
`openclaw onboard` ومنتقي النماذج. راجع [/providers/ollama](/ar/providers/ollama)
للاطلاع على الإعداد، ووضع السحابة/الوضع المحلي، والإعدادات المخصّصة.

### vLLM

يُشحن vLLM كإضافة موفّر مضمّنة للخوادم المحلية/المستضافة ذاتيًا
المتوافقة مع OpenAI:

- الموفّر: `vllm`
- المصادقة: اختيارية (بحسب خادمك)
- عنوان URL الأساسي الافتراضي: `http://127.0.0.1:8000/v1`

للاشتراك في الاكتشاف التلقائي محليًا (أي قيمة تعمل إذا لم يفرض خادمك المصادقة):

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

يُشحن SGLang كإضافة موفّر مضمّنة للخوادم السريعة المستضافة ذاتيًا
المتوافقة مع OpenAI:

- الموفّر: `sglang`
- المصادقة: اختيارية (بحسب خادمك)
- عنوان URL الأساسي الافتراضي: `http://127.0.0.1:30000/v1`

للاشتراك في الاكتشاف التلقائي محليًا (أي قيمة تعمل إذا كان خادمك لا
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

### الوكلاء المحليون (LM Studio وvLLM وLiteLLM وما إلى ذلك)

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
        apiKey: "${LM_API_TOKEN}",
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

- بالنسبة إلى الموفّرين المخصّصين، فإن `reasoning` و `input` و `cost` و `contextWindow` و `maxTokens` اختيارية.
  وعند حذفها، يستخدم OpenClaw القيم الافتراضية التالية:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- يُنصح بذلك: عيّن قيمًا صريحة تطابق حدود الوكيل/النموذج لديك.
- بالنسبة إلى `api: "openai-completions"` على نقاط النهاية غير الأصلية (أي `baseUrl` غير فارغ لا يكون مضيفه `api.openai.com`)، يفرض OpenClaw القيمة `compat.supportsDeveloperRole: false` لتجنب أخطاء 400 من الموفّر بسبب أدوار `developer` غير المدعومة.
- كما تتجاوز مسارات OpenAI-compatible بنمط الوكيل أيضًا
  تشكيل الطلبات الأصلي الخاص بـ OpenAI فقط: لا `service_tier`، ولا `store` الخاص بـ Responses، ولا تلميحات لذاكرة التخزين المؤقت للموجّه، ولا
  تشكيل لحمولة توافق الاستدلال الخاصة بـ OpenAI، ولا رؤوس إسناد مخفية خاصة بـ OpenClaw.
- إذا كان `baseUrl` فارغًا/محذوفًا، يحتفظ OpenClaw بسلوك OpenAI الافتراضي (الذي يُحل إلى `api.openai.com`).
- من أجل السلامة، يتم مع ذلك تجاوز `compat.supportsDeveloperRole: true` الصريح على نقاط نهاية `openai-completions` غير الأصلية.

## أمثلة CLI

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

راجع أيضًا: [/gateway/configuration](/ar/gateway/configuration) للحصول على أمثلة إعدادات كاملة.

## ذو صلة

- [النماذج](/ar/concepts/models) — إعدادات النماذج والأسماء المستعارة
- [الفشل الاحتياطي للنماذج](/ar/concepts/model-failover) — سلاسل الفشل الاحتياطي وسلوك إعادة المحاولة
- [مرجع الإعدادات](/ar/gateway/configuration-reference#agent-defaults) — مفاتيح إعدادات النموذج
- [الموفّرون](/ar/providers) — أدلة الإعداد لكل موفّر
