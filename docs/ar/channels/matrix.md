---
read_when:
    - إعداد Matrix في OpenClaw
    - تهيئة التشفير التام بين الطرفين E2EE والتحقق في Matrix
summary: حالة دعم Matrix وإعدادها وأمثلة التهيئة
title: Matrix
x-i18n:
    generated_at: "2026-04-07T07:18:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: d53baa2ea5916cd00a99cae0ded3be41ffa13c9a69e8ea8461eb7baa6a99e13c
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix هي plugin القناة المضمّنة Matrix لـ OpenClaw.
تستخدم `matrix-js-sdk` الرسمية وتدعم الرسائل الخاصة، والغرف، وسلاسل الرسائل، والوسائط، والتفاعلات، واستطلاعات الرأي، والموقع، وE2EE.

## plugin مضمّنة

تأتي Matrix كـ plugin مضمّنة في إصدارات OpenClaw الحالية، لذلك لا تحتاج
البنيات المجمّعة العادية إلى تثبيت منفصل.

إذا كنت تستخدم إصدارًا أقدم أو تثبيتًا مخصصًا يستبعد Matrix، فقم بتثبيتها
يدويًا:

التثبيت من npm:

```bash
openclaw plugins install @openclaw/matrix
```

التثبيت من نسخة محلية:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

راجع [Plugins](/ar/tools/plugin) لمعرفة سلوك plugin وقواعد التثبيت.

## الإعداد

1. تأكد من أن plugin Matrix متاحة.
   - إصدارات OpenClaw المجمّعة الحالية تتضمنها بالفعل.
   - يمكن للتثبيتات الأقدم/المخصصة إضافتها يدويًا باستخدام الأوامر أعلاه.
2. أنشئ حساب Matrix على خادمك المنزلي.
3. هيّئ `channels.matrix` باستخدام أحد الخيارين:
   - `homeserver` + `accessToken`، أو
   - `homeserver` + `userId` + `password`.
4. أعد تشغيل البوابة.
5. ابدأ رسالة خاصة مع الروبوت أو قم بدعوته إلى غرفة.
   - لا تعمل دعوات Matrix الجديدة إلا عندما يسمح `channels.matrix.autoJoin` بذلك.

مسارات الإعداد التفاعلي:

```bash
openclaw channels add
openclaw configure --section channels
```

ما الذي يطلبه معالج Matrix فعليًا:

- عنوان URL لـ homeserver
- طريقة المصادقة: access token أو كلمة مرور
- معرّف المستخدم فقط عند اختيار مصادقة كلمة المرور
- اسم جهاز اختياري
- ما إذا كان يجب تمكين E2EE
- ما إذا كان يجب تهيئة الوصول إلى غرف Matrix الآن
- ما إذا كان يجب تهيئة الانضمام التلقائي إلى دعوات Matrix الآن
- عند تمكين الانضمام التلقائي للدعوات، ما إذا كان يجب أن يكون `allowlist` أو `always` أو `off`

سلوك المعالج الذي يهمك:

- إذا كانت متغيرات بيئة مصادقة Matrix موجودة بالفعل للحساب المحدد، ولم يكن لهذا الحساب مصادقة محفوظة بالفعل في التهيئة، فسيعرض المعالج اختصارًا لمتغيرات البيئة حتى يحتفظ الإعداد بالمصادقة في متغيرات البيئة بدلًا من نسخ الأسرار إلى التهيئة.
- عند إضافة حساب Matrix آخر بشكل تفاعلي، يُطبَّع اسم الحساب المُدخل إلى معرّف الحساب المستخدم في التهيئة ومتغيرات البيئة. على سبيل المثال، يتحول `Ops Bot` إلى `ops-bot`.
- تقبل مطالبات allowlist للرسائل الخاصة قيم `@user:server` الكاملة مباشرةً. تعمل أسماء العرض فقط عندما يعثر البحث الحي في الدليل على تطابق واحد دقيق؛ وإلا يطلب منك المعالج إعادة المحاولة باستخدام معرّف Matrix كامل.
- تقبل مطالبات allowlist للغرف معرّفات الغرف والأسماء المستعارة مباشرةً. ويمكنها أيضًا تحليل أسماء الغرف المنضم إليها مباشرة، لكن الأسماء التي لا يمكن تحليلها تُحتفظ بها كما أُدخلت أثناء الإعداد فقط ويتم تجاهلها لاحقًا بواسطة تحليل allowlist أثناء التشغيل. يفضَّل استخدام `!room:server` أو `#alias:server`.
- يعرض المعالج الآن تحذيرًا صريحًا قبل خطوة الانضمام التلقائي للدعوات لأن `channels.matrix.autoJoin` تكون افتراضيًا `off`؛ ولن تنضم الوكلاء إلى الغرف المدعوة أو دعوات الرسائل الخاصة الجديدة ما لم تقم بتعيينها.
- في وضع allowlist للانضمام التلقائي للدعوات، استخدم فقط أهداف الدعوات الثابتة: `!roomId:server` أو `#alias:server` أو `*`. تُرفض أسماء الغرف العادية.
- تستخدم هوية الغرفة/الجلسة أثناء التشغيل معرّف غرفة Matrix الثابت. تُستخدم الأسماء المستعارة المعلنة للغرفة فقط كمدخلات للبحث، وليس كمفتاح جلسة طويل الأمد أو هوية مجموعة ثابتة.
- لتحليل أسماء الغرف قبل حفظها، استخدم `openclaw channels resolve --channel matrix "Project Room"`.

<Warning>
القيمة الافتراضية لـ `channels.matrix.autoJoin` هي `off`.

إذا تركتها دون تعيين، فلن ينضم الروبوت إلى الغرف المدعوة أو دعوات الرسائل الخاصة الجديدة، ولذلك لن يظهر في المجموعات الجديدة أو الرسائل الخاصة المدعوة ما لم تنضم يدويًا أولًا.

عيّن `autoJoin: "allowlist"` مع `autoJoinAllowlist` لتقييد الدعوات التي يقبلها، أو عيّن `autoJoin: "always"` إذا كنت تريده أن ينضم إلى كل دعوة.

في وضع `allowlist`، لا يقبل `autoJoinAllowlist` إلا `!roomId:server` أو `#alias:server` أو `*`.
</Warning>

مثال allowlist:

```json5
{
  channels: {
    matrix: {
      autoJoin: "allowlist",
      autoJoinAllowlist: ["!ops:example.org", "#support:example.org"],
      groups: {
        "!ops:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

الانضمام إلى كل دعوة:

```json5
{
  channels: {
    matrix: {
      autoJoin: "always",
    },
  },
}
```

إعداد أدنى يعتمد على token:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      dm: { policy: "pairing" },
    },
  },
}
```

إعداد يعتمد على كلمة المرور (يُخزَّن token مؤقتًا بعد تسجيل الدخول):

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: allowlist secret
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

تخزّن Matrix بيانات الاعتماد المؤقتة في `~/.openclaw/credentials/matrix/`.
يستخدم الحساب الافتراضي `credentials.json`؛ وتستخدم الحسابات المسماة `credentials-<account>.json`.
عند وجود بيانات اعتماد مؤقتة هناك، يتعامل OpenClaw مع Matrix على أنها مُهيأة لأغراض الإعداد وdoctor واكتشاف حالة القناة حتى إذا لم تُضبط المصادقة الحالية مباشرة في التهيئة.

مكافئات متغيرات البيئة (تُستخدم عندما لا يكون مفتاح التهيئة مضبوطًا):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

للحسابات غير الافتراضية، استخدم متغيرات بيئة بنطاق الحساب:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

مثال للحساب `ops`:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

بالنسبة إلى معرّف الحساب المطبع `ops-bot`، استخدم:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

تقوم Matrix بتهريب علامات الترقيم في معرّفات الحسابات للحفاظ على خلو متغيرات البيئة ذات النطاق المحدد من التصادمات.
فعلى سبيل المثال، يتحول `-` إلى `_X2D_`، لذلك يتحول `ops-prod` إلى `MATRIX_OPS_X2D_PROD_*`.

لا يعرض المعالج التفاعلي اختصار متغيرات البيئة إلا عندما تكون متغيرات بيئة المصادقة تلك موجودة بالفعل، ولا يكون للحساب المحدد مصادقة Matrix محفوظة بالفعل في التهيئة.

## مثال على التهيئة

