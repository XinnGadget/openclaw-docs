---
read_when:
    - تريد تشغيل OpenClaw مع نماذج سحابية أو محلية عبر Ollama
    - تحتاج إلى إرشادات إعداد Ollama وتهيئته
summary: شغّل OpenClaw مع Ollama (النماذج السحابية والمحلية)
title: Ollama
x-i18n:
    generated_at: "2026-04-12T23:31:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: ec796241b884ca16ec7077df4f3f1910e2850487bb3ea94f8fdb37c77e02b219
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

Ollama هو وقت تشغيل محلي لـ LLM يجعل تشغيل النماذج مفتوحة المصدر على جهازك
أمرًا سهلًا. يتكامل OpenClaw مع API الأصلي لـ Ollama (`/api/chat`)، ويدعم
البث واستدعاء الأدوات، ويمكنه الاكتشاف التلقائي لنماذج Ollama المحلية عندما
تفعّل ذلك عبر `OLLAMA_API_KEY` (أو ملف مصادقة) ولا تعرّف إدخالًا صريحًا
`models.providers.ollama`.

<Warning>
**مستخدمو Ollama البعيد:** لا تستخدم عنوان URL المتوافق مع OpenAI على المسار
`/v1` (`http://host:11434/v1`) مع OpenClaw. فهذا يكسر استدعاء الأدوات وقد
تُخرج النماذج JSON الخام للأدوات كنص عادي. استخدم عنوان URL الأصلي لـ API الخاص
بـ Ollama بدلًا من ذلك: `baseUrl: "http://host:11434"` (من دون `/v1`).
</Warning>

## البدء

اختر طريقة الإعداد والوضع المفضلين لديك.

<Tabs>
  <Tab title="Onboarding (recommended)">
    **الأفضل لـ:** أسرع مسار إلى إعداد Ollama عامل مع اكتشاف تلقائي للنماذج.

    <Steps>
      <Step title="Run onboarding">
        ```bash
        openclaw onboard
        ```

        اختر **Ollama** من قائمة الموفّرين.
      </Step>
      <Step title="Choose your mode">
        - **Cloud + Local** — النماذج المستضافة سحابيًا والنماذج المحلية معًا
        - **Local** — النماذج المحلية فقط

        إذا اخترت **Cloud + Local** ولم تكن قد سجلت الدخول إلى ollama.com،
        فسيفتح onboarding تدفق تسجيل دخول عبر المتصفح.
      </Step>
      <Step title="Select a model">
        يكتشف onboarding النماذج المتاحة ويقترح القيم الافتراضية. ويقوم تلقائيًا
        بسحب النموذج المحدد إذا لم يكن متاحًا محليًا.
      </Step>
      <Step title="Verify the model is available">
        ```bash
        openclaw models list --provider ollama
        ```
      </Step>
    </Steps>

    ### الوضع غير التفاعلي

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --accept-risk
    ```

    ويمكنك اختياريًا تحديد Base URL مخصص أو نموذج:

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --custom-base-url "http://ollama-host:11434" \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk
    ```

  </Tab>

  <Tab title="Manual setup">
    **الأفضل لـ:** تحكم كامل في التثبيت وسحب النماذج والإعداد.

    <Steps>
      <Step title="Install Ollama">
        نزّله من [ollama.com/download](https://ollama.com/download).
      </Step>
      <Step title="Pull a local model">
        ```bash
        ollama pull gemma4
        # أو
        ollama pull gpt-oss:20b
        # أو
        ollama pull llama3.3
        ```
      </Step>
      <Step title="Sign in for cloud models (optional)">
        إذا كنت تريد النماذج السحابية أيضًا:

        ```bash
        ollama signin
        ```
      </Step>
      <Step title="Enable Ollama for OpenClaw">
        عيّن أي قيمة لمفتاح API (لا يتطلب Ollama مفتاحًا حقيقيًا):

        ```bash
        # عيّن متغير البيئة
        export OLLAMA_API_KEY="ollama-local"

        # أو اضبطه في ملف الإعدادات
        openclaw config set models.providers.ollama.apiKey "ollama-local"
        ```
      </Step>
      <Step title="Inspect and set your model">
        ```bash
        openclaw models list
        openclaw models set ollama/gemma4
        ```

        أو عيّن النموذج الافتراضي في الإعدادات:

        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "ollama/gemma4" },
            },
          },
        }
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## النماذج السحابية

