---
read_when:
    - 모델 공급자로 Synthetic을 사용하려는 경우
    - Synthetic API 키 또는 base URL 설정이 필요한 경우
summary: OpenClaw에서 Synthetic의 Anthropic 호환 API 사용
title: Synthetic
x-i18n:
    generated_at: "2026-04-05T12:53:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3495bca5cb134659cf6c54e31fa432989afe0cc04f53cf3e3146ce80a5e8af49
    source_path: providers/synthetic.md
    workflow: 15
---

# Synthetic

Synthetic은 Anthropic 호환 엔드포인트를 제공합니다. OpenClaw는 이를 `synthetic` 공급자로 등록하고 Anthropic Messages API를 사용합니다.

## 빠른 설정

1. `SYNTHETIC_API_KEY`를 설정합니다(또는 아래 마법사를 실행합니다).
2. 온보딩을 실행합니다:

```bash
openclaw onboard --auth-choice synthetic-api-key
```

기본 모델은 다음으로 설정됩니다:

```
synthetic/hf:MiniMaxAI/MiniMax-M2.5
```

## 구성 예시

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

참고: OpenClaw의 Anthropic 클라이언트는 base URL에 `/v1`을 추가하므로 `https://api.synthetic.new/anthropic`를 사용하세요(``/anthropic/v1``가 아님). Synthetic이 base URL을 변경하면 `models.providers.synthetic.baseUrl`을 재정의하세요.

## 모델 카탈로그

아래의 모든 모델은 비용이 `0`(입력/출력/캐시)입니다.

| 모델 ID | 컨텍스트 창 | 최대 토큰 | 추론 | 입력 |
| ------------------------------------------------------ | -------------- | ---------- | --------- | ------------ |
| `hf:MiniMaxAI/MiniMax-M2.5`                            | 192000         | 65536      | false     | text         |
| `hf:moonshotai/Kimi-K2-Thinking`                       | 256000         | 8192       | true      | text         |
| `hf:zai-org/GLM-4.7`                                   | 198000         | 128000     | false     | text         |
| `hf:deepseek-ai/DeepSeek-R1-0528`                      | 128000         | 8192       | false     | text         |
| `hf:deepseek-ai/DeepSeek-V3-0324`                      | 128000         | 8192       | false     | text         |
| `hf:deepseek-ai/DeepSeek-V3.1`                         | 128000         | 8192       | false     | text         |
| `hf:deepseek-ai/DeepSeek-V3.1-Terminus`                | 128000         | 8192       | false     | text         |
| `hf:deepseek-ai/DeepSeek-V3.2`                         | 159000         | 8192       | false     | text         |
| `hf:meta-llama/Llama-3.3-70B-Instruct`                 | 128000         | 8192       | false     | text         |
| `hf:meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | 524000         | 8192       | false     | text         |
| `hf:moonshotai/Kimi-K2-Instruct-0905`                  | 256000         | 8192       | false     | text         |
| `hf:moonshotai/Kimi-K2.5`                              | 256000         | 8192       | true      | text + image |
| `hf:openai/gpt-oss-120b`                               | 128000         | 8192       | false     | text         |
| `hf:Qwen/Qwen3-235B-A22B-Instruct-2507`                | 256000         | 8192       | false     | text         |
| `hf:Qwen/Qwen3-Coder-480B-A35B-Instruct`               | 256000         | 8192       | false     | text         |
| `hf:Qwen/Qwen3-VL-235B-A22B-Instruct`                  | 250000         | 8192       | false     | text + image |
| `hf:zai-org/GLM-4.5`                                   | 128000         | 128000     | false     | text         |
| `hf:zai-org/GLM-4.6`                                   | 198000         | 128000     | false     | text         |
| `hf:zai-org/GLM-5`                                     | 256000         | 128000     | true      | text + image |
| `hf:deepseek-ai/DeepSeek-V3`                           | 128000         | 8192       | false     | text         |
| `hf:Qwen/Qwen3-235B-A22B-Thinking-2507`                | 256000         | 8192       | true      | text         |

## 참고 사항

- 모델 참조는 `synthetic/<modelId>`를 사용합니다.
- 모델 허용 목록(`agents.defaults.models`)을 활성화하는 경우 사용할 모든 모델을 추가하세요.
- 공급자 규칙은 [모델 공급자](/ko/concepts/model-providers)를 참조하세요.
