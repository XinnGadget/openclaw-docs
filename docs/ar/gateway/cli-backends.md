---
read_when:
    - تريد بديلاً موثوقًا عندما يفشل موفرو API
    - أنت تشغّل Codex CLI أو واجهات AI CLI محلية أخرى وتريد إعادة استخدامها
    - تريد فهم جسر MCP المحلي loopback للوصول إلى أدوات الواجهة الخلفية لـ CLI
summary: 'واجهات CLI الخلفية: بديل محلي لـ AI CLI مع جسر أداة MCP اختياري'
title: واجهات CLI الخلفية
x-i18n:
    generated_at: "2026-04-09T01:28:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9b458f9fe6fa64c47864c8c180f3dedfd35c5647de470a2a4d31c26165663c20
    source_path: gateway/cli-backends.md
    workflow: 15
---

# واجهات CLI الخلفية (بيئة تشغيل احتياطية)

يمكن لـ OpenClaw تشغيل **واجهات AI CLI محلية** كخيار **احتياطي نصي فقط** عندما تتعطل موفرو API،
أو تُفرض عليها حدود المعدل، أو تتصرف بشكل غير صحيح مؤقتًا. هذا مصمم عمدًا بشكل متحفظ:

- **لا يتم حقن أدوات OpenClaw مباشرةً**، لكن الواجهات الخلفية التي تتضمن `bundleMcp: true`
  يمكنها تلقي أدوات البوابة عبر جسر MCP محلي loopback.
- **بث JSONL** لواجهات CLI التي تدعمه.
- **الجلسات مدعومة** (بحيث تبقى التفاعلات اللاحقة مترابطة).
- **يمكن تمرير الصور** إذا كانت واجهة CLI تقبل مسارات الصور.

هذا مصمم ليكون **شبكة أمان** وليس مسارًا أساسيًا. استخدمه عندما
تريد ردودًا نصية “تعمل دائمًا” من دون الاعتماد على API خارجية.

إذا كنت تريد بيئة تشغيل كاملة مع عناصر تحكم جلسات ACP، والمهام في الخلفية،
وربط السلاسل/المحادثات، وجلسات ترميز خارجية مستمرة، فاستخدم
[وكلاء ACP](/ar/tools/acp-agents) بدلًا من ذلك. واجهات CLI الخلفية ليست ACP.

## بداية سريعة مناسبة للمبتدئين

يمكنك استخدام Codex CLI **من دون أي إعداد** (إضافة OpenAI المضمنة
تسجل واجهة خلفية افتراضية):

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

إذا كانت البوابة تعمل تحت launchd/systemd وكان `PATH` محدودًا، فأضف فقط
مسار الأمر:

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
      },
    },
  },
}
```

هذا كل شيء. لا حاجة إلى مفاتيح أو إعدادات مصادقة إضافية بخلاف ما تتطلبه واجهة CLI نفسها.

إذا كنت تستخدم واجهة CLI خلفية مضمنة كـ **موفر الرسائل الأساسي** على
مضيف البوابة، فإن OpenClaw يحمّل الآن الإضافة المضمنة المالكة تلقائيًا عندما يشير إعدادك
صراحةً إلى تلك الواجهة الخلفية في مرجع نموذج أو تحت
`agents.defaults.cliBackends`.

## استخدامه كبديل احتياطي

أضف واجهة CLI خلفية إلى قائمة البدائل الاحتياطية بحيث لا تعمل إلا عندما تفشل النماذج الأساسية:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["codex-cli/gpt-5.4"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "codex-cli/gpt-5.4": {},
      },
    },
  },
}
```

ملاحظات:

- إذا كنت تستخدم `agents.defaults.models` (قائمة سماح)، فيجب أن تضمّن نماذج واجهة CLI الخلفية هناك أيضًا.
- إذا فشل الموفر الأساسي (المصادقة، حدود المعدل، المهلات)، فسيحاول OpenClaw
  استخدام واجهة CLI الخلفية التالية.

## نظرة عامة على الإعداد

توجد جميع واجهات CLI الخلفية تحت:

```
agents.defaults.cliBackends
```

يُفهرس كل إدخال بواسطة **معرّف موفر** (مثل `codex-cli` أو `my-cli`).
ويصبح معرّف الموفر هو الجزء الأيسر من مرجع النموذج:

```
<provider>/<model>
```

### مثال على الإعداد

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-6": "opus",
            "claude-sonnet-4-6": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          // يمكن لواجهات CLI بأسلوب Codex الإشارة إلى ملف موجه بدلاً من ذلك:
          // systemPromptFileConfigArg: "-c",
          // systemPromptFileConfigKey: "model_instructions_file",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## كيف يعمل

