---
read_when:
    - تريد استخدام Synthetic كمزوّد نماذج
    - تحتاج إلى إعداد مفتاح API أو عنوان URL أساسي لـ Synthetic
summary: استخدم API المتوافق مع Anthropic من Synthetic في OpenClaw
title: Synthetic
x-i18n:
    generated_at: "2026-04-12T23:32:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1c4d2c6635482e09acaf603a75c8a85f0782e42a4a68ef6166f423a48d184ffa
    source_path: providers/synthetic.md
    workflow: 15
---

# Synthetic

توفّر [Synthetic](https://synthetic.new) نقاط نهاية متوافقة مع Anthropic.
يسجّلها OpenClaw كمزوّد `synthetic` ويستخدم
Anthropic Messages API.

| الخاصية | القيمة                                 |
| -------- | ------------------------------------- |
| المزوّد | `synthetic`                           |
| المصادقة     | `SYNTHETIC_API_KEY`                   |
| API      | Anthropic Messages                    |
| عنوان URL الأساسي | `https://api.synthetic.new/anthropic` |

## البدء

<Steps>
  <Step title="احصل على مفتاح API">
    احصل على `SYNTHETIC_API_KEY` من حسابك في Synthetic، أو دع
    معالج الإعداد يطلبه منك.
  </Step>
  <Step title="شغّل الإعداد">
    ```bash
    openclaw onboard --auth-choice synthetic-api-key
    ```
  </Step>
  <Step title="تحقق من النموذج الافتراضي">
    بعد الإعداد، يتم تعيين النموذج الافتراضي إلى:
    ```
    synthetic/hf:MiniMaxAI/MiniMax-M2.5
    ```
  </Step>
</Steps>

<Warning>
يقوم عميل Anthropic في OpenClaw بإلحاق `/v1` بعنوان URL الأساسي تلقائيًا، لذا استخدم
`https://api.synthetic.new/anthropic` (وليس `/anthropic/v1`). وإذا غيّرت Synthetic
عنوان URL الأساسي الخاص بها، فتجاوز `models.providers.synthetic.baseUrl`.
</Warning>

## مثال على الإعداد

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

## كتالوج النماذج

تستخدم جميع نماذج Synthetic تكلفة مقدارها `0` (للإدخال/الإخراج/التخزين المؤقت).

| معرّف النموذج                                               | نافذة السياق | الحد الأقصى للرموز | الاستدلال | الإدخال        |
| ------------------------------------------------------ | -------------- | ---------- | --------- | ------------ |
| `hf:MiniMaxAI/MiniMax-M2.5`                            | 192,000        | 65,536     | لا        | نص         |
| `hf:moonshotai/Kimi-K2-Thinking`                       | 256,000        | 8,192      | نعم       | نص         |
| `hf:zai-org/GLM-4.7`                                   | 198,000        | 128,000    | لا        | نص         |
| `hf:deepseek-ai/DeepSeek-R1-0528`                      | 128,000        | 8,192      | لا        | نص         |
| `hf:deepseek-ai/DeepSeek-V3-0324`                      | 128,000        | 8,192      | لا        | نص         |
| `hf:deepseek-ai/DeepSeek-V3.1`                         | 128,000        | 8,192      | لا        | نص         |
| `hf:deepseek-ai/DeepSeek-V3.1-Terminus`                | 128,000        | 8,192      | لا        | نص         |
| `hf:deepseek-ai/DeepSeek-V3.2`                         | 159,000        | 8,192      | لا        | نص         |
| `hf:meta-llama/Llama-3.3-70B-Instruct`                 | 128,000        | 8,192      | لا        | نص         |
| `hf:meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | 524,000        | 8,192      | لا        | نص         |
| `hf:moonshotai/Kimi-K2-Instruct-0905`                  | 256,000        | 8,192      | لا        | نص         |
| `hf:moonshotai/Kimi-K2.5`                              | 256,000        | 8,192      | نعم       | نص + صورة |
| `hf:openai/gpt-oss-120b`                               | 128,000        | 8,192      | لا        | نص         |
| `hf:Qwen/Qwen3-235B-A22B-Instruct-2507`                | 256,000        | 8,192      | لا        | نص         |
| `hf:Qwen/Qwen3-Coder-480B-A35B-Instruct`               | 256,000        | 8,192      | لا        | نص         |
| `hf:Qwen/Qwen3-VL-235B-A22B-Instruct`                  | 250,000        | 8,192      | لا        | نص + صورة |
| `hf:zai-org/GLM-4.5`                                   | 128,000        | 128,000    | لا        | نص         |
| `hf:zai-org/GLM-4.6`                                   | 198,000        | 128,000    | لا        | نص         |
| `hf:zai-org/GLM-5`                                     | 256,000        | 128,000    | نعم       | نص + صورة |
| `hf:deepseek-ai/DeepSeek-V3`                           | 128,000        | 8,192      | لا        | نص         |
| `hf:Qwen/Qwen3-235B-A22B-Thinking-2507`                | 256,000        | 8,192      | نعم       | نص         |

<Tip>
تستخدم مراجع النماذج الصيغة `synthetic/<modelId>`. استخدم
`openclaw models list --provider synthetic` لرؤية جميع النماذج المتاحة على
حسابك.
</Tip>

<AccordionGroup>
  <Accordion title="قائمة سماح النماذج">
    إذا قمت بتمكين قائمة سماح للنماذج (`agents.defaults.models`)، فأضف كل
    نموذج Synthetic تخطط لاستخدامه. ستُخفى النماذج غير الموجودة في قائمة السماح
    عن الوكيل.
  </Accordion>

  <Accordion title="تجاوز عنوان URL الأساسي">
    إذا غيّرت Synthetic نقطة نهاية API الخاصة بها، فتجاوز عنوان URL الأساسي في إعدادك:

    ```json5
    {
      models: {
        providers: {
          synthetic: {
            baseUrl: "https://new-api.synthetic.new/anthropic",
          },
        },
      },
    }
    ```

    تذكّر أن OpenClaw يُلحق `/v1` تلقائيًا.

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="مزوّدو النماذج" href="/ar/concepts/model-providers" icon="layers">
    قواعد المزوّدين، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference" icon="gear">
    مخطط الإعداد الكامل بما في ذلك إعدادات المزوّد.
  </Card>
  <Card title="Synthetic" href="https://synthetic.new" icon="arrow-up-right-from-square">
    لوحة معلومات Synthetic ووثائق API.
  </Card>
</CardGroup>
