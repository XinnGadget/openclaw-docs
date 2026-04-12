---
read_when:
    - تريد معرفة دائمة تتجاوز ملاحظات `MEMORY.md` العادية
    - أنت تقوم بتهيئة Plugin المضمّن memory-wiki
    - تريد فهم `wiki_search` أو `wiki_get` أو وضع الجسر
summary: 'ويكي الذاكرة: مخزن معرفة مُجمَّع مع مصدرية، وادعاءات، ولوحات معلومات، ووضع الجسر'
title: ويكي الذاكرة
x-i18n:
    generated_at: "2026-04-12T23:28:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 44d168a7096f744c56566ecac57499192eb101b4dd8a78e1b92f3aa0d6da3ad1
    source_path: plugins/memory-wiki.md
    workflow: 15
---

# ويكي الذاكرة

`memory-wiki` هو Plugin مضمّن يحوّل الذاكرة الدائمة إلى مخزن معرفة مُجمَّع.

وهو **لا** يستبدل Plugin الذاكرة النشطة. فما يزال Plugin الذاكرة النشطة مسؤولًا
عن الاستدعاء والترقية والفهرسة وDreaming. ويأتي `memory-wiki` إلى جانبه ويجمع
المعرفة الدائمة في ويكي قابل للتصفح مع صفحات حتمية، وادعاءات منظّمة، ومصدرية،
ولوحات معلومات، وملخصات قابلة للقراءة آليًا.

استخدمه عندما تريد أن تتصرف الذاكرة على نحو أقرب إلى طبقة معرفة مُدارة، وأقل
شبهًا بكومة من ملفات Markdown.

## ما الذي يضيفه

- مخزن ويكي مخصص مع تخطيط صفحات حتمي
- بيانات وصفية منظّمة للادعاءات والأدلة، وليس مجرد نص وصفي
- مصدرية على مستوى الصفحة، ودرجة ثقة، وتناقضات، وأسئلة مفتوحة
- ملخصات مُجمَّعة لمستهلكي الوكيل/وقت التشغيل
- أدوات أصلية للويكي للبحث/الجلب/التطبيق/الفحص
- وضع جسر اختياري يستورد العناصر العامة من Plugin الذاكرة النشطة
- وضع عرض اختياري متوافق مع Obsidian وتكامل مع CLI

## كيف ينسجم مع الذاكرة

فكر في التقسيم على هذا النحو:

| الطبقة                                                  | المسؤوليات                                                                                 |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Plugin الذاكرة النشطة (`memory-core` وQMD وHoncho وغيرها) | الاستدعاء، والبحث الدلالي، والترقية، وDreaming، ووقت تشغيل الذاكرة                         |
| `memory-wiki`                                           | صفحات ويكي مُجمَّعة، وملخصات غنية بالمصدرية، ولوحات معلومات، وبحث/جلب/تطبيق خاص بالويكي   |

إذا كان Plugin الذاكرة النشطة يوفّر عناصر استدعاء مشتركة، فيمكن لـ OpenClaw
البحث في كلتا الطبقتين في تمريرة واحدة باستخدام `memory_search corpus=all`.

وعندما تحتاج إلى ترتيب خاص بالويكي، أو مصدرية، أو وصول مباشر إلى الصفحة،
فاستخدم الأدوات الأصلية الخاصة بالويكي بدلًا من ذلك.

## النمط الهجين الموصى به

إعداد افتراضي قوي لبيئات local-first هو:

- QMD كواجهة خلفية للذاكرة النشطة للاستدعاء والبحث الدلالي الواسع
- `memory-wiki` في وضع `bridge` لصفحات المعرفة الدائمة المُجمَّعة

يعمل هذا التقسيم جيدًا لأن كل طبقة تبقى مركزة على مهمتها:

- يحتفظ QMD بإمكانية البحث في الملاحظات الخام، وعمليات تصدير الجلسات،
  والمجموعات الإضافية
- يجمع `memory-wiki` الكيانات المستقرة، والادعاءات، ولوحات المعلومات،
  وصفحات المصادر

قاعدة عملية:

