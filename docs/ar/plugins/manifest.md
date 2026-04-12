---
read_when:
    - أنت تبني Plugin لـ OpenClaw
    - تحتاج إلى شحن مخطط إعدادات Plugin أو تصحيح أخطاء التحقق من صحة Plugin
summary: متطلبات Plugin manifest + مخطط JSON ‏(التحقق الصارم من صحة الإعدادات)
title: Plugin Manifest
x-i18n:
    generated_at: "2026-04-12T23:28:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 93b57c7373e4ccd521b10945346db67991543bd2bed4cc8b6641e1f215b48579
    source_path: plugins/manifest.md
    workflow: 15
---

# Plugin manifest ‏(`openclaw.plugin.json`)

هذه الصفحة مخصّصة فقط لـ **Plugin manifest الأصلي في OpenClaw**.

للتعرف على تخطيطات الحزم المتوافقة، راجع [حزم Plugin](/ar/plugins/bundles).

تستخدم تنسيقات الحزم المتوافقة ملفات manifest مختلفة:

- حزمة Codex: `.codex-plugin/plugin.json`
- حزمة Claude: `.claude-plugin/plugin.json` أو تخطيط مكوّن Claude الافتراضي
  من دون manifest
- حزمة Cursor: `.cursor-plugin/plugin.json`

يكتشف OpenClaw تلقائيًا تخطيطات الحزم هذه أيضًا، لكنها لا تُتحقق
مقابل مخطط `openclaw.plugin.json` الموضّح هنا.

بالنسبة إلى الحزم المتوافقة، يقرأ OpenClaw حاليًا بيانات تعريف الحزمة بالإضافة إلى
جذور skill المعلنة، وجذور أوامر Claude، والقيم الافتراضية لملف `settings.json` في حزمة Claude،
والقيم الافتراضية لـ Claude bundle LSP، وحِزم Hook المدعومة عندما يطابق التخطيط
توقعات وقت تشغيل OpenClaw.

يجب على كل Plugin أصلي في OpenClaw **أن** يوفّر ملف `openclaw.plugin.json` داخل
**جذر Plugin**. يستخدم OpenClaw هذا الـ manifest للتحقق من صحة الإعدادات
**من دون تنفيذ كود Plugin**. وتُعامل ملفات manifest المفقودة أو غير الصالحة
كأخطاء Plugin وتمنع التحقق من صحة الإعدادات.

