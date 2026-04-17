---
read_when:
    - Ви хочете використовувати моделі Amazon Bedrock з OpenClaw
    - Для викликів моделей вам потрібно налаштувати облікові дані AWS і регіон
summary: Використовуйте моделі Amazon Bedrock (Converse API) з OpenClaw
title: Amazon Bedrock
x-i18n:
    generated_at: "2026-04-12T10:03:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: 88e7e24907ec26af098b648e2eeca32add090a9e381c818693169ab80aeccc47
    source_path: providers/bedrock.md
    workflow: 15
---

# Amazon Bedrock

OpenClaw може використовувати моделі **Amazon Bedrock** через потокового провайдера **Bedrock Converse** від pi-ai. Автентифікація Bedrock використовує **стандартний ланцюжок облікових даних AWS SDK**, а не API-ключ.

| Властивість | Значення                                                     |
| -------- | ----------------------------------------------------------- |
| Провайдер | `amazon-bedrock`                                            |
| API      | `bedrock-converse-stream`                                   |
| Автентифікація | Облікові дані AWS (змінні середовища, спільна конфігурація або роль екземпляра) |
| Регіон   | `AWS_REGION` або `AWS_DEFAULT_REGION` (типово: `us-east-1`) |

## Початок роботи

Виберіть бажаний спосіб автентифікації та виконайте кроки налаштування.

<Tabs>
  <Tab title="Ключі доступу / змінні середовища">
    **Найкраще підходить для:** машин розробників, CI або хостів, де ви безпосередньо керуєте обліковими даними AWS.

    <Steps>
      <Step title="Установіть облікові дані AWS на хості Gateway">
        ```bash
        export AWS_ACCESS_KEY_ID="AKIA..."
        export AWS_SECRET_ACCESS_KEY="..."
        export AWS_REGION="us-east-1"
        # Необов’язково:
        export AWS_SESSION_TOKEN="..."
        export AWS_PROFILE="your-profile"
        # Необов’язково (API-ключ/bearer token Bedrock):
        export AWS_BEARER_TOKEN_BEDROCK="..."
        ```
      </Step>
      <Step title="Додайте провайдер Bedrock і модель до своєї конфігурації">
        `apiKey` не потрібен. Налаштуйте провайдера з `auth: "aws-sdk"`:

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
      <Step title="Переконайтеся, що моделі доступні">
        ```bash
        openclaw models list
        ```
      </Step>
    </Steps>

    <Tip>
    З автентифікацією через маркери середовища (`AWS_ACCESS_KEY_ID`, `AWS_PROFILE` або `AWS_BEARER_TOKEN_BEDROCK`) OpenClaw автоматично вмикає неявний провайдер Bedrock для виявлення моделей без додаткової конфігурації.
    </Tip>

  </Tab>

  <Tab title="Ролі екземпляра EC2 (IMDS)">
    **Найкраще підходить для:** екземплярів EC2 із прикріпленою роллю IAM, які використовують службу метаданих екземпляра для автентифікації.

    <Steps>
      <Step title="Явно ввімкніть виявлення">
        Під час використання IMDS OpenClaw не може виявити автентифікацію AWS лише за маркерами середовища, тому ви маєте явно погодитися на це:

        ```bash
        openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
        openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1
        ```
      </Step>
      <Step title="За бажанням додайте маркер середовища для автоматичного режиму">
        Якщо ви також хочете, щоб працював шлях автовиявлення через маркери середовища (наприклад, для поверхонь `openclaw status`):

        ```bash
        export AWS_PROFILE=default
        export AWS_REGION=us-east-1
        ```

        Вам **не** потрібен фальшивий API-ключ.
      </Step>
      <Step title="Переконайтеся, що моделі виявлено">
        ```bash
        openclaw models list
        ```
      </Step>
    </Steps>

    <Warning>
    Роль IAM, прикріплена до вашого екземпляра EC2, повинна мати такі дозволи:

    - `bedrock:InvokeModel`
    - `bedrock:InvokeModelWithResponseStream`
    - `bedrock:ListFoundationModels` (для автоматичного виявлення)
    - `bedrock:ListInferenceProfiles` (для виявлення профілів інференсу)

    Або прикріпіть керовану політику `AmazonBedrockFullAccess`.
    </Warning>

    <Note>
    `AWS_PROFILE=default` потрібен лише якщо ви спеціально хочете маркер середовища для автоматичного режиму або поверхонь статусу. Фактичний шлях автентифікації Bedrock під час виконання використовує стандартний ланцюжок AWS SDK, тому автентифікація роллю екземпляра через IMDS працює навіть без маркерів середовища.
    </Note>

  </Tab>
