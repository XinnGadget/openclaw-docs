---
read_when:
    - OpenClaw에서 OpenAI 모델을 사용하려는 경우
    - API 키 대신 Codex 구독 인증을 사용하려는 경우
summary: OpenClaw에서 API 키 또는 Codex 구독으로 OpenAI 사용하기
title: OpenAI
x-i18n:
    generated_at: "2026-04-05T12:53:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 537119853503d398f9136170ac12ecfdbd9af8aef3c4c011f8ada4c664bdaf6d
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI는 GPT 모델용 개발자 API를 제공합니다. Codex는 구독 기반 액세스를 위한 **ChatGPT 로그인**과 사용량 기반 액세스를 위한 **API 키** 로그인을 지원합니다. Codex 클라우드는 ChatGPT 로그인이 필요합니다.
OpenAI는 OpenClaw 같은 외부 도구/워크플로에서 구독 OAuth 사용을 명시적으로 지원합니다.

## 기본 상호작용 스타일

OpenClaw는 기본적으로 `openai/*` 및 `openai-codex/*` 실행 모두에 대해
작은 OpenAI 전용 프롬프트 오버레이를 추가합니다. 이 오버레이는 기본 OpenClaw 시스템
프롬프트를 대체하지 않으면서 어시스턴트를 친근하고, 협업적이며, 간결하고, 직접적으로 유지합니다.

설정 키:

`plugins.entries.openai.config.personalityOverlay`

허용 값:

- `"friendly"`: 기본값; OpenAI 전용 오버레이를 활성화합니다.
- `"off"`: 오버레이를 비활성화하고 기본 OpenClaw 프롬프트만 사용합니다.

범위:

- `openai/*` 모델에 적용됩니다.
- `openai-codex/*` 모델에 적용됩니다.
- 다른 제공자에는 영향을 주지 않습니다.

이 동작은 기본적으로 활성화되어 있습니다:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personalityOverlay: "friendly",
        },
      },
    },
  },
}
```

### OpenAI 프롬프트 오버레이 비활성화

수정되지 않은 기본 OpenClaw 프롬프트를 선호한다면 오버레이를 끄세요:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personalityOverlay: "off",
        },
      },
    },
  },
}
```

설정 CLI로 직접 지정할 수도 있습니다:

```bash
openclaw config set plugins.entries.openai.config.personalityOverlay off
```

## 옵션 A: OpenAI API 키(OpenAI Platform)

**가장 적합한 경우:** 직접 API에 접근하고 사용량 기반 과금을 사용하는 경우.
OpenAI 대시보드에서 API 키를 발급받으세요.

### CLI 설정

```bash
openclaw onboard --auth-choice openai-api-key
# 또는 비대화형
openclaw onboard --openai-api-key "$OPENAI_API_KEY"
```

### 설정 스니펫

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

OpenAI의 현재 API 모델 문서에는 직접 OpenAI API 사용용으로 `gpt-5.4`와 `gpt-5.4-pro`가
나열되어 있습니다. OpenClaw는 두 모델 모두를 `openai/*` Responses 경로를 통해 전달합니다.
OpenClaw는 오래된 `openai/gpt-5.3-codex-spark` 항목을 의도적으로 숨깁니다.
직접 OpenAI API 호출에서는 실제 트래픽에서 이 모델이 거부되기 때문입니다.

OpenClaw는 직접 OpenAI
API 경로에서 `openai/gpt-5.3-codex-spark`를 노출하지 않습니다. `pi-ai`는 여전히 이 모델에 대한
내장 항목을 제공하지만, 현재 실제 OpenAI API 요청에서는 거부됩니다. OpenClaw에서는
Spark를 Codex 전용으로 취급합니다.

## 옵션 B: OpenAI Code(Codex) 구독

**가장 적합한 경우:** API 키 대신 ChatGPT/Codex 구독 액세스를 사용하는 경우.
Codex 클라우드는 ChatGPT 로그인이 필요하며, Codex CLI는 ChatGPT 또는 API 키 로그인을 지원합니다.

