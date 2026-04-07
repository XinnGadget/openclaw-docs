---
read_when:
    - عند إضافة ترحيلات doctor أو تعديلها
    - عند تقديم تغييرات كاسرة في الإعدادات
summary: 'أمر Doctor: فحوصات السلامة، وترحيلات الإعدادات، وخطوات الإصلاح'
title: Doctor
x-i18n:
    generated_at: "2026-04-07T07:18:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: a834dc7aec79c20d17bc23d37fb5f5e99e628d964d55bd8cf24525a7ee57130c
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

اقبل القيم الافتراضية من دون طلب تأكيد (بما في ذلك خطوات إصلاح إعادة التشغيل/الخدمة/sandbox عند الاقتضاء).

```bash
openclaw doctor --repair
```

طبّق الإصلاحات الموصى بها من دون طلب تأكيد (الإصلاحات + إعادة التشغيل حيثما كان ذلك آمنًا).

```bash
openclaw doctor --repair --force
```

طبّق أيضًا الإصلاحات المتقدمة (يكتب فوق إعدادات المشرف المخصصة).

```bash
openclaw doctor --non-interactive
```

شغّل بدون مطالبات وطبّق فقط الترحيلات الآمنة (تطبيع الإعدادات + نقل الحالة على القرص). ويتخطى إجراءات إعادة التشغيل/الخدمة/sandbox التي تتطلب تأكيدًا بشريًا.
تعمل ترحيلات الحالة القديمة تلقائيًا عند اكتشافها.

```bash
openclaw doctor --deep
```

افحص خدمات النظام بحثًا عن تثبيتات Gateway إضافية (launchd/systemd/schtasks).

إذا كنت تريد مراجعة التغييرات قبل الكتابة، فافتح ملف الإعدادات أولًا:

```bash
cat ~/.openclaw/openclaw.json
```

## ما الذي يفعله (ملخص)

- تحديث اختياري قبل التشغيل لتثبيتات git (في الوضع التفاعلي فقط).
- فحص حداثة بروتوكول واجهة المستخدم (ويعيد بناء Control UI عندما يكون مخطط البروتوكول أحدث).
- فحص السلامة + مطالبة بإعادة التشغيل.
- ملخص حالة Skills ‏(المؤهلة/المفقودة/المحجوبة) وحالة plugin.
- تطبيع الإعدادات للقيم القديمة.
- ترحيل إعدادات Talk من حقول `talk.*` القديمة المسطحة إلى `talk.provider` + `talk.providers.<provider>`.
- فحوصات ترحيل المتصفح لإعدادات إضافات Chrome القديمة وجاهزية Chrome MCP.
- تحذيرات تجاوز مزود OpenCode (`models.providers.opencode` / `models.providers.opencode-go`).
- فحص متطلبات OAuth TLS الأساسية لملفات تعريف OpenAI Codex OAuth.
- ترحيل الحالة القديمة على القرص (الجلسات/دليل الوكيل/مصادقة WhatsApp).
- ترحيل مفتاح عقد manifest القديم لـ plugin (`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`).
- ترحيل مخزن cron القديم (`jobId`, `schedule.cron`, حقول delivery/payload ذات المستوى الأعلى، و`provider` في payload، ووظائف webhook الاحتياطية البسيطة `notify: true`).
- فحص ملفات قفل الجلسة وتنظيف الأقفال القديمة.
- فحوصات سلامة الحالة والأذونات (الجلسات، transcripts، دليل الحالة).
- فحوصات أذونات ملف الإعدادات (chmod 600) عند التشغيل محليًا.
- سلامة مصادقة النماذج: يفحص انتهاء صلاحية OAuth، ويمكنه تحديث الرموز التي توشك على الانتهاء، ويعرض حالات التهدئة/التعطيل لملفات تعريف المصادقة.
- اكتشاف دليل workspace إضافي (`~/openclaw`).
- إصلاح صورة sandbox عند تفعيل sandboxing.
- ترحيل الخدمة القديمة واكتشاف Gateway إضافي.
- ترحيل الحالة القديمة لقناة Matrix (في وضع `--fix` / `--repair`).
- فحوصات وقت تشغيل Gateway (الخدمة مثبتة ولكنها لا تعمل؛ ووسم launchd مخزن مؤقتًا).
- تحذيرات حالة القنوات (يتم فحصها من Gateway العامل).
- تدقيق إعدادات المشرف (launchd/systemd/schtasks) مع إصلاح اختياري.
- فحوصات أفضل الممارسات لوقت تشغيل Gateway ‏(Node مقابل Bun، ومسارات مديري الإصدارات).
- تشخيص تعارض منفذ Gateway ‏(الافتراضي `18789`).
- تحذيرات أمنية لسياسات DM المفتوحة.
- فحوصات مصادقة Gateway لوضع الرمز المحلي (يوفر إنشاء رمز عند عدم وجود مصدر رمز؛ ولا يكتب فوق إعدادات token SecretRef).
- فحص systemd linger على Linux.
- فحص حجم ملف bootstrap في workspace (تحذيرات الاقتطاع/الاقتراب من الحد لملفات السياق).
- فحص حالة shell completion والتثبيت/الترقية التلقائيين.
- فحص جاهزية مزود embedding الخاص ببحث الذاكرة (نموذج محلي، أو مفتاح API بعيد، أو ملف QMD تنفيذي).
- فحوصات تثبيت المصدر (عدم تطابق pnpm workspace، وغياب أصول UI، وغياب ملف tsx التنفيذي).
- يكتب الإعدادات المحدَّثة + بيانات wizard الوصفية.

