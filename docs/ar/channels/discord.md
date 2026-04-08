---
read_when:
    - العمل على ميزات قناة Discord
summary: حالة دعم بوت Discord وإمكاناته وإعداده
title: Discord
x-i18n:
    generated_at: "2026-04-08T07:18:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3cd2886fad941ae2129e681911309539e9a65a2352b777b538d7f4686a68f73f
    source_path: channels/discord.md
    workflow: 15
---

# Discord (Bot API)

الحالة: جاهز للرسائل الخاصة والقنوات الجماعية عبر بوابة Discord الرسمية.

<CardGroup cols={3}>
  <Card title="الإقران" icon="link" href="/ar/channels/pairing">
    تُستخدم الرسائل الخاصة في Discord افتراضيًا لوضع الإقران.
  </Card>
  <Card title="أوامر الشرطة المائلة" icon="terminal" href="/ar/tools/slash-commands">
    سلوك الأوامر الأصلي وفهرس الأوامر.
  </Card>
  <Card title="استكشاف أخطاء القناة وإصلاحها" icon="wrench" href="/ar/channels/troubleshooting">
    التشخيص عبر القنوات وتدفق الإصلاح.
  </Card>
</CardGroup>

## إعداد سريع

ستحتاج إلى إنشاء تطبيق جديد مع بوت، وإضافة البوت إلى خادمك، ثم إقرانه مع OpenClaw. نوصي بإضافة البوت إلى خادمك الخاص. إذا لم يكن لديك واحد بعد، [فأنشئ واحدًا أولًا](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server) (اختر **Create My Own > For me and my friends**).

<Steps>
  <Step title="أنشئ تطبيق Discord وبوت">
    انتقل إلى [Discord Developer Portal](https://discord.com/developers/applications) وانقر **New Application**. سمّه باسم مثل "OpenClaw".

    انقر **Bot** في الشريط الجانبي. اضبط **Username** على أي اسم تطلقه على وكيل OpenClaw الخاص بك.

  </Step>

  <Step title="فعّل الامتيازات الخاصة">
    وأنت لا تزال في صفحة **Bot**، مرّر لأسفل إلى **Privileged Gateway Intents** وفعّل:

    - **Message Content Intent** (مطلوب)
    - **Server Members Intent** (موصى به؛ مطلوب لقوائم السماح المستندة إلى الأدوار ولمطابقة الأسماء مع المعرّفات)
    - **Presence Intent** (اختياري؛ مطلوب فقط لتحديثات الحالة)

  </Step>

  <Step title="انسخ رمز البوت المميز">
    مرّر مرة أخرى إلى أعلى صفحة **Bot** وانقر **Reset Token**.

    <Note>
    على الرغم من الاسم، فإن هذا يُنشئ أول رمز مميز لك — لا تتم "إعادة تعيين" أي شيء.
    </Note>

    انسخ الرمز المميز واحفظه في مكان ما. هذا هو **Bot Token** الخاص بك وستحتاج إليه بعد قليل.

  </Step>

  <Step title="أنشئ رابط دعوة وأضف البوت إلى خادمك">
    انقر **OAuth2** في الشريط الجانبي. ستنشئ رابط دعوة بالأذونات الصحيحة لإضافة البوت إلى خادمك.

    مرّر لأسفل إلى **OAuth2 URL Generator** وفعّل:

    - `bot`
    - `applications.commands`

    سيظهر قسم **Bot Permissions** أدناه. فعّل:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (اختياري)

    انسخ الرابط المُنشأ في الأسفل، والصقه في متصفحك، وحدد خادمك، ثم انقر **Continue** للاتصال. يجب أن ترى الآن البوت الخاص بك في خادم Discord.

  </Step>

  <Step title="فعّل وضع المطور واجمع معرّفاتك">
    بالعودة إلى تطبيق Discord، تحتاج إلى تفعيل وضع المطور حتى تتمكن من نسخ المعرّفات الداخلية.

    1. انقر **User Settings** (أيقونة الترس بجانب صورتك الرمزية) → **Advanced** → فعّل **Developer Mode**
    2. انقر بزر الماوس الأيمن على **أيقونة الخادم** في الشريط الجانبي → **Copy Server ID**
    3. انقر بزر الماوس الأيمن على **صورتك الرمزية** → **Copy User ID**

    احفظ **Server ID** و**User ID** مع Bot Token الخاص بك — سترسل الثلاثة جميعًا إلى OpenClaw في الخطوة التالية.

  </Step>

  <Step title="اسمح بالرسائل الخاصة من أعضاء الخادم">
    لكي يعمل الإقران، يحتاج Discord إلى السماح للبوت الخاص بك بإرسال رسالة خاصة إليك. انقر بزر الماوس الأيمن على **أيقونة الخادم** → **Privacy Settings** → فعّل **Direct Messages**.

    يتيح هذا لأعضاء الخادم (بمن فيهم البوتات) إرسال رسائل خاصة إليك. أبقِ هذا الخيار مفعّلًا إذا كنت تريد استخدام الرسائل الخاصة في Discord مع OpenClaw. إذا كنت تخطط لاستخدام القنوات الجماعية فقط، يمكنك تعطيل الرسائل الخاصة بعد الإقران.

  </Step>

  <Step title="اضبط رمز البوت المميز بأمان (لا ترسله في الدردشة)">
    رمز بوت Discord المميز سرّي (مثل كلمة المرور). اضبطه على الجهاز الذي يشغّل OpenClaw قبل مراسلة وكيلك.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN --dry-run
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN
openclaw config set channels.discord.enabled true --strict-json
openclaw gateway
```

    إذا كان OpenClaw يعمل بالفعل كخدمة في الخلفية، فأعد تشغيله عبر تطبيق OpenClaw على Mac أو بإيقاف عملية `openclaw gateway run` ثم إعادة تشغيلها.

  </Step>

  <Step title="اضبط OpenClaw وأجرِ الإقران">

    <Tabs>
      <Tab title="اسأل وكيلك">
        تحدث مع وكيل OpenClaw الخاص بك على أي قناة موجودة (مثل Telegram) وأخبره بذلك. إذا كانت Discord هي قناتك الأولى، فاستخدم علامة تبويب CLI / config بدلًا من ذلك.

        > "لقد ضبطت بالفعل رمز بوت Discord الخاص بي في الإعدادات. يُرجى إكمال إعداد Discord باستخدام User ID `<user_id>` وServer ID `<server_id>`."
      </Tab>
      <Tab title="CLI / config">
        إذا كنت تفضّل إعدادات قائمة على الملفات، فاضبط:

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: {
        source: "env",
        provider: "default",
        id: "DISCORD_BOT_TOKEN",
      },
    },
  },
}
```

        بديل env للحساب الافتراضي:

```bash
DISCORD_BOT_TOKEN=...
```

        القيم النصية الصريحة لـ `token` مدعومة. كما أن قيم SecretRef مدعومة أيضًا لـ `channels.discord.token` عبر موفري env/file/exec. راجع [إدارة الأسرار](/ar/gateway/secrets).

      </Tab>
    </Tabs>

  </Step>

  <Step title="وافق على أول إقران عبر الرسائل الخاصة">
    انتظر حتى تعمل البوابة، ثم أرسل رسالة خاصة إلى البوت في Discord. سيرد عليك برمز إقران.

    <Tabs>
      <Tab title="اسأل وكيلك">
        أرسل رمز الإقران إلى وكيلك على قناتك الحالية:

        > "وافق على رمز إقران Discord هذا: `<CODE>`"
      </Tab>
      <Tab title="CLI">

```bash
openclaw pairing list discord
openclaw pairing approve discord <CODE>
```

      </Tab>
    </Tabs>

    تنتهي صلاحية رموز الإقران بعد ساعة واحدة.

    يجب أن تتمكن الآن من الدردشة مع وكيلك في Discord عبر الرسائل الخاصة.

  </Step>
</Steps>

<Note>
تحليل الرمز المميز يعتمد على الحساب. قيم الرمز المميز في الإعدادات لها الأولوية على بديل env. يُستخدم `DISCORD_BOT_TOKEN` فقط للحساب الافتراضي.
بالنسبة للاتصالات الصادرة المتقدمة (أداة الرسائل/إجراءات القناة)، يُستخدم `token` صريح لكل استدعاء لذلك الاستدعاء. ينطبق هذا على إجراءات الإرسال والقراءة/الفحص (مثل read/search/fetch/thread/pins/permissions). وتظل إعدادات سياسة الحساب/إعادة المحاولة قادمة من الحساب المحدد في اللقطة النشطة لوقت التشغيل.
</Note>

## موصى به: إعداد مساحة عمل جماعية

بمجرد أن تعمل الرسائل الخاصة، يمكنك إعداد خادم Discord الخاص بك كمساحة عمل كاملة حيث تحصل كل قناة على جلسة وكيل خاصة بها مع سياقها الخاص. يُوصى بهذا للخوادم الخاصة التي تكون أنت والبوت فقط فيها.

<Steps>
  <Step title="أضف خادمك إلى قائمة السماح الجماعية">
    يتيح هذا لوكيلك الرد في أي قناة على خادمك، وليس فقط في الرسائل الخاصة.

    <Tabs>
      <Tab title="اسأل وكيلك">
        > "أضف Server ID الخاص بي في Discord وهو `<server_id>` إلى قائمة السماح الجماعية"
      </Tab>
      <Tab title="الإعدادات">

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: true,
          users: ["YOUR_USER_ID"],
        },
      },
    },
  },
}
```

      </Tab>
    </Tabs>

  </Step>

  <Step title="اسمح بالردود دون @mention">
    افتراضيًا، لا يرد وكيلك في القنوات الجماعية إلا عند الإشارة إليه بواسطة @mention. بالنسبة إلى خادم خاص، من المرجح أنك تريد أن يرد على كل رسالة.

    <Tabs>
      <Tab title="اسأل وكيلك">
        > "اسمح لوكيلي بالرد على هذا الخادم دون الحاجة إلى الإشارة إليه باستخدام @mention"
      </Tab>
      <Tab title="الإعدادات">
        اضبط `requireMention: false` في إعدادات الخادم الجماعي:

```json5
{
  channels: {
    discord: {
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: false,
        },
      },
    },
  },
}
```

      </Tab>
    </Tabs>

  </Step>

  <Step title="خطط للذاكرة في القنوات الجماعية">
    افتراضيًا، لا يتم تحميل الذاكرة طويلة الأمد (MEMORY.md) إلا في جلسات الرسائل الخاصة. ولا تُحمّل MEMORY.md تلقائيًا في القنوات الجماعية.

    <Tabs>
      <Tab title="اسأل وكيلك">
        > "عندما أطرح أسئلة في قنوات Discord، استخدم memory_search أو memory_get إذا احتجت إلى سياق طويل الأمد من MEMORY.md."
      </Tab>
      <Tab title="يدوي">
        إذا كنت بحاجة إلى سياق مشترك في كل قناة، فضع التعليمات الثابتة في `AGENTS.md` أو `USER.md` (يتم حقنها في كل جلسة). واحتفظ بالملاحظات طويلة الأمد في `MEMORY.md` واصل إليها عند الطلب باستخدام أدوات الذاكرة.
      </Tab>
    </Tabs>

  </Step>
</Steps>

أنشئ الآن بعض القنوات على خادم Discord الخاص بك وابدأ الدردشة. يمكن لوكيلك رؤية اسم القناة، وتحصل كل قناة على جلسة معزولة خاصة بها — لذا يمكنك إعداد `#coding` أو `#home` أو `#research` أو أي شيء يناسب سير عملك.