</Tabs>

## Автоматичне виявлення моделей

OpenClaw може автоматично виявляти моделі Bedrock, які підтримують **потокову передачу**
та **текстовий вивід**. Для виявлення використовуються `bedrock:ListFoundationModels` і
`bedrock:ListInferenceProfiles`, а результати кешуються (типово: 1 година).

Як вмикається неявний провайдер:

- Якщо `plugins.entries.amazon-bedrock.config.discovery.enabled` має значення `true`,
  OpenClaw спробує виконати виявлення, навіть якщо жоден маркер середовища AWS не присутній.
- Якщо `plugins.entries.amazon-bedrock.config.discovery.enabled` не встановлено,
  OpenClaw автоматично додає
  неявний провайдер Bedrock лише тоді, коли бачить один із цих маркерів автентифікації AWS:
  `AWS_BEARER_TOKEN_BEDROCK`, `AWS_ACCESS_KEY_ID` +
  `AWS_SECRET_ACCESS_KEY` або `AWS_PROFILE`.
- Фактичний шлях автентифікації Bedrock під час виконання все одно використовує стандартний ланцюжок AWS SDK, тому
  спільна конфігурація, SSO та автентифікація роллю екземпляра IMDS можуть працювати, навіть якщо для виявлення
  потрібно було явно ввімкнути `enabled: true`.

<Note>
Для явних записів `models.providers["amazon-bedrock"]` OpenClaw усе ще може рано визначити автентифікацію Bedrock через маркери середовища з AWS, наприклад `AWS_BEARER_TOKEN_BEDROCK`, без примусового повного завантаження автентифікації під час виконання. Фактичний шлях автентифікації для викликів моделей усе одно використовує стандартний ланцюжок AWS SDK.
</Note>

<AccordionGroup>
  <Accordion title="Параметри конфігурації виявлення">
    Параметри конфігурації розміщуються в `plugins.entries.amazon-bedrock.config.discovery`:

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

    | Параметр | Типово | Опис |
    | ------ | ------- | ----------- |
    | `enabled` | auto | У режимі auto OpenClaw вмикає неявний провайдер Bedrock лише тоді, коли бачить підтримуваний маркер середовища AWS. Установіть `true`, щоб примусово ввімкнути виявлення. |
    | `region` | `AWS_REGION` / `AWS_DEFAULT_REGION` / `us-east-1` | Регіон AWS, який використовується для API-викликів виявлення. |
    | `providerFilter` | (усі) | Відповідає назвам провайдерів Bedrock (наприклад, `anthropic`, `amazon`). |
    | `refreshInterval` | `3600` | Тривалість кешу в секундах. Установіть `0`, щоб вимкнути кешування. |
    | `defaultContextWindow` | `32000` | Контекстне вікно, яке використовується для виявлених моделей (перевизначте, якщо знаєте обмеження своєї моделі). |
    | `defaultMaxTokens` | `4096` | Максимальна кількість вихідних токенів, яка використовується для виявлених моделей (перевизначте, якщо знаєте обмеження своєї моделі). |

  </Accordion>
</AccordionGroup>

## Швидке налаштування (шлях AWS)

Цей приклад створює роль IAM, прикріплює дозволи Bedrock, асоціює
профіль екземпляра та вмикає виявлення OpenClaw на хості EC2.

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

## Розширена конфігурація

