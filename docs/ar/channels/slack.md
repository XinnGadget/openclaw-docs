---
read_when:
    - إعداد Slack أو تصحيح أخطاء وضع socket/HTTP في Slack
summary: إعداد Slack وسلوك وقت التشغيل (Socket Mode + عناوين URL لطلبات HTTP)
title: Slack
x-i18n:
    generated_at: "2026-04-07T07:17:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2b8fd2cc6c638ee82069f0af2c2b6f6f49c87da709b941433a0343724a9907ea
    source_path: channels/slack.md
    workflow: 15
---

# Slack

الحالة: جاهز للإنتاج للرسائل الخاصة + القنوات عبر تكاملات تطبيق Slack. الوضع الافتراضي هو Socket Mode؛ كما أن عناوين URL لطلبات HTTP مدعومة أيضًا.

<CardGroup cols={3}>
  <Card title="الاقتران" icon="link" href="/ar/channels/pairing">
    الرسائل الخاصة في Slack تستخدم وضع الاقتران افتراضيًا.
  </Card>
  <Card title="أوامر الشرطة المائلة" icon="terminal" href="/ar/tools/slash-commands">
    سلوك الأوامر الأصلي وفهرس الأوامر.
  </Card>
  <Card title="استكشاف أخطاء القنوات وإصلاحها" icon="wrench" href="/ar/channels/troubleshooting">
    التشخيصات المشتركة بين القنوات وأدلة الإصلاح.
  </Card>
</CardGroup>

## إعداد سريع

<Tabs>
  <Tab title="Socket Mode (الافتراضي)">
    <Steps>
      <Step title="أنشئ تطبيق Slack جديدًا">
        في إعدادات تطبيق Slack اضغط زر **[Create New App](https://api.slack.com/apps/new)**:

        - اختر **from a manifest** وحدد مساحة عمل لتطبيقك
        - الصق [نموذج manifest المثال](#manifest-and-scope-checklist) أدناه وتابع الإنشاء
        - أنشئ **App-Level Token** (`xapp-...`) مع `connections:write`
        - ثبّت التطبيق وانسخ **Bot Token** (`xoxb-...`) الظاهر
      </Step>

      <Step title="اضبط OpenClaw">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "socket",
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

        بديل متغيرات البيئة (للحساب الافتراضي فقط):

```bash
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
```

      </Step>

      <Step title="ابدأ البوابة">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="عناوين URL لطلبات HTTP">
    <Steps>
      <Step title="أنشئ تطبيق Slack جديدًا">
        في إعدادات تطبيق Slack اضغط زر **[Create New App](https://api.slack.com/apps/new)**:

        - اختر **from a manifest** وحدد مساحة عمل لتطبيقك
        - الصق [نموذج manifest المثال](#manifest-and-scope-checklist) وحدّث عناوين URL قبل الإنشاء
        - احفظ **Signing Secret** للتحقق من الطلبات
        - ثبّت التطبيق وانسخ **Bot Token** (`xoxb-...`) الظاهر

      </Step>

      <Step title="اضبط OpenClaw">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "your-signing-secret",
      webhookPath: "/slack/events",
    },
  },
}
```

        <Note>
        استخدم مسارات webhook فريدة لـ HTTP متعدد الحسابات

        امنح كل حساب `webhookPath` مختلفًا (الافتراضي `/slack/events`) حتى لا تتصادم التسجيلات.
        </Note>

      </Step>

      <Step title="ابدأ البوابة">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>
</Tabs>

## قائمة مراجعة manifest والنطاقات

<Tabs>
  <Tab title="Socket Mode (الافتراضي)">

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    }
  }
}
```

  </Tab>

  <Tab title="عناوين URL لطلبات HTTP">

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false,
        "url": "https://gateway-host.example.com/slack/events"
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "event_subscriptions": {
      "request_url": "https://gateway-host.example.com/slack/events",
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    },
    "interactivity": {
      "is_enabled": true,
      "request_url": "https://gateway-host.example.com/slack/events",
      "message_menu_options_url": "https://gateway-host.example.com/slack/events"
    }
  }
}
```

  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="نطاقات تأليف اختيارية (عمليات الكتابة)">
    أضف نطاق البوت `chat:write.customize` إذا كنت تريد أن تستخدم الرسائل الصادرة هوية الوكيل النشطة (اسم مستخدم وأيقونة مخصصين) بدلًا من هوية تطبيق Slack الافتراضية.

    إذا كنت تستخدم أيقونة emoji، فإن Slack يتوقع صيغة `:emoji_name:`.
  </Accordion>
  <Accordion title="نطاقات user-token اختيارية (عمليات القراءة)">
    إذا قمت بإعداد `channels.slack.userToken`، فإن نطاقات القراءة المعتادة هي:

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read` (إذا كنت تعتمد على قراءات البحث في Slack)

  </Accordion>
