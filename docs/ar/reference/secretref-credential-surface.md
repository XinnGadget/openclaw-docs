---
read_when:
    - التحقق من تغطية بيانات اعتماد SecretRef
    - تدقيق ما إذا كانت بيانات اعتماد مؤهلة لـ `secrets configure` أو `secrets apply`
    - التحقق من سبب كون بيانات اعتماد خارج السطح المدعوم
summary: السطح القياسي المعتمد وغير المعتمد لبيانات اعتماد SecretRef
title: سطح بيانات اعتماد SecretRef
x-i18n:
    generated_at: "2026-04-07T07:21:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 211f4b504c5808f7790683066fc2c8b700c705c598f220a264daf971b81cc593
    source_path: reference/secretref-credential-surface.md
    workflow: 15
---

# سطح بيانات اعتماد SecretRef

تحدد هذه الصفحة السطح القياسي لبيانات اعتماد SecretRef.

الغرض من النطاق:

- ضمن النطاق: بيانات الاعتماد التي يزوّدها المستخدم مباشرةً والتي لا يقوم OpenClaw بإصدارها أو تدويرها.
- خارج النطاق: بيانات الاعتماد التي تُصدر أثناء التشغيل أو التي تتناوب، ومواد تحديث OAuth، والعناصر الشبيهة بالجلسات.

## بيانات الاعتماد المدعومة

### أهداف `openclaw.json` (`secrets configure` + `secrets apply` + `secrets audit`)

