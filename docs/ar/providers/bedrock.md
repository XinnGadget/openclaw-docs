---
read_when:
    - تريد استخدام نماذج Amazon Bedrock مع OpenClaw
    - تحتاج إلى إعداد بيانات اعتماد AWS/المنطقة لإجراء استدعاءات النماذج
summary: استخدم نماذج Amazon Bedrock ‏(Converse API) مع OpenClaw
title: Amazon Bedrock
x-i18n:
    generated_at: "2026-04-12T23:29:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 88e7e24907ec26af098b648e2eeca32add090a9e381c818693169ab80aeccc47
    source_path: providers/bedrock.md
    workflow: 15
---

# Amazon Bedrock

يمكن لـ OpenClaw استخدام نماذج **Amazon Bedrock** عبر مزود البث **Bedrock Converse**
الخاص بـ pi-ai. تستخدم مصادقة Bedrock **سلسلة بيانات الاعتماد الافتراضية في AWS SDK**،
وليس مفتاح API.

| الخاصية | القيمة                                                        |
| -------- | ------------------------------------------------------------- |
| المزود | `amazon-bedrock`                                              |
| API      | `bedrock-converse-stream`                                     |
| المصادقة | بيانات اعتماد AWS (متغيرات البيئة، أو الإعدادات المشتركة، أو دور المثيل) |
| المنطقة | `AWS_REGION` أو `AWS_DEFAULT_REGION` (الافتراضي: `us-east-1`) |

## البدء

اختر طريقة المصادقة المفضلة لديك واتبع خطوات الإعداد.

<Tabs>
  <Tab title="مفاتيح الوصول / متغيرات البيئة">
    **الأفضل لـ:** أجهزة المطورين، وCI، أو المضيفين الذين تدير عليهم بيانات اعتماد AWS مباشرة.

    <Steps>
      <Step title="تعيين بيانات اعتماد AWS على مضيف Gateway">
        ```bash
        export AWS_ACCESS_KEY_ID="AKIA..."
        export AWS_SECRET_ACCESS_KEY="..."
        export AWS_REGION="us-east-1"
        # اختياري:
        export AWS_SESSION_TOKEN="..."
        export AWS_PROFILE="your-profile"
        # اختياري (مفتاح API/رمز Bearer لـ Bedrock):
        export AWS_BEARER_TOKEN_BEDROCK="..."
        ```
      </Step>
      <Step title="إضافة مزود Bedrock ونموذج إلى إعداداتك">
        لا يلزم `apiKey`. قم بإعداد المزود باستخدام `auth: "aws-sdk"`:

        ```json5
        {
          models: {
            providers: {
              "amazon-bedrock": {
                baseUrl: "https://bedrock-runtime.us-east-1.amazonaws.com",
                api: "bedrock-converse-stream",
                auth: "aws-sdk",
                models: [
                  {
                    id: "us.anthropic.claude-opus-4-6-v1:0",
                    name: "Claude Opus 4.6 (Bedrock)",
                    reasoning: true,
                    input: ["text", "image"],
                    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                    contextWindow: 200000,
                    maxTokens: 8192,
                  },
                ],
              },
            },
          },
          agents: {
            defaults: {
              model: { primary: "amazon-bedrock/us.anthropic.claude-opus-4-6-v1:0" },
            },
          },
        }
        ```
      </Step>
      <Step title="التحقق من توفر النماذج">
        ```bash
        openclaw models list
        ```
      </Step>
    </Steps>

    <Tip>
    مع مصادقة علامات البيئة (`AWS_ACCESS_KEY_ID` أو `AWS_PROFILE` أو `AWS_BEARER_TOKEN_BEDROCK`)، يقوم OpenClaw بتمكين مزود Bedrock الضمني تلقائيًا لاكتشاف النماذج دون إعدادات إضافية.
    </Tip>

  </Tab>

  <Tab title="أدوار مثيلات EC2 ‏(IMDS)">
    **الأفضل لـ:** مثيلات EC2 التي تم إرفاق دور IAM بها، باستخدام خدمة بيانات تعريف المثيل للمصادقة.

    <Steps>
      <Step title="تمكين الاكتشاف صراحةً">
        عند استخدام IMDS، لا يستطيع OpenClaw اكتشاف مصادقة AWS من علامات البيئة وحدها، لذلك يجب عليك الاشتراك صراحةً:

        ```bash
        openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
        openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1
        ```
      </Step>
      <Step title="إضافة علامة بيئة اختياريًا لوضع الاكتشاف التلقائي">
        إذا كنت تريد أيضًا أن يعمل مسار الاكتشاف التلقائي بعلامات البيئة (على سبيل المثال، لواجهات `openclaw status`):

        ```bash
        export AWS_PROFILE=default
        export AWS_REGION=us-east-1
        ```

        **لا** تحتاج إلى مفتاح API وهمي.
      </Step>
      <Step title="التحقق من اكتشاف النماذج">
        ```bash
        openclaw models list
        ```
      </Step>
    </Steps>

    <Warning>
    يجب أن يمتلك دور IAM المرفق بمثيل EC2 الأذونات التالية:

    - `bedrock:InvokeModel`
    - `bedrock:InvokeModelWithResponseStream`
    - `bedrock:ListFoundationModels` (للاكتشاف التلقائي)
    - `bedrock:ListInferenceProfiles` (لاكتشاف ملفات تعريف الاستدلال)

    أو قم بإرفاق السياسة المُدارة `AmazonBedrockFullAccess`.
    </Warning>

    <Note>
    تحتاج إلى `AWS_PROFILE=default` فقط إذا كنت تريد تحديدًا علامة بيئة لوضع الاكتشاف التلقائي أو لواجهات الحالة. أما مسار مصادقة Bedrock الفعلي أثناء التشغيل فيستخدم سلسلة AWS SDK الافتراضية، لذلك تعمل مصادقة دور المثيل عبر IMDS حتى بدون علامات بيئة.
    </Note>

  </Tab>
