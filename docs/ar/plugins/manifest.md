---
read_when:
    - أنت تبني إضافة لـ OpenClaw
    - تحتاج إلى شحن مخطط إعدادات إضافة أو تصحيح أخطاء التحقق من صحة الإضافات
summary: بيان الإضافة + متطلبات JSON Schema (تحقق صارم من صحة الإعدادات)
title: بيان الإضافة
x-i18n:
    generated_at: "2026-04-09T01:29:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9a7ee4b621a801d2a8f32f8976b0e1d9433c7810eb360aca466031fc0ffb286a
    source_path: plugins/manifest.md
    workflow: 15
---

# بيان الإضافة (openclaw.plugin.json)

هذه الصفحة مخصصة **لبيان الإضافة الأصلي في OpenClaw** فقط.

للتخطيطات المتوافقة مع الحِزم، راجع [حِزم الإضافات](/ar/plugins/bundles).

تستخدم تنسيقات الحِزم المتوافقة ملفات بيان مختلفة:

- حزمة Codex: ‏`.codex-plugin/plugin.json`
- حزمة Claude: ‏`.claude-plugin/plugin.json` أو تخطيط مكونات Claude
  الافتراضي من دون بيان
- حزمة Cursor: ‏`.cursor-plugin/plugin.json`

يكتشف OpenClaw أيضًا تخطيطات الحِزم هذه تلقائيًا، ولكن لا يتم التحقق من صحتها
مقابل مخطط `openclaw.plugin.json` الموضح هنا.

بالنسبة إلى الحِزم المتوافقة، يقرأ OpenClaw حاليًا بيانات الحزمة الوصفية بالإضافة إلى
جذور Skills المعلنة، وجذور أوامر Claude، والقيم الافتراضية في `settings.json` لحزمة Claude،
وقيم Claude LSP الافتراضية، وحِزم الخطافات المدعومة عندما يتطابق التخطيط مع
توقعات وقت تشغيل OpenClaw.

**يجب** أن تشحن كل إضافة أصلية في OpenClaw ملف `openclaw.plugin.json` في
**جذر الإضافة**. يستخدم OpenClaw هذا البيان للتحقق من صحة الإعدادات
**من دون تنفيذ كود الإضافة**. وتُعامل البيانات المفقودة أو غير الصالحة
على أنها أخطاء في الإضافة وتمنع التحقق من صحة الإعدادات.

