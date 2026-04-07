---
read_when:
    - تشغيل إعداد CLI الأولي أو تهيئته
    - إعداد جهاز جديد
sidebarTitle: 'Onboarding: CLI'
summary: 'إعداد CLI الأولي: إعداد موجّه لـ gateway ومساحة العمل والقنوات وSkills'
title: الإعداد الأولي (CLI)
x-i18n:
    generated_at: "2026-04-07T07:22:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6773b07afa8babf1b5ac94d857063d08094a962ee21ec96ca966e99ad57d107d
    source_path: start/wizard.md
    workflow: 15
---

# الإعداد الأولي (CLI)

يُعد الإعداد الأولي عبر CLI الطريقة **الموصى بها** لإعداد OpenClaw على macOS
أو Linux أو Windows (عبر WSL2؛ ويوصى به بشدة).
فهو يهيّئ Gateway محليًا أو اتصال Gateway بعيدًا، بالإضافة إلى القنوات وSkills
وافتراضيات مساحة العمل ضمن تدفق موجّه واحد.

```bash
openclaw onboard
```

<Info>
أسرع طريقة لأول دردشة: افتح Control UI (لا حاجة إلى إعداد قناة). شغّل
`openclaw dashboard` وابدأ الدردشة في المتصفح. الوثائق: [Dashboard](/web/dashboard).
</Info>

لإعادة التهيئة لاحقًا:

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
لا يعني `--json` الوضع غير التفاعلي ضمنًا. بالنسبة إلى السكربتات، استخدم `--non-interactive`.
</Note>

<Tip>
يتضمن إعداد CLI الأولي خطوة بحث ويب يمكنك فيها اختيار مزوّد
مثل Brave أو DuckDuckGo أو Exa أو Firecrawl أو Gemini أو Grok أو Kimi أو MiniMax Search
أو Ollama Web Search أو Perplexity أو SearXNG أو Tavily. تتطلب بعض المزوّدات
مفتاح API، بينما لا يتطلب بعضها الآخر مفتاحًا. يمكنك أيضًا تهيئة هذا لاحقًا باستخدام
`openclaw configure --section web`. الوثائق: [أدوات الويب](/ar/tools/web).
</Tip>

## QuickStart مقابل Advanced

يبدأ الإعداد الأولي بخيار **QuickStart** (افتراضيات) مقابل **Advanced** (تحكم كامل).

