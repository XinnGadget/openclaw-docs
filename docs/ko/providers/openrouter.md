---
read_when:
    - 여러 LLM에 대해 단일 API 키를 사용하려는 경우
    - OpenClaw에서 OpenRouter를 통해 모델을 실행하려는 경우
summary: OpenClaw에서 OpenRouter의 통합 API를 사용해 다양한 모델에 액세스하기
title: OpenRouter
x-i18n:
    generated_at: "2026-04-05T12:52:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8dd354ba060bcb47724c89ae17c8e2af8caecac4bd996fcddb584716c1840b87
    source_path: providers/openrouter.md
    workflow: 15
---

# OpenRouter

OpenRouter는 단일 엔드포인트와 API 키 뒤에서 많은 모델로 요청을 라우팅하는 **통합 API**를 제공합니다. OpenAI 호환이므로, 대부분의 OpenAI SDK는 base URL만 바꾸면 사용할 수 있습니다.

## CLI 설정

```bash
openclaw onboard --auth-choice openrouter-api-key
```

## 구성 스니펫

```json5
{
  env: { OPENROUTER_API_KEY: "sk-or-..." },
  agents: {
    defaults: {
      model: { primary: "openrouter/auto" },
    },
  },
}
```

## 참고

- 모델 참조는 `openrouter/<provider>/<model>`입니다.
- 온보딩의 기본값은 `openrouter/auto`입니다. 나중에 `openclaw models set openrouter/<provider>/<model>`로 구체적인 모델로 전환하세요.
- 더 많은 모델/provider 옵션은 [/concepts/model-providers](/ko/concepts/model-providers)를 참조하세요.
- OpenRouter는 내부적으로 API 키와 함께 Bearer 토큰을 사용합니다.
- 실제 OpenRouter 요청(`https://openrouter.ai/api/v1`)에서는 OpenClaw가 OpenRouter 문서에 설명된 앱 attribution 헤더도 추가합니다:
  `HTTP-Referer: https://openclaw.ai`, `X-OpenRouter-Title: OpenClaw`, `X-OpenRouter-Categories: cli-agent`.
- 검증된 OpenRouter 경로에서는 Anthropic 모델 참조도 OpenClaw가 시스템/개발자 프롬프트 블록에서 더 나은 프롬프트 캐시 재사용을 위해 사용하는 OpenRouter 전용 Anthropic `cache_control` 마커를 유지합니다.
- OpenRouter provider를 다른 프록시/base URL로 다시 지정하면, OpenClaw는 해당 OpenRouter 전용 헤더나 Anthropic 캐시 마커를 주입하지 않습니다.
- OpenRouter는 여전히 프록시 스타일의 OpenAI 호환 경로를 통해 실행되므로, `serviceTier`, Responses `store`, OpenAI reasoning 호환 페이로드, 프롬프트 캐시 힌트 같은 OpenAI 전용 네이티브 요청 형태 조정은 전달되지 않습니다.
- Gemini 기반 OpenRouter 참조는 프록시-Gemini 경로에 유지됩니다. OpenClaw는 그 경로에서 Gemini thought-signature 정리를 유지하지만, 네이티브 Gemini 재생 검증이나 bootstrap 재작성은 활성화하지 않습니다.
- 지원되는 `auto`가 아닌 경로에서는 OpenClaw가 선택된 thinking 수준을 OpenRouter 프록시 reasoning 페이로드에 매핑합니다. 지원되지 않는 모델 힌트와 `openrouter/auto`는 해당 reasoning 주입을 건너뜁니다.
- 모델 params 아래에 OpenRouter provider 라우팅을 전달하면, OpenClaw는 공통 스트림 래퍼가 실행되기 전에 이를 OpenRouter 라우팅 메타데이터로 전달합니다.
