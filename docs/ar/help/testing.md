---
read_when:
    - تشغيل الاختبارات محليًا أو في CI
    - إضافة اختبارات انحدار لأخطاء النموذج/المزوّد
    - تصحيح سلوك Gateway + الوكيل
summary: 'مجموعة الاختبار: أجنحة unit/e2e/live، ومشغّلات Docker، وما الذي يغطيه كل اختبار'
title: الاختبار
x-i18n:
    generated_at: "2026-04-16T21:51:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: af2bc0e9b5e08ca3119806d355b517290f6078fda430109e7a0b153586215e34
    source_path: help/testing.md
    workflow: 15
---

# الاختبار

يحتوي OpenClaw على ثلاث مجموعات Vitest ‏(unit/integration و e2e و live) ومجموعة صغيرة من مشغّلات Docker.

هذا المستند هو دليل «كيف نختبر»:

- ما الذي تغطيه كل مجموعة (وما الذي لا تغطيه عمدًا)
- الأوامر التي يجب تشغيلها لسير العمل الشائع (محليًا، قبل الدفع، وتصحيح الأخطاء)
- كيف تكتشف الاختبارات الحية بيانات الاعتماد وتحدّد النماذج/المزوّدين
- كيفية إضافة اختبارات انحدار لمشكلات النموذج/المزوّد في العالم الحقيقي

## البداية السريعة

في معظم الأيام:

- البوابة الكاملة (متوقعة قبل الدفع): `pnpm build && pnpm check && pnpm test`
- تشغيل أسرع للمجموعة الكاملة محليًا على جهاز واسع الموارد: `pnpm test:max`
- حلقة مراقبة Vitest مباشرة: `pnpm test:watch`
- استهداف ملف مباشر يوجّه الآن أيضًا مسارات الإضافات/القنوات: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- فضّل التشغيلات الموجّهة أولًا عندما تكون تكرّر العمل على فشل واحد.
- موقع QA مدعوم بـ Docker: `pnpm qa:lab:up`
- مسار QA مدعوم بآلة Linux افتراضية: `pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

عندما تلمس الاختبارات أو تريد ثقة إضافية:

- بوابة التغطية: `pnpm test:coverage`
- مجموعة E2E: `pnpm test:e2e`

عند تصحيح مزوّدين/نماذج حقيقية (يتطلب بيانات اعتماد حقيقية):

- المجموعة الحية (فحوصات النماذج + Gateway للأدوات/الصور): `pnpm test:live`
- استهدف ملفًا حيًا واحدًا بهدوء: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

نصيحة: عندما تحتاج فقط إلى حالة فاشلة واحدة، ففضّل تضييق الاختبارات الحية عبر متغيرات بيئة قائمة السماح الموضحة أدناه.

## مشغّلات خاصة بـ QA

توجد هذه الأوامر إلى جانب مجموعات الاختبار الرئيسية عندما تحتاج إلى واقعية QA-lab:

- `pnpm openclaw qa suite`
  - يشغّل سيناريوهات QA المدعومة من المستودع مباشرة على المضيف.
  - يشغّل عدة سيناريوهات محددة بالتوازي افتراضيًا مع عمّال Gateway معزولين، حتى 64 عاملًا أو عدد السيناريوهات المحددة. استخدم `--concurrency <count>` لضبط عدد العمّال، أو `--concurrency 1` للمسار التسلسلي الأقدم.
- `pnpm openclaw qa suite --runner multipass`
  - يشغّل مجموعة QA نفسها داخل آلة Multipass Linux افتراضية قابلة للتخلص منها.
  - يحافظ على سلوك تحديد السيناريو نفسه مثل `qa suite` على المضيف.
  - يعيد استخدام علامات تحديد المزوّد/النموذج نفسها مثل `qa suite`.
  - التشغيلات الحية تمرّر مدخلات مصادقة QA المدعومة والعملية للضيف:
    مفاتيح المزوّد المعتمدة على env، ومسار إعداد مزوّد QA الحي، و `CODEX_HOME` عند وجوده.
  - يجب أن تبقى مجلدات الإخراج تحت جذر المستودع حتى يتمكن الضيف من الكتابة مرة أخرى عبر مساحة العمل المركبة.
  - يكتب تقرير QA العادي + الملخص بالإضافة إلى سجلات Multipass تحت
    `.artifacts/qa-e2e/...`.
- `pnpm qa:lab:up`
  - يبدأ موقع QA المدعوم بـ Docker لأعمال QA على نمط المشغّل.
- `pnpm openclaw qa matrix`
  - يشغّل مسار Matrix QA الحي مقابل خادم Tuwunel منزلي مؤقت ومدعوم بـ Docker.
  - مضيف QA هذا مخصص حاليًا للمستودع/التطوير فقط. لا تشحن تثبيتات OpenClaw المعبأة `qa-lab`، لذلك فهي لا تعرض `openclaw qa`.
  - تحمّل نسخ المستودع العاملة المشغّل المضمن مباشرة؛ لا حاجة إلى خطوة تثبيت Plugin منفصلة.
  - يوفّر ثلاثة مستخدمي Matrix مؤقتين (`driver` و `sut` و `observer`) بالإضافة إلى غرفة خاصة واحدة، ثم يبدأ عملية QA Gateway فرعية مع Plugin Matrix الحقيقي كناقل SUT.
  - يستخدم صورة Tuwunel الثابتة المثبتة `ghcr.io/matrix-construct/tuwunel:v1.5.1` افتراضيًا. تجاوز ذلك باستخدام `OPENCLAW_QA_MATRIX_TUWUNEL_IMAGE` عندما تحتاج إلى اختبار صورة مختلفة.
  - لا يعرّض Matrix علامات مصدر بيانات اعتماد مشتركة لأن المسار يوفّر مستخدمين مؤقتين محليًا.
  - يكتب تقرير Matrix QA وملخصًا و artifact للأحداث المرصودة وسجل إخراج stdout/stderr المجمّع تحت `.artifacts/qa-e2e/...`.
- `pnpm openclaw qa telegram`
  - يشغّل مسار Telegram QA الحي مقابل مجموعة خاصة حقيقية باستخدام رمزي bot الخاصين بـ driver و SUT من env.
  - يتطلب `OPENCLAW_QA_TELEGRAM_GROUP_ID` و `OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` و `OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`. يجب أن يكون معرّف المجموعة هو معرّف دردشة Telegram الرقمي.
  - يدعم `--credential-source convex` لبيانات الاعتماد المشتركة المجمّعة. استخدم وضع env افتراضيًا، أو اضبط `OPENCLAW_QA_CREDENTIAL_SOURCE=convex` للاشتراك في حجوزات مجمّعة.
  - يتطلب botين مختلفين في المجموعة الخاصة نفسها، مع تعريض bot الخاص بـ SUT لاسم مستخدم Telegram.
  - للحصول على مراقبة مستقرة من bot إلى bot، فعّل وضع Bot-to-Bot Communication Mode في `@BotFather` لكلا botين، وتأكد من أن bot الخاص بـ driver يمكنه مراقبة حركة bot في المجموعة.
  - يكتب تقرير Telegram QA وملخصًا و artifact للرسائل المرصودة تحت `.artifacts/qa-e2e/...`.

تشارك مسارات النقل الحية عقدًا قياسيًا واحدًا حتى لا تنحرف وسائل النقل الجديدة:

يبقى `qa-channel` مجموعة QA الاصطناعية الواسعة وليس جزءًا من مصفوفة تغطية النقل الحي.

| المسار | Canary | بوابة الإشارة | حظر قائمة السماح | رد على المستوى الأعلى | استئناف بعد إعادة التشغيل | متابعة الخيط | عزل الخيط | مراقبة التفاعل | أمر المساعدة |
| ------- | ------ | -------------- | ---------------- | ---------------------- | -------------------------- | ------------ | ---------- | --------------- | ------------ |
| Matrix   | x      | x              | x                | x                      | x                          | x            | x          | x               |              |
| Telegram | x      |                |                  |                        |                            |              |            |                 | x            |

### بيانات اعتماد Telegram المشتركة عبر Convex (الإصدار 1)

عند تمكين `--credential-source convex` (أو `OPENCLAW_QA_CREDENTIAL_SOURCE=convex`) لـ
`openclaw qa telegram`، يحصل QA lab على حجز حصري من مجموعة مدعومة بـ Convex، ويرسل Heartbeat لذلك الحجز أثناء تشغيل المسار، ويحرّر الحجز عند الإيقاف.

هيكل مشروع Convex المرجعي:

- `qa/convex-credential-broker/`

متغيرات env المطلوبة:

- `OPENCLAW_QA_CONVEX_SITE_URL` (على سبيل المثال `https://your-deployment.convex.site`)
- سر واحد للدور المحدد:
  - `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER` للدور `maintainer`
  - `OPENCLAW_QA_CONVEX_SECRET_CI` للدور `ci`
- تحديد دور بيانات الاعتماد:
  - CLI: `--credential-role maintainer|ci`
  - القيمة الافتراضية في env: ‏`OPENCLAW_QA_CREDENTIAL_ROLE` (القيمة الافتراضية `maintainer`)

متغيرات env الاختيارية:

- `OPENCLAW_QA_CREDENTIAL_LEASE_TTL_MS` (الافتراضي `1200000`)
- `OPENCLAW_QA_CREDENTIAL_HEARTBEAT_INTERVAL_MS` (الافتراضي `30000`)
- `OPENCLAW_QA_CREDENTIAL_ACQUIRE_TIMEOUT_MS` (الافتراضي `90000`)
- `OPENCLAW_QA_CREDENTIAL_HTTP_TIMEOUT_MS` (الافتراضي `15000`)
- `OPENCLAW_QA_CONVEX_ENDPOINT_PREFIX` (الافتراضي `/qa-credentials/v1`)
- `OPENCLAW_QA_CREDENTIAL_OWNER_ID` (معرّف تتبع اختياري)
- يسمح `OPENCLAW_QA_ALLOW_INSECURE_HTTP=1` بعناوين Convex من نوع `http://` على loopback للتطوير المحلي فقط.

