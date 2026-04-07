---
read_when:
    - تحتاج إلى دلالات إعداد دقيقة على مستوى الحقل أو إلى القيم الافتراضية
    - أنت تتحقق من كتل إعدادات القناة أو النموذج أو البوابة أو الأدوات
summary: المرجع الكامل لكل مفتاح إعداد في OpenClaw، والقيم الافتراضية، وإعدادات القنوات
title: مرجع الإعدادات
x-i18n:
    generated_at: "2026-04-07T07:23:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7768cb77e1d3fc483c66f655ea891d2c32f21b247e3c1a56a919b28a37f9b128
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# مرجع الإعدادات

كل حقل متاح في `~/.openclaw/openclaw.json`. للاطلاع على نظرة عامة موجّهة بالمهام، انظر [الإعدادات](/ar/gateway/configuration).

تنسيق الإعداد هو **JSON5** (يُسمح بالتعليقات والفواصل اللاحقة). جميع الحقول اختيارية — يستخدم OpenClaw قيمًا افتراضية آمنة عند حذفها.

---

## القنوات

تبدأ كل قناة تلقائيًا عند وجود قسم إعدادها (ما لم يكن `enabled: false`).

### الوصول إلى الرسائل الخاصة والمجموعات

تدعم جميع القنوات سياسات الرسائل الخاصة وسياسات المجموعات:

| سياسة الرسائل الخاصة | السلوك                                                        |
| -------------------- | ------------------------------------------------------------- |
| `pairing` (الافتراضي) | يحصل المرسلون غير المعروفين على رمز اقتران لمرة واحدة؛ ويجب أن يوافق المالك |
| `allowlist`          | فقط المرسلون الموجودون في `allowFrom` (أو مخزن السماح المقترن) |
| `open`               | السماح بجميع الرسائل الخاصة الواردة (يتطلب `allowFrom: ["*"]`) |
| `disabled`           | تجاهل جميع الرسائل الخاصة الواردة                             |

| سياسة المجموعة        | السلوك                                               |
| --------------------- | ---------------------------------------------------- |
| `allowlist` (الافتراضي) | فقط المجموعات المطابقة لقائمة السماح المكوّنة         |
| `open`                | تجاوز قوائم السماح الخاصة بالمجموعات (مع استمرار تطبيق بوابة الإشارة) |
| `disabled`            | حظر جميع رسائل المجموعات/الغرف                       |

<Note>
يضبط `channels.defaults.groupPolicy` السياسة الافتراضية عندما لا يكون `groupPolicy` الخاص بالمزوّد معيّنًا.
تنتهي صلاحية رموز الاقتران بعد ساعة واحدة. ويكون الحد الأقصى لطلبات اقتران الرسائل الخاصة المعلّقة **3 لكل قناة**.
إذا كانت كتلة المزوّد مفقودة بالكامل (`channels.<provider>` غير موجودة)، فإن سياسة المجموعات أثناء التشغيل تعود إلى `allowlist` (إغلاق آمن عند الفشل) مع تحذير عند بدء التشغيل.
</Note>

### تجاوزات نموذج القناة

استخدم `channels.modelByChannel` لتثبيت معرّفات قنوات محددة على نموذج بعينه. تقبل القيم `provider/model` أو الأسماء المستعارة للنماذج المكوّنة. ويُطبّق تعيين القناة عندما لا تكون الجلسة تمتلك بالفعل تجاوزًا للنموذج (على سبيل المثال، تم تعيينه عبر `/model`).

```json5
{
  channels: {
    modelByChannel: {
      discord: {
        "123456789012345678": "anthropic/claude-opus-4-6",
      },
      slack: {
        C1234567890: "openai/gpt-4.1",
      },
      telegram: {
        "-1001234567890": "openai/gpt-4.1-mini",
        "-1001234567890:topic:99": "anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

### الإعدادات الافتراضية للقنوات ونبض الحياة

استخدم `channels.defaults` للسلوك المشترك الخاص بسياسة المجموعات ونبض الحياة عبر المزوّدين:

```json5
{
  channels: {
    defaults: {
      groupPolicy: "allowlist", // open | allowlist | disabled
      contextVisibility: "all", // all | allowlist | allowlist_quote
      heartbeat: {
        showOk: false,
        showAlerts: true,
        useIndicator: true,
      },
    },
  },
}
```

- `channels.defaults.groupPolicy`: سياسة المجموعات الاحتياطية عندما لا يكون `groupPolicy` على مستوى المزوّد معيّنًا.
- `channels.defaults.contextVisibility`: وضع الرؤية الافتراضي للسياق التكميلي لجميع القنوات. القيم: `all` (الافتراضي، تضمين كل سياق الاقتباس/الخيط/السجل)، و`allowlist` (تضمين السياق من المرسلين الموجودين في قائمة السماح فقط)، و`allowlist_quote` (مثل allowlist ولكن مع الاحتفاظ بسياق الاقتباس/الرد الصريح). تجاوز لكل قناة: `channels.<channel>.contextVisibility`.
- `channels.defaults.heartbeat.showOk`: تضمين حالات القنوات السليمة في مخرجات نبض الحياة.
- `channels.defaults.heartbeat.showAlerts`: تضمين حالات التدهور/الخطأ في مخرجات نبض الحياة.
- `channels.defaults.heartbeat.useIndicator`: عرض مخرجات نبض الحياة بنمط مؤشرات مدمج.

### WhatsApp

يعمل WhatsApp من خلال قناة الويب الخاصة بالبوابة (Baileys Web). ويبدأ تلقائيًا عند وجود جلسة مرتبطة.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // علامات القراءة الزرقاء (false في وضع الدردشة الذاتية)
      groups: {
        "*": { requireMention: true },
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
  web: {
    enabled: true,
    heartbeatSeconds: 60,
    reconnect: {
      initialMs: 2000,
      maxMs: 120000,
      factor: 1.4,
      jitter: 0.2,
      maxAttempts: 0,
    },
  },
}
```

<Accordion title="WhatsApp متعدد الحسابات">

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: {},
        personal: {},
        biz: {
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

- تستخدم الأوامر الصادرة الحساب `default` افتراضيًا إذا كان موجودًا؛ وإلا فسيتم استخدام أول معرّف حساب مكوَّن (بعد الفرز).
- يجاوز `channels.whatsapp.defaultAccount` الاختياري اختيار الحساب الافتراضي الاحتياطي هذا عندما يطابق معرّف حساب مكوَّن.
- يتم ترحيل دليل مصادقة Baileys القديم أحادي الحساب بواسطة `openclaw doctor` إلى `whatsapp/default`.
- تجاوزات لكل حساب: `channels.whatsapp.accounts.<id>.sendReadReceipts` و`channels.whatsapp.accounts.<id>.dmPolicy` و`channels.whatsapp.accounts.<id>.allowFrom`.

</Accordion>

### Telegram

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groups: {
        "*": { requireMention: true },
        "-1001234567890": {
          allowFrom: ["@admin"],
          systemPrompt: "Keep answers brief.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Stay on topic.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" },
      ],
      historyLimit: 50,
      replyToMode: "first", // off | first | all | batched
      linkPreview: true,
      streaming: "partial", // off | partial | block | progress (default: off; فعّله صراحة لتجنب حدود معدل تعديل المعاينة)
      actions: { reactions: true, sendMessage: true },
      reactionNotifications: "own", // off | own | all
      mediaMaxMb: 100,
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: {
        autoSelectFamily: true,
        dnsResultOrder: "ipv4first",
      },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

- رمز الروبوت: `channels.telegram.botToken` أو `channels.telegram.tokenFile` (ملف عادي فقط؛ تُرفض الروابط الرمزية)، مع `TELEGRAM_BOT_TOKEN` كبديل للحساب الافتراضي.
- يجاوز `channels.telegram.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مكوَّن.
- في إعدادات الحسابات المتعددة (معرّفا حساب أو أكثر)، اضبط قيمة افتراضية صريحة (`channels.telegram.defaultAccount` أو `channels.telegram.accounts.default`) لتجنب التوجيه الاحتياطي؛ ويحذّر `openclaw doctor` عند غياب ذلك أو عدم صحته.
- يمنع `configWrites: false` عمليات كتابة الإعدادات التي يبدأها Telegram (ترحيل معرّفات المجموعات الخارقة، و`/config set|unset`).
- تضبط إدخالات `bindings[]` على المستوى الأعلى مع `type: "acp"` ارتباطات ACP دائمة لموضوعات المنتدى (استخدم `chatId:topic:topicId` القياسي في `match.peer.id`). تتم مشاركة دلالات الحقول في [وكلاء ACP](/ar/tools/acp-agents#channel-specific-settings).
- تستخدم معاينات البث في Telegram `sendMessage` و`editMessageText` (وتعمل في المحادثات المباشرة والجماعية).
- سياسة إعادة المحاولة: راجع [سياسة إعادة المحاولة](/ar/concepts/retry).

### Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 100,
      allowBots: false,
      actions: {
        reactions: true,
        stickers: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        roles: false,
        channelInfo: true,
        voiceStatus: true,
        events: true,
        moderation: false,
      },
      replyToMode: "off", // off | first | all | batched
      dmPolicy: "pairing",
      allowFrom: ["1234567890", "123456789012345678"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["openclaw-dm"] },
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
          ignoreOtherMentions: true,
          reactionNotifications: "own",
          users: ["987654321098765432"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["docs"],
              systemPrompt: "Short answers only.",
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length", // length | newline
      streaming: "off", // off | partial | block | progress (progress تُطابق partial على Discord)
      maxLinesPerMessage: 17,
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // تفعيل اختياري لـ sessions_spawn({ thread: true })
      },
      voice: {
        enabled: true,
        autoJoin: [
          {
            guildId: "123456789012345678",
            channelId: "234567890123456789",
          },
        ],
        daveEncryption: true,
        decryptionFailureTolerance: 24,
        tts: {
          provider: "openai",
          openai: { voice: "alloy" },
        },
      },
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["987654321098765432"],
        agentFilter: ["default"],
        sessionFilter: ["discord:"],
        target: "dm", // dm | channel | both
        cleanupAfterResolve: false,
      },
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

- الرمز: `channels.discord.token`، مع `DISCORD_BOT_TOKEN` كبديل للحساب الافتراضي.
- تستخدم الاستدعاءات الصادرة المباشرة التي توفّر `token` صريحًا لـ Discord ذلك الرمز في الاستدعاء؛ بينما تظل إعدادات إعادة المحاولة/السياسة للحساب مأخوذة من الحساب المحدد في اللقطة النشطة لوقت التشغيل.
- يجاوز `channels.discord.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مكوَّن.
- استخدم `user:<id>` (رسالة خاصة) أو `channel:<id>` (قناة guild) كأهداف للتسليم؛ ويتم رفض المعرّفات الرقمية المجردة.
- تكون slugs الخاصة بـ guild بأحرف صغيرة مع استبدال المسافات بـ `-`؛ وتستخدم مفاتيح القنوات الاسم المحوّل إلى slug (من دون `#`). ويفضَّل استخدام معرّفات guild.
- يتم تجاهل الرسائل التي يكتبها الروبوت افتراضيًا. يفعّل `allowBots: true` قبولها؛ واستخدم `allowBots: "mentions"` لقبول رسائل الروبوت التي تشير إلى الروبوت فقط (مع استمرار تصفية رسائل الروبوت نفسه).
- يقوم `channels.discord.guilds.<id>.ignoreOtherMentions` (وتجاوزات القنوات) بإسقاط الرسائل التي تشير إلى مستخدم أو دور آخر ولكن ليس الروبوت (باستثناء @everyone/@here).
- يقوم `maxLinesPerMessage` (الافتراضي 17) بتقسيم الرسائل الطويلة رأسيًا حتى لو كانت أقل من 2000 حرف.
- يتحكم `channels.discord.threadBindings` في التوجيه المرتبط بخيوط Discord:
  - `enabled`: تجاوز Discord لميزات الجلسات المرتبطة بالخيط (`/focus` و`/unfocus` و`/agents` و`/session idle` و`/session max-age` والتسليم/التوجيه المرتبط)
  - `idleHours`: تجاوز Discord لإلغاء التركيز التلقائي بعد الخمول بالساعات (`0` للتعطيل)
  - `maxAgeHours`: تجاوز Discord للحد الأقصى الصارم للعمر بالساعات (`0` للتعطيل)
  - `spawnSubagentSessions`: مفتاح تفعيل اختياري للإنشاء/الربط التلقائي للخيط بواسطة `sessions_spawn({ thread: true })`
- تضبط إدخالات `bindings[]` على المستوى الأعلى مع `type: "acp"` ارتباطات ACP دائمة للقنوات والخيوط (استخدم معرّف القناة/الخيط في `match.peer.id`). تتم مشاركة دلالات الحقول في [وكلاء ACP](/ar/tools/acp-agents#channel-specific-settings).
- يحدد `channels.discord.ui.components.accentColor` لون التمييز لحاويات Discord components v2.
- يفعّل `channels.discord.voice` محادثات القنوات الصوتية في Discord مع تجاوزات اختيارية للانضمام التلقائي وTTS.
- يتم تمرير `channels.discord.voice.daveEncryption` و`channels.discord.voice.decryptionFailureTolerance` إلى خيارات DAVE في `@discordjs/voice` (القيم الافتراضية `true` و`24`).
- يحاول OpenClaw أيضًا استرداد استقبال الصوت عبر مغادرة جلسة الصوت ثم إعادة الانضمام إليها بعد تكرار فشل فك التشفير.
- يعدّ `channels.discord.streaming` مفتاح وضع البث القياسي. وتتم ترقية القيم القديمة `streamMode` والقيم المنطقية `streaming` تلقائيًا.
- يربط `channels.discord.autoPresence` التوفر أثناء التشغيل بحالة وجود الروبوت (سليم => online، متدهور => idle، منهك => dnd) ويسمح بتجاوزات اختيارية لنص الحالة.
- يعيد `channels.discord.dangerouslyAllowNameMatching` تمكين مطابقة الاسم/الوسم القابلة للتغيير (وضع توافق لكسر الزجاج).
- `channels.discord.execApprovals`: تسليم موافقات exec الأصلية في Discord وتفويض الموافقين.
  - `enabled`: إما `true` أو `false` أو `"auto"` (الافتراضي). في الوضع التلقائي، تُفعَّل موافقات exec عندما يمكن حل الموافقين من `approvers` أو `commands.ownerAllowFrom`.
  - `approvers`: معرّفات مستخدمي Discord المسموح لهم بالموافقة على طلبات exec. وتعود إلى `commands.ownerAllowFrom` عند الحذف.
  - `agentFilter`: قائمة سماح اختيارية لمعرّفات الوكلاء. احذفها لتمرير الموافقات لجميع الوكلاء.
  - `sessionFilter`: أنماط اختيارية لمفاتيح الجلسات (substring أو regex).
  - `target`: أين تُرسل مطالبات الموافقة. ترسل `"dm"` (الافتراضي) إلى الرسائل الخاصة للموافقين، وترسل `"channel"` إلى القناة الأصلية، وترسل `"both"` إلى كليهما. وعندما يتضمن الهدف `"channel"`، لا تكون الأزرار قابلة للاستخدام إلا من قِبل الموافقين المحلولين.
  - `cleanupAfterResolve`: عندما تكون `true`، تحذف رسائل الموافقة الخاصة بعد الموافقة أو الرفض أو انتهاء المهلة.

**أوضاع إشعارات التفاعل:** `off` (لا شيء)، و`own` (رسائل الروبوت، الافتراضي)، و`all` (كل الرسائل)، و`allowlist` (من `guilds.<id>.users` على جميع الرسائل).

### Google Chat

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url", // app-url | project-number
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890",
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["users/1234567890"],
      },
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": { allow: true, requireMention: true },
      },
      actions: { reactions: true },
      typingIndicator: "message",
      mediaMaxMb: 20,
    },
  },
}
```

- JSON الخاص بحساب الخدمة: مضمّن (`serviceAccount`) أو معتمد على ملف (`serviceAccountFile`).
- يُدعَم أيضًا SecretRef لحساب الخدمة (`serviceAccountRef`).
- البدائل من البيئة: `GOOGLE_CHAT_SERVICE_ACCOUNT` أو `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- استخدم `spaces/<spaceId>` أو `users/<userId>` كأهداف للتسليم.
- يعيد `channels.googlechat.dangerouslyAllowNameMatching` تمكين مطابقة البريد الإلكتروني القابلة للتغيير (وضع توافق لكسر الزجاج).

### Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",
      dmPolicy: "pairing",
      allowFrom: ["U123", "U456", "*"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["G123"] },
      channels: {
        C123: { allow: true, requireMention: true, allowBots: false },
        "#general": {
          allow: true,
          requireMention: true,
          allowBots: false,
          users: ["U123"],
          skills: ["docs"],
          systemPrompt: "Short answers only.",
        },
      },
      historyLimit: 50,
      allowBots: false,
      reactionNotifications: "own",
      reactionAllowlist: ["U123"],
      replyToMode: "off", // off | first | all | batched
      thread: {
        historyScope: "thread", // thread | channel
        inheritParent: false,
      },
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true,
      },
      slashCommand: {
        enabled: true,
        name: "openclaw",
        sessionPrefix: "slack:slash",
        ephemeral: true,
      },
      typingReaction: "hourglass_flowing_sand",
      textChunkLimit: 4000,
      chunkMode: "length",
      streaming: "partial", // off | partial | block | progress (وضع معاينة)
      nativeStreaming: true, // استخدم Slack native streaming API عندما streaming=partial
      mediaMaxMb: 20,
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["U123"],
        agentFilter: ["default"],
        sessionFilter: ["slack:"],
        target: "dm", // dm | channel | both
      },
    },
  },
}
```

- **وضع Socket** يتطلب كِلا `botToken` و`appToken` (`SLACK_BOT_TOKEN` و`SLACK_APP_TOKEN` كبدائل بيئية للحساب الافتراضي).
- **وضع HTTP** يتطلب `botToken` بالإضافة إلى `signingSecret` (على الجذر أو لكل حساب).
- تقبل `botToken` و`appToken` و`signingSecret` و`userToken` سلاسل نصية
  صريحة أو كائنات SecretRef.
- تعرض لقطات حسابات Slack حقول المصدر/الحالة لكل بيانات اعتماد، مثل
  `botTokenSource` و`botTokenStatus` و`appTokenStatus` و، في وضع HTTP،
  `signingSecretStatus`. تعني `configured_unavailable` أن الحساب
  مكوَّن من خلال SecretRef لكن مسار الأمر/وقت التشغيل الحالي لم يتمكن
  من حل قيمة السر.
- يمنع `configWrites: false` عمليات كتابة الإعدادات التي يبدأها Slack.
- يجاوز `channels.slack.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مكوَّن.
- يعدّ `channels.slack.streaming` مفتاح وضع البث القياسي. وتتم ترقية القيم القديمة `streamMode` والقيم المنطقية `streaming` تلقائيًا.
- استخدم `user:<id>` (رسالة خاصة) أو `channel:<id>` كأهداف للتسليم.

**أوضاع إشعارات التفاعل:** `off` و`own` (الافتراضي) و`all` و`allowlist` (من `reactionAllowlist`).

**عزل جلسة الخيط:** يكون `thread.historyScope` لكل خيط على حدة (الافتراضي) أو مشتركًا عبر القناة. يقوم `thread.inheritParent` بنسخ سجل القناة الأصلية إلى الخيوط الجديدة.

- تضيف `typingReaction` تفاعلًا مؤقتًا إلى رسالة Slack الواردة أثناء تنفيذ الرد، ثم تزيله عند الاكتمال. استخدم رمز emoji مختصر لـ Slack مثل `"hourglass_flowing_sand"`.
- `channels.slack.execApprovals`: تسليم موافقات exec الأصلية في Slack وتفويض الموافقين. نفس مخطط Discord: `enabled` (`true`/`false`/`"auto"`)، و`approvers` (معرّفات مستخدمي Slack)، و`agentFilter` و`sessionFilter` و`target` (`"dm"` أو `"channel"` أو `"both"`).

| مجموعة الإجراءات | الافتراضي | الملاحظات                 |
| ---------------- | --------- | ------------------------- |
| reactions        | مفعّلة    | تفاعل + سرد التفاعلات     |
| messages         | مفعّلة    | قراءة/إرسال/تحرير/حذف     |
| pins             | مفعّلة    | تثبيت/إلغاء تثبيت/سرد     |
| memberInfo       | مفعّلة    | معلومات العضو             |
| emojiList        | مفعّلة    | قائمة emoji المخصصة       |

### Mattermost

