---
read_when:
    - تريد استخدام Fireworks مع OpenClaw
    - تحتاج إلى متغير البيئة الخاص بمفتاح API لـ Fireworks أو معرّف النموذج الافتراضي
summary: إعداد Fireworks (المصادقة + اختيار النموذج)
title: Fireworks
x-i18n:
    generated_at: "2026-04-12T23:30:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1a85d9507c19e275fdd846a303d844eda8045d008774d4dde1eae408e8716b6f
    source_path: providers/fireworks.md
    workflow: 15
---

# Fireworks

توفّر [Fireworks](https://fireworks.ai) نماذج مفتوحة الأوزان ونماذج موجهة عبر API
متوافق مع OpenAI. ويتضمن OpenClaw Plugin موفّر Fireworks مضمّنًا.

| الخاصية         | القيمة                                                   |
| --------------- | -------------------------------------------------------- |
| الموفّر         | `fireworks`                                              |
| المصادقة        | `FIREWORKS_API_KEY`                                      |
| API             | chat/completions متوافق مع OpenAI                        |
| Base URL        | `https://api.fireworks.ai/inference/v1`                  |
| النموذج الافتراضي | `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` |

## البدء

<Steps>
  <Step title="Set up Fireworks auth through onboarding">
    ```bash
    openclaw onboard --auth-choice fireworks-api-key
    ```

    يخزّن هذا مفتاح Fireworks الخاص بك في إعدادات OpenClaw ويعيّن نموذج Fire Pass
    الابتدائي كنموذج افتراضي.

  </Step>
  <Step title="Verify the model is available">
    ```bash
    openclaw models list --provider fireworks
    ```
  </Step>
</Steps>

## مثال غير تفاعلي

لإعدادات السكربتات أو CI، مرّر جميع القيم في سطر الأوامر:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice fireworks-api-key \
  --fireworks-api-key "$FIREWORKS_API_KEY" \
  --skip-health \
  --accept-risk
```

## الفهرس المضمّن

| مرجع النموذج                                         | الاسم                        | الإدخال    | السياق   | الحد الأقصى للإخراج | ملاحظات                                   |
| ---------------------------------------------------- | --------------------------- | ---------- | -------- | ------------------- | ----------------------------------------- |
| `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` | Kimi K2.5 Turbo (Fire Pass) | نص، صورة   | 256,000  | 256,000             | النموذج الابتدائي المضمّن الافتراضي على Fireworks |

<Tip>
إذا نشرت Fireworks نموذجًا أحدث مثل إصدار جديد من Qwen أو Gemma، فيمكنك التبديل إليه مباشرةً باستخدام معرّف نموذج Fireworks الخاص به من دون انتظار تحديث الفهرس المضمّن.
</Tip>

## معرّفات نماذج Fireworks المخصصة

يقبل OpenClaw أيضًا معرّفات نماذج Fireworks الديناميكية. استخدم معرّف النموذج أو
الموجّه الدقيق كما يظهر في Fireworks، وأضف البادئة `fireworks/` إليه.

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "fireworks/accounts/fireworks/routers/kimi-k2p5-turbo",
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="How model id prefixing works">
    يبدأ كل مرجع نموذج Fireworks في OpenClaw بالبادئة `fireworks/` متبوعة
    بالمعرّف الدقيق أو مسار الموجّه من منصة Fireworks. على سبيل المثال:

    - نموذج موجّه: `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo`
    - نموذج مباشر: `fireworks/accounts/fireworks/models/<model-name>`

    يزيل OpenClaw البادئة `fireworks/` عند إنشاء طلب API ويرسل المسار المتبقي
    إلى نقطة نهاية Fireworks.

  </Accordion>

  <Accordion title="Environment note">
    إذا كان Gateway يعمل خارج بيئة shell التفاعلية لديك، فتأكد من أن
    `FIREWORKS_API_KEY` متاح لتلك العملية أيضًا.

    <Warning>
    لن يفيد المفتاح الموجود فقط في `~/.profile` خدمة daemon تعمل عبر
    launchd/systemd ما لم يتم استيراد تلك البيئة هناك أيضًا. عيّن المفتاح في
    `~/.openclaw/.env` أو عبر `env.shellEnv` لضمان قدرة عملية Gateway على قراءته.
    </Warning>

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="Model selection" href="/ar/concepts/model-providers" icon="layers">
    اختيار الموفّرات، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="Troubleshooting" href="/ar/help/troubleshooting" icon="wrench">
    استكشاف الأخطاء وإصلاحها والأسئلة الشائعة العامة.
  </Card>
</CardGroup>