## السلوك المفصل والمبررات

### 0) تحديث اختياري (تثبيتات git)

إذا كان هذا مستودع git checkout وكان doctor يعمل في الوضع التفاعلي، فسيعرض
التحديث (fetch/rebase/build) قبل تشغيل doctor.

### 1) تطبيع الإعدادات

إذا احتوت الإعدادات على أشكال قيم قديمة (على سبيل المثال `messages.ackReaction`
من دون تجاوز خاص بالقناة)، يقوم doctor بتطبيعها إلى
المخطط الحالي.

ويشمل ذلك حقول Talk القديمة المسطحة. إعدادات Talk العامة الحالية هي
`talk.provider` + `talk.providers.<provider>`. ويعيد doctor كتابة
أشكال `talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` القديمة إلى خريطة المزود.

### 2) ترحيلات مفاتيح الإعدادات القديمة

عندما تحتوي الإعدادات على مفاتيح مهجورة، ترفض الأوامر الأخرى التشغيل وتطلب
منك تشغيل `openclaw doctor`.

سيقوم Doctor بما يلي:

- شرح مفاتيح الإعدادات القديمة التي تم العثور عليها.
- عرض الترحيل الذي طبقه.
- إعادة كتابة `~/.openclaw/openclaw.json` بالمخطط المحدّث.

كما يشغّل Gateway ترحيلات doctor تلقائيًا عند بدء التشغيل عندما يكتشف
تنسيق إعدادات قديمًا، بحيث يتم إصلاح الإعدادات القديمة بدون تدخل يدوي.
تتم معالجة ترحيلات مخزن وظائف Cron بواسطة `openclaw doctor --fix`.

