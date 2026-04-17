---
read_when:
    - تريد استخدام النماذج المفتوحة في OpenClaw مجانًا
    - تحتاج إلى إعداد `NVIDIA_API_KEY`
summary: استخدم API المتوافق مع OpenAI من NVIDIA في OpenClaw
title: NVIDIA
x-i18n:
    generated_at: "2026-04-12T23:31:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 45048037365138141ee82cefa0c0daaf073a1c2ae3aa7b23815f6ca676fc0d3e
    source_path: providers/nvidia.md
    workflow: 15
---

# NVIDIA

توفّر NVIDIA واجهة API متوافقة مع OpenAI على `https://integrate.api.nvidia.com/v1`
للنماذج المفتوحة مجانًا. قم بالمصادقة باستخدام مفتاح API من
[build.nvidia.com](https://build.nvidia.com/settings/api-keys).

## البدء

<Steps>
  <Step title="احصل على مفتاح API الخاص بك">
    أنشئ مفتاح API على [build.nvidia.com](https://build.nvidia.com/settings/api-keys).
  </Step>
  <Step title="صدّر المفتاح وشغّل الإعداد">
    ```bash
    export NVIDIA_API_KEY="nvapi-..."
    openclaw onboard --auth-choice skip
    ```
  </Step>
  <Step title="عيّن نموذج NVIDIA">
    ```bash
    openclaw models set nvidia/nvidia/nemotron-3-super-120b-a12b
    ```
  </Step>
</Steps>

<Warning>
إذا مرّرت `--token` بدلًا من متغير البيئة، فستظهر القيمة في سجل shell وفي
خرج `ps`. فضّل استخدام متغير البيئة `NVIDIA_API_KEY` كلما أمكن.
</Warning>

## مثال على الإعداد

```json5
{
  env: { NVIDIA_API_KEY: "nvapi-..." },
  models: {
    providers: {
      nvidia: {
        baseUrl: "https://integrate.api.nvidia.com/v1",
        api: "openai-completions",
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "nvidia/nvidia/nemotron-3-super-120b-a12b" },
    },
  },
}
```

## الكتالوج المضمّن

| مرجع النموذج                                  | الاسم                         | السياق | الحد الأقصى للإخراج |
| ------------------------------------------ | ---------------------------- | ------- | ---------- |
| `nvidia/nvidia/nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super 120B | 262,144 | 8,192      |
| `nvidia/moonshotai/kimi-k2.5`              | Kimi K2.5                    | 262,144 | 8,192      |
| `nvidia/minimaxai/minimax-m2.5`            | Minimax M2.5                 | 196,608 | 8,192      |
| `nvidia/z-ai/glm5`                         | GLM 5                        | 202,752 | 8,192      |

## ملاحظات متقدمة

<AccordionGroup>
  <Accordion title="سلوك التمكين التلقائي">
    يتم تمكين المزوّد تلقائيًا عند ضبط متغير البيئة `NVIDIA_API_KEY`.
    لا يلزم أي إعداد صريح إضافي للمزوّد بخلاف المفتاح.
  </Accordion>

  <Accordion title="الكتالوج والتسعير">
    الكتالوج المضمّن ثابت. وتكون التكاليف افتراضيًا `0` في المصدر لأن NVIDIA
    توفّر حاليًا وصول API مجانيًا للنماذج المدرجة.
  </Accordion>

  <Accordion title="نقطة نهاية متوافقة مع OpenAI">
    تستخدم NVIDIA نقطة النهاية القياسية للإكمالات `/v1`. ويجب أن تعمل أي أدوات
    متوافقة مع OpenAI مباشرةً مع عنوان NVIDIA الأساسي.
  </Accordion>
</AccordionGroup>

<Tip>
نماذج NVIDIA مجانية الاستخدام حاليًا. راجع
[build.nvidia.com](https://build.nvidia.com/) لمعرفة أحدث تفاصيل التوفر
وحدود المعدل.
</Tip>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدين ومراجع النماذج وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference" icon="gear">
    مرجع الإعداد الكامل للوكلاء والنماذج والمزوّدين.
  </Card>
</CardGroup>
