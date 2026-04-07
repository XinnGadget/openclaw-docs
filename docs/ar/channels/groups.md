---
read_when:
    - عند تغيير سلوك الدردشة الجماعية أو تقييد الإشارات
summary: سلوك الدردشة الجماعية عبر الأسطح المختلفة (Discord/iMessage/Matrix/Microsoft Teams/Signal/Slack/Telegram/WhatsApp/Zalo)
title: المجموعات
x-i18n:
    generated_at: "2026-04-07T07:16:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: f5045badbba30587c8f1bf27f6b940c7c471a95c57093c9adb142374413ac81e
    source_path: channels/groups.md
    workflow: 15
---

# المجموعات

يتعامل OpenClaw مع الدردشات الجماعية بشكل متسق عبر الأسطح المختلفة: Discord وiMessage وMatrix وMicrosoft Teams وSignal وSlack وTelegram وWhatsApp وZalo.

## مقدمة للمبتدئين (دقيقتان)

يعيش OpenClaw على حسابات المراسلة الخاصة بك. لا يوجد مستخدم بوت منفصل لـ WhatsApp.
إذا كنت **أنت** ضمن مجموعة، يمكن لـ OpenClaw رؤية تلك المجموعة والرد فيها.

السلوك الافتراضي:

- المجموعات مقيّدة (`groupPolicy: "allowlist"`).
- تتطلب الردود إشارة ما لم تقم بتعطيل تقييد الإشارات صراحةً.

بعبارة أخرى: يمكن للمرسلين المدرجين في قائمة السماح تشغيل OpenClaw من خلال الإشارة إليه.

> باختصار
>
> - يتم التحكم في **الوصول إلى الرسائل الخاصة** بواسطة `*.allowFrom`.
> - يتم التحكم في **الوصول إلى المجموعات** بواسطة `*.groupPolicy` + قوائم السماح (`*.groups`, `*.groupAllowFrom`).
> - يتم التحكم في **تشغيل الردود** بواسطة تقييد الإشارات (`requireMention`, `/activation`).

تدفق سريع (ما الذي يحدث لرسالة المجموعة):

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

## رؤية السياق وقوائم السماح

يتضمن الأمان في المجموعات عنصرَي تحكم مختلفين:

- **تفويض التشغيل**: من يمكنه تشغيل الوكيل (`groupPolicy`, `groups`, `groupAllowFrom`, قوائم السماح الخاصة بالقناة).
- **رؤية السياق**: ما السياق التكميلي الذي يتم حقنه في النموذج (نص الرد، الاقتباسات، سجل السلسلة، بيانات إعادة التوجيه الوصفية).

بشكل افتراضي، يعطي OpenClaw الأولوية لسلوك الدردشة الطبيعي ويُبقي السياق في الغالب كما تم استلامه. وهذا يعني أن قوائم السماح تحدد أساسًا من يمكنه تشغيل الإجراءات، وليست حدًا عامًا لإخفاء كل مقتطف مقتبس أو تاريخي.

السلوك الحالي خاص بكل قناة:

- بعض القنوات تطبق بالفعل تصفية تستند إلى المرسل للسياق التكميلي في مسارات محددة (مثل تهيئة سلاسل Slack، وعمليات بحث الرد/السلسلة في Matrix).
- قنوات أخرى ما تزال تمرر سياق الاقتباس/الرد/إعادة التوجيه كما تم استلامه.

اتجاه التحصين (مخطط له):

- `contextVisibility: "all"` (الافتراضي) يُبقي السلوك الحالي كما تم استلامه.
- `contextVisibility: "allowlist"` يرشح السياق التكميلي إلى المرسلين الموجودين في قائمة السماح.
- `contextVisibility: "allowlist_quote"` هو `allowlist` مع استثناء صريح واحد للاقتباس/الرد.

إلى أن يتم تنفيذ نموذج التحصين هذا بشكل متسق عبر القنوات، توقّع وجود اختلافات حسب السطح.

![تدفق رسائل المجموعات](/images/groups-flow.svg)

إذا كنت تريد...

