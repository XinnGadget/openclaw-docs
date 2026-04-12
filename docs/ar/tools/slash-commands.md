---
read_when:
    - استخدام أو إعداد أوامر الدردشة
    - تصحيح توجيه الأوامر أو الأذونات
summary: 'أوامر الشرطة المائلة: النصية مقابل الأصلية، والإعدادات، والأوامر المدعومة'
title: أوامر الشرطة المائلة
x-i18n:
    generated_at: "2026-04-12T23:33:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9ef6f54500fa2ce3b873a8398d6179a0882b8bf6fba38f61146c64671055505e
    source_path: tools/slash-commands.md
    workflow: 15
---

# أوامر الشرطة المائلة

تتولى Gateway معالجة الأوامر. ويجب إرسال معظم الأوامر كرسالة **مستقلة** تبدأ بـ `/`.
ويستخدم أمر bash الخاص بالدردشة على المضيف فقط الصيغة `! <cmd>` ‏(مع `/bash <cmd>` كاسم بديل).

هناك نظامان مرتبطان:

- **الأوامر**: رسائل مستقلة بصيغة `/...`.
- **التوجيهات**: `/think` و`/fast` و`/verbose` و`/trace` و`/reasoning` و`/elevated` و`/exec` و`/model` و`/queue`.
  - تُزال التوجيهات من الرسالة قبل أن يراها النموذج.
  - في رسائل الدردشة العادية (وليست رسائل توجيه فقط)، تُعامل على أنها «تلميحات مضمّنة» ولا **تستمر** كإعدادات للجلسة.
  - في الرسائل التي تحتوي على توجيهات فقط (أي أن الرسالة تحتوي على توجيهات فقط)، فإنها تستمر في الجلسة وترد برسالة إقرار.
  - لا تُطبَّق التوجيهات إلا على **المرسلين المصرّح لهم**. إذا تم ضبط `commands.allowFrom`، فهو allowlist الوحيد
    المستخدم؛ وإلا فتأتي المصادقة من allowlists/الاقتران الخاصة بالقنوات بالإضافة إلى `commands.useAccessGroups`.
    أما المرسلون غير المصرّح لهم فيُعامل ما يرسلونه من توجيهات كنص عادي.

هناك أيضًا بعض **الاختصارات المضمّنة** (للمرسلين المدرجين في allowlist/المصرّح لهم فقط): `/help` و`/commands` و`/status` و`/whoami` ‏(`/id`).
تُشغَّل هذه فورًا، وتُزال قبل أن يراها النموذج، ويستمر النص المتبقي عبر المسار العادي.

## الإعدادات

