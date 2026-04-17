---
read_when:
    - تريد استخدام Together AI مع OpenClaw
    - تحتاج إلى متغير البيئة الخاص بمفتاح API أو خيار مصادقة CLI
summary: إعداد Together AI ‏(المصادقة + اختيار النموذج)
title: Together AI
x-i18n:
    generated_at: "2026-04-12T23:33:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 33531a1646443ac2e46ee1fbfbb60ec71093611b022618106e8e5435641680ac
    source_path: providers/together.md
    workflow: 15
---

# Together AI

توفّر [Together AI](https://together.ai) وصولًا إلى أبرز النماذج مفتوحة المصدر
بما في ذلك Llama وDeepSeek وKimi وغير ذلك من خلال API موحّدة.

| الخاصية | القيمة                        |
| -------- | ----------------------------- |
| Provider | `together`                    |
| المصادقة | `TOGETHER_API_KEY`            |
| API      | متوافق مع OpenAI              |
| عنوان URL الأساسي | `https://api.together.xyz/v1` |

## البدء

<Steps>
  <Step title="الحصول على مفتاح API">
    أنشئ مفتاح API من
    [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys).
  </Step>
  <Step title="تشغيل التهيئة الأولية">
    ```bash
    openclaw onboard --auth-choice together-api-key
    ```
  </Step>
  <Step title="تعيين نموذج افتراضي">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "together/moonshotai/Kimi-K2.5" },
        },
      },
    }
    ```
  </Step>
</Steps>

### مثال غير تفاعلي

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

<Note>
يضبط إعداد التهيئة الأولية المسبق النموذج `together/moonshotai/Kimi-K2.5` كنموذج
افتراضي.
</Note>

## الكتالوج المدمج

يوفّر OpenClaw كتالوج Together المدمج التالي:

| مرجع النموذج                                                | الاسم                                   | الإدخال      | السياق     | ملاحظات                           |
| ----------------------------------------------------------- | -------------------------------------- | ------------ | ---------- | --------------------------------- |
| `together/moonshotai/Kimi-K2.5`                             | Kimi K2.5                              | نص، صورة     | 262,144    | النموذج الافتراضي؛ الاستدلال مفعّل |
| `together/zai-org/GLM-4.7`                                  | GLM 4.7 Fp8                            | نص           | 202,752    | نموذج نصي عام                     |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`          | Llama 3.3 70B Instruct Turbo           | نص           | 131,072    | نموذج تعليمات سريع                |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct`        | Llama 4 Scout 17B 16E Instruct         | نص، صورة     | 10,000,000 | متعدد الوسائط                     |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8`| Llama 4 Maverick 17B 128E Instruct FP8 | نص، صورة     | 20,000,000 | متعدد الوسائط                     |
| `together/deepseek-ai/DeepSeek-V3.1`                        | DeepSeek V3.1                          | نص           | 131,072    | نموذج نصي عام                     |
| `together/deepseek-ai/DeepSeek-R1`                          | DeepSeek R1                            | نص           | 131,072    | نموذج استدلال                     |
| `together/moonshotai/Kimi-K2-Instruct-0905`                 | Kimi K2-Instruct 0905                  | نص           | 262,144    | نموذج Kimi نصي ثانوي              |

## توليد الفيديو

يسجّل Plugin المدمج `together` أيضًا توليد الفيديو عبر الأداة المشتركة
`video_generate`.

| الخاصية             | القيمة                                |
| ------------------- | ------------------------------------- |
| نموذج الفيديو الافتراضي | `together/Wan-AI/Wan2.2-T2V-A14B`     |
| الأوضاع             | نص إلى فيديو، ومرجع بصورة واحدة       |
| المعلمات المدعومة   | `aspectRatio` و`resolution`           |

لاستخدام Together كمزوّد الفيديو الافتراضي:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "together/Wan-AI/Wan2.2-T2V-A14B",
      },
    },
  },
}
```

<Tip>
راجع [توليد الفيديو](/ar/tools/video-generation) للاطلاع على معلمات الأداة المشتركة،
واختيار Provider، وسلوك التحويل الاحتياطي.
</Tip>

<AccordionGroup>
  <Accordion title="ملاحظة حول البيئة">
    إذا كان Gateway يعمل كخدمة daemon ‏(launchd/systemd)، فتأكد من أن
    `TOGETHER_API_KEY` متاح لتلك العملية (على سبيل المثال، في
    `~/.openclaw/.env` أو عبر `env.shellEnv`).

    <Warning>
    المفاتيح المضبوطة فقط في shell التفاعلية الخاصة بك لا تكون مرئية لعمليات
    gateway المُدارة بواسطة daemon. استخدم `~/.openclaw/.env` أو إعداد
    `env.shellEnv` لضمان التوفر الدائم.
    </Warning>

  </Accordion>

  <Accordion title="استكشاف الأخطاء وإصلاحها">
    - تحقّق من أن مفتاحك يعمل: `openclaw models list --provider together`
    - إذا لم تكن النماذج تظهر، فتأكد من ضبط مفتاح API في البيئة
      الصحيحة لعملية Gateway الخاصة بك.
    - تستخدم مراجع النماذج الصيغة `together/<model-id>`.
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="مزوّدو النماذج" href="/ar/concepts/model-providers" icon="layers">
    قواعد Provider، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="توليد الفيديو" href="/ar/tools/video-generation" icon="video">
    معلمات أداة توليد الفيديو المشتركة واختيار Provider.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference" icon="gear">
    مخطط الإعدادات الكامل بما في ذلك إعدادات Provider.
  </Card>
  <Card title="Together AI" href="https://together.ai" icon="arrow-up-right-from-square">
    لوحة تحكم Together AI ووثائق API والأسعار.
  </Card>
</CardGroup>
