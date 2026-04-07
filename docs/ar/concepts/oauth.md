---
read_when:
    - تريد فهم OAuth في OpenClaw من البداية إلى النهاية
    - واجهت مشاكل في إبطال الرموز المميزة / تسجيل الخروج
    - تريد تدفقات مصادقة Claude CLI أو OAuth
    - تريد استخدام حسابات متعددة أو توجيه الملفات الشخصية
summary: 'OAuth في OpenClaw: تبادل الرموز المميزة، والتخزين، وأنماط تعدد الحسابات'
title: OAuth
x-i18n:
    generated_at: "2026-04-07T07:16:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4117fee70e3e64fd3a762403454ac2b78de695d2b85a7146750c6de615921e02
    source_path: concepts/oauth.md
    workflow: 15
---

# OAuth

يدعم OpenClaw "مصادقة الاشتراك" عبر OAuth لموفري الخدمة الذين يتيحون ذلك
(وخاصة **OpenAI Codex (ChatGPT OAuth)**). أما بالنسبة إلى Anthropic، فالانقسام
العملي الآن هو:

- **Anthropic API key**: فوترة Anthropic API العادية
- **مصادقة Anthropic Claude CLI / الاشتراك داخل OpenClaw**: أخبرنا موظفو Anthropic
  أن هذا الاستخدام مسموح به مرة أخرى

إن OpenAI Codex OAuth مدعوم صراحةً للاستخدام في الأدوات الخارجية مثل
OpenClaw. تشرح هذه الصفحة ما يلي:

بالنسبة إلى Anthropic في بيئات الإنتاج، فإن مصادقة API key هي المسار الأكثر أمانًا والموصى به.

- كيف يعمل **تبادل الرموز المميزة** في OAuth ‏(PKCE)
- أين يتم **تخزين** الرموز المميزة (ولماذا)
- كيفية التعامل مع **حسابات متعددة** (الملفات الشخصية + التجاوزات لكل جلسة)

يدعم OpenClaw أيضًا **provider plugins** التي تأتي مع تدفقات OAuth أو API‑key
الخاصة بها. شغّلها عبر:

```bash
openclaw models auth login --provider <id>
```

## مصرف الرموز المميزة (لماذا يوجد)

يقوم موفرو OAuth عادةً بإصدار **رمز تحديث مميز جديد** أثناء تدفقات تسجيل الدخول/التحديث. يمكن لبعض الموفرين (أو عملاء OAuth) إبطال رموز التحديث الأقدم عندما يتم إصدار رمز جديد للمستخدم/التطبيق نفسه.

العرض العملي للمشكلة:

- تسجّل الدخول عبر OpenClaw _وأيضًا_ عبر Claude Code / Codex CLI → ثم يتم "تسجيل الخروج" من أحدهما عشوائيًا لاحقًا

للحد من ذلك، يتعامل OpenClaw مع `auth-profiles.json` باعتباره **مصرفًا للرموز المميزة**:

- يقرأ وقت التشغيل بيانات الاعتماد من **مكان واحد**
- يمكننا الاحتفاظ بملفات شخصية متعددة وتوجيهها بشكل حتمي
- عندما تتم إعادة استخدام بيانات الاعتماد من CLI خارجي مثل Codex CLI، فإن OpenClaw
  يعكسها مع بيانات المصدر ويعيد قراءة ذلك المصدر الخارجي بدلًا من
  تدوير رمز التحديث بنفسه

## التخزين (مكان وجود الرموز المميزة)

يتم تخزين الأسرار **لكل وكيل**:

- ملفات تعريف المصادقة (OAuth + API keys + مراجع اختيارية على مستوى القيمة): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- ملف التوافق القديم: `~/.openclaw/agents/<agentId>/agent/auth.json`
  (تتم إزالة إدخالات `api_key` الثابتة عند اكتشافها)

ملف قديم للاستيراد فقط (لا يزال مدعومًا، لكنه ليس المخزن الرئيسي):

- `~/.openclaw/credentials/oauth.json` (يتم استيراده إلى `auth-profiles.json` عند أول استخدام)