```json5
{
  commands: {
    native: "auto",
    nativeSkills: "auto",
    text: true,
    bash: false,
    bashForegroundMs: 2000,
    config: false,
    mcp: false,
    plugins: false,
    debug: false,
    restart: true,
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw",
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- يفعّل `commands.text` ‏(الافتراضي `true`) تحليل `/...` في رسائل الدردشة.
  - في الأسطح التي لا تحتوي على أوامر أصلية (WhatsApp/WebChat/Signal/iMessage/Google Chat/Microsoft Teams)، تستمر الأوامر النصية في العمل حتى إذا ضبطت هذا الحقل على `false`.
- يسجّل `commands.native` ‏(الافتراضي `"auto"`) الأوامر الأصلية.
  - الوضع التلقائي: مفعّل لـ Discord/Telegram؛ ومعطّل لـ Slack (إلى أن تضيف slash commands)؛ ويتم تجاهله لدى المزوّدين الذين لا يدعمون الأوامر الأصلية.
  - اضبط `channels.discord.commands.native` أو `channels.telegram.commands.native` أو `channels.slack.commands.native` للتجاوز لكل مزوّد على حدة (قيمة منطقية أو `"auto"`).
  - تؤدي القيمة `false` إلى مسح الأوامر المسجّلة سابقًا على Discord/Telegram عند بدء التشغيل. أما أوامر Slack فتُدار داخل تطبيق Slack ولا تُزال تلقائيًا.
- يسجّل `commands.nativeSkills` ‏(الافتراضي `"auto"`) أوامر **Skills** بشكل أصلي عندما يكون ذلك مدعومًا.
  - الوضع التلقائي: مفعّل لـ Discord/Telegram؛ ومعطّل لـ Slack (يتطلب Slack إنشاء slash command لكل Skill).
  - اضبط `channels.discord.commands.nativeSkills` أو `channels.telegram.commands.nativeSkills` أو `channels.slack.commands.nativeSkills` للتجاوز لكل مزوّد على حدة (قيمة منطقية أو `"auto"`).
- يفعّل `commands.bash` ‏(الافتراضي `false`) الصيغة `! <cmd>` لتشغيل أوامر shell على المضيف (وتُعد `/bash <cmd>` اسمًا بديلًا؛ ويتطلب allowlists في `tools.elevated`).
- يتحكم `commands.bashForegroundMs` ‏(الافتراضي `2000`) في مدة انتظار bash قبل التبديل إلى وضع الخلفية (`0` يعني التشغيل في الخلفية فورًا).
- يفعّل `commands.config` ‏(الافتراضي `false`) الأمر `/config` ‏(لقراءة/كتابة `openclaw.json`).
- يفعّل `commands.mcp` ‏(الافتراضي `false`) الأمر `/mcp` ‏(لقراءة/كتابة إعدادات MCP التي يديرها OpenClaw تحت `mcp.servers`).
- يفعّل `commands.plugins` ‏(الافتراضي `false`) الأمر `/plugins` ‏(اكتشاف Plugins/حالته بالإضافة إلى عناصر التحكم في التثبيت + التفعيل/التعطيل).
- يفعّل `commands.debug` ‏(الافتراضي `false`) الأمر `/debug` ‏(تجاوزات وقت التشغيل فقط).
- يفعّل `commands.restart` ‏(الافتراضي `true`) الأمر `/restart` بالإضافة إلى إجراءات أداة إعادة تشغيل Gateway.
- يضبط `commands.ownerAllowFrom` ‏(اختياري) allowlist الصريح للمالك للأسطح الخاصة بالأوامر/الأدوات المخصّصة للمالك فقط. وهذا منفصل عن `commands.allowFrom`.
- يتحكم `commands.ownerDisplay` في كيفية ظهور معرّفات المالك في system prompt: ‏`raw` أو `hash`.
- يضبط `commands.ownerDisplaySecret` اختياريًا السرّ المستخدم في HMAC عندما تكون القيمة `commands.ownerDisplay="hash"`.
- يضبط `commands.allowFrom` ‏(اختياري) allowlist لكل مزوّد من أجل مصادقة الأوامر. وعند ضبطه، يصبح
  مصدر المصادقة الوحيد للأوامر والتوجيهات (ويتم تجاهل allowlists/الاقتران الخاصة بالقنوات و`commands.useAccessGroups`). استخدم `"*"` كقيمة افتراضية عامة؛ وتتجاوز المفاتيح الخاصة بالمزوّد هذه القيمة.
- يفرض `commands.useAccessGroups` ‏(الافتراضي `true`) allowlists/السياسات على الأوامر عندما لا يكون `commands.allowFrom` مضبوطًا.

## قائمة الأوامر

المصدر المرجعي الحالي:

- تأتي العناصر المدمجة الأساسية من `src/auto-reply/commands-registry.shared.ts`
- تأتي dock commands المولَّدة من `src/auto-reply/commands-registry.data.ts`
- تأتي أوامر Plugin من استدعاءات `registerCommand()` في Plugin
- وما يزال التوفر الفعلي على Gateway الخاص بك يعتمد على أعلام الإعدادات، وسطح القناة، والـ Plugins المثبّتة/المفعّلة

### الأوامر الأساسية المدمجة

الأوامر المدمجة المتاحة اليوم:

- يبدأ `/new [model]` جلسة جديدة؛ و`/reset` هو الاسم البديل لإعادة التعيين.
- يقوم `/compact [instructions]` بضغط سياق الجلسة. راجع [/concepts/compaction](/ar/concepts/compaction).
- يقوم `/stop` بإيقاف التشغيل الحالي.
- يدير `/session idle <duration|off>` و`/session max-age <duration|off>` انتهاء صلاحية ربط الخيط.
- يضبط `/think <off|minimal|low|medium|high|xhigh>` مستوى التفكير. الأسماء البديلة: `/thinking` و`/t`.
- يبدّل `/verbose on|off|full` الإخراج المطوّل. الاسم البديل: `/v`.
- يبدّل `/trace on|off` إخراج trace الخاص بـ Plugin للجلسة الحالية.
- يعرض `/fast [status|on|off]` الوضع السريع أو يضبطه.
- يبدّل `/reasoning [on|off|stream]` إظهار الاستدلال. الاسم البديل: `/reason`.
- يبدّل `/elevated [on|off|ask|full]` الوضع المرتفع. الاسم البديل: `/elev`.
- يعرض `/exec host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>` إعدادات exec الافتراضية أو يضبطها.
- يعرض `/model [name|#|status]` النموذج أو يضبطه.
- يسرد `/models [provider] [page] [limit=<n>|size=<n>|all]` المزوّدين أو النماذج الخاصة بمزوّد معيّن.
- يدير `/queue <mode>` سلوك الطابور (`steer` و`interrupt` و`followup` و`collect` و`steer-backlog`) بالإضافة إلى خيارات مثل `debounce:2s cap:25 drop:summarize`.
- يعرض `/help` ملخص المساعدة القصير.
- يعرض `/commands` كتالوج الأوامر المولَّد.
- يعرض `/tools [compact|verbose]` ما الذي يمكن للوكيل الحالي استخدامه الآن.
- يعرض `/status` حالة وقت التشغيل، بما في ذلك استخدام المزوّد/الحصة عند توفرها.
- يسرد `/tasks` المهام النشطة/الحديثة في الخلفية للجلسة الحالية.
- يشرح `/context [list|detail|json]` كيفية تجميع السياق.
- يصدّر `/export-session [path]` الجلسة الحالية إلى HTML. الاسم البديل: `/export`.
- يعرض `/whoami` معرّف المرسل الخاص بك. الاسم البديل: `/id`.
- يشغّل `/skill <name> [input]` Skill بالاسم.
- يدير `/allowlist [list|add|remove] ...` إدخالات allowlist. نصّي فقط.
- يحل `/approve <id> <decision>` مطالبات الموافقة على exec.
- يطرح `/btw <question>` سؤالًا جانبيًا من دون تغيير سياق الجلسة المستقبلي. راجع [/tools/btw](/ar/tools/btw).
- يدير `/subagents list|kill|log|info|send|steer|spawn` تشغيلات الوكلاء الفرعيين للجلسة الحالية.
- يدير `/acp spawn|cancel|steer|close|sessions|status|set-mode|set|cwd|permissions|timeout|model|reset-options|doctor|install|help` جلسات ACP وخيارات وقت التشغيل.
- يربط `/focus <target>` خيط Discord الحالي أو موضوع/محادثة Telegram بهدف جلسة.
- يزيل `/unfocus` الربط الحالي.
- يسرد `/agents` الوكلاء المرتبطين بالخيط للجلسة الحالية.
- يوقف `/kill <id|#|all>` وكيلًا فرعيًا واحدًا أو جميع الوكلاء الفرعيين الجاري تشغيلهم.
- يرسل `/steer <id|#> <message>` توجيهًا إلى وكيل فرعي قيد التشغيل. الاسم البديل: `/tell`.
- يقرأ `/config show|get|set|unset` الملف `openclaw.json` أو يكتبه. للمالك فقط. ويتطلب `commands.config: true`.
- يقرأ `/mcp show|get|set|unset` إعدادات خادم MCP التي يديرها OpenClaw تحت `mcp.servers` أو يكتبها. للمالك فقط. ويتطلب `commands.mcp: true`.
- يفحص `/plugins list|inspect|show|get|install|enable|disable` حالة Plugin أو يغيّرها. و`/plugin` اسم بديل. تكون عمليات الكتابة للمالك فقط. ويتطلب `commands.plugins: true`.
- يدير `/debug show|set|unset|reset` تجاوزات الإعدادات الخاصة بوقت التشغيل فقط. للمالك فقط. ويتطلب `commands.debug: true`.
- يتحكم `/usage off|tokens|full|cost` في تذييل الاستخدام لكل استجابة أو يطبع ملخص تكلفة محليًا.
- يتحكم `/tts on|off|status|provider|limit|summary|audio|help` في TTS. راجع [/tools/tts](/ar/tools/tts).
- يعيد `/restart` تشغيل OpenClaw عندما يكون مفعّلًا. الافتراضي: مفعّل؛ اضبط `commands.restart: false` لتعطيله.
- يضبط `/activation mention|always` وضع تنشيط المجموعة.
- يضبط `/send on|off|inherit` سياسة الإرسال. للمالك فقط.
- يشغّل `/bash <command>` أمر shell على المضيف. نصّي فقط. الاسم البديل: `! <command>`. ويتطلب `commands.bash: true` بالإضافة إلى allowlists في `tools.elevated`.
- يتحقق `!poll [sessionId]` من مهمة bash تعمل في الخلفية.
- يوقف `!stop [sessionId]` مهمة bash تعمل في الخلفية.

### dock commands المولّدة

يتم توليد Dock commands من Plugins القنوات التي تدعم الأوامر الأصلية. المجموعة المدمجة الحالية:

- `/dock-discord` ‏(الاسم البديل: `/dock_discord`)
- `/dock-mattermost` ‏(الاسم البديل: `/dock_mattermost`)
- `/dock-slack` ‏(الاسم البديل: `/dock_slack`)
- `/dock-telegram` ‏(الاسم البديل: `/dock_telegram`)

### أوامر Plugin المجمّعة

يمكن للـ Plugins المجمّعة إضافة مزيد من slash commands. أوامر الحزم المجمّعة الحالية في هذا المستودع:

- يبدّل `/dreaming [on|off|status|help]` Dreaming الخاص بالذاكرة. راجع [Dreaming](/ar/concepts/dreaming).
- يدير `/pair [qr|status|pending|approve|cleanup|notify]` تدفق الاقتران/الإعداد للجهاز. راجع [Pairing](/ar/channels/pairing).
- يقوم `/phone status|arm <camera|screen|writes|all> [duration]|disarm` بتسليح أوامر Node الخاصة بالهاتف عالية المخاطر مؤقتًا.
- يدير `/voice status|list [limit]|set <voiceId|name>` إعدادات صوت Talk. وفي Discord، يكون اسم الأمر الأصلي هو `/talkvoice`.
- يرسل `/card ...` إعدادات مسبقة للبطاقات الغنية في LINE. راجع [LINE](/ar/channels/line).
- يفحص `/codex status|models|threads|resume|compact|review|account|mcp|skills` ويضبط harness الخاص بخادم التطبيق Codex المجمّع. راجع [Codex Harness](/ar/plugins/codex-harness).
- أوامر خاصة بـ QQBot فقط:
  - `/bot-ping`
  - `/bot-version`
  - `/bot-help`
  - `/bot-upgrade`
  - `/bot-logs`

### أوامر Skills الديناميكية

يتم أيضًا عرض Skills التي يمكن للمستخدم استدعاؤها كأوامر slash:

- تعمل `/skill <name> [input]` دائمًا كنقطة الدخول العامة.
- قد تظهر Skills أيضًا كأوامر مباشرة مثل `/prose` عندما يسجّلها Skill/Plugin.
- يتحكم `commands.nativeSkills` و`channels.<provider>.commands.nativeSkills` في تسجيل أوامر Skills الأصلية.

ملاحظات:

- تقبل الأوامر وجود `:` اختياري بين الأمر والوسيطات (مثل: `/think: high` و`/send: on` و`/help:`).
- يقبل `/new <model>` اسمًا بديلًا للنموذج، أو `provider/model`، أو اسم مزوّد (مطابقة تقريبية)؛ وإذا لم توجد مطابقة، يُعامل النص على أنه نص الرسالة.
- للحصول على تفصيل كامل لاستخدام المزوّد، استخدم `openclaw status --usage`.
- يتطلب `/allowlist add|remove` القيمة `commands.config=true` ويلتزم بـ `configWrites` الخاصة بالقناة.
- في القنوات متعددة الحسابات، تلتزم أيضًا أوامر `/allowlist --account <id>` الموجهة للإعدادات وأوامر `/config set channels.<provider>.accounts.<id>...` بـ `configWrites` الخاصة بالحساب الهدف.
- يتحكم `/usage` في تذييل الاستخدام لكل استجابة؛ ويطبع `/usage cost` ملخص تكلفة محليًا من سجلات جلسات OpenClaw.
- يكون `/restart` مفعّلًا افتراضيًا؛ اضبط `commands.restart: false` لتعطيله.
- يقبل `/plugins install <spec>` مواصفات Plugin نفسها التي يقبلها `openclaw plugins install`: مسار/أرشيف محلي، أو حزمة npm، أو `clawhub:<pkg>`.
- يقوم `/plugins enable|disable` بتحديث إعدادات Plugin وقد يطالب بإعادة التشغيل.
- أمر أصلي خاص بـ Discord فقط: يتحكم `/vc join|leave|status` في القنوات الصوتية (يتطلب `channels.discord.voice` والأوامر الأصلية؛ وغير متاح كنص).
- تتطلب أوامر ربط الخيوط الخاصة بـ Discord (`/focus` و`/unfocus` و`/agents` و`/session idle` و`/session max-age`) أن تكون روابط الخيوط الفعالة مفعّلة (`session.threadBindings.enabled` و/أو `channels.discord.threadBindings.enabled`).
- مرجع أمر ACP وسلوك وقت التشغيل: [وكلاء ACP](/ar/tools/acp-agents).
- الغرض من `/verbose` هو تصحيح الأخطاء وزيادة الوضوح؛ أبقه **معطّلًا** في الاستخدام العادي.
- `/trace` أضيق من `/verbose`: فهو يكشف فقط أسطر trace/debug المملوكة للـ Plugin ويُبقي ضجيج الأدوات المطوّل العادي معطّلًا.
- يحفظ `/fast on|off` تجاوزًا على مستوى الجلسة. استخدم خيار `inherit` في واجهة Sessions لمسح هذا التجاوز والعودة إلى إعدادات الإعدادات الافتراضية.
- `/fast` خاص بالمزوّد: حيث تقوم OpenAI/OpenAI Codex بربطه إلى `service_tier=priority` على نقاط نهاية Responses الأصلية، بينما تقوم طلبات Anthropic العامة المباشرة، بما في ذلك الحركة الموثقة عبر OAuth المرسلة إلى `api.anthropic.com`، بربطه إلى `service_tier=auto` أو `standard_only`. راجع [OpenAI](/ar/providers/openai) و[Anthropic](/ar/providers/anthropic).
- ما تزال ملخصات فشل الأدوات تُعرض عند الاقتضاء، لكن نص الفشل التفصيلي لا يُضمَّن إلا عندما يكون `/verbose` على `on` أو `full`.
- تُعد `/reasoning` و`/verbose` و`/trace` محفوفة بالمخاطر في إعدادات المجموعات: فقد تكشف استدلالًا داخليًا أو مخرجات أدوات أو تشخيصات Plugin لم تكن تقصد كشفها. ويفضل تركها معطّلة، خاصة في محادثات المجموعات.
- يحفظ `/model` نموذج الجلسة الجديد فورًا.
- إذا كان الوكيل في وضع خمول، فسيستخدم التشغيل التالي هذا النموذج مباشرةً.
- إذا كان هناك تشغيل نشط بالفعل، فيضع OpenClaw التبديل المباشر في حالة انتظار ولا يعيد التشغيل إلى النموذج الجديد إلا عند نقطة إعادة محاولة نظيفة.
- إذا كان نشاط الأدوات أو إخراج الرد قد بدأ بالفعل، فقد يبقى التبديل المعلّق في الطابور حتى فرصة إعادة محاولة لاحقة أو حتى دور المستخدم التالي.
- **المسار السريع:** تُعالَج الرسائل التي تحتوي على أوامر فقط من مرسلين مدرجين في allowlist فورًا (تتجاوز الطابور + النموذج).
- **تقييد الإشارة في المجموعات:** تتجاوز الرسائل التي تحتوي على أوامر فقط من مرسلين مدرجين في allowlist متطلبات الإشارة.
- **الاختصارات المضمّنة (للمرسلين المدرجين في allowlist فقط):** تعمل بعض الأوامر أيضًا عند تضمينها داخل رسالة عادية وتُزال قبل أن يرى النموذج النص المتبقي.
  - مثال: `hey /status` يؤدي إلى رد حالة، ويستمر النص المتبقي عبر التدفق العادي.
- حاليًا: `/help` و`/commands` و`/status` و`/whoami` ‏(`/id`).
- يتم تجاهل الرسائل التي تحتوي على أوامر فقط من مرسلين غير مصرّح لهم بصمت، وتُعامل رموز `/...` المضمّنة كنص عادي.
- **أوامر Skills:** تُعرَض Skills القابلة للاستدعاء من المستخدم كأوامر slash. وتُنظَّف الأسماء إلى `a-z0-9_` ‏(بحد أقصى 32 حرفًا)؛ وتحصل التصادمات على لواحق رقمية (مثل `_2`).
  - يشغّل `/skill <name> [input]` Skill بالاسم (وهو مفيد عندما تمنع قيود الأوامر الأصلية وجود أوامر لكل Skill).
  - افتراضيًا، تُمرَّر أوامر Skills إلى النموذج كطلب عادي.
  - يمكن للـ Skills أن تصرّح اختياريًا بـ `command-dispatch: tool` لتوجيه الأمر مباشرةً إلى أداة (حتمي، من دون نموذج).
  - مثال: `/prose` ‏(Plugin OpenProse) — راجع [OpenProse](/ar/prose).
- **وسيطات الأوامر الأصلية:** يستخدم Discord الإكمال التلقائي للخيارات الديناميكية (وقوائم الأزرار عندما تحذف الوسيطات المطلوبة). بينما يعرض Telegram وSlack قائمة أزرار عندما يدعم الأمر خيارات وتحذف الوسيطة.

## `/tools`

يجيب `/tools` عن سؤال وقت تشغيل، وليس عن سؤال إعدادات: **ما الذي يمكن لهذا الوكيل استخدامه الآن
في هذه المحادثة**.

- يكون `/tools` الافتراضي مختصرًا ومحسّنًا للمسح السريع.
- يضيف `/tools verbose` أوصافًا قصيرة.
- توفر أسطح الأوامر الأصلية التي تدعم الوسيطات مفتاح الوضع نفسه بصيغة `compact|verbose`.
- تكون النتائج على نطاق الجلسة، لذلك فإن تغيير الوكيل أو القناة أو الخيط أو تفويض المرسل أو النموذج يمكن
  أن يغيّر المخرجات.
- يتضمن `/tools` الأدوات التي يمكن الوصول إليها فعليًا في وقت التشغيل، بما في ذلك الأدوات الأساسية، والأدوات المتصلة
  بالـ Plugin، والأدوات المملوكة للقناة.

لتحرير الملفات الشخصية والتجاوزات، استخدم لوحة Tools في Control UI أو أسطح الإعدادات/الكتالوج بدلًا
من التعامل مع `/tools` على أنه كتالوج ثابت.

## أسطح الاستخدام (ما الذي يظهر وأين)

- **استخدام/حصة المزوّد** (مثال: “Claude متبقٍ 80%”) يظهر في `/status` لمزوّد النموذج الحالي عندما يكون تتبع الاستخدام مفعّلًا. يطبّع OpenClaw نوافذ المزوّد إلى `% المتبقي`؛ وبالنسبة إلى MiniMax، يتم قلب حقول النسبة المئوية التي تعرض المتبقي فقط قبل العرض، كما أن استجابات `model_remains` تفضّل إدخال نموذج الدردشة بالإضافة إلى تسمية خطة موسومة باسم النموذج.
- يمكن لأسطر **الرموز/الذاكرة المؤقتة** في `/status` أن تعود إلى أحدث إدخال استخدام في النص المسجل عندما تكون لقطة الجلسة الحية متناثرة. وما تزال القيم الحية غير الصفرية الموجودة تفوز، ويمكن لهذا الرجوع إلى النص المسجل أيضًا استعادة تسمية نموذج وقت التشغيل النشط بالإضافة إلى إجمالي أكبر موجّه نحو الموجّه عندما تكون الإجماليات المخزنة مفقودة أو أصغر.
- يتم التحكم في **الرموز/التكلفة لكل استجابة** بواسطة `/usage off|tokens|full` ‏(وتُلحَق بالردود العادية).
- يتعلق `/model status` بـ **النماذج/المصادقة/نقاط النهاية**، وليس بالاستخدام.

## اختيار النموذج (`/model`)

يتم تنفيذ `/model` كتوجيه.

أمثلة:

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model opus@anthropic:default
/model status
```

ملاحظات:

- يعرض `/model` و`/model list` محددًا مرقمًا ومختصرًا (عائلة النموذج + المزوّدون المتاحون).
- في Discord، يفتح `/model` و`/models` محددًا تفاعليًا مع قوائم منسدلة للمزوّد والنموذج بالإضافة إلى خطوة Submit.
- يختار `/model <#>` من ذلك المحدد (ويفضّل المزوّد الحالي عندما يكون ذلك ممكنًا).
- يعرض `/model status` العرض التفصيلي، بما في ذلك نقطة نهاية المزوّد المهيأة (`baseUrl`) ووضع API ‏(`api`) عند توفرهما.

## تجاوزات التصحيح

يتيح لك `/debug` ضبط تجاوزات إعدادات **وقت تشغيل فقط** (في الذاكرة، وليس على القرص). للمالك فقط. وهو معطّل افتراضيًا؛ فعّله عبر `commands.debug: true`.

أمثلة:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

ملاحظات:

- تُطبَّق التجاوزات فورًا على قراءات الإعدادات الجديدة، لكنها **لا** تكتب إلى `openclaw.json`.
- استخدم `/debug reset` لمسح جميع التجاوزات والعودة إلى إعدادات القرص.

## مخرجات trace الخاصة بالـ Plugin

يتيح لك `/trace` تبديل **أسطر trace/debug الخاصة بالـ Plugin على نطاق الجلسة** من دون تشغيل الوضع المطوّل الكامل.

أمثلة:

```text
/trace
/trace on
/trace off
```

ملاحظات:

- يعرض `/trace` من دون وسيطة حالة trace الحالية للجلسة.
- يفعّل `/trace on` أسطر trace الخاصة بالـ Plugin للجلسة الحالية.
- يعطّل `/trace off` تلك الأسطر مرة أخرى.
- يمكن أن تظهر أسطر trace الخاصة بالـ Plugin في `/status` وكـرسالة تشخيص متابعة بعد رد المساعد العادي.
- لا يحل `/trace` محل `/debug`؛ فما يزال `/debug` يدير تجاوزات الإعدادات الخاصة بوقت التشغيل فقط.
- لا يحل `/trace` محل `/verbose`؛ فما تزال مخرجات الأدوات/الحالة المطوّلة العادية ضمن `/verbose`.

## تحديثات الإعدادات

يكتب `/config` إلى إعداداتك الموجودة على القرص (`openclaw.json`). للمالك فقط. وهو معطّل افتراضيًا؛ فعّله عبر `commands.config: true`.

أمثلة:

```
/config show
/config show messages.responsePrefix
/config get messages.responsePrefix
/config set messages.responsePrefix="[openclaw]"
/config unset messages.responsePrefix
```

ملاحظات:

- يتم التحقق من الإعدادات قبل الكتابة؛ وتُرفض التغييرات غير الصالحة.
- تستمر تحديثات `/config` عبر إعادة التشغيل.

## تحديثات MCP

يكتب `/mcp` تعريفات خوادم MCP التي يديرها OpenClaw تحت `mcp.servers`. للمالك فقط. وهو معطّل افتراضيًا؛ فعّله عبر `commands.mcp: true`.

أمثلة:

```text
/mcp show
/mcp show context7
/mcp set context7={"command":"uvx","args":["context7-mcp"]}
/mcp unset context7
```

ملاحظات:

- يخزّن `/mcp` الإعدادات في إعدادات OpenClaw، وليس في إعدادات المشروع التي يملكها Pi.
- تحدد محوّلات وقت التشغيل وسائل النقل القابلة للتنفيذ فعليًا.

## تحديثات Plugin

يتيح `/plugins` للمشغلين فحص Plugins المكتشفة وتبديل حالة تفعيلها في الإعدادات. ويمكن للمسارات للقراءة فقط استخدام `/plugin` كاسم بديل. وهو معطّل افتراضيًا؛ فعّله عبر `commands.plugins: true`.

أمثلة:

```text
/plugins
/plugins list
/plugin show context7
/plugins enable context7
/plugins disable context7
```

ملاحظات:

- تستخدم `/plugins list` و`/plugins show` اكتشاف Plugin الحقيقي مقابل مساحة العمل الحالية بالإضافة إلى الإعدادات الموجودة على القرص.
- يقوم `/plugins enable|disable` بتحديث إعدادات Plugin فقط؛ ولا يقوم بتثبيت Plugins أو إلغاء تثبيتها.
- بعد تغييرات التفعيل/التعطيل، أعد تشغيل Gateway لتطبيقها.

## ملاحظات الأسطح

- تعمل **الأوامر النصية** ضمن جلسة الدردشة العادية (تشارك الرسائل الخاصة الجلسة `main`، وتمتلك المجموعات جلستها الخاصة).
- تستخدم **الأوامر الأصلية** جلسات معزولة:
  - Discord: ‏`agent:<agentId>:discord:slash:<userId>`
  - Slack: ‏`agent:<agentId>:slack:slash:<userId>` ‏(البادئة قابلة للضبط عبر `channels.slack.slashCommand.sessionPrefix`)
  - Telegram: ‏`telegram:slash:<userId>` ‏(وتستهدف جلسة الدردشة عبر `CommandTargetSessionKey`)
- يستهدف **`/stop`** جلسة الدردشة النشطة حتى يتمكن من إيقاف التشغيل الحالي.
- **Slack:** ما يزال `channels.slack.slashCommand` مدعومًا لأمر واحد من نمط `/openclaw`. وإذا فعّلت `commands.native`، فيجب عليك إنشاء أمر slash واحد في Slack لكل أمر مدمج (بالأسماء نفسها مثل `/help`). وتُسلَّم قوائم وسيطات الأوامر في Slack على هيئة أزرار Block Kit مؤقتة.
  - استثناء أصلي في Slack: سجّل `/agentstatus` ‏(وليس `/status`) لأن Slack يحجز `/status`. وما يزال `/status` النصي يعمل في رسائل Slack.

## أسئلة BTW الجانبية

`/btw` هو **سؤال جانبي** سريع حول الجلسة الحالية.

وعلى خلاف الدردشة العادية:

- يستخدم الجلسة الحالية كسياق خلفي،
- ويعمل كاستدعاء منفصل **من دون أدوات** لمرة واحدة،
- ولا يغيّر سياق الجلسة المستقبلي،
- ولا يُكتب في سجل النص،
- ويُسلَّم كنتيجة جانبية حية بدلًا من رسالة مساعد عادية.

وهذا يجعل `/btw` مفيدًا عندما تريد توضيحًا مؤقتًا بينما
تستمر المهمة الأساسية.

مثال:

```text
/btw ماذا نفعل الآن؟
```

راجع [الأسئلة الجانبية BTW](/ar/tools/btw) للاطلاع على السلوك الكامل وتفاصيل
تجربة العميل.
