---
read_when:
    - تريد إعداد موفّري بحث الذاكرة أو نماذج التضمين
    - تريد إعداد الواجهة الخلفية لـ QMD
    - تريد ضبط البحث الهجين، أو MMR، أو التلاشي الزمني
    - تريد تفعيل فهرسة الذاكرة متعددة الوسائط
summary: جميع خيارات الإعداد الخاصة ببحث الذاكرة، وموفّري التضمين، وQMD، والبحث الهجين، والفهرسة متعددة الوسائط
title: مرجع إعداد الذاكرة
x-i18n:
    generated_at: "2026-04-12T23:33:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 299ca9b69eea292ea557a2841232c637f5c1daf2bc0f73c0a42f7c0d8d566ce2
    source_path: reference/memory-config.md
    workflow: 15
---

# مرجع إعداد الذاكرة

تسرد هذه الصفحة جميع خيارات الإعداد الخاصة ببحث الذاكرة في OpenClaw. وللاطلاع على
النظرات العامة المفاهيمية، راجع:

- [نظرة عامة على الذاكرة](/ar/concepts/memory) -- كيف تعمل الذاكرة
- [المحرّك المدمج](/ar/concepts/memory-builtin) -- الواجهة الخلفية الافتراضية SQLite
- [محرّك QMD](/ar/concepts/memory-qmd) -- sidecar محلي أولًا
- [بحث الذاكرة](/ar/concepts/memory-search) -- مسار البحث والضبط
- [Active Memory](/ar/concepts/active-memory) -- تفعيل الوكيل الفرعي للذاكرة للجلسات التفاعلية

توجد جميع إعدادات بحث الذاكرة تحت `agents.defaults.memorySearch` في
`openclaw.json` ما لم يُذكر خلاف ذلك.

إذا كنت تبحث عن مفتاح تفعيل ميزة **Active Memory** وإعداد الوكيل الفرعي،
فهذا يوجد تحت `plugins.entries.active-memory` بدلًا من `memorySearch`.

تستخدم Active Memory نموذجًا ذا بوابتين:

1. يجب أن تكون Plugin ممكّنة وأن تستهدف معرف الوكيل الحالي
2. يجب أن يكون الطلب جلسة دردشة تفاعلية دائمة مؤهلة

راجع [Active Memory](/ar/concepts/active-memory) للاطلاع على نموذج التفعيل،
والإعداد المملوك لـ Plugin، واستمرارية التفريغ، ونمط الطرح الآمن.

---

## اختيار الموفّر

| المفتاح   | النوع      | الافتراضي      | الوصف                                                                                      |
| --------- | ---------- | -------------- | ------------------------------------------------------------------------------------------- |
| `provider` | `string`  | يُكتشف تلقائيًا | معرف مهايئ التضمين: `openai`، `gemini`، `voyage`، `mistral`، `bedrock`، `ollama`، `local` |
| `model`    | `string`  | افتراضي الموفّر | اسم نموذج التضمين                                                                           |
| `fallback` | `string`  | `"none"`       | معرف المهايئ الاحتياطي عند فشل الأساسي                                                       |
| `enabled`  | `boolean` | `true`         | تفعيل أو تعطيل بحث الذاكرة                                                                   |

### ترتيب الاكتشاف التلقائي

عندما لا يتم ضبط `provider`، يختار OpenClaw أول موفّر متاح:

1. `local` -- إذا كان `memorySearch.local.modelPath` مضبوطًا والملف موجودًا.
2. `openai` -- إذا أمكن حل مفتاح OpenAI.
3. `gemini` -- إذا أمكن حل مفتاح Gemini.
4. `voyage` -- إذا أمكن حل مفتاح Voyage.
5. `mistral` -- إذا أمكن حل مفتاح Mistral.
6. `bedrock` -- إذا تم حل سلسلة بيانات اعتماد AWS SDK (دور المثيل، أو مفاتيح الوصول، أو الملف الشخصي، أو SSO، أو هوية الويب، أو الإعداد المشترك).

`ollama` مدعوم لكنه لا يُكتشف تلقائيًا (اضبطه صراحةً).

### حل مفتاح API

