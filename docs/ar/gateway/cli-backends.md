---
read_when:
    - تريد آلية احتياطية موثوقة عندما يفشل موفرو API
    - أنت تشغّل Codex CLI أو غيره من واجهات CLI المحلية للذكاء الاصطناعي وتريد إعادة استخدامها
    - تريد فهم جسر MCP عبر local loopback للوصول إلى أدوات الخلفية الخاصة بـ CLI
summary: 'خلفيات CLI: آلية احتياطية محلية لـ CLI للذكاء الاصطناعي مع جسر أدوات MCP اختياري'
title: خلفيات CLI
x-i18n:
    generated_at: "2026-04-16T19:31:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 381273532a8622bc4628000a6fb999712b12af08faade2b5f2b7ac4cc7d23efe
    source_path: gateway/cli-backends.md
    workflow: 15
---

# خلفيات CLI (بيئة تشغيل احتياطية)

يمكن لـ OpenClaw تشغيل **واجهات CLI محلية للذكاء الاصطناعي** كـ **آلية احتياطية نصية فقط** عندما تتعطل موفّرات API،
أو تُقيَّد بالمعدل، أو تُظهر سلوكًا غير مستقر مؤقتًا. هذا التصميم متحفّظ عمدًا:

- **لا يتم حقن أدوات OpenClaw مباشرة**، لكن الخلفيات التي تضبط `bundleMcp: true`
  يمكنها تلقي أدوات Gateway عبر جسر MCP محلي loopback.
- **بث JSONL** لواجهات CLI التي تدعمه.
- **الجلسات مدعومة** (حتى تظل الجولات اللاحقة مترابطة).
- **يمكن تمرير الصور** إذا كانت واجهة CLI تقبل مسارات الصور.

هذا مصمم ليكون **شبكة أمان** لا مسارًا أساسيًا. استخدمه عندما
تريد ردودًا نصية "تعمل دائمًا" من دون الاعتماد على API خارجية.

إذا كنت تريد بيئة تشغيل كاملة مع عناصر تحكم جلسات ACP، والمهام الخلفية،
وربط الخيوط/المحادثات، وجلسات ترميز خارجية مستمرة، فاستخدم
[وكلاء ACP](/ar/tools/acp-agents) بدلًا من ذلك. خلفيات CLI ليست ACP.

## بداية سريعة مناسبة للمبتدئين

يمكنك استخدام Codex CLI **من دون أي إعداد** (إذ إن Plugin OpenAI المضمّن
يسجل خلفية افتراضية):

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

إذا كان Gateway يعمل تحت launchd/systemd وكان PATH محدودًا، فأضف فقط
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

هذا كل شيء. لا مفاتيح، ولا إعدادات مصادقة إضافية مطلوبة بخلاف ما يخص CLI نفسه.

إذا كنت تستخدم خلفية CLI مضمّنة كـ **موفّر الرسائل الأساسي** على
مضيف Gateway، فإن OpenClaw يقوم الآن بتحميل Plugin المضمّن المالك تلقائيًا عندما
يشير إعدادك صراحة إلى تلك الخلفية في مرجع نموذج أو تحت
`agents.defaults.cliBackends`.

## استخدامه كآلية احتياطية

أضف خلفية CLI إلى قائمة الآليات الاحتياطية بحيث لا تعمل إلا عند فشل النماذج الأساسية:

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

- إذا كنت تستخدم `agents.defaults.models` (قائمة السماح)، فيجب عليك تضمين نماذج خلفية CLI هناك أيضًا.
- إذا فشل الموفّر الأساسي (المصادقة، حدود المعدل، المهلات)، فسيحاول OpenClaw
  استخدام خلفية CLI بعده.

## نظرة عامة على الإعداد

توجد كل خلفيات CLI تحت:

```
agents.defaults.cliBackends
```

كل إدخال يُعرَّف بواسطة **معرّف موفّر** (مثل `codex-cli` أو `my-cli`).
ويصبح معرّف الموفّر هو الطرف الأيسر من مرجع النموذج:

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
          // يمكن لواجهات CLI بأسلوب Codex الإشارة إلى ملف prompt بدلًا من ذلك:
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

1. **يحدد خلفية** بناءً على بادئة الموفّر (`codex-cli/...`).
2. **يبني prompt نظام** باستخدام نفس prompt الخاص بـ OpenClaw وسياق مساحة العمل.
3. **ينفذ CLI** باستخدام معرّف جلسة (إن كان مدعومًا) حتى يظل السجل متسقًا.
4. **يحلل المخرجات** (`JSON` أو نص عادي) ويعيد النص النهائي.
5. **يحفظ معرّفات الجلسات** لكل خلفية، بحيث تعيد الجولات اللاحقة استخدام جلسة CLI نفسها.

<Note>
أصبحت الخلفية المضمّنة `claude-cli` من Anthropic مدعومة مجددًا. وقد أخبرنا موظفو Anthropic
أن استخدام Claude CLI بأسلوب OpenClaw مسموح به مرة أخرى، لذا يعامل OpenClaw
استخدام `claude -p` على أنه معتمد لهذا التكامل ما لم تنشر Anthropic
سياسة جديدة.
</Note>

تقوم الخلفية المضمّنة `codex-cli` من OpenAI بتمرير prompt النظام الخاص بـ OpenClaw
عبر تجاوز إعداد `model_instructions_file` في Codex (`-c
model_instructions_file="..."`). لا يوفّر Codex
علمًا بأسلوب Claude مثل `--append-system-prompt`، لذا يكتب OpenClaw prompt المُجمّع إلى
ملف مؤقت لكل جلسة Codex CLI جديدة.

تستقبل الخلفية المضمّنة `claude-cli` من Anthropic لقطة Skills الخاصة بـ OpenClaw
بطريقتين: كتالوج Skills المضغوط الخاص بـ OpenClaw داخل prompt النظام المُلحق، و
Claude Code Plugin مؤقت يُمرَّر عبر `--plugin-dir`. يحتوي Plugin
فقط على Skills المؤهلة لذلك الوكيل/تلك الجلسة، بحيث يرى محلّل Skills الأصلي في Claude Code
نفس المجموعة المُفلترة التي كان OpenClaw سيعلن عنها داخل
prompt. وما تزال تجاوزات env/API key الخاصة بـ Skills تُطبَّق من OpenClaw على
بيئة العملية الفرعية أثناء التشغيل.

## الجلسات

- إذا كانت واجهة CLI تدعم الجلسات، فاضبط `sessionArg` (مثل `--session-id`) أو
  `sessionArgs` (العنصر النائب `{sessionId}`) عندما يلزم إدراج المعرّف
  في عدة أعلام.
- إذا كانت واجهة CLI تستخدم **أمرًا فرعيًا للاستئناف** مع أعلام مختلفة، فاضبط
  `resumeArgs` (يستبدل `args` عند الاستئناف) واختياريًا `resumeOutput`
  (للاستئناف غير المعتمد على JSON).
- `sessionMode`:
  - `always`: أرسل معرّف جلسة دائمًا (UUID جديد إذا لم يكن هناك معرّف محفوظ).
  - `existing`: أرسل معرّف جلسة فقط إذا كان محفوظًا مسبقًا.
  - `none`: لا ترسل معرّف جلسة أبدًا.

ملاحظات حول التسلسل:

- `serialize: true` يحافظ على ترتيب التشغيلات ضمن المسار نفسه.
- معظم واجهات CLI تسلسل العمليات على مسار موفّر واحد.
- يتخلى OpenClaw عن إعادة استخدام جلسة CLI المخزنة عندما تتغير حالة مصادقة الخلفية، بما في ذلك إعادة تسجيل الدخول، أو تدوير الرمز المميز، أو تغيير بيانات اعتماد ملف تعريف المصادقة.

## الصور (تمرير مباشر)

إذا كانت واجهة CLI تقبل مسارات الصور، فاضبط `imageArg`:

```json5
imageArg: "--image",
imageMode: "repeat"
```

سيكتب OpenClaw الصور المشفرة base64 إلى ملفات مؤقتة. إذا كان `imageArg` مضبوطًا، فستُمرَّر
تلك المسارات كوسائط CLI. وإذا لم يكن `imageArg` موجودًا، فسيُلحق OpenClaw
مسارات الملفات إلى prompt (حقن المسار)، وهذا يكفي لواجهات CLI التي
تحمّل الملفات المحلية تلقائيًا من المسارات النصية العادية.

## المدخلات / المخرجات

- `output: "json"` (الافتراضي) يحاول تحليل JSON واستخراج النص + معرّف الجلسة.
- بالنسبة إلى مخرجات JSON الخاصة بـ Gemini CLI، يقرأ OpenClaw نص الرد من `response` و
  بيانات الاستخدام من `stats` عندما يكون `usage` مفقودًا أو فارغًا.
- `output: "jsonl"` يحلل تدفقات JSONL (مثل Codex CLI `--json`) ويستخرج رسالة الوكيل النهائية بالإضافة إلى معرّفات الجلسة
  عندما تكون موجودة.
- `output: "text"` يعامل stdout على أنه الاستجابة النهائية.

أنماط الإدخال:

- `input: "arg"` (الافتراضي) يمرر prompt كآخر وسيط CLI.
- `input: "stdin"` يرسل prompt عبر stdin.
- إذا كان prompt طويلًا جدًا وكان `maxPromptArgChars` مضبوطًا، فسيُستخدم stdin.

## القيم الافتراضية (مملوكة لـ Plugin)

يسجّل Plugin OpenAI المضمّن أيضًا قيمة افتراضية لـ `codex-cli`:

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","-c","sandbox_mode=\"workspace-write\"","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

ويسجّل Plugin Google المضمّن أيضًا قيمة افتراضية لـ `google-gemini-cli`:

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

- يُقرأ نص الرد من الحقل `response` في JSON.
- يعتمد الاستخدام على `stats` كبديل عندما يكون `usage` غائبًا أو فارغًا.
- تُطبَّع `stats.cached` إلى `cacheRead` في OpenClaw.
- إذا كان `stats.input` مفقودًا، يشتق OpenClaw رموز الإدخال من
  `stats.input_tokens - stats.cached`.

لا تُجرِ تجاوزًا إلا عند الحاجة (الشائع: مسار `command` مطلق).

## القيم الافتراضية المملوكة لـ Plugin

أصبحت القيم الافتراضية لخلفيات CLI الآن جزءًا من واجهة Plugin:

- تسجلها Plugins عبر `api.registerCliBackend(...)`.
- يصبح `id` الخاص بالخلفية هو بادئة الموفّر في مراجع النماذج.
- ما يزال إعداد المستخدم في `agents.defaults.cliBackends.<id>` يتجاوز القيمة الافتراضية الخاصة بـ Plugin.
- تبقى تنقية الإعداد الخاصة بالخلفية مملوكة لـ Plugin عبر
  الخطاف الاختياري `normalizeConfig`.

يمكن لـ Plugins التي تحتاج إلى طبقات توافق صغيرة جدًا لـ prompt/الرسائل أن تعلن
تحويلات نصية ثنائية الاتجاه من دون استبدال موفّر أو خلفية CLI:

```typescript
api.registerTextTransforms({
  input: [
    { from: /red basket/g, to: "blue basket" },
    { from: /paper ticket/g, to: "digital ticket" },
    { from: /left shelf/g, to: "right shelf" },
  ],
  output: [
    { from: /blue basket/g, to: "red basket" },
    { from: /digital ticket/g, to: "paper ticket" },
    { from: /right shelf/g, to: "left shelf" },
  ],
});
```

يعيد `input` كتابة prompt النظام وprompt المستخدم الممرَّرين إلى CLI. ويعيد `output`
كتابة تدفقات deltas الخاصة بالمساعد والنص النهائي المحلَّل قبل أن يعالج OpenClaw
علامات التحكم الخاصة به وتسليم القناة.

بالنسبة إلى واجهات CLI التي تُخرج JSONL متوافقًا مع stream-json الخاص بـ Claude Code، اضبط
`jsonlDialect: "claude-stream-json"` في إعداد تلك الخلفية.

## تراكبات Bundle MCP

لا تتلقى خلفيات CLI **استدعاءات أدوات OpenClaw مباشرة**، لكن يمكن لخلفية ما
أن تفعل الاشتراك في تراكب إعداد MCP مُولَّد عبر `bundleMcp: true`.

السلوك المضمّن الحالي:

- `claude-cli`: ملف إعداد MCP صارم مُولَّد
- `codex-cli`: تجاوزات إعداد مضمنة لـ `mcp_servers`
- `google-gemini-cli`: ملف إعدادات نظام Gemini مُولَّد

عند تمكين bundle MCP، يقوم OpenClaw بما يلي:

- يشغّل خادم HTTP MCP محلي loopback يعرّض أدوات Gateway لعملية CLI
- يصادق الجسر باستخدام رمز مميز لكل جلسة (`OPENCLAW_MCP_TOKEN`)
- يقيّد الوصول إلى الأدوات بحسب الجلسة الحالية، والحساب، وسياق القناة
- يحمّل خوادم bundle-MCP المُمكّنة لمساحة العمل الحالية
- يدمجها مع أي شكل إعداد/ضبط MCP موجود للخلفية
- يعيد كتابة إعداد التشغيل باستخدام نمط التكامل المملوك للخلفية من الامتداد المالك

إذا لم تكن أي خوادم MCP مُمكّنة، فسيظل OpenClaw يحقن إعدادًا صارمًا عندما
تشترك خلفية ما في bundle MCP حتى تبقى التشغيلات الخلفية معزولة.

## القيود

- **لا توجد استدعاءات مباشرة لأدوات OpenClaw.** لا يحقن OpenClaw استدعاءات الأدوات في
  بروتوكول خلفية CLI. لا ترى الخلفيات أدوات Gateway إلا عندما تشترك في
  `bundleMcp: true`.
- **البث خاص بالخلفية.** بعض الخلفيات تبث JSONL؛ وأخرى تُخزّن
  حتى الخروج.
- **المخرجات المهيكلة** تعتمد على تنسيق JSON الخاص بـ CLI.
- **جلسات Codex CLI** تستأنف عبر مخرجات نصية (من دون JSONL)، وهذا أقل
  هيكلة من تشغيل `--json` الأولي. وما تزال جلسات OpenClaw تعمل
  بشكل طبيعي.

## استكشاف الأخطاء وإصلاحها

- **تعذر العثور على CLI**: اضبط `command` على مسار كامل.
- **اسم النموذج غير صحيح**: استخدم `modelAliases` لربط `provider/model` → نموذج CLI.
- **لا يوجد استمرارية للجلسة**: تأكد من ضبط `sessionArg` وأن `sessionMode` ليس
  `none` (لا يستطيع Codex CLI حاليًا الاستئناف مع مخرجات JSON).
- **يتم تجاهل الصور**: اضبط `imageArg` (وتحقق من أن CLI يدعم مسارات الملفات).
