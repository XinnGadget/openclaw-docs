---
read_when:
    - 로컬 SGLang 서버에 대해 OpenClaw를 실행하려는 경우
    - 자체 모델과 함께 OpenAI 호환 `/v1` 엔드포인트를 사용하려는 경우
summary: OpenAI 호환 자체 호스팅 서버인 SGLang으로 OpenClaw 실행하기
title: SGLang
x-i18n:
    generated_at: "2026-04-05T12:53:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9850277c6c5e318e60237688b4d8a5b1387d4e9586534ae2eb6ad953abba8948
    source_path: providers/sglang.md
    workflow: 15
---

# SGLang

SGLang은 **OpenAI 호환** HTTP API를 통해 오픈 소스 모델을 제공할 수 있습니다.
OpenClaw는 `openai-completions` API를 사용해 SGLang에 연결할 수 있습니다.

OpenClaw는 `SGLANG_API_KEY`로 선택적으로 활성화하고 명시적인 `models.providers.sglang` 항목을 정의하지 않은 경우, SGLang에서 사용 가능한 모델도 **자동 검색**할 수 있습니다(서버가 인증을 강제하지 않으면 어떤 값이든 동작합니다).

## 빠른 시작

1. OpenAI 호환 서버로 SGLang을 시작합니다.

base URL은 `/v1` 엔드포인트(예: `/v1/models`, `/v1/chat/completions`)를 노출해야 합니다. SGLang은 일반적으로 다음에서 실행됩니다:

- `http://127.0.0.1:30000/v1`

2. 선택적으로 활성화합니다(인증이 구성되지 않은 경우 어떤 값이든 동작함):

```bash
export SGLANG_API_KEY="sglang-local"
```

3. 온보딩을 실행하고 `SGLang`을 선택하거나, 모델을 직접 설정합니다:

```bash
openclaw onboard
```

```json5
{
  agents: {
    defaults: {
      model: { primary: "sglang/your-model-id" },
    },
  },
}
```

## 모델 검색(암시적 provider)

`SGLANG_API_KEY`가 설정되어 있거나(또는 인증 프로필이 존재하고) `models.providers.sglang`을 **정의하지 않은** 경우, OpenClaw는 다음을 조회합니다:

- `GET http://127.0.0.1:30000/v1/models`

그리고 반환된 ID를 모델 항목으로 변환합니다.

`models.providers.sglang`을 명시적으로 설정하면 자동 검색은 건너뛰며, 모델을 수동으로 정의해야 합니다.

## 명시적 구성(수동 모델)

다음과 같은 경우 명시적 구성을 사용하세요:

- SGLang이 다른 호스트/포트에서 실행되는 경우
- `contextWindow`/`maxTokens` 값을 고정하려는 경우
- 서버에 실제 API 키가 필요하거나(또는 헤더를 직접 제어하려는 경우)

```json5
{
  models: {
    providers: {
      sglang: {
        baseUrl: "http://127.0.0.1:30000/v1",
        apiKey: "${SGLANG_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "로컬 SGLang 모델",
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

- 서버에 연결 가능한지 확인합니다:

```bash
curl http://127.0.0.1:30000/v1/models
```

- 요청이 인증 오류로 실패하면 서버 구성과 일치하는 실제 `SGLANG_API_KEY`를 설정하거나, `models.providers.sglang` 아래에 provider를 명시적으로 구성하세요.

## 프록시 스타일 동작

SGLang은 네이티브 OpenAI 엔드포인트가 아니라 프록시 스타일의 OpenAI 호환 `/v1` 백엔드로 처리됩니다.

- 네이티브 OpenAI 전용 요청 형태 조정은 여기에는 적용되지 않습니다
- `service_tier`, Responses `store`, 프롬프트 캐시 힌트, OpenAI reasoning 호환 페이로드 형태 조정은 지원되지 않습니다
- 숨겨진 OpenClaw attribution 헤더(`originator`, `version`, `User-Agent`)는 사용자 지정 SGLang base URL에서는 주입되지 않습니다