تتطلب التضمينات البعيدة مفتاح API. أما Bedrock فيستخدم سلسلة
بيانات الاعتماد الافتراضية الخاصة بـ AWS SDK بدلًا من ذلك (أدوار المثيل، وSSO، ومفاتيح الوصول).

| الموفّر | متغير البيئة                   | مفتاح الإعداد                      |
| ------- | ------------------------------ | ---------------------------------- |
| OpenAI  | `OPENAI_API_KEY`              | `models.providers.openai.apiKey`   |
| Gemini  | `GEMINI_API_KEY`              | `models.providers.google.apiKey`   |
| Voyage  | `VOYAGE_API_KEY`              | `models.providers.voyage.apiKey`   |
| Mistral | `MISTRAL_API_KEY`             | `models.providers.mistral.apiKey`  |
| Bedrock | سلسلة بيانات اعتماد AWS       | لا حاجة إلى مفتاح API              |
| Ollama  | `OLLAMA_API_KEY` (عنصر نائب) | --                                 |

يغطي Codex OAuth الدردشة/الإكمالات فقط ولا يلبّي طلبات التضمين.

---

## إعداد نقطة النهاية البعيدة

لنقاط النهاية المخصصة المتوافقة مع OpenAI أو لتجاوز الإعدادات الافتراضية للموفّر:

| المفتاح           | النوع    | الوصف                                        |
| ----------------- | -------- | -------------------------------------------- |
| `remote.baseUrl`  | `string` | Base URL مخصص لـ API                         |
| `remote.apiKey`   | `string` | تجاوز مفتاح API                              |
| `remote.headers`  | `object` | رؤوس HTTP إضافية (تُدمج مع افتراضيات الموفّر) |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        remote: {
          baseUrl: "https://api.example.com/v1/",
          apiKey: "YOUR_KEY",
        },
      },
    },
  },
}
```

---

## إعداد خاص بـ Gemini

| المفتاح               | النوع    | الافتراضي             | الوصف                                    |
| --------------------- | -------- | --------------------- | ---------------------------------------- |
| `model`               | `string` | `gemini-embedding-001` | يدعم أيضًا `gemini-embedding-2-preview` |
| `outputDimensionality` | `number` | `3072`               | بالنسبة إلى Embedding 2: ‏768 أو 1536 أو 3072 |

<Warning>
يؤدي تغيير النموذج أو `outputDimensionality` إلى إعادة فهرسة كاملة تلقائية.
</Warning>

---

## إعداد تضمين Bedrock

يستخدم Bedrock سلسلة بيانات الاعتماد الافتراضية الخاصة بـ AWS SDK -- ولا يحتاج إلى مفاتيح API.
إذا كان OpenClaw يعمل على EC2 مع دور مثيل مفعّل لـ Bedrock، فما عليك سوى ضبط
الموفّر والنموذج:

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "bedrock",
        model: "amazon.titan-embed-text-v2:0",
      },
    },
  },
}
```

| المفتاح               | النوع    | الافتراضي                     | الوصف                              |
| --------------------- | -------- | ----------------------------- | ---------------------------------- |
| `model`               | `string` | `amazon.titan-embed-text-v2:0` | أي معرف نموذج تضمين في Bedrock    |
| `outputDimensionality` | `number` | الافتراضي الخاص بالنموذج      | بالنسبة إلى Titan V2: ‏256 أو 512 أو 1024 |

### النماذج المدعومة

النماذج التالية مدعومة (مع اكتشاف العائلة والإعدادات الافتراضية للأبعاد):

| معرف النموذج                               | الموفّر     | الأبعاد الافتراضية | الأبعاد القابلة للإعداد |
| ------------------------------------------ | ----------- | ------------------ | ----------------------- |
| `amazon.titan-embed-text-v2:0`             | Amazon      | 1024               | 256، 512، 1024          |
| `amazon.titan-embed-text-v1`               | Amazon      | 1536               | --                      |
| `amazon.titan-embed-g1-text-02`            | Amazon      | 1536               | --                      |
| `amazon.titan-embed-image-v1`              | Amazon      | 1024               | --                      |
| `amazon.nova-2-multimodal-embeddings-v1:0` | Amazon      | 1024               | 256، 384، 1024، 3072    |
| `cohere.embed-english-v3`                  | Cohere      | 1024               | --                      |
| `cohere.embed-multilingual-v3`             | Cohere      | 1024               | --                      |
| `cohere.embed-v4:0`                        | Cohere      | 1536               | 256-1536                |
| `twelvelabs.marengo-embed-3-0-v1:0`        | TwelveLabs  | 512                | --                      |
| `twelvelabs.marengo-embed-2-7-v1:0`        | TwelveLabs  | 1024               | --                      |

