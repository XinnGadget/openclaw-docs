---
read_when:
    - تريد نماذج MiniMax في OpenClaw
    - تحتاج إلى إرشادات إعداد MiniMax
summary: استخدم نماذج MiniMax في OpenClaw
title: MiniMax
x-i18n:
    generated_at: "2026-04-12T23:31:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: ee9c89faf57384feb66cda30934000e5746996f24b59122db309318f42c22389
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

الإعداد الافتراضي لمزوّد MiniMax في OpenClaw هو **MiniMax M2.7**.

كما يوفّر MiniMax أيضًا:

- توليد الكلام المدمج عبر T2A v2
- فهم الصور المدمج عبر `MiniMax-VL-01`
- توليد الموسيقى المدمج عبر `music-2.5+`
- `web_search` مدمجًا عبر MiniMax Coding Plan search API

تقسيم المزوّد:

| معرّف المزوّد     | المصادقة | القدرات                                                       |
| ----------------- | -------- | ------------------------------------------------------------- |
| `minimax`         | مفتاح API | النص، وتوليد الصور، وفهم الصور، والكلام، والبحث على الويب     |
| `minimax-portal`  | OAuth    | النص، وتوليد الصور، وفهم الصور                                |

## تشكيلة النماذج

| النموذج                   | النوع            | الوصف                                       |
| ------------------------- | ---------------- | ------------------------------------------- |
| `MiniMax-M2.7`            | دردشة (استدلال)  | نموذج الاستدلال المستضاف الافتراضي          |
| `MiniMax-M2.7-highspeed`  | دردشة (استدلال)  | طبقة استدلال M2.7 الأسرع                    |
| `MiniMax-VL-01`           | رؤية             | نموذج فهم الصور                              |
| `image-01`                | توليد الصور      | تحويل النص إلى صورة وتحرير صورة إلى صورة     |
| `music-2.5+`              | توليد الموسيقى   | نموذج الموسيقى الافتراضي                     |
| `music-2.5`               | توليد الموسيقى   | طبقة توليد الموسيقى السابقة                  |
| `music-2.0`               | توليد الموسيقى   | طبقة توليد الموسيقى القديمة                  |
| `MiniMax-Hailuo-2.3`      | توليد الفيديو    | مسارات النص إلى فيديو ومرجع الصورة           |

## البدء

اختر طريقة المصادقة المفضلة لديك واتبع خطوات الإعداد.

