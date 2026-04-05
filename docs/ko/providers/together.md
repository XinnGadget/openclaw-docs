---
read_when:
    - OpenClaw에서 Together AI를 사용하려는 경우
    - API 키 env var 또는 CLI auth choice가 필요한 경우
summary: Together AI 설정(인증 + 모델 선택)
title: Together AI
x-i18n:
    generated_at: "2026-04-05T12:53:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 22aacbaadf860ce8245bba921dcc5ede9da8fd6fa1bc3cc912551aecc1ba0d71
    source_path: providers/together.md
    workflow: 15
---

# Together AI

[Together AI](https://together.ai)는 통합 API를 통해 Llama, DeepSeek, Kimi 등 주요 오픈소스 모델에 대한 액세스를 제공합니다.

- Provider: `together`
- 인증: `TOGETHER_API_KEY`
- API: OpenAI 호환
- 기본 URL: `https://api.together.xyz/v1`

## 빠른 시작

1. API 키를 설정합니다(권장: Gateway용으로 저장):

```bash
openclaw onboard --auth-choice together-api-key
```

2. 기본 모델을 설정합니다:

```json5
{
  agents: {
    defaults: {
      model: { primary: "together/moonshotai/Kimi-K2.5" },
    },
  },
}
```

## 비대화형 예시

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

이렇게 하면 `together/moonshotai/Kimi-K2.5`가 기본 모델로 설정됩니다.

## 환경 참고

Gateway가 데몬(launchd/systemd)으로 실행되는 경우, `TOGETHER_API_KEY`가
해당 프로세스에서 사용할 수 있도록 해야 합니다(예: `~/.openclaw/.env` 또는
`env.shellEnv`를 통해).

## 내장 카탈로그

OpenClaw는 현재 다음과 같은 번들 Together 카탈로그를 제공합니다:

| 모델 참조                                                     | 이름                                   | 입력        | 컨텍스트   | 참고                             |
| ------------------------------------------------------------ | -------------------------------------- | ----------- | ---------- | -------------------------------- |
| `together/moonshotai/Kimi-K2.5`                              | Kimi K2.5                              | 텍스트, 이미지 | 262,144    | 기본 모델, reasoning 활성화됨    |
| `together/zai-org/GLM-4.7`                                   | GLM 4.7 Fp8                            | 텍스트      | 202,752    | 범용 텍스트 모델                 |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`           | Llama 3.3 70B Instruct Turbo           | 텍스트      | 131,072    | 빠른 지시 모델                   |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct`         | Llama 4 Scout 17B 16E Instruct         | 텍스트, 이미지 | 10,000,000 | 멀티모달                         |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | Llama 4 Maverick 17B 128E Instruct FP8 | 텍스트, 이미지 | 20,000,000 | 멀티모달                         |
| `together/deepseek-ai/DeepSeek-V3.1`                         | DeepSeek V3.1                          | 텍스트      | 131,072    | 범용 텍스트 모델                 |
| `together/deepseek-ai/DeepSeek-R1`                           | DeepSeek R1                            | 텍스트      | 131,072    | reasoning 모델                   |
| `together/moonshotai/Kimi-K2-Instruct-0905`                  | Kimi K2-Instruct 0905                  | 텍스트      | 262,144    | 보조 Kimi 텍스트 모델            |

onboarding 프리셋은 `together/moonshotai/Kimi-K2.5`를 기본 모델로 설정합니다.
