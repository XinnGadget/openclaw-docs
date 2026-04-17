---
read_when:
    - تريد استخدام نماذج OSS المستضافة على Bedrock Mantle مع OpenClaw
    - تحتاج إلى نقطة نهاية Mantle المتوافقة مع OpenAI لنماذج GPT-OSS أو Qwen أو Kimi أو GLM
summary: استخدم نماذج Amazon Bedrock Mantle (المتوافقة مع OpenAI) مع OpenClaw
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-12T23:29:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27e602b6f6a3ae92427de135cb9df6356e0daaea6b6fe54723a7542dd0d5d21e
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

يتضمن OpenClaw موفّر **Amazon Bedrock Mantle** مضمّنًا يتصل بنقطة نهاية Mantle
المتوافقة مع OpenAI. تستضيف Mantle نماذج مفتوحة المصدر ونماذج من جهات خارجية
(GPT-OSS وQwen وKimi وGLM وما شابه) عبر واجهة قياسية
`/v1/chat/completions` مدعومة ببنية Bedrock التحتية.

| الخاصية        | القيمة                                                                              |
| -------------- | ----------------------------------------------------------------------------------- |
| معرّف الموفّر  | `amazon-bedrock-mantle`                                                             |
| API            | `openai-completions` (متوافق مع OpenAI)                                             |
| المصادقة       | `AWS_BEARER_TOKEN_BEDROCK` صريح أو إنشاء bearer token من سلسلة بيانات اعتماد IAM   |
| المنطقة الافتراضية | `us-east-1` (يمكن تجاوزها باستخدام `AWS_REGION` أو `AWS_DEFAULT_REGION`)       |

## البدء

اختر طريقة المصادقة المفضلة لديك واتبع خطوات الإعداد.

<Tabs>
  <Tab title="Explicit bearer token">
    **الأفضل لـ:** البيئات التي لديك فيها بالفعل bearer token لـ Mantle.

    <Steps>
      <Step title="Set the bearer token on the gateway host">
        ```bash
        export AWS_BEARER_TOKEN_BEDROCK="..."
        ```

        اختياريًا، عيّن منطقة (الافتراضية هي `us-east-1`):

        ```bash
        export AWS_REGION="us-west-2"
        ```
      </Step>
      <Step title="Verify models are discovered">
        ```bash
        openclaw models list
        ```

        تظهر النماذج المكتشفة تحت الموفّر `amazon-bedrock-mantle`. ولا يلزم أي
        إعداد إضافي ما لم تكن تريد تجاوز القيم الافتراضية.
      </Step>
    </Steps>

  </Tab>

  <Tab title="IAM credentials">
    **الأفضل لـ:** استخدام بيانات اعتماد متوافقة مع AWS SDK (الإعدادات المشتركة، وSSO، وweb identity، أو أدوار المثيل أو المهام).

    <Steps>
      <Step title="Configure AWS credentials on the gateway host">
        يعمل أي مصدر مصادقة متوافق مع AWS SDK:

        ```bash
        export AWS_PROFILE="default"
        export AWS_REGION="us-west-2"
        ```
      </Step>
      <Step title="Verify models are discovered">
        ```bash
        openclaw models list
        ```

        ينشئ OpenClaw bearer token لـ Mantle من سلسلة بيانات الاعتماد تلقائيًا.
      </Step>
    </Steps>

    <Tip>
    عندما لا يكون `AWS_BEARER_TOKEN_BEDROCK` معيّنًا، ينشئ OpenClaw bearer token نيابةً عنك من سلسلة بيانات الاعتماد الافتراضية لـ AWS، بما في ذلك بيانات الاعتماد/ملفات الإعداد المشتركة، وSSO، وweb identity، أو أدوار المثيل أو المهام.
    </Tip>

  </Tab>
</Tabs>

## الاكتشاف التلقائي للنماذج