<Tabs>
  <Tab title="OAuth (Coding Plan)">
    **الأفضل من أجل:** إعداد سريع مع MiniMax Coding Plan عبر OAuth، من دون الحاجة إلى مفتاح API.

    <Tabs>
      <Tab title="دولي">
        <Steps>
          <Step title="تشغيل التهيئة الأولية">
            ```bash
            openclaw onboard --auth-choice minimax-global-oauth
            ```

            يؤدي هذا إلى المصادقة مع `api.minimax.io`.
          </Step>
          <Step title="التحقق من توفر النموذج">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="الصين">
        <Steps>
          <Step title="تشغيل التهيئة الأولية">
            ```bash
            openclaw onboard --auth-choice minimax-cn-oauth
            ```

            يؤدي هذا إلى المصادقة مع `api.minimaxi.com`.
          </Step>
          <Step title="التحقق من توفر النموذج">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    <Note>
    تستخدم إعدادات OAuth معرّف المزوّد `minimax-portal`. وتتبع مراجع النماذج الصيغة `minimax-portal/MiniMax-M2.7`.
    </Note>

    <Tip>
    رابط إحالة لـ MiniMax Coding Plan ‏(خصم 10%): [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
    </Tip>

  </Tab>

  <Tab title="مفتاح API">
    **الأفضل من أجل:** MiniMax المستضاف مع API متوافق مع Anthropic.

    <Tabs>
      <Tab title="دولي">
        <Steps>
          <Step title="تشغيل التهيئة الأولية">
            ```bash
            openclaw onboard --auth-choice minimax-global-api
            ```

            يؤدي هذا إلى ضبط `api.minimax.io` كعنوان URL أساسي.
          </Step>
          <Step title="التحقق من توفر النموذج">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="الصين">
        <Steps>
          <Step title="تشغيل التهيئة الأولية">
            ```bash
            openclaw onboard --auth-choice minimax-cn-api
            ```

            يؤدي هذا إلى ضبط `api.minimaxi.com` كعنوان URL أساسي.
          </Step>
          <Step title="التحقق من توفر النموذج">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    ### مثال إعداد

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "minimax/MiniMax-M2.7" } } },
      models: {
        mode: "merge",
        providers: {
          minimax: {
            baseUrl: "https://api.minimax.io/anthropic",
            apiKey: "${MINIMAX_API_KEY}",
            api: "anthropic-messages",
            models: [
              {
                id: "MiniMax-M2.7",
                name: "MiniMax M2.7",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
                contextWindow: 204800,
                maxTokens: 131072,
              },
              {
                id: "MiniMax-M2.7-highspeed",
                name: "MiniMax M2.7 Highspeed",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0.6, output: 2.4, cacheRead: 0.06, cacheWrite: 0.375 },
                contextWindow: 204800,
                maxTokens: 131072,
              },
            ],
          },
        },
      },
    }
    ```

    <Warning>
    في مسار البث المتوافق مع Anthropic، يعطّل OpenClaw التفكير في MiniMax افتراضيًا ما لم تضبط `thinking` بنفسك صراحةً. تصدر نقطة نهاية البث في MiniMax قيمة `reasoning_content` في أجزاء delta بنمط OpenAI بدلًا من كتل التفكير الأصلية الخاصة بـ Anthropic، ما قد يسرّب الاستدلال الداخلي إلى المخرجات المرئية إذا تُرك مفعّلًا ضمنيًا.
    </Warning>

    <Note>
    تستخدم إعدادات مفتاح API معرّف المزوّد `minimax`. وتتبع مراجع النماذج الصيغة `minimax/MiniMax-M2.7`.
    </Note>

  </Tab>
</Tabs>

## الإعداد عبر `openclaw configure`

استخدم معالج الإعدادات التفاعلي لضبط MiniMax من دون تحرير JSON:

<Steps>
  <Step title="تشغيل المعالج">
    ```bash
    openclaw configure
    ```
  </Step>
  <Step title="تحديد النموذج/المصادقة">
    اختر **النموذج/المصادقة** من القائمة.
  </Step>
  <Step title="اختيار أحد خيارات مصادقة MiniMax">
    اختر أحد خيارات MiniMax المتاحة:

    | خيار المصادقة | الوصف |
    | --- | --- |
    | `minimax-global-oauth` | OAuth دولي (Coding Plan) |
    | `minimax-cn-oauth` | OAuth الصين (Coding Plan) |
    | `minimax-global-api` | مفتاح API دولي |
    | `minimax-cn-api` | مفتاح API الصين |

  </Step>
  <Step title="اختيار النموذج الافتراضي">
    حدّد النموذج الافتراضي عند مطالبتك بذلك.
  </Step>
</Steps>

## القدرات

### توليد الصور

يسجّل Plugin الخاص بـ MiniMax النموذج `image-01` لأداة `image_generate`. وهو يدعم:

- **توليد الصور من النص** مع التحكم في نسبة الأبعاد
- **تحرير صورة إلى صورة** (مرجع الموضوع) مع التحكم في نسبة الأبعاد
- حتى **9 صور ناتجة** لكل طلب
- حتى **صورة مرجعية واحدة** لكل طلب تحرير
- نسب الأبعاد المدعومة: `1:1` و`16:9` و`4:3` و`3:2` و`2:3` و`3:4` و`9:16` و`21:9`

لاستخدام MiniMax في توليد الصور، اضبطه كمزوّد توليد الصور:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "minimax/image-01" },
    },
  },
}
```

يستخدم Plugin نفس مصادقة `MINIMAX_API_KEY` أو OAuth المستخدمة مع النماذج النصية. ولا يلزم أي إعداد إضافي إذا كان MiniMax معدًا بالفعل.

يسجّل كل من `minimax` و`minimax-portal` أداة `image_generate` باستخدام النموذج نفسه
`image-01`. تستخدم إعدادات مفتاح API القيمة `MINIMAX_API_KEY`؛ ويمكن لإعدادات OAuth استخدام
مسار المصادقة المدمج `minimax-portal` بدلًا من ذلك.

