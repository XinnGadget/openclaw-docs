---
read_when:
    - تريد استخدام مسارات عمل ComfyUI المحلية مع OpenClaw
    - تريد استخدام Comfy Cloud مع مسارات عمل الصور أو الفيديو أو الموسيقى
    - تحتاج إلى مفاتيح إعداد Plugin `comfy` المضمّن
summary: إعداد توليد الصور والفيديو والموسيقى عبر مسارات عمل ComfyUI في OpenClaw
title: ComfyUI
x-i18n:
    generated_at: "2026-04-12T23:30:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 85db395b171f37f80b34b22f3e7707bffc1fd9138e7d10687eef13eaaa55cf24
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

يوفّر OpenClaw Plugin مضمّنًا باسم `comfy` لتشغيلات ComfyUI المعتمدة على مسارات العمل. هذا Plugin يعتمد بالكامل على مسارات العمل، لذلك لا يحاول OpenClaw إسقاط عناصر التحكم العامة مثل `size` أو `aspectRatio` أو `resolution` أو `durationSeconds` أو عناصر التحكم المشابهة لـ TTS على الرسم البياني الخاص بك.

| الخاصية        | التفاصيل                                                                           |
| --------------- | -------------------------------------------------------------------------------- |
| المزوّد        | `comfy`                                                                          |
| النماذج          | `comfy/workflow`                                                                 |
| الأسطح المشتركة | `image_generate`، `video_generate`، `music_generate`                             |
| المصادقة            | لا شيء لـ ComfyUI المحلي؛ `COMFY_API_KEY` أو `COMFY_CLOUD_API_KEY` لـ Comfy Cloud |
| API             | ‎`/prompt` / `/history` / `/view` في ComfyUI و`/api/*` في Comfy Cloud                |

## ما الذي يدعمه

- توليد الصور من ملف JSON لمسار عمل
- تحرير الصور باستخدام صورة مرجعية مرفوعة واحدة
- توليد الفيديو من ملف JSON لمسار عمل
- توليد الفيديو باستخدام صورة مرجعية مرفوعة واحدة
- توليد الموسيقى أو الصوت عبر الأداة المشتركة `music_generate`
- تنزيل المخرجات من عقدة مضبوطة أو من جميع عقد الإخراج المطابقة

## البدء

اختر بين تشغيل ComfyUI على جهازك أو استخدام Comfy Cloud.