عند تعيين `AWS_BEARER_TOKEN_BEDROCK`، يستخدمه OpenClaw مباشرةً. بخلاف ذلك،
يحاول OpenClaw إنشاء bearer token لـ Mantle من سلسلة بيانات الاعتماد
الافتراضية لـ AWS. ثم يكتشف نماذج Mantle المتاحة عبر الاستعلام عن نقطة النهاية
`/v1/models` الخاصة بالمنطقة.

| السلوك             | التفاصيل                    |
| ------------------ | --------------------------- |
| ذاكرة التخزين المؤقت للاكتشاف | تُخزَّن النتائج مؤقتًا لمدة ساعة واحدة |
| تحديث IAM token    | كل ساعة                     |

<Note>
إن bearer token هو نفسه `AWS_BEARER_TOKEN_BEDROCK` المستخدم بواسطة موفّر [Amazon Bedrock](/ar/providers/bedrock) القياسي.
</Note>

### المناطق المدعومة

`us-east-1` و`us-east-2` و`us-west-2` و`ap-northeast-1`،
و`ap-south-1` و`ap-southeast-3` و`eu-central-1` و`eu-west-1` و`eu-west-2`،
و`eu-south-1` و`eu-north-1` و`sa-east-1`.

## الإعداد اليدوي

إذا كنت تفضل إعدادًا صريحًا بدلًا من الاكتشاف التلقائي:

```json5
{
  models: {
    providers: {
      "amazon-bedrock-mantle": {
        baseUrl: "https://bedrock-mantle.us-east-1.api.aws/v1",
        api: "openai-completions",
        auth: "api-key",
        apiKey: "env:AWS_BEARER_TOKEN_BEDROCK",
        models: [
          {
            id: "gpt-oss-120b",
            name: "GPT-OSS 120B",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 32000,
            maxTokens: 4096,
          },
        ],
      },
    },
  },
}
```

## ملاحظات متقدمة

<AccordionGroup>
  <Accordion title="Reasoning support">
    يُستدل على دعم الاستدلال من معرّفات النماذج التي تحتوي على أنماط مثل
    `thinking` أو `reasoner` أو `gpt-oss-120b`. ويعيّن OpenClaw
    `reasoning: true` تلقائيًا للنماذج المطابقة أثناء الاكتشاف.
  </Accordion>

  <Accordion title="Endpoint unavailability">
    إذا كانت نقطة نهاية Mantle غير متاحة أو لم تُرجع أي نماذج، فسيتم
    تخطي الموفّر بصمت. ولن يُظهر OpenClaw خطأ؛ وستستمر الموفّرات الأخرى
    المهيأة في العمل كالمعتاد.
  </Accordion>

  <Accordion title="Relationship to Amazon Bedrock provider">
    يُعد Bedrock Mantle موفّرًا منفصلًا عن موفّر
    [Amazon Bedrock](/ar/providers/bedrock) القياسي. يستخدم Mantle واجهة
    `/v1` متوافقة مع OpenAI، بينما يستخدم موفّر Bedrock القياسي
    Bedrock API الأصلية.

    يشترك كلا الموفّرين في بيانات الاعتماد نفسها `AWS_BEARER_TOKEN_BEDROCK`
    عند وجودها.

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="Amazon Bedrock" href="/ar/providers/bedrock" icon="cloud">
    موفّر Bedrock الأصلي لنماذج Anthropic Claude وTitan ونماذج أخرى.
  </Card>
  <Card title="Model selection" href="/ar/concepts/model-providers" icon="layers">
    اختيار الموفّرات، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="OAuth and auth" href="/ar/gateway/authentication" icon="key">
    تفاصيل المصادقة وقواعد إعادة استخدام بيانات الاعتماد.
  </Card>
  <Card title="Troubleshooting" href="/ar/help/troubleshooting" icon="wrench">
    المشكلات الشائعة وكيفية حلها.
  </Card>
</CardGroup>
