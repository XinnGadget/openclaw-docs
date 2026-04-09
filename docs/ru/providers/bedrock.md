---
summary: "Использовать модели Amazon Bedrock (Converse API) с OpenClaw"
read_when:
  - Вы хотите использовать модели Amazon Bedrock с OpenClaw
  - Вам нужно настроить учётные данные AWS/регион для вызовов моделей
title: "Amazon Bedrock"
---

# Amazon Bedrock

OpenClaw может использовать модели **Amazon Bedrock** через потокового провайдера **Bedrock Converse** от pi-ai. Для аутентификации в Bedrock используется **цепочка учётных данных AWS SDK по умолчанию**, а не API-ключ.

## Что поддерживает pi-ai

- Провайдер: `amazon-bedrock`
- API: `bedrock-converse-stream`
- Аутентификация: учётные данные AWS (переменные окружения, общая конфигурация или роль экземпляра)
- Регион: `AWS_REGION` или `AWS_DEFAULT_REGION` (по умолчанию: `us-east-1`)

## Автоматическое обнаружение моделей

OpenClaw может автоматически обнаруживать модели Bedrock, поддерживающие **потоковую передачу** и **вывод текста**. Для обнаружения используются операции `bedrock:ListFoundationModels` и `bedrock:ListInferenceProfiles`, результаты кэшируются (по умолчанию — 1 час).

Как включается неявный провайдер:

- Если `plugins.entries.amazon-bedrock.config.discovery.enabled` имеет значение `true`, OpenClaw попытается выполнить обнаружение, даже если маркер окружения AWS отсутствует.
- Если `plugins.entries.amazon-bedrock.config.discovery.enabled` не задан, OpenClaw автоматически добавляет неявный провайдер Bedrock только при обнаружении одного из маркеров аутентификации AWS: `AWS_BEARER_TOKEN_BEDROCK`, `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` или `AWS_PROFILE`.
- Фактический путь аутентификации во время выполнения Bedrock по-прежнему использует цепочку учётных данных AWS SDK по умолчанию, поэтому общая конфигурация, SSO и аутентификация через роль экземпляра IMDS могут работать, даже если для обнаружения требовалось установить `enabled: true`.

Параметры конфигурации находятся в разделе `plugins.entries.amazon-bedrock.config.discovery`:

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

Примечания:

- `enabled` по умолчанию имеет значение "автоматический режим". В автоматическом режиме OpenClaw включает неявный провайдер Bedrock только при обнаружении поддерживаемого маркера окружения AWS.
- `region` по умолчанию использует `AWS_REGION` или `AWS_DEFAULT_REGION`, затем `us-east-1`.
- `providerFilter` сопоставляет имена провайдеров Bedrock (например, `anthropic`).
- `refreshInterval` указывается в секундах; установите значение `0`, чтобы отключить кэширование.
- `defaultContextWindow` (по умолчанию: `32000`) и `defaultMaxTokens` (по умолчанию: `4096`) используются для обнаруженных моделей (переопределите их, если знаете ограничения своей модели).
- Для явных записей `models.providers["amazon-bedrock"]` OpenClaw по-прежнему может заранее разрешить аутентификацию по маркерам окружения AWS (таким как `AWS_BEARER_TOKEN_BEDROCK`), не загружая полностью аутентификацию во время выполнения. Фактический путь аутентификации при вызове модели по-прежнему использует цепочку учётных данных AWS SDK по умолчанию.

## Подключение

1. Убедитесь, что учётные данные AWS доступны на **хосте шлюза**:

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
# Опционально:
export AWS_SESSION_TOKEN="..."
export AWS_PROFILE="your-profile"
# Опционально (API-ключ/токен Bearer для Bedrock):
export AWS_BEARER_TOKEN_BEDROCK="..."
```

2. Добавьте провайдер и модель Bedrock в конфигурацию (API-ключ не требуется):

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

## Роли экземпляров EC2

При запуске OpenClaw на экземпляре EC2 с прикреплённой ролью IAM AWS SDK может использовать службу метаданных экземпляра (IMDS) для аутентификации. Для обнаружения моделей Bedrock OpenClaw автоматически включает неявный провайдер только при наличии маркеров окружения AWS, если вы явно не установили `plugins.entries.amazon-bedrock.config.discovery.enabled: true`.

Рекомендуемая настройка для хостов с поддержкой IMDS:

- Установите `plugins.entries.amazon-bedrock.config.discovery.enabled` в `true`.
- Установите `plugins.entries.amazon-bedrock.config.discovery.region` (или экспортируйте `AWS_REGION`).
- Вам **не** нужен фиктивный API-ключ.
- Вам нужен только `AWS_PROFILE=default`, если вы специально хотите использовать маркер окружения для автоматического режима или отображения статуса.

```bash
# Рекомендуется: явное включение обнаружения + регион
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# Опционально: добавьте маркер окружения, если хотите использовать автоматический режим без явного включения
export AWS_PROFILE=default
export AWS_REGION=us-east-1
```

**Необходимые разрешения IAM** для роли экземпляра EC2:

- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`
- `bedrock:ListFoundationModels` (для автоматического обнаружения)
- `bedrock:ListInferenceProfiles` (для обнаружения профилей вывода)

Или прикрепите управляемую политику `AmazonBedrockFullAccess`.

## Быстрая настройка (путь AWS)

```bash
# 1. Создайте роль IAM и профиль экземпляра
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

# 2. Прикрепите к вашему экземпляру EC2
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. На экземпляре EC2 явно включите обнаружение
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 4. Опционально: добавьте маркер окружения, если хотите использовать автоматический режим без явного включения
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. Проверьте, что модели обнаружены
openclaw models list
```

## Профили вывода

OpenClaw