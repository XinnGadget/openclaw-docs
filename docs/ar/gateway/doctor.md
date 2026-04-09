---
read_when:
    - إضافة ترحيلات doctor أو تعديلها
    - إدخال تغييرات جذرية على الإعدادات
summary: 'أمر Doctor: فحوصات السلامة، وترحيلات الإعدادات، وخطوات الإصلاح'
title: Doctor
x-i18n:
    generated_at: "2026-04-09T01:29:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: 75d321bd1ad0e16c29f2382e249c51edfc3a8d33b55bdceea39e7dbcd4901fce
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

يُعد `openclaw doctor` أداة الإصلاح + الترحيل في OpenClaw. فهو يصلح
الإعدادات/الحالة القديمة، ويفحص السلامة، ويوفر خطوات إصلاح عملية.

## البدء السريع

```bash
openclaw doctor
```

### بدون واجهة / للأتمتة

```bash
openclaw doctor --yes
```

اقبل القيم الافتراضية من دون مطالبة (بما في ذلك خطوات إصلاح إعادة التشغيل/الخدمة/بيئة sandbox عند الاقتضاء).

```bash
openclaw doctor --repair
```

طبّق الإصلاحات الموصى بها من دون مطالبة (إصلاحات + عمليات إعادة تشغيل حيث يكون ذلك آمنًا).

```bash
openclaw doctor --repair --force
```

طبّق الإصلاحات القوية أيضًا (يستبدل إعدادات supervisor المخصصة).

```bash
openclaw doctor --non-interactive
```

شغّل بدون مطالبات وطبّق فقط الترحيلات الآمنة (تطبيع الإعدادات + نقل الحالة على القرص). يتخطى إجراءات إعادة التشغيل/الخدمة/بيئة sandbox التي تتطلب تأكيدًا بشريًا.
تعمل ترحيلات الحالة القديمة تلقائيًا عند اكتشافها.

```bash
openclaw doctor --deep
```

افحص خدمات النظام لاكتشاف تثبيتات Gateway إضافية (launchd/systemd/schtasks).

إذا أردت مراجعة التغييرات قبل الكتابة، فافتح ملف الإعدادات أولًا:

```bash
cat ~/.openclaw/openclaw.json
```

## ما الذي يفعله (ملخص)

- تحديث اختياري قبل التنفيذ لتثبيتات git (تفاعلي فقط).
- فحص حداثة بروتوكول واجهة المستخدم (يعيد بناء Control UI عندما يكون مخطط البروتوكول أحدث).
- فحص السلامة + مطالبة بإعادة التشغيل.
- ملخص حالة Skills (مؤهلة/مفقودة/محجوبة) وحالة الإضافات.
- تطبيع الإعدادات للقيم القديمة.
- ترحيل إعدادات Talk من الحقول المسطحة القديمة `talk.*` إلى `talk.provider` + `talk.providers.<provider>`.
- فحوصات ترحيل المتصفح لإعدادات إضافة Chrome القديمة وجهوزية Chrome MCP.
- تحذيرات تجاوز موفّر OpenCode (`models.providers.opencode` / `models.providers.opencode-go`).
- تحذيرات حجب Codex OAuth (`models.providers.openai-codex`).
- فحص متطلبات OAuth TLS لملفات OpenAI Codex OAuth التعريفية.
- ترحيل الحالة القديمة على القرص (sessions/دليل agent/مصادقة WhatsApp).
- ترحيل مفتاح عقد بيان plugin القديم (`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`).
- ترحيل مخزن cron القديم (`jobId`, `schedule.cron`, حقول delivery/payload العلوية، و`provider` داخل payload، ووظائف fallback للويب هوك البسيطة `notify: true`).
- فحص ملفات قفل الجلسات وتنظيف الأقفال القديمة.
- فحوصات سلامة الحالة والصلاحيات (الجلسات، والسجلات، ودليل الحالة).
- فحوصات صلاحيات ملف الإعدادات (`chmod 600`) عند التشغيل محليًا.
- سلامة مصادقة النماذج: يفحص انتهاء OAuth، ويمكنه تحديث الرموز الموشكة على الانتهاء، ويبلغ عن حالات التهدئة/التعطيل لملفات تعريف المصادقة.
- اكتشاف دليل مساحة عمل إضافي (`~/openclaw`).
- إصلاح صورة sandbox عند تفعيل العزل.
- ترحيل الخدمة القديمة واكتشاف Gateway إضافي.
- ترحيل الحالة القديمة لقناة Matrix (في وضع `--fix` / `--repair`).
- فحوصات وقت تشغيل Gateway (الخدمة مثبّتة ولكنها لا تعمل؛ تسمية launchd مخزنة مؤقتًا).
- تحذيرات حالة القنوات (يتم فحصها من Gateway الجاري تشغيله).
- تدقيق إعدادات supervisor (launchd/systemd/schtasks) مع إصلاح اختياري.
- فحوصات أفضل ممارسات وقت تشغيل Gateway (Node مقابل Bun، ومسارات مديري الإصدارات).
- تشخيص تعارض منفذ Gateway (الافتراضي `18789`).
- تحذيرات أمنية لسياسات الرسائل الخاصة المفتوحة.
- فحوصات مصادقة Gateway لوضع الرمز المحلي (يوفر إنشاء رمز عندما لا يوجد مصدر رمز؛ ولا يستبدل إعدادات SecretRef الخاصة بالرمز).
- فحص `systemd linger` على Linux.
- فحص حجم ملف تمهيد مساحة العمل (تحذيرات الاقتطاع/الاقتراب من الحد لملفات السياق).
- فحص حالة الإكمال الصدفي والتثبيت/الترقية التلقائيين.
- فحص جاهزية موفّر embedding للبحث في الذاكرة (نموذج محلي، أو مفتاح API بعيد، أو ملف QMD ثنائي).
- فحوصات تثبيت المصدر (عدم تطابق مساحة عمل pnpm، وغياب أصول UI، وغياب ملف tsx الثنائي).
- يكتب الإعدادات المحدّثة + بيانات تعريف المعالج.

