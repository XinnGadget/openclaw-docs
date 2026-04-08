---
read_when:
    - تحتاج إلى دلالات إعدادات دقيقة على مستوى الحقول أو إلى القيم الافتراضية
    - تتحقق من كتل إعدادات القنوات أو النماذج أو البوابة أو الأدوات
summary: مرجع إعدادات البوابة لمفاتيح OpenClaw الأساسية والقيم الافتراضية والروابط إلى مراجع الأنظمة الفرعية المخصصة
title: مرجع الإعدادات
x-i18n:
    generated_at: "2026-04-08T07:22:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: fd5f69050455e610fc7c825d95f546a16aa867b8a9c0d692a48de36419b0afc2
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# مرجع الإعدادات

مرجع الإعدادات الأساسي لملف `~/.openclaw/openclaw.json`. للحصول على نظرة عامة موجهة بحسب المهمة، راجع [الإعدادات](/ar/gateway/configuration).

تغطي هذه الصفحة أسطح إعدادات OpenClaw الرئيسية وتضع روابط خارجية عندما يكون لدى نظام فرعي مرجع أعمق خاص به. وهي **لا** تحاول تضمين كل فهرس أوامر مملوك للقنوات/الـ plugin أو كل خيار عميق للذاكرة/QMD في صفحة واحدة.

مصدر الحقيقة في الشيفرة:

- يطبع `openclaw config schema` مخطط JSON Schema الحي المستخدم للتحقق وواجهة Control UI، مع دمج بيانات bundled/plugin/channel الوصفية عند توفرها
- يعيد `config.schema.lookup` عقدة مخطط واحدة ضمن نطاق مسار واحد لأدوات التعمق
- يتحقق `pnpm config:docs:check` / `pnpm config:docs:gen` من تجزئة خط الأساس لوثائق الإعدادات مقابل سطح المخطط الحالي

المراجع العميقة المخصصة:

- [مرجع إعدادات الذاكرة](/ar/reference/memory-config) لـ `agents.defaults.memorySearch.*` و`memory.qmd.*` و`memory.citations` وإعدادات dreaming تحت `plugins.entries.memory-core.config.dreaming`
- [أوامر Slash](/ar/tools/slash-commands) لفهرس الأوامر الحالي المضمن + bundled
- صفحات القنوات/الـ plugin المالكة لأسطح الأوامر الخاصة بكل قناة

صيغة الإعدادات هي **JSON5** (يُسمح بالتعليقات والفواصل اللاحقة). جميع الحقول اختيارية — يستخدم OpenClaw قيمًا افتراضية آمنة عند حذفها.

---

## القنوات

تبدأ كل قناة تلقائيًا عندما يوجد قسم إعداداتها (إلا إذا كان `enabled: false`).

### الوصول إلى الرسائل الخاصة والمجموعات

تدعم جميع القنوات سياسات الرسائل الخاصة وسياسات المجموعات:

| سياسة الرسائل الخاصة | السلوك |
| ------------------- | ------ |
| `pairing` (الافتراضي) | يحصل المرسلون غير المعروفين على رمز اقتران لمرة واحدة؛ ويجب على المالك الموافقة |
| `allowlist` | فقط المرسلون الموجودون في `allowFrom` (أو مخزن السماح المقترن) |
| `open` | السماح بكل الرسائل الخاصة الواردة (يتطلب `allowFrom: ["*"]`) |
| `disabled` | تجاهل كل الرسائل الخاصة الواردة |

| سياسة المجموعة | السلوك |
| --------------------- | ------------------------------------------------------ |
| `allowlist` (الافتراضي) | فقط المجموعات المطابقة لقائمة السماح المهيأة |
| `open` | تجاوز قوائم سماح المجموعات (لا يزال فرض الإشارة مطبقًا) |
| `disabled` | حظر كل رسائل المجموعات/الغرف |

<Note>
يضبط `channels.defaults.groupPolicy` القيمة الافتراضية عندما لا تكون `groupPolicy` الخاصة بالموفر مضبوطة.
تنتهي صلاحية رموز الاقتران بعد ساعة واحدة. يتم تقييد طلبات اقتران الرسائل الخاصة المعلقة عند **3 لكل قناة**.
إذا كانت كتلة الموفّر مفقودة بالكامل (`channels.<provider>` غير موجودة)، فإن سياسة المجموعة وقت التشغيل تعود إلى `allowlist` (إغلاق آمن) مع تحذير عند بدء التشغيل.
</Note>

### تجاوزات نموذج القناة

استخدم `channels.modelByChannel` لتثبيت معرفات قنوات محددة على نموذج معين. تقبل القيم `provider/model` أو الأسماء المستعارة للنماذج المهيأة. يتم تطبيق تعيين القناة عندما لا تكون الجلسة تملك بالفعل تجاوزًا للنموذج (على سبيل المثال، تم ضبطه عبر `/model`).

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

### القيم الافتراضية للقنوات ونبض الحياة

استخدم `channels.defaults` لسلوك سياسة المجموعات ونبض الحياة المشترك عبر الموفّرين:

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

- `channels.defaults.groupPolicy`: سياسة المجموعة الاحتياطية عندما لا تكون `groupPolicy` على مستوى الموفّر مضبوطة.
- `channels.defaults.contextVisibility`: وضع ظهور السياق التكميلي الافتراضي لكل القنوات. القيم: `all` (افتراضي، تضمين كل سياق الاقتباس/الخيط/السجل)، `allowlist` (تضمين السياق فقط من المرسلين الموجودين في قائمة السماح)، `allowlist_quote` (مثل allowlist لكن مع الاحتفاظ بسياق الاقتباس/الرد الصريح). تجاوز لكل قناة: `channels.<channel>.contextVisibility`.
- `channels.defaults.heartbeat.showOk`: تضمين حالات القنوات السليمة في خرج نبض الحياة.
- `channels.defaults.heartbeat.showAlerts`: تضمين الحالات المتدهورة/الخطأ في خرج نبض الحياة.
- `channels.defaults.heartbeat.useIndicator`: عرض خرج نبض الحياة بأسلوب مؤشرات مدمج.

### WhatsApp

يعمل WhatsApp عبر قناة الويب الخاصة بالبوابة (Baileys Web). ويبدأ تلقائيًا عندما توجد جلسة مرتبطة.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // العلامات الزرقاء (false في وضع الدردشة الذاتية)
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

- تستخدم الأوامر الصادرة الحساب `default` افتراضيًا إذا كان موجودًا؛ وإلا فيُستخدم أول معرّف حساب مهيأ (بعد الفرز).
- يجاوز `channels.whatsapp.defaultAccount` الاختياري اختيار الحساب الافتراضي الاحتياطي ذلك عندما يطابق معرّف حساب مهيأ.
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
      streaming: "partial", // off | partial | block | progress (الافتراضي: off؛ فعّل صراحة لتجنب حدود معدل تعديل المعاينة)
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

- رمز bot: `channels.telegram.botToken` أو `channels.telegram.tokenFile` (ملف عادي فقط؛ تُرفض الروابط الرمزية)، مع `TELEGRAM_BOT_TOKEN` كاحتياطي للحساب الافتراضي.
- يجاوز `channels.telegram.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مهيأ.
- في إعدادات الحسابات المتعددة (2+ من معرّفات الحسابات)، اضبط قيمة افتراضية صريحة (`channels.telegram.defaultAccount` أو `channels.telegram.accounts.default`) لتجنب التوجيه الاحتياطي؛ ويصدر `openclaw doctor` تحذيرًا عند غياب ذلك أو عدم صحته.
- يحظر `configWrites: false` عمليات كتابة الإعدادات التي تبدأ من Telegram (ترحيلات معرّفات supergroup و`/config set|unset`).
- تهيّئ الإدخالات `bindings[]` العليا ذات `type: "acp"` ارتباطات ACP دائمة لمواضيع المنتديات (استخدم الصيغة المعيارية `chatId:topic:topicId` في `match.peer.id`). دلالات الحقول مشتركة في [ACP Agents](/ar/tools/acp-agents#channel-specific-settings).
- تستخدم معاينات تدفق Telegram الأمرين `sendMessage` + `editMessageText` (ويعمل ذلك في المحادثات المباشرة والجماعية).
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
      streaming: "off", // off | partial | block | progress (progress تتحول إلى partial على Discord)
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

- الرمز: `channels.discord.token`، مع `DISCORD_BOT_TOKEN` كاحتياطي للحساب الافتراضي.
- تستخدم الاستدعاءات الصادرة المباشرة التي توفر `token` صريحًا لـ Discord ذلك الرمز للاستدعاء؛ بينما لا تزال إعدادات إعادة المحاولة/السياسة للحساب تأتي من الحساب المحدد في لقطة وقت التشغيل النشطة.
- يجاوز `channels.discord.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مهيأ.
- استخدم `user:<id>` (رسالة خاصة) أو `channel:<id>` (قناة guild) لأهداف التسليم؛ تُرفض المعرّفات الرقمية العارية.
- تكون Slugات الـ guild بأحرف صغيرة مع استبدال المسافات بـ `-`؛ وتستخدم مفاتيح القنوات الاسم المولد كـ slug (بدون `#`). فضّل معرّفات guild.
- تُتجاهل الرسائل التي يؤلفها bot افتراضيًا. يفعّل `allowBots: true` قبولها؛ واستخدم `allowBots: "mentions"` لقبول رسائل bots التي تذكر bot فقط (مع استمرار تصفية رسائله الذاتية).
- يسقط `channels.discord.guilds.<id>.ignoreOtherMentions` (وتجاوزات القنوات) الرسائل التي تذكر مستخدمًا أو دورًا آخر لكن لا تذكر bot (باستثناء @everyone/@here).
- يجزئ `maxLinesPerMessage` (الافتراضي 17) الرسائل الطويلة عموديًا حتى عندما تكون أقل من 2000 حرف.
- يتحكم `channels.discord.threadBindings` في التوجيه المرتبط بخيوط Discord:
  - `enabled`: تجاوز Discord لميزات الجلسة المرتبطة بالخيط (`/focus` و`/unfocus` و`/agents` و`/session idle` و`/session max-age` والتسليم/التوجيه المرتبط)
  - `idleHours`: تجاوز Discord لإزالة التركيز التلقائية بعد عدم النشاط بالساعات (`0` يعطّل)
  - `maxAgeHours`: تجاوز Discord للعمر الأقصى الصلب بالساعات (`0` يعطّل)
  - `spawnSubagentSessions`: مفتاح تفعيل اختياري لإنشاء/ربط الخيوط تلقائيًا لـ `sessions_spawn({ thread: true })`
