---
read_when:
    - تريد إعداد Moonshot K2 ‏(Moonshot Open Platform) مقابل Kimi Coding
    - تحتاج إلى فهم نقاط النهاية المنفصلة، والمفاتيح المنفصلة، ومراجع النماذج المنفصلة
    - تريد إعدادات جاهزة للنسخ/اللصق لأيٍّ من المزودين
summary: إعداد Moonshot K2 مقابل Kimi Coding ‏(مزودات منفصلة + مفاتيح منفصلة)
title: Moonshot AI
x-i18n:
    generated_at: "2026-04-12T23:31:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3f261f83a9b37e4fffb0cd0803e0c64f27eae8bae91b91d8a781a030663076f8
    source_path: providers/moonshot.md
    workflow: 15
---

# Moonshot AI (Kimi)

توفّر Moonshot واجهة Kimi API مع نقاط نهاية متوافقة مع OpenAI. قم بإعداد
المزود واضبط النموذج الافتراضي على `moonshot/kimi-k2.5`، أو استخدم
Kimi Coding مع `kimi/kimi-code`.

<Warning>
إن Moonshot وKimi Coding **مزودان منفصلان**. المفاتيح غير قابلة للتبادل، ونقاط النهاية مختلفة، ومراجع النماذج مختلفة (`moonshot/...` مقابل `kimi/...`).
</Warning>

## فهرس النماذج المدمج

[//]: # "moonshot-kimi-k2-ids:start"

| مرجع النموذج                    | الاسم                  | التفكير | الإدخال      | السياق  | الحد الأقصى للإخراج |
| ------------------------------ | ---------------------- | ------- | ------------ | ------- | ------------------- |
| `moonshot/kimi-k2.5`           | Kimi K2.5              | لا      | text, image  | 262,144 | 262,144             |
| `moonshot/kimi-k2-thinking`    | Kimi K2 Thinking       | نعم     | text         | 262,144 | 262,144             |
| `moonshot/kimi-k2-thinking-turbo` | Kimi K2 Thinking Turbo | نعم   | text         | 262,144 | 262,144             |
| `moonshot/kimi-k2-turbo`       | Kimi K2 Turbo          | لا      | text         | 256,000 | 16,384              |

[//]: # "moonshot-kimi-k2-ids:end"

## البدء

اختر المزود واتبع خطوات الإعداد.

<Tabs>
  <Tab title="Moonshot API">
    **الأفضل لـ:** نماذج Kimi K2 عبر Moonshot Open Platform.

    <Steps>
      <Step title="اختر منطقة نقطة النهاية">
        | خيار المصادقة         | نقطة النهاية                  | المنطقة         |
        | --------------------- | ----------------------------- | ---------------- |
        | `moonshot-api-key`    | `https://api.moonshot.ai/v1`  | دولي             |
        | `moonshot-api-key-cn` | `https://api.moonshot.cn/v1`  | الصين            |
      </Step>
      <Step title="شغّل الإعداد الأولي">
        ```bash
        openclaw onboard --auth-choice moonshot-api-key
        ```

        أو لنقطة نهاية الصين:

        ```bash
        openclaw onboard --auth-choice moonshot-api-key-cn
        ```
      </Step>
      <Step title="اضبط نموذجًا افتراضيًا">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "moonshot/kimi-k2.5" },
            },
          },
        }
        ```
      </Step>
      <Step title="تحقق من توفر النماذج">
        ```bash
        openclaw models list --provider moonshot
        ```
      </Step>
    </Steps>

    ### مثال على الإعداد

    ```json5
    {
      env: { MOONSHOT_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "moonshot/kimi-k2.5" },
          models: {
            // moonshot-kimi-k2-aliases:start
            "moonshot/kimi-k2.5": { alias: "Kimi K2.5" },
            "moonshot/kimi-k2-thinking": { alias: "Kimi K2 Thinking" },
            "moonshot/kimi-k2-thinking-turbo": { alias: "Kimi K2 Thinking Turbo" },
            "moonshot/kimi-k2-turbo": { alias: "Kimi K2 Turbo" },
            // moonshot-kimi-k2-aliases:end
          },
        },
      },
      models: {
        mode: "merge",
        providers: {
          moonshot: {
            baseUrl: "https://api.moonshot.ai/v1",
            apiKey: "${MOONSHOT_API_KEY}",
            api: "openai-completions",
            models: [
              // moonshot-kimi-k2-models:start
              {
                id: "kimi-k2.5",
                name: "Kimi K2.5",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-thinking",
                name: "Kimi K2 Thinking",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-thinking-turbo",
                name: "Kimi K2 Thinking Turbo",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-turbo",
                name: "Kimi K2 Turbo",
                reasoning: false,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 256000,
                maxTokens: 16384,
              },
              // moonshot-kimi-k2-models:end
            ],
          },
        },
      },
    }
    ```

  </Tab>

  <Tab title="Kimi Coding">
    **الأفضل لـ:** المهام البرمجية المركزة عبر نقطة نهاية Kimi Coding.

    <Note>
    يستخدم Kimi Coding مفتاح API مختلفًا وبادئة مزود مختلفة (`kimi/...`) عن Moonshot (`moonshot/...`). يظل مرجع النموذج القديم `kimi/k2p5` مقبولًا كمعرّف توافق.
    </Note>

    <Steps>
      <Step title="شغّل الإعداد الأولي">
        ```bash
        openclaw onboard --auth-choice kimi-code-api-key
        ```
      </Step>
      <Step title="اضبط نموذجًا افتراضيًا">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "kimi/kimi-code" },
            },
          },
        }
        ```
      </Step>
      <Step title="تحقق من توفر النموذج">
        ```bash
        openclaw models list --provider kimi
        ```
      </Step>
    </Steps>

    ### مثال على الإعداد

    ```json5
    {
      env: { KIMI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "kimi/kimi-code" },
          models: {
            "kimi/kimi-code": { alias: "Kimi" },
          },
        },
      },
    }
    ```

  </Tab>