| الهدف | ما الذي يجب ضبطه |
| -------------------------------------------- | ---------------------------------------------------------- |
| السماح بكل المجموعات لكن الرد فقط عند @mentions | `groups: { "*": { requireMention: true } }`                |
| تعطيل كل الردود في المجموعات | `groupPolicy: "disabled"`                                  |
| مجموعات محددة فقط | `groups: { "<group-id>": { ... } }` (بدون المفتاح `"*"`)         |
| أنت فقط من يمكنه التشغيل داخل المجموعات | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## مفاتيح الجلسات

- تستخدم جلسات المجموعات مفاتيح جلسات بصيغة `agent:<agentId>:<channel>:group:<id>` (وتستخدم الغرف/القنوات `agent:<agentId>:<channel>:channel:<id>`).
- تضيف موضوعات منتدى Telegram ‎`:topic:<threadId>` إلى معرّف المجموعة بحيث يكون لكل موضوع جلسته الخاصة.
- تستخدم الدردشات المباشرة الجلسة الرئيسية (أو جلسة لكل مرسل إذا كان ذلك مضبوطًا).
- يتم تخطي heartbeat لجلسات المجموعات.

<a id="pattern-personal-dms-public-groups-single-agent"></a>

## النمط: الرسائل الخاصة الشخصية + المجموعات العامة (وكيل واحد)

نعم — يعمل هذا جيدًا إذا كانت حركة المرور “الشخصية” لديك هي **الرسائل الخاصة** وكانت حركة المرور “العامة” لديك هي **المجموعات**.

السبب: في وضع الوكيل الواحد، تصل الرسائل الخاصة عادةً إلى مفتاح الجلسة **الرئيسي** (`agent:main:main`)، بينما تستخدم المجموعات دائمًا مفاتيح جلسات **غير رئيسية** (`agent:main:<channel>:group:<id>`). إذا فعّلت العزل باستخدام `mode: "non-main"`، فستعمل جلسات المجموعات تلك داخل Docker بينما تبقى جلسة الرسائل الخاصة الرئيسية على المضيف.

ويمنحك هذا “عقل” وكيل واحد (مساحة عمل + ذاكرة مشتركتان)، ولكن مع وضعي تنفيذ:

- **الرسائل الخاصة**: أدوات كاملة (المضيف)
- **المجموعات**: عزل + أدوات مقيّدة (Docker)

> إذا كنت تحتاج إلى مساحات عمل/شخصيات منفصلة تمامًا (يجب ألا يختلط “الشخصي” و”العام” أبدًا)، فاستخدم وكيلاً ثانيًا + bindings. راجع [التوجيه متعدد الوكلاء](/ar/concepts/multi-agent).

مثال (الرسائل الخاصة على المضيف، والمجموعات داخل العزل + أدوات مراسلة فقط):

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // groups/channels are non-main -> sandboxed
        scope: "session", // strongest isolation (one container per group/channel)
        workspaceAccess: "none",
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        // If allow is non-empty, everything else is blocked (deny still wins).
        allow: ["group:messaging", "group:sessions"],
        deny: ["group:runtime", "group:fs", "group:ui", "nodes", "cron", "gateway"],
      },
    },
  },
}
```

هل تريد أن “تتمكن المجموعات من رؤية المجلد X فقط” بدلًا من “عدم وجود وصول إلى المضيف”؟ أبقِ `workspaceAccess: "none"` وقم بتحميل المسارات الموجودة في قائمة السماح فقط داخل sandbox:

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
        docker: {
          binds: [
            // hostPath:containerPath:mode
            "/home/user/FriendsShared:/data:ro",
          ],
        },
      },
    },
  },
}
```

ذو صلة:

- مفاتيح الإعدادات والقيم الافتراضية: [إعدادات Gateway](/ar/gateway/configuration-reference#agentsdefaultssandbox)
- تصحيح سبب حظر أداة: [Sandbox مقابل Tool Policy مقابل Elevated](/ar/gateway/sandbox-vs-tool-policy-vs-elevated)
- تفاصيل bind mounts: [العزل](/ar/gateway/sandboxing#custom-bind-mounts)

## تسميات العرض

- تستخدم تسميات واجهة المستخدم `displayName` عندما تكون متاحة، وتُنسَّق بالشكل `<channel>:<token>`.
- الرمز `#room` مخصص للغرف/القنوات؛ تستخدم الدردشات الجماعية `g-<slug>` (أحرف صغيرة، المسافات -> `-`، مع الإبقاء على `#@+._-`).

## سياسة المجموعات

تحكم في كيفية التعامل مع رسائل المجموعات/الغرف لكل قناة:

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "disabled", // "open" | "disabled" | "allowlist"
      groupAllowFrom: ["+15551234567"],
    },
    telegram: {
      groupPolicy: "disabled",
      groupAllowFrom: ["123456789"], // numeric Telegram user id (wizard can resolve @username)
    },
    signal: {
      groupPolicy: "disabled",
      groupAllowFrom: ["+15551234567"],
    },
    imessage: {
      groupPolicy: "disabled",
      groupAllowFrom: ["chat_id:123"],
    },
    msteams: {
      groupPolicy: "disabled",
      groupAllowFrom: ["user@org.com"],
    },
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        GUILD_ID: { channels: { help: { allow: true } } },
      },
    },
    slack: {
      groupPolicy: "allowlist",
      channels: { "#general": { allow: true } },
    },
    matrix: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["@owner:example.org"],
      groups: {
        "!roomId:example.org": { enabled: true },
        "#alias:example.org": { enabled: true },
      },
    },
  },
}
```

| السياسة | السلوك |
| ------------- | ------------------------------------------------------------ |
| `"open"`      | تتجاوز المجموعات قوائم السماح؛ ولا يزال تقييد الإشارات مطبقًا.      |
| `"disabled"`  | حظر جميع رسائل المجموعات بالكامل.                           |
| `"allowlist"` | السماح فقط بالمجموعات/الغرف المطابقة لقائمة السماح المضبوطة. |

ملاحظات:

- `groupPolicy` منفصلة عن تقييد الإشارات (الذي يتطلب @mentions).
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams/Zalo: استخدم `groupAllowFrom` (والبديل الاحتياطي: `allowFrom` الصريح).
- تنطبق موافقات الاقتران للرسائل الخاصة (إدخالات التخزين `*-allowFrom`) على الوصول إلى الرسائل الخاصة فقط؛ أما تفويض مرسل المجموعة فيظل صريحًا عبر قوائم السماح الخاصة بالمجموعات.
- Discord: تستخدم قائمة السماح `channels.discord.guilds.<id>.channels`.
- Slack: تستخدم قائمة السماح `channels.slack.channels`.
- Matrix: تستخدم قائمة السماح `channels.matrix.groups`. فَضِّل معرّفات الغرف أو الأسماء المستعارة؛ ويكون البحث باسم الغرفة المنضم إليها بأفضل جهد، ويتم تجاهل الأسماء غير المحلولة وقت التشغيل. استخدم `channels.matrix.groupAllowFrom` لتقييد المرسلين؛ كما أن قوائم السماح `users` لكل غرفة مدعومة أيضًا.
- يتم التحكم في الرسائل الخاصة الجماعية بشكل منفصل (`channels.discord.dm.*`, `channels.slack.dm.*`).
- يمكن أن تطابق قائمة السماح في Telegram معرّفات المستخدمين (`"123456789"`, `"telegram:123456789"`, `"tg:123456789"`) أو أسماء المستخدمين (`"@alice"` أو `"alice"`); والبادئات غير حساسة لحالة الأحرف.
- القيمة الافتراضية هي `groupPolicy: "allowlist"`؛ وإذا كانت قائمة السماح الخاصة بالمجموعات فارغة، فسيتم حظر رسائل المجموعات.
- أمان وقت التشغيل: عندما تكون كتلة الموفر مفقودة بالكامل (`channels.<provider>` غير موجودة)، تعود سياسة المجموعات إلى وضع مغلق افتراضيًا وآمنًا (عادةً `allowlist`) بدلًا من وراثة `channels.defaults.groupPolicy`.

نموذج ذهني سريع (ترتيب التقييم لرسائل المجموعات):

1. `groupPolicy` ‏(open/disabled/allowlist)
2. قوائم السماح الخاصة بالمجموعات (`*.groups`, `*.groupAllowFrom`, قائمة السماح الخاصة بالقناة)
3. تقييد الإشارات (`requireMention`, `/activation`)

## تقييد الإشارات (الافتراضي)

تتطلب رسائل المجموعات إشارة ما لم يتم تجاوز ذلك لكل مجموعة. توجد القيم الافتراضية لكل نظام فرعي ضمن `*.groups."*"`.

يُحسب الرد على رسالة من البوت كإشارة ضمنية عندما تدعم القناة
بيانات وصفية للرد. ويمكن أيضًا أن يُحسب اقتباس رسالة من البوت كإشارة ضمنية
على القنوات التي تعرض بيانات وصفية للاقتباس. تشمل الحالات المضمنة الحالية
Telegram وWhatsApp وSlack وDiscord وMicrosoft Teams وZaloUser.

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
        "123@g.us": { requireMention: false },
      },
    },
    telegram: {
      groups: {
        "*": { requireMention: true },
        "123456789": { requireMention: false },
      },
    },
    imessage: {
      groups: {
        "*": { requireMention: true },
        "123": { requireMention: false },
      },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          mentionPatterns: ["@openclaw", "openclaw", "\\+15555550123"],
          historyLimit: 50,
        },
      },
    ],
  },
}
```