1. **يحدد واجهة خلفية** استنادًا إلى بادئة الموفر (`codex-cli/...`).
2. **ينشئ موجه نظام** باستخدام نفس موجه OpenClaw + سياق مساحة العمل.
3. **يشغّل واجهة CLI** مع معرّف جلسة (إذا كان مدعومًا) حتى يبقى السجل متسقًا.
4. **يحلل المخرجات** (`JSON` أو نص عادي) ويعيد النص النهائي.
5. **يحفظ معرّفات الجلسات** لكل واجهة خلفية، بحيث تعيد التفاعلات اللاحقة استخدام جلسة CLI نفسها.

<Note>
أصبحت الواجهة الخلفية المضمنة `claude-cli` من Anthropic مدعومة مرة أخرى. أخبرنا
موظفو Anthropic أن استخدام Claude CLI بأسلوب OpenClaw مسموح مرة أخرى، لذلك يتعامل OpenClaw مع
استخدام `claude -p` على أنه مسموح لهذا التكامل ما لم تنشر Anthropic
سياسة جديدة.
</Note>

تمرر الواجهة الخلفية المضمنة `codex-cli` من OpenAI موجه النظام الخاص بـ OpenClaw عبر
تجاوز إعداد `model_instructions_file` في Codex (`-c
model_instructions_file="..."`). لا يوفّر Codex علمًا بأسلوب Claude مثل
`--append-system-prompt`، لذا يكتب OpenClaw الموجه المُنشأ إلى
ملف مؤقت لكل جلسة جديدة من Codex CLI.

## الجلسات

- إذا كانت واجهة CLI تدعم الجلسات، فاضبط `sessionArg` (مثل `--session-id`) أو
  `sessionArgs` (العنصر النائب `{sessionId}`) عندما يلزم إدراج المعرّف
  في عدة أعلام.
- إذا كانت واجهة CLI تستخدم **أمرًا فرعيًا للاستئناف** مع أعلام مختلفة، فاضبط
  `resumeArgs` (يستبدل `args` عند الاستئناف) واختياريًا `resumeOutput`
  (لعمليات الاستئناف غير المعتمدة على JSON).
- `sessionMode`:
  - `always`: أرسل دائمًا معرّف جلسة (UUID جديد إذا لم يكن هناك معرّف محفوظ).
  - `existing`: أرسل معرّف جلسة فقط إذا كان قد تم حفظه من قبل.
  - `none`: لا ترسل معرّف جلسة مطلقًا.

ملاحظات حول التسلسل:

- `serialize: true` يبقي العمليات على المسار نفسه مرتبة.
- معظم واجهات CLI تسلسل التنفيذ على مسار موفر واحد.
- يسقط OpenClaw إعادة استخدام جلسة CLI المخزنة عندما تتغير حالة مصادقة الواجهة الخلفية، بما في ذلك إعادة تسجيل الدخول، أو تدوير الرمز، أو تغيير بيانات اعتماد ملف تعريف المصادقة.

## الصور (تمرير مباشر)

إذا كانت واجهة CLI تقبل مسارات الصور، فاضبط `imageArg`:

```json5
imageArg: "--image",
imageMode: "repeat"
```

سيكتب OpenClaw الصور المشفرة base64 إلى ملفات مؤقتة. إذا تم تعيين `imageArg`، فسيتم
تمرير هذه المسارات كوسائط CLI. وإذا لم يتم تعيين `imageArg`، فسيُلحق OpenClaw
مسارات الملفات بالموجه (حقن المسار)، وهو ما يكفي لواجهات CLI التي
تحمّل الملفات المحلية تلقائيًا من المسارات العادية.

## المدخلات / المخرجات

- `output: "json"` (الافتراضي) يحاول تحليل JSON واستخراج النص + معرّف الجلسة.
- بالنسبة إلى مخرجات JSON الخاصة بـ Gemini CLI، يقرأ OpenClaw نص الرد من `response` و
  الاستخدام من `stats` عندما يكون `usage` مفقودًا أو فارغًا.
- `output: "jsonl"` يحلل تدفقات JSONL (مثل Codex CLI `--json`) ويستخرج رسالة الوكيل النهائية بالإضافة إلى
  معرّفات الجلسة عند وجودها.
- `output: "text"` يتعامل مع stdout على أنه الاستجابة النهائية.

أوضاع الإدخال:

- `input: "arg"` (الافتراضي) يمرر الموجه كآخر وسيطة CLI.
- `input: "stdin"` يرسل الموجه عبر stdin.
- إذا كان الموجه طويلًا جدًا وتم تعيين `maxPromptArgChars`، فسيُستخدم stdin.

## القيم الافتراضية (مملوكة للإضافة)

تسجل إضافة OpenAI المضمنة أيضًا قيمة افتراضية لـ `codex-cli`:

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

تسجل إضافة Google المضمنة أيضًا قيمة افتراضية لـ `google-gemini-cli`:

- `command: "gemini"`
- `args: ["--output-format", "json", "--prompt", "{prompt}"]`
- `resumeArgs: ["--resume", "{sessionId}", "--output-format", "json", "--prompt", "{prompt}"]`
- `imageArg: "@"`
- `imagePathScope: "workspace"`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

المتطلب المسبق: يجب أن تكون Gemini CLI المحلية مثبتة ومتاحة باسم
`gemini` على `PATH` (`brew install gemini-cli` أو
`npm install -g @google/gemini-cli`).

ملاحظات JSON الخاصة بـ Gemini CLI:

- تتم قراءة نص الرد من حقل JSON `response`.
- يعود الاستخدام إلى `stats` عندما يكون `usage` غائبًا أو فارغًا.
- تتم تسوية `stats.cached` إلى OpenClaw `cacheRead`.
- إذا كان `stats.input` مفقودًا، يشتق OpenClaw رموز الإدخال من
  `stats.input_tokens - stats.cached`.

قم بالتجاوز فقط عند الحاجة (الشائع: مسار `command` مطلق).

## القيم الافتراضية المملوكة للإضافة

أصبحت القيم الافتراضية لواجهات CLI الخلفية الآن جزءًا من سطح الإضافة:

- تسجلها الإضافات باستخدام `api.registerCliBackend(...)`.
- يصبح `id` الخاص بالواجهة الخلفية هو بادئة الموفر في مراجع النماذج.
- يظل إعداد المستخدم في `agents.defaults.cliBackends.<id>` يتجاوز القيمة الافتراضية للإضافة.
- تبقى عملية تنظيف الإعداد الخاصة بالواجهة الخلفية مملوكة للإضافة عبر الخطاف
  الاختياري `normalizeConfig`.

## تراكبات Bundle MCP

لا تتلقى واجهات CLI الخلفية **استدعاءات أدوات OpenClaw** مباشرة، لكن يمكن للواجهة الخلفية
الاشتراك في تراكب إعداد MCP مُنشأ عبر `bundleMcp: true`.

السلوك المضمن الحالي:

- `claude-cli`: ملف إعداد MCP صارم مُنشأ
- `codex-cli`: تجاوزات إعدادات مضمنة لـ `mcp_servers`
- `google-gemini-cli`: ملف إعدادات نظام Gemini مُنشأ

عند تمكين bundle MCP، يقوم OpenClaw بما يلي:

- يشغّل خادم HTTP MCP محلي loopback يعرّض أدوات البوابة لعملية CLI
- يصادق الجسر باستخدام رمز مميز لكل جلسة (`OPENCLAW_MCP_TOKEN`)
- يقيّد الوصول إلى الأدوات وفق الجلسة الحالية والحساب وسياق القناة
- يحمّل خوادم bundle-MCP المفعلة لمساحة العمل الحالية
- يدمجها مع أي شكل إعدادات/تهيئة MCP موجود للواجهة الخلفية
- يعيد كتابة إعدادات التشغيل باستخدام وضع التكامل المملوك للواجهة الخلفية من الإضافة المالكة

إذا لم تكن أي خوادم MCP مفعلة، فسيظل OpenClaw يحقن إعدادًا صارمًا عندما
تشترك واجهة خلفية في bundle MCP حتى تبقى عمليات الخلفية معزولة.

## القيود

- **لا توجد استدعاءات مباشرة لأدوات OpenClaw.** لا يحقن OpenClaw استدعاءات الأدوات في
  بروتوكول واجهة CLI الخلفية. ترى الواجهات الخلفية أدوات البوابة فقط عندما تشترك في
  `bundleMcp: true`.
- **البث خاص بكل واجهة خلفية.** بعض الواجهات الخلفية تبث JSONL؛ بينما تقوم أخرى بالتخزين المؤقت
  حتى الخروج.
- **المخرجات المنظمة** تعتمد على تنسيق JSON الخاص بواجهة CLI.
- **جلسات Codex CLI** تُستأنف عبر مخرجات نصية (من دون JSONL)، وهو ما يجعلها أقل
  تنظيمًا من تشغيل `--json` الأولي. ومع ذلك، تستمر جلسات OpenClaw في العمل
  بشكل طبيعي.

## استكشاف الأخطاء وإصلاحها

- **لم يتم العثور على CLI**: اضبط `command` على مسار كامل.
- **اسم نموذج غير صحيح**: استخدم `modelAliases` لربط `provider/model` → نموذج CLI.
- **لا يوجد استمرار للجلسة**: تأكد من تعيين `sessionArg` وأن `sessionMode` ليس
  `none` (لا يمكن لـ Codex CLI حاليًا الاستئناف مع مخرجات JSON).
- **يتم تجاهل الصور**: اضبط `imageArg` (وتحقق من أن واجهة CLI تدعم مسارات الملفات).