يجب أن يستخدم `OPENCLAW_QA_CONVEX_SITE_URL` البروتوكول `https://` في التشغيل العادي.

تتطلب أوامر الإدارة الخاصة بالمشرف (إضافة/إزالة/سرد المجموعة)
`OPENCLAW_QA_CONVEX_SECRET_MAINTAINER` تحديدًا.

مساعدات CLI للمشرفين:

```bash
pnpm openclaw qa credentials add --kind telegram --payload-file qa/telegram-credential.json
pnpm openclaw qa credentials list --kind telegram
pnpm openclaw qa credentials remove --credential-id <credential-id>
```

استخدم `--json` للحصول على مخرجات قابلة للقراءة آليًا في السكربتات وأدوات CI.

العقد الافتراضي لنقطة النهاية (`OPENCLAW_QA_CONVEX_SITE_URL` + `/qa-credentials/v1`):

- `POST /acquire`
  - الطلب: `{ kind, ownerId, actorRole, leaseTtlMs, heartbeatIntervalMs }`
  - النجاح: `{ status: "ok", credentialId, leaseToken, payload, leaseTtlMs?, heartbeatIntervalMs? }`
  - نفاد/قابل لإعادة المحاولة: `{ status: "error", code: "POOL_EXHAUSTED" | "NO_CREDENTIAL_AVAILABLE", ... }`
- `POST /heartbeat`
  - الطلب: `{ kind, ownerId, actorRole, credentialId, leaseToken, leaseTtlMs }`
  - النجاح: `{ status: "ok" }` (أو `2xx` فارغ)
- `POST /release`
  - الطلب: `{ kind, ownerId, actorRole, credentialId, leaseToken }`
  - النجاح: `{ status: "ok" }` (أو `2xx` فارغ)
- `POST /admin/add` (سر المشرف فقط)
  - الطلب: `{ kind, actorId, payload, note?, status? }`
  - النجاح: `{ status: "ok", credential }`
- `POST /admin/remove` (سر المشرف فقط)
  - الطلب: `{ credentialId, actorId }`
  - النجاح: `{ status: "ok", changed, credential }`
  - حماية الحجز النشط: `{ status: "error", code: "LEASE_ACTIVE", ... }`
- `POST /admin/list` (سر المشرف فقط)
  - الطلب: `{ kind?, status?, includePayload?, limit? }`
  - النجاح: `{ status: "ok", credentials, count }`

شكل الحمولة لنوع Telegram:

- `{ groupId: string, driverToken: string, sutToken: string }`
- يجب أن يكون `groupId` سلسلة معرّف دردشة Telegram رقمية.
- يتحقق `admin/add` من هذا الشكل لـ `kind: "telegram"` ويرفض الحمولة غير الصحيحة.

### إضافة قناة إلى QA

تتطلب إضافة قناة إلى نظام QA المعتمد على Markdown أمرين فقط بالضبط:

1. مُحوّل نقل للقناة.
2. حزمة سيناريوهات تختبر عقد القناة.

لا تضف جذر أوامر QA جديدًا على المستوى الأعلى عندما يستطيع مضيف `qa-lab` المشترك
امتلاك هذا التدفق.

يمتلك `qa-lab` آليات المضيف المشتركة:

- جذر الأمر `openclaw qa`
- بدء المجموعة وإنهاؤها
- توازي العمّال
- كتابة artifacts
- إنشاء التقارير
- تنفيذ السيناريوهات
- أسماء التوافق البديلة لسيناريوهات `qa-channel` الأقدم

تمتلك Plugins المشغّل عقد النقل:

- كيفية تركيب `openclaw qa <runner>` تحت الجذر المشترك `qa`
- كيفية إعداد Gateway لذلك النقل
- كيفية التحقق من الجاهزية
- كيفية حقن الأحداث الواردة
- كيفية مراقبة الرسائل الصادرة
- كيفية تعريض النصوص المنسوخة transcript وحالة النقل المعيارية
- كيفية تنفيذ الإجراءات المدعومة بالنقل
- كيفية التعامل مع إعادة الضبط أو التنظيف الخاص بالنقل

الحد الأدنى المطلوب لاعتماد قناة جديدة هو:

1. الإبقاء على `qa-lab` كمالك لجذر `qa` المشترك.
2. تنفيذ مشغّل النقل على واجهة مضيف `qa-lab` المشتركة.
3. الإبقاء على الآليات الخاصة بالنقل داخل Plugin المشغّل أو حزمة القناة.
4. تركيب المشغّل باسم `openclaw qa <runner>` بدلًا من تسجيل أمر جذري منافس.
   يجب أن تعلن Plugins المشغّل عن `qaRunners` في `openclaw.plugin.json` وتصدّر مصفوفة `qaRunnerCliRegistrations` مطابقة من `runtime-api.ts`.
   اجعل `runtime-api.ts` خفيفًا؛ يجب أن يبقى CLI الكسول وتنفيذ المشغّل وراء نقاط دخول منفصلة.
5. تأليف أو تكييف سيناريوهات Markdown تحت `qa/scenarios/`.
6. استخدام مساعدات السيناريو العامة للسيناريوهات الجديدة.
7. الإبقاء على أسماء التوافق البديلة الحالية عاملة ما لم يكن المستودع ينفّذ ترحيلًا مقصودًا.

قاعدة اتخاذ القرار صارمة:

- إذا كان يمكن التعبير عن السلوك مرة واحدة داخل `qa-lab`، فضعه في `qa-lab`.
- إذا كان السلوك يعتمد على نقل قناة واحدة، فأبقِه في Plugin ذلك المشغّل أو حزمة Plugin.
- إذا كان السيناريو يحتاج إلى قدرة جديدة يمكن لأكثر من قناة استخدامها، فأضف مساعدًا عامًا بدلًا من فرع خاص بقناة داخل `suite.ts`.
- إذا كان السلوك ذا معنى لنقل واحد فقط، فأبقِ السيناريو خاصًا بهذا النقل واجعل ذلك صريحًا في عقد السيناريو.

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

لا تزال أسماء التوافق البديلة متاحة للسيناريوهات الحالية، بما في ذلك:

- `waitForQaChannelReady`
- `waitForOutboundMessage`
- `waitForNoOutbound`
- `formatConversationTranscript`
- `resetBus`

يجب أن تستخدم أعمال القنوات الجديدة أسماء المساعدات العامة.
توجد أسماء التوافق البديلة لتجنب ترحيل شامل في يوم واحد، لا كنموذج
لتأليف سيناريوهات جديدة.

## مجموعات الاختبار (ما الذي يعمل وأين)

فكّر في المجموعات على أنها «واقعية متزايدة» (ومعها زيادة في عدم الاستقرار/الكلفة):

### Unit / integration (الافتراضي)

- الأمر: `pnpm test`
- الإعداد: عشر تشغيلات shards متسلسلة (`vitest.full-*.config.ts`) عبر مشاريع Vitest المحددة الموجودة
- الملفات: قوائم core/unit تحت `src/**/*.test.ts` و `packages/**/*.test.ts` و `test/**/*.test.ts`، واختبارات `ui` الخاصة بـ node المدرجة في قائمة السماح والمغطاة بواسطة `vitest.unit.config.ts`
- النطاق:
  - اختبارات unit خالصة
  - اختبارات تكامل داخل العملية (مصادقة gateway، والتوجيه، والأدوات، والتحليل، والإعداد)
  - اختبارات انحدار حتمية للأخطاء المعروفة
- التوقعات:
  - تعمل في CI
  - لا تتطلب مفاتيح حقيقية
  - يجب أن تكون سريعة ومستقرة
- ملاحظة المشاريع:
  - يشغّل `pnpm test` غير الموجّه الآن أحد عشر إعداد shard أصغر (`core-unit-src` و `core-unit-security` و `core-unit-ui` و `core-unit-support` و `core-support-boundary` و `core-contracts` و `core-bundled` و `core-runtime` و `agentic` و `auto-reply` و `extensions`) بدلًا من عملية root-project أصلية واحدة ضخمة. هذا يقلّل ذروة RSS على الأجهزة المحمّلة ويتجنب أن تؤدي أعمال auto-reply/extension إلى تجويع المجموعات غير المرتبطة.
  - لا يزال `pnpm test --watch` يستخدم مخطط مشاريع الجذر الأصلي في `vitest.config.ts`، لأن حلقة watch متعددة الـ shard غير عملية.
  - يوجّه `pnpm test` و `pnpm test:watch` و `pnpm test:perf:imports` أهداف الملفات/الأدلة الصريحة عبر المسارات المحددة أولًا، لذا فإن `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` يتجنب تكلفة بدء تشغيل مشروع الجذر الكامل.
  - يوسّع `pnpm test:changed` مسارات git المتغيرة إلى المسارات المحددة نفسها عندما يلمس الفرق ملفات مصدر/اختبار قابلة للتوجيه فقط؛ أما تعديلات config/setup فلا تزال تعود إلى إعادة التشغيل الواسعة لمشروع الجذر.
  - تُوجَّه اختبارات unit الخفيفة من حيث الاستيراد من agents و commands و plugins و مساعدات auto-reply و `plugin-sdk` ومناطق الأدوات الخالصة المشابهة عبر مسار `unit-fast`، الذي يتخطى `test/setup-openclaw-runtime.ts`؛ وتبقى الملفات ذات الحالة/الثقيلة وقت التشغيل على المسارات الحالية.
  - تُعيّن أيضًا بعض ملفات المصدر المساعدة المختارة من `plugin-sdk` و `commands` تشغيلات وضع changed إلى اختبارات الأشقاء الصريحة في تلك المسارات الخفيفة، حتى تتجنب تعديلات المساعدين إعادة تشغيل المجموعة الثقيلة الكاملة لذلك الدليل.
  - يحتوي `auto-reply` الآن على ثلاث سلال مخصصة: مساعدات core على المستوى الأعلى، واختبارات تكامل `reply.*` على المستوى الأعلى، والشجرة الفرعية `src/auto-reply/reply/**`. وهذا يُبقي أثقل أعمال حزمة reply بعيدًا عن اختبارات الحالة/التقسيم/token الرخيصة.
