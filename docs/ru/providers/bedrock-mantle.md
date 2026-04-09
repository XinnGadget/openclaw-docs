---
summary: "Использовать модели Amazon Bedrock Mantle (совместимые с OpenAI) с OpenClaw"
read_when:
  - Вы хотите использовать размещённые в Bedrock Mantle модели OSS с OpenClaw
  - Вам нужен совместимый с OpenAI эндпоинт Mantle для GPT-OSS, Qwen, Kimi или GLM
title: "Amazon Bedrock Mantle"
---

# Amazon Bedrock Mantle

OpenClaw включает встроенный провайдер **Amazon Bedrock Mantle**, который подключается к совместимому с OpenAI эндпоинту Mantle. Mantle размещает модели с открытым исходным кодом и сторонние модели (GPT-OSS, Qwen, Kimi, GLM и аналогичные) через стандартный интерфейс `/v1/chat/completions`, поддерживаемый инфраструктурой Bedrock.

## Что поддерживает OpenClaw

- Провайдер: `amazon-bedrock-mantle`
- API: `openai-completions` (совместимый с OpenAI)
- Аутентификация: явный `AWS_BEARER_TOKEN_BEDROCK` или генерация токена-носителя через цепочку учётных данных IAM
- Регион: `AWS_REGION` или `AWS_DEFAULT_REGION` (по умолчанию: `us-east-1`)

## Автоматическое обнаружение моделей

Если переменная `AWS_BEARER_TOKEN_BEDROCK` задана, OpenClaw использует её напрямую. В противном случае OpenClaw пытается сгенерировать токен-носитель Mantle из стандартной цепочки учётных данных AWS, включая общие профили учётных данных/конфигурации, SSO, веб-идентификацию, а также роли экземпляра или задачи. Затем он обнаруживает доступные модели Mantle, отправляя запрос к эндпоинту `/v1/models` соответствующего региона. Результаты обнаружения кэшируются в течение 1 часа, а токены-носители, полученные через IAM, обновляются ежечасно.

Поддерживаемые регионы: `us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-1`, `ap-south-1`, `ap-southeast-3`, `eu-central-1`, `eu-west-1`, `eu-west-2`, `eu-south-1`, `eu-north-1`, `sa-east-1`.

## Подключение

1. Выберите один из способов аутентификации на **хосте шлюза**:

Явный токен-носитель:

```bash
export AWS_BEARER_TOKEN_BEDROCK="..."
# Опционально (по умолчанию us-east-1):
export AWS_REGION="us-west-2"
```

Учётные данные IAM:

```bash
# Здесь подойдёт любой источник аутентификации, совместимый с AWS SDK, например:
export AWS_PROFILE="default"
export AWS_REGION="us-west-2"
```

2. Проверьте, что модели обнаружены:

```bash
openclaw models list
```

Обнаруженные модели появятся в разделе провайдера `amazon-bedrock-mantle`. Дополнительная конфигурация не требуется, если вы не хотите переопределить значения по умолчанию.

## Ручная конфигурация

Если вы предпочитаете явную конфигурацию вместо автоматического обнаружения:

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

## Примечания

- OpenClaw может сгенерировать токен-носитель Mantle для вас из учётных данных IAM, совместимых с AWS SDK, если переменная `AWS_BEARER_TOKEN_BEDROCK` не задана.
- Токен-носитель — это тот же `AWS_BEARER_TOKEN_BEDROCK`, который используется стандартным провайдером [Amazon Bedrock](/providers/bedrock).
- Поддержка рассуждений (reasoning) определяется по идентификаторам моделей, содержащим такие шаблоны, как `thinking`, `reasoner` или `gpt-oss-120b`.
- Если эндпоинт Mantle недоступен или не возвращает моделей, провайдер пропускается без вывода сообщений.