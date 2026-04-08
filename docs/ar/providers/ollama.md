---
read_when:
    - تريد تشغيل OpenClaw مع نماذج سحابية أو محلية عبر Ollama
    - تحتاج إلى إرشادات إعداد Ollama وتهيئته
summary: شغّل OpenClaw مع Ollama (النماذج السحابية والمحلية)
title: Ollama
x-i18n:
    generated_at: "2026-04-08T07:16:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: d3295a7c879d3636a2ffdec05aea6e670e54a990ef52bd9b0cae253bc24aa3f7
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

Ollama هو بيئة تشغيل محلية لنماذج LLM تجعل من السهل تشغيل النماذج مفتوحة المصدر على جهازك. يتكامل OpenClaw مع واجهة Ollama API الأصلية (`/api/chat`)، ويدعم البث واستدعاء الأدوات، ويمكنه الاكتشاف التلقائي لنماذج Ollama المحلية عند تفعيل ذلك باستخدام `OLLAMA_API_KEY` (أو ملف تعريف مصادقة) وعدم تعريف إدخال صريح لـ `models.providers.ollama`.

<Warning>
**مستخدمو Ollama البعيد**: لا تستخدم عنوان URL المتوافق مع OpenAI عبر `/v1` (`http://host:11434/v1`) مع OpenClaw. فهذا يعطل استدعاء الأدوات وقد تُخرج النماذج JSON الخام الخاص بالأدوات كنص عادي. استخدم بدلًا من ذلك عنوان URL الخاص بواجهة Ollama API الأصلية: `baseUrl: "http://host:11434"` (من دون `/v1`).
</Warning>

## البدء السريع

### الإعداد الأولي (موصى به)

أسرع طريقة لإعداد Ollama هي من خلال الإعداد الأولي:

```bash
openclaw onboard
```

اختر **Ollama** من قائمة موفري الخدمة. سيقوم الإعداد الأولي بما يلي:

1. سيسأل عن عنوان URL الأساسي لـ Ollama الذي يمكن الوصول إلى مثيلك من خلاله (الافتراضي هو `http://127.0.0.1:11434`).
2. يتيح لك اختيار **Cloud + Local** (نماذج سحابية ومحلية) أو **Local** (نماذج محلية فقط).
3. يفتح تدفق تسجيل دخول عبر المتصفح إذا اخترت **Cloud + Local** ولم تكن قد سجلت الدخول إلى ollama.com.
4. يكتشف النماذج المتاحة ويقترح إعدادات افتراضية.
5. يسحب النموذج المحدد تلقائيًا إذا لم يكن متاحًا محليًا.

كما أن الوضع غير التفاعلي مدعوم أيضًا:

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --accept-risk
```

يمكنك اختياريًا تحديد عنوان URL أساسي مخصص أو نموذج:

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --custom-base-url "http://ollama-host:11434" \
  --custom-model-id "qwen3.5:27b" \
  --accept-risk
```

### الإعداد اليدوي

