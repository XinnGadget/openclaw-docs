---
read_when:
    - تنفيذ عملاء WS لـ Gateway أو تحديثهم
    - تصحيح أخطاء عدم تطابق البروتوكول أو حالات فشل الاتصال
    - إعادة توليد مخطط/نماذج البروتوكول
summary: 'بروتوكول WebSocket لـ Gateway: المصافحة، الإطارات، إدارة الإصدارات'
title: بروتوكول Gateway
x-i18n:
    generated_at: "2026-04-16T07:18:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 683e61ebe993a2d739bc34860060b0e3eda36b5c57267a2bcc03d177ec612fb3
    source_path: gateway/protocol.md
    workflow: 15
---

# بروتوكول Gateway ‏(WebSocket)

يُعد بروتوكول WS الخاص بـ Gateway **مستوى التحكم الوحيد + ناقل العقد** لـ
OpenClaw. تتصل جميع العملاء (CLI، وواجهة الويب، وتطبيق macOS، وعقد iOS/Android،
والعقد عديمة الواجهة) عبر WebSocket وتُعلن **الدور** + **النطاق** الخاصين بها وقت
المصافحة.

## النقل

- WebSocket، وإطارات نصية بحمولة JSON.
- يجب أن يكون الإطار الأول **بالضرورة** طلب `connect`.

## المصافحة (`connect`)

Gateway → العميل (تحدي ما قبل الاتصال):

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

العميل → Gateway:

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

Gateway → العميل:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": {
    "type": "hello-ok",
    "protocol": 3,
    "server": { "version": "…", "connId": "…" },
    "features": { "methods": ["…"], "events": ["…"] },
    "snapshot": { "…": "…" },
    "policy": {
      "maxPayload": 26214400,
      "maxBufferedBytes": 52428800,
      "tickIntervalMs": 15000
    }
  }
}
```

`server` و`features` و`snapshot` و`policy` كلها مطلوبة بحسب المخطط
(`src/gateway/protocol/schema/frames.ts`). ويُعد كل من `auth` و`canvasHostUrl` اختياريًا.

عند إصدار رمز جهاز مميز، يتضمن `hello-ok` أيضًا:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

أثناء تسليم bootstrap الموثوق، قد يتضمن `hello-ok.auth` أيضًا إدخالات أدوار إضافية
مقيدة ضمن `deviceTokens`:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "node",
    "scopes": [],
    "deviceTokens": [
      {
        "deviceToken": "…",
        "role": "operator",
        "scopes": ["operator.approvals", "operator.read", "operator.talk.secrets", "operator.write"]
      }
    ]
  }
}
```

في تدفق bootstrap المدمج للعقدة/المشغّل، يبقى الرمز المميز الأساسي للعقدة
`scopes: []`، وأي رمز مميز للمشغّل يتم تسليمه يبقى مقيدًا بقائمة السماح الخاصة
بمشغّل bootstrap (`operator.approvals` و`operator.read` و`operator.talk.secrets`
و`operator.write`). وتظل فحوصات النطاق في bootstrap ذات بادئة مرتبطة بالدور:
إدخالات المشغّل تلبّي فقط طلبات المشغّل، بينما لا تزال الأدوار غير التابعة
للمشغّل تحتاج إلى نطاقات ضمن بادئة الدور الخاصة بها.

### مثال للعقدة

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## التأطير

- **الطلب**: `{type:"req", id, method, params}`
- **الاستجابة**: `{type:"res", id, ok, payload|error}`
- **الحدث**: `{type:"event", event, payload, seq?, stateVersion?}`

تتطلب الطرق ذات الآثار الجانبية **مفاتيح idempotency** (راجع المخطط).

## الأدوار + النطاقات

### الأدوار

- `operator` = عميل مستوى التحكم (CLI/UI/الأتمتة).
- `node` = مضيف القدرات (camera/screen/canvas/system.run).

### النطاقات (`operator`)

النطاقات الشائعة:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

يتطلب `talk.config` مع `includeSecrets: true` النطاق `operator.talk.secrets`
(أو `operator.admin`).

قد تطلب طرق Gateway RPC المسجلة من Plugin نطاق مشغّل خاصًا بها، لكن بادئات
الإدارة الأساسية المحجوزة (`config.*` و`exec.approvals.*` و`wizard.*` و`update.*`)
تُحل دائمًا إلى `operator.admin`.

نطاق الطريقة ليس سوى البوابة الأولى. بعض أوامر الشرطة المائلة التي يتم الوصول
إليها عبر `chat.send` تطبق فحوصات أكثر صرامة على مستوى الأمر فوق ذلك. على سبيل
المثال، تتطلب عمليات الكتابة الدائمة لـ `/config set` و`/config unset`
النطاق `operator.admin`.

