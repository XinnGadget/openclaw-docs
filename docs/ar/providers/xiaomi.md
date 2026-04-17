---
read_when:
    - تريد نماذج Xiaomi MiMo في OpenClaw
    - تحتاج إلى إعداد `XIAOMI_API_KEY`
summary: استخدام نماذج Xiaomi MiMo مع OpenClaw
title: Xiaomi MiMo
x-i18n:
    generated_at: "2026-04-12T23:33:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: cd5a526764c796da7e1fff61301bc2ec618e1cf3857894ba2ef4b6dd9c4dc339
    source_path: providers/xiaomi.md
    workflow: 15
---

# Xiaomi MiMo

Xiaomi MiMo هي منصة API لنماذج **MiMo**. يستخدم OpenClaw
نقطة نهاية Xiaomi المتوافقة مع OpenAI مع مصادقة مفتاح API.

| الخاصية | القيمة                          |
| ------- | ------------------------------- |
| الموفّر | `xiaomi`                        |
| المصادقة | `XIAOMI_API_KEY`               |
| API     | متوافق مع OpenAI               |
| Base URL | `https://api.xiaomimimo.com/v1` |

## البدء

<Steps>
  <Step title="الحصول على مفتاح API">
    أنشئ مفتاح API في [لوحة Xiaomi MiMo](https://platform.xiaomimimo.com/#/console/api-keys).
  </Step>
  <Step title="تشغيل التهيئة">
    ```bash
    openclaw onboard --auth-choice xiaomi-api-key
    ```

    أو مرّر المفتاح مباشرةً:

    ```bash
    openclaw onboard --auth-choice xiaomi-api-key --xiaomi-api-key "$XIAOMI_API_KEY"
    ```

  </Step>
  <Step title="التحقق من توفر النموذج">
    ```bash
    openclaw models list --provider xiaomi
    ```
  </Step>
</Steps>

## النماذج المتاحة

| مرجع النموذج          | الإدخال      | السياق    | الحد الأقصى للمخرجات | الاستدلال | ملاحظات         |
| --------------------- | ------------ | --------- | -------------------- | --------- | --------------- |
| `xiaomi/mimo-v2-flash` | text        | 262,144   | 8,192                | لا        | النموذج الافتراضي |
| `xiaomi/mimo-v2-pro`   | text        | 1,048,576 | 32,000               | نعم       | سياق كبير       |
| `xiaomi/mimo-v2-omni`  | text, image | 262,144   | 32,000               | نعم       | متعدد الوسائط   |

<Tip>
مرجع النموذج الافتراضي هو `xiaomi/mimo-v2-flash`. يُحقن الموفّر تلقائيًا عند ضبط `XIAOMI_API_KEY` أو عند وجود ملف تعريف للمصادقة.
</Tip>

## مثال على الإعداد

```json5
{
  env: { XIAOMI_API_KEY: "your-key" },
  agents: { defaults: { model: { primary: "xiaomi/mimo-v2-flash" } } },
  models: {
    mode: "merge",
    providers: {
      xiaomi: {
        baseUrl: "https://api.xiaomimimo.com/v1",
        api: "openai-completions",
        apiKey: "XIAOMI_API_KEY",
        models: [
          {
            id: "mimo-v2-flash",
            name: "Xiaomi MiMo V2 Flash",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 8192,
          },
          {
            id: "mimo-v2-pro",
            name: "Xiaomi MiMo V2 Pro",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 1048576,
            maxTokens: 32000,
          },
          {
            id: "mimo-v2-omni",
            name: "Xiaomi MiMo V2 Omni",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="سلوك الحقن التلقائي">
    يُحقن الموفّر `xiaomi` تلقائيًا عند ضبط `XIAOMI_API_KEY` في بيئتك أو عند وجود ملف تعريف للمصادقة. لا تحتاج إلى إعداد الموفّر يدويًا إلا إذا أردت تجاوز البيانات الوصفية للنموذج أو Base URL.
  </Accordion>

  <Accordion title="تفاصيل النموذج">
    - **mimo-v2-flash** — خفيف وسريع، ومثالي للمهام النصية العامة. لا يدعم الاستدلال.
    - **mimo-v2-pro** — يدعم الاستدلال مع نافذة سياق بحجم 1M رمز لأحمال العمل الخاصة بالمستندات الطويلة.
    - **mimo-v2-omni** — نموذج متعدد الوسائط مع دعم للاستدلال ويقبل كلًا من النصوص والصور.

    <Note>
    تستخدم جميع النماذج البادئة `xiaomi/` (على سبيل المثال `xiaomi/mimo-v2-pro`).
    </Note>

  </Accordion>

  <Accordion title="استكشاف الأخطاء وإصلاحها">
    - إذا لم تظهر النماذج، فتأكد من أن `XIAOMI_API_KEY` مضبوط وصالح.
    - عندما تعمل Gateway كعملية daemon، فتأكد من أن المفتاح متاح لتلك العملية (على سبيل المثال في `~/.openclaw/.env` أو عبر `env.shellEnv`).

    <Warning>
    المفاتيح المضبوطة فقط في الصدفة التفاعلية لديك لا تكون مرئية لعمليات gateway المُدارة عبر daemon. استخدم `~/.openclaw/.env` أو إعداد `env.shellEnv` لضمان التوفر الدائم.
    </Warning>

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار الموفّرين، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="مرجع الإعداد" href="/ar/gateway/configuration" icon="gear">
    المرجع الكامل لإعداد OpenClaw.
  </Card>
  <Card title="لوحة Xiaomi MiMo" href="https://platform.xiaomimimo.com" icon="arrow-up-right-from-square">
    لوحة Xiaomi MiMo وإدارة مفاتيح API.
  </Card>
</CardGroup>
