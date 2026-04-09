---
read_when:
    - إعداد Matrix في OpenClaw
    - تكوين التشفير التام بين الطرفين E2EE والتحقق في Matrix
summary: حالة دعم Matrix وإعداده وأمثلة التكوين
title: Matrix
x-i18n:
    generated_at: "2026-04-09T01:30:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 28fc13c7620c1152200315ae69c94205da6de3180c53c814dd8ce03b5cb1758f
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix هو إضافة قناة مدمجة لـ OpenClaw.
ويستخدم `matrix-js-sdk` الرسمي ويدعم الرسائل المباشرة، والغرف، والخيوط، والوسائط، والتفاعلات، واستطلاعات الرأي، والموقع، وE2EE.

## الإضافة المدمجة

يأتي Matrix كإضافة مدمجة في إصدارات OpenClaw الحالية، لذلك لا تحتاج
البنيات المعبأة العادية إلى تثبيت منفصل.

إذا كنت تستخدم إصدارًا أقدم أو تثبيتًا مخصصًا يستبعد Matrix، فقم بتثبيته
يدويًا:

التثبيت من npm:

```bash
openclaw plugins install @openclaw/matrix
```

التثبيت من نسخة محلية:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

راجع [Plugins](/ar/tools/plugin) لمعرفة سلوك الإضافات وقواعد التثبيت.

## الإعداد

1. تأكد من توفر إضافة Matrix.
   - إصدارات OpenClaw الحالية المعبأة تتضمنها بالفعل.
   - يمكن للتثبيتات الأقدم/المخصصة إضافتها يدويًا بالأوامر أعلاه.
2. أنشئ حساب Matrix على الخادم المنزلي الخاص بك.
3. كوّن `channels.matrix` باستخدام أحد الخيارين:
   - `homeserver` + `accessToken`، أو
   - `homeserver` + `userId` + `password`.
4. أعد تشغيل البوابة.
5. ابدأ رسالة مباشرة مع البوت أو ادعه إلى غرفة.
   - تعمل دعوات Matrix الجديدة فقط عندما يسمح `channels.matrix.autoJoin` بذلك.

مسارات الإعداد التفاعلية:

```bash
openclaw channels add
openclaw configure --section channels
```

يطلب معالج Matrix ما يلي:

- عنوان URL للخادم المنزلي
- طريقة المصادقة: رمز وصول أو كلمة مرور
- معرّف المستخدم (لمصادقة كلمة المرور فقط)
- اسم جهاز اختياري
- ما إذا كنت تريد تمكين E2EE
- ما إذا كنت تريد تكوين الوصول إلى الغرف والانضمام التلقائي للدعوات

سلوكيات المعالج الأساسية:

- إذا كانت متغيرات البيئة الخاصة بمصادقة Matrix موجودة بالفعل ولم يكن لدى ذلك الحساب مصادقة محفوظة بالفعل في التكوين، فسيعرض المعالج اختصارًا لاستخدام البيئة للإبقاء على المصادقة في متغيرات البيئة.
- تتم تسوية أسماء الحسابات إلى معرّف الحساب. على سبيل المثال، يتحول `Ops Bot` إلى `ops-bot`.
- تقبل إدخالات قائمة السماح للرسائل المباشرة `@user:server` مباشرة؛ أما أسماء العرض فلا تعمل إلا عندما يعثر البحث الحي في الدليل على تطابق واحد دقيق.
- تقبل إدخالات قائمة السماح للغرف معرّفات الغرف والأسماء المستعارة مباشرة. يفضل استخدام `!room:server` أو `#alias:server`؛ ويتم تجاهل الأسماء غير المحلولة وقت التشغيل بواسطة دقة قائمة السماح.
- في وضع قائمة السماح للانضمام التلقائي للدعوات، استخدم فقط أهداف الدعوة الثابتة: `!roomId:server` أو `#alias:server` أو `*`. تُرفض أسماء الغرف العادية.
- لحل أسماء الغرف قبل الحفظ، استخدم `openclaw channels resolve --channel matrix "Project Room"`.

<Warning>
القيمة الافتراضية لـ `channels.matrix.autoJoin` هي `off`.

إذا تركته بدون تعيين، فلن ينضم البوت إلى الغرف المدعو إليها أو الدعوات الجديدة على نمط الرسائل المباشرة، لذلك لن يظهر في المجموعات الجديدة أو الرسائل المباشرة المدعو إليها إلا إذا انضممت يدويًا أولًا.

عيّن `autoJoin: "allowlist"` مع `autoJoinAllowlist` لتقييد الدعوات التي يقبلها، أو عيّن `autoJoin: "always"` إذا كنت تريد أن ينضم إلى كل دعوة.

في وضع `allowlist`، لا يقبل `autoJoinAllowlist` إلا `!roomId:server` أو `#alias:server` أو `*`.
</Warning>

مثال على قائمة السماح:

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

إعداد حد أدنى قائم على الرمز:

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

إعداد قائم على كلمة المرور (يتم تخزين الرمز مؤقتًا بعد تسجيل الدخول):

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

يخزن Matrix بيانات الاعتماد المؤقتة في `~/.openclaw/credentials/matrix/`.
ويستخدم الحساب الافتراضي `credentials.json`؛ بينما تستخدم الحسابات المسماة `credentials-<account>.json`.
وعندما توجد بيانات اعتماد مخزنة مؤقتًا هناك، يتعامل OpenClaw مع Matrix على أنه مكوَّن من أجل الإعداد وdoctor واكتشاف حالة القناة حتى إذا لم تكن المصادقة الحالية مضبوطة مباشرة في التكوين.

المعادِلات من متغيرات البيئة (تُستخدم عندما لا يكون مفتاح التكوين معيّنًا):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

للحسابات غير الافتراضية، استخدم متغيرات البيئة الخاصة بنطاق الحساب:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

مثال للحساب `ops`:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

وبالنسبة إلى معرّف الحساب الموحّد `ops-bot`، استخدم:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

يقوم Matrix بتهريب علامات الترقيم في معرّفات الحسابات لإبقاء متغيرات البيئة المحددة بالنطاق خالية من التعارضات.
فعلى سبيل المثال، يتحول `-` إلى `_X2D_`، لذلك يتحول `ops-prod` إلى `MATRIX_OPS_X2D_PROD_*`.

لا يعرض المعالج التفاعلي اختصار متغيرات البيئة إلا عندما تكون متغيرات بيئة المصادقة هذه موجودة بالفعل، ولا يكون لدى الحساب المحدد مصادقة Matrix محفوظة بالفعل في التكوين.

## مثال على التكوين

هذا تكوين أساسي عملي يتضمن اقتران الرسائل المباشرة، وقائمة سماح للغرف، وتمكين E2EE:

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

ينطبق `autoJoin` على جميع دعوات Matrix، بما في ذلك الدعوات على نمط الرسائل المباشرة. لا يستطيع OpenClaw
تصنيف الغرفة المدعو إليها بشكل موثوق على أنها رسالة مباشرة أو مجموعة وقت الدعوة، لذلك تمر جميع الدعوات عبر `autoJoin`
أولًا. ويُطبَّق `dm.policy` بعد انضمام البوت وتصنيف الغرفة على أنها رسالة مباشرة.

## معاينات البث

بث الردود في Matrix يتم تمكينه اختياريًا.

