---
read_when:
    - تريد استخدام DeepSeek مع OpenClaw
    - تحتاج إلى متغير البيئة الخاص بمفتاح API أو خيار المصادقة عبر CLI
summary: إعداد DeepSeek (المصادقة + اختيار النموذج)
title: DeepSeek
x-i18n:
    generated_at: "2026-04-12T23:30:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad06880bd1ab89f72f9e31f4927e2c099dcf6b4e0ff2b3fcc91a24468fbc089d
    source_path: providers/deepseek.md
    workflow: 15
---

# DeepSeek

يوفّر [DeepSeek](https://www.deepseek.com) نماذج ذكاء اصطناعي قوية مع API متوافق مع OpenAI.

| الخاصية | القيمة                     |
| ------- | -------------------------- |
| الموفّر | `deepseek`                 |
| المصادقة | `DEEPSEEK_API_KEY`        |
| API     | متوافق مع OpenAI          |
| Base URL | `https://api.deepseek.com` |

## البدء

<Steps>
  <Step title="Get your API key">
    أنشئ مفتاح API من [platform.deepseek.com](https://platform.deepseek.com/api_keys).
  </Step>
  <Step title="Run onboarding">
    ```bash
    openclaw onboard --auth-choice deepseek-api-key
    ```

    سيطلب هذا مفتاح API الخاص بك ويعيّن `deepseek/deepseek-chat` كنموذج افتراضي.

  </Step>
  <Step title="Verify models are available">
    ```bash
    openclaw models list --provider deepseek
    ```
  </Step>
</Steps>

<AccordionGroup>
  <Accordion title="Non-interactive setup">
    لعمليات التثبيت المؤتمتة أو غير التفاعلية، مرّر جميع الأعلام مباشرةً:

    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice deepseek-api-key \
      --deepseek-api-key "$DEEPSEEK_API_KEY" \
      --skip-health \
      --accept-risk
    ```

  </Accordion>
</AccordionGroup>

<Warning>
إذا كان Gateway يعمل كخدمة daemon (`launchd/systemd`)، فتأكد من أن `DEEPSEEK_API_KEY`
متاح لتلك العملية (على سبيل المثال، في `~/.openclaw/.env` أو عبر
`env.shellEnv`).
</Warning>

## الفهرس المضمّن

| مرجع النموذج                  | الاسم             | الإدخال | السياق   | الحد الأقصى للإخراج | ملاحظات                                             |
| ---------------------------- | ----------------- | ------- | -------- | ------------------- | --------------------------------------------------- |
| `deepseek/deepseek-chat`     | DeepSeek Chat     | نص      | 131,072  | 8,192               | النموذج الافتراضي؛ واجهة DeepSeek V3.2 غير الاستدلالية |
| `deepseek/deepseek-reasoner` | DeepSeek Reasoner | نص      | 131,072  | 65,536              | واجهة V3.2 مع تمكين الاستدلال                        |

<Tip>
يعلن كلا النموذجين المضمّنين حاليًا في المصدر عن توافق مع الاستخدام المتدفق.
</Tip>

## مثال على الإعداد

```json5
{
  env: { DEEPSEEK_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "deepseek/deepseek-chat" },
    },
  },
}
```

## ذو صلة

<CardGroup cols={2}>
  <Card title="Model selection" href="/ar/concepts/model-providers" icon="layers">
    اختيار الموفّرات، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="Configuration reference" href="/ar/gateway/configuration-reference" icon="gear">
    المرجع الكامل لإعدادات الوكلاء والنماذج والموفّرات.
  </Card>
</CardGroup>
