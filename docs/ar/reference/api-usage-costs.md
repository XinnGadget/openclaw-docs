---
read_when:
    - تريد أن تفهم الميزات التي قد تستدعي واجهات API مدفوعة الثمن
    - تحتاج إلى مراجعة المفاتيح والتكاليف وإمكانية عرض الاستخدام
    - أنت تشرح تقارير التكلفة في `/status` أو `/usage`
summary: راجع ما الذي يمكن أن ينفق المال، وما المفاتيح المستخدمة، وكيفية عرض الاستخدام
title: استخدام API والتكاليف
x-i18n:
    generated_at: "2026-04-13T07:28:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: f5077e74d38ef781ac7a72603e9f9e3829a628b95c5a9967915ab0f321565429
    source_path: reference/api-usage-costs.md
    workflow: 15
---

# استخدام API والتكاليف

تسرد هذه الوثيقة **الميزات التي يمكن أن تستدعي مفاتيح API** وأماكن ظهور تكاليفها. وتركّز على
ميزات OpenClaw التي يمكن أن تولّد استخدامًا لمزوّد الخدمة أو استدعاءات API مدفوعة.

## أين تظهر التكاليف (الدردشة + CLI)

**لقطة تكلفة لكل جلسة**

- يعرض `/status` نموذج الجلسة الحالي، واستخدام السياق، ورموز آخر استجابة.
- إذا كان النموذج يستخدم **مصادقة بمفتاح API**، فإن `/status` يعرض أيضًا **التكلفة التقديرية** لآخر رد.
- إذا كانت البيانات الوصفية للجلسة الحية محدودة، يمكن لـ `/status` استعادة
  عدّادات الرموز/التخزين المؤقت
  ووسم نموذج وقت التشغيل النشط من أحدث إدخال لاستخدام السجل
  النصي. وتظل القيم الحية الحالية غير الصفرية ذات أولوية، كما يمكن أن
  تتفوّق إجماليات السجل النصي ذات حجم المطالبة عندما تكون الإجماليات المخزّنة
  مفقودة أو أصغر.

**تذييل تكلفة لكل رسالة**

- يضيف `/usage full` تذييل استخدام إلى كل رد، بما في ذلك **التكلفة التقديرية** (لمفاتيح API فقط).
- يعرض `/usage tokens` الرموز فقط؛ بينما تُخفي تدفقات OAuth/الرموز بنمط الاشتراك وتدفقات CLI تكلفة الدولار.
- ملاحظة Gemini CLI: عندما يعيد CLI مخرجات JSON، يقرأ OpenClaw الاستخدام من
  `stats`، ويطبّع `stats.cached` إلى `cacheRead`، ويستنتج رموز الإدخال
  من `stats.input_tokens - stats.cached` عند الحاجة.

ملاحظة Anthropic: أخبرنا فريق Anthropic أن استخدام Claude CLI بأسلوب OpenClaw
مسموح به مرة أخرى، لذا يتعامل OpenClaw مع إعادة استخدام Claude CLI واستخدام `claude -p` على أنهما
مصرّح بهما لهذا التكامل ما لم تنشر Anthropic سياسة جديدة.
ولا تزال Anthropic لا توفّر تقديرًا بالدولار لكل رسالة يمكن لـ OpenClaw
عرضه في `/usage full`.

**نوافذ استخدام CLI (حصص المزوّد)**

- يعرض `openclaw status --usage` و`openclaw channels list` **نوافذ الاستخدام** الخاصة بالمزوّد
  (لقطات للحصص، وليست تكاليف لكل رسالة).
- يتم توحيد المخرجات البشرية إلى `X% left` عبر جميع المزوّدين.
- مزوّدو نوافذ الاستخدام الحاليون: Anthropic وGitHub Copilot وGemini CLI،
  وOpenAI Codex وMiniMax وXiaomi وz.ai.
- ملاحظة MiniMax: تعني حقول `usage_percent` / `usagePercent` الخام لديه
  الحصة المتبقية، لذلك يعكسها OpenClaw قبل العرض. وتظل الحقول المعتمدة على العد
  ذات أولوية عند توفّرها. وإذا أعاد المزوّد `model_remains`، فإن OpenClaw يفضّل
  إدخال نموذج الدردشة، ويستنتج تسمية النافذة من الطوابع الزمنية عند الحاجة،
  ويضمّن اسم النموذج في تسمية الخطة.
- تأتي مصادقة الاستخدام لنوافذ الحصص تلك من خطّافات خاصة بالمزوّد عند
  توفّرها؛ وإلا يعود OpenClaw إلى مطابقة بيانات اعتماد OAuth/مفاتيح API
  من ملفات تعريف المصادقة، أو البيئة، أو الإعدادات.