عيّن `channels.matrix.streaming` إلى `"partial"` عندما تريد أن يرسل OpenClaw معاينة حية واحدة
للرد، ويحرر تلك المعاينة في مكانها أثناء قيام النموذج بإنشاء النص، ثم ينهيها عندما
يكتمل الرد:

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
- `streaming: "partial"` ينشئ رسالة معاينة واحدة قابلة للتحرير لكتلة المساعد الحالية باستخدام رسائل Matrix النصية العادية. يحافظ ذلك على سلوك الإشعار القديم في Matrix الذي يعتمد على المعاينة أولًا، لذلك قد تُظهر العملاء القياسية إشعارًا عند أول نص معاينة متدفق بدلًا من الكتلة المكتملة.
- `streaming: "quiet"` ينشئ إشعار معاينة هادئًا واحدًا قابلاً للتحرير لكتلة المساعد الحالية. استخدم هذا فقط عندما تكون قد كوّنت أيضًا قواعد دفع للمستلمين من أجل تعديلات المعاينة النهائية.
- `blockStreaming: true` يفعّل رسائل تقدم منفصلة في Matrix. عند تمكين بث المعاينة، يحتفظ Matrix بالمسودة الحية للكتلة الحالية ويحافظ على الكتل المكتملة كرسائل منفصلة.
- عند تشغيل بث المعاينة وإيقاف `blockStreaming`، يقوم Matrix بتحرير المسودة الحية في مكانها وينهي الحدث نفسه عندما تنتهي الكتلة أو الدور.
- إذا لم تعد المعاينة تلائم حدث Matrix واحدًا، يوقف OpenClaw بث المعاينة ويعود إلى التسليم النهائي العادي.
- تستمر ردود الوسائط في إرسال المرفقات بشكل طبيعي. وإذا لم يعد من الممكن إعادة استخدام معاينة قديمة بأمان، يقوم OpenClaw بحذفها قبل إرسال رد الوسائط النهائي.
- تتطلب تعديلات المعاينة استدعاءات إضافية إلى Matrix API. اترك البث متوقفًا إذا كنت تريد السلوك الأكثر تحفظًا فيما يتعلق بحدود المعدل.

لا يقوم `blockStreaming` بتمكين معاينات المسودات بمفرده.
استخدم `streaming: "partial"` أو `streaming: "quiet"` لتعديلات المعاينة؛ ثم أضف `blockStreaming: true` فقط إذا كنت تريد أيضًا أن تظل كتل المساعد المكتملة مرئية كرسائل تقدم منفصلة.

إذا كنت تحتاج إلى إشعارات Matrix القياسية بدون قواعد دفع مخصصة، فاستخدم `streaming: "partial"` لسلوك المعاينة أولًا أو اترك `streaming` متوقفًا للتسليم النهائي فقط. مع `streaming: "off"`:

- `blockStreaming: true` يرسل كل كتلة مكتملة كرسالة Matrix عادية مُشعِرة.
- `blockStreaming: false` يرسل فقط الرد النهائي المكتمل كرسالة Matrix عادية مُشعِرة.

### قواعد الدفع المستضافة ذاتيًا للمعاينات النهائية الهادئة

إذا كنت تشغّل بنية Matrix الخاصة بك وتريد أن تُشعِر المعاينات الهادئة فقط عند اكتمال كتلة أو
رد نهائي، فعيّن `streaming: "quiet"` وأضف قاعدة دفع لكل مستخدم لتعديلات المعاينة النهائية.

يكون هذا عادة إعدادًا على مستوى المستخدم المستلم، وليس تغييرًا عامًا في تكوين الخادم المنزلي:

خريطة سريعة قبل أن تبدأ:

- المستخدم المستلم = الشخص الذي ينبغي أن يتلقى الإشعار
- مستخدم البوت = حساب Matrix الخاص بـ OpenClaw الذي يرسل الرد
- استخدم رمز وصول المستخدم المستلم في استدعاءات API أدناه
- طابق `sender` في قاعدة الدفع مع MXID الكامل لمستخدم البوت

1. كوّن OpenClaw لاستخدام المعاينات الهادئة:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. تأكد من أن حساب المستلم يتلقى بالفعل إشعارات دفع Matrix العادية. لا تعمل قواعد
   المعاينة الهادئة إلا إذا كان لدى ذلك المستخدم بالفعل pushers/أجهزة تعمل.

3. احصل على رمز وصول المستخدم المستلم.
   - استخدم رمز المستخدم المتلقي، وليس رمز البوت.
   - تكون إعادة استخدام رمز جلسة عميل موجودة هي الأسهل عادة.
   - إذا كنت بحاجة إلى إنشاء رمز جديد، يمكنك تسجيل الدخول عبر Matrix Client-Server API القياسي:

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

4. تحقق من أن حساب المستلم لديه بالفعل pushers:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

إذا أعاد هذا الاستدعاء عدم وجود pushers/أجهزة نشطة، فأصلِح إشعارات Matrix العادية أولًا قبل إضافة
قاعدة OpenClaw أدناه.

يضع OpenClaw علامة على تعديلات المعاينة النصية النهائية فقط باستخدام:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. أنشئ قاعدة دفع من نوع override لكل حساب مستلم ينبغي أن يتلقى هذه الإشعارات:

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

- `https://matrix.example.org`: عنوان URL الأساسي للخادم المنزلي لديك
- `$USER_ACCESS_TOKEN`: رمز وصول المستخدم المستلم
- `openclaw-finalized-preview-botname`: معرّف قاعدة فريد لهذا البوت لهذا المستخدم المستلم
- `@bot:example.org`: MXID بوت Matrix الخاص بـ OpenClaw لديك، وليس MXID المستخدم المستلم

مهم لإعدادات البوتات المتعددة:

- تُفهرس قواعد الدفع باستخدام `ruleId`. تؤدي إعادة تشغيل `PUT` على معرّف القاعدة نفسه إلى تحديث تلك القاعدة الواحدة.
- إذا كان ينبغي لمستخدم مستلم واحد أن يتلقى إشعارات لعدة حسابات بوت Matrix تابعة لـ OpenClaw، فأنشئ قاعدة واحدة لكل بوت مع معرّف قاعدة فريد لكل تطابق مرسل.
- نمط بسيط هو `openclaw-finalized-preview-<botname>`، مثل `openclaw-finalized-preview-ops` أو `openclaw-finalized-preview-support`.

يتم تقييم القاعدة مقابل مرسل الحدث:

- قم بالمصادقة باستخدام رمز المستخدم المستلم
- طابق `sender` مع MXID بوت OpenClaw

6. تحقق من وجود القاعدة:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. اختبر ردًا متدفقًا. في الوضع الهادئ، ينبغي أن تُظهر الغرفة معاينة مسودة هادئة وأن
   يُرسل التعديل النهائي في مكانه إشعارًا واحدًا عند انتهاء الكتلة أو الدور.

إذا احتجت إلى إزالة القاعدة لاحقًا، فاحذف معرّف القاعدة نفسه باستخدام رمز المستخدم المستلم:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

ملاحظات:

- أنشئ القاعدة باستخدام رمز وصول المستخدم المستلم، وليس رمز البوت.
- تُدرج قواعد `override` المعرّفة من قبل المستخدم الجديدة قبل قواعد المنع الافتراضية، لذلك لا حاجة إلى معامل ترتيب إضافي.
- يؤثر هذا فقط في تعديلات المعاينة النصية النهائية التي يستطيع OpenClaw إنهاءها بأمان في مكانها. أما بدائل الوسائط وبدائل المعاينات القديمة فما تزال تستخدم تسليم Matrix العادي.
- إذا أظهر `GET /_matrix/client/v3/pushers` عدم وجود pushers، فهذا يعني أن المستخدم لا يملك بعد تسليم دفع Matrix عاملًا لهذا الحساب/الجهاز.

