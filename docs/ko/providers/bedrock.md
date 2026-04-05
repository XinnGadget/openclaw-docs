---
read_when:
    - OpenClaw에서 Amazon Bedrock 모델을 사용하려는 경우
    - 모델 호출을 위한 AWS 자격 증명/리전 설정이 필요한 경우
summary: OpenClaw에서 Amazon Bedrock(Converse API) 모델 사용하기
title: Amazon Bedrock
x-i18n:
    generated_at: "2026-04-05T12:52:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: a751824b679a9340db714ee5227e8d153f38f6c199ca900458a4ec092b4efe54
    source_path: providers/bedrock.md
    workflow: 15
---

# Amazon Bedrock

OpenClaw는 pi‑ai의 **Bedrock Converse** 스트리밍 provider를 통해 **Amazon Bedrock** 모델을 사용할 수 있습니다. Bedrock 인증은 API 키가 아니라 **AWS SDK 기본 자격 증명 체인**을 사용합니다.

## pi-ai가 지원하는 항목

- Provider: `amazon-bedrock`
- API: `bedrock-converse-stream`
- 인증: AWS 자격 증명(환경 변수, 공유 구성 또는 인스턴스 역할)
- 리전: `AWS_REGION` 또는 `AWS_DEFAULT_REGION` (기본값: `us-east-1`)

## 자동 모델 검색

OpenClaw는 **스트리밍**과 **텍스트 출력**을 지원하는 Bedrock 모델을 자동으로 검색할 수 있습니다. 검색에는 `bedrock:ListFoundationModels` 및 `bedrock:ListInferenceProfiles`가 사용되며, 결과는 캐시됩니다(기본값: 1시간).

암시적 provider가 활성화되는 방식:

- `plugins.entries.amazon-bedrock.config.discovery.enabled`가 `true`이면 AWS 환경 마커가 없어도 OpenClaw는 검색을 시도합니다.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`가 설정되지 않은 경우, OpenClaw는 다음 AWS 인증 마커 중 하나를 감지했을 때만 암시적 Bedrock provider를 자동 추가합니다: `AWS_BEARER_TOKEN_BEDROCK`, `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`, 또는 `AWS_PROFILE`.
- 실제 Bedrock 런타임 인증 경로는 여전히 AWS SDK 기본 체인을 사용하므로, 검색에 참여하기 위해 `enabled: true`가 필요했더라도 공유 구성, SSO 및 IMDS 인스턴스 역할 인증은 동작할 수 있습니다.

구성 옵션은 `plugins.entries.amazon-bedrock.config.discovery` 아래에 있습니다:

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

참고:

- `enabled`의 기본값은 auto 모드입니다. auto 모드에서 OpenClaw는 지원되는 AWS 환경 마커를 감지했을 때만 암시적 Bedrock provider를 활성화합니다.
- `region`의 기본값은 `AWS_REGION` 또는 `AWS_DEFAULT_REGION`이며, 그다음 `us-east-1`입니다.
- `providerFilter`는 Bedrock provider 이름(예: `anthropic`)과 일치시킵니다.
- `refreshInterval`의 단위는 초이며, 캐시를 비활성화하려면 `0`으로 설정합니다.
- `defaultContextWindow`(기본값: `32000`)와 `defaultMaxTokens`(기본값: `4096`)는 검색된 모델에 사용됩니다(모델 한도를 알고 있다면 재정의하세요).
- 명시적인 `models.providers["amazon-bedrock"]` 항목의 경우에도 OpenClaw는 전체 런타임 인증 로딩을 강제하지 않고 `AWS_BEARER_TOKEN_BEDROCK` 같은 AWS 환경 마커에서 Bedrock 환경 마커 인증을 조기에 확인할 수 있습니다. 실제 모델 호출 인증 경로는 여전히 AWS SDK 기본 체인을 사용합니다.

## 온보딩

1. **gateway host**에서 AWS 자격 증명을 사용할 수 있는지 확인합니다:

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
# 선택 사항:
export AWS_SESSION_TOKEN="..."
export AWS_PROFILE="your-profile"
# 선택 사항(Bedrock API 키/베어러 토큰):
export AWS_BEARER_TOKEN_BEDROCK="..."
```

2. 구성에 Bedrock provider와 모델을 추가합니다(`apiKey`는 필요 없음):

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

## EC2 인스턴스 역할

IAM 역할이 연결된 EC2 인스턴스에서 OpenClaw를 실행하면 AWS SDK는 인증을 위해 인스턴스 메타데이터 서비스(IMDS)를 사용할 수 있습니다. Bedrock 모델 검색의 경우, OpenClaw는 `plugins.entries.amazon-bedrock.config.discovery.enabled: true`를 명시적으로 설정하지 않는 한 AWS 환경 마커를 기반으로만 암시적 provider를 자동 활성화합니다.

IMDS 기반 호스트에 권장되는 설정:

- `plugins.entries.amazon-bedrock.config.discovery.enabled`를 `true`로 설정합니다.
- `plugins.entries.amazon-bedrock.config.discovery.region`을 설정합니다(또는 `AWS_REGION`을 export합니다).
- 가짜 API 키는 필요하지 않습니다.
- auto 모드 또는 상태 표시 화면을 위한 환경 마커가 특별히 필요한 경우에만 `AWS_PROFILE=default`가 필요합니다.