راجع [استخدام الرموز والتكاليف](/ar/reference/token-use) للاطلاع على التفاصيل والأمثلة.

## كيفية اكتشاف المفاتيح

يمكن لـ OpenClaw التقاط بيانات الاعتماد من:

- **ملفات تعريف المصادقة** (لكل وكيل، وتُخزَّن في `auth-profiles.json`).
- **متغيّرات البيئة** (مثل `OPENAI_API_KEY` و`BRAVE_API_KEY` و`FIRECRAWL_API_KEY`).
- **الإعدادات** (`models.providers.*.apiKey` و`plugins.entries.*.config.webSearch.apiKey`،
  و`plugins.entries.firecrawl.config.webFetch.apiKey` و`memorySearch.*`،
  و`talk.providers.*.apiKey`).
- **Skills** (`skills.entries.<name>.apiKey`) التي قد تصدّر المفاتيح إلى بيئة عملية Skill.

## الميزات التي يمكن أن تنفق المفاتيح

### 1) استجابات النموذج الأساسية (الدردشة + الأدوات)

كل رد أو استدعاء أداة يستخدم **مزوّد النموذج الحالي** (OpenAI أو Anthropic أو غيرهما). وهذا هو
المصدر الأساسي للاستخدام والتكلفة.

ويتضمن ذلك أيضًا المزوّدين المستضافين بنمط الاشتراك الذين لا تزال تتم
محاسبتهم خارج واجهة OpenClaw المحلية، مثل **OpenAI Codex** و**Alibaba Cloud Model Studio
Coding Plan** و**MiniMax Coding Plan** و**Z.AI / GLM Coding Plan**،
ومسار Claude-login في OpenClaw الخاص بـ Anthropic مع تفعيل **Extra Usage**.

راجع [النماذج](/ar/providers/models) لإعدادات التسعير و[استخدام الرموز والتكاليف](/ar/reference/token-use) للعرض.

### 2) فهم الوسائط (الصوت/الصورة/الفيديو)

يمكن تلخيص الوسائط الواردة أو تفريغها نصيًا قبل تنفيذ الرد. وهذا يستخدم واجهات API الخاصة بالنموذج/المزوّد.

- الصوت: OpenAI / Groq / Deepgram / Google / Mistral.
- الصورة: OpenAI / OpenRouter / Anthropic / Google / MiniMax / Moonshot / Qwen / Z.AI.
- الفيديو: Google / Qwen / Moonshot.

راجع [فهم الوسائط](/ar/nodes/media-understanding).

### 3) إنشاء الصور والفيديو

يمكن لقدرات الإنشاء المشتركة أيضًا أن تستهلك مفاتيح المزوّدين:

- إنشاء الصور: OpenAI / Google / fal / MiniMax
- إنشاء الفيديو: Qwen

يمكن لإنشاء الصور استنتاج مزوّد افتراضي يعتمد على المصادقة عندما
يكون `agents.defaults.imageGenerationModel` غير مضبوط. أما إنشاء الفيديو فيتطلّب حاليًا
ضبطًا صريحًا لـ `agents.defaults.videoGenerationModel` مثل
`qwen/wan2.6-t2v`.

راجع [إنشاء الصور](/ar/tools/image-generation)، و[Qwen Cloud](/ar/providers/qwen)،
و[النماذج](/ar/concepts/models).

### 4) تضمينات الذاكرة + البحث الدلالي

يستخدم البحث الدلالي في الذاكرة **واجهات API للتضمينات** عند تهيئته لمزوّدين بعيدين:

- `memorySearch.provider = "openai"` ← تضمينات OpenAI
- `memorySearch.provider = "gemini"` ← تضمينات Gemini
- `memorySearch.provider = "voyage"` ← تضمينات Voyage
- `memorySearch.provider = "mistral"` ← تضمينات Mistral
- `memorySearch.provider = "lmstudio"` ← تضمينات LM Studio (محلي/مستضاف ذاتيًا)
- `memorySearch.provider = "ollama"` ← تضمينات Ollama (محلي/مستضاف ذاتيًا؛ عادةً بلا فوترة API مستضافة)
- رجوع اختياري إلى مزوّد بعيد إذا فشلت التضمينات المحلية

يمكنك إبقاءه محليًا باستخدام `memorySearch.provider = "local"` (من دون استخدام API).

راجع [الذاكرة](/ar/concepts/memory).

### 5) أداة البحث على الويب

قد تؤدي `web_search` إلى رسوم استخدام بحسب مزوّدك:

- **Brave Search API**: ‏`BRAVE_API_KEY` أو `plugins.entries.brave.config.webSearch.apiKey`
- **Exa**: ‏`EXA_API_KEY` أو `plugins.entries.exa.config.webSearch.apiKey`
- **Firecrawl**: ‏`FIRECRAWL_API_KEY` أو `plugins.entries.firecrawl.config.webSearch.apiKey`
- **Gemini (Google Search)**: ‏`GEMINI_API_KEY` أو `plugins.entries.google.config.webSearch.apiKey`
- **Grok (xAI)**: ‏`XAI_API_KEY` أو `plugins.entries.xai.config.webSearch.apiKey`
- **Kimi (Moonshot)**: ‏`KIMI_API_KEY` أو `MOONSHOT_API_KEY` أو `plugins.entries.moonshot.config.webSearch.apiKey`
- **MiniMax Search**: ‏`MINIMAX_CODE_PLAN_KEY` أو `MINIMAX_CODING_API_KEY` أو `MINIMAX_API_KEY` أو `plugins.entries.minimax.config.webSearch.apiKey`
- **Ollama Web Search**: بلا مفتاح افتراضيًا، لكنه يتطلّب مضيف Ollama يمكن الوصول إليه بالإضافة إلى `ollama signin`؛ ويمكنه أيضًا إعادة استخدام مصادقة bearer العادية الخاصة بمزوّد Ollama عندما يتطلّبها المضيف
- **Perplexity Search API**: ‏`PERPLEXITY_API_KEY` أو `OPENROUTER_API_KEY` أو `plugins.entries.perplexity.config.webSearch.apiKey`
- **Tavily**: ‏`TAVILY_API_KEY` أو `plugins.entries.tavily.config.webSearch.apiKey`
- **DuckDuckGo**: بديل احتياطي بلا مفتاح (من دون فوترة API، لكنه غير رسمي ويعتمد على HTML)
- **SearXNG**: ‏`SEARXNG_BASE_URL` أو `plugins.entries.searxng.config.webSearch.baseUrl` (بلا مفتاح/مستضاف ذاتيًا؛ من دون فوترة API مستضافة)

لا تزال مسارات المزوّد القديمة `tools.web.search.*` تُحمَّل عبر طبقة التوافق المؤقتة، لكنها لم تعد سطح الإعدادات الموصى به.

**رصيد Brave Search المجاني:** تتضمن كل خطة Brave رصيدًا مجانيًا متجددًا
بقيمة \$5 شهريًا. وتبلغ تكلفة خطة Search ‏\$5 لكل 1,000 طلب، لذا يغطي الرصيد
1,000 طلب شهريًا من دون رسوم. اضبط حد الاستخدام في لوحة تحكم Brave
لتجنّب الرسوم غير المتوقعة.

راجع [أدوات الويب](/ar/tools/web).

### 5) أداة جلب الويب (Firecrawl)

يمكن لـ `web_fetch` استدعاء **Firecrawl** عندما يكون مفتاح API موجودًا:

- `FIRECRAWL_API_KEY` أو `plugins.entries.firecrawl.config.webFetch.apiKey`

إذا لم يكن Firecrawl مهيّأً، فستعود الأداة إلى الجلب المباشر + readability (من دون API مدفوع).

راجع [أدوات الويب](/ar/tools/web).

### 6) لقطات استخدام المزوّد (الحالة/السلامة)

تستدعي بعض أوامر الحالة **نقاط نهاية استخدام المزوّد** لعرض نوافذ الحصص أو سلامة المصادقة.
وعادةً ما تكون هذه استدعاءات منخفضة الحجم، لكنها لا تزال تضرب واجهات API الخاصة بالمزوّد:

- `openclaw status --usage`
- `openclaw models status --json`

راجع [Models CLI](/cli/models).

### 7) تلخيص حماية Compaction

يمكن لحماية Compaction تلخيص سجل الجلسة باستخدام **النموذج الحالي**، ما
يستدعي واجهات API الخاصة بالمزوّد عند تشغيله.

راجع [إدارة الجلسة + Compaction](/ar/reference/session-management-compaction).

### 8) فحص / سبر النموذج

يمكن لـ `openclaw models scan` سبر نماذج OpenRouter ويستخدم `OPENROUTER_API_KEY` عندما
يكون السبر مفعّلًا.

راجع [Models CLI](/cli/models).

### 9) Talk (الكلام)

يمكن لوضع Talk استدعاء **ElevenLabs** عند تهيئته:

- `ELEVENLABS_API_KEY` أو `talk.providers.elevenlabs.apiKey`

راجع [وضع Talk](/ar/nodes/talk).

### 10) Skills (واجهات API لجهات خارجية)

يمكن لـ Skills تخزين `apiKey` في `skills.entries.<name>.apiKey`. وإذا كانت Skill تستخدم هذا المفتاح مع
واجهات API خارجية، فقد تترتب عليها تكاليف وفقًا لمزوّد تلك Skill.

راجع [Skills](/ar/tools/skills).
