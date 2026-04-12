---
read_when:
    - تريد استخدام Qwen مع OpenClaw
    - كنت تستخدم Qwen OAuth سابقًا
summary: استخدم Qwen Cloud عبر مزوّد qwen المضمّن في OpenClaw
title: Qwen
x-i18n:
    generated_at: "2026-04-12T23:32:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5247f851ef891645df6572d748ea15deeea47cd1d75858bc0d044a2930065106
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**تمت إزالة Qwen OAuth.** لم يعد تكامل OAuth ذي المستوى المجاني
(`qwen-portal`) الذي كان يستخدم نقاط نهاية `portal.qwen.ai` متاحًا.
راجع [Issue #49557](https://github.com/openclaw/openclaw/issues/49557) للاطلاع
على الخلفية.

</Warning>

يتعامل OpenClaw الآن مع Qwen باعتباره مزوّدًا مضمّنًا من الدرجة الأولى
بالمعرّف القياسي `qwen`. ويستهدف المزوّد المضمّن نقاط نهاية Qwen Cloud /
Alibaba DashScope وCoding Plan، مع إبقاء معرّفات `modelstudio` القديمة تعمل
كاسم مستعار للتوافق.

- المزوّد: `qwen`
- متغير env المفضّل: `QWEN_API_KEY`
- مقبول أيضًا للتوافق: `MODELSTUDIO_API_KEY` و`DASHSCOPE_API_KEY`
- نمط API: متوافق مع OpenAI

<Tip>
إذا كنت تريد `qwen3.6-plus`، فافضّل نقطة نهاية **Standard (الدفع حسب الاستخدام)**.
قد يتأخر دعم Coding Plan عن الفهرس العام.
</Tip>

## البدء

اختر نوع خطتك واتبع خطوات الإعداد.

<Tabs>
  <Tab title="Coding Plan (اشتراك)">
    **الأفضل لـ:** الوصول القائم على الاشتراك عبر Qwen Coding Plan.

    <Steps>
      <Step title="احصل على مفتاح API الخاص بك">
        أنشئ أو انسخ مفتاح API من [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys).
      </Step>
      <Step title="شغّل الإعداد الأولي">
        لنقطة النهاية **العالمية**:

        ```bash
        openclaw onboard --auth-choice qwen-api-key
        ```

        ولنقطة النهاية **الصينية**:

        ```bash
        openclaw onboard --auth-choice qwen-api-key-cn
        ```
      </Step>
      <Step title="اضبط نموذجًا افتراضيًا">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="تحقق من توفر النموذج">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    لا تزال معرّفات `auth-choice` القديمة من نوع `modelstudio-*` ومراجع النماذج `modelstudio/...`
    تعمل كأسماء مستعارة للتوافق، لكن تدفقات الإعداد الجديدة يجب أن تفضّل
    معرّفات `auth-choice` القياسية `qwen-*` ومراجع النماذج `qwen/...`.
    </Note>

  </Tab>

  <Tab title="Standard (الدفع حسب الاستخدام)">
    **الأفضل لـ:** الوصول بنظام الدفع حسب الاستخدام عبر نقطة نهاية Model Studio القياسية، بما في ذلك نماذج مثل `qwen3.6-plus` التي قد لا تكون متاحة في Coding Plan.

    <Steps>
      <Step title="احصل على مفتاح API الخاص بك">
        أنشئ أو انسخ مفتاح API من [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys).
      </Step>
      <Step title="شغّل الإعداد الأولي">
        لنقطة النهاية **العالمية**:

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key
        ```

        ولنقطة النهاية **الصينية**:

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key-cn
        ```
      </Step>
      <Step title="اضبط نموذجًا افتراضيًا">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="تحقق من توفر النموذج">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    لا تزال معرّفات `auth-choice` القديمة من نوع `modelstudio-*` ومراجع النماذج `modelstudio/...`
    تعمل كأسماء مستعارة للتوافق، لكن تدفقات الإعداد الجديدة يجب أن تفضّل
    معرّفات `auth-choice` القياسية `qwen-*` ومراجع النماذج `qwen/...`.
    </Note>

  </Tab>
</Tabs>

## أنواع الخطط ونقاط النهاية

| الخطة                      | المنطقة | Auth choice                | نقطة النهاية                                      |
| -------------------------- | ------- | -------------------------- | ------------------------------------------------- |
| Standard (الدفع حسب الاستخدام) | الصين   | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1`      |
| Standard (الدفع حسب الاستخدام) | عالمي   | `qwen-standard-api-key`    | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (اشتراك)       | الصين   | `qwen-api-key-cn`          | `coding.dashscope.aliyuncs.com/v1`               |
| Coding Plan (اشتراك)       | عالمي   | `qwen-api-key`             | `coding-intl.dashscope.aliyuncs.com/v1`          |

يختار المزوّد نقطة النهاية تلقائيًا بناءً على `auth choice` الخاص بك. وتستخدم
الخيارات القياسية عائلة `qwen-*`؛ بينما تبقى `modelstudio-*` للتوافق فقط.
يمكنك التجاوز باستخدام `baseUrl` مخصص في الإعداد.

<Tip>
**إدارة المفاتيح:** [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys) |
**المستندات:** [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)
</Tip>

## الفهرس المضمّن

يشحن OpenClaw حاليًا فهرس Qwen المضمّن التالي. ويكون الفهرس المُعدّ
مدركًا لنقطة النهاية: إذ تحذف إعدادات Coding Plan النماذج التي لا يُعرف
أنها تعمل إلا على نقطة النهاية Standard.

| مرجع النموذج                | الإدخال      | السياق    | ملاحظات                                              |
| -------------------------- | ------------ | --------- | ---------------------------------------------------- |
| `qwen/qwen3.5-plus`        | نص، صورة     | 1,000,000 | النموذج الافتراضي                                    |
| `qwen/qwen3.6-plus`        | نص، صورة     | 1,000,000 | فضّل نقاط النهاية Standard عندما تحتاج إلى هذا النموذج |
| `qwen/qwen3-max-2026-01-23` | نص          | 262,144   | سلسلة Qwen Max                                      |
| `qwen/qwen3-coder-next`    | نص           | 262,144   | ترميز                                               |
| `qwen/qwen3-coder-plus`    | نص           | 1,000,000 | ترميز                                               |
| `qwen/MiniMax-M2.5`        | نص           | 1,000,000 | الاستدلال مفعّل                                      |
| `qwen/glm-5`               | نص           | 202,752   | GLM                                                 |
| `qwen/glm-4.7`             | نص           | 202,752   | GLM                                                 |
| `qwen/kimi-k2.5`           | نص، صورة     | 262,144   | Moonshot AI عبر Alibaba                             |

<Note>
قد يظل التوفر مختلفًا بحسب نقطة النهاية وخطة الفوترة حتى عندما يكون النموذج
موجودًا في الفهرس المضمّن.
</Note>

## الإضافات متعددة الوسائط

يعرض امتداد `qwen` أيضًا قدرات متعددة الوسائط على نقاط نهاية DashScope **Standard**
(وليس على نقاط نهاية Coding Plan):

- **فهم الفيديو** عبر `qwen-vl-max-latest`
- **إنشاء الفيديو Wan** عبر `wan2.6-t2v` (الافتراضي)، و`wan2.6-i2v`، و`wan2.6-r2v`، و`wan2.6-r2v-flash`، و`wan2.7-r2v`

لاستخدام Qwen كمزوّد الفيديو الافتراضي:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

<Note>
راجع [إنشاء الفيديو](/ar/tools/video-generation) للاطلاع على معلمات الأداة المشتركة، واختيار المزوّد، وسلوك التبديل الاحتياطي.
</Note>

## خيارات متقدمة

<AccordionGroup>
  <Accordion title="فهم الصور والفيديو">
    يسجّل Plugin Qwen المضمّن إمكانات فهم الوسائط للصور والفيديو
    على نقاط نهاية DashScope **Standard** (وليس على نقاط نهاية Coding Plan).

    | الخاصية        | القيمة                |
    | -------------- | --------------------- |
    | النموذج        | `qwen-vl-max-latest`  |
    | الإدخال المدعوم | الصور، الفيديو        |

    يتم حل فهم الوسائط تلقائيًا من مصادقة Qwen المُعدّة — ولا
    يلزم أي إعداد إضافي. تأكد من أنك تستخدم نقطة نهاية Standard (الدفع حسب الاستخدام)
    لدعم فهم الوسائط.

  </Accordion>

  <Accordion title="توفر Qwen 3.6 Plus">
    يتوفر `qwen3.6-plus` على نقاط نهاية Model Studio من نوع Standard (الدفع حسب الاستخدام):

    - الصين: `dashscope.aliyuncs.com/compatible-mode/v1`
    - عالمي: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

    إذا أعادت نقاط نهاية Coding Plan خطأ "unsupported model" للنموذج
    `qwen3.6-plus`، فانتقل إلى Standard (الدفع حسب الاستخدام) بدلًا من زوج
    نقطة النهاية/المفتاح الخاص بـ Coding Plan.

  </Accordion>

  <Accordion title="خطة القدرات">
    يجري وضع امتداد `qwen` باعتباره الموطن المزوّد الكامل لواجهة Qwen
    Cloud، وليس فقط لنماذج الترميز/النص.

    - **نماذج النص/الدردشة:** مضمّنة الآن
    - **استدعاء الأدوات، والمخرجات المنظمة، والتفكير:** موروثة من النقل المتوافق مع OpenAI
    - **إنشاء الصور:** مخطط له على مستوى Plugin المزوّد
    - **فهم الصور/الفيديو:** مضمّن الآن على نقطة النهاية Standard
    - **الكلام/الصوت:** مخطط له على مستوى Plugin المزوّد
    - **تضمينات/إعادة ترتيب الذاكرة:** مخطط لها عبر واجهة محول التضمين
    - **إنشاء الفيديو:** مضمّن الآن عبر قدرة إنشاء الفيديو المشتركة

  </Accordion>

  <Accordion title="تفاصيل إنشاء الفيديو">
    بالنسبة إلى إنشاء الفيديو، يربط OpenClaw منطقة Qwen المُعدّة بمضيف
    DashScope AIGC المطابق قبل إرسال المهمة:

    - عالمي/دولي: `https://dashscope-intl.aliyuncs.com`
    - الصين: `https://dashscope.aliyuncs.com`

    وهذا يعني أن `models.providers.qwen.baseUrl` العادي الذي يشير إلى أحد مضيفي
    Qwen من نوع Coding Plan أو Standard سيُبقي إنشاء الفيديو على نقطة نهاية
    الفيديو الإقليمية الصحيحة في DashScope.

    الحدود الحالية لإنشاء الفيديو في Qwen المضمّن:

    - حتى **1** فيديو ناتج لكل طلب
    - حتى **1** صورة إدخال
    - حتى **4** فيديوهات إدخال
    - مدة تصل إلى **10 ثوانٍ**
    - يدعم `size` و`aspectRatio` و`resolution` و`audio` و`watermark`
    - يتطلب وضع الصورة/الفيديو المرجعي حاليًا **عناوين URL بعيدة من نوع http(s)**. ويتم
      رفض مسارات الملفات المحلية مسبقًا لأن نقطة نهاية فيديو DashScope لا
      تقبل الذاكرات المؤقتة المحلية المرفوعة لهذه المراجع.

  </Accordion>

  <Accordion title="توافق استخدام البث">
    تعلن نقاط نهاية Model Studio الأصلية عن توافق استخدام البث على
    النقل المشترك `openai-completions`. ويربط OpenClaw ذلك الآن بقدرات
    نقطة النهاية، لذلك ترث معرّفات المزوّدين المخصصين المتوافقة مع DashScope التي تستهدف
    المضيفين الأصليين أنفسهم سلوك استخدام البث ذاته بدلًا من
    اشتراط معرّف المزوّد المضمّن `qwen` تحديدًا.

    ينطبق توافق استخدام البث الأصلي على كل من مضيفي Coding Plan
    والمضيفين المتوافقين مع DashScope من نوع Standard:

    - `https://coding.dashscope.aliyuncs.com/v1`
    - `https://coding-intl.dashscope.aliyuncs.com/v1`
    - `https://dashscope.aliyuncs.com/compatible-mode/v1`
    - `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="مناطق نقاط النهاية متعددة الوسائط">
    تستخدم الأسطح متعددة الوسائط (فهم الفيديو وإنشاء فيديو Wan) نقاط نهاية
    DashScope **Standard**، وليس نقاط نهاية Coding Plan:

    - عنوان URL الأساسي لـ Standard العالمي/الدولي: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
    - عنوان URL الأساسي لـ Standard في الصين: `https://dashscope.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="إعداد البيئة والخدمة">
    إذا كان Gateway يعمل كخدمة (launchd/systemd)، فتأكد من أن `QWEN_API_KEY`
    متاح لتلك العملية (على سبيل المثال، في `~/.openclaw/.env` أو عبر
    `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدين، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="إنشاء الفيديو" href="/ar/tools/video-generation" icon="video">
    معلمات أداة الفيديو المشتركة واختيار المزوّد.
  </Card>
  <Card title="Alibaba (ModelStudio)" href="/ar/providers/alibaba" icon="cloud">
    مزوّد ModelStudio القديم وملاحظات الترحيل.
  </Card>
  <Card title="استكشاف الأخطاء وإصلاحها" href="/ar/help/troubleshooting" icon="wrench">
    استكشاف الأخطاء وإصلاحها العام والأسئلة الشائعة.
  </Card>
</CardGroup>
