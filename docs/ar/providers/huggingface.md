---
read_when:
    - تريد استخدام Hugging Face Inference مع OpenClaw
    - تحتاج إلى متغير البيئة لرمز HF أو خيار المصادقة عبر CLI
summary: إعداد Hugging Face Inference ‏(المصادقة + اختيار النموذج)
title: Hugging Face (Inference)
x-i18n:
    generated_at: "2026-04-12T23:30:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7787fce1acfe81adb5380ab1c7441d661d03c574da07149c037d3b6ba3c8e52a
    source_path: providers/huggingface.md
    workflow: 15
---

# Hugging Face (Inference)

توفّر [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) واجهة إكمالات دردشة متوافقة مع OpenAI عبر API موجه واحد. وهذا يمنحك إمكانية الوصول إلى العديد من النماذج (DeepSeek وLlama وغيرهما) باستخدام رمز واحد. يستخدم OpenClaw **نقطة النهاية المتوافقة مع OpenAI** (إكمالات الدردشة فقط)؛ أما لتحويل النص إلى صورة، أو التضمينات، أو الكلام فاستخدم [عملاء HF inference](https://huggingface.co/docs/api-inference/quicktour) مباشرة.

- المزود: `huggingface`
- المصادقة: `HUGGINGFACE_HUB_TOKEN` أو `HF_TOKEN` (رمز دقيق الصلاحيات مع إذن **Make calls to Inference Providers**)
- API: متوافق مع OpenAI ‏(`https://router.huggingface.co/v1`)
- الفوترة: رمز HF واحد؛ [الأسعار](https://huggingface.co/docs/inference-providers/pricing) تتبع أسعار المزود مع فئة مجانية.

## البدء

<Steps>
  <Step title="أنشئ رمزًا دقيق الصلاحيات">
    انتقل إلى [Hugging Face Settings Tokens](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained) وأنشئ رمزًا جديدًا دقيق الصلاحيات.

    <Warning>
    يجب أن يكون الرمز مفعّلًا له إذن **Make calls to Inference Providers** وإلا فسيتم رفض طلبات API.
    </Warning>

  </Step>
  <Step title="شغّل الإعداد الأولي">
    اختر **Hugging Face** من القائمة المنسدلة للمزود، ثم أدخل مفتاح API عند مطالبتك بذلك:

    ```bash
    openclaw onboard --auth-choice huggingface-api-key
    ```

  </Step>
  <Step title="اختر نموذجًا افتراضيًا">
    من القائمة المنسدلة **Default Hugging Face model**، اختر النموذج الذي تريده. يتم تحميل القائمة من Inference API عندما يكون لديك رمز صالح؛ وإلا فستُعرض قائمة مدمجة. يتم حفظ اختيارك كنموذج افتراضي.

    يمكنك أيضًا تعيين النموذج الافتراضي أو تغييره لاحقًا في الإعدادات:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/deepseek-ai/DeepSeek-R1" },
        },
      },
    }
    ```

  </Step>
  <Step title="تحقق من توفر النموذج">
    ```bash
    openclaw models list --provider huggingface
    ```
  </Step>
</Steps>

### الإعداد غير التفاعلي

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice huggingface-api-key \
  --huggingface-api-key "$HF_TOKEN"
```

سيؤدي هذا إلى تعيين `huggingface/deepseek-ai/DeepSeek-R1` كنموذج افتراضي.

## معرّفات النماذج

تستخدم مراجع النماذج الصيغة `huggingface/<org>/<model>` (معرّفات بنمط Hub). القائمة أدناه مأخوذة من **GET** ‏`https://router.huggingface.co/v1/models`؛ وقد يتضمن الفهرس لديك المزيد.