</AccordionGroup>

## نموذج الرموز المميزة

- `botToken` + `appToken` مطلوبان لـ Socket Mode.
- يتطلب وضع HTTP `botToken` + `signingSecret`.
- تقبل `botToken` و`appToken` و`signingSecret` و`userToken` سلاسل
  نصية صريحة أو كائنات SecretRef.
- تتجاوز رموز الإعداد بديل متغيرات البيئة.
- ينطبق بديل متغيرات البيئة `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` على الحساب الافتراضي فقط.
- `userToken` (`xoxp-...`) خاص بالإعداد فقط (لا يوجد بديل من متغيرات البيئة) ويكون افتراضيًا بسلوك للقراءة فقط (`userTokenReadOnly: true`).

سلوك لقطة الحالة:

- يتتبع فحص حساب Slack حقول `*Source` و`*Status`
  لكل بيانات اعتماد (`botToken`, `appToken`, `signingSecret`, `userToken`).
- تكون الحالة `available` أو `configured_unavailable` أو `missing`.
- تعني `configured_unavailable` أن الحساب مُعد عبر SecretRef
  أو مصدر أسرار غير مضمن آخر، لكن مسار الأمر/وقت التشغيل الحالي
  لم يتمكن من حل القيمة الفعلية.
- في وضع HTTP، يتم تضمين `signingSecretStatus`؛ وفي Socket Mode،
  يكون الزوج المطلوب هو `botTokenStatus` + `appTokenStatus`.

<Tip>
بالنسبة للإجراءات/قراءات الدليل، يمكن تفضيل user token عند إعداده. بالنسبة للكتابة، يظل bot token هو المفضل؛ ولا يُسمح بعمليات الكتابة باستخدام user-token إلا عندما يكون `userTokenReadOnly: false` ويكون bot token غير متاح.
</Tip>

## الإجراءات والبوابات

يتم التحكم في إجراءات Slack بواسطة `channels.slack.actions.*`.

مجموعات الإجراءات المتاحة في أدوات Slack الحالية:

| المجموعة | الافتراضي |
| ---------- | ------- |
| messages   | مفعّل |
| reactions  | مفعّل |
| pins       | مفعّل |
| memberInfo | مفعّل |
| emojiList  | مفعّل |

تشمل إجراءات رسائل Slack الحالية `send` و`upload-file` و`download-file` و`read` و`edit` و`delete` و`pin` و`unpin` و`list-pins` و`member-info` و`emoji-list`.

## التحكم في الوصول والتوجيه

