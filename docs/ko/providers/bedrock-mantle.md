---
read_when:
    - Bedrock Mantle이 호스팅하는 OSS 모델을 OpenClaw에서 사용하려고 함
    - GPT-OSS, Qwen, Kimi, 또는 GLM용 Mantle OpenAI 호환 엔드포인트가 필요함
summary: OpenClaw에서 Amazon Bedrock Mantle(OpenAI 호환) 모델 사용하기
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-05T12:50:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2efe61261fbb430f63be9f5025c0654c44b191dbe96b3eb081d7ccbe78458907
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

OpenClaw에는
Mantle OpenAI 호환 엔드포인트에 연결하는 번들 **Amazon Bedrock Mantle** provider가 포함되어 있습니다. Mantle은
Bedrock 인프라를 기반으로 한 표준
`/v1/chat/completions` 표면을 통해 오픈 소스 및
서드파티 모델(GPT-OSS, Qwen, Kimi, GLM 등)을 호스팅합니다.

## OpenClaw에서 지원하는 항목

- Provider: `amazon-bedrock-mantle`
- API: `openai-completions` (OpenAI 호환)
- 인증: `AWS_BEARER_TOKEN_BEDROCK`를 통한 bearer token
- 리전: `AWS_REGION` 또는 `AWS_DEFAULT_REGION` (기본값: `us-east-1`)

## 자동 모델 검색

`AWS_BEARER_TOKEN_BEDROCK`가 설정되어 있으면 OpenClaw는
리전의 `/v1/models` 엔드포인트를 조회하여 사용 가능한 Mantle 모델을 자동으로 검색합니다.
검색 결과는 1시간 동안 캐시됩니다.

지원 리전: `us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-1`,
`ap-south-1`, `ap-southeast-3`, `eu-central-1`, `eu-west-1`, `eu-west-2`,
`eu-south-1`, `eu-north-1`, `sa-east-1`.

## 온보딩

1. **gateway 호스트**에 bearer token을 설정합니다:

```bash
export AWS_BEARER_TOKEN_BEDROCK="..."
# 선택 사항(기본값은 us-east-1):
export AWS_REGION="us-west-2"
```

2. 모델이 검색되는지 확인합니다:

```bash
openclaw models list
```

검색된 모델은 `amazon-bedrock-mantle` provider 아래에 표시됩니다. 기본값을 재정의하려는 경우가 아니라면
추가 config는 필요하지 않습니다.

## 수동 구성

자동 검색 대신 명시적 config를 선호한다면:

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

## 참고

- Mantle은 현재 bearer token이 필요합니다. 일반 IAM 자격 증명(instance roles,
  SSO, access keys)만으로는 token 없이 충분하지 않습니다.
- bearer token은 표준
  [Amazon Bedrock](/providers/bedrock) provider에서 사용하는 것과 동일한 `AWS_BEARER_TOKEN_BEDROCK`입니다.
- reasoning 지원은
  `thinking`, `reasoner`, 또는 `gpt-oss-120b` 같은 패턴이 포함된 모델 ID에서 추론됩니다.
- Mantle 엔드포인트를 사용할 수 없거나 모델을 반환하지 않으면 provider는
  조용히 건너뜁니다.