## نموذج وقت التشغيل

- البوابة تملك اتصال Discord.
- توجيه الردود حتمي: الرسائل الواردة من Discord تُعاد إلى Discord.
- افتراضيًا (`session.dmScope=main`)، تشارك الدردشات المباشرة الجلسة الرئيسية للوكيل (`agent:main:main`).
- القنوات الجماعية لها مفاتيح جلسات معزولة (`agent:<agentId>:discord:channel:<channelId>`).
- يتم تجاهل الرسائل الخاصة الجماعية افتراضيًا (`channels.discord.dm.groupEnabled=false`).
- تعمل أوامر الشرطة المائلة الأصلية في جلسات أوامر معزولة (`agent:<agentId>:discord:slash:<userId>`)، مع الاستمرار في حمل `CommandTargetSessionKey` إلى جلسة المحادثة الموجّهة.

## قنوات المنتدى

قنوات المنتدى والوسائط في Discord لا تقبل إلا منشورات السلاسل. يدعم OpenClaw طريقتين لإنشائها:

- أرسل رسالة إلى أصل المنتدى (`channel:<forumId>`) لإنشاء سلسلة تلقائيًا. يستخدم عنوان السلسلة أول سطر غير فارغ من رسالتك.
- استخدم `openclaw message thread create` لإنشاء سلسلة مباشرة. لا تمرر `--message-id` لقنوات المنتدى.

مثال: أرسل إلى أصل المنتدى لإنشاء سلسلة

```bash
openclaw message send --channel discord --target channel:<forumId> \
  --message "Topic title\nBody of the post"
```

مثال: أنشئ سلسلة منتدى بشكل صريح

```bash
openclaw message thread create --channel discord --target channel:<forumId> \
  --thread-name "Topic title" --message "Body of the post"
```