### CLI 설정(Codex OAuth)

```bash
# 마법사에서 Codex OAuth 실행
openclaw onboard --auth-choice openai-codex

# 또는 OAuth 직접 실행
openclaw models auth login --provider openai-codex
```

### 설정 스니펫(Codex 구독)

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

OpenAI의 현재 Codex 문서에는 현재 Codex 모델로 `gpt-5.4`가 나열되어 있습니다. OpenClaw는
이를 ChatGPT/Codex OAuth 사용을 위한 `openai-codex/gpt-5.4`로 매핑합니다.

온보딩이 기존 Codex CLI 로그인을 재사용하는 경우, 해당 자격 증명은 계속
Codex CLI에서 관리됩니다. 만료 시 OpenClaw는 먼저 외부 Codex 소스를 다시 읽고,
제공자가 갱신할 수 있는 경우 별도의 OpenClaw 전용 사본을 소유하지 않고
갱신된 자격 증명을 다시 Codex 저장소에 기록합니다.

Codex 계정에 Codex Spark 권한이 있다면 OpenClaw는 다음도 지원합니다:

- `openai-codex/gpt-5.3-codex-spark`

OpenClaw는 Codex Spark를 Codex 전용으로 취급합니다. 직접
`openai/gpt-5.3-codex-spark` API 키 경로는 노출하지 않습니다.

OpenClaw는 또한 `pi-ai`가
이를 탐색했을 때 `openai-codex/gpt-5.3-codex-spark`를 보존합니다. 이는 권한 의존적이고 실험적인 기능으로
취급하세요. Codex Spark는 GPT-5.4 `/fast`와 별개이며, 사용 가능 여부는 로그인한 Codex /
ChatGPT 계정에 따라 달라집니다.

### Codex 컨텍스트 윈도우 상한

OpenClaw는 Codex 모델 메타데이터와 런타임 컨텍스트 상한을 별도의 값으로 취급합니다.

`openai-codex/gpt-5.4`의 경우:

- 기본 `contextWindow`: `1050000`
- 기본 런타임 `contextTokens` 상한: `272000`

이렇게 하면 모델 메타데이터를 사실대로 유지하면서도 실제로 더 나은 지연 시간과 품질 특성을 보이는
더 작은 기본 런타임 윈도우를 유지할 수 있습니다.

