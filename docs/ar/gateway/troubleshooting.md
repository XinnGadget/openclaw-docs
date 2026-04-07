---
read_when:
    - أحالَك مركز استكشاف الأخطاء وإصلاحها إلى هنا للحصول على تشخيص أعمق
    - تحتاج إلى أقسام دليل تشغيل مستقرة قائمة على الأعراض مع أوامر دقيقة
summary: دليل متعمق لاستكشاف الأخطاء وإصلاحها للـ gateway، والقنوات، والأتمتة، والعُقد، والمتصفح
title: استكشاف الأخطاء وإصلاحها
x-i18n:
    generated_at: "2026-04-07T07:18:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0202e8858310a0bfc1c994cd37b01c3b2d6c73c8a74740094e92dc3c4c36729
    source_path: gateway/troubleshooting.md
    workflow: 15
---

# استكشاف أخطاء Gateway وإصلاحها

هذه الصفحة هي دليل التشغيل المتعمق.
ابدأ من [/help/troubleshooting](/ar/help/troubleshooting) إذا كنت تريد أولًا مسار الفرز السريع.

## تسلسل الأوامر

شغّل هذه الأوامر أولًا، بهذا الترتيب:

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

الإشارات المتوقعة للحالة السليمة:

- يعرض `openclaw gateway status` القيمتين `Runtime: running` و`RPC probe: ok`.
- يُبلغ `openclaw doctor` بعدم وجود مشكلات حظر في الإعداد/الخدمة.
- يعرض `openclaw channels status --probe` حالة النقل المباشر لكل حساب، ونتائج
  الفحص/التدقيق عند الدعم، مثل `works` أو `audit ok`.

## يتطلب Anthropic 429 استخدامًا إضافيًا للسياق الطويل

استخدم هذا القسم عندما تتضمن السجلات/الأخطاء:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

ابحث عن:

- أن نموذج Anthropic Opus/Sonnet المحدد يحتوي على `params.context1m: true`.
- أن بيانات اعتماد Anthropic الحالية غير مؤهلة لاستخدام السياق الطويل.
- أن الطلبات تفشل فقط في الجلسات الطويلة/تشغيلات النماذج التي تحتاج إلى مسار 1M التجريبي.

خيارات الإصلاح:

1. عطّل `context1m` لهذا النموذج للعودة إلى نافذة السياق العادية.
2. استخدم بيانات اعتماد Anthropic مؤهلة لطلبات السياق الطويل، أو بدّل إلى Anthropic API key.
3. اضبط نماذج احتياطية حتى تستمر التشغيلات عند رفض طلبات Anthropic للسياق الطويل.

ذو صلة:

- [/providers/anthropic](/ar/providers/anthropic)
- [/reference/token-use](/ar/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/ar/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## لا توجد ردود

إذا كانت القنوات تعمل لكن لا يوجد أي رد، فتحقق من التوجيه والسياسة قبل إعادة توصيل أي شيء.

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

ابحث عن:

- اقتران معلّق لمرسلي الرسائل المباشرة.
- تقييد الإشارة في المجموعات (`requireMention`، `mentionPatterns`).
- عدم تطابق قائمة السماح للقناة/المجموعة.

العلامات الشائعة:

- `drop guild message (mention required` → تم تجاهل رسالة المجموعة حتى حدوث إشارة.
- `pairing request` → يحتاج المرسل إلى موافقة.
- `blocked` / `allowlist` → تمّت تصفية المرسل/القناة بواسطة السياسة.

ذو صلة:

- [/channels/troubleshooting](/ar/channels/troubleshooting)
- [/channels/pairing](/ar/channels/pairing)
- [/channels/groups](/ar/channels/groups)

## اتصال dashboard/control UI

عندما يتعذر على dashboard/control UI الاتصال، تحقّق من عنوان URL، ووضع المصادقة، وافتراضات السياق الآمن.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

ابحث عن:

- عنوان URL الصحيح للفحص وdashboard.
- عدم تطابق وضع المصادقة/الرمز المميز بين العميل وgateway.
- استخدام HTTP في مواضع تتطلب هوية الجهاز.

العلامات الشائعة:

- `device identity required` → سياق غير آمن أو مصادقة جهاز مفقودة.
- `origin not allowed` → `Origin` الخاص بالمتصفح ليس ضمن `gateway.controlUi.allowedOrigins`
  (أو أنك تتصل من origin متصفح غير loopback بدون
  قائمة سماح صريحة).
- `device nonce required` / `device nonce mismatch` → العميل لا يكمل
  تدفق مصادقة الجهاز القائم على التحدي (`connect.challenge` + `device.nonce`).
- `device signature invalid` / `device signature expired` → العميل وقّع الحمولة الخطأ
  (أو استخدم طابعًا زمنيًا قديمًا) للمصافحة الحالية.
- `AUTH_TOKEN_MISMATCH` مع `canRetryWithDeviceToken=true` → يمكن للعميل تنفيذ إعادة محاولة موثوقة واحدة باستخدام رمز الجهاز المميز المخزّن مؤقتًا.
- تعيد محاولة الرمز المخزّن مؤقتًا هذه استخدام مجموعة النطاقات المخزّنة مع
  رمز الجهاز المميز المقترن. أما المستدعون الذين يستخدمون `deviceToken` صريحًا / `scopes` صريحة فيحتفظون
  بمجموعة النطاقات المطلوبة الخاصة بهم.
- خارج مسار إعادة المحاولة هذا، تكون أولوية مصادقة الاتصال هي
  الرمز/كلمة المرور المشتركة الصريحة أولًا، ثم `deviceToken` الصريح، ثم رمز الجهاز المخزّن، ثم رمز bootstrap.
- في مسار Control UI غير المتزامن عبر Tailscale Serve، يتم تسلسل المحاولات الفاشلة لنفس
  `{scope, ip}` قبل أن يسجل المحدِّد الفشل. لذلك قد تُظهر محاولتان سيئتان
  متزامنتان من العميل نفسه الرسالة `retry later`
  في المحاولة الثانية بدلًا من عدم تطابقين عاديين.
- `too many failed authentication attempts (retry later)` من عميل loopback ذي أصل متصفح
  → يتم حظر الإخفاقات المتكررة من `Origin` المطبّع نفسه مؤقتًا؛ بينما يستخدم أصل localhost آخر حاوية منفصلة.
- تكرار `unauthorized` بعد إعادة المحاولة تلك → انجراف في الرمز المشترك/رمز الجهاز؛ حدّث إعداد الرمز وأعد الموافقة/تدوير رمز الجهاز عند الحاجة.
- `gateway connect failed:` → هدف host/port/url غير صحيح.

### خريطة سريعة لرموز تفاصيل المصادقة

استخدم `error.details.code` من استجابة `connect` الفاشلة لاختيار الإجراء التالي:

| رمز التفاصيل                | المعنى                                                   | الإجراء الموصى به                                                                                                                                                                                                                                                                       |
| --------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AUTH_TOKEN_MISSING`        | لم يرسل العميل الرمز المشترك المطلوب.                   | الصق/اضبط الرمز في العميل ثم أعد المحاولة. لمسارات dashboard: استخدم `openclaw config get gateway.auth.token` ثم الصقه في إعدادات Control UI.                                                                                                                                         |
| `AUTH_TOKEN_MISMATCH`       | الرمز المشترك لا يطابق رمز مصادقة gateway.              | إذا كانت `canRetryWithDeviceToken=true`، فاسمح بإعادة محاولة موثوقة واحدة. تعيد محاولات الرمز المخزّن مؤقتًا استخدام النطاقات المعتمدة المخزنة؛ أما المستدعون الذين يستخدمون `deviceToken` / `scopes` صريحة فيحتفظون بالنطاقات المطلوبة. إذا استمر الفشل، فشغّل [قائمة التحقق من استعادة انجراف الرمز](/cli/devices#token-drift-recovery-checklist). |
| `AUTH_DEVICE_TOKEN_MISMATCH` | رمز كل جهاز المخزّن مؤقتًا قديم أو ملغى.               | دوّر/أعد الموافقة على رمز الجهاز باستخدام [devices CLI](/cli/devices)، ثم أعد الاتصال.                                                                                                                                                                                                 |
| `PAIRING_REQUIRED`          | هوية الجهاز معروفة لكنها غير معتمدة لهذا الدور.         | وافق على الطلب المعلق: `openclaw devices list` ثم `openclaw devices approve <requestId>`.                                                                                                                                                                                              |

فحص ترحيل device auth v2:

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

إذا أظهرت السجلات أخطاء nonce/signature، فحدّث العميل المتصل وتحقق من أنه:

1. ينتظر `connect.challenge`
2. يوقّع الحمولة المرتبطة بالتحدي
3. يرسل `connect.params.device.nonce` مع nonce التحدي نفسه

إذا تم رفض `openclaw devices rotate` / `revoke` / `remove` بشكل غير متوقع:

- يمكن لجلسات رموز الأجهزة المقترنة إدارة **أجهزتها الخاصة فقط** إلا إذا
  كان لدى المستدعي أيضًا `operator.admin`
- لا يمكن لـ `openclaw devices rotate --scope ...` طلب نطاقات operator
  إلا إذا كانت جلسة المستدعي تملكها بالفعل

ذو صلة:

- [/web/control-ui](/web/control-ui)
- [/gateway/configuration](/ar/gateway/configuration) (أوضاع مصادقة gateway)
- [/gateway/trusted-proxy-auth](/ar/gateway/trusted-proxy-auth)
- [/gateway/remote](/ar/gateway/remote)
- [/cli/devices](/cli/devices)

## خدمة Gateway لا تعمل

استخدم هذا القسم عندما تكون الخدمة مثبتة لكن العملية لا تظل قيد التشغيل.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep   # يفحص أيضًا الخدمات على مستوى النظام
```

ابحث عن:

- `Runtime: stopped` مع تلميحات الخروج.
- عدم تطابق إعداد الخدمة (`Config (cli)` مقابل `Config (service)`).
- تعارضات المنفذ/المستمع.
- عمليات تثبيت launchd/systemd/schtasks إضافية عند استخدام `--deep`.
- تلميحات التنظيف في `Other gateway-like services detected (best effort)`.

العلامات الشائعة:

- `Gateway start blocked: set gateway.mode=local` أو `existing config is missing gateway.mode` → وضع gateway المحلي غير مفعّل، أو تم إفساد ملف الإعداد وفقد `gateway.mode`. الإصلاح: اضبط `gateway.mode="local"` في إعدادك، أو أعد تشغيل `openclaw onboard --mode local` / `openclaw setup` لإعادة ختم إعداد الوضع المحلي المتوقع. إذا كنت تشغّل OpenClaw عبر Podman، فمسار الإعداد الافتراضي هو `~/.openclaw/openclaw.json`.
- `refusing to bind gateway ... without auth` → ربط non-loopback بدون مسار مصادقة صالح للـ gateway (رمز/كلمة مرور، أو trusted-proxy عند ضبطه).
- `another gateway instance is already listening` / `EADDRINUSE` → تعارض منفذ.
- `Other gateway-like services detected (best effort)` → توجد وحدات launchd/systemd/schtasks قديمة أو متوازية. يجب أن تحتفظ معظم الإعدادات بـ gateway واحد لكل جهاز؛ وإذا كنت تحتاج بالفعل إلى أكثر من واحد، فاعزل المنافذ + الإعداد + الحالة + مساحة العمل. راجع [/gateway#multiple-gateways-same-host](/ar/gateway#multiple-gateways-same-host).

ذو صلة:

- [/gateway/background-process](/ar/gateway/background-process)
- [/gateway/configuration](/ar/gateway/configuration)
- [/gateway/doctor](/ar/gateway/doctor)

## تحذيرات فحص Gateway

استخدم هذا القسم عندما يتمكن `openclaw gateway probe` من الوصول إلى شيء ما، لكنه لا يزال يطبع كتلة تحذير.

```bash
openclaw gateway probe
openclaw gateway probe --json
openclaw gateway probe --ssh user@gateway-host
```

ابحث عن:

- `warnings[].code` و`primaryTargetId` في خرج JSON.
- ما إذا كان التحذير يتعلق ببديل SSH، أو تعدد الـ gateways، أو النطاقات المفقودة، أو مراجع المصادقة غير المحلولة.

العلامات الشائعة:

- `SSH tunnel failed to start; falling back to direct probes.` → فشل إعداد SSH، لكن الأمر ما زال يجرّب الأهداف المباشرة المضبوطة/loopback.
- `multiple reachable gateways detected` → استجاب أكثر من هدف واحد. عادةً ما يعني هذا إعدادًا مقصودًا متعدد الـ gateways أو مستمعين قديمين/مكررَين.
- `Probe diagnostics are limited by gateway scopes (missing operator.read)` → نجح الاتصال، لكن RPC التفصيلي محدود بالنطاقات؛ قم بإقران هوية الجهاز أو استخدم بيانات اعتماد تحتوي على `operator.read`.
- نص تحذير SecretRef غير المحلول لـ `gateway.auth.*` / `gateway.remote.*` → كانت مواد المصادقة غير متاحة في مسار هذا الأمر للهدف الفاشل.

ذو صلة:

- [/cli/gateway](/cli/gateway)
- [/gateway#multiple-gateways-same-host](/ar/gateway#multiple-gateways-same-host)
- [/gateway/remote](/ar/gateway/remote)

## القناة متصلة لكن الرسائل لا تتدفق

إذا كانت حالة القناة متصلة لكن تدفق الرسائل متوقف، فركّز على السياسة، والأذونات، وقواعد التسليم الخاصة بالقناة.

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

ابحث عن:

- سياسة الرسائل المباشرة (`pairing`، `allowlist`، `open`، `disabled`).
- قائمة السماح للمجموعة ومتطلبات الإشارة.
- أذونات/نطاقات API الخاصة بالقناة المفقودة.

العلامات الشائعة:

- `mention required` → تم تجاهل الرسالة بسبب سياسة الإشارة في المجموعة.
- آثار `pairing` / الموافقة المعلّقة → المرسل غير معتمد.
- `missing_scope`، `not_in_channel`، `Forbidden`، `401/403` → مشكلة في مصادقة/أذونات القناة.

ذو صلة:

- [/channels/troubleshooting](/ar/channels/troubleshooting)
- [/channels/whatsapp](/ar/channels/whatsapp)
- [/channels/telegram](/ar/channels/telegram)
- [/channels/discord](/ar/channels/discord)

## تسليم cron وheartbeat

إذا لم يتم تشغيل cron أو heartbeat أو لم يتم التسليم، فتحقق أولًا من حالة المجدول، ثم من هدف التسليم.

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

ابحث عن:

- أن cron مفعّل ووقت الاستيقاظ التالي موجود.
- حالة سجل تشغيل المهمة (`ok`، `skipped`، `error`).
- أسباب تخطي heartbeat (`quiet-hours`، `requests-in-flight`، `alerts-disabled`، `empty-heartbeat-file`، `no-tasks-due`).

العلامات الشائعة:

- `cron: scheduler disabled; jobs will not run automatically` → تم تعطيل cron.
- `cron: timer tick failed` → فشل نبض المجدول؛ تحقق من أخطاء الملف/السجل/وقت التشغيل.
- `heartbeat skipped` مع `reason=quiet-hours` → خارج نافذة الساعات النشطة.
- `heartbeat skipped` مع `reason=empty-heartbeat-file` → الملف `HEARTBEAT.md` موجود لكنه يحتوي فقط على أسطر فارغة / عناوين markdown، لذلك يتخطى OpenClaw استدعاء النموذج.
- `heartbeat skipped` مع `reason=no-tasks-due` → يحتوي `HEARTBEAT.md` على كتلة `tasks:`، لكن لا توجد مهام مستحقة في هذه النبضة.
- `heartbeat: unknown accountId` → معرّف حساب غير صالح لهدف تسليم heartbeat.
- `heartbeat skipped` مع `reason=dm-blocked` → تم حل هدف heartbeat إلى وجهة على نمط الرسائل المباشرة بينما `agents.defaults.heartbeat.directPolicy` (أو التجاوز لكل وكيل) مضبوط على `block`.

ذو صلة:

- [/automation/cron-jobs#troubleshooting](/ar/automation/cron-jobs#troubleshooting)
- [/automation/cron-jobs](/ar/automation/cron-jobs)
- [/gateway/heartbeat](/ar/gateway/heartbeat)

## فشل أداة العقدة المقترنة

إذا كانت العقدة مقترنة لكن الأدوات تفشل، فاعزل حالة الواجهة الأمامية، والأذونات، والموافقة.

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

ابحث عن:

- أن العقدة متصلة وبها الإمكانات المتوقعة.
- منح أذونات نظام التشغيل للكاميرا/الميكروفون/الموقع/الشاشة.
- الموافقات التنفيذية وحالة قائمة السماح.

العلامات الشائعة:

- `NODE_BACKGROUND_UNAVAILABLE` → يجب أن يكون تطبيق العقدة في الواجهة الأمامية.
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → أذونات نظام التشغيل مفقودة.
- `SYSTEM_RUN_DENIED: approval required` → موافقة التنفيذ معلّقة.
- `SYSTEM_RUN_DENIED: allowlist miss` → تم حظر الأمر بواسطة قائمة السماح.

ذو صلة:

- [/nodes/troubleshooting](/ar/nodes/troubleshooting)
- [/nodes/index](/ar/nodes/index)
- [/tools/exec-approvals](/ar/tools/exec-approvals)

## فشل أداة المتصفح

استخدم هذا القسم عندما تفشل إجراءات أداة المتصفح رغم أن gateway نفسه بحالة سليمة.

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

ابحث عن:

- ما إذا كان `plugins.allow` مضبوطًا ويتضمن `browser`.
- صحة مسار الملف التنفيذي للمتصفح.
- إمكانية الوصول إلى ملف تعريف CDP.
- توفر Chrome المحلي لملفات التعريف `existing-session` / `user`.

العلامات الشائعة:

- `unknown command "browser"` أو `unknown command 'browser'` → تم استبعاد browser plugin المضمّن بواسطة `plugins.allow`.
- غياب أداة المتصفح / عدم توفرها بينما `browser.enabled=true` → يستبعد `plugins.allow` قيمة `browser`، لذلك لم يتم تحميل الـ plugin.
- `Failed to start Chrome CDP on port` → فشلت عملية المتصفح في الإطلاق.
- `browser.executablePath not found` → المسار المضبوط غير صالح.
- `browser.cdpUrl must be http(s) or ws(s)` → يستخدم عنوان CDP المضبوط مخططًا غير مدعوم مثل `file:` أو `ftp:`.
- `browser.cdpUrl has invalid port` → يحتوي عنوان CDP المضبوط على منفذ سيئ أو خارج النطاق.
- `No Chrome tabs found for profile="user"` → لا توجد علامات تبويب Chrome محلية مفتوحة لملف تعريف الإرفاق Chrome MCP.
- `Remote CDP for profile "<name>" is not reachable` → تعذّر الوصول إلى نقطة نهاية CDP البعيدة المضبوطة من مضيف gateway.
- `Browser attachOnly is enabled ... not reachable` أو `Browser attachOnly is enabled and CDP websocket ... is not reachable` → لا يوجد هدف قابل للوصول لملف تعريف attach-only، أو أن نقطة نهاية HTTP استجابت لكن تعذّر مع ذلك فتح CDP WebSocket.
- `Playwright is not available in this gateway build; '<feature>' is unsupported.` → لا يحتوي تثبيت gateway الحالي على حزمة Playwright الكاملة؛ لا تزال لقطات ARIA ولقطات الشاشة الأساسية للصفحات تعمل، لكن التنقل ولقطات AI ولقطات العناصر باستخدام محددات CSS وتصدير PDF تظل غير متاحة.
- `fullPage is not supported for element screenshots` → خلط طلب لقطة الشاشة `--full-page` مع `--ref` أو `--element`.
- `element screenshots are not supported for existing-session profiles; use ref from snapshot.` → يجب أن تستخدم استدعاءات لقطات الشاشة الخاصة بـ Chrome MCP / `existing-session` التقاط الصفحة أو `--ref` من اللقطة، وليس CSS `--element`.
- `existing-session file uploads do not support element selectors; use ref/inputRef.` → تحتاج خطافات رفع الملفات في Chrome MCP إلى مراجع لقطات، لا إلى محددات CSS.
- `existing-session file uploads currently support one file at a time.` → أرسل عملية رفع واحدة لكل استدعاء في ملفات تعريف Chrome MCP.
- `existing-session dialog handling does not support timeoutMs.` → لا تدعم خطافات الحوار في ملفات تعريف Chrome MCP تجاوزات timeout.
- `response body is not supported for existing-session profiles yet.` → لا يزال `responsebody` يتطلب متصفحًا مُدارًا أو ملف تعريف CDP خامًا.
- تجاوزات viewport / dark-mode / locale / offline القديمة في ملفات تعريف attach-only أو CDP البعيدة → شغّل `openclaw browser stop --browser-profile <name>` لإغلاق جلسة التحكم النشطة وتحرير حالة المحاكاة Playwright/CDP بدون إعادة تشغيل gateway بالكامل.

ذو صلة:

- [/tools/browser-linux-troubleshooting](/ar/tools/browser-linux-troubleshooting)
- [/tools/browser](/ar/tools/browser)

## إذا قمت بالترقية وتوقف شيء ما فجأة

معظم الأعطال بعد الترقية تكون بسبب انجراف في الإعداد أو فرض إعدادات افتراضية أكثر صرامة.

### 1) تغيّر سلوك المصادقة وتجاوز عنوان URL

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

ما الذي يجب التحقق منه:

- إذا كانت `gateway.mode=remote`، فقد تكون استدعاءات CLI تستهدف جهة بعيدة بينما خدمتك المحلية سليمة.
- لا تعود الاستدعاءات الصريحة `--url` إلى بيانات الاعتماد المخزنة.

العلامات الشائعة:

- `gateway connect failed:` → هدف URL غير صحيح.
- `unauthorized` → يمكن الوصول إلى نقطة النهاية لكن المصادقة غير صحيحة.

### 2) أصبحت قيود الربط والمصادقة أكثر صرامة

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

ما الذي يجب التحقق منه:

- تحتاج عمليات الربط non-loopback (`lan`، `tailnet`، `custom`) إلى مسار مصادقة صالح للـ gateway: مصادقة برمز/كلمة مرور مشتركة، أو نشر `trusted-proxy` مضبوط بشكل صحيح على non-loopback.
- لا تستبدل المفاتيح القديمة مثل `gateway.token` القيمة `gateway.auth.token`.

العلامات الشائعة:

- `refusing to bind gateway ... without auth` → ربط non-loopback بدون مسار مصادقة صالح للـ gateway.
- `RPC probe: failed` بينما وقت التشغيل يعمل → الـ gateway حي لكن يتعذر الوصول إليه باستخدام المصادقة/عنوان URL الحاليين.

### 3) تغيّرت حالة الاقتران وهوية الجهاز

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

ما الذي يجب التحقق منه:

- طلبات الموافقة المعلقة للأجهزة الخاصة بـ dashboard/nodes.
- طلبات موافقة اقتران الرسائل المباشرة المعلقة بعد تغييرات السياسة أو الهوية.

العلامات الشائعة:

- `device identity required` → لم يتم استيفاء مصادقة الجهاز.
- `pairing required` → يجب الموافقة على المرسل/الجهاز.

إذا ظل إعداد الخدمة ووقت التشغيل غير متطابقين بعد الفحوصات، فأعد تثبيت بيانات تعريف الخدمة من ملف التعريف/دليل الحالة نفسه:

```bash
openclaw gateway install --force
openclaw gateway restart
```

ذو صلة:

- [/gateway/pairing](/ar/gateway/pairing)
- [/gateway/authentication](/ar/gateway/authentication)
- [/gateway/background-process](/ar/gateway/background-process)