#### Synapse

بالنسبة إلى Synapse، يكون الإعداد أعلاه كافيًا عادة بمفرده:

- لا يلزم أي تغيير خاص في `homeserver.yaml` لإشعارات معاينة OpenClaw النهائية.
- إذا كان نشر Synapse لديك يرسل بالفعل إشعارات دفع Matrix العادية، فإن رمز المستخدم + استدعاء `pushrules` أعلاه هما خطوة الإعداد الأساسية.
- إذا كنت تشغّل Synapse خلف وكيل عكسي أو workers، فتأكد من أن `/_matrix/client/.../pushrules/` يصل إلى Synapse بشكل صحيح.
- إذا كنت تشغّل Synapse workers، فتأكد من أن pushers تعمل بشكل سليم. تتم معالجة تسليم الدفع بواسطة العملية الرئيسية أو `synapse.app.pusher` / عمال pusher المكوّنين.

#### Tuwunel

بالنسبة إلى Tuwunel، استخدم تدفق الإعداد نفسه واستدعاء API لقواعد الدفع كما هو موضح أعلاه:

- لا يلزم أي تكوين خاص بـ Tuwunel لعلامة المعاينة النهائية نفسها.
- إذا كانت إشعارات Matrix العادية تعمل بالفعل لذلك المستخدم، فإن رمز المستخدم + استدعاء `pushrules` أعلاه هما خطوة الإعداد الأساسية.
- إذا بدا أن الإشعارات تختفي أثناء نشاط المستخدم على جهاز آخر، فتحقق مما إذا كان `suppress_push_when_active` مفعّلًا. أضاف Tuwunel هذا الخيار في Tuwunel 1.4.2 بتاريخ 12 سبتمبر 2025، ويمكنه أن يمنع عمدًا الإشعارات المرسلة إلى الأجهزة الأخرى أثناء نشاط أحد الأجهزة.

## غرف البوت إلى البوت

بشكل افتراضي، يتم تجاهل رسائل Matrix الواردة من حسابات Matrix أخرى مكوّنة لـ OpenClaw.

استخدم `allowBots` عندما تريد عمدًا حركة Matrix بين الوكلاء:

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

- `allowBots: true` يقبل الرسائل من حسابات بوت Matrix أخرى مكوّنة في الغرف المسموح بها والرسائل المباشرة.
- `allowBots: "mentions"` يقبل تلك الرسائل فقط عندما تذكر هذا البوت بوضوح في الغرف. وتظل الرسائل المباشرة مسموحًا بها.
- يقوم `groups.<room>.allowBots` بتجاوز الإعداد على مستوى الحساب لغرفة واحدة.
- ما يزال OpenClaw يتجاهل الرسائل من معرّف مستخدم Matrix نفسه لتجنب حلقات الرد الذاتي.
- لا يكشف Matrix هنا عن علامة بوت أصلية؛ ويتعامل OpenClaw مع "مكتوبة بواسطة بوت" على أنها "مرسلة بواسطة حساب Matrix آخر مكوَّن على بوابة OpenClaw هذه".

استخدم قوائم سماح صارمة للغرف ومتطلبات الذكر عند تمكين حركة البوت إلى البوت في الغرف المشتركة.

## التشفير والتحقق

في الغرف المشفرة (E2EE)، تستخدم أحداث الصور الصادرة `thumbnail_file` بحيث تُشفَّر معاينات الصور إلى جانب المرفق الكامل. وتستمر الغرف غير المشفرة في استخدام `thumbnail_url` العادي. لا يلزم أي تكوين — تكتشف الإضافة حالة E2EE تلقائيًا.

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

الحالة المفصلة (تشخيصات كاملة):

```bash
openclaw matrix verify status --verbose
```

تضمين مفتاح الاسترداد المخزَّن في المخرجات القابلة للقراءة آليًا:

```bash
openclaw matrix verify status --include-recovery-key --json
```

تهيئة التوقيع المتقاطع وحالة التحقق:

```bash
openclaw matrix verify bootstrap
```

تشخيصات التهيئة التفصيلية:

```bash
openclaw matrix verify bootstrap --verbose
```

فرض إعادة تعيين جديدة لهوية التوقيع المتقاطع قبل التهيئة:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

تحقق من هذا الجهاز باستخدام مفتاح استرداد:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

تفاصيل التحقق المفصلة للجهاز:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

التحقق من سلامة النسخ الاحتياطي لمفاتيح الغرف:

```bash
openclaw matrix verify backup status
```

تشخيصات سلامة النسخ الاحتياطي المفصلة:

```bash
openclaw matrix verify backup status --verbose
```

استعادة مفاتيح الغرف من النسخة الاحتياطية على الخادم:

```bash
openclaw matrix verify backup restore
```

تشخيصات الاستعادة المفصلة:

```bash
openclaw matrix verify backup restore --verbose
```

احذف النسخة الاحتياطية الحالية على الخادم وأنشئ خط أساس جديدًا للنسخ الاحتياطي. إذا تعذر تحميل
مفتاح النسخة الاحتياطية المخزن بشكل نظيف، فقد تؤدي إعادة التعيين هذه أيضًا إلى إعادة إنشاء التخزين السري بحيث
تستطيع عمليات البدء البارد المستقبلية تحميل مفتاح النسخة الاحتياطية الجديد:

```bash
openclaw matrix verify backup reset --yes
```

تكون جميع أوامر `verify` موجزة افتراضيًا (بما في ذلك السجل الداخلي الهادئ لـ SDK) وتعرض تشخيصات مفصلة فقط مع `--verbose`.
استخدم `--json` للحصول على مخرجات كاملة قابلة للقراءة آليًا عند كتابة السكربتات.

في إعدادات الحسابات المتعددة، تستخدم أوامر Matrix CLI حساب Matrix الافتراضي الضمني ما لم تمرر `--account <id>`.
إذا قمت بتكوين عدة حسابات مسماة، فعيّن `channels.matrix.defaultAccount` أولًا وإلا فستتوقف عمليات CLI الضمنية تلك وتطلب منك اختيار حساب بشكل صريح.
استخدم `--account` كلما أردت أن تستهدف عمليات التحقق أو الجهاز حسابًا مسمى بشكل صريح:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

عندما يكون التشفير معطلًا أو غير متاح لحساب مسمى، تشير تحذيرات Matrix وأخطاء التحقق إلى مفتاح تكوين ذلك الحساب، مثل `channels.matrix.accounts.assistant.encryption`.

### ما معنى "تم التحقق"

يتعامل OpenClaw مع جهاز Matrix هذا على أنه تم التحقق منه فقط عندما يتم التحقق منه بواسطة هوية التوقيع المتقاطع الخاصة بك.
عمليًا، يعرض `openclaw matrix verify status --verbose` ثلاث إشارات ثقة:

- `Locally trusted`: هذا الجهاز موثوق به من قبل العميل الحالي فقط
- `Cross-signing verified`: يبلّغ SDK أن الجهاز قد تم التحقق منه عبر التوقيع المتقاطع
- `Signed by owner`: الجهاز موقَّع بواسطة مفتاح التوقيع الذاتي الخاص بك

تتحول `Verified by owner` إلى `yes` فقط عندما يكون التحقق عبر التوقيع المتقاطع أو توقيع المالك موجودًا.
ولا تكفي الثقة المحلية وحدها لكي يتعامل OpenClaw مع الجهاز على أنه متحقق منه بالكامل.