<Tabs>
  <Tab title="Cloud + Local">
    تتيح لك النماذج السحابية تشغيل النماذج المستضافة سحابيًا إلى جانب نماذجك
    المحلية. ومن الأمثلة على ذلك `kimi-k2.5:cloud` و`minimax-m2.7:cloud`
    و`glm-5.1:cloud` -- وهذه **لا** تتطلب تنفيذ `ollama pull` محليًا.

    اختر وضع **Cloud + Local** أثناء الإعداد. يتحقق المعالج مما إذا كنت قد سجلت
    الدخول ويفتح تدفق تسجيل دخول عبر المتصفح عند الحاجة. وإذا تعذر التحقق من
    المصادقة، يعود المعالج إلى القيم الافتراضية للنماذج المحلية.

    ويمكنك أيضًا تسجيل الدخول مباشرةً على
    [ollama.com/signin](https://ollama.com/signin).

    يقترح OpenClaw حاليًا هذه القيم السحابية الافتراضية:
    `kimi-k2.5:cloud` و`minimax-m2.7:cloud` و`glm-5.1:cloud`.

  </Tab>

  <Tab title="Local only">
    في وضع المحلي فقط، يكتشف OpenClaw النماذج من مثيل Ollama المحلي.
    ولا يلزم تسجيل دخول سحابي.

    يقترح OpenClaw حاليًا `gemma4` باعتباره القيمة الافتراضية المحلية.

  </Tab>
</Tabs>

## اكتشاف النموذج (الموفّر الضمني)

عند تعيين `OLLAMA_API_KEY` (أو ملف مصادقة) و**عدم** تعريف
`models.providers.ollama`، يكتشف OpenClaw النماذج من مثيل Ollama المحلي على
`http://127.0.0.1:11434`.

| السلوك               | التفاصيل                                                                                                                                                              |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| استعلام الفهرس       | يستعلم عن `/api/tags`                                                                                                                                                 |
| اكتشاف القدرات       | يستخدم عمليات بحث `/api/show` بأفضل جهد لقراءة `contextWindow` واكتشاف القدرات (بما في ذلك الرؤية)                                                                  |
| نماذج الرؤية         | تُعلَّم النماذج التي تبلغ عن قدرة `vision` عبر `/api/show` بأنها قادرة على التعامل مع الصور (`input: ["text", "image"]`)، لذلك يحقن OpenClaw الصور تلقائيًا في المطالبة |
| اكتشاف الاستدلال     | يعيّن `reasoning` باستخدام أسلوب استدلالي قائم على اسم النموذج (`r1` و`reasoning` و`think`)                                                                         |
| حدود الرموز          | يعيّن `maxTokens` إلى حد Ollama الافتراضي الأقصى للرموز المستخدم في OpenClaw                                                                                         |
| التكاليف             | يعيّن جميع التكاليف إلى `0`                                                                                                                                           |

وهذا يتجنب إدخالات النماذج اليدوية مع إبقاء الفهرس متوافقًا مع مثيل Ollama المحلي.

```bash
# اعرض النماذج المتاحة
ollama list
openclaw models list
```

ولإضافة نموذج جديد، ما عليك سوى سحبه باستخدام Ollama:

```bash
ollama pull mistral
```

سيتم اكتشاف النموذج الجديد تلقائيًا ويصبح متاحًا للاستخدام.

<Note>
إذا عيّنت `models.providers.ollama` بشكل صريح، فسيتم تخطي الاكتشاف التلقائي
ويجب عليك تعريف النماذج يدويًا. راجع قسم الإعداد الصريح أدناه.
</Note>

## الإعداد

<Tabs>
  <Tab title="Basic (implicit discovery)">
    أبسط طريقة لتمكين Ollama هي عبر متغير البيئة:

    ```bash
    export OLLAMA_API_KEY="ollama-local"
    ```

    <Tip>
    إذا كان `OLLAMA_API_KEY` معيّنًا، يمكنك حذف `apiKey` من إدخال الموفّر
    وسيقوم OpenClaw بملئه لفحوصات التوفر.
    </Tip>

  </Tab>

  <Tab title="Explicit (manual models)">
    استخدم الإعداد الصريح عندما يعمل Ollama على مضيف/منفذ آخر، أو عندما تريد
    فرض نوافذ سياق أو قوائم نماذج محددة، أو عندما تريد تعريفات نماذج يدوية بالكامل.

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434",
            apiKey: "ollama-local",
            api: "ollama",
            models: [
              {
                id: "gpt-oss:20b",
                name: "GPT-OSS 20B",
                reasoning: false,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 8192,
                maxTokens: 8192 * 10
              }
            ]
          }
        }
      }
    }
    ```

  </Tab>

  <Tab title="Custom base URL">
    إذا كان Ollama يعمل على مضيف أو منفذ مختلف (يؤدي الإعداد الصريح إلى تعطيل
    الاكتشاف التلقائي، لذا عرّف النماذج يدويًا):

    ```json5
    {
      models: {
        providers: {
          ollama: {
            apiKey: "ollama-local",
            baseUrl: "http://ollama-host:11434", // بدون /v1 - استخدم عنوان URL الأصلي لـ API الخاص بـ Ollama
            api: "ollama", // عيّنه صراحةً لضمان سلوك استدعاء الأدوات الأصلي
          },
        },
      },
    }
    ```

    <Warning>
    لا تضف `/v1` إلى عنوان URL. يستخدم المسار `/v1` الوضع المتوافق مع OpenAI،
    حيث لا يكون استدعاء الأدوات موثوقًا. استخدم عنوان URL الأساسي لـ Ollama من
    دون لاحقة مسار.
    </Warning>

  </Tab>
</Tabs>

### اختيار النموذج

بمجرد التهيئة، تصبح جميع نماذج Ollama لديك متاحة:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## بحث الويب في Ollama

يدعم OpenClaw **بحث الويب في Ollama** كموفّر `web_search` مضمّن.

| الخاصية    | التفاصيل                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------ |
| المضيف      | يستخدم مضيف Ollama المهيأ لديك (`models.providers.ollama.baseUrl` عند تعيينه، وإلا `http://127.0.0.1:11434`)          |
| المصادقة    | لا يحتاج إلى مفتاح                                                                                                       |
| المتطلب     | يجب أن يكون Ollama قيد التشغيل وأن تكون قد سجلت الدخول عبر `ollama signin`                                              |

