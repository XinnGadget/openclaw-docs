---
read_when:
    - 로컬 vLLM 서버에 연결해 OpenClaw를 실행하려고 합니다
    - 자체 모델로 OpenAI 호환 `/v1` 엔드포인트를 사용하려고 합니다
summary: vLLM(OpenAI 호환 로컬 서버)로 OpenClaw 실행하기
title: vLLM
x-i18n:
    generated_at: "2026-04-05T12:53:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: ebde34d0453586d10340680b8d51465fdc98bd28e8a96acfaeb24606886b50f4
    source_path: providers/vllm.md
    workflow: 15
---

# vLLM

vLLM은 **OpenAI 호환** HTTP API를 통해 오픈소스 모델(및 일부 커스텀 모델)을 제공할 수 있습니다. OpenClaw는 `openai-completions` API를 사용해 vLLM에 연결할 수 있습니다.

또한 `VLLM_API_KEY`로 옵트인하고(서버에서 인증을 강제하지 않는다면 아무 값이나 동작함) 명시적인 `models.providers.vllm` 항목을 정의하지 않으면, OpenClaw는 vLLM에서 사용 가능한 모델을 **자동 감지**할 수도 있습니다.

## 빠른 시작

1. OpenAI 호환 서버로 vLLM을 시작합니다.

기본 URL은 `/v1` 엔드포인트(예: `/v1/models`, `/v1/chat/completions`)를 노출해야 합니다. vLLM은 일반적으로 다음에서 실행됩니다:

- `http://127.0.0.1:8000/v1`

2. 옵트인합니다(인증이 구성되지 않았다면 아무 값이나 동작함):

```bash
export VLLM_API_KEY="vllm-local"
```

3. 모델을 선택합니다(vLLM 모델 ID 중 하나로 바꾸세요):

```json5
{
  agents: {
    defaults: {
      model: { primary: "vllm/your-model-id" },
    },
  },
}
```

## 모델 검색(암시적 제공자)

`VLLM_API_KEY`가 설정되어 있거나(auth profile이 존재하는 경우 포함) **그리고** `models.providers.vllm`을 정의하지 않은 경우, OpenClaw는 다음을 조회합니다:

- `GET http://127.0.0.1:8000/v1/models`

…그리고 반환된 ID를 모델 항목으로 변환합니다.

`models.providers.vllm`을 명시적으로 설정하면 자동 검색은 건너뛰며, 모델을 수동으로 정의해야 합니다.

## 명시적 구성(수동 모델)

다음과 같은 경우에는 명시적 config를 사용하세요:

- vLLM이 다른 호스트/포트에서 실행되는 경우
- `contextWindow`/`maxTokens` 값을 고정하려는 경우
- 서버에 실제 API 키가 필요하거나(또는 헤더를 직접 제어하려는 경우)

```json5
{
  models: {
    providers: {
      vllm: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "${VLLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "Local vLLM Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## 문제 해결

- 서버에 연결할 수 있는지 확인합니다:

```bash
curl http://127.0.0.1:8000/v1/models
```

- 인증 오류로 요청이 실패하면, 서버 구성과 일치하는 실제 `VLLM_API_KEY`를 설정하거나 `models.providers.vllm` 아래에 제공자를 명시적으로 구성하세요.

## 프록시 스타일 동작

vLLM은 네이티브 OpenAI 엔드포인트가 아니라, 프록시 스타일의 OpenAI 호환 `/v1` 백엔드로 취급됩니다.

- 네이티브 OpenAI 전용 요청 형태 조정은 여기에 적용되지 않습니다
- `service_tier`, Responses `store`, 프롬프트 캐시 힌트, OpenAI reasoning-compat 페이로드 형태 조정은 없습니다
- 숨겨진 OpenClaw attribution 헤더(`originator`, `version`, `User-Agent`)는 커스텀 vLLM 기본 URL에 주입되지 않습니다