ملاحظات:

- `mentionPatterns` هي أنماط regex آمنة وغير حساسة لحالة الأحرف؛ ويتم تجاهل الأنماط غير الصالحة وأشكال التكرار المتداخل غير الآمنة.
- الأسطح التي توفر إشارات صريحة تظل تمر؛ والأنماط هي بديل احتياطي.
- تجاوز لكل وكيل: `agents.list[].groupChat.mentionPatterns` (مفيد عندما تشترك عدة وكلاء في مجموعة).
- لا يتم فرض تقييد الإشارات إلا عندما يكون اكتشاف الإشارات ممكنًا (إشارات أصلية أو تم ضبط `mentionPatterns`).
- توجد القيم الافتراضية لـ Discord ضمن `channels.discord.guilds."*"` (وقابلة للتجاوز لكل guild/channel).
- يتم تغليف سياق سجل المجموعات بشكل موحد عبر القنوات وهو **معلّق فقط** (الرسائل التي تم تخطيها بسبب تقييد الإشارات)؛ استخدم `messages.groupChat.historyLimit` كقيمة افتراضية عامة و`channels.<channel>.historyLimit` (أو `channels.<channel>.accounts.*.historyLimit`) للتجاوزات. عيّن القيمة `0` للتعطيل.

## قيود أدوات المجموعة/القناة (اختياري)

تدعم بعض إعدادات القنوات تقييد الأدوات المتاحة **داخل مجموعة/غرفة/قناة محددة**.

- `tools`: السماح/المنع للأدوات على مستوى المجموعة بالكامل.
- `toolsBySender`: تجاوزات لكل مرسل داخل المجموعة.
  استخدم بادئات مفاتيح صريحة:
  `id:<senderId>`, `e164:<phone>`, `username:<handle>`, `name:<displayName>`، وبديل `"*"` العام.
  ما تزال المفاتيح القديمة غير المسبوقة ببادئة مقبولة وتُطابق على أنها `id:` فقط.

ترتيب الحل (الأكثر تحديدًا يفوز):

1. تطابق `toolsBySender` للمجموعة/القناة
2. `tools` للمجموعة/القناة
3. تطابق `toolsBySender` الافتراضي (`"*"` )
4. `tools` الافتراضي (`"*"`)