## الإكمال الرجعي وإعادة الضبط في Dreams UI

يتضمن مشهد Dreams في Control UI إجراءات **Backfill** و**Reset** و**Clear Grounded**
لسير العمل الخاص بالأحلام المرتكزة. تستخدم هذه الإجراءات
أساليب RPC على نمط doctor في Gateway، لكنها **ليست** جزءًا من إصلاح/ترحيل
CLI الخاص بـ `openclaw doctor`.

ما الذي تفعله:

- يفحص **Backfill** ملفات `memory/YYYY-MM-DD.md` التاريخية في
  مساحة العمل النشطة، ويشغّل مرور يوميات REM المرتكزة، ويكتب إدخالات
  إكمال رجعي قابلة للعكس في `DREAMS.md`.
- يزيل **Reset** فقط إدخالات يوميات الإكمال الرجعي المعلَّمة من `DREAMS.md`.
- يزيل **Clear Grounded** فقط الإدخالات المرحلية قصيرة الأجل المرتكزة فقط
  التي جاءت من إعادة تشغيل تاريخية ولم تراكم بعد استدعاءً حيًا أو
  دعمًا يوميًا.

ما الذي لا تفعله بمفردها:

- لا تعدّل `MEMORY.md`
- لا تشغّل ترحيلات doctor الكاملة
- لا ترحّل المرشحين المرتكزين تلقائيًا إلى مخزن الترقية قصير الأجل الحي
  ما لم تشغّل صراحةً مسار CLI المرحلي أولًا

إذا أردت أن تؤثر إعادة التشغيل التاريخية المرتكزة في
مسار الترقية العميق المعتاد، فاستخدم مسار CLI بدلًا من ذلك:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

يؤدي ذلك إلى ترحيل المرشحين الدائمين المرتكزين إلى مخزن الأحلام قصير الأجل
مع إبقاء `DREAMS.md` كسطح للمراجعة.

## السلوك المفصل والمبررات

### 0) تحديث اختياري (تثبيتات git)

إذا كان هذا checkout من git وكان doctor يعمل بشكل تفاعلي، فإنه يعرض
التحديث (fetch/rebase/build) قبل تشغيل doctor.

### 1) تطبيع الإعدادات

إذا كانت الإعدادات تحتوي على أشكال قيم قديمة (مثل `messages.ackReaction`
من دون تجاوز خاص بالقناة)، فإن doctor يطبّعها إلى
المخطط الحالي.

ويشمل ذلك حقول Talk المسطحة القديمة. فالإعدادات العامة الحالية لـ Talk هي
`talk.provider` + `talk.providers.<provider>`. ويعيد doctor كتابة
الأشكال القديمة مثل
`talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` إلى خريطة الموفّر.

### 2) ترحيلات مفاتيح الإعدادات القديمة

عندما تحتوي الإعدادات على مفاتيح مهجورة، ترفض الأوامر الأخرى التشغيل وتطلب
منك تشغيل `openclaw doctor`.

سيقوم Doctor بما يلي:

- شرح المفاتيح القديمة التي تم العثور عليها.
- عرض الترحيل الذي طبّقه.
- إعادة كتابة `~/.openclaw/openclaw.json` بالمخطط المحدّث.