### ما الذي تفعله التهيئة

يعد `openclaw matrix verify bootstrap` أمر الإصلاح والإعداد لحسابات Matrix المشفرة.
وينفذ كل ما يلي بالترتيب:

- يهيئ التخزين السري، مع إعادة استخدام مفتاح استرداد موجود عند الإمكان
- يهيئ التوقيع المتقاطع ويرفع مفاتيح التوقيع المتقاطع العامة المفقودة
- يحاول وضع علامة على الجهاز الحالي وتوقيعه توقيعًا متقاطعًا
- ينشئ نسخة احتياطية جديدة على الخادم لمفاتيح الغرف إذا لم تكن موجودة بالفعل

إذا كان الخادم المنزلي يتطلب مصادقة تفاعلية لرفع مفاتيح التوقيع المتقاطع، يحاول OpenClaw الرفع بدون مصادقة أولًا، ثم باستخدام `m.login.dummy`، ثم باستخدام `m.login.password` عندما يكون `channels.matrix.password` مكوّنًا.

استخدم `--force-reset-cross-signing` فقط عندما تريد عمدًا التخلص من هوية التوقيع المتقاطع الحالية وإنشاء هوية جديدة.

إذا كنت تريد عمدًا التخلص من النسخة الاحتياطية الحالية لمفاتيح الغرف وبدء
خط أساس جديد للنسخ الاحتياطي للرسائل المستقبلية، فاستخدم `openclaw matrix verify backup reset --yes`.
افعل ذلك فقط إذا كنت تقبل بأن السجل المشفر القديم غير القابل للاسترداد سيظل
غير متاح، وأن OpenClaw قد يعيد إنشاء التخزين السري إذا تعذر تحميل سر
النسخة الاحتياطية الحالية بأمان.

### خط أساس جديد للنسخ الاحتياطي

إذا كنت تريد إبقاء الرسائل المشفرة المستقبلية تعمل وتقبل فقدان السجل القديم غير القابل للاسترداد، فشغّل هذه الأوامر بالترتيب:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

أضف `--account <id>` إلى كل أمر عندما تريد استهداف حساب Matrix مسمى بشكل صريح.

### سلوك بدء التشغيل

عندما يكون `encryption: true`، يعيّن Matrix القيمة الافتراضية لـ `startupVerification` إلى `"if-unverified"`.
عند بدء التشغيل، إذا ظل هذا الجهاز غير متحقق منه، فسيطلب Matrix تحققًا ذاتيًا في عميل Matrix آخر،
ويتخطى الطلبات المكررة عندما يكون أحدها معلقًا بالفعل، ويطبق مهلة محلية قبل إعادة المحاولة بعد إعادة التشغيل.
تعاد محاولة الطلبات الفاشلة أسرع من إنشاء الطلبات الناجحة افتراضيًا.
عيّن `startupVerification: "off"` لتعطيل طلبات بدء التشغيل التلقائية، أو اضبط `startupVerificationCooldownHours`
إذا كنت تريد نافذة إعادة محاولة أقصر أو أطول.

ينفذ بدء التشغيل أيضًا تمريرة تهيئة تشفير محافظة تلقائيًا.
وتحاول تلك التمريرة أولًا إعادة استخدام التخزين السري الحالي وهوية التوقيع المتقاطع الحالية، وتتجنب إعادة تعيين التوقيع المتقاطع إلا إذا شغّلت تدفق إصلاح تهيئة صريحًا.

إذا اكتشف بدء التشغيل حالة تهيئة معطلة وكان `channels.matrix.password` مكوّنًا، فيمكن لـ OpenClaw محاولة مسار إصلاح أكثر صرامة.
وإذا كان الجهاز الحالي موقّعًا من المالك بالفعل، يحافظ OpenClaw على تلك الهوية بدلًا من إعادة تعيينها تلقائيًا.

راجع [ترحيل Matrix](/ar/install/migrating-matrix) للحصول على تدفق الترقية الكامل، والقيود، وأوامر الاسترداد، ورسائل الترحيل الشائعة.

### إشعارات التحقق

ينشر Matrix إشعارات دورة حياة التحقق مباشرة في غرفة التحقق الصارمة للرسائل المباشرة كرسائل `m.notice`.
ويتضمن ذلك:

- إشعارات طلب التحقق
- إشعارات جاهزية التحقق (مع إرشاد صريح "تحقق عبر الرموز التعبيرية")
- إشعارات بدء التحقق واكتماله
- تفاصيل SAS (الرموز التعبيرية والأرقام العشرية) عند توفرها

يتم تتبع طلبات التحقق الواردة من عميل Matrix آخر وقبولها تلقائيًا بواسطة OpenClaw.
وبالنسبة إلى تدفقات التحقق الذاتي، يبدأ OpenClaw أيضًا تدفق SAS تلقائيًا عندما يصبح التحقق بالرموز التعبيرية متاحًا ويؤكد جانبه الخاص.
أما بالنسبة إلى طلبات التحقق الواردة من مستخدم/جهاز Matrix آخر، فيقبل OpenClaw الطلب تلقائيًا ثم ينتظر أن يتابع تدفق SAS بشكل طبيعي.
ولا يزال يتعين عليك مقارنة SAS الرمزية أو العشرية في عميل Matrix لديك وتأكيد "إنها متطابقة" هناك لإكمال التحقق.

لا يقبل OpenClaw تلقائيًا التدفقات المكررة التي بدأها بنفسه بشكل أعمى. ويتخطى بدء التشغيل إنشاء طلب جديد عندما يكون طلب تحقق ذاتي معلقًا بالفعل.

لا يتم تمرير إشعارات بروتوكول/نظام التحقق إلى مسار دردشة الوكيل، لذلك لا تنتج `NO_REPLY`.

### نظافة الأجهزة

يمكن أن تتراكم أجهزة Matrix القديمة التي يديرها OpenClaw على الحساب وتجعل فهم الثقة في الغرف المشفرة أصعب.
اعرضها باستخدام:

```bash
openclaw matrix devices list
```

أزل الأجهزة القديمة التي يديرها OpenClaw باستخدام:

```bash
openclaw matrix devices prune-stale
```

### مخزن التشفير

يستخدم E2EE في Matrix مسار التشفير Rust الرسمي في `matrix-js-sdk` على Node، مع `fake-indexeddb` كطبقة محاكاة لـ IndexedDB. تُحفظ حالة التشفير في ملف لقطة (`crypto-idb-snapshot.json`) وتُستعاد عند بدء التشغيل. ويُعد ملف اللقطة حالة تشغيل حساسة مخزنة بأذونات ملفات مقيّدة.

تعيش حالة التشغيل المشفرة تحت جذور لكل حساب ولكل مستخدم ولكل تجزئة رمز في
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`.
ويحتوي ذلك الدليل على مخزن المزامنة (`bot-storage.json`)، ومخزن التشفير (`crypto/`)،
وملف مفتاح الاسترداد (`recovery-key.json`)، ولقطة IndexedDB (`crypto-idb-snapshot.json`)،
وروابط الخيوط (`thread-bindings.json`)، وحالة التحقق عند بدء التشغيل (`startup-verification.json`).
وعندما يتغير الرمز مع بقاء هوية الحساب نفسها، يعيد OpenClaw استخدام أفضل جذر موجود
لهذا الصفيف account/homeserver/user بحيث تظل حالة المزامنة السابقة وحالة التشفير وروابط الخيوط
وحالة التحقق عند بدء التشغيل مرئية.

## إدارة الملف الشخصي

حدّث الملف الشخصي الذاتي في Matrix للحساب المحدد باستخدام:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

أضف `--account <id>` عندما تريد استهداف حساب مسمى بشكل صريح.

يقبل Matrix عناوين URL للصور الرمزية من نوع `mxc://` مباشرة. وعندما تمرر عنوان URL للصورة الرمزية من نوع `http://` أو `https://`، يقوم OpenClaw برفعه إلى Matrix أولًا ثم يخزن عنوان `mxc://` الناتج مرة أخرى في `channels.matrix.avatarUrl` (أو تجاوز الحساب المحدد).