هذه تهيئة أساسية عملية تتضمن pairing للرسائل الخاصة، وallowlist للغرف، وتمكين E2EE:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,

      dm: {
        policy: "pairing",
        sessionScope: "per-room",
        threadReplies: "off",
      },

      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },

      autoJoin: "allowlist",
      autoJoinAllowlist: ["!roomid:example.org"],
      threadReplies: "inbound",
      replyToMode: "off",
      streaming: "partial",
    },
  },
}
```

ينطبق `autoJoin` على دعوات Matrix عمومًا، وليس فقط على دعوات الغرف/المجموعات.
ويشمل ذلك دعوات الرسائل الخاصة الجديدة. في وقت الدعوة، لا يعرف OpenClaw بشكل موثوق ما إذا كانت
الغرفة المدعوة ستُعامل في النهاية كرسالة خاصة أو كمجموعة، لذلك تمر جميع الدعوات عبر قرار
`autoJoin` نفسه أولًا. يظل `dm.policy` مطبقًا بعد انضمام الروبوت وتصنيف الغرفة
كرسالة خاصة، لذلك يتحكم `autoJoin` في سلوك الانضمام بينما يتحكم `dm.policy` في سلوك
الرد/الوصول.

## معاينات البث

بث الردود في Matrix ميزة اختيارية.

عيّن `channels.matrix.streaming` إلى `"partial"` عندما تريد من OpenClaw إرسال
رد معاينة مباشر واحد، وتحرير هذه المعاينة في مكانها أثناء توليد النص من النموذج، ثم إنهاءها عند
اكتمال الرد:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` هو الإعداد الافتراضي. ينتظر OpenClaw الرد النهائي ويرسله مرة واحدة.
- `streaming: "partial"` ينشئ رسالة معاينة واحدة قابلة للتحرير لكتلة المساعد الحالية باستخدام رسائل Matrix النصية العادية. يحافظ هذا على سلوك الإشعارات القديم في Matrix القائم على المعاينة أولًا، لذلك قد تُرسل التطبيقات القياسية إشعارًا عند نص المعاينة الأول المتدفق بدلًا من الكتلة النهائية.
- `streaming: "quiet"` ينشئ إشعار معاينة هادئًا واحدًا قابلًا للتحرير لكتلة المساعد الحالية. استخدم هذا فقط عندما تهيئ أيضًا قواعد push للمستلمين من أجل تعديلات المعاينة النهائية.
- `blockStreaming: true` يمكّن رسائل تقدم Matrix المنفصلة. عند تمكين بث المعاينة، تحتفظ Matrix بالمسودة المباشرة للكتلة الحالية وتحافظ على الكتل المكتملة كرسائل منفصلة.
- عند تشغيل بث المعاينة وإيقاف `blockStreaming`، تقوم Matrix بتحرير المسودة المباشرة في مكانها وتُنهي الحدث نفسه عند اكتمال الكتلة أو الدورة.
- إذا لم تعد المعاينة مناسبة لحدث Matrix واحد، يوقف OpenClaw بث المعاينة ويعود إلى التسليم النهائي العادي.
- تظل ردود الوسائط ترسل المرفقات بشكل طبيعي. وإذا تعذّر إعادة استخدام معاينة قديمة بأمان، يقوم OpenClaw بحذفها قبل إرسال رد الوسائط النهائي.
- تتطلب تعديلات المعاينة استدعاءات إضافية إلى Matrix API. اترك البث معطلًا إذا كنت تريد أكثر سلوك تحفظًا من ناحية حدود المعدل.

لا يقوم `blockStreaming` بتمكين معاينات المسودات بمفرده.
استخدم `streaming: "partial"` أو `streaming: "quiet"` لتعديلات المعاينة؛ ثم أضف `blockStreaming: true` فقط إذا كنت تريد أيضًا أن تبقى كتل المساعد المكتملة مرئية كرسائل تقدم منفصلة.

إذا كنت تحتاج إلى إشعارات Matrix القياسية دون قواعد push مخصصة، فاستخدم `streaming: "partial"` لسلوك المعاينة أولًا أو اترك `streaming` معطلًا للتسليم النهائي فقط. مع `streaming: "off"`:

- `blockStreaming: true` يرسل كل كتلة مكتملة كرسالة Matrix عادية تُرسل إشعارًا.
- `blockStreaming: false` يرسل فقط الرد النهائي المكتمل كرسالة Matrix عادية تُرسل إشعارًا.

### قواعد push مستضافة ذاتيًا للمعاينات النهائية الهادئة

إذا كنت تشغّل بنية Matrix التحتية الخاصة بك وتريد أن ترسل المعاينات الهادئة إشعارًا فقط عند اكتمال كتلة أو
الرد النهائي، فعيّن `streaming: "quiet"` وأضف قاعدة push لكل مستخدم من أجل تعديلات المعاينة النهائية.

يكون هذا عادة إعدادًا على مستوى المستخدم المستلم، وليس تغييرًا عامًا في تهيئة homeserver:

خريطة سريعة قبل البدء:

- المستخدم المستلم = الشخص الذي يجب أن يتلقى الإشعار
- مستخدم الروبوت = حساب Matrix الخاص بـ OpenClaw الذي يرسل الرد
- استخدم access token الخاص بالمستخدم المستلم لطلبات API أدناه
- طابق `sender` في قاعدة push مع MXID الكامل لمستخدم الروبوت

1. هيّئ OpenClaw لاستخدام المعاينات الهادئة:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. تأكد من أن حساب المستلم يتلقى بالفعل إشعارات push العادية من Matrix. تعمل قواعد المعاينة الهادئة
   فقط إذا كان لدى هذا المستخدم بالفعل pushers/أجهزة عاملة.

3. احصل على access token الخاص بالمستخدم المستلم.
   - استخدم token المستخدم المتلقي، وليس token الروبوت.
   - عادةً ما تكون إعادة استخدام token جلسة عميل موجودة هي الأسهل.
   - إذا كنت بحاجة إلى إصدار token جديد، يمكنك تسجيل الدخول عبر Matrix Client-Server API القياسية:

```bash
curl -sS -X POST \
  "https://matrix.example.org/_matrix/client/v3/login" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "m.login.password",
    "identifier": {
      "type": "m.id.user",
      "user": "@alice:example.org"
    },
    "password": "REDACTED"
  }'
```

4. تحقق من أن حساب المستلم لديه pushers بالفعل:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

إذا أعاد هذا الاستعلام عدم وجود pushers/أجهزة نشطة، فأصلح إشعارات Matrix العادية أولًا قبل إضافة
قاعدة OpenClaw أدناه.

تضع OpenClaw علامة على تعديلات معاينات النص النهائي فقط بالقيمة التالية:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. أنشئ قاعدة push من نوع override لكل حساب مستلم يجب أن يتلقى هذه الإشعارات:

```bash
curl -sS -X PUT \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname" \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "conditions": [
      { "kind": "event_match", "key": "type", "pattern": "m.room.message" },
      {
        "kind": "event_property_is",
        "key": "content.m\\.relates_to.rel_type",
        "value": "m.replace"
      },
      {
        "kind": "event_property_is",
        "key": "content.com\\.openclaw\\.finalized_preview",
        "value": true
      },
      { "kind": "event_match", "key": "sender", "pattern": "@bot:example.org" }
    ],
    "actions": [
      "notify",
      { "set_tweak": "sound", "value": "default" },
      { "set_tweak": "highlight", "value": false }
    ]
  }'
```

استبدل هذه القيم قبل تشغيل الأمر:

- `https://matrix.example.org`: عنوان URL الأساسي لـ homeserver لديك
- `$USER_ACCESS_TOKEN`: access token الخاص بالمستخدم المتلقي
- `openclaw-finalized-preview-botname`: معرّف قاعدة فريد لهذا الروبوت لهذا المستخدم المتلقي
- `@bot:example.org`: معرّف MXID لروبوت Matrix الخاص بـ OpenClaw، وليس MXID الخاص بالمستخدم المتلقي

مهم لعمليات إعداد الروبوتات المتعددة:

- تُفهرس قواعد push بواسطة `ruleId`. تؤدي إعادة تشغيل `PUT` على معرّف القاعدة نفسه إلى تحديث تلك القاعدة.
- إذا كان يجب على مستخدم متلقٍ واحد تلقي إشعارات من عدة حسابات روبوت Matrix تابعة لـ OpenClaw، فأنشئ قاعدة واحدة لكل روبوت مع معرّف قاعدة فريد لكل تطابق `sender`.
- نمط بسيط لذلك هو `openclaw-finalized-preview-<botname>`، مثل `openclaw-finalized-preview-ops` أو `openclaw-finalized-preview-support`.