مثال (Telegram):

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { tools: { deny: ["exec"] } },
        "-1001234567890": {
          tools: { deny: ["exec", "read", "write"] },
          toolsBySender: {
            "id:123456789": { alsoAllow: ["exec"] },
          },
        },
      },
    },
  },
}
```

ملاحظات:

- تُطبّق قيود أدوات المجموعة/القناة بالإضافة إلى سياسة الأدوات العامة/الخاصة بالوكيل (ويظل المنع هو الغالب).
- تستخدم بعض القنوات تداخلًا مختلفًا للغرف/القنوات (مثل Discord `guilds.*.channels.*`، وSlack `channels.*`، وMicrosoft Teams `teams.*.channels.*`).

## قوائم السماح الخاصة بالمجموعات

عند ضبط `channels.whatsapp.groups` أو `channels.telegram.groups` أو `channels.imessage.groups`، تعمل المفاتيح كقائمة سماح للمجموعات. استخدم `"*"` للسماح بكل المجموعات مع الاستمرار في ضبط سلوك الإشارات الافتراضي.

التباس شائع: موافقة اقتران الرسائل الخاصة ليست نفسها تفويض المجموعة.
بالنسبة إلى القنوات التي تدعم اقتران الرسائل الخاصة، يفتح مخزن الاقتران الرسائل الخاصة فقط. أما أوامر المجموعات فلا تزال تتطلب تفويضًا صريحًا لمرسل المجموعة من قوائم السماح في الإعدادات مثل `groupAllowFrom` أو البديل الاحتياطي الموثق للإعدادات في تلك القناة.

نوايا شائعة (نسخ/لصق):

1. تعطيل كل الردود في المجموعات

```json5
{
  channels: { whatsapp: { groupPolicy: "disabled" } },
}
```

2. السماح فقط بمجموعات محددة (WhatsApp)

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "123@g.us": { requireMention: true },
        "456@g.us": { requireMention: false },
      },
    },
  },
}
```

3. السماح بكل المجموعات لكن طلب الإشارة (صراحةً)

```json5
{
  channels: {
    whatsapp: {
      groups: { "*": { requireMention: true } },
    },
  },
}
```

4. المالك فقط يمكنه التشغيل داخل المجموعات (WhatsApp)

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
      groups: { "*": { requireMention: true } },
    },
  },
}
```

## التفعيل (للمالك فقط)

يمكن لمالكي المجموعات تبديل التفعيل لكل مجموعة:

- `/activation mention`
- `/activation always`

يتم تحديد المالك بواسطة `channels.whatsapp.allowFrom` (أو E.164 الخاص بالبوت نفسه إذا لم يتم تعيينه). أرسل الأمر كرسالة مستقلة. وتتجاهل الأسطح الأخرى حاليًا `/activation`.

## حقول السياق

تقوم الحمولات الواردة للمجموعات بضبط ما يلي:

- `ChatType=group`
- `GroupSubject` (إذا كان معروفًا)
- `GroupMembers` (إذا كان معروفًا)
- `WasMentioned` (نتيجة تقييد الإشارات)
- تتضمن موضوعات منتدى Telegram أيضًا `MessageThreadId` و`IsForum`.

ملاحظات خاصة بالقنوات:

- يمكن لـ BlueBubbles اختياريًا إثراء المشاركين غير المُسمّين في مجموعات macOS من قاعدة بيانات Contacts المحلية قبل تعبئة `GroupMembers`. يكون هذا معطلًا افتراضيًا ولا يعمل إلا بعد تجاوز التقييد العادي للمجموعات.

يتضمن system prompt الخاص بالوكيل مقدمة عن المجموعات في أول دورة من جلسة مجموعة جديدة. وهو يذكّر النموذج بالرد مثل الإنسان، وتجنب جداول Markdown، وتقليل الأسطر الفارغة واتباع تباعد الدردشة العادي، وتجنب كتابة تسلسلات `\n` الحرفية.

## تفاصيل iMessage

- فضّل `chat_id:<id>` عند التوجيه أو إضافة العناصر إلى قائمة السماح.
- عرض الدردشات: `imsg chats --limit 20`.
- تعود الردود في المجموعات دائمًا إلى نفس `chat_id`.

## تفاصيل WhatsApp

راجع [رسائل المجموعات](/ar/channels/group-messages) للاطلاع على السلوك الخاص بـ WhatsApp فقط (حقن السجل، وتفاصيل التعامل مع الإشارات).
