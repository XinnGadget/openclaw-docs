---
read_when:
    - تريد استخدام Vercel AI Gateway مع OpenClaw
    - تحتاج إلى متغير البيئة لمفتاح API أو خيار مصادقة CLI
summary: إعداد Vercel AI Gateway (المصادقة + اختيار النموذج)
title: Vercel AI Gateway
x-i18n:
    generated_at: "2026-04-12T23:33:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 48c206a645d7a62e201a35ae94232323c8570fdae63129231c38d363ea78a60b
    source_path: providers/vercel-ai-gateway.md
    workflow: 15
---

# Vercel AI Gateway

يوفر [Vercel AI Gateway](https://vercel.com/ai-gateway) واجهة API موحدة للوصول
إلى مئات النماذج عبر نقطة نهاية واحدة.

| الخاصية      | القيمة                           |
| ------------ | -------------------------------- |
| الموفّر      | `vercel-ai-gateway`              |
| المصادقة     | `AI_GATEWAY_API_KEY`             |
| API          | متوافق مع Anthropic Messages     |
| فهرس النماذج | يُكتشف تلقائيًا عبر `/v1/models` |

<Tip>
يكتشف OpenClaw تلقائيًا فهرس Gateway عند `/v1/models`، لذا فإن
`/models vercel-ai-gateway` يتضمن مراجع النماذج الحالية مثل
`vercel-ai-gateway/openai/gpt-5.4`.
</Tip>

## البدء

<Steps>
  <Step title="تعيين مفتاح API">
    شغّل التهيئة واختر خيار مصادقة AI Gateway:

    ```bash
    openclaw onboard --auth-choice ai-gateway-api-key
    ```

  </Step>
  <Step title="تعيين نموذج افتراضي">
    أضف النموذج إلى إعداد OpenClaw لديك:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "vercel-ai-gateway/anthropic/claude-opus-4.6" },
        },
      },
    }
    ```

  </Step>
  <Step title="التحقق من توفر النموذج">
    ```bash
    openclaw models list --provider vercel-ai-gateway
    ```
  </Step>
</Steps>

## مثال غير تفاعلي

بالنسبة إلى الإعدادات المعتمدة على السكربتات أو CI، مرّر جميع القيم في سطر الأوامر:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice ai-gateway-api-key \
  --ai-gateway-api-key "$AI_GATEWAY_API_KEY"
```

## الصيغة المختصرة لمعرّف النموذج

يقبل OpenClaw مراجع نماذج Claude المختصرة الخاصة بـ Vercel ويطبّعها أثناء
وقت التشغيل:

| الإدخال المختصر                      | مرجع النموذج بعد التطبيع                      |
| ------------------------------------ | --------------------------------------------- |
| `vercel-ai-gateway/claude-opus-4.6`  | `vercel-ai-gateway/anthropic/claude-opus-4.6` |
| `vercel-ai-gateway/opus-4.6`         | `vercel-ai-gateway/anthropic/claude-opus-4-6` |

<Tip>
يمكنك استخدام الصيغة المختصرة أو مرجع النموذج المؤهل بالكامل في
إعدادك. ويحل OpenClaw الصيغة القياسية تلقائيًا.
</Tip>

## ملاحظات متقدمة

<AccordionGroup>
  <Accordion title="متغير البيئة لعمليات daemon">
    إذا كانت OpenClaw Gateway تعمل كعملية daemon ‏(launchd/systemd)، فتأكد من أن
    `AI_GATEWAY_API_KEY` متاح لتلك العملية.

    <Warning>
    لن يكون المفتاح المضبوط فقط في `~/.profile` مرئيًا لعملية daemon تعمل عبر launchd/systemd
    ما لم يتم استيراد تلك البيئة صراحةً. اضبط المفتاح في
    `~/.openclaw/.env` أو عبر `env.shellEnv` لضمان أن تتمكن عملية gateway من
    قراءته.
    </Warning>

  </Accordion>

  <Accordion title="توجيه الموفّر">
    يوجّه Vercel AI Gateway الطلبات إلى الموفّر upstream بناءً على بادئة مرجع
    النموذج. على سبيل المثال، يتم توجيه `vercel-ai-gateway/anthropic/claude-opus-4.6`
    عبر Anthropic، بينما يتم توجيه `vercel-ai-gateway/openai/gpt-5.4` عبر
    OpenAI. ويتولى مفتاح `AI_GATEWAY_API_KEY` الواحد المصادقة لجميع
    الموفّرين upstream.
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار الموفّرين، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="استكشاف الأخطاء وإصلاحها" href="/ar/help/troubleshooting" icon="wrench">
    استكشاف الأخطاء وإصلاحها والأسئلة الشائعة العامة.
  </Card>
</CardGroup>
