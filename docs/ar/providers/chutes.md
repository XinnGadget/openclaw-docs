---
read_when:
    - تريد استخدام Chutes مع OpenClaw
    - تحتاج إلى مسار إعداد OAuth أو مفتاح API
    - تريد النموذج الافتراضي أو الأسماء المستعارة أو سلوك الاكتشاف
summary: إعداد Chutes (OAuth أو مفتاح API، واكتشاف النماذج، والأسماء المستعارة)
title: Chutes
x-i18n:
    generated_at: "2026-04-12T23:29:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 07c52b1d1d2792412e6daabc92df5310434b3520116d9e0fd2ad26bfa5297e1c
    source_path: providers/chutes.md
    workflow: 15
---

# Chutes

توفّر [Chutes](https://chutes.ai) كتالوجات نماذج مفتوحة المصدر عبر
OpenAI-compatible API. يدعم OpenClaw كلًا من OAuth عبر المتصفح ومصادقة
مفتاح API المباشرة للمزوّد المضمّن `chutes`.

| الخاصية | القيمة                        |
| -------- | ---------------------------- |
| المزوّد | `chutes`                     |
| API      | متوافق مع OpenAI            |
| عنوان URL الأساسي | `https://llm.chutes.ai/v1`   |
| المصادقة     | OAuth أو مفتاح API (انظر أدناه) |

## البدء

<Tabs>
  <Tab title="OAuth">
    <Steps>
      <Step title="شغّل تدفق إعداد OAuth">
        ```bash
        openclaw onboard --auth-choice chutes
        ```
        يطلق OpenClaw تدفق المتصفح محليًا، أو يعرض تدفق عنوان URL + لصق إعادة التوجيه
        على المضيفات البعيدة أو عديمة الواجهة. يتم تحديث رموز OAuth تلقائيًا عبر ملفات
        المصادقة الشخصية في OpenClaw.
      </Step>
      <Step title="تحقق من النموذج الافتراضي">
        بعد الإعداد، يتم تعيين النموذج الافتراضي إلى
        `chutes/zai-org/GLM-4.7-TEE` ويتم تسجيل كتالوج Chutes
        المضمّن.
      </Step>
    </Steps>
  </Tab>
  <Tab title="مفتاح API">
    <Steps>
      <Step title="احصل على مفتاح API">
        أنشئ مفتاحًا في
        [chutes.ai/settings/api-keys](https://chutes.ai/settings/api-keys).
      </Step>
      <Step title="شغّل تدفق إعداد مفتاح API">
        ```bash
        openclaw onboard --auth-choice chutes-api-key
        ```
      </Step>
      <Step title="تحقق من النموذج الافتراضي">
        بعد الإعداد، يتم تعيين النموذج الافتراضي إلى
        `chutes/zai-org/GLM-4.7-TEE` ويتم تسجيل كتالوج Chutes
        المضمّن.
      </Step>
    </Steps>
  </Tab>
</Tabs>

<Note>
يسجّل كلا مساري المصادقة كتالوج Chutes المضمّن ويضبطان النموذج الافتراضي على
`chutes/zai-org/GLM-4.7-TEE`. متغيرات البيئة في وقت التشغيل: `CHUTES_API_KEY`،
`CHUTES_OAUTH_TOKEN`.
</Note>

## سلوك الاكتشاف

عندما تتوفر مصادقة Chutes، يستعلم OpenClaw عن كتالوج Chutes باستخدام
بيانات الاعتماد تلك ويستخدم النماذج المكتشفة. وإذا فشل الاكتشاف، يعود OpenClaw
إلى كتالوج ثابت مضمّن حتى يظل الإعداد والتشغيل عند البدء يعملان.

## الأسماء المستعارة الافتراضية

يسجّل OpenClaw ثلاثة أسماء مستعارة مريحة لكتالوج Chutes المضمّن:

| الاسم المستعار | النموذج الهدف                                          |
| --------------- | ----------------------------------------------------- |
| `chutes-fast`   | `chutes/zai-org/GLM-4.7-FP8`                          |
| `chutes-pro`    | `chutes/deepseek-ai/DeepSeek-V3.2-TEE`                |
| `chutes-vision` | `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506` |

## كتالوج البداية المضمّن

يتضمن كتالوج الرجوع الاحتياطي المضمّن مراجع Chutes الحالية:

| مرجع النموذج                                             |
| ----------------------------------------------------- |
| `chutes/zai-org/GLM-4.7-TEE`                          |
| `chutes/zai-org/GLM-5-TEE`                            |
| `chutes/deepseek-ai/DeepSeek-V3.2-TEE`                |
| `chutes/deepseek-ai/DeepSeek-R1-0528-TEE`             |
| `chutes/moonshotai/Kimi-K2.5-TEE`                     |
| `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506` |
| `chutes/Qwen/Qwen3-Coder-Next-TEE`                    |
| `chutes/openai/gpt-oss-120b-TEE`                      |

## مثال على الإعداد

```json5
{
  agents: {
    defaults: {
      model: { primary: "chutes/zai-org/GLM-4.7-TEE" },
      models: {
        "chutes/zai-org/GLM-4.7-TEE": { alias: "Chutes GLM 4.7" },
        "chutes/deepseek-ai/DeepSeek-V3.2-TEE": { alias: "Chutes DeepSeek V3.2" },
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="تجاوزات OAuth">
    يمكنك تخصيص تدفق OAuth باستخدام متغيرات بيئة اختيارية:

    | المتغير | الغرض |
    | -------- | ------- |
    | `CHUTES_CLIENT_ID` | معرّف عميل OAuth مخصص |
    | `CHUTES_CLIENT_SECRET` | سر عميل OAuth مخصص |
    | `CHUTES_OAUTH_REDIRECT_URI` | URI مخصص لإعادة التوجيه |
    | `CHUTES_OAUTH_SCOPES` | نطاقات OAuth مخصصة |

    راجع [مستندات Chutes OAuth](https://chutes.ai/docs/sign-in-with-chutes/overview)
    لمعرفة متطلبات تطبيق إعادة التوجيه والمساعدة.

  </Accordion>

  <Accordion title="ملاحظات">
    - يستخدم كل من اكتشاف مفتاح API وOAuth معرّف المزوّد نفسه `chutes`.
    - يتم تسجيل نماذج Chutes بصيغة `chutes/<model-id>`.
    - إذا فشل الاكتشاف عند بدء التشغيل، يتم استخدام الكتالوج الثابت المضمّن تلقائيًا.
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="مزوّدو النماذج" href="/ar/concepts/model-providers" icon="layers">
    قواعد المزوّدين ومراجع النماذج وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference" icon="gear">
    مخطط الإعداد الكامل بما في ذلك إعدادات المزوّد.
  </Card>
  <Card title="Chutes" href="https://chutes.ai" icon="arrow-up-right-from-square">
    لوحة معلومات Chutes ووثائق API.
  </Card>
  <Card title="مفاتيح API لـ Chutes" href="https://chutes.ai/settings/api-keys" icon="key">
    أنشئ مفاتيح API لـ Chutes وأدرها.
  </Card>
</CardGroup>