عندما تكتب التهيئة الأولية أو إعداد مفتاح API إدخالات صريحة في `models.providers.minimax`،
يقوم OpenClaw بتهيئة `MiniMax-M2.7` و
`MiniMax-M2.7-highspeed` مع `input: ["text", "image"]`.

أما كتالوج النصوص MiniMax المدمج نفسه فيبقى بيانات تعريف خاصة بالنص فقط إلى أن
يوجد إعداد مزوّد صريح. ويتم عرض فهم الصور بشكل منفصل
من خلال مزوّد الوسائط `MiniMax-VL-01` الذي يملكه Plugin.

<Note>
راجع [توليد الصور](/ar/tools/image-generation) للاطلاع على معلمات الأداة المشتركة، واختيار Provider، وسلوك التحويل الاحتياطي.
</Note>

### توليد الموسيقى

يسجّل Plugin المدمج `minimax` أيضًا توليد الموسيقى عبر الأداة المشتركة
`music_generate`.

- نموذج الموسيقى الافتراضي: `minimax/music-2.5+`
- يدعم أيضًا `minimax/music-2.5` و`minimax/music-2.0`
- عناصر التحكم في الموجّه: `lyrics` و`instrumental` و`durationSeconds`
- تنسيق الإخراج: `mp3`
- تفصل عمليات التشغيل المدعومة بالجلسة عبر مسار المهمة/الحالة المشترك، بما في ذلك `action: "status"`

لاستخدام MiniMax كمزوّد الموسيقى الافتراضي:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "minimax/music-2.5+",
      },
    },
  },
}
```

<Note>
راجع [توليد الموسيقى](/ar/tools/music-generation) للاطلاع على معلمات الأداة المشتركة، واختيار Provider، وسلوك التحويل الاحتياطي.
</Note>

### توليد الفيديو

يسجّل Plugin المدمج `minimax` أيضًا توليد الفيديو عبر الأداة المشتركة
`video_generate`.

- نموذج الفيديو الافتراضي: `minimax/MiniMax-Hailuo-2.3`
- الأوضاع: نص إلى فيديو ومسارات مرجع بصورة واحدة
- يدعم `aspectRatio` و`resolution`

لاستخدام MiniMax كمزوّد الفيديو الافتراضي:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "minimax/MiniMax-Hailuo-2.3",
      },
    },
  },
}
```

<Note>
راجع [توليد الفيديو](/ar/tools/video-generation) للاطلاع على معلمات الأداة المشتركة، واختيار Provider، وسلوك التحويل الاحتياطي.
</Note>

### فهم الصور

يسجّل Plugin الخاص بـ MiniMax فهم الصور بشكل منفصل عن
كتالوج النصوص:

| معرّف Provider     | نموذج الصور الافتراضي |
| ------------------ | --------------------- |
| `minimax`          | `MiniMax-VL-01`       |
| `minimax-portal`   | `MiniMax-VL-01`       |

ولهذا السبب يمكن للتوجيه التلقائي للوسائط استخدام فهم الصور في MiniMax حتى
عندما يستمر كتالوج موفّر النصوص المدمج في إظهار مراجع دردشة M2.7 النصية فقط.

### البحث على الويب

يسجّل Plugin الخاص بـ MiniMax أيضًا `web_search` عبر MiniMax Coding Plan
search API.

- معرّف المزوّد: `minimax`
- نتائج منظمة: عناوين، وعناوين URL، ومقتطفات، واستعلامات ذات صلة
- متغير البيئة المفضل: `MINIMAX_CODE_PLAN_KEY`
- الاسم البديل المقبول للبيئة: `MINIMAX_CODING_API_KEY`
- خيار التوافق الاحتياطي: `MINIMAX_API_KEY` عندما يكون يشير بالفعل إلى رمز coding-plan
- إعادة استخدام المنطقة: `plugins.entries.minimax.config.webSearch.region`، ثم `MINIMAX_API_HOST`، ثم عناوين URL الأساسية لمزوّد MiniMax
- يبقى البحث على معرّف المزوّد `minimax`؛ وما تزال إعدادات OAuth الصينية/الدولية قادرة على توجيه المنطقة بشكل غير مباشر عبر `models.providers.minimax-portal.baseUrl`