- استخدم `memory_search` عندما تريد تمريرة استدعاء واسعة واحدة عبر الذاكرة
- استخدم `wiki_search` و`wiki_get` عندما تريد نتائج ويكي مدركة للمصدرية
- استخدم `memory_search corpus=all` عندما تريد أن يمتد البحث المشترك عبر كلتا الطبقتين

إذا أبلغ وضع الجسر عن صفر من العناصر المصدّرة، فهذا يعني أن Plugin الذاكرة
النشطة لا يعرّض حاليًا مدخلات الجسر العامة بعد. شغّل `openclaw wiki doctor`
أولًا، ثم تأكد من أن Plugin الذاكرة النشطة يدعم العناصر العامة.

## أوضاع المخزن

يدعم `memory-wiki` ثلاثة أوضاع للمخزن:

### `isolated`

مخزن مستقل، ومصادر مستقلة، ومن دون اعتماد على `memory-core`.

استخدم هذا عندما تريد أن يكون الويكي مخزن معرفة منسقًا قائمًا بذاته.

### `bridge`

يقرأ عناصر الذاكرة العامة وأحداث الذاكرة من Plugin الذاكرة النشطة
عبر نقاط Plugin SDK العامة.

استخدم هذا عندما تريد أن يقوم الويكي بتجميع وتنظيم العناصر المصدّرة من Plugin
الذاكرة من دون الوصول إلى الأجزاء الداخلية الخاصة غير العامة للـ Plugin.

يمكن لوضع الجسر فهرسة ما يلي:

- عناصر الذاكرة المصدّرة
- تقارير Dreaming
- الملاحظات اليومية
- ملفات جذر الذاكرة
- سجلات أحداث الذاكرة

### `unsafe-local`

منفذ هروب صريح على الجهاز نفسه للمسارات المحلية الخاصة.

هذا الوضع تجريبي عمدًا وغير قابل للنقل. استخدمه فقط عندما تفهم حدود الثقة
وتحتاج تحديدًا إلى وصول إلى نظام الملفات المحلي لا يستطيع وضع الجسر توفيره.

## تخطيط المخزن

يهيّئ Plugin مخزنًا على هذا النحو:

```text
<vault>/
  AGENTS.md
  WIKI.md
  index.md
  inbox.md
  entities/
  concepts/
  syntheses/
  sources/
  reports/
  _attachments/
  _views/
  .openclaw-wiki/
```

يبقى المحتوى المُدار داخل كتل مُولَّدة. وتُحفَظ كتل الملاحظات البشرية.

ومجموعات الصفحات الرئيسية هي:

- `sources/` للمواد الخام المستوردة والصفحات المدعومة بالجسر
- `entities/` للأشياء والأشخاص والأنظمة والمشاريع والكائنات الدائمة
- `concepts/` للأفكار والتجريدات والأنماط والسياسات
- `syntheses/` للملخصات المُجمَّعة والتجميعات المُدارة
- `reports/` للوحات المعلومات المُولَّدة

## الادعاءات والأدلة المنظَّمة

يمكن أن تحمل الصفحات `claims` في frontmatter بشكل منظّم، وليس مجرد نص حر.

يمكن أن يتضمن كل ادعاء:

- `id`
- `text`
- `status`
- `confidence`
- `evidence[]`
- `updatedAt`

ويمكن أن تتضمن إدخالات الأدلة ما يلي:

- `sourceId`
- `path`
- `lines`
- `weight`
- `note`
- `updatedAt`

وهذا ما يجعل الويكي يعمل أقرب إلى طبقة معتقدات بدلًا من مجرد تفريغ سلبي
للملاحظات. إذ يمكن تتبع الادعاءات وتقييمها والطعن فيها وربطها مجددًا بالمصادر.

## مسار التجميع

تقرأ خطوة التجميع صفحات الويكي، وتطبع الملخصات، وتنتج عناصر ثابتة موجّهة للآلة
ضمن:

- `.openclaw-wiki/cache/agent-digest.json`
- `.openclaw-wiki/cache/claims.jsonl`

توجد هذه الملخصات حتى لا تضطر الوكلاء وتعليمات وقت التشغيل إلى كشط صفحات
Markdown.

كما أن المخرجات المُجمَّعة تدعم أيضًا:

- الفهرسة الأولية للويكي لتدفقات البحث/الجلب
- إرجاع معرّفات الادعاءات إلى الصفحات المالكة لها
- مكمّلات مطالبات مدمجة
- توليد التقارير/لوحات المعلومات

## لوحات المعلومات وتقارير السلامة

عند تفعيل `render.createDashboards`، يحافظ التجميع على لوحات المعلومات ضمن
`reports/`.

وتشمل التقارير المضمّنة ما يلي:

- `reports/open-questions.md`
- `reports/contradictions.md`
- `reports/low-confidence.md`
- `reports/claim-health.md`
- `reports/stale-pages.md`

تتعقب هذه التقارير أمورًا مثل:

- مجموعات ملاحظات التناقض
- مجموعات الادعاءات المتنافسة
- الادعاءات التي تفتقد إلى أدلة منظّمة
- الصفحات والادعاءات منخفضة الثقة
- التقادم أو حداثة غير المعروفة
- الصفحات التي تحتوي على أسئلة غير محلولة

## البحث والاسترجاع

يدعم `memory-wiki` واجهتين خلفيتين للبحث:

- `shared`: استخدام تدفق بحث الذاكرة المشترك عندما يكون متاحًا
- `local`: البحث في الويكي محليًا

كما يدعم ثلاثة corpora:

- `wiki`
- `memory`
- `all`

سلوك مهم:

- يستخدم `wiki_search` و`wiki_get` الملخصات المُجمَّعة كتمرير أول عندما يكون ذلك ممكنًا
- يمكن لمعرّفات الادعاءات أن تُعاد إلى الصفحة المالكة لها
- تؤثر الادعاءات المتنازع عليها/القديمة/الحديثة في الترتيب
- يمكن أن تبقى تسميات المصدرية ضمن النتائج

قاعدة عملية:

- استخدم `memory_search corpus=all` للحصول على تمريرة استدعاء واسعة واحدة
- استخدم `wiki_search` + `wiki_get` عندما تهتم بالترتيب الخاص بالويكي،
  أو المصدرية، أو بنية المعتقدات على مستوى الصفحة

## أدوات الوكيل

يسجل Plugin هذه الأدوات:

- `wiki_status`
- `wiki_search`
- `wiki_get`
- `wiki_apply`
- `wiki_lint`

وظائفها:

- `wiki_status`: وضع المخزن الحالي، والسلامة، وتوفر Obsidian CLI
- `wiki_search`: البحث في صفحات الويكي، وعند التهيئة، في corpora الذاكرة المشتركة
- `wiki_get`: قراءة صفحة ويكي حسب المعرّف/المسار أو الرجوع إلى corpus الذاكرة المشترك
- `wiki_apply`: تعديلات ضيقة على الملخصات/البيانات الوصفية من دون جراحة حرة للصفحات
- `wiki_lint`: فحوصات بنيوية، وفجوات في المصدرية، وتناقضات، وأسئلة مفتوحة

كما يسجل Plugin مكمّل corpus ذاكرة غير حصري، بحيث يمكن لأداتي
`memory_search` و`memory_get` المشتركتين الوصول إلى الويكي عندما يدعم Plugin
الذاكرة النشطة اختيار corpus.

## سلوك المطالبات والسياق

عند تفعيل `context.includeCompiledDigestPrompt`، تقوم أقسام مطالبة الذاكرة
بإلحاق لقطة مُجمَّعة مدمجة من `agent-digest.json`.

وهذه اللقطة صغيرة عمدًا وعالية الإشارة:

- أهم الصفحات فقط
- أهم الادعاءات فقط
- عدد التناقضات
- عدد الأسئلة
- مؤهلات الثقة/الحداثة

وهذا اختياري لأنه يغيّر شكل المطالبة، وهو مفيد أساسًا لمحركات السياق أو
لتجميع المطالبات القديمة التي تستهلك مكمّلات الذاكرة صراحةً.

## الإعداد

ضع الإعداد تحت `plugins.entries.memory-wiki.config`:

```json5
{
  plugins: {
    entries: {
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "isolated",
          vault: {
            path: "~/.openclaw/wiki/main",
            renderMode: "obsidian",
          },
          obsidian: {
            enabled: true,
            useOfficialCli: true,
            vaultName: "OpenClaw Wiki",
            openAfterWrites: false,
          },
          bridge: {
            enabled: false,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          ingest: {
            autoCompile: true,
            maxConcurrentJobs: 1,
            allowUrlIngest: true,
          },
          search: {
            backend: "shared",
            corpus: "wiki",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
          render: {
            preserveHumanBlocks: true,
            createBacklinks: true,
            createDashboards: true,
          },
        },
      },
    },
  },
}
```

أهم خيارات التبديل:

- `vaultMode`: ‏`isolated` أو `bridge` أو `unsafe-local`
- `vault.renderMode`: ‏`native` أو `obsidian`
- `bridge.readMemoryArtifacts`: استيراد العناصر العامة من Plugin الذاكرة النشطة
- `bridge.followMemoryEvents`: تضمين سجلات الأحداث في وضع الجسر
- `search.backend`: ‏`shared` أو `local`
- `search.corpus`: ‏`wiki` أو `memory` أو `all`
- `context.includeCompiledDigestPrompt`: إلحاق لقطة ملخص مدمجة إلى أقسام مطالبة الذاكرة
- `render.createBacklinks`: توليد كتل مرتبطة ذات صلة بشكل حتمي
- `render.createDashboards`: توليد صفحات لوحات معلومات

### مثال: QMD + وضع الجسر

استخدم هذا عندما تريد QMD للاستدعاء و`memory-wiki` لطبقة معرفة مُدارة:

```json5
{
  memory: {
    backend: "qmd",
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "bridge",
          bridge: {
            enabled: true,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          search: {
            backend: "shared",
            corpus: "all",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
        },
      },
    },
  },
}
```

وهذا يبقي:

- QMD مسؤولًا عن استدعاء الذاكرة النشطة
- `memory-wiki` مركزًا على الصفحات المُجمَّعة ولوحات المعلومات
- شكل المطالبة دون تغيير حتى تقوم عمدًا بتفعيل مطالبات الملخص المُجمَّع

## CLI

يعرّض `memory-wiki` أيضًا واجهة CLI عليا:

```bash
openclaw wiki status
openclaw wiki doctor
openclaw wiki init
openclaw wiki ingest ./notes/alpha.md
openclaw wiki compile
openclaw wiki lint
openclaw wiki search "alpha"
openclaw wiki get entity.alpha
openclaw wiki apply synthesis "Alpha Summary" --body "..." --source-id source.alpha
openclaw wiki bridge import
openclaw wiki obsidian status
```

راجع [CLI: wiki](/cli/wiki) للاطلاع على مرجع الأوامر الكامل.

## دعم Obsidian

عندما تكون `vault.renderMode` مساوية لـ `obsidian`، يكتب Plugin ملفات
Markdown متوافقة مع Obsidian ويمكنه اختياريًا استخدام CLI الرسمي لـ `obsidian`.

وتشمل تدفقات العمل المدعومة ما يلي:

- فحص الحالة
- البحث في المخزن
- فتح صفحة
- استدعاء أمر Obsidian
- الانتقال إلى الملاحظة اليومية

وهذا اختياري. فما يزال الويكي يعمل في الوضع الأصلي من دون Obsidian.

## سير العمل الموصى به

1. احتفظ بـ Plugin الذاكرة النشطة لديك للاستدعاء/الترقية/Dreaming.
2. فعّل `memory-wiki`.
3. ابدأ بوضع `isolated` ما لم تكن تريد وضع الجسر صراحةً.
4. استخدم `wiki_search` / `wiki_get` عندما تكون المصدرية مهمة.
5. استخدم `wiki_apply` للتلخيصات الضيقة أو تحديثات البيانات الوصفية.
6. شغّل `wiki_lint` بعد التغييرات المهمة.
7. فعّل لوحات المعلومات إذا كنت تريد رؤية التقادم/التناقضات.

## مستندات ذات صلة

- [نظرة عامة على الذاكرة](/ar/concepts/memory)
- [CLI: memory](/cli/memory)
- [CLI: wiki](/cli/wiki)
- [نظرة عامة على Plugin SDK](/ar/plugins/sdk-overview)