<Tabs>
  <Tab title="محلي">
    **الأفضل لـ:** تشغيل نسخة ComfyUI الخاصة بك على جهازك أو على شبكة LAN.

    <Steps>
      <Step title="شغّل ComfyUI محليًا">
        تأكد من أن نسخة ComfyUI المحلية لديك قيد التشغيل (الافتراضي هو `http://127.0.0.1:8188`).
      </Step>
      <Step title="حضّر ملف JSON لمسار العمل">
        صدّر أو أنشئ ملف JSON لمسار عمل ComfyUI. دوّن معرّفات العقد لعقدة إدخال الموجّه وعقدة الإخراج التي تريد أن يقرأ OpenClaw منها.
      </Step>
      <Step title="اضبط المزوّد">
        اضبط `mode: "local"` ووجّه الإعداد إلى ملف مسار العمل. إليك مثالًا أدنى للصور:

        ```json5
        {
          models: {
            providers: {
              comfy: {
                mode: "local",
                baseUrl: "http://127.0.0.1:8188",
                image: {
                  workflowPath: "./workflows/flux-api.json",
                  promptNodeId: "6",
                  outputNodeId: "9",
                },
              },
            },
          },
        }
        ```
      </Step>
      <Step title="عيّن النموذج الافتراضي">
        وجّه OpenClaw إلى نموذج `comfy/workflow` للإمكانات التي قمت بإعدادها:

        ```json5
        {
          agents: {
            defaults: {
              imageGenerationModel: {
                primary: "comfy/workflow",
              },
            },
          },
        }
        ```
      </Step>
      <Step title="تحقق">
        ```bash
        openclaw models list --provider comfy
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Comfy Cloud">
    **الأفضل لـ:** تشغيل مسارات العمل على Comfy Cloud دون إدارة موارد GPU محلية.

    <Steps>
      <Step title="احصل على مفتاح API">
        سجّل في [comfy.org](https://comfy.org) وأنشئ مفتاح API من لوحة تحكم حسابك.
      </Step>
      <Step title="عيّن مفتاح API">
        قدّم المفتاح بإحدى الطرق التالية:

        ```bash
        # متغير بيئة (مفضّل)
        export COMFY_API_KEY="your-key"

        # متغير بيئة بديل
        export COMFY_CLOUD_API_KEY="your-key"

        # أو مباشرة داخل الإعداد
        openclaw config set models.providers.comfy.apiKey "your-key"
        ```
      </Step>
      <Step title="حضّر ملف JSON لمسار العمل">
        صدّر أو أنشئ ملف JSON لمسار عمل ComfyUI. دوّن معرّفات العقد لعقدة إدخال الموجّه وعقدة الإخراج.
      </Step>
      <Step title="اضبط المزوّد">
        اضبط `mode: "cloud"` ووجّه الإعداد إلى ملف مسار العمل:

        ```json5
        {
          models: {
            providers: {
              comfy: {
                mode: "cloud",
                image: {
                  workflowPath: "./workflows/flux-api.json",
                  promptNodeId: "6",
                  outputNodeId: "9",
                },
              },
            },
          },
        }
        ```

        <Tip>
        يستخدم وضع السحابة افتراضيًا `baseUrl` بالقيمة `https://cloud.comfy.org`. لا تحتاج إلى تعيين `baseUrl` إلا إذا كنت تستخدم نقطة نهاية سحابية مخصصة.
        </Tip>
      </Step>
      <Step title="عيّن النموذج الافتراضي">
        ```json5
        {
          agents: {
            defaults: {
              imageGenerationModel: {
                primary: "comfy/workflow",
              },
            },
          },
        }
        ```
      </Step>
      <Step title="تحقق">
        ```bash
        openclaw models list --provider comfy
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## الإعداد

يدعم Comfy إعدادات اتصال مشتركة على المستوى الأعلى بالإضافة إلى أقسام مسارات العمل لكل قدرة (`image` و`video` و`music`):

```json5
{
  models: {
    providers: {
      comfy: {
        mode: "local",
        baseUrl: "http://127.0.0.1:8188",
        image: {
          workflowPath: "./workflows/flux-api.json",
          promptNodeId: "6",
          outputNodeId: "9",
        },
        video: {
          workflowPath: "./workflows/video-api.json",
          promptNodeId: "12",
          outputNodeId: "21",
        },
        music: {
          workflowPath: "./workflows/music-api.json",
          promptNodeId: "3",
          outputNodeId: "18",
        },
      },
    },
  },
}
```

### المفاتيح المشتركة

| المفتاح                   | النوع                   | الوصف                                                                           |
| --------------------- | ---------------------- | ------------------------------------------------------------------------------------- |
| `mode`                | `"local"` أو `"cloud"` | وضع الاتصال.                                                                      |
| `baseUrl`             | string                 | القيمة الافتراضية هي `http://127.0.0.1:8188` للوضع المحلي أو `https://cloud.comfy.org` لوضع السحابة. |
| `apiKey`              | string                 | مفتاح اختياري مباشر داخل الإعداد، بديل عن متغيري البيئة `COMFY_API_KEY` / `COMFY_CLOUD_API_KEY`. |
| `allowPrivateNetwork` | boolean                | السماح بعنوان `baseUrl` خاص/محلي في وضع السحابة.                                          |

### المفاتيح لكل قدرة

تُطبّق هذه المفاتيح داخل أقسام `image` أو `video` أو `music`:

| المفتاح                          | مطلوب | الافتراضي  | الوصف                                                                  |
| ---------------------------- | -------- | -------- | ---------------------------------------------------------------------------- |
| `workflow` أو `workflowPath` | نعم      | --       | مسار ملف JSON لمسار عمل ComfyUI.                                      |
| `promptNodeId`               | نعم      | --       | معرّف العقدة التي تستقبل موجّه النص.                                       |
| `promptInputName`            | لا       | `"text"` | اسم الإدخال على عقدة الموجّه.                                               |
| `outputNodeId`               | لا       | --       | معرّف العقدة التي تُقرأ منها المخرجات. إذا تم حذفه، تُستخدم جميع عقد الإخراج المطابقة. |
| `pollIntervalMs`             | لا       | --       | فترة الاستطلاع بالمللي ثانية لاكتمال المهمة.                         |
| `timeoutMs`                  | لا       | --       | المهلة الزمنية بالمللي ثانية لتشغيل مسار العمل.                                |

