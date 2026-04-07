---
read_when:
    - تريد فهم الميزات التي قد تستدعي APIs مدفوعة
    - تحتاج إلى مراجعة المفاتيح، والتكاليف، ووضوح الاستخدام
    - أنت تشرح تقارير التكلفة في /status أو /usage
summary: راجع ما الذي يمكن أن ينفق المال، والمفاتيح المستخدمة، وكيفية عرض الاستخدام
title: استخدام API والتكاليف
x-i18n:
    generated_at: "2026-04-07T07:21:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab6eefcde9ac014df6cdda7aaa77ef48f16936ab12eaa883d9fe69425a31a2dd
    source_path: reference/api-usage-costs.md
    workflow: 15
---

# استخدام API والتكاليف

يسرد هذا المستند **الميزات التي يمكنها استدعاء مفاتيح API** والمكان الذي تظهر فيه تكاليفها. ويركز على
ميزات OpenClaw التي يمكنها توليد استخدام للمزود أو استدعاءات API مدفوعة.

## أين تظهر التكاليف (الدردشة + CLI)

**لقطة تكلفة لكل جلسة**

- يعرض `/status` نموذج الجلسة الحالي، واستخدام السياق، ورموز آخر استجابة.
- إذا كان النموذج يستخدم **مصادقة بمفتاح API**، فإن `/status` يعرض أيضًا **التكلفة التقديرية** لآخر رد.
- إذا كانت البيانات الوصفية الحية للجلسة محدودة، يمكن لـ `/status` استعادة
  عدادات الرموز/الذاكرة المؤقتة وعلامة نموذج وقت التشغيل النشط من أحدث إدخال استخدام في transcript.
  وتظل القيم الحية غير الصفرية الموجودة مسبقًا هي صاحبة الأولوية، ويمكن لإجماليات transcript
  بحجم prompt أن تتغلب عندما تكون الإجماليات المخزنة مفقودة أو أصغر.

**تذييل التكلفة لكل رسالة**

- يقوم `/usage full` بإلحاق تذييل استخدام بكل رد، بما في ذلك **التكلفة التقديرية** (لمصادقة مفتاح API فقط).
- يعرض `/usage tokens` الرموز فقط؛ وتخفي تدفقات OAuth/token وCLI ذات نمط الاشتراك التكلفة بالدولار.
- ملاحظة Gemini CLI: عندما يعيد CLI مخرجات JSON، يقرأ OpenClaw معلومات الاستخدام من
  `stats`، ويُطبّع `stats.cached` إلى `cacheRead`، ويستنتج رموز الإدخال
  من `stats.input_tokens - stats.cached` عند الحاجة.

ملاحظة Anthropic: أخبرنا موظفو Anthropic أن استخدام Claude CLI بأسلوب OpenClaw
مسموح به مجددًا، لذلك يتعامل OpenClaw مع إعادة استخدام Claude CLI واستخدام `claude -p` على أنه
معتمد لهذا التكامل ما لم تنشر Anthropic سياسة جديدة.
ولا تزال Anthropic لا تعرض تقديرًا بالدولار لكل رسالة يمكن لـ OpenClaw
عرضه في `/usage full`.

**نوافذ استخدام CLI ‏(حصص المزود)**

- يعرض `openclaw status --usage` و`openclaw channels list` **نوافذ استخدام** المزود
  (لقطات للحصة، وليست تكاليف لكل رسالة).
- يتم تطبيع المخرجات البشرية إلى `X% left` عبر جميع المزودين.
- مزودو نوافذ الاستخدام الحاليون: Anthropic، وGitHub Copilot، وGemini CLI،
  وOpenAI Codex، وMiniMax، وXiaomi، وz.ai.
- ملاحظة MiniMax: تعني الحقول الخام `usage_percent` / `usagePercent` مقدار
  الحصة المتبقية، لذلك يعكسها OpenClaw قبل العرض. وتظل الحقول المعتمدة على العدّ هي الغالبة
  عند وجودها. وإذا أعاد المزود `model_remains`، فإن OpenClaw يفضل
  إدخال نموذج الدردشة، ويستنتج تسمية النافذة من الطوابع الزمنية عند الحاجة،
  ويتضمن اسم النموذج في تسمية الخطة.
- تأتي مصادقة الاستخدام لنوافذ الحصص هذه من hooks خاصة بالمزود عند
  توفرها؛ وإلا فإن OpenClaw يرجع إلى مطابقة بيانات اعتماد OAuth/API-key
  من ملفات تعريف المصادقة، أو البيئة، أو الإعدادات.