تُقيَّم القاعدة مقابل مرسل الحدث:

- قم بالمصادقة باستخدام token المستخدم المتلقي
- طابق `sender` مع MXID الخاص بروبوت OpenClaw

6. تحقق من وجود القاعدة:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. اختبر ردًا متدفقًا. في الوضع الهادئ، يجب أن تعرض الغرفة معاينة مسودة هادئة وأن
   يرسل التعديل النهائي في مكانه إشعارًا واحدًا عند اكتمال الكتلة أو الدورة.

إذا احتجت إلى إزالة القاعدة لاحقًا، فاحذف معرّف القاعدة نفسه باستخدام token المستخدم المتلقي:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

ملاحظات:

- أنشئ القاعدة باستخدام access token الخاص بالمستخدم المتلقي، وليس token الروبوت.
- تُدرج قواعد `override` الجديدة المعرّفة من المستخدم قبل قواعد الكبت الافتراضية، لذلك لا حاجة إلى معامل ترتيب إضافي.
- يؤثر هذا فقط في تعديلات معاينة النص النهائي التي يمكن لـ OpenClaw إنهاؤها بأمان في مكانها. أما بدائل الوسائط وبدائل المعاينات القديمة فما زالت تستخدم تسليم Matrix العادي.
- إذا أظهر `GET /_matrix/client/v3/pushers` عدم وجود pushers، فهذا يعني أن المستخدم لا يملك بعد تسليم push من Matrix يعمل لهذا الحساب/الجهاز.

#### Synapse

بالنسبة إلى Synapse، يكون الإعداد أعلاه كافيًا عادةً بمفرده:

- لا يلزم أي تغيير خاص في `homeserver.yaml` لإشعارات معاينات OpenClaw النهائية.
- إذا كان نشر Synapse لديك يرسل بالفعل إشعارات Matrix العادية، فإن token المستخدم + استدعاء `pushrules` أعلاه هما خطوة الإعداد الأساسية.
- إذا كنت تشغّل Synapse خلف reverse proxy أو workers، فتأكد من أن `/_matrix/client/.../pushrules/` يصل إلى Synapse بشكل صحيح.
- إذا كنت تشغّل Synapse workers، فتأكد من أن pushers سليمة. تتم معالجة تسليم push بواسطة العملية الرئيسية أو `synapse.app.pusher` / عمال pusher المهيئين.

#### Tuwunel

بالنسبة إلى Tuwunel، استخدم مسار الإعداد نفسه واستدعاء API الخاص بـ push-rule المبيّن أعلاه:

- لا يلزم أي إعداد خاص بـ Tuwunel لعلامة المعاينة النهائية نفسها.
- إذا كانت إشعارات Matrix العادية تعمل بالفعل لهذا المستخدم، فإن token المستخدم + استدعاء `pushrules` أعلاه هما خطوة الإعداد الأساسية.
- إذا بدت الإشعارات وكأنها تختفي بينما يكون المستخدم نشطًا على جهاز آخر، فتحقق مما إذا كان `suppress_push_when_active` مفعّلًا. أضاف Tuwunel هذا الخيار في Tuwunel 1.4.2 بتاريخ 12 سبتمبر 2025، ويمكنه عمدًا كبت إشعارات push إلى الأجهزة الأخرى أثناء نشاط أحد الأجهزة.

## التشفير والتحقق

في الغرف المشفرة (E2EE)، تستخدم أحداث الصور الصادرة `thumbnail_file` بحيث تُشفّر معاينات الصور إلى جانب المرفق الكامل. أما الغرف غير المشفرة فما تزال تستخدم `thumbnail_url` العادي. لا حاجة إلى أي تهيئة — إذ تكتشف plugin حالة E2EE تلقائيًا.

### غرف الروبوت إلى الروبوت

افتراضيًا، يتم تجاهل رسائل Matrix الواردة من حسابات OpenClaw Matrix الأخرى المهيأة.

استخدم `allowBots` عندما تريد عمدًا حركة مرور Matrix بين الوكلاء:

```json5
{
  channels: {
    matrix: {
      allowBots: "mentions", // true | "mentions"
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

- `allowBots: true` يقبل الرسائل من حسابات Matrix bot الأخرى المهيأة في الغرف والرسائل الخاصة المسموح بها.
- `allowBots: "mentions"` يقبل تلك الرسائل فقط عندما تذكر هذا الروبوت صراحةً في الغرف. تظل الرسائل الخاصة مسموحًا بها.
- يتجاوز `groups.<room>.allowBots` الإعداد على مستوى الحساب لغرفة واحدة.
- ما يزال OpenClaw يتجاهل الرسائل من معرّف مستخدم Matrix نفسه لتجنب حلقات الرد الذاتي.
- لا تكشف Matrix هنا عن علامة روبوت أصلية؛ ويتعامل OpenClaw مع "صادر عن روبوت" على أنه "أُرسل من حساب Matrix مهيأ آخر على بوابة OpenClaw هذه".

استخدم allowlistات غرف صارمة ومتطلبات الذكر عند تمكين حركة المرور بين الروبوتات في الغرف المشتركة.

تمكين التشفير:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

التحقق من حالة التحقق:

```bash
openclaw matrix verify status
```

حالة مفصلة (تشخيصات كاملة):

```bash
openclaw matrix verify status --verbose
```

تضمين مفتاح الاسترداد المخزّن في مخرجات قابلة للقراءة آليًا:

```bash
openclaw matrix verify status --include-recovery-key --json
```

تهيئة حالة cross-signing والتحقق:

```bash
openclaw matrix verify bootstrap
```

دعم الحسابات المتعددة: استخدم `channels.matrix.accounts` مع بيانات اعتماد لكل حساب و`name` اختياري. راجع [مرجع التهيئة](/ar/gateway/configuration-reference#multi-account-all-channels) للنمط المشترك.

تشخيصات bootstrap مفصلة:

```bash
openclaw matrix verify bootstrap --verbose
```

فرض إعادة تعيين هوية cross-signing جديدة قبل bootstrap:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

تحقق من هذا الجهاز باستخدام مفتاح استرداد:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

تفاصيل مفصلة للتحقق من الجهاز:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

التحقق من سلامة النسخ الاحتياطي لمفاتيح الغرفة:

```bash
openclaw matrix verify backup status
```

تشخيصات مفصلة لسلامة النسخ الاحتياطي:

```bash
openclaw matrix verify backup status --verbose
```

استعادة مفاتيح الغرفة من النسخة الاحتياطية على الخادم:

```bash
openclaw matrix verify backup restore
```

تشخيصات مفصلة للاستعادة:

```bash
openclaw matrix verify backup restore --verbose
```

احذف النسخة الاحتياطية الحالية على الخادم وأنشئ خط أساس جديدًا للنسخ الاحتياطي. إذا تعذر تحميل
مفتاح النسخ الاحتياطي المخزّن بشكل سليم، فقد تؤدي إعادة التعيين هذه أيضًا إلى إعادة إنشاء التخزين السري بحيث
تتمكن عمليات التشغيل البارد المستقبلية من تحميل مفتاح النسخ الاحتياطي الجديد:

```bash
openclaw matrix verify backup reset --yes
```

تكون جميع أوامر `verify` موجزة افتراضيًا (بما في ذلك تسجيل SDK الداخلي الهادئ) وتعرض تشخيصات مفصلة فقط مع `--verbose`.
استخدم `--json` للحصول على مخرجات كاملة قابلة للقراءة آليًا عند كتابة السكربتات.

في إعدادات الحسابات المتعددة، تستخدم أوامر Matrix CLI الحساب الافتراضي الضمني لـ Matrix ما لم تمرر `--account <id>`.
إذا هيأت عدة حسابات مسماة، فقم أولًا بتعيين `channels.matrix.defaultAccount` وإلا ستتوقف عمليات CLI الضمنية تلك وتطلب منك اختيار حساب صراحةً.
استخدم `--account` كلما أردت أن تستهدف عمليات التحقق أو عمليات الجهاز حسابًا مسمىً صراحةً:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

عندما يكون التشفير معطلًا أو غير متاح لحساب مسمى، تشير تحذيرات Matrix وأخطاء التحقق إلى مفتاح تهيئة ذلك الحساب، مثل `channels.matrix.accounts.assistant.encryption`.

### ما معنى "تم التحقق"

يعامل OpenClaw جهاز Matrix هذا على أنه تم التحقق منه فقط عندما يتم التحقق منه بواسطة هوية cross-signing الخاصة بك.
عمليًا، يكشف `openclaw matrix verify status --verbose` ثلاث إشارات ثقة:

- `Locally trusted`: هذا الجهاز موثوق من قبل العميل الحالي فقط
- `Cross-signing verified`: تُبلغ SDK أن الجهاز تم التحقق منه عبر cross-signing
- `Signed by owner`: الجهاز موقّع بواسطة مفتاح self-signing الخاص بك

تصبح `Verified by owner` مساوية لـ `yes` فقط عند وجود تحقق عبر cross-signing أو توقيع المالك.
الثقة المحلية وحدها لا تكفي لكي يعامل OpenClaw الجهاز على أنه موثوق بالكامل.

### ما الذي يفعله bootstrap

الأمر `openclaw matrix verify bootstrap` هو أمر الإصلاح والإعداد لحسابات Matrix المشفرة.
وهو ينفذ جميع ما يلي بالترتيب:

- يهيئ التخزين السري، مع إعادة استخدام مفتاح استرداد موجود إن أمكن
- يهيئ cross-signing ويرفع مفاتيح cross-signing العامة المفقودة
- يحاول تعليم الجهاز الحالي والتوقيع عليه عبر cross-signing
- ينشئ نسخة احتياطية جديدة لمفاتيح الغرف على الخادم إذا لم تكن موجودة بالفعل

إذا كان homeserver يتطلب مصادقة تفاعلية لرفع مفاتيح cross-signing، يحاول OpenClaw الرفع أولًا بدون مصادقة، ثم باستخدام `m.login.dummy`، ثم باستخدام `m.login.password` عندما يكون `channels.matrix.password` مهيأً.

استخدم `--force-reset-cross-signing` فقط عندما تريد عمدًا تجاهل هوية cross-signing الحالية وإنشاء واحدة جديدة.

إذا كنت تريد عمدًا تجاهل النسخة الاحتياطية الحالية لمفاتيح الغرف والبدء بخط أساس جديد
للنسخ الاحتياطي للرسائل المستقبلية، فاستخدم `openclaw matrix verify backup reset --yes`.
افعل ذلك فقط عندما تقبل بأن السجل المشفر القديم غير القابل للاسترداد سيبقى
غير متاح، وأن OpenClaw قد يعيد إنشاء التخزين السري إذا تعذر تحميل سر النسخ الاحتياطي
الحالي بأمان.

### خط أساس جديد للنسخ الاحتياطي

إذا كنت تريد الإبقاء على عمل الرسائل المشفرة المستقبلية وتقبل فقدان السجل القديم غير القابل للاسترداد، فشغّل هذه الأوامر بالترتيب:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

أضف `--account <id>` إلى كل أمر عندما تريد استهداف حساب Matrix مسمىً صراحةً.

### سلوك بدء التشغيل

عندما تكون `encryption: true`، تضبط Matrix قيمة `startupVerification` افتراضيًا على `"if-unverified"`.
عند بدء التشغيل، إذا كان هذا الجهاز لا يزال غير متحقق منه، فستطلب Matrix التحقق الذاتي في عميل Matrix آخر،
وستتخطى الطلبات المكررة ما دام هناك طلب معلّق بالفعل، وتطبّق فترة تهدئة محلية قبل إعادة المحاولة بعد إعادة التشغيل.
تُعاد محاولة الطلبات الفاشلة بشكل أسرع افتراضيًا من إنشاء الطلبات الناجحة.
عيّن `startupVerification: "off"` لتعطيل طلبات بدء التشغيل التلقائية، أو اضبط `startupVerificationCooldownHours`
إذا كنت تريد نافذة إعادة محاولة أقصر أو أطول.

ينفذ بدء التشغيل أيضًا مرور bootstrap محافظًا للتشفير تلقائيًا.
يحاول هذا المرور أولًا إعادة استخدام التخزين السري الحالي وهوية cross-signing الحالية، ويتجنب إعادة تعيين cross-signing ما لم تشغّل مسار إصلاح bootstrap صريحًا.

إذا اكتشف بدء التشغيل حالة bootstrap معطلة وكان `channels.matrix.password` مهيأً، فيمكن لـ OpenClaw محاولة مسار إصلاح أكثر صرامة.
إذا كان الجهاز الحالي موقّعًا بالفعل من المالك، فيحافظ OpenClaw على تلك الهوية بدلًا من إعادة تعيينها تلقائيًا.

الترقية من plugin Matrix العامة السابقة:

- يعيد OpenClaw تلقائيًا استخدام حساب Matrix نفسه وaccess token وهوية الجهاز نفسها متى أمكن.
- قبل تشغيل أي تغييرات ترحيل Matrix قابلة للتنفيذ، ينشئ OpenClaw أو يعيد استخدام لقطة استرداد ضمن `~/Backups/openclaw-migrations/`.
- إذا كنت تستخدم عدة حسابات Matrix، فقم بتعيين `channels.matrix.defaultAccount` قبل الترقية من تخطيط التخزين القديم المسطح حتى يعرف OpenClaw أي حساب يجب أن يستقبل هذه الحالة القديمة المشتركة.
- إذا كانت plugin السابقة تخزن مفتاح فك تشفير نسخة Matrix الاحتياطية لمفاتيح الغرف محليًا، فسيقوم بدء التشغيل أو `openclaw doctor --fix` باستيراده إلى تدفق مفتاح الاسترداد الجديد تلقائيًا.
- إذا تغيّر access token الخاص بـ Matrix بعد إعداد الترحيل، فإن بدء التشغيل يفحص الآن جذور تخزين sibling token-hash بحثًا عن حالة استعادة قديمة معلّقة قبل التخلي عن الاستعادة التلقائية للنسخ الاحتياطي.
- إذا تغيّر access token الخاص بـ Matrix لاحقًا لنفس الحساب وhomeserver والمستخدم، فإن OpenClaw يفضّل الآن إعادة استخدام جذر token-hash الموجود الأكثر اكتمالًا بدلًا من البدء من دليل حالة Matrix فارغ.
- عند بدء تشغيل البوابة التالي، تُستعاد مفاتيح الغرف المنسوخة احتياطيًا تلقائيًا إلى مخزن التشفير الجديد.
- إذا كانت plugin القديمة تحتوي على مفاتيح غرف محلية فقط لم تُنسخ احتياطيًا مطلقًا، فسيحذر OpenClaw بوضوح. لا يمكن تصدير تلك المفاتيح تلقائيًا من مخزن rust crypto السابق، لذلك قد يظل بعض السجل المشفر القديم غير متاح حتى يُستعاد يدويًا.
- راجع [ترحيل Matrix](/ar/install/migrating-matrix) لمعرفة تدفق الترقية الكامل والقيود وأوامر الاسترداد ورسائل الترحيل الشائعة.

تُنظَّم حالة التشغيل المشفرة ضمن جذور token-hash لكل حساب ولكل مستخدم في
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`.
يحتوي هذا الدليل على مخزن المزامنة (`bot-storage.json`) ومخزن التشفير (`crypto/`) وملف
مفتاح الاسترداد (`recovery-key.json`) ولقطة IndexedDB (`crypto-idb-snapshot.json`) وروابط
سلاسل الرسائل (`thread-bindings.json`) وحالة التحقق عند بدء التشغيل (`startup-verification.json`)
عندما تكون هذه الميزات قيد الاستخدام.
عندما يتغير token لكن تبقى هوية الحساب نفسها، يعيد OpenClaw استخدام أفضل
جذر موجود لذلك الثلاثي account/homeserver/user بحيث تبقى حالة المزامنة السابقة وحالة التشفير وروابط سلاسل الرسائل
وحالة التحقق عند بدء التشغيل مرئية.

### نموذج مخزن Node crypto

يستخدم E2EE في Matrix ضمن هذه plugin مسار Rust crypto الرسمي من `matrix-js-sdk` في Node.
ويتوقع هذا المسار وجود تخزين دائم قائم على IndexedDB إذا كنت تريد بقاء حالة التشفير بعد إعادة التشغيل.

يوفر OpenClaw ذلك حاليًا في Node من خلال:

- استخدام `fake-indexeddb` بوصفه واجهة IndexedDB shim التي تتوقعها SDK
- استعادة محتويات Rust crypto IndexedDB من `crypto-idb-snapshot.json` قبل `initRustCrypto`
- حفظ محتويات IndexedDB المحدثة مرة أخرى إلى `crypto-idb-snapshot.json` بعد التهيئة وأثناء التشغيل
- تسلسل استعادة اللقطة وحفظها مقابل `crypto-idb-snapshot.json` باستخدام قفل ملف استشاري حتى لا تتسابق استمرارية تشغيل البوابة وصيانة CLI على ملف اللقطة نفسه

هذا مجرد توافق/بنية تخزين، وليس تنفيذًا مخصصًا للتشفير.
ملف اللقطة حالة تشغيل حساسة ويُخزن بأذونات ملفات مقيدة.
وبموجب نموذج الأمان في OpenClaw، يكون مضيف البوابة ودليل الحالة المحلي لـ OpenClaw داخل حدود المشغّل الموثوقة بالفعل، لذلك فهذه مسألة متانة تشغيلية بالدرجة الأولى وليست حد ثقة بعيد منفصل.

تحسين مخطط له:

- إضافة دعم SecretRef لمواد مفاتيح Matrix الدائمة بحيث يمكن جلب مفاتيح الاسترداد وأسرار تشفير المخزن المرتبطة بها من مزودي الأسرار في OpenClaw بدلًا من الملفات المحلية فقط

## إدارة الملف الشخصي

حدّث الملف الشخصي الذاتي لـ Matrix للحساب المحدد باستخدام:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

أضف `--account <id>` عندما تريد استهداف حساب Matrix مسمىً صراحةً.

تقبل Matrix عناوين URL للصورة الرمزية من نوع `mxc://` مباشرةً. وعندما تمرر عنوان URL للصورة الرمزية من نوع `http://` أو `https://`، يقوم OpenClaw أولًا برفعه إلى Matrix ثم يخزن عنوان `mxc://` الناتج مرة أخرى في `channels.matrix.avatarUrl` (أو في تجاوز الحساب المحدد).

## إشعارات التحقق التلقائية

تنشر Matrix الآن إشعارات دورة حياة التحقق مباشرة داخل غرفة الرسائل الخاصة الصارمة الخاصة بالتحقق بوصفها رسائل `m.notice`.
ويشمل ذلك:

- إشعارات طلب التحقق
- إشعارات جاهزية التحقق (مع إرشادات صريحة "التحقق عبر الرموز التعبيرية")
- إشعارات بدء التحقق واكتماله
- تفاصيل SAS (الرموز التعبيرية والأرقام) عند توفرها

تُتتبَّع طلبات التحقق الواردة من عميل Matrix آخر وتُقبل تلقائيًا بواسطة OpenClaw.
وبالنسبة إلى تدفقات التحقق الذاتي، يبدأ OpenClaw أيضًا تدفق SAS تلقائيًا عندما يصبح التحقق بالرموز التعبيرية متاحًا ويؤكد جانبه الخاص.
أما بالنسبة إلى طلبات التحقق من مستخدم/جهاز Matrix آخر، فيقبل OpenClaw الطلب تلقائيًا ثم ينتظر متابعة تدفق SAS بشكل طبيعي.
ما يزال عليك مقارنة SAS بالرموز التعبيرية أو الأرقام في عميل Matrix لديك وتأكيد "They match" هناك لإكمال التحقق.

لا يقبل OpenClaw تلقائيًا التدفقات المكررة التي بدأها ذاتيًا بشكل أعمى. يتخطى بدء التشغيل إنشاء طلب جديد عندما يكون طلب التحقق الذاتي معلّقًا بالفعل.

لا تُمرَّر إشعارات البروتوكول/النظام الخاصة بالتحقق إلى مسار دردشة الوكيل، لذلك لا تنتج `NO_REPLY`.

### نظافة الأجهزة

يمكن أن تتراكم أجهزة Matrix القديمة التي يديرها OpenClaw على الحساب وتجعل الثقة في الغرف المشفرة أصعب في الفهم.
اعرضها باستخدام:

```bash
openclaw matrix devices list
```

أزل أجهزة OpenClaw-managed القديمة باستخدام:

```bash
openclaw matrix devices prune-stale
```

### إصلاح الغرفة المباشرة

إذا خرجت حالة الرسائل الخاصة عن المزامنة، فقد ينتهي الأمر بـ OpenClaw إلى الحصول على تعيينات `m.direct` قديمة تشير إلى غرف منفردة قديمة بدلًا من الرسالة الخاصة الحية. افحص التعيين الحالي لنظير باستخدام:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

وأصلحه باستخدام:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

يبقي الإصلاح منطق Matrix الخاص داخل plugin:

- يفضّل رسالة خاصة صارمة 1:1 تكون معيّنة بالفعل في `m.direct`
- وإلا فيعود إلى أي رسالة خاصة صارمة 1:1 منضم إليها حاليًا مع ذلك المستخدم
- وإذا لم توجد رسالة خاصة سليمة، ينشئ غرفة direct جديدة ويعيد كتابة `m.direct` للإشارة إليها

لا يحذف تدفق الإصلاح الغرف القديمة تلقائيًا. بل يختار فقط الرسالة الخاصة السليمة ويحدّث التعيين بحيث تستهدف عمليات إرسال Matrix الجديدة وإشعارات التحقق والتدفقات الأخرى للرسائل الخاصة الغرفة الصحيحة مرة أخرى.

## سلاسل الرسائل

تدعم Matrix سلاسل Matrix الأصلية لكل من الردود التلقائية وعمليات الإرسال عبر أداة الرسائل.

- `dm.sessionScope: "per-user"` (الافتراضي) يبقي توجيه الرسائل الخاصة في Matrix ضمن نطاق المرسل، لذلك يمكن لعدة غرف رسائل خاصة مشاركة جلسة واحدة عندما تُحل إلى النظير نفسه.
- `dm.sessionScope: "per-room"` يعزل كل غرفة رسائل خاصة في Matrix ضمن مفتاح جلسة خاص بها مع الاستمرار في استخدام فحوصات المصادقة وallowlist العادية للرسائل الخاصة.
- لا تزال روابط محادثات Matrix الصريحة تتقدم على `dm.sessionScope`، لذلك تحتفظ الغرف وسلاسل الرسائل المرتبطة بجلساتها الهدف المحددة.
- `threadReplies: "off"` يبقي الردود على المستوى الأعلى ويبقي الرسائل الواردة ضمن سلاسل الرسائل على جلسة الأصل.
- `threadReplies: "inbound"` يرد داخل سلسلة رسائل فقط عندما تكون الرسالة الواردة أصلًا ضمن تلك السلسلة.
- `threadReplies: "always"` يبقي ردود الغرف ضمن سلسلة رسائل متجذرة عند الرسالة المحفزة ويوجه تلك المحادثة عبر الجلسة ذات النطاق الخاص بسلسلة الرسائل المطابقة ابتداءً من أول رسالة محفزة.
- `dm.threadReplies` يتجاوز الإعداد الأعلى مستوى للرسائل الخاصة فقط. على سبيل المثال، يمكنك إبقاء سلاسل رسائل الغرف معزولة مع إبقاء الرسائل الخاصة مسطحة.
- تتضمن الرسائل الواردة ضمن سلاسل الرسائل الرسالة الجذرية للسلسلة كسياق إضافي للوكيل.
- ترث عمليات الإرسال عبر أداة الرسائل الآن سلسلة Matrix الحالية تلقائيًا عندما يكون الهدف هو الغرفة نفسها، أو الهدف نفسه لمستخدم الرسائل الخاصة، ما لم يُوفَّر `threadId` صريح.
- لا يُفعَّل إعادة استخدام هدف مستخدم الرسائل الخاصة للجلسة نفسها إلا عندما تثبت بيانات تعريف الجلسة الحالية أنه نفس نظير الرسائل الخاصة على حساب Matrix نفسه؛ وإلا يعود OpenClaw إلى التوجيه العادي ضمن نطاق المستخدم.
- عندما يرى OpenClaw أن غرفة رسائل خاصة في Matrix تتصادم مع غرفة رسائل خاصة أخرى على جلسة Matrix DM مشتركة نفسها، فإنه ينشر `m.notice` لمرة واحدة في تلك الغرفة مع مخرج الهروب `/focus` عندما تكون روابط سلاسل الرسائل مفعّلة ومع تلميح `dm.sessionScope`.
- تُدعَم روابط سلاسل الرسائل أثناء التشغيل لـ Matrix. تعمل الآن `/focus` و`/unfocus` و`/agents` و`/session idle` و`/session max-age` و`/acp spawn` المرتبط بسلسلة الرسائل في غرف Matrix والرسائل الخاصة.
- يؤدي `/focus` على مستوى أعلى لغرفة/رسالة خاصة Matrix إلى إنشاء سلسلة Matrix جديدة وربطها بالجلسة الهدف عندما تكون `threadBindings.spawnSubagentSessions=true`.
- يؤدي تشغيل `/focus` أو `/acp spawn --thread here` داخل سلسلة Matrix موجودة إلى ربط هذه السلسلة الحالية بدلًا من ذلك.