## الخيوط

يدعم Matrix خيوط Matrix الأصلية لكل من الردود التلقائية وعمليات الإرسال عبر أدوات الرسائل.

- يبقي `dm.sessionScope: "per-user"` (الافتراضي) توجيه الرسائل المباشرة في Matrix ضمن نطاق المرسل، بحيث يمكن لعدة غرف رسائل مباشرة مشاركة جلسة واحدة عندما تُحل إلى النظير نفسه.
- يعزل `dm.sessionScope: "per-room"` كل غرفة رسائل مباشرة في Matrix داخل مفتاح جلسة خاص بها مع الاستمرار في استخدام فحوصات مصادقة الرسائل المباشرة وقائمة السماح العادية.
- تظل روابط محادثات Matrix الصريحة ذات أولوية على `dm.sessionScope`، لذلك تحتفظ الغرف والخيوط المرتبطة بالجلسة الهدف التي اختيرت لها.
- يبقي `threadReplies: "off"` الردود على المستوى الأعلى ويبقي الرسائل الواردة ذات الخيوط على جلسة الرسالة الأصل.
- يرد `threadReplies: "inbound"` داخل خيط فقط عندما تكون الرسالة الواردة موجودة بالفعل في ذلك الخيط.
- يبقي `threadReplies: "always"` ردود الغرفة في خيط متجذر في الرسالة المحفزة ويوجه تلك المحادثة عبر الجلسة المطابقة ذات نطاق الخيط بدءًا من أول رسالة محفزة.
- يتجاوز `dm.threadReplies` الإعداد الأعلى مستوى للرسائل المباشرة فقط. على سبيل المثال، يمكنك إبقاء خيوط الغرف معزولة مع إبقاء الرسائل المباشرة مسطحة.
- تتضمن الرسائل الواردة ذات الخيوط رسالة جذر الخيط كسياق إضافي للوكيل.
- ترث عمليات الإرسال عبر أدوات الرسائل خيط Matrix الحالي تلقائيًا عندما يكون الهدف هو الغرفة نفسها أو الهدف نفسه لمستخدم الرسائل المباشرة، ما لم يتم توفير `threadId` صريح.
- لا يعمل إعادة استخدام الهدف نفسه لمستخدم الرسائل المباشرة ضمن الجلسة نفسها إلا عندما تثبت بيانات تعريف الجلسة الحالية النظير نفسه في الرسائل المباشرة على حساب Matrix نفسه؛ وإلا يعود OpenClaw إلى التوجيه العادي ضمن نطاق المستخدم.
- عندما يكتشف OpenClaw أن غرفة رسائل مباشرة في Matrix تتصادم مع غرفة رسائل مباشرة أخرى على جلسة الرسائل المباشرة المشتركة نفسها في Matrix، فإنه ينشر `m.notice` لمرة واحدة في تلك الغرفة مع مخرج `/focus` عندما تكون روابط الخيوط ممكّنة وتلميح `dm.sessionScope`.
- يتم دعم روابط الخيوط وقت التشغيل في Matrix. تعمل `/focus` و`/unfocus` و`/agents` و`/session idle` و`/session max-age` و`/acp spawn` المرتبط بالخيط في غرف Matrix والرسائل المباشرة.
- يقوم `/focus` على المستوى الأعلى في غرفة/رسائل مباشرة في Matrix بإنشاء خيط Matrix جديد وربطه بالجلسة الهدف عندما يكون `threadBindings.spawnSubagentSessions=true`.
- يؤدي تشغيل `/focus` أو `/acp spawn --thread here` داخل خيط Matrix موجود إلى ربط ذلك الخيط الحالي بدلًا من ذلك.

## روابط محادثات ACP

يمكن تحويل غرف Matrix والرسائل المباشرة وخيوط Matrix الموجودة إلى مساحات عمل ACP دائمة دون تغيير واجهة الدردشة.

تدفق المشغّل السريع:

- شغّل `/acp spawn codex --bind here` داخل رسالة Matrix المباشرة أو الغرفة أو الخيط الموجود الذي تريد الاستمرار في استخدامه.
- في رسالة Matrix مباشرة أو غرفة على المستوى الأعلى، تبقى الرسالة المباشرة/الغرفة الحالية هي واجهة الدردشة، وتُوجَّه الرسائل المستقبلية إلى جلسة ACP التي تم إنشاؤها.
- داخل خيط Matrix موجود، يقوم `--bind here` بربط ذلك الخيط الحالي في مكانه.
- يقوم `/new` و`/reset` بإعادة تعيين جلسة ACP المرتبطة نفسها في مكانها.
- يقوم `/acp close` بإغلاق جلسة ACP وإزالة الربط.

ملاحظات:

- لا ينشئ `--bind here` خيط Matrix فرعيًا.
- لا يكون `threadBindings.spawnAcpSessions` مطلوبًا إلا مع `/acp spawn --thread auto|here`، حيث يحتاج OpenClaw إلى إنشاء خيط Matrix فرعي أو ربطه.

### تكوين ربط الخيوط

يرث Matrix القيم الافتراضية العامة من `session.threadBindings`، كما يدعم أيضًا تجاوزات لكل قناة:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

علامات إنشاء الخيوط المرتبطة في Matrix اختيارية:

- عيّن `threadBindings.spawnSubagentSessions: true` للسماح لـ `/focus` على المستوى الأعلى بإنشاء خيوط Matrix جديدة وربطها.
- عيّن `threadBindings.spawnAcpSessions: true` للسماح لـ `/acp spawn --thread auto|here` بربط جلسات ACP بخيوط Matrix.

## التفاعلات

يدعم Matrix إجراءات التفاعلات الصادرة، وإشعارات التفاعلات الواردة، وتفاعلات الإقرار الواردة.

- يتم التحكم في أدوات التفاعل الصادر بواسطة `channels["matrix"].actions.reactions`.
- يضيف `react` تفاعلًا إلى حدث Matrix محدد.
- يسرد `reactions` ملخص التفاعلات الحالي لحدث Matrix محدد.
- تؤدي `emoji=""` إلى إزالة تفاعلات حساب البوت نفسه على ذلك الحدث.
- تؤدي `remove: true` إلى إزالة تفاعل الرمز التعبيري المحدد فقط من حساب البوت.

يُحل نطاق تفاعلات الإقرار وفق ترتيب OpenClaw القياسي:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- الرجوع إلى الرمز التعبيري لهوية الوكيل

يُحل نطاق تفاعل الإقرار بهذا الترتيب:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

يُحل وضع إشعارات التفاعلات بهذا الترتيب:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- الافتراضي: `own`

السلوك:

- `reactionNotifications: "own"` يمرر أحداث `m.reaction` المضافة عندما تستهدف رسائل Matrix التي أنشأها البوت.
- `reactionNotifications: "off"` يعطل أحداث نظام التفاعلات.
- لا يتم توليف عمليات إزالة التفاعلات إلى أحداث نظام لأن Matrix يعرضها كعمليات حذف redactions، وليس كعمليات إزالة مستقلة لـ `m.reaction`.

## سياق السجل

- يتحكم `channels.matrix.historyLimit` في عدد رسائل الغرفة الأخيرة التي تُضمَّن باعتبارها `InboundHistory` عندما تُحفّز رسالة غرفة Matrix الوكيل. ويرجع إلى `messages.groupChat.historyLimit`؛ وإذا لم يكن أيٌّ منهما معيّنًا، تكون القيمة الافتراضية الفعلية `0`. عيّن `0` للتعطيل.
- يقتصر سجل غرف Matrix على الغرفة فقط. وتستمر الرسائل المباشرة في استخدام سجل الجلسة العادي.
- سجل غرف Matrix معلق فقط: يخزن OpenClaw رسائل الغرفة التي لم تُحفّز ردًا بعد، ثم يلتقط تلك النافذة عندما تصل إشارة أو محفز آخر.
- لا تُضمَّن رسالة التحفيز الحالية في `InboundHistory`؛ بل تبقى في النص الرئيسي الوارد لذلك الدور.
- تعيد محاولات الحدث نفسه في Matrix استخدام لقطة السجل الأصلية بدلًا من الانجراف إلى رسائل أحدث في الغرفة.

## رؤية السياق

يدعم Matrix عنصر التحكم المشترك `contextVisibility` للسياق التكميلي للغرفة مثل نص الرد المجلوِب وجذور الخيوط والسجل المعلق.

- `contextVisibility: "all"` هو الإعداد الافتراضي. يُحتفظ بالسياق التكميلي كما تم استلامه.
- `contextVisibility: "allowlist"` يرشح السياق التكميلي إلى المرسلين المسموح بهم وفق فحوصات قائمة السماح النشطة للغرفة/المستخدم.
- `contextVisibility: "allowlist_quote"` يتصرف مثل `allowlist`، لكنه يحتفظ مع ذلك برد مقتبس صريح واحد.

يؤثر هذا الإعداد في رؤية السياق التكميلي، وليس في ما إذا كانت الرسالة الواردة نفسها تستطيع تحفيز رد.
ولا يزال تفويض التحفيز يأتي من إعدادات `groupPolicy` و`groups` و`groupAllowFrom` وسياسة الرسائل المباشرة.

## سياسة الرسائل المباشرة والغرف

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

راجع [Groups](/ar/channels/groups) لمعرفة سلوك تقييد الإشارات وقائمة السماح.

مثال على الاقتران للرسائل المباشرة في Matrix:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

إذا استمر مستخدم Matrix غير معتمد في مراسلتك قبل الموافقة، يعيد OpenClaw استخدام رمز الاقتران المعلق نفسه، وقد يرسل رد تذكير مرة أخرى بعد فترة تهدئة قصيرة بدلًا من إنشاء رمز جديد.

راجع [Pairing](/ar/channels/pairing) لمعرفة تدفق اقتران الرسائل المباشرة المشترك وتخطيط التخزين.

## إصلاح الغرف المباشرة

إذا خرجت حالة الرسائل المباشرة عن التزامن، فقد ينتهي الأمر بـ OpenClaw إلى وجود تعيينات `m.direct` قديمة تشير إلى غرف فردية قديمة بدلًا من الرسالة المباشرة الحية. افحص التعيين الحالي لنظير باستخدام:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

أصلحه باستخدام:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

يقوم تدفق الإصلاح بما يلي:

- يفضل رسالة مباشرة صارمة 1:1 تكون مُعيَّنة بالفعل في `m.direct`
- يعود إلى أي رسالة مباشرة صارمة 1:1 منضم إليها حاليًا مع ذلك المستخدم
- ينشئ غرفة مباشرة جديدة ويعيد كتابة `m.direct` إذا لم تكن هناك رسالة مباشرة سليمة

لا يحذف تدفق الإصلاح الغرف القديمة تلقائيًا. بل يختار فقط الرسالة المباشرة السليمة ويحدّث التعيين بحيث تستهدف عمليات الإرسال الجديدة في Matrix وإشعارات التحقق وغيرها من تدفقات الرسائل المباشرة الغرفة الصحيحة مرة أخرى.

## موافقات Exec