- تهيّئ الإدخالات `bindings[]` العليا ذات `type: "acp"` ارتباطات ACP دائمة للقنوات والخيوط (استخدم معرّف القناة/الخيط في `match.peer.id`). دلالات الحقول مشتركة في [ACP Agents](/ar/tools/acp-agents#channel-specific-settings).
- يضبط `channels.discord.ui.components.accentColor` لون التمييز لحاويات مكونات Discord v2.
- يفعّل `channels.discord.voice` محادثات قنوات Discord الصوتية وتجاوزات الانضمام التلقائي + TTS الاختيارية.
- يمرر `channels.discord.voice.daveEncryption` و`channels.discord.voice.decryptionFailureTolerance` مباشرة إلى خيارات DAVE في `@discordjs/voice` (الافتراضيان `true` و`24`).
- يحاول OpenClaw أيضًا استعادة استقبال الصوت عبر مغادرة جلسة صوتية وإعادة الانضمام إليها بعد فشل متكرر في فك التشفير.
- `channels.discord.streaming` هو مفتاح وضع البث المعياري. تتم ترقية `streamMode` القديم وقيم `streaming` المنطقية تلقائيًا.
- يربط `channels.discord.autoPresence` توفر وقت التشغيل بحضور bot (سليم => online، متدهور => idle، مستنفد => dnd) ويسمح بتجاوزات نص الحالة الاختيارية.
- يعيد `channels.discord.dangerouslyAllowNameMatching` تفعيل المطابقة على الأسماء/الوسوم القابلة للتغيير (وضع توافق لكسر الزجاج).
- `channels.discord.execApprovals`: تسليم موافقات exec الأصلية في Discord وتفويض الموافقين.
  - `enabled`: `true` أو `false` أو `"auto"` (افتراضي). في الوضع التلقائي، تُفعّل موافقات exec عندما يمكن حل الموافقين من `approvers` أو `commands.ownerAllowFrom`.
  - `approvers`: معرّفات مستخدمي Discord المسموح لهم بالموافقة على طلبات exec. تعود إلى `commands.ownerAllowFrom` عند الحذف.
  - `agentFilter`: قائمة سماح اختيارية لمعرّفات الوكلاء. احذفها لتمرير الموافقات لكل الوكلاء.
  - `sessionFilter`: أنماط اختيارية لمفاتيح الجلسات (substring أو regex).
  - `target`: مكان إرسال مطالبات الموافقة. `"dm"` (افتراضي) يرسل إلى الرسائل الخاصة للموافق، `"channel"` يرسل إلى القناة الأصلية، `"both"` يرسل إلى كليهما. عندما يتضمن الهدف `"channel"`، لا تكون الأزرار قابلة للاستخدام إلا من قبل الموافقين المحلولين.
  - `cleanupAfterResolve`: عندما تكون `true`، تحذف رسائل الموافقة الخاصة بعد الموافقة أو الرفض أو انتهاء المهلة.

**أوضاع إشعارات التفاعل:** `off` (لا شيء)، `own` (رسائل bot، الافتراضي)، `all` (كل الرسائل)، `allowlist` (من `guilds.<id>.users` على كل الرسائل).

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

- JSON حساب الخدمة: مضمن (`serviceAccount`) أو قائم على ملف (`serviceAccountFile`).
- يدعم أيضًا SecretRef لحساب الخدمة (`serviceAccountRef`).
- المتغيرات البيئية الاحتياطية: `GOOGLE_CHAT_SERVICE_ACCOUNT` أو `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- استخدم `spaces/<spaceId>` أو `users/<userId>` لأهداف التسليم.
- يعيد `channels.googlechat.dangerouslyAllowNameMatching` تفعيل مطابقة هوية البريد الإلكتروني القابلة للتغيير (وضع توافق لكسر الزجاج).

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
      streaming: {
        mode: "partial", // off | partial | block | progress
        nativeTransport: true, // استخدم API البث الأصلية لـ Slack عندما mode=partial
      },
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

- يتطلب **وضع Socket** كلاً من `botToken` و`appToken` (`SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` كاحتياطي متغيرات بيئة للحساب الافتراضي).
- يتطلب **وضع HTTP** `botToken` بالإضافة إلى `signingSecret` (على الجذر أو لكل حساب).
- تقبل `botToken` و`appToken` و`signingSecret` و`userToken` سلاسل نصية
  صريحة أو كائنات SecretRef.
- تكشف لقطات حساب Slack عن حقول مصدر/حالة لكل اعتماد مثل
  `botTokenSource` و`botTokenStatus` و`appTokenStatus` و، في وضع HTTP،
  `signingSecretStatus`. تعني `configured_unavailable` أن الحساب
  مهيأ عبر SecretRef لكن مسار الأمر/وقت التشغيل الحالي تعذر عليه
  حل قيمة السر.
- يحظر `configWrites: false` عمليات كتابة الإعدادات التي تبدأ من Slack.
- يجاوز `channels.slack.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مهيأ.
- `channels.slack.streaming.mode` هو مفتاح وضع بث Slack المعياري. ويتحكم `channels.slack.streaming.nativeTransport` في نقل البث الأصلي لـ Slack. تتم ترقية `streamMode` القديم وقيم `streaming` المنطقية و`nativeStreaming` تلقائيًا.
- استخدم `user:<id>` (رسالة خاصة) أو `channel:<id>` لأهداف التسليم.

**أوضاع إشعارات التفاعل:** `off` و`own` (افتراضي) و`all` و`allowlist` (من `reactionAllowlist`).

**عزل جلسات الخيوط:** يكون `thread.historyScope` لكل خيط (افتراضي) أو مشتركًا عبر القناة. ينسخ `thread.inheritParent` نص القناة الأصلية إلى الخيوط الجديدة.

- يتطلب البث الأصلي في Slack بالإضافة إلى حالة الخيط "is typing..." بأسلوب المساعد في Slack هدف رد داخل خيط. تبقى الرسائل الخاصة ذات المستوى الأعلى خارج الخيوط افتراضيًا، لذا تستخدم `typingReaction` أو التسليم العادي بدلًا من المعاينة بأسلوب الخيط.
- تضيف `typingReaction` تفاعلًا مؤقتًا إلى رسالة Slack الواردة أثناء تشغيل الرد، ثم تزيله عند الاكتمال. استخدم shortcode لرمز Slack مثل `"hourglass_flowing_sand"`.
- `channels.slack.execApprovals`: تسليم موافقات exec الأصلية في Slack وتفويض الموافقين. المخطط نفسه كما في Discord: `enabled` (`true`/`false`/`"auto"`) و`approvers` (معرّفات مستخدمي Slack) و`agentFilter` و`sessionFilter` و`target` (`"dm"` أو `"channel"` أو `"both"`).

| مجموعة الإجراءات | الافتراضي | ملاحظات |
| ------------ | ------- | ---------------------- |
| reactions    | مفعّل | التفاعل + سرد التفاعلات |
| messages     | مفعّل | قراءة/إرسال/تحرير/حذف |
| pins         | مفعّل | تثبيت/إزالة تثبيت/سرد |
| memberInfo   | مفعّل | معلومات العضو |
| emojiList    | مفعّل | قائمة emoji المخصصة |

### Mattermost

يأتي Mattermost كـ plugin: `openclaw plugins install @openclaw/mattermost`.

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
        // URL صريح اختياري لعمليات النشر عبر reverse-proxy/العامة
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

أوضاع الدردشة: `oncall` (الرد عند @-mention، الافتراضي)، `onmessage` (كل رسالة)، `onchar` (الرسائل التي تبدأ ببادئة تشغيل).

عند تفعيل أوامر Mattermost الأصلية:

- يجب أن تكون `commands.callbackPath` مسارًا (مثل `/api/channels/mattermost/command`) وليس URL كاملًا.
- يجب أن تحل `commands.callbackUrl` إلى نقطة نهاية بوابة OpenClaw وأن تكون قابلة للوصول من خادم Mattermost.
- تتم مصادقة ردود slash الأصلية بواسطة الرموز الخاصة بكل أمر
  التي يعيدها Mattermost أثناء تسجيل slash command. إذا فشل التسجيل أو لم
  تُفعَّل أي أوامر، يرفض OpenClaw الردود برسالة
  `Unauthorized: invalid command token.`
- بالنسبة لمضيفي callback الخاصين/الداخليين/tailnet، قد يتطلب Mattermost
  أن تتضمن `ServiceSettings.AllowedUntrustedInternalConnections` المضيف/المجال الخاص بالـ callback.
  استخدم قيم المضيف/المجال، وليس URLs كاملة.
- `channels.mattermost.configWrites`: السماح أو المنع لعمليات كتابة الإعدادات التي تبدأ من Mattermost.
- `channels.mattermost.requireMention`: يتطلب `@mention` قبل الرد في القنوات.
- `channels.mattermost.groups.<channelId>.requireMention`: تجاوز فرض الإشارة لكل قناة (`"*"` للافتراضي).
- يجاوز `channels.mattermost.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مهيأ.

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

**أوضاع إشعارات التفاعل:** `off` و`own` (افتراضي) و`all` و`allowlist` (من `reactionAllowlist`).

- `channels.signal.account`: يثبت بدء تشغيل القناة على هوية حساب Signal محددة.
- `channels.signal.configWrites`: السماح أو المنع لعمليات كتابة الإعدادات التي تبدأ من Signal.
- يجاوز `channels.signal.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مهيأ.

### BlueBubbles

يعد BlueBubbles المسار الموصى به لـ iMessage (مدعومًا عبر plugin، ويُضبط تحت `channels.bluebubbles`).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl وpassword وwebhookPath وعناصر تحكم المجموعات والإجراءات المتقدمة:
      // راجع /channels/bluebubbles
    },
  },
}
```

- مسارات المفاتيح الأساسية المغطاة هنا: `channels.bluebubbles` و`channels.bluebubbles.dmPolicy`.
- يجاوز `channels.bluebubbles.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مهيأ.
- يمكن لإدخالات `bindings[]` العليا ذات `type: "acp"` ربط محادثات BlueBubbles بجلسات ACP دائمة. استخدم handle في BlueBubbles أو سلسلة الهدف (`chat_id:*` أو `chat_guid:*` أو `chat_identifier:*`) في `match.peer.id`. دلالات الحقول المشتركة: [ACP Agents](/ar/tools/acp-agents#channel-specific-settings).
- إعدادات قناة BlueBubbles الكاملة موثقة في [BlueBubbles](/ar/channels/bluebubbles).

### iMessage

يشغّل OpenClaw الأمر `imsg rpc` (JSON-RPC عبر stdio). لا حاجة إلى daemon أو منفذ.

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

- يجاوز `channels.imessage.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مهيأ.

- يتطلب Full Disk Access إلى قاعدة بيانات Messages.
- فضّل أهداف `chat_id:<id>`. استخدم `imsg chats --limit 20` لسرد المحادثات.
- يمكن أن يشير `cliPath` إلى غلاف SSH؛ واضبط `remoteHost` (`host` أو `user@host`) لجلب المرفقات عبر SCP.
- تقيد `attachmentRoots` و`remoteAttachmentRoots` مسارات المرفقات الواردة (الافتراضي: `/Users/*/Library/Messages/Attachments`).
- يستخدم SCP تحققًا صارمًا من مفتاح المضيف، لذا تأكد من وجود مفتاح مضيف relay بالفعل في `~/.ssh/known_hosts`.
- `channels.imessage.configWrites`: السماح أو المنع لعمليات كتابة الإعدادات التي تبدأ من iMessage.
- يمكن لإدخالات `bindings[]` العليا ذات `type: "acp"` ربط محادثات iMessage بجلسات ACP دائمة. استخدم handle مطبعًا أو هدف محادثة صريحًا (`chat_id:*` أو `chat_guid:*` أو `chat_identifier:*`) في `match.peer.id`. دلالات الحقول المشتركة: [ACP Agents](/ar/tools/acp-agents#channel-specific-settings).

<Accordion title="مثال على غلاف SSH لـ iMessage">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix مدعوم عبر extension ويُضبط تحت `channels.matrix`.

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
- يوجّه `channels.matrix.proxy` حركة HTTP الخاصة بـ Matrix عبر وكيل HTTP(S) صريح. ويمكن للحسابات المسماة تجاوزه عبر `channels.matrix.accounts.<id>.proxy`.
- يسمح `channels.matrix.network.dangerouslyAllowPrivateNetwork` بخوادم homeserver الخاصة/الداخلية. إن `proxy` وهذا التفعيل الشبكي تحكمان مستقلان.
- يحدد `channels.matrix.defaultAccount` الحساب المفضل في إعدادات الحسابات المتعددة.
- يكون `channels.matrix.autoJoin` افتراضيًا `off`، لذا تُتجاهل الغرف المدعو إليها ودعوات الرسائل الخاصة الجديدة حتى تضبط `autoJoin: "allowlist"` مع `autoJoinAllowlist` أو `autoJoin: "always"`.
- `channels.matrix.execApprovals`: تسليم موافقات exec الأصلية في Matrix وتفويض الموافقين.
  - `enabled`: `true` أو `false` أو `"auto"` (افتراضي). في الوضع التلقائي، تُفعّل موافقات exec عندما يمكن حل الموافقين من `approvers` أو `commands.ownerAllowFrom`.
  - `approvers`: معرّفات مستخدمي Matrix (مثل `@owner:example.org`) المسموح لهم بالموافقة على طلبات exec.
  - `agentFilter`: قائمة سماح اختيارية لمعرّفات الوكلاء. احذفها لتمرير الموافقات لكل الوكلاء.
  - `sessionFilter`: أنماط اختيارية لمفاتيح الجلسات (substring أو regex).
  - `target`: مكان إرسال مطالبات الموافقة. `"dm"` (افتراضي) أو `"channel"` (الغرفة الأصلية) أو `"both"`.
  - تجاوزات لكل حساب: `channels.matrix.accounts.<id>.execApprovals`.
- يتحكم `channels.matrix.dm.sessionScope` في كيفية تجميع الرسائل الخاصة لـ Matrix إلى جلسات: `per-user` (افتراضي) يشارك حسب النظير الموجه إليه، بينما `per-room` يعزل كل غرفة رسالة خاصة.
- تستخدم مجسات حالة Matrix وعمليات البحث في الدليل الحي سياسة الوكيل نفسها المستخدمة في حركة وقت التشغيل.
- إعدادات Matrix الكاملة وقواعد الاستهداف وأمثلة الإعداد موثقة في [Matrix](/ar/channels/matrix).

### Microsoft Teams

Microsoft Teams مدعوم عبر extension ويُضبط تحت `channels.msteams`.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId وappPassword وtenantId وwebhook وسياسات الفريق/القناة:
      // راجع /channels/msteams
    },
  },
}
```

- مسارات المفاتيح الأساسية المغطاة هنا: `channels.msteams` و`channels.msteams.configWrites`.
- إعدادات Teams الكاملة (بيانات الاعتماد وwebhook وسياسة الرسائل الخاصة/المجموعات وتجاوزات كل فريق/كل قناة) موثقة في [Microsoft Teams](/ar/channels/msteams).

### IRC

IRC مدعوم عبر extension ويُضبط تحت `channels.irc`.

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
- يجاوز `channels.irc.defaultAccount` الاختياري اختيار الحساب الافتراضي عندما يطابق معرّف حساب مهيأ.
- إعدادات قناة IRC الكاملة (المضيف/المنفذ/TLS/القنوات/قوائم السماح/فرض الإشارة) موثقة في [IRC](/ar/channels/irc).

### متعدد الحسابات (كل القنوات)

شغّل عدة حسابات لكل قناة (لكل منها `accountId` خاص بها):

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

- يُستخدم `default` عندما يتم حذف `accountId` (CLI + التوجيه).
- تنطبق رموز المتغيرات البيئية فقط على الحساب **default**.
- تنطبق إعدادات القناة الأساسية على كل الحسابات ما لم تُتجاوز لكل حساب.
- استخدم `bindings[].match.accountId` لتوجيه كل حساب إلى وكيل مختلف.
- إذا أضفت حسابًا غير افتراضي عبر `openclaw channels add` (أو onboarding للقناة) بينما لا تزال على إعداد قناة أحادي الحساب في المستوى الأعلى، يقوم OpenClaw أولًا بترقية القيم العليا الخاصة بالحساب الأحادي إلى خريطة حسابات القناة بحيث يستمر الحساب الأصلي بالعمل. تنقل معظم القنوات هذه القيم إلى `channels.<channel>.accounts.default`؛ ويمكن لـ Matrix الاحتفاظ بهدف مسمى/افتراضي موجود ومطابق بدلًا من ذلك.
- تستمر ارتباطات القنوات الموجودة فقط (بدون `accountId`) في مطابقة الحساب الافتراضي؛ وتبقى الارتباطات ذات النطاق الحسابي اختيارية.
- يقوم `openclaw doctor --fix` أيضًا بإصلاح الأشكال المختلطة بنقل القيم العليا الخاصة بالحساب الأحادي إلى الحساب المرقى المختار لتلك القناة. تستخدم معظم القنوات `accounts.default`؛ ويمكن لـ Matrix الاحتفاظ بهدف مسمى/افتراضي موجود ومطابق بدلًا من ذلك.

### قنوات extension أخرى

تُضبط كثير من قنوات extension على شكل `channels.<id>` وتُوثق في صفحات القنوات المخصصة لها (مثل Feishu وMatrix وLINE وNostr وZalo وNextcloud Talk وSynology Chat وTwitch).
راجع فهرس القنوات الكامل: [القنوات](/ar/channels).

### فرض الإشارة في محادثات المجموعات

تكون رسائل المجموعات افتراضيًا **تتطلب إشارة** (إشارة وصفية أو أنماط regex آمنة). ينطبق ذلك على محادثات مجموعات WhatsApp وTelegram وDiscord وGoogle Chat وiMessage.

**أنواع الإشارات:**

- **الإشارات الوصفية**: إشارات @-mentions الأصلية في المنصة. تُتجاهل في وضع الدردشة الذاتية في WhatsApp.
- **أنماط النص**: أنماط regex آمنة في `agents.list[].groupChat.mentionPatterns`. يتم تجاهل الأنماط غير الصالحة والتكرار المتداخل غير الآمن.
- يُفرض شرط الإشارة فقط عندما يكون الاكتشاف ممكنًا (إشارات أصلية أو نمط واحد على الأقل).

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

آلية الحل: تجاوز لكل رسالة خاصة → افتراضي الموفّر → بلا حد (الاحتفاظ بكل شيء).

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
    nativeSkills: "auto", // تسجيل أوامر Skills الأصلية عندما تكون مدعومة
    text: true, // تحليل /commands في رسائل الدردشة
    bash: false, // السماح بـ ! (اسم بديل: /bash)
    bashForegroundMs: 2000,
    config: false, // السماح بـ /config
    mcp: false, // السماح بـ /mcp
    plugins: false, // السماح بـ /plugins
    debug: false, // السماح بـ /debug
    restart: true, // السماح بـ /restart + أداة إعادة تشغيل البوابة
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw", // raw | hash
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="تفاصيل الأوامر">

- تضبط هذه الكتلة أسطح الأوامر. لفهرس الأوامر الحالي المضمن + bundled، راجع [أوامر Slash](/ar/tools/slash-commands).
- هذه الصفحة هي **مرجع لمفاتيح الإعدادات**، وليست فهرس الأوامر الكامل. الأوامر المملوكة للقنوات/الـ plugin مثل QQ Bot `/bot-ping` و`/bot-help` و`/bot-logs`، وLINE `/card`، وdevice-pair `/pair`، وmemory `/dreaming`، وphone-control `/phone`، وTalk `/voice` موثقة في صفحات القنوات/الـ plugin إضافة إلى [أوامر Slash](/ar/tools/slash-commands).
- يجب أن تكون أوامر النص رسائل **مستقلة** تبدأ بـ `/`.
- يفعّل `native: "auto"` الأوامر الأصلية لـ Discord/Telegram، ويترك Slack معطّلًا.
- يفعّل `nativeSkills: "auto"` أوامر Skills الأصلية لـ Discord/Telegram، ويترك Slack معطّلًا.
- تجاوز لكل قناة: `channels.discord.commands.native` (قيمة منطقية أو `"auto"`). يزيل `false` الأوامر المسجلة سابقًا.
- تجاوز تسجيل Skills الأصلية لكل قناة عبر `channels.<provider>.commands.nativeSkills`.
- يضيف `channels.telegram.customCommands` إدخالات إضافية إلى قائمة bot في Telegram.
- يفعّل `bash: true` الأمر `! <cmd>` لصدفة المضيف. ويتطلب `tools.elevated.enabled` وأن يكون المرسل ضمن `tools.elevated.allowFrom.<channel>`.
- يفعّل `config: true` الأمر `/config` (قراءة/كتابة `openclaw.json`). وبالنسبة لعملاء `chat.send` في البوابة، تتطلب كتابات `/config set|unset` الدائمة أيضًا `operator.admin`؛ بينما يبقى `/config show` للقراءة فقط متاحًا لعملاء operator ذوي نطاق الكتابة العادي.
- يفعّل `mcp: true` الأمر `/mcp` لإعدادات خادم MCP المُدار من OpenClaw تحت `mcp.servers`.
- يفعّل `plugins: true` الأمر `/plugins` لاكتشاف الـ plugin وتثبيتها وتمكينها/تعطيلها.
- يتحكم `channels.<provider>.configWrites` بطفرات الإعدادات لكل قناة (الافتراضي: true).
- بالنسبة للقنوات متعددة الحسابات، يتحكم أيضًا `channels.<provider>.accounts.<id>.configWrites` بالكتابات التي تستهدف ذلك الحساب (مثل `/allowlist --config --account <id>` أو `/config set channels.<provider>.accounts.<id>...`).
- يعطل `restart: false` الأمر `/restart` وإجراءات أداة إعادة تشغيل البوابة. الافتراضي: `true`.
- `ownerAllowFrom` هي قائمة السماح الصريحة للمالك للأوامر/الأدوات الخاصة بالمالك فقط. وهي منفصلة عن `allowFrom`.
- يقوم `ownerDisplay: "hash"` بتجزئة معرّفات المالك في system prompt. اضبط `ownerDisplaySecret` للتحكم في التجزئة.
- `allowFrom` خاص بكل موفّر. عند ضبطه، يصبح **مصدر التفويض الوحيد** (وتُتجاهل قوائم سماح القنوات/الاقتران و`useAccessGroups`).
- يسمح `useAccessGroups: false` للأوامر بتجاوز سياسات مجموعات الوصول عندما لا يكون `allowFrom` مضبوطًا.
- خريطة وثائق الأوامر:
  - الفهرس المضمن + bundled: [أوامر Slash](/ar/tools/slash-commands)
  - أسطح الأوامر الخاصة بالقنوات: [القنوات](/ar/channels)
  - أوامر QQ Bot: [QQ Bot](/ar/channels/qqbot)
  - أوامر الاقتران: [الاقتران](/ar/channels/pairing)
  - أمر بطاقة LINE: [LINE](/ar/channels/line)
  - dreaming الخاصة بالذاكرة: [Dreaming](/ar/concepts/dreaming)

</Accordion>

---

## القيم الافتراضية للوكلاء

### `agents.defaults.workspace`

الافتراضي: `~/.openclaw/workspace`.

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

جذر المستودع الاختياري الذي يُعرض في سطر Runtime ضمن system prompt. إذا لم يُضبط، يكتشفه OpenClaw تلقائيًا عبر الصعود من مساحة العمل.

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
      { id: "writer" }, // يرث github وweather
      { id: "docs", skills: ["docs-search"] }, // يستبدل القيم الافتراضية
      { id: "locked-down", skills: [] }, // بلا Skills
    ],
  },
}
```

- احذف `agents.defaults.skills` للحصول على Skills غير مقيدة افتراضيًا.
- احذف `agents.list[].skills` لوراثة القيم الافتراضية.
- اضبط `agents.list[].skills: []` لعدم وجود Skills.
- تكون القائمة غير الفارغة في `agents.list[].skills` هي المجموعة النهائية لذلك الوكيل؛
  ولا تُدمج مع القيم الافتراضية.

### `agents.defaults.skipBootstrap`

يعطل الإنشاء التلقائي لملفات bootstrap لمساحة العمل (`AGENTS.md` و`SOUL.md` و`TOOLS.md` و`IDENTITY.md` و`USER.md` و`HEARTBEAT.md` و`BOOTSTRAP.md`).

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

يتحكم في وقت حقن ملفات bootstrap لمساحة العمل داخل system prompt. الافتراضي: `"always"`.

- `"continuation-skip"`: تتجاوز الأدوار الآمنة المتواصلة (بعد اكتمال رد المساعد) إعادة حقن bootstrap لمساحة العمل، مما يقلل حجم prompt. تعيد تشغيلات نبض الحياة وإعادات المحاولة بعد الضغط بناء السياق رغم ذلك.

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

الحد الأقصى للأحرف لكل ملف bootstrap في مساحة العمل قبل الاقتطاع. الافتراضي: `20000`.

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

الحد الأقصى لإجمالي الأحرف المحقونة عبر جميع ملفات bootstrap لمساحة العمل. الافتراضي: `150000`.

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

يتحكم في نص التحذير المرئي للوكيل عندما يُقتطع سياق bootstrap.
الافتراضي: `"once"`.

- `"off"`: لا يحقن نص تحذير أبدًا في system prompt.
- `"once"`: يحقن التحذير مرة واحدة لكل توقيع اقتطاع فريد (موصى به).
- `"always"`: يحقن التحذير في كل تشغيل عندما يوجد اقتطاع.

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

الحد الأقصى لحجم البكسل لأطول ضلع في الصورة في كتل الصور الخاصة بالنص/الأدوات قبل استدعاءات الموفّر.
الافتراضي: `1200`.

القيم الأقل تقلل عادة استخدام vision-token وحجم حمولة الطلب في الحالات الكثيفة لصور الشاشة.
أما القيم الأعلى فتحافظ على تفاصيل بصرية أكثر.

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

المنطقة الزمنية لسياق system prompt (وليست طوابع الرسائل الزمنية). تعود إلى المنطقة الزمنية للمضيف.

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

صيغة الوقت في system prompt. الافتراضي: `auto` (تفضيل نظام التشغيل).

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
      params: { cacheRetention: "long" }, // معلمات الموفّر الافتراضية العامة
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

- `model`: يقبل إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - تضبط صيغة السلسلة النموذج الأساسي فقط.
  - تضبط صيغة الكائن النموذج الأساسي بالإضافة إلى نماذج الفشل الاحتياطية المرتبة.
- `imageModel`: يقبل إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يُستخدم بواسطة مسار أداة `image` بوصفه إعداد نموذج الرؤية الخاص بها.
  - ويستخدم أيضًا كتوجيه احتياطي عندما لا يستطيع النموذج المحدد/الافتراضي قبول إدخال الصور.
- `imageGenerationModel`: يقبل إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يُستخدم بواسطة قابلية توليد الصور المشتركة وأي سطح أداة/Plugin مستقبلي يولد صورًا.
  - القيم النموذجية: `google/gemini-3.1-flash-image-preview` لتوليد صور Gemini الأصلي، أو `fal/fal-ai/flux/dev` لـ fal، أو `openai/gpt-image-1` لـ OpenAI Images.
  - إذا اخترت موفّرًا/نموذجًا مباشرة، فقم بتهيئة المصادقة/مفتاح API المطابق للموفّر أيضًا (مثل `GEMINI_API_KEY` أو `GOOGLE_API_KEY` لـ `google/*`، و`OPENAI_API_KEY` لـ `openai/*`، و`FAL_KEY` لـ `fal/*`).
  - إذا حُذف، يمكن لـ `image_generate` رغم ذلك استنتاج افتراضي لموفّر مدعوم بالمصادقة. إذ يحاول أولًا موفّر الإعداد الافتراضي الحالي، ثم بقية موفّري توليد الصور المسجلين بترتيب معرّف الموفّر.
- `musicGenerationModel`: يقبل إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يُستخدم بواسطة قابلية توليد الموسيقى المشتركة وأداة `music_generate` المضمنة.
  - القيم النموذجية: `google/lyria-3-clip-preview` أو `google/lyria-3-pro-preview` أو `minimax/music-2.5+`.
  - إذا حُذف، يمكن لـ `music_generate` رغم ذلك استنتاج افتراضي لموفّر مدعوم بالمصادقة. إذ يحاول أولًا موفّر الإعداد الافتراضي الحالي، ثم بقية موفّري توليد الموسيقى المسجلين بترتيب معرّف الموفّر.
  - إذا اخترت موفّرًا/نموذجًا مباشرة، فقم بتهيئة المصادقة/مفتاح API المطابق للموفّر أيضًا.
- `videoGenerationModel`: يقبل إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يُستخدم بواسطة قابلية توليد الفيديو المشتركة وأداة `video_generate` المضمنة.
  - القيم النموذجية: `qwen/wan2.6-t2v` أو `qwen/wan2.6-i2v` أو `qwen/wan2.6-r2v` أو `qwen/wan2.6-r2v-flash` أو `qwen/wan2.7-r2v`.
  - إذا حُذف، يمكن لـ `video_generate` رغم ذلك استنتاج افتراضي لموفّر مدعوم بالمصادقة. إذ يحاول أولًا موفّر الإعداد الافتراضي الحالي، ثم بقية موفّري توليد الفيديو المسجلين بترتيب معرّف الموفّر.
  - إذا اخترت موفّرًا/نموذجًا مباشرة، فقم بتهيئة المصادقة/مفتاح API المطابق للموفّر أيضًا.
  - يدعم موفّر توليد الفيديو Qwen المضمن حاليًا حتى 1 فيديو ناتج، و1 صورة إدخال، و4 فيديوهات إدخال، ومدة 10 ثوانٍ، وخيارات `size` و`aspectRatio` و`resolution` و`audio` و`watermark` على مستوى الموفّر.
- `pdfModel`: يقبل إما سلسلة (`"provider/model"`) أو كائنًا (`{ primary, fallbacks }`).
  - يُستخدم بواسطة أداة `pdf` لتوجيه النموذج.
  - إذا حُذف، تعود أداة PDF إلى `imageModel`، ثم إلى النموذج المحلول للجلسة/الافتراضي.
- `pdfMaxBytesMb`: حد حجم PDF الافتراضي لأداة `pdf` عندما لا يُمرر `maxBytesMb` وقت الاستدعاء.
- `pdfMaxPages`: الحد الأقصى الافتراضي للصفحات التي تؤخذ في الاعتبار بواسطة وضع الاستخراج الاحتياطي في أداة `pdf`.
- `verboseDefault`: مستوى verbose الافتراضي للوكلاء. القيم: `"off"` و`"on"` و`"full"`. الافتراضي: `"off"`.
- `elevatedDefault`: مستوى الخرج elevated الافتراضي للوكلاء. القيم: `"off"` و`"on"` و`"ask"` و`"full"`. الافتراضي: `"on"`.
- `model.primary`: الصيغة `provider/model` (مثل `openai/gpt-5.4`). إذا حذفت الموفّر، يحاول OpenClaw أولًا الاسم المستعار، ثم مطابقة موفّر مهيأ فريد لذلك المعرّف الدقيق للنموذج، وبعد ذلك فقط يعود إلى الموفّر الافتراضي المهيأ (سلوك توافق قديم، لذا فضّل الصيغة الصريحة `provider/model`). إذا لم يعد ذلك الموفّر يعرّض النموذج الافتراضي المهيأ، يعود OpenClaw إلى أول موفّر/نموذج مهيأ بدلًا من إظهار افتراضي قديم لموفّر تمت إزالته.
- `models`: فهرس النماذج المهيأ وقائمة السماح لـ `/model`. يمكن أن يتضمن كل إدخال `alias` (اختصار) و`params` (خاصة بالموفّر، مثل `temperature` و`maxTokens` و`cacheRetention` و`context1m`).
- `params`: معلمات الموفّر الافتراضية العامة المطبقة على كل النماذج. تضبط في `agents.defaults.params` (مثل `{ cacheRetention: "long" }`).
- أسبقية دمج `params` (في الإعدادات): يتم تجاوز `agents.defaults.params` (الأساس العام) بواسطة `agents.defaults.models["provider/model"].params` (لكل نموذج)، ثم تتجاوز `agents.list[].params` (للوكيل المطابق) حسب المفتاح. راجع [Prompt Caching](/ar/reference/prompt-caching) للتفاصيل.
- تحفظ أدوات كتابة الإعدادات التي تعدل هذه الحقول (مثل `/models set` و`/models set-image` وأوامر الإضافة/الإزالة الاحتياطية) صيغة الكائن المعيارية وتحافظ على قوائم fallback الحالية متى أمكن.
- `maxConcurrent`: الحد الأقصى لتشغيلات الوكلاء المتوازية عبر الجلسات (مع بقاء كل جلسة متسلسلة). الافتراضي: 4.

**اختصارات الأسماء المستعارة المضمنة** (تنطبق فقط عندما يكون النموذج ضمن `agents.defaults.models`):

| الاسم المستعار | النموذج |
| ------------------- | -------------------------------------- |
| `opus`              | `anthropic/claude-opus-4-6`            |
| `sonnet`            | `anthropic/claude-sonnet-4-6`          |
| `gpt`               | `openai/gpt-5.4`                       |
| `gpt-mini`          | `openai/gpt-5.4-mini`                  |
| `gpt-nano`          | `openai/gpt-5.4-nano`                  |
| `gemini`            | `google/gemini-3.1-pro-preview`        |
| `gemini-flash`      | `google/gemini-3-flash-preview`        |
| `gemini-flash-lite` | `google/gemini-3.1-flash-lite-preview` |

تتغلب الأسماء المستعارة التي تهيئها أنت دائمًا على القيم الافتراضية.

تفعّل نماذج Z.AI GLM-4.x وضع thinking تلقائيًا ما لم تضبط `--thinking off` أو تعرّف `agents.defaults.models["zai/<model>"].params.thinking` بنفسك.
وتفعّل نماذج Z.AI القيمة `tool_stream` افتراضيًا لبث استدعاءات الأدوات. اضبط `agents.defaults.models["zai/<model>"].params.tool_stream` على `false` لتعطيله.
وتفترض نماذج Anthropic Claude 4.6 الوضع `adaptive` للتفكير عندما لا يكون هناك مستوى تفكير صريح مضبوط.

### `agents.defaults.cliBackends`

خلفيات CLI اختيارية لتشغيلات fallback النصية فقط (من دون استدعاءات أدوات). مفيدة كنسخة احتياطية عندما تفشل موفّرات API.

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

- تعد خلفيات CLI موجهة للنص أولًا؛ وتكون الأدوات دائمًا معطلة.
- تُدعم الجلسات عندما يكون `sessionArg` مضبوطًا.
- يُدعم تمرير الصور عندما يقبل `imageArg` مسارات الملفات.

### `agents.defaults.systemPromptOverride`

استبدل system prompt الكامل الذي يجمعه OpenClaw بسلسلة ثابتة. يضبط على المستوى الافتراضي (`agents.defaults.systemPromptOverride`) أو لكل وكيل (`agents.list[].systemPromptOverride`). تتقدم القيم الخاصة بكل وكيل؛ ويتم تجاهل القيمة الفارغة أو المكونة من مسافات فقط. هذا مفيد لتجارب prompt محكومة.

```json5
{
  agents: {
    defaults: {
      systemPromptOverride: "You are a helpful assistant.",
    },
  },
}
```

### `agents.defaults.heartbeat`

تشغيلات نبض حياة دورية.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m يعطّل
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        includeSystemPromptSection: true, // الافتراضي: true؛ false يحذف قسم Heartbeat من system prompt
        lightContext: false, // الافتراضي: false؛ true يحتفظ فقط بـ HEARTBEAT.md من ملفات bootstrap لمساحة العمل
        isolatedSession: false, // الافتراضي: false؛ true يشغّل كل نبض حياة في جلسة جديدة (بلا سجل محادثة)
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

- `every`: سلسلة مدة (ms/s/m/h). الافتراضي: `30m` (مصادقة API-key) أو `1h` (مصادقة OAuth). اضبطها على `0m` للتعطيل.
- `includeSystemPromptSection`: عند `false`، يحذف قسم Heartbeat من system prompt ويتجاوز حقن `HEARTBEAT.md` ضمن سياق bootstrap. الافتراضي: `true`.
- `suppressToolErrorWarnings`: عند `true`، يقمع حمولات تحذير أخطاء الأدوات أثناء تشغيلات نبض الحياة.
- `directPolicy`: سياسة التسليم المباشر/الرسائل الخاصة. تسمح `allow` (الافتراضي) بالتسليم المباشر إلى الهدف. ويقمع `block` التسليم المباشر ويصدر `reason=dm-blocked`.
- `lightContext`: عند `true`، تستخدم تشغيلات نبض الحياة سياق bootstrap خفيفًا وتحتفظ فقط بـ `HEARTBEAT.md` من ملفات bootstrap لمساحة العمل.
- `isolatedSession`: عند `true`، يعمل كل نبض حياة في جلسة جديدة من دون أي سجل محادثة سابق. نمط العزل نفسه مثل `sessionTarget: "isolated"` في cron. يقلل تكلفة الرموز لكل نبض حياة من نحو 100 ألف إلى 2-5 آلاف رمز.
- لكل وكيل: اضبط `agents.list[].heartbeat`. عندما يعرّف أي وكيل `heartbeat`، **فإن هؤلاء الوكلاء فقط** يشغلون نبض الحياة.
- تشغّل عمليات نبض الحياة أدوار الوكيل كاملة — وكلما قصرت الفواصل زاد استهلاك الرموز.

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        provider: "my-provider", // معرّف plugin موفّر compaction مسجل (اختياري)
        timeoutSeconds: 900,
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "Preserve deployment IDs, ticket IDs, and host:port pairs exactly.", // يُستخدم عندما identifierPolicy=custom
        postCompactionSections: ["Session Startup", "Red Lines"], // [] يعطّل إعادة الحقن
        model: "openrouter/anthropic/claude-sonnet-4-6", // تجاوز نموذج اختياري خاص بالـ compaction فقط
        notifyUser: true, // أرسل إشعارًا موجزًا عندما يبدأ compaction (الافتراضي: false)
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

- `mode`: `default` أو `safeguard` (تلخيص مقسم إلى أجزاء للسجلات الطويلة). راجع [Compaction](/ar/concepts/compaction).
- `provider`: معرّف plugin موفّر compaction مسجل. عند ضبطه، يُستدعى `summarize()` الخاص بالموفّر بدلًا من التلخيص المضمن عبر LLM. ويعود إلى المضمن عند الفشل. يؤدي ضبط موفّر إلى فرض `mode: "safeguard"`. راجع [Compaction](/ar/concepts/compaction).
- `timeoutSeconds`: الحد الأقصى للثواني المسموح بها لعملية compaction واحدة قبل أن يجهضها OpenClaw. الافتراضي: `900`.
- `identifierPolicy`: `strict` (افتراضي) أو `off` أو `custom`. يضيف `strict` إرشادات مضمنة للحفاظ على المعرفات المعتمة أثناء تلخيص compaction.
- `identifierInstructions`: نص اختياري مخصص للحفاظ على المعرفات يُستخدم عندما `identifierPolicy=custom`.
- `postCompactionSections`: أسماء أقسام H2/H3 اختيارية من AGENTS.md لإعادة حقنها بعد compaction. الافتراضي `["Session Startup", "Red Lines"]`؛ اضبط `[]` للتعطيل. عند حذفها أو ضبطها صراحة على هذا الزوج الافتراضي، تُقبل أيضًا العناوين الأقدم `Every Session`/`Safety` كاحتياطي قديم.
- `model`: تجاوز اختياري `provider/model-id` لتلخيص compaction فقط. استخدمه عندما يجب أن تحتفظ الجلسة الرئيسية بنموذج معين بينما يجب أن تعمل ملخصات compaction على نموذج آخر؛ وعند حذفه يستخدم compaction النموذج الأساسي للجلسة.
- `notifyUser`: عندما تكون `true`، يرسل إشعارًا موجزًا إلى المستخدم عندما يبدأ compaction (مثل "Compacting context..."). وهو معطل افتراضيًا للحفاظ على صمت compaction.
- `memoryFlush`: دور وكيل صامت قبل compaction التلقائي لتخزين الذكريات الدائمة. يُتجاوز عندما تكون مساحة العمل للقراءة فقط.

### `agents.defaults.contextPruning`

يقتطع **نتائج الأدوات القديمة** من السياق الموجود في الذاكرة قبل إرسالها إلى LLM. ولا **يعدّل** سجل الجلسة على القرص.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // المدة (ms/s/m/h)، الوحدة الافتراضية: دقائق
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

- يفعّل `mode: "cache-ttl"` تمريرات الاقتطاع.
- يتحكم `ttl` في عدد مرات السماح بتشغيل الاقتطاع مرة أخرى (بعد آخر لمسة للكاش).
- يقتطع أولًا نتائج الأدوات كبيرة الحجم جزئيًا، ثم يمسح النتائج الأقدم كليًا عند الحاجة.

**الاقتطاع الجزئي** يحتفظ بالبداية + النهاية ويُدخل `...` في المنتصف.

**المسح الكامل** يستبدل نتيجة الأداة بالكامل بالنص البديل.

ملاحظات:

- لا يتم اقتطاع/مسح كتل الصور أبدًا.
- النسب تعتمد على الأحرف (تقريبية)، وليست على عدد الرموز بدقة.
- إذا وُجدت رسائل مساعد أقل من `keepLastAssistants`، يتم تجاوز الاقتطاع.

</Accordion>

راجع [اقتطاع الجلسات](/ar/concepts/session-pruning) لتفاصيل السلوك.

### البث على شكل كتل

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

- تتطلب القنوات غير Telegram تفعيلًا صريحًا لـ `*.blockStreaming: true` لتفعيل الردود على شكل كتل.
- تجاوزات القنوات: `channels.<channel>.blockStreamingCoalesce` (ومتغيرات كل حساب). تستخدم Signal/Slack/Discord/Google Chat افتراضيًا `minChars: 1500`.
- `humanDelay`: توقف عشوائي بين ردود الكتل. `natural` = 800–2500ms. تجاوز لكل وكيل: `agents.list[].humanDelay`.

راجع [Streaming](/ar/concepts/streaming) للسلوك وتفاصيل التقسيم.

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

- القيم الافتراضية: `instant` للمحادثات المباشرة/الإشارات، و`message` لمحادثات المجموعات غير المشار فيها.
- تجاوزات لكل جلسة: `session.typingMode` و`session.typingIntervalSeconds`.

راجع [مؤشرات الكتابة](/ar/concepts/typing-indicators).

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

وضع sandboxing اختياري للوكيل المضمن. راجع [Sandboxing](/ar/gateway/sandboxing) للدليل الكامل.

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
          // SecretRefs / المحتويات المضمنة مدعومة أيضًا:
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

<Accordion title="تفاصيل Sandbox">

**الخلفية:**

- `docker`: بيئة Docker محلية (افتراضي)
- `ssh`: بيئة وقت تشغيل بعيدة عامة مدعومة بـ SSH
- `openshell`: بيئة وقت تشغيل OpenShell

عند اختيار `backend: "openshell"`، تنتقل الإعدادات الخاصة بوقت التشغيل إلى
`plugins.entries.openshell.config`.

**إعداد خلفية SSH:**

- `target`: هدف SSH بصيغة `user@host[:port]`
- `command`: أمر عميل SSH (الافتراضي: `ssh`)
- `workspaceRoot`: جذر بعيد مطلق يُستخدم لمساحات العمل لكل نطاق
- `identityFile` / `certificateFile` / `knownHostsFile`: ملفات محلية موجودة تُمرر إلى OpenSSH
- `identityData` / `certificateData` / `knownHostsData`: محتويات مضمنة أو SecretRefs يقوم OpenClaw بتحويلها إلى ملفات مؤقتة وقت التشغيل
- `strictHostKeyChecking` / `updateHostKeys`: مقابض سياسة مفاتيح المضيف في OpenSSH

**أسبقية مصادقة SSH:**

- يتغلب `identityData` على `identityFile`
- يتغلب `certificateData` على `certificateFile`
- يتغلب `knownHostsData` على `knownHostsFile`
- تُحل قيم `*Data` المدعومة بـ SecretRef من لقطة secrets النشطة قبل بدء جلسة sandbox

**سلوك خلفية SSH:**

- يزرع مساحة العمل البعيدة مرة واحدة بعد الإنشاء أو إعادة الإنشاء
- ثم يحافظ على مساحة عمل SSH البعيدة بوصفها المعيارية
- يوجّه `exec` وأدوات الملفات ومسارات الوسائط عبر SSH
- لا يزامن التغييرات البعيدة تلقائيًا إلى المضيف
- لا يدعم حاويات browser داخل sandbox

**وصول مساحة العمل:**

- `none`: مساحة عمل sandbox لكل نطاق تحت `~/.openclaw/sandboxes`
- `ro`: مساحة عمل sandbox عند `/workspace`، مع تركيب مساحة عمل الوكيل للقراءة فقط عند `/agent`
- `rw`: تُركب مساحة عمل الوكيل للقراءة/الكتابة عند `/workspace`

**النطاق:**

- `session`: حاوية + مساحة عمل لكل جلسة
- `agent`: حاوية + مساحة عمل واحدة لكل وكيل (افتراضي)
- `shared`: حاوية ومساحة عمل مشتركتان (بدون عزل بين الجلسات)

**إعداد Plugin OpenShell:**

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

- `mirror`: زرع البعيد من المحلي قبل exec، ثم المزامنة العكسية بعد exec؛ تبقى مساحة العمل المحلية هي المعيارية
- `remote`: زرع البعيد مرة واحدة عند إنشاء sandbox، ثم تبقى مساحة العمل البعيدة هي المعيارية

في وضع `remote`، لا تُزامن التعديلات المحلية على المضيف التي تتم خارج OpenClaw تلقائيًا إلى sandbox بعد خطوة الزرع.
ويكون النقل عبر SSH إلى sandbox الخاص بـ OpenShell، لكن الـ plugin يملك دورة حياة sandbox والمزامنة الانعكاسية الاختيارية.

**`setupCommand`** يعمل مرة واحدة بعد إنشاء الحاوية (عبر `sh -lc`). ويحتاج إلى خروج شبكة، وجذر قابل للكتابة، ومستخدم root.

**تكون الحاويات افتراضيًا مع `network: "none"`** — اضبطها إلى `"bridge"` (أو شبكة bridge مخصصة) إذا كان الوكيل يحتاج إلى وصول صادر.
يُحظر `"host"`. كما يُحظر `"container:<id>"` افتراضيًا ما لم تضبط صراحة
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` (خيار كسر زجاج).

**المرفقات الواردة** تُجهّز في `media/inbound/*` داخل مساحة العمل النشطة.

**`docker.binds`** يركب أدلة مضيف إضافية؛ ويتم دمج التركيبات العامة وتركيبات كل وكيل.

**browser داخل sandbox** (`sandbox.browser.enabled`): Chromium + CDP داخل حاوية. يُحقن عنوان noVNC في system prompt. لا يتطلب `browser.enabled` في `openclaw.json`.
يستخدم وصول noVNC للمراقبة مصادقة VNC افتراضيًا ويُخرج OpenClaw عنوان URL برمز قصير العمر (بدلًا من كشف كلمة المرور في URL المشترك).

- `allowHostControl: false` (افتراضي) يحظر على الجلسات داخل sandbox استهداف browser المضيف.
- تكون `network` افتراضيًا `openclaw-sandbox-browser` (شبكة bridge مخصصة). اضبطها إلى `bridge` فقط عندما تريد صراحة اتصال bridge عامًا.
- يقيّد `cdpSourceRange` اختياريًا دخول CDP عند حافة الحاوية إلى نطاق CIDR (مثل `172.21.0.1/32`).
- يقوم `sandbox.browser.binds` بتركيب أدلة مضيف إضافية داخل حاوية browser في sandbox فقط. عند ضبطه (بما في ذلك `[]`) فإنه يستبدل `docker.binds` لحاوية browser.
- تُعرَّف افتراضيات الإطلاق في `scripts/sandbox-browser-entrypoint.sh` وتُضبط لمضيفي الحاويات:
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
  - `--disable-extensions` (مفعّل افتراضيًا)
  - تكون `--disable-3d-apis` و`--disable-software-rasterizer` و`--disable-gpu`
    مفعّلة افتراضيًا ويمكن تعطيلها عبر
    `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` إذا كانت WebGL/الاستخدامات ثلاثية الأبعاد تتطلب ذلك.
  - يعيد `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` تفعيل الإضافات إذا كان سير عملك
    يعتمد عليها.
  - يمكن تغيير `--renderer-process-limit=2` عبر
    `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`؛ اضبط `0` لاستخدام الحد
    الافتراضي لعمليات Chromium.
  - إضافة إلى `--no-sandbox` و`--disable-setuid-sandbox` عندما يكون `noSandbox` مفعّلًا.
  - القيم الافتراضية هي خط الأساس لصورة الحاوية؛ استخدم صورة browser مخصصة مع entrypoint مخصص لتغيير افتراضيات الحاوية.

</Accordion>

تتوفر حاليًا sandboxing لـ browser و`sandbox.docker.binds` فقط مع Docker.

ابنِ الصور:

```bash
scripts/sandbox-setup.sh           # صورة sandbox الرئيسية
scripts/sandbox-browser-setup.sh   # صورة browser الاختيارية
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
        reasoningDefault: "on", // تجاوز رؤية reasoning الافتراضي لكل وكيل
        fastModeDefault: false, // تجاوز fast mode الافتراضي لكل وكيل
        params: { cacheRetention: "none" }, // يتجاوز matching defaults.models params حسب المفتاح
        skills: ["docs-search"], // يستبدل agents.defaults.skills عند ضبطه
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
- `default`: عندما تُضبط عدة قيم، يفوز الأول (مع تسجيل تحذير). إذا لم يُضبط أي منها، تكون أول قائمة هي الافتراضية.
- `model`: تتجاوز صيغة السلسلة `primary` فقط؛ وتتجاوز صيغة الكائن `{ primary, fallbacks }` كليهما (`[]` يعطل fallback العامة). تستمر وظائف cron التي تتجاوز `primary` فقط في وراثة fallback الافتراضية ما لم تضبط `fallbacks: []`.
- `params`: معلمات بث لكل وكيل تُدمج فوق إدخال النموذج المحدد في `agents.defaults.models`. استخدم هذا لتجاوزات خاصة بالوكيل مثل `cacheRetention` أو `temperature` أو `maxTokens` من دون تكرار فهرس النماذج الكامل.
- `skills`: قائمة سماح اختيارية لـ Skills لكل وكيل. إذا حُذفت، يرث الوكيل `agents.defaults.skills` عند ضبطها؛ والقائمة الصريحة تستبدل القيم الافتراضية بدل دمجها، و`[]` تعني بلا Skills.
- `thinkingDefault`: مستوى التفكير الافتراضي الاختياري لكل وكيل (`off | minimal | low | medium | high | xhigh | adaptive`). يتجاوز `agents.defaults.thinkingDefault` لهذا الوكيل عندما لا يكون هناك تجاوز لكل رسالة أو لكل جلسة.
- `reasoningDefault`: ظهور reasoning الافتراضي الاختياري لكل وكيل (`on | off | stream`). يطبق عندما لا يكون هناك تجاوز لكل رسالة أو لكل جلسة.
- `fastModeDefault`: افتراضي fast mode الاختياري لكل وكيل (`true | false`). يطبق عندما لا يكون هناك تجاوز لكل رسالة أو لكل جلسة.
- `runtime`: واصف وقت تشغيل اختياري لكل وكيل. استخدم `type: "acp"` مع القيم الافتراضية لـ `runtime.acp` (`agent` و`backend` و`mode` و`cwd`) عندما يجب أن يفترض الوكيل جلسات ACP harness.
- `identity.avatar`: مسار نسبي لمساحة العمل، أو URL من نوع `http(s)`، أو URI من نوع `data:`.
- تستمد `identity` قيمًا افتراضية: `ackReaction` من `emoji`، و`mentionPatterns` من `name`/`emoji`.
- `subagents.allowAgents`: قائمة سماح لمعرّفات الوكلاء لـ `sessions_spawn` (`["*"]` = أي وكيل؛ الافتراضي: الوكيل نفسه فقط).
- حاجز وراثة sandbox: إذا كانت جلسة الطالب داخل sandbox، يرفض `sessions_spawn` الأهداف التي ستعمل خارج sandbox.
- `subagents.requireAgentId`: عندما تكون true، يحظر استدعاءات `sessions_spawn` التي تحذف `agentId` (يفرض اختيار ملف شخصي صريح؛ الافتراضي: false).

---

## التوجيه متعدد الوكلاء

شغّل عدة وكلاء معزولين داخل بوابة واحدة. راجع [متعدد الوكلاء](/ar/concepts/multi-agent).

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

- `type` (اختياري): `route` للتوجيه العادي (غياب النوع يعني route افتراضيًا)، و`acp` لارتباطات محادثة ACP الدائمة.
- `match.channel` (مطلوب)
- `match.accountId` (اختياري؛ `*` = أي حساب؛ الحذف = الحساب الافتراضي)
- `match.peer` (اختياري؛ `{ kind: direct|group|channel, id }`)
- `match.guildId` / `match.teamId` (اختياري؛ خاص بالقناة)
- `acp` (اختياري؛ فقط لـ `type: "acp"`): `{ mode, label, cwd, backend }`

**ترتيب المطابقة الحتمي:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId` (مطابقة دقيقة، من دون peer/guild/team)
5. `match.accountId: "*"` (على مستوى القناة)
6. الوكيل الافتراضي

داخل كل طبقة، يفوز أول إدخال مطابق في `bindings`.

بالنسبة لإدخالات `type: "acp"`، يحل OpenClaw عبر هوية المحادثة الدقيقة (`match.channel` + الحساب + `match.peer.id`) ولا يستخدم ترتيب طبقات route binding أعلاه.

### ملفات وصول لكل وكيل

<Accordion title="وصول كامل (بدون sandbox)">

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

<Accordion title="بدون وصول إلى نظام الملفات (مراسلة فقط)">

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

راجع [Sandbox & Tools لمتعدد الوكلاء](/ar/tools/multi-agent-sandbox-tools) لتفاصيل الأسبقية.

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
    parentForkMaxTokens: 100000, // تجاوز تفرع خيط الأصل فوق هذا العدد من الرموز (0 يعطّل)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // مدة أو false
      maxDiskBytes: "500mb", // ميزانية صلبة اختيارية
      highWaterBytes: "400mb", // هدف تنظيف اختياري
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // الافتراضي لإزالة التركيز التلقائي بعد عدم النشاط بالساعات (`0` يعطّل)
      maxAgeHours: 0, // الافتراضي للعمر الأقصى الصلب بالساعات (`0` يعطّل)
    },
    mainKey: "main", // قديم (يستخدم وقت التشغيل دائمًا "main")
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="تفاصيل حقول الجلسة">

- **`scope`**: استراتيجية تجميع الجلسات الأساسية لسياقات محادثات المجموعات.
  - `per-sender` (افتراضي): يحصل كل مرسل على جلسة معزولة ضمن سياق قناة.
  - `global`: يشترك كل المشاركين في سياق القناة في جلسة واحدة (استخدمه فقط عندما يكون السياق المشترك مقصودًا).
- **`dmScope`**: كيفية تجميع الرسائل الخاصة.
  - `main`: تشترك كل الرسائل الخاصة في الجلسة الرئيسية.
  - `per-peer`: عزل حسب معرّف المرسل عبر القنوات.
  - `per-channel-peer`: عزل حسب القناة + المرسل (موصى به لصناديق الوارد متعددة المستخدمين).
  - `per-account-channel-peer`: عزل حسب الحساب + القناة + المرسل (موصى به لتعدد الحسابات).
- **`identityLinks`**: خريطة للمعرّفات المعيارية إلى نظائر مسبوقة بموفّر لمشاركة الجلسات عبر القنوات.
- **`reset`**: سياسة إعادة الضبط الأساسية. يعيد `daily` الضبط عند `atHour` حسب الوقت المحلي؛ ويعيد `idle` الضبط بعد `idleMinutes`. عند ضبط كليهما، يفوز الذي تنتهي صلاحيته أولًا.
- **`resetByType`**: تجاوزات لكل نوع (`direct` و`group` و`thread`). يُقبل `dm` القديم كاسم بديل لـ `direct`.
- **`parentForkMaxTokens`**: الحد الأقصى المسموح به لقيمة `totalTokens` في جلسة الأصل عند إنشاء جلسة خيط متفرعة (الافتراضي `100000`).
  - إذا كانت `totalTokens` في الأصل أعلى من هذه القيمة، يبدأ OpenClaw جلسة خيط جديدة بدلًا من وراثة سجل نص الأصل.
  - اضبط `0` لتعطيل هذا الحاجز والسماح دائمًا بالتفرع من الأصل.
- **`mainKey`**: حقل قديم. يستخدم وقت التشغيل الآن دائمًا `"main"` لحاوية الدردشة المباشرة الرئيسية.
- **`agentToAgent.maxPingPongTurns`**: الحد الأقصى لأدوار الرد المتبادلة بين الوكلاء أثناء تبادلات agent-to-agent (عدد صحيح، النطاق: `0`–`5`). يؤدي `0` إلى تعطيل سلسلة ping-pong.
- **`sendPolicy`**: المطابقة حسب `channel` أو `chatType` (`direct|group|channel`، مع الاسم البديل القديم `dm`) أو `keyPrefix` أو `rawKeyPrefix`. ويفوز أول منع.
- **`maintenance`**: عناصر تحكم تنظيف مخزن الجلسات + الاحتفاظ.
  - `mode`: يخرج `warn` تحذيرات فقط؛ بينما يطبق `enforce` التنظيف.
  - `pruneAfter`: حد العمر لإدخالات الركود (الافتراضي `30d`).
  - `maxEntries`: العدد الأقصى للإدخالات في `sessions.json` (الافتراضي `500`).
  - `rotateBytes`: تدوير `sessions.json` عندما يتجاوز هذا الحجم (الافتراضي `10mb`).
  - `resetArchiveRetention`: الاحتفاظ بأرشيفات النص `*.reset.<timestamp>`. يفترض افتراضيًا قيمة `pruneAfter`؛ واضبط `false` للتعطيل.
  - `maxDiskBytes`: ميزانية قرص اختيارية لدليل الجلسات. في وضع `warn` يسجل تحذيرات؛ وفي وضع `enforce` يزيل أقدم العناصر/الجلسات أولًا.
  - `highWaterBytes`: هدف اختياري بعد التنظيف وفق الميزانية. الافتراضي `80%` من `maxDiskBytes`.
- **`threadBindings`**: القيم الافتراضية العامة لميزات الجلسة المرتبطة بالخيط.
  - `enabled`: مفتاح افتراضي رئيسي (يمكن للموفّرين تجاوزه؛ ويستخدم Discord القيمة `channels.discord.threadBindings.enabled`)
  - `idleHours`: الافتراضي العام لإزالة التركيز التلقائية بسبب عدم النشاط بالساعات (`0` يعطّل؛ ويمكن للموفّرين التجاوز)
  - `maxAgeHours`: الافتراضي العام للعمر الأقصى الصلب بالساعات (`0` يعطّل؛ ويمكن للموفّرين التجاوز)

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
      debounceMs: 2000, // 0 يعطّل
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

آلية الحل (الأكثر تحديدًا يفوز): الحساب → القناة → العام. تؤدي `""` إلى التعطيل وإيقاف التسلسل. وتشتق `"auto"` القيمة `[{identity.name}]`.

**متغيرات القالب:**

| المتغير | الوصف | المثال |
| ----------------- | ---------------------- | --------------------------- |
| `{model}`         | اسم النموذج القصير | `claude-opus-4-6` |
| `{modelFull}`     | معرّف النموذج الكامل | `anthropic/claude-opus-4-6` |
| `{provider}`      | اسم الموفّر | `anthropic` |
| `{thinkingLevel}` | مستوى التفكير الحالي | `high`، `low`، `off` |
| `{identity.name}` | اسم هوية الوكيل | (مثل `"auto"`) |

المتغيرات غير حساسة لحالة الأحرف. ويعد `{think}` اسمًا بديلًا لـ `{thinkingLevel}`.

### تفاعل التأكيد

- القيمة الافتراضية هي `identity.emoji` للوكيل النشط، وإلا `"👀"`. اضبط `""` للتعطيل.
- تجاوزات لكل قناة: `channels.<channel>.ackReaction` و`channels.<channel>.accounts.<id>.ackReaction`.
- ترتيب الحل: الحساب → القناة → `messages.ackReaction` → احتياطي الهوية.
- النطاق: `group-mentions` (افتراضي)، أو `group-all`، أو `direct`، أو `all`.
- تزيل `removeAckAfterReply` تفاعل التأكيد بعد الرد في Slack وDiscord وTelegram.
- يفعّل `messages.statusReactions.enabled` تفاعلات الحالة الدورية على Slack وDiscord وTelegram.
  في Slack وDiscord، يؤدي عدم ضبطه إلى إبقاء تفاعلات الحالة مفعّلة عندما تكون تفاعلات التأكيد نشطة.
  في Telegram، اضبطه صراحة على `true` لتفعيل تفاعلات الحالة الدورية.

### إلغاء ارتداد الوارد

يجمع الرسائل النصية السريعة من المرسل نفسه في دور وكيل واحد. ويتم تفريغ الوسائط/المرفقات فورًا. وتتجاوز أوامر التحكم إلغاء الارتداد.

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

- يتحكم `auto` في وضع TTS التلقائي الافتراضي: `off` أو `always` أو `inbound` أو `tagged`. ويمكن لـ `/tts on|off` تجاوز التفضيلات المحلية، ويعرض `/tts status` الحالة الفعلية.
- يتجاوز `summaryModel` القيمة `agents.defaults.model.primary` للملخص التلقائي.
- يكون `modelOverrides` مفعّلًا افتراضيًا؛ وتكون `modelOverrides.allowProvider` افتراضيًا `false` (تفعيل اختياري).
- تعود مفاتيح API إلى `ELEVENLABS_API_KEY`/`XI_API_KEY` و`OPENAI_API_KEY`.
- يتجاوز `openai.baseUrl` نقطة نهاية OpenAI TTS. ترتيب الحل هو: الإعدادات، ثم `OPENAI_TTS_BASE_URL`، ثم `https://api.openai.com/v1`.
- عندما يشير `openai.baseUrl` إلى نقطة نهاية غير OpenAI، يعامله OpenClaw بوصفه خادم TTS متوافقًا مع OpenAI ويخفف التحقق من النموذج/الصوت.

---

## Talk

القيم الافتراضية لوضع Talk (macOS/iOS/Android).

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

- يجب أن يطابق `talk.provider` مفتاحًا في `talk.providers` عندما تكون عدة موفّرات Talk مهيأة.
- مفاتيح Talk القديمة المسطحة (`talk.voiceId` و`talk.voiceAliases` و`talk.modelId` و`talk.outputFormat` و`talk.apiKey`) للتوافق فقط ويتم ترحيلها تلقائيًا إلى `talk.providers.<provider>`.
- تعود معرّفات الأصوات إلى `ELEVENLABS_VOICE_ID` أو `SAG_VOICE_ID`.
- يقبل `providers.*.apiKey` سلاسل نصية صريحة أو كائنات SecretRef.
- يطبق احتياطي `ELEVENLABS_API_KEY` فقط عندما لا يكون هناك مفتاح Talk API مهيأ.
- يتيح `providers.*.voiceAliases` لتوجيهات Talk استخدام أسماء ودية.
- يتحكم `silenceTimeoutMs` في مدة انتظار وضع Talk بعد صمت المستخدم قبل إرسال النص المفرغ. وعند عدم ضبطه يُحتفظ بنافذة التوقف الافتراضية للمنصة (`700 ms على macOS وAndroid، و900 ms على iOS`).

---

## الأدوات

### ملفات تعريف الأدوات

يضبط `tools.profile` قائمة سماح أساسية قبل `tools.allow`/`tools.deny`:

تضبط إعدادات onboarding المحلية القيم الجديدة افتراضيًا على `tools.profile: "coding"` عندما تكون غير مضبوطة (مع الحفاظ على الملفات الشخصية الصريحة الحالية).

| الملف الشخصي | يتضمن |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | `session_status` فقط |
| `coding`    | `group:fs` و`group:runtime` و`group:web` و`group:sessions` و`group:memory` و`cron` و`image` و`image_generate` و`video_generate` |
| `messaging` | `group:messaging` و`sessions_list` و`sessions_history` و`sessions_send` و`session_status` |
| `full`      | بدون تقييد (مثل غير المضبوط) |

### مجموعات الأدوات

| المجموعة | الأدوات |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec` و`process` و`code_execution` (`bash` مقبول كاسم بديل لـ `exec`) |
| `group:fs`         | `read` و`write` و`edit` و`apply_patch` |
| `group:sessions`   | `sessions_list` و`sessions_history` و`sessions_send` و`sessions_spawn` و`sessions_yield` و`subagents` و`session_status` |
| `group:memory`     | `memory_search` و`memory_get` |
| `group:web`        | `web_search` و`x_search` و`web_fetch` |
| `group:ui`         | `browser` و`canvas` |
| `group:automation` | `cron` و`gateway` |
| `group:messaging`  | `message` |
| `group:nodes`      | `nodes` |
| `group:agents`     | `agents_list` |
| `group:media`      | `image` و`image_generate` و`video_generate` و`tts` |
| `group:openclaw`   | كل الأدوات المضمنة (باستثناء provider plugins) |

### `tools.allow` / `tools.deny`

سياسة السماح/المنع العامة للأدوات (المنع يفوز). غير حساسة لحالة الأحرف، وتدعم wildcards `*`. تطبق حتى عندما يكون Docker sandbox معطّلًا.

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

تقييد إضافي للأدوات لموفّرين أو نماذج محددة. الترتيب: الملف الشخصي الأساسي → ملف الموفّر الشخصي → السماح/المنع.

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

- يمكن لتجاوز كل وكيل (`agents.list[].tools.elevated`) فقط زيادة التقييد.
- يخزن `/elevated on|off|ask|full` الحالة لكل جلسة؛ وتطبق التوجيهات المضمنة على رسالة واحدة.
- يتجاوز `exec` المرتفع sandboxing ويستخدم مسار الهروب المهيأ (`gateway` افتراضيًا، أو `node` عندما يكون هدف exec هو `node`).

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

فحوصات أمان حلقات الأدوات تكون **معطلة افتراضيًا**. اضبط `enabled: true` لتفعيل الاكتشاف.
يمكن تعريف الإعدادات بشكل عام في `tools.loopDetection` وتجاوزها لكل وكيل في `agents.list[].tools.loopDetection`.

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
- `warningThreshold`: عتبة تحذير للأنماط المتكررة من دون تقدم.
- `criticalThreshold`: عتبة أعلى لحظر الحلقات الحرجة المتكررة.
- `globalCircuitBreakerThreshold`: عتبة إيقاف صارمة لأي تشغيل دون تقدم.
- `detectors.genericRepeat`: يحذر من تكرار الاستدعاءات للأداة نفسها/الوسائط نفسها.
- `detectors.knownPollNoProgress`: يحذر/يحظر الأدوات المعروفة للاستطلاع من دون تقدم (`process.poll` و`command_status` وغيرها).
- `detectors.pingPong`: يحذر/يحظر أنماط الأزواج المتناوبة دون تقدم.
- إذا كانت `warningThreshold >= criticalThreshold` أو `criticalThreshold >= globalCircuitBreakerThreshold`، يفشل التحقق.

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // أو BRAVE_API_KEY env
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
        directSend: false, // تفعيل اختياري: أرسل المهام المكتملة async للموسيقى/الفيديو مباشرة إلى القناة
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

**إدخال الموفّر** (`type: "provider"` أو محذوف):

- `provider`: معرّف موفّر API (`openai` أو `anthropic` أو `google`/`gemini` أو `groq`، إلخ)
- `model`: تجاوز معرّف النموذج
- `profile` / `preferredProfile`: اختيار ملف `auth-profiles.json`

**إدخال CLI** (`type: "cli"`):

- `command`: الملف التنفيذي المراد تشغيله
- `args`: وسائط قائمة على القوالب (تدعم `{{MediaPath}}` و`{{Prompt}}` و`{{MaxChars}}` وما إلى ذلك)

**الحقول المشتركة:**

- `capabilities`: قائمة اختيارية (`image` أو `audio` أو `video`). الافتراضيات: `openai`/`anthropic`/`minimax` → صورة، `google` → صورة+صوت+فيديو، `groq` → صوت.
- `prompt` و`maxChars` و`maxBytes` و`timeoutSeconds` و`language`: تجاوزات لكل إدخال.
- تعود الإخفاقات إلى الإدخال التالي.

تتبع مصادقة الموفّر الترتيب القياسي: `auth-profiles.json` → متغيرات البيئة → `models.providers.*.apiKey`.

**حقول الإكمال غير المتزامن:**

- `asyncCompletion.directSend`: عندما تكون `true`، تحاول مهام `music_generate`
  و`video_generate` غير المتزامنة المكتملة أولًا التسليم المباشر إلى القناة. الافتراضي: `false`
  (المسار القديم لإيقاظ جلسة الطالب/تسليم النموذج).

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

يتحكم في الجلسات التي يمكن استهدافها بواسطة أدوات الجلسة (`sessions_list` و`sessions_history` و`sessions_send`).

الافتراضي: `tree` (الجلسة الحالية + الجلسات التي أنشأتها، مثل subagents).

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
- `tree`: الجلسة الحالية + الجلسات التي أنشأتها الجلسة الحالية (subagents).
- `agent`: أي جلسة تخص معرّف الوكيل الحالي (وقد يشمل ذلك مستخدمين آخرين إذا كنت تشغّل جلسات لكل مرسل تحت معرّف الوكيل نفسه).
- `all`: أي جلسة. ولا يزال الاستهداف عبر الوكلاء يتطلب `tools.agentToAgent`.
- فرض sandbox: عندما تكون الجلسة الحالية داخل sandbox ويكون `agents.defaults.sandbox.sessionToolsVisibility="spawned"`، تُفرض الرؤية إلى `tree` حتى لو كانت `tools.sessions.visibility="all"`.

### `tools.sessions_spawn`

يتحكم في دعم المرفقات المضمنة لـ `sessions_spawn`.

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // تفعيل اختياري: اضبط true للسماح بمرفقات ملفات مضمنة
        maxTotalBytes: 5242880, // إجمالي 5 MB لكل الملفات
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 MB لكل ملف
        retainOnSessionKeep: false, // الاحتفاظ بالمرفقات عندما cleanup="keep"
      },
    },
  },
}
```

ملاحظات:

- المرفقات مدعومة فقط لـ `runtime: "subagent"`. ويرفض وقت تشغيل ACP هذه المرفقات.
- تُحوَّل الملفات إلى مساحة عمل الابن عند `.openclaw/attachments/<uuid>/` مع ملف `.manifest.json`.
- يُحجب محتوى المرفقات تلقائيًا من حفظ النصوص.
- يتم التحقق من مدخلات Base64 مع فحوص صارمة للأبجدية/الحشو وحاجز حجم قبل فك الترميز.
- تكون أذونات الملفات `0700` للأدلة و`0600` للملفات.
- يتبع التنظيف سياسة `cleanup`: يقوم `delete` دائمًا بإزالة المرفقات؛ ويحتفظ `keep` بها فقط عندما تكون `retainOnSessionKeep: true`.

### `tools.experimental`

أعلام الأدوات المضمنة التجريبية. تكون معطلة افتراضيًا ما لم تنطبق قاعدة تفعيل تلقائي خاصة بوقت التشغيل.

```json5
{
  tools: {
    experimental: {
      planTool: true, // فعّل update_plan التجريبية
    },
  },
}
```

ملاحظات:

- `planTool`: يفعّل أداة `update_plan` الهيكلية للعمل غير البسيط متعدد الخطوات.
- الافتراضي: `false` للموفّرين غير OpenAI. تقوم تشغيلات OpenAI وOpenAI Codex بتفعيلها تلقائيًا عندما تكون غير مضبوطة؛ واضبط `false` لتعطيل ذلك.
- عند التفعيل، تضيف system prompt أيضًا إرشادات استخدام بحيث يستخدمها النموذج فقط للعمل الجوهري ويحافظ على خطوة واحدة فقط كحد أقصى في حالة `in_progress`.

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

- `model`: النموذج الافتراضي للوكلاء الفرعيين المنشئين. إذا حُذف، يرث الوكلاء الفرعيون نموذج المستدعي.
- `allowAgents`: قائمة السماح الافتراضية لمعرّفات الوكلاء المستهدفة لـ `sessions_spawn` عندما لا يضبط الوكيل الطالب `subagents.allowAgents` الخاص به (`["*"]` = أي وكيل؛ الافتراضي: الوكيل نفسه فقط).
- `runTimeoutSeconds`: المهلة الافتراضية (بالثواني) لـ `sessions_spawn` عندما يحذف استدعاء الأداة `runTimeoutSeconds`. تعني `0` عدم وجود مهلة.
- سياسة الأدوات لكل وكيل فرعي: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.

---

## الموفّرون المخصصون وعناوين URL الأساسية

يستخدم OpenClaw فهرس النماذج المضمن. أضف موفّرين مخصصين عبر `models.providers` في الإعدادات أو `~/.openclaw/agents/<agentId>/agent/models.json`.

```json5
{
  models: {
    mode: "merge", // merge (افتراضي) | replace
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
- تجاوز جذر إعدادات الوكيل عبر `OPENCLAW_AGENT_DIR` (أو `PI_CODING_AGENT_DIR`، وهو اسم بديل قديم لمتغير بيئة).
- أسبقية الدمج لمعرّفات الموفّرين المطابقة:
  - تفوز قيم `baseUrl` غير الفارغة في `models.json` الخاصة بالوكيل.
  - تفوز قيم `apiKey` غير الفارغة الخاصة بالوكيل فقط عندما لا يكون ذلك الموفّر مُدارًا عبر SecretRef في سياق config/auth-profile الحالي.
  - تُحدّث قيم `apiKey` الخاصة بالموفّرين المُدارين عبر SecretRef من علامات المصدر (`ENV_VAR_NAME` لمراجع env، و`secretref-managed` لمراجع file/exec) بدلًا من حفظ الأسرار المحلولة.
  - تُحدّث قيم رؤوس الموفّر المُدارة عبر SecretRef من علامات المصدر (`secretref-env:ENV_VAR_NAME` لمراجع env، و`secretref-managed` لمراجع file/exec).
  - تعود قيم `apiKey`/`baseUrl` الفارغة أو المحذوفة الخاصة بالوكيل إلى `models.providers` في الإعدادات.
  - تستخدم القيم `contextWindow`/`maxTokens` الأعلى بين الإعداد الصريح وقيم الفهرس الضمنية للنماذج المطابقة.
  - تحافظ القيم `contextTokens` للنماذج المطابقة على حد وقت تشغيل صريح عندما يكون موجودًا؛ استخدمها لتقييد السياق الفعال دون تغيير بيانات النموذج الأصلية.
  - استخدم `models.mode: "replace"` عندما تريد من الإعدادات إعادة كتابة `models.json` بالكامل.
  - يكون حفظ العلامات معتمدًا على المصدر: تُكتب العلامات من لقطة إعدادات المصدر النشطة (قبل الحل)، وليس من قيم الأسرار المحلولة وقت التشغيل.

### تفاصيل حقول الموفّر

- `models.mode`: سلوك فهرس الموفّر (`merge` أو `replace`).
- `models.providers`: خريطة موفّرين مخصصين مفهرسة بمعرّف الموفّر.
- `models.providers.*.api`: محوّل الطلب (`openai-completions` أو `openai-responses` أو `anthropic-messages` أو `google-generative-ai`، إلخ).
- `models.providers.*.apiKey`: اعتماد الموفّر (فضّل SecretRef/الاستبدال بمتغيرات البيئة).
- `models.providers.*.auth`: استراتيجية المصادقة (`api-key` أو `token` أو `oauth` أو `aws-sdk`).
- `models.providers.*.injectNumCtxForOpenAICompat`: بالنسبة لـ Ollama + `openai-completions`، يحقن `options.num_ctx` في الطلبات (الافتراضي: `true`).
- `models.providers.*.authHeader`: يفرض نقل بيانات الاعتماد في ترويسة `Authorization` عندما يكون ذلك مطلوبًا.
- `models.providers.*.baseUrl`: عنوان URL الأساسي لـ API upstream.
- `models.providers.*.headers`: رؤوس ثابتة إضافية للتوجيه عبر proxy/tenant.
- `models.providers.*.request`: تجاوزات النقل لطلبات HTTP الخاصة بموفّر النموذج.
  - `request.headers`: رؤوس إضافية (تُدمج مع افتراضيات الموفّر). تقبل القيم SecretRef.
  - `request.auth`: تجاوز استراتيجية المصادقة. الأوضاع: `"provider-default"` (استخدم المصادقة المضمنة للموفّر)، `"authorization-bearer"` (مع `token`)، `"header"` (مع `headerName` و`value` و`prefix` الاختياري).
  - `request.proxy`: تجاوز وكيل HTTP. الأوضاع: `"env-proxy"` (استخدم متغيرات `HTTP_PROXY`/`HTTPS_PROXY`)، و`"explicit-proxy"` (مع `url`). يقبل كلا الوضعين كائن `tls` فرعيًا اختياريًا.
  - `request.tls`: تجاوز TLS للاتصالات المباشرة. الحقول: `ca` و`cert` و`key` و`passphrase` (كلها تقبل SecretRef) و`serverName` و`insecureSkipVerify`.
- `models.providers.*.models`: إدخالات فهرس نماذج موفّر صريحة.
- `models.providers.*.models.*.contextWindow`: بيانات وصفية لنافذة سياق النموذج الأصلية.
- `models.providers.*.models.*.contextTokens`: حد سياق اختياري لوقت التشغيل. استخدمه عندما تريد ميزانية سياق فعالة أصغر من `contextWindow` الأصلية للنموذج.
- `models.providers.*.models.*.compat.supportsDeveloperRole`: تلميح توافق اختياري. بالنسبة إلى `api: "openai-completions"` مع `baseUrl` غير فارغ وغير أصلي (مضيف ليس `api.openai.com`)، يفرض OpenClaw هذه القيمة إلى `false` وقت التشغيل. أما `baseUrl` الفارغ/المحذوف فيبقي سلوك OpenAI الافتراضي.
- `models.providers.*.models.*.compat.requiresStringContent`: تلميح توافق اختياري لنقاط نهاية chat المتوافقة مع OpenAI والتي تقبل السلاسل فقط. عندما تكون `true`، يقوم OpenClaw بتسطيح مصفوفات `messages[].content` النصية الخالصة إلى سلاسل عادية قبل إرسال الطلب.
- `plugins.entries.amazon-bedrock.config.discovery`: جذر إعدادات الاكتشاف التلقائي لـ Bedrock.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: تفعيل/تعطيل الاكتشاف الضمني.
- `plugins.entries.amazon-bedrock.config.discovery.region`: منطقة AWS للاكتشاف.
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: مرشح معرّف موفّر اختياري لاكتشاف مستهدف.
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: فاصل الاستطلاع لتحديث الاكتشاف.
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: نافذة السياق الاحتياطية للنماذج المكتشفة.
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: الحد الاحتياطي لرموز الخرج للنماذج المكتشفة.

### أمثلة الموفّر

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

استخدم `cerebras/zai-glm-4.7` مع Cerebras؛ و`zai/glm-4.7` مع Z.AI direct.

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

اضبط `OPENCODE_API_KEY` (أو `OPENCODE_ZEN_API_KEY`). استخدم مراجع `opencode/...` لفهرس Zen أو مراجع `opencode-go/...` لفهرس Go. اختصار: `openclaw onboard --auth-choice opencode-zen` أو `openclaw onboard --auth-choice opencode-go`.

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

اضبط `ZAI_API_KEY`. وتُقبل الصيغتان `z.ai/*` و`z-ai/*` كأسماء بديلة. اختصار: `openclaw onboard --auth-choice zai-api-key`.

- نقطة النهاية العامة: `https://api.z.ai/api/paas/v4`
- نقطة نهاية البرمجة (الافتراضية): `https://api.z.ai/api/coding/paas/v4`
- بالنسبة إلى نقطة النهاية العامة، عرّف موفّرًا مخصصًا مع تجاوز base URL.

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

بالنسبة إلى نقطة النهاية في الصين: `baseUrl: "https://api.moonshot.cn/v1"` أو `openclaw onboard --auth-choice moonshot-api-key-cn`.

تعلن نقاط نهاية Moonshot الأصلية عن توافق استخدام البث على النقل المشترك
`openai-completions`، وأصبح OpenClaw الآن يربط ذلك بقدرات نقطة النهاية
بدلًا من الاكتفاء بمعرّف الموفّر المضمن.

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

متوافق مع Anthropic، وموفّر مضمن. اختصار: `openclaw onboard --auth-choice kimi-code-api-key`.

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

يجب أن يحذف base URL اللاحقة `/v1` (إذ يضيفها عميل Anthropic). اختصار: `openclaw onboard --auth-choice synthetic-api-key`.

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
يفترض فهرس النماذج الآن M2.7 فقط.
على مسار البث المتوافق مع Anthropic، يعطّل OpenClaw التفكير في MiniMax
افتراضيًا ما لم تضبط `thinking` صراحة بنفسك. ويعيد `/fast on` أو
`params.fastMode: true` كتابة `MiniMax-M2.7` إلى
`MiniMax-M2.7-highspeed`.

</Accordion>

<Accordion title="النماذج المحلية (LM Studio)">

راجع [النماذج المحلية](/ar/gateway/local-models). باختصار: شغّل نموذجًا محليًا كبيرًا عبر LM Studio Responses API على عتاد قوي؛ واحتفظ بالنماذج المستضافة مدمجةً كاحتياطي.

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
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // أو سلسلة صريحة
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: قائمة سماح اختيارية لـ bundled skills فقط (لا تتأثر managed/workspace skills).
- `load.extraDirs`: جذور Skills مشتركة إضافية (أدنى أسبقية).
- `install.preferBrew`: عندما تكون true، يُفضَّل استخدام مثبّتات Homebrew عندما يكون `brew` متاحًا قبل الرجوع إلى أنواع المثبتات الأخرى.
- `install.nodeManager`: تفضيل مثبت node لمواصفات `metadata.openclaw.install`
  (`npm` | `pnpm` | `yarn` | `bun`).
- `entries.<skillKey>.enabled: false` يعطّل Skill حتى لو كانت bundled/مثبتة.
- `entries.<skillKey>.apiKey`: حقل تسهيلي لمفتاح API للـ Skills التي تعلن متغير env أساسيًا (سلسلة صريحة أو كائن SecretRef).

---

## Plugins

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

- تُحمّل من `~/.openclaw/extensions` و`<workspace>/.openclaw/extensions` بالإضافة إلى `plugins.load.paths`.
- يقبل الاكتشاف plugins الأصلية في OpenClaw بالإضافة إلى حزم Codex المتوافقة وحزم Claude، بما في ذلك حزم Claude عديمة manifest ذات التخطيط الافتراضي.
- **تتطلب تغييرات الإعدادات إعادة تشغيل للبوابة.**
- `allow`: قائمة سماح اختيارية (لا تُحمَّل إلا الـ plugins المدرجة). يفوز `deny`.
- `plugins.entries.<id>.apiKey`: حقل تسهيلي لمفتاح API على مستوى plugin (عندما يدعمه الـ plugin).
- `plugins.entries.<id>.env`: خريطة متغيرات بيئة ضمن نطاق plugin.
- `plugins.entries.<id>.hooks.allowPromptInjection`: عندما تكون `false`، يحظر core قيمة `before_prompt_build` ويتجاهل الحقول القديمة المعدلة لـ prompt من `before_agent_start` القديم، مع الحفاظ على `modelOverride` و`providerOverride` القديمين. ينطبق هذا على hooks الخاصة بالـ plugins الأصلية وعلى أدلة hooks التي توفرها الحزم المدعومة.
- `plugins.entries.<id>.subagent.allowModelOverride`: يثق صراحة بهذا الـ plugin لطلب تجاوزات `provider` و`model` لكل تشغيل بالنسبة لتشغيلات subagent الخلفية.
- `plugins.entries.<id>.subagent.allowedModels`: قائمة سماح اختيارية لأهداف `provider/model` المعيارية لتجاوزات subagent الموثوقة. استخدم `"*"` فقط عندما تريد عمدًا السماح بأي نموذج.
- `plugins.entries.<id>.config`: كائن إعدادات يعرّفه الـ plugin (ويُتحقق منه بواسطة مخطط plugin الأصلي في OpenClaw عند توفره).
- `plugins.entries.firecrawl.config.webFetch`: إعدادات موفّر جلب الويب Firecrawl.
  - `apiKey`: مفتاح Firecrawl API (يقبل SecretRef). يعود إلى `plugins.entries.firecrawl.config.webSearch.apiKey` أو `tools.web.fetch.firecrawl.apiKey` القديم أو متغير البيئة `FIRECRAWL_API_KEY`.
  - `baseUrl`: عنوان Firecrawl API الأساسي (الافتراضي: `https://api.firecrawl.dev`).
  - `onlyMainContent`: استخراج المحتوى الرئيسي فقط من الصفحات (الافتراضي: `true`).
  - `maxAgeMs`: الحد الأقصى لعمر الكاش بالميلي ثانية (الافتراضي: `172800000` / يومان).
  - `timeoutSeconds`: مهلة طلب الكشط بالثواني (الافتراضي: `60`).
- `plugins.entries.xai.config.xSearch`: إعدادات xAI X Search (بحث الويب Grok).
  - `enabled`: تمكين موفّر X Search.
  - `model`: نموذج Grok المستخدم للبحث (مثل `"grok-4-1-fast"`).
- `plugins.entries.memory-core.config.dreaming`: إعدادات dreaming الخاصة بالذاكرة (تجريبية). راجع [Dreaming](/ar/concepts/dreaming) للمراحل والعتبات.
  - `enabled`: مفتاح dreaming الرئيسي (الافتراضي `false`).
  - `frequency`: إيقاع cron لكل دورة dreaming كاملة (`"0 3 *