اختر **Ollama Web Search** أثناء `openclaw onboard` أو
`openclaw configure --section web`، أو عيّن:

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

<Note>
للاطلاع على تفاصيل الإعداد والسلوك كاملة، راجع [Ollama Web Search](/ar/tools/ollama-search).
</Note>

## إعداد متقدم

<AccordionGroup>
  <Accordion title="Legacy OpenAI-compatible mode">
    <Warning>
    **استدعاء الأدوات ليس موثوقًا في الوضع المتوافق مع OpenAI.** استخدم هذا
    الوضع فقط إذا كنت بحاجة إلى تنسيق OpenAI لوكيل ما ولا تعتمد على السلوك
    الأصلي لاستدعاء الأدوات.
    </Warning>

    إذا كنت بحاجة إلى استخدام نقطة النهاية المتوافقة مع OpenAI بدلًا من ذلك
    (على سبيل المثال، خلف وكيل لا يدعم إلا تنسيق OpenAI)، فعيّن
    `api: "openai-completions"` صراحةً:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: true, // الافتراضي: true
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

    قد لا يدعم هذا الوضع البث واستدعاء الأدوات في الوقت نفسه. وقد تحتاج إلى
    تعطيل البث باستخدام `params: { streaming: false }` في إعداد النموذج.

    عند استخدام `api: "openai-completions"` مع Ollama، يحقن OpenClaw
    `options.num_ctx` افتراضيًا حتى لا يعود Ollama بصمت إلى نافذة سياق 4096.
    وإذا كان الوكيل/الجهة الأصلية لديك يرفض حقول `options` غير المعروفة،
    فعطّل هذا السلوك:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: false,
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Context windows">
    بالنسبة إلى النماذج المكتشفة تلقائيًا، يستخدم OpenClaw نافذة السياق التي
    يبلغ عنها Ollama عندما تكون متاحة، وإلا فيعود إلى نافذة سياق Ollama
    الافتراضية المستخدمة في OpenClaw.

    ويمكنك تجاوز `contextWindow` و`maxTokens` في إعداد الموفّر الصريح:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            models: [
              {
                id: "llama3.3",
                contextWindow: 131072,
                maxTokens: 65536,
              }
            ]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="نماذج الاستدلال">
    يتعامل OpenClaw مع النماذج التي تحمل أسماء مثل `deepseek-r1` أو `reasoning` أو `think` على أنها قادرة على الاستدلال افتراضيًا.

    ```bash
    ollama pull deepseek-r1:32b
    ```

    لا حاجة إلى أي إعداد إضافي -- يضع OpenClaw عليها هذه العلامة تلقائيًا.

  </Accordion>

  <Accordion title="تكاليف النماذج">
    Ollama مجاني ويعمل محليًا، لذا تُضبط جميع تكاليف النماذج على $0. وينطبق ذلك على كل من النماذج المكتشفة تلقائيًا والنماذج المعرّفة يدويًا.
  </Accordion>

  <Accordion title="تضمينات الذاكرة">
    يسجّل Plugin Ollama المضمّن موفّر تضمينات للذاكرة من أجل
    [بحث الذاكرة](/ar/concepts/memory). ويستخدم Base URL ومفتاح API المهيأين لـ Ollama.

    | الخاصية      | القيمة              |
    | ------------- | ------------------- |
    | النموذج الافتراضي | `nomic-embed-text` |
    | السحب التلقائي | نعم — يُسحب نموذج التضمين تلقائيًا إذا لم يكن موجودًا محليًا |

    لاختيار Ollama كموفّر تضمينات لبحث الذاكرة:

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: { provider: "ollama" },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="إعداد البث">
    يستخدم تكامل Ollama في OpenClaw **Ollama API الأصلي** (`/api/chat`) افتراضيًا، والذي يدعم بالكامل البث واستدعاء الأدوات في الوقت نفسه. لا حاجة إلى أي إعداد خاص.

    <Tip>
    إذا كنت بحاجة إلى استخدام نقطة النهاية المتوافقة مع OpenAI، فراجع قسم "الوضع القديم المتوافق مع OpenAI" أعلاه. قد لا يعمل البث واستدعاء الأدوات في الوقت نفسه في ذلك الوضع.
    </Tip>

  </Accordion>