1. ثبّت Ollama: [https://ollama.com/download](https://ollama.com/download)

2. اسحب نموذجًا محليًا إذا كنت تريد استدلالًا محليًا:

```bash
ollama pull gemma4
# أو
ollama pull gpt-oss:20b
# أو
ollama pull llama3.3
```

3. إذا كنت تريد النماذج السحابية أيضًا، فسجّل الدخول:

```bash
ollama signin
```

4. شغّل الإعداد الأولي واختر `Ollama`:

```bash
openclaw onboard
```

- `Local`: نماذج محلية فقط
- `Cloud + Local`: نماذج محلية بالإضافة إلى نماذج سحابية
- النماذج السحابية مثل `kimi-k2.5:cloud` و`minimax-m2.7:cloud` و`glm-5.1:cloud` لا تتطلب `ollama pull` محليًا

يقترح OpenClaw حاليًا ما يلي:

- الافتراضي المحلي: `gemma4`
- الإعدادات الافتراضية السحابية: `kimi-k2.5:cloud` و`minimax-m2.7:cloud` و`glm-5.1:cloud`

5. إذا كنت تفضّل الإعداد اليدوي، ففعّل Ollama لـ OpenClaw مباشرةً (أي قيمة تعمل؛ إذ لا يتطلب Ollama مفتاحًا حقيقيًا):

```bash
# تعيين متغير البيئة
export OLLAMA_API_KEY="ollama-local"

# أو التهيئة في ملف الإعداد
openclaw config set models.providers.ollama.apiKey "ollama-local"
```

6. افحص النماذج أو بدّل بينها:

```bash
openclaw models list
openclaw models set ollama/gemma4
```

7. أو عيّن الافتراضي في الإعداد:

```json5
{
  agents: {
    defaults: {
      model: { primary: "ollama/gemma4" },
    },
  },
}
```

## اكتشاف النماذج (موفر ضمني)

عند تعيين `OLLAMA_API_KEY` (أو ملف تعريف مصادقة) و**عدم** تعريف `models.providers.ollama`، يكتشف OpenClaw النماذج من مثيل Ollama المحلي على `http://127.0.0.1:11434`:

- يستعلم عن `/api/tags`
- يستخدم عمليات بحث `/api/show` بأفضل جهد لقراءة `contextWindow` واكتشاف القدرات (بما في ذلك الرؤية) عند توفرها
- تُعلَّم النماذج التي تُبلغ عن قدرة `vision` عبر `/api/show` على أنها قادرة على التعامل مع الصور (`input: ["text", "image"]`)، لذلك يحقن OpenClaw الصور تلقائيًا في الموجّه لهذه النماذج
- يعلّم `reasoning` باستخدام استدلال يعتمد على اسم النموذج (`r1` و`reasoning` و`think`)
- يضبط `maxTokens` على الحد الأقصى الافتراضي للرموز في Ollama الذي يستخدمه OpenClaw
- يضبط جميع التكاليف على `0`

يؤدي ذلك إلى تجنّب الإدخالات اليدوية للنماذج مع إبقاء الفهرس متوافقًا مع مثيل Ollama المحلي.

لمعرفة النماذج المتاحة:

```bash
ollama list
openclaw models list
```

لإضافة نموذج جديد، ما عليك سوى سحبه باستخدام Ollama:

```bash
ollama pull mistral
```

سيُكتشف النموذج الجديد تلقائيًا ويصبح متاحًا للاستخدام.

إذا عيّنت `models.providers.ollama` صراحةً، فسيتم تخطي الاكتشاف التلقائي ويجب عليك تعريف النماذج يدويًا (انظر أدناه).

## التهيئة

### الإعداد الأساسي (اكتشاف ضمني)

أبسط طريقة لتمكين Ollama هي عبر متغير بيئة:

```bash
export OLLAMA_API_KEY="ollama-local"
```

### الإعداد الصريح (نماذج يدوية)

استخدم التهيئة الصريحة عندما:

- يكون Ollama يعمل على مضيف أو منفذ آخر.
- تريد فرض نوافذ سياق أو قوائم نماذج محددة.
- تريد تعريفات نماذج يدوية بالكامل.

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434",
        apiKey: "ollama-local",
        api: "ollama",
        models: [
          {
            id: "gpt-oss:20b",
            name: "GPT-OSS 20B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 8192,
            maxTokens: 8192 * 10
          }
        ]
      }
    }
  }
}
```

إذا كان `OLLAMA_API_KEY` معينًا، يمكنك حذف `apiKey` من إدخال الموفر وسيقوم OpenClaw بملئه لعمليات التحقق من التوفر.

### عنوان URL أساسي مخصص (تهيئة صريحة)

إذا كان Ollama يعمل على مضيف أو منفذ مختلف (تعطّل التهيئة الصريحة الاكتشاف التلقائي، لذا عرّف النماذج يدويًا):

```json5
{
  models: {
    providers: {
      ollama: {
        apiKey: "ollama-local",
        baseUrl: "http://ollama-host:11434", // بدون /v1 - استخدم عنوان URL الأصلي لواجهة Ollama API
        api: "ollama", // عيّنه صراحةً لضمان سلوك استدعاء الأدوات الأصلي
      },
    },
  },
}
```

<Warning>
لا تضف `/v1` إلى عنوان URL. يستخدم المسار `/v1` وضع التوافق مع OpenAI، حيث لا يكون استدعاء الأدوات موثوقًا. استخدم عنوان URL الأساسي لـ Ollama من دون لاحقة مسار.
</Warning>

### اختيار النموذج

بعد اكتمال التهيئة، تصبح جميع نماذج Ollama الخاصة بك متاحة:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## النماذج السحابية

تتيح لك النماذج السحابية تشغيل النماذج المستضافة سحابيًا (مثل `kimi-k2.5:cloud` و`minimax-m2.7:cloud` و`glm-5.1:cloud`) إلى جانب نماذجك المحلية.

لاستخدام النماذج السحابية، اختر وضع **Cloud + Local** أثناء الإعداد. يتحقق المعالج مما إذا كنت قد سجلت الدخول ويفتح تدفق تسجيل دخول عبر المتصفح عند الحاجة. إذا تعذر التحقق من المصادقة، يعود المعالج إلى الإعدادات الافتراضية للنماذج المحلية.

يمكنك أيضًا تسجيل الدخول مباشرةً على [ollama.com/signin](https://ollama.com/signin).

## Ollama Web Search

يدعم OpenClaw أيضًا **Ollama Web Search** كموفر `web_search` مضمّن.

- يستخدم مضيف Ollama المهيأ لديك (`models.providers.ollama.baseUrl` عند تعيينه، وإلا `http://127.0.0.1:11434`).
- لا يتطلب مفتاحًا.
- يتطلب أن يكون Ollama قيد التشغيل وأن تكون قد سجلت الدخول باستخدام `ollama signin`.