يدعم قسمَا `image` و`video` أيضًا:

| المفتاح                   | مطلوب                             | الافتراضي   | الوصف                                         |
| --------------------- | ------------------------------------ | --------- | --------------------------------------------------- |
| `inputImageNodeId`    | نعم (عند تمرير صورة مرجعية) | --        | معرّف العقدة التي تستقبل الصورة المرجعية المرفوعة. |
| `inputImageInputName` | لا                                   | `"image"` | اسم الإدخال على عقدة الصورة.                       |

## تفاصيل مسار العمل

<AccordionGroup>
  <Accordion title="مسارات عمل الصور">
    عيّن نموذج الصور الافتراضي إلى `comfy/workflow`:

    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "comfy/workflow",
          },
        },
      },
    }
    ```

    **مثال على التحرير باستخدام صورة مرجعية:**

    لتمكين تحرير الصور باستخدام صورة مرجعية مرفوعة، أضف `inputImageNodeId` إلى إعداد الصور:

    ```json5
    {
      models: {
        providers: {
          comfy: {
            image: {
              workflowPath: "./workflows/edit-api.json",
              promptNodeId: "6",
              inputImageNodeId: "7",
              inputImageInputName: "image",
              outputNodeId: "9",
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="مسارات عمل الفيديو">
    عيّن نموذج الفيديو الافتراضي إلى `comfy/workflow`:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "comfy/workflow",
          },
        },
      },
    }
    ```

    تدعم مسارات عمل الفيديو في Comfy التحويل من نص إلى فيديو ومن صورة إلى فيديو عبر الرسم البياني المضبوط.

    <Note>
    لا يمرّر OpenClaw فيديوهات الإدخال إلى مسارات عمل Comfy. المدخلات المدعومة هي موجّهات النصوص والصور المرجعية المفردة فقط.
    </Note>

  </Accordion>

  <Accordion title="مسارات عمل الموسيقى">
    يسجل Plugin المضمّن مزوّدًا لتوليد الموسيقى لإخراجات الصوت أو الموسيقى المعرّفة عبر مسار العمل، وتظهر عبر الأداة المشتركة `music_generate`:

    ```text
    /tool music_generate prompt="Warm ambient synth loop with soft tape texture"
    ```

    استخدم قسم الإعداد `music` للإشارة إلى ملف JSON الخاص بمسار عمل الصوت وعقدة الإخراج.

  </Accordion>

  <Accordion title="التوافق مع الإصدارات السابقة">
    لا يزال إعداد الصور الموجود على المستوى الأعلى (من دون قسم `image` المتداخل) يعمل:

    ```json5
    {
      models: {
        providers: {
          comfy: {
            workflowPath: "./workflows/flux-api.json",
            promptNodeId: "6",
            outputNodeId: "9",
          },
        },
      },
    }
    ```

    يتعامل OpenClaw مع هذا الشكل القديم على أنه إعداد مسار عمل الصور. لا تحتاج إلى الترحيل فورًا، لكن أقسام `image` / `video` / `music` المتداخلة موصى بها للإعدادات الجديدة.

    <Tip>
    إذا كنت تستخدم توليد الصور فقط، فالإعداد المسطّح القديم والقسم المتداخل الجديد `image` متكافئان وظيفيًا.
    </Tip>

  </Accordion>

  <Accordion title="الاختبارات الحية">
    توجد تغطية حيّة اختيارية للPlugin المضمّن:

    ```bash
    OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
    ```

    يتخطى الاختبار الحي حالات الصور أو الفيديو أو الموسيقى الفردية ما لم يتم إعداد قسم Comfy المطابق لمسار العمل.

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="توليد الصور" href="/ar/tools/image-generation" icon="image">
    إعداد أداة توليد الصور واستخدامها.
  </Card>
  <Card title="توليد الفيديو" href="/ar/tools/video-generation" icon="video">
    إعداد أداة توليد الفيديو واستخدامها.
  </Card>
  <Card title="توليد الموسيقى" href="/ar/tools/music-generation" icon="music">
    إعداد توليد الموسيقى والصوت.
  </Card>
  <Card title="دليل المزوّدين" href="/ar/providers/index" icon="layers">
    نظرة عامة على جميع المزوّدين ومراجع النماذج.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference#agent-defaults" icon="gear">
    مرجع الإعداد الكامل بما في ذلك الإعدادات الافتراضية للوكيل.
  </Card>
</CardGroup>