다른 유효 상한을 원한다면 `models.providers.<provider>.models[].contextTokens`를 설정하세요:

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [
          {
            id: "gpt-5.4",
            contextTokens: 160000,
          },
        ],
      },
    },
  },
}
```

기본 모델
메타데이터를 선언하거나 재정의할 때만 `contextWindow`를 사용하세요. 런타임 컨텍스트 예산을 제한하려면 `contextTokens`를 사용하세요.

### 기본 전송 방식

OpenClaw는 모델 스트리밍에 `pi-ai`를 사용합니다. `openai/*`와
`openai-codex/*` 모두에서 기본 전송 방식은 `"auto"`입니다(WebSocket 우선, 이후 SSE
폴백).

`"auto"` 모드에서 OpenClaw는 SSE로 폴백하기 전에
초기 단계의 재시도 가능한 WebSocket 실패도 한 번 재시도합니다. 강제 `"websocket"` 모드에서는 여전히 전송 오류를
폴백 뒤에 숨기지 않고 직접 표시합니다.

`"auto"` 모드에서 연결 또는 초기 턴 WebSocket 실패가 발생한 후 OpenClaw는
해당 세션의 WebSocket 경로를 약 60초 동안 성능 저하 상태로 표시하고,
전송 방식 사이를 계속 오가며 흔들리지 않도록 이 냉각 시간 동안 이후 턴을 SSE로 전송합니다.

기본 OpenAI 계열 엔드포인트(`openai/*`, `openai-codex/*`, Azure
OpenAI Responses)의 경우, OpenClaw는 재시도, 재연결, SSE 폴백이 동일한
대화 식별성에 맞춰 정렬되도록 요청에 안정적인 세션 및 턴 식별 상태도 첨부합니다. 기본 OpenAI 계열 경로에서는 여기에는 안정적인
세션/턴 요청 식별 헤더와 일치하는 전송 메타데이터가 포함됩니다.

OpenClaw는 또한 OpenAI 사용량 카운터가
세션/상태 표면에 도달하기 전에 전송 방식 변형 전반에서 이를 정규화합니다. 기본 OpenAI/Codex Responses 트래픽은
사용량을 `input_tokens` / `output_tokens` 또는
`prompt_tokens` / `completion_tokens`로 보고할 수 있습니다. OpenClaw는 이를 `/status`, `/usage`, 세션 로그에서 동일한 입력 및
출력 카운터로 취급합니다. 기본 WebSocket 트래픽에서 `total_tokens`가 생략되거나(`0`을 보고하는 경우 포함)
OpenClaw는 정규화된 입력 + 출력 합계를 대신 사용하여 세션/상태 표시가 계속 채워지도록 합니다.

`agents.defaults.models.<provider/model>.params.transport`를 설정할 수 있습니다:

- `"sse"`: SSE 강제 사용
- `"websocket"`: WebSocket 강제 사용
- `"auto"`: WebSocket을 시도한 후 SSE로 폴백

`openai/*`(Responses API)의 경우 OpenClaw는 WebSocket 전송이 사용될 때
기본적으로 WebSocket 워밍업도 활성화합니다(`openaiWsWarmup: true`).

관련 OpenAI 문서:

- [WebSocket을 사용하는 Realtime API](https://platform.openai.com/docs/guides/realtime-websocket)
- [스트리밍 API 응답(SSE)](https://platform.openai.com/docs/guides/streaming-responses)

```json5
{
  agents: {
    defaults: {
      model: { primary: "openai-codex/gpt-5.4" },
      models: {
        "openai-codex/gpt-5.4": {
          params: {
            transport: "auto",
          },
        },
      },
    },
  },
}
```

### OpenAI WebSocket 워밍업

OpenAI 문서에서는 워밍업을 선택 사항으로 설명합니다. OpenClaw는
WebSocket 전송 사용 시 첫 번째 턴 지연 시간을 줄이기 위해 `openai/*`에 대해 기본적으로 이를 활성화합니다.

### 워밍업 비활성화

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: false,
          },
        },
      },
    },
  },
}
```

### 워밍업 명시적 활성화

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: true,
          },
        },
      },
    },
  },
}
```

### OpenAI 및 Codex 우선 처리

OpenAI API는 `service_tier=priority`를 통해 우선 처리를 노출합니다. OpenClaw에서는
`agents.defaults.models["<provider>/<model>"].params.serviceTier`를 설정해
기본 OpenAI/Codex Responses 엔드포인트에 해당 필드를 그대로 전달합니다.

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

지원되는 값은 `auto`, `default`, `flex`, `priority`입니다.

OpenClaw는 `params.serviceTier`를 직접 `openai/*` Responses
요청과 `openai-codex/*` Codex Responses 요청 모두에 전달합니다. 단, 해당 모델이
기본 OpenAI/Codex 엔드포인트를 가리킬 때에만 그렇습니다.

중요한 동작:

- 직접 `openai/*`는 `api.openai.com`을 대상으로 해야 합니다
- `openai-codex/*`는 `chatgpt.com/backend-api`를 대상으로 해야 합니다
- 두 제공자 중 하나라도 다른 기본 URL 또는 프록시를 통해 라우팅하면 OpenClaw는 `service_tier`를 그대로 둡니다

### OpenAI fast 모드

OpenClaw는 `openai/*`와
`openai-codex/*` 세션 모두에 대해 공통 fast 모드 토글을 제공합니다:

- Chat/UI: `/fast status|on|off`
- 설정: `agents.defaults.models["<provider>/<model>"].params.fastMode`

fast 모드가 활성화되면 OpenClaw는 이를 OpenAI 우선 처리로 매핑합니다:

- `api.openai.com`으로 가는 직접 `openai/*` Responses 호출은 `service_tier = "priority"`를 전송합니다
- `chatgpt.com/backend-api`로 가는 `openai-codex/*` Responses 호출도 `service_tier = "priority"`를 전송합니다
- 기존 페이로드의 `service_tier` 값은 보존됩니다
- fast 모드는 `reasoning` 또는 `text.verbosity`를 다시 쓰지 않습니다

예시:

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
      },
    },
  },
}
```

세션 재정의는 설정보다 우선합니다. Sessions UI에서 세션 재정의를 지우면
세션은 설정된 기본값으로 돌아갑니다.

### 기본 OpenAI와 OpenAI 호환 경로 비교

OpenClaw는 직접 OpenAI, Codex, Azure OpenAI 엔드포인트를
일반적인 OpenAI 호환 `/v1` 프록시와 다르게 취급합니다:

- 기본 `openai/*`, `openai-codex/*`, Azure OpenAI 경로는
  추론을 명시적으로 비활성화할 때 `reasoning: { effort: "none" }`를 그대로 유지합니다
- 기본 OpenAI 계열 경로는 도구 스키마를 기본적으로 strict 모드로 설정합니다
- 숨겨진 OpenClaw attribution 헤더(`originator`, `version`,
  `User-Agent`)는 검증된 기본 OpenAI 호스트
  (`api.openai.com`)와 기본 Codex 호스트(`chatgpt.com/backend-api`)에만 첨부됩니다
- 기본 OpenAI/Codex 경로는 `service_tier`, Responses `store`, OpenAI 추론 호환 페이로드,
  프롬프트 캐시 힌트와 같은 OpenAI 전용 요청 형태를 유지합니다
- 프록시 스타일 OpenAI 호환 경로는 더 느슨한 호환 동작을 유지하며
  strict 도구 스키마, 기본 전용 요청 형태, 숨겨진
  OpenAI/Codex attribution 헤더를 강제하지 않습니다

Azure OpenAI는 전송 및 호환 동작 면에서는 기본 라우팅 묶음에 남아 있지만,
숨겨진 OpenAI/Codex attribution 헤더는 받지 않습니다.

이렇게 하면 오래된
OpenAI 호환 shim을 서드파티 `/v1` 백엔드에 강제하지 않으면서 현재 기본 OpenAI Responses 동작을 보존할 수 있습니다.

### OpenAI Responses 서버 측 압축

직접 OpenAI Responses 모델(`api: "openai-responses"`를 사용하는 `openai/*`, 그리고
`baseUrl`이 `api.openai.com`인 경우)에 대해 OpenClaw는 이제 OpenAI 서버 측
압축 페이로드 힌트를 자동으로 활성화합니다:

- `store: true` 강제 설정(단, 모델 호환성이 `supportsStore: false`를 설정한 경우 제외)
- `context_management: [{ type: "compaction", compact_threshold: ... }]` 주입

기본적으로 `compact_threshold`는 모델 `contextWindow`의 `70%`입니다(사용할 수 없으면 `80000`).

### 서버 측 압축 명시적 활성화

호환되는 Responses 모델(예: Azure OpenAI Responses)에서 `context_management`
주입을 강제로 사용하려는 경우 이 설정을 사용하세요:

```json5
{
  agents: {
    defaults: {
      models: {
        "azure-openai-responses/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
          },
        },
      },
    },
  },
}
```

### 사용자 지정 임계값으로 활성화

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
            responsesCompactThreshold: 120000,
          },
        },
      },
    },
  },
}
```

### 서버 측 압축 비활성화

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: false,
          },
        },
      },
    },
  },
}
```

`responsesServerCompaction`은 `context_management` 주입만 제어합니다.
직접 OpenAI Responses 모델은 호환성이
`supportsStore: false`를 설정하지 않는 한 여전히 `store: true`를 강제합니다.

## 참고

- 모델 참조는 항상 `provider/model`을 사용합니다([/concepts/models](/ko/concepts/models) 참고).
- 인증 세부 정보와 재사용 규칙은 [/concepts/oauth](/ko/concepts/oauth)에 있습니다.