</Tabs>

## بحث الويب في Kimi

يشحن OpenClaw أيضًا **Kimi** كمزود `web_search`، ومدعومًا ببحث الويب من Moonshot.

<Steps>
  <Step title="شغّل إعداد بحث الويب التفاعلي">
    ```bash
    openclaw configure --section web
    ```

    اختر **Kimi** في قسم بحث الويب لتخزين
    `plugins.entries.moonshot.config.webSearch.*`.

  </Step>
  <Step title="إعداد منطقة بحث الويب والنموذج">
    يطلب الإعداد التفاعلي ما يلي:

    | الإعداد            | الخيارات                                                              |
    | ------------------ | -------------------------------------------------------------------- |
    | منطقة API          | `https://api.moonshot.ai/v1` (دولي) أو `https://api.moonshot.cn/v1` (الصين) |
    | نموذج بحث الويب    | الافتراضي هو `kimi-k2.5`                                             |

  </Step>
</Steps>

توجد الإعدادات ضمن `plugins.entries.moonshot.config.webSearch`:

```json5
{
  plugins: {
    entries: {
      moonshot: {
        config: {
          webSearch: {
            apiKey: "sk-...", // or use KIMI_API_KEY / MOONSHOT_API_KEY
            baseUrl: "https://api.moonshot.ai/v1",
            model: "kimi-k2.5",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "kimi",
      },
    },
  },
}
```

## متقدم

<AccordionGroup>
  <Accordion title="وضع التفكير الأصلي">
    تدعم Moonshot Kimi وضع تفكير أصلي ثنائي:

    - `thinking: { type: "enabled" }`
    - `thinking: { type: "disabled" }`

    قم بإعداده لكل نموذج عبر `agents.defaults.models.<provider/model>.params`:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "moonshot/kimi-k2.5": {
              params: {
                thinking: { type: "disabled" },
              },
            },
          },
        },
      },
    }
    ```

    يقوم OpenClaw أيضًا بربط مستويات `/think` أثناء التشغيل لـ Moonshot:

    | مستوى `/think`      | سلوك Moonshot              |
    | ------------------- | -------------------------- |
    | `/think off`        | `thinking.type=disabled`   |
    | أي مستوى غير off    | `thinking.type=enabled`    |

    <Warning>
    عند تمكين التفكير في Moonshot، يجب أن تكون `tool_choice` هي `auto` أو `none`. يقوم OpenClaw بتطبيع قيم `tool_choice` غير المتوافقة إلى `auto` من أجل التوافق.
    </Warning>

  </Accordion>

  <Accordion title="توافق استخدام البث">
    تعلن نقاط نهاية Moonshot الأصلية (`https://api.moonshot.ai/v1` و
    `https://api.moonshot.cn/v1`) عن توافق استخدام البث على
    ناقل `openai-completions` المشترك. يعتمد OpenClaw على ذلك من خلال قدرات نقطة النهاية، لذلك ترث معرّفات المزودات المخصصة المتوافقة التي تستهدف مضيفي Moonshot الأصليين أنفسهم سلوك استخدام البث ذاته.
  </Accordion>

  <Accordion title="مرجع نقطة النهاية ومرجع النموذج">
    | المزود        | بادئة مرجع النموذج | نقطة النهاية                   | متغير بيئة المصادقة |
    | ------------- | ------------------ | ------------------------------ | ------------------- |
    | Moonshot      | `moonshot/`        | `https://api.moonshot.ai/v1`   | `MOONSHOT_API_KEY`  |
    | Moonshot CN   | `moonshot/`        | `https://api.moonshot.cn/v1`   | `MOONSHOT_API_KEY`  |
    | Kimi Coding   | `kimi/`            | نقطة نهاية Kimi Coding         | `KIMI_API_KEY`      |
    | بحث الويب     | غير متاح           | نفس منطقة Moonshot API         | `KIMI_API_KEY` أو `MOONSHOT_API_KEY` |

    - يستخدم بحث الويب في Kimi `KIMI_API_KEY` أو `MOONSHOT_API_KEY`، ويكون افتراضيًا على `https://api.moonshot.ai/v1` مع النموذج `kimi-k2.5`.
    - قم بتجاوز بيانات التسعير وبيانات السياق الوصفية في `models.providers` إذا لزم الأمر.
    - إذا نشرت Moonshot حدود سياق مختلفة لأحد النماذج، فقم بتعديل `contextWindow` وفقًا لذلك.

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزودات، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="بحث الويب" href="/tools/web-search" icon="magnifying-glass">
    إعداد مزودات بحث الويب بما في ذلك Kimi.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference" icon="gear">
    المخطط الكامل لإعدادات المزودات والنماذج وPlugin.
  </Card>
  <Card title="Moonshot Open Platform" href="https://platform.moonshot.ai" icon="globe">
    إدارة مفاتيح Moonshot API والوثائق.
  </Card>
</CardGroup>