## روابط محادثات ACP

يمكن تحويل غرف Matrix والرسائل الخاصة وسلاسل Matrix الموجودة إلى مساحات عمل ACP دائمة دون تغيير سطح الدردشة.

تدفق المشغّل السريع:

- شغّل `/acp spawn codex --bind here` داخل الرسالة الخاصة أو الغرفة أو سلسلة الرسائل الموجودة في Matrix التي تريد الاستمرار في استخدامها.
- في رسالة خاصة أو غرفة Matrix على المستوى الأعلى، تبقى الرسالة الخاصة/الغرفة الحالية هي سطح الدردشة وتُوجَّه الرسائل المستقبلية إلى جلسة ACP التي تم إنشاؤها.
- داخل سلسلة Matrix موجودة، يربط `--bind here` تلك السلسلة الحالية في مكانها.
- يعيد `/new` و`/reset` تعيين جلسة ACP المرتبطة نفسها في مكانها.
- يغلق `/acp close` جلسة ACP ويزيل الربط.

ملاحظات:

- لا يؤدي `--bind here` إلى إنشاء سلسلة Matrix فرعية.
- لا تكون `threadBindings.spawnAcpSessions` مطلوبة إلا لـ `/acp spawn --thread auto|here`، حيث يحتاج OpenClaw إلى إنشاء سلسلة Matrix فرعية أو ربطها.

### تهيئة ربط سلاسل الرسائل

ترث Matrix القيم الافتراضية العامة من `session.threadBindings`، كما تدعم أيضًا تجاوزات لكل قناة:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

علامات إنشاء الروابط الخاصة بسلاسل Matrix اختيارية:

- عيّن `threadBindings.spawnSubagentSessions: true` للسماح لـ `/focus` على المستوى الأعلى بإنشاء سلاسل Matrix جديدة وربطها.
- عيّن `threadBindings.spawnAcpSessions: true` للسماح لـ `/acp spawn --thread auto|here` بربط جلسات ACP بسلاسل Matrix.

## التفاعلات

تدعم Matrix إجراءات التفاعل الصادرة، وإشعارات التفاعل الواردة، وتفاعلات الإقرار الواردة.

- تخضع أدوات التفاعل الصادرة إلى `channels["matrix"].actions.reactions`.
- يضيف `react` تفاعلًا إلى حدث Matrix محدد.
- يعرض `reactions` ملخص التفاعلات الحالي لحدث Matrix محدد.
- يؤدي `emoji=""` إلى إزالة تفاعلات حساب الروبوت نفسه على ذلك الحدث.
- يؤدي `remove: true` إلى إزالة تفاعل الرمز التعبيري المحدد فقط من حساب الروبوت.

يُحل نطاق تفاعلات الإقرار وفق ترتيب OpenClaw القياسي:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- الرجوع إلى الرمز التعبيري لهوية الوكيل

يُحل نطاق تفاعلات الإقرار بهذا الترتيب:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

يُحل وضع إشعارات التفاعل بهذا الترتيب:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- الافتراضي: `own`

السلوك الحالي:

- `reactionNotifications: "own"` يمرر أحداث `m.reaction` المضافة عندما تستهدف رسائل Matrix التي ألّفها الروبوت.
- `reactionNotifications: "off"` يعطل أحداث نظام التفاعل.
- لا تزال إزالة التفاعلات لا تُركَّب كأحداث نظام لأن Matrix تعرضها كعمليات حذف، وليس كعمليات إزالة `m.reaction` مستقلة.

## سياق السجل

- يتحكم `channels.matrix.historyLimit` في عدد رسائل الغرفة الحديثة التي تُضمَّن بوصفها `InboundHistory` عندما تحفز رسالة غرفة Matrix الوكيل.
- ويرجع إلى `messages.groupChat.historyLimit`. وإذا لم يُضبط أي منهما، تكون القيمة الافتراضية الفعلية `0`، لذلك لا تُخزَّن رسائل الغرف المقيدة بالذكر مؤقتًا. اضبط `0` للتعطيل.
- يكون سجل غرف Matrix خاصًا بالغرف فقط. وتستمر الرسائل الخاصة باستخدام سجل الجلسات العادي.
- سجل غرف Matrix خاص بالعناصر المعلّقة فقط: يخزّن OpenClaw رسائل الغرف التي لم تحفز ردًا بعد، ثم يلتقط تلك النافذة عندما يصل ذكر أو محفز آخر.
- لا تُضمَّن رسالة التحفيز الحالية في `InboundHistory`؛ بل تبقى في متن الإدخال الرئيسي لتلك الدورة.
- تعيد محاولات الحدث نفسه في Matrix استخدام لقطة السجل الأصلية بدلًا من الانجراف إلى رسائل غرف أحدث.

## رؤية السياق

تدعم Matrix عنصر التحكم المشترك `contextVisibility` لسياق الغرفة التكميلي مثل نص الرد المستجلب وجذور سلاسل الرسائل والسجل المعلّق.

- `contextVisibility: "all"` هو الافتراضي. يُحتفظ بالسياق التكميلي كما وصل.
- `contextVisibility: "allowlist"` يرشّح السياق التكميلي إلى المرسلين المسموح لهم بموجب فحوصات allowlist النشطة للغرفة/المستخدم.
- `contextVisibility: "allowlist_quote"` يعمل مثل `allowlist`، لكنه يحتفظ مع ذلك برد مقتبس صريح واحد.

يؤثر هذا الإعداد في رؤية السياق التكميلي، وليس في ما إذا كانت الرسالة الواردة نفسها يمكن أن تحفز ردًا.
ولا يزال ترخيص التحفيز يأتي من `groupPolicy` و`groups` و`groupAllowFrom` وإعدادات سياسة الرسائل الخاصة.

## مثال على سياسة الرسائل الخاصة والغرف

```json5
{
  channels: {
    matrix: {
      dm: {
        policy: "allowlist",
        allowFrom: ["@admin:example.org"],
        threadReplies: "off",
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

راجع [Groups](/ar/channels/groups) لمعرفة سلوك التقييد بالذكر وallowlist.

مثال pairing لرسائل Matrix الخاصة:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

إذا استمر مستخدم Matrix غير معتمد في مراسلتك قبل الموافقة، يعيد OpenClaw استخدام رمز pairing المعلّق نفسه وقد يرسل رد تذكير مرة أخرى بعد فترة تهدئة قصيرة بدلًا من إصدار رمز جديد.

راجع [Pairing](/ar/channels/pairing) لمعرفة تدفق pairing المشترك للرسائل الخاصة وتخطيط التخزين.

## موافقات exec

يمكن لـ Matrix أن تعمل كعميل موافقات exec لحساب Matrix.

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (اختياري؛ يرجع إلى `channels.matrix.dm.allowFrom`)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`، الافتراضي: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

يجب أن يكون الموافقون معرّفات مستخدمي Matrix مثل `@owner:example.org`. تفعّل Matrix موافقات exec الأصلية تلقائيًا عندما تكون `enabled` غير مضبوطة أو تساوي `"auto"` ويمكن تحليل موافق واحد على الأقل، إما من `execApprovals.approvers` أو من `channels.matrix.dm.allowFrom`. عيّن `enabled: false` لتعطيل Matrix كعميل موافقة أصلي صراحةً. وبخلاف ذلك، تعود طلبات الموافقة إلى مسارات الموافقة المهيأة الأخرى أو إلى سياسة الموافقة الاحتياطية لـ exec.

التوجيه الأصلي لـ Matrix خاص بـ exec فقط حاليًا:

- يتحكم `channels.matrix.execApprovals.*` في التوجيه الأصلي للرسائل الخاصة/القنوات لموافقات exec فقط.
- ما تزال موافقات plugin تستخدم `/approve` المشترك في المحادثة نفسها بالإضافة إلى أي توجيه `approvals.plugin` مهيأ.
- ما تزال Matrix قادرة على إعادة استخدام `channels.matrix.dm.allowFrom` لتفويض موافقات plugin عندما تتمكن من استنتاج الموافقين بأمان، لكنها لا تعرض مسار توزيع أصلي منفصل لموافقات plugin عبر الرسائل الخاصة/القنوات.

