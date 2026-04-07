---
read_when:
    - تريد بديلًا موثوقًا عندما يفشل موفرو API
    - أنت تشغّل Codex CLI أو غيره من واجهات AI CLI المحلية وتريد إعادة استخدامها
    - تريد فهم جسر local loopback MCP لوصول أدوات الواجهة الخلفية CLI
summary: 'واجهات CLI الخلفية: بديل محلي لـ AI CLI مع جسر أدوات MCP اختياري'
title: واجهات CLI الخلفية
x-i18n:
    generated_at: "2026-04-07T07:17:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: f061357f420455ad6ffaabe7fe28f1fb1b1769d73a4eb2e6f45c6eb3c2e36667
    source_path: gateway/cli-backends.md
    workflow: 15
---

# واجهات CLI الخلفية (بيئة تشغيل احتياطية)

يمكن لـ OpenClaw تشغيل **واجهات AI CLI محلية** كـ **بديل نصي فقط** عندما تتعطل موفرو API،
أو تُقيَّد بالمعدل، أو تسيء التصرف مؤقتًا. هذا النهج متحفظ عمدًا:

- **لا يتم حقن أدوات OpenClaw مباشرة**، لكن الواجهات الخلفية التي تحتوي على `bundleMcp: true`
  يمكنها تلقي أدوات gateway عبر جسر MCP من نوع local loopback.
- **بث JSONL** لواجهات CLI التي تدعمه.
- **الجلسات مدعومة** (بحيث تبقى المنعطفات اللاحقة متماسكة).
- **يمكن تمرير الصور** إذا كانت واجهة CLI تقبل مسارات الصور.

تم تصميم ذلك ليكون **شبكة أمان** بدلًا من كونه مسارًا أساسيًا. استخدمه عندما
تريد ردودًا نصية "تعمل دائمًا" من دون الاعتماد على API خارجية.

إذا كنت تريد بيئة تشغيل كاملة مع عناصر تحكم جلسات ACP، والمهام الخلفية،
وربط الخيوط/المحادثات، وجلسات ترميز خارجية دائمة، فاستخدم
[ACP Agents](/ar/tools/acp-agents) بدلًا من ذلك. واجهات CLI الخلفية ليست ACP.

## بداية سريعة مناسبة للمبتدئين

يمكنك استخدام Codex CLI **من دون أي إعدادات** (يسجل plugin OpenAI
المضمن واجهة خلفية افتراضية):

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

إذا كانت gateway تعمل تحت launchd/systemd وكان PATH محدودًا، فأضف فقط
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

هذا كل شيء. لا مفاتيح، ولا حاجة إلى إعدادات مصادقة إضافية تتجاوز ما تتطلبه CLI نفسها.

إذا كنت تستخدم واجهة CLI خلفية مضمنة باعتبارها **موفر الرسائل الأساسي** على
مضيف gateway، فإن OpenClaw يحمّل الآن تلقائيًا plugin المضمن المالك عندما
تشير إعداداتك صراحةً إلى تلك الواجهة الخلفية في مرجع نموذج أو تحت
`agents.defaults.cliBackends`.

## استخدامه كبديل احتياطي

أضف واجهة CLI خلفية إلى قائمة البدائل الاحتياطية لديك بحيث تعمل فقط عند فشل النماذج الأساسية:

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

- إذا كنت تستخدم `agents.defaults.models` (قائمة السماح)، فيجب أن تتضمن نماذج واجهات CLI الخلفية هناك أيضًا.
- إذا فشل الموفر الأساسي (المصادقة، أو حدود المعدل، أو انتهاء المهلة)، فسيحاول OpenClaw
  استخدام واجهة CLI الخلفية بعد ذلك.

## نظرة عامة على الإعدادات

توجد جميع واجهات CLI الخلفية تحت:

```
agents.defaults.cliBackends
```

يُفهرس كل إدخال بواسطة **معرّف موفر** (مثل `codex-cli` أو `my-cli`).
ويصبح معرّف الموفر هو الجزء الأيسر من مرجع النموذج:

```
<provider>/<model>
```

### مثال على الإعدادات

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

