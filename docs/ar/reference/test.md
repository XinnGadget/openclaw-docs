---
read_when:
    - تشغيل الاختبارات أو إصلاحها
summary: كيفية تشغيل الاختبارات محليًا (vitest) ومتى تستخدم وضعي force/coverage
title: الاختبارات
x-i18n:
    generated_at: "2026-04-07T07:22:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: a25236a707860307cc324f32752ad13a53e448bee9341d8df2e11655561e841c
    source_path: reference/test.md
    workflow: 15
---

# الاختبارات

- عدة الاختبار الكاملة (المجموعات، المباشر، Docker): [الاختبار](/ar/help/testing)

- `pnpm test:force`: يقتل أي عملية بوابة متبقية تحتفظ بمنفذ التحكم الافتراضي، ثم يشغّل مجموعة Vitest الكاملة بمنفذ بوابة معزول حتى لا تتصادم اختبارات الخادم مع نسخة قيد التشغيل. استخدم هذا عندما يترك تشغيل سابق للبوابة المنفذ 18789 مشغولًا.
- `pnpm test:coverage`: يشغّل مجموعة اختبارات الوحدات مع تغطية V8 ‏(عبر `vitest.unit.config.ts`). الحدود العامة هي 70% للأسطر/الفروع/الدوال/العبارات. تستبعد التغطية نقاط الدخول الثقيلة تكامليًا (ربط CLI، وجسور gateway/telegram، وخادم webchat الثابت) للحفاظ على تركيز الهدف على المنطق القابل لاختبار الوحدات.
- `pnpm test:coverage:changed`: يشغّل تغطية اختبارات الوحدات فقط للملفات التي تغيّرت منذ `origin/main`.
- `pnpm test:changed`: يوسّع مسارات git المتغيرة إلى مسارات Vitest محددة النطاق عندما يلمس الفرق فقط ملفات المصدر/الاختبار القابلة للتوجيه. أما تغييرات الإعداد/التهيئة فتعود إلى تشغيل مشاريع الجذر الأصلية بحيث تعيد تعديلات التوصيل التشغيل على نطاق واسع عند الحاجة.
- `pnpm test`: يوجّه أهداف الملفات/الأدلة الصريحة عبر مسارات Vitest محددة النطاق. أمّا التشغيلات غير المستهدفة فتنفّذ الآن عشرة إعدادات شظايا متسلسلة (`vitest.full-core-unit-src.config.ts`, `vitest.full-core-unit-security.config.ts`, `vitest.full-core-unit-ui.config.ts`, `vitest.full-core-unit-support.config.ts`, `vitest.full-core-contracts.config.ts`, `vitest.full-core-bundled.config.ts`, `vitest.full-core-runtime.config.ts`, `vitest.full-agentic.config.ts`, `vitest.full-auto-reply.config.ts`, `vitest.full-extensions.config.ts`) بدلًا من عملية مشروع جذر عملاقة واحدة.
- توجَّه الآن ملفات اختبار `plugin-sdk` و `commands` المحددة عبر مسارات خفيفة مخصصة تُبقي فقط `test/setup.ts`، وتترك الحالات الثقيلة من جهة وقت التشغيل على مساراتها الحالية.
- كما تقوم ملفات المصدر المساعدة المحددة في `plugin-sdk` و `commands` أيضًا بربط `pnpm test:changed` باختبارات شقيقة صريحة في تلك المسارات الخفيفة، بحيث تتجنب التعديلات الصغيرة على المساعدات إعادة تشغيل المجموعات الثقيلة المدعومة بوقت التشغيل.
- تنقسم `auto-reply` الآن أيضًا إلى ثلاثة إعدادات مخصصة (`core`, `top-level`, `reply`) حتى لا تهيمن عدة الردود على اختبارات الحالة/الرمز/المساعد الأخف على المستوى الأعلى.
- يستخدم إعداد Vitest الأساسي الآن افتراضيًا `pool: "threads"` و `isolate: false`، مع تمكين المشغّل المشترك غير المعزول عبر إعدادات المستودع.
- `pnpm test:channels` يشغّل `vitest.channels.config.ts`.
- `pnpm test:extensions` يشغّل `vitest.extensions.config.ts`.
- `pnpm test:extensions`: يشغّل مجموعات الإضافات/Plugins.
- `pnpm test:perf:imports`: يفعّل تقارير مدة الاستيراد + تفصيلات الاستيراد في Vitest، مع الاستمرار في استخدام توجيه المسارات المحددة النطاق لأهداف الملفات/الأدلة الصريحة.
- `pnpm test:perf:imports:changed`: يطبّق profiling الاستيراد نفسه، ولكن فقط للملفات التي تغيّرت منذ `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` يقيس أداء مسار الوضع المتغير الموجّه مقابل تشغيل مشروع الجذر الأصلي لنفس فرق git الملتزم.
- `pnpm test:perf:changed:bench -- --worktree` يقيس مجموعة تغييرات worktree الحالية من دون عمل commit أولًا.
- `pnpm test:perf:profile:main`: يكتب ملف تعريف CPU للخيط الرئيسي في Vitest ‏(`.artifacts/vitest-main-profile`).
- `pnpm test:perf:profile:runner`: يكتب ملفات تعريف CPU + heap لمشغّل الوحدات (`.artifacts/vitest-runner-profile`).
- تكامل Gateway: الاشتراك اختياري عبر `OPENCLAW_TEST_INCLUDE_GATEWAY=1 pnpm test` أو `pnpm test:gateway`.
- `pnpm test:e2e`: يشغّل اختبارات smoke الشاملة للبوابة (إقران WS/HTTP/node متعدد النسخ). يستخدم افتراضيًا `threads` + `isolate: false` مع عمّال متكيّفين في `vitest.e2e.config.ts`; اضبطه عبر `OPENCLAW_E2E_WORKERS=<n>` وعيّن `OPENCLAW_E2E_VERBOSE=1` للحصول على سجلات مطوّلة.
- `pnpm test:live`: يشغّل الاختبارات المباشرة للمزوّدين (minimax/zai). يتطلب مفاتيح API و `LIVE=1` (أو `*_LIVE_TEST=1` الخاص بالمزوّد) لإزالة التخطي.
- `pnpm test:docker:openwebui`: يبدأ OpenClaw + Open WebUI داخل Docker، ويسجّل الدخول عبر Open WebUI، ويفحص `/api/models`، ثم يشغّل دردشة حقيقية عبر الوكيل من خلال `/api/chat/completions`. يتطلب مفتاح نموذج مباشر قابلًا للاستخدام (مثل OpenAI في `~/.profile`)، ويسحب صورة Open WebUI خارجية، ولا يُتوقع أن يكون مستقرًا في CI مثل مجموعات الوحدات/e2e العادية.
- `pnpm test:docker:mcp-channels`: يبدأ حاوية Gateway مهيأة مسبقًا وحاوية عميل ثانية تشغّل `openclaw mcp serve`، ثم يتحقق من اكتشاف المحادثات الموجّهة، وقراءات النصوص، وبيانات تعريف المرفقات، وسلوك قائمة انتظار الأحداث المباشرة، وتوجيه الإرسال الصادر، وإشعارات القناة + الأذونات على نمط Claude عبر جسر stdio الحقيقي. يقرأ تأكيد إشعارات Claude إطارات MCP الخام لـ stdio مباشرةً بحيث يعكس اختبار smoke ما يصدره الجسر فعلًا.

