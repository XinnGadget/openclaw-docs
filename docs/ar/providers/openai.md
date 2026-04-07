---
read_when:
    - تريد استخدام نماذج OpenAI في OpenClaw
    - تريد استخدام مصادقة اشتراك Codex بدلًا من مفاتيح API
summary: استخدم OpenAI عبر مفاتيح API أو اشتراك Codex في OpenClaw
title: OpenAI
x-i18n:
    generated_at: "2026-04-07T07:22:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6a2ce1ce5f085fe55ec50b8d20359180b9002c9730820cd5b0e011c3bf807b64
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

توفّر OpenAI واجهات API للمطورين لنماذج GPT. يدعم Codex **تسجيل الدخول إلى ChatGPT** للوصول
عبر الاشتراك أو **تسجيل الدخول بمفتاح API** للوصول القائم على الاستخدام. يتطلب Codex cloud تسجيل الدخول إلى ChatGPT.
وتدعم OpenAI صراحةً استخدام OAuth الخاص بالاشتراك في الأدوات/سير العمل الخارجية مثل OpenClaw.

## نمط التفاعل الافتراضي

يمكن لـ OpenClaw إضافة تراكب توجيه صغير خاص بـ OpenAI لكل من تشغيلات `openai/*` و
`openai-codex/*`. وبشكل افتراضي، يبقي هذا التراكب المساعد ودودًا،
وتعاونيًا، ومقتضبًا، ومباشرًا، وأكثر تعبيرًا عاطفيًا قليلًا
من دون أن يستبدل توجيه نظام OpenClaw الأساسي. كما يسمح التراكب الودود أيضًا
باستخدام الرموز التعبيرية أحيانًا عندما يكون ذلك مناسبًا بشكل طبيعي، مع الحفاظ
على اقتضاب المخرجات عمومًا.

مفتاح الإعدادات:

`plugins.entries.openai.config.personality`

القيم المسموح بها:

- `"friendly"`: الافتراضي؛ يفعّل التراكب الخاص بـ OpenAI.
- `"on"`: اسم مستعار لـ `"friendly"`.
- `"off"`: يعطّل التراكب ويستخدم توجيه OpenClaw الأساسي فقط.

النطاق:

- ينطبق على نماذج `openai/*`.
- ينطبق على نماذج `openai-codex/*`.
- لا يؤثر في الموفّرين الآخرين.

هذا السلوك مفعّل افتراضيًا. احتفظ بـ `"friendly"` صراحةً إذا كنت تريد أن
يستمر ذلك رغم تقلبات الإعدادات المحلية مستقبلًا:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "friendly",
        },
      },
    },
  },
}
```

### تعطيل تراكب توجيه OpenAI

إذا أردت توجيه OpenClaw الأساسي غير المعدّل، فاضبط التراكب على `"off"`:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "off",
        },
      },
    },
  },
}
```

يمكنك أيضًا ضبطه مباشرةً باستخدام config CLI:

```bash
openclaw config set plugins.entries.openai.config.personality off
```

يقوم OpenClaw بتسوية هذا الإعداد دون حساسية لحالة الأحرف وقت التشغيل، لذا فإن قيمًا مثل
`"Off"` ستعطّل التراكب الودود أيضًا.

## الخيار A: مفتاح OpenAI API (OpenAI Platform)

**الأفضل لـ:** الوصول المباشر إلى API والفوترة القائمة على الاستخدام.
احصل على مفتاح API من لوحة تحكم OpenAI.

ملخص المسار:

- `openai/gpt-5.4` = مسار OpenAI Platform API مباشر
- يتطلب `OPENAI_API_KEY` (أو إعداد موفّر OpenAI مكافئ)
- في OpenClaw، يتم توجيه تسجيل الدخول إلى ChatGPT/Codex عبر `openai-codex/*` وليس `openai/*`

### إعداد CLI

```bash
openclaw onboard --auth-choice openai-api-key
# أو بدون تفاعل
openclaw onboard --openai-api-key "$OPENAI_API_KEY"
```

### مقتطف إعدادات

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

تسرد وثائق نماذج API الحالية من OpenAI النموذجين `gpt-5.4` و`gpt-5.4-pro` للاستخدام المباشر
مع OpenAI API. ويقوم OpenClaw بتمرير كليهما عبر مسار `openai/*` الخاص بـ Responses.
ويتعمّد OpenClaw إخفاء السطر القديم `openai/gpt-5.3-codex-spark`،
لأن استدعاءات OpenAI API المباشرة ترفضه في حركة المرور الحية.