راجع دليل نظام الإضافات الكامل: [الإضافات](/ar/tools/plugin).
وبالنسبة إلى نموذج الإمكانات الأصلي وإرشادات التوافق الخارجي الحالية:
[نموذج الإمكانات](/ar/plugins/architecture#public-capability-model).

## ما الذي يفعله هذا الملف

`openclaw.plugin.json` هو البيانات الوصفية التي يقرأها OpenClaw قبل أن يحمّل
كود الإضافة.

استخدمه من أجل:

- هوية الإضافة
- التحقق من صحة الإعدادات
- بيانات المصادقة والإعداد الأولي التي يجب أن تكون متاحة من دون تشغيل
  وقت تشغيل الإضافة
- بيانات الأسماء المستعارة والتمكين التلقائي التي يجب حلها قبل تحميل وقت تشغيل الإضافة
- بيانات ملكية عائلات النماذج المختصرة التي يجب أن تفعّل
  الإضافة تلقائيًا قبل تحميل وقت التشغيل
- لقطات ملكية الإمكانات الثابتة المستخدمة في توصيلات التوافق المضمّنة
  وتغطية العقود
- بيانات إعدادات خاصة بالقنوات يجب دمجها في أسطح الفهرسة والتحقق
  من دون تحميل وقت التشغيل
- تلميحات واجهة المستخدم للإعدادات

لا تستخدمه من أجل:

- تسجيل سلوك وقت التشغيل
- تعريف نقاط دخول الكود
- بيانات تثبيت npm الوصفية

فهذه تنتمي إلى كود الإضافة و`package.json`.

## مثال أدنى

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## مثال غني

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "OpenRouter provider plugin",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "OpenRouter API key",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter API key",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## مرجع الحقول ذات المستوى الأعلى

| الحقل                               | مطلوب | النوع                            | معناه                                                                                                                                                                                                    |
| ----------------------------------- | ------ | -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                | نعم    | `string`                         | معرّف الإضافة الأساسي. هذا هو المعرّف المستخدم في `plugins.entries.<id>`.                                                                                                                               |
| `configSchema`                      | نعم    | `object`                         | JSON Schema مضمن لإعدادات هذه الإضافة.                                                                                                                                                                   |
| `enabledByDefault`                  | لا     | `true`                           | يحدد أن الإضافة المضمّنة مفعّلة افتراضيًا. احذفه أو اضبط أي قيمة لا تساوي `true` لترك الإضافة معطلة افتراضيًا.                                                                                         |
| `legacyPluginIds`                   | لا     | `string[]`                       | معرّفات قديمة تُطبّع إلى معرّف الإضافة الأساسي هذا.                                                                                                                                                      |
| `autoEnableWhenConfiguredProviders` | لا     | `string[]`                       | معرّفات المزوّدين التي يجب أن تفعّل هذه الإضافة تلقائيًا عندما تشير إليها المصادقة أو الإعدادات أو مراجع النماذج.                                                                                       |
| `kind`                              | لا     | `"memory"` \| `"context-engine"` | يعلن نوع إضافة حصريًا يُستخدم بواسطة `plugins.slots.*`.                                                                                                                                                 |
| `channels`                          | لا     | `string[]`                       | معرّفات القنوات المملوكة لهذه الإضافة. تُستخدم للاكتشاف والتحقق من صحة الإعدادات.                                                                                                                       |
| `providers`                         | لا     | `string[]`                       | معرّفات المزوّدين المملوكة لهذه الإضافة.                                                                                                                                                                 |
| `modelSupport`                      | لا     | `object`                         | بيانات وصفية مختصرة لعائلات النماذج يملكها البيان وتُستخدم لتحميل الإضافة تلقائيًا قبل وقت التشغيل.                                                                                                    |
| `cliBackends`                       | لا     | `string[]`                       | معرّفات واجهات CLI الخلفية للاستدلال المملوكة لهذه الإضافة. تُستخدم للتفعيل التلقائي عند بدء التشغيل من مراجع إعدادات صريحة.                                                                            |
| `providerAuthEnvVars`               | لا     | `Record<string, string[]>`       | بيانات وصفية خفيفة لبيئة مصادقة المزوّد يمكن لـ OpenClaw فحصها من دون تحميل كود الإضافة.                                                                                                               |
| `providerAuthAliases`               | لا     | `Record<string, string>`         | معرّفات المزوّدين التي يجب أن تعيد استخدام معرّف مزوّد آخر للبحث عن المصادقة، مثل مزوّد برمجي يشارك مفتاح API الأساسي وملفات المصادقة الشخصية مع المزوّد الأساسي.                                      |
| `channelEnvVars`                    | لا     | `Record<string, string[]>`       | بيانات وصفية خفيفة لبيئة القناة يمكن لـ OpenClaw فحصها من دون تحميل كود الإضافة. استخدم هذا لإعداد القنوات المعتمد على البيئة أو أسطح المصادقة التي يجب أن تراها أدوات البدء/الإعداد العامة.             |
| `providerAuthChoices`               | لا     | `object[]`                       | بيانات وصفية خفيفة لخيارات المصادقة لمحددات الإعداد الأولي، وحل المزوّد المفضّل، وتوصيل أعلام CLI البسيطة.                                                                                             |
| `contracts`                         | لا     | `object`                         | لقطة ثابتة مضمّنة للإمكانات لميزات speech، وrealtime transcription، وrealtime voice، وmedia-understanding، وimage-generation، وmusic-generation، وvideo-generation، وweb-fetch، وweb search، وملكية الأدوات. |
| `channelConfigs`                    | لا     | `Record<string, object>`         | بيانات إعدادات القناة يملكها البيان وتُدمج في أسطح الاكتشاف والتحقق قبل تحميل وقت التشغيل.                                                                                                              |
| `skills`                            | لا     | `string[]`                       | أدلة Skills المطلوب تحميلها، نسبةً إلى جذر الإضافة.                                                                                                                                                      |
| `name`                              | لا     | `string`                         | اسم إضافة مقروء للبشر.                                                                                                                                                                                   |
| `description`                       | لا     | `string`                         | ملخص قصير يُعرض في أسطح الإضافة.                                                                                                                                                                         |
| `version`                           | لا     | `string`                         | إصدار معلوماتي للإضافة.                                                                                                                                                                                  |
| `uiHints`                           | لا     | `Record<string, object>`         | تسميات واجهة المستخدم، والعناصر النائبة، وتلميحات الحساسية لحقول الإعدادات.                                                                                                                              |

## مرجع providerAuthChoices

يصف كل إدخال في `providerAuthChoices` خيار إعداد أولي أو مصادقة واحدًا.
يقرأ OpenClaw هذا قبل تحميل وقت تشغيل المزوّد.

| الحقل                 | مطلوب | النوع                                           | معناه                                                                                                 |
| --------------------- | ------ | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `provider`            | نعم    | `string`                                        | معرّف المزوّد الذي ينتمي إليه هذا الخيار.                                                              |
| `method`              | نعم    | `string`                                        | معرّف طريقة المصادقة المطلوب التوجيه إليه.                                                            |
| `choiceId`            | نعم    | `string`                                        | معرّف ثابت لخيار المصادقة يُستخدم بواسطة تدفقات الإعداد الأولي وCLI.                                  |
| `choiceLabel`         | لا     | `string`                                        | تسمية موجهة للمستخدم. إذا حُذفت، يعود OpenClaw إلى `choiceId`.                                       |
| `choiceHint`          | لا     | `string`                                        | نص مساعد قصير للمحدد.                                                                                 |
| `assistantPriority`   | لا     | `number`                                        | تُرتّب القيم الأقل أولًا في المحددات التفاعلية التي يقودها المساعد.                                   |
| `assistantVisibility` | لا     | `"visible"` \| `"manual-only"`                  | يُخفي الخيار من محددات المساعد مع السماح مع ذلك بالاختيار اليدوي عبر CLI.                            |
| `deprecatedChoiceIds` | لا     | `string[]`                                      | معرّفات خيارات قديمة يجب أن تعيد توجيه المستخدمين إلى هذا الخيار البديل.                              |
| `groupId`             | لا     | `string`                                        | معرّف مجموعة اختياري لتجميع الخيارات المرتبطة.                                                        |
| `groupLabel`          | لا     | `string`                                        | تسمية موجهة للمستخدم لتلك المجموعة.                                                                   |
| `groupHint`           | لا     | `string`                                        | نص مساعد قصير للمجموعة.                                                                               |
| `optionKey`           | لا     | `string`                                        | مفتاح خيار داخلي لتدفقات المصادقة البسيطة أحادية العلم.                                              |
| `cliFlag`             | لا     | `string`                                        | اسم علم CLI، مثل `--openrouter-api-key`.                                                              |
| `cliOption`           | لا     | `string`                                        | شكل خيار CLI الكامل، مثل `--openrouter-api-key <key>`.                                               |
| `cliDescription`      | لا     | `string`                                        | الوصف المستخدم في تعليمات CLI.                                                                        |
| `onboardingScopes`    | لا     | `Array<"text-inference" \| "image-generation">` | أسطح الإعداد الأولي التي يجب أن يظهر فيها هذا الخيار. إذا حُذفت، تكون القيمة الافتراضية `["text-inference"]`. |

## مرجع uiHints

`uiHints` هي خريطة من أسماء حقول الإعدادات إلى تلميحات عرض صغيرة.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "help": "Used for OpenRouter requests",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

يمكن أن يتضمن كل تلميح حقل ما يلي:

| الحقل         | النوع      | معناه                                 |
| ------------- | ---------- | ------------------------------------- |
| `label`       | `string`   | تسمية حقل موجهة للمستخدم.             |
| `help`        | `string`   | نص مساعد قصير.                        |
| `tags`        | `string[]` | وسوم واجهة مستخدم اختيارية.           |
| `advanced`    | `boolean`  | يحدد أن الحقل متقدم.                  |
| `sensitive`   | `boolean`  | يحدد أن الحقل سري أو حساس.            |
| `placeholder` | `string`   | نص العنصر النائب لحقول الإدخال.       |

## مرجع contracts

استخدم `contracts` فقط لبيانات ملكية الإمكانات الثابتة التي يمكن لـ OpenClaw
قراءتها من دون استيراد وقت تشغيل الإضافة.

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

كل قائمة اختيارية:

| الحقل                            | النوع      | معناه                                                        |
| -------------------------------- | ---------- | ------------------------------------------------------------ |
| `speechProviders`                | `string[]` | معرّفات مزوّدي speech التي تملكها هذه الإضافة.               |
| `realtimeTranscriptionProviders` | `string[]` | معرّفات مزوّدي realtime-transcription التي تملكها هذه الإضافة. |
| `realtimeVoiceProviders`         | `string[]` | معرّفات مزوّدي realtime-voice التي تملكها هذه الإضافة.       |
| `mediaUnderstandingProviders`    | `string[]` | معرّفات مزوّدي media-understanding التي تملكها هذه الإضافة.  |
| `imageGenerationProviders`       | `string[]` | معرّفات مزوّدي image-generation التي تملكها هذه الإضافة.     |
| `videoGenerationProviders`       | `string[]` | معرّفات مزوّدي video-generation التي تملكها هذه الإضافة.     |
| `webFetchProviders`              | `string[]` | معرّفات مزوّدي web-fetch التي تملكها هذه الإضافة.            |
| `webSearchProviders`             | `string[]` | معرّفات مزوّدي web-search التي تملكها هذه الإضافة.           |
| `tools`                          | `string[]` | أسماء أدوات الوكيل التي تملكها هذه الإضافة لفحوصات العقود المضمّنة. |

## مرجع channelConfigs

استخدم `channelConfigs` عندما تحتاج إضافة قناة إلى بيانات إعدادات خفيفة قبل
تحميل وقت التشغيل.

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "Homeserver URL",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Matrix homeserver connection",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

يمكن أن يتضمن كل إدخال قناة ما يلي:

| الحقل         | النوع                    | معناه                                                                                     |
| ------------- | ------------------------ | ----------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | JSON Schema لـ `channels.<id>`. مطلوب لكل إدخال إعدادات قناة مُعلن عنه.                  |
| `uiHints`     | `Record<string, object>` | تسميات واجهة مستخدم اختيارية/عناصر نائبة/تلميحات حساسية لقسم إعدادات تلك القناة.         |
| `label`       | `string`                 | تسمية القناة المدمجة في أسطح المحدد والفحص عندما لا تكون بيانات وقت التشغيل الوصفية جاهزة. |
| `description` | `string`                 | وصف قصير للقناة لأسطح الفحص والفهرس.                                                     |
| `preferOver`  | `string[]`               | معرّفات إضافات قديمة أو أقل أولوية يجب أن تتفوق عليها هذه القناة في أسطح الاختيار.       |

## مرجع modelSupport

استخدم `modelSupport` عندما يجب على OpenClaw استنتاج إضافة المزوّد الخاصة بك من
معرّفات نماذج مختصرة مثل `gpt-5.4` أو `claude-sonnet-4.6` قبل أن يحمّل وقت تشغيل الإضافة.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

يطبق OpenClaw ترتيب الأولوية هذا:

- تستخدم مراجع `provider/model` الصريحة بيانات `providers` الوصفية المملوكة للبيان
- تتغلب `modelPatterns` على `modelPrefixes`
- إذا طابقت كل من إضافة غير مضمّنة وإضافة مضمّنة، تفوز الإضافة غير المضمّنة
- يُتجاهل الغموض المتبقي إلى أن يحدد المستخدم أو الإعدادات مزوّدًا

الحقول:

| الحقل           | النوع      | معناه                                                                          |
| --------------- | ---------- | ------------------------------------------------------------------------------ |
| `modelPrefixes` | `string[]` | بادئات تُطابق باستخدام `startsWith` مع معرّفات النماذج المختصرة.               |
| `modelPatterns` | `string[]` | مصادر Regex تُطابق مع معرّفات النماذج المختصرة بعد إزالة لاحقة ملف التعريف.     |

أصبحت مفاتيح الإمكانات القديمة ذات المستوى الأعلى مهملة. استخدم `openclaw doctor --fix`
لنقل `speechProviders` و`realtimeTranscriptionProviders`،
و`realtimeVoiceProviders` و`mediaUnderstandingProviders`،
و`imageGenerationProviders` و`videoGenerationProviders`،
و`webFetchProviders` و`webSearchProviders` إلى `contracts`؛ فلم يعد
تحميل البيانات العادي يعامل تلك الحقول ذات المستوى الأعلى كملكية
للإمكانات.

## البيان مقابل package.json

يخدم الملفان مهمتين مختلفتين:

| الملف                  | الاستخدام                                                                                                                          |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | الاكتشاف، والتحقق من صحة الإعدادات، وبيانات خيارات المصادقة، وتلميحات واجهة المستخدم التي يجب أن توجد قبل تشغيل كود الإضافة       |
| `package.json`         | بيانات npm الوصفية، وتثبيت التبعيات، وكتلة `openclaw` المستخدمة لنقاط الدخول، وضبط التثبيت، والإعداد، أو بيانات الفهرس الوصفية |

إذا لم تكن متأكدًا من المكان الذي تنتمي إليه قطعة من البيانات الوصفية، فاستخدم هذه القاعدة:

- إذا كان يجب على OpenClaw معرفتها قبل تحميل كود الإضافة، فضعها في `openclaw.plugin.json`
- إذا كانت تتعلق بالتغليف، أو ملفات الإدخال، أو سلوك تثبيت npm، فضعها في `package.json`

### حقول package.json التي تؤثر في الاكتشاف

توجد بعض بيانات الإضافة الوصفية لما قبل وقت التشغيل عمدًا في `package.json` ضمن
كتلة `openclaw` بدلًا من `openclaw.plugin.json`.

أمثلة مهمة:

| الحقل                                                             | معناه                                                                                                                                      |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `openclaw.extensions`                                             | يعلن نقاط دخول الإضافات الأصلية.                                                                                                          |
| `openclaw.setupEntry`                                             | نقطة دخول خفيفة خاصة بالإعداد فقط وتُستخدم أثناء الإعداد الأولي وبدء تشغيل القنوات المؤجل.                                                |
| `openclaw.channel`                                                | بيانات وصفية خفيفة لفهرس القنوات مثل التسميات ومسارات المستندات والأسماء المستعارة ونص الاختيار.                                         |
| `openclaw.channel.configuredState`                                | بيانات وصفية خفيفة لفاحص الحالة المضبوطة يمكنها الإجابة عن سؤال "هل يوجد إعداد قائم على البيئة فقط بالفعل؟" من دون تحميل وقت تشغيل القناة الكامل. |
| `openclaw.channel.persistedAuthState`                             | بيانات وصفية خفيفة لفاحص المصادقة المحفوظة يمكنها الإجابة عن سؤال "هل تم تسجيل الدخول إلى أي شيء بالفعل؟" من دون تحميل وقت تشغيل القناة الكامل. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | تلميحات التثبيت/التحديث للإضافات المضمّنة والمنشورة خارجيًا.                                                                              |
| `openclaw.install.defaultChoice`                                  | مسار التثبيت المفضل عندما تكون هناك مصادر تثبيت متعددة متاحة.                                                                             |
| `openclaw.install.minHostVersion`                                 | الحد الأدنى لإصدار مضيف OpenClaw المدعوم، باستخدام حد أدنى semver مثل `>=2026.3.22`.                                                     |
| `openclaw.install.allowInvalidConfigRecovery`                     | يسمح بمسار استرداد ضيق لإعادة تثبيت الإضافات المضمّنة عندما تكون الإعدادات غير صالحة.                                                     |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | يسمح بتحميل أسطح القنوات الخاصة بالإعداد فقط قبل الإضافة الكاملة للقناة أثناء بدء التشغيل.                                                 |

يُفرض `openclaw.install.minHostVersion` أثناء التثبيت وتحميل سجل البيان.
تُرفض القيم غير الصالحة؛ أما القيم الأحدث ولكن الصالحة فتتجاوز
الإضافة على المضيفات الأقدم.

إن `openclaw.install.allowInvalidConfigRecovery` ضيق عمدًا. فهو
لا يجعل الإعدادات المعطوبة العشوائية قابلة للتثبيت. واليوم لا يسمح إلا
لتدفقات التثبيت بالتعافي من حالات فشل ترقية محددة في الإضافات المضمّنة القديمة، مثل
مسار إضافة مضمّنة مفقود أو إدخال `channels.<id>` قديم للإضافة المضمّنة نفسها.
أما أخطاء الإعدادات غير ذات الصلة فلا تزال تمنع التثبيت وتوجّه المشغلين
إلى `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` هو بيانات حزمة وصفية لوحدة فاحص
صغيرة:

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

استخدمه عندما تحتاج تدفقات الإعداد أو doctor أو الحالة المضبوطة إلى
فحص مصادقة خفيف بنعم/لا قبل تحميل إضافة القناة الكاملة. يجب أن يكون
التصدير الهدف دالة صغيرة تقرأ الحالة المحفوظة فقط؛ لا تمررها عبر شريط
وقت تشغيل القناة الكامل.

يتبع `openclaw.channel.configuredState` الشكل نفسه لفحوصات الحالة المضبوطة
الخفيفة المعتمدة على البيئة فقط:

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

استخدمه عندما تتمكن القناة من تحديد الحالة المضبوطة من البيئة أو من
مدخلات صغيرة غير مرتبطة بوقت التشغيل. إذا كان الفحص يحتاج إلى حل إعدادات كامل أو
وقت تشغيل القناة الفعلي، فأبقِ هذا المنطق في خطاف الإضافة
`config.hasConfiguredState` بدلًا من ذلك.

## متطلبات JSON Schema

- **يجب أن تشحن كل إضافة JSON Schema**، حتى لو كانت لا تقبل أي إعدادات.
- يُقبل مخطط فارغ (على سبيل المثال، `{ "type": "object", "additionalProperties": false }`).
- يتم التحقق من المخططات في وقت قراءة/كتابة الإعدادات، وليس في وقت التشغيل.

## سلوك التحقق

- مفاتيح `channels.*` غير المعروفة تُعد **أخطاء**، ما لم يكن معرّف القناة مُعلنًا
  بواسطة بيان إضافة.
- يجب أن تشير `plugins.entries.<id>` و`plugins.allow` و`plugins.deny` و`plugins.slots.*`
  إلى معرّفات إضافات **قابلة للاكتشاف**. والمعرّفات غير المعروفة تُعد **أخطاء**.
- إذا كانت الإضافة مثبتة ولكن بيانها أو مخططها معطوبًا أو مفقودًا،
  يفشل التحقق من الصحة ويبلّغ Doctor عن خطأ الإضافة.
- إذا كانت إعدادات الإضافة موجودة ولكن الإضافة **معطلة**، تُحتفظ الإعدادات
  ويظهر **تحذير** في Doctor + السجلات.

راجع [مرجع الإعدادات](/ar/gateway/configuration) للحصول على مخطط `plugins.*` الكامل.

## ملاحظات

- البيان **مطلوب للإضافات الأصلية في OpenClaw**، بما في ذلك التحميلات المحلية من نظام الملفات.
- لا يزال وقت التشغيل يحمّل وحدة الإضافة بشكل منفصل؛ فالبيان مخصص فقط
  للاكتشاف + التحقق.
- يتم تحليل البيانات الأصلية باستخدام JSON5، لذلك تُقبل التعليقات والفواصل اللاحقة
  والمفاتيح غير الموضوعة بين علامتي اقتباس ما دامت القيمة النهائية لا تزال كائنًا.
- لا يقرأ محمّل البيان إلا الحقول الموثقة. تجنب إضافة
  مفاتيح مخصصة ذات مستوى أعلى هنا.
- `providerAuthEnvVars` هو مسار البيانات الوصفية الخفيف لفحوصات المصادقة، والتحقق
  من علامات البيئة، وأسُطح مصادقة المزوّد المشابهة التي يجب ألا تشغّل وقت تشغيل الإضافة
  فقط لفحص أسماء متغيرات البيئة.
- يتيح `providerAuthAliases` لمتغيرات المزوّد إعادة استخدام
  متغيرات بيئة المصادقة وملفات تعريف المصادقة والمصادقة المعتمدة على الإعدادات
  وخيار الإعداد الأولي لمفتاح API لمزوّد آخر من دون ترميز هذه العلاقة
  بشكل صلب في النواة.
- `channelEnvVars` هو مسار البيانات الوصفية الخفيف للرجوع إلى shell-env، ورسائل
  الإعداد، وأسطح القنوات المشابهة التي يجب ألا تشغّل وقت تشغيل الإضافة
  فقط لفحص أسماء متغيرات البيئة.
- `providerAuthChoices` هو مسار البيانات الوصفية الخفيف لمحددات خيارات المصادقة،
  وحل `--auth-choice`، وربط المزوّد المفضل، وتسجيل أعلام CLI البسيطة
  للإعداد الأولي قبل تحميل وقت تشغيل المزوّد. أما بيانات معالج وقت التشغيل
  التي تتطلب كود المزوّد، فراجع
  [خطافات وقت تشغيل المزوّد](/ar/plugins/architecture#provider-runtime-hooks).
- يتم اختيار أنواع الإضافات الحصرية من خلال `plugins.slots.*`.
  - يتم اختيار `kind: "memory"` بواسطة `plugins.slots.memory`.
  - يتم اختيار `kind: "context-engine"` بواسطة `plugins.slots.contextEngine`
    (الافتراضي: `legacy` المضمّن).
- يمكن حذف `channels` و`providers` و`cliBackends` و`skills` عندما
  لا تحتاج الإضافة إليها.
- إذا كانت إضافتك تعتمد على وحدات أصلية، فوثّق خطوات البناء وأي
  متطلبات قائمة سماح لمدير الحزم (على سبيل المثال، pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## ذو صلة

- [بناء الإضافات](/ar/plugins/building-plugins) — البدء باستخدام الإضافات
- [بنية الإضافات](/ar/plugins/architecture) — البنية الداخلية
- [نظرة عامة على SDK](/ar/plugins/sdk-overview) — مرجع Plugin SDK
