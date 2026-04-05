---
read_when:
    - 많은 LLM에 대해 단일 API 키를 원하는 경우
    - OpenClaw에서 Kilo Gateway를 통해 모델을 실행하려는 경우
summary: Kilo Gateway의 통합 API를 사용해 OpenClaw에서 다양한 모델에 액세스합니다
title: Kilo Gateway
x-i18n:
    generated_at: "2026-04-05T12:52:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 857266967b4a7553d501990631df2bae0f849d061521dc9f34e29687ecb94884
    source_path: providers/kilocode.md
    workflow: 15
---

# Kilo Gateway

Kilo Gateway는 단일
엔드포인트와 API 키 뒤에서 많은 모델로 요청을 라우팅하는 **통합 API**를 제공합니다. OpenAI 호환이므로 기본 URL만 변경하면 대부분의 OpenAI SDK를 사용할 수 있습니다.

## API 키 받기

1. [app.kilo.ai](https://app.kilo.ai)로 이동합니다
2. 로그인하거나 계정을 생성합니다
3. API Keys로 이동해 새 키를 생성합니다

## CLI 설정

```bash
openclaw onboard --auth-choice kilocode-api-key
```

또는 환경 변수를 설정합니다.

```bash
export KILOCODE_API_KEY="<your-kilocode-api-key>" # pragma: allowlist secret
```

## 설정 스니펫

```json5
{
  env: { KILOCODE_API_KEY: "<your-kilocode-api-key>" }, // pragma: allowlist secret
  agents: {
    defaults: {
      model: { primary: "kilocode/kilo/auto" },
    },
  },
}
```

## 기본 모델

기본 모델은 Kilo Gateway가 관리하는 provider 소유의 스마트 라우팅
모델인 `kilocode/kilo/auto`입니다.

OpenClaw는 `kilocode/kilo/auto`를 안정적인 기본 ref로 취급하지만, 해당 경로에 대한 작업별 업스트림 모델 매핑은 소스 기반으로 게시하지 않습니다.

## 사용 가능한 모델

OpenClaw는 시작 시 Kilo Gateway에서 사용 가능한 모델을 동적으로 검색합니다.
계정에서 사용할 수 있는 전체 모델 목록을 보려면 `/models kilocode`를 사용하세요.

게이트웨이에서 사용할 수 있는 모든 모델은 `kilocode/` 접두사와 함께 사용할 수 있습니다.

```
kilocode/kilo/auto              (기본값 - 스마트 라우팅)
kilocode/anthropic/claude-sonnet-4
kilocode/openai/gpt-5.4
kilocode/google/gemini-3-pro-preview
...그 외 다수
```

## 참고 사항

- 모델 ref는 `kilocode/<model-id>`입니다(예: `kilocode/anthropic/claude-sonnet-4`).
- 기본 모델: `kilocode/kilo/auto`
- 기본 URL: `https://api.kilo.ai/api/gateway/`
- 번들된 대체 카탈로그에는 항상 `kilocode/kilo/auto` (`Kilo Auto`)가 포함되며,
  `input: ["text", "image"]`, `reasoning: true`, `contextWindow: 1000000`,
  `maxTokens: 128000`을 가집니다
- 시작 시 OpenClaw는 `GET https://api.kilo.ai/api/gateway/models`를 시도하고
  정적 대체 카탈로그보다 앞서 검색된 모델을 병합합니다
- `kilocode/kilo/auto` 뒤의 정확한 업스트림 라우팅은 OpenClaw에 하드코딩되어 있지 않고
  Kilo Gateway가 소유합니다
- 소스에서 Kilo Gateway는 OpenRouter 호환으로 문서화되어 있으므로,
  네이티브 OpenAI 요청 셰이핑이 아니라 프록시 스타일의 OpenAI 호환 경로에 머뭅니다
- Gemini 기반 Kilo ref는 프록시-Gemini 경로에 머무르므로 OpenClaw는
  네이티브 Gemini 재생 검증이나 부트스트랩 재작성을 활성화하지 않고도
  그 경로에서 Gemini thought-signature 정리를 유지합니다.
- Kilo의 공유 스트림 래퍼는 provider app 헤더를 추가하고
  지원되는 구체적인 모델 ref에 대해 프록시 추론 페이로드를 정규화합니다. `kilocode/kilo/auto`
  및 기타 프록시 추론 미지원 힌트는 해당 추론 주입을 건너뜁니다.
- 더 많은 모델/provider 옵션은 [/concepts/model-providers](/ko/concepts/model-providers)를 참조하세요.
- Kilo Gateway는 내부적으로 API 키와 함께 Bearer 토큰을 사용합니다.