لا يعرض OpenClaw **`openai/gpt-5.3-codex-spark`** على مسار OpenAI
API المباشر. لا يزال `pi-ai` يوفّر سطرًا مضمّنًا لذلك النموذج، لكن طلبات OpenAI API الحية
ترفضه حاليًا. ويُتعامل مع Spark على أنه خاص بـ Codex فقط في OpenClaw.

## توليد الصور

يسجل plugin `openai` المضمن أيضًا توليد الصور عبر الأداة المشتركة
`image_generate`.

- نموذج الصور الافتراضي: `openai/gpt-image-1`
- التوليد: حتى 4 صور لكل طلب
- وضع التعديل: مفعّل، حتى 5 صور مرجعية
- يدعم `size`
- ملاحظة حالية خاصة بـ OpenAI: لا يمرّر OpenClaw حاليًا تجاوزات `aspectRatio` أو
  `resolution` إلى OpenAI Images API

لاستخدام OpenAI كموفّر الصور الافتراضي:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
      },
    },
  },
}
```

راجع [توليد الصور](/ar/tools/image-generation) لمعلمات الأداة
المشتركة، واختيار الموفّر، وسلوك التحويل الاحتياطي.

## توليد الفيديو

يسجل plugin `openai` المضمن أيضًا توليد الفيديو عبر الأداة المشتركة
`video_generate`.

- نموذج الفيديو الافتراضي: `openai/sora-2`
- الأوضاع: من نص إلى فيديو، ومن صورة إلى فيديو، وتدفقات مرجعية/تحرير لفيديو واحد
- الحدود الحالية: صورة واحدة أو مرجع فيديو واحد
- ملاحظة حالية خاصة بـ OpenAI: يمرّر OpenClaw حاليًا فقط تجاوزات `size`
  لتوليد الفيديو الأصلي في OpenAI. أما التجاوزات الاختيارية غير المدعومة
  مثل `aspectRatio` و`resolution` و`audio` و`watermark` فيتم تجاهلها
  والإبلاغ عنها كتحذير أداة.

لاستخدام OpenAI كموفّر الفيديو الافتراضي:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "openai/sora-2",
      },
    },
  },
}
```

راجع [توليد الفيديو](/ar/tools/video-generation) لمعلمات الأداة
المشتركة، واختيار الموفّر، وسلوك التحويل الاحتياطي.

## الخيار B: اشتراك OpenAI Code (Codex)

**الأفضل لـ:** استخدام وصول اشتراك ChatGPT/Codex بدلًا من مفتاح API.
يتطلب Codex cloud تسجيل الدخول إلى ChatGPT، بينما تدعم Codex CLI تسجيل الدخول عبر ChatGPT أو مفتاح API.

ملخص المسار:

- `openai-codex/gpt-5.4` = مسار ChatGPT/Codex OAuth
- يستخدم تسجيل الدخول إلى ChatGPT/Codex، وليس مفتاح OpenAI Platform API مباشرًا
- قد تختلف الحدود من جهة الموفّر لـ `openai-codex/*` عن تجربة ChatGPT على الويب/التطبيق

### إعداد CLI ‏(Codex OAuth)

```bash
# شغّل Codex OAuth في المعالج
openclaw onboard --auth-choice openai-codex

# أو شغّل OAuth مباشرة
openclaw models auth login --provider openai-codex
```

### مقتطف إعدادات (اشتراك Codex)

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

تسرد وثائق Codex الحالية من OpenAI النموذج `gpt-5.4` باعتباره نموذج Codex الحالي. ويقوم OpenClaw
بربطه إلى `openai-codex/gpt-5.4` لاستخدام ChatGPT/Codex OAuth.

هذا المسار منفصل عمدًا عن `openai/gpt-5.4`. إذا أردت
مسار OpenAI Platform API المباشر، فاستخدم `openai/*` مع مفتاح API. وإذا أردت
تسجيل الدخول إلى ChatGPT/Codex، فاستخدم `openai-codex/*`.