- ملاحظة المشغّل المضمّن:
  - عندما تغيّر مدخلات اكتشاف message-tool أو سياق وقت تشغيل Compaction،
    حافظ على مستويي التغطية معًا.
  - أضف اختبارات انحدار مركزة للمساعدات لحدود التوجيه/التطبيع الخالصة.
  - وحافظ أيضًا على سلامة مجموعات تكامل المشغّل المضمّن:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`, و
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - تتحقق هذه المجموعات من أن المعرّفات المحددة وسلوك Compaction لا يزالان يمران
    عبر المسارات الحقيقية `run.ts` / `compact.ts`؛ واختبارات المساعدات وحدها ليست
    بديلًا كافيًا لتلك مسارات التكامل.
- ملاحظة pool:
  - يعتمد إعداد Vitest الأساسي الآن على `threads` افتراضيًا.
  - ويثبت إعداد Vitest المشترك أيضًا `isolate: false` ويستخدم المشغّل غير المعزول عبر مشاريع الجذر وتهيئات e2e و live.
  - يحتفظ مسار UI في الجذر بإعداد `jsdom` والمُحسّن الخاص به، لكنه يعمل الآن أيضًا على المشغّل المشترك غير المعزول.
  - يرث كل shard من `pnpm test` القيم الافتراضية نفسها `threads` + `isolate: false` من إعداد Vitest المشترك.
  - يضيف مشغّل `scripts/run-vitest.mjs` المشترك الآن أيضًا `--no-maglev` افتراضيًا لعمليات Node الفرعية الخاصة بـ Vitest لتقليل churn ترجمة V8 أثناء التشغيلات المحلية الكبيرة. اضبط `OPENCLAW_VITEST_ENABLE_MAGLEV=1` إذا كنت تحتاج إلى المقارنة مع سلوك V8 الافتراضي.
- ملاحظة التكرار المحلي السريع:
  - يوجّه `pnpm test:changed` عبر المسارات المحددة عندما تعيّن المسارات المتغيرة بشكل نظيف إلى مجموعة أصغر.
  - يحتفظ `pnpm test:max` و `pnpm test:changed:max` بسلوك التوجيه نفسه، ولكن مع حد أعلى للعمّال.
  - أصبح التحجيم التلقائي للعمّال محليًا محافظًا عمدًا الآن، ويتراجع أيضًا عندما يكون متوسط تحميل المضيف مرتفعًا أصلًا، بحيث تُحدث تشغيلات Vitest المتزامنة المتعددة ضررًا أقل افتراضيًا.
  - يعلّم إعداد Vitest الأساسي ملفات المشاريع/الإعداد كـ `forceRerunTriggers` حتى تبقى إعادة تشغيل وضع changed صحيحة عندما تتغير أسلاك الاختبار.
  - يبقي الإعداد `OPENCLAW_VITEST_FS_MODULE_CACHE` مفعّلًا على المضيفين المدعومين؛ اضبط `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` إذا أردت موقع cache صريحًا واحدًا للتوصيف المباشر.
- ملاحظة تصحيح الأداء:
  - يفعّل `pnpm test:perf:imports` تقارير مدة الاستيراد في Vitest بالإضافة إلى مخرجات تفصيل الاستيراد.
  - يقيّد `pnpm test:perf:imports:changed` عرض التوصيف نفسه إلى الملفات المتغيرة منذ `origin/main`.
- يقارن `pnpm test:perf:changed:bench -- --ref <git-ref>` بين `test:changed` الموجّه ومسار root-project الأصلي لذلك الفرق الملتزم ويطبع زمن التنفيذ بالإضافة إلى macOS max RSS.
- يختبر `pnpm test:perf:changed:bench -- --worktree` الشجرة المتسخة الحالية عبر توجيه قائمة الملفات المتغيرة من خلال `scripts/test-projects.mjs` وإعداد Vitest للجذر.
  - يكتب `pnpm test:perf:profile:main` ملف تعريف CPU للخيط الرئيسي لتكاليف بدء تشغيل Vitest/Vite والتحويل.
  - يكتب `pnpm test:perf:profile:runner` ملفات تعريف CPU+heap للمشغّل لمجموعة unit مع تعطيل التوازي على مستوى الملفات.

### E2E (اختبار smoke لـ gateway)

- الأمر: `pnpm test:e2e`
- الإعداد: `vitest.e2e.config.ts`
- الملفات: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- القيم الافتراضية لوقت التشغيل:
  - يستخدم Vitest `threads` مع `isolate: false`، بما يطابق بقية المستودع.
  - يستخدم عمّالًا تكيفيين (في CI: حتى 2، محليًا: 1 افتراضيًا).
  - يعمل في الوضع الصامت افتراضيًا لتقليل تكلفة I/O الخاصة بالطرفية.
- تجاوزات مفيدة:
  - `OPENCLAW_E2E_WORKERS=<n>` لفرض عدد العمّال (بحد أقصى 16).
  - `OPENCLAW_E2E_VERBOSE=1` لإعادة تفعيل مخرجات الطرفية التفصيلية.
- النطاق:
  - سلوك gateway من طرف إلى طرف عبر عدة مثيلات
  - أسطح WebSocket/HTTP، واقتران Node، وشبكات أثقل
- التوقعات:
  - يعمل في CI (عند تمكينه في المسار)
  - لا يتطلب مفاتيح حقيقية
  - يحتوي على أجزاء متحركة أكثر من اختبارات unit (وقد يكون أبطأ)

### E2E: اختبار smoke للواجهة الخلفية OpenShell

- الأمر: `pnpm test:e2e:openshell`
- الملف: `test/openshell-sandbox.e2e.test.ts`
- النطاق:
  - يبدأ OpenShell gateway معزولًا على المضيف عبر Docker
  - ينشئ sandbox من Dockerfile محلي مؤقت
  - يختبر الواجهة الخلفية OpenShell الخاصة بـ OpenClaw عبر `sandbox ssh-config` + تنفيذ SSH حقيقيين
  - يتحقق من سلوك نظام الملفات canonical البعيد عبر جسر fs الخاص بـ sandbox
- التوقعات:
  - اشتراك اختياري فقط؛ ليس جزءًا من تشغيل `pnpm test:e2e` الافتراضي
  - يتطلب CLI محليًا لـ `openshell` بالإضافة إلى Docker daemon يعمل
  - يستخدم `HOME` / `XDG_CONFIG_HOME` معزولين، ثم يدمّر test gateway و sandbox
- تجاوزات مفيدة:
  - `OPENCLAW_E2E_OPENSHELL=1` لتمكين الاختبار عند تشغيل مجموعة e2e الأوسع يدويًا
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell` للإشارة إلى ملف CLI ثنائي غير افتراضي أو سكربت wrapper

### Live (مزوّدون حقيقيون + نماذج حقيقية)

- الأمر: `pnpm test:live`
- الإعداد: `vitest.live.config.ts`
- الملفات: `src/**/*.live.test.ts`
- الافتراضي: **مفعّل** بواسطة `pnpm test:live` (يضبط `OPENCLAW_LIVE_TEST=1`)
- النطاق:
  - «هل يعمل هذا المزوّد/النموذج فعلًا _اليوم_ باستخدام بيانات اعتماد حقيقية؟»
  - التقاط تغييرات تنسيق المزوّد، وخصائص استدعاء الأدوات، ومشكلات المصادقة، وسلوك حدود المعدل
- التوقعات:
  - غير مستقر في CI بطبيعته (شبكات حقيقية، وسياسات مزوّد حقيقية، وحصص، وانقطاعات)
  - يكلّف مالًا / يستهلك حدود المعدل
  - يُفضَّل تشغيل مجموعات فرعية مضيقة بدلًا من تشغيل «كل شيء»
- تستورد التشغيلات الحية `~/.profile` لالتقاط مفاتيح API الناقصة.
- افتراضيًا، لا تزال التشغيلات الحية تعزل `HOME` وتنسخ مواد config/auth إلى home اختبار مؤقت حتى لا تتمكن تجهيزات unit من تعديل `~/.openclaw` الحقيقي لديك.
- اضبط `OPENCLAW_LIVE_USE_REAL_HOME=1` فقط عندما تحتاج عمدًا إلى أن تستخدم الاختبارات الحية دليل home الحقيقي لديك.
- أصبح `pnpm test:live` الآن افتراضيًا في وضع أكثر هدوءًا: فهو يُبقي على مخرجات التقدم `[live] ...`، لكنه يخفي إشعار `~/.profile` الإضافي ويكتم سجلات بدء gateway وضجيج Bonjour. اضبط `OPENCLAW_LIVE_TEST_QUIET=0` إذا أردت استعادة سجلات بدء التشغيل الكاملة.
- تدوير مفاتيح API (خاص بالمزوّد): اضبط `*_API_KEYS` بتنسيق فاصلة/فاصلة منقوطة أو `*_API_KEY_1`, `*_API_KEY_2` (على سبيل المثال `OPENAI_API_KEYS` و `ANTHROPIC_API_KEYS` و `GEMINI_API_KEYS`) أو استخدم تجاوزًا لكل live عبر `OPENCLAW_LIVE_*_KEY`؛ تعيد الاختبارات المحاولة عند استجابات rate limit.
- مخرجات التقدم/Heartbeat:
  - تصدر مجموعات live الآن أسطر التقدم إلى stderr بحيث تظهر استدعاءات المزوّد الطويلة على أنها نشطة بوضوح حتى عندما يكون التقاط طرفية Vitest هادئًا.
  - يعطّل `vitest.live.config.ts` اعتراض طرفية Vitest بحيث تتدفق أسطر تقدم المزوّد/gateway مباشرة أثناء التشغيلات الحية.
  - اضبط Heartbeat النموذج المباشر باستخدام `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - اضبط Heartbeat الخاص بـ gateway/probe باستخدام `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## أي مجموعة يجب أن أشغّل؟