يمكن لـ Matrix أن يعمل كعميل موافقة أصلي لحساب Matrix. وتظل
عناصر التحكم الأصلية لتوجيه الرسائل المباشرة/القنوات موجودة ضمن تكوين موافقات exec:

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (اختياري؛ ويرجع إلى `channels.matrix.dm.allowFrom`)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`، الافتراضي: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

يجب أن يكون الموافقون معرّفات مستخدمي Matrix مثل `@owner:example.org`. يقوم Matrix بتمكين الموافقات الأصلية تلقائيًا عندما يكون `enabled` غير معيّن أو `"auto"` ويكون من الممكن حلّ معتمد واحد على الأقل. تستخدم موافقات Exec مجموعة الموافقين من `execApprovals.approvers` أولًا ويمكنها الرجوع إلى `channels.matrix.dm.allowFrom`. وتفوض موافقات الإضافة من خلال `channels.matrix.dm.allowFrom`. عيّن `enabled: false` لتعطيل Matrix كعميل موافقة أصلي بشكل صريح. بخلاف ذلك، تعود طلبات الموافقة إلى مسارات الموافقة الأخرى المكوّنة أو إلى سياسة الرجوع للموافقة.

يدعم التوجيه الأصلي في Matrix كلا نوعي الموافقات:

- يتحكم `channels.matrix.execApprovals.*` في وضع التوزيع الأصلي للرسائل المباشرة/القنوات لمطالبات موافقة Matrix.
- تستخدم موافقات Exec مجموعة الموافقين التنفيذيين من `execApprovals.approvers` أو `channels.matrix.dm.allowFrom`.
- تستخدم موافقات الإضافات قائمة السماح للرسائل المباشرة في Matrix من `channels.matrix.dm.allowFrom`.
- تنطبق اختصارات التفاعلات في Matrix وتحديثات الرسائل على موافقات exec والإضافات معًا.

قواعد التسليم:

- `target: "dm"` يرسل مطالبات الموافقة إلى الرسائل المباشرة للموافقين
- `target: "channel"` يرسل المطالبة مرة أخرى إلى غرفة Matrix أو الرسالة المباشرة الأصلية
- `target: "both"` يرسل إلى الرسائل المباشرة للموافقين وإلى غرفة Matrix أو الرسالة المباشرة الأصلية

تزرع مطالبات الموافقة في Matrix اختصارات التفاعلات على رسالة الموافقة الأساسية:

- `✅` = السماح مرة واحدة
- `❌` = الرفض
- `♾️` = السماح دائمًا عندما يكون هذا القرار مسموحًا به وفق سياسة exec الفعالة

يمكن للموافقين التفاعل على تلك الرسالة أو استخدام أوامر الشرطة المائلة البديلة: `/approve <id> allow-once` أو `/approve <id> allow-always` أو `/approve <id> deny`.

يمكن فقط للموافقين الذين تم حلهم الموافقة أو الرفض. وبالنسبة إلى موافقات exec، يتضمن التسليم عبر القناة نص الأمر، لذا لا تمكّن `channel` أو `both` إلا في الغرف الموثوقة.

التجاوز لكل حساب:

- `channels.matrix.accounts.<account>.execApprovals`

الوثائق ذات الصلة: [Exec approvals](/ar/tools/exec-approvals)

## الحسابات المتعددة

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

تعمل قيم `channels.matrix` في المستوى الأعلى كقيم افتراضية للحسابات المسماة ما لم يتجاوزها أحد الحسابات.
يمكنك تقييد إدخالات الغرف الموروثة إلى حساب Matrix واحد باستخدام `groups.<room>.account`.
وتبقى الإدخالات التي لا تحتوي على `account` مشتركة بين جميع حسابات Matrix، كما تظل الإدخالات التي تحتوي على `account: "default"` تعمل عندما يكون الحساب الافتراضي مكوّنًا مباشرة على المستوى الأعلى في `channels.matrix.*`.
ولا تُنشئ القيم الافتراضية المشتركة الجزئية للمصادقة حسابًا افتراضيًا ضمنيًا منفصلًا بمفردها. لا يقوم OpenClaw بإنشاء حساب `default` على المستوى الأعلى إلا عندما يمتلك ذلك الافتراضي مصادقة حديثة (`homeserver` مع `accessToken`، أو `homeserver` مع `userId` و`password`)؛ ويمكن للحسابات المسماة أن تظل قابلة للاكتشاف من `homeserver` مع `userId` عندما تلبّي بيانات الاعتماد المؤقتة المصادقة لاحقًا.
إذا كان لدى Matrix بالفعل حساب مسمى واحد بالضبط، أو كان `defaultAccount` يشير إلى مفتاح حساب مسمى موجود، فإن ترقية الإصلاح/الإعداد من حساب واحد إلى عدة حسابات تحافظ على ذلك الحساب بدلًا من إنشاء إدخال `accounts.default` جديد. لا تنتقل إلى ذلك الحساب المُرقّى إلا مفاتيح المصادقة/التهيئة الخاصة بـ Matrix؛ أما مفاتيح سياسة التسليم المشتركة فتبقى في المستوى الأعلى.
عيّن `defaultAccount` عندما تريد أن يفضّل OpenClaw حساب Matrix مسمى واحدًا للتوجيه الضمني والفحص وعمليات CLI.
إذا قمت بتكوين عدة حسابات مسماة، فعيّن `defaultAccount` أو مرر `--account <id>` لأوامر CLI التي تعتمد على اختيار حساب ضمني.
مرر `--account <id>` إلى `openclaw matrix verify ...` و`openclaw matrix devices ...` عندما تريد تجاوز ذلك الاختيار الضمني لأمر واحد.

راجع [مرجع التكوين](/ar/gateway/configuration-reference#multi-account-all-channels) لمعرفة نمط الحسابات المتعددة المشترك.

## الخوادم المنزلية الخاصة/الشبكات المحلية

بشكل افتراضي، يحظر OpenClaw خوادم Matrix المنزلية الخاصة/الداخلية للحماية من SSRF ما لم
تفعّل ذلك صراحةً لكل حساب.

إذا كان الخادم المنزلي لديك يعمل على localhost أو عنوان IP لشبكة LAN/Tailscale أو اسم مضيف داخلي، فقم بتمكين
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

مثال على إعداد CLI:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

يسمح هذا التفعيل الاختياري فقط بالأهداف الخاصة/الداخلية الموثوقة. أما الخوادم المنزلية العامة ذات النص الصريح مثل
`http://matrix.example.org:8008` فتظل محظورة. ويفضل استخدام `https://` كلما أمكن.

## تمرير حركة Matrix عبر وكيل

إذا كان نشر Matrix لديك يحتاج إلى وكيل HTTP(S) صادر صريح، فعيّن `channels.matrix.proxy`:

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

يمكن للحسابات المسماة تجاوز القيمة الافتراضية على المستوى الأعلى باستخدام `channels.matrix.accounts.<id>.proxy`.
ويستخدم OpenClaw إعداد الوكيل نفسه لكل من حركة Matrix وقت التشغيل وفحوصات حالة الحساب.

## دقة الأهداف

يقبل Matrix صيغ الأهداف التالية أينما طلب منك OpenClaw هدف غرفة أو مستخدم:

- المستخدمون: `@user:server` أو `user:@user:server` أو `matrix:user:@user:server`
- الغرف: `!room:server` أو `room:!room:server` أو `matrix:room:!room:server`
- الأسماء المستعارة: `#alias:server` أو `channel:#alias:server` أو `matrix:channel:#alias:server`

يستخدم البحث الحي في الدليل حساب Matrix المسجل دخوله:

- تستعلم عمليات البحث عن المستخدمين عن دليل مستخدمي Matrix على ذلك الخادم المنزلي.
- تقبل عمليات البحث عن الغرف معرّفات الغرف والأسماء المستعارة الصريحة مباشرة، ثم تعود إلى البحث في أسماء الغرف المنضم إليها لذلك الحساب.
- يُعد البحث في أسماء الغرف المنضم إليها أفضل جهد. إذا تعذر حل اسم غرفة إلى معرّف أو اسم مستعار، فسيتم تجاهله بواسطة دقة قائمة السماح وقت التشغيل.

## مرجع التكوين