يُشحن Mattermost كإضافة: `openclaw plugins install @openclaw/mattermost`.

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
      chatmode: "oncall", // oncall | onmessage | onchar
      oncharPrefixes: [">", "!"],
      groups: {
        "*": { requireMention: true },
        "team-channel-id": { requireMention: false },
      },
      commands: {
        native: true, // تفعيل اختياري
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // عنوان URL صريح اختياري لعمليات النشر ذات الوكيل العكسي/العامة
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

أوضاع الدردشة: `oncall` (الرد عند @-mention، الافتراضي)، و`onmessage` (كل رسالة)، و`onchar` (الرسائل التي تبدأ ببادئة تشغيل).

عند تفعيل الأوامر الأصلية في Mattermost:

- يجب أن تكون `commands.callbackPath` مسارًا (على سبيل المثال `/api/channels/mattermost/command`)، لا عنوان URL كاملًا.
- يجب أن تُحل `commands.callbackUrl` إلى نقطة نهاية بوابة OpenClaw وأن يكون خادم Mattermost قادرًا على الوصول إليها.
- تتم مصادقة استدعاءات slash الأصلية بواسطة الرموز المميزة لكل أمر التي يعيدها
  Mattermost أثناء تسجيل أوامر slash. وإذا فشل التسجيل أو لم يتم
  تفعيل أي أوامر، يرفض OpenClaw الاستدعاءات برسالة
  `Unauthorized: invalid command token.`
- بالنسبة إلى مضيفات الاستدعاء الخاصة/الداخلية/ذات tailnet، قد يتطلب Mattermost
  أن تتضمن `ServiceSettings.AllowedUntrustedInternalConnections` المضيف/النطاق الخاص بالاستدعاء.
  استخدم قيم المضيف/النطاق، وليس عناوين URL كاملة.
- `channels.mattermost.configWrites`: السماح أو المنع لعمليات كتابة الإعدادات التي يبدأها Mattermost.
- `channels.mattermost.requireMention`: يتطلب `@mention` قبل الرد في القنوات.
- `channels.mattermost.groups.<channelId>.requireMention`: تجاوز بوابة الإشارة لكل قناة (`"*"` للقيمة الافتراضية).
- يجاوز `channels.mattermost.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مكوَّن.

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // ربط حساب اختياري
      dmPolicy: "pairing",
      allowFrom: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      configWrites: true,
      reactionNotifications: "own", // off | own | all | allowlist
      reactionAllowlist: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      historyLimit: 50,
    },
  },
}
```

**أوضاع إشعارات التفاعل:** `off` و`own` (الافتراضي) و`all` و`allowlist` (من `reactionAllowlist`).

- `channels.signal.account`: يثبّت بدء تشغيل القناة على هوية حساب Signal محددة.
- `channels.signal.configWrites`: السماح أو المنع لعمليات كتابة الإعدادات التي يبدأها Signal.
- يجاوز `channels.signal.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مكوَّن.

### BlueBubbles

BlueBubbles هو المسار الموصى به لـ iMessage (مدعوم بإضافة، ومكوَّن ضمن `channels.bluebubbles`).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl، وpassword، وwebhookPath، وعناصر التحكم في المجموعة، والإجراءات المتقدمة:
      // راجع /channels/bluebubbles
    },
  },
}
```

- مسارات المفاتيح الأساسية المغطاة هنا: `channels.bluebubbles` و`channels.bluebubbles.dmPolicy`.
- يجاوز `channels.bluebubbles.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مكوَّن.
- يمكن لإدخالات `bindings[]` على المستوى الأعلى مع `type: "acp"` ربط محادثات BlueBubbles بجلسات ACP دائمة. استخدم مقبض BlueBubbles أو سلسلة الهدف (`chat_id:*` أو `chat_guid:*` أو `chat_identifier:*`) في `match.peer.id`. دلالات الحقول المشتركة: [وكلاء ACP](/ar/tools/acp-agents#channel-specific-settings).
- تم توثيق إعداد قناة BlueBubbles الكامل في [BlueBubbles](/ar/channels/bluebubbles).

### iMessage

يقوم OpenClaw بتشغيل `imsg rpc` ‏(JSON-RPC عبر stdio). لا حاجة إلى daemon أو منفذ.

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host",
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123"],
      historyLimit: 50,
      includeAttachments: false,
      attachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      remoteAttachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      mediaMaxMb: 16,
      service: "auto",
      region: "US",
    },
  },
}
```

- يجاوز `channels.imessage.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مكوَّن.

- يتطلب Full Disk Access إلى قاعدة بيانات Messages.
- يُفضَّل استخدام أهداف `chat_id:<id>`. استخدم `imsg chats --limit 20` لسرد المحادثات.
- يمكن أن يشير `cliPath` إلى غلاف SSH؛ اضبط `remoteHost` (`host` أو `user@host`) لجلب المرفقات عبر SCP.
- تقيد `attachmentRoots` و`remoteAttachmentRoots` مسارات المرفقات الواردة (الافتراضي: `/Users/*/Library/Messages/Attachments`).
- يستخدم SCP تحققًا صارمًا من مفتاح المضيف، لذا تأكد من أن مفتاح مضيف relay موجود بالفعل في `~/.ssh/known_hosts`.
- `channels.imessage.configWrites`: السماح أو المنع لعمليات كتابة الإعدادات التي يبدأها iMessage.
- يمكن لإدخالات `bindings[]` على المستوى الأعلى مع `type: "acp"` ربط محادثات iMessage بجلسات ACP دائمة. استخدم مقبضًا مسوّى أو هدف محادثة صريحًا (`chat_id:*` أو `chat_guid:*` أو `chat_identifier:*`) في `match.peer.id`. دلالات الحقول المشتركة: [وكلاء ACP](/ar/tools/acp-agents#channel-specific-settings).

<Accordion title="مثال غلاف SSH لـ iMessage">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix مدعوم بإضافة ويُكوَّن ضمن `channels.matrix`.

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
      encryption: true,
      initialSyncLimit: 20,
      defaultAccount: "ops",
      accounts: {
        ops: {
          name: "Ops",
          userId: "@ops:example.org",
          accessToken: "syt_ops_xxx",
        },
        alerts: {
          userId: "@alerts:example.org",
          password: "secret",
          proxy: "http://127.0.0.1:7891",
        },
      },
    },
  },
}
```

- تستخدم مصادقة الرمز `accessToken`؛ وتستخدم مصادقة كلمة المرور `userId` + `password`.
- يقوم `channels.matrix.proxy` بتوجيه حركة HTTP الخاصة بـ Matrix عبر وكيل HTTP(S) صريح. ويمكن للحسابات المسماة تجاوزه عبر `channels.matrix.accounts.<id>.proxy`.
- يسمح `channels.matrix.network.dangerouslyAllowPrivateNetwork` بخوادم homeserver الخاصة/الداخلية. ويُعد `proxy` وهذا التفعيل الشبكي عنصرَي تحكم مستقلين.
- يحدد `channels.matrix.defaultAccount` الحساب المفضل في إعدادات الحسابات المتعددة.
- تكون القيمة الافتراضية لـ `channels.matrix.autoJoin` هي `off`، لذا يتم تجاهل الغرف المدعو إليها والدعوات الجديدة ذات نمط الرسائل الخاصة حتى تضبط `autoJoin: "allowlist"` مع `autoJoinAllowlist` أو `autoJoin: "always"`.
- `channels.matrix.execApprovals`: تسليم موافقات exec الأصلية في Matrix وتفويض الموافقين.
  - `enabled`: إما `true` أو `false` أو `"auto"` (الافتراضي). في الوضع التلقائي، تُفعَّل موافقات exec عندما يمكن حل الموافقين من `approvers` أو `commands.ownerAllowFrom`.
  - `approvers`: معرّفات مستخدمي Matrix (مثل `@owner:example.org`) المسموح لهم بالموافقة على طلبات exec.
  - `agentFilter`: قائمة سماح اختيارية لمعرّفات الوكلاء. احذفها لتمرير الموافقات لجميع الوكلاء.
  - `sessionFilter`: أنماط اختيارية لمفاتيح الجلسات (substring أو regex).
  - `target`: أين تُرسل مطالبات الموافقة. `"dm"` (الافتراضي)، أو `"channel"` (الغرفة الأصلية)، أو `"both"`.
  - تجاوزات لكل حساب: `channels.matrix.accounts.<id>.execApprovals`.
- يتحكم `channels.matrix.dm.sessionScope` في كيفية تجميع الرسائل الخاصة في Matrix ضمن الجلسات: `per-user` (الافتراضي) يشارك بحسب النظير الموجَّه، بينما `per-room` يعزل كل غرفة رسائل خاصة.
- تستخدم فحوصات الحالة في Matrix وعمليات البحث المباشر في الدليل نفس سياسة الوكيل الخاصة بحركة وقت التشغيل.
- تم توثيق إعداد Matrix الكامل وقواعد الاستهداف وأمثلة الإعداد في [Matrix](/ar/channels/matrix).

### Microsoft Teams

Microsoft Teams مدعوم بإضافة ويُكوَّن ضمن `channels.msteams`.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId، وappPassword، وtenantId، وwebhook، وسياسات الفريق/القناة:
      // راجع /channels/msteams
    },
  },
}
```

- مسارات المفاتيح الأساسية المغطاة هنا: `channels.msteams` و`channels.msteams.configWrites`.
- تم توثيق إعداد Teams الكامل (بيانات الاعتماد، وwebhook، وسياسة الرسائل الخاصة/المجموعات، والتجاوزات لكل فريق/قناة) في [Microsoft Teams](/ar/channels/msteams).

### IRC

IRC مدعوم بإضافة ويُكوَّن ضمن `channels.irc`.

```json5
{
  channels: {
    irc: {
      enabled: true,
      dmPolicy: "pairing",
      configWrites: true,
      nickserv: {
        enabled: true,
        service: "NickServ",
        password: "${IRC_NICKSERV_PASSWORD}",
        register: false,
        registerEmail: "bot@example.com",
      },
    },
  },
}
```

- مسارات المفاتيح الأساسية المغطاة هنا: `channels.irc` و`channels.irc.dmPolicy` و`channels.irc.configWrites` و`channels.irc.nickserv.*`.
- يجاوز `channels.irc.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مكوَّن.
- تم توثيق إعداد قناة IRC الكامل (المضيف/المنفذ/TLS/القنوات/قوائم السماح/بوابة الإشارة) في [IRC](/ar/channels/irc).

### متعدد الحسابات (كل القنوات)

شغّل عدة حسابات لكل قناة (كل منها مع `accountId` خاص به):

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "Primary bot",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "Alerts bot",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- يُستخدم `default` عندما يتم حذف `accountId` (في CLI + التوجيه).
- تنطبق رموز البيئة فقط على الحساب **الافتراضي**.
- تنطبق إعدادات القناة الأساسية على جميع الحسابات ما لم يتم تجاوزها لكل حساب.
- استخدم `bindings[].match.accountId` لتوجيه كل حساب إلى وكيل مختلف.
- إذا أضفت حسابًا غير افتراضي عبر `openclaw channels add` (أو عبر إعداد القناة) بينما لا تزال تستخدم إعداد قناة أحادي الحساب على المستوى الأعلى، فسيقوم OpenClaw أولًا بترقية القيم أحادية الحساب الموجودة على المستوى الأعلى والمحددة نطاقًا بالحساب إلى خريطة حسابات القناة حتى يستمر الحساب الأصلي في العمل. تنقل معظم القنوات هذه القيم إلى `channels.<channel>.accounts.default`؛ بينما يمكن لـ Matrix الاحتفاظ بهدف مسمى/افتراضي قائم ومطابق بدلًا من ذلك.
- تستمر ارتباطات القناة فقط الموجودة (من دون `accountId`) في مطابقة الحساب الافتراضي؛ وتظل الارتباطات المقيّدة بالحساب اختيارية.
- يقوم `openclaw doctor --fix` أيضًا بإصلاح الأشكال المختلطة عبر نقل القيم أحادية الحساب على المستوى الأعلى والمقيدة بالحساب إلى الحساب المُرقّى المختار لتلك القناة. تستخدم معظم القنوات `accounts.default`؛ بينما يمكن لـ Matrix الاحتفاظ بهدف مسمى/افتراضي قائم ومطابق بدلًا من ذلك.

### قنوات الإضافات الأخرى

تُكوَّن العديد من قنوات الإضافات على شكل `channels.<id>` ويتم توثيقها في صفحات القنوات المخصصة لها (على سبيل المثال Feishu وMatrix وLINE وNostr وZalo وNextcloud Talk وSynology Chat وTwitch).
راجع فهرس القنوات الكامل: [القنوات](/ar/channels).

### بوابة الإشارة في الدردشة الجماعية

تتطلب رسائل المجموعات افتراضيًا **الإشارة** (إشارة metadata أو أنماط regex آمنة). وينطبق ذلك على الدردشات الجماعية في WhatsApp وTelegram وDiscord وGoogle Chat وiMessage.

**أنواع الإشارة:**

- **إشارات metadata**: إشارات @-mentions الأصلية للمنصة. ويتم تجاهلها في وضع الدردشة الذاتية لـ WhatsApp.
- **أنماط النص**: أنماط regex آمنة في `agents.list[].groupChat.mentionPatterns`. ويتم تجاهل الأنماط غير الصالحة والتكرار المتداخل غير الآمن.
- يتم فرض بوابة الإشارة فقط عندما يكون الاكتشاف ممكنًا (إشارات أصلية أو نمط واحد على الأقل).

```json5
{
  messages: {
    groupChat: { historyLimit: 50 },
  },
  agents: {
    list: [{ id: "main", groupChat: { mentionPatterns: ["@openclaw", "openclaw"] } }],
  },
}
```

يضبط `messages.groupChat.historyLimit` القيمة الافتراضية العامة. ويمكن للقنوات التجاوز عبر `channels.<channel>.historyLimit` (أو لكل حساب). اضبط `0` للتعطيل.

#### حدود سجل الرسائل الخاصة

```json5
{
  channels: {
    telegram: {
      dmHistoryLimit: 30,
      dms: {
        "123456789": { historyLimit: 50 },
      },
    },
  },
}
```

آلية الحل: تجاوز لكل رسالة خاصة → القيمة الافتراضية للمزوّد → بلا حد (يتم الاحتفاظ بكل شيء).

المدعوم: `telegram` و`whatsapp` و`discord` و`slack` و`signal` و`imessage` و`msteams`.

#### وضع الدردشة الذاتية

ضمّن رقمك الخاص في `allowFrom` لتفعيل وضع الدردشة الذاتية (يتجاهل إشارات @ الأصلية، ويرد فقط على أنماط النص):

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: { mentionPatterns: ["reisponde", "@openclaw"] },
      },
    ],
  },
}
```

### الأوامر (معالجة أوامر الدردشة)

```json5
{
  commands: {
    native: "auto", // تسجيل الأوامر الأصلية عندما تكون مدعومة
    text: true, // تحليل /commands في رسائل الدردشة
    bash: false, // السماح بـ ! (اسم بديل: /bash)
    bashForegroundMs: 2000,
    config: false, // السماح بـ /config
    debug: false, // السماح بـ /debug
    restart: false, // السماح بـ /restart + أداة إعادة تشغيل البوابة
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="تفاصيل الأوامر">

- يجب أن تكون الأوامر النصية رسائل **مستقلة** مع `/` في البداية.
- يقوم `native: "auto"` بتشغيل الأوامر الأصلية لـ Discord/Telegram، ويترك Slack معطّلًا.
- تجاوز لكل قناة: `channels.discord.commands.native` (قيمة منطقية أو `"auto"`). تقوم `false` بمسح الأوامر المسجلة سابقًا.
- يضيف `channels.telegram.customCommands` إدخالات إضافية إلى قائمة روبوت Telegram.
- يفعّل `bash: true` الأمر `! <cmd>` لصدفة المضيف. ويتطلب `tools.elevated.enabled` وأن يكون المرسل موجودًا في `tools.elevated.allowFrom.<channel>`.
- يفعّل `config: true` الأمر `/config` (قراءة/كتابة `openclaw.json`). بالنسبة إلى عملاء البوابة `chat.send`، تتطلب أيضًا عمليات الكتابة المستمرة عبر `/config set|unset` صلاحية `operator.admin`؛ بينما يظل `/config show` للقراءة فقط متاحًا لعملاء المشغّل العاديين ذوي نطاق الكتابة.
- تتحكم `channels.<provider>.configWrites` في طفرات الإعدادات لكل قناة (الافتراضي: true).
- بالنسبة إلى القنوات متعددة الحسابات، تتحكم أيضًا `channels.<provider>.accounts.<id>.configWrites` في عمليات الكتابة التي تستهدف ذلك الحساب (على سبيل المثال `/allowlist --config --account <id>` أو `/config set channels.<provider>.accounts.<id>...`).
- تكون `allowFrom` لكل مزوّد. وعند تعيينها، فإنها تكون **المصدر الوحيد** للتفويض (ويتم تجاهل قوائم سماح القناة/الاقتران و`useAccessGroups`).
- يسمح `useAccessGroups: false` للأوامر بتجاوز سياسات مجموعات الوصول عندما لا تكون `allowFrom` معيّنة.

</Accordion>

---

## الإعدادات الافتراضية للوكلاء

### `agents.defaults.workspace`

الافتراضي: `~/.openclaw/workspace`.

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

جذر مستودع اختياري يظهر في سطر Runtime ضمن system prompt. وإذا لم يُعيّن، يكتشفه OpenClaw تلقائيًا من خلال الصعود من مساحة العمل.

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

قائمة سماح افتراضية اختيارية لـ Skills للوكلاء الذين لا يضبطون
`agents.list[].skills`.

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // يرث github, weather
      { id: "docs", skills: ["docs-search"] }, // يستبدل الإعدادات الافتراضية
      { id: "locked-down", skills: [] }, // بلا Skills
    ],
  },
}
```

- احذف `agents.defaults.skills` للحصول على Skills غير مقيّدة افتراضيًا.
- احذف `agents.list[].skills` لوراثة الإعدادات الافتراضية.
- اضبط `agents.list[].skills: []` لعدم استخدام أي Skills.
- تكون القائمة غير الفارغة في `agents.list[].skills` هي المجموعة النهائية لذلك الوكيل؛
  ولا يتم دمجها مع الإعدادات الافتراضية.

### `agents.defaults.skipBootstrap`

يعطّل الإنشاء التلقائي لملفات bootstrap في مساحة العمل (`AGENTS.md` و`SOUL.md` و`TOOLS.md` و`IDENTITY.md` و`USER.md` و`HEARTBEAT.md` و`BOOTSTRAP.md`).

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

يتحكم في وقت حقن ملفات bootstrap الخاصة بمساحة العمل في system prompt. القيمة الافتراضية: `"always"`.

- `"continuation-skip"`: تتخطى أدوار المتابعة الآمنة (بعد رد مساعد مكتمل) إعادة حقن bootstrap الخاص بمساحة العمل، مما يقلل حجم prompt. وتعيد تشغيلات نبض الحياة وإعادة المحاولة بعد الضغط بناء السياق.

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

الحد الأقصى لعدد الأحرف لكل ملف bootstrap في مساحة العمل قبل الاقتصاص. الافتراضي: `20000`.

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

الحد الأقصى لإجمالي الأحرف المحقونة عبر جميع ملفات bootstrap الخاصة بمساحة العمل. الافتراضي: `150000`.

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

يتحكم في نص التحذير المرئي للوكيل عندما يتم اقتطاع سياق bootstrap.
الافتراضي: `"once"`.

- `"off"`: لا يحقن نص تحذير في system prompt مطلقًا.
- `"once"`: يحقن التحذير مرة واحدة لكل توقيع اقتطاع فريد (موصى به).
- `"always"`: يحقن التحذير في كل تشغيل عندما يوجد اقتطاع.

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

الحد الأقصى لحجم البكسل لأطول ضلع في الصور ضمن كتل الصور الخاصة بالسجل/الأدوات قبل استدعاءات المزوّد.
الافتراضي: `1200`.

تقلل القيم الأقل عادة من استخدام vision-token وحجم حمولة الطلب في التشغيلات الثقيلة لصور الشاشة.
وتحافظ القيم الأعلى على مزيد من التفاصيل المرئية.

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

المنطقة الزمنية لسياق system prompt (وليس طوابع وقت الرسائل). وتعود إلى المنطقة الزمنية للمضيف.

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

تنسيق الوقت في system prompt. الافتراضي: `auto` (تفضيل نظام التشغيل).

```json5
{
  agents: { defaults: { timeFormat: "auto" } }, // auto | 12 | 24
}
```

### `agents.defaults.model`

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview"],
      },
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-i2v"],
      },
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.4-mini"],
      },
      params: { cacheRetention: "long" }, // معاملات المزوّد الافتراضية العامة
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
      thinkingDefault: "low",
      verboseDefault: "off",
      elevatedDefault: "on",
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      contextTokens: 200000,
      maxConcurrent: 3,
    },
  },
}
```

- يقبل `model` إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يضبط الشكل النصي النموذج الأساسي فقط.
  - يضبط شكل الكائن النموذج الأساسي بالإضافة إلى نماذج الفشل الاحتياطية المرتّبة.
- يقبل `imageModel` إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يُستخدم بواسطة مسار أداة `image` كإعداد نموذج الرؤية الخاص بها.
  - ويُستخدم أيضًا كتوجيه احتياطي عندما لا يستطيع النموذج المحدد/الافتراضي قبول إدخال صور.
- يقبل `imageGenerationModel` إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يُستخدم بواسطة قدرة توليد الصور المشتركة وأي سطح أداة/إضافة مستقبلي يولّد الصور.
  - القيم النموذجية: `google/gemini-3.1-flash-image-preview` لتوليد صور Gemini الأصلي، أو `fal/fal-ai/flux/dev` لـ fal، أو `openai/gpt-image-1` لـ OpenAI Images.
  - إذا حددت مزوّدًا/نموذجًا مباشرة، فاضبط أيضًا مصادقة/مفتاح API للمزوّد المطابق (على سبيل المثال `GEMINI_API_KEY` أو `GOOGLE_API_KEY` لـ `google/*`، و`OPENAI_API_KEY` لـ `openai/*`، و`FAL_KEY` لـ `fal/*`).
  - إذا تم حذفها، فلا يزال بإمكان `image_generate` استنتاج قيمة افتراضية لمزوّد مدعوم بالمصادقة. وهو يجرّب أولًا المزوّد الافتراضي الحالي، ثم بقية مزوّدي توليد الصور المسجلين بترتيب معرّف المزوّد.
- يقبل `musicGenerationModel` إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يُستخدم بواسطة قدرة توليد الموسيقى المشتركة والأداة المضمّنة `music_generate`.
  - القيم النموذجية: `google/lyria-3-clip-preview` أو `google/lyria-3-pro-preview` أو `minimax/music-2.5+`.
  - إذا تم حذفها، فلا يزال بإمكان `music_generate` استنتاج قيمة افتراضية لمزوّد مدعوم بالمصادقة. وهو يجرّب أولًا المزوّد الافتراضي الحالي، ثم بقية مزوّدي توليد الموسيقى المسجلين بترتيب معرّف المزوّد.
  - إذا حددت مزوّدًا/نموذجًا مباشرة، فاضبط أيضًا مصادقة/مفتاح API للمزوّد المطابق.
- يقبل `videoGenerationModel` إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يُستخدم بواسطة قدرة توليد الفيديو المشتركة والأداة المضمّنة `video_generate`.
  - القيم النموذجية: `qwen/wan2.6-t2v` أو `qwen/wan2.6-i2v` أو `qwen/wan2.6-r2v` أو `qwen/wan2.6-r2v-flash` أو `qwen/wan2.7-r2v`.
  - إذا تم حذفها، فلا يزال بإمكان `video_generate` استنتاج قيمة افتراضية لمزوّد مدعوم بالمصادقة. وهو يجرّب أولًا المزوّد الافتراضي الحالي، ثم بقية مزوّدي توليد الفيديو المسجلين بترتيب معرّف المزوّد.
  - إذا حددت مزوّدًا/نموذجًا مباشرة، فاضبط أيضًا مصادقة/مفتاح API للمزوّد المطابق.
  - يدعم مزوّد توليد الفيديو المضمّن Qwen حاليًا حتى فيديو خرج واحد، وصورة دخل واحدة، و4 فيديوهات دخل، ومدة 10 ثوانٍ، وخيارات على مستوى المزوّد مثل `size` و`aspectRatio` و`resolution` و`audio` و`watermark`.
- يقبل `pdfModel` إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يُستخدم بواسطة أداة `pdf` لتوجيه النموذج.
  - إذا تم حذفها، تعود أداة PDF إلى `imageModel`، ثم إلى النموذج المحلول للجلسة/الافتراضي.
- `pdfMaxBytesMb`: الحد الافتراضي لحجم PDF لأداة `pdf` عندما لا يتم تمرير `maxBytesMb` وقت الاستدعاء.
- `pdfMaxPages`: الحد الأقصى الافتراضي للصفحات التي ينظر إليها وضع الاستخراج الاحتياطي في أداة `pdf`.
- `verboseDefault`: مستوى verbose الافتراضي للوكلاء. القيم: `"off"` و`"on"` و`"full"`. الافتراضي: `"off"`.
- `elevatedDefault`: مستوى المخرجات المرتفعة الافتراضي للوكلاء. القيم: `"off"` و`"on"` و`"ask"` و`"full"`. الافتراضي: `"on"`.
- `model.primary`: التنسيق `provider/model` (مثل `openai/gpt-5.4`). إذا حذفت المزوّد، يحاول OpenClaw أولًا اسمًا مستعارًا، ثم مطابقة فريدة لمزوّد مكوَّن لهذا المعرّف الدقيق للنموذج، وبعدها فقط يعود إلى المزوّد الافتراضي المكوَّن (سلوك توافق قديم، لذا يفضَّل `provider/model` الصريح). وإذا لم يعد ذلك المزوّد يوفّر النموذج الافتراضي المكوَّن، يعود OpenClaw إلى أول مزوّد/نموذج مكوَّن بدلًا من إظهار قيمة افتراضية قديمة لمزوّد تمت إزالته.
- `models`: كتالوج النماذج المكوَّن وقائمة السماح الخاصة بـ `/model`. يمكن أن يتضمن كل إدخال `alias` (اختصارًا) و`params` (خاصة بالمزوّد، مثل `temperature` و`maxTokens` و`cacheRetention` و`context1m`).
- `params`: معاملات المزوّد الافتراضية العامة المطبقة على جميع النماذج. وتُضبط عند `agents.defaults.params` (مثل `{ cacheRetention: "long" }`).
- أسبقية دمج `params` (في الإعداد): يتم تجاوز `agents.defaults.params` (القاعدة العامة) بواسطة `agents.defaults.models["provider/model"].params` (لكل نموذج)، ثم تتجاوزها `agents.list[].params` (لمعرّف الوكيل المطابق) حسب المفتاح. راجع [Prompt Caching](/ar/reference/prompt-caching) للتفاصيل.
- يقوم كتّاب الإعداد الذين يغيّرون هذه الحقول (على سبيل المثال `/models set` و`/models set-image` وأوامر إضافة/إزالة fallback) بحفظ الشكل القياسي للكائن والحفاظ على قوائم fallback الموجودة عندما يكون ذلك ممكنًا.
- `maxConcurrent`: الحد الأقصى لتشغيلات الوكلاء المتوازية عبر الجلسات (مع بقاء كل جلسة مسلسلة). الافتراضي: 4.

**اختصارات الأسماء المستعارة المضمّنة** (لا تُطبّق إلا عندما يكون النموذج موجودًا في `agents.defaults.models`):

| الاسم المستعار      | النموذج                                |
| ------------------- | -------------------------------------- |
| `opus`              | `anthropic/claude-opus-4-6`            |
| `sonnet`            | `anthropic/claude-sonnet-4-6`          |
| `gpt`               | `openai/gpt-5.4`                       |
| `gpt-mini`          | `openai/gpt-5.4-mini`                  |
| `gpt-nano`          | `openai/gpt-5.4-nano`                  |
| `gemini`            | `google/gemini-3.1-pro-preview`        |
| `gemini-flash`      | `google/gemini-3-flash-preview`        |
| `gemini-flash-lite` | `google/gemini-3.1-flash-lite-preview` |

تتغلب الأسماء المستعارة التي تضبطها أنت دائمًا على القيم الافتراضية.

تفعّل نماذج Z.AI GLM-4.x وضع التفكير تلقائيًا ما لم تضبط `--thinking off` أو تعرّف `agents.defaults.models["zai/<model>"].params.thinking` بنفسك.
وتفعّل نماذج Z.AI القيمة `tool_stream` افتراضيًا لبث استدعاءات الأدوات. اضبط `agents.defaults.models["zai/<model>"].params.tool_stream` إلى `false` لتعطيلها.
وتستخدم نماذج Anthropic Claude 4.6 القيمة الافتراضية `adaptive` للتفكير عندما لا يكون هناك مستوى تفكير صريح.

### `agents.defaults.cliBackends`

واجهات CLI خلفية اختيارية لتشغيلات النص فقط الاحتياطية (من دون استدعاءات أدوات). وهي مفيدة كنسخة احتياطية عندما تفشل مزوّدات API.

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          modelArg: "--model",
          sessionArg: "--session",
          sessionMode: "existing",
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
        },
      },
    },
  },
}
```

- الواجهات الخلفية لـ CLI موجهة للنص أولًا؛ وتكون الأدوات معطّلة دائمًا.
- تُدعَم الجلسات عندما يكون `sessionArg` معيّنًا.
- يُدعَم تمرير الصور عندما يقبل `imageArg` مسارات الملفات.

### `agents.defaults.heartbeat`

تشغيلات نبض حياة دورية.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m للتعطيل
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        lightContext: false, // الافتراضي: false؛ تجعل true الإبقاء على HEARTBEAT.md فقط من ملفات bootstrap الخاصة بمساحة العمل
        isolatedSession: false, // الافتراضي: false؛ تجعل true كل نبضة تعمل في جلسة جديدة (من دون سجل محادثة)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (الافتراضي) | block
        target: "none", // الافتراضي: none | الخيارات: last | whatsapp | telegram | discord | ...
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
      },
    },
  },
}
```

- `every`: سلسلة مدة (ms/s/m/h). الافتراضي: `30m` (مصادقة API-key) أو `1h` (مصادقة OAuth). اضبطها إلى `0m` للتعطيل.
- `suppressToolErrorWarnings`: عندما تكون true، تكبت حمولات تحذير أخطاء الأدوات أثناء تشغيلات نبض الحياة.
- `directPolicy`: سياسة التسليم المباشر/الرسائل الخاصة. تسمح `allow` (الافتراضي) بالتسليم إلى هدف مباشر. وتمنع `block` التسليم إلى هدف مباشر وتصدر `reason=dm-blocked`.
- `lightContext`: عندما تكون true، تستخدم تشغيلات نبض الحياة سياق bootstrap خفيفًا وتحتفظ فقط بـ `HEARTBEAT.md` من ملفات bootstrap الخاصة بمساحة العمل.
- `isolatedSession`: عندما تكون true، تعمل كل نبضة في جلسة جديدة من دون أي سجل محادثة سابق. نفس نمط العزل المستخدم في cron `sessionTarget: "isolated"`. ويقلل تكلفة tokens لكل نبضة من نحو 100K إلى 2-5K tokens.
- لكل وكيل: اضبط `agents.list[].heartbeat`. وعندما يعرّف أي وكيل `heartbeat`، **فإن هؤلاء الوكلاء فقط** هم الذين ينفذون نبضات الحياة.
- تنفذ نبضات الحياة أدوار وكيل كاملة — والفترات الأقصر تستهلك tokens أكثر.

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        timeoutSeconds: 900,
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "Preserve deployment IDs, ticket IDs, and host:port pairs exactly.", // تُستخدم عندما identifierPolicy=custom
        postCompactionSections: ["Session Startup", "Red Lines"], // [] للتعطيل
        model: "openrouter/anthropic/claude-sonnet-4-6", // تجاوز اختياري للنموذج الخاص بالضغط فقط
        notifyUser: true, // أرسل إشعارًا موجزًا عند بدء الضغط (الافتراضي: false)
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with the exact silent token NO_REPLY if nothing to store.",
        },
      },
    },
  },
}
```

- `mode`: إما `default` أو `safeguard` (تلخيص مجزأ للسجلات الطويلة). راجع [الضغط](/ar/concepts/compaction).
- `timeoutSeconds`: الحد الأقصى للثواني المسموح بها لعملية ضغط واحدة قبل أن يقوم OpenClaw بإلغائها. الافتراضي: `900`.
- `identifierPolicy`: إما `strict` (الافتراضي) أو `off` أو `custom`. تقوم `strict` بإضافة إرشادات مضمّنة للاحتفاظ بالمعرّفات غير الشفافة أثناء تلخيص الضغط.
- `identifierInstructions`: نص اختياري مخصص للحفاظ على المعرّفات يُستخدم عندما `identifierPolicy=custom`.
- `postCompactionSections`: أسماء أقسام H2/H3 اختيارية من AGENTS.md لإعادة حقنها بعد الضغط. والقيمة الافتراضية هي `["Session Startup", "Red Lines"]`؛ اضبط `[]` للتعطيل. وعندما لا تكون معيّنة أو عندما تُضبط صراحة على هذا الزوج الافتراضي، تُقبل أيضًا العناوين القديمة `Every Session`/`Safety` كبديل قديم.
- `model`: تجاوز اختياري بصيغة `provider/model-id` للتلخيص الخاص بالضغط فقط. استخدمه عندما يجب أن تبقى الجلسة الرئيسية على نموذج معيّن بينما تعمل ملخصات الضغط على نموذج آخر؛ وعند حذفه، يستخدم الضغط النموذج الأساسي للجلسة.
- `notifyUser`: عندما تكون `true`، يرسل إشعارًا موجزًا إلى المستخدم عند بدء الضغط (على سبيل المثال، "Compacting context..."). وهو معطل افتراضيًا لإبقاء الضغط صامتًا.
- `memoryFlush`: دور وكيل صامت قبل الضغط التلقائي لتخزين الذكريات الدائمة. ويتم تخطيه عندما تكون مساحة العمل للقراءة فقط.

### `agents.defaults.contextPruning`

يقوم بتقليم **نتائج الأدوات القديمة** من السياق الموجود في الذاكرة قبل إرسالها إلى LLM. وهو **لا** يغيّر سجل الجلسة على القرص.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // مدة (ms/s/m/h)، الوحدة الافتراضية: دقائق
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Old tool result content cleared]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="سلوك وضع cache-ttl">

- يفعّل `mode: "cache-ttl"` تمريرات التقليم.
- يتحكم `ttl` في عدد المرات التي يمكن بعدها تشغيل التقليم مجددًا (بعد آخر لمسة على cache).
- يقوم التقليم أولًا باقتطاع نتائج الأدوات كبيرة الحجم اقتطاعًا ناعمًا، ثم يمسح نتائج الأدوات الأقدم مسحًا كاملًا إذا لزم الأمر.

**الاقتطاع الناعم** يحتفظ بالبداية + النهاية ويُدرج `...` في الوسط.

**المسح الكامل** يستبدل نتيجة الأداة بالكامل بالنص البديل.

ملاحظات:

- لا يتم أبدًا اقتطاع/مسح كتل الصور.
- تستند النِّسب إلى الأحرف (تقريبية)، وليست إلى أعداد tokens الدقيقة.
- إذا كان عدد رسائل المساعد أقل من `keepLastAssistants`، يتم تخطي التقليم.

</Accordion>

راجع [تقليم الجلسة](/ar/concepts/session-pruning) لتفاصيل السلوك.

### البث الكتلي

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (استخدم minMs/maxMs)
    },
  },
}
```

- تتطلب القنوات غير Telegram تعيين `*.blockStreaming: true` صراحة لتفعيل الردود الكتلية.
- تجاوزات القنوات: `channels.<channel>.blockStreamingCoalesce` (وتغايرات كل حساب). تستخدم Signal/Slack/Discord/Google Chat افتراضيًا `minChars: 1500`.
- `humanDelay`: توقف عشوائي بين الردود الكتلية. وتعني `natural` ‏800–2500ms. تجاوز لكل وكيل: `agents.list[].humanDelay`.

راجع [البث](/ar/concepts/streaming) لمعرفة السلوك وتفاصيل التقسيم.

### مؤشرات الكتابة

```json5
{
  agents: {
    defaults: {
      typingMode: "instant", // never | instant | thinking | message
      typingIntervalSeconds: 6,
    },
  },
}
```

- القيم الافتراضية: `instant` للمحادثات المباشرة/الإشارات، و`message` للمحادثات الجماعية غير المشار فيها.
- تجاوزات لكل جلسة: `session.typingMode` و`session.typingIntervalSeconds`.

راجع [مؤشرات الكتابة](/ar/concepts/typing-indicators).

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

العزل الاختياري للوكيل المضمّن. راجع [العزل](/ar/gateway/sandboxing) للدليل الكامل.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        backend: "docker", // docker | ssh | openshell
        scope: "agent", // session | agent | shared
        workspaceAccess: "none", // none | ro | rw
        workspaceRoot: "~/.openclaw/sandboxes",
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          containerPrefix: "openclaw-sbx-",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: {
            nofile: { soft: 1024, hard: 2048 },
            nproc: 256,
          },
          seccompProfile: "/path/to/seccomp.json",
          apparmorProfile: "openclaw-sandbox",
          dns: ["1.1.1.1", "8.8.8.8"],
          extraHosts: ["internal.service:10.0.0.5"],
          binds: ["/home/user/source:/source:rw"],
        },
        ssh: {
          target: "user@gateway-host:22",
          command: "ssh",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // SecretRefs / المحتويات المضمّنة مدعومة أيضًا:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
        browser: {
          enabled: false,
          image: "openclaw-sandbox-browser:bookworm-slim",
          network: "openclaw-sandbox-browser",
          cdpPort: 9222,
          cdpSourceRange: "172.21.0.1/32",
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          allowHostControl: false,
          autoStart: true,
          autoStartTimeoutMs: 12000,
        },
        prune: {
          idleHours: 24,
          maxAgeDays: 7,
        },
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        allow: [
          "exec",
          "process",
          "read",
          "write",
          "edit",
          "apply_patch",
          "sessions_list",
          "sessions_history",
          "sessions_send",
          "sessions_spawn",
          "session_status",
        ],
        deny: ["browser", "canvas", "nodes", "cron", "discord", "gateway"],
      },
    },
  },
}
```

<Accordion title="تفاصيل sandbox">

**الواجهة الخلفية:**

- `docker`: بيئة Docker محلية (الافتراضية)
- `ssh`: بيئة بعيدة عامة مدعومة بـ SSH
- `openshell`: بيئة OpenShell

عند تحديد `backend: "openshell"`، تنتقل الإعدادات الخاصة بالبيئة إلى
`plugins.entries.openshell.config`.

**إعداد الواجهة الخلفية SSH:**

- `target`: هدف SSH بصيغة `user@host[:port]`
- `command`: أمر عميل SSH (الافتراضي: `ssh`)
- `workspaceRoot`: جذر بعيد مطلق يُستخدم لمساحات العمل بحسب النطاق
- `identityFile` / `certificateFile` / `knownHostsFile`: ملفات محلية موجودة تُمرَّر إلى OpenSSH
- `identityData` / `certificateData` / `knownHostsData`: محتويات مضمّنة أو SecretRefs يقوم OpenClaw بتحويلها إلى ملفات مؤقتة وقت التشغيل
- `strictHostKeyChecking` / `updateHostKeys`: مفاتيح سياسة مفتاح المضيف في OpenSSH

**أسبقية مصادقة SSH:**

- تتفوق `identityData` على `identityFile`
- تتفوق `certificateData` على `certificateFile`
- تتفوق `knownHostsData` على `knownHostsFile`
- يتم حل قيم `*Data` المدعومة بـ SecretRef من لقطة secrets النشطة وقت التشغيل قبل بدء جلسة sandbox

**سلوك الواجهة الخلفية SSH:**

- يزرع مساحة العمل البعيدة مرة واحدة بعد الإنشاء أو إعادة الإنشاء
- ثم يُبقي مساحة العمل البعيدة عبر SSH هي المرجع
- يوجّه `exec` وأدوات الملفات ومسارات الوسائط عبر SSH
- لا يزامن التغييرات البعيدة مرة أخرى إلى المضيف تلقائيًا
- لا يدعم حاويات متصفح sandbox

**الوصول إلى مساحة العمل:**

- `none`: مساحة عمل sandbox لكل نطاق ضمن `~/.openclaw/sandboxes`
- `ro`: مساحة عمل sandbox عند `/workspace`، ومساحة عمل الوكيل مركّبة للقراءة فقط عند `/agent`
- `rw`: مساحة عمل الوكيل مركّبة للقراءة/الكتابة عند `/workspace`

**النطاق:**

- `session`: حاوية + مساحة عمل لكل جلسة
- `agent`: حاوية + مساحة عمل واحدة لكل وكيل (الافتراضي)
- `shared`: حاوية ومساحة عمل مشتركتان (من دون عزل بين الجلسات)

**إعداد إضافة OpenShell:**

```json5
{
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          mode: "mirror", // mirror | remote
          from: "openclaw",
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
          gateway: "lab", // اختياري
          gatewayEndpoint: "https://lab.example", // اختياري
          policy: "strict", // معرّف سياسة OpenShell اختياري
          providers: ["openai"], // اختياري
          autoProviders: true,
          timeoutSeconds: 120,
        },
      },
    },
  },
}
```

**وضع OpenShell:**

- `mirror`: زرع البعيد من المحلي قبل exec، ثم المزامنة بعد exec؛ وتبقى مساحة العمل المحلية هي المرجع
- `remote`: زرع البعيد مرة واحدة عند إنشاء sandbox، ثم تصبح مساحة العمل البعيدة هي المرجع

في وضع `remote`، لا تتم مزامنة التعديلات المحلية على المضيف التي تُجرى خارج OpenClaw إلى sandbox تلقائيًا بعد خطوة الزرع.
تتم عملية النقل عبر SSH إلى sandbox الخاص بـ OpenShell، لكن الإضافة تمتلك دورة حياة sandbox ومزامنة mirror الاختيارية.

**`setupCommand`** يعمل مرة واحدة بعد إنشاء الحاوية (عبر `sh -lc`). ويتطلب وصول شبكة صادرة وجذرًا قابلًا للكتابة ومستخدم root.

**تستخدم الحاويات افتراضيًا `network: "none"`** — اضبطها على `"bridge"` (أو شبكة bridge مخصصة) إذا كان الوكيل يحتاج إلى وصول صادر.
يتم حظر `"host"`. ويتم حظر `"container:<id>"` افتراضيًا ما لم تضبط صراحة
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` (كسر الزجاج).

**المرفقات الواردة** تُوضَع مرحليًا في `media/inbound/*` داخل مساحة العمل النشطة.

**`docker.binds`** يركّب أدلة مضيف إضافية؛ ويتم دمج التركيبات العامة وتلك الخاصة بكل وكيل.

**المتصفح المعزول** (`sandbox.browser.enabled`): Chromium + CDP داخل حاوية. ويتم حقن عنوان noVNC في system prompt. ولا يتطلب `browser.enabled` في `openclaw.json`.
يستخدم الوصول للمراقبة عبر noVNC مصادقة VNC افتراضيًا، ويصدر OpenClaw عنوان URL مميزًا قصير العمر (بدلًا من كشف كلمة المرور في الرابط المشترك).

- `allowHostControl: false` (الافتراضي) يمنع الجلسات المعزولة من استهداف متصفح المضيف.
- تكون القيمة الافتراضية لـ `network` هي `openclaw-sandbox-browser` (شبكة bridge مخصصة). واضبطها على `bridge` فقط عندما تريد صراحة اتصال bridge عامًا.
- تقوم `cdpSourceRange` اختياريًا بتقييد دخول CDP على حافة الحاوية إلى مدى CIDR (على سبيل المثال `172.21.0.1/32`).
- تقوم `sandbox.browser.binds` بتركيب أدلة مضيف إضافية داخل حاوية متصفح sandbox فقط. وعند تعيينها (بما في ذلك `[]`)، فإنها تستبدل `docker.binds` بالنسبة إلى حاوية المتصفح.
- يتم تعريف القيم الافتراضية للتشغيل في `scripts/sandbox-browser-entrypoint.sh` ومواءمتها لمضيفي الحاويات:
  - `--remote-debugging-address=127.0.0.1`
  - `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
  - `--user-data-dir=${HOME}/.chrome`
  - `--no-first-run`
  - `--no-default-browser-check`
  - `--disable-3d-apis`
  - `--disable-gpu`
  - `--disable-software-rasterizer`
  - `--disable-dev-shm-usage`
  - `--disable-background-networking`
  - `--disable-features=TranslateUI`
  - `--disable-breakpad`
  - `--disable-crash-reporter`
  - `--renderer-process-limit=2`
  - `--no-zygote`
  - `--metrics-recording-only`
  - `--disable-extensions` (مفعّلة افتراضيًا)
  - تكون `--disable-3d-apis` و`--disable-software-rasterizer` و`--disable-gpu`
    مفعّلة افتراضيًا ويمكن تعطيلها عبر
    `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` إذا كان استخدام WebGL/3D يتطلب ذلك.
  - يعيد `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` تمكين الإضافات إذا كان سير عملك
    يعتمد عليها.
  - يمكن تغيير `--renderer-process-limit=2` عبر
    `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`؛ واضبطه إلى `0` لاستخدام
    الحد الافتراضي لعمليات Chromium.
  - بالإضافة إلى `--no-sandbox` و`--disable-setuid-sandbox` عندما تكون `noSandbox` مفعّلة.
  - تعد القيم الافتراضية خط الأساس لصورة الحاوية؛ استخدم صورة متصفح مخصصة مع
    entrypoint مخصص لتغيير القيم الافتراضية للحاوية.

</Accordion>

يقتصر Browser sandboxing و`sandbox.docker.binds` حاليًا على Docker فقط.

أنشئ الصور:

```bash
scripts/sandbox-setup.sh           # صورة sandbox الرئيسية
scripts/sandbox-browser-setup.sh   # صورة المتصفح الاختيارية
```

### `agents.list` (تجاوزات لكل وكيل)

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6", // أو { primary, fallbacks }
        thinkingDefault: "high", // تجاوز مستوى التفكير الافتراضي لكل وكيل
        reasoningDefault: "on", // تجاوز رؤية الاستدلال الافتراضية لكل وكيل
        fastModeDefault: false, // تجاوز الوضع السريع الافتراضي لكل وكيل
        params: { cacheRetention: "none" }, // تتجاوز defaults.models.params المطابقة حسب المفتاح
        skills: ["docs-search"], // تستبدل agents.defaults.skills عندما تُضبط
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
        subagents: { allowAgents: ["*"] },
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
          elevated: { enabled: true },
        },
      },
    ],
  },
}
```

- `id`: معرّف وكيل ثابت (مطلوب).
- `default`: عند ضبط أكثر من واحد، يفوز الأول (مع تسجيل تحذير). وإذا لم يُضبط أيٌّ منها، يكون أول إدخال في القائمة هو الافتراضي.
- `model`: الشكل النصي يتجاوز `primary` فقط؛ ويقوم شكل الكائن `{ primary, fallbacks }` بتجاوز الاثنين معًا (`[]` يعطّل fallbacks العامة). تظل مهام Cron التي تتجاوز `primary` فقط ترث fallbacks الافتراضية ما لم تضبط `fallbacks: []`.
- `params`: معاملات stream لكل وكيل تُدمج فوق إدخال النموذج المحدد في `agents.defaults.models`. استخدم هذا للتجاوزات الخاصة بالوكيل مثل `cacheRetention` أو `temperature` أو `maxTokens` من دون تكرار كتالوج النماذج بأكمله.
- `skills`: قائمة سماح اختيارية لـ Skills لكل وكيل. وإذا حُذفت، يرث الوكيل `agents.defaults.skills` عندما تكون معيّنة؛ وتستبدل القائمة الصريحة القيم الافتراضية بدلًا من دمجها، و`[]` تعني عدم استخدام أي Skills.
- `thinkingDefault`: مستوى التفكير الافتراضي الاختياري لكل وكيل (`off | minimal | low | medium | high | xhigh | adaptive`). ويتجاوز `agents.defaults.thinkingDefault` لهذا الوكيل عندما لا يكون هناك تجاوز لكل رسالة أو جلسة.
- `reasoningDefault`: تجاوز اختياري لكل وكيل لرؤية الاستدلال (`on | off | stream`). ويُطبّق عندما لا يكون هناك تجاوز للاستدلال لكل رسالة أو جلسة.
- `fastModeDefault`: تجاوز اختياري لكل وكيل للوضع السريع (`true | false`). ويُطبّق عندما لا يكون هناك تجاوز للوضع السريع لكل رسالة أو جلسة.
- `runtime`: واصف runtime اختياري لكل وكيل. استخدم `type: "acp"` مع الإعدادات الافتراضية لـ `runtime.acp` ‏(`agent` و`backend` و`mode` و`cwd`) عندما يجب أن يستخدم الوكيل جلسات ACP harness افتراضيًا.
- `identity.avatar`: مسار نسبي لمساحة العمل، أو عنوان URL ‏`http(s)`، أو `data:` URI.
- تستمد `identity` القيم الافتراضية: `ackReaction` من `emoji`، و`mentionPatterns` من `name`/`emoji`.
- `subagents.allowAgents`: قائمة سماح لمعرّفات الوكلاء لأداة `sessions_spawn` (`["*"]` = أي وكيل؛ الافتراضي: نفس الوكيل فقط).
- حاجز وراثة sandbox: إذا كانت جلسة الطالب داخل sandbox، ترفض `sessions_spawn` الأهداف التي ستعمل من دون sandbox.
- `subagents.requireAgentId`: عندما تكون true، تمنع استدعاءات `sessions_spawn` التي تحذف `agentId` (تفرض اختيار ملف تعريف صريح؛ الافتراضي: false).

---

## التوجيه متعدد الوكلاء

شغّل عدة وكلاء معزولين داخل بوابة واحدة. راجع [تعدد الوكلاء](/ar/concepts/multi-agent).

```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

### حقول مطابقة الارتباط

- `type` (اختياري): `route` للتوجيه العادي (وغيابه يعني route افتراضيًا)، و`acp` لارتباطات محادثات ACP الدائمة.
- `match.channel` (مطلوب)
- `match.accountId` (اختياري؛ `*` = أي حساب؛ وحذفه = الحساب الافتراضي)
- `match.peer` (اختياري؛ `{ kind: direct|group|channel, id }`)
- `match.guildId` / `match.teamId` (اختياري؛ بحسب القناة)
- `acp` (اختياري؛ فقط للإدخالات ذات `type: "acp"`): ‏`{ mode, label, cwd, backend }`

**ترتيب المطابقة الحتمي:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId` (مطابقة تامة، من دون peer/guild/team)
5. `match.accountId: "*"` (على مستوى القناة)
6. الوكيل الافتراضي

داخل كل طبقة، يفوز أول إدخال مطابق في `bindings`.

بالنسبة إلى إدخالات `type: "acp"`، يقوم OpenClaw بالحل باستخدام هوية المحادثة الدقيقة (`match.channel` + الحساب + `match.peer.id`) ولا يستخدم ترتيب طبقات route binding المذكور أعلاه.

### ملفات تعريف الوصول لكل وكيل

<Accordion title="وصول كامل (من دون sandbox)">

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="أدوات + مساحة عمل للقراءة فقط">

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "ro" },
        tools: {
          allow: [
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="من دون وصول إلى نظام الملفات (مراسلة فقط)">

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "none" },
        tools: {
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
            "gateway",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

</Accordion>

راجع [Sandbox والأدوات متعددة الوكلاء](/ar/tools/multi-agent-sandbox-tools) لمعرفة تفاصيل الأسبقية.

---

## الجلسة

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main", // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily", // daily | idle
      atHour: 4,
      idleMinutes: 60,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    parentForkMaxTokens: 100000, // تخطّي fork من الخيط الأصل فوق هذا العدد من tokens (0 للتعطيل)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // مدة أو false
      maxDiskBytes: "500mb", // اختياري، ميزانية صارمة
      highWaterBytes: "400mb", // اختياري، هدف التنظيف
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // الإلغاء التلقائي للتركيز بعد الخمول افتراضيًا بالساعات (`0` للتعطيل)
      maxAgeHours: 0, // الحد الأقصى الصارم للعمر افتراضيًا بالساعات (`0` للتعطيل)
    },
    mainKey: "main", // قديم (وقت التشغيل يستخدم دائمًا "main")
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="تفاصيل حقول الجلسة">

- **`scope`**: استراتيجية تجميع الجلسات الأساسية لسياقات الدردشة الجماعية.
  - `per-sender` (الافتراضي): يحصل كل مرسل على جلسة معزولة داخل سياق القناة.
  - `global`: يشترك جميع المشاركين في سياق القناة في جلسة واحدة (يُستخدم فقط عندما يكون المقصود سياقًا مشتركًا).
- **`dmScope`**: كيفية تجميع الرسائل الخاصة.
  - `main`: تشترك جميع الرسائل الخاصة في الجلسة الرئيسية.
  - `per-peer`: عزل حسب معرّف المرسل عبر القنوات.
  - `per-channel-peer`: عزل لكل قناة + مرسل (موصى به لصناديق الوارد متعددة المستخدمين).
  - `per-account-channel-peer`: عزل لكل حساب + قناة + مرسل (موصى به للتعدد الحسابي).
- **`identityLinks`**: تربط المعرّفات القياسية بنظراء ذوي بادئة مزوّد لمشاركة الجلسات عبر القنوات.
- **`reset`**: سياسة إعادة التعيين الأساسية. تقوم `daily` بإعادة التعيين عند `atHour` حسب التوقيت المحلي؛ وتقوم `idle` بإعادة التعيين بعد `idleMinutes`. وعند تهيئة الاثنين، يفوز أول ما تنتهي صلاحيته.
- **`resetByType`**: تجاوزات حسب النوع (`direct` و`group` و`thread`). وتُقبل `dm` القديمة كاسم بديل لـ `direct`.
- **`parentForkMaxTokens`**: الحد الأقصى لـ `totalTokens` في الجلسة الأصلية المسموح به عند إنشاء جلسة خيط forked (الافتراضي `100000`).
  - إذا كانت قيمة `totalTokens` في الأصل أعلى من هذا، يبدأ OpenClaw جلسة خيط جديدة بدلًا من وراثة سجل transcript الخاص بالأصل.
  - اضبط `0` لتعطيل هذا الحاجز والسماح دائمًا بعمل fork من الأصل.
- **`mainKey`**: حقل قديم. ويستخدم وقت التشغيل الآن دائمًا `"main"` لدلو الدردشة المباشرة الرئيسي.
- **`agentToAgent.maxPingPongTurns`**: العدد الأقصى لأدوار الرد المتبادل بين الوكلاء أثناء تبادلات وكيل إلى وكيل (عدد صحيح، المجال: `0`–`5`). وتعطّل `0` تسلسل ping-pong.
- **`sendPolicy`**: المطابقة حسب `channel` أو `chatType` (`direct|group|channel`، مع الاسم القديم `dm`) أو `keyPrefix` أو `rawKeyPrefix`. ويفوز أول deny.
- **`maintenance`**: عناصر التحكم في تنظيف مخزن الجلسة والاحتفاظ بها.
  - `mode`: تقوم `warn` بإصدار تحذيرات فقط؛ وتقوم `enforce` بتطبيق التنظيف.
  - `pruneAfter`: حد عمر الإدخالات القديمة (الافتراضي `30d`).
  - `maxEntries`: العدد الأقصى للإدخالات في `sessions.json` (الافتراضي `500`).
  - `rotateBytes`: تدوير `sessions.json` عندما يتجاوز هذا الحجم (الافتراضي `10mb`).
  - `resetArchiveRetention`: مدة الاحتفاظ بأرشيفات transcript من نوع `*.reset.<timestamp>`. وتكون افتراضيًا مساوية لـ `pruneAfter`؛ اضبط `false` للتعطيل.
  - `maxDiskBytes`: ميزانية قرص اختيارية لدليل الجلسات. في وضع `warn` تقوم بتسجيل التحذيرات؛ وفي وضع `enforce` تزيل أقدم العناصر/الجلسات أولًا.
  - `highWaterBytes`: الهدف الاختياري بعد تنظيف الميزانية. والقيمة الافتراضية هي `80%` من `maxDiskBytes`.
- **`threadBindings`**: القيم الافتراضية العامة لميزات الجلسات المرتبطة بالخيوط.
  - `enabled`: مفتاح افتراضي رئيسي (يمكن للمزوّدين تجاوزه؛ يستخدم Discord القيمة `channels.discord.threadBindings.enabled`)
  - `idleHours`: القيمة الافتراضية لإلغاء التركيز التلقائي بعد الخمول بالساعات (`0` للتعطيل؛ ويمكن للمزوّدين التجاوز)
  - `maxAgeHours`: القيمة الافتراضية للحد الأقصى الصارم للعمر بالساعات (`0` للتعطيل؛ ويمكن للمزوّدين التجاوز)

</Accordion>

---

## الرسائل

```json5
{
  messages: {
    responsePrefix: "🦞", // أو "auto"
    ackReaction: "👀",
    ackReactionScope: "group-mentions", // group-mentions | group-all | direct | all
    removeAckAfterReply: false,
    queue: {
      mode: "collect", // steer | followup | collect | steer-backlog | steer+backlog | queue | interrupt
      debounceMs: 1000,
      cap: 20,
      drop: "summarize", // old | new | summarize
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
      },
    },
    inbound: {
      debounceMs: 2000, // 0 للتعطيل
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### بادئة الرد

تجاوزات لكل قناة/حساب: `channels.<channel>.responsePrefix` و`channels.<channel>.accounts.<id>.responsePrefix`.

آلية الحل (الأكثر تحديدًا يفوز): الحساب → القناة → العام. تؤدي `""` إلى التعطيل وإيقاف التدرج. ويشتق `"auto"` القيمة `[{identity.name}]`.

**متغيرات القالب:**

| المتغير           | الوصف                 | المثال                     |
| ----------------- | --------------------- | -------------------------- |
| `{model}`         | اسم النموذج المختصر   | `claude-opus-4-6`          |
| `{modelFull}`     | معرّف النموذج الكامل  | `anthropic/claude-opus-4-6` |
| `{provider}`      | اسم المزوّد           | `anthropic`                |
| `{thinkingLevel}` | مستوى التفكير الحالي  | `high`, `low`, `off`       |
| `{identity.name}` | اسم هوية الوكيل       | (نفس `"auto"`)             |

المتغيرات غير حساسة لحالة الأحرف. ويعد `{think}` اسمًا بديلًا لـ `{thinkingLevel}`.

### تفاعل الإقرار

- يكون افتراضيًا هو `identity.emoji` الخاص بالوكيل النشط، وإلا `"👀"`. اضبط `""` للتعطيل.
- تجاوزات لكل قناة: `channels.<channel>.ackReaction` و`channels.<channel>.accounts.<id>.ackReaction`.
- ترتيب الحل: الحساب → القناة → `messages.ackReaction` → بديل الهوية.
- النطاق: `group-mentions` (الافتراضي) و`group-all` و`direct` و`all`.
- تقوم `removeAckAfterReply` بإزالة الإقرار بعد الرد على Slack وDiscord وTelegram.
- تقوم `messages.statusReactions.enabled` بتمكين تفاعلات حالة دورة الحياة على Slack وDiscord وTelegram.
  وفي Slack وDiscord، يؤدي عدم تعيينها إلى إبقاء تفاعلات الحالة مفعّلة عندما تكون تفاعلات الإقرار نشطة.
  وفي Telegram، اضبطها صراحة على `true` لتمكين تفاعلات حالة دورة الحياة.

### إلغاء الارتداد للوارد

يجمع الرسائل النصية السريعة المتتالية من المرسل نفسه في دور وكيل واحد. وتؤدي الوسائط/المرفقات إلى التفريغ الفوري. وتتجاوز أوامر التحكم آلية إلغاء الارتداد.

### TTS (تحويل النص إلى كلام)

```json5
{
  messages: {
    tts: {
      auto: "always", // off | always | inbound | tagged
      mode: "final", // final | all
      provider: "elevenlabs",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: { enabled: true },
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
      elevenlabs: {
        apiKey: "elevenlabs_api_key",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 42,
        applyTextNormalization: "auto",
        languageCode: "en",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          style: 0.0,
          useSpeakerBoost: true,
          speed: 1.0,
        },
      },
      openai: {
        apiKey: "openai_api_key",
        baseUrl: "https://api.openai.com/v1",
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
    },
  },
}
```

- يتحكم `auto` في TTS التلقائي. ويقوم `/tts off|always|inbound|tagged` بالتجاوز لكل جلسة.
- يتجاوز `summaryModel` قيمة `agents.defaults.model.primary` للملخص التلقائي.
- تكون `modelOverrides` مفعّلة افتراضيًا؛ وتكون القيمة الافتراضية لـ `modelOverrides.allowProvider` هي `false` (تفعيل اختياري).
- تعود مفاتيح API إلى `ELEVENLABS_API_KEY`/`XI_API_KEY` و`OPENAI_API_KEY`.
- تتجاوز `openai.baseUrl` نقطة نهاية OpenAI TTS. ويكون ترتيب الحل: الإعداد، ثم `OPENAI_TTS_BASE_URL`، ثم `https://api.openai.com/v1`.
- عندما تشير `openai.baseUrl` إلى نقطة نهاية غير OpenAI، يتعامل OpenClaw معها على أنها خادم TTS متوافق مع OpenAI ويخفف التحقق من النموذج/الصوت.

---

## Talk

القيم الافتراضية لوضع Talk ‏(macOS/iOS/Android).

```json5
{
  talk: {
    provider: "elevenlabs",
    providers: {
      elevenlabs: {
        voiceId: "elevenlabs_voice_id",
        voiceAliases: {
          Clawd: "EXAVITQu4vr4xnSDxMaL",
          Roger: "CwhRBWXzGAHq8TQ4Fs17",
        },
        modelId: "eleven_v3",
        outputFormat: "mp3_44100_128",
        apiKey: "elevenlabs_api_key",
      },
    },
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
  },
}
```

- يجب أن تطابق `talk.provider` مفتاحًا في `talk.providers` عند تكوين عدة مزوّدات Talk.
- مفاتيح Talk القديمة المسطحة (`talk.voiceId` و`talk.voiceAliases` و`talk.modelId` و`talk.outputFormat` و`talk.apiKey`) هي للتوافق فقط ويتم ترحيلها تلقائيًا إلى `talk.providers.<provider>`.
- تعود معرّفات الصوت إلى `ELEVENLABS_VOICE_ID` أو `SAG_VOICE_ID`.
- تقبل `providers.*.apiKey` سلاسل نصية صريحة أو كائنات SecretRef.
- لا يُستخدم البديل `ELEVENLABS_API_KEY` إلا عندما لا يكون أي مفتاح Talk API مكوَّنًا.
- تسمح `providers.*.voiceAliases` لتوجيهات Talk باستخدام أسماء ودية.
- تتحكم `silenceTimeoutMs` في مدة انتظار وضع Talk بعد صمت المستخدم قبل إرسال transcript. ويؤدي عدم تعيينها إلى الإبقاء على نافذة التوقف الافتراضية للمنصة (`700 ms على macOS وAndroid، و900 ms على iOS`).

---

## الأدوات

### ملفات تعريف الأدوات

يضبط `tools.profile` قائمة سماح أساسية قبل `tools.allow`/`tools.deny`:

تضبط عملية الإعداد المحلية الافتراضية التهيئات المحلية الجديدة على `tools.profile: "coding"` عندما لا تكون معيّنة (ويتم الحفاظ على ملفات التعريف الصريحة الموجودة).

| الملف الشخصي | يتضمن                                                                                                                        |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `minimal`    | `session_status` فقط                                                                                                          |
| `coding`     | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging`  | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                      |
| `full`       | بلا تقييد (مثل الحذف)                                                                                                         |

### مجموعات الأدوات

| المجموعة           | الأدوات                                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec`, `process`, `code_execution` (`bash` مقبول كاسم بديل لـ `exec`)                                                   |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                                                    |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory`     | `memory_search`, `memory_get`                                                                                             |
| `group:web`        | `web_search`, `x_search`, `web_fetch`                                                                                     |
| `group:ui`         | `browser`, `canvas`                                                                                                       |
| `group:automation` | `cron`, `gateway`                                                                                                         |
| `group:messaging`  | `message`                                                                                                                 |
| `group:nodes`      | `nodes`                                                                                                                   |
| `group:agents`     | `agents_list`                                                                                                             |
| `group:media`      | `image`, `image_generate`, `video_generate`, `tts`                                                                        |
| `group:openclaw`   | كل الأدوات المضمّنة (باستثناء إضافات المزوّدين)                                                                          |

### `tools.allow` / `tools.deny`

سياسة السماح/المنع العامة للأدوات (المنع يفوز). غير حساسة لحالة الأحرف، وتدعم أحرف البدل `*`. وتُطبق حتى عندما يكون Docker sandbox معطّلًا.

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

تقيّد الأدوات أكثر لمزوّدين أو نماذج محددة. الترتيب: الملف الشخصي الأساسي → ملف تعريف المزوّد → allow/deny.

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.4": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

### `tools.elevated`

يتحكم في وصول exec المرتفع خارج sandbox:

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["1234567890123", "987654321098765432"],
      },
    },
  },
}
```

- يمكن لتجاوز كل وكيل (`agents.list[].tools.elevated`) فقط أن يقيّد أكثر.
- يخزن `/elevated on|off|ask|full` الحالة لكل جلسة؛ بينما تنطبق التوجيهات المضمنة على رسالة واحدة.
- يتجاوز `exec` المرتفع العزل ويستخدم مسار الهروب المكوّن (`gateway` افتراضيًا، أو `node` عندما يكون هدف exec هو `node`).

### `tools.exec`

```json5
{
  tools: {
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
      notifyOnExitEmptySuccess: false,
      applyPatch: {
        enabled: false,
        allowModels: ["gpt-5.4"],
      },
    },
  },
}
```

### `tools.loopDetection`

فحوصات أمان حلقات الأدوات تكون **معطّلة افتراضيًا**. اضبط `enabled: true` لتفعيل الاكتشاف.
يمكن تعريف الإعدادات عمومًا في `tools.loopDetection` وتجاوزها لكل وكيل في `agents.list[].tools.loopDetection`.

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

- `historySize`: الحد الأقصى لسجل استدعاءات الأدوات المحتفظ به لتحليل الحلقات.
- `warningThreshold`: عتبة التحذير للأنماط المتكررة من دون تقدم.
- `criticalThreshold`: عتبة أعلى لحظر الحلقات الحرجة المتكررة.
- `globalCircuitBreakerThreshold`: عتبة توقف صارمة لأي تشغيل من دون تقدم.
- `detectors.genericRepeat`: التحذير من الاستدعاءات المتكررة لنفس الأداة/نفس الوسائط.
- `detectors.knownPollNoProgress`: التحذير/الحظر على أدوات poll المعروفة (`process.poll`, `command_status`, إلخ).
- `detectors.pingPong`: التحذير/الحظر على الأنماط الزوجية المتناوبة من دون تقدم.
- إذا كانت `warningThreshold >= criticalThreshold` أو `criticalThreshold >= globalCircuitBreakerThreshold`، يفشل التحقق.

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // أو BRAVE_API_KEY من البيئة
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // اختياري؛ احذفه للاكتشاف التلقائي
        maxChars: 50000,
        maxCharsCap: 50000,
        maxResponseBytes: 2000000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        maxRedirects: 3,
        readability: true,
        userAgent: "custom-ua",
      },
    },
  },
}
```

### `tools.media`

يضبط فهم الوسائط الواردة (صورة/صوت/فيديو):

```json5
{
  tools: {
    media: {
      concurrency: 2,
      asyncCompletion: {
        directSend: false, // تفعيل اختياري: أرسل مهام الموسيقى/الفيديو غير المتزامنة المكتملة مباشرة إلى القناة
      },
      audio: {
        enabled: true,
        maxBytes: 20971520,
        scope: {
          default: "deny",
          rules: [{ action: "allow", match: { chatType: "direct" } }],
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { type: "cli", command: "whisper", args: ["--model", "base", "{{MediaPath}}"] },
        ],
      },
      video: {
        enabled: true,
        maxBytes: 52428800,
        models: [{ provider: "google", model: "gemini-3-flash-preview" }],
      },
    },
  },
}
```

<Accordion title="حقول إدخال نموذج الوسائط">

**إدخال المزوّد** (`type: "provider"` أو عند الحذف):

- `provider`: معرّف مزوّد API (`openai` أو `anthropic` أو `google`/`gemini` أو `groq`، إلخ)
- `model`: تجاوز معرّف النموذج
- `profile` / `preferredProfile`: اختيار ملف التعريف في `auth-profiles.json`

**إدخال CLI** (`type: "cli"`):

- `command`: الملف التنفيذي المطلوب تشغيله
- `args`: وسائط بقوالب (تدعم `{{MediaPath}}` و`{{Prompt}}` و`{{MaxChars}}`، إلخ)

**الحقول المشتركة:**

- `capabilities`: قائمة اختيارية (`image`, `audio`, `video`). القيم الافتراضية: `openai`/`anthropic`/`minimax` → صورة، `google` → صورة+صوت+فيديو، `groq` → صوت.
- `prompt` و`maxChars` و`maxBytes` و`timeoutSeconds` و`language`: تجاوزات لكل إدخال.
- تعود الإخفاقات إلى الإدخال التالي.

تتبع مصادقة المزوّد الترتيب القياسي: `auth-profiles.json` → متغيرات البيئة → `models.providers.*.apiKey`.

**حقول الإكمال غير المتزامن:**

- `asyncCompletion.directSend`: عندما تكون `true`، تحاول مهام `music_generate`
  و`video_generate` غير المتزامنة المكتملة التسليم المباشر إلى القناة أولًا. الافتراضي: `false`
  (المسار القديم لإيقاظ جلسة الطالب/التسليم عبر النموذج).

</Accordion>

### `tools.agentToAgent`

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },
}
```

### `tools.sessions`

يتحكم في الجلسات التي يمكن استهدافها بواسطة أدوات الجلسات (`sessions_list` و`sessions_history` و`sessions_send`).

الافتراضي: `tree` (الجلسة الحالية + الجلسات التي أنشأتها، مثل الوكلاء الفرعيين).

```json5
{
  tools: {
    sessions: {
      // "self" | "tree" | "agent" | "all"
      visibility: "tree",
    },
  },
}
```

ملاحظات:

- `self`: مفتاح الجلسة الحالية فقط.
- `tree`: الجلسة الحالية + الجلسات التي أنشأتها الجلسة الحالية (الوكلاء الفرعيون).
- `agent`: أي جلسة تخص معرّف الوكيل الحالي (قد يشمل ذلك مستخدمين آخرين إذا كنت تشغّل جلسات لكل مرسل تحت نفس معرّف الوكيل).
- `all`: أي جلسة. لا يزال الاستهداف عبر الوكلاء يتطلب `tools.agentToAgent`.
- تقييد sandbox: عندما تكون الجلسة الحالية داخل sandbox وكانت `agents.defaults.sandbox.sessionToolsVisibility="spawned"`، يتم فرض الرؤية على `tree` حتى لو كانت `tools.sessions.visibility="all"`.

### `tools.sessions_spawn`

يتحكم في دعم المرفقات المضمّنة لـ `sessions_spawn`.

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // تفعيل اختياري: اضبط true للسماح بمرفقات الملفات المضمّنة
        maxTotalBytes: 5242880, // 5 MB إجماليًا عبر جميع الملفات
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 MB لكل ملف
        retainOnSessionKeep: false, // احتفظ بالمرفقات عندما cleanup="keep"
      },
    },
  },
}
```

ملاحظات:

- لا تُدعَم المرفقات إلا لـ `runtime: "subagent"`. ويرفض ACP runtime هذه المرفقات.
- تتم مادية الملفات في مساحة عمل الطفل ضمن `.openclaw/attachments/<uuid>/` مع `.manifest.json`.
- يتم تلقائيًا تنقيح محتوى المرفقات من حفظ transcript.
- يتم التحقق من مدخلات Base64 مع تدقيق صارم للأبجدية/الحشو وحاجز حجم قبل فك الترميز.
- تكون أذونات الملفات `0700` للأدلة و`0600` للملفات.
- يتبع التنظيف سياسة `cleanup`: يقوم `delete` دائمًا بإزالة المرفقات؛ بينما يحتفظ `keep` بها فقط عندما تكون `retainOnSessionKeep: true`.

### `tools.experimental`

أعلام الأدوات المضمّنة التجريبية. تكون معطّلة افتراضيًا ما لم تنطبق قاعدة تفعيل تلقائي خاصة بوقت التشغيل.

```json5
{
  tools: {
    experimental: {
      planTool: true, // تمكين update_plan التجريبية
    },
  },
}
```

ملاحظات:

- `planTool`: يفعّل الأداة المهيكلة `update_plan` لتتبع الأعمال غير التافهة متعددة الخطوات.
- الافتراضي: `false` للمزوّدين غير OpenAI. ويتم تفعيلها تلقائيًا في تشغيلات OpenAI وOpenAI Codex.
- عند التفعيل، تضيف system prompt أيضًا إرشادات استخدام حتى لا يستخدمها النموذج إلا للأعمال الجوهرية ويحتفظ بخطوة واحدة فقط في حالة `in_progress`.

### `agents.defaults.subagents`

```json5
{
  agents: {
    defaults: {
      subagents: {
        allowAgents: ["research"],
        model: "minimax/MiniMax-M2.7",
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

- `model`: النموذج الافتراضي للوكلاء الفرعيين الذين يتم إنشاؤهم. وإذا حُذف، يرث الوكلاء الفرعيون نموذج المستدعي.
- `allowAgents`: قائمة السماح الافتراضية لمعرّفات الوكلاء الهدف في `sessions_spawn` عندما لا يضبط الوكيل الطالب `subagents.allowAgents` الخاص به (`["*"]` = أي وكيل؛ الافتراضي: نفس الوكيل فقط).
- `runTimeoutSeconds`: المهلة الافتراضية (بالثواني) لـ `sessions_spawn` عندما يحذف استدعاء الأداة `runTimeoutSeconds`. وتعني `0` عدم وجود مهلة.
- سياسة الأدوات لكل وكيل فرعي: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.

---

## المزوّدون المخصصون وعناوين base URL

يستخدم OpenClaw كتالوج النماذج المضمّن. أضف مزوّدين مخصصين عبر `models.providers` في الإعداد أو `~/.openclaw/agents/<agentId>/agent/models.json`.

```json5
{
  models: {
    mode: "merge", // merge (الافتراضي) | replace
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions", // openai-completions | openai-responses | anthropic-messages | google-generative-ai
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            contextTokens: 96000,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

- استخدم `authHeader: true` + `headers` لاحتياجات المصادقة المخصصة.
- تجاوز جذر إعداد الوكيل عبر `OPENCLAW_AGENT_DIR` (أو `PI_CODING_AGENT_DIR`، وهو اسم بديل بيئي قديم).
- أسبقية الدمج لمعرّفات المزوّدات المتطابقة:
  - تفوز قيم `baseUrl` غير الفارغة في `models.json` الخاص بالوكيل.
  - تفوز قيم `apiKey` غير الفارغة الخاصة بالوكيل فقط عندما لا يكون ذلك المزوّد مُدارًا عبر SecretRef في سياق الإعداد/ملف المصادقة الحالي.
  - يتم تحديث قيم `apiKey` المُدارة عبر SecretRef من علامات المصدر (`ENV_VAR_NAME` لمراجع env، و`secretref-managed` لمراجع file/exec) بدلًا من حفظ الأسرار المحلولة.
  - يتم تحديث قيم header الخاصة بالمزوّد والمُدارة عبر SecretRef من علامات المصدر (`secretref-env:ENV_VAR_NAME` لمراجع env، و`secretref-managed` لمراجع file/exec).
  - تعود قيم `apiKey`/`baseUrl` الفارغة أو المحذوفة لدى الوكيل إلى `models.providers` في الإعداد.
  - تستخدم قيم `contextWindow`/`maxTokens` للنموذج المطابق القيمة الأعلى بين الإعداد الصريح وقيم الكتالوج الضمنية.
  - تحتفظ `contextTokens` للنموذج المطابق بسقف وقت تشغيل صريح عند توفره؛ استخدمه لتقييد السياق الفعّال من دون تغيير بيانات النموذج الأصلية.
  - استخدم `models.mode: "replace"` عندما تريد من الإعداد إعادة كتابة `models.json` بالكامل.
  - يكون حفظ العلامات معتمدًا على المصدر: تُكتب العلامات من لقطة إعداد المصدر النشطة (قبل الحل)، وليس من قيم الأسرار المحلولة وقت التشغيل.

### تفاصيل حقول المزوّد

- `models.mode`: سلوك كتالوج المزوّد (`merge` أو `replace`).
- `models.providers`: خريطة المزوّدات المخصصة مفهرسة بمعرّف المزوّد.
- `models.providers.*.api`: مكيّف الطلب (`openai-completions` أو `openai-responses` أو `anthropic-messages` أو `google-generative-ai`، إلخ).
- `models.providers.*.apiKey`: بيانات اعتماد المزوّد (يُفضَّل SecretRef/استبدال env).
- `models.providers.*.auth`: استراتيجية المصادقة (`api-key` أو `token` أو `oauth` أو `aws-sdk`).
- `models.providers.*.injectNumCtxForOpenAICompat`: بالنسبة إلى Ollama + `openai-completions`، يحقن `options.num_ctx` في الطلبات (الافتراضي: `true`).
- `models.providers.*.authHeader`: يفرض نقل بيانات الاعتماد في ترويسة `Authorization` عند الحاجة.
- `models.providers.*.baseUrl`: عنوان API الأساسي للمنبع.
- `models.providers.*.headers`: ترويسات ثابتة إضافية لتوجيه proxy/tenant.
- `models.providers.*.request`: تجاوزات النقل لطلبات HTTP الخاصة بمزوّد النموذج.
  - `request.headers`: ترويسات إضافية (تُدمج مع القيم الافتراضية للمزوّد). وتقبل القيم SecretRef.
  - `request.auth`: تجاوز استراتيجية المصادقة. الأوضاع: `"provider-default"` (استخدام المصادقة المضمّنة للمزوّد)، و`"authorization-bearer"` (مع `token`)، و`"header"` (مع `headerName` و`value` و`prefix` الاختياري).
  - `request.proxy`: تجاوز وكيل HTTP. الأوضاع: `"env-proxy"` (استخدام متغيرات `HTTP_PROXY`/`HTTPS_PROXY` من البيئة)، و`"explicit-proxy"` (مع `url`). ويقبل كلا الوضعين عنصر `tls` فرعيًا اختياريًا.
  - `request.tls`: تجاوز TLS للاتصالات المباشرة. الحقول: `ca` و`cert` و`key` و`passphrase` (تقبل جميعها SecretRef)، و`serverName` و`insecureSkipVerify`.
- `models.providers.*.models`: إدخالات كتالوج نماذج صريحة للمزوّد.
- `models.providers.*.models.*.contextWindow`: بيانات وصفية لنافذة السياق الأصلية للنموذج.
- `models.providers.*.models.*.contextTokens`: سقف سياق اختياري لوقت التشغيل. استخدمه عندما تريد ميزانية سياق فعّالة أصغر من `contextWindow` الأصلية للنموذج.
- `models.providers.*.models.*.compat.supportsDeveloperRole`: تلميح توافق اختياري. بالنسبة إلى `api: "openai-completions"` مع `baseUrl` غير فارغ وغير أصلي (المضيف ليس `api.openai.com`)، يفرض OpenClaw هذه القيمة إلى `false` وقت التشغيل. ويُبقي `baseUrl` الفارغ/المحذوف السلوك الافتراضي لـ OpenAI.
- `plugins.entries.amazon-bedrock.config.discovery`: جذر إعدادات الاكتشاف التلقائي لـ Bedrock.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: تشغيل/إيقاف الاكتشاف الضمني.
- `plugins.entries.amazon-bedrock.config.discovery.region`: منطقة AWS للاكتشاف.
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: عامل تصفية اختياري لمعرّف المزوّد لاكتشاف موجّه.
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: فترة الاقتراع لتحديث الاكتشاف.
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: نافذة السياق الاحتياطية للنماذج المكتشفة.
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: الحد الأقصى الاحتياطي لرموز الإخراج للنماذج المكتشفة.

### أمثلة للمزوّدين

<Accordion title="Cerebras (GLM 4.6 / 4.7)">

```json5
{
  env: { CEREBRAS_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: {
        primary: "cerebras/zai-glm-4.7",
        fallbacks: ["cerebras/zai-glm-4.6"],
      },
      models: {
        "cerebras/zai-glm-4.7": { alias: "GLM 4.7 (Cerebras)" },
        "cerebras/zai-glm-4.6": { alias: "GLM 4.6 (Cerebras)" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      cerebras: {
        baseUrl: "https://api.cerebras.ai/v1",
        apiKey: "${CEREBRAS_API_KEY}",
        api: "openai-completions",
        models: [
          { id: "zai-glm-4.7", name: "GLM 4.7 (Cerebras)" },
          { id: "zai-glm-4.6", name: "GLM 4.6 (Cerebras)" },
        ],
      },
    },
  },
}
```

استخدم `cerebras/zai-glm-4.7` لـ Cerebras؛ واستخدم `zai/glm-4.7` لـ Z.AI المباشر.

</Accordion>

<Accordion title="OpenCode">

```json5
{
  agents: {
    defaults: {
      model: { primary: "opencode/claude-opus-4-6" },
      models: { "opencode/claude-opus-4-6": { alias: "Opus" } },
    },
  },
}
```

اضبط `OPENCODE_API_KEY` (أو `OPENCODE_ZEN_API_KEY`). استخدم مراجع `opencode/...` لكتالوج Zen أو مراجع `opencode-go/...` لكتالوج Go. اختصار: `openclaw onboard --auth-choice opencode-zen` أو `openclaw onboard --auth-choice opencode-go`.

</Accordion>

<Accordion title="Z.AI (GLM-4.7)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "zai/glm-4.7" },
      models: { "zai/glm-4.7": {} },
    },
  },
}
```

اضبط `ZAI_API_KEY`. وتُقبل الأسماء البديلة `z.ai/*` و`z-ai/*`. اختصار: `openclaw onboard --auth-choice zai-api-key`.

- نقطة النهاية العامة: `https://api.z.ai/api/paas/v4`
- نقطة نهاية البرمجة (الافتراضية): `https://api.z.ai/api/coding/paas/v4`
- بالنسبة إلى نقطة النهاية العامة، عرّف مزوّدًا مخصصًا مع تجاوز base URL.

</Accordion>

<Accordion title="Moonshot AI (Kimi)">

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: { "moonshot/kimi-k2.5": { alias: "Kimi K2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
        ],
      },
    },
  },
}
```

بالنسبة إلى نقطة نهاية الصين: `baseUrl: "https://api.moonshot.cn/v1"` أو `openclaw onboard --auth-choice moonshot-api-key-cn`.

تعلن نقاط النهاية الأصلية لـ Moonshot عن توافق استخدام البث على النقل المشترك
`openai-completions`، ويعتمد OpenClaw الآن ذلك على
قدرات نقطة النهاية بدلًا من معرّف المزوّد المضمّن وحده.

</Accordion>

<Accordion title="Kimi Coding">

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi/kimi-code" },
      models: { "kimi/kimi-code": { alias: "Kimi Code" } },
    },
  },
}
```

متوافق مع Anthropic، ومزوّد مضمّن. اختصار: `openclaw onboard --auth-choice kimi-code-api-key`.

</Accordion>

<Accordion title="Synthetic (متوافق مع Anthropic)">

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

يجب أن يحذف base URL القيمة `/v1` (لأن عميل Anthropic يضيفها). اختصار: `openclaw onboard --auth-choice synthetic-api-key`.

</Accordion>

<Accordion title="MiniMax M2.7 (مباشر)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.7" },
      models: {
        "minimax/MiniMax-M2.7": { alias: "Minimax" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

اضبط `MINIMAX_API_KEY`. الاختصارات:
`openclaw onboard --auth-choice minimax-global-api` أو
`openclaw onboard --auth-choice minimax-cn-api`.
يستخدم كتالوج النماذج الآن M2.7 فقط افتراضيًا.
على مسار البث المتوافق مع Anthropic، يعطّل OpenClaw التفكير في MiniMax
افتراضيًا ما لم تضبط `thinking` صراحة بنفسك. يقوم `/fast on` أو
`params.fastMode: true` بإعادة كتابة `MiniMax-M2.7` إلى
`MiniMax-M2.7-highspeed`.

</Accordion>

<Accordion title="النماذج المحلية (LM Studio)">

راجع [النماذج المحلية](/ar/gateway/local-models). باختصار: شغّل نموذجًا محليًا كبيرًا عبر LM Studio Responses API على عتاد قوي؛ واحتفظ بالنماذج المستضافة مدمجة كخيار احتياطي.

</Accordion>

---

## Skills

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm", // npm | pnpm | yarn | bun
    },
    entries: {
      "image-lab": {
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // أو سلسلة نصية صريحة
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: قائمة سماح اختيارية لـ Skills المضمّنة فقط (ولا تتأثر Skills المُدارة/الخاصة بمساحة العمل).
- `load.extraDirs`: جذور Skills مشتركة إضافية (أدنى أسبقية).
- `install.preferBrew`: عندما تكون true، يفضّل مُثبّتات Homebrew عندما يكون `brew`
  متاحًا قبل الرجوع إلى أنواع مُثبّتات أخرى.
- `install.nodeManager`: تفضيل مُثبّت node لمواصفات `metadata.openclaw.install`
  (`npm` | `pnpm` | `yarn` | `bun`).
- تقوم `entries.<skillKey>.enabled: false` بتعطيل Skill حتى لو كانت مضمّنة/مثبّتة.
- `entries.<skillKey>.apiKey`: وسيلة ملائمة لـ Skills التي تعلن متغير env أساسيًا (سلسلة نصية صريحة أو كائن SecretRef).

---

## الإضافات

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: [],
    load: {
      paths: ["~/Projects/oss/voice-call-extension"],
    },
    entries: {
      "voice-call": {
        enabled: true,
        hooks: {
          allowPromptInjection: false,
        },
        config: { provider: "twilio" },
      },
    },
  },
}
```

- يتم تحميلها من `~/.openclaw/extensions`، و`<workspace>/.openclaw/extensions`، بالإضافة إلى `plugins.load.paths`.
- يَقبل الاكتشاف إضافات OpenClaw الأصلية بالإضافة إلى حزم Codex المتوافقة وحزم Claude، بما في ذلك حزم Claude ذات التخطيط الافتراضي من دون manifest.
- **تتطلب تغييرات الإعداد إعادة تشغيل البوابة.**
- `allow`: قائمة سماح اختيارية (تُحمّل الإضافات المدرجة فقط). ويفوز `deny`.
- `plugins.entries.<id>.apiKey`: حقل مناسب لمفتاح API على مستوى الإضافة (عندما تدعمه الإضافة).
- `plugins.entries.<id>.env`: خريطة متغيرات env بنطاق الإضافة.
- `plugins.entries.<id>.hooks.allowPromptInjection`: عندما تكون `false`، يقوم core بحظر `before_prompt_build` ويتجاهل الحقول التي تغيّر prompt من `before_agent_start` القديم، مع الحفاظ على `modelOverride` و`providerOverride` القديمين. وينطبق ذلك على hooks الخاصة بالإضافة الأصلية وعلى أدلة hooks التي توفرها الحزم المدعومة.
- `plugins.entries.<id>.subagent.allowModelOverride`: يثق صراحة في هذه الإضافة لطلب تجاوزات `provider` و`model` لكل تشغيل في تشغيلات الوكلاء الفرعيين الخلفية.
- `plugins.entries.<id>.subagent.allowedModels`: قائمة سماح اختيارية لأهداف `provider/model` القياسية الخاصة بتجاوزات الوكلاء الفرعيين الموثوق بها. واستخدم `"*"` فقط عندما تريد عمدًا السماح بأي نموذج.
- `plugins.entries.<id>.config`: كائن إعداد معرّف من الإضافة (ويتحقق منه مخطط إضافة OpenClaw الأصلية عند توفره).
- `plugins.entries.firecrawl.config.webFetch`: إعدادات مزوّد web-fetch الخاص بـ Firecrawl.
  - `apiKey`: مفتاح Firecrawl API (يقبل SecretRef). ويعود إلى `plugins.entries.firecrawl.config.webSearch.apiKey`، أو `tools.web.fetch.firecrawl.apiKey` القديم، أو متغير البيئة `FIRECRAWL_API_KEY`.
  - `baseUrl`: عنوان Firecrawl API الأساسي (الافتراضي: `https://api.firecrawl.dev`).
  - `onlyMainContent`: استخراج المحتوى الرئيسي فقط من الصفحات (الافتراضي: `true`).
  - `maxAgeMs`: الحد الأقصى لعمر cache بالمللي ثانية (الافتراضي: `172800000` / يومان).
  - `timeoutSeconds`: مهلة طلب scraping بالثواني (الافتراضي: `60`).
- `plugins.entries.xai.config.xSearch`: إعدادات xAI X Search ‏(بحث الويب Grok).
  - `enabled`: تمكين مزوّد X Search.
  - `model`: نموذج Grok المستخدم للبحث (مثل `"grok-4-1-fast"`).
- `plugins.entries.memory-core.config.dreaming`: إعدادات dreaming الخاصة بالذاكرة (تجريبية). راجع [Dreaming](/ar/concepts/dreaming) للمراحل والعتبات.
  - `enabled`: مفتاح dreaming الرئيسي (الافتراضي `false`).
  - `frequency`: إيقاع cron لكل دورة dreaming كاملة (`"0 3 * * *"` افتراضيًا).
  - سياسة المراحل والعتبات هي تفاصيل تنفيذية (وليست مفاتيح إعداد موجّهة للمستخدم).
- يمكن لإضافات Claude bundle المفعّلة أيضًا أن تساهم بقيم Pi الافتراضية المضمّنة من `settings.json`؛ ويطبق OpenClaw هذه القيم كإعدادات وكيل منقّحة، لا كتصحيحات إعداد OpenClaw خام.
- `plugins.slots.memory`: اختر معرّف الإضافة النشطة للذاكرة، أو `"none"` لتعطيل إضافات الذاكرة.
- `plugins.slots.contextEngine`: اختر معرّف الإضافة النشطة لمحرك السياق؛ وتكون القيمة الافتراضية `"legacy"` ما لم تثبت وتحدد محركًا آخر.
- `plugins.installs`: بيانات تثبيت مُدارة عبر CLI يستخدمها `openclaw plugins update`.
  - تتضمن `source` و`spec` و`sourcePath` و`installPath` و`version` و`resolvedName` و`resolvedVersion` و`resolvedSpec` و`integrity` و`shasum` و`resolvedAt` و`installedAt`.
  - تعامل مع `plugins.installs.*` على أنها حالة مُدارة؛ ويفضَّل استخدام أوامر CLI بدلًا من التحرير اليدوي.

راجع [الإضافات](/ar/tools/plugin).

---

## المتصفح

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    defaultProfile: "user",
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true, // وضع الشبكة الموثوقة الافتراضي
      // allowPrivateNetwork: true, // اسم بديل قديم
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: { driver: "existing-session", attachOnly: true, color: "#00AA00" },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    color: "#FF4500",
    // headless: false,
    // noSandbox: false,
    // extraArgs: [],
    // executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    // attachOnly: false,
  },
}
```

- تقوم `evaluateEnabled: false` بتعطيل `act:evaluate` و`wait --fn`.
- تكون القيمة الافتراضية لـ `ssrfPolicy.dangerouslyAllowPrivateNetwork` هي `true` عندما لا تُعيَّن (نموذج شبكة موثوقة).
- اضبط `ssrfPolicy.dangerouslyAllowPrivateNetwork: false` لتصفح صارم يقتصر على الشبكات العامة.
- في الوضع الصارم، تخضع نقاط نهاية ملفات تعريف CDP البعيدة (`profiles.*.cdpUrl`) لنفس حظر الشبكات الخاصة أثناء فحوصات reachability/discovery.
- يظل `ssrfPolicy.allowPrivateNetwork` مدعومًا كاسم بديل قديم.
- في الوضع الصارم، استخدم `ssrfPolicy.hostnameAllowlist` و`ssrfPolicy.allowedHostnames` للاستثناءات الصريحة.
- تكون الملفات الشخصية البعيدة attach-only (ويتم تعطيل start/stop/reset).
- تقبل `profiles.*.cdpUrl` القيم `http://` و`https://` و`ws://` و`wss://`.
  استخدم HTTP(S) عندما تريد أن يكتشف OpenClaw المسار `/json/version`؛ واستخدم WS(S)
  عندما يوفّر لك المزوّد عنوان DevTools WebSocket مباشرًا.
- تكون ملفات تعريف `existing-session` خاصة بالمضيف فقط وتستخدم Chrome MCP بدلًا من CDP.
- يمكن لملفات تعريف `existing-session` تعيين `userDataDir` لاستهداف ملف تعريف محدد
  لمتصفح قائم على Chromium مثل Brave أو Edge.
- تحتفظ ملفات تعريف `existing-session` بقيود مسارات Chrome MCP الحالية:
  إجراءات snapshot/ref بدلًا من استهداف محددات