كما أن Gateway يشغّل ترحيلات doctor تلقائيًا عند بدء التشغيل عندما يكتشف
تنسيق إعدادات قديمًا، بحيث يتم إصلاح الإعدادات القديمة من دون تدخل يدوي.
تتم معالجة ترحيلات مخزن وظائف Cron بواسطة `openclaw doctor --fix`.

الترحيلات الحالية:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → `bindings` في المستوى الأعلى
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- الحقول القديمة `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `messages.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `messages.tts.providers.<provider>`
- `channels.discord.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.voice.tts.providers.<provider>`
- `channels.discord.accounts.<id>.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.accounts.<id>.voice.tts.providers.<provider>`
- `plugins.entries.voice-call.config.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `plugins.entries.voice-call.config.tts.providers.<provider>`
- `plugins.entries.voice-call.config.provider: "log"` → `"mock"`
- `plugins.entries.voice-call.config.twilio.from` → `plugins.entries.voice-call.config.fromNumber`
- `plugins.entries.voice-call.config.streaming.sttProvider` → `plugins.entries.voice-call.config.streaming.provider`
- `plugins.entries.voice-call.config.streaming.openaiApiKey|sttModel|silenceDurationMs|vadThreshold`
  → `plugins.entries.voice-call.config.streaming.providers.openai.*`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- بالنسبة إلى القنوات التي تحتوي على `accounts` مسماة ولكن لا تزال فيها قيم قنوات علوية لحساب واحد، انقل تلك القيم ذات النطاق الحسابي إلى الحساب المُرقّى المختار لتلك القناة (`accounts.default` لمعظم القنوات؛ ويمكن لـ Matrix الحفاظ على هدف مسمى/افتراضي مطابق موجود)
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- إزالة `browser.relayBindHost` (إعداد relay قديم للإضافة)

وتشمل تحذيرات Doctor أيضًا إرشادات الافتراضي للحسابات للقنوات متعددة الحسابات:

- إذا تم إعداد إدخالين أو أكثر في `channels.<channel>.accounts` من دون `channels.<channel>.defaultAccount` أو `accounts.default`، يحذر doctor من أن التوجيه الاحتياطي قد يختار حسابًا غير متوقع.
- إذا تم ضبط `channels.<channel>.defaultAccount` على معرّف حساب غير معروف، يحذر doctor ويسرد معرّفات الحسابات المهيأة.

### 2b) تجاوزات موفّر OpenCode

إذا أضفت يدويًا `models.providers.opencode` أو `opencode-zen` أو `opencode-go`،
فإن ذلك يتجاوز فهرس OpenCode المضمّن من `@mariozechner/pi-ai`.
وقد يفرض ذلك استخدام واجهة API خاطئة للنماذج أو يجعل التكاليف صفرًا. يحذر doctor حتى تتمكن
من إزالة التجاوز واستعادة توجيه API + التكاليف لكل نموذج.

### 2c) ترحيل المتصفح وجهوزية Chrome MCP

إذا كانت إعدادات المتصفح لا تزال تشير إلى مسار إضافة Chrome الذي أُزيل، فإن doctor
يطبعها إلى نموذج الربط الحالي لـ Chrome MCP المحلي على المضيف:

- `browser.profiles.*.driver: "extension"` تصبح `"existing-session"`
- تتم إزالة `browser.relayBindHost`

كما يدقق doctor مسار Chrome MCP المحلي على المضيف عندما تستخدم
`defaultProfile: "user"` أو ملف تعريف `existing-session` مهيأ:

- يفحص ما إذا كان Google Chrome مثبتًا على نفس المضيف لملفات التعريف
  ذات الاتصال التلقائي الافتراضي
- يفحص إصدار Chrome المكتشف ويحذر عندما يكون أقل من Chrome 144
- يذكّرك بتمكين التنقيح عن بُعد في صفحة فحص المتصفح (مثل
  `chrome://inspect/#remote-debugging` أو `brave://inspect/#remote-debugging`
  أو `edge://inspect/#remote-debugging`)

لا يمكن لـ Doctor تمكين الإعداد من جهة Chrome نيابةً عنك. ولا يزال Chrome MCP المحلي على المضيف
يتطلب ما يلي:

- متصفحًا قائمًا على Chromium بإصدار 144+ على مضيف gateway/node
- أن يكون المتصفح قيد التشغيل محليًا
- تمكين التنقيح عن بُعد في ذلك المتصفح
- الموافقة على أول مطالبة موافقة على الربط في المتصفح