</Tabs>

## الاكتشاف التلقائي للنماذج

يمكن لـ OpenClaw اكتشاف نماذج Bedrock التي تدعم **البث**
و**إخراج النص** تلقائيًا. يستخدم الاكتشاف `bedrock:ListFoundationModels` و
`bedrock:ListInferenceProfiles`، ويتم تخزين النتائج مؤقتًا (الافتراضي: ساعة واحدة).

كيفية تمكين المزود الضمني:

- إذا كانت `plugins.entries.amazon-bedrock.config.discovery.enabled` تساوي `true`،
  فسيحاول OpenClaw الاكتشاف حتى عند عدم وجود علامة بيئة AWS.
- إذا لم يتم تعيين `plugins.entries.amazon-bedrock.config.discovery.enabled`،
  فلن يضيف OpenClaw
  مزود Bedrock الضمني تلقائيًا إلا عندما يرى أحد علامات مصادقة AWS التالية:
  `AWS_BEARER_TOKEN_BEDROCK`، أو `AWS_ACCESS_KEY_ID` +
  `AWS_SECRET_ACCESS_KEY`، أو `AWS_PROFILE`.
- لا يزال مسار مصادقة Bedrock الفعلي أثناء التشغيل يستخدم سلسلة AWS SDK الافتراضية، لذلك
  يمكن أن تعمل الإعدادات المشتركة، وSSO، ومصادقة دور المثيل عبر IMDS حتى عندما كان
  الاكتشاف يحتاج إلى `enabled: true` للاشتراك.

<Note>
بالنسبة إلى إدخالات `models.providers["amazon-bedrock"]` الصريحة، لا يزال بإمكان OpenClaw حل مصادقة Bedrock المبكرة القائمة على علامات البيئة من متغيرات AWS البيئية مثل `AWS_BEARER_TOKEN_BEDROCK` دون فرض تحميل مصادقة التشغيل الكاملة. أما مسار مصادقة استدعاء النموذج الفعلي فيستخدم سلسلة AWS SDK الافتراضية.
</Note>

