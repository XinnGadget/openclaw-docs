---
read_when:
    - عند العمل على سلوك قناة WhatsApp/الويب أو توجيه صندوق الوارد
summary: دعم قناة WhatsApp، وعناصر التحكم في الوصول، وسلوك التسليم، والعمليات
title: WhatsApp
x-i18n:
    generated_at: "2026-04-07T07:16:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9e2ce84d869ace6c0bebd9ec17bdbbef997a5c31e5da410b02a19a0f103f7359
    source_path: channels/whatsapp.md
    workflow: 15
---

# WhatsApp (قناة الويب)

الحالة: جاهزة للإنتاج عبر WhatsApp Web ‏(Baileys). تتولى البوابة جلسة/جلسات الربط.

## التثبيت (عند الطلب)

- الإعداد (`openclaw onboard`) و `openclaw channels add --channel whatsapp`
  يطالبان بتثبيت إضافة WhatsApp أول مرة تحددها فيها.
- يوفّر `openclaw channels login --channel whatsapp` أيضًا تدفق التثبيت عندما
  لا تكون الإضافة موجودة بعد.
- قناة التطوير + سحب git: يُستخدم مسار الإضافة المحلي افتراضيًا.
- Stable/Beta: تُستخدم حزمة npm ‏`@openclaw/whatsapp` افتراضيًا.

يبقى التثبيت اليدوي متاحًا:

```bash
openclaw plugins install @openclaw/whatsapp
```

<CardGroup cols={3}>
  <Card title="الاقتران" icon="link" href="/ar/channels/pairing">
    سياسة الرسائل الخاصة الافتراضية هي الاقتران للمرسلين غير المعروفين.
  </Card>
  <Card title="استكشاف أخطاء القناة وإصلاحها" icon="wrench" href="/ar/channels/troubleshooting">
    تشخيصات متعددة القنوات وكتيبات الإصلاح.
  </Card>
  <Card title="إعدادات البوابة" icon="settings" href="/ar/gateway/configuration">
    أنماط وأمثلة كاملة لإعداد القنوات.
  </Card>
</CardGroup>

## إعداد سريع