<AccordionGroup>
  <Accordion title="Профілі інференсу">
    OpenClaw виявляє **регіональні та глобальні профілі інференсу** поряд із
    базовими моделями. Коли профіль зіставляється з відомою базовою моделлю, цей
    профіль успадковує можливості моделі (контекстне вікно, максимальну кількість токенів,
    reasoning, vision), а правильний регіон запиту Bedrock автоматично
    додається. Це означає, що міжрегіональні профілі Claude працюють без ручного
    перевизначення провайдера.

    Ідентифікатори профілів інференсу мають вигляд `us.anthropic.claude-opus-4-6-v1:0` (регіональний)
    або `anthropic.claude-opus-4-6-v1:0` (глобальний). Якщо базову модель уже
    присутня в результатах виявлення, профіль успадковує її повний набір можливостей;
    в іншому разі застосовуються безпечні типові значення.

    Додаткова конфігурація не потрібна. Поки виявлення ввімкнено і принципал IAM
    має дозвіл `bedrock:ListInferenceProfiles`, профілі з’являються поряд
    із базовими моделями в `openclaw models list`.

  </Accordion>

  <Accordion title="Guardrails">
    Ви можете застосувати [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
    до всіх викликів моделей Bedrock, додавши об’єкт `guardrail` до
    конфігурації plugin `amazon-bedrock`. Guardrails дають змогу застосовувати фільтрацію контенту,
    заборону тем, фільтри слів, фільтри чутливої інформації та перевірки
    контекстуального узгодження.

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

    | Параметр | Обов’язковий | Опис |
    | ------ | -------- | ----------- |
    | `guardrailIdentifier` | Так | Ідентифікатор guardrail (наприклад, `abc123`) або повний ARN (наприклад, `arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123`). |
    | `guardrailVersion` | Так | Номер опублікованої версії або `"DRAFT"` для робочої чернетки. |
    | `streamProcessingMode` | Ні | `"sync"` або `"async"` для оцінювання guardrail під час потокової передачі. Якщо не вказано, Bedrock використовує своє типове значення. |
    | `trace` | Ні | `"enabled"` або `"enabled_full"` для налагодження; не вказуйте або встановіть `"disabled"` для production. |

    <Warning>
    Принципал IAM, який використовується Gateway, повинен мати дозвіл `bedrock:ApplyGuardrail` на додачу до стандартних дозволів виклику.
    </Warning>

  </Accordion>

  <Accordion title="Embeddings для пошуку в пам’яті">
    Bedrock також може виступати провайдером embeddings для
    [пошуку в пам’яті](/uk/concepts/memory-search). Це налаштовується окремо від
    провайдера інференсу — установіть `agents.defaults.memorySearch.provider` у `"bedrock"`:

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

    Embeddings Bedrock використовують той самий ланцюжок облікових даних AWS SDK, що й інференс (ролі
    екземпляра, SSO, ключі доступу, спільна конфігурація та web identity). API-ключ
    не потрібен. Коли `provider` має значення `"auto"`, Bedrock визначається автоматично, якщо цей
    ланцюжок облікових даних успішно розв’язується.

    Підтримувані моделі embeddings включають Amazon Titan Embed (v1, v2), Amazon Nova
    Embed, Cohere Embed (v3, v4) і TwelveLabs Marengo. Повний
    список моделей і параметри розмірності див. у
    [довіднику з конфігурації пам’яті -- Bedrock](/uk/reference/memory-config#bedrock-embedding-config).

  </Accordion>

  <Accordion title="Примітки та застереження">
    - Bedrock вимагає ввімкненого **доступу до моделей** у вашому обліковому записі/регіоні AWS.
    - Для автоматичного виявлення потрібні дозволи `bedrock:ListFoundationModels` і
      `bedrock:ListInferenceProfiles`.
    - Якщо ви покладаєтеся на автоматичний режим, установіть один із підтримуваних маркерів середовища автентифікації AWS на
      хості Gateway. Якщо ви віддаєте перевагу автентифікації IMDS/shared-config без маркерів середовища, установіть
      `plugins.entries.amazon-bedrock.config.discovery.enabled: true`.
    - OpenClaw показує джерело облікових даних у такому порядку: `AWS_BEARER_TOKEN_BEDROCK`,
      потім `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`, потім `AWS_PROFILE`, а потім
      стандартний ланцюжок AWS SDK.
    - Підтримка reasoning залежить від моделі; перевіряйте картку моделі Bedrock щодо
      поточних можливостей.
    - Якщо ви віддаєте перевагу керованому потоку ключів, ви також можете розмістити OpenAI-compatible
      проксі перед Bedrock і натомість налаштувати його як провайдер OpenAI.
  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Вибір моделі" href="/uk/concepts/model-providers" icon="layers">
    Вибір провайдерів, посилань на моделі та поведінки перемикання на резервний варіант.
  </Card>
  <Card title="Пошук у пам’яті" href="/uk/concepts/memory-search" icon="magnifying-glass">
    Конфігурація embeddings Bedrock для пошуку в пам’яті.
  </Card>
  <Card title="Довідник з конфігурації пам’яті" href="/uk/reference/memory-config#bedrock-embedding-config" icon="database">
    Повний список моделей embeddings Bedrock і параметри розмірності.
  </Card>
  <Card title="Усунення несправностей" href="/uk/help/troubleshooting" icon="wrench">
    Загальне усунення несправностей і поширені запитання.
  </Card>
</CardGroup>