1. **يختار واجهة خلفية** بناءً على بادئة الموفر (`codex-cli/...`).
2. **يبني توجيه نظام** باستخدام توجيه OpenClaw نفسه + سياق مساحة العمل.
3. **ينفذ CLI** باستخدام معرّف جلسة (إذا كان مدعومًا) حتى يبقى السجل متسقًا.
4. **يحلل المخرجات** (JSON أو نص عادي) ويعيد النص النهائي.
5. **يحفظ معرّفات الجلسات** لكل واجهة خلفية، بحيث تعيد المتابعات استخدام جلسة CLI نفسها.

<Note>
واجهة `claude-cli` الخلفية المضمنة الخاصة بـ Anthropic مدعومة مرة أخرى. أخبرنا
موظفو Anthropic أن استخدام Claude CLI بأسلوب OpenClaw مسموح به مجددًا، لذا
يتعامل OpenClaw مع استخدام `claude -p` على أنه معتمد لهذا التكامل ما لم تنشر
Anthropic سياسة جديدة.
</Note>

## الجلسات

- إذا كانت CLI تدعم الجلسات، فاضبط `sessionArg` (مثل `--session-id`) أو
  `sessionArgs` (العنصر النائب `{sessionId}`) عندما يلزم إدراج
  المعرّف في عدة علامات.
- إذا كانت CLI تستخدم **أمرًا فرعيًا للاستئناف** بعلامات مختلفة، فاضبط
  `resumeArgs` (يستبدل `args` عند الاستئناف) ويمكنك اختياريًا ضبط `resumeOutput`
  (للاستئنافات غير المعتمدة على JSON).
- `sessionMode`:
  - `always`: أرسل دائمًا معرّف جلسة (UUID جديد إذا لم يكن هناك معرّف مخزن).
  - `existing`: أرسل معرّف جلسة فقط إذا كان قد تم تخزينه مسبقًا.
  - `none`: لا ترسل أبدًا معرّف جلسة.

ملاحظات حول التسلسل:

- `serialize: true` يُبقي عمليات التشغيل في المسار نفسه مرتبة.
- تسلسل معظم واجهات CLI يتم على مسار موفر واحد.
- يسقط OpenClaw إعادة استخدام جلسة CLI المخزنة عندما تتغير حالة مصادقة الواجهة الخلفية، بما في ذلك إعادة تسجيل الدخول، أو تدوير الرموز، أو تغيير بيانات اعتماد ملف تعريف المصادقة.

## الصور (تمرير مباشر)

إذا كانت CLI تقبل مسارات الصور، فاضبط `imageArg`:

```json5
imageArg: "--image",
imageMode: "repeat"
```

سيكتب OpenClaw الصور المشفرة بصيغة base64 إلى ملفات مؤقتة. إذا تم ضبط `imageArg`،
فسيتم تمرير تلك المسارات كوسائط CLI. وإذا لم يكن `imageArg` موجودًا، فسيُلحق OpenClaw
مسارات الملفات بالتوجيه (حقن المسار)، وهذا يكفي لواجهات CLI التي تحمّل
الملفات المحلية تلقائيًا من المسارات النصية العادية.

## المدخلات / المخرجات

- `output: "json"` (الافتراضي) يحاول تحليل JSON واستخراج النص + معرّف الجلسة.
- بالنسبة إلى مخرجات JSON الخاصة بـ Gemini CLI، يقرأ OpenClaw نص الرد من `response` و
  الاستخدام من `stats` عندما يكون `usage` مفقودًا أو فارغًا.
- `output: "jsonl"` يحلل تدفقات JSONL (مثل Codex CLI `--json`) ويستخرج رسالة العامل النهائية بالإضافة إلى
  معرّفات الجلسة عند وجودها.
- `output: "text"` يتعامل مع stdout باعتباره الاستجابة النهائية.

أنماط الإدخال:

- `input: "arg"` (الافتراضي) يمرر التوجيه باعتباره آخر وسيط CLI.
- `input: "stdin"` يرسل التوجيه عبر stdin.
- إذا كان التوجيه طويلًا جدًا وكان `maxPromptArgChars` مضبوطًا، فسيتم استخدام stdin.

## القيم الافتراضية (مملوكة لـ plugin)

يسجل plugin OpenAI المضمن أيضًا قيمة افتراضية لـ `codex-cli`:

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

يسجل plugin Google المضمن أيضًا قيمة افتراضية لـ `google-gemini-cli`:

- `command: "gemini"`
- `args: ["--prompt", "--output-format", "json"]`
- `resumeArgs: ["--resume", "{sessionId}", "--prompt", "--output-format", "json"]`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

المتطلب المسبق: يجب أن تكون Gemini CLI المحلية مثبتة ومتاحة باسم
`gemini` على `PATH` (`brew install gemini-cli` أو
`npm install -g @google/gemini-cli`).

ملاحظات JSON الخاصة بـ Gemini CLI:

- يُقرأ نص الرد من حقل JSON `response`.
- يعود الاستخدام إلى `stats` عندما يكون `usage` غائبًا أو فارغًا.
- تتم تسوية `stats.cached` إلى OpenClaw `cacheRead`.
- إذا كان `stats.input` مفقودًا، يشتق OpenClaw رموز الإدخال من
  `stats.input_tokens - stats.cached`.

لا تُجرِ تجاوزًا إلا عند الحاجة (الأكثر شيوعًا: مسار `command` المطلق).

## القيم الافتراضية المملوكة لـ plugin

أصبحت القيم الافتراضية لواجهات CLI الخلفية الآن جزءًا من سطح plugin:

- تسجلها Plugins باستخدام `api.registerCliBackend(...)`.
- يصبح `id` الخاص بالواجهة الخلفية هو بادئة الموفر في مراجع النماذج.
- تظل إعدادات المستخدم في `agents.defaults.cliBackends.<id>` تتجاوز القيمة الافتراضية الخاصة بـ plugin.
- تبقى تنقية الإعدادات الخاصة بالواجهة الخلفية مملوكة لـ plugin من خلال الخطاف الاختياري
  `normalizeConfig`.

## تراكبات bundle MCP

لا تتلقى واجهات CLI الخلفية **استدعاءات أدوات OpenClaw مباشرة**، لكن يمكن لواجهة خلفية
أن تشترك في تراكب إعداد MCP مُولَّد عبر `bundleMcp: true`.

السلوك المضمن الحالي:

- `codex-cli`: لا يوجد تراكب bundle MCP
- `google-gemini-cli`: لا يوجد تراكب bundle MCP

عند تمكين bundle MCP، يقوم OpenClaw بما يلي:

- يشغّل خادم HTTP MCP من نوع loopback يعرّض أدوات gateway لعملية CLI
- يصادق الجسر باستخدام رمز مميز لكل جلسة (`OPENCLAW_MCP_TOKEN`)
- يقيّد وصول الأدوات بسياق الجلسة والحساب والقناة الحالية
- يحمّل خوادم bundle-MCP الممكّنة لمساحة العمل الحالية
- يدمجها مع أي `--mcp-config` موجود للواجهة الخلفية
- يعيد كتابة وسائط CLI لتمرير `--strict-mcp-config --mcp-config <generated-file>`

إذا لم تكن أي خوادم MCP مفعّلة، فسيظل OpenClaw يحقن إعدادًا صارمًا عندما
تشترك واجهة خلفية في bundle MCP حتى تظل عمليات التشغيل الخلفية معزولة.

## القيود

- **لا توجد استدعاءات مباشرة لأدوات OpenClaw.** لا يحقن OpenClaw استدعاءات الأدوات ضمن
  بروتوكول واجهة CLI الخلفية. لا ترى الواجهات الخلفية أدوات gateway إلا عندما تشترك في
  `bundleMcp: true`.
- **البث خاص بالواجهة الخلفية.** بعض الواجهات الخلفية تبث JSONL؛ بينما تخزن أخرى
  كل شيء مؤقتًا حتى الخروج.
- **المخرجات المنظمة** تعتمد على تنسيق JSON الخاص بـ CLI.
- **جلسات Codex CLI** تُستأنف عبر مخرجات نصية (وليس JSONL)، وهو ما يجعلها أقل
  تنظيمًا من تشغيل `--json` الأولي. ومع ذلك، تظل جلسات OpenClaw تعمل
  بشكل طبيعي.

## استكشاف الأخطاء وإصلاحها

- **لم يتم العثور على CLI**: اضبط `command` على مسار كامل.
- **اسم نموذج غير صحيح**: استخدم `modelAliases` لربط `provider/model` → نموذج CLI.
- **لا يوجد استمرارية للجلسة**: تأكد من ضبط `sessionArg` وأن `sessionMode` ليس
  `none` (لا يمكن لـ Codex CLI حاليًا الاستئناف بمخرجات JSON).
- **تم تجاهل الصور**: اضبط `imageArg` (وتأكد من أن CLI تدعم مسارات الملفات).