إذا أعاد onboarding استخدام تسجيل دخول موجود مسبقًا في Codex CLI، فستظل بيانات الاعتماد تلك
مُدارة بواسطة Codex CLI. وعند انتهاء الصلاحية، يعيد OpenClaw قراءة مصدر Codex الخارجي
أولًا، وعندما يتمكن الموفّر من تحديثه، يكتب بيانات الاعتماد المحدّثة
مرة أخرى إلى تخزين Codex بدلًا من أخذ الملكية في نسخة منفصلة خاصة بـ OpenClaw فقط.

إذا كان حساب Codex الخاص بك مخوّلًا لاستخدام Codex Spark، فإن OpenClaw يدعم أيضًا:

- `openai-codex/gpt-5.3-codex-spark`

يتعامل OpenClaw مع Codex Spark على أنه خاص بـ Codex فقط. وهو لا يعرض مسار
مباشرًا بمفتاح API من نوع `openai/gpt-5.3-codex-spark`.

كما يحتفظ OpenClaw أيضًا بـ `openai-codex/gpt-5.3-codex-spark` عندما
يكتشفه `pi-ai`. ويجب التعامل معه على أنه تجريبي ومعتمد على الاستحقاق: إذ إن Codex Spark
منفصل عن GPT-5.4 `/fast`، كما أن توفره يعتمد على حساب Codex /
ChatGPT المسجّل دخوله.

### حد نافذة سياق Codex

يتعامل OpenClaw مع بيانات نموذج Codex الوصفية وحد وقت تشغيل السياق على أنهما
قيمتان منفصلتان.

بالنسبة إلى `openai-codex/gpt-5.4`:

- `contextWindow` الأصلي: `1050000`
- الحد الافتراضي لوقت التشغيل `contextTokens`: `272000`

يحافظ ذلك على صحة بيانات النموذج الوصفية مع الإبقاء على نافذة
وقت التشغيل الافتراضية الأصغر، التي تتمتع عمليًا بخصائص أفضل من حيث الكمون والجودة.

