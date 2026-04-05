---
read_when:
    - OpenClaw에서 NVIDIA 모델을 사용하려는 경우
    - NVIDIA_API_KEY 설정이 필요한 경우
summary: OpenClaw에서 NVIDIA의 OpenAI 호환 API 사용하기
title: NVIDIA
x-i18n:
    generated_at: "2026-04-05T12:52:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: a24c5e46c0cf0fbc63bf09c772b486dd7f8f4b52e687d3b835bb54a1176b28da
    source_path: providers/nvidia.md
    workflow: 15
---

# NVIDIA

NVIDIA는 Nemotron 및 NeMo 모델용 OpenAI 호환 API를 `https://integrate.api.nvidia.com/v1`에서 제공합니다. [NVIDIA NGC](https://catalog.ngc.nvidia.com/)의 API 키로 인증하세요.

## CLI 설정

키를 한 번 내보낸 다음 온보딩을 실행하고 NVIDIA 모델을 설정하세요:

```bash
export NVIDIA_API_KEY="nvapi-..."
openclaw onboard --auth-choice skip
openclaw models set nvidia/nvidia/llama-3.1-nemotron-70b-instruct
```

여전히 `--token`을 전달하는 경우, 셸 기록과 `ps` 출력에 남는다는 점을 기억하세요. 가능하면 환경 변수를 사용하는 것이 좋습니다.

## 설정 스니펫

```json5
{
  env: { NVIDIA_API_KEY: "nvapi-..." },
  models: {
    providers: {
      nvidia: {
        baseUrl: "https://integrate.api.nvidia.com/v1",
        api: "openai-completions",
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "nvidia/nvidia/llama-3.1-nemotron-70b-instruct" },
    },
  },
}
```

## 모델 ID

| 모델 참조                                            | 이름                                     | 컨텍스트 | 최대 출력 |
| ---------------------------------------------------- | ---------------------------------------- | ------- | ---------- |
| `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`      | NVIDIA Llama 3.1 Nemotron 70B Instruct   | 131,072 | 4,096      |
| `nvidia/meta/llama-3.3-70b-instruct`                 | Meta Llama 3.3 70B Instruct              | 131,072 | 4,096      |
| `nvidia/nvidia/mistral-nemo-minitron-8b-8k-instruct` | NVIDIA Mistral NeMo Minitron 8B Instruct | 8,192   | 2,048      |

## 참고

- OpenAI 호환 `/v1` 엔드포인트입니다. NVIDIA NGC의 API 키를 사용하세요.
- `NVIDIA_API_KEY`가 설정되면 제공자가 자동으로 활성화됩니다.
- 번들 카탈로그는 정적이며 비용은 소스에서 기본값 `0`으로 설정됩니다.