يحتوي `node.pair.approve` أيضًا على فحص نطاق إضافي وقت الموافقة فوق نطاق الطريقة
الأساسي:

- الطلبات من دون أوامر: `operator.pairing`
- الطلبات التي تتضمن أوامر عقدة غير تنفيذية: `operator.pairing` + `operator.write`
- الطلبات التي تتضمن `system.run` أو `system.run.prepare` أو `system.which`:
  `operator.pairing` + `operator.admin`

### `caps`/`commands`/`permissions` (`node`)

تعلن العقد مطالبات القدرات عند وقت الاتصال:

- `caps`: فئات القدرات عالية المستوى.
- `commands`: قائمة سماح الأوامر للاستدعاء.
- `permissions`: مفاتيح تبديل دقيقة (مثل `screen.record` و`camera.capture`).

يتعامل Gateway مع هذه القيم على أنها **مطالبات** ويفرض قوائم السماح على جانب الخادم.

## الحضور

- يعيد `system-presence` إدخالات مفهرسة بحسب هوية الجهاز.
- تتضمن إدخالات الحضور `deviceId` و`roles` و`scopes` لكي تتمكن واجهات المستخدم من عرض صف واحد لكل جهاز
  حتى عندما يتصل بصفته **operator** و**node** معًا.

## عائلات طرق RPC الشائعة

هذه الصفحة ليست تفريغًا مولدًا كاملًا، لكن سطح WS العام أوسع من أمثلة
المصافحة/المصادقة الواردة أعلاه. وهذه هي عائلات الطرق الرئيسية التي يعرّضها
Gateway اليوم.

تُعد `hello-ok.features.methods` قائمة اكتشاف محافظة مبنية من
`src/gateway/server-methods-list.ts` إضافةً إلى صادرات الطرق المحمّلة من
Plugin/channel. تعامل معها على أنها لاكتشاف الميزات، لا على أنها تفريغ مولد
لكل مساعد قابل للاستدعاء مُنفّذ في `src/gateway/server-methods/*.ts`.

### النظام والهوية

- يعيد `health` لقطة الحالة الصحية المخزنة مؤقتًا لـ gateway أو التي جرى فحصها حديثًا.
- يعيد `status` ملخص gateway بأسلوب `/status`؛ وتُضمَّن الحقول الحساسة فقط
  لعملاء المشغّل ذوي نطاق الإدارة.
- يعيد `gateway.identity.get` هوية جهاز gateway المستخدمة في تدفقات relay
  والإقران.
- يعيد `system-presence` لقطة الحضور الحالية للأجهزة المتصلة من نوع
  operator/node.
- يضيف `system-event` حدث نظام ويمكنه تحديث/بث سياق الحضور.
- يعيد `last-heartbeat` أحدث حدث Heartbeat محفوظ.
- يبدّل `set-heartbeats` معالجة Heartbeat على الـ gateway.

### النماذج والاستخدام

- يعيد `models.list` فهرس النماذج المسموح بها وقت التشغيل.
- يعيد `usage.status` نوافذ استخدام المزوّد/ملخصات الحصة المتبقية.
- يعيد `usage.cost` ملخصات تكلفة الاستخدام المجمعة لنطاق زمني.
- يعيد `doctor.memory.status` جاهزية الذاكرة المتجهية / التضمين لمساحة عمل
  الوكيل الافتراضية النشطة.
- يعيد `sessions.usage` ملخصات الاستخدام لكل جلسة.
- يعيد `sessions.usage.timeseries` سلسلة زمنية للاستخدام لجلسة واحدة.
- يعيد `sessions.usage.logs` إدخالات سجل الاستخدام لجلسة واحدة.

### القنوات ومساعدات تسجيل الدخول

- يعيد `channels.status` ملخصات حالة القنوات/Plugin المدمجة والمجمعة.
- يسجّل `channels.logout` الخروج من قناة/حساب محدد حيث تدعم القناة
  تسجيل الخروج.
- يبدأ `web.login.start` تدفق تسجيل دخول QR/الويب لمزوّد قناة الويب الحالي
  القادر على QR.
- ينتظر `web.login.wait` اكتمال تدفق تسجيل دخول QR/الويب هذا ويبدأ القناة
  عند النجاح.
- يرسل `push.test` دفعة APNs اختبارية إلى عقدة iOS مسجلة.
- يعيد `voicewake.get` مشغلات كلمة التنبيه المخزنة.
- يحدّث `voicewake.set` مشغلات كلمة التنبيه ويبث التغيير.

### المراسلة والسجلات

- يُعد `send` RPC التسليم الصادر المباشر لعمليات الإرسال المستهدفة إلى
  القناة/الحساب/المحادثة خارج مشغّل الدردشة.