<Steps>
  <Step title="تكوين سياسة الوصول في WhatsApp">

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      allowFrom: ["+15551234567"],
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
}
```

  </Step>

  <Step title="ربط WhatsApp ‏(QR)">

```bash
openclaw channels login --channel whatsapp
```

    لحساب معيّن:

```bash
openclaw channels login --channel whatsapp --account work
```

  </Step>

  <Step title="بدء تشغيل البوابة">

```bash
openclaw gateway
```

  </Step>

  <Step title="الموافقة على أول طلب اقتران (إذا كنت تستخدم وضع الاقتران)">

```bash
openclaw pairing list whatsapp
openclaw pairing approve whatsapp <CODE>
```

    تنتهي صلاحية طلبات الاقتران بعد ساعة واحدة. ويكون الحد الأقصى للطلبات المعلّقة 3 لكل قناة.

  </Step>
</Steps>

<Note>
يوصي OpenClaw بتشغيل WhatsApp على رقم منفصل كلما أمكن. (البيانات الوصفية للقناة وتدفق الإعداد محسّنان لهذا الإعداد، لكن إعدادات الأرقام الشخصية مدعومة أيضًا.)
</Note>

## أنماط النشر

<AccordionGroup>
  <Accordion title="رقم مخصص (موصى به)">
    هذا هو وضع التشغيل الأنظف:

    - هوية WhatsApp منفصلة لـ OpenClaw
    - حدود أوضح لقوائم السماح في الرسائل الخاصة والتوجيه
    - احتمال أقل لحدوث ارتباك في الدردشة الذاتية

    نمط السياسة الأدنى:

    ```json5
    {
      channels: {
        whatsapp: {
          dmPolicy: "allowlist",
          allowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="العودة إلى الرقم الشخصي">
    يدعم الإعداد وضع الرقم الشخصي ويكتب خط أساس مناسبًا للدردشة الذاتية:

    - `dmPolicy: "allowlist"`
    - يتضمن `allowFrom` رقمك الشخصي
    - `selfChatMode: true`

    أثناء التشغيل، تعتمد وسائل الحماية الخاصة بالدردشة الذاتية على الرقم الذاتي المرتبط و `allowFrom`.

  </Accordion>

  <Accordion title="نطاق قناة WhatsApp Web فقط">
    قناة منصة المراسلة تعتمد على WhatsApp Web ‏(`Baileys`) في بنية قنوات OpenClaw الحالية.

    لا توجد قناة مراسلة WhatsApp منفصلة عبر Twilio في سجل قنوات الدردشة المضمّن.

  </Accordion>
</AccordionGroup>

## نموذج التشغيل

- تتولى البوابة مقبس WhatsApp وحلقة إعادة الاتصال.
- تتطلب عمليات الإرسال الصادرة مستمع WhatsApp نشطًا للحساب المستهدف.
- يتم تجاهل محادثات الحالة والبث (`@status`, `@broadcast`).
- تستخدم المحادثات المباشرة قواعد جلسة الرسائل الخاصة (`session.dmScope`؛ والقيمة الافتراضية `main` تدمج الرسائل الخاصة في الجلسة الرئيسية للوكيل).
- جلسات المجموعات معزولة (`agent:<agentId>:whatsapp:group:<jid>`).
- يراعي نقل WhatsApp Web متغيرات بيئة الوكيل القياسية على مضيف البوابة (`HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY` / والمتغيرات المكافئة بالأحرف الصغيرة). يُفضَّل إعداد الوكيل على مستوى المضيف بدلًا من إعدادات وكيل WhatsApp الخاصة بالقناة.

## التحكم في الوصول والتفعيل

<Tabs>
  <Tab title="سياسة الرسائل الخاصة">
    يتحكم `channels.whatsapp.dmPolicy` في الوصول إلى المحادثات المباشرة:

    - `pairing` (الافتراضي)
    - `allowlist`
    - `open` (يتطلب أن يتضمن `allowFrom` القيمة `"*"`)
    - `disabled`

    يقبل `allowFrom` أرقامًا بنمط E.164 (مع تسويتها داخليًا).

    تجاوز متعدد الحسابات: يحظى `channels.whatsapp.accounts.<id>.dmPolicy` (و `allowFrom`) بالأولوية على الإعدادات الافتراضية على مستوى القناة لذلك الحساب.

    تفاصيل سلوك التشغيل:

    - يتم الاحتفاظ بعمليات الاقتران في مخزن السماح الخاص بالقناة ودمجها مع `allowFrom` المكوَّنة
    - إذا لم تُكوَّن قائمة سماح، فسيُسمح بالرقم الذاتي المرتبط افتراضيًا
    - لا تُقرن الرسائل الخاصة الصادرة `fromMe` تلقائيًا أبدًا

  </Tab>

  <Tab title="سياسة المجموعات + قوائم السماح">
    يمتلك الوصول إلى المجموعات طبقتين:

    1. **قائمة سماح عضوية المجموعة** (`channels.whatsapp.groups`)
       - إذا تم حذف `groups`، تكون كل المجموعات مؤهلة
       - إذا كانت `groups` موجودة، فإنها تعمل كقائمة سماح للمجموعات (مع السماح بـ `"*"`)

    2. **سياسة مرسل المجموعة** (`channels.whatsapp.groupPolicy` + `groupAllowFrom`)
       - `open`: يتم تجاوز قائمة سماح المرسل
       - `allowlist`: يجب أن يطابق المرسل `groupAllowFrom` (أو `*`)
       - `disabled`: حظر كل الرسائل الواردة من المجموعات

    بديل قائمة سماح المرسل:

    - إذا لم يتم تعيين `groupAllowFrom`، يعود التشغيل إلى `allowFrom` عند توفره
    - تُقيَّم قوائم سماح المرسلين قبل تفعيل الإشارة/الرد

    ملاحظة: إذا لم توجد كتلة `channels.whatsapp` على الإطلاق، فسيكون بديل سياسة المجموعات أثناء التشغيل هو `allowlist` (مع سجل تحذير)، حتى إذا كانت `channels.defaults.groupPolicy` معيّنة.

  </Tab>

  <Tab title="الإشارات + /activation">
    تتطلب ردود المجموعات الإشارة بشكل افتراضي.

    يتضمن اكتشاف الإشارة ما يلي:

    - إشارات WhatsApp الصريحة لهوية الروبوت
    - أنماط regex للإشارة المكوّنة (`agents.list[].groupChat.mentionPatterns`، والبديل `messages.groupChat.mentionPatterns`)
    - اكتشاف الرد الضمني على الروبوت (يطابق مرسل الرد هوية الروبوت)

    ملاحظة أمنية:

    - يلبّي الاقتباس/الرد فقط بوابة الإشارة؛ لكنه **لا** يمنح تفويضًا للمرسل
    - مع `groupPolicy: "allowlist"`، يظل المرسلون غير المدرجين في قائمة السماح محظورين حتى إذا ردوا على رسالة مستخدم مدرج في القائمة

    أمر التفعيل على مستوى الجلسة:

    - `/activation mention`
    - `/activation always`

    يحدّث `activation` حالة الجلسة (وليس الإعداد العام). وهو مقيّد بالمالك.

  </Tab>
</Tabs>

## سلوك الرقم الشخصي والدردشة الذاتية

عندما يكون الرقم الذاتي المرتبط موجودًا أيضًا في `allowFrom`، يتم تفعيل وسائل الحماية الخاصة بالدردشة الذاتية في WhatsApp:

- تخطي إيصالات القراءة في دورات الدردشة الذاتية
- تجاهل سلوك التشغيل التلقائي لإشارة JID الذي قد يؤدي بخلاف ذلك إلى تنبيهك أنت نفسك
- إذا لم يتم تعيين `messages.responsePrefix`، فستكون بادئة ردود الدردشة الذاتية افتراضيًا `[{identity.name}]` أو `[openclaw]`

## تسوية الرسائل والسياق

<AccordionGroup>
  <Accordion title="غلاف الوارد + سياق الرد">
    تُغلّف رسائل WhatsApp الواردة داخل الغلاف المشترك للوارد.

    إذا وُجد رد مقتبس، يُضاف السياق بهذا الشكل:

    ```text
    [Replying to <sender> id:<stanzaId>]
    <quoted body or media placeholder>
    [/Replying]
    ```

    تُعبّأ أيضًا حقول بيانات تعريف الرد عند توفرها (`ReplyToId`, `ReplyToBody`, `ReplyToSender`, ومرسل JID/E.164).

  </Accordion>

  <Accordion title="العناصر النائبة للوسائط واستخراج الموقع/جهة الاتصال">
    تتم تسوية الرسائل الواردة التي تحتوي على وسائط فقط بعناصر نائبة مثل:

    - `<media:image>`
    - `<media:video>`
    - `<media:audio>`
    - `<media:document>`
    - `<media:sticker>`

    تتم تسوية حمولات الموقع وجهة الاتصال إلى سياق نصي قبل التوجيه.

  </Accordion>

  <Accordion title="حقن سجل المجموعة المعلّق">
    بالنسبة للمجموعات، يمكن تخزين الرسائل غير المعالجة مؤقتًا وحقنها كسياق عندما يتم تشغيل الروبوت أخيرًا.

    - الحد الافتراضي: `50`
    - الإعداد: `channels.whatsapp.historyLimit`
    - البديل: `messages.groupChat.historyLimit`
    - `0` يعطّل الميزة

    علامات الحقن:

    - `[Chat messages since your last reply - for context]`
    - `[Current message - respond to this]`

  </Accordion>

  <Accordion title="إيصالات القراءة">
    تكون إيصالات القراءة مفعّلة افتراضيًا لرسائل WhatsApp الواردة المقبولة.

    للتعطيل على مستوى عام:

    ```json5
    {
      channels: {
        whatsapp: {
          sendReadReceipts: false,
        },
      },
    }
    ```

    تجاوز لكل حساب:

    ```json5
    {
      channels: {
        whatsapp: {
          accounts: {
            work: {
              sendReadReceipts: false,
            },
          },
        },
      },
    }
    ```

    تتخطى دورات الدردشة الذاتية إيصالات القراءة حتى عند تفعيلها على مستوى عام.

  </Accordion>
</AccordionGroup>

## التسليم، والتقسيم، والوسائط

<AccordionGroup>
  <Accordion title="تقسيم النص">
    - الحد الافتراضي للتقسيم: `channels.whatsapp.textChunkLimit = 4000`
    - `channels.whatsapp.chunkMode = "length" | "newline"`
    - يفضّل وضع `newline` حدود الفقرات (الأسطر الفارغة)، ثم يعود إلى تقسيم آمن بحسب الطول
  </Accordion>

  <Accordion title="سلوك الوسائط الصادرة">
    - يدعم حمولات الصور والفيديو والصوت (مذكرة صوتية PTT) والمستندات
    - يُعاد كتابة `audio/ogg` إلى `audio/ogg; codecs=opus` لتوافق الملاحظات الصوتية
    - يتم دعم تشغيل GIF المتحرك عبر `gifPlayback: true` عند إرسال الفيديو
    - تُطبّق التسميات التوضيحية على أول عنصر وسائط عند إرسال حمولات رد متعددة الوسائط
    - يمكن أن يكون مصدر الوسائط HTTP(S) أو `file://` أو مسارات محلية
  </Accordion>

  <Accordion title="حدود حجم الوسائط وسلوك الرجوع">
    - الحد الأقصى لحفظ الوسائط الواردة: `channels.whatsapp.mediaMaxMb` (الافتراضي `50`)
    - الحد الأقصى لإرسال الوسائط الصادرة: `channels.whatsapp.mediaMaxMb` (الافتراضي `50`)
    - تستخدم التجاوزات لكل حساب `channels.whatsapp.accounts.<accountId>.mediaMaxMb`
    - تُحسَّن الصور تلقائيًا (تغيير الحجم/اختبار الجودة) لتلائم الحدود
    - عند فشل إرسال الوسائط، يرسل الرجوع الخاص بالعنصر الأول تحذيرًا نصيًا بدلًا من إسقاط الرد بصمت
  </Accordion>
</AccordionGroup>

## مستوى التفاعلات

يتحكم `channels.whatsapp.reactionLevel` في مدى استخدام الوكيل لتفاعلات الإيموجي على WhatsApp:

| المستوى      | تفاعلات الإقرار | تفاعلات يبدأها الوكيل | الوصف                                            |
| ------------ | --------------- | ---------------------- | ------------------------------------------------ |
| `"off"`      | لا              | لا                     | بدون أي تفاعلات على الإطلاق                      |
| `"ack"`      | نعم             | لا                     | تفاعلات الإقرار فقط (إقرار ما قبل الرد)          |
| `"minimal"`  | نعم             | نعم (بحذر)            | الإقرار + تفاعلات الوكيل مع إرشادات متحفظة       |
| `"extensive"`| نعم             | نعم (مستحسنة)         | الإقرار + تفاعلات الوكيل مع إرشادات مشجعة        |

الافتراضي: `"minimal"`.

تستخدم التجاوزات لكل حساب `channels.whatsapp.accounts.<id>.reactionLevel`.

```json5
{
  channels: {
    whatsapp: {
      reactionLevel: "ack",
    },
  },
}
```

## تفاعلات الإقرار

يدعم WhatsApp تفاعلات الإقرار الفورية عند استلام الرسائل الواردة عبر `channels.whatsapp.ackReaction`.
تخضع تفاعلات الإقرار لـ `reactionLevel` — ويتم كبتها عندما تكون قيمة `reactionLevel` هي `"off"`.

```json5
{
  channels: {
    whatsapp: {
      ackReaction: {
        emoji: "👀",
        direct: true,
        group: "mentions", // always | mentions | never
      },
    },
  },
}
```

ملاحظات السلوك:

- تُرسل فورًا بعد قبول الوارد (قبل الرد)
- يتم تسجيل الإخفاقات لكنها لا تمنع تسليم الرد العادي
- يتفاعل وضع المجموعة `mentions` في الدورات التي يتم تشغيلها بالإشارة؛ ويعمل تفعيل المجموعة `always` كتجاوز لهذا الفحص
- يستخدم WhatsApp ‏`channels.whatsapp.ackReaction` (ولا يُستخدم هنا الإرثي `messages.ackReaction`)

## الحسابات المتعددة وبيانات الاعتماد

<AccordionGroup>
  <Accordion title="اختيار الحساب والإعدادات الافتراضية">
    - تأتي معرّفات الحسابات من `channels.whatsapp.accounts`
    - اختيار الحساب الافتراضي: `default` إذا كان موجودًا، وإلا أول معرّف حساب مُكوَّن (بعد الفرز)
    - تتم تسوية معرّفات الحسابات داخليًا لأغراض البحث
  </Accordion>

  <Accordion title="مسارات بيانات الاعتماد والتوافق مع الإصدارات السابقة">
    - مسار المصادقة الحالي: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
    - ملف النسخة الاحتياطية: `creds.json.bak`
    - لا يزال يتم التعرّف على المصادقة الافتراضية القديمة في `~/.openclaw/credentials/` وترحيلها لتدفقات الحساب الافتراضي
  </Accordion>

  <Accordion title="سلوك تسجيل الخروج">
    يقوم `openclaw channels logout --channel whatsapp [--account <id>]` بمسح حالة مصادقة WhatsApp لذلك الحساب.

    في أدلة المصادقة القديمة، يتم الاحتفاظ بـ `oauth.json` بينما تتم إزالة ملفات مصادقة Baileys.

  </Accordion>
</AccordionGroup>

## الأدوات والإجراءات وكتابة الإعدادات

- يتضمن دعم أدوات الوكيل إجراء تفاعل WhatsApp ‏(`react`).
- بوابات الإجراءات:
  - `channels.whatsapp.actions.reactions`
  - `channels.whatsapp.actions.polls`
- تكون عمليات كتابة الإعدادات التي تبدأها القناة مفعّلة افتراضيًا (يمكن تعطيلها عبر `channels.whatsapp.configWrites=false`).

## استكشاف الأخطاء وإصلاحها

<AccordionGroup>
  <Accordion title="غير مرتبط (يتطلب QR)">
    العَرَض: تشير حالة القناة إلى أنها غير مرتبطة.

    الإصلاح:

    ```bash
    openclaw channels login --channel whatsapp
    openclaw channels status
    ```

  </Accordion>

  <Accordion title="مرتبط ولكن غير متصل / حلقة إعادة الاتصال">
    العَرَض: حساب مرتبط مع انقطاعات متكررة أو محاولات إعادة اتصال.

    الإصلاح:

    ```bash
    openclaw doctor
    openclaw logs --follow
    ```

    عند الحاجة، أعد الربط باستخدام `channels login`.

  </Accordion>

  <Accordion title="لا يوجد مستمع نشط عند الإرسال">
    تفشل عمليات الإرسال الصادرة سريعًا عندما لا يوجد مستمع بوابة نشط للحساب المستهدف.

    تأكد من أن البوابة قيد التشغيل وأن الحساب مرتبط.

  </Accordion>

  <Accordion title="يتم تجاهل رسائل المجموعات بشكل غير متوقع">
    تحقق بهذا الترتيب:

    - `groupPolicy`
    - `groupAllowFrom` / `allowFrom`
    - إدخالات قائمة السماح `groups`
    - بوابة الإشارة (`requireMention` + أنماط الإشارة)
    - المفاتيح المكررة في `openclaw.json` ‏(JSON5): الإدخالات اللاحقة تتجاوز السابقة، لذا احتفظ بقيمة `groupPolicy` واحدة لكل نطاق

  </Accordion>

  <Accordion title="تحذير وقت تشغيل Bun">
    يجب أن يستخدم وقت تشغيل بوابة WhatsApp ‏Node. ويتم تمييز Bun على أنه غير متوافق لتشغيل بوابة WhatsApp/Telegram بشكل مستقر.
  </Accordion>
</AccordionGroup>

## مؤشرات مرجعية للإعداد

المرجع الأساسي:

- [مرجع الإعداد - WhatsApp](/ar/gateway/configuration-reference#whatsapp)

حقول WhatsApp عالية الأهمية:

- الوصول: `dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`
- التسليم: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `sendReadReceipts`, `ackReaction`, `reactionLevel`
- الحسابات المتعددة: `accounts.<id>.enabled`, `accounts.<id>.authDir`, والتجاوزات على مستوى الحساب
- العمليات: `configWrites`, `debounceMs`, `web.enabled`, `web.heartbeatSeconds`, `web.reconnect.*`
- سلوك الجلسة: `session.dmScope`, `historyLimit`, `dmHistoryLimit`, `dms.<id>.historyLimit`

## ذو صلة

- [الاقتران](/ar/channels/pairing)
- [المجموعات](/ar/channels/groups)
- [الأمان](/ar/gateway/security)
- [توجيه القنوات](/ar/channels/channel-routing)
- [التوجيه متعدد الوكلاء](/ar/concepts/multi-agent)
- [استكشاف الأخطاء وإصلاحها](/ar/channels/troubleshooting)