اختر **Ollama Web Search** أثناء `openclaw onboard` أو
`openclaw configure --section web`، أو عيّن:

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

للحصول على تفاصيل الإعداد والسلوك كاملة، راجع [Ollama Web Search](/ar/tools/ollama-search).

## متقدم

### نماذج الاستدلال

يتعامل OpenClaw مع النماذج ذات الأسماء مثل `deepseek-r1` أو `reasoning` أو `think` على أنها قادرة على الاستدلال افتراضيًا:

```bash
ollama pull deepseek-r1:32b
```

### تكاليف النماذج

Ollama مجاني ويعمل محليًا، لذا يتم تعيين جميع تكاليف النماذج إلى $0.

### تهيئة البث

يستخدم تكامل OpenClaw مع Ollama **واجهة Ollama API الأصلية** (`/api/chat`) افتراضيًا، وهي تدعم بالكامل البث واستدعاء الأدوات في الوقت نفسه. لا حاجة إلى أي تهيئة خاصة.

#### وضع التوافق القديم مع OpenAI

<Warning>
**استدعاء الأدوات غير موثوق في وضع التوافق مع OpenAI.** استخدم هذا الوضع فقط إذا كنت بحاجة إلى تنسيق OpenAI لوكيل وسيط ولا تعتمد على سلوك استدعاء الأدوات الأصلي.
</Warning>

إذا كنت تحتاج إلى استخدام نقطة النهاية المتوافقة مع OpenAI بدلًا من ذلك (على سبيل المثال، خلف وكيل وسيط لا يدعم سوى تنسيق OpenAI)، فعيّن `api: "openai-completions"` صراحةً:

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: true, // الافتراضي: true
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

قد لا يدعم هذا الوضع البث + استدعاء الأدوات في الوقت نفسه. قد تحتاج إلى تعطيل البث باستخدام `params: { streaming: false }` في تهيئة النموذج.

عند استخدام `api: "openai-completions"` مع Ollama، يحقن OpenClaw `options.num_ctx` افتراضيًا حتى لا يعود Ollama بصمت إلى نافذة سياق قدرها 4096. إذا كان الوكيل الوسيط/الجهة العليا يرفض حقول `options` غير المعروفة، فعطّل هذا السلوك:

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: false,
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

### نوافذ السياق

بالنسبة إلى النماذج المكتشفة تلقائيًا، يستخدم OpenClaw نافذة السياق التي يبلغ عنها Ollama عند توفرها، وإلا فإنه يعود إلى نافذة سياق Ollama الافتراضية التي يستخدمها OpenClaw. يمكنك تجاوز `contextWindow` و`maxTokens` في تهيئة الموفر الصريحة.

## استكشاف الأخطاء وإصلاحها

### لم يتم اكتشاف Ollama

تأكد من أن Ollama قيد التشغيل وأنك عيّنت `OLLAMA_API_KEY` (أو ملف تعريف مصادقة)، وأنك **لم** تعرّف إدخال `models.providers.ollama` صريحًا:

```bash
ollama serve
```

وتأكد من أن واجهة API قابلة للوصول:

```bash
curl http://localhost:11434/api/tags
```

### لا توجد نماذج متاحة

إذا لم يكن نموذجك مدرجًا، فإما:

- اسحب النموذج محليًا، أو
- عرّف النموذج صراحةً في `models.providers.ollama`.

لإضافة نماذج:

```bash
ollama list  # اعرض ما هو مثبت
ollama pull gemma4
ollama pull gpt-oss:20b
ollama pull llama3.3     # أو نموذج آخر
```

### تم رفض الاتصال

تحقق من أن Ollama يعمل على المنفذ الصحيح:

```bash
# تحقق مما إذا كان Ollama قيد التشغيل
ps aux | grep ollama

# أو أعد تشغيل Ollama
ollama serve
```

## راجع أيضًا

- [موفرو النماذج](/ar/concepts/model-providers) - نظرة عامة على جميع الموفّرين
- [اختيار النموذج](/ar/concepts/models) - كيفية اختيار النماذج
- [التهيئة](/ar/gateway/configuration) - المرجع الكامل للتهيئة