كل ما سبق يحترم أيضًا `$OPENCLAW_STATE_DIR` (تجاوز دليل الحالة). المرجع الكامل: [/gateway/configuration](/ar/gateway/configuration-reference#auth-storage)

بالنسبة إلى مراجع الأسرار الثابتة وسلوك تفعيل اللقطة في وقت التشغيل، راجع [Secrets Management](/ar/gateway/secrets).

## توافق الرمز المميز القديم لـ Anthropic

<Warning>
توضح مستندات Claude Code العامة من Anthropic أن استخدام Claude Code المباشر يبقى ضمن
حدود اشتراك Claude، كما أخبرنا موظفو Anthropic أن استخدام Claude
CLI على نمط OpenClaw مسموح به مرة أخرى. لذلك يتعامل OpenClaw مع إعادة استخدام Claude CLI واستخدام
`claude -p` على أنهما مسموح بهما لهذا التكامل ما لم تنشر Anthropic
سياسة جديدة.

للاطلاع على مستندات خطط Claude Code المباشرة الحالية من Anthropic، راجع [Using Claude Code
with your Pro or Max
plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
و [Using Claude Code with your Team or Enterprise
plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/).

إذا كنت تريد خيارات أخرى بنمط الاشتراك داخل OpenClaw، فراجع [OpenAI
Codex](/ar/providers/openai)، و[Qwen Cloud Coding
Plan](/ar/providers/qwen)، و[MiniMax Coding Plan](/ar/providers/minimax)،
و[Z.AI / GLM Coding Plan](/ar/providers/glm).
</Warning>

يكشف OpenClaw أيضًا عن setup-token الخاص بـ Anthropic باعتباره مسارًا مدعومًا للمصادقة بالرمز المميز، لكنه يفضّل الآن إعادة استخدام Claude CLI و`claude -p` عند توفرهما.

## ترحيل Anthropic Claude CLI

يدعم OpenClaw إعادة استخدام Anthropic Claude CLI مرة أخرى. إذا كان لديك بالفعل
تسجيل دخول محلي إلى Claude على المضيف، فيمكن لعملية onboarding/configure إعادة استخدامه مباشرةً.

## تبادل OAuth (كيف يعمل تسجيل الدخول)

يتم تنفيذ تدفقات تسجيل الدخول التفاعلية في OpenClaw داخل `@mariozechner/pi-ai` وربطها بالمعالجات/الأوامر.

### Anthropic setup-token

شكل التدفق:

1. ابدأ Anthropic setup-token أو paste-token من OpenClaw
2. يخزّن OpenClaw بيانات اعتماد Anthropic الناتجة في ملف تعريف مصادقة
3. يبقى اختيار النموذج على `anthropic/...`
4. تظل ملفات تعريف مصادقة Anthropic الحالية متاحة للتراجع/التحكم في الترتيب

### OpenAI Codex (ChatGPT OAuth)

إن OpenAI Codex OAuth مدعوم صراحةً للاستخدام خارج Codex CLI، بما في ذلك تدفقات عمل OpenClaw.

شكل التدفق (PKCE):

1. توليد PKCE verifier/challenge + قيمة `state` عشوائية
2. فتح `https://auth.openai.com/oauth/authorize?...`
3. محاولة التقاط callback على `http://127.0.0.1:1455/auth/callback`
4. إذا تعذر ربط callback (أو كنت تعمل عن بُعد/بدون واجهة)، الصق عنوان URL أو الرمز الخاص بإعادة التوجيه
5. إجراء التبادل عند `https://auth.openai.com/oauth/token`
6. استخراج `accountId` من رمز الوصول المميز وتخزين `{ access, refresh, expires, accountId }`

مسار المعالج هو `openclaw onboard` → اختيار المصادقة `openai-codex`.

## التحديث + انتهاء الصلاحية

تخزّن الملفات الشخصية طابعًا زمنيًا `expires`.

في وقت التشغيل:

- إذا كان `expires` في المستقبل → استخدم رمز الوصول المميز المخزّن
- إذا انتهت صلاحيته → حدّثه (ضمن قفل ملف) واكتب بيانات الاعتماد المخزنة فوق القديمة
- الاستثناء: تظل بيانات الاعتماد المعاد استخدامها من CLI خارجي مُدارة خارجيًا؛ إذ يعيد OpenClaw
  قراءة مخزن مصادقة CLI ولا يستهلك رمز التحديث المنسوخ بنفسه أبدًا

تدفق التحديث تلقائي؛ وبشكل عام لا تحتاج إلى إدارة الرموز المميزة يدويًا.

## حسابات متعددة (الملفات الشخصية) + التوجيه

هناك نمطان:

### 1) المفضل: وكلاء منفصلون

إذا كنت تريد ألا يتفاعل "الشخصي" و"العمل" مطلقًا، فاستخدم وكلاء معزولين (جلسات منفصلة + بيانات اعتماد + مساحة عمل):

```bash
openclaw agents add work
openclaw agents add personal
```

ثم اضبط المصادقة لكل وكيل (المعالج) ووجّه المحادثات إلى الوكيل الصحيح.

### 2) متقدم: ملفات شخصية متعددة داخل وكيل واحد

يدعم `auth-profiles.json` معرّفات ملفات شخصية متعددة للموفر نفسه.

اختر الملف الشخصي المستخدم:

- بشكل عام عبر ترتيب الإعداد (`auth.order`)
- لكل جلسة عبر `/model ...@<profileId>`

مثال (تجاوز الجلسة):

- `/model Opus@anthropic:work`

كيفية معرفة معرّفات الملفات الشخصية الموجودة:

- `openclaw channels list --json` (يعرض `auth[]`)

مستندات ذات صلة:

- [/concepts/model-failover](/ar/concepts/model-failover) (قواعد التدوير + التهدئة)
- [/tools/slash-commands](/ar/tools/slash-commands) (واجهة الأوامر)

## ذو صلة

- [Authentication](/ar/gateway/authentication) — نظرة عامة على مصادقة موفري النماذج
- [Secrets](/ar/gateway/secrets) — تخزين بيانات الاعتماد وSecretRef
- [Configuration Reference](/ar/gateway/configuration-reference#auth-storage) — مفاتيح إعداد المصادقة