<Tabs>
  <Tab title="سياسة الرسائل الخاصة">
    يتحكم `channels.slack.dmPolicy` في الوصول إلى الرسائل الخاصة (قديمًا: `channels.slack.dm.policy`):

    - `pairing` (الافتراضي)
    - `allowlist`
    - `open` (يتطلب أن يتضمن `channels.slack.allowFrom` القيمة `"*"`؛ قديمًا: `channels.slack.dm.allowFrom`)
    - `disabled`

    علامات الرسائل الخاصة:

    - `dm.enabled` (الافتراضي true)
    - `channels.slack.allowFrom` (المفضل)
    - `dm.allowFrom` (قديم)
    - `dm.groupEnabled` (الرسائل الخاصة الجماعية افتراضيًا false)
    - `dm.groupChannels` (قائمة سماح اختيارية لـ MPIM)

    أولوية الحسابات المتعددة:

    - `channels.slack.accounts.default.allowFrom` ينطبق فقط على الحساب `default`.
    - ترث الحسابات المسماة `channels.slack.allowFrom` عندما لا يتم تعيين `allowFrom` الخاص بها.
    - لا ترث الحسابات المسماة `channels.slack.accounts.default.allowFrom`.

    يستخدم الاقتران في الرسائل الخاصة `openclaw pairing approve slack <code>`.

  </Tab>

  <Tab title="سياسة القنوات">
    يتحكم `channels.slack.groupPolicy` في التعامل مع القنوات:

    - `open`
    - `allowlist`
    - `disabled`

    توجد قائمة سماح القنوات تحت `channels.slack.channels` ويجب أن تستخدم معرّفات قنوات مستقرة.

    ملاحظة وقت التشغيل: إذا كان `channels.slack` مفقودًا بالكامل (إعداد يعتمد على متغيرات البيئة فقط)، يعود وقت التشغيل إلى `groupPolicy="allowlist"` ويسجل تحذيرًا (حتى لو كان `channels.defaults.groupPolicy` مضبوطًا).

    حل الاسم/المعرّف:

    - يتم حل إدخالات قائمة سماح القنوات وإدخالات قائمة سماح الرسائل الخاصة عند بدء التشغيل عندما يسمح الوصول إلى الرمز بذلك
    - تُحتفظ بإدخالات أسماء القنوات غير المحلولة كما هي في الإعداد، لكنها تُتجاهل افتراضيًا في التوجيه
    - يكون تفويض الرسائل الواردة وتوجيه القنوات قائمًا على المعرّف أولًا افتراضيًا؛ وتتطلب المطابقة المباشرة لاسم المستخدم/الاسم المختصر `channels.slack.dangerouslyAllowNameMatching: true`

  </Tab>

  <Tab title="الإشارات ومستخدمي القنوات">
    تكون رسائل القنوات مقيدة بالإشارة افتراضيًا.

    مصادر الإشارة:

    - إشارة صريحة للتطبيق (`<@botId>`)
    - أنماط regex للإشارة (`agents.list[].groupChat.mentionPatterns`، والبديل `messages.groupChat.mentionPatterns`)
    - سلوك ضمني لخيط الرد إلى البوت (يتم تعطيله عندما تكون `thread.requireExplicitMention` مساوية لـ `true`)

    عناصر التحكم لكل قناة (`channels.slack.channels.<id>`؛ الأسماء فقط عبر الحل عند بدء التشغيل أو `dangerouslyAllowNameMatching`):

    - `requireMention`
    - `users` (قائمة سماح)
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - صيغة مفتاح `toolsBySender`: ‏`id:` أو `e164:` أو `username:` أو `name:` أو البدل `"*"`
      (لا تزال المفاتيح القديمة غير المسبوقة تُربط بـ `id:` فقط)

  </Tab>
</Tabs>

## الخيوط والجلسات وعلامات الرد

- يتم توجيه الرسائل الخاصة كـ `direct`؛ والقنوات كـ `channel`؛ وMPIMs كـ `group`.
- مع الإعداد الافتراضي `session.dmScope=main`، تُدمج الرسائل الخاصة في Slack في الجلسة الرئيسية للوكيل.
- جلسات القنوات: `agent:<agentId>:slack:channel:<channelId>`.
- يمكن أن تنشئ ردود الخيوط لاحقات جلسة للخيط (`:thread:<threadTs>`) عند الاقتضاء.
- القيمة الافتراضية لـ `channels.slack.thread.historyScope` هي `thread`؛ والقيمة الافتراضية لـ `thread.inheritParent` هي `false`.
- يتحكم `channels.slack.thread.initialHistoryLimit` في عدد رسائل الخيط الموجودة التي يتم جلبها عند بدء جلسة خيط جديدة (الافتراضي `20`؛ اضبطه على `0` للتعطيل).
- `channels.slack.thread.requireExplicitMention` (الافتراضي `false`): عندما تكون `true`، يتم منع الإشارات الضمنية في الخيوط بحيث لا يرد البوت إلا على إشارات `@bot` الصريحة داخل الخيوط، حتى عندما يكون البوت قد شارك بالفعل في الخيط. وبدون هذا، فإن الردود في خيط شارك فيه البوت تتجاوز بوابة `requireMention`.

عناصر التحكم في خيوط الرد:

- `channels.slack.replyToMode`: ‏`off|first|all|batched` (الافتراضي `off`)
- `channels.slack.replyToModeByChatType`: لكل من `direct|group|channel`
- البديل القديم للمحادثات المباشرة: `channels.slack.dm.replyToMode`

علامات الرد اليدوية مدعومة:

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

ملاحظة: يؤدي `replyToMode="off"` إلى تعطيل **كل** خيوط الرد في Slack، بما في ذلك علامات `[[reply_to_*]]` الصريحة. يختلف هذا عن Telegram، حيث لا تزال العلامات الصريحة تُحترم في وضع `"off"`. يعكس هذا الاختلاف نماذج الخيوط الخاصة بكل منصة: إذ تُخفي خيوط Slack الرسائل عن القناة، بينما تظل ردود Telegram مرئية في تدفق المحادثة الرئيسي.

## تفاعلات التأكيد

يرسل `ackReaction` emoji للتأكيد بينما يعالج OpenClaw رسالة واردة.

ترتيب الحل:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- بديل emoji لهوية الوكيل (`agents.list[].identity.emoji`، وإلا `"👀"`)

ملاحظات:

- يتوقع Slack رموزًا قصيرة (مثل `"eyes"`).
- استخدم `""` لتعطيل التفاعل لهذا الحساب في Slack أو بشكل عام.

## بث النص

يتحكم `channels.slack.streaming` في سلوك المعاينة المباشرة:

- `off`: تعطيل بث المعاينة المباشرة.
- `partial` (الافتراضي): استبدال نص المعاينة بأحدث إخراج جزئي.
- `block`: إلحاق تحديثات معاينة مجزأة.
- `progress`: إظهار نص حالة التقدم أثناء الإنشاء، ثم إرسال النص النهائي.

يتحكم `channels.slack.nativeStreaming` في البث النصي الأصلي لـ Slack عندما تكون `streaming` مساوية لـ `partial` (الافتراضي: `true`).

- يجب أن يكون خيط رد متاحًا حتى يظهر البث النصي الأصلي. ويظل اختيار الخيط يتبع `replyToMode`. وبدون ذلك، تُستخدم معاينة المسودة العادية.
- تعود الوسائط والحمولات غير النصية إلى التسليم العادي.
- إذا فشل البث أثناء الرد، يعود OpenClaw إلى التسليم العادي للحمولات المتبقية.

استخدم معاينة المسودة بدلًا من البث النصي الأصلي لـ Slack:

```json5
{
  channels: {
    slack: {
      streaming: "partial",
      nativeStreaming: false,
    },
  },
}
```

المفاتيح القديمة:

- تتم الترحيل التلقائي لـ `channels.slack.streamMode` (`replace | status_final | append`) إلى `channels.slack.streaming`.
- تتم الترحيل التلقائي للقيمة المنطقية `channels.slack.streaming` إلى `channels.slack.nativeStreaming`.

## بديل تفاعل الكتابة

يضيف `typingReaction` تفاعلًا مؤقتًا إلى رسالة Slack الواردة بينما يعالج OpenClaw ردًا، ثم يزيله عند انتهاء التشغيل. وهذا مفيد بشكل خاص خارج ردود الخيوط، التي تستخدم مؤشر حالة افتراضي "is typing...".

ترتيب الحل:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

ملاحظات:

- يتوقع Slack رموزًا قصيرة (مثل `"hourglass_flowing_sand"`).
- يكون التفاعل على أساس أفضل جهد، وتتم محاولة التنظيف تلقائيًا بعد اكتمال الرد أو مسار الفشل.

## الوسائط والتجزئة والتسليم

