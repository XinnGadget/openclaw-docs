---
read_when:
    - تحتاج إلى فحص مخرجات النموذج الخام للكشف عن تسرّب الاستدلال
    - تريد تشغيل Gateway في وضع المراقبة أثناء التكرار
    - تحتاج إلى سير عمل متكرر لتصحيح الأخطاء
summary: 'أدوات تصحيح الأخطاء: وضع المراقبة، وتدفقات النموذج الخام، وتتبع تسرّب الاستدلال'
title: تصحيح الأخطاء
x-i18n:
    generated_at: "2026-04-12T23:28:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: bc31ce9b41e92a14c4309f32df569b7050b18024f83280930e53714d3bfcd5cc
    source_path: help/debugging.md
    workflow: 15
---

# تصحيح الأخطاء

تغطي هذه الصفحة أدوات المساعدة لتصحيح أخطاء المخرجات المتدفقة، خاصةً عندما
يمزج موفّر ما الاستدلال داخل النص العادي.

## تجاوزات التصحيح وقت التشغيل

استخدم `/debug` في الدردشة لتعيين تجاوزات إعداد **وقت التشغيل فقط** (في
الذاكرة، وليس على القرص). يكون `/debug` معطّلًا افتراضيًا؛ فعّله باستخدام
`commands.debug: true`.
وهذا مفيد عندما تحتاج إلى تبديل إعدادات غير شائعة بدون تعديل `openclaw.json`.

أمثلة:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

يؤدي `/debug reset` إلى مسح جميع التجاوزات والعودة إلى الإعدادات الموجودة على
القرص.

## مخرجات التتبع للجلسة

استخدم `/trace` عندما تريد رؤية أسطر التتبع/التصحيح المملوكة لـ Plugin في جلسة
واحدة بدون تشغيل الوضع المطوّل الكامل.

أمثلة:

```text
/trace
/trace on
/trace off
```

استخدم `/trace` لتشخيصات Plugin مثل ملخصات تصحيح Active Memory.
واستمر في استخدام `/verbose` لحالة الإخراج المطوّلة العادية/مخرجات الأدوات،
واستمر في استخدام `/debug` لتجاوزات الإعداد الخاصة بوقت التشغيل فقط.

## وضع المراقبة في Gateway

للتكرار السريع، شغّل الـ Gateway تحت مراقب الملفات:

```bash
pnpm gateway:watch
```

وهذا يعادل:

```bash
node scripts/watch-node.mjs gateway --force
```

يعيد المراقب التشغيل عند حدوث تغييرات في الملفات ذات الصلة بالبناء ضمن `src/`،
وملفات مصدر الإضافات، وملفات `package.json` و`openclaw.plugin.json` الوصفية
للإضافات، و`tsconfig.json`، و`package.json`، و`tsdown.config.ts`. تؤدي تغييرات
البيانات الوصفية للإضافات إلى إعادة تشغيل الـ Gateway دون فرض إعادة بناء
`tsdown`؛ أما تغييرات المصدر والإعدادات فتستمر في إعادة بناء `dist` أولًا.

أضف أي أعلام CLI للـ Gateway بعد `gateway:watch` وسيتم تمريرها في كل إعادة
تشغيل. تؤدي إعادة تشغيل أمر المراقبة نفسه للمستودع نفسه/ومجموعة الأعلام نفسها
الآن إلى استبدال المراقب الأقدم بدلًا من ترك عمليات مراقبة أصلية مكررة في الخلفية.

## ملف تعريف التطوير + Gateway التطوير (`--dev`)

استخدم ملف تعريف التطوير لعزل الحالة وإنشاء بيئة آمنة ومؤقتة للتصحيح. توجد
رايتا `--dev` **اثنتان**:

- **الراية العامة `--dev` (ملف التعريف):** تعزل الحالة تحت `~/.openclaw-dev`
  وتجعل منفذ الـ Gateway الافتراضي `19001` (وتتغير المنافذ المشتقة معه).
- **`gateway --dev`:** يوجّه Gateway إلى إنشاء إعداد افتراضي + مساحة عمل
  تلقائيًا عند عدم وجودهما (وتخطي `BOOTSTRAP.md`).

التدفق الموصى به (ملف تعريف التطوير + إقلاع التطوير):

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

إذا لم يكن لديك تثبيت عام بعد، فشغّل CLI عبر `pnpm openclaw ...`.

ما الذي يفعله هذا:

1. **عزل ملف التعريف** (الراية العامة `--dev`)
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001` (وتتغير منافذ browser/canvas وفقًا لذلك)

2. **إقلاع التطوير** (`gateway --dev`)
   - يكتب إعدادًا مصغرًا إذا لم يكن موجودًا (`gateway.mode=local`، وربط
     loopback).
   - يعيّن `agent.workspace` إلى مساحة عمل التطوير.
   - يعيّن `agent.skipBootstrap=true` (بدون `BOOTSTRAP.md`).
   - يملأ ملفات مساحة العمل إذا لم تكن موجودة:
     `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`.
   - الهوية الافتراضية: **C3‑PO** (روبوت بروتوكول).
   - يتخطى موفّري القنوات في وضع التطوير (`OPENCLAW_SKIP_CHANNELS=1`).

تدفق إعادة التعيين (بداية جديدة):

```bash
pnpm gateway:dev:reset
```

ملاحظة: `--dev` هي راية **عامة** لملف التعريف وتقوم بعض المشغلات باستهلاكها.
إذا احتجت إلى كتابتها صراحةً، فاستخدم صيغة متغير البيئة:

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

يؤدي `--reset` إلى مسح الإعدادات وبيانات الاعتماد والجلسات ومساحة عمل التطوير
(باستخدام `trash`، وليس `rm`) ثم يعيد إنشاء إعداد التطوير الافتراضي.

نصيحة: إذا كان Gateway غير مخصّص للتطوير يعمل بالفعل (`launchd/systemd`)،
فأوقفه أولًا:

```bash
openclaw gateway stop
```

## تسجيل التدفق الخام (OpenClaw)

يمكن لـ OpenClaw تسجيل **تدفق المساعد الخام** قبل أي ترشيح/تنسيق.
وهذه أفضل طريقة لمعرفة ما إذا كان الاستدلال يصل على شكل فروقات نصية عادية
أم على شكل كتل تفكير منفصلة.

فعّله عبر CLI:

```bash
pnpm gateway:watch --raw-stream
```

تجاوز اختياري للمسار:

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

متغيرات البيئة المكافئة:

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

الملف الافتراضي:

`~/.openclaw/logs/raw-stream.jsonl`

## تسجيل المقاطع الخام (pi-mono)

لالتقاط **مقاطع OpenAI-compat الخام** قبل تحليلها إلى كتل،
يقدّم pi-mono مسجلًا منفصلًا:

```bash
PI_RAW_STREAM=1
```

مسار اختياري:

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

الملف الافتراضي:

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> ملاحظة: لا يتم إصدار هذا إلا من العمليات التي تستخدم موفّر
> `openai-completions` الخاص بـ pi-mono.

## ملاحظات السلامة

- قد تتضمن سجلات التدفق الخام المطالبات الكاملة ومخرجات الأدوات وبيانات المستخدم.
- احتفظ بالسجلات محليًا واحذفها بعد الانتهاء من التصحيح.
- إذا شاركت السجلات، فنقّح الأسرار ومعلومات التعريف الشخصية أولًا.