- يعيد `logs.tail` ذيل سجل ملفات gateway المهيأ مع عناصر التحكم
  cursor/limit والحد الأقصى للبايتات.

### Talk وTTS

- يعيد `talk.config` حمولة تهيئة Talk الفعالة؛ ويتطلب `includeSecrets`
  النطاق `operator.talk.secrets` (أو `operator.admin`).
- يضبط `talk.mode` حالة وضع Talk الحالية لعملاء WebChat/Control UI
  ويقوم ببثها.
- يقوم `talk.speak` بتوليف الكلام عبر مزود كلام Talk النشط.
- يعيد `tts.status` حالة تمكين TTS، والمزوّد النشط، ومزوّدي الاحتياط،
  وحالة تهيئة المزوّد.
- يعيد `tts.providers` قائمة مزوّدي TTS الظاهرين.
- يبدّل `tts.enable` و`tts.disable` حالة تفضيلات TTS.
- يحدّث `tts.setProvider` مزوّد TTS المفضل.
- ينفّذ `tts.convert` تحويل نص إلى كلام لمرة واحدة.

### الأسرار والتهيئة والتحديث والمعالج

- يعيد `secrets.reload` حل SecretRefs النشطة ويستبدل حالة الأسرار وقت التشغيل
  فقط عند النجاح الكامل.
- يحل `secrets.resolve` تعيينات الأسرار المستهدفة بالأوامر لمجموعة
  أوامر/أهداف محددة.
- يعيد `config.get` لقطة التهيئة الحالية وقيمة hash.
- يكتب `config.set` حمولة تهيئة تم التحقق منها.
- يدمج `config.patch` تحديث تهيئة جزئيًا.
- يتحقق `config.apply` من حمولة التهيئة الكاملة ويستبدلها.
- يعيد `config.schema` حمولة مخطط التهيئة الحي المستخدم من Control UI وأدوات
  CLI: المخطط، و`uiHints`، والإصدار، وبيانات التوليد الوصفية، بما في ذلك
  بيانات مخطط Plugin + channel الوصفية عندما يتمكن وقت التشغيل من تحميلها. يتضمن
  المخطط بيانات الحقول `title` / `description` المشتقة من نفس التسميات
  ونصوص المساعدة التي تستخدمها واجهة المستخدم، بما في ذلك الفروع المتداخلة
  للكائنات، والرموز العامة، وعناصر المصفوفات، وتركيبات
  `anyOf` / `oneOf` / `allOf` عندما تتوفر وثائق مطابقة للحقول.
- يعيد `config.schema.lookup` حمولة بحث محددة بالمسار لمسار تهيئة واحد:
  المسار المطبّع، وعقدة مخطط سطحية، و`hint` المطابق + `hintPath`،
  وملخصات الأبناء المباشرين للتنقل التفصيلي في UI/CLI.
  - تحتفظ عقد مخطط البحث بالوثائق المواجهة للمستخدم وحقول التحقق الشائعة:
    `title` و`description` و`type` و`enum` و`const` و`format` و`pattern`،
    وحدود الأرقام/السلاسل/المصفوفات/الكائنات، وأعلام منطقية مثل
    `additionalProperties` و`deprecated` و`readOnly` و`writeOnly`.
  - تعرض ملخصات الأبناء `key` و`path` المطبّع و`type` و`required` و`hasChildren`،
    بالإضافة إلى `hint` / `hintPath` المطابقين.
- يشغّل `update.run` تدفق تحديث gateway ويجدول إعادة تشغيل فقط عندما
  ينجح التحديث نفسه.
- توفّر `wizard.start` و`wizard.next` و`wizard.status` و`wizard.cancel`
  معالج الإعداد الأولي عبر WS RPC.

### العائلات الرئيسية الحالية

#### مساعدات الوكيل ومساحة العمل

- يعيد `agents.list` إدخالات الوكلاء المهيأة.
- تدير `agents.create` و`agents.update` و`agents.delete` سجلات الوكلاء
  وربط مساحة العمل.
- تدير `agents.files.list` و`agents.files.get` و`agents.files.set` ملفات
  مساحة عمل bootstrap المكشوفة لوكيل.
- يعيد `agent.identity.get` هوية المساعد الفعالة لوكيل أو جلسة.
- ينتظر `agent.wait` انتهاء التشغيل ويعيد اللقطة الطرفية عند توفرها.

#### التحكم في الجلسة

- يعيد `sessions.list` فهرس الجلسات الحالي.
- يبدّل `sessions.subscribe` و`sessions.unsubscribe` اشتراكات أحداث تغيّر الجلسة
  لعميل WS الحالي.
- يبدّل `sessions.messages.subscribe` و`sessions.messages.unsubscribe`
  اشتراكات أحداث النصوص/الرسائل لجلسة واحدة.