## بوابة PR المحلية

لفحوصات الهبوط/البوابة المحلية لـ PR، شغّل:

- `pnpm check`
- `pnpm build`
- `pnpm test`
- `pnpm check:docs`

إذا كان `pnpm test` غير مستقر على مضيف محمّل، فأعد تشغيله مرة واحدة قبل اعتباره تراجعًا، ثم اعزله باستخدام `pnpm test <path/to/test>`. وبالنسبة إلى المضيفين المقيّدين بالذاكرة، استخدم:

- `OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test`
- `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/tmp/openclaw-vitest-cache pnpm test:changed`

## معيار زمن استجابة النموذج (مفاتيح محلية)

البرنامج النصي: [`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

الاستخدام:

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- متغيرات البيئة الاختيارية: `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL`, `ANTHROPIC_API_KEY`
- المطالبة الافتراضية: “Reply with a single word: ok. No punctuation or extra text.”

آخر تشغيل (2025-12-31، ‏20 تشغيلًا):

- median لـ minimax: ‏1279ms ‏(الحد الأدنى 1114، الحد الأقصى 2431)
- median لـ opus: ‏2454ms ‏(الحد الأدنى 1224، الحد الأقصى 3170)

## معيار بدء تشغيل CLI

البرنامج النصي: [`scripts/bench-cli-startup.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-cli-startup.ts)