<AccordionGroup>
  <Accordion title="المرفقات الواردة">
    يتم تنزيل مرفقات ملفات Slack من عناوين URL خاصة مستضافة على Slack (تدفق طلبات موثقة بالرمز المميز) وكتابتها إلى مخزن الوسائط عند نجاح الجلب والسماح بحدود الحجم.

    يكون الحد الأقصى الافتراضي لحجم الرسائل الواردة في وقت التشغيل `20MB` ما لم يتم تجاوزه بواسطة `channels.slack.mediaMaxMb`.

  </Accordion>

  <Accordion title="النصوص والملفات الصادرة">
    - تستخدم مقاطع النص `channels.slack.textChunkLimit` (الافتراضي 4000)
    - يفعّل `channels.slack.chunkMode="newline"` التقسيم مع إعطاء الأولوية للفقرات
    - تستخدم عمليات إرسال الملفات واجهات رفع Slack ويمكن أن تتضمن ردود الخيوط (`thread_ts`)
    - يتبع الحد الأقصى للوسائط الصادرة `channels.slack.mediaMaxMb` عند إعداده؛ وإلا تستخدم عمليات الإرسال عبر القناة الحدود الافتراضية حسب نوع MIME من مسار الوسائط
  </Accordion>

  <Accordion title="أهداف التسليم">
    الأهداف الصريحة المفضلة:

    - `user:<id>` للرسائل الخاصة
    - `channel:<id>` للقنوات

    يتم فتح الرسائل الخاصة في Slack عبر واجهات Slack conversation APIs عند الإرسال إلى أهداف المستخدمين.

  </Accordion>
</AccordionGroup>

## الأوامر وسلوك الشرطة المائلة

- الوضع التلقائي للأوامر الأصلية **معطّل** في Slack (`commands.native: "auto"` لا يفعّل أوامر Slack الأصلية).
- فعّل معالجات أوامر Slack الأصلية باستخدام `channels.slack.commands.native: true` (أو `commands.native: true` على المستوى العام).
- عند تفعيل الأوامر الأصلية، سجّل أوامر الشرطة المائلة المطابقة في Slack (`/<command>`)، مع استثناء واحد:
  - سجّل `/agentstatus` لأمر الحالة (يحجز Slack الأمر `/status`)
- إذا لم تكن الأوامر الأصلية مفعلة، يمكنك تشغيل أمر شرطة مائلة واحد مُعد عبر `channels.slack.slashCommand`.
- أصبحت قوائم الوسائط الأصلية للوسائط تتكيف الآن مع استراتيجية العرض:
  - حتى 5 خيارات: كتل أزرار
  - من 6 إلى 100 خيار: قائمة تحديد ثابتة
  - أكثر من 100 خيار: تحديد خارجي مع تصفية خيارات غير متزامنة عندما تكون معالجات خيارات interactivity متاحة
  - إذا تجاوزت قيم الخيارات المرمزة حدود Slack، يعود التدفق إلى الأزرار
- بالنسبة لحمولات الخيارات الطويلة، تستخدم قوائم وسائط وسائط أوامر الشرطة المائلة مربع تأكيد قبل إرسال القيمة المحددة.

إعدادات أمر الشرطة المائلة الافتراضية:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

تستخدم جلسات الشرطة المائلة مفاتيح معزولة:

- `agent:<agentId>:slack:slash:<userId>`

ومع ذلك تظل توجه تنفيذ الأمر إلى جلسة المحادثة الهدف (`CommandTargetSessionKey`).

## الردود التفاعلية

يمكن لـ Slack عرض عناصر تحكم الردود التفاعلية التي ينشئها الوكيل، لكن هذه الميزة معطلة افتراضيًا.

فعّلها عالميًا:

```json5
{
  channels: {
    slack: {
      capabilities: {
        interactiveReplies: true,
      },
    },
  },
}
```

أو فعّلها لحساب Slack واحد فقط:

```json5
{
  channels: {
    slack: {
      accounts: {
        ops: {
          capabilities: {
            interactiveReplies: true,
          },
        },
      },
    },
  },
}
```

عند التفعيل، يمكن للوكلاء إصدار توجيهات رد خاصة بـ Slack:

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

تُحوَّل هذه التوجيهات إلى Slack Block Kit وتُعيد توجيه النقرات أو التحديدات عبر مسار حدث التفاعل الحالي في Slack.

ملاحظات:

- هذه واجهة مستخدم خاصة بـ Slack. لا تقوم القنوات الأخرى بترجمة توجيهات Slack Block Kit إلى أنظمة الأزرار الخاصة بها.
- قيم رد النداء التفاعلي هي رموز معتمة يُنشئها OpenClaw، وليست قيمًا أولية يكتبها الوكيل.
- إذا كانت الكتل التفاعلية المولدة ستتجاوز حدود Slack Block Kit، يعود OpenClaw إلى الرد النصي الأصلي بدلًا من إرسال حمولة blocks غير صالحة.

