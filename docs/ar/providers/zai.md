---
read_when:
    - تريد استخدام نماذج Z.AI / GLM في OpenClaw
    - تحتاج إلى إعداد بسيط لـ `ZAI_API_KEY`
summary: استخدم Z.AI ‏(نماذج GLM) مع OpenClaw
title: Z.AI
x-i18n:
    generated_at: "2026-04-12T23:33:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 972b467dab141c8c5126ac776b7cb6b21815c27da511b3f34e12bd9e9ac953b7
    source_path: providers/zai.md
    workflow: 15
---

# Z.AI

Z.AI هي منصة API لنماذج **GLM**. وهي توفّر واجهات REST API لـ GLM وتستخدم مفاتيح API
للمصادقة. أنشئ مفتاح API الخاص بك في وحدة تحكم Z.AI. يستخدم OpenClaw المزود `zai`
مع مفتاح API من Z.AI.

- المزود: `zai`
- المصادقة: `ZAI_API_KEY`
- API: Z.AI Chat Completions ‏(مصادقة Bearer)

## البدء

<Tabs>
  <Tab title="الاكتشاف التلقائي لنقطة النهاية">
    **الأفضل لـ:** معظم المستخدمين. يكتشف OpenClaw نقطة نهاية Z.AI المطابقة من المفتاح ويطبّق عنوان URL الأساسي الصحيح تلقائيًا.

    <Steps>
      <Step title="شغّل الإعداد الأولي">
        ```bash
        openclaw onboard --auth-choice zai-api-key
        ```
      </Step>
      <Step title="عيّن نموذجًا افتراضيًا">
        ```json5
        {
          env: { ZAI_API_KEY: "sk-..." },
          agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
        }
        ```
      </Step>
      <Step title="تحقق من توفر النموذج">
        ```bash
        openclaw models list --provider zai
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="نقطة نهاية إقليمية صريحة">
    **الأفضل لـ:** المستخدمين الذين يريدون فرض سطح Coding Plan أو سطح API العام المحدد.

    <Steps>
      <Step title="اختر خيار الإعداد الأولي الصحيح">
        ```bash
        # Coding Plan Global (recommended for Coding Plan users)
        openclaw onboard --auth-choice zai-coding-global

        # Coding Plan CN (China region)
        openclaw onboard --auth-choice zai-coding-cn

        # General API
        openclaw onboard --auth-choice zai-global

        # General API CN (China region)
        openclaw onboard --auth-choice zai-cn
        ```
      </Step>
      <Step title="عيّن نموذجًا افتراضيًا">
        ```json5
        {
          env: { ZAI_API_KEY: "sk-..." },
          agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
        }
        ```
      </Step>
      <Step title="تحقق من توفر النموذج">
        ```bash
        openclaw models list --provider zai
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## فهرس GLM المدمج

يقوم OpenClaw حاليًا بتهيئة المزود المدمج `zai` بما يلي:

| مرجع النموذج         | ملاحظات           |
| -------------------- | ----------------- |
| `zai/glm-5.1`        | النموذج الافتراضي |
| `zai/glm-5`          |                   |
| `zai/glm-5-turbo`    |                   |
| `zai/glm-5v-turbo`   |                   |
| `zai/glm-4.7`        |                   |
| `zai/glm-4.7-flash`  |                   |
| `zai/glm-4.7-flashx` |                   |
| `zai/glm-4.6`        |                   |
| `zai/glm-4.6v`       |                   |
| `zai/glm-4.5`        |                   |
| `zai/glm-4.5-air`    |                   |
| `zai/glm-4.5-flash`  |                   |
| `zai/glm-4.5v`       |                   |

<Tip>
تتوفر نماذج GLM بصيغة `zai/<model>` (مثال: `zai/glm-5`). مرجع النموذج المدمج الافتراضي هو `zai/glm-5.1`.
</Tip>

## إعدادات متقدمة

<AccordionGroup>
  <Accordion title="الحل الأمامي لمعرفات GLM-5 غير المعروفة">
    تظل معرّفات `glm-5*` غير المعروفة تُحل للأمام على مسار المزود المدمج عبر
    توليف بيانات وصفية مملوكة للمزود من قالب `glm-4.7` عندما يطابق المعرّف
    شكل عائلة GLM-5 الحالية.
  </Accordion>

  <Accordion title="بث استدعاءات الأدوات">
    يكون `tool_stream` مفعّلًا افتراضيًا لبث استدعاءات الأدوات في Z.AI. ولتعطيله:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "zai/<model>": {
              params: { tool_stream: false },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="فهم الصور">
    يقوم Plugin المدمج لـ Z.AI بتسجيل فهم الصور.

    | الخاصية | القيمة      |
    | -------- | ----------- |
    | النموذج  | `glm-4.6v`  |

    يتم حل فهم الصور تلقائيًا من مصادقة Z.AI المُعدة — ولا
    حاجة إلى إعدادات إضافية.

  </Accordion>

  <Accordion title="تفاصيل المصادقة">
    - تستخدم Z.AI مصادقة Bearer مع مفتاح API الخاص بك.
    - يقوم خيار الإعداد الأولي `zai-api-key` باكتشاف نقطة نهاية Z.AI المطابقة تلقائيًا من بادئة المفتاح.
    - استخدم الخيارات الإقليمية الصريحة (`zai-coding-global`، و`zai-coding-cn`، و`zai-global`، و`zai-cn`) عندما تريد فرض سطح API محدد.
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="عائلة نماذج GLM" href="/ar/providers/glm" icon="microchip">
    نظرة عامة على عائلة نماذج GLM.
  </Card>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزودات، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
</CardGroup>