- `enabled`: تمكين القناة أو تعطيلها.
- `name`: تسمية اختيارية للحساب.
- `defaultAccount`: معرّف الحساب المفضل عندما تكون عدة حسابات Matrix مكوّنة.
- `homeserver`: عنوان URL للخادم المنزلي، مثل `https://matrix.example.org`.
- `network.dangerouslyAllowPrivateNetwork`: السماح لهذا الحساب في Matrix بالاتصال بخوادم منزلية خاصة/داخلية. فعّل هذا عندما يُحل الخادم المنزلي إلى `localhost` أو عنوان IP لشبكة LAN/Tailscale أو مضيف داخلي مثل `matrix-synapse`.
- `proxy`: عنوان URL اختياري لوكيل HTTP(S) لحركة Matrix. يمكن للحسابات المسماة تجاوز القيمة الافتراضية على المستوى الأعلى باستخدام `proxy` خاص بها.
- `userId`: معرّف مستخدم Matrix الكامل، مثل `@bot:example.org`.
- `accessToken`: رمز وصول للمصادقة القائمة على الرمز. تُدعَم القيم النصية الصريحة وقيم SecretRef لكل من `channels.matrix.accessToken` و`channels.matrix.accounts.<id>.accessToken` عبر موفري env/file/exec. راجع [Secrets Management](/ar/gateway/secrets).
- `password`: كلمة مرور لتسجيل الدخول القائم على كلمة المرور. تُدعَم القيم النصية الصريحة وقيم SecretRef.
- `deviceId`: معرّف جهاز Matrix صريح.
- `deviceName`: اسم عرض الجهاز لتسجيل الدخول بكلمة المرور.
- `avatarUrl`: عنوان URL للصورة الرمزية الذاتية المخزّن لمزامنة الملف الشخصي وتحديثات `profile set`.
- `initialSyncLimit`: الحد الأقصى لعدد الأحداث التي يتم جلبها أثناء مزامنة بدء التشغيل.
- `encryption`: تمكين E2EE.
- `allowlistOnly`: عندما تكون القيمة `true`، تتم ترقية سياسة الغرف `open` إلى `allowlist`، وتُفرض جميع سياسات الرسائل المباشرة النشطة باستثناء `disabled` (بما في ذلك `pairing` و`open`) إلى `allowlist`. ولا يؤثر ذلك في سياسات `disabled`.
- `allowBots`: السماح بالرسائل من حسابات Matrix أخرى مكوّنة لـ OpenClaw (`true` أو `"mentions"`).
- `groupPolicy`: ‏`open` أو `allowlist` أو `disabled`.
- `contextVisibility`: وضع رؤية سياق الغرفة التكميلي (`all` أو `allowlist` أو `allowlist_quote`).
- `groupAllowFrom`: قائمة سماح لمعرّفات المستخدمين لحركة الغرف. ينبغي أن تكون الإدخالات معرّفات مستخدمي Matrix كاملة؛ وتُتجاهل الأسماء غير المحلولة وقت التشغيل.
- `historyLimit`: الحد الأقصى لرسائل الغرفة التي تُضمَّن كسياق سجل للمجموعات. ويرجع إلى `messages.groupChat.historyLimit`؛ وإذا لم يكن أيٌّ منهما معيّنًا، تكون القيمة الافتراضية الفعلية `0`. عيّن `0` للتعطيل.
- `replyToMode`: ‏`off` أو `first` أو `all` أو `batched`.
- `markdown`: تكوين اختياري لتصيير Markdown في نص Matrix الصادر.
- `streaming`: ‏`off` (الافتراضي) أو `"partial"` أو `"quiet"` أو `true` أو `false`. يقوم `"partial"` و`true` بتمكين تحديثات المسودة المعتمدة على المعاينة أولًا باستخدام رسائل Matrix النصية العادية. ويستخدم `"quiet"` إشعارات معاينة غير مشعرة لإعدادات قواعد الدفع المستضافة ذاتيًا. ويعادل `false` القيمة `"off"`.
- `blockStreaming`: تؤدي `true` إلى تمكين رسائل تقدم منفصلة لكتل المساعد المكتملة أثناء نشاط بث معاينة المسودة.
- `threadReplies`: ‏`off` أو `inbound` أو `always`.
- `threadBindings`: تجاوزات لكل قناة لتوجيه الجلسات المرتبط بالخيوط ودورة حياتها.
- `startupVerification`: وضع طلب التحقق الذاتي التلقائي عند بدء التشغيل (`if-unverified` أو `off`).
- `startupVerificationCooldownHours`: فترة التهدئة قبل إعادة محاولة طلبات التحقق التلقائية عند بدء التشغيل.
- `textChunkLimit`: حجم تجزئة الرسالة الصادرة بالأحرف (يُطبّق عندما يكون `chunkMode` هو `length`).
- `chunkMode`: يقوم `length` بتقسيم الرسائل حسب عدد الأحرف؛ ويقوم `newline` بالتقسيم عند حدود الأسطر.
- `responsePrefix`: سلسلة اختيارية تُسبق بها جميع الردود الصادرة لهذه القناة.
- `ackReaction`: تجاوز اختياري لتفاعل الإقرار لهذه القناة/الحساب.
- `ackReactionScope`: تجاوز اختياري لنطاق تفاعل الإقرار (`group-mentions` أو `group-all` أو `direct` أو `all` أو `none` أو `off`).
- `reactionNotifications`: وضع إشعارات التفاعلات الواردة (`own` أو `off`).
- `mediaMaxMb`: حد حجم الوسائط بالميجابايت للإرسال الصادر ومعالجة الوسائط الواردة.
- `autoJoin`: سياسة الانضمام التلقائي للدعوات (`always` أو `allowlist` أو `off`). الافتراضي: `off`. تنطبق على جميع دعوات Matrix، بما في ذلك الدعوات على نمط الرسائل المباشرة.
- `autoJoinAllowlist`: الغرف/الأسماء المستعارة المسموح بها عندما يكون `autoJoin` هو `allowlist`. تُحل إدخالات الأسماء المستعارة إلى معرّفات غرف أثناء معالجة الدعوة؛ ولا يثق OpenClaw بحالة الاسم المستعار التي تدّعيها الغرفة المدعو إليها.
- `dm`: كتلة سياسة الرسائل المباشرة (`enabled` و`policy` و`allowFrom` و`sessionScope` و`threadReplies`).
- `dm.policy`: يتحكم في الوصول إلى الرسائل المباشرة بعد انضمام OpenClaw إلى الغرفة وتصنيفها كرسالة مباشرة. ولا يغيّر ما إذا كان سيتم الانضمام تلقائيًا إلى الدعوة.
- `dm.allowFrom`: ينبغي أن تكون الإدخالات معرّفات مستخدمي Matrix كاملة ما لم تكن قد قمت بالفعل بحلها عبر البحث الحي في الدليل.
- `dm.sessionScope`: ‏`per-user` (الافتراضي) أو `per-room`. استخدم `per-room` عندما تريد أن تحتفظ كل غرفة رسائل مباشرة في Matrix بسياق منفصل حتى إذا كان النظير نفسه.
- `dm.threadReplies`: تجاوز سياسة الخيوط للرسائل المباشرة فقط (`off` أو `inbound` أو `always`). ويتجاوز الإعداد الأعلى مستوى `threadReplies` لكل من موضع الرد وعزل الجلسة في الرسائل المباشرة.
- `execApprovals`: تسليم موافقات exec الأصلي في Matrix (`enabled` و`approvers` و`target` و`agentFilter` و`sessionFilter`).
- `execApprovals.approvers`: معرّفات مستخدمي Matrix المسموح لهم بالموافقة على طلبات exec. اختياري عندما يكون `dm.allowFrom` يحدد الموافقين بالفعل.
- `execApprovals.target`: ‏`dm | channel | both` (الافتراضي: `dm`).
- `accounts`: تجاوزات مسماة لكل حساب. تعمل قيم `channels.matrix` في المستوى الأعلى كقيم افتراضية لهذه الإدخالات.
- `groups`: خريطة سياسات لكل غرفة. يفضل استخدام معرّفات الغرف أو الأسماء المستعارة؛ وتُتجاهل أسماء الغرف غير المحلولة وقت التشغيل. وتستخدم هوية الجلسة/المجموعة معرّف الغرفة الثابت بعد الحل.
- `groups.<room>.account`: قصر إدخال غرفة موروث واحد على حساب Matrix محدد في إعدادات الحسابات المتعددة.
- `groups.<room>.allowBots`: تجاوز على مستوى الغرفة للمرسلين من البوتات المكوّنة (`true` أو `"mentions"`).
- `groups.<room>.users`: قائمة سماح للمرسلين لكل غرفة.
- `groups.<room>.tools`: تجاوزات السماح/المنع للأدوات لكل غرفة.
- `groups.<room>.autoReply`: تجاوز على مستوى الغرفة لتقييد الإشارات. تؤدي `true` إلى تعطيل متطلبات الإشارة لتلك الغرفة؛ بينما تعيد `false` فرضها.
- `groups.<room>.skills`: مرشح Skills اختياري على مستوى الغرفة.
- `groups.<room>.systemPrompt`: مقتطف اختياري من system prompt على مستوى الغرفة.
- `rooms`: اسم مستعار قديم لـ `groups`.
- `actions`: التحكم في الأدوات لكل إجراء (`messages` و`reactions` و`pins` و`profile` و`memberInfo` و`channelInfo` و`verification`).

## ذو صلة

- [نظرة عامة على القنوات](/ar/channels) — جميع القنوات المدعومة
- [Pairing](/ar/channels/pairing) — مصادقة الرسائل المباشرة وتدفق الاقتران
- [Groups](/ar/channels/groups) — سلوك دردشات المجموعات وتقييد الإشارات
- [توجيه القنوات](/ar/channels/channel-routing) — توجيه الجلسات للرسائل
- [الأمان](/ar/gateway/security) — نموذج الوصول والتقوية