الترحيلات الحالية:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → `bindings` في المستوى الأعلى
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` القديمة → `talk.provider` + `talk.providers.<provider>`
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
- بالنسبة إلى القنوات التي تحتوي على `accounts` مسماة مع بقاء قيم قناة ذات مستوى أعلى مخصصة لحساب واحد، انقل تلك القيم ذات النطاق الخاص بالحساب إلى الحساب المُرقّى المختار لتلك القناة (`accounts.default` لمعظم القنوات؛ ويمكن لـ Matrix الحفاظ على هدف مسمى/افتراضي موجود ومطابق)
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` ‏(tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- إزالة `browser.relayBindHost` (إعداد relay قديم للإضافة)

تتضمن تحذيرات Doctor أيضًا إرشادات حول الحساب الافتراضي للقنوات متعددة الحسابات:

- إذا تم ضبط إدخالين أو أكثر ضمن `channels.<channel>.accounts` بدون `channels.<channel>.defaultAccount` أو `accounts.default`، فسيحذر doctor من أن توجيه fallback قد يختار حسابًا غير متوقع.
- إذا تم ضبط `channels.<channel>.defaultAccount` على معرّف حساب غير معروف، فسيحذر doctor ويعرض معرّفات الحسابات المضبوطة.

### 2b) تجاوزات مزود OpenCode

إذا كنت قد أضفت `models.providers.opencode` أو `opencode-zen` أو `opencode-go`
يدويًا، فإنه يتجاوز كتالوج OpenCode المضمّن من `@mariozechner/pi-ai`.
وقد يؤدي ذلك إلى فرض النماذج على API غير صحيح أو تصفير التكاليف. يحذّر doctor حتى
تتمكن من إزالة التجاوز واستعادة توجيه API والتكاليف لكل نموذج.

### 2c) ترحيل المتصفح وجاهزية Chrome MCP

إذا كانت إعدادات متصفحك لا تزال تشير إلى مسار إضافة Chrome الذي تمت إزالته، فإن doctor
يقوم بتطبيعها إلى نموذج الإرفاق الحالي لـ Chrome MCP المحلي على المضيف:

- `browser.profiles.*.driver: "extension"` تصبح `"existing-session"`
- تتم إزالة `browser.relayBindHost`

كما يدقّق doctor في مسار Chrome MCP المحلي على المضيف عندما تستخدم `defaultProfile:
"user"` أو ملف تعريف `existing-session` مضبوط:

- يفحص ما إذا كان Google Chrome مثبتًا على نفس المضيف لملفات التعريف
  ذات الاتصال التلقائي الافتراضي
- يفحص إصدار Chrome المكتشف ويحذر إذا كان أقل من Chrome 144
- يذكّرك بتمكين remote debugging في صفحة inspect الخاصة بالمتصفح (على
  سبيل المثال `chrome://inspect/#remote-debugging` أو `brave://inspect/#remote-debugging`
  أو `edge://inspect/#remote-debugging`)

لا يستطيع doctor تمكين الإعداد في Chrome نيابةً عنك. لا يزال Chrome MCP المحلي على المضيف
يتطلب:

- متصفحًا قائمًا على Chromium بإصدار 144+ على مضيف gateway/node
- تشغيل المتصفح محليًا
- تمكين remote debugging في ذلك المتصفح
- الموافقة على مطالبة الإذن الأولى بالإرفاق في المتصفح

الجاهزية هنا تتعلق فقط بمتطلبات الإرفاق المحلي. يحتفظ existing-session
بقيود مسار Chrome MCP الحالية؛ أما المسارات المتقدمة مثل `responsebody` وتصدير PDF
واعتراض التنزيلات والإجراءات المجمعة فما تزال تتطلب
متصفحًا مُدارًا أو ملف تعريف CDP خام.

لا ينطبق هذا الفحص على تدفقات Docker أو sandbox أو remote-browser أو غيرها من
التدفقات بدون واجهة. إذ تواصل تلك استخدام CDP الخام.

### 2d) متطلبات OAuth TLS الأساسية

عندما يتم ضبط ملف تعريف OpenAI Codex OAuth، يقوم doctor بفحص نقطة
تفويض OpenAI للتحقق من أن مكدس TLS المحلي في Node/OpenSSL يمكنه
التحقق من سلسلة الشهادات. إذا فشل الفحص بخطأ في الشهادة (على
سبيل المثال `UNABLE_TO_GET_ISSUER_CERT_LOCALLY` أو شهادة منتهية أو شهادة موقعة ذاتيًا)،
فسيعرض doctor إرشادات إصلاح خاصة بالمنصة. على macOS مع Node من Homebrew،
يكون الإصلاح عادةً `brew postinstall ca-certificates`. ومع `--deep`، يُشغَّل الفحص
حتى لو كانت حالة Gateway سليمة.

### 3) ترحيلات الحالة القديمة (تخطيط القرص)

يمكن لـ Doctor ترحيل تخطيطات القرص القديمة إلى البنية الحالية:

- مخزن الجلسات + transcripts:
  - من `~/.openclaw/sessions/` إلى `~/.openclaw/agents/<agentId>/sessions/`
- دليل الوكيل:
  - من `~/.openclaw/agent/` إلى `~/.openclaw/agents/<agentId>/agent/`
- حالة مصادقة WhatsApp ‏(Baileys):
  - من `~/.openclaw/credentials/*.json` القديمة (باستثناء `oauth.json`)
  - إلى `~/.openclaw/credentials/whatsapp/<accountId>/...` (معرّف الحساب الافتراضي: `default`)

هذه الترحيلات تُنفَّذ بأفضل جهد وهي idempotent؛ وسيصدر doctor تحذيرات عندما
يترك أي مجلدات قديمة كنسخ احتياطية. كما يقوم Gateway/CLI بترحيل
الجلسات القديمة + دليل الوكيل تلقائيًا عند بدء التشغيل لكي تنتقل
السجلات/المصادقة/النماذج إلى مسار كل وكيل من دون تشغيل doctor يدويًا. أما مصادقة WhatsApp
فيتم ترحيلها عمدًا فقط عبر `openclaw doctor`. كما أن تطبيع provider/provider-map لـ Talk
يقارن الآن بالمساواة البنيوية، لذلك لم تعد الفروقات الناتجة فقط عن ترتيب المفاتيح
تسبب تغييرات `doctor --fix` متكررة عديمة الأثر.

### 3a) ترحيلات manifest القديمة لـ plugin

يفحص Doctor جميع manifest الخاصة بالـ plugin المثبتة بحثًا عن مفاتيح
الإمكانات القديمة ذات المستوى الأعلى (`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`). وعند العثور عليها، يعرض نقلها إلى الكائن `contracts`
وإعادة كتابة ملف manifest في مكانه. هذا الترحيل idempotent؛
وإذا كان المفتاح `contracts` يحتوي بالفعل على القيم نفسها، تتم إزالة
المفتاح القديم من دون تكرار البيانات.

### 3b) ترحيلات مخزن cron القديمة

يفحص Doctor أيضًا مخزن وظائف cron ‏(`~/.openclaw/cron/jobs.json` افتراضيًا،
أو `cron.store` عند التجاوز) بحثًا عن أشكال وظائف قديمة ما يزال المجدول
يقبلها للتوافق.

تتضمن عمليات تنظيف cron الحالية:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- حقول payload ذات المستوى الأعلى (`message`, `model`, `thinking`, ...) → `payload`
- حقول delivery ذات المستوى الأعلى (`deliver`, `channel`, `to`, `provider`, ...) → `delivery`
- الأسماء البديلة للتسليم `provider` في payload → `delivery.channel` صريح
- وظائف webhook الاحتياطية القديمة البسيطة `notify: true` → `delivery.mode="webhook"` صريح مع `delivery.to=cron.webhook`

لا يرحّل Doctor تلقائيًا وظائف `notify: true` إلا عندما يتمكن من ذلك
من دون تغيير السلوك. وإذا جمعت وظيفة ما بين fallback notify قديم ووضع
delivery موجود ليس webhook، فسيحذر doctor ويترك تلك الوظيفة للمراجعة اليدوية.

### 3c) تنظيف قفل الجلسة

يفحص Doctor كل دليل جلسات وكلاء بحثًا عن ملفات write-lock قديمة — وهي ملفات
تُترك خلفها عندما تنتهي الجلسة بشكل غير طبيعي. ولكل ملف قفل يعثر عليه، يعرض:
المسار وPID وما إذا كان PID ما يزال حيًا وعمر القفل وما إذا كان
يُعتبر قديمًا (PID ميت أو أقدم من 30 دقيقة). في وضع `--fix` / `--repair`
يقوم بإزالة ملفات القفل القديمة تلقائيًا؛ وإلا فإنه يطبع ملاحظة
ويطلب منك إعادة التشغيل باستخدام `--fix`.

### 4) فحوصات سلامة الحالة (استمرارية الجلسة، والتوجيه، والسلامة)

يُعد دليل الحالة بمثابة جذع الدماغ التشغيلي. فإذا اختفى، ستفقد
الجلسات وبيانات الاعتماد والسجلات والإعدادات (ما لم تكن لديك نسخ احتياطية في مكان آخر).

يفحص Doctor ما يلي:

- **دليل الحالة مفقود**: يحذر من فقدان الحالة الكارثي، ويطلب إعادة إنشاء
  الدليل، ويذكّرك بأنه لا يستطيع استعادة البيانات المفقودة.
- **أذونات دليل الحالة**: يتحقق من قابلية الكتابة؛ ويعرض إصلاح الأذونات
  (ويصدر تلميح `chown` عند اكتشاف عدم تطابق المالك/المجموعة).
- **دليل حالة macOS المتزامن سحابيًا**: يحذر عندما تُحل الحالة تحت iCloud Drive
  (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) أو
  `~/Library/CloudStorage/...` لأن المسارات المدعومة بالمزامنة قد تسبب إدخال/إخراج أبطأ
  وسباقات قفل/مزامنة.
- **دليل حالة Linux على SD أو eMMC**: يحذر عندما تُحل الحالة إلى
  مصدر تركيب `mmcblk*`، لأن الإدخال/الإخراج العشوائي المدعوم بـ SD أو eMMC قد يكون أبطأ
  ويتسبب في اهتراء أسرع مع كتابات الجلسات وبيانات الاعتماد.
- **أدلة الجلسات مفقودة**: مطلوب وجود `sessions/` ودليل مخزن الجلسة من
  أجل حفظ السجل وتجنب أعطال `ENOENT`.
- **عدم تطابق transcript**: يحذر عندما تحتوي إدخالات الجلسات الحديثة على
  ملفات transcript مفقودة.
- **main session “1-line JSONL”**: يضع علامة عند احتواء transcript الرئيسي على سطر واحد فقط
  (السجل لا يتراكم).
- **أدلة حالة متعددة**: يحذر عند وجود عدة مجلدات `~/.openclaw` عبر
  أدلة home أو عندما يشير `OPENCLAW_STATE_DIR` إلى مكان آخر (قد ينقسم السجل بين التثبيتات).
- **تذكير الوضع البعيد**: إذا كان `gateway.mode=remote`، يذكّرك doctor بتشغيله
  على المضيف البعيد (فالحالة موجودة هناك).
- **أذونات ملف الإعدادات**: يحذر إذا كان `~/.openclaw/openclaw.json`
  قابلاً للقراءة من قبل المجموعة/العالم ويعرض تشديده إلى `600`.

### 5) سلامة مصادقة النماذج (انتهاء OAuth)

يفحص Doctor ملفات تعريف OAuth في مخزن المصادقة، ويحذر عندما تكون
الرموز على وشك الانتهاء/منتهية، ويمكنه تحديثها عندما يكون ذلك آمنًا. وإذا كان ملف
تعريف Anthropic OAuth/token قديمًا، فإنه يقترح مفتاح Anthropic API أو
مسار setup-token الخاص بـ Anthropic.
لا تظهر مطالبات التحديث إلا عند التشغيل تفاعليًا (TTY)؛ أما `--non-interactive`
فيتخطى محاولات التحديث.

كما يعرض Doctor أيضًا ملفات تعريف المصادقة غير القابلة للاستخدام مؤقتًا بسبب:

- فترات تهدئة قصيرة (حدود المعدل/انقضاء المهلة/فشل المصادقة)
- تعطيلات أطول (فشل الفوترة/الرصيد)

### 6) التحقق من نموذج Hooks

إذا كان `hooks.gmail.model` مضبوطًا، فإن doctor يتحقق من مرجع النموذج مقابل
الكتالوج وقائمة السماح ويحذر عندما يتعذر حله أو لا يُسمح به.

### 7) إصلاح صورة sandbox

عند تفعيل sandboxing، يفحص doctor صور Docker ويعرض بناءها أو
التبديل إلى الأسماء القديمة إذا كانت الصورة الحالية مفقودة.

### 7b) تبعيات وقت التشغيل للـ plugin المضمّنة

يتحقق Doctor من وجود تبعيات وقت التشغيل للـ plugin المضمّنة (على سبيل المثال
حزم وقت تشغيل plugin الخاصة بـ Discord) في جذر تثبيت OpenClaw.
إذا كان أي منها مفقودًا، فسيبلغ doctor عن الحزم ويثبتها في
وضع `openclaw doctor --fix` / `openclaw doctor --repair`.

### 8) ترحيلات خدمة Gateway وتلميحات التنظيف

يكتشف Doctor خدمات Gateway القديمة (launchd/systemd/schtasks) و
يعرض إزالتها وتثبيت خدمة OpenClaw باستخدام منفذ gateway الحالي.
كما يمكنه أيضًا فحص الخدمات الإضافية الشبيهة بـ gateway وطباعة تلميحات للتنظيف.
تُعد خدمات OpenClaw gateway المسماة باسم ملف التعريف خدمات من الدرجة الأولى ولا
يتم وضع علامة "إضافية" عليها.

### 8b) ترحيل Matrix عند بدء التشغيل

عندما يكون لدى حساب قناة Matrix ترحيل حالة قديم معلّق أو قابل للتنفيذ،
فإن doctor (في وضع `--fix` / `--repair`) ينشئ لقطة قبل الترحيل ثم
يشغّل خطوات الترحيل بأفضل جهد: ترحيل حالة Matrix القديمة وإعداد
الحالة المشفرة القديمة. كلتا الخطوتين غير قاتلتين؛ يتم تسجيل الأخطاء
ويستمر بدء التشغيل. أما في وضع القراءة فقط (`openclaw doctor` بدون `--fix`) فسيتم
تخطي هذا الفحص بالكامل.

### 9) التحذيرات الأمنية

يصدر Doctor تحذيرات عندما يكون أحد الموفرين مفتوحًا على الرسائل الخاصة DM بدون قائمة سماح، أو
عندما تكون إحدى السياسات مضبوطة بطريقة خطرة.

### 10) systemd linger ‏(Linux)

إذا كان يعمل كخدمة مستخدم systemd، يتأكد doctor من تفعيل lingering حتى
يبقى gateway يعمل بعد تسجيل الخروج.

### 11) حالة workspace ‏(Skills وplugins والأدلة القديمة)

يطبع Doctor ملخصًا لحالة workspace للوكيل الافتراضي:

- **حالة Skills**: عدد Skills المؤهلة، وذات المتطلبات المفقودة، والمحجوبة بقائمة السماح.
- **أدلة workspace القديمة**: يحذر عند وجود `~/openclaw` أو أدلة workspace قديمة أخرى
  إلى جانب workspace الحالية.
- **حالة plugin**: عدد plugins المحملة/المعطلة/التي بها أخطاء؛ ويسرد معرّفات plugin لأي
  أخطاء؛ ويعرض إمكانات bundle plugin.
- **تحذيرات توافق plugin**: يضع علامة على plugins التي لديها مشكلات توافق مع
  وقت التشغيل الحالي.
- **تشخيصات plugin**: يعرض أي تحذيرات أو أخطاء وقت التحميل صادرة عن
  plugin registry.

### 11b) حجم ملف Bootstrap

يفحص Doctor ما إذا كانت ملفات bootstrap الخاصة بـ workspace (على سبيل المثال `AGENTS.md`،
أو `CLAUDE.md`، أو ملفات سياق أخرى يتم حقنها) قريبة من
الميزانية المكوّنة للأحرف أو تتجاوزها. ويعرض لكل ملف عدد الأحرف الخام مقابل المحقونة، ونسبة
الاقتطاع، وسبب الاقتطاع (`max/file` أو `max/total`)، وإجمالي الأحرف
المحقونة كنسبة من إجمالي الميزانية. وعندما يتم اقتطاع الملفات أو تكون قريبة من
الحد، يطبع doctor نصائح لضبط `agents.defaults.bootstrapMaxChars`
و`agents.defaults.bootstrapTotalMaxChars`.

### 11c) Shell completion

يفحص Doctor ما إذا كان tab completion مثبتًا للـ shell الحالي
(zsh أو bash أو fish أو PowerShell):

- إذا كان ملف تعريف shell يستخدم نمط completion ديناميكيًا بطيئًا
  (`source <(openclaw completion ...)`)، فإن doctor يرقّيه إلى
  متغير الملف المخزن مؤقتًا والأسرع.
- إذا كان completion مضبوطًا في ملف التعريف لكن ملف cache مفقودًا،
  فإن doctor يعيد إنشاء cache تلقائيًا.
- إذا لم يكن completion مضبوطًا على الإطلاق، فسيعرض doctor تثبيته
  (في الوضع التفاعلي فقط؛ ويتم التخطي مع `--non-interactive`).

شغّل `openclaw completion --write-state` لإعادة إنشاء cache يدويًا.

### 12) فحوصات مصادقة Gateway ‏(الرمز المحلي)

يفحص Doctor جاهزية مصادقة رمز gateway المحلي.

- إذا كان وضع الرمز يحتاج إلى رمز ولا يوجد مصدر له، فسيعرض doctor إنشاء واحد.
- إذا كان `gateway.auth.token` مُدارًا بواسطة SecretRef ولكنه غير متاح، فسيحذر doctor ولن يكتب فوقه بنص صريح.
- يفرض `openclaw doctor --generate-gateway-token` الإنشاء فقط عند عدم ضبط أي token SecretRef.

### 12b) إصلاحات واعية بـ SecretRef للقراءة فقط

تحتاج بعض تدفقات الإصلاح إلى فحص بيانات الاعتماد المضبوطة دون إضعاف
سلوك الفشل السريع في وقت التشغيل.

- يستخدم `openclaw doctor --fix` الآن نموذج ملخص SecretRef نفسه للقراءة فقط كما في أوامر عائلة الحالة لإصلاحات الإعدادات المستهدفة.
- مثال: يحاول إصلاح `allowFrom` / `groupAllowFrom` `@username` في Telegram استخدام بيانات اعتماد البوت المضبوطة عندما تكون متاحة.
- إذا كان رمز Telegram bot مضبوطًا عبر SecretRef لكنه غير متاح في مسار الأمر الحالي، فإن doctor يبلغ أن بيانات الاعتماد مضبوطة لكنها غير متاحة، ويتخطى الحل التلقائي بدلًا من التعطل أو الإبلاغ خطأً عن أن الرمز مفقود.

### 13) فحص سلامة Gateway + إعادة التشغيل

يشغّل Doctor فحص سلامة ويعرض إعادة تشغيل gateway عندما يبدو
غير سليم.

### 13b) جاهزية بحث الذاكرة

يفحص Doctor ما إذا كان مزود embedding المضبوط لبحث الذاكرة جاهزًا
للوكيل الافتراضي. ويعتمد السلوك على backend والمزود المضبوطين:

- **QMD backend**: يفحص ما إذا كان الملف التنفيذي `qmd` متاحًا وقابلًا للتشغيل.
  وإذا لم يكن كذلك، يطبع إرشادات الإصلاح بما في ذلك حزمة npm وخيار مسار binary يدوي.
- **مزود محلي صريح**: يفحص وجود ملف نموذج محلي أو عنوان URL
  معرَّف لنموذج بعيد/قابل للتنزيل. وإذا كان مفقودًا، يقترح التحويل إلى مزود بعيد.
- **مزود بعيد صريح** (`openai`, `voyage`، إلخ): يتحقق من وجود مفتاح API
  في البيئة أو في مخزن المصادقة. ويطبع تلميحات إصلاح عملية إذا كان مفقودًا.
- **مزود تلقائي**: يفحص توفر النموذج المحلي أولًا، ثم يجرب كل مزود بعيد
  بترتيب الاختيار التلقائي.

عندما تكون نتيجة فحص gateway متاحة (كانت حالة gateway سليمة وقت
الفحص)، فإن doctor يربط نتيجتها مع الإعدادات المرئية من CLI ويشير
إلى أي اختلاف.

استخدم `openclaw memory status --deep` للتحقق من جاهزية embedding في وقت التشغيل.

### 14) تحذيرات حالة القنوات

إذا كانت حالة gateway سليمة، فسيجري doctor فحصًا لحالة القنوات ويعرض
تحذيرات مع إصلاحات مقترحة.

### 15) تدقيق إعدادات المشرف + الإصلاح

يفحص Doctor إعدادات المشرف المثبتة (launchd/systemd/schtasks) بحثًا عن
القيم الافتراضية المفقودة أو القديمة (مثل تبعيات systemd network-online و
تأخير إعادة التشغيل). وعندما يجد عدم تطابق، فإنه يوصي بالتحديث ويمكنه
إعادة كتابة ملف الخدمة/المهمة إلى القيم الافتراضية الحالية.

ملاحظات:

- يطلب `openclaw doctor` التأكيد قبل إعادة كتابة إعدادات المشرف.
- يقبل `openclaw doctor --yes` مطالبات الإصلاح الافتراضية.
- يطبّق `openclaw doctor --repair` الإصلاحات الموصى بها من دون مطالبات.
- يكتب `openclaw doctor --repair --force` فوق إعدادات المشرف المخصصة.
- إذا كانت مصادقة الرمز تتطلب رمزًا وكان `gateway.auth.token` مُدارًا بواسطة SecretRef، فإن تثبيت/إصلاح خدمة doctor يتحقق من SecretRef لكنه لا يحفظ قيم الرمز النصية الصريحة التي تم حلها في بيانات بيئة خدمة المشرف الوصفية.
- إذا كانت مصادقة الرمز تتطلب رمزًا وكان token SecretRef المضبوط غير محلول، فإن doctor يمنع مسار التثبيت/الإصلاح مع إرشادات عملية.
- إذا تم ضبط كل من `gateway.auth.token` و`gateway.auth.password` وكان `gateway.auth.mode` غير مضبوط، فإن doctor يمنع التثبيت/الإصلاح حتى يتم ضبط الوضع صراحةً.
- بالنسبة إلى وحدات Linux user-systemd، تتضمن فحوصات انجراف الرمز في doctor الآن كلاً من مصدري `Environment=` و`EnvironmentFile=` عند مقارنة بيانات مصادقة الخدمة الوصفية.
- يمكنك دائمًا فرض إعادة كتابة كاملة عبر `openclaw gateway install --force`.

### 16) تشخيصات وقت تشغيل Gateway + المنفذ

يفحص Doctor وقت تشغيل الخدمة (PID، وآخر حالة خروج) ويحذر عندما تكون
الخدمة مثبتة لكنها لا تعمل فعليًا. كما يفحص تعارضات المنافذ
على منفذ gateway ‏(الافتراضي `18789`) ويعرض الأسباب المحتملة (gateway يعمل بالفعل،
أو نفق SSH).

### 17) أفضل ممارسات وقت تشغيل Gateway

يحذر Doctor عندما تعمل خدمة gateway على Bun أو على مسار Node مُدار بإدارة الإصدارات
(`nvm`, `fnm`, `volta`, `asdf`، إلخ). تتطلب قنوات WhatsApp + Telegram وجود Node،
كما يمكن أن تتعطل مسارات مديري الإصدارات بعد الترقيات لأن الخدمة لا
تحمّل تهيئة shell الخاصة بك. يعرض doctor الترحيل إلى تثبيت Node على مستوى النظام عندما
يكون متاحًا (Homebrew/apt/choco).

### 18) كتابة الإعدادات + بيانات wizard الوصفية

يحفظ Doctor أي تغييرات في الإعدادات ويضع ختمًا على بيانات wizard الوصفية لتسجيل
تشغيل doctor.

### 19) نصائح workspace ‏(النسخ الاحتياطي + نظام الذاكرة)

يقترح Doctor نظام ذاكرة للـ workspace عند غيابه ويطبع تلميحًا للنسخ الاحتياطي
إذا لم تكن workspace تحت git بالفعل.

راجع [/concepts/agent-workspace](/ar/concepts/agent-workspace) للحصول على دليل كامل
لبنية workspace والنسخ الاحتياطي باستخدام git (يُوصى باستخدام GitHub أو GitLab خاص).
