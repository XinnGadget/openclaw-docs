---
read_when:
    - 워크플로 내부에 JSON 전용 LLM 단계를 두고 싶은 경우
    - 자동화를 위해 스키마 검증된 LLM 출력이 필요한 경우
summary: 워크플로용 JSON 전용 LLM 작업(선택적 plugin 도구)
title: LLM Task
x-i18n:
    generated_at: "2026-04-05T12:57:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: cbe9b286a8e958494de06a59b6e7b750a82d492158df344c7afe30fce24f0584
    source_path: tools/llm-task.md
    workflow: 15
---

# LLM Task

`llm-task`는 JSON 전용 LLM 작업을 실행하고
구조화된 출력을 반환하는 **선택적 plugin 도구**입니다(선택적으로 JSON Schema로 검증 가능).

이것은 Lobster 같은 워크플로 엔진에 이상적입니다. 각 워크플로마다
별도의 OpenClaw 코드를 작성하지 않고도 단일 LLM 단계를 추가할 수 있습니다.

## plugin 활성화

1. plugin을 활성화합니다:

```json
{
  "plugins": {
    "entries": {
      "llm-task": { "enabled": true }
    }
  }
}
```

2. 도구를 allowlist에 추가합니다(`optional: true`로 등록됨):

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": { "allow": ["llm-task"] }
      }
    ]
  }
}
```

## 설정(선택 사항)

```json
{
  "plugins": {
    "entries": {
      "llm-task": {
        "enabled": true,
        "config": {
          "defaultProvider": "openai-codex",
          "defaultModel": "gpt-5.4",
          "defaultAuthProfileId": "main",
          "allowedModels": ["openai-codex/gpt-5.4"],
          "maxTokens": 800,
          "timeoutMs": 30000
        }
      }
    }
  }
}
```

`allowedModels`는 `provider/model` 문자열의 allowlist입니다. 설정된 경우,
목록 밖의 요청은 모두 거부됩니다.

## 도구 매개변수

- `prompt`(string, 필수)
- `input`(any, 선택 사항)
- `schema`(object, 선택 사항 JSON Schema)
- `provider`(string, 선택 사항)
- `model`(string, 선택 사항)
- `thinking`(string, 선택 사항)
- `authProfileId`(string, 선택 사항)
- `temperature`(number, 선택 사항)
- `maxTokens`(number, 선택 사항)
- `timeoutMs`(number, 선택 사항)

`thinking`은 `low` 또는 `medium` 같은 표준 OpenClaw 추론 프리셋을 받습니다.

## 출력

파싱된 JSON이 들어 있는 `details.json`을 반환합니다(`schema`가 제공된 경우
이에 대해 검증도 수행).

## 예시: Lobster 워크플로 단계

```lobster
openclaw.invoke --tool llm-task --action json --args-json '{
  "prompt": "입력 이메일을 바탕으로 intent와 draft를 반환하세요.",
  "thinking": "low",
  "input": {
    "subject": "Hello",
    "body": "Can you help?"
  },
  "schema": {
    "type": "object",
    "properties": {
      "intent": { "type": "string" },
      "draft": { "type": "string" }
    },
    "required": ["intent", "draft"],
    "additionalProperties": false
  }
}'
```

## 안전 참고 사항

- 이 도구는 **JSON 전용**이며 모델에 JSON만 출력하도록 지시합니다(
  코드 펜스 없음, 설명 없음).
- 이 실행에서는 모델에 어떤 도구도 노출되지 않습니다.
- `schema`로 검증하지 않는 한 출력은 신뢰할 수 없는 것으로 취급하세요.
- 부작용이 있는 단계(보내기, 게시, 실행) 앞에는 승인을 두세요.