## موافقات exec في Slack

يمكن أن يعمل Slack كعميل موافقة أصلي مع أزرار وتفاعلات تفاعلية، بدلًا من الرجوع إلى واجهة الويب أو الطرفية.

- تستخدم موافقات exec الإعداد `channels.slack.execApprovals.*` للتوجيه الأصلي في الرسائل الخاصة/القنوات.
- لا تزال موافقات plugin تُحل عبر نفس سطح أزرار Slack الأصلي عندما يصل الطلب بالفعل إلى Slack ويكون نوع معرّف الموافقة هو `plugin:`.
- لا يزال تفويض الموافقين مطبقًا: لا يمكن إلا للمستخدمين المحددين كموافقين الموافقة على الطلبات أو رفضها عبر Slack.

يستخدم هذا نفس سطح أزرار الموافقة المشترك مع القنوات الأخرى. عندما تكون `interactivity` مفعلة في إعدادات تطبيق Slack لديك، تُعرض مطالبات الموافقة كأزرار Block Kit مباشرة داخل المحادثة.
وعندما تكون هذه الأزرار موجودة، فإنها تكون تجربة الاستخدام الأساسية للموافقة؛ ويجب على OpenClaw
أن يتضمن أمر `/approve` يدويًا فقط عندما تشير نتيجة الأداة إلى أن
موافقات الدردشة غير متاحة أو أن الموافقة اليدوية هي المسار الوحيد.

مسار الإعداد:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers` (اختياري؛ يعود إلى `commands.ownerAllowFrom` عندما يكون ذلك ممكنًا)
- `channels.slack.execApprovals.target` (`dm` | `channel` | `both`، الافتراضي: `dm`)
- `agentFilter`, `sessionFilter`

يفعّل Slack موافقات exec الأصلية تلقائيًا عندما تكون `enabled` غير مضبوطة أو مساوية لـ `"auto"` ويتم حل موافق واحد على الأقل. اضبط `enabled: false` لتعطيل Slack كعميل موافقة أصلي بشكل صريح.
واضبط `enabled: true` لفرض تفعيل الموافقات الأصلية عند حل الموافقين.

السلوك الافتراضي بدون إعداد صريح لموافقات exec في Slack:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

لا يلزم إعداد Slack الأصلي الصريح إلا عندما تريد تجاوز الموافقين أو إضافة عوامل تصفية أو
اختيار التسليم إلى دردشة المصدر:

```json5
{
  channels: {
    slack: {
      execApprovals: {
        enabled: true,
        approvers: ["U12345678"],
        target: "both",
      },
    },
  },
}
```

يكون توجيه `approvals.exec` المشترك منفصلًا. استخدمه فقط عندما يجب أيضًا
توجيه مطالبات موافقة exec إلى دردشات أخرى أو أهداف صريحة خارج النطاق. كما أن توجيه `approvals.plugin` المشترك
منفصل أيضًا؛ ولا تزال أزرار Slack الأصلية قادرة على حل موافقات plugin عندما تصل هذه الطلبات بالفعل
إلى Slack.

يعمل `/approve` في نفس الدردشة أيضًا في قنوات Slack والرسائل الخاصة التي تدعم الأوامر بالفعل. راجع [Exec approvals](/ar/tools/exec-approvals) للاطلاع على نموذج توجيه الموافقات الكامل.

## الأحداث والسلوك التشغيلي

- يتم ربط تعديلات الرسائل/حذفها/بث الخيوط بأحداث نظام.
- يتم ربط أحداث إضافة/إزالة التفاعلات بأحداث نظام.
- يتم ربط أحداث انضمام/مغادرة الأعضاء، وإنشاء/إعادة تسمية القنوات، وإضافة/إزالة التثبيتات بأحداث نظام.
- يمكن لـ `channel_id_changed` ترحيل مفاتيح إعداد القناة عندما تكون `configWrites` مفعلة.
- تُعامل بيانات topic/purpose الوصفية للقناة على أنها سياق غير موثوق ويمكن حقنها في سياق التوجيه.
- تتم تصفية بادئ الخيط وسياق تعبئة محفوظات الخيط الأولية بواسطة قوائم سماح المرسلين المهيأة عند الاقتضاء.
- تصدر إجراءات الكتل وتفاعلات النوافذ المنبثقة أحداث نظام منظّمة بصيغة `Slack interaction: ...` مع حقول حمولة غنية:
  - إجراءات الكتل: القيم المحددة، والتسميات، وقيم أداة الاختيار، وبيانات `workflow_*` الوصفية
  - أحداث النوافذ المنبثقة `view_submission` و`view_closed` مع بيانات القناة الموجهة ومدخلات النماذج

## مؤشرات مرجعية للإعداد

المرجع الأساسي:

- [مرجع الإعداد - Slack](/ar/gateway/configuration-reference#slack)

  حقول Slack عالية الإشارة:
  - الوضع/المصادقة: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - الوصول إلى الرسائل الخاصة: `dm.enabled`, `dmPolicy`, `allowFrom` (قديمًا: `dm.policy`, `dm.allowFrom`), `dm.groupEnabled`, `dm.groupChannels`
  - مفتاح التوافق: `dangerouslyAllowNameMatching` (للاستخدام الطارئ؛ اتركه معطّلًا ما لم تكن بحاجة إليه)
  - الوصول إلى القنوات: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - الخيوط/السجل: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - التسليم: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - العمليات/الميزات: `configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## استكشاف الأخطاء وإصلاحها