| النموذج                  | المرجع (أضف البادئة `huggingface/`) |
| ------------------------ | ----------------------------------- |
| DeepSeek R1              | `deepseek-ai/DeepSeek-R1`           |
| DeepSeek V3.2            | `deepseek-ai/DeepSeek-V3.2`         |
| Qwen3 8B                 | `Qwen/Qwen3-8B`                     |
| Qwen2.5 7B Instruct      | `Qwen/Qwen2.5-7B-Instruct`          |
| Qwen3 32B                | `Qwen/Qwen3-32B`                    |
| Llama 3.3 70B Instruct   | `meta-llama/Llama-3.3-70B-Instruct` |
| Llama 3.1 8B Instruct    | `meta-llama/Llama-3.1-8B-Instruct`  |
| GPT-OSS 120B             | `openai/gpt-oss-120b`               |
| GLM 4.7                  | `zai-org/GLM-4.7`                   |
| Kimi K2.5                | `moonshotai/Kimi-K2.5`              |

<Tip>
يمكنك إلحاق `:fastest` أو `:cheapest` بأي معرّف نموذج. عيّن ترتيبك الافتراضي في [Inference Provider settings](https://hf.co/settings/inference-providers)؛ وراجع [Inference Providers](https://huggingface.co/docs/inference-providers) و**GET** ‏`https://router.huggingface.co/v1/models` للاطلاع على القائمة الكاملة.
</Tip>

## تفاصيل متقدمة

<AccordionGroup>
  <Accordion title="اكتشاف النماذج والقائمة المنسدلة في الإعداد الأولي">
    يكتشف OpenClaw النماذج عن طريق استدعاء **نقطة نهاية Inference مباشرة**:

    ```bash
    GET https://router.huggingface.co/v1/models
    ```

    (اختياري: أرسل `Authorization: Bearer $HUGGINGFACE_HUB_TOKEN` أو `$HF_TOKEN` للحصول على القائمة الكاملة؛ إذ تعرض بعض نقاط النهاية مجموعة فرعية بدون مصادقة.) تكون الاستجابة بأسلوب OpenAI على هيئة `{ "object": "list", "data": [ { "id": "Qwen/Qwen3-8B", "owned_by": "Qwen", ... }, ... ] }`.

    عندما تضبط مفتاح API لـ Hugging Face (عبر الإعداد الأولي، أو `HUGGINGFACE_HUB_TOKEN`، أو `HF_TOKEN`)، يستخدم OpenClaw هذا الطلب GET لاكتشاف نماذج إكمال الدردشة المتاحة. أثناء **الإعداد التفاعلي**، بعد إدخال الرمز الخاص بك سترى قائمة منسدلة باسم **Default Hugging Face model** يتم تعبئتها من تلك القائمة (أو من الفهرس المدمج إذا فشل الطلب). أثناء التشغيل (مثل بدء Gateway)، وعند وجود مفتاح، يستدعي OpenClaw مرة أخرى **GET** ‏`https://router.huggingface.co/v1/models` لتحديث الفهرس. يتم دمج القائمة مع فهرس مدمج (لبيانات وصفية مثل نافذة السياق والتكلفة). وإذا فشل الطلب أو لم يتم تعيين مفتاح، فسيتم استخدام الفهرس المدمج فقط.

  </Accordion>

  <Accordion title="أسماء النماذج، والأسماء المستعارة، ولواحق السياسات">
    - **الاسم من API:** يتم **ملء** اسم عرض النموذج من **GET /v1/models** عندما يعيد API الحقول `name` أو `title` أو `display_name`؛ وإلا فسيتم اشتقاقه من معرّف النموذج (مثلًا، يتحول `deepseek-ai/DeepSeek-R1` إلى "DeepSeek R1").
    - **تجاوز اسم العرض:** يمكنك تعيين تسمية مخصصة لكل نموذج بحيث يظهر بالطريقة التي تريدها في CLI وواجهة المستخدم:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1 (fast)" },
            "huggingface/deepseek-ai/DeepSeek-R1:cheapest": { alias: "DeepSeek R1 (cheap)" },
          },
        },
      },
    }
    ```

    - **لواحق السياسات:** تتعامل مستندات وأدوات Hugging Face المدمجة في OpenClaw حاليًا مع هاتين اللاحقتين بوصفهما متغيري السياسة المدمجين:
      - **`:fastest`** — أعلى معدل معالجة.
      - **`:cheapest`** — أقل تكلفة لكل رمز إخراج.

      يمكنك إضافتهما كإدخالات منفصلة في `models.providers.huggingface.models` أو تعيين `model.primary` مع اللاحقة. ويمكنك أيضًا تعيين ترتيب المزود الافتراضي في [Inference Provider settings](https://hf.co/settings/inference-providers) (بدون لاحقة = استخدم ذلك الترتيب).

    - **دمج الإعدادات:** يتم الاحتفاظ بالإدخالات الموجودة في `models.providers.huggingface.models` (مثلًا في `models.json`) عند دمج الإعدادات. لذلك يتم الحفاظ على أي `name` أو `alias` أو خيارات نموذج مخصصة تضبطها هناك.

  </Accordion>

  <Accordion title="البيئة وإعداد daemon">
    إذا كان Gateway يعمل كخدمة daemon ‏(launchd/systemd)، فتأكد من أن `HUGGINGFACE_HUB_TOKEN` أو `HF_TOKEN` متاحان لتلك العملية (على سبيل المثال، في `~/.openclaw/.env` أو عبر `env.shellEnv`).

    <Note>
    يقبل OpenClaw كلاً من `HUGGINGFACE_HUB_TOKEN` و`HF_TOKEN` كأسماء بديلة لمتغير البيئة. أيٌّ منهما يعمل؛ وإذا تم تعيينهما معًا، تكون الأولوية لـ `HUGGINGFACE_HUB_TOKEN`.
    </Note>

  </Accordion>

  <Accordion title="الإعداد: DeepSeek R1 مع بديل احتياطي من Qwen">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-R1",
            fallbacks: ["huggingface/Qwen/Qwen3-8B"],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1" },
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="الإعداد: Qwen مع متغيري cheapest وfastest">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen3-8B" },
          models: {
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
            "huggingface/Qwen/Qwen3-8B:cheapest": { alias: "Qwen3 8B (cheapest)" },
            "huggingface/Qwen/Qwen3-8B:fastest": { alias: "Qwen3 8B (fastest)" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="الإعداد: DeepSeek + Llama + GPT-OSS مع أسماء مستعارة">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-V3.2",
            fallbacks: [
              "huggingface/meta-llama/Llama-3.3-70B-Instruct",
              "huggingface/openai/gpt-oss-120b",
            ],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-V3.2": { alias: "DeepSeek V3.2" },
            "huggingface/meta-llama/Llama-3.3-70B-Instruct": { alias: "Llama 3.3 70B" },
            "huggingface/openai/gpt-oss-120b": { alias: "GPT-OSS 120B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="الإعداد: عدة نماذج Qwen وDeepSeek مع لواحق السياسات">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest" },
          models: {
            "huggingface/Qwen/Qwen2.5-7B-Instruct": { alias: "Qwen2.5 7B" },
            "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest": { alias: "Qwen2.5 7B (cheap)" },
            "huggingface/deepseek-ai/DeepSeek-R1:fastest": { alias: "DeepSeek R1 (fast)" },
            "huggingface/meta-llama/Llama-3.1-8B-Instruct": { alias: "Llama 3.1 8B" },
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="مزودات النماذج" href="/ar/concepts/model-providers" icon="layers">
    نظرة عامة على جميع المزودات، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="اختيار النموذج" href="/ar/concepts/models" icon="brain">
    كيفية اختيار النماذج وإعدادها.
  </Card>
  <Card title="مستندات Inference Providers" href="https://huggingface.co/docs/inference-providers" icon="book">
    مستندات Hugging Face Inference Providers الرسمية.
  </Card>
  <Card title="الإعدادات" href="/ar/gateway/configuration" icon="gear">
    المرجع الكامل للإعدادات.
  </Card>
</CardGroup>