قواعد التسليم:

- `target: "dm"` يرسل مطالبات الموافقة إلى الرسائل الخاصة للموافقين
- `target: "channel"` يعيد إرسال المطالبة إلى غرفة أو رسالة Matrix الأصلية
- `target: "both"` يرسل إلى الرسائل الخاصة للموافقين وإلى غرفة أو رسالة Matrix الأصلية

تزرع مطالبات الموافقة في Matrix اختصارات التفاعل على رسالة الموافقة الأساسية:

- `✅` = السماح مرة واحدة
- `❌` = الرفض
- `♾️` = السماح دائمًا عندما يكون هذا القرار مسموحًا بموجب سياسة exec الفعلية

يمكن للموافقين التفاعل على تلك الرسالة أو استخدام أوامر الشرطة المائلة الاحتياطية: `/approve <id> allow-once` أو `/approve <id> allow-always` أو `/approve <id> deny`.

لا يمكن الموافقة أو الرفض إلا من قبل الموافقين الذين تم تحليلهم. ويتضمن التسليم عبر القناة نص الأمر، لذلك فعّل `channel` أو `both` فقط في الغرف الموثوقة.

تعيد مطالبات الموافقة في Matrix استخدام مخطط الموافقة الأساسي المشترك. والسطح الأصلي الخاص بـ Matrix هو مجرد وسيلة نقل لموافقات exec: توجيه الغرف/الرسائل الخاصة وسلوك إرسال/تحديث/حذف الرسائل.

تجاوز لكل حساب:

- `channels.matrix.accounts.<account>.execApprovals`

المستندات ذات الصلة: [Exec approvals](/ar/tools/exec-approvals)

## مثال على الحسابات المتعددة

```json5
{
  channels: {
    matrix: {
      enabled: true,
      defaultAccount: "assistant",
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_xxx",
          encryption: true,
        },
        alerts: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_xxx",
          dm: {
            policy: "allowlist",
            allowFrom: ["@ops:example.org"],
            threadReplies: "off",
          },
        },
      },
    },
  },
}
```

تعمل قيم `channels.matrix` ذات المستوى الأعلى كقيم افتراضية للحسابات المسماة ما لم يتجاوزها الحساب.
يمكنك تحديد إدخالات الغرف الموروثة لحساب Matrix واحد باستخدام `groups.<room>.account` (أو `rooms.<room>.account` القديم).
تبقى الإدخالات التي لا تحتوي على `account` مشتركة عبر جميع حسابات Matrix، ولا تزال الإدخالات التي تحتوي على `account: "default"` تعمل عندما يكون الحساب الافتراضي مهيأً مباشرة على `channels.matrix.*` الأعلى مستوى.
لا تؤدي القيم الافتراضية المشتركة الجزئية للمصادقة إلى إنشاء حساب افتراضي ضمني منفصل بمفردها. لا يقوم OpenClaw بتركيب الحساب `default` الأعلى مستوى إلا عندما تكون لهذا الافتراضي مصادقة حديثة (`homeserver` مع `accessToken`، أو `homeserver` مع `userId` و`password`)؛ ويمكن للحسابات المسماة أن تبقى قابلة للاكتشاف من `homeserver` مع `userId` عندما تلبي بيانات الاعتماد المؤقتة المصادقة لاحقًا.
إذا كان لدى Matrix بالفعل حساب مسمى واحد فقط بالضبط، أو كان `defaultAccount` يشير إلى مفتاح حساب مسمى موجود، فإن ترقية الإصلاح/الإعداد من حساب واحد إلى عدة حسابات تحافظ على ذلك الحساب بدلًا من إنشاء إدخال `accounts.default` جديد. تنتقل فقط مفاتيح مصادقة/bootstrap الخاصة بـ Matrix إلى ذلك الحساب المُرقّى؛ أما مفاتيح سياسة التسليم المشتركة فتبقى على المستوى الأعلى.
عيّن `defaultAccount` عندما تريد أن يفضّل OpenClaw حساب Matrix مسمىً واحدًا للتوجيه الضمني والفحص وعمليات CLI.
إذا هيأت عدة حسابات مسماة، فقم بتعيين `defaultAccount` أو مرر `--account <id>` لأوامر CLI التي تعتمد على اختيار الحساب الضمني.
مرر `--account <id>` إلى `openclaw matrix verify ...` و`openclaw matrix devices ...` عندما تريد تجاوز هذا الاختيار الضمني لأمر واحد.

## homeserverات الخاصة/ضمن LAN

افتراضيًا، يحظر OpenClaw homeserverات Matrix الخاصة/الداخلية للحماية من SSRF ما لم
تقم بالاشتراك الصريح لكل حساب.

إذا كان homeserver لديك يعمل على localhost أو عنوان LAN/Tailscale IP أو اسم مضيف داخلي، فقم بتمكين
`network.dangerouslyAllowPrivateNetwork` لذلك الحساب في Matrix:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      network: {
        dangerouslyAllowPrivateNetwork: true,
      },
      accessToken: "syt_internal_xxx",
    },
  },
}
```

مثال إعداد CLI:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

يسمح هذا الاشتراك الاختياري فقط بالأهداف الخاصة/الداخلية الموثوقة. أما homeserverات
النص الواضح العامة مثل `http://matrix.example.org:8008` فتبقى محظورة. ويفضَّل استخدام `https://` كلما أمكن.

## تمرير حركة Matrix عبر proxy

إذا كان نشر Matrix لديك يحتاج إلى proxy HTTP(S) صريح للخروج، فعيّن `channels.matrix.proxy`:

```json5
{
  channels: {
    matrix: {
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
    },
  },
}
```

يمكن للحسابات المسماة تجاوز القيمة الافتراضية الأعلى مستوى باستخدام `channels.matrix.accounts.<id>.proxy`.
ويستخدم OpenClaw إعداد proxy نفسه لحركة Matrix أثناء التشغيل ولفحوصات حالة الحساب.

## تحليل الأهداف

تقبل Matrix أشكال الأهداف التالية في أي موضع يطلب منك فيه OpenClaw هدف غرفة أو مستخدم:

- المستخدمون: `@user:server` أو `user:@user:server` أو `matrix:user:@user:server`
- الغرف: `!room:server` أو `room:!room:server` أو `matrix:room:!room:server`
- الأسماء المستعارة: `#alias:server` أو `channel:#alias:server` أو `matrix:channel:#alias:server`

يستخدم البحث الحي في الدليل حساب Matrix المسجل دخوله:

- تستعلم عمليات البحث عن المستخدمين دليل مستخدمي Matrix على ذلك homeserver.
- تقبل عمليات البحث عن الغرف معرّفات الغرف والأسماء المستعارة الصريحة مباشرة، ثم تعود إلى البحث في أسماء الغرف المنضم إليها لذلك الحساب.
- إن البحث في أسماء الغرف المنضم إليها هو أفضل جهد. وإذا تعذر تحليل اسم غرفة إلى معرّف أو اسم مستعار، فسيُتجاهل في تحليل allowlist أثناء التشغيل.

## مرجع التهيئة