الجهوزية هنا تتعلق فقط بمتطلبات الربط المحلي. ويحتفظ existing-session
بحدود مسار Chrome MCP الحالية؛ أما المسارات المتقدمة مثل `responsebody` وتصدير PDF
واعتراض التنزيلات والإجراءات الدفعية فما تزال تتطلب
متصفحًا مُدارًا أو ملف تعريف CDP خامًا.

لا ينطبق هذا الفحص على تدفقات Docker أو sandbox أو remote-browser أو غيرها
من التدفقات عديمة الواجهة. فهي تواصل استخدام CDP الخام.

### 2d) متطلبات OAuth TLS

عند إعداد ملف تعريف OpenAI Codex OAuth، يفحص doctor نقطة نهاية
تفويض OpenAI للتحقق من أن حزمة TLS المحلية لـ Node/OpenSSL يمكنها
التحقق من سلسلة الشهادات. إذا فشل الفحص بخطأ شهادة (مثل
`UNABLE_TO_GET_ISSUER_CERT_LOCALLY` أو شهادة منتهية أو شهادة موقعة ذاتيًا)،
يطبع doctor إرشادات إصلاح خاصة بالمنصة. وعلى macOS مع Node من Homebrew،
يكون الإصلاح عادةً `brew postinstall ca-certificates`. ومع `--deep`، يعمل
الفحص حتى إذا كان Gateway سليمًا.

### 2c) تجاوزات موفّر Codex OAuth

إذا كنت قد أضفت سابقًا إعدادات نقل OpenAI قديمة ضمن
`models.providers.openai-codex`، فقد تحجب مسار
موفّر Codex OAuth المضمّن الذي تستخدمه الإصدارات الأحدث تلقائيًا. ويحذر
doctor عندما يرى إعدادات النقل القديمة هذه إلى جانب Codex OAuth حتى
تتمكن من إزالة أو إعادة كتابة تجاوز النقل القديم واستعادة
سلوك التوجيه/الاحتياطيات المضمّن. وما تزال الوكلاء المخصصة والتجاوزات
المعتمدة على الرؤوس فقط مدعومة ولا تطلق هذا التحذير.

### 3) ترحيلات الحالة القديمة (تخطيط القرص)

يمكن لـ Doctor ترحيل التخطيطات القديمة على القرص إلى البنية الحالية:

- مخزن الجلسات + السجلات:
  - من `~/.openclaw/sessions/` إلى `~/.openclaw/agents/<agentId>/sessions/`
- دليل Agent:
  - من `~/.openclaw/agent/` إلى `~/.openclaw/agents/<agentId>/agent/`
- حالة مصادقة WhatsApp ‏(Baileys):
  - من `~/.openclaw/credentials/*.json` القديمة (باستثناء `oauth.json`)
  - إلى `~/.openclaw/credentials/whatsapp/<accountId>/...` (معرّف الحساب الافتراضي: `default`)

هذه الترحيلات تتم بأفضل جهد وهي idempotent؛ وسيُصدر doctor تحذيرات عندما
يترك أي مجلدات قديمة خلفه كنسخ احتياطية. كما أن Gateway/CLI يرحّل
الجلسات القديمة + دليل agent تلقائيًا عند بدء التشغيل بحيث تهبط
السجلات/المصادقة/النماذج في المسار الخاص بكل agent من دون تشغيل doctor يدويًا.
ويتم ترحيل مصادقة WhatsApp عمدًا فقط عبر `openclaw doctor`. كما أن تطبيع
Talk provider/provider-map يقارن الآن وفق المساواة البنيوية، لذا لم تعد
الاختلافات في ترتيب المفاتيح فقط تطلق تغييرات no-op متكررة مع
`doctor --fix`.

### 3a) ترحيلات بيانات plugin القديمة

يفحص Doctor جميع بيانات plugin المثبتة لاكتشاف مفاتيح
القدرات العلوية المهجورة (`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`). وعند العثور عليها، يعرض نقلها إلى الكائن `contracts`
وإعادة كتابة ملف البيان في مكانه. هذا الترحيل idempotent؛
فإذا كان المفتاح `contracts` يحتوي بالفعل على القيم نفسها، تتم إزالة
المفتاح القديم من دون تكرار البيانات.

### 3b) ترحيلات مخزن cron القديمة

يفحص Doctor أيضًا مخزن وظائف cron (`~/.openclaw/cron/jobs.json` افتراضيًا،
أو `cron.store` عند تجاوزه) لاكتشاف أشكال الوظائف القديمة التي لا يزال
الجدول الزمني يقبلها للتوافق.