أصول المنتدى لا تقبل مكونات Discord. إذا كنت بحاجة إلى مكونات، فأرسل إلى السلسلة نفسها (`channel:<threadId>`).

## المكونات التفاعلية

يدعم OpenClaw حاويات Discord components v2 لرسائل الوكيل. استخدم أداة الرسائل مع حمولة `components`. تُوجَّه نتائج التفاعل مرة أخرى إلى الوكيل كرسائل واردة عادية وتتبع إعدادات Discord `replyToMode` الحالية.

الكتل المدعومة:

- `text` و`section` و`separator` و`actions` و`media-gallery` و`file`
- تسمح صفوف الإجراءات بما يصل إلى 5 أزرار أو قائمة تحديد واحدة
- أنواع التحديد: `string` و`user` و`role` و`mentionable` و`channel`

افتراضيًا، تكون المكونات للاستخدام مرة واحدة. اضبط `components.reusable=true` للسماح باستخدام الأزرار وعمليات التحديد والنماذج عدة مرات حتى تنتهي صلاحيتها.

لتقييد من يمكنه النقر على زر، اضبط `allowedUsers` على ذلك الزر (معرّفات مستخدمي Discord أو الوسوم أو `*`). عند الضبط، يتلقى المستخدمون غير المطابقين رفضًا مؤقتًا.

يفتح الأمران المائلان `/model` و`/models` منتقي نماذج تفاعليًا مع قوائم منسدلة للموفر والنموذج بالإضافة إلى خطوة Submit. ويكون رد المنتقي مؤقتًا ولا يمكن استخدامه إلا من المستخدم الذي استدعاه.

مرفقات الملفات:

- يجب أن تشير كتل `file` إلى مرجع مرفق (`attachment://<filename>`)
- وفّر المرفق عبر `media`/`path`/`filePath` (ملف واحد)؛ استخدم `media-gallery` لعدة ملفات
- استخدم `filename` لتجاوز اسم الرفع عندما يجب أن يطابق مرجع المرفق

النماذج المنبثقة:

- أضف `components.modal` بما يصل إلى 5 حقول
- أنواع الحقول: `text` و`checkbox` و`radio` و`select` و`role-select` و`user-select`
- يضيف OpenClaw زر تشغيل تلقائيًا

مثال:

```json5
{
  channel: "discord",
  action: "send",
  to: "channel:123456789012345678",
  message: "Optional fallback text",
  components: {
    reusable: true,
    text: "Choose a path",
    blocks: [
      {
        type: "actions",
        buttons: [
          {
            label: "Approve",
            style: "success",
            allowedUsers: ["123456789012345678"],
          },
          { label: "Decline", style: "danger" },
        ],
      },
      {
        type: "actions",
        select: {
          type: "string",
          placeholder: "Pick an option",
          options: [
            { label: "Option A", value: "a" },
            { label: "Option B", value: "b" },
          ],
        },
      },
    ],
    modal: {
      title: "Details",
      triggerLabel: "Open form",
      fields: [
        { type: "text", label: "Requester" },
        {
          type: "select",
          label: "Priority",
          options: [
            { label: "Low", value: "low" },
            { label: "High", value: "high" },
          ],
        },
      ],
    },
  },
}
```

## التحكم في الوصول والتوجيه

