---
read_when:
    - تريد استدلالًا يركز على الخصوصية في OpenClaw
    - تريد إرشادات إعداد Venice AI
summary: استخدم نماذج Venice AI التي تركز على الخصوصية في OpenClaw
title: Venice AI
x-i18n:
    generated_at: "2026-04-12T23:33:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6f8005edb1d7781316ce8b5432bf4f9375c16113594a2a588912dce82234a9e5
    source_path: providers/venice.md
    workflow: 15
---

# Venice AI

توفّر Venice AI **استدلال ذكاء اصطناعي يركز على الخصوصية** مع دعم للنماذج غير
المقيّدة والوصول إلى النماذج الاحتكارية الكبرى عبر الوكيل المجهول الخاص بها.
جميع عمليات الاستدلال خاصة افتراضيًا — لا تدريب على بياناتك، ولا تسجيل.

## لماذا Venice في OpenClaw

- **استدلال خاص** للنماذج مفتوحة المصدر (من دون تسجيل).
- **نماذج غير مقيّدة** عندما تحتاج إليها.
- **وصول مجهول** إلى النماذج الاحتكارية (Opus/GPT/Gemini) عندما تكون الجودة مهمة.
- نقاط نهاية `/v1` متوافقة مع OpenAI.

## أوضاع الخصوصية

توفّر Venice مستويين من الخصوصية — وفهم هذا أمر أساسي لاختيار النموذج المناسب:

| الوضع            | الوصف                                                                                                                       | النماذج                                                       |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Private**      | خاص بالكامل. لا يتم **أبدًا** تخزين المطالبات/الاستجابات أو تسجيلها. مؤقت.                                                  | Llama وQwen وDeepSeek وKimi وMiniMax وVenice Uncensored وغيرها. |
| **Anonymized**   | يُمرَّر عبر Venice مع إزالة البيانات الوصفية. يرى الموفّر الأساسي (OpenAI أو Anthropic أو Google أو xAI) طلبات مجهولة الهوية. | Claude وGPT وGemini وGrok                                      |

<Warning>
النماذج المجهولة **ليست** خاصة بالكامل. تقوم Venice بإزالة البيانات الوصفية قبل
إعادة التوجيه، لكن الموفّر الأساسي (OpenAI أو Anthropic أو Google أو xAI) ما
يزال يعالج الطلب. اختر نماذج **Private** عندما تكون الخصوصية الكاملة مطلوبة.
</Warning>

## الميزات

- **تركيز على الخصوصية**: اختر بين وضعي "private" (خاص بالكامل) و"anonymized" (عبر وكيل)
- **نماذج غير مقيّدة**: وصول إلى نماذج من دون قيود على المحتوى
- **الوصول إلى النماذج الكبرى**: استخدم Claude وGPT وGemini وGrok عبر الوكيل المجهول الخاص بـ Venice
- **API متوافق مع OpenAI**: نقاط نهاية `/v1` قياسية لتكامل سهل
- **البث**: مدعوم على جميع النماذج
- **استدعاء الدوال**: مدعوم على نماذج محددة (تحقق من قدرات النموذج)
- **الرؤية**: مدعومة على النماذج التي تمتلك قدرة الرؤية
- **لا توجد حدود صارمة للمعدل**: قد يُطبَّق تقييد استخدام عادل عند الاستخدام المفرط

## البدء