راجع الدليل الكامل لنظام Plugin: [Plugins](/ar/tools/plugin).
وللاطلاع على نموذج القدرات الأصلي وإرشادات التوافق الخارجي الحالية:
[نموذج القدرات](/ar/plugins/architecture#public-capability-model).

## ما وظيفة هذا الملف

`openclaw.plugin.json` هو ملف البيانات الوصفية الذي يقرأه OpenClaw قبل أن يحمّل
كود Plugin الخاص بك.

استخدمه من أجل:

- هوية Plugin
- التحقق من صحة الإعدادات
- بيانات تعريف المصادقة والإعداد الأولي التي يجب أن تكون متاحة من دون تشغيل وقت تشغيل Plugin
- تلميحات تنشيط خفيفة يمكن لأسطح مستوى التحكم فحصها قبل تحميل وقت التشغيل
- واصفات إعداد خفيفة يمكن لأسطح الإعداد/التهيئة الأولية فحصها قبل
  تحميل وقت التشغيل
- بيانات تعريف الأسماء البديلة والتمكين التلقائي التي يجب حلها قبل تحميل وقت تشغيل Plugin
- بيانات تعريف مختصرة لملكية عائلة النموذج يجب أن تفعّل
  Plugin تلقائيًا قبل تحميل وقت التشغيل
- لقطات ثابتة لملكية القدرات تُستخدم في أسلاك التوافق المجمّعة وتغطية العقود
- بيانات تعريف إعدادات خاصة بالقنوات يجب دمجها في أسطح الكتالوج والتحقق
  من دون تحميل وقت التشغيل
- تلميحات واجهة المستخدم للإعدادات

لا تستخدمه من أجل:

- تسجيل سلوك وقت التشغيل
- تعريف نقاط دخول الكود
- بيانات تعريف تثبيت npm

فهذه تنتمي إلى كود Plugin الخاص بك وإلى `package.json`.

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

## مثال موسّع

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

| الحقل                               | مطلوب | النوع                            | المعنى                                                                                                                                                                                                       |
| ----------------------------------- | ------ | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | نعم    | `string`                         | معرّف Plugin القياسي. هذا هو المعرّف المستخدم في `plugins.entries.<id>`.                                                                                                                                   |
| `configSchema`                      | نعم    | `object`                         | مخطط JSON Schema مضمن لإعدادات هذا Plugin.                                                                                                                                                                   |
| `enabledByDefault`                  | لا     | `true`                           | يحدّد أن Plugin المجمّع مفعّل افتراضيًا. احذف هذا الحقل، أو اضبطه على أي قيمة ليست `true`، لترك Plugin معطّلًا افتراضيًا.                                                                                |
| `legacyPluginIds`                   | لا     | `string[]`                       | معرّفات قديمة تُطبّع إلى معرّف Plugin القياسي هذا.                                                                                                                                                          |
| `autoEnableWhenConfiguredProviders` | لا     | `string[]`                       | معرّفات Provider التي يجب أن تفعّل هذا Plugin تلقائيًا عندما تشير إليها المصادقة أو الإعدادات أو مراجع النموذج.                                                                                           |
| `kind`                              | لا     | `"memory"` \| `"context-engine"` | يصرّح بنوع Plugin حصري يُستخدم بواسطة `plugins.slots.*`.                                                                                                                                                    |
| `channels`                          | لا     | `string[]`                       | معرّفات القنوات التي يملكها هذا Plugin. تُستخدم للاكتشاف والتحقق من صحة الإعدادات.                                                                                                                         |
| `providers`                         | لا     | `string[]`                       | معرّفات Provider التي يملكها هذا Plugin.                                                                                                                                                                     |
| `modelSupport`                      | لا     | `object`                         | بيانات تعريف مختصرة لعائلة النموذج يملكها manifest وتُستخدم لتحميل Plugin تلقائيًا قبل وقت التشغيل.                                                                                                        |
| `cliBackends`                       | لا     | `string[]`                       | معرّفات واجهات CLI الخلفية للاستدلال التي يملكها هذا Plugin. تُستخدم للتنشيط التلقائي عند بدء التشغيل من مراجع الإعدادات الصريحة.                                                                        |
| `commandAliases`                    | لا     | `object[]`                       | أسماء الأوامر التي يملكها هذا Plugin والتي يجب أن تنتج إعدادات خاصة بالـ Plugin وتشخيصات CLI قبل تحميل وقت التشغيل.                                                                                        |
| `providerAuthEnvVars`               | لا     | `Record<string, string[]>`       | بيانات تعريف خفيفة لمتغيرات بيئة مصادقة Provider يمكن لـ OpenClaw فحصها من دون تحميل كود Plugin.                                                                                                           |
| `providerAuthAliases`               | لا     | `Record<string, string>`         | معرّفات Provider التي يجب أن تعيد استخدام معرّف Provider آخر لبحث المصادقة، مثل Provider خاص بالبرمجة يشارك مفتاح API الأساسي وملفات تعريف المصادقة مع Provider الأساسي.                                 |
| `channelEnvVars`                    | لا     | `Record<string, string[]>`       | بيانات تعريف خفيفة لمتغيرات بيئة القنوات يمكن لـ OpenClaw فحصها من دون تحميل كود Plugin. استخدم هذا لأسطح إعداد القنوات أو المصادقة المعتمدة على البيئة التي ينبغي أن تراها مساعدات بدء التشغيل/الإعداد العامة. |
| `providerAuthChoices`               | لا     | `object[]`                       | بيانات تعريف خفيفة لاختيارات المصادقة لمحددات الإعداد الأولي، وحل Provider المفضّل، وربط أعلام CLI البسيطة.                                                                                                 |
| `activation`                        | لا     | `object`                         | تلميحات تنشيط خفيفة لتحميل يعتمد على Provider أو الأمر أو القناة أو المسار أو القدرات. بيانات تعريف فقط؛ وما يزال وقت تشغيل Plugin يملك السلوك الفعلي.                                                     |
| `setup`                             | لا     | `object`                         | واصفات إعداد/تهيئة أولية خفيفة يمكن لأسطح الاكتشاف والإعداد فحصها من دون تحميل وقت تشغيل Plugin.                                                                                                          |
| `contracts`                         | لا     | `object`                         | لقطة قدرات ثابتة مجمّعة لملكية speech وrealtime transcription وrealtime voice وmedia-understanding وimage-generation وmusic-generation وvideo-generation وweb-fetch وweb search والأدوات.                      |
| `channelConfigs`                    | لا     | `Record<string, object>`         | بيانات تعريف إعدادات القنوات المملوكة من manifest والتي تُدمج في أسطح الاكتشاف والتحقق قبل تحميل وقت التشغيل.                                                                                               |
| `skills`                            | لا     | `string[]`                       | أدلة Skills التي يجب تحميلها، نسبةً إلى جذر Plugin.                                                                                                                                                         |
| `name`                              | لا     | `string`                         | اسم Plugin مقروء للبشر.                                                                                                                                                                                      |
| `description`                       | لا     | `string`                         | ملخص قصير يظهر في أسطح Plugin.                                                                                                                                                                               |
| `version`                           | لا     | `string`                         | إصدار معلوماتي لـ Plugin.                                                                                                                                                                                    |
| `uiHints`                           | لا     | `Record<string, object>`         | تسميات واجهة المستخدم، والعناصر النائبة، وتلميحات الحساسية لحقول الإعدادات.                                                                                                                                 |

## مرجع `providerAuthChoices`

يصف كل إدخال في `providerAuthChoices` خيار إعداد أولي أو مصادقة واحدًا.
يقرأ OpenClaw هذا قبل تحميل وقت تشغيل Provider.

| الحقل                | مطلوب | النوع                                           | المعنى                                                                                           |
| -------------------- | ------ | ----------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `provider`           | نعم    | `string`                                        | معرّف Provider الذي ينتمي إليه هذا الخيار.                                                        |
| `method`             | نعم    | `string`                                        | معرّف طريقة المصادقة المراد التوجيه إليها.                                                        |
| `choiceId`           | نعم    | `string`                                        | معرّف ثابت لخيار المصادقة يُستخدم في مسارات الإعداد الأولي وCLI.                                 |
| `choiceLabel`        | لا     | `string`                                        | تسمية موجهة للمستخدم. إذا تم حذفها، يعود OpenClaw إلى `choiceId`.                                |
| `choiceHint`         | لا     | `string`                                        | نص مساعد قصير للمحدد.                                                                            |
| `assistantPriority`  | لا     | `number`                                        | القيم الأقل تُرتّب أولًا في المحددات التفاعلية التي يقودها المساعد.                              |
| `assistantVisibility`| لا     | `"visible"` \| `"manual-only"`                  | إخفاء الخيار من محددات المساعد مع الاستمرار في السماح بالاختيار اليدوي عبر CLI.                  |
| `deprecatedChoiceIds`| لا     | `string[]`                                      | معرّفات خيارات قديمة يجب أن تعيد توجيه المستخدمين إلى هذا الخيار البديل.                         |
| `groupId`            | لا     | `string`                                        | معرّف مجموعة اختياري لتجميع الخيارات ذات الصلة.                                                  |
| `groupLabel`         | لا     | `string`                                        | تسمية موجهة للمستخدم لتلك المجموعة.                                                               |
| `groupHint`          | لا     | `string`                                        | نص مساعد قصير للمجموعة.                                                                           |
| `optionKey`          | لا     | `string`                                        | مفتاح خيار داخلي لمسارات المصادقة البسيطة ذات العلم الواحد.                                      |
| `cliFlag`            | لا     | `string`                                        | اسم علم CLI، مثل `--openrouter-api-key`.                                                         |
| `cliOption`          | لا     | `string`                                        | الشكل الكامل لخيار CLI، مثل `--openrouter-api-key <key>`.                                        |
| `cliDescription`     | لا     | `string`                                        | الوصف المستخدم في مساعدة CLI.                                                                     |
| `onboardingScopes`   | لا     | `Array<"text-inference" \| "image-generation">` | أسطح الإعداد الأولي التي يجب أن يظهر فيها هذا الخيار. إذا تم حذفه، تكون القيمة الافتراضية `["text-inference"]`. |

## مرجع `commandAliases`

استخدم `commandAliases` عندما يملك Plugin اسم أمر وقت تشغيل قد يضعه المستخدمون
عن طريق الخطأ في `plugins.allow` أو يحاولون تشغيله كأمر CLI جذري. يستخدم OpenClaw
هذه البيانات الوصفية لأغراض التشخيص من دون استيراد كود وقت تشغيل Plugin.

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| الحقل       | مطلوب | النوع             | المعنى                                                                      |
| ----------- | ------ | ----------------- | ---------------------------------------------------------------------------- |
| `name`      | نعم    | `string`          | اسم الأمر الذي ينتمي إلى هذا Plugin.                                        |
| `kind`      | لا     | `"runtime-slash"` | يحدد الاسم البديل كأمر slash للدردشة بدلًا من أمر CLI جذري.                 |
| `cliCommand`| لا     | `string`          | أمر CLI جذري ذو صلة يُقترح لعمليات CLI، إذا كان موجودًا.                    |

## مرجع `activation`

استخدم `activation` عندما يمكن لـ Plugin أن يصرّح بتكلفة منخفضة عن أحداث مستوى التحكم
التي ينبغي أن تفعّله لاحقًا.

هذه الكتلة عبارة عن بيانات وصفية فقط. فهي لا تسجل سلوك وقت التشغيل، ولا
تحل محل `register(...)` أو `setupEntry` أو نقاط دخول وقت التشغيل/Plugin الأخرى.
يستخدمها المستهلكون الحاليون كتلميح تضييق قبل تحميل Plugin الأوسع، لذلك فإن
غياب بيانات تعريف التنشيط عادةً لا يكلّف سوى الأداء؛ ولا ينبغي أن
يغيّر الصحة ما دامت آليات fallback القديمة لملكية manifest لا تزال موجودة.

```json
{
  "activation": {
    "onProviders": ["openai"],
    "onCommands": ["models"],
    "onChannels": ["web"],
    "onRoutes": ["gateway-webhook"],
    "onCapabilities": ["provider", "tool"]
  }
}
```

| الحقل            | مطلوب | النوع                                                | المعنى                                                        |
| ---------------- | ------ | ---------------------------------------------------- | ------------------------------------------------------------- |
| `onProviders`    | لا     | `string[]`                                           | معرّفات Provider التي ينبغي أن تفعّل هذا Plugin عند طلبها.    |
| `onCommands`     | لا     | `string[]`                                           | معرّفات الأوامر التي ينبغي أن تفعّل هذا Plugin.               |
| `onChannels`     | لا     | `string[]`                                           | معرّفات القنوات التي ينبغي أن تفعّل هذا Plugin.               |
| `onRoutes`       | لا     | `string[]`                                           | أنواع المسارات التي ينبغي أن تفعّل هذا Plugin.                |
| `onCapabilities` | لا     | `Array<"provider" \| "channel" \| "tool" \| "hook">` | تلميحات قدرات عامة تُستخدم في تخطيط التنشيط على مستوى التحكم. |

المستهلكون الحاليون الفعليون:

- تخطيط CLI المُفعّل بالأوامر يعود إلى الآلية القديمة
  `commandAliases[].cliCommand` أو `commandAliases[].name`
- تخطيط الإعداد/القنوات المُفعّل بالقنوات يعود إلى ملكية
  `channels[]` القديمة عندما تكون بيانات تعريف تنشيط القنوات الصريحة مفقودة
- تخطيط الإعداد/وقت التشغيل المُفعّل بمزوّد Provider يعود إلى الملكية القديمة
  `providers[]` وملكية `cliBackends[]` ذات المستوى الأعلى عندما تكون بيانات تعريف
  تنشيط Provider الصريحة مفقودة

## مرجع `setup`

استخدم `setup` عندما تحتاج أسطح الإعداد والتهيئة الأولية إلى بيانات تعريف منخفضة الكلفة يملكها Plugin
قبل تحميل وقت التشغيل.

```json
{
  "setup": {
    "providers": [
      {
        "id": "openai",
        "authMethods": ["api-key"],
        "envVars": ["OPENAI_API_KEY"]
      }
    ],
    "cliBackends": ["openai-cli"],
    "configMigrations": ["legacy-openai-auth"],
    "requiresRuntime": false
  }
}
```

يبقى `cliBackends` ذو المستوى الأعلى صالحًا ويستمر في وصف
واجهات CLI الخلفية للاستدلال. أمّا `setup.cliBackends` فهو سطح الواصفات
الخاص بالإعداد لمسارات مستوى التحكم/الإعداد التي ينبغي أن تبقى بيانات وصفية فقط.

عند وجودها، تُعد `setup.providers` و`setup.cliBackends` سطح البحث المفضل
القائم على الواصفات أولًا لاكتشاف الإعداد. وإذا كان الواصف يضيّق فقط
Plugin المرشح وكان الإعداد لا يزال يحتاج إلى Hooks وقت تشغيل أغنى في وقت الإعداد،
فاضبط `requiresRuntime: true` وأبقِ `setup-api` في مكانه
كمسار تنفيذ احتياطي.

ولأن بحث الإعداد يمكن أن ينفّذ كود `setup-api` يملكه Plugin،
فيجب أن تبقى القيم المطَبَّعة في `setup.providers[].id` و`setup.cliBackends[]`
فريدة عبر Plugins المكتشفة. وتفشل الملكية الملتبسة بشكل مغلق بدلًا من
اختيار فائز بحسب ترتيب الاكتشاف.

### مرجع `setup.providers`

| الحقل         | مطلوب | النوع      | المعنى                                                                                 |
| ------------- | ------ | ---------- | --------------------------------------------------------------------------------------- |
| `id`          | نعم    | `string`   | معرّف Provider المُعرَض أثناء الإعداد أو التهيئة الأولية. حافظ على فرادة المعرّفات المطَبَّعة عالميًا. |
| `authMethods` | لا     | `string[]` | معرّفات أساليب الإعداد/المصادقة التي يدعمها هذا Provider من دون تحميل وقت التشغيل الكامل. |
| `envVars`     | لا     | `string[]` | متغيرات البيئة التي يمكن لأسطح الإعداد/الحالة العامة التحقق منها قبل تحميل وقت تشغيل Plugin. |

### حقول `setup`

| الحقل              | مطلوب | النوع      | المعنى                                                                                           |
| ------------------ | ------ | ---------- | ------------------------------------------------------------------------------------------------- |
| `providers`        | لا     | `object[]` | واصفات إعداد Provider المعروضة أثناء الإعداد والتهيئة الأولية.                                    |
| `cliBackends`      | لا     | `string[]` | معرّفات الواجهات الخلفية وقت الإعداد المستخدمة للبحث القائم على الواصفات أولًا. حافظ على فرادة المعرّفات المطَبَّعة عالميًا. |
| `configMigrations` | لا     | `string[]` | معرّفات ترحيل الإعدادات التي يملكها سطح الإعداد لهذا Plugin.                                     |
| `requiresRuntime`  | لا     | `boolean`  | ما إذا كان الإعداد لا يزال يحتاج إلى تنفيذ `setup-api` بعد البحث القائم على الواصفات.            |

## مرجع `uiHints`

`uiHints` هو خريطة من أسماء حقول الإعدادات إلى تلميحات عرض صغيرة.

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

| الحقل        | النوع      | المعنى                                 |
| ------------ | ---------- | -------------------------------------- |
| `label`      | `string`   | تسمية الحقل الموجهة للمستخدم.          |
| `help`       | `string`   | نص مساعد قصير.                         |
| `tags`       | `string[]` | وسوم واجهة مستخدم اختيارية.            |
| `advanced`   | `boolean`  | يحدد الحقل على أنه متقدم.              |
| `sensitive`  | `boolean`  | يحدد الحقل على أنه سري أو حساس.        |
| `placeholder`| `string`   | نص العنصر النائب لحقول النماذج.        |

## مرجع `contracts`

استخدم `contracts` فقط لبيانات تعريف ملكية القدرات الثابتة التي يمكن لـ OpenClaw
قراءتها من دون استيراد وقت تشغيل Plugin.

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

| الحقل                            | النوع      | المعنى                                                     |
| -------------------------------- | ---------- | ---------------------------------------------------------- |
| `speechProviders`                | `string[]` | معرّفات موفري Speech التي يملكها هذا Plugin.               |
| `realtimeTranscriptionProviders` | `string[]` | معرّفات موفري realtime-transcription التي يملكها هذا Plugin. |
| `realtimeVoiceProviders`         | `string[]` | معرّفات موفري realtime-voice التي يملكها هذا Plugin.       |
| `mediaUnderstandingProviders`    | `string[]` | معرّفات موفري media-understanding التي يملكها هذا Plugin.  |
| `imageGenerationProviders`       | `string[]` | معرّفات موفري image-generation التي يملكها هذا Plugin.     |
| `videoGenerationProviders`       | `string[]` | معرّفات موفري video-generation التي يملكها هذا Plugin.     |
| `webFetchProviders`              | `string[]` | معرّفات موفري web-fetch التي يملكها هذا Plugin.            |
| `webSearchProviders`             | `string[]` | معرّفات موفري web-search التي يملكها هذا Plugin.           |
| `tools`                          | `string[]` | أسماء أدوات الوكيل التي يملكها هذا Plugin لفحوصات العقود المجمّعة. |

## مرجع `channelConfigs`

استخدم `channelConfigs` عندما يحتاج Plugin قناة إلى بيانات تعريف إعدادات منخفضة الكلفة قبل
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

| الحقل        | النوع                    | المعنى                                                                                 |
| ------------ | ------------------------ | --------------------------------------------------------------------------------------- |
| `schema`     | `object`                 | JSON Schema لـ `channels.<id>`. مطلوب لكل إدخال إعدادات قناة مُعلن عنه.                |
| `uiHints`    | `Record<string, object>` | تسميات واجهة مستخدم/عناصر نائبة/تلميحات حساسية اختيارية لقسم إعدادات تلك القناة.       |
| `label`      | `string`                 | تسمية القناة المدمجة في أسطح الاختيار والفحص عندما لا تكون بيانات تعريف وقت التشغيل جاهزة. |
| `description`| `string`                 | وصف قصير للقناة لأسطح الفحص والكتالوج.                                                 |
| `preferOver` | `string[]`               | معرّفات Plugin قديمة أو أقل أولوية ينبغي أن تتفوق عليها هذه القناة في أسطح الاختيار.   |

## مرجع `modelSupport`

استخدم `modelSupport` عندما ينبغي لـ OpenClaw أن يستنتج Plugin Provider الخاص بك من
معرّفات نماذج مختصرة مثل `gpt-5.4` أو `claude-sonnet-4.6` قبل أن يُحمَّل وقت تشغيل Plugin.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

يطبّق OpenClaw أسبقية الترتيب التالية:

- تستخدم مراجع `provider/model` الصريحة بيانات تعريف manifest المملوكة في `providers`
- تتفوق `modelPatterns` على `modelPrefixes`
- إذا طابق Plugin غير مجمّع وPlugin مجمّع معًا، فإن
  Plugin غير المجمّع يفوز
- يتم تجاهل أي غموض متبقٍ حتى يحدد المستخدم أو الإعدادات Provider

الحقول:

| الحقل          | النوع      | المعنى                                                                        |
| -------------- | ---------- | ----------------------------------------------------------------------------- |
| `modelPrefixes`| `string[]` | بادئات تتم مطابقتها باستخدام `startsWith` مع معرّفات النماذج المختصرة.       |
| `modelPatterns`| `string[]` | مصادر Regex تتم مطابقتها مع معرّفات النماذج المختصرة بعد إزالة لاحقة profile. |

مفاتيح القدرات القديمة ذات المستوى الأعلى أصبحت مهجورة. استخدم `openclaw doctor --fix`
لنقل `speechProviders` و`realtimeTranscriptionProviders`،
و`realtimeVoiceProviders` و`mediaUnderstandingProviders`،
و`imageGenerationProviders` و`videoGenerationProviders`،
و`webFetchProviders` و`webSearchProviders` إلى `contracts`؛ ولم يعد
تحميل manifest العادي يعامل تلك الحقول ذات المستوى الأعلى على أنها
ملكية للقدرات.

## الـ Manifest مقابل `package.json`

يخدم الملفان وظيفتين مختلفتين:

| الملف                  | استخدمه من أجل                                                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | الاكتشاف، والتحقق من صحة الإعدادات، وبيانات تعريف خيارات المصادقة، وتلميحات واجهة المستخدم التي يجب أن توجد قبل تشغيل كود Plugin |
| `package.json`         | بيانات تعريف npm، وتثبيت التبعيات، وكتلة `openclaw` المستخدمة لنقاط الدخول، وبوابات التثبيت، والإعداد، أو بيانات تعريف الكتالوج |

إذا لم تكن متأكدًا من موضع قطعة بيانات تعريف معينة، فاستخدم هذه القاعدة:

- إذا كان يجب على OpenClaw معرفتها قبل تحميل كود Plugin، فضعها في `openclaw.plugin.json`
- إذا كانت تتعلق بالتغليف أو ملفات الدخول أو سلوك تثبيت npm، فضعها في `package.json`

### حقول `package.json` التي تؤثر في الاكتشاف

توجد بعض بيانات تعريف Plugin السابقة لوقت التشغيل عمدًا داخل `package.json` تحت
كتلة `openclaw` بدلًا من `openclaw.plugin.json`.

أمثلة مهمة:

| الحقل                                                            | المعنى                                                                                                                                 |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                            | يصرّح بنقاط دخول Plugin الأصلية.                                                                                                      |
| `openclaw.setupEntry`                                            | نقطة دخول خفيفة مخصّصة للإعداد فقط تُستخدم أثناء التهيئة الأولية وبدء تشغيل القنوات المؤجل.                                          |
| `openclaw.channel`                                               | بيانات تعريف خفيفة لكتالوج القنوات مثل التسميات، ومسارات المستندات، والأسماء البديلة، ونصوص الاختيار.                              |
| `openclaw.channel.configuredState`                               | بيانات تعريف خفيفة لفاحص حالة التهيئة يمكنها الإجابة عن سؤال "هل يوجد إعداد قائم على البيئة فقط بالفعل؟" من دون تحميل وقت تشغيل القناة الكامل. |
| `openclaw.channel.persistedAuthState`                            | بيانات تعريف خفيفة لفاحص المصادقة المحفوظة يمكنها الإجابة عن سؤال "هل توجد أي عملية تسجيل دخول بالفعل؟" من دون تحميل وقت تشغيل القناة الكامل. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`        | تلميحات التثبيت/التحديث الخاصة بالـ Plugins المجمّعة والمنشورة خارجيًا.                                                               |
| `openclaw.install.defaultChoice`                                 | مسار التثبيت المفضل عند توفر عدة مصادر للتثبيت.                                                                                        |
| `openclaw.install.minHostVersion`                                | الحد الأدنى لإصدار مضيف OpenClaw المدعوم، باستخدام حد semver أدنى مثل `>=2026.3.22`.                                                 |
| `openclaw.install.allowInvalidConfigRecovery`                    | يسمح بمسار استرداد ضيق لإعادة تثبيت Plugin مجمّع عندما تكون الإعدادات غير صالحة.                                                      |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`| يتيح تحميل أسطح القنوات الخاصة بالإعداد فقط قبل تحميل Plugin القناة الكامل أثناء بدء التشغيل.                                          |

يتم فرض `openclaw.install.minHostVersion` أثناء التثبيت
وأثناء تحميل سجل manifest. تُرفض القيم غير الصالحة؛ أما القيم الصحيحة
ولكن الأحدث فتتسبب في تخطي Plugin على المضيفات الأقدم.

إن `openclaw.install.allowInvalidConfigRecovery` ضيق النطاق عمدًا. فهو
لا يجعل الإعدادات المعطوبة التعسفية قابلة للتثبيت. اليوم، هو يسمح فقط
لمسارات التثبيت بالتعافي من إخفاقات ترقية معينة قديمة تخص Plugins المجمّعة، مثل
مسار Plugin مجمّع مفقود أو إدخال `channels.<id>` قديم لذلك Plugin المجمّع نفسه.
أما أخطاء الإعدادات غير ذات الصلة فما تزال تمنع التثبيت وتوجّه المشغلين
إلى `openclaw doctor --fix`.

يمثل `openclaw.channel.persistedAuthState` بيانات تعريف حزمة لوحدة فحص صغيرة:

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

استخدمه عندما تحتاج مسارات الإعداد أو doctor أو الحالة المهيأة إلى
فحص مصادقة بسيط بنعم/لا قبل تحميل Plugin القناة الكامل. ينبغي أن يكون
التصدير الهدف دالة صغيرة تقرأ الحالة المحفوظة فقط؛ ولا توجّهها
عبر شريط وقت تشغيل القناة الكامل.

يتبع `openclaw.channel.configuredState` الشكل نفسه من أجل فحوصات التهيئة
البسيطة المعتمدة على البيئة فقط:

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

استخدمه عندما تتمكن قناة من تحديد حالة التهيئة من البيئة أو من مدخلات صغيرة
أخرى غير تشغيلية. وإذا كان الفحص يحتاج إلى حل كامل للإعدادات أو إلى
وقت تشغيل القناة الحقيقي، فأبقِ هذا المنطق داخل Hook
`config.hasConfiguredState` في Plugin بدلًا من ذلك.

## متطلبات JSON Schema

- **يجب على كل Plugin أن يوفّر JSON Schema**، حتى لو كان لا يقبل أي إعدادات.
- يُعد المخطط الفارغ مقبولًا (على سبيل المثال، `{ "type": "object", "additionalProperties": false }`).
- يتم التحقق من المخططات وقت قراءة/كتابة الإعدادات، وليس في وقت التشغيل.

## سلوك التحقق

- تُعد مفاتيح `channels.*` غير المعروفة **أخطاء**، ما لم يكن معرّف القناة معلنًا بواسطة
  manifest خاص بـ Plugin.
- يجب أن تشير `plugins.entries.<id>` و`plugins.allow` و`plugins.deny` و`plugins.slots.*`
  إلى معرّفات Plugin **قابلة للاكتشاف**. وتُعد المعرّفات غير المعروفة **أخطاء**.
- إذا كان Plugin مثبتًا لكن manifest أو schema الخاص به معطوبًا أو مفقودًا،
  يفشل التحقق ويبلّغ Doctor عن خطأ Plugin.
- إذا كانت إعدادات Plugin موجودة لكن Plugin **معطّل**، يتم الاحتفاظ بالإعدادات
  وتظهر **تحذير** في Doctor + السجلات.

راجع [مرجع الإعدادات](/ar/gateway/configuration) للاطلاع على مخطط `plugins.*` الكامل.

## ملاحظات

- إن الـ manifest **مطلوب للـ Plugins الأصلية في OpenClaw**، بما في ذلك التحميلات المحلية من نظام الملفات.
- ما يزال وقت التشغيل يحمّل وحدة Plugin بشكل منفصل؛ والـ manifest مخصّص فقط
  للاكتشاف + التحقق.
- يتم تحليل ملفات manifest الأصلية باستخدام JSON5، لذا تُقبل التعليقات والفواصل اللاحقة
  والمفاتيح غير المحاطة بعلامات اقتباس ما دامت القيمة النهائية لا تزال كائنًا.
- لا يقرأ محمّل manifest سوى حقول manifest الموثقة. تجنّب إضافة
  مفاتيح مخصّصة ذات مستوى أعلى هنا.
- يمثل `providerAuthEnvVars` مسار البيانات الوصفية منخفض الكلفة لفحوصات المصادقة، والتحقق من
  علامات البيئة، والأسطح المماثلة لمصادقة Provider التي ينبغي ألا تشغّل وقت تشغيل Plugin
  لمجرد فحص أسماء متغيرات البيئة.
- يتيح `providerAuthAliases` لمتغيرات Provider إعادة استخدام متغيرات بيئة المصادقة الخاصة بـ Provider آخر،
  وملفات تعريف المصادقة، والمصادقة المعتمدة على الإعدادات، وخيار التهيئة الأولية بمفتاح API
  من دون ترميز هذه العلاقة بشكل صريح داخل النواة.
- يمثل `channelEnvVars` مسار البيانات الوصفية منخفض الكلفة للرجوع إلى shell-env، وموجّهات الإعداد،
  والأسطح المماثلة الخاصة بالقنوات التي ينبغي ألا تشغّل وقت تشغيل Plugin
  لمجرد فحص أسماء متغيرات البيئة.
- يمثل `providerAuthChoices` مسار البيانات الوصفية منخفض الكلفة لمحددات خيارات المصادقة،
  وحل `--auth-choice`، وربط Provider المفضل، وتسجيل أعلام CLI البسيطة الخاصة بالتهيئة الأولية
  قبل تحميل وقت تشغيل Provider. أما بيانات تعريف المعالج التفاعلي في وقت التشغيل
  التي تتطلب كود Provider، فراجع
  [Provider runtime hooks](/ar/plugins/architecture#provider-runtime-hooks).
- يتم اختيار أنواع Plugin الحصرية عبر `plugins.slots.*`.
  - يتم اختيار `kind: "memory"` بواسطة `plugins.slots.memory`.
  - يتم اختيار `kind: "context-engine"` بواسطة `plugins.slots.contextEngine`
    (الافتراضي: `legacy` المدمج).
- يمكن حذف `channels` و`providers` و`cliBackends` و`skills` عندما لا
  يحتاجها Plugin.
- إذا كان Plugin الخاص بك يعتمد على وحدات أصلية، فوثّق خطوات البناء وأي
  متطلبات قائمة سماح لمدير الحزم (على سبيل المثال، `allow-build-scripts` في pnpm
  - `pnpm rebuild <package>`).

## ذو صلة

- [بناء Plugins](/ar/plugins/building-plugins) — بدء العمل مع Plugins
- [بنية Plugin](/ar/plugins/architecture) — البنية الداخلية
- [نظرة عامة على SDK](/ar/plugins/sdk-overview) — مرجع Plugin SDK
