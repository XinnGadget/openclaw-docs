---
read_when:
    - تريد مفتاح API واحدًا للعديد من نماذج LLM
    - تريد تشغيل النماذج عبر Kilo Gateway في OpenClaw
summary: استخدم واجهة Kilo Gateway الموحّدة للوصول إلى العديد من النماذج في OpenClaw
title: Kilocode
x-i18n:
    generated_at: "2026-04-12T23:31:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 32946f2187f3933115341cbe81006718b10583abc4deea7440b5e56366025f4a
    source_path: providers/kilocode.md
    workflow: 15
---

# Kilo Gateway

يوفّر Kilo Gateway **واجهة API موحّدة** توجّه الطلبات إلى العديد من النماذج
خلف نقطة نهاية واحدة ومفتاح API واحد. وهو متوافق مع OpenAI، لذا تعمل معظم
حِزم OpenAI SDK بمجرد تبديل Base URL.

| الخاصية | القيمة                               |
| -------- | ------------------------------------ |
| الموفّر | `kilocode`                           |
| المصادقة | `KILOCODE_API_KEY`                  |
| API      | متوافق مع OpenAI                    |
| Base URL | `https://api.kilo.ai/api/gateway/`  |

## البدء

<Steps>
  <Step title="Create an account">
    انتقل إلى [app.kilo.ai](https://app.kilo.ai)، وسجّل الدخول أو أنشئ حسابًا،
    ثم انتقل إلى API Keys وأنشئ مفتاحًا جديدًا.
  </Step>
  <Step title="Run onboarding">
    ```bash
    openclaw onboard --auth-choice kilocode-api-key
    ```

    أو عيّن متغير البيئة مباشرةً:

    ```bash
    export KILOCODE_API_KEY="<your-kilocode-api-key>" # pragma: allowlist secret
    ```

  </Step>
  <Step title="Verify the model is available">
    ```bash
    openclaw models list --provider kilocode
    ```
  </Step>
</Steps>

## النموذج الافتراضي

النموذج الافتراضي هو `kilocode/kilo/auto`، وهو نموذج توجيه ذكي يملكه الموفّر
وتديره Kilo Gateway.

<Note>
يتعامل OpenClaw مع `kilocode/kilo/auto` باعتباره مرجعًا افتراضيًا مستقرًا، لكنه
لا ينشر ربطًا مدعومًا بالمصدر بين المهام والنماذج الأصلية لهذا المسار. فالتوجيه
الدقيق للنماذج الأصلية خلف `kilocode/kilo/auto` مملوك لـ Kilo Gateway، وليس
مشفّرًا بشكل ثابت داخل OpenClaw.
</Note>

## النماذج المتاحة

يكتشف OpenClaw النماذج المتاحة ديناميكيًا من Kilo Gateway عند بدء التشغيل.
استخدم `/models kilocode` لرؤية القائمة الكاملة للنماذج المتاحة في حسابك.

يمكن استخدام أي نموذج متاح على البوابة مع البادئة `kilocode/`:

| مرجع النموذج                           | ملاحظات                         |
| -------------------------------------- | ------------------------------- |
| `kilocode/kilo/auto`                   | الافتراضي — توجيه ذكي          |
| `kilocode/anthropic/claude-sonnet-4`   | Anthropic عبر Kilo             |
| `kilocode/openai/gpt-5.4`              | OpenAI عبر Kilo                |
| `kilocode/google/gemini-3-pro-preview` | Google عبر Kilo                |
| ...وغيرها الكثير                       | استخدم `/models kilocode` لعرض الجميع |

<Tip>
عند بدء التشغيل، يستعلم OpenClaw عن
`GET https://api.kilo.ai/api/gateway/models`
ويضم النماذج المكتشفة قبل الفهرس الاحتياطي الثابت. ويتضمن الاحتياطي المضمّن
دائمًا `kilocode/kilo/auto` (`Kilo Auto`) مع
`input: ["text", "image"]` و`reasoning: true` و`contextWindow: 1000000`
و`maxTokens: 128000`.
</Tip>

## مثال على الإعداد

```json5
{
  env: { KILOCODE_API_KEY: "<your-kilocode-api-key>" }, // pragma: allowlist secret
  agents: {
    defaults: {
      model: { primary: "kilocode/kilo/auto" },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Transport and compatibility">
    تم توثيق Kilo Gateway في المصدر على أنه متوافق مع OpenRouter، لذا يبقى على
    مسار الوكيل المتوافق مع OpenAI بدلًا من تشكيل الطلبات الأصلي الخاص بـ OpenAI.

    - تبقى مراجع Kilo المدعومة من Gemini على مسار proxy-Gemini، لذلك يحتفظ
      OpenClaw هناك بتنقية thought-signature الخاصة بـ Gemini من دون تفعيل
      التحقق الأصلي من إعادة التشغيل في Gemini أو إعادة كتابة bootstrap.
    - تستخدم Kilo Gateway Bearer token مع مفتاح API الخاص بك في الخلفية.

  </Accordion>

  <Accordion title="Stream wrapper and reasoning">
    يضيف غلاف التدفق المشترك في Kilo ترويسة تطبيق الموفّر ويطبع حمولات
    الاستدلال الخاصة بالوكيل لمراجع النماذج الملموسة المدعومة.

    <Warning>
    يتخطى `kilocode/kilo/auto` وتلميحات الوكيل الأخرى غير المدعومة للاستدلال
    حقن الاستدلال. وإذا كنت بحاجة إلى دعم الاستدلال، فاستخدم مرجع نموذج ملموسًا
    مثل `kilocode/anthropic/claude-sonnet-4`.
    </Warning>

  </Accordion>

  <Accordion title="Troubleshooting">
    - إذا فشل اكتشاف النموذج عند بدء التشغيل، فسيرجع OpenClaw إلى الفهرس الثابت
      المضمّن الذي يحتوي على `kilocode/kilo/auto`.
    - تأكد من أن مفتاح API الخاص بك صالح وأن النماذج المطلوبة مفعّلة في حساب Kilo.
    - عندما يعمل Gateway كخدمة daemon، تأكد من أن `KILOCODE_API_KEY` متاح
      لتلك العملية أيضًا (مثلًا في `~/.openclaw/.env` أو عبر `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="Model selection" href="/ar/concepts/model-providers" icon="layers">
    اختيار الموفّرات، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="Configuration reference" href="/ar/gateway/configuration" icon="gear">
    المرجع الكامل لإعدادات OpenClaw.
  </Card>
  <Card title="Kilo Gateway" href="https://app.kilo.ai" icon="arrow-up-right-from-square">
    لوحة تحكم Kilo Gateway، ومفاتيح API، وإدارة الحساب.
  </Card>
</CardGroup>
