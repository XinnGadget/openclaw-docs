---
read_when:
    - تريد استخدام نماذج GLM في OpenClaw
    - تحتاج إلى اصطلاح تسمية النماذج والإعداد
summary: نظرة عامة على عائلة نماذج GLM + كيفية استخدامها في OpenClaw
title: GLM (Zhipu)
x-i18n:
    generated_at: "2026-04-12T23:30:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: b38f0896c900fae3cf3458ff99938d73fa46973a057d1dd373ae960cb7d2e9b5
    source_path: providers/glm.md
    workflow: 15
---

# نماذج GLM

GLM هي **عائلة نماذج** (وليست شركة) متاحة عبر منصة Z.AI. في OpenClaw، يتم الوصول إلى
نماذج GLM عبر المزود `zai` ومعرّفات النماذج مثل `zai/glm-5`.

## البدء

<Steps>
  <Step title="اختر مسار مصادقة وشغّل الإعداد الأولي">
    اختر خيار الإعداد الأولي الذي يطابق خطة Z.AI والمنطقة لديك:

    | خيار المصادقة | الأفضل لـ |
    | ----------- | -------- |
    | `zai-api-key` | إعداد عام بمفتاح API مع اكتشاف تلقائي لنقطة النهاية |
    | `zai-coding-global` | مستخدمي Coding Plan ‏(عالمي) |
    | `zai-coding-cn` | مستخدمي Coding Plan ‏(منطقة الصين) |
    | `zai-global` | API عام ‏(عالمي) |
    | `zai-cn` | API عام ‏(منطقة الصين) |

    ```bash
    # Example: generic auto-detect
    openclaw onboard --auth-choice zai-api-key

    # Example: Coding Plan global
    openclaw onboard --auth-choice zai-coding-global
    ```

  </Step>
  <Step title="عيّن GLM كنموذج افتراضي">
    ```bash
    openclaw config set agents.defaults.model.primary "zai/glm-5.1"
    ```
  </Step>
  <Step title="تحقق من توفر النماذج">
    ```bash
    openclaw models list --provider zai
    ```
  </Step>
</Steps>

## مثال على الإعداد

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

<Tip>
يتيح `zai-api-key` لـ OpenClaw اكتشاف نقطة نهاية Z.AI المطابقة من المفتاح
وتطبيق عنوان URL الأساسي الصحيح تلقائيًا. استخدم الخيارات الإقليمية الصريحة عندما
تريد فرض سطح Coding Plan أو سطح API العام المحدد.
</Tip>

## نماذج GLM المدمجة

يقوم OpenClaw حاليًا بتهيئة المزود المدمج `zai` بمراجع GLM التالية:

| النموذج        | النموذج           |
| -------------- | ----------------- |
| `glm-5.1`      | `glm-4.7`         |
| `glm-5`        | `glm-4.7-flash`   |
| `glm-5-turbo`  | `glm-4.7-flashx`  |
| `glm-5v-turbo` | `glm-4.6`         |
| `glm-4.5`      | `glm-4.6v`        |
| `glm-4.5-air`  |                   |
| `glm-4.5-flash` |                  |
| `glm-4.5v`     |                   |

<Note>
مرجع النموذج المدمج الافتراضي هو `zai/glm-5.1`. قد تتغير إصدارات GLM ومدى توفرها؛
تحقق من مستندات Z.AI للاطلاع على الأحدث.
</Note>

## ملاحظات متقدمة

<AccordionGroup>
  <Accordion title="الاكتشاف التلقائي لنقطة النهاية">
    عند استخدام خيار المصادقة `zai-api-key`، يفحص OpenClaw تنسيق المفتاح
    لتحديد عنوان URL الأساسي الصحيح لـ Z.AI. أما الخيارات الإقليمية الصريحة
    (`zai-coding-global`، و`zai-coding-cn`، و`zai-global`، و`zai-cn`) فتتجاوز
    الاكتشاف التلقائي وتثبّت نقطة النهاية مباشرة.
  </Accordion>

  <Accordion title="تفاصيل المزود">
    يتم تقديم نماذج GLM بواسطة مزود التشغيل `zai`. وللاطلاع على الإعداد الكامل للمزود،
    ونقاط النهاية الإقليمية، والإمكانات الإضافية، راجع
    [توثيق مزود Z.AI](/ar/providers/zai).
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="مزود Z.AI" href="/ar/providers/zai" icon="server">
    الإعداد الكامل لمزود Z.AI ونقاط النهاية الإقليمية.
  </Card>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزودات، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
</CardGroup>
