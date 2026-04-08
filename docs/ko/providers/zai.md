---
read_when:
    - OpenClaw에서 Z.AI / GLM 모델을 사용하려는 경우
    - 간단한 ZAI_API_KEY 설정이 필요한 경우
summary: OpenClaw에서 Z.AI(GLM 모델) 사용하기
title: Z.AI
x-i18n:
    generated_at: "2026-04-08T05:55:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66cbd9813ee28d202dcae34debab1b0cf9927793acb00743c1c62b48d9e381f9
    source_path: providers/zai.md
    workflow: 15
---

# Z.AI

Z.AI는 **GLM** 모델용 API 플랫폼입니다. GLM용 REST API를 제공하며 인증에는 API 키를
사용합니다. Z.AI 콘솔에서 API 키를 생성하세요. OpenClaw는 Z.AI API 키와 함께 `zai` provider를
사용합니다.

## CLI 설정

```bash
# 엔드포인트 자동 감지를 사용하는 일반 API 키 설정
openclaw onboard --auth-choice zai-api-key

# 코딩 플랜 Global, 코딩 플랜 사용자에게 권장
openclaw onboard --auth-choice zai-coding-global

# 코딩 플랜 CN(중국 리전), 코딩 플랜 사용자에게 권장
openclaw onboard --auth-choice zai-coding-cn

# 일반 API
openclaw onboard --auth-choice zai-global

# 일반 API CN(중국 리전)
openclaw onboard --auth-choice zai-cn
```

## 구성 스니펫

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

`zai-api-key`를 사용하면 OpenClaw가 키에서 일치하는 Z.AI 엔드포인트를 감지하고
올바른 기본 URL을 자동으로 적용할 수 있습니다. 특정 코딩 플랜 또는 일반 API 표면을 강제하려는 경우
명시적인 지역 선택지를 사용하세요.

## 번들된 GLM 카탈로그

OpenClaw는 현재 번들된 `zai` provider를 다음으로 시드합니다:

- `glm-5.1`
- `glm-5`
- `glm-5-turbo`
- `glm-5v-turbo`
- `glm-4.7`
- `glm-4.7-flash`
- `glm-4.7-flashx`
- `glm-4.6`
- `glm-4.6v`
- `glm-4.5`
- `glm-4.5-air`
- `glm-4.5-flash`
- `glm-4.5v`

## 참고

- GLM 모델은 `zai/<model>`로 사용할 수 있습니다(예: `zai/glm-5`).
- 기본 번들 모델 ref: `zai/glm-5.1`
- 알 수 없는 `glm-5*` ID도 현재 GLM-5 패밀리 형태와 일치하는 경우
  `glm-4.7` 템플릿에서 provider 소유 메타데이터를 합성하여 번들된 provider 경로에서 계속 해석됩니다.
- Z.AI 도구 호출 스트리밍을 위해 `tool_stream`은 기본적으로 활성화되어 있습니다.
  비활성화하려면 `agents.defaults.models["zai/<model>"].params.tool_stream`을 `false`로 설정하세요.
- 모델 패밀리 개요는 [/providers/glm](/ko/providers/glm)를 참조하세요.
- Z.AI는 API 키와 함께 Bearer 인증을 사용합니다.