<Steps>
  <Step title="Get your API key">
    1. سجّل في [venice.ai](https://venice.ai)
    2. انتقل إلى **Settings > API Keys > Create new key**
    3. انسخ مفتاح API الخاص بك (بالتنسيق: `vapi_xxxxxxxxxxxx`)
  </Step>
  <Step title="Configure OpenClaw">
    اختر طريقة الإعداد المفضلة لديك:

    <Tabs>
      <Tab title="Interactive (recommended)">
        ```bash
        openclaw onboard --auth-choice venice-api-key
        ```

        سيؤدي هذا إلى:
        1. طلب مفتاح API الخاص بك (أو استخدام `VENICE_API_KEY` الموجود)
        2. عرض جميع نماذج Venice المتاحة
        3. السماح لك باختيار النموذج الافتراضي
        4. تهيئة الموفّر تلقائيًا
      </Tab>
      <Tab title="Environment variable">
        ```bash
        export VENICE_API_KEY="vapi_xxxxxxxxxxxx"
        ```
      </Tab>
      <Tab title="Non-interactive">
        ```bash
        openclaw onboard --non-interactive \
          --auth-choice venice-api-key \
          --venice-api-key "vapi_xxxxxxxxxxxx"
        ```
      </Tab>
    </Tabs>

  </Step>
  <Step title="Verify setup">
    ```bash
    openclaw agent --model venice/kimi-k2-5 --message "Hello, are you working?"
    ```
  </Step>
</Steps>

## اختيار النموذج

بعد الإعداد، يعرض OpenClaw جميع نماذج Venice المتاحة. اختر وفقًا لاحتياجاتك:

- **النموذج الافتراضي**: `venice/kimi-k2-5` لاستدلال خاص قوي مع الرؤية.
- **خيار عالي القدرات**: `venice/claude-opus-4-6` لأقوى مسار Venice مجهول.
- **الخصوصية**: اختر نماذج "private" للاستدلال الخاص بالكامل.
- **القدرات**: اختر نماذج "anonymized" للوصول إلى Claude وGPT وGemini عبر وكيل Venice.

غيّر النموذج الافتراضي في أي وقت:

```bash
openclaw models set venice/kimi-k2-5
openclaw models set venice/claude-opus-4-6
```

اعرض جميع النماذج المتاحة:

```bash
openclaw models list | grep venice
```

يمكنك أيضًا تشغيل `openclaw configure`، ثم اختيار **Model/auth**، ثم اختيار **Venice AI**.

<Tip>
استخدم الجدول أدناه لاختيار النموذج المناسب لحالة استخدامك.

| حالة الاستخدام             | النموذج الموصى به                 | السبب                                          |
| -------------------------- | -------------------------------- | ---------------------------------------------- |
| **الدردشة العامة (الافتراضي)** | `kimi-k2-5`                      | استدلال خاص قوي مع الرؤية                      |
| **أفضل جودة إجمالية**      | `claude-opus-4-6`                | أقوى خيار Venice مجهول                         |
| **الخصوصية + البرمجة**     | `qwen3-coder-480b-a35b-instruct` | نموذج برمجة خاص بسياق كبير                     |
| **رؤية خاصة**              | `kimi-k2-5`                      | دعم للرؤية من دون مغادرة الوضع الخاص           |
| **سريع + منخفض التكلفة**   | `qwen3-4b`                       | نموذج استدلال خفيف                             |
| **مهام خاصة معقدة**        | `deepseek-v3.2`                  | استدلال قوي، لكن من دون دعم أدوات Venice       |
| **غير مقيّد**              | `venice-uncensored`              | بلا قيود على المحتوى                           |

</Tip>

## النماذج المتاحة (41 إجمالًا)

<AccordionGroup>
  <Accordion title="Private models (26) — خاصة بالكامل، من دون تسجيل">
    | معرّف النموذج                            | الاسم                                | السياق | الميزات                    |
    | --------------------------------------- | ----------------------------------- | ------ | -------------------------- |
    | `kimi-k2-5`                             | Kimi K2.5                           | 256k   | افتراضي، استدلال، رؤية     |
    | `kimi-k2-thinking`                      | Kimi K2 Thinking                    | 256k   | استدلال                    |
    | `llama-3.3-70b`                         | Llama 3.3 70B                       | 128k   | عام                        |
    | `llama-3.2-3b`                          | Llama 3.2 3B                        | 128k   | عام                        |
    | `hermes-3-llama-3.1-405b`               | Hermes 3 Llama 3.1 405B             | 128k   | عام، الأدوات معطلة         |
    | `qwen3-235b-a22b-thinking-2507`         | Qwen3 235B Thinking                 | 128k   | استدلال                    |
    | `qwen3-235b-a22b-instruct-2507`         | Qwen3 235B Instruct                 | 128k   | عام                        |
    | `qwen3-coder-480b-a35b-instruct`        | Qwen3 Coder 480B                    | 256k   | برمجة                      |
    | `qwen3-coder-480b-a35b-instruct-turbo`  | Qwen3 Coder 480B Turbo              | 256k   | برمجة                      |
    | `qwen3-5-35b-a3b`                       | Qwen3.5 35B A3B                     | 256k   | استدلال، رؤية              |
    | `qwen3-next-80b`                        | Qwen3 Next 80B                      | 256k   | عام                        |
    | `qwen3-vl-235b-a22b`                    | Qwen3 VL 235B (Vision)              | 256k   | رؤية                       |
    | `qwen3-4b`                              | Venice Small (Qwen3 4B)             | 32k    | سريع، استدلال              |
    | `deepseek-v3.2`                         | DeepSeek V3.2                       | 160k   | استدلال، الأدوات معطلة     |
    | `venice-uncensored`                     | Venice Uncensored (Dolphin-Mistral) | 32k    | غير مقيّد، الأدوات معطلة   |
    | `mistral-31-24b`                        | Venice Medium (Mistral)             | 128k   | رؤية                       |
    | `google-gemma-3-27b-it`                 | Google Gemma 3 27B Instruct         | 198k   | رؤية                       |
    | `openai-gpt-oss-120b`                   | OpenAI GPT OSS 120B                 | 128k   | عام                        |
    | `nvidia-nemotron-3-nano-30b-a3b`        | NVIDIA Nemotron 3 Nano 30B          | 128k   | عام                        |
    | `olafangensan-glm-4.7-flash-heretic`    | GLM 4.7 Flash Heretic               | 128k   | استدلال                    |
    | `zai-org-glm-4.6`                       | GLM 4.6                             | 198k   | عام                        |
    | `zai-org-glm-4.7`                       | GLM 4.7                             | 198k   | استدلال                    |
    | `zai-org-glm-4.7-flash`                 | GLM 4.7 Flash                       | 128k   | استدلال                    |
    | `zai-org-glm-5`                         | GLM 5                               | 198k   | استدلال                    |
    | `minimax-m21`                           | MiniMax M2.1                        | 198k   | استدلال                    |
    | `minimax-m25`                           | MiniMax M2.5                        | 198k   | استدلال                    |
  </Accordion>

  <Accordion title="Anonymized models (15) — عبر وكيل Venice">
    | معرّف النموذج                          | الاسم                           | السياق | الميزات                   |
    | ------------------------------------- | ------------------------------ | ------ | ------------------------- |
    | `claude-opus-4-6`                     | Claude Opus 4.6 (via Venice)   | 1M     | استدلال، رؤية             |
    | `claude-opus-4-5`                     | Claude Opus 4.5 (via Venice)   | 198k   | استدلال، رؤية             |
    | `claude-sonnet-4-6`                   | Claude Sonnet 4.6 (via Venice) | 1M     | استدلال، رؤية             |
    | `claude-sonnet-4-5`                   | Claude Sonnet 4.5 (via Venice) | 198k   | استدلال، رؤية             |
    | `openai-gpt-54`                       | GPT-5.4 (via Venice)           | 1M     | استدلال، رؤية             |
    | `openai-gpt-53-codex`                 | GPT-5.3 Codex (via Venice)     | 400k   | استدلال، رؤية، برمجة      |
    | `openai-gpt-52`                       | GPT-5.2 (via Venice)           | 256k   | استدلال                   |
    | `openai-gpt-52-codex`                 | GPT-5.2 Codex (via Venice)     | 256k   | استدلال، رؤية، برمجة      |
    | `openai-gpt-4o-2024-11-20`            | GPT-4o (via Venice)            | 128k   | رؤية                      |
    | `openai-gpt-4o-mini-2024-07-18`       | GPT-4o Mini (via Venice)       | 128k   | رؤية                      |
    | `gemini-3-1-pro-preview`              | Gemini 3.1 Pro (via Venice)    | 1M     | استدلال، رؤية             |
    | `gemini-3-pro-preview`                | Gemini 3 Pro (via Venice)      | 198k   | استدلال، رؤية             |
    | `gemini-3-flash-preview`              | Gemini 3 Flash (via Venice)    | 256k   | استدلال، رؤية             |
    | `grok-41-fast`                        | Grok 4.1 Fast (via Venice)     | 1M     | استدلال، رؤية             |
    | `grok-code-fast-1`                    | Grok Code Fast 1 (via Venice)  | 256k   | استدلال، برمجة            |
  </Accordion>
</AccordionGroup>

## اكتشاف النموذج

يكتشف OpenClaw النماذج تلقائيًا من Venice API عندما يكون `VENICE_API_KEY`
مُعيَّنًا. وإذا تعذر الوصول إلى API، فإنه يعود إلى فهرس ثابت.

نقطة النهاية `/models` عامة (لا تحتاج إلى مصادقة للعرض)، لكن الاستدلال يتطلب
مفتاح API صالحًا.

## دعم البث والأدوات

| الميزة                | الدعم                                                |
| --------------------- | ---------------------------------------------------- |
| **البث**              | جميع النماذج                                         |
| **استدعاء الدوال**    | معظم النماذج (تحقق من `supportsFunctionCalling` في API) |
| **الرؤية/الصور**      | النماذج المعلّمة بميزة "Vision"                      |
| **وضع JSON**          | مدعوم عبر `response_format`                          |

## التسعير

تستخدم Venice نظامًا قائمًا على الرصيد. راجع
[venice.ai/pricing](https://venice.ai/pricing) للاطلاع على الأسعار الحالية:

- **النماذج الخاصة**: تكلفة أقل عمومًا
- **النماذج المجهولة**: مشابهة لتسعير API المباشر + رسوم صغيرة لـ Venice

### Venice (مجهول) مقابل API المباشر

| الجانب         | Venice (مجهول)                 | API المباشر         |
| -------------- | ------------------------------ | ------------------- |
| **الخصوصية**   | إزالة البيانات الوصفية، وإخفاء الهوية | حسابك مرتبط         |
| **زمن الاستجابة** | +10-50ms (وكيل)               | مباشر               |
| **الميزات**    | معظم الميزات مدعومة            | الميزات الكاملة     |
| **الفوترة**    | أرصدة Venice                   | فوترة الموفّر       |

## أمثلة الاستخدام

```bash
# استخدم النموذج الخاص الافتراضي
openclaw agent --model venice/kimi-k2-5 --message "Quick health check"

# استخدم Claude Opus عبر Venice (مجهول)
openclaw agent --model venice/claude-opus-4-6 --message "Summarize this task"

# استخدم نموذجًا غير مقيّد
openclaw agent --model venice/venice-uncensored --message "Draft options"

# استخدم نموذج رؤية مع صورة
openclaw agent --model venice/qwen3-vl-235b-a22b --message "Review attached image"

# استخدم نموذج برمجة
openclaw agent --model venice/qwen3-coder-480b-a35b-instruct --message "Refactor this function"
```

## استكشاف الأخطاء وإصلاحها

<AccordionGroup>
  <Accordion title="لم يتم التعرف على مفتاح API">
    ```bash
    echo $VENICE_API_KEY
    openclaw models list | grep venice
    ```

    تأكد من أن المفتاح يبدأ بـ `vapi_`.

  </Accordion>

  <Accordion title="النموذج غير متاح">
    يتم تحديث فهرس نماذج Venice ديناميكيًا. شغّل `openclaw models list` لرؤية
    النماذج المتاحة حاليًا. وقد تكون بعض النماذج غير متصلة مؤقتًا.
  </Accordion>

  <Accordion title="مشكلات الاتصال">
    يقع Venice API على `https://api.venice.ai/api/v1`. تأكد من أن شبكتك تسمح
    باتصالات HTTPS.
  </Accordion>
</AccordionGroup>

<Note>
مزيد من المساعدة: [استكشاف الأخطاء وإصلاحها](/ar/help/troubleshooting) و[الأسئلة الشائعة](/ar/help/faq).
</Note>

## إعداد متقدم

<AccordionGroup>
  <Accordion title="مثال على ملف الإعداد">
    ```json5
    {
      env: { VENICE_API_KEY: "vapi_..." },
      agents: { defaults: { model: { primary: "venice/kimi-k2-5" } } },
      models: {
        mode: "merge",
        providers: {
          venice: {
            baseUrl: "https://api.venice.ai/api/v1",
            apiKey: "${VENICE_API_KEY}",
            api: "openai-completions",
            models: [
              {
                id: "kimi-k2-5",
                name: "Kimi K2.5",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 256000,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="Model selection" href="/ar/concepts/model-providers" icon="layers">
    اختيار الموفّرات، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="Venice AI" href="https://venice.ai" icon="globe">
    الصفحة الرئيسية لـ Venice AI وإنشاء الحساب.
  </Card>
  <Card title="API documentation" href="https://docs.venice.ai" icon="book">
    مرجع Venice API ووثائق المطورين.
  </Card>
  <Card title="Pricing" href="https://venice.ai/pricing" icon="credit-card">
    أسعار أرصدة Venice الحالية والخطط.
  </Card>
</CardGroup>
