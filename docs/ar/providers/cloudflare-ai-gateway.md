---
read_when:
    - تريد استخدام Cloudflare AI Gateway مع OpenClaw
    - تحتاج إلى معرّف الحساب أو معرّف Gateway أو متغير البيئة لمفتاح API
summary: إعداد Cloudflare AI Gateway (المصادقة + اختيار النموذج)
title: Cloudflare AI Gateway
x-i18n:
    generated_at: "2026-04-12T23:29:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 12e9589fe74e6a6335370b9cf2361a464876a392a33f8317d7fd30c3f163b2e5
    source_path: providers/cloudflare-ai-gateway.md
    workflow: 15
---

# Cloudflare AI Gateway

تقع Cloudflare AI Gateway أمام واجهات API الخاصة بالمزوّدين وتتيح لك إضافة التحليلات والتخزين المؤقت وعناصر التحكم. بالنسبة إلى Anthropic، يستخدم OpenClaw واجهة Anthropic Messages API عبر نقطة نهاية Gateway الخاصة بك.

| الخاصية      | القيمة                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------- |
| المزوّد      | `cloudflare-ai-gateway`                                                                  |
| عنوان URL الأساسي      | `https://gateway.ai.cloudflare.com/v1/<account_id>/<gateway_id>/anthropic`               |
| النموذج الافتراضي | `cloudflare-ai-gateway/claude-sonnet-4-5`                                                |
| مفتاح API       | `CLOUDFLARE_AI_GATEWAY_API_KEY` (مفتاح API الخاص بالمزوّد لطلبات المرور عبر Gateway) |

<Note>
بالنسبة إلى نماذج Anthropic التي يتم توجيهها عبر Cloudflare AI Gateway، استخدم **مفتاح Anthropic API** الخاص بك كمفتاح للمزوّد.
</Note>

## البدء

<Steps>
  <Step title="عيّن مفتاح API الخاص بالمزوّد وتفاصيل Gateway">
    شغّل الإعداد واختر خيار مصادقة Cloudflare AI Gateway:

    ```bash
    openclaw onboard --auth-choice cloudflare-ai-gateway-api-key
    ```

    سيطلب هذا معرّف الحساب ومعرّف Gateway ومفتاح API.

  </Step>
  <Step title="عيّن نموذجًا افتراضيًا">
    أضف النموذج إلى إعداد OpenClaw الخاص بك:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "cloudflare-ai-gateway/claude-sonnet-4-5" },
        },
      },
    }
    ```

  </Step>
  <Step title="تحقق من أن النموذج متاح">
    ```bash
    openclaw models list --provider cloudflare-ai-gateway
    ```
  </Step>
</Steps>

## مثال غير تفاعلي

لإعدادات السكربتات أو CI، مرّر جميع القيم في سطر الأوامر:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice cloudflare-ai-gateway-api-key \
  --cloudflare-ai-gateway-account-id "your-account-id" \
  --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
  --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY"
```

## الإعداد المتقدم

<AccordionGroup>
  <Accordion title="بوابات Gateway الموثّقة">
    إذا قمت بتمكين مصادقة Gateway في Cloudflare، فأضف الترويسة `cf-aig-authorization`. وهذا يكون **بالإضافة إلى** مفتاح API الخاص بالمزوّد.

    ```json5
    {
      models: {
        providers: {
          "cloudflare-ai-gateway": {
            headers: {
              "cf-aig-authorization": "Bearer <cloudflare-ai-gateway-token>",
            },
          },
        },
      },
    }
    ```

    <Tip>
    تقوم الترويسة `cf-aig-authorization` بالمصادقة مع Cloudflare Gateway نفسها، بينما يقوم مفتاح API الخاص بالمزوّد (على سبيل المثال، مفتاح Anthropic الخاص بك) بالمصادقة مع المزوّد upstream.
    </Tip>

  </Accordion>

  <Accordion title="ملاحظة حول البيئة">
    إذا كان Gateway يعمل كخدمة daemon (`launchd`/`systemd`)، فتأكد من أن `CLOUDFLARE_AI_GATEWAY_API_KEY` متاح لتلك العملية.

    <Warning>
    لن يفيد وجود المفتاح فقط في `~/.profile` خدمة daemon تعمل عبر `launchd`/`systemd` ما لم يتم أيضًا استيراد تلك البيئة هناك. عيّن المفتاح في `~/.openclaw/.env` أو عبر `env.shellEnv` لضمان قدرة عملية gateway على قراءته.
    </Warning>

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدين ومراجع النماذج وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="استكشاف الأخطاء وإصلاحها" href="/ar/help/troubleshooting" icon="wrench">
    استكشاف الأخطاء وإصلاحها بشكل عام والأسئلة الشائعة.
  </Card>
</CardGroup>
