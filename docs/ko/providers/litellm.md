---
read_when:
    - OpenClaw를 LiteLLM 프록시를 통해 라우팅하려는 경우
    - LiteLLM을 통한 비용 추적, 로깅 또는 모델 라우팅이 필요한 경우
summary: 통합 모델 액세스 및 비용 추적을 위해 OpenClaw를 LiteLLM Proxy를 통해 실행하기
title: LiteLLM
x-i18n:
    generated_at: "2026-04-05T12:52:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4e8ca73458186285bc06967b397b8a008791dc58eea1159d6c358e1a794982d1
    source_path: providers/litellm.md
    workflow: 15
---

# LiteLLM

[LiteLLM](https://litellm.ai)은 100개 이상의 모델 provider에 대한 통합 API를 제공하는 오픈 소스 LLM 게이트웨이입니다. OpenClaw를 LiteLLM을 통해 라우팅하면 중앙 집중식 비용 추적, 로깅, 그리고 OpenClaw 구성을 변경하지 않고도 백엔드를 전환할 수 있는 유연성을 얻을 수 있습니다.

## OpenClaw와 함께 LiteLLM을 사용하는 이유

- **비용 추적** — 모든 모델에서 OpenClaw의 지출을 정확히 확인
- **모델 라우팅** — 구성 변경 없이 Claude, GPT-4, Gemini, Bedrock 간 전환
- **가상 키** — OpenClaw용 지출 한도가 있는 키 생성
- **로깅** — 디버깅을 위한 전체 요청/응답 로그
- **대체 경로** — 기본 provider가 다운된 경우 자동 장애 조치

## 빠른 시작

### 온보딩을 통해

```bash
openclaw onboard --auth-choice litellm-api-key
```

### 수동 설정

1. LiteLLM Proxy를 시작합니다:

```bash
pip install 'litellm[proxy]'
litellm --model claude-opus-4-6
```

2. OpenClaw가 LiteLLM을 가리키도록 설정합니다:

```bash
export LITELLM_API_KEY="your-litellm-key"

openclaw
```

이제 완료되었습니다. OpenClaw는 이제 LiteLLM을 통해 라우팅됩니다.

## 구성

### 환경 변수

```bash
export LITELLM_API_KEY="sk-litellm-key"
```

### 구성 파일

```json5
{
  models: {
    providers: {
      litellm: {
        baseUrl: "http://localhost:4000",
        apiKey: "${LITELLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "claude-opus-4-6",
            name: "Claude Opus 4.6",
            reasoning: true,
            input: ["text", "image"],
            contextWindow: 200000,
            maxTokens: 64000,
          },
          {
            id: "gpt-4o",
            name: "GPT-4o",
            reasoning: false,
            input: ["text", "image"],
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "litellm/claude-opus-4-6" },
    },
  },
}
```

## 가상 키

OpenClaw 전용 키를 지출 한도와 함께 생성합니다:

```bash
curl -X POST "http://localhost:4000/key/generate" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "key_alias": "openclaw",
    "max_budget": 50.00,
    "budget_duration": "monthly"
  }'
```

생성된 키를 `LITELLM_API_KEY`로 사용하세요.

## 모델 라우팅

LiteLLM은 모델 요청을 서로 다른 백엔드로 라우팅할 수 있습니다. LiteLLM의 `config.yaml`에서 구성하세요:

```yaml
model_list:
  - model_name: claude-opus-4-6
    litellm_params:
      model: claude-opus-4-6
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY
```

OpenClaw는 계속 `claude-opus-4-6`을 요청하고, 라우팅은 LiteLLM이 처리합니다.

## 사용량 보기

LiteLLM의 대시보드 또는 API를 확인하세요:

```bash
# 키 정보
curl "http://localhost:4000/key/info" \
  -H "Authorization: Bearer sk-litellm-key"

# 지출 로그
curl "http://localhost:4000/spend/logs" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

## 참고

- LiteLLM은 기본적으로 `http://localhost:4000`에서 실행됩니다
- OpenClaw는 LiteLLM의 프록시 스타일 OpenAI 호환 `/v1` 엔드포인트를 통해 연결됩니다
- OpenAI 전용 기본 요청 형태 조정은 LiteLLM을 통해서는 적용되지 않습니다:
  `service_tier`, Responses `store`, 프롬프트 캐시 힌트, OpenAI reasoning 호환 페이로드 형태 조정은 지원되지 않습니다
- 숨겨진 OpenClaw attribution 헤더(`originator`, `version`, `User-Agent`)는 사용자 지정 LiteLLM base URL에서는 주입되지 않습니다

## 함께 보기

- [LiteLLM 문서](https://docs.litellm.ai)
- [모델 provider](/ko/concepts/model-providers)
