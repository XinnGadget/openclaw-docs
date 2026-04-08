---
read_when:
    - OpenClaw에서 GLM 모델을 사용하려는 경우
    - 모델 명명 규칙과 설정이 필요한 경우
summary: GLM 모델 패밀리 개요와 OpenClaw에서 사용하는 방법
title: GLM 모델
x-i18n:
    generated_at: "2026-04-08T05:55:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 79a55acfa139847b4b85dbc09f1068cbd2febb1e49f984a23ea9e3b43bc910eb
    source_path: providers/glm.md
    workflow: 15
---

# GLM 모델

GLM은 Z.AI 플랫폼을 통해 사용할 수 있는 **모델 패밀리**(회사가 아님)입니다. OpenClaw에서 GLM
모델은 `zai` provider와 `zai/glm-5` 같은 모델 ID를 통해 액세스합니다.

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

## 현재 번들된 GLM 모델

OpenClaw는 현재 번들된 `zai` provider에 다음 GLM ref를 시드합니다:

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

- GLM 버전과 제공 여부는 변경될 수 있으므로 최신 정보는 Z.AI 문서를 확인하세요.
- 기본 번들 모델 ref는 `zai/glm-5.1`입니다.
- provider 세부 정보는 [/providers/zai](/ko/providers/zai)를 참조하세요.