<AccordionGroup>
  <Accordion title="خيارات إعدادات الاكتشاف">
    توجد خيارات الإعداد ضمن `plugins.entries.amazon-bedrock.config.discovery`:

    ```json5
    {
      plugins: {
        entries: {
          "amazon-bedrock": {
            config: {
              discovery: {
                enabled: true,
                region: "us-east-1",
                providerFilter: ["anthropic", "amazon"],
                refreshInterval: 3600,
                defaultContextWindow: 32000,
                defaultMaxTokens: 4096,
              },
            },
          },
        },
      },
    }
    ```

    | الخيار | الافتراضي | الوصف |
    | ------ | --------- | ------ |
    | `enabled` | auto | في الوضع التلقائي، لا يفعّل OpenClaw مزود Bedrock الضمني إلا عندما يرى علامة بيئة AWS مدعومة. عيّنه إلى `true` لفرض الاكتشاف. |
    | `region` | `AWS_REGION` / `AWS_DEFAULT_REGION` / `us-east-1` | منطقة AWS المستخدمة في استدعاءات API الخاصة بالاكتشاف. |
    | `providerFilter` | (الكل) | يطابق أسماء مزودي Bedrock (على سبيل المثال `anthropic`، `amazon`). |
    | `refreshInterval` | `3600` | مدة التخزين المؤقت بالثواني. عيّنه إلى `0` لتعطيل التخزين المؤقت. |
    | `defaultContextWindow` | `32000` | نافذة السياق المستخدمة للنماذج المكتشفة (جاوزها إذا كنت تعرف حدود نموذجك). |
    | `defaultMaxTokens` | `4096` | الحد الأقصى لرموز الإخراج المستخدمة للنماذج المكتشفة (جاوزها إذا كنت تعرف حدود نموذجك). |

  </Accordion>
</AccordionGroup>

## إعداد سريع (مسار AWS)

ينشئ هذا الدليل دور IAM، ويرفق أذونات Bedrock، ويربط
ملف تعريف المثيل، ويمكّن اكتشاف OpenClaw على مضيف EC2.

```bash
# 1. Create IAM role and instance profile
aws iam create-role --role-name EC2-Bedrock-Access \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy --role-name EC2-Bedrock-Access \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam create-instance-profile --instance-profile-name EC2-Bedrock-Access
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-Bedrock-Access \
  --role-name EC2-Bedrock-Access

# 2. Attach to your EC2 instance
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. On the EC2 instance, enable discovery explicitly
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 4. Optional: add an env marker if you want auto mode without explicit enable
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. Verify models are discovered
openclaw models list
```

## إعدادات متقدمة

