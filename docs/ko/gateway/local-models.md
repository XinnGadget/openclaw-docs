---
read_when:
    - 자신의 GPU 머신에서 모델을 서빙하려는 경우
    - LM Studio 또는 OpenAI 호환 프록시를 연결하는 경우
    - 가장 안전한 로컬 모델 가이드가 필요한 경우
summary: 로컬 LLM(LM Studio, vLLM, LiteLLM, 사용자 지정 OpenAI 엔드포인트)에서 OpenClaw 실행하기
title: 로컬 모델
x-i18n:
    generated_at: "2026-04-13T08:50:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3ecb61b3e6e34d3666f9b688cd694d92c5fb211cf8c420fa876f7ccf5789154a
    source_path: gateway/local-models.md
    workflow: 15
---

# 로컬 모델

로컬에서도 가능하지만, OpenClaw는 **큰 컨텍스트**와 프롬프트 인젝션에 대한 **강력한 방어**를 기대합니다. 작은 GPU 카드에서는 컨텍스트가 잘리고 안전성이 약해집니다. 목표는 높게 잡으세요: **최소 2대의 풀옵션 Mac Studio 또는 그에 준하는 GPU 장비(약 $30k 이상)**. **24 GB** GPU 1대로도 가능하긴 하지만, 더 가벼운 프롬프트에서만 가능하며 지연 시간도 더 높습니다. 실행 가능한 범위에서 **가장 크고 전체 크기의 모델 변형**을 사용하세요. 과도하게 양자화된 체크포인트나 “small” 모델은 프롬프트 인젝션 위험을 높입니다([보안](/ko/gateway/security) 참고).

가장 마찰이 적은 로컬 설정을 원한다면 [LM Studio](/ko/providers/lmstudio) 또는 [Ollama](/ko/providers/ollama)로 시작한 뒤 `openclaw onboard`를 실행하세요. 이 페이지는 더 높은 사양의 로컬 스택과 사용자 지정 OpenAI 호환 로컬 서버를 위한 의견이 반영된 가이드입니다.

## 권장: LM Studio + 대형 로컬 모델 (Responses API)

현재 기준으로 가장 좋은 로컬 스택입니다. LM Studio에 대형 모델(예: 전체 크기의 Qwen, DeepSeek, 또는 Llama 빌드)을 로드하고, 로컬 서버(기본값 `http://127.0.0.1:1234`)를 활성화한 뒤, Responses API를 사용해 추론과 최종 텍스트를 분리하세요.

```json5
{
  agents: {
    defaults: {
      model: { primary: “lmstudio/my-local-model” },
      models: {
        “anthropic/claude-opus-4-6”: { alias: “Opus” },
        “lmstudio/my-local-model”: { alias: “Local” },
      },
    },
  },
  models: {
    mode: “merge”,
    providers: {
      lmstudio: {
        baseUrl: “http://127.0.0.1:1234/v1”,
        apiKey: “lmstudio”,
        api: “openai-responses”,
        models: [
          {
            id: “my-local-model”,
            name: “Local Model”,
            reasoning: false,
            input: [“text”],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**설정 체크리스트**

- LM Studio 설치: [https://lmstudio.ai](https://lmstudio.ai)
- LM Studio에서 **사용 가능한 가장 큰 모델 빌드**를 다운로드하고(“small”/강한 양자화 변형은 피하세요), 서버를 시작한 다음 `http://127.0.0.1:1234/v1/models`에 해당 모델이 표시되는지 확인합니다.
- `my-local-model`을 LM Studio에 표시된 실제 모델 ID로 바꾸세요.
- 모델을 계속 로드된 상태로 유지하세요. 콜드 로드는 시작 지연을 추가합니다.
- LM Studio 빌드가 다르면 `contextWindow`와 `maxTokens`를 조정하세요.
- WhatsApp에서는 최종 텍스트만 전송되도록 Responses API를 사용하세요.

로컬로 실행하더라도 호스팅 모델 구성은 유지하세요. `models.mode: "merge"`를 사용하면 폴백이 계속 사용 가능합니다.