ترث المتغيرات ذات لاحقة معدل النقل (مثل `amazon.titan-embed-text-v1:2:8k`)
إعداد النموذج الأساسي.

### المصادقة

تستخدم مصادقة Bedrock ترتيب حل بيانات الاعتماد القياسي في AWS SDK:

1. متغيرات البيئة (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`)
2. ذاكرة التخزين المؤقت لرمز SSO
3. بيانات اعتماد رمز هوية الويب
4. ملفات بيانات الاعتماد والإعدادات المشتركة
5. بيانات اعتماد بيانات تعريف ECS أو EC2

يُحل الإقليم من `AWS_REGION` أو `AWS_DEFAULT_REGION` أو
`baseUrl` الخاص بموفّر `amazon-bedrock`، أو تكون القيمة الافتراضية `us-east-1`.

### أذونات IAM

يحتاج دور IAM أو المستخدم إلى:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

ولتطبيق أقل قدر من الامتيازات، حدّد نطاق `InvokeModel` إلى النموذج المحدد:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## إعداد التضمين المحلي

| المفتاح               | النوع    | الافتراضي               | الوصف                          |
| --------------------- | -------- | ----------------------- | ------------------------------ |
| `local.modelPath`     | `string` | يُنزّل تلقائيًا         | مسار ملف نموذج GGUF           |
| `local.modelCacheDir` | `string` | افتراضي node-llama-cpp | دليل التخزين المؤقت للنماذج المنزّلة |

النموذج الافتراضي: `embeddinggemma-300m-qat-Q8_0.gguf` ‏(~0.6 GB، يُنزّل تلقائيًا).
يتطلب بناءً أصليًا: `pnpm approve-builds` ثم `pnpm rebuild node-llama-cpp`.

---

## إعداد البحث الهجين

كل شيء تحت `memorySearch.query.hybrid`:

| المفتاح               | النوع      | الافتراضي | الوصف                               |
| --------------------- | ---------- | --------- | ----------------------------------- |
| `enabled`             | `boolean`  | `true`    | تفعيل البحث الهجين BM25 + vector    |
| `vectorWeight`        | `number`   | `0.7`     | الوزن لدرجات vector ‏(0-1)          |
| `textWeight`          | `number`   | `0.3`     | الوزن لدرجات BM25 ‏(0-1)            |
| `candidateMultiplier` | `number`   | `4`       | مضاعف حجم مجموعة المرشحين           |

### MMR (التنوع)

| المفتاح        | النوع      | الافتراضي | الوصف                                 |
| -------------- | ---------- | --------- | ------------------------------------- |
| `mmr.enabled`  | `boolean`  | `false`   | تفعيل إعادة الترتيب باستخدام MMR      |
| `mmr.lambda`   | `number`   | `0.7`     | 0 = أقصى تنوع، 1 = أقصى صلة           |

### التلاشي الزمني (الحداثة)

| المفتاح                     | النوع      | الافتراضي | الوصف                         |
| --------------------------- | ---------- | --------- | ----------------------------- |
| `temporalDecay.enabled`     | `boolean`  | `false`   | تفعيل تعزيز الحداثة           |
| `temporalDecay.halfLifeDays` | `number`  | `30`      | تنخفض الدرجة إلى النصف كل N يومًا |

لا يطبق التلاشي أبدًا على الملفات الدائمة (`MEMORY.md`، والملفات غير المؤرخة في `memory/`).

### مثال كامل

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        query: {
          hybrid: {
            vectorWeight: 0.7,
            textWeight: 0.3,
            mmr: { enabled: true, lambda: 0.7 },
            temporalDecay: { enabled: true, halfLifeDays: 30 },
          },
        },
      },
    },
  },
}
```

---

## مسارات ذاكرة إضافية

| المفتاح     | النوع       | الوصف                                 |
| ----------- | ----------- | ------------------------------------- |
| `extraPaths` | `string[]` | أدلة أو ملفات إضافية لفهرستها         |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        extraPaths: ["../team-docs", "/srv/shared-notes"],
      },
    },
  },
}
```

يمكن أن تكون المسارات مطلقة أو نسبية إلى مساحة العمل. وتُفحص الأدلة
تكراريًا بحثًا عن ملفات `.md`. ويعتمد التعامل مع الروابط الرمزية على
الواجهة الخلفية النشطة: إذ يتجاهل المحرّك المدمج الروابط الرمزية، بينما يتبع QMD
سلوك ماسح QMD الأساسي.

وبالنسبة إلى بحث التفريغ بين الوكلاء على نطاق الوكيل، استخدم
`agents.list[].memorySearch.qmd.extraCollections` بدلًا من `memory.qmd.paths`.
تتبع هذه المجموعات الإضافية البنية نفسها `{ path, name, pattern? }`، لكنها
تُدمج لكل وكيل ويمكنها الحفاظ على أسماء مشتركة صريحة عندما يشير المسار
إلى خارج مساحة العمل الحالية.
إذا ظهر المسار المحلول نفسه في كل من `memory.qmd.paths` و
`memorySearch.qmd.extraCollections`، فسيحتفظ QMD بالإدخال الأول ويتخطى
الإدخال المكرر.

---

## الذاكرة متعددة الوسائط (Gemini)

افهرس الصور والصوت إلى جانب Markdown باستخدام Gemini Embedding 2:

| المفتاح                    | النوع       | الافتراضي  | الوصف                                  |
| -------------------------- | ----------- | ---------- | -------------------------------------- |
| `multimodal.enabled`       | `boolean`   | `false`    | تفعيل الفهرسة متعددة الوسائط           |
| `multimodal.modalities`    | `string[]`  | --         | `["image"]` أو `["audio"]` أو `["all"]` |
| `multimodal.maxFileBytes`  | `number`    | `10000000` | الحد الأقصى لحجم الملف لأجل الفهرسة    |

ينطبق هذا فقط على الملفات الموجودة في `extraPaths`. وتبقى جذور الذاكرة الافتراضية خاصة بـ Markdown فقط.
ويتطلب `gemini-embedding-2-preview`. ويجب أن تكون قيمة `fallback` هي `"none"`.

التنسيقات المدعومة: `.jpg` و`.jpeg` و`.png` و`.webp` و`.gif` و`.heic` و`.heif`
(صور)؛ و`.mp3` و`.wav` و`.ogg` و`.opus` و`.m4a` و`.aac` و`.flac` (صوت).

---

## ذاكرة التخزين المؤقت للتضمين

| المفتاح            | النوع      | الافتراضي | الوصف                               |
| ------------------ | ---------- | --------- | ----------------------------------- |
| `cache.enabled`    | `boolean`  | `false`   | تخزين تضمينات المقاطع في SQLite     |
| `cache.maxEntries` | `number`   | `50000`   | الحد الأقصى لعدد التضمينات المخزنة  |

يمنع إعادة تضمين النص غير المتغير أثناء إعادة الفهرسة أو تحديثات التفريغ.

---

## الفهرسة على دفعات

| المفتاح                      | النوع      | الافتراضي | الوصف                    |
| ---------------------------- | ---------- | --------- | ------------------------ |
| `remote.batch.enabled`       | `boolean`  | `false`   | تفعيل API للتضمين الدفعي |
| `remote.batch.concurrency`   | `number`   | `2`       | وظائف الدفعات المتوازية  |
| `remote.batch.wait`          | `boolean`  | `true`    | انتظار اكتمال الدفعة     |
| `remote.batch.pollIntervalMs` | `number`  | --        | الفاصل الزمني للاستطلاع  |
| `remote.batch.timeoutMinutes` | `number`  | --        | مهلة الدفعة              |

متاح لـ `openai` و`gemini` و`voyage`. وعادةً ما تكون دفعات OpenAI
الأسرع والأرخص لعمليات الملء الخلفي الكبيرة.

---

## بحث ذاكرة الجلسة (تجريبي)

افهرس تفريغات الجلسات وأظهرها عبر `memory_search`:

| المفتاح                      | النوع       | الافتراضي     | الوصف                                  |
| ---------------------------- | ----------- | ------------- | -------------------------------------- |
| `experimental.sessionMemory` | `boolean`   | `false`       | تفعيل فهرسة الجلسة                     |
| `sources`                    | `string[]`  | `["memory"]`  | أضف `"sessions"` لتضمين التفريغات      |
| `sync.sessions.deltaBytes`   | `number`    | `100000`      | حد البايت لإعادة الفهرسة               |
| `sync.sessions.deltaMessages` | `number`   | `50`          | حد الرسائل لإعادة الفهرسة              |

تُفعّل فهرسة الجلسة بشكل اختياري وتعمل بشكل غير متزامن. وقد تكون النتائج
قديمة قليلًا. وتوجد سجلات الجلسات على القرص، لذا تعامل مع الوصول إلى نظام الملفات على أنه حد الثقة.

---

## تسريع SQLite المتجهي (sqlite-vec)

| المفتاح                     | النوع      | الافتراضي | الوصف                              |
| --------------------------- | ---------- | --------- | ---------------------------------- |
| `store.vector.enabled`      | `boolean`  | `true`    | استخدام sqlite-vec للاستعلامات المتجهية |
| `store.vector.extensionPath` | `string`  | مضمّن     | تجاوز مسار sqlite-vec              |

عندما لا يكون sqlite-vec متاحًا، يعود OpenClaw تلقائيًا إلى
تشابه جيب التمام داخل العملية.

---

## تخزين الفهرس

| المفتاح              | النوع     | الافتراضي                               | الوصف                                      |
| -------------------- | -------- | --------------------------------------- | ------------------------------------------ |
| `store.path`         | `string` | `~/.openclaw/memory/{agentId}.sqlite`   | موقع الفهرس (يدعم الرمز `{agentId}`)       |
| `store.fts.tokenizer` | `string` | `unicode61`                            | محلل FTS5 (`unicode61` أو `trigram`)       |

---

## إعداد الواجهة الخلفية لـ QMD

اضبط `memory.backend = "qmd"` للتفعيل. وتوجد جميع إعدادات QMD تحت
`memory.qmd`:

| المفتاح                 | النوع      | الافتراضي | الوصف                                      |
| ----------------------- | ---------- | --------- | ------------------------------------------ |
| `command`               | `string`   | `qmd`     | مسار الملف التنفيذي لـ QMD                 |
| `searchMode`            | `string`   | `search`  | أمر البحث: `search` أو `vsearch` أو `query` |
| `includeDefaultMemory`  | `boolean`  | `true`    | فهرسة `MEMORY.md` + `memory/**/*.md` تلقائيًا |
| `paths[]`               | `array`    | --        | مسارات إضافية: `{ name, path, pattern? }`  |
| `sessions.enabled`      | `boolean`  | `false`   | فهرسة تفريغات الجلسات                      |
| `sessions.retentionDays` | `number`  | --        | مدة الاحتفاظ بالتفريغ                      |
| `sessions.exportDir`    | `string`   | --        | دليل التصدير                               |

يفضّل OpenClaw الأشكال الحالية للمجموعات واستعلامات MCP في QMD، لكنه
يبقي الإصدارات الأقدم من QMD عاملة عبر الرجوع إلى أعلام المجموعات القديمة
`--mask` وأسماء أدوات MCP الأقدم عند الحاجة.

تبقى تجاوزات نماذج QMD على جانب QMD، لا في إعداد OpenClaw. إذا احتجت إلى
تجاوز نماذج QMD عالميًا، فاضبط متغيرات البيئة مثل
`QMD_EMBED_MODEL` و`QMD_RERANK_MODEL` و`QMD_GENERATE_MODEL` في
بيئة وقت تشغيل gateway.

### جدول التحديث

| المفتاح                    | النوع      | الافتراضي | الوصف                                  |
| -------------------------- | ---------- | --------- | -------------------------------------- |
| `update.interval`          | `string`   | `5m`      | فاصل التحديث                           |
| `update.debounceMs`        | `number`   | `15000`   | إزالة ارتداد تغييرات الملفات           |
| `update.onBoot`            | `boolean`  | `true`    | التحديث عند بدء التشغيل                 |
| `update.waitForBootSync`   | `boolean`  | `false`   | حظر بدء التشغيل حتى اكتمال التحديث      |
| `update.embedInterval`     | `string`   | --        | وتيرة تضمين منفصلة                      |
| `update.commandTimeoutMs`  | `number`   | --        | المهلة الزمنية لأوامر QMD              |
| `update.updateTimeoutMs`   | `number`   | --        | المهلة الزمنية لعمليات تحديث QMD       |
| `update.embedTimeoutMs`    | `number`   | --        | المهلة الزمنية لعمليات تضمين QMD       |

### الحدود

| المفتاح                  | النوع     | الافتراضي | الوصف                        |
| ------------------------ | -------- | --------- | ---------------------------- |
| `limits.maxResults`      | `number` | `6`       | الحد الأقصى لنتائج البحث     |
| `limits.maxSnippetChars` | `number` | --        | تقييد طول المقتطف            |
| `limits.maxInjectedChars` | `number` | --       | تقييد إجمالي الأحرف المحقونة |
| `limits.timeoutMs`       | `number` | `4000`    | مهلة البحث                   |

### النطاق

يتحكم في الجلسات التي يمكنها تلقي نتائج بحث QMD. وهو بنفس مخطط
[`session.sendPolicy`](/ar/gateway/configuration-reference#session):

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

يسمح الإعداد الافتراضي المرفق بجلسات direct وchannel، مع الاستمرار في
رفض المجموعات.

القيمة الافتراضية هي DM فقط. يطابق `match.keyPrefix` مفتاح الجلسة بعد التطبيع؛
ويطابق `match.rawKeyPrefix` المفتاح الخام بما في ذلك `agent:<id>:`.

### الاستشهادات

ينطبق `memory.citations` على جميع الواجهات الخلفية:

| القيمة            | السلوك                                              |
| ----------------- | --------------------------------------------------- |
| `auto` (الافتراضي) | تضمين تذييل `Source: <path#line>` في المقتطفات     |
| `on`              | تضمين التذييل دائمًا                                |
| `off`             | حذف التذييل (يبقى المسار مُمررًا إلى الوكيل داخليًا) |