استخدم جدول القرار هذا:

- تعديل المنطق/الاختبارات: شغّل `pnpm test` (و `pnpm test:coverage` إذا غيّرت الكثير)
- لمس شبكات gateway / بروتوكول WS / الاقتران: أضف `pnpm test:e2e`
- تصحيح «البوت الخاص بي متوقف» / الإخفاقات الخاصة بالمزوّد / استدعاء الأدوات: شغّل `pnpm test:live` بشكل مضيّق

## Live: مسح قدرات Android Node

- الاختبار: `src/gateway/android-node.capabilities.live.test.ts`
- السكربت: `pnpm android:test:integration`
- الهدف: استدعاء **كل أمر مُعلن عنه حاليًا** من Android Node متصل والتحقق من سلوك عقد الأمر.
- النطاق:
  - إعداد يدوي/مشروط مسبقًا (المجموعة لا تثبّت التطبيق ولا تشغّله ولا تقترنه).
  - التحقق أمرًا بأمر من `node.invoke` في gateway لعقدة Android المحددة.
- الإعداد المسبق المطلوب:
  - تطبيق Android متصل ومقترن بالفعل مع gateway.
  - إبقاء التطبيق في المقدمة.
  - منح الأذونات/موافقة الالتقاط للقدرات التي تتوقع أن تنجح.
- تجاوزات الهدف الاختيارية:
  - `OPENCLAW_ANDROID_NODE_ID` أو `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- تفاصيل إعداد Android الكاملة: [تطبيق Android](/ar/platforms/android)

## Live: اختبار smoke للنموذج (مفاتيح الملف الشخصي)

تنقسم الاختبارات الحية إلى طبقتين حتى نتمكن من عزل الإخفاقات:

- يخبرنا «النموذج المباشر» ما إذا كان المزوّد/النموذج يستطيع الرد أصلًا باستخدام المفتاح المعطى.
- يخبرنا «اختبار smoke لـ Gateway» ما إذا كان خط gateway+agent الكامل يعمل لذلك النموذج (الجلسات، والسجل، والأدوات، وسياسة sandbox، وما إلى ذلك).

### الطبقة 1: إكمال مباشر للنموذج (من دون gateway)

- الاختبار: `src/agents/models.profiles.live.test.ts`
- الهدف:
  - تعداد النماذج المكتشفة
  - استخدام `getApiKeyForModel` لتحديد النماذج التي لديك بيانات اعتماد لها
  - تشغيل إكمال صغير لكل نموذج (واختبارات الانحدار الموجهة عند الحاجة)
- كيفية التمكين:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` إذا كنت تستدعي Vitest مباشرة)
- اضبط `OPENCLAW_LIVE_MODELS=modern` (أو `all`، وهو اسم بديل لـ modern) لتشغيل هذه المجموعة فعلًا؛ وإلا فسيتم تخطيها للحفاظ على تركيز `pnpm test:live` على اختبار smoke لـ gateway
- كيفية اختيار النماذج:
  - `OPENCLAW_LIVE_MODELS=modern` لتشغيل قائمة السماح الحديثة (Opus/Sonnet 4.6+، GPT-5.x + Codex، Gemini 3، GLM 4.7، MiniMax M2.7، Grok 4)
  - `OPENCLAW_LIVE_MODELS=all` اسم بديل لقائمة السماح الحديثة
  - أو `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (قائمة سماح مفصولة بفواصل)
  - تستخدم عمليات المسح modern/all حدًا منسقًا عالي الإشارة افتراضيًا؛ اضبط `OPENCLAW_LIVE_MAX_MODELS=0` لمسح حديث شامل أو رقمًا موجبًا لحد أصغر.
- كيفية اختيار المزوّدين:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (قائمة سماح مفصولة بفواصل)
- من أين تأتي المفاتيح:
  - افتراضيًا: من مخزن الملفات الشخصية وبدائل env
  - اضبط `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض **مخزن الملفات الشخصية** فقط
- سبب وجود هذا:
  - يفصل بين «واجهة API الخاصة بالمزوّد معطلة / المفتاح غير صالح» و«خط agent في gateway معطل»
  - يحتوي على اختبارات انحدار صغيرة ومعزولة (مثال: تدفق إعادة تشغيل reasoning في OpenAI Responses/Codex Responses + تدفقات استدعاء الأدوات)

### الطبقة 2: اختبار smoke لـ Gateway + dev agent (ما الذي يفعله "@openclaw" فعليًا)

- الاختبار: `src/gateway/gateway-models.profiles.live.test.ts`
- الهدف:
  - تشغيل gateway داخل العملية
  - إنشاء/تعديل جلسة `agent:dev:*` (مع تجاوز النموذج لكل تشغيل)
  - التكرار عبر النماذج التي تملك مفاتيح والتحقق من:
    - استجابة «ذات معنى» (من دون أدوات)
    - أن استدعاء أداة حقيقي يعمل (`read` probe)
    - probes إضافية اختيارية للأدوات (`exec+read` probe)
    - استمرار عمل مسارات انحدار OpenAI ‏(استدعاء-أداة-فقط → متابعة)
- تفاصيل الـ probe ‏(حتى تتمكن من شرح الإخفاقات بسرعة):
  - probe ‏`read`: يكتب الاختبار ملف nonce في مساحة العمل ويطلب من الوكيل `read` له ثم إعادة nonce.
  - probe ‏`exec+read`: يطلب الاختبار من الوكيل أن يكتب nonce عبر `exec` في ملف temp، ثم `read` له مرة أخرى.
  - probe الصورة: يرفق الاختبار ملف PNG مُولّدًا (قط + رمز عشوائي) ويتوقع من النموذج أن يعيد `cat <CODE>`.
  - مرجع التنفيذ: `src/gateway/gateway-models.profiles.live.test.ts` و `src/gateway/live-image-probe.ts`.