<Tabs>
  <Tab title="سياسة الرسائل الخاصة">
    يتحكم `channels.discord.dmPolicy` في الوصول إلى الرسائل الخاصة (القديم: `channels.discord.dm.policy`):

    - `pairing` (افتراضي)
    - `allowlist`
    - `open` (يتطلب أن يتضمن `channels.discord.allowFrom` القيمة `"*"`؛ القديم: `channels.discord.dm.allowFrom`)
    - `disabled`

    إذا لم تكن سياسة الرسائل الخاصة مفتوحة، فسيتم حظر المستخدمين غير المعروفين (أو مطالبتهم بالإقران في وضع `pairing`).

    أولوية الحسابات المتعددة:

    - ينطبق `channels.discord.accounts.default.allowFrom` على الحساب `default` فقط.
    - ترث الحسابات المسمّاة `channels.discord.allowFrom` عندما لا يكون `allowFrom` الخاص بها مضبوطًا.
    - لا ترث الحسابات المسمّاة `channels.discord.accounts.default.allowFrom`.

    تنسيق هدف الرسائل الخاصة للتسليم:

    - `user:<id>`
    - الإشارة `<@id>`

    تكون المعرّفات الرقمية المجردة ملتبسة ويتم رفضها ما لم يتم توفير نوع هدف مستخدم/قناة صريح.

  </Tab>

  <Tab title="سياسة الخادم الجماعي">
    تتم إدارة التعامل مع الخوادم الجماعية بواسطة `channels.discord.groupPolicy`:

    - `open`
    - `allowlist`
    - `disabled`

    خط الأساس الآمن عندما يكون `channels.discord` موجودًا هو `allowlist`.

    سلوك `allowlist`:

    - يجب أن يطابق الخادم الجماعي `channels.discord.guilds` (`id` مفضل، وslug مقبول)
    - قوائم سماح اختيارية للمرسلين: `users` (يوصى بالمعرّفات الثابتة) و`roles` (معرّفات الأدوار فقط)؛ إذا تم ضبط أي منهما، يُسمح للمرسلين عندما يطابقون `users` أو `roles`
    - تكون المطابقة المباشرة للاسم/الوسم معطلة افتراضيًا؛ فعّل `channels.discord.dangerouslyAllowNameMatching: true` فقط كوضع توافق طارئ
    - الأسماء/الوسوم مدعومة في `users`، لكن المعرّفات أكثر أمانًا؛ يحذّر `openclaw security audit` عند استخدام إدخالات اسم/وسم
    - إذا كان لدى خادم جماعي `channels` مضبوطة، فسيتم رفض القنوات غير المدرجة
    - إذا لم يكن لدى خادم جماعي كتلة `channels`، فسيُسمح بكل القنوات ضمن ذلك الخادم الجماعي الموجود في قائمة السماح

    مثال:

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        "123456789012345678": {
          requireMention: true,
          ignoreOtherMentions: true,
          users: ["987654321098765432"],
          roles: ["123456789012345678"],
          channels: {
            general: { allow: true },
            help: { allow: true, requireMention: true },
          },
        },
      },
    },
  },
}
```

    إذا قمت فقط بضبط `DISCORD_BOT_TOKEN` ولم تُنشئ كتلة `channels.discord`، فإن بديل وقت التشغيل يكون `groupPolicy="allowlist"` (مع تحذير في السجلات)، حتى لو كان `channels.defaults.groupPolicy` يساوي `open`.

  </Tab>

  <Tab title="الإشارات والرسائل الخاصة الجماعية">
    تكون رسائل الخوادم الجماعية محكومة بالإشارة افتراضيًا.

    يشمل اكتشاف الإشارة:

    - إشارة صريحة للبوت
    - أنماط الإشارة المضبوطة (`agents.list[].groupChat.mentionPatterns`، والبديل `messages.groupChat.mentionPatterns`)
    - سلوك الرد الضمني على البوت في الحالات المدعومة

    يتم ضبط `requireMention` لكل خادم جماعي/قناة (`channels.discord.guilds...`).
    ويؤدي `ignoreOtherMentions` اختياريًا إلى إسقاط الرسائل التي تذكر مستخدمًا/دورًا آخر ولكن ليس البوت (باستثناء @everyone/@here).

    الرسائل الخاصة الجماعية:

    - افتراضي: يتم تجاهلها (`dm.groupEnabled=false`)
    - قائمة سماح اختيارية عبر `dm.groupChannels` (معرّفات القنوات أو slugs)

  </Tab>
</Tabs>

### التوجيه المستند إلى الأدوار للوكلاء

استخدم `bindings[].match.roles` لتوجيه أعضاء خوادم Discord الجماعية إلى وكلاء مختلفين حسب معرّف الدور. تقبل الارتباطات المستندة إلى الأدوار معرّفات الأدوار فقط ويتم تقييمها بعد ارتباطات النظير أو نظير الأصل وقبل الارتباطات الخاصة بالخادم الجماعي فقط. إذا كان الارتباط يضبط أيضًا حقول مطابقة أخرى (مثل `peer` + `guildId` + `roles`) فيجب أن تتطابق كل الحقول المضبوطة.

```json5
{
  bindings: [
    {
      agentId: "opus",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
        roles: ["111111111111111111"],
      },
    },
    {
      agentId: "sonnet",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
      },
    },
  ],
}
```

## إعداد Developer Portal

<AccordionGroup>
  <Accordion title="أنشئ التطبيق والبوت">

    1. Discord Developer Portal -> **Applications** -> **New Application**
    2. **Bot** -> **Add Bot**
    3. انسخ رمز البوت المميز

  </Accordion>

  <Accordion title="الامتيازات الخاصة">
    في **Bot -> Privileged Gateway Intents**، فعّل:

    - Message Content Intent
    - Server Members Intent (موصى به)

    امتياز Presence اختياري ومطلوب فقط إذا كنت تريد تلقي تحديثات الحالة. لا يتطلب ضبط حالة البوت (`setPresence`) تفعيل تحديثات الحالة للأعضاء.

  </Accordion>

  <Accordion title="نطاقات OAuth والأذونات الأساسية">
    مولد رابط OAuth:

    - النطاقات: `bot` و`applications.commands`

    الأذونات الأساسية النموذجية:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (اختياري)

    تجنب `Administrator` ما لم يكن مطلوبًا صراحة.

  </Accordion>

  <Accordion title="انسخ المعرّفات">
    فعّل Discord Developer Mode، ثم انسخ:

    - معرّف الخادم
    - معرّف القناة
    - معرّف المستخدم

    فضّل المعرّفات الرقمية في إعدادات OpenClaw من أجل تدقيقات وفحوصات أكثر موثوقية.

  </Accordion>
</AccordionGroup>

## الأوامر الأصلية ومصادقة الأوامر

- القيمة الافتراضية لـ `commands.native` هي `"auto"` وهي مفعّلة لـ Discord.
- تجاوز لكل قناة: `channels.discord.commands.native`.
- يؤدي `commands.native=false` إلى مسح أوامر Discord الأصلية المسجلة سابقًا صراحةً.
- تستخدم مصادقة الأوامر الأصلية نفس قوائم السماح/السياسات في Discord مثل معالجة الرسائل العادية.
- قد تظل الأوامر مرئية في واجهة Discord للمستخدمين غير المصرّح لهم؛ لكن التنفيذ يظل يفرض مصادقة OpenClaw ويعيد "غير مخوّل".

راجع [أوامر الشرطة المائلة](/ar/tools/slash-commands) للاطلاع على فهرس الأوامر والسلوك.

إعدادات أوامر الشرطة المائلة الافتراضية:

- `ephemeral: true`

## تفاصيل الميزات

<AccordionGroup>
  <Accordion title="وسوم الردود والردود الأصلية">
    يدعم Discord وسوم الردود في مخرجات الوكيل:

    - `[[reply_to_current]]`
    - `[[reply_to:<id>]]`

    يتحكم بها `channels.discord.replyToMode`:

    - `off` (افتراضي)
    - `first`
    - `all`
    - `batched`

    ملاحظة: يؤدي `off` إلى تعطيل سلاسل الردود الضمنية. ولا تزال وسوم `[[reply_to_*]]` الصريحة محترمة.
    يقوم `first` دائمًا بإرفاق مرجع الرد الأصلي الضمني بأول رسالة Discord صادرة في الدورة.
    يقوم `batched` بإرفاق مرجع الرد الأصلي الضمني في Discord فقط عندما
    تكون الدورة الواردة دفعة مؤجلة من عدة رسائل. ويكون هذا مفيدًا
    عندما تريد الردود الأصلية أساسًا للمحادثات المتدفقة والغامضة، وليس لكل
    دورة رسالة مفردة.

    تظهر معرّفات الرسائل في السياق/السجل حتى تتمكن الوكلاء من استهداف رسائل محددة.

  </Accordion>

  <Accordion title="معاينة البث المباشر">
    يمكن لـ OpenClaw بث مسودات الردود عن طريق إرسال رسالة مؤقتة وتحريرها مع وصول النص.

    - يتحكم `channels.discord.streaming` في بث المعاينة (`off` | `partial` | `block` | `progress`، الافتراضي: `off`).
    - يظل الافتراضي `off` لأن تعديلات معاينة Discord قد تصطدم بسرعة بحدود المعدل، خاصة عند مشاركة عدة بوتات أو بوابات للحساب نفسه أو لحركة خادم جماعي واحد.
    - القيمة `progress` مقبولة لاتساق القنوات المختلفة ويتم تعيينها إلى `partial` في Discord.
    - `channels.discord.streamMode` اسم بديل قديم ويتم ترحيله تلقائيًا.
    - يقوم `partial` بتحرير رسالة معاينة واحدة مع وصول الرموز.
    - يُصدر `block` مقاطع بحجم المسودة (استخدم `draftChunk` لضبط الحجم ونقاط الفصل).

    مثال:

```json5
{
  channels: {
    discord: {
      streaming: "partial",
    },
  },
}
```

    القيم الافتراضية لتقطيع وضع `block` (مقيدة بـ `channels.discord.textChunkLimit`):

```json5
{
  channels: {
    discord: {
      streaming: "block",
      draftChunk: {
        minChars: 200,
        maxChars: 800,
        breakPreference: "paragraph",
      },
    },
  },
}
```

    بث المعاينة نصي فقط؛ أما الردود التي تحتوي على وسائط فتعود إلى التسليم العادي.

    ملاحظة: بث المعاينة منفصل عن البث الكتلي. عندما يكون البث الكتلي مفعّلًا صراحةً
    لـ Discord، يتخطى OpenClaw بث المعاينة لتجنب البث المزدوج.

  </Accordion>

  <Accordion title="السجل والسياق وسلوك السلاسل">
    سياق سجل الخوادم الجماعية:

    - الافتراضي لـ `channels.discord.historyLimit` هو `20`
    - البديل: `messages.groupChat.historyLimit`
    - القيمة `0` تعطل الميزة

    عناصر التحكم في سجل الرسائل الخاصة:

    - `channels.discord.dmHistoryLimit`
    - `channels.discord.dms["<user_id>"].historyLimit`

    سلوك السلاسل:

    - تُوجَّه سلاسل Discord كجلسات قنوات
    - يمكن استخدام بيانات السلسلة الأصلية الوصفية لربط جلسة الأصل
    - يرث ضبط السلسلة إعدادات القناة الأصلية ما لم يوجد إدخال خاص بالسلسلة

    يتم حقن مواضيع القنوات كسياق **غير موثوق** (وليس كموجّه نظام).
    ويظل سياق الردود والرسائل المقتبسة حاليًا كما تم استلامه.
    قوائم السماح في Discord تتحكم أساسًا في من يمكنه تشغيل الوكيل، وليست حدًا كاملًا لحجب السياق التكميلي.

  </Accordion>

  <Accordion title="جلسات مرتبطة بالسلاسل للوكلاء الفرعيين">
    يمكن لـ Discord ربط سلسلة بهدف جلسة بحيث تستمر الرسائل اللاحقة في تلك السلسلة بالتوجيه إلى الجلسة نفسها (بما في ذلك جلسات الوكلاء الفرعيين).

    الأوامر:

    - `/focus <target>` لربط السلسلة الحالية/الجديدة بهدف وكيل فرعي/جلسة
    - `/unfocus` لإزالة الارتباط الحالي للسلسلة
    - `/agents` لإظهار التشغيلات النشطة وحالة الارتباط
    - `/session idle <duration|off>` لفحص/تحديث إلغاء التركيز التلقائي بعد عدم النشاط للارتباطات المركزة
    - `/session max-age <duration|off>` لفحص/تحديث الحد الأقصى الصارم للعمر للارتباطات المركزة

    الإعدادات:

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // اشتراك اختياري
      },
    },
  },
}
```

    ملاحظات:

    - يضبط `session.threadBindings.*` القيم الافتراضية العامة.
    - يتجاوز `channels.discord.threadBindings.*` سلوك Discord.
    - يجب أن تكون `spawnSubagentSessions` مساوية لـ true لإنشاء/ربط السلاسل تلقائيًا من أجل `sessions_spawn({ thread: true })`.
    - يجب أن تكون `spawnAcpSessions` مساوية لـ true لإنشاء/ربط السلاسل تلقائيًا من أجل ACP (`/acp spawn ... --thread ...` أو `sessions_spawn({ runtime: "acp", thread: true })`).
    - إذا كانت ارتباطات السلاسل معطلة لحساب ما، فلن تكون `/focus` وعمليات ارتباط السلاسل ذات الصلة متاحة.

    راجع [الوكلاء الفرعيون](/ar/tools/subagents) و[وكلاء ACP](/ar/tools/acp-agents) و[مرجع الإعدادات](/ar/gateway/configuration-reference).

  </Accordion>

  <Accordion title="ارتباطات قنوات ACP الدائمة">
    بالنسبة لمساحات عمل ACP المستقرة "الدائمة التشغيل"، اضبط ارتباطات ACP مكتوبة على المستوى الأعلى تستهدف محادثات Discord.

    مسار الإعدادات:

    - `bindings[]` مع `type: "acp"` و`match.channel: "discord"`

    مثال:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": {
              requireMention: false,
            },
          },
        },
      },
    },
  },
}
```

    ملاحظات:

    - يقوم `/acp spawn codex --bind here` بربط قناة أو سلسلة Discord الحالية في مكانها ويُبقي الرسائل المستقبلية موجّهة إلى جلسة ACP نفسها.
    - قد يعني ذلك أيضًا "بدء جلسة Codex ACP جديدة"، لكنه لا ينشئ سلسلة Discord جديدة بحد ذاته. تظل القناة الحالية هي سطح الدردشة.
    - قد يستمر Codex في العمل ضمن `cwd` أو مساحة عمل خلفية خاصة به على القرص. مساحة العمل هذه حالة وقت تشغيل وليست سلسلة Discord.
    - يمكن لرسائل السلاسل أن ترث ارتباط ACP الخاص بالقناة الأصلية.
    - في قناة أو سلسلة مرتبطة، يعيد `/new` و`/reset` ضبط جلسة ACP نفسها في مكانها.
    - لا تزال ارتباطات السلاسل المؤقتة تعمل ويمكنها تجاوز تحليل الهدف أثناء نشاطها.
    - تكون `spawnAcpSessions` مطلوبة فقط عندما يحتاج OpenClaw إلى إنشاء/ربط سلسلة فرعية عبر `--thread auto|here`. وهي غير مطلوبة لـ `/acp spawn ... --bind here` في القناة الحالية.

    راجع [وكلاء ACP](/ar/tools/acp-agents) لتفاصيل سلوك الارتباط.

  </Accordion>

  <Accordion title="إشعارات التفاعلات">
    وضع إشعارات التفاعلات لكل خادم جماعي:

    - `off`
    - `own` (افتراضي)
    - `all`
    - `allowlist` (يستخدم `guilds.<id>.users`)

    تتحول أحداث التفاعلات إلى أحداث نظام وتُرفق بجلسة Discord الموجّهة.

  </Accordion>

  <Accordion title="تفاعلات التأكيد">
    يرسل `ackReaction` رمزًا تعبيريًا للتأكيد بينما يعالج OpenClaw رسالة واردة.

    ترتيب التحليل:

    - `channels.discord.accounts.<accountId>.ackReaction`
    - `channels.discord.ackReaction`
    - `messages.ackReaction`
    - بديل رمز الهوية الخاص بالوكيل (`agents.list[].identity.emoji`، وإلا `"👀"`)

    ملاحظات:

    - يقبل Discord الرموز التعبيرية الموحّدة أو أسماء الرموز التعبيرية المخصصة.
    - استخدم `""` لتعطيل التفاعل لقناة أو حساب.

  </Accordion>

  <Accordion title="كتابات الإعدادات">
    تكون كتابات الإعدادات التي تبدأ من القناة مفعلة افتراضيًا.

    يؤثر هذا في تدفقات `/config set|unset` (عندما تكون ميزات الأوامر مفعلة).

    التعطيل:

```json5
{
  channels: {
    discord: {
      configWrites: false,
    },
  },
}
```

  </Accordion>

  <Accordion title="وكيل البوابة">
    وجّه حركة WebSocket الخاصة ببوابة Discord وعمليات REST الأولية عند بدء التشغيل (معرّف التطبيق + تحليل قائمة السماح) عبر وكيل HTTP(S) باستخدام `channels.discord.proxy`.

```json5
{
  channels: {
    discord: {
      proxy: "http://proxy.example:8080",
    },
  },
}
```

    تجاوز لكل حساب:

```json5
{
  channels: {
    discord: {
      accounts: {
        primary: {
          proxy: "http://proxy.example:8080",
        },
      },
    },
  },
}
```

  </Accordion>

  <Accordion title="دعم PluralKit">
    فعّل تحليل PluralKit لربط الرسائل الممررة بهوية عضو النظام:

```json5
{
  channels: {
    discord: {
      pluralkit: {
        enabled: true,
        token: "pk_live_...", // اختياري؛ مطلوب للأنظمة الخاصة
      },
    },
  },
}
```

    ملاحظات:

    - يمكن لقوائم السماح استخدام `pk:<memberId>`
    - تتم مطابقة أسماء عرض الأعضاء حسب الاسم/slug فقط عندما تكون `channels.discord.dangerouslyAllowNameMatching: true`
    - تستخدم عمليات البحث معرّف الرسالة الأصلي وهي مقيّدة بنافذة زمنية
    - إذا فشل البحث، فستُعامل الرسائل الممررة كرسائل بوت ويتم إسقاطها ما لم يكن `allowBots=true`

  </Accordion>

  <Accordion title="إعدادات الحالة">
    تُطبَّق تحديثات الحالة عندما تضبط حقل حالة أو نشاط، أو عندما تفعّل الحالة التلقائية.

    مثال للحالة فقط:

```json5
{
  channels: {
    discord: {
      status: "idle",
    },
  },
}
```

    مثال للنشاط (الحالة المخصصة هي نوع النشاط الافتراضي):

```json5
{
  channels: {
    discord: {
      activity: "Focus time",
      activityType: 4,
    },
  },
}
```

    مثال للبث:

```json5
{
  channels: {
    discord: {
      activity: "Live coding",
      activityType: 1,
      activityUrl: "https://twitch.tv/openclaw",
    },
  },
}
```

    خريطة أنواع النشاط:

    - 0: Playing
    - 1: Streaming (يتطلب `activityUrl`)
    - 2: Listening
    - 3: Watching
    - 4: Custom (يستخدم نص النشاط كحالة الحالة؛ والرمز التعبيري اختياري)
    - 5: Competing

    مثال للحالة التلقائية (إشارة صحة وقت التشغيل):

```json5
{
  channels: {
    discord: {
      autoPresence: {
        enabled: true,
        intervalMs: 30000,
        minUpdateIntervalMs: 15000,
        exhaustedText: "token exhausted",
      },
    },
  },
}
```

    تقوم الحالة التلقائية بربط توفر وقت التشغيل بحالة Discord: healthy => online، وdegraded أو unknown => idle، وexhausted أو unavailable => dnd. تجاوزات النص الاختيارية:

    - `autoPresence.healthyText`
    - `autoPresence.degradedText`
    - `autoPresence.exhaustedText` (يدعم العنصر النائب `{reason}`)

  </Accordion>

  <Accordion title="الموافقات في Discord">
    يدعم Discord معالجة الموافقات المستندة إلى الأزرار في الرسائل الخاصة، ويمكنه اختياريًا نشر مطالبات الموافقة في القناة الأصلية.

    مسار الإعدادات:

    - `channels.discord.execApprovals.enabled`
    - `channels.discord.execApprovals.approvers` (اختياري؛ يعود إلى `commands.ownerAllowFrom` عندما يكون ذلك ممكنًا)
    - `channels.discord.execApprovals.target` (`dm` | `channel` | `both`، الافتراضي: `dm`)
    - `agentFilter` و`sessionFilter` و`cleanupAfterResolve`

    يفعّل Discord موافقات التنفيذ الأصلية تلقائيًا عندما تكون `enabled` غير مضبوطة أو تساوي `"auto"` ويمكن تحليل معتمد واحد على الأقل، إما من `execApprovals.approvers` أو من `commands.ownerAllowFrom`. لا يستنتج Discord معتمدي التنفيذ من `allowFrom` الخاص بالقناة أو `dm.allowFrom` القديم أو `defaultTo` للرسائل المباشرة. اضبط `enabled: false` لتعطيل Discord كعميل موافقات أصلي صراحةً.

    عندما تكون `target` هي `channel` أو `both`، تكون مطالبة الموافقة مرئية في القناة. ويمكن فقط للمعتمدين الذين تم تحليلهم استخدام الأزرار؛ أما المستخدمون الآخرون فيتلقون رفضًا مؤقتًا. تتضمن مطالبات الموافقة نص الأمر، لذا فعّل التسليم إلى القناة فقط في القنوات الموثوقة. وإذا تعذر اشتقاق معرّف القناة من مفتاح الجلسة، يعود OpenClaw إلى التسليم عبر الرسائل الخاصة.

    يعرض Discord أيضًا أزرار الموافقة المشتركة المستخدمة من قِبل قنوات الدردشة الأخرى. يضيف محول Discord الأصلي أساسًا توجيه الرسائل الخاصة للمعتمدين والتوزيع إلى القناة.
    وعندما تكون هذه الأزرار موجودة، فإنها تكون تجربة الموافقة الأساسية؛ لذا
    يجب على OpenClaw أن يتضمن أمر `/approve` يدويًا فقط عندما تشير نتيجة الأداة إلى
    أن موافقات الدردشة غير متاحة أو أن الموافقة اليدوية هي المسار الوحيد.

    تستخدم مصادقة البوابة لهذا المعالج نفس عقد تحليل بيانات الاعتماد المشترك مثل عملاء البوابة الآخرين:

    - مصادقة محلية تبدأ من env (`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD` ثم `gateway.auth.*`)
    - في الوضع المحلي، يمكن استخدام `gateway.remote.*` كبديل فقط عندما لا يكون `gateway.auth.*` مضبوطًا؛ أما SecretRefs المحلية المضبوطة ولكن غير المحلولة فتفشل بشكل مغلق
    - دعم الوضع البعيد عبر `gateway.remote.*` عند الاقتضاء
    - تجاوزات URL آمنة للتجاوز: تجاوزات CLI لا تعيد استخدام بيانات الاعتماد الضمنية، وتجاوزات env تستخدم بيانات اعتماد env فقط

    سلوك تحليل الموافقة:

    - يتم تحليل المعرّفات التي تبدأ بـ `plugin:` عبر `plugin.approval.resolve`.
    - يتم تحليل المعرّفات الأخرى عبر `exec.approval.resolve`.
    - لا يجري Discord هنا قفزة بديلة إضافية من exec إلى plugin؛ إذ يحدد
      بادئة المعرّف طريقة البوابة التي يستدعيها.

    تنتهي موافقات التنفيذ افتراضيًا بعد 30 دقيقة. إذا فشلت الموافقات مع
    معرّفات موافقة غير معروفة، فتحقق من تحليل المعتمدين وتمكين الميزة
    وأن نوع معرّف الموافقة المُسلَّم يطابق الطلب المعلّق.

    المستندات ذات الصلة: [موافقات التنفيذ](/ar/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## الأدوات وبوابات الإجراءات

تتضمن إجراءات رسائل Discord المراسلة وإدارة القنوات والإشراف والحالة وإجراءات البيانات الوصفية.

أمثلة أساسية:

- المراسلة: `sendMessage` و`readMessages` و`editMessage` و`deleteMessage` و`threadReply`
- التفاعلات: `react` و`reactions` و`emojiList`
- الإشراف: `timeout` و`kick` و`ban`
- الحالة: `setPresence`

يقبل الإجراء `event-create` معامل `image` اختياريًا (URL أو مسار ملف محلي) لتعيين صورة غلاف الحدث المجدول.

توجد بوابات الإجراءات تحت `channels.discord.actions.*`.

السلوك الافتراضي للبوابات:

| Action group                                                                                                                                                             | Default  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| reactions, messages, threads, pins, polls, search, memberInfo, roleInfo, channelInfo, channels, voiceStatus, events, stickers, emojiUploads, stickerUploads, permissions | مفعّل  |
| roles                                                                                                                                                                    | معطّل |
| moderation                                                                                                                                                               | معطّل |
| presence                                                                                                                                                                 | معطّل |

## واجهة Components v2

يستخدم OpenClaw Discord components v2 لموافقات التنفيذ وعلامات السياق المتقاطع. ويمكن أيضًا لإجراءات رسائل Discord قبول `components` لواجهة مستخدم مخصصة (متقدم؛ يتطلب إنشاء حمولة مكونات عبر أداة discord)، بينما لا تزال `embeds` القديمة متاحة لكنها غير موصى بها.

- يضبط `channels.discord.ui.components.accentColor` لون التمييز المستخدم بواسطة حاويات مكونات Discord (ست عشري).
- اضبطه لكل حساب باستخدام `channels.discord.accounts.<id>.ui.components.accentColor`.
- يتم تجاهل `embeds` عندما تكون مكونات v2 موجودة.

مثال:

```json5
{
  channels: {
    discord: {
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
    },
  },
}
```

## القنوات الصوتية

يمكن لـ OpenClaw الانضمام إلى القنوات الصوتية في Discord لمحادثات آنية ومستمرة. وهذا منفصل عن مرفقات الرسائل الصوتية.

المتطلبات:

- فعّل الأوامر الأصلية (`commands.native` أو `channels.discord.commands.native`).
- اضبط `channels.discord.voice`.
- يحتاج البوت إلى أذونات Connect + Speak في القناة الصوتية المستهدفة.

استخدم الأمر الأصلي الخاص بـ Discord فقط `/vc join|leave|status` للتحكم في الجلسات. يستخدم الأمر الوكيل الافتراضي للحساب ويتبع نفس قواعد قائمة السماح والسياسة الجماعية مثل أوامر Discord الأخرى.

مثال على الانضمام التلقائي:

```json5
{
  channels: {
    discord: {
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
    },
  },
}
```

ملاحظات:

- يتجاوز `voice.tts` القيمة `messages.tts` لتشغيل الصوت فقط.
- تستمد دورات النسخ الصوتي حالة المالك من `allowFrom` في Discord (أو `dm.allowFrom`)؛ ولا يمكن للمتحدثين غير المالكين الوصول إلى الأدوات الخاصة بالمالك فقط (مثل `gateway` و`cron`).
- تكون الميزة الصوتية مفعلة افتراضيًا؛ اضبط `channels.discord.voice.enabled=false` لتعطيلها.
- يتم تمرير `voice.daveEncryption` و`voice.decryptionFailureTolerance` إلى خيارات الانضمام في `@discordjs/voice`.
- القيم الافتراضية في `@discordjs/voice` هي `daveEncryption=true` و`decryptionFailureTolerance=24` إذا لم يتم ضبطها.
- يراقب OpenClaw أيضًا فشل فك التشفير عند الاستقبال ويستعيد الحالة تلقائيًا عبر المغادرة/إعادة الانضمام إلى القناة الصوتية بعد حالات الفشل المتكررة خلال نافذة قصيرة.
- إذا كانت سجلات الاستقبال تعرض مرارًا `DecryptionFailed(UnencryptedWhenPassthroughDisabled)`، فقد يكون هذا الخطأ المرتبط بالاستقبال في `@discordjs/voice` والمتتبع في [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419).

## الرسائل الصوتية

تعرض الرسائل الصوتية في Discord معاينة شكل موجة وتتطلب صوت OGG/Opus بالإضافة إلى بيانات وصفية. ينشئ OpenClaw شكل الموجة تلقائيًا، لكنه يحتاج إلى توفر `ffmpeg` و`ffprobe` على مضيف البوابة لفحص الملفات الصوتية وتحويلها.

المتطلبات والقيود:

- قدّم **مسار ملف محليًا** (يتم رفض عناوين URL).
- احذف المحتوى النصي (لا يسمح Discord بالنص + الرسالة الصوتية في الحمولة نفسها).
- يُقبل أي تنسيق صوتي؛ ويحوّل OpenClaw الملف إلى OGG/Opus عند الحاجة.

مثال:

```bash
message(action="send", channel="discord", target="channel:123", path="/path/to/audio.mp3", asVoice=true)
```

## استكشاف الأخطاء وإصلاحها

<AccordionGroup>
  <Accordion title="استخدمت امتيازات غير مسموح بها أو أن البوت لا يرى رسائل الخادم الجماعي">

    - فعّل Message Content Intent
    - فعّل Server Members Intent عندما تعتمد على تحليل المستخدم/العضو
    - أعد تشغيل البوابة بعد تغيير الامتيازات

  </Accordion>

  <Accordion title="تم حظر رسائل الخادم الجماعي بشكل غير متوقع">

    - تحقّق من `groupPolicy`
    - تحقّق من قائمة سماح الخادم الجماعي تحت `channels.discord.guilds`
    - إذا كانت خريطة `channels` موجودة للخادم الجماعي، فستُسمح فقط القنوات المدرجة
    - تحقّق من سلوك `requireMention` وأنماط الإشارة

    فحوصات مفيدة:

```bash
openclaw doctor
openclaw channels status --probe
openclaw logs --follow
```

  </Accordion>

  <Accordion title="القيمة Require mention false ولكن ما زال الحظر قائمًا">
    الأسباب الشائعة:

    - `groupPolicy="allowlist"` من دون قائمة سماح مطابقة للخادم/القناة
    - تم ضبط `requireMention` في المكان الخطأ (يجب أن تكون تحت `channels.discord.guilds` أو إدخال القناة)
    - تم حظر المرسل بواسطة قائمة السماح `users` الخاصة بالخادم/القناة

  </Accordion>

  <Accordion title="تنتهي مهلة المعالجات طويلة التشغيل أو تتكرر الردود">

    السجلات النموذجية:

    - `Listener DiscordMessageListener timed out after 30000ms for event MESSAGE_CREATE`
    - `Slow listener detected ...`
    - `discord inbound worker timed out after ...`

    مفتاح ميزانية المستمع:

    - حساب واحد: `channels.discord.eventQueue.listenerTimeout`
    - حسابات متعددة: `channels.discord.accounts.<accountId>.eventQueue.listenerTimeout`

    مفتاح مهلة تشغيل العامل:

    - حساب واحد: `channels.discord.inboundWorker.runTimeoutMs`
    - حسابات متعددة: `channels.discord.accounts.<accountId>.inboundWorker.runTimeoutMs`
    - الافتراضي: `1800000` (30 دقيقة)؛ اضبط `0` لتعطيله

    خط أساس موصى به:

```json5
{
  channels: {
    discord: {
      accounts: {
        default: {
          eventQueue: {
            listenerTimeout: 120000,
          },
          inboundWorker: {
            runTimeoutMs: 1800000,
          },
        },
      },
    },
  },
}
```

    استخدم `eventQueue.listenerTimeout` لإعداد المستمع البطيء و`inboundWorker.runTimeoutMs`
    فقط إذا كنت تريد صمام أمان منفصلًا للدورات الوكيلة الموضوعة في قائمة الانتظار.

  </Accordion>

  <Accordion title="عدم تطابق في تدقيق الأذونات">
    تعمل فحوصات الأذونات في `channels status --probe` فقط مع معرّفات القنوات الرقمية.

    إذا استخدمت مفاتيح slug، فقد يظل التطابق في وقت التشغيل يعمل، لكن الفحص لا يمكنه التحقق الكامل من الأذونات.

  </Accordion>

  <Accordion title="مشكلات الرسائل الخاصة والإقران">

    - الرسائل الخاصة معطلة: `channels.discord.dm.enabled=false`
    - سياسة الرسائل الخاصة معطلة: `channels.discord.dmPolicy="disabled"` (القديم: `channels.discord.dm.policy`)
    - بانتظار الموافقة على الإقران في وضع `pairing`

  </Accordion>

  <Accordion title="حلقات البوت إلى البوت">
    افتراضيًا يتم تجاهل الرسائل التي يكتبها البوت.

    إذا قمت بضبط `channels.discord.allowBots=true`، فاستخدم قواعد صارمة للإشارة وقائمة السماح لتجنب سلوك الحلقات.
    فضّل `channels.discord.allowBots="mentions"` لقبول رسائل البوت التي تذكر البوت فقط.

  </Accordion>

  <Accordion title="تسقط STT الصوتية مع DecryptionFailed(...)">

    - أبقِ OpenClaw محدثًا (`openclaw update`) حتى يكون منطق استعادة استقبال الصوت في Discord موجودًا
    - أكّد أن `channels.discord.voice.daveEncryption=true` (افتراضي)
    - ابدأ من `channels.discord.voice.decryptionFailureTolerance=24` (القيمة الافتراضية upstream) واضبط فقط عند الحاجة
    - راقب السجلات بحثًا عن:
      - `discord voice: DAVE decrypt failures detected`
      - `discord voice: repeated decrypt failures; attempting rejoin`
    - إذا استمرت الأعطال بعد إعادة الانضمام التلقائية، فاجمع السجلات وقارنها مع [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419)

  </Accordion>
</AccordionGroup>

## مؤشرات مرجع الإعدادات

المرجع الأساسي:

- [مرجع الإعدادات - Discord](/ar/gateway/configuration-reference#discord)

حقول Discord عالية الأهمية:

- بدء التشغيل/المصادقة: `enabled` و`token` و`accounts.*` و`allowBots`
- السياسة: `groupPolicy` و`dm.*` و`guilds.*` و`guilds.*.channels.*`
- الأمر: `commands.native` و`commands.useAccessGroups` و`configWrites` و`slashCommand.*`
- قائمة انتظار الأحداث: `eventQueue.listenerTimeout` (ميزانية المستمع) و`eventQueue.maxQueueSize` و`eventQueue.maxConcurrency`
- العامل الوارد: `inboundWorker.runTimeoutMs`
- الرد/السجل: `replyToMode` و`historyLimit` و`dmHistoryLimit` و`dms.*.historyLimit`
- التسليم: `textChunkLimit` و`chunkMode` و`maxLinesPerMessage`
- البث: `streaming` (الاسم البديل القديم: `streamMode`) و`draftChunk` و`blockStreaming` و`blockStreamingCoalesce`
- الوسائط/إعادة المحاولة: `mediaMaxMb` و`retry`
  - يحدد `mediaMaxMb` الحد الأقصى لعمليات الرفع الصادرة إلى Discord (الافتراضي: `100MB`)
- الإجراءات: `actions.*`
- الحالة: `activity` و`status` و`activityType` و`activityUrl`
- واجهة المستخدم: `ui.components.accentColor`
- الميزات: `threadBindings` و`bindings[]` على المستوى الأعلى (`type: "acp"`) و`pluralkit` و`execApprovals` و`intents` و`agentComponents` و`heartbeat` و`responsePrefix`

## السلامة والعمليات

- تعامل مع رموز البوت المميزة كأسرار (يُفضّل `DISCORD_BOT_TOKEN` في البيئات الخاضعة للإشراف).
- امنح أقل أذونات Discord لازمة.
- إذا كانت حالة نشر الأوامر/الحالة قديمة، فأعد تشغيل البوابة وأعد التحقق باستخدام `openclaw channels status --probe`.

## ذو صلة

- [الإقران](/ar/channels/pairing)
- [المجموعات](/ar/channels/groups)
- [توجيه القنوات](/ar/channels/channel-routing)
- [الأمان](/ar/gateway/security)
- [التوجيه متعدد الوكلاء](/ar/concepts/multi-agent)
- [استكشاف الأخطاء وإصلاحها](/ar/channels/troubleshooting)
- [أوامر الشرطة المائلة](/ar/tools/slash-commands)