الاستخدام:

- `pnpm test:startup:bench`
- `pnpm test:startup:bench:smoke`
- `pnpm test:startup:bench:save`
- `pnpm test:startup:bench:update`
- `pnpm test:startup:bench:check`
- `pnpm tsx scripts/bench-cli-startup.ts`
- `pnpm tsx scripts/bench-cli-startup.ts --runs 12`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case status --case gatewayStatus --runs 3`
- `pnpm tsx scripts/bench-cli-startup.ts --entry openclaw.mjs --entry-secondary dist/entry.js --preset all`
- `pnpm tsx scripts/bench-cli-startup.ts --preset all --output .artifacts/cli-startup-bench-all.json`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case gatewayStatusJson --output .artifacts/cli-startup-bench-smoke.json`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --cpu-prof-dir .artifacts/cli-cpu`
- `pnpm tsx scripts/bench-cli-startup.ts --json`

الإعدادات المسبقة:

- `startup`: ‏`--version`، ‏`--help`، ‏`health`، ‏`health --json`، ‏`status --json`، ‏`status`
- `real`: ‏`health`، ‏`status`، ‏`status --json`، ‏`sessions`، ‏`sessions --json`، ‏`agents list --json`، ‏`gateway status`، ‏`gateway status --json`، ‏`gateway health --json`، ‏`config get gateway.port`
- `all`: كلا الإعدادين المسبقين

يتضمن الخرج `sampleCount`، وavg، وp50، وp95، والحدين الأدنى/الأقصى، وتوزيع exit-code/signal، وملخصات أعلى RSS لكل أمر. ويكتب `--cpu-prof-dir` / `--heap-prof-dir` الاختياري ملفات تعريف V8 لكل تشغيل بحيث يستخدم القياس الزمني والتقاط ملفات التعريف المشغّل نفسه.

اتفاقيات الخرج المحفوظ:

- يكتب `pnpm test:startup:bench:smoke` العنصر المستهدف لاختبار smoke في `.artifacts/cli-startup-bench-smoke.json`
- يكتب `pnpm test:startup:bench:save` عنصر المجموعة الكاملة في `.artifacts/cli-startup-bench-all.json` باستخدام `runs=5` و `warmup=1`
- يحدّث `pnpm test:startup:bench:update` ملف baseline المثبّت في `test/fixtures/cli-startup-bench.json` باستخدام `runs=5` و `warmup=1`

الملف المثبّت:

- `test/fixtures/cli-startup-bench.json`
- حدّثه باستخدام `pnpm test:startup:bench:update`
- قارن النتائج الحالية بالملف باستخدام `pnpm test:startup:bench:check`

## E2E للتهيئة (Docker)

Docker اختياري؛ وهذا مطلوب فقط لاختبارات smoke الخاصة بالتهيئة داخل الحاويات.

تدفق بدء تشغيل كامل من الصفر داخل حاوية Linux نظيفة:

```bash
scripts/e2e/onboard-docker.sh
```

يقود هذا البرنامج النصي المعالج التفاعلي عبر pseudo-tty، ويتحقق من ملفات الإعداد/مساحة العمل/الجلسة، ثم يبدأ البوابة ويشغّل `openclaw health`.

## اختبار smoke لاستيراد QR ‏(Docker)

يضمن أن `qrcode-terminal` يُحمّل ضمن بيئات Node المدعومة في Docker ‏(Node 24 افتراضيًا، وNode 22 متوافق):

```bash
pnpm test:docker:qr
```