### 하이브리드 구성: 호스팅 모델을 기본으로, 로컬 모델을 폴백으로

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["lmstudio/my-local-model", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "lmstudio/my-local-model": { alias: "Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### 로컬 우선, 호스팅 모델을 안전망으로 사용

기본 모델과 폴백 순서를 바꾸면 됩니다. 동일한 providers 블록과 `models.mode: "merge"`를 유지하면 로컬 머신이 내려갔을 때 Sonnet 또는 Opus로 폴백할 수 있습니다.

### 지역별 호스팅 / 데이터 라우팅

- 호스팅되는 MiniMax/Kimi/GLM 변형도 OpenRouter에서 지역 고정 엔드포인트(예: 미국 호스팅)로 제공됩니다. 선택한 관할 구역 내에서 트래픽을 유지하려면 해당 지역 변형을 선택하고, Anthropic/OpenAI 폴백은 계속 사용할 수 있도록 `models.mode: "merge"`를 유지하세요.
- 완전한 로컬 전용이 가장 강력한 프라이버시 경로입니다. 호스팅된 지역 라우팅은 공급자 기능이 필요하지만 데이터 흐름을 통제하고 싶을 때의 중간 지점입니다.

## 기타 OpenAI 호환 로컬 프록시

vLLM, LiteLLM, OAI-proxy 또는 사용자 지정 게이트웨이도 OpenAI 스타일의 `/v1` 엔드포인트를 노출하면 사용할 수 있습니다. 위의 provider 블록을 여러분의 엔드포인트와 모델 ID로 바꾸세요.

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

호스팅 모델을 폴백으로 계속 사용할 수 있도록 `models.mode: "merge"`를 유지하세요.

로컬/프록시 `/v1` 백엔드의 동작 참고 사항:

- OpenClaw는 이를 네이티브 OpenAI 엔드포인트가 아니라 프록시 스타일의 OpenAI 호환 경로로 처리합니다.
- 여기에는 OpenAI 전용 요청 형태 조정이 적용되지 않습니다. 즉, `service_tier`, Responses `store`, OpenAI 추론 호환 페이로드 조정, 프롬프트 캐시 힌트가 없습니다.
- 숨겨진 OpenClaw attribution 헤더(`originator`, `version`, `User-Agent`)도 이러한 사용자 지정 프록시 URL에는 주입되지 않습니다.

더 엄격한 OpenAI 호환 백엔드를 위한 호환성 참고 사항:

- 일부 서버는 Chat Completions에서 구조화된 content-part 배열이 아니라 문자열 `messages[].content`만 허용합니다. 그런 엔드포인트에는 `models.providers.<provider>.models[].compat.requiresStringContent: true`를 설정하세요.
- 더 작거나 더 엄격한 일부 로컬 백엔드는, 특히 도구 스키마가 포함될 때 OpenClaw의 전체 에이전트 런타임 프롬프트 형태에서 불안정할 수 있습니다. 백엔드가 작은 직접 `/v1/chat/completions` 호출에서는 동작하지만 일반적인 OpenClaw 에이전트 턴에서는 실패한다면, 먼저 `models.providers.<provider>.models[].compat.supportsTools: false`를 시도하세요.
- 백엔드가 더 큰 OpenClaw 실행에서만 계속 실패한다면, 남은 문제는 보통 OpenClaw의 전송 계층이 아니라 업스트림 모델/서버 용량 또는 백엔드 버그입니다.

## 문제 해결

- Gateway가 프록시에 연결 가능한가요? `curl http://127.0.0.1:1234/v1/models`.
- LM Studio 모델이 언로드되었나요? 다시 로드하세요. 콜드 스타트는 “멈춘 것처럼 보이는” 흔한 원인입니다.
- 컨텍스트 오류가 나나요? `contextWindow`를 낮추거나 서버 제한을 올리세요.
- OpenAI 호환 서버가 `messages[].content ... expected a string`을 반환하나요? 해당 모델 항목에 `compat.requiresStringContent: true`를 추가하세요.
- 작은 직접 `/v1/chat/completions` 호출은 동작하지만 `openclaw infer model run`이 Gemma 또는 다른 로컬 모델에서 실패하나요? 먼저 `compat.supportsTools: false`로 도구 스키마를 비활성화한 뒤 다시 테스트하세요. 서버가 더 큰 OpenClaw 프롬프트에서만 계속 충돌한다면, 이를 업스트림 서버/모델 제한으로 취급하세요.
- 안전성: 로컬 모델은 공급자 측 필터를 건너뜁니다. 프롬프트 인젝션의 영향 범위를 제한하려면 에이전트 범위를 좁게 유지하고 Compaction을 켜 두세요.
