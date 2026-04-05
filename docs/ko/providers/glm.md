---
read_when:
    - OpenClaw에서 GLM 모델을 사용하려는 경우
    - 모델 명명 규칙과 설정 방법이 필요한 경우
summary: GLM 모델 패밀리 개요 + OpenClaw에서 사용하는 방법
title: GLM 모델
x-i18n:
    generated_at: "2026-04-05T12:51:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 59622edab5094d991987f9788fbf08b33325e737e7ff88632b0c3ac89412d4c7
    source_path: providers/glm.md
    workflow: 15
---

# GLM 모델

GLM은 Z.AI 플랫폼에서 제공되는 **모델 패밀리**(회사가 아님)입니다. OpenClaw에서 GLM
모델은 `zai` 제공자와 `zai/glm-5` 같은 모델 ID를 통해 사용합니다.

## CLI 설정

```bash
# 엔드포인트 자동 감지가 포함된 일반 API 키 설정
openclaw onboard --auth-choice zai-api-key

# Coding Plan Global, Coding Plan 사용자에게 권장
openclaw onboard --auth-choice zai-coding-global

# Coding Plan CN(중국 지역), Coding Plan 사용자에게 권장
openclaw onboard --auth-choice zai-coding-cn

# 일반 API
openclaw onboard --auth-choice zai-global

# 일반 API CN(중국 지역)
openclaw onboard --auth-choice zai-cn
```

## 설정 스니펫

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5" } } },
}
```

`zai-api-key`를 사용하면 OpenClaw가 키에서 일치하는 Z.AI 엔드포인트를 감지하고
올바른 기본 URL을 자동으로 적용할 수 있습니다. 특정 Coding Plan 또는 일반 API 표면을
강제로 사용하려면 명시적인 지역 선택지를 사용하세요.

## 현재 번들된 GLM 모델

OpenClaw는 현재 번들된 `zai` 제공자에 다음 GLM 참조를 시드합니다:

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
- 기본 번들 모델 참조는 `zai/glm-5`입니다.
- 제공자에 대한 자세한 내용은 [/providers/zai](/providers/zai)를 참고하세요.
