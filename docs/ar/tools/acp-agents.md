---
read_when:
    - تشغيل coding harnesses عبر ACP
    - إعداد جلسات ACP مرتبطة بالمحادثة على قنوات المراسلة
    - ربط محادثة قناة رسائل بجلسة ACP مستمرة
    - استكشاف أخطاء الواجهة الخلفية لـ ACP وتوصيل الإضافة وإصلاحها
    - تشغيل أوامر `/acp` من الدردشة
summary: استخدم جلسات وقت تشغيل ACP لـ Codex وClaude Code وCursor وGemini CLI وOpenClaw ACP ووكلاء harness آخرين
title: وكلاء ACP
x-i18n:
    generated_at: "2026-04-07T07:24:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb651ab39b05e537398623ee06cb952a5a07730fc75d3f7e0de20dd3128e72c6
    source_path: tools/acp-agents.md
    workflow: 15
---

# وكلاء ACP

تتيح جلسات [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) لـ OpenClaw تشغيل coding harnesses خارجية (مثل Pi، وClaude Code، وCodex، وCursor، وCopilot، وOpenClaw ACP، وOpenCode، وGemini CLI، وغيرها من harnesses المدعومة عبر ACPX) من خلال إضافة واجهة خلفية لـ ACP.

إذا طلبت من OpenClaw بلغة طبيعية "شغّل هذا في Codex" أو "ابدأ Claude Code في سلسلة محادثة"، فيجب على OpenClaw توجيه هذا الطلب إلى وقت تشغيل ACP (وليس وقت تشغيل الوكيل الفرعي الأصلي). يتم تتبع كل عملية spawn لجلسة ACP باعتبارها [مهمة في الخلفية](/ar/automation/tasks).

إذا كنت تريد أن يتصل Codex أو Claude Code كعميل MCP خارجي مباشرةً
بمحادثات قنوات OpenClaw الموجودة، فاستخدم [`openclaw mcp serve`](/cli/mcp)
بدلًا من ACP.

## أي صفحة أريد؟

هناك ثلاث واجهات متقاربة يسهل الخلط بينها:

| أنت تريد أن...                                                                     | استخدم هذا                              | ملاحظات                                                                                                       |
| ---------------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| تشغيل Codex أو Claude Code أو Gemini CLI أو harness خارجي آخر _عبر_ OpenClaw      | هذه الصفحة: وكلاء ACP                   | جلسات مرتبطة بالدردشة، و`/acp spawn`، و`sessions_spawn({ runtime: "acp" })`، والمهام الخلفية، وعناصر تحكم وقت التشغيل |
| عرض جلسة OpenClaw Gateway _كخادم_ ACP لمحرر أو عميل                              | [`openclaw acp`](/cli/acp)              | وضع الجسر. يتحدث IDE/العميل عبر ACP إلى OpenClaw عبر stdio/WebSocket                                          |
| إعادة استخدام AI CLI محلي كنموذج احتياطي نصي فقط                                  | [CLI Backends](/ar/gateway/cli-backends)   | ليس ACP. لا أدوات OpenClaw، ولا عناصر تحكم ACP، ولا وقت تشغيل harness                                         |

## هل يعمل هذا مباشرة؟

عادةً نعم.

- تأتي التثبيتات الجديدة الآن مع تفعيل إضافة وقت التشغيل المضمّنة `acpx` افتراضيًا.
- تفضّل الإضافة المضمّنة `acpx` الثنائية المثبتة والمثبت إصدارها محليًا ضمن الإضافة.
- عند بدء التشغيل، يفحص OpenClaw هذه الثنائية ويصلحها ذاتيًا عند الحاجة.
- ابدأ بـ `/acp doctor` إذا كنت تريد فحص جاهزية سريعًا.

ما الذي قد يحدث مع أول استخدام:

- قد يتم جلب مهايئ harness الهدف عند الطلب عبر `npx` في أول مرة تستخدم فيها ذلك الـ harness.
- يجب أن تكون مصادقة المورّد موجودة أيضًا على المضيف لذلك الـ harness.
- إذا لم يكن لدى المضيف وصول إلى npm/الشبكة، فقد تفشل عمليات الجلب الأولى للمهايئات إلى أن يتم تسخين الذاكرات المؤقتة مسبقًا أو تثبيت المهايئ بطريقة أخرى.

أمثلة:

- `/acp spawn codex`: يجب أن يكون OpenClaw جاهزًا لتمهيد `acpx`، لكن قد يظل مهايئ Codex ACP بحاجة إلى جلب أولي.
- `/acp spawn claude`: الأمر نفسه بالنسبة إلى مهايئ Claude ACP، بالإضافة إلى مصادقة Claude على ذلك المضيف.

## تدفق تشغيل سريع للمشغّل

استخدم هذا عندما تريد دليلًا عمليًا لأوامر `/acp`:

1. أنشئ جلسة:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. اعمل في المحادثة أو السلسلة المرتبطة (أو استهدف مفتاح تلك الجلسة صراحةً).
3. افحص حالة وقت التشغيل:
   - `/acp status`
4. اضبط خيارات وقت التشغيل حسب الحاجة:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. وجّه جلسة نشطة من دون استبدال السياق:
   - `/acp steer tighten logging and continue`
6. أوقف العمل:
   - `/acp cancel` (إيقاف الدور الحالي)، أو
   - `/acp close` (إغلاق الجلسة + إزالة الروابط)

## بدء سريع للبشر

أمثلة على طلبات طبيعية:

- "اربط قناة Discord هذه بـ Codex."
- "ابدأ جلسة Codex مستمرة في سلسلة هنا وأبقها مركزة."
- "شغّل هذا كجلسة Claude Code ACP لمرة واحدة ولخّص النتيجة."
- "اربط دردشة iMessage هذه بـ Codex واحتفظ بالمتابعات في مساحة العمل نفسها."
- "استخدم Gemini CLI لهذه المهمة في سلسلة، ثم احتفظ بالمتابعات في السلسلة نفسها."