[//]: # "secretref-supported-list-start"

- `models.providers.*.apiKey`
- `models.providers.*.headers.*`
- `models.providers.*.request.auth.token`
- `models.providers.*.request.auth.value`
- `models.providers.*.request.headers.*`
- `models.providers.*.request.proxy.tls.ca`
- `models.providers.*.request.proxy.tls.cert`
- `models.providers.*.request.proxy.tls.key`
- `models.providers.*.request.proxy.tls.passphrase`
- `models.providers.*.request.tls.ca`
- `models.providers.*.request.tls.cert`
- `models.providers.*.request.tls.key`
- `models.providers.*.request.tls.passphrase`
- `skills.entries.*.apiKey`
- `agents.defaults.memorySearch.remote.apiKey`
- `agents.list[].memorySearch.remote.apiKey`
- `talk.providers.*.apiKey`
- `messages.tts.providers.*.apiKey`
- `tools.web.fetch.firecrawl.apiKey`
- `plugins.entries.brave.config.webSearch.apiKey`
- `plugins.entries.google.config.webSearch.apiKey`
- `plugins.entries.xai.config.webSearch.apiKey`
- `plugins.entries.moonshot.config.webSearch.apiKey`
- `plugins.entries.perplexity.config.webSearch.apiKey`
- `plugins.entries.firecrawl.config.webSearch.apiKey`
- `plugins.entries.minimax.config.webSearch.apiKey`
- `plugins.entries.tavily.config.webSearch.apiKey`
- `tools.web.search.apiKey`
- `gateway.auth.password`
- `gateway.auth.token`
- `gateway.remote.token`
- `gateway.remote.password`
- `cron.webhookToken`
- `channels.telegram.botToken`
- `channels.telegram.webhookSecret`
- `channels.telegram.accounts.*.botToken`
- `channels.telegram.accounts.*.webhookSecret`
- `channels.slack.botToken`
- `channels.slack.appToken`
- `channels.slack.userToken`
- `channels.slack.signingSecret`
- `channels.slack.accounts.*.botToken`
- `channels.slack.accounts.*.appToken`
- `channels.slack.accounts.*.userToken`
- `channels.slack.accounts.*.signingSecret`
- `channels.discord.token`
- `channels.discord.pluralkit.token`
- `channels.discord.voice.tts.providers.*.apiKey`
- `channels.discord.accounts.*.token`
- `channels.discord.accounts.*.pluralkit.token`
- `channels.discord.accounts.*.voice.tts.providers.*.apiKey`
- `channels.irc.password`
- `channels.irc.nickserv.password`
- `channels.irc.accounts.*.password`
- `channels.irc.accounts.*.nickserv.password`
- `channels.bluebubbles.password`
- `channels.bluebubbles.accounts.*.password`
- `channels.feishu.appSecret`
- `channels.feishu.encryptKey`
- `channels.feishu.verificationToken`
- `channels.feishu.accounts.*.appSecret`
- `channels.feishu.accounts.*.encryptKey`
- `channels.feishu.accounts.*.verificationToken`
- `channels.msteams.appPassword`
- `channels.mattermost.botToken`
- `channels.mattermost.accounts.*.botToken`
- `channels.matrix.accessToken`
- `channels.matrix.password`
- `channels.matrix.accounts.*.accessToken`
- `channels.matrix.accounts.*.password`
- `channels.nextcloud-talk.botSecret`
- `channels.nextcloud-talk.apiPassword`
- `channels.nextcloud-talk.accounts.*.botSecret`
- `channels.nextcloud-talk.accounts.*.apiPassword`
- `channels.zalo.botToken`
- `channels.zalo.webhookSecret`
- `channels.zalo.accounts.*.botToken`
- `channels.zalo.accounts.*.webhookSecret`
- `channels.googlechat.serviceAccount` عبر النظير `serviceAccountRef` (استثناء توافق)
- `channels.googlechat.accounts.*.serviceAccount` عبر النظير `serviceAccountRef` (استثناء توافق)

### أهداف `auth-profiles.json` (`secrets configure` + `secrets apply` + `secrets audit`)

- `profiles.*.keyRef` (`type: "api_key"`؛ غير مدعوم عندما تكون `auth.profiles.<id>.mode = "oauth"`)
- `profiles.*.tokenRef` (`type: "token"`؛ غير مدعوم عندما تكون `auth.profiles.<id>.mode = "oauth"`)

[//]: # "secretref-supported-list-end"

ملاحظات:

- تتطلب أهداف خطة ملف تعريف المصادقة `agentId`.
- تستهدف إدخالات الخطة `profiles.*.key` / `profiles.*.token` وتكتب المراجع النظيرة (`keyRef` / `tokenRef`).
- تُدرج مراجع ملفات تعريف المصادقة في تحليل وقت التشغيل وتغطية التدقيق.
- حاجز سياسة OAuth: لا يمكن دمج `auth.profiles.<id>.mode = "oauth"` مع مدخلات SecretRef لذلك الملف التعريفي. يفشل بدء التشغيل/إعادة التحميل وتحليل ملف تعريف المصادقة بسرعة عند انتهاك هذه السياسة.
- بالنسبة إلى موفري النماذج المُدارين عبر SecretRef، تستمر إدخالات `agents/*/agent/models.json` المُنشأة في حفظ علامات غير سرية (وليس القيم السرية المحلَّلة) لأسطح `apiKey`/الترويسات.
- حفظ العلامات ذو مصدر موثوق: يكتب OpenClaw العلامات من لقطة تهيئة المصدر النشطة (قبل التحليل)، وليس من القيم السرية المحلَّلة وقت التشغيل.
- بالنسبة إلى البحث على الويب:
  - في وضع الموفّر الصريح (مع تعيين `tools.web.search.provider`)، يكون مفتاح الموفّر المحدد فقط نشطًا.
  - في الوضع التلقائي (عندما لا يكون `tools.web.search.provider` معيّنًا)، يكون مفتاح الموفّر الأول فقط الذي يُحل وفق الأسبقية نشطًا.
  - في الوضع التلقائي، تُعامل مراجع الموفّرين غير المحددين على أنها غير نشطة حتى يتم تحديدها.
  - ما تزال مسارات الموفّر القديمة `tools.web.search.*` تُحل خلال نافذة التوافق، لكن السطح القياسي لـ SecretRef هو `plugins.entries.<plugin>.config.webSearch.*`.

## بيانات الاعتماد غير المدعومة

تشمل بيانات الاعتماد الخارجة عن النطاق ما يلي:

[//]: # "secretref-unsupported-list-start"

- `commands.ownerDisplaySecret`
- `hooks.token`
- `hooks.gmail.pushToken`
- `hooks.mappings[].sessionKey`
- `auth-profiles.oauth.*`
- `channels.discord.threadBindings.webhookToken`
- `channels.discord.accounts.*.threadBindings.webhookToken`
- `channels.whatsapp.creds.json`
- `channels.whatsapp.accounts.*.creds.json`

[//]: # "secretref-unsupported-list-end"

المبررات:

- تُصدر هذه البيانات الاعتمادية، أو تُدوَّر، أو تحمل جلسات، أو تنتمي إلى فئات OAuth دائمة لا تتوافق مع تحليل SecretRef الخارجي للقراءة فقط.