توجد الإعدادات تحت `plugins.entries.minimax.config.webSearch.*`.

<Note>
راجع [بحث MiniMax](/ar/tools/minimax-search) للاطلاع على إعدادات البحث على الويب الكاملة وطريقة الاستخدام.
</Note>

## الإعدادات المتقدمة

<AccordionGroup>
  <Accordion title="خيارات الإعدادات">
    | الخيار | الوصف |
    | --- | --- |
    | `models.providers.minimax.baseUrl` | فضّل `https://api.minimax.io/anthropic` ‏(متوافق مع Anthropic)؛ ويُعد `https://api.minimax.io/v1` اختياريًا لحمولات متوافقة مع OpenAI |
    | `models.providers.minimax.api` | فضّل `anthropic-messages`؛ ويُعد `openai-completions` اختياريًا لحمولات متوافقة مع OpenAI |
    | `models.providers.minimax.apiKey` | مفتاح API لـ MiniMax ‏(`MINIMAX_API_KEY`) |
    | `models.providers.minimax.models` | عرّف `id` و`name` و`reasoning` و`contextWindow` و`maxTokens` و`cost` |
    | `agents.defaults.models` | أعطِ أسماء بديلة للنماذج التي تريدها في allowlist |
    | `models.mode` | أبقه `merge` إذا كنت تريد إضافة MiniMax إلى جانب المزوّدات المدمجة |
  </Accordion>

  <Accordion title="إعدادات التفكير الافتراضية">
    عند `api: "anthropic-messages"`، يحقن OpenClaw القيمة `thinking: { type: "disabled" }` ما لم يكن التفكير مضبوطًا بالفعل صراحةً في المعلمات/الإعدادات.

    يمنع ذلك نقطة نهاية البث في MiniMax من إصدار `reasoning_content` على شكل أجزاء delta بنمط OpenAI، وهو ما قد يسرّب الاستدلال الداخلي إلى المخرجات المرئية.

  </Accordion>

  <Accordion title="الوضع السريع">
    يقوم `/fast on` أو `params.fastMode: true` بإعادة كتابة `MiniMax-M2.7` إلى `MiniMax-M2.7-highspeed` على مسار البث المتوافق مع Anthropic.
  </Accordion>

  <Accordion title="مثال على التحويل الاحتياطي">
    **الأفضل من أجل:** إبقاء أقوى نموذج حديث الجيل لديك كنموذج أساسي، مع التحويل الاحتياطي إلى MiniMax M2.7. يستخدم المثال أدناه Opus كنموذج أساسي ملموس؛ استبدله بالنموذج الأساسي الحديث المفضل لديك.

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-..." },
      agents: {
        defaults: {
          models: {
            "anthropic/claude-opus-4-6": { alias: "primary" },
            "minimax/MiniMax-M2.7": { alias: "minimax" },
          },
          model: {
            primary: "anthropic/claude-opus-4-6",
            fallbacks: ["minimax/MiniMax-M2.7"],
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="تفاصيل استخدام Coding Plan">
    - واجهة استخدام Coding Plan API: ‏`https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains` ‏(تتطلب مفتاح coding plan).
    - يطبّع OpenClaw استخدام MiniMax coding-plan إلى عرض `% المتبقي` نفسه المستخدم لدى المزوّدين الآخرين. إن الحقول الخام `usage_percent` / `usagePercent` في MiniMax تمثل الحصة المتبقية، وليس الحصة المستهلكة، لذا يعكسها OpenClaw. وتكون الحقول المعتمدة على العدد هي الأرجح عند وجودها.
    - عندما تعيد API القيمة `model_remains`، يفضّل OpenClaw إدخال نموذج الدردشة، ويشتق تسمية النافذة من `start_time` / `end_time` عند الحاجة، ويضمّن اسم النموذج المحدد في تسمية الخطة لتسهيل التمييز بين نوافذ coding-plan.
    - تتعامل لقطات الاستخدام مع `minimax` و`minimax-cn` و`minimax-portal` على أنها سطح حصة MiniMax نفسه، وتفضّل MiniMax OAuth المخزن قبل الرجوع إلى متغيرات بيئة مفتاح Coding Plan.
  </Accordion>
</AccordionGroup>

## ملاحظات

- تتبع مراجع النماذج مسار المصادقة:
  - إعداد مفتاح API: ‏`minimax/<model>`
  - إعداد OAuth: ‏`minimax-portal/<model>`
- نموذج الدردشة الافتراضي: `MiniMax-M2.7`
- نموذج الدردشة البديل: `MiniMax-M2.7-highspeed`
- تكتب التهيئة الأولية وإعداد مفتاح API المباشر تعريفات نماذج صريحة مع `input: ["text", "image"]` لكلا متغيري M2.7
- يعرض كتالوج المزوّد المدمج حاليًا مراجع الدردشة كبيانات تعريف نصية فقط إلى أن يوجد إعداد MiniMax صريح للمزوّد
- حدّث قيم الأسعار في `models.json` إذا كنت تحتاج إلى تتبّع دقيق للتكلفة
- استخدم `openclaw models list` لتأكيد معرّف المزوّد الحالي، ثم بدّل باستخدام `openclaw models set minimax/MiniMax-M2.7` أو `openclaw models set minimax-portal/MiniMax-M2.7`

<Tip>
رابط إحالة لـ MiniMax Coding Plan ‏(خصم 10%): [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
</Tip>

<Note>
راجع [مزوّدو النماذج](/ar/concepts/model-providers) للاطلاع على قواعد المزوّد.
</Note>

## استكشاف الأخطاء وإصلاحها

<AccordionGroup>
  <Accordion title='"نموذج غير معروف: minimax/MiniMax-M2.7"'>
    يعني هذا عادةً أن **مزوّد MiniMax غير مُعدّ** (لا يوجد إدخال مزوّد مطابق ولا ملف تعريف مصادقة/مفتاح بيئة لـ MiniMax تم العثور عليه). يوجد إصلاح لهذا الاكتشاف في **2026.1.12**. أصلح ذلك عبر:

    - الترقية إلى **2026.1.12** (أو التشغيل من المصدر `main`)، ثم إعادة تشغيل Gateway.
    - تشغيل `openclaw configure` واختيار أحد خيارات مصادقة **MiniMax**، أو
    - إضافة كتلة `models.providers.minimax` أو `models.providers.minimax-portal` المطابقة يدويًا، أو
    - ضبط `MINIMAX_API_KEY` أو `MINIMAX_OAUTH_TOKEN` أو ملف تعريف مصادقة MiniMax بحيث يمكن حقن المزوّد المطابق.

    تأكد من أن معرّف النموذج **حساس لحالة الأحرف**:

    - مسار مفتاح API: ‏`minimax/MiniMax-M2.7` أو `minimax/MiniMax-M2.7-highspeed`
    - مسار OAuth: ‏`minimax-portal/MiniMax-M2.7` أو `minimax-portal/MiniMax-M2.7-highspeed`

    ثم أعد التحقق باستخدام:

    ```bash
    openclaw models list
    ```

  </Accordion>
</AccordionGroup>

<Note>
مساعدة إضافية: [استكشاف الأخطاء وإصلاحها](/ar/help/troubleshooting) و[الأسئلة الشائعة](/ar/help/faq).
</Note>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدين، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="توليد الصور" href="/ar/tools/image-generation" icon="image">
    معلمات أداة الصور المشتركة واختيار Provider.
  </Card>
  <Card title="توليد الموسيقى" href="/ar/tools/music-generation" icon="music">
    معلمات أداة الموسيقى المشتركة واختيار Provider.
  </Card>
  <Card title="توليد الفيديو" href="/ar/tools/video-generation" icon="video">
    معلمات أداة الفيديو المشتركة واختيار Provider.
  </Card>
  <Card title="بحث MiniMax" href="/ar/tools/minimax-search" icon="magnifying-glass">
    إعداد البحث على الويب عبر MiniMax Coding Plan.
  </Card>
  <Card title="استكشاف الأخطاء وإصلاحها" href="/ar/help/troubleshooting" icon="wrench">
    استكشاف الأخطاء العامة وإصلاحها والأسئلة الشائعة.
  </Card>
</CardGroup>