<AccordionGroup>
  <Accordion title="لا توجد ردود في القنوات">
    تحقق، بالترتيب، من:

    - `groupPolicy`
    - قائمة سماح القنوات (`channels.slack.channels`)
    - `requireMention`
    - قائمة سماح `users` لكل قناة

    أوامر مفيدة:

```bash
openclaw channels status --probe
openclaw logs --follow
openclaw doctor
```

  </Accordion>

  <Accordion title="يتم تجاهل رسائل الرسائل الخاصة">
    تحقق من:

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy` (أو المفتاح القديم `channels.slack.dm.policy`)
    - موافقات الاقتران / إدخالات قائمة السماح

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Socket mode لا يتصل">
    تحقّق من صحة bot token وapp token ومن تمكين Socket Mode في إعدادات تطبيق Slack.

    إذا أظهر `openclaw channels status --probe --json` قيمة `botTokenStatus` أو
    `appTokenStatus: "configured_unavailable"`، فهذا يعني أن حساب Slack
    مُعد، لكن وقت التشغيل الحالي لم يتمكن من حل
    القيمة المدعومة بـ SecretRef.

  </Accordion>

  <Accordion title="وضع HTTP لا يستقبل الأحداث">
    تحقّق من:

    - signing secret
    - مسار webhook
    - عناوين URL لطلبات Slack (الأحداث + Interactivity + أوامر الشرطة المائلة)
    - `webhookPath` فريد لكل حساب HTTP

    إذا ظهر `signingSecretStatus: "configured_unavailable"` في لقطات
    الحساب، فهذا يعني أن حساب HTTP مُعد لكن وقت التشغيل الحالي لم يتمكن من
    حل signing secret المدعوم بـ SecretRef.

  </Accordion>

  <Accordion title="الأوامر الأصلية/أوامر الشرطة المائلة لا تعمل">
    تحقّق مما إذا كنت تقصد:

    - وضع الأوامر الأصلية (`channels.slack.commands.native: true`) مع تسجيل أوامر الشرطة المائلة المطابقة في Slack
    - أو وضع أمر الشرطة المائلة الفردي (`channels.slack.slashCommand.enabled: true`)

    تحقّق أيضًا من `commands.useAccessGroups` وقوائم سماح القنوات/المستخدمين.

  </Accordion>
</AccordionGroup>

## ذو صلة

- [الاقتران](/ar/channels/pairing)
- [المجموعات](/ar/channels/groups)
- [الأمان](/ar/gateway/security)
- [توجيه القنوات](/ar/channels/channel-routing)
- [استكشاف الأخطاء وإصلاحها](/ar/channels/troubleshooting)
- [الإعداد](/ar/gateway/configuration)
- [أوامر الشرطة المائلة](/ar/tools/slash-commands)
