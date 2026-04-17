---
read_when:
    - تريد استخدام نماذج StepFun في OpenClaw
    - تحتاج إلى إرشادات إعداد StepFun
summary: استخدم نماذج StepFun مع OpenClaw
title: StepFun
x-i18n:
    generated_at: "2026-04-12T23:32:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: a463bed0951d33802dcdb3a7784406272ee206b731e9864ea020323e67b4d159
    source_path: providers/stepfun.md
    workflow: 15
---

# StepFun

يتضمن OpenClaw Plugin مزود StepFun مدمجًا مع معرّفي مزود:

- `stepfun` لنقطة النهاية القياسية
- `stepfun-plan` لنقطة نهاية Step Plan

<Warning>
إن Standard وStep Plan **مزودان منفصلان** مع نقاط نهاية مختلفة وبوادئ مراجع نماذج مختلفة (`stepfun/...` مقابل `stepfun-plan/...`). استخدم مفتاح China مع نقاط النهاية `.com` ومفتاحًا عالميًا مع نقاط النهاية `.ai`.
</Warning>

## نظرة عامة على المنطقة ونقطة النهاية

| نقطة النهاية | China (`.com`)                         | عالمي (`.ai`)                        |
| ------------ | -------------------------------------- | ------------------------------------ |
| Standard     | `https://api.stepfun.com/v1`           | `https://api.stepfun.ai/v1`          |
| Step Plan    | `https://api.stepfun.com/step_plan/v1` | `https://api.stepfun.ai/step_plan/v1` |

متغير بيئة المصادقة: `STEPFUN_API_KEY`

## الفهارس المدمجة

Standard (`stepfun`):

| مرجع النموذج             | السياق  | الحد الأقصى للإخراج | ملاحظات                  |
| ------------------------ | ------- | ------------------- | ------------------------ |
| `stepfun/step-3.5-flash` | 262,144 | 65,536              | النموذج القياسي الافتراضي |

Step Plan (`stepfun-plan`):

| مرجع النموذج                       | السياق  | الحد الأقصى للإخراج | ملاحظات                    |
| ---------------------------------- | ------- | ------------------- | -------------------------- |
| `stepfun-plan/step-3.5-flash`      | 262,144 | 65,536              | نموذج Step Plan الافتراضي  |
| `stepfun-plan/step-3.5-flash-2603` | 262,144 | 65,536              | نموذج Step Plan إضافي      |

## البدء

اختر واجهة المزود واتبع خطوات الإعداد.

<Tabs>
  <Tab title="Standard">
    **الأفضل لـ:** الاستخدام العام عبر نقطة النهاية القياسية لـ StepFun.

    <Steps>
      <Step title="اختر منطقة نقطة النهاية">
        | خيار المصادقة                     | نقطة النهاية                      | المنطقة         |
        | --------------------------------- | --------------------------------- | ---------------- |
        | `stepfun-standard-api-key-intl`   | `https://api.stepfun.ai/v1`       | دولي             |
        | `stepfun-standard-api-key-cn`     | `https://api.stepfun.com/v1`      | الصين            |
      </Step>
      <Step title="شغّل الإعداد الأولي">
        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-intl
        ```

        أو لنقطة نهاية الصين:

        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-cn
        ```
      </Step>
      <Step title="بديل غير تفاعلي">
        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-intl \
          --stepfun-api-key "$STEPFUN_API_KEY"
        ```
      </Step>
      <Step title="تحقق من توفر النماذج">
        ```bash
        openclaw models list --provider stepfun
        ```
      </Step>
    </Steps>

    ### مراجع النماذج

    - النموذج الافتراضي: `stepfun/step-3.5-flash`

  </Tab>

  <Tab title="Step Plan">
    **الأفضل لـ:** نقطة نهاية الاستدلال Step Plan.

    <Steps>
      <Step title="اختر منطقة نقطة النهاية">
        | خيار المصادقة                 | نقطة النهاية                            | المنطقة         |
        | ----------------------------- | --------------------------------------- | ---------------- |
        | `stepfun-plan-api-key-intl`   | `https://api.stepfun.ai/step_plan/v1`   | دولي             |
        | `stepfun-plan-api-key-cn`     | `https://api.stepfun.com/step_plan/v1`  | الصين            |
      </Step>
      <Step title="شغّل الإعداد الأولي">
        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-intl
        ```

        أو لنقطة نهاية الصين:

        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-cn
        ```
      </Step>
      <Step title="بديل غير تفاعلي">
        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-intl \
          --stepfun-api-key "$STEPFUN_API_KEY"
        ```
      </Step>
      <Step title="تحقق من توفر النماذج">
        ```bash
        openclaw models list --provider stepfun-plan
        ```
      </Step>
    </Steps>

    ### مراجع النماذج

    - النموذج الافتراضي: `stepfun-plan/step-3.5-flash`
    - النموذج البديل: `stepfun-plan/step-3.5-flash-2603`

  </Tab>
</Tabs>

## متقدم

<AccordionGroup>
  <Accordion title="الإعداد الكامل: مزود Standard">
    ```json5
    {
      env: { STEPFUN_API_KEY: "your-key" },
      agents: { defaults: { model: { primary: "stepfun/step-3.5-flash" } } },
      models: {
        mode: "merge",
        providers: {
          stepfun: {
            baseUrl: "https://api.stepfun.ai/v1",
            api: "openai-completions",
            apiKey: "${STEPFUN_API_KEY}",
            models: [
              {
                id: "step-3.5-flash",
                name: "Step 3.5 Flash",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="الإعداد الكامل: مزود Step Plan">
    ```json5
    {
      env: { STEPFUN_API_KEY: "your-key" },
      agents: { defaults: { model: { primary: "stepfun-plan/step-3.5-flash" } } },
      models: {
        mode: "merge",
        providers: {
          "stepfun-plan": {
            baseUrl: "https://api.stepfun.ai/step_plan/v1",
            api: "openai-completions",
            apiKey: "${STEPFUN_API_KEY}",
            models: [
              {
                id: "step-3.5-flash",
                name: "Step 3.5 Flash",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
              {
                id: "step-3.5-flash-2603",
                name: "Step 3.5 Flash 2603",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="ملاحظات">
    - المزود مدمج مع OpenClaw، لذلك لا توجد خطوة منفصلة لتثبيت Plugin.
    - `step-3.5-flash-2603` متاح حاليًا فقط على `stepfun-plan`.
    - يكتب تدفق مصادقة واحد ملفات تعريف مطابقة للمنطقة لكلٍّ من `stepfun` و`stepfun-plan`، لذا يمكن اكتشاف كلا الواجهتين معًا.
    - استخدم `openclaw models list` و`openclaw models set <provider/model>` لفحص النماذج أو تبديلها.
  </Accordion>
</AccordionGroup>

<Note>
للاطلاع على النظرة العامة الأوسع للمزودات، راجع [مزودات النماذج](/ar/concepts/model-providers).
</Note>

## ذو صلة

<CardGroup cols={2}>
  <Card title="مزودات النماذج" href="/ar/concepts/model-providers" icon="layers">
    نظرة عامة على جميع المزودات، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference" icon="gear">
    المخطط الكامل لإعدادات المزودات والنماذج وPlugin.
  </Card>
  <Card title="اختيار النموذج" href="/ar/concepts/models" icon="brain">
    كيفية اختيار النماذج وإعدادها.
  </Card>
  <Card title="منصة StepFun" href="https://platform.stepfun.com" icon="globe">
    إدارة مفاتيح StepFun API والوثائق.
  </Card>
</CardGroup>
