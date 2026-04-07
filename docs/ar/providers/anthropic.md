---
read_when:
    - تريد استخدام نماذج Anthropic في OpenClaw
summary: استخدم Anthropic Claude عبر مفاتيح API أو Claude CLI في OpenClaw
title: Anthropic
x-i18n:
    generated_at: "2026-04-07T07:21:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 423928fd36c66729985208d4d3f53aff1f94f63b908df85072988bdc41d5cf46
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

تطوّر Anthropic عائلة نماذج **Claude** وتوفر الوصول إليها عبر API و
Claude CLI. في OpenClaw، كل من مفاتيح Anthropic API وإعادة استخدام Claude CLI
مدعومان. كما تظل ملفات تعريف Anthropic token القديمة الحالية محترمة أثناء
التشغيل إذا كانت مهيأة بالفعل.

<Warning>
أخبرنا فريق Anthropic أن استخدام Claude CLI بأسلوب OpenClaw مسموح به مرة أخرى، لذلك
يتعامل OpenClaw مع إعادة استخدام Claude CLI واستخدام `claude -p` على أنهما معتمدان لهذا
التكامل ما لم تنشر Anthropic سياسة جديدة.

بالنسبة إلى مضيفي البوابة طويلة العمر، تظل مفاتيح Anthropic API هي المسار الإنتاجي
الأوضح والأكثر قابلية للتنبؤ. وإذا كنت تستخدم Claude CLI بالفعل على المضيف،
فيمكن لـ OpenClaw إعادة استخدام تسجيل الدخول هذا مباشرة.

مستندات Anthropic العامة الحالية:

- [مرجع Claude Code CLI](https://code.claude.com/docs/en/cli-reference)
- [نظرة عامة على Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)

- [استخدام Claude Code مع خطة Pro أو Max الخاصة بك](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [استخدام Claude Code مع خطة Team أو Enterprise الخاصة بك](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

إذا كنت تريد أوضح مسار للفوترة، فاستخدم مفتاح Anthropic API بدلًا من ذلك.
يدعم OpenClaw أيضًا خيارات أخرى بأسلوب الاشتراك، بما في ذلك [OpenAI
Codex](/ar/providers/openai) و[Qwen Cloud Coding Plan](/ar/providers/qwen) و
[MiniMax Coding Plan](/ar/providers/minimax) و[Z.AI / GLM Coding
Plan](/ar/providers/glm).
</Warning>

## الخيار A: مفتاح Anthropic API

**الأفضل لـ:** الوصول القياسي إلى API والفوترة حسب الاستخدام.
أنشئ مفتاح API الخاص بك في Anthropic Console.

### إعداد CLI

```bash
openclaw onboard
# اختر: Anthropic API key

# أو بشكل غير تفاعلي
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### مقتطف تهيئة Anthropic

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## القيم الافتراضية للتفكير (Claude 4.6)

- تستخدم نماذج Anthropic Claude 4.6 افتراضيًا مستوى التفكير `adaptive` في OpenClaw عندما لا يكون هناك مستوى تفكير صريح مضبوط.
- يمكنك التجاوز لكل رسالة (`/think:<level>`) أو في params الخاصة بالنموذج:
  `agents.defaults.models["anthropic/<model>"].params.thinking`.
- مستندات Anthropic ذات الصلة:
  - [التفكير التكيفي](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [التفكير الممتد](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## الوضع السريع (Anthropic API)

يدعم مفتاح التبديل المشترك `/fast` في OpenClaw أيضًا حركة Anthropic العامة المباشرة، بما في ذلك الطلبات الموثقة بمفتاح API وOAuth المرسلة إلى `api.anthropic.com`.

- يتحول `/fast on` إلى `service_tier: "auto"`
- يتحول `/fast off` إلى `service_tier: "standard_only"`
- الإعداد الافتراضي في التهيئة:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-sonnet-4-6": {
          params: { fastMode: true },
        },
      },
    },
  },
}
```

قيود مهمة:

- لا يحقن OpenClaw مستويات خدمة Anthropic إلا لطلبات `api.anthropic.com` المباشرة. وإذا مرّرت `anthropic/*` عبر proxy أو بوابة، فسيترك `/fast` قيمة `service_tier` دون تعديل.
- تتجاوز params الصريحة للنموذج `serviceTier` أو `service_tier` الخاصة بـ Anthropic القيمة الافتراضية لـ `/fast` عند تعيينهما معًا.
- تُبلغ Anthropic عن المستوى الفعلي في الاستجابة تحت `usage.service_tier`. وفي الحسابات التي لا تملك سعة Priority Tier، قد تُحل `service_tier: "auto"` إلى `standard` رغم ذلك.

## التخزين المؤقت للـ prompt (Anthropic API)

يدعم OpenClaw ميزة التخزين المؤقت للـ prompt في Anthropic. هذا **خاص بـ API فقط**؛ فمصادقة Anthropic token القديمة لا تحترم إعدادات التخزين المؤقت.

### التهيئة

استخدم المعامل `cacheRetention` في تهيئة النموذج:

| القيمة   | مدة التخزين المؤقت | الوصف                        |
| ------- | ------------------ | ---------------------------- |
| `none`  | بدون تخزين مؤقت    | تعطيل التخزين المؤقت للـ prompt |
| `short` | 5 دقائق            | الافتراضي لمصادقة API Key    |
| `long`  | ساعة واحدة         | تخزين مؤقت ممتد              |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

### القيم الافتراضية

عند استخدام مصادقة Anthropic API Key، يطبق OpenClaw تلقائيًا `cacheRetention: "short"` (تخزين مؤقت لمدة 5 دقائق) على جميع نماذج Anthropic. ويمكنك تجاوز ذلك عبر تعيين `cacheRetention` صراحةً في التهيئة.

### تجاوزات cacheRetention لكل وكيل

استخدم params على مستوى النموذج كخط أساس، ثم تجاوز وكلاء محددين عبر `agents.list[].params`.

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // خط أساس لمعظم الوكلاء
        },
      },
    },
    list: [
      { id: "research", default: true },
      { id: "alerts", params: { cacheRetention: "none" } }, // تجاوز لهذا الوكيل فقط
    ],
  },
}
```

ترتيب دمج التهيئة للمعاملات المرتبطة بالتخزين المؤقت:

1. `agents.defaults.models["provider/model"].params`
2. `agents.list[].params` (مطابقة حسب `id`، مع التجاوز حسب المفتاح)

يتيح هذا لوكيل واحد الاحتفاظ بتخزين مؤقت طويل العمر، بينما يعطل وكيل آخر على النموذج نفسه التخزين المؤقت لتجنب تكاليف الكتابة على الحركة المتدفقة أو منخفضة إعادة الاستخدام.

### ملاحظات Claude على Bedrock

- تقبل نماذج Anthropic Claude على Bedrock (`amazon-bedrock/*anthropic.claude*`) تمرير `cacheRetention` عند تهيئته.
- تُفرض قيمة `cacheRetention: "none"` على نماذج Bedrock غير التابعة لـ Anthropic أثناء التشغيل.
- تقوم القيم الافتراضية الذكية لمفتاح Anthropic API أيضًا بتهيئة `cacheRetention: "short"` لمراجع نماذج Claude-on-Bedrock عند عدم تعيين قيمة صريحة.

## نافذة سياق 1M (إصدار Anthropic التجريبي)

تخضع نافذة السياق 1M في Anthropic لبوابة بيتا. في OpenClaw، يمكنك تمكينها لكل نموذج
باستخدام `params.context1m: true` للنماذج المدعومة من Opus/Sonnet.

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { context1m: true },
        },
      },
    },
  },
}
```

يقوم OpenClaw بتعيين هذا إلى `anthropic-beta: context-1m-2025-08-07` في
طلبات Anthropic.

لا يتم تفعيل هذا إلا عندما تكون `params.context1m` مضبوطة صراحةً إلى `true`
لذلك النموذج.

المتطلب: يجب أن تسمح Anthropic باستخدام السياق الطويل لتلك البيانات الاعتمادية.

ملاحظة: ترفض Anthropic حاليًا طلبات بيتا `context-1m-*` عند استخدام
مصادقة Anthropic token القديمة (`sk-ant-oat-*`). وإذا قمت بتهيئة
`context1m: true` مع وضع المصادقة القديم هذا، فسيسجل OpenClaw تحذيرًا ويعود
إلى نافذة السياق القياسية عبر تخطي ترويسة context1m beta
مع الإبقاء على إصدارات OAuth التجريبية المطلوبة.

## خلفية Claude CLI

الخلفية المضمّنة `claude-cli` الخاصة بـ Anthropic مدعومة في OpenClaw.

- أخبرنا فريق Anthropic أن هذا الاستخدام مسموح به مرة أخرى.
- لذلك يتعامل OpenClaw مع إعادة استخدام Claude CLI واستخدام `claude -p` على أنه
  معتمد لهذا التكامل ما لم تنشر Anthropic سياسة جديدة.
- تظل مفاتيح Anthropic API أوضح مسار إنتاجي لمضيفي البوابة
  الدائمين ولمزيد من التحكم الصريح في الفوترة على جانب الخادم.
- تفاصيل الإعداد ووقت التشغيل موجودة في [/gateway/cli-backends](/ar/gateway/cli-backends).

## ملاحظات

- ما تزال مستندات Claude Code العامة من Anthropic توثّق الاستخدام المباشر لـ CLI مثل
  `claude -p`، كما أخبرنا فريق Anthropic أن استخدام Claude CLI بأسلوب OpenClaw
  مسموح به مرة أخرى. ونحن نتعامل مع هذا التوجيه على أنه محسوم ما لم تنشر Anthropic
  تغييرًا جديدًا في السياسة.
- ما يزال Anthropic setup-token متاحًا في OpenClaw كمسار مصادقة مدعوم قائم على token، لكن OpenClaw يفضّل الآن إعادة استخدام Claude CLI و`claude -p` عند توفرهما.
- تفاصيل المصادقة + قواعد إعادة الاستخدام موجودة في [/concepts/oauth](/ar/concepts/oauth).

## استكشاف الأخطاء وإصلاحها

**أخطاء 401 / أصبح token غير صالح فجأة**

- قد تنتهي صلاحية مصادقة Anthropic token أو يتم إلغاؤها.
- بالنسبة إلى الإعدادات الجديدة، انتقل إلى مفتاح Anthropic API.

**لم يتم العثور على مفتاح API للموفّر "anthropic"**

- المصادقة تكون **لكل وكيل**. الوكلاء الجدد لا يرثون مفاتيح الوكيل الرئيسي.
- أعد تشغيل onboarding لذلك الوكيل، أو هيّئ مفتاح API على مضيف
  البوابة، ثم تحقق باستخدام `openclaw models status`.

**لم يتم العثور على بيانات اعتماد لملف التعريف `anthropic:default`**

- شغّل `openclaw models status` لمعرفة ملف تعريف المصادقة النشط.
- أعد تشغيل onboarding، أو هيّئ مفتاح API لذلك المسار الخاص بملف التعريف.

**لا يوجد ملف تعريف مصادقة متاح (الكل في cooldown/غير متاح)**

- تحقق من `openclaw models status --json` لمعرفة `auth.unusableProfiles`.
- يمكن أن تكون فترات cooldown الخاصة بحد المعدل في Anthropic ضمن نطاق النموذج، لذلك قد يظل
  نموذج Anthropic آخر مرتبط قابلًا للاستخدام حتى عندما يكون النموذج الحالي في فترة cooldown.
- أضف ملف تعريف Anthropic آخر أو انتظر انتهاء cooldown.

المزيد: [/gateway/troubleshooting](/ar/gateway/troubleshooting) و[/help/faq](/ar/help/faq).