- يعيد `sessions.preview` معاينات نصوص مقيدة لمفاتيح جلسات محددة.
- يقوم `sessions.resolve` بحل هدف جلسة أو جعله بالشكل القياسي.
- ينشئ `sessions.create` إدخال جلسة جديدًا.
- يرسل `sessions.send` رسالة إلى جلسة موجودة.
- يُعد `sessions.steer` صيغة المقاطعة وإعادة التوجيه لجلسة نشطة.
- يوقف `sessions.abort` العمل النشط لجلسة ما.
- يحدّث `sessions.patch` بيانات تعريف الجلسة/التجاوزات.
- تنفّذ `sessions.reset` و`sessions.delete` و`sessions.compact`
  صيانة الجلسة.
- يعيد `sessions.get` صف الجلسة المخزّن الكامل.
- لا يزال تنفيذ الدردشة يستخدم `chat.history` و`chat.send` و`chat.abort` و
  `chat.inject`.
- جرى تطبيع `chat.history` للعرض لعملاء UI: تُزال وسوم التوجيه المضمنة من
  النص المرئي، وتُزال حمولات XML النصية العادية لاستدعاء الأدوات (بما في ذلك
  `<tool_call>...</tool_call>` و`<function_call>...</function_call>` و
  `<tool_calls>...</tool_calls>` و`<function_calls>...</function_calls>` و
  كتل استدعاء الأدوات المقتطعة)، كما تُزال رموز التحكم بالنموذج المتسربة
  بنمط ASCII/العرض الكامل، وتُحذف صفوف المساعد التي تتكون فقط من رموز صامتة
  مثل `NO_REPLY` / `no_reply` تمامًا، ويمكن استبدال الصفوف كبيرة الحجم
  بعناصر نائبة.

#### إقران الأجهزة ورموز الأجهزة المميزة

- يعيد `device.pair.list` الأجهزة المقترنة المعلقة والموافق عليها.
- تدير `device.pair.approve` و`device.pair.reject` و`device.pair.remove`
  سجلات إقران الأجهزة.
- يقوم `device.token.rotate` بتدوير رمز جهاز مقترن ضمن حدود الدور
  والنطاق الموافق عليهما.
- يلغي `device.token.revoke` رمز جهاز مقترن.

#### إقران العقد والاستدعاء والعمل المعلّق

- تغطي `node.pair.request` و`node.pair.list` و`node.pair.approve` و
  `node.pair.reject` و`node.pair.verify` إقران العقد والتحقق من bootstrap.
- يعيد `node.list` و`node.describe` حالة العقد المعروفة/المتصلة.
- يحدّث `node.rename` تسمية عقدة مقترنة.
- يمرر `node.invoke` أمرًا إلى عقدة متصلة.
- يعيد `node.invoke.result` نتيجة طلب استدعاء.
- يحمل `node.event` الأحداث الصادرة من العقدة عائدًا إلى gateway.
- يحدّث `node.canvas.capability.refresh` رموز canvas المميزة ذات النطاق المحدد.
- تُعد `node.pending.pull` و`node.pending.ack` واجهات API لطابور
  العقدة المتصلة.
- تدير `node.pending.enqueue` و`node.pending.drain` العمل المعلق الدائم
  للعقد غير المتصلة/غير المتاحة.

#### عائلات الموافقات

- تغطي `exec.approval.request` و`exec.approval.get` و`exec.approval.list` و
  `exec.approval.resolve` طلبات موافقة exec لمرة واحدة إضافةً إلى
  البحث/إعادة التشغيل للموافقات المعلقة.
- ينتظر `exec.approval.waitDecision` قرار موافقة exec واحدًا معلقًا ويعيد
  القرار النهائي (أو `null` عند انتهاء المهلة).
- تدير `exec.approvals.get` و`exec.approvals.set` لقطات سياسة موافقة exec
  الخاصة بـ gateway.
- تدير `exec.approvals.node.get` و`exec.approvals.node.set` سياسة موافقة exec
  المحلية للعقدة عبر أوامر relay الخاصة بالعقدة.
- تغطي `plugin.approval.request` و`plugin.approval.list` و
  `plugin.approval.waitDecision` و`plugin.approval.resolve`
  تدفقات الموافقة المعرّفة من Plugin.

#### عائلات رئيسية أخرى

- الأتمتة:
  - يجدول `wake` حقن نص تنبيه فوريًا أو عند Heartbeat التالي
  - `cron.list` و`cron.status` و`cron.add` و`cron.update` و`cron.remove` و
    `cron.run` و`cron.runs`
- Skills/الأدوات: `commands.list` و`skills.*` و`tools.catalog` و`tools.effective`

### عائلات الأحداث الشائعة

- `chat`: تحديثات دردشة UI مثل `chat.inject` وأحداث الدردشة الأخرى الخاصة
  بالنص فقط.