إذا أردت حدًا فعليًا مختلفًا، فاضبط `models.providers.<provider>.models[].contextTokens`:

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [
          {
            id: "gpt-5.4",
            contextTokens: 160000,
          },
        ],
      },
    },
  },
}
```

استخدم `contextWindow` فقط عندما تقوم بتعريف أو تجاوز بيانات النموذج الأصلية
الوصفية. واستخدم `contextTokens` عندما تريد تقييد ميزانية السياق وقت التشغيل.

### النقل الافتراضي

يستخدم OpenClaw `pi-ai` لبث النموذج. ولكل من `openai/*` و
`openai-codex/*`، يكون النقل الافتراضي هو `"auto"` (WebSocket أولًا، ثم
التحويل الاحتياطي إلى SSE).

في وضع `"auto"`، يعيد OpenClaw أيضًا محاولة واحدة عند حدوث فشل مبكر قابل لإعادة المحاولة في WebSocket
قبل أن يتحول احتياطيًا إلى SSE. أما وضع `"websocket"` المفروض فلا يزال يُظهر أخطاء النقل
مباشرةً بدلًا من إخفائها وراء التحويل الاحتياطي.

بعد فشل WebSocket عند الاتصال أو في الدور المبكر في وضع `"auto"`، يعلّم OpenClaw
مسار WebSocket الخاص بتلك الجلسة على أنه متدهور لمدة تقارب 60 ثانية، ويرسل
الأدوار اللاحقة عبر SSE خلال فترة التهدئة بدلًا من التنقل العنيف بين
وسائل النقل.

بالنسبة إلى نقاط نهاية OpenAI الأصلية (`openai/*` و`openai-codex/*` وAzure
OpenAI Responses)، يرفق OpenClaw أيضًا حالة مستقرة لهوية الجلسة والدور
بالطلبات حتى تظل إعادة المحاولة وإعادة الاتصال والتحويل الاحتياطي إلى SSE منسجمة مع
هوية المحادثة نفسها. ويتضمن ذلك على مسارات عائلة OpenAI الأصلية رؤوس هوية طلب مستقرة للجلسة/الدور بالإضافة إلى بيانات نقل وصفية مطابقة.

كما يطبع OpenClaw أيضًا عدادات استخدام OpenAI عبر متغيرات النقل المختلفة قبل
أن تصل إلى واجهات الجلسة/الحالة. فقد يبلّغ مرور Native OpenAI/Codex Responses
عن الاستخدام بصيغة `input_tokens` / `output_tokens` أو
`prompt_tokens` / `completion_tokens`؛ ويتعامل OpenClaw معها على أنها عدادات
الإدخال والإخراج نفسها بالنسبة إلى `/status` و`/usage` وسجلات الجلسات. وعندما يحذف
مرور WebSocket الأصلي `total_tokens` (أو يبلّغ عنه بقيمة `0`)، يعود OpenClaw إلى
إجمالي الإدخال + الإخراج المُطبّع حتى تظل عروض الجلسة/الحالة مليئة بالبيانات.

يمكنك ضبط `agents.defaults.models.<provider/model>.params.transport`:

- `"sse"`: فرض SSE
- `"websocket"`: فرض WebSocket
- `"auto"`: جرّب WebSocket، ثم تحوّل احتياطيًا إلى SSE

بالنسبة إلى `openai/*` (Responses API)، يفعّل OpenClaw أيضًا الإحماء عبر WebSocket
افتراضيًا (`openaiWsWarmup: true`) عند استخدام نقل WebSocket.

وثائق OpenAI ذات الصلة:

- [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
- [Streaming API responses (SSE)](https://platform.openai.com/docs/guides/streaming-responses)

```json5
{
  agents: {
    defaults: {
      model: { primary: "openai-codex/gpt-5.4" },
      models: {
        "openai-codex/gpt-5.4": {
          params: {
            transport: "auto",
          },
        },
      },
    },
  },
}
```

### إحماء OpenAI WebSocket

تصف وثائق OpenAI الإحماء بأنه اختياري. ويقوم OpenClaw بتفعيله افتراضيًا لـ
`openai/*` لتقليل كمون الدور الأول عند استخدام نقل WebSocket.

### تعطيل الإحماء

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: false,
          },
        },
      },
    },
  },
}
```

### تفعيل الإحماء صراحةً

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: true,
          },
        },
      },
    },
  },
}
```

### OpenAI وCodex والمعالجة ذات الأولوية

تعرض API الخاصة بـ OpenAI المعالجة ذات الأولوية عبر `service_tier=priority`. في
OpenClaw، اضبط `agents.defaults.models["<provider>/<model>"].params.serviceTier`
لتمرير هذا الحقل في نقاط نهاية Native OpenAI/Codex Responses.

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

القيم المدعومة هي `auto` و`default` و`flex` و`priority`.

يمرّر OpenClaw `params.serviceTier` إلى كل من طلبات Responses المباشرة `openai/*`
وطلبات Codex Responses من نوع `openai-codex/*` عندما تشير تلك النماذج
إلى نقاط نهاية Native OpenAI/Codex.

سلوك مهم:

- يجب أن يستهدف `openai/*` المباشر `api.openai.com`
- يجب أن يستهدف `openai-codex/*` ‏`chatgpt.com/backend-api`
- إذا قمت بتوجيه أي من الموفّرين عبر base URL آخر أو proxy، فإن OpenClaw يترك `service_tier` من دون تعديل

### وضع OpenAI السريع

يعرض OpenClaw مفتاح تبديل مشترك للوضع السريع لكل من جلسات `openai/*` و
`openai-codex/*`:

- Chat/UI: ‏`/fast status|on|off`
- Config: ‏`agents.defaults.models["<provider>/<model>"].params.fastMode`

عندما يكون الوضع السريع مفعّلًا، يربطه OpenClaw بمعالجة OpenAI ذات الأولوية:

- ترسل استدعاءات Responses المباشرة من `openai/*` إلى `api.openai.com` القيمة `service_tier = "priority"`
- وترسل استدعاءات Responses من `openai-codex/*` إلى `chatgpt.com/backend-api` أيضًا القيمة `service_tier = "priority"`
- يتم الحفاظ على قيم `service_tier` الموجودة في الحمولة
- لا يعيد الوضع السريع كتابة `reasoning` أو `text.verbosity`

وبالنسبة إلى GPT 5.4 تحديدًا، فإن الإعداد الأكثر شيوعًا هو:

- إرسال `/fast on` في جلسة تستخدم `openai/gpt-5.4` أو `openai-codex/gpt-5.4`
- أو ضبط `agents.defaults.models["openai/gpt-5.4"].params.fastMode = true`
- وإذا كنت تستخدم Codex OAuth أيضًا، فاضبط `agents.defaults.models["openai-codex/gpt-5.4"].params.fastMode = true` أيضًا

مثال:

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
      },
    },
  },
}
```

تتغلب تجاوزات الجلسة على config. وتؤدي إزالة تجاوز الجلسة في واجهة Sessions
إلى إعادة الجلسة إلى القيمة الافتراضية المضبوطة.

### مسارات Native OpenAI مقابل المسارات المتوافقة مع OpenAI

يتعامل OpenClaw مع نقاط النهاية المباشرة لـ OpenAI وCodex وAzure OpenAI بشكل مختلف
عن الوكلاء العامين المتوافقين مع OpenAI من نوع `/v1`:

- تحافظ المسارات الأصلية `openai/*` و`openai-codex/*` ومسارات Azure OpenAI على
  `reasoning: { effort: "none" }` كما هو عندما تعطل reasoning صراحةً
- تجعل مسارات عائلة OpenAI الأصلية مخططات الأدوات في الوضع الصارم افتراضيًا
- لا تُرفق رؤوس الإسناد المخفية الخاصة بـ OpenClaw (`originator` و`version` و
  `User-Agent`) إلا على مضيفي OpenAI الأصليين المؤكدين
  (`api.openai.com`) ومضيفي Codex الأصليين (`chatgpt.com/backend-api`)
- تحتفظ مسارات Native OpenAI/Codex بتشكيل الطلبات الخاص بـ OpenAI فقط مثل
  `service_tier`، و`store` الخاصة بـ Responses، والحمولات المتوافقة مع OpenAI reasoning،
  وتلميحات cache الخاصة بالتوجيه
- تحتفظ المسارات المتوافقة مع OpenAI على نمط proxy بسلوك التوافق الأكثر مرونة، ولا
  تفرض مخططات أدوات صارمة، أو تشكيل طلبات خاص بالأصل، أو رؤوس
  إسناد OpenAI/Codex المخفية

يبقى Azure OpenAI ضمن فئة التوجيه الأصلي بالنسبة إلى سلوك النقل والتوافق،
لكنه لا يتلقى رؤوس الإسناد المخفية الخاصة بـ OpenAI/Codex.

يحافظ هذا على السلوك الحالي لـ Native OpenAI Responses من دون فرض طبقات
التوافق القديمة الخاصة بـ OpenAI على الواجهات الخلفية `/v1` التابعة لجهات خارجية.

### الضغط من جهة الخادم في OpenAI Responses

بالنسبة إلى نماذج OpenAI Responses المباشرة (`openai/*` التي تستخدم `api: "openai-responses"` مع
`baseUrl` على `api.openai.com`)، يقوم OpenClaw الآن بتفعيل تلميحات حمولة
الضغط من جهة خادم OpenAI تلقائيًا:

- يفرض `store: true` (إلا إذا ضبط توافق النموذج `supportsStore: false`)
- ويحقن `context_management: [{ type: "compaction", compact_threshold: ... }]`

افتراضيًا، تكون قيمة `compact_threshold` هي `70%` من `contextWindow` الخاص بالنموذج (أو `80000`
عند عدم توفره).

### تفعيل الضغط من جهة الخادم صراحةً

استخدم هذا عندما تريد فرض حقن `context_management` على
نماذج Responses المتوافقة (مثل Azure OpenAI Responses):

```json5
{
  agents: {
    defaults: {
      models: {
        "azure-openai-responses/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
          },
        },
      },
    },
  },
}
```

### التفعيل مع عتبة مخصصة

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
            responsesCompactThreshold: 120000,
          },
        },
      },
    },
  },
}
```

### تعطيل الضغط من جهة الخادم

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: false,
          },
        },
      },
    },
  },
}
```

لا يتحكم `responsesServerCompaction` إلا في حقن `context_management`.
ولا تزال نماذج OpenAI Responses المباشرة تفرض `store: true` ما لم يضبط التوافق
`supportsStore: false`.

## ملاحظات

- تستخدم مراجع النماذج دائمًا الصيغة `provider/model` (راجع [/concepts/models](/ar/concepts/models)).
- توجد تفاصيل المصادقة + قواعد إعادة الاستخدام في [/concepts/oauth](/ar/concepts/oauth).