راجع [استخدام الرموز والتكاليف](/ar/reference/token-use) للاطلاع على التفاصيل والأمثلة.

## كيف يتم اكتشاف المفاتيح

يمكن لـ OpenClaw التقاط بيانات الاعتماد من:

- **ملفات تعريف المصادقة** (لكل وكيل، مخزنة في `auth-profiles.json`).
- **متغيرات البيئة** (مثل `OPENAI_API_KEY`, `BRAVE_API_KEY`, `FIRECRAWL_API_KEY`).
- **الإعدادات** (`models.providers.*.apiKey`, `plugins.entries.*.config.webSearch.apiKey`,
  `plugins.entries.firecrawl.config.webFetch.apiKey`, `memorySearch.*`,
  `talk.providers.*.apiKey`).
- **Skills** ‏(`skills.entries.<name>.apiKey`) التي قد تصدر المفاتيح إلى بيئة عملية Skill.

## الميزات التي يمكنها إنفاق المفاتيح

### 1) استجابات النماذج الأساسية (الدردشة + الأدوات)

كل رد أو استدعاء أداة يستخدم **مزود النموذج الحالي** (OpenAI أو Anthropic أو غيرهما). وهذا هو
المصدر الرئيسي للاستخدام والتكلفة.

ويشمل ذلك أيضًا المزودين المستضافين بنمط الاشتراك الذين ما زالوا يفرضون الرسوم خارج
واجهة OpenClaw المحلية، مثل **OpenAI Codex** و**Alibaba Cloud Model Studio
Coding Plan** و**MiniMax Coding Plan** و**Z.AI / GLM Coding Plan** و
مسار تسجيل دخول Claude في OpenClaw من Anthropic مع تفعيل **Extra Usage**.

راجع [النماذج](/ar/providers/models) لإعدادات التسعير و[استخدام الرموز والتكاليف](/ar/reference/token-use) للعرض.

### 2) فهم الوسائط (الصوت/الصورة/الفيديو)

يمكن تلخيص الوسائط الواردة أو نسخها قبل تشغيل الرد. وهذا يستخدم APIs النماذج/المزودين.

- الصوت: OpenAI / Groq / Deepgram / Google / Mistral.
- الصورة: OpenAI / OpenRouter / Anthropic / Google / MiniMax / Moonshot / Qwen / Z.A.I.
- الفيديو: Google / Qwen / Moonshot.

راجع [فهم الوسائط](/ar/nodes/media-understanding).

### 3) توليد الصور والفيديو

يمكن لقدرات التوليد المشتركة أيضًا إنفاق مفاتيح المزود:

- توليد الصور: OpenAI / Google / fal / MiniMax
- توليد الفيديو: Qwen

يمكن لتوليد الصور استنتاج مزود افتراضي مدعوم بالمصادقة عندما
لا يتم ضبط `agents.defaults.imageGenerationModel`. أما توليد الفيديو فيتطلب حاليًا
`agents.defaults.videoGenerationModel` صريحًا مثل
`qwen/wan2.6-t2v`.

راجع [توليد الصور](/ar/tools/image-generation)، و[Qwen Cloud](/ar/providers/qwen)،
و[النماذج](/ar/concepts/models).

### 4) Embeddings الذاكرة + البحث الدلالي

يستخدم البحث الدلالي في الذاكرة **APIs embeddings** عند ضبطه لمزودات بعيدة:

- `memorySearch.provider = "openai"` ← OpenAI embeddings
- `memorySearch.provider = "gemini"` ← Gemini embeddings
- `memorySearch.provider = "voyage"` ← Voyage embeddings
- `memorySearch.provider = "mistral"` ← Mistral embeddings
- `memorySearch.provider = "ollama"` ← Ollama embeddings ‏(محلي/مستضاف ذاتيًا؛ وعادةً لا توجد رسوم API مستضافة)
- إمكانية fallback اختيارية إلى مزود بعيد إذا فشلت embeddings المحلية

يمكنك إبقاؤه محليًا باستخدام `memorySearch.provider = "local"` ‏(بدون استخدام API).

راجع [الذاكرة](/ar/concepts/memory).

### 5) أداة البحث على الويب

قد تتحمل `web_search` رسوم استخدام حسب المزود:

- **Brave Search API**: ‏`BRAVE_API_KEY` أو `plugins.entries.brave.config.webSearch.apiKey`
- **Exa**: ‏`EXA_API_KEY` أو `plugins.entries.exa.config.webSearch.apiKey`
- **Firecrawl**: ‏`FIRECRAWL_API_KEY` أو `plugins.entries.firecrawl.config.webSearch.apiKey`
- **Gemini (Google Search)**: ‏`GEMINI_API_KEY` أو `plugins.entries.google.config.webSearch.apiKey`
- **Grok (xAI)**: ‏`XAI_API_KEY` أو `plugins.entries.xai.config.webSearch.apiKey`
- **Kimi (Moonshot)**: ‏`KIMI_API_KEY`, `MOONSHOT_API_KEY` أو `plugins.entries.moonshot.config.webSearch.apiKey`
- **MiniMax Search**: ‏`MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, `MINIMAX_API_KEY` أو `plugins.entries.minimax.config.webSearch.apiKey`
- **Ollama Web Search**: بدون مفتاح افتراضيًا، لكنه يتطلب مضيف Ollama يمكن الوصول إليه بالإضافة إلى `ollama signin`؛ ويمكنه أيضًا إعادة استخدام مصادقة bearer العادية لمزود Ollama عندما يتطلبها المضيف
- **Perplexity Search API**: ‏`PERPLEXITY_API_KEY`, `OPENROUTER_API_KEY` أو `plugins.entries.perplexity.config.webSearch.apiKey`
- **Tavily**: ‏`TAVILY_API_KEY` أو `plugins.entries.tavily.config.webSearch.apiKey`
- **DuckDuckGo**: fallback بدون مفتاح (من دون رسوم API، لكنه غير رسمي ويعتمد على HTML)
- **SearXNG**: ‏`SEARXNG_BASE_URL` أو `plugins.entries.searxng.config.webSearch.baseUrl` ‏(بدون مفتاح/مستضاف ذاتيًا؛ من دون رسوم API مستضافة)

لا تزال مسارات المزود القديمة `tools.web.search.*` تُحمّل عبر طبقة التوافق المؤقتة، لكنها لم تعد سطح الإعدادات الموصى به.

**رصيد Brave Search المجاني:** تتضمن كل خطة Brave رصيدًا مجانيًا متجددًا بقيمة \$5 شهريًا.
تبلغ تكلفة خطة Search مبلغ \$5 لكل 1,000 طلب، لذلك يغطي الرصيد
1,000 طلب شهريًا بدون رسوم. اضبط حد الاستخدام في لوحة تحكم Brave
لتجنب الرسوم غير المتوقعة.

راجع [أدوات الويب](/ar/tools/web).

### 5) أداة جلب الويب (Firecrawl)

يمكن لـ `web_fetch` استدعاء **Firecrawl** عندما يكون مفتاح API موجودًا:

- `FIRECRAWL_API_KEY` أو `plugins.entries.firecrawl.config.webFetch.apiKey`

إذا لم يتم ضبط Firecrawl، فستعود الأداة إلى fetch مباشر + readability ‏(من دون API مدفوع).

راجع [أدوات الويب](/ar/tools/web).

### 6) لقطات استخدام المزود (الحالة/السلامة)

تستدعي بعض أوامر الحالة **endpoints استخدام المزود** لعرض نوافذ الحصص أو سلامة المصادقة.
وتكون هذه الاستدعاءات عادة منخفضة الحجم لكنها ما تزال تضرب APIs المزود:

- `openclaw status --usage`
- `openclaw models status --json`

راجع [CLI النماذج](/cli/models).

### 7) تلخيص وسيلة الحماية للضغط

يمكن لوسيلة الحماية للضغط تلخيص سجل الجلسة باستخدام **النموذج الحالي**، ما
يستدعي APIs المزود عند تشغيلها.

راجع [إدارة الجلسات + الضغط](/ar/reference/session-management-compaction).

### 8) فحص / استكشاف النماذج

يمكن لـ `openclaw models scan` فحص نماذج OpenRouter ويستخدم `OPENROUTER_API_KEY` عندما
يكون الفحص مفعّلًا.

راجع [CLI النماذج](/cli/models).

### 9) Talk ‏(الكلام)

يمكن لوضع Talk استدعاء **ElevenLabs** عند ضبطه:

- `ELEVENLABS_API_KEY` أو `talk.providers.elevenlabs.apiKey`

راجع [وضع Talk](/ar/nodes/talk).

### 10) Skills ‏(APIs خارجية)

يمكن لـ Skills تخزين `apiKey` في `skills.entries.<name>.apiKey`. وإذا استخدمت Skill هذا المفتاح مع
APIs خارجية، فقد تتحمل تكاليف وفقًا لمزود تلك Skill.

راجع [Skills](/ar/tools/skills).