تشمل عمليات تنظيف cron الحالية ما يلي:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- حقول payload العلوية (`message`, `model`, `thinking`, ...) → `payload`
- حقول delivery العلوية (`deliver`, `channel`, `to`, `provider`, ...) → `delivery`
- أسماء delivery المستعارة `provider` داخل payload → `delivery.channel` صريح
- وظائف fallback القديمة البسيطة للويب هوك `notify: true` → `delivery.mode="webhook"` صريح مع `delivery.to=cron.webhook`

لا يرحّل Doctor وظائف `notify: true` تلقائيًا إلا عندما يمكنه
فعل ذلك من دون تغيير السلوك. وإذا جمعت وظيفة بين fallback notify القديم و
وضع delivery غير webhook موجود، فإن doctor يحذر ويترك الوظيفة للمراجعة اليدوية.

### 3c) تنظيف قفل الجلسة

يفحص Doctor كل دليل جلسات agent بحثًا عن ملفات قفل كتابة قديمة — وهي الملفات التي تُترك
وراءها عندما تخرج الجلسة بشكل غير طبيعي. ولكل ملف قفل يتم العثور عليه، يبلّغ بما يلي:
المسار، وPID، وما إذا كان PID لا يزال حيًا، وعمر القفل، وما إذا كان
يُعتبر قديمًا (PID ميت أو أقدم من 30 دقيقة). وفي وضع `--fix` / `--repair`
يزيل ملفات القفل القديمة تلقائيًا؛ وإلا فإنه يطبع ملاحظة ويطلب
منك إعادة التشغيل باستخدام `--fix`.

### 4) فحوصات سلامة الحالة (استمرارية الجلسة، والتوجيه، والسلامة)

دليل الحالة هو الجذع التشغيلي. وإذا اختفى، فستفقد
الجلسات وبيانات الاعتماد والسجلات والإعدادات (إلا إذا كانت لديك نسخ احتياطية في مكان آخر).

يفحص Doctor ما يلي:

- **غياب دليل الحالة**: يحذر من فقدان كارثي للحالة، ويطالب بإعادة إنشاء
  الدليل، ويذكّرك بأنه لا يمكنه استعادة البيانات المفقودة.
- **صلاحيات دليل الحالة**: يتحقق من قابلية الكتابة؛ ويعرض إصلاح الصلاحيات
  (ويصدر تلميح `chown` عند اكتشاف عدم تطابق المالك/المجموعة).
- **دليل حالة macOS المتزامن سحابيًا**: يحذر عندما تُحل الحالة ضمن iCloud Drive
  (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) أو
  `~/Library/CloudStorage/...` لأن المسارات المدعومة بالمزامنة قد تتسبب في بطء الإدخال/الإخراج
  وسباقات القفل/المزامنة.
- **دليل حالة Linux على SD أو eMMC**: يحذر عندما تُحل الحالة إلى مصدر تركيب `mmcblk*`،
  لأن الإدخال/الإخراج العشوائي المعتمد على SD أو eMMC قد يكون أبطأ ويتعرض لاستهلاك أسرع
  مع كتابات الجلسات وبيانات الاعتماد.
- **غياب دلائل الجلسات**: إن `sessions/` ودليل مخزن الجلسات
  مطلوبان للحفاظ على السجل وتجنب أعطال `ENOENT`.
- **عدم تطابق السجلات**: يحذر عندما تحتوي إدخالات الجلسات الحديثة على ملفات
  سجل مفقودة.
- **جلسة رئيسية “JSONL بسطر واحد”**: يعلّم الحالة عندما يحتوي السجل الرئيسي على
  سطر واحد فقط (السجل لا يتراكم).
- **أدلة حالة متعددة**: يحذر عند وجود عدة مجلدات `~/.openclaw` عبر
  أدلة منزلية أو عندما يشير `OPENCLAW_STATE_DIR` إلى مكان آخر (قد ينقسم السجل بين التثبيتات).
- **تذكير الوضع البعيد**: إذا كان `gateway.mode=remote`، يذكّرك doctor بتشغيله
  على المضيف البعيد (لأن الحالة موجودة هناك).
- **صلاحيات ملف الإعدادات**: يحذر إذا كان `~/.openclaw/openclaw.json`
  قابلاً للقراءة من المجموعة/العالم ويعرض تشديده إلى `600`.

### 5) سلامة مصادقة النماذج (انتهاء OAuth)

يفحص Doctor ملفات OAuth التعريفية في مخزن المصادقة، ويحذر عندما تكون
الرموز المميزة على وشك الانتهاء/منتهية، ويمكنه تحديثها عندما يكون ذلك آمنًا. وإذا كان
ملف تعريف OAuth/token الخاص بـ Anthropic قديمًا، فإنه يقترح
مفتاح Anthropic API أو مسار Anthropic setup-token.
ولا تظهر مطالبات التحديث إلا عند التشغيل بشكل تفاعلي (TTY)؛ أما `--non-interactive`
فيتخطى محاولات التحديث.

