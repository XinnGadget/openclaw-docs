---
read_when:
    - تريد استخدام Arcee AI مع OpenClaw
    - تحتاج إلى متغير البيئة لمفتاح API أو خيار المصادقة عبر CLI
summary: إعداد Arcee AI (المصادقة + اختيار النموذج)
title: Arcee AI
x-i18n:
    generated_at: "2026-04-12T23:29:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 68c5fddbe272c69611257ceff319c4de7ad21134aaf64582d60720a6f3b853cc
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

توفّر [Arcee AI](https://arcee.ai) إمكانية الوصول إلى مجموعة نماذج Trinity القائمة على مزيج من الخبراء عبر API متوافق مع OpenAI. جميع نماذج Trinity مرخّصة بموجب Apache 2.0.

يمكن الوصول إلى نماذج Arcee AI مباشرة عبر منصة Arcee أو من خلال [OpenRouter](/ar/providers/openrouter).

| الخاصية | القيمة                                                                                |
| -------- | ------------------------------------------------------------------------------------- |
| المزود | `arcee`                                                                               |
| المصادقة | `ARCEEAI_API_KEY` (مباشر) أو `OPENROUTER_API_KEY` (عبر OpenRouter)                   |
| API      | متوافق مع OpenAI                                                                     |
| عنوان URL الأساسي | `https://api.arcee.ai/api/v1` (مباشر) أو `https://openrouter.ai/api/v1` (OpenRouter) |

## البدء

<Tabs>
  <Tab title="مباشر (منصة Arcee)">
    <Steps>
      <Step title="الحصول على مفتاح API">
        أنشئ مفتاح API في [Arcee AI](https://chat.arcee.ai/).
      </Step>
      <Step title="تشغيل الإعداد الأولي">
        ```bash
        openclaw onboard --auth-choice arceeai-api-key
        ```
      </Step>
      <Step title="تعيين نموذج افتراضي">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```
      </Step>
    </Steps>
  </Tab>

  <Tab title="عبر OpenRouter">
    <Steps>
      <Step title="الحصول على مفتاح API">
        أنشئ مفتاح API في [OpenRouter](https://openrouter.ai/keys).
      </Step>
      <Step title="تشغيل الإعداد الأولي">
        ```bash
        openclaw onboard --auth-choice arceeai-openrouter
        ```
      </Step>
      <Step title="تعيين نموذج افتراضي">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```

        تعمل مراجع النماذج نفسها مع كل من الإعداد المباشر وإعداد OpenRouter (على سبيل المثال `arcee/trinity-large-thinking`).
      </Step>
    </Steps>

  </Tab>
</Tabs>

## الإعداد غير التفاعلي

<Tabs>
  <Tab title="مباشر (منصة Arcee)">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-api-key \
      --arceeai-api-key "$ARCEEAI_API_KEY"
    ```
  </Tab>

  <Tab title="عبر OpenRouter">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-openrouter \
      --openrouter-api-key "$OPENROUTER_API_KEY"
    ```
  </Tab>
</Tabs>

## الفهرس المدمج

يشحن OpenClaw حاليًا فهرس Arcee المدمج التالي:

| مرجع النموذج                  | الاسم                  | الإدخال | السياق | التكلفة (إدخال/إخراج لكل 1M) | ملاحظات                                      |
| ----------------------------- | ---------------------- | ------- | ------ | ----------------------------- | -------------------------------------------- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text    | 256K   | $0.25 / $0.90                 | النموذج الافتراضي؛ التفكير ممكّن             |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text    | 128K   | $0.25 / $1.00                 | للأغراض العامة؛ 400B معلمات، 13B نشطة        |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text    | 128K   | $0.045 / $0.15                | سريع وفعّال من حيث التكلفة؛ استدعاء الدوال    |

<Tip>
يضبط الإعداد الأولي `arcee/trinity-large-thinking` كنموذج افتراضي.
</Tip>

## الميزات المدعومة

| الميزة                                        | مدعومة                     |
| --------------------------------------------- | -------------------------- |
| البث                                          | نعم                        |
| استخدام الأدوات / استدعاء الدوال              | نعم                        |
| المخرجات المهيكلة (وضع JSON ومخطط JSON)       | نعم                        |
| التفكير الموسّع                               | نعم (Trinity Large Thinking) |

<AccordionGroup>
  <Accordion title="ملاحظة حول البيئة">
    إذا كان Gateway يعمل كخدمة daemon ‏(launchd/systemd)، فتأكد من أن `ARCEEAI_API_KEY`
    (أو `OPENROUTER_API_KEY`) متاح لتلك العملية (على سبيل المثال، في
    `~/.openclaw/.env` أو عبر `env.shellEnv`).
  </Accordion>

  <Accordion title="توجيه OpenRouter">
    عند استخدام نماذج Arcee عبر OpenRouter، تنطبق مراجع النماذج `arcee/*` نفسها.
    يتولى OpenClaw معالجة التوجيه بشفافية استنادًا إلى خيار المصادقة الذي اخترته. راجع
    [توثيق مزود OpenRouter](/ar/providers/openrouter) للحصول على تفاصيل إعدادات
    خاصة بـ OpenRouter.
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="OpenRouter" href="/ar/providers/openrouter" icon="shuffle">
    الوصول إلى نماذج Arcee والعديد من النماذج الأخرى عبر مفتاح API واحد.
  </Card>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزودات، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
</CardGroup>
