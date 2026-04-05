---
read_when:
    - 여러 LLM에 대해 단일 API 키를 사용하려는 경우
    - Baidu Qianfan 설정 안내가 필요한 경우
summary: OpenClaw에서 Qianfan의 통합 API로 여러 모델에 액세스합니다
title: Qianfan
x-i18n:
    generated_at: "2026-04-05T12:53:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 965d83dd968563447ce3571a73bd71c6876275caff8664311a852b2f9827e55b
    source_path: providers/qianfan.md
    workflow: 15
---

# Qianfan 공급자 가이드

Qianfan은 Baidu의 MaaS 플랫폼으로, 단일 엔드포인트와 API 키 뒤에서 많은 모델로 요청을 라우팅하는 **통합 API**를 제공합니다. OpenAI 호환이므로 대부분의 OpenAI SDK는 base URL만 바꾸면 작동합니다.

## 사전 요구 사항

1. Qianfan API 액세스가 있는 Baidu Cloud 계정
2. Qianfan 콘솔에서 발급한 API 키
3. 시스템에 설치된 OpenClaw

## API 키 받기

1. [Qianfan Console](https://console.bce.baidu.com/qianfan/ais/console/apiKey)에 방문합니다
2. 새 애플리케이션을 만들거나 기존 애플리케이션을 선택합니다
3. API 키를 생성합니다(형식: `bce-v3/ALTAK-...`)
4. OpenClaw에서 사용할 수 있도록 API 키를 복사합니다

## CLI 설정

```bash
openclaw onboard --auth-choice qianfan-api-key
```

## 구성 스니펫

```json5
{
  env: { QIANFAN_API_KEY: "bce-v3/ALTAK-..." },
  agents: {
    defaults: {
      model: { primary: "qianfan/deepseek-v3.2" },
      models: {
        "qianfan/deepseek-v3.2": { alias: "QIANFAN" },
      },
    },
  },
  models: {
    providers: {
      qianfan: {
        baseUrl: "https://qianfan.baidubce.com/v2",
        api: "openai-completions",
        models: [
          {
            id: "deepseek-v3.2",
            name: "DEEPSEEK V3.2",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 98304,
            maxTokens: 32768,
          },
          {
            id: "ernie-5.0-thinking-preview",
            name: "ERNIE-5.0-Thinking-Preview",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 119000,
            maxTokens: 64000,
          },
        ],
      },
    },
  },
}
```

## 참고 사항

- 기본 번들 모델 참조: `qianfan/deepseek-v3.2`
- 기본 base URL: `https://qianfan.baidubce.com/v2`
- 번들 카탈로그에는 현재 `deepseek-v3.2`와 `ernie-5.0-thinking-preview`가 포함되어 있습니다
- 사용자 지정 base URL 또는 모델 메타데이터가 필요한 경우에만 `models.providers.qianfan`을 추가하거나 재정의하세요
- Qianfan은 기본 OpenAI 요청 형태가 아니라 OpenAI 호환 전송 경로를 통해 실행됩니다

## 관련 문서

- [OpenClaw 구성](/ko/gateway/configuration)
- [모델 공급자](/ko/concepts/model-providers)
- [에이전트 설정](/ko/concepts/agent)
- [Qianfan API 문서](https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb)