وعندما يفشل تحديث OAuth فشلًا دائمًا (مثل `refresh_token_reused` أو
`invalid_grant` أو عندما يخبرك الموفّر بتسجيل الدخول مرة أخرى)،
فإن doctor يبلغ بأن إعادة المصادقة مطلوبة ويطبع
أمر `openclaw models auth login --provider ...` الدقيق المطلوب تشغيله.

كما يبلغ Doctor أيضًا عن ملفات تعريف المصادقة غير القابلة للاستخدام مؤقتًا بسبب:

- فترات تهدئة قصيرة (حدود المعدل/المهلات/إخفاقات المصادقة)
- تعطيلات أطول (إخفاقات الفوترة/الرصيد)

### 6) التحقق من نموذج Hooks

إذا كان `hooks.gmail.model` مضبوطًا، فإن doctor يتحقق من مرجع النموذج
مقابل الفهرس وقائمة السماح ويحذر عندما لا يمكن حله أو يكون غير مسموح.

### 7) إصلاح صورة sandbox

عند تفعيل العزل، يفحص doctor صور Docker ويعرض بناءها أو
التبديل إلى الأسماء القديمة إذا كانت الصورة الحالية مفقودة.

### 7b) تبعيات وقت تشغيل plugin المجمعة

يتحقق Doctor من وجود تبعيات وقت التشغيل الخاصة بالـ plugin المجمعة (مثل
حزم وقت تشغيل Discord plugin) في جذر تثبيت OpenClaw.
وإذا كانت أي منها مفقودة، فإن doctor يبلغ عن الحزم ويثبتها في
وضع `openclaw doctor --fix` / `openclaw doctor --repair`.

### 8) ترحيلات خدمة Gateway وتلميحات التنظيف

يكتشف Doctor خدمات Gateway القديمة (launchd/systemd/schtasks) و
يعرض إزالتها وتثبيت خدمة OpenClaw باستخدام منفذ Gateway الحالي.
كما يمكنه أيضًا فحص خدمات إضافية شبيهة بـ Gateway وطباعة تلميحات للتنظيف.
وتُعتبر خدمات OpenClaw Gateway المسماة بحسب الملف التعريفي خدمات من الدرجة الأولى ولا
تُوسم بأنها "إضافية".

### 8b) ترحيل Matrix عند بدء التشغيل

عندما يحتوي حساب قناة Matrix على ترحيل حالة قديم معلّق أو قابل للتنفيذ،
فإن doctor (في وضع `--fix` / `--repair`) ينشئ لقطة قبل الترحيل ثم
يشغّل خطوات الترحيل بأفضل جهد: ترحيل حالة Matrix القديمة وإعداد
الحالة المشفرة القديمة. وكلتا الخطوتين غير قاتلتين؛ تُسجّل الأخطاء ويستمر
بدء التشغيل. وفي وضع القراءة فقط (`openclaw doctor` بدون `--fix`) يتم
تخطي هذا الفحص بالكامل.

### 9) تحذيرات أمنية

يصدر Doctor تحذيرات عندما يكون موفّر مفتوحًا للرسائل الخاصة من دون قائمة سماح، أو
عندما تكون سياسة ما مهيأة بطريقة خطرة.

### 10) ‏systemd linger ‏(Linux)

إذا كان يعمل كخدمة مستخدم systemd، فإن doctor يضمن تمكين lingering حتى يبقى
Gateway حيًا بعد تسجيل الخروج.

### 11) حالة مساحة العمل (Skills، وplugins، والأدلة القديمة)

يطبع Doctor ملخصًا لحالة مساحة العمل الخاصة بالـ agent الافتراضي:

- **حالة Skills**: يحسب Skills المؤهلة وتلك ذات المتطلبات المفقودة والمحجوبة بقائمة السماح.
- **أدلة مساحة العمل القديمة**: يحذر عند وجود `~/openclaw` أو أدلة مساحة عمل قديمة أخرى
  إلى جانب مساحة العمل الحالية.
- **حالة Plugin**: يحسب الإضافات المحمّلة/المعطلة/التي بها أخطاء؛ ويسرد معرفات plugin عند وجود
  أي أخطاء؛ ويبلغ عن قدرات bundle plugin.
- **تحذيرات توافق plugin**: يعلّم plugins التي تواجه مشكلات توافق مع
  وقت التشغيل الحالي.
- **تشخيصات plugin**: يعرض أي تحذيرات أو أخطاء وقت التحميل تصدرها
  سجلات plugin.