ما الذي يجب أن يفعله OpenClaw:

1. اختيار `runtime: "acp"`.
2. حل هدف harness المطلوب (`agentId`، مثل `codex`).
3. إذا طُلب الربط بالمحادثة الحالية وكانت القناة النشطة تدعم ذلك، فاربط جلسة ACP بهذه المحادثة.
4. وإلا، إذا طُلب ربط سلسلة محادثة وكانت القناة الحالية تدعم ذلك، فاربط جلسة ACP بالسلسلة.
5. وجّه رسائل المتابعة المرتبطة إلى جلسة ACP نفسها حتى يتم إلغاء التركيز/الإغلاق/الانتهاء.

## ACP مقابل الوكلاء الفرعيين

استخدم ACP عندما تريد وقت تشغيل harness خارجيًا. واستخدم الوكلاء الفرعيين عندما تريد تشغيلات مفوّضة أصلية لـ OpenClaw.

| المجال         | جلسة ACP                                | تشغيل وكيل فرعي                   |
| -------------- | --------------------------------------- | --------------------------------- |
| وقت التشغيل    | إضافة واجهة خلفية لـ ACP (مثل acpx)     | وقت تشغيل الوكيل الفرعي الأصلي في OpenClaw |
| مفتاح الجلسة   | `agent:<agentId>:acp:<uuid>`            | `agent:<agentId>:subagent:<uuid>` |
| الأوامر الرئيسية | `/acp ...`                             | `/subagents ...`                  |
| أداة spawn     | `sessions_spawn` مع `runtime:"acp"`     | `sessions_spawn` (وقت التشغيل الافتراضي) |

راجع أيضًا [الوكلاء الفرعيون](/ar/tools/subagents).

## كيف يشغّل ACP ‏Claude Code

بالنسبة إلى Claude Code عبر ACP، تكون الطبقات كالتالي:

1. مستوى التحكم في جلسة OpenClaw ACP
2. إضافة وقت التشغيل المضمّنة `acpx`
3. مهايئ Claude ACP
4. آلية وقت التشغيل/الجلسة على جهة Claude

تمييز مهم:

- ACP Claude عبارة عن جلسة harness مع عناصر تحكم ACP، واستئناف الجلسة، وتتبع المهام في الخلفية، وإمكانية اختيارية للربط بالمحادثة/السلسلة.
- الواجهات الخلفية لـ CLI هي بيئات تشغيل احتياطية نصية فقط محلية ومنفصلة. راجع [CLI Backends](/ar/gateway/cli-backends).

بالنسبة إلى المشغّلين، القاعدة العملية هي:

- إذا كنت تريد `/acp spawn`، أو جلسات قابلة للربط، أو عناصر تحكم وقت التشغيل، أو عمل harness مستمرًا: استخدم ACP
- إذا كنت تريد احتياطيًا نصيًا محليًا بسيطًا عبر CLI الخام: استخدم الواجهات الخلفية لـ CLI

## الجلسات المرتبطة

### الربط بالمحادثة الحالية

استخدم `/acp spawn <harness> --bind here` عندما تريد أن تصبح المحادثة الحالية مساحة عمل ACP دائمة من دون إنشاء سلسلة فرعية.

السلوك:

- يواصل OpenClaw امتلاك نقل القناة، والمصادقة، والأمان، والتسليم.
- تُثبَّت المحادثة الحالية على مفتاح جلسة ACP الذي تم إنشاؤه.
- تُوجَّه رسائل المتابعة في تلك المحادثة إلى جلسة ACP نفسها.
- يعيد `/new` و`/reset` تعيين جلسة ACP المرتبطة نفسها في مكانها.
- يغلق `/acp close` الجلسة ويزيل ربط المحادثة الحالية.

ماذا يعني هذا عمليًا:

- يحافظ `--bind here` على سطح الدردشة نفسه. في Discord، تبقى القناة الحالية هي القناة الحالية.
- يمكن أن ينشئ `--bind here` مع ذلك جلسة ACP جديدة إذا كنت تبدأ عملًا جديدًا. يقوم الربط بإلحاق تلك الجلسة بالمحادثة الحالية.
- لا ينشئ `--bind here` سلسلة Discord فرعية أو موضوع Telegram بحد ذاته.
- يمكن لوقت تشغيل ACP مع ذلك أن يملك دليل عمل خاصًا به (`cwd`) أو مساحة عمل على القرص يديرها backend. تكون مساحة عمل وقت التشغيل هذه منفصلة عن سطح الدردشة ولا تعني وجود سلسلة رسائل جديدة.
- إذا أجريت spawn إلى وكيل ACP مختلف ولم تمرر `--cwd`، فسيرث OpenClaw مساحة عمل **الوكيل الهدف** افتراضيًا، وليس مساحة عمل طالب الطلب.
- إذا كان مسار مساحة العمل الموروثة هذا مفقودًا (`ENOENT`/`ENOTDIR`)، فسيعود OpenClaw إلى `cwd` الافتراضي للواجهة الخلفية بدلًا من إعادة استخدام الشجرة الخاطئة بصمت.
- إذا كانت مساحة العمل الموروثة موجودة لكن لا يمكن الوصول إليها (مثل `EACCES`)، فستُرجع عملية spawn خطأ الوصول الحقيقي بدلًا من إسقاط `cwd`.

النموذج الذهني:

- سطح الدردشة: المكان الذي يواصل فيه الأشخاص الحديث (`Discord channel`، `Telegram topic`، `iMessage chat`)
- جلسة ACP: حالة وقت تشغيل Codex/Claude/Gemini الدائمة التي يوجّه إليها OpenClaw
- سلسلة/موضوع فرعي: سطح رسائل إضافي اختياري لا يُنشأ إلا بواسطة `--thread ...`
- مساحة عمل وقت التشغيل: موقع نظام الملفات الذي يعمل فيه الـ harness (`cwd`، نسخة المستودع المحلية، مساحة العمل التي تديرها الواجهة الخلفية)

أمثلة:

- `/acp spawn codex --bind here`: احتفظ بهذه الدردشة، وأنشئ أو أرفق جلسة Codex ACP، ووجّه الرسائل المستقبلية هنا إليها
- `/acp spawn codex --thread auto`: قد ينشئ OpenClaw سلسلة/موضوعًا فرعيًا ويربط جلسة ACP هناك
- `/acp spawn codex --bind here --cwd /workspace/repo`: نفس ربط الدردشة أعلاه، لكن Codex يعمل في `/workspace/repo`

دعم الربط بالمحادثة الحالية:

- يمكن لقنوات الدردشة/الرسائل التي تعلن دعم الربط بالمحادثة الحالية استخدام `--bind here` عبر مسار الربط المشترك للمحادثات.
- يمكن للقنوات ذات دلالات السلاسل/الموضوعات المخصصة مع ذلك توفير جعل معياري خاص بالقناة خلف الواجهة المشتركة نفسها.
- يعني `--bind here` دائمًا "اربط المحادثة الحالية في مكانها".
- تستخدم عمليات الربط العامة بالمحادثة الحالية مخزن الربط المشترك في OpenClaw وتبقى بعد عمليات إعادة تشغيل البوابة العادية.

ملاحظات:

- إن `--bind here` و `--thread ...` متنافيان في `/acp spawn`.
- في Discord، يربط `--bind here` القناة أو السلسلة الحالية في مكانها. لا تكون `spawnAcpSessions` مطلوبة إلا عندما يحتاج OpenClaw إلى إنشاء سلسلة فرعية من أجل `--thread auto|here`.
- إذا لم تكشف القناة النشطة روابط ACP للمحادثة الحالية، فسيُرجع OpenClaw رسالة واضحة بعدم الدعم.
- أسئلة `resume` و"جلسة جديدة" هي أسئلة خاصة بجلسة ACP، وليست أسئلة خاصة بالقناة. يمكنك إعادة استخدام حالة وقت التشغيل أو استبدالها من دون تغيير سطح الدردشة الحالي.

### الجلسات المرتبطة بالسلسلة

عندما تكون روابط السلاسل مفعّلة لمهايئ قناة، يمكن ربط جلسات ACP بالسلاسل:

- يربط OpenClaw سلسلةً بجلسة ACP مستهدفة.
- تُوجَّه رسائل المتابعة في تلك السلسلة إلى جلسة ACP المرتبطة.
- يُسلَّم خرج ACP إلى السلسلة نفسها.
- تؤدي عملية unfocus/close/archive/انتهاء المهلة عند الخمول أو انتهاء max-age إلى إزالة الربط.

يعتمد دعم ربط السلاسل على المهايئ. وإذا لم يكن مهايئ القناة النشطة يدعم روابط السلاسل، فسيُرجع OpenClaw رسالة واضحة بعدم الدعم/عدم التوفر.

أعلام الميزات المطلوبة لـ ACP المرتبط بالسلسلة:

- `acp.enabled=true`
- `acp.dispatch.enabled` مفعّل افتراضيًا (عيّنه إلى `false` لإيقاف توجيه ACP مؤقتًا)
- تمكين علم spawn الخاص بجلسات ACP في مهايئ القناة (بحسب المهايئ)
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### القنوات التي تدعم السلاسل

- أي مهايئ قناة يكشف قدرة ربط الجلسات/السلاسل.
- الدعم المضمّن الحالي:
  - سلاسل/قنوات Discord
  - موضوعات Telegram (موضوعات المنتدى في المجموعات/المجموعات الفائقة وموضوعات الرسائل المباشرة)
- يمكن لقنوات الإضافات إضافة الدعم عبر واجهة الربط نفسها.

## إعدادات خاصة بالقناة

بالنسبة إلى مسارات العمل غير المؤقتة، قم بتهيئة روابط ACP المستمرة في إدخالات `bindings[]` ذات المستوى الأعلى.

### نموذج الربط

- يحدد `bindings[].type="acp"` ربط محادثة ACP مستمر.
- يحدد `bindings[].match` المحادثة المستهدفة:
  - قناة أو سلسلة Discord: ‏`match.channel="discord"` + ‏`match.peer.id="<channelOrThreadId>"`
  - موضوع منتدى Telegram: ‏`match.channel="telegram"` + ‏`match.peer.id="<chatId>:topic:<topicId>"`
  - دردشة مباشرة/مجموعة BlueBubbles: ‏`match.channel="bluebubbles"` + ‏`match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    فضّل `chat_id:*` أو `chat_identifier:*` للروابط الجماعية المستقرة.
  - دردشة مباشرة/مجموعة iMessage: ‏`match.channel="imessage"` + ‏`match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    فضّل `chat_id:*` للروابط الجماعية المستقرة.
- `bindings[].agentId` هو معرّف وكيل OpenClaw المالك.
- توجد تجاوزات ACP الاختيارية تحت `bindings[].acp`:
  - `mode` ‏(`persistent` أو `oneshot`)
  - `label`
  - `cwd`
  - `backend`

### القيم الافتراضية لوقت التشغيل لكل وكيل

استخدم `agents.list[].runtime` لتعريف القيم الافتراضية لـ ACP مرة واحدة لكل وكيل:

- `agents.list[].runtime.type="acp"`
- `agents.list[].runtime.acp.agent` ‏(معرّف harness، مثل `codex` أو `claude`)
- `agents.list[].runtime.acp.backend`
- `agents.list[].runtime.acp.mode`
- `agents.list[].runtime.acp.cwd`

ترتيب أسبقية التجاوز للجلسات المرتبطة بـ ACP:

1. ‏`bindings[].acp.*`
2. ‏`agents.list[].runtime.acp.*`
3. القيم الافتراضية العامة لـ ACP ‏(مثل `acp.backend`)

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
      {
        id: "claude",
        runtime: {
          type: "acp",
          acp: { agent: "claude", backend: "acpx", mode: "persistent" },
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
    {
      type: "acp",
      agentId: "claude",
      match: {
        channel: "telegram",
        accountId: "default",
        peer: { kind: "group", id: "-1001234567890:topic:42" },
      },
      acp: { cwd: "/workspace/repo-b" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "discord", accountId: "default" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "telegram", accountId: "default" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": { requireMention: false },
          },
        },
      },
    },
    telegram: {
      groups: {
        "-1001234567890": {
          topics: { "42": { requireMention: false } },
        },
      },
    },
  },
}
```

السلوك:

- يضمن OpenClaw وجود جلسة ACP المهيأة قبل الاستخدام.
- تُوجَّه الرسائل في تلك القناة أو الموضوع إلى جلسة ACP المهيأة.
- في المحادثات المرتبطة، يعيد `/new` و`/reset` تعيين مفتاح جلسة ACP نفسه في مكانه.
- تظل روابط وقت التشغيل المؤقتة (مثل تلك التي تنشئها تدفقات التركيز على السلسلة) مطبّقة حيثما كانت موجودة.
- بالنسبة إلى عمليات spawn عبر وكلاء ACP من دون `cwd` صريح، يرث OpenClaw مساحة عمل الوكيل الهدف من إعدادات الوكيل.
- تعود مسارات مساحات العمل الموروثة المفقودة إلى `cwd` الافتراضي للواجهة الخلفية؛ أما إخفاقات الوصول إلى المسارات الموجودة فتظهر كأخطاء spawn.

## بدء جلسات ACP ‏(الواجهات)

### من `sessions_spawn`

استخدم `runtime: "acp"` لبدء جلسة ACP من دور وكيل أو استدعاء أداة.

```json
{
  "task": "Open the repo and summarize failing tests",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

ملاحظات:

- تكون القيمة الافتراضية لـ `runtime` هي `subagent`، لذا عيّن `runtime: "acp"` صراحةً لجلسات ACP.
- إذا حُذف `agentId`، يستخدم OpenClaw القيمة `acp.defaultAgent` إذا كانت مهيأة.
- يتطلب `mode: "session"` وجود `thread: true` للاحتفاظ بمحادثة مرتبطة مستمرة.

تفاصيل الواجهة:

- `task` ‏(مطلوب): المطالبة الأولية المرسلة إلى جلسة ACP.
- `runtime` ‏(مطلوب لـ ACP): يجب أن يكون `"acp"`.
- `agentId` ‏(اختياري): معرّف harness الهدف لـ ACP. يعود إلى `acp.defaultAgent` إذا كان مضبوطًا.
- `thread` ‏(اختياري، الافتراضي `false`): طلب تدفق ربط السلسلة عند الدعم.
- `mode` ‏(اختياري): ‏`run` ‏(مرة واحدة) أو `session` ‏(مستمر).
  - القيمة الافتراضية هي `run`
  - إذا كانت `thread: true` وحُذف `mode`، فقد يستخدم OpenClaw سلوكًا مستمرًا افتراضيًا بحسب مسار وقت التشغيل
  - يتطلب `mode: "session"` وجود `thread: true`
- `cwd` ‏(اختياري): دليل العمل المطلوب لوقت التشغيل (ويتحقق منه backend/سياسة وقت التشغيل). إذا حُذف، ترث عملية spawn لـ ACP مساحة عمل الوكيل الهدف عند تهيئتها؛ وتعود المسارات الموروثة المفقودة إلى القيم الافتراضية للواجهة الخلفية، بينما تُرجع أخطاء الوصول الحقيقية.
- `label` ‏(اختياري): تسمية موجهة للمشغّل تُستخدم في نص الجلسة/اللافتة.
- `resumeSessionId` ‏(اختياري): استئناف جلسة ACP موجودة بدلًا من إنشاء أخرى جديدة. يعيد الوكيل تشغيل سجل محادثاته عبر `session/load`. يتطلب `runtime: "acp"`.
- `streamTo` ‏(اختياري): تقوم القيمة `"parent"` ببث ملخصات تقدّم التشغيل الأولي لـ ACP إلى جلسة الطالب كأحداث نظام.
  - عند التوفر، قد تتضمن الاستجابات المقبولة `streamLogPath` الذي يشير إلى سجل JSONL ضمن نطاق الجلسة (`<sessionId>.acp-stream.jsonl`) يمكنك تتبعه لمعرفة سجل الترحيل الكامل.

### استئناف جلسة موجودة

استخدم `resumeSessionId` لمتابعة جلسة ACP سابقة بدلًا من البدء من جديد. يعيد الوكيل تشغيل سجل محادثته عبر `session/load`، لذلك يلتقط العمل مع السياق الكامل لما سبق.

```json
{
  "task": "Continue where we left off — fix the remaining test failures",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

حالات الاستخدام الشائعة:

- تسليم جلسة Codex من الكمبيوتر المحمول إلى الهاتف — اطلب من وكيلك متابعة العمل من حيث توقفت
- متابعة جلسة برمجة بدأتَها تفاعليًا في CLI، ولكن الآن بصورة غير تفاعلية عبر وكيلك
- متابعة عمل انقطع بسبب إعادة تشغيل البوابة أو انتهاء مهلة الخمول

ملاحظات:

- يتطلب `resumeSessionId` وجود `runtime: "acp"` — ويعيد خطأ إذا استُخدم مع وقت تشغيل الوكيل الفرعي.
- يستعيد `resumeSessionId` سجل المحادثة الأعلى مستوى لـ ACP؛ وما تزال `thread` و`mode` تطبقان بشكل طبيعي على جلسة OpenClaw الجديدة التي تنشئها، لذلك ما يزال `mode: "session"` يتطلب `thread: true`.
- يجب أن يدعم الوكيل الهدف `session/load` ‏(كل من Codex وClaude Code يدعمان ذلك).
- إذا لم يُعثر على معرّف الجلسة، تفشل عملية spawn برسالة خطأ واضحة — ولا يوجد تراجع صامت إلى جلسة جديدة.

### اختبار smoke للمشغّل

استخدم هذا بعد نشر البوابة عندما تريد فحصًا مباشرًا سريعًا يثبت أن spawn لـ ACP
يعمل فعليًا من طرف إلى طرف، وليس مجرد اجتياز اختبارات الوحدات.

البوابة الموصى بها:

1. تحقّق من إصدار/commit البوابة المنشورة على المضيف الهدف.
2. أكّد أن المصدر المنشور يتضمن قبول نسب ACP في
   `src/gateway/sessions-patch.ts` ‏(`subagent:* or acp:* sessions`).
3. افتح جلسة جسر ACPX مؤقتة إلى وكيل مباشر (مثل
   `razor(main)` على `jpclawhq`).
4. اطلب من ذلك الوكيل استدعاء `sessions_spawn` بالقيم التالية:
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - المهمة: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. تحقّق من أن الوكيل يبلّغ بما يلي:
   - `accepted=yes`
   - `childSessionKey` حقيقي
   - لا يوجد خطأ تحقق
6. نظّف جلسة جسر ACPX المؤقتة.

مثال على مطالبة إلى الوكيل المباشر:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

ملاحظات:

- أبقِ اختبار smoke هذا على `mode: "run"` ما لم تكن تختبر عمدًا
  جلسات ACP المستمرة المرتبطة بالسلسلة.
- لا تجعل `streamTo: "parent"` شرطًا لهذه البوابة الأساسية. فهذا المسار يعتمد على
  قدرات الجلسة/الطالب وهو فحص تكامل منفصل.
- تعامل مع اختبار `mode: "session"` المرتبط بالسلسلة باعتباره تمرير تكامل
  ثانيًا وأكثر غنى من سلسلة Discord حقيقية أو موضوع Telegram.

## توافق sandbox

تعمل جلسات ACP حاليًا على وقت تشغيل المضيف، وليس داخل sandbox في OpenClaw.

القيود الحالية:

- إذا كانت جلسة الطالب تعمل داخل sandbox، فسيتم حظر عمليات spawn الخاصة بـ ACP لكل من `sessions_spawn({ runtime: "acp" })` و`/acp spawn`.
  - الخطأ: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- لا يدعم `sessions_spawn` مع `runtime: "acp"` القيمة `sandbox: "require"`.
  - الخطأ: `sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

استخدم `runtime: "subagent"` عندما تحتاج إلى تنفيذ مفروض عبر sandbox.

### من أمر `/acp`

استخدم `/acp spawn` للتحكم الصريح من المشغّل من داخل الدردشة عند الحاجة.

```text
/acp spawn codex --mode persistent --thread auto
/acp spawn codex --mode oneshot --thread off
/acp spawn codex --bind here
/acp spawn codex --thread here
```

الأعلام الرئيسية:

- `--mode persistent|oneshot`
- `--bind here|off`
- `--thread auto|here|off`
- `--cwd <absolute-path>`
- `--label <name>`

راجع [أوامر الشرطة المائلة](/ar/tools/slash-commands).

## حل هدف الجلسة

تقبل معظم إجراءات `/acp` هدف جلسة اختياريًا (`session-key` أو `session-id` أو `session-label`).

ترتيب الحل:

1. وسيطة الهدف الصريحة (أو `--session` في `/acp steer`)
   - يحاول أولًا المفتاح
   - ثم معرّف جلسة على شكل UUID
   - ثم التسمية
2. ربط السلسلة الحالية (إذا كانت هذه المحادثة/السلسلة مرتبطة بجلسة ACP)
3. الرجوع إلى جلسة الطالب الحالية

تشارك روابط المحادثة الحالية وروابط السلاسل في الخطوة 2.

إذا تعذر حل أي هدف، فسيُرجع OpenClaw خطأ واضحًا (`Unable to resolve session target: ...`).

## أوضاع الربط عند spawn

يدعم `/acp spawn` ‏`--bind here|off`.

| الوضع  | السلوك                                                                |
| ------ | --------------------------------------------------------------------- |
| `here` | اربط المحادثة النشطة الحالية في مكانها؛ وافشل إذا لم تكن هناك محادثة نشطة. |
| `off`  | لا تنشئ ربطًا بالمحادثة الحالية.                                      |

ملاحظات:

- يُعد `--bind here` أبسط مسار للمشغّل لتحقيق "اجعل هذه القناة أو الدردشة مدعومة بـ Codex."
- لا ينشئ `--bind here` سلسلة فرعية.
- لا يتوفر `--bind here` إلا على القنوات التي تكشف دعم الربط بالمحادثة الحالية.
- لا يمكن الجمع بين `--bind` و`--thread` في الاستدعاء نفسه لـ `/acp spawn`.

## أوضاع السلسلة عند spawn

يدعم `/acp spawn` ‏`--thread auto|here|off`.

| الوضع  | السلوك                                                                                              |
| ------ | --------------------------------------------------------------------------------------------------- |
| `auto` | داخل سلسلة نشطة: اربط هذه السلسلة. خارج سلسلة: أنشئ/اربط سلسلة فرعية عند الدعم.                     |
| `here` | يتطلب سلسلة نشطة حالية؛ ويفشل إذا لم تكن داخل سلسلة.                                               |
| `off`  | لا يوجد ربط. تبدأ الجلسة من دون ربط.                                                               |

ملاحظات:

- على الأسطح التي لا تدعم ربط السلاسل، يكون السلوك الافتراضي فعليًا هو `off`.
- يتطلب spawn المرتبط بالسلسلة دعم سياسة القناة:
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- استخدم `--bind here` عندما تريد تثبيت المحادثة الحالية من دون إنشاء سلسلة فرعية.

## عناصر تحكم ACP

عائلة الأوامر المتاحة:

- `/acp spawn`
- `/acp cancel`
- `/acp steer`
- `/acp close`
- `/acp status`
- `/acp set-mode`
- `/acp set`
- `/acp cwd`
- `/acp permissions`
- `/acp timeout`
- `/acp model`
- `/acp reset-options`
- `/acp sessions`
- `/acp doctor`
- `/acp install`

يعرض `/acp status` خيارات وقت التشغيل الفعلية، وعند التوفر، يوضح كلًا من معرّفات الجلسات على مستوى وقت التشغيل وعلى مستوى الواجهة الخلفية.

تعتمد بعض عناصر التحكم على قدرات الواجهة الخلفية. وإذا لم تكن واجهة خلفية ما تدعم عنصر تحكم معينًا، فسيُرجع OpenClaw خطأً واضحًا يفيد بعدم دعم ذلك العنصر.

## كتاب وصفات أوامر ACP

| الأمر                | ما الذي يفعله                                               | مثال                                                         |
| -------------------- | ----------------------------------------------------------- | ------------------------------------------------------------ |
| `/acp spawn`         | إنشاء جلسة ACP؛ مع ربط اختياري بالحالية أو بالسلسلة.        | `/acp spawn codex --bind here --cwd /repo`                   |
| `/acp cancel`        | إلغاء الدور الجاري للجلسة الهدف.                           | `/acp cancel agent:codex:acp:<uuid>`                         |
| `/acp steer`         | إرسال توجيه إلى جلسة قيد التشغيل.                          | `/acp steer --session support inbox prioritize failing tests` |
| `/acp close`         | إغلاق الجلسة وفك ربط أهداف السلسلة.                        | `/acp close`                                                 |
| `/acp status`        | عرض الواجهة الخلفية، والوضع، والحالة، وخيارات وقت التشغيل، والقدرات. | `/acp status`                                                |
| `/acp set-mode`      | تعيين وضع وقت التشغيل للجلسة الهدف.                        | `/acp set-mode plan`                                         |
| `/acp set`           | كتابة عامة لخيار من خيارات إعداد وقت التشغيل.              | `/acp set model openai/gpt-5.4`                              |
| `/acp cwd`           | تعيين تجاوز دليل العمل لوقت التشغيل.                       | `/acp cwd /Users/user/Projects/repo`                         |
| `/acp permissions`   | تعيين ملف سياسة الموافقات.                                 | `/acp permissions strict`                                    |
| `/acp timeout`       | تعيين مهلة وقت التشغيل (بالثواني).                         | `/acp timeout 120`                                           |
| `/acp model`         | تعيين تجاوز نموذج وقت التشغيل.                             | `/acp model anthropic/claude-opus-4-6`                       |
| `/acp reset-options` | إزالة تجاوزات خيارات وقت التشغيل للجلسة.                    | `/acp reset-options`                                         |
| `/acp sessions`      | سرد جلسات ACP الحديثة من المخزن.                           | `/acp sessions`                                              |
| `/acp doctor`        | صحة الواجهة الخلفية، والقدرات، والإصلاحات القابلة للتنفيذ.  | `/acp doctor`                                                |
| `/acp install`       | طباعة خطوات تثبيت وتمكين حتمية.                             | `/acp install`                                               |

يقرأ `/acp sessions` المخزن للجلسة الحالية المرتبطة أو جلسة الطالب الحالية. وتحل الأوامر التي تقبل رموز `session-key` أو `session-id` أو `session-label` الأهداف عبر اكتشاف جلسات البوابة، بما في ذلك جذور `session.store` المخصصة لكل وكيل.

## ربط خيارات وقت التشغيل

يحتوي `/acp` على أوامر تسهيلية ومُعيّن عام.

العمليات المكافئة:

- يربط `/acp model <id>` بمفتاح إعداد وقت التشغيل `model`.
- يربط `/acp permissions <profile>` بمفتاح إعداد وقت التشغيل `approval_policy`.
- يربط `/acp timeout <seconds>` بمفتاح إعداد وقت التشغيل `timeout`.
- يحدّث `/acp cwd <path>` تجاوز `cwd` لوقت التشغيل مباشرة.
- يمثّل `/acp set <key> <value>` المسار العام.
  - حالة خاصة: إذا كان `key=cwd` فإنه يستخدم مسار تجاوز `cwd`.
- يمسح `/acp reset-options` كل تجاوزات وقت التشغيل للجلسة الهدف.

## دعم harness في acpx ‏(الحالي)

الأسماء المستعارة المضمّنة الحالية لـ harness في acpx:

- `claude`
- `codex`
- `copilot`
- `cursor` ‏(Cursor CLI: ‏`cursor-agent acp`)
- `droid`
- `gemini`
- `iflow`
- `kilocode`
- `kimi`
- `kiro`
- `openclaw`
- `opencode`
- `pi`
- `qwen`

عندما يستخدم OpenClaw الواجهة الخلفية acpx، ففضّل هذه القيم لـ `agentId` ما لم يحدد إعداد acpx لديك أسماء مستعارة مخصصة للوكلاء.
إذا كان تثبيت Cursor المحلي لديك ما يزال يعرض ACP على شكل `agent acp`، فقم بتجاوز أمر الوكيل `cursor` في إعداد acpx بدلًا من تغيير القيمة الافتراضية المضمّنة.

يمكن أيضًا لاستخدام acpx CLI المباشر استهداف مهايئات عشوائية عبر `--agent <command>`، لكن منفذ الهروب الخام هذا هو ميزة في acpx CLI (وليس المسار المعتاد لـ `agentId` في OpenClaw).

## الإعداد المطلوب

خط الأساس الأساسي لـ ACP:

```json5
{
  acp: {
    enabled: true,
    // اختياري. القيمة الافتراضية هي true؛ عيّن false لإيقاف توجيه ACP مؤقتًا مع الإبقاء على عناصر التحكم /acp.
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: [
      "claude",
      "codex",
      "copilot",
      "cursor",
      "droid",
      "gemini",
      "iflow",
      "kilocode",
      "kimi",
      "kiro",
      "openclaw",
      "opencode",
      "pi",
      "qwen",
    ],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

يكون إعداد ربط السلاسل خاصًا بمهايئ القناة. مثال لـ Discord:

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
        spawnAcpSessions: true,
      },
    },
  },
}
```

إذا لم يعمل spawn لـ ACP المرتبط بالسلسلة، فتحقق أولًا من علم الميزة في المهايئ:

- Discord: ‏`channels.discord.threadBindings.spawnAcpSessions=true`

لا تتطلب روابط المحادثة الحالية إنشاء سلسلة فرعية. لكنها تتطلب سياق محادثة نشطًا ومهايئ قناة يكشف روابط محادثات ACP.

راجع [مرجع الإعدادات](/ar/gateway/configuration-reference).

## إعداد الإضافة للواجهة الخلفية acpx

تأتي التثبيتات الجديدة مع تفعيل إضافة وقت التشغيل المضمّنة `acpx` افتراضيًا، لذا يعمل ACP
عادةً من دون خطوة تثبيت إضافة يدوية.

ابدأ بـ:

```text
/acp doctor
```

إذا كنت قد عطّلت `acpx`، أو رفضته عبر `plugins.allow` / `plugins.deny`، أو أردت
التحول إلى نسخة تطوير محلية، فاستخدم مسار الإضافة الصريح:

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

تثبيت مساحة عمل محلية أثناء التطوير:

```bash
openclaw plugins install ./path/to/local/acpx-plugin
```

ثم تحقق من صحة الواجهة الخلفية:

```text
/acp doctor
```

### إعداد أمر acpx والإصدار

افتراضيًا، تستخدم إضافة الواجهة الخلفية المضمّنة acpx ‏(`acpx`) الثنائية المثبتة إصدارًا محليًا ضمن الإضافة:

1. تكون القيمة الافتراضية للأمر هي `node_modules/.bin/acpx` المحلي ضمن حزمة إضافة ACPX.
2. تكون القيمة الافتراضية للإصدار المتوقع هي الإصدار المثبّت في الإضافة.
3. يسجل بدء التشغيل الواجهة الخلفية لـ ACP فورًا على أنها غير جاهزة.
4. تتحقق مهمة ensure في الخلفية من `acpx --version`.
5. إذا كانت الثنائية المحلية ضمن الإضافة مفقودة أو لا تطابق الإصدار، فيُشغِّل:
   `npm install --omit=dev --no-save acpx@<pinned>` ثم يعيد التحقق.

يمكنك تجاوز الأمر/الإصدار في إعداد الإضافة:

```json
{
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "command": "../acpx/dist/cli.js",
          "expectedVersion": "any"
        }
      }
    }
  }
}
```

ملاحظات:

- يقبل `command` مسارًا مطلقًا أو نسبيًا أو اسم أمر (`acpx`).
- تُحل المسارات النسبية انطلاقًا من دليل مساحة عمل OpenClaw.
- يؤدي `expectedVersion: "any"` إلى تعطيل المطابقة الصارمة للإصدار.
- عندما يشير `command` إلى ثنائية/مسار مخصص، يتم تعطيل التثبيت التلقائي المحلي ضمن الإضافة.
- يظل بدء تشغيل OpenClaw غير حاجز أثناء تنفيذ فحص صحة الواجهة الخلفية.

راجع [الإضافات](/ar/tools/plugin).

### التثبيت التلقائي للتبعيات

عند تثبيت OpenClaw عالميًا عبر `npm install -g openclaw`، تُثبَّت تبعيات وقت تشغيل acpx
(الثنائيات الخاصة بالمنصة) تلقائيًا
عبر خطاف postinstall. وإذا فشل التثبيت التلقائي، فستبدأ البوابة بشكل طبيعي
وتبلّغ عن التبعية المفقودة عبر `openclaw acp doctor`.

### جسر MCP لأدوات الإضافات

افتراضيًا، لا تعرض جلسات ACPX **أدوات** الإضافات المسجلة في OpenClaw إلى
ACP harness.

إذا كنت تريد أن تستدعي وكلاء ACP مثل Codex أو Claude Code أدوات
إضافات OpenClaw المثبتة مثل استدعاء/تخزين الذاكرة، ففعّل الجسر المخصص:

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

ما الذي يفعله هذا:

- يحقن خادم MCP مضمّنًا باسم `openclaw-plugin-tools` ضمن
  تمهيد جلسة ACPX.
- يكشف أدوات الإضافات المسجلة أصلًا بواسطة إضافات OpenClaw
  المثبتة والمفعّلة.
- يُبقي هذه الميزة صريحة ومعطّلة افتراضيًا.

ملاحظات الأمان والثقة:

- يوسّع هذا سطح أدوات ACP harness.
- لا يحصل وكلاء ACP إلا على أدوات الإضافات النشطة أصلًا في البوابة.
- تعامل مع هذا على أنه نفس حد الثقة الذي ينطبق على السماح لتلك الإضافات بالتنفيذ داخل
  OpenClaw نفسه.
- راجع الإضافات المثبتة قبل تفعيله.

تظل `mcpServers` المخصصة تعمل كما كانت من قبل. إن جسر أدوات الإضافات المضمّن هو
ميزة راحة إضافية اختيارية، وليس بديلًا عن إعداد خادم MCP العام.

## إعداد الأذونات

تعمل جلسات ACP بصورة غير تفاعلية — لا يوجد TTY للموافقة أو الرفض على مطالبات أذونات كتابة الملفات وتنفيذ shell. توفّر إضافة acpx مفتاحي إعداد يتحكمان في كيفية التعامل مع الأذونات:

هذه الأذونات الخاصة بـ ACPX harness منفصلة عن موافقات التنفيذ في OpenClaw ومنفصلة عن أعلام تجاوز المورّد في CLI-backend مثل Claude CLI ‏`--permission-mode bypassPermissions`. تمثل ACPX ‏`approve-all` مفتاح كسر الزجاج على مستوى harness لجلسات ACP.

### `permissionMode`

يتحكم في العمليات التي يمكن لوكيل harness تنفيذها من دون مطالبة.

| القيمة          | السلوك                                                   |
| --------------- | -------------------------------------------------------- |
| `approve-all`   | الموافقة التلقائية على جميع عمليات كتابة الملفات وأوامر shell. |
| `approve-reads` | الموافقة التلقائية على عمليات القراءة فقط؛ أما الكتابة والتنفيذ فتتطلبان مطالبات. |
| `deny-all`      | رفض جميع مطالبات الأذونات.                               |

### `nonInteractivePermissions`

يتحكم فيما يحدث عندما يفترض أن تظهر مطالبة أذونات ولكن لا يوجد TTY تفاعلي متاح (وهو الحال دائمًا بالنسبة إلى جلسات ACP).

| القيمة | السلوك                                                             |
| ------ | ------------------------------------------------------------------ |
| `fail` | إجهاض الجلسة مع `AcpRuntimeError`. **(الافتراضي)**                 |
| `deny` | رفض الإذن بصمت والمتابعة (تراجع سلس).                             |

### الإعداد

قم بالتعيين عبر إعداد الإضافة:

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

أعد تشغيل البوابة بعد تغيير هذه القيم.

> **مهم:** يستخدم OpenClaw حاليًا القيم الافتراضية `permissionMode=approve-reads` و`nonInteractivePermissions=fail`. وفي جلسات ACP غير التفاعلية، يمكن أن تفشل أي عملية كتابة أو تنفيذ تؤدي إلى مطالبة إذن بالخطأ `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`.
>
> إذا كنت بحاجة إلى تقييد الأذونات، فعيّن `nonInteractivePermissions` إلى `deny` حتى تتراجع الجلسات بسلاسة بدلًا من أن تتعطل.

## استكشاف الأخطاء وإصلاحها

| العرض                                                                      | السبب المحتمل                                                                    | الإصلاح                                                                                                                                                              |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured`                                    | إضافة الواجهة الخلفية مفقودة أو معطّلة.                                          | ثبّت إضافة الواجهة الخلفية وفعّلها، ثم شغّل `/acp doctor`.                                                                                                          |
| `ACP is disabled by policy (acp.enabled=false)`                            | تم تعطيل ACP عالميًا.                                                            | عيّن `acp.enabled=true`.                                                                                                                                             |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)`          | تم تعطيل التوجيه من رسائل السلاسل العادية.                                       | عيّن `acp.dispatch.enabled=true`.                                                                                                                                    |
| `ACP agent "<id>" is not allowed by policy`                                | الوكيل غير موجود في قائمة السماح.                                                 | استخدم `agentId` مسموحًا به أو حدّث `acp.allowedAgents`.                                                                                                            |
| `Unable to resolve session target: ...`                                    | رمز مفتاح/معرّف/تسمية غير صحيح.                                                  | شغّل `/acp sessions`، وانسخ المفتاح/التسمية بدقة، ثم أعد المحاولة.                                                                                                  |
| `--bind here requires running /acp spawn inside an active ... conversation` | استُخدم `--bind here` من دون محادثة نشطة قابلة للربط.                            | انتقل إلى الدردشة/القناة المستهدفة وأعد المحاولة، أو استخدم spawn غير مرتبط.                                                                                        |
| `Conversation bindings are unavailable for <channel>.`                     | لا يملك المهايئ قدرة ربط ACP بالمحادثة الحالية.                                   | استخدم `/acp spawn ... --thread ...` عند الدعم، أو هيئ `bindings[]` على المستوى الأعلى، أو انتقل إلى قناة مدعومة.                                                 |
| `--thread here requires running /acp spawn inside an active ... thread`    | استُخدم `--thread here` خارج سياق سلسلة.                                          | انتقل إلى السلسلة المستهدفة أو استخدم `--thread auto`/`off`.                                                                                                        |
| `Only <user-id> can rebind this channel/conversation/thread.`              | يمتلك مستخدم آخر هدف الربط النشط.                                                | أعد الربط بصفتك المالك أو استخدم محادثة أو سلسلة مختلفة.                                                                                                            |
| `Thread bindings are unavailable for <channel>.`                           | لا يملك المهايئ قدرة ربط السلاسل.                                                 | استخدم `--thread off` أو انتقل إلى مهايئ/قناة مدعومة.                                                                                                               |
| `Sandboxed sessions cannot spawn ACP sessions ...`                         | وقت تشغيل ACP يعمل على جهة المضيف؛ جلسة الطالب تعمل داخل sandbox.                 | استخدم `runtime="subagent"` من جلسات sandboxed، أو شغّل ACP spawn من جلسة غير sandboxed.                                                                           |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...`    | تم طلب `sandbox="require"` لوقت تشغيل ACP.                                        | استخدم `runtime="subagent"` عندما يكون sandbox مطلوبًا، أو استخدم ACP مع `sandbox="inherit"` من جلسة غير sandboxed.                                               |
| Missing ACP metadata for bound session                                     | بيانات تعريف ACP قديمة/محذوفة للجلسة المرتبطة.                                   | أعد الإنشاء باستخدام `/acp spawn`، ثم أعد الربط/تركيز السلسلة.                                                                                                      |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`   | تمنع `permissionMode` عمليات الكتابة/التنفيذ في جلسة ACP غير تفاعلية.             | عيّن `plugins.entries.acpx.config.permissionMode` إلى `approve-all` ثم أعد تشغيل البوابة. راجع [إعداد الأذونات](#permission-configuration).                      |
| تفشل جلسة ACP مبكرًا مع خرج قليل                                           | تُحظر مطالبات الأذونات بواسطة `permissionMode`/`nonInteractivePermissions`.       | تحقق من سجلات البوابة للعثور على `AcpRuntimeError`. للحصول على أذونات كاملة، عيّن `permissionMode=approve-all`؛ وللتراجع السلس، عيّن `nonInteractivePermissions=deny`. |
| تتوقف جلسة ACP إلى أجل غير مسمى بعد إكمال العمل                           | انتهت عملية harness لكن جلسة ACP لم تبلغ عن الاكتمال.                             | راقب عبر `ps aux \| grep acpx`; واقتل العمليات القديمة يدويًا.                                                                                                      |