- `session.message` و`session.tool`: تحديثات النص/تدفق الأحداث لجلسة
  مشترَك فيها.
- `sessions.changed`: تغيّر فهرس الجلسات أو بياناتها الوصفية.
- `presence`: تحديثات لقطة حضور النظام.
- `tick`: حدث keepalive / liveliness دوري.
- `health`: تحديث لقطة سلامة gateway.
- `heartbeat`: تحديث تدفق أحداث Heartbeat.
- `cron`: حدث تغيّر تشغيل/مهمة Cron.
- `shutdown`: إشعار إيقاف تشغيل gateway.
- `node.pair.requested` / `node.pair.resolved`: دورة حياة إقران العقدة.
- `node.invoke.request`: بث طلب استدعاء العقدة.
- `device.pair.requested` / `device.pair.resolved`: دورة حياة الجهاز المقترن.
- `voicewake.changed`: تغيّرت تهيئة مشغّل كلمة التنبيه.
- `exec.approval.requested` / `exec.approval.resolved`: دورة حياة
  موافقة exec.
- `plugin.approval.requested` / `plugin.approval.resolved`: دورة حياة موافقة
  Plugin.

### طرق مساعدة العقدة

- يمكن للعقد استدعاء `skills.bins` لجلب القائمة الحالية للملفات التنفيذية الخاصة بـ Skills
  للتحقق من السماح التلقائي.

### طرق مساعدة المشغّل

- يمكن للمشغّلين استدعاء `commands.list` (`operator.read`) لجلب قائمة الأوامر
  وقت التشغيل لوكيل.
  - `agentId` اختياري؛ احذفه لقراءة مساحة عمل الوكيل الافتراضية.
  - يتحكم `scope` في السطح الذي يستهدفه `name` الأساسي:
    - يعيد `text` رمز الأمر النصي الأساسي من دون الشرطة المائلة `/`
    - يعيد `native` ومسار `both` الافتراضي أسماء أصلية مدركة للمزوّد
      عند توفرها
  - يحمل `textAliases` الأسماء المستعارة الدقيقة ذات الشرطة المائلة مثل
    `/model` و`/m`.
  - يحمل `nativeName` اسم الأمر الأصلي المدرك للمزوّد عندما يكون موجودًا.
  - `provider` اختياري ولا يؤثر إلا في التسمية الأصلية وإتاحة أوامر Plugin
    الأصلية.
  - يؤدي `includeArgs=false` إلى حذف بيانات الوسائط التسلسلية من الاستجابة.
- يمكن للمشغّلين استدعاء `tools.catalog` (`operator.read`) لجلب فهرس الأدوات وقت التشغيل لوكيل.
  تتضمن الاستجابة أدوات مجمعة وبيانات تعريف المصدر:
  - `source`: `core` أو `plugin`
  - `pluginId`: مالك Plugin عندما تكون `source="plugin"`
  - `optional`: ما إذا كانت أداة Plugin اختيارية
- يمكن للمشغّلين استدعاء `tools.effective` (`operator.read`) لجلب فهرس الأدوات الفعّال
  وقت التشغيل لجلسة.
  - `sessionKey` مطلوب.
  - يستخلص gateway سياق وقت تشغيل موثوقًا من الجلسة على جانب الخادم بدلًا من قبول
    سياق المصادقة أو التسليم المزوَّد من المستدعي.
  - تكون الاستجابة ذات نطاق جلسة وتعكس ما يمكن للمحادثة النشطة استخدامه الآن،
    بما في ذلك أدوات core وPlugin وchannel.
- يمكن للمشغّلين استدعاء `skills.status` (`operator.read`) لجلب قائمة
  Skills المرئية لوكيل.
  - `agentId` اختياري؛ احذفه لقراءة مساحة عمل الوكيل الافتراضية.
  - تتضمن الاستجابة الأهلية، والمتطلبات الناقصة، وفحوصات التهيئة،
    وخيارات التثبيت المنقحة من دون كشف قيم الأسرار الخام.
- يمكن للمشغّلين استدعاء `skills.search` و`skills.detail` (`operator.read`) لبيانات
  اكتشاف ClawHub الوصفية.