<AccordionGroup>
  <Accordion title="ملفات تعريف الاستدلال">
    يكتشف OpenClaw **ملفات تعريف الاستدلال الإقليمية والعالمية** إلى جانب
    النماذج الأساسية. عندما يطابق ملف تعريف نموذجًا أساسيًا معروفًا، يرث
    ملف التعريف إمكانات ذلك النموذج (نافذة السياق، الحد الأقصى للرموز،
    التفكير، والرؤية) ويتم حقن منطقة طلب Bedrock الصحيحة
    تلقائيًا. وهذا يعني أن ملفات تعريف Claude عبر المناطق تعمل دون
    تجاوزات يدوية للمزود.

    تبدو معرّفات ملفات تعريف الاستدلال مثل `us.anthropic.claude-opus-4-6-v1:0` (إقليمي)
    أو `anthropic.claude-opus-4-6-v1:0` (عالمي). إذا كان النموذج الداعم موجودًا بالفعل
    في نتائج الاكتشاف، فإن ملف التعريف يرث مجموعة إمكاناته الكاملة؛
    وإلا تُطبَّق افتراضيات آمنة.

    لا حاجة إلى إعدادات إضافية. طالما أن الاكتشاف مفعّل وأن كيان IAM
    يمتلك `bedrock:ListInferenceProfiles`، فستظهر ملفات التعريف إلى جانب
    النماذج الأساسية في `openclaw models list`.

  </Accordion>

  <Accordion title="Guardrails">
    يمكنك تطبيق [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
    على جميع استدعاءات نماذج Bedrock عن طريق إضافة كائن `guardrail` إلى
    إعدادات Plugin ‏`amazon-bedrock`. تتيح لك Guardrails فرض تصفية المحتوى،
    وحظر الموضوعات، ومرشحات الكلمات، ومرشحات المعلومات الحساسة، وعمليات التحقق
    من الارتكاز السياقي.

    ```json5
    {
      plugins: {
        entries: {
          "amazon-bedrock": {
            config: {
              guardrail: {
                guardrailIdentifier: "abc123", // guardrail ID or full ARN
                guardrailVersion: "1", // version number or "DRAFT"
                streamProcessingMode: "sync", // optional: "sync" or "async"
                trace: "enabled", // optional: "enabled", "disabled", or "enabled_full"
              },
            },
          },
        },
      },
    }
    ```

    | الخيار | مطلوب | الوصف |
    | ------ | ------ | ------ |
    | `guardrailIdentifier` | نعم | معرّف Guardrail (مثل `abc123`) أو ARN كامل (مثل `arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123`). |
    | `guardrailVersion` | نعم | رقم الإصدار المنشور، أو `"DRAFT"` لمسودة العمل. |
    | `streamProcessingMode` | لا | `"sync"` أو `"async"` لتقييم Guardrail أثناء البث. إذا تم حذفه، يستخدم Bedrock الإعداد الافتراضي الخاص به. |
    | `trace` | لا | `"enabled"` أو `"enabled_full"` لأغراض التصحيح؛ احذفه أو عيّنه إلى `"disabled"` في بيئات الإنتاج. |

    <Warning>
    يجب أن يمتلك كيان IAM الذي يستخدمه Gateway الإذن `bedrock:ApplyGuardrail` بالإضافة إلى أذونات الاستدعاء القياسية.
    </Warning>

  </Accordion>

  <Accordion title="التضمينات للبحث في الذاكرة">
    يمكن لـ Bedrock أن يعمل أيضًا كمزود تضمين من أجل
    [البحث في الذاكرة](/ar/concepts/memory-search). ويتم إعداد ذلك بشكل منفصل عن
    مزود الاستدلال -- عيّن `agents.defaults.memorySearch.provider` إلى `"bedrock"`:

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: {
            provider: "bedrock",
            model: "amazon.titan-embed-text-v2:0", // default
          },
        },
      },
    }
    ```

    تستخدم تضمينات Bedrock سلسلة بيانات الاعتماد نفسها في AWS SDK مثل الاستدلال (أدوار
    المثيل، وSSO، ومفاتيح الوصول، والإعدادات المشتركة، وهوية الويب). لا حاجة إلى مفتاح API.
    عندما تكون `provider` هي `"auto"`، يتم اكتشاف Bedrock تلقائيًا إذا أمكن
    حل سلسلة بيانات الاعتماد تلك بنجاح.

    تشمل نماذج التضمين المدعومة Amazon Titan Embed ‏(v1 وv2)، وAmazon Nova
    Embed، وCohere Embed ‏(v3 وv4)، وTwelveLabs Marengo. راجع
    [مرجع إعدادات الذاكرة -- Bedrock](/ar/reference/memory-config#bedrock-embedding-config)
    للاطلاع على القائمة الكاملة للنماذج وخيارات الأبعاد.

  </Accordion>

  <Accordion title="ملاحظات ومحاذير">
    - يتطلب Bedrock تمكين **الوصول إلى النموذج** في حساب/منطقة AWS الخاصة بك.
    - يتطلب الاكتشاف التلقائي الإذنين `bedrock:ListFoundationModels` و
      `bedrock:ListInferenceProfiles`.
    - إذا كنت تعتمد على الوضع التلقائي، فعيّن أحد علامات بيئة مصادقة AWS المدعومة على
      مضيف Gateway. وإذا كنت تفضّل مصادقة IMDS/الإعدادات المشتركة دون علامات بيئة، فعيّن
      `plugins.entries.amazon-bedrock.config.discovery.enabled: true`.
    - يكشف OpenClaw عن مصدر بيانات الاعتماد بهذا الترتيب: `AWS_BEARER_TOKEN_BEDROCK`,
      ثم `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`، ثم `AWS_PROFILE`، ثم
      سلسلة AWS SDK الافتراضية.
    - يعتمد دعم التفكير على النموذج؛ تحقّق من بطاقة نموذج Bedrock لمعرفة
      الإمكانات الحالية.
    - إذا كنت تفضّل تدفق مفتاح مُدار، فيمكنك أيضًا وضع
      proxy متوافق مع OpenAI أمام Bedrock وإعداده بدلًا من ذلك كمزود OpenAI.
  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزودات، ومراجع النماذج، وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="البحث في الذاكرة" href="/ar/concepts/memory-search" icon="magnifying-glass">
    إعداد تضمينات Bedrock للبحث في الذاكرة.
  </Card>
  <Card title="مرجع إعدادات الذاكرة" href="/ar/reference/memory-config#bedrock-embedding-config" icon="database">
    القائمة الكاملة لنماذج تضمين Bedrock وخيارات الأبعاد.
  </Card>
  <Card title="استكشاف الأخطاء وإصلاحها" href="/ar/help/troubleshooting" icon="wrench">
    استكشاف الأخطاء وإصلاحها العام والأسئلة الشائعة.
  </Card>
</CardGroup>