- `enabled`: تمكين القناة أو تعطيلها.
- `name`: تسمية اختيارية للحساب.
- `defaultAccount`: معرّف الحساب المفضل عند تهيئة عدة حسابات Matrix.
- `homeserver`: عنوان URL لـ homeserver، مثل `https://matrix.example.org`.
- `network.dangerouslyAllowPrivateNetwork`: السماح لهذا الحساب في Matrix بالاتصال بـ homeserverات خاصة/داخلية. فعّل هذا عندما يُحل homeserver إلى `localhost` أو عنوان LAN/Tailscale IP أو مضيف داخلي مثل `matrix-synapse`.
- `proxy`: عنوان URL اختياري لـ proxy HTTP(S) لحركة Matrix. ويمكن للحسابات المسماة تجاوز القيمة الافتراضية الأعلى مستوى باستخدام `proxy` الخاص بها.
- `userId`: معرّف مستخدم Matrix الكامل، مثل `@bot:example.org`.
- `accessToken`: access token للمصادقة المعتمدة على token. القيم النصية الصريحة وقيم SecretRef مدعومة في `channels.matrix.accessToken` و`channels.matrix.accounts.<id>.accessToken` عبر مزودي env/file/exec. راجع [إدارة الأسرار](/ar/gateway/secrets).
- `password`: كلمة المرور لتسجيل الدخول المعتمد على كلمة المرور. القيم النصية الصريحة وقيم SecretRef مدعومة.
- `deviceId`: معرّف جهاز Matrix صريح.
- `deviceName`: اسم عرض الجهاز لتسجيل الدخول بكلمة المرور.
- `avatarUrl`: عنوان URL مخزّن للصورة الذاتية لمزامنة الملف الشخصي وتحديثات `set-profile`.
- `initialSyncLimit`: حد أحداث المزامنة عند بدء التشغيل.
- `encryption`: تمكين E2EE.
- `allowlistOnly`: فرض سلوك allowlist فقط للرسائل الخاصة والغرف.
- `allowBots`: السماح بالرسائل من حسابات OpenClaw Matrix الأخرى المهيأة (`true` أو `"mentions"`).
- `groupPolicy`: `open` أو `allowlist` أو `disabled`.
- `contextVisibility`: وضع رؤية سياق الغرفة التكميلي (`all` أو `allowlist` أو `allowlist_quote`).
- `groupAllowFrom`: allowlist لمعرّفات المستخدمين لحركة الغرف.
- يجب أن تكون إدخالات `groupAllowFrom` معرّفات مستخدمي Matrix كاملة. وتُتجاهل الأسماء غير المحللة أثناء التشغيل.
- `historyLimit`: الحد الأقصى لرسائل الغرفة التي تُضمَّن كسياق سجل للمجموعة. ويرجع إلى `messages.groupChat.historyLimit`؛ وإذا لم يُضبط أي منهما، تكون القيمة الافتراضية الفعلية `0`. اضبط `0` للتعطيل.
- `replyToMode`: `off` أو `first` أو `all` أو `batched`.
- `markdown`: تهيئة اختيارية لتصيير Markdown في نص Matrix الصادر.
- `streaming`: `off` (الافتراضي) أو `partial` أو `quiet` أو `true` أو `false`. يعمل `partial` و`true` على تمكين تحديثات المسودة القائمة على المعاينة أولًا باستخدام رسائل Matrix النصية العادية. ويستخدم `quiet` إشعارات معاينة غير مُرسِلة للإشعار من أجل إعدادات push-rule المستضافة ذاتيًا.
- `blockStreaming`: تؤدي القيمة `true` إلى تمكين رسائل تقدم منفصلة لكتل المساعد المكتملة أثناء نشاط بث معاينة المسودة.
- `threadReplies`: `off` أو `inbound` أو `always`.
- `threadBindings`: تجاوزات لكل قناة لتوجيه الجلسات المرتبطة بسلاسل الرسائل ودورة حياتها.
- `startupVerification`: وضع طلب التحقق الذاتي التلقائي عند بدء التشغيل (`if-unverified` أو `off`).
- `startupVerificationCooldownHours`: فترة التهدئة قبل إعادة محاولة طلبات التحقق التلقائي عند بدء التشغيل.
- `textChunkLimit`: حجم تجزئة الرسائل الصادرة.
- `chunkMode`: `length` أو `newline`.
- `responsePrefix`: بادئة رسائل اختيارية للردود الصادرة.
- `ackReaction`: تجاوز اختياري لتفاعل الإقرار لهذه القناة/الحساب.
- `ackReactionScope`: تجاوز اختياري لنطاق تفاعل الإقرار (`group-mentions` أو `group-all` أو `direct` أو `all` أو `none` أو `off`).
- `reactionNotifications`: وضع إشعارات التفاعل الواردة (`own` أو `off`).
- `mediaMaxMb`: حد حجم الوسائط بالميغابايت لمعالجة وسائط Matrix. ينطبق على الإرسال الصادر ومعالجة الوسائط الواردة.
- `autoJoin`: سياسة الانضمام التلقائي للدعوات (`always` أو `allowlist` أو `off`). الافتراضي: `off`. ينطبق هذا على دعوات Matrix عمومًا، بما في ذلك دعوات الرسائل الخاصة، وليس فقط دعوات الغرف/المجموعات. يتخذ OpenClaw هذا القرار وقت الدعوة، قبل أن يتمكن من تصنيف الغرفة المنضم إليها بشكل موثوق على أنها رسالة خاصة أو مجموعة.
- `autoJoinAllowlist`: الغرف/الأسماء المستعارة المسموح بها عندما تكون `autoJoin` مساوية لـ `allowlist`. تُحل إدخالات الأسماء المستعارة إلى معرّفات غرف أثناء التعامل مع الدعوة؛ ولا يثق OpenClaw بحالة الاسم المستعار التي تدّعيها الغرفة المدعوة.
- `dm`: كتلة سياسة الرسائل الخاصة (`enabled` أو `policy` أو `allowFrom` أو `sessionScope` أو `threadReplies`).
- `dm.policy`: يتحكم في الوصول إلى الرسائل الخاصة بعد أن ينضم OpenClaw إلى الغرفة ويصنفها على أنها رسالة خاصة. ولا يغيّر ما إذا كانت الدعوة تُضم تلقائيًا.
- يجب أن تكون إدخالات `dm.allowFrom` معرّفات مستخدمي Matrix كاملة ما لم تكن قد حللتها بالفعل عبر البحث الحي في الدليل.
- `dm.sessionScope`: `per-user` (الافتراضي) أو `per-room`. استخدم `per-room` عندما تريد أن تحتفظ كل غرفة رسائل خاصة في Matrix بسياق منفصل حتى لو كان النظير نفسه.
- `dm.threadReplies`: تجاوز سياسة سلاسل الرسائل الخاص بالرسائل الخاصة فقط (`off` أو `inbound` أو `always`). وهو يتجاوز إعداد `threadReplies` الأعلى مستوى لكل من موضع الرد وعزل الجلسة في الرسائل الخاصة.
- `execApprovals`: تسليم موافقات exec الأصلية في Matrix (`enabled` أو `approvers` أو `target` أو `agentFilter` أو `sessionFilter`).
- `execApprovals.approvers`: معرّفات مستخدمي Matrix المسموح لهم بالموافقة على طلبات exec. وهو اختياري عندما يحدد `dm.allowFrom` الموافقين بالفعل.
- `execApprovals.target`: `dm | channel | both` (الافتراضي: `dm`).
- `accounts`: تجاوزات مسماة لكل حساب. تعمل قيم `channels.matrix` الأعلى مستوى كقيم افتراضية لهذه الإدخالات.
- `groups`: خريطة سياسة لكل غرفة. يفضَّل استخدام معرّفات الغرف أو الأسماء المستعارة؛ وتُتجاهل أسماء الغرف غير المحللة أثناء التشغيل. تستخدم هوية الجلسة/المجموعة معرّف الغرفة الثابت بعد التحليل، بينما تستمر التسميات المقروءة للبشر في القدوم من أسماء الغرف.
- `groups.<room>.account`: تقييد إدخال غرفة موروث واحد إلى حساب Matrix محدد في إعدادات الحسابات المتعددة.
- `groups.<room>.allowBots`: تجاوز على مستوى الغرفة للمرسلين من الروبوتات المهيأة (`true` أو `"mentions"`).
- `groups.<room>.users`: allowlist للمرسلين على مستوى الغرفة.
- `groups.<room>.tools`: تجاوزات السماح/المنع للأدوات على مستوى الغرفة.
- `groups.<room>.autoReply`: تجاوز التقييد بالذكر على مستوى الغرفة. تعني `true` تعطيل متطلبات الذكر لتلك الغرفة؛ وتعني `false` فرضها مرة أخرى.
- `groups.<room>.skills`: عامل تصفية Skills اختياري على مستوى الغرفة.
- `groups.<room>.systemPrompt`: مقتطف system prompt اختياري على مستوى الغرفة.
- `rooms`: اسم مستعار قديم لـ `groups`.
- `actions`: تقييد الأدوات لكل إجراء (`messages` أو `reactions` أو `pins` أو `profile` أو `memberInfo` أو `channelInfo` أو `verification`).

## ذو صلة

- [نظرة عامة على القنوات](/ar/channels) — جميع القنوات المدعومة
- [Pairing](/ar/channels/pairing) — مصادقة الرسائل الخاصة وتدفق pairing
- [Groups](/ar/channels/groups) — سلوك الدردشة الجماعية والتقييد بالذكر
- [توجيه القنوات](/ar/channels/channel-routing) — توجيه الجلسات للرسائل
- [الأمان](/ar/gateway/security) — نموذج الوصول والتقوية