<Tabs>
  <Tab title="QuickStart (الافتراضيات)">
    - Gateway محلي (`loopback`)
    - مساحة العمل الافتراضية (أو مساحة عمل موجودة)
    - منفذ Gateway **18789**
    - مصادقة Gateway **Token** (يُولَّد تلقائيًا، حتى على `loopback`)
    - سياسة الأدوات الافتراضية للإعدادات المحلية الجديدة: `tools.profile: "coding"` (يتم الاحتفاظ بأي ملف تعريف صريح موجود)
    - عزل DM الافتراضي: يكتب الإعداد المحلي `session.dmScope: "per-channel-peer"` عندما لا يكون مضبوطًا. التفاصيل: [مرجع إعداد CLI](/ar/start/wizard-cli-reference#outputs-and-internals)
    - إتاحة Tailscale **معطلة**
    - افتراضيًا تكون الرسائل الخاصة في Telegram وWhatsApp على **قائمة السماح** (سيُطلب منك رقم هاتفك)
  </Tab>
  <Tab title="Advanced (تحكم كامل)">
    - يكشف كل خطوة (الوضع، ومساحة العمل، وGateway، والقنوات، والخدمة، وSkills).
  </Tab>
</Tabs>

## ما الذي يهيئه الإعداد الأولي

**الوضع المحلي (الافتراضي)** يرشدك عبر هذه الخطوات:

1. **النموذج/المصادقة** — اختر أي تدفق مزوّد/مصادقة مدعوم (مفتاح API أو OAuth أو مصادقة يدوية خاصة بالمزوّد)، بما في ذلك Custom Provider
   (متوافق مع OpenAI أو متوافق مع Anthropic أو Unknown auto-detect). اختر نموذجًا افتراضيًا.
   ملاحظة أمنية: إذا كان هذا الوكيل سيشغّل أدوات أو يعالج محتوى webhook/hooks، فافضّل أقوى نموذج متاح من أحدث جيل مع إبقاء سياسة الأدوات صارمة. الفئات الأضعف/الأقدم أسهل في الحقن عبر المطالبات.
   بالنسبة إلى التشغيلات غير التفاعلية، يخزن `--secret-input-mode ref` مراجع مدعومة بالبيئة في ملفات تعريف المصادقة بدلًا من قيم مفاتيح API النصية الصريحة.
   في وضع `ref` غير التفاعلي، يجب ضبط متغير البيئة الخاص بالمزوّد؛ وتمرير إشارات مفاتيح مضمّنة من دون متغير البيئة هذا يؤدي إلى فشل سريع.
   في التشغيلات التفاعلية، يتيح لك اختيار وضع مرجع السر الإشارة إلى متغير بيئة أو مرجع مزوّد مهيأ (`file` أو `exec`)، مع تحقق أولي سريع قبل الحفظ.
   بالنسبة إلى Anthropic، يقدّم الإعداد/التهيئة التفاعليان **Anthropic Claude CLI** بوصفه المسار المحلي المفضّل و**Anthropic API key** بوصفه مسار الإنتاج الموصى به. كما يظل Anthropic setup-token متاحًا بوصفه مسار مصادقة مدعومًا قائمًا على الرموز.
2. **مساحة العمل** — موقع ملفات الوكيل (الافتراضي `~/.openclaw/workspace`). ويزرع ملفات bootstrap.
3. **Gateway** — المنفذ، وعنوان الربط، ووضع المصادقة، وإتاحة Tailscale.
   في وضع token التفاعلي، اختر تخزين token النصي الصريح الافتراضي أو فعّل SecretRef.
   مسار SecretRef الخاص بـ token في الوضع غير التفاعلي: `--gateway-token-ref-env <ENV_VAR>`.
4. **القنوات** — قنوات الدردشة المدمجة والمضمّنة مثل BlueBubbles وDiscord وFeishu وGoogle Chat وMattermost وMicrosoft Teams وQQ Bot وSignal وSlack وTelegram وWhatsApp وغير ذلك.
5. **الخدمة** — يثبّت LaunchAgent ‏(macOS)، أو وحدة systemd للمستخدم ‏(Linux/WSL2)، أو Scheduled Task أصلية في Windows مع بديل لكل مستخدم داخل مجلد Startup.
   إذا كانت مصادقة token تتطلب token وكان `gateway.auth.token` مُدارًا عبر SecretRef، فإن تثبيت الخدمة يتحقق منه لكنه لا يحتفظ بالرمز المحلول ضمن بيانات بيئة خدمة الإشراف الوصفية.
   إذا كانت مصادقة token تتطلب token وكان SecretRef الخاص بالرمز المهيأ غير محلول، فسيُمنع تثبيت الخدمة مع إرشادات عملية.
   إذا كان كل من `gateway.auth.token` و`gateway.auth.password` مهيأين وكان `gateway.auth.mode` غير مضبوط، فسيُمنع تثبيت الخدمة حتى يُضبط الوضع صراحةً.
6. **فحص السلامة** — يبدأ Gateway ويتحقق من أنه يعمل.
7. **Skills** — يثبّت Skills الموصى بها والتبعيات الاختيارية.

<Note>
لا تؤدي إعادة تشغيل الإعداد الأولي إلى مسح أي شيء ما لم تختر صراحةً **Reset** (أو تمرر `--reset`).
يفترض `--reset` في CLI افتراضيًا الإعدادات وبيانات الاعتماد والجلسات؛ استخدم `--reset-scope full` لتضمين مساحة العمل.
إذا كانت الإعدادات غير صالحة أو تحتوي على مفاتيح قديمة، فسيطلب منك الإعداد الأولي تشغيل `openclaw doctor` أولًا.
</Note>

**الوضع البعيد** يهيّئ فقط العميل المحلي للاتصال بـ Gateway موجود في مكان آخر.
وهو **لا** يثبّت أو يغيّر أي شيء على المضيف البعيد.

## إضافة وكيل آخر

استخدم `openclaw agents add <name>` لإنشاء وكيل منفصل له مساحة العمل الخاصة به،
وجلساته، وملفات تعريف المصادقة. يؤدي التشغيل من دون `--workspace` إلى بدء الإعداد الأولي.

ما الذي يضبطه:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

ملاحظات:

- تتبع مساحات العمل الافتراضية النمط `~/.openclaw/workspace-<agentId>`.
- أضف `bindings` لتوجيه الرسائل الواردة (يمكن للإعداد الأولي القيام بذلك).
- الإشارات غير التفاعلية: `--model` و`--agent-dir` و`--bind` و`--non-interactive`.

## المرجع الكامل

للحصول على تفصيلات خطوة بخطوة ومخرجات الإعدادات، راجع
[مرجع إعداد CLI](/ar/start/wizard-cli-reference).
وللأمثلة غير التفاعلية، راجع [أتمتة CLI](/ar/start/wizard-cli-automation).
وللمرجع التقني الأعمق، بما في ذلك تفاصيل RPC، راجع
[مرجع الإعداد الأولي](/ar/reference/wizard).

## وثائق ذات صلة

- مرجع أوامر CLI: [`openclaw onboard`](/cli/onboard)
- نظرة عامة على الإعداد الأولي: [نظرة عامة على الإعداد الأولي](/ar/start/onboarding-overview)
- الإعداد الأولي لتطبيق macOS: [الإعداد الأولي](/ar/start/onboarding)
- طقس التشغيل الأول للوكيل: [تهيئة الوكيل الأولية](/ar/start/bootstrapping)