### مثال كامل على QMD

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",
    qmd: {
      includeDefaultMemory: true,
      update: { interval: "5m", debounceMs: 15000 },
      limits: { maxResults: 6, timeoutMs: 4000 },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

---

## Dreaming (تجريبي)

يُضبط Dreaming تحت `plugins.entries.memory-core.config.dreaming`،
وليس تحت `agents.defaults.memorySearch`.

يعمل Dreaming كعملية مسح مجدولة واحدة ويستخدم داخليًا مراحل light/deep/REM
كتفصيل تنفيذي.

للاطلاع على السلوك المفاهيمي وأوامر الشرطة المائلة، راجع [Dreaming](/ar/concepts/dreaming).

### إعدادات المستخدم

| المفتاح    | النوع      | الافتراضي    | الوصف                                         |
| ---------- | ---------- | ------------ | --------------------------------------------- |
| `enabled`  | `boolean`  | `false`      | تفعيل أو تعطيل Dreaming بالكامل               |
| `frequency` | `string`  | `0 3 * * *`  | وتيرة Cron اختيارية لعملية المسح الكاملة لـ Dreaming |

### مثال

```json5
{
  plugins: {
    entries: {
      "memory-core": {
        config: {
          dreaming: {
            enabled: true,
            frequency: "0 3 * * *",
          },
        },
      },
    },
  },
}
```

ملاحظات:

- يكتب Dreaming حالة الآلة إلى `memory/.dreams/`.
- يكتب Dreaming مخرجات سردية مقروءة للبشر إلى `DREAMS.md` (أو `dreams.md` الموجودة).
- تمثل سياسة المراحل light/deep/REM والحدود السلوكية سلوكًا داخليًا، لا إعدادًا موجّهًا للمستخدم.
