---
read_when:
    - تريد استخدام نماذج Grok في OpenClaw
    - أنت تقوم بإعداد مصادقة xAI أو معرّفات النماذج
summary: استخدم نماذج xAI Grok في OpenClaw
title: xAI
x-i18n:
    generated_at: "2026-04-12T23:33:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 820fef290c67d9815e41a96909d567216f67ca0f01df1d325008fd04666ad255
    source_path: providers/xai.md
    workflow: 15
---

# xAI

يشحن OpenClaw Plugin مزوّد `xai` مضمّنًا لنماذج Grok.

## البدء

<Steps>
  <Step title="أنشئ مفتاح API">
    أنشئ مفتاح API في [وحدة تحكم xAI](https://console.x.ai/).
  </Step>
  <Step title="اضبط مفتاح API الخاص بك">
    اضبط `XAI_API_KEY`، أو شغّل:

    ```bash
    openclaw onboard --auth-choice xai-api-key
    ```

  </Step>
  <Step title="اختر نموذجًا">
    ```json5
    {
      agents: { defaults: { model: { primary: "xai/grok-4" } } },
    }
    ```
  </Step>
</Steps>

<Note>
يستخدم OpenClaw واجهة xAI Responses API كوسيلة النقل المضمّنة لـ xAI. ويمكن أن
يُستخدم `XAI_API_KEY` نفسه أيضًا لتشغيل `web_search` المعتمد على Grok، و`x_search`
من الدرجة الأولى، و`code_execution` البعيد.
إذا خزّنت مفتاح xAI ضمن `plugins.entries.xai.config.webSearch.apiKey`،
فإن مزوّد نماذج xAI المضمّن يعيد استخدام ذلك المفتاح كخيار احتياطي أيضًا.
وتوجد إعدادات ضبط `code_execution` تحت `plugins.entries.xai.config.codeExecution`.
</Note>

## فهرس النماذج المضمّن

يتضمن OpenClaw عائلات نماذج xAI التالية بشكل افتراضي:

| العائلة        | معرّفات النماذج                                                           |
| -------------- | ------------------------------------------------------------------------- |
| Grok 3         | `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`               |
| Grok 4         | `grok-4`, `grok-4-0709`                                                   |
| Grok 4 Fast    | `grok-4-fast`, `grok-4-fast-non-reasoning`                                |
| Grok 4.1 Fast  | `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`                            |
| Grok 4.20 Beta | `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning` |
| Grok Code      | `grok-code-fast-1`                                                        |

ويقوم Plugin أيضًا بحلّ معرّفات `grok-4*` و`grok-code-fast*` الأحدث بشكل تمريري عندما
تتبع شكل API نفسه.

<Tip>
تُعد `grok-4-fast` و`grok-4-1-fast` ومتغيرات `grok-4.20-beta-*`
مراجع Grok الحالية القادرة على معالجة الصور في الفهرس المضمّن.
</Tip>

### تعيينات الوضع السريع

يعيد `/fast on` أو `agents.defaults.models["xai/<model>"].params.fastMode: true`
كتابة طلبات xAI الأصلية كما يلي:

| النموذج المصدر | هدف الوضع السريع   |
| ------------- | ------------------ |
| `grok-3`      | `grok-3-fast`      |
| `grok-3-mini` | `grok-3-mini-fast` |
| `grok-4`      | `grok-4-fast`      |
| `grok-4-0709` | `grok-4-fast`      |

### الأسماء المستعارة القديمة للتوافق

لا تزال الأسماء المستعارة القديمة تُطبّع إلى المعرّفات القياسية المضمّنة:

| الاسم المستعار القديم      | المعرّف القياسي                        |
| ------------------------- | ------------------------------------- |
| `grok-4-fast-reasoning`   | `grok-4-fast`                         |
| `grok-4-1-fast-reasoning` | `grok-4-1-fast`                       |
| `grok-4.20-reasoning`     | `grok-4.20-beta-latest-reasoning`     |
| `grok-4.20-non-reasoning` | `grok-4.20-beta-latest-non-reasoning` |

## الميزات

<AccordionGroup>
  <Accordion title="البحث على الويب">
    يستخدم مزوّد البحث على الويب المضمّن `grok` أيضًا المفتاح `XAI_API_KEY`:

    ```bash
    openclaw config set tools.web.search.provider grok
    ```

  </Accordion>

  <Accordion title="إنشاء الفيديو">
    يسجّل Plugin `xai` المضمّن إنشاء الفيديو عبر
    الأداة المشتركة `video_generate`.

    - نموذج الفيديو الافتراضي: `xai/grok-imagine-video`
    - الأوضاع: تحويل النص إلى فيديو، وتحويل الصورة إلى فيديو، وتدفقات تعديل/تمديد الفيديو البعيدة
    - يدعم `aspectRatio` و`resolution`

    <Warning>
    لا تُقبل الذاكرات المؤقتة المحلية للفيديو. استخدم عناوين URL بعيدة من نوع `http(s)` لمدخلات
    مرجع الفيديو والتعديل.
    </Warning>

    لاستخدام xAI كمزوّد الفيديو الافتراضي:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "xai/grok-imagine-video",
          },
        },
      },
    }
    ```

    <Note>
    راجع [إنشاء الفيديو](/ar/tools/video-generation) للاطلاع على معلمات الأداة المشتركة،
    واختيار المزوّد، وسلوك التبديل الاحتياطي.
    </Note>

  </Accordion>

  <Accordion title="إعداد x_search">
    يعرّض Plugin xAI المضمّن `x_search` كأداة OpenClaw للبحث في
    محتوى X (المعروف سابقًا باسم Twitter) عبر Grok.

    مسار الإعداد: `plugins.entries.xai.config.xSearch`

    | المفتاح            | النوع   | الافتراضي         | الوصف                             |
    | ------------------ | ------- | ----------------- | --------------------------------- |
    | `enabled`          | boolean | —                 | تفعيل أو تعطيل x_search           |
    | `model`            | string  | `grok-4-1-fast`   | النموذج المستخدم لطلبات x_search  |
    | `inlineCitations`  | boolean | —                 | تضمين استشهادات مضمنة في النتائج  |
    | `maxTurns`         | number  | —                 | الحد الأقصى لأدوار المحادثة       |
    | `timeoutSeconds`   | number  | —                 | مهلة الطلب بالثواني               |
    | `cacheTtlMinutes`  | number  | —                 | مدة صلاحية التخزين المؤقت بالدقائق |

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              xSearch: {
                enabled: true,
                model: "grok-4-1-fast",
                inlineCitations: true,
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="إعداد code_execution">
    يعرّض Plugin xAI المضمّن `code_execution` كأداة OpenClaw من أجل
    تنفيذ التعليمات البرمجية عن بُعد في بيئة sandbox الخاصة بـ xAI.

    مسار الإعداد: `plugins.entries.xai.config.codeExecution`

    | المفتاح           | النوع   | الافتراضي                 | الوصف                                  |
    | ----------------- | ------- | ------------------------- | -------------------------------------- |
    | `enabled`         | boolean | `true` (إذا كان المفتاح متاحًا) | تفعيل أو تعطيل تنفيذ التعليمات البرمجية |
    | `model`           | string  | `grok-4-1-fast`           | النموذج المستخدم لطلبات تنفيذ التعليمات البرمجية |
    | `maxTurns`        | number  | —                         | الحد الأقصى لأدوار المحادثة            |
    | `timeoutSeconds`  | number  | —                         | مهلة الطلب بالثواني                    |

    <Note>
    هذا تنفيذ بعيد داخل sandbox الخاص بـ xAI، وليس [`exec`](/ar/tools/exec) محليًا.
    </Note>

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              codeExecution: {
                enabled: true,
                model: "grok-4-1-fast",
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="القيود المعروفة">
    - المصادقة اليوم تعتمد فقط على مفتاح API. ولا يوجد حتى الآن تدفق xAI OAuth أو device-code في
      OpenClaw.
    - لا يتم دعم `grok-4.20-multi-agent-experimental-beta-0304` على
      المسار العادي لمزوّد xAI لأنه يتطلب سطح API مختلفًا في المنبع
      عن وسيلة النقل القياسية لـ xAI في OpenClaw.
  </Accordion>

  <Accordion title="ملاحظات متقدمة">
    - يطبّق OpenClaw إصلاحات توافق خاصة بـ xAI لمخطط الأدوات واستدعاءات الأدوات
      تلقائيًا على مسار المشغّل المشترك.
    - تستخدم طلبات xAI الأصلية القيمة الافتراضية `tool_stream: true`. اضبط
      `agents.defaults.models["xai/<model>"].params.tool_stream` إلى `false` من أجل
      تعطيله.
    - يزيل الغلاف المضمّن لـ xAI علامات مخطط الأدوات الصارمة غير المدعومة ومفاتيح
      حمولة الاستدلال قبل إرسال طلبات xAI الأصلية.
    - يتم عرض `web_search` و`x_search` و`code_execution` كأدوات
      OpenClaw. ويفعّل OpenClaw العنصر المضمّن المحدد من xAI الذي يحتاجه داخل كل طلب
      أداة بدلًا من إرفاق جميع الأدوات الأصلية بكل دور دردشة.
    - يملك Plugin xAI المضمّن كلًا من `x_search` و`code_execution` بدلًا
      من ترميزهما مباشرة داخل وقت تشغيل النموذج الأساسي.
    - `code_execution` هو تنفيذ بعيد داخل sandbox الخاص بـ xAI، وليس
      [`exec`](/ar/tools/exec) محليًا.
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
  <Card title="جميع المزوّدين" href="/ar/providers/index" icon="grid-2">
    النظرة العامة الأوسع على المزوّدين.
  </Card>
  <Card title="استكشاف الأخطاء وإصلاحها" href="/ar/help/troubleshooting" icon="wrench">
    المشكلات الشائعة والحلول.
  </Card>
</CardGroup>
