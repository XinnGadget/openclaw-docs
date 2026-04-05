---
read_when:
    - OpenClaw에서 Volcano Engine 또는 Doubao 모델을 사용하려는 경우
    - Volcengine API 키 설정이 필요한 경우
summary: Volcano Engine 설정(Doubao 모델, 일반 + 코딩 엔드포인트)
title: Volcengine (Doubao)
x-i18n:
    generated_at: "2026-04-05T12:53:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: 85d9e737e906cd705fb31479d6b78d92b68c9218795ea9667516c1571dcaaf3a
    source_path: providers/volcengine.md
    workflow: 15
---

# Volcengine (Doubao)

Volcengine 제공자는 Volcano Engine에 호스팅된 Doubao 모델과 서드파티 모델에 대한
액세스를 제공하며, 일반 워크로드와 코딩 워크로드에 대해 별도의 엔드포인트를
사용합니다.

- 제공자: `volcengine`(일반) + `volcengine-plan`(코딩)
- 인증: `VOLCANO_ENGINE_API_KEY`
- API: OpenAI 호환

## 빠른 시작

1. API 키를 설정합니다:

```bash
openclaw onboard --auth-choice volcengine-api-key
```

2. 기본 모델을 설정합니다:

```json5
{
  agents: {
    defaults: {
      model: { primary: "volcengine-plan/ark-code-latest" },
    },
  },
}
```

## 비대화형 예시

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice volcengine-api-key \
  --volcengine-api-key "$VOLCANO_ENGINE_API_KEY"
```

## 제공자 및 엔드포인트

| 제공자          | 엔드포인트                                  | 사용 사례      |
| ----------------- | ----------------------------------------- | -------------- |
| `volcengine`      | `ark.cn-beijing.volces.com/api/v3`        | 일반 모델 |
| `volcengine-plan` | `ark.cn-beijing.volces.com/api/coding/v3` | 코딩 모델  |

두 제공자 모두 단일 API 키로 설정됩니다. 설정하면 둘 다 자동으로
등록됩니다.

## 사용 가능한 모델

일반 제공자(`volcengine`):

| 모델 참조                                    | 이름                            | 입력        | 컨텍스트 |
| -------------------------------------------- | ------------------------------- | ----------- | ------- |
| `volcengine/doubao-seed-1-8-251228`          | Doubao Seed 1.8                 | text, image | 256,000 |
| `volcengine/doubao-seed-code-preview-251028` | doubao-seed-code-preview-251028 | text, image | 256,000 |
| `volcengine/kimi-k2-5-260127`                | Kimi K2.5                       | text, image | 256,000 |
| `volcengine/glm-4-7-251222`                  | GLM 4.7                         | text, image | 200,000 |
| `volcengine/deepseek-v3-2-251201`            | DeepSeek V3.2                   | text, image | 128,000 |

코딩 제공자(`volcengine-plan`):

| 모델 참조                                         | 이름                     | 입력 | 컨텍스트 |
| ------------------------------------------------- | ------------------------ | ----- | ------- |
| `volcengine-plan/ark-code-latest`                 | Ark Coding Plan          | text  | 256,000 |
| `volcengine-plan/doubao-seed-code`                | Doubao Seed Code         | text  | 256,000 |
| `volcengine-plan/glm-4.7`                         | GLM 4.7 Coding           | text  | 200,000 |
| `volcengine-plan/kimi-k2-thinking`                | Kimi K2 Thinking         | text  | 256,000 |
| `volcengine-plan/kimi-k2.5`                       | Kimi K2.5 Coding         | text  | 256,000 |
| `volcengine-plan/doubao-seed-code-preview-251028` | Doubao Seed Code Preview | text  | 256,000 |

`openclaw onboard --auth-choice volcengine-api-key`는 현재
일반 `volcengine` 카탈로그도 함께 등록하면서
`volcengine-plan/ark-code-latest`를 기본 모델로 설정합니다.

온보딩/설정 중 모델 선택에서는 Volcengine 인증 선택이
`volcengine/*`와 `volcengine-plan/*` 항목을 모두 우선적으로 표시합니다. 해당 모델이 아직
로드되지 않았다면 OpenClaw는 빈 제공자 범위 선택기를 보여주는 대신
필터링되지 않은 카탈로그로 폴백합니다.

## 환경 참고

Gateway가 데몬(launchd/systemd)으로 실행되는 경우,
`VOLCANO_ENGINE_API_KEY`가 해당 프로세스에서 사용 가능하도록 해야 합니다(예:
`~/.openclaw/.env` 또는 `env.shellEnv`를 통해).