```bash
# 권장: 명시적으로 검색 활성화 + 리전 설정
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 선택 사항: 명시적 활성화 없이 auto 모드를 원하면 환경 마커 추가
export AWS_PROFILE=default
export AWS_REGION=us-east-1
```

EC2 인스턴스 역할에 필요한 **IAM 권한**:

- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`
- `bedrock:ListFoundationModels` (자동 검색용)
- `bedrock:ListInferenceProfiles` (추론 프로필 검색용)

또는 관리형 정책 `AmazonBedrockFullAccess`를 연결합니다.

## 빠른 설정(AWS 경로)

```bash
# 1. IAM 역할 및 인스턴스 프로필 생성
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

# 2. EC2 인스턴스에 연결
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. EC2 인스턴스에서 검색을 명시적으로 활성화
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 4. 선택 사항: 명시적 활성화 없이 auto 모드를 원하면 환경 마커 추가
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. 모델이 검색되는지 확인
openclaw models list
```

## 추론 프로필

OpenClaw는 foundation model과 함께 **리전별 및 전역 추론 프로필**도 검색합니다. 프로필이 알려진 foundation model에 매핑되면 해당 프로필은 그 모델의 기능(context window, max tokens, reasoning, vision)을 상속하며, 올바른 Bedrock 요청 리전이 자동으로 주입됩니다. 즉, 리전 간 Claude 프로필도 수동 provider 재정의 없이 동작합니다.

추론 프로필 ID는 `us.anthropic.claude-opus-4-6-v1:0`(리전별) 또는 `anthropic.claude-opus-4-6-v1:0`(전역)처럼 보입니다. 기반 모델이 이미 검색 결과에 있으면 프로필은 그 전체 기능 집합을 상속합니다. 그렇지 않으면 안전한 기본값이 적용됩니다.

추가 구성은 필요하지 않습니다. 검색이 활성화되어 있고 IAM 주체에 `bedrock:ListInferenceProfiles` 권한이 있으면, 프로필은 `openclaw models list`에서 foundation model과 함께 표시됩니다.

## 참고

- Bedrock를 사용하려면 AWS 계정/리전에서 **모델 액세스**가 활성화되어 있어야 합니다.
- 자동 검색에는 `bedrock:ListFoundationModels` 및 `bedrock:ListInferenceProfiles` 권한이 필요합니다.
- auto 모드를 사용하는 경우, **gateway host**에서 지원되는 AWS 인증 환경 마커 중 하나를 설정하세요. 환경 마커 없이 IMDS/공유 구성 인증을 사용하려면 `plugins.entries.amazon-bedrock.config.discovery.enabled: true`를 설정하세요.
- OpenClaw는 자격 증명 소스를 다음 순서로 표시합니다: `AWS_BEARER_TOKEN_BEDROCK`, 그다음 `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`, 그다음 `AWS_PROFILE`, 마지막으로 기본 AWS SDK 체인.
- reasoning 지원 여부는 모델에 따라 다르므로, 현재 기능은 Bedrock 모델 카드에서 확인하세요.
- 관리형 키 흐름을 선호한다면, Bedrock 앞단에 OpenAI 호환 프록시를 두고 대신 OpenAI provider로 구성할 수도 있습니다.

## Guardrails

`amazon-bedrock` 플러그인 구성에 `guardrail` 객체를 추가하면 모든 Bedrock 모델 호출에 [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)를 적용할 수 있습니다. Guardrails를 사용하면 콘텐츠 필터링, 주제 차단, 단어 필터, 민감한 정보 필터, 컨텍스트 기반 근거 확인을 강제할 수 있습니다.

```json5
{
  plugins: {
    entries: {
      "amazon-bedrock": {
        config: {
          guardrail: {
            guardrailIdentifier: "abc123", // guardrail ID 또는 전체 ARN
            guardrailVersion: "1", // 버전 번호 또는 "DRAFT"
            streamProcessingMode: "sync", // 선택 사항: "sync" 또는 "async"
            trace: "enabled", // 선택 사항: "enabled", "disabled" 또는 "enabled_full"
          },
        },
      },
    },
  },
}
```

- `guardrailIdentifier`(필수)는 guardrail ID(예: `abc123`) 또는 전체 ARN(예: `arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123`)을 받습니다.
- `guardrailVersion`(필수)은 사용할 게시된 버전을 지정하거나 작업 중인 초안을 위해 `"DRAFT"`를 지정합니다.
- `streamProcessingMode`(선택 사항)는 스트리밍 중 guardrail 평가를 동기식(`"sync"`)으로 실행할지 비동기식(`"async"`)으로 실행할지 제어합니다. 생략하면 Bedrock의 기본 동작이 사용됩니다.
- `trace`(선택 사항)는 API 응답에서 guardrail 추적 출력을 활성화합니다. 디버깅용으로는 `"enabled"` 또는 `"enabled_full"`로 설정하고, 프로덕션에서는 생략하거나 `"disabled"`로 설정하세요.

gateway가 사용하는 IAM 주체에는 표준 invoke 권한에 더해 `bedrock:ApplyGuardrail` 권한도 있어야 합니다.