- يمكن للمشغّلين استدعاء `skills.install` (`operator.admin`) في وضعين:
  - وضع ClawHub: يثبّت `{ source: "clawhub", slug, version?, force? }`
    مجلد skill في دليل `skills/` الخاص بمساحة عمل الوكيل الافتراضية.
  - وضع مُثبّت Gateway: يشغّل `{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    إجراء `metadata.openclaw.install` مُعلنًا على مضيف gateway.
- يمكن للمشغّلين استدعاء `skills.update` (`operator.admin`) في وضعين:
  - يحدّث وضع ClawHub معرّف slug متتبعًا واحدًا أو جميع تثبيتات ClawHub
    المتتبعة في مساحة عمل الوكيل الافتراضية.
  - يقوم وضع التهيئة بترقيع قيم `skills.entries.<skillKey>` مثل `enabled`
    و`apiKey` و`env`.

## موافقات Exec

- عندما يحتاج طلب exec إلى موافقة، يبث gateway الحدث `exec.approval.requested`.
- يحل عملاء المشغّل ذلك عبر استدعاء `exec.approval.resolve` (ويتطلب النطاق `operator.approvals`).
- بالنسبة إلى `host=node`، يجب أن يتضمن `exec.approval.request` القيمة `systemRunPlan`
  (القيَم القياسية `argv`/`cwd`/`rawCommand`/بيانات تعريف الجلسة). وتُرفض الطلبات
  التي تفتقد `systemRunPlan`.
- بعد الموافقة، تعيد استدعاءات `node.invoke system.run` الممررة استخدام
  `systemRunPlan` القياسي هذا بوصفه السياق المرجعي للأمر/`cwd`/الجلسة.
- إذا عدّل مستدعٍ `command` أو`rawCommand` أو`cwd` أو`agentId` أو
  `sessionKey` بين التحضير وتمرير `system.run` الموافق عليه نهائيًا،
  يرفض gateway التشغيل بدلًا من الوثوق بالحمولة المعدلة.

## بديل تسليم الوكيل

- يمكن أن تتضمن طلبات `agent` القيمة `deliver=true` لطلب تسليم صادر.
- يحافظ `bestEffortDeliver=false` على السلوك الصارم: تعيد أهداف التسليم غير المحلولة أو الداخلية فقط القيمة `INVALID_REQUEST`.
- يسمح `bestEffortDeliver=true` بالرجوع إلى التنفيذ ضمن الجلسة فقط عندما يتعذر حل مسار خارجي قابل للتسليم (على سبيل المثال جلسات internal/webchat أو إعدادات متعددة القنوات ملتبسة).

## إدارة الإصدارات

- يوجد `PROTOCOL_VERSION` في `src/gateway/protocol/schema/protocol-schemas.ts`.
- يرسل العملاء `minProtocol` + `maxProtocol`؛ ويرفض الخادم حالات عدم التطابق.
- تُولَّد المخططات + النماذج من تعريفات TypeBox:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

### ثوابت العميل

يستخدم العميل المرجعي في `src/gateway/client.ts` هذه القيم الافتراضية. وهذه القيم
مستقرة عبر البروتوكول v3 وهي خط الأساس المتوقع لعملاء الجهات الخارجية.

| الثابت | الافتراضي | المصدر |
| --- | --- | --- |
| `PROTOCOL_VERSION` | `3` | `src/gateway/protocol/schema/protocol-schemas.ts` |
| مهلة الطلب (لكل RPC) | `30_000` ms | `src/gateway/client.ts` (`requestTimeoutMs`) |
| مهلة ما قبل المصادقة / تحدي الاتصال | `10_000` ms | `src/gateway/handshake-timeouts.ts` (التقييد `250`–`10_000`) |
| مهلة التراجع الأولية لإعادة الاتصال | `1_000` ms | `src/gateway/client.ts` (`backoffMs`) |
| الحد الأقصى لمهلة التراجع لإعادة الاتصال | `30_000` ms | `src/gateway/client.ts` (`scheduleReconnect`) |
| تقييد إعادة المحاولة السريعة بعد إغلاق رمز الجهاز المميز | `250` ms | `src/gateway/client.ts` |
| مهلة السماح قبل `terminate()` في الإيقاف القسري | `250` ms | `FORCE_STOP_TERMINATE_GRACE_MS` |
| المهلة الافتراضية لـ `stopAndWait()` | `1_000` ms | `STOP_AND_WAIT_TIMEOUT_MS` |
| الفاصل الزمني الافتراضي لـ tick (قبل `hello-ok`) | `30_000` ms | `src/gateway/client.ts` |
| إغلاق مهلة tick | الرمز `4000` عندما يتجاوز الصمت `tickIntervalMs * 2` | `src/gateway/client.ts` |
| `MAX_PAYLOAD_BYTES` | `25 * 1024 * 1024` (25 MB) | `src/gateway/server-constants.ts` |

يعلن الخادم عن القيم الفعالة `policy.tickIntervalMs` و`policy.maxPayload`
و`policy.maxBufferedBytes` في `hello-ok`؛ ويجب على العملاء الالتزام بهذه القيم
بدلًا من القيم الافتراضية السابقة للمصافحة.

## المصادقة

- تستخدم مصادقة Gateway ذات السر المشترك `connect.params.auth.token` أو
  `connect.params.auth.password`، بحسب وضع المصادقة المهيأ.
- الأوضاع الحاملة للهوية مثل Tailscale Serve
  (`gateway.auth.allowTailscale: true`) أو
  `gateway.auth.mode: "trusted-proxy"` غير المعتمد على loopback
  تستوفي فحص مصادقة الاتصال من ترويسات الطلب بدلًا من `connect.params.auth.*`.
- يتجاوز `gateway.auth.mode: "none"` الخاص بالإدخال الخاص مصادقة الاتصال
  ذات السر المشترك بالكامل؛ لا تعرّض هذا الوضع على إدخال عام/غير موثوق.
- بعد الإقران، يُصدر Gateway **رمز جهاز مميزًا** ذا نطاق محدد بحسب دور الاتصال + نطاقاته.
  ويُعاد ضمن `hello-ok.auth.deviceToken` ويجب أن يحتفظ به العميل
  للاتصالات المستقبلية.
- يجب على العملاء حفظ `hello-ok.auth.deviceToken` الأساسي بعد أي
  اتصال ناجح.
- يجب أن تؤدي إعادة الاتصال باستخدام رمز الجهاز المميز **المحفوظ** هذا أيضًا إلى إعادة استخدام
  مجموعة النطاقات الموافق عليها والمحفوظة لهذا الرمز. يحافظ ذلك على صلاحيات
  الوصول للقراءة/الفحص/الحالة التي مُنحت سابقًا ويتجنب تقليص عمليات
  إعادة الاتصال بصمت إلى نطاق إدارة ضمني أضيق فقط.
- تجميع مصادقة الاتصال على جانب العميل (`selectConnectAuth` في
  `src/gateway/client.ts`):
  - `auth.password` مستقل ويُمرَّر دائمًا عند ضبطه.
  - يُملأ `auth.token` وفق ترتيب أولوية: الرمز المشترك الصريح أولًا،
    ثم `deviceToken` صريح، ثم رمز محفوظ لكل جهاز (مفهرس حسب
    `deviceId` + `role`).
  - لا يُرسل `auth.bootstrapToken` إلا عندما لا يحل أي مما سبق قيمة
    `auth.token`. ويؤدي الرمز المشترك أو أي رمز جهاز مميز محلول إلى منعه.
  - الترقية التلقائية لرمز جهاز محفوظ في إعادة المحاولة الوحيدة
    `AUTH_TOKEN_MISMATCH` مقيّدة **بنقاط النهاية الموثوقة فقط** —
    loopback، أو `wss://` مع `tlsFingerprint` مثبت. ولا يُعد `wss://` العام
    من دون تثبيت مؤهلًا.
- تُعد إدخالات `hello-ok.auth.deviceTokens` الإضافية رموز تسليم bootstrap.
  احتفظ بها فقط عندما يكون الاتصال قد استخدم مصادقة bootstrap على نقل موثوق
  مثل `wss://` أو loopback/local pairing.
- إذا قدّم عميل `deviceToken` **صريحًا** أو `scopes` صريحة، فإن
  مجموعة النطاقات المطلوبة من المستدعي تبقى هي المرجع؛ ولا يُعاد استخدام
  النطاقات المخبأة إلا عندما يعيد العميل استخدام الرمز المحفوظ لكل جهاز.
- يمكن تدوير/إبطال رموز الأجهزة عبر `device.token.rotate` و
  `device.token.revoke` (ويتطلب ذلك النطاق `operator.pairing`).
- يظل إصدار/تدوير الرموز محصورًا ضمن مجموعة الأدوار الموافق عليها والمسجلة
  في إدخال إقران ذلك الجهاز؛ ولا يمكن لتدوير رمز أن يوسّع الجهاز إلى
  دور لم تمنحه موافقة الإقران أصلًا.
- بالنسبة إلى جلسات رموز الأجهزة المقترنة، تكون إدارة الأجهزة محصورة ذاتيًا ما لم يكن
  لدى المستدعي أيضًا `operator.admin`: لا يمكن للمستدعين غير الإداريين
  إزالة/إبطال/تدوير إلا إدخال أجهزتهم **هم فقط**.
- يتحقق `device.token.rotate` أيضًا من مجموعة نطاقات المشغّل المطلوبة مقارنةً بـ
  نطاقات جلسة المستدعي الحالية. ولا يمكن للمستدعين غير الإداريين تدوير رمز إلى
  مجموعة نطاقات مشغّل أوسع مما يملكونه بالفعل.
- تتضمن حالات فشل المصادقة `error.details.code` إضافةً إلى تلميحات الاسترداد:
  - `error.details.canRetryWithDeviceToken` (قيمة منطقية)
  - `error.details.recommendedNextStep` (`retry_with_device_token`، `update_auth_configuration`، `update_auth_credentials`، `wait_then_retry`، `review_auth_configuration`)
- سلوك العميل عند `AUTH_TOKEN_MISMATCH`:
  - يمكن للعملاء الموثوقين محاولة إعادة واحدة محدودة باستخدام رمز محفوظ لكل جهاز.
  - إذا فشلت إعادة المحاولة هذه، يجب على العملاء إيقاف حلقات إعادة الاتصال التلقائية
    وإظهار إرشادات للإجراء المطلوب من المشغّل.

## هوية الجهاز + الإقران

- يجب أن تتضمن العقد هوية جهاز ثابتة (`device.id`) مشتقة من
  بصمة زوج مفاتيح.
- تُصدر Gateways رموزًا مميزة لكل جهاز + دور.
- تتطلب معرّفات الأجهزة الجديدة موافقات إقران ما لم يكن التفعيل المحلي التلقائي
  للموافقة ممكّنًا.
- تتمحور الموافقة التلقائية على الإقران حول اتصالات loopback المحلية المباشرة.
- يوفّر OpenClaw أيضًا مسار self-connect ضيقًا محليًا للخلفية/الحاوية
  لتدفقات المساعد الموثوق ذات السر المشترك.
- لا تزال اتصالات tailnet أو LAN على نفس المضيف تُعامل على أنها بعيدة للإقران
  وتتطلب موافقة.
- يجب أن تتضمن جميع عملاء WS هوية `device` أثناء `connect` (operator + node).
  يمكن لـ Control UI حذفها فقط في هذه الأوضاع:
  - `gateway.controlUi.allowInsecureAuth=true` للتوافق مع HTTP غير الآمن على localhost فقط.
  - نجاح مصادقة operator في `gateway.auth.mode: "trusted-proxy"` لـ Control UI.
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true` (وضع طوارئ، خفض أمني شديد).
- يجب أن توقّع جميع الاتصالات قيمة nonce الخاصة بـ `connect.challenge` التي يوفرها الخادم.

### تشخيصات ترحيل مصادقة الجهاز

بالنسبة إلى العملاء القدامى الذين لا يزالون يستخدمون سلوك التوقيع السابق للتحدي، يعيد `connect` الآن
رموز التفاصيل `DEVICE_AUTH_*` ضمن `error.details.code` مع `error.details.reason` ثابتة.

أعطال الترحيل الشائعة:

| الرسالة | details.code | details.reason | المعنى |
| --------------------------- | -------------------------------- | ------------------------ | -------------------------------------------------- |
| `device nonce required` | `DEVICE_AUTH_NONCE_REQUIRED` | `device-nonce-missing` | لم يرسل العميل `device.nonce` (أو أرسله فارغًا). |
| `device nonce mismatch` | `DEVICE_AUTH_NONCE_MISMATCH` | `device-nonce-mismatch` | وقّع العميل باستخدام nonce قديم/خاطئ. |
| `device signature invalid` | `DEVICE_AUTH_SIGNATURE_INVALID` | `device-signature` | لا تطابق حمولة التوقيع حمولة v2. |
| `device signature expired` | `DEVICE_AUTH_SIGNATURE_EXPIRED` | `device-signature-stale` | الطابع الزمني الموقّع خارج مقدار الانحراف المسموح. |
| `device identity mismatch` | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch` | لا يطابق `device.id` بصمة المفتاح العام. |
| `device public key invalid` | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key` | فشل تنسيق/تطبيع المفتاح العام. |

هدف الترحيل:

- انتظر دائمًا `connect.challenge`.
- وقّع حمولة v2 التي تتضمن nonce الخاص بالخادم.
- أرسل nonce نفسه في `connect.params.device.nonce`.
- حمولة التوقيع المفضلة هي `v3`، التي تربط `platform` و`deviceFamily`
  بالإضافة إلى حقول device/client/role/scopes/token/nonce.
- لا تزال توقيعات `v2` القديمة مقبولة للتوافق، لكن تثبيت بيانات
  الأجهزة المقترنة الوصفية ما يزال يتحكم في سياسة الأوامر عند إعادة الاتصال.

## TLS + التثبيت

- يدعم TLS اتصالات WS.
- يمكن للعملاء اختياريًا تثبيت بصمة شهادة gateway (راجع تهيئة `gateway.tls`
  إضافةً إلى `gateway.remote.tlsFingerprint` أو خيار CLI ‏`--tls-fingerprint`).

## النطاق

يعرض هذا البروتوكول **واجهة API الكاملة لـ gateway** (الحالة، والقنوات، والنماذج، والدردشة،
والوكيل، والجلسات، والعقد، والموافقات، وغير ذلك). ويُعرَّف السطح الدقيق بواسطة
مخططات TypeBox في `src/gateway/protocol/schema.ts`.