</AccordionGroup>

## استكشاف الأخطاء وإصلاحها

<AccordionGroup>
  <Accordion title="لم يتم اكتشاف Ollama">
    تأكد من أن Ollama قيد التشغيل وأنك عيّنت `OLLAMA_API_KEY` (أو ملف مصادقة)، وأنك **لم** تعرّف إدخالًا صريحًا `models.providers.ollama`:

    ```bash
    ollama serve
    ```

    تحقّق من أن API متاح:

    ```bash
    curl http://localhost:11434/api/tags
    ```

  </Accordion>

  <Accordion title="لا توجد نماذج متاحة">
    إذا لم يكن نموذجك مدرجًا، فإما أن تسحب النموذج محليًا أو تعرّفه صراحةً في `models.providers.ollama`.

    ```bash
    ollama list  # اعرض ما هو مثبت
    ollama pull gemma4
    ollama pull gpt-oss:20b
    ollama pull llama3.3     # أو نموذجًا آخر
    ```

  </Accordion>

  <Accordion title="تم رفض الاتصال">
    تحقّق من أن Ollama يعمل على المنفذ الصحيح:

    ```bash
    # تحقق مما إذا كان Ollama قيد التشغيل
    ps aux | grep ollama

    # أو أعد تشغيل Ollama
    ollama serve
    ```

  </Accordion>
</AccordionGroup>

<Note>
مزيد من المساعدة: [استكشاف الأخطاء وإصلاحها](/ar/help/troubleshooting) و[الأسئلة الشائعة](/ar/help/faq).
</Note>

## ذو صلة

<CardGroup cols={2}>
  <Card title="Model providers" href="/ar/concepts/model-providers" icon="layers">
    نظرة عامة على جميع الموفّرين، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="Model selection" href="/ar/concepts/models" icon="brain">
    كيفية اختيار النماذج وتهيئتها.
  </Card>
  <Card title="Ollama Web Search" href="/ar/tools/ollama-search" icon="magnifying-glass">
    تفاصيل الإعداد والسلوك الكاملة لبحث الويب المدعوم من Ollama.
  </Card>
  <Card title="Configuration" href="/ar/gateway/configuration" icon="gear">
    المرجع الكامل للإعدادات.
  </Card>
</CardGroup>