### 11b) حجم ملف التمهيد

يفحص Doctor ما إذا كانت ملفات تمهيد مساحة العمل (مثل `AGENTS.md` أو
`CLAUDE.md` أو غيرها من ملفات السياق المحقونة) قريبة من ميزانية
الأحرف المهيأة أو تجاوزتها. ويبلغ لكل ملف عن عدد الأحرف الخام مقابل المحقونة، ونسبة
الاقتطاع، وسبب الاقتطاع (`max/file` أو `max/total`)، وإجمالي الأحرف
المحقونة كنسبة من الميزانية الإجمالية. وعندما تكون الملفات مقتطعة أو قريبة من
الحد، فإن doctor يطبع نصائح لضبط `agents.defaults.bootstrapMaxChars`
و`agents.defaults.bootstrapTotalMaxChars`.

### 11c) الإكمال الصدفي

يفحص Doctor ما إذا كان الإكمال باستخدام Tab مثبتًا للصدفة الحالية
(zsh أو bash أو fish أو PowerShell):

- إذا كان ملف تعريف الصدفة يستخدم نمط إكمال ديناميكي بطيء
  (`source <(openclaw completion ...)`)، فإن doctor يرقّيه إلى
  صيغة الملف المخبأ الأسرع.
- إذا كان الإكمال مهيأً في الملف التعريفي لكن ملف التخزين المؤقت مفقود،
  فإن doctor يعيد إنشاء التخزين المؤقت تلقائيًا.
- إذا لم يكن هناك أي إكمال مهيأ على الإطلاق، فإن doctor يطلب تثبيته
  (في الوضع التفاعلي فقط؛ ويتم تخطيه مع `--non-interactive`).

شغّل `openclaw completion --write-state` لإعادة إنشاء التخزين المؤقت يدويًا.

### 12) فحوصات مصادقة Gateway (الرمز المحلي)

يفحص Doctor جاهزية مصادقة رمز Gateway المحلي.

- إذا كان وضع الرمز يحتاج إلى رمز ولا يوجد مصدر رمز، فإن doctor يعرض إنشاء واحد.
- إذا كان `gateway.auth.token` مُدارًا بواسطة SecretRef لكنه غير متاح، فإن doctor يحذر ولا يستبدله بنص صريح.
- يفرض `openclaw doctor --generate-gateway-token` الإنشاء فقط عندما لا يكون هناك SecretRef مهيأ للرمز.

### 12b) إصلاحات للقراءة فقط مع مراعاة SecretRef

تحتاج بعض مسارات الإصلاح إلى فحص بيانات الاعتماد المهيأة من دون إضعاف
سلوك الفشل السريع في وقت التشغيل.

- يستخدم `openclaw doctor --fix` الآن نموذج الملخص نفسه الخاص بـ SecretRef للقراءة فقط كما في أوامر عائلة status لإصلاحات إعدادات مستهدفة.
- مثال: يحاول إصلاح `allowFrom` / `groupAllowFrom` `@username` في Telegram استخدام بيانات اعتماد البوت المهيأة عندما تكون متاحة.
- إذا كان رمز Telegram bot مهيأً عبر SecretRef لكنه غير متاح في مسار الأمر الحالي، فإن doctor يبلغ بأن بيانات الاعتماد مهيأة ولكنها غير متاحة ويتخطى الحل التلقائي بدلًا من الانهيار أو الإبلاغ خطأً عن أن الرمز مفقود.

### 13) فحص سلامة Gateway + إعادة التشغيل

يشغّل Doctor فحص سلامة ويعرض إعادة تشغيل Gateway عندما يبدو
غير سليم.

### 13b) جاهزية البحث في الذاكرة

يفحص Doctor ما إذا كان موفّر embedding المهيأ للبحث في الذاكرة جاهزًا
للـ agent الافتراضي. ويعتمد السلوك على backend والموفّر المهيأين:

- **QMD backend**: يفحص ما إذا كان الملف الثنائي `qmd` متاحًا وقابلًا للتشغيل.
  وإذا لم يكن كذلك، يطبع إرشادات إصلاح بما في ذلك حزمة npm وخيار مسار ثنائي يدوي.
- **موفّر محلي صريح**: يفحص وجود ملف نموذج محلي أو عنوان URL معرّف
  لنموذج بعيد/قابل للتنزيل. وإذا كان مفقودًا، يقترح التبديل إلى موفّر بعيد.
- **موفّر بعيد صريح** (`openai` و`voyage` وغيرها): يتحقق من وجود مفتاح API
  في البيئة أو مخزن المصادقة. ويطبع تلميحات إصلاح عملية إذا كان مفقودًا.