- كيفية التمكين:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` إذا كنت تستدعي Vitest مباشرة)
- كيفية اختيار النماذج:
  - الافتراضي: قائمة السماح الحديثة (Opus/Sonnet 4.6+، ‏GPT-5.x + Codex، ‏Gemini 3، ‏GLM 4.7، ‏MiniMax M2.7، ‏Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` هو اسم بديل لقائمة السماح الحديثة
  - أو اضبط `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (أو قائمة مفصولة بفواصل) للتضييق
  - تستخدم عمليات مسح gateway الحديثة/‏all حدًا منسقًا عالي الإشارة افتراضيًا؛ اضبط `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0` لمسح حديث شامل أو رقمًا موجبًا لحد أصغر.
- كيفية اختيار المزوّدين (تجنّب «كل شيء في OpenRouter»):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (قائمة سماح مفصولة بفواصل)
- تكون probes الأدوات + الصور مفعّلة دائمًا في هذا الاختبار الحي:
  - probe ‏`read` + probe ‏`exec+read` (ضغط على الأدوات)
  - يعمل probe الصورة عندما يعلن النموذج دعمه لإدخال الصور
  - التدفق (عالي المستوى):
    - يولّد الاختبار ملف PNG صغيرًا يحتوي على “CAT” + رمز عشوائي (`src/gateway/live-image-probe.ts`)
    - يرسله عبر `agent` باستخدام `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - يحلّل Gateway المرفقات إلى `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - يمرّر الوكيل المضمّن رسالة مستخدم متعددة الوسائط إلى النموذج
    - التحقق: يحتوي الرد على `cat` + الرمز (مع سماح OCR بأخطاء طفيفة)

نصيحة: لمعرفة ما يمكنك اختباره على جهازك (ومعرّفات `provider/model` الدقيقة)، شغّل:

```bash
openclaw models list
openclaw models list --json
```

## Live: اختبار smoke للواجهة الخلفية CLI ‏(Claude أو Codex أو Gemini أو CLIs محلية أخرى)

- الاختبار: `src/gateway/gateway-cli-backend.live.test.ts`
- الهدف: التحقق من مسار Gateway + الوكيل باستخدام واجهة خلفية CLI محلية، من دون لمس إعدادك الافتراضي.
- توجد إعدادات smoke الافتراضية الخاصة بكل واجهة خلفية مع تعريف `cli-backend.ts` المملوك للإضافة المعنية.
- التمكين:
  - `pnpm test:live` (أو `OPENCLAW_LIVE_TEST=1` إذا كنت تستدعي Vitest مباشرة)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- القيم الافتراضية:
  - المزوّد/النموذج الافتراضي: `claude-cli/claude-sonnet-4-6`
  - يأتي سلوك الأمر/الوسائط/الصورة من بيانات تعريف Plugin الواجهة الخلفية CLI المالكة.
- التجاوزات (اختيارية):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` لإرسال مرفق صورة حقيقي (تُحقن المسارات داخل prompt).
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` لتمرير مسارات ملفات الصور كوسائط CLI بدلًا من حقنها في prompt.
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (أو `"list"`) للتحكم في كيفية تمرير وسائط الصور عند ضبط `IMAGE_ARG`.
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` لإرسال دور ثانٍ والتحقق من تدفق الاستئناف.
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0` لتعطيل probe الاستمرارية الافتراضي للجلسة نفسها من Claude Sonnet إلى Opus (اضبطه على `1` لفرض تشغيله عندما يدعم النموذج المحدد هدف تبديل).

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
- يشغّل اختبار smoke الحي للواجهة الخلفية CLI داخل صورة Docker الخاصة بالمستودع بصفته المستخدم غير الجذر `node`.
- يحلّ بيانات تعريف smoke الخاصة بـ CLI من الإضافة المالكة، ثم يثبّت حزمة Linux CLI المطابقة (`@anthropic-ai/claude-code` أو `@openai/codex` أو `@google/gemini-cli`) في بادئة قابلة للكتابة ومخبأة في `OPENCLAW_DOCKER_CLI_TOOLS_DIR` (الافتراضي: `~/.cache/openclaw/docker-cli-tools`).
- يتطلب `pnpm test:docker:live-cli-backend:claude-subscription` مصادقة OAuth محمولة لاشتراك Claude Code عبر أحد الخيارين: `~/.claude/.credentials.json` مع `claudeAiOauth.subscriptionType` أو `CLAUDE_CODE_OAUTH_TOKEN` من `claude setup-token`. ويثبت أولًا أن `claude -p` يعمل مباشرة داخل Docker، ثم يشغّل دورين لـ Gateway CLI-backend من دون الاحتفاظ بمتغيرات env الخاصة بمفتاح Anthropic API. يعطّل مسار الاشتراك هذا probes أداة Claude MCP والصورة افتراضيًا لأن Claude يوجّه حاليًا استخدام تطبيقات الجهات الخارجية عبر فوترة استخدام إضافية بدلًا من حدود خطة الاشتراك العادية.
- يختبر smoke الحي للواجهة الخلفية CLI الآن التدفق الكامل نفسه من طرف إلى طرف لكل من Claude و Codex و Gemini: دور نصي، ثم دور تصنيف صورة، ثم استدعاء أداة MCP ‏`cron` يتم التحقق منه عبر CLI الخاص بـ gateway.
- يقوم اختبار smoke الافتراضي لـ Claude أيضًا بتعديل الجلسة من Sonnet إلى Opus ويتحقق من أن الجلسة المستأنفة ما زالت تتذكر ملاحظة سابقة.

## Live: اختبار smoke لربط ACP ‏(`/acp spawn ... --bind here`)

- الاختبار: `src/gateway/gateway-acp-bind.live.test.ts`
- الهدف: التحقق من تدفق ربط المحادثة ACP الحقيقي مع وكيل ACP حي:
  - إرسال `/acp spawn <agent> --bind here`
  - ربط محادثة قناة رسائل اصطناعية في مكانها
  - إرسال متابعة عادية على المحادثة نفسها
  - التحقق من وصول المتابعة إلى transcript جلسة ACP المرتبطة
- التمكين:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- القيم الافتراضية:
  - وكلاء ACP في Docker: ‏`claude,codex,gemini`
  - وكيل ACP لـ `pnpm test:live ...` المباشر: `claude`
  - القناة الاصطناعية: سياق محادثة بأسلوب Slack DM
  - الواجهة الخلفية ACP: ‏`acpx`
- التجاوزات:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- ملاحظات:
  - يستخدم هذا المسار سطح gateway ‏`chat.send` مع حقول originating-route اصطناعية للمشرف فقط حتى تتمكن الاختبارات من إرفاق سياق قناة الرسائل من دون التظاهر بالتسليم الخارجي.
  - عندما لا يكون `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` مضبوطًا، يستخدم الاختبار سجل الوكلاء المضمّن في Plugin ‏`acpx` للوكلاء المحددين في حزمة ACP.

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
- افتراضيًا، يشغّل اختبار smoke لربط ACP مقابل جميع وكلاء CLI الحية المدعومة بالتتابع: `claude` ثم `codex` ثم `gemini`.
- استخدم `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude` أو `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` أو `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` لتضييق المصفوفة.
- يستورد `~/.profile`، ويجهّز مواد مصادقة CLI المطابقة داخل الحاوية، ويثبّت `acpx` في بادئة npm قابلة للكتابة، ثم يثبّت CLI الحي المطلوب (`@anthropic-ai/claude-code` أو `@openai/codex` أو `@google/gemini-cli`) إذا كان مفقودًا.
- داخل Docker، يضبط المشغّل `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` حتى يبقي acpx متغيرات env الخاصة بالمزوّد من profile المستورد متاحة لـ CLI الحزمة الفرعية.

## Live: اختبار smoke لحزمة Codex app-server

- الهدف: التحقق من حزمة Codex المملوكة لـ Plugin عبر طريقة gateway
  العادية `agent`:
  - تحميل Plugin المضمّن `codex`
  - تحديد `OPENCLAW_AGENT_RUNTIME=codex`
  - إرسال أول دور لوكيل gateway إلى `codex/gpt-5.4`
  - إرسال دور ثانٍ إلى جلسة OpenClaw نفسها والتحقق من أن خيط app-server
    يمكنه الاستئناف
  - تشغيل `/codex status` و `/codex models` عبر مسار أوامر gateway
    نفسه
- الاختبار: `src/gateway/gateway-codex-harness.live.test.ts`
- التمكين: `OPENCLAW_LIVE_CODEX_HARNESS=1`
- النموذج الافتراضي: `codex/gpt-5.4`
- probe صورة اختياري: `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1`
- probe MCP/أداة اختياري: `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1`
- يضبط اختبار smoke القيمة `OPENCLAW_AGENT_HARNESS_FALLBACK=none` حتى لا
  ينجح عطل في حزمة Codex عبر الرجوع الصامت إلى PI.
- المصادقة: `OPENAI_API_KEY` من الصدفة/‏profile، بالإضافة إلى نسخ اختيارية
  من `~/.codex/auth.json` و `~/.codex/config.toml`

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
- يستورد `~/.profile` المركّب، ويمرّر `OPENAI_API_KEY`، وينسخ ملفات مصادقة Codex CLI
  عند وجودها، ويثبّت `@openai/codex` في بادئة npm قابلة للكتابة ومركّبة،
  ويجهّز شجرة المصدر، ثم يشغّل فقط الاختبار الحي لحزمة Codex.
- يفعّل Docker probes الصورة و MCP/الأداة افتراضيًا. اضبط
  `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=0` أو
  `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=0` عندما تحتاج إلى تشغيل تصحيح أضيق.
- يصدّر Docker أيضًا `OPENCLAW_AGENT_HARNESS_FALLBACK=none`، بما يطابق إعداد
  الاختبار الحي حتى لا يتمكن `openai-codex/*` أو الرجوع إلى PI من إخفاء
  انحدار حزمة Codex.

### وصفات Live الموصى بها

تكون قوائم السماح الضيقة والصريحة هي الأسرع والأقل عرضة للتذبذب:

- نموذج واحد، مباشر (من دون gateway):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- نموذج واحد، اختبار smoke لـ gateway:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- استدعاء أدوات عبر عدة مزوّدين:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- تركيز Google ‏(مفتاح Gemini API + Antigravity):
  - Gemini ‏(مفتاح API): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity ‏(OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

ملاحظات:

- يستخدم `google/...` واجهة Gemini API ‏(مفتاح API).
- يستخدم `google-antigravity/...` جسر Antigravity OAuth ‏(نقطة نهاية وكيل على نمط Cloud Code Assist).
- يستخدم `google-gemini-cli/...` ‏Gemini CLI المحلي على جهازك (مصادقة منفصلة وخصائص أدوات مختلفة).
- Gemini API مقابل Gemini CLI:
  - API: يستدعي OpenClaw واجهة Gemini API المستضافة من Google عبر HTTP ‏(مفتاح API / مصادقة الملف الشخصي)؛ وهذا هو ما يقصده معظم المستخدمين بعبارة “Gemini”.
  - CLI: يستدعي OpenClaw ملف `gemini` الثنائي المحلي؛ وله مصادقة خاصة به وقد يتصرف بشكل مختلف (الدفق/دعم الأدوات/اختلاف الإصدارات).

## Live: مصفوفة النماذج (ما الذي نغطيه)

لا توجد «قائمة نماذج CI» ثابتة (لأن live اختياري)، لكن هذه هي النماذج **الموصى بها** للتغطية بانتظام على جهاز تطوير يملك مفاتيح.

### مجموعة smoke الحديثة (استدعاء الأدوات + الصور)

هذا هو تشغيل «النماذج الشائعة» الذي نتوقع أن يظل عاملًا:

- OpenAI ‏(غير Codex): ‏`openai/gpt-5.4` (اختياري: `openai/gpt-5.4-mini`)
- OpenAI Codex: ‏`openai-codex/gpt-5.4`
- Anthropic: ‏`anthropic/claude-opus-4-6` (أو `anthropic/claude-sonnet-4-6`)
- Google ‏(Gemini API): ‏`google/gemini-3.1-pro-preview` و `google/gemini-3-flash-preview` (تجنب نماذج Gemini 2.x الأقدم)
- Google ‏(Antigravity): ‏`google-antigravity/claude-opus-4-6-thinking` و `google-antigravity/gemini-3-flash`
- Z.AI ‏(GLM): ‏`zai/glm-4.7`
- MiniMax: ‏`minimax/MiniMax-M2.7`

شغّل اختبار smoke لـ gateway مع الأدوات + الصورة:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### خط الأساس: استدعاء الأدوات (Read + ‏Exec اختياري)

اختر واحدًا على الأقل من كل عائلة مزوّد:

- OpenAI: ‏`openai/gpt-5.4` (أو `openai/gpt-5.4-mini`)
- Anthropic: ‏`anthropic/claude-opus-4-6` (أو `anthropic/claude-sonnet-4-6`)
- Google: ‏`google/gemini-3-flash-preview` (أو `google/gemini-3.1-pro-preview`)
- Z.AI ‏(GLM): ‏`zai/glm-4.7`
- MiniMax: ‏`minimax/MiniMax-M2.7`

تغطية إضافية اختيارية (من الجيد توفرها):

- xAI: ‏`xai/grok-4` (أو أحدث إصدار متاح)
- Mistral: ‏`mistral/`… (اختر نموذجًا واحدًا يدعم “tools” ويكون مفعّلًا لديك)
- Cerebras: ‏`cerebras/`… (إذا كان لديك وصول)
- LM Studio: ‏`lmstudio/`… (محلي؛ يعتمد استدعاء الأدوات على وضع API)

### الرؤية: إرسال صورة (مرفق → رسالة متعددة الوسائط)

أدرج نموذجًا واحدًا على الأقل يدعم الصور في `OPENCLAW_LIVE_GATEWAY_MODELS` ‏(Claude/Gemini/OpenAI بالإصدارات الداعمة للرؤية، إلخ) لاختبار probe الصورة.

### المجمّعات / البوابات البديلة

إذا كانت لديك مفاتيح مفعّلة، فنحن ندعم أيضًا الاختبار عبر:

- OpenRouter: ‏`openrouter/...` (مئات النماذج؛ استخدم `openclaw models scan` للعثور على مرشحين يدعمون الأدوات+الصور)
- OpenCode: ‏`opencode/...` لـ Zen و `opencode-go/...` لـ Go ‏(المصادقة عبر `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

مزيد من المزوّدين الذين يمكنك تضمينهم في مصفوفة live ‏(إذا كانت لديك بيانات اعتماد/إعداد):

- مضمّنة: `openai` و `openai-codex` و `anthropic` و `google` و `google-vertex` و `google-antigravity` و `google-gemini-cli` و `zai` و `openrouter` و `opencode` و `opencode-go` و `xai` و `groq` و `cerebras` و `mistral` و `github-copilot`
- عبر `models.providers` ‏(نقاط نهاية مخصصة): ‏`minimax` ‏(سحابي/API)، بالإضافة إلى أي وكيل متوافق مع OpenAI/Anthropic ‏(LM Studio و vLLM و LiteLLM وغيرها)

نصيحة: لا تحاول تثبيت «كل النماذج» بشكل ثابت في التوثيق. القائمة الموثوقة هي كل ما تعيده `discoverModels(...)` على جهازك + أي مفاتيح متاحة.

## بيانات الاعتماد (لا تُلتزم أبدًا)

تكتشف الاختبارات الحية بيانات الاعتماد بالطريقة نفسها التي تعمل بها CLI. والآثار العملية:

- إذا كانت CLI تعمل، فيجب أن تجد الاختبارات الحية المفاتيح نفسها.
- إذا قال اختبار حي «لا توجد بيانات اعتماد»، فصحّح المشكلة بالطريقة نفسها التي ستصحح بها `openclaw models list` / تحديد النموذج.

- ملفات مصادقة لكل وكيل: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (هذا هو المقصود بـ «مفاتيح الملف الشخصي» في الاختبارات الحية)
- الإعداد: `~/.openclaw/openclaw.json` (أو `OPENCLAW_CONFIG_PATH`)
- دليل الحالة القديم: `~/.openclaw/credentials/` (يُنسخ إلى home الحي المرحلي عند وجوده، لكنه ليس مخزن مفاتيح الملف الشخصي الرئيسي)
- تنسخ التشغيلات الحية المحلية الإعداد النشط، وملفات `auth-profiles.json` لكل وكيل، و `credentials/` القديمة، وأدلة مصادقة CLI الخارجية المدعومة إلى home اختبار مؤقت افتراضيًا؛ وتتخطى المنازل الحية المرحلية `workspace/` و `sandboxes/`، وتُزال تجاوزات المسار `agents.*.workspace` / `agentDir` حتى تبقى probes بعيدة عن مساحة العمل الحقيقية على المضيف.

إذا أردت الاعتماد على مفاتيح env ‏(مثل المصدّرة في `~/.profile`)، فشغّل الاختبارات المحلية بعد `source ~/.profile`، أو استخدم مشغّلات Docker أدناه (يمكنها تركيب `~/.profile` داخل الحاوية).

## Deepgram live ‏(نسخ صوتي)

- الاختبار: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- التمكين: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- الاختبار: `src/agents/byteplus.live.test.ts`
- التمكين: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- تجاوز اختياري للنموذج: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow media live

- الاختبار: `extensions/comfy/comfy.live.test.ts`
- التمكين: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- النطاق:
  - يختبر مسارات comfy المضمّنة للصور والفيديو و `music_generate`
  - يتخطى كل قدرة ما لم يتم إعداد `models.providers.comfy.<capability>`
  - مفيد بعد تغيير إرسال سير عمل comfy أو الاستطلاع أو التنزيلات أو تسجيل Plugin

## Image generation live

- الاختبار: `src/image-generation/runtime.live.test.ts`
- الأمر: `pnpm test:live src/image-generation/runtime.live.test.ts`
- الحزمة: `pnpm test:live:media image`
- النطاق:
  - يعدّد كل Plugins مزوّدي توليد الصور المسجّلين
  - يحمّل متغيرات env المفقودة للمزوّد من shell تسجيل الدخول لديك (`~/.profile`) قبل الفحص
  - يستخدم مفاتيح API الحية/من env قبل ملفات المصادقة المخزنة افتراضيًا، حتى لا تحجب مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات اعتماد shell الحقيقية
  - يتخطى المزوّدين الذين لا يملكون مصادقة/ملفًا شخصيًا/نموذجًا صالحًا
  - يشغّل متغيرات توليد الصور القياسية عبر قدرة وقت التشغيل المشتركة:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- المزوّدون المضمّنون المغطّون حاليًا:
  - `openai`
  - `google`
- تضييق اختياري:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- سلوك مصادقة اختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن الملف الشخصي وتجاهل التجاوزات المعتمدة على env فقط

## Music generation live

- الاختبار: `extensions/music-generation-providers.live.test.ts`
- التمكين: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- الحزمة: `pnpm test:live:media music`
- النطاق:
  - يختبر مسار مزوّد توليد الموسيقى المضمّن المشترك
  - يغطي حاليًا Google و MiniMax
  - يحمّل متغيرات env الخاصة بالمزوّد من shell تسجيل الدخول لديك (`~/.profile`) قبل الفحص
  - يستخدم مفاتيح API الحية/من env قبل ملفات المصادقة المخزنة افتراضيًا، حتى لا تحجب مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات اعتماد shell الحقيقية
  - يتخطى المزوّدين الذين لا يملكون مصادقة/ملفًا شخصيًا/نموذجًا صالحًا
  - يشغّل كلا وضعي وقت التشغيل المعلنين عند التوفر:
    - `generate` بإدخال يعتمد على prompt فقط
    - `edit` عندما يعلن المزوّد `capabilities.edit.enabled`
  - التغطية الحالية للمسار المشترك:
    - `google`: ‏`generate`, `edit`
    - `minimax`: ‏`generate`
    - `comfy`: ملف Comfy حي منفصل، وليس هذا المسح المشترك
- تضييق اختياري:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- سلوك مصادقة اختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن الملف الشخصي وتجاهل التجاوزات المعتمدة على env فقط

## Video generation live

- الاختبار: `extensions/video-generation-providers.live.test.ts`
- التمكين: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- الحزمة: `pnpm test:live:media video`
- النطاق:
  - يختبر مسار مزوّد توليد الفيديو المضمّن المشترك
  - يستخدم افتراضيًا مسار smoke آمنًا للإصدار: مزوّدون غير FAL، وطلب text-to-video واحد لكل مزوّد، وprompt لوبستر مدته ثانية واحدة، وحدّ عمليات لكل مزوّد من `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS` ‏(الافتراضي `180000`)
  - يتخطى FAL افتراضيًا لأن زمن انتظار الطابور من جهة المزوّد قد يهيمن على وقت الإصدار؛ مرّر `--video-providers fal` أو `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="fal"` لتشغيله صراحةً
  - يحمّل متغيرات env الخاصة بالمزوّد من shell تسجيل الدخول لديك (`~/.profile`) قبل الفحص
  - يستخدم مفاتيح API الحية/من env قبل ملفات المصادقة المخزنة افتراضيًا، حتى لا تحجب مفاتيح الاختبار القديمة في `auth-profiles.json` بيانات اعتماد shell الحقيقية
  - يتخطى المزوّدين الذين لا يملكون مصادقة/ملفًا شخصيًا/نموذجًا صالحًا
  - يشغّل `generate` فقط افتراضيًا
  - اضبط `OPENCLAW_LIVE_VIDEO_GENERATION_FULL_MODES=1` لتشغيل أوضاع التحويل المعلنة أيضًا عند توفرها:
    - `imageToVideo` عندما يعلن المزوّد `capabilities.imageToVideo.enabled` ويقبل المزوّد/النموذج المحدد إدخال صور محليًا مدعومًا بالـ buffer في المسح المشترك
    - `videoToVideo` عندما يعلن المزوّد `capabilities.videoToVideo.enabled` ويقبل المزوّد/النموذج المحدد إدخال فيديو محليًا مدعومًا بالـ buffer في المسح المشترك
  - مزوّدو `imageToVideo` المعلنون لكن المتخطَّون حاليًا في المسح المشترك:
    - `vydra` لأن `veo3` المضمّن نصّي فقط و `kling` المضمّن يتطلب عنوان URL بعيدًا للصورة
  - تغطية Vydra الخاصة بالمزوّد:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - يشغّل هذا الملف `veo3` لتحويل النص إلى فيديو بالإضافة إلى مسار `kling` يستخدم تجهيز عنوان URL بعيد للصورة افتراضيًا
  - التغطية الحية الحالية لـ `videoToVideo`:
    - `runway` فقط عندما يكون النموذج المحدد هو `runway/gen4_aleph`
  - مزوّدو `videoToVideo` المعلنون لكن المتخطَّون حاليًا في المسح المشترك:
    - `alibaba` و `qwen` و `xai` لأن تلك المسارات تتطلب حاليًا عناوين URL مرجعية بعيدة من نوع `http(s)` / MP4
    - `google` لأن مسار Gemini/Veo المشترك الحالي يستخدم إدخالًا محليًا مدعومًا بالـ buffer وهذا المسار غير مقبول في المسح المشترك
    - `openai` لأن المسار المشترك الحالي يفتقر إلى ضمانات وصول خاصة بالمؤسسة لفيديو inpaint/remix
- تضييق اختياري:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_SKIP_PROVIDERS=""` لتضمين كل مزوّد في المسح الافتراضي، بما في ذلك FAL
  - `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS=60000` لتقليل الحد الأقصى لعملية كل مزوّد من أجل تشغيل smoke أكثر شدة
- سلوك مصادقة اختياري:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لفرض مصادقة مخزن الملف الشخصي وتجاهل التجاوزات المعتمدة على env فقط

## حزمة Media الحية

- الأمر: `pnpm test:live:media`
- الغرض:
  - يشغّل مجموعات الصور والموسيقى والفيديو الحية المشتركة عبر نقطة دخول أصلية واحدة في المستودع
  - يحمّل تلقائيًا متغيرات env المفقودة للمزوّد من `~/.profile`
  - يضيّق تلقائيًا كل مجموعة إلى المزوّدين الذين يملكون حاليًا مصادقة صالحة افتراضيًا
  - يعيد استخدام `scripts/test-live.mjs`، لذلك يبقى سلوك Heartbeat والوضع الهادئ متسقًا
- أمثلة:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## مشغّلات Docker ‏(اختبارات اختيارية من نوع "يعمل على Linux")

تنقسم مشغّلات Docker هذه إلى فئتين:

- مشغّلات النماذج الحية: يشغّل `test:docker:live-models` و `test:docker:live-gateway` فقط ملف live المطابق القائم على مفاتيح الملف الشخصي داخل صورة Docker الخاصة بالمستودع (`src/agents/models.profiles.live.test.ts` و `src/gateway/gateway-models.profiles.live.test.ts`)، مع تركيب دليل الإعداد المحلي ومساحة العمل لديك (واستيراد `~/.profile` إذا تم تركيبه). نقاط الدخول المحلية المطابقة هي `test:live:models-profiles` و `test:live:gateway-profiles`.
- تستخدم مشغّلات Docker الحية افتراضيًا حد smoke أصغر حتى يبقى المسح الكامل عبر Docker عمليًا:
  يضبط `test:docker:live-models` افتراضيًا `OPENCLAW_LIVE_MAX_MODELS=12`، ويضبط
  `test:docker:live-gateway` افتراضيًا `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`، و
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. تجاوز متغيرات env هذه عندما
  تريد صراحةً المسح الأكبر الشامل.
- يقوم `test:docker:all` ببناء صورة Docker الحية مرة واحدة عبر `test:docker:live-build`، ثم يعيد استخدامها لمساري Docker الحيين.
- مشغّلات smoke للحاويات: تقوم `test:docker:openwebui` و `test:docker:onboard` و `test:docker:gateway-network` و `test:docker:mcp-channels` و `test:docker:plugins` بتشغيل حاوية أو أكثر فعلية والتحقق من مسارات تكامل على مستوى أعلى.

تقوم مشغّلات Docker الخاصة بالنماذج الحية أيضًا بتركيب منازل مصادقة CLI المطلوبة فقط ربطًا مباشرًا (أو جميع المنازل المدعومة عندما لا يكون التشغيل مضيقًا)، ثم تنسخها إلى home الحاوية قبل التشغيل حتى تتمكن OAuth الخاصة بـ CLI الخارجي من تحديث الرموز من دون تعديل مخزن مصادقة المضيف:

- النماذج المباشرة: `pnpm test:docker:live-models` ‏(السكريبت: `scripts/test-live-models-docker.sh`)
- اختبار smoke لربط ACP: ‏`pnpm test:docker:live-acp-bind` ‏(السكريبت: `scripts/test-live-acp-bind-docker.sh`)
- اختبار smoke للواجهة الخلفية CLI: ‏`pnpm test:docker:live-cli-backend` ‏(السكريبت: `scripts/test-live-cli-backend-docker.sh`)
- اختبار smoke لحزمة Codex app-server: ‏`pnpm test:docker:live-codex-harness` ‏(السكريبت: `scripts/test-live-codex-harness-docker.sh`)
- Gateway + وكيل dev: ‏`pnpm test:docker:live-gateway` ‏(السكريبت: `scripts/test-live-gateway-models-docker.sh`)
- اختبار smoke حي لـ Open WebUI: ‏`pnpm test:docker:openwebui` ‏(السكريبت: `scripts/e2e/openwebui-docker.sh`)
- معالج onboarding ‏(TTY، مع البنية الكاملة): ‏`pnpm test:docker:onboard` ‏(السكريبت: `scripts/e2e/onboard-docker.sh`)
- شبكات Gateway ‏(حاويتان، مصادقة WS + health): ‏`pnpm test:docker:gateway-network` ‏(السكريبت: `scripts/e2e/gateway-network-docker.sh`)
- جسر قناة MCP ‏(Gateway مُهيّأ مسبقًا + جسر stdio + اختبار smoke لإطار إشعارات Claude الخام): ‏`pnpm test:docker:mcp-channels` ‏(السكريبت: `scripts/e2e/mcp-channels-docker.sh`)
- Plugins ‏(اختبار smoke للتثبيت + الاسم البديل `/plugin` + دلالات إعادة تشغيل Claude-bundle): ‏`pnpm test:docker:plugins` ‏(السكريبت: `scripts/e2e/plugins-docker.sh`)

تقوم مشغّلات Docker الخاصة بالنماذج الحية أيضًا بتركيب النسخة الحالية من المستودع
كتركيب للقراءة فقط، ثم تجهّزها داخل دليل عمل مؤقت داخل الحاوية. وهذا يحافظ على
رشاقة صورة وقت التشغيل مع الاستمرار في تشغيل Vitest على المصدر/الإعداد المحليين لديك بدقة.
تتخطى خطوة التجهيز ذاكرات cache المحلية الكبيرة ومخرجات بناء التطبيقات مثل
`.pnpm-store` و `.worktrees` و `__openclaw_vitest__` وأدلة مخرجات `.build` المحلية للتطبيق أو
Gradle حتى لا تقضي تشغيلات Docker الحية دقائق في نسخ
artifacts خاصة بالجهاز.
كما تضبط `OPENCLAW_SKIP_CHANNELS=1` حتى لا تبدأ probes الحية لـ gateway
عمّال القنوات الحقيقية مثل Telegram/Discord وغيرها داخل الحاوية.
لا يزال `test:docker:live-models` يشغّل `pnpm test:live`، لذا مرّر
`OPENCLAW_LIVE_GATEWAY_*` أيضًا عندما تحتاج إلى تضييق أو استبعاد تغطية gateway
الحية من مسار Docker هذا.
يُعد `test:docker:openwebui` اختبار smoke توافق على مستوى أعلى: فهو يبدأ
حاوية OpenClaw gateway مع تمكين نقاط النهاية HTTP المتوافقة مع OpenAI،
ويبدأ حاوية Open WebUI مثبتة مقابل ذلك gateway، ويسجّل الدخول عبر
Open WebUI، ويتحقق من أن `/api/models` يعرّض `openclaw/default`، ثم يرسل
طلب دردشة حقيقيًا عبر وكيل `/api/chat/completions` الخاص بـ Open WebUI.
قد يكون التشغيل الأول أبطأ بشكل ملحوظ لأن Docker قد يحتاج إلى سحب
صورة Open WebUI، وقد يحتاج Open WebUI إلى إكمال إعداد البدء البارد الخاص به.
يتوقع هذا المسار وجود مفتاح نموذج حي صالح، ويُعد `OPENCLAW_PROFILE_FILE`
(`~/.profile` افتراضيًا) الطريقة الأساسية لتوفيره في التشغيلات عبر Docker.
تطبع التشغيلات الناجحة حمولة JSON صغيرة مثل `{ "ok": true, "model":
"openclaw/default", ... }`.
يتميّز `test:docker:mcp-channels` بأنه حتمي عمدًا ولا يحتاج إلى
حساب Telegram أو Discord أو iMessage حقيقي. فهو يشغّل حاوية Gateway
مهيأة مسبقًا، ويبدأ حاوية ثانية تشغّل `openclaw mcp serve`، ثم
يتحقق من اكتشاف المحادثات الموجّهة، وقراءات transcript، وبيانات المرفقات الوصفية،
وسلوك قائمة الانتظار الحية للأحداث، وتوجيه الإرسال الصادر، وإشعارات القناة +
الأذونات على نمط Claude عبر جسر stdio MCP الحقيقي. ويفحص تحقق الإشعارات
إطارات stdio MCP الخام مباشرة، بحيث يتحقق smoke مما يصدره الجسر
فعليًا، لا فقط مما تعرضه SDK عميل معين.

اختبار smoke يدوي لخيط ACP بلغة طبيعية بسيطة (ليس في CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- احتفظ بهذا السكريبت من أجل تدفقات الانحدار/تصحيح الأخطاء. قد تكون هناك حاجة إليه مرة أخرى للتحقق من توجيه خيوط ACP، لذلك لا تحذفه.

متغيرات env مفيدة:

- `OPENCLAW_CONFIG_DIR=...` ‏(الافتراضي: `~/.openclaw`) ويُركّب إلى `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` ‏(الافتراضي: `~/.openclaw/workspace`) ويُركّب إلى `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` ‏(الافتراضي: `~/.profile`) ويُركّب إلى `/home/node/.profile` ويُستورد قبل تشغيل الاختبارات
- `OPENCLAW_DOCKER_PROFILE_ENV_ONLY=1` للتحقق من متغيرات env المستوردة فقط من `OPENCLAW_PROFILE_FILE`، باستخدام أدلة إعداد/مساحة عمل مؤقتة ومن دون أي تراكيب مصادقة CLI خارجية
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` ‏(الافتراضي: `~/.cache/openclaw/docker-cli-tools`) ويُركّب إلى `/home/node/.npm-global` لتثبيتات CLI المخزنة داخل Docker
- تُركّب أدلة/ملفات مصادقة CLI الخارجية تحت `$HOME` للقراءة فقط تحت `/host-auth...`، ثم تُنسخ إلى `/home/node/...` قبل بدء الاختبارات
  - الأدلة الافتراضية: `.minimax`
  - الملفات الافتراضية: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - تقوم التشغيلات المضيقة للمزوّد بتركيب الأدلة/الملفات المطلوبة فقط والمستنتجة من `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - يمكن التجاوز يدويًا باستخدام `OPENCLAW_DOCKER_AUTH_DIRS=all` أو `OPENCLAW_DOCKER_AUTH_DIRS=none` أو قائمة مفصولة بفواصل مثل `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` لتضييق التشغيل
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...` لتصفية المزوّدين داخل الحاوية
- `OPENCLAW_SKIP_DOCKER_BUILD=1` لإعادة استخدام صورة `openclaw:local-live` موجودة لتشغيلات الإعادة التي لا تحتاج إلى إعادة بناء
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` لضمان أن تأتي بيانات الاعتماد من مخزن الملف الشخصي (وليس من env)
- `OPENCLAW_OPENWEBUI_MODEL=...` لاختيار النموذج الذي يعرّضه gateway لاختبار Open WebUI smoke
- `OPENCLAW_OPENWEBUI_PROMPT=...` لتجاوز prompt فحص nonce المستخدم في اختبار Open WebUI smoke
- `OPENWEBUI_IMAGE=...` لتجاوز وسم صورة Open WebUI المثبّت

## التحقق من التوثيق

شغّل فحوصات التوثيق بعد تعديلات المستندات: `pnpm check:docs`.
وشغّل التحقق الكامل من روابط Mintlify عندما تحتاج أيضًا إلى فحوصات عناوين الصفحة الداخلية: `pnpm docs:check-links:anchors`.

## اختبارات الانحدار دون اتصال (آمنة لـ CI)

هذه اختبارات انحدار «لخط الأنابيب الحقيقي» من دون مزوّدين حقيقيين:

- استدعاء أدوات Gateway ‏(OpenAI وهمي، مع حلقة gateway + agent حقيقية): `src/gateway/gateway.test.ts` ‏(الحالة: `"runs a mock OpenAI tool call end-to-end via gateway agent loop"`)
- معالج Gateway ‏(‏WS ‏`wizard.start`/`wizard.next`، مع فرض كتابة config + auth): ‏`src/gateway/gateway.test.ts` ‏(الحالة: `"runs wizard over ws and writes auth token config"`)

## تقييمات موثوقية الوكيل (Skills)

لدينا بالفعل بعض الاختبارات الآمنة لـ CI التي تتصرف مثل «تقييمات موثوقية الوكيل»:

- استدعاء أدوات وهمي عبر حلقة gateway + agent الحقيقية (`src/gateway/gateway.test.ts`).
- تدفقات معالج كاملة من طرف إلى طرف تتحقق من ربط الجلسات وتأثيرات الإعداد (`src/gateway/gateway.test.ts`).

ما الذي لا يزال ناقصًا بالنسبة إلى Skills ‏(انظر [Skills](/ar/tools/skills)):

- **اتخاذ القرار:** عندما تكون Skills مدرجة في prompt، هل يختار الوكيل Skill الصحيحة (أو يتجنب غير ذات الصلة)؟
- **الامتثال:** هل يقرأ الوكيل `SKILL.md` قبل الاستخدام ويتبع الخطوات/الوسائط المطلوبة؟
- **عقود سير العمل:** سيناريوهات متعددة الأدوار تتحقق من ترتيب الأدوات، واستمرار سجل الجلسة، وحدود sandbox.

يجب أن تبقى التقييمات المستقبلية حتمية أولًا:

- مشغّل سيناريو يستخدم مزوّدين وهميين للتحقق من استدعاءات الأدوات + ترتيبها، وقراءات ملفات Skill، وربط الجلسات.
- مجموعة صغيرة من السيناريوهات المركزة على Skills ‏(استخدام مقابل تجنب، والبوابات، وحقن prompt).
- تقييمات حية اختيارية (opt-in، ومقيّدة عبر env) فقط بعد وجود المجموعة الآمنة لـ CI.

## اختبارات العقود (شكل Plugin والقناة)

تتحقق اختبارات العقود من أن كل Plugin وقناة مسجلين يطابقان
عقد الواجهة الخاص بهما. فهي تكرّر على كل Plugins المكتشفة وتشغّل مجموعة من
التحققات الخاصة بالشكل والسلوك. ويتخطى مسار unit الافتراضي `pnpm test`
هذه الملفات المشتركة لاختبار الأسطح و smoke عمدًا؛ شغّل أوامر العقود صراحةً
عندما تلمس أسطح القنوات أو المزوّدين المشتركة.

### الأوامر

- كل العقود: `pnpm test:contracts`
- عقود القنوات فقط: `pnpm test:contracts:channels`
- عقود المزوّدين فقط: `pnpm test:contracts:plugins`

### عقود القنوات

توجد في `src/channels/plugins/contracts/*.contract.test.ts`:

- **plugin** - الشكل الأساسي لـ Plugin ‏(المعرّف، والاسم، والقدرات)
- **setup** - عقد معالج الإعداد
- **session-binding** - سلوك ربط الجلسة
- **outbound-payload** - بنية حمولة الرسالة
- **inbound** - معالجة الرسائل الواردة
- **actions** - معالجات إجراءات القناة
- **threading** - التعامل مع معرّف الخيط
- **directory** - واجهة API للدليل/القائمة
- **group-policy** - فرض سياسة المجموعة

### عقود حالة المزوّد

توجد في `src/plugins/contracts/*.contract.test.ts`.

- **status** - probes حالة القناة
- **registry** - شكل سجل Plugin

### عقود المزوّد

توجد في `src/plugins/contracts/*.contract.test.ts`:

- **auth** - عقد تدفق المصادقة
- **auth-choice** - اختيار/تحديد المصادقة
- **catalog** - واجهة API لفهرس النماذج
- **discovery** - اكتشاف Plugin
- **loader** - تحميل Plugin
- **runtime** - وقت تشغيل المزوّد
- **shape** - شكل/واجهة Plugin
- **wizard** - معالج الإعداد

### متى يجب تشغيلها

- بعد تغيير صادرات `plugin-sdk` أو مساراته الفرعية
- بعد إضافة Plugin قناة أو مزوّد أو تعديلها
- بعد إعادة هيكلة تسجيل Plugin أو اكتشافه

تعمل اختبارات العقود في CI ولا تتطلب مفاتيح API حقيقية.

## إضافة اختبارات الانحدار (إرشادات)

عندما تصلح مشكلة مزوّد/نموذج اكتُشفت في live:

- أضف اختبار انحدار آمنًا لـ CI إن أمكن (مزوّد وهمي/بديل، أو التقاط تحويل شكل الطلب الدقيق)
- إذا كانت المشكلة بطبيعتها حية فقط (حدود المعدل، وسياسات المصادقة)، فأبقِ الاختبار الحي ضيقًا واختياريًا عبر متغيرات env
- فضّل استهداف أصغر طبقة تلتقط الخطأ:
  - خطأ تحويل/إعادة تشغيل طلب المزوّد → اختبار نماذج مباشر
  - خطأ خط جلسة/سجل/أدوات gateway → اختبار smoke حي لـ gateway أو اختبار Gateway وهمي وآمن لـ CI
- حاجز حماية اجتياز SecretRef:
  - يشتق `src/secrets/exec-secret-ref-id-parity.test.ts` هدفًا نموذجيًا واحدًا لكل فئة SecretRef من بيانات تعريف السجل (`listSecretTargetRegistryEntries()`)، ثم يتحقق من رفض معرّفات exec لمقاطع الاجتياز.
  - إذا أضفت عائلة هدف SecretRef جديدة من نوع `includeInPlan` في `src/secrets/target-registry-data.ts`، فحدّث `classifyTargetClass` في ذلك الاختبار. يفشل الاختبار عمدًا عند وجود معرّفات هدف غير مصنفة حتى لا يمكن تخطي الفئات الجديدة بصمت.