- **موفّر تلقائي**: يفحص توفر النموذج المحلي أولًا، ثم يحاول كل موفّر بعيد
  وفق ترتيب الاختيار التلقائي.

وعندما تكون نتيجة فحص Gateway متاحة (كان Gateway سليمًا وقت
الفحص)، فإن doctor يطابق نتيجتها مع الإعدادات المرئية من CLI ويشير
إلى أي اختلاف.

استخدم `openclaw memory status --deep` للتحقق من جاهزية embedding وقت التشغيل.

### 14) تحذيرات حالة القنوات

إذا كان Gateway سليمًا، فإن doctor يشغّل فحص حالة القنوات ويبلغ
عن التحذيرات مع الإصلاحات المقترحة.

### 15) تدقيق إعدادات supervisor + الإصلاح

يفحص Doctor إعدادات supervisor المثبّتة (launchd/systemd/schtasks) لاكتشاف
الافتراضيات المفقودة أو القديمة (مثل تبعيات systemd للشبكة عند الاتصال و
تأخير إعادة التشغيل). وعندما يجد عدم تطابق، فإنه يوصي بالتحديث ويمكنه
إعادة كتابة ملف الخدمة/المهمة إلى الافتراضيات الحالية.

ملاحظات:

- يطلب `openclaw doctor` تأكيدًا قبل إعادة كتابة إعدادات supervisor.
- يقبل `openclaw doctor --yes` مطالبات الإصلاح الافتراضية.
- يطبّق `openclaw doctor --repair` الإصلاحات الموصى بها من دون مطالبات.
- يقوم `openclaw doctor --repair --force` باستبدال إعدادات supervisor المخصصة.
- إذا كانت مصادقة الرمز تتطلب رمزًا وكان `gateway.auth.token` مُدارًا بواسطة SecretRef، فإن تثبيت/إصلاح خدمة doctor يتحقق من SecretRef لكنه لا يحفظ قيم الرمز النصية الصريحة المحلولة في بيانات بيئة خدمة supervisor.
- إذا كانت مصادقة الرمز تتطلب رمزًا وكان SecretRef المهيأ للرمز غير محلول، فإن doctor يمنع مسار التثبيت/الإصلاح مع إرشادات عملية.
- إذا كان كل من `gateway.auth.token` و`gateway.auth.password` مهيأين وكان `gateway.auth.mode` غير مضبوط، فإن doctor يمنع التثبيت/الإصلاح حتى يتم ضبط الوضع صراحةً.
- بالنسبة إلى وحدات systemd الخاصة بمستخدمي Linux، تشمل فحوصات انجراف الرمز في doctor الآن كلا المصدرين `Environment=` و`EnvironmentFile=` عند مقارنة بيانات مصادقة الخدمة.
- يمكنك دائمًا فرض إعادة كتابة كاملة عبر `openclaw gateway install --force`.

### 16) تشخيصات وقت تشغيل Gateway + المنفذ

يفحص Doctor وقت تشغيل الخدمة (PID، وآخر حالة خروج) ويحذر عندما تكون
الخدمة مثبتة لكنها لا تعمل فعليًا. كما يفحص تعارضات
المنفذ على منفذ Gateway (الافتراضي `18789`) ويبلغ عن الأسباب المحتملة (Gateway يعمل بالفعل،
أو نفق SSH).

### 17) أفضل ممارسات وقت تشغيل Gateway

يحذر Doctor عندما تعمل خدمة Gateway على Bun أو على مسار Node مُدار بالإصدارات
(`nvm` أو `fnm` أو `volta` أو `asdf` وغيرها). تتطلب قنوات WhatsApp + Telegram
Node، وقد تتعطل مسارات مديري الإصدارات بعد الترقيات لأن الخدمة لا
تحمّل تهيئة الصدفة لديك. ويعرض doctor الترحيل إلى تثبيت Node نظامي عندما
يكون متاحًا (Homebrew/apt/choco).

### 18) كتابة الإعدادات + بيانات تعريف المعالج

يحفظ Doctor أي تغييرات في الإعدادات ويضع بيانات تعريف المعالج لتسجيل
تشغيل doctor.

### 19) نصائح مساحة العمل (النسخ الاحتياطي + نظام الذاكرة)

يقترح Doctor نظام ذاكرة لمساحة العمل عند غيابه ويطبع نصيحة للنسخ الاحتياطي
إذا لم تكن مساحة العمل تحت git بالفعل.

راجع [/concepts/agent-workspace](/ar/concepts/agent-workspace) للحصول على دليل كامل إلى
بنية مساحة العمل والنسخ الاحتياطي عبر git (يُوصى باستخدام GitHub أو GitLab خاص